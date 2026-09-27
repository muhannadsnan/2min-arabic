# 03 — Production Pipeline

From a script in `videos/` to a published video.

```
script (.md) ──► make_audio.py (your recordings + local TTS) ──► voiceover.wav + timeline.md + captions.srt ──┐
             └─► scene images (AI image generator) ─────────────────────────────────────────┼─► Shotcut ──► export ──► YouTube
                                                    music (optional, YouTube Audio Library) ─┘
```

---

## 1. Voice

### Decision (2026-09-27): your own voice + free local open-source TTS — no paid service

Azure/Edge voices were tested and **rejected**: the Arabic sounded robotic, and a robotic Arabic voice would destroy
the channel's credibility. Rule: **nothing on this channel may sound robotic.**

| Part of the video | Who speaks | Why |
|---|---|---|
| **Day 1** | **You, on camera** | The founder story must be a real person. |
| **Arabic lines** (teacher, Sami) | **Your own recordings** — a reusable phrase library | Native, 100% authentic, legally yours. Phrases repeat across the curriculum, so each line is recorded once and reused forever. |
| **English narration** | **Your cloned voice** (Chatterbox, from your own sample) — Kokoro `am_michael` until then | Sounds like the person viewers met in Day 1; cloning your **own** voice needs no AI disclosure on YouTube. |
| **Lina** (female) and any Arabic line not recorded yet | **Chatterbox v3** female voice | Stop-gap; a real female voice (someone close to you, with consent) is better. |

### The engines (both free, both licensed for commercial use, run on your RTX 3060)

| Engine | License | Used for | Settings chosen by ear |
|---|---|---|---|
| **Chatterbox Multilingual v3** (Resemble AI) | Code MIT, weights MIT | Arabic (and English with your clone) | **default** settings (exaggeration 0.5, cfg 0.5, temperature 0.8), **with tashkeel**. Female: built-in voice. Male: conditioned on Kokoro `am_michael` (synthetic, not a real person) until your own sample replaces it. |
| **Kokoro-82M** | Apache 2.0 | English narration (until your clone) | `am_michael` |

Notes:
- Chatterbox adds an **inaudible Perth watermark** marking the audio as AI-generated. It doesn't restrict use.
- Tashkeel **stays in the scripts**: by ear it sounded best for both voices.
- The test clips were **too quiet** → every clip gets loudness-normalized (≈ −16 LUFS per clip, final mix ≈ −14 LUFS).
- Chatterbox has no speed setting; `teacher-slow` is slowed with ffmpeg `atempo 0.8`.
- For each line, generate 2–3 takes and keep the best one automatically (speech-to-text check). This filters out the occasional bad take.
- Test files: `audio-drafts/tts-tests/` (your picks: `compare/cbv3-ar-female-default-tashkeel-all6.mp3` and
  `compare/cbv3-ar-male-michael-default-tashkeel-all6.mp3`).

### Your recordings — the phrase library

- Claude generates a numbered **recording sheet** with every Arabic line of the next videos (lines already in the library are skipped).
- You read it in **one session** (~10 min for a week of videos): phone or headset mic, quiet room, a 2-second pause between lines.
- A script cuts the recording at the pauses, names each clip by its line, normalizes the volume and stores it in the library.
- `make_audio.py` uses your recording whenever one exists for a line, and generates the line with Chatterbox otherwise.

### Where it's installed

`/media/msn/GamesLinux/AI/tts/` — `venv/` (Python 3.11, PyTorch + CUDA, 6.5 GB), `hf/` (models, 4.8 GB: Chatterbox v3,
Kokoro, Whisper-medium for the automatic take check), `local_tts.py` (the voice map), `refs/` (voice reference clips).
Models are found via `HF_HOME=/media/msn/GamesLinux/AI/tts/hf`. Speed on the RTX 3060: ~30 s to load, then 1–4 s per line.

### Status of the tool

`tools/make_audio.py` still contains the old Azure engine and is being **switched to the local engines + your recordings**
(see [09-backlog.md](09-backlog.md)). It keeps the same output (`voiceover.wav`, `timeline.md`, `captions.srt`, `clips/`),
and it gets tested end-to-end on all five videos before you use it.

## 2. Images

One image per scene; prompts are in each script under **🖼️ Image**.

