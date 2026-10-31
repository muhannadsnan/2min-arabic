#!/usr/bin/env python3
"""Daily Instagram Reel from GitHub Actions — the laptop can be off (owner, 2026-10-15).

    python3 tools/ig_cloud_post.py [--dry-run] [--force]

The queue is the `ig-queue` release of this repo: one encrypted bundle per Reel, `reel-NN.bin`
(tar of video.mp4 + cover.jpg + caption.txt, AES-256 with the IG_QUEUE_KEY secret — unreadable for anyone else).
Each run: only after 15:00 Oslo time (the workflow runs at 13:05 and 14:05 UTC so summer and winter time both work),
only if nothing was posted to Instagram today (asked from Instagram itself, so a re-run can't double-post), then
the lowest NN is decrypted and posted through instagram_api.post (ig-temp link for a few minutes, deleted after),
and its bundle is removed from the queue. The queue is refilled from the laptop: tools/ig_queue_add.sh.
"""
import argparse
import datetime
import os
import pathlib
import subprocess
import sys
import tempfile
from zoneinfo import ZoneInfo

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import instagram_api as ig  # noqa: E402

OSLO = ZoneInfo("Europe/Oslo")
POST_HOUR = 15
QUEUE = "ig-queue"


def gh(*args, capture=True):
    return subprocess.run(["gh", *args, "-R", ig.REPO], check=True, capture_output=capture, text=True).stdout


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true", help="upload + let Instagram process it, but don't publish")
    ap.add_argument("--force", action="store_true", help="ignore the 15:00 gate and the once-a-day check")
    ap.add_argument("--trial", action="store_true", help="post the next dubbed Trial Reel from the ig-trial queue")
    ap.add_argument("--carousel", action="store_true", help="post the next carousel from the ig-carousel queue")
    a = ap.parse_args()
    if a.carousel:
        return carousel(a)
    if a.trial:
        return trial(a)
    now = datetime.datetime.now(OSLO)
    if not a.force and now.hour < POST_HOUR:
        print(f"{now:%H:%M} Oslo — before {POST_HOUR}:00, nothing to do")
        return
    if not a.force:
        # only our normal Reels count (owner 2026-10-19): Trial Reels (not shared to the profile) and the owner's own
        # photo posts must not block the daily Reel
        recent = ig.call("me/media", fields="timestamp,media_product_type,is_shared_to_feed", limit=10).get("data", [])
        latest = [m for m in recent if m.get("media_product_type") == "REELS" and m.get("is_shared_to_feed") is not False]
        if latest:
            last = datetime.datetime.strptime(latest[0]["timestamp"], "%Y-%m-%dT%H:%M:%S%z").astimezone(OSLO)
            if last.date() == now.date():
                print(f"already posted today ({last:%H:%M} Oslo) — one Reel a day")
                return
    names = sorted(n for n in gh("release", "view", QUEUE, "--json", "assets", "--jq", ".assets[].name").split()
                   if n.startswith("reel-") and n.endswith(".bin"))
    if not names:
        sys.exit("Instagram queue is empty — ask Claude for the next Reels (tools/ig_queue_add.sh)")
    name = names[0]
    tmp = pathlib.Path(tempfile.mkdtemp())
    gh("release", "download", QUEUE, "-p", name, "-D", str(tmp))
    key = tmp / "key"
    key.write_text(os.environ["IG_QUEUE_KEY"])
    subprocess.run(f'openssl enc -d -aes-256-cbc -pbkdf2 -pass file:"{key}" -in "{tmp / name}" | tar -C "{tmp}" -xf -',
                   shell=True, check=True)
    key.unlink()
    cap = tmp / "caption.txt"
    cap.write_text(add_languages(cap.read_text(encoding="utf-8"), now.timetuple().tm_yday), encoding="utf-8")
    print(f"{name}: {cap.read_text(encoding='utf-8').splitlines()[0][:80]}")
    print("languages today:", cap.read_text(encoding="utf-8").strip().split("\n\n")[-2].replace("\n", " · "))
    ig.post(argparse.Namespace(video=str(tmp / "video.mp4"), caption_file=str(cap),
                               cover=str(tmp / "cover.jpg"), apply=not a.dry_run, trial=False))
    if not a.dry_run and os.environ.get("FB_PAGE_TOKEN"):   # owner 2026-10-20: the same Reel on the Facebook Page
        try:
            import facebook_api as fb
            print(f"✅ Facebook: {fb.post_video(tmp / 'video.mp4', cap.read_text(encoding='utf-8').strip())}")
        except (Exception, SystemExit) as e:   # Facebook failing must never block the Instagram post
            print(f"::warning::Facebook post failed: {str(e)[:200]}")
    if not a.dry_run:
        gh("release", "delete-asset", QUEUE, name, "-y")
        print(f"{name} removed from the queue · {len(names) - 1} Reels left")
        if len(names) - 1 <= 3:
            print(f"::warning::Only {len(names) - 1} Reels left in the Instagram queue")


