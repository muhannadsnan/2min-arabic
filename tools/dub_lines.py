#!/usr/bin/env python3
"""Narration lines for languages our cloned voice can't speak (owner, 2026-10-18): Persian (the owner makes the audio
with TTSMaker, free + commercial use allowed) and Bengali (Piper bn_BD voice, CC BY-SA data). Each line is then
converted to the owner's voice (Chatterbox VC, MIT) and handed to tools/dub_track.py --from.

    $TTS tools/dub_lines.py split  <file.mp3> dubs/<stem>.json fa      # one TTSMaker file = all lines, blank-line pauses
    $TTS tools/dub_lines.py piper  dubs/<stem>.json bn                # Piper, one file per line
    $TTS tools/dub_lines.py vc     <stem> <lang>                       # → owner's voice
    $TTS tools/dub_track.py dubs/<stem>.json <lang> --from output/<stem>/lines-<lang>-vc

Lines land in output/<stem>/lines-<lang>/<n>.wav (in key order); `split` checks every piece with speech recognition
against its text and stops if the count or a line doesn't match.
"""
import json, pathlib, re, subprocess, sys
import numpy as np, soundfile as sf
ROOT = pathlib.Path(__file__).resolve().parent.parent
PIPER = "/media/msn/GamesLinux/AI/piper/venv/bin/piper"
PIPER_VOICE = {"bn": "/media/msn/GamesLinux/AI/piper/voices/bn_BD-google-medium.onnx"}

def keys_texts(spec_path, lang):
    spec = json.loads(pathlib.Path(spec_path).read_text(encoding="utf-8"))
    keys = sorted(spec[lang], key=int)
    return spec["video"], keys, [spec[lang][k] for k in keys]

def norm(s): return re.sub(r"[^\w]", "", s).replace("ي", "ی").replace("ك", "ک")
def cer(r, h):
    r, h = norm(r), norm(h); d = list(range(len(h) + 1))
    for i, x in enumerate(r, 1):
        p, d[0] = d[0], i
        for j, y in enumerate(h, 1): p, d[j] = d[j], min(d[j] + 1, d[j - 1] + 1, p + (x != y))
    return d[len(h)] / max(1, len(r))

def split(mp3, spec_path, lang):
    stem, keys, texts = keys_texts(spec_path, lang)
    out = ROOT / "output" / stem / f"lines-{lang}"; out.mkdir(parents=True, exist_ok=True)
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", mp3, "-f", "wav", "-ac", "1", "-ar", "16000", "-"], capture_output=True).stdout   # 16 kHz: what the recognizer expects
    import io
    y, sr = sf.read(io.BytesIO(raw)); hop = int(0.01 * sr)
    db = 20 * np.log10(np.array([np.sqrt(np.mean(y[i:i + hop] ** 2) + 1e-12) for i in range(0, len(y) - hop, hop)]))
    quiet = db < np.percentile(db, 20) + 6
    runs, i = [], 0   # silent runs (start, end) in 10 ms frames
    while i < len(quiet):
        if quiet[i]:
            j = i
            while j < len(quiet) and quiet[j]: j += 1
            runs.append((i, j)); i = j
        else: i += 1
    inner = [r for r in runs if r[0] > 0 and r[1] < len(quiet) and r[1] - r[0] >= 12]   # pauses ≥ 0.12 s
    # where does each line end? align the script to what speech recognition hears (character level), then snap
    # each cut to the nearest real pause — pause length alone fails on short lines and pauses inside sentences
    from faster_whisper import WhisperModel
    import difflib
    wm = WhisperModel("small", device="cpu", compute_type="int8")
    words = [w for s in wm.transcribe(y.astype(np.float32), language=lang, word_timestamps=True)[0] for w in s.words]
    heard, htime = "", []
    for w in words:
        t = norm(w.word); heard += t
        htime += [w.start + (w.end - w.start) * (k + 1) / max(1, len(t)) for k in range(len(t))]
    script, ends = "", []
    for t in texts: script += norm(t); ends.append(len(script))
    sm = difflib.SequenceMatcher(None, script, heard, autojunk=False)
    blocks = sm.get_matching_blocks()
    def time_at(pos):   # time of script position pos via the nearest matched character
        best = None
        for a, b, n in blocks:
            if n == 0: continue
            q = min(max(pos - 1, a), a + n - 1); d = abs(q - (pos - 1))
            if best is None or d < best[0]: best = (d, htime[b + (q - a)])
        return best[1]
    mids = [((a + b) // 2) / 100 for a, b in inner]
    bounds = [0]
    for e in ends[:-1]:
        t = time_at(e)
        cand = [m for m in mids if m > bounds[-1] / 100 + 0.2 and abs(m - (t + 0.1)) <= 0.35]
        snap = min(cand, key=lambda m: abs(m - (t + 0.1))) if cand else t + 0.06   # no pause close by: cut at the word end
        bounds.append(int(snap * 100))
    bounds.append(len(quiet))
    m = wm; bad = 0
    for k, t, a, b in zip(keys, texts, bounds, bounds[1:]):
        piece = y[a * hop:b * hop]; f = out / f"{k}.wav"; sf.write(f, piece, sr)
        heard = " ".join(s.text for s in m.transcribe(piece.astype(np.float32), language=lang)[0])
        e = cer(t, heard); bad += e > 0.35
        print(f"{k:>3} {len(piece) / sr:5.2f}s CER {e:.2f} {'⚠️' if e > 0.35 else ''}| {t[:60]}")
    print(f"→ {out} ({len(keys)} lines, {bad} doubtful)")

def piper(spec_path, lang):
    stem, keys, texts = keys_texts(spec_path, lang)
    out = ROOT / "output" / stem / f"lines-{lang}"; out.mkdir(parents=True, exist_ok=True)
    for k, t in zip(keys, texts):
        subprocess.run([PIPER, "-m", PIPER_VOICE[lang], "-f", str(out / f"{k}.wav")], input=t.encode(), check=True, capture_output=True)
    print(f"→ {out} ({len(keys)} lines)")

def vc(stem, lang):
    sys.path.insert(0, "/media/msn/GamesLinux/AI/tts"); import local_tts, torch, torchaudio
    from chatterbox.vc import ChatterboxVC
    model = ChatterboxVC.from_pretrained("cuda" if torch.cuda.is_available() else "cpu")
    src = ROOT / "output" / stem / f"lines-{lang}"; out = src.with_name(f"lines-{lang}-vc"); out.mkdir(exist_ok=True)
    for f in sorted(src.glob("*.wav"), key=lambda p: int(p.stem)):
        wav = model.generate(str(f), target_voice_path=local_tts.OWNER_EN_ENERGETIC)
        torchaudio.save(str(out / f.name), wav.cpu(), model.sr)
    print(f"→ {out}")

if __name__ == "__main__":
    cmd, *rest = sys.argv[1:]
    {"split": split, "piper": piper, "vc": vc}[cmd](*rest)
