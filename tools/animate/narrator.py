#!/usr/bin/env python3
"""The clay narrator for the 16:9 story video (owner 2026-11-03: "the talking claymation continues as me").

    $TTS tools/animate/narrator.py VOICE.wav OUT.mp4 [--set …/half/set] [--square-set …/set] [--picture scene.png --switch 3.3]

Owner's verdict on the first test: "the mouth has a shadow of the mustache … the hands are fixed, very unnatural" →
- the mouth shapes are INPAINTED inside the still (tools/images/generate.py --mask), so beard and mustache stay
  pixel-identical in every shape — no ghost of a second beard;
- full screen = a HALF-BODY shot (owner 2026-11-03), arms down, cut above the hands; the small square = the close-up
  face set; the body is never frozen: slow breathing, a slight sway, the head lifts a little
  on stressed (loud) syllables, a blink every few seconds;
- the mouth follows the LOUDNESS of the voice (quiet → small shapes, loud → open), held ≥ 3 frames, quick 2-frame
  blends; closed whenever the voice is silent.
Set folder: still.png, mouth1–5.png (1 slight · 2 open 'ah' · 3 half · 4 'ee' · 5 'oo'), blink.png, eyemask.png —
all the same size, green screen (library/work/narrator/film3d/set = the 3D-film half body 896×1000 — owner's pick 2026-11-04; half/set = the old clay one;
…/set = clay close-up 1344×768).
Full screen = the narrator alone (explanations); --picture = the story picture with him in a small square, from
--switch seconds on.
"""
import argparse
import math
import pathlib
import random
import shutil
import signal
import subprocess
import sys
import tempfile
import time

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from compose_talk import keyed  # noqa: E402

W, H, FPS = 1920, 1080, 30
PAPER = (250, 247, 240)


def envelope(wav):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", str(wav), "-ac", "1", "-ar", "16000", "-f", "f32le", "-"],
                         capture_output=True, check=True).stdout
    x = np.frombuffer(raw, np.float32)
    hop = 16000 // FPS
    n = len(x) // hop
    rms = np.sqrt(np.mean(x[:n * hop].reshape(n, hop) ** 2, axis=1))
    db = 20 * np.log10(rms + 1e-6)
    voiced = db > -38                                          # the same threshold as voiced.py
    ref = np.percentile(rms[voiced], 95) if voiced.any() else 1
    return np.clip(rms / ref, 0, 1), voiced, len(x) / 16000


def mouth_track(env, voiced):
    """mouth index per frame: 0 = still (closed), 1–5 = the set's mouths."""
    small, mid = [1, 4], [3, 5]
    out, cur, held, syl = [], 0, 99, 0
    for e, v in zip(env, voiced):
        want = 0 if not v else (2 if e > 0.62 else mid[syl % 2] if e > 0.33 else small[syl % 2])
        if want != cur and held >= 3:
            if want and not cur or (want == 2):
                syl += 1
            cur, held = want, 0
        out.append(cur); held += 1
    return out


def load_set(folder, size):
    folder = pathlib.Path(folder)
    still = Image.open(folder / "still.png").convert("RGB")
    blink = Image.open(folder / "blink.png").convert("RGB")
    m = Image.open(folder / "eyemask.png").convert("L").filter(ImageFilter.GaussianBlur(3))
    faces = [still] + [Image.open(folder / f"mouth{i}.png").convert("RGB") for i in range(1, 6)]
    out = {}
    tmp = pathlib.Path(tempfile.mkdtemp(prefix="narrset-"))
    try:
        for i, f in enumerate(faces):
            for b in (0, 1):
                p = tmp / f"{i}-{b}.png"
                (Image.composite(blink, f, m) if b else f).save(p)
                out[i, b] = np.asarray(keyed(str(p)).resize(size, Image.LANCZOS), dtype=np.float32)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    return out


def body(t, lift):
    """(angle°, dx, dy, yscale) — breathing, sway and the small lift on stressed syllables."""
    ang = 0.55 * math.sin(2 * math.pi * t / 6.3) + 0.25 * math.sin(2 * math.pi * t / 2.9 + 1.0)
    dx = 5 * math.sin(2 * math.pi * t / 8.1)
    dy = -9 * lift
    ys = 1 + 0.006 * math.sin(2 * math.pi * t / 3.8)
    return ang, dx, dy, ys


