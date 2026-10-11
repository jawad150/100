# RENDER_JOBS · Pencil Se Rewind (final 3D renders on the GPU PC)

Target: Windows PC, RTX 4060 8 GB (OptiX), 16 GB RAM. Run everything **from the repo root**. Every line is a plain
python call (no bash, no heavy.sh needed on that PC). `FOSTER_GPU=1` makes `assets3d_gpu.set_device` choose
OPTIX > CUDA > ...; each job then uses its GPU sample count (256-1024, adaptive 0.01, OIDN on the GPU). Check the first
log line: `[assets3d] Cycles device: OPTIX:NVIDIA GeForce RTX 4060 ...`. If it says CPU, stop (see Troubleshooting).
Do not mix devices inside one asset folder: if a job is interrupted, resume it on the same PC with `SKIP_EXISTING=1`.

## 0. One-time setup
    python -m pip install bpy==5.2.2 numpy opencv-python pillow      # bpy needs the Python version its 5.2 wheel targets
    git pull                                                         # brings the module + the committed tex3d maps

Textures are restored automatically from `brand_reels/assets/pencil_se_rewind/tex3d/` (no fonts needed). Output goes
to `workspace\jawad_reels\pencil_se_rewind\assets3d\` (from `pipeline/jawad_reels/project.json`).

## 1. Final renders (PowerShell; one line per job)
Estimates: RTX 4060, measure frame 0 and multiply. The scene build (SDF meshing) takes ~30-60 s per job the first time
(cached afterwards in `workspace\...\out\cache3d`).

| # | job | frames | GPU spp | est. per frame | est. job |
|---|---|---|---|---|---|
| 1 | `$env:FOSTER_GPU="1"; python pipeline/jawad_reels/assets3d_pencil_se_rewind.py hub_loop` | 16 | 384 | 40-70 s | 11-19 min |
| 2 | `$env:FOSTER_GPU="1"; python pipeline/jawad_reels/assets3d_pencil_se_rewind.py hub_cover` | 1 | 1024 | 2-3 min | 3 min |
| 3 | `$env:FOSTER_GPU="1"; python pipeline/jawad_reels/assets3d_pencil_se_rewind.py hub_rescue` | 32 | 256 | 20-40 s | 11-21 min |
| 4 | `$env:FOSTER_GPU="1"; python pipeline/jawad_reels/assets3d_pencil_se_rewind.py label` | 1 | 512 | 1-2 min | 2 min |
| 5 | `$env:FOSTER_GPU="1"; python pipeline/jawad_reels/assets3d_pencil_se_rewind.py walkman_loop` | 8 | 384 | 40-70 s | 6-10 min |
| 6 | `$env:FOSTER_GPU="1"; python pipeline/jawad_reels/assets3d_pencil_se_rewind.py walkman_keys` | 4 | 512 | 10-20 s (crop) | 1-2 min |
| 7 | `$env:FOSTER_GPU="1"; python pipeline/jawad_reels/assets3d_pencil_se_rewind.py walkman_eat` | 32 | 256 | 20-40 s | 11-21 min |
| 8 | `$env:FOSTER_GPU="1"; python pipeline/jawad_reels/assets3d_pencil_se_rewind.py pencil_top` | 2 | 512 | 10-20 s | 1 min |

Total 96 frames, roughly 45-80 min. All eight in one go:

    $env:FOSTER_GPU="1"; python pipeline/jawad_reels/assets3d_pencil_se_rewind.py all

(cmd.exe: `set FOSTER_GPU=1 && python pipeline/jawad_reels/assets3d_pencil_se_rewind.py hub_loop`;
Linux / macOS / WSL: `FOSTER_GPU=1 python3 pipeline/jawad_reels/assets3d_pencil_se_rewind.py hub_loop`.)
Resume an interrupted job: `$env:FOSTER_GPU="1"; $env:SKIP_EXISTING="1"; python pipeline/jawad_reels/assets3d_pencil_se_rewind.py <name>`.

## 2. Verify
    python pipeline/jawad_reels/assets3d_pencil_se_rewind.py selftest        # every folder: meta.json, frame count, uint8 RGBA
    python pipeline/jawad_reels/assets3d_pencil_se_rewind.py sheet           # -> workspace\...\out\sheets3d\psr_finals_sheet.jpg

Look at the sheet: hub_rescue f31 must hand on to hub_loop f0, walkman_eat f0 must equal walkman_loop f0 with PLAY down.

## 3. Compressed restore copies (< 60 MB) and commit
    python pipeline/jawad_reels/assets3d_pencil_se_rewind.py pack

Writes `brand_reels/assets/pencil_se_rewind/assets3d/<name>/passes/` (opaque frames as JPEG q93, RGBA as PNG,
meta.json); it lowers the JPEG quality by itself if the folder would pass 58 MB (expected ~30 MB). Then commit that
folder (Linux box: `pipeline/jawad_reels/tools/commit_step.sh "pencil_se_rewind: 3D finals (restore pack)" brand_reels/assets/pencil_se_rewind/assets3d`;
on Windows: `git add brand_reels/assets/pencil_se_rewind/assets3d` + commit + push). A fresh container restores the
spec folders with `python3 pipeline/jawad_reels/assets3d_pencil_se_rewind.py restore`.

## Troubleshooting
- Device line says CPU: update the NVIDIA driver; try `$env:FOSTER_GPU_TYPE="CUDA"` if OptiX fails.
- Out of VRAM (unlikely, the heaviest scene is ~0.6 M quads + 4k textures): close other GPU apps, or render that job with
  `--samples 192`.
- Tests on the shared Linux box (CPU, never finals there): `pipeline/jawad_reels/tools/heavy.sh python3 pipeline/jawad_reels/assets3d_pencil_se_rewind.py <name> --preview`.
