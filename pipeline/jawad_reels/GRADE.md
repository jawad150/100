# GRADE.md - colour for @jawad_mp4 reels (colorist)

Owner: colorist. Files: `jawad_grade.py` (finish, looks, LUT writer, chart, QA), `luts/*.cube`, this page.
Measured 2026-10-08 on the shared 4-core box (`nice -n 10`, 2 OpenCV threads). Every number below comes from
`python3 jawad_grade.py ...` runs; outputs live in `workspace/jawad_reels/looks/`.

## 1. Adopt it (builders)
```python
import jawad_kit                       # first, as always
import jawad_grade as G                # registers 'inferno', 'gold_hour', 'dusk' (idempotent)
LOOK = 'dusk'                          # 'ember' | 'noir_ember' | 'inferno' | 'gold_hour' | 'dusk'
def post(cv, t): return G.finish(cv, LOOK, t)                                    # plain reels
def post(cv, t): return G.tx_finish(cv, t, LOOK, cuts=CUTS, **plan.post_kw(t))   # reels on jawad_tx (X.finish args)
```
* `G.tx_finish` takes exactly `jawad_tx.finish`'s arguments (cuts, push, bloomout, rgb_split, bloom_scale, any
  K.post key): jawad_tx computes its exposure push / L4 bloom-out / D7 split, then `G.finish` grades the frame.
  Self-test proves it equals `G.finish(..., exposure=1.4*push, bloom=bloom*(1+0.9*push))` bit for bit.
* Overrides: any K.post key (`exposure=`, `bloom=`, `footage=1` for bright full-bleed footage, `vignette=`),
  `grain=` / `grain_size=`, `skin=0..1`, `rays=` / `rays_center=(x, y)` (gold_hour god rays, default at the sun
  core 0.52 W, 0.78 H; move it with the sun if the camera pans hard).
* Never `K.flash` / `post(flash=)`: exposure pushes only (blacks stay down).
* Draw everything UNGRADED (backgrounds, type, UI, Blender props, Jawad's cut-outs, footage with `look=None` or
  `look=LOOK`): the finish grades each frame once. Do not pre-grade anything with a LUT that will pass through
  `G.finish` (that grades it twice).

## 2. The finish (`G.finish(cv, look, t, **ov)`, in place, linear premultiplied float32)
1. **K.post in two halves.** The toolkit's spatial post (exposure, bloom + halation, vignette, edge chroma; grain
   off), then the kit's per-pixel `mono` + `crush` in jawad_kit's order. The kit's `crush` (c^2/(c+k), never
   lifts) IS the toe for every look; my curve's toe stays neutral. Skin's reference value is taken between the halves.
2. **Characteristic curve**, per channel, in log2 stops around 0.18: `y = s + (g-1)*s*exp(-s^2/2w^2)` (slope g at
   0, back to ~1 in the deep toe and around +2.5 stops), then a soft shoulder `2.5 + D(1-exp(-(y-2.5)/D))`. Applied
   as ONE gain LUT (65536 entries) indexed by the top 16 bits of each float32 (1/128-octave steps, gain steps
   <= 0.16 %); deep blacks get a constant gain, so 0 stays 0.
3. **Split tone by luminance** (8-bit sqrt(L) index into cv2.LUT tables): shadow gain `n_sh^(a*w_sh)`, highlight
   gain `n_hi^(a*w_hi)` (n = colour / its luminance), renormalised to unit luminance, multiplicative (black stays
   black); weights: shadows below -4.5..-1 stops, highlights above +0.5..+2.5 stops, mids neutral.
4. **Blackbody roll-off**: saturated pixels (HSV S > 0.35..0.75) with pre-curve luminance above l0 move toward the
   look's hot colour (l0..l1) and then toward warm white (w0..w1), luminance kept. Before: FLAME x12 displayed as
   lemon (255,255,99), RED x9 as pink (255,143,128); after (ember): warm white (255,255,243) and peach-orange
   (255,181,116); inferno keeps its cores orange-yellow (FLAME x12 -> 255,253,130).
