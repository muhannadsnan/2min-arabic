#!/usr/bin/env python3
"""English caption track for a sleep video built by tools/sleep_video.py (2026-11-17) — no re-render.

    python3 tools/sleep_captions.py sleep01 [--rounds 8]   → output/<stem>/captions-upload.srt

Re-walks the same card timeline as build_round() from the cached clips (output/<stem>/clips) and offsets each round by
the REAL duration of its round file (output/<stem>/<stem>-r1/-r2/-rs/-rl.mp4), so small per-segment encoder padding
never adds up over 8 hours. Cues: learn card = "English — Arabic (translit)", review = "Arabic (translit)" then the
English, plus the opening and the chapter lines.
"""
import argparse, json, pathlib, subprocess, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
from sleep_video import BLOCK, VARIANTS, SR, load   # noqa: E402
from arabic_text import minimal                     # noqa: E402
AR = lambda l: minimal(l["ar"]) + (f" ({l['tr']})" if l.get("tr") else "")

OPEN = "Close your eyes, and just listen. You don't have to remember anything."


def dur_of(p):
    return float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(p)],
                                capture_output=True, text=True, check=True).stdout)


def round_cues(C, clips, variant, opening):
    """[(start, end, text)] relative to the round start, and the nominal round length."""
    v = VARIANTS[variant]; ln = lambda p: len(load(p)) / SR
    cues, t = [], 0.0
    for i, c in enumerate(C, 1):
        pos = 0.0
        if opening and i == 1:
            o = ln(clips / "n-open.wav"); od_ = 1.5 + o + max(2.5, 10.5 - 1.5 - o)
            cues.append((t + 1.5, t + 1.5 + o, OPEN)); t += od_
        pos = 1.5
        if v["chapter_line"]:
            d = ln(clips / f"n-ch{i:02}.wav"); cues.append((t + pos, t + pos + d, f"Chapter {i}. {c['name']}.")); pos += d + 2.5
        def say(d, text):
            nonlocal pos
            cues.append((t + pos, t + pos + d, text))
        def review(keys, pauses):
            nonlocal pos
            for j in keys:
                l = c["lines"][j - 1]; a = ln(clips / f"a-c{i:02}-{j:02}.wav"); e = ln(clips / f"n-c{i:02}-{j:02}.wav")
                say(a + pauses[0], AR(l)); pos += a + pauses[0]
                say(e, l["en"]); pos += e + pauses[1]
        keys = list(range(1, len(c["lines"]) + 1))
        for b0 in range(0, len(keys), BLOCK):
            for j in keys[b0:b0 + BLOCK]:
                l = c["lines"][j - 1]; a = ln(clips / f"a-c{i:02}-{j:02}.wav"); e = ln(clips / f"n-c{i:02}-{j:02}.wav")
                d = e + v["gap"] + a + v["learn"][0] + a
                say(d, f"{l['en']} — {AR(l)}"); pos += d + v["learn"][1]
            pos += 0.8; review(keys[b0:b0 + BLOCK], v["review"]); pos += 0.8
        if v["chapter_review"]:
            review(keys, v["chapter_review"])
        pos += 1.5; t += pos
    return cues, t


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("stem"); ap.add_argument("--rounds", type=int, default=8)
    a = ap.parse_args(); od = ROOT / "output" / a.stem; clips = od / "clips"
    C = json.load(open(ROOT / "videos" / f"{a.stem}-lines.json", encoding="utf-8"))
    parts = {"r1": round_cues(C, clips, "normal", True), "r2": round_cues(C, clips, "normal", False),
             "rs": round_cues(C, clips, "slow", False)}
    parts["rl"] = parts["rs"]
    real = {k: dur_of(od / f"{a.stem}-{k}.mp4") for k in parts}
    for k in parts:
        print(f"{k}: nominal {parts[k][1]:.2f} s, file {real[k]:.2f} s (diff {real[k] - parts[k][1]:+.2f})")
    order = ["r1", "r2"] + ["rs"] * (a.rounds - 3) + ["rl"]
    ts = lambda s: f"{int(s // 3600):02}:{int(s % 3600 // 60):02}:{int(s % 60):02},{int(round(s % 1 * 1000)) % 1000:03}"
    out, n, off = [], 0, 0.0
    for k in order:
        for st, en, txt in parts[k][0]:
            n += 1; out.append(f"{n}\n{ts(off + st)} --> {ts(off + max(en, st + 0.8))}\n{txt}\n")
        off += real[k]
    total = dur_of(od / f"{a.stem}.mp4")
    print(f"{n} cues, last ends {off:.1f} s, video {total:.1f} s")
    (od / "captions-upload.srt").write_text("\n".join(out), encoding="utf-8")


if __name__ == "__main__":
    main()
