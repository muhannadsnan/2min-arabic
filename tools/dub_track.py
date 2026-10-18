#!/usr/bin/env python3
"""Extra-language audio track for a finished video (owner, 2026-10-18): the English narrator is replaced by the same
cloned voice speaking the language; the owner's and Koki's Arabic, the filmed clips and the sounds stay.

    $TTS tools/dub_track.py dubs/<video>.json fr [--takes 3]
        → output/<video>/dub-<lang>.m4a (upload in Studio → Languages → Add audio) + dub-<lang>-preview.mp4

dubs/<video>.json: {"video": "<stem>", "<lang>": {"<narrator clip n>": "translated line", …}}. Each line is generated in
several takes; the take with the best speech-to-text match that fits the original slot (until the next clip) wins;
a take longer than the slot is sped up (max 1.18×), longer still = reported, shorten the line. Only Chatterbox
languages (free, MIT: fr, tr, es, hi, ms …). Indonesian = Indonesian text read by the Malay voice (same sounds,
owner 2026-10-18); Urdu viewers get the Hindi track in plain spoken Hindustani (no Persian: no free model).
"""
import argparse, json, pathlib, subprocess, sys, tempfile
import numpy as np, soundfile as sf
ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, "/media/msn/GamesLinux/AI/tts")
import local_tts  # noqa: E402
VOICE = {"id": "ms"}   # track language → Chatterbox voice language
TEMPO = {"id": 1.08}   # the Malay voice speaks slowly (x03 sample, 2026-10-18)

def run(*a): subprocess.run(a, check=True, capture_output=True)
def dur(p): return float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(p)], capture_output=True, text=True).stdout)

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("spec"); ap.add_argument("lang"); ap.add_argument("--takes", type=int, default=3)
    a = ap.parse_args()
    spec = json.loads(pathlib.Path(a.spec).read_text(encoding="utf-8")); stem = spec["video"]; lines = spec[a.lang]
    tl = json.loads((ROOT / "audio" / stem / "timeline.json").read_text()); clips = tl["clips"]
    cands = sorted(p for p in (ROOT / "output" / stem).glob("*.mp4") if "video-only" not in p.name and "preview" not in p.name)
    final = next((p for p in cands if "uploaded" in p.name), cands[0])   # the render that is on YouTube
    T = pathlib.Path(tempfile.mkdtemp())
    local_tts.SPEAKERS[f"narrator-{a.lang}"] = ("chatterbox", local_tts.OWNER_EN_ENERGETIC, dict(lang=VOICE.get(a.lang, a.lang), exaggeration=0.5, cfg_weight=0.5, tempo=TEMPO.get(a.lang, 0.95)))
    from faster_whisper import WhisperModel
    asr = WhisperModel("small", device="cpu", compute_type="int8")
    norm = lambda s: "".join(ch for ch in s.lower() if ch.isalnum())
    def cer(r, h):
        r, h = norm(r), norm(h); d = list(range(len(h) + 1))
        for i, x in enumerate(r, 1):
            p, d[0] = d[0], i
            for j, y in enumerate(h, 1): p, d[j] = d[j], min(d[j] + 1, d[j - 1] + 1, p + (x != y))
        return d[len(h)] / max(1, len(r))
    placed, report = [], []
    for i, c in enumerate(clips):
        if c["speaker"] != "narrator" or str(c["n"]) not in lines: continue
        text = lines[str(c["n"])]; slot = (clips[i + 1]["start"] if i + 1 < len(clips) else tl["duration"]) - c["start"] - 0.2
        best = None
        for k in range(a.takes):
            out = T / f"{c['n']}-{k}.wav"; local_tts.synthesize(text, f"narrator-{a.lang}", out, seed=k)
            heard = " ".join(s.text for s in asr.transcribe(str(out), language=a.lang)[0]); e = cer(text, heard); d = dur(out)
            score = e + max(0, d / slot - 1) * 0.5
            if best is None or score < best[0]: best = (score, out, d, e, heard)
        _, out, d, e, heard = best
        speed = max(1.0, d / slot)
        fit = T / f"{c['n']}-fit.wav"
        run("ffmpeg", "-y", "-i", str(out), "-af", f"atempo={min(speed, 1.18):.3f},loudnorm=I=-18:TP=-2", "-ar", "48000", "-ac", "1", str(fit))
        flag = "TOO LONG — shorten" if speed > 1.18 else ("sped up %.2f×" % speed if speed > 1.0 else "fits")
        report.append(f"{c['n']:>3} {d:5.2f}s / slot {slot:5.2f}s  CER {e:.2f}  {flag} | {text}")
        placed.append((c["start"], c["end"], fit))
    # full mix: the final video's audio with the English narration muted, the new lines on top
    base = T / "base.wav"; run("ffmpeg", "-y", "-i", str(final), "-vn", "-ac", "2", "-ar", "48000", str(base))
    y, sr = sf.read(base)
    for s, e, _ in placed:
        a0, a1 = int(s * sr), min(len(y), int((e + 0.08) * sr)); fade = int(0.02 * sr)
        y[a0:a1] = 0
    for s, _, f in placed:
        v, _ = sf.read(f); v = np.stack([v, v], axis=1) if v.ndim == 1 else v; a0 = int(s * sr)
        y[a0:a0 + len(v)] += v[: max(0, len(y) - a0)] * 0.92
    mixed = T / "mixed.wav"; sf.write(mixed, np.clip(y, -1, 1), sr)
    od = ROOT / "output" / stem; m4a = od / f"dub-{a.lang}.m4a"
    run("ffmpeg", "-y", "-i", str(mixed), "-af", "loudnorm=I=-14:TP=-1.5", "-c:a", "aac", "-b:a", "192k", "-ar", "48000", str(m4a))
    run("ffmpeg", "-y", "-i", str(final), "-i", str(m4a), "-map", "0:v", "-map", "1:a", "-c:v", "copy", "-c:a", "copy", "-shortest", str(od / f"dub-{a.lang}-preview.mp4"))
    print("\n".join(report)); print(f"→ {m4a}  ({dur(m4a):.1f}s, video {dur(final):.1f}s)")

if __name__ == "__main__":
    main()
