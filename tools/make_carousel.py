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
from arabic_text import minimal   # noqa: E402

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


def is_drawing(im):
    return sum(im.convert("L").resize((64, 64)).get_flattened_data()) / 4096 > 200   # mostly white paper


def trimmed(im, pad=0.06):
    """A drawing on white paper cut to the drawing itself (owner 2026-11-09: "enlarge the image as double"), paper → white."""
    # flat-field: divide by the paper's own brightness (a wide blur of the brightest nearby pixels), so grey or
    # unevenly lit paper turns pure white everywhere (the thumbs-up came on grey paper → a grey box on the slide)
    small = im.convert("L").resize((im.width // 8, im.height // 8))
    bg = small.filter(ImageFilter.MaxFilter(9)).filter(ImageFilter.GaussianBlur(12)).resize(im.size, Image.BILINEAR)
    from PIL import ImageMath
    im = Image.merge("RGB", [ImageMath.lambda_eval(lambda e: e["convert"](e["min"](e["c"] * 262.65 / e["max"](e["bg"], 1), 255), "L"),
                                                   c=ch.convert("F"), bg=bg.convert("F")) for ch in im.split()])
    ink = im.convert("L").point(lambda v: 255 if v < 238 else 0).filter(ImageFilter.GaussianBlur(5)).point(lambda v: 255 if v > 40 else 0)   # faint pencil counts (the thumbs-down's thumb was cut off)
    box = ink.getbbox() or (0, 0, im.width, im.height)   # faint loose strokes far out don't count (blur + threshold)
    px, py = int((box[2] - box[0]) * pad), int((box[3] - box[1]) * pad)
    return im.crop((max(0, box[0] - px), max(0, box[1] - py), min(im.width, box[2] + px), min(im.height, box[3] + py)))


def fit_white(im, w, h, top=0, bottom=0, side=0):
    """The trimmed drawing as big as fits w×h (minus the margins) on white, edges softened into the paper."""
    out = Image.new("RGB", (w, h), (255, 255, 255)); ih = h - top - bottom
    s = min((w - 2 * side) / im.width, ih / im.height); p = im.resize((int(im.width * s), int(im.height * s)), Image.LANCZOS)
    m = Image.new("L", p.size, 0); ImageDraw.Draw(m).rectangle((18, 18, p.width - 19, p.height - 19), fill=255)
    out.paste(p, ((w - p.width) // 2, top + (ih - p.height) // 2), m.filter(ImageFilter.GaussianBlur(10)))
    return out


def photo(path, box_h):
    """The whole scene picture, fitted to box_h and centred on a blurred, darkened copy of itself (nothing cut off —
    a body-part picture needs its head, a leg picture its feet)."""
    im = Image.open(path).convert("RGB")
    if is_drawing(im):   # drawing style: no dark blur, the drawing itself as big as the space allows
        return fit_white(trimmed(im), W, box_h, top=110, bottom=75, side=40)   # badge on top, the word card below
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
    pic = Image.open(img).convert("RGB")
    if is_drawing(pic):   # a drawing on white paper (owner 2026-11-09):
        return cover_light(pic, title, sub, n)                           # darkening it gave a muddy grey slide
    slide = photo(img, H).filter(ImageFilter.GaussianBlur(2))
    shade = Image.new("RGB", (W, H), (20, 20, 20)); slide = Image.blend(slide, shade, 0.45)
    d = ImageDraw.Draw(slide)
    badge(d, "2 MINUTE ARABIC")
    size = 120   # shrink a long title so it fits the slide width (18: "5 QUESTION WORDS" was cut off)
    while size > 70 and d.textlength(title, font=BOLD(size)) > W - 80:
        size -= 6
    y = centered(d, 430, title, BOLD(size), (255, 255, 255)) + 40
    y = centered(d, y, sub, BOLD(80), YELLOW) + 120
    centered(d, y, f"swipe for all {n} {'phrases' if 'PHRASE' in title.upper() else 'words'}", REG, (255, 255, 255))
    centered(d, H - 150, "save it for later", BOLD(52), YELLOW)
    return slide


def cover_light(pic, title, sub, n):
    """The cover for drawing-style pictures: white paper, the title in dark teal on top, the whole drawing below."""
    slide = Image.new("RGB", (W, H), (255, 255, 255)); d = ImageDraw.Draw(slide)
    badge(d, "2 MINUTE ARABIC")
    size = 120
    while size > 70 and d.textlength(title, font=BOLD(size)) > W - 80:
        size -= 6
    y = centered(d, 150, title, BOLD(size), TEAL) + 30
    y = centered(d, y, sub, BOLD(76), TERRA) + 40
    slide.paste(fit_white(trimmed(pic), W - 40, H - y - 250), (20, y + 10))   # as big as it fits (owner: "double")
    centered(d, H - 210, f"swipe for all {n} {'phrases' if 'PHRASE' in title.upper() else 'words'}", REG, INK)
    centered(d, H - 120, "save it for later", BOLD(52), TERRA)
    return slide


def closing():
    slide = Image.new("RGB", (W, H), TEAL)
    d = ImageDraw.Draw(slide)
    logo = ROOT / "assets" / "logo-3d-narrator-1024.png"   # the 3D-film owner (2026-11-04; was logo-clay-teacher)
    if logo.exists():
        D = 600                                   # owner 2026-11-04: bigger circle (was 420)
        lg = Image.open(logo).convert("RGB").resize((D, D), Image.LANCZOS)
        m = Image.new("L", lg.size, 0); ImageDraw.Draw(m).ellipse((0, 0, D - 1, D - 1), fill=255)
        slide.paste(lg, ((W - D) // 2, 80), m)
    y = centered(d, 750, "A new Arabic lesson", BOLD(72), (255, 255, 255)) + 30
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
        if len(parts) >= 4 and re.fullmatch(r"([A-Z][a-z]+ )?\d+/\d+", parts[-1]) or i in EXTRA:
            words.append((i, minimal(parts[0]), parts[1], parts[2]))   # harakat only where needed (owner 2026-11-03)
    if not words and not opt.get("cards"):   # with cards= the script needs no N/M cards (v01 café, 2026-11-12)
        sys.exit("no 'N/M' word cards in this script")
    if pick:
        words = [words[k - 1] for k in pick]
    if opt.get("cards"):   # cards=file.json: [[arabic, translit, english], …] — the carousel's own list (owner 2026-11-09:
        # simplest transliteration for beginners, "ashrab" not "ashrabu"; extra words like good/bad); pictures p01…pNN
        import json as _j
        words = [(0, minimal(a), t, e) for a, t, e in _j.loads(pathlib.Path(opt["cards"]).read_text(encoding="utf-8"))]
        pick = list(range(1, len(words) + 1))
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
    total = len([1 for x in screens if x and re.search(r"(Word |Phrase |Question )?\d+/\d+$", x.strip())])
    more = f" (all {total} words)" if pick and total > len(words) else ""
    cap = (f"{re.sub(r"\b(Of|The|And|In|To|A|Or)\b", lambda m: m[0].lower(), title.title())} {sub} 👇 Save this and swipe through it once a day this week.\n\n"
           + "\n".join(f"{a} — {t} — {e}" for _, a, t, e in words)
           + f"\n\nFull lesson{more}: \"{lesson}\" on YouTube, link in bio ▶️\nWhich one will you use first? Tell me in the comments 👇\n\n"
           + "#learnarabic #arabicvocabulary #arabicforbeginners #2minutearabic\n")
    (out / "caption.txt").write_text(cap, encoding="utf-8")
    print(f"{len(slides)} slides → {out}")


if __name__ == "__main__":
    main()
