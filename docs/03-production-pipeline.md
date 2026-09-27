# 03 — Production Pipeline

From a script in `videos/` to a published video.

```
script (.md) ──► make_audio.py (Azure TTS) ──► voiceover.wav + timeline.md + captions.srt ──┐
             └─► scene images (AI image generator) ─────────────────────────────────────────┼─► Shotcut ──► export ──► YouTube
                                                    music (optional, YouTube Audio Library) ─┘
```

---

## 1. Voice

### Decision: Azure AI Speech, paid "Standard (S0)" tier

We only use voices whose license **clearly allows commercial / monetized use**:

| Option | Commercial use | Verdict |
|---|---|---|
| Edge TTS (`edge-tts`, free) | ❌ Not granted — unofficial use of Microsoft's Read-Aloud service | **Not used for published videos.** |
| Azure Speech **Free (F0)** tier | ❌ Microsoft's Product Terms grant output rights "for customers of the **paid tier** TTS Service only" | Not used. |
| Azure Speech **Standard (S0)** tier | ✅ "Customer may use the audio output of prebuilt neural voices … including for commercial purposes" | **Chosen.** |
| Your own voice | ✅ 100% yours | **Best of all** — see below. |

Why Azure S0:
- **Same neural voices** as the drafts you already reviewed (Hamed, Laith, Zariyah, Andrew) — what you approved is what you get.
- **Cheap:** ~$16 per 1 million characters. One video ≈ 2,500 characters ≈ **$0.04**.
  A daily video on both channels (~60 videos/month) ≈ **$2.50/month**.
- No royalties, no attribution required, when the input text is your own content.

