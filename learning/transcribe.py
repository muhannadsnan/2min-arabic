#!/usr/bin/env python3
"""learning/transcribe.py <audio> <out.txt> — faster-whisper medium, [mm:ss] per segment (learn-from-source step 2)."""
import sys
from faster_whisper import WhisperModel
src, out = sys.argv[1], sys.argv[2]
m = WhisperModel("medium", device="cuda", compute_type="float16")
seg, info = m.transcribe(src, language="en", vad_filter=True)
with open(out, "w", encoding="utf-8") as f:
    for s in seg:
        f.write(f"[{int(s.start // 60):02d}:{int(s.start % 60):02d}] {s.text.strip()}\n")
print("done", out)
