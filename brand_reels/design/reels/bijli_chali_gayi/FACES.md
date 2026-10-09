# FACES · Reel 2 · C11 · Bijli Chali Gayi (face-compositor)

2026-10-09. Built from BRIEF.md §6.13 (face plan), §6.2 (S7b, S8a), §6.8 (L4 at f880), §6.9 (camera law, candle), SLATE
§3.2 / §5 and `brand_reels/research/face_assets.md`. Look `dusk` is registered in `jawad_grade` (real look, no stand-in).
Every number below was measured on renders through `G.tx_finish(..., 'dusk', cuts=CUTS)` (the brief's CUTS) and the real
`jawad_tx` L4.

## 1. Files

| what | path |
|---|---|
| face module (import it; never edit it from the reel) | `pipeline/jawad_reels/bijli_chali_gayi_faces.py` (`BF`) |
| test harness (stand-in worlds, render.py-compatible, QA) | `pipeline/jawad_reels/bijli_chali_gayi_faces_preview.py` (not production art) |
| test outputs | `workspace/jawad_reels/bijli_chali_gayi/out/faces_preview/` (symlinked as `<WS>/out/bijli_chali_gayi_faces_preview`) |
| source assets (read only, nothing new downloaded) | `workspace/brand_reels/charsheet/cutouts/suit_profile.*`, `suit_smiling.*`, `crops/suit_*.png` |

Assets and licences (from `face_assets.md`; no new weights were fetched for this reel): Real-ESRGAN x4plus ONNX 2x
masters (BSD-3), BiRefNet-portrait matte (MIT) + pymatting decontamination, Depth-Anything-V2-**Small** depth (Apache-2.0),
YuNet landmarks (MIT). Poses: `suit_profile` 355x556 native -> 710x1112 (face 202 px native), `suit_smiling` 355x561 ->
710x1122 (face 213 px native). Both shown at display scale **1.0** of the 2x master (the cap); never above.

## 2. API (one line each)

```python
import jawad_kit; import bijli_chali_gayi_faces as BF   # jawad_kit FIRST
BF.prewarm()                                    # builds both looks once per worker (~4 s)
cam = BF.cam_s7b(t)                             # S7b shot camera: render the WHOLE S7b world through it (K.Scene / draw_plane)
BF.plate_shift(t, z)                            # (dx, dy) for a 2D-drawn S7b layer at depth z (no roll) if not using cam
BF.draw_s7b(cv, t, cam=cam, flicker=BF.candle_flicker(t))   # JD profile over the world already in cv (in place)
BF.candle_flicker(t)                            # +-8 % candle level; use the SAME call for the flame's brightness
BF.draw_s8a(cv, t, cam=BF.cam_s8a(), key=1.0)   # JD smiling over the lit room; key = tube state (0 off .. 1 on)
BF.draw(cv, t)                                  # whichever shot owns t (frame rule), no-op elsewhere
BF.jd_rect(t) / BF.head_rect(t)                 # caption avoid rects (+28 px), None outside the shots
BF.jd_alpha(t)                                  # (1920, 1080) float32 matte of JD on screen (QA masks)
BF.eye_screen(t)                                # screen eye midpoint (eye lock / QA)
BF.FACES                                        # shot table below
# python3 bijli_chali_gayi_faces.py check       -> limits / parallax / texture / cost JSON
# tools/heavy.sh python3 render.py bijli_chali_gayi_faces_preview --stills 25.5,29.6 --workers 1
# tools/heavy.sh python3 bijli_chali_gayi_faces_preview.py qa   -> out/faces_preview/qa.json + face / edge crops
```

Constants for the builder: `BF.FOCAL = 3825` (85 mm on the 1080 width), `BF.APERTURE = 64` (wall at `BF.Z_WALL = 3825`
gets CoC r 16 px), `BF.Z_CANDLE = 150` (S7b candle depth), `BF.CANDLE_XY = (800, 1130)` (the face light is built for a
flame there; move the flame and the light no longer matches).

## 3. Shot table (`BF.FACES`)

| shot | frames (s) | pose | look | P = eye_mid on screen | scale | camera | rim | on screen |
|---|---|---|---|---|---|---|---|---|
| S7b | f740-f839 (24.667-27.967) | suit_profile | A rim, candle | (440, 1210) | 1.0 | `cam_s7b`: BRIEF §6.9 drift capped 4 px / 0.3 deg (translation + roll; yaw = pitch = push = 0) | light (0.85, -0.15), gain 2.0, falls off from the flame | 3.33 s |
| S8a | f880-f919 (29.333-30.633) | suit_smiling | A rim, tube + CRT | (540, 1150) | 1.0 | `cam_s8a`: locked | light (-0.6, -0.8), gain 2.4, RED counter-rim 0.30 | 1.33 s |

Layout (measured on the renders): profile face box (222, 1069, 509, 1474), hair crest y 884 (lockup ink ends y 783:
101 px clear; face box 286 px clear), bust bottom y 1929.8 minimum; `head_rect` (0, 818, 601, 1535), `jd_rect` (0, 856,
547, 1920). Smiling face box (333, 984, 681, 1410), bust bottom y 1936.1, `head_rect` (228, 786, 786, 1473), `jd_rect`
(114, 831, 881, 1920). No face pixel at x > 930 or in the bottom 300 px; nothing crosses either face.

## 4. How each shot is built

- **Layers (2.5D, no warps):** torso layer + head layer (hair, ears, face, beard as ONE rigid plane, split along a neck
  polyline read off the cut-out; exact recombination at rest). Each is a `K.draw_plane` at its own depth through the shot
  camera: head z = 0 (focus on the eyes), torso z from the Depth-Anything medians (profile -189, smiling -124 world
  units: the depth map puts the near shoulder / chest nearer than the head), widths set so both project at exactly 1.0.
  Composited in photo-occlusion order (head over torso). DOF from the camera: head CoC 0, torso 1.1-1.7 px, wall 16 px.
- **Breathing:** torso only, vertical 1.000 -> 0.996 about the bust bottom (compress-only, so display scale never
  exceeds 1.0), 0.29 Hz; the head rides the neck (<= 1.7 px), never scales, never rotates on its own.
- **Light (2D only, never a depth relight):** warm-dark base (exposure 0.50 / 0.52) x a light shape: S7b horizontal
  0.40 -> 1.0 toward the flame (smoothstep^1.6) + warm tint (1.0, 0.86, 0.70) on the lit side + chest falloff to 0.35;
  S8a diagonal 1.0 -> 0.72 from the top-left tube + warm-white tint + chest falloff to 0.45. 25-30 % ambient, the rest
  is the key (S7b key, rim and glow track `candle_flicker`; S8a key follows `key=`).
- **Rim look A:** `FA.rim_light` emission (no default all-round halo) + a halo outside the silhouette on the LIT side
  only. S7b rim and glow fall off with distance from the flame (1.0 within 310 px, power 1.5): nose / lips / brow strong,
  hair top and chest edge ~0.3. Max linear emission 2.27 (S7b) / 2.83 (S8a), under the 3x cap.
- **Light wrap:** the world behind him blurred (sigma 30) screened over his outer 14 / 16 px at 22 / 24 %.
- **Panel cuts:** profile's cut left side and bottom sit off-frame; smiling's cut shoulders fade over 12 % of the width
  (as `FA.fade_open`) into the dark; bottoms below y 1920 in every frame.
- **Texture (human-realism / photo-realism):** x4plus made the suit cheeks 6.7-7.2x the Laplacian variance of a Lanczos
  2x of the native crop. The SR detail is pulled back toward the native photo on SKIN ONLY (HSV skin mask, feathered 3 px):
  k = 0.35 (profile), 0.25 (smiling). Eyes, lashes, brows, beard, hair and suit keep full SR detail. No smoothing, no
  sharpening, no grain of our own (grain comes from the `dusk` finish only).
- **Contact shadow:** not used: both are busts anchored below the frame (no ground in shot). `FA.contact_shadow` stays
  available if a later cut shows a surface under him.

## 5. Measurements

| check | S7b (suit_profile) | S8a (suit_smiling) | limit |
|---|---|---|---|
| matte fringe over the REAL plate (halo_cv method: composite minus interior-extended colour, 3 px ring outside alpha 0.5) | -0.48 (p95 +2.13) | -0.84 (p95 +2.68) | <= +6 |
| same over pure black | -0.88 (p95 +2.88) | -1.25 (p95 +3.48) | <= +6 |
| final ring minus plate (designed rim + glow) / share of the brightened ring px that is red-orange / low-saturation | +37 to +43 / 98.4-99.5 % / 0 % | +40 / 92 % / 1.8 % | no grey halo |
| black match: JD p2 minus scene p2 (finished, grain off) | -1.5 to -1.8 | +1.07 (f900, f919) | within 2 |
| JD p99.5 luma vs the scene key max | 154-171 vs 244-255 (flame) | 169 vs 251 (tube) | below the key |
| eye midpoint, max distance from P over the shot | 2.12 px | 1.58 px | 6 px (brief) |
| camera, measured over the shot | drift <= 1.06 px x, 1.03 px y, roll <= 0.058 deg | 0 | yaw 4, pitch 3, roll 2 deg |
| head speed / torso speed / head-vs-torso (px per frame, peak) | 0.085 / 0.087 / 0.039 | 0.056 / 0.018 / 0.037 | |
| head-to-plate parallax, peak (wall z 3825) | 1.78 px/s = 0.165 % W/s | 1.68 px/s (breathing only) | 3 % W/s |
| display scale head / torso | 1.000 / 1.000 (breath min 0.996) | 1.000 / 1.000 (0.9965) | <= 1.0 |
| cheek texture vs Lanczos 2x: SR -> used (two cheek patches) | 4.90 -> 1.25, 6.72 -> 1.45 | 7.17 -> 1.26, 6.79 -> 1.43 | within 1.5x |
| same in the final frame (grain off; shipped sprite vs a full-Lanczos sprite, same look) | 1.11 | 1.15 | within 1.5x |
| skin (`G.skin_stats`, face box): source -> final, HSV hue / OKLab L, C, h | 12.7 -> 15.5 deg / 74.4 -> 54.5, 6.2 -> 6.3, 36.5 -> 40.8 | 9.9 -> 12.7 deg / 72.5 -> 56.1, 6.4 -> 6.1, 32.4 -> 35.5 | natural, not orange (orange >= 25 deg), never lighter |
| `draw` cost per call (1 sample) | 162 ms | 168 ms | |

At f880 (the L4 halation peak) the whole frame is lifted by the transition (JD p2 42 vs scene p2 13, skin L 79): that is
the bloom-out, back to the f900 numbers by f889.

## 6. Stills and strips looked at (all Read at full size)

`out/faces_preview/stills/bijli_chali_gayi_faces_preview_{024.67,025.50,026.33,027.33,027.97,029.33,029.60,030.00,030.63}.png`
(S7b first / brief still / mid / lockup / last; S8a f880 L4 peak / brief still 29.6 / mid / last), contact sheet
`out/faces_preview/sheet_stills.jpg`; strips of every frame within +-0.4 s of the face cuts:
`out/faces_preview/strip_f828-f852.jpg` (S7b -> S7c hard cut at f840: clean, no ghost) and `strip_f868-f892.jpg`
(S7c -> L4 -> S8a at f880: JD appears only on f880, inside the bloom; no dissolve, no double face). Face crops for the
colorist's skin check: `out/faces_preview/face_{s7b,s8a}_*_f*.png`; 200 % edge crops `edge200_*.png`; matte edge board
over black / FLAME / white `edge_board_bw_flame.png`; texture A/B `tex_suit_*_sr_vs_lanczos.png`; numbers `qa.json`.

What I fixed after looking: a sticker-like orange outline round the whole silhouette (all-round outline / halo cut,
side halo only, candle falloff on the S7b rim so the hair top and chest stop glowing), a too-flat candle light on the
profile (gradient 0.40 -> 1.0 with a curve, chest falloff), over-sharp SR skin (skin-only pull-back), a NaN and a
clipped-halo box in the stand-in flame, a missing wall strip in the S7c stand-in.

## 7. Deviations from BRIEF §6.13 (and why)

1. **Candle gradient 0.40 -> 1.0** (brief 0.55 -> 1.0): the flame sits in front of his face, so the visible side of a
   profile is lit at grazing angles; at 0.55 the ear and cheek read as the photo's flat studio light ("pasted").
2. **No `FA.idle(seed=5/6)`:** idle's 3 px drift + 0.5 deg sway on top of the S7b camera drift moves the whole cut-out
   like a puppet and pushed the eye past the brief's +-6 px. Motion = the brief's camera drift (S7b) + torso-only
   breathing; the head never rotates on its own.
3. **No 1.00 -> 1.03 push-in on S8a:** the reel's camera law locks the camera while the power is on (QA: 0 px offset
   from 4 frames after f880) and the pose is already at the 1.0 scale cap; the L4 bloom and the finish's exposure push
   sell the cut.
