#!/usr/bin/env python3
"""Exact-count scenes: put N copies of a green-screen object (a coffee cup) on a background (an empty table).

    python3 tools/images/cups.py images/<video>     # reads prompts.json entries {"s": 5, "cups": 3[, "row": true]}

Needs images/<video>/table.png (empty table) and cup.png (one cup on chroma green), both made with generate.py from
the prompts.json entries {"key": "table"} / {"key": "cup"}. Image models can't count — compositing guarantees that
"three cups" really shows three cups. Cups go on the table top in neat rows (back row smaller), or one row if "row".
"""
import json
import pathlib
import sys

from PIL import Image, ImageDraw, ImageFilter


def cutout(path):
    """Key out the chroma green: strongly saturated green anywhere (incl. the hole in the handle), plus the weaker
    green shadow only where it connects to the image border — so the cup's own soft shading is never cut out."""
    import colorsys
    from collections import deque
    im = Image.open(path).convert("RGBA")
    px = im.load()
    w, h = im.size
    hsv = [[colorsys.rgb_to_hsv(*(v / 255 for v in px[x, y][:3])) for x in range(w)] for y in range(h)]
    green = lambda x, y, smin: 0.20 < hsv[y][x][0] < 0.50 and hsv[y][x][1] > smin
    bg = [[green(x, y, 0.62) for x in range(w)] for y in range(h)]
    q = deque((x, y) for x in range(w) for y in (0, h - 1)) + deque((x, y) for y in range(h) for x in (0, w - 1))
    seen = set()
    while q:
        x, y = q.popleft()
        if (x, y) in seen or not (0 <= x < w and 0 <= y < h) or not (green(x, y, 0.30) or (0.15 < hsv[y][x][0] < 0.55 and hsv[y][x][1] > 0.06 and hsv[y][x][2] < 0.72)):
            continue
        seen.add((x, y)); bg[y][x] = True
        q.extend(((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)))
    for y in range(h):
        for x in range(w):
            r, g, b, _ = px[x, y]
            px[x, y] = (r, g, b, 0) if bg[y][x] else (r, min(g, (r + b) // 2 + 6), b, 255)
    # the cup's own shadow on the green screen stays as a grey band under the saucer: cut below the saucer's rim
    bright_rows = [y for y in range(h) if sum(1 for x in range(w) if px[x, y][3] and sum(px[x, y][:3]) > 560) > w * 0.08]
    if bright_rows:
        for y in range(bright_rows[-1] + 4, h):
            for x in range(w):
                px[x, y] = (0, 0, 0, 0)
    return im.crop(im.getbbox())


def layout(n, row=False):
    """(x centre, y bottom, width as a share of the frame) per cup — never overlapping, using the full width
    (owner, 2026-10-05: from 3 cups on they overlapped). Up to 4 in one row; more = two rows (back row smaller)."""
    def row_of(k, y, scale):
        step = 0.94 / k
        w = min(0.24, 0.80 * step) * scale
        return [(0.03 + step * (j + 0.5), y, w) for j in range(k)]
    if n <= 4:
        return row_of(n, 0.585, 1.0)
    back = n // 2
    return row_of(back, 0.52, 0.85) + row_of(n - back, 0.645, 1.0)


def main():
    d = pathlib.Path(sys.argv[1])
    table = Image.open(d / "table.png").convert("RGBA")
    # zoom into the lower part so the table top sits mid-frame — the lower third is reserved for burned-in captions
    # and the YOUR TURN label (they covered the cups on the first build)
    tw, th = table.size
    table = table.crop((int(tw * 0.2), int(th * 0.4), int(tw * 0.8), th)).resize((tw, th), Image.LANCZOS)
    cup = cutout(d / "cup.png")
    W, H = table.size
    for e in json.loads((d / "prompts.json").read_text(encoding="utf-8")):
        if "cups" not in e:
            continue
        n, img = e["cups"], table.copy()
        for x, y, wf in layout(n, e.get("row")):
            cw = int(W * wf)
            c = cup.resize((cw, int(cup.height * cw / cup.width)))
            sh = Image.new("L", (cw, max(6, cw // 5)), 0)   # soft contact shadow under the saucer (alpha mask)
            ImageDraw.Draw(sh).ellipse((cw // 10, 0, cw - cw // 10, sh.height - 1), fill=70)
            sh = sh.filter(ImageFilter.GaussianBlur(cw // 18 + 1))
            dark = Image.new("RGBA", sh.size, (45, 28, 15, 255)); dark.putalpha(sh)
            img.alpha_composite(dark, (int(W * x - cw / 2), int(H * y - sh.height * 0.55)))
            img.alpha_composite(c, (int(W * x - cw / 2), int(H * y - c.height)))
        img.convert("RGB").save(d / f"s{e['s']:02d}.png")
        print(f"s{e['s']:02d}: {n} cups")


if __name__ == "__main__":
    main()
