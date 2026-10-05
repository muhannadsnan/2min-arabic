#!/usr/bin/env python3
"""Voice balance + narrator delivery check for one video (run with the TTS venv python — it uses librosa).

    $TTS tools/voice_balance.py videos/008-….md

Per voice group — narrator (owner's clone) · owner's recorded Arabic (teacher/teacher-slow/sami) · Koki (lina):
loudness (LUFS, as perceived) and clarity (energy above 2 kHz relative to the whole voice). Groups must sit within
±1.5 LU of the narrator; the owner's clarity within ±3 dB of the narrator's (Koki is naturally brighter), otherwise ⚠️. Then every narrator clip: words/s,
pitch movement and inner gaps (rushed > 3.6 w/s, flat < 6 st on lines of 5+ words, gap > 0.9 s).
"""
import json
import pathlib
import re
import subprocess
import sys

import librosa
import numpy as np

ROOT = pathlib.Path(__file__).resolve().parent.parent
GROUP = {"narrator": "narrator", "teacher": "owner", "teacher-slow": "owner", "sami": "owner", "lina": "koki"}


def lufs(path):
    out = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", str(path), "-af", "ebur128", "-f", "null", "-"],
                         capture_output=True, text=True).stderr
    m = re.search(r"I:\s+(-?[\d.]+) LUFS", out[out.rfind("Summary"):])
    return float(m.group(1)) if m else -70.0


def clarity(y, sr):
    """Share of energy above 2 kHz, on speech frames only (within 25 dB of the loudest frame)."""
    S = np.abs(librosa.stft(y, n_fft=2048, hop_length=512)) ** 2
    f = librosa.fft_frequencies(sr=sr, n_fft=2048)
    e = S.sum(axis=0)
    speech = e > e.max() * 10 ** (-25 / 10)
    S = S[:, speech]
    return 10 * np.log10(S[f > 2000].sum() / S.sum() + 1e-12)


_VE = {}


def voice_sim(y, sr):
    """Similarity of a narrator clip to the owner's English reference (Chatterbox voice encoder)."""
    import glob
    import torch
    from chatterbox.models.voice_encoder import VoiceEncoder
    if "ve" not in _VE:
        ve = VoiceEncoder()
        ve.load_state_dict(torch.load(glob.glob("/media/msn/GamesLinux/AI/tts/hf/hub/models--ResembleAI--chatterbox/snapshots/*/ve.pt")[0], map_location="cpu"))
        ve.eval(); _VE["ve"] = ve
        w, _ = librosa.load("/media/msn/GamesLinux/AI/tts/refs/owner_en_energetic.wav", sr=16000)
        _VE["ref"] = ve.embeds_from_wavs([w], sample_rate=16000, as_spk=True)
    w = librosa.resample(y, orig_sr=sr, target_sr=16000)
    e = _VE["ve"].embeds_from_wavs([w], sample_rate=16000, as_spk=True)
    return float(np.dot(_VE["ref"], e) / (np.linalg.norm(_VE["ref"]) * np.linalg.norm(e)))


def main():
    stem = pathlib.Path(sys.argv[1]).stem
    tl = json.loads((ROOT / "audio" / stem / "timeline.json").read_text(encoding="utf-8"))
    groups, problems = {}, []
    for c in tl["clips"]:
        g = GROUP.get(c["speaker"])
        if not g:
            continue
        path = ROOT / "audio" / stem / "clips" / c["file"] if not pathlib.Path(c["file"]).is_absolute() else pathlib.Path(c["file"])
        if not path.exists():
            path = ROOT / c["file"]
        y, sr = librosa.load(str(path), sr=24000, mono=True)
        groups.setdefault(g, []).append((lufs(path), clarity(y, sr)))
        if g == "narrator":
            words = len(c["text"].split())
            dur = len(y) / sr
            iv = librosa.effects.split(y, top_db=35)
            gaps = [(b[0] - a[1]) / sr for a, b in zip(iv, iv[1:])]
            f0, vf, _ = librosa.pyin(y, fmin=70, fmax=300, sr=sr)
            f0 = f0[vf] if vf is not None else np.array([])
            semis = 12 * np.log2(np.percentile(f0, 95) / np.percentile(f0, 5)) if len(f0) > 10 else 0
            notes = []
            if dur and words / dur > 3.6: notes.append(f"rushed {words / dur:.1f} w/s")
            if words >= 5 and semis < 6: notes.append(f"flat {semis:.1f} st")
            if gaps and max(gaps) > 0.9: notes.append(f"gap {max(gaps):.1f} s")
            sim = voice_sim(y, sr) if dur >= 2.6 else 1.0   # under ~2.5 s the voice embedding is unreliable
            if sim < 0.88: notes.append(f"voice/accent drift {sim:.2f}")
            print(f"{'⚠️ ' if notes else '✅ '}{c['n']:>3} {', '.join(notes) or 'ok':22} {c['text'][:70]}")
            if notes: problems.append(c["n"])
    print()
    ref = np.median([l for l, _ in groups["narrator"]])
    for g, vals in groups.items():
        L, C = np.median([v[0] for v in vals]), np.median([v[1] for v in vals])
        flag = "⚠️" if abs(L - ref) > 1.5 else "✅"
        print(f"{flag} {g:9} loudness {L:6.1f} LUFS ({L - ref:+.1f} vs narrator) · clarity {C:6.1f} dB · {len(vals)} clips")
    # the two male voices (owner + his clone) must sound alike; Koki is naturally ~5 dB brighter — leave her as is
    cl = [np.median([v[1] for v in groups[g]]) for g in ("narrator", "owner") if g in groups]
    if len(cl) == 2:
        print(("⚠️" if abs(cl[0] - cl[1]) > 3 else "✅") + f" owner vs narrator clarity {cl[1] - cl[0]:+.1f} dB (within ±3)")
    print("\nnarrator clips to redo:", ",".join(map(str, problems)) or "none")


if __name__ == "__main__":
    main()
