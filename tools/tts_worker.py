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
    import librosa
    NUM = {"0": "zero", "1": "one", "2": "two", "3": "three", "4": "four", "5": "five", "6": "six", "7": "seven",
           "8": "eight", "9": "nine", "10": "ten", "30": "thirty"}
    ref_pitch = {}

    def median_pitch(path):
        y, sr = librosa.load(path, sr=16000)
        f0, _, _ = librosa.pyin(y, fmin=65, fmax=320, sr=sr)
        f0 = f0[~np.isnan(f0)]
        return (float(np.median(f0)), f0) if len(f0) else (0.0, f0)

    ve_cache = {}

    def voice_match(path, speaker):
        """Cosine similarity of the take's speaker embedding to the speaker's reference (Chatterbox's own voice
        encoder). Low = the clone drifted to another voice/accent (owner, 2026-10-05: keep the relaxed American accent)."""
        import glob
        import torch
        from chatterbox.models.voice_encoder import VoiceEncoder
        if "ve" not in ve_cache:
            ve = VoiceEncoder()
            ck = glob.glob(str(pathlib.Path(os.environ.get("HF_HOME", "")) / "hub/models--ResembleAI--chatterbox/snapshots/*/ve.pt"))
            ve.load_state_dict(torch.load(ck[0], map_location="cpu")); ve.eval(); ve_cache["ve"] = ve
        ve = ve_cache["ve"]
        def emb(f):
            w, _ = librosa.load(str(f), sr=16000)
            return ve.embeds_from_wavs([w], sample_rate=16000, as_spk=True)
        if speaker not in ve_cache:
            ve_cache[speaker] = emb(local_tts.SPEAKERS[speaker][1])
        r, e = ve_cache[speaker], emb(path)
        return float(np.dot(r, e) / (np.linalg.norm(r) * np.linalg.norm(e)))

    def delivery(path, words, speaker):
        """Penalty for a take that sounds robotic: flat, rushed, stretched, pitch drifting away from the speaker,
        or a voice/accent that drifts away from the reference."""
        if speaker not in ref_pitch:
            ref = local_tts.SPEAKERS[speaker][1]
            ref_pitch[speaker] = median_pitch(ref)[0] if ref and str(ref).endswith(".wav") else 0.0
        med, f0 = median_pitch(path)
        notes, pen = [], 0.0
        if len(f0) and len(words) >= 5:
            st = 12 * np.log2(f0 / med)
            rng = np.percentile(st, 90) - np.percentile(st, 10)
            if rng < 8.0:
                pen += 0.25 if rng < 6.0 else 0.12
                notes.append(f"flat {rng:.1f}st")
        if ref_pitch[speaker] and med and abs(12 * np.log2(med / ref_pitch[speaker])) > 1.5:
            pen += 0.2
            notes.append("pitch drift")
        if len(words) >= 3:
            speech = words[-1].end - words[0].start
            wps = len(words) / max(speech, 0.1)
            if wps > 3.6:
                pen += 0.25
                notes.append(f"rushed {wps:.1f}w/s")
            gaps = [b.start - a.end for a, b in zip(words, words[1:])]
            if gaps and max(gaps) > 1.0:
                pen += 0.2
                notes.append("long gap")
        try:
            sim = voice_match(path, speaker) if sf.info(path).duration >= 2.6 else 1.0   # short clips: unreliable
            if sim < 0.90:
                pen += 0.3 if sim < 0.87 else 0.12
                notes.append(f"voice/accent drift {sim:.2f}")
            # a few words in another accent: score 1.6-s windows, penalise the worst (owner: American only)
            if sf.info(path).duration >= 2.6:
                yy, srr = librosa.load(path, sr=16000)
                win = int(1.6 * srr)
                worst = 1.0
                for i in range(0, len(yy) - win + 1, int(0.4 * srr)):
                    seg = path + ".win.wav"
                    sf.write(seg, yy[i:i + win], srr)
                    worst = min(worst, voice_match(seg, speaker))
                pathlib.Path(path + ".win.wav").unlink(missing_ok=True)
                if worst < 0.70:   # calibrated on the owner's real voice (windows 0.47–0.87, median 0.84)
                    pen += 0.25
                    notes.append(f"accent slip {worst:.2f}")
        except Exception as ex:   # never block generation on the check itself
            notes.append(f"voice check failed: {ex.__class__.__name__}")
        for w in words:
            token = re.sub(r"\W", "", w.word)
            letters = len(NUM.get(token, token)) or 1
            if (w.end - w.start) / letters > 0.22 and letters >= 1 and (w.end - w.start) > 0.75:
                pen += 0.25
                notes.append(f"stretched '{token}'")
                break
        return pen, notes
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
            d_pen, d_notes = delivery(take, words, job["speaker"]) if lang == "en" else (0.0, [])
            score_k = cer(job["text"], heard) + penalty + d_pen
            if best is None or score_k < best[0]:
                best = (score_k, take, heard, last_end, tail, last_len, start_at, d_notes)
        score_k, take, heard, last_end, tail, last_len, start_at, d_notes = best
        audio, rate = sf.read(take)
        cut = min(len(audio), int((last_end + 0.22) * rate))   # keep a little air after the last word
        audio = audio[int(start_at * rate):cut].copy()
        if start_at:
            f_in = min(len(audio), int(0.03 * rate))
            audio[:f_in] *= np.linspace(0.0, 1.0, f_in)[:, None] if audio.ndim > 1 else np.linspace(0.0, 1.0, f_in)
        fade = min(len(audio), int(0.08 * rate))
        audio[-fade:] *= np.linspace(1.0, 0.0, fade)[:, None] if audio.ndim > 1 else np.linspace(1.0, 0.0, fade)
        sf.write(job["target"], audio, rate)   # generated speech is clean (clean references) - no extra processing
        job["delivery"] = ", ".join(d_notes)
        job["cer"], job["heard"] = round(score_k, 3), heard
        job["tail"], job["last_word"] = round(tail, 2), round(last_len, 2)
        flag = "  ⚠️" if score_k > 0.25 else ""
        print(f"  best {score_k:.2f}{flag} {job['delivery'] or 'delivery ok'} [{job['speaker']}] "
              f"{job['text'][:36]} → {heard[:36]}", flush=True)


if __name__ == "__main__":
    phase, path = sys.argv[1], pathlib.Path(sys.argv[2])
    jobs = json.loads(path.read_text(encoding="utf-8"))
    {"generate": generate, "score": score}[phase](jobs)
    path.write_text(json.dumps(jobs, ensure_ascii=False, indent=1), encoding="utf-8")
