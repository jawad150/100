# FACES: Reel 5 · C15 · Log Kya Kahenge (face-compositor)

Date 2026-10-09 (r2; r1 2026-10-08) · Author: face-compositor · Code: `pipeline/jawad_reels/log_kya_kahenge_faces.py` (the reel
module imports it and never edits it; it never edits the shared toolkit) · Plan source: `BRIEF.md` §14 (+ §7.1 cameras, §7.2 shot
list), SLATE §3.5 / §5.1. Test outputs: `workspace/jawad_reels/log_kya_kahenge/faces_test/` (stills, strips, range clips,
`qa/measure.json`, `qa/motion_*.json`; scripts in `faces_test/tools/`).

**r2 changes (2026-10-09):** re-verified against BRIEF r2 + VO_TIMING (no face beat moved: V2 8.80-14.01 plays over S3-01, V6
26.00-28.95 over S5-01 and across the f864 cut, as planned). New `LF.s3_rays()`: G.finish's god rays used JD's white tee, hand and
trainers as ray sources (a faint light trail down-left of his legs, p99 +6 / max +9 code values); JD is now held out as a source.
That was also the whole "+6.6-7.6 after the finish" S3 halo number of r1: it is now +0.4-0.7. Shared request R5 filed. Shot table
label fixed (S3 tilt ease is `inout_sine`, as coded). Every still, strip and range clip in §6 (except the r1 edge boards) was re-rendered
today through `tools/heavy.sh` and looked at.

The stadium module and the reel module do not exist yet, so all stills are on **stand-in worlds** built to BRIEF §7.1 geometry
(10 tiers of flat seated silhouettes, barrier, floor, lamp bank, noir_ember backdrop for S3-01; a dark 85 mm bokeh plate with
amber phone glows and a warm left haze for S5-01), finished with `G.finish(cv, 'noir_ember', t)` (`noir_ember` is registered in
`jawad_grade.FIN`; no stand-in look). Re-run the numbers on the real frames when the world exists (commands in §7).

## 1. Poses (only the two SLATE assigns; streetwear only, no mirroring, no swaps)

| pose | file | native -> 2x | face (native) | on screen | SR / matte / depth (licences) | defects and fixes |
|---|---|---|---|---|---|---|
| `street_threequarter_turn` | `workspace/brand_reels/charsheet/cutouts/street_threequarter_turn.png` (+ `_depth.png`, `.json`) | 410x1024 -> 820x2048 | 117 px | ~560 px tall, scale 0.284 of the 2x master (0.57x native): wide only, as required for a < 250 px face | Real-ESRGAN x4plus ONNX (BSD-3) -> area 2x; BiRefNet-portrait ONNX (MIT) + backdrop edge solve + pymatting; Depth-Anything-V2-**Small** (Apache-2.0) | none (200 % board over black / FLAME / white `qa/edges_s3_threequarter_0.57x2.png`: hand, watch, zip, laces, hair part clean). Shown below native: no SR pull-back needed |
| `street_chinup_gaze` | `.../cutouts/street_chinup_gaze.png` (+ `_depth.png`, `.json`) | 470x482 -> 940x964 | 212 px | bust 668-688 px wide, scale 0.750 -> 0.7725 of the 2x master (1.5x native): medium close-up, never full-frame | same | (1) SR over-sharpened and waxed the cheeks: pulled back toward the source in the opaque interior, `rgb = lanczos2x + 0.5 (sr - lanczos2x)`, 16 bit (`TEX_K`); (2) a 6x4 px backdrop-grey speck in the hair crest inpainted with the hair (`SPECKS`). Remaining light dots on the crest are real strand sheen (checked at 6x) |

No new model was downloaded; no non-commercial weights (no Depth-Anything Base/Large).

## 2. API (`import jawad_kit` first, then `import log_kya_kahenge_faces as LF`)

