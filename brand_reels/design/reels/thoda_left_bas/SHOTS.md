# SHOTS · Bijli series #2 · Thoda Left... Bas Bas! (`thoda_left_bas`)

r1, 2026-10-11, creative director. Frames at 30 fps; 100 BPM = 18 f / beat, 72 f / bar; DUR 1008 f. Words come from
`SCRIPT.md` (ids H1…P1, UI ids T1…B1); this file owns frames, cameras, transitions, assets and cues. No humans and no
Jawad face anywhere: people exist only as shouted captions, chat bubbles, objects that move by themselves, and light.

## 0. The two clocks that drive the picture

**Antenna yaw `yaw(f)`** (degrees about the mast axis, 0 = locked on the transmitter, + = counter-clockwise seen from
above). One table drives the roof shots (the rendered mast via `Asset3D.at_yaw`) and, off screen, the TV.
`sig = clamp(|yaw| / 12)` (smoothed 3 f); locked when `|yaw| < 0.75`. Between keys: the ease named; "wob" = wind
wobble `a·sin(2π·hz·t)`.

| f | yaw | ease into it | note |
|---|---|---|---|
| ≤ 5 (and the loop tail f864-1007 on `t - DUR`) | -14 | wob 1.5° @ 1.3 Hz | pre-roll state, snowy |
| 6-16 | +9 | inout_cubic | "right..." |
| 28-36 | 0 | out_back (s 0.6) | **lock f36** |
| 60-66 | -18 | in_cubic | slip (wind), wob 1° to f107 |
| 108-113 / 114-117 / 118-126 | -25 / hold / -32 | inout_cubic | wrong way, regrip pause |
| 162-179 | -32 frozen (wob 0) | | "kiska left?!" |
| 180-197 / 198-213 / 225-240 | -14 / +6 / -4 | inout_cubic | overshoot = snow at f214 |
| 252, 261, 270, 279, 288 | -3, -2, -1, -0.5, 0 | each 4 f out_cubic | clamp clicks on 8ths; chalk marks align f288 |
| 346-358 | +11 | in_cubic | gust f342; wob 3° @ 0.8 Hz to f413 |
| 414-431 | -40 | in_expo | the swing that carries M3 |
| 576 / 594 / 612 / 630 (6 f each) | -6 / +4 / -6 / -1 | inout_cubic | split screen (S10) |
| 720-827 / 828-833 | 0 / +2 | / out_cubic | sunset; the 2° nudge by itself (easter egg) |

**Client clock (edit world):** title X in the viewer (1080-px comp units): 540 (f432) → **538 f477** (v2) → 540 f495
(v3) → 538 f509 (v4) → 541, 539, 538, 540, 537, 539 on the 8ths f522-f567 (v5-v22, list rows every 3 f) → 538, 541,
538, 539 on f576/594/612/630 (v23-v26) → **538 locked f648 (v27, = v2: easter egg)**. `sig_c` = 1 f468-f647 (viewer
title ghost-double: 0.25 opacity, offset 6 px toward the last move), 0 from f648.

## 1. Shot list

Transitions: `jawad_tx` ids; "cut + L3 p" = beat cut with exposure push p in `CUTS`. Every cut on a beat.

