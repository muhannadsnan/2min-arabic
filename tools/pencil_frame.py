#!/usr/bin/env python3
"""Pencil picture -> centred, zoomed 1080x1920 frame on white paper.

  pencil_frame.py in.png out.png [--box 1020x880] [--cy 0.70]

Finds the main drawing (where most of the pencil is — stray marks near the edges are ignored), zooms it so it
fills the box (more empty paper = more zoom), centres it on the page and fades the cut edges into white.
Paper: border median scaled to 250, then a LUT (<195 keep, >=228 white, linear between)."""
import argparse
import numpy as np
from PIL import Image, ImageFilter

ap = argparse.ArgumentParser()
ap.add_argument("inp"); ap.add_argument("out")
ap.add_argument("--box", default="1020x880"); ap.add_argument("--cy", type=float, default=0.70)
ap.add_argument("--margin", type=float, default=0.06)
ap.add_argument("--keep", type=float, default=0.78, help="never cut more than this share of the drawing's height off")
ap.add_argument("--minw", type=float, default=0.62, help="narrow tall drawings zoom until this share of the box width; the bottom runs off the page")
a = ap.parse_args()
BW, BH = map(int, a.box.split("x"))
W, H = 1080, 1920

im = np.asarray(Image.open(a.inp).convert("RGB")).astype(np.float32)
h, w, _ = im.shape
b = 12
border = np.concatenate([im[:b].reshape(-1, 3), im[-b:].reshape(-1, 3), im[:, :b].reshape(-1, 3), im[:, -b:].reshape(-1, 3)])
im = np.clip(im * (250.0 / np.maximum(np.median(border, 0), 1)), 0, 255)
lut = np.arange(256, dtype=np.float32)
mid = (lut >= 195) & (lut < 228)
lut[mid] = 195 + (lut[mid] - 195) * (255 - 195) / (228 - 195)
lut[lut >= 228] = 255
im = lut[im.astype(np.uint8)]

# main drawing: ink density blurred, then the smallest box holding ~97 % of the dense ink
grey = im.mean(2)
ink = (grey < 200).astype(np.float32)
dens = np.asarray(Image.fromarray((ink * 255).astype(np.uint8)).filter(ImageFilter.BoxBlur(15))).astype(np.float32) / 255
main = ink * (dens > 0.04)
if main.sum() < 500: main = ink
col, row = main.sum(0), main.sum(1)
def span(p, lo=0.004, hi=0.996):
    c = np.cumsum(p) / p.sum()
    return int(np.searchsorted(c, lo)), int(np.searchsorted(c, hi))
x0, x1 = span(col); y0, y1 = span(row)
mx, my = (x1 - x0) * a.margin + 10, (y1 - y0) * a.margin + 10
x0, x1 = max(0, int(x0 - mx)), min(w, int(x1 + mx))
y0, y1 = max(0, int(y0 - my)), min(h, int(y1 + my))
crop = im[y0:y1, x0:x1]
ch, cw = crop.shape[:2]

# fade the cut edges (only where the crop cuts into the picture, not at the picture's own border)
f = 28
mask = np.ones((ch, cw), np.float32)
ramp = np.linspace(0, 1, f)
if x0 > 0: mask[:, :f] *= ramp[None, :min(f, cw)]
if x1 < w: mask[:, -f:] *= ramp[::-1][None, :min(f, cw)]
if y0 > 0: mask[:f, :] *= ramp[:min(f, ch), None]
if y1 < h: mask[-f:, :] *= ramp[::-1][:min(f, ch), None]
crop = 255 - (255 - crop) * mask[..., None]

z = min(BW / cw, BH / ch)
top = int(H * a.cy - ch * z / 2)
if cw * z < a.minw * BW:          # tall + narrow (full-body figure): zoom more, head stays at the box top, legs run off
    z = max(z, min(a.minw * BW / cw, (H - top) / (a.keep * ch)))
nw, nh = int(round(cw * z)), int(round(ch * z))
pic = Image.fromarray(crop.astype(np.uint8)).resize((nw, nh), Image.LANCZOS)
if top + nh > H:                   # soft fade where the page cuts the drawing
    keep = H - top
    arr = np.asarray(pic.crop((0, 0, nw, keep))).astype(np.float32)
    fade = np.ones(keep, np.float32); n = min(90, keep); fade[-n:] = np.linspace(1, 0, n)
    pic = Image.fromarray((255 - (255 - arr) * fade[:, None, None]).astype(np.uint8))
page = Image.new("RGB", (W, H), (255, 255, 255))
page.paste(pic, ((W - nw) // 2, top))
page.save(a.out)
print(f"{a.inp}: drawing {cw}x{ch} at x{x0}-{x1} y{y0}-{y1}, zoom {z:.2f}")
