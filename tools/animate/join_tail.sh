#!/bin/bash
# join_tail.sh action.mp4 out.mp4 [tail_frames] — for openers that END in a held pose (raised hand, finger, thumbs-up):
# the AI idle smears a raised hand (2026-10-16, Day 18), so the hold is the clip's own last frames rocking gently
# back and forth at half speed (pendulum, eased by the 60-fps interpolation) — real frames, sharp hands, no freeze.
A=$1; OUT=$2; N=${3:-10}
ffmpeg -v error -y -i "$A" -filter_complex \
 "[0:v]fps=24,setsar=1,format=yuv420p,split=2[a][t];[t]reverse,trim=end_frame=$N,setpts=PTS-STARTPTS,split=2[r1][r2];[r1]setpts=2*PTS[back];[r2]reverse,setpts=2*PTS,split=2[f1][f2];[back]split=2[b1][b2];[a][b1][f1][b2][f2]concat=n=5:v=1:a=0,tmix=frames=3:weights='1 3 1',minterpolate=fps=60:mi_mode=mci:mc_mode=aobmc:me_mode=bidir:vsbmc=1,fps=30,scale=1080:1920:flags=lanczos,format=yuv420p" \
 -an -c:v libx264 -crf 17 "$OUT"
