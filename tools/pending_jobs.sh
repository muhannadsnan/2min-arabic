#!/bin/bash
# Daily (cron, 09:15 — after the YouTube API quota resets): run queued youtube_api.py commands, one per line in
# ~/.local/share/2min-yt/pending-commands.txt (arguments as for tools/youtube_api.py); successful lines are removed.
cd "$(dirname "$0")/.." || exit 1
# wait for the network (up to 5 min): after a wake-up, a catch-up run starts before Wi-Fi is back (17 Oct)
for _ in $(seq 60); do getent hosts oauth2.googleapis.com >/dev/null 2>&1 && break; sleep 5; done
Q=~/.local/share/2min-yt/pending-commands.txt; LOG=~/.local/share/2min-yt/comments.log
[ -s "$Q" ] || exit 0
cp "$Q" "$Q.work"; : > "$Q"
while read -r line; do
  [ -z "$line" ] && continue
  if eval ~/.local/share/2min-yt/venv/bin/python tools/youtube_api.py $line </dev/null >> "$LOG" 2>&1; then
    echo "[$(date '+%F %T')] done: $line" >> "$LOG"
  else
    echo "$line" >> "$Q"
  fi
done < "$Q.work"
rm -f "$Q.work"
export DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/$(id -u)/bus
[ -s "$Q" ] || notify-send "2 Minute Arabic" "Queued YouTube updates are done (scheduling / details)." 2>/dev/null