- **Generated on your own PC with ComfyUI** (`/media/msn/GamesLinux/AI/ComfyUI`, RTX 3060 6 GB) using
  **FLUX.2 [klein] 4B (fp8)** — **Apache 2.0**, commercial use allowed
  ([model card](https://huggingface.co/black-forest-labs/FLUX.2-klein-4B)). ⚠️ Only the **4B** klein is Apache;
  **klein 9B and FLUX.1 dev are non-commercial — never use them.**
  - ~12–17 s per 768×1344 image, ~31 s with a reference image. 4 steps (6 steps for tricky scenes).
  - Built-in **reference-image editing**: feed a character image back in and the same face/hair/clothes carry over —
    this is how Sami and Lina stay consistent.
  - Alternative installed: **Z-Image Turbo** (Apache 2.0) — slower (45–70 s), no reference editing yet.
  - Tool: [tools/images/generate.py](../tools/images/generate.py) (stdlib only; appends the style suffix automatically;
    `--ref img.png` for references; `--seed`, `--steps`). Start ComfyUI first: `/media/msn/GamesLinux/AI/run_comfyui.sh`.
  - Prompt tips from the tests: say **"olive skin"** / "Arab" features explicitly (otherwise people come out generic),
    and say **"stopwatch"** plus "no numbers on the dial" (it tends to draw an alarm clock with wrong numerals).
  - Test images: `audio-drafts/image-tests/`.
- Every prompt ends with **`+ STYLE`** — replace it with the **shared style suffix** from the
  [style guide](05-style-guide.md#visual-style) (or save the suffix once as a template/style preset in your
  generator) so the whole channel looks consistent.
- **Never ask the image model to write Arabic text.** Image models garble Arabic letters. All text is added in Shotcut.
- Keep Sami and Lina consistent: generate a **character reference sheet** once (prompts in the style guide),
  then use image-to-image / IP-Adapter / "reference image" features for every scene they appear in.
- Generate at **1080×1920** (or any 9:16 size) and leave the **top ~15% and bottom ~25%** calm — that's where
  on-screen text and YouTube's buttons go.
- Name files by scene: `s01.png`, `s02.png`, `s04-1.png` … so they drop onto the timeline in order.

---

## 3. Editing in Shotcut

### One-time project template

1. **Settings → Video Mode → Vertical HD 30 fps** (1080×1920).
2. Install the fonts (system-wide, then restart Shotcut): **Noto Naskh Arabic** or **Amiri** for Arabic (full tashkeel
   support), **Poppins** or **Montserrat** for English. All free on Google Fonts.
3. Build Day 1 fully, then **File → Save As** `template.mlt` with: the stopwatch icon and "Day N" badge on the top
   video track, the text styles set up, the music track in place.
   Every next video: open the template, **Save As** the new day, swap the voiceover, images and texts.

### Per video

1. **Audio:** drag `voiceover.wav` onto an audio track at **0:00**. Everything is already in order with pauses —
   no clip-by-clip work.
2. **Markers (optional, handy):** open `timeline.md`, and add a marker at each **🎬 scene** time
   (Timeline menu → Markers) so you can snap images to them.
3. **Images:** drag the scene images onto video track V1 and trim each one to end where the next scene starts.
4. **Slow zoom ("Ken Burns"):** on each image add the **Size, Position & Rotate** filter with two keyframes
   (100% at start → ~105% at end). Copy/paste the filter between images.
5. **On-screen text — generated for you as transparent PNG cards** (Arabic shaped correctly right-to-left with harakat,
   transliteration, English; tested: `audio-drafts/overlay-test.png`). Drop each card on the track above the images.
   You never type Arabic in Shotcut. If you do want to type text yourself, the fallback is: add a **Text: Rich** filter on a transparent/color clip on the track above the images,
   and paste the 🔤 **On screen** text from the script. Layout: Arabic big (top), transliteration medium (italic),
   English small (bottom). Use **Text: Rich** for anything Arabic — it handles right-to-left and harakat.
   ⚠️ Check once, zoomed in, that the harakat (ـَ ـُ ـِ ـّ ـْ) render correctly with your font.
6. **Pauses:** during each ⏸️ pause, show a small "🗣️ Your turn!" label (part of the template) so viewers know to speak.
7. **Music (optional):** a quiet track from the YouTube Audio Library (free and safe for monetized videos) on a second
   audio track, **Gain/Volume filter ≈ −25 dB** so the voice stays clear.
8. **Loudness:** add the **Normalize: Two Pass** filter to the Output track (target ≈ −14 LUFS).

About subtitles: Shotcut can import `captions.srt` (Subtitles panel) and burn it in, but its burn-in can lose the
right-to-left order of Arabic lines. **Don't burn in Arabic subtitles** — use Text: Rich for Arabic, and upload
`captions.srt` to YouTube as a separate subtitle file instead (YouTube renders Arabic correctly).

---

### Sound finishing for on-camera videos (Claude does it)

Measured on Day 1: phone audio was −25 LUFS (too quiet) and the two phone mics were 5 dB apart (voice leaning to one side).
Recipe: take the cleaner channel as mono → 80 Hz high-pass → gentle compression (−22 dB, 2.5:1) → gain to **−14 LUFS**
(measure on mono and target −17, because mono copied to both channels reads +3 dB) → limiter → AAC 192 kb/s.
The video stream is copied untouched. Captions: Whisper word timestamps → cleaned English `.srt`.

## 4. Export (Shotcut → Export)

| Setting | Value |
|---|---|
| Preset | **YouTube** (H.264 + AAC) — resolution follows the project (1080×1920) |
| Frame rate | 30 fps |
| Length | ≤ 2:59 (Shorts eligible) |
| Loudness | ≈ −14 LUFS (Normalize filter above) |

**Weekly long-form version:** every 7 days, make a **16:9 (Settings → Video Mode → HD 1080p 30 fps)** project,
put the week's 7 vertical videos in a row over a branded background, export, upload as a normal video.
This matters for monetization — see [07-channel-and-monetization.md](07-channel-and-monetization.md#what-this-means-for-our-strategy).

---

## 5. Per-video checklist

- [ ] `make_audio.py` run; voiceover listened to once (TTS sometimes misreads — fix the tashkeel and re-run)
- [ ] Every scene has an image, placed at the times in `timeline.md`
- [ ] Every Arabic line is on screen with tashkeel + transliteration + English (Text: Rich)
- [ ] "Your turn" label shown during every ⏸️ pause
- [ ] Length between 1:45 and 2:20 (never over 2:59)
- [ ] Exported with the YouTube preset, 1080×1920
- [ ] Title, description, pinned comment copied from the script; `captions.srt` uploaded as subtitles
- [ ] Status updated in the README table
