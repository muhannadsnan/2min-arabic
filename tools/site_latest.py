#!/usr/bin/env python3
"""The website's start page with the newest lessons on top (owner 2026-10-30: the Instagram bio link goes here, so
"Full lesson: Day N — link in bio" is one tap away; the channel page has no "start here" and no PDFs).

    python3 tools/site_latest.py [--push]        (GitHub: .github/workflows/site-latest.yml, 15:25 + 17:25 Oslo)

Builds index.html for the gh-pages branch: the 3 newest public videos (thumbnail + title, youtu.be link), "Start from
Day 1" (the 30-day playlist), the free PDFs, Instagram + YouTube, and the "About 2min tools" box Google's app check
reads. --push commits it to gh-pages (a temporary worktree) and pushes. Runs on GitHub, not on the laptop (owner
2026-10-30: "not connected to PC working time"); YouTube data from the public feed, the Instagram list from data/.
"""
import html
import pathlib
import subprocess
import sys
import tempfile

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import json, re, urllib.request   # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parent.parent
PLAYLIST = "https://www.youtube.com/playlist?list=PLUw_4McNI7-w"
DAY1 = "https://youtu.be/XTQXhypYDLU"


CHANNEL = "UCSPLk1XgELl4vkPFi_hDszA"


def feed():
    """YouTube's public feed (no login, works on GitHub): the 15 newest public videos, newest first."""
    x = urllib.request.urlopen(f"https://www.youtube.com/feeds/videos.xml?channel_id={CHANNEL}", timeout=60).read().decode()
    return re.findall(r"<yt:videoId>([\w-]{11})</yt:videoId>\s*<yt:channelId>[^<]*</yt:channelId>\s*<title>([^<]*)</title>", x)


def title(vid, known):
    if vid in known: return known[vid]
    try:   # older than the feed: YouTube's public oEmbed
        return json.load(urllib.request.urlopen(f"https://www.youtube.com/oembed?url=https://youtu.be/{vid}&format=json", timeout=30))["title"]
    except Exception:
        return None


def newest(n=3):
    return [(i, html.unescape(t)) for i, t in feed()[:n]]


def on_instagram(n=3):
    """The videos of the newest Instagram Reels (Instagram runs ~9 days behind YouTube): ig-queued.txt lists every queued
    video in order; the ones still waiting in the ig-queue release are the last lines."""
    q = ROOT / "data" / "ig-queued.txt"
    ids = [l.strip() for l in q.read_text().splitlines() if l.strip()] if q.exists() else []
    r = subprocess.run(["gh", "release", "view", "ig-queue", "--json", "assets", "--jq", ".assets[].name"],
                       cwd=ROOT, capture_output=True, text=True)
    waiting = sum(1 for a in r.stdout.split() if a.startswith("reel-"))
    posted = ids[:len(ids) - waiting] if waiting else ids
    want = posted[-n:][::-1]
    if not want: return []
    known = {i: html.unescape(t) for i, t in feed()}
    return [(i, t) for i in want if (t := title(i, known))]


def cards_html(items):
    return "".join(
        f'<a class="vid" href="https://youtu.be/{i}"><img src="https://i.ytimg.com/vi/{i}/hqdefault.jpg" alt="" loading="lazy">'
        f'<span>{html.escape(t.split(" | ")[0])}<small>{html.escape(t.split(" | ")[1]) if " | " in t else ""}</small></span></a>'
        for i, t in items)


def page(latest, insta):
    cards, ig = cards_html(latest), cards_html(insta)
    igbox = f'<section class="card"><h2>From our Instagram this week</h2><div class="vids">{ig}</div></section>' if insta else ""
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin><link href="https://fonts.googleapis.com/css2?family=Noto+Naskh+Arabic:wght@700&family=Noto+Sans:wght@400;700&display=swap" rel="stylesheet"><link rel="stylesheet" href="style.css">
<style>.vids{{display:grid;gap:12px}}.vid{{display:flex;gap:14px;align-items:center;text-decoration:none;color:var(--ink);border:1px solid var(--line);border-radius:14px;padding:8px;background:var(--bg)}}.vid img{{width:120px;aspect-ratio:16/9;object-fit:cover;border-radius:10px;flex:none}}.vid span{{font-weight:700;line-height:1.3}}.vid small{{display:block;font-weight:400;color:var(--muted);margin-top:4px}}.vid:first-child{{border-color:var(--terra)}}</style>
<title>2 Minute Arabic</title><meta name="description" content="Learn Arabic two minutes a day. Your first Arabic conversation in 30 days."></head><body>
<header><div class="wrap"><span class="badge">2 MINUTE ARABIC</span><h1><span class="nw">Learn Arabic</span><br><span class="nw">2 minutes a day</span></h1><p class="ar" lang="ar" dir="rtl">مَرْحَبًا</p><p class="tag">Your first Arabic conversation in 30 days.</p></div></header>
<main class="wrap">
<section class="card"><h2>Newest lessons</h2><div class="vids">{cards}</div></section>
{igbox}
<section class="card"><h2>New here? Start from Day 1</h2><p>Two minutes a day, in order: real phrases, little stories and simple grammar for complete beginners.</p>
<div class="links"><a class="btn" href="{DAY1}">▶ Day 1</a><a class="btn alt" href="{PLAYLIST}">All 30 days</a></div></section>
<section class="card"><h2>Free downloads</h2><p>Every word of the course as a printable PDF: Arabic, transliteration and English.</p><div class="links"><a class="btn" href="free/">Free PDFs</a></div></section>
<section class="card"><h2>Follow</h2><div class="links"><a class="btn" href="https://www.youtube.com/@2MinArabic">▶ YouTube</a><a class="btn alt" href="https://www.instagram.com/2minutearabic/">Instagram</a></div></section>
<section class="card"><h2>About “2min tools”</h2><p>“2min tools” is a small private tool used only by the channel owner to manage his own YouTube channel: lesson details, subtitles, schedules and the channel's own statistics. It is not offered to anyone else.</p><p><a href="privacy.html">Read the privacy policy →</a></p></section>
</main><footer><div class="wrap"><a href="index.html">Home</a>·<a href="privacy.html">Privacy policy</a>·<a href="https://www.youtube.com/@2MinArabic">YouTube</a>·<a href="https://www.instagram.com/2minutearabic/">Instagram</a><p>© 2026 2 Minute Arabic</p></div></footer></body></html>
"""


def main():
    latest, insta = newest(), on_instagram()
    out = page(latest, insta)
    print("\n".join(f"  {i}  {t}" for i, t in latest + [("IG", "")] + insta))
    if "--push" not in sys.argv:
        (pathlib.Path(tempfile.gettempdir()) / "site-index.html").write_text(out, encoding="utf-8"); return
    wt = pathlib.Path(tempfile.mkdtemp()) / "gh"
    run = lambda *a, **k: subprocess.run(a, cwd=k.get("cwd", ROOT), check=True, capture_output=True, text=True)
    run("git", "fetch", "-q", "origin", "gh-pages")
    run("git", "worktree", "add", "--detach", str(wt), "origin/gh-pages")
    try:
        f = wt / "index.html"
        if f.read_text(encoding="utf-8") == out:
            print("no change"); return
        f.write_text(out, encoding="utf-8")
        run("git", "add", "index.html", cwd=wt)
        run("git", "commit", "-m", f"Newest lessons: {latest[0][1].split(' | ')[0]}", cwd=wt)
        run("git", "push", "-q", "origin", "HEAD:gh-pages", cwd=wt)
        print("pushed")
    finally:
        run("git", "worktree", "remove", "--force", str(wt))


if __name__ == "__main__":
    main()
