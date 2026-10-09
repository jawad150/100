# FACES · Reel 4 · C02 "Beta, tum karte kya ho?" (face-compositor)

Date 2026-10-09 · Status: **ready for the motion-timeline-builder** · Look `gold_hour` (registered in `jawad_grade`, no
stand-in needed) · rim look A (hero: S0/S12 confused, S10 hand-on-chest) and cine look D (narration: S3 shocked, S6
neutral), as BRIEF 6.10 assigns.

| file | what |
|---|---|
| `pipeline/jawad_reels/beta_tum_karte_kya_ho_faces.py` | the module the reel imports (API below; `check` / `export` / `boards` CLI) |
| `pipeline/jawad_reels/beta_tum_karte_kya_ho_faces_preview.py` | render.py harness for QA only (gold_hour plate + JD + embers + labelled stand-ins of the bubbles). Not the reel. |
| `workspace/jawad_reels/beta_tum_karte_kya_ho/out/faces_preview/` | `stills/` (19 beat stills, png + jpg), `sheets/` (5 contact sheets), `strips/` (7 every-frame strips around each cut), 7 range clips `*_a-b.mp4`, `boards/` (200 % edge boards), `check.json` (all numbers) |
| `workspace/jawad_reels/beta_tum_karte_kya_ho/faces/<pose>/` | exported assets: `rgba.png` (16-bit straight sRGB, texture-corrected), `layers/head.png` + `layers/torso.png` (look A), `depth.png` (16-bit), `rim_mask.png`, `meta.json` (source crop, hand-marked eyes, face / head box, head pivot, layer z, focal, offsets) |

No `plate.png`: the sheets' grey sweep is never used, the gold_hour world replaces it.

## 1. Poses (only the four SLATE §3.4 assigns; one wardrobe, never mirrored)

| pose | native → 2x master | face h (native) | used as | max display scale | texture k (cheek ratio vs 2x Lanczos) | defects / notes |
|---|---|---|---|---|---|---|
| `suit_confused` | 382x561 → 764x1122 | 228 px | S0 hook + cover, S12 loop | 0.958 | 0.27 (1.44; raw SR 8.80) | panel-cut left/right/bottom (hidden: sill shadow + 5 % side fade, bottom off-frame); mouth open (never animated) |
| `suit_shocked` | 406x561 → 812x1122 | 221 px | S3 punch-in | 0.953 | 0.23 (1.44; raw 11.36) | cut sides |
| `suit_neutral` | 406x556 → 812x1112 | 220 px | S6 | 0.979 | 0.29 (1.43; raw 7.64) | cut sides; the fringe specks of face_assets.md are invisible on this plate (edge board) |
| `suit_hand_on_chest` | 355x561 → 710x1122 | 195 px | S10 payoff anchor | 0.987 | 0.26 (1.44; raw 8.76) | fingers, nails and watch complete (edge board); pocket square sits on the right cut, in the dark sill zone |

Sources (no new model run here): Real-ESRGAN x4plus ONNX 2x masters (BSD-3), BiRefNet-portrait matte (MIT) +
pymatting decontamination, Depth-Anything-V2-Small depth (Apache-2.0), YuNet landmarks (MIT). No non-commercial weights.
All faces are 195-228 px tall natively, so every shot is a medium-close bust at <= 0.987 of the 2x master, never a
full-frame close-up.

**Human-realism / photo-realism (texture).** x4plus put 7.6-11.4x the cheek Laplacian variance of the 2x Lanczos source
into these small suit faces (crisp edges on waxy skin). Fix: a skin-only pull-back `rgb = lanczos2x + k (sr - lanczos2x)`
on face / ear / neck skin (HSV skin mask inside the face box, opaque interior only); eyes, lashes, brows, beard, hair,
lips' edges, shirt and suit keep the full SR detail. k is the largest value (bisection) giving <= 1.45x. At 100 % the
skin now shows the source's own pores and mottling, the eyes stay sharp, no seams (`stills/*_001.00.png`,
`boards/edges_*.jpg`). Grain comes only from the finish. Skin is never lightened: final OKLab L 51-54 vs 69-72 in the
studio photo (low-key backlit room), hue 35.5-39.2° vs 32.7-35.1° (+3-4° warmer), chroma 7.3-7.7 vs 6.3 (not orange).

