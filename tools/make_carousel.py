#!/usr/bin/env python3
"""Instagram carousel from a word-list video (owner, 2026-10-30: "carousels are a good idea, start making them").
Saves are what bring followers on Instagram (Day 12: 38 saves → +66 follows); a swipeable word list is made to be saved.

    python3 tools/make_carousel.py videos/v02-body-words.md "10 BODY PARTS" "in Arabic" [pick=1,3,4,6,7,10] [extra=8]
      pick = which word cards (owner 2026-10-30: 4–8 slides in all → cover + 5–6 words + closing)
        → output/carousel/<stem>/slide-01.jpg … + caption.txt

Slides (1080×1350, Instagram's 4:5): a cover (title + the first picture), one slide per word card "N/10" from the
script (its own picture on top, the card below: Arabic big, transliteration, English), and a closing slide (follow +
YouTube). Post with: python3 tools/instagram_api.py carousel output/carousel/<stem> [--apply]
"""
import pathlib
import re
import sys

from PIL import Image, ImageDraw, ImageFilter, ImageFont

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from assemble import FONTS, on_screen_by_scene   # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parent.parent
W, H = 1080, 1350
EXTRA = set()
CREAM, TEAL, TERRA, INK, YELLOW = (253, 247, 236), (31, 95, 91), (196, 98, 52), (40, 40, 40), (246, 196, 0)
AR = ImageFont.truetype(str(FONTS / "NotoNaskhArabic-Bold.ttf"), 130)
BOLD = lambda s: ImageFont.truetype(str(FONTS / "NotoSans-Bold.ttf"), s)
ITAL = ImageFont.truetype(str(FONTS / "NotoSans-Italic.ttf"), 64)
REG = ImageFont.truetype(str(FONTS / "NotoSans-Regular.ttf"), 60)


def centered(d, y, text, font, fill):
    b = d.textbbox((0, 0), text, font=font)
    d.text(((W - (b[2] - b[0])) / 2 - b[0], y), text, font=font, fill=fill)
    return y + (b[3] - b[1])


