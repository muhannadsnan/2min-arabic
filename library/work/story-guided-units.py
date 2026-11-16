#!/usr/bin/env python3
"""Story Shorts 2–5 with English guidance (owner 2026-11-16: "only the opener is English, new beginners won't like it").

    python3 library/work/story-guided-units.py <stem> [<stem> …]

Plan: videos/s01-shorts-guided.json → {stem: {"units": [{"cues": [1, 2], "en": "Who goes to the market?"}, …]}}.
Each unit = consecutive cues of output/<stem>/captions-arabic-only.srt (the owner's Arabic) with ONE English narrator
line before them; cues not in any unit are cut out (s01-2 keeps ~19 of its 29 questions to stay under 3 min).
Video: hook (C2 narrator over the thumbnail) → per unit: the English line over the unit's own first frame (tpad clone,
no PNG round trip = no flicker, as in story-guided.py) → the Arabic segment as cut. Narrator wavs: audio/s01-shorts-guided/
<stem>/uNN.wav (narrator-wpe = C2), hook: audio/s01-hooks-c2t/<stem>.wav. Writes output/<stem>/<stem>.mp4 (the old
English-hook version is kept as <stem>-hook-only.mp4) + captions-upload.srt: English lines, then Arabic script, with
the English under it for answers the narrator didn't say.
"""
import json, pathlib, re, subprocess, sys, tempfile, shutil

