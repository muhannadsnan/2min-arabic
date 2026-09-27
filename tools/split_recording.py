#!/usr/bin/env python3
"""Cut the owner's one-take Arabic recording into the video's lines (runs in the local TTS environment).

    /media/msn/GamesLinux/AI/tts/venv/bin/python tools/split_recording.py videos/003-first-conversation.md

Reads the newest audio/video file in footage/recordings/<video>/ and:
  1. cleans it: phone mics → centered mono, 80 Hz low-cut, DeepFilterNet noise removal, loudness −20 LUFS;
  2. splits it at the pauses (≥ 0.7 s of silence) and transcribes every piece (Whisper, Arabic);
  3. matches the pieces to the recording sheet's lines in order — joining neighbouring pieces when a line had an
     inner pause, and keeping the LAST good take when a line was repeated;
  4. converts Lina's lines to Sara's voice (Chatterbox VC, MIT), keeps everything else as recorded;
  5. writes lines/NN-<speaker>.wav + map.json (used by make_audio.py) + report.md.
"""
import json
import os
import pathlib
import re
import subprocess
import sys

import numpy as np
import soundfile as sf

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from recording_sheet import unique_lines  # noqa: E402
from tts_worker import cer  # noqa: E402

TTS_HOME = pathlib.Path(os.environ.get("TTS_HOME", "/media/msn/GamesLinux/AI/tts"))
SARA_VC = TTS_HOME / "refs" / "sara_ar_2.wav"   # best voice-conversion target in the 2026-09-27 test
AUDIO_EXT = {".m4a", ".mp3", ".wav", ".ogg", ".mov", ".mp4", ".aac", ".flac", ".opus", ".webm"}
SR = 48000


def run(cmd):
    subprocess.run(cmd, check=True)


def loudness(path):
    err = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", str(path), "-af", "ebur128", "-f", "null", "-"],
                         capture_output=True, text=True).stderr
    return float(re.search(r"I:\s+(-?[\d.]+) LUFS", err[err.rfind("Summary:"):]).group(1))


def clean(src, work):
    raw, dfn, out = work / "raw.wav", work / "dfn.wav", work / "clean.wav"
    channels = int(subprocess.run(["ffprobe", "-v", "error", "-select_streams", "a:0", "-show_entries",
                                   "stream=channels", "-of", "csv=p=0", str(src)], capture_output=True,
                                  text=True).stdout.strip() or 1)
    mix = "pan=mono|c0=0.5*c0+0.5*c1," if channels >= 2 else ""
    run(["ffmpeg", "-v", "error", "-y", "-i", str(src), "-map", "0:a:0", "-af", f"{mix}highpass=f=80",
         "-ac", "1", "-ar", str(SR), str(raw)])
    from df.enhance import enhance, init_df, load_audio, save_audio
    model, state, _ = init_df()
    audio, _ = load_audio(str(raw), sr=state.sr())
    save_audio(str(dfn), enhance(model, state, audio), state.sr())
    gain = -20.0 - loudness(dfn)
    run(["ffmpeg", "-v", "error", "-y", "-i", str(dfn), "-af", f"volume={gain:.2f}dB,alimiter=limit=0.8:level=false",
         "-ar", str(SR), str(out)])
    return out


def pieces(wav, min_silence=1.0, threshold_db=-55):   # after DeepFilterNet, real pauses sit near -80 dB
    """Speech pieces between pauses: [(start, end)] in seconds."""
    y, sr = sf.read(wav)
    hop = int(0.02 * sr)
    frames = len(y) // hop
    rms = np.array([np.sqrt(np.mean(y[i * hop:(i + 1) * hop] ** 2) + 1e-12) for i in range(frames)])
    voiced = 20 * np.log10(rms) > threshold_db
    out, start, quiet = [], None, 0
    for i, v in enumerate(voiced):
        if v:
            if start is None:
                start = i
            quiet = 0
        elif start is not None:
            quiet += 1
            if quiet * 0.02 >= min_silence:
                out.append((start * 0.02, (i - quiet + 1) * 0.02))
                start, quiet = None, 0
    if start is not None:
        out.append((start * 0.02, frames * 0.02))
    return [(s, e) for s, e in out if e - s >= 0.25]


