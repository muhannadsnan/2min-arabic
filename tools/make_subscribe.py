#!/usr/bin/env python3
"""Render our own animated "SUBSCRIBE + bell" overlay (transparent video) and its click sound.

    python3 tools/make_subscribe.py        → assets/subscribe.mov (1080×300, alpha, 3 s) + assets/click.wav

Drawn from scratch (no stock footage, no watermark, no license issues). assemble.py lays it over the goodbye clip.
"""
import math
import pathlib
import shutil
import subprocess
import tempfile
import wave

import array
import random
from PIL import Image, ImageDraw, ImageFont

ROOT = pathlib.Path(__file__).resolve().parent.parent
ASSETS = ROOT / "assets"
W, H, FPS, DUR = 1080, 300, 30, 6.0
BOLD = "/usr/share/fonts/truetype/noto/NotoSans-Bold.ttf"
CLICK_TIMES = (1.9, 3.4)     # seconds: subscribe click, bell click (assemble.py mixes clicks here)
DING_TIME = 3.45             # the bell "ding" right after the bell click

RED, GREY, WHITE, DARK = (230, 33, 23), (150, 150, 150), (255, 255, 255), (30, 30, 30)


def ease(x):
    x = min(max(x, 0.0), 1.0)
    return 1 - (1 - x) ** 3


def lerp(a, b, x):
    return a + (b - a) * x


def cursor(d, x, y, s=1.0):
    pts = [(0, 0), (0, 46), (12, 35), (21, 55), (29, 51), (20, 32), (36, 32)]
    pts = [(x + px * s, y + py * s) for px, py in pts]
    d.polygon(pts, fill=WHITE, outline=DARK, width=4)


def bell(d, cx, cy, angle):
    # a simple bell: dome + rim + clapper, rotated by `angle` degrees around its top
    img = Image.new("RGBA", (120, 120), (0, 0, 0, 0))
    b = ImageDraw.Draw(img)
    b.pieslice((25, 20, 95, 90), 180, 360, fill=DARK)
    b.rectangle((25, 55, 95, 80), fill=DARK)
    b.rounded_rectangle((15, 78, 105, 90), radius=6, fill=DARK)
    b.ellipse((50, 90, 70, 106), fill=DARK)
    b.rectangle((55, 10, 65, 22), fill=DARK)
    img = img.rotate(angle, center=(60, 15), resample=Image.BICUBIC)
    return img, (int(cx - 60), int(cy - 55))


