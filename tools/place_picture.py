#!/usr/bin/env python3
"""Put a generated landscape scene picture into the 9:16 frame so no face sits under the card or the subtitles
(owner 2026-11-02): scaled to a share of the video height (default 80 %), positioned at `top` (px) and cropped
around `cx` (source x), over a blurred copy of itself. Faces must land between the card's bottom and y ≈ 1280
(subtitles: 1290–1380) — or entirely below 1390.

    python3 tools/place_picture.py <in.png> <out.png> --top 680 --cx 445 [--height 0.8]
"""
import argparse
from PIL import Image, ImageFilter
W, H = 1080, 1920
a = argparse.ArgumentParser(); a.add_argument("src"); a.add_argument("out")
a.add_argument("--top", type=int, required=True); a.add_argument("--cx", type=float, required=True)
a.add_argument("--height", type=float, default=0.8); a = a.parse_args()
im = Image.open(a.src).convert("RGB")
s = H * a.height / im.height
fg = im.resize((round(im.width * s), round(im.height * s)), Image.LANCZOS)
x0 = min(max(round(a.cx * s - W / 2), 0), fg.width - W)
fg = fg.crop((x0, 0, x0 + W, fg.height))
k = max(W / im.width, H / im.height)
bg = im.resize((round(im.width * k) + 1, round(im.height * k) + 1)).crop((0, 0, W, H)).filter(ImageFilter.GaussianBlur(28))
bg.paste(fg, (0, a.top)); bg.save(a.out)
print(f"{a.out}: picture {fg.size} at top {a.top}, source x {x0 / s:.0f}–{(x0 + W) / s:.0f}")
