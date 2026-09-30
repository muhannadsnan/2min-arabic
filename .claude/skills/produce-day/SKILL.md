---
name: produce-day
description: Produce one daily lesson video for the 2 Minute Arabic YouTube channel, end to end — script, recording sheet for the owner (and Koki), splitting the recording, English voice, images, assembly, every quality check, thumbnail, captions and the upload sheet. Use this whenever the user asks for "Day N", the next day/lesson/video, a new episode, redoing a day, or sends an Arabic recording for a day, even if they don't say "produce".
---

# Produce a daily video (2 Minute Arabic)

Repo: `/home/msn/Documents/Youtube channels/2min-arabic`. The owner is a busy dad: he records the Arabic, watches
the finished video once and uploads it. Everything else is yours. The source of truth for the rules is
`docs/02-format.md`, `docs/04-curriculum-30-days.md`, `docs/05-style-guide.md`, `docs/06-publishing.md`,
`docs/10-production-flow.md` and `docs/11-monetization-policy.md` — read the parts you need; this skill is the
running order plus the traps we already fell into.

Python: `TTS=/media/msn/GamesLinux/AI/tts/venv/bin/python` for anything that needs Whisper/Chatterbox/DeepFilterNet
(`split_recording.py`, `final_check.py`); plain `python3` for the rest (`make_audio.py` calls the TTS venv itself).

## 1. Script — `videos/NNN-<slug>.md`

Copy the markup of the previous day (`say:<speaker>` blocks, `🎬 Scene`, `🖼️ Image`, `🔤 On screen`,
`⏸️ Pause`, `🎥 Clip: hello` / `🎥 Clip: goodbye`). Rules that matter:
- Length 2:00–2:40 when spoken (never over 2:59 — it's a Short). 5–8 new words, following the curriculum.
- Sukun on the last letter of every Arabic phrase. Arabic is only ever spoken by Arabic speakers
  (`teacher`, `teacher-slow`, `sami`, `lina`), never by the narrator.
- From Day 6 on: no English repetition after each Arabic line (the card shows the meaning).
- The line after the hello clip continues the thought (no second "welcome").
- "Subscribe so you don't break your streak." is its **own** narrator block — the subscribe animation starts there.
- Narrator lines are full sentences: one-word lines and exclamations ("Goodbye!") come out in a different register.
- Every lesson must feel different from the others (inauthentic-content policy, docs/11).

Then render the cards: `python3 tools/check_cards.py videos/NNN-….md` → look at `output/<video>/cards-sheet.png`.
Fonts lack `…`, `_` (Arabic font) and `→`, `▶` (bold Latin) — they show as □.

## 2. Recording sheets → WhatsApp

`python3 tools/recording_sheet.py videos/NNN-….md` → paste the owner's lines **in the chat as WhatsApp-ready text**
(numbered, Arabic with tashkeel, no markdown tables). Lina's lines go to Koki in a separate list — check first whether
`footage/recordings/_lina-koki/map.json` already has them (exact same text); only new ones need recording.
Remind: record in **iPhone Voice Memos** and send it as a **document** (WhatsApp voice notes are 7–9 kbps and smear
consonants), ~2 s between lines, a repeated line = the last take wins. Files land in
`footage/recordings/<video>/`.

## 3. Split the recording

```
$TTS tools/split_recording.py videos/NNN-….md                     # the owner's lines
python3 tools/merge_koki.py videos/NNN-….md                        # Koki's Lina lines into the day's map.json
```
Koki's own sheet is split with `--as-recorded --min-silence=0.5` (never voice-convert her). Read
`footage/recordings/<video>/report.md`: every line matched, CER low; listen-worthy lines flagged.

## 4. Voice — `python3 tools/make_audio.py videos/NNN-….md`

English narrator = the owner's clone (energetic Day 1 reference). The delivery check rejects flat, rushed,
stretched, gappy and pitch-drifting takes automatically; still read `audio/<video>/report.md` and redo flagged lines
with `--redo N,M --takes 8`. It stops if an Arabic line has no recording — fix the recording, don't reach for
`--allow-tts` (robotic Arabic TTS is why the owner records). If the voice setup changed, send the owner a 30 s
sample before building the whole video — his ear is the judge, and overstating checks has burned us before.

## 5. Images — ComfyUI + FLUX.2 klein

Start: `cd /media/msn/GamesLinux/AI/ComfyUI && venv/bin/python main.py --listen 127.0.0.1 --port 8188 --lowvram
--use-split-cross-attention` (background), then `python3 tools/images/batch.py images/<video>` (reads its `prompts.json`)
(`--only`, `--seed-offset` for redos). Follow the image QA rules in docs/05 (character refs in `assets/`, olive skin,
simple hands, no text). Reuse shots with `"same"`. Inspect every candidate sheet at full size, copy the chosen take to `sNN.png`, reasons in `picks.json`.
**Stop ComfyUI by its PID** when done (never `pkill -f` — it kills your own shell) and before the laptop sleeps.

## 6. Assemble + final check

```
python3 tools/assemble.py videos/NNN-….md
$TTS tools/final_check.py output/<video>/<video>.mp4
```
`final_check` must show: length ✅, −14 LUFS ✅, peak < −1 dB ✅, EN and AR transcripts in the right order with
0 overlaps. Open `check-frames.png` and `contact.png` and actually look: hello clip, YOUR TURN, subscribe
animation, goodbye; captions don't cover faces or cards.

## 7. Thumbnail, captions, description, upload sheet

- Thumbnail from one of the video's own images (the caption-free original in `images/`, not a frame with burned-in
  captions): `python3 tools/thumbnail.py images/<video>/sNN.png "output/<video>/thumbnail (vertical).jpg"
  --badge "DAY N" --line1 … --line2 … --arabic …` → check the `-phone-size.png`.
- `python3 tools/upload_captions.py videos/NNN-….md` → `output/<video>/captions-upload.srt`.
- `videos/NNN-description.txt` + `videos/NNN-upload.md` → follow the **upload-handover** skill.

## 8. Hand over

Run the **pre-upload-gate** skill first (SHIP / FIX / KILL); only a SHIP gets handed over.
Commit and push (recordings, audio, images, output are git-ignored; voice references are private and never
committed). Then hand over per the upload-handover skill with a short, honest report: what was checked, what was
redone and why, anything worth a listen. Update the memory notes if something new was learned.