**Eye anchor (hand-marked).** YuNet's `meta['eye_mid']` sits 10-15 px right / 8-15 px above the eyes and its bias
differs between poses by up to 7 px. The module locks the midpoint of the four eye corners (canthi), marked by hand on
4x crops (`EYE_CORNERS` in the module, `eye_corners_hand` / `eye_mid_hand` in the exported meta.json). Verified
independently on rendered frames by template matching (gradient NCC 0.81-0.94): every shot's eyes land 1.25-1.93 px from
(540, 1280), within 0.15 px of the model. Consequence: face / head rects differ from the brief's proof numbers by up to
~15 px (new rects in §3; always take them from the module's functions).

## 2. API (`import jawad_kit` first; then `import beta_tum_karte_kya_ho_faces as FF`)

```python
FF.prewarm()                                   # once per worker: builds the 4 looks (~8 s), fills FACES P/width/cam_keys
key = FF.shot_at(t)                            # 'S0'|'S3'|'S6'|'S10'|'S12'|None, frame-exact (jawad_tx fidx / side_b rule)
cv = K.background(LOOK, t, FF.world_cam(t), bokeh=0.6, intensity=FF.window_gain(t))   # plate moves with the dolly
#   S10 only: draw the sun disc (540, 1260) here, BEFORE JD (he hides it; it is his backlight)
FF.draw_face(cv, key, t)                       # sill shadow + torso + rigid head + rim + phone uplight + light wrap
#   then: J.embers in front with FF.world_cam(t), bubbles / lockups, captions (AVOID uses FF.head_rect)
FF.head_rect(key, t)     # (x0, top, x1, 1920) caption avoid rect, +6 px margin      e.g. S10 @30.0 -> (305, 1021, 721, 1920)
FF.face_rect(key, t)     # screen face box                                          e.g. S10 @30.0 -> (372, 1130, 653, 1505)
FF.eye_point(key, t)     # screen eye midpoint incl. idle (QA)                      -> ~(540, 1280) +- 2.5 px
FF.bust_bottom(key, t)   # >= 1950 everywhere (panel cut never seen)
FF.scale(key, t)         # head-plane display scale (BRIEF 6.10 formula, out_quad punch-in)
FF.cam(key, t)           # the 85 mm JD camera (K.Cam, focal 4516 px, aperture 24, focus on the head)
FF.window_gain(t)        # window light: S6 1.0 -> 0.85 (15.4-16.8 s, inout_sine); S10 1.0 -> 1.35 (30.8-31.3 s, out_cubic)
FF.jd_alpha(key, t)      # (1920, 1080) float32 screen alpha of JD (QA: "no face pixel under UI")
FF.look(pose, kind, phone, rim_dir, rim_back)   # the built read-only layer dict
FF.FACES                 # shot table (§3)
```
CLI (run through `tools/heavy.sh`): `python3 beta_tum_karte_kya_ho_faces.py check` (writes `check.json`), `export`,
`boards`. Stills: `tools/heavy.sh python3 render.py beta_tum_karte_kya_ho_faces_preview --stills ... --workers 1 --jpg`.

**Builder notes.** (1) Do NOT add the brief's `K.radial(900, AMBER x 0.08)` phone glow: it lives inside `draw_face`
as an albedo-modulated uplight (warms shirt, collar and jaw underside; the black suit stays black). (2) `draw_face`
darkens the canvas below y ~1540 (the wall under the window sill, NIGHT_0 86 %) BEFORE drawing JD, so draw everything
that sits behind JD first and all UI after. (3) Use `window_gain(t)` for the world's intensity in S6/S10 so his rim and
the room dim / swell together (BRIEF says -15 % from 15.4 s and +35 % at 30.8 s; eases above are mine). (4) No
cross-dissolve, no blur across the cuts: `shot_at` switches on the frame. (5) Cost: 170-210 ms per `draw_face` call on
the shared box (1 sample); x3 samples on 315 face frames is ~3 min of a full render.

## 3. Shot table (`FF.FACES`; frames half-open, P = screen eye midpoint)

| key | frames (t) | pose | look | P | width @t_push0 | scale first → last | punch-in | light | face rect first → last | head_rect first |
|---|---|---|---|---|---|---|---|---|---|---|
| S0 | f0-f83 (0-2.8) | suit_confused | A, rim (0.8, -0.5), phone | (540, 1280) | 703 px | 0.9277 → 0.9583 (dolly from t = -0.7, continuous with S12) | — | window 1.0 | (386,1115)-(704,1539) → (381,1108)-(710,1546) | (310, 992, 780, 1920) |
| S3 | f231-f251 (7.7-8.4) | suit_shocked | D, phone | (540, 1280) | 747 | 0.9200 → 0.9533 | 7.7 (c3), 1.00 → 1.03 over 0.9 s | 1.0 | (384,1118)-(693,1524) → (378,1111)-(699,1532) | (311, 994, 767, 1920) |
| S6 | f420-f503 (14.0-16.8) | suit_neutral | D, phone | (540, 1280) | 747 | 0.9200 → 0.9791 | 14.0 (c6) | 1.0 → 0.85 from 15.4 | (386,1116)-(692,1520) → (376,1106)-(702,1536) | (313, 977, 766, 1920) |
| S10 | f861-f965 (28.7-32.2) | suit_hand_on_chest | A, rim (0.55, -0.85), counter-rim 0.85 (both sides), no phone | (540, 1280) | 653 | 0.9200 → 0.9870 | 28.7 (c10) | 1.0 → 1.35 at 30.8-31.3 | (380,1133)-(648,1492) → (366,1122)-(655,1508) | (315, 1030, 713, 1920) |
| S12 | f1071-f1091 (35.7-36.4) | suit_confused | A, phone | (540, 1280) | 703 | 0.9200 → 0.9274 (= S0 at t - 36.4) | — (hard cut c12, no push) | 1.0 | (387,1115)-(703,1535) | (312, 992, 779, 1920) |

Pose time: confused 0.7 + 2.8 = 3.5 s across the loop, shocked 0.7, neutral 2.8, hand-on-chest 3.5 (all <= 3.5).
No face-to-face cut exists in this reel (every face shot is entered from a card, the sun or the end-card world), so
"eye lock" = every JD shot lands his eyes on the same point (540, 1280); measured 1.25-1.93 px.

## 4. How the 2.5D and the light are built (never-uncanny)

- **Planes, real camera.** Each pose = a rigid HEAD plane (hair, ears, face, beard, head box feathered, exact
  recombination with the torso) at z 0 and a TORSO plane 100 units (~4 cm) behind it, drawn with `K.draw_plane` through
  an 85 mm `K.Cam` (focal 4516 px, aperture 24, focus on the head). The camera dollies along the ray through the eyes
  (BRIEF scale curve), so the eyes stay locked while the planes and the plate scale at their own rates. `world_cam(t)`
  gives the builder a default-focal cam that moves the gold_hour plate like a wall 2.5 m behind him (S10: plate +3.1 %
  and 9.9 px up while JD grows +7.3 % about his locked eyes; the plate is unmoved on each shot's registration frame, so
  c12 into S12 keeps the end-card world continuous).
- **Depth maps.** Drive the rim's normal wrap (cheek / jaw / ear relief) and a torso-only micro-parallax for the dolly
  (lapels and shoulders vs chest; <= 3.0 px in S10, 0 at the head seam). The head is never warped. (The monocular maps
  read the chest NEARER than the face, the usual "lower = nearer" bias, so plane z is anatomical, not from the map.)
- **Idle.** Subject sway <= 0.25° about the bust bottom (roll measured <= 0.10°), drift 1.5 px, breathing 0.4 % at
  0.29 Hz on the torso layer only (the head rides on it, never scaled). FA.idle was not used: it scales the whole
  sprite, i.e. stretches the face 0.4 %.
- **Rim.** `FA.rim_light` emission (FLAME + AMBER core, RED counter-rim, normal wrap), light from the window behind /
  camera-right; outline 0.04 and halo 0.16 (A) / 0.10 (D) instead of the library's 0.15 / 0.55, whose all-round glow
  read as a sticker outline. The rim follows `window_gain`.
- **Light wrap.** The plate behind him blurred sigma 30 px, screened over his outer 14 px at 22 %.
- **Sill shadow.** The panel crops cut his shoulders flat exactly where the horizon band is brightest (a dark
  column against gold = pasted). The plate now ends at a soft sill line (y 1540 → 1770, NIGHT_0 86 %) and the cut sides
  fade 5 % into it. The sun core and band stay visible behind his neck. (This replaces the full-body contact shadow: no
  feet are on screen in this reel.)
- **Match the scene.** Torso fill falls to x0.62 below the chin and a soft highlight shoulder keeps the white shirt
  under the window glow: JD p99 133 vs the plate's key 136-145 (S10 sun 235). Look D exposure 0.52 (library 0.80 read +30
  code values brighter than A) + a NIGHT_1 veil of 0.35 so its blacks meet the room's.

