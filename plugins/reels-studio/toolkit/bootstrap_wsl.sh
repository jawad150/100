#!/usr/bin/env bash
# One-shot setup of the Organic Fostering reel pipeline on a PC running WSL2 Ubuntu (or plain Ubuntu).
#
#   bash pipeline/fostering/bootstrap_wsl.sh [--no-footage] [--no-videos] [--render-3d]
#
# Run it from inside the cloned repo. It installs system tools, Python 3.13 + packages (Blender bpy 5.2),
# fonts/logo/website photos (+ the client's Drive footage unless --no-footage), the 3D prop library
# (from the Git LFS backup, or re-rendered on the GPU with --render-3d), Claude Code, and on WSL a
# .wslconfig that gives Linux most of your RAM. Safe to run again: finished steps are skipped.
# What it can't do for you: the NVIDIA driver (Windows), `wsl --install` + reboot, and browser sign-ins.
set -euo pipefail

FOOTAGE=1; VIDEOS=1; RENDER3D=0
for a in "$@"; do
  case "$a" in
    --no-footage) FOOTAGE=0 ;;
    --no-videos) VIDEOS=0 ;;
    --render-3d) RENDER3D=1 ;;
    *) echo "unknown option: $a"; exit 2 ;;
  esac
done

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$REPO"
say() { printf '\n\033[1;35m==> %s\033[0m\n' "$*"; }

case "$REPO" in /mnt/*) echo "WARNING: the repo is on the Windows drive ($REPO); clone it into ~ for 5-10x faster renders." ;; esac

say "System tools (sudo password needed once)"
sudo apt-get update -y
sudo apt-get install -y git git-lfs ffmpeg libcairo2 curl gh ca-certificates
git lfs install --skip-repo >/dev/null

if [ "$VIDEOS" = 1 ]; then
  say "Git LFS: finished videos + 3D prop backup"
  git lfs pull --include="reel/organic_fostering/*,media/fostering/*" || echo "(LFS pull skipped: run 'gh auth login && gh auth setup-git' and retry)"
else
  git lfs pull --include="media/fostering/*" || true
fi

say "Python 3.13 + packages (uv)"
if ! command -v uv >/dev/null 2>&1; then
  curl -LsSf https://astral.sh/uv/install.sh | sh
  export PATH="$HOME/.local/bin:$PATH"
fi
[ -x .venv/bin/python ] || uv venv --python 3.13 .venv
# shellcheck disable=SC1091
source .venv/bin/activate
uv pip install bpy==5.2.2 numpy opencv-python-headless pillow scipy cairosvg fonttools imageio-ffmpeg
python -c "import bpy, cv2, cairosvg; print('Blender', bpy.app.version_string, '| OpenCV', cv2.__version__)"
LINE="cd $REPO && source .venv/bin/activate"
grep -qxF "$LINE" ~/.bashrc || echo "$LINE" >> ~/.bashrc

say "Fonts, logo variants, website photos$( [ "$FOOTAGE" = 1 ] && echo ', Drive footage' )"
( cd pipeline/fostering && python setup_workspace.py $( [ "$FOOTAGE" = 1 ] && echo --footage ) )

GPU=0
if command -v nvidia-smi >/dev/null 2>&1 && nvidia-smi -L >/dev/null 2>&1; then
  GPU=1; nvidia-smi -L
  grep -qxF "export FOSTER_GPU=1" ~/.bashrc || echo "export FOSTER_GPU=1" >> ~/.bashrc
  export FOSTER_GPU=1
else
  echo "No NVIDIA GPU visible here (update the Windows NVIDIA driver); Blender will render on the CPU."
fi

say "3D prop library"
if [ "$RENDER3D" = 0 ] && [ -f media/fostering/assets3d.tar ] && [ "$(stat -c %s media/fostering/assets3d.tar)" -gt 100000 ]; then
  mkdir -p workspace3 && tar -xf media/fostering/assets3d.tar -C workspace3/ && echo "restored from media/fostering/assets3d.tar"
else
  ( cd pipeline/fostering
    python assets3d_icons.py heart house coin_gbp shield_check grad_cap chat_bubble key_heart check_tile star_badge orbs pin_phone
    python assets3d_hero.py logo_mark3d question pound_glyph sprout leaf seed puzzle_pair blocks
    [ -f assets3d_everyday.py ] && python assets3d_everyday.py
    [ -f assets3d_household.py ] && python assets3d_household.py ) || echo "(some 3D renders failed; re-run with --render-3d)"
fi

say "Claude Code"
if ! command -v claude >/dev/null 2>&1 && [ ! -x "$HOME/.local/bin/claude" ]; then
  curl -fsSL https://claude.ai/install.sh | bash
fi

if grep -qi microsoft /proc/version 2>/dev/null && command -v powershell.exe >/dev/null 2>&1; then
  say "WSL memory (.wslconfig)"
  WINHOME="$(wslpath "$(powershell.exe -NoProfile -Command '$env:USERPROFILE' | tr -d '\r')")"
  if [ -f "$WINHOME/.wslconfig" ]; then
    echo "$WINHOME/.wslconfig already exists; left unchanged:"; cat "$WINHOME/.wslconfig"
  else
    RAM_GB=$(powershell.exe -NoProfile -Command '[math]::Floor((Get-CimInstance Win32_ComputerSystem).TotalPhysicalMemory/1GB)' | tr -d '\r')
    CPUS=$(powershell.exe -NoProfile -Command '[Environment]::ProcessorCount' | tr -d '\r')
    MEM=$(( RAM_GB > 12 ? RAM_GB - 4 : RAM_GB * 3 / 4 )); PROCS=$(( CPUS > 6 ? CPUS - 4 : CPUS ))
    printf '[wsl2]\nmemory=%sGB\nprocessors=%s\nswap=8GB\n' "$MEM" "$PROCS" > "$WINHOME/.wslconfig"
    echo "wrote $WINHOME/.wslconfig (memory=${MEM}GB, processors=${PROCS}). Run 'wsl --shutdown' in PowerShell, then reopen Ubuntu."
  fi
fi

say "Done"
cat <<EOF
GPU for Blender: $( [ "$GPU" = 1 ] && echo yes || echo no )
Next:
  1. claude auth login          (browser sign-in with the same claude.ai account)
  2. cd $REPO && git status     (must be clean)
  3. claude --teleport          (pick the Organic Fostering session), or just: claude
Render example:  cd $REPO/pipeline/fostering && python render.py anim1 --workers 4
EOF
