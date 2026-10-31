# 2 Minute Arabic — how we work

The owner records Arabic, uploads, and sends Studio screenshots. Claude does everything else and drives the flow:
the owner never has to name a skill. At the start of a session, check the **calendar** below and mention anything due.

## The flow (skills in `.claude/skills/`, chained by Claude)

| Owner says / sends | Claude runs |
|---|---|
| "next", "what's next", "plan the week" | **plan-lessons** → next 3–5 days + Extras, one batched recording sheet |
| a recording (Voice Memos file, sent as a document) | **produce-day** / **arabic-extras** → split, voice, images, assemble, checks |
| (automatically, every finished video) | **pre-upload-gate** → SHIP / FIX / KILL, then **upload-handover** (sheet opened with `code -r`) |
| every 5th day done | **compile-part** (Part N, 16:9, quiz from recorded lines) |
| Studio screenshots, comments, "how are we doing" | **channel-review** → report + max 5 next actions |
| openers, loops, green screen, 3D, monthly refresh | **animation-library** → 3D units in `library/`, rotation via `index.json` |
| a video/audio/article "to learn from" | **learn-from-source** → transcript, claims vs our data, proposals · `learning/` |

YouTube API: `~/.local/share/2min-yt/venv/bin/python tools/youtube_api.py` (videos, stats, retention, search-terms,
comments, fill). Secrets in `~/.config/2min-youtube/` (never in git). Testing mode → login expires weekly: re-run
`login` and send the owner the link (brand account **2 Minute Arabic**, not "Glorious Victorious").

Always end a hand-over with **what's next for the owner** (record / upload / screenshots) so nothing stalls.

## Calendar (keep it current)

- **Weekly social rhythm (owner 2026-10-30):** Instagram Reel daily 15:00 + dubbed trial Reel daily 17:37 (owner 2026-10-30: each language its OWN LOOK —
  tools/ig_lang_version.py: other cover character + background, frame colour, translated badge, zoom, subtitles in its
  script; only `-v2` bundles post; languages hi → ur → id → tr → ms; videos Day 12 → x03 → Day 8 → Day 3 → Day 4 → x01;
  Instagram profile stays English-only — language versions only as trials, never shared to followers;
  Day 12 hi (2,375 views, record) posted 30 Oct, ur/id/tr/ms queued as trials 31 Oct–3 Nov; **2 Nov check:**
  < ~30 views each or the "shared before" warning → stop dubs; ~100 → continue, maybe 2/day after 2 weeks) · **Instagram carousel Wed + Sun 19:00** (GitHub
  instagram-carousel.yml, queue `ig-carousel`; 7–8 slides = cover + 5–6 words + closing; the words of the latest
  Instagram Reel's video; every picture a dedicated close-up made for the slide, every hand finger-checked at full
  size; owner approves each batch — tools/make_carousel.py + tools/ig_carousel_add.py; queued: Day 19 directions
  1 Nov, body parts 4 Nov) · **YouTube Post Mon / Wed / Fri** (owner posts by hand, Claude prepares picture + text):
  a teaser for the newest YouTube video with 2 new words or sentences + the video attached (a post takes pictures OR a video, not both); every other one a quiz. Files: output/yt-posts/<date>-<video>/ (post.txt + HOW.md).
  Review after 2 weeks (saves, follows, reach per post) — up to 3 carousels/week if it holds, down if reach per post drops.
- **Facebook page (owner 2026-10-31):** app Live since 30 Oct; the 22 invisible older Reels deleted + republished.
  **English only.** Daily: proven hit 12:00 (facebook-hits.yml, data/fb-hits.txt) · English Reel 15:00.
  **Groups:** owner shares by hand (no API since 2024) from https://muhannadsnan.github.io/2min-arabic/groups.html —
  ~19 groups (tools/fb_groups_page.py GROUPS; owner sends the final English list), 3 a day by calendar, same on every
  device; language groups upload files from ~/Downloads/fb-groups/ (data/fb-group-files.json); reminder .ics 15:15.
  **2 Nov check:** Facebook watch time per Reel (Day 17: 125 views, 2 s avg) — hits vs daily vs language versions.
