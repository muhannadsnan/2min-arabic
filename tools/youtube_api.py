#!/usr/bin/env python3
"""Our own YouTube connection (official Google API, the owner's OAuth login; nothing third-party).

Run with the small venv that has the Google libraries:
    Y=~/.local/share/2min-yt/venv/bin/python

    $Y tools/youtube_api.py login                      # once: browser opens → pick the channel → Allow
    $Y tools/youtube_api.py videos                     # every upload: id, date, privacy, views, title
    $Y tools/youtube_api.py stats [--days 28]          # per video: views, watch time, avg % viewed, subs, likes…
    $Y tools/youtube_api.py retention <video-id>       # audience retention curve (for channel-review)
    $Y tools/youtube_api.py search-terms [--days 28]   # what people typed to find us (→ tags)
    $Y tools/youtube_api.py comments [--max 50]        # latest comments (for channel-review)
    $Y tools/youtube_api.py audit                      # every video vs our upload + tag rules (weekly)
    $Y tools/youtube_api.py fill <stem> <video-id> [--publish-at next|2026-10-02T16:00:00+02:00] [--apply]
        # --publish-at next = the day after the channel's latest (scheduled) video, same time of day
    $Y tools/youtube_api.py title <video-id> "New title" [--apply]
    $Y tools/youtube_api.py post-comments              # hourly job: posts the sheet's pinned comment once a video is live
        # fills title, description, tags, category, language, not-for-kids, AI label, thumbnail, captions, playlist
        # from videos/<stem>-upload.md. Without --apply it only prints what it WOULD change.

Secrets live outside the repo in ~/.config/2min-youtube/ (client_secret.json from Google Cloud, token.json after
login) — never commit them. Uploading the video file itself stays manual: YouTube keeps videos uploaded by an
unaudited API project private, so the owner drops the file in Studio and this tool fills in everything else.
"""
import argparse
import datetime as dt
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
CONF = pathlib.Path.home() / ".config" / "2min-youtube"
SCOPES = ["https://www.googleapis.com/auth/youtube.force-ssl",
          "https://www.googleapis.com/auth/yt-analytics.readonly"]
EDUCATION = "27"


def creds(channel):
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    tok = CONF / f"token-{channel}.json"
    if not tok.exists():
        sys.exit(f"not logged in for '{channel}': run  login --channel {channel}")
    c = Credentials.from_authorized_user_file(str(tok), SCOPES)
    if not c.valid:
        from google.auth.exceptions import RefreshError
        try:
            c.refresh(Request())
        except RefreshError:   # Testing-mode apps: Google expires the login after 7 days
            sys.exit(f"login for '{channel}' expired (weekly in Testing mode): run  login --channel {channel}  and "
                     "send the owner the link — brand account '2 Minute Arabic'")
        tok.write_text(c.to_json())
    return c


def yt(channel):
    from googleapiclient.discovery import build
    return build("youtube", "v3", credentials=creds(channel), cache_discovery=False)


def yta(channel):
    from googleapiclient.discovery import build
    return build("youtubeAnalytics", "v2", credentials=creds(channel), cache_discovery=False)


def login(a):
    from google_auth_oauthlib.flow import InstalledAppFlow
    secret = CONF / "client_secret.json"
    if not secret.exists():
        sys.exit(f"put the downloaded OAuth client file at {secret} first")
    c = InstalledAppFlow.from_client_secrets_file(str(secret), SCOPES).run_local_server(port=0, prompt="consent")
    CONF.mkdir(parents=True, exist_ok=True)
    tok = CONF / f"token-{a.channel}.json"
    tok.write_text(c.to_json())
    tok.chmod(0o600)
    me = yt(a.channel).channels().list(part="snippet,statistics", mine=True).execute(num_retries=3)["items"][0]
    print(f"logged in: {me['snippet']['title']} ({me['id']}) · {me['statistics'].get('subscriberCount')} subscribers")


def my_videos(y):
    ch = y.channels().list(part="contentDetails", mine=True).execute(num_retries=3)["items"][0]
    uploads = ch["contentDetails"]["relatedPlaylists"]["uploads"]
    ids, token = [], None
    while True:
        r = y.playlistItems().list(part="contentDetails", playlistId=uploads, maxResults=50, pageToken=token).execute(num_retries=3)
        ids += [i["contentDetails"]["videoId"] for i in r["items"]]
        token = r.get("nextPageToken")
        if not token:
            break
    out = []
    for k in range(0, len(ids), 50):
        out += y.videos().list(part="snippet,status,statistics,contentDetails", id=",".join(ids[k:k + 50])).execute(num_retries=3)["items"]
    return out


