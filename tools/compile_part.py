#!/usr/bin/env python3
"""Build a horizontal (16:9) "Part" compilation of 5 daily videos, for long-form watch time.

    python3 tools/compile_part.py parts/part-01.json

The JSON lists the segments in order: {"title", "file", "start", "end", "words": [[arabic, translit, english], ...]}.
Each vertical segment is shown in the middle (1080 px tall); the left panel shows the brand, the part and the chapter
list (current chapter highlighted); the right panel shows that segment's words. Output: output/<name>/<name>.mp4,
chapters.txt (for the description) and contact.png.
"""
import json
import pathlib
import re
import subprocess
import sys

from PIL import Image, ImageDraw, ImageFont

ROOT = pathlib.Path(__file__).resolve().parent.parent
W, H, FPS = 1920, 1080, 30
VW = 608                      # 1080 × 9/16
PANEL = (W - VW) // 2
FONTS = pathlib.Path("/usr/share/fonts/truetype/noto")
BOLD, REG, AR = FONTS / "NotoSans-Bold.ttf", FONTS / "NotoSans-Regular.ttf", FONTS / "NotoNaskhArabic-Bold.ttf"
CREAM, TEAL, TERRA, CHAR, YELLOW = (255, 246, 233), (31, 95, 91), (192, 99, 58), (51, 51, 51), (255, 200, 0)


def run(cmd):
    subprocess.run(cmd, check=True)


def duration(path):
    return float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0",
                                 str(path)], capture_output=True, text=True).stdout)


def fit(d, text, path, size, max_w, **kw):
    while size > 16:
        f = ImageFont.truetype(str(path), size)
        b = d.textbbox((0, 0), text, font=f, **kw)
        if b[2] - b[0] <= max_w:
            return f
        size -= 2
    return f


