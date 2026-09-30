---
name: arabic-extras
description: Make an "Arabic Extras" Short for 2 Minute Arabic — a 30–60 s bonus clip outside the 30-day course (e.g. "10 ways to say hello", "10 ways to say goodbye", slang, dialect vs. standard, sketches), with x0N- file names and the ARABIC EXTRAS badge. Use this whenever the user mentions extras, bonus videos, "10 ways to say…", dialect/Syrian/Levantine phrases, a sketch, or sends a recording that isn't a numbered day.
---

# Arabic Extras

Bonus Shorts between the daily lessons: quick, fun, shareable — more reach for the channel without breaking the
course. They reuse the whole daily pipeline (see the **produce-day** skill); only the differences are here.

## What's different from a day

- **Stem** `videos/x0N-<slug>.md` (x01, x02, …). `assemble.py` shows the badge **ARABIC EXTRAS** for any stem
  starting with `x`, instead of "DAY N".
- **Length 30–75 s** (a 10-phrase list lands around 1:05–1:10; Shorts allow up to 3 min, but keep it tight). Short hook in the first 2 s ("10 ways to say hello in Arabic — number 7 is what Syrians
  really say"). Keep the hello clip only if it doesn't eat the hook; always end with the goodbye clip + subscribe
  line.
- **Dialect is allowed here — and only here.** The course stays Modern Standard Arabic (fusha). In Extras every
  phrase card is labelled: `Standard Arabic` or `Syrian dialect` (e.g. a small tag line on the card), so nobody
  confuses the two. Syrian lines are written the way they're said (e.g. `كِيفَكْ`, `مْنْشُوفَكْ بَعْدَيْن`), with
  tashkeel where it helps pronunciation, and the transliteration reflects the dialect (kiifak, mnshuufak ba'dein).
- **No English repeat** after each Arabic line; one short narrator line of context per phrase (when to use it,
  formal or casual), all in full sentences.
- **All Arabic is the owner's recording.** One sheet, one take, split with `tools/split_recording.py` as usual.
  If one recording covers several Extras (e.g. 20 lines for hello + goodbye), split it once against a combined
  sheet (like `_345-combined`) and point each video's `map.json` at the lines it uses.
- **Upload**: title `<hook> | Arabic Extras`; playlist **Arabic Extras** (create it once); related video = Day 1;
  tags: video-specific (e.g. "how to say hello in arabic", "syrian arabic") + niche + broad; AI use as usual (No).
  Hand over with the **upload-handover** skill. Schedule Extras between days, never instead of a day.

## Sketch Extras (later)

Short scenes with the owner on camera (filmed, cleaned with `tools/clean_footage.py`), Arabic lines subtitled with
transliteration + English. Real people on camera also strengthen the channel against the inauthentic-content rule.
