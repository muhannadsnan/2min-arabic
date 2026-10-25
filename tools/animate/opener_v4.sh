#!/bin/bash
# opener_v4.sh away.mp4 still.png out.mp4 — owner's opener shape (2026-10-25):
# the clip was animated FROM the high-quality still with the opposite movement (looks down / away); here it is played
# BACKWARDS and slowed to ~3 s (motion-interpolated), so the action ends exactly on the still. No fades, no idle part.
# In prompts.json: {"s": 1, "clip": "openers/<name>", "hold": 0, "shift": 0} and images/<video>/s01.png = the still
# (assemble.py cuts from the clip's last frame to the still — the same picture, sharper).
A=$1; STILL=$2; OUT=$3
ffmpeg -v error -y -i "$A" -vf "reverse,setpts=PTS/0.667,minterpolate=fps=30:mi_mode=mci:mc_mode=aobmc:me_mode=bidir:vsbmc=1,scale=1080:1920:flags=lanczos,format=yuv420p" -an -c:v libx264 -crf 14 "$OUT"
echo "$OUT $(ffprobe -v error -show_entries format=duration -of csv=p=0 "$OUT")s · still: $STILL"
