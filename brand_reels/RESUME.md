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


## Exact status when this session stopped (2026-10-09, ~14:30 PKT)
All agents were stopped on purpose so the project can continue on another account. Nothing is rendered or delivered yet
(`reel/jawad_reels/` is empty).

| # | reel (slug) | look | pre-production | build |
|---|---|---|---|---|
| 1 | Pehle Wala Hi Theek Tha (`pehle_wala`) | inferno | **done** (HANDOFF.md ready) | not started (no `pehle_wala.py` yet) |
| 2 | Bijli Chali Gayi (`bijli_chali_gayi`) | dusk | VO, faces, SFX done; **HANDOFF.md missing** | not started |
| 3 | Ek Frame ki Keemat (`ek_frame_ki_keemat`) | ember | VO, SFX done; **faces module + FACES.md + HANDOFF.md missing** | not started |
| 4 | Beta, tum karte kya ho? (`beta_tum_karte_kya_ho`) | gold_hour | VO, faces, SFX done; **HANDOFF.md missing** | not started |
| 5 | Log Kya Kahenge (`log_kya_kahenge`) | noir_ember | **done** (HANDOFF.md ready) | **in progress**: `log_kya_kahenge.py`, `_crowd.py`, `_hookb.py`, `_mix.py` exist; finish the build, preview, master, QA, delivery |

Binding decisions for the build: `brand_reels/design/LEAD_DECISIONS.md`.

### Next steps, in order
1. Restore the workspace (section below).
2. Finish pre-production for reels 2-4: ek_frame_ki_keemat needs its faces module (`<slug>_faces.py` + FACES.md, face plan in its
   BRIEF.md) and all three need HANDOFF.md (the "Handoff" stage of `pipeline/jawad_reels/workflows/preprod.js`).
3. For each reel: build (`pipeline/jawad_reels/workflows/build.js`): reel module -> stills/contact sheet -> preview -> viral
   + colour review -> fixes -> master render -> two-lens QA with verification -> fixes -> delivery into
   `reel/jawad_reels/<slug>/` (IG mp4, song-ready mp4 with VO + SFX only, CRF 14 master, stems, cover, caption txt with
   "Turn on AI info", SRT). Run `build.js` with args like
   `{"id":"C15","title":"Log Kya Kahenge","slug":"log_kya_kahenge","look":"noir_ember","dur":35.2}` (other reels:
   C26 pehle_wala inferno 34.133; C11 bijli_chali_gayi dusk 34.667; C08 ek_frame_ki_keemat ember 33.6; C02
   beta_tum_karte_kya_ho gold_hour 36.4).
4. Send Jawad each final reel as soon as it passes QA; do not send previews.

### Voice assets (do not regenerate)
`brand_reels/assets/<slug>/vo_raw/` = every paid Vlad take (mp3); `brand_reels/assets/<slug>/vo_final/` = the processed,
timed stems as FLAC (`vo_stem*.flac`, `*_vo_A/B.flac`) plus word timings (`*.json`). Restore them to
`workspace/jawad_reels/<slug>/vo/` as WAV (`ffmpeg -i x.flac -c:a pcm_s24le x.wav`). Higgsfield is allowed for voice only;
about 107 of the 250-credit budget is used (casting about 64 + VO about 9-12 per reel); re-takes max 5 credits per reel.

## Restore a fresh container
1. `git fetch origin claude/beautiful-planck-mtdn0c && git checkout claude/beautiful-planck-mtdn0c`
2. `python3 pipeline/jawad_reels/setup_workspace.py` (fonts, logos) and `pip install numpy opencv-python pillow scipy faster-whisper`; Blender 5.x bpy for props.
3. Copy assets back: `brand_reels/assets/<slug>/vo_raw` -> `workspace/jawad_reels/<slug>/vo/raw`, `vo_final/*` -> `workspace/jawad_reels/<slug>/vo/` (FLAC -> WAV), `*.json` -> `workspace/jawad_reels/<slug>/vo/`,
   props -> `workspace/jawad_reels/<slug>/`, `brand_reels/assets/charsheet/cutouts` -> `workspace/brand_reels/charsheet/cutouts`,
   `faces.py` -> `workspace/brand_reels/charsheet/tools/`. Re-run `pipeline/jawad_reels/vo_chain.py` on the raw takes and `<slug>_music.py` for the beds.
4. Continue with `build.js` for every reel whose `reel/jawad_reels/<slug>/` folder is missing.
