#!/usr/bin/env python3
"""Turn a video script into ready-to-edit audio with the local voices (owner's cloned voice + Chatterbox; free, MIT).

For every ```say:<speaker>``` block it generates 3 takes, keeps the one that a speech-to-text check hears best,
levels its loudness, and assembles the whole voiceover with the ⏸️ pauses inserted.

Needs: ffmpeg, and the local TTS environment (default /media/msn/GamesLinux/AI/tts, override with TTS_HOME).
See docs/10-production-flow.md.

Usage:
    python3 tools/make_audio.py videos/002-10-most-useful-phrases.md
    python3 tools/make_audio.py videos/*.md --out audio --takes 3

Output (per video), in audio/<video-name>/:
    voiceover.wav   the full voiceover with gaps and pauses — drop it on the timeline at 0:00
    timeline.md     where each scene and each clip starts (human-readable)
    timeline.json   the same, for the assembly script
    captions.srt    every spoken line with timings
    clips/NN-<speaker>.wav   the single clips
    report.md       speech-to-text check of every line (anything flagged ⚠️ deserves a listen)

Clips are cached in audio/.cache by voice + text, so re-running after editing one line only regenerates that line.
"""
import argparse
import hashlib
import json
import os
import pathlib
import re
import shutil
import subprocess
import sys

TTS_HOME = pathlib.Path(os.environ.get("TTS_HOME", "/media/msn/GamesLinux/AI/tts"))
TTS_PYTHON = TTS_HOME / "venv" / "bin" / "python"
WORKER = pathlib.Path(__file__).resolve().parent / "tts_worker.py"

# Bump a speaker's version when its voice reference or setting in <TTS_HOME>/local_tts.py changes,
# so only that speaker's clips are regenerated.
VOICE_VERSIONS = {"narrator": "owner-en-5", "teacher": "owner-ar-4", "teacher-slow": "owner-ar-4",
                  "sami": "owner-ar-4", "lina": "sara-ar-5", "narrator-kokoro": "kokoro-2"}
# -2: neutral, 5% slower · -3 (Arabic): denoised reference, cfg 0.5, tail check + trim
# owner-en-3 / sara-ar-4: all references denoised with DeepFilterNet (2026-09-27)
# -4/-5: every generated clip also passes through DeepFilterNet (noise-free guarantee)
SPEAKERS = ("narrator", "teacher", "teacher-slow", "sami", "lina", "narrator-kokoro")

MAX_PAUSE = 2.0     # seconds — longer waits bore the viewer (easy words: 1.5 s)
GAP = 0.35          # seconds of silence between two clips when the script has no explicit pause
SAMPLE_RATE = 24000
CLIP_LUFS = -18.0   # per-clip loudness (the final video mix is brought to -14 LUFS)

SCENE = re.compile(r"^### 🎬 (.+?)(?:\s+·\s+[\d:–-]+)?\s*$")
SAY = re.compile(r"^```say:([\w-]+)\s*$")
PAUSE = re.compile(r"⏸️ \*\*Pause (\d+(?:\.\d+)?)s\*\*")
VIDEO = re.compile(r"^🎥 \*\*Clip:\*\*\s*([\w-]+)(?:\s*—\s*(.+))?$")
ROOT = pathlib.Path(__file__).resolve().parent.parent
CLIPS_DIR = ROOT / "footage" / "clips"
ARABIC_SPEAKERS = ("teacher", "teacher-slow", "sami", "lina")


def parse(script: pathlib.Path):
    """Events: ('scene', name) / ('say', speaker, text) / ('pause', seconds) / ('video', clip name, caption)."""
    events, lines, i = [], script.read_text(encoding="utf-8").splitlines(), 0
    while i < len(lines):
        line = lines[i]
        if m := SCENE.match(line):
            events.append(("scene", m.group(1)))
        elif m := SAY.match(line):
            speaker, body = m.group(1), []
            if speaker not in SPEAKERS:
                sys.exit(f"{script}:{i + 1}: unknown speaker '{speaker}' (known: {', '.join(SPEAKERS)})")
            i += 1
            while i < len(lines) and lines[i].strip() != "```":
                body.append(lines[i])
                i += 1
            events.append(("say", speaker, " ".join(" ".join(body).split())))
        elif m := VIDEO.match(line):
            if not (CLIPS_DIR / f"{m.group(1)}.mp4").exists():
                sys.exit(f"{script}:{i + 1}: filmed clip {CLIPS_DIR / m.group(1)}.mp4 not found")
            events.append(("video", m.group(1), (m.group(2) or "").strip()))
        elif m := PAUSE.search(line):   # owner, 2026-10-02: a "your turn" wait is never longer than 2 s
            events.append(("pause", min(float(m.group(1)), MAX_PAUSE)))
        i += 1
    return events


