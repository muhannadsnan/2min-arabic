#!/bin/bash
# Weekly (cron, Sunday 10:00): collect the channel numbers into reports/<date>.md so Claude can review them at the next
# session (channel-review skill) — stats, audit, search terms, comments, top retention. Desktop notification when done.
cd "$(dirname "$0")/.." || exit 1
# wait for the network (up to 5 min): after a wake-up, a catch-up run starts before Wi-Fi is back (17 Oct)
for _ in $(seq 60); do getent hosts oauth2.googleapis.com >/dev/null 2>&1 && break; sleep 5; done
Y=~/.local/share/2min-yt/venv/bin/python
mkdir -p reports; R=reports/$(date +%F).md
{
  echo "# Weekly numbers $(date +%F)"; echo
  echo '## Videos'; echo '```'; $Y tools/youtube_api.py videos 2>&1; echo '```'
  echo '## Stats, last 7 days'; echo '```'; $Y tools/youtube_api.py stats --days 7 2>&1; echo '```'
  echo '## Search terms (28 days)'; echo '```'; $Y tools/youtube_api.py search-terms 2>&1; echo '```'
  echo '## Audit'; echo '```'; $Y tools/youtube_api.py audit 2>&1 | grep -v "^✅"; echo '```'
  echo '## Comments'; echo '```'; $Y tools/youtube_api.py comments --max 30 2>&1; echo '```'
} > "$R"
export DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/$(id -u)/bus
if grep -q "expired" "$R"; then notify-send -u critical "2 Minute Arabic" "Weekly report: YouTube login problem — ask Claude"; 
else notify-send "2 Minute Arabic" "Weekly numbers ready ($R) — say 'weekly review' to Claude"; fi
