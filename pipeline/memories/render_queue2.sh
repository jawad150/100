#!/bin/bash
# v2 animated hero shots (real camera motion + Cycles motion blur), then the full 60 fps composite + mix.
cd "$(dirname "$0")"
W=../../workspace2
LOG=$W/work/render_queue2.log
run() { echo "$(date -u +%H:%M:%S) START $*" >> $LOG; env "$@" >> $W/work/render_detail2.log 2>&1; echo "$(date -u +%H:%M:%S) END($?) $*" >> $LOG; }
[ -f $W/plates3/h1_hook/0131.png ] || run RES=0.75 SAMPLES=20 STEP=2 python3 film.py h1_hook
[ -f $W/plates3/e3_anim/0089.png ] || run RES=0.65 SAMPLES=16 STEP=2 python3 film.py e3_anim
[ -f $W/plates3/f1_anim/0089.png ] || run RES=0.65 SAMPLES=16 STEP=2 python3 film.py f1_anim
echo "$(date -u +%H:%M:%S) PLATES DONE" >> $LOG
python3 reel.py cues >> $LOG 2>&1
python3 sound.py $W/work/cues.json 32 >> $LOG 2>&1
mkdir -p $W/work/chunks
python3 -c "
import sys; sys.path.insert(0, '.')
from multiprocessing import Pool
import reel as R
jobs = [(ci, ci * 60, min(R.NF, ci * 60 + 60)) for ci in range((R.NF + 59) // 60)]
with Pool(4) as p:
    list(p.imap_unordered(R._chunk, jobs))
" >> $LOG 2>&1
ls $W/work/chunks/c*.mp4 | grep -v part | sort | sed "s|^|file '$(pwd)/|; s|$|'|" > $W/work/chunks/list.txt
ffmpeg -y -v error -f concat -safe 0 -i $W/work/chunks/list.txt -c copy $W/work/video_60.mp4
ffmpeg -y -v error -i $W/work/video_60.mp4 -i $W/out/audio.wav -map 0:v -map 1:a -c:v copy -c:a aac -b:a 320k \
  -movflags +faststart -shortest $W/out/yaadein_reel_60fps.mp4
echo "$(date -u +%H:%M:%S) FINISHED" >> $LOG
