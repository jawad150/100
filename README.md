# Rida — Japan bonds × Yen carry trade reel

An 89-second vertical talking-head reel (1080×1920, 30 fps) in Roman-Urdu captions, edited from the
"Rida Proj" Drive folder:

- **Main clip**: `Rida Raww Final 2 3.mp4`
- **Captions**: Roman-Urdu text taken from `Script/Script.txt`, aligned word by word to the audio
- **Grade**: matched to the natural-colour reference (clean neutral whites, natural warm skin, soft contrast, lifted shadows), with sharpening and the baked-in vignette lifted
- **Caption and motion style**: taken from the reference reel. Single-word pop captions in a bold SF-Pro-style sans (Inter Display), stacked yellow kinetic type tilted in 3D, yellow icons and a face-tracking box
- **SFX**: the reference reel's own sound effects. The voice was removed with Demucs and the whooshes, pops, clicks, booms and ding were sliced from the remaining stem

**Video:** [`reel/rida_japan_yen_reel.mp4`](reel/rida_japan_yen_reel.mp4) · **LUT:** [`reel/rida_natural_grade.cube`](reel/rida_natural_grade.cube)

The 3D cutaways are built After-Effects style with a 3D camera, a perspective grid floor, glass cards and coins in depth:

- Japan ↔ U.S. Treasury connection
- JGB yield chart
- Yen carry-trade flow, filmed with a camera move through three stations
- ¥360T → $2.34T counter
- 1996 → 2026 timeline with the 3% slam
- money flowing back to Japan
- impact cards
- gold and oil
- opportunities vs. risks

The reel ends on a follow card for Floret Capitals.

Captions and key graphics stay inside the Instagram Reels safe zone (x 64–940, y 260–1480). Text is placed so it never covers the talent's face.

### Rebuild

```bash
pip install numpy scipy pillow "opencv-python-headless==4.10.0.84" faster-whisper demucs gdown
# workspace/rida/src/: main.mp4, ref_style.mp4, ref_grade2.jpg, script.txt, broll/*.png (from the Drive folder)
python3 pipeline/rida/grade.py workspace/rida/ana/grade.cube                 # natural grade LUT
ffmpeg -i workspace/rida/src/main.mp4 -vf "fps=30,hqdn3d=0:2.5:0:0,lut3d=workspace/rida/ana/grade.cube" \
       -crf 10 -an workspace/rida/work_graded.mp4                            # graded plate
python3 pipeline/rida/facetrack.py workspace/rida/work_graded.mp4 workspace/rida/ana/face.json
# whisper word timings -> ana/main_words*.json, then:
python3 pipeline/rida/align.py workspace/rida/src/script.txt ... workspace/rida/ana/captions_words.json
python3 -m demucs -n htdemucs --two-stems=vocals -o workspace/rida/ana/sep workspace/rida/ana/ref_audio.wav
python3 pipeline/rida/extract_sfx.py workspace/rida/ana/sep/htdemucs/ref_audio/no_vocals.wav workspace/rida/sfx
python3 pipeline/rida/render_all.py                                          # -> workspace/rida/out/
```

Preview frames with `python3 pipeline/rida/edit.py still 1.0,30.8,47.6`. Set `SAFE_GUIDE=1` to draw the safe-zone box.

---

# Higgsfield Genjutsu — orange × black SaaS reel

A 30-second vertical reel (1080×1920, 30 fps, with sound design). It shows a Higgsfield Genjutsu motion-transfer result and walks through how it was made, in a cinematic orange-and-black SaaS motion-graphics style.

**Latest (v3, SFX only, no voiceover):** [`reel/higgsfield_genjutsu_reel_v3.mp4`](reel/higgsfield_genjutsu_reel_v3.mp4)

**v2 (with voiceover, 32 s, voiceover + SFX, profile ending):** [`reel/higgsfield_genjutsu_reel_v2.mp4`](reel/higgsfield_genjutsu_reel_v2.mp4)