def videos(a):
    for v in my_videos(yt(a.channel)):
        s = v["status"]
        when = s.get("publishAt") or v["snippet"]["publishedAt"]
        print(f"{v['id']}  {when[:16]}  {s['privacyStatus']:9}  {v['statistics'].get('viewCount', '0'):>6} views  "
              f"{v['snippet']['title']}")


def span(days):
    end = dt.date.today()
    return str(end - dt.timedelta(days=days)), str(end)


def stats(a):
    start, end = span(a.days)
    metrics = "views,estimatedMinutesWatched,averageViewDuration,averageViewPercentage,subscribersGained,likes,comments,shares"
    r = yta(a.channel).reports().query(ids="channel==MINE", startDate=start, endDate=end, metrics=metrics,
                                       dimensions="video", sort="-views", maxResults=50).execute(num_retries=3)
    titles = {v["id"]: v["snippet"]["title"] for v in my_videos(yt(a.channel))}
    cols = [h["name"] for h in r["columnHeaders"]]
    print(f"{start} → {end}\n" + " | ".join(["title"] + cols[1:]))
    for row in r.get("rows", []):
        d = dict(zip(cols, row))
        print(" | ".join([titles.get(d["video"], d["video"])[:60]] + [str(round(d[c], 1)) for c in cols[1:]]))
    if a.json:
        (ROOT / "output" / f"stats-{end}.json").write_text(json.dumps(r, indent=1))


def retention(a):
    start, end = span(365)
    r = yta(a.channel).reports().query(ids="channel==MINE", startDate=start, endDate=end, filters=f"video=={a.video}",
                                       metrics="audienceWatchRatio,relativeRetentionPerformance",
                                       dimensions="elapsedVideoTimeRatio").execute(num_retries=3)
    for t, watch, rel in r.get("rows", []):
        print(f"{t:4.2f}  {watch:5.2f}  {'#' * int(watch * 40):40}  rel {rel:4.2f}")


def search_terms(a):
    start, end = span(a.days)
    r = yta(a.channel).reports().query(ids="channel==MINE", startDate=start, endDate=end, metrics="views",
                                       dimensions="insightTrafficSourceDetail", filters="insightTrafficSourceType==YT_SEARCH",
                                       sort="-views", maxResults=25).execute(num_retries=3)
    for term, views in r.get("rows", []):
        print(f"{views:5}  {term}")


def comments(a):
    y = yt(a.channel)
    cid = y.channels().list(part="id", mine=True).execute(num_retries=3)["items"][0]["id"]
    r = y.commentThreads().list(part="snippet", allThreadsRelatedToChannelId=cid, maxResults=a.max,
                                order="time").execute(num_retries=3)
    for t in r["items"]:
        c = t["snippet"]["topLevelComment"]["snippet"]
        print(f"[{c['publishedAt'][:10]}] {t['snippet']['videoId']} · {c['authorDisplayName']}: {c['textOriginal']}"
              f"  ({t['snippet']['totalReplyCount']} replies)")


def seconds(iso):
    """ISO 8601 duration (PT1M4S) → seconds."""
    m = re.fullmatch(r"P(?:(\d+)D)?T?(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?", iso or "P")
    d, h, mi, se = (int(x or 0) for x in m.groups()) if m else (0, 0, 0, 0)
    return d * 86400 + h * 3600 + mi * 60 + se


def next_slot(y, exclude=None):
    """The day after the latest scheduled/published video OF THE SAME KIND, at the same time of day (UTC ISO).
    Shorts (≤ 3 min) and long videos (Parts) keep separate daily chains: a Part on 2 Oct must not push the next
    Short to 3 Oct and leave a gap in the Shorts tab (owner, 2026-10-01)."""
    vids = my_videos(y)
    me = next((v for v in vids if v["id"] == exclude), None)
    short = seconds(me["contentDetails"].get("duration")) <= 180 if me else True
    times = []
    for v in vids:
        if v["id"] == exclude or (seconds(v["contentDetails"].get("duration")) <= 180) != short:
            continue
        t = v["status"].get("publishAt") or v["snippet"]["publishedAt"]
        times.append(dt.datetime.fromisoformat(t.replace("Z", "+00:00")))
    last = max(times)
    slot = last + dt.timedelta(days=1)
    now = dt.datetime.now(dt.timezone.utc)
    while slot < now + dt.timedelta(hours=1):
        slot += dt.timedelta(days=1)
    return slot.strftime("%Y-%m-%dT%H:%M:%SZ"), last


