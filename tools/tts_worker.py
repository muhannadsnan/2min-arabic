#!/usr/bin/env python3
"""GPU worker for make_audio.py. Runs inside the local TTS environment (see docs/10-production-flow.md).

    <TTS_HOME>/venv/bin/python tools/tts_worker.py generate jobs.json   # synthesize N takes per line
    <TTS_HOME>/venv/bin/python tools/tts_worker.py score jobs.json      # speech-to-text check, pick the best take

The two phases run as separate processes so the voice model and the speech-to-text model never share the 6 GB GPU.
jobs.json: [{"text", "speaker", "takes", "prefix", "target"}, ...]  — takes are written to <prefix>-take<k>.wav,
the best one is copied to <target> and its score stored in the job ("cer", "heard").
"""
import json
import os
import pathlib
import re
import shutil
import sys

TTS_HOME = pathlib.Path(os.environ.get("TTS_HOME", "/media/msn/GamesLinux/AI/tts"))
sys.path.insert(0, str(TTS_HOME))
os.environ.setdefault("HF_HOME", str(TTS_HOME / "hf"))

HARAKAT = re.compile(r"[ً-ْٰـ]")
PUNCT = re.compile(r"[^\w\s]")


def normalize(text: str) -> str:
    text = HARAKAT.sub("", text)
    text = text.replace("أ", "ا").replace("إ", "ا").replace("آ", "ا").replace("ة", "ه").replace("ى", "ي")
    return " ".join(PUNCT.sub(" ", text.lower()).split())


def cer(ref: str, hyp: str) -> float:
    ref, hyp = normalize(ref), normalize(hyp)
    if not ref:
        return 0.0
    prev = list(range(len(hyp) + 1))
    for i, a in enumerate(ref, 1):
        cur = [i]
        for j, b in enumerate(hyp, 1):
            cur.append(min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + (a != b)))
        prev = cur
    return prev[-1] / len(ref)


def generate(jobs):
    import local_tts

    for job in jobs:
        for k in range(job["takes"]):
            local_tts.synthesize(job["text"], job["speaker"], pathlib.Path(f"{job['prefix']}-take{k}.wav"), seed=k)
        print(f"  generated {job['takes']}x [{job['speaker']}] {job['text'][:50]}", flush=True)


def score(jobs):
    import local_tts

    from faster_whisper import WhisperModel

    model = WhisperModel("medium", device="cuda", compute_type="float16")
    for job in jobs:
        lang = local_tts.SPEAKERS[job["speaker"]][2].get("lang", "en")
        best = None
        for k in range(job["takes"]):
            take = f"{job['prefix']}-take{k}.wav"
            segments, _ = model.transcribe(take, language=lang, beam_size=5)
            heard = " ".join(s.text for s in segments).strip()
            score_k = cer(job["text"], heard)
            if best is None or score_k < best[0]:
                best = (score_k, take, heard)
        shutil.copy(best[1], job["target"])
        job["cer"], job["heard"] = round(best[0], 3), best[2]
        flag = "  ⚠️" if best[0] > 0.25 else ""
        print(f"  best CER {best[0]:.2f}{flag}  [{job['speaker']}] {job['text'][:40]}  →  heard: {best[2][:40]}", flush=True)


if __name__ == "__main__":
    phase, path = sys.argv[1], pathlib.Path(sys.argv[2])
    jobs = json.loads(path.read_text(encoding="utf-8"))
    {"generate": generate, "score": score}[phase](jobs)
    path.write_text(json.dumps(jobs, ensure_ascii=False, indent=1), encoding="utf-8")
