#!/usr/bin/env python3
"""Put a green-screen character unit on a background (still picture or video), 1080×1920, 30 fps.

    python3 tools/animate/composite.py library/talk/sami-talk-1-loop.mp4 BACKGROUND.png|.mp4 OUT.mp4 \
        [--seconds 6] [--scale 0.95] [--y bottom|center] [--zoom]

Keying is by green dominance (green clearly above red and blue), so olive or teal clothes survive; the green fringe
on hair and edges is pulled down. A still background gets an optional slow zoom (--zoom); a video
background is looped. The character unit is looped to fill --seconds (its loop starts and ends on the same frame).
"""
import argparse
import pathlib
import subprocess

from PIL import Image


def corner_colour(clip):
    tmp = pathlib.Path("/tmp") / f"key-{pathlib.Path(clip).stem}.png"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(clip), "-frames:v", "1", str(tmp)], check=True)
    im = Image.open(tmp).convert("RGB")
    w, h = im.size
    px = [im.getpixel((x, y)) for x in (5, w - 6) for y in (5, h // 3, h // 2)]
    r, g, b = (sorted(c[i] for c in px)[len(px) // 2] for i in range(3))
    return f"0x{r:02X}{g:02X}{b:02X}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("unit")
    ap.add_argument("background")
    ap.add_argument("out")
    ap.add_argument("--seconds", type=float, default=6.0)
    ap.add_argument("--scale", type=float, default=0.95, help="character height as a share of the frame")
    ap.add_argument("--y", choices=["bottom", "center"], default="bottom")
    ap.add_argument("--zoom", action="store_true", help="slow zoom on a still background")
    ap.add_argument("--dominance", type=float, default=1.3, help="green must exceed red and blue by this factor")
    a = ap.parse_args()

    key = corner_colour(a.unit)   # reported only (sanity check that the corners really are green)
    frames = round(a.seconds * 30)
    still = pathlib.Path(a.background).suffix.lower() in (".png", ".jpg", ".jpeg", ".webp")
    bg_in = ["-loop", "1", "-i", a.background] if still else ["-stream_loop", "-1", "-i", a.background]
    if still and a.zoom:
        bg = (f"[0:v]scale=2160:3840:force_original_aspect_ratio=increase,crop=2160:3840,"
              f"zoompan=z='1+0.05*on/{frames}':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={frames}:s=1080x1920:fps=30[bg]")
    else:
        bg = "[0:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,setsar=1,fps=30[bg]"
    h = int(1920 * a.scale)
    y = "H-h" if a.y == "bottom" else "(H-h)/2"
    # strict green-dominance key: only pixels that are clearly, brightly green go transparent — a chroma-distance key
    # made Sami's olive hoodie half see-through. Green fringe on edges is pulled down to the red/blue level.
    k = a.dominance
    key_px = f"gt(g(X,Y),{k}*r(X,Y))*gt(g(X,Y),{k}*b(X,Y))*gt(g(X,Y),90)"
    chain = (f"{bg};[1:v]fps=30,scale=-2:{h},format=rgba,"
             f"geq=r='r(X,Y)':g='min(g(X,Y),1.12*max(r(X,Y),b(X,Y)))':b='b(X,Y)':a='if({key_px},0,255)'[fg];"
             f"[bg][fg]overlay=(W-w)/2:{y}:shortest=0[v]")
    subprocess.run(["ffmpeg", "-v", "error", "-y", *bg_in, "-stream_loop", "-1", "-i", a.unit, "-filter_complex", chain,
                    "-map", "[v]", "-frames:v", str(frames), "-c:v", "libx264", "-crf", "18", "-preset", "medium",
                    "-pix_fmt", "yuv420p", "-an", a.out], check=True)
    print(f"{a.out} ({a.seconds}s, key {key})")


if __name__ == "__main__":
    main()
