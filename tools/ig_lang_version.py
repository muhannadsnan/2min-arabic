#!/usr/bin/env python3
"""A language version of a Short for Instagram that looks like its own video (owner 2026-10-30): the dubbed voice,
subtitles burned in IN THAT LANGUAGE'S SCRIPT, a big hook line in that language — AND different pictures, because
the near-copy filter compares images (9 x03 dubs that only changed the voice stopped getting views; the first
text-only version still looked like the English Reel, owner 2026-10-30):
  · a cover for the first 2.2 s: another character's close-up (talking) on another background, hook on top;
  · the whole video zoomed and shifted a little differently, colour-shifted, in a coloured frame;
  · the yellow badge replaced by a translated badge in the language's colour.

    $TTS tools/ig_lang_version.py <stem> <lang> [--audio hi] [--hook "…"]      ($TTS: needs numpy + PIL)
        → output/<stem>/ig-<lang>.mp4   (Instagram order: hi, ur, id, tr, ms — owner 2026-10-30)

Needs: output/<stem>/<title>-nocap.mp4 (NO_CAPTIONS=1 python3 tools/assemble.py videos/<stem>.md),
output/<stem>/dub-<audio>.m4a (tools/dub_track.py; ur uses hi, ms uses id), dubs/<stem>.json (the translations).
Only the translated narrator lines are burned in — the Arabic is already on the cards.
"""
import argparse
import json
import pathlib
import re
import subprocess
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools" / "animate"))
from compose_talk import keyed, place  # noqa: E402

FONT = {"hi": "Noto Sans Devanagari", "ur": "Noto Nastaliq Urdu", "fa": "Noto Nastaliq Urdu", "bn": "Noto Sans Bengali"}
AUDIO = {"ur": "hi", "ms": "id"}
SIZE = {"ur": 150, "fa": 150, "hi": 96}   # Nastaliq renders small at the Latin size
# the look per language: cover character + background, frame colour (RGB), zoom, horizontal shift (-1…1), hue shift
# no rooftop: its skyline is all minarets (owner 2026-10-28: too many mosques)
LOOK = {
    "hi": dict(char="omar", bg="cafe", color=(234, 108, 22), zoom=1.08, shift=-0.6, hue=6),
    "ur": dict(char="sami", bg="alley", color=(21, 128, 61), zoom=1.10, shift=0.6, hue=-6),
    "id": dict(char="lina", bg="desk", color=(200, 38, 38), zoom=1.09, shift=0.0, hue=8),
    "tr": dict(char="waiter", bg="alley", color=(14, 116, 184), zoom=1.11, shift=-0.3, hue=-8),
    "ms": dict(char="lina", bg="cafe", color=(109, 40, 217), zoom=1.08, shift=0.4, hue=4),
}
BADGE = {"hi": "2 मिनट अरबी", "ur": "دو منٹ عربی", "id": "2 Menit Bahasa Arab", "tr": "2 Dakikada Arapça",
         "ms": "2 Minit Bahasa Arab"}
DAY = {"hi": "दिन", "ur": "دن", "id": "Hari", "tr": "Gün", "ms": "Hari"}
BADGE_BOX = (188, 70, 891, 149)   # the yellow badge in the 1080×1920 frame (assemble.py BADGE_Y)
W, H, COVER, FPS = 1080, 1920, 2.2, 30


def ts(t):
    return f"{int(t // 3600)}:{int(t % 3600 // 60):02d}:{t % 60:05.2f}"


