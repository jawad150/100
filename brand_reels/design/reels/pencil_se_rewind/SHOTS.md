# SHOTS · Pencil Se Rewind

v1, 2026-10-11. Grid 112.5 BPM: beat = 16 f, bar = 64 f, DUR = 1024 f (34.133 s). Captions: SCRIPT.md §2 /
`script.json`. Look `ember`; post = `G.tx_finish(cv, t, 'ember', cuts=CUTS, **PLAN.post_kw(t))` (+ D7 at f464).
No humans, no hands: keys press themselves, the pencil turns by itself, the camera and the light do the rest.
Plates = photoreal Blender renders (§A); "2.5D" = `X.zoom_canvas` / `X.shift_canvas` moves on the rendered plate.

## Shot list

| shot | f (s) | picture | camera | out (jawad_tx) | text | SFX (frame) |
|---|---|---|---|---|---|---|
| S1 hook A | 0-63 (0-2.10) | **R1 loop** (idx = f mod 16): hex pencil upright in the left hub of a cassette on a worn desk, turning clockwise one rev per beat; tape slides in the window; lamp pool + FLAME rim. Lit and moving at f0 | 2.5D push 1.00 -> 1.04 (easy_ease, starts at rest = seam from S14) | L3 glue f64, push 0.5 | HA: caps mid-rise f0, `Pencil.` slam f16, exit f56-f63 | ratchet 1x f0; hiss bed; impact_soft f0; hit f16 |
| S1B hook B (trial) | 0-63 | **R4 walkman** with `rew_down` key pass; spools (R4 loop reversed) slow from 4x to 0 over f0-f44 (battery dying); amber LED fades f40-f52 | locked, 2 px jolt f0 | splice f64 (L3 0.5) | HB: caps mid-rise f0, `khatam?` slam f32 | key_down f0, motor_whine slowing f0-f44, tick f48 |
| S2 | 64-127 (2.13-4.23) | **R4** walkman, keys up, orange-foam headphones, two AA cells (one tooth-dented: easter egg) | 2.5D slide x +40 px linear + zoom 1.00 -> 1.03 | L3 f128, 0.25 | L2 upper | room_tone bed |
| S3 | 128-191 (4.27-6.37) | **R1 loop**, crop on the pencil-hub contact (teeth biting the hex) | 2.5D zoom 1.40 -> 1.46 about (560, 1240) | L3 f192, 0.3 | L3 upper | ratchet 1x f128 |
| S4 | 192-255 (6.40-8.50) | **R3** label still, top-down: handwritten "Mix '98 · Side A", scribbled track list; pencil lying lower right | 2.5D pan y -60 -> +60 px (inout_sine) "down the track list", zoom 1.05 | **D8** speed-ramp f256 (window f249-f262) | L4 lower | paper rustle f192; D8 cues |
| S5 | 256-319 (8.53-10.63) | **R1 loop** at a 3x clock (idx = floor(3f) mod 16, 7 samples = spin blur): the fast rewind | 2.5D push 1.00 -> 1.10 + roll 0 -> 2 deg (out_cubic) | hard cut + L3 0.4 f320 | L5 lockup | ratchet 3x f256-f319 |
| S6 | 320-383 (10.67-12.77) | **R4** walkman: keys press themselves: PLAY f320 (spools 1x), STOP f336 (spools stop, PLAY pops), REW f340 (spools reversed 4x, LED on) | locked; 2 px down-jolt per key (impulse, decay 18) | L3 f384, 0.3 | L6 stack f320 / f328 / f336 | key_down f320, music snippet f322-f334, key f336, key + motor f340 |
| S7 | 384-447 (12.80-14.90) | **R4** zoomed into the lid window: the cassette playing through the smoked glass (spools 1x), PLAY down | 2.5D zoom 1.35 -> 1.42 about the window | hard cut + L3 0.5 f448 | L7 slam f384, L8 upper f420 | key_down f384; cassette-tone music |
| S8 **re-hook** | 448-511 (14.93-17.03) | **R4b eat**: f448-f451 frame 0 (spools stall), f452-f457 lid springs open (frames 0-5), f458-f483 tape ribbon spills out in crinkled curls (frames 6-31), f484-f511 hold frame 31 | locked to f463; f464 shake (6 px, decay 10) + D7; 2.5D push 1.00 -> 1.05 + roll 1 deg f464-f511 | hard cut + L3 0.2 f512 | L9: `CASSETTE` f448, `phans gayi!` SLAM f464 (45.3 %) | warble + tape_stop f448-f463, lid_pop f452, crinkle f458, D7 + sub f464 |
| S9 rescue | 512-575 (17.07-19.17) | **R1b** (32 frames, 2-on: idx = (f-512)//2): cassette alone on the desk, the crinkled loop drawn back into the shell as the pencil turns slowly; frame 31 hands on to R1 frame 0 | 2.5D push 1.00 -> 1.06 (easy_ease) | in-scene pull-back from f576 | L10 upper | ratchet 0.5x, crinkle reversed, heartbeat on beats, riser into f576 |
| S10 **reveal** | 576-639 (19.20-21.30) | the frame shrinks into a glass NLE viewer (f576-f597): it was a clip all along. Viewer plays R1 loop at 1x; timeline panel + header slide in f584-f600; playhead crawls 1 px/f | pull-back: world scale 1.0 -> viewer rect (inout_sine 22 f, 7 samples), 9:16 mask tightens to 4:5 | none (continues) | L11 top | whoosh_slow f576, glass_tap f590, music opens up |
| S11 scrub | 640-703 (21.33-23.43) | playhead jumps on 8ths: back f640, fwd f648, back f656, fwd f664 onto a CUT marker; viewer follows the playhead time (back = pencil turning counter-clockwise), stepping at 12 Hz like real scrubbing; timecode follows | locked | none | L12 slams f640 / f648 / f656 / f664 | timeline_scrub x4, ui_click + pop f664 |
| S12 | 704-767 (23.47-25.57) | push into the timeline: viewer slides up and out (f704-f727), timeline scales 1.0 -> 1.9 about the playhead into the payoff layout (settled f744). **Drop-out f752-f767**: the playhead line becomes the pencil (wipe top -> bottom, f752-f767) | 2.5D group scale (inout_cubic 40 f) | hard cut-in-place f768 + L3 0.6 | L13 top, gone by f751 | whoosh_slow f704; silence f752-f767 + reverse_swell into f768 |
| S13 **payoff** | 768-895 (25.60-29.83) | timeline close: V2 / V1 / A1 lanes, the yellow pencil standing in as the playhead (eraser + ferrule = the head in the ruler), snaps from x 520 to the cut at x 600 on f800 (SNAP spring, 2 deg wobble); clips under the tip glow FLAME on contact f800-f816 | 2.5D push 1.00 -> 1.03 | **D2** razor f896 (window f888-f909) | L14 lockup f768; L15 tag f816; exit f880-f895 | PLAY clack + impact + sub f768; tick + pop f800; D2 cues |
| S14 outro | 896-1023 (29.87-34.10) | **R1 loop** on the global clock (idx = f mod 16; 1024 mod 16 = 0, so f1023 -> f0 is continuous), framed exactly as S1 at zoom 1.00, dimmed by the card | locked at 1.00 (S1's push starts from rest) | loop seam -> f0 (`card.post_kw` + `cuts=[(0.0, 0.6)]`) | `PO.ProfileOutro('Aap ki pehli cassette kaunsi thi?', key='Pencil ya pen?', dur=128/30)`, `T_END = 896/30` | ratchet 1x -20; filter closes to cassette tone; reverse_swell ends f1024 |

Rhythm: 2.1 / 2.1 / 2.1 / 2.1 / 2.1 / 2.1 / 2.1 / 2.1 / 2.1 / 2.1 / 2.1 / 2.1 / 4.3 / 4.3 s. Feature transitions:
D8 (f256), D7 (f464, in-scene), D2 (f896); all else L3 glue. `PLAN = X.Plan([('D8', 256/30), ('D2', 896/30)])`.
Frame-0 gate: f0 YAVG >= 35 (limited) and the pencil, hub and keyword readable at 360 px wide.

---------------------------------------------------------------------------------------------------------------

## A. BLENDER PROPS (blender-3d-artist)

Builder `pipeline/jawad_reels/assets3d_pencil_se_rewind.py`, bpy 5.2, Cycles CPU, `threads = 2`, every render
through `tools/heavy.sh`. Output the shared spec: `RWS/assets3d/<name>/passes/0000.png ...` + `meta.json` (written
last), loaded with `S3.Asset3D(name, 'passes', root=RWS + '/assets3d')`. RGBA 8-bit sRGB, view transform Standard,
look None, dither 1.0; expose so the brightest diffuse in the lamp pool sits <= 0.85 (glints may clip; the finish
blooms them). Adaptive sampling 0.02, OIDN with albedo + normal, bounces 6 (transmission 8 for the shell), caustics
off, filter glossy 1.0, motion blur ON for sequences (shutter 0.5), fixed seed. `--preview` = 16 spp, half res.

**Realism brief (Jawad 2026-10-11): every prop photoreal, tied to the story.** Real dimensions, 0.2-0.5 mm bevels on
every edge, PBR materials, surface imperfections (dust, scratches, fingerprints, wear, decals), physically plausible
light, real macro depth of field. A few high-detail hero props shot close beat many simple ones. **No brand marks**
on anything (generic symbols and handwriting only).

### Props (model once, reuse in every render)

| id | real size | build + PBR materials | imperfections |
|---|---|---|---|
| **CASSETTE** (hero) | 100.4 x 63.8 x 12.0 mm; hubs 42 mm apart; window 54 x 14 mm | two shell halves, smoked amber-brown polystyrene (base `#3A2618`, transmission 0.85, IOR 1.59, roughness 0.06 faces / 0.30 ribbed grips); clear PS window; 5 cross-head steel screws (metallic 1, rough 0.3); hubs white POM `#E9E4DA` (SSS 0.03, rough 0.45), ID 8.0 mm with 6 drive teeth; tape packs: oxide `#2B1A10`, anisotropic 0.85 (tangent along the winding), rough 0.22, concentric banding +-8 %, left pack OD 34 mm / right 40 mm; head opening with felt pressure pad on a phosphor-bronze leaf spring, 2 white guide rollers; paper label side A: off-white `#EDE3CF`, fibre bump (0.2 mm noise), generic ruled lines `#E7A27A`, **blue ballpoint `#26306E` handwriting decal "Mix '98" + "Side A" + 6 scribbled track lines** (ink pooling at stroke ends) | micro-scratches on the window (roughness map 0.02-0.12), 2 oily fingerprints, dust specks 0.05-0.2 mm, rust in screw slots, a faint chai-ring stain on the label (8 %), label edge yellowing, mould parting line |
| **PENCIL** (hero) | hex 7.0 mm across flats, 120 mm long (used): body 98, ferrule 9, eraser 5, cone 13 (graphite 2 mm) | chrome-yellow lacquer `#E3A21A` (clearcoat 0.5, rough 0.22), cedar under it `#C4915E` with grain; brushed aluminium ferrule (anisotropic 0.6) with 2 crimp grooves; pink eraser `#D7837C` (rough 0.75) worn at an angle with a graphite smudge; sharpened cone with 5 blade facets (not a perfect cone), end-grain wood, graphite (metallic 0.25, rough 0.35), tip slightly blunted; gold foil "HB" (metallic, rough 0.35), 40 % rubbed off | lacquer chipped along the 6 arrises (wood shows), **4 tooth dents near the ferrule** with cracked lacquer (the chewed school pencil), small ferrule dent, dull oxidation |
| **WALKMAN** | 110 x 80 x 29 mm | generic: black ABS body `#141210` (rough 0.45); brushed-aluminium lid `#B9B4AC` (anisotropic 0.7, rough 0.28) hinged on the left (0-22 deg) with a smoked window 62 x 26 mm showing a CASSETTE instance; 4 piano keys 14 x 9 mm on the top edge (travel 3 mm) with engraved white-filled generic symbols (stop, play, ff, rew); ribbed volume wheel; nickel 3.5 mm jack; 2 mm amber LED (emission `#FFB547`, 6 when on) | edge-wear shine (rough 0.2 mask), scuffs, fingerprints on the lid, dust in the key gaps, worn white fill in the symbols, a blank sticker residue on the lid corner |
| **HEADPHONES** | band span 140 mm, cups 45 mm, pads 50 x 10 mm | thin chrome steel band; black cups; **orange foam pads `#E2581B`** (SSS 0.2, rough 1.0, fine pore displacement); 2 mm matte cable in a loose tangle to the jack | scratched band, one torn pad edge |
| **BATTERIES** x2 | AA 50.5 x 14.5 mm | generic sleeve: matte deep red `#8C1A10` + black band, white "AA 1.5V" only; nickel terminals | one with **3 tooth dents** mid-sleeve (wrinkled sleeve): the easter egg |
| **TAPE_SPILL** | ribbon 3.81 x 0.05 mm (solidify) | curve + bevel, oxide material (front) and glossy back `#1E140D` (rough 0.3); crinkle = noise displacement + an accordion section 30 mm | twist and kinks; one stretched (thinner, lighter) segment |
| **DESK** | top 900 x 600 x 22 mm | sheesham veneer `#4A2A18` with grain, worn clearcoat (rough 0.25 polished / 0.6 worn), wall plane 0.9 m behind (`#2A1C14`, far out of focus) | compass scratches, an old blue ink stain, pink eraser crumbs near the cassette, dust |

**Light rig LAMP (every render):** key = tungsten desk lamp, disc area/spot Ø 12 cm, colour `#FFB46B` (~2900 K), cone
60 deg, blend 0.4, 45 cm above the desk, top-left of frame (off-frame); rim = area 20 x 6 cm FLAME `#FF6A1A`, back-right,
15 cm above the desk (edge lights on shell, pencil, aluminium, foam); fill = World `#120A06` strength 0.35 (warm,
HDRI-like) + a warm bounce card front-right. Everything outside the lamp pool falls toward NIGHT_0. No blue light.

**Cameras.** `CAM_HUB` 100 mm, 36 mm sensor fitted vertically, f/4 focused on the pencil-hub contact, 32 deg above the
desk, 0.30 m from the hub; cassette side A up, long axis yawed 18 deg; left hub at frame (560, 1260), eraser top at
~(575, 820), window toward (800, 1180), right hub soft at the right edge. `CAM_LABEL` 60 mm straight down, f/5.6,
label ~880 px wide centred (540, 900), yawed 6 deg, pencil diagonal lower right (y 1300-1650). `CAM_WALK` 50 mm, 30 deg
above the desk, walkman 3/4 from front-left, ~760 px wide at (540, 1180), key row toward lower left, headphones back
left (pads ~(260, 1000)), batteries lower right (~(820, 1500)). `CAM_PENCIL` orthographic top-down, eraser up.

### Render list (est. on 2 threads; total ~90 min + modelling)

| name | camera | frames / animation | size | spp | labels / meta | est. |
|---|---|---|---|---|---|---|
| `hub_loop` (R1) | CAM_HUB | 16 f: pencil, both hubs and packs turn **clockwise** (rewind, seen on side A) 22.5 deg/f = 1 rev per beat; window tape texture slides to match; f16 == f0 | 1080x1920 opaque | 64 | `loop` x16; meta `hub_xy`, `eraser_xy`, `window_rect`, `pencil_axis` | 20 min |
| `hub_cover` | CAM_HUB | still = hub_loop f0 | 1080x1920 | 192 | `cover` | 4 min |
| `hub_rescue` (R1b) | CAM_HUB | 32 f: pencil 11.25 deg/f clockwise (frame 32 == hub_loop f0); a crinkled tape loop hangs from the head opening toward camera, shrinking 120 mm -> 0 by frame 31; the crinkle section enters the shell around frames 18-26 | 810x1440 opaque (comp upscales 1.333) | 48 | `rescue` x32 | 21 min |
| `label` (R3) | CAM_LABEL | still | 1080x1920 opaque | 128 | `still`; meta `label_rect` | 3 min |
| `walkman_loop` (R4) | CAM_WALK | 8 f: all keys up, spools in the lid window turn 7.5 deg/f (play direction; the comp reverses and speeds it for REW), LED on | 1080x1920 opaque | 64 | `loop` x8; meta `window_rect`, `key_rects`, `led_xy` | 10 min |
| `walkman_keys` | CAM_WALK | stills, cropped to the key-row bbox + 24 px: `play_down`, `rew_down`, `stop_down`, `led_off` | crop | 96 | meta `frame_xy` | 4 min |
| `walkman_eat` (R4b) | CAM_WALK | 32 f, PLAY down: f0-f5 lid springs open 0 -> 26 -> 22 deg (out_back), f6-f31 the ribbon spills from the head opening over the lid lip in 3 crinkled curls onto the desk (bevel end 0 -> 1, crinkle animated) | 810x1440 opaque | 48 | `eat` x32 | 24 min |
| `pencil_top` (R5) | CAM_PENCIL | still + shadow catcher | 600x1700 RGBA (pencil 1500 px long, ~88 px wide) | 96 | `key`, `shadow`; meta `eraser_top`, `tip` | 1 min |

Continuity locks: the same PENCIL in every render (same dents, same "HB" facet); the CASSETTE label reads the same in
R1 (partly), R3 and inside the walkman; R1b frame 31 -> R1 frame 0 seamless; R4b frame 0 == R4 loop frame 0 with PLAY
down. If over budget: drop `hub_cover` (use hub_loop f0) and render `walkman_eat` at 32 spp.

## B. SOUND (sound-designer + music-supervisor)

**Music (original, `pencil_se_rewind_music.py`).** 112.5 BPM, 4/4, 16 bars, circular (bar 15 flows into bar 0).
Instruments: Casio-style home-keyboard lead (an original 2-bar hook, "vibes / piano" preset tone), dusty drum machine
(kick, rim / snare, quiet 16th hats), round finger bass, soft pad. Two characters:
- **Cassette tone** (bars 0-8 and the outro from f896): band-limited 120 Hz-6 kHz, near-mono, tape saturation, wow &
  flutter 0.3 %, hiss.
- **Upgraded tone** (bars 9-13, from the f576 reveal): full range 30 Hz-18 kHz, wide stereo, sub kick, the same hook
  re-voiced on clean e-piano + pluck. The filter opens over f576-f597 with the pull-back, closes again over f896-f927.
Arc: warm playful (0-5) -> mischief (5-6, the "wrong spot" snippet f322-f334 is a mid-phrase jump of the same track) ->
panic (f448-f463 the music itself warbles and tape-stops) -> hush (bar 8: ratchet clicks, filtered pad, heartbeat kick
on beats) -> reveal swell (f576) -> bouncy scrub with stutter edits on the 8ths (bar 10) -> **drop-out f752-f767**
(everything muted but room tone at ~-45 LUFS) -> **payoff hit f768** = the walkman PLAY clack as the downbeat +
impact + sub + full band with the hook resolved -> outro back in cassette tone so f1023 matches f0.
Mix: -14 LUFS integrated, TP <= -1.5 dBTP after AAC (series rule); SFX-only stem for `_songready`; leave a VO pocket
(music -3 dB at 1-4 kHz inside the optional VO windows, SCRIPT §3). Stems 48 kHz 24-bit: music, sfx, (vo).

**New local sounds** (`pencil_se_rewind_sfx.py`, synthesised / foley-modelled, no paid service): `pencil_ratchet`
(16 f loop = 1 rev: 6 soft wood-on-plastic ticks + hub friction whir; rate 0.5-3x), `tape_hiss` (bed),
`walkman_key_down` (two transients 8 ms apart + short spring ring), `walkman_key_up`, `motor_whine` (small DC motor
180-260 Hz + gear grind, speed param), `lid_pop` (spring + plastic knock), `tape_crinkle` (granular cellophane,
reversible), `tape_warble` (wow 4-6 Hz +-6 % on the music stem). From `sfx_jawad`: `jd_tape_stop`, `tape_stop_fx`,
`jd_timeline_scrub`, `jd_reverse_swell`. Catalog: `impact_soft, sub_drop, glitch_short, whip, whoosh_fast,
whoosh_slow, riser, glass_tap, heartbeat, pop, ui_click, ui_tick, card_slide, shimmer, leaf_rustle, room_tone`.

**Cue list (hook A; hit-aligned; dB).**

| f | sound | dB | note |
|---|---|---|---|
| 0 | pencil_ratchet 1x (to f63) | -14 | loop phase = f mod 16 (seam-safe) |
| 0 | tape_hiss bed (f0-f575, f896-f1023) | -40 | circular |
| 0 | room_tone bed (whole reel) | -34 | |
| 0 | impact_soft lp 900 | -10 | release of the f1024 reverse_swell |
| 16 | impact_soft + shimmer hp 5500 | -6 / -14 | `Pencil.` slam |
| 128 | pencil_ratchet 1x (to f191) | -14 | |
| 192 | leaf_rustle (paper) | -18 | label shot |
| 249-262 | D8 cues (`X.TX['D8'].cues`): riser -8 into f256, whoosh_fast -4, impact_soft 0 at f256 | | |
| 256 | pencil_ratchet 3x (to f319) | -10 | the fast rewind |
| 320 | walkman_key_down (PLAY) | -4 | music jumps mid-phrase f322-f334 |
| 328 | impact_soft | -12 | `Galat!` |
| 336 | walkman_key_down (STOP) | -4 | music cut dead |
| 340 | walkman_key_down (REW) + motor_whine fast (to f383) | -6 / -12 | |
| 384 | walkman_key_down (PLAY) | -4 | the right spot: hook melody in cassette tone |
| 420 | music low-pass starts closing + sub swell | | "Aur phir..." |
| 448-463 | tape_warble + jd_tape_stop on the music stem | | the walkman eats it |
| 452 | lid_pop | -6 | |
| 458 | tape_crinkle (0.87 s) | -8 | spill |
| 464 | D7 cues: glitch_short -6, whip -8; + sub_drop -6, impact_soft -2 | | **re-hook** |
| 464-511 | low drone (music), room_tone up to -30 | | |
| 512 | pencil_ratchet 0.5x (to f575) | -10 | |
| 512, 528, 544, 560 | heartbeat | -18 | saans rok ke |
| 530 | tape_crinkle reversed (1.0 s) | -16 | tape drawn back |
| 544 | riser (1.0 s, ends f575) | -12 | into the reveal |
| 576 | whoosh_slow | -10 | pull-back; filter opens |
| 590 | glass_tap | -14 | NLE panels land |
| 640 / 648 / 656 / 664 | jd_timeline_scrub 0.22 s (back / fwd / back / fwd) | -8 | |
| 664 | ui_click + pop pitch 1.2 | 0 / -12 | CUT marker |
| 704 | whoosh_slow | -14 | push into the timeline |
| 752-767 | **drop-out** (all but room_tone -45); jd_reverse_swell 0.53 s ends f768 | -14 | |
| 768 | walkman_key_down (PLAY clack) + impact_soft + sub_drop | 0 / -2 / -10 | **payoff**, full band |
| 800 | ui_tick + pop | -8 / -14 | pencil snaps to the cut |
| 888-909 | D2 cues: ui_click (alt razor_snip) f896, card_slide f898 | 0 / -8 | |
| 896 | pencil_ratchet 1x (to f1023) | -20 | continuous into f0 |
| 896+ | `card.cues(T_END, DUR)` | | profile outro |
| 1000 | jd_reverse_swell 0.8 s, ends exactly f1024 | -12 | loop |

Hook B (f0-f63): walkman_key_down (REW) -4 at f0; motor_whine slowing 1 -> 0 over f0-f44 (-10); `tape_stop_fx` slows
the cassette-tone music over f0-f44; impact_soft -6 at f32 (`khatam?`); ui_tick -18 at f48 (LED dies); splice f64.

## C. UI / TYPE (caption-designer + brand-kit-builder; `ui.py` glass in the `ember` ui look)

**Lockups** (sizes measured with `T.measure`; positions = text-box centres; full table in SCRIPT.md §2):
- HA: caps `REWIND BUTTON?` jw_caps 86 (817 x 60) at (540, 400), house caps rise with t0 = -0.1; key
  `T.Glyphs('Pencil.', 'jw_key', px=250).slam(cv, t, 540, 580, t0=16/30)` (604 x 180), static `T.render` after
  settle; `J.underline(640).draw(cv, 220, 700, u)` f24-f44. HB: `BATTERY` 96 / `khatam?` 240 (776 px), same layout.
- L5 `SIRF` 96 / `andaza.` 220 (761 px); L6 stack `Play.` jw_caps_bold 150 (407 px) y 420 / `Galat!` jw_key 200
  (442 px) y 590 / `Phir se.` jw_caps_bold 150 (606 px) y 760; L7 `Mil gaya!` jw_key 220 (744 px) y 520; L9 `CASSETTE`
  96 (513 px) y 400 / `phans gayi!` jw_key 190 (809 px) y 570; L12 one word at a time at (540, 330): `Peeche.` /
  `Aage.` jw_caps_bold 140 (607 / 447 px), `Yahan.` jw_key 220 (559 px).
- L14 payoff: `J.HouseTitle('PEHLA EDITING TOOL?', 'Pencil.', caps_px=74, key_px=260).draw(cv, t, 540, 560, t0=768/30, out_t0=880/30)`
  (caps 860 x 52 at y 360; key 629 x 187); L15 `Scrubbing toh` / `cassette pe sikhi thi.` jw_body 56 (402 / 578 px)
  at y 772 / 846, `cassette` inline jw_key 96.
- Snake captions: `SC.Captions(words, hide=[lockup windows], clear=PLAN)`; words from `script.json` tokens. Bands:
  upper (y ~390) for S2 / S3 / S7 / S9, lower (y ~1380) for S4, top (y ~330) for S10-S12. `avoid` rects per shot:
  S2 walkman (190, 900, 900, 1560); S3 / S9 hub + pencil (300, 700, 860, 1500); S4 label (100, 520, 980, 1260);
  S10-S12 viewer (220, 430, 860, 1230) + timeline (70, 1260, 1010, 1470).
- All copy inside x 70-1010, y 230-1480; nothing textual right of x 930 in y 1050-1700. Copy within 40 px of an edge:
  none (widest line `phans gayi!` 809 px = 135 px margins).

**Glass NLE (S10-S13; generic, no Adobe / Premiere / DaVinci styling; built like `X._nle_bg` / `X._nle_timeline`):**
- Background: NIGHT_1 -> NIGHT_0 gradient + a 40 px grid at 4 %.
- Viewer: `ui.glass_card(660, 820, r=28, look='ember', rim=0.8)` centred (540, 830); content = R1 4:5 crop (R1 px
  x 0-1080, y 510-1860) fitted to 640 x 800 with `ui.media_fit` + `ui.put_media`; header row inside the card top:
  `cassette_rewind.mov` jw_mono 30 ASH left, timecode jw_mono 34 IVORY right (= the reel's real timecode in S10,
  e.g. `00:00:19:20`; in S11 it follows the scrubbed time).
- Timeline panel: `ui.glass_card(940, 210, r=22, look='ember')` at (540, 1365) (x 70-1010, y 1260-1470). Ruler
  y 1272-1300, ticks every 30 px, labels jw_mono 28 ASH every 120 px (`00:18`, `00:19`, ...). Lanes: `V2` y 1320
  (EMBER clips, 40 px), `V1` y 1372 (FLAME clips, 44 px, thumbnails = tiny R1 frames), `A1` y 1430 (GOLD waveform
  bars); lane labels jw_mono 28 at x 96.
- Playhead: 4 px FLAME line y 1262-1470 with `K.glow(sigmas=(3, 10, 28))`, head = a 22 x 26 px down-pointing pentagon
  with an AMBER core. Scrub moves: inout_expo over 6 f, landing with the SNAP spring.
- CUT marker (f664): `ui.chip('CUT', size=28, h=56, look='ember')` above the ruler at (600, 1235), POP spring, plus a
  dashed AMBER line through the lanes at x 600.
- Payoff layout (S12 push, settled f744): the timeline group scaled 1.9 about (600, 1365) and lifted: ruler y 900-950
  (jw_mono 34), V2 y 1010-1090, V1 y 1120-1220, A1 y 1250-1420; viewer gone by f727.
- Pencil-playhead (R5 `pencil_top`): scaled to a 620 px visible length (~36 px wide), eraser + ferrule as the head
  in the ruler (y ~880-930), tip at y ~1490; `shadow` pass offset (+10, +14) at 35 %. Morph f752-f767: the FLAME line
  narrows 4 -> 0 px (out_cubic) while the pencil wipes in top -> bottom along the same x (mask y 880 -> 1500,
  out_cubic 16 f); snap x 520 -> 600 at f800 (SNAP, 2 deg wobble); clip edges under the tip glow FLAME f800-f816.

**Cover and grid crop.** `_cover.jpg` = `hub_cover` still + HA lockup at full opacity, underline settled, `G.finish`
'ember' (no grain flicker: fixed seed). 3:4 grid crop (y 240-1680): lockup y 340-720 and pencil + hub y 820-1420 both
inside; the keyword reads at 210 px wide. `_cover_grid_3x4.jpg` = that crop.
