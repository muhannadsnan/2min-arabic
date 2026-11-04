#!/usr/bin/env python3
"""The YouTube Post that goes with each Instagram carousel (owner 2026-11-04: "the same post, all 3 synced with the
Instagram carousel"). Instagram and the Facebook Page get the carousel automatically (instagram-carousel.yml, Wed +
Sun 19:00); the YouTube Post is made by hand in Studio (the API can't create Posts), so the groups page shows it as a
card on its day with the text to copy, and the pictures wait in ~/Downloads/yt-posts/<day>-<stem>/.

    python3 tools/yt_post.py output/carousel/<stem> [--date YYYY-MM-DD]

Without --date: the next Wed/Sun after the last scheduled post (the carousel queue posts one per Wed/Sun in order).
ig_carousel_add.py --apply calls this. Slides: all but the closing one (it says "link in bio", Instagram only).
"""
import datetime, json, pathlib, re, shutil, subprocess, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
DATA = ROOT / "data" / "yt-posts.json"
OUT = pathlib.Path.home() / "Downloads" / "yt-posts"
Y = pathlib.Path.home() / ".local/share/2min-yt/venv/bin/python"


def next_day(after):
    d = after + datetime.timedelta(days=1)
    while d.weekday() not in (2, 6): d += datetime.timedelta(days=1)   # Wed, Sun
    return d


def video_url(title):
    """The full lesson's link, by its title (the carousel caption quotes the start of the YouTube title)."""
    try:
        r = subprocess.run([str(Y), "tools/youtube_api.py", "videos"], cwd=ROOT, capture_output=True, text=True, timeout=120)
    except Exception:
        return None
    for line in r.stdout.splitlines():
        m = re.match(r"(\S{11})\s+\S+\s+\S+\s+\d+ views\s+(.*)", line)
        if m and m.group(2).startswith(title): return f"https://youtu.be/{m.group(1)}"


def yt_text(caption):
    out = []
    for line in caption.strip().splitlines():
        line = line.replace("👇 Save this and swipe through it once a day this week.", "👉 Swipe through the pictures, once a day this week.")
        m = re.match(r'Full lesson(.*?): "(.+)" on YouTube, link in bio ▶️', line)
        if m:
            url = video_url(m.group(2))
            line = f"▶️ Full lesson{m.group(1)}: {m.group(2)}" + (f"\n{url}" if url else " (on this channel)")
        out.append(line)
    return "\n".join(out)


def main():
    src = pathlib.Path(sys.argv[1]); stem = src.name
    posts = json.loads(DATA.read_text(encoding="utf-8")) if DATA.exists() else []
    posts = [p for p in posts if p["stem"] != stem]
    if "--date" in sys.argv:
        day = datetime.date.fromisoformat(sys.argv[sys.argv.index("--date") + 1])
    else:
        today = datetime.date.today()
        last = max([datetime.date.fromisoformat(p["date"]) for p in posts] + [today - datetime.timedelta(days=1)])
        day = next_day(max(last, today - datetime.timedelta(days=1)))
    folder = f"{day:%a}-{day.day}-{day:%b}-{stem}".lower()
    slides = sorted(src.glob("slide-*.jpg"))[:-1]
    dst = OUT / folder; dst.mkdir(parents=True, exist_ok=True)
    for f in dst.glob("slide-*.jpg"): f.unlink()
    for f in slides: shutil.copy(f, dst / f.name)
    posts.append({"date": day.isoformat(), "stem": stem, "folder": folder, "n": len(slides),
                  "title": (src / "caption.txt").read_text(encoding="utf-8").splitlines()[0].split(" 👇")[0],
                  "text": yt_text((src / "caption.txt").read_text(encoding="utf-8"))})
    posts.sort(key=lambda p: p["date"])
    posts = [p for p in posts if p["date"] >= (datetime.date.today() - datetime.timedelta(days=14)).isoformat()]
    DATA.write_text(json.dumps(posts, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(f"YouTube Post {day:%a %d %b}: {len(slides)} pictures in {dst}")


if __name__ == "__main__":
    main()
