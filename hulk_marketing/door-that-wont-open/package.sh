#!/bin/bash
# package.sh: final picture + master mix -> reel/hulk_marketing/ (run from hulk_marketing/ after the render and audio/mix.py)
#   bash door-that-wont-open/package.sh
set -euo pipefail
F=door-that-wont-open
V=out/$F/video_9x16.mp4
OUT=../reel/hulk_marketing
NAME=hulk_door_that_wont_open
COVER_T=${COVER_T:-5.9}
mkdir -p "$OUT/stems"
# reel with voiceover (primary) and a music + SFX version for captions-only use
ffmpeg -v error -y -i "$V" -i $F/audio/mix.wav -map 0:v -map 1:a -c:v copy -c:a aac -b:a 320k -ar 48000 -shortest \
  -movflags +faststart -metadata title="The Door That Won't Open - Hulk Marketing" "$OUT/${NAME}_9x16.mp4"
ffmpeg -v error -y -i "$V" -i $F/audio/mix_novo.wav -map 0:v -map 1:a -c:v copy -c:a aac -b:a 320k -ar 48000 -shortest \
  -movflags +faststart -metadata title="The Door That Won't Open - Hulk Marketing (no voiceover)" "$OUT/${NAME}_9x16_no_vo.mp4"
# cover frame, taken from the encoded file itself
ffmpeg -v error -y -ss "$COVER_T" -i "$OUT/${NAME}_9x16.mp4" -frames:v 1 -q:v 2 "$OUT/${NAME}_cover.jpg"
# stems at the master's level (48 kHz, 24-bit)
for s in vo music sfx; do cp $F/audio/stems/${s}_stem.wav "$OUT/stems/${NAME}_${s}_stem.wav"; done
for f in "$OUT/${NAME}_9x16.mp4" "$OUT/${NAME}_9x16_no_vo.mp4"; do
  echo "$f"
  ffprobe -v error -show_entries format=duration,size,bit_rate:stream=codec_name,width,height,r_frame_rate,nb_frames,pix_fmt,sample_rate,channels \
    -of default=nw=1 "$f" | tr '\n' ' '; echo
  ffmpeg -hide_banner -nostats -i "$f" -vn -af ebur128=peak=true -f null - 2>&1 | grep -E "^\s+(I|Peak):" | tr -s ' ' | tr '\n' ' '; echo
done
ls -la "$OUT" "$OUT/stems"
