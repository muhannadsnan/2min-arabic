#!/bin/bash
# Daily 19:30 (systemd user timer 2min-comment-replies, catches up after the laptop was off): Claude answers new
# YouTube + Instagram comments by the rules in tools/comment_replies_prompt.md (owner, 2026-10-19). Claude may only
# run the two listing commands and the two reply commands; everything is logged, and the owner gets one notification.
cd "$(dirname "$0")/.." || exit 1
for _ in $(seq 60); do getent hosts oauth2.googleapis.com >/dev/null 2>&1 && break; sleep 5; done
export DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/$(id -u)/bus
LOG=~/.local/share/2min-yt/comment-replies.log; PY=~/.local/share/2min-yt/venv/bin/python
echo "=== $(date '+%F %T')" >> "$LOG"
OUT=$(~/.local/bin/claude -p "$(cat tools/comment_replies_prompt.md)" \
  --allowedTools "Bash($PY tools/youtube_api.py pending-comments)" "Bash($PY tools/instagram_api.py pending-comments)" \
                 "Bash($PY tools/youtube_api.py reply:*)" "Bash($PY tools/instagram_api.py reply:*)" \
  --max-turns 60 2>&1)
echo "$OUT" >> "$LOG"
SUM=$(grep -m1 "^SUMMARY:" <<<"$OUT" | sed 's/^SUMMARY: //')
if [ -n "$SUM" ]; then
  notify-send "2 Minute Arabic · comments" "$SUM"
else
  notify-send -u critical "2 Minute Arabic · comments" "The comment run had a problem — log: $LOG"
fi
