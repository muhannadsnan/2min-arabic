# 15 — Tag research (YouTube autocomplete, newest on top)

Source: `python3 tools/suggest.py "<seed>"` — YouTube's own search suggestions, most-searched first. Only learner
phrases are used; dropped: songs, kids, Quran-specific, Malayalam/Urdu/Hindi/Tamil course variants, kalolsavam,
other dialects (Egyptian/Moroccan) unless the video teaches them, everyday-life Arabic searches by native speakers.

## 2026-10-05

| Topic | Good suggestions (used) |
|---|---|
| learn arabic | learn arabic language · learn arabic conversation |
| arabic for beginners | arabic for beginners conversation · arabic for beginners course |
| arabic phrases | arabic phrases for travel · arabic phrases for tourists · arabic phrases with english translation · arabic phrases to know · arabic phrases levantine |
| greetings | arabic greetings and responses · arabic greetings and self introduction · hello in arabic pronunciation |
| goodbye | goodbye in arabic language |
| yes / no | yes no in arabic · yes in arabic pronunciation |
| sorry | how to say i'm sorry in arabic · how to say excuse me in arabic |
| conversation | arabic conversation with english subtitles · arabic conversation msa |
| story | arabic story learning |
| pronouns | arabic pronouns for beginners · arabic pronouns in english · pronouns arabic grammar |
| countries | countries in arabic language · countries and nationalities in arabic |
| **Day 9 (ة)** | masculine and feminine in arabic · male and female in arabic · how to identify masculine and feminine in arabic |
| **Day 10 (numbers)** | numbers 1 to 10 in arabic · number names 1 to 10 in arabic · arabic numbers 1 to 10 in english |
| Arabic script | تعلم العربية من الصفر · تعلم العربية الفصحى · العربية لغير الناطقين بها · المحادثة العربية لغير الناطقين بها · تعليم اللغة العربية لغير الناطقين بها · تعليم عربي للاجانب |

## 2026-10-06 — x03 (introduce yourself) + x04 (Arabic digits)

`suggest.py` picks (learner phrases only):
- x03: "introduce yourself in arabic", "how to introduce yourself in arabic", "introduce myself in arabic",
  "tell me about yourself in arabic", "my name is in arabic", "how to say my name is in arabic",
  "what's your name in arabic"; Arabic: "تعريف عن النفس بالعربية".
- x04: "arabic numbers", "arabic numbers 1-10", "arabic numerals 1-10", "how to read arabic numbers",
  "how to read arabic eastern numbers", "eastern arabic numerals", "how to write arabic numbers 1 to 10";
  Arabic: "الارقام العربية". Dropped: "arabic numerals" alone (memes/politics), kids' songs ("للاطفال").
