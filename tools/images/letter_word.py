#!/usr/bin/env python3
"""An Arabic word (or letter) written big in pencil grey on white paper, one letter in red pencil — for the letters
series (owner 2026-11-19 "go" for Letter 1). The image model can't write, so we draw the text ourselves.

    python3 tools/images/letter_word.py out.png "أنا" --mark 0+2          # colour the letters at index 0 and 2 red
    python3 tools/images/letter_word.py out.png "كتاب" --mark 2
    python3 tools/images/letter_word.py out.png "ا   ـا" --mark all        # everything red (the letter's shapes)
    python3 tools/images/letter_word.py out.png "قهوة|شاي" --mark -,2     # two words side by side ("|"), marks per word

Output: 1216×832 like the pencil pictures, so tools/pencil_frame.py places it in the video the same way.
Marking works for letters that never join the next letter (ا د ذ ر ز و — and any letter at the END of a word): the
word is shaped as a whole, and the marked letter's columns are found by shaping the part after it on its own.
"""
import argparse
import random

from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont

FONT = "/usr/share/fonts/truetype/noto/NotoNaskhArabic-Bold.ttf"
W, H = 1216, 832
GREY, RED = (70, 70, 72), (196, 52, 44)
ZWJ = "‍"
NON_JOIN = set("اأإآدذرزوؤة ")   # letters that never join the NEXT letter


def width(font, s):
    if not s:
        return 0
    b = font.getbbox(s, direction="rtl")
    return b[2] - b[0]


def word_img(word, mark, size):
    font = ImageFont.truetype(FONT, size)
    l, t, r, b = font.getbbox(word, direction="rtl")
    pad = size // 4
    im = Image.new("L", (r - l + 2 * pad, b - t + 2 * pad), 0)
    ImageDraw.Draw(im).text((pad - l, pad - t), word, font=font, fill=255, direction="rtl")
    red = Image.new("L", im.size, 0)
    if mark == "all":
        red = im.copy()
    elif mark is not None:
        for i in mark:                                                               # one or more letter indexes
            suffix = word[i + 1:]
            x0 = pad + width(font, suffix) if suffix else pad                       # the suffix sits on the left
            joined = i > 0 and word[i - 1] not in NON_JOIN                          # joined to the letter before it
            lw = width(font, "\u0640" + word[i]) - width(font, "\u0640") if joined else width(font, word[i])
            x1 = x0 + lw                                                             # just this letter's own shape
            band = Image.new("L", im.size, 0); ImageDraw.Draw(band).rectangle([x0 - 2, 0, x1 + 2, im.height], fill=255)
            red = ImageChops.lighter(red, ImageChops.multiply(im, band))
    return im, red


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("out"); ap.add_argument("text"); ap.add_argument("--mark", default="")
    ap.add_argument("--size", type=int, default=0)
    a = ap.parse_args()
    words = a.text.split("|"); marks = (a.mark.split(",") + [""] * len(words))[:len(words)]
    size = a.size or (420 if max(len(w) for w in words) <= 2 else 300 if len(words) == 1 else 220)
    imgs = [word_img(w, None if m in ("", "-") else ("all" if m == "all" else [int(v) for v in m.split("+")]), size) for w, m in zip(words, marks)]
    gap = size // 2
    tw = sum(i[0].width for i in imgs) + gap * (len(imgs) - 1); th = max(i[0].height for i in imgs)
    ink = Image.new("L", (tw, th), 0); red = Image.new("L", (tw, th), 0); x = tw
    for im, rd in imgs:                       # first word on the right (reading order)
        x -= im.width; y = (th - im.height) // 2
        ink.paste(im, (x, y)); red.paste(rd, (x, y)); x -= gap
    s = min(1.0, (W * 0.86) / tw, (H * 0.8) / th)
    ink = ink.resize((int(tw * s), int(th * s)), Image.LANCZOS); red = red.resize(ink.size, Image.LANCZOS)
    rnd = random.Random(7)                    # pencil grain: a little noise in the strokes, soft edges
    grain = Image.effect_noise(ink.size, 60).point(lambda v: 255 - max(0, v - 128) // 2)
    ink = ImageChops.multiply(ink, grain).filter(ImageFilter.GaussianBlur(0.8))
    red = ImageChops.multiply(red, grain).filter(ImageFilter.GaussianBlur(0.8))
    paper = Image.new("RGB", (W, H), (255, 255, 255))
    ox, oy = (W - ink.width) // 2, (H - ink.height) // 2
    paper.paste(Image.new("RGB", ink.size, GREY), (ox, oy), ink)
    paper.paste(Image.new("RGB", ink.size, RED), (ox, oy), red)
    paper.save(a.out)


if __name__ == "__main__":
    main()
