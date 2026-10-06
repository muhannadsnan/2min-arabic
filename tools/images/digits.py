#!/usr/bin/env python3
"""Arabic digits written in chalk on an empty chalkboard — the image model can't write, so we draw them.

    python3 tools/images/digits.py images/<video>     # reads prompts.json entries {"s": 2, "digit": "١"}

Needs images/<video>/board.png (an empty chalkboard, made with generate.py from the {"key": "board"} prompt).
The board area is found automatically (the large dark-green region); the digit fills ~48 % of its height, a little above the middle
(clear of the card above and the burned-in captions below — they crossed the digit on the first build),
chalk-white with a little grain and softness so it looks written, not printed.
"""
import json
import pathlib
import random
import sys

from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont

AR_FONT = "/usr/share/fonts/truetype/noto/NotoNaskhArabic-Bold.ttf"


def board_box(im):
    """Bounding box of the dark-green chalkboard (rows/columns where most pixels are dark green)."""
    small = im.convert("RGB").resize((im.width // 4, im.height // 4))
    w, h = small.size
    px = small.load()
    green = [[(lambda r, g, b: g >= r and g >= b - 10 and r + g + b < 300)(*px[x, y]) for x in range(w)] for y in range(h)]
    rows = [y for y in range(h) if sum(green[y]) > w * 0.45]
    if not rows:
        sys.exit("no chalkboard found in board.png")
    y0, y1 = rows[0], rows[-1]
    cols = [x for x in range(w) if sum(green[y][x] for y in range(y0, y1 + 1)) > (y1 - y0) * 0.6]
    return cols[0] * 4, y0 * 4, cols[-1] * 4, y1 * 4


def chalk(board, text, box):
    x0, y0, x1, y1 = box
    bw, bh = x1 - x0, y1 - y0
    size = int(bh * 0.75)
    while True:
        font = ImageFont.truetype(AR_FONT, size)
        tb = ImageDraw.Draw(board).textbbox((0, 0), text, font=font, direction="rtl", language="ar")
        if tb[2] - tb[0] <= bw * 0.62 and tb[3] - tb[1] <= bh * 0.48:
            break
        size -= 8
    mask = Image.new("L", board.size, 0)
    ImageDraw.Draw(mask).text((x0 + (bw - (tb[2] - tb[0])) / 2 - tb[0], y0 + bh * 0.42 - (tb[3] - tb[1]) / 2 - tb[1]),
                              text, font=font, fill=235, direction="rtl", language="ar")
    rnd = random.Random(7)
    grain = Image.new("L", board.size)
    grain.putdata([rnd.randint(150, 255) for _ in range(board.width * board.height)])
    mask = ImageChops.multiply(mask.filter(ImageFilter.GaussianBlur(1.6)), grain.filter(ImageFilter.GaussianBlur(0.6)))
    out = board.convert("RGB").copy()
    out.paste(Image.new("RGB", board.size, (244, 242, 232)), (0, 0), mask)
    return out


def main():
    d = pathlib.Path(sys.argv[1])
    board = Image.open(d / "board.png")
    box = board_box(board)
    print(f"board area {box}")
    for e in json.loads((d / "prompts.json").read_text(encoding="utf-8")):
        if "digit" in e:
            chalk(board, e["digit"], box).save(d / f"s{e['s']:02d}.png")
            print(f"s{e['s']:02d}: {e['digit']}")


if __name__ == "__main__":
    main()
