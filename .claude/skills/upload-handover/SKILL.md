---
name: upload-handover
description: Write the upload sheet (videos/NNN-upload.md) and description file for a finished 2 Minute Arabic video and hand it to the owner — title, description with Arabic direction markers, tags, every YouTube Studio setting, subtitles, pinned comment, video elements. Use this whenever a video, Part or Extra is ready to upload, when the user asks for title/description/tags/settings, or asks "what do I paste", even if they don't mention the sheet.
---

# Upload hand-over

The owner uploads manually from his phone or PC and has little time. The sheet must be **self-contained**: he should
never have to open another file or think — just copy, paste, tick. Rules come from `docs/06-publishing.md`; the last
sheet in `videos/` (e.g. `005-upload.md`, `w01-upload.md`) is the template.

## File name (one final file, named after the title)

`assemble.py` writes the finished video **once**, named after the title's benefit part (from the script header's
"YouTube title" row): `output/<video>/10-ways-to-say-hello-in-arabic-5-in-syrian-dialect.mp4` — a small search bonus
and no duplicate copies (owner, 2026-10-01). The sheet points at that file. `final_check.py` takes that path.

## Scheduling

Default: **the day after the latest (scheduled) video of the same kind — Shorts and long videos (Parts) have separate daily chains — same time of day** — `fill <stem> <id> --publish-at next`
works it out from the channel (owner's rule, 2026-09-30). Only use a fixed time when the owner asks for one.

## The sheet — `videos/<stem>-upload.md`

1. **File to upload** (path) and whether it's a Short (vertical) or a normal video (16:9).
2. **Thumbnail:** "Upload file" → `output/<video>/thumbnail (vertical).jpg` (never "Select from video").
3. **Title** in a code box. Pattern `<benefit or curiosity> | Day N · 2 Minute Arabic` (Parts: `… | Part N · Days a–b`;
   Extras: `… | Arabic Extras`). Benefit part under ~50 characters. No hashtags in the title.
4. **Description** embedded in a code box (also saved as `videos/<stem>-description.txt`):
   - **no flag emojis** (🇸🇾 renders the old Syrian flag; flags are political) — use 🗣️ / 📍 for regions;
   - every Arabic phrase at the **end** of its line, wrapped in U+2067 … U+2069 (otherwise YouTube scrambles it);
   - transliteration — meaning — Arabic;
   - "Start from Day 1" link without `?si=…`; ~3 hashtags at the end (`#learnarabic` … `#2minutearabic`).
   Write it with Python so the invisible markers are really in the file, then print it once to verify.
5. **Tags** in a code box, 18–26 tags, ≤ 480 characters, in this order (owner, 2026-10-02/05):
   - 3 **search phrases** people really type, specific to this video ("how to say sorry in arabic", "arabic
     conversation for beginners") — real terms from channel-review's search-terms report win;
   - 3 **question-form / synonym searches** in the owner's style (2026-10-05): "what is greeting in arabic",
     "welcome in arabic", "sorry in arabic", "how to talk to arabic people", "ways to say hello in arabic";
   - 2–4 **transliterated keywords** of today's words ("shukran", "ma ismuk", "tayyib") — learners search these;
   - **Research first:** `python3 tools/suggest.py "<topic> in arabic" "<Arabic topic>"` = YouTube's own
     autocomplete (what people really type, most-searched first). Pick learner phrases only (drop songs, kids,
     perfumes, games, everyday-life Arabic like "كيف تعتذر من شخص" — that's Arabic speakers, not learners);
   - 2 **learner Arabic** tags on every video: "تعليم اللغة العربية لغير الناطقين بها", "تعليم عربي للاجانب"
     (+ topic ones: "محادثة تعارف بالعربية", "قصة قصيرة بالعربي", "الاعتذار بالعربية" — owner, 2026-10-05);
   - 5–7 **Arabic-script** tags (owner, 2026-10-02): today's words in Arabic ("نعم", "طيب"), 2 **mixed** phrases a
     learner pastes in after seeing a word ("طيب meaning", "من أين أنت in english"), and one topic phrase
     ("تعلم اللغة العربية", "قصة قصيرة بالعربية");
   - niche ("learn arabic", "arabic for beginners", "modern standard arabic") · broad ("language learning", "shorts").
   Arabic script goes in tags, descriptions and the **thumbnail** (big word) — **not in titles** (it tells YouTube the
   video is for Arabic speakers and mixed-direction titles get scrambled); titles may use transliteration.
   Formerly: 3-group formula: 3–4 video-specific · 3–4 niche · 3–4 broad. Keep the running
   "viral shorts" experiment in mind (Days 3/5 have it, 2/4 don't; check on 2026-10-06).
6. **Settings table:** playlist; not made for kids; **AI use** (No when only the owner's own voice clone + real
   recordings are used; Yes if anyone else's voice is cloned); paid promotion No; related video; Education / Concept
   overview; English; standard license; Shorts remixing allowed; visibility / schedule time.
7. **Subtitles:** Studio → Subtitles → Add language English → Upload file → With timing →
   `output/<video>/captions-upload.srt` → Publish.
8. **Video elements** for long videos (Parts): end screen, card, quiz — concrete values, not advice.
9. **Pinned comment** in a code box, with a tiny task in Arabic. The hourly cron job (`tools/comment_job.sh`) posts it
   as the channel once the video is live (it matches the sheet by title) and notifies the owner to tap ⋮ → Pin.
10. **Quality check (Claude)** — short and truthful: measured numbers, what was redone, what to listen to.

## Hand-over

- Run the **pre-upload-gate** skill first: hand over only on SHIP (fix every FIX first; never hand over a KILL).
- Open the sheet for him: `code -r "videos/<stem>-upload.md"`, and give the link in the reply as well.
- **API fill (connected 2026-09-30):** the owner only drops the file in Studio and saves it as a draft/private. Then
  find its id (`$Y tools/youtube_api.py videos`) and run `fill <stem> <id> --publish-at next` — dry run first, then
  `--apply`. It sets title, description, tags, category, language, not-for-kids, AI label, thumbnail, captions and
  playlist. The sheet still lists the manual bits: Related video, pinned comment, Parts' end screen/cards/quiz.
- **Not settable by the API — always list them as the owner's Studio checklist** (owner, 2026-10-02):
  Education → Type **Concept overview**, Level **Beginner** (Academic system: leave empty) ·
  Automatic chapters **on**, Automatic places **off**, Automatic concepts **off**. Ask once that the owner sets them in
  Studio → Settings → **Upload defaults** (whichever are offered there), so they're right for every upload.
- **After every fill, end the reply with the owner's Studio checklist** (the tool prints it):
  Type Concept overview · Level Beginner · Automatic places/concepts off — every time, never assume it's done.
- After `fill`, run `$Y tools/youtube_api.py audit` and fix every ⚠️; also audit the channel (title = sheet, isolates in the description, 10–14 tags, Education, English
  title/audio language, not for kids, English captions, custom thumbnail, playlist) — never just trust the call.
- **After it goes live (automatic):** the hourly job posts the pinned comment and pops one desktop notification per
  video: "Day N is live: pin the comment and set Related video = …" — Related video **can't be set before publishing**.
- **Playlist order after every fill/replacement:** 30-day playlist = Day 1 → … → Day 5 → Part 1 → Day 6 → … (a Part
  right after its 5th day), Extras playlist in x-order; remove "Deleted video"/"Private video" placeholders.
- **Problems field (Education):** leave empty — it's built for academic problem-solving (maths/physics); no
  evidence it helps language Shorts reach people, and it costs the owner time every upload.
- **Replacing a video:** owner uploads the new file first → delete the old one via the API (only if private and
  0 views) → fill + schedule the new one into the old slot → remove "Deleted video" placeholders from every playlist
  and re-order the 30-day playlist (Day 1 → … → Part after each 5th day).
- Uploads go **in day order** — if an earlier day isn't up yet, say so.
- Account-level reminders when relevant: automatic dubbing must stay OFF; a Short with ~0 views gets 48 h before
  any action (then check viewed-vs-swiped, re-upload with a new title if still ~0).
