# 10 — Production Flow (Claude produces, the owner approves)

From Day 2 on, a video is **fully generated** — no filming needed. The owner's job per video is to **watch it once
and upload it** (~10 minutes). Everything runs locally on the owner's PC, with free tools licensed for monetized use.

## Who does what

| Step | Who | Tool | Output |
|---|---|---|---|
| 1. Script | 🤖 Claude | curriculum ([04](04-curriculum-30-days.md)) + markup ([05](05-style-guide.md)) | `videos/NNN-*.md` |
| 2. Voice | 🤖 Claude | `tools/make_audio.py` → local TTS (below) | `voiceover.wav`, `timeline.md`, `captions.srt` |
| 3. Images | 🤖 Claude | ComfyUI + FLUX.2 klein 4B → `tools/images/generate.py` | one checked image per scene |
| 4. Text cards | 🤖 Claude | Pillow (Arabic shaping verified) | transparent PNG per Arabic line |
| 5. Assembly | 🤖 Claude | ffmpeg | `NNN-final.mp4` (1080×1920, captions burned in) |
| 6. Quality check | 🤖 Claude | contact sheets + speech-to-text + loudness meter | fixes before handing over |
| 7. Thumbnail + upload sheet | 🤖 Claude | real frame / best image + text | `thumbnail.jpg`, `videos/NNN-upload.md` |
| 8. Approve + upload | 👤 Owner | YouTube Studio | scheduled video |
| Weekly | 🤖 Claude | ffmpeg | 16:9 compilation of the week |

## The voices

All on **Chatterbox Multilingual v3** (MIT license — code and weights), running on the RTX 3060.

| Speaker | Voice | Language |
|---|---|---|
| `narrator` | **the owner's cloned voice** | English |
| `teacher`, `teacher-slow` | **the owner's cloned voice** | Arabic |
| `sami` | synthetic male (Kokoro `am_michael` reference — not a real person) | Arabic |
| `lina` | Chatterbox built-in female voice | Arabic |

- **The owner's voice sample:** `/media/msn/GamesLinux/AI/tts/refs/owner_en.wav` — 12 s cut from his Day 1 video
  (clean, loudness-fixed). **Private: never committed to git, never shared, used only for this channel.**
- Tested 2026-09-27: English came back word-perfect through speech-to-text, Arabic almost perfect
  (samples: `audio-drafts/voice-clone-tests/`).
- **Licensing:** the voice is the owner's own + an MIT-licensed model → no license issue for monetization.
  YouTube: cloning **your own** voice needs no "altered or synthetic content" label.
- Every line: **3 takes → speech-to-text check → keep the best**, then loudness-normalize (bad takes happen,
  e.g. "لا أسهم" instead of "لا أفهم").
- Optional upgrade: a 15-second **Arabic** sample from the owner for an even more natural Arabic accent.

## Assembly recipe (step 5)

1. Voiceover at 0:00; scene images placed at the scene times from `timeline.md`, each with a slow zoom (100 → 105%).
2. Text cards (Arabic with tashkeel · transliteration · English) over the image, in the upper area.
3. "🗣️ Your turn!" label during every ⏸️ pause.
4. Burned-in captions ([tools/captions/srt_to_burnin_ass.py](../tools/captions/srt_to_burnin_ass.py)) on the chest area,
   Arabic on its own line in Noto Naskh Arabic, yellow.
5. Brand: stopwatch icon + "DAY N" badge.
6. Export: H.264 CRF 18, 30 fps, AAC 192 kb/s, **−14 LUFS**, ≤ 2:59.

## Quality check before handing over (step 6)

- Every image passed the [image QA rules](05-style-guide.md) (no text/numbers, hands, faces, duplicates, crops, character match).
- Final audio re-transcribed: every line says what the script says.
- Loudness −14 LUFS ±1, peaks below −1 dB, length 1:45–2:20.
- Contact sheet of the finished video checked: captions readable, nothing covers faces or text cards.

## Build status

| Piece | Status |
|---|---|
| Local voices + owner clone | ✅ working (`/media/msn/GamesLinux/AI/tts/local_tts.py`) |
| `make_audio.py` on local voices, best-of-3, loudness | ⏳ to build (still has the old Azure engine) |
| Image generation + QA | ✅ working |
| Text cards | ✅ renderer proven; batch tool ⏳ |
| Assembly script | ⏳ to build |
| Burned-in captions | ✅ tool saved |
| Sound finishing for filmed videos | ✅ recipe in [03](03-production-pipeline.md) |

The ⏳ pieces are built and tested end-to-end on Day 2 before it's handed over.

## Things to keep in mind

- **Stay human (monetization):** fully generated template videos are exactly what YouTube's "inauthentic content" policy
  targets. The owner's real voice (cloned) and face help. **Recommended:** film one reusable 3–5 s clip of yourself
  (a wave + "Welcome to 2 Minute Arabic") and one goodbye clip ("مع السلامة!") once — Claude puts them in every video.
  Film a real video again now and then (e.g. every review day, Day 7/14/21/30).
- **Buffer:** keep 5–7 finished videos scheduled so a busy week never breaks the daily streak.
- **File names:** no `|` and no line breaks — use `day NN - title.mp4`.
- **Space:** the games drive holds the AI tools (~40 GB); keep ≥ 20 GB free there and on the root disk.
- **Weekly compilation** every Sunday — it's what earns the watch hours for monetization.
- **Spanish channel** is on hold (decisions saved in its repo's README).
