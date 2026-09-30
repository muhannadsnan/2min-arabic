#!/usr/bin/env bash
# 3 takes per keyframe via tools/images/generate.py (FLUX.2 klein 4B, character ref, 3D style instead of flat vector)
cd "$(dirname "$0")"; R="../../.."
for key in ${KEYS:-A_sami_peek B_sami_cup C_lina_notebook}; do
  read -r ref prompt < <(python3 -c "import json,sys;d=json.load(open('keyframes.json'));k=d['$key'];print(k['ref'], k['p'].rstrip('. ')+'. '+d['style'])")
  for k in 0 1 2; do
    out="keyframes/${key}_$k.png"; [ -f "$out" ] && continue
    python3 "$R/tools/images/generate.py" "$prompt" "$out" --no-style --seed $((700+k)) --ref "$R/assets/characters/$ref.png" || echo "FAIL $out"
  done
done
echo KEYFRAMES_DONE
