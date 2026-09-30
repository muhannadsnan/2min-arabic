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

## Tag experiment: "viral shorts" (started 2026-09-29, check 2026-10-06)

Days 3 and 5 got the extra tag "viral shorts"; Days 2 and 4 are the comparison (same tags otherwise).
After 7 days compare in Studio: views, "viewed vs swiped away", impressions. Small numbers → treat as a hint only.

## Old tag list (superseded)

`learn arabic, arabic for beginners, arabic lesson, speak arabic, arabic phrases, modern standard arabic,
fusha, arabic conversation, learn arabic fast, 2 minute arabic`

Put 3 hashtags max in the description (the first 3 show above the title).

## Thumbnail / Shorts cover

- One big idea, max 3–4 words: e.g. **"2 MIN A DAY"**, **"10 PHRASES"**, **"NO 'IS'?!"**
- Arabic word large in the center (added in the editor, not by the image AI).
- Same layout every time: stopwatch icon top corner, "DAY N" badge. Recognizable in the feed.
- For Shorts: pick a strong frame as the cover in the upload screen.

## Playlists

- **30 Days to Your First Arabic Conversation** (Days 1–30, in order)
- **Arabic Phrases**, **Arabic Conversations**, **Arabic Stories**, **Arabic Grammar Made Easy** (by format)
- **Arabic Extras** — bonus Shorts outside the 30 days (`videos/x0N-…`, e.g. 10 ways to say hello/goodbye).
  Standard Arabic and Syrian dialect, each phrase labelled; the course itself stays standard Arabic.

## Cross-promotion with 2 Minute Spanish

- Add the sister channel under **Customization → Layout → Featured channels**.
- Day 1's story is about learning Spanish — link the Spanish channel in its description.
- Now and then a community post: "Learning Spanish too? Same method: …".
- Never post Spanish lessons here — keep each channel's audience clean.

## Community

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
