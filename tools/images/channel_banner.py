#!/usr/bin/env python3
"""YouTube channel banner (owner 2026-11-04: "a good banner with the channel logo included" + the 2 Minute Arabic
text logo). 2560×1440; everything that matters sits in the 1546×423 safe area that every device shows.

    python3 tools/images/channel_banner.py OUT.png [--guides]
"""
import math, pathlib, sys
from PIL import Image, ImageDraw, ImageFilter, ImageFont

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from narrator_cutout import cutout, terracotta

ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
FONTS = ROOT / "assets" / "fonts" if (ROOT / "assets" / "fonts").exists() else ROOT / "fonts"
W, H = 2560, 1440
SAFE = ((W - 1546) // 2, (H - 423) // 2, (W + 1546) // 2, (H + 423) // 2)
TEAL, TEAL_D, YELLOW, CREAM, TERRA = (31, 95, 91), (18, 62, 60), (246, 196, 0), (253, 247, 236), (196, 98, 52)


def font(name, s):
    return ImageFont.truetype(str(FONTS / name), s)


def avatar(d):
    """The round channel logo: the 3D narrator on the clay logo's terracotta (assets/channel-logo-3d-800.png)."""
    lg = Image.open(ROOT / "assets/channel-logo-3d-800.png").convert("RGB").resize((d, d), Image.LANCZOS)
    m = Image.new("L", (d * 4, d * 4), 0); ImageDraw.Draw(m).ellipse((0, 0, d * 4 - 1, d * 4 - 1), fill=255)
    return lg, m.resize((d, d), Image.LANCZOS)


def clock_two(s):
    """The '2' of the text logo: a yellow clock face with the minute ticks and a teal 2."""
    im = Image.new("RGBA", (s * 4, s * 4), (0, 0, 0, 0)); d = ImageDraw.Draw(im); S = s * 4; c = S / 2
    d.ellipse((0, 0, S - 1, S - 1), fill=YELLOW)
    for k in range(12):
        a = math.radians(k * 30); r1, r2 = S * 0.45, S * (0.40 if k % 3 else 0.37)
        d.line((c + r1 * math.sin(a), c - r1 * math.cos(a), c + r2 * math.sin(a), c - r2 * math.cos(a)), fill=TEAL_D, width=int(S * .025))
    f = font("NotoSans-Bold.ttf", int(S * 0.68)); b = d.textbbox((0, 0), "2", font=f)
    d.text((c - (b[0] + b[2]) / 2, c - (b[1] + b[3]) / 2), "2", font=f, fill=TEAL_D)
    return im.resize((s, s), Image.LANCZOS)


def main():
    out = pathlib.Path(sys.argv[1])
    im = Image.new("RGB", (W, H), TEAL); px = im.load()
    for y in range(H):                                  # soft teal light from the upper middle
        for x in range(0, W, 4):
            t = min(1, math.hypot((x - W * .45) / W, (y - H * .35) / H) * 1.6)
            col = tuple(int(TEAL[i] * (1 - t) + TEAL_D[i] * t) for i in range(3))
            for dx in range(4): px[x + dx, y] = col
    # faint Arabic letters in the wide outer band (desktop/TV only)
    deco = Image.new("L", (W, H), 0); dd = ImageDraw.Draw(deco); fa = font("NotoNaskhArabic-Bold.ttf", 300)
    for (x, y, ch) in [(140, 380, "ع"), (330, 860, "ب"), (2180, 300, "ر"), (2330, 820, "ي"), (60, 1060, "س"), (2060, 1080, "م")]:
        dd.text((x, y), ch, font=fa, fill=34)
    im.paste(Image.new("RGB", (W, H), CREAM), (0, 0), deco)

    d = ImageDraw.Draw(im)
    x0, y0, x1, y1 = SAFE; cy = (y0 + y1) // 2
    # the text logo + promise, three lines: [clock 2] Minute Arabic / العربية في دقيقتين / LEARN ARABIC · …
    C, f1 = 150, font("NotoSans-Bold.ttf", 124)
    far, f3 = font("NotoNaskhArabic-Bold.ttf", 66), font("NotoSans-Bold.ttf", 42)
    L3 = "A NEW LESSON EVERY DAY"
    tw = max(C + 24 + d.textlength("Minute Arabic", font=f1), d.textlength(L3, font=f3))
    D, gap = 340, 70                                      # the round logo (cream ring), then the text
    total = D + 24 + gap + tw; lx = int((x0 + x1 - total) / 2)
    ring = Image.new("L", (D + 24, D + 24), 0); ImageDraw.Draw(ring).ellipse((0, 0, D + 23, D + 23), fill=255)
    sh = Image.new("L", (W, H), 0); ImageDraw.Draw(sh).ellipse((lx + 4, cy - D // 2 + 2, lx + D + 28, cy + D // 2 + 26), fill=90)
    im.paste(Image.new("RGB", (W, H), (8, 30, 28)), (0, 0), sh.filter(ImageFilter.GaussianBlur(14)))
    im.paste(Image.new("RGB", ring.size, CREAM), (lx, cy - D // 2 - 12), ring)
    lg, m = avatar(D); im.paste(lg, (lx + 12, cy - D // 2), m)
    tx = lx + D + 24 + gap; ty = cy - 165
    two = clock_two(C); im.paste(two, (tx, ty), two)
    d.text((tx + C + 24, ty + C // 2 + 4), "Minute Arabic", font=f1, fill=(255, 255, 255), anchor="lm")
    d.text((tx + C + 24, ty + C + 62), "العربية في دقيقتين", font=far, fill=CREAM, anchor="lm", direction="rtl", language="ar")
    d.text((tx + C + 28, ty + C + 160), L3, font=f3, fill=YELLOW, anchor="lm")

    if "--guides" in sys.argv:
        g = ImageDraw.Draw(im); g.rectangle(SAFE, outline=(255, 0, 0), width=4)
        g.rectangle(((W - 2560) // 2, (H - 423) // 2, (W + 2560) // 2, (H + 423) // 2), outline=(255, 160, 0), width=3)   # desktop max
    im.save(out, optimize=True); print(out)


if __name__ == "__main__":
    main()
