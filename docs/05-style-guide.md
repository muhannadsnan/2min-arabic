# 05 — Style Guide

## Script markup

Every video script uses the same building blocks, so it can be read by a human **and** by
[tools/make_audio.py](../tools/make_audio.py).

| Markup | Meaning |
|---|---|
| `### 🎬 Scene N — Name · 0:00–0:05` | A scene. Timing is an estimate. |
| 🖼️ **Image:** … | Prompt for the image shown during the scene. |
| 🔤 **On screen:** … | Text to add in the editor. |
| ` ```say:<speaker> ` … ` ``` ` | A voice clip. One block = one audio file. Speakers: `narrator`, `teacher`, `teacher-slow`, `sami`, `lina`. |
| ⏸️ **Pause Ns** — … | Silence to insert in the editor (usually the viewer speaks). |
| ✂️ **Edit:** … | Other editing instructions (sound effect, zoom, reuse a clip…). |

Rules:
- Only text meant to be **spoken** goes inside `say:` blocks. No stage directions inside them.
- One language per block. Never mix Arabic and English in the same block (TTS voices handle one language well).
- Reusing a line? Write the block again anyway — the tool generates it again, which keeps clip order simple.

## Arabic conventions

- **Variety:** simple Modern Standard Arabic, spoken style (see [concept](01-channel-concept.md#which-arabic)).
- **Tashkeel (vowel marks):** always full tashkeel in `say:` blocks and on screen. It helps TTS pronounce
  correctly and helps learners read.
- **No case ending on the last word of a phrase** (pausal form, as people actually speak):
  write كَيْفَ حَالُك not كَيْفَ حَالُكَ; مَا اسْمُك not مَا اسْمُكَ. Inside a phrase, keep the vowels needed for flow
  (e.g. وَعَلَيْكُمُ السَّلَام).
- If TTS mispronounces a word: first check the tashkeel, then try adding/removing the shadda or a sukun,
  then try another voice.

### Transliteration (simple, learner-friendly)

We deliberately avoid academic symbols. The audio is the real guide; transliteration is just a crutch.

| Arabic | Written as | Example |
|---|---|---|
| long vowels ا / ي / و | aa / ii / uu | *salaam, ismii, shukran* |
| ع | ' (apostrophe) | *'afwan, 'alaykum* |
| ح | h | *haaluk* |
| خ | kh | *bikhayr* |
| غ | gh | *mughlaq* |
| ش | sh | *shukran* |
| ث / ذ | th / dh | *haadhaa* |
| ق | q | *qahwa* |
| definite article with sun letter | assimilated | *as-salaam, ash-shaay* |

Words and names inside English narration are written in plain English ("Sami", "Lina").

## Visual style

**Shared style suffix** — in the scripts, every image prompt ends with `+ STYLE`; replace that with:

> `flat vector illustration, warm pastel palette (sand, terracotta, teal, cream), soft shadows, clean simple shapes, friendly, vertical 9:16 composition, calm empty area at top and bottom for text, no text, no letters, no watermark`

Negative prompt (if your generator supports it):

> `text, letters, writing, calligraphy, watermark, logo, extra fingers, distorted face, photorealistic, dark, gloomy`

Recurring visual elements:
- **2:00 stopwatch** icon — top corner of every video (make it once, as a PNG).
- **Day N badge** — small rounded label under the stopwatch.
- On-screen text colors: Arabic in dark teal `#1F5F5B`, transliteration in terracotta `#C0633A`, English in charcoal `#333333`,
  on a cream `#FFF6E9` rounded box.

## Recurring characters

Generate one reference sheet per character first, then reuse it for consistency.

**Sami (سَامِي)** — male, mid-20s, university student, loves coffee, a bit clumsy, kind.
> `character reference sheet, young Arab man in his mid-20s, short curly black hair, short neat beard, warm smile, olive-green hoodie, beige trousers, white sneakers, front view, side view, three-quarter view, several facial expressions (happy, sad, surprised), plain cream background, flat vector illustration, warm pastel palette, no text`

**Lina (لِينَا)** — female, mid-20s, cheerful and confident, works in a bookshop, always has two coffees.
> `character reference sheet, young Arab woman in her mid-20s, shoulder-length wavy dark brown hair, bright friendly eyes, mustard-yellow cardigan over white shirt, blue jeans, tote bag, front view, side view, three-quarter view, several facial expressions (happy, laughing, curious), plain cream background, flat vector illustration, warm pastel palette, no text`

**The host** — never shown as a face (keeps it simple and lets any viewer project themselves).
Represented by the stopwatch icon, desk/notebook scenes, or hands.
