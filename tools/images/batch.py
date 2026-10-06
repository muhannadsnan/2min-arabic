#!/usr/bin/env python3
"""Generate candidate images for every scene of a video (ComfyUI must be running — see generate.py).

    python3 tools/images/batch.py images/002-10-most-useful-phrases [--takes 3] [--only 4,7]

Reads <dir>/prompts.json: [{"style": "3d"}?, {"s": scene, "p": prompt, "ref": ["sami", …]} | {"s": scene, "asset": "desk-intro.png"}]
A leading {"style": "3d"} switches to the 3D look and to the 3D character references (assets/characters/<name>-3d.png).
Writes <dir>/candidates/sNN_k.png and <dir>/candidates/sNN_sheet.png (the takes side by side, for review).
Characters come from assets/characters/<name>.png; assets from assets/<file>.
After review, copy the chosen take to <dir>/sNN.png (tools/images/pick.py).
"""
import argparse
import json
import pathlib
import shutil
import subprocess
import sys
import time

from PIL import Image, ImageDraw

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parent.parent
ASSETS = ROOT / "assets"


def sheet(files, out):
    thumbs = [Image.open(f).convert("RGB").resize((432, 756)) for f in files]
    img = Image.new("RGB", (442 * len(thumbs), 756), "white")
    d = ImageDraw.Draw(img)
    for k, t in enumerate(thumbs):
        img.paste(t, (k * 442, 0))
        d.rectangle((k * 442, 0, k * 442 + 44, 40), fill="black")
        d.text((k * 442 + 14, 10), str(k), fill="yellow")
    img.save(out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("dir", type=pathlib.Path)
    ap.add_argument("--takes", type=int, default=3)
    ap.add_argument("--only", default="", help="comma-separated scene numbers")
    ap.add_argument("--seed-offset", type=int, default=0, help="use new seeds for a retry round")
    args = ap.parse_args()
    only = {int(x) for x in args.only.split(",") if x}
    cand = args.dir / "candidates"
    cand.mkdir(parents=True, exist_ok=True)
    style = "flat"
    for item in json.loads((args.dir / "prompts.json").read_text(encoding="utf-8")):
        if "s" not in item:   # {"style": "3d"} applies to the entries after it (3D look from Day 6 on)
            style = item.get("style", style)
            continue
        s = item["s"]
        if only and s not in only:
            continue
        if "from" in item:   # reuse an approved image from another video: {"from": "004-…/s09.png"}
            if not (ROOT / "images" / item["from"]).exists():   # not picked yet (same batch week): run again later
                print(f"s{s:02d}: from {item['from']} — not there yet, skipped")
                continue
            shutil.copy(ROOT / "images" / item["from"], args.dir / f"s{s:02d}.png")
            print(f"s{s:02d}: from {item['from']}")
            continue
        if "same" in item:   # reuse another scene's chosen image (copied by pick/assemble time)
            print(f"s{s:02d}: same as s{item['same']:02d}")
            continue
        if "asset" in item:
            shutil.copy(ASSETS / item["asset"], args.dir / f"s{s:02d}.png")
            print(f"s{s:02d}: asset {item['asset']}")
            continue
        if "p" not in item:   # e.g. {"s": 1, "clip": "openers/…"} — a library clip, nothing to generate
            print(f"s{s:02d}: clip {item.get('clip', '—')}")
            continue
        refs = []
        for name in item.get("ref", []):
            ref = ASSETS / "characters" / f"{name}.png"
            if style == "3d" and (ASSETS / "characters" / f"{name}-3d.png").exists():
                ref = ASSETS / "characters" / f"{name}-3d.png"   # 3D reference keeps the 3D look consistent
            if not ref.exists():
                sys.exit(f"missing character reference {ref}")
            refs += ["--ref", str(ref)]
        files = []
        for k in range(args.takes):
            out = cand / f"s{s:02d}_{k}.png"
            files.append(out)
            if out.exists() and not args.seed_offset:   # resume: keep takes that are already done
                continue
            cmd = [sys.executable, str(HERE / "generate.py"), item["p"], str(out),
                   "--seed", str(1000 * s + k + args.seed_offset), "--style", style, *refs]
            for attempt in range(3):   # the GPU sometimes runs out of memory on 2-reference images: retry
                if subprocess.run(cmd, stdout=subprocess.DEVNULL).returncode == 0:
                    break
                print(f"  s{s:02d} take {k}: failed (attempt {attempt + 1}), retrying", flush=True)
                time.sleep(10)
            else:
                sys.exit(f"s{s:02d} take {k}: failed 3 times")
        sheet(files, cand / f"s{s:02d}_sheet.png")
        print(f"s{s:02d}: {len(files)} takes", flush=True)


if __name__ == "__main__":
    main()