def photo(path, box_h):
    """The whole scene picture, fitted to box_h and centred on a blurred, darkened copy of itself (nothing cut off —
    a body-part picture needs its head, a leg picture its feet)."""
    im = Image.open(path).convert("RGB")
    s = max(W / im.width, box_h / im.height)
    bg = im.resize((int(im.width * s) + 1, int(im.height * s) + 1), Image.LANCZOS)
    bg = bg.crop(((bg.width - W) // 2, (bg.height - box_h) // 2, (bg.width - W) // 2 + W, (bg.height - box_h) // 2 + box_h))
    bg = Image.blend(bg.filter(ImageFilter.GaussianBlur(28)), Image.new("RGB", (W, box_h), (30, 30, 30)), 0.25)
    f = box_h / im.height
    fg = im.resize((int(im.width * f), box_h), Image.LANCZOS)
    bg.paste(fg, ((W - fg.width) // 2, 0))
    return bg


def badge(d, text):
    f = BOLD(34); b = d.textbbox((0, 0), text, font=f); w = b[2] - b[0] + 60
    d.rounded_rectangle(((W - w) / 2, 34, (W + w) / 2, 98), radius=32, fill=YELLOW)
    centered(d, 46, text, f, INK)


def word_slide(img, arabic, translit, english, k, n):
    slide = Image.new("RGB", (W, H), CREAM)
    slide.paste(photo(img, 820), (0, 0))
    d = ImageDraw.Draw(slide)
    badge(d, f"2 MINUTE ARABIC  ·  {k}/{n}")
    d.rounded_rectangle((40, 760, W - 40, H - 40), radius=48, fill=CREAM)
    y = centered(d, 800, arabic, AR, TEAL) + 70
    y = centered(d, y, translit, ITAL, TERRA) + 40
    centered(d, y, english, BOLD(66), INK)
    return slide


def cover(img, title, sub, n):
    slide = photo(img, H).filter(ImageFilter.GaussianBlur(2))
    shade = Image.new("RGB", (W, H), (20, 20, 20)); slide = Image.blend(slide, shade, 0.45)
    d = ImageDraw.Draw(slide)
    badge(d, "2 MINUTE ARABIC")
    y = centered(d, 430, title, BOLD(120), (255, 255, 255)) + 40
    y = centered(d, y, sub, BOLD(80), YELLOW) + 120
    centered(d, y, f"swipe for all {n} words", REG, (255, 255, 255))
    centered(d, H - 150, "save it for later", BOLD(52), YELLOW)
    return slide


def closing():
    slide = Image.new("RGB", (W, H), TEAL)
    d = ImageDraw.Draw(slide)
    logo = ROOT / "assets" / "logo-clay-teacher-1024.png"
    if logo.exists():
        lg = Image.open(logo).convert("RGB").resize((420, 420), Image.LANCZOS)
        m = Image.new("L", lg.size, 0); ImageDraw.Draw(m).ellipse((0, 0, 419, 419), fill=255)
        slide.paste(lg, ((W - 420) // 2, 150), m)
    y = centered(d, 640, "A new Arabic lesson", BOLD(72), (255, 255, 255)) + 30
    y = centered(d, y, "every day, in 2 minutes", BOLD(72), (255, 255, 255)) + 90
    y = centered(d, y, "Follow @2minutearabic", BOLD(64), YELLOW) + 40
    centered(d, y, "Full course on YouTube · link in bio", REG, (255, 255, 255))
    return slide


def main():
    global EXTRA
    script = pathlib.Path(sys.argv[1]); title, sub = sys.argv[2], sys.argv[3]
    opt = dict(a.split("=", 1) for a in sys.argv[4:] if "=" in a)
    EXTRA = {int(x) for x in opt.get("extra", "").split(",") if x}   # extra=8 → also scene 8's card (a phrase)
    pick = [int(x) for x in opt.get("pick", "").split(",") if x]   # pick=1,3,4 → only these word cards (7–8 slides)
    imgdir = opt.get("imgdir")   # imgdir=library/work/carousel-v02 → pNN.png per word (dedicated close-ups, owner 2026-10-30)
    stem = script.stem
    screens = on_screen_by_scene(script)
    words = []
    for i, s in enumerate(screens, 1):
        parts = [p.strip().strip("*") for p in (s or "").split("·")]
        if len(parts) >= 4 and re.fullmatch(r"(Word |Phrase )?\d+/\d+", parts[-1]) or i in EXTRA:
            words.append((i, parts[0], parts[1], parts[2]))
    if not words:
        sys.exit("no 'N/M' word cards in this script")
    if pick:
        words = [words[k - 1] for k in pick]
    out = ROOT / "output" / "carousel" / stem; out.mkdir(parents=True, exist_ok=True)
    for f in out.glob("slide-*.jpg"): f.unlink()
    import json
    pj = ROOT / "images" / stem / "prompts.json"
    opts = {e["s"]: e for e in (json.loads(pj.read_text(encoding="utf-8")) if pj.exists() else []) if "s" in e}
    def img(n):   # follow the script's picture links ("same": scene, "from": another video's picture)
        for _ in range(5):
            o = opts.get(n, {}); f = ROOT / "images" / stem / f"s{n:02d}.png"
            if "same" in o: n = o["same"]; continue
            if "from" in o: return ROOT / "images" / o["from"]
            return f
        return f
    order = pick or list(range(1, len(words) + 1))   # original word numbers, for the pNN close-ups
    pic = lambda k, n: (ROOT / imgdir / f"p{order[k - 1]:02d}.png") if imgdir else img(n)
    cov = ROOT / imgdir / "cover.png" if imgdir else None   # a dedicated cover picture (owner 2026-10-30: full shot)
    slides = [cover(cov if cov and cov.exists() else pic(1, words[0][0]), title, sub, len(words))]
    slides += [word_slide(pic(k, n), a, t, e, k, len(words)) for k, (n, a, t, e) in enumerate(words, 1)]
    slides.append(closing())
    for k, s in enumerate(slides, 1):
        s.save(out / f"slide-{k:02d}.jpg", quality=92)
    # caption: the words as text (searchable, copyable) + the way to the full lesson (owner 2026-10-30)
    yt = re.search(r"\*\*YouTube title\*\* \| `([^`]+)`", script.read_text(encoding="utf-8"))
    lesson = yt.group(1).replace("\\|", "|").split(" | ")[0] if yt else "the full lesson"
    total = len([1 for x in screens if x and re.search(r"(Word |Phrase )?\d+/\d+$", x.strip())])
    more = f" (all {total} words)" if pick and total > len(words) else ""
    cap = (f"{title.title()} {sub} 👇 Save this and swipe through it once a day this week.\n\n"
           + "\n".join(f"{t} — {e}" for _, a, t, e in words)
           + f"\n\nFull lesson{more}: \"{lesson}\" on YouTube, link in bio ▶️\nWhich one will you use first? Tell me in the comments 👇\n\n"
           + "#learnarabic #arabicvocabulary #arabicforbeginners #2minutearabic\n")
    (out / "caption.txt").write_text(cap, encoding="utf-8")
    print(f"{len(slides)} slides → {out}")


if __name__ == "__main__":
    main()
