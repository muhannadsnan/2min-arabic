#!/bin/bash
# Hourly (cron): post the pinned-comment text on newly published videos, then pop a desktop notification to pin it.
cd "$(dirname "$0")/.." || exit 1
LOG=~/.local/share/2min-yt/comments.log
OUT=$(~/.local/share/2min-yt/venv/bin/python tools/youtube_api.py post-comments 2>&1)
echo "[$(date '+%F %T')] $OUT" >> "$LOG"
export DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/$(id -u)/bus
if grep -q "✅" <<<"$OUT"; then
  notify-send -u critical "2 Minute Arabic" "Comment posted on a new video — open YouTube and tap ⋮ → Pin" 2>/dev/null
elif grep -q "expired" <<<"$OUT"; then
  notify-send -u critical "2 Minute Arabic" "YouTube login expired — ask Claude for the login link" 2>/dev/null
fi
