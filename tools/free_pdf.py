#!/usr/bin/env python3
"""Free PDF word lists (docs/20): every on-screen word card of a range of days (+ Extras/Vocab), deduped, as a PDF.

    python3 tools/free_pdf.py 11 20 --extra x05-syrians-say-biddi,x06-arabic-numbers-11-to-20,v01-cafe-words,v02-body-words

Writes output/free-pdfs/days-<a>-<b>.json + .html + 2-minute-arabic-days-<a>-<b>.pdf (Chrome headless, A4), using the
look of PDF 1 (days-1-10.html). Cards are the "🔤 On screen:" lines "Arabic · *translit* · English" of each script.
"""
import argparse
import html
import json
import pathlib
import re
import subprocess
import unicodedata


def norm(ar):
    """Dedupe key: Arabic letters only (no harakat, punctuation or spaces)."""
    return "".join(c for c in ar if "\u0621" <= c <= "\u064A")

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "output" / "free-pdfs"
CARD = re.compile(r"^🔤 \*\*On screen:\*\* (.+)$", re.M)
TITLE = re.compile(r"^# (?:Day \d+|Arabic Extras|Arabic Vocab)\s*[—-]\s*(?:[A-Za-z]+:\s*)?(.+)$", re.M)
NOISE = re.compile(r"\s*·?\s*(Word|Verb|Step|Question|Lifesaver|Round|Quiz|Day)\s*\d+(/\d+)?.*$")
CLEAN = [re.compile(x) for x in (r"\s*·\s*NEW(:.*)?$", r"\s*·\s*\d+/\d+$", r"\s*·\s*you know it from.*$", r"\s*·\s*special$")]


def cards(path):
    text = path.read_text(encoding="utf-8")
    title = (TITLE.search(text).group(1) if TITLE.search(text) else path.stem).strip()
    title = re.sub(r"\s*\(.*?\)\s*$", "", title).strip()
    title = title[0].upper() + title[1:]
    out, seen = [], set()
    for line in CARD.findall(text):
        parts = [p.strip() for p in line.split(" · ")]
        if len(parts) < 3 or not re.search(r"[؀-ۿ]", parts[0]) or not parts[1].startswith("*"):
            continue
        ar, tr = parts[0], parts[1].strip("*")
        en = NOISE.sub("", " · ".join(parts[2:])).strip(" ·")
        en = re.sub(r"\s*·\s*NEW\s*(?=·)", "", en)
        for c in CLEAN:
            en = c.sub("", en).strip(" ·")
        if not en or norm(ar) in seen or "Your turn" in en:
            continue
        seen.add(norm(ar)); out.append([ar, tr, en])
    return title, out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("a", type=int); ap.add_argument("b", type=int)
    ap.add_argument("--extra", default="")
    a = ap.parse_args()
    groups, total, global_seen = [], 0, set()
    for prev in OUT.glob("days-*-*.json"):   # words already in an earlier PDF are not repeated
        if prev.name != f"days-{a.a}-{a.b}.json":
            for v in json.loads(prev.read_text()).values():
                global_seen.update(norm(x[0]) for x in v)
    stems = [f"{d:03d}" for d in range(a.a, a.b + 1)] + [s for s in a.extra.split(",") if s]
    for st in stems:
        f = next((p for p in sorted((ROOT / "videos").glob(f"{st}*.md"))
                  if not re.search(r"(upload|description|recording|whatsapp)", p.name)), None)
        if not f:
            continue
        title, cs = cards(f)
        cs = [c for c in cs if norm(c[0]) not in global_seen]
        global_seen.update(norm(c[0]) for c in cs)
        label = f"Day {int(st)}" if st.isdigit() else ("Extra" if st.startswith("x") else "Vocab")
        if cs:
            groups.append((label, title, cs)); total += len(cs)
    tag = f"days-{a.a}-{a.b}"
    (OUT / f"{tag}.json").write_text(json.dumps({g[0] + " " + g[1]: g[2] for g in groups}, ensure_ascii=False, indent=1))
    style = (OUT / "days-1-10.html").read_text(encoding="utf-8").split("</style>")[0] + "</style>"
    body = [f"""</head><body>
<div class="cover">
 <div class="badge">FREE · DAYS {a.a}–{a.b}</div>
 <h1>{total} more<br>Arabic words &amp; phrases</h1>
 <div class="ar" dir="rtl">أُرِيدُ قَهْوَةْ، مِنْ فَضْلِكْ</div>
 <p>Every word from Days {a.a}–{a.b} of the free course, plus the bonus videos</p>
 <p>Arabic · transliteration · meaning</p>
 <div class="foot">2 Minute Arabic · youtube.com/@2MinArabic · instagram.com/2minutearabic</div>
</div>
<div class="tip"><b>How to use this list:</b> watch the day's 2-minute lesson, then read the words here out loud once. Cover the English column and test yourself the next day. Two minutes a day is enough.</div>"""]
    for label, title, cs in groups:
        rows = "".join(f'<tr><td class="ar" dir="rtl">{html.escape(ar)}</td><td class="tr">{html.escape(tr)}</td>'
                       f'<td class="en">{html.escape(en)}</td></tr>' for ar, tr, en in cs)
        body.append(f'<section><h2><span class="d">{label}</span> {html.escape(title)}</h2><table>{rows}</table></section>')
    body.append(f'<div class="end">Continue with Day {a.b + 1} on YouTube — <b>2 Minute Arabic</b>. Two minutes a day.</div></body></html>')
    page = OUT / f"{tag}.html"
    page.write_text(style + "\n".join(body), encoding="utf-8")
    pdf = OUT / f"2-minute-arabic-{tag}.pdf"
    subprocess.run(["google-chrome", "--headless=new", "--disable-gpu", "--no-pdf-header-footer",
                    f"--print-to-pdf={pdf}", page.as_uri()], check=True, capture_output=True)
    print(f"{pdf}: {total} entries in {len(groups)} sections")


if __name__ == "__main__":
    main()
