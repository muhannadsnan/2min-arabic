#!/usr/bin/env python3
"""Upload captions timed against the FINISHED VIDEO itself (not the voiceover timeline) — run with the TTS venv:

    $TTS tools/sync_captions.py videos/NNN-….md [--video output/<video>/<file>.mp4]
        → output/<video>/captions-upload.srt  + a sync report

Why: captions built from timeline.json drift whenever the audio was rebuilt after the video was uploaded, and long
captions (a whole narrator line) feel out of sync with auto-translate (owner, 2026-10-05).
How: Whisper (English + Arabic, word timestamps) on the video's own audio; the SCRIPT's words are aligned to the
heard words (difflib), so the text is always exactly the script and the timing is the real one. English lines are
split into short captions (≤ 42 characters, at punctuation); Arabic lines read "Arabic (transliteration)"; filmed
clips keep their caption. Unmatched words are interpolated between matched neighbours.
Verify: every caption's own words must be heard inside its time window (report shows coverage).
"""
import argparse
import difflib
import json
import os
import pathlib
import re
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
TTS_HOME = pathlib.Path(os.environ.get("TTS_HOME", "/media/msn/GamesLinux/AI/tts"))
ARABIC = re.compile(r"[؀-ۿ]")
TASHKEEL = re.compile(r"[ً-ْٰ]")
MAX_CHARS, MAX_DUR, LEAD, TAIL = 42, 5.0, 0.08, 0.25


def ensure_cuda_libs():
    libs = sorted(str(p) for p in (TTS_HOME / "venv").glob("lib/python3*/site-packages/nvidia/*/lib"))
    if libs and not set(libs) <= set(os.environ.get("LD_LIBRARY_PATH", "").split(":")):
        os.environ["LD_LIBRARY_PATH"] = ":".join(libs + [os.environ.get("LD_LIBRARY_PATH", "")])
        os.execv(sys.executable, [sys.executable] + sys.argv)


def norm_en(w):
    import unicodedata
    w = unicodedata.normalize("NFKD", w).encode("ascii", "ignore").decode().lower().replace("’", "'")
    w = {"two": "2", "five": "5", "seven": "7", "eight": "8", "ten": "10", "one": "1", "three": "3", "four": "4",
         "six": "6", "nine": "9", "thirty": "30"}.get(re.sub(r"[^a-z0-9']", "", w), re.sub(r"[^a-z0-9']", "", w))
    return w


def norm_ar(w):
    w = TASHKEEL.sub("", w)
    w = re.sub("[إأآا]", "ا", w).replace("ة", "ه").replace("ى", "ي")
    return re.sub(r"[^ء-ي]", "", w)


def srt_time(x):
    ms = max(0, round(x * 1000))
    return f"{ms // 3600000:02}:{ms // 60000 % 60:02}:{ms // 1000 % 60:02},{ms % 1000:03}"


def align(script_tokens, heard):
    """script_tokens: [(norm, ...)], heard: [(norm, start, end)] → per script token (start, end) or None."""
    sm = difflib.SequenceMatcher(None, [t for t in script_tokens], [h[0] for h in heard], autojunk=False)
    times = [None] * len(script_tokens)
    for a, b, size in sm.get_matching_blocks():
        for k in range(size):
            times[a + k] = (heard[b + k][1], heard[b + k][2])
    return times


def fill(times):
    """Interpolate missing token times between matched neighbours."""
    n = len(times)
    for i in range(n):
        if times[i] is None:
            prev = next((times[j] for j in range(i - 1, -1, -1) if times[j]), None)
            nxt = next((times[j] for j in range(i + 1, n) if times[j]), None)
            if prev and nxt:
                times[i] = (prev[1], max(prev[1] + 0.05, nxt[0]))
            elif prev:
                times[i] = (prev[1], prev[1] + 0.3)
            elif nxt:
                times[i] = (max(0, nxt[0] - 0.3), nxt[0])
    return times


def chunks(words):
    """Split a line's words into captions ≤ MAX_CHARS: first at sentence ends, then at commas/colons, then at the word
    boundary nearest the middle — never leaving a lonely last word ("café.")."""
    def text(ws):
        return " ".join(x[0] for x in ws)

    def split(ws):
        if len(text(ws)) <= MAX_CHARS or len(ws) < 2:
            return [ws]
        mid = len(text(ws)) / 2
        cands = [k for k in range(1, len(ws)) if re.search(r"[.?!]$", ws[k - 1][0])] or \
                [k for k in range(1, len(ws)) if re.search(r"[,:;—]$", ws[k - 1][0])] or list(range(1, len(ws)))
        k = min(cands, key=lambda k: abs(len(text(ws[:k])) - mid))
        return split(ws[:k]) + split(ws[k:])

    out, cur = [], []
    for w in words:   # sentence ends first (short sentences may stay together)
        cur.append(w)
        if re.search(r"[.?!]$", w[0]) and len(text(cur)) > 18:
            out += split(cur); cur = []
    if cur:
        out += split(cur)
    return out