| shot | f (s) | picture (3D asset → SHOTS §a) | camera | text (SCRIPT ids) | out | SFX anchors (§b) |
|---|---|---|---|---|---|---|
| **S1** hook A | 0-71 (0-2.37) | CRT macro (A5): curved glass full of warm snow; the `SUNDAY KI FILM` card ghosting and sliding with `yaw`; f36 snaps clean (snow 3 %, colour in); f63 slips back to snow; **B0** bubble pops top-right f63-f71 | locked 50 mm, low 8°; f0 carries the loop push 0.6 | H1, H1b f18, **H2 f36**, H3 f54, B0 f63 | cut + L3 0.5 @ f72 (splice) | static bed (sig), tv_lock f36, notif_ping f63 |
| S1B hook B | 0-71 | glass viewer + client bubble (UI §c): title nudges 540 → 538 on f9 with "-2 px"; f62-f71 a horizontal snow tear (2D) wipes it | locked 2.5D, push 1.00 → 1.02 | HB1, B0b | splice f72 | bubble_pop f0, ui_tick f9, glitch_short f62 |
| **S2** roof day | 72-197 (2.40-6.60) | roof plate day (A3) + mast/antenna (A1) on `yaw`, low angle against a gold sky, rays; coax sways; the mast jerks the wrong way f108-126, freezes f162 | 35 mm low angle 25° up, handheld drift 3 px / 0.2° | R1, R2 f99, R3 f135, **R4 f162** | cut + L3 0.3 @ f198 | wind bed, antenna_creak f108/f118, tape_stop f162 |
| S3 CRT room | 198-251 (6.60-8.40) | CRT room (A6): the TV on a table under a lace doily, coax running down the wall from a ceiling hole, window light; picture improves, overshoots into snow f214, recovers | locked 35 mm, slow push 1.00 → 1.03 | C5, C6 f225 | beat cut @ f252 | static bed, glitch_short f214 |
| S4 clamp macro | 252-305 (8.40-10.20) | clamp macro (A4): GI pipe turning in the rusted strap clamp in clicks on the 8ths; a white paint mark on the pipe walks toward the mark on the clamp, aligns f288 | locked 100 mm f/2.8, focus on the strap | C7, C8 f288 | cut + L3 0.6 @ f306 | clamp_tick ×5, slot_tick f288 |
| **S5** CRT lock | 306-377 (10.20-12.60) | CRT macro (A5, 1.12× push-in framing): picture locked and crisp, warm card + a 1 s "film starts" shimmer; gust f342, slip f346-358 → snow, horizontal roll | locked; 2D push 1.12 → 1.15 | C9, C10 f351 | beat cut @ f378 | tv_lock f306 (+ sitar/harmonium sting), wind_gust f342, glitch_short f348 |
| S6 roof wind | 378-431 (12.60-14.40) | roof day (A1 + A3), mast wobbling in wind, f414 big swing left | drift 3 px; f414-431 camera pans 40 px with the swing | C11 (exits on the M3 track) | **M3 @ f432** (move track x 940 → 540 → 140 at y 760: the director rod tip → the title clip) | whoosh_fast + card_slide (M3 cues) |
| **S7** UI timeline | 432-485 (14.40-16.20) | glass UI (viewer + timeline, UI §c), warm dark void with bokeh; title slides in on the M3 track and settles f441; **T1 toast f468** (re-hook 46 %); nudge 540 → 538 f477 | 2.5D plane rot (4°, -6°, 0), push 1.00 → 1.03 | C12, T1, X1 | cut + L3 0.3 @ f486 | laptop_fan bed, notif_ping f468, mouse_click + ui_tick f477 |
| S8 phone macro | 486-521 (16.20-17.37) | phone on the desk (A7): screen shows the client thread (UI §c), bubbles f490 / f504; the phone buzzes (2D jitter ±2 px, 8 f) on each | locked 100 mm f/2.0, 30° down | P1b, P1c | beat cut @ f522 | phone_buzz f488/f502, bubble_pop f490/f504 |
| S9 avalanche | 522-575 (17.40-19.17) | UI: timeline slides down out (f522-528); revision list stacks a row every 3 f (v5 → v22), X readout jitters on 8ths, ghost-double on the title | push 1.03 → 1.06 | L1, C13 f540 | beat cut @ f576 | ui_tick on 8ths, slot_tick per row (−18 dB) |
| **S10** TAB / AB split | 576-647 (19.20-21.57) | top half y 0-958: roof day + antenna (A1 at 0.62 scale); bottom half y 962-1920: mini viewer + chat bubble; FLAME 2 px divider y 960; both move together on f576/594/612/630 | locked both halves | S1-S4 (far caption top, bubble bottom, same words) | cut + L3 0.5 @ f648 | antenna_creak + ui_tick together ×4, bubble_pop ×4 |
| **S11** client lock | 648-719 (21.60-24.00) | UI: client bubble T2 f648, title snaps crisp at 538 (sig_c → 0), list row v27 lights; export dialog f684, bar 0 → 100 % by f716 | push 1.00 → 1.03 | **C14 f648**, T2, C15 f684, E1 | **M2 @ f720** | tv_lock f648 (same sound as f36/f306), impact_big, render_complete f716 |
| **S12** roof sunset | 720-863 (24.00-28.80) | roof sunset plate (A3) + antenna sunset (A2): the antenna as a backlit silhouette against a low sun, rays; still; **drop-out f738-755**; **PAYOFF f756**; antenna nudges 2° by itself f828 | 50 mm, drift 2 px; slow push 1.00 → 1.04 | **P1 f756-863** | **M3 @ f864** (track: rod tip x 600 → 540 → 480: the nudge → the TV picture slide) | wind only f738-755, reverse_cymbal → f756, sub_drop + payoff hit f756, clamp_tick f828 |
| S13 CRT loop | 864-1007 (28.80-33.60) | CRT macro (A5) = the frame-0 world on the `t - DUR` clock (snowy, ghost sliding); **profile outro f882-1007** dims it; **B1** bubble f990 | locked (= f0 framing) | outro (question + key), B1 | **loop seam → f0** (`E.loop_world(..., d=0.6)`) | static bed back, outro cues, notif_ping f990, reverse_swell ends f1008 |

