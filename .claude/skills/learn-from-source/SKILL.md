---
name: learn-from-source
description: Learn from a file the owner provides for 2 Minute Arabic — a video, podcast, audio, article, PDF or screenshot about YouTube growth, Shorts, teaching, scripting or production — by transcribing it, extracting its claims with timestamps, checking every claim against the channel's own analytics, and turning what survives into concrete proposals, doc updates or new skills. Use this whenever the owner drops a file "to learn from", says "listen to this / watch this / read this and learn", mentions a creator's advice (e.g. Danny Why), or asks what we can apply from some content — even if he doesn't say "learn".
---

# Learn from a source

The owner sometimes hands over content about YouTube or teaching. The goal is not a summary: it's **what changes on our
channel**, backed by **our own numbers**. Advice is a hypothesis; our analytics decide.

## Steps

1. **File it.** Move the file to `learning/sources/` (audio/video are git-ignored; keep the original name).
2. **Transcribe** (audio/video) with the TTS venv's faster-whisper, timestamps per segment:
   ```
   TTS=/media/msn/GamesLinux/AI/tts/venv/bin/python   # set LD_LIBRARY_PATH like final_check.py does
   WhisperModel("medium", device="cuda", compute_type="float16").transcribe(src, language=…, vad_filter=True)
   ```
   → `learning/sources/<slug>.transcript.txt` (`[mm:ss] text`). Text/PDF/screenshots: read directly.
3. **Read all of it**, then note who it is, the format it talks about (Shorts vs long-form!), and any **bias**
   (sponsorships, selling a course, one lucky channel).
4. **Extract claims** (numbered, each with a timestamp). Skip filler and the sponsor segment's claims about its product.
5. **Check every claim against our data**: `youtube_api.py stats / retention / search-terms`, docs/12 (review tables),
   docs/06 Learnings. Verdict per claim: *matches* · *already done* · *contradicted by our data* · *can't tell yet*.
   Our numbers are small — say "hint" when they are.
6. **Turn the survivors into actions**, each one concrete (which file/skill/script changes, from which video on).
   Anything that changes the **format, the voice, what the owner records, money or public accounts → proposal for
   the owner**, never applied silently. Pure process improvements → apply and say so.
7. **Write the note** `learning/notes/<date>-<slug>.md`: source + bias, claims, the evidence table, what we change.
   Add a line to `learning/README.md` (newest on top) and to "Ideas adopted" once the owner agrees.
8. **Feed it back:** adopted rules go into the right skill (produce-day, pre-upload-gate, plan-lessons, …) with
   "(source: learning/notes/…)"; a new repeatable workflow can become a new skill (skill-creator). Learnings that our
   data confirms on ≥ 2 videos also go into docs/06 `## Learnings (dated)`.

## Never

Adopt a tool because a source sponsors it (licence + no-paid-tools rules) · copy a creator's content · chase "viral"
tricks that conflict with docs/11 (policy) · treat one creator's anecdote as proof over our own analytics.
