#!/bin/bash
# Daily (systemd user timer 2min-ig-queue-check, catches up after the laptop was off): Instagram queue level.
# ≤ 3 Reels left → refill it by itself from the Shorts that are already public on YouTube (tools/ig_refill.py,
# owner 2026-10-15: "Claude just goes ahead and does that"). The owner only hears about it when there is nothing new
# to refill (= time to produce videos) or when something fails.
cd "$(dirname "$0")/.." || exit 1
# wait for the network (up to 5 min): after a wake-up, a catch-up run starts before Wi-Fi is back (17 Oct)
for _ in $(seq 60); do getent hosts oauth2.googleapis.com >/dev/null 2>&1 && break; sleep 5; done
export DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/$(id -u)/bus
LOG=~/.local/share/2min-yt/instagram.log; PY=~/.local/share/2min-yt/venv/bin/python
note(){ echo "[$(date '+%F %T')] $1" >> "$LOG"; }
if left=$(gh release view ig-queue -R muhannadsnan/2min-arabic --json assets --jq '[.assets[].name | select(startswith("reel-"))] | length' 2>/dev/null); then
  note "queue check: $left Reels left (GitHub queue)"
  [ "$left" -gt 3 ] && exit 0
  out=$($PY tools/ig_refill.py --apply 2>&1); note "refill: $(echo "$out" | tail -1)"
  if echo "$out" | grep -q "^REFILLED"; then
    notify-send "2 Minute Arabic" "Instagram queue refilled by itself: $(echo "$out" | tail -1 | sed 's/^REFILLED //')"
  elif echo "$out" | grep -q "NOTHING_TO_REFILL"; then
    notify-send -u critical "2 Minute Arabic" "Instagram: $left Reels left and no new public Shorts to add — time for new videos (ask Claude)"
  else
    notify-send -u critical "2 Minute Arabic" "Instagram queue refill failed — ask Claude (log: $LOG)"
  fi
else   # cloud posting not set up yet: the laptop folder + ig-last.txt
  Q="/home/msn/Documents/Youtube channels/instagram-reels-oct"; last=$(cat ~/.local/share/2min-yt/ig-last.txt 2>/dev/null || echo 0)
  left=$(ls "$Q"/[0-9][0-9]_*.mp4 2>/dev/null | awk -F/ -v l="$last" '{n=substr($NF,1,2)+0; if (n>l) c++} END{print c+0}')
  note "queue check: $left Reels left (laptop queue)"
  [ "$left" -le 3 ] && notify-send -u critical "2 Minute Arabic" "Instagram queue: only $left Reels left — tell Claude: refill the Instagram queue"
fi

# the other queues (owner 2026-11-02): built ahead by Claude, a warning when they're about to run out
R=muhannadsnan/2min-arabic
count(){ gh release view "$1" -R $R --json assets --jq "[.assets[].name | select(test(\"$2\"))] | length" 2>/dev/null; }
if t=$(count ig-trial '^trial-.*-v2[.]bin$'); then
  note "trial check: $t language versions left"
  [ "$t" -le 1 ] && notify-send -u critical "2 Minute Arabic" "Instagram trials: $t left — tomorrow there's nothing to post. Ask Claude for the next video's 5 languages."
fi
if c=$(count ig-carousel '^carousel-.*[.]bin$'); then
  note "carousel check: $c left"
  [ "$c" -le 1 ] && notify-send -u critical "2 Minute Arabic" "Instagram carousels: $c left (Wed + Sun). Ask Claude for the next carousels."
fi
h=$(grep -cv '^#\|^\s*$' data/fb-hits.txt 2>/dev/null || echo 0)
note "facebook hits: $h left"
[ "$h" -le 3 ] && notify-send "2 Minute Arabic" "Facebook hits: $h left — the list restarts from the best ones after that."
exit 0
