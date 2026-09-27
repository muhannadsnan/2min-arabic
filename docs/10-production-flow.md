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

## The Arabic voice = the owner's own recording (from Day 3, 2026-09-27)

All Arabic is **recorded by the owner** — human, native, clear. Only the English narration is generated (his clone).

1. `python3 tools/recording_sheet.py videos/NNN-….md` → `videos/NNN-recording-sheet.md`: every unique Arabic line in
   order, marked *you* / *you — slowly* / *Lina (becomes Sara)*.
2. The owner records the whole sheet **in one take** (≈ 2 s silence between lines; a repeated line = the last take is used)
   and drops the file into `footage/recordings/<video>/`.
3. `/media/msn/GamesLinux/AI/tts/venv/bin/python tools/split_recording.py videos/NNN-….md`:
   cleans (DeepFilterNet, −20 LUFS) → splits at pauses ≥ 1 s → transcribes each piece → **order-preserving alignment**
   to the sheet (false starts and retakes skipped, later take wins, unreadable pieces assigned by position and flagged)
   → **Lina's lines converted to Sara's voice** (Chatterbox VC, MIT; tested: 129 Hz → 212 Hz, words intact)
   → `lines/`, `map.json`, `report.md`.
4. `tools/make_audio.py` uses the recorded line for every Arabic `say:` block (it stops if one is missing —
   `--allow-tts` only on purpose). English narrator lines are generated as before.

Tested end-to-end on 2026-09-27 with a noisy fake recording containing a false start: all 14 lines cut correctly.

## The voices

All on **Chatterbox Multilingual v3** (MIT license — code and weights), running on the RTX 3060.

| Speaker | Voice | Language |
|---|---|---|
| `narrator` | **the owner's cloned voice** (English reference, from the Day 1 video) | English |
| `teacher`, `teacher-slow` | **the owner's cloned voice** (Arabic reference, from his self-presentation clip) | Arabic |
| `sami` and every male role | **the owner's cloned voice** (Arabic reference) | Arabic |
| `lina` and every female role | **Sara's cloned voice** (owner's sister, permission given 2026-09-27) | Arabic |

**AI label:** videos with Sara's cloned voice → answer **Yes** to YouTube's AI-use question (cloning someone else's
voice). Videos with only the owner's own voice → **No**. Later option: Sara records Lina's lines for real → **No**.

