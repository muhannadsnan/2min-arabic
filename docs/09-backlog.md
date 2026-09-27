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
- [x] 🔔 Filmed and edited Day 1 (owner).
- [x] 🤖 Day 1 sound fixed (right channel → centered mono, 80 Hz low-cut, light compression, −14 LUFS, peaks −2.9 dB) and English captions made from the speech.
- [ ] 🔔 Skim the captions once (a few unclear words were cleaned up), then upload Day 1 with [videos/001-upload.md](../videos/001-upload.md).
- [ ] 🔔 Next time you film: turn the phone's stereo recording off or use one mic — the two built-in mics were 5 dB apart.

## Images
- [x] 🤖 Image model installed & tested: FLUX.2 [klein] 4B fp8 (Apache 2.0), ~15 s/image — `tools/images/generate.py`.
- [x] ~~Fix other ComfyUI custom nodes~~ — not needed (owner only uses the models Claude installed).
- [x] 🤖 Image QA rules defined ([05-style-guide.md](05-style-guide.md)); blank-dial fix verified (`audio-drafts/image-tests/klein_desk_fixed_blank_dial.png`).
- [ ] 🤖 Character sheets for Sami and Lina → reuse for consistency.
- [ ] 🤖 Batch-generate each video's scene images through the ComfyUI API.

## Video assembly
- [ ] 🤖 Text cards (Arabic + transliteration + English) as transparent PNGs — renderer tested ✅ (`audio-drafts/overlay-test.png`).
- [ ] 🤖 Auto-build a draft video / Shotcut project per day (voiceover + images at scene times + text cards + slow zoom + "your turn" labels).
- [ ] 🤖 Weekly 16:9 compilation in one command.

## Later
- [ ] 🤖 Days 6–30 scripts.
- [ ] 🤝 2 Minute Spanish rework (on hold — see that repo's README).
