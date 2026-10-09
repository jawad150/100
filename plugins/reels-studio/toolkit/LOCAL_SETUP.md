# Continue the Organic Fostering reels on your own PC

These steps were written for a Windows PC (Intel i9 14th gen, RTX 4060, 16 GB RAM) running WSL2 with Ubuntu 24.04.

**What runs where:**
- **Anthropic's cloud:** Claude itself (the AI model).
- **Your PC:** everything Claude runs: Blender (GPU), the frame compositor (CPU and RAM), ffmpeg and git.

**Project:** repo `github.com/jawad150/100`, branch `claude/festive-lovelace-6gletw`. You'll need about 40 GB of free disk.

## Fast path: one script does steps 5–10
Do steps 1–4 by hand first (driver, WSL and reboot). Then, in Ubuntu:
```bash
sudo apt update && sudo apt install -y gh git git-lfs
gh auth login && gh auth setup-git
cd ~ && gh repo clone jawad150/100 && cd 100 && git checkout claude/festive-lovelace-6gletw
bash pipeline/fostering/bootstrap_wsl.sh      # --no-footage skips the Drive clips; --render-3d re-renders props
claude auth login && claude --teleport
```
The script is safe to re-run; it skips finished steps. If `.wslconfig` is missing, it also writes one sized to your RAM. In that case run `wsl --shutdown` once afterwards.

## 1. Let the cloud work finish
1. Wait until the cloud session says its work is rendered and pushed.
2. Ask it to *"push everything, including the 3D render backup"*. The 3D renders are git-ignored, so they're backed up as `media/fostering/assets3d.tar` in Git LFS.

Teleport carries the conversation and the branch, not running agents or unpushed files.

## 2. Update the NVIDIA driver (Windows)
Install the latest Studio or Game Ready driver. In PowerShell, `nvidia-smi` should list the RTX 4060.

Don't install a separate NVIDIA driver inside Ubuntu.

## 3. Install WSL2 with Ubuntu (PowerShell as Administrator)
```powershell
wsl --install -d Ubuntu-24.04
wsl --update
```
Reboot, open **Ubuntu** from the Start menu, and create a Linux user.

## 4. Give WSL more RAM and cores
Create `C:\Users\<you>\.wslconfig`:
```ini
[wsl2]
memory=12GB
processors=28
swap=8GB
```
Then run `wsl --shutdown` in PowerShell and reopen Ubuntu. `free -g` should show about 12 GB.

## 5. Install system tools (Ubuntu)
```bash
sudo apt update
sudo apt install -y git git-lfs ffmpeg libcairo2 curl gh
git lfs install
nvidia-smi        # the GPU should be visible inside Ubuntu
```

## 6. Sign in to GitHub and clone
Use a GitHub account with read and write access to `jawad150/100`.
```bash
gh auth login && gh auth setup-git
cd ~ && gh repo clone jawad150/100 && cd 100
git checkout claude/festive-lovelace-6gletw
```
Keep the repo in `~/100`, not under `/mnt/c`, which is much slower.

The clone pulls about 1.5 GB of master videos. To skip them, clone with `GIT_LFS_SKIP_SMUDGE=1 gh repo clone jawad150/100`, then fetch only what you need with `git lfs pull --include="reel/organic_fostering/*"`.

