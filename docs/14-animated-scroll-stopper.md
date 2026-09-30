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
