# 21 — The monthly episode (owner, 2026-10-24)

**Idea (owner):** once a month, one long video (30+ min) that gathers everything from that month's Shorts into one
lesson, organised by topic and not by day. The Shorts are the small units; 5 of them make a weekly **Part**; a month
makes an **Episode**. Named "Episode 1, 2, …" and never mentions day numbers, so a stranger can start with it.

**Why:** YouTube's Partner Program needs 8,000 long-form watch hours from 1 Feb 2027 (4,000 now); Shorts watch time
doesn't count, and we had 3.6 long-form hours in our first 4 weeks (learning/notes/2026-10-24-steffen…). A 30–40 min
lesson that people search for ("learn arabic for beginners full course") is the strongest watch-hour unit we can make.
It also counts as new work, not re-upload: new order, new chapters, a new combined conversation and a final challenge
(docs/11, reused-content rule).

## Shape (16:9, like the Parts — side panel with the table of contents, the current chapter highlighted)

1. **Opening (≤ 20 s):** what you'll be able to do after this video + the table of contents on screen. No welcome.
2. **Chapters by topic** (each one = the lesson bodies of the Shorts on that topic, re-rendered with an "EPISODE N"
   badge instead of "DAY N"; every narrator line that mentions a day, "yesterday", "tomorrow" or "next lesson" is
   reworded and re-voiced; all Arabic stays the owner's/Koki's recordings).
3. **The big conversation:** one long Arabic conversation stitched from all the month's conversations and stories
   (only recorded lines), shown with Arabic + transliteration + English on screen — played once through, then the key
   lines again.
4. **Vocabulary review:** the month's word lists (v01, v02, …) as one quick picture-and-word run.
5. **Final challenge:** a real-situation challenge mixing the whole month (new questions, recorded answers).
6. **End on the peak:** the challenge payoff → "next episode" → subscribe + goodbye clip.

Chapters go into the description (YouTube chapters) and onto the side panel. Captions: English + Arabic
(transliteration), then the 13 translated subtitle languages like every other video.

## Episode 1 (October: everything up to Day 21 + Extras x01–x06 + Vocab v01–v02)

| # | Chapter | From |
|---|---|---|
| 0 | What you'll learn | new |
| 1 | Hello and your first words | Days 1–2, x01 hello, x02 goodbye |
| 2 | Your first conversation | Days 3–4 (story: Sami and the coffee) |
| 3 | I, you, he, she — no word for "is" | Day 5 |
| 4 | Yes, no, sorry, okay | Day 6 |
| 5 | Where are you from? Introduce yourself | Day 8, x03 |
| 6 | Man or woman: one letter | Day 9 |
| 7 | Numbers 1–20 and Arabic digits | Day 10, x04, x06 |
| 8 | Meeting someone in the street | Day 11 |
| 9 | My and your | Day 12 |
| 10 | Family | Day 13 |
| 11 | At the café: I want, ordering, the Syrian way | Days 15–16, v01, x05 |
| 12 | "The": sun and moon letters | Day 17 |
| 13 | Asking questions | Day 18 |
| 14 | Finding your way | Day 19 |
| 15 | I drink, I eat, I go, I love | Day 20 |
| 16 | Your body in Arabic | v02 |
| 17 | The big conversation (Arabic + English) | Days 3, 4, 8, 11, 13, 16, 19 + x03 lines |
| 18 | Final challenge | new questions, recorded answers (not Day 7/14/21's) |

Estimated length: ~25 lesson bodies × ~70 s ≈ 30 min + conversation ~3 min + challenge ~3 min ≈ **35 min**.
Quizzes (Days 7, 14) and the Day 21 challenge are not re-used inside; the final challenge replaces them.

**Title idea:** `Learn Arabic for Beginners: Full Course, Episode 1 (35 Minutes)` — searched words first, no day numbers.
**Thumbnail:** the Part style, with "ARABIC FOR BEGINNERS · FULL COURSE", "EPISODE 1" and the chapter highlights.

## How it's built (tools to add)

- `episodes/ep-01.json`: chapters → which scenes of which script (lesson body: from the first lesson scene to before
  "Your turn"/outro), plus rewritten narrator lines.
- An episode script `videos/ep01-full-course.md` generated from those scenes → `make_audio.py` (unchanged narrator lines
  come from the cache; only the reworded lines are new) → `assemble.py` with an "EPISODE 1" badge → the Part compiler
  for the 16:9 side panel and chapters.
- Cost: ~40 reworded narrator lines to re-voice + a few new pictures (opening, conversation, challenge). Nothing new to
  record unless the final challenge needs a line we don't have.

**Publish:** the first Sunday after the month's last Day is out (Episode 1 ≈ 8 Nov, or 1 Nov for October as it stands).
