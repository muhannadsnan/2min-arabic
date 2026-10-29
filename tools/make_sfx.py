#!/usr/bin/env python3
"""Our own sound effects (owner, 2026-10-28: "we need sound effects!"), synthesized here so there is no licence
question — like the subscribe click and the star chime. Idea from learning/notes/2026-10-28-danny-why-…: cartoons
feel alive through sound, not only motion.

    $TTS tools/make_sfx.py        → assets/sfx/{card,pop,whoosh,tick,tock,boing,sparkle}.wav (48 kHz mono)

assemble.py places them (see "sound effects" there): whoosh as the hook card leaves · card swoosh when a word card appears · pop as the YOUR TURN label appears ·
tick-tock through every ⏸️ pause · per-scene extras from prompts.json {"sfx": [[scene, "boing"], …]}.
"""
import pathlib
import wave

import numpy as np

RATE = 48000
OUT = pathlib.Path(__file__).resolve().parent.parent / "assets" / "sfx"


def save(name, sig, peak=0.5):
    sig = sig / np.max(np.abs(sig)) * peak
    fade = min(len(sig), 240)
    sig[-fade:] *= np.linspace(1, 0, fade)
    with wave.open(str(OUT / f"{name}.wav"), "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(RATE)
        w.writeframes((sig * 32767).astype(np.int16).tobytes())


def t_(sec):
    return np.arange(int(sec * RATE)) / RATE


def bandpass(x, centre, q=2.0):
    """Time-varying 2-pole band-pass (centre = array of Hz per sample)."""
    y = np.zeros_like(x); y1 = y2 = x1 = x2 = 0.0
    for i in range(len(x)):
        w0 = 2 * np.pi * centre[i] / RATE; al = np.sin(w0) / (2 * q); c = np.cos(w0)
        b0, a0, a1, a2 = al, 1 + al, -2 * c, 1 - al
        yi = (b0 * x[i] - b0 * x2 - a1 * y1 - a2 * y2) / a0
        x2, x1, y2, y1 = x1, x[i], y1, yi
        y[i] = yi
    return y


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    rnd = np.random.default_rng(7)
    # pop: a soft bubble — a sine sweeping up 520→1300 Hz, 70 ms (owner 28 Oct: "a bit higher")
    t = t_(0.09); f = 520 + 780 * (1 - np.exp(-t * 45))
    save("pop", np.sin(2 * np.pi * np.cumsum(f) / RATE) * np.exp(-t * 38) * np.minimum(1, t * 900), 0.45)
    # whoosh: band-passed noise, the band sweeping up and down, swelling in and out (0.45 s)
    t = t_(0.45); env = np.sin(np.pi * t / t[-1]) ** 1.6
    save("whoosh", bandpass(rnd.normal(0, 1, len(t)), 500 + 2200 * np.sin(np.pi * t / t[-1]) ** 2, 1.4) * env, 0.4)
    # card: an airy swoosh that settles (0.28 s), the band sweeping high → mid — a word card sliding into place
    # (owner picked it 28 Oct from 3 air sounds: swish / puff / swoosh-in)
    t = t_(0.28); env = np.sin(np.pi * t / t[-1]) ** 1.2 * np.exp(-t * 3)
    save("card", bandpass(np.random.default_rng(3).normal(0, 1, len(t)), 3800 - 2800 * (t / t[-1]) ** 0.7, 1.6) * env, 0.4)
    # tick / tock: a little wood block (two partials, 35 ms)
    for name, f0 in (("tick", 1900), ("tock", 1450)):
        t = t_(0.05)
        save(name, (np.sin(2 * np.pi * f0 * t) + 0.4 * np.sin(2 * np.pi * f0 * 2.7 * t)) * np.exp(-t * 140)
             + 0.15 * rnd.normal(0, 1, len(t)) * np.exp(-t * 400), 0.35)
    # boing: a cartoon spring for a funny twist — wobbling pitch around 230 Hz that settles (0.6 s)
    t = t_(0.6); f = 230 * (1 + 0.3 * np.exp(-t * 5) * np.sin(2 * np.pi * 13 * t)) * (1 + 0.15 * t)
    ph = 2 * np.pi * np.cumsum(f) / RATE
    save("boing", (np.sin(ph) + 0.3 * np.sin(2 * ph)) * np.exp(-t * 4.5) * np.minimum(1, t * 400), 0.4)
    # sparkle: a quick rising glitter of 5 bell notes (pentatonic) for an "aha" reveal (0.7 s)
    t = t_(0.7); sig = np.zeros_like(t)
    for k, fn in enumerate((1047, 1319, 1568, 2093, 2637)):
        s = int(k * 0.06 * RATE); tt = t[: len(t) - s]
        sig[s:] += np.sin(2 * np.pi * fn * tt) * np.exp(-tt * 7) * 0.6 ** (k * 0.3)
    save("sparkle", sig, 0.35)
    print("wrote", ", ".join(p.name for p in sorted(OUT.glob("*.wav"))))


if __name__ == "__main__":
    main()
