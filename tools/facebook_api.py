#!/usr/bin/env python3
"""Post to the Facebook Page "2 Minute Arabic" (owner, 2026-10-20): the same videos as Instagram, uploaded natively.

    python3 tools/facebook_api.py reel <video.mp4> --caption-file <txt>     # one video (a Reel; longer ones as a video)
    python3 tools/facebook_api.py backfill [--gap 300] [--apply]            # every Instagram post so far, oldest first

Credentials: env FB_PAGE_ID + FB_PAGE_TOKEN (GitHub secrets) or ~/.config/2min-facebook/page.json (tools/fb_page_setup.py).
Videos up to 90 s go up as Facebook Reels (video_reels API); longer ones as a Page video (Facebook shows those as reels
too). The backfill downloads each Instagram post through the Instagram API (exact same file and caption), skips Trial
Reels (not shared to the profile) and anything already posted (log: ~/.local/share/2min-yt/facebook.jsonl).
"""
import argparse, json, os, pathlib, subprocess, sys, tempfile, time, urllib.parse, urllib.request

GRAPH = "https://graph.facebook.com/v21.0"
LOG = pathlib.Path.home() / ".local/share/2min-yt/facebook.jsonl"


def creds():
    if os.environ.get("FB_PAGE_TOKEN"):
        return os.environ["FB_PAGE_ID"], os.environ["FB_PAGE_TOKEN"]
    c = json.loads((pathlib.Path.home() / ".config/2min-facebook/page.json").read_text())
    return c["page_id"], c["page_token"]


def req(url, data=None, headers=None, method=None):
    body = urllib.parse.urlencode(data).encode() if isinstance(data, dict) else data
    r = urllib.request.Request(url, data=body, headers=headers or {}, method=method or ("POST" if data is not None else "GET"))
    try:
        with urllib.request.urlopen(r, timeout=300) as resp:
            return json.load(resp)
    except urllib.error.HTTPError as e:
        sys.exit(f"Facebook error {e.code}: {e.read().decode(errors='ignore')[:400]}")


def duration(path):
    import shutil
    if not shutil.which("ffprobe"): return 9999.0   # unknown length (e.g. on GitHub) → the normal video upload, any length
    return float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(path)],
                                capture_output=True, text=True).stdout or 0)


def post_video(path, caption):
    """Upload a local video to the Page; returns the Facebook video id."""
    pid, tok = creds(); path = pathlib.Path(path); size = path.stat().st_size
    if duration(path) <= 90:
        start = req(f"{GRAPH}/{pid}/video_reels", {"upload_phase": "start", "access_token": tok})
        vid = start["video_id"]
        req(f"https://rupload.facebook.com/video-upload/v21.0/{vid}", path.read_bytes(),
            {"Authorization": f"OAuth {tok}", "offset": "0", "file_size": str(size)})
        req(f"{GRAPH}/{pid}/video_reels", {"upload_phase": "finish", "video_id": vid, "video_state": "PUBLISHED",
                                           "description": caption, "access_token": tok})
    else:   # longer than a Reel allows: a normal Page video (multipart upload)
        r = subprocess.run(["curl", "-s", "-F", f"access_token={tok}", "-F", f"description={caption}",
                            "-F", f"source=@{path}", f"https://graph-video.facebook.com/v21.0/{pid}/videos"],
                           capture_output=True, text=True)
        out = json.loads(r.stdout or "{}")
        if "id" not in out: sys.exit(f"Facebook video upload failed: {r.stdout[:300]}")
        vid = out["id"]
    return vid


def post_photo(url, caption):
    pid, tok = creds()
    return req(f"{GRAPH}/{pid}/photos", {"url": url, "caption": caption, "access_token": tok})["id"]


def log(entry):
    LOG.parent.mkdir(parents=True, exist_ok=True)
    with LOG.open("a") as f: f.write(json.dumps(entry, ensure_ascii=False) + "\n")


def reel(a):
    caption = pathlib.Path(a.caption_file).read_text(encoding="utf-8").strip()
    vid = post_video(a.video, caption); log({"fb": vid, "source": str(a.video), "at": time.strftime("%Y-%m-%dT%H:%M:%S")})
    print(f"✅ Facebook: {vid}")


def backfill(a):
    sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent)); import instagram_api as ig
    done = {json.loads(l).get("ig") for l in LOG.read_text().splitlines() if l.strip()} if LOG.exists() else set()
    items = ig.call("me/media", fields="id,media_type,media_product_type,is_shared_to_feed,caption,media_url,timestamp",
                    limit=50).get("data", [])
    items = [m for m in reversed(items) if m.get("is_shared_to_feed") is not False and m["id"] not in done]
    print(f"{len(items)} Instagram posts to bring to Facebook, oldest first")
    for i, m in enumerate(items):
        cap = (m.get("caption") or "").strip()
        print(f"  {m['timestamp'][:10]} {m['media_type']:5} {cap.splitlines()[0][:60] if cap else ''}")
        if not a.apply: continue
        if m["media_type"] == "VIDEO":
            tmp = pathlib.Path(tempfile.mkdtemp()) / "v.mp4"
            urllib.request.urlretrieve(m["media_url"], tmp)
            fb = post_video(tmp, cap); tmp.unlink()
        elif m["media_type"] == "IMAGE":
            fb = post_photo(m["media_url"], cap)
        elif m["media_type"] == "CAROUSEL_ALBUM":   # one Facebook post with all the photos
            pid, tok = creds()
            kids = ig.call(f"{m['id']}/children", fields="media_type,media_url").get("data", [])
            ids = [req(f"{GRAPH}/{pid}/photos", {"url": k["media_url"], "published": "false", "access_token": tok})["id"]
                   for k in kids if k["media_type"] == "IMAGE"]
            data = {"message": cap, "access_token": tok}
            for j, x in enumerate(ids): data[f"attached_media[{j}]"] = json.dumps({"media_fbid": x})
            fb = req(f"{GRAPH}/{pid}/feed", data)["id"]
        else:
            print("    skipped"); continue
        log({"ig": m["id"], "fb": fb, "at": time.strftime("%Y-%m-%dT%H:%M:%S")}); print(f"    ✅ Facebook {fb}")
        if i < len(items) - 1: time.sleep(a.gap)
    if not a.apply: print("dry run — add --apply to post")


def main():
    ap = argparse.ArgumentParser(); sub = ap.add_subparsers(required=True)
    p = sub.add_parser("reel"); p.add_argument("video"); p.add_argument("--caption-file", required=True); p.set_defaults(fn=reel)
    p = sub.add_parser("backfill"); p.add_argument("--gap", type=int, default=300); p.add_argument("--apply", action="store_true")
    p.set_defaults(fn=backfill)
    a = ap.parse_args(); a.fn(a)


if __name__ == "__main__":
    main()
