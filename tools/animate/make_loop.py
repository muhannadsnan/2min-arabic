#!/usr/bin/env python3
"""Turn a raw Wan clip into library units (1080×1920, 30 fps) and register them in library/index.json.

    python3 tools/animate/make_loop.py RAW.mp4 openers/sami-peek-door --character sami --action "peeks out, waves" \
        [--start 0 --end 2.0] [--peak 0.15] [--hold 1.0] [--green]

Writes, in library/<kind>/:
    <name>.mp4         the clean part, played once (an entrance: ends in the action's end pose)
    <name>-loop.mp4    forward → short pause at the turn → backward to the START pose → start pose held 1 s.
                       It begins and ends on the same frame, so it repeats with no visible jump, and the held start
                       pose makes the repetition feel like a natural pause (owner's idea, 2026-10-01).
    <name>_sheet.png   6 frames of the clean part (for the quality check)
Frames are repeated (not blended) for 24 → 30 fps: blending ghosted a waving hand.
--green marks a green-screen unit (talking characters for tools/animate/composite.py).
"""
import argparse
import datetime as dt
import json
import pathlib
import subprocess

ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
LIB = ROOT / "library"
UP = "scale=1080:1920:force_original_aspect_ratio=increase:flags=lanczos,crop=1080:1920,setsar=1"
ENC = ["-c:v", "libx264", "-crf", "18", "-preset", "slow", "-pix_fmt", "yuv420p", "-movflags", "+faststart", "-an"]


def ff(*args):
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", *args], check=True)


def duration(p):
    return float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0",
                                 str(p)], capture_output=True, text=True).stdout)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("raw", type=pathlib.Path)
    ap.add_argument("name", help="kind/name, e.g. openers/sami-peek-door or talk/sami-talk-1")
    ap.add_argument("--character", required=True)
    ap.add_argument("--action", required=True)
    ap.add_argument("--start", type=float, default=0.0)
    ap.add_argument("--end", type=float, default=99.0)
    ap.add_argument("--peak", type=float, default=0.15, help="pause at the turnaround (s)")
    ap.add_argument("--hold", type=float, default=1.0, help="hold of the start pose at the end (s)")
    ap.add_argument("--green", action="store_true")
    a = ap.parse_args()

    once = LIB / f"{a.name}.mp4"
    loop = LIB / f"{a.name}-loop.mp4"
    once.parent.mkdir(parents=True, exist_ok=True)
    ff("-i", str(a.raw), "-vf", f"trim=start={a.start}:end={a.end},setpts=PTS-STARTPTS,{UP},fps=30", *ENC, str(once))
    ff("-i", str(once), "-filter_complex",
       f"[0]split[f][b];[f]tpad=stop_mode=clone:stop_duration={a.peak}[f2];"
       f"[b]reverse,trim=start_frame=1,setpts=PTS-STARTPTS,tpad=stop_mode=clone:stop_duration={a.hold}[r];"
       f"[f2][r]concat=n=2:v=1[v]", "-map", "[v]", *ENC, str(loop))
    n = int(subprocess.run(["ffprobe", "-v", "error", "-count_frames", "-select_streams", "v:0", "-show_entries",
                            "stream=nb_read_frames", "-of", "csv=p=0", str(once)], capture_output=True, text=True).stdout)
    sel = "+".join(f"eq(n\\,{k * (n - 1) // 5})" for k in range(6))
    ff("-i", str(once), "-vf", f"select='{sel}',scale=360:-2,tile=6x1:padding=4:color=white", "-fps_mode", "vfr",
       "-frames:v", "1", str(LIB / f"{a.name}_sheet.png"))

    idx_file = LIB / "index.json"
    idx = json.loads(idx_file.read_text()) if idx_file.exists() else []
    idx = [u for u in idx if u["name"] != a.name]
    idx.append({"name": a.name, "kind": a.name.split("/")[0], "character": a.character, "action": a.action,
                "green": a.green, "once_s": round(duration(once), 2), "loop_s": round(duration(loop), 2),
                "source": str(a.raw.relative_to(ROOT)) if a.raw.is_relative_to(ROOT) else str(a.raw),
                "created": str(dt.date.today()), "used_in": []})
    idx_file.write_text(json.dumps(sorted(idx, key=lambda u: u["name"]), indent=1, ensure_ascii=False) + "\n")
    print(f"{once.relative_to(ROOT)} {duration(once):.2f}s · {loop.relative_to(ROOT)} {duration(loop):.2f}s")


if __name__ == "__main__":
    main()
