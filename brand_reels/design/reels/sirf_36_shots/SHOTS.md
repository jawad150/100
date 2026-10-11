# SHOTS · Bijli series #3 · Sirf 36 Shots (@jawad_mp4)

v1, 2026-10-11 · creative-director. Builds from `BRIEF.md` + `SCRIPT.md` / `script.json`. 36.000 s = 1,080 f, 30 fps,
120 BPM (beat 15 f, bar 60 f), LOOK `noir_ember` (one red-orange practical per shot). No humans, no faces, no Jawad: objects move by themselves, the camera
moves, light changes. Every picture element is a photoreal Blender render (§A) or house type / glass UI (§C).

## 0. Grid
| bar | f | section |
|---|---|---|
| 0 | 0 | HOOK: counter ticks 35 -> 36 (lands f15), flash charges; C1, C2 |
| 1 | 60 | FLASH POP; camera hero; crank rewinds by itself f105 |
| 2 | 120 | (S2 cont.) C1 whip up at f150 into the canister |
| 3 | 180 | canister spin, drops out f225 |
| 4 | 240 | studio counter: day 1 / day 2 (f255) / night + envelope lands (f270) |
| 5-6 | 300 | C6 rack into the envelope; prints fan (f315-f345); thumb print slam f375 |
| 7 | 420 | album; sleeve seals |
| **8** | **480** | **RE-HOOK (44 %): C8 snap zoom, drives, `AUR / aaj?`** |
| 9 | 540 | `2 TB` f540, `4 CAMERAS` f570 (tape labels light up) |
| 10-12 | 600 | media bin: `3,000 TAKES` f600, snap zoom f660, `HAR TAKE dekha` f675, `DISK full` f735 |
| 13 | 780 | **drop-out f780-f809**: freeze, toast + typing dots f795 |
| **13.5** | **810** | **PAYOFF (75 %): `"EK ACHHA SHOT / nahi hai."`** |
| 15 | 900 | C3 portal through the toast avatar into the counter window; `TAB / 36 / KAAFI THE.` f909 |
| 16-17 | 960 | profile outro over the dimmed counter world; seam f1079 -> f0 |

## 1. Shot list
Positions are 1080x1920 px. Transitions are `jawad_tx` ids (default windows: C1 4/4, C6 9/9, C8 4/6, C3 24/8 frames
pre/post). L3 = exposure push on the cut frame via `G.tx_finish(cv, t, LOOK, cuts=CUTS, **PLAN.post_kw(t))`.

