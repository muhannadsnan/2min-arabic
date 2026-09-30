---
name: pre-upload-gate
description: Run the SHIP / FIX / KILL pre-upload gate on a finished 2 Minute Arabic video (Day, Part or Extra) before its upload sheet is handed over — hook in the first 2 s, title + thumbnail pair, packaging promise kept, length, ending/loop, not-interchangeable check, and our metadata rules (no hashtags in titles, 3-group tags, ~3 hashtags, Arabic in direction isolates) — plus 3 backup title/thumbnail-text pairs. Use this every time a video is finished, before the upload-handover hand-over, and whenever the user asks "is it ready?", "check it before I upload", "better title?", "is this clickbait?" or needs a new title for a re-upload, even if they don't say "gate".
---

# Pre-upload gate (SHIP / FIX / KILL)

The owner watches a finished video once and uploads it. This gate is the last look before that: short, honest, and
done by Claude. Run it after `final_check` passed and the thumbnail and the upload sheet exist, and **before** the
upload-handover hand-over. Our rules (docs/06, docs/11) beat any generic YouTube advice.

## Inputs

The script `videos/<stem>.md` · the `final_check` output (length, transcript with timings) · `check-frames.png` and
`contact.png` · the thumbnail's `-phone-size.png` · `videos/<stem>-upload.md` + `-description.txt` · the scripts and
sheets of the **last 3 published or ready videos** (for gate 6).

## The 7 gates

Each gate is PASS or FAIL. Every FAIL gets **one fix, written as a command** ("Rewrite the hook line as …").

1. **Hook (0–2 s).** The first spoken line and the first card state the payoff or a tension. No greeting, no "today
   we'll learn", no logo before it. The card works muted. The hello clip comes *after* the hook.
   Pass: *"Arabic has no word for 'is'."* Fail: *"In this lesson we'll look at pronouns."*
   Fix without the owner: re-voice line 1 (`make_audio.py --redo 1`) and re-assemble. It's the English narrator, so no
   new recording is needed.
2. **Title + thumbnail pair.** The title follows the pattern `<benefit> | Day N · 2 Minute Arabic` (Parts
   `… | Part N · Days a–b`, Extras `… | Arabic Extras`). The benefit part is ≤ 50 characters and has a concrete noun or
   number. The thumbnail has 3–4 words max, **adds** to the title instead of repeating its words, has one focal
   point, a big Arabic word and the DAY N badge, and is readable in the phone-size preview.
3. **Promise kept.** Everything the title, thumbnail and hook claim happens in the video, and the payoff starts within
   ~20 s (the "Today…" scene). The thumbnail image is a scene from this video, and its emotion matches. No shock, no
   fake stakes, no "fluent in 2 minutes". If a claim is only half true, change the words, not the video.
4. **Length.** Day 2:00–2:40 (never over 2:59). Extra 30–75 s. Part ≈ 10–12 min. Read it from `final_check`.
5. **Ending / loop.**
   - **Day:** "Day N done — tomorrow: …" teaser → "Subscribe so you don't break your streak." (its own block) →
     goodbye clip. Nothing after the goodbye, and no long silent tail.
   - **Extra:** the last line may point back to the hook so a re-watch feels natural (e.g. the hook asks "number 7?"
     and the ending answers it). Always the goodbye + subscribe line.
   - **Part:** the end screen and the playlist card are in the sheet.
6. **Not interchangeable** (inauthentic-content policy, docs/11). Compare with the last 3 videos: different format or
   topic, a different hook shape, a different title formula and different thumbnail wording. FAIL if it would feel
   like "the same video again", e.g. a third "X?!" thumbnail in a row, or the same list shape two days running.
   Real voices (owner, Koki) carry all the Arabic.
7. **Metadata rules.** Run the helper:
   ```
   python3 .claude/skills/pre-upload-gate/check_metadata.py <stem>     # e.g. 006, w02, x01
   ```
   It checks: no hashtags in the title, benefit ≤ 50 characters, series suffix, Arabic at line end inside
   U+2067…U+2069, 2–3 hashtags, no `?si=`, description.txt identical to the sheet's box, 9–14 tags ≤ 500 characters,
   and that the AI use / related video / playlist / not-for-kids lines are present. Then check by eye what a script
   can't:
   - the tags follow the 3-group formula: video-specific · niche · broad;
   - no misleading tags (`syrian arabic` only on dialect Extras);
   - `viral shorts` only per the running experiment (Days 3/5 until the 2026-10-06 verdict, then whatever docs/06
     says);
   - AI use is decided correctly (No = only the owner's and Koki's real voices + the owner's own clone);
   - the sheet reminds that **automatic dubbing stays OFF**.

## Verdict

- **SHIP**: 7/7. Hand over via upload-handover.
- **FIX**: any fail that can be fixed today without the owner (title, thumbnail text, tags, description, re-voicing
  the hook, a trim). Fix it, re-run the failed gates, then SHIP. Don't hand over a FIX.
- **KILL**: gate 3 or 6 fails at the **content** level (the video can't keep its promise, or it is interchangeable
  with a recent one), or the length can't be fixed with a trim. Don't upload it. Say plainly why, name the one change
  (back to produce-day), and tell the owner which day slips. Uploads go in day order, so a KILLed day holds up the
  days after it.

Never pad the verdict. A "SHIP" with a doubt in it is a FIX.

## Backup titles (always)

Write **3 alternative title + thumbnail-text pairs**. Each uses a different formula:
- curiosity or contradiction (*Arabic Has No Word for "Is"*);
- number or list (*10 Arabic Phrases You'll Use Every Day*);
- challenge (*Can You Understand This Arabic Story?*);
- mistake (*Don't Say This to a Woman in Arabic*).

Each must pass gates 2 and 3. Tag each pair with its formula and benefit-part character count, and mark the one you'd
lead with. They go at the bottom of the upload sheet under `## Backup titles`, because the 48-hour rule (a Short still
at ~0 views → re-upload with a new title) and Studio's Test & compare for Parts need them ready.

## Output (in the chat, and one line in the sheet's Quality check)

```
Gate: SHIP 7/7 — <stem>, <date>
1 Hook ✅ "…" (ends 3.1 s) · 2 Pair ✅ · 3 Promise ✅ · 4 Length ✅ 2:11 · 5 Ending ✅ · 6 Distinct ✅ (vs 003–005) · 7 Metadata ✅
Fixes: none
```

---
Credits: adapted from ravsau/youtuber-skills (youtube-virality-gate, youtube-packaging, youtube-shorts),
sergebulaev/youtube-skills (yt-title-optimizer, yt-thumbnail-brief, yt-hook-scripter) and AgriciDaniel/claude-youtube
(shorts, metadata, hook) — all MIT.
