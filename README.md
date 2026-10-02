# Gold market reel — black × gold motion graphics (Rida)

**Final video:** [`reel/gold_reel_4k.mp4`](reel/gold_reel_4k.mp4) is native 4K (2160×3840) at 29.97 fps, 79.4 s, with voice and SFX. A 1080p copy is at [`reel/gold_reel_1080p.mp4`](reel/gold_reel_1080p.mp4), and the captions as SRT are at [`reel/captions_roman_urdu.srt`](reel/captions_roman_urdu.srt).

This adds 3D motion graphics on top of the color-corrected, green-screen-removed render (`color correction.mp4`, 4K). The edit follows the script "Sona achanak itna neeche kyun gira". Gold is `#E49F38` (lit as metal, so it carries highlights and shade); everything else is black.

**Look**
- **Native 4K render.** The layout is designed at 1080×1920 and every frame is rendered at 2×, straight from the 4K source frames.
- **Grade.** Deep neutral blacks, a filmic S-curve with a soft shoulder, warm-gold highlights, neutral shadows and natural skin. Teal spill from the keyed stage is removed, and the teal stage is pushed toward black. A detail pass adds a thresholded fine sharpen and light clarity. Bloom has gold-leaning halation, and there's fine grain.
- **Type.** Cinzel (overlap-free) is used for titles, the chapter cards, tags and the 3D numbers; General Sans is used for the captions.
- **Text styling.** All text is styled as cinematic 3D: bevel and emboss, an extruded side, a deep glow and a contact shadow.
- **Captions.** Roman Urdu, word by word, synced to her speech (cross-checked against two transcriptions and speech onsets). Lines are centered and share exact baselines, and gold keywords are emphasized.
- **Camera.** A virtual 3D camera with parallax, built from three layers:
  - authored moves (push-ins, orbits, dutch angles, angle cuts, impact shakes);
  - a fast-paced edit layer that snaps to a new angle on every caption phrase, with motion-blurred 0.3 s expo moves and every third one a hard cut;
  - an edge guard so the original frame edges never show.
- **Transitions.** Whip pans (both shots side by side), zoom-throughs and a spin, all with real sub-frame motion blur.

| Time | Script beat | Motion graphics |
|---|---|---|
| 0.0–5.2 s | Hook: "Sona achanak itna mehnga kaise ho gaya? … crash … opportunity zone?" | Reference-style hook: a gold halo disc behind her head, "SONA" then "MEHNGA?" split behind her head, neon gold light trails wrapping around her, 3D gold bars raining down, a slammed gold "CRASH?" title block, a crash arrow and a target |
| 5.2–13.6 s | Gold traders, sharp retracement, 3 reasons | 3D gold/black candlestick chart, a crash arrow, and a 3D "3" |
| 13.6–25.1 s | 01 · Treasury yields | Chapter card (video on a floating gold-edged 3D card, neon "YIELDS", tags), a 3D Treasury bond, "2007", a money bag and return arrow, a gold "Au" coin, and an "INTEREST 0%" tag |
| 25.1–30.4 s | 02 · US Dollar | Chapter card (neon "DOLLAR"), a 3D gold "$", a dollar coin and a selling-pressure arrow |
| 30.4–40.2 s | 03 · Fed rate hike | Chapter card (neon "FED"), a 3D Fed building, an October/25 bp calendar, "0.25%" and "60-70%" with a rate-hike odds meter |
| 40.2–51.4 s | 28 Sept drop, −4 %, $4,145; "har drop crash nahi hota" | 28 Sept calendar, "−4%", "$4,145", crash arrow, gold bar; then a spotlight push-in with rays, "CRASH NAHI" and a gold check badge |
| 51.4–64.6 s | 30 Sept, 40 %, $4,200, correction not crash | Empty-stage rebound arrow, 30 Sept calendar, "40%" with the meter falling, "$4,200" with an up arrow and a $-cycle icon, a struck-through "STRUCTURAL CRASH" tag, and "CORRECTION" |
| 64.6–79.4 s | Fed next move, PCE, oil risk; selective buying; risk and news flow | Fed building, candles and oil barrel with tags; target; shield and news bubble; outro rays and fade |

## How it's built (`pipeline/gold/`)

- `matte.py`: Robust Video Matting (ONNX) person matte for every frame. It lets type and 3D objects sit behind her, and lets the stage move separately from her.
- `gold_assets.py`: Blender (Cycles) renders of the script elements as transparent PNG sequences. These are gold bar, Au coin, $, crash and rebound arrows, candlesticks, Fed building, Treasury bond, oil barrel, shield, calendars and 3D numbers.
- `timeline.py`: the edit. It holds the shots, camera keys, transitions, chapter cards, element cues, captions (with Whisper word indices) and SFX cues.
- `gold_reel.py`: the compositor, which reuses `pipeline/engine.py`. It renders in a 1080×1920 design space at `OUT_K`× resolution (2 means 4K, from `workspace/frames4k`). It handles the grade, 3D text styles, captions, camera layers and motion blur, and renders stills (`still 2.0,16.5`) or encoded frame ranges.
- `gold_audio.py`: synthesized SFX (whooshes, impacts, risers, coin chings, pops, clicks) ducked under the original voice, normalized to −12 LUFS.
- `render.py`: parallel chunked render, audio, the 4K master and the 1080p copy.
- `export_captions.py`: writes the synced captions as SRT.

Rebuild (sources from the Drive folder go in `workspace/src`, the script's PNGs in `workspace/assets2d`):

```bash
pip install bpy numpy "opencv-python-headless==4.10.0.84" pillow scipy faster-whisper onnxruntime
python3 pipeline/gold/matte.py
ffmpeg -i workspace/src/color_correction.mp4 -q:v 2 -start_number 0 workspace/frames4k/%05d.jpg
python3 pipeline/gold/gold_assets.py ingot coin_au dollar3d arrow_crash arrow_up candles3d fed bond barrel shield cal_oct cal_28sep cal_30sep num_3 num_2007 num_025 num_6070 num_4pct num_4145 num_40 num_4200
python3 pipeline/gold/render.py
```

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
