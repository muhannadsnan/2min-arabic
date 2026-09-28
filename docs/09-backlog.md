# 09 — Backlog

What's next, in order. **🔔 = reminder for you**, 🤖 = Claude does it, 🤝 = together.

## Now — channel setup
- [x] 🤝 Channel setup, Steps 0–5 of [08-channel-setup.md](08-channel-setup.md) — done 2026-09-27.

## Voice
- [x] 🤖 **Owner's voice cloned** from the Day 1 video (12 s reference, private, on the games drive) — English word-perfect,
      Arabic almost perfect in tests. Narrator + teacher now use it ([10-production-flow.md](10-production-flow.md)).
- [ ] 🔔 Optional: a 15 s **Arabic** voice sample for an even more natural Arabic accent.
- [ ] 🔔 Recommended: film a reusable 3–5 s **hello clip** and **goodbye clip** of yourself once (goes in every video).
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

## New flow (2026-09-27)
- [x] 🤖 Recording sheet + splitter + Sara voice conversion + make_audio integration — tested end-to-end.
- [ ] 🔔 Record the Day 3 sheet (`videos/003-recording-sheet.md`) → Claude re-produces Day 3.
- [x] 🤖 Day 3 content: plan exchange added (6 new words); Day 4: "هَلْ تُرِيدُ قَهْوَةْ؟"; sukun pass on Days 4–5.
- [ ] 🤖 Days 4–5: restructure to the current format (hello/goodbye clips, one image per scene) at production time.

## Reminders for the owner
- [ ] 🔔 **Next hello/bye (or any on-camera) recording:** use the **iPhone's built-in mic, Jabra disconnected**
      (Bluetooth = 16 kHz call quality). Back camera ~50–80 cm, chest up, quiet room with soft furnishings;
      upload the .mov via the cloud (no WhatsApp). Claude cleans it with `tools/clean_footage.py`.
- [ ] 🔔 **Before long GPU jobs:** charger plugged in + power mode Balanced/Performance (on battery + power-saver the GPU runs at
      ~1/3 speed and the battery drains in ~1 hour).

## Later
- [ ] 🤖 Days 6–30 scripts.
- [ ] 🤝 2 Minute Spanish rework (on hold — see that repo's README).
