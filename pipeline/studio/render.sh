#!/bin/bash
# Full 60 fps render + audio mux + delivery encodes for the studio reel.
cd "$(dirname "$0")"
W=../../workspace3
LOG=$W/work/render.log
echo "$(date -u +%H:%M:%S) START" >> $LOG
python3 studio.py sound >> $LOG 2>&1
python3 studio.py render 4 >> $LOG 2>&1
mkdir -p $W/out
ffmpeg -y -v error -i $W/work/video_60.mp4 -i $W/work/audio.wav -map 0:v -map 1:a -c:v copy -c:a aac -b:a 320k \
  -movflags +faststart -shortest $W/out/studio_reel_master.mp4
ffmpeg -y -v error -i $W/out/studio_reel_master.mp4 -c:v libx264 -preset slow -crf 16 -maxrate 25M -bufsize 50M \
  -pix_fmt yuv420p -c:a aac -b:a 256k -movflags +faststart $W/out/studio_reel_instagram.mp4
ffmpeg -y -v error -i $W/out/studio_reel_master.mp4 -c:v libx264 -b:v 5600k -pass 1 -passlogfile $W/work/p2 -preset slow -an -f mp4 /dev/null && \
ffmpeg -y -v error -i $W/out/studio_reel_master.mp4 -c:v libx264 -b:v 5600k -pass 2 -passlogfile $W/work/p2 -preset slow \
  -c:a aac -b:a 192k -movflags +faststart $W/out/studio_reel_chat.mp4
echo "$(date -u +%H:%M:%S) FINISHED" >> $LOG
