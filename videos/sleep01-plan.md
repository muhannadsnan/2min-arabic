# sleep01 — "Learn Arabic While Sleeping" pilot (PLAN for the owner, Tue 17 Nov)

**Publish:** Sat 21 Nov, 12:00 (long-video slot) · 16:9 · **8 hours = a 1-hour lesson × 8 rounds**, said openly (owner 17 Nov: "I liked the dark drawing style"; 8 h chosen from the search check below).
**Why:** real searches ("learn arabic while sleeping 7 hours / 8 hours", "…while you sleep (english - arabic)",
"arabic listening practice beginner"); long videos bring ~1 sub per 30 views vs ~1 per 60 for our best Shorts, and
watch hours count toward the 8,000. Source: learning/notes/2026-11-17-sanji-sleep-videos.md.
**No new recording:** all Arabic = the owner's (and Koki's) lines already in the pool; English = the owner's voice
clone (narrator-c2c, the 70/30 voice).

## Length: why 8 hours (search check, 17 Nov)

| Views | Length | Video |
|---|---|---|
| 4.8 M | 1.2 h | Arabic Shehab — "Learn Arabic while you Sleep (English - Arabic)" |
| 1.4 M | 3.0 h | Eko Languages — "Learn Arabic While You Sleep · 130 basic words and phrases" |
| 720 k | 8.0 h | Eko Languages — "Learn Arabic While You Sleep · most important phrases" (Eko's standard length) |
| 214 k | 7.0 h | Arabic Shehab — "Learn Arabic in 7 Hours" |
| 200 k | 7.8 h | Learn Arabic Language — "…While You Sleep" |

Autocomplete: "8 hours" in 4 of 5 lists, "7 hours" in 2. The wording matters more than the length → the searched
phrase "(English - Arabic)" goes first in the title.

## The 1-hour lesson (the master)

| Ch | Topic | ~lines | Night picture (one per chapter, see below) |
|---|---|---|---|
| 1 | Hello and first words | 25 | an old wooden door with a small lantern, at night |
| 2 | Introduce yourself | 25 | two empty chairs on a rooftop under the stars |
| 3 | The 5 questions + answers | 20 | a desk lamp over an open notebook and a pencil |
| 4 | Polite words: please, thank you, sorry | 20 | a bakery window, softly lit, street empty |
| 5 | Numbers 1–20 | 20 | a night sky full of stars over flat roofs ("count the stars") |
| 6 | Family | 20 | a small house with two warm lit windows |
| 7 | At the café | 25 | a closed café at night, chairs on the tables, one lamp on |
| 8 | I drink, I eat, I go | 25 | a quiet road with one street lamp |
| 9 | Finding your way | 25 | a narrow old street with arches and lanterns |
| 10 | The horse and the turtle (Story 1) | 25 | the turtle asleep under the tree, crescent moon above |

≈ 250 lines × ~14 s ≈ 58 min. Lines are picked from footage/recordings/*/map.json (the best take of each), short and
useful first; each line once per round.

**One line =** English (soft) → the Arabic → 3 s quiet → the same Arabic again → 2 s quiet.
**Chapter change =** a 2-second slow crossfade to the next picture + one soft English line ("Chapter 5: numbers.").
Opening (round 1 only): 15 s — "Close your eyes and just listen. You don't have to remember anything." No hook,
no stars, no sound effects, no subscribe animation, no ending line: round 8 fades out at the very end.

## The 8 rounds

| Rounds | Pace | Level |
|---|---|---|
| 1–2 | normal (as above) | −20 LUFS (quieter than our −14 videos — it's for falling asleep) |
| 3–8 | slower: 4 s + 3 s pauses, no chapter lines | −24 LUFS, the picture a little darker each round |

Rounds 3–8 are rendered once and copied (the same file 6×) — honest: the title and chapters say it repeats.

## The pictures (new, our pencil style — at night)

- **Style:** the same naive pencil drawing as our other pictures, but drawn **in white and pale-yellow pencil on dark
  navy paper** — like a night drawing: soft lines, a few warm colour touches (lamp light, the moon), no bright white
  areas. One picture per chapter (10) + 1 thumbnail picture, no people (the scene stays calm and nobody looks at you).
- **Motion:** a very slow zoom on each picture (about 3 % over the whole chapter) — nothing moves fast, no cuts.
- **Brightness:** the whole frame stays dark (checked: average brightness ≤ 15 %, no white flashes) so a phone or TV
  in a dark bedroom doesn't light the room.

## The text on screen

- Centre of the frame, over the picture: the **Arabic big** (cream colour, no harakat except where a word would be
  misread), the **transliteration** small under it, the **English** small and grey under that.
- A thin chapter name in the top-left corner ("5 · Numbers 1–20"); a small "Round 2 of 8" from round 2 on.
- From round 3 the text is dimmer too (the voice carries it; the screen is for the first rounds).

## Packaging

- **Title:** `Learn Arabic While You Sleep (English - Arabic) | 8 Hours, a 1-Hour Lesson Repeated` — the exact searched phrase first (it is the title of the most-viewed Arabic sleep video, 4.8 M)
- **Thumbnail:** the night window with a crescent moon and stars · big words **LEARN ARABIC WHILE YOU SLEEP** ·
  an **8 HOURS** badge · one small Arabic word: تصبح على خير (good night).
- **Chapters:** round 1 by topic (10 chapters), then "Round 2 (repeat)" … "Round 8 (slow, quiet)".
- **Description:** what it is in one line ("one hour of beginner Arabic, repeated 8 times — the later rounds slower and
  quieter"), the 10 topics, "Start from Day 1", the language line, 3 hashtags. AI label: No (owner's voice clone + real
  recordings). Playlist: Full Lessons. Related video: Episode 1 (Full Course).
- **Pinned comment:** "How far did you get before you fell asleep? 😴 Tell me which chapter."

## Build steps (after the owner's OK and his game)

1. Line list per chapter (text, no GPU) → owner can glance at it.
2. English narration for ~250 lines in the c2c voice (GPU, ~1.5 h).
3. 11 night pictures (GPU, ~30 min) → owner approves the pictures first.
4. Render the master hour + the slow round, copy to 8 h (CPU, ~1 h), check brightness/levels/chapters.
5. Upload sheet → owner uploads (~4 GB) → Claude fills; publish Sat 21 Nov 12:00.

**Verdict ~5 Dec:** watch hours, average view duration, subscribers, returning viewers → sleep02 (14 Dec) or not.