- **Voice samples** (`/media/msn/GamesLinux/AI/tts/refs/`): `owner_en.wav` (12 s, Day 1 video), `owner_ar.wav`
  (13 s, self-presentation clip, denoised), `sara_ar_1.wav` / `sara_ar_2.wav` (Sara's voice notes).
  **Private: never committed to git, never shared, used only for this channel.**
- Tested 2026-09-27: English came back word-perfect through speech-to-text, Arabic almost perfect
  (samples: `audio-drafts/voice-clone-tests/`).
- **Licensing:** the voice is the owner's own + an MIT-licensed model → no license issue for monetization.
  YouTube: cloning **your own** voice needs no "altered or synthetic content" label.
- Every line: **3 takes → speech-to-text check → keep the best**, then loudness-normalize (bad takes happen,
  e.g. "لا أسهم" instead of "لا أفهم").
- Optional upgrade: a 15-second **Arabic** sample from the owner for an even more natural Arabic accent.

## Filmed clips (reused in every video)

In `footage/clips/` (git-ignored), sound cleaned (centered mono, low-cut, light noise reduction, −14 LUFS):

| Clip | Length | Used for |
|---|---|---|
| `hello.mp4` — "مرحبا بكم في 2 Minute Arabic" | 2.8 s | first seconds of every video (real human opening) |
| `goodbye.mp4` — wave + "شكرا ومع السلامة" | 3.1 s | last seconds of every video |
| `self-presentation.mp4` — "السلام عليكم، اسمي مهند…" | 13.6 s | Arabic voice reference; "meet your teacher" moment; channel trailer/community post |

## Sound quality rules (learned on Day 2)

- **Voice references must be clean**: the clone copies room hiss. All references (owner EN/AR, Sara) are cleaned with
  **DeepFilterNet** (MIT/Apache, local, in the TTS environment); originals kept in `refs/original/`.
- **Every generated clip** also passes through DeepFilterNet after the best take is chosen → noise-free guarantee.
- **Every filmed recording** goes through `tools/clean_footage.py src.mov out.mp4 [--start --end]` (centered mono,
  DeepFilterNet, compression, −14 LUFS, 1080×1920/30 fps).
- **Subscribe animation in every video**: over the goodbye clip, or over the last 3 s if there is none.
- **No dragged endings**: the checker penalizes takes whose last word is > 1.1 s or that keep sounding > 0.35 s after
  the last word, and every clip is trimmed 0.22 s after its last word with a short fade.
- Arabic voices use cfg 0.5 (lower made endings drag); the 5% slowdown comes from tempo.
- After a filmed clip, the narration must continue the thought (no second "welcome").
- **Never use stock clips with watermarks** (e.g. iStock/Getty previews). The end-screen subscribe animation is our own:
  `tools/make_subscribe.py` → `assets/subscribe.mov` + `assets/click.wav`, laid over the goodbye clip by `assemble.py`.

## Assembly recipe (step 5)

1. Voiceover at 0:00; scene images placed at the scene times from `timeline.md`, each with a slow zoom (100 → 105%).
2. Text cards (Arabic with tashkeel · transliteration · English) over the image, in the upper area.
3. "🗣️ Your turn!" label during every ⏸️ pause.
4. Burned-in captions ([tools/captions/srt_to_burnin_ass.py](../tools/captions/srt_to_burnin_ass.py)) on the chest area,
   Arabic on its own line in Noto Naskh Arabic, yellow.
5. Brand: stopwatch icon + "DAY N" badge.
6. Export: H.264 CRF 18, 30 fps, AAC 192 kb/s, **−14 LUFS**, ≤ 2:59.

## Mandatory checks for every video

The owner only watches the finished video once. **Every stage below is done and passed by Claude, in this order,
before hand-over.** Nothing is skipped; a failed check is fixed and re-checked.

### Before generating (script stage)

1. **Script rules:** sukun on the last letter of every Arabic phrase; one image per short scene (≈ 5–10 s);
   Arabic words spoken only by Arabic voices (never by the English narrator); `🎥 hello` in the intro and
   `🎥 goodbye` at the end; the line after the hello continues the thought.
2. **Text cards rendered and inspected** (all scenes, one sheet): no missing glyphs (□), no jumbled Arabic, readable
   sizes; "NEW:" and "Your answer:" lines highlighted.
3. **Image prompts** follow the [image QA rules](05-style-guide.md): character references, olive skin, simple hand
   poses, no text/numbers, "fills the whole frame"; repeated shots use `"same"`.
4. **Upload sheet + `NNN-description.txt`** written (Arabic isolated with direction markers; AI label decided:
   Sara's voice → Yes, otherwise No).

### After generating (post-checks)

5. **Voice report** (`audio/<video>/report.md`): every line heard as written; flagged lines are redone
   (`--redo N --takes 8`) or verified in context (known checker spellings: عَفْوًا → "اف 1", مَا اسْمُكْ → "مسموك").
   **Tails:** no dragged last word / long fade-out (checker penalty + trim).
   **Extra words:** anything the voice adds after the script's last word is cut automatically (Day 3: "…his coffee. Aby").
6. **Images:** every take inspected at full size (zoom on hands, faces, edges); best take picked and the reasons written
   to `images/<video>/picks.json`; failed scenes redone with a better prompt / new seeds.
7. **Assembly** with `tools/assemble.py`.
8. **Finished-video check:**
   - full soundtrack re-transcribed with timings → correct order, **no overlaps**, nothing garbled;
   - **noise** measured (quiet gaps of voice clips ≈ silence; filmed clips cleaned) — no audible hiss;
   - loudness **−14 LUFS ±1**, peaks below −1 dB, length 1:45–2:20 (never over 2:59);
   - contact sheet + frames at the hello clip, a pause ("YOUR TURN"), and the goodbye/subscribe moment: captions
     readable, nothing covers faces or cards, every card correct.
9. **Thumbnail** made and checked at phone size.
10. **Hand-over** with a short report: what was checked, what was redone and why, anything the owner should listen to.

## Build status

| Piece | Status |
|---|---|
| Local voices + owner/Sara clones, DeepFilterNet cleaning | ✅ |
| `tools/make_audio.py` (best-of-N, speech-to-text check, tail trim, `--redo`, filmed clips) | ✅ |
| `tools/images/batch.py` (+ `generate.py`, retry, resume, `same`) | ✅ |
| `tools/assemble.py` (cards, badge, YOUR TURN, captions, clips, subscribe, −14 LUFS, contact sheet) | ✅ |
| `tools/clean_footage.py` (filmed recordings) · `tools/make_subscribe.py` | ✅ |
