# 06 — Publishing

## Where

Upload every video as a **vertical Short** (≤ 2:59). Shorts are where new channels get discovered.
Every Sunday, upload a **long-form compilation** of the week (16:9, ~15 min). This is **not optional**: only
long-form watch time counts toward the 8,000 watch hours needed for monetization
(see [07-channel-and-monetization.md](07-channel-and-monetization.md#what-this-means-for-our-strategy)).
Once a month, a "whole month in one video" (~1 hour) for bingeing and review.

## Part compilations (every 5 days)

After Days 5, 10, 15 … a horizontal **Part** video (≈ 10–12 min): short welcome → the 5 lessons back to back (each
day's repeated hook / intro / subscribe / goodbye cut) → a review quiz with the recorded Arabic → outro. Side panels:
chapter list + that day's words. Built with `tools/compile_part.py parts/part-NN.json` (review part:
`videos/wNN-review.md`). Chapters in the description; own playlist "Full Lessons".

## When

- **Daily**, same time every day — the channel preaches consistency, so it must practice it.
- Build a **buffer** of 7–10 finished videos before publishing Day 1, and schedule uploads in YouTube Studio.
  A busy week must never break the streak.

## Upload checklist (learned on Day 2)

- **Title:** no hashtags in the title (they're already shown above it from the description).
- **Description with Arabic:** put each Arabic phrase **at the end of its line**, wrapped in invisible direction markers
  (U+2067 … U+2069) — otherwise YouTube jumbles the order and moves ؟ to the wrong side. Claude writes a ready-to-paste
  `videos/NNN-description.txt` for every video.
- **Links:** strip `?si=…` from YouTube links. Links in Shorts descriptions aren't clickable → use **Related video**.
- **Related video:** always set it (Day 1 for early videos; later the playlist's first video or the weekly compilation).
- **Thumbnail:** "Upload file" with Claude's `thumbnail (vertical).jpg` (not "Select from video").
- **Title and description language:** English. **Category:** Education, **Type:** Concept overview.
  Education type/level and automatic places/concepts are **per video** in Studio → Details — Upload defaults don't
  offer them and the API can't set them (checked 2026-10-19).
  Problems / Academic system: leave empty (they're for school subjects).
- **Shorts remixing:** allow video and audio remixing (free exposure).
- **Automatic dubbing: OFF** (Studio → Settings → Channel → Advanced settings → uncheck "Allow automatic dubbing").
  Since Feb 2026 YouTube auto-dubs every upload by default; a dub would also "translate" the Arabic being taught.
  Check already-published videos under Languages and remove auto-dubbed tracks. Caption auto-translation is fine.
- A "Video verification in review" pop-up means the Advanced-features verification is pending (~24 h). Click "Got it";
  nothing else to do.

## Titles

Pattern: **`<Benefit or curiosity> | Day N · 2 Minute Arabic`**

Examples:
- `I Learned Spanish the Wrong Way — Don't Do This With Arabic | Day 1 · 2 Minute Arabic`
- `10 Arabic Phrases You'll Use Every Day | Day 2 · 2 Minute Arabic`

Keep the benefit part under ~50 characters so it isn't cut off on mobile.

**Parts (long-form, found by search):** search phrase first, series last —
`Learn Arabic in 10 Minutes – Full Beginner Lesson | Part 1 · Days 1–5` (decided 2026-09-30).
**Extras:** `<hook> | Arabic Extras`, e.g. `10 Ways to Say Hello in Arabic (5 in Syrian dialect) | Arabic Extras`
(owner's wording, 2026-09-30 — may run a few characters over 50).

## Description template

```
Day N of 30 — <one-sentence summary>.

Two minutes a day. Your first Arabic conversation in 30 days.
Missed a day? No guilt — just do today's two minutes.

📝 Today's Arabic:
<the words/phrases with transliteration and meaning>

▶️ Start from Day 1: <playlist link>
🔔 Subscribe to keep your streak.

#learnarabic #arabicforbeginners #2minutearabic
```

## Tags (3-group formula, from "If your shorts get under 1,000 views…" by Dan the Creator)

3–4 **video-specific** tags (what this video is) + 3–4 **niche** tags (learn arabic, arabic for beginners, arabic lesson,
modern standard arabic) + 3–4 **broad** tags (language learning, learn languages, shorts, study with me).
No hashtags in the title; ~3 hashtags in the description.

## A Short that gets no views (new channel)
- New channels are throttled at first — **wait 48 h**. Use the channel's Google account normally (watch, like, comment).
- After 48 h check Studio → Analytics → **Viewed vs. swiped away** (aim ≥ 70 %).
- Still ~0 after 48 h → delete and re-upload on another day with a new title.
- Hook in the first 2 seconds. Later idea: a 15–20 s teaser Short per lesson that points to the full lesson.

## Tag experiment: "viral shorts" (started 2026-09-29, CLOSED 2026-10-06: dropped — see Learnings)

Days 3 and 5 got the extra tag "viral shorts"; Days 2 and 4 are the comparison (same tags otherwise).
After 7 days compare in Studio: views, "viewed vs swiped away", impressions. Small numbers → treat as a hint only.

## Old tag list (superseded)

`learn arabic, arabic for beginners, arabic lesson, speak arabic, arabic phrases, modern standard arabic,
fusha, arabic conversation, learn arabic fast, 2 minute arabic`

Put 3 hashtags max in the description (the first 3 show above the title).

## Thumbnail / Shorts cover

(The old rules — big Arabic word in the centre, stopwatch icon — are superseded.)
- **Shorts (2026-10-16):** big **English** words naming the subject + the DAY N / category badge + **one small Arabic word**;
  one big object or place that IS the subject; a person only when the person is the subject, then close-up. Shorts
  thumbnails are shown in a 16:9 box (search, suggested), so check the phone-size AND a 16:9 mock. The first ~1.5 s of a
  Short looks like the thumbnail.
- **Parts (2026-10-19, the channel page's first impression):** "**ARABIC CONVERSATION**" (the series' promise) + the
  Part's 3 topics as a **bullet list** (never mixed like "FAMILY CAFE") + **one useful phrase that is really said in that
  Part**, a different one per Part (اسمي سامي، تشرفنا · أنا من سوريا. وأنت؟ · أريد شاي، من فضلك) — never مرحبا /
  أهلا وسهلا (they repeated across the page and looked too basic). `thumbnail.py --wide --bullets "a|b|c"`.
- **Viewpoint:** topics and titles from the learner's side — they are the visitor in an Arab country ("Talking to
  native speakers", not "Meeting a tourist"; "native speakers", never just "natives").
- Two thumbnails side by side on the channel page should look different (e.g. the talk videos: one close-up, one
  full shot).

## Playlists

- **30 Days to Your First Arabic Conversation** (Days 1–30, in order)
- **Arabic Phrases**, **Arabic Conversations**, **Arabic Stories**, **Arabic Grammar Made Easy** (by format)
- **Arabic Vocabulary** — top-10 words per situation (`videos/v0N-…`, café, street, store, school, home, kitchen, family…).
- **Arabic Extras** — bonus Shorts outside the 30 days (`videos/x0N-…`, e.g. 10 ways to say hello/goodbye).
  Standard Arabic and Syrian dialect, each phrase labelled; the course itself stays standard Arabic.

## Cross-promotion with 2 Minute Spanish

- Add the sister channel under **Customization → Layout → Featured channels**.
- Day 1's story is about learning Spanish — link the Spanish channel in its description.
- Now and then a community post: "Learning Spanish too? Same method: …".
- Never post Spanish lessons here — keep each channel's audience clean.

## Community

- **Daily comment replies (19 Oct, owner):** a laptop timer (2min-comment-replies, 19:30, catches up after sleep) starts
  Claude with the rules in `tools/comment_replies_prompt.md`: praise → ❤️ / 👍 / a few words of Arabic WITHOUT harakat;
  learners' Arabic → a short warm line; lesson questions → one or two sentences; criticism, religion, politics, personal,
  money, spam → not answered, listed for the owner. Every reply is logged (`~/.local/share/2min-yt/replies.jsonl`); one
  desktop summary per run. Hearts can't be given through the API — the owner adds them in the Studio app. Instagram
  replies may need one re-login for the comments permission.

- Pin a comment on every video with a mini task: *"Write today's phrase in the comments — in Arabic letters if you can!"*
- Reply to comments in both English and Arabic (with transliteration). Early replies boost the video.
- Use the comments to collect ideas for Month 2.

## Track (weekly)

| Metric | Why |
|---|---|
| Average % viewed | Is 2 minutes holding attention? Where do people drop? |
| Returning viewers | Is the streak idea working? |
| Subscribers per video | Which formats convert? |
| Top comments/questions | Future episode ideas |

## Weekly rhythm (from Week 3, owner 2026-10-05)

| Slot | Shorts chain (17:00 Oslo, one a day) | Long chain |
|---|---|---|
| Mon–Fri | 5 course days | |
| Sat | Arabic Extra (phrases, dialect, filmed sketch by the owner) | Part (the 5 days + quiz) |
| Sun | Arabic Vocab (top 10 words in one place) | |
| Monthly | — | "The whole month in one video" |

## Facebook Page + groups (owner 2026-10-31)
- The Meta app "2minarabic tools" must stay **Live**: Reels posted while it was in development mode were visible only
  to app roles (22 Reels, 20–29 Oct, 0–3 views each — deleted 31 Oct and republished).
- **The Page is English-only** (like the Instagram profile). Daily: a proven Instagram hit at 12:00
  (facebook-hits.yml, data/fb-hits.txt: 13 hits by Instagram views, then the other older Reels) · the English Reel
  at 15:00 (instagram-daily.yml). Language versions never go to the Page.
- **Groups:** no API (Meta removed group posting in 2024) and no bots (account risk). The owner posts 3 a day by
  hand from https://muhannadsnan.github.io/2min-arabic/groups.html (tools/fb_groups_page.py: calendar rotation, the
  same 3 on every device + yesterday's 3 to catch up; English groups share the Page Reel, other languages upload the
  file from ~/Downloads/fb-groups/). More than ~3 shares at once into groups risks "temporarily blocked from posting
  in groups". Groups chosen for topic fit first (general/beginner Arabic, not grammar/religion/exams), then size ×
  activity, a mix of busy and quiet (posts in quiet groups stay on top for days). Hindi-script and Malay Arabic-learning
  groups barely exist (searches return tiny or spam groups) — Hindi speakers sit in English/Urdu groups, Malaysians
  in the Indonesian ones.

## Learnings (dated)
- 2026-10-06: "viral shorts" tag experiment → **dropped**. Tagged Day 3 (55 views, 38 % viewed) and Day 5 (38, 40 %) did not
  beat untagged Day 4 (86, 109 %) or the Day 2 re-upload (26 in 4 days, 61 %); content and hook matter, the tag doesn't
  (evidence: YouTube Analytics 20 Sep–6 Oct). Removed from Days 3 and 5; never add it again.
- 2026-10-15: The channel-intro scene (≈7–18 s: hello clip + "I'm your teacher… my promise") loses 35–50 % of viewers on every Day measured (Days 6, 8, 9: 0.86→0.50, 0.88→0.62, 0.96→0.48); x03 without the intro holds 0.98→0.77 (evidence: YouTube Analytics retention, 15 Oct).

- 2026-10-20: **Instagram grows the audience, YouTube keeps it.** Same videos: 330 Instagram followers vs 27 YouTube
  subscribers; Instagram's best Reels are **word lists and clear rules** — Day 5 (1 858 views, 50 saves), Day 3 (1 803,
  66 saves), Day 8 (1 385, 34 saves, +69 followers that day) — while greetings and quizzes stay at 195–460 (evidence:
  Instagram insights 20 Oct). → More word-list / one-rule content, the weekly carousel, and every Instagram surface points
  to YouTube (bio link, free PDF page).
- 2026-10-20: **Search traffic needs a steady supply of searched-topic videos.** x03 brought 181 search views in its
  first 5 days, then faded; with no new searched hit, search fell 254 → 108 views week over week while the Shorts feed
  held (292 → 320) (evidence: YouTube Analytics traffic sources 6–19 Oct). → Keep the 1 searched-topic Extra a week.
- 2026-10-20: **Busy stories lose viewers** (second time): Day 13's family story held 14 % this week (17 % to 14 Oct)
  while one-place, two-character stories hold (Day 4 lifetime 92 %). → Stories: one place, two characters, one twist.

## Other languages (owner, 2026-10-18/19)

Priority (owner): 1. titles + descriptions → 2. top-language tags → 3. subtitles → 4. audio tracks.
- **YouTube, every video:** titles + descriptions in 13 languages (hi ur id bn tr fa ms fr ru de so sw es) — set by
  `fill` itself for new videos; top-language tags (Hindi, Urdu, Indonesian/Malay, Bengali, Turkish, Persian; the most
  generic tags go first when 500 characters don't fit); subtitles in the same 13, uploaded by the daily job one language
  across the whole channel at a time (22 a day = 8,800 units; a quota extension to 50,000/day was requested 18 Oct).
  New descriptions carry the 13-language block; the 31 older ones get it when the API has room (calendar).
- **YouTube, top videos (top 6 by views + the first video of each week):** audio tracks in 11 labels from 9 files —
  French, Turkish, Spanish, Hindi = Hindi + Urdu, Indonesian = Indonesian + Malay, Russian, Swahili, Persian (TTSMaker,
  pasted by the owner, then Chatterbox voice conversion to the owner's voice), Bengali (Piper bn_BD, CC BY-SA → credit
  line in the description, + voice conversion). All 66 tracks of the 6 top videos live since 19 Oct; the Arabic in every
  track checked identical to the original. YouTube auto-dubbing stays off (it would re-voice the Arabic). Free,
  commercial-OK models only.
- **What made the dubs fit (18 Oct):** trim the voice's ~0.6 s of silence around each take; shorten pauses inside a
  sentence to 80 ms before speeding up; extra takes when none fits; lines that still don't fit get shorter text
  (102 → 0 too-long lines). Subtitle-only translations often run long when spoken — shorten before generating audio.
- **Channel level (19 Oct):** About text has a "🌍 Learn in your language" paragraph and is translated into 13
  languages (6 live, 7 queued for the next quota day — `youtube_api.py channel-about`); channel keywords = "learn
  Arabic" + "Arabic conversation" in all the languages (494/500 characters).
- **Instagram:** no audio tracks. Each Reel's caption gets 2 rotating language lines + 2 language hashtags (3 fixed +
  2 = 5) that point to YouTube ("…with Bengali subtitles on YouTube" — never promise lessons in their language on
  Instagram). Dubbed versions of top videos go out as **Trial Reels** (non-followers only, hidden from the profile grid,
  visible in Professional dashboard → Trial reels): x03 in 9 languages, 2 a day (~11:30 + ~18:30) until ~23 Oct, then
  1 a day starting with Day 12. Hint after 1 day: the Indonesian and Hindi Trial Reels got 122 and 107 views from
  non-followers only, vs 147 (Day 10) and 187 (Day 9) for normal Reels incl. followers — check on 22 Oct.
- Details and tools: the upload-handover skill ("Subtitles + audio tracks", "Instagram"), memory note 2min-other-languages.
- 2026-10-31: **Instagram's near-copy filter kills same-picture dubs; a different look per language fixes it.** Dubbed
  Reels that only changed the voice dropped to 0 views and got "looks like something you shared before" (x03 ms/sw,
  Day 12 id); the Hindi Day 12 with its own cover, frame, badge and Hindi subtitles got 2,375 views, 33 saves,
  15 shares and 34 s average watch in ~18 h — 10× a normal Reel (evidence: Instagram insights 30–31 Oct).
  → Every language version is built with tools/ig_lang_version.py.
- 2026-10-31: **Facebook shows nothing posted while the Meta app is in development mode.** 22 Reels (20–29 Oct): 0–3
  views; the first Reel after switching to Live (Day 17): 125 views — but 2 s average watch from 100 % non-followers
  (evidence: Business Dashboard 31 Oct). → App stays Live; watch whether Facebook finds the right audience.
