# 09 — Backlog

What's next, in order. **🔔 = reminder for you**, 🤖 = Claude does it, 🤝 = together.

## Now — channel setup
- [ ] 🤝 Steps 2–5 of [08-channel-setup.md](08-channel-setup.md): photo, banner, description, upload defaults, audience "not made for kids".
- [ ] 🔔 Take the profile photo (see Step 2), send it to Claude → 🤖 banner.

## Voice
- [ ] 🔔 **Record your voice sample for cloning**: ~15–30 s, clear, natural talking pace, quiet room — once in **English**
      (for the narrator) and once in **Arabic** (for the teacher voice). Save as WAV/MP3 and give Claude the path.
- [ ] 🔔 Optional: a **female voice** for Lina — someone close to you records the same kind of sample (with their consent),
      or reads Lina's lines directly.
- [ ] 🤖 Move the local TTS setup (Chatterbox + Kokoro, ~13 GB) from the temporary folder to the games drive (needs your OK).
- [ ] 🤖 Switch `tools/make_audio.py` to: your recordings → Chatterbox (Arabic, tashkeel, default settings) → Kokoro/clone
      (English); loudness normalization; best-of-3 takes with a speech-to-text check. **Test end-to-end on Days 1–5.**
- [ ] 🤖 Recording sheet + auto-cut script for your phrase library.
- [ ] 🔔 Record the Arabic lines for Days 1–5 (one session).

## Day 1
- [ ] 🤖 Turn Day 1 into an on-camera teleprompter script (short spoken sentences, where the B-roll images go).
- [ ] 🔔 Film Day 1 (phone, eye level, window light, 2–3 takes).

## Images
- [ ] 🤖 Install a commercially-licensed image model into ComfyUI (e.g. FLUX.1 schnell GGUF, Apache 2.0) on the games drive (needs your OK).
- [ ] 🤖 Character sheets for Sami and Lina → reuse for consistency.
- [ ] 🤖 Batch-generate each video's scene images through the ComfyUI API.

## Video assembly
- [ ] 🤖 Text cards (Arabic + transliteration + English) as transparent PNGs — renderer tested ✅ (`audio-drafts/overlay-test.png`).
- [ ] 🤖 Auto-build a draft video / Shotcut project per day (voiceover + images at scene times + text cards + slow zoom + "your turn" labels).
- [ ] 🤖 Weekly 16:9 compilation in one command.

## Later
- [ ] 🤖 Days 6–30 scripts.
- [ ] 🤝 2 Minute Spanish rework (on hold — see that repo's README).
