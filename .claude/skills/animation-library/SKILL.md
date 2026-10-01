---
name: animation-library
description: Make, check and reuse the 3D animated units of 2 Minute Arabic — scroll-stopper openers (2-s entrances + seamless 5-s loops), green-screen talking characters composited on any background, 3D character references, and the monthly library refresh with rotation so videos don't repeat. Use this whenever the user mentions openers, scroll-stoppers, the first 2–3 seconds, animation, loops, green screen, talking characters, backgrounds, reusable clips/units, 3D, ComfyUI video, Wan, the monthly refresh, or when produce-day / arabic-extras needs scene 1's opener — even if they don't say "library".
---

# Animation library (3D units)

Why it exists: the first ~2 s decide "viewed vs swiped away", and moving 3D characters stop the scroll far better
than a still. Generating video is slow on the owner's laptop (RTX 3060 Laptop **6 GB**, 16 GB RAM, ~6 min per 2-s
clip), so we make **reusable units once a month or on demand** and rotate them across videos. Graphics only need to
be good, not impressive — no bigger models or PC upgrades (owner, 2026-10-01). Full test history: docs/14.

## Licence rule (hard)

Only models whose code **and** weights allow commercial use with no strings. Cleared: **Wan 2.2 TI2V-5B** (Apache
2.0; GGUF Q5_K_M by QuantStack; UMT5-XXL GGUF by city96; Wan 2.2 VAE), **FLUX.2 klein 4B** (Apache 2.0).
Rejected: LTX-Video / LTX-2 (forced in-video AI disclaimer, remote restriction), anything using **InsightFace**
(ReActor, LivePortrait, LatentSync — non-commercial), MuseTalk (non-commercial face parser). Check every new model
before downloading and write the result into docs/14. No AI label on our videos (owner's decision).

## Before a GPU session

Tell the owner to **close all apps** (Chrome, VS Code, WhatsApp): RAM, not the GPU, is the bottleneck; with apps open
the laptop swaps 10–19 GB per clip. Start ComfyUI (`--lowvram --use-split-cross-attention`), record the **python**
PID (`pgrep -f "main.py --listen"`), stop it by that PID at the end.

## Library layout — `library/` (videos git-ignored, `index.json` tracked)

| Folder | Unit | Used for |
|---|---|---|
| `openers/` | `<name>.mp4` (2-s entrance, plays once) + `<name>-loop.mp4` (5.2 s) | scene 1 of every Short |
| `talk/` | green-screen character talking calmly (no lip-sync), 6-s loop — prefer the `*-calm` units | narrator moments, intros, Part videos — on any background |
| `backgrounds/` | 3D stills (and later short animated ones) | behind talk units, still scenes |
| `work/` | keyframes, raw clips, takes | not used directly |

**Owner's rules (2026-10-01):**
- **Every new video (Day, Extra, Part) gets its OWN new opener**, themed to its lesson (Day 6 yes/no → Sami nods and
  shakes his head; a story day → the story's first moment) — no repeated openers, so videos and Part compilations
  look different. ~20 min laptop time per opener (keyframe + 2 seeds + review), accepted.
- **The owner approves every new opener before it is used** (send the clip + its sheet, open it with `xdg-open`).
- **Waving (hello or goodbye):** a couple of waves, then the arm goes down — that's it (owner, 2026-10-01).
- **Model limits seen so far:** with two people, Wan 2.2 5B usually animates only ONE of them (Part 2: Sami waved,
  Lina only smiled) — prefer one-person openers, or prompt the second person's action first and check; a head
  **nod** is too small to see (5–15 px) — use arm actions (wave, thumbs-up, fist pump) instead.
- **Keep it normal, never exaggerated** (owner, 2026-10-01): seated people stay seated; prompt "stays seated, small calm
  natural movements, does not stand up, does not lean forward"; 49 frames and trim before the model adds extra moves.
- **Opener shape:** one simple action (e.g. a wave), the arm goes back down, the final pose holds **1 s**, then the
  scene's own picture continues (slow zoom). No repeated waving, no long freezes.
- **New backgrounds per video** (cheap: ~1 min each) — the talk units and stills sit on fresh scenes every time.
- Library units (talk loops, backgrounds) are reused with rotation; openers are archived after use.

`index.json` lists every unit: character, action, lengths, source, `used_in` (filled automatically by
`assemble.py`). **Rotation:** for a new video pick the unit of the right character with the fewest / oldest
`used_in`; never the same opener on two videos in a row. Target 6–10 openers, extend over time.

## Making a unit

1. **Keyframe (3D still)** — `python3 tools/images/generate.py "<prompt>" out.png --style 3d --ref assets/characters/<name>-3d.png`
   (3 takes, seeds 900+k). Start **mid-action** so the motion completes it (half-hidden behind a wall, looking down at a
   notebook). Green-screen units: "… on a perfectly flat solid chroma-key green background (pure #00B140), evenly lit,
   no shadow, no floor, no props". Check at full size: face, hands (5 fingers), no text/signs.
2. **Animate** — `python3 tools/animate/animate.py key.png raw.mp4 --look 3d --width 576 --height 1024 --frames 61 --fps 24 --steps 20 --seed N --prompt "<gentle motion>"`
   (61 frames ≈ 20 real frames per second once stretched to 3 s — smoother than 49; 73 frames drift).
   Two seeds per unit, pick the clean one. **49 frames (2 s) is the sweet spot**: 73 frames drift in the last second
   (creepy faces). Gentle words only ("smiles, waves, looks up"); never "leans into the camera", "zooms", fast moves.
   Avoid revealing a hidden mouth/face (the model invents it: painted moustaches).
3. **Check every frame** (6-frame sheet + close-ups of face and hands). Reject: face drift, eyes changing, extra
   fingers, melting hands, sudden zoom, colour blobs. Ask: "would a viewer find this odd?" — if yes, reject.
4. **Build** — `python3 tools/animate/make_loop.py raw.mp4 openers/<name> --character sami --action "…" --speed 0.667 [--tail 0.8] [--green]`
   → `<name>.mp4` (the 2-s clip stretched to **3 s** with motion-compensated in-between frames — no extra GPU time),
   `<name>-loop.mp4` (**6-s pendulum**: start → end → start, slowing gently into each turn — no frozen frames; first
   and last frame identical, so it repeats seamlessly), `<name>-tail.mp4` (end pose ↔ a little back, eased: plays
   after an entrance so the character keeps moving instead of freezing), sheet, `index.json` entry.
   Owner's rules (2026-10-01): **no freezes**; **calm, neutral gestures** for anything that loops (big arm swings
   reveal the loop); entrances may be lively. Fast motion (a quick arm raise) shows 2–3 frames of smear after the
   in-betweening — reads as motion blur, but check it.
5. **Green-screen units** — `python3 tools/animate/composite.py library/talk/<name>-loop.mp4 <background> out.mp4 --seconds N [--zoom]`
   (green-dominance key: only clearly bright-green pixels go transparent, so Sami's **olive** hoodie survives — a
   chroma-distance key made it see-through; green fringe pulled down). Look at hair edges and clothes; lower
   `--dominance` (default 1.3) if green remains, raise it if the character gets holes.
6. **Longer actions** — chain 2-s parts: animate the next part from the last frame of the previous one, then check the
   join and the face across both parts (see docs/14 for the test result).

## Using units in a video (assemble.py, via images/<video>/prompts.json)

- `{"s": 1, "clip": "openers/<name>"}` — the opener once, its final pose held 1 s (`"hold"`), then the scene's
  own picture `sNN.png` with the slow zoom. `"clip_mode": "tail"` keeps the end moving instead (rarely wanted).
- `{"s": 4, "clip": "talk/…-on-cafe", "clip_mode": "loop"}` — repeats a loop for the whole scene.
- `{"s": 9, "motion": "still"}` / `"fade"` — a still picture with no zoom / with a slow fade in and out (photo-only
  scenes). Default is the slow zoom.
- From Day 6 on the whole video uses the 3D look: put `{"style": "3d"}` first in prompts.json (batch.py then uses the
  3D character references `assets/characters/<name>-3d.png`).

## Monthly refresh (calendar in CLAUDE.md)

Make 3–5 new openers (different entrances per character: peek, look-up, turn-around, walk-in, wave from a balcony …),
1–2 talk units, a few backgrounds. ~15 min laptop time per unit (2 seeds + review). Update docs/14 with what worked.

## Characters and variety

3D references: `assets/characters/{sami,lina,waiter}-3d.png` (the 3D waiter is deliberately different from Sami:
late fifties, grey hair, glasses, moustache, waistcoat, red apron). **Future:** give Sami and Lina several outfits and
styles (seasonal clothes, formal/casual) as extra keyframe sets, so talk units and openers don't look identical across
months — same face, different clothes.
