#!/usr/bin/env python3
"""Arabic digits written in chalk on an empty chalkboard — the image model can't write, so we draw them.

    python3 tools/images/digits.py images/<video>     # reads prompts.json entries {"s": 2, "digit": "١"}
                                                      # or {"s": 4, "chalk": "my book"} (English, Arabic or digits;
                                                      # "\n" = a second line) — the board-style quiz (Day 14)

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

# Kufi digits: ٢ with a straight top (a 7 facing the other way) — the curly Naskh ٢ confused beginners (owner, 2026-10-06)
AR_FONT = "/usr/share/fonts/truetype/noto/NotoKufiArabic-Bold.ttf"
NASKH = "/usr/share/fonts/truetype/noto/NotoNaskhArabic-Bold.ttf"   # Arabic words (with tashkeel)
LATIN = "/usr/share/fonts/truetype/noto/NotoSans-Bold.ttf"          # English questions


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


def font_for(text):
    if all("\u0660" <= ch <= "\u0669" for ch in text.strip()):
        return AR_FONT, {"direction": "rtl", "language": "ar"}
    if any("\u0600" <= ch <= "\u06ff" for ch in text):
        return NASKH, {"direction": "rtl", "language": "ar"}
    return LATIN, {}


def chalk(board, text, box):
    x0, y0, x1, y1 = box
    bw, bh = x1 - x0, y1 - y0
    lines = text.split("\n")
    path, kw = font_for(text)
    d = ImageDraw.Draw(board)
    size = int(bh * 0.75)
    while True:   # largest size where every line fits the board's middle area
        font = ImageFont.truetype(path, size)
        boxes = [d.textbbox((0, 0), ln, font=font, **kw) for ln in lines]
        gap = int(size * 0.25)
        total = sum(b[3] - b[1] for b in boxes) + gap * (len(lines) - 1)
        if max(b[2] - b[0] for b in boxes) <= bw * (0.62 if path == AR_FONT else 0.9) and total <= bh * (0.48 if path == AR_FONT else 0.55):
            break
        size -= 6
    mask = Image.new("L", board.size, 0)
    md = ImageDraw.Draw(mask)
    y = y0 + bh * 0.42 - total / 2
    for ln, b in zip(lines, boxes):
        md.text((x0 + (bw - (b[2] - b[0])) / 2 - b[0], y - b[1]), ln, font=font, fill=235, **kw)
        y += (b[3] - b[1]) + gap
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
        if "digit" in e or "chalk" in e:
            text = e.get("digit") or e["chalk"]
            chalk(board, text, box).save(d / f"s{e['s']:02d}.png")
            print(f"s{e['s']:02d}: {text!r}")


if __name__ == "__main__":
    main()
