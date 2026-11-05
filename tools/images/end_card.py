#!/usr/bin/env python3
"""End card for the long videos (owner 2026-11-05: "a last frame … the YouTube, Insta, Facebook accounts in the middle,
5–10 s"). The banner's look: teal, the round 3D-narrator logo, the text logo, then the three accounts in the middle.
The left and right thirds stay calm so the YouTube end-screen elements (a video, Subscribe) can sit there.

    python3 tools/images/end_card.py OUT.png
"""
import pathlib, sys
from PIL import Image, ImageDraw, ImageFilter

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from channel_banner import TEAL, TEAL_D, YELLOW, CREAM, avatar, clock_two, font

W, H = 1920, 1080


def yt_icon(s):
    im = Image.new("RGBA", (s * 4, s * 4), (0, 0, 0, 0)); d = ImageDraw.Draw(im); S = s * 4
    d.rounded_rectangle((0, S * .16, S, S * .84), S * .2, fill=(255, 0, 0))
    d.polygon([(S * .40, S * .33), (S * .40, S * .67), (S * .69, S * .5)], fill=(255, 255, 255))
    return im.resize((s, s), Image.LANCZOS)


def ig_icon(s):
    S = s * 4; g = Image.new("RGB", (S, S)); px = g.load()
    a, b, c = (254, 218, 117), (214, 41, 118), (79, 91, 213)        # Instagram's gradient, bottom-left → top-right
    for y in range(S):
        for x in range(S):
            t = (x + (S - y)) / (2 * S)
            px[x, y] = tuple(int(a[i] + (b[i] - a[i]) * t * 2) if t < .5 else int(b[i] + (c[i] - b[i]) * (t - .5) * 2) for i in range(3))
    m = Image.new("L", (S, S), 0); ImageDraw.Draw(m).rounded_rectangle((0, 0, S - 1, S - 1), S * .28, fill=255)
    im = Image.new("RGBA", (S, S), (0, 0, 0, 0)); im.paste(g, (0, 0), m); d = ImageDraw.Draw(im); w = int(S * .085)
    d.rounded_rectangle((S * .2, S * .2, S * .8, S * .8), S * .18, outline="white", width=w)
    d.ellipse((S * .35, S * .35, S * .65, S * .65), outline="white", width=w)
    d.ellipse((S * .66, S * .26, S * .74, S * .34), fill="white")
    return im.resize((s, s), Image.LANCZOS)


def fb_icon(s):
    im = Image.new("RGBA", (s * 4, s * 4), (0, 0, 0, 0)); d = ImageDraw.Draw(im); S = s * 4
    d.ellipse((0, 0, S - 1, S - 1), fill=(24, 119, 242))
    f = font("NotoSans-Bold.ttf", int(S * .78)); d.text((S * .54, S * .58), "f", font=f, fill="white", anchor="mm")
    return im.resize((s, s), Image.LANCZOS)


def main():
    out = pathlib.Path(sys.argv[1])
    im = Image.new("RGB", (W, H), TEAL); px = im.load()
    for y in range(H):                                  # the banner's soft light from the middle
        for x in range(0, W, 4):
            t = min(1, (((x - W / 2) / W) ** 2 + ((y - H * .4) / H) ** 2) ** .5 * 1.7)
            col = tuple(int(TEAL[i] * (1 - t) + TEAL_D[i] * t) for i in range(3))
            for dx in range(4): px[x + dx, y] = col
    # faint Arabic letters spread around, like the banner (owner 2026-11-05)
    deco = Image.new("L", (W, H), 0); dd = ImageDraw.Draw(deco); fa = font("NotoNaskhArabic-Bold.ttf", 230)
    for x, y, ch in [(90, 40, "ع"), (330, 560, "ب"), (40, 760, "س"), (1560, 60, "ر"), (1720, 470, "ي"), (1430, 760, "م"),
                     (520, 120, "ك"), (1250, 20, "ح")]:
        dd.text((x, y), ch, font=fa, fill=30)
    im.paste(Image.new("RGB", (W, H), CREAM), (0, 0), deco)
    d = ImageDraw.Draw(im)
    D = 250; lx, ly = (W - D) // 2, 80                  # the round logo with a cream ring
    ring = Image.new("L", (D + 20, D + 20), 0); ImageDraw.Draw(ring).ellipse((0, 0, D + 19, D + 19), fill=255)
    sh = Image.new("L", (W, H), 0); ImageDraw.Draw(sh).ellipse((lx - 4, ly + 4, lx + D + 24, ly + D + 28), fill=90)
    im.paste(Image.new("RGB", (W, H), (8, 30, 28)), (0, 0), sh.filter(ImageFilter.GaussianBlur(12)))
    im.paste(Image.new("RGB", ring.size, CREAM), (lx - 10, ly - 10), ring)
    lg, m = avatar(D); im.paste(lg, (lx, ly), m)
    C, f1 = 96, font("NotoSans-Bold.ttf", 84)           # the text logo: [clock 2] Minute Arabic
    tw = C + 18 + d.textlength("Minute Arabic", font=f1); tx = int((W - tw) / 2); ty = ly + D + 44
    two = clock_two(C); im.paste(two, (tx, ty), two)
    d.text((tx + C + 18, ty + C // 2 + 3), "Minute Arabic", font=f1, fill="white", anchor="lm")
    d.text((W / 2, ty + C + 50), "A new Arabic lesson every day", font=font("NotoSans-Regular.ttf", 40), fill=CREAM, anchor="mm")
    rows = [(yt_icon, "YouTube", "@2MinArabic"), (ig_icon, "Instagram", "@2minutearabic"), (fb_icon, "Facebook", "2 Minute Arabic")]
    fs, fn = font("NotoSans-Bold.ttf", 50), font("NotoSans-Regular.ttf", 30)
    I = 70; colw = I + 26 + max(d.textlength(h, font=fs) for _, _, h in rows); cx0 = int((W - colw) / 2)
    y = ty + C + 120
    for icon, name, handle in rows:
        ic = icon(I); im.paste(ic, (cx0, y), ic)
        d.text((cx0 + I + 26, y + 6), handle, font=fs, fill="white", anchor="lt")
        d.text((cx0 + I + 28, y + 62), name, font=fn, fill=YELLOW, anchor="lt")
        y += 118
    im.save(out); print(out)


if __name__ == "__main__":
    main()