def title(a):
    y = yt(a.channel)
    v = y.videos().list(part="snippet", id=a.video).execute(num_retries=3)["items"][0]
    snip = {k: v["snippet"][k] for k in ("title", "description", "tags", "categoryId", "defaultLanguage",
                                         "defaultAudioLanguage") if k in v["snippet"]}
    print(f"{v['snippet']['title']}\n→ {a.title}")
    if a.apply:
        snip["title"] = a.title
        y.videos().update(part="snippet", body={"id": a.video, "snippet": snip}).execute(num_retries=3)
        print("✅ title changed")
    else:
        print("dry run — add --apply")


def norm(t):
    return re.sub(r"[^a-z0-9]+", " ", t.lower()).strip()


def post_comments(a):
    """For videos that went public in the last few days: post the sheet's pinned-comment text as the channel (once).
    Pinning itself has no API — the owner taps ⋮ → Pin."""
    y = yt(a.channel)
    me = y.channels().list(part="id", mine=True).execute(num_retries=3)["items"][0]["id"]
    sheets = {}
    for f in (ROOT / "videos").glob("*-upload.md"):
        sh = f.read_text(encoding="utf-8")
        t, c = box(sh, "Title"), box(sh, "Pinned comment")
        if t and c:
            sheets[norm(t)] = (f.name, c.strip(), setting(sh, "Related video"))
    now = dt.datetime.now(dt.timezone.utc)
    for v in my_videos(y):
        if v["status"]["privacyStatus"] != "public":
            continue
        age = now - dt.datetime.fromisoformat(v["snippet"]["publishedAt"].replace("Z", "+00:00"))
        if age > dt.timedelta(days=a.days):
            continue
        hit = sheets.get(norm(v["snippet"]["title"]))
        if not hit:
            print(f"–  no sheet with this title: {v['snippet']['title']}")
            continue
        threads = y.commentThreads().list(part="snippet", videoId=v["id"], maxResults=100).execute(num_retries=3)["items"]
        if any(t["snippet"]["topLevelComment"]["snippet"].get("authorChannelId", {}).get("value") == me for t in threads):
            print(f"=  already commented: {v['snippet']['title']}")
            continue
        y.commentThreads().insert(part="snippet", body={"snippet": {"videoId": v["id"], "topLevelComment": {
            "snippet": {"textOriginal": hit[1]}}}}).execute(num_retries=3)
        day = re.search(r"Day (\d+)|Part (\d+)|Arabic Extras", v["snippet"]["title"])
        print(f"✅ comment posted on {v['snippet']['title']} → owner: ⋮ → Pin · Related video = {hit[2] or 'previous day'}"
              f" (only possible now that it's live)")
        print(f"NOTIFY {(day.group(0) if day else v['snippet']['title'][:30])} is live: pin the comment (⋮ → Pin) and set "
              f"Related video = {hit[2] or 'the previous day'}")


AR = re.compile("[\u0600-\u06ff]")
GENERIC_AR = ("شورتس", "فيرال", "ترند", "اكسبلور")   # generic Arabic reach tags → wrong audience (Arabic speakers)


