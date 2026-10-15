#!/usr/bin/env python3
"""Look at an animated clip the way the owner does: a 6-frame strip + the held last frame at full size with the face
zoomed 2× (eyes, hands, arms per side) — see animation-library "double check".

    python3 tools/animate/check_clip.py clip.mp4 out.png [--face x0,y0,x1,y1]
"""
import argparse, subprocess, tempfile, pathlib
from PIL import Image

ap = argparse.ArgumentParser(); ap.add_argument("clip"); ap.add_argument("out"); ap.add_argument("--face", default="138,120,438,420")
a = ap.parse_args()
d = pathlib.Path(tempfile.mkdtemp())
n = int(subprocess.run(["ffprobe", "-v", "error", "-count_frames", "-select_streams", "v:0", "-show_entries",
                        "stream=nb_read_frames", "-of", "csv=p=0", a.clip], capture_output=True, text=True).stdout)
frames = [0, n // 5, 2 * n // 5, 3 * n // 5, 4 * n // 5, n - 1]
ims = []
for i, f in enumerate(frames):
    p = d / f"{i}.png"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", a.clip, "-vf", f"select=eq(n\\,{f})", "-vframes", "1", str(p)], check=True)
    ims.append(Image.open(p).convert("RGB"))
w, h = 288, 512
strip = Image.new("RGB", (w * 6, h)); [strip.paste(im.resize((w, h)), (k * w, 0)) for k, im in enumerate(ims)]
last = ims[-1]; box = tuple(int(v) for v in a.face.split(","))
face = last.crop(box).resize((400, 400))
out = Image.new("RGB", (max(strip.width, last.width + 420), h + last.height + 10), "white")
out.paste(strip, (0, 0)); out.paste(last, (0, h + 10)); out.paste(face, (last.width + 20, h + 10))
out.save(a.out); print(a.out)
