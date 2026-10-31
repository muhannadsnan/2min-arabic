#!/usr/bin/env python3
"""One proven Instagram hit a day on the Facebook Page (owner 2026-10-31: "start publishing with the best videos we
have, then the next one"). Every Reel posted to the Page before the Meta app went Live (30 Oct 2026) was only
visible to app roles, so Facebook has never shown our best videos to anyone.

    python3 tools/fb_hits.py [--dry-run]     # GitHub: .github/workflows/facebook-hits.yml, 12:00 Oslo

Takes the first line of data/fb-hits.txt (Instagram media id, best first), downloads that Reel and its caption
through the Instagram API, posts it to the Page and removes the line (the workflow commits the file).
"""
import datetime
import pathlib
import sys
import tempfile
import urllib.request
from zoneinfo import ZoneInfo

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import facebook_api as fb    # noqa: E402
import instagram_api as ig   # noqa: E402

LIST = pathlib.Path(__file__).resolve().parent.parent / "data" / "fb-hits.txt"


def main():
    lines = LIST.read_text(encoding="utf-8").splitlines()
    # GitHub starts scheduled runs late or skips them (31 Oct: 5 h late) → the workflow runs several times a day and
    # only the first one posts: "# last posted: YYYY-MM-DD" (Oslo date) in the list
    today = f"# last posted: {datetime.datetime.now(ZoneInfo('Europe/Oslo')):%Y-%m-%d}"
    if today in lines and "--force" not in sys.argv:
        print(f"already posted today ({today[16:]})"); return
    todo = [i for i, l in enumerate(lines) if l.strip() and not l.startswith("#")]
    if not todo:
        print("fb-hits.txt is empty — nothing to post"); return
    i = todo[0]; mid = lines[i].split()[0]
    m = ig.call(mid, fields="media_url,caption,timestamp")
    cap = (m.get("caption") or "").strip()
    print(f"{mid}: {cap.splitlines()[0][:80] if cap else ''}")
    if "--dry-run" in sys.argv:
        print("dry run"); return
    tmp = pathlib.Path(tempfile.mkdtemp()) / "v.mp4"
    urllib.request.urlretrieve(m["media_url"], tmp)
    vid = fb.post_video(tmp, cap)
    print(f"✅ Facebook: {vid} · {len(todo) - 1} hits left")
    del lines[i]
    lines = [l for l in lines if not l.startswith("# last posted:")] + [today]
    LIST.write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
