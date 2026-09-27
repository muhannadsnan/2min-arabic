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
| ⏸️ **Pause Ns** — … | Silence (N seconds, usually the viewer speaks). `make_audio.py` inserts it automatically — keep the exact form `⏸️ **Pause 2s**`. |
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

## Image quality control (Claude does this — the owner has no time to check details)

Nothing may look "AI-generated". Every image is checked by Claude **before** it reaches the video.

**Process per scene:** generate **3 takes** (different seeds) → Claude inspects each at full resolution →
keeps the best one that passes **every** check below → if none passes, rewrite the prompt and try again
(up to 3 rounds) → only if it still fails, flag it to the owner with the best candidate.

**Reject an image if it has:**
- any **text, letters or numbers** — including clock/stopwatch numerals, book pages with writing, signs, screens,
  labels, logos (all real text comes from our text cards);
- **wrong hands or bodies**: extra/missing/merged fingers, twisted wrists, extra limbs, broken perspective;
- **face problems**: asymmetry, odd eyes/teeth, melted features;
- **duplicated or impossible objects**: two cups when one was asked for, floating things, a cup fused with a hand;
- **cropped key objects** (the thing the scene is about cut off at the edge);
- **character mismatch**: Sami/Lina not matching their reference sheet (hair, beard, clothes, skin tone);
- **cultural mismatch**: generic/Western-looking people when the scene is Arab; odd clothing for the setting;
- anything that breaks the **flat illustration style** (photo-like textures, 3D render look, busy background);
- nothing calm at the **top ~15% / bottom ~25%** (text and YouTube buttons go there).

**Prompt rules that prevent problems** (learned in testing):
- Clocks/stopwatches: always *"completely blank white face, no numbers, no markings, one short hand"* —
  the model writes wrong numerals (e.g. 15 instead of 11). The "2:00" is added by us as a text card.
- Notebooks/books: *"blank empty pages"*. Phones/laptops: *"blank screen"* or seen from behind.
- People: say **"olive skin"** and the character details every time; for Sami/Lina always pass the reference image.
- Hands: prefer simple poses (holding a cup, waving with an open palm, hands on a table); avoid pointing fingers and
  hands holding small objects.
- One subject per scene, max two people; simple backgrounds; *"all objects fully inside the frame"*.

## Recurring characters

Generate one reference sheet per character first, then reuse it for consistency.

**Sami (سَامِي)** — male, mid-20s, university student, loves coffee, a bit clumsy, kind.
> `character reference sheet, young Arab man in his mid-20s, short curly black hair, short neat beard, warm smile, olive-green hoodie, beige trousers, white sneakers, front view, side view, three-quarter view, several facial expressions (happy, sad, surprised), plain cream background, flat vector illustration, warm pastel palette, no text`

**Lina (لِينَا)** — female, mid-20s, cheerful and confident, works in a bookshop, always has two coffees.
> `character reference sheet, young Arab woman in her mid-20s, shoulder-length wavy dark brown hair, bright friendly eyes, mustard-yellow cardigan over white shirt, blue jeans, tote bag, front view, side view, three-quarter view, several facial expressions (happy, laughing, curious), plain cream background, flat vector illustration, warm pastel palette, no text`

**The host** — never shown as a face (keeps it simple and lets any viewer project themselves).
Represented by the stopwatch icon, desk/notebook scenes, or hands.
