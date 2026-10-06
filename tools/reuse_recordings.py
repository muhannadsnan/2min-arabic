#!/usr/bin/env python3
"""Point a video at Arabic lines that were already recorded for other videos — nothing new to record.

    python3 tools/reuse_recordings.py videos/x03-….md     → footage/recordings/<video>/map.json

Every `say:<arabic speaker>` line must exist with the same speaker and exact text in another video's map.json
(lowest CER wins). Lines that don't exist are listed — those go on the next recording sheet.
"""
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
SPEAKERS = {"teacher", "teacher-slow", "sami", "lina"}


def main():
    script = pathlib.Path(sys.argv[1])
    lines = re.findall(r"```say:([\w-]+)\n(.+?)\n```", script.read_text(encoding="utf-8"), re.S)
    wanted = [(sp, t.strip()) for sp, t in lines if sp in SPEAKERS]
    best = {}
    for f in sorted((ROOT / "footage" / "recordings").glob("*/map.json")):
        if f.parent.name == script.stem:
            continue
        for r in json.loads(f.read_text(encoding="utf-8")):
            key = (r["speaker"], r["text"])
            if r.get("file") and (ROOT / r["file"]).exists() and (key not in best or r["cer"] < best[key]["cer"]):
                best[key] = r
    out, missing = [], []
    for n, key in enumerate(dict.fromkeys(wanted), 1):
        if key in best:
            out.append({**best[key], "n": n})
        else:
            missing.append(key)
    target = ROOT / "footage" / "recordings" / script.stem / "map.json"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    for r in out:
        print(f"✅ [{r['speaker']}] {r['text']}  ← {r['file']}")
    for sp, t in missing:
        print(f"❌ [{sp}] {t}  — not recorded yet")
    print(f"{len(out)} re-used, {len(missing)} missing → {target}")
    sys.exit(1 if missing else 0)


if __name__ == "__main__":
    main()
