#!/usr/bin/env python3
"""Story Short with English guidance (owner 2026-11-15): English hook over the thumbnail, then for every sentence the
narrator's English line (over that sentence's frame, held still) followed by the owner's Arabic sentence as cut.

    python3 library/work/story-guided.py s01-1-story audio/s01-1-guided videos/s01-story.json

Needs: output/<stem>/<stem>.mp4 (the Arabic-only Short), its captions-upload.srt (cue 1 = the Arabic hook, then one
cue per sentence), <stem>-thumbnail.jpg, and narrator wavs e00 (hook) + e01… (one per sentence) in the audio folder.
Writes output/<stem>-guided/<stem>-guided.mp4 + captions-upload.srt. Narrator lines are levelled ~0.7 dB above the
owner's Arabic (owner: the narrator must not sound lower than his recording), true peak ≤ -1.5 dB.
"""
import json, pathlib, re, subprocess, sys, tempfile

stem, adir, story = sys.argv[1], pathlib.Path(sys.argv[2]), json.load(open(sys.argv[3], encoding="utf-8"))
src = pathlib.Path(f"output/{stem}/{stem}.mp4")
out_dir = pathlib.Path(f"output/{stem}-guided"); out_dir.mkdir(parents=True, exist_ok=True)
out = out_dir / f"{stem}-guided.mp4"
GAP = 0.15                     # air after each English line
ENC = ["-c:v", "libx264", "-preset", "medium", "-crf", "18", "-r", "30", "-pix_fmt", "yuv420p",
       "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "1"]


def sh(*a): return subprocess.run(a, check=True, capture_output=True, text=True)
def dur(p): return float(sh("ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(p)).stdout)
def lufs(p, extra=()):
    r = subprocess.run(["ffmpeg", "-nostats", *extra, "-i", str(p), "-af", "ebur128", "-f", "null", "-"], capture_output=True, text=True)
    return float(re.findall(r"\bI:\s+(-?[\d.]+) LUFS", r.stderr)[-1])
def sec(t): h, m, r = t.split(":"); s, ms = r.split(","); return int(h) * 3600 + int(m) * 60 + int(s) + int(ms) / 1000
def ts(x): ms = round(x * 1000); return f"{ms//3600000:02}:{ms//60000%60:02}:{ms//1000%60:02},{ms%1000:03}"


cues = []
for b in open(src.parent / "captions-upload.srt", encoding="utf-8").read().strip().split("\n\n"):
    ln = b.split("\n"); a, z = ln[1].split(" --> "); cues.append((sec(a), sec(z), " ".join(ln[2:])))
ar_of = {s["en"]: s["ar"] for s in story["segments"] if s.get("kind") == "story" and "en" in s and "ar" in s}
total = dur(src)
sent = cues[1:]                                                   # cue 0 = the Arabic hook (replaced by the English one)
mids = [(sent[i - 1][1] + sent[i][0]) / 2 if i else (cues[0][1] + sent[0][0]) / 2 for i in range(len(sent))]


def picture_change(lo, hi, fallback):
    """First frame of the sentence's new picture between lo and hi (scene detection) — the English line must hold the
    NEW picture, not the last frame of the previous sentence (owner 2026-11-15: the frame jumped at every join)."""
    r = subprocess.run(["ffmpeg", "-v", "info", "-ss", f"{lo:.3f}", "-to", f"{hi:.3f}", "-i", str(src), "-an", "-vf",
                        "select='gt(scene,0.08)',showinfo", "-f", "null", "-"], capture_output=True, text=True)
    t = [float(x) for x in re.findall(r"pts_time:([\d.]+)", r.stderr)]
    return lo + t[0] if t else fallback


bounds = [picture_change(max(mids[i] - 1.0, 0), sent[i][0] + 0.6, mids[i]) for i in range(len(sent))] + [total]
target = lufs(src) + 0.7

with tempfile.TemporaryDirectory() as tmp:
    tmp = pathlib.Path(tmp); parts, srt, t = [], [], 0.0
    def narr(k):
        o = tmp / f"n{k}.wav"
        sh("ffmpeg", "-v", "error", "-y", "-i", str(adir / f"e{k:02}.wav"), "-af",
           f"silenceremove=start_periods=1:start_threshold=-60dB:start_silence=0.1,areverse,silenceremove=start_periods=1:start_threshold=-55dB:start_silence=0.1,areverse,"
           f"acompressor=threshold=-22dB:ratio=3:attack=5:release=80:makeup=2,loudnorm=I={target:.1f}:TP=-1.5:LRA=7,apad=pad_dur={GAP}",
           "-ar", "48000", "-ac", "1", str(o))
        return o
    def still(img, wav, name):
        o = tmp / f"{name}.mp4"; d = dur(wav)
        sh("ffmpeg", "-v", "error", "-y", "-loop", "1", "-framerate", "30", "-t", f"{d:.3f}", "-i", str(img), "-i", str(wav),
           "-vf", "scale=1080:1920,setsar=1", "-shortest", *ENC, str(o))
        return o, d
    # hook
    h = narr(0); clip, d = still(src.parent / f"{stem}-thumbnail.jpg", h, "hook"); parts.append(clip)
    hook_en = json.loads((adir / "e00.json").read_text())["text"] if (adir / "e00.json").exists() else ""
    srt.append((0, d - 0.1, hook_en)); t = d
    for i, (a, z, en) in enumerate(sent):
        # owner 2026-11-15 "the frame flickers each time": the English line now holds the sentence's OWN first frame
        # (tpad clone in the same encode — no PNG round trip, so no colour shift and no word popping twice)
        k = i + 1; w = narr(k); d = dur(w)
        seg = tmp / f"s{k}.mp4"; s0, s1 = bounds[i], bounds[i + 1]
        sh("ffmpeg", "-v", "error", "-y", "-ss", f"{s0:.3f}", "-to", f"{s1:.3f}", "-i", str(src), "-i", str(w),
           "-filter_complex", f"[0:v]tpad=start_duration={d:.3f}:start_mode=clone,setsar=1[v];"
           "[1:a]aformat=sample_rates=48000:channel_layouts=mono[n];[0:a]aformat=sample_rates=48000:channel_layouts=mono[s];"
           "[n][s]concat=n=2:v=0:a=1[a]", "-map", "[v]", "-map", "[a]", *ENC, str(seg))
        parts.append(seg)
        srt.append((t, t + d - 0.1, en)); t += d
        sd = dur(seg) - d
        srt.append((t + (a - s0), t + (z - s0), ar_of.get(en, en))); t += sd
    lst = tmp / "list.txt"; lst.write_text("".join(f"file '{p}'\n" for p in parts))
    sh("ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", str(lst), *ENC, "-movflags", "+faststart", str(out))

(out_dir / "captions-upload.srt").write_text("\n\n".join(f"{n}\n{ts(a)} --> {ts(z)}\n{x}" for n, (a, z, x) in enumerate(srt, 1)) + "\n", encoding="utf-8")
print(out, f"{dur(out):.1f} s", f"narrator target {target:.1f} LUFS", len(srt), "captions")
