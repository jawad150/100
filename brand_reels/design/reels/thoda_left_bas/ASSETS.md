# ASSETS · Thoda Left... Bas Bas! (3D props, Blender artist)

Builder: `pipeline/jawad_reels/assets3d_thoda_left_bas.py` (bpy 5.2 Cycles, procedural PBR, real-world metres).
Finals render on the GPU PC (see `RENDER_JOBS.md`); this box only ran half-res 16-spp previews
(`workspace/jawad_reels/thoda_left_bas/out/preview3d/`, sheets in `.../out/sheets3d/preview_*.jpg`).
**Status (2026-10-11): every builder is done and preview-checked; no folder has a final meta.json yet** (finals = the
GPU jobs). Until then the compositor's `Asset3D` stand-in fallback applies; swap in when `meta.json` appears.

All paths below are under `workspace/jawad_reels/thoda_left_bas/assets3d/` (= `RWS/assets3d`). Load with
`S3.Asset3D(name, variant, root=RWS + '/assets3d')`; yaw folders `.at_yaw(deg)`, static folders `.by_label(label)`.
PNG: 8-bit RGBA straight alpha sRGB (view Standard, look None) except the STMaps (16-bit RGBA, view Raw = linear).
All coordinates are frame px of the 1080 x 1920 frame (top-left origin). Cropped yaw folders: sprite px + meta
`frame_xy` (the crop's top-left in the frame) = frame px; `features_per_frame` are in sprite px.
Yaw: degrees about the mast axis, + = counter-clockwise seen from above, 0 = locked on the transmitter (SHOTS §0).

| # | folder | mode / frames | size px | what it shows | camera | anchors / features (frame px, final res) |
|---|---|---|---|---|---|---|
| A5 | `crt/macro/` | static: `room`, `refl`, `spill`, `stmap` (0000-0003) | 1080 x 1920 | 21" CRT close-up, wood-grain vinyl shell, stippled bezel, curved glass (screen off), doily fringe on top, knobs + LED bottom-right, lace runner on the teak table, distemper wall, window light | CAM_TV_MACRO 50 mm, 1.27 m, 8 deg below the picture centre, f/4 on the glass | `screen_quad` TL (127, 678) TR (953, 678) BR (968, 1304) BL (112, 1304); `screen_centre` (540, 981); `knob_ch` (981, 1442); `knob_vol` (871, 1442); `led_xy` (775, 1432) |
| A6 | `crt/room/` | static: `room`, `refl`, `spill`, `stmap` | 1080 x 1920 | the CRT on the teak side table + lace runner, coax from a hole high on the wall, 4 nail clips, cream switchboard (right edge), window sun patch with the iron-bar shadows on the wall left of the TV, terrazzo floor | CAM_TV_ROOM 35 mm, 2.3 m, 1.0 m high, f/5.6 | `screen_quad` TL (417, 922) TR (742, 922) BR (743, 1167) BL (417, 1167); `screen_centre` (580, 1045); `knob_ch` (745, 1222); `led_xy` (668, 1217) |
| A1 | `antenna/day_yaw/` | yaw [-45, +15], 61 frames, 1 deg (frame i = yaw -45 + i) | crop ~830 x 1600 (union alpha bbox + 24 px; exact in meta `size`) | Yagi VHF/UHF (boom 1.5 m, reflector, folded dipole + ABS terminal box with blank sticker, 7 directors, #3 bent 4 deg) on the 42 mm GI mast with the coax taped 3x; golden-hour sun back-left (el 14) | CAM_ROOF 35 mm, 1.2 m high, 3.5 m back, looking up 13 deg, f/5.6 | per frame: `rod_tip`, `mast_top`, `dipole_box`, `mast_axis`, `mast_coping`. Frame px at yaw 0: dipole_box (296, 441), rod_tip (520, 681), mast_top (319, 435); mast at the coping (286, 1565). Union bbox x 93-900, y 345-1920 |
| A2 | `antenna/sunset_yaw/` | yaw [-3, +3], 7 frames, 1 deg | crop ~520 x 1420 | the same antenna backlit by the low sun (el 3): dark silhouette, hot rim lines | CAM_SUNSET 50 mm, 6.2 m back, f/4 | per frame as A1. Yaw 0: dipole_box (615, 501), rod_tip (737, 646); mast at the coping (628, 1413) |
| A3 | `roof/day/` | static: `bg` (opaque), `fg_clamp` (RGBA) | 1080 x 1920 | parapet (weathered plaster, rust streaks under the clamps, chipped coping), black ribbed tank, clothesline + pegs, hazed rooftops with their own antennas; **the pipe is NOT in the plate** | CAM_ROOF (= A1) | `mast_xy` (286, 1565) = pipe axis at the coping; `strap_mark`, `bolt_l`, `bolt_r` (upper clamp) |
| A3 | `roof/sunset/` | static: `bg`, `fg_clamp` | 1080 x 1920 | the roof at sunset, sun disc low right of the mast | CAM_SUNSET (= A2) | `mast_xy` (628, 1413); `sun_xy` (854, 1204) |
| A4 | `clamp/macro/` | static: `bg` (opaque), `fg` (RGBA) | 1080 x 1920 | upper rusty strap clamp in macro on the plaster wall (raking sun from the left, warm floor bounce): `bg` = wall + clamp (pipe invisible, its shadow kept); `fg` = strap + bolts only (pipe holdout) | CAM_CLAMP 100 mm, 0.5 m, 10 deg down, f/2.8 on the strap mark | `strap_mark` (284, 1088); `pipe_mark` (282, 786) at yaw 0; `pipe_axis` (290, 1109); `bolt_r` (782, 1040); `bolt_l` (-369, 1108) off frame left |
| A4 | `clamp/pipe_yaw/` | yaw [-6, +2], 17 frames, 0.5 deg (frame i = yaw -6 + 0.5 i; yaw 0 = frame 12) | strip ~510 x 1920 (meta `size`, `frame_xy`) | the GI pipe (zinc spangle, white rust, rust drips) with its hand-painted 6 x 40 mm mark, coax on the wall side; the clamp's shadow on it | CAM_CLAMP | `features_per_frame.pipe_mark` (sprite px; + frame_xy). At yaw 0 the pipe mark is vertically above the strap mark (x 282 vs 284) |
| A7 | `phone/desk/` | static: `lit`, `spill`, `stmap` (0000-0002) | 1080 x 1920 | phone 162 x 75 x 8.3 mm face up (screen off: black glass, fingerprints, soft monitor-strip reflection), walnut desk, keyboard corner top-right and a fluted cutting-chai glass top-left (both out of focus), tea ring stain | CAM_PHONE 100 mm, 0.84 m, 30 deg off top-down, f/2.0 on the glass | `screen_quad` TL (431, 544) TR (848, 617) BR (661, 1466) BL (205, 1378); `punch_hole` (632, 606); `phone_centre` (540, 982) |

## Layering (bottom -> top)
- Roof: `roof/<v>` bg -> `antenna/<v>_yaw` `.at_yaw(yaw(f))` at its `frame_xy` -> `roof/<v>` fg_clamp.
- Clamp: `clamp/macro` bg -> `clamp/pipe_yaw` `.at_yaw(yaw)` at its `frame_xy` -> `clamp/macro` fg.
- CRT / phone: `room` / `lit` (opaque, screen off) -> picture (snow / film card / phone UI) warped through the `stmap`
  (R = u 0 left -> 1 right, G = v 0 bottom -> 1 top, A = visible picture mask: rounded corners r 30 mm (CRT) / 8.5 mm
  (phone), bezel lip and punch hole excluded) -> `refl` ADD (CRT only: glass reflections on black, alpha = visible
  glass) -> `spill` multiplied by the picture's mean luma, ADD (the screen as an ivory #EFE6D6 emitter, strength 2,
  every other light off: its glow on the bezel, doily, knobs, desk).
- Picture size: CRT 406 x 305 mm (4:3), phone 70.2 x 156.2 mm (9:20). Use `screen_quad` only for a quick
  homography; the stmap carries the real curvature of the CRT glass.

## Deviations from SHOTS §a (tell the motion designer)
1. **CAM_TV_MACRO at 1.27 m, not 0.95 m**: at 50 mm and 0.95 m the 406 mm picture would overfill the frame; 1.27 m
   puts it exactly on the SHOTS target box (x 110-970 / y 640-1330).
2. **CRT controls moved to a bottom strip** under the picture (knobs, LED, 4 keys) and only the speaker grille stays
   in the right column, so the knobs read "bottom-right" in CAM_TV_MACRO as SHOTS asks (a right column would be off frame).
3. **CAM_PHONE at 0.84 m, phone turned 12 deg** (not 0.55 m): needed for the screen box x 220-860 / y 520-1500 at
   100 mm (the bbox is x 205-848, y 544-1466).
4. **CAM_CLAMP at 0.5 m**, centred a little right of the marks so the right ear + bolt read; the mark walk over
   yaw -6..+2 is ~2.2 mm on the pipe = ~23 px at final res (real proportion).
5. **Clamp macro sun from the left (az 203, el 14)** instead of the roof's back-left sun: on the roof the parapet face
   is in shade; the macro needs the raking light SHOTS describes ("raking 14 deg, strong texture").
6. GPU finals (RTX 4060) instead of CPU (lead update); samples per pass in `RENDER_JOBS.md`.

## Look notes (from the previews)
- CRT: dark grey-green phosphor glass with fingerprint smudges and a dust film at the bezel; stippled bezel shinier
  round the knobs; doily scallops on the top edge; window sun patch with bar shadows on the wall (crt/room).
- Antenna / roof: oxidised aluminium, galvanised mast with white rust, rust bands at the clamps, faded coax + black
  tape; the sunset pass reads as a silhouette with rim lines against the sun glow.
- Clamp: rust strap with flaking green-grey paint, dull off-white hand-painted index marks on the strap and pipe.
- Phone: black glass with a soft monitor strip reflection and a lamp edge highlight; walnut veneer with pores and
  scratches; fluted cutting-chai glass two-thirds full on its ring stain.

## Restore copies
`python3 pipeline/jawad_reels/assets3d_thoda_left_bas.py archive` -> `brand_reels/assets/thoda_left_bas/assets3d/`
(JPEG + alpha PNG + 16-bit STMap PNG, < 58 MB, auto quality step-down); `restore` rebuilds the spec folders. Run after
the GPU finals (RENDER_JOBS §3).
