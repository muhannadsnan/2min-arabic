# أكاديمية نمو — "لماذا قناتك على يوتيوب لا تنجح؟ (5 أخطاء قاتلة)"

- **Type:** YouTube video (audio from the owner), 24:03, in Levantine Arabic · transcribed 2026-10-15 (Whisper medium,
  ar) → `../sources/numuw-academy-5-deadly-mistakes.transcript.txt` (Whisper slips on some dialect words).
- **Who:** an Arabic YouTube coach (Numuw Academy). **Bias:** promotes his paid community / free course on Telegram
  (02:30–03:20). Mostly about **long-form** videos.
- **Trust:** shows his own Studio numbers (channel 0 → 93 k subs in ~5 weeks, 2.5 M long-form views; a student
  +4 k subs in 90 days). Anecdotal but concrete.

## The 5 mistakes (with timestamps)

1. **[03:24–07:16] Begging for subscribers** (sub-for-sub, comment spam). Subscribers with unrelated interests are the
   **first test audience** for every new video; they don't click → low CTR → YouTube stops showing it, "even if it's the
   best video in the world".
2. **[07:18–10:46] Publishing without a plan:**
   - videos from your mood instead of what the audience wants → **search YouTube for what already gets views in your
     niche** (if a niche channel's video got many views, people want that topic);
   - **a fixed schedule** so viewers know when to come;
   - **one clear goal per video**: what does the viewer get by watching?
3. **[10:46–13:34] A boring or long intro:** "the first 10 seconds decide if the viewer stays… don't say *salam, my name
   is…, today we'll…*: start the topic, the problem and your promise immediately."
4. **[13:35–17:58] Weak title + thumbnail:** a thumbnail with **3 elements (4 at most)**, simple, instantly saying what
   the video is about and **who it's for** (his 1.4 M example: black background + one known person + a few words).
5. **[18:00–23:36] Not analysing results:** impressions → **CTR (aim 5 %; new channels often < 1.5 %)** → low CTR = the
   idea or the thumbnail is bad · **watch time** · **the retention graph**: steep drops = where viewers leave; rises =
   re-watched parts (do more of that); a curve that "falls to the floor" early kills the video's reach.

## Checked against our channel

| Claim | Our evidence | Verdict |
|---|---|---|
| 1 No sub-begging | Never done (docs/11); our 20 subs came from real viewers (x03 gave 5) | **Already done** |
| 2a Topics people want | x03 ("introduce yourself") → 181 search views; niche research below shows big demand we don't serve yet | **Matches — act** |
| 2b Fixed schedule | Daily 17:00 Oslo since day 1 | **Already done** |
| 2c One clear goal | Titles state a benefit (pre-upload-gate) | **Already done** |
| 3 First 10 s | Our intro drop at 7–18 s on every Day; 3rd source saying the same | **Matches — approved change from Day 16** |
| 4 Thumbnail ≤ 3 elements | Ours have 5: picture + badge + 2 text lines + Arabic word. Shorts thumbnails show mainly in search/channel page — where x03 found its viewers | **Plausible — test** |
| 5 Analyse | Weekly channel-review with retention; CTR/impressions aren't in the API → Studio screenshot for Parts | **Already done** (CTR: ask) |

## Niche research (new command, 15 Oct: `youtube_api.py niche "<query>"`, last 365 days)

- **Story Shorts for beginners are a proven format:** "Learn Arabic Through a Short Story 🌟📚 | Easy Arabic for
  Beginners" (Short) **2.06 M views, ~147 k/day**; "Easy Story with Sami and Basbous" 98 k. → our story days fit.
- **The alphabet / single letters are the biggest demand by far:** "Learn Arabic Letter Ta (ت)" (Short) **1.39 M**;
  alphabet songs 10–180 M (kids). We teach no letters yet.
- **Curiosity word Shorts:** "The Arabic word for 'now' is fascinating" 800 k · "NEVER say this in Morocco" 1.1 M ·
  "These Arabic words are fascinating" 420 k.
- **Numbers:** an Indonesian "count in Arabic numbers" Short 22 M; our own search terms include Persian, Kurdish and
  Indonesian learners. → our audience is international, not only English natives.
- Levantine/Syrian content is small (≤ 39 k on Shorts): keep dialect for the occasional Extra, not the core.

## What we change

1. 🤖 **Niche research is now part of planning** (plan-lessons: run `niche` for the week's topics; channel-review: a
   monthly look) — applied.
2. **Proposal — "Arabic letters" series:** one Short per letter (the shape, the sound, 3 words from our course that use
   it, a "find the letter" game) — 28 reusable Shorts in one template, low recording effort (≈5 lines per letter).
   Huge proven demand and it fills a real gap (our viewers read only transliteration today).
3. **Proposal — curiosity word Extras** ("The Arabic word for 'now' is fascinating" shape) using our course words.
4. **Proposal — thumbnail test:** 3 elements only (the picture + 2–3 big words + the Arabic word), drop the badge, on
   one week of Shorts; compare search views with the week before.
5. Ask for **impressions + CTR** screenshots on Parts in channel-review (aim 5 %).
