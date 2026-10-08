#!/usr/bin/env bash
# Global CPU semaphore for the shared 4-core box: at most 2 heavy jobs (Blender, render.py, music
# generation, whisper on long files) run at once across ALL agents. Usage:
#   pipeline/jawad_reels/tools/heavy.sh <command> [args...]
# The command runs under nice -n 10 with OMP/MKL/OPENBLAS threads capped at 2.
set -u
LOCKDIR=/home/user/100/workspace/jawad_reels/locks
mkdir -p "$LOCKDIR"
export OMP_NUM_THREADS=2 MKL_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2 NUMEXPR_NUM_THREADS=2
while true; do
  for slot in 1 2; do
    flock -n -E 75 "$LOCKDIR/slot$slot" nice -n 10 "$@"
    rc=$?
    if [ $rc -ne 75 ]; then exit $rc; fi
  done
  sleep 5
done
