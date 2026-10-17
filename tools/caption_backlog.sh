#!/bin/bash
# Daily (cron): upload pending caption files (one "video-id srt-path" per line in ~/.local/share/2min-yt/captions-pending.txt);
# lines that succeed are removed. Used when the YouTube API quota (10,000 units/day) runs out mid-batch.
cd "$(dirname "$0")/.." || exit 1
# wait for the network (up to 5 min): after a wake-up, a catch-up run starts before Wi-Fi is back (17 Oct)
for _ in $(seq 60); do getent hosts oauth2.googleapis.com >/dev/null 2>&1 && break; sleep 5; done
Q=~/.local/share/2min-yt/captions-pending.txt; LOG=~/.local/share/2min-yt/comments.log
[ -s "$Q" ] || exit 0
cp "$Q" "$Q.work"; : > "$Q"
while read -r vid srt; do
  [ -z "$vid" ] && continue
  if ~/.local/share/2min-yt/venv/bin/python tools/youtube_api.py captions "$vid" --replace "$srt" </dev/null 2>&1 | grep -q "✅"; then
    echo "[$(date '+%F %T')] captions replaced $vid" >> "$LOG"
  else
    echo "$vid $srt" >> "$Q"
  fi
done < "$Q.work"
rm -f "$Q.work"
