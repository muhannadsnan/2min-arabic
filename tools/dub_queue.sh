#!/bin/bash
# All audio tracks, one GPU job at a time; skips tracks already made. Usage: tools/dub_queue.sh <stem> … (default: every dubs/*.json)
cd "$(dirname "$0")/.." || exit 1
TTS=/media/msn/GamesLinux/AI/tts/venv/bin/python; LOG=output/dub-queue.log
stems=("$@"); [ ${#stems[@]} -eq 0 ] && stems=($(ls dubs/*.json | xargs -n1 basename | sed 's/\.json$//'))
for s in "${stems[@]}"; do for l in fr tr es hi id; do
  [ -s "output/$s/dub-$l.m4a" ] && continue
  echo "=== $s $l $(date +%T)" >> "$LOG"
  $TTS tools/dub_track.py "dubs/$s.json" "$l" 2>&1 | grep -v -i warn | tail -25 >> "$LOG"
done; done
echo "=== ALL DONE $(date +%T)" >> "$LOG"