5. **Saturation by luminance** k(L): deep shadows `sat[0]`, mids `sat[1]` (<= +8 %), highlights `sat[2]`.
   **Skin protection**: skin-like pixels (section 5) keep 70 % of their ungraded value (after the spatial half
   of K.post) and half of the rest of their chromaticity, so mono, crush and steps 2-4 reach skin at ~15-30 %.
6. **Grain** `K.grain(cv, t, amount, size)` after the curve, sizes 1.6-1.8 px (section 8).

Cost on top of K.post (two self-test runs, 1080x1920 test frame, shared box): ember +116..207 ms, noir_ember
+138..158, inferno +114..143, dusk +133..137, gold_hour +182..208 (incl. ~40 ms god rays). Over the ~60 ms
target: the 2 M-pixel gain gather (~25 ms), the split / saturation apply (~20 ms) and the skin map + blend
(~30 ms when a face is on screen) dominate. A test frame renders at 0.52-0.59 s/frame including the finish
(1 sample).

## 3. The five looks (one per reel; all orange-red on deep black)
| key | owner | world (generic mood; slate 6.3 use) | blacks / toe (crush kR,kG,kB) | curve slope / width | accents |
|---|---|---|---|---|---|
| `ember` | kit | void with flame key + ember haze (floating glass, C08) | crushed warm (0.010, 0.015, 0.020) | 1.16 / 1.6 | FLAME lead, gold-white cores |
| `noir_ember` | kit | near-monochrome warm black, one practical (floodlit stadium, C15) | deeper (0.018, 0.024, 0.030), mono 0.85, shadow sat 0.60 | 1.26 / 1.5 | red-orange the only colour |
| `inferno` | colorist | hot chaos: red-black, fire floor from below, red / ember hazes (C24 right) | deep red-black (0.014, 0.018, 0.026) | 1.30 / 1.7 | RED / EMBER lead, highlights roll to orange |
| `gold_hour` | colorist | dusk-to-sunrise: brown-black floor, gold horizon band, amber sun core, god rays (C10) | brown-black, light toe (0.004, 0.007, 0.012) | 1.10 / 1.8 | GOLD / AMBER with FLAME edges |
| `dusk` | colorist | night interior: indigo-violet base, candle pool + amber core, torch beam, warm floor (C11) | indigo-violet toe (0.010, 0.014, 0.005: green crushed most, blue least) | 1.20 / 1.6 | red-orange practicals, violet only in the dark |

### 3.1 Finish table (`G.FIN`)
| look | shoulder (start, depth) | shadow split | highlight split | sat (deep, mid, high) | blackbody hot / white (linear), k, l0-l1 / w0-w1 | grain amount / size |
|---|---|---|---|---|---|---|
| ember | 2.5, 1.5 | EMBER 0.05 | GOLD 0.04 | 0.82, 1.06, 1.0 | (1, .45, .12) / (1, .88, .70), .75 / .85, 0.8-2.5 / 1.6-5.0 | 0.016 / 1.8 |
| noir_ember | 2.5, 1.5 | SMOKE 0.04 | AMBER 0.03 | 0.60, 0.92, 1.0 | (1, .50, .18) / (1, .90, .78), .70 / .85, 0.8-2.5 / 1.6-5.0 | 0.022 / 1.7 |
| inferno | 2.5, 1.3 | EMBER 0.08 | FLAME 0.04 | 0.86, 1.05, 1.0 | (1, .30, .06) / (1, .75, .50), .80 / .40, 0.8-3.0 / 3.0-8.0 | 0.020 / 1.7 |
| gold_hour | 2.5, 1.7 | #2B1407 0.10 | GOLD 0.07 | 0.86, 1.05, 1.0 | (1, .55, .20) / (1, .92, .78), .75 / .90, 0.7-2.2 / 1.4-4.0 | 0.018 / 1.6 |
| dusk | 2.5, 1.5 | #171431 0.20 | FLAME 0.04 | 0.80, 1.06, 1.0 | (1, .45, .12) / (1, .88, .72), .75 / .80, 0.8-2.5 / 1.8-5.5 | 0.020 / 1.7 |
All looks: skin 0.70, skin_chroma 0.5. gold_hour: rays 0.26 at (0.52, 0.78), threshold 0.30, length 0.42.

