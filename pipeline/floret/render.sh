#!/bin/bash
# Full Floret render: wait for Blender, audio, 60 fps chunks, mux, delivery encodes.
cd "$(dirname "$0")"
W=../../workspace4
LOG=$W/work/render.log
until grep -q ALLDONE $W/work/b3d.log; do sleep 10; done
echo "$(date -u +%H:%M:%S) START" >> $LOG
python3 audio_floret.py >> $LOG 2>&1
python3 floret.py render 4 >> $LOG 2>&1
mkdir -p $W/out
ffmpeg -y -v error -i $W/work/video.mp4 -i $W/work/audio.wav -map 0:v -map 1:a -c:v copy -c:a aac -b:a 320k \
  -movflags +faststart -shortest $W/out/floret_capitals_master.mp4
ffmpeg -y -v error -i $W/out/floret_capitals_master.mp4 -c:v libx264 -preset slow -crf 16 -maxrate 25M -bufsize 50M \
  -pix_fmt yuv420p -c:a aac -b:a 256k -movflags +faststart $W/out/floret_capitals_social.mp4
ffmpeg -y -v error -i $W/out/floret_capitals_master.mp4 -c:v libx264 -b:v 5800k -pass 1 -passlogfile $W/work/p2 -preset slow -an -f mp4 /dev/null && \
ffmpeg -y -v error -i $W/out/floret_capitals_master.mp4 -c:v libx264 -b:v 5800k -pass 2 -passlogfile $W/work/p2 -preset slow \
  -c:a aac -b:a 192k -movflags +faststart $W/out/floret_capitals_chat.mp4
echo "$(date -u +%H:%M:%S) FINISHED" >> $LOG
