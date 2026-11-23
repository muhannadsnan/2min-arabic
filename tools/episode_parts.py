#!/usr/bin/env python3
"""The 16:9 compile config of a monthly Episode (parts/ep-NN.json), from its built script + audio timeline.

    python3 tools/episode_parts.py episodes/ep-02.json "Learn Arabic step by step:" "questions, plans, …"

Run after make_audio.py and assemble.py (it needs audio/<stem>/timeline.json). One segment per chapter (the intro is
"What you'll learn" with the panel text given on the command line; the last chapter runs to the end, outro included),
each with the first 6 different Arabic cards of that chapter as its side-panel words — the same shape as
parts/ep-01.json, which compile_part.py turns into the 16:9 video with chapters.txt.
"""
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
from build_episode import scenes   # noqa: E402

CARD = re.compile(r"^🔤 \*\*On screen:\*\*\s*(.+)$", re.M)
ARABIC = re.compile(r"[؀-ۿ]")


def main():
    spec = json.loads(pathlib.Path(sys.argv[1]).read_text(encoding="utf-8"))
    panel = [x for x in sys.argv[2:]] or ["Learn Arabic step by step.", "", "All Arabic is spoken", "by native speakers."]
    stem = spec["stem"]
    n = int(re.search(r"ep(\d+)", stem).group(1))
    tl = json.loads((ROOT / "audio" / stem / "timeline.json").read_text(encoding="utf-8"))["scenes"]
    chapters = json.loads((ROOT / "images" / stem / "chapters.json").read_text(encoding="utf-8"))
    sc = scenes((ROOT / "videos" / f"{stem}.md").read_text(encoding="utf-8"))
    mp4, srt = f"output/{stem}/{stem}.mp4", f"output/{stem}/captions-upload.srt"
    segs = [{"title": "What you'll learn", "file": mp4, "start": 0.0, "end": round(tl[chapters[0]["first_scene"] - 1]["start"], 3),
             "srt": srt, "panel_title": "In this episode", "panel_text": panel}]
    for i, ch in enumerate(chapters):
        first = ch["first_scene"]
        last = chapters[i + 1]["first_scene"] - 1 if i + 1 < len(chapters) else len(tl)
        words, seen = [], set()
        for k in range(first, last + 1):
            for card in CARD.findall(sc.get(k, ("", ""))[1]):
                parts = [p.strip().strip("*").strip() for p in card.split(" · ")]
                if len(parts) >= 3 and ARABIC.search(parts[0]) and parts[0] not in seen:
                    seen.add(parts[0]); words.append(parts[:3])
        segs.append({"title": ch["title"], "file": mp4, "start": round(tl[first - 1]["start"], 3),
                     "end": round(tl[last - 1]["end"], 3) if i + 1 < len(chapters) else None, "srt": srt, "words": words[:6]})
    out = {"name": f"{stem}-16x9", "title": f"Episode {n}", "subtitle": "Learn Arabic for beginners · full course", "segments": segs}
    path = ROOT / "parts" / f"ep-{n:02d}.json"
    path.write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"{path.relative_to(ROOT)}: {len(segs)} segments")
    for s in segs:
        print(f"  {s['start']:8.1f}  {s['title']}  ({len(s.get('words', []))} words)")


if __name__ == "__main__":
    main()
