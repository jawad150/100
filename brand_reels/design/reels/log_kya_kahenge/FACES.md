# FACES: Reel 5 · C15 · Log Kya Kahenge (face-compositor)

Date 2026-10-08 · Author: face-compositor · Code: `pipeline/jawad_reels/log_kya_kahenge_faces.py` (imported by the reel
module, never edited by it) · Plan source: `BRIEF.md` §14 (+ §7.1 cameras, §7.2 shot list), SLATE §3.5 / §5.1.
Test outputs: `workspace/jawad_reels/log_kya_kahenge/faces_test/` (stills, strips, range clips, QA boards, `qa/measure.json`).

The real stadium (`log_kya_kahenge_crowd.py`) and the reel module do not exist yet, so every still below was rendered on
**stand-in worlds** built to the BRIEF §7.1 geometry (10 tiers of flat seated silhouettes, barrier, floor, lamp bank, noir_ember
backdrop for S3-01; a dark 85 mm bokeh plate with amber phone glows and a warm left haze for S5-01), finished with
`G.finish(cv, 'noir_ember', t)` (`noir_ember` is registered in `jawad_grade.FIN`; no stand-in look). Re-run the numbers on the real
frames when the world exists (commands at the end).

## 1. Poses (only the two SLATE assigns to this reel; streetwear only, no mirroring, no swaps)

| pose | file | native -> 2x | face (native) | on screen | SR / matte / depth (licences) | defects and fixes |
|---|---|---|---|---|---|---|
| `street_threequarter_turn` | `charsheet/cutouts/street_threequarter_turn.png` (+ `_depth.png`, `.json`) | 410x1024 -> 820x2048 | 117 px | 560 px tall, scale 0.284 of the 2x master (0.57x native): mid/wide only, as required for a < 250 px face | Real-ESRGAN x4plus ONNX (BSD-3) -> area 2x; BiRefNet-portrait ONNX (MIT) + backdrop edge solve + pymatting; Depth-Anything-V2-**Small** (Apache-2.0) | none found (200 % board over black / FLAME / white: hand, watch, zip, laces, hair part clean). Texture: shown below native, no SR pull-back needed |
| `street_chinup_gaze` | `charsheet/cutouts/street_chinup_gaze.png` (+ `_depth.png`, `.json`) | 470x482 -> 940x964 | 212 px | bust 668-688 px wide, scale 0.750 -> 0.7725 of the 2x master (1.5x native): a medium close-up, not a full-frame close-up | same | (1) SR over-sharpened the face and waxed the cheeks: pulled back toward the source, `rgb = lanczos2x + 0.5 (sr - lanczos2x)` in the opaque interior only, kept at 16 bit; (2) a 6x4 px backdrop-grey speck in the hair crest (the matte filled a see-through gap): inpainted with the surrounding hair (`SPECKS`) |

No new model was downloaded; no non-commercial weights are used (no Depth-Anything Base/Large).

## 2. API (`import log_kya_kahenge_faces as LF`, after `import jawad_kit`)

