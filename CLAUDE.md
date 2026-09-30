# 2 Minute Arabic — how we work

The owner records Arabic, uploads, and sends Studio screenshots. Claude does everything else and drives the flow:
the owner never has to name a skill. At the start of a session, check the **calendar** below and mention anything due.

## The flow (skills in `.claude/skills/`, chained by Claude)

| Owner says / sends | Claude runs |
|---|---|
| "next", "what's next", "plan the week" | **plan-lessons** → next 3–5 days + Extras, one batched recording sheet |
| a recording (Voice Memos file, sent as a document) | **produce-day** / **arabic-extras** → split, voice, images, assemble, checks |
| (automatically, every finished video) | **pre-upload-gate** → SHIP / FIX / KILL, then **upload-handover** (sheet opened with `code -r`) |
| every 5th day done | **compile-part** (Part N, 16:9, quiz from recorded lines) |
| Studio screenshots, comments, "how are we doing" | **channel-review** → report + max 5 next actions |

YouTube API: `~/.local/share/2min-yt/venv/bin/python tools/youtube_api.py` (videos, stats, retention, search-terms,
comments, fill). Secrets in `~/.config/2min-youtube/` (never in git). Testing mode → login expires weekly: re-run
`login` and send the owner the link (brand account **2 Minute Arabic**, not "Glorious Victorious").

Always end a hand-over with **what's next for the owner** (record / upload / screenshots) so nothing stalls.

## Calendar (keep it current)

- **Weekly (Sunday):** channel-review — ask for the screenshots.
- **2026-10-06:** verdict on the "viral shorts" tag experiment (Days 3/5 vs 2/4) → docs/06.
- **48 h after each Short:** if ~0 views, re-upload with a backup title (pre-upload-gate writes them).
- **After Day 10:** Part 2 (Days 6–10).
- **Next up (2026-09-30):** Extras x01 hello / x02 goodbye in production; then plan Days 6–10.

## Rules that are easy to forget

- All Arabic = real recordings (owner; Lina = Koki). No Arabic TTS, no voice conversion. English = owner's clone.
- Voice references and recordings are private: never committed, never shared.
- Uploads in day order. Automatic dubbing OFF. No hashtags in titles. Arabic in descriptions inside U+2067…U+2069.
- Never buy views/subs or use engagement groups; never use third-party or watermarked footage (docs/11).
- Stop ComfyUI by PID; set LD_LIBRARY_PATH for Whisper (final_check.py does it itself).
- Details: docs/02 format · 04 curriculum · 05 style · 06 publishing · 07 monetization · 10 production · 11 policy.
