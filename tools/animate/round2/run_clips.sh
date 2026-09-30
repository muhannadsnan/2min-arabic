#!/usr/bin/env bash
# 2 seeds per entrance: seed 11 at 73 frames (3 s), seed 12 at 49 frames (2 s). 576x1024, 20 steps.
cd "$(dirname "$0")"
for e in ${ENTRANCES:-C A B}; do
  img=$(python3 -c "import json;print(json.load(open('prompts.json'))['$e']['key'])")
  p=$(python3 -c "import json;print(json.load(open('prompts.json'))['$e']['p'])")
  for sf in "11 73" "12 49"; do
    set -- $sf; out="clips/${e}_s$1_$2f.mp4"; [ -f "$out" ] && continue
    python3 ../animate.py "$img" "$out" --prompt "$p" --seed $1 --frames $2 --width 576 --height 1024 --look 3d || echo "FAIL $out"
  done
done
echo CLIPS_DONE
