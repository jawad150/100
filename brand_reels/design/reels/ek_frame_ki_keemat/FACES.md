# FACES · Reel 3 · C08 · Ek Frame ki Keemat (face-compositor)

2026-10-09, session 3. Built from BRIEF.md §14 (face plan), §7.2 (layers 04 / 05 / 06), §4 (JD rules), §6 / §7.3 (frames
and cameras), `brand_reels/research/face_assets.md`, LEAD_DECISIONS. Look `ember` (jawad_kit), finish `G.tx_finish(cv, t,
'ember', cuts=CUTS)` with the brief's CUTS. HANDOFF.md does not exist yet. The previs folder (`previs/B1_f0.png` and the
rest) was lost with the workspace, so the stills below are the reference now.

## 1. Files

| what | path |
|---|---|
| face module (import it; never edit it from the reel) | `pipeline/jawad_reels/ek_frame_ki_keemat_faces.py` (`FF`) |
| test stills + numbers (stand-in world, real layers / look / finish) | `workspace/jawad_reels/ek_frame_ki_keemat/faces_test/` (`stills.json`) |
| BRIEF §14 output `<RW>/qa/faces_check.png` | f0 composite at 1:1 (stand-in world; the builder overwrites it with the real f0) |
| source assets (read only, nothing new downloaded) | `workspace/brand_reels/charsheet/cutouts/suit_threequarter.{png,json}`, `_depth.png`; `crops/suit_threequarter*.png` (reconstructed, see §5) |

Pose and licences: `suit_threequarter` only (no swaps, no other pose, no mirroring). 382x556 native -> 764x1112 2x
master (face 246 px tall native), Real-ESRGAN x4plus ONNX (BSD-3), BiRefNet-portrait matte (MIT) + pymatting
decontamination, Depth-Anything-V2-**Small** depth (Apache-2.0). Shown at **0.90** of the 2x master (cap 1.0).

## 2. API (exactly the brief's `face_layers()`, plus draw helpers)

```python
import jawad_kit; import ek_frame_ki_keemat_faces as FF        # jawad_kit FIRST
L = FF.face_layers()   # cached (~3 s): base, rim, halo, shadow, l06, anchor, xy, scale, boxes, head_w, pin, off, shape
                       # every sprite (1437, 1004, 4) premultiplied linear, read-only, SAME anchor (0.5, 0.874)
                       # K.draw(cv, L['base'], *L['xy'], scale=L['scale'], anchor=L['anchor'])  == the BRIEF placement
tl = FF.layer_clock(t) # BRIEF 7.2 clock: t (< 0.3) | 0.3 (0.3-26.4) | t - 33.6 (>= 26.4; the loop's t < 0 world uses t)
FF.draw_layer(cv, 4, tl)        # 04 chehra  (light wrap from what is already in cv = layers 01-03)
FF.draw_layer(cv, 5, tl)        # 05 rim light (emissive, alpha 0)
FF.draw_layer(cv, 6, tl)        # 06 saaya: shadow + halo in one 'over' draw
FF.draw_all(cv, tl)             # 04 + 05 + 06 in order
FF.pane(4, bg) / FF.pane(5) / FF.pane(6)   # 1080x1920 pane sprites at tl 0.3 for the exploded stack
                                # bg = layers 01-03 composited at tl 0.3 (layer 04's wrap, so panes == assembled frame)
FF.idle(tl)                     # (dx, dy, rot_deg, breath) relative to the pause pose (all zero at tl 0.3)
FF.eye_screen(tl)               # (465.7, 1282.0) paused = the C8 punch centre
FF.face_rect(tl) / FF.jd_rect(tl, margin=28) / FF.jd_alpha(tl) / FF.point(tl, uv)
FF.prewarm()                    # call in the reel's prewarm (layers + head / torso parts)
# python3 ek_frame_ki_keemat_faces.py check            -> limits / placement / texture / cost (JSON)
# tools/heavy.sh python3 ek_frame_ki_keemat_faces.py stills  -> faces_test/*.png + stills.json + qa/faces_check.png
```

`boxes` (screen px, paused): face (242.3, 1120.5, 563.6, 1563.6), head (171.7, 925.2, 634.3, 1599.0), eye_mid (465.7,
1282.0), eyes (402.6, 1283.7) / (528.8, 1280.2), hair_top_y 987.3, jd silhouette (0, 987.3, 673.8, 1920). These are the
brief's numbers (face box 242-564 x 1120-1564, eye 465/1282, hair top 987).

## 3. Shot table (`FF.FACES`)

