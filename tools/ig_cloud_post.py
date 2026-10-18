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
    a = ap.parse_args()
    now = datetime.datetime.now(OSLO)
    if not a.force and now.hour < POST_HOUR:
        print(f"{now:%H:%M} Oslo — before {POST_HOUR}:00, nothing to do")
        return
    if not a.force:
        latest = ig.call("me/media", fields="timestamp", limit=1).get("data", [])
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
    if not a.dry_run:
        gh("release", "delete-asset", QUEUE, name, "-y")
        print(f"{name} removed from the queue · {len(names) - 1} Reels left")
        if len(names) - 1 <= 3:
            print(f"::warning::Only {len(names) - 1} Reels left in the Instagram queue")


# owner 2026-10-18: every Reel also speaks to two other language audiences — one short line each above the hashtags and
# one hashtag each (3 fixed + 2 rotating = 5). Rotates daily through the top languages so each gets regular reach.
FIXED_TAGS = "#learnarabic #arabicforbeginners #2minutearabic"
LANG_ROT = [("Belajar bahasa Arab, 2 menit sehari.", "#belajarbahasaarab"),          # Indonesian
            ("Arabi seekhein, roz sirf 2 minute.", "#learnarabicinurdu"),            # Urdu / Hindi (Latin letters)
            ("Günde 2 dakikada sıfırdan Arapça.", "#arapçaöğren"),                   # Turkish
            ("آموزش زبان عربی از صفر، روزی ۲ دقیقه.", "#آموزش_زبان_عربی"),            # Persian
            ("প্রতিদিন ২ মিনিটে আরবি শিখুন।", "#আরবি_শিক্ষা"),                        # Bengali
            ("Belajar bahasa Arab, 2 minit sehari.", "#belajarbahasaarab"),           # Malay
            ("Apprendre l'arabe, 2 minutes par jour.", "#apprendrelarabe")]           # French

def add_languages(caption, day):
    """Two languages a day: their line goes above the hashtags, their hashtag replaces the kind-specific ones."""
    picks = [LANG_ROT[day % len(LANG_ROT)], LANG_ROT[(day + 1) % len(LANG_ROT)]]
    parts = caption.strip().split("\n\n")
    body = parts[:-1] if parts[-1].lstrip().startswith("#") else parts
    tags = " ".join(dict.fromkeys([*FIXED_TAGS.split(), *(t for _, t in picks)]))
    return "\n\n".join([*body, "🌍 " + "\n🌍 ".join(l for l, _ in picks), tags])


if __name__ == "__main__":
    main()
