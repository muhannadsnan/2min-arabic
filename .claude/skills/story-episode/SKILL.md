---
name: story-episode
description: Make the monthly STORY video of 2 Minute Arabic — a 16:9 long video (12–15 min) that re-uses the month's best words in an animal mini-story: the story read in full, then sentence by sentence with many easy logical questions, word pairs (a word + its opposite), the story in the past, the story in the future — drawn-and-painted drawing-book pictures, Arabic without tashkeel, the narrator full screen between the story parts, 5 chiming stars, and 3–4 Shorts cut from it. Use this whenever the owner mentions the monthly story, a story video, animal story, "story for beginners", the monthly top video, or the video that extends the Episode, even if he doesn't say "story".
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
  white space beside it, one by one, as **one bullet list on the right — no borders, close together, a different colour
  per word, and the word lights up in that same colour in the sentence** (owner 2026-11-03; past/future: "يذهب ← ذهب" — the present grey, the new form + its English in the word's colour: grey always means the present).
  **Only the important words pop — verbs and the small words (here, too, because, before, after, with, under, while,
  not, slowly); no names or nouns.** The list RUNS across sentences: up to 5, the 6th clears it; a word already in the
  list only lights up again. A talk/pair/camera view clears it. A full list hangs ≥ 2 s and fades before the 6th comes.
  **LEFT list = the opposites** (spec `opposites`: سريع ↔ بطيء, قبل ↔ بعد, مع ↔ بدون, ينام ↔ يستيقظ, هنا ↔ هناك —
  owner 2026-11-03), popping the first time either word is said, each English word centred under its own Arabic word (here under هنا — owner 2026-11-03); same running rules; opposite words never go on the right, which keeps the other verbs and small words.
  **Sound (owner 2026-11-03: "the chimes make an annoying echo"):** loudness = ONE gain for the whole track + a peak
  limiter — never dynamic `loudnorm`, which pumped the gain up again inside the chime's tail (a swell 0.7 s later =
  the echo). Also no pop sound within 1.2 s of a star chime. the sentence being read sits under the picture; the
  narrator appears alone full screen for explanations. **No narrator square over the story (owner 2026-11-03: "just
  disturbing to the learner" — the learner keeps their eyes on the story; maybe back after the recording, `--square`).**
**Harakat rule (owner 2026-11-03):** Arabic for learners is shown WITHOUT harakat, except where the plain word would be read as another word (مَن/مِن, أنتَ/أنتِ, final ـكِ) — `tools/arabic_text.py minimal()` for every card, slide and caption from Month 2 on (published videos stay).
- **Arabic on screen without tashkeel** (beginner text); add a vowel only where a word would be misread.
- **Questions are the heart:** many easy, logical questions per sentence, asked in different ways — who…? who is X?
  is X a cat? where does X go? what does X do? is X fast? why? is Y fast like him? how does Y walk? what did Z say?
  coffee or tea? did he keep walking? who sleeps — Hani? did X say "very good"? who arrived first? did X arrive before
  Y? why? — pause after each, then the answer. This is the owner's story-telling signature for beginners.
- **5 stars** at the top left (84 px — owner 2026-11-04: bigger), one chimes in after each section: ① the story read the first time (early, to motivate)
  ② the questions ③ the word pairs ④ the past version ⑤ the future version.

## Voice + presenter (owner 2026-11-03)
- **The owner narrates the whole video in simple, slow Arabic** (comprehensible-input style) — no AI voice; English
  subtitles on screen for everything. The recording sheet is the whole video in order (`videos/_sNN-whatsapp.txt`):
  🎥 filmed intro, 🎙️ narration, 📖 story lines, 🎥 filmed outro.
- **After his filmed intro, the 3D-film narrator (library/work/narrator/film3d/set, logo assets/logo-3d-narrator-1024.png; clay retired 2026-11-04) continues as him:** full screen
  when he explains (no story sentence on screen), from time to time; NOT on screen while a story sentence is shown (square
  off since 2026-11-03, see above). His filmed outro closes it.
- **Narrator v2 (owner 2026-11-03: first test had a "shadow of the mustache" round the mouth and frozen fists — "very
  unnatural"):** full screen = HALF-BODY set `library/work/narrator/film3d/set/` — **3D animated-film look, early 30s** (owner 2026-11-04, approved after the talking test: the clay one looked ~50; he is in his 30s; old clay set: `narrator/half/set/`; options tried: library/work/narrator/styles/) — arms down, cut above the hands, small square (only with `--square`) = close-up set `library/work/narrator/set/` (NO hands; mouths + blink **inpainted inside the still** with
  `tools/images/generate.py --mask`, so the beard never changes) rendered by `tools/animate/narrator.py` — mouth follows
  the voice's loudness, breathing, slight sway, head lifts on stressed syllables, a blink every 2.5–5 s.

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

Keep every section short (≤ 3–4 min) and change the view every few seconds (picture ↔ narrator full ↔ word pop-ups) — no boring stretches.

## Production
- Script `videos/sNN-<slug>.md`, recording sheet `videos/_sNN-whatsapp.txt` (story lines, questions, answers, word
  examples, past, future — one line each; the fox/bird quotes in a character voice).
- Pictures: `library/work/storyNN/` via tools/images/generate.py `--no-style` + the style text in this skill.
- Layout + pop-up words + 5 stars (`--square` brings back the narrator square — off by default): `$TTS tools/story_episode.py videos/sNN-story.json output/sNN-story/sNN-story.mp4`
  (built 2026-11-03 with story 1). The spec lists segments in video order — camera · talk · story (words / verbs / replay) ·
  qa ("question … answer") · pair · star — with the English per line. `--preview` = placeholders before the recording
  (layout check), `--from/--to` = a part. Clips: the recording cut by split_recording.py into `footage/recordings/sNN/lines/NN-*.wav`
  (NN = the sheet's line number); the filmed intro/outro: `footage/recordings/sNN/intro.mp4`, `outro.mp4`. Renders ≈ 2× real time (CPU only).
- Shorts (vertical): the story · "can you answer these 3 questions?" · present → past · the future.
- Then pre-upload-gate + upload-handover as usual (playlist "Arabic Stories", Related = the month's Episode).

## Story Shorts — the template (owner approved 2026-11-11, Story 1 → 5 Shorts)

After the long story video, cut **5 vertical Shorts** from it — new material for the Shorts tab, never a crop of the
16:9 frames. `tools/story_episode.py videos/sNN-story.json output/<stem>/<stem>.mp4 --vertical --ranges "a-b[,c-d]" [--heading "TITLE|subtitle|Arabic"]`
(library/work/story-shorts.sh is the Story 1 example). Topics that worked: ① the story (the hook line + all sentences)
② the comprehension questions of the ending ③ the opposites ④ the past ⑤ the future. Titles from real searches
("arabic short story for beginners", "arabic opposites", "past/future tense in arabic"); thumbnails "STORY N" +
2–3 big words (MINI STORY IN ARABIC · UNDERSTAND ARABIC STORY / EASY QUESTIONS · OPPOSITES IN ARABIC · PAST TENSE · FUTURE TENSE).

Layout rules (all from the owner's rounds of feedback — keep them):
- **3 stars** close together at the very top; chimes at ⅓, ~57 % and 6 s before the end.
- **Popping words as LISTS in columns** right under the stars, staying to the end: opposites on the right, the other
  words / verbs on the left (past/future: only the verbs); the block centred; big text, translations in **black**.
- **The picture full width** (paper border trimmed, never side margins) in the lower half; a big list pushes it down,
  and it trims up to 12 % of its own height before it would ever shrink; ≥ 400 px kept for the subtitles and a small
  margin at the bottom.
- **Sentence under the picture:** Arabic then English, plain (no card). Two lines only when needed, broken where it
  reads well — after . ، : ; if there is one, else at the most even point — never one word alone.
- **Presenter parts:** text above him, never on his face; a pair = two cards centred as a group, arrow between.
- **Pace:** pauses between sentences cut, pauses inside a sentence halved, nothing longer than 1 s (a question's
  thinking pause included). Cuts on whole frames (sound stays in sync).
- **Openings:** the hook in Arabic + English (Short 1, no frames of the filmed face after it); a big heading for the
  grammar Shorts (OPPOSITES · PAST TENSE … ); drop a filler first word ("رائع!", "الآن") — start on the content.
- Captions come from the same run (`--captions` with the same --ranges) on the cut timeline.
