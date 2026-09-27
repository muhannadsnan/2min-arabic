#!/usr/bin/env python3
"""Turn a video script into ready-to-edit audio with Azure AI Speech (paid S0 tier = commercial use allowed).

For every ```say:<speaker>``` block it synthesizes one clip, then assembles the whole voiceover with the
⏸️ pauses inserted, so the editor only has to place images and text on top.

Setup (once):
    export AZURE_SPEECH_KEY="<key from your Azure Speech resource>"
    export AZURE_SPEECH_REGION="<its region, e.g. westeurope>"
    # ffmpeg and ffprobe must be installed (sudo apt install ffmpeg)

Usage:
    python tools/make_audio.py videos/001-why-2-minutes.md
    python tools/make_audio.py videos/*.md --out audio

Output (per video), in audio/<video-name>/:
    voiceover.wav   the full voiceover with gaps and pauses — drop it on the timeline at 0:00
    timeline.md     where each scene and each clip starts (place the scene images at these times)
    captions.srt    every spoken line with timings (upload to YouTube as subtitles)
    clips/NN-<speaker>.mp3   the single clips, in case you want to move one by hand

Clips are cached in audio/.cache by voice+rate+text, so re-running after editing one line
only pays for that one line.
"""
import argparse
import hashlib
import os
import pathlib
import re
import shutil
import subprocess
import sys
import urllib.error
import urllib.request
from xml.sax.saxutils import escape

# speaker tag -> (Azure neural voice, speaking rate)
SPEAKERS = {
    "narrator": ("en-US-AndrewNeural", "+0%"),
    "teacher": ("ar-SA-HamedNeural", "-10%"),
    "teacher-slow": ("ar-SA-HamedNeural", "-35%"),
    "sami": ("ar-SY-LaithNeural", "-10%"),
    "lina": ("ar-SA-ZariyahNeural", "-10%"),
}

GAP = 0.35  # seconds of silence between two clips when the script has no explicit pause
SAMPLE_RATE = 24000

SCENE = re.compile(r"^### 🎬 (.+?)(?:\s+·\s+[\d:–-]+)?\s*$")
SAY = re.compile(r"^```say:([\w-]+)\s*$")
PAUSE = re.compile(r"⏸️ \*\*Pause (\d+(?:\.\d+)?)s\*\*")


def parse(script: pathlib.Path):
    """Return the script as a list of events: ('scene', name) / ('say', speaker, text) / ('pause', seconds)."""
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
        elif m := PAUSE.search(line):
            events.append(("pause", float(m.group(1))))
        i += 1
    return events


def synthesize(text: str, voice: str, rate: str, target: pathlib.Path):
    key, region = os.environ.get("AZURE_SPEECH_KEY"), os.environ.get("AZURE_SPEECH_REGION")
    if not key or not region:
        sys.exit("Set AZURE_SPEECH_KEY and AZURE_SPEECH_REGION first (see docs/03-production-pipeline.md).")
    ssml = (
        f"<speak version='1.0' xmlns='http://www.w3.org/2001/10/synthesis' xml:lang='{voice[:5]}'>"
        f"<voice name='{voice}'><prosody rate='{rate}'>{escape(text)}</prosody></voice></speak>"
    )
    request = urllib.request.Request(
        f"https://{region}.tts.speech.microsoft.com/cognitiveservices/v1",
        data=ssml.encode("utf-8"),
        headers={
            "Ocp-Apim-Subscription-Key": key,
            "Content-Type": "application/ssml+xml",
            "X-Microsoft-OutputFormat": "audio-24khz-96kbitrate-mono-mp3",
            "User-Agent": "2min-make-audio",
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=60) as response:
            target.write_bytes(response.read())
    except urllib.error.HTTPError as e:
        sys.exit(f"Azure TTS failed ({e.code} {e.reason}) for: {text[:60]}")


def duration(path: pathlib.Path) -> float:
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(path)],
        capture_output=True, text=True, check=True,
    )
    return float(out.stdout)


def timestamp(seconds: float, srt: bool = False) -> str:
    ms = round(seconds * 1000)
    h, ms = divmod(ms, 3_600_000)
    m, ms = divmod(ms, 60_000)
    s, ms = divmod(ms, 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}" if srt else f"{m}:{s:02d}.{ms // 100}"


def render(script: pathlib.Path, out_root: pathlib.Path):
    events = parse(script)
    if not any(e[0] == "say" for e in events):
        print(f"{script}: no say: blocks, skipped")
        return
    out_dir, cache = out_root / script.stem, out_root / ".cache"
    clips_dir = out_dir / "clips"
    shutil.rmtree(clips_dir, ignore_errors=True)
    clips_dir.mkdir(parents=True)
    cache.mkdir(parents=True, exist_ok=True)

    # 1. synthesize clips and lay them out on a timeline
    segments, timeline, captions = [], ["| Starts at | What |", "|---|---|"], []
    t, n, pending_gap = 0.0, 0, 0.0
    for event in events:
        if event[0] == "scene":
            timeline.append(f"| **{timestamp(t + ((pending_gap or GAP) if n else 0))}** | **🎬 {event[1]}** |")
        elif event[0] == "pause":
            pending_gap = event[1]
            timeline.append(f"| {timestamp(t)} | ⏸️ pause {event[1]:g}s |")
        else:
            _, speaker, text = event
            voice, rate = SPEAKERS[speaker]
            cached = cache / (hashlib.sha1(f"{voice}|{rate}|{text}".encode()).hexdigest() + ".mp3")
            if not cached.exists():
                synthesize(text, voice, rate, cached)
            n += 1
            clip = clips_dir / f"{n:02d}-{speaker}.mp3"
            shutil.copy(cached, clip)
            if n > 1:
                gap = pending_gap or GAP
                segments.append(("silence", gap))
                t += gap
            pending_gap = 0.0
            length = duration(clip)
            segments.append(("clip", clip))
            timeline.append(f"| {timestamp(t)} | `{clip.name}` {text} |")
            captions.append(f"{n}\n{timestamp(t, True)} --> {timestamp(t + length, True)}\n{text}\n")
            t += length
    if pending_gap:  # a pause after the last clip
        segments.append(("silence", pending_gap))
        t += pending_gap

    # 2. assemble the full voiceover with ffmpeg
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
    subprocess.run(cmd, check=True)

    (out_dir / "timeline.md").write_text(
        f"# {script.stem} — voiceover timeline\n\nTotal length: **{timestamp(t)}**\n\n" + "\n".join(timeline) + "\n",
        encoding="utf-8",
    )
    (out_dir / "captions.srt").write_text("\n".join(captions), encoding="utf-8")
    print(f"{script.name}: {n} clips, {timestamp(t)} -> {out_dir}")


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("scripts", nargs="+", type=pathlib.Path, help="video script .md files")
    parser.add_argument("--out", type=pathlib.Path, default=pathlib.Path("audio"), help="output folder (default: audio)")
    args = parser.parse_args()
    for tool in ("ffmpeg", "ffprobe"):
        if not shutil.which(tool):
            sys.exit(f"{tool} not found — install ffmpeg first.")
    for script in args.scripts:
        render(script, args.out)


if __name__ == "__main__":
    main()
