#!/usr/bin/env bash
# finish.sh CLIP.mp4 -> CLIP_1080x1920.mp4 (upscaled, cover-cropped to 9:16) + CLIP_sheet.png (6 frames)
set -euo pipefail
in="$1"; base="${in%.mp4}"
ffmpeg -loglevel error -y -i "$in" \
  -vf "scale=1080:1920:force_original_aspect_ratio=increase:flags=lanczos,crop=1080:1920,setsar=1,fps=30" \
  -c:v libx264 -crf 18 -preset slow -pix_fmt yuv420p -movflags +faststart -an "${base}_1080x1920.mp4"
n=$(ffprobe -v error -count_frames -select_streams v:0 -show_entries stream=nb_read_frames -of csv=p=0 "$in")
sel=""; for k in 0 1 2 3 4 5; do f=$(( k * (n - 1) / 5 )); sel="${sel}eq(n\,$f)+"; done; sel="${sel%+}"
ffmpeg -loglevel error -y -i "$in" \
  -vf "select='$sel',scale=360:-2,drawtext=text='%{pts}s':x=8:y=8:fontsize=22:fontcolor=white:box=1:boxcolor=black@0.5,tile=6x1:padding=4:color=white" \
  -fps_mode vfr -frames:v 1 "${base}_sheet.png"
echo "$n frames -> ${base}_1080x1920.mp4 ${base}_sheet.png"
