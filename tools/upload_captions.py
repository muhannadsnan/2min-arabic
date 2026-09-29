#!/usr/bin/env python3
"""Caption file to UPLOAD to YouTube (not burned in): exact English narration + every Arabic line as
"Arabic (transliteration)". Viewers can then use CC → Auto-translate into any language.

    python3 tools/upload_captions.py videos/003-first-conversation.md   → output/<video>/captions-upload.srt
"""
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
from assemble import on_screen_by_scene  # noqa: E402
from make_audio import parse  # noqa: E402

ARABIC = re.compile(r"[؀-ۿ]")


def srt_time(x):
    ms = round(x * 1000)
    return f"{ms // 3600000:02}:{ms // 60000 % 60:02}:{ms // 1000 % 60:02},{ms % 1000:03}"


def main():
    script = pathlib.Path(sys.argv[1])
    stem = script.stem
    tl = json.loads((ROOT / "audio" / stem / "timeline.json").read_text(encoding="utf-8"))
    # transliteration per Arabic line, from the on-screen cards ("Arabic · translit · English")
    translit = {}
    for card in on_screen_by_scene(script):
        if card:
            parts = [p.strip().strip("*") for p in card.split(" · ")]
            if len(parts) >= 2 and ARABIC.search(parts[0]):
                translit[re.sub(r"[ً-ْ\s.،؟!?]", "", parts[0])] = parts[1]
    items = []
    for c in tl["clips"]:
        text = c["text"]
        if ARABIC.search(text):
            key = re.sub(r"[ً-ْ\s.،؟!?]", "", text)
            tr = next((v for k, v in translit.items() if k and (k == key or k in key or key in k)), "")
            text = f"{text} ({tr})" if tr else text
        items.append((c["start"], c["end"], text))
    items += [(v["start"], v["end"], v["caption"]) for v in tl.get("videos", []) if v["caption"]]
    items.sort()
    out = ROOT / "output" / stem / "captions-upload.srt"
    out.write_text("\n".join(f"{k}\n{srt_time(a)} --> {srt_time(b)}\n{t}\n" for k, (a, b, t) in enumerate(items, 1)),
                   encoding="utf-8")
    print(f"{out}: {len(items)} captions")


if __name__ == "__main__":
    main()
