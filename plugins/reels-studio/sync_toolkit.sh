#!/usr/bin/env bash
# Maintainer script: refresh plugins/reels-studio/toolkit/ from a project's toolkit folder (default
# pipeline/fostering, where the toolkit is developed). Run from the repo root, then commit.
#   bash plugins/reels-studio/sync_toolkit.sh [pipeline/<project>]
set -euo pipefail
SRC=${1:-pipeline/fostering}
DST=plugins/reels-studio/toolkit
[ -f "$SRC/wsconf.py" ] || { echo "no toolkit in $SRC"; exit 1; }

CORE="core.py footage.py type3d.py ui.py sprites3d.py audio.py render.py package.py setup_workspace.py wsconf.py
      assets3d_gpu.py assets3d_icons.py assets3d_hero.py assets3d_everyday.py assets3d_household.py"
mkdir -p "$DST/examples"
for f in $CORE; do cp "$SRC/$f" "$DST/$f"; done
cp "$SRC/TOOLKIT.md" "$SRC/LOCAL_SETUP.md" "$SRC/bootstrap_wsl.sh" "$DST/"

# finished timelines and briefs from earlier projects: reading material, never rendered in a new project
for f in "$SRC"/reel[0-9]*.py "$SRC"/anim[0-9]*.py "$SRC"/reel_demo.py "$SRC"/demo_looks.py "$SRC"/BRIEF*.md; do
  [ -e "$f" ] && cp "$f" "$DST/examples/"
done
cat > "$DST/examples/README.md" <<'EOF'
# Examples (read, don't render)

Finished timelines from the Organic Fostering project, the first client built with this toolkit:

| files | piece | look |
|---|---|---|
| reel1*.py | "Could you?" 26 s, footage montage hook, 3D type, orbit tags | night neon |
| reel2*.py | Financial support 24 s, glass dashboard, counters, coins | amber dashboard |
| reel3*.py | Nurture / develop / grow 26 s, organic light, growth devices | light organic |
| anim1*.py | Day in the Life 21 s, pure animation on relit crumpled paper | editorial paper |
| anim4*.py | £447.60 where does it go 25 s, money stream through scenes | clean SaaS light |
| reel_demo.py, demo_looks.py | 3 s end-to-end render test and the look gallery | all |
| BRIEF.md, BRIEF2.md | the briefs those pieces were built from: a model for new briefs | |

Their copy, figures, footage and brand belong to that client. Reuse patterns (module contract, camera tracks,
transitions, samples() windows, cue sheets, `_fx` / `_sfx` / `_dev` helper split), never content.
They import the toolkit by name, so to run one for study, copy it next to the toolkit with that client's workspace.
EOF
echo "toolkit -> $DST"; ls "$DST" "$DST/examples" | tr '\n' ' '; echo
du -sh "$DST"
