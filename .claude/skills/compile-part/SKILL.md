---
name: compile-part
description: Build a horizontal 16:9 "Part" compilation for 2 Minute Arabic (every 5 days — Days 1–5, 6–10, …) with a new review quiz, side panels, chapters, captions, a wide thumbnail and the upload sheet. Use this whenever the user mentions a Part, weekly/long video, compilation, review video, or after every 5th day is finished.
---

# Compile a Part (every 5 days)

Why it exists: only long-form watch time counts toward monetization, and reused content is only allowed when we add
something substantial — so every Part **must** carry new material (at minimum the review quiz) and never anyone
else's footage. See `docs/06-publishing.md` (Part compilations) and `docs/11-monetization-policy.md`.
Template: Part 1 = `videos/w01-review.md` + `parts/part-01.json` + `videos/w01-upload.md`.

## Steps

1. **Review script** `videos/wNN-review.md`: short welcome, quiz intro, ~12 quiz questions (English question →
   ⏸️ pause → the Arabic answer), outro. **Re-use recorded Arabic only** — pick answers whose lines exist in the
   days' `footage/recordings/<day>/map.json`, then build `footage/recordings/wNN-review/map.json` pointing at those
   files. Nothing new to record. Images: `"same"`/`"from"` links to the days' images.
2. `python3 tools/make_audio.py videos/wNN-review.md` → `python3 tools/assemble.py videos/wNN-review.md`
   (badge becomes "PART N · DAYS a–b") → `$TTS tools/sync_captions.py videos/wNN-review.md --video output/wNN-review/wNN-review.mp4`.
3. **`parts/part-NN.json`**: segments in order — welcome (review 0 → quiz start), each day cut from its "Today…"
   scene to before its outro/subscribe/goodbye (find the times in `audio/<day>/timeline.json`), then the quiz and
   outro. Each segment has `title`, `file`, `start`, `end`, `words` for the side panel; add `"srt"` when the source
   captions aren't at `output/<video>/captions-upload.srt` (e.g. a filmed day).
4. `python3 tools/compile_part.py parts/part-NN.json` → `.mp4`, `chapters.txt`, `contact.png`.
   Then `python3 tools/part_captions.py parts/part-NN.json` → `captions-upload.srt`.
5. **Check**: `$TTS tools/final_check.py output/<part>/<part>.mp4 --frames …` (pick a frame in every chapter);
   joins are clean, no overlaps, current chapter highlighted, words panel right, no □ glyphs. Length isn't capped
   (≈10–12 min), loudness −14 LUFS, peak < −1 dB.
6. **Thumbnail**: `python3 tools/thumbnail.py <image> "output/<part>/thumbnail.jpg" --wide --badge "DAYS a–b"
   --line1 … --line2 … --line3 … --arabic …` and check the phone-size preview.
7. **Upload sheet** via the upload-handover skill, including chapters from `chapters.txt` in the description and the
   **Video elements** section (end screen, playlist card, quiz). Playlist: "Full Lessons".

## Captions

Every segment's `.srt` must be the synced one (`sync_captions.py`, run on the exact file the Part uses; a filmed day
uses `--text-srt` with its own caption text). Then `python3 tools/part_captions.py parts/part-NN.json`.