### 3.2 Keys added through `J.register_look(name, base='ember', ...)` (nothing existing is edited)
K.LOOKS (post; merged over 'ember'):
| look | bloom / threshold / tint | halation | vignette | chroma | grain | crush | mono |
|---|---|---|---|---|---|---|---|
| inferno | 0.70 / 0.38 / (1, .30, .12) | 0.20 | 0.58 | 1.4 | 0.020 | (0.014, 0.018, 0.026) | 0 |
| gold_hour | 0.66 / 0.42 / (1, .62, .28) | 0.14 | 0.42 | 1.0 | 0.018 | (0.004, 0.007, 0.012) | 0 |
| dusk | 0.60 / 0.42 / (1, .45, .20) | 0.16 | 0.55 | 1.2 | 0.020 | (0.010, 0.014, 0.005) | 0 |

Backdrops (`K._BG_LOOKS`, blob = cx, cy, rx, ry, angle, colour, intensity, drift x, drift y, period, aurora;
rim None, dots 0):
* inferno: top NIGHT_0, bottom NIGHT_1, lift 0.20, base_tint (1.55, 0.78, 0.70), noise 0.80; blobs EMBER fire
  floor (0.50, 1.04, 0.95, 0.26, 0, 0.46), FLAME tips (0.52, 0.95, 0.40, 0.09, 0, 0.10), RED haze (0.16, 0.30,
  0.46, 0.26, 22, 0.15), EMBER haze (0.88, 0.58, 0.42, 0.30, -30, 0.30), RED light (0.72, 0.10, 0.30, 0.14, -20,
  0.07). Bokeh (34, RED/FLAME/EMBER, 6-52 px, 0.30).
* gold_hour: lift 0.45, base_tint (2.85, 1.95, 0.92), noise 0.45; GOLD horizon (0.50, 0.80, 0.90, 0.20, 0, 0.24),
  AMBER sun core (0.52, 0.78, 0.24, 0.09, 0, 0.20), FLAME edges (0.08, 0.68, ...0.11) and (0.94, 0.62, ...0.09),
  GOLD sky lift (0.50, -0.06, 0.90, 0.22, 0, 0.05), EMBER ground (0.50, 1.06, 0.90, 0.12, 0, 0.10). Bokeh (26,
  GOLD/AMBER/FLAME, 8-60, 0.22).
* dusk: lift 0.55, base_tint (1.05, 1.45, 7.0) (indigo-violet from the NIGHT gradient), noise 0.40; FLAME candle
  pool (0.78, 0.70, 0.30, 0.20, -15, 0.20, period 7 s), AMBER core (0.80, 0.69, 0.08, 0.06, 0, 0.14, 3.1 s),
  FLAME torch beam (0.30, 0.30, 0.70, 0.07, -38, 0.05), EMBER floor (0.10, 0.95, 0.50, 0.25, 20, 0.10).
  Bokeh (14, FLAME/AMBER/RED, 8-56, 0.18).
Exact tuples: `jawad_grade._new_look_defs()`.

Glass UI (`ui.LOOKS`, cloned from 'ember'):
* inferno: tint NIGHT_1 + 20 % EMBER -> NIGHT_0, tint_a 0.72; accent RED, accent_hi FLAME, grad RED -> EMBER
  (IVORY on EMBER 6.4:1), grad_hi FLAME -> RED, rim FLAME, rim2 RED, glow RED, ok FLAME.
