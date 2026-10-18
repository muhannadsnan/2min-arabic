#!/usr/bin/env python3
"""Owner's clay presenter talk video (owner, 2026-10-18): his recorded voice + the keyed clay takes, cutting between
the close and the wide shot at sentence breaks, channel-style captions and a title for the first seconds.

    $TTS tools/talk_video.py <name> --close shots/close-alley.mp4 --wide shots/wide-rooftop.mp4 \
        --title "Learning Arabic?|Listen carefully" --groups "0 1 2-4 5-6 7 8-10" --start close
        → output/talk-videos/<name>.mp4

<name> = a list in footage/recordings/_talk-scripts/edl.json (voice built by tools/talk_audio.py). --groups = which EDL
chunks share one shot; shots alternate close/wide. Each shot takes the least-used part of its angle's 8.5 s take (no
repeat of the same motion close together); a shot longer than a whole take is split onto the other angle.
"""
import argparse, json, pathlib, subprocess
ROOT = pathlib.Path(__file__).resolve().parent.parent
TAKE = 8.45
FAREWELL = "Ila l-liqaa', wa-s-salaamu 'alaykum"

def dur(p): return float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(p)], capture_output=True, text=True).stdout)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("name"); ap.add_argument("--close", required=True); ap.add_argument("--wide", required=True)
    ap.add_argument("--title", required=True, help="two lines separated by |"); ap.add_argument("--groups", required=True)
    ap.add_argument("--start", choices=["close", "wide"], default="close"); ap.add_argument("--title-seconds", type=float, default=2.6)
    a = ap.parse_args()
    D = ROOT / "footage/recordings/_talk-scripts"; E = json.loads((D / "edl.json").read_text()); e = E[a.name]
    pscale = E.get("settings", {}).get("pause_scale", 1.0)
    voice = D / f"{a.name}.wav"; total = dur(voice)
    # chunk times in the finished voice track (the cut keeps each chunk's length; loudnorm doesn't change timing)
    t, times = 0.0, []
    for s, en, p in e:
        times.append((t, t + (en - s))); t += (en - s) + p * pscale
    scale = total / t
    times = [(x * scale, y * scale) for x, y in times]
    groups = []
    for g in a.groups.split():
        lo, hi = (int(x) for x in g.split("-")) if "-" in g else (int(g), int(g))
        groups.append((lo, hi))
    # shots: each group from its first chunk's start to the next group's start
    starts = [times[lo][0] if i else 0.0 for i, (lo, hi) in enumerate(groups)] + [total]
    angle = a.start; used = {"close": [], "wide": []}; src = {"close": a.close, "wide": a.wide}; shots = []
    def overlap(iv, lst): return sum(max(0.0, min(iv[1], b) - max(iv[0], x)) for x, b in lst)
    for i in range(len(groups)):
        need = starts[i + 1] - starts[i]
        while need > 0.01:
            take = min(need, TAKE)
            # the part of this take used least so far (no repeat of the same head movement within a few seconds)
            cands = [k * 0.25 for k in range(int((TAKE - take) / 0.25) + 1)]
            off = min(cands, key=lambda o: (overlap((o, o + take), used[angle]), o))
            shots.append((src[angle], off, take)); used[angle].append((off, off + take)); need -= take
            if need > 0.01: angle = "wide" if angle == "close" else "close"
        angle = "wide" if angle == "close" else "close"
    out_dir = ROOT / "output/talk-videos"; tmp = out_dir / f"_{a.name}"; tmp.mkdir(parents=True, exist_ok=True)
    parts = []
    for k, (f, off, d) in enumerate(shots):
        p = tmp / f"s{k:02}.mp4"; parts.append(p)
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{off:.3f}", "-i", str(ROOT / f), "-t", f"{d:.3f}", "-an",
                        "-vf", "fps=30,format=yuv420p", "-c:v", "libx264", "-crf", "18", "-preset", "fast", str(p)], check=True)
    (tmp / "list.txt").write_text("".join(f"file '{p.name}'\n" for p in parts))
    # captions: word timings from speech recognition, 2–3 words per caption (channel style); the Arabic farewell by hand
    from faster_whisper import WhisperModel
    m = WhisperModel("small", device="cpu", compute_type="int8")
    words = [w for s in m.transcribe(str(voice), language="en", word_timestamps=True)[0] for w in s.words]
    # the Arabic farewell follows the last "tuned"/"later" (it may share a cut with the sentence before it)
    ends = [w.end for w in words if w.word.strip(" .,!").lower() in ("tuned", "later")]
    fare0 = (ends[-1] + 0.12) if ends else times[-1][0]; words = [w for w in words if w.start < fare0 - 0.05]
    caps, cur = [], []
    for w in words:
        cur.append(w)
        txt = " ".join(x.word.strip() for x in cur)
        if len(txt) >= 17 or w.word.strip()[-1:] in ".!?,":
            caps.append((cur[0].start, w.end, txt)); cur = []
    if cur: caps.append((cur[0].start, cur[-1].end, " ".join(x.word.strip() for x in cur)))
    caps.append((fare0, total, FAREWELL))
    ts = lambda x: f"{int(x // 3600)}:{int(x % 3600 // 60):02}:{x % 60:05.2f}"
    head = (ROOT / "output/x03-introduce-yourself-in-arabic/captions.ass").read_text(encoding="utf-8").split("[Events]")[0]
    style2 = "Style: Title,Noto Sans,96,&H00FFFFFF,&H00FFFFFF,&H00000000,&H64000000,-1,0,0,0,100,100,0,0,1,8,3,8,80,80,200,1\n"
    head = head.replace(",110,110,540,1", ",110,110,300,1")   # lower than lessons: the close shot's face fills the frame
    head = head.rstrip("\n") + "\n" + style2 + "\n"
    l1, l2 = a.title.split("|")
    ev = ["[Events]", "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text",
          f"Dialogue: 1,{ts(0)},{ts(a.title_seconds)},Title,,0,0,0,,{l1}\\N{{\\c&H00D7FF&}}{l2}"]
    for i, (s, en, txt) in enumerate(caps):
        nxt = caps[i + 1][0] if i + 1 < len(caps) else total
        ev.append(f"Dialogue: 0,{ts(s)},{ts(min(max(en, s + 0.5), nxt))},Default,,0,0,0,,{txt}")
    ass = tmp / "captions.ass"; ass.write_text(head + "\n".join(ev) + "\n", encoding="utf-8")
    out = out_dir / f"{a.name}.mp4"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", str(tmp / "list.txt"), "-i", str(voice),
                    "-vf", f"ass={ass}", "-c:v", "libx264", "-crf", "19", "-preset", "medium", "-pix_fmt", "yuv420p",
                    "-c:a", "aac", "-b:a", "192k", "-af", "loudnorm=I=-14:TP=-1.5", "-shortest", str(out)], check=True)
    print(f"{out}  {dur(out):.1f}s · {len(shots)} shots: " + ", ".join(f"{pathlib.Path(f).stem}@{o:.1f}+{d:.1f}" for f, o, d in shots))

if __name__ == "__main__":
    main()
