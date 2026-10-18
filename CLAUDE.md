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
- **2026-10-23: re-packaging check** — ALL published Shorts got new titles (subject first + category) and thumbnails
  (big English words + small Arabic) on 16 Oct (owner, option a; log + views at change: output/repackage-proposals-2026-10-16/
  applied-log.json; earlier 15 Oct changes: output/repackage-2026-10-15/). Compare views/day for 7 days before vs after,
  channel-wide and per video; search-traffic share; revert single videos that clearly lost.
- **YouTube API quota extension requested 2026-10-18** (50,000/day, form evidence output/api-quota-form/) — watch the email for Google's questions; when granted, raise `subtitle-backlog --max` in tools/caption_backlog.sh.
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
  caption-backlog 10:30 · weekly-report Sun 10:00 · instagram-refresh Mon 09:00 (also updates the GitHub secret IG_TOKEN).
  **Instagram posting runs on GitHub Actions**, started at 15:00 sharp by **cron-job.org** (owner's account, job "2min Instagram 15:00"; GitHub token `2min-ig-cron`, Actions-write on this repo only, **expires 2027-10-17 → renew ~1 Oct 2027**; GitHub's own schedule was up to 3 h late),  (.github/workflows/instagram-daily.yml, 15:00 Oslo, laptop can be off) from the
  encrypted `ig-queue` release (key: ~/.config/2min-instagram/queue.key = secret IG_QUEUE_KEY); the laptop timer
  2min-instagram-daily is disabled (don't re-enable: double posts). Dry run: `gh workflow run instagram-daily.yml -f dry_run=true`. A run missed
  while the laptop was off runs when it's back on. Only comment_job stays in cron (hourly). Units in ~/.config/systemd/user.
- **Hourly (cron, automatic):** `tools/comment_job.sh` posts each sheet's pinned comment once its video is live and
  pops a desktop notification; the owner taps ⋮ → Pin (no API for pinning). Log: `~/.local/share/2min-yt/comments.log`.
- **Schedule (Shorts, 17:00 Oslo):** Day 2 re-upload 2 Oct · x01 3 Oct · x02 4 Oct · Day 6 5 Oct (7IQ0GYOC9X4) · Day 7 6 Oct (QuLTZ42HMxs) · Day 8 7 Oct (nYz4KkohiIc) · Day 9 8 Oct (KiwR8OU3aeQ) · Day 10 9 Oct (5kaDplowig4) · x03 10 Oct (pbIY5duEYzE) · x04 11 Oct (fbHfwdMExss) · Day 11 12 Oct (eX2rqmZpd34) · Day 12 13 Oct (9LaQeya3gbw) · Day 13 14 Oct (_iPKgHfT_b4) · Day 14 15 Oct (nXRwJBqOPy0) · Day 15 16 Oct (7hZTq8KtA1I) · x05 17 Oct (-ju67hph1EI) · v01 18 Oct (W5tlsFXCjyY) · Day 16 19 Oct (PEsT02c8BE4) · Day 17 20 Oct (ecqKTY00R14) · Day 18 21 Oct (h_TbkPZZlgw) · Day 19 22 Oct (hF3mP86tixw) · Day 20 23 Oct (zfXQKp1XWUY) · x06 24 Oct (LWlgINnlAk0) · v02 25 Oct (pYM-T12xe6s) · **next: Day 21 (board quiz) 26 Oct**. Long chain: Part 2 10 Oct (lYgjF0MTaYo) · Part 3 17 Oct (_xqKbGy66dY, filled + scheduled 15 Oct).
- **48 h checks:** Day 2 (re-upload) 4 Oct · x01 5 Oct · x02 6 Oct.
- ~~2026-10-06: viral shorts verdict~~ → dropped (docs/06 Learnings).
- **48 h after each Short:** if ~0 views, re-upload with a backup title (pre-upload-gate writes them).
- **After Day 10 (2026-10-06):** Part 2 scheduled. Extras **x03** + **x04** (from existing recordings) uploaded + scheduled 10/11 Oct. **Day 11 is due ~12 Oct**: plan Days 11–15 +
  record them together with **v01 café words** (`videos/v01-cafe-words-recording-sheet.md`, 9 words) now.
  Weekly rhythm: 5 days → Extra → Vocab; Part on the long chain; monthly long video (docs/06).
- **Monthly (~1st of the month, first: 2026-11-01):** refresh the animation library — 3–5 new openers, 1–2 talk
  units, backgrounds. Ask the owner to close all apps and leave the laptop to it.
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
