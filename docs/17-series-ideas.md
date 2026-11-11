# 17 — Series ideas (owner's backlog, newest additions at the bottom)

The 30-day course is the core. These are the next series. Each gets a template (one skill or a section in
arabic-extras) so episodes are cheap to repeat. Pick by niche research (`youtube_api.py niche`) + our own analytics.

| # | Series | Shape | Length | Notes / evidence |
|---|---|---|---|---|
| 1 | **Arabic letters** (absolute basics) | one letter per episode: shapes (start/middle/end), sound, 3 course words, "find the letter" game; then **harakat** (fatha, kasra, damma, sukun, shadda, tanween) and **special letters** (hamza forms, madda, taa marbuta, alif maqsura) | Short | niche: "Learn Arabic Letter Ta (ت)" 1.4 M · fills a real gap (we only show transliteration) · **owner: start soon** |
| 2 | **Q&A picture games** | "What do we call this?" — animals, objects, fruits & vegetables, colours, family members, country flags (flags: careful — politics/old Syrian flag rule, docs/06) | Short | board style; reuses recorded words; easy "quests" |
| 3 | **Pure Arabic conversations** | 2+ characters, whole scene in Arabic with subtitles: café, school, cooking & diet, health, shopping… | 1–30 min (Short teaser + long video) | comprehensible input, like successful Spanish channels; long-form watch time for monetization |
| 4 | **Situation sentences** | 5 or 10 easy sentences for one situation; words and specific letters highlighted in colour | Short | beginner+ level; colour-coding needs a card upgrade |
| 5 | **Words → explained → story** | a few words introduced, explained, then used in a story; can use a fully cartoony style for variation | Short + longer cut of the same words | niche: "Learn Arabic Through a Short Story" Short 2.06 M |
| 6 | **Curiosity words** | "The Arabic word for X is fascinating" shape | Short | niche: 420 k–1.1 M |
| 7 | **Numbers in life** (Month 3) | the counting ladder (tens, 21–99, hundreds, thousands) + numbers in subjects: phone, time, prices, weights, height, distance, weather, years, the Arab world / the body in numbers | Short + 1–100 long + Episode 3 | owner 2026-11-09 · plan: docs/23-month-3-numbers.md · searches "arabic numbers 1 to 100 / 1 to 20 / 1 to 50" |
| 8 | **Top N word lists** (owner 2026-11-11) | "Top 10 / 20 / 50 / 100 X in Arabic": food, jobs (v05 = Top 20), animals, countries, cities, fruits, colours, body, family, verbs, everyday words… — N fits the subject. One picture per word (pencil style), the owner's recording names them one by one | Top 10–20 = Short (≤ 3 min); Top 50–100 = a long video (watch hours) + Shorts cut from it | searches (suggest.py 11 Nov): "100 arabic words / for everyday life / basic / common", "50 arabic words", "animals in arabic (and english)", "countries in arabic", "fruits in arabic" · proven: Colors + Food (v03/v04) |
| … | *(more to come from the owner)* | | | |

## How series run together (owner approved 2026-10-15)

Finish the 30-day course first (it's the channel's promise; Days 16–30 ≈ 2 weeks). Meanwhile the **Extra slot**
alternates: letters ↔ other Extras. After Day 30: a weekday rhythm, e.g. Mon/Wed/Fri course "Month 2", Tue/Thu
letters, Sat story/conversation, Sun Vocab/Q&A game — one Short per day, one long video per week (Part or conversation).

## Idea bank from real searches (YouTube autocomplete, 2026-11-11 — owner: "more ideas people search for")

Each line = the search phrases that exist → the video. Check `tools/suggest.py` again before producing (searches move).

**Words people look up ("X in Arabic")**
- "animals in arabic (and english / name)" → Top 20 animals (clean animals only: no dogs/pigs)
- "fruits in arabic (and english)" / "vegetables" → Top 15 fruits · Top 15 vegetables
- "countries in arabic", "arab countries name" → the 22 Arab countries in Arabic (map style) · Top 20 world countries
- "arabic food names (and pictures)", "arabic dishes" → Top 20 Arab dishes (dolma, falafel, hummus…, real dishes)
- "100 arabic words / for everyday life / basic / common", "arabic words for daily use" → the long "100 everyday words" video
- "50 arabic words", "most common arabic words", "50 arabic phrases" → long video + Shorts
- "arabic numbers 1 to 100 / 100 to 200" → Month 3 numbers (docs/23)

**"How to say … in Arabic" (one Short each — the classic search shape)**
- "how to say I love you / how are you / what is your name / thank you in arabic" → one-question Shorts (some re-use recordings)
- "arabic love words (and meanings)", "arabic romantic words" → 10 sweet words (habibi, hayati, ya albi…) — clean, family-friendly

