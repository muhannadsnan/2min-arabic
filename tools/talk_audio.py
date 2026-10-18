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
    src = str(D / e["source"])
    for name, cuts in e.items():
        if not isinstance(cuts, list): continue
        parts = []
        for i, (a, b, p) in enumerate(cuts):
            f = D / f"_{name}-{i:02}.wav"
            subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", str(a), "-to", str(b), "-i", src, "-af",
                            f"afade=t=in:d=0.03,afade=t=out:st={b - a - 0.06:.3f}:d=0.06,apad=pad_dur={p}",
                            "-ar", "48000", "-ac", "1", str(f)], check=True)
            parts.append(f)
        lst = D / f"_{name}.txt"; lst.write_text("".join(f"file '{x.name}'\n" for x in parts))
        out = D / f"{name}.wav"
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", str(lst),
                        "-af", "highpass=f=80,loudnorm=I=-16:TP=-1.5", "-ar", "48000", str(out)], check=True)
        for x in parts + [lst]: x.unlink()
        d = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(out)],
                                 capture_output=True, text=True).stdout)
        print(f"{name}: {d:.1f}s → {out}")

if __name__ == "__main__":
    main()