def audit(a):
    """Every video on the channel against our upload + tag rules (weekly, in channel-review)."""
    y = yt(a.channel)
    vids = my_videos(y)
    in_pl = {}
    for p in y.playlists().list(part="snippet", mine=True, maxResults=50).execute(num_retries=3)["items"]:
        for i in y.playlistItems().list(part="snippet", playlistId=p["id"], maxResults=50).execute(num_retries=3)["items"]:
            if i["snippet"]["title"] in ("Deleted video", "Private video"):
                print(f"⚠️ placeholder '{i['snippet']['title']}' in playlist {p['snippet']['title']}")
            in_pl.setdefault(i["snippet"]["resourceId"]["videoId"], []).append(p["snippet"]["title"])
    bad = 0
    for v in sorted(vids, key=lambda v: v["status"].get("publishAt") or v["snippet"]["publishedAt"]):
        sn, st = v["snippet"], v["status"]
        tags = sn.get("tags", [])
        ar = [t for t in tags if AR.search(t)]
        caps = [c["snippet"]["language"] for c in y.captions().list(part="snippet", videoId=v["id"]).execute(num_retries=3)["items"]
                if c["snippet"]["trackKind"] == "standard"]
        issues = []
        if "#" in sn["title"]: issues.append("hashtag in title")
        if AR.search(sn["title"]): issues.append("Arabic script in title")
        if not 12 <= len(tags) <= 28: issues.append(f"{len(tags)} tags")
        if len(", ".join(tags)) > 480: issues.append("tags > 480 chars")
        if len(ar) < 5: issues.append(f"only {len(ar)} Arabic tags")
        if not any(AR.search(t) and re.search(r"[A-Za-z]", t) for t in tags): issues.append("no mixed 'X meaning' tag")
        if any(g in t for t in tags for g in GENERIC_AR): issues.append("generic Arabic reach tag")
        if AR.search(sn["description"]) and "\u2067" not in sn["description"]: issues.append("Arabic without direction isolates")
        if re.search("[\U0001F1E6-\U0001F1FF]", sn["description"] + sn["title"]): issues.append("flag emoji (renders outdated flags)")
        if sn.get("defaultLanguage") != "en": issues.append(f"title language {sn.get('defaultLanguage')}")
        if sn["categoryId"] != EDUCATION: issues.append("not Education")
        if st.get("selfDeclaredMadeForKids"): issues.append("made for kids")
        if "en" not in caps: issues.append("no English captions")
        if v["id"] not in in_pl: issues.append("in no playlist")
        bad += bool(issues)
        when = (st.get("publishAt") or sn["publishedAt"])[:10]
        print(f"{'⚠️' if issues else '✅'} {when} {sn['title'][:50]:50} {', '.join(issues) or 'ok'}")
    print(f"\n{len(vids) - bad}/{len(vids)} videos pass")


# ---------- fill: upload sheet → video ----------

def box(sheet, heading):
    m = re.search(rf"## {heading}.*?```\n(.*?)\n```", sheet, re.S)
    return m.group(1) if m else None


def setting(sheet, name):
    m = re.search(rf"^\|\s*\**{name}\**\s*\|\s*(.+?)\s*\|\s*$", sheet, re.M | re.I)
    return re.sub(r"\*", "", m.group(1)) if m else ""


def find(stem, suffix):
    hits = sorted((ROOT / "videos").glob(f"{stem}*{suffix}"))
    return hits[0] if hits else None


