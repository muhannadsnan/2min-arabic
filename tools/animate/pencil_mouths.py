#!/usr/bin/env python3
"""One mouth shape for a pencil-style still (owner 2026-11-10: natural talking, 6 fps).

    python3 tools/animate/pencil_mouths.py base.png x0 y0 x1 y1 "<mouth prompt>" out.png [--seed N]
(x0 y0 x1 y1) = the mouth box in the still (corners of the smile included). A square around it (≥ 4× the mouth width)
is cut out, enlarged to 512×512 and only the mouth ellipse is inpainted (generate.py --mask), then the result is
shrunk back and pasted in with a soft edge → everything outside the mouth stays pixel-identical to the still, so the
frames never "boil" while he talks, and small faces (full / side shots) still get a properly drawn mouth.
Needs ComfyUI running (the queue scripts start it and check for a game first).
"""
import argparse, pathlib, subprocess, sys, tempfile
from PIL import Image, ImageDraw, ImageFilter

ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
STYLE = ("the same naive colour-pencil drawing on plain white paper, same style, same lines, same skin colour, "
         "everything else exactly the same")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("base"); ap.add_argument("box", nargs=4, type=int); ap.add_argument("prompt"); ap.add_argument("out")
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--jaw", action="store_true", help="redraw the lower face around the mouth (beard / stubble edits)")
    a = ap.parse_args()
    im = Image.open(a.base).convert("RGB"); x0, y0, x1, y1 = a.box
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    S = int(max(4 * (x1 - x0), 4 * (y1 - y0), 120))
    if a.jaw: S = int(max(S, 3.2 * (x1 - x0) + 2 * (y1 - y0)))
    L = int(min(max(0, cx - S / 2), im.width - S)); T = int(min(max(0, cy - S / 2), im.height - S))
    S = min(S, im.width, im.height)
    crop = im.crop((L, T, L + S, T + S)); k = 512 / S
    tmp = pathlib.Path(tempfile.mkdtemp())
    crop.resize((512, 512), Image.LANCZOS).save(tmp / "crop.png")
    m = Image.new("L", (512, 512), 0)
    pad = 0.12 * (x1 - x0)
    if a.jaw:   # jaw + chin + lips: from just under the nose to below the chin, cheek to cheek (2026-11-10 beard edits)
        w = x1 - x0; e = (cx - 1.15 * w, y0 - 0.15 * w, cx + 1.15 * w, y1 + 0.75 * w)
    else:
        e = (x0 - pad, y0 - pad, x1 + pad, y1 + pad)
    ImageDraw.Draw(m).ellipse(((e[0] - L) * k, (e[1] - T) * k, (e[2] - L) * k, (e[3] - T) * k), fill=255)
    m.save(tmp / "mask.png")
    subprocess.run([sys.executable, str(ROOT / "tools/images/generate.py"), f"{a.prompt}, {STYLE}", str(tmp / "gen.png"),
                    "--no-style", "--ref", str(tmp / "crop.png"), "--mask", str(tmp / "mask.png"),
                    "--width", "512", "--height", "512", "--ref-mp", "0.27", "--seed", str(a.seed)],
                   check=True, stdout=subprocess.DEVNULL)
    gen = Image.open(tmp / "gen.png").convert("RGB").resize((S, S), Image.LANCZOS)
    soft = m.resize((S, S), Image.LANCZOS).filter(ImageFilter.GaussianBlur(S / 120))
    out = im.copy(); out.paste(gen, (L, T), soft); out.save(a.out)
    print(a.out)


if __name__ == "__main__":
    main()
