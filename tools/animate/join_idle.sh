#!/bin/bash
# join.sh action.mp4 idle.mp4 out.mp4 [speed] — action (optionally slowed, motion-interpolated) + idle forward/back,
# 3-frame blend at the join, light temporal smoothing (Wan's 4-frame chunk stutter), 60-fps master → 30 fps.
A=$1; I=$2; OUT=$3; SP=${4:-1.0}
T=$(mktemp -d)
ffmpeg -v error -y -i "$A" -vf "fps=24,setpts=PTS/$SP,minterpolate=fps=24:mi_mode=mci:mc_mode=aobmc:me_mode=bidir:vsbmc=1" -c:v libx264 -crf 12 $T/a.mp4
DUR=$(ffprobe -v error -show_entries format=duration -of csv=p=0 $T/a.mp4)
OFF=$(python3 -c "print(round($DUR-0.125-1/24,3))")
ffmpeg -v error -y -i $T/a.mp4 -i "$I" -filter_complex \
 "[0:v]fps=24,setsar=1,format=yuv420p,settb=1/24[a];[1:v]fps=24,setsar=1,format=yuv420p,split[i1][i2];[i2]reverse,trim=start_frame=1,setpts=PTS-STARTPTS[ir];[i1][ir]concat=n=2:v=1:a=0,fps=24,settb=1/24[idle];[a][idle]xfade=transition=fade:duration=0.125:offset=$OFF,tmix=frames=3:weights='1 3 1',minterpolate=fps=60:mi_mode=mci:mc_mode=aobmc:me_mode=bidir:vsbmc=1,fps=30,scale=1080:1920:flags=lanczos,format=yuv420p" \
 -an -c:v libx264 -crf 17 "$OUT"
rm -rf $T