4. **No eye-locked swap pair:** there is no face-to-face cut in C11 (S7c, 40 frames of candle, sits between the profile
   and the smile). Eye positions are the brief's P values: (440, 1210) and (540, 1150), 116 px apart across S7c.
5. **Rim falloff and lit-side halo** instead of `FA.rim_light`'s default all-round outline / halo (realism; brand rim
   kept on the lit edges).

## 8. Notes for the timeline builder (bijli_chali_gayi.py)

- Render the S7b world (wall, candle, sparks) with `BF.cam_s7b(t)` and draw JD with the same `cam`; a world drawn
  without it leaves JD drifting over a static plate (the opposite of 2.5D). Use `BF.candle_flicker(t)` for the flame.
- Measured on the shared `K.wiggle`: the brief's drift with the 4 px / 0.3 deg cap moves only ~1 px / 0.06 deg over S7b.
  That is the camera law as written; if the director wants a visibly handheld S7b, raise it in the brief (the eye budget
  allows ~3 px more).
- The payoff lockup (`out_t0=29.0`, 0.35 s exit) is still at ~14 % on f880 (gone on f881), over the room above his head
  (no face overlap). The brief says "gone by f880": use `out_t0=28.98` or less if that matters.
- `draw_s8a(..., key=)`: pass the tube's per-frame state if the strike flickers (mains snap, never fade).
- Captions: pass `BF.head_rect(t)` / `BF.jd_rect(t)` as `avoid` (they include the profile's back hair, x from 0).
- The suit_smiling hair crest has a few see-through specks at its left fringe (visible on flat FLAME / white at 200 %,
  covered by the rim on the room plate; check if the S8a background is ever bright behind his crown).

## 9. Open questions

- AI label: the character sheets look AI-generated and the voice is synthetic: SLATE §7.1 default (label on) stands;
  the lead decides.
- No new angles are needed for C11; a frontal "candle-lit" smile does not exist on the sheets (S8a is lit-room only).
