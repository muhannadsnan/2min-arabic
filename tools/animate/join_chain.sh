#!/bin/bash
# join_chain.sh out.mp4 part1.mp4 part2.mp4 … — one continuous take from chained Wan parts (each part was generated
# from the previous part's last frame): the first frame of every later part (= the previous last frame) is dropped,
# then the whole take is motion-interpolated once (60 fps master → 30 fps) at REAL speed — no slow-down, no loop.
OUT=$1; shift
T=$(mktemp -d); i=0; : > $T/list.txt
for p in "$@"; do
  if [ $i -eq 0 ]; then ffmpeg -v error -y -i "$p" -vf "fps=24" -c:v libx264 -crf 10 $T/$i.mp4
  else ffmpeg -v error -y -i "$p" -vf "fps=24,trim=start_frame=1,setpts=PTS-STARTPTS" -c:v libx264 -crf 10 $T/$i.mp4; fi
  echo "file '$T/$i.mp4'" >> $T/list.txt; i=$((i+1))
done
ffmpeg -v error -y -f concat -safe 0 -i $T/list.txt -vf "fps=24,tmix=frames=3:weights='1 4 1',minterpolate=fps=60:mi_mode=mci:mc_mode=aobmc:me_mode=bidir:vsbmc=1,fps=30,scale=1080:1920:flags=lanczos,format=yuv420p" -an -c:v libx264 -crf 15 "$OUT"
rm -rf $T; echo "$OUT $(ffprobe -v error -show_entries format=duration -of csv=p=0 "$OUT")s"
