# 2 Minute Arabic

> **Two minutes a day. Your first Arabic conversation in 30 days.**

A YouTube channel that teaches beginner Arabic in daily ~2-minute lessons.
The whole idea is **consistency over intensity**: nobody is too busy for two minutes.

This repo holds everything needed to produce the channel: the concept, the fixed video format,
the 30-day curriculum, the production pipeline (free AI voice + AI images + free editor),
and the ready-to-produce video scripts.

---

## Repo map

| Path | What it is |
|---|---|
| [docs/01-channel-concept.md](docs/01-channel-concept.md) | Philosophy, the founder story, the 1% math, the promise, audience, tone |
| [docs/02-video-format.md](docs/02-video-format.md) | The fixed 2-minute structure, the standard intro/outro, the 5 lesson formats |
| [docs/03-production-pipeline.md](docs/03-production-pipeline.md) | Voice (your recordings + free local TTS), images on your PC, text cards, editing in Shotcut, export — step by step |
| [docs/04-curriculum-30-days.md](docs/04-curriculum-30-days.md) | Day 1 → Day 30 plan that delivers the "first conversation" promise |
| [docs/05-style-guide.md](docs/05-style-guide.md) | Script markup, Arabic conventions (MSA, tashkeel, transliteration), visual style, characters |
| [docs/06-publishing.md](docs/06-publishing.md) | Titles, descriptions, thumbnails, schedule, Shorts, playlists |
| [docs/07-channel-and-monetization.md](docs/07-channel-and-monetization.md) | Which account, one vs two channels, AdSense, YPP thresholds (incl. 2027 changes), staying monetizable |
| [docs/11-monetization-policy.md](docs/11-monetization-policy.md) | YouTube's monetization policies (inauthentic / reused content…) and how this channel complies |
| [docs/08-channel-setup.md](docs/08-channel-setup.md) | Creating the channel step by step: safety checks, name, photo/banner, description, settings, features |
| [docs/10-production-flow.md](docs/10-production-flow.md) | **How every video is produced from Day 2 on** — who does what, voices, assembly, quality check |
| [docs/09-backlog.md](docs/09-backlog.md) | What's next, in order — including reminders for you |
| [templates/video-template.md](templates/video-template.md) | Copy this to start a new video script |
| [videos/](videos/) | The video scripts, one `.md` per video |
| [tools/make_audio.py](tools/make_audio.py) | Turns a script into a finished voiceover + scene timeline + captions (being switched to local TTS) |

## Videos

| Day | Format | Script | Status |
|---|---|---|---|
| 1 | Intro / story — **you on camera** | [001-why-2-minutes.md](videos/001-why-2-minutes.md) · [teleprompter](videos/001-on-camera-teleprompter.md) · [upload sheet](videos/001-upload.md) | 🎬 Edited, sound fixed, captions ready → upload |
| 2 | Phrases — **fully generated** | [002-10-most-useful-phrases.md](videos/002-10-most-useful-phrases.md) · [upload sheet](videos/002-upload.md) | 🎬 Ready to upload (`output/002-…/`) |
| 3 | Conversation — owner-recorded Arabic | [003-first-conversation.md](videos/003-first-conversation.md) · [upload sheet](videos/003-upload.md) | 🎬 Ready to upload |
| 4 | Story — owner-recorded Arabic | [004-story-sami-and-the-coffee.md](videos/004-story-sami-and-the-coffee.md) · [upload sheet](videos/004-upload.md) | 🎬 Ready to upload |
| 5 | Grammar — owner-recorded Arabic | [005-grammar-no-is-in-arabic.md](videos/005-grammar-no-is-in-arabic.md) · [upload sheet](videos/005-upload.md) | 🎬 Ready to upload |
| 6–30 | — | see [curriculum](docs/04-curriculum-30-days.md) | 📋 Planned |

Status legend: 📋 Planned → ✍️ Script ready → 🎙️ Audio done → 🖼️ Images done → 🎬 Edited → ✅ Published

## Producing one video (short version)

1. Open the script in `videos/`.
2. Generate the audio: `python3 tools/make_audio.py videos/001-why-2-minutes.md`
   → `audio/001-why-2-minutes/voiceover.wav` (pauses already inserted), `timeline.md`, `captions.srt`.
3. Generate one image per scene from the **🖼️ Image** prompts.
4. In Shotcut: voiceover at 0:00, each scene's image at the time given in `timeline.md`,
   the **🔤 On screen** text with the Text: Rich filter.
5. Export vertical 1080×1920 (YouTube preset), upload with the title/description from the script, add `captions.srt`.

Full details: [docs/03-production-pipeline.md](docs/03-production-pipeline.md).

## Sister channel

**2 Minute Spanish** mirrors this exact methodology (same format, same docs structure, same tooling)
in its own repo: [github.com/muhannadsnan/2min-spanish](https://github.com/muhannadsnan/2min-spanish).
Why two channels and not one: [docs/07](docs/07-channel-and-monetization.md#3-one-combined-channel-or-two).