| shot | f | picture (3D asset §A) | camera (2.5D on the plate) | text (SCRIPT ids, §C) | out | SFX (§B) |
|---|---|---|---|---|---|---|
| S1 hook | 0-59 | `counter_macro`: top-rear macro of the camera, counter window (540, 1120) Ø ~280 px; `tick` seq f0-f15: thumb wheel turns by itself (4 ratchet steps f0/4/8/11), dial lands **36** on f15; flash-ready LED (250, 1380) dark -> glows f20 and pulses with the charge whine (brightness 0.3 -> 1.0 f20-f58) | locked f0-f15, then slow push 1.00 -> 1.04 (easy_ease) to f59 | C1 `SIRF / ek / PHOTO BACHI.` mid-rise at f0; C2 `SAB / ready / HO JAO!` f45 | hard cut f60 + L3 push 0.9 | wind ratchet + detent f15, flash charge f15-f58 |
| S2 flash | 60-149 | `cam_hero` 3/4 front on a doily: f60 **flash pop** = `flash` pass ×(1.0 -> 0 decay τ 0.12 s) + flash-window `glow` + local bloom (never full frame); f64-f106 flash window faintly re-charges (orange glow ×0.15); f105-f141 the rewind crank (300, 905) spins by itself (`crank` seq, 45°/f) | f60-f70 tiny shake (3 px, decays); drift (2 px, 0.2 Hz) | C3 `HAR / click / GINTI MEIN THA.` f75-f141 | **C1** whip, axis y, sign up, c = f150 | shutter + flash pop f60, recharge whine, crank whirr f105 |
| S3 canister | 150-239 | `canister` `spin` seq over the warm dark void (bokeh from `J.embers`, kept dim; the R_HOME rim is the practical): canister flies up into frame on the whip, spins 2 rev (f150-f224, out_cubic slowdown, 5 samples), leader tongue catches the key light; f225-f239 tips and falls out of frame bottom (in_cubic, +900 px) | follow tilt down f225-f239 (in_cubic 300 px) | C4 `PHIR ROLL / studio / JAATA THA...` f165-f236 | hard cut f240 + L3 0.25 (motion carries the fall) | whip f150, spin swishes, fall whoosh f225 |
| S4 counter | 240-299 | `studio_counter` overhead plate, light state cuts on beats: `day1` f240 (sun shaft + grille shadow from left), `day2` f255 (low warm sun from right), `night` f270 (a single red darkroom safelight from the studio's back door). Canister `lying` lands f240 at (380, 1180) with a 6 px bounce (POP); envelope `closed` drops in f270 at (620, 1210), rot -8°, scale 1.04 -> 1 (SLAM spring) | locked (overhead) | C6 `3 DIN KA / intezaar.` f243-f290; day chip `DIN 1/2/3` f240/255/270 (§C) | **C6** rack-focus hand-off, c = f300 | tin land f240, clock tick f255, safelight switch + paper plap f270 |
| S5 prints | 300-419 | `envelope` close-up overhead (fills 760 px at (540, 1260)); `flap` seq opens f300-f315; prints slide out of the mouth (between `back` and `front` layers) and fan, one per 8th: P1 landscape f315 -> (330, 1130, -12°), P2 silhouettes f323 -> (560, 1100, 4°), P3 cake f330 -> (770, 1170, 14°), negatives strip f338 peeks out (frame numbers 34 35 36); **f375 P4 thumb print slaps on top** at (540, 1230, -3°), scale 1.08 -> 1 (SLAM); contact shadows move with each print | locked; 1.5 % push f375 (impulse) | C7 `AADHI MEIN / aankhein / BAND,` f315-f369; C8 `AADHI MEIN / thumb.` f375-f417 | hard cut f420 + L3 0.3 | flap, 4 print slides, slap f375 (music stops f375-f389) |
| S6 album | 420-479 | `album_page` overhead; P4, P2, P1 already placed (P4 (300, 1110), P2 (770, 1180), P1 (330, 1520)); the PVC `sleeve` slides down over them f430-f450 (out_cubic), its glare streak sweeps diagonally f450-f470 | slow push 1.00 -> 1.03 | C9 `PHIR BHI HAR PHOTO / sambhaali.` f420-f475 | **C8** snap zoom, center (300, 1110) (the thumb print), c = f480 | sticky peel f422, sleeve slide f430 |
| S7 drives | 480-599 | `drives` plate (stack of 4, masking-tape labels CAM A-D); LEDs (`emit`) flicker on 8ths (random per drive, seeded); f540 storage HUD fills 0 -> 2.00 TB (f540-f565, out_cubic); **f570/574/578/582 the labels light up one by one** (CAM A -> D: `labels_mask` × warm local glow +0.8 stop, decays 10 f) | push 1.00 -> 1.06 f480-f599 (easy_ease); 4 px handheld drift | C10 `AUR / aaj?` f486-f536; C11 `2 TB / FOOTAGE,` f540; C12 `4 / CAMERAS,` f570 | hard cut f600 + L3 0.35 | snap + sub drop f480, HDD bed, slams f540/f570, label taps |
| S8 bin | 600-779 | glass **media bin** (§C) over the `drives` plate (blur 18 px, ×0.45): thousands of thumbnails scroll up, speed 0.6 -> 3.0 rows/s (in_quad), 5 samples; take counter `TAKE 0001 -> 3,000` rolls f600-f650; f660 in-scene snap zoom ×1.0 -> 1.5 into the grid (out_expo 6 f); f735 storage bar turns RED, `DISK FULL` chip pops, 2-frame glitch (D7-style rgb split 0.6, impulse) | locked; zoom f660 | C13 `3,000 / TAKES.` f600-f652; C14 `HAR TAKE / dekha.` f675-f727; C15 `DISK / full.` f735-f777 | freeze f780 (no cut) | take ticks, scroll whoosh, snap f660, error f735, riser f750-f779, tape stop f772-f780 |
| S9 payoff | 780-899 | **f780 everything freezes** (bin holds its last frame, LEDs off, grain keeps running); bin dims ×0.45 f780-f795; f795 the glass toast slides up (POP) with avatar circle (540, 1120) and `Client` + typing dots; **f810 dots stop**, toast settles to `Client · abhi`; payoff lockup above it | locked; 1 % push at f810 (impulse) | P `"EK ACHHA SHOT / nahi hai."` f810-f875 | **C3** portal, center (540, 1120), r0 56, c = f900 | silence f780-f809, typing f795, **payoff stack f810 (loudest)** |
| S10 closer | 900-959 | `counter_macro` plate at **35** (tick frame 0) = the frame-0 world; LED glow 0.3 steady; the counter window sits exactly where the avatar was, so the portal opens into it | locked | C16 `TAB / 36 / KAAFI THE.` f909-f957 | outro layer at f960 (no cut) | warm room tone back |
| S11 outro | 960-1079 | same world (static wheel), dimmed by the outro (dim 0.74); f1076-f1079 the wheel starts its first ratchet step, continuing at f0 (`tick` frames read the clock `t - DUR`) | locked; loop push `cuts=[(0.0, 0.6)]` at f0 | `PO.ProfileOutro('Ghar ka pehla camera kaunsa tha?', key='Roll wala ya digital?', dur=4.0)`, T_END = 32.0 | **loop seam f1079 -> f0** | outro cues, reverse swell into f0, ratchet across the seam |
| S1B hook B | 0-59 | `cam_hero` with the flash window `glow` charging (0.1 -> 0.6, pulsing with the whine), lens toward us; f60 = A's flash pop (S2 continues the same shot) | slow push 1.00 -> 1.05 | HB1 `HILNA / mat!` mid-rise f0-f25; HB2 `AANKH MAT / jhapkana.` f27-f70 | none (same shot) | charge whine f0-f58 |

Change audit (<= 2.5 s between visible changes): f0 tick, f15 dial, f20 LED, f45 C2, f60 flash, f75 C3, f105 crank,
f150 whip, f165 C4, f225 fall, f240/255/270 light cuts, f300 rack, f315-f345 prints, f375 slap, f420 album, f430
sleeve, f480 snap, f540/570/600 slams, f660 zoom, f675 C14, f735 error, f780 freeze, f795 toast, f810 payoff, f876
portal, f909 C16, f960 outro, f999 question. Longest gap: f810-f876 (2.2 s, held payoff: intentional).

## 2. Transition plan (module)
```python
PLAN = X.Plan([('C1', 5.0, dict(axis='y', sign=-1)),            # sign: the plates move so the canister rises; check in the C1 test frame
               ('C6', 10.0),
               ('C8', 16.0, dict(center=(300, 1110))),
               ('C3', 30.0, dict(center=(540, 1120), r0=56))])
CUTS = [(0.0, 0.6), (2.0, 0.9), (8.0, 0.25), (14.0, 0.3), (20.0, 0.35), (27.0, 0.25)]   # L3 pushes (loop seam, flash, hard cuts, payoff)
```
Scenes: S1-S2 (one scene function, hard cut f60 inside), S3, S4-S5 split at C6, S5-S6-S7 (hard cut f420 inside;
S7 is B of C8), S7-S8-S9 (hard cut f600 inside), S10-S11. Captions are drawn in `draw()` after the plan and are off
screen inside every window (SCRIPT timings already respect them). Present section (f480-f899):
`G.tx_finish(..., exposure=-0.15)` (noir_ember throughout; LOOK = 'noir_ember').

---------------------------------------------------------------------------------------------------------------

## A. BLENDER PROPS (blender-3d-artist; builder `pipeline/jawad_reels/assets3d_sirf_36_shots.py`)
**Goal: photoreal product-macro realism, not stylised props.** Few hero props, shot close, with real materials, real
dimensions, bevels, wear and macro depth of field. Realism comes from: bevelled edges catching light, roughness
variation (fingerprints, smudges, worn touch points), dust in cavities, printed decals with wear, physically plausible
light (area lights with real colour temperatures, practicals, a real flash), and shallow DOF on the macro plates.

**Render spec (all assets).** bpy 5.2, Cycles CPU, `threads = 2`, every job through `tools/heavy.sh`. Adaptive sampling
threshold 0.015, OpenImageDenoise with albedo + normal guides, fixed seed. Light paths: max 8, diffuse 3, glossy 4,
transmission 8 (lens + magnifier glass), caustics off, filter glossy 0.8, clamp indirect 8. View transform Standard,
look None (house spec: the grade tone-maps); expose so non-emissive highlights stay <= 0.9; flash and LEDs live in
their own passes. Output PNG RGBA 8-bit straight alpha sRGB, `RWS/assets3d/<name>/<pass>/0000.png ...` + `meta.json`
written last (anchors, `frame_xy`, features). Opaque plates = full 1080x1920; sprites cropped to alpha + 24 px.
Real-world units (metres), sensor 36 mm fitted vertically, DOF via the camera's f-stop (baked into plates; sprites are
rendered sharp at f/8 and defocused in comp). Run `--preview` first (16 spp, half res, one contact sheet, Read it),
then finals. Hex below are sRGB (convert with `K.hexlin`). **No brand names, logos or trade dress on any prop.**