* gold_hour: tint #2B1407 + 50 % SMOKE -> #1D1007, tint_a 0.68; accent GOLD, accent_hi AMBER, grad FLAME -> RED
  (kept: white button text never sits on gold), grad_hi AMBER -> FLAME, rim AMBER, rim2 FLAME, glow GOLD.
* dusk: tint #171431 + 35 % NIGHT_0 -> #0C0208, tint_a 0.72; accent FLAME, grad FLAME -> RED, rim HOT_PINK
  (#FF8A3D hot orange), rim2 RED, glow FLAME, ok GOLD, text2 ivory with a cool lilac touch.

Footage / still grades (`F.GRADES`, display-referred, black 0 = never lifted). Kept gentle because the finish
does the look; skin numbers from `G.footage_skin_check`:
| look | wb | exp | contrast / pivot | shadow tint | highlight tint | sat | skin dhue / chroma ratio |
|---|---|---|---|---|---|---|---|
| inferno | (1.03, .99, .95) | -0.06 | 1.10 / 0.40 | (0, -.010, -.016) | (.010, 0, -.010) | 0.96 | <= 2.8 deg / 1.06-1.10 |
| gold_hour | (1.02, 1.0, .96) | 0.0 | 1.00 / 0.42 | (0, -.002, -.012) | (.006, .004, -.008) | 0.97 | <= 2.9 deg / 1.01-1.04 |
| dusk | (1.0, .98, 1.03) | -0.06 | 1.08 / 0.40 | (-.006, -.008, .006) | (.020, .006, -.016) | 0.98 | <= 3.3 deg / 0.99-1.03 (black -> +2 B codes) |
`G.cutout(spr, look)` = F.GRADES[look] + the finish's skin protection for a cut-out (Jawad street_smirk: dhue
<= 1.5 deg, chroma x0.95-1.08); optional, most scenes need no cut-out pre-grade.

## 4. Brand fit and distinctness
* Hue budget (OpenCV HSV, S > 80, V > 60, test clips at 1 fps): red-orange 97.5-100 % of saturated pixels in every
  look; dusk's brightest 5 % of saturated pixels 99.3 % red-orange, violet <= 0.4 % (its violet lives below V 60).
* Same frame at feed-thumbnail size (27x48 px), mean OKLab distance x 100 between looks: ember|inferno 5.2,
  inferno|dusk 5.6, ember|dusk 5.7, ember|noir 6.5, noir|dusk 6.9, noir|inferno 8.3, gold|* 11.2-16.2. The sheet
  (`looks_sheet.jpg`, `looks_thumbs.png`) shows them apart at a glance: orange haze / black / red / gold rays /
  indigo. k-means (5 colours, 2 fps) dominant darks: ember #1C0302, noir #0A0403, inferno #260302, gold_hour
  #330F03, dusk #180514.

## 5. Skin (human-realism + photo-realism applied to Jawad's cut-outs)
Rules taken from Jawad's skills: never smooth or retouch (the finish is colour only, per pixel, no blur on skin);
never lighten skin (no colourism); deep skin keeps shadow-side detail; natural highlight roll-off; no HDR, no
oversaturation; Portra-like warm highlights, gentle contrast; real grain.
* Qualifier (`_skin_weight`, on sqrt-encoded RGB): hue 8-29 deg full (fading to 0 at 0 and 43 deg), HSV S
  0.30-0.60 full (0 below 0.16 / above 0.76: brand orange S~0.9 and warm-white shirts S~0.2 are out), luminance
  linear ~0.045-0.5. Wide smooth ramps so a 33-point LUT follows them. Colour-only qualifier: warm glass UI and
  rim-halo blends catch partial weight. Measured on the test frame (finish with vs without skin protection, dE
  x100): UI card mean 0.27-0.81 (p95 1.6-3.7), title 0.00-0.05, face mean 0.9-2.2 (the intended change).