def carousel(a):
    """Carousel twice a week (owner 2026-10-30: Wed + Sun 19:00, 7–8 slides, the words of the latest Reel's video):
    the next carousel-NN.bin from the `ig-carousel` release (encrypted tar of slide-*.jpg + caption.txt, made by
    tools/ig_carousel_add.py). Once per day (done-YYYY-MM-DD marker)."""
    now = datetime.datetime.now(OSLO); Q = "ig-carousel"
    assets = gh("release", "view", Q, "--json", "assets", "--jq", ".assets[].name").split()
    marker = f"done-{now:%Y-%m-%d}"
    if marker in assets and not a.force:
        print(f"a carousel was already posted today ({marker})"); return
    names = sorted(n for n in assets if n.startswith("carousel-") and n.endswith(".bin"))
    if not names:
        print("::warning::carousel queue is empty — ask Claude for the next carousels"); return
    name = names[0]; tmp = pathlib.Path(tempfile.mkdtemp())
    gh("release", "download", Q, "-p", name, "-D", str(tmp))
    key = tmp / "key"; key.write_text(os.environ["IG_QUEUE_KEY"])
    subprocess.run(f'openssl enc -d -aes-256-cbc -pbkdf2 -pass file:"{key}" -in "{tmp / name}" | tar -C "{tmp}" -xf -',
                   shell=True, check=True)
    key.unlink()
    print(f"{name}: {(tmp / 'caption.txt').read_text(encoding='utf-8').splitlines()[0][:80]}")
    ig.carousel(argparse.Namespace(folder=str(tmp), apply=not a.dry_run))
    if not a.dry_run:
        gh("release", "delete-asset", Q, name, "-y")
        (tmp / marker).write_text("1"); gh("release", "upload", Q, str(tmp / marker), "--clobber")
        for old in (n for n in assets if n.startswith("done-") and n != marker):
            gh("release", "delete-asset", Q, old, "-y")
        print(f"{name} posted · {len(names) - 1} carousels left")