> ⚠️ Azure pricing and terms can change — glance at the [pricing page](https://azure.microsoft.com/en-us/pricing/details/speech/)
> and the Product Terms once a year. Set a **budget alert** (e.g. $5/month) in the Azure portal so there are never surprises.

### Your own voice (strongly recommended, at least partly)

You're a native Arabic speaker. Recording **your own voice** — especially the Day 1 story and the Arabic lines — is:
- the most **authentic** thing the channel can have (viewers trust a real teacher);
- the strongest protection against YouTube's **"inauthentic content"** policy for monetization
  (template videos with only AI narration are exactly what that policy targets — see [07-channel-and-monetization.md](07-channel-and-monetization.md#staying-monetizable-inauthentic-content-policy));
- free, and legally 100% yours.

A phone, a quiet room (a closet full of clothes is a great vocal booth) and Audacity's noise reduction are enough.
A realistic plan: AI voices now → your own voice for the story/intro videos → your own voice for everything once the routine is set.

### Setting up Azure (once, ~10 minutes)

1. Create a Microsoft Azure account at [portal.azure.com](https://portal.azure.com) (needs a payment card).
2. **Create a resource → "Speech"** (Azure AI Speech). Pick a region near you (e.g. `westeurope`),
   pricing tier **Standard S0** (not Free F0).
3. Open the resource → **Keys and Endpoint** → copy **KEY 1** and the **Location/Region**.
4. Add them to your shell (e.g. in `~/.bashrc`):
   ```bash
   export AZURE_SPEECH_KEY="paste-key-1-here"
   export AZURE_SPEECH_REGION="westeurope"
   ```
5. **Cost Management → Budgets** → create a $5/month budget with an email alert.

Never commit the key to git.

### Generating the audio

Requirements: Python 3 and ffmpeg (`sudo apt install ffmpeg`). No Python packages needed.

```bash
python3 tools/make_audio.py videos/001-why-2-minutes.md     # one video
python3 tools/make_audio.py videos/*.md                     # all videos
```

Output in `audio/001-why-2-minutes/` (the `audio/` folder is git-ignored):

| File | Use |
|---|---|
| `voiceover.wav` | **The full voiceover, already assembled** — every clip in order, 0.35 s between clips, and every ⏸️ pause inserted. Put it on the timeline at 0:00. |
| `timeline.md` | The start time of **every scene** and every clip — place the scene images at these times. |
| `captions.srt` | Every spoken line with timings — upload to YouTube as subtitles. |
| `clips/NN-speaker.mp3` | Single clips, if you want to move or replace one by hand. |

Clips are cached (`audio/.cache`), so after fixing one line only that line is re-generated (and paid for).

Voice cast (edit `SPEAKERS` at the top of [tools/make_audio.py](../tools/make_audio.py) to change):

| Speaker tag | Voice | Used for |
|---|---|---|
| `narrator` | `en-US-AndrewNeural` | All English narration (the host) |
| `teacher` | `ar-SA-HamedNeural` (rate −10%) | Arabic words/phrases in lessons |
| `teacher-slow` | `ar-SA-HamedNeural` (rate −35%) | Slow "say it with me" repetitions |
| `sami` | `ar-SY-LaithNeural` (rate −10%) | Sami's lines |
| `lina` | `ar-SA-ZariyahNeural` (rate −10%) | Lina's lines |

Replacing a clip with your own recording: record the line, export it as MP3, and use it in place of that clip on
the timeline (or replace `clips/NN-…mp3` and re-assemble by hand).

---

## 2. Images

One image per scene; prompts are in each script under **🖼️ Image**.

- Use whichever generator you like (local ComfyUI / Stable Diffusion / Flux, Leonardo, Bing Image Creator, Ideogram…).
  **Check its license allows commercial use** of the images, same rule as the voices.
- Every prompt ends with **`+ STYLE`** — replace it with the **shared style suffix** from the
  [style guide](05-style-guide.md#visual-style) (or save the suffix once as a template/style preset in your
  generator) so the whole channel looks consistent.
- **Never ask the image model to write Arabic text.** Image models garble Arabic letters. All text is added in Shotcut.
- Keep Sami and Lina consistent: generate a **character reference sheet** once (prompts in the style guide),
  then use image-to-image / IP-Adapter / "reference image" features for every scene they appear in.
- Generate at **1080×1920** (or any 9:16 size) and leave the **top ~15% and bottom ~25%** calm — that's where
  on-screen text and YouTube's buttons go.
- Name files by scene: `s01.png`, `s02.png`, `s04-1.png` … so they drop onto the timeline in order.

---

## 3. Editing in Shotcut

### One-time project template

1. **Settings → Video Mode → Vertical HD 30 fps** (1080×1920).
2. Install the fonts (system-wide, then restart Shotcut): **Noto Naskh Arabic** or **Amiri** for Arabic (full tashkeel
   support), **Poppins** or **Montserrat** for English. All free on Google Fonts.
3. Build Day 1 fully, then **File → Save As** `template.mlt` with: the stopwatch icon and "Day N" badge on the top
   video track, the text styles set up, the music track in place.
   Every next video: open the template, **Save As** the new day, swap the voiceover, images and texts.

### Per video

1. **Audio:** drag `voiceover.wav` onto an audio track at **0:00**. Everything is already in order with pauses —
   no clip-by-clip work.
2. **Markers (optional, handy):** open `timeline.md`, and add a marker at each **🎬 scene** time
   (Timeline menu → Markers) so you can snap images to them.
3. **Images:** drag the scene images onto video track V1 and trim each one to end where the next scene starts.
4. **Slow zoom ("Ken Burns"):** on each image add the **Size, Position & Rotate** filter with two keyframes
   (100% at start → ~105% at end). Copy/paste the filter between images.
5. **On-screen text:** add a **Text: Rich** filter on a transparent/color clip on the track above the images,
   and paste the 🔤 **On screen** text from the script. Layout: Arabic big (top), transliteration medium (italic),
   English small (bottom). Use **Text: Rich** for anything Arabic — it handles right-to-left and harakat.
   ⚠️ Check once, zoomed in, that the harakat (ـَ ـُ ـِ ـّ ـْ) render correctly with your font.
6. **Pauses:** during each ⏸️ pause, show a small "🗣️ Your turn!" label (part of the template) so viewers know to speak.
7. **Music (optional):** a quiet track from the YouTube Audio Library (free and safe for monetized videos) on a second
   audio track, **Gain/Volume filter ≈ −25 dB** so the voice stays clear.
8. **Loudness:** add the **Normalize: Two Pass** filter to the Output track (target ≈ −14 LUFS).

About subtitles: Shotcut can import `captions.srt` (Subtitles panel) and burn it in, but its burn-in can lose the
right-to-left order of Arabic lines. **Don't burn in Arabic subtitles** — use Text: Rich for Arabic, and upload
`captions.srt` to YouTube as a separate subtitle file instead (YouTube renders Arabic correctly).

---

## 4. Export (Shotcut → Export)

| Setting | Value |
|---|---|
| Preset | **YouTube** (H.264 + AAC) — resolution follows the project (1080×1920) |
| Frame rate | 30 fps |
| Length | ≤ 2:59 (Shorts eligible) |
| Loudness | ≈ −14 LUFS (Normalize filter above) |

**Weekly long-form version:** every 7 days, make a **16:9 (Settings → Video Mode → HD 1080p 30 fps)** project,
put the week's 7 vertical videos in a row over a branded background, export, upload as a normal video.
This matters for monetization — see [07-channel-and-monetization.md](07-channel-and-monetization.md#what-this-means-for-our-strategy).

---

## 5. Per-video checklist

- [ ] `make_audio.py` run; voiceover listened to once (TTS sometimes misreads — fix the tashkeel and re-run)
- [ ] Every scene has an image, placed at the times in `timeline.md`
- [ ] Every Arabic line is on screen with tashkeel + transliteration + English (Text: Rich)
- [ ] "Your turn" label shown during every ⏸️ pause
- [ ] Length between 1:45 and 2:20 (never over 2:59)
- [ ] Exported with the YouTube preset, 1080×1920
- [ ] Title, description, pinned comment copied from the script; `captions.srt` uploaded as subtitles
- [ ] Status updated in the README table