def run(cmd, **kw):
    return subprocess.run(cmd, check=True, **kw)


def duration(path: pathlib.Path) -> float:
    out = run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(path)],
              capture_output=True, text=True)
    return float(out.stdout)


def loudness(path: pathlib.Path) -> float:
    out = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", str(path), "-af", "ebur128", "-f", "null", "-"],
                         capture_output=True, text=True).stderr
    summary = out[out.rfind("Summary:"):]
    m = re.search(r"I:\s+(-?[\d.]+) LUFS", summary)
    return float(m.group(1)) if m else -70.0


# the owner's own recordings (phone mic + noise removal) sound darker than Koki's and the narrator: lift clarity and
# level them 2 dB above the other clips (owner, 2026-10-02: "my voice is lower and less clear")
OWNER_CLARITY = ("highpass=f=90,equalizer=f=250:t=q:w=1.2:g=-2.5,equalizer=f=2800:t=q:w=1.0:g=3.5,"
                 "highshelf=f=6000:g=4,")   # the EQ the owner approved on Day 8 (hiss is now handled by RECORDED_CLEAN)
# recorded lines (owner + Koki): light spectral denoise + a soft gate in the pauses — the treble boost had lifted the
# phone's hiss to ~-55 dB, audible on headphones next to the narrator's silent pauses (owner, 2026-10-05)
RECORDED_CLEAN = "afftdn=nr=12:nf=-50:tn=1,agate=threshold=0.012:ratio=3:attack=5:release=150:range=0.06"
OWNER_LIFT_DB = 1.0   # measured 2026-10-02: +2 put him 2 LU above the narrator; the EQ does most of the work
OWNER_SPEAKERS = {"teacher", "teacher-slow", "sami"}


def level(src: pathlib.Path, dst: pathlib.Path, owner=None):
    """Trim silence at both ends, bring the clip to CLIP_LUFS, keep peaks below -1.5 dB.
    owner=True: the owner's recorded voice — clarity EQ and +2 dB (see OWNER_CLARITY)."""
    trimmed = dst.with_suffix(".trim.wav")
    trim = ("silenceremove=start_periods=1:start_threshold=-45dB:start_silence=0.05,"
            "areverse,silenceremove=start_periods=1:start_threshold=-45dB:start_silence=0.1,areverse")
    run(["ffmpeg", "-v", "error", "-y", "-i", str(src), "-af", trim, "-ac", "1", "-ar", str(SAMPLE_RATE), str(trimmed)])
    if owner is not None:   # a recorded line (owner=True/False): denoise + gate; the owner's also gets the EQ
        eq = dst.with_suffix(".eq.wav")
        chain = (OWNER_CLARITY if owner else "") + RECORDED_CLEAN
        run(["ffmpeg", "-v", "error", "-y", "-i", str(trimmed), "-af", chain, str(eq)])
        trimmed.unlink(); eq.rename(trimmed)
    gain = CLIP_LUFS + (OWNER_LIFT_DB if owner else 0.0) - loudness(trimmed)   # owner=None: generated speech
    run(["ffmpeg", "-v", "error", "-y", "-i", str(trimmed), "-af",
         f"volume={gain:.2f}dB,alimiter=limit=0.84:attack=3:release=40:level=false", str(dst)])
    trimmed.unlink()