- **Website** https://muhannadsnan.github.io/2min-arabic/ = the Instagram bio link: newest YouTube lessons + this
  week's Instagram videos, refreshed by GitHub (site-latest.yml, 15:25 + 17:25), tools/site_latest.py.

- ~~After the vacation: restore sleep-on-power~~ → done 2026-10-15.
- **After the trip (14 Oct), Instagram:** account 2minutearabic (Creator, Education, bio + YouTube link set). Reels
  01–14 scheduled by hand in the app 8–21 Oct (folder `../instagram-reels-oct`, SCHEDULE.txt). Still to do: link the
  Facebook Page "2-Minute Arabic" (rename to "2 Minute Arabic") to Instagram — connection failed on 7 Oct (new-account
  limit); do NOT attach the business portfolio "BM Muhannad Senan" or the ad account. Meta app "2minarabic tools"
  (Instagram API, development mode, Facebook-login route) → Graph API Explorer token (instagram_basic,
  instagram_content_publish, pages_show_list, pages_read_engagement, business_management) + App ID/secret →
  long-lived token → build the posting tool. Then: "Share to Facebook" for Reels. Also: Google OAuth "In production"
  (needs homepage + privacy policy page).
- **2026-10-15: RAM upgraded to 40 GB** (8 GB SK Hynix + 32 GB Samsung, both 3200). GPU sessions no longer need
  "close all apps"; measure the real speed gain at the next session and update docs/16.