| call | one-line use |
|---|---|
| `LF.prewarm()` | in the reel's `prewarm()`: builds both looks (~5 s, ~1 GB peak worker memory measured) |
| `LF.cam_s3(t)` | the S3-01 camera (9.6-12.8 s): render the WHOLE world of that shot with it (`K.background(LOOK, t, cam, ...)`, tiers, rays centre `cam.project(bank)`) |
| `LF.draw_s3(cv, cam, t)` | inside the world's scene: `sc.custom(LF.S3_FEET, lambda c, cm: LF.draw_s3(c, cm, t))` = floor contact shadow + JD plane (DOF from cam) + light wrap from what is behind him |
| `LF.draw_s5(cv, t)` | S5-01 (25.6-28.8 s): after the 85 mm plate, before the payoff lockup and captions |
| `LF.key_gain(t)` | warm key ignition per frame: 0 before f768, f768 0.6, f769 0.3, f770 0.9, f771 0.95, 1.0 from f772 (drive the world's warm light with the same value) |
| `LF.jd_rect(t, margin=28)` | caption avoid rect (x0, y0, x1, y1) or `None` outside his shots |
| `LF.jd_alpha(t)` | (1920, 1080) float32 screen matte of JD (QA, O6 masks), or `None` |
| `LF.s5_point(t, uv)` | screen px of a cut-out pixel in S5-01 (e.g. `LF.meta(LF.POSE_S5)['eye_mid']`) |
| `LF.FACES` | the shot table below |
| `python3 log_kya_kahenge_faces.py check` | limits, parallax, texture, placement, cost as JSON |

`draw_s3` / `draw_s5` take `mode='full' | 'plain' | 'alpha'` ('plain' = matte only, for halo QA). Everything is a pure function of
`t` (motion-blur samples at sub-frame times agree; `key_gain` is constant inside a frame).

## 3. Shot table (`LF.FACES`)

| shot | frames | pose | look | placement | camera / move | light | idle | avoid rect |
|---|---|---|---|---|---|---|---|---|
| S3-01 | f288-f383 (9.6-12.8 s; in under the O2 smoke, hard cut at f384) | `street_threequarter_turn`, faces screen-left | **D cine**: `cine_grade` (exposure 0.55) x crown 1.0 -> feet 0.8, `rim_light(light=(0.35, -0.95), gain 1.4, back 0.12, outline 0.04, depth_wrap 0.2, halo 0.18)`, rim emission faded 1.0 (shoulders) -> 0.3 (waist) -> 0 (hips and below) | plane at world (900, 0, 2500), 1800 mm tall, feet anchored, parallel to the sensor | `cam_s3`: pos (193, -h, -1614), h 1100 -> 1420 mm **linear**, pitch -3 -> +3 deg `inout_sine`, yaw 0, roll 0, focal 1280, aperture 10, focus 4114 | flat floodlight from the bank top-right, no cone, no pool; contact shadow on the floor (60 % under each sole, 45 % soft ellipse), 40 mm left; light wrap 5 px at 22 % | breathing only: height x(1 +- 0.25 %) about the feet, 0.29 Hz (no drift: the feet stay planted) | (658, 643, 863, 1260) at f288 -> (659, 879, 866, 1506) at f383 |
| S5-01 | f768-f863 (25.6-28.8 s; hard cut + clunk at f768, hard cut at f864) | `street_chinup_gaze`, looks up screen-left | **A rim**: `warm_dark` (0.42) = 24 % ambient + 76 % warm key from screen-left (lateral falloff 1.0 -> 0.30 + soft depth-normal shading; the right cheek falls off), `rim_light(light=(-0.9, -0.3), gain 2.4, back 0.3, outline 0.12)`; key + rim scaled by `key_gain` | pin: cut-out (470, 615) (bust centre at the beard's lowest point) at screen (700, 1617); eye-mid (641, 1371); hair crest y 1191 -> 1179; face x 558-814 | push 1.00 -> 1.03 `easy_ease` about the pin (scale 0.750 -> 0.7725); 2D over the CAM_JD plate | key ignites with the clunk; light falls off below the collar (x0.30 at the cut) and the panel-cut bottom fades out over its last 144 cut-out px (the bust ends at y 1879-1887 in the dark, under the IG caption zone); light wrap 16 px at 24 % | head = ONE rigid layer; torso layer breathes 0.4 % at 0.29 Hz (the head rides the neck, unscaled); sway <= 0.25 deg, drift <= 1.6 px | (339, 1162, 1064, 1908) at f768 -> (329, 1149, 1074, 1916) at f863 |

No expression swaps exist in this reel (two different framings 13 s apart, other shots between), so eye-locking does not apply;
each pose holds 3.2 s (limit 3.5 s).

## 4. Where this differs from BRIEF §14, and why (each is a never-uncanny limit or a composition rule)

1. **S3-01 camera (needs the timeline builder to use `LF.cam_s3`).** The brief's level pedestal 700 -> 2600 mm (`easy_ease`) at
   4114 mm from a flat plane changes the viewpoint on JD by 26 deg (looking 13.7 deg up at his head, then 12.3 deg down) and moves
   him against the tiers at 96-137 px/s on average and 477-675 px/s at the `easy_ease` peak, i.e. 9-13 %/s average and 44-62 %/s
   peak of the frame width per second against the limit of 3 %/s. A flat cut-out seen from 26 deg of new elevation reads as a
   standee, the exact thing this reel reveals about the crowd. `cam_s3` keeps a rise: a constant-speed pedestal of 320 mm at chest
   height (viewpoint change 4.45 deg) plus a 6 deg tilt-up (`inout_sine`; a pure rotation produces no parallax). Measured
   head-to-plate parallax, peak: row 0 16.7 px/s (1.54 %/s), row 9 23.6 (2.18 %/s), K.background reference plane 19.5 (1.81 %/s),
   lamp-bank distance 24.2 (2.24 %/s), even infinity 31.9 (2.95 %/s). On screen the stands and the lamp bank still slide down
   about 160-180 px while he slides 0.9-3.6 px per frame (measured on the rendered clip), and the floodlight bank enters the top of
   the frame at about 11 s, so the shot still reads as a rise. The floor occupies the lower ~40 % of the frame: the V2 caption band
   (y 1090-1405) sits on clean dark floor.
2. **S5-01 placement.** At the brief's anchor (bust bottom at (700, 1926), scale 0.75) the beard's lowest point (cut-out y
   608-615, below the YuNet face box the brief measured) lands at y ~1664, inside the bottom 300 px that IG covers. Keeping the
   brief's scale and x, the bust is pinned at the beard instead: face fully above y 1620 at every frame (max 1617.3 with the idle),
   eye-mid (641, 1371) instead of (641, 1419), crest 1191 instead of 1238. The bust then ends at y ~1880 above the frame bottom, so
   its lower chest falls off into darkness (the key is aimed at his face) and the panel cut fades out; the white tee and chains
   dissolve smoothly (looked at in every S5 still). The caption free band under the payoff lockup becomes y 841-1149 (308 px)
   instead of 841-1190; `jd_rect(t)` returns the exact rect per frame.
3. **Look strengths.** S3-01 keeps look D but with a low outline and counter-rim and no rim below the hips: with the brief's
   defaults the whole 560 px figure, legs and soles included, carried an orange outline that read as a sticker (first test
   still). S5-01 keeps look A (glowing flame outline, house style) with the counter-rim at 0.3 instead of 0.5 so the light plot
   holds: rim and key on the left, the right cheek falls off.
4. **"JD's chin lifts toward the warm light"** (shot list action) is not animated: a still cannot lift its chin without
   puppeting the face. The lift is sold by the clunk ignition on his face and rim (`key_gain`) and the 3 % push-in.
5. **No `FA.idle` drift on the full body** (the brief's "breathing only" holds; drift would slide the feet on the floor).

## 5. Measurements (stand-in worlds; `faces_test/qa/measure.json`, `python3 log_kya_kahenge_faces.py check`)

| check | S3-01 (f288 / f336 / f383) | S5-01 (f768 / f769 / f816 / f863) | limit |
|---|---|---|---|
| matte halo: 3 px ring outside the matte, plain cut-out minus plate, before the finish | +0.16 / +0.16 / +0.19 cv (p95 0.7-0.8) | +0.85 / +0.83 / +0.83 / +0.69 cv (p95 3.6-6.1) | <= +6 |
| same ring after the finish (bloom + halation of his own highlights, plain matte) | +6.6 / +6.9 / +7.6 | +4.8 / +4.8 / +5.0 / +4.7 | optical, not a fringe |
| ring with the full look (intended rim glow) | +4.8 / +5.0 / +5.0 | +47.7 / +29.9 / +66.8 / +66.5 (look A outline) | intended |
| 200 % edge boards over black / FLAME / white | `qa/edges_s3_threequarter_0.57x2.png`: no fringe; hand, watch, zip, laces intact | `qa/edges_s5_chinup_0.75x2.png`: no fringe; hair, beard, chains intact (crest speck fixed) | clean |
| blacks: JD p2 luma vs frame p2 (vs a 60 px neighbourhood) | 0 vs 0 (2.1 / 1.8 / 1.6) | 0 vs 0 (0) | within 2 cv |
| JD p99 luma vs the scene's brightest | 133-135 vs 214-253 (lamp bank) | 86-140 vs 172-201 | below the key |
| skin hue (median, p10-p90), face box | n/a (face 30 px) | 18.3 / 18.3 / 16.9 / 16.9 deg (14.1-19.7) | 8-29 deg |
| cheek texture, float luma Laplacian variance vs Lanczos 2x of the native crop | n/a (shown at 0.57x native) | right 3.66x raw -> 1.31x used, left 2.62x -> 1.12x | within 1.5x |
| camera | yaw 0, roll 0, pitch -3 -> +3 deg, viewpoint change 4.45 deg | locked; push 0.750 -> 0.7725, peak 4.57 %/s | 4 / 3 / 2 deg, <= 8 %/s |
| head-to-plate parallax, peak | 1.54-2.95 %/s (16.7-31.9 px/s) | eye moves <= 0.39 px/frame (push + idle) | <= 3 %/s |
| head screen motion, measured on the rendered clip (phase correlation) | 0.9-3.6 px/frame, smooth | <= 0.18 px/frame | |
| face rigidity under breathing | single plane | head region with breathing = pure translation of the unsplit sprite (max diff 9e-5 linear); split vs unsplit with no breathing: 88 px differ by <= 0.09 on the rim at the jaw line | rigid |
| display scale of the 2x master | 0.284 | 0.750-0.7725 | <= 1.0 |
| cost per draw (shared box, under load) | 44 ms | 135 ms (x3 motion-blur samples) | |

## 6. Stills and strips I looked at (all in `workspace/jawad_reels/log_kya_kahenge/faces_test/`)

- `stills/lkk_faces_test_009.60.png` (f288), `_011.20` (f336), `_012.77` (f383): JD stands small, centre-right, facing
  screen-left in front of the staring tiers; rim only on hair and shoulders; trainers grounded; the bank enters at the top.
- `stills/lkk_faces_test_025.60.png` (f768, key 0.6), `_025.63` (f769, key 0.3), `_027.20` (f816), `_028.77` (f863): chin-up bust,
  warm key from the left, right cheek falling off, pores and beard texture kept, hair crest clean, chest dissolving into the dark.
- `strip_s3.jpg` (f288-f291, f312, f336, f360, f380-f383) and `strip_s5.jpg` (f768-f771, f792, f816, f840, f860-f863) from
  `lkk_faces_test_9.60-12.80.mp4` / `lkk_faces_test_25.60-28.80.mp4` (3 motion-blur samples): no pops, no edge crawl, the
  ignition flicker reads, the push-in is smooth.
- `qa/edges_*.png` (200 %), `qa/face_*.png` (the S5 face box per still), `qa/plain_*.jpg` / `qa/none_*.jpg` (matte-only and
  no-JD renders used for the ring numbers).

## 7. Notes for the timeline builder and the caption designer

- S3-01: build the shot's world with `LF.cam_s3(t)` (not the brief's `CAM_RISE` numbers) and put JD in the same `K.Scene` via
  `sc.custom(LF.S3_FEET, ...)`; the field floor must be drawn before him (the contact shadow is drawn on top of what is there).
  Keep the haze BEHIND him (between him and the tiers), dust in front is fine. `rays_center = cam.project(bank)` with `cam_s3`.
- S5-01: `LF.draw_s5(cv, t)` after the plate; no particles or embers in front of the face; use `LF.key_gain(t)` for the
  plate's warm light (`boost`) so the world and his rim ignite together.
- Captions: `avoid` should call `LF.jd_rect(t)` for 9.6-12.8 and 25.6-28.8 (plus 29.1 + tail for V6, as the brief says); the
  S5 rect top is now y 1149-1162.
- Re-measure on the real frames: `heavy.sh python3 render.py log_kya_kahenge --stills 9.6,11.2,12.7667,25.6,25.6333,27.2,28.7667
  --workers 1`, then the same ring / black / skin numbers. The stand-in harness and the measure script are kept in
  `faces_test/tools/` (`lkk_faces_test.py`, `measure.py`: a 'plain' render, a no-JD render and `LF.jd_alpha(t)`; run with
  `PYTHONPATH=<that folder> heavy.sh python3 render.py lkk_faces_test --stills ...` after linking
  `workspace/jawad_reels/out/lkk_faces_test -> ../log_kya_kahenge/faces_test`, and `heavy.sh python3 measure.py t1,t2,...`).

## 8. Open questions

1. **AI disclosure:** the character sheets look AI-generated (and the VO is synthetic): Meta's AI label on this reel is the lead's
   call (SLATE default: label ON).
2. **Brief deviation 1 (S3 camera)** needs the lead / timeline builder to adopt `LF.cam_s3`; if the brief's big pedestal is wanted,
   it needs a real back-lit silhouette or a 3D body, not a cut-out.
3. **Missing angles:** no back or profile view of the streetwear look, and no streetwear bust facing the lens; S3 therefore can
   only be seen from the front, close to the photo's own chest-height viewpoint.
