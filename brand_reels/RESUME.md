# How to resume this project in a new session (any account with access to jawad150/100)

Branch: `claude/beautiful-planck-mtdn0c`. Everything that matters is committed; the git-ignored `workspace/` holds
re-buildable scratch only, except what is saved under `brand_reels/assets/`.

## State (2026-10-09)
- Research: `brand_reels/research/`. Slate + series bible: `brand_reels/design/SLATE.md`.
- Per reel design docs: `brand_reels/design/reels/<slug>/` (BRIEF, packet.yaml, SCRIPT, script.json, GATE, VO_TIMING,
  FACES, SOUND, HANDOFF). Slugs: pehle_wala, bijli_chali_gayi, ek_frame_ki_keemat, beta_tum_karte_kya_ho, log_kya_kahenge.
- Toolkit + per-reel code: `pipeline/jawad_reels/` (jawad_kit, jawad_grade looks, jawad_tx transitions, snake_captions,
  endcard, vo_chain, `<slug>*.py` modules, `assets3d_<slug>.py` prop builders, `<slug>_music.py` deterministic beds).
- Voice: Higgsfield preset "Vlad" on elevenlabs_v4 (`pipeline/jawad_reels/vo_config.json`). The paid VO takes are saved in
  `brand_reels/assets/<slug>/vo_raw/` with word timings (`*.json`) - do NOT regenerate them (credits). Credit budget: 250
  for the whole project; about 64 were used for casting plus about 12 per reel for VO.
- Face cut-outs (+ depth + metadata) and `faces.py`: `brand_reels/assets/charsheet/`. 3D prop renders: `brand_reels/assets/<slug>/props|assets3d`.
- Previews: `brand_reels/previews/`.
- Pipeline used: `pipeline/jawad_reels/workflows/preprod.js` then `build.js` (Workflow scripts; args per reel are in the
  script headers / SLATE), shared context `pipeline/jawad_reels/workflows/ctx.txt`.

## Restore a fresh container
1. `git fetch origin claude/beautiful-planck-mtdn0c && git checkout claude/beautiful-planck-mtdn0c`
2. `python3 pipeline/jawad_reels/setup_workspace.py` (fonts, logos) and `pip install numpy opencv-python pillow scipy faster-whisper`; Blender 5.x bpy for props.
3. Copy assets back: `brand_reels/assets/<slug>/vo_raw` -> `workspace/jawad_reels/<slug>/vo/raw`, `*.json` -> `workspace/jawad_reels/<slug>/vo/`,
   props -> `workspace/jawad_reels/<slug>/`, `brand_reels/assets/charsheet/cutouts` -> `workspace/brand_reels/charsheet/cutouts`,
   `faces.py` -> `workspace/brand_reels/charsheet/tools/`. Re-run `pipeline/jawad_reels/vo_chain.py` on the raw takes and `<slug>_music.py` for the beds.
4. Continue with `build.js` for every reel whose `reel/jawad_reels/<slug>/` folder is missing.