PLAN = json.load(open("videos/s01-shorts-guided.json", encoding="utf-8"))
STORY = json.load(open("videos/s01-story.json", encoding="utf-8"))
GAP = 0.15
ENC = ["-c:v", "libx264", "-preset", "medium", "-crf", "18", "-r", "30", "-pix_fmt", "yuv420p",
       "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "1"]
TIGHT = "silenceremove=stop_periods=-1:stop_duration=0.2:stop_threshold=-42dB:stop_silence=0.15"
TRIM = ("silenceremove=start_periods=1:start_threshold=-60dB:start_silence=0.1,areverse,"
        "silenceremove=start_periods=1:start_threshold=-55dB:start_silence=0.1,areverse")


def sh(*a): return subprocess.run(a, check=True, capture_output=True, text=True)
def dur(p): return float(sh("ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(p)).stdout)
def lufs(p):
    r = subprocess.run(["ffmpeg", "-nostats", "-i", str(p), "-af", "ebur128", "-f", "null", "-"], capture_output=True, text=True)
    return float(re.findall(r"\bI:\s+(-?[\d.]+) LUFS", r.stderr)[-1])
def sec(t): h, m, r = t.split(":"); s, ms = r.split(","); return int(h) * 3600 + int(m) * 60 + int(s) + int(ms) / 1000
def ts(x): ms = round(x * 1000); return f"{ms//3600000:02}:{ms//60000%60:02}:{ms//1000%60:02},{ms%1000:03}"
def norm(s): return re.sub(r"[^a-z]+", " ", s.lower()).strip()


# English caption text → Arabic script (story lines, talk lines incl. the shorter _v versions, Q … A split in halves)
AR = {}
for s in STORY["segments"]:
    if "en" not in s or "ar" not in s: continue
    AR[norm(s["en"])] = s["ar"]
    if s.get("en_v"): AR[norm(s["en_v"])] = s.get("ar_v", s["ar"]).replace("\n", " ")
    if s.get("kind") == "qa":
        for e, a in zip(s["en"].split(" … "), s["ar"].split(" … ")): AR[norm(e)] = a


def build(stem):
    src = pathlib.Path(f"output/{stem}/{stem}-arabic-only.mp4")
    srt_in = src.parent / "captions-arabic-only.srt"
    cues = []
    for b in open(srt_in, encoding="utf-8").read().strip().split("\n\n"):
        ln = b.split("\n"); a, z = ln[1].split(" --> "); cues.append((sec(a), sec(z), " ".join(ln[2:])))
    total = dur(src)

    def changes(lo, hi):
        r = subprocess.run(["ffmpeg", "-v", "info", "-ss", f"{lo:.3f}", "-to", f"{hi:.3f}", "-i", str(src), "-an", "-vf",
                            "select='gt(scene,0.04)',showinfo", "-f", "null", "-"], capture_output=True, text=True)
        return [lo + float(x) for x in re.findall(r"pts_time:([\d.]+)", r.stderr)]

    def start_of(c):
        """(cut, hold): cut = where the segment before cue c starts (a picture change in the silence, else the middle of
        the gap); hold = the frame the English line shows. In s01-3 the new sentence text appears only as the Arabic
        starts (owner's rule: no jump at the join, 2026-11-15) → the English line holds that NEW frame and the video
        continues from it (the old-picture frames between cut and hold are skipped; the audio is untouched)."""
        if c == 1: return 0.0, 0.0
        lo, start = cues[c - 2][1] + 0.03, cues[c - 1][0]
        ch = changes(lo, start + 0.5)
        before = [t for t in ch if t <= start - 0.02]
        cut = before[0] if before else (lo + start) / 2
        hold = max([t for t in ch if t >= cut], default=cut)
        return cut, hold

    def end_of(c):            # the cut point after cue c (= the start of cue c+1, or the end of the video)
        return total if c == len(cues) else start_of(c + 1)[0]

    units = PLAN[stem]["units"]
    adir = pathlib.Path(f"audio/s01-shorts-guided/{stem}")
    target = lufs(src) + 1.0   # narrator at or slightly above the owner's Arabic
    with tempfile.TemporaryDirectory() as tmp:
        tmp = pathlib.Path(tmp)

        def narr(wav, k, pad=GAP):
            # separate passes, each with a timeout: one big ffmpeg 6.1 graph hangs forever on some files (2026-11-15)
            t0, t1, o = tmp / f"{k}-t.wav", tmp / f"{k}-tr.wav", tmp / f"{k}.wav"
            sh("timeout", "60", "ffmpeg", "-v", "error", "-y", "-i", str(wav), "-af", TIGHT, str(t0))
            sh("timeout", "60", "ffmpeg", "-v", "error", "-y", "-i", str(t0), "-af", TRIM, str(t1))
            sh("timeout", "60", "ffmpeg", "-v", "error", "-y", "-i", str(t1), "-af",
               f"acompressor=threshold=-22dB:ratio=3:attack=5:release=80:makeup=2,loudnorm=I={target:.1f}:TP=-1.5:LRA=7,apad=pad_dur={pad}",
               "-ar", "48000", "-ac", "1", str(o))
            return o

        parts, srt = [], []
        h = narr(pathlib.Path(f"audio/s01-hooks-c2t/{stem}.wav"), "hook", 0.25); d = dur(h)
        clip = tmp / "hook.mp4"
        sh("ffmpeg", "-v", "error", "-y", "-loop", "1", "-framerate", "30", "-t", f"{d:.3f}", "-i", str(src.parent / f"{stem}-thumbnail.jpg"),
           "-i", str(h), "-vf", "scale=1080:1920,setsar=1", "-shortest", *ENC, str(clip))
        parts.append(clip)
        hook_en = json.loads(pathlib.Path(f"audio/s01-hooks-c2t/{stem}.json").read_text())["text"]
        srt.append((0, d - 0.1, hook_en)); t = dur(clip)
        lead = []                 # English-only units (no cues): their line runs straight into the next unit's line
        outro = PLAN[stem].get("outro")   # owner 2026-11-16: like + subscribe after the last Arabic line (last frame held)
        ow = narr(adir / "outro.wav", "outro", 0.4) if outro else None
        for k, u in enumerate(units, 1):
            w = narr(adir / f"u{k:02}.wav", f"u{k:02}")
            if not u["cues"]:     # owner 2026-11-16 (s01-3): the Arabic intro sentence is cut, its English line stays
                lead.append((w, u["en"])); continue
            if lead:
                ws = [x for x, _ in lead] + [w]; w2 = tmp / f"u{k:02}-lead.wav"
                sh("ffmpeg", "-v", "error", "-y", *sum((["-i", str(x)] for x in ws), []), "-filter_complex",
                   "".join(f"[{i}:a]" for i in range(len(ws))) + f"concat=n={len(ws)}:v=0:a=1[a]", "-map", "[a]", str(w2))
                for x, en in lead:
                    srt.append((t, t + dur(x) - 0.1, en)); t += dur(x)
                tl = sum(dur(x) for x, _ in lead); lead = []
            else:
                w2, tl = w, 0.0
            d = dur(w2)
            c0, c1 = u["cues"][0], u["cues"][-1]
            (s0, hold), s1 = start_of(c0), end_of(c1)
            skip = hold - s0
            seg = tmp / f"s{k:02}.mp4"
            last = k == len(units) and ow is not None
            vpad = f":stop_duration={dur(ow):.3f}:stop_mode=clone" if last else ""   # ONE tpad: a second chained tpad loses ~2 s (ffmpeg 6.1)
            ins = ["-i", str(ow)] if last else []
            amix = "[2:a]aformat=sample_rates=48000:channel_layouts=mono[o];[n][s][o]concat=n=3:v=0:a=1[a]" if last else "[n][s]concat=n=2:v=0:a=1[a]"
            sh("ffmpeg", "-v", "error", "-y", "-ss", f"{s0:.3f}", "-to", f"{s1:.3f}", "-i", str(src), "-i", str(w2), *ins,
               "-filter_complex", f"[0:v]trim=start={skip:.3f},setpts=PTS-STARTPTS,tpad=start_duration={d + skip:.3f}:start_mode=clone{vpad},setsar=1[v];"
               "[1:a]aformat=sample_rates=48000:channel_layouts=mono[n];[0:a]aformat=sample_rates=48000:channel_layouts=mono[s];"
               + amix, "-map", "[v]", "-map", "[a]", *ENC, str(seg))
            parts.append(seg)
            d -= tl
            srt.append((t, t + d - 0.1, u["en"]))
            for c in u["cues"]:
                a, z, en = cues[c - 1]
                ar = AR.get(norm(en))
                said = norm(en) in norm(u["en"]) or norm(u["en"]) in norm(en)
                txt = en if not ar else (ar if said else f"{ar}\n{en}")
                srt.append((t + d + (a - s0), t + d + (z - s0), txt))
            t += dur(seg) - tl    # t already moved past the lead lines
        if ow is not None:
            srt.append((t - dur(ow), t - 0.1, outro["en"]))
        out = src.parent / f"{stem}.mp4"
        old = src.parent / f"{stem}-hook-only.mp4"
        if out.exists() and not old.exists(): shutil.copy2(out, old)
        old_srt = src.parent / "captions-hook-only.srt"
        if not old_srt.exists(): shutil.copy2(src.parent / "captions-upload.srt", old_srt)
        lst = tmp / "list.txt"; lst.write_text("".join(f"file '{p}'\n" for p in parts))
        if ow is None:
            sh("ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", str(lst), *ENC, "-movflags", "+faststart", str(out))
        else:
            # owner 2026-11-16: LIKE + SUBSCRIBE + bell clicked (tools/make_like_subscribe.py) under the outro line, with a
            # click per button and the bell ding; y per Short (plan "outro.y") so it never covers a face
            sys.path.insert(0, "tools"); from make_like_subscribe import CLICK_TIMES, DING_TIME
            st = t - dur(ow) - 0.1; y = outro.get("y", 1000)
            snd = [("assets/click.wav", c, 0.5) for c in CLICK_TIMES] + [("assets/ding.wav", DING_TIME, 0.35)]
            ins = sum((["-i", f] for f, _, _ in snd), [])
            ach = "".join(f";[{2 + j}:a]volume={v},aformat=sample_rates=48000:channel_layouts=mono,adelay={round((st + a) * 1000)}:all=1[x{j}]"
                          for j, (_, a, v) in enumerate(snd))
            sh("ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", str(lst), "-i", "assets/like-subscribe.mov", *ins, "-filter_complex",
               f"[1:v]format=rgba,setpts=PTS-STARTPTS+{st:.3f}/TB[o];[0:v][o]overlay=0:{y}:eof_action=pass[v];"
               f"[0:a]aresample=48000:async=1:first_pts=0,aformat=sample_rates=48000:channel_layouts=mono[m]{ach};"   # async: keep the gaps between parts (amix drops them → drift)
               "[m]" + "".join(f"[x{j}]" for j in range(len(snd))) + f"amix=inputs={1 + len(snd)}:duration=first:normalize=0,alimiter=limit=0.84:level=false[a]",
               "-map", "[v]", "-map", "[a]", *ENC, "-movflags", "+faststart", str(out))
    (src.parent / "captions-upload.srt").write_text(
        "\n\n".join(f"{n}\n{ts(a)} --> {ts(z)}\n{x}" for n, (a, z, x) in enumerate(srt, 1)) + "\n", encoding="utf-8")
    print(out, f"{dur(out):.1f} s", f"narrator target {target:.1f} LUFS", len(units), "units", len(srt), "captions", flush=True)


for stem in sys.argv[1:]:
    build(stem)
