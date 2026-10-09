# FACES · Reel 1 · C26 `pehle_wala` · JD's reaction-cam tile

Author: face-compositor · 2026-10-09 · Status: **built and measured**. Plan: BRIEF.md §5.1, §7 (#21, #24, #44, #47), §14.
Code: `pipeline/jawad_reels/pehle_wala_faces.py` (the reel imports it, never edits it). Look: `inferno`, registered by
`jawad_grade` (no stand-in look). Faces: `street_sunglasses` (v16) and `street_smirk` (hero, payoff + cover), the only
two cut-outs SLATE gives this reel. One wardrobe (streetwear), no mirroring, no swap inside a showing.

## 1. API (pure functions of t; sprites premultiplied linear, screen px)

```python
import jawad_kit                      # first
import jawad_grade as G               # registers 'inferno'
import pehle_wala_faces as PF
PF.prewarm()                          # in prewarm(): both poses' layers, ~2.6 s per worker
PF.draw_tile(cv, t)                   # in draw(t): after PLAN.draw + the Ctrl+Z chip, BEFORE the captions; in place;
                                      #   draws nothing outside f448-f511 and f836-f895; outside W_core (never in D9)
PF.avoid_rect(t)                      # (70, 952, 430, 1284) while the tile shows, else None -> snake_captions avoid
PF.tile_rect(t) / PF.face_rect(t) / PF.eye_screen(t)    # drawn tile + tab box, face box, eye midpoint (or None)
PF.jd_alpha(t) / PF.tile_alpha(t)     # (1920, 1080) masks of JD / of the feed (QA, colorist's skin check)
PF.draw_tile(cv, t, mode='plate')     # QA: the room without JD; mode='matte': plain cut-out, no look
PF.FACES                              # the shot table below
```
Captions: `avoid=lambda t: [(80, 236, 1000, 1268)] + ([PF.avoid_rect(t)] if PF.avoid_rect(t) else [])`.
`python3 pehle_wala_faces.py check` prints the limits / placement / texture / halo / eye-lock / cost JSON;
`python3 pehle_wala_faces.py boards` writes the 200 % matte boards.

## 2. Shot table (`PF.FACES`)

| shot | frames (s) | pose | look | in / settled / out | eye midpoint (screen) | rim | note |
|---|---|---|---|---|---|---|---|
| S4-01 | f448-f511 (14.933-17.067) | street_sunglasses | A | POP f448-f453 (opaque from f454, spring settled ~f460), held to f501, exit f502-f511 (gone by 17.050; f512 clean) | (258.9, 1140.4) mean | (0.8, -0.5), gain 1.0 | v16 "Thora cinematic"; JD looks screen-left inside the tile (allowed by the brief) |
| S6-01 | f836-f895 (27.867-29.867) | street_smirk | A | POP f836-f841 (opaque from f842, spring settled ~f848), held to f885 (cover f855), exit f886-f895 (f896 clean) | (260.2, 1140.4) mean | (0.8, -0.5), gain 1.0 | v1 restored, hero smirk |

Keys per entry: `t0, t1, f0, f1, shot, pose, look, tile, scale (0.40), eye_mid_tile (190, 160), rim_dir, rim_gain,
enter ('POP', 6), exit ('in_cubic', 10, 'y+24'), seed, P, width, cam_keys (locked webcam, no push), swap_on_beat
(False), note`. Envelope: opacity `inout_sine` over 6 f from t0, scale 0.92 -> 1 on the POP spring (2.6 Hz, 0.50);
exit `in_cubic` over 9.5 f (ends half a frame before t1, so the next frame's motion-blur samples never catch a ghost:
seen and fixed on the first strips at f512 / f896), y +24, opacity -> 0. `look='D'` (cine) is built and works per shot
but neither showing uses it (BRIEF: A for both).

## 3. What is inside the tile (back to front, built once per pose at display scale)

| layer | build | numbers |
|---|---|---|
| L0 webcam room | NIGHT_1 -> NIGHT_0 wall + `K.radial(480, FLAME x0.35)` at the tile's top-right (the ad side: motivates the rim) + 20 % webcam corner fall-off (multiplicative, never lifts black) | 360 x 300, r 26 |
| wall shadow ("contact shadow" for a bust) | JD's alpha offset (-12, +7) px, blurred sigma 13, x0.30 on the wall: the key is up-right, so it falls down-left | moves with him |
| L1 torso | look A, breathes 0.4 % at 0.29 Hz (scale y about the bust bottom); depth parallax from the Depth-Anything-V2-Small map: a 1.2 px body micro-turn on shoulders / chest / hair edges, head box flattened to its median (rigid) | torso vs head <= 0.048 px/frame |
| L2 head + hair | ONE rigid layer (exact split: head over torso == whole look), rides the breathing neck unscaled | no warp, no depth displacement on the face |
| idle (whole body) | drift +-1.1 / 0.6 px, sway +-0.3 deg about the bust bottom, sines at 0.21 / 0.17 / 0.23 Hz | eye speed <= 0.11 px/frame |
| light wrap | blurred wall (sigma 10) screened over JD's outer 6 px (15 px of the 2x master) at 22 % | |
| look A | `faces.warm_dark(exposure 0.42, warmth (1, .92, .84), contrast 1.12, sat 0.85)` + black-point toe 0.004 + `faces.rim_light(light (0.8, -0.5), gain 2.4, back 0.08, outline 0.02, depth_wrap 0.3, halo 0)` | rim peak 2.34-2.38 linear (<= 3) |
| texture | SR detail pulled back toward the source in the opaque interior: `lanczos2x + 0.3 (sr - lanczos2x)` | §4 |
| card + tab | `ui.glass_card(360, 300, r=26, look='inferno', shadow=0.6)` with the feed inside under its rim (no glass sheen: it lifted his hair to code ~48); tab `glass_card(270, 48, r=16)` + "JD · editor" jw_mono 34 | tile x 70-430, y 980-1280; tab x 82-352, y 952-1000 |

Placement (measured): scale 0.40 of the 2x master (<= 1.0). Sunglasses: face box 110 x 160 px at x 212-326,
y 1089-1250; hair top 1019.6; bust bottom 1380 (hidden). Smirk: face box 127 x 167 px at x 220-351, y 1074-1241; hair
top 1007.5; bust bottom 1367 (hidden). Both cut panel borders (bust bottom, sunglasses' right side) fall outside the
tile. Face box to the tab >= 73.6 px; to the lowest caption ink (avoid bottom 1284 + the solver's 28 px) 61.9 /
71.1 px settled; never at x > 930, never in the bottom 300 px. Eyes locked across the two showings: 1.3 px apart.

## 4. Measurements (stand-in world + real finish; JSON: `<WS>/pehle_wala/qa/faces/{check,measure}.json`)

| check | S4-01 sunglasses | S6-01 smirk | limit |
|---|---|---|---|
| halo, 3 px ring outside the alpha minus the room render, before the finish | +2.39 (15.6 s) / +0.77 (16.0 s) | +0.24 (28.5 s) | <= +6 |
| same, after `G.tx_finish` (includes the finish's bloom of his rim) | +5.65 / +4.13 | +4.27 | <= +6 |
| matte alone (no look) vs room, before the finish | +0.23 | +0.36 | edge contamination only |
| blacks with the bloom off: JD p2 / wall p2 / frame p2 (code values) | 0.0 / 0.43 / 0.0-0.21 | 0.0 / 0.43 / 0.43 | within 2 |
| blacks after the full finish: JD p2 / wall at the same pixels / frame p2 | 3.6 / 2.1-2.3 / 1.1 | 2.8 / 1.5 / 0.9 | within 2 (see §6.1) |
| key: JD p99 / p99.9 vs the ad's p99 | 149-150 / 177-179 vs 253 | 150 / 187 vs 253 | never brighter than the key |
| skin (OKLab, lit cheek / forehead): source -> final | L 0.71 -> 0.52, C 0.074 -> 0.069, hue 45 -> 43 | L 0.73-0.79 -> 0.54-0.60, C 0.071-0.074 -> 0.070-0.071, hue +-1 | natural, darker, never lightened or orange |
| skin (HSV hue, deg): source -> final | 14-18 -> 10-18 | 14-18 -> 14-18 | |
| cheek / forehead texture at display scale vs Lanczos 2x of the native crop (SR raw -> used) | L 1.97 -> 1.21, R 1.87 -> 1.19, forehead 0.95 -> 0.88 | L 2.12 -> 1.21, R 0.77 -> 0.87, forehead 0.95 -> 0.88 | within 1.5x both ways |
| torso vs rigid head parallax | <= 0.048 px/frame (1.2 px max) | same | <= 4 px; head-to-plate <= 32 px/s |
| idle | drift 1.1 px, sway 0.3 deg, breathing 0.4 % at 0.29 Hz | same | yaw / pitch 0 (locked webcam) |
| on screen | 2.133 s | 2.000 s | <= 3.5 s |
| cost of `draw_tile` | 39 ms per call (x3 samples) | 45 ms | |

## 5. Stills and strips looked at (all in `/home/user/100/workspace/jawad_reels/pehle_wala/qa/faces/`)

- Every face beat at its scheduled frame (`render/stills/pehle_wala_faces_proof_<t>.jpg`): 14.93 (f448, tile in, opacity
  0), 15.00 (f450), 15.13 (f454, settled), 16.00 (f480), 16.73 (f502, exit start), 17.03 (f511), 27.87 (f836), 28.20
  (f846), 28.50 (f855, cover), 29.53 (f886), 29.83 (f895). Tile crops side by side: `stills_tiles.jpg`; 2.4x of f480 /
  f855: `tiles_f480_f855_x2.4.jpg`.
- Every frame within +-0.4 s of each entry / exit (range renders, `render/*.mp4`, strips): `strip_14.53-15.37.jpg`
  (f435-f461), `strip_16.33-17.47.jpg` (f489-f524), `strip_27.47-28.30.jpg` (f824-f848), `strip_29.13-30.27.jpg`
  (f873-f908). Before the fix, f512 and f896 showed a faint ghost of the tab (motion-blur samples); now clean.
- Matte at 200 % over black / FLAME / white: `matte200_street_{sunglasses,smirk}.png` (+ `_view.jpg`): no fringe,
  no missing chain, ear or sunglasses arm.
- Skin crops for the colorist (3x, nearest): `skin_street_sunglasses_t15.60_x3.png`, `..._t16.00_x3.png`,
  `skin_street_smirk_t28.50_x3.png`. Masks: `PF.jd_alpha(t)`.
- The stand-in world is `pipeline/jawad_reels/pehle_wala_faces_proof.py` (BRIEF §5 layout, real player window, real
  chai glass frame 0006, pins, chips, payoff lockup, snake captions from the measured `pehle_wala_vo_A.words.json`,
  `G.tx_finish` with the L3 / D9 pushes). Re-run: `tools/heavy.sh python3 render.py pehle_wala_faces_proof --stills ...`
  and `tools/heavy.sh python3 pehle_wala_faces_proof.py measure 15.6 16.0 28.5`. Once `pehle_wala.py` exists, re-shoot
  with `render.py pehle_wala --stills 14.9333,15.1333,16.0,16.7333,17.0333,27.8667,28.2,28.5,29.5333,29.8333`.

## 6. Limits pushed, and why

1. **Blacks after the finish.** Before the bloom JD's p2 equals the wall's (0.0 vs 0.43 code values). The inferno
   bloom (threshold 0.38, radii 8-170 px) of his own skin and rim, the ad's glass and the v16 flares then veils his
   hair and beard: p2 3.6 (v16) / 2.8 (cover) vs the wall at the same pixels 2.1-2.3 / 1.5 (within 2) but vs the whole
   frame's p2 1.1 / 0.9 (2.5 / 1.9). A black-point toe (0.004 linear) already removes what the finish would crush
   anyway; more would crush visible beard and hair detail. Colorist: your call if you want a local black on the tile.
2. **POP scale 0.92 -> 1 in 6 frames** (BRIEF) is a UI card entrance of the whole tile, not a camera push: the face
   never changes size inside its feed.
3. **Exit y +24.** While the tile is still >= 50 % opaque the sunglasses face box comes within 50 px of the lowest
   caption ink (3-4 frames); settled it is 61.9 px.
4. **Fades.** The BRIEF's 6 f opacity ramp starts at 0 on f448/f836, so the tile is first visible on f449/f837; during
   the 4 entry and ~5 exit frames the v16 flare reads through the half-transparent face. A 3 f opacity ramp would halve
   that; not changed (brief value).

## 7. For the timeline builder / QA

- Draw order: `PF.draw_tile` after the world (incl. pins and their collapses) and the Ctrl+Z chip, before captions.
  The Mummy thread card 4 (x 180-553, y 870-954) collapses on f446-f452 under the tab (y 952-1000): the tab draws on
  top; check that frame range in the real reel.
- `samples(t)`: the default 3 is enough (eye motion <= 0.11 px/frame once settled).
- No face shot is inside `W_core`, so the D9 rewind never flashes a face.

## 8. Open questions

- AI disclosure: the character sheets look AI-generated and the VO is synthetic; default Meta AI label ON (SLATE §7.1).
- "JD · editor" nameplate in a labelled POV skit (SLATE §7.4, defaulted yes).
- The face-compositor's shared helper `faces25d.py` was not created: four other reels build faces in parallel and a
  shared file would collide; everything this reel needs is in `pehle_wala_faces.py` (it imports the charsheet
  `faces.py` by path, read-only).
- Assets and licences (built earlier, `research/face_assets.md`; nothing new downloaded here): Real-ESRGAN x4plus ONNX
  (BSD-3), BiRefNet-portrait (MIT), Depth-Anything-V2-Small (Apache-2.0), YuNet (MIT).
