# ASSETS · Pencil Se Rewind (Blender props, stage 2)

Builder: `pipeline/jawad_reels/assets3d_pencil_se_rewind.py` (bpy 5.2.2, Cycles). Status 2026-10-11: module
finished, low-res / low-sample CPU tests looked at for every asset; **finals not rendered yet** (they run on the
RTX 4060 PC, commands in `RENDER_JOBS.md`). An asset is finished only when its `meta.json` exists.

## Where the files land
`RWS = workspace/jawad_reels/pencil_se_rewind`

    RWS/assets3d/<name>/passes/0000.png ... + meta.json        (meta.json written LAST)
    load:  S3.Asset3D(name, 'passes', root=os.path.join(RWS, 'assets3d'))   -> .frame(i) / .by_label('key') / .features

PNG: RGBA 8-bit straight alpha, sRGB, view transform Standard, look None, dither 1.0, exposure -0.8 (label paper in
the lamp pool <= 0.85; glints on aluminium / desk clear coat may clip, the finish blooms them). Opaque plates have
alpha 255. Restore copies: `brand_reels/assets/pencil_se_rewind/assets3d/<name>/passes/` (JPEG for opaque frames,
PNG for RGBA, meta.json as is), rebuilt with `python pipeline/jawad_reels/assets3d_pencil_se_rewind.py restore`.
Texture maps (label handwriting, desk wear, key symbols, HB foil, AA sleeve) are committed in
`brand_reels/assets/pencil_se_rewind/tex3d/` so every machine renders the same pixels.

## Render list
| name | out folder (under RWS/assets3d) | size px | frames / labels | camera | spp CPU / GPU | what it shows |
|---|---|---|---|---|---|---|
| `hub_loop` (R1) | `hub_loop/passes` | 1080x1920 opaque | 16, `loop` x16; f16 == f0 (idx = f mod 16) | CAM_HUB | 64 / 384 | hex pencil upright in the left hub, pencil + both hubs + packs turn clockwise 22.5 deg/f (rewind, side A); motion blur 0.5 |
| `hub_cover` | `hub_cover/passes` | 1080x1920 opaque | 1, `cover` | CAM_HUB | 192 / 1024 | still = hub_loop f0, clean, no motion blur |
| `hub_rescue` (R1b) | `hub_rescue/passes` | 810x1440 opaque (comp x1.333) | 32, `rescue` x32; f32 == hub_loop f0 | CAM_HUB | 48 / 256 | pencil + hubs 11.25 deg/f clockwise; a crinkled tape loop out of the centre head opening flops back over the lower label and is drawn in: 120 mm (f0) -> 0 (f31) |
| `label` (R3) | `label/passes` | 1080x1920 opaque | 1, `still` | CAM_LABEL | 128 / 512 | top-down side-A label: blue ballpoint "Mix '98" / "Side A" / track list (ink pooling, scribble), printed rules, chai ring; pencil lying lower left -> lower right |
| `walkman_loop` (R4) | `walkman_loop/passes` | 1080x1920 opaque | 8, `loop` x8; f8 == f0 | CAM_WALK | 64 / 384 | generic walkman, keys up, LED on, spools in the lid window turn 7.5 deg/f (play direction; comp reverses / speeds for REW); orange-foam headphones back left, two AA cells lower right (one tooth-dented) |
| `walkman_keys` | `walkman_keys/passes` | 519x247 crop (of 1080x1920) | 4: `play_down`, `rew_down`, `stop_down`, `led_off` | CAM_WALK | 96 / 512 | key row + LED patches; paste at `frame_xy` = (360, 1135) over walkman_loop |
| `walkman_eat` (R4b) | `walkman_eat/passes` | 810x1440 opaque (comp x1.333) | 32, `eat` x32 | CAM_WALK | 48 / 256 | PLAY down; f0-f5 lid springs open 0 -> 9 -> 19 -> 26 -> 24 -> 22 deg; f6-f31 ribbon spills from the head opening over the front strip (between REW and the LED), down the front face and curls on the desk towards screen left; f0 == walkman_loop f0 with PLAY down |
| `pencil_top` (R5) | `pencil_top/passes` | 600x1700 RGBA | 2: `key` (pencil), `shadow` (shadow catcher: black, alpha = shadow) | ortho top-down | 96 / 512 | the same pencil (dents, HB facet) eraser up, 1500 px long, ~100 px across corners; neutral-warm key so the lacquer reads yellow on UI glass |

Total 96 frames.

## Features / anchors (px in each asset's own frame; also written into meta.json `features`)
Solved from the scenes with `python pipeline/jawad_reels/assets3d_pencil_se_rewind.py cams`
(saved to `RWS/out/features_solve.json`). Quads are TL, TR, BR, BL of the object (screen order may rotate).

**CAM_HUB** (100 mm, 73 deg above the desk, 0.45 m, f/5.6 focused on the pencil-hub contact; cassette yawed 18 deg)
- `hub_loop`, `hub_cover` (1080x1920): `hub_xy` = `pencil_contact_xy` (560.0, 1255.8) = pivot of the spin;
  `eraser_xy` (560.0, 812.1); `pencil_axis` [(560.0, 1255.8), (560.0, 812.1)]; `hub_r_xy` (1030.6, 1109.6) (soft at the
  right edge); `window_quad` [(466.8, 1201.4), (1069.6, 1015.1), (1125.1, 1163.4), (517.7, 1353.1)],
  `window_rect` [466.8, 1015.1, 1125.1, 1353.1]; `label_quad` [(199.6, 1049.1), (1182.4, 749.3), (1364.6, 1220.4),
  (357.3, 1537.3)] (runs off the right edge).
