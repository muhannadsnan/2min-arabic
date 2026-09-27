# 07 — Channel Setup Strategy & Monetization

Findings and decisions about accounts, the two-channel structure and getting paid.
Researched September 2026 — YouTube changes its rules often, so re-check the official pages before acting.

## Decisions at a glance

| Question | Decision |
|---|---|
| Which Google account? | **mnd.senan@gmail.com** — both channels live under it |
| New channel or reuse a stale one? | **New channels.** Leave the two stale channels alone. |
| One channel for both languages, or two? | **Two separate channels:** 2 Minute Arabic and 2 Minute Spanish |
| Getting paid from two channels | **One AdSense account** linked to both channels; one combined payment, revenue visible per channel |
| Voice | Your own recordings + your cloned voice + free local open-source TTS (Chatterbox MIT, Kokoro Apache 2.0) — no paid service ([03-production-pipeline.md](03-production-pipeline.md#1-voice)) |

---

## 1. Using mnd.senan@gmail.com

One Google account can own **several YouTube channels**. Each new one is created as a *brand account* channel
(YouTube does this automatically when you create an additional channel), with its own name, handle, icon,
subscribers and analytics. The two stale channels don't affect the new ones.

Before creating the channels, check:

- [ ] **No strikes or terminations** on the two stale channels (YouTube Studio → each channel → *Settings → Channel →
  Feature eligibility* and the Community Guidelines status). A terminated channel on the same account can block
  creating or monetizing new channels. If one has a strike, let it expire first.
- [ ] **2-Step Verification** is turned on for the Google account — required for monetization, and important with
  several channels on one account.
- [ ] You're **18+** and in a country where the YouTube Partner Program is available (needed for AdSense).

**Don't repurpose a stale channel.** Its old subscribers came for other content; they won't watch Arabic lessons,
and their silence tells YouTube "this channel's audience doesn't like these videos". A fresh channel lets the
algorithm learn the right audience from the first upload.

## 2. Two channels on one account — do they conflict for monetization?

No. How it works:

- **Each channel qualifies separately** for the YouTube Partner Program (its own subscribers and watch hours).
  2 Minute Arabic being monetized doesn't make 2 Minute Spanish monetized, and vice versa.
- A person can have **only one AdSense account**. When each channel is accepted into YPP, you **link it to the same
  AdSense account** — that's the normal, allowed setup.
- **Payment:** AdSense pays you **one combined monthly payment** for all linked channels (once the balance passes
  the payment threshold, e.g. $100 in many countries). You can't receive two separate payouts, but you **see each
  channel's revenue separately** in YouTube Studio → Analytics → Revenue, and in AdSense reports.
- **Shared risk:** because both channels hang off the same Google account and AdSense account, a serious policy
  problem (e.g. an AdSense suspension for invalid traffic) can affect both. Never buy views/subscribers, never
  ask people to click ads — the normal rules, but they matter double here.

## 3. One combined channel or two?

**Two channels.** Reasons:

1. **The algorithm matches videos to audiences per channel.** An Arabic learner who subscribes and then gets a
   Spanish lesson doesn't click → YouTube sees low click-through and short watch time → it shows *both* kinds of
   videos to fewer people. Mixed channels grow slower, not faster.
2. **Subscribers subscribe to a promise.** "2 Minute Arabic — first conversation in 30 days" is a clear promise.
   "2 Minute Arabic *and* Spanish" is two half-promises; people who want only one language skip it.
3. **The Day N streak breaks.** Two interleaved Day 1…30 series on one channel is confusing.
4. **Different host positions:** native teacher on Arabic, "fellow learner two years ahead" on Spanish — each is a
   clean story on its own channel.
5. **Clean monetization and analytics** — each channel's numbers tell you what works for *that* audience.

Get the "shared growth" benefit through **cross-promotion** instead:
- Day 1 of each channel tells the same founder story and mentions the sister channel.
- A pinned comment / channel description link to the other channel.
- Channel page → *Related channels / Featured channels* section shows the other one.
- Occasional community post: "Learning Spanish too? My sister channel…"

## 4. Monetization thresholds (as of September 2026)

Official source: [YouTube Partner Program overview](https://support.google.com/youtube/answer/72851) and the
[YouTube blog announcement of the 2027 changes](https://blog.youtube/news-and-events/youtube-partner-program-updates-2027-new-opportunities-earn/).

| Level | Requirements | Unlocks |
|---|---|---|
| **Early access (fan funding)** | 500 subscribers + 3 public uploads in 90 days + (3,000 watch hours in 12 months **or** 3M Shorts views in 90 days) | Memberships, Super Thanks/Chat/Stickers, Shopping — **no ad revenue** |
| **Full YPP — until Jan 31, 2027** | 1,000 subscribers + (4,000 watch hours in 12 months **or** 10M Shorts views in 90 days) | Ad revenue |
| **Full YPP — from Feb 1, 2027** | 1,000 subscribers + (**8,000** watch hours in 365 days **or** **20M** Shorts views in 90 days) | Ad revenue |
| **Shorts ad revenue — from Feb 1, 2027** | also **10M Shorts views in the last 90 days**, otherwise the channel earns on long-form only | Shorts ad share |

Plus for all: follow the monetization policies, 2-Step Verification, linked AdSense account.
Channels already in YPP before Feb 1, 2027 keep their status. The fan-funding tier is unchanged.

### What this means for our strategy

- Realistically, new channels starting now will apply **under the 2027 rules**: 1,000 subs + 8,000 watch hours.
- **Watch hours come from long-form videos, not Shorts.** Shorts bring discovery and subscribers; long-form brings
  the hours. So we publish **both**:
  - **Daily:** the 2-minute lesson as a vertical Short (discovery, streak).
  - **Weekly:** a **long-form compilation** (all 7 days back to back, ~15 min, 16:9) — that's what earns watch hours.
  - **Later:** a monthly "full 30 days in one video" (~1 hour) — people who want to binge or review will watch it
    for a long time, which is the best possible thing for watch hours.
- The **500-subscriber fan-funding tier** is a realistic first milestone: channel memberships
  (e.g. PDF worksheets, early access) can earn before ad revenue does.

## Staying monetizable: "inauthentic content" policy

Since July 2025, YouTube's monetization policy targets **"inauthentic content"**: mass-produced, repetitive,
template-based videos, e.g. slideshows with synthetic narration and little original value. **Our format looks like
that from the outside** (fixed template, AI images, AI voice), so we design against it on purpose:

| Risk | What we do |
|---|---|
| "Same video over and over" | Every video teaches **different, original** content in a real curriculum; five formats rotate. |
| "No human behind it" | A **real host with a real story** (Day 1), a consistent personality, and the host's **own voice** on as many videos as possible — the single strongest signal. |
| "Low effort slideshow" | Speak-out-loud pauses, role-play, quizzes, recurring characters — actual teaching design. |
| "Bulk uploads" | One video a day, scheduled — never dozens at once. |
| Reused content | All scripts, images and audio are made for this channel. No clips from other channels. |

Using AI voices and AI images is **allowed** — the policy is about low-value mass production, not the tools.

## AI disclosure label

When uploading, YouTube asks whether the video contains **"altered or synthetic content"**. That label is for
**realistic** content that could mislead (e.g. a real person saying something they never said, a fake real event).
Our illustrated characters and a generic AI narrator voice are **not** in that category, so normally the answer is
**No**. If you ever clone a real person's voice or make photorealistic scenes of real people, answer **Yes**.
Re-read the upload screen's help text when in doubt; the rules evolve.
