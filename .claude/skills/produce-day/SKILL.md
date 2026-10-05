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

## Never again — fixed problems (check BEFORE assembling, not after the owner watches)

Every item here cost a rebuild once. Apply them while writing the script and building the audio/images.

**Narration (English, owner's clone) — the narrator is the viewer's teacher, human and calm:**
- No rapid-fire lists ("Yes, no, sorry, okay."). Put lists inside a sentence: "…four little words: yes, no, sorry and okay."
- No short casual lines ("Keep that word in mind.") — the clone rushes them (> 3.6 words/s). Write fuller, calmer
  sentences ("Remember this word well, because you will need it again today.").
- No two short sentences in one line when the clone leaves a long gap between them (> 0.9 s) — join them with a comma
  or "so" ("Now imagine someone thanks you, so how do you say you're welcome?").
- No one-word lines or exclamations; no "Number one/two…" lists — use "Let's start with an easy one…", "Next…".
- A connector at every scene change: "And later that day…", "Then…", "Back at the café…".
- **Sounds are written the way they sound, never as a single letter:** "a soft ah", "an ee sound" — not "a soft a"
  (the clone glues a lone letter to the next word: "soft a sound" → "soft-a sound"; owner, 2026-10-05).
- **Accent:** the narrator is the owner's relaxed American accent. The take picker now scores each take's voice
  against his reference (Chatterbox voice encoder) and the audio gate flags "voice/accent drift" below 0.88 —
  redo those lines. Very short lines drift most ("Subscribe so you don't break your streak." scored lowest).
- **The approval preview includes the filmed hello/goodbye clips** (`tools/preview_audio.py`), otherwise their
  slots sound like silent gaps.
- Numbers and maths are hard to say: "one point zero one, seven times" stumbles — say it in words of meaning.
- Fix a flagged line by **rewording**, not just more takes.

**Pauses:** "Your turn" waits are **at most 2 s** (`make_audio.py` caps them); easy single words 1.5 s.

**Voices — the same level to the ear (owner approved Day 8's sound, 2026-10-02: keep this pattern):**
- Every clip is normalised to its target both ways (quiet clips raised, loud clips lowered): narrator −18 LUFS,
  Koki −18, owner's recorded lines −17 after the clarity EQ (`OWNER_CLARITY`, `OWNER_LIFT_DB = 1.0`).
- The **audio gate runs automatically** at the end of `make_audio.py` (`tools/voice_balance.py`): all ✅ and
  "narrator clips to redo: none" before assembling. Koki is naturally brighter — never EQ her.

**Pictures and cards:**
- Cards and the YOUR TURN label never cover a head or face → `"shift"` per scene (clips too); look at `contact.png`.
- Count hands on every person, including picture edges and the lower half (a floating hand slipped through on Day 6).
- Two-person scenes: give **both** character refs, or the model draws two Samis.
- Scene-1 card: one line, comma-separated, one style. Pauses fit the difficulty.

**Openers:** one simple, normal action (no exaggeration), arms back down, 1-s hold, then the scene picture;
one person per opener; the owner approves each one before use.

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

- **Scene 1's card** (today's subject): keep it to **one line**, items comma-separated ("Yes, No, Sorry, OK"); if it
  has more lines, assemble.py renders them all in the same style (bold, same size, same colour) — owner, 2026-10-02.
- **Pauses fit the difficulty:** very easy words (yes, no, a number) get ~1.5 s to repeat; phrases 3 s; full
  sentences in "Your turn" 4 s. Don't bore the viewer (owner, 2026-10-02).

- **The narrator is the viewer's teacher — human and natural, never robotic** (owner, 2026-10-02):
  - no rapid-fire lists ("Yes, no, sorry, okay."): put lists inside a sentence and join the last item with "and"
    ("So now you know four little words: yes, no, sorry and okay.");
  - every **scene change gets a connector** so the story flows: "And later that day…", "Then…", "Now…", "Back at the
    café…" — never jump into a new situation cold;
  - full, relaxed sentences; listen for rushed or flat delivery in the report and re-voice it.

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

**Owner's voice treatment (automatic, 2026-10-02):** `make_audio.py` gives the owner's recorded lines (teacher,
teacher-slow, sami) a clarity EQ (−2.5 dB at 250 Hz, +3.5 dB at 2.8 kHz, +4 dB shelf from 6 kHz) and +1 dB, because his
phone recordings sounded darker and quieter than Koki's. Koki's lines are left as they are.

**Audio gate — before building any video (owner, 2026-10-02):** after `make_audio.py`, run
`$TTS tools/voice_balance.py videos/NNN-….md`. It must show:
- narrator / owner / Koki loudness within ±1.5 LU of each other (same level to the ear);
- owner vs narrator clarity within ±3 dB (Koki is naturally brighter — leave her);
- "narrator clips to redo: none" (no rushed > 3.6 w/s, flat < 6 st, or gap > 0.9 s lines).
Fix flagged narrator lines by **rewording** into a calmer, fuller sentence (more takes alone rarely fixes a rushed
short line — the clone hurries short casual sentences), re-run, and only then assemble.

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
**Hands:** count hands per person and look at the *edges and the lower half* too — a stray floating hand next to
a knee slipped through on Day 6 (owner caught it). Every visible hand must belong to someone's arm.
**Stop ComfyUI by its PID** when done (never `pkill -f` — it kills your own shell) and before the laptop sleeps.

**3D look from Day 6 on** (owner, 2026-10-01 — costs the same as flat, animates far better): put `{"style": "3d"}` as
the first entry of prompts.json; batch.py then uses the 3D style and `assets/characters/<name>-3d.png`. Days 1–5 and
x01/x02 stay flat. Per-scene options: `"clip"` (a library unit), `"motion": "still" | "fade"` (photo-only scenes),
`"shift"` (move the picture down so the card never hides a face).

**Scroll-stopper (scene 1):** make a **new opener for this video**, themed to its lesson (animation-library skill),
**get the owner's approval**, then `{"s": 1, "clip": "openers/<name>"}`. Also make this video's own 3D backgrounds.
Ask the owner to close all apps for the GPU session.

## 6. Assemble + final check

```
python3 tools/assemble.py videos/NNN-….md
$TTS tools/final_check.py output/<video>/<video>.mp4
```
`final_check` must show: length ✅, −14 LUFS ✅, peak < −1 dB ✅, EN and AR transcripts in the right order with
0 overlaps. **Cards must never cover a head or face** (owner, 2026-10-02): in `contact.png`, every character's
hair-top must sit below the card; if not, add `"shift": 0.08–0.18` to that scene (clips too) and re-assemble.
Open `check-frames.png` and `contact.png` and actually look: hello clip, YOUR TURN, subscribe
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
