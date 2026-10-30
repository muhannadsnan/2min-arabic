#!/usr/bin/env python3
"""Queue a carousel for the twice-weekly Instagram post (owner 2026-10-30: Wed + Sun 19:00 Oslo).

    python3 tools/ig_carousel_add.py output/carousel/<stem> [--apply]

The folder holds slide-*.jpg (tools/make_carousel.py) + caption.txt. It is tarred, encrypted with the Instagram queue
key (like the Reel queue) and uploaded to the `ig-carousel` release as carousel-NN.bin, numbered after what is queued.
The workflow instagram-carousel.yml posts the lowest number.
"""
import pathlib, re, subprocess, sys, tempfile
KEY = pathlib.Path.home() / ".config/2min-instagram/queue.key"; REPO, Q = "muhannadsnan/2min-arabic", "ig-carousel"

def main():
    folder = pathlib.Path(sys.argv[1]); apply = "--apply" in sys.argv
    slides = sorted(folder.glob("slide-*.jpg"))
    if not 2 <= len(slides) <= 10 or not (folder / "caption.txt").exists():
        sys.exit(f"{folder}: needs 2–10 slides + caption.txt")
    r = subprocess.run(["gh", "release", "view", Q, "-R", REPO, "--json", "assets", "--jq", ".assets[].name"], capture_output=True, text=True)
    if r.returncode != 0:
        if apply:
            subprocess.run(["gh", "release", "create", Q, "-R", REPO, "--title", "Instagram carousel queue (encrypted)",
                            "--notes", "Encrypted carousels, Wed + Sun 19:00 Oslo (tools/ig_carousel_add.py)."], check=True)
        existing = []
    else:
        existing = [int(m.group(1)) for m in re.finditer(r"carousel-(\d+)", r.stdout)]
    n = max(existing, default=0) + 1
    b = pathlib.Path(tempfile.mkdtemp()) / f"carousel-{n:02d}.bin"
    files = " ".join(f'"{s.name}"' for s in slides) + " caption.txt"
    subprocess.run(f'tar -C "{folder}" -cf - {files} | openssl enc -aes-256-cbc -pbkdf2 -salt -pass file:"{KEY}" -out "{b}"',
                   shell=True, check=True)
    print(f"{b.name}: {len(slides)} slides · {(folder / 'caption.txt').read_text(encoding='utf-8').splitlines()[0][:70]}")
    if apply:
        subprocess.run(["gh", "release", "upload", Q, "-R", REPO, str(b)], check=True); print("queued")
    else:
        print("dry run — add --apply to upload")

if __name__ == "__main__":
    main()