- `hub_rescue` (810x1440 = the same framing x0.75): `hub_xy` (420.0, 941.9), `eraser_xy` (420.0, 609.1),
  `hub_r_xy` (773.0, 832.2), `window_rect` [350.1, 761.3, 843.8, 1014.8], `label_quad` [(149.7, 786.8), (886.8, 562.0),
  (1023.5, 915.3), (268.0, 1153.0)]. Upscaled x1.333 it matches hub_loop.

**CAM_LABEL** (60 mm straight down, f/5.6, cassette yawed 6 deg) `label` (1080x1920): `label_quad`
[(88.0, 728.1), (946.3, 637.9), (992.0, 1071.9), (133.7, 1162.1)], `label_rect` [88.0, 637.9, 992.0, 1162.1]
(centre ~(540, 900)); `cassette_quad` [(30.6, 710.8), (998.9, 609.0), (1063.6, 1224.3), (95.3, 1326.0)];
`pencil_tip` (263.1, 1349.0), eraser off frame at (1364.6, 1623.6).

**CAM_WALK** (50 mm, 30 deg above the desk, 0.40 m, f/8, walkman 3/4 from front-left)
- `walkman_loop` (1080x1920): `window_quad` (lid window) [(276.8, 1122.3), (621.1, 1024.0), (714.5, 1088.5),
  (359.9, 1196.5)], `window_rect` [276.8, 1024.0, 714.5, 1196.5]; `hub_l_xy` (377.5, 1152.6), `hub_r_xy` (613.4, 1082.5)
  (spool pivots seen through the window); `key_rects` stop [388.2, 1254.6, 512.0, 1314.4], play [490.2, 1222.8,
  611.5, 1280.2], ff [588.1, 1192.2, 707.0, 1247.3], rew [682.2, 1162.7, 798.9, 1215.8]; `led_xy` (840.1, 1169.6);
  `walkman_bbox` [77.6, 947.9, 983.5, 1541.4]; `battery_dented_xy` (790.0, 1630.0); `torn_pad_xy` (254.6, 907.5).
- `walkman_keys`: crop rect in the full frame [360, 1135, 879, 1382] -> `frame_xy` (360, 1135), crop 519x247;
  meta features are shifted into the crop.
- `walkman_eat` (810x1440, x0.75 of the same camera; values at f0, lid closed): `window_rect` [207.6, 768.0, 535.9,
  897.4], `led_xy` (630.1, 877.2), `hub_l_xy` (283.1, 864.5), `hub_r_xy` (460.1, 811.9), `walkman_bbox`
  [58.2, 710.9, 737.6, 1156.0], `battery_dented_xy` (592.5, 1222.5).

**pencil_top** (600x1700, ortho): `eraser_top` (300, 100), `ferrule` (300, 218.8), `tip` (300, 1600); axis vertical.

## Props (modelled once, reused)
CASSETTE 100.4 x 63.8 x 12 mm SDF shell (smoked PS with shadow-ray tint so hubs / packs inside are lit), clear window,
5 cross-head screws with rust, POM hubs with 6 teeth, anisotropic oxide packs (34 / 40 mm), tape path, rollers, felt pad
on a bronze spring, paper label (fibre bump, ink grooves), scratches / fingerprints / dust. PENCIL hex 7 mm x 120 mm,
5 blade facets, blunted graphite, chipped lacquer, 4 tooth dents, HB foil 40 % rubbed off, crimped ferrule with a dent,
worn eraser. WALKMAN 110 x 80 x 29 mm ABS body (edge wear, dust in gaps), brushed-alu lid on a hinge with a smoked
window, engraved keys (3 mm travel), ribbed wheel, nickel jack + plug, amber LED, sticker residue on the lid corner.
HEADPHONES chrome band, black cups, flat open-cell orange foam discs 50 x 10 mm (one torn), tangled cable to the jack.
BATTERIES 2 x AA generic red/black "AA 1.5V", one with 3 tooth dents. TAPE ribbon 3.81 x 0.05 mm (oxide / glossy back,
accordion crinkle, twist, kinks, one stretched lighter segment). DESK sheesham veneer, worn clear coat, compass arcs,
ink stain, dust, eraser crumbs. No brand marks anywhere. Light rig LAMP: tungsten spot (2900 K) top-left, FLAME rim
back-right, warm world + bounce card; no blue light.

## Deviations from SHOTS.md (lead please note)
- CAM_HUB is 73 deg above the desk at 0.45 m (SHOTS says 32 deg / 0.30 m): that is the only framing that also meets the
  SHOTS feature targets (hub (560, 1260), eraser ~(575, 820) -> (560, 812), window towards (800, 1180), right hub soft at
  the right edge) and the cover crop "pencil + hub y 820-1420". f/5.6 instead of f/4 (f/4 at 0.45 m blurs the label).
- R1b loop: the desk in front of the shell is below the frame edge in CAM_HUB, so the pulled-out loop flops back over
  the lower label (dark tape on lit paper) instead of hanging toward the camera on the desk.
- AA cells at ~(790, 1630) instead of (820, 1500) so the R4b spill on the desk stays clear of them.
- Exposure -0.8 EV and softer keys so the label paper sits <= 0.85.
