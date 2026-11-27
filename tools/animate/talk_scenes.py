#!/usr/bin/env python3
"""3D talking scenes for a video (owner 2026-11-27: back to semi-3D — the 3D counterpart of pencil_scene_clips.py).

    $TTS tools/animate/talk_scenes.py 034-hobby [--only 1,13]

Reads images/<video>/prompts.json entries that have a "talk" spec next to their "clip":
    {"s": 13, "clip": "sets/scenes/d34-s13", "clip_mode": "loop",
     "talk": {"bg": "library/backgrounds/home-living.png",
              "layers": [{"who": "sami", "set": "sami_side_free", "x": 0.27, "h": 0.66},
                         {"who": "lina", "set": "lina_side", "x": 0.73, "h": 0.66, "mirror": false}]}}
"who" = sami / lina / omar / waiter for their own recorded lines, or "narrator" for the presenter (the narrator is
the owner's male voice → a man's close-up; his mouth moves on the narrator's voiced parts only, never on Arabic lines).
"set" = library/sets/v2/<set>.png + <set>_talk1–5.png. The scene's length and the speaking times come from
audio/<video>/timeline.json (voiced parts only: the mouth closes when the sentence ends — tools/animate/voiced.py).
Writes library/sets/scenes/specs/<name>.json and library/<clip>-loop.mp4 (compose_talk.py), the name assemble.py loads.
Sizes (animation-library skill): two-shots h 0.66 (owner 27 Nov), presenter cB 0.7232, close2 1.0.
"""
import argparse, json, pathlib, subprocess, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT / "tools" / "animate"))
from voiced import voiced_parts   # noqa: E402

SETS = ROOT / "library" / "sets" / "v2"


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("video"); ap.add_argument("--only", default="")
    a = ap.parse_args()
    only = {int(s) for s in a.only.split(",") if s}
    P = json.load(open(ROOT / "images" / a.video / "prompts.json"))
    tl = json.load(open(ROOT / "audio" / a.video / "timeline.json"))
    for o in P:
        if "talk" not in o or (only and o["s"] not in only):
            continue
        s = o["s"]; sc = tl["scenes"][s - 1]; t0, t1 = sc["start"], sc["end"]
        clips = [c for c in tl["clips"] if t0 - 0.01 <= c["start"] < t1]
        layers = []
        for L in o["talk"]["layers"]:
            speak = []
            for c in clips:
                if c["speaker"] != L["who"]:
                    continue
                parts = voiced_parts(ROOT / "audio" / a.video / "clips" / c["file"]) or [(0.1, c["end"] - c["start"] - 0.1)]
                speak += [[round(c["start"] - t0 + p, 2), round(c["start"] - t0 + q, 2)] for p, q in parts]
            lay = {"still": str((SETS / f"{L['set']}.png").relative_to(ROOT)), "x": L["x"], "h": L["h"]}
            if speak:
                lay["talk"] = [str((SETS / f"{L['set']}_talk{i}.png").relative_to(ROOT)) for i in range(1, 6)]
                lay["speak"] = speak
            if L.get("mirror"):
                lay["mirror"] = True
            layers.append(lay)
        spec = {"layers": layers, "bg": o["talk"]["bg"], "seconds": round(t1 - t0, 2)}
        name = pathlib.Path(o["clip"]).name
        sp = ROOT / "library" / "sets" / "scenes" / "specs" / f"{name}.json"
        sp.write_text(json.dumps(spec, indent=1))
        out = ROOT / "library" / f"{o['clip']}-loop.mp4"
        r = subprocess.run([sys.executable, str(ROOT / "tools/animate/compose_talk.py"), str(sp), str(out)],
                           capture_output=True, text=True)
        print(f"s{s:02d} {name}: {spec['seconds']} s · " + (r.stdout.strip().splitlines()[-1] if r.returncode == 0 else "FAILED " + r.stderr[-300:]))


if __name__ == "__main__":
    main()
