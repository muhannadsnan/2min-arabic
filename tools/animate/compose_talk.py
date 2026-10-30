#!/usr/bin/env python3
"""Characters v5.1 (owner, 2026-10-26 after the Day 24 pilot): calm green-screen characters that only move when they talk.

    $TTS tools/animate/compose_talk.py scene.json OUT.mp4

scene.json: {"bg": "…png", "seconds": 6.2, "layers": [
    {"still": "…png", "x": 0.28, "h": 0.6,
     "talk": ["…talk1.png", "…talk2.png", …],          # mouth shapes, same head pose
     "speak": [[0.4, 1.9], …],                           # seconds (scene time) when this character speaks
     "react": [{"img": "…png", "from": 2.0, "to": 4.0}], # optional expression changes (laugh, smile)
     "mirror": true                                      # optional: flip so the character faces the other way
    }, …]}
Owner's rules: the character stays still unless speaking; speaking = mostly mouth movement (a new mouth shape ~6×/s,
switched with a quick 0.07-s blend), steady eyes, no big gestures; two-person scenes: they face each other and each
moves only during their own line. Green key with strong despill and a 1-px eroded edge (no green rim).
"""
import json
import pathlib
import subprocess
import sys
import tempfile

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

W, H, FPS = 1080, 1920, 30
_cache = {}


def keyed(path, mirror=False):
    if (path, mirror) in _cache:
        return _cache[path, mirror]
    src = Image.open(path).convert("RGB")
    a = np.asarray(src.transpose(Image.FLIP_LEFT_RIGHT) if mirror else src, dtype=np.float32)
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    dom = g - np.maximum(r, b)
    alpha = np.clip(1.0 - (dom - 12) / 40, 0, 1)
    # dark clothes catch green bounce light (the waiter's trousers were half see-through, owner 2026-10-29): the screen
    # itself is bright, so anything darker than it stays solid, fading over g 80–110
    alpha = np.maximum(alpha, np.clip((110 - g) / 30, 0, 1))
    a[..., 1] = np.minimum(g, np.maximum(r, b) * 1.04)          # despill everywhere: no green tint on hair/edges
    al = Image.fromarray((alpha * 255).astype(np.uint8)).filter(ImageFilter.MinFilter(3)).filter(ImageFilter.GaussianBlur(1.0))
    im = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).convert("RGBA"); im.putalpha(al)
    _cache[path, mirror] = im
    return im


def place(canvas, im, x, h, bg_mean):
    hh = int(H * h); ww = int(im.width * hh / im.height)
    ch = im.resize((ww, hh), Image.LANCZOS)
    arr = np.asarray(ch, dtype=np.float32)
    m = arr[..., :3][arr[..., 3] > 128].mean(axis=0)
    arr[..., :3] = np.clip(arr[..., :3] + (bg_mean - m) * 0.10, 0, 255)
    ch = Image.fromarray(arr.astype(np.uint8), "RGBA")
    x0 = int(W * x - ww / 2)
    sh = Image.new("L", (W, H), 0)
    ImageDraw.Draw(sh).ellipse((x0 + ww * 0.15, H - 60, x0 + ww * 0.85, H + 60), fill=90)
    canvas = Image.composite(Image.new("RGB", (W, H), (20, 15, 10)), canvas, sh.filter(ImageFilter.GaussianBlur(40)))
    canvas.paste(ch, (x0, H - hh), ch)
    return canvas


def state(layer, t):
    """(image path, key) the layer shows at time t."""
    for r in layer.get("react", []):
        if r["from"] <= t < r["to"]:
            return r["img"]
    for s, e in layer.get("speak", []):
        if s <= t < e and layer.get("talk"):
            k = int((t - s) * 6)
            order = [1, 2, 0, 3, 1, 4, 2, 0]                        # varied mouth shapes, never the same twice in a row
            return layer["talk"][order[k % len(order)] % len(layer["talk"])]
    return layer["still"]


def main():
    spec = json.loads(pathlib.Path(sys.argv[1]).read_text())
    out = sys.argv[2]
    src = Image.open(spec["bg"]).convert("RGB")
    s = max(W / src.width, H / src.height)
    src = src.resize((int(src.width * s) + 1, int(src.height * s) + 1), Image.LANCZOS)
    bg = src.crop(((src.width - W) // 2, (src.height - H) // 2, (src.width - W) // 2 + W, (src.height - H) // 2 + H))
    bg_mean = np.asarray(bg, dtype=np.float32).reshape(-1, 3).mean(axis=0)
    n = int(round(spec["seconds"] * FPS))
    tmp = pathlib.Path(tempfile.mkdtemp())
    frames_cache = {}
    prev_key, prev_img, blend_left = None, None, 0
    BL = 2   # frames of quick blend (~0.07 s)
    for i in range(n):
        t = i / FPS
        keys = tuple(state(l, t) for l in spec["layers"])
        if keys not in frames_cache:
            c = bg.copy()
            for l, k in zip(spec["layers"], keys):
                c = place(c, keyed(k, l.get("mirror", False)), l["x"], l["h"], bg_mean)
            frames_cache[keys] = np.asarray(c, dtype=np.float32)
        cur = frames_cache[keys]
        if prev_key is not None and keys != prev_key:
            blend_left, start = BL, prev_img
        if blend_left:
            a = (BL - blend_left + 1) / (BL + 1)
            frame = start * (1 - a) + cur * a; blend_left -= 1
        else:
            frame = cur
        Image.fromarray(frame.astype(np.uint8)).save(tmp / f"{i:05d}.png")
        prev_key, prev_img = keys, frame
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-framerate", str(FPS), "-i", str(tmp / "%05d.png"),
                    "-c:v", "libx264", "-crf", "14", "-pix_fmt", "yuv420p", out], check=True)
    print(f"{out}: {n} frames, {len(frames_cache)} distinct pictures")


if __name__ == "__main__":
    main()
