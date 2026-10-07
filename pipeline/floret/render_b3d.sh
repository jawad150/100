#!/bin/bash
# Render every Blender element sequence (skips frames already on disk).
cd "$(dirname "$0")"
LOG=../../workspace4/work/b3d.log
for j in logo goldbar silverbar barrel coin shield; do
  echo "$(date -u +%H:%M:%S) START $j" >> $LOG
  python3 b3d.py $j >> ../../workspace4/work/b3d_detail.log 2>&1
  echo "$(date -u +%H:%M:%S) END $j" >> $LOG
done
echo "$(date -u +%H:%M:%S) ALLDONE" >> $LOG
