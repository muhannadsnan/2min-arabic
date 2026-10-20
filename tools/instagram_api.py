#!/usr/bin/env python3
"""Instagram (Instagram-login API) for @2minutearabic: stats, comments, posting Reels, token refresh.

    python3 tools/instagram_api.py media                 # posts with views / reach / likes / comments / shares / saves
    python3 tools/instagram_api.py comments              # recent comments on our posts
    python3 tools/instagram_api.py post VIDEO.mp4 --caption-file c.txt [--cover cover.jpg] [--apply]
                                                         # dry run uploads + checks, --apply publishes
    python3 tools/instagram_api.py refresh               # renew the 60-day token (cron, weekly)

Secrets (never in git): ~/.config/2min-instagram/app.json (Instagram app id + secret), token.json (long-lived token).
Instagram-login API needs public URLs → the files sit in the repo's ig-temp release for a few minutes. Dev-mode app.
"""
import argparse
import json
import pathlib
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

CONF = pathlib.Path.home() / ".config" / "2min-instagram"
API = "https://graph.instagram.com/v23.0/"


def token():
    import os
    if os.environ.get("IG_TOKEN"):   # GitHub Actions: the token comes from the repo's encrypted secrets
        return {"access_token": os.environ["IG_TOKEN"], "user_id": os.environ["IG_USER_ID"]}
    return json.loads((CONF / "token.json").read_text())


def call(path, method="GET", data=None, headers=None, raw=None, url=None, **q):
    q["access_token"] = token()["access_token"]
    u = url or (API + path + "?" + urllib.parse.urlencode(q))
    body = raw if raw is not None else (urllib.parse.urlencode(data).encode() if data else None)
    req = urllib.request.Request(u, data=body, method=method, headers=headers or {})
    for attempt in range(3):
        try:
            return json.load(urllib.request.urlopen(req, timeout=600))
        except urllib.error.HTTPError as e:
            err = json.loads(e.read() or b"{}")
            if e.code >= 500 and attempt < 2:
                time.sleep(5)
                continue
            sys.exit(f"Instagram API error {e.code}: {err.get('error', err)}")


def media(a):
    r = call("me/media", fields="id,caption,timestamp,like_count,comments_count,permalink", limit=a.limit)
    print("date        views  reach likes comm share saved  caption")
    for m in r.get("data", []):
        ins = call(f"{m['id']}/insights", metric="views,reach,shares,saved")
        v = {i["name"]: i["values"][0]["value"] for i in ins.get("data", [])}
        cap = (m.get("caption") or "").split("\n")[0][:50]
        print(f"{m['timestamp'][:10]}  {v.get('views', 0):>5} {v.get('reach', 0):>6} {m.get('like_count', 0):>5} "
              f"{m.get('comments_count', 0):>4} {v.get('shares', 0):>5} {v.get('saved', 0):>5}  {cap}")


def fbcall(path, method="GET", data=None, **q):
    """Instagram through the Facebook Page token (Facebook-login route, page linked 2026-10-20). The Instagram-login
    API hides other people's comments while the app is in development mode; this route returns them all."""
    c = json.loads((pathlib.Path.home() / ".config/2min-facebook/page.json").read_text())
    q["access_token"] = c["page_token"]
    req = urllib.request.Request("https://graph.facebook.com/v21.0/" + path + "?" + urllib.parse.urlencode(q),
                                 data=urllib.parse.urlencode(data).encode() if data else None, method=method)
    try:
        return json.load(urllib.request.urlopen(req, timeout=60))
    except urllib.error.HTTPError as e:
        sys.exit(f"Instagram (via Facebook) error {e.code}: {e.read().decode(errors='ignore')[:300]}")


def all_comments(limit):
    """Our posts with their comments (and replies) — via the Page token."""
    r = fbcall(f"{token()['user_id']}/media", limit=limit,
               fields="id,caption,comments_count,comments.limit(50){id,username,text,timestamp,replies{username,text}}")
    return r.get("data", [])


def comments(a):
    for m in all_comments(a.limit):
        for c in (m.get("comments") or {}).get("data", []):
            print(f"[{c['timestamp'][:10]}] {(m.get('caption') or '')[:28]!r} · @{c.get('username')}: {c['text']}")
            for x in (c.get("replies") or {}).get("data", []):
                print(f"      ↳ @{x.get('username')}: {x.get('text')}")


REPLIES = pathlib.Path.home() / ".local/share/2min-yt/replies.jsonl"


def pending_comments(a):
    """Instagram comments still needing an answer (owner 2026-10-19): not ours, no reply from us, not answered before."""
    me = token().get("username") or "2minutearabic"
    done = {json.loads(l).get("parent") for l in REPLIES.read_text().splitlines() if l.strip()} if REPLIES.exists() else set()
    for m in all_comments(a.limit):
        cs = (m.get("comments") or {}).get("data", [])
        for c in cs:
            if c.get("username") == me or c["id"] in done: continue
            if any(x.get("username") == me for x in (c.get("replies") or {}).get("data", [])): continue
            # answered with a top-level "@user …" comment (the app's old way) counts as answered too
            if any(o.get("username") == me and f"@{c.get('username')}" in o.get("text", "") and o["timestamp"] > c["timestamp"]
                   for o in cs): continue
            print(json.dumps({"platform": "instagram", "id": c["id"], "video": (m.get("caption") or "")[:60],
                              "author": c.get("username"), "text": c["text"], "date": c["timestamp"][:10]}, ensure_ascii=False))


