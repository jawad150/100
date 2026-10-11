# Build contract for the Bijli series (lead, 2026-10-11)

Read `brand_reels/design/BIJLI_SERIES.md` first (binding), then your reel's `brand_reels/design/reels/<slug>/`
(BRIEF.md, SCRIPT.md, script.json, SHOTS.md). SHOTS.md is the source of truth for timing; if you must deviate, write
the change in your own notes file and tell the lead in your final message.

## Stage 2 runs three roles in parallel per reel; each owns only its files
| role (agent file) | owns | writes renders to | notes file |
|---|---|---|---|
| Blender artist (`.claude/agents/blender-3d-artist.md`, skill `.claude/skills/blender-pro-reference`) | `pipeline/jawad_reels/assets3d_<slug>.py` | `workspace/jawad_reels/<slug>/assets3d/` | `brand_reels/design/reels/<slug>/ASSETS.md` |
| Sound designer (`sound-designer.md` + `music-supervisor.md`) | `pipeline/jawad_reels/<slug>_music.py`, `<slug>_sfx.py` | `workspace/jawad_reels/<slug>/audio/` | `.../<slug>/SOUND.md` |
| UI/UX designer (`caption-designer.md` + `brand-kit-builder.md`) | `pipeline/jawad_reels/<slug>_ui.py` | `workspace/jawad_reels/<slug>/ui_selftest/` | `.../<slug>/UI.md` |

Stage 3 (motion designer, `motion-timeline-builder.md`) writes `pipeline/jawad_reels/<slug>.py` (+ `<slug>_world.py`),
using the three modules above, renders, and delivers. Stage 4 is QA (`motion-qa-reviewer.md`).

### Interfaces
- **Blender:** photoreal (BIJLI_SERIES "Photoreal 3D"). Cycles CPU, denoiser on, sensible samples, through
  `pipeline/jawad_reels/tools/heavy.sh`. Output transparent RGBA PNG (or EXR->PNG) stills/sequences, plus any
  full-frame background plates. ASSETS.md lists every file: path, size in px, frame count, what it shows, camera,
  pivot/anchor points the compositor needs (e.g. the sprocket centre, the screen quad corners), and the render command.
  Also copy compressed versions (PNG optimised or high-quality JPG for opaque plates) into
  `brand_reels/assets/<slug>/assets3d/` so a fresh container can restore without re-rendering; keep that folder under
  60 MB. Pattern to copy: `assets3d_bijli_chali_gayi.py`, `assets3d_hero.py`, `assets3d_household.py`.
- **Sound:** use the house kit `epic_music.py` / `epic_sfx.py` / `epic_mix.py` (sample library already fetched in
  `workspace/brand_reels/sfx/library/`, marker `workspace/brand_reels/wf/KIT_READY`). Pattern: `bijli_chali_gayi_music.py`,
  `bijli_chali_gayi_sfx.py`. Keep the frame cue list as a table at the top of `<slug>_sfx.py` so the motion designer can
  retime and re-run. Output 48 kHz 24-bit: `music.wav`, `sfx.wav`, `mix_A.wav` (music + SFX, -14 LUFS, TP <= -2 dBTP),
  `mix_B.wav` (SFX only, for the song-ready version). No VO (not approved); leave mid-range headroom so a VO could sit
  on top later. CLI: `python3 <slug>_sfx.py build` / `python3 <slug>_music.py build` regenerate everything.
- **UI/UX:** `<slug>_ui.py` exposes pure draw functions `fn(cv, t, ...)` on the house canvas (jawad_kit `K`, type3d `T`,
  `ui.py`, `snake_captions.py`): every caption lockup from script.json with its in/out animation, every glass UI element
  (timeline, chat bubbles, meters, bins), the outro question config for `profile_outro.ProfileOutro`, and a
  `cover(cv)` overlay for the cover still + the 3:4 grid-crop safe area. `python3 <slug>_ui.py selftest` writes PNG stills
  of each element to `workspace/jawad_reels/<slug>/ui_selftest/`. Look at those PNGs yourself (Read tool) and fix
  anything that is off before you finish. Pattern: `pehle_wala_ui.py`, `beta_tum_karte_kya_ho_ui.py`.

## Rules for every agent
- Never call `mcp__hearthbot__*` tools, never call paid generation services (Higgsfield, OpenArt, Magnific...).
- No Jawad face / character-sheet / cut-out images anywhere (the profile-photo badge inside profile_outro is allowed).
- Heavy jobs (Blender, render.py, music render, ffmpeg encodes of full reels) only through
  `pipeline/jawad_reels/tools/heavy.sh`, at most one at a time per agent; `render.py --workers 1`.
- Commit + push your finished files with `pipeline/jawad_reels/tools/commit_step.sh "<slug>: <message>" <paths...>`
  (only your own files; never `workspace/`; never raw git add/commit/push; never switch branches).
- Final message: what you built, file list, anything the next stage must know, any deviation from SHOTS.md.
