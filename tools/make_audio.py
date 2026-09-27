#!/usr/bin/env python3
"""Generate one MP3 per ```say:<speaker>``` block of a video script, using free Edge TTS voices.

Usage:
    pip install -r tools/requirements.txt
    python tools/make_audio.py videos/001-why-2-minutes.md
    python tools/make_audio.py videos/*.md --out audio

Output (per video):
    audio/<video-name>/01-narrator.mp3, 02-teacher.mp3, ...
    audio/<video-name>/cues.txt   (clip number, speaker and text, in timeline order)
"""
import argparse
import asyncio
import pathlib
import re
import sys

import edge_tts

# speaker tag -> (Edge TTS voice, speaking rate)
SPEAKERS = {
    "narrator": ("en-US-AndrewNeural", "+0%"),
    "teacher": ("ar-SA-HamedNeural", "-10%"),
    "teacher-slow": ("ar-SA-HamedNeural", "-35%"),
    "sami": ("ar-SY-LaithNeural", "-10%"),
    "lina": ("ar-SA-ZariyahNeural", "-10%"),
}

BLOCK = re.compile(r"^```say:([\w-]+)[ \t]*\n(.*?)\n```", re.MULTILINE | re.DOTALL)


def parse_blocks(script: pathlib.Path):
    blocks = []
    for speaker, text in BLOCK.findall(script.read_text(encoding="utf-8")):
        if speaker not in SPEAKERS:
            sys.exit(f"{script}: unknown speaker '{speaker}' (known: {', '.join(SPEAKERS)})")
        blocks.append((speaker, " ".join(text.split())))
    return blocks


async def render(script: pathlib.Path, out_root: pathlib.Path):
    blocks = parse_blocks(script)
    if not blocks:
        print(f"{script}: no say: blocks, skipped")
        return
    out_dir = out_root / script.stem
    out_dir.mkdir(parents=True, exist_ok=True)
    cues = []
    for i, (speaker, text) in enumerate(blocks, 1):
        voice, rate = SPEAKERS[speaker]
        target = out_dir / f"{i:02d}-{speaker}.mp3"
        await edge_tts.Communicate(text, voice, rate=rate).save(str(target))
        cues.append(f"{i:02d}  [{speaker}]  {text}")
        print(f"  {target.name}")
    (out_dir / "cues.txt").write_text("\n".join(cues) + "\n", encoding="utf-8")
    print(f"{script.name}: {len(blocks)} clips -> {out_dir}")


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("scripts", nargs="+", type=pathlib.Path, help="video script .md files")
    parser.add_argument("--out", type=pathlib.Path, default=pathlib.Path("audio"), help="output folder (default: audio)")
    args = parser.parse_args()
    for script in args.scripts:
        asyncio.run(render(script, args.out))


if __name__ == "__main__":
    main()
