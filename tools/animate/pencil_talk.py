#!/usr/bin/env python3
"""A pencil-style character talking to the camera, 6 fps (owner 2026-11-10: "take motion 6fps", natural mouth).

    python3 tools/animate/pencil_talk.py <char> <shot> voice.wav out.mp4 [--bg green|white|picture.png] [--mirror] [--x 0.5]
<shot>: face (head + shoulders, fills the width) · upper (head to waist, the lower half of the video, cards above) ·
full (head to shoes, the whole video height) · side (turned to talk to someone; --mirror faces the other way).
Set: library/sets/pencil/<char>/<shot>.png (+ <shot>-m1a.png … m3b.png), RGBA cut-outs made by pencil_set.py.
Mouth: the voice's loudness per frame picks closed · slightly open (m1) · half open (m2) · open (m3), at most 2 steps
per frame, alternating the two pictures of a level; closed in the pauses (voiced.py). Green = #00B140 for keying.
"""
import argparse, array, math, pathlib, subprocess, sys, tempfile
from PIL import Image
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from voiced import voiced_parts

ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
W, H, FPS = 1080, 1920, 6
GREEN = (0, 177, 64)


def levels(wav, dt):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", str(wav), "-ac", "1", "-ar", "16000", "-f", "s16le", "-"], capture_output=True).stdout
    a = array.array("h"); a.frombytes(raw); n = int(16000 * dt)
    rms = [math.sqrt(sum(x * x for x in a[i:i + n]) / max(1, len(a[i:i + n]))) for i in range(0, len(a), n)]
    ref = sorted(rms)[int(len(rms) * 0.9)] or 1
    return [0 if r < 0.12 * ref else 1 if r < 0.45 * ref else 2 if r < 0.8 * ref else 3 for r in rms]


def placer(shot, still, mirror, xpos):
    bb = still.getchannel("A").getbbox()
    def place(im):
        im = im.crop(bb)
        if mirror: im = im.transpose(Image.FLIP_LEFT_RIGHT)
        if shot == "face":
            s = W * 1.0 / im.width
        elif shot == "upper":                       # head at the middle of the video, shoulders ~62 % of the width,
            s = 0.62 * W / im.width                 # the rest runs off the bottom (stills differ in how far down they go)
        else:
            s = 1800 / im.height
        im = im.resize((round(im.width * s), round(im.height * s)), Image.LANCZOS)
        x = round(W * xpos - im.width / 2)
        y = H // 2 if shot == "upper" else H - im.height - (60 if shot in ("full", "side") else 0)
        return im, (x, y)
    return place


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("char"); ap.add_argument("shot"); ap.add_argument("voice"); ap.add_argument("out")
    ap.add_argument("--bg", default="green"); ap.add_argument("--mirror", action="store_true")
    ap.add_argument("--x", type=float, default=0.5, help="horizontal centre, 0–1")
    ap.add_argument("--lead", type=float, default=0.3, help="seconds before the voice starts (closed mouth)")
    a = ap.parse_args()
    d = ROOT / "library/sets/pencil" / a.char
    still = Image.open(d / f"{a.shot}.png").convert("RGBA")
    mouths = [sorted(d.glob(f"{a.shot}-m{l}?.png")) for l in (1, 2, 3)]
    mouths = [[Image.open(p).convert("RGBA") for p in ms] or [still] for ms in mouths]
    if a.bg == "green": back = Image.new("RGB", (W, H), GREEN)
    elif a.bg == "white": back = Image.new("RGB", (W, H), (255, 255, 255))
    else: back = Image.open(a.bg).convert("RGB").resize((W, H), Image.LANCZOS)
    place = placer(a.shot, still, a.mirror, a.x)
    dt = 1 / FPS; lv = levels(a.voice, dt); parts = voiced_parts(a.voice)
    lead = round(a.lead * FPS); frames = [0] * lead
    prev = 0
    for k, l in enumerate(lv):
        t = k * dt
        if not any(s - 0.05 <= t + dt / 2 <= e + 0.05 for s, e in parts): l = 0
        l = max(prev - 2, min(prev + 2, l)); prev = l; frames.append(l)
    frames += [0] * 3
    tmp = pathlib.Path(tempfile.mkdtemp()); cache = {}; alt = 0; lines = []
    for i, l in enumerate(frames):
        if l == 0: key = ("s", 0); src = still
        else: ms = mouths[l - 1]; key = (l, alt % len(ms)); src = ms[key[1]]; alt += 1
        if key not in cache:
            im, xy = place(src); fr = back.copy(); fr.paste(im, xy, im); p = tmp / f"k{len(cache):03d}.png"; fr.save(p); cache[key] = p
        lines += [f"file '{cache[key]}'", f"duration {dt:.4f}"]
    lines.append(lines[-2])
    (tmp / "list.txt").write_text("\n".join(lines))
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-f", "concat", "-safe", "0", "-i", str(tmp / "list.txt"),
                    "-itsoffset", f"{lead * dt:.3f}", "-i", str(a.voice), "-map", "0:v", "-map", "1:a", "-r", "30",
                    "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "18", "-c:a", "aac", "-b:a", "160k", a.out], check=True)
    print(a.out)


if __name__ == "__main__":
    main()
