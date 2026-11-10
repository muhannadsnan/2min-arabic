#!/usr/bin/env python3
"""Motion sample for the pencil style (owner 2026-11-10: "primitive like simple moving cartoons … 3 frames/sec").

    python3 tools/animate/pencil_sample.py frames.json out.mp4 --fps 3
frames.json: {"base": png, "close": png (optional close-shot still), "mouth": [[level-1 pngs], [level-2 pngs], [level-3 pngs]],
              "wave": [png, png], "half": png, "audio": wav}
Mouth (owner 2026-11-10 "make it look natural"): the loudness of the voice in each frame picks how open the mouth is
(closed · slightly open · half open · open); it moves at most 2 steps per frame and alternates pictures within a level.
Plays: full shot — hand up (half) → wave (alternating) → hand down; then close shot (head + chest) talking to the
camera: a mouth picture on every frame while the voice sounds (voiced.py), the closed mouth in the pauses.
Everything changes only on the frame grid (1/fps), which is what gives the hand-drawn, primitive look.
"""
import argparse, json, pathlib, random, subprocess, sys, tempfile
from PIL import Image
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from voiced import voiced_parts

W, H = 1080, 1920
PAPER = (255, 255, 255)
LEVEL = [min(255, round(v * 255 / 228)) for v in range(256)] * 3   # paper (~230+) → pure white, lines keep their tone



def full(p):
    im = Image.open(p).convert("RGB").point(LEVEL); h = 1650; w = round(im.width * h / im.height)
    c = Image.new("RGB", (W, H), PAPER); c.paste(im.resize((w, h), Image.LANCZOS), ((W - w) // 2, H - h - 60)); return c


def close(p):
    im = Image.open(p).convert("RGB").point(LEVEL)
    box = (im.width * 0.12, 0, im.width * 0.88, im.height * 0.52)        # head + chest
    cr = im.crop(tuple(map(round, box))); w = W; h = round(cr.height * w / cr.width)
    c = Image.new("RGB", (W, H), PAPER); c.paste(cr.resize((w, h), Image.LANCZOS), (0, H - h)); return c


def still(p):
    """a close-shot drawing (head + chest already framed): fill the width, sit at the bottom"""
    im = Image.open(p).convert("RGB").point(LEVEL); w = W; h = round(im.height * w / im.width)
    c = Image.new("RGB", (W, H), PAPER); c.paste(im.resize((w, h), Image.LANCZOS), (0, H - h)); return c


def levels(wav, dt):
    """mouth openness 0–3 per frame from the voice's loudness (RMS), scaled to this clip's loud parts"""
    import array, math
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", wav, "-ac", "1", "-ar", "16000", "-f", "s16le", "-"], capture_output=True).stdout
    a = array.array("h"); a.frombytes(raw); n = int(16000 * dt)
    rms = [math.sqrt(sum(x * x for x in a[i:i + n]) / max(1, len(a[i:i + n]))) for i in range(0, len(a), n)]
    ref = sorted(rms)[int(len(rms) * 0.9)] or 1
    return [0 if r < 0.12 * ref else 1 if r < 0.45 * ref else 2 if r < 0.8 * ref else 3 for r in rms] + [0, 0]


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("frames"); ap.add_argument("out"); ap.add_argument("--fps", type=float, default=3)
    a = ap.parse_args(); F = json.loads(pathlib.Path(a.frames).read_text()); dt = 1 / a.fps
    seq = []                                                             # (image, seconds)
    for t in [F["half"]] + F["wave"] * 3 + [F["half"], F["base"]]:      # ~2.7 s at 3 fps
        seq.append((full(t), dt))
    seq.append((full(F["base"]), 0.6))
    lv = levels(F["audio"], dt)
    parts = voiced_parts(F["audio"]); dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", F["audio"]], capture_output=True, text=True).stdout)
    t0 = sum(s for _, s in seq); prev = 0; alt = 0; cbase = F.get("close", F["base"]); closeshot = "close" not in F
    for k, l in enumerate(lv):
        t = k * dt
        if not any(s - 0.05 <= t + dt / 2 <= e + 0.05 for s, e in parts): l = 0
        l = max(prev - 2, min(prev + 2, l)); prev = l
        if l == 0: m = cbase
        else:
            opts = F["mouth"][l - 1]; m = opts[alt % len(opts)]; alt += 1
        seq.append((close(m) if closeshot else still(m), dt))
    tmp = pathlib.Path(tempfile.mkdtemp()); lines = []
    for i, (im, s) in enumerate(seq):
        f = tmp / f"{i:04d}.png"; im.save(f); lines += [f"file '{f}'", f"duration {s:.4f}"]
    lines.append(f"file '{tmp / f'{len(seq) - 1:04d}.png'}'")
    (tmp / "list.txt").write_text("\n".join(lines))
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-f", "concat", "-safe", "0", "-i", str(tmp / "list.txt"),
                    "-itsoffset", f"{t0:.3f}", "-i", F["audio"], "-map", "0:v", "-map", "1:a", "-r", "30",
                    "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "20", "-c:a", "aac", "-b:a", "160k", a.out], check=True)
    print(a.out)


if __name__ == "__main__":
    main()
