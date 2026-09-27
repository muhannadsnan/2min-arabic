# Day 1 — Upload sheet

**File to upload:** `footage/day01/day 1 - final with captions.mp4` (2:25, vertical ≤ 3 min → published as a **Short**;
sound fixed to −14 LUFS; captions burned into the picture)
**Thumbnail/cover:** `footage/day01/day 1 - thumbnail (vertical).jpg` (16:9 version: `day 1 - thumbnail (16x9).jpg`)
**Captions file:** not needed for this video — the captions are already in the picture (a CC track on top would double them).

## Title

```
Don't Make This Mistake When Learning Arabic | Day 1 · 2 Minute Arabic
```

## Description

```
Day 1 of 30 — why I teach Arabic in just 2 minutes a day (and the mistake I made learning Spanish).

Two minutes a day. Your first Arabic conversation in 30 days.
1.01^365 ≈ 38 — get 1% better every day and you're 38 times better after a year. Small things, done daily, compound.

📝 Today's Arabic:
مرحبا — marhaba — hello
مع السلامة — ma'a as-salaama — goodbye

▶️ Tomorrow: the most useful Arabic phrases.
🔔 Subscribe so you don't break your streak.

#learnarabic #arabicforbeginners #2minutearabic
```

## Tags

```
learn arabic, arabic for beginners, arabic lesson, speak arabic, arabic phrases, modern standard arabic, fusha, arabic conversation, 2 minute arabic, how to learn a language, language learning motivation
```

## Settings

| Setting | Value |
|---|---|
| Playlist | create **"30 Days to Your First Arabic Conversation"** and add this video |
| Audience | No, it's not made for kids |
| Altered or synthetic content | **No** (it's you, filmed for real) |
| Category | Education |
| Video language / caption language | English |
| Comments | On |
| Visibility | Schedule (see below) |

## Cover (Short thumbnail)

Use `day 1 - thumbnail (vertical).jpg` if the upload screen offers a custom thumbnail. If it only lets you pick a frame
(Shorts on mobile), pick the one at **0:03** — it's the frame the thumbnail was made from.

## More settings (as answered)

| Setting | Value |
|---|---|
| Caption certification | None |
| Recording date / location | leave empty (privacy) |
| License | Standard YouTube License |
| Allow embedding | ✅ |
| Publish to subscriptions feed and notify subscribers | ✅ |
| Automatic chapters | ✅ (harmless) |
| Featured places | ❌ off |
| Automatic concepts | ❌ off |

## Pinned comment

```
Day 1 ✅ — write مرحبا (or marhaba) below to start your streak! Which language did YOU learn the wrong way? 😅
```

## After publishing

- Studio → **Customization → Home tab → Channel trailer** (for people who haven't subscribed) → this video.
- Reply to the first comments within the first hour (in English + a bit of Arabic).

---

## Q&A from the Day 1 upload (2026-09-27)

**Is this a Short? Is that the point?**
Yes. Vertical + under 3 minutes → YouTube makes it a Short automatically. Shorts are for **reach**: they're shown to
people who don't know the channel yet → new subscribers. Watch hours for monetization come later from the weekly
long-form compilations (see [07](../docs/07-channel-and-monetization.md#what-this-means-for-our-strategy)).

**Did the sound need fixing? (recorded with Jabra Elite 8 earbuds in the ear)**
The earbuds didn't record anything: the audio came from the phone's two built-in mics (two different channels, full
high frequencies — a Bluetooth earbud mic would cut those). The recording was clean (very low background noise) but
**too quiet (−25 LUFS)** and **5 dB louder on one side**. Fixed: cleaner mic as centered mono, low-cut, light compression,
**−14 LUFS**, safe peaks. Next time: phone's stereo recording off (or one mic), stand a bit closer; earbuds not needed.

**The fixed file had no sound when I played it.**
The file has sound (checked: full decode, speech all the way through, −14 LUFS). The player was the problem — VS Code's
built-in video preview often plays MP4 without sound (no AAC decoder), or an old copy was still open. Use VLC/Shotcut.
A 10-second test clip is in the footage folder: `sound-check (10 s).wav`.

**Can the captions be burned into the video?**
Yes — done: `day 1 - final with captions.mp4`. Big bold one-line captions on the chest area; Arabic words on their own
line in Arabic script + transliteration, in yellow. Because the captions are in the picture, **don't upload the `.srt`**
for this video (CC would show them twice). Tool for next videos: `tools/captions/srt_to_burnin_ass.py`.

**Thumbnail — now or later?**
Now. Made from a **real frame (0:03)**, not AI: `day 1 - thumbnail (vertical).jpg` (Short / channel grid) and
`day 1 - thumbnail (16x9).jpg` (search / compilations). If the upload screen only allows picking a frame, pick 0:03.

**AI use question ("Was AI used to generate or edit your content…")?**
**No.** It's you, filmed for real. The label is only for realistic fakes (a real person saying things they didn't,
altered real events, realistic scenes that never happened). Later videos with illustrated Sami/Lina, a generic AI voice
or your **own** cloned voice are also **No**.

**Automatic chapters / featured places / automatic concepts?**
Chapters **on** (harmless; useful for long compilations). Featured places **off** (no places in the videos).
Automatic concepts **off** (experimental; would add things to your description automatically).

**Video language, caption certification, recording date/location, license, embedding, notify subscribers?**
English · None (only for TV broadcasts) · leave empty (privacy) · Standard YouTube License · embedding on · notify on.

**Title wording?**
"Don't *Do* This Mistake" sounds off in English → use
`Don't Make This Mistake When Learning Arabic | Day 1 · 2 Minute Arabic`.
Also: a file renamed to the title got a hidden line break before `.mp4` — avoid `|` and line breaks in file names.

**I already uploaded the old version — how do I update it?**
YouTube can't replace the file of an existing upload (the Studio editor only trims/blurs/adds music). Delete and
re-upload — no loss while it has no views:
1. Studio → **Content** → hover the old video → **⋮ → Delete forever** → confirm.
2. **Create → Upload videos** → `day 1 - final with captions.mp4`.
3. Fill everything from this sheet (title, description, tags, playlist, audience, AI use = No, thumbnail, settings).
4. No captions file. 5. Schedule or publish.
If the old link was shared anywhere (or set as trailer / in a playlist), update it — the new upload has a new link.
