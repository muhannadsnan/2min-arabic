---
name: upload-handover
description: Write the upload sheet (videos/NNN-upload.md) and description file for a finished 2 Minute Arabic video and hand it to the owner — title, description with Arabic direction markers, tags, every YouTube Studio setting, subtitles, pinned comment, video elements. Use this whenever a video, Part or Extra is ready to upload, when the user asks for title/description/tags/settings, or asks "what do I paste", even if they don't mention the sheet.
---

# Upload hand-over

The owner uploads manually from his phone or PC and has little time. The sheet must be **self-contained**: he should
never have to open another file or think — just copy, paste, tick. Rules come from `docs/06-publishing.md`; the last
sheet in `videos/` (e.g. `005-upload.md`, `w01-upload.md`) is the template.

## File names (small SEO bonus, free)

Hand over the video and thumbnail under **keyword file names** (hard links next to the originals, nothing re-encoded):
`output/<video>/<search-phrase-slug>.mp4` and `<slug>-thumbnail.jpg`, e.g. `10-ways-to-say-hello-in-arabic-syrian-dialect.mp4`
— the main search phrase of the title, lowercase, hyphens. The sheet points at these names.

## Scheduling

Default: **the day after the channel's latest (scheduled) video, same time of day** — `fill <stem> <id> --publish-at next`
works it out from the channel (owner's rule, 2026-09-30). Only use a fixed time when the owner asks for one.

## The sheet — `videos/<stem>-upload.md`

1. **File to upload** (path) and whether it's a Short (vertical) or a normal video (16:9).
2. **Thumbnail:** "Upload file" → `output/<video>/thumbnail (vertical).jpg` (never "Select from video").
3. **Title** in a code box. Pattern `<benefit or curiosity> | Day N · 2 Minute Arabic` (Parts: `… | Part N · Days a–b`;
   Extras: `… | Arabic Extras`). Benefit part under ~50 characters. No hashtags in the title.
4. **Description** embedded in a code box (also saved as `videos/<stem>-description.txt`):
   - every Arabic phrase at the **end** of its line, wrapped in U+2067 … U+2069 (otherwise YouTube scrambles it);
   - transliteration — meaning — Arabic;
   - "Start from Day 1" link without `?si=…`; ~3 hashtags at the end (`#learnarabic` … `#2minutearabic`).
   Write it with Python so the invisible markers are really in the file, then print it once to verify.
5. **Tags** in a code box, 3-group formula: 3–4 video-specific · 3–4 niche · 3–4 broad. Keep the running
   "viral shorts" experiment in mind (Days 3/5 have it, 2/4 don't; check on 2026-10-06).
6. **Settings table:** playlist; not made for kids; **AI use** (No when only the owner's own voice clone + real
   recordings are used; Yes if anyone else's voice is cloned); paid promotion No; related video; Education / Concept
   overview; English; standard license; Shorts remixing allowed; visibility / schedule time.
7. **Subtitles:** Studio → Subtitles → Add language English → Upload file → With timing →
   `output/<video>/captions-upload.srt` → Publish.
8. **Video elements** for long videos (Parts): end screen, card, quiz — concrete values, not advice.
9. **Pinned comment** in a code box, with a tiny task in Arabic. Note: comments can't be pinned while a video is
   private/scheduled — pin it after it goes live.
10. **Quality check (Claude)** — short and truthful: measured numbers, what was redone, what to listen to.

## Hand-over

- Run the **pre-upload-gate** skill first: hand over only on SHIP (fix every FIX first; never hand over a KILL).
- Open the sheet for him: `code -r "videos/<stem>-upload.md"`, and give the link in the reply as well.
- **API fill (connected 2026-09-30):** the owner only drops the file in Studio and saves it as a draft/private. Then
  find its id (`$Y tools/youtube_api.py videos`) and run `fill <stem> <id> --publish-at next` — dry run first, then
  `--apply`. It sets title, description, tags, category, language, not-for-kids, AI label, thumbnail, captions and
  playlist. The sheet still lists the manual bits: Related video, pinned comment, Parts' end screen/cards/quiz.
- Uploads go **in day order** — if an earlier day isn't up yet, say so.
- Account-level reminders when relevant: automatic dubbing must stay OFF; a Short with ~0 views gets 48 h before
  any action (then check viewed-vs-swiped, re-upload with a new title if still ~0).