def main():
    ensure_cuda_libs()
    ap = argparse.ArgumentParser()
    ap.add_argument("script", type=pathlib.Path)
    ap.add_argument("--video", type=pathlib.Path)
    ap.add_argument("--out", type=pathlib.Path)
    ap.add_argument("--text-srt", type=pathlib.Path, help="take the caption text from this .srt (no markup script)")
    a = ap.parse_args()
    from make_audio import parse
    from upload_captions import on_screen_by_scene
    stem = a.script.stem
    video = a.video or next(p for p in sorted((ROOT / "output" / stem).glob("*.mp4"))
                            if "v1" not in p.name and "video-only" not in p.name)
    out = a.out or ROOT / "output" / stem / "captions-upload.srt"

    translit, cards = {}, []
    for card in (on_screen_by_scene(a.script) if not a.text_srt else []):
        if card:
            parts = [p.strip().strip("*") for p in card.split(" · ")]
            if len(parts) >= 2 and ARABIC.search(parts[0]):
                translit[re.sub(r"[\s.،؟!?]", "", parts[0])] = parts[1]   # exact (keeps vowel marks: أَنْتَ ≠ أَنْتِ)
                translit.setdefault(norm_ar(parts[0]), parts[1])
                cards.append((parts[0], parts[1]))

    if a.text_srt:   # no markup script (Day 1, filmed): the text of an existing .srt is the "script"
        blocks = a.text_srt.read_text(encoding="utf-8").strip().split("\n\n")
        events = [("say", "narrator", " ".join(b.split("\n")[2:])) for b in blocks if len(b.split("\n")) > 2]
    else:
        events = [e for e in parse(a.script) if e[0] in ("say", "video")]
    wav = out.parent / "sync-audio.wav"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(video), "-vn", "-ac", "1", "-ar", "16000", str(wav)], check=True)
    os.environ.setdefault("HF_HOME", str(TTS_HOME / "hf"))
    from faster_whisper import WhisperModel
    m = WhisperModel("medium", device="cuda", compute_type="float16")
    heard = {}
    for lang in ("en",):   # Arabic is placed by the gaps between narrator lines (an Arabic pass mis-hears English)
        segs, _ = m.transcribe(str(wav), language=lang, word_timestamps=True, beam_size=5, vad_filter=False)
        heard[lang] = [((norm_en if lang == "en" else norm_ar)(w.word), w.start, w.end) for s in segs for w in s.words]
        heard[lang] = [h for h in heard[lang] if h[0]]
    wav.unlink()

    # 1. English: align each narrator line IN ORDER against the heard words (a moving pointer, so a phrase that is
    #    repeated later in the video can never be matched to the wrong occurrence)
    import numpy as np, librosa
    H = heard["en"]
    by_event, p = {}, 0
    for k, e in enumerate(events):
        if e[0] != "say" or ARABIC.search(e[2]):
            continue
        words = []
        for w in e[2].split():   # punctuation-only tokens ("—") stay attached to the previous word
            if norm_en(w) or not words:
                words.append(w)
            else:
                words[-1] += " " + w
        words = [w for w in words if norm_en(w)]
        T = [norm_en(w) for w in words]
        # try windows that start at each of the next few heard words; keep the one that matches the most script
        # words, earliest first (repeated phrases like "How do you say" must not pull the pointer ahead)
        best = None
        for off in range(0, 40):
            win = H[p + off: p + off + int(1.3 * len(T)) + 6]
            if not win:
                break
            sm = difflib.SequenceMatcher(None, T, [h[0] for h in win], autojunk=False)
            n_match = sum(b[2] for b in sm.get_matching_blocks())
            if best is None or n_match > best[0]:
                best = (n_match, off, win, sm.get_matching_blocks())
            if n_match == len(T):
                break
        t = [None] * len(T)
        if best and best[0] >= max(1, len(T) // 2):
            _, off, win, blocks = best
            for a_, b_, size in blocks:
                for j in range(size):
                    t[a_ + j] = (win[b_ + j][1], win[b_ + j][2]); last = b_ + j
            p += off + last + 1
            by_event[k] = [(w, *tt) for w, tt in zip(words, fill(t)) if tt]
    # 2. Arabic lines and filmed clips sit in the gaps between narrator lines: split each gap's voiced audio
    y, sr = librosa.load(str(video), sr=16000)
    voiced = [(a_ / sr, b_ / sr) for a_, b_ in librosa.effects.split(y, top_db=32)]
    duration = len(y) / sr
    k = 0
    while k < len(events):
        if k in by_event or events[k][0] == "say" and not ARABIC.search(events[k][2]):
            k += 1; continue
        run_ = []
        while k < len(events) and not (events[k][0] == "say" and not ARABIC.search(events[k][2])):
            run_.append(k); k += 1
        g0 = max((by_event[j][-1][2] for j in range(run_[0]) if j in by_event), default=0.0)
        g1 = min((by_event[j][0][1] for j in range(k, len(events)) if j in by_event), default=duration)
        segs = [(max(a_, g0), min(b_, g1)) for a_, b_ in voiced if b_ > g0 + 0.05 and a_ < g1 - 0.05]
        n = len(run_)
        while len(segs) > n:   # merge the closest neighbours
            gaps = [segs[i + 1][0] - segs[i][1] for i in range(len(segs) - 1)]
            i = gaps.index(min(gaps)); segs[i:i + 2] = [(segs[i][0], segs[i + 1][1])]
        while 0 < len(segs) < n:   # split the longest
            i = max(range(len(segs)), key=lambda q: segs[q][1] - segs[q][0]); a_, b_ = segs[i]
            segs[i:i + 1] = [(a_, (a_ + b_) / 2), ((a_ + b_) / 2, b_)]
        if not segs:
            segs = [(g0 + (g1 - g0) * q / n, g0 + (g1 - g0) * (q + 1) / n) for q in range(n)]
        for j, (a_, b_) in zip(run_, segs):
            by_event[j] = [(events[j][2], a_, b_)]

    items = []
    for k, e in enumerate(events):
        words = by_event.get(k)
        if not words:
            print(f"⚠️ not found in the audio: {str(e[2])[:60]}")
            continue
        if e[0] == "video":
            if e[2]:
                items.append((words[0][1], words[-1][2], e[2]))
        elif ARABIC.search(e[2]):
            tr = translit.get(re.sub(r"[\s.،؟!?]", "", e[2])) or translit.get(norm_ar(e[2]), "")
            if not tr:   # the line is part of a longer card: take the matching words of that card's transliteration
                lw = [norm_ar(w) for w in e[2].split() if norm_ar(w)]
                for card_ar, card_tr in cards:
                    cw = [norm_ar(w) for w in card_ar.split() if norm_ar(w)]
                    tw = card_tr.split()
                    if len(tw) >= len(cw) and lw and cw[-len(lw):] == lw:   # "wa anti" = 2 words for وَأَنْتِ
                        tr = " ".join(tw[-(len(lw) + len(tw) - len(cw)):]); break
                    if len(cw) == len(tw) and lw and cw[:len(lw)] == lw:
                        tr = " ".join(tw[:len(lw)]); break
            items.append((words[0][1], words[-1][2], f"{e[2]} ({tr})" if tr else e[2]))
        else:
            for c in chunks(words):
                items.append((c[0][1], c[-1][2], " ".join(x[0] for x in c)))

    items.sort()
    final = []
    for i, (s, e, t) in enumerate(items):
        s = max(0.0, s - LEAD)
        nxt = items[i + 1][0] - LEAD if i + 1 < len(items) else duration
        e = min(max(e + TAIL, s + 0.8), nxt - 0.04, duration)
        if final and s < final[-1][1]:
            s = final[-1][1] + 0.02
        final.append((s, max(e, s + 0.3), t))
    out.write_text("\n".join(f"{n}\n{srt_time(s)} --> {srt_time(e)}\n{t}\n" for n, (s, e, t) in enumerate(final, 1)),
                   encoding="utf-8")

    # verification: each English caption's words must be heard inside its window
    bad = 0
    for s, e, t in final:
        if ARABIC.search(t):
            continue
        want = [norm_en(w) for w in t.split() if norm_en(w)]
        got = {h[0] for h in heard["en"] if s - 0.3 <= h[1] <= e + 0.3}
        cov = sum(w in got for w in want) / max(1, len(want))
        if cov < 0.6:
            bad += 1
            print(f"⚠️ {srt_time(s)} coverage {cov:.0%}: {t}")
    print(f"{out}: {len(final)} captions, {bad} with weak sync")


if __name__ == "__main__":
    main()
