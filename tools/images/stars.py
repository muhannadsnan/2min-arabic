#!/usr/bin/env python3
"""Draw the progress-star assets (owner, 2026-10-17): assets/stars/grey.png, gold.png and pop.mov (a 14-frame gold
pop with a glow). 3D look: 10 bevelled facets lit from the top left, edge line, drop shadow, specular highlight.
    python3 tools/images/stars.py
"""
import math, pathlib, subprocess
from PIL import Image, ImageDraw, ImageFilter
D = pathlib.Path(__file__).resolve().parent.parent.parent / "assets" / "stars"; X = 4; S = 160
GOLD = {"light": (255, 240, 150), "dark": (196, 118, 0), "edge": (120, 70, 0), "glass": True}
GREY = {"light": (205, 210, 216), "dark": (110, 115, 122), "edge": (55, 58, 64)}

def star(pal, alpha=255, scale=1.0, glow=False, canvas=S):
    B = canvas * X; im = Image.new("RGBA", (B, B), (0, 0, 0, 0)); cx = cy = B / 2; R = S * X * 0.40 * scale; r = R * 0.46
    outer = [(cx + R * math.sin(2 * math.pi * k / 5), cy - R * math.cos(2 * math.pi * k / 5)) for k in range(5)]
    inner = [(cx + r * math.sin(2 * math.pi * (k + .5) / 5), cy - r * math.cos(2 * math.pi * (k + .5) / 5)) for k in range(5)]
    pts = [p for k in range(5) for p in (outer[k], inner[k])]
    if glow:
        g = Image.new("RGBA", im.size, (0, 0, 0, 0)); ImageDraw.Draw(g).polygon(pts, fill=(255, 220, 90, int(190 * alpha / 255)))
        im = Image.alpha_composite(im, g.filter(ImageFilter.GaussianBlur(16 * X)))
    sh = Image.new("RGBA", im.size, (0, 0, 0, 0))
    ImageDraw.Draw(sh).polygon([(x + 5 * X, y + 7 * X) for x, y in pts], fill=(0, 0, 0, int(120 * alpha / 255)))
    im = Image.alpha_composite(im, sh.filter(ImageFilter.GaussianBlur(5 * X))); d = ImageDraw.Draw(im)
    for i in range(10):
        p1, p2 = pts[i], pts[(i + 1) % 10]
        mx, my = (p1[0] + p2[0]) / 2 - cx, (p1[1] + p2[1]) / 2 - cy; n = math.hypot(mx, my) or 1
        t = ((mx / n * -0.6 + my / n * -0.8) * (1 if i % 2 == 0 else 0.55) + 1) / 2
        d.polygon([(cx, cy), p1, p2], fill=tuple(int(pal["dark"][j] + (pal["light"][j] - pal["dark"][j]) * t) for j in range(3)) + (alpha,))
    d.polygon(pts, outline=pal["edge"] + (alpha,), width=int(4.5 * X))
    if pal.get("glass"):   # glassy: gloss over the top half, bright rim, a white streak (owner, 2026-10-17)
        mask = Image.new("L", im.size, 0); ImageDraw.Draw(mask).polygon(pts, fill=255)
        mask = mask.filter(ImageFilter.MinFilter(int(4 * X) | 1))
        grad = Image.new("L", im.size, 0); gd = ImageDraw.Draw(grad)
        top, mid = cy - R, cy + R * 0.05
        for yy in range(int(top), int(mid)):
            gd.line([(0, yy), (B, yy)], fill=int(150 * (1 - (yy - top) / (mid - top)) ** 1.4))
        gloss = Image.new("RGBA", im.size, (255, 255, 240, 0)); gloss.putalpha(Image.composite(grad, Image.new("L", im.size, 0), mask))
        im = Image.alpha_composite(im, gloss)
        rim = Image.new("RGBA", im.size, (0, 0, 0, 0)); ImageDraw.Draw(rim).polygon(pts, outline=(255, 245, 190, int(200 * alpha / 255)), width=int(2 * X))
        im = Image.alpha_composite(im, rim.filter(ImageFilter.GaussianBlur(1.2 * X)))
        st = Image.new("RGBA", im.size, (0, 0, 0, 0))
        ImageDraw.Draw(st).line([(cx - R * 0.55, cy - R * 0.02), (cx - R * 0.08, cy - R * 0.62)], fill=(255, 255, 255, int(210 * alpha / 255)), width=int(5 * X))
        im = Image.alpha_composite(im, Image.composite(st.filter(ImageFilter.GaussianBlur(2.5 * X)), Image.new("RGBA", im.size, (0, 0, 0, 0)), mask))
        d = ImageDraw.Draw(im)
    return im.resize((canvas, canvas), Image.LANCZOS)

(D / "pop").mkdir(parents=True, exist_ok=True)
g, o = star(GREY, 225), star(GOLD)
bb = o.getbbox(); (D / "bbox.txt").write_text(" ".join(map(str, bb)))   # assemble.py scales the pop to match
g.crop(bb).save(D / "grey.png"); o.crop(bb).save(D / "gold.png")
for f in (D / "pop").glob("*.png"): f.unlink()
for i in range(14):
    t = i / 13; star(GOLD, int(255 * min(1, i / 3)), 1.0 + 0.55 * (1 - t) ** 2, glow=i < 11, canvas=2 * S).save(D / "pop" / f"{i:02d}.png")   # 2× canvas: the glow never clips
subprocess.run(["ffmpeg", "-v", "error", "-y", "-framerate", "30", "-i", str(D / "pop" / "%02d.png"), "-c:v", "png",
                "-pix_fmt", "rgba", str(D / "pop.mov")], check=True)
print("stars drawn →", D)
