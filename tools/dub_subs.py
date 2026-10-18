#!/usr/bin/env python3
"""Translated subtitle tracks from the same translations as the audio tracks (owner, 2026-10-18).

    python3 tools/dub_subs.py dubs/<video>.json [lang …]   → output/<video>/subs-<lang>.srt

Takes the English captions-upload.srt; every cue inside a translated narrator clip is replaced by the translation
(split into short cues over the clip's time); the Arabic cues (Arabic + transliteration) and everything else stay.
Upload: youtube_api.py subtitle <id> <lang> <srt> (400 quota units each → more than ~20 a day goes to the 09:15 queue).
"""
import json, pathlib, re, sys
ROOT = pathlib.Path(__file__).resolve().parent.parent
FIXED = {   # recurring filmed-clip cues
    "Thank you, and goodbye!": {"fr": "Merci, et au revoir !", "tr": "Teşekkürler, hoşça kal!", "es": "¡Gracias, y adiós!",
                                "hi": "शुक्रिया, और ख़ुदा हाफ़िज़!", "id": "Terima kasih, sampai jumpa!", "ms": "Terima kasih, selamat tinggal!", "ur": "شکریہ، اور خدا حافظ!",
                                "fa": "ممنون، و خداحافظ!", "de": "Danke, und tschüss!", "ru": "Спасибо, и до свидания!",
                                "pt": "Obrigado, e tchau!", "sw": "Asante, na kwaheri!", "zh": "谢谢，再见！",
                                "bn": "ধন্যবাদ, আর বিদায়!", "so": "Mahadsanid, nabadgelyo!"},
    "Welcome to 2 Minute Arabic!": {"fr": "Bienvenue sur 2 Minute Arabic !", "tr": "2 Minute Arabic'e hoş geldin!",
                                    "es": "¡Bienvenido a 2 Minute Arabic!", "hi": "2 Minute Arabic में आपका स्वागत है!",
                                    "id": "Selamat datang di 2 Minute Arabic!", "ms": "Selamat datang ke 2 Minute Arabic!", "ur": "2 Minute Arabic میں خوش آمدید!",
                                    "fa": "به 2 Minute Arabic خوش آمدید!", "de": "Willkommen bei 2 Minute Arabic!",
                                    "ru": "Добро пожаловать в 2 Minute Arabic!", "pt": "Bem-vindo ao 2 Minute Arabic!",
                                    "sw": "Karibu 2 Minute Arabic!", "zh": "欢迎来到 2 Minute Arabic！",
                                    "bn": "2 Minute Arabic-এ স্বাগতম!", "so": "Ku soo dhawoow 2 Minute Arabic!"},
}

def t2s(t): h, m, s = t.replace(",", ".").split(":"); return int(h) * 3600 + int(m) * 60 + float(s)
def s2t(x): ms = round(x * 1000); return f"{ms // 3600000:02}:{ms // 60000 % 60:02}:{ms // 1000 % 60:02},{ms % 1000:03}"

def chunks(text, n=42):   # even parts of ≤ ~n characters (no lonely last word)
    k = -(-len(text) // n); target = len(text) / k; out, cur = [], ""
    for w in text.split():
        if cur and len(cur) + 1 + len(w) > target * 1.15 and len(out) < k - 1: out.append(cur); cur = w
        else: cur = f"{cur} {w}".strip()
    return out + [cur] if cur else out

def main():
    spec = json.loads(pathlib.Path(sys.argv[1]).read_text(encoding="utf-8")); stem = spec["video"]
    langs = sys.argv[2:] or [k for k in spec if k != "video"]
    clips = json.loads((ROOT / "audio" / stem / "timeline.json").read_text())["clips"]
    od = ROOT / "output" / stem
    cues = [(t2s(a), t2s(b), txt.strip()) for a, b, txt in
            re.findall(r"\d+\n([\d:,]+) --> ([\d:,]+)\n(.*?)(?:\n\n|\Z)", (od / "captions-upload.srt").read_text(encoding="utf-8"), re.S)]
    for lang in langs:
        tr = spec[lang]; out = []
        arabic = lambda txt: re.search(r"[\u0600-\u06FF]", txt)
        for c in clips:   # translated narrator clips → new cues, proportional to text length
            if c["speaker"] == "narrator" and str(c["n"]) in tr:
                parts = chunks(tr[str(c["n"])]); tot = sum(map(len, parts)); t = c["start"]
                for p in parts:
                    d = (c["end"] - c["start"]) * len(p) / tot; out.append((t, t + d - 0.04, p)); t += d
        done = [c for c in clips if c["speaker"] == "narrator" and str(c["n"]) in tr]
        for a, b, txt in cues:   # keep the rest (Arabic lines, filmed clips), translating the fixed ones
            # the English captions are timed loosely → an English-only cue touching a translated clip goes
            if not arabic(txt) and any(a < c["end"] - 0.1 and b > c["start"] + 0.1 for c in done): continue
            for en, m in FIXED.items():
                if txt.startswith(en) and lang in m: txt = txt.replace(en, m[lang])
            out.append((a, b, txt))
        out.sort()
        srt = "\n".join(f"{i}\n{s2t(a)} --> {s2t(b)}\n{txt}\n" for i, (a, b, txt) in enumerate(out, 1))
        (od / f"subs-{lang}.srt").write_text(srt, encoding="utf-8")
        print(f"{lang}: {len(out)} cues → output/{stem}/subs-{lang}.srt")

if __name__ == "__main__":
    main()