* Chart skin patches (light #E0B49A, Jawad suit #C49487 and street #B4806F measured from his cut-outs, deep
  #6E4A3A): hue shift <= 2.25 deg (OKLab), lightness change -0.34..+1.47 (x100), chroma x0.91-1.09 (section 6).
* Real cut-out (street_smirk, Haar face box, cheek band): raw L 64.0 C 6.73 h 42.1 (HSV 15.5 deg); after the
  face-compositor's `FA.rim_light` (low-key warm_dark base) L 49.2 C 7.05 h 41.3; in the finished test clips
  L 47.0-48.7, C 7.2-8.6, h 37.4-44.4 (HSV hue 14-17 deg). Hue holds within 5 deg; the extra chroma in inferno
  / gold_hour is the world's light spill from bloom / halation, which skin protection deliberately keeps.
* Vectorscope of the face for the hand-back: `looks/<look>/qa_<look>_test/vs.png` (ffmpeg `vectorscope=mode=color3`
  of `face.png`); the numeric skin hue / chroma per second is in `verify.json`.

## 6. Test charts (`python3 jawad_grade.py chart all`)
1080x1920: grey ramp 0-1.6, hue wheels (V 0.85 / 0.40), palette swatches at 0.5x / 1x / 2x, four skin patches,
dark warm + neutral gradients, emissive patches (FLAME 3/6/12, RED 4/9, GOLD 4/10, IVORY 1.6). `chart_<look>_before
.png` (toolkit display only) / `_after.png` (colour part of the finish) / `.json`.
| look | FLAME 1x dE | RED 1x dE | skin max dhue (deg) | skin dL x100 (max) | skin chroma ratio |
|---|---|---|---|---|---|
| ember | 2.06 | 2.28 | 2.25 | +0.65 | 1.029-1.064 |
| noir_ember | 1.98 | 0.28 | 1.41 | -0.34 | 0.914-0.946 |
| inferno | 2.58 | 2.57 | 1.07 | +1.47 | 1.031-1.093 |
| gold_hour | 1.30 | 1.79 | 0.72 | +0.46 | 1.024-1.054 |
| dusk | 2.08 | 2.16 | 1.94 | +1.09 | 1.018-1.052 |
Gates: FLAME / RED <= 3, skin hue <= 4 deg, skin dL <= +1.5, chroma 0.85-1.12: all pass.

## 7. LUTs (`python3 jawad_grade.py lut all` -> `luts/<look>_33.cube`, `luts/identity_33.cube`)
33^3, red index fastest, TITLE / LUT_3D_SIZE 33 / DOMAIN_MIN 0 0 0 / DOMAIN_MAX 1 1 1, 6 decimals. Chain: sRGB ->
linear -> the per-pixel part of K.post (exposure, mono, crush) -> steps 2-5 incl. skin protection -> toolkit
shoulder (`core._shoulder_curve`, knee 0.82) -> sRGB. No bloom, halation, vignette, edge chroma or grain.
* Orientation: identity cube through `ffmpeg lut3d` reproduces the chart within 1 code (rgb24) and 0.004 code
  (16-bit in / out).
* Look cubes vs the in-process grade on the chart (non-emissive px, ffmpeg lut3d tetrahedral, 16-bit):
  mean dE x100 0.037-0.045, max 1.69 (ember), 2.37 (noir_ember), 1.82 (inferno), 1.96 (gold_hour), 1.77 (dusk).
  ffmpeg's 8-bit lut3d path truncates (mean -0.21..-0.27 code): mean 0.12-0.19, max 1.6-6.7 only at 1-code
  near-black differences (OKLab is steep there). For previews on 8-bit sources this is invisible; for exact
  work run lut3d in 16 bit (`-vf format=rgb48le,lut3d=...`) or in the NLE.
* Use: ffmpeg previews, Jawad's NLE, external clips that will NOT pass through `G.finish`. Never on anything
  that the compositor finishes (no double grade).

## 8. Encode checks (test clips: `python3 jawad_grade.py clip all 3`, then `verify <mp4> <look>`)
3 s of the shared test frame (world + house title + glass UI card + Jawad cut-out + sparks, camera drift), 1
sample, CRF 14 master; QA under `looks/<look>/qa_<look>_test/` (`verify.json`, `stats.csv`, `band_*.png`,
`face.png`, `vs.png`, `ig_crf23.mp4`, `ig_3m5.mp4`).
| look | YMIN | YLOW | YAVG | YHIGH | YMAX | SATAVG | HUEMED | Y p1 / px < 16 | red-orange min | top-5 % red-orange | violet | face HSV hue / OKLab L, C, h | flat 8x8 blocks master / CRF 23 / 3.5 Mbit |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| ember | 11-14 | 19 | 48.4-50.3 | 98-103 | 237-247 | 22.5-23.0 | 158-159 | 16 / 0.19 % | 99.8 % | 99.4 % | 0.1 % | 15.5 / 47.8, 8.2, 39.2 | 0.002 / 0.026 / 0.017 |
| noir_ember | 9-12 | 17 | 45.2-47.1 | 94-100 | 239-245 | 12.1-12.7 | 154-156 | 15 / 1.40 % | 100 % | 99.5 % | 0.0 % | 15.5 / 47.0, 7.2, 38.8 | 0.000 / 0.000 / 0.000 |
| inferno | 13-14 | 20-21 | 47.5-49.1 | 96-100 | 239-247 | 25.7-26.4 | 162-163 | 17 / 0.01 % | 99.8 % | 99.6 % | 0.1 % | 14.8 / 47.4, 8.6, 37.6 | 0.001 / 0.009 / 0.012 |
| gold_hour | 14-16 | 29-30 | 69.8-72.2 | 118-124 | 238-243 | 31.1-31.7 | 143-144 | 22 / 0.00 % | 99.7 % | 94.1 % | 0.0 % | 16.9 / 48.7, 8.4, 44.4 | 0.000 / 0.003 / 0.002 |
| dusk | 9-14 | 20 | 48.6-50.3 | 98-103 | 238-247 | 18.4-18.7 | 192-196 | 17 / 0.06 % | 97.5 % | 99.3 % | 0.4 % | 14.1 / 48.2, 8.2, 37.4 | 0.000 / 0.000 / 0.001 |
| dusk, grain 0 (control) | 13-15 | 20 | 48.7-50.4 | 98-103 | 237-244 | 18.4-18.8 | 192-196 | 18 / 0.00 % | 97.4 % | 100 % | 0.3 % | 14.1 / 48.3, 8.1, 38.3 | 0.361 / 0.529 / 0.478 |
* No YMIN jump > 6 between frames in any clip. YLOW 17-21 (gold_hour 29-30 by design: its brown-black floor).
  YAVG 45-50 (gold_hour 70-72) inside 35-75. YMAX > 240 only in emissive cores (keyword glow, underline head).
* YMIN below 16 is x264 undershoot of grain on true black, not a lift: Y p1 is 15-17 and 0.01-0.19 % of pixels sit
  at 9-15 (noir_ember 1.4 %: most black area + strongest grain). The kit's own `brand_smoke` master shows the
  same (YMIN 12-13). Display clips them to black.
* Banding (darkest smooth world gradient, 300x300, after `libx264 -crf 23` and `-b:v 3.5M -maxrate 4M -bufsize 8M`):
  with grain no contour bands; flat 8x8 blocks <= 2.6 % (ember) and <= 1.2 % elsewhere. Grain-off control: 36 %
  flat blocks in the master, 53 % after CRF 23, with visible concentric contours (`dusk_nograin/.../band_*.png`).
  Grain size was raised before amount: ember at 1.5 px gave 23 % flat blocks after CRF 23 on a 1 s check, 8.7 %
  at 1.8 px; the clip above (1.8 px) shows 2.6 %.

## 9. Hand-offs
**motion-toolkit-engineer** (owns jawad_kit.py / jawad_tx.py; exact values, not applied here):
1. `F.GRADES['ember']` lifts footage black to R +6 codes (shadow_tint R +0.022) and turns skin orange
   (OKLab hue up to +8.7 deg on light / medium skin, chroma x1.29-1.37). Suggest wb (1.02, 1.0, 0.97), contrast 1.10, sat 0.96,
   shadow_tint (0.0, -0.006, -0.012), highlight_tint (0.008, 0.003, -0.008): black stays 0, skin <= 2.0 deg,
   chroma x1.02-1.06.
2. `F.GRADES['noir_ember']` (sat 0.40) greys skin (chroma x0.49-0.53, +10 deg on light skin) and lifts black R +3.
   Suggest wb (1.01, 1.0, 0.98), contrast 1.14, sat 0.85, shadow_tint (0.0, -0.004, -0.008), highlight_tint
   (0.006, 0.002, -0.006): black 0, skin <= 3.0 deg, chroma x0.89-0.95 (the finish's mono + skin protection
   make the monochrome).
3. `jawad_tx.finish`: add a `post=` hook (default `K.post`) so `G.tx_finish` can pass `G.finish` instead of
   capturing K.post for the call; until then `G.tx_finish` is the drop-in.
4. The three new backdrops (section 3.2) are registered from jawad_grade through `J.register_look`; copy them into
   the kit if you want them owned there.

**face-compositor**: `FA.rim_light` (warm_dark base) keeps skin hue (41.3 vs 42.1 raw) and sets the face at OKLab
L ~49 (about 1.25 stops under the cut-out): right for low-key; for hook frames that must reach YAVG >= 45 with the
face as the subject, consider warm_dark exposure ~0.55. Do not stack `G.cutout` on top of warm_dark.

**builders**: adopt the two lines of section 1; bright full-bleed footage: `footage=1`; gold_hour: move
`rays_center` with the sun (or `rays=0` for scenes without a sun); dusk: keep faces near the candle side so the
red-orange rim stays the brightest saturated thing; noir_ember: one practical only (the shadow saturation 0.60
already greys the rest).

**delivery-packager**: masters hold 0.01-1.4 % sub-16 luma from x264 grain undershoot (above); Instagram re-encodes
anyway.

## 10. Open questions
* The slate may reassign looks; each look is generic to its mood (no story props in any backdrop).
* noir_ember's casebook world is a floodlit stadium; the kit's backdrop has one top-right practical. A floodlit
  variant (two or three overhead pools) is a backdrop change for the toolkit engineer, not a grade change.
* Reel masters do not exist yet: per-reel stats, skin crops from the face plan and banding must be re-run on each
  master with `python3 jawad_grade.py verify <master.mp4> <look>` before delivery.

## 11. Commands
```bash
cd pipeline/jawad_reels
python3 jawad_grade.py --selftest          # registration, kit untouched, black never lifted, charts, LUT identity +
                                           # match through ffmpeg, tx_finish, finish timing; exit 1 on failure
python3 jawad_grade.py lut all             # luts/<look>_33.cube + identity_33.cube
python3 jawad_grade.py lutcheck all        # identity + match numbers through ffmpeg lut3d
python3 jawad_grade.py chart all           # <WS>/looks/chart_<look>_{before,after}.png + .json
python3 jawad_grade.py sheet               # <WS>/looks/looks_sheet.jpg, looks_thumbs.png, frame_<look>.png
nice -n 10 python3 jawad_grade.py clip all 3        # <WS>/looks/<look>/<look>_test.mp4
nice -n 10 python3 jawad_grade.py verify <mp4> <look>   # signalstats, hue budget, skin, vectorscope, banding
```
