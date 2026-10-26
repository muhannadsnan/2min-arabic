#!/usr/bin/env python3
"""Find extra sounds (throat clearing, coughs, breaths, a stray word) in recorded lines — owner, 2026-10-26:
"don't you listen to the audio?". Each recorded clip a video uses is split at its pauses; every sound burst is
transcribed on its own and must belong to the expected text. Bursts that don't are reported (and optionally cut).

    $TTS tools/check_bursts.py videos/x07-inshallah-meaning.md [--fix]

--fix keeps only the bursts that match the text (with 40 ms fades), backing the original up as <file>-orig.wav.
"""
import json
import pathlib
import re
import subprocess
import sys
import unicodedata

ROOT = pathlib.Path(__file__).resolve().parent.parent


def letters(s):
    s = "".join(c for c in unicodedata.normalize("NFKD", s) if not unicodedata.combining(c))
    s = s.replace("أ", "ا").replace("إ", "ا").replace("آ", "ا").replace("ة", "ه").replace("ى", "ي")
    return re.sub(r"[^ء-ي]", "", s)


def bursts(path, noise=-38, gap=0.22):
    out = subprocess.run(["ffmpeg", "-i", str(path), "-af", f"silencedetect=noise={noise}dB:d={gap}", "-f", "null", "-"],
                         capture_output=True, text=True).stderr
    dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(path)],
                               capture_output=True, text=True).stdout)
    st = [float(x) for x in re.findall(r"silence_start: ([\d.]+)", out)]
    en = [float(x) for x in re.findall(r"silence_end: ([\d.]+)", out)]
    sil = sorted(zip(st, en + [dur] * (len(st) - len(en))))
    segs, t = [], 0.0
    for s, e in sil:
        if s - t > 0.06:
            segs.append((t, s))
        t = e
    if dur - t > 0.06:
        segs.append((t, dur))
    return segs, dur


def main():
    script = pathlib.Path(sys.argv[1]); fix = "--fix" in sys.argv
    rec = json.loads((ROOT / "footage/recordings" / script.stem / "map.json").read_text())
    from faster_whisper import WhisperModel
    m = WhisperModel("small", device="cpu", compute_type="int8")
    seen, bad = set(), 0
    for r in rec:
        f = ROOT / r["file"]
        if f in seen or "_placeholder" in str(f):
            continue
        seen.add(f)
        segs, dur = bursts(f)
        want = letters(r["text"])
        keep, extra = [], []
        for a, b in segs:
            tmp = pathlib.Path("/tmp/_burst.wav")
            subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(f), "-af", f"atrim={max(0, a - 0.05)}:{b + 0.05}", str(tmp)])
            heard = letters(" ".join(s.text for s in m.transcribe(str(tmp), language="ar", vad_filter=False)[0]))
            import difflib
            h2 = heard.replace("ء", "").replace("ه", "")
            w2 = want.replace("ء", "").replace("ه", "")
            best = max((difflib.SequenceMatcher(None, h2, w2[i:i + len(h2)]).ratio() for i in range(max(1, len(w2) - len(h2) + 1))), default=0)
            vol = subprocess.run(["ffmpeg", "-i", str(tmp), "-af", "volumedetect", "-f", "null", "-"], capture_output=True, text=True).stderr
            mx = float((re.findall(r"max_volume: ([-\d.]+)", vol) or ["-99"])[0])
            ok = mx < -30 and not h2 or (len(h2) >= 2 and best >= 0.5 and not re.search(r"(.)\1{3,}", heard))
            (keep if ok else extra).append((a, b, heard))
        if extra and keep:
            bad += 1
            print(f"⚠️  {r['speaker']:8} {r['text']}  [{f.name}]  extra: " +
                  ", ".join(f"{a:.2f}–{b:.2f}s '{h or '(no words)'}'" for a, b, h in extra))
            if fix:
                orig = f.with_name(f.stem + "-orig.wav")
                if not orig.exists():
                    f.rename(orig)
                a0, b0 = keep[0][0], keep[-1][1]
                subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(orig), "-af",
                                f"atrim={max(0, a0 - 0.08)}:{b0 + 0.12},asetpts=PTS-STARTPTS,afade=t=in:d=0.04,"
                                f"areverse,afade=t=in:d=0.06,areverse", str(f)], check=True)
                print(f"    → cut to {a0:.2f}–{b0:.2f}s (original kept as {orig.name})")
    print(f"{len(seen)} recorded clips checked, {bad} with extra sounds")


if __name__ == "__main__":
    main()
