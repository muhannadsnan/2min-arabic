#!/usr/bin/env python3
"""LIKE + SUBSCRIBE + bell overlay (owner 2026-11-16: "why not the subscribe button click and like and chiming?").

    python3 tools/make_like_subscribe.py   → assets/like-subscribe.mov (1080×300, alpha, 5.2 s)

Same look as tools/make_subscribe.py (white card, red SUBSCRIBE, bell, our own cursor) with a 👍 LIKE button first:
the cursor clicks LIKE (turns blue), SUBSCRIBE (turns grey "SUBSCRIBED"), then the bell (rings, ding). Short enough to
sit under a ~5 s "like and subscribe" line. Clicks/ding: CLICK_TIMES / DING_TIME (assets/click.wav, assets/ding.wav).
"""
import math
import pathlib
import shutil
import subprocess
import sys
import tempfile

from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from make_subscribe import BOLD, DARK, GREY, RED, WHITE, bell, cursor, ease, lerp  # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parent.parent
W, H, FPS, DUR = 1080, 300, 30, 5.2
CLICK_TIMES = (1.0, 2.1, 3.2)   # like, subscribe, bell
DING_TIME = 3.25
BLUE = (6, 95, 212)


def thumb(color):
    """A simple thumbs-up drawn from shapes (no emoji font, no stock icon)."""
    img = Image.new("RGBA", (120, 120), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((14, 52, 36, 106), radius=5, fill=color)                       # cuff
    d.rounded_rectangle((42, 50, 100, 106), radius=12, fill=color)                     # fist
    d.polygon([(44, 54), (58, 16), (70, 12), (76, 22), (72, 52)], fill=color)          # thumb
    d.ellipse((58, 8, 78, 28), fill=color)                                              # thumb tip
    for y in (64, 78, 92):                                                              # finger lines
        d.line((70, y, 98, y), fill=WHITE, width=3)
    return img


def frame(t):
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    appear = ease(t / 0.3)
    alpha = appear * (1.0 - ease((t - (DUR - 0.4)) / 0.4))
    if alpha <= 0:
        return img
    s = 0.85 + 0.15 * appear
    cw, ch = 980 * s, 170 * s
    x0, y0 = (W - cw) / 2, (H - ch) / 2
    d.rounded_rectangle((x0 + 6, y0 + 10, x0 + cw + 6, y0 + ch + 10), radius=int(40 * s), fill=(0, 0, 0, 70))
    d.rounded_rectangle((x0, y0, x0 + cw, y0 + ch), radius=int(40 * s), fill=WHITE)

    def press(c):
        return 1.0 - 0.08 * math.exp(-((t - c) / 0.06) ** 2)

    # LIKE: an outlined pill with a thumb; blue + filled once clicked
    liked = t >= CLICK_TIMES[0]
    p = press(CLICK_TIMES[0])
    lw, lh = 190 * s * p, 110 * s * p
    lx, ly = x0 + 36 * s + (190 * s - lw) / 2, y0 + (ch - lh) / 2
    d.rounded_rectangle((lx, ly, lx + lw, ly + lh), radius=int(55 * s), fill=BLUE if liked else (242, 242, 242))
    pop = 1.0 + 0.25 * math.exp(-((t - CLICK_TIMES[0] - 0.08) / 0.12) ** 2) if liked else 1.0
    ti = thumb(WHITE if liked else DARK).resize((int(84 * s * pop), int(84 * s * pop)), Image.LANCZOS)
    img.alpha_composite(ti, (int(lx + (lw - ti.width) / 2), int(ly + (lh - ti.height) / 2 - 2)))

    # SUBSCRIBE
    subscribed = t >= CLICK_TIMES[1]
    p = press(CLICK_TIMES[1])
    bw, bh = 470 * s * p, 110 * s * p
    bx, by = x0 + 256 * s + (470 * s - bw) / 2, y0 + (ch - bh) / 2
    d.rounded_rectangle((bx, by, bx + bw, by + bh), radius=int(22 * s), fill=GREY if subscribed else RED)
    font = ImageFont.truetype(BOLD, int(54 * s * p))
    label = "SUBSCRIBED" if subscribed else "SUBSCRIBE"
    box = d.textbbox((0, 0), label, font=font)
    d.text((bx + (bw - (box[2] - box[0])) / 2 - box[0], by + (bh - (box[3] - box[1])) / 2 - box[1]), label, font=font,
           fill=WHITE)

    # bell
    ring = 20 * math.sin((t - CLICK_TIMES[2]) * 28) * math.exp(-(t - CLICK_TIMES[2]) * 2.5) if t >= CLICK_TIMES[2] else 0
    bimg, pos = bell(d, x0 + cw - 110 * s, y0 + ch / 2 + 5, ring)
    img.alpha_composite(bimg, pos)

    # cursor: bottom-right → like → subscribe → bell
    pts = [(W - 60, H - 20), (lx + lw * 0.55, ly + lh * 0.6), (bx + bw * 0.6, by + bh * 0.55),
           (x0 + cw - 100 * s, y0 + ch / 2 + 10)]
    starts = [0.3] + [c + 0.25 for c in CLICK_TIMES[:2]]
    cx, cy = pts[0]
    for i in range(3):
        if t >= starts[i]:
            k = ease((t - starts[i]) / max(CLICK_TIMES[i] - starts[i], 0.01))
            cx, cy = lerp(pts[i][0], pts[i + 1][0], k), lerp(pts[i][1], pts[i + 1][1], k)
    cursor(d, cx, cy, 1.0 - 0.15 * max(math.exp(-((t - c) / 0.05) ** 2) for c in CLICK_TIMES))
    if alpha < 1:
        img.putalpha(img.getchannel("A").point(lambda v: int(v * alpha)))
    return img


def main():
    tmp = pathlib.Path(tempfile.mkdtemp())
    for i in range(int(DUR * FPS)):
        frame(i / FPS).save(tmp / f"f{i:04d}.png")
    out = ROOT / "assets" / "like-subscribe.mov"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-framerate", str(FPS), "-i", str(tmp / "f%04d.png"),
                    "-c:v", "png", "-pix_fmt", "rgba", str(out)], check=True)
    for t in (0.6, 1.6, 2.7, 4.0):
        frame(t).save(ROOT / "assets" / f"like-subscribe-preview-{t}.png")
    shutil.rmtree(tmp)
    print(f"wrote {out} (clicks at {CLICK_TIMES}, ding {DING_TIME})")


if __name__ == "__main__":
    main()