def transform(fig, ang, dx, dy, ys):
    """rotate/scale the figure around its bottom centre (the cut-off chest), then shift."""
    h, w = fig.shape[:2]
    a = math.radians(ang); c, s = math.cos(a), math.sin(a)
    cx, cy = w / 2, h
    # inverse map: output (x, y) → input
    m = (c, s, cx - c * (cx + dx) - s * (cy + dy),
         -s / ys, c / ys, cy - (-s * (cx + dx) + c * (cy + dy)) / ys)
    im = Image.fromarray(fig.astype(np.uint8), "RGBA")
    return im.transform((w, h), Image.AFFINE, m, resample=Image.BICUBIC)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("voice"); ap.add_argument("out")
    ap.add_argument("--set", default="library/work/narrator/film3d/set")
    ap.add_argument("--square-set", default="library/work/narrator/set")
    ap.add_argument("--picture"); ap.add_argument("--switch", type=float, default=0)
    a = ap.parse_args()

    env, voiced, dur = envelope(a.voice)
    mouths = mouth_track(env, voiced)
    lift = np.convolve(env * voiced, np.ones(8) / 8, mode="same")     # smoothed loudness → the head lifts a little
    rnd = random.Random(7); blinks, t = set(), 1.2
    while t < dur:
        f = int(t * FPS); blinks.update({f + 1, f + 2}); t += rnd.uniform(2.5, 5.0)

    sw, sh = Image.open(pathlib.Path(a.set) / "still.png").size
    fh = int(H * 1.04); fw = int(sw * fh / sh)                           # full screen: the waist runs off the bottom
    big = load_set(a.set, (fw, fh))
    sq = 380                                                             # the small square
    small = load_set(a.square_set, (int(1344 * 0.72), int(768 * 0.72)))
    paper = Image.new("RGB", (W, H), PAPER)
    pic = None
    if a.picture:
        p = Image.open(a.picture).convert("RGB"); ph = 900; p = p.resize((int(p.width * ph / p.height), ph), Image.LANCZOS)
        pic = paper.copy(); pic.paste(p, ((W - p.width) // 2, 60))

    signal.signal(signal.SIGTERM, lambda *_: sys.exit(1))
    n = len(mouths)
    prev, cur_key, start, left = None, None, None, 0
    with tempfile.TemporaryDirectory(prefix="narrframes-") as tmp:
        tmp = pathlib.Path(tmp)
        for i in range(n):
            t = i / FPS
            key = (mouths[i], int(i in blinks))
            sqmode = pic is not None and t >= a.switch
            src = small if sqmode else big
            if cur_key is not None and key != cur_key:
                start, left = prev_fig, 2
            fig = src[key]
            if left and start is not None and start.shape == fig.shape:
                k = (3 - left) / 3; fig = start * (1 - k) + fig * k; left -= 1
            prev_fig, cur_key = fig, key
            im = transform(fig, *body(t, lift[i]))
            if sqmode:
                box = Image.new("RGB", im.size, PAPER); box.paste(im, (0, 0), im)
                cx, cy = box.width // 2, int(box.height * 0.47)
                face = box.crop((cx - 230, cy - 230, cx + 230, cy + 230)).resize((sq, sq), Image.LANCZOS)
                frame = pic.copy()
                x0, y0 = W - sq - 40, H - sq - 40
                ImageDraw.Draw(frame).rounded_rectangle((x0 - 6, y0 - 6, x0 + sq + 6, y0 + sq + 6), radius=26, fill=(255, 255, 255))
                mask = Image.new("L", (sq, sq), 0); ImageDraw.Draw(mask).rounded_rectangle((0, 0, sq, sq), radius=22, fill=255)
                frame.paste(face, (x0, y0), mask)
            else:
                frame = paper.copy(); frame.paste(im, ((W - im.width) // 2, H - im.height + int(H * 0.03)), im)
            frame.save(tmp / f"{i:05d}.png")
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-framerate", str(FPS), "-i", str(tmp / "%05d.png"), "-i", a.voice,
                        "-c:v", "libx264", "-crf", "16", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k",
                        "-shortest", a.out], check=True)
    print(f"{a.out}: {n} frames")


if __name__ == "__main__":
    main()
