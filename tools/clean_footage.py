#!/usr/bin/env python3
"""Clean the sound of a phone recording (noise-free, centered, YouTube loudness) and normalize the video.

    python3 tools/clean_footage.py "footage/my take.mov" footage/clips/hello.mp4 [--start 0.7 --end 3.45]

Steps: blend the phone's two mics into centered mono → 80 Hz low-cut → DeepFilterNet AI noise removal (removes hiss,
fan and room noise) → gentle compression → −14 LUFS (−17 mono) with a peak limiter → optional cut with soft fades →
1080×1920, 30 fps, H.264 + AAC. Uses the local TTS environment for DeepFilterNet (TTS_HOME, see make_audio.py).
"""
import argparse
import os
import pathlib
import re
import subprocess
import sys
import tempfile

TTS_HOME = pathlib.Path(os.environ.get("TTS_HOME", "/media/msn/GamesLinux/AI/tts"))
DFN = """
import sys
from df.enhance import enhance, init_df, load_audio, save_audio
model, state, _ = init_df()
audio, _ = load_audio(sys.argv[1], sr=state.sr())
save_audio(sys.argv[2], enhance(model, state, audio), state.sr())
"""


def run(cmd, **kw):
    return subprocess.run(cmd, check=True, **kw)


def loudness(path):
    err = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", str(path), "-af", "ebur128", "-f", "null", "-"],
                         capture_output=True, text=True).stderr
    return float(re.search(r"I:\s+(-?[\d.]+) LUFS", err[err.rfind("Summary:"):]).group(1))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("src", type=pathlib.Path)
    ap.add_argument("dst", type=pathlib.Path)
    ap.add_argument("--start", type=float, default=None)
    ap.add_argument("--end", type=float, default=None)
    args = ap.parse_args()
    with tempfile.TemporaryDirectory() as tmp:
        tmp = pathlib.Path(tmp)
        raw, clean, level = tmp / "raw.wav", tmp / "clean.wav", tmp / "level.wav"
        run(["ffmpeg", "-v", "error", "-y", "-i", str(args.src), "-map", "0:a:0", "-af",
             "pan=mono|c0=0.5*c0+0.5*c1,highpass=f=80", "-ar", "48000", str(raw)])
        env = dict(os.environ, HF_HOME=str(TTS_HOME / "hf"))
        run([str(TTS_HOME / "venv" / "bin" / "python"), "-c", DFN, str(raw), str(clean)], env=env,
            stderr=subprocess.DEVNULL)
        comp = tmp / "comp.wav"
        run(["ffmpeg", "-v", "error", "-y", "-i", str(clean), "-af",
             "acompressor=threshold=-22dB:ratio=2.5:attack=15:release=250", str(comp)])
        gain = -17.0 - loudness(comp)
        run(["ffmpeg", "-v", "error", "-y", "-i", str(comp), "-af",
             f"volume={gain:.2f}dB,alimiter=limit=0.708:level=false", "-ar", "48000", str(level)])
        cut, fades = [], "anull"
        if args.start is not None or args.end is not None:
            s = args.start or 0.0
            e = args.end if args.end is not None else float(subprocess.run(
                ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(args.src)],
                capture_output=True, text=True).stdout)
            cut = ["-ss", f"{s}", "-to", f"{e}"]
            fades = f"afade=t=in:d=0.08,afade=t=out:st={max(e - s - 0.15, 0):.2f}:d=0.15"
        args.dst.parent.mkdir(parents=True, exist_ok=True)
        run(["ffmpeg", "-v", "error", "-y", *cut, "-i", str(args.src), *cut, "-i", str(level), "-map", "0:v:0",
             "-map", "1:a", "-vf", "fps=30,scale=1080:1920,setsar=1", "-af", f"{fades},pan=stereo|c0=c0|c1=c0",
             "-c:v", "libx264", "-crf", "18", "-preset", "medium", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a",
             "192k", "-movflags", "+faststart", str(args.dst)])
    print(f"cleaned: {args.dst}  ({loudness(args.dst):.1f} LUFS)")


if __name__ == "__main__":
    main()
