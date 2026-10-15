#!/bin/bash
# Daily (cron 17:00): post the next Reel of the Instagram queue folder (numbered NN_<date>_<slug>.mp4 + _cover.jpg,
# captions in SCHEDULE.txt), remember the last number in ~/.local/share/2min-yt/ig-last.txt, notify the owner.
cd "$(dirname "$0")/.." || exit 1
Q="${IG_QUEUE:-/home/msn/Documents/Youtube channels/instagram-reels-oct}"
STATE=~/.local/share/2min-yt/ig-last.txt; LOG=~/.local/share/2min-yt/instagram.log
last=$(cat "$STATE" 2>/dev/null || echo 0); next=$(printf "%02d" $((10#$last + 1)))
export DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/$(id -u)/bus
vid=$(ls "$Q"/${next}_*.mp4 2>/dev/null | head -1)
if [ -z "$vid" ]; then notify-send -u critical "2 Minute Arabic" "Instagram queue is empty after Reel $last — ask Claude for the next Reels"; exit 0; fi
cap=$(mktemp); python3 - "$Q/SCHEDULE.txt" "$next" "$cap" <<'PY'
import re,sys
s=open(sys.argv[1],encoding="utf-8").read(); blk=s.split(f"{sys.argv[2]}.  ")[1]
open(sys.argv[3],"w",encoding="utf-8").write(re.search(r"-{40}\n(.*?)\n-{40}",blk,re.S).group(1))
PY
out=$(python3 tools/instagram_api.py post "$vid" --cover "${vid%.mp4}_cover.jpg" --caption-file "$cap" --apply 2>&1); rm -f "$cap"
echo "[$(date '+%F %T')] $next: $out" >> "$LOG"
if echo "$out" | grep -q "published:"; then echo "$((10#$next))" > "$STATE"; notify-send "2 Minute Arabic" "Instagram Reel $next posted ✅";
else notify-send -u critical "2 Minute Arabic" "Instagram Reel $next failed — ask Claude (log: $LOG)"; fi
