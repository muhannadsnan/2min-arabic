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
    import numpy as np, soundfile as sf, io
    SR = 48000
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", src, "-f", "wav", "-ac", "1", "-ar", str(SR), "-"], capture_output=True).stdout
    y, _ = sf.read(io.BytesIO(raw))
    # room tone (owner 2026-10-18: pauses must sound like the room, not digital silence): a quiet stretch of the same
    # recording, looped with crossfades under the whole track; it ducks under each sentence (which has its own room)
    a0, a1 = e.get("room_tone", [0, 0])
    rt = y[int(a0 * SR):int(a1 * SR)]; xf = int(0.25 * SR)
    def bed(n):
        out = np.zeros(n); pos = 0; ramp = np.linspace(0, 1, xf)
        while pos < n:
            seg = rt.copy()
            if pos: seg[:xf] *= ramp; out[pos:pos + xf] *= 1 - ramp[:max(0, min(xf, n - pos))]
            k = min(len(seg), n - pos); out[pos:pos + k] += seg[:k]; pos += len(seg) - xf
        return out
    for name, cuts in e.items():
        if not isinstance(cuts, list) or name in ("settings", "room_tone"): continue
        pieces, t = [], 0.0
        for a, b, p in cuts:
            seg = y[int(a * SR):int(b * SR)].copy(); f = int(0.03 * SR)
            seg[:f] *= np.linspace(0, 1, f); seg[-f:] *= np.linspace(1, 0, f)
            pieces.append((int(t * SR), seg)); t += (b - a) + p * pscale
        n = int(t * SR) + SR // 10
        voice = np.zeros(n); duck = np.ones(n); r = int(0.04 * SR)
        for at, seg in pieces:
            voice[at:at + len(seg)] += seg
            duck[at + r:at + len(seg) - r] = 0
            duck[at:at + r] = np.minimum(duck[at:at + r], np.linspace(1, 0, r))
            duck[at + len(seg) - r:at + len(seg)] = np.minimum(duck[at + len(seg) - r:at + len(seg)], np.linspace(0, 1, r))
        mix = voice + bed(n) * duck if len(rt) else voice
        tmp = D / f"_{name}.wav"; sf.write(tmp, mix, SR)
        out = D / f"{name}.wav"
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(tmp), "-af", chain, "-ar", "48000", str(out)], check=True)
        tmp.unlink()
        d = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(out)],
                                 capture_output=True, text=True).stdout)
        print(f"{name}: {d:.1f}s → {out}")


if __name__ == "__main__":
    main()