**v1:** [`reel/higgsfield_genjutsu_reel.mp4`](reel/higgsfield_genjutsu_reel.mp4) (10 Mbps master) · [`reel/higgsfield_genjutsu_reel_share.mp4`](reel/higgsfield_genjutsu_reel_share.mp4) (7 Mbps, under 30 MB) · cover frame [`reel/cover.jpg`](reel/cover.jpg)

## Storyboard

| Time | Scene | What happens |
|---|---|---|
| 0.0–6.9 s | **Hook: the result** | The split-screen result (ORIGINAL on top, GENJUTSU below) flies in on 3D-tilted glass cards, cutting from the close-up face swap to the crowd chaos with a whip-pan. Headline "I PUT MYSELF INTO A MOVIE" with a CTA pill "WATCH FULL VIDEO FOR THE GUIDE". |
| 6.9–8.6 s | **"HERE'S HOW"** | Letter slams with camera shake, light rays, a perspective grid floor, and orange/black 3D blob mascots popping in. |
| 8.6–21.6 s | **4 steps (screen recording)** | Floating 3D browser window with zooms that follow the action, 3D cursor clicks with ripples, and a step progress bar: **01** Open Genjutsu · **02** Pick a motion video → Recreate · **03** Add your character · **04** 1080p → Generate. |
| 16.2–18.0 s | **Character-sheet clone** | The character sheet flies out of the upload slot, splits into 9 clone cards that fan out in 3D, then all fly back into the upload tile. |
| 21.6–24.2 s | **Payoff** | Generate shockwave and flash, then the Genjutsu output in a big 4:5 card with the original shown picture-in-picture. "ONE CHARACTER. ANY SCENE." |
| 24.2–26.0 s | **Clone wall** | Camera pulls back through a tilted wall of clones (character-sheet angles and Genjutsu frames). "CLONE YOURSELF INTO ANY VIDEO". |
| 26.0–30.0 s | **Outro** | 3D extruded Higgsfield logo rotates in, surrounded by blob mascots; "WATCH THE FULL VIDEO FOR THE COMPLETE GUIDE". |

## How it's built

Everything is rendered from code; no editor project is involved.

- `pipeline/blender_assets.py` renders the 3D elements with Blender (the `bpy` module, Cycles). These are glossy orange/black blob mascots, a torus, capsule, cube, chrome sphere, 3D cursor, 3D arrow, and the extruded Higgsfield logo, which is traced from `logo.png`. They come out as transparent PNG sequences.
- `pipeline/engine.py` is a small 2.5D compositor built on numpy and OpenCV. It does:
  - perspective 3D planes and rounded glass cards with glow and shadow
  - kinetic type, pills, light streaks and particles
  - bloom, grain, vignette and chromatic aberration
- `pipeline/reel.py` holds the timeline and scenes. Motion blur is real: each frame averages 6 sub-frame renders across a 0.55 shutter.
- `pipeline/audio.py` generates the soundtrack: the score (pulse, bass, pad, arpeggio), whooshes, impacts, risers, UI clicks and blob pops. The original scene audio sits underneath at low level.
- `pipeline/render_all.py` renders in parallel chunks, then concatenates them, muxes the audio and does the final H.264 encode.

## Rebuild

```bash
pip install bpy numpy "opencv-python-headless==4.10.0.84" pillow scipy imageio-ffmpeg
# put screenrec.mp4, result_split.mp4, charsheet.png, logo.png into workspace/src/
python3 pipeline/prep_sources.py          # fonts, logo vectorization, frame extraction
python3 pipeline/blender_assets.py blob_drop blob_bear blob_flower blob_cube torus rcube capsule sphere cursor3d arrow3d logo3d
python3 pipeline/render_all.py            # -> workspace/out/higgsfield_genjutsu_reel.mp4
```

To preview single frames, run `python3 pipeline/reel.py still 1.8,12.9,22.8`. Set `REEL_WORKDIR` to use a different workspace folder.
