#!/bin/bash
# Final plate renders for Yaadein (sequential: Cycles already uses every core).
cd "$(dirname "$0")"
LOG=../../workspace2/work/render_queue.log
mkdir -p ../../workspace2/work
run() { echo "$(date -u +%H:%M:%S) START $*" >> $LOG
        env "$@" >> ../../workspace2/work/render_detail.log 2>&1
        echo "$(date -u +%H:%M:%S) END($?) $*" >> $LOG; }
S="RES=1.0 SAMPLES=24"
run $S LAYERS=full python3 film.py c2_mj_portrait
run $S LAYERS=full python3 film.py a1_mask
run $S LAYERS=bg,hero,fg python3 film.py a2_reveal
run $S LAYERS=full python3 film.py b2_hands
run $S LAYERS=full python3 film.py b1_frame
run $S LAYERS=bg,hero,fg python3 film.py c1_temple
run $S LAYERS=full python3 film.py e3_kneel
run $S LAYERS=full python3 film.py d4_goblin
run $S LAYERS=bg,hero,fg python3 film.py f1_grave
run $S LAYERS=full python3 film.py f2_rose
run $S LAYERS=full python3 film.py a4_wide
A="RES=0.6 SAMPLES=16 STEP=2"
run $A python3 film.py d2_dagger
run $A python3 film.py e1_bomb
run $A python3 film.py d1_lasso
run $A python3 film.py logo_spin
run $A python3 film.py c3_together
run $A python3 film.py g1_sunrise
echo "$(date -u +%H:%M:%S) ALLDONE" >> $LOG
