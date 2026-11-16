# Sanji Nai-Chien — "Sleeping Videos Made Me Generational Profit ($250/Day)" (15 min, audio)

Source: `learning/sources/Sleeping Videos Made Me Generational Profit (250_Day) - Sanji Nai-Chien.mp3`
(transcript: `learning/sources/sanji-sleeping-videos.transcript.txt`). Given by the owner 2026-11-16 ("see if there are
things to learn from that kid too").

**Who / bias.** A faceless-AI tutorial channel. The whole video is a **Higgsfield advert** (paid AI image/video tool,
"links and prompts in the description") — the tool is rejected as before (paid; docs/14 licence + no-paid-tools rule,
same as the 2026-10-28 Danny Why note). The niche is 100 % AI ambience (rain + fireplace loops, AI music) made for
AdSense; the revenue counter and "under two minutes" are sales show. Long-form only; nothing about Shorts or teaching.
Several of his numbers are out of date for us: YPP needs **8,000** long-form hours from Feb 2027 (verified 24 Oct,
learning/notes/2026-10-24-steffen…), not 4,000.

## Claims (timestamped) and our evidence

| # | Claim | Our data | Verdict |
|---|---|---|---|
| 1 | Sleep/ambient videos win on watch time: viewers let a 1.5–3 h video run all night (00:21, 10:04) | Long videos are where our watch hours come from (docs/06: Parts 8–9 % of all watch hours each); YPP needs 8,000 long-form h | **matches the need** → proposal below |
| 2 | The biggest search term is a trap; pick high volume + low competition + rising (02:07–03:34) | We pick by real searches (suggest.py) + `niche`; outlier scan | **already done** |
| 3 | One small channel with one huge video proves the niche (04:08, 04:38) | Same as our outlier scan (learning/notes/2026-10-23-kellan…) | **already done** |
| 4 | Seasonality: cozy topics peak in autumn/winter (05:14) | docs/24 already times seasonal topics (New Year late Dec, Ramadan from mid-Jan) | **already done** |
| 5 | Visual rule: warm inside, weather outside, one story object, no people (06:03) | Ambience-only; our pictures teach a word or a scene | **not for us** |
| 6 | Seamless loop: locked camera, only small things move (07:58) | We already loop openers (sets/scenes *-loop.mp4) | **already done** |
| 7 | Thumbnail: 2–4 words; put it side by side with the top-ranking videos and compare 3 variants (09:39) | Our rule: big English subject words + small Arabic; we check phone size + a 16:9 mock, and keep 3 backup titles | **mostly done** — the "next to the top results" check is not; cheap to add when a long video is packaged |
| 8 | Title = promise + scene + purpose ("Fall asleep in 5 minutes … for deep sleep") (10:27) | Ours = subject in search words + hook; works for search (28 % of views) | **already done (our form)** |
| 9 | Description: first lines = the keyword cluster (10:46) | Our first line states the subject in search words | **already done** |
| 10 | Check "AI content: yes" (11:17) | Our rule: No (only the owner's own voice clone + real recordings) | **not for us** — his videos are fully synthetic; ours aren't |
| 11 | Mid-rolls off, pre-roll on (10:58) | Not monetized yet | **can't tell yet** |

**Rejected:** Higgsfield and any paid generator · AI music · the "under 2 minutes per video" mass-production model —
repetitive, mass-produced uploads are exactly what YouTube's inauthentic-content policy targets (docs/11), and they'd
hurt the teaching channel.

## The one idea that transfers (proposal for the owner)

**A long passive-listening video built only from recordings we already have.** Learners search for this format
(suggest.py, 2026-11-17): "learn arabic while sleeping **7 hours** / **8 hours**", "learn arabic while you sleep
(english - arabic)", "learn **levantine** arabic while you sleep", "arabic listening practice **beginner**".

- Shape: English narrator line → the owner's Arabic line → pause → the Arabic again; calm, dark, low-motion picture
  (the card only, no bright flashes), soft volume, no stars/SFX/subscribe animation; 1–2 hours to start.
- Content: the 513 recorded lines in the pool (Days 1–30, Extras, vocab, Story 1) grouped by topic — **no new
  recording**; only English narrator lines to generate (voice = the owner's pick from the C/C2 test).
- Honest packaging (gate 3): learning while asleep is not proven — promise *review/listening practice*, e.g.
  "Arabic Listening Practice While You Sleep: 300 Beginner Phrases (English–Arabic)". A Levantine/Syrian edition
  later (the owner's dialect, and it's a real search).
- Why: long-form watch hours (YPP 8,000 h) + a searched evergreen format; it re-uses Days 1–30 as spaced review.
- Before building: check the top results for these searches (`youtube_api.py niche`, ~100 units, after 09:15) —
  views vs channel size, length, how they label it.

Decision needed from the owner (format + voice): build a 1-hour pilot or not.
