#!/usr/bin/env bash
# make_opener.sh CLIP.mp4 NAME [START_S] [END_S]
#   -> ../library/openers/NAME.mp4       the clean part, 1080x1920, 30 fps (plays once: the entrance)
#   -> ../library/openers/NAME-loop.mp4  seamless ping-pong loop (forward + reversed), 1080x1920, 30 fps
#   -> ../library/openers/NAME_sheet.png 6 frames of the clean part
set -euo pipefail
in="$1"; name="$2"; ss="${3:-0}"; to="${4:-99}"
lib="$(dirname "$0")/../library/openers"; mkdir -p "$lib"
up="scale=1080:1920:force_original_aspect_ratio=increase:flags=lanczos,crop=1080:1920,setsar=1"
enc=(-c:v libx264 -crf 18 -preset slow -pix_fmt yuv420p -movflags +faststart -an)
# 1) clean part, upscaled; 24 -> 30 fps by repeating frames (blend interpolation ghosted the waving hand)
ffmpeg -loglevel error -y -i "$in" -vf "trim=start=$ss:end=$to,setpts=PTS-STARTPTS,$up,fps=30" \
  "${enc[@]}" "$lib/$name.mp4"
# 2) ping-pong loop: forward, then reversed without its first and last frame (no stutter at either turn)
n=$(ffprobe -v error -count_frames -select_streams v:0 -show_entries stream=nb_read_frames -of csv=p=0 "$lib/$name.mp4")
ffmpeg -loglevel error -y -i "$lib/$name.mp4" -filter_complex \
  "[0]split[f][b];[b]reverse,trim=start_frame=1:end_frame=$((n-1)),setpts=PTS-STARTPTS[r];[f][r]concat=n=2:v=1[v]" \
  -map "[v]" "${enc[@]}" "$lib/$name-loop.mp4"
# 3) contact sheet, 6 evenly spaced frames of the clean part
sel=""; for k in 0 1 2 3 4 5; do f=$(( k * (n - 1) / 5 )); sel="${sel}eq(n\,$f)+"; done; sel="${sel%+}"
ffmpeg -loglevel error -y -i "$lib/$name.mp4" \
  -vf "select='$sel',scale=360:-2,drawtext=text='%{pts}s':x=8:y=8:fontsize=22:fontcolor=white:box=1:boxcolor=black@0.5,tile=6x1:padding=4:color=white" \
  -fps_mode vfr -frames:v 1 "$lib/${name}_sheet.png"
for f in "$lib/$name.mp4" "$lib/$name-loop.mp4"; do
  echo "$f $(ffprobe -v error -show_entries format=duration -of csv=p=0 "$f")s"
done
