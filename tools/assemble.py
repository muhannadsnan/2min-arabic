#!/usr/bin/env python3
"""Assemble a finished vertical video from a script, its voiceover (make_audio.py) and its scene images.

    python3 tools/assemble.py videos/002-10-most-useful-phrases.md
        [--audio audio] [--images images] [--out output]

Inputs:
    audio/<video>/voiceover.wav, timeline.json, captions.srt     (from tools/make_audio.py)
    images/<video>/sNN.png   one image per scene, NN = scene number in the script (01, 02, …)
Output:
    output/<video>/<video>.mp4    1080×1920, 30 fps, H.264, AAC, −14 LUFS, captions burned in
    output/<video>/cards/         the rendered text cards (for checking)
    output/<video>/contact.png    one frame per scene (for the quality check)

Per scene: the image with a slow zoom · a text card built from the scene's "🔤 On screen:" line (Arabic with
tashkeel · transliteration · English) · a "DAY N" badge. During every ⏸️ pause a "YOUR TURN" label appears.
English narration is burned in as captions (Arabic lines are already on the card).
"""
import argparse
import json
import pathlib
import re
import shutil
import subprocess
import sys

from PIL import Image, ImageDraw, ImageFont

W, H, FPS = 1080, 1920, 30
FONTS = pathlib.Path("/usr/share/fonts/truetype/noto")
AR_FONT = FONTS / "NotoNaskhArabic-Bold.ttf"
LATIN_BOLD = FONTS / "NotoSans-Bold.ttf"
LATIN = FONTS / "NotoSans-Regular.ttf"
LATIN_ITALIC = FONTS / "NotoSans-Italic.ttf"
TEAL, TERRACOTTA, CHARCOAL, CREAM = (31, 95, 91), (192, 99, 58), (51, 51, 51), (255, 246, 233, 255)
HERE = pathlib.Path(__file__).resolve().parent
CLIPS_DIR = HERE.parent / "footage" / "clips"
ARABIC = re.compile(r"[\u0600-\u06FF]")
SCENE = re.compile(r"^### 🎬 (.+?)(?:\s+·\s+[\d:–-]+)?\s*$")
ON_SCREEN = re.compile(r"^🔤 \*\*On screen[^:]*:\*\*\s*(.+)$")


def run(cmd):
    subprocess.run(cmd, check=True)


def clean(text: str) -> str:
    """Drop markdown and characters the fonts can't draw (emoji)."""
    text = text.replace("*", "").replace("`", "")
    text = re.sub(r"_{2,}", "…", text)  # blanks: the Arabic font has no underscore
    text = text.replace("→", ",")      # the bold Latin font has no arrow glyph
    keep = lambda ch: ord(ch) < 0x2190 or 0x0600 <= ord(ch) <= 0x06FF or ch in "—–·’“”…"
    return " ".join("".join(ch for ch in text if keep(ch)).split())


def on_screen_by_scene(script: pathlib.Path):
    texts, current = [], None
    for line in script.read_text(encoding="utf-8").splitlines():
        if SCENE.match(line):
            texts.append(None)
        elif (m := ON_SCREEN.match(line)) and texts and texts[-1] is None:
            texts[-1] = m.group(1)
    return texts


def fit(draw, text, font_path, size, max_w, **kw):
    while size > 20:
        font = ImageFont.truetype(str(font_path), size)
        box = draw.textbbox((0, 0), text, font=font, **kw)
        if box[2] - box[0] <= max_w:
            return font, box
        size -= 4
    return font, box


