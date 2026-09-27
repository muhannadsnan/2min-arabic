# 03 — Production Pipeline

From a script in `videos/` to a published video, using free tools.

```
script (.md) ──► voice clips (TTS) ──┐
             └─► scene images (AI) ──┼─► editor (timeline + on-screen text + pauses) ──► export ──► YouTube
                                      └─ music (optional, royalty-free)
```

---

## 1. Voice

### Recommended: Microsoft Edge TTS (free, unlimited, runs on Linux)

Neural voices, very good Arabic, no account needed. This repo includes a script that reads
every `say:` block in a video file and produces numbered MP3 clips.

```bash
cd 2min-arabic
python3 -m venv .venv && source .venv/bin/activate
pip install -r tools/requirements.txt

python tools/make_audio.py videos/001-why-2-minutes.md     # one video
python tools/make_audio.py videos/*.md                     # all videos
```

Output: `audio/001-why-2-minutes/01-narrator.mp3`, `02-narrator.mp3`, `03-teacher.mp3`, …
plus a `cues.txt` listing what each clip says. Drop them onto the timeline in number order.

Voice cast (edit `SPEAKERS` in [tools/make_audio.py](../tools/make_audio.py) to change):

| Speaker tag | Voice | Used for |
|---|---|---|
| `narrator` | `en-US-AndrewNeural` | All English narration (the host) |
| `teacher` | `ar-SA-HamedNeural` (rate −10%) | Arabic words/phrases in lessons |
| `teacher-slow` | `ar-SA-HamedNeural` (rate −35%) | Slow "say it with me" repetitions |
| `sami` | `ar-SY-LaithNeural` (rate −10%) | Sami's lines in conversations/stories |
| `lina` | `ar-SA-ZariyahNeural` (rate −10%) | Lina's lines |

To hear alternatives: `edge-tts --list-voices | grep ^ar-` (there are 30+ Arabic voices), then test with
`edge-tts --voice ar-EG-SalmaNeural --text "مَرْحَبًا" --write-media test.mp3`.

No script? Paste each `say:` block into any Edge "Read aloud" style web front-end manually — the blocks are
designed to be copy-paste units.

> ⚠️ **Licensing:** `edge-tts` uses Microsoft's Read-Aloud service unofficially. It's fine for starting out,
> but its terms for **monetized** content are unclear. Before the channel is monetized, consider one of the
> options below for anything commercial.

### Alternatives

| Option | Cost | Arabic | Notes |
|---|---|---|---|
| **Your own voice** (Arabic lines) | Free | Native ✅ | **Strongest option long-term.** You're a native speaker — that's authenticity no AI has, and it's 100% yours legally. Phone + quiet room (closet with clothes) + Audacity noise reduction is enough. |
| **Google AI Studio – Gemini TTS** | Free tier | Good | Web UI, can voice a **two-speaker dialogue in one go** (great for conversation videos). Check current usage terms. |
| **ElevenLabs** | Free tier (~10k characters/month) | Very good | Best quality. The free plan requires attribution and does not include a commercial license — check current terms; paid tier needed once monetized. |

A good hybrid: AI English narrator + **your own Arabic** lines.

---

## 2. Images

One image per scene; prompts are in each script under **🖼️ Image**.

- Use whichever generator you like (local ComfyUI / Stable Diffusion / Flux, Leonardo, Bing Image Creator,
  Ideogram…).
- Every prompt ends with **`+ STYLE`** — replace it with the **shared style suffix** from the
  [style guide](05-style-guide.md#visual-style) (or save the suffix once as a template/style preset in your
  generator) so the whole channel looks consistent.
- **Never ask the image model to write Arabic text.** Image models garble Arabic letters. All text is added
  in the editor.
- Keep Sami and Lina consistent: generate a **character reference sheet** once (prompts in the style guide),
  then use image-to-image / IP-Adapter / "reference image" features for every scene they appear in.
- Leave the **top ~15% and bottom ~25%** of each vertical image calm (sky, wall, table) — that's where
  the on-screen text and YouTube's UI go.

---

## 3. Editing

| Editor | Platform | Why |
|---|---|---|
| **Kdenlive** | Linux (native), free | Solid, open source, good title tool |
| **DaVinci Resolve** | Linux/Win/Mac, free | Pro-grade; steeper learning curve |
| **CapCut** | Web / Win / Mac | Fastest for Shorts, auto-captions (not native on Linux; use the web version) |

Assembly per video:

1. **Project:** 1080×1920 (9:16), 30 fps.
2. **Audio track:** clips in number order. Add the gaps marked **⏸️ Pause** (silence of the given length;
   optionally a soft "tick" sound so viewers know it's their turn).
3. **Image track:** each scene's image under its clips. Add a slow zoom (Ken Burns, ~105%) so still images feel alive.
4. **Text track:** the **🔤 On screen** lines.
   - Arabic font with good **tashkeel** support: **Noto Naskh Arabic** or **Amiri** (both free, Google Fonts).
     Headline font for English: **Poppins** or **Montserrat**.
   - Layout: Arabic big (top), transliteration medium (middle, italic), English small (bottom).
   - Check the harakat render correctly — some editor/font combos drop them. Test once at project start.
5. **Brand:** the 2:00 stopwatch icon in the top corner; a "Day N" badge.
6. **Music (optional):** very quiet (−25 dB) lo-fi bed from the YouTube Audio Library (free, safe for monetization).
   Duck it under speech.
7. **Captions:** burn in the on-screen text; additionally upload an `.srt` with the English narration for accessibility.

Save the first finished project as a **template** (intro clip, outro clip, badges, text styles already placed).
Every following video is then: swap clips, swap images, edit text.

---

## 4. Export

| Setting | Value |
|---|---|
| Resolution | 1080×1920 (vertical) |
| Codec | H.264, high profile |
| Bitrate | 10–16 Mbps |
| Audio | AAC 48 kHz, 192 kbps, loudness ≈ −14 LUFS |
| Length | ≤ 2:59 (Shorts eligible) |

Optional: also export a **16:9 version** (1920×1080 with the vertical video centered on a branded background)
for the channel's long-form tab and for weekly compilations ("Week 1 — all 7 days in 14 minutes").

---

## 5. Per-video checklist

- [ ] Audio clips generated and listened to once (TTS sometimes misreads — fix the tashkeel and regenerate)
- [ ] Every scene has an image
- [ ] Every Arabic line is on screen with tashkeel + transliteration + English
- [ ] All ⏸️ pauses inserted
- [ ] Length between 1:45 and 2:15 (never over 2:59)
- [ ] Title, description, tags copied from the script header
- [ ] Thumbnail / Shorts cover frame ready
- [ ] Status updated in the README table