## 5. Measurements (`check.json`, final code)

| shot | eye vs (540,1280): model max / measured | push max | parallax px/frame head / torso / plate | head-to-plate %W/s | torso micro max | halo ring (plain) mean / p95 | JD p2 vs scene p2 | JD p99 vs plate key | face mean | ms / draw_face |
|---|---|---|---|---|---|---|---|---|---|---|
| S0 | 1.87 / 1.31 px | 1.19 %/s | 0.21 / 0.27 / 0.05 | 0.46 | 1.39 px | +3.65 / +23.5 | 3.0 / 3.3 | 133.2 / 135.7 | 74.2 | 192 |
| S3 | 1.88 / 1.41 | 7.86 | 0.82 / 1.14 / 0.31 | 1.39 | 1.26 | +3.90 / +23.3 | 2.4 / 2.3 | 133.4 / 144.5 | 71.3 | 203 |
| S6 | 1.61 / 1.37 | 7.86 | 0.77 / 1.19 / 0.33 | 1.20 | 2.37 | +3.45 / +20.2 | 2.4 / 2.6 | 133.5 / 138.9 | 74.3 | 208 |
| S10 | 2.51 / 1.93 | 7.86 | 0.66 / 1.17 / 0.27 | 1.08 | 3.03 | +2.84 / +20.0 | 3.1 / 2.8 | 133.4 / 234.9 | 77.1 | 178 |
| S12 | 1.74 / 1.25 | 1.20 | 0.21 / 0.27 / 0.05 | 0.45 | 0.26 | +3.56 / +22.8 | 2.8 / 2.6 | 133.4 / 139.3 | 74.4 | 172 |