Rhythm: 2.4 / 4.2 / 1.8 / 1.8 / 2.4 / 1.8 / 1.8 / 1.2 / 1.8 / 2.4 / 2.4 / 4.8 / 4.8 s. Single image (cover / anchor):
S1 at f36-f45 (the lock). Payoff anchor: S12 f780. Loop: f1007 → f0 is the same CRT, same yaw clock.

---------------------------------------------------------------------------------------------------------------

## a. BLENDER PROPS (blender-3d-artist)

Builder `pipeline/jawad_reels/assets3d_thoda_left_bas.py` (copy the engine helpers of
`assets3d_bijli_chali_gayi.py`: `reset`, `principled`, `aged`, `mat_teak`, `lathe`, `cyl`, `light`, the crop-to-alpha +
meta writer). bpy 5.2, Cycles **CPU, threads 2**, adaptive threshold 0.02, OpenImageDenoise with albedo + normal,
fixed seed, view transform Standard, look None; RGBA 8-bit straight-alpha sRGB PNG (STMaps 16-bit, linear, no
denoise). Output `RWS/assets3d/<name>/<variant>/0000.png … + meta.json` (written last), loadable as
`S3.Asset3D(name, variant, root=RWS + '/assets3d')`. Every run through `tools/heavy.sh`; `--preview` = 16 spp,
half res. Palette references as in Bijli (project.json tokens); **no text, logo or brand mark on any prop** (the
only marks are the paint index marks and a blank sticker).

**Realism rules (Jawad 2026-10-11, binding):** physically based materials with real-world dimensions (metres in the
scene); every hard edge bevelled (0.5-2 mm, 2-3 segments); surface breakup on every material (roughness noise,
dust in cavities via AO/pointiness masks, scratches, rust/oxidation where water runs); lighting only from plausible
sources (sun + sky, window, practical screen glow, desk lamp, monitor fill) with area/sun soft shadows; real lens
DOF (`dof.use_dof`, f-stop given per camera). Few heroes, seen close: the antenna, the CRT, the clamp, the phone.

### Materials (shared library in the builder)

