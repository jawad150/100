# Organic Fostering — "Day in the life" reel

19-second vertical reel (1080×1920, 30 fps, -14 LUFS sound), cinematic AI footage + SaaS-style motion graphics in the Organic Fostering brand (plum / magenta / orange / green, Nunito).

**Final:** [`reel/organic_fostering/organic_fostering_day_in_the_life.mp4`](reel/organic_fostering/organic_fostering_day_in_the_life.mp4) (master, ~30 Mbps) · [`…_share.mp4`](reel/organic_fostering/organic_fostering_day_in_the_life_share.mp4) (12 Mbps) · [`cover.jpg`](reel/organic_fostering/cover.jpg)

| Time | Scene | What happens |
|---|---|---|
| 0.0–0.8 s | Hook | Flash montage of the whole day with a "A day in the life" pill |
| 0.8–2.7 s | The allowance | 3D £ coin + 3D "£447.60", "Weekly fostering allowance", typed "Where does it go?", coin bursts into four glowing orbs |
| 2.7–5.1 s | Child's bedroom | "Sometimes, / it's not the / big things." (blur-in words, glow, light sweep); live clock chip starts at 7:00 am |
| 5.1–8.4 s | Morning light → shoes → school bag | Each orb flies in and lands as a glass tag: "School shoes ✓", "Books & packed lunch ✓" |
| 8.4–11.0 s | Warm kitchen | "It's breakfast / at the table." + "Breakfast ✓" tag, 3D heart |
| 11.0–14.1 s | Bedroom at night | Clock rolls to 7:30 pm, "A goodnight / at bedtime.", "Someone asking," + chat bubble "How was your day?" |
| 14.1–16.8 s | The message | Plum stage: "Sometimes, ordinary moments / help create / **extraordinary** (3D) / change." over the hands-and-seedling clip |
| 16.8–19.0 s | End card | Logo, three-colour bar, organicfostering.co.uk, small print on the allowance |

Pipeline (`pipeline_of/`): Higgsfield keyframes (`gpt_image_2_5`) animated with `seedance_2_5` at 1080p; `blender_of.py` renders the 3D brand elements; `reel_of.py` is the compositor timeline (reuses `pipeline/engine.py`); `audio_of.py` synthesises the score and SFX; `render_all.py` renders in parallel and muxes. Rebuild: put clips into `workspace_of/gen/clip1..7.mp4`, extract frames to `workspace_of/frames/cN/`, add fonts (Nunito static instances) and `src/logo_full.png`, run the Blender assets, then `python3 pipeline_of/render_all.py`.

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