def fill(a):
    sheet_file = find(a.stem, "-upload.md")
    if not sheet_file:
        sys.exit(f"no upload sheet for {a.stem}")
    sheet = sheet_file.read_text(encoding="utf-8")
    desc_file = find(a.stem, "-description.txt")
    title = box(sheet, "Title")
    desc = desc_file.read_text(encoding="utf-8").strip() if desc_file else box(sheet, "Description")
    tags = [t.strip() for t in (box(sheet, "Tags") or "").split(",") if t.strip()]
    ai = setting(sheet, "AI use").lower().startswith("yes")
    playlist = setting(sheet, "Playlist")
    files = dict(re.findall(r"\*\*(Thumbnail|File to upload):\*\*[^`]*`([^`]+)`", sheet))
    thumb = ROOT / files["Thumbnail"] if "Thumbnail" in files else None
    srt = next(iter(re.findall(r"`(output/[^`]+captions-upload\.srt)`", sheet)), None)

    y = yt(a.channel)
    v = y.videos().list(part="snippet,status", id=a.video).execute(num_retries=3)["items"]
    if not v:
        sys.exit(f"video {a.video} not found on this channel")
    v = v[0]
    snip = dict(v["snippet"], title=title, description=desc, tags=tags, categoryId=EDUCATION,
                defaultLanguage="en", defaultAudioLanguage="en")
    snip.pop("thumbnails", None), snip.pop("localized", None)
    status = {k: v["status"][k] for k in ("privacyStatus", "embeddable", "license", "publicStatsViewable")
              if k in v["status"]}
    status.update(selfDeclaredMadeForKids=False, containsSyntheticMedia=ai, embeddable=True)
    if a.publish_at == "next":   # the day after the latest video, same time of day
        a.publish_at, last = next_slot(y, exclude=a.video)
        print(f"  latest video goes out {last:%Y-%m-%d %H:%M} UTC → this one {a.publish_at}")
    if a.publish_at:
        status.update(privacyStatus="private", publishAt=a.publish_at)

    print(f"{sheet_file.name} → {a.video} ({v['snippet']['title']})")
    print(f"  title: {title}\n  description: {len(desc)} chars · tags: {len(tags)} · category Education · English")
    print(f"  not made for kids · AI label: {'Yes' if ai else 'No'}"
          + (f" · scheduled {a.publish_at}" if a.publish_at else f" · stays {status['privacyStatus']}"))
    print(f"  thumbnail: {thumb.name if thumb and thumb.exists() else '—'} · captions: {srt or '—'} · playlist: {playlist or '—'}")
    if not a.apply:
        print("dry run — add --apply to write it")
        return
    from googleapiclient.http import MediaFileUpload
    y.videos().update(part="snippet,status", body={"id": a.video, "snippet": snip, "status": status}).execute(num_retries=3)
    print("  ✅ details + settings")
    if thumb and thumb.exists():
        y.thumbnails().set(videoId=a.video, media_body=MediaFileUpload(str(thumb))).execute(num_retries=3)
        print("  ✅ thumbnail")
    if srt and (ROOT / srt).exists():
        existing = y.captions().list(part="snippet", videoId=a.video).execute(num_retries=3)["items"]
        if not any(c["snippet"]["language"] == "en" and c["snippet"]["trackKind"] == "standard" for c in existing):
            y.captions().insert(part="snippet", body={"snippet": {"videoId": a.video, "language": "en",
                                                                  "name": "English", "isDraft": False}},
                                media_body=MediaFileUpload(str(ROOT / srt), mimetype="application/octet-stream")).execute(num_retries=3)
            print("  ✅ English captions")
        else:
            print("  = English captions already there")
    if playlist:
        name = re.sub(r"\s*\(.*?\)\s*$", "", playlist).strip()
        pls = y.playlists().list(part="snippet", mine=True, maxResults=50).execute(num_retries=3)["items"]
        pl = next((p for p in pls if p["snippet"]["title"].lower() == name.lower()), None)
        if pl is None:
            print(f"  ⚠️ playlist '{name}' not found — create it in Studio once, then re-run")
        else:
            inside = y.playlistItems().list(part="contentDetails", playlistId=pl["id"], maxResults=50).execute(num_retries=3)["items"]
            if a.video not in {i["contentDetails"]["videoId"] for i in inside}:
                y.playlistItems().insert(part="snippet", body={"snippet": {
                    "playlistId": pl["id"], "resourceId": {"kind": "youtube#video", "videoId": a.video}}}).execute(num_retries=3)
                print(f"  ✅ added to playlist '{name}'")
            else:
                print(f"  = already in playlist '{name}'")
    print("Left for Studio (no API): Education Type = Concept overview, Level = Beginner\n"
          "  · Automatic chapters ✅, places ❌, concepts ❌ · Parts: end screen/cards/quiz.\n"
          "  After it goes live (desktop notification): pin the comment + set Related video.")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--channel", default="arabic", help="token name: arabic (default) or spanish")
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("login").set_defaults(fn=login)
    sub.add_parser("videos").set_defaults(fn=videos)
    p = sub.add_parser("stats"); p.add_argument("--days", type=int, default=28); p.add_argument("--json", action="store_true"); p.set_defaults(fn=stats)
    p = sub.add_parser("retention"); p.add_argument("video"); p.set_defaults(fn=retention)
    p = sub.add_parser("search-terms"); p.add_argument("--days", type=int, default=28); p.set_defaults(fn=search_terms)
    p = sub.add_parser("comments"); p.add_argument("--max", type=int, default=50); p.set_defaults(fn=comments)
    sub.add_parser("audit").set_defaults(fn=audit)
    p = sub.add_parser("post-comments"); p.add_argument("--days", type=int, default=3); p.set_defaults(fn=post_comments)
    p = sub.add_parser("title"); p.add_argument("video"); p.add_argument("title"); p.add_argument("--apply", action="store_true"); p.set_defaults(fn=title)
    p = sub.add_parser("fill"); p.add_argument("stem"); p.add_argument("video")
    p.add_argument("--publish-at", help="ISO time, or 'next' = the day after the latest video"); p.add_argument("--apply", action="store_true"); p.set_defaults(fn=fill)
    a = ap.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()
