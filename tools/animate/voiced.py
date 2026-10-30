#!/usr/bin/env python3
"""Voiced intervals of a video's recorded lines (owner 2026-10-26: the mouth stops when the sentence is over).

    from voiced import speaking   # speaking(stem) -> {scene_no: {speaker: [[start, end], …]}} in scene time
The timeline gives each clip's slot; the clip's own audio (audio/<stem>/clips/NN-speaker.wav) is silence-trimmed
(-38 dB, 0.12 s) so the intervals cover only the time the voice really sounds.
"""
import json, pathlib, re, subprocess
ROOT = pathlib.Path(__file__).resolve().parent.parent.parent


def voiced_parts(wav):
    out = subprocess.run(["ffmpeg", "-i", str(wav), "-af", "silencedetect=noise=-38dB:d=0.12", "-f", "null", "-"],
                         capture_output=True, text=True).stderr
    dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(wav)],
                               capture_output=True, text=True).stdout or 0)
    st = [float(x) for x in re.findall(r"silence_start: ([\d.]+)", out)]
    en = [float(x) for x in re.findall(r"silence_end: ([\d.]+)", out)]
    parts, t = [], 0.0
    for s, e in zip(st, en + [dur] * (len(st) - len(en))):
        if s - t > 0.15: parts.append((t, s))
        t = e
    if dur - t > 0.15: parts.append((t, dur))
    return parts


def speaking(stem):
    t = json.loads((ROOT / "audio" / stem / "timeline.json").read_text())
    scenes = [(s["start"], s["end"]) for s in t["scenes"]]
    res = {}
    for c in t["clips"]:
        if c["speaker"] == "narrator":
            continue
        n = next(i + 1 for i, (s, e) in enumerate(scenes) if s <= c["start"] < e)
        s0 = scenes[n - 1][0]
        parts = voiced_parts(ROOT / "audio" / stem / "clips" / c["file"])
        if not parts:   # silent placeholder (preview before the recording): the mouth moves through the whole slot
            parts = [(0.1, c["end"] - c["start"] - 0.1)]
        for a, b in parts:
            res.setdefault(n, {}).setdefault(c["speaker"], []).append([round(c["start"] - s0 + a, 2), round(c["start"] - s0 + b, 2)])
    return res
