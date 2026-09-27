# 09 — Backlog

What's next, in order. **🔔 = reminder for you**, 🤖 = Claude does it, 🤝 = together.

## Now — channel setup
- [x] 🤝 Channel setup, Steps 0–5 of [08-channel-setup.md](08-channel-setup.md) — done 2026-09-27.

## Voice
- [ ] 🔔 **Record your voice sample for cloning**: ~15–30 s, clear, natural talking pace, quiet room — once in **English**
      (for the narrator) and once in **Arabic** (for the teacher voice). Save as WAV/MP3 and give Claude the path.
- [ ] 🔔 Optional: a **female voice** for Lina — someone close to you records the same kind of sample (with their consent),
      or reads Lina's lines directly.
- [x] 🤖 Local TTS moved to `/media/msn/GamesLinux/AI/tts` (12 GB: 6.5 GB PyTorch/CUDA engine, 4.8 GB models incl. 1.5 GB Whisper checker); old Chatterbox v2 removed; smoke-tested ✅
- [ ] 🤖 Switch `tools/make_audio.py` to: your recordings → Chatterbox (Arabic, tashkeel, default settings) → Kokoro/clone
      (English); loudness normalization; best-of-3 takes with a speech-to-text check. **Test end-to-end on Days 1–5.**
- [ ] 🤖 Recording sheet + auto-cut script for your phrase library.
- [ ] 🔔 Record the Arabic lines for Days 1–5 (one session).

## Day 1
- [x] 🤖 On-camera teleprompter script: [videos/001-on-camera-teleprompter.md](../videos/001-on-camera-teleprompter.md)
- [ ] 🔔 Film Day 1 (phone vertical, eye level, window light, 2–3 takes per part) → give Claude the folder path.

## Images
- [x] 🤖 Image model installed & tested: FLUX.2 [klein] 4B fp8 (Apache 2.0), ~15 s/image — `tools/images/generate.py`.
- [ ] 🤖 Optional: fix your other ComfyUI custom nodes (Impact-Pack, Crystools, VideoHelperSuite, LTXVideo) in the new ComfyUI venv — they don't load yet (image generation is unaffected).
- [ ] 🤖 Character sheets for Sami and Lina → reuse for consistency.
- [ ] 🤖 Batch-generate each video's scene images through the ComfyUI API.

## Video assembly
- [ ] 🤖 Text cards (Arabic + transliteration + English) as transparent PNGs — renderer tested ✅ (`audio-drafts/overlay-test.png`).
- [ ] 🤖 Auto-build a draft video / Shotcut project per day (voiceover + images at scene times + text cards + slow zoom + "your turn" labels).
- [ ] 🤖 Weekly 16:9 compilation in one command.

## Later
- [ ] 🤖 Days 6–30 scripts.
- [ ] 🤝 2 Minute Spanish rework (on hold — see that repo's README).