| stretch | frames | state | look | placement | motion | on screen as a person |
|---|---|---|---|---|---|---|
| S1-01 | f0-f8 (0-0.3) | playing | A rim, layers 04/05/06 | bust bottom-centre (330, 1926), 0.90 | `idle(tl)`, tl = t | yes (hook) |
| S1-S3 | f9-f791 (0.3-26.4) | paused / exploded | one pane per layer | same, frozen at tl 0.3 | none (camera only) | as panes; C8 punch 1.09 at f789-f791 is the builder's |
| S4-01/02 | f792-f1007 (26.4-33.6) | playing | A rim | same | `idle(tl)`, tl = t - 33.6, runs into f0 | 26.4-29.4 (3.0 s), then dimmed under the end card |

Rim direction (0.8, -0.5) (flame key and god rays top-right), rim gain 2.4 (look A default), no swaps.

## 4. How it is built

- **Layers (BRIEF 7.2 / 14, exactly):** 04 base = `FA.rim_light(plain, dep, light=(0.8, -0.5), gain=0, halo_strength=0,
  base=warm_dark + veil)`; 05 rim = rgb(look without halo) - rgb(base), alpha 0; 06 halo = rgb(full look A) - rgb(look
  without halo), alpha 0; 06 shadow = matte blurred 28 px (screen), offset (-24, +18), black x0.45, x (1 - matte).
  `FA.fade_open(('left', 'right'))` on all of them (the shadow comes from the faded matte). `l06` = shadow alpha + halo rgb
  in one sprite (drawn 'over': halo + world x (1 - shadow)). All sprites share one size / anchor (padded 120 px left and
  right and 133 px below for the shadow blur).
- **Rigid head, breathing torso (no warp anywhere):** each layer is split into a head plane (feathered `head_box` mask:
  hair, ears, face, beard) and a torso plane with exact recombination (head over torso == the layer at zero offset). The
  torso breathes (vertical scale about the bust bottom, horizontal x0.4); the head rides the neck unscaled.
- **Idle:** `FA.idle(tl, seed=4, breathe=0.0025)` applied RELATIVE to its value at tl 0.3, so every paused frame, every
  pane and the C8 centre sit exactly at the brief's placement. Only while playing (the clock freezes it otherwise).
- **Parallax from the depth map (layered, not per-pixel):** the head plane's idle translation is scaled by
  1 + 0.5 (median nearness of the face - of the torso). Depth-Anything says face 0.441 vs chest 0.455 (the 3/4 head sits
  level with the chest), so the lead is 0.993: effectively none, and honest. In the exploded views JD is a flat card on
  purpose (BRIEF: "an honest flat card"); no depth displacement is used.
- **Black match:** warm_dark exposure 0.42 + a NIGHT_0 airlight veil x0.5 (premultiplied, alpha unchanged).
- **Light wrap (layer 04):** the world behind him blurred sigma 30 px, SCREENED over his outer 14 px at 22 %.
- **Bust bottom guard:** the panel-cut bottom is edge-extended 48 rows (43 screen px) below the cut; measured lift of the
  cut row is never above y 1924.7 anyway, so the guard only matters if a builder punch moves him up.
- **Skin texture:** the SR master is used as it is (no pull-back, no smoothing, no relight); §5.

## 5. Measurements (`check` + `stills.json`)

| item | value | limit / target |
|---|---|---|
| display scale | 0.90 of the 2x master (torso breath peak 0.9045) | <= 1.0 |
| eye at the pause | (465.7, 1282.0) | brief 465 / 1282 |
| idle: eye deviation from the pause pose | <= 2.94 px | small |
| idle: eye speed peak | 0.107 px/frame = 0.30 % of width per s | parallax <= 3 %/s |
| idle: roll | -0.11 .. +0.02 deg | <= 2 deg |
| breathing (torso layer only) | 0 .. +0.50 %, 0.29 Hz | <= 0.5 %, 0.2-0.3 Hz |
| head lead from depth | 0.993 (face 0.441, chest 0.455 nearness) | head lead <= 4 px |
| eye jump at the C8 cut f791 -> f792 | 1.57 px (hard cut, B settles 1.1 -> 1.0) | <= 6 px |
| eye step f1007 -> f0 (loop) | 0.065 px | continuous |
| bust cut row, highest point while playing | y 1924.7 (below the frame) | > 1920 |
| matte fringe, 3 px ring outside alpha, layer 04 alone, BEFORE the finish | +0.10 code values (p95 +0.8) | <= +6 |
| same ring AFTER the ember finish (layer 04 alone) | +1.8 (paused / playing), +7.8 on the f0 / f792 push frames | finish bloom of his shirt and face, not a matte fringe |
| blacks: JD p2 vs the world within 150 px of him (after the finish) | f9 2.34 vs 1.91; f803 1.99 vs 2.13; f846 2.12 vs 2.13 | within 2 code values |
| JD p50 / p99 luma (paused) | 27 / 171 (world p99 237, glow 255) | never brighter than the key |
| texture, cheek patch (416-480, 453-517) Laplacian var. SR / Lanczos 2x of the native crop | 4.55 (right cheek 3.70, forehead 4.89) | agent rule 1.5x: NOT met, kept on purpose (below) |
| cost | `face_layers()` 3 s once; `draw_all` 217 ms per playing frame (base+wrap 127, l06 62, rim 33) | panes are cached for the paused states |
| face vs layout | face box ends x 564; chip pill starts x 595 (31 px; its text at x 649); DEKHA bottom ~915 vs hair top 987 (72 px); no face pixel at x > 930 or y > 1620 | no copy within 60 px of the face (the chip pill edge is HUD, placed by the brief) |

