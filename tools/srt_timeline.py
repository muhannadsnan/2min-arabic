#!/usr/bin/env python3
"""Timeline for videos not built by make_audio (Story Shorts, 2026-11-17) so dub_subs.py / subtitle-backlog work.

    python3 tools/srt_timeline.py <stem> [<stem> …]   → audio/<stem>/timeline.json

Every English-only cue of output/<stem>/captions-upload.srt becomes a "narrator" clip numbered by its cue number
(= the keys in dubs/<stem>.json); cues with Arabic become "teacher" clips and stay as they are in every language.
Never overwrites a real make_audio timeline (one that has no "from_srt" flag).
"""
import json, pathlib, re, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
def t2s(t): h, m, s = t.replace(",", ".").split(":"); return int(h) * 3600 + int(m) * 60 + float(s)

for stem in sys.argv[1:]:
    srt = (ROOT / "output" / stem / "captions-upload.srt").read_text(encoding="utf-8")
    clips = []
    for n, a, b, txt in re.findall(r"(\d+)\n([\d:,]+) --> ([\d:,]+)\n(.*?)(?:\n\n|\Z)", srt, re.S):
        ar = bool(re.search(r"[؀-ۿ]", txt))
        clips.append({"n": int(n), "speaker": "teacher" if ar else "narrator", "start": t2s(a), "end": t2s(b), "text": txt.strip()})
    out = ROOT / "audio" / stem / "timeline.json"
    if out.exists() and not json.loads(out.read_text()).get("from_srt"):
        sys.exit(f"{out} is a real make_audio timeline — not overwritten")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps({"from_srt": True, "clips": clips}, ensure_ascii=False, indent=1), encoding="utf-8")
    print(stem, sum(c["speaker"] == "narrator" for c in clips), "narrator cues →", out.relative_to(ROOT))
