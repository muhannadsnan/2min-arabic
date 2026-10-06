#!/usr/bin/env python3
"""Make the owner's recording sheet for a video: every unique Arabic line, in order, in one list.

    python3 tools/recording_sheet.py videos/003-first-conversation.md   → videos/003-recording-sheet.md

The owner records the whole sheet in ONE take (see the instructions in the sheet); tools/split_recording.py then cuts
it into lines and cleans it. Lina's lines go to Koki on a separate sheet and are used as recorded.
"""
import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from make_audio import parse  # noqa: E402

ARABIC_SPEAKERS = {"teacher": "you", "teacher-slow": "you — slowly", "sami": "you (Sami)", "tom": "you (Tom, the tourist — a learner, a bit slower)",
                   "lina": "Lina — recorded by Koki"}


def unique_lines(script):
    seen, lines = set(), []
    for e in parse(script):
        if e[0] == "say" and e[1] in ARABIC_SPEAKERS and (e[1], e[2]) not in seen:
            seen.add((e[1], e[2]))
            lines.append((e[1], e[2]))
    return lines


def main():
    script = pathlib.Path(sys.argv[1])
    lines = unique_lines(script)
    stem = script.stem
    out = script.with_name((stem[:3] if stem[:3].isdigit() else stem) + "-recording-sheet.md")
    rows = "\n".join(f"| {i} | {ARABIC_SPEAKERS[sp]} | {text} |" for i, (sp, text) in enumerate(lines, 1))
    out.write_text(f"""# Recording sheet — {script.stem}

Record **all {len(lines)} lines in one recording**, top to bottom.

**How:**
- Quiet room, phone **close** (20–30 cm), earbuds **disconnected**, **iPhone Voice Memos**.
- Read each line calmly and clearly, neutral tone, the way you'd teach a beginner — sukun on the last letter.
- **Stay silent ~2 seconds between lines.** Don't say the numbers.
- Misspoke? Pause 2 seconds and **say the whole line again** — the last take of a line is used.
- Send it on WhatsApp **as a document** (not as a voice note — voice notes are compressed and blur the consonants).

| # | Who | Arabic |
|---|---|---|
{rows}
""", encoding="utf-8")
    print(f"{out}: {len(lines)} lines")


if __name__ == "__main__":
    main()
