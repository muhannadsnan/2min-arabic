#!/usr/bin/env python3
"""Upload-caption file for a Part compilation: stitches each segment's captions-upload.srt at its new position.

    python3 tools/part_captions.py parts/part-01.json      → output/<part>/captions-upload.srt

Needs each segment's source .srt: output/<video>/captions-upload.srt (make with tools/upload_captions.py), or
"srt" in the segment's JSON entry (e.g. Day 1's filmed video). Run after tools/compile_part.py.
"""
import json
import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent


def t2s(t):
    h, m, r = t.strip().split(":")
    s, ms = r.split(",")
    return int(h) * 3600 + int(m) * 60 + int(s) + int(ms) / 1000


def s2t(x):
    ms = round(x * 1000)
    return f"{ms // 3600000:02}:{ms // 60000 % 60:02}:{ms // 1000 % 60:02},{ms % 1000:03}"


def duration(p):
    return float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0",
                                 str(p)], capture_output=True, text=True).stdout)


def main():
    spec = json.loads(pathlib.Path(sys.argv[1]).read_text(encoding="utf-8"))
    out_dir = ROOT / "output" / spec["name"]
    segs = sorted((out_dir / "segments").glob("seg*.mp4"))
    offsets, t = [], 0.0
    for s in segs:
        offsets.append(t)
        t += duration(s)
    items = []
    for k, seg in enumerate(spec["segments"]):
        src = seg.get("srt") or f"output/{pathlib.Path(next(ROOT.glob(seg['file']))).parent.name}/captions-upload.srt"
        a, b = seg.get("start") or 0.0, seg.get("end") or 1e9
        for block in (ROOT / src).read_text(encoding="utf-8").strip().split("\n\n"):
            lines = block.split("\n")
            st, en = (t2s(x) for x in lines[1].split("-->"))
            if en <= a + 0.05 or st >= b - 0.05:
                continue
            items.append((offsets[k] + max(st, a) - a, offsets[k] + min(en, b) - a, " ".join(lines[2:])))
    out = out_dir / "captions-upload.srt"
    out.write_text("\n".join(f"{i}\n{s2t(x)} --> {s2t(y)}\n{txt}\n" for i, (x, y, txt) in enumerate(items, 1)),
                   encoding="utf-8")
    print(f"{out}: {len(items)} captions, ends {s2t(items[-1][1])} (video {s2t(t)})")


if __name__ == "__main__":
    main()
