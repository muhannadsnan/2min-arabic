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
    """YouTube-style cards: the big 16:9 thumbnail YouTube itself shows (the Short with blurred sides), title below."""
    out = []
    for i, t in items:
        title, cat = (t.split(" | ") + [""])[:2]
        out.append(f'<a class="yt-card" href="https://youtu.be/{i}"><div class="thumb"><img src="https://i.ytimg.com/vi/{i}/maxresdefault.jpg" '
                   f'alt="" loading="lazy"><span class="play"></span></div><b>{html.escape(title)}</b><small>{html.escape(cat)}</small></a>')
    return "".join(out)


def reels_html(items):
    """Instagram-style Reels grid: three vertical tiles — the centre of YouTube's 16:9 thumbnail is exactly our vertical
    custom thumbnail (oardefault shows YouTube's own frame grab instead), play icon, label as tooltip."""
    out = []
    for i, t in items:
        label = t.split(" | ")[0]
        out.append(f'<a class="reel" href="https://youtu.be/{i}" title="{html.escape(label)}"><img src="https://i.ytimg.com/vi/{i}/maxresdefault.jpg" '
                   f'alt="{html.escape(label)}" loading="lazy"><svg viewBox="0 0 24 24" aria-hidden="true"><path fill="#fff" d="M8 5v14l11-7z"/></svg></a>')
    return "".join(out)


