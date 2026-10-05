#!/usr/bin/env python3
"""Approval preview of a video's soundtrack: the voiceover WITH the filmed clips' sound (hello, goodbye) mixed in at
their times, so the owner hears exactly what the video will sound like (no silent gaps where the clips go).

    python3 tools/preview_audio.py videos/009-….md     → output/audio-for-approval/<video>.mp3
"""
import json
import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent


def main():
    stem = pathlib.Path(sys.argv[1]).stem
    tl = json.loads((ROOT / "audio" / stem / "timeline.json").read_text(encoding="utf-8"))
    ins = ["-i", str(ROOT / "audio" / stem / "voiceover.wav")]
    chain, labels = [], ["[0:a]"]
    for k, v in enumerate(tl.get("videos", []), 1):
        ins += ["-i", str(ROOT / "footage" / "clips" / f"{v['name']}.mp4")]
        ms = int(v["start"] * 1000)
        chain.append(f"[{k}:a]aresample=48000,adelay={ms}|{ms}[c{k}]")
        labels.append(f"[c{k}]")
    chain.append(f"{''.join(labels)}amix=inputs={len(labels)}:normalize=0,loudnorm=I=-14:TP=-1.5[a]")
    out = ROOT / "output" / "audio-for-approval" / f"{stem}.mp3"
    out.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(["ffmpeg", "-v", "error", "-y", *ins, "-filter_complex", ";".join(chain), "-map", "[a]",
                    "-c:a", "libmp3lame", "-q:a", "2", str(out)], check=True)
    print(out)


if __name__ == "__main__":
    main()
