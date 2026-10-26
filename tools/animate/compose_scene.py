#!/usr/bin/env python3
"""Characters v5 (owner, 2026-10-26): green-screen picture sequences composited on a background, blended.

    $TTS tools/animate/compose_scene.py BG.png OUT.mp4 --seconds 6 --pps 3 \
        --layer library/sets/sami-talk:0.5:1.0[:once]  [--layer library/sets/lina-listen:0.72:0.95] [--still]

--layer DIR:X:H[:once] — the pictures 01.png, 02.png … of a set on flat green; X = horizontal centre (0–1),
H = character height as a share of the frame (the character stands on the bottom edge — chest-up shots).
Sets loop back and forth (ping-pong) unless ":once" (openers: play once, then hold the last picture).
--pps = pictures per second (openers 5, mid-video 3); transitions are soft blends (ffmpeg framerate).
--still OUT.png also writes the last composed picture at full quality (the opener's hold image).
Green key: a pixel is background when green clearly dominates red and blue; edges get a soft alpha and the green
spill is pulled down. Each character gets a soft contact shadow and is colour-matched lightly to the background.
"""
import argparse
import pathlib
import subprocess
import tempfile

import numpy as np
from PIL import Image, ImageFilter

W, H = 1080, 1920


def key(img):
    a = np.asarray(img.convert("RGB"), dtype=np.float32)
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    dom = g - np.maximum(r, b)
    alpha = np.clip(1.0 - (dom - 20) / 50, 0, 1)            # 0 = green background, 1 = character
    spill = np.clip(g - np.maximum(r, b), 0, None)
    a[..., 1] = np.where(alpha > 0, g - spill * 0.85, g)       # pull green fringe down
    out = np.dstack([np.clip(a, 0, 255), alpha * 255]).astype(np.uint8)
    im = Image.fromarray(out, "RGBA")
    al = im.getchannel("A").filter(ImageFilter.GaussianBlur(1.2))
    im.putalpha(al)
    return im


def colour_match(char, bg_mean, amount=0.12):
    a = np.asarray(char, dtype=np.float32)
    m = a[..., :3][a[..., 3] > 128].mean(axis=0) if (a[..., 3] > 128).any() else bg_mean
    a[..., :3] = np.clip(a[..., :3] + (bg_mean - m) * amount, 0, 255)
    return Image.fromarray(a.astype(np.uint8), "RGBA")


def compose(bg, layers, idx):
    canvas = bg.copy()
    bg_mean = np.asarray(bg, dtype=np.float32).reshape(-1, 3).mean(axis=0)
    for (frames, x, h, once) in layers:
        n = len(frames)
        k = min(idx, n - 1) if once else (idx % (2 * n - 2) if n > 1 else 0)
        if not once and k >= n:
            k = 2 * n - 2 - k
        ch = frames[k]
        hh = int(H * h); ww = int(ch.width * hh / ch.height)
        ch = ch.resize((ww, hh), Image.LANCZOS)
        ch = colour_match(ch, bg_mean)
        x0 = int(W * x - ww / 2); y0 = H - hh
        sh = Image.new("L", (W, H), 0)                         # soft contact shadow at the bottom
        from PIL import ImageDraw
        ImageDraw.Draw(sh).ellipse((x0 + ww * 0.15, H - 60, x0 + ww * 0.85, H + 60), fill=90)
        sh = sh.filter(ImageFilter.GaussianBlur(40))
        canvas = Image.composite(Image.new("RGB", (W, H), (20, 15, 10)), canvas, sh)
        canvas.paste(ch, (x0, y0), ch)
    return canvas


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("bg"); ap.add_argument("out")
    ap.add_argument("--seconds", type=float, default=6); ap.add_argument("--pps", type=int, default=3)
    ap.add_argument("--layer", action="append", required=True)
    ap.add_argument("--still")
    a = ap.parse_args()
    bg = Image.open(a.bg).convert("RGB").resize((W, H), Image.LANCZOS) if True else None
    bw, bh = Image.open(a.bg).size
    src = Image.open(a.bg).convert("RGB")
    s = max(W / bw, H / bh); src = src.resize((int(bw * s) + 1, int(bh * s) + 1), Image.LANCZOS)
    bg = src.crop(((src.width - W) // 2, (src.height - H) // 2, (src.width - W) // 2 + W, (src.height - H) // 2 + H))
    layers = []
    for spec in a.layer:
        parts = spec.split(":")
        d = pathlib.Path(parts[0]); once = len(parts) > 3 and parts[3] == "once"
        frames = [key(Image.open(f)) for f in sorted(d.glob("[0-9][0-9].png"))]
        layers.append((frames, float(parts[1]), float(parts[2]), once))
    n_out = max(1, int(round(a.seconds * a.pps)))
    tmp = pathlib.Path(tempfile.mkdtemp())
    for i in range(n_out):
        compose(bg, layers, i).save(tmp / f"{i:04d}.png")
    if a.still:
        compose(bg, layers, 10 ** 6 if all(l[3] for l in layers) else n_out - 1).save(a.still)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-framerate", str(a.pps), "-i", str(tmp / "%04d.png"),
                    "-vf", "framerate=fps=30:interp_start=0:interp_end=255:scene=100,format=yuv420p",
                    "-c:v", "libx264", "-crf", "14", a.out], check=True)
    print(f"{a.out}: {n_out} pictures at {a.pps}/s")


if __name__ == "__main__":
    main()
