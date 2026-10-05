#!/usr/bin/env python3
"""What people really type into YouTube search — YouTube's own autocomplete (free, no account, no API key).

    python3 tools/suggest.py "numbers in arabic" "محادثة بالعربي" [--hl en]

Prints the top suggestions per seed (most-searched first). Use them for search-phrase tags and the description's first
line; keep only suggestions a learner of THIS video would type (drop songs, perfumes, games, adult topics, "for kids").
"""
import argparse
import json
import urllib.parse
import urllib.request


def suggest(q, hl="en"):
    url = "https://suggestqueries.google.com/complete/search?" + urllib.parse.urlencode(
        {"client": "firefox", "ds": "yt", "hl": hl, "q": q})
    with urllib.request.urlopen(url, timeout=10) as r:
        return json.loads(r.read().decode("utf-8", "replace"))[1]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("seeds", nargs="+")
    ap.add_argument("--hl", default="en")
    a = ap.parse_args()
    for q in a.seeds:
        print(f"== {q}\n   " + "\n   ".join(suggest(q, a.hl)[:10]))


if __name__ == "__main__":
    main()
