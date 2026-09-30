#!/usr/bin/env python3
"""Put Koki's recorded Lina lines into a video's recording map (replaces the owner's placeholder lina lines).

    python3 tools/merge_koki.py videos/006-….md [--koki footage/recordings/_lina-koki]

Matches by the exact Arabic text of each `say:lina` line; prints what was replaced and what is still missing
(missing lines → add them to Koki's next sheet). Run after split_recording.py, before make_audio.py.
"""
import argparse
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
from recording_sheet import unique_lines  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("script", type=pathlib.Path)
    ap.add_argument("--koki", type=pathlib.Path, default=ROOT / "footage/recordings/_lina-koki")
    a = ap.parse_args()
    koki = {e["text"]: e for e in json.loads((a.koki / "map.json").read_text(encoding="utf-8")) if e.get("file")}
    map_file = ROOT / "footage/recordings" / a.script.stem / "map.json"
    entries = json.loads(map_file.read_text(encoding="utf-8")) if map_file.exists() else []
    by_text = {(e["speaker"], e["text"]): e for e in entries}
    missing = []
    for speaker, text in unique_lines(a.script):
        if speaker != "lina":
            continue
        if text not in koki:
            missing.append(text)
            continue
        src = koki[text]
        e = by_text.get((speaker, text))
        if e is None:
            e = {"n": len(entries) + 1, "speaker": speaker, "text": text}
            entries.append(e)
        e.update(file=src["file"], heard=src.get("heard", ""), cer=src.get("cer", 0.0), source="koki")
        print(f"✅ lina ← Koki: {text}")
    map_file.parent.mkdir(parents=True, exist_ok=True)
    map_file.write_text(json.dumps(entries, ensure_ascii=False, indent=1), encoding="utf-8")
    for t in missing:
        print(f"❌ not in Koki's recordings: {t}")
    print(f"{map_file}: {len(entries)} lines" + (f", {len(missing)} Lina lines missing" if missing else ""))


if __name__ == "__main__":
    main()
