#!/usr/bin/env python3
"""Final check of a finished video — run in the TTS environment (it has Whisper):

    /media/msn/GamesLinux/AI/tts/venv/bin/python tools/final_check.py output/<video>/<video>.mp4 [--frames 6.5,36,110]

Prints: length, loudness (target −14 LUFS), peak, a full transcript in English AND Arabic with overlap counts
(overlapping speech = a timing bug), and writes <video-folder>/check-frames.png with frames at the given times
(default: hello clip, first pause, subscribe moment, goodbye — read from audio/<video>/timeline.json when present).
"""
import argparse
import json
import os
import pathlib
import re
import subprocess
import sys

TTS_HOME = pathlib.Path(os.environ.get("TTS_HOME", "/media/msn/GamesLinux/AI/tts"))
ROOT = pathlib.Path(__file__).resolve().parent.parent


def ensure_cuda_libs():
    libs = sorted(str(p) for p in (TTS_HOME / "venv").glob("lib/python3*/site-packages/nvidia/*/lib"))
    if libs and not set(libs) <= set(os.environ.get("LD_LIBRARY_PATH", "").split(":")):
        os.environ["LD_LIBRARY_PATH"] = ":".join(libs + [os.environ.get("LD_LIBRARY_PATH", "")])
        os.execv(sys.executable, [sys.executable] + sys.argv)


def main():
    ensure_cuda_libs()
    ap = argparse.ArgumentParser()
    ap.add_argument("video", type=pathlib.Path)
    ap.add_argument("--frames", default="")
    a = ap.parse_args()
    v = a.video
    dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(v)],
                               capture_output=True, text=True).stdout)
    err = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", str(v), "-af", "ebur128=peak=true", "-f", "null",
                          "-"], capture_output=True, text=True).stderr
    summ = err[err.rfind("Summary:"):]
    lufs = float(re.search(r"I:\s+(-?[\d.]+) LUFS", summ).group(1))
    peak = float(re.search(r"Peak:\s+(-?[\d.]+) dBFS", summ).group(1))
    ok = lambda c: "✅" if c else "❌"
    print(f"length {int(dur // 60)}:{dur % 60:04.1f} {ok(dur <= 179)}   loudness {lufs} LUFS {ok(abs(lufs + 14) <= 1)}   "
          f"peak {peak} dB {ok(peak < -1)}")
    wav = v.parent / "check-audio.wav"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(v), "-vn", "-ac", "1", "-ar", "16000", str(wav)], check=True)
    os.environ.setdefault("HF_HOME", str(TTS_HOME / "hf"))
    from faster_whisper import WhisperModel
    m = WhisperModel("medium", device="cuda", compute_type="float16")
    for lang in ("en", "ar"):
        segs = list(m.transcribe(str(wav), language=lang, word_timestamps=True, beam_size=5, vad_filter=True)[0])
        prev, ov = 0.0, 0
        for s in segs:
            ws = list(s.words)
            if ws and ws[0].start < prev - 0.05:
                ov += 1
            prev = s.end
        print(f"\n===== transcript {lang} — overlaps: {ov} {ok(ov == 0)}")
        print(" | ".join(f"[{s.start:5.1f}] {s.text.strip()}" for s in segs))
    wav.unlink()
    # frames at key moments
    times = [float(x) for x in a.frames.split(",") if x]
    tl_file = ROOT / "audio" / v.parent.name / "timeline.json"   # folder = script stem
    if not times and tl_file.exists():
        tl = json.loads(tl_file.read_text(encoding="utf-8"))
        vids = tl.get("videos", [])
        times = [vids[0]["start"] + 1.3] if vids else [2.0]
        if tl.get("pauses"):
            p = tl["pauses"][0]
            times.append((p["start"] + p["end"]) / 2)
        sub = next((c for c in tl["clips"] if "subscribe" in c["text"].lower()), None)
        if sub:
            times.append(sub["start"] + 2.5)
        times.append(dur - 1.2)
    if times:
        from PIL import Image
        tiles = []
        for k, t in enumerate(times):
            png = v.parent / f"check-frame{k}.png"
            subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{t:.2f}", "-i", str(v), "-frames:v", "1", "-vf",
                            "scale=-2:533", str(png)], check=True)
            tiles.append(Image.open(png))
        sheet = Image.new("RGB", (sum(t.width + 10 for t in tiles), 533), "white")
        x = 0
        for k, t in enumerate(tiles):
            sheet.paste(t, (x, 0))
            x += t.width + 10
            (v.parent / f"check-frame{k}.png").unlink()
        sheet.save(v.parent / "check-frames.png")
        print(f"\nframes at {', '.join(f'{t:.1f}s' for t in times)} → {v.parent / 'check-frames.png'} (look at it)")


if __name__ == "__main__":
    main()