def page(latest, insta):
    cards, ig = cards_html(latest), reels_html(insta)
    igbox = (f'<section class="card ig"><h2 class="sh"><svg class="logo" viewBox="0 0 24 24" aria-hidden="true"><defs><radialGradient id="igg" cx="30%" cy="107%" r="150%"><stop offset="0" stop-color="#fdf497"/><stop offset=".45" stop-color="#fd5949"/><stop offset=".6" stop-color="#d6249f"/><stop offset=".9" stop-color="#285AEB"/></radialGradient></defs><rect x="1" y="1" width="22" height="22" rx="6" fill="url(#igg)"/><rect x="5" y="5" width="14" height="14" rx="4" fill="none" stroke="#fff" stroke-width="1.8"/><circle cx="12" cy="12" r="3.3" fill="none" stroke="#fff" stroke-width="1.8"/><circle cx="16.3" cy="7.7" r="1" fill="#fff"/></svg>On Instagram this week</h2><p class="muted">Tap a Reel for the full lesson on YouTube.</p>'
             f'<div class="reels">{ig}</div></section>') if insta else ""
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin><link href="https://fonts.googleapis.com/css2?family=Noto+Naskh+Arabic:wght@700&family=Noto+Sans:wght@400;700&display=swap" rel="stylesheet"><link rel="stylesheet" href="style.css">
<style>
.sh{{display:flex;align-items:center;gap:10px}}.sh .logo{{width:30px;height:30px;flex:none}}
.ytrow{{display:flex;gap:14px;overflow-x:auto;scroll-snap-type:x mandatory;padding-bottom:6px;margin:0 -4px;-webkit-overflow-scrolling:touch}}.ytrow .yt-card{{flex:0 0 78%;scroll-snap-align:start}}@media (min-width:640px){{.ytrow .yt-card{{flex-basis:46%}}}}
.yt-card{{text-decoration:none;color:var(--ink);display:block}}.yt-card b{{display:block;margin-top:10px;line-height:1.3;font-size:1.05rem}}.yt-card small{{color:var(--muted)}}
.thumb{{position:relative;border-radius:14px;overflow:hidden;aspect-ratio:16/9;background:#000}}.thumb img{{width:100%;height:100%;object-fit:cover;display:block;transition:transform .2s}}.yt-card:hover img{{transform:scale(1.03)}}
.play{{position:absolute;left:10px;bottom:10px;width:44px;height:31px;background:#ff0000;border-radius:9px;box-shadow:0 2px 6px rgba(0,0,0,.4)}}.play:after{{content:"";position:absolute;left:17px;top:9px;border-style:solid;border-width:6.5px 0 6.5px 11px;border-color:transparent transparent transparent #fff}}
.reels{{display:grid;grid-template-columns:repeat(3,1fr);gap:6px;margin-top:8px}}.reel{{position:relative;aspect-ratio:9/16;border-radius:10px;overflow:hidden;display:block}}.reel img{{position:absolute;top:0;left:50%;height:100%;width:auto;transform:translateX(-50%);display:block}}.reel svg{{position:absolute;top:8px;right:8px;width:26px;height:26px;filter:drop-shadow(0 1px 2px rgba(0,0,0,.6))}}
.ig{{border:2px solid transparent;background:linear-gradient(var(--card),var(--card)) padding-box,linear-gradient(45deg,#f58529,#dd2a7b,#8134af,#515bd4) border-box}}
.ig h2{{background:linear-gradient(90deg,#f58529,#dd2a7b,#8134af);-webkit-background-clip:text;background-clip:text;color:transparent}}
.start{{position:relative;border:2px solid transparent;background:linear-gradient(var(--card),var(--card)) padding-box,linear-gradient(120deg,var(--gold),var(--terra),var(--teal),var(--gold)) border-box;background-size:100% 100%,300% 300%;animation:glowmove 6s ease infinite,pulse 2.8s ease-in-out infinite}}
.start h2{{font-size:1.45rem}}
@keyframes glowmove{{0%,100%{{background-position:0 0,0% 50%}}50%{{background-position:0 0,100% 50%}}}}
@keyframes pulse{{0%,100%{{box-shadow:0 0 0 rgba(242,193,78,0)}}50%{{box-shadow:0 0 28px rgba(242,193,78,.45)}}}}
@media (prefers-reduced-motion:reduce){{.start{{animation:none}}}}
.free{{position:relative;overflow:hidden;background:linear-gradient(135deg,#fff3c4,#f2c14e);border:none;color:#2b2b2b}}
.free h2{{color:#1f5f5b}}.free p{{color:#3a3328}}
.free .seal{{position:absolute;top:14px;right:14px;width:78px;height:78px;border-radius:50%;background:#c0633a;color:#fff;display:flex;flex-direction:column;align-items:center;justify-content:center;transform:rotate(-12deg);box-shadow:0 4px 12px rgba(120,50,20,.35);outline:2px dashed rgba(255,255,255,.75);outline-offset:-7px;line-height:1}}
.free .seal b{{font-size:1.15rem;letter-spacing:.06em}}.free .seal small{{font-size:.62rem;letter-spacing:.08em;margin-top:3px;opacity:.95}}
.free h2{{padding-right:84px;min-height:58px}}
.free .row{{display:flex;gap:18px;align-items:center}}.free svg{{flex:none;width:64px;height:64px}}
.free .btn{{background:#1f5f5b}}
.follow{{display:grid;grid-template-columns:1fr 1fr;gap:14px;margin-top:6px}}
.social{{display:flex;flex-direction:column;align-items:center;justify-content:center;gap:8px;padding:22px 10px;border-radius:18px;text-decoration:none;color:#fff;font-weight:800;font-size:1.45rem;transition:transform .15s}}
.social:hover{{transform:translateY(-3px)}}.social svg{{width:64px;height:64px}}
.yt{{background:#ff0000}}.insta{{background:radial-gradient(circle at 30% 107%,#fdf497 0%,#fd5949 45%,#d6249f 60%,#285AEB 90%)}}
.social small{{font-weight:700;opacity:.95;font-size:1rem;text-align:center;line-height:1.3}}
header .badge{{font-size:1.6rem;padding:8px 28px}}
footer .tool{{max-width:560px;margin:10px auto 0;font-size:.8rem;opacity:.8}}
</style>
<title>2 Minute Arabic</title><meta name="description" content="Become fluent in Arabic, two minutes a day. Your first Arabic conversation in 30 days."></head><body>
<header><div class="wrap"><span class="badge">2 MINUTE ARABIC</span><h1><span class="nw">Become fluent in Arabic,</span><br><span class="nw">2 minutes a day</span></h1><p class="ar" lang="ar" dir="rtl">مَرْحَبًا</p><p class="tag">Your first Arabic conversation in 30 days.</p></div></header>
<main class="wrap">
<section class="card"><h2 class="sh"><svg class="logo" viewBox="0 0 24 24" aria-hidden="true"><path fill="#ff0000" d="M23.5 6.2a3 3 0 0 0-2.1-2.1C19.5 3.6 12 3.6 12 3.6s-7.5 0-9.4.5A3 3 0 0 0 .5 6.2 31 31 0 0 0 0 12a31 31 0 0 0 .5 5.8 3 3 0 0 0 2.1 2.1c1.9.5 9.4.5 9.4.5s7.5 0 9.4-.5a3 3 0 0 0 2.1-2.1A31 31 0 0 0 24 12a31 31 0 0 0-.5-5.8z"/><path fill="#fff" d="M9.6 15.6 15.8 12 9.6 8.4z"/></svg>Newest lessons on YouTube</h2><div class="ytrow">{cards}</div></section>
{igbox}
<section class="card start"><h2>✨ New here? Start here</h2><p>Two minutes a day, in order: real phrases, little stories and simple grammar for complete beginners.</p>
<div class="links"><a class="btn" href="{DAY1}">▶ Start Day 1</a><a class="btn alt" href="{PLAYLIST}">All 30 days</a></div></section>
<section class="card free"><span class="seal"><b>FREE</b><small>PDF</small></span><div class="row"><svg viewBox="0 0 64 64" aria-hidden="true"><path d="M14 4h26l12 12v42a2 2 0 0 1-2 2H14a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2z" fill="#fff"/><path d="M40 4v12h12" fill="#e9dcc0"/><rect x="18" y="34" width="28" height="14" rx="3" fill="#c0633a"/><text x="32" y="45" text-anchor="middle" font-family="Noto Sans,sans-serif" font-weight="700" font-size="10" fill="#fff">PDF</text><rect x="18" y="20" width="22" height="3" rx="1.5" fill="#1f5f5b"/><rect x="18" y="26" width="16" height="3" rx="1.5" fill="#1f5f5b"/></svg>
<div><h2>Free downloads</h2><p>Every word of the course as a printable PDF: Arabic, transliteration and English.</p></div></div>
<div class="links"><a class="btn" href="free/">⬇ Get the free PDFs</a></div></section>
<section class="card"><h2>Follow</h2><div class="follow">
<a class="social yt" href="https://www.youtube.com/@2MinArabic"><svg viewBox="0 0 24 24" aria-hidden="true"><path fill="#fff" d="M23.5 6.2a3 3 0 0 0-2.1-2.1C19.5 3.6 12 3.6 12 3.6s-7.5 0-9.4.5A3 3 0 0 0 .5 6.2 31 31 0 0 0 0 12a31 31 0 0 0 .5 5.8 3 3 0 0 0 2.1 2.1c1.9.5 9.4.5 9.4.5s7.5 0 9.4-.5a3 3 0 0 0 2.1-2.1A31 31 0 0 0 24 12a31 31 0 0 0-.5-5.8z"/><path fill="#ff0000" d="M9.6 15.6 15.8 12 9.6 8.4z"/></svg>YouTube<small>daily lessons + full course</small></a>
<a class="social insta" href="https://www.instagram.com/2minutearabic/"><svg viewBox="0 0 24 24" aria-hidden="true"><rect x="2" y="2" width="20" height="20" rx="6" fill="none" stroke="#fff" stroke-width="2"/><circle cx="12" cy="12" r="4.6" fill="none" stroke="#fff" stroke-width="2"/><circle cx="17.6" cy="6.4" r="1.4" fill="#fff"/></svg>Instagram<small>a new lesson every day</small></a>
</div></section>
</main><footer><div class="wrap"><a href="index.html">Home</a>·<a href="privacy.html">Privacy policy</a>·<a href="terms.html">Terms</a><p>© 2026 2 Minute Arabic</p>
<p class="tool">“2min tools” is the channel's own private helper for its YouTube, Instagram and Facebook accounts (lesson details, subtitles, schedules, the channel's own statistics). It is not offered to anyone else. <a href="privacy.html">Privacy policy</a></p></div></footer></body></html>
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
