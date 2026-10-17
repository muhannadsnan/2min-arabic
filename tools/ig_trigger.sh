#!/bin/bash
# Daily 15:01 (systemd user timer 2min-ig-trigger, catches up after the laptop was off): start the Instagram workflow
# right away instead of waiting for GitHub's unreliable schedule (17 Oct: 3 h late). Safe to run any time: the posting
# script only posts after 15:00 Oslo and only once a day.
cd "$(dirname "$0")/.." || exit 1
for _ in $(seq 60); do getent hosts api.github.com >/dev/null 2>&1 && break; sleep 5; done
LOG=~/.local/share/2min-yt/instagram.log
gh workflow run instagram-daily.yml -R muhannadsnan/2min-arabic -f dry_run=false >> "$LOG" 2>&1 \
  && echo "[$(date '+%F %T')] laptop nudge: workflow started" >> "$LOG" \
  || echo "[$(date '+%F %T')] laptop nudge FAILED" >> "$LOG"
