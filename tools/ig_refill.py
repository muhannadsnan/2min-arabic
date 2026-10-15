#!/usr/bin/env python3
"""Refill the Instagram queue by itself (owner, 2026-10-15: "Claude just goes ahead and does that").

    ~/.local/share/2min-yt/venv/bin/python tools/ig_refill.py [--max 14] [--apply] [--out DIR]

Takes the channel's Shorts that are already PUBLIC on YouTube, in publish order, skips the ones Instagram already
had (~/.local/share/2min-yt/ig-queued.txt, one YouTube id per line), and builds one Reel per video:
video = the uploaded file, cover = its thumbnail, caption = the description's first line + its word lists
(🆕 / 📝 blocks) + the fixed Instagram footer. Each Reel is packed (tar) and encrypted with the queue key
(~/.config/2min-instagram/queue.key) as reel-NN.bin; --apply uploads them to the `ig-queue` release that
GitHub Actions posts from (tools/ig_cloud_post.py) and records the ids. Without --apply: builds them in --out only.
"""
import argparse
import json
import pathlib
import re
import shutil
import subprocess
import sys
import tempfile

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
REPO, QUEUE = "muhannadsnan/2min-arabic", "ig-queue"
STATE = pathlib.Path.home() / ".local/share/2min-yt/ig-queued.txt"
KEY = pathlib.Path.home() / ".config/2min-instagram/queue.key"
FOOTER = ("Two minutes a day. Your first Arabic conversation in 30 days.\n"
          "▶️ Full lessons + the whole course on YouTube: link in bio\n"
          "Save this and say it out loud 👇\n\n"
          "#learnarabic #arabiclanguage #arabicforbeginners #learnarabiconline #2minutearabic")


def sheets():
    """YouTube id → (sheet path, video file, thumbnail, description file), Shorts only."""
    out = {}
    for s in sorted((ROOT / "videos").glob("*-upload.md")):
        t = s.read_text(encoding="utf-8")
        vid = re.search(r"video id `([\w-]{11})`", t)
        f = re.search(r"\*\*File to upload:\*\* `([^`]+\.mp4)`", t)
        th = re.search(r"\*\*Thumbnail:\*\*[^`]*`([^`]+\.jpg)`", t)
        if not (vid and f and th) or "Short" not in t.split("\n", 3)[2]:
            continue
        desc = s.with_name(s.name.replace("-upload.md", "-description.txt"))
        out[vid.group(1)] = (s, ROOT / f.group(1), ROOT / th.group(1), desc)
    return out


TAGS = {"x": "#learnarabic #arabiclanguage #syrianarabic #arabicforbeginners #2minutearabic",
        "v": "#learnarabic #arabicvocabulary #arabicforbeginners #learnarabiconline #2minutearabic",
        "": "#learnarabic #arabiclanguage #arabicforbeginners #learnarabiconline #2minutearabic"}


def caption(desc):
    """Everything above the description's YouTube-only part (links, other languages, chapters), minus the slogan
    (it's in the footer), + the Instagram footer with the hashtags for this kind of video (Day / Extra / Vocab)."""
    paras = [p.strip() for p in desc.read_text(encoding="utf-8").split("\n\n") if p.strip()]
    body = []
    for p in paras:
        if p.startswith(("▶️", "🔔", "🌍", "⏱️")):
            break
        if not p.startswith("Two minutes a day."):
            body.append(p)
    kind = desc.name[0] if desc.name[0] in "xv" else ""
    return "\n\n".join([*body, FOOTER.rsplit("\n\n", 1)[0], TAGS[kind]])


def public_shorts_in_order(ids):
    import youtube_api as yt
    y = yt.yt("arabic")
    items = []
    for i in range(0, len(ids), 50):
        r = y.videos().list(part="status,snippet", id=",".join(ids[i:i + 50])).execute(num_retries=3)
        items += [v for v in r["items"] if v["status"]["privacyStatus"] == "public"]
    return [v["id"] for v in sorted(items, key=lambda v: v["snippet"]["publishedAt"])]


def queued_numbers():
    r = subprocess.run(["gh", "release", "view", QUEUE, "-R", REPO, "--json", "assets", "--jq", ".assets[].name"],
                       capture_output=True, text=True)
    return [int(m.group(1)) for m in re.finditer(r"reel-(\d+)\.bin", r.stdout)] if r.returncode == 0 else None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--max", type=int, default=14, help="Reels per refill (two weeks)")
    ap.add_argument("--apply", action="store_true", help="upload to the ig-queue release and record them")
    ap.add_argument("--out", type=pathlib.Path, default=None, help="keep the built Reels here (dry run)")
    a = ap.parse_args()
    done = set(STATE.read_text().split()) if STATE.exists() else set()
    sh = sheets()
    todo = [v for v in public_shorts_in_order(list(sh)) if v not in done][:a.max]
    if not todo:
        print("NOTHING_TO_REFILL — no public Short that Instagram hasn't had yet")
        return
    have = queued_numbers()
    if a.apply and have is None:
        sys.exit("no ig-queue release yet — the cloud posting isn't set up")
    last = max([*(have or []), int(pathlib.Path.home().joinpath(".local/share/2min-yt/ig-last.txt").read_text() or 0)
                if pathlib.Path.home().joinpath(".local/share/2min-yt/ig-last.txt").exists() else 0])
    tmp = pathlib.Path(tempfile.mkdtemp())
    built = []
    for n, vid in enumerate(todo, last + 1):
        sheet, video, thumb, desc = sh[vid]
        w = tmp / f"w{n:02d}"
        w.mkdir()
        shutil.copy(video, w / "video.mp4")
        shutil.copy(thumb, w / "cover.jpg")
        (w / "caption.txt").write_text(caption(desc), encoding="utf-8")
        if len((w / "caption.txt").read_text(encoding="utf-8")) > 2200:
            sys.exit(f"{sheet.name}: caption too long")
        b = tmp / f"reel-{n:02d}.bin"
        subprocess.run(f'tar -C "{w}" -cf - video.mp4 cover.jpg caption.txt | '
                       f'openssl enc -aes-256-cbc -pbkdf2 -salt -pass file:"{KEY}" -out "{b}"', shell=True, check=True)
        built.append((n, vid, sheet.name, b))
        print(f"reel-{n:02d}  {vid}  {sheet.name}  {caption(desc).splitlines()[0][:70]}")
    if a.out:
        a.out.mkdir(parents=True, exist_ok=True)
        for d in tmp.iterdir():
            shutil.move(str(d), a.out / d.name)
    if a.apply:
        subprocess.run(["gh", "release", "upload", QUEUE, "-R", REPO, *[str(b) for *_, b in built]], check=True)
        with STATE.open("a") as f:
            f.writelines(f"{vid}\n" for _, vid, _, _ in built)
        print(f"REFILLED reel-{built[0][0]:02d}–{built[-1][0]:02d} ({len(built)} Reels)")
    shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    main()
