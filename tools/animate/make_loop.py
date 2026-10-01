#!/usr/bin/env python3
"""Turn a raw Wan clip into library units (1080×1920, 30 fps) and register them in library/index.json.

    python3 tools/animate/make_loop.py RAW.mp4 talk/sami-talk-2 --character sami --action "calm talk" \
        [--start 0 --end 2.0] [--speed 0.667] [--loop 6] [--green]

Writes, in library/<kind>/:
    <name>.mp4        the clean part, played once (an entrance). --speed 0.667 stretches a 2-s Wan clip (49 frames)
                      to 3 s; motion-compensated in-between frames keep it smooth (no extra GPU time).
    <name>-loop.mp4   a smooth "pendulum" loop: start pose → end pose → start pose, slowing down gently into each
                      turn and speeding up out of it (cosine easing) — no frozen frames, no jump. It starts and
                      ends on the same frame, so it repeats seamlessly. Default length = 2 × the clean part.
    <name>-tail.mp4   end pose → a little back → end pose (eased), over the last --tail s: assemble.py plays it after
                      the entrance so the character keeps moving instead of freezing (e.g. the wave keeps waving)
    <name>_sheet.png  6 frames of the clean part (for the quality check)
(Owner, 2026-10-01: hard freezes at the turns and at the end made the loop feel mechanical.)
"""
import argparse
import datetime as dt
import json
import math
import pathlib
import shutil
import subprocess
import tempfile

ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
LIB = ROOT / "library"
UP = "scale=1080:1920:force_original_aspect_ratio=increase:flags=lanczos,crop=1080:1920,setsar=1"
ENC = ["-c:v", "libx264", "-crf", "18", "-preset", "slow", "-pix_fmt", "yuv420p", "-movflags", "+faststart", "-an"]
DENSE = 60   # in-between frames per second used for the eased loop


def ff(*args):
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", *args], check=True)


def duration(p):
    return float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0",
                                 str(p)], capture_output=True, text=True).stdout)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("raw", type=pathlib.Path)
    ap.add_argument("name", help="kind/name, e.g. openers/sami-peek-door or talk/sami-talk-2")
    ap.add_argument("--character", required=True)
    ap.add_argument("--action", required=True)
    ap.add_argument("--start", type=float, default=0.0)
    ap.add_argument("--end", type=float, default=99.0)
    ap.add_argument("--speed", type=float, default=1.0, help="0.667 = a 2-s clip becomes 3 s (smooth slow motion)")
    ap.add_argument("--loop", type=float, default=0.0, help="loop length in s (default: 2 × the clean part)")
    ap.add_argument("--tail", type=float, default=0.0,
                    help="also make <name>-tail.mp4: a pendulum over the last N s (keeps an entrance alive after it ends)")
    ap.add_argument("--green", action="store_true")
    a = ap.parse_args()

    once = LIB / f"{a.name}.mp4"
    loop = LIB / f"{a.name}-loop.mp4"
    once.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as tmp:
        tmp = pathlib.Path(tmp)
        # 1. clean part at the native size, slowed if asked, as a dense smooth 60-fps master
        dense = tmp / "dense.mp4"
        ff("-i", str(a.raw), "-vf",
           f"trim=start={a.start}:end={a.end},setpts=(PTS-STARTPTS)/{a.speed},"
           f"minterpolate=fps={DENSE}:mi_mode=mci:mc_mode=aobmc:me_mode=bidir:vsbmc=1",
           "-c:v", "libx264", "-crf", "12", "-pix_fmt", "yuv420p", str(dense))
        ff("-i", str(dense), "-vf", f"fps=30,{UP}", *ENC, str(once))
        # 2. eased pendulum loop picked from the dense frames
        frames = tmp / "f"
        frames.mkdir()
        ff("-i", str(dense), str(frames / "%05d.png"))
        files = sorted(frames.glob("*.png"))
        m = len(files)
        length = a.loop or 2 * duration(once)
        n = round(length * 30)
        lst = []
        for k in range(n):
            pos = (1 - math.cos(2 * math.pi * k / n)) / 2          # 0 → 1 → 0, zero speed at both turns
            lst.append(f"file '{files[round(pos * (m - 1))]}'\nduration {1 / 30:.6f}")
        (tmp / "list.txt").write_text("\n".join(lst) + "\n")
        ff("-f", "concat", "-safe", "0", "-i", str(tmp / "list.txt"), "-vf", f"fps=30,{UP}", "-frames:v", str(n),
           *ENC, str(loop))
        if a.tail:   # end pose → a little back → end pose, eased: played after the entrance instead of a freeze
            t0 = max(0, m - 1 - round(a.tail * DENSE))
            nt = round(2 * a.tail * 30)
            lst = []
            for k in range(nt):
                pos = (1 - math.cos(2 * math.pi * k / nt)) / 2
                lst.append(f"file '{files[round(m - 1 - pos * (m - 1 - t0))]}'\nduration {1 / 30:.6f}")
            (tmp / "tail.txt").write_text("\n".join(lst) + "\n")
            ff("-f", "concat", "-safe", "0", "-i", str(tmp / "tail.txt"), "-vf", f"fps=30,{UP}", "-frames:v", str(nt),
               *ENC, str(LIB / f"{a.name}-tail.mp4"))
    cnt = int(subprocess.run(["ffprobe", "-v", "error", "-count_frames", "-select_streams", "v:0", "-show_entries",
                              "stream=nb_read_frames", "-of", "csv=p=0", str(once)], capture_output=True, text=True).stdout)
    sel = "+".join(f"eq(n\\,{k * (cnt - 1) // 5})" for k in range(6))
    ff("-i", str(once), "-vf", f"select='{sel}',scale=360:-2,tile=6x1:padding=4:color=white", "-fps_mode", "vfr",
       "-frames:v", "1", str(LIB / f"{a.name}_sheet.png"))

    idx_file = LIB / "index.json"
    idx = json.loads(idx_file.read_text()) if idx_file.exists() else []
    old = next((u for u in idx if u["name"] == a.name), {})
    idx = [u for u in idx if u["name"] != a.name]
    idx.append({"name": a.name, "kind": a.name.split("/")[0], "character": a.character, "action": a.action,
                "green": a.green, "once_s": round(duration(once), 2), "loop_s": round(duration(loop), 2),
                "speed": a.speed, "source": str(a.raw.relative_to(ROOT)) if a.raw.is_relative_to(ROOT) else str(a.raw),
                "created": str(dt.date.today()), "used_in": old.get("used_in", [])})
    idx_file.write_text(json.dumps(sorted(idx, key=lambda u: u["name"]), indent=1, ensure_ascii=False) + "\n")
    print(f"{once.relative_to(ROOT)} {duration(once):.2f}s · {loop.relative_to(ROOT)} {duration(loop):.2f}s")


if __name__ == "__main__":
    main()
