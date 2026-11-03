---
name: story-episode
description: Make the monthly STORY video of 2 Minute Arabic — a 16:9 long video (12–15 min) that re-uses the month's best words in an animal mini-story: the story read in full, then sentence by sentence with many easy logical questions, word pairs (a word + its opposite), the story in the past, the story in the future — drawn-and-painted drawing-book pictures, Arabic without tashkeel, the narrator in a small square, 5 chiming stars, and 3–4 Shorts cut from it. Use this whenever the owner mentions the monthly story, a story video, animal story, "story for beginners", the monthly top video, or the video that extends the Episode, even if he doesn't say "story".
---

# Monthly story video (owner 2026-11-03 — docs/22-monthly-story-video.md)

The Episode teaches the month's lessons; the story video **re-uses the month's best words in a new shape**. Long
videos bring ~3× more subscribers per view than Shorts (Parts 3.1 vs Shorts 0.9 per 100 views, Oct 2026), and 3–4
Shorts cut from it promote it and fill days.

## The signature (owner's words — keep it every month)
- **Simplicity is the key and the signature.**
- **Pictures:** drawn and painted in a drawing book — a children's picture-book look, pencil + soft watercolour; the
  **centre is detailed and colourful and fades out to sketchy lines and bare white paper** at the edges. One picture
  per story sentence, the same animal characters every time (a name each: رامي الحصان, ماهر السلحفاة …).
  Clean animals only (horse, sheep, camel, fox, turtle, rabbit, birds — no dogs, no pigs). Every picture checked at full
  size (faces, legs, paws; a hand only if a human appears).
- **The white space is the stage:** while a sentence is read, its key Arabic words pop up **outside the picture**, in the
  four spots (left, right, top, bottom), one by one, then fade; the sentence being read sits under the picture; the
  narrator appears in a **small square** in a corner some of the time, or alone full screen for explanations.
- **Arabic on screen without tashkeel** (beginner text); add a vowel only where a word would be misread.
- **Questions are the heart:** many easy, logical questions per sentence, asked in different ways — who…? who is X?
  is X a cat? where does X go? what does X do? is X fast? why? is Y fast like him? how does Y walk? what did Z say?
  coffee or tea? did he keep walking? who sleeps — Hani? did X say "very good"? who arrived first? did X arrive before
  Y? why? — pause after each, then the answer. This is the owner's story-telling signature for beginners.
- **5 small stars** at the top, one chimes in after each section: ① the story read the first time (early, to motivate)
  ② the questions ③ the word pairs ④ the past version ⑤ the future version.

## Voice + presenter (owner 2026-11-03)
- **The owner narrates the whole video in simple, slow Arabic** (comprehensible-input style) — no AI voice; English
  subtitles on screen for everything. The recording sheet is the whole video in order (`videos/_sNN-whatsapp.txt`):
  🎥 filmed intro, 🎙️ narration, 📖 story lines, 🎥 filmed outro.
- **After his filmed intro, the clay teacher (assets/logo-clay-teacher, talking mouth sets) continues as him:** full screen
  when he explains (no story sentence on screen); in a **small square** while a story sentence is shown. His filmed outro closes it.

## Shape (≈ 12–15 min, 16:9)
1. **Hook (≤ 20 s):** the ending first (the surprise), and the promise: "by the end you'll tell this story in Arabic —
   in the past and in the future."
2. **The full story, read once** in Arabic (owner), pictures + words popping up outside the frame. ⭐1
3. Narrator: "Now let's go through it sentence by sentence and understand every word."
4. **Sentence by sentence + questions** (the owner asks in Arabic, pause, short answer). ⭐2
5. **Word pairs — a word and its opposite** (easier to remember together): سريع/بطيء, قبل/بعد, مع/بدون … each: what it
   means, when, where and with whom you use it, two short examples. ⭐3
6. **The story in the past** — same pictures; each changed verb highlighted (يذهب → ذهب). ⭐4
7. **The story in the future** — سـ + the verb (سيذهب). ⭐5
8. Outro: "tell the story in the comments", subscribe, Episode link. No goodbye clip needed.

Keep every section short (≤ 3–4 min) and change the view every few seconds (picture ↔ narrator square ↔ narrator
full ↔ word pop-ups) — no boring stretches.

## Production
- Script `videos/sNN-<slug>.md`, recording sheet `videos/_sNN-whatsapp.txt` (story lines, questions, answers, word
  examples, past, future — one line each; the fox/bird quotes in a character voice).
- Pictures: `library/work/storyNN/` via tools/images/generate.py `--no-style` + the style text in this skill.
- Layout + pop-up words + narrator square + 5 stars: tools/story_episode.py (built with story 1; 16:9).
- Shorts (vertical): the story · "can you answer these 3 questions?" · present → past · the future.
- Then pre-upload-gate + upload-handover as usual (playlist "Arabic Stories", Related = the month's Episode).