def panel_image(part, segments, idx, out):
    img = Image.new("RGB", (W, H), CREAM)
    d = ImageDraw.Draw(img)
    # left panel: brand, part, chapters
    d.rectangle((0, 0, PANEL, H), fill=(246, 232, 214))
    d.rounded_rectangle((60, 70, PANEL - 60, 150), radius=40, fill=YELLOW)
    f = fit(d, "2 MINUTE ARABIC", BOLD, 44, PANEL - 180)
    b = d.textbbox((0, 0), "2 MINUTE ARABIC", font=f)
    d.text(((PANEL - (b[2] - b[0])) / 2 - b[0], 110 - (b[3] + b[1]) / 2), "2 MINUTE ARABIC", font=f, fill=(25, 25, 25))
    d.text((70, 190), part["title"], font=ImageFont.truetype(str(BOLD), 46), fill=TEAL)
    d.text((70, 250), part["subtitle"], font=ImageFont.truetype(str(REG), 30), fill=CHAR)
    y = 340
    for k, seg in enumerate(segments):
        cur = k == idx
        if cur:
            d.rounded_rectangle((55, y - 10, PANEL - 55, y + 52), radius=26, fill=TEAL)
        f = fit(d, seg["title"], BOLD if cur else REG, 34, PANEL - 170)
        if cur:   # drawn triangle (the fonts have no ▶ glyph)
            d.polygon([(78, y + 10), (78, y + 34), (98, y + 22)], fill=(255, 255, 255))
        d.text((112, y), seg["title"], font=f, fill=(255, 255, 255) if cur else CHAR)
        y += 70
    # right panel: words of this segment
    x0 = PANEL + VW
    d.rectangle((x0, 0, W, H), fill=(246, 232, 214))
    words = segments[idx].get("words", [])
    heading = segments[idx].get("panel_title", "Words in this part" if words else "")
    d.text((x0 + 60, 80), heading, font=ImageFont.truetype(str(BOLD), 40), fill=TEAL)
    if not words and segments[idx].get("panel_text"):
        yy = 170
        for line in segments[idx]["panel_text"]:
            d.text((x0 + 60, yy), line, font=ImageFont.truetype(str(REG), 34), fill=CHAR)
            yy += 56
    row = min(92, (H - 190) // max(len(words), 1))
    ar_size = min(52, int(row * 0.62))
    y = 170
    for ar, tr, en in words:
        fa = fit(d, ar, AR, ar_size, PANEL - 140, direction="rtl", language="ar")
        b = d.textbbox((0, 0), ar, font=fa, direction="rtl", language="ar")
        d.text((W - 60 - (b[2] - b[0]) - b[0], y - b[1]), ar, font=fa, fill=TEAL, direction="rtl", language="ar")
        room = (W - 60 - (b[2] - b[0])) - (x0 + 60) - 28      # space left of the Arabic word
        small = fit(d, en, REG, max(22, int(ar_size * 0.6)), room)
        d.text((x0 + 60, y), en, font=small, fill=CHAR)
        d.text((x0 + 60, y + int(ar_size * 0.66)), tr, font=fit(d, tr, FONTS / "NotoSans-Italic.ttf",
                                                                  max(20, int(ar_size * 0.5)), room), fill=TERRA)
        y += row
    img.save(out)


MISSING_IN_ARABIC_FONT = "/…_"   # render as □ in Noto Naskh Arabic


def main():
    spec = json.loads(pathlib.Path(sys.argv[1]).read_text(encoding="utf-8"))
    name = spec["name"]
    out_dir = ROOT / "output" / name
    seg_dir = out_dir / "segments"
    seg_dir.mkdir(parents=True, exist_ok=True)
    segs, lst, chapters, t = spec["segments"], [], [], 0.0
    for k, seg in enumerate(segs):
        src = next(ROOT.glob(seg["file"]))
        start, end = seg.get("start", 0.0), seg.get("end") or duration(src)
        bg = seg_dir / f"panel{k:02d}.png"
        panel_image(spec, segs, k, bg)
        out = seg_dir / f"seg{k:02d}.mp4"
        run(["ffmpeg", "-v", "error", "-y", "-loop", "1", "-i", str(bg), "-ss", f"{start}", "-to", f"{end}", "-i", str(src),
             "-filter_complex",
             f"[1:v]fps={FPS},scale={VW}:{H},setsar=1[v];[0:v][v]overlay={PANEL}:0:shortest=1,format=yuv420p[o];"
             f"[1:a]aresample=48000,aformat=channel_layouts=stereo,afade=t=in:d=0.05,"
             f"afade=t=out:st={max(end - start - 0.08, 0):.3f}:d=0.08[a]",
             "-map", "[o]", "-map", "[a]", "-c:v", "libx264", "-crf", "18", "-preset", "medium", "-r", str(FPS),
             "-c:a", "aac", "-b:a", "192k", str(out)])
        chapters.append((t, seg["title"]))
        t += duration(out)
        lst.append(f"file '{out.resolve()}'")
        print(f"  {seg['title']:<30} {end - start:6.1f}s")
    (seg_dir / "list.txt").write_text("\n".join(lst) + "\n")
    joined = out_dir / "joined.mp4"
    run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", str(seg_dir / "list.txt"), "-c", "copy",
         str(joined)])
    # one loudness pass over the whole program (-14 LUFS)
    err = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", str(joined), "-af", "ebur128", "-f", "null", "-"],
                         capture_output=True, text=True).stderr
    measured = float(re.search(r"I:\s+(-?[\d.]+) LUFS", err[err.rfind("Summary:"):]).group(1))
    final = out_dir / f"{name}.mp4"
    run(["ffmpeg", "-v", "error", "-y", "-i", str(joined), "-c:v", "copy", "-af",
         f"volume={-14.0 - measured:.2f}dB,alimiter=limit=0.79:level=false", "-c:a", "aac", "-b:a", "192k",
         "-movflags", "+faststart", str(final)])
    joined.unlink()
    fmt = lambda s: f"{int(s // 60)}:{int(s % 60):02d}"
    (out_dir / "chapters.txt").write_text("\n".join(f"{fmt(a)} {b}" for a, b in chapters) + "\n", encoding="utf-8")
    thumbs = []
    for k, (a, _) in enumerate(chapters):
        png = seg_dir / f"frame{k:02d}.png"
        run(["ffmpeg", "-v", "error", "-y", "-ss", f"{a + 6:.1f}", "-i", str(final), "-frames:v", "1", "-vf",
             "scale=640:360", str(png)])
        thumbs.append(Image.open(png))
    sheet = Image.new("RGB", (640 * 2, 360 * ((len(thumbs) + 1) // 2)), "white")
    for k, im in enumerate(thumbs):
        sheet.paste(im, ((k % 2) * 640, (k // 2) * 360))
    sheet.save(out_dir / "contact.png")
    print(f"done: {final} ({fmt(t)})")


if __name__ == "__main__":
    main()