def cover_frames(look, folder):
    """The talking close-up on its own background, 8 mouth changes a second → folder/c%03d.png."""
    bg = Image.open(ROOT / "library" / "backgrounds" / f"{look['bg']}.png").convert("RGB")
    s = max(W / bg.width, H / bg.height)
    bg = bg.resize((round(bg.width * s), round(bg.height * s)), Image.LANCZOS)
    bg = bg.crop(((bg.width - W) // 2, (bg.height - H) // 2, (bg.width - W) // 2 + W, (bg.height - H) // 2 + H))
    bg = bg.filter(ImageFilter.GaussianBlur(4))
    mean = np.asarray(bg, dtype=np.float32).reshape(-1, 3).mean(axis=0)
    sets = ROOT / "library" / "sets" / "v2"
    mouths = [sets / f"{look['char']}_cB_talk{i}.png" for i in (1, 3, 2, 5, 4, 2)] + [sets / f"{look['char']}_cB.png"]
    pics = {m: place(bg.copy(), keyed(str(m)), 0.5, 0.7232, mean) for m in set(mouths)}
    for i in range(int(COVER * FPS)):
        pics[mouths[(i * 8 // FPS) % len(mouths)]].save(folder / f"c{i:03d}.png")


def frame_overlay(look, path):
    """Coloured frame + the badge plate (covers the yellow badge wherever the zoom moved it)."""
    z, ox, oy = look["zoom"], crop_x(look), 0
    x0, y0, x1, y1 = BADGE_BOX
    box = (x0 * z - ox - 26, y0 * z - oy - 14, x1 * z - ox + 26, y1 * z - oy + 14)
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rectangle((0, 0, W - 1, H - 1), outline=look["color"] + (255,), width=16)
    d.rounded_rectangle(box, radius=(box[3] - box[1]) // 2, fill=look["color"] + (255,), outline=(255, 255, 255, 255), width=5)
    im.save(path)
    return box


def crop_x(look):
    spare = W * look["zoom"] - W
    return round(spare / 2 * (1 + look["shift"]))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("stem"); ap.add_argument("lang")
    ap.add_argument("--audio"); ap.add_argument("--hook", help="hook line in that language (default: the first sentence)")
    a = ap.parse_args()
    out_dir = ROOT / "output" / a.stem
    nocap = next(out_dir.glob("*-nocap.mp4"))
    audio = out_dir / f"dub-{a.audio or AUDIO.get(a.lang, a.lang)}.m4a"
    spec = json.loads((ROOT / "dubs" / f"{a.stem}.json").read_text(encoding="utf-8"))
    subprocess.run(["python3", str(ROOT / "tools" / "dub_subs.py"), f"dubs/{a.stem}.json", a.lang], cwd=ROOT, check=True,
                   capture_output=True)
    srt = (out_dir / f"subs-{a.lang}.srt").read_text(encoding="utf-8")
    cues = re.findall(r"\d+\n([\d:,]+) --> ([\d:,]+)\n(.*?)(?:\n\n|\Z)", srt, re.S)
    sec = lambda s: sum(float(x) * m for x, m in zip(s.replace(",", ".").split(":"), (3600, 60, 1)))
    arabic = re.compile(r"[ء-ي][ً-ْ]")   # Arabic WITH tashkeel = a lesson line (already on a card)
    hook = a.hook or re.split(r"(?<=[.!?۔।])\s", spec[a.lang]["1"])[0]
    look = LOOK[a.lang]
    font, size = FONT.get(a.lang, "Noto Sans"), SIZE.get(a.lang, 84)

    work = out_dir / f"ig-{a.lang}-look"; work.mkdir(exist_ok=True)
    cover_frames(look, work)
    box = frame_overlay(look, work / "frame.png")
    day = re.match(r"(\d{3})-", a.stem)
    num = str(int(day.group(1))) if day else ""
    if a.lang in ("ur", "fa"):   # Latin digits inside right-to-left text came out as "212": use Eastern digits
        num = num.translate(str.maketrans("0123456789", "۰۱۲۳۴۵۶۷۸۹"))
    badge = BADGE[a.lang] + (f" · {DAY[a.lang]} {num}" if day else "")
    bx, by = (box[0] + box[2]) / 2, (box[1] + box[3]) / 2
    ass = [
        "[Script Info]", "ScriptType: v4.00+", "PlayResX: 1080", "PlayResY: 1920", "WrapStyle: 0", "",
        "[V4+ Styles]",
        "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, "
        "StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding",
        f"Style: Sub,{font},{size},&H00FFFFFF,&H00FFFFFF,&H00000000,&H64000000,-1,0,0,0,100,100,0,0,1,7,3,2,90,90,540,1",
        f"Style: Hook,{font},{int(size * 1.3)},&H0000C8F6,&H00FFFFFF,&H00000000,&H96000000,-1,0,0,0,100,100,0,0,1,10,5,8,70,70,250,1",
        f"Style: Badge,{font},{int(size * 0.8)},&H00FFFFFF,&H00FFFFFF,&H00000000,&H00000000,-1,0,0,0,100,100,0,0,1,0,0,5,0,0,0,1",
        "", "[Events]", "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text",
        f"Dialogue: 1,{ts(0)},{ts(COVER)},Hook,,0,0,0,,{hook}",
        f"Dialogue: 2,{ts(0)},{ts(9999)},Badge,,0,0,0,,{{\\pos({bx:.0f},{by:.0f})}}{badge}",
    ]
    for s, e, txt in cues:
        if arabic.search(txt) or sec(s) < COVER:
            continue
        ass.append(f"Dialogue: 0,{ts(sec(s))},{ts(sec(e))},Sub,,0,0,0,,{txt.replace(chr(10), ' ')}")
    af = out_dir / f"ig-{a.lang}.ass"; af.write_text("\n".join(ass) + "\n", encoding="utf-8")
    z = look["zoom"]
    vf = (f"[0:v]scale={round(W * z / 2) * 2}:{round(H * z / 2) * 2},crop={W}:{H}:{crop_x(look)}:0,"
          f"hue=h={look['hue']}:s=1.08[v];"
          f"[v][2:v]overlay=0:0:eof_action=pass[c];[c][3:v]overlay=0:0,"
          f"ass={af}:fontsdir=/usr/share/fonts/truetype/noto[out]")
    out = out_dir / f"ig-{a.lang}.mp4"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(nocap), "-i", str(audio),
                    "-framerate", str(FPS), "-i", str(work / "c%03d.png"), "-loop", "1", "-i", str(work / "frame.png"),
                    "-filter_complex", vf, "-map", "[out]", "-map", "1:a", "-c:v", "libx264", "-crf", "18",
                    "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "160k", "-shortest", str(out)], check=True)
    print(f"{out}  (hook: {hook} · badge: {badge})")


if __name__ == "__main__":
    main()