def tts_env():
    """Environment for the GPU worker: models folder + NVIDIA libraries (must be set before the process starts)."""
    libs = sorted(str(p) for p in (TTS_HOME / "venv").glob("lib/python3*/site-packages/nvidia/*/lib"))
    return dict(os.environ, TTS_HOME=str(TTS_HOME), HF_HOME=str(TTS_HOME / "hf"),
                LD_LIBRARY_PATH=":".join(libs + [os.environ.get("LD_LIBRARY_PATH", "")]))


def synthesize_missing(todo, cache: pathlib.Path, takes: int):
    """todo: {cache_path: (speaker, text)} — generate takes, pick the best, level it.

    Takes are kept in cache/work/ until the line is finished, so a crash never loses generated audio."""
    if not todo:
        return []
    if not TTS_PYTHON.exists():
        sys.exit(f"Local TTS not found at {TTS_HOME} (set TTS_HOME).")
    work = cache / "work"
    work.mkdir(exist_ok=True)
    jobs = []
    for path, (speaker, text) in todo.items():
        key = path.stem
        job = {"text": text, "speaker": speaker, "takes": takes, "prefix": str(work / key),
               "target": str(work / f"{key}-best.wav"), "cache": str(path)}
        job["done"] = all(pathlib.Path(f"{job['prefix']}-take{k}.wav").exists() for k in range(takes))
        jobs.append(job)
    env = tts_env()
    pending = [j for j in jobs if not j["done"]]
    if pending:
        jobs_file = work / "generate.json"
        jobs_file.write_text(json.dumps(pending, ensure_ascii=False), encoding="utf-8")
        print(f"  generating {len(pending)} line(s) x {takes} takes …")
        run([str(TTS_PYTHON), str(WORKER), "generate", str(jobs_file)], env=env)
    jobs_file = work / "score.json"
    jobs_file.write_text(json.dumps(jobs, ensure_ascii=False), encoding="utf-8")
    print("  checking takes with speech-to-text …")
    run([str(TTS_PYTHON), str(WORKER), "score", str(jobs_file)], env=env)
    jobs = json.loads(jobs_file.read_text(encoding="utf-8"))
    for job in jobs:
        level(pathlib.Path(job["target"]), pathlib.Path(job["cache"]))
        pathlib.Path(job["cache"]).with_suffix(".json").write_text(
            json.dumps({k: job[k] for k in ("speaker", "text", "cer", "heard")}, ensure_ascii=False), encoding="utf-8")
        for k in range(takes):
            pathlib.Path(f"{job['prefix']}-take{k}.wav").unlink(missing_ok=True)
        pathlib.Path(job["target"]).unlink(missing_ok=True)
    return jobs