def reply(a):
    """Reply to an Instagram comment (Page token, instagram_manage_comments) and log it."""
    r = fbcall(f"{a.comment}/replies", method="POST", data={"message": a.text})
    with REPLIES.open("a") as f:
        f.write(json.dumps({"platform": "instagram", "parent": a.comment, "reply_id": r.get("id"), "text": a.text,
                            "at": time.strftime("%Y-%m-%dT%H:%M:%S")}, ensure_ascii=False) + "\n")
    print(f"✅ replied to {a.comment}: {a.text}")


REPO, BUFFER = "muhannadsnan/2min-arabic", "ig-temp"   # public release used as a short-lived download link


def gh(*args):
    import subprocess
    subprocess.run(["gh", *args], check=True, capture_output=True, cwd=pathlib.Path(__file__).resolve().parent.parent)


def post(a):
    """Instagram-login API needs public URLs: the video (and cover) go to the ig-temp release for a few minutes,
    Instagram fetches them, then they're deleted again (owner approved 2026-10-15)."""
    import shutil, tempfile
    video = pathlib.Path(a.video)
    caption = pathlib.Path(a.caption_file).read_text(encoding="utf-8").strip()
    if len(caption) > 2200:
        sys.exit(f"caption too long ({len(caption)} > 2200)")
    me = token()["user_id"]
    tmp = pathlib.Path(tempfile.mkdtemp())
    names = {"video": f"reel-{int(time.time())}.mp4"}
    shutil.copy(video, tmp / names["video"])
    if a.cover:
        names["cover"] = names["video"].replace(".mp4", "-cover.jpg")
        shutil.copy(a.cover, tmp / names["cover"])
    url = lambda n: f"https://github.com/{REPO}/releases/download/{BUFFER}/{n}"
    gh("release", "upload", BUFFER, *[str(tmp / n) for n in names.values()], "--clobber", "-R", REPO)
    try:
        params = {"media_type": "REELS", "video_url": url(names["video"]), "caption": caption, "share_to_feed": "true"}
        if a.cover:
            params["cover_url"] = url(names["cover"])
        if getattr(a, "trial", False):   # Trial Reel: shown to non-followers only, graduates by hand in the app
            params["trial_params"] = json.dumps({"graduation_strategy": "MANUAL"})
        cid = call(f"{me}/media", method="POST", data={"_": "1"}, **params)["id"]
        for _ in range(60):
            st = call(cid, fields="status_code,status")
            if st.get("status_code") == "FINISHED":
                break
            if st.get("status_code") == "ERROR":
                sys.exit(f"processing failed: {st.get('status')}")
            time.sleep(10)
        else:
            sys.exit("still processing after 10 min")
        print(f"✅ fetched + processed by Instagram, container {cid}")
        if not a.apply:
            print("dry run — not published (the container expires by itself in 24 h). Add --apply to publish.")
            return
        pid = call(f"{me}/media_publish", method="POST", data={"creation_id": cid})["id"]
        print(f"✅ published: {call(pid, fields='permalink').get('permalink')}")
    finally:
        for n in names.values():
            gh("release", "delete-asset", BUFFER, n, "-y", "-R", REPO)
        shutil.rmtree(tmp, ignore_errors=True)


def refresh(a):
    t = token()
    r = json.load(urllib.request.urlopen("https://graph.instagram.com/refresh_access_token?" + urllib.parse.urlencode(
        {"grant_type": "ig_refresh_token", "access_token": t["access_token"]}), timeout=30))
    t.update(access_token=r["access_token"], saved=int(time.time()))
    f = CONF / "token.json"
    f.write_text(json.dumps(t))
    f.chmod(0o600)
    print(f"token renewed: valid {r.get('expires_in', 0) // 86400} days")


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(required=True)
    p = sub.add_parser("media"); p.add_argument("--limit", type=int, default=20); p.set_defaults(fn=media)
    p = sub.add_parser("comments"); p.add_argument("--limit", type=int, default=20); p.set_defaults(fn=comments)
    p = sub.add_parser("pending-comments"); p.add_argument("--limit", type=int, default=25); p.set_defaults(fn=pending_comments)
    p = sub.add_parser("reply"); p.add_argument("comment"); p.add_argument("text"); p.set_defaults(fn=reply)
    p = sub.add_parser("post"); p.add_argument("video"); p.add_argument("--caption-file", required=True)
    p.add_argument("--cover"); p.add_argument("--apply", action="store_true")
    p.add_argument("--trial", action="store_true", help="Trial Reel: non-followers only (owner 2026-10-18 test)"); p.set_defaults(fn=post)
    sub.add_parser("refresh").set_defaults(fn=refresh)
    a = ap.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()
