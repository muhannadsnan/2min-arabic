#!/usr/bin/env python3
"""The monthly STORY video, 16:9 (owner 2026-11-03 — .claude/skills/story-episode/SKILL.md, docs/22).

    $TTS tools/story_episode.py videos/s01-story.json output/s01-story/s01-story.mp4 [--from 0 --to 60] [--preview]

The spec lists the segments in video order (`kind`):
  camera  the owner's filmed intro/outro (spec "camera"[file]); English subtitles per line; an optional "pic" is
          shown full screen during the first line (the hook: the ending first)
  talk    the clay owner, half body, full screen; Arabic + English caption at the bottom
  story   the picture in the centre on paper; the key "words" pop up as they are said, as ONE bullet list on the
          right (no borders, close together, a colour per word — owner 2026-11-03), and light up in the same colour in
          the sentence under the picture; English under it (the clay owner in a small square only with --square:
          owner 2026-11-03 "disturbing to the learner", off for now). "verbs" (past/future): the item is
          "present ← new form" instead, the new verb lights up.
          "replay": true = the same line again (section 2: the sentence before its questions)
  qa      the picture; the question, a short thinking pause (dots), then the answer in green
  pair    a word and its opposite as two big cards on the left, the clay owner on the right, the example as caption
  star    the next of the 5 stars turns gold with a chime (on the previous view)
Audio = the owner's lines (clips/NN-*.wav, cut by split_recording.py) — no AI voice. A line without a recording is a
silent placeholder of estimated length (the mouth still moves), so the layout can be checked before the recording.
"""
import argparse
import json
import math
import pathlib
import random
import re
import shutil
import signal
import subprocess
import sys
import tempfile

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools")); sys.path.insert(0, str(ROOT / "tools" / "animate"))
from arabic_text import minimal  # noqa: E402
import narrator as nar  # noqa: E402

W, H, FPS, SR = 1920, 1080, 30, 48000
PAPER = (250, 247, 240)
INK = (45, 40, 38)
GREY = (110, 104, 98)
LIT = (214, 104, 28)          # a word that has popped, lit in the sentence
GREEN = (46, 140, 70)         # answers
CRAYON = [(86, 160, 214), (110, 176, 84), (232, 146, 52), (222, 104, 140)]   # card borders, one per spot
FONTS = pathlib.Path("/usr/share/fonts/truetype/noto")
AR = lambda s: ImageFont.truetype(str(FONTS / "NotoNaskhArabic-Bold.ttf"), s)
EN = lambda s: ImageFont.truetype(str(FONTS / "NotoSans-Regular.ttf"), s)
ENB = lambda s: ImageFont.truetype(str(FONTS / "NotoSans-Bold.ttf"), s)
ENI = lambda s: ImageFont.truetype(str(FONTS / "NotoSans-Italic.ttf"), s)
SYM = lambda s: ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", s)   # ↓ ↕ (not in Noto)
PUNCT = "؟?!.،,:؛…\"'«»()"

PIC = (500, 96, 1420, 726)                 # the story picture's box (fit inside, centred)
STAR = (84, 81)                            # the 5 stars, top left, beside the picture (owner 2026-11-04: bigger, was 58×56)
LIST_R = 1880                                # the word list: right edge (Arabic reads from the right)
LIST_CY = (PIC[1] + PIC[3]) // 2            # …centred on the picture's middle
WORD_COLS = [(38, 110, 196), (214, 104, 28), (46, 140, 70), (186, 52, 128), (118, 72, 186), (16, 138, 140)]


LIST_MAX = 5                                 # the list holds 5 words; the 6th clears it and starts again (owner 2026-11-03)
LIST_YS = [LIST_CY + (j - (LIST_MAX - 1) / 2) * 128 for j in range(LIST_MAX)]   # fixed rows: nothing moves when one is added
LIST_L = 470                                 # the LEFT list (opposites: fast – slow, before – after …): its bullets, by the picture
HANG, FADE = 2.0, 0.3                        # a full list stays ≥ 2 s before the 6th clears it, fading out (owner 2026-11-03)


class RunningList:
    """a list that runs across sentences: up to LIST_MAX items, the next one clears it (after HANG s); an item already
    in it doesn't pop again."""
    def __init__(self):
        self.entries, self.alive, self.last = [], [], -1e9

    def clear(self, at):
        for e in self.alive: e["until"] = at
        self.alive.clear()

    def add(self, key, t, **kw):
        """→ (entry, is_new); a new item may come later than t (the hang)."""
        e = next((e for e in self.alive if e["key"] == key), None)
        if e: return e, False
        if len(self.alive) == LIST_MAX:
            t = max(t, self.last + HANG); self.clear(t)
        e = dict(kw, key=key, row=len(self.alive), t=t, until=1e9, col=WORD_COLS[len(self.alive) % len(WORD_COLS)])
        self.alive.append(e); self.entries.append(e); self.last = t
        return e, True


SQ = (1590, 752, 1890, 1052)               # the narrator square
TEXT_CX, TEXT_W = 960, 1400                # sentence block under the picture (1000, 1120 with --square: clear of it)


# ---------- audio ----------
def read_audio(path):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", str(path), "-vn", "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"],
                         capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.float32).copy()


def voiced(x, thr_db=-38, min_gap=0.12):
    hop = SR // 100
    n = len(x) // hop
    if not n:
        return []
    db = 20 * np.log10(np.sqrt(np.mean(x[:n * hop].reshape(n, hop) ** 2, axis=1)) + 1e-6)
    on = db > thr_db
    parts, start, gap = [], None, 0
    for i, v in enumerate(on):
        if v:
            if start is None: start = i
            gap = 0
        elif start is not None:
            gap += 1
            if gap * hop / SR >= min_gap:
                parts.append([start * hop / SR, (i - gap + 1) * hop / SR]); start, gap = None, 0
    if start is not None: parts.append([start * hop / SR, n * hop / SR])
    return [p for p in parts if p[1] - p[0] > 0.08]


def est(text):
    """placeholder length of a slow, simple Arabic line"""
    return 0.6 + 0.085 * len(re.sub(r"\s+", "", text))


def fake_voice(dur, seed):
    """silent-placeholder stand-in for the mouth only (never mixed into the sound): syllable-like bursts"""
    rnd = np.random.default_rng(seed)
    t = np.arange(int(dur * SR)) / SR
    am = 0.35 + 0.65 * np.abs(np.sin(2 * np.pi * (3.2 + rnd.random()) * t))
    return (rnd.standard_normal(len(t)) * 0.08 * am).astype(np.float32)


# ---------- text ----------
def text_w(font, s, rtl=False):
    b = font.getbbox(s, direction="rtl") if rtl else font.getbbox(s)
    return b[2] - b[0]


def ar_lines(tokens, font, maxw):
    lines, cur = [], []
    for tok in tokens:
        if cur and text_w(font, " ".join(cur + [tok]), True) > maxw:
            lines.append(cur); cur = []
        cur.append(tok)
    return lines + [cur] if cur else lines


def draw_ar_tokens(d, tokens, colors, font, cx, y, maxw):
    """Arabic word by word, right to left, so single words can be coloured. Returns the bottom y."""
    sp = text_w(font, " ") or 18
    lh = int(font.size * 1.45)
    k = 0
    for line in ar_lines(tokens, font, maxw):
        ws = [text_w(font, t, True) for t in line]
        x = cx + (sum(ws) + sp * (len(line) - 1)) / 2
        for t, w in zip(line, ws):
            d.text((x - w, y), t, font=font, fill=colors[k], direction="rtl", anchor="la"); x -= w + sp; k += 1
        y += lh
    return y


