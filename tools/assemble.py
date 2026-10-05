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
LIBRARY = pathlib.Path(__file__).resolve().parent.parent / "library"   # reusable 3D clips: openers/, loops/, units/
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


def render_card(text: str, path: pathlib.Path, all_bold: bool = False):
    """A cream rounded card: Arabic (big) / transliteration (italic) / English — or plain title lines.
    all_bold: every line bold (convention for scene 1, the card that names today's subject — owner, 2026-10-02)."""
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
            if extra.startswith(("NEW", "Your answer", "Syrian dialect", "Standard Arabic")):   # highlights stand out
                lines.append((extra, LATIN_BOLD, 50, TERRACOTTA if extra.startswith(("NEW", "Syrian")) else TEAL, {}))
            else:
                lines.append((extra, LATIN, 50, CHARCOAL, {}))
    else:
        for i, p in enumerate(parts):
            if all_bold:   # scene 1: every line the same — bold, same size, same colour
                lines.append((p, LATIN_BOLD, 64, TEAL, {}))
            else:
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


def shifted(src: pathlib.Path, frac: float, out: pathlib.Path) -> pathlib.Path:
    """Move a scene picture down by frac of its height; the gap on top is the top edge stretched and blurred."""
    from PIL import ImageFilter
    im = Image.open(src).convert("RGB")
    w, h = im.size
    dy = int(h * frac)
    top = im.crop((0, 0, w, max(4, h // 40))).resize((w, dy)).filter(ImageFilter.GaussianBlur(18))
    canvas = Image.new("RGB", (w, h))
    canvas.paste(top, (0, 0))
    canvas.paste(im.crop((0, 0, w, h - dy)), (0, dy))
    canvas.save(out)
    return out


def title_slug(script: pathlib.Path) -> str:
    """The script header's YouTube title, before ' | ', as a file name: '10-ways-to-say-hello-in-arabic-…'."""
    m = re.search(r"\*\*YouTube title\*\*\s*\|\s*`(.+?)`\s*\|", script.read_text(encoding="utf-8"))
    if not m:
        return ""
    benefit = m.group(1).replace("\\|", "|").split(" | ")[0]
    return re.sub(r"[^a-z0-9]+", "-", benefit.lower()).strip("-")


def clip_fit(src: str, shift, out: str) -> str:
    """Filter: a library clip scaled to the frame; with "shift" (e.g. 0.18) moved down so the face sits below the
    card — the gap on top is the clip's own top edge, stretched and blurred (like shifted() for stills)."""
    base = f"[{src}]scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},setsar=1,fps={FPS}"
    if not shift:
        return f"{base}[{out}]"
    dy = int(H * float(shift)) // 2 * 2
    return (f"{base},split[{out}a][{out}b];[{out}a]crop={W}:{max(4, H // 40)}:0:0,scale={W}:{dy},boxblur=18[{out}t];"
            f"[{out}b]crop={W}:{H - dy}:0:0[{out}m];[{out}t][{out}m]vstack,setsar=1[{out}]")


def render_badge(day: str, path: pathlib.Path):
    img = Image.new("RGBA", (W, 130), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    font = ImageFont.truetype(str(LATIN_BOLD), 46)
    label = f"2 MINUTE ARABIC  ·  {day}"
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
    if stem[:3].isdigit():
        badge_label = f"DAY {int(stem[:3])}"
    elif stem.startswith("x"):   # extras outside the day count: x01-…, x02-…
        badge_label = "ARABIC EXTRAS"
    elif stem.startswith("v"):   # vocabulary Shorts: v01-cafe, v02-street … (owner, 2026-10-05)
        badge_label = "ARABIC VOCAB"
    else:   # part compilations: w01 = Part 1 (Days 1-5), w02 = Part 2 (Days 6-10) …
        k = int(stem[1:3])
        badge_label = f"PART {k} · DAYS {5 * k - 4}–{5 * k}"
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
    render_badge(badge_label, badge)
    render_your_turn(turn)

    # 1. one video segment per scene: image + slow zoom + badge + card
    concat, contact = [], []
    prompts = img_dir / "prompts.json"
    opts = {p["s"]: p for p in json.loads(prompts.read_text(encoding="utf-8")) if "s" in p} if prompts.exists() else {}
    for i, scene in enumerate(tl["scenes"], 1):
        frames = round(scene["end"] * FPS) - round(scene["start"] * FPS)
        o = opts.get(i, {})
        image = img_dir / f"s{i:02d}.png"
        if "same" in o:   # "same" links win over any leftover file from an older numbering
            image = img_dir / f"s{o['same']:02d}.png"
            o = {**opts.get(o["same"], {}), **o}
        clip = LIBRARY / f"{o['clip']}{'-loop' if o.get('clip_mode') == 'loop' else ''}.mp4" if "clip" in o else None
        if clip is not None and not clip.exists():
            sys.exit(f"missing library clip {clip}")
        if clip is None and not image.exists():
            sys.exit(f"missing image {image}")
        if o.get("shift") and clip is None:   # "shift": 0.2 → picture moved down 20 % so faces sit below the card
            image = shifted(image, o["shift"], seg_dir / f"s{i:02d}-shifted.png")
        overlays = ["-i", str(badge)]
        fit = f"scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},setsar=1,fps={FPS}"
        if clip is not None and o.get("clip_mode", "once") == "once":
            # owner's rule (2026-10-01): the opener plays once, its final pose holds 1 s, then the scene's own picture
            # takes over with the usual slow zoom — no long freeze, no extra waving
            joined = seg_dir / f"s{i:02d}-clip.mp4"
            hold = float(o.get("hold", 1.0))
            n_clip = round((float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of",
                                                  "csv=p=0", str(clip)], capture_output=True, text=True).stdout) + hold) * FPS)
            rest = frames - n_clip
            if not image.exists() and rest > FPS // 2:   # no scene picture: continue from the opener's last frame
                image = seg_dir / f"s{i:02d}-lastframe.png"
                run(["ffmpeg", "-v", "error", "-y", "-sseof", "-0.1", "-i", str(LIBRARY / f"{o['clip']}.mp4"),
                     "-update", "1", "-frames:v", "1", str(image)])
                if o.get("shift"):   # match the shifted opener exactly, so the hand-over is seamless
                    image = shifted(image, o["shift"], seg_dir / f"s{i:02d}-lastframe-shifted.png")
            if image.exists() and rest > FPS // 2:
                run(["ffmpeg", "-v", "error", "-y", "-i", str(clip), "-loop", "1", "-i", str(image), "-filter_complex",
                     f"{clip_fit('0:v', o.get('shift'), 'c0')};[c0]"
                     f"tpad=stop_mode=clone:stop_duration={hold}[a];"
                     f"[1:v]scale={W * 2}:{H * 2}:force_original_aspect_ratio=increase,crop={W * 2}:{H * 2},"
                     f"zoompan=z='1+0.05*on/{rest}':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={rest}:s={W}x{H}:fps={FPS},"
                     f"setsar=1[b];[a][b]concat=n=2:v=1[v]", "-map", "[v]", "-frames:v", str(frames), "-c:v", "libx264",
                     "-crf", "16", "-pix_fmt", "yuv420p", str(joined)])
                clip = joined
        elif clip is not None and o.get("clip_mode") == "tail" and (LIBRARY / f"{o['clip']}-tail.mp4").exists():
            # optional: entrance, then its eased tail pendulum repeated
            joined = seg_dir / f"s{i:02d}-clip.mp4"
            reps = max(1, int(frames / FPS / 1.6) + 1)
            run(["ffmpeg", "-v", "error", "-y", "-i", str(clip), "-stream_loop", str(reps), "-i",
                 str(LIBRARY / f"{o['clip']}-tail.mp4"), "-filter_complex", "[0:v][1:v]concat=n=2:v=1[v]", "-map", "[v]",
                 "-c:v", "libx264", "-crf", "16", "-pix_fmt", "yuv420p", str(joined)])
            clip = joined
        if clip is not None:
            # library clip: "once" (default) = opener + 1-s hold (+ the scene picture); "loop" repeats it
            src = (["-stream_loop", "-1"] if o.get("clip_mode") == "loop" else []) + ["-i", str(clip)]
            chain = f"[0:v]{fit},tpad=stop_mode=clone:stop_duration=600[bg];[bg][1:v]overlay=0:40[b1]"
        elif o.get("motion") in ("still", "fade"):
            # still picture (no zoom); "fade" adds a slow fade in and out (for photo-only scenes)
            src = ["-loop", "1", "-i", str(image)]
            fade = (f",fade=t=in:st=0:d=0.5,fade=t=out:st={max(frames / FPS - 0.5, 0):.2f}:d=0.5"
                    if o.get("motion") == "fade" else "")
            chain = f"[0:v]{fit}{fade}[bg];[bg][1:v]overlay=0:40[b1]"
        else:
            src = ["-loop", "1", "-i", str(image)]
            chain = (f"[0:v]scale={W * 2}:{H * 2}:force_original_aspect_ratio=increase,crop={W * 2}:{H * 2},"
                     f"zoompan=z='1+0.05*on/{max(frames, 1)}':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)'"
                     f":d={frames}:s={W}x{H}:fps={FPS},setsar=1[bg];[bg][1:v]overlay=0:40[b1]")
        last = "b1"
        if screens[i - 1]:
            card = out_dir / "cards" / f"s{i:02d}.png"
            render_card(screens[i - 1], card, all_bold=(i == 1))
            overlays += ["-i", str(card)]
            chain += f";[b1][2:v]overlay=0:170[b2]"
            last = "b2"
        seg = seg_dir / f"s{i:02d}.mp4"
        run(["ffmpeg", "-v", "error", "-y", *src, *overlays, "-filter_complex", chain,
             "-map", f"[{last}]", "-frames:v", str(frames), "-c:v", "libx264", "-crf", "18", "-preset", "medium",
             "-pix_fmt", "yuv420p", "-r", str(FPS), str(seg)])
        concat.append(f"file '{seg.resolve()}'")
        print(f"  scene {i:02d}  {frames / FPS:5.1f}s  {scene['name']}")
    (seg_dir / "list.txt").write_text("\n".join(concat) + "\n")
    used = sorted({o["clip"] for o in opts.values() if "clip" in o})
    idx_file = LIBRARY / "index.json"
    if used and idx_file.exists() and args.out.resolve() == (LIBRARY.parent / "output").resolve():   # rotation log
        idx = json.loads(idx_file.read_text(encoding="utf-8"))
        for u in idx:
            if u["name"] in used and stem not in u["used_in"]:
                u["used_in"].append(stem)
        idx_file.write_text(json.dumps(idx, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
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
    final = out_dir / f"{title_slug(args.script) or stem}.mp4"   # owner (2026-10-01): one final file, named after its title
    inputs = ["-i", str(video_only), "-i", str(turn), "-i", str(voice)]
    vchain = f"[0:v][1:v]overlay=0:1400:enable='{enable}'[v0]"
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
    # our own animated SUBSCRIBE + bell (tools/make_subscribe.py), shown while the narrator asks to subscribe
    # (not at the very end), with a click on each button and a bell "ding"
    sub_mov = HERE.parent / "assets" / "subscribe.mov"
    click, ding = HERE.parent / "assets" / "click.wav", HERE.parent / "assets" / "ding.wav"
    if sub_mov.exists() and click.exists() and ding.exists():
        sys.path.insert(0, str(HERE))
        from make_subscribe import CLICK_TIMES, DING_TIME, DUR
        ask = next((c for c in tl["clips"] if c["speaker"].startswith("narrator") and "subscribe" in c["text"].lower()),
                   None)
        start = max(ask["start"] - 0.5, 0.0) if ask else max(tl["duration"] - DUR, 0.0)
        end = min(start + DUR, tl["duration"])
        idx = 3 + len(tl.get("videos", []))
        inputs += ["-i", str(sub_mov)]
        vchain += (f";[{idx}:v]format=rgba,setpts=PTS-STARTPTS+{start:.3f}/TB[sub];"
                   f"[{last}][sub]overlay=0:930:eof_action=pass:enable='between(t,{start:.3f},{end:.3f})'[vs]")
        last = "vs"
        sounds = [(click, CLICK_TIMES[0], 0.5), (click, CLICK_TIMES[1], 0.5), (ding, DING_TIME, 0.35)]
        for j, (wav, at, vol) in enumerate(sounds):
            inputs += ["-i", str(wav)]
            achain += (f";[{idx + 1 + j}:a]volume={vol},aformat=channel_layouts=mono,"
                       f"adelay={round((start + at) * 1000)}:all=1[sx{j}]")
            mix.append(f"[sx{j}]")
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
    old_name = out_dir / f"{stem}.mp4"
    if final != old_name and old_name.exists():   # no second copy under the working name
        old_name.unlink()
    print(f"done: {final}")


if __name__ == "__main__":
    main()
