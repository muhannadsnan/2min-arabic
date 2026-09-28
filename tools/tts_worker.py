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

    import numpy as np
    import soundfile as sf
    from faster_whisper import WhisperModel

    model = WhisperModel("medium", device="cuda", compute_type="float16")
    from df.enhance import enhance, init_df, load_audio, save_audio   # DeepFilterNet: final noise removal
    df_model, df_state, _ = init_df()
    for job in jobs:
        lang = local_tts.SPEAKERS[job["speaker"]][2].get("lang", "en")
        best = None
        for k in range(job["takes"]):
            take = f"{job['prefix']}-take{k}.wav"
            # neutral Arabic context: very short words are otherwise misheard (عَفْوًا "af-wan" -> "اف 1")
            prompt = "جملة عربية قصيرة:" if lang == "ar" else None
            segments, _ = model.transcribe(take, language=lang, beam_size=5, initial_prompt=prompt, word_timestamps=True)
            segments = list(segments)
            heard = " ".join(s.text for s in segments).strip()
            words = [w for s in segments for w in s.words]
            length = sf.info(take).duration
            # extra made-up words after the sentence ("…his coffee. Aby"): cut after the script's last word
            script_last = normalize(job["text"]).split()[-1] if normalize(job["text"]) else ""
            match = [k for k, w in enumerate(words) if normalize(w.word) == script_last]
            extra = 0
            if match and len(words) - 1 - match[-1] > 0:
                extra = len(words) - 1 - match[-1]
                words = words[:match[-1] + 1]
                heard = " ".join(w.word.strip() for w in words)
            # extra made-up words before the sentence ("them. And did you notice…"): start at the script's first word
            script_first = normalize(job["text"]).split()[0] if normalize(job["text"]) else ""
            first = next((k for k, w in enumerate(words) if normalize(w.word) == script_first), None)
            lead = first if first is not None and first <= 2 else 0
            start_at = max(words[lead].start - 0.08, 0.0) if lead else 0.0
            if lead:
                words = words[lead:]
                heard = " ".join(w.word.strip() for w in words)
            extra += lead
            last_end = words[-1].end if words else length
            last_len = (words[-1].end - words[-1].start) if words else 0.0
            tail = length - last_end
            # penalties: a dragged last word or a long sound after it ("falling off a cliff")
            penalty = (0.3 if tail > 0.6 else 0.1 if tail > 0.35 else 0.2 if tail < 0.08 else 0.0) \
                + (0.2 if last_len > 1.1 else 0.0) + 0.15 * extra
            score_k = cer(job["text"], heard) + penalty
            if best is None or score_k < best[0]:
                best = (score_k, take, heard, last_end, tail, last_len, start_at)
        score_k, take, heard, last_end, tail, last_len, start_at = best
        audio, rate = sf.read(take)
        cut = min(len(audio), int((last_end + 0.22) * rate))   # keep a little air after the last word
        audio = audio[int(start_at * rate):cut].copy()
        if start_at:
            f_in = min(len(audio), int(0.03 * rate))
            audio[:f_in] *= np.linspace(0.0, 1.0, f_in)[:, None] if audio.ndim > 1 else np.linspace(0.0, 1.0, f_in)
        fade = min(len(audio), int(0.08 * rate))
        audio[-fade:] *= np.linspace(1.0, 0.0, fade)[:, None] if audio.ndim > 1 else np.linspace(1.0, 0.0, fade)
        sf.write(job["target"], audio, rate)
        clean, _ = load_audio(job["target"], sr=df_state.sr())          # guarantee a noise-free clip
        save_audio(job["target"], enhance(df_model, df_state, clean), df_state.sr())
        job["cer"], job["heard"] = round(score_k, 3), heard
        job["tail"], job["last_word"] = round(tail, 2), round(last_len, 2)
        flag = "  ⚠️" if score_k > 0.25 else ""
        print(f"  best {score_k:.2f}{flag} tail {tail:.2f}s last-word {last_len:.2f}s [{job['speaker']}] "
              f"{job['text'][:36]} → {heard[:36]}", flush=True)


if __name__ == "__main__":
    phase, path = sys.argv[1], pathlib.Path(sys.argv[2])
    jobs = json.loads(path.read_text(encoding="utf-8"))
    {"generate": generate, "score": score}[phase](jobs)
    path.write_text(json.dumps(jobs, ensure_ascii=False, indent=1), encoding="utf-8")
