#!/bin/bash
# Daily (systemd user timer 2min-ig-queue-check, catches up after the laptop was off): how many Reels are left in the
# Instagram queue? ≤ 3 → desktop notification so the owner asks Claude to refill it (owner's idea, 2026-10-15).
# Cloud queue = the ig-queue release (GitHub posts from it); before that exists, the laptop folder + ig-last.txt.
export DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/$(id -u)/bus
LOG=~/.local/share/2min-yt/instagram.log
if left=$(gh release view ig-queue -R muhannadsnan/2min-arabic --json assets --jq '[.assets[].name | select(startswith("reel-"))] | length' 2>/dev/null); then
  where="GitHub queue"
else
  Q="/home/msn/Documents/Youtube channels/instagram-reels-oct"; last=$(cat ~/.local/share/2min-yt/ig-last.txt 2>/dev/null || echo 0)
  left=$(ls "$Q"/[0-9][0-9]_*.mp4 2>/dev/null | awk -F/ -v l="$last" '{n=substr($NF,1,2)+0; if (n>l) c++} END{print c+0}')
  where="laptop queue"
fi
echo "[$(date '+%F %T')] queue check: $left Reels left ($where)" >> "$LOG"
if [ "$left" -le 3 ]; then
  notify-send -u critical "2 Minute Arabic" "Instagram queue: only $left Reels left — tell Claude: refill the Instagram queue"
fi