def render_card(text: str, path: pathlib.Path):
    """A cream rounded card: Arabic (big) / transliteration (italic) / English — or plain title lines."""
    parts = [clean(p) for p in text.split(" · ") if clean(p)]
    img = Image.new("RGBA", (W, 700), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    lines = []  # (text, font_path, size, color, kw)
    if parts and ARABIC.search(parts[0]) and not re.search(r"[A-Za-z]", parts[0]):
        arabic = parts[0].replace("…", "").strip()  # the Arabic font has no ellipsis: show the word only
        lines.append((arabic, AR_FONT, 130, TEAL, {"direction": "rtl", "language": "ar"}))
        rest = parts[1:]
        if rest:
            lines.append((rest[0], LATIN_ITALIC, 60, TERRACOTTA, {}))
        for extra in rest[1:]:
            lines.append((extra, LATIN, 50, CHARCOAL, {}))
    else:
        for i, p in enumerate(parts):
            lines.append((p, LATIN_BOLD if i == 0 else LATIN, 72 if i == 0 else 54, TEAL if i == 0 else CHARCOAL, {}))
    y, drawn = 50, []
    for txt, font_path, size, color, kw in lines:
        font, box = fit(d, txt, font_path, size, W - 200, **kw)
        drawn.append((txt, font, box, color, kw, y))
        y += (box[3] - box[1]) + 38
    height = y + 12
    card = Image.new("RGBA", (W, height), (0, 0, 0, 0))
    d = ImageDraw.Draw(card)
    d.rounded_rectangle((60, 10, W - 60, height - 10), radius=40, fill=CREAM)
    for txt, font, box, color, kw, ty in drawn:
        d.text(((W - (box[2] - box[0])) / 2 - box[0], ty - box[1]), txt, font=font, fill=color, **kw)
    card.save(path)
    return height


def render_badge(day: str, path: pathlib.Path):
    img = Image.new("RGBA", (W, 130), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    font = ImageFont.truetype(str(LATIN_BOLD), 46)
    label = f"2 MINUTE ARABIC  ·  DAY {day}"
    box = d.textbbox((0, 0), label, font=font)
    w = box[2] - box[0] + 80
    x = (W - w) // 2
    d.rounded_rectangle((x, 30, x + w, 110), radius=40, fill=(255, 200, 0, 245))
    d.text((x + 40 - box[0], 70 - (box[3] + box[1]) / 2), label, font=font, fill=(25, 25, 25))
    img.save(path)


def render_your_turn(path: pathlib.Path):
    img = Image.new("RGBA", (W, 170), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    font = ImageFont.truetype(str(LATIN_BOLD), 70)
    label = "YOUR TURN — SAY IT!"
    box = d.textbbox((0, 0), label, font=font)
    w = box[2] - box[0] + 100
    x = (W - w) // 2
    d.rounded_rectangle((x, 20, x + w, 150), radius=65, fill=(31, 95, 91, 240))
    d.text((x + 50 - box[0], 85 - (box[3] + box[1]) / 2), label, font=font, fill=(255, 255, 255))
    img.save(path)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("script", type=pathlib.Path)
    ap.add_argument("--audio", type=pathlib.Path, default=pathlib.Path("audio"))
    ap.add_argument("--images", type=pathlib.Path, default=pathlib.Path("images"))
    ap.add_argument("--out", type=pathlib.Path, default=pathlib.Path("output"))
    args = ap.parse_args()

    stem = args.script.stem
    day = str(int(stem[:3]))
    audio_dir, img_dir, out_dir = args.audio / stem, args.images / stem, args.out / stem
    tl = json.loads((audio_dir / "timeline.json").read_text(encoding="utf-8"))
    screens = on_screen_by_scene(args.script)
    if len(screens) != len(tl["scenes"]):
        sys.exit(f"scene count mismatch: script {len(screens)} vs timeline {len(tl['scenes'])}")
    (out_dir / "cards").mkdir(parents=True, exist_ok=True)
    seg_dir = out_dir / "segments"
    shutil.rmtree(seg_dir, ignore_errors=True)
    seg_dir.mkdir()

    badge, turn = out_dir / "cards" / "badge.png", out_dir / "cards" / "your-turn.png"
    render_badge(day, badge)
    render_your_turn(turn)

    # 1. one video segment per scene: image + slow zoom + badge + card
    concat, contact = [], []
    for i, scene in enumerate(tl["scenes"], 1):
        frames = round(scene["end"] * FPS) - round(scene["start"] * FPS)
        image = img_dir / f"s{i:02d}.png"
        if not image.exists():
            sys.exit(f"missing image {image}")
        overlays = ["-i", str(badge)]
        chain = (f"[0:v]scale={W * 2}:{H * 2}:force_original_aspect_ratio=increase,crop={W * 2}:{H * 2},"
                 f"zoompan=z='1+0.05*on/{max(frames, 1)}':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)'"
                 f":d={frames}:s={W}x{H}:fps={FPS},setsar=1[bg];[bg][1:v]overlay=0:40[b1]")
        last = "b1"
        if screens[i - 1]:
            card = out_dir / "cards" / f"s{i:02d}.png"
            render_card(screens[i - 1], card)
            overlays += ["-i", str(card)]
            chain += f";[b1][2:v]overlay=0:170[b2]"
            last = "b2"
        seg = seg_dir / f"s{i:02d}.mp4"
        run(["ffmpeg", "-v", "error", "-y", "-loop", "1", "-i", str(image), *overlays, "-filter_complex", chain,
             "-map", f"[{last}]", "-frames:v", str(frames), "-c:v", "libx264", "-crf", "18", "-preset", "medium",
             "-pix_fmt", "yuv420p", "-r", str(FPS), str(seg)])
        concat.append(f"file '{seg.resolve()}'")
        print(f"  scene {i:02d}  {frames / FPS:5.1f}s  {scene['name']}")
    (seg_dir / "list.txt").write_text("\n".join(concat) + "\n")
    video_only = out_dir / "video-only.mp4"
    run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", str(seg_dir / "list.txt"), "-c", "copy",
         str(video_only)])

    # 2. captions: English narration + filmed-clip captions (Arabic lesson lines are on the cards)
    def srt_time(x):
        ms = round(x * 1000)
        return f"{ms // 3600000:02}:{ms // 60000 % 60:02}:{ms // 1000 % 60:02},{ms % 1000:03}"
    items = [(c["start"], c["end"], c["text"]) for c in tl["clips"] if c["speaker"].startswith("narrator")]
    items += [(v["start"], v["end"], v["caption"]) for v in tl.get("videos", []) if v["caption"]]
    items.sort()
    en_srt, ass = out_dir / "captions-en.srt", out_dir / "captions.ass"
    en_srt.write_text("\n".join(f"{k}\n{srt_time(a)} --> {srt_time(b)}\n{txt}\n" for k, (a, b, txt) in enumerate(items, 1)),
                      encoding="utf-8")
    run([sys.executable, str(HERE / "captions" / "srt_to_burnin_ass.py"), str(en_srt), str(ass)])

    # 3. final: YOUR TURN during pauses, captions, voiceover at -14 LUFS (mono measured -17 → dual-mono -14)
    enable = "+".join(f"between(t,{p['start']:.2f},{p['end']:.2f})" for p in tl["pauses"]) or "0"
    voice = audio_dir / "voiceover.wav"
    out = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", str(voice), "-af", "ebur128", "-f", "null", "-"],
                         capture_output=True, text=True).stderr
    measured = float(re.search(r"I:\s+(-?[\d.]+) LUFS", out[out.rfind("Summary:"):]).group(1))
    gain = -17.0 - measured
    final = out_dir / f"{stem}.mp4"
    inputs = ["-i", str(video_only), "-i", str(turn), "-i", str(voice)]
    vchain = f"[0:v][1:v]overlay=0:1100:enable='{enable}'[v0]"
    achain = f"[2:a]volume={gain:.2f}dB,aformat=channel_layouts=mono[vo]"
    mix, last = ["[vo]"], "v0"
    for k, v in enumerate(tl.get("videos", [])):   # filmed clips: full screen with their own sound
        idx = 3 + k
        inputs += ["-i", str(CLIPS_DIR / f"{v['name']}.mp4")]
        vchain += (f";[{idx}:v]fps={FPS},scale={W}:{H},setsar=1,setpts=PTS-STARTPTS+{v['start']:.3f}/TB[c{k}];"
                   f"[{last}][c{k}]overlay=0:0:eof_action=pass:enable='between(t,{v['start']:.3f},{v['end']:.3f})'[v{k + 1}]")
        last = f"v{k + 1}"
        delay = round(v["start"] * 1000)
        achain += f";[{idx}:a]aformat=channel_layouts=mono,adelay={delay}:all=1[ca{k}]"
        mix.append(f"[ca{k}]")
    # our own animated SUBSCRIBE + bell (tools/make_subscribe.py) over the goodbye clip, with click sounds
    sub_mov, click = HERE.parent / "assets" / "subscribe.mov", HERE.parent / "assets" / "click.wav"
    goodbye = next((v for v in tl.get("videos", []) if v["name"] == "goodbye"), None)
    if goodbye and sub_mov.exists() and click.exists():
        sys.path.insert(0, str(HERE))
        from make_subscribe import CLICK_TIMES
        idx = 3 + len(tl.get("videos", []))
        inputs += ["-i", str(sub_mov)]
        vchain += (f";[{idx}:v]format=rgba,setpts=PTS-STARTPTS+{goodbye['start']:.3f}/TB[sub];"
                   f"[{last}][sub]overlay=0:150:eof_action=pass:enable='between(t,{goodbye['start']:.3f},{goodbye['end']:.3f})'[vs]")
        last = "vs"
        for j, ct in enumerate(CLICK_TIMES):
            inputs += ["-i", str(click)]
            achain += f";[{idx + 1 + j}:a]volume=0.5,aformat=channel_layouts=mono,adelay={round((goodbye['start'] + ct) * 1000)}:all=1[ck{j}]"
            mix.append(f"[ck{j}]")
    vchain += f";[{last}]subtitles={ass}[v]"
    if len(mix) > 1:
        achain += f";{''.join(mix)}amix=inputs={len(mix)}:normalize=0:duration=first[m]"
    else:
        achain += ";[vo]anull[m]"
    achain += ";[m]alimiter=limit=0.79:level=false,pan=stereo|c0=c0|c1=c0[a]"
    run(["ffmpeg", "-v", "error", "-y", *inputs, "-filter_complex", vchain + ";" + achain,
         "-map", "[v]", "-map", "[a]", "-c:v", "libx264", "-crf", "18", "-preset", "medium", "-pix_fmt", "yuv420p",
         "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-shortest", "-movflags", "+faststart", str(final)])

    # 4. contact sheet: middle frame of each scene
    thumbs = []
    for i, scene in enumerate(tl["scenes"], 1):
        t = (scene["start"] + scene["end"]) / 2
        png = out_dir / "segments" / f"frame{i:02d}.png"
        run(["ffmpeg", "-v", "error", "-y", "-ss", f"{t:.2f}", "-i", str(final), "-frames:v", "1", "-vf", "scale=270:480",
             str(png)])
        thumbs.append(png)
    cols = 6
    sheet = Image.new("RGB", (270 * cols, 480 * ((len(thumbs) + cols - 1) // cols)), "white")
    for k, png in enumerate(thumbs):
        sheet.paste(Image.open(png), ((k % cols) * 270, (k // cols) * 480))
    sheet.save(out_dir / "contact.png")
    video_only.unlink()
    print(f"done: {final}")


if __name__ == "__main__":
    main()
