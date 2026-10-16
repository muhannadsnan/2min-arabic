#!/bin/bash
# Weekly (systemd timer 2min-instagram-refresh): renew the Instagram token and copy it to the GitHub secret IG_TOKEN
# that the daily posting workflow uses. Fails loudly instead of ever saving an empty secret (16 Oct: the old inline
# command saved an empty IG_TOKEN and the cloud post failed).
set -euo pipefail
cd "$(dirname "$0")/.."
LOG=~/.local/share/2min-yt/instagram.log
python3 tools/instagram_api.py refresh >> "$LOG" 2>&1
TOK=$(python3 -c "import json;print(json.load(open('$HOME/.config/2min-instagram/token.json'))['access_token'])")
[ ${#TOK} -gt 50 ] || { echo "[$(date '+%F %T')] token looks wrong (${#TOK} chars) — GitHub secret NOT updated" >> "$LOG"; exit 1; }
printf '%s' "$TOK" | gh secret set IG_TOKEN -R muhannadsnan/2min-arabic
echo "[$(date '+%F %T')] GitHub secret IG_TOKEN updated (${#TOK} chars)" >> "$LOG"