| id | real material | PBR recipe |
|---|---|---|
| `alu_oxidised` | weathered aluminium tube (antenna elements, boom) | metallic 1, base #B9B6B0, roughness 0.38 → 0.62 by noise (scale 40), white-chalky oxidation patches (metallic 0, base #D8D4CC, rough 0.85) masked by noise × pointiness × "up-facing", fine longitudinal brushed bump (anisotropic stretch 20:1), dark grime in rivet cavities |
| `gi_pipe` | galvanised iron pipe 42 mm OD (mast) | metallic 1, base #9A9A94, zinc spangle (Voronoi scale 300, ±0.08 roughness), rust patches (base #6B3A1E → #A0522D, metallic 0, rough 0.9, slight bump) concentrated at threads, clamp contacts and drip lines down the pipe |
| `steel_strap` | mild-steel flat strap clamp 25 × 3 mm + M8 bolts | mostly rust (#5A2E16 / #8B4513), flaking old green-grey paint remnants (#5F6B5C, 30 % coverage), orange rust streaks down the plaster below it (decal-like gradient on the wall material) |
| `plastic_abs_aged` | black ABS terminal box, element insulators, knobs | base #151312, roughness 0.45, sun-faded grey on up-facing faces (#3A3632), micro-scratches (noise-line bump), dust in edges |
| `coax_pvc` | RG-6 coax, PVC jacket 7 mm | base #1C1A19 sun-faded to #3B3734 on top, roughness 0.6; black PVC tape wraps (rough 0.35, slight sheen) at 3 points on the mast |
| `plaster_weathered` | cement-plastered brick parapet | base #8E8478 with darker water stains (#5D5248) running down from the coping, hairline crack bump, chipped corner exposing brick (#8A4B32), black algae streaks, roughness 0.9, displacement-free (bump only) |
| `paint_mark` | white enamel index mark, hand-painted | base #E8E2D2, roughness 0.5, uneven brush edge (noise-warped mask), chipped |
| `crt_glass` | CRT faceplate glass | transmission 0, glossy dielectric IOR 1.52, roughness 0.04, coat 1; dark phosphor base #101412 (screen off); fingerprint smudges (roughness +0.1 noise) and a thin dust film near the bezel |
| `wood_vinyl` | 90s TV cabinet wood-grain vinyl | `mat_teak` re-tinted (#5B3A22 → #7A5232), roughness 0.42, slight coat, edge wear to the pale substrate on corners |
| `bezel_plastic` | dark grey textured plastic front | base #2B2927, roughness 0.55, fine stipple bump, worn shiny where hands touch (around the knobs) |
| `knob_worn` | channel / volume knobs | ABS knob #1A1817 with a brushed chrome insert (#C9C7C2, metallic 1, rough 0.25), ridged grip bump, white index line worn half off |
| `lace_doily` | crocheted cotton doily, aged | base #E9DFC8 yellowed, alpha-mask lace pattern (procedural radial pattern), sheen 0.3, slight drape (cloth sim or shrinkwrap onto the cabinet top, bake once) |
| `distemper_wall` | 90s distemper-painted wall | base #C8B48E (pale yellow), mottled, roughness 0.95, a darker hand-height smudge band |
| `walnut_desk` | desk veneer | walnut grain, roughness 0.35-0.5, light scratches and a tea ring |
| `phone_glass` / `phone_alu` | modern phone | black glass IOR 1.5, rough 0.02, faint fingerprints; bead-blasted aluminium frame #3A3A3C rough 0.35; camera bump with sapphire lens covers |
| `tea_glass` | fluted "cutting chai" glass | glass IOR 1.5 with 12 vertical flutes, inner tea film residue (#7A4A1E alpha 0.6) and a tea line 1/3 down |

### Assets

| # | asset (name/variant, mode) | geometry and real dimensions | camera | lighting | render (size, spp, passes) | est. CPU (2 thr) |
|---|---|---|---|---|---|---|
| A1 | `antenna/day_yaw` (mode `yaw`, yaw_range [-45, 15], 61 frames, 1°) | **Yagi** VHF/UHF combo: boom 1.50 m × 19 mm square alu tube, 1 mm wall, end caps (one missing); reflector 0.72 m; folded dipole 0.64 m (12 mm tube loop) with the black ABS terminal box 80×50×30 mm (2 screws, blank faded sticker); 7 directors 9.5 mm rod tapering 0.58 → 0.48 m, spacing 0.18-0.22 m, each through a black insulator saddle with a rivet; **director 3 bent 4°**; boom-to-mast U-bolt clamp (8 mm rod, 2 nuts, rust); **mast** GI pipe 42 mm OD, 2.2 m visible above the parapet coping, threads + rust at the top; coax RG-6 from the terminal box looping down the mast, taped 3×. The mast + antenna rotate together about the pipe axis | `CAM_ROOF`: 35 mm, at 1.2 m from the floor, 2.6 m from the mast, pitch 25° up; DOF f/5.6 focused on the dipole | sun (angle 0.6°, strength 4, warm #FFD7A0 from the sky model) elevation 14°, azimuth back-left 140° → gold rims on the rods; Nishita-type sky world (air 1, dust 3) as fill; no other lights | 1080×1920 frame, cropped to the union alpha bbox + 24 px (expect ~1080×1150, top of frame); 48 spp + OIDN; single pass `day` (RGBA over sky = alpha); meta features `rod_tip` (director 7 tip), `mast_axis_x`, `dipole_box` per frame | ~25 min |
| A2 | `antenna/sunset_yaw` (mode `yaw`, [-3, 3], 7 frames) | A1 | `CAM_SUNSET`: 50 mm, 3.5 m back, pitch 18° up, the low sun disc just right of the mast; DOF f/4 | sun elevation 3°, behind the antenna (azimuth 175°), strength 3 #FFB45A; sky as fill only → rods read as dark silhouettes with hot gold rim lines | 1080×1920 crop, 64 spp | ~5 min |
| A3 | `roof/day`, `roof/sunset` (mode `static`, labels `bg`, `fg_clamp`) | parapet 0.90 m high, 0.23 m brick + plaster, 60 mm coping lip, cracked corner; **two strap clamps** (`steel_strap`) holding the mast to the inside face of the parapet (the pipe itself NOT in the plate: holdout); rust streaks under the clamps; coax running over the coping and down; black HDPE water tank Ø 1.10 × 1.30 m (ribbed, no logo, sun-faded top) at 4 m left; clothesline steel wire 3 mm with 3 wooden pegs; 6-8 distant rooftop boxes with their own small antennas and tanks (low poly, hazed, out of focus) | `CAM_ROOF` (day), `CAM_SUNSET` (sunset) | as A1 / A2 | 1080×1920 opaque; `bg` 128 spp; `fg_clamp` = the strap clamps only (everything else holdout), RGBA, composited **over** the rotating pipe; meta `mast_xy` (pipe axis at the coping) | ~16 min |
| A4 | `clamp/macro` (mode `static`: `bg`, `fg`) + `clamp/pipe_yaw` (mode `yaw`, [-6, 2], 17 frames, 0.5°) | the upper strap clamp of A3 in macro: strap, 2 M8 bolts with rust bloom, plaster texture, a **white paint index mark** on the strap edge; the pipe with its own hand-painted mark (vertical stroke 6 × 40 mm) that walks toward the strap mark (aligned at yaw 0) | `CAM_CLAMP`: 100 mm, 0.45 m, eye-level to the strap, slight 10° down; **f/2.8**, focus on the strap mark (pipe mark sharp at 0°) | sun from A1 (raking 14°, strong texture) + sky fill; a faint warm bounce card from below (sunlit roof floor) | `bg` / `fg` 1080×1920 128 spp; pipe strip cropped (~460×1920) 96 spp ×17 | ~12 min |
| A5 | `crt/macro` (mode `static`: `room`, `refl`, `spill`, `stmap`) | **21" CRT TV**, cabinet 560 W × 470 H × 480 D mm, `wood_vinyl` sides/top, `bezel_plastic` front; faceplate 406 × 305 mm visible, spherical bulge (sagitta 18 mm), rounded corners r 30 mm, inner black mask; right column: speaker grille (perforated, 80 holes), 2 `knob_worn` (Ø 28 × 18 mm, channel knob with 12 detent ridges), 4 push buttons, red standby LED (off) | `CAM_TV_MACRO`: 50 mm, 0.95 m, 8° below the screen centre; screen ≈ x 110-970, y 640-1330; knobs bottom-right, doily fringe top edge; DOF f/4 on the glass | afternoon room: window area light 1.2 × 1.0 m from screen-left (warm #FFD9A8, 6500 K-ish sun patch through it hitting the cabinet side), soft fill bounce from the floor, faint ceiling bounce; **screen dark** in `room` | 1080×1920 opaque. `room` 128 spp; `refl` = glass reflections only (screen glass glossy, everything else holdout/visible to reflection only) RGBA; `spill` = the screen as a uniform IVORY emitter (strength 2), lights off: its light on the bezel, doily, cabinet top (multiplied by the picture's mean luma in 2D); `stmap` = screen UV (R, G) + mask (A), 16-bit, 16 spp, no denoise. Meta `screen_quad`, `knob_ch`, `led_xy` | ~14 min |
| A6 | `crt/room` (same passes as A5) | A5 on a teak side table (0.65 m) with a lace runner; distemper wall; coax entering through a hole near the ceiling, clipped down the wall with 4 nail clips; a plastic switchboard with 2 switches + socket (cream, yellowed); window frame at left edge with light patch on the wall | `CAM_TV_ROOM`: 35 mm, 2.3 m, camera 1.0 m high, TV centred y 1050; DOF f/5.6 | as A5 + god rays added in 2D (look rays_center (0.08, 0.30)) | 1080×1920, 4 passes as A5 | ~14 min |
| A7 | `phone/desk` (mode `static`: `lit`, `spill`, `stmap`) | phone 162 × 75 × 8.3 mm (`phone_glass`, `phone_alu`, camera bump 3 lenses, no logo) face up on `walnut_desk`; at frame edges: a keyboard corner (dark keycaps, no legends readable, out of focus), the `tea_glass` half full of chai on a ring stain | `CAM_PHONE`: 100 mm, 0.55 m, 30° down, phone diagonal, screen ≈ x 220-860, y 520-1500; **f/2.0**, focus plane on the screen glass | warm desk lamp area light 0.3 m top-left (#FFC88A), cool-neutral monitor fill from behind-top (dim, #E8E4DC), screen as practical in `spill` | 1080×1920 opaque, `lit` 128 spp, `spill` 64, `stmap` 16-bit 16 spp; meta `screen_quad` | ~12 min |

Total ≈ 1 h 50 min CPU at 2 threads (estimates; run `--preview` first, finals only after the layout check). Order:
A5 (hook) → A1 → A3 → A4 → A6 → A7 → A2. Layout check: `python3 assets3d_thoda_left_bas.py targets` prints each
camera's screen boxes against: CRT screen (A5) x 110-970 / y 640-1330; antenna dipole box (A1) inside y 280-1000,
rod tips ≥ 60 px inside the frame at yaw -45 and +15; phone screen (A7) x 220-860 / y 520-1500; all lockups in
SCRIPT §3 stay clear of the hero: lockups sit in y 300-780, the CRT screen starts at y 640, so H/C lockups on CRT
shots get a SMOKE scrim (ui.frost_poly or a 0.55 dark gradient) where they overlap the glass.

**2D, not rendered:** the snow, ghost and roll on the CRT (procedural noise warped through `stmap`, warm ivory
#EFE6D6, 2-frame grain hold = 15 fps snow), the `SUNDAY KI FILM` card (UI §c), the phone screen content, all glass UI,
the split-screen layout, wind sway of the coax (2D mesh warp ±4 px), the phone buzz jitter, god rays (`gold_hour`).

## b. SOUND (sound-designer + music-supervisor)

Files: `thoda_left_bas_music.py`, `thoda_left_bas_sfx.py` (cues on `audio.py` catalog names + the new synth sounds
below), mixed per the series: `_ig` = music + SFX, `_ig_songready` = SFX only. -14 LUFS, TP ≤ -2.0 dBTP wav
(≤ -1.5 after AAC). Leave a 1-4 kHz pocket (-3 dB shelf on music during caption shouts) for an optional VO later.

**Music (original, 100 BPM, 4/4, key D minor → F major on the payoff).** A 90s-Sunday-TV lo-fi: dholak + light tabla
groove, a detuned Casio-style keyboard melody (2-bar riff), sitar plucks as answers, harmonium pads; edit world
(bars 6-9) keeps the riff on clean Rhodes keys + 808 sub + tight hats (same melody = same "dialogue").
**Signature: the tuning filter.** The music bus runs through a band-pass driven by the same `sig(t)`: sig 1 =
300 Hz-2.5 kHz + crackle + slight wow (±8 cents), sig 0 = full range; every lock (f36, f306, f648) opens the filter in
4 frames and lands a downbeat. Static (pink-ish noise, `tv_static`) sits *under* the music, gain = -20 dB + 14·sig.
| bar | f | music |
|---|---|---|
| 0 | 0-71 | riff band-limited; f36 filter opens, kick + tabla "dha"; f63 closes again |
| 1-2 | 72-197 | roof: dholak groove, mid-fi (wind-filtered); f162 **tape_stop** halts the music for 1 beat (f162-179), restarts f180 |
| 2-5 | 198-431 | groove builds; f306 full open + harmonium swell + sitar run ("the film starts"); f342 gust, filter closes; f414 riser into M3 |
| 6-9 | 432-719 | modern version, 808 under; ghost-double = a slight chorus on the keys while sig_c 1; f648 opens fully (lock), f684-716 build with the export bar |
| 10 | 720-737 | sunset: pads only; **drop-out f738-755** (music and SFX off, wind -40 dB only) |
| 10-11 | **756**-863 | **payoff hit f756**: sub + dholak "dha" + harmonium F major chord + reverse cymbal landing on f756; riff returns warm and full-range |
| 12-13 | 864-1007 | riff band-limited again under the outro (-4 dB), resolves to bar 0's first note so f1007 → f0 loops |

**SFX cue list (frame = hit frame, `align='hit'`; NEW = synthesise in `thoda_left_bas_sfx.py`)**
| f | name | dB | note |
|---|---|---|---|
| 0 | impact_soft | -8 | loop release (lp 900) |
| 0-1007 | tv_static (NEW, bed) | -20 + 14·sig | only on CRT shots (S1, S3, S5, S13) and as a far bed (-34) on the roof |
| 0-71 | room_tone | -32 | TV room |
| 6, 120 | antenna_creak (NEW: GI pipe squeal in the strap, 0.3-0.6 s) | -16 / -12 | off-screen in S1; in S2 on the jerks |
| 18 | swish_small | -14 | keyword flip |
| **36** | **tv_lock** (NEW: static gate-out + low thunk + 30 ms tonal "ping" of the picture) | -6 | the lock; reused at **306** and **648** |
| 63 | glitch_short | -12 | slip |
| 63 | notif_ping | -14 | anachronism bubble |
| 72-431 | wind_bed (NEW, roof air, gusty) | -28 | + outdoor_birds -32, desi_city -36 |
| 108 | antenna_creak | -12 | wrong way |
| 162 | tape_stop | -8 | "kiska left?!" (music halt) |
| 214 | glitch_short | -14 | overshoot into snow |
| 252, 261, 270, 279 | clamp_tick (NEW: metal-on-metal click + ring, pitch up 1 semitone each) | -12 | 8ths |
| 288 | clamp_tick + slot_tick | -8 / -14 | marks align |
| 306 | tv_lock + sitar_pluck + harmonium_swell | -6 / -12 / -14 | the film starts (band-limited as if from the TV speaker, hp 300 lp 4k) |
| 342 | wind_gust (NEW) | -10 | |
| 348 | glitch_short | -12 | picture tears |
| 423-440 | whoosh_fast @432, card_slide @440 | -3 / -8 | M3 paired cues (`PLAN.cues()`) |
| 432-719 | laptop_fan | -34 | edit-room bed (+ room_tone -36) |
| 468 | notif_ping | -10 | toast (re-hook) |
| 477 | mouse_click + ui_tick | -12 / -16 | 2 px nudge |
| 488, 502 | phone_buzz (NEW: vibration on wood, 0.35 s) | -12 | |
| 490, 504 | bubble_pop | -14 | bubbles |
| 522-567 (8ths) | ui_tick | -16 | X jitter; slot_tick -20 every 3 f for list rows (rate-limited: max 1 per 3 f) |
| 576, 594, 612, 630 | antenna_creak + ui_tick + bubble_pop | -14 / -16 / -16 | split: both eras on the same frame |
| **648** | tv_lock + impact_big | -6 / -10 | client "BAS BAS!" |
| 684-716 | typing (soft) → render_complete @716 | -24 / -10 | export |
| 714-725 | reverse_swell @720, shimmer @720 | -6 / -10 | M2 paired cues |
| 720-1007 | wind_bed (evening) + outdoor_birds (sparse) | -30 / -34 | |
| 738-755 | **drop-out** | | everything off except wind -40 |
| 756 | reverse_cymbal (ends 756) + sub_drop + dhol_hit | -8 / -6 / -8 | payoff |
| 828 | clamp_tick | -20 | the 2° nudge (easter egg) |
| 855-872 | whoosh_fast @864, card_slide @872 | -6 / -10 | M3 paired cues |
| 864-1007 | tv_static (CRT) + room_tone | as S1 | |
| 882-1007 | `card.cues(T_END, DUR)` | per profile_outro | |
| 990 | notif_ping | -14 | bubble B1 |
| 980-1008 | reverse_swell (ends exactly on 1008) | -10 | releases into f0 impact_soft |

Hook B (f0-71): bubble_pop f0, ui_tick f9, notif_ping f30, glitch_short f62, static swell f62-71 into the splice.

## c. UI / TYPE (caption-designer + brand-kit-builder; `ui.py` with `look='gold_hour'`, `jawad_kit` styles)

**House lockups.** Every caption in SCRIPT §3 with its style, px, position and animation (`script.json →
captions[].anim`). Rules: `J.HouseTitle(caps, key, caps_px, key_px, underline=False)` for all near/narrator lockups;
underline only on P1 and the cover (2 of the 3 allowed). Exits 0.12-0.15 s in_cubic + 8 px up + blur 0 → 6. **Ghost
double** (signal grammar): a second draw of the keyword sprite at opacity `0.35·sig`, x offset `40·sig·sign(yaw)` px,
plus a 1-px horizontal slice jitter on 3 random 12-px bands per frame while sig > 0.5; gone when locked. **Far voice:**
`T.render(text, 'jw_caps', px=64)` in ASH, rises y 1480 → 1420 (out_cubic 10 f), 2 echo copies (+10 f and +20 f
delay, 14 px higher each, opacity 0.35 / 0.15), exit in_cubic 5 f. Scrim: where a lockup overlaps the CRT glass or UI,
a SMOKE gradient (0.55, feather 80 px) behind it; contrast ≥ 4.5:1 measured on the finished frame.

**`SUNDAY KI FILM` card (the TV picture, 2D, 1080×810 4:3, warped through A5/A6 `stmap`):** NIGHT_1 → PLUM vertical
gradient, `SUNDAY KI FILM` jw_caps_bold 90 IVORY centred (766 px), thin AMBER rule under it, a desaturated (40 %)
7-bar colour strip 60 px tall at the bottom, slight vignette and 1-px scanlines; on lock a soft AMBER shimmer sweep.
Signal FX: snow mix = sig, ghost copy offset 60·sig px at 0.4 opacity, vertical roll speed 0.6·sig screens/s,
chroma drop (desat) = sig.

**Glass UI (S7, S9, S11; 2.5D plane rot (4°, -6°, 0); `ui.glass_card(..., look='gold_hour')`):**
| element | build | size / position (frame px) | text (style px) |
|---|---|---|---|
| Viewer | `glass_card(960, 600, r=32)`, media slot 912×513 at card (24, 60) via `ui.put_media` | centre (540, 780) | the trailer frame: blurred roof-sunset plate + `SUNDAY KI FILM` jw_caps_bold 58 at viewer centre + X offset × 0.845; readout chip `X 540` (jw_mono 30, card top-right, ≤ x 900); delta flash `-2 px` FLAME jw_mono 30 (6 f) |
| Timeline | `glass_card(960, 360, r=32)` | centre (540, 1290) (y 1110-1470) | ruler `00:12 00:13 …` jw_mono 28 ASH; track T: FLAME clip `SUNDAY KI FILM` jw_mono 28 INK; V1: EMBER clips with tiny roof thumbs; A1: ASH waveform; IVORY playhead 4 px + flame head; all text ≤ x 900 |
| Toast T1 | `ui.toast('Client', 'thoda left...', icon_name='chat', look='gold_hour', w=640)` | drops y 300 → 420 (POP spring) f468, out f483 | title ui_bold 34, sub 38 |
| Cursor | `ui.draw_cursor(..., 'arrow', 64, press, click)` | clicks the X readout f477 | |
| Revision list L1 | glass rows 560×64 r 20 (stack), newest on top with flame rim (`face_at(sweep)`), older rows dim 0.6, max 5 visible | centre x 540, rows y 1150 → 1450 (timeline slid out) | `trailer_v12_final.mp4` jw_mono 30 IVORY + `X 539` jw_mono 26 ASH right; v2 row and v27 row both read `X 538` (easter egg) |
| Version chip | `ui.chip('v2', sel=1, look='gold_hour', size=34)` → v27 | viewer top-left (150, 520) | |
| Client bubble T2 | glass pill 600×120 r 60, left-tail, SMOKE + FLAME hairline | centre (540, 1240) | `Client` ui_bold 30 ASH / `BAS BAS! ab theek hai!` body 38 IVORY (421 px) |
| Export E1 | `glass_card(760, 260, r=28)` | centre (540, 1250) | `Exporting` body 34 ASH; `v27_final_FINAL.mp4` jw_mono 34 IVORY (≈ 370 px); bar 680×14 FLAME → RED; `%` jw_mono 34 right edge x 880 |
| Anachronism bubble B0 / B1 | glass pill 380×96, avatar disc SMOKE with `C` (ui_bold 34) | centre (790, 300) (top band: clear of the right rail rule) | `Client` ui_bold 26 ASH / `thoda left...` body 34 IVORY |

**Phone screen (S8, rendered 2D at 720×1560 and warped via A7 `stmap`):** dark warm chat theme, no app branding:
header (NIGHT_1, 140 px) back arrow icon, avatar disc `C`, `Client` ui_bold 44, `online` body 30 ASH; incoming bubbles
SMOKE r 28 with IVORY body 44 text, outgoing PLUM with IVORY + a drawn double-tick (`ui.icon('check')` ×2, GOLD), time
`4:12` 26 ASH. Thread (top → bottom): in `thoda left...` · out `done` ✓✓ · in **`thoda right...` (pops f490)** · in
**`nahi, pehle wala` (pops f504)** · typing dots (3 × 10 px, 1.4 Hz) from f510. Screen brightness drives the `spill` pass.

**Split S10:** top half y 0-958 = roof day plate + A1 at 0.62 scale (mast axis x 540); bottom half y 962-1920 = viewer
mini `glass_card(840, 472)` centre (540, 1330) with the title + a chat bubble 360×84 centre (600, 1010); divider FLAME
2 px with glow at y 960. Chips `ui.chip('TAB', size=34)` at (150, 290) and `ui.chip('AB', size=34)` at (150, 1010).
Far-voice words in the top half: jw_caps 56 at (540, 860) (`THODA LEFT...` 411 px · `THODA RIGHT...` 464 ·
`NAHI, PEHLE WALA!` 574 · `THODA SA...` 361); the same words in the bubble below on the same frame. Test at 360 px wide.

**Outro:** `PO.ProfileOutro('Aap ke ghar antenna kaun ghumata tha?', key='Papa, bhai ya aap?', dur=4.2)` drawn at
`T_END = 882/30`; its layout is fixed by `profile_outro.py` (pill y 700, question under it, key, FOLLOW button).
Nothing else on screen except B1 (y 300, above the pill) f990-1007.

**Cover (`_cover.jpg`, dedicated still, `TLB_COVER=1`):** CRT macro frame, the screen half snow (top) / half locked
(bottom) split by a rolling tear at y ≈ 1010; lockup `THODA` jw_caps 96 at y 360 + `left...` jw_key 250 at y 540
with the underline; `BAS BAS!` jw_caps_bold 150 (746 px) at y 1500; B0 bubble at (790, 300); `J.signature` at y 1580;
gold_hour finish, no grain boost. **Grid crop (`_cover_grid_3x4.jpg`):** the same still cropped to y 240-1680 (1080×1440):
lockup, TV and BAS BAS! all inside; verify the bubble (y 252-348) and `BAS BAS!` (y 1447-1553) clear the crop edges
by ≥ 12 px; readable at 210 px wide.