def main():
    script = pathlib.Path(sys.argv[1])
    stem = script.stem
    root = HERE.parent
    rec_dir = root / "footage" / "recordings" / stem
    sources = sorted((p for p in rec_dir.iterdir() if p.suffix.lower() in AUDIO_EXT), key=lambda p: p.stat().st_mtime)
    if not sources:
        sys.exit(f"no recording in {rec_dir}")
    src = sources[-1]
    work = rec_dir / "work"
    lines_dir = rec_dir / "lines"
    work.mkdir(exist_ok=True)
    lines_dir.mkdir(exist_ok=True)
    print(f"recording: {src.name}")
    wav = clean(src, work)
    y, sr = sf.read(wav)
    segs = pieces(wav)
    print(f"{len(segs)} speech pieces found")

    from faster_whisper import WhisperModel
    asr = WhisperModel("medium", device="cuda", compute_type="float16")

    def hear(a, b):
        tmp = work / "piece.wav"
        sf.write(tmp, y[int(a * sr):int(b * sr)], sr)
        got, _ = asr.transcribe(str(tmp), language="ar", beam_size=5)  # no prompt: it gets echoed on unclear pieces
        return " ".join(g.text for g in got).strip()

    # candidate spans: single pieces and up to 3 joined neighbours (lines with an inner pause)
    spans = {}
    for i in range(len(segs)):
        for j in range(i, min(i + 3, len(segs))):
            spans[(i, j)] = hear(segs[i][0], segs[j][1])

    expected = unique_lines(script)
    K, P = len(expected), len(segs)
    score = {(k, span): cer(expected[k][1], heard) for k in range(K) for span, heard in spans.items()}
    # order-preserving alignment (dynamic programming): each line gets one span, spans in order, skipped pieces
    # (false starts, repeated takes) cost a little; among equal matches the LATER take wins (retakes).
    SKIP, MISSING = 0.08, 1.0
    # how well a span matches its best line — a piece that sounds like another line (e.g. a false start of the next
    # line) must not be taken as a position-only match
    best_line = {span: min(score[(k, span)] for k in range(K)) for span in spans}
    INF = float("inf")
    f = [[INF] * (P + 1) for _ in range(K + 1)]
    choice = [[None] * (P + 1) for _ in range(K + 1)]
    for p in range(P + 1):
        f[K][p] = 0.02 * (P - p)
    for k in range(K - 1, -1, -1):
        for p in range(P, -1, -1):
            best, pick = MISSING + f[k + 1][p], None
            for i in range(p, P):
                for j in range(i, min(i + 3, P)):
                    # joining pieces must clearly help (+0.12 each); an unreadable single piece in the right
                    # position still beats "missing" (score capped at 0.6 → flagged for review)
                    sc = score[(k, (i, j))]
                    if j == i and sc > 0.6:
                        sc = 0.6 + (0.3 if best_line[(i, j)] < 0.5 else 0.0)
                    c = SKIP * (i - p) + sc + 0.12 * (j - i) - 0.002 * i + f[k + 1][j + 1]
                    if c < best:
                        best, pick = c, (i, j)
            f[k][p], choice[k][p] = best, pick
    result, pos = [], 0
    for n, (speaker, text) in enumerate(expected, 1):
        pick = choice[n - 1][pos]
        if pick is None:
            result.append({"n": n, "speaker": speaker, "text": text, "file": None, "heard": "", "cer": 1.0})
            continue
        i, j = pick
        heard, sc = spans[(i, j)], score[(n - 1, (i, j))]
        a, b = max(segs[i][0] - 0.12, 0), min(segs[j][1] + 0.18, len(y) / sr)
        clip = y[int(a * sr):int(b * sr)].copy()
        fade = int(0.03 * sr)
        clip[:fade] *= np.linspace(0, 1, fade)
        clip[-fade:] *= np.linspace(1, 0, fade)
        out = lines_dir / f"{n:02d}-{speaker}.wav"
        sf.write(out, clip, sr)
        result.append({"n": n, "speaker": speaker, "text": text, "file": str(out.relative_to(root)),
                       "heard": heard, "cer": round(sc, 3), "start": round(a, 2), "end": round(b, 2)})
        pos = j + 1

    # Lina's lines → Sara's voice
    female = [r for r in result if r["speaker"] == "lina" and r["file"]]
    if female:
        import torchaudio as ta
        from chatterbox.vc import ChatterboxVC
        vc = ChatterboxVC.from_pretrained("cuda")
        for r in female:
            conv = root / r["file"].replace(".wav", "-sara.wav")
            ta.save(str(conv), vc.generate(str(root / r["file"]), target_voice_path=str(SARA_VC)), vc.sr)
            r["recorded"], r["file"] = r["file"], str(conv.relative_to(root))

    (rec_dir / "map.json").write_text(json.dumps(result, ensure_ascii=False, indent=1), encoding="utf-8")
    rows = "\n".join(f"| {r['n']:02d} | {r['speaker']} | {r['text']} | {r['heard']} | {r['cer']:.2f}"
                     f"{' ⚠️' if r['cer'] > 0.35 else ''} |" for r in result)
    (rec_dir / "report.md").write_text(f"# {stem} — recording split\n\nSource: `{src.name}` · {len(segs)} pieces\n\n"
                                       f"| # | Speaker | Line | Heard | CER |\n|---|---|---|---|---|\n{rows}\n",
                                       encoding="utf-8")
    bad = [r for r in result if r["cer"] > 0.35]   # includes lines matched by position only (listen to them)
    print(f"{len(result) - len(bad)}/{len(result)} lines matched" + (f" — check: {[r['n'] for r in bad]}" if bad else ""))


if __name__ == "__main__":
    main()
