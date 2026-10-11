# RENDER_JOBS · Thoda Left... Bas Bas! (final 3D renders on the GPU PC)

Target: Windows PC, RTX 4060 8 GB (OptiX), 16 GB RAM. Run everything **from the repo root**. Every line is a plain
python call (no bash, no heavy.sh needed on that PC). `FOSTER_GPU=1` makes `assets3d_gpu.set_device` pick
OPTIX > CUDA > ...; each pass then uses its GPU sample count (256-512, adaptive threshold 0.01, OIDN on the GPU).
Check the first log line: `[assets3d] Cycles device: OPTIX:NVIDIA GeForce RTX 4060 ...`. If it says CPU, stop (see
Troubleshooting). Never mix devices inside one asset folder: if a job is interrupted, resume it on the same PC with
`SKIP_EXISTING=1` (raw frames are kept until the folder is complete; the crop and meta.json happen at the end).

## 0. One-time setup
    python -m pip install bpy==5.2.2 numpy opencv-python pillow      # bpy needs the Python version its 5.2 wheel targets
    git pull                                                         # brings pipeline/jawad_reels/assets3d_thoda_left_bas.py

No textures or fonts are needed (every material is procedural). Output goes to
`workspace\jawad_reels\thoda_left_bas\assets3d\<name>\<variant>\` (workspace root from `pipeline/jawad_reels/project.json`).
Optional layout check before rendering (no render, ~1 min): `python pipeline/jawad_reels/assets3d_thoda_left_bas.py targets`.

## 1. Final renders (PowerShell; one line per job, SHOTS order A5 -> A1 -> A3 -> A4 -> A6 -> A7 -> A2)
Estimates for the RTX 4060 are scaled from the CPU preview timings (measure the first frame and multiply).
Scene build takes 10-30 s per job.

| # | job | frames (passes) | GPU spp | est. per frame | est. job |
|---|---|---|---|---|---|
| 1 | `$env:FOSTER_GPU="1"; python pipeline/jawad_reels/assets3d_thoda_left_bas.py crt/macro` | 4 (room, refl, spill, stmap) | 512 / 256 / 256 / 16 flat | 1-4 min | 6-10 min |
| 2 | `$env:FOSTER_GPU="1"; python pipeline/jawad_reels/assets3d_thoda_left_bas.py antenna/day_yaw` | 61 (yaw -45..+15, 1 deg) | 256 | 15-30 s (cropped) | 15-30 min |
| 3 | `$env:FOSTER_GPU="1"; python pipeline/jawad_reels/assets3d_thoda_left_bas.py roof/day` | 2 (bg, fg_clamp) | 512 / 256 | 1-3 min | 3-5 min |
| 4 | `$env:FOSTER_GPU="1"; python pipeline/jawad_reels/assets3d_thoda_left_bas.py clamp/macro` | 2 (bg, fg) | 512 / 384 | 1-3 min | 3-5 min |
| 5 | `$env:FOSTER_GPU="1"; python pipeline/jawad_reels/assets3d_thoda_left_bas.py clamp/pipe_yaw` | 17 (yaw -6..+2, 0.5 deg) | 256 | 15-40 s (strip) | 5-10 min |
| 6 | `$env:FOSTER_GPU="1"; python pipeline/jawad_reels/assets3d_thoda_left_bas.py crt/room` | 4 (room, refl, spill, stmap) | 512 / 256 / 256 / 16 flat | 1-4 min | 6-10 min |
| 7 | `$env:FOSTER_GPU="1"; python pipeline/jawad_reels/assets3d_thoda_left_bas.py phone/desk` | 3 (lit, spill, stmap) | 512 / 256 / 16 flat | 1-3 min | 3-6 min |
| 8 | `$env:FOSTER_GPU="1"; python pipeline/jawad_reels/assets3d_thoda_left_bas.py antenna/sunset_yaw` | 7 (yaw -3..+3, 1 deg) | 384 | 15-40 s (cropped) | 2-5 min |
| 9 | `$env:FOSTER_GPU="1"; python pipeline/jawad_reels/assets3d_thoda_left_bas.py roof/sunset` | 2 (bg, fg_clamp) | 512 / 256 | 1-3 min | 3-5 min |

Total 102 frames, roughly 45-90 min. All nine in one go (same order):

    $env:FOSTER_GPU="1"; python pipeline/jawad_reels/assets3d_thoda_left_bas.py all

(cmd.exe: `set FOSTER_GPU=1 && python pipeline/jawad_reels/assets3d_thoda_left_bas.py crt/macro`;
Linux / macOS / WSL: `FOSTER_GPU=1 python3 pipeline/jawad_reels/assets3d_thoda_left_bas.py crt/macro`.)
Resume an interrupted job: `$env:FOSTER_GPU="1"; $env:SKIP_EXISTING="1"; python pipeline/jawad_reels/assets3d_thoda_left_bas.py <name/variant>`.

## 2. Verify
    python pipeline/jawad_reels/assets3d_thoda_left_bas.py selftest       # every folder: meta.json, frame count, S3 load
    python pipeline/jawad_reels/assets3d_thoda_left_bas.py sheet          # -> workspace\jawad_reels\thoda_left_bas\out\sheets3d\finals_*.jpg

Look at the sheets: `finals_roof_day.jpg` / `finals_roof_sunset.jpg` (plate + antenna + fg clamp layered),
`finals_clamp.jpg` (pipe mark walks onto the strap mark; aligned in the middle cell = yaw 0), `finals_crt_macro.jpg` /
`finals_crt_room.jpg` / `finals_phone_desk.jpg` (a test grid warped through the stmap must sit exactly inside the glass).
Every meta.json must say `"device": "OPTIX:..."` and `"preview": false`.

## 3. Compressed restore copies (< 60 MB) and commit
    python pipeline/jawad_reels/assets3d_thoda_left_bas.py archive

Writes `brand_reels/assets/thoda_left_bas/assets3d/<name>/<variant>/` (opaque frames as JPEG q92, RGBA frames as a JPEG
colour plate + `<n>.a.png` alpha plate, 16-bit STMaps as PNG, meta.json, archive.json); it lowers the JPEG quality by
itself if the folder would pass 58 MB (expected ~30-45 MB). Then commit that folder (Linux box:
`pipeline/jawad_reels/tools/commit_step.sh "thoda_left_bas: 3D finals (restore pack)" brand_reels/assets/thoda_left_bas/assets3d`;
on Windows: `git add brand_reels/assets/thoda_left_bas/assets3d` + commit + push). A fresh container restores the spec
folders with `python3 pipeline/jawad_reels/assets3d_thoda_left_bas.py restore`.

## Troubleshooting
- Device line says CPU: update the NVIDIA driver; try `$env:FOSTER_GPU_TYPE="CUDA"` if OptiX fails.
- Out of VRAM (unlikely: the heaviest scene, the CRT room, is < 1 M triangles and has no image textures): close other
  GPU apps, or add `--samples 256`.
- Fireflies in the CRT `room` pass (sun through the window bars): re-run that asset with `--samples 768`.
- Tests on the shared Linux box (CPU, never finals there):
  `pipeline/jawad_reels/tools/heavy.sh python3 pipeline/jawad_reels/assets3d_thoda_left_bas.py <name/variant> --preview`
  then `python3 pipeline/jawad_reels/assets3d_thoda_left_bas.py previewsheet`.
