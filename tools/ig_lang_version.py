#!/usr/bin/env python3
"""A language version of a Short for Instagram that looks like its own video (owner 2026-10-30): the dubbed voice,
subtitles burned in IN THAT LANGUAGE'S SCRIPT, and a big hook line in that language over the first 2 s — so the
near-copy filter doesn't see "the same video again" (9 x03 dubs that only changed the voice stopped getting views).

    python3 tools/ig_lang_version.py <stem> <lang> [--audio hi] [--hook "…"]
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

ROOT = pathlib.Path(__file__).resolve().parent.parent
FONT = {"hi": "Noto Sans Devanagari", "ur": "Noto Nastaliq Urdu", "fa": "Noto Nastaliq Urdu", "bn": "Noto Sans Bengali"}
AUDIO = {"ur": "hi", "ms": "id"}
SIZE = {"ur": 150, "fa": 150, "hi": 96}   # Nastaliq renders small at the Latin size


def ts(t):
    return f"{int(t // 3600)}:{int(t % 3600 // 60):02d}:{t % 60:05.2f}"


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
    font, size = FONT.get(a.lang, "Noto Sans"), SIZE.get(a.lang, 84)
    ass = [
        "[Script Info]", "ScriptType: v4.00+", "PlayResX: 1080", "PlayResY: 1920", "WrapStyle: 0", "",
        "[V4+ Styles]",
        "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, "
        "StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding",
        f"Style: Sub,{font},{size},&H00FFFFFF,&H00FFFFFF,&H00000000,&H64000000,-1,0,0,0,100,100,0,0,1,7,3,2,90,90,540,1",
        f"Style: Hook,{font},{int(size * 1.3)},&H0000C8F6,&H00FFFFFF,&H00000000,&H96000000,-1,0,0,0,100,100,0,0,1,10,5,2,70,70,620,1",
        "", "[Events]", "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text",
        f"Dialogue: 1,{ts(0)},{ts(2.2)},Hook,,0,0,0,,{hook}",
    ]
    for s, e, txt in cues:
        if arabic.search(txt) or sec(s) < 2.2:
            continue
        ass.append(f"Dialogue: 0,{ts(sec(s))},{ts(sec(e))},Sub,,0,0,0,,{txt.replace(chr(10), ' ')}")
    af = out_dir / f"ig-{a.lang}.ass"; af.write_text("\n".join(ass) + "\n", encoding="utf-8")
    out = out_dir / f"ig-{a.lang}.mp4"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(nocap), "-i", str(audio), "-map", "0:v", "-map", "1:a",
                    "-vf", f"ass={af}:fontsdir=/usr/share/fonts/truetype/noto", "-c:v", "libx264", "-crf", "18",
                    "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "160k", "-shortest", str(out)], check=True)
    print(f"{out}  (hook: {hook})")


if __name__ == "__main__":
    main()
