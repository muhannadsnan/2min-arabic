#!/usr/bin/env bash
# review.sh CLIP.mp4 -> review/<name>_strip.png : every 6th frame with frame number, 8 per row
in="$1"; b=$(basename "${in%.mp4}")
ffmpeg -loglevel error -y -i "$in" -vf "select='not(mod(n\,6))',scale=240:-2,drawtext=text='%{n}':x=4:y=4:fontsize=22:fontcolor=white:box=1:boxcolor=black,tile=7x2:padding=2" -fps_mode vfr -frames:v 1 "review/${b}_strip.png"
echo "review/${b}_strip.png"