def wrap_en(s, font, maxw):
    out, cur = [], ""
    for w in s.split():
        if cur and text_w(font, cur + " " + w) > maxw:
            out.append(cur); cur = w
        else:
            cur = (cur + " " + w).strip()
    return out + [cur] if cur else out


def draw_en(d, s, font, cx, y, maxw, fill=GREY):
    for line in wrap_en(s, font, maxw):
        d.text((cx, y), line, font=font, fill=fill, anchor="ma"); y += int(font.size * 1.3)
    return y


def ar_text(s):
    return minimal(s).replace("…", "...")


def core(tok):
    return tok.strip(PUNCT)


def find_token(tokens, word):
    """index of the first token that is the word (or the word with و/ف/ب in front)"""
    for i, t in enumerate(tokens):
        c = core(t)
        if c == word or (len(c) == len(word) + 1 and c.endswith(word) and c[0] in "وفب"):
            return i
    for i, t in enumerate(tokens):
        if word in core(t):
            return i
    return None


def card(lines, border, pad=26):
    """a white rounded card: lines = [(text, font, color, rtl)] centred; soft shadow; RGBA"""
    sizes = [(text_w(f, s, r), int(f.size * 1.35)) for s, f, c, r in lines]
    w = max(s[0] for s in sizes) + 2 * pad + 10
    h = sum(s[1] for s in sizes) + 2 * pad - 6
    im = Image.new("RGBA", (w + 24, h + 24), (0, 0, 0, 0))
    sh = Image.new("L", im.size, 0); ImageDraw.Draw(sh).rounded_rectangle((14, 16, w + 12, h + 14), 26, fill=70)
    im.putalpha(sh.filter(ImageFilter.GaussianBlur(7)))
    im = Image.composite(Image.new("RGBA", im.size, (60, 50, 40, 255)), Image.new("RGBA", im.size, (0, 0, 0, 0)), im.getchannel("A"))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((10, 10, w + 10, h + 10), 24, fill=(255, 255, 255, 255), outline=border + (255,), width=6)
    y = 10 + pad - 8
    for (s, f, c, r), (tw, lh) in zip(lines, sizes):
        d.text((10 + w / 2, y), s, font=f, fill=c, anchor="ma", direction="rtl" if r else None); y += lh
    return im


def pop_scale(age):
    """0 → 1.1 → 1 over 0.3 s"""
    if age >= 0.3: return 1.0
    a = age / 0.3
    return 0.5 + 0.6 * a / 0.75 if a < 0.75 else 1.1 - 0.1 * (a - 0.75) / 0.25


LIST_EN = 32   # the list's English size (vertical Shorts: 38, owner 2026-11-11 "a bit enlarged … in black")