**Situations (travel = big intent)**
- "arabic phrases for travel / for tourists / basic arabic for travel", "arabic for travelers" → a "Travel Arabic" set: airport, taxi, hotel, restaurant, shop, emergency (Short each + a long compilation)
- "arabic phrases for conversation", "arabic greetings and responses" → greeting + the right answer pairs

**Curiosity / comparison (Instagram-style surprise)**
- "arabic words in english" (sugar, coffee, algebra, cotton…) → "10 English words that are secretly Arabic" (very shareable)
- "arabic words in spanish" → Spanish words from Arabic (ojalá = inshallah!) — perfect for the Spanish test audience
- "arabic vs persian / hebrew / turkish" → "Arabic vs Turkish: same word?" (Turkish audience is strong)
- "arabic words that just make sense" → words whose logic is beautiful (e.g. the root k-t-b: kitaab, maktab, kaatib)

**Dialect + slang (label clearly as dialect)**
- "arabic slang (words / phrases)", "egyptian arabic slang" → 10 Syrian slang words · "yalla, khalas, wallah…" (the "What does X mean?" series)
- "arabic name meaning (in urdu / for girls)", "islamic names meaning" → "What your Arabic name means" (Muhammad, Fatima, Noor, Amir…) — huge in Urdu/Hindi/Indonesian

**Learning formats**
- "learn arabic through (short) stories / stories and reading texts" → the monthly Story + its Shorts (proven)
- "arabic alphabet (for beginners / pronunciation)" → the letters series (docs/17 #1)
- "arabic 101 common mistakes" → "5 mistakes every beginner makes" (wrong vs right)

**Avoid even though searched:** insults / swear words (brand + policy), songs / nasheeds / kids' songs (not our audience, and music rights).

**Dialects (owner 2026-11-11: "add Egyptian slang + the top-3 searched nationalities")** — `youtube_api.py niche`, last 365 days:
- **Egyptian:** "egyptian arabic slang / lessons / for beginners"; top Shorts 24k–50k ("POV: you went to Egypt to learn Arabic…", "Egyptian vs Moroccan"), a 9-min "10 essential Egyptian words before your trip" 15k.
- **Moroccan (Darija):** the biggest: "NEVER say this in Morocco…" 1.1 M, "Why is Moroccan Arabic so hard?" 741k, "Darija words that sound Spanish" 403k.
- **Gulf / Saudi:** "Hindi to Arabic · daily use words in Saudi" 361k, "Hotel Arabic words for Gulf travelers" 186k, "2 everyday Gulf phrases" 293k — the Indian/Pakistani worker audience = our Hindi/Urdu trial audience.
- (Lebanese/Levantine close behind — our own Syrian dialect, already in the "What Syrians say" Extras.)
→ Format: **"Same thing, 4 dialects"** — one everyday phrase (how are you / I want / what's up / no problem / now) in Syria · Egypt · Morocco · Gulf, + the standard Arabic; and "10 Egyptian slang words". Every dialect word is checked with a native source before recording (the owner is Syrian; mark anything he isn't sure of).

**"What your Arabic name means" — one video = 10 names** on a theme (boys' names · girls' names · names of prophets · names from nature · names with "Abd"), each name: the Arabic, the root meaning, one picture. Single-name Shorts only later, for a name that a themed video shows people search for.

**"Your language is full of Arabic words" (owner 2026-11-12: "hindi words from arabic, pakistani words from arabic…")**
— one edition per language, 10 everyday words the viewer already says that are Arabic (with the Arabic, the meaning, a
picture). Evidence (niche, 365 days): Hindi Short "अरब का यह शब्द कैसे हमारा शब्द हो गया" 2.28 M · "Word differences
between Arabic & Urdu & Persian & Turkic" 993k · "Plural forms in Arabic and Turkish" 2.0 M · "Common dishes Arabic and
Turkish" 1.77 M; searches "arabic words in urdu / hindi / turkish / persian / spanish / swahili", "urdu and arabic
similar words". Editions, by our audience strength:
1. **Hindi & Urdu** (kitaab, waqt, duniya, khabar, sabr, qalam, insaan, mausam, shukriya, zaroor…) — English video + Hindi and Urdu trials
2. **Turkish** (kitap, kalem, saat, dünya, merhaba, insan, sabır…) · 3. **Indonesian / Malay** (kitab, waktu, dunia, ilmu, kursi, hadir, selamat…)
4. **Spanish** (ojalá, aceite, azúcar, almohada, ojalá, hasta, aldea…) · 5. **Swahili** (kitabu, saa, habari, dunia, salama…) · 6. Persian · 7. English (sugar, coffee, algebra, cotton…)
Each edition goes out on YouTube (English narration, the language in the title + translations) AND as an Instagram trial
narrated in that language — the viewer hears his own words. Every word is checked (real Arabic origin, everyday use).
