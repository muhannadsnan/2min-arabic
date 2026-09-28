#!/usr/bin/env python3
"""Female voice from the owner's recording, with his exact consonants (runs in the TTS environment).

    hybrid_voice.py original.wav converted.wav out.wav [--pitch 1.1225]

converted.wav = the Chatterbox voice conversion of original.wav (Sara's timbre, but it softens unvoiced consonants,
e.g. خ → غ). This keeps the conversion for voiced sound and puts the ORIGINAL recording back wherever the original
has an unvoiced consonant (خ ش س ف ت ك ح ث ص ه…): noisy, energetic, high-frequency, no pitch. Those sounds carry no
gender, so the result keeps Sara's voice and the owner's pronunciation.
"""
import argparse
import subprocess
import tempfile

import librosa
import numpy as np
import soundfile as sf

SR = 24000
HOP = 120  # 5 ms


def align(orig, conv):
    """Shift conv so its energy envelope lines up with orig (VC can be offset by a few ms)."""
    e1 = librosa.feature.rms(y=orig, hop_length=HOP)[0]
    e2 = librosa.feature.rms(y=conv, hop_length=HOP)[0]
    n = min(len(e1), len(e2))
    best, lag_best = -1, 0
    for lag in range(-8, 9):
        a = e1[max(0, lag):n + min(0, lag)]
        b = e2[max(0, -lag):n - max(0, lag)]
        c = np.corrcoef(a, b)[0, 1]
        if c > best:
            best, lag_best = c, lag
    shift = lag_best * HOP
    conv = np.roll(conv, shift)
    return conv, lag_best * HOP / SR


def consonant_mask(y):
    """1 where the original has an unvoiced consonant: high-frequency noise, some energy, no pitch."""
    f0, voiced, vprob = librosa.pyin(y, fmin=70, fmax=400, sr=SR, hop_length=HOP, frame_length=1024)
    spec = np.abs(librosa.stft(y, n_fft=512, hop_length=HOP))
    freqs = librosa.fft_frequencies(sr=SR, n_fft=512)
    hf = spec[freqs >= 1500].sum(0) / (spec.sum(0) + 1e-9)   # خ has most energy 1.5-4 kHz, ش/س higher
    rms = librosa.feature.rms(y=y, frame_length=512, hop_length=HOP)[0]
    n = min(len(vprob), len(hf), len(rms))
    loud = rms[:n] > 0.02 * rms.max()                       # consonants are quiet; silence is ~0
    m = ((vprob[:n] < 0.2) & (hf[:n] > 0.4) & loud).astype(float)   # calibrated on بخير / شكرا (line 09)
    # close tiny gaps, then soften the edges (10 ms fades) so there are no clicks
    m = np.convolve(m, np.ones(3) / 3, mode="same") > 0.34
    m = np.convolve(m.astype(float), np.hanning(5) / np.hanning(5).sum(), mode="same")
    return np.clip(m, 0, 1)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("original")
    ap.add_argument("converted")
    ap.add_argument("out")
    ap.add_argument("--pitch", type=float, default=1.1225, help="pitch factor applied to the converted voice")
    ap.add_argument("--report", action="store_true")
    a = ap.parse_args()
    orig, _ = librosa.load(a.original, sr=SR)
    conv, _ = librosa.load(a.converted, sr=SR)
    if a.pitch != 1.0:   # lift the converted voice (formants follow) — brighter, less deep
        with tempfile.NamedTemporaryFile(suffix=".wav") as t1, tempfile.NamedTemporaryFile(suffix=".wav") as t2:
            sf.write(t1.name, conv, SR)
            subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", t1.name, "-af", f"rubberband=pitch={a.pitch}",
                            t2.name], check=True)
            conv, _ = librosa.load(t2.name, sr=SR)
    n = min(len(orig), len(conv))
    orig, conv = orig[:n], conv[:n]
    conv, offset = align(orig, conv)
    m = consonant_mask(orig)
    mask = np.interp(np.arange(n), np.arange(len(m)) * HOP, m)
    # level-match the original consonants to the converted voice
    g = (np.sqrt(np.mean(conv ** 2)) + 1e-9) / (np.sqrt(np.mean(orig ** 2)) + 1e-9)
    out = conv * (1 - mask) + orig * g * mask
    out /= max(1.0, np.abs(out).max() / 0.95)
    sf.write(a.out, out, SR)
    if a.report:
        print(f"offset {offset*1000:.0f} ms, consonant time {mask.mean()*100:.0f}% of the line")


if __name__ == "__main__":
    main()
