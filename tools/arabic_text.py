#!/usr/bin/env python3
"""Arabic for beginners on screen: harakat ONLY where a word would otherwise be read as another word (owner 2026-11-03:
"don't overwhelm the beginner with such things now, they might take it later as they proceed").

    from arabic_text import minimal
    minimal("مَنْ هَذِهِ؟ أَنَا مِنْ سُورِيَا")  →  "مَن هذه؟ أنا مِن سوريا"

Kept: مَن (who) / مِن (from) · أنتَ / أنتِ (you, man / woman) · a final ـكِ / ـتِ (your / you, to a woman) when the
masculine form looks the same · shadda is dropped too (beginners read the word without it). Everything else: plain.
"""
import re
import sys

HARAKAT = re.compile(r"[ً-ْٰ]")   # tanween, fatha, damma, kasra, shadda, sukun, dagger alif
KEEP = {   # the plain word → how it must be shown, because the plain spelling reads as another word
    "من": None,          # decided from the original vowel: مَن (who) or مِن (from)
    "انت": None, "أنت": None,
}


def _plain(w):
    return HARAKAT.sub("", w)


def _word(w):
    plain = _plain(w)
    core = plain.strip("؟?!.،,:؛«»\"'()")
    if core == "من":
        if "مَن" in w or "مَنْ" in w:
            return plain.replace("من", "مَن", 1)
        if "مِن" in w or "مِنْ" in w:
            return plain.replace("من", "مِن", 1)
        return plain
    if core in ("أنت", "انت"):
        if "تِ" in w:
            return plain.replace("ت", "تِ", 1)
        if "تَ" in w:
            return plain.replace("ت", "تَ", 1)
        return plain
    # feminine endings that look like the masculine ones: ـكِ (your, to a woman) and a final ـتِ
    m = re.search(r"([كت])ِ([؟?!.،,:؛»\"')]*)$", w)
    if m and len(core) > 2:
        return re.sub(r"([كت])([؟?!.،,:؛»\"')]*)$", r"\1ِ\2", plain)
    return plain


def minimal(text):
    return " ".join(_word(w) for w in text.split(" "))


if __name__ == "__main__":
    for line in sys.argv[1:] or sys.stdin:
        print(minimal(line.rstrip("\n")))
