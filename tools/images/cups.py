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

from PIL import Image


def cutout(path):
    im = Image.open(path).convert("RGBA")
    px = im.load()
    w, h = im.size
    for y in range(h):
        for x in range(w):
            r, g, b, _ = px[x, y]
            if g > 90 and g > 1.3 * r and g > 1.3 * b:
                px[x, y] = (r, g, b, 0)
            else:
                px[x, y] = (r, min(g, int(1.12 * max(r, b))), b, 255)
    return im.crop(im.getbbox())


def layout(n, row=False):
    """(x centre, y bottom, scale) per cup, as fractions of the table area."""
    if row or n <= 4:
        return [((k + 1) / (n + 1), 0.62, 1.0) for k in range(n)]
    back = n // 2
    front = n - back
    return ([((k + 1) / (back + 1), 0.50, 0.82) for k in range(back)] +
            [((k + 1) / (front + 1), 0.70, 1.0) for k in range(front)])


def main():
    d = pathlib.Path(sys.argv[1])
    table = Image.open(d / "table.png").convert("RGBA")
    cup = cutout(d / "cup.png")
    W, H = table.size
    for e in json.loads((d / "prompts.json").read_text(encoding="utf-8")):
        if "cups" not in e:
            continue
        n, img = e["cups"], table.copy()
        base_w = int(W * (0.15 if (e.get("row") or n > 6) else 0.2))
        for x, y, sc in layout(n, e.get("row")):
            cw = int(base_w * sc)
            c = cup.resize((cw, int(cup.height * cw / cup.width)))
            img.alpha_composite(c, (int(W * x - cw / 2), int(H * y - c.height)))
        img.convert("RGB").save(d / f"s{e['s']:02d}.png")
        print(f"s{e['s']:02d}: {n} cups")


if __name__ == "__main__":
    main()
