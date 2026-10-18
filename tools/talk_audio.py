#!/usr/bin/env python3
"""Owner's talk videos (clay presenter): cut the chosen takes from a raw recording into one clean voice track.

    python3 tools/talk_audio.py footage/recordings/_talk-scripts/edl.json
        → footage/recordings/_talk-scripts/<name>.wav for every list in the EDL

edl.json: {"source": "<raw file in the same folder>", "<name>": [[start, end, pause after], ...]}. Cut points come from
transcribing each speech chunk (pick the LAST clean take of each sentence), trimmed to the first/last word.
Recordings stay private (footage/recordings is git-ignored).
"""
import json, pathlib, subprocess, sys

def main():
    edl = pathlib.Path(sys.argv[1]); D = edl.parent; e = json.loads(edl.read_text())
    src = str(D / e["source"]); st = e.get("settings", {})
    tempo, pscale = st.get("tempo", 1.0), st.get("pause_scale", 1.0)
    # livelier delivery (owner 2026-10-18: "too stiff"): a touch faster (pitch kept), shorter pauses, presence EQ,
    # gentle compression so quiet words don't sink, then loudness
    chain = (f"highpass=f=80,equalizer=f=300:t=q:w=1:g=-2,equalizer=f=3500:t=q:w=1.2:g=3,highshelf=f=9000:g=2,"
             f"acompressor=threshold=-20dB:ratio=3:attack=8:release=120:makeup=2,"
             f"atempo={tempo},loudnorm=I=-16:TP=-1.5")
    for name, cuts in e.items():
        if not isinstance(cuts, list) or name == "settings": continue
        parts = []
        for i, (a, b, p) in enumerate(cuts):
            f = D / f"_{name}-{i:02}.wav"
            subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", str(a), "-to", str(b), "-i", src, "-af",
                            f"afade=t=in:d=0.02,afade=t=out:st={b - a - 0.04:.3f}:d=0.04,apad=pad_dur={p * pscale}",
                            "-ar", "48000", "-ac", "1", str(f)], check=True)
            parts.append(f)
        lst = D / f"_{name}.txt"; lst.write_text("".join(f"file '{x.name}'\n" for x in parts))
        out = D / f"{name}.wav"
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", str(lst),
                        "-af", chain, "-ar", "48000", str(out)], check=True)
        for x in parts + [lst]: x.unlink()
        d = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(out)],
                                 capture_output=True, text=True).stdout)
        print(f"{name}: {d:.1f}s → {out}")

if __name__ == "__main__":
    main()