def trial(a):
    """Daily dubbed Trial Reel (owner 2026-10-19): one language a day from the `ig-trial` release (trial-NN-<lang>.bin,
    same encryption as the main queue), posted as a Trial Reel = non-followers only. Its caption is already in that
    language (no rotation). Once per slot (morning / evening): a `done-YYYY-MM-DD-am|pm` marker asset."""
    now = datetime.datetime.now(OSLO); Q = "ig-trial"
    pause = pathlib.Path(__file__).resolve().parent.parent / "data" / "trial-paused.txt"
    if pause.exists():   # owner 2026-10-30: the old-style dubs are flagged "looks like something you shared before"
        print(f"Trial Reels paused: {pause.read_text().strip()}"); return
    assets = gh("release", "view", Q, "--json", "assets", "--jq", ".assets[].name").split()
    marker = f"done-{now:%Y-%m-%d}-{'am' if now.hour < 14 else 'pm'}"   # two slots a day (owner 2026-10-19, x03 phase)
    if marker in assets and not a.force:
        print(f"a Trial Reel was already posted today ({marker})"); return
    # only the new-style language versions (own subtitles + hook, "-v2"): the old ones (same picture, new voice) are
    # flagged "looks like something you shared before" (owner 2026-10-30)
    names = sorted(n for n in assets if n.startswith("trial-") and n.endswith("-v2.bin"))
    if not names:
        print("trial queue has no new-style versions — nothing to do"); return
    name = names[0]; tmp = pathlib.Path(tempfile.mkdtemp())
    gh("release", "download", Q, "-p", name, "-D", str(tmp))
    key = tmp / "key"; key.write_text(os.environ["IG_QUEUE_KEY"])
    subprocess.run(f'openssl enc -d -aes-256-cbc -pbkdf2 -pass file:"{key}" -in "{tmp / name}" | tar -C "{tmp}" -xf -',
                   shell=True, check=True)
    key.unlink()
    print(f"{name}: {(tmp / 'caption.txt').read_text(encoding='utf-8').splitlines()[0][:80]}")
    ig.post(argparse.Namespace(video=str(tmp / "video.mp4"), caption_file=str(tmp / "caption.txt"),
                               cover=str(tmp / "cover.jpg"), apply=not a.dry_run, trial=True))
    if not a.dry_run and os.environ.get("FB_PAGE_TOKEN"):   # owner 2026-10-31: the language versions on Facebook too
        try:
            import facebook_api as fb
            print(f"✅ Facebook: {fb.post_video(tmp / 'video.mp4', (tmp / 'caption.txt').read_text(encoding='utf-8').strip())}")
        except (Exception, SystemExit) as e:   # Facebook failing must never block the Instagram post
            print(f"::warning::Facebook post failed: {str(e)[:200]}")
    if not a.dry_run:
        gh("release", "delete-asset", Q, name, "-y")
        (tmp / marker).write_text("1"); gh("release", "upload", Q, str(tmp / marker), "--clobber")
        for old in (n for n in assets if n.startswith("done-") and n != marker):
            gh("release", "delete-asset", Q, old, "-y")
        print(f"{name} posted as a Trial Reel · {len(names) - 1} left")


# owner 2026-10-18: every Reel also speaks to two other language audiences — one short line each above the hashtags and
# one hashtag each (3 fixed + 2 rotating = 5). Rotates daily through the top languages so each gets regular reach.
FIXED_TAGS = "#learnarabic #arabicforbeginners #2minutearabic"
LANG_ROT = [("Belajar bahasa Arab 2 menit sehari — dengan subtitle bahasa Indonesia di YouTube.", "#belajarbahasaarab"),
            ("Arabi seekhein, roz sirf 2 minute — YouTube par Urdu / Hindi subtitles ke saath.", "#learnarabicinurdu"),
            ("Günde 2 dakikada Arapça — YouTube'da Türkçe altyazıyla.", "#arapçaöğren"),
            ("آموزش عربی، روزی ۲ دقیقه — با زیرنویس فارسی در یوتیوب.", "#آموزش_زبان_عربی"),
            ("প্রতিদিন ২ মিনিটে আরবি — ইউটিউবে বাংলা সাবটাইটেলসহ।", "#আরবি_শিক্ষা"),
            ("Belajar bahasa Arab 2 minit sehari — dengan sari kata Bahasa Melayu di YouTube.", "#belajarbahasaarab"),
            ("L'arabe en 2 minutes par jour — sous-titres français sur YouTube.", "#apprendrelarabe")]
# (owner 2026-10-18: the line must not promise lessons in their language on Instagram — it points to YouTube, where
#  every video has subtitles in it and the top videos audio too; the YouTube link is in the bio)

def add_languages(caption, day):
    """Two languages a day: their line goes above the hashtags, their hashtag replaces the kind-specific ones."""
    picks = [LANG_ROT[day % len(LANG_ROT)], LANG_ROT[(day + 1) % len(LANG_ROT)]]
    parts = caption.strip().split("\n\n")
    body = parts[:-1] if parts[-1].lstrip().startswith("#") else parts
    tags = " ".join(dict.fromkeys([*FIXED_TAGS.split(), *(t for _, t in picks)]))
    return "\n\n".join([*body, "🌍 " + "\n🌍 ".join(l for l, _ in picks), tags])


if __name__ == "__main__":
    main()
