"""SRT -> styled one-line burn-in captions (ASS) for vertical Shorts. Usage: mkass.py in.srt out.ass"""
import re
import sys

MAX = 18  # max characters per caption line
YELLOW = r"\c&H00D7FF&"
ARABIC = re.compile(r"\(([؀-ۿ ]+)\)")

HEADER = """[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
WrapStyle: 0
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,Noto Sans,84,&H00FFFFFF,&H00FFFFFF,&H00000000,&H64000000,-1,0,0,0,100,100,0,0,1,7,3,2,110,110,540,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""


def t2s(t):
    h, m, r = t.strip().split(":")
    s, ms = r.split(",")
    return int(h) * 3600 + int(m) * 60 + int(s) + int(ms) / 1000


def s2a(x):
    cs = round(x * 100)
    h, cs = divmod(cs, 360000)
    m, cs = divmod(cs, 6000)
    s, cs = divmod(cs, 100)
    return f"{h}:{m:02}:{s:02}.{cs:02}"


def fmt(p):
    """Arabic in (...) goes on its own line above, big, in Naskh; Arabic words in yellow."""
    p = re.sub(r"(Marhaba!?|Ma'a as-salaama!?)", lambda m: "{" + YELLOW + "}" + m.group(1) + r"{\r}", p)
    m = ARABIC.search(p)
    if m:
        rest = (p[:m.start()] + p[m.end():]).strip()
        arabic = "{" + YELLOW + r"\fnNoto Naskh Arabic\b1\fs124}" + m.group(1) + r"{\r}"
        p = arabic + (r"\N" + rest if rest else "")
    return p


events = []
for block in open(sys.argv[1], encoding="utf-8").read().strip().split("\n\n"):
    lines = block.split("\n")
    st, en = (t2s(x) for x in lines[1].split("-->"))
    text = " ".join(lines[2:])
    if ARABIC.search(text):  # keep Arabic captions whole
        events.append((st, en, text))
        continue
    parts, cur = [], ""
    for w in text.split():
        if cur and len(cur) + 1 + len(w) > MAX:
            parts.append(cur)
            cur = w
        else:
            cur = (cur + " " + w).strip()
    parts.append(cur)
    if len(parts) > 1 and len(parts[-1]) <= 4:
        last = parts.pop()
        parts[-1] += " " + last
    total, t = sum(len(p) for p in parts), st
    for p in parts:
        d = (en - st) * len(p) / total
        events.append((t, t + d, p))
        t += d

with open(sys.argv[2], "w", encoding="utf-8") as f:
    f.write(HEADER)
    for a, b, p in events:
        f.write(f"Dialogue: 0,{s2a(a)},{s2a(b)},Default,,0,0,0,,{fmt(p)}\n")
print(len(events), "caption lines")
