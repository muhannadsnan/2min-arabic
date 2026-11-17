#!/usr/bin/env python3
"""Sleep / listening-practice video (owner 2026-11-17, plan: videos/sleep01-plan.md).

    python3 tools/sleep_video.py sleep01 [--rounds 8] [--only-round normal|slow]

Inputs: videos/<stem>-lines.json (chapters → lines with ar/tr/en + the recorded Arabic "file"), the narrator clips in
audio/<stem>-narration/ (c01-01.wav …, ch01.wav, open.wav — voiced by library/work/sleep01-narration.sh), the night
pictures images/<stem>/c01.png … (1920×1080). Output: output/<stem>/<stem>.mp4 (= round 1 + round 2 + slow rounds) +
chapters.txt + check frames.

One line = English → 0.6 s → the owner's Arabic → pause → the Arabic again → pause. Rounds 1–2 "normal" (chapter
line, −20 LUFS); rounds 3–N "slow" (longer pauses, no chapter lines, dimmer text, −24 LUFS) — the slow round is
rendered once and copied (said openly in the title). Pauses are sized so one round ≈ 60 minutes.
Static pictures (a very slow zoom shimmered), darkened; each chapter fades in/out over 1 s. Nothing flashes.
"""
import argparse, json, pathlib, re, subprocess, sys, tempfile, shutil
import numpy as np, soundfile as sf
from PIL import Image, ImageDraw, ImageFont

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
from arabic_text import minimal                       # noqa: E402
from make_audio import OWNER_CLARITY, RECORDED_CLEAN   # noqa: E402

SR, FPS, W, H = 48000, 12, 1920, 1080
FONTS = pathlib.Path("/usr/share/fonts/truetype/noto")
AR_FONT, LAT, LAT_I = FONTS / "NotoNaskhArabic-Bold.ttf", FONTS / "NotoSans-Regular.ttf", FONTS / "NotoSans-Italic.ttf"
TRIM = ("silenceremove=start_periods=1:start_threshold=-50dB:start_silence=0.05,areverse,"
        "silenceremove=start_periods=1:start_threshold=-50dB:start_silence=0.08,areverse")
VARIANTS = {"normal": dict(gap=0.6, pause1=3.0, pause2=2.0, chapter_line=True, lufs=-20.0, text_alpha=1.0, dim=0.45),
            "slow":   dict(gap=0.8, pause1=4.0, pause2=3.0, chapter_line=False, lufs=-24.0, text_alpha=0.7, dim=0.38)}


def sh(*a, **k): return subprocess.run(a, check=True, capture_output=True, text=True, **k)


def clip(src, out, owner_voice, recorded):
    """Trim + gentle clean (recorded lines: the course's own chain) + level, 48 kHz mono."""
    if out.exists():
        return
    chain = ((OWNER_CLARITY if owner_voice else "") + RECORDED_CLEAN + ",") if recorded else ""
    sh("ffmpeg", "-v", "error", "-y", "-i", str(src), "-af", chain + TRIM + ",loudnorm=I=-20:TP=-2:LRA=7",
       "-ar", str(SR), "-ac", "1", str(out))


def load(p): a, sr = sf.read(str(p), dtype="float32"); return a if a.ndim == 1 else a.mean(1)


def card(path, ar, tr, en, chapter, alpha):
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(img)
    a = lambda rgb, k=1.0: rgb + (int(255 * alpha * k),)
    # soft dark band behind the text so it reads on any picture
    band = Image.new("RGBA", (W, 520), (8, 12, 30, 0))
    ramp = np.concatenate([np.linspace(0, 1, 110), np.ones(300), np.linspace(1, 0, 110)])   # soft top/bottom edges
    band.putalpha(Image.fromarray(np.repeat((ramp * 150 * alpha).astype("uint8")[:, None], W, 1)))
    img.alpha_composite(band, (0, 280))
    f_ar, f_tr, f_en, f_ch = (ImageFont.truetype(str(AR_FONT), 104), ImageFont.truetype(str(LAT_I), 44),
                             ImageFont.truetype(str(LAT), 46), ImageFont.truetype(str(LAT), 32))
    y = 380
    for txt, f, col, k, kw in ((minimal(ar), f_ar, (234, 223, 196), 1.0, dict(direction="rtl", language="ar")),
                               (tr, f_tr, (200, 191, 168), 0.85, {}), (en, f_en, (170, 180, 200), 0.85, {})):
        if not txt:
            continue
        while d.textlength(txt, font=f, **kw) > W - 160 and f.size > 40:
            f = ImageFont.truetype(f.path, f.size - 6)
        bb = d.textbbox((0, 0), txt, font=f, **kw)
        x = (W - (bb[2] - bb[0])) // 2 - bb[0]
        d.text((x + 3, y + 3), txt, font=f, fill=(0, 0, 0, int(160 * alpha)), **kw)
        d.text((x, y), txt, font=f, fill=a(col, k), **kw)
        y += (bb[3] - bb[1]) + (60 if f is f_ar or f.path == str(AR_FONT) else 34)
    d.text((48, 36), chapter, font=f_ch, fill=a((150, 160, 185), 0.8))
    img.save(path)


