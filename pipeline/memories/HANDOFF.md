# Yaadein – Spider-Man memory reel: how to continue in a new session

Branch: `claude/festive-lovelace-6gletw` of `jawad150/100`. Everything below runs from `pipeline/memories/`.
Big media live in `workspace2/` (git-ignored) and are rebuilt by these steps; rendered plates are
pushed under `media/yaadein/` (Git LFS) once rendered, so they do not have to be re-rendered.

## What the reel is
* 32 s, 1080x1920 @ 60 fps. Voice + music: `workspace2/src/audio_src.mp4`, which is the user's upload
  (27.84 s). Re-upload it if it is missing.
* Script and word timings: `script.py`. The theme is Spider-Man red/blue/black visuals, with captions in the
  creator's orange/black/white.
* Ending: the creator's photo in a ring → full frame → orange/black gradient → `@jawad_mp4` → CTA
  ("Kaunsi yaad bhulana sabse mushkil hai?") → Follow click. **The creator's photo goes in
  `workspace2/assets/user_photo.jpg`.** Until then, the hero mask portrait is used as a placeholder.

## Rebuild from scratch
1. `pip install bpy==5.0.1 opencv-python pillow scipy` (Blender as a Python module, Cycles CPU).
2. Assets:
   * `bash fetch_drive.sh` downloads the user's Drive folder **spiderman**. The folder must be shared
     as "Anyone with the link".
   * `python3 fetch_assets.py` downloads the Poly Haven HDRIs and textures.
3. Plates: `bash render_queue.sh`. It renders `film.py` shots into `workspace2/plates3`, takes about 1.5 h on
   4 cores, and logs to `workspace2/work/render_queue.log`. If the LFS copies exist, copy
   `media/yaadein/plates3` to `workspace2/plates3` and skip this step.
4. Sound: `python3 reel.py cues && python3 sound.py ../../workspace2/work/cues.json 32` writes
   `workspace2/out/audio.wav`.
5. Picture: `python3 reel.py render 4` runs 4 workers and writes `workspace2/work/video_60.mp4`, then mux:
   `ffmpeg -i ../../workspace2/work/video_60.mp4 -i ../../workspace2/out/audio.wav -c:v copy -c:a aac -b:a 320k -shortest out.mp4`
6. Checks: `python3 reel.py still 1.2 15.2 26.4` writes stills, and `python3 reel.py preview` writes a fast half-res cut.

## Modules
| file | role |
|---|---|
| `film.py` | Blender shots: the ruins at night, the temple at golden hour, the mountains at dawn and sunrise, and the insert shots in a void (lasso, dagger, bomb, logo) |
| `cast.py` | loads and normalises the user's characters and props, plus the pose recipes (crouch, kneel, kneel_hold, sit, stand, grief) |
| `world.py` | Cycles helpers: HDRI, PBR, fog, lights and cameras |
| `comp.py` | 2.5D camera, lens blur, shutter motion blur, bloom/halation/anamorphic, grade and grain |
| `anim.py` | After Effects-style bezier easing (influence), springs and wiggle |
| `fx.py` | 30→60 fps optical-flow clips, polaroids, glass shatter, lightning, fireball, particles |
| `captions.py` | snake captions in orange, white and black |
| `hud.py` | the Spider-Man HUD and SaaS glass panels (memory card, delete dialog, meter, truth check) |
| `ending.py` | the end card |
| `reel.py` | timeline, captions, HUD, the SFX cue sheet and the renderer |
| `sound.py` | synthesized SFX, the beat-matched music extension and the mix |