- **TODO when the API allows (owner 2026-10-19: don't spend today's quota on it):** replace the 5-language block in all 31 video descriptions with the 13-language block (tools/description_languages.json "block"; old one kept as "block_5_until_2026-10-19") + add the Bengali voice credit line to the 6 top videos (Piper bn_BD, OpenSLR 37, CC BY-SA 4.0). ≈ 1,850 units — best right after the quota extension is granted or when the subtitle backlog is done. New videos already get the 13-language block.
- **2026-11-01: Trial Reels check** — x03's Malay + Swahili trials got 0 views (earlier ones ~110, never a follow/save). Day 12's 9 dubs queued 29 Oct (id, hi, tr first; one a day 17:37 Oslo). If id/hi/tr also get ~0 → stop trials, put the effort into normal Reels. (`instagram_api.py media`)
- ~~**~2026-10-23: queue Day 12's dubbed Trial Reels** (x03's run 2 a day — ~11:30 + ~18:30 — until ~23 Oct; owner: then 1 a day → remove the `37 9 * * *` line in .github/workflows/instagram-trial.yml): write output/ig-trial/captions-012-grammar-no-word-for-my.json (9 languages, like x03's) → `python3 tools/ig_trial_add.py 012-grammar-no-word-for-my <json> --apply`. Then the next top video.~~ → done 29 Oct, one a day.
- **Meta setup 20 Oct:** own business portfolio **"2 Minute Arabic"** (separate from "BM Muhannad Senan", which stays for the other business — don't delete it, don't add 2 Minute Arabic assets to it); Facebook page "2 Minute Arabic" (https://www.facebook.com/profile.php?id=61595131652324, page ID 61595131652324) **linked to Instagram 2minutearabic (done 20 Oct, API posting re-checked OK)**; owner turns on Instagram → Crossposting → share Reels to Facebook. **20 Oct after 15:00: check whether the API-posted Reel also appeared on the Facebook page** — if not, add Facebook Page publishing to ig_cloud_post.py (needs a Page token with pages_manage_posts). **Owner TODO (security, soon):** remove/delete the page "No Problem" (left from the old hack), check Page access on 2 Minute Arabic (only the owner), 2FA on, "Where you're logged in" cleaned, Facebook + Instagram.
- **Meta block 22 Oct ~15:00 → 23 Oct ~11:00:** "unusual activity" on the developer account (most likely the 14-post Facebook backfill in one hour on 20 Oct) blocked the app for Instagram + Facebook; owner confirmed the account. Missed Day 12 posted 23 Oct 11:05, today's Reel by a one-off timer at 15:10. **Rule: never post more than ~3 things an hour through the API; catch-ups spread over days.** Reply to Google (quota review, due within 7 business days of 23 Oct): output/api-quota-form/REPLY-2026-10-23.txt.
- **Early November: Instagram boost** (owner postponed) — docs/18: Day 3 Reel, pay in the browser, tier-1 / tier-2 split, judge by cost per follower.
- **Free PDF link** (https://muhannadsnan.github.io/2min-arabic/free/) goes into every new sheet's description from now on and into the 31 older descriptions with the queued 13-language update (docs/20).
- **2026-10-22: Instagram Trial Reels check** — x03 dubbed in Indonesian (Deo_WECFWx5) + Hindi (Deo_ffDDMBX), posted 18 Oct as Trial Reels (non-followers only). Compare reach/plays with normal Reels (`instagram_api.py media`); if better → one more language a day (tr, fa, bn, ru, es, fr, sw from x03), captions pointing to YouTube for their language. Also: which rotating language hashtags bring reach.
- **After the 23 Oct check (owner to confirm):** retitle Day 11 (eX2rqmZpd34) "Basic Arabic Conversation: Meeting a Tourist" → "…: Talking to Locals" (learner = the visitor).
- **2026-10-25: Lina motivation Reel check** (posted by the owner 23 Oct 13:54 with Sia "Unstoppable", normal Reel, De1fxT8uJ_7; still image + text, made from FLUX klein) — views, reach, follows that day vs normal Reels (~200 views). Better → 1 such post a week (docs/18).
- **2026-10-24: viewed-vs-swiped check** — ask the owner for "Stayed to watch" (Analytics → Engagement) on Days 17–20. Day 16 (first with the short intro) 67.7 % vs Days 14/15 37 %/45 % (learning/notes/2026-10-20-dan-the-creator…). ≥ 2 of Days 17–20 at ≥ 60 % → confirmed learning in docs/06.
- **2026-10-23: re-packaging check** — ALL published Shorts got new titles (subject first + category) and thumbnails
  (big English words + small Arabic) on 16 Oct (owner, option a; log + views at change: output/repackage-proposals-2026-10-16/
  applied-log.json; earlier 15 Oct changes: output/repackage-2026-10-15/). (19 Oct also: the 3 Part thumbnails → "ARABIC CONVERSATION" + topic bullets + a real phrase from each Part, output/part-thumbs-2026-10-19/.) Compare views/day for 7 days before vs after,
  channel-wide and per video; search-traffic share; revert single videos that clearly lost.
- **Quota lesson (19 Oct):** the subtitle job uses the rest of the day's 10,000 units — since 27 Oct it runs at 20:30, after the 09:15 fills and the 19:30 comment replies (quota resets 09:00 Oslo).
- **YouTube API quota extension SUBMITTED 2026-10-18 afternoon** (50,000/day; answers + evidence in output/api-quota-form/). Once granted: (50,000/day, form evidence output/api-quota-form/) — watch the email for Google's questions; when granted, raise `subtitle-backlog --max` in tools/caption_backlog.sh.
- **2026-10-31: translations + subtitles check** (also: Studio → Audience → Top geographies → cut subtitle languages that bring nothing; 13 now) — 5 videos got fa/ur/tr/id/fr titles + descriptions on 17 Oct (tools/localizations.json,
  `youtube_api.py localize`). Studio → Analytics → Research: search terms in those languages + views from IR, AF, PK, TR, ID, FR
  before vs after. Up → localize all older videos too.
- **From 2026-10-17 (owner, growth plan):** Day 21 = real-situation challenge · share hook on every new video (compare
  with 8 shares total) · 1 Extra/week (owner: 2/week too tight), always a searched topic from the plan-lessons list; Days stay daily · 1 Instagram carousel/week from the week of 20 Oct (best word list, own cards; needs a
  carousel option in tools/instagram_api.py) · from 26 Oct: search share per video (Extras > 30 %) + saves per carousel.
- **Weekly (Sunday):** channel-review — `audit` (fix every ⚠️), search terms → tags of matching videos, stats,
  then ask only for the screenshots the API can't give (viewed vs swiped).
- **YouTube login: permanent since 2026-10-15** — Google app "In production" (unverified, personal use; login shows
  "Google hasn't verified this app" → Advanced → Go to 2min tools). Home + privacy pages on the `gh-pages` branch:
  https://muhannadsnan.github.io/2min-arabic/ (verified in Search Console — keep `google413904a81875b8fb.html`).
- **Scheduled jobs = systemd user timers with catch-up (2026-10-15, owner):** `systemctl --user list-timers '2min-*'` —
  pending-jobs 09:15 · ig-queue-check 10:00 (refills the Instagram queue itself when ≤ 3, tools/ig_refill.py) ·
  caption-backlog 20:30 (translated subtitles, last job of the day: uses whatever quota is left, ≈ 18–22 tracks) · **comment-replies 19:30** (Claude answers YouTube + Instagram comments, tools/comment_replies_prompt.md, desktop summary) · weekly-report Sun 10:00 · instagram-refresh Mon 09:00 (also updates the GitHub secret IG_TOKEN).
  **Instagram posting runs on GitHub Actions**, started at 15:00 sharp by **cron-job.org** (owner's account, job "2min Instagram 15:00"; GitHub token `2min-ig-cron`, Actions-write on this repo only, **expires 2027-10-17 → renew ~1 Oct 2027**; GitHub's own schedule was up to 3 h late),  (.github/workflows/instagram-daily.yml, 15:00 Oslo, laptop can be off) from the
  encrypted `ig-queue` release (key: ~/.config/2min-instagram/queue.key = secret IG_QUEUE_KEY); the laptop timer
  2min-instagram-daily is disabled (don't re-enable: double posts). Dry run: `gh workflow run instagram-daily.yml -f dry_run=true`. The once-a-day check counts only normal shared Reels (Trial Reels and the owner's photo posts don't block it). **Trial Reels:** .github/workflows/instagram-trial.yml posts dubbed versions from the encrypted `ig-trial` release (tools/ig_trial_add.py), ~11:37 + ~18:37 Oslo while x03 runs, then once a day. A run missed
  while the laptop was off runs when it's back on. Only comment_job stays in cron (hourly). Units in ~/.config/systemd/user.
- **Hourly (cron, automatic):** `tools/comment_job.sh` posts each sheet's pinned comment once its video is live and
  pops a desktop notification; the owner taps ⋮ → Pin (no API for pinning). Log: `~/.local/share/2min-yt/comments.log`.
- **Schedule (Shorts, 17:00 Oslo):** Day 2 re-upload 2 Oct · x01 3 Oct · x02 4 Oct · Day 6 5 Oct (7IQ0GYOC9X4) · Day 7 6 Oct (QuLTZ42HMxs) · Day 8 7 Oct (nYz4KkohiIc) · Day 9 8 Oct (KiwR8OU3aeQ) · Day 10 9 Oct (5kaDplowig4) · x03 10 Oct (pbIY5duEYzE) · x04 11 Oct (fbHfwdMExss) · Day 11 12 Oct (eX2rqmZpd34) · Day 12 13 Oct (9LaQeya3gbw) · Day 13 14 Oct (_iPKgHfT_b4) · Day 14 15 Oct (nXRwJBqOPy0) · Day 15 16 Oct (7hZTq8KtA1I) · x05 17 Oct (-ju67hph1EI) · v01 18 Oct (W5tlsFXCjyY) · Day 16 19 Oct (PEsT02c8BE4) · Day 17 20 Oct (ecqKTY00R14) · Day 18 21 Oct (h_TbkPZZlgw) · Day 19 22 Oct (hF3mP86tixw) · Day 20 23 Oct (zfXQKp1XWUY) · x06 24 Oct (LWlgINnlAk0) · v02 25 Oct (pYM-T12xe6s) · **talk video t01 (owner, clay) 26 Oct · next: Day 21 27 Oct** · trailer t02 public 19 Oct 12:00 + set as channel trailer. Long chain: Part 2 10 Oct (lYgjF0MTaYo) · Part 3 17 Oct (_xqKbGy66dY, filled + scheduled 15 Oct).
- **48 h checks:** Day 2 (re-upload) 4 Oct · x01 5 Oct · x02 6 Oct.
- ~~2026-10-06: viral shorts verdict~~ → dropped (docs/06 Learnings).
- **48 h after each Short:** if ~0 views, re-upload with a backup title (pre-upload-gate writes them).
- **After Day 10 (2026-10-06):** Part 2 scheduled. Extras **x03** + **x04** (from existing recordings) uploaded + scheduled 10/11 Oct. **Day 11 is due ~12 Oct**: plan Days 11–15 +
  record them together with **v01 café words** (`videos/v01-cafe-words-recording-sheet.md`, 9 words) now.
  Weekly rhythm: 5 days → Extra → Vocab; Part on the long chain; monthly long video (docs/06).
- **To assess at the 1 Nov review (owner 2026-10-23: "remember what's useful, assess later"):** (1) monthly **outlier-topic scan** — other Arabic-teaching channels' videos far above their own average → topics for Extras (learning/notes/2026-10-23-kellan…; a few search.list calls, within the quota-form promise); (2) owner checks Studio → Settings → Channel → Feature eligibility (intermediate + advanced); (3) Part openings: start with the first lesson/quiz question (Part 1 loses half its viewers in 30 s); (4) after YPP: ad pay is high Oct–Dec, low in January; sponsors/own products > AdSense (learning/notes/2026-10-23-pov…).
- **Monthly (~1st of the month, first: 2026-11-01):** refresh the animation library — 3–5 new openers, 1–2 talk
  units, backgrounds. Ask the owner to close all apps and leave the laptop to it.
- **Characters v5 (owner plan 2026-10-26, animation-library skill):** all characters on green screen as blended picture sequences — openers 5 pics/s, mid-video 3 pics/s from reusable motion sets, new background per video, finger check on every picture. **Pilot Day 24 → v5.1 approved 26 Oct** (still unless speaking, mouth-only talk, facing each other; tools/animate/compose_talk.py).
- **Monthly Episode (owner 2026-10-24, docs/21-monthly-episode.md):** Shorts → weekly Parts → a monthly 30+ min "Episode N" by topic, no day numbers, big combined conversation (Arabic + English), vocab, final challenge. Episode 1 (October) planned ≈ 35 min; owner to pick the publish date (1 or 8 Nov).
- **Next up (2026-10-31):** Days 26–30, x08, v04 built with real voices, checked, in ~/Downloads/to confirm/ — waiting
  for the owner's OK (Day 26 publishes 3 Nov) → then upload sheets, 13-language titles, thumbnails, gate. Every video
  for the owner goes to ~/Downloads/to confirm/.
- **Next up (2026-10-29):** Days 23–25 + x07 re-uploaded with sound effects (new IDs KcnBpXKKpAM · MxlEx771Dnk · jXjfzVXmkhQ · ZjH1guEQuvI); v03 colors uploaded (slqxiJIVVVk, 2 Nov; captions/playlist/translations in the 09:15 queue). **Part 5 produced** (videos/w05-upload.md, 9:13, fill key `w05`, schedule Sat 7 Nov 17:00) — waiting for the owner's upload. Translated subtitles: dubs/ for 021–025, x07, v03 written 28 Oct (fill now registers dubs/ids.json itself); Parts + Episode still have none (multi-timeline, to build). Next: plan Days 26–30 + recording sheet.
- **Next up (2026-10-24):** Days 22 + 23 prepared up to the recording (scripts, cards, images, chalk boards, openers d22-sami-slowly + d23-lina-planner — owner approval pending, sheets + 13 translations in tools/localizations-pending.json keys `022`/`023`). When `_2125` arrives: put it in footage/recordings/_2125-combined/ → `$TTS tools/split_recording.py videos/_2125-combined.md` → build day maps from the pool (like 021) → make_audio → assemble → checks. Part 4 filled 24 Oct (09:15 queue). **Decide with the owner:** monthly long searched video (YPP 8,000 h from 1 Feb 2027; we have 3.6 long-form h in 4 weeks) + end-on-the-peak outro (learning/notes/2026-10-24-*).
- **Next up (2026-10-23):** Day 21 (videos/021-answer-the-waiter, 27 Oct) + Part 4 (videos/w04, 25 Oct) **produced, waiting for the owner's upload** (fill keys: `021-answer-the-waiter`, `w04` → 13 translations in tools/localizations-pending.json). Waiter opener d21-waiter-notepad = owner approval pending. Recording sheets out: videos/_2125-whatsapp.txt (Days 22–25 + x07 Inshallah + v03 colors, 58 lines) + videos/_lina-koki-5-whatsapp.txt (4). Schedule: Day 22 28 Oct · 23 29 · 24 30 · 25 31 · x07 1 Nov · v03 2 Nov · Part 5 ~7 Nov.
- **PAUSED 2026-10-16 ~16:40 (owner) — resume here:** openers all picked (library/work/keys/w4/PICKS.txt; joined
  clips in library/work/joined/: d17 (AI idle), d18 + d20 + x06 (tools/animate/join_tail.sh — held hands smear in AI idles)).
  Rerun `library/work/queue-w4t.sh` (skips finished clips; starts its own ComfyUI): images resume at Day 16 s12 (keys
  board/table done), then stops ComfyUI and makes audio for all 7. Then `queue-w4u.sh` (idle clips d16/d19/v02) →
  join_idle.sh → assemble → checks → sheets (titles/thumbnails per the 2026-10-16 packaging rules, categories).
  **Re-packaging (owner chose option a: all published Shorts incl. the 4 in the 22 Oct test):** proposals in
  output/repackage-proposals-2026-10-16/ (proposals.json + thumbnails) — owner reviews the folder, then apply via API.
- **Next up (2026-10-15):** scripts written 15 Oct (videos/016–020, x06, v02; all lines mapped, 0 missing). Next: images + openers + produce. Days 16–20 + x06 (numbers 11–20, search "arabic numbers 1 to 20") + v02 (10 body words incl. صَدْرْ chest, not بَطْنْ — owner,
  real search "parts of body in arabic") planned; sheets `videos/_1620-whatsapp.txt` (71) + `_lina-koki-4-whatsapp.txt` (8).
  Schedule: Day 16 19 Oct … Day 20 23 Oct · x06 24 · v02 25 · Day 21 (real-situation challenge, re-used recordings) 26. Approved 15 Oct: short intro,
  visible quests, recall moved to "Your turn" (produce-day). Pending: reusable-video upgrade (style/model test) · Part 3.
- (older) **Next up (2026-10-07):** Days 11–15 + x05 + v01 produced and scheduled to 18 Oct. Next: Part 3 (Days 11–15, long chain, after 16 Oct) and plan Days 16–20 after the trip. (Old note:
  owner `videos/_1115-whatsapp.txt` (51 lines) + Koki `videos/_lina-koki-3-whatsapp.txt` (11 lines), due ~9 Oct.
  Then: split → new characters (Tom; Lina's family + cat) → openers (41 frames) → produce in day order.
  Schedule: Day 11 12 Oct · 12 13 · 13 14 · 14 15 · 15 16 · x05 17 · v01 18 · Day 16 19 Oct; Part 3 (11–15) 17 Oct.

## Rules that are easy to forget

- All Arabic = real recordings (owner; Lina = Koki). No Arabic TTS, no voice conversion. English = owner's clone.
- Voice references and recordings are private: never committed, never shared.
- Uploads in day order. Automatic dubbing OFF. No hashtags in titles. Arabic in descriptions inside U+2067…U+2069.
- Never buy views/subs or use engagement groups; never use third-party or watermarked footage (docs/11).
- From Day 6: 3D look + library opener in scene 1. No AI label on videos (owner). No PC upgrades / bigger models for now.
- Stop ComfyUI by PID; set LD_LIBRARY_PATH for Whisper (final_check.py does it itself).
- Details: docs/02 format · 04 curriculum · 05 style · 06 publishing · 07 monetization · 10 production · 11 policy · 16 hardware, speed + power.
