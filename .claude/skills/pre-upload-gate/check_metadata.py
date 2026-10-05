#!/usr/bin/env python3
"""Metadata part of the pre-upload gate: python3 .claude/skills/pre-upload-gate/check_metadata.py <stem>

Reads videos/<stem>-upload.md and videos/<stem>-description.txt and checks our upload rules
(docs/06-publishing.md). Prints one line per check; exit code 1 if any check fails.
"""
import re
import sys
from datetime import date
from pathlib import Path

stem = sys.argv[1]
repo = Path(__file__).resolve().parents[3]


def find(suffix):
    """videos/<stem>-<suffix> or, for full-slug names (Extras), videos/<stem>*-<suffix>."""
    exact = repo / f"videos/{stem}-{suffix}"
    hits = [exact] if exact.exists() else sorted((repo / "videos").glob(f"{stem}*-{suffix}"))
    if len(hits) > 1:
        sys.exit(f"ambiguous stem {stem!r}: {[h.name for h in hits]}")
    return hits[0] if hits else exact


if not find("upload.md").exists():
    sys.exit(f"no upload sheet for {stem!r} yet: write it with the upload-handover skill first")
sheet = find("upload.md").read_text(encoding="utf-8")
desc_file = find("description.txt")
fails = 0


def check(ok, label):
    global fails
    fails += not ok
    print(("PASS  " if ok else "FAIL  ") + label)


check(desc_file.exists(), f"{desc_file.name} exists")
if desc_file.exists():
    desc = desc_file.read_text(encoding="utf-8")
else:  # fall back to the box in the sheet
    m = re.search(r"## Description.*?```\n(.+?)\n```", sheet, re.S)
    desc = m.group(1) if m else ""


# Title
m = re.search(r"## Title\s+```\n(.+?)\n```", sheet)
title = m.group(1) if m else ""
check(bool(title), "title found in a code box")
benefit, _, series = title.partition(" | ")
check("#" not in title, "no hashtags in the title")
check(len(benefit) <= 50, f"benefit part {len(benefit)} chars (≤ 50)")
check(bool(re.fullmatch(r"(Day \d+ · 2 Minute Arabic|Part \d+ · Days \d+–\d+|Arabic Extras)", series)),
      f"series suffix: '{series}'")
caps = [w for w in re.findall(r"[A-Za-z']+", benefit) if len(w) > 2 and w.isupper()]
check(len(caps) <= 1, f"at most one ALL-CAPS word (found {caps or 'none'})")

# Description
ar = re.compile("[؀-ۿ]")
bad = [n for n, line in enumerate(desc.splitlines(), 1) if ar.search(line) and not (
    "⁧" in line and line.rstrip().endswith("⁩") and not ar.search(line.split("⁧")[0]))]
check(not bad, f"Arabic at line end inside U+2067…U+2069 (bad lines: {bad or 'none'})")
tags_h = re.findall(r"#\w+", desc)
check(2 <= len(tags_h) <= 3, f"~3 hashtags in the description: {tags_h}")
check("?si=" not in desc, "no ?si= in links")
check(desc.strip() in sheet, "description.txt matches the box in the sheet")

# Tags
m = re.search(r"## Tags.*?```\n(.+?)\n```", sheet, re.S)
tags = [t.strip() for t in m.group(1).split(",")] if m else []
check(12 <= len(tags) <= 28, f"{len(tags)} tags (search phrases · translit · Arabic · niche · broad)")
check(len(", ".join(tags)) <= 480, f"tags {len(', '.join(tags))} chars (≤ 500)")
check(not any("#" in t for t in tags), "no # inside tags")
check(sum(bool(ar.search(t)) for t in tags) >= 5, f"{sum(bool(ar.search(t)) for t in tags)} Arabic-script tags (≥ 5)")
check(any(ar.search(t) and re.search(r"[A-Za-z]", t) for t in tags), "a mixed tag ('طيب meaning')")
check(any(t.isascii() and " " not in t and t not in ("shorts",) for t in tags) or len(tags) >= 12, "transliterated keyword tags present")
if "viral shorts" in tags and date.today() >= date(2026, 10, 6):
    print("NOTE  'viral shorts' tag: the experiment was due for a verdict on 2026-10-06 — check docs/06")

# Settings the owner must not miss
for needed in ("AI use", "Related video", "Playlist", "not made for kids"):
    check(needed.lower() in sheet.lower(), f"sheet mentions '{needed}'")

sys.exit(1 if fails else 0)
