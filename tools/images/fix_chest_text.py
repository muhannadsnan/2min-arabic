#!/usr/bin/env python3
"""Replace whatever the image model wrote on a sweater with the real words (it garbles text): finds the bright-white
writing on the dark chest, covers it with sweater texture cloned from beside it, and paints the words in soft white.

    python3 tools/images/fix_chest_text.py in.png out.png [--text "2min|arabic"] [--region x0,y0,x1,y1 (fractions)]
"""
import argparse
from PIL import Image, ImageDraw, ImageFont, ImageFilter

ap = argparse.ArgumentParser()
ap.add_argument("inp"); ap.add_argument("out")
ap.add_argument("--text", default="2min|arabic")
ap.add_argument("--region", default="0.2,0.3,0.85,0.75", help="where to look for the old writing (fractions)")
a = ap.parse_args()
im = Image.open(a.inp).convert("RGB"); W, H = im.size
rx0, ry0, rx1, ry1 = [float(v) for v in a.region.split(",")]
px = im.load(); xs, ys = [], []
for y in range(int(ry0 * H), int(ry1 * H)):
    for x in range(int(rx0 * W), int(rx1 * W)):
        r, g, b = px[x, y]
        if r > 185 and g > 185 and b > 175:
            xs.append(x); ys.append(y)
if not xs:
    raise SystemExit("no writing found — pass --region")
pad = int(W * 0.012)
x0, y0, x1, y1 = min(xs) - pad, min(ys) - pad, max(xs) + pad, max(ys) + pad
bw, bh = x1 - x0, y1 - y0
# the words are wider than most garbles: make the box at least wide enough for them
lines = a.text.split("|")
fsize = max(int(W * 0.034), int(bh / (len(lines) * 1.25)))
f = ImageFont.truetype("/usr/share/fonts/truetype/noto/NotoSans-Bold.ttf", fsize)
d0 = ImageDraw.Draw(im)
tw = max(d0.textbbox((0, 0), ln, font=f)[2] for ln in lines); th = sum(d0.textbbox((0, 0), ln, font=f)[3] for ln in lines)
cx, cy = (x0 + x1) // 2, (y0 + y1) // 2
X0, Y0 = min(x0, cx - tw // 2 - pad), min(y0, cy - th // 2 - pad)
X1, Y1 = max(x1, cx + tw // 2 + pad), max(y1, cy + th // 2 + pad)
cw, ch = X1 - X0, Y1 - Y0
src_x = X0 - int(cw * 1.15) if X0 - int(cw * 1.15) > 0 else X1 + int(cw * 0.15)   # plain sweater beside it
src = im.crop((src_x, Y0, src_x + cw, Y1))
m = Image.new("L", (cw, ch), 0); ImageDraw.Draw(m).rounded_rectangle((4, 4, cw - 5, ch - 5), radius=14, fill=255)
im.paste(src, (X0, Y0), m.filter(ImageFilter.GaussianBlur(5)))
layer = Image.new("RGBA", im.size, (0, 0, 0, 0)); d = ImageDraw.Draw(layer)
y = cy - th // 2
for ln in lines:
    b = d.textbbox((0, 0), ln, font=f)
    d.text((cx - (b[2] - b[0]) // 2 - b[0], y - b[1]), ln, font=f, fill=(240, 238, 230, 255)); y += (b[3] - b[1]) + int(fsize * 0.2)
im = Image.alpha_composite(im.convert("RGBA"), layer.filter(ImageFilter.GaussianBlur(0.8))).convert("RGB")
im.save(a.out); print(a.out, "text box", (X0, Y0, X1, Y1))
