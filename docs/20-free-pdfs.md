# 20 — Free PDFs (lead magnets)

Why (owner + Claude, 20 Oct): too early to sell; a free, useful PDF gives YouTube and Instagram viewers a reason to
visit, shows real demand, and later can collect emails for the membership launch (docs/19).

## PDF 1 — "Your first 83 Arabic words & phrases" (Days 1–10)

- File: `output/free-pdfs/2-minute-arabic-days-1-10.pdf` (6 pages), built from `output/free-pdfs/days-1-10.html`.
- Content: every on-screen word card of Days 1–10 (Arabic with harakat · transliteration · meaning), grouped by day and
  topic, repeats removed (`days-1-10.json` = the cards extracted from `videos/0NN-*.md` "On screen" lines — the ledger in
  docs/13 has only key words, 36 of them). Cover, "how to use", transliteration key, "Continue with Day 11 on YouTube".
- **Hosted on our website** (GitHub Pages, branch gh-pages, folder `free/`):
  download page **https://muhannadsnan.github.io/2min-arabic/free/** · PDF
  https://muhannadsnan.github.io/2min-arabic/free/2-minute-arabic-days-1-10.pdf · also linked from the homepage.
  Conventional place for a lead magnet = your own site; later the same page can get an email form (e.g. MailerLite free
  plan) without changing the link.

## Where the link goes

- **YouTube descriptions:** one line "📄 Free PDF — your first 83 Arabic words: <link>" under the Day 1 link — added
  with the queued 13-language description update (API, when there's room) and in every new sheet from now on.
- **Instagram:** the bio link (Linktree-style or the site's homepage) + a mention in captions of word-list Reels.
- **Pinned comments** on Days 1–10.

## PDF 2 — "118 more Arabic words & phrases" (Days 11–20 + Extras x05, x06, Vocab v01, v02) — published 26 Oct

- Built with `python3 tools/free_pdf.py 11 20 --extra x05-…,x06-…,v01-…,v02-…` (8 pages; words already in PDF 1 skipped).
- https://muhannadsnan.github.io/2min-arabic/free/2-minute-arabic-days-11-20.pdf, card on the downloads page.

## Next PDFs (one per 10 days)

Days 11–20 (after Day 20), Days 21–30, then topic sheets (numbers, café words, body words). Same builder: extract the
"On screen" cards of the days, dedupe, render with the same HTML, publish under `free/`.