def build_round(stem, C, nar, clips_dir, tmp, variant, opening, fade_end, tag):
    v = VARIANTS[variant]
    # pauses sized so the round lasts ~60 min: measure first, then stretch the two pauses evenly
    lines = [(i, j, l) for i, c in enumerate(C, 1) for j, l in enumerate(c["lines"], 1)]
    eng = {(i, j): load(clips_dir / f"n-c{i:02}-{j:02}.wav") for i, j, _ in lines}
    arb = {(i, j): load(clips_dir / f"a-c{i:02}-{j:02}.wav") for i, j, _ in lines}
    chl = {i: load(clips_dir / f"n-ch{i:02}.wav") for i in range(1, len(C) + 1)}
    fixed = sum(len(eng[k]) + 2 * len(arb[k]) for k in eng) / SR + len(lines) * v["gap"]
    if v["chapter_line"]:
        fixed += sum(len(x) / SR + 2.5 for x in chl.values())
    if opening:
        fixed += len(load(clips_dir / "n-open.wav")) / SR + 2.0
    fixed += len(C) * 3.0                                       # 1.5 s air at each chapter start and end
    spare = max(0.0, 3600.0 - fixed) / len(lines)
    p1, p2 = v["pause1"] + spare * 0.55, v["pause2"] + spare * 0.45
    print(f"  {tag}: {len(lines)} lines, pauses {p1:.1f} s + {p2:.1f} s", flush=True)
    sil = lambda s: np.zeros(int(s * SR), dtype="float32")
    segs, chapters, t = [], [], 0.0
    for i, c in enumerate(C, 1):
        audio, cards, t0 = [sil(1.5)], [], 0.0
        if opening and i == 1:
            o = load(clips_dir / "n-open.wav"); audio += [o, sil(2.0)]
        if v["chapter_line"]:
            audio += [chl[i], sil(2.5)]
        pos = sum(len(x) for x in audio) / SR
        for j, l in enumerate(c["lines"], 1):
            k = (i, j); seq = [eng[k], sil(v["gap"]), arb[k], sil(p1), arb[k], sil(p2)]
            cards.append((pos, l)); audio += seq; pos += sum(len(x) for x in seq) / SR
        audio.append(sil(1.5)); a = np.concatenate(audio); dur = len(a) / SR
        if fade_end and i == len(C):
            n = int(30 * SR); a[-n:] *= np.linspace(1, 0, n, dtype="float32")
        wav = tmp / f"{tag}-c{i:02}.wav"; sf.write(str(wav), a, SR)
        # text cards: each shows from its line's start to the next line's start
        lst, label = tmp / f"{tag}-c{i:02}.txt", f"{i} · {c['name']}"
        blank = tmp / "blank.png"
        if not blank.exists():
            Image.new("RGBA", (W, H), (0, 0, 0, 0)).save(blank)
        with open(lst, "w") as f:
            if cards[0][0] > 0:
                f.write(f"file '{blank}'\nduration {cards[0][0]:.3f}\n")
            for n, (st, l) in enumerate(cards):
                png = tmp / f"{tag}-c{i:02}-{n:03}.png"; card(png, l["ar"], l["tr"], l["en"], label, v["text_alpha"])
                end = cards[n + 1][0] if n + 1 < len(cards) else dur
                f.write(f"file '{png}'\nduration {end - st:.3f}\n")
            f.write(f"file '{png}'\n")
        pic = ROOT / "images" / stem / f"c{i:02}.png"
        seg = tmp / f"{tag}-c{i:02}.mp4"
        vf = (f"[0:v]scale={W}:{H},setsar=1,eq=brightness=0:contrast=1,colorchannelmixer=rr={v['dim']}:gg={v['dim']}:bb={v['dim'] + 0.04}[bg];"
              f"[1:v]fps={FPS},format=rgba[tx];[bg][tx]overlay=0:0:shortest=0,format=yuv420p,"
              f"fade=t=in:st=0:d=1,fade=t=out:st={dur - (30 if fade_end and i == len(C) else 1):.3f}:d={30 if fade_end and i == len(C) else 1}[v]")
        sh("ffmpeg", "-v", "error", "-y", "-loop", "1", "-framerate", str(FPS), "-t", f"{dur:.3f}", "-i", str(pic),
           "-f", "concat", "-safe", "0", "-i", str(lst), "-i", str(wav), "-filter_complex", vf, "-map", "[v]", "-map", "2:a",
           "-t", f"{dur:.3f}", "-r", str(FPS), "-c:v", "libx264", "-preset", "medium", "-crf", "24", "-tune", "stillimage",
           "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "128k", "-ar", str(SR), "-ac", "1", str(seg))
        segs.append(seg); chapters.append((t, c["name"])); t += dur
    out = tmp / f"{tag}.mp4"; lst = tmp / f"{tag}.list"
    lst.write_text("".join(f"file '{s}'\n" for s in segs))
    sh("ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", str(lst), "-c", "copy", str(out))
    # level the whole round to the variant's loudness (gain only — the clips are already even)
    r = subprocess.run(["ffmpeg", "-nostats", "-i", str(out), "-af", "ebur128", "-f", "null", "-"], capture_output=True, text=True)
    lu = float(re.findall(r"\bI:\s+(-?[\d.]+) LUFS", r.stderr)[-1]); g = v["lufs"] - lu
    lev = tmp / f"{tag}-lev.mp4"
    sh("ffmpeg", "-v", "error", "-y", "-i", str(out), "-c:v", "copy", "-af", f"volume={g:.2f}dB,alimiter=limit=0.7:level=false",
       "-c:a", "aac", "-b:a", "128k", "-ar", str(SR), "-ac", "1", str(lev))
    return lev, chapters, t


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("stem"); ap.add_argument("--rounds", type=int, default=8)
    a = ap.parse_args(); stem = a.stem
    C = json.load(open(ROOT / "videos" / f"{stem}-lines.json", encoding="utf-8"))
    nar = ROOT / "audio" / f"{stem}-narration"
    od = ROOT / "output" / stem; od.mkdir(parents=True, exist_ok=True)
    clips_dir = od / "clips"; clips_dir.mkdir(exist_ok=True)
    print("clips …", flush=True)
    clip(nar / "open.wav", clips_dir / "n-open.wav", False, False)
    for i, c in enumerate(C, 1):
        clip(nar / f"ch{i:02}.wav", clips_dir / f"n-ch{i:02}.wav", False, False)
        for j, l in enumerate(c["lines"], 1):
            clip(nar / f"c{i:02}-{j:02}.wav", clips_dir / f"n-c{i:02}-{j:02}.wav", False, False)
            clip(ROOT / l["file"], clips_dir / f"a-c{i:02}-{j:02}.wav", l["speaker"] != "lina", True)
    tmp = pathlib.Path(tempfile.mkdtemp(prefix="sleep-", dir=od))
    try:
        r1, ch1, d1 = build_round(stem, C, nar, clips_dir, tmp, "normal", True, False, "r1")
        r2, _, d2 = build_round(stem, C, nar, clips_dir, tmp, "normal", False, False, "r2")
        rs, _, ds = build_round(stem, C, nar, clips_dir, tmp, "slow", False, False, "rs")
        rl, _, dl = build_round(stem, C, nar, clips_dir, tmp, "slow", False, True, "rl")
        order = [r1, r2] + [rs] * (a.rounds - 3) + [rl]
        lst = tmp / "all.list"; lst.write_text("".join(f"file '{p}'\n" for p in order))
        out = od / f"{stem}.mp4"
        sh("ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", str(lst), "-c", "copy", "-movflags", "+faststart", str(out))
        hms = lambda s: f"{int(s // 3600)}:{int(s % 3600 // 60):02}:{int(s % 60):02}"
        rows = [(s, f"{n}") for s, n in ch1] + [(d1, "Round 2 (repeat)")]
        tt = d1 + d2
        for k in range(3, a.rounds + 1):
            rows.append((tt, f"Round {k} (slow, quiet)")); tt += ds
        (od / "chapters.txt").write_text("\n".join(f"{hms(s)} {n}" for s, n in rows) + "\n")
        for p in (r1, r2, rs, rl):
            shutil.copy2(p, od / f"{stem}-{p.stem.split('-')[0]}.mp4")
        print(out, f"{hms(d1 + d2 + ds * (a.rounds - 3) + dl)}", flush=True)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    main()
