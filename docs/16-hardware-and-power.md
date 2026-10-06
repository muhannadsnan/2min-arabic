# 16 — Hardware, speed and power (reference)

Written 2026-10-06 after the Week 3 GPU session. Owner's decision stands: **no PC upgrades for now.** This page is
reference for when that changes. Numbers marked *estimate* are worked out from run times, not measured at the plug —
next GPU session, log `nvidia-smi --query-gpu=power.draw` to replace them with measured values.

## The laptop today

| Part | Value |
|---|---|
| Model | Lenovo IdeaPad Gaming 3 16IAH7 (82SA) |
| CPU | Intel Core i5-12500H (12 cores / 16 threads, 45 W base, up to 95 W) |
| GPU | RTX 3060 Laptop, **6 GB**, up to **105 W** |
| RAM | **16 GB** + 16 GB swap file on disk |

Models in use (all Apache 2.0): FLUX.2 klein 4B (pictures, 768×1344), Wan 2.2 TI2V-5B GGUF Q5_K_M (openers,
576×1024, 41 frames, 24 fps → built to 1080×1920 at 30 fps), Chatterbox (English voice), faster-whisper (checks).

## Time and power per video — now

| Step (per video) | Time |
|---|---|
| Opener clip | **5.4 min per clip** (Week 3 average of 16 clips: 324 s). ~3–4 clips per opener ≈ 20 min |
| — of which pure GPU sampling | 20 steps × 12 s = 4 min; the other ~1.4 min is loading, text encoding, decoding, swapping |
| Picture batch (~6 new scenes × 3 takes) | **~12 min** |
| English voice + retakes | ~10–15 min |
| Speech-to-text checks + captions | ~3–5 min |
| Assembly (CPU, ffmpeg) | ~3–5 min |
| **Total full-load time** | **~50–60 min per video** |

Power at full load ≈ 150–180 W at the wall (GPU ≤ 105 W + CPU 45–95 W + screen/board) *estimate*:
- **≈ 0.15 kWh per video** (≈ 0.2–0.4 NOK)
- **≈ 6–8 kWh per month** (~40 Shorts + Parts) ≈ 10–15 NOK.

Power cost is negligible; the real cost is the laptop being busy ~1 hour per video.

## With a better GPU *(estimates)*

| | RTX 3060 Laptop (now) | **RTX 5060 Laptop** | RTX 5060 desktop | **RTX 5060 Ti 16 GB** (desktop) |
|---|---|---|---|---|
| VRAM | 6 GB | 8 GB | 8 GB | **16 GB** |
| Power | ≤ 105 W | ~100–115 W | ~145 W | ~180 W |
| Opener clip | 5.4 min | ~3–3.5 min | ~2–2.5 min | ~1.5–2 min |
| Picture batch / video | ~12 min | **~7–8 min** | ~5–6 min | ~4–5 min |
| Full-load time / video | ~50–60 min | **~35 min** | ~25 min | ~20 min |
| Energy / video | ~0.15 kWh | **~0.10 kWh** | ~0.10 kWh | ~0.08 kWh |
| What it changes | — | speed | speed | **speed + quality** |

- Faster cards use **less** energy per video: more watts, but for much less time.
- **8 GB still can't run the bigger, better-looking models** (Wan 2.2 14B) or full 720p generation without heavy
  offloading. **16 GB (RTX 5060 Ti 16 GB) is the upgrade that changes quality, not just speed** — the best GPU upgrade
  for this channel. It is a desktop card (an eGPU dock for a laptop costs speed and money; a small desktop is the
  usual route).
- Licence rule still applies to any new model (docs/14): Apache-2.0-style, commercial use, no strings.

## RAM 16 → 32 GB — the biggest and cheapest win (with or without a new GPU)

**Why RAM is today's bottleneck:** the GPU has 6 GB, so ComfyUI keeps the rest of each model (Wan, its 4 GB text
encoder, FLUX, its text encoder) in normal RAM and moves pieces to the GPU as needed. With 16 GB, the system plus the
models don't fit, so Linux pushes data out to the swap file on disk (10–19 GB per clip with apps open; 3.9 GB was in
swap even at idle on 2026-10-06). Disk is ~50× slower than RAM. That is why every GPU session needs "close all apps".

**What 32 GB alone would change (same GPU):**

| | Now (16 GB) | With 32 GB *(estimate)* |
|---|---|---|
| Opener clip | 5.4 min | ~4.5–5 min (the 4-min GPU sampling stays; loading/swap overhead shrinks) |
| Picture batch | ~12 min | ~10 min (models stay cached between scenes) |
| Switching voice ↔ pictures ↔ video | models reload from disk | stay in RAM |
| Full-load time / video | ~50–60 min | **~45–50 min** |
| Using the laptop during a run (browser, WhatsApp, VS Code) | slows runs 2–3× → "close all apps" | **fine** |
| Random stalls / crashed runs from memory pressure | happen | mostly gone |

So: RAM alone gives a **modest speed-up (~10–20 %) but a big comfort and reliability gain** — no more "close
everything", runs you can leave going while you work. It does **not** fix GPU-memory limits (6 GB VRAM errors, model
size, resolution) — only a new GPU does that. With a new GPU later, 32 GB is still needed: offloaded model parts and
bigger models live in RAM.

**For this laptop:** DDR4-3200 SO-DIMM, 2 slots. Lenovo's spec sheet (PSREF) should be checked for the official
maximum; 2 × 16 GB is the usual upgrade. Buy a matched 2 × 16 GB kit (dual channel), ~400–700 NOK *estimate*.

## CPU and disk

- **CPU barely matters**: the heavy work runs on the GPU; the CPU does assembly and file handling. A faster CPU would
  save ~1–2 min per video. The i5-12500H is fine.
- **Disk**: models already load quickly from the NVMe drive. Small gain.

## Upgrade order (value for this channel)

1. **+16 GB RAM (32 GB total)** — cheapest; reliability, comfort, ~10–20 % faster.
2. **RTX 5060-class GPU (8 GB)** — ~2× faster (laptop ~35 min/video, desktop ~25 min).
3. **RTX 5060 Ti 16 GB** — the best GPU upgrade: speed **and** better-looking video (bigger models, higher resolution).
4. **CPU** — last; hardly any effect.