## 7. Python 3.13 and packages
`bpy` 5.2 needs exactly Python 3.13.
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh && source ~/.bashrc
cd ~/100 && uv venv --python 3.13 .venv && source .venv/bin/activate
uv pip install bpy==5.2.2 numpy opencv-python-headless pillow scipy cairosvg fonttools imageio-ffmpeg
python -c "import bpy, cv2, cairosvg; print('Blender', bpy.app.version_string)"
```
Every new terminal needs `cd ~/100 && source .venv/bin/activate`.

## 8. Fonts, logo, website photos and footage
```bash
cd ~/100/pipeline/fostering
python setup_workspace.py --footage
```
Drop `--footage` if you only work on the animated videos #1 and #4. The Drive folder must stay shared as "Anyone with the link".

## 9. Restore the 3D props
**Option A, fastest:** unpack the backup.
```bash
cd ~/100
git lfs pull --include="media/fostering/*"
mkdir -p workspace3 && tar -xf media/fostering/assets3d.tar -C workspace3/
```

**Option B:** re-render. With `FOSTER_GPU=1` Blender uses the RTX 4060, which is about 10× faster than CPU.
```bash
cd ~/100/pipeline/fostering && export FOSTER_GPU=1
python assets3d_icons.py heart house coin_gbp shield_check grad_cap chat_bubble key_heart check_tile star_badge orbs pin_phone
python assets3d_hero.py logo_mark3d question pound_glyph sprout leaf seed puzzle_pair blocks
python assets3d_everyday.py
python assets3d_household.py
```

## 10. Install Claude Code and sign in
```bash
curl -fsSL https://claude.ai/install.sh | bash && source ~/.bashrc
claude --version
claude auth login
```
`claude auth login` opens a browser. Sign in with the same claude.ai account; no password is typed into the terminal.

Then install the Reels Studio plugin once (the 14 agents and 4 skills for future projects):
```bash
claude plugin marketplace add jawad150/100
claude plugin install reels-studio@jawad-reels --scope user
```
In a new project folder, run `claude` and say *"Start 3 reels for <client website>"*, or `/reels-studio:new-reel-project <slug> <website>`. The README section "Reels Studio" has the full list.

## 11. Bring the cloud conversation to your PC
Teleport needs a clean `git status`, the branch pushed to GitHub, and the same claude.ai account.
```bash
cd ~/100
git status        # must be clean; otherwise: git stash
git fetch
claude --teleport # pick the Organic Fostering session
```
You can also go to claude.ai/code, open the session menu, choose **Open in → Terminal**, and paste the command it copies.

To start fresh instead, run `claude` in `~/100` and say:
> Read pipeline/fostering/BRIEF.md, BRIEF2.md, TOOLKIT.md and the README section "Organic Fostering", then continue the Organic Fostering reels work on this branch. This PC has 16 GB RAM (use --workers 4) and an RTX 4060 (use FOSTER_GPU=1 for Blender).

## 12. Render, check and deliver
```bash
cd ~/100/pipeline/fostering
python render.py anim1 --stills 1.0,8.0,19.0   # full-quality stills
python render.py anim1 --sheet 48              # contact sheet
python render.py anim1 --preview               # fast preview mp4
python render.py anim1 --workers 4             # final master with motion blur and SFX
python package.py anim1 anim1_day_in_the_life --cover 1.5
cd ~/100 && git add reel/organic_fostering && git commit -m "Anim 1 final" && git push
```
- **Modules:** `reel1`, `reel2`, `reel3`, `anim1`, `anim4`.
- **Outputs:** `workspace3/out/<module>/`. Deliverables go to `reel/organic_fostering/`.
- **Windows Explorer path:** `\\wsl.localhost\Ubuntu-24.04\home\<linux user>\100`.

| Task | Cloud (4 cores) | Your PC |
|---|---|---|
| 3D props (~1,000 frames) | ~1.5 h | 10–15 min with `FOSTER_GPU=1` |
| Final render, one 26 s reel | 13–15 min | 4–6 min (`--workers 4`) |
| Encodes | ~5 min | 1–2 min |
| Claude's own thinking | same | same |

Keep `--workers 4` with 16 GB of RAM. With 32 GB you can run 8–10 workers.

## 13. Troubleshooting
| Problem | Fix |
|---|---|
| A render prints "Killed" or a worker dies | Out of memory: use fewer `--workers`, or raise `memory=` in `.wslconfig` and run `wsl --shutdown` |
| `bpy==5.2.2` not found | The venv isn't Python 3.13: run `uv venv --python 3.13 .venv` again |
| cairosvg says "no library called cairo" | `sudo apt install -y libcairo2` |
| Teleport: "Unable to get organization UUID" | `claude auth login` with the same account |
| `git push` 403 | Your account needs write access to `jawad150/100`, then `gh auth login` |
| Wrong fonts | Re-run `python setup_workspace.py` |
| GPU not used | Check `nvidia-smi` inside Ubuntu, then `export FOSTER_GPU=1` |
| Very slow | Move the repo out of `/mnt/c` into `~/100` |

Sources:
- install guide: https://code.claude.com/docs/en/setup
- teleport: https://code.claude.com/docs/en/claude-code-on-the-web (section "Move tasks between terminal and cloud")
