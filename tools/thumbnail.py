#!/usr/bin/env python3
"""Thumbnail from one of the video's own images (never a separately AI-generated picture).

    python3 tools/thumbnail.py <image.png> <out.jpg> --badge "DAY 6" --line1 "YES OR" --line2 "NO?!" --arabic "نَعَمْ"
    python3 tools/thumbnail.py <frame.png> <out.jpg> --wide --badge "DAYS 6–10" --line1 "LEARN" --line2 "ARABIC" \
        --line3 "in 10 minutes" --arabic "مَرْحَبًا"

Vertical (1080×1920, for Shorts) by default; --wide makes 1280×720 with the image on the right (long videos).
Keep lines short (2–3 words each) and check the result at phone size.
"""
import argparse

from PIL import Image, ImageDraw, ImageFont

F = "/usr/share/fonts/truetype/noto/"
BOLD, AR = F + "NotoSans-Bold.ttf", F + "NotoNaskhArabic-Bold.ttf"
YELLOW, WHITE, DARK, TEAL, TERRA = (255, 200, 0), (255, 255, 255), (15, 15, 20), (31, 95, 91), (192, 99, 58)


def fit(d, text, path, size, max_w, **kw):
    while size > 20:
        f = ImageFont.truetype(path, size)
        b = d.textbbox((0, 0), text, font=f, **kw)
        if b[2] - b[0] <= max_w:
            return f
        size -= 4
    return f


def vertical(a):
    im = Image.open(a.image).convert("RGB").resize((1080, 1890))
    bg = Image.new("RGB", (1080, 1920), (245, 230, 210))
    bg.paste(im, (0, 15))
    im, (W, H) = bg, bg.size
    grad = Image.new("L", (1, H))
    for y in range(H):
        grad.putpixel((0, y), int(max(0, (y - H * 0.5) / (H * 0.5)) * 190))
    im.paste(Image.new("RGB", (W, H), (15, 15, 25)), (0, 0), grad.resize((W, H)))
    d = ImageDraw.Draw(im)

    def center(y, t, f, fill, stroke=14, **kw):
        b = d.textbbox((0, 0), t, font=f, stroke_width=stroke, **kw)
        d.text(((W - (b[2] - b[0])) / 2 - b[0], y), t, font=f, fill=fill, stroke_width=stroke, stroke_fill=DARK, **kw)

    bf = fit(d, a.badge, BOLD, 78, 700)
    b = d.textbbox((0, 0), a.badge, font=bf)
    bw = b[2] - b[0] + 100
    x0 = (W - bw) // 2
    d.rounded_rectangle((x0, 70, x0 + bw, 190), radius=60, fill=YELLOW)
    d.text((x0 + 50 - b[0], 130 - (b[3] + b[1]) / 2), a.badge, font=bf, fill=(20, 20, 20))
    center(1230, a.line1, fit(d, a.line1, BOLD, 170, 1000), WHITE)
    center(1440, a.line2, fit(d, a.line2, BOLD, 170, 1000), YELLOW)
    if a.arabic:
        center(1660, a.arabic, fit(d, a.arabic, AR, 150, 1000, direction="rtl", language="ar"), WHITE, stroke=10,
               direction="rtl", language="ar")
    return im


def wide(a):
    W, H = 1280, 720
    im = Image.new("RGB", (W, H), (255, 246, 233))
    src = Image.open(a.image).convert("RGB")
    s = H / src.height if src.width / src.height > 540 / 720 else 540 / src.width
    src = src.resize((int(src.width * s), int(src.height * s)))
    im.paste(src.crop(((src.width - 540) // 2, (src.height - 720) // 2, (src.width + 540) // 2, (src.height + 720) // 2)),
             (W - 540, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((50, 50, 470, 130), radius=40, fill=YELLOW)
    f = fit(d, a.badge, BOLD, 46, 380)
    b = d.textbbox((0, 0), a.badge, font=f)
    d.text((50 + (420 - (b[2] - b[0])) / 2 - b[0], 90 - (b[3] + b[1]) / 2), a.badge, font=f, fill=(20, 20, 20))
    d.text((50, 160), a.line1, font=fit(d, a.line1, BOLD, 120, 660), fill=TEAL)
    d.text((50, 300), a.line2, font=fit(d, a.line2, BOLD, 120, 660), fill=TERRA)
    if a.line3:
        d.text((50, 450), a.line3, font=fit(d, a.line3, BOLD, 64, 660), fill=(51, 51, 51))
    if a.arabic:
        fa = fit(d, a.arabic, AR, 110, 660, direction="rtl", language="ar")
        b = d.textbbox((0, 0), a.arabic, font=fa, direction="rtl", language="ar")
        d.text((60 - b[0], 560 - b[1]), a.arabic, font=fa, fill=TEAL, direction="rtl", language="ar")
    return im


MISSING_GLYPHS = "→▶…_"   # not in Noto Sans Bold / Naskh Bold → would render as empty boxes


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("image")
    ap.add_argument("out")
    ap.add_argument("--badge", required=True)
    ap.add_argument("--line1", required=True)
    ap.add_argument("--line2", required=True)
    ap.add_argument("--line3", default="")
    ap.add_argument("--arabic", default="")
    ap.add_argument("--wide", action="store_true")
    a = ap.parse_args()
    for t in (a.badge, a.line1, a.line2, a.line3, a.arabic):
        if any(ch in MISSING_GLYPHS for ch in t or ""):
            raise SystemExit(f"'{t}' contains a character the fonts don't have ({MISSING_GLYPHS}) — rephrase")
    im = wide(a) if a.wide else vertical(a)
    im.save(a.out, quality=92)
    im.resize((im.width // 3, im.height // 3)).save(a.out.rsplit(".", 1)[0] + "-phone-size.png")
    print(f"{a.out} (+ phone-size preview)")


if __name__ == "__main__":
    main()
