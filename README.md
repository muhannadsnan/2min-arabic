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
| [docs/03-production-pipeline.md](docs/03-production-pipeline.md) | Voice (free TTS), images, editing, export specs — step by step |
| [docs/04-curriculum-30-days.md](docs/04-curriculum-30-days.md) | Day 1 → Day 30 plan that delivers the "first conversation" promise |
| [docs/05-style-guide.md](docs/05-style-guide.md) | Script markup, Arabic conventions (MSA, tashkeel, transliteration), visual style, characters |
| [docs/06-publishing.md](docs/06-publishing.md) | Titles, descriptions, thumbnails, schedule, Shorts, playlists |
| [templates/video-template.md](templates/video-template.md) | Copy this to start a new video script |
| [videos/](videos/) | The video scripts, one `.md` per video |
| [tools/make_audio.py](tools/make_audio.py) | Turns a script into numbered MP3 clips with free Edge TTS voices |

## Videos

| Day | Format | Script | Status |
|---|---|---|---|
| 1 | Intro / story | [001-why-2-minutes.md](videos/001-why-2-minutes.md) | ✍️ Script ready |
| 2 | Phrases | [002-10-most-useful-phrases.md](videos/002-10-most-useful-phrases.md) | ✍️ Script ready |
| 3 | Conversation | [003-first-conversation.md](videos/003-first-conversation.md) | ✍️ Script ready |
| 4 | Story | [004-story-sami-and-the-coffee.md](videos/004-story-sami-and-the-coffee.md) | ✍️ Script ready |
| 5 | Grammar | [005-grammar-no-is-in-arabic.md](videos/005-grammar-no-is-in-arabic.md) | ✍️ Script ready |
| 6–30 | — | see [curriculum](docs/04-curriculum-30-days.md) | 📋 Planned |

Status legend: 📋 Planned → ✍️ Script ready → 🎙️ Audio done → 🖼️ Images done → 🎬 Edited → ✅ Published

## Producing one video (short version)

1. Open the script in `videos/`.
2. Generate the audio: `python tools/make_audio.py videos/001-why-2-minutes.md`
   (or paste each `say:` block into your TTS service by hand).
3. Generate one image per scene from the **🖼️ Image** prompts.
4. In the editor: lay the clips in order, put each scene's image under its clips,
   add the **🔤 On screen** text, and insert the **⏸️ Pause** gaps.
5. Export vertical 1080×1920, upload with the title/description from the script header.

Full details: [docs/03-production-pipeline.md](docs/03-production-pipeline.md).

## Sister channel

**2 Minute Spanish** will mirror this exact methodology (same format, same docs structure, same tooling)
in its own repo: `github.com/muhannadsnan/2min-spanish`.
