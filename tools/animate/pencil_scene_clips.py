#!/usr/bin/env python3
"""Talking pencil-character clips for every "clip" scene of a video, lip-synced to that scene's audio (owner "go"
2026-11-19, Days 31–33 — the first pencil videos where Sami and Lina talk).

    python3 tools/animate/pencil_scene_clips.py 031-favorite-color [--side 13,9] [--mirror 13]

Reads images/<video>/prompts.json (scenes with "clip": "sets/scenes/<name>") and audio/<video>/timeline.json.
Per scene: who talks = sami / lina if they speak in the scene, else the narrator. A wav as long as the scene is cut
from voiceover.wav with everyone else silenced, so the mouth moves only on that character's own lines (the narrator
can introduce Sami while Sami's picture is on screen). Then tools/animate/pencil_talk.py renders it on white.
The hook's narrator (scene 1, one-line card) is the upper shot zoomed 1.4× (head at y≈580 — owner 2026-11-13: "make him
BIG"); later narrator scenes keep the plain upper shot (head at the middle, clear of 2–3 line cards); side shots are
scaled to 55 % with the head at y≈900.
Output: library/sets/scenes/<name>.mp4 (clip_mode "once": exactly the scene's length).
"""
import argparse, json, pathlib, subprocess, sys, tempfile

ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
TALKERS = ("sami", "lina")


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("video")
    ap.add_argument("--side", default="", help="scenes that use the side shot (turned to the other person)")
    ap.add_argument("--mirror", default="", help="scenes whose shot is mirrored")
    ap.add_argument("--only", default="")
    a = ap.parse_args()
    side = {int(s) for s in a.side.split(",") if s}; mirror = {int(s) for s in a.mirror.split(",") if s}
    only = {int(s) for s in a.only.split(",") if s}
    P = json.load(open(ROOT / "images" / a.video / "prompts.json"))
    tl = json.load(open(ROOT / "audio" / a.video / "timeline.json"))
    vo = ROOT / "audio" / a.video / "voiceover.wav"
    for o in P:
        if "s" not in o or "clip" not in o or (only and o["s"] not in only):
            continue
        s = o["s"]; sc = tl["scenes"][s - 1]; t0, t1 = sc["start"], sc["end"]
        clips = [c for c in tl["clips"] if c["start"] >= t0 - 0.01 and c["end"] <= t1 + 0.01]
        who = next((sp for sp in TALKERS if any(c["speaker"] == sp for c in clips)), "narrator")
        mine = [c for c in clips if c["speaker"] == who]
        out = ROOT / "library" / f"{o['clip']}.mp4"; out.parent.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory() as td:
            wav = pathlib.Path(td) / "v.wav"
            vol = "+".join(f"between(t,{c['start'] - t0:.3f},{c['end'] - t0:.3f})" for c in mine) or "0"
            subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{t0:.3f}", "-t", f"{t1 - t0:.3f}", "-i", str(vo),
                            "-af", f"volume='if({vol},1,0)':eval=frame", "-ar", "16000", "-ac", "1", str(wav)], check=True)
            shot = "side" if s in side else "upper"
            raw = pathlib.Path(td) / "raw.mp4"
            cmd = [sys.executable, str(ROOT / "tools/animate/pencil_talk.py"), who, shot, str(wav), str(raw), "--bg", "white"]
            if s in mirror: cmd.append("--mirror")
            subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL)
            if who == "narrator" and s == 1:      # hook: one-line card → the big narrator
                vf = "crop=771:1371:154:549,scale=1080:1920:flags=lanczos,"
            elif shot == "side":                  # full-body side shot: smaller, head below the card (y ≈ 900)
                vf = "scale=594:1056:flags=lanczos,pad=1080:1920:243:864:white,"
            else:                                 # upper shot: head at the middle, clear of 2–3 line cards
                vf = ""
            subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(raw), "-vf", f"{vf}tpad=stop_mode=clone:stop_duration=5",
                            "-t", f"{t1 - t0:.3f}", "-an", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "18", str(out)], check=True)
        print(f"scene {s}: {who} {shot}{' mirrored' if s in mirror else ''} · {t1 - t0:.2f} s · {len(mine)} lines → {out.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
