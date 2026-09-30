---
name: channel-review
description: Weekly channel review for 2 Minute Arabic from numbers or screenshots the owner pastes from YouTube Studio (no API, no OAuth) — views, viewed vs swiped away, retention curves, impressions and CTR, subscribers per video, which titles/hooks/tags worked, comments turned into video ideas, the "viral shorts" tag experiment and the 48-hour rule for Shorts with no views — ending in a short report and concrete next actions. Use this whenever the user shares Studio screenshots or analytics, pastes comments, asks how the channel or a video is doing, why a Short has no views, what to change, for the weekly check-in, or on/after 2026-10-06 for the tag experiment, even if they don't say "review".
---

# Weekly channel review

The channel is new and the numbers are tiny. The job is to find **hints**, act on the few that are clear, and never
pretend small numbers prove something. There is no API. Everything comes from what the owner pastes or screenshots.

## 0. Pull the numbers yourself first (API, connected 2026-09-30)

```
Y=~/.local/share/2min-yt/venv/bin/python
$Y tools/youtube_api.py videos · stats --days 7 · retention <id> · search-terms · comments
```
Analytics lag ~2 days. If it says the login expired (Testing mode: every 7 days), run `login` and send the owner
the printed link (pick **2 Minute Arabic** in the brand-account list). Ask for screenshots **only** for what the API
doesn't give: Shorts "viewed vs swiped away" and "shown in feed".

## 1. Ask for exactly this (only what the API can't give)

Send the list, phone-friendly:
1. Studio → **Content → Shorts** (and **Videos** for Parts): the list with views and dates. One screenshot.
2. For each video from the last 7 days → **Analytics → Engagement**: **viewed vs swiped away**, **audience retention**
   graph, average % viewed. Shorts: the **Reach** tab ("shown in feed"). Parts: **impressions + CTR**.
3. Studio → **Analytics → Audience/Overview**: subscribers gained per video (the **Content** table, "Subscribers"
   column).
4. **Reach → Traffic source: YouTube search**: the search terms (for tags).
5. Studio → **Comments**: copy-paste the text (or a screenshot).

Read screenshots with the Read tool. Anything not given is **"not given"**, never estimated.

## 2. The table

| Video | Format | Published (age h) | Views | Viewed vs swiped | Avg % viewed | Subs | Notes |
|---|---|---|---|---|---|---|---|

- Use the **median** of the views, not the mean. Mark outliers (> 3× median) and misses (< 0.5× median).
- Under ~100 views per video, any difference is a **hint**. Say so in the report.
- Subscriber conversion = subs gained per 100 views. Compare the formats (phrases / conversation / story / grammar /
  Extra / Part).
- Keep last week's table next to this week's (see §8) and show the change.

## 3. Rules to apply

- **48-hour rule (new Shorts).** Under 48 h: no action. After 48 h, check viewed vs swiped (aim **≥ 70 %**).
  Still ~0 views → the owner deletes it and **re-uploads on another day with a new title**. Take one of the gate's
  `## Backup titles` from the sheet. Afterwards, fix the order in the 30-day playlist. Don't re-upload over and over:
  one retry, then learn from it.
- **Viewed vs swiped away:** ≥ 70 % good · 60–70 % watch it · < 60 % the hook is the problem. Rewrite the hook shape
  on the next days, not just this one.
- **Retention curve**, read against the script's scene times (`videos/<stem>.md`, `audio/<video>/timeline.json`):
  - cliff at 0–3 s → hook;
  - drop at the channel intro (≈ 6–18 s) → the intro is too long or too samey (docs/02 allows 2–3 intro variants);
  - slow slide through the lesson → pacing or too many new words;
  - drop at a ⏸️ pause → the pause is too long;
  - **bump** (rewatch) → note the phrase: it's a candidate for an Extra or a teaser Short;
  - drop at the outro → normal.
  Every fix names a **timestamp and one change**. A fix without a timestamp isn't a fix.
- **Impressions and CTR** (mostly Parts): CTR 4–8 % healthy, < 3 % = title/thumbnail problem. High CTR but low
  average view duration = the packaging over-promises (gate 3 in pre-upload-gate).
- **What worked:** set the best and worst titles, hook lines, thumbnail texts and hook shapes side by side. Only call
  something a pattern when one thing differs and it repeats on ≥ 2 videos.
- **Tags:** real search terms from the Traffic-source report go into future video-specific tags (3-group formula stays).

## 4. Tag experiment: "viral shorts" (check on 2026-10-06)

Days 3 and 5 have the tag; Days 2 and 4 are the comparison. Compare views, viewed vs swiped and shown-in-feed as pairs
(3 vs 2, 5 vs 4). Name the confounders: publish date and age, format, title. Verdict:
- **keep** if both tagged days clearly beat their pair and the swipe rate isn't worse;
- otherwise **drop it**, because generic tags add nothing we can see.

With such small numbers, "no difference" is the likely honest result. Write the verdict into docs/06 (see §7) and update
the experiment section and the upload-handover skill line if it changes the tag rule.

## 5. Comments → video ideas

Drop praise, spam and replies to other viewers. Group the rest by the question or complaint underneath. For each
group: the count ("1 comment" when it's one, never rounded up), the clearest comment **quoted word for word**, and a
title that **answers** it. Map each to one of: an **Extra**, a later **day** in docs/04, or **just a reply**. An idea
with no quoted comment is a guess and doesn't go in the list. Also draft replies (English + Arabic with
transliteration, per docs/06 Community) for comments still unanswered.

## 6. Never suggest

Buying views, subs or likes, sub-for-sub, engagement groups, asking friends to loop videos, or asking anyone to click
ads (docs/11, creator integrity: it can cost **both** channels). "Like, comment, subscribe" asks are fine.

## 7. Report (short) + learnings

```
Week of <date> — <one-sentence headline>
<table>
Worked: … · Didn't: … · Experiment: … · 48 h: …
Ideas from comments: 1. "<quote>" → <title> (<n> comments) → Extra/Day N
Next actions (max 5):
🔔 <owner, with the exact Studio path>   🤖 <Claude>
```

Append to **docs/06-publishing.md** under `## Learnings (dated)` (create the heading at the end the first time) **only
when it's real**: an experiment verdict, or a pattern seen on ≥ 2 videos. Format:
`- 2026-10-06: <learning> (evidence: <numbers>).` Hints stay in the report.

## 8. Keep the numbers

Append the week's table to `docs/12-channel-reviews.md` (create it on the first review, newest week on top), so next
week can compare. Update the memory notes when a rule changes.

---
Credits: adapted from AgriciDaniel/claude-youtube (analyze, audit, shorts), ravsau/youtuber-skills
(youtube-retention, youtube-comments-to-ideas, youtube-channel-audit) and sergebulaev/youtube-skills
(yt-audience-insights) — all MIT; their API/OAuth parts left out on purpose.