def timestamp(seconds: float, srt: bool = False) -> str:
    ms = round(seconds * 1000)
    h, ms = divmod(ms, 3_600_000)
    m, ms = divmod(ms, 60_000)
    s, ms = divmod(ms, 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}" if srt else f"{m}:{s:02d}.{ms // 100}"


def render(script: pathlib.Path, out_root: pathlib.Path, takes: int, redo=(), allow_tts=False):
    events = parse(script)
    if not any(e[0] == "say" for e in events):
        print(f"{script}: no say: blocks, skipped")
        return
    out_dir, cache = out_root / script.stem, out_root / ".cache"
    clips_dir = out_dir / "clips"
    shutil.rmtree(clips_dir, ignore_errors=True)
    clips_dir.mkdir(parents=True)
    cache.mkdir(parents=True, exist_ok=True)

    # the owner's own Arabic recording (tools/split_recording.py) replaces generated Arabic voices
    rec_map_file = ROOT / "footage" / "recordings" / script.stem / "map.json"
    recorded = {}
    if rec_map_file.exists():
        for r in json.loads(rec_map_file.read_text(encoding="utf-8")):
            if r.get("file"):
                recorded[(r["speaker"], r["text"])] = r
    missing = [e for e in events if e[0] == "say" and e[1] in ARABIC_SPEAKERS and recorded
               and (e[1], e[2]) not in recorded]
    if missing and not allow_tts:
        sys.exit("lines missing from the recording (re-record or use --allow-tts):\n" +
                 "\n".join(f"  [{e[1]}] {e[2]}" for e in missing))

    def cache_path(speaker, text):
        rec = recorded.get((speaker, text))
        if rec:
            digest = hashlib.sha1((ROOT / rec["file"]).read_bytes()).hexdigest()
            tag = "rec7" if speaker in OWNER_SPEAKERS else "reck2"   # rec4/reck2 = denoise + gate (+ owner EQ)
            return cache / f"{tag}-{digest}.wav"
        return cache / (hashlib.sha1(f"{VOICE_VERSIONS[speaker]}|{speaker}|{text}".encode()).hexdigest() + ".wav")

    for (speaker, text), rec in recorded.items():   # recorded lines: level them into the cache
        target = cache_path(speaker, text)
        if not target.exists():
            level(ROOT / rec["file"], target, owner=speaker in OWNER_SPEAKERS)
            target.with_suffix(".json").write_text(json.dumps(
                {"speaker": speaker, "text": text, "cer": rec["cer"], "heard": "🎙️ recorded: " + rec["heard"]},
                ensure_ascii=False), encoding="utf-8")

    # 1. generate every line that isn't cached yet (--redo N forgets clip N's cached take)
    says = [e for e in events if e[0] == "say"]
    for n in redo:
        cache_path(says[n - 1][1], says[n - 1][2]).unlink(missing_ok=True)
    todo = {}
    PINNED = {sp for sp in VOICE_VERSIONS if sys.argv and f"{sp}=" in " ".join(sys.argv)}
    for e in events:
        if e[0] == "say" and not cache_path(e[1], e[2]).exists():
            todo[cache_path(e[1], e[2])] = (e[1], e[2])
    print(f"{script.name}: {sum(e[0] == 'say' for e in events)} clips, {len(todo)} new line(s)")
    if any(sp in PINNED for sp, _ in todo.values()):
        sys.exit("a pinned voice would need new takes — not allowed: " +
                 "; ".join(t for sp, t in todo.values() if sp in PINNED))
    synthesize_missing(todo, cache, takes)

    # 2. lay the clips out on a timeline
    segments, captions, report = [], [], []
    timeline = ["| Starts at | What |", "|---|---|"]
    data = {"scenes": [], "clips": [], "pauses": [], "videos": []}
    t, n, pending_gap = 0.0, 0, 0.0
    for event in events:
        if event[0] == "scene":
            start = t + ((pending_gap or GAP) if t > 0 else 0)
            timeline.append(f"| **{timestamp(start)}** | **🎬 {event[1]}** |")
            data["scenes"].append({"name": event[1], "start": round(start, 3)})
        elif event[0] == "video":
            _, name, caption = event
            if t > 0:
                gap = pending_gap or GAP
                segments.append(("silence", gap))
                t += gap
            pending_gap = 0.0
            length = duration(CLIPS_DIR / f"{name}.mp4")
            segments.append(("silence", length))
            timeline.append(f"| {timestamp(t)} | 🎥 filmed clip `{name}` ({length:.1f}s) {caption} |")
            data["videos"].append({"name": name, "caption": caption, "start": round(t, 3), "end": round(t + length, 3)})
            if caption:
                captions.append(f"{len(captions) + 1}\n{timestamp(t, True)} --> {timestamp(t + length, True)}\n{caption}\n")
            t += length
            continue
        elif event[0] == "pause":
            pending_gap = event[1]
            timeline.append(f"| {timestamp(t)} | ⏸️ pause {event[1]:g}s |")
            data["pauses"].append({"start": round(t, 3), "end": round(t + event[1], 3)})
        else:
            _, speaker, text = event
            cached = cache_path(speaker, text)
            n += 1
            clip = clips_dir / f"{n:02d}-{speaker}.wav"
            shutil.copy(cached, clip)
            info = json.loads(cached.with_suffix(".json").read_text(encoding="utf-8"))
            if t > 0:
                gap = pending_gap or GAP
                segments.append(("silence", gap))
                t += gap
            pending_gap = 0.0
            length = duration(clip)
            segments.append(("clip", clip))
            timeline.append(f"| {timestamp(t)} | `{clip.name}` {text} |")
            captions.append(f"{len(captions) + 1}\n{timestamp(t, True)} --> {timestamp(t + length, True)}\n{text}\n")
            data["clips"].append({"n": n, "speaker": speaker, "text": text, "start": round(t, 3),
                                  "end": round(t + length, 3), "file": clip.name})
            flag = " ⚠️" if info["cer"] > 0.25 else ""
            report.append(f"| {n:02d} | {speaker} | {text} | {info['heard']} | {info['cer']:.2f}{flag} |")
            t += length
    if pending_gap:  # a pause after the last clip
        segments.append(("silence", pending_gap))
        t += pending_gap
    for i, scene in enumerate(data["scenes"]):
        scene["end"] = data["scenes"][i + 1]["start"] if i + 1 < len(data["scenes"]) else round(t, 3)
    data["duration"] = round(t, 3)

    # 3. assemble the full voiceover with ffmpeg
    cmd, filters = ["ffmpeg", "-y", "-loglevel", "error"], []
    for i, (kind, value) in enumerate(segments):
        if kind == "clip":
            cmd += ["-i", str(value)]
        else:
            cmd += ["-f", "lavfi", "-t", f"{value}", "-i", f"anullsrc=r={SAMPLE_RATE}:cl=mono"]
        filters.append(f"[{i}:a]aresample={SAMPLE_RATE},aformat=channel_layouts=mono[a{i}]")
    joined = "".join(f"[a{i}]" for i in range(len(segments)))
    filters.append(f"{joined}concat=n={len(segments)}:v=0:a=1[out]")
    cmd += ["-filter_complex", ";".join(filters), "-map", "[out]", str(out_dir / "voiceover.wav")]
    run(cmd)

    (out_dir / "timeline.md").write_text(
        f"# {script.stem} — voiceover timeline\n\nTotal length: **{timestamp(t)}**\n\n" + "\n".join(timeline) + "\n",
        encoding="utf-8")
    (out_dir / "timeline.json").write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")
    (out_dir / "captions.srt").write_text("\n".join(captions), encoding="utf-8")
    (out_dir / "report.md").write_text(
        f"# {script.stem} — speech-to-text check\n\nCER = character error rate of the best take (0 = heard exactly). "
        "⚠️ = worth a listen.\n\n| # | Speaker | Script | Heard | CER |\n|---|---|---|---|---|\n" + "\n".join(report) + "\n",
        encoding="utf-8")
    print(f"{script.name}: {n} clips, {timestamp(t)} -> {out_dir}")
    # audio gate (owner, 2026-10-02): voices level to the ear + every narrator line natural — runs automatically
    gate = subprocess.run([str(TTS_HOME / "venv" / "bin" / "python"), str(ROOT / "tools" / "voice_balance.py"), str(script)],
                          capture_output=True, text=True, env=tts_env())
    lines = [l for l in gate.stdout.splitlines() if l.startswith("⚠️") or "loudness" in l or "clarity" in l or "redo" in l]
    print("  audio gate:\n    " + "\n    ".join(lines))


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("scripts", nargs="+", type=pathlib.Path, help="video script .md files")
    parser.add_argument("--out", type=pathlib.Path, default=pathlib.Path("audio"), help="output folder (default: audio)")
    parser.add_argument("--takes", type=int, default=3, help="takes per line (default: 3)")
    parser.add_argument("--redo", default="", help="comma-separated clip numbers to regenerate (see report.md)")
    parser.add_argument("--allow-tts", action="store_true", help="generate Arabic lines missing from the owner's recording")
    parser.add_argument("--voice", action="append", default=[],
                        help="pin a speaker to an older voice version, e.g. --voice narrator=owner-en-2 "
                             "(re-use a published video's takes; stops if a line would need generating)")
    args = parser.parse_args()
    for tool in ("ffmpeg", "ffprobe"):
        if not shutil.which(tool):
            sys.exit(f"{tool} not found — install ffmpeg first.")
    pinned = dict(v.split("=", 1) for v in args.voice)
    VOICE_VERSIONS.update(pinned)
    for script in args.scripts:
        render(script, args.out, args.takes, [int(x) for x in args.redo.split(",") if x], args.allow_tts)


if __name__ == "__main__":
    main()