def frame(t):
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    appear = ease(t / 0.3)
    fade = 1.0 - ease((t - 5.5) / 0.5)
    alpha = appear * fade
    if alpha <= 0:
        return img
    scale = 0.85 + 0.15 * appear
    cw, ch = 760 * scale, 170 * scale
    x0, y0 = (W - cw) / 2, (H - ch) / 2
    d.rounded_rectangle((x0 + 6, y0 + 10, x0 + cw + 6, y0 + ch + 10), radius=int(40 * scale), fill=(0, 0, 0, 70))
    d.rounded_rectangle((x0, y0, x0 + cw, y0 + ch), radius=int(40 * scale), fill=WHITE)
    subscribed = t >= CLICK_TIMES[0]
    press = 1.0 - 0.08 * math.exp(-((t - CLICK_TIMES[0]) / 0.06) ** 2)
    bw, bh = 470 * scale * press, 110 * scale * press
    bx, by = x0 + 40 * scale + (470 * scale - bw) / 2, y0 + (ch - bh) / 2
    d.rounded_rectangle((bx, by, bx + bw, by + bh), radius=int(22 * scale), fill=GREY if subscribed else RED)
    font = ImageFont.truetype(BOLD, int(54 * scale * press))
    label = "SUBSCRIBED" if subscribed else "SUBSCRIBE"
    box = d.textbbox((0, 0), label, font=font)
    d.text((bx + (bw - (box[2] - box[0])) / 2 - box[0], by + (bh - (box[3] - box[1])) / 2 - box[1]), label, font=font,
           fill=WHITE)
    ring = 20 * math.sin((t - CLICK_TIMES[1]) * 28) * math.exp(-(t - CLICK_TIMES[1]) * 2.5) if t >= CLICK_TIMES[1] else 0
    bimg, pos = bell(d, x0 + cw - 110 * scale, y0 + ch / 2 + 5, ring)
    img.alpha_composite(bimg, pos)
    # cursor path: from bottom-right → subscribe button → bell
    sub_pt = (bx + bw * 0.6, by + bh * 0.55)
    bell_pt = (x0 + cw - 100 * scale, y0 + ch / 2 + 10)
    start = (W - 60, H - 20)
    if t < 0.6:
        cx, cy = start
    elif t < CLICK_TIMES[0]:
        k = ease((t - 0.6) / (CLICK_TIMES[0] - 0.6))
        cx, cy = lerp(start[0], sub_pt[0], k), lerp(start[1], sub_pt[1], k)
    elif t < CLICK_TIMES[0] + 0.5:
        cx, cy = sub_pt
    elif t < CLICK_TIMES[1]:
        k = ease((t - CLICK_TIMES[0] - 0.5) / (CLICK_TIMES[1] - CLICK_TIMES[0] - 0.5))
        cx, cy = lerp(sub_pt[0], bell_pt[0], k), lerp(sub_pt[1], bell_pt[1], k)
    else:
        cx, cy = bell_pt
    click_scale = 1.0 - 0.15 * max(math.exp(-((t - c) / 0.05) ** 2) for c in CLICK_TIMES)
    cursor(d, cx, cy, click_scale)
    if alpha < 1:
        a = img.getchannel("A").point(lambda v: int(v * alpha))
        img.putalpha(a)
    return img


def click_wav(path):
    """A short, soft UI click: a decaying 2.4 kHz tick plus a little noise."""
    rate, n = 48000, int(0.03 * 48000)
    rnd = random.Random(7)
    sig = [(0.35 * rnd.gauss(0, 1) * math.exp(-9 * i / n) + 0.5 * math.sin(2 * math.pi * 2400 * i / rate) * math.exp(-12 * i / n))
           for i in range(n)]
    peak = max(abs(v) for v in sig)
    data = array.array("h", (int(v / peak * 0.5 * 32767) for v in sig))
    with wave.open(str(path), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(rate)
        w.writeframes(data.tobytes())


def ding_wav(path):
    """A soft notification bell: two bright partials with a gentle 1.2 s decay."""
    rate, n = 48000, int(1.2 * 48000)
    sig = [(0.6 * math.sin(2 * math.pi * 1568 * i / rate) + 0.3 * math.sin(2 * math.pi * 3136 * i / rate)
            + 0.15 * math.sin(2 * math.pi * 2093 * i / rate)) * math.exp(-4.0 * i / n) * min(1.0, i / 120)
           for i in range(n)]
    peak = max(abs(v) for v in sig)
    data = array.array("h", (int(v / peak * 0.45 * 32767) for v in sig))
    with wave.open(str(path), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(rate)
        w.writeframes(data.tobytes())


def main():
    ASSETS.mkdir(exist_ok=True)
    tmp = pathlib.Path(tempfile.mkdtemp())
    for i in range(int(DUR * FPS)):
        frame(i / FPS).save(tmp / f"f{i:04d}.png")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-framerate", str(FPS), "-i", str(tmp / "f%04d.png"),
                    "-c:v", "png", "-pix_fmt", "rgba", str(ASSETS / "subscribe.mov")], check=True)
    frame(2.5).save(ASSETS / "subscribe-preview.png")
    shutil.rmtree(tmp)
    click_wav(ASSETS / "click.wav")
    ding_wav(ASSETS / "ding.wav")
    print(f"wrote {ASSETS / 'subscribe.mov'} and {ASSETS / 'click.wav'} (clicks at {CLICK_TIMES})")


if __name__ == "__main__":
    main()