Texture decision: the reconstructed native crop (area 2x downscale of the SR master, `tools/rebuild_crops.py`) gives the
same 4x ratio session 2 measured on the real crop (meta `tex_ratio` 4.05). The pull-back that bijli_chali_gayi used
(k = 0.35, skin only) was rendered next to the untouched master through the full look and the ember finish on f9 at 200 %
(reproduce by setting `FF.TEX_K = 0.35`): the two are indistinguishable under the finish grain, and the
untouched master keeps a little more pore structure. The brief (§14 "skin texture kept, no smoothing") and human-realism /
photo-realism forbid smoothing, so `TEX_K = 1.0`. Nothing reads waxy or crunchy at 100 % or at phone size.

## 6. Stills looked at (all Read; `faces_test/`)

Full frames at 1:1 and at phone size (360x640), plus JD crops at 100 %: `f0000` (hook, push 0.6 frame), `f0009` (pause),
`f0026`, `f0792` (payoff cut, push 1.0), `f0803`, `f0846` (glint), `f0873`, `f0938` (end card dim), `f1007` (loop end).
Exploded stand-in stack (panes 01, 04, 05, 06 through the §7.3 key cameras): `f0153_stack` (cover, yaw 52: face card, the
rim card a hand's width away, the shadow card), `f0234_stack` (FLY 04), `f0252_stack` (FLY 05: the rim alone, sharp),
`f0396_stack` (frontal gap 30), `f0480_stack` (pushed + racked: JD sharp). Panes alone over black: `pane04/05/06.png`.
200 % crops of the hair crest and the jaw edge on f9: clean rim, no grey fringe, no missing hair; the grey wisps at the
back of his head are the photo's own hair highlights. Verdicts: natural skin (warm, not orange, not lightened), suit blacks
on the world's floor, rim reads as his house rim, the face reads at phone size; nothing pasted-on, haloed or rubbery.

## 7. Deviations from BRIEF §14 (and why)

1. `FA.idle` runs **relative to the pause** (zero at tl 0.3) instead of absolute: the paused placement, every pane and the
   C8 centre stay exactly on the brief's numbers; the cost is a 1.57 px eye jump on the hard cut at 26.4 (invisible).
2. `breathe=0.0025` instead of the default 0.004: the pause sits on the breathing trough, so the default would breathe
   0.8 % relative to the rest pose (limit 0.5 %).
3. Breathing on the **torso plane only** (head rigid): the brief applies `FA.idle`'s scale to whole layers, which would
   stretch the face 0.4 % vertically (never-uncanny rule: the face never scales on its own).
4. Black-match veil and light wrap added to layer 04 (task + agent rules); both measured above.
5. No skin pull-back despite the agent's 1.5x texture rule (§5).

## 8. Notes for the timeline builder (`ek_frame_ki_keemat.py`)

- Draw 04 / 05 / 06 with `FF.draw_layer` (or `draw_all`) in assembled states and `FF.pane(i)` sprites in exploded ones;
  build `FF.pane(4, bg)` with the same layers 01-03 canvas you use at tl 0.3 so the panes add up to the assembled frame.
- **DOF on the focus pane (f234 FLY 04, and any yawed pane):** `K.draw_plane(..., dof=True)` blurs a whole pane by the
  CoC at the pane's CENTRE depth. At FLY(04) (yaw 32, aperture 420) the centre is 71 units nearer than the focus distance (4849 vs 4920),
  so the "in focus" face gets a 2.8 px CoC and reads soft (measured on the stand-in: dof=False sharp, dof=True visibly soft at 100 %).
  Draw the pane in focus with `dof=False`, or set `focus_dist` to `cam.depth((0, 0, z_k))` (the pane centre) while it is
  the focus pane. The same applies to pane 05 at f252.
- The C8 punch centre is `FF.eye_screen()` = (465.7, 1282.0) (the brief's 465 / 1282).
- Captions are hidden whenever JD is a readable person; `FF.jd_rect(tl)` is there if an avoid rect is ever needed.
- `G.tx_finish` skin protection stays on (ember: skin 0.70, skin_chroma 0.5); no grade on the cut-out itself beyond §4.

## 9. Open questions

- AI label: LEAD_DECISIONS 5 says ON for all five reels (the character sheets look AI-generated); nothing open here.
- The previs reference `previs/B1_f0.png` is lost; `faces_test/f0000.png` / `qa/faces_check.png` replace it until the
  real f0 is rendered.
