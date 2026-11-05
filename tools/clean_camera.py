#!/usr/bin/env python3
"""Clean a 16:9 on-camera take of the owner (story intro/outro): cut out retakes and tame the car's boxy echo.

    python3 tools/clean_camera.py SRC.mp4 footage/recordings/s01/intro.mp4 --cut 15.6-26.4 [--cut a-b …] [--ab OUT.wav]

Sound (owner 2026-11-04: "even though I use the mic, the car makes it like a dead echo"): mono + 90 Hz low-cut →
DeepFilterNet (noise + part of the room tail) → EQ against the car's boxiness (−4 dB around 250 Hz, −2 dB at 120 Hz,
+2 dB presence at 4 kHz) → a soft downward expander that shortens the echo tail between words → gentle compression →
−16 LUFS, peak −1.5 dB. Video: each kept part is trimmed, joined with a hard cut (pick cut points where the eyes are
open), 30 fps, the source resolution. --ab writes a before/after sound sample of the first 12 s.
"""
import argparse, os, pathlib, re, subprocess, tempfile

TTS_HOME = pathlib.Path(os.environ.get("TTS_HOME", "/media/msn/GamesLinux/AI/tts"))
DFN = """
import sys
from df.enhance import enhance, init_df, load_audio, save_audio
model, state, _ = init_df()
audio, _ = load_audio(sys.argv[1], sr=state.sr())
save_audio(sys.argv[2], enhance(model, state, audio, atten_lim_db=30), state.sr())   # keep a faint natural room tone
"""
EQ = ("equalizer=f=120:t=o:w=1:g=-2,equalizer=f=250:t=o:w=1:g=-4,equalizer=f=4000:t=o:w=1.5:g=2,"
      "agate=threshold=0.022:ratio=3:range=0.08:attack=4:release=110:knee=4,"
      "acompressor=threshold=-22dB:ratio=2.5:attack=15:release=250")


def run(cmd, **kw):
    return subprocess.run(cmd, check=True, **kw)


def loudness(path):
    err = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", str(path), "-af", "ebur128", "-f", "null", "-"],
                         capture_output=True, text=True).stderr
    return float(re.search(r"I:\s+(-?[\d.]+) LUFS", err[err.rfind("Summary:"):]).group(1))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("src", type=pathlib.Path); ap.add_argument("dst", type=pathlib.Path)
    ap.add_argument("--cut", action="append", default=[], help="a-b seconds to remove (repeatable)")
    ap.add_argument("--ab", type=pathlib.Path, help="before/after sound sample")
    ap.add_argument("--patch", action="append", default=[], help="START=FILE.wav: put a separately cleaned piece over the "
                    "sound from START s (source time), level-matched, 30 ms crossfades — e.g. the intro hook restored by "
                    "Resemble Enhance (owner's pick 2026-11-05)")
    ap.add_argument("--look", default="", help="extra video filter for light/colour, e.g. the outro's "
                    "'eq=brightness=0.03:contrast=1.07:saturation=1.06,hqdn3d=1.5:1.5:4:4'")
    a = ap.parse_args()
    dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(a.src)],
                               capture_output=True, text=True).stdout)
    cuts = sorted(tuple(map(float, c.split("-"))) for c in a.cut)
    keep, t = [], 0.0
    for c0, c1 in cuts:
        keep.append((t, c0)); t = c1
    keep.append((t, dur))
    with tempfile.TemporaryDirectory() as tmp:
        tmp = pathlib.Path(tmp); raw, dfn, eq, lvl = (tmp / f"{n}.wav" for n in ("raw", "dfn", "eq", "lvl"))
        run(["ffmpeg", "-v", "error", "-y", "-i", str(a.src), "-map", "0:a:0", "-af",
             "pan=mono|c0=0.5*c0+0.5*c1,highpass=f=90", "-ar", "48000", str(raw)])
        run([str(TTS_HOME / "venv/bin/python"), "-c", DFN, str(raw), str(dfn)],
            env=dict(os.environ, HF_HOME=str(TTS_HOME / "hf")), stderr=subprocess.DEVNULL)
        run(["ffmpeg", "-v", "error", "-y", "-i", str(dfn), "-af", EQ, str(eq)])
        gain = -16.0 - loudness(eq)
        run(["ffmpeg", "-v", "error", "-y", "-i", str(eq), "-af",
             f"volume={gain:.2f}dB,alimiter=limit={10 ** (-1.5 / 20):.3f}:level=false", "-ar", "48000", str(lvl)])
        if a.patch:
            import numpy as np, soundfile as sf
            y, sr = sf.read(lvl)
            for pt in a.patch:
                t0, f = pt.split("=", 1); i0 = int(float(t0) * sr)
                p_, psr = sf.read(f)
                if p_.ndim > 1: p_ = p_.mean(1)
                if psr != sr:
                    p_ = np.interp(np.arange(int(len(p_) * sr / psr)) * psr / sr, np.arange(len(p_)), p_)
                n = min(len(p_), len(y) - i0); seg = y[i0:i0 + n]
                loud = lambda v: np.sqrt(np.mean(v[np.abs(v) > 0.02] ** 2)) if np.any(np.abs(v) > 0.02) else 1e-9
                p_ = p_[:n] * loud(seg) / loud(p_[:n])
                fade = int(0.03 * sr); w = np.ones(n); w[:fade] = np.linspace(0, 1, fade); w[-fade:] = np.linspace(1, 0, fade)
                y[i0:i0 + n] = seg * (1 - w) + p_ * w
            sf.write(lvl, y, sr)
        if a.ab:
            before = tmp / "before.wav"
            g0 = -16.0 - loudness(raw)
            run(["ffmpeg", "-v", "error", "-y", "-t", "12", "-i", str(raw), "-af", f"volume={g0:.2f}dB", str(before)])
            run(["ffmpeg", "-v", "error", "-y", "-i", str(before), "-t", "12", "-i", str(lvl), "-filter_complex",
                 "[0][1]concat=n=2:v=0:a=1", str(a.ab)])
        # trim + join: video parts and sound parts (a 20 ms fade at each join, so no click)
        fv, fa, n = [], [], len(keep)
        for i, (s, e) in enumerate(keep):
            fv.append(f"[0:v]trim={s}:{e},setpts=PTS-STARTPTS,fps=30{',' + a.look if a.look else ''}[v{i}]")
            fa.append(f"[1:a]atrim={s}:{e},asetpts=PTS-STARTPTS,afade=t=in:d=0.02,afade=t=out:st={e - s - 0.02:.3f}:d=0.02[a{i}]")
        fc = ";".join(fv + fa) + ";" + "".join(f"[v{i}][a{i}]" for i in range(n)) + f"concat=n={n}:v=1:a=1[v][a]"
        a.dst.parent.mkdir(parents=True, exist_ok=True)
        run(["ffmpeg", "-v", "error", "-y", "-i", str(a.src), "-i", str(lvl), "-filter_complex", fc, "-map", "[v]",
             "-map", "[a]", "-ac", "2", "-c:v", "libx264", "-crf", "18", "-preset", "medium", "-pix_fmt", "yuv420p",
             "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", str(a.dst)])
    print(f"cleaned: {a.dst}  {sum(e - s for s, e in keep):.1f} s (cut {sum(c1 - c0 for c0, c1 in cuts):.1f} s) · {loudness(a.dst):.1f} LUFS")


if __name__ == "__main__":
    main()