| call | one-line use |
|---|---|
| `LF.prewarm()` | in the reel's `prewarm()`: builds both looks (~5 s, worker peak ~1 GB) |
| `LF.cam_s3(t)` | the S3-01 camera (9.6-12.8 s): render the WHOLE world of that shot with it (`K.background(LOOK, t, cam, ...)`, tiers, `rays_center = cam.project(bank)`) |
| `LF.draw_s3(cv, cam, t)` | inside the world's scene: `sc.custom(LF.S3_FEET, lambda c, cm: LF.draw_s3(c, cm, t))` = floor contact shadow + JD plane (DOF from cam) + light wrap from what is behind him |
| `LF.s3_rays(cv, t, centre, 0.22)` | **new**, in `post` for 9.6-12.8 BEFORE the finish: the floodlight god rays with JD held out as a source; then call the finish with `rays=0` for that window (no-op outside it). +~30 ms over the finish's own rays |
| `LF.draw_s5(cv, t)` | S5-01 (25.6-28.8 s): after the 85 mm plate, before the payoff lockup and captions |
| `LF.key_gain(t)` | warm key ignition: 0 before f768, f768 0.6, f769 0.3, f770 0.9, f771 0.95, 1.0 from f772 (drive the plate's warm light / `boost` with it) |
| `LF.jd_rect(t, margin=28)` | caption avoid rect (x0, y0, x1, y1), `None` outside his shots (f287, f384, f767, f864 all return `None`) |
| `LF.jd_alpha(t)` | (1920, 1080) float32 screen matte of JD (QA, masks), or `None` |
| `LF.s5_point(t, uv)` | screen px of a cut-out pixel in S5-01 (e.g. `LF.meta(LF.POSE_S5)['eye_mid']`) |
| `LF.FACES` | the shot table below |
| `python3 log_kya_kahenge_faces.py check` | limits, parallax, texture, placement, cost as JSON |

`draw_s3` / `draw_s5` take `mode='full' | 'plain' | 'alpha'` ('plain' = matte only, for halo QA). Everything is a pure function of
`t` (motion-blur sub-samples agree; `key_gain` is constant inside a frame).

Post wiring for the timeline builder (BRIEF §17.2 `post`):
```python
def post(cv, t):
    r = rays(t)
    if LF.S3_T0 <= t < LF.S3_T1:                 # S3-01: JD must not emit rays
        LF.s3_rays(cv, t, rays_centre(t), r); r = 0.0
    return G.tx_finish(cv, t, LOOK, cuts=..., **merge(...), rays=r, rays_center=rays_centre(t))
```

## 3. Shot table (`LF.FACES`)

| shot | frames | pose | look | placement | camera / move | light | idle | avoid rect |
|---|---|---|---|---|---|---|---|---|
| S3-01 | f288-f383 (9.6-12.8 s; in under the O2 smoke, hard cut at f384) | `street_threequarter_turn`, faces screen-left | **D cine**: `cine_grade` (exposure 0.55) x crown 1.0 -> feet 0.8, `rim_light(light=(0.35, -0.95), gain 1.4, back 0.12, outline 0.04, depth_wrap 0.2, halo 0.18)`, rim faded 1.0 (shoulders) -> 0.3 (waist) -> 0 (hips down) | plane at world (900, 0, 2500), 1800 mm tall, feet anchored, parallel to the sensor | `cam_s3`: pos (193, -h, -1614), h 1100 -> 1420 mm linear, pitch -3 -> +3 deg `inout_sine`, yaw 0, roll 0, focal 1280, aperture 10, focus 4114 | flat floodlight from the bank top-right, no cone, no pool; contact shadow on the floor (60 % under each sole, 45 % soft ellipse) 40 mm left; light wrap 5 px at 22 %; not a ray source (`s3_rays`) | breathing only: height x(1 +- 0.25 %) about the feet, 0.29 Hz | (658, 643, 863, 1260) f288 -> (659, 879, 866, 1506) f383 |
| S5-01 | f768-f863 (25.6-28.8 s; hard cut + clunk at f768, hard cut at f864) | `street_chinup_gaze`, looks up screen-left (toward the `LOG / busy / HAIN.` lockup) | **A rim**: `warm_dark` (0.42) = 24 % ambient + 76 % warm key from screen-left (lateral falloff 1.0 -> 0.30, soft depth-normal shading; right cheek falls off), `rim_light(light=(-0.9, -0.3), gain 2.4, back 0.3, outline 0.12)`; key + rim x `key_gain` | pin: cut-out (470, 615) (beard bottom) at screen (700, 1617); eye-mid (641, 1371) -> (639, 1364); face box x 553-817, y 1246-1575; crest y 1191 -> 1179 | push 1.00 -> 1.03 `easy_ease` about the pin (scale 0.750 -> 0.7725); 2D over the CAM_JD plate; no rays (BRIEF: 0 in 25.6-33.6) | key ignites with the clunk; light falls off below the collar; panel-cut bottom fades out over its last 144 cut-out px (bust ends ~y 1880 in the dark); light wrap 16 px at 24 % | head = ONE rigid layer; torso layer breathes 0.4 % at 0.29 Hz (head rides the neck, unscaled); sway <= 0.25 deg, drift <= 1.6 px | (339, 1162, 1064, 1908) f768 -> (329, 1149, 1074, 1916) f863 |

No expression swaps in this reel (two framings 13 s apart with other shots between), so eye-locking does not apply; each pose holds
3.2 s (limit 3.5 s).

## 4. Where this differs from BRIEF §14 (each one is a never-uncanny limit or a composition rule; unchanged from r1)

1. **S3-01 camera: use `LF.cam_s3`, not the brief's CAM_RISE.** The brief's level pedestal 700 -> 2600 mm (`easy_ease`) changes the
   viewpoint on a flat cut-out by 26 deg and slides him against the tiers at 9-13 %/s of frame width on average (44-62 %/s at the
   ease peak) against the 3 %/s limit: a standee. `cam_s3` keeps a rise: a constant-speed 320 mm pedestal (viewpoint change
   4.45 deg) + a 6 deg tilt-up (pure rotation, no parallax). Head-to-plate parallax peak: row 0 1.54 %/s, row 9 2.18, backdrop
   1.81, lamp bank 2.24, infinity 2.95 (limit 3). The stands still slide down ~160-180 px and the lamp bank enters at ~11 s.
2. **S5-01 placement.** At the brief's anchor (bust bottom (700, 1926)) the beard bottom lands at y ~1664, inside the bottom 300 px;
   pinned at the beard instead (same scale and x): face fully above y 1620 at every frame (max 1617.3). Caption free band under
   the payoff lockup = y 841-1149 (not 841-1190): use `LF.jd_rect(t)`, not the brief's fixed (330, 1190, 1073, 1954).
3. **Look strengths.** S3: low outline / counter-rim and no rim below the hips (a full glowing outline on a 560 px figure read as a
   sticker). S5: counter-rim 0.3 instead of 0.5 so the light plot holds (key + rim left, right cheek falls off).
   *Build note (motion-timeline-builder, 2026-10-09, HANDOFF risk 9 checked on the real plate):* after the finish the outline +
   counter-rim still saturated to an even stroke on both sides (rendered edge luma left 209-214, right 107-112), so `_s5_layers`
   now multiplies the rim emission by a lateral falloff, 1.0 left of the face centre (cut-out x 450) to 0.25 at x 741: left rim
   unchanged, right edge 60-75. The rim parameters above are otherwise unchanged.
4. **"JD's chin lifts toward the warm light"** is not animated (a still cannot lift its chin without puppeting the face): sold by
   the clunk ignition on his face and rim plus the 3 % push-in.
5. **No `FA.idle` drift on the full body** (drift would slide the feet on the floor).

## 5. Measurements (stand-in worlds, 2026-10-09; `faces_test/qa/measure.json`, `qa/motion_*.json`, `check`)

| check | S3-01 (f288 / f336 / f383) | S5-01 (f768 / f769 / f772 / f816 / f863) | limit |
|---|---|---|---|
| matte halo: 3 px ring outside the matte, plain cut-out minus no-JD plate, before the finish | +0.16 / +0.16 / +0.18 cv (p95 0.7-0.8) | +0.85 / +0.83 / +0.80 / +0.83 / +0.69 (p95 3.6-6.1) | <= +6 |
| same ring after the finish (bloom + halation of his own highlights) | **+0.41 / +0.50 / +0.74** (r1 without the ray hold-out: +6.6-7.6) | +4.8 / +4.8 / +4.8 / +5.0 / +4.7 | <= +6 |
| ring with the full look (intended rim glow) | +3.9 / +4.0 / +4.1 | +47.7 / +29.9 / +68.1 / +66.8 / +66.5 (look A outline) | intended |
| ray trail beside his legs (floor band, full look minus no-JD) | mean +0.05 / +0.06 / +0.04, p99 2.7-3.0 (JPEG + grain noise) (r1: +1.2 mean, p99 +6, max +9) | n/a (no rays) | none |
| blacks: JD p2 luma vs frame p2 (vs a 60 px neighbourhood) | 0 vs 0 (2.0 / 1.8 / 1.6) | 0 vs 0 (0) | within 2 cv |
| JD p99 luma vs the scene's brightest | 132-133 vs 214-253 (lamp bank) | 86-140 vs 172-204 | below the key |
| skin hue in the face box (median, p10-p90) | n/a (face ~30 px) | 18.3 / 18.3 / 16.9 / 16.9 / 16.9 deg (14.1-19.7); sat 0.47-0.48 | 8-29 deg |
| cheek texture, float-luma Laplacian variance vs Lanczos 2x of the native crop | n/a (0.57x native) | right 3.66x raw -> 1.31x used, left 2.62x -> 1.12x | within 1.5x |
| camera | yaw 0, roll 0, pitch -3 -> +3 deg, viewpoint change 4.45 deg | locked; push 0.750 -> 0.7725, peak 4.57 %/s | 4 / 3 / 2 deg, <= 8 %/s |
| head-to-plate parallax, peak | 0.56-1.06 px/frame (1.54-2.95 %/s) | eye <= 0.39 px/frame (push + idle) | <= 3 %/s |
| head screen motion on the rendered clip (phase correlation) | 0.87-3.29 px/frame (analytic peak 3.26), frame-to-frame change <= 0.35 px: smooth | 0-0.51 px/frame, change <= 0.31 | no pops |
| face rigidity | single plane | head = pure translation of the unsplit sprite under breathing (max diff 9e-5 linear) | rigid |
| display scale of the 2x master | 0.284 | 0.750-0.7725 | <= 1.0 |
| composition | JD x 658-866 (clear of x > 930), feet <= y 1478 | face x 553-817 (clear of x > 930), face bottom <= 1617.3 (clear of y > 1620); lockup ink bottom y 813 -> hair crest 1179 (366 px); caption band bottom 1149 -> face box top 1246 (97 px) | >= 60 px copy-to-face |
| cost per draw (shared box, under load) | 32-44 ms; `s3_rays` 216 ms total, i.e. +~30 ms over the finish's own rays | 137-191 ms | |

## 6. Stills and strips I looked at (all in `workspace/jawad_reels/log_kya_kahenge/faces_test/`, rendered 2026-10-09)

- `stills/lkk_faces_f0288.png` (S3 in), `f0336` (mid), `f0383` (out) + `*_jd200.png` (JD at 200 %): JD small, centre-right, facing
  screen-left in front of the staring tiers; rim only on hair and shoulders; trainers grounded with the contact shadow; no light
  trail beside his legs any more; the lamp bank enters at the top by f336.
- `stills/lkk_faces_f0768.png` (S5 in, key 0.6), `f0769` (0.3), `f0770` (0.9), `f0772` (1.0), `f0816` (mid), `f0863` (out) +
  `*_face200.png` (face at 200 %): chin-up bust, warm key from the left, right cheek falling off, pores and beard hairs kept
  (no wax), hair crest clean, chest dissolving into the dark, face clear of the IG zones.
- `strip_beats.jpg` (all nine beat frames), `strip_s3.jpg` (f288-f291, f335, f380-f383) and `strip_s5.jpg` (f768-f771, f815,
  f860-f863) from `range_s3_f288-f383.mp4` / `range_s5_f768-f863.mp4` (3 motion-blur samples): no pops, no edge crawl, the ignition
  flicker reads, the push-in is smooth.
- `qa/edges_*.png` (200 % boards over black / FLAME / white; from r1 2026-10-08, the cut-out path is unchanged), `qa/face_*.png`, `qa/plain_*.jpg` / `qa/none_*.jpg` (matte-only and
  no-JD renders for the ring numbers); hair crest checked at 6x (strand sheen, no backdrop speck).

## 7. Notes for the timeline builder and the caption designer

- S3-01: build the shot's world with `LF.cam_s3(t)` and put JD in the same `K.Scene` via `sc.custom(LF.S3_FEET, ...)`; the field
  floor must be drawn before him. Haze BEHIND him (between him and the tiers); dust in front is fine. In `post`, `LF.s3_rays` then
  the finish with `rays=0` for 9.6-12.8 (snippet in §2).
- S5-01: `LF.draw_s5(cv, t)` after the plate; no particles or embers in front of the face; use `LF.key_gain(t)` for the plate's warm
  light so the world and his rim ignite together.
- Captions: `avoid` calls `LF.jd_rect(t)` for 9.6-12.8 and 25.6-28.8; for V6's tail across f864 (to <= 29.10 + tail) keep the
  last S5 rect `LF.jd_rect(28.7667)` = (329, 1149, 1074, 1916) so a chunk spanning the cut does not jump (BRIEF §15).
- Re-measure on the real frames: `tools/heavy.sh python3 render.py log_kya_kahenge --stills 9.6,11.2,12.7667,25.6,25.6333,25.7333,
  27.2,28.7667 --workers 1`, then the ring / black / skin numbers with `faces_test/tools/measure.py` adapted to the reel module
  (it renders 'full', 'plain' and 'none' through `LKK_FT_MODE` on the stand-in; the reel needs the same three switches or
  `LF.jd_alpha(t)` + a no-JD render). Stand-in tools: `faces_test/tools/{lkk_faces_test,stills,range,measure}.py`
  (`heavy.sh python3 stills.py [frames]`, `heavy.sh python3 range.py f0 f1 name`, `heavy.sh python3 measure.py t1,t2,...`).

## 8. Open questions

1. **AI disclosure:** the character sheets look AI-generated and the VO is synthetic: Meta's AI label is the lead's call (SLATE
   default: label ON).
2. **S3 camera deviation** needs the timeline builder to adopt `LF.cam_s3`; the brief's big pedestal would need a real back-lit
   silhouette or a 3D body, not a cut-out.
3. **Shared request R5** (god-ray source hold-out) is filed in `SHARED_REQUESTS.md`; the local `LF.s3_rays` covers it until then.
4. **Missing angles:** no back or profile view of the streetwear look and no streetwear bust facing the lens; S3 can only be seen
   from the front, close to the photo's own chest-height viewpoint.
