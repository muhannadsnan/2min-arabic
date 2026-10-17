#!/bin/bash
# loop_xfade.sh raw.mp4 out-loop.mp4 [speed=0.85] [xf=0.6]
# A talking/idle loop at ONE constant speed (owner, 2026-10-17: the pendulum loop sped up and slowed down at every
# turn): forward only, the last XF s cross-faded into the first XF s, so repeating it is seamless. 60-fps motion-
# interpolated master → 30 fps, light 3-frame smoothing against Wan's chunk stutter.
RAW=$1; OUT=$2; SP=${3:-0.85}; XF=${4:-0.6}
T=$(mktemp -d)
ffmpeg -v error -y -i "$RAW" -vf "fps=24,setpts=PTS/$SP,tmix=frames=3:weights='1 3 1',minterpolate=fps=60:mi_mode=mci:mc_mode=aobmc:me_mode=bidir:vsbmc=1,fps=30,setsar=1,format=yuv420p" -an -c:v libx264 -crf 12 $T/m.mp4
D=$(ffprobe -v error -show_entries format=duration -of csv=p=0 $T/m.mp4)
read LA OFF < <(python3 -c "d=$D;x=$XF;print(round(d-x,3),round(d-2*x,3))")
ffmpeg -v error -y -i $T/m.mp4 -filter_complex "[0:v]split[a][b];[a]trim=start=$XF,setpts=PTS-STARTPTS,settb=1/30[A];[b]trim=end=$XF,setpts=PTS-STARTPTS,settb=1/30[B];[A][B]xfade=transition=fade:duration=$XF:offset=$OFF,scale=1080:1920:flags=lanczos,format=yuv420p" -an -c:v libx264 -crf 15 "$OUT"
rm -rf $T
echo "$OUT $(ffprobe -v error -show_entries format=duration -of csv=p=0 "$OUT")s loop"