def list_item(row, en, col, en_at=0, en_col=GREY):
    """one bullet of the word list, RGBA: ● + row (right to left: [(text, font, color, rtl)]) + the English under the
    row's piece en_at (verbs: under the coloured new form, in its colour — grey means the present; owner 2026-11-03).
    en may be {piece: text}: each English word centred under its own Arabic word (opposites: "here" under هنا)."""
    gap, dot = 14, 20
    ws = [text_w(f, t, r) for t, f, c, r in row]
    boxes = [f.getbbox(t, anchor="rs", direction="rtl" if r else None) for t, f, c, r in row]
    top, bot = min(bx[1] for bx in boxes), max(bx[3] for bx in boxes)     # ink above / below the baseline
    ef = ENI(LIST_EN); eh = int(ef.size * 1.35)
    rights = [sum(ws[:i]) + gap * i for i in range(len(row))]            # each piece's right edge, from the text's right
    if isinstance(en, dict):   # English centred under each piece
        ens = [(t, max(rights[i] + ws[i] / 2, text_w(ef, t) / 2), "ma") for i, t in en.items()]   # never past the bullet side
        need = max(r + text_w(ef, t) / 2 for t, r, _ in ens)
    else:                      # one English line, right-aligned under piece en_at
        ens = [(en, rights[en_at], "ra")]
        need = rights[en_at] + text_w(ef, en)
    tw = int(max(sum(ws) + gap * (len(ws) - 1), need))
    base = -top + 4; ey = base + bot + 2                                   # English under the lowest Arabic ink
    w, h = tw + dot + 18, ey + eh
    im = Image.new("RGBA", (w + 4, h + 4), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    by = int(base - 0.3 * max(f.size for t, f, c, r in row))
    d.ellipse((w - dot, by - dot // 2, w, by + dot // 2), fill=col + (255,))
    x0 = w - dot - 18
    for (t, f, c, r), rr in zip(row, rights):
        d.text((x0 - rr, base), t, font=f, fill=c + (255,), anchor="rs", direction="rtl" if r else None)
    for t, rr, anchor in ens:
        d.text((x0 - rr, ey), t, font=ef, fill=en_col + (255,), anchor=anchor)
    return im


def paste_item(frame, im, right, cy, age, left=None, fade=1.0):
    """pop a list item in, anchored at its right edge (or its left edge); fade < 1 = fading out."""
    if left is not None: right = left + im.width
    s = pop_scale(age)
    if s <= 0.05: return
    if abs(s - 1) > 0.01:
        im = im.resize((max(1, int(im.width * s)), max(1, int(im.height * s))), Image.BICUBIC)
    k = min(1.0, age / 0.15) * fade
    if k < 1:
        a = im.getchannel("A").point(lambda v: int(v * k)); im = im.copy(); im.putalpha(a)
    frame.paste(im, (int(right - im.width), int(cy - im.height / 2)), im)


def paste_card(frame, im, cx, cy, age):
    s = pop_scale(age)
    if s <= 0.05: return
    if abs(s - 1) > 0.01:
        im = im.resize((max(1, int(im.width * s)), max(1, int(im.height * s))), Image.BICUBIC)
    if age < 0.15:
        a = im.getchannel("A").point(lambda v: int(v * age / 0.15)); im = im.copy(); im.putalpha(a)
    frame.paste(im, (int(cx - im.width / 2), int(cy - im.height / 2)), im)


# ---------- the timeline ----------
def build(spec, preview):
    clips = ROOT / spec["clips"]
    first = {s["line"]: s for s in spec["segments"] if s.get("line") and not s.get("replay")}
    segs, voice, mouthv, t = [], [], [], 0.0

    def add_audio(x, at, fake=None):
        voice.append((at, x)); mouthv.append((at, x if fake is None else fake))

    def clip(line):
        f = sorted(clips.glob(f"{line:02d}-*.wav")) if clips.exists() else []
        return None if preview or not f else read_audio(f[-1])

    for i, s in enumerate(spec["segments"]):
        s = dict(first.get(s.get("line"), {}), **s) if s.get("replay") else dict(s)
        k = s["kind"]
        if k == "star":
            if s.get("gap") == 0:   # owner 2026-11-05: no pause — the chime rings in the tail and he keeps talking
                segs[-1].setdefault("stars", []).append(segs[-1]["end"] - 0.45)
            else:
                segs[-1]["end"] += 1.6; segs[-1].setdefault("stars", []).append(segs[-1]["end"] - 1.45); t += 1.6
            continue
        s["start"] = t
        if k == "card":   # a still at the very end (owner 2026-11-05: the accounts, 5–10 s; room for YouTube's end screen)
            s["end"] = t + s.get("dur", 10); segs.append(s); t = s["end"]
            continue
        if k == "camera":
            f = ROOT / spec["camera"][s["file"]]
            if f.exists() and not preview:
                x = read_audio(f); dur = len(x) / SR
                if s.get("subs"):   # given by hand (seconds in the clip): the 1st one's end = where the hook picture ends
                    bounds = [tuple(b) for b in s["subs"]]
                else:
                    vp = voiced(x, min_gap=0.35)
                    gaps = sorted(range(len(vp) - 1), key=lambda j: vp[j][1] - vp[j + 1][0])[:len(s["lines"]) - 1]   # biggest silences (end → next start)
                    bounds, a = [], 0
                    for c in sorted(gaps) + [len(vp) - 1]:
                        bounds.append((vp[a][0], vp[c][1])); a = c + 1
                s["subs"] = [(t + b0, t + b1) for b0, b1 in bounds]
                voice.append((t, x)); s["video"] = str(f)
            else:
                dur, st = 0.4, []
                for ln, e in zip(s["lines"], s["en"]):
                    d_ = 1.0 + 0.06 * len(e); st.append((t + dur, t + dur + d_)); dur += d_ + 0.5
                s["subs"] = st; dur += 0.4
            s["end"] = t + dur
        else:
            lead = 0.35
            x = clip(s["line"])
            if k == "qa":
                q, a = [p.strip() for p in s["ar"].split("…", 1)]
                qe, ae = [p.strip() for p in s["en"].split("…", 1)]
                s.update(q=q, a=a, qe=qe, ae=ae)
                if x is not None:
                    vp = voiced(x, min_gap=0.5)
                    j = max(range(len(vp) - 1), key=lambda j: vp[j + 1][0] - vp[j][1]) if len(vp) > 1 else 0
                    s["q_span"] = (t + lead + vp[0][0], t + lead + vp[j][1])
                    s["a_span"] = (t + lead + vp[min(j + 1, len(vp) - 1)][0], t + lead + vp[-1][1])
                    add_audio(x, t + lead); dur = lead + len(x) / SR + 0.8
                else:
                    dq, da = est(q), est(a)
                    s["q_span"] = (t + lead, t + lead + dq); s["a_span"] = (t + lead + dq + 2.2, t + lead + dq + 2.2 + da)
                    add_audio(np.zeros(int((dq + 2.2 + da) * SR), np.float32), t + lead,
                              np.concatenate([fake_voice(dq, i), np.zeros(int(2.2 * SR), np.float32), fake_voice(da, i + 999)]))
                    dur = lead + dq + 2.2 + da + 0.8
            else:
                if x is not None:
                    vp = voiced(x) or [[0, len(x) / SR]]
                    s["span"] = (t + lead + vp[0][0], t + lead + vp[-1][1]); add_audio(x, t + lead); n = len(x) / SR
                else:
                    n = est(s["ar"]); s["span"] = (t + lead, t + lead + n)
                    add_audio(np.zeros(int(n * SR), np.float32), t + lead, fake_voice(n, i))
                tail = {"story": 0.9, "talk": 0.6, "pair": 0.8}[k]
                if k == "pair" and (not segs or segs[-1].get("pair") != s["pair"]):
                    s["new_pair"] = True
                dur = lead + n + tail
            s["end"] = t + dur
        segs.append(s); t = s["end"]
    return segs, voice, mouthv, t


def mix(parts, total):
    out = np.zeros(int(total * SR) + SR, np.float32)
    for at, x in parts:
        a = int(at * SR); out[a:a + len(x)] += x[:len(out) - a]
    return out


# ---------- drawing ----------
class Painter:
    def __init__(self, spec):
        self.pics = {}
        self.pdir = ROOT / spec["pictures"]
        self.stars = (Image.open(ROOT / "assets/stars/grey.png").convert("RGBA").resize(STAR, Image.LANCZOS),
                      Image.open(ROOT / "assets/stars/gold.png").convert("RGBA").resize(STAR, Image.LANCZOS))
        self.cards, self.bases = {}, {}

    def picture(self, n):
        if n not in self.pics:
            p = Image.open(self.pdir / f"scene-{n:02d}.png").convert("RGB")
            bw, bh = PIC[2] - PIC[0], PIC[3] - PIC[1]
            s = min(bw / p.width, bh / p.height); p = p.resize((int(p.width * s), int(p.height * s)), Image.LANCZOS)
            self.pics[n] = p
        return self.pics[n]

    def page(self, n):
        if n in self.bases:
            return self.bases[n].copy()
        im = Image.new("RGB", (W, H), PAPER)
        p = self.picture(n)
        x0 = (PIC[0] + PIC[2] - p.width) // 2; y0 = PIC[1] + (PIC[3] - PIC[1] - p.height) // 2
        sh = Image.new("L", (W, H), 0); ImageDraw.Draw(sh).rectangle((x0 + 6, y0 + 10, x0 + p.width + 6, y0 + p.height + 10), fill=60)
        im = Image.composite(Image.new("RGB", (W, H), (120, 105, 90)), im, sh.filter(ImageFilter.GaussianBlur(10)))
        im.paste(p, (x0, y0))
        self.bases[n] = im
        return im.copy()

    def stars_on(self, frame, t, star_times):
        for k in range(5):
            x, y = 30 + k * (STAR[0] + 8), 8
            done = k < len(star_times) and t >= star_times[k]
            im = self.stars[1 if done else 0]
            if done and t - star_times[k] < 0.45:
                s = 1 + 0.5 * math.sin(math.pi * (t - star_times[k]) / 0.45)
                im = im.resize((int(STAR[0] * s), int(STAR[1] * s)), Image.BICUBIC)
            frame.paste(im, (int(x + STAR[0] / 2 - im.width / 2), int(y + STAR[1] / 2 - im.height / 2)), im)

    def word_item(self, ar, en, col):
        key = ("w", ar, en, col)
        if key not in self.cards:
            self.cards[key] = list_item([(minimal(ar), AR(64), col, True)], en, col)
        return self.cards[key]

    def opp_item(self, a, b, col):
        key = ("o", tuple(a), tuple(b), col)
        if key not in self.cards:
            self.cards[key] = list_item([(minimal(a[0]), AR(56), col, True), ("↔", SYM(40), GREY, False),
                                         (minimal(b[0]), AR(56), col, True)], {0: a[1], 2: b[1]}, col)
        return self.cards[key]

    def verb_item(self, old, new, en, col):
        key = ("v", old, new, en, col)
        if key not in self.cards:
            # past/future: the present (small, grey) ← the new form (in the word's colour)
            self.cards[key] = list_item([(minimal(old), AR(42), GREY, True), ("←", SYM(30), GREY, False),
                                         (minimal(new), AR(64), col, True)], en, col, en_at=2, en_col=col)
        return self.cards[key]

    def pair_card(self, ar, en, col):
        key = ("p", ar, en)
        if key not in self.cards:
            self.cards[key] = card([(minimal(ar), AR(130), INK, True), (en, ENI(50), GREY, False)], col, pad=34)
        return self.cards[key]


def caption_box(frame, ar, en, x0=60, x1=None, top=None, fs=54):
    """Arabic + English at the bottom (talk / pair), or from `top` down (vertical Shorts); returns the box's bottom y"""
    W, H = frame.size
    x1 = x1 or W - 60
    f, fe = AR(fs), ENI(int(fs * 0.63))
    toks = ar_text(ar).split()
    lines = ar_lines(toks, f, x1 - x0 - 80)
    en_l = wrap_en(en, fe, x1 - x0 - 80)
    h = len(lines) * int(f.size * 1.45) + len(en_l) * int(fe.size * 1.3) + 40
    y0 = H - 40 - h if top is None else top
    box = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(box).rounded_rectangle((x0, y0, x1, y0 + h), 28, fill=(255, 255, 255, 236))
    frame.paste(box, (0, 0), box)
    d = ImageDraw.Draw(frame)
    y = draw_ar_tokens(d, toks, [INK] * len(toks), f, (x0 + x1) / 2, y0 + 14, x1 - x0 - 80)
    draw_en(d, en, fe, (x0 + x1) / 2, y - 6, x1 - x0 - 80)
    return y0 + h


CHAPTERS = ["The story", "Questions about the story", "Opposites: fast and slow, before and after", "The story in the past",
            "The story in the future"]   # one per star (the 5 sections); the camera intro/outro + the end card frame them


# ---- vertical Shorts from the story (owner 2026-11-10/11) ----
VW, VH = 1080, 1920
V_BOTTOM = 1610        # text stays above this (the Shorts title/channel overlay covers the bottom)


def write_vcaptions(segs, ranges, out):
    """captions-upload.srt for a vertical Short: the same English cues, mapped onto the kept (cut) timeline"""
    cues = []
    for s in segs:
        k = s["kind"]
        if k == "camera": cues += [(a_, b_, e) for (a_, b_), e in zip(s["subs"][:1], s["en"][:1])]
        elif k == "qa": cues += [(*s["q_span"], s["qe"]), (*s["a_span"], s["ae"])]
        elif k in ("story", "talk", "pair"): cues.append((*s["span"], (s.get("en_v") or s["en"]).replace("\n", " ")))
    def loc(t):
        off = 0
        for r0, r1 in ranges:
            if t < r0: return off
            if t <= r1: return off + t - r0
            off += r1 - r0
        return off
    first = ranges[0][0]
    out_ = []
    for a_, b_, e in cues:
        if b_ < first - 0.05 or not any(r0 - 0.05 <= a_ < r1 or r0 < b_ <= r1 + 0.05 for r0, r1 in ranges): continue
        if a_ < first - 0.3 and e[:12].count("!") and e.split("!", 1)[1].strip(): e = e.split("!", 1)[1].strip()   # cut first word
        x, y = loc(a_), loc(b_)
        if y - x > 0.2: out_.append((x, y, e))
    ts = lambda x: "%02d:%02d:%02d,%03d" % (x // 3600, x % 3600 // 60, x % 60, round(x % 1 * 1000) % 1000)
    (out.parent / "captions-upload.srt").write_text("\n".join(f"{i}\n{ts(a_)} --> {ts(b_)}\n{e}\n" for i, (a_, b_, e) in enumerate(out_, 1)), encoding="utf-8")


def squeeze_pauses(track, ranges, thr=0.012, min_gap=0.3):
    """split the kept ranges inside every silence ≥ 0.3 s of the voice so it plays half as long (0.25–1.0 s)"""
    out, w = [], int(0.02 * SR)
    for r0, r1 in ranges:
        x = track[int(r0 * SR):int(r1 * SR)]
        n = len(x) // w
        if n == 0: out.append((r0, r1)); continue
        loud = np.sqrt((x[:n * w].reshape(n, w) ** 2).mean(axis=1)) > thr
        runs, i = [], 0
        while i < n:
            if not loud[i]:
                j = i
                while j < n and not loud[j]: j += 1
                if (j - i) * 0.02 >= min_gap and i > 0 and j < n: runs.append((r0 + i * 0.02, r0 + j * 0.02))
                i = j
            else: i += 1
        a_ = r0
        for s0, s1 in runs:
            keep = min(max(0.5 * (s1 - s0), 0.25), 1.0)
            out.append((a_, s0 + keep / 2)); a_ = s1 - keep / 2
        out.append((a_, r1))
    snap = lambda v: round(v * FPS) / FPS          # cut on whole video frames: sound and picture stay in sync
    return [(snap(a_), snap(b_)) for a_, b_ in out if snap(b_) - snap(a_) >= 1 / FPS]


def vertical_keep(segs, ranges):
    """the parts worth keeping (owner 2026-11-11: "cut the silence between sentences"): each line's voice ±0.3 s; a
    question keeps its thinking pause (q → a); the camera hook keeps its first line only"""
    out = []
    for x in segs:
        if x["kind"] == "qa": a_, b_ = x["q_span"][0] - 0.25, x["a_span"][1] + 0.35
        elif x["kind"] == "camera": a_, b_ = x["start"] + x["subs"][0][0] - 0.3, x["start"] + x["subs"][0][1] + 0.3
        elif x.get("span"): a_, b_ = x["span"][0] - 0.25, x["span"][1] + 0.35
        else: continue
        for r0, r1 in ranges:
            lo, hi = max(a_, r0), min(b_, r1)
            if hi - lo > 0.2: out.append([lo, hi])
    out.sort(); m = []
    for lo, hi in out:
        if m and lo <= m[-1][1] + 0.05: m[-1][1] = max(m[-1][1], hi)
        else: m.append([lo, hi])
    return [tuple(x) for x in m]


PUNCT_END = (".", "،", ",", ":", "؛", ";", "!", "؟", "?", "…")


def smart_lines(words, wfun, sp, maxw):
    """owner 2026-11-11: a sentence that needs two lines breaks where it reads well — after . ، : … if there is one
    (the most even such break), else at the most even point — never leaving one word alone; one line if it fits"""
    W_ = lambda ws: sum(wfun(w) for w in ws) + sp * max(0, len(ws) - 1)
    if W_(words) <= maxw or len(words) < 2: return [words]
    cands = [i for i in range(1, len(words)) if W_(words[:i]) <= maxw and W_(words[i:]) <= maxw]
    if not cands: return None
    punct = [i for i in cands if words[i - 1].endswith(PUNCT_END)]
    best = min(punct or cands, key=lambda i: abs(W_(words[:i]) - W_(words[i:])))
    return [words[:best], words[best:]]


def draw_ar_smart(d, tokens, colors, font, cx, y, maxw):
    sp = text_w(font, " ") or 18; lh = int(font.size * 1.45)
    lines = smart_lines(tokens, lambda t: text_w(font, t, True), sp, maxw)
    if lines is None: return draw_ar_tokens(d, tokens, colors, font, cx, y, maxw)
    k = 0
    for line in lines:
        ws = [text_w(font, t, True) for t in line]
        x = cx + (sum(ws) + sp * (len(line) - 1)) / 2
        for t, w in zip(line, ws):
            d.text((x - w, y), t, font=font, fill=colors[k], direction="rtl", anchor="la"); x -= w + sp; k += 1
        y += lh
    return y


def draw_en_smart(d, s_, font, cx, y, maxw, fill=GREY):
    words = s_.split(); lines = smart_lines(words, lambda w: text_w(font, w), text_w(font, " ") or 10, maxw)
    if lines is None: return draw_en(d, s_, font, cx, y, maxw, fill)
    for line in lines:
        d.text((cx, y), " ".join(line), font=font, fill=fill, anchor="ma"); y += int(font.size * 1.3)
    return y


def v_text(d, ar, en, y, far, fen, col_ar=INK, col_en=GREY):
    """Arabic (explicit \\n = new line, each wrapped) + English under it, centred, no card"""
    for part in ar.split("\n"):
        t = ar_text(part).split()
        y = draw_ar_smart(d, t, [col_ar] * len(t), far, VW / 2, y, 1040)
    for part in en.split("\n"):
        y = draw_en_smart(d, part, fen, VW / 2, y - 4, 1040, fill=col_en)
    return y


def vertical_painter(a, spec, segs, ranges, P, R, L, big, nar, star_t):
    """frame(t, tl, s, k, key, body) for a 9:16 Short (owner 2026-11-11, 2nd round):
    3 stars close together at the very top · the words as LISTS in columns, opposites on the right, the other words /
    verbs on the left, popping in and staying · the picture full width (no paper margin) in the lower half with the
    sentence under it · talk/pair: plain text (no card) and the presenter under it · --heading until the first word."""
    global LIST_EN
    LIST_EN = 38
    in_rng = lambda t: any(r0 - 0.4 <= t < r1 + 0.4 for r0, r1 in ranges)
    left, right, seen = [], [], set()
    for e in sorted(R.entries + L.entries, key=lambda e: e["t"]):
        if not in_rng(e["t"]): continue
        kind = e.get("typ", "o"); kk = (kind, repr(e["it"]))
        if kk in seen: continue
        seen.add(kk)
        if kind == "o": right.append({"t": e["t"], "im": P.opp_item(*e["it"], e["col"])})
        else: left.append({"t": e["t"], "im": P.verb_item(*e["it"], e["col"]) if kind == "v" else P.word_item(*e["it"], e["col"])})
    for x in segs:
        if x["kind"] == "pair" and x.get("new_pair") and in_rng(x["span"][0] + 0.1):
            kk = ("p", repr(x["pair"]))
            if kk in seen: continue
            seen.add(kk)
            right.append({"t": x["pops"][1]["t"] + 0.6, "im": P.opp_item(x["pair"][0], x["pair"][1], WORD_COLS[len(right) % len(WORD_COLS)])})
    items = left + right
    SW = 160; stars = [Image.open(ROOT / f"assets/stars/{n}.png").convert("RGBA").resize((SW, int(SW * 135 / 140)), Image.LANCZOS) for n in ("grey", "gold")]
    STAR_Y = 46; WY0 = STAR_Y + stars[0].height + 16
    # columns: the biggest scale (then the fewest rows) whose columns fit the width and ≤ 470 px of height
    def cols(group, rows):
        return [group[i:i + rows] for i in range(0, len(group), rows)]
    def width(group, rows, sc):
        cs = cols(group, rows)
        return sum(max(it["im"].width for it in c) * sc for c in cs) + 26 * sc * max(0, len(cs) - 1)
    best = None
    if items:
        mh = max(it["im"].height for it in items)
        for sc in (1.1, 1.0, 0.92, 0.85, 0.78, 0.72, 0.66, 0.6, 0.55, 0.5, 0.45):
            rh = mh * sc + 4
            for rows in range(max(1, min(int(560 // rh), max(len(left), len(right)))), 0, -1):   # a list: as many rows as fit, no empty ones
                tw = width(left, rows, sc) + width(right, rows, sc) + (50 if left and right else 0)
                if tw <= VW - 40: best = (sc, rows, rh); break
            if best: break
        best = best or (0.45, max(len(left), len(right)), mh * 0.45 + 4)
        sc, rows, rh = best
        def place(group, x_right):
            x = x_right
            for c in cols(group, rows):
                cw = max(it["im"].width for it in c) * sc
                for i, it in enumerate(c):
                    it["sim"] = it["im"].resize((max(1, int(it["im"].width * sc)), max(1, int(it["im"].height * sc))), Image.LANCZOS) if sc != 1 else it["im"]
                    it.update(right=x, cy=WY0 + i * rh + rh / 2)
                x -= cw + 26 * sc
        # the whole block centred (owner 2026-11-11: few words shouldn't hug the edge): opposites on its right side,
        # the other words on its left side; inside a column the Arabic is right-aligned
        wr, wl = width(right, rows, sc), width(left, rows, sc)
        tw = wr + wl + (50 if left and right else 0)
        xr = VW / 2 + tw / 2
        place(right, xr)
        place(left, xr - wr - (50 if right else 0))
        words_end = WY0 + rows * rh
    else:
        words_end = WY0
    head = a.heading.split("|") if a.heading else []
    if head: words_end = max(words_end, WY0 + 70 + 124 + (62 if len(head) > 1 else 0) + (80 if len(head) > 2 else 0))
    FS, FE, FQ, FQE = AR(80), ENI(45), AR(74), ENI(42)
    def text_h(x):
        if x["kind"] == "story":
            return len(ar_lines(ar_text(x["ar"]).split(), FS, 1040)) * int(FS.size * 1.45) + len(wrap_en(x["en"], FE, 1040)) * int(FE.size * 1.3)
        if x["kind"] == "qa":
            return (len(ar_lines(ar_text(x["q"]).split(), FQ, 1040)) + len(ar_lines(ar_text(x["a"]).split(), FQ, 1040))) * int(FQ.size * 1.45) \
                + (len(wrap_en(x["qe"], FQE, 1040)) + len(wrap_en(x["ae"], FQE, 1040))) * int(FQE.size * 1.3) + 50
        return int(FS.size * 1.45) + 2 * int(FE.size * 1.3)
    t_of = lambda x: (x.get("q_span") or x.get("span") or (x["start"] + x["subs"][0][0], 0))[0] + 0.1
    vis = [x for x in segs if x["kind"] in ("story", "qa", "camera") and in_rng(t_of(x))]
    th = max([text_h(x) for x in vis] + [200])
    th_pic = {}
    for x in vis:
        if x.get("pic"): th_pic[x["pic"]] = max(th_pic.get(x["pic"], 0), text_h(x))
    def trimmed(n):
        p = P.picture(n)
        bb = p.convert("L").point(lambda v: 255 if v < 228 else 0).getbbox()
        return p.crop(bb) if bb else p
    pics = {}
    hmax = max([int(trimmed(x["pic"]).height * VW / trimmed(x["pic"]).width) for x in vis if x.get("pic")] + [600])
    PIC_Y = int(max(words_end + 24, VH - 40 - th - 24 - hmax))
    room = VH - 40 - th - 24 - PIC_Y          # the picture's height budget (full width when it fits)
    def pic(n):
        """full width always (owner 2026-11-11: no side margins); it moves up into free space instead of shrinking,
        and only shrinks if even that doesn't leave room for the text"""
        # owner 2026-11-11: the subtitles get a minimum room (≥ 400 px, more if this picture's own sentences need it)
        # and a small margin stays at the bottom of the video
        p = trimmed(n); h = int(p.height * VW / p.width)
        t_room = max(400, th_pic.get(n, 0)); limit = VH - 70 - t_room - 24
        top = int(max(words_end + 24, limit - h))
        if top + h > limit:
            h = limit - top
            full = int(p.height * VW / p.width)
            if h < full:   # keep the full width: trim up to 12 % of the picture's height (top/bottom) before shrinking
                cut = min(p.height - int(h * p.width / VW), int(0.12 * p.height))
                if cut > 0: p = p.crop((0, cut // 2, p.width, p.height - (cut - cut // 2)))
        k_ = min(VW / p.width, h / p.height)
        return p.resize((int(p.width * k_), int(p.height * k_)), Image.LANCZOS), top

    def frame(t, tl, s, k, key, body):
        f = Image.new("RGB", (VW, VH), PAPER); d = ImageDraw.Draw(f)
        for j in range(3):
            done = tl >= star_t[j]; im = stars[1 if done else 0]
            if done and tl - star_t[j] < 0.45:
                z = 1 + 0.35 * math.sin(math.pi * (tl - star_t[j]) / 0.45); im = im.resize((int(im.width * z), int(im.height * z)), Image.BICUBIC)
            cx = VW / 2 + (j - 1) * 215
            f.paste(im, (int(cx - im.width / 2), int(STAR_Y + stars[0].height / 2 - im.height / 2)), im)
        shown = [it for it in items if it["t"] <= t]
        if head and not shown:
            hy = WY0 + 50
            d.text((VW / 2, hy), head[0], font=ENB(104), fill=LIT, anchor="ma"); hy += 124
            if len(head) > 1: d.text((VW / 2, hy), head[1], font=ENB(46), fill=INK, anchor="ma"); hy += 62
            if len(head) > 2: draw_ar_tokens(d, ar_text(head[2]).split(), [GREEN] * len(ar_text(head[2]).split()), AR(58), VW / 2, hy - 8, 1000)
        for it in shown:
            paste_item(f, it["sim"], it["right"], it["cy"], t - it["t"])
        if k in ("story", "qa", "camera"):
            n = s.get("pic")
            if n:
                if n not in pics: pics[n] = pic(n)
                im, top_ = pics[n]; f.paste(im, ((VW - im.width) // 2, top_)); y_ = top_ + im.height + 24
            else:
                y_ = PIC_Y
            if k == "story":
                toks = ar_text(s["ar"]).split(); cols_ = [INK] * len(toks)
                for p_ in s.get("lit_l", []) + s.get("lit", []):
                    if t >= p_["t"] and p_["tok"] is not None: cols_[p_["tok"]] = p_["e"]["col"]
                y_ = draw_ar_smart(d, toks, cols_, FS, VW / 2, y_, 1040)
                draw_en_smart(d, s["en"], FE, VW / 2, y_ - 4, 1040)
            elif k == "qa":
                q0, q1 = s["q_span"]; a0, a1 = s["a_span"]
                y_ = v_text(d, s["q"], s["qe"], y_, FQ, FQE)
                if q1 + 0.2 <= t < a0:
                    nd = min(3, int((t - q1 - 0.2) / max(0.3, (a0 - q1 - 0.2) / 3)) + 1)
                    for j in range(3):
                        cx = VW / 2 - 50 + j * 50
                        d.ellipse((cx - 12, y_ + 14, cx + 12, y_ + 38), fill=GREEN if j < nd else (215, 210, 200))
                if t >= a0:
                    v_text(d, s["a"], s["ae"], y_ + 2, FQ, FQE, GREEN, GREEN)
            else:   # the hook: Arabic + English like the story sentences (owner 2026-11-11)
                v_text(d, s.get("ar_subs", [""])[0], s["en"][0], y_, FS, FE)
            return f
        top = words_end + 24
        if k == "pair":   # the pair as one group centred on the screen, the arrow between (wide words stay inside)
            p0 = segs.index(s); first = next(x for x in reversed(segs[:p0 + 1]) if x.get("new_pair"))
            ims = [P.pair_card(*s["pair"][j], col) for j, col in ((0, CRAYON[0]), (1, CRAYON[2]))]
            g = 50; tw = ims[0].width + ims[1].width + 2 * g + 40
            if tw > VW - 40:
                z = (VW - 40) / tw; ims = [im.resize((int(im.width * z), int(im.height * z)), Image.LANCZOS) for im in ims]; tw = VW - 40
            x0 = (VW - tw) / 2; ch = max(im.height for im in ims); cy = top + ch / 2 + 10
            cxs = [x0 + tw - ims[0].width / 2, x0 + ims[1].width / 2]       # first word on the right (Arabic order)
            ax = x0 + ims[1].width + g + 20
            for j in range(2):
                pt = first["pops"][j]["t"]
                if t >= pt: paste_card(f, ims[j], int(cxs[j]), int(cy), t - pt)
            if t >= first["pops"][1]["t"]:
                d.text((ax, cy), "↔", font=SYM(64), fill=GREY, anchor="mm")
            top = cy + ch / 2 + 26
        ar_, en_ = s.get("ar_v") or s.get("ar", ""), s.get("en_v") or s.get("en", "")
        if s.get("span") and s["span"][0] < ranges[0][0] - 0.3 and s["start"] < ranges[0][0] <= s["end"]:
            ar_ = ar_.split("!", 1)[1].strip() if "!" in ar_[:12] else ar_
            en_ = en_.split("!", 1)[1].strip() if "!" in en_[:12] else en_
        bot = v_text(d, ar_, en_, top, AR(64), ENI(42)) if ar_ else top
        im = nar.transform(big[key], *body)
        hy = bot + 30; z = max(0.85, (VH + 30 - hy) / im.height)
        im = im.resize((int(im.width * z), int(im.height * z)), Image.LANCZOS)
        f.paste(im, ((VW - im.width) // 2, int(hy)), im)
        return f
    return frame


def write_captions(segs, total, out):
    """captions-upload.srt (the English lines as shown on screen; a question and its answer = two cues) + chapters.txt."""
    cues = []
    for s in segs:
        k = s["kind"]
        if k == "camera":
            cues += [(a, b, e) for (a, b), e in zip(s["subs"], s["en"])]
        elif k == "qa":
            cues += [(*s["q_span"], s["qe"]), (*s["a_span"], s["ae"])]
        elif k in ("story", "talk", "pair"):
            cues.append((*s["span"], s["en"]))
    ts = lambda x: "%02d:%02d:%02d,%03d" % (x // 3600, x % 3600 // 60, x % 60, round(x % 1 * 1000) % 1000)
    srt = out.parent / "captions-upload.srt"
    srt.write_text("\n".join(f"{i}\n{ts(a)} --> {ts(min(b, total))}\n{e}\n" for i, (a, b, e) in enumerate(cues, 1)), encoding="utf-8")
    # chapters: a section starts where the previous star's segment ends (the first after the intro)
    starts, names, k = [0.0], ["Intro: a turtle before a horse?"], 0
    for i, s in enumerate(segs):
        if s["kind"] == "camera" and i == 0:
            starts.append(s["end"]); names.append(CHAPTERS[0]); k = 1
        elif s.get("stars") and i + 1 < len(segs):
            nxt = segs[i + 1]
            if k < len(CHAPTERS): starts.append(nxt["start"]); names.append(CHAPTERS[k]); k += 1
            elif nxt["kind"] == "camera": starts.append(nxt["start"]); names.append("Your turn: tell the story")
    mmss = lambda x: f"{int(x // 60)}:{int(x % 60):02d}"
    (out.parent / "chapters.txt").write_text("\n".join(f"{mmss(t)} {n}" for t, n in zip(starts, names)) + "\n", encoding="utf-8")
    print(f"{srt} ({len(cues)} cues) · {out.parent / 'chapters.txt'}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("spec"); ap.add_argument("out")
    ap.add_argument("--from", dest="t0", type=float, default=0); ap.add_argument("--to", dest="t1", type=float)
    ap.add_argument("--preview", action="store_true", help="ignore recordings: placeholders everywhere")
    ap.add_argument("--square", action="store_true", help="the clay owner in a small square on story/qa (off: owner 2026-11-03)")
    ap.add_argument("--vertical", action="store_true", help="9:16 Short; give the parts with --ranges")
    ap.add_argument("--ranges", default="", help="vertical: source seconds a-b,c-d … joined in order")
    ap.add_argument("--heading", default="", help="vertical: 'TITLE|subtitle|Arabic' shown at the top until the first word pops")
    ap.add_argument("--segments", action="store_true", help="no render: print every segment's start/end/kind/line")
    ap.add_argument("--captions", action="store_true", help="no render: write captions-upload.srt + chapters.txt next to OUT "
                    "from the same timeline (English, as on screen)")
    a = ap.parse_args()
    spec = json.loads((ROOT / a.spec).read_text())
    segs, voice, mouthv, total = build(spec, a.preview)
    if a.captions and not a.vertical:
        return write_captions(segs, total, ROOT / a.out)
    if a.segments:
        for x in segs:
            print(f"{x['start']:8.2f} {x['end']:8.2f} {x['kind']:6} {x.get('line', '')!s:>4} voice {x.get('span', ('', ''))} {(x.get('ar') or x.get('file') or '')[:50]}")
        return
    if a.vertical:
        ranges = [tuple(map(float, r.split("-"))) for r in a.ranges.split(",")] if a.ranges else [(a.t0, a.t1 or total)]
        ranges = vertical_keep(segs, ranges)
    star_times = [x for s in segs for x in s.get("stars", [])]
    t1 = min(a.t1 or total, total)

    tmp = pathlib.Path(tempfile.mkdtemp(prefix="story-"))
    signal.signal(signal.SIGTERM, lambda *_: sys.exit(1))
    try:
        vtrack = mix(voice, total)
        if a.vertical:   # owner 2026-11-11: pauses inside a sentence halved, no pause longer than 1 s
            ranges = squeeze_pauses(vtrack, ranges)
            write_vcaptions(segs, ranges, ROOT / a.out)
            if a.captions: return
        sfx = np.zeros_like(vtrack)
        chime = read_audio(ROOT / "assets/stars/chime.wav") * 0.6
        pop = read_audio(ROOT / "assets/sfx/pop.wav") * 0.18
        for st in ([] if a.vertical else star_times):   # vertical Shorts get their own 3 chimes (below)
            p = int(st * SR); sfx[p:p + len(chime)] += chime[:len(sfx) - p]
        # mouth: the voice's loudness (placeholders: syllable-like bursts), only outside the filmed parts
        mv = mix(mouthv, total)
        for s in segs:
            if s["kind"] == "camera": mv[int(s["start"] * SR):int(s["end"] * SR)] = 0
        import soundfile as sf
        sf.write(tmp / "mouth.wav", mv, SR)
        env, vo, _ = nar.envelope(tmp / "mouth.wav")
        mouths = nar.mouth_track(env, vo)
        lift = np.convolve(env * vo, np.ones(8) / 8, mode="same")
        rnd = random.Random(7); blinks, bt = set(), 1.2
        while bt < total:
            f_ = int(bt * FPS); blinks.update({f_ + 1, f_ + 2}); bt += rnd.uniform(2.5, 5.0)

        half_dir = ROOT / "library/work/narrator/film3d/set"   # 3D-film look, early 30s (owner 2026-11-04; clay = narrator/half/set)
        hw, hh = Image.open(half_dir / "still.png").size
        fh = int(H * 1.04); big = nar.load_set(half_dir, (int(hw * fh / hh), fh))
        if a.square:
            global TEXT_CX, TEXT_W
            TEXT_CX, TEXT_W = 1000, 1120
            small = nar.load_set(ROOT / "library/work/narrator/set", (int(1344 * 0.72), int(768 * 0.72)))
        P = Painter(spec)

        # pops: when each word joins the list (and its sound). ONE running list on the right across sentences (owner
        # 2026-11-03): only the important words (verbs, here/too/before/after…), up to 5, the 6th clears it; a word
        # already in the list doesn't pop again — it only lights up in the sentence, in its list colour.
        # LEFT: the opposites (spec "opposites"), popping the first time either word is said; they never go on the right,
        # which keeps the other verbs and small words (owner 2026-11-03).
        R, L = RunningList(), RunningList()
        muted = 0
        opp = spec.get("opposites", [])
        def opposite(tok):
            c = core(tok)
            for k, o in enumerate(opp):
                if c in o["forms"] or (len(c) > 2 and c[0] in "وفب" and c[1:] in o["forms"]): return k
            return None
        for s in segs:
            s["pops"] = []
            if s["kind"] in ("talk", "pair", "camera"):
                R.clear(s["start"]); L.clear(s["start"])
            if s["kind"] == "story":
                toks = ar_text(s["ar"]).split()
                v0, v1 = s["span"]; n = max(1, sum(len(core(x)) + 1 for x in toks))
                pos = lambda idx: v0 + (v1 - v0) * (sum(len(core(x)) + 1 for x in toks[:idx]) + 0.5 * len(core(toks[idx]))) / n
                items = [("v", vb) for vb in s.get("verbs", [])] or [("w", w) for w in s.get("words", [])]
                for j, (typ, it) in enumerate(items):
                    word = minimal(it[1] if typ == "v" else it[0])
                    idx = find_token(toks, word.split()[-1])
                    tt = pos(idx) if idx is not None else v0 + (v1 - v0) * (j + 0.5) / len(items)
                    if opposite(word) is not None: continue   # opposites live on the LEFT only (owner 2026-11-03)
                    e, new = R.add(word, tt, typ=typ, it=it)
                    if new: s["pops"].append({"t": e["t"], "new": True})
                    s.setdefault("lit", []).append({"t": e["t"] if new else tt, "tok": idx, "e": e})
                for idx, tok in enumerate(toks):
                    k = opposite(tok)
                    if k is None: continue
                    e, new = L.add(k, pos(idx), it=(opp[k]["a"], opp[k]["b"]))
                    if new: s["pops"].append({"t": e["t"], "new": True})
                    s.setdefault("lit_l", []).append({"t": e["t"] if new else pos(idx), "tok": idx, "e": e})
            elif s["kind"] == "pair" and s.get("new_pair"):
                v0, v1 = s["span"]
                s["pops"] = [{"t": v0 + 0.1, "k": 0}, {"t": v0 + (v1 - v0) * 0.6, "k": 1}]
            for p in s["pops"]:
                if not p.get("new", True): continue
                if any(-1.2 < p["t"] - st < 1.2 for st in star_times):   # a pop next to the star chime sounded like an
                    muted += 1; continue                                   # echo (owner 2026-11-03): the card pops silently
                q = int(p["t"] * SR); sfx[q:q + len(pop)] += pop[:len(sfx) - q]
        if muted: print(f"{muted} pop sound(s) next to a star chime muted")
        sf.write(tmp / "audio.wav", np.clip(vtrack + sfx, -1, 1), SR)
        # loudness: ONE gain for the whole track to −14 LUFS + a peak limiter. Dynamic loudnorm pumped the gain up in
        # the pauses and again inside the star chime's tail — a swell 0.7 s later that sounded like an echo (owner 2026-11-03).
        meas = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", str(tmp / "audio.wav"), "-af", "ebur128", "-f", "null", "-"],
                              capture_output=True, text=True).stderr
        lufs = float(re.findall(r"I:\s+(-?[\d.]+) LUFS", meas)[-1])
        afilter = f"volume={-14 - lufs:.2f}dB,alimiter=limit={10 ** (-1.5 / 20):.3f}:level=false"
        if a.vertical:
            full = np.clip(vtrack + sfx, -1, 1)
            short = np.concatenate([full[round(r0 * FPS) * (SR // FPS):round(r1 * FPS) * (SR // FPS)] for r0, r1 in ranges])
            dloc = len(short) / SR
            v_stars_t = [dloc / 3, 2 * dloc / 3 - 0.1 * dloc, dloc - 6.0]   # owner 2026-11-11: 2nd 10 % earlier, 3rd 5 s earlier
            for st in v_stars_t:
                p = max(0, int(st * SR)); n_ = len(short[p:p + len(chime)]); short[p:p + n_] += chime[:n_]
            sf.write(tmp / "short.wav", np.clip(short, -1, 1), SR)
            meas = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", str(tmp / "short.wav"), "-af", "ebur128", "-f", "null", "-"],
                                  capture_output=True, text=True).stderr
            lufs = float(re.findall(r"I:\s+(-?[\d.]+) LUFS", meas)[-1])
            afilter = f"volume={-14 - lufs:.2f}dB,alimiter=limit={10 ** (-1.5 / 20):.3f}:level=false"

        cam = None
        ain = ["-i", str(tmp / "short.wav")] if a.vertical else ["-ss", f"{a.t0:.3f}", "-t", f"{t1 - a.t0:.3f}", "-i", str(tmp / "audio.wav")]
        if a.vertical:
            vframe = vertical_painter(a, spec, segs, ranges, P, R, L, big, nar, v_stars_t)
        enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{VW}x{VH}" if a.vertical else f"{W}x{H}",
                                "-r", str(FPS), "-i", "-"] + ain + [
                                "-c:v", "libx264", "-crf", "17", "-preset", "medium", "-pix_fmt", "yuv420p",
                                "-c:a", "aac", "-b:a", "192k", "-af", afilter, "-shortest", str(ROOT / a.out)],
                               stdin=subprocess.PIPE)
        fis = [fi for r0, r1 in ranges for fi in range(round(r0 * FPS), round(r1 * FPS))] if a.vertical else range(int(a.t0 * FPS), int(t1 * FPS))
        for li, fi in enumerate(fis):
            t = fi / FPS
            s = next((x for x in segs if x["start"] <= t < x["end"]), segs[-1])
            k = s["kind"]
            key = (mouths[min(fi, len(mouths) - 1)], int(fi in blinks))
            body = nar.body(t, lift[min(fi, len(lift) - 1)])
            if a.vertical:
                enc.stdin.write(vframe(t, li / FPS, s, k, key, body).tobytes()); continue
            if k == "card":
                if "card_im" not in s:
                    s["card_im"] = Image.open(ROOT / s["image"]).convert("RGB").resize((W, H), Image.LANCZOS)
                enc.stdin.write(s["card_im"].tobytes()); continue
            if k == "camera":
                if s.get("video"):
                    if cam is None or cam[0] is not s:
                        cam = (s, subprocess.Popen(["ffmpeg", "-v", "error", "-i", s["video"], "-vf",
                               f"fps={FPS},scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H}",
                               "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE))
                    buf = cam[1].stdout.read(W * H * 3)
                    frame = Image.frombytes("RGB", (W, H), buf) if len(buf) == W * H * 3 else Image.new("RGB", (W, H), PAPER)
                else:
                    frame = Image.new("RGB", (W, H), (70, 74, 80)); d = ImageDraw.Draw(frame)
                    d.text((W / 2, H / 2 - 40), f"your filmed {s['file']} (lines {s['lines'][0]}–{s['lines'][-1]})", font=ENB(54), fill=(235, 235, 235), anchor="mm")
                hook = s.get("pic") and s["subs"] and t < s["subs"][0][1]
                if hook:
                    frame = P.page(s["pic"])
                for j, (b0, b1) in enumerate(s["subs"]):
                    if b0 <= t < b1 + 0.2:
                        box = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(box)
                        lines = wrap_en(s["en"][j], ENB(44), 1500)
                        y = H - 70 - len(lines) * 58
                        d.rounded_rectangle((W / 2 - 800, y - 18, W / 2 + 800, H - 50), 22, fill=(0, 0, 0, 150))
                        for ln in lines:
                            d.text((W / 2, y), ln, font=ENB(44), fill=(255, 255, 255, 255), anchor="ma"); y += 58
                        frame.paste(box, (0, 0), box)
            elif k == "talk":
                frame = Image.new("RGB", (W, H), PAPER)
                im = nar.transform(big[key], *body)
                frame.paste(im, ((W - im.width) // 2, H - im.height + int(H * 0.03)), im)
                caption_box(frame, s["ar"], s["en"], 260, W - 260)
            elif k == "pair":
                frame = Image.new("RGB", (W, H), PAPER)
                im = nar.transform(big[key], *body)
                frame.paste(im, (int(W * 0.75 - im.width / 2), H - im.height + int(H * 0.03)), im)
                p0 = segs.index(s)
                first_pair = next(x for x in reversed(segs[:p0 + 1]) if x.get("new_pair"))
                for j, (cy, col) in enumerate([(240, CRAYON[0]), (590, CRAYON[2])]):
                    pt = first_pair["pops"][j]["t"]
                    if t >= pt:
                        paste_card(frame, P.pair_card(*s["pair"][j], col), 530, cy, t - pt)
                if t >= first_pair["pops"][1]["t"]:
                    ImageDraw.Draw(frame).text((530, 415), "↕", font=SYM(64), fill=GREY, anchor="mm")
                caption_box(frame, s["ar"], s["en"], 60, 1000)
            else:   # story / qa
                frame = P.page(s["pic"])
                d = ImageDraw.Draw(frame)
                if k == "story":
                    toks = ar_text(s["ar"]).split()
                    cols = [INK] * len(toks)
                    for p in s.get("lit_l", []) + s.get("lit", []):   # lit in its list colour while still in the list (right wins)
                        if t >= p["t"] and p["tok"] is not None and t < p["e"]["until"]: cols[p["tok"]] = p["e"]["col"]
                    y = draw_ar_tokens(d, toks, cols, AR(60), TEXT_CX, 742, TEXT_W)
                    draw_en(d, s["en"], ENI(34), TEXT_CX, y - 4, TEXT_W)
                else:
                    q0, q1 = s["q_span"]; a0, a1 = s["a_span"]
                    qt = ar_text(s["q"]).split()
                    y = draw_ar_tokens(d, qt, [INK] * len(qt), AR(56), TEXT_CX, 738, TEXT_W)
                    y = draw_en(d, s["qe"], ENI(32), TEXT_CX, y - 6, TEXT_W)
                    if q1 + 0.2 <= t < a0:      # thinking: three dots filling up
                        n = min(3, int((t - q1 - 0.2) / max(0.3, (a0 - q1 - 0.2) / 3)) + 1)
                        for j in range(3):
                            cx = TEXT_CX - 50 + j * 50
                            d.ellipse((cx - 12, y + 14, cx + 12, y + 38), fill=GREEN if j < n else (215, 210, 200))
                    if t >= a0:
                        at = ar_text(s["a"]).split()
                        y2 = draw_ar_tokens(d, at, [GREEN] * len(at), AR(56), TEXT_CX, y + 2, TEXT_W)
                        draw_en(d, s["ae"], ENI(32), TEXT_CX, y2 - 6, TEXT_W, fill=GREEN)
                for e in R.entries + L.entries:   # the two running lists (a full one fades out before the next item)
                    if e["t"] <= t < e["until"]:
                        fade = min(1.0, (e["until"] - t) / FADE)
                        if "typ" in e:
                            cimg = P.verb_item(*e["it"], e["col"]) if e["typ"] == "v" else P.word_item(*e["it"], e["col"])
                            paste_item(frame, cimg, LIST_R, LIST_YS[e["row"]], t - e["t"], fade=fade)
                        else:
                            paste_item(frame, P.opp_item(*e["it"], e["col"]), LIST_L, LIST_YS[e["row"]], t - e["t"], fade=fade)
                if a.square:  # the narrator square
                    im = nar.transform(small[key], *body)
                    boxi = Image.new("RGB", im.size, PAPER); boxi.paste(im, (0, 0), im)
                    cx, cy = boxi.width // 2, int(boxi.height * 0.47)
                    sqw = SQ[2] - SQ[0]
                    face = boxi.crop((cx - 230, cy - 230, cx + 230, cy + 230)).resize((sqw, sqw), Image.LANCZOS)
                    ImageDraw.Draw(frame).rounded_rectangle((SQ[0] - 6, SQ[1] - 6, SQ[2] + 6, SQ[3] + 6), 26, fill=(255, 255, 255))
                    m = Image.new("L", (sqw, sqw), 0); ImageDraw.Draw(m).rounded_rectangle((0, 0, sqw, sqw), 22, fill=255)
                    frame.paste(face, SQ[:2], m)
            P.stars_on(frame, t, star_times)
            enc.stdin.write(frame.tobytes())
        enc.stdin.close(); enc.wait()
        if cam: cam[1].kill()
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    print(f"{a.out}: {a.t0:.1f}–{t1:.1f} s of {total:.1f} s ({total / 60:.1f} min), stars at "
          + ", ".join(f"{x:.0f}s" for x in star_times))


if __name__ == "__main__":
    main()