Limits: eye <= 6 px, push <= 8 %/s, head-to-plate <= 3 %W/s, micro <= 4 px, halo <= +6, |p2 delta| <= 2, JD <= key: all
pass. Halo p95 is the anti-aliased edge of skin / ears (subject colour), not fringe; the look's deliberate rim glow
reads +19.7..+30.9 in the same ring. Luma is full-range 8-bit Rec.709 after `G.tx_finish(rays=0)`; face mean 71-77 =
78-82 in limited range (BRIEF QA >= 70); frame 0 YAVG 55.0 limited with the stand-ins (>= 40). Display scale <= 0.987.
Bust bottom >= 1950 (>= 1926). Faces x <= 710 (like column x > 930 clear), bottom <= 1546 (bottom 300 px clear); text
>= 332 px from every face. Guards: alpha <= 1 and no negative light in every shot. Loop seam f1091 → f0: mean |delta|
0.070 = a normal frame step (0.070); scale 0.92736 → 0.92773, eyes (539.90, 1279.68) → (539.88, 1279.78).

## 6. Stills and strips looked at (all under `out/faces_preview/`)

Stills at f0, f30 (cover), f42, f83 · f231, f241, f251 · f420, f449, f462, f503 · f861, f900 (anchor), f924, f940,
f965 · f1071, f1081, f1091 (`stills/*_<t>.png`, sheets in `sheets/`). Every frame +-0.4 s around c3/c4, c6, c7, c10,
c11, c12 and across the loop: `strips/strip_*.jpg` from the range clips. Seen: JD appears exactly on the cut frame
(f231, f420, f861, f1071) and is gone on the exit frame (f252, f504, f966); the punch-in is a smooth 3 % push; the loop
is continuous; rim brightest camera-right, both sides in S10; S6 dims, S10 swells without any colour shift on the face;
no halo, no grey fringe, no missing hair / fingers / watch (edge boards over black, FLAME, white at 200 %).
Bug found and fixed on the way: the window gain first scaled the premultiplied ALPHA too (S10 swell made JD's alpha
1.1 → a purple, subtracted face at 31.3 s; S6 dimming made him 15 % see-through). Light now scales RGB only; a guard
in `check` fails if alpha > 1 or light goes negative.

## 7. Deviations from BRIEF 6.10 (and why)

1. Eye anchor = hand-marked canthi midpoint, not `meta['eye_mid']` (YuNet bias, see §1). Face / head rects move by up
   to ~15 px; use the module's functions, not the brief's numbers.
2. Punch-in ease `out_quad` (FA.swap_push's `out_cubic` peaks at 11.2 %/s with the dolly, over the 8 %/s limit).
3. Breathing on the torso only + rigid head; sway about the bust bottom (not FA.idle about the eyes).
4. Phone glow is light on albedo inside `draw_face` (not an additive radial over JD).
5. New sill shadow, torso falloff + highlight shoulder, look D exposure / veil (scene match, §4).
6. Rim outline / halo reduced (sticker read); skin-only SR pull-back (texture rule).

Limits used at their edge: confused and hand-on-chest each hold exactly 3.5 s; punch-ins peak at 7.86 %/s.

## 8. Open questions for the lead

1. AI-imagery disclosure: the character sheets look AI-generated (face_assets.md); with the synthetic voice the
   brief's default is "AI info" ON. Confirm.
2. `suit_hand_on_chest` looks up-right while the payoff bubble sits top-centre: it reads as looking past it into the
   light. No up-left suit pose exists and mirroring is banned; acceptable, or re-block the bubble slightly right?
3. The sill shadow darkens the plate's bottom ~380 px during face shots only; the colorist may want the same sill in
   S9 / S11 for continuity (builder / colorist call).
