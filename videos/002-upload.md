# Day 2 — Upload sheet

**File to upload:** `output/002-10-most-useful-phrases/002-10-most-useful-phrases.mp4`
(1:58, vertical → published as a **Short**; −14 LUFS; captions burned in; your real hello + goodbye clips inside;
our own animated SUBSCRIBE + bell over the goodbye)
**Thumbnail/cover:** `output/002-10-most-useful-phrases/thumbnail (vertical).jpg` — if the upload screen only allows picking
a frame, pick **0:02** (Sami and Lina at the café).

## Title

```
10 Arabic Phrases You'll Use Every Day | Day 2 · 2 Minute Arabic
```

## Description

> ⚠️ Use [002-description.txt](002-description.txt) (Arabic kept in order with direction markers) instead of the block below.

```
Day 2 of 30 — the 10 Arabic phrases you'll use every single day.

Two minutes a day. Your first Arabic conversation in 30 days.

📝 Today's Arabic:
1. السَّلَامُ عَلَيْكُمْ — as-salaamu 'alaykum — peace be upon you (hello)
2. وَعَلَيْكُمُ السَّلَامْ — wa 'alaykumu s-salaam — and upon you, peace (the reply)
3. كَيْفَ حَالُكْ؟ — kayfa haaluk? — how are you? (to a woman: kayfa haaluki?)
4. بِخَيْرْ، الْحَمْدُ لِلَّهْ — bikhayr, al-hamdu lillaah — fine, thank God
5. شُكْرًا — shukran — thank you
6. عَفْوًا — 'afwan — you're welcome
7. مِنْ فَضْلِكْ — min fadlik — please
8. مَا اسْمُكْ؟ — maa smuk? — what's your name?
9. اسْمِي ... — ismii ... — my name is ...
10. لَا أَفْهَمْ — laa afham — I don't understand

▶️ Start from Day 1: <playlist link>
🔔 Subscribe so you don't break your streak.

#learnarabic #arabicphrases #2minutearabic
```

## Tags

```
learn arabic, arabic phrases, arabic for beginners, basic arabic phrases, arabic greetings, how to say thank you in arabic, modern standard arabic, fusha, speak arabic, 2 minute arabic
```

## Settings

| Setting | Value |
|---|---|
| Playlist | 30 Days to Your First Arabic Conversation |
| Audience | No, it's not made for kids |
| **AI use** ("Was AI used…") | **No** — only your own voice (cloned) + illustrations; no one else's voice |
| Category / language | Education / English |
| Caption certification, recording date/location | None / empty |
| License, embedding, notify subscribers | Standard / ✅ / ✅ |
| Automatic chapters / featured places / concepts | ✅ / ❌ / ❌ |
| Visibility | **Schedule: the day after Day 1, 16:00 Oslo time** |
| Related video | **Day 1** |
| Type | Concept overview |

## Subtitles (for auto-translation into any language)

Studio → the video → **Subtitles** → **Add language: English** → **Upload file** → **With timing** →
`output/002-10-most-useful-phrases/captions-upload.srt` → **Publish**.
Viewers can then use CC → ⚙️ → Auto-translate (Spanish, French, …). Your audio is never changed.

## Pinned comment

```
Day 2 ✅ — introduce yourself in Arabic below: اسْمِي … (ismii …) 👇
```

## Quality check (done by Claude before hand-over)

- **Voice:** every line generated 3× (hard lines 8×) and checked by speech-to-text — all lines heard exactly as written.
  عَفْوًا was flagged by the checker ("اف 1" — it hears "af-**wan**" as English "one"); verified correct in context
  ("شكرا عفوا"). Report: `audio/002-10-most-useful-phrases/report.md`.
- **Voice rules applied:** sukun on the last letter, neutral intonation, 5% slower.
- **Images:** 3 takes per scene, every take inspected; 2 scenes redone (8, 11), 1 take rejected for an ambiguous extra hand.
  Choices and reasons: `images/002-10-most-useful-phrases/picks.json`.
- **Final video:** 1:58.5 · −14.0 LUFS · peaks −1.9 dB · all text cards checked for missing glyphs · full soundtrack
  re-transcribed: no overlaps.
- **Round 2 fixes (owner's review):** Arabic noise (noisy voice reference → cleaned with DeepFilterNet; Arabic lines now
  have less hiss than the English) · filmed clips denoised · dragged/fading sentence endings rejected and trimmed ·
  line after the hello rewritten so it continues naturally · subscribe animation added (the supplied stock clip was an
  iStock watermarked preview — not usable).

## Version 2 (2026-09-28) — owner's recorded Arabic

- **Only the Arabic changed:** all 10 phrases are the owner's own recording (iPhone, cleaned, presence EQ).
- **English unchanged:** the 16 English lines are the exact published takes (`make_audio.py --voice narrator=owner-en-2`,
  0 new lines generated).
- Longer subscribe animation (click + ding) during the last narrator sentence.
- Checked: 1:58.3 · −14.0 LUFS · peaks −1.9 dB · transcribed EN + AR: right order, no overlaps.
- **AI use: No** (unchanged).
- Replacing the published video = delete + re-upload (YouTube can't swap the file); views/comments on the old upload are lost.
