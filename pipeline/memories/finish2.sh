#!/bin/bash
# Resume: wait for the mid chunks, render the rest (incl. the new end card), concat + mux the final reel.
cd "$(dirname "$0")"
W=../../workspace2
S=/tmp/claude-0/-home-user-100/10e3f559-562e-5998-b4c9-35a1ddb64a00/scratchpad/chunks_run.py
while pgrep -f "chunks_run.py 10 24" > /dev/null; do sleep 5; done
python3 $S 24 54 >> $W/work/chunks_end.log 2>&1
ls $W/work/chunks/c0*.mp4 | sort | sed "s|^|file '$(pwd)/|; s|$|'|" > $W/work/chunks/list.txt
ffmpeg -y -v error -f concat -safe 0 -i $W/work/chunks/list.txt -c copy $W/work/video_60.mp4
ffmpeg -y -v error -i $W/work/video_60.mp4 -i $W/out/audio.wav -map 0:v -map 1:a -c:v copy -c:a aac -b:a 320k \
  -movflags +faststart -shortest $W/out/yaadein_reel_60fps.mp4
echo "$(date -u +%H:%M:%S) FINISHED" >> $W/work/finish.log