**Shared node group `S36_Wear`** (apply to every hard-surface material): (1) edge wear: Bevel-node/pointiness mask ×
noise (scale 400/m) -> lighter base and lower roughness on 0.3-0.8 mm edges; (2) cavity dust: AO (distance 2 mm)
inverted × fine white noise (scale 3000/m, threshold 0.82) -> base #8A8178, roughness 0.95; (3) fingerprints:
procedural ridged ovals (wave rings in a voronoi cell, 2-3 per surface) driving roughness ±0.15 on glossy parts;
(4) micro-scratches: stretched noise (scale 20 × 2000) into roughness and a 0.01 mm normal. Bevel modifier on every
hard edge (0.4-1.0 mm, 3 segments, harden normals). Decals as alpha textures in the base colour with the wear mask
eating 10-20 % of them at edges.

**Light rigs** (colour temperature via Blackbody node)
| rig | lights | used by |
|---|---|---|
| R_HOME | key area 40×40 cm 2700 K, 45° up, camera-left, 1.1 m; fill area 1×1 m 4300 K at 8 % of key, camera-right (window); rim strip 10×60 cm 2000 K behind-right (FLAME-warm edge); 2 practical bulbs (emissive spheres 2700 K) 2.5 m behind for bokeh | counter_macro, cam_hero, canister |
| R_FLASH | area 22×12 mm at the flash window, 5600 K, strength for ≈ +3 stops on the doily; all other lights off | cam_hero `flash` |
| R_COUNTER | `day1`: sun 1.5° angle, 4800 K, elev 35°, from left through a window-grille gobo plane; `day2`: sun 3200 K, elev 14°, from right, longer shadows; `night`: one darkroom safelight (15 W bulb behind a deep-red filter #B3120E, 0.8 m above-right, soft 20 cm) as the only light (noir_ember's single practical); each + a weak 3000 K bounce | studio_counter |
| R_TABLE | area 60×60 cm 3200 K overhead-left 30° off axis + white bounce card right (gives every glossy print one soft specular streak) | envelope, prints, negatives, album_page |
| R_DESK | monitor glow area 60×35 cm 6500 K at 30 %, front-top; desk lamp 2700 K camera-left, low; rim strip 2000 K behind-right; LEDs emissive | drives |

### Assets (dimensions are real; screen sizes for the 1080x1920 frame)
| asset | geometry and real dimensions | materials (PBR) + imperfections | camera | passes / sequence | size, spp |
|---|---|---|---|---|---|
| **counter_macro** (S1, S10, S11, cover) | generic fixed-focus 35 mm camera, body 118×64×38 mm; silver top plate; **counter window Ø 9 mm domed acrylic magnifier** over a black dial disc Ø 16 mm with white numerals 2.2 mm tall (every number 0-36 + "S"), orange index triangle; **thumb wheel Ø 16 × 5 mm, 36 knurl ridges**, protruding 4 mm from a slot at the back-right; flash-ready LED Ø 2.5 mm by the eyepiece; rubber eyepiece; chrome shutter button Ø 9 mm | top plate: metallic paint #B8B2AA, metallic 0.6, rough 0.28, scratches with black ABS showing at edges, one fingerprint smudge; body ABS #0F0D0C rough 0.42 + stipple bump 0.02 mm; wheel ridge tops polished by thumbs (rough 0.22) vs grooves 0.5 + dust; magnifier IOR 1.49, rough 0.03, hairline scratches, dust in the rim; dial print slightly misregistered; LED lens #FF6A1A transmissive | 100 mm macro, f/2.8, focus on the numerals, 35° down from behind-right; window centre on screen (540, 1120) | `plate` (dial at 35, R_HOME); `tick` 16 f (f0-f15): wheel 1 rev in 4 ratchet steps (f0-3, 4-7, 8-10, 11-15) and dial 35 -> 36 with detent settle; border render region x 360-1080, y 880-1400 (same camera, so it drops onto the plate); `led` emission only | plate 1080x1920 128 spp; tick 720x520 ×16 at 96 spp; led 16 spp |
| **cam_hero** (S2, hook B) | the same camera model, front: lens bezel Ø 26 mm (barrel protrudes 8 mm, glass Ø 14 mm), flash window 22×12 mm (clear acrylic over a fresnel prism + aluminium reflector + xenon tube), viewfinder window 12×9 mm, leatherette front panel, **fold-out rewind crank** Ø 14 mm on the top-left, wrist strap (frayed black nylon) trailing onto the doily; on a crochet doily Ø 30 cm on a sheesham table | lens glass thin-film coating 380 nm (amber/violet reflections), black baffles; leatherette #121010 pebbled voronoi bump 0.15 mm rough 0.6; printed generic white legends "35 mm" + "FOCUS FREE" 2 mm, worn; doily cotton #E8DCC4 (radial open-work alpha texture, fibre fuzz via fine noise) ; table #3A2216 satin varnish rough 0.3, scratches + one tea ring | 70 mm, f/4, focus on the lens ring, yaw 30°, 10° above; camera body centre (540, 1180), 760 px wide | `lit` (R_HOME); `flash` (R_FLASH only: window glow + spill on doily/table); `glow` (flash window emission only, orange charge glow for hook B); `crank` 8 f seamless (45°/f), region 320×260 around (300, 905) | 1080x1920: lit 128, flash 64, glow 16; crank 8 × 64 spp |
| **canister** (S3, S4) | 135 cartridge: shell Ø 25 × 44 mm, spool knob +6 mm top (slot), +4 mm bottom, light-trap lip 9 mm with black velvet, film leader tongue 30 mm (translucent grey-brown base #4B3A2E, sprocket holes 2.8×2.0 mm, slight curl) | printed tinplate label: yellow #F2B705 field, black bands top + bottom, large "36", "135-36 · ISO 200" (own generic layout), DX checkerboard (bare steel vs black ink) on the back; varnish coat 0.6 rough 0.15; end caps steel #C9C6C0 metallic, rough 0.22, crimp ring + turning marks; scuffs to bare tin at edges, a small dent by the lip, lint on the velvet | 85 mm, f/8 (sprite), axis tilted 15° to camera | `spin` 16 f = 360° about the long axis, light fixed (label highlights travel); `lying` top-down still (on its side, leader out) + shadow catcher | spin 600x900 ×16 at 64 spp; lying 500x400 64 spp |
| **studio_counter** (S4) | photo-studio counter top 1.2 × 0.7 m: wood-grain laminate, chipped edge banding, a pen groove; a carbon-copy receipt book (no legible text) top-left, a rubber stamp pad bottom-right | laminate #6A4329 rough 0.35 + scratches + 2 faded tea rings; receipt paper #E9E2D2 rough 0.8 with blue carbon smudges; stamp pad tin + violet ink | 100 mm from 2.2 m straight down (near-ortho), f/8 | `day1`, `day2`, `night` (R_COUNTER) | 1080x1920 ×3 at 64 spp |
| **envelope** (S4, S5) | photo-print envelope 130 × 185 mm kraft, flap 45 mm with gum strip, soft dog-ear, two creases | kraft #A8794A rough 0.85, fibre albedo noise + 0.04 mm bump; red-ink printed generic box "PHOTO STUDIO · PRINTS · NEGATIVES · No. ____" (no shop name), handwritten blue ballpoint "36" in the box; gum strip rough 0.35 | top-down as studio_counter | `closed` still; `flap` 6 f (0° -> 180°, paper bend via Simple Deform); `back` (body, open mouth, darker inside) + `front` (front pocket face) so prints slide out between them | 760x1300, 64 spp (9 renders) |
| **prints** (S5, S6) | 5 × 4R glossy prints 102 × 152 × 0.25 mm, 2-3 mm bow (Simple Deform), corners r 1 mm; 1 print back; 1 **negatives** strip 35 × 150 mm (4 frames) | gloss: base rough 0.25 + coat 1.0 rough 0.04, a fingerprint and 1-2 hairline scratches in the coat; image = A7 textures with a lab cast (warm/magenta, blacks lifted to #1A1412), minilab orange 7-segment date stamp `'98 10 11` bottom-right; back #EDE7DC rough 0.7, faint generic grey line pattern (no words); negatives: orange-brown base #B85A28 (transmission 0.3), sprocket holes, edge print "34 35 36" + arrows, inverted silhouettes | top-down, R_TABLE (one soft specular streak per print) | one still each: P1-P5 fronts, back, negatives | prints 720x1080, negatives 300x1100, 64 spp (7 renders) |
| **print_src** (A7, textures for prints) | P1 low hills + Nishita sky (sun 8°, haze), horizon tilted 6°; P2 four smooth faceless mannequin capsules (**no facial features**) against a pale wall, direct flash, motion blur + f/2 defocus -> blurred silhouettes with hard flash shadows ("eyes shut" is the caption's joke, never drawn); P3 round cake Ø 22 cm, cream piping (SSS), 5 lit candles, steel plates, hard flash shadow on the wall; P4 P3's room heavily defocused + a thumb (capsule with nail, SSS skin #C98A6E) 20 mm from the lens covering the top-left 40 %, fully out of focus; P5 dressing-table mirror with a huge flash flare, rest dark | simple materials, realism from light + defocus | 35 mm, as a 90s compact would see it | one still each | 800x1200, 32 spp (5 renders) |
| **album_page** (S6) | magnetic album page 240 × 320 mm, raised adhesive ridges every 3 mm, gold-foil printed border; clear PVC sleeve with 0.2 mm wrinkles and one lifted corner | board #E9DFC8 rough 0.75 + ridge bump; foil metallic #C9A24A rough 0.3, worn; PVC transmission 1, IOR 1.54, rough 0.06 | top-down, R_TABLE | `page` plate (empty, prints are composited); `sleeve` = PVC reflections only (everything else holdout) as RGBA overlay | page 1080x1920 64 spp; sleeve 1080x1920 64 spp |
| **drives** (S7, S8-S9 bg) | stack of 4 portable 2.5" drives, each 120 × 78 × 19 mm, 2 mm rounded edges + 1.5 mm chamfer, USB-C ports, braided cables coiling right; 6 × 1 mm activity LED slit per drive; masking-tape label 60 × 18 mm per drive; stack misaligned 2-4 mm / 1-3° yaw on a walnut desk | sandblasted anodised aluminium #2E2C2A metallic 1, rough 0.38, anisotropic 0.3, chamfers polished (rough 0.15); end caps black ABS; tape #E6D9B5 rough 0.8, torn fibre ends, one corner lifted, hand-lettered black marker "CAM A" ... "CAM D" + "2 TB" (texture from `WS/fonts/Caveat-Bold.ttf`, ink bleed); fingerprints + dust on the top drive; desk #2A1A12 satin with a coffee ring | 60 mm, f/2.0, 12° above the desk, focus on the "CAM B" label; stack fills y 950-1550, monitor glow a soft out-of-focus rectangle at the top | `plate` (R_DESK); `emit` (LEDs only); `labels_mask` (4 frames, one label each, emission 1 spp) for the f570 light-up | 1080x1920: plate 128, emit 16; masks 4 × 1 spp |

**Budget (2 threads, estimate):** counter_macro 25 min (plate 8, tick 16 × ~1 min), cam_hero 20 min, canister 18 min,
studio_counter 12, envelope 12, prints + negatives 10, print_src 6, album 8, drives 12: **≈ 2 h** (≈ 75 renders, most
small sprites). If over budget: tick 12 f (3 ratchet steps), canister spin 12 f, crank 6 f; never drop samples below 64
on the macro plates (the noise reads as fake at macro).

**Done when:** every pass exists with meta.json; a contact sheet of all passes is Read at full and at 360 px; no brand
marks, no faces, no legible receipt text; numerals 35/36 sharp in the tick frames; LED and flash not clipped in their
own passes; plates hold the screen anchors above (±20 px).

---------------------------------------------------------------------------------------------------------------

## B. SOUND (sound-designer + music-supervisor; `sirf_36_shots_sfx.py`, `sirf_36_shots_music.py`)
**Mix targets** (LEAD #1): -14 LUFS integrated ±0.5, TP <= -2.0 dBTP wav (<= -1.5 after AAC), the drop-out audible,
the payoff (f810) the loudest moment. Two masters: `_ig` = music + SFX; `_songready` = SFX only (-18 LUFS stem
normalised to the same peak policy). Everything loop-exact (beds and tails wrap f1079 -> f0, `_add_wrap`). If a VO
is approved later: carve 1-4 kHz -3 dB in the music under each VO window (SCRIPT §3) and keep VO >= 8 LU over the bed.

**Music (original, procedural, 120 BPM, key D minor; chords per bar Dm9 - Bbmaj7 - F/A - C, repeating).**
| f | section | arrangement |
|---|---|---|
| 0-59 | hook | felt upright piano 4-note motif (D-F-A-C) on beats, tape wow 0.3 %, vinyl crackle -40; nothing else (the wheel and the whine own the hook) |
| 60-479 | past | full lo-fi half-time on the flash: soft kick f60n, brushed snare on beat 3 (f60n+30), round upright-style bass, santoor-like plucked shimmer on bar starts, crackle. **Stop f375-f389** (one beat of silence for the thumb joke), back on f390 |
| 480-779 | present | same chords re-voiced cold: filtered synth pulse on 8ths, kick on every beat (full time), closed hats 8ths, filter opens over 5 bars; riser f750-f779 |
| 780-809 | **drop-out** | music off; only room tone + HDD hum at about -45 LUFS |
| 810-899 | **payoff** | piano chord Bbmaj7(9) + sub swell + the velvet hit = momentary max of the reel; then sparse piano + warm pad |
| 900-1079 | closer + outro | the hook motif returns soft (piano + crackle), under the outro; the final bar resolves into the f0 motif (tail wrapped into the head) |

**New local sounds** (numpy, `register()` like `sfx_jawad`; no samples, no downloads): `s36_wind` (thumb-wheel ratchet:
4 dry plastic clicks + spring detent, hit = detent), `s36_flash_charge` (rising xenon whine 1.8 -> 7 kHz with capacitor
hum, hit = end), `s36_flash_pop` (capacitor thump + xenon tick), `s36_rewind` (crank whirr with ratchet grain, 1.2 s),
`s36_tin_land` (tin canister on laminate: clink + short roll), `s36_clock_tick`, `s36_paper_plap` (envelope lands),
`s36_paper_flap`, `s36_print_slide` (glossy paper slide, seeds 0-4), `s36_sticky_peel` (album adhesive crackle),
`s36_hdd` (bed: 5,400 rpm hum + random seek clicks, loopable), `s36_error` (double low buzz). Catalog names used:
`camera_shutter, impact_soft, sub_drop, whip, whoosh_fast, whoosh_slow, air_zoom, glitch_short, ui_click, ui_tick,
ui_hover, glass_tap, card_slide, bar_grow, slot_tick, swish_small, typing, toast_chime, reverse_swell, room_tone,
outdoor_birds` + sfx_jawad `jd_hit_soft, jd_riser, jd_tape_stop, jd_stack_velvet_hit, jd_room_night_home`.

**Cue list** (f = hit frame, `align='hit'`; gains are starting points in dB)
| f | sound | gain | note |
|---|---|---|---|
| 1076 -> 15 | s36_wind | -6 | ratchet clicks f1076 (wrap), f0, f4, f8, f11; detent on f15 when the dial lands 36 |
| 0 | impact_soft (lp 900) | -12 | frame-0 transient |
| 15-58 | s36_flash_charge | -14 | ends f58 |
| 60 | camera_shutter + s36_flash_pop + jd_hit_soft | 0 / -2 / -6 | flash pop; kit enters |
| 64-106 | s36_flash_charge (seed 1) | -26 | the flash recharging after the shot |
| 105 | s36_rewind | -8 | crank spins f105-f141 |
| 150 | whip (C1 auto cue) | -6 | |
| 160, 180, 200 | swish_small | -18 | canister spins |
| 225 | whoosh_fast | -12 | canister falls |
| 240 | s36_tin_land + impact_soft | -2 / -10 | L3 cut; outdoor_birds bed -30 f240-f269 |
| 255 | s36_clock_tick | -12 | day 2 |
| 270 | ui_click (safelight switch, lp 3 kHz) + s36_paper_plap | -14 / -4 | night (safelight on), envelope lands |
| 300 | ui_hover (C6 auto) + s36_paper_flap | -12 / -8 | rack, flap opens |
| 315, 323, 330, 338 | s36_print_slide (seeds 0-3) | -10 | prints fan; f338 negatives (seed 4, -16) |
| 375 | s36_print_slide + impact_soft | -4 / -8 | thumb print slap; music stops f375-f389 |
| 420 | impact_soft + s36_sticky_peel | -10 / -10 | album; peel f422-f445 |
| 430 | card_slide | -12 | sleeve slides |
| 479, 480 | whip (C8 auto), impact_soft, sub_drop, glitch_short, air_zoom | -6 / 0 / -4 / -10 / -8 | **re-hook**; s36_hdd bed -26 starts f480 |
| 540 | jd_hit_soft + ui_click + bar_grow (f540-f565) | -4 / -12 / -14 | 2 TB |
| 570, 574, 578, 582 | jd_hit_soft (f570) + glass_tap | -4 / -16 | labels CAM A-D light up |
| 600 | jd_hit_soft + whoosh_slow | -2 / -18 | 3,000 takes; slot_tick roll f600-f650 at -12 |
| 660 | whoosh_fast | -8 | in-scene snap zoom |
| 735 | s36_error + glitch_short | -6 / -12 | disk full |
| 750-779 | jd_riser (ends f779) | -8 | |
| 772-780 | jd_tape_stop | -8 | the bin freezes on f780 |
| 780-809 | (silence) | | room tone + s36_hdd at -45 LUFS only |
| 795-809 | typing | -18 | typing dots |
| 810 | toast_chime + jd_stack_velvet_hit + music payoff chord | -2 / 0 | **loudest moment** |
| 876-908 | C3 auto cues + air_zoom (hit f900) | -8 | portal into the counter |
| 900 | jd_room_night_home bed | -32 | warm room back, to DUR (wraps) |
| 960 | `card.cues(32.0, 36.0)` | | profile outro pops |
| 1035-1079 | reverse_swell (ends f1080) | -8 | releases into the f0 ratchet |
Max 3 sounds on one instant (f480 stacks 5 short layers: sum them into one bounce before the mix, or drop air_zoom).

---------------------------------------------------------------------------------------------------------------

## C. UI / TYPE (caption-designer + brand-kit-builder; `jawad_kit` styles, `ui.py` with look `'noir_ember'`)
**Lockups** (widths measured with `T.measure`, all <= 940 px; centres x 540). Three-line lockup = caps line centre
y 318, keyword y 520, caps line y 720 (a local helper `lock3()` = `J.HouseTitle(top, key)` + `T.render(bottom,
'jw_caps', px=96)` rising 4 f after the keyword); two-line caps-over-key = `J.HouseTitle(caps, key).draw(cv, t, 540,
520, t0, out_t0)`; key-over-caps slams (C11-C13) = keyword y 470 + `jw_caps_bold` 110 px y 650 via
`T.Glyphs(...).slam(...)`, static `T.render` after 0.6 s. Exits: opacity in_cubic + 8 px up + blur 0 -> 6 over 5 f.
| id | lines (style px: width) | layout | entry |
|---|---|---|---|
| C1 | SIRF caps 96: 215 · *ek* key 240: ~180 · PHOTO BACHI. caps 96: 744 | 3-line | mid-rise at f0 (t0 -0.1 s) |
| C2 | SAB 200 · *ready* 484 · HO JAO! 434 | 3-line | f45 |
| C3 | HAR 211 · *click* 398 · GINTI MEIN THA. 832 | 3-line | f75 |
| C4 | PHIR ROLL 509 · *studio* (220) 495 · JAATA THA... 670 | 3-line | f165 |
| C6 | 3 DIN KA caps 96 · *intezaar.* key 220: 716 | 2-line | f243 |
| C7 | AADHI MEIN 611 · *aankhein* (220) 773 · BAND, 317 | 3-line | f315 |
| C8 | AADHI MEIN 611 · *thumb.* (230) 597 | 2-line, keyword slams with the print (SLAM spring) | f375 |
| C9 | PHIR BHI HAR PHOTO caps 72: 804 · *sambhaali.* key 200: 776 | 2-line | f420 |
| C10 | AUR 209 · *aaj?* key 260: 409 | 2-line | f486 |
| C11 / C12 / C13 | *2 TB* 370 / FOOTAGE, 556 · *4* (280) 116 / CAMERAS, 579 · *3,000* (250) 489 / TAKES. 372 | slams, each replaces the last | f540 / f570 / f600 |
| C14 | HAR TAKE 501 · *dekha.* 579 | 2-line | f675 |
| C15 | DISK 235 · *full.* key 260: 376 | 2-line | f735 |
| P | “EK ACHHA SHOT caps 86: 796 · *nahi hai.”* key 230: 841 | `J.HouseTitle('“EK ACHHA SHOT', 'nahi hai.”', caps_px=86, key_px=230).draw(cv, t, 540, 600, t0=27.0, out_t0=28.8)` (exit done by f875), underline on | f810 |
| C16 | TAB 197 · *36* key 260: 223 · KAAFI THE. 554 | 3-line (same positions as C1: the loop reads as one composition) | f909 |
| HB1 / HB2 | HILNA · *mat!* (260) / AANKH MAT · *jhapkana.* (220) | 2-line | f0 / f27 |
All lockups sit in y 250-800 over dark bokeh, wall or plate shadow (contrast >= 4.5:1; add a feathered NIGHT_0 scrim
at 0.35 behind the lockup if a plate measures brighter than luma 60 there). Nothing textual at x > 930 in y 1050-1700;
bottom 300 px free.

**Glass UI** (all `ui.glass_card(..., look='noir_ember')`, rim hot spot at -55°, comet sweep `(t * 0.35) % 1` on the
active card only):
- **Day chip (S4):** `ui.chip('DIN 1' | 'DIN 2' | 'DIN 3', size=36, h=76, look='noir_ember')` at (540, 820), swaps on
  f240 / f255 / f270 (POP spring), `sel=1` on DIN 3; exits with C6.
- **Storage HUD (S7):** glass card 640 × 140 at (540, 860), f540 in (POP); `STORAGE` jw_mono 34 ASH at left; value
  `0.00 -> 2.00 TB` jw_mono 46 IVORY right-aligned at x 840; bar track x 260-820, y 900, 14 px, SMOKE; fill FLAME ->
  RED gradient, width = value / 2.00, f540-f565 out_cubic. Carries into S8 as the bin's header row.
- **Media bin (S8):** glass card 900 × 760 at (540, 1160) (x 90-990, y 780-1540). Header row (y 820): `MEDIA BIN`
  jw_mono 34 ASH left; `TAKE 3,000` jw_mono 46 right edge x 900 (rolls `0001 -> 3,000` f600-f650 with `slot_tick`,
  in_cubic, then holds); storage bar under it (full, FLAME; turns RED f735 + chip `DISK FULL` `ui.chip(..., sel=1,
  grad=('RED', 'EMBER'))` at (720, 900)). Grid: 7 columns × endless rows of thumbnails 108 × 192 (9:16), gap 12,
  radius 10, via `ui.media_fit` from a pool of 24 thumbs cut from our own renders (prints, canister, drives, counter
  plate crops, each with random exposure/hue ±10 %); every 3rd thumb has a 3 px FLAME "selected" ring; a 6 px FLAME
  playhead line scrubs across the top row. Scroll per S8. No clip-name text (too small at phone size).
- **Toast (S9):** avatar circle Ø 112 at (540, 1120) (SMOKE fill, flame ring 4 px, IVORY initial `C` Poppins
  SemiBold 54), card 760 × 150 at (540, 1236): `Client` ui 40 IVORY + three typing dots (ASH, staggered bounce 0.4 s)
  f795-f809; from f810 `Client · abhi` (ASH 34 for `abhi`). The avatar is C3's portal centre.
- **Frame counter:** the hero counter is the 3D dial (not UI); the UI echoes it only in the take counter (`TAKE`) and the
  day chip (the count device), so the reel has one counter per world.

**Profile outro:** `PO.ProfileOutro('Ghar ka pehla camera kaunsa tha?', key='Roll wala ya digital?', dur=4.0)`,
`card.draw(cv, t, 32.0)`, `card.post_kw(t, 32.0, 36.0)`, `card.cues(32.0, 36.0)`; world behind = S10 counter plate.
Check the question wraps to <= 2 lines at 66 px and the key stays <= 800 px (auto-shrinks).

**Cover** (`JAWAD_S36_COVER=1`, still at t = 0.5 s with overrides): counter `tick` frame 15 (dial 36), LED 1.0,
`J.HouseTitle('SIRF', '36 shots', caps_px=110, key_px=250)` caps 246 px / key 678 px, keyword centre y 590, caps
y ~400, underline ~740. **Grid crop 3:4 (y 240-1680):** lockup y 330-790 and the counter window (y 970-1270) both
inside, keyword in the upper third of the crop; check at 210 px wide (keyword legible, dial "36" readable).
`_cover_grid_3x4.jpg` = the same still cropped y 240-1680.

**SRT:** one cue per lockup from `script.json` `lines[].roman` (sentence case, keyword asterisks removed), times
`t_in`-`t_out`.
