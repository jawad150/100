#!/bin/bash
# After the plate queue: rebuild cue sheet + mix, composite the 60 fps reel, mux the final file.
cd "$(dirname "$0")"
W=../../workspace2
until grep -q ALLDONE $W/work/render_queue.log 2>/dev/null; do sleep 30; done
while pgrep -f "reel.py preview" > /dev/null; do sleep 10; done
# cut-out layers rendered before the fog fix
RES=1.0 SAMPLES=24 LAYERS=hero,fg python3 film.py a2_reveal >> $W/work/render_detail.log 2>&1
RES=1.0 SAMPLES=24 LAYERS=hero,fg python3 film.py c1_temple >> $W/work/render_detail.log 2>&1
echo "$(date -u +%H:%M:%S) re-rendered a2/c1 cut-outs" >> $W/work/finish.log
echo "$(date -u +%H:%M:%S) composite start" >> $W/work/finish.log
rm -rf $W/work/chunks
python3 reel.py cues >> $W/work/finish.log 2>&1
python3 sound.py $W/work/cues.json 32 >> $W/work/finish.log 2>&1
python3 reel.py render 4 >> $W/work/finish.log 2>&1
mkdir -p $W/out
ffmpeg -y -v error -i $W/work/video_60.mp4 -i $W/out/audio.wav -map 0:v -map 1:a -c:v copy -c:a aac -b:a 320k \
  -movflags +faststart -shortest $W/out/yaadein_reel_60fps.mp4 >> $W/work/finish.log 2>&1
echo "$(date -u +%H:%M:%S) FINISHED $(ls -la $W/out/yaadein_reel_60fps.mp4)" >> $W/work/finish.log
