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
3. **Title** in a code box. Pattern `<subject in search words> (+ hook) | <Category> · Day N` — Category = Phrases,
   Grammar, Story, Conversation, Quiz, Numbers, Greetings, Vocabulary, Syrian Dialect, Intro (owner, 2026-10-16: "Arabic
   Extras" is the series name, not what the video is). Extras/vocab: `… | <Category>` (no day). Parts: `… | Part N · Days a–b`. No channel name, subject part ≤ 50 characters, no hashtags —
   see **Packaging rules** below.
4. **Description** embedded in a code box (also saved as `videos/<stem>-description.txt`):
   - **no flag emojis** (🇸🇾 renders the old Syrian flag; flags are political) — use 🗣️ / 📍 for regions;
   - every Arabic phrase at the **end** of its line, wrapped in U+2067 … U+2069 (otherwise YouTube scrambles it);
   - transliteration — meaning — Arabic;
   - **the 5-language line** before the hashtags (`tools/description_languages.json`: Farsi, Indonesian, Urdu/Hindi,
     Turkish, French — the biggest learner searches + our #1 search term, owner 2026-10-15);
   - "Start from Day 1" link without `?si=…`; ~3 hashtags at the end (`#learnarabic` … `#2minutearabic`).
   Write it with Python so the invisible markers are really in the file, then print it once to verify.
5. **Tags** in a code box, 20–26 tags, use the room up to ~470 characters, most important first, in this order (owner, 2026-10-02/05):
   - 3 **search phrases** people really type, specific to this video ("how to say sorry in arabic", "arabic
     conversation for beginners") — real terms from channel-review's search-terms report win;
   - 3 **question-form / synonym searches** in the owner's style (2026-10-05): "what is greeting in arabic",
     "welcome in arabic", "sorry in arabic", "how to talk to arabic people", "ways to say hello in arabic";
   - 2–4 **transliterated keywords** of today's words ("shukran", "ma ismuk", "tayyib") — learners search these;
   - **Research first** (log the picks in `docs/15-tag-research.md`): `python3 tools/suggest.py "<topic> in arabic" "<Arabic topic>"` = YouTube's own
     autocomplete (what people really type, most-searched first). Pick learner phrases only (drop songs, kids,
     perfumes, games, everyday-life Arabic like "كيف تعتذر من شخص" — that's Arabic speakers, not learners);
   - 2 **learner Arabic** tags on every video: "تعليم اللغة العربية لغير الناطقين بها", "تعليم عربي للاجانب"
     (+ topic ones: "محادثة تعارف بالعربية", "قصة قصيرة بالعربي", "الاعتذار بالعربية" — owner, 2026-10-05);
   - 5–7 **Arabic-script** tags (owner, 2026-10-02): today's words in Arabic ("نعم", "طيب"), 2 **mixed** phrases a
     learner pastes in after seeing a word ("طيب meaning", "من أين أنت in english"), and one topic phrase
     ("تعلم اللغة العربية", "قصة قصيرة بالعربية");
   - niche ("learn arabic", "arabic for beginners", "modern standard arabic") · broad ("language learning", "shorts").
   Arabic script goes in tags and descriptions — **not in titles and not on thumbnails** (2026-10-16) (it tells YouTube the
   video is for Arabic speakers and mixed-direction titles get scrambled); titles may use transliteration.
   Formerly: 3-group formula: 3–4 video-specific · 3–4 niche · 3–4 broad. "viral shorts": tested and dropped 2026-10-06 — never use it.
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
  Automatic chapters **on**, Automatic places **off**, Automatic concepts **off**. Studio → Settings → Upload defaults
  does NOT offer these (owner checked 2026-10-18) — they stay a per-video step in Studio → the video → Details.
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
- **Captions on the channel:** `$Y tools/youtube_api.py captions <id> --replace <srt>` swaps the English track. API
  quota is 10,000 units/day (a caption upload = 450, a fill ≈ 600): for big batches put the rest in
  `~/.local/share/2min-yt/captions-pending.txt` — `tools/caption_backlog.sh` (cron, 10:30 daily) uploads them.
- **Quota out?** Queue the command line (e.g. `fill w02 <id> --publish-at … --apply`) in
  `~/.local/share/2min-yt/pending-commands.txt`; `tools/pending_jobs.sh` (cron 09:15, after the reset) runs it.
- **Parts are published after their last day** (Part 2 after Day 10) — never before, it would spoil the days.
- **Replacing a video:** owner uploads the new file first → delete the old one via the API (only if private and
  0 views) → fill + schedule the new one into the old slot → remove "Deleted video" placeholders from every playlist
  and re-order the 30-day playlist (Day 1 → … → Part after each 5th day).
- Uploads go **in day order** — if an earlier day isn't up yet, say so.
- Account-level reminders when relevant: automatic dubbing must stay OFF; a Short with ~0 views gets 48 h before
  any action (then check viewed-vs-swiped, re-upload with a new title if still ~0).
- **Batch fills (2026-10-07):** fill a batch with **fixed dates** (`--publish-at 2026-10-14T15:00:00Z`), not `next` —
  one failed call made `next` skip ahead and scheduled Day 15 before Days 13–14. Fill is safe to re-run; retry a 401.
  A video ID starting with "-" needs the options first: `fill --publish-at … --apply -- <stem> -ju67…`.
  Afterwards re-sort the 30-day playlist (Day 1 → … → Part after each 5th day) and run `audit`.

## Packaging rules (owner + channel data, 2026-10-16) — titles and thumbnails

Why: 28 % of our views come from YouTube **search**, and search matches the title's words. Our best long-tail video is
the plain subject title "Introduce Yourself in Arabic…" (303 views); story/teaser titles ("Meet Lina's Family", "Understand
a Real Street Conversation") got 37–57. Shorts thumbnails are shown in a **16:9 box** in Studio, search and suggested
(our 9:16 image becomes a narrow centre strip with blurred sides), so small people and small Arabic text are unreadable.
- **Title = the subject first, in the words people search for, then the series:** `<subject in Arabic> (+ short hook) | Day N`
  — e.g. `How to Order Coffee in Arabic (With Milk, No Sugar) | Day 16`, `Arabic Question Words: What, Who, Where | Day 18`.
  then the **category** (`| Grammar · Day 17`, `| Numbers`, `| Syrian Dialect` — never "Arabic Extras"/"Arabic Vocab", which
  are series names), Parts `| Part N · Days a–b`. **No channel name** in the
  title (YouTube shows it under the title; it cost 19 characters that phones cut). Subject part ≤ 50 characters.
  Avoid story/teaser-only titles ("Meet Lina's Family") — say what the viewer learns ("Family Words in Arabic: …").
- **Thumbnail text = big English words** naming the subject ("ORDER COFFEE", "FAMILY WORDS", "BODY PARTS"), the DAY N
  (or category) badge, and **one small Arabic word** under them — it tells the viewer which language the lesson is for
  (owner, 2026-10-16); never a big Arabic word. `tools/thumbnail.py` default style "subject" does exactly this; `--crop`
  zooms into an object inside one of the video's own images.
  The words may repeat the title's subject — clarity beats cleverness.
- **Thumbnail picture = one big object or place that IS the subject** (a coffee cup, a family photo frame, a street with
  an arrow, a chalkboard, a hand) rather than small characters; a person only when the person is the subject, and then
  close-up. Check the `-phone-size.png` AND a 16:9 mock (centre strip) — both must read at a glance.
- **The first ~1.5 s of a Short looks like the thumbnail** (owner, 2026-10-16): the same big subject words + small
  Arabic word over the moving opener, narrator already speaking from 0.0 s — the first frame doubles as the thumbnail in
  the feed, and the motion behind it still stops the scroll. Then the normal scene-1 card.

**Schedule in Oslo time (2026-10-16):** `fill --publish-at "2026-10-26 17:00"` (no Z) — the tool converts to UTC itself.
Never type a fixed `T15:00:00Z`: 17:00 Oslo is 15:00Z in summer but 16:00Z from the last Sunday of October (v02 was
almost published at 16:00). After filling, read the times back (`videos`) and check each is 17:00 Oslo.

## Localize — every video, automatically inside `fill` (owner, 2026-10-17; 13 languages since 2026-10-18)

Translated titles + description openers in the **13 languages** (hi ur id bn tr fa ms fr ru de so sw es), written
with the upload sheet. `fill --apply` publishes them + the top-language tags by itself when the video's entry is in
the file (it warns when it isn't); the translated subtitles come from `dubs/<stem>.json` via the daily job:
1. Write them into `tools/localizations.json` (`{"<video id>": {"name": …, "fa": [title, opener], …}}`): titles use the
   words people search ("آموزش زبان عربی از صفر", "عربی سیکھیں", "Arapça öğren", "belajar bahasa Arab", "apprendre
   l'arabe"), Day/Part numbers the local way (روز ۱۰ · دن 10 · 10. Gün · Hari 10 · Jour 10), max 100 characters; the
   opener = 1–2 plain sentences. Keep the wording close to the approved ones already in the file.
2. `$Y tools/youtube_api.py localize <id>` = dry run (prints every title/description; fa + ur marked "needs native
   check" = written by Claude, not checked by a native speaker) → `--apply`.
   It keeps the English title/description, sets defaultLanguage en, merges existing localizations (never deletes),
   builds each description as opener + the English links/language block/hashtags unchanged, and adds the 7 shared
   language tags, removing the most generic tags one by one (LOC_GENERIC order) until they fit 500 characters.
   It never touches the file or the thumbnail (YouTube has one thumbnail for all languages).
3. Report video × language done/failed (the tool reads it back after a short wait — YouTube shows it with a delay).
Check on 2026-10-31: Studio → Analytics → Research — search terms in those languages + views from Iran, Afghanistan,
Pakistan, Turkey, Indonesia, France, before vs after.

**Other languages — rules (owner, 2026-10-17):** ONE video with translated titles/descriptions (localizations) —
never re-upload the same video per language (duplicate content, split views). Tags are shared by all languages, so
each language's search terms go into the tags. A native speaker check of Persian/Urdu is welcome when one is available
(the owner can't read them; Claude writes them in the approved style). Narration in another language later = an extra
audio track on the SAME video. New content made for one language audience gets its own upload (e.g. "Arabic words you
already know in Persian").

## Subtitles + audio tracks in other languages (owner, 2026-10-18)

**Priority (owner, 2026-10-18), cheapest reach first:** 1. translated **titles + descriptions** (all 13 languages,
every video — `localize`, ~50 units per video) → 2. **tags** of the top languages (LOC_TAGS, added by `localize`; the
most generic tags go first when 500 characters don't fit) → 3. **subtitles**, one language at a time on the whole
channel (`subtitle-backlog`) → 4. **audio tracks** for the selected top videos (owner in Studio).

**Three tiers (owner, 2026-10-18):**
| Tier | Which videos | Subtitles (text, no owner work) | Audio tracks (owner adds in Studio) |
|---|---|---|---|
| All | every video, from now on + backfill | 13, in priority order: hi ur id bn tr fa ms · fr ru de so sw · es | — |
| Top | top 6 by views + the first video of each week | same | fr, tr, es, hi (= Hindi + Urdu), id (= Indonesian + Malay), ru, sw, fa (TTSMaker), bn (Piper) — owner 2026-10-18 |
| Star | > 2× the channel median views (now x03, Day 12) | same | = Top for now (German = subtitles only, owner) |
Portuguese + Chinese dropped (owner 2026-10-18: small Arabic-learning interest; YouTube blocked in China). Re-check the
tiers at every weekly review (`videos`); on 31 Oct compare with Studio → Audience → Top geographies and cut languages
that bring nothing. Not filmed videos (Day 1: lips on camera), not Parts yet
(compiled from several timelines). YouTube's own auto-dubbing stays OFF (it would re-voice the Arabic too).
New video: write its `dubs/<stem>.json` (13 languages) with the sheet; `caption_backlog.sh` (10:30 daily) uploads
missing tracks itself, language by language in priority order, most-viewed first, max 22 a day (a new video = 13 tracks) (`youtube_api.py subtitle-backlog`; IDs in `dubs/ids.json`). **Free, commercial-OK models only** (owner: "we only use free licenced models everywhere").
1. **Translations** `dubs/<stem>.json`: every narrator clip (`audio/<stem>/timeline.json`, speaker narrator, key = n)
   in the 13 languages of the table (audio languages: fr, tr, es, hi, id + star ru, sw; ur/ms = proper Urdu/Malay text). Same or fewer syllables than the English
   (the line must fit its slot). Arabic words stay transliterated (ismi). hi = plain spoken Hindustani that Urdu
   speakers understand too (lafz, zaroori, sawaal; ख़/ग़/क़ kept); id = everyday Indonesian (read by the Malay voice).
2. **Audio** (GPU, one at a time): `$TTS tools/dub_track.py dubs/<stem>.json <lang>` for fr, tr, es, hi, id →
   `output/<stem>/dub-<lang>.m4a` + `-preview.mp4`. The owner's clone speaks the language; all Arabic stays the
   owner's/Koki's real voice. Check the report: every line "fits"/"sped up ≤ 1.18×", CER ≤ 0.15 (hi ≤ 0.3: Whisper writes English loanwords in Latin letters); "TOO LONG" → shorten
   the line and re-run. Persian: no free model → no audio. Indonesian = Chatterbox `ms` voice (VOICE map in the tool).
3. **Subtitles** (API, 400 units each): `python3 tools/dub_subs.py dubs/<stem>.json` → `subs-<lang>.srt` (Arabic cues
   with transliteration kept) → `$Y tools/youtube_api.py subtitle <id> <lang> output/<stem>/subs-<lang>.srt` for all 8.
   More than ~20 tracks in a day → put the rest in `~/.local/share/2min-yt/pending-commands.txt`
   (`subtitle <id> <lang> <srt>`, runs at 09:15).
4. **Owner (no API for audio tracks):** Studio → the video → Languages → add language → Audio → Add → the m4a.
   Language labels: French · Turkish · Spanish · **Hindi AND Urdu (the same dub-hi.m4a twice)** · **Indonesian AND
   Malay (the same dub-id.m4a twice)** — spoken, these pairs are understood both ways; YouTube plays the track that
   matches the viewer's language (owner, 2026-10-18). The hand-over lists the files per video. Automatic dubbing stays OFF.

## Instagram (owner, 2026-10-17)
- **Saves decide reach:** word lists and clear rules get saved (Day 3: 65 saves, Day 5: 50); quizzes and greetings don't.
- **One carousel a week** from the week's best word list, built from the video's own cards, one word per slide.
- Captions keep the consistent style (first line of the description · word lists · fixed footer · 5 hashtags —
  tools/ig_refill.py builds them).
- **Other languages on Instagram (owner, 2026-10-18):** no extra audio tracks there (Instagram has no upload for them;
  Meta's AI voice translation would re-voice the Arabic → stays off). Instead, at posting time `ig_cloud_post.py`
  (`add_languages`) adds **two rotating language lines** above the hashtags ("Belajar bahasa Arab, 2 menit sehari.",
  "Arabi seekhein, roz sirf 2 minute." …) that point to YouTube ("…with Bengali subtitles on YouTube" — never promise
  lessons in their language on Instagram) and **two rotating language hashtags** next to the 3 fixed ones
  (#learnarabic #arabicforbeginners #2minutearabic + e.g. #belajarbahasaarab #learnarabicinurdu = 5). Rotation:
  Indonesian, Urdu/Hindi, Turkish, Persian, Bengali, Malay, French (LANG_ROT, by day of the year). Instagram search
  reads caption words; "See translation" covers the rest. Check which language hashtags bring views at the review.
- **Trial Reels with dubbed audio (owner, 2026-10-18 test):** a top video's dubbed version (`dub-<lang>-preview.mp4`)
  posted as a Trial Reel — shown to non-followers only, so followers don't get the same video twice:
  `instagram_api.py post <mp4> --caption-file <txt> --cover <jpg> --trial --apply` (caption in that language +
  its hashtags). Graduation to followers is by hand in the app (MANUAL). Compare their reach with the normal Reels.
  **Daily since 2026-10-19 (owner):** one language a day, automatic — `tools/ig_trial_add.py <stem> <captions.json>
  --apply` queues a video's dubbed versions (encrypted, `ig-trial` release); `.github/workflows/instagram-trial.yml`
  posts one at ~18:30 (after the 15:00 Reel; once a day via a done-<date> marker). Order: x03 first (tr, fa, bn, ur,
  ru, es, fr, ms, sw — Urdu uses the Hindi audio, Malay the Indonesian), then the next top video (Day 12). Captions in
  that language, ending "more lessons with <language> subtitles on YouTube (link in bio)".
