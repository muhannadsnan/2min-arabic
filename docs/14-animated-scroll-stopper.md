# 14 — Animated scroll-stopper (test, 2026-09-30)

**Question:** can the owner's laptop (RTX 3060 Laptop, 6 GB graphics memory, 16 GB RAM) turn the first scene image of
a Short into a ~3-second moving clip, using only free models that are allowed on a monetized channel?

**Short answer: yes.** Wan 2.2 TI2V-5B (Apache 2.0) animated Sami waving in the Damascus alley. A 3-second clip
takes **about 10 minutes at the recommended 576×1024** (6–7 minutes at 480×832), and the face, hands and flat vector
style hold together. One of the four test clips broke in its last half second, so every clip still needs a quick look
before use. "Sami **saying** the hook with moving lips" is **not** possible with AI on this laptop yet: the
licence-clean talking models are far too big for it. A clean cartoon-style alternative is proposed in section 6.

## 1. Licences (checked 2026-09-30 on the official model cards / LICENSE files)

Rule: code **and** weights must allow commercial use on a monetized channel, with no revenue share, no revenue cap
that could matter, no forced credit or "made with AI" labels, and nothing non-commercial hidden inside.

| Model / tool | Licence | Commercial OK? | Link |
|---|---|---|---|
| **Wan 2.2 TI2V-5B** (image/text → video) — **chosen** | Apache 2.0 (code + weights) | ✅ Yes, no conditions beyond Apache | [model card](https://huggingface.co/Wan-AI/Wan2.2-TI2V-5B) · [code LICENSE](https://github.com/Wan-Video/Wan2.2/blob/main/LICENSE.txt) |
| ↳ ComfyUI repackaged VAE `wan2.2_vae.safetensors` (Comfy-Org) | Apache 2.0 | ✅ Yes | [Comfy-Org/Wan_2.2_ComfyUI_Repackaged](https://huggingface.co/Comfy-Org/Wan_2.2_ComfyUI_Repackaged) |
| ↳ GGUF quantisation `Wan2.2-TI2V-5B-Q5_K_M.gguf` (uploader **QuantStack**, base model tagged Wan-AI/Wan2.2-TI2V-5B) | Apache 2.0 | ✅ Yes | [QuantStack/Wan2.2-TI2V-5B-GGUF](https://huggingface.co/QuantStack/Wan2.2-TI2V-5B-GGUF) |
| ↳ Text encoder `umt5-xxl-encoder-Q5_K_M.gguf` (uploader **city96**, Google UMT5-XXL) | Apache 2.0 | ✅ Yes | [city96/umt5-xxl-encoder-gguf](https://huggingface.co/city96/umt5-xxl-encoder-gguf) |
| ↳ ComfyUI-GGUF node (city96) | Apache 2.0 | ✅ Yes | local `custom_nodes/ComfyUI-GGUF/LICENSE` |
| ↳ ComfyUI itself | GPL-3.0 (covers the program, not the videos you make) | ✅ Yes | local `ComfyUI/LICENSE` |
| Wan 2.1 T2V-1.3B | Apache 2.0 | ✅ Yes (not needed: 5B fits and is better) | [model card](https://huggingface.co/Wan-AI/Wan2.1-T2V-1.3B) · [code LICENSE](https://github.com/Wan-Video/Wan2.1/blob/main/LICENSE.txt) |
| Wan 2.1 Fun 1.3B InP (image → video, Alibaba PAI) | Apache 2.0 | ✅ Yes (backup option) | [model card](https://huggingface.co/alibaba-pai/Wan2.1-Fun-1.3B-InP) · [VideoX-Fun LICENSE](https://github.com/aigc-apps/VideoX-Fun/blob/main/LICENSE) |
| LTX-Video 0.9.6–0.9.8 | "LTXV Open Weights License 0.X" | ⚠️ Conditional → **rejected** | [LICENSE](https://huggingface.co/Lightricks/LTX-Video/blob/main/LTX-Video-Open-Weights-License-0.X.txt) |
| LTX-2 | "LTX-2 Community License Agreement" | ⚠️ Conditional → **rejected** | [LICENSE](https://huggingface.co/Lightricks/LTX-2/blob/main/LICENSE) |
| **Talking / lip-sync:** Wan 2.2 S2V-14B (speech → video) | Apache 2.0; its audio encoder wav2vec2-large-xlsr-53-english is Apache 2.0 | ✅ Licence clean, ❌ too big for this laptop | [model card](https://huggingface.co/Wan-AI/Wan2.2-S2V-14B) · [audio encoder](https://huggingface.co/jonatasgrosman/wav2vec2-large-xlsr-53-english) |
| InfiniteTalk / MultiTalk (MeiGen, on Wan 2.1 I2V-14B + chinese-wav2vec2-base, MIT) | Apache 2.0 | ✅ Licence clean, ❌ too big (14B base) | [InfiniteTalk](https://github.com/MeiGen-AI/InfiniteTalk) · [chinese-wav2vec2-base](https://huggingface.co/TencentGameMate/chinese-wav2vec2-base) |
| MuseTalk | Code MIT, weights "any purpose, even commercially" — **but** it needs the face-parsing model trained on CelebAMask-HQ, a dataset that is non-commercial only | ⚠️ Unclear → **rejected** | [MuseTalk](https://github.com/TMElyralab/MuseTalk) · [face-parsing](https://github.com/zllrunning/face-parsing.PyTorch) · [CelebAMask-HQ terms](https://github.com/switchablenorms/CelebAMask-HQ) |
| LatentSync (ByteDance) | Apache 2.0, but uses InsightFace for face detection | ❌ No (InsightFace models are non-commercial) | [LatentSync](https://github.com/bytedance/LatentSync) |
| LivePortrait | Code MIT, but "the models of InsightFace are for non-commercial research purposes only" | ❌ No as shipped (and it is video-driven, not audio-driven) | [LICENSE](https://github.com/KwaiVGI/LivePortrait/blob/main/LICENSE) |
| ReActor (already installed in ComfyUI) | uses InsightFace | ❌ No — do not use | — |
| **Rhubarb Lip Sync** (classic 2D mouth shapes from audio, not AI video) | MIT; all bundled parts BSD/MIT/Boost | ✅ Yes | [LICENSE.md](https://github.com/DanielSWolf/rhubarb-lip-sync/blob/master/LICENSE.md) |

**Why LTX is rejected even though small channels may use it:** both LTX licences are free only below **US $10 million
annual revenue** (fine for us today), but they add strings Apache 2.0 does not have: Attachment A forbids publishing
output "without expressly and intelligibly disclaiming that the … content is machine generated" (a forced AI label on
every video), Lightricks may "restrict (remotely or otherwise)" use and asks you to keep updating to the latest
version, and any redistribution must carry the whole agreement. That is exactly the kind of trap we avoid. Wan is
simpler and better anyway.

## 2. What was run

- ComfyUI 0.22.0 (`--lowvram --use-split-cross-attention`), native Wan 2.2 5B template nodes
  (`Wan22ImageToVideoLatent`, `ModelSamplingSD3` shift 8, KSampler uni_pc/simple, 20 steps, CFG 5) with GGUF loaders.
- Model: **Wan 2.2 TI2V-5B, GGUF Q5_K_M** · text encoder **UMT5-XXL GGUF Q5_K_M** · Wan 2.2 VAE.
- Input: `images/x01-10-ways-to-say-hello/s01.png` (Sami waving in a Damascus alley).
- Output: **73 frames at 24 fps = 3.0 s**, then upscaled/cropped to 1080×1920 at 30 fps with ffmpeg for the preview.

| Clip | Resolution | Prompt | Time per clip | GPU memory (peak) | Lowest free RAM · swap | Result |
|---|---|---|---|---|---|---|
| v1 | 480×832 | wave + jasmine + "subtle push-in" (seed 1) | **6.8 min** (5.0 min sampling, 15 s/step; first run incl. loading) | 5.8 of 6 GB | 2.5 GB · ~13 GB swapped | ✅ good |
| v2 | 480×832 | stronger: "waves several times, nods, **leans toward the camera**" (seed 2) | **6.2 min** | 5.8 GB | 1.3 GB · ~11 GB | ⚠️ first 2.4 s good, then a sudden zoom into a broken face |
| v3 | 704×1280 (the model's native size) | same as v1 (seed 1) | **19.1 min** (47 s/step) | 5.8 GB | 1.1 GB · ~19 GB | ✅ sharpest, but face drifts a little at the end |
| v4 | **576×1024** | "waves side to side … camera stays steady, very slight push-in" (seed 3) | **10.4 min** (25 s/step) | 5.8 GB | 1.3 GB · ~13 GB | ✅ **best overall** |

All clips: 73 frames, 24 fps, 3.0 s. At 576×1024 and 704×1280 the final decoding step ran out of graphics memory once
and ComfyUI automatically retried in tiles (costs a little extra time, no action needed).

"Swap" = the laptop pushed memory out to disk. RAM (not the graphics card) is the tight spot: with Chrome, VS Code
and WhatsApp open, only 1–2.5 GB stayed free and the system swapped several GB during each run. Nothing crashed, and the
animation step itself always fit, because ComfyUI streams the model from RAM and the card stayed at ~5.8 GB.

## 3. Disk used

- New model files (under `/media/msn/GamesLinux/AI/ComfyUI/models/`): **9.4 GB**
  - `unet/Wan2.2-TI2V-5B-Q5_K_M.gguf` 3.8 GB
  - `text_encoders/umt5-xxl-encoder-Q5_K_M.gguf` 4.1 GB
  - `vae/wan2.2_vae.safetensors` 1.4 GB
- Test outputs: 15 MB (4 clips + 4 upscaled previews + 4 contact sheets + the two small scripts) in `output/scroll-stopper-test/` (plus a copy of each raw clip in ComfyUI's own `output/video/`).

## 4. Quality verdict (checked on contact sheets, frame strips and close-ups of face and hand)

- **Style:** stays flat vector, same colours, same alley, balconies and jasmine in every clip. No drift into 3D or
  photo look. ✅
- **Face:** Sami stays recognisable with the same beard, curls and smile in v1, v3 and v4. In v3 the face gets a bit
  longer and thinner in the last half second as the camera pushes in. ✅ (small drift)
- **Hands:** five fingers, no melting. During fast waves the hand is soft or smeared for a frame or two, which reads as
  normal motion blur when played. ✅
- **Motion:** v1 and v4 show a real, repeated side-to-side wave; the jasmine and vines barely move. v3 is more of a hand
  held up plus a clear camera push-in. The movement is gentle rather than dramatic; it is enough to show the image is a
  video, not a big "wow". ⚠️
- **Failure seen:** v2's "leans toward the camera" turned into a hard zoom in the last 0.5 s, with a darker face, a
  wrong mouth and a magenta blob. Camera or lean words that are too strong break it. ❌ So each clip must be checked
  before it is used (Claude does this), and one in two or three tries may need a re-roll with a new seed.
- **Sharpness:** 480×832 upscaled to 1080×1920 is slightly soft but fine on a phone; 576×1024 is clearly cleaner;
  704×1280 is crispest but takes 3× longer than 480.

**Verdict: good enough to use** for the opening of a Short, with the settings below and a quick look at every clip.
It is a gentle living-picture effect (wave, smile, breeze, slow push-in), not lip-sync.
Clips to watch: `output/scroll-stopper-test/v4_576x1024_73f_seed3_1080x1920.mp4` (best) and `v1_…_1080x1920.mp4`.

## 5. Recommended pipeline

1. **Model:** Wan 2.2 TI2V-5B GGUF Q5_K_M + UMT5-XXL GGUF Q5_K_M + Wan 2.2 VAE (already installed).
2. **Settings:** 576×1024, 73 frames at 24 fps (3.0 s), 20 steps, CFG 5, shift 8, sampler uni_pc / simple. Start
   ComfyUI with the usual `--lowvram --use-split-cross-attention`.
   Script: `python3 output/scroll-stopper-test/animate.py images/<video>/s01.png out.mp4 --prompt "…" --width 576 --height 1024 --seed N`,
   then `output/scroll-stopper-test/finish.sh out.mp4` for the 1080×1920 version and the 6-frame contact sheet.
3. **Prompt recipe:** "2D cartoon animation of *(who, what he wears)* in *(place)*. He *(one simple action: waves side to
   side / raises his cup / nods and smiles)*. *(one small background movement)*. The camera stays steady with a very
   slight slow push-in. Flat vector illustration style, clean simple shapes, warm pastel colors." Avoid "leans toward
   the camera", "zoom", "walks toward", several actions at once, and anything "talking".
4. **Two seeds per video**, Claude picks the better one from the contact sheets (and checks the last frames for a
   sudden zoom).
5. **Time added per video:** about **20 minutes of laptop time** (2 × ~10 min), unattended; **0 minutes for the owner**.
   Quick mode: 480×832 at ~6 min per clip (~12 min for two). Close Chrome/other big apps while it runs: RAM is the
   tight spot and the laptop swaps several GB per clip.
6. **Assembly (next step, not built yet):** `assemble.py` should accept `images/<video>/s01.mp4`: upscale to
   1080×1920 at 30 fps, play the 3 s clip, then hold its last frame (with the usual slow zoom) for the rest of scene 1.
   The first frame of the clip is the original image, so the thumbnail still matches. Keep the text card on top as now.
7. **YouTube:** Apache 2.0 needs no credit and no label. YouTube's "altered or synthetic content" question is about
   realistic-looking content, and a cartoon wave isn't realistic, so the channel's current rule stays as it is.

## 6. Next steps for "Sami says the hook" (lip-sync)

There is **no licence-clean lip-sync model that runs on this laptop today.**

- **Wan 2.2 S2V-14B** (Apache 2.0, audio encoder Apache 2.0) is the clean AI option: it makes a character speak from an
  audio file. But its smallest GGUF is 9.5 GB (Q2_K) and a usable one is 11–15 GB, bigger than the 6 GB graphics card
  and more than the RAM that is usually free. It might run very slowly with heavy swapping, or not at all. It becomes
  realistic with **32 GB RAM** (a cheap laptop upgrade, if the slots allow) or a 12–16 GB graphics card.
- **InfiniteTalk / MultiTalk** (Apache 2.0) are the same size class (14B), so they don't fit either.
- **MuseTalk** is rejected because it depends on a face-parsing model trained on a non-commercial dataset. **LatentSync,
  LivePortrait and ReActor** are rejected because they use InsightFace (non-commercial). They are also built for
  real human faces, not flat cartoons.
- **Recommended next test (clean, cheap, fits our style):** classic cartoon lip-sync. **Rhubarb Lip Sync** (MIT) reads
  the owner's real Arabic recording ("phonetic" mode works for any language) and outputs which mouth shape to show when.
  Claude makes 6–9 mouth drawings of Sami once (FLUX.2 klein edits of his face, checked), and ffmpeg swaps them over
  the still image in time with the voice. Then the Wan clip can do the wave, and the talking happens on the still
  after it (or on a v4-style clip where the head barely moves). Cost: ~1 hour to set up once, then seconds per video.
- Check again in a few months for a small (≤5B) Apache-licensed speech-to-video model; this area moves fast.

---

# Round 2 — 3D look, three "entrances", a reusable opener library (2026-09-30)

**Owner feedback on round 1:** only a "humble animation"; the v3 ending looked creepy (the face drifted); he expected
something closer to 3D animation; v4 was the best but he was still unsure. He wants a small library of reusable,
loopable openers, refreshed about once a month.

**What changed:** the keyframe (the still the animation starts from) is now made in a **3D animated-movie look**, and
it is built so that the animation *completes an action* (peeking → stepping out, cup → reveal, writing → looking up),
instead of a character who is already waving. Same laptop, same Wan 2.2 TI2V-5B, and no new downloads.

## R2.1 Keyframes (FLUX.2 klein 4B, Apache 2.0, already installed)

`tools/images/generate.py --no-style --ref assets/characters/<sami|lina>.png` with the style *"3D animated movie
style, soft cinematic lighting, expressive stylized characters, Pixar-like but original, rich depth, vertical 9:16, the
scene fills the whole frame, no text…"*. 3 takes each, about 30 s per image. Prompts: `output/scroll-stopper-test/round2/keyframes.json`.

| Entrance | Takes | Picked | Notes |
|---|---|---|---|
| A — Sami peeks from behind a Damascus stone wall | 3 + 3 retry | `A2_sami_peek_1.png` | The first prompt showed his whole face, so I made the half-hidden retry. Great 3D look; the character refs carry over well (curls, beard, hoodie). |
| B — Sami lowers a coffee cup | 3 + 3 retry | `B2_sami_cup_0.png` | The first try had the cup too low, "steam from the beard" in 2 takes and fake sign lettering in 1. The retry covers mouth and beard as asked. |
| C — Lina at a café table, writing | 3 | `C_lina_notebook_1.png` | Clean on the first try; hands and pen correct, no text. |

The 3D keyframes look much richer than the flat-vector scenes. They are the part the owner will like most.

## R2.2 Animation runs (576×1024, 20 steps, 2 seeds per entrance + 1 extra for B)

| Clip | Frames | Time | Verdict |
|---|---|---|---|
| C seed 11 | 73 (3 s) | 10.9 min | Good: looks up, smiles, waves. In the last 0.5 s the mouth goes into an "ooh" shape as if talking. |
| **C seed 12** | **49 (2 s)** | **6.0 min** | ✅ **Chosen.** Looks up at 0.75 s, warm closed-mouth smile, 5-finger wave, face steady to the last frame. |
| A seed 11 | 73 | 10.3 min | Good step-out, but from ~2 s one eye half-closes (a lopsided "wink"), which is face drift. Rejected. |
| **A seed 12** | **49** | **6.2 min** | ✅ **Chosen, the best clip of both rounds.** Hidden → steps out → big grin → big clear 5-finger wave. The face is stable, and there's one natural blink. |
| **B seed 11** | **73** | **11.3 min** | ⚠️ **Chosen, but weakest.** The cup comes down toward the camera and the face is revealed with a surprised stare, then a big grin. The invented mouth area has a thin, painted-on moustache that looks a bit odd. |
| B seed 12 | 49 | 7.3 min | ❌ Creepy: the beard grows into a black blob over the mouth, the eyes go huge, and the cup glows. Rejected. |
| B seed 13 | 73 | 10.5 min | ❌ Asked for a "thick mustache" and got a giant cartoon handlebar moustache plus an unblinking stare. Rejected. |

Graphics memory peaked at 5.8 of 6 GB every time. RAM stayed the tight spot: the 73-frame runs pushed 11–19 GB through
swap, while the **49-frame runs mostly didn't** (0.7–1.8 GB, except B-12 at 13 GB) and took **~6 minutes instead of ~11**.

**What we learned**
- **49 frames (2 s) is the sweet spot.** Both 2-second clips of A and C finished the whole action *and* kept the face;
  the 3-second versions drifted in their last second (the same problem as round 1's v3).
- **Reveals are risky.** Anything the keyframe hides (Sami's mouth behind the cup) has to be *invented* by the model,
  and that's where identity breaks. The peek works because half his face and his beard are already visible.
- The 3D look animates **better** than flat vector: the motion is bigger and more "movie-like", and it's no longer a
  humble animation.

## R2.3 The opener library

`output/scroll-stopper-test/library/openers/` (made by `round2/make_opener.sh CLIP NAME [start] [end]`):

| Opener | Plays once (1080×1920, 30 fps) | Loop (ping-pong) | Contact sheet |
|---|---|---|---|
| `sami-peek-door` | 2.0 s | 4.0 s | `sami-peek-door_sheet.png` |
| `lina-notebook-lookup` | 2.0 s | 4.0 s | `lina-notebook-lookup_sheet.png` |
| `sami-coffee-reveal` (use with care) | 3.0 s | 6.0 s | `sami-coffee-reveal_sheet.png` |

The **loop** plays the entrance forward and then backward (he steps out and waves, then steps back behind the wall),
which joins seamlessly. It suits looping backgrounds (e.g. behind a title card). For a Short's opening, use the
**play-once** version, then cut to (or freeze on) its last frame.
Frame-blending up to 30 fps made a ghosted double hand during the wave, so the 30 fps versions repeat frames instead.

**Would a viewer find it creepy?**
- `sami-peek-door`: **no**. It reads as a playful Pixar-style hello, and it is the one I'd lead with.
- `lina-notebook-lookup`: **no**. Calm and friendly, though her eyes look slightly past the camera rather than straight into it.
- `sami-coffee-reveal`: **a little**. The stare plus the thin moustache sit close to the uncanny line. Fine as a
  comedic "surprise" beat, but I wouldn't make it the channel's signature opener.

**Consistency with the videos:** the openers are 3D while the lesson scenes are flat vector. Either accept the
contrast (the opener becomes a recognisable "intro sting"), or switch the scene images to the 3D style too. Klein
does it in the same ~15–30 s per image, but it is a channel-look decision for the owner.

**Time per library clip:** ~6 min per 2-second clip, so 2 seeds + review ≈ **15 minutes of laptop time per opener**.
A monthly refresh of 3–5 openers is about **1–1.5 hours of unattended laptop time**, plus 2–3 min of keyframes.

**Extra disk (round 2):** about **100 MB** (keyframes 30 MB, clips 2.5 MB, library 19 MB, strips/scripts, plus copies
in ComfyUI's `output/`). No new models.

## R2.4 Research: can the bigger Wan 2.2 A14B image-to-video run here? (nothing downloaded)

| Part | Licence | Size | Link |
|---|---|---|---|
| Wan 2.2 I2V-A14B (two 14B "experts": high-noise + low-noise) | Apache 2.0 | — | [model card](https://huggingface.co/Wan-AI/Wan2.2-I2V-A14B) |
| GGUF quantisations (uploader QuantStack) | Apache 2.0 | per expert: Q3_K_S 6.5 GB · Q3_K_M 7.2 GB · Q4_K_S 8.8 GB · Q4_K_M 9.7 GB | [QuantStack/Wan2.2-I2V-A14B-GGUF](https://huggingface.co/QuantStack/Wan2.2-I2V-A14B-GGUF) |
| 4-step distill LoRAs, lightx2v "Wan2.2-Distill-Loras" (I2V, rank 64) | Apache 2.0 | 0.63 + 0.74 GB | [lightx2v/Wan2.2-Distill-Loras](https://huggingface.co/lightx2v/Wan2.2-Distill-Loras) |
| or lightx2v "Wan2.2-Lightning" I2V 4-step LoRA (also repackaged by Comfy-Org) | Apache 2.0 | 2 × 1.23 GB | [lightx2v/Wan2.2-Lightning](https://huggingface.co/lightx2v/Wan2.2-Lightning) |
| Wan 2.1 VAE (A14B uses it) | Apache 2.0 | 0.25 GB | Comfy-Org repackaged |
| Text encoder | same UMT5 GGUF we already have | 0 | — |

**All licence-clean.** A trial set (Q3_K_M ×2 + distill LoRAs + VAE) is about **16 GB of disk**.

**Would it run?** Probably yes, slowly and on the edge:
- Graphics memory isn't the blocker. ComfyUI streams the weights (as it already does for the 5B model at 5.8 GB).
- **RAM is.** One Q3_K_M expert (7.2 GB) must sit in RAM while it works, and ComfyUI swaps to the other expert half-way.
  With Chrome, VS Code and WhatsApp open, only ~1–4 GB is free, so the system would thrash the 16 GB swapfile (already
  ~12 GB used during our runs). **Close the browser and other apps**, and it should fit at Q3_K_M. Q4 is too big for 16 GB RAM.
- More swap (a second 16 GB swapfile on the NVMe) only prevents crashes; it doesn't make it faster. The real fix is
  **32 GB RAM**.
- **Rough time per clip** (my estimate from the 5B timings scaled by model size and video length, not measured): with the
  4-step LoRA and no CFG, **~10–15 min for a 3-second 480×832 clip**, ~6–8 min for 2 seconds. It could easily double
  if the laptop swaps heavily. The 4-step LoRA's own card warns about artifacts with very large motion.
- **Is it worth it?** A14B is the model with clearly better motion, faces and hands, the step up toward "real 3D animation".
  But it runs at 480p (upscaled), it is uncertain on 16 GB RAM, and it costs 16 GB of disk. I'd try it **after** the
  cheaper fix below, or right away if the owner adds RAM.

**Other licence-clean routes to better, drift-free motion on this PC**
1. **Wan 2.2 Fun 5B InP (first + last frame).** Apache 2.0, and it is the same 5B size we already run (GGUF Q5_K_M
   3.8 GB, QuantStack, Apache 2.0). We give it a **start** keyframe *and* an **end** keyframe (both made with klein,
   e.g. Sami hidden → Sami waving with *his* face), and it animates between them. The end frame pins the face, which
   directly fixes the late drift and the invented-face problem of the coffee reveal. **Recommended next test**
   (one 3.8 GB download, same ~6–10 min per clip).
2. **A 4-step LoRA for our 5B model** is listed as "todo" by lightx2v but not released yet. When it lands, today's
   ~6-minute clip would drop to ~1–2 minutes.
3. **Real 3D (Blender, GPL; the renders are yours).** Truly drift-free and perfectly loopable, but it needs rigged 3D
   models of Sami and Lina. That's days of modelling or a commissioned artist, so it is out of scope for now.
   AI 3D-model generators are not clean for us: **Hunyuan3D 2**'s licence "does not apply in the European Union, United
   Kingdom and South Korea", and **TRELLIS** needs a 16 GB GPU and pulls in non-commercial rasterizers (nvdiffrast,
   Inria's gaussian rasterizer).

## R2.5 Recommendation

- **Use now:** `sami-peek-door` (lead opener) and `lina-notebook-lookup`. Keep `sami-coffee-reveal` only as a spare
  comedic beat.
- **Settings for new openers:** 3D klein keyframe that starts *mid-action*, 576×1024, **49 frames**, 20 steps,
  2 seeds, "static camera", one simple action, and no hidden faces to reveal.
- **Next test:** Wan 2.2 Fun 5B InP with first + last keyframes (3.8 GB), then A14B + 4-step LoRA if RAM is upgraded.
- **Owner decision:** keep 3D openers with flat-vector lessons (an "intro sting") or move the whole channel to the 3D look?
