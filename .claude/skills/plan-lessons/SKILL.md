---
name: plan-lessons
description: Plan the next 2 Minute Arabic lessons and Arabic Extras before any script is written — the curriculum day and format, 5–8 new words, 2–3 earlier words that are due again (spaced repetition), the "Your turn" recall item, due words for the next review quiz or Part, a distinct hook per day, batched recording sessions, and an Extras calendar between days. Use this whenever the user asks what's next, to plan the week, the next days or Days N–M, to plan extras or bonus Shorts, when comments suggest topics, or before produce-day starts a day that has no plan yet, even if they don't say "plan".
---

# Plan lessons and Extras

The curriculum (`docs/04-curriculum-30-days.md`) is the backbone. Change a day's topic or words only with the
owner's OK. This skill adds three things the table doesn't have: **which old words come back when**, **how each day
stays different**, and **when the Extras go out**. Plan 3–5 days at a time. That also batches the owner's recording
into one session.

## 1. The vocabulary ledger — `docs/13-vocabulary-ledger.md`

One row per word or phrase:

| Arabic (tashkeel, final sukun) | Translit | English | Introduced | Re-used on | Next due | Recorded clip |
|---|---|---|---|---|---|---|

- If the ledger doesn't exist, build it from the scripts: the **New words** header row plus every Arabic
  `🔤 On screen` card (Day 2's header only says "the 10 phrases below"). "Recorded clip" = the line exists in some
  `footage/recordings/<day>/map.json`, so a quiz can re-use it with nothing new to record.
- Update it whenever a day's script is final.

## 2. Spacing (which old words come back)

We can't measure each viewer's recall, so we use fixed expanding gaps. A word introduced on Day d is **due on
d+1, d+3, d+7 and d+14**, and every core word comes back on Day 30.
- **d+1:** the "Today…" scene recalls yesterday (as Day 5 did with سَامِي حَزِينْ).
- **Every day re-uses 2–3 due words inside the new material**: a line in the conversation, a story sentence, an
  example for the grammar rule. They are not a separate list. The cards show them as known, not "NEW:".
- **Signals that reset a word to "due tomorrow":** comments that get it wrong or ask about it, or a retention drop at
  its ⏸️ pause (from channel-review).
- If a day has more due words than it can hold, the oldest and the most useful for the Day-30 conversation win. The
  rest move to the next quiz.

## 3. Active recall

- Every day's **Your turn** asks for at least one **earlier** word: an English prompt → ⏸️ pause → the Arabic answer.
  The viewer retrieves before hearing it.
- **Review days (7, 14, 21)** and **Part quizzes** (after Days 5, 10, 15 …) draw on the words that are due, **mixed
  across days and formats**, not in day order. The Part quiz takes answers that have a recorded clip (compile-part
  rule). The review Short and the Part quiz covering the same days use **different questions**.

## 4. Keep every lesson different (inauthentic-content policy, docs/11)

For each planned day, check against the previous 3:
- **Format** (phrases / conversation / story / grammar / review / challenge): never the same twice in a row. Where
  docs/04 has two in a row (Days 22–23 Phrases, 28–29 Conversation), give the second a different inner shape, e.g. a
  mini-game, "wrong vs right", or a situation with Sami or Lina.
- **Hook shape** (contradiction · challenge · mistake · number · story-open), **title formula** and **thumbnail
  wording**: none repeats the previous day's.
- **Real people:** the owner's hello and goodbye clips, Koki's Lina lines where the scene has a woman, and a planned
  on-camera moment at least once per Part (docs/11). Never invent a personal anecdote for the host.

## 5. Hooks

For each day, write 2–3 hook lines (English narrator, ≤ 2 s to the point, no greeting) that the video can **keep**
(pre-upload-gate, gate 3). For example:
- *"Arabic has no word for 'is'."*
- *"Can you understand this story? Only 12 words."*
- *"Don't say أَنْتَ to a woman."*
- *"Sami walks into the café. It's closed."*

## 6. Extras calendar

30–60 s bonus Shorts (arabic-extras skill, `x0N-` stems). They go **between** days and never replace a day. The daily
16:00 Oslo slot stays the lesson's.
- **1 per week** to start (2 at most while the channel is new). The course is the core, and the cadence must be one the
  owner can hold for months: sustainable beats ambitious. Each Extra points back to the course (related video = Day 1,
  or the day whose words it re-uses).
- Pick topics that **re-use the week's due words** (a free review), evergreen search phrases ("how to say thank you
  in Arabic"), or a comment idea with a quoted comment behind it (channel-review §5).
- Dialect only here, labelled. Check which Extras are already in progress (x01 hello / x02 goodbye:
  `videos/_x0102-combined.md`).
- **Batch the recording:** put each Extra's lines in the same sheet as the next days' (like `_345-combined`,
  `_x0102-combined`), so the owner records once.

## Output

Show this in the chat for the owner's OK:

| Day | Format | Topic | New words (5–8) | Re-used, due (2–3, Day introduced) | Your turn (recall) | Hook options | Title idea | Thumb text |
|---|---|---|---|---|---|---|---|---|

Then the **Extras calendar** (slot · stem · topic · why now · words), the **quiz list** for the next review day or
Part (words and questions, each with its recorded clip), and the **recording session** (which days and Extras share
one sheet; Koki's lines separately).

After the OK:
- update docs/04 rows that changed, and the ledger's "Next due";
- put **New words** and a **Re-used** row into each script's header when produce-day writes it.

---
Credits: spacing and active-recall ideas adapted from m98/fluent (SM-2, fluent-review); calendar, series and hook ideas
from AgriciDaniel/claude-youtube (calendar, hook) and sergebulaev/youtube-skills (yt-hook-scripter,
yt-content-planner) — all MIT.
