# BRIEF · Reel 1 · C26 · Pehle Wala Hi Theek Tha (v1 se v27 tak)

Production brief for `pehle_wala` (slot 1 of the @jawad_mp4 set). Author: creative-director. Date: 2026-10-08.
Status: **LOCKED for build**. Binding sources: `brand_reels/design/SLATE.md` §0, §2, §3.1, §4, §5 (this brief
resolves every open default there); the Production Packet twin is `packet.yaml` next to this file. Anything that
changes here must change there.

Inputs read for this brief: SLATE.md; panel_viral.md §3-4.1 (C26 card, retention map); panel_production.md §1-2,
§6; transitions_sound_music_bible.md §0-3.6, §4.1-4.9, §6; hooks_retention_captions.md §0-3.5; face_assets.md;
TOOLKIT.md; the live code of `jawad_tx.py`, `endcard.py`, `snake_captions.py`, `jawad_kit.py`, `jawad_grade.py`,
`ui.py`, `type3d.py`, `sprites3d.py`, `epic_music.py`, `epic_sfx.py`, `epic_mix.py`; Jawad's `cinematic-director`
(packet template, World Bible, shot-list template) and `jawad-brand-reels` skill.

**Verified by the creative director before hand-back (all numbers below were measured, not estimated):**
- every on-screen string measured with `T.measure` / `ui.measure` / `ui.chip_size` in its planned style and size;
- a layout proof rendered with the real toolkit (inferno look, `G.finish`, real face cut-outs, real snake captions,
  real `EndCard`) and inspected: `workspace/jawad_reels/pehle_wala/brief_proof/{A_hookA_t0.70, B_v16_t15.60,
  C_v27_t22.60, D_cover_t28.50, E_endcard_t31.60, F_hookB_t0.40, chips}.jpg` (+ `_zones.jpg` overlays). The proof
  uses a placeholder glass and simplified ad states; positions in this brief are the corrected ones;
- the `X.Plan` below builds without window overlap, every SFX name resolves in `audio.names()` after
  `epic_sfx.register()`, `X.check_cues(plan.cues()) == []`;
- the D9 keycap workaround (`keys_y=-2000`) draws nothing (max abs diff 0.0 against the plain scene at a press
  frame; 1.06 with the default keycaps);
- `E.EndCard('US CLIENT KO', 'bhejo', monogram='JD', dur=4.2667)` builds; settled hold 2.057 s (>= 1.5);
- `snake_captions.Captions(..., band='lower', y=1400, avoid=window + tile)` solved every test chunk inside the safe
  zone with no issues (ink y 1302-1474).

---------------------------------------------------------------------------------------------------------------

## 0. One screen

| field | value |
|---|---|
| reel / module | C26 "Pehle Wala Hi Theek Tha (v1 se v27 tak)" · `pehle_wala` (+ `pehle_wala_hookb` for the Trial hook) |
| logline | A beautiful 3-second chai ad gets "bas ek chhota sa change" 26 times. The frame obeys every note literally, version by version, until the client's last message, "Pehle wala hi theek tha.", sends Ctrl+Z ×26 back to v1, which is frame 0. |
| emotion | exasperation, then laughter (core: mischief) |
| look | `inferno` (`jawad_grade`), post = `G.tx_finish` only |
| grid | **112.5 BPM**, 16 f/beat, 64 f/bar (2.1333 s), frame-locked. **DUR = 16 bars = 34.1333 s = 1,024 frames** at 30 fps |
| key | D minor (Sa = D3 146.83 Hz), progression i-VI-III-VII (Dm-Bb-F-C), one chord per bar |
| hook A (public) | v1 ad + pin "Logo thora bara?" + lockup `BAS EK / *chhota sa* / CHANGE`; VO "Bas ek chhota sa change." |
| hook B (Trial) | v27 mess + lockup `*26* / REVISIONS BAAD`; VO "Chhabbees revision baad, client ne kaha..."; D1 scrub lands on the body at the **splice frame 80 (2.667 s)** |
| re-hook | 12.800 s (bar 6, 37.5 %): a new reviewer, Owner ki Mummy (her messages stack line by line) + D7. Second pattern break at 17.067 s (bar 8, 50 %): "Sab kuch thora bara" |
| payoff | **25.600 s (bar 12, 75 %)**: pin "Pehle wala hi theek tha." after a 1-beat drop-out; Ctrl+Z ×26 rewind 26.133-27.733 (D9); v1 restored at 27.733 (bar 13) with `*pehle wala* / HI THEEK THA` |
| end card | 29.8667 s (bar 14, f896), dur 4.2667 s: `endcard.EndCard('US CLIENT KO', 'bhejo', monogram='JD', dur=4.2667)` |
| loop | the payoff world IS frame 0's world (`P(t) = W_core(t - DUR)`); VO "...aur phir client ne bola" ends at DUR - 0.04 s and frame 0 says "Bas ek chhota sa change." |
| transition family | digital / editor: **D9** Ctrl+Z rewind (signature, once), **D7** RGB shock (full twice; quarter-strength "pin tick" on other pins), **D1** scrub (hook B only), **L3** exposure-push glue |
| signature device | the reel under revision (every note obeyed literally on one frame, live version counter, Ctrl+Z ×26 into frame 0) |
| camera law | the camera never moves; the frame under review does all the moving (one slow push of the product plate, 2 % per bar) |
| sound motif | the pin "thock" (`pin_thock`: glass_tap + impact_soft) with a `slot_tick` on every version step |
| bed | original score in `dark_pulse` grammar at 112.5 BPM that clutters with the frame; tape-stops at the Ctrl+Z press; restarts from bar 0's motif on v1. Desi voice: none |
| faces | `street_smirk` (hero: payoff + cover), `street_sunglasses` (v16) in a docked reaction-cam tile, rim look A |
| 3D | one Blender prop: `pw_chai_glass` (cutting-chai glass with chai), 13-frame yaw set |
| send target | the colleague who suffers the same client or boss (or, bravely, the client) |
| cover | frame 855 (28.500 s), rendered with captions off |

---------------------------------------------------------------------------------------------------------------

## 1. Deliverables

| item | spec |
|---|---|
| master | 1080x1920, 30 fps CFR, exactly 1,024 frames (34.1333 s), H.264 High CRF 14 yuv420p bt709, AAC 320k 48 kHz (render.py master) |
| share | H.264 High 2-pass ~22 Mbps, +faststart, AAC 320k, < 100 MB |
| preview | ~7 Mbps, < 30 MB |
| hook B Trial master | frames 0-79 from `pehle_wala_hookb`, frames 80-1023 from the main master (frame-identical from f80), its own mix |
| audio | Version A full mix (VO + SFX + music) and Version B (VO + SFX only) for both hooks; stems `vo`, `sfx`, `music` at mix gains; 48 kHz / 24-bit; -14 LUFS ±0.5, TP <= -2.0 dBTP (wav), <= -1.5 after AAC, LRA 5-9 |
| captions | burned snake captions + `pehle_wala.srt` (Roman Urdu, house spelling) |
| cover | `pehle_wala_cover.jpg` = frame 855 rendered with captions off (env `PW_CAPTIONS=0`) |
| delivery folder | `reel/jawad_reels/` with prefix `jawad` (project.json `deliver`), packaged by delivery-packager |
| paid ads | no (organic + Trial Reel). Organic safe zone applies (§5) |

---------------------------------------------------------------------------------------------------------------

## 2. Brand tokens used (source of truth: `pipeline/jawad_reels/project.json`, `BRAND.md`)

| token | hex | job in this reel |
|---|---|---|
| NIGHT_0 / NIGHT_1 | #070404 / #170A07 | the void and the v1 ad plate (70-85 % of the frame dark) |
| SMOKE / PLUM | #2A1A15 / #4A0E08 | glass UI bodies, "Approved" chip gradient end |
| FLAME | #FF6A1A | rims, client pin ring, logo roundel, flares, steam outline |
| RED / EMBER | #F2312B / #B3120E | inferno haze; EMBER = 50% OFF ribbon, v21 starburst, drop shadows, "Approved" chip start |
| GOLD / AMBER | #FF9F1C / #FFB547 | Mummy's pin ring, glitter border, NEW starburst (v5), CALL NOW pill, sparkles |
| IVORY / ASH | #FFF3E6 / #A8978C | all UI and pin text (IVORY), reviewer names (ASH) |
| INK | #0B0706 | text on GOLD (NEW, CALL NOW) and the logo wordmark during the cream gag |
| cream (parody only) | linear IVORY x 0.8 | the "white background" gag, inside the ad rect only, v6-v12 |

Contrast pairs used (BRAND.md table): IVORY on SMOKE glass 15.3; IVORY on EMBER 6.4 (ribbon, v21 burst, Approved
chip, measured 8.35 on the rendered chip); INK on GOLD/AMBER >= 7.0; EMBER-PLUM keyword on cream (cream gag). Never
IVORY on flat FLAME, never FLAME on IVORY (the cream gag swaps the ad's keyword to EMBER->PLUM for that reason).
Emissive FLAME/RED <= 3x linear (inferno turns lemon/salmon above it).

Fonts: Instrument Serif Italic (`jw_key`, `jw_key_core`, `jw_key_halo`), Poppins (`jw_caps`, `jw_caps_bold`,
`jw_body`, `jw_handle`, ui), JetBrains Mono (`jw_mono`). Parody face (inside the ad only, never brand type):
Caveat Bold, OFL, copied from the animation-studio engine fonts to `<WS>/fonts/pw_parody_fun.ttf` (+ `OFL-Caveat.txt`
next to it) and used as `font='pw_parody_fun'` (a name without "Caveat", because project.json `font_map` remaps the
Caveat family to the serif).

---------------------------------------------------------------------------------------------------------------

## 3. World Bible (cinematic-director, verbatim lines; the packet carries the same strings)

- **Palette:** "near-black warm void #070404, flame orange #FF6A1A, red #F2312B, ivory type #FFF3E6"
- **Light logic:** "Every light is motivated inside the frame: the ember backlight behind the chai glass lights the
  ad; the void is lit only by the inferno fire floor from below and red haze; glass UI catches flame rims from the
  ad's side; JD's reaction tile takes its rim from the ad (screen-right)."
- **Lens set:** "flat orthographic UI plane (no perspective on the player); 85 mm product lens for the chai glass,
  7 degrees above; 35 mm-equivalent webcam bust for the reaction tile"
- **Camera law:** "The camera never moves. The frame under review does all the moving: one slow push-in of the
  product plate, 2 % per bar, that rewinds with Ctrl+Z."
- **Texture line:** "inferno finish: deep red-black toe crush, film grain 0.020 at 1.7 px from the look only,
  halation on emissive edges, highlights roll off to orange"
- **Sound motif:** "the pin thock: a glass tap over a soft impact, and a slot tick on every version step"
- **Recurring symbol:** "the review pin"
- **Forbidden:** keycaps (Ctrl+Z is a `jw_mono` chip only); typing dots (C02's motif); ERROR / unsaved / delete
  dialogs, cursor hesitation (his Yaadein devices); hearts; real review apps, brand logos, currency, prices with a
  currency, phone numbers, URLs, QR codes; a real chai brand; religious decor in the glitter border;
  India-Pakistan cues; anything from Organic Fostering / Floret or the old prop library (heart, house, chat_bubble,
  star_badge, pin_phone, question, logo_mark3d, coins ...); built-in looks neon / amber / airy; K.flash, K.fade,
  post(flash=); full-frame white; the cream outside the ad rect; first-person "main" about Jawad's life; any
  claim about Jawad's real clients.

Cast blocks:
- **JD** (identity source: locked, character-sheet cut-outs `street_smirk`, `street_sunglasses` only; one wardrobe:
  streetwear, black bomber, white tee, chains). Appears only inside the reaction-cam tile with the label
  "JD · editor". No lip-sync, no talking, no morphs, rigid face, display scale 0.40 (<= 1.0).
- **CLIENT** (incidental; never shown): exists only as FLAME-ringed pins with the initial "C" and the name "Client".
  Stays likable: terse, never rude.
- **MUMMY** (incidental; never shown): "Owner ki Mummy", GOLD-ringed pins with the initial "M"; sends her notes as
  separate consecutive messages.

Location block: **REVIEW_PLAYER in the EDIT_VOID**: "a dark-glass review player floating in a red-black edit void;
traffic-light dots top-left, the file name centred in the title bar, the version counter top-right, 'Review · POV'
header with the status chip; the ad under review fills the slot; bokeh and embers drift in the void outside."
Anchors (same positions in every shot): player body x 80-1000, y 236-1268; ad rect x 120-960, y 468-1228; counter
chip top-right of the title bar.

---------------------------------------------------------------------------------------------------------------

## 4. Global craft rules (Standards, copied from the creative-director agent; binding for every agent)

- **Safe zones 1080x1920:** key copy inside x 70-1010, y 230-1480 (a CTA may reach 1600); bottom 300 px free of
  text (nothing below y 1620); never copy at x > 930 for y 1050-1700; the cover crop is 3:4 (y 240-1680).
- **Sizes:** hero >= 130 px; H2 80-120; UI body >= 34-40 px; fine print >= 28 px after perspective (the window
  title "ubaal_chai_ad.mp4" is fine print at 28 px, drawn flat at scale 1.0, never scaled down); tags read in motion
  (filenames) >= 40 px; pins >= 44 px. Contrast >= 4.5:1 (scrim, glass or falloff behind text).
- **Finish:** no full-frame flash or fade; exposure pushes only (`X.finish` / `G.tx_finish`); motion blur never
  crosses a cut (HALF rule); exits ease out >= 0.2 s; animated-to-static type hand-offs continuous; 3 samples by
  default, 5 inside D9, transition policy elsewhere; logo glows never the logo's own colour; particles and bokeh
  stay off type and logos; at most 2 text blocks at once (§5.3); at least 3 depth layers in every frame.
- **Faces:** never cut an eye at a card edge, never cover a face, no copy within 60 px of the face box, faces never
  in the caption band, never under the like column, <= 3.5 s per still pose, halo <= +6 code values.
- **Sound:** -14 LUFS, TP <= -2.0 dBTP, speech >= 8 LU over the bed, <= 3 sounds starting on one instant, nothing
  busy in 1-4 kHz under words (dark `lp` 900-1200 or air `hp` 5000-6000 variants), hero hits in VO gaps.
- **Delivery:** verify duration, fps and frame count with ffprobe; CRF 14 master; 48 kHz/24-bit stems; cover JPG.
- **QA:** two lenses (copy/layout/legibility/safe zones; motion/transitions/finish/audio sync), a skeptical
  verifier per major finding, 5 fps sheets plus every frame within ±0.4 s of each transition, measured numbers.
- **Ops:** heavy jobs only through `pipeline/jawad_reels/tools/heavy.sh` (2-slot semaphore, nice 10, 2 threads);
  Blender `threads = 2`; `render.py --workers 1` while iterating, at most 2 for the master; `draw(t)` pure; static
  sprites in `lru_cache` + `prewarm()`; this reel's workspace under 2 GB; delete intermediates; no commits by
  agents (the lead commits).

---------------------------------------------------------------------------------------------------------------

## 5. Screen geometry (frame px, y down; the camera never moves, so these hold all reel long)

### 5.1 Fixed layout

| element | build | rect / anchor | notes |
|---|---|---|---|
| world | `K.background('inferno', t, bokeh=1.0)` (static cam) + `J.embers(60, seed=26)` behind the player | full frame | embers never over the player or type |
| player | `ui.app_window(w=920, h=1032, look='inferno', title='ubaal_chai_ad.mp4', header='Review · POV', sidebar=False, header_size=52)` drawn with `win.draw(cv, 80, 236, anchor=(0, 0))` | body x 80-1000, y 236-1268 | its `meta['slot']` = (40, 232, 840, 760) = the ad rect |
| ad rect (frame under review) | the ad canvas, rounded mask r 18 | x 120-960, y 468-1228 (840 x 760 = 30.8 % of the frame) | the cream gag never leaves this rect (<= 35 % rule) |
| title (fine print) | built into the window | pill centred at (552, 280), x 350-729, 28 px | |
| version counter | `ui.glass_card(140, 60, r=18, look='inferno', shadow=0.4)` + `T.Counter('jw_mono', prefix='v', decimals=0, px=56)` | centre (908, 280); body x 838-978, y 250-310 | odometer roll 4 f ending on each change frame |
| status chip | `ui.chip(txt, sel, look='inferno', size=34, h=64, pad_x=26, ...)`, right edge at x 960, centre y 404 | "Approved": `sel=1, icon_name='check', grad=('EMBER', 'PLUM')`, body 272 x 64 (x 688-960). "Changes requested": `sel=0`, body 400 x 64 (x 560-960) | header text "Review · POV" spans x 128-472 (52 px, measured 344 px) |
| clock chip | `ui.chip('3:47 AM', sel=0, look='inferno', size=34, h=56, icon_name='clock', pad_x=22)`, body 224 x 56 | centre (836, 512) | 19.200-23.467 only |
| reaction-cam tile | `ui.glass_card(360, 300, r=26, look='inferno', shadow=0.6)` + cut-out clipped to the card | x 70-430, y 980-1280 | the label tab sits on its top edge (next row) |
| tile label | "JD · editor" `jw_mono` 34 px (measured 231 px) in a glass tab 270 x 48 | x 82-352, y 952-1000 | face box stays >= 74 px below the tab |
| hook A lockup | §6.1 | spans y 628-1058 | scrim ellipse (540, 860) radii (520, 330), dim 0.6 |
| payoff lockup | §6.1 | spans y 595-931 | scrim ellipse (540, 740) radii (500, 230), dim 0.55 |
| captions band | `snake_captions`, `band='lower', y=1400` | ink y ~1300-1475, x 70-930 | avoid = player rect always + tile rect while shown |
| Ctrl+Z chip | glass card 410 x 96 r 24 + `T.render('Ctrl+Z ×26', 'jw_mono', px=56)` (346 px) | centre (540, 1388) | 26.133-27.933 (no VO then) |
| version drawer | `ui.glass_card(760, 300, r=24, look='inferno', shadow=0.6)` | centre (540, 1060): x 160-920, y 910-1210 | 21.333-23.467 |
| end card | `endcard.EndCard` defaults: monogram y 560, caps y ~768, key y 930, signature y 1575 | boxes measured: caps 229-851 x 738-798, key 350-730 x 858-1082, monogram 420-660 x 440-680, signature 411-669 x 1563-1587 | plus a local extra multiplicative dim on the player rect during the card (player x0.35 when settled; §16) |

### 5.2 The ad canvas (840 x 760, ad-local = screen - (120, 468))

v1 (the "finished" ad, frame 0 and the payoff) is premium and quiet:
- **plate:** vertical gradient NIGHT_1 (top) to NIGHT_0 (bottom); ember backlight: `K.radial(900, EMBER x0.9)` +
  `K.radial(420, FLAME x0.6)` added at screen (515, 980); contact shadow ellipse 300 x 40 at (515, 1212), 0.6;
  2D floor reflection of the glass (flipped, x0.22, fades out over 140 px).
- **glass:** `pw_chai_glass` sprite, base centre at screen (515, 1210), height 440 px at push 1.00 (top ~770); yaw
  drift `yaw(t) = 5 deg * sin(2 pi t / 8.5333)` (period 4 bars, so yaw(t - DUR) = yaw(t)).
- **steam:** `K.Particles(90, seed=26)` of large soft discs (r 18-46 px, SLATE: steam from K.Particles) plus three
  thin wisp ribbons for shape (pure f(t)), from the rim (515, 790) up to y ~560, IVORY at alpha 0.10-0.35, rising
  60 px/s with a sideways sine drift, clipped to the ad rect, `screen` blend.
- **logo plate "UBAAL CHAI" (fictional mark):** FLAME ring roundel (r 26, 5 px, x1.6 emissive) with three short
  steam strokes inside + wordmark `jw_caps_bold` 38 px IVORY. Sprite 311 x 52; top-left anchor at screen
  (154, 504); roundel centre (180, 530); wordmark x 218-465.
- **keyword *garam*:** `T.render('garam', 'jw_key', px=120)` right-aligned at x 900, centre y 1150 (box x 602-900,
  measured 298 px). Right edge stays <= 914 even with its v11 shadow and <= 922 with the 8 px shake (rule x <= 930).
- **product push:** plate + glass + steam + reflection scale about (515, 990) by
  `z(s) = 1 + 0.02 * max(0, s + 0.4) / 2.1333` for state time s <= 25.6, held after (graphics do not push).
- **frame-0 lock:** the ad's state is a pure function of *state time* `s` (pins, counter, chip, changes) and an
  *ambient clock* `a` (steam, yaw, glitter twinkle, bokeh). Body: `s = a = t`. Payoff and end card:
  `s = a = t - DUR` (negative: v1, "Approved", no pins). Rewind: `s = a = tau`.

### 5.3 Text blocks on screen (never more than 2; UI chrome = title, header, status chip, counter, clock chip, tile label is not counted)

| window (s) | blocks |
|---|---|
| 0-2.667 | pin card + hook lockup (captions hidden) |
| 2.667-12.8 | pin card + captions |
| 12.8-14.933 | Mummy thread + captions |
| 14.933-21.333 | pin card + captions |
| 21.333-23.467 | pin card + version drawer (no VO, so no captions) |
| 23.467-25.6 | captions only (the hovering marker carries no text) |
| 25.6-26.133 | payoff pin card |
| 26.133-27.733 | Ctrl+Z chip + at most one rewinding pin card (or the Mummy thread) |
| 27.733-29.867 | payoff lockup + captions |
| 29.867-34.133 | end card + captions |

---------------------------------------------------------------------------------------------------------------

## 6. Verified copy table (every on-screen string; house spelling of `prior/captions_roman_urdu.srt`)

Status: `verified` = from SLATE §3.1 or designed here as fiction inside a labelled POV skit (no facts about Jawad).
Widths measured with `T.measure` (type3d) / `ui.measure` / `ui.chip_size` (ui).

### 6.1 Lockups and UI

| id | exact text | style, px | measured w (px) | position (centre unless noted) | in / out (frames) | animation | status |
|---|---|---|---|---|---|---|---|
| HA1 | BAS EK | jw_caps 86 | 318 | (540, 658) | in f0 (t0 = -0.100 s) / exit from f67 | `J.HouseTitle('BAS EK', 'chhota sa', caps_px=86, key_px=200).draw(cv, t, 540, 820, t0=-0.1, out_t0=2.2333)`: caps rise 0.6 s out_cubic, key rises per glyph from 0.12 s (readable by f16), underline draws on 0.45-1.15 s | verified (SLATE) |
| HA2 | chhota sa | jw_key 200 | 674 | key centre (540, 820) | as HA1 | as HA1 (no bounce) | verified |
| HA3 | CHANGE | jw_caps 86 | 390 | (540, 1028) | rise 0.250-0.850 s (out_cubic, +28 px, blur 6 -> 0) / exit with HA1 (in_cubic 0.35 s from 2.2333) | local extra line under the HouseTitle underline | verified |
| HB1 | 26 | jw_key 240 | 217 | (540, 760) | hook B only: t0 = -0.1 / exit from 1.6 s (0.35 s) | local key-first lockup (`KeyFirstTitle`, §16) inside hook B's scene A, so it shrinks into the D1 monitor | verified (SLATE §2.1) |
| HB2 | REVISIONS BAAD | jw_caps 86 | 773 | (540, 1003); box y 973-1033 (above y 1050) | rise 0.2-0.8 s | under HB1's underline (underline at y 933, length 274) | verified |
| PO1 | pehle wala | jw_key 210 | 813 | key centre (540, 670); box y 595-745 (above y 1050, as SLATE requires) | rise from f832 (27.733) per glyph, `dur 0.5, stagger 0.025` (settled 28.458) / exit f886-f896 (in_cubic) | `KeyFirstTitle('pehle wala', 'HI THEEK THA', key_px=210, caps_px=86)`; underline `J.underline(918)` draws 27.983-28.483 (inout_cubic) at y 821 | verified (SLATE) |
| PO2 | HI THEEK THA | jw_caps 86 | 616 | (540, 891); box y 861-921 | rise 27.833-28.433 (out_cubic) / exit with PO1 | | verified |
| EC1 | US CLIENT KO | jw_caps 86 | 623 | EndCard caps (box 229-851 x 738-798) | card t0 f896 | `endcard.EndCard` | verified (SLATE) |
| EC2 | bhejo | jw_key 200 | 379 | EndCard key (box 350-730 x 858-1082) | card t0 f896 | `endcard.EndCard` | verified |
| EC3 | JD (monogram) | jw_key_core 126 | ring r 112 | (540, 560) | card t0 + 0.1 s | `endcard.Monogram` | verified |
| SIG | @jawad_mp4 | jw_handle 34 | 258 | (540, 1575) | card t0 + 1.0 s | `J.signature` (via EndCard) | verified |
| UI1 | ubaal_chai_ad.mp4 | ui_medium 28 (window title) | 299 | title pill, y 280 | always | static | verified (SLATE) |
| UI2 | Review · POV | head 52 (window header) | 344 | left x 128, baseline y 418 | always | static | verified (SLATE: "POV" in the header) |
| UI3 | Approved | ui chip 34, check icon | body 272 | right edge 960, y 404 | f0-f11 and f832-f1023 | f12: hard swap to UI4 + POP spring (scale 1.08 -> 1); f832: hard swap back | verified |
| UI4 | Changes requested | ui chip 34 | body 400 | right edge 960, y 404 | f12-f831 | | verified |
| UI5 | v1 ... v27 | jw_mono 56 (T.Counter, prefix 'v') | "v27" 103 | (908, 280) | always | 4-frame odometer roll ending on each change frame; spins back during D9 | verified (SLATE number lock) |
| UI6 | 3:47 AM | ui chip 34 + clock icon | body 224 | (836, 512) | f576 POP in / exit f696-f704 | a story clock, not a claim | verified (SLATE) |
| UI7 | Ctrl+Z ×26 | jw_mono 56 | 346 | (540, 1388) | f784 POP in / exit f832-f838 (in_cubic) | static chip, never keycaps | verified (SLATE) |
| UI8 | JD · editor | jw_mono 34 | 231 | tile tab x 82-352, y 952-1000 | with the tile | | verified (SLATE §3.1; open question 4 defaulted to yes) |
| VS1 | v24_final.mp4 | jw_mono 40 | 322 | drawer row 1, left x 292, y 960 | f640 | drawer slides up 40 px + POP | verified (SLATE) |
| VS2 | v25_FINAL.mp4 | jw_mono 40 | 322 | row 2, y 1022 | f640 | | verified |
| VS3 | v26_final_final.mp4 | jw_mono 40 | 470 | row 3, y 1084 | f656 (row slides in from x +60, 6 f out_cubic) | | verified |
| VS4 | v27_ab_pakka_final.mp4 | jw_mono 40 | 545 | row 4, y 1146 | f672 | | verified |
| RN1 | Client | jw_mono 34, ASH | 126 | pin card name line | with each client card | | verified |
| RN2 | Owner ki Mummy | jw_mono 34, ASH | 294 | Mummy thread card 1 | f384-f448 | | verified (SLATE; "Mummy" default) |

Drawer rows: a 80 x 46 thumbnail (the ad canvas of that version, downscaled and cached per version) at x 212-292
left of each filename.

### 6.2 Ad copy (inside the frame under review; fictional brand "Ubaal Chai")

| id | text | style, px | measured w | anchor | versions | status |
|---|---|---|---|---|---|---|
| AD1 | UBAAL CHAI | jw_caps_bold 38 (INK during the cream gag) | 247 | logo plate top-left (154, 504) | all; scale per §7 | verified (fictional; SLATE: trademark check before posting) |
| AD2 | garam | jw_key 120; v10+ `font='pw_parody_fun'` 130 px; cream gag fill EMBER->PLUM | 298 (parody 285) | right-aligned x 900, y 1150 | all | verified (SLATE) |
| AD3 | NEW | jw_caps_bold 60, INK, on a GOLD 16-point starburst | 147 | starburst centre (810, 800), rot -12 deg | v5+ | verified |
| AD4 | NEW! | jw_caps_bold 52, IVORY, on an EMBER starburst | ~145 | (260, 880), rot +10 deg | v21+ | verified |
| AD5 | 50% OFF | jw_caps_bold 84, IVORY on an EMBER ribbon 460 x 120 r 16 | 383 | (720, 748), rot -8 deg | v17+ | verified (no currency) |
| AD6 | CALL NOW | jw_caps_bold 72, INK on a GOLD pill 470 x 100 r 50 + 2 px IVORY stroke | 404 | (540, 1060) | v20+ | verified (no number) |

### 6.3 Pins (the client's notes: `jw_body` 44 px IVORY on a glass card; the spine of the reel)

Card build: `ui.glass_card(w, h, r=24, look='inferno', shadow=0.5)`, w = max(text, name) + 56, h = 118 (name +
one line), 150 (two lines), 84 (Mummy follow-ups, text only); name line `jw_mono` 34 ASH at top-left inset
(28, 22); text bottom-left inset (28, 26). Marker: 44 px avatar disc NIGHT_1 with a 4 px ring (client FLAME x1.8,
Mummy GOLD x1.6), initial `jw_caps_bold` 26 ("C" / "M"), a 12 px pointer tip at the target point (disc centre =
tip + (0, -34)); no card overlaps its own disc, the counter, the status chip, the active lockup, the tile or the
drawer (checked for all 27 cards); a 2 px FLAME
leader line (alpha 0.6) from the marker to the card's nearest edge. Widths measured (text px at 44 px).

| # | v | land f (t) | reviewer | text | text w | marker tip (screen) | card centre | change (the frame obeys) |
|---|---|---|---|---|---|---|---|---|
| 1 | v2 | 8 (0.267) | Client | Logo thora bara? | 380 | (470, 506) logo top-right | (712, 540) | logo x2 at **f32** (1.067, POP spring 15 f) |
| 2 | v3 | 64 (2.133) | Client | Aur bara. | 208 | (560, 612) logo bottom edge | (760, 540) | logo x3 (POP); wordmark runs off the ad's right edge (clipped) |
| 3 | v4 | 96 (3.200) | Client | Thora left. | 224 | (560, 600) | (300, 680) | logo anchor x -72 px over 6 f (out_cubic); now clipped on the left too |
| 4 | v5 | 128 (4.267) | Client | Thora aur pop karo | 427 | (515, 1000) glass | (440, 880) | ad saturation x1.45 + exposure +0.2 (ad rect only, 6 f inout_sine, persists); GOLD starburst AD3 POPs in at f130 |
| 5 | v6 | 192 (6.400) | Client | Background white kar do, / clean lagega | 570 / 294 | (250, 1120) plate | (450, 980), 2 lines | plate eases to cream over 12 f (f192-f204, inout_sine); garam -> EMBER->PLUM, wordmark -> INK; steam vanishes on cream |
| 6 | v7 | 224 (7.467) | Client | Bhaap nazar nahi aa rahi | 565 | (515, 690) steam | (600, 570) | steam gets a 3 px FLAME cartoon outline (+6 px glow) at alpha 0.15 iso-line; persists |
| 7 | v8 | 256 (8.533) | Client | Music thora energetic | 488 | (540, 800) | (540, 680) | player + ad + markers shake 5 px on every beat from f256 (damped: `A*sin(2 pi 9 dt)*exp(-14 dt)`, dy 0.6x); the music gets drums at the same frame |
| 8 | v9 | 288 (9.600) | Client | Glass thora chamkao | 482 | (600, 980) glass | (430, 860) | 4 `ui.icon('sparkle')` AMBER/IVORY x2 emissive, 90/70/56/48 px at (440, 860), (610, 900), (470, 1080), (590, 1150), spinning 25 deg/s, pulsing 0.8-1.0 at 2 Hz; scale with the glass |
| 9 | v10 | 320 (10.667) | Client | Font fun wala karo | 413 | (700, 1130) garam | (440, 1000) | garam -> parody face 130 px, wobble ±4 deg at 2 Hz |
| 10 | v11 | 352 (11.733) | Client | Har cheez pe shadow daalo | 617 | (810, 800) starburst | (520, 640) | hard drop shadows on every ad graphic: EMBER alpha 0.85, offset (+14, +14), no blur |
| 11 | v12 | 384 (12.800) | Owner ki Mummy | Mujhe pasand nahi aaya. | 569 | (150, 600) | thread card 1: x 180-805, y 560-678 | GOLD glitter border: 320 discs r 3-6 px, 18 px band inset 10 px inside the ad edge, emissive x1.5, per-disc twinkle 3 Hz |
| 12 | v13 | 400 (13.333) | Owner ki Mummy | Background wapas dark karo | 661 | (thread) | card 2: x 180-897, y 686-770 | cream eases back to the dark plate over 12 f (f400-f412); garam and wordmark back to brand fills; the steam outline stays |
| 13 | v14 | 416 (13.867) | Owner ki Mummy | Aur glitter. | 234 | (thread) | card 3: x 180-470, y 778-862 | glitter band 36 px, 640 discs + 12 sparkle stars |
| 14 | v15 | 432 (14.400) | Owner ki Mummy | Logo bhi bara. | 317 | (thread) | card 4: x 180-553, y 870-954 | logo x1.25 (now x3.75) |
| 15 | v16 | 448 (14.933) | Client | Thora cinematic | 367 | (515, 790) glass rim | (640, 640) | letterbox bars 64 px top and bottom inside the ad (8 f out_cubic), two `K.streak` anamorphic flares (FLAME/AMBER, <= 3x) at y 790 and 1140 clipped to the ad, steam speed x0.3 (slow-mo); JD tile in (street_sunglasses) |
| 16 | v17 | 480 (16.000) | Client | Price bhi daal do | 373 | (840, 720) | (640, 560) | 50% OFF ribbon SLAMs in (scale 1.4 -> 1, SLAM spring) |
| 17 | v18 | 496 (16.533) | Client | Bhaap aur zyada | 382 | (515, 690) steam | (680, 900) | steam density x3 + 2 extra wisps, rising to y 480 |
| 18 | v19 | 512 (17.067) | Client | Sab kuch thora bara | 457 | (540, 848) | (560, 600) | every ad element x1.2 about its own anchor (logo top-left, garam right edge, glass base, bursts and banners centres; glitter band width), POP spring |
| 19 | v20 | 544 (18.133) | Client | Call now bhi likho | 392 | (540, 1100) | (540, 940) | CALL NOW pill SLAMs in |
| 20 | v21 | 576 (19.200) | Client | Aur pop. | 188 | (260, 880) | (490, 760) | second starburst AD4 POPs in + ad saturation +10 % |
| 21 | v22 | 592 (19.733) | Client | Logo aur bara. | 323 | (400, 600) logo | (600, 680) | logo x1.2 (now x5.4) |
| 22 | v23 | 608 (20.267) | Client | Shadow kam karo | 405 | (800, 1180) garam shadow | (560, 950) | shadows to alpha 0.42 |
| 23 | v24 | 624 (20.800) | Client | Shadow wapas. | 353 | (800, 1180) | (560, 950) | shadows back to 0.85 |
| 24 | v25 | 640 (21.333) | Client | Aur energetic | 303 | (540, 800) | (540, 640) | shake 8 px (max; 12 px SLATE cap minus garam's margin); second drum layer; version drawer slides in |
| 25 | v26 | 656 (21.867) | Client | Thora left. | 224 | (400, 600) logo | (560, 660) | logo x -72 px |
| 26 | v27 | 672 (22.400) | Client | Thora right. | 258 | (400, 600) logo | (600, 660) | logo x +72 px (back where it was at v25); counter reaches **v27** at f672 (SLATE: by 23.0) |
| - | - | 704-767 | Client | (no text: the last pin hovers, undecided) | - | path `(540 + 180 sin(2 pi 0.45 u), 820 + 90 sin(2 pi 0.7 u))`, u = t - 23.4667; frozen from f752 | - | no version |
| 27 | - | **768 (25.600)** | Client | **Pehle wala hi theek tha.** (56 px) | 672 | (515, 900) glass | (540, 760), card 728 x 114 | no version: triggers Ctrl+Z ×26; **no chroma tick** (clean landing) |

Pin motion (frames relative to the land frame L): marker appears at L-3 at y -48 px and falls (in_cubic) to land
exactly on L, then SLAM squash (1.25 x 0.8 -> 1, 13 f); card POPs from L (scale 0.86 -> 1, POP spring; opacity
0 -> 1 over 3 f inout_sine). A card collapses into its marker from (next L) - 2 to (next L) + 4 (in_cubic, scale
0.5, opacity 0). The Mummy thread cards stack and all collapse together f446-f452. A collapsed marker stays on the
frame as a 14 px dot (FLAME; GOLD for Mummy) that moves with the player: by v27 the frame is littered with 26 dots.
Pin tick: `rgb_split = 0.25 * K.impulse(t, L/30 - 0.02, 20)` on every landing except f384 and f640 (full D7 from
the plan) and f768 (clean).

---------------------------------------------------------------------------------------------------------------

## 7. Beat sheet (frame-exact; bar.beat is 0-based, beat = 16 f, bar = 64 f)

REEL 1 · "Pehle Wala Hi Theek Tha" · BPM 112.5 (16 f/beat, 64 f/bar, locked ✓) · DUR 16 bars = 34.1333 s (1,024 f) ·
key D minor (Sa D3) · arc: escalation ladder -> drop-out -> reveal -> resolve · look `inferno` · family D ·
signature D9 · palette intimate (v1) -> cluttered epic (v8-v27) -> intimate (v1) · desi voice none · audio original
score (Version B for in-app songs) · re-hook @ 6.0 (37.5 %), pattern break @ 8.0 (50 %) · drop-out 11.3-12.0 ·
reveal @ 12.0 · restore @ 13.0.

| # | bar.beat | t (s) | f | picture | transition | SFX (name@align gain, params) | music | VO | caption |
|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.0 | 0.000 | 0 | v1 ad: glass, steam mid-rise, ember backlight, logo, garam; chip Approved; counter v1; HA1 caps already rising (t0 -0.1) | frame-0 push `cuts=[(0.0, 0.6)]` (loop landing) | impact_soft@hit -6 | bar 0 "v1 motif": Dm pad LP 700, soft kick on f0, epiano motif | L1 starts 0.10 | hidden 0-2.667 |
| 2 | 0.0+½ | 0.267 | 8 | pin 1 lands on the logo; card "Logo thora bara?" | pin tick | pin_thock_dark@hit -6 (lp 1100) | | L1 | |
| 3 | 0.0+¾ | 0.400 | 12 | chip swaps Approved -> Changes requested (POP) | | ui_click@hit -10 (hp 4000) | | L1 | |
| 4 | 0.1 | 0.533 | 16 | lockup readable (key glyphs rising from 0.12 s); underline draws 0.45-1.15 | | shimmer@hit -10 (hp 5500) | | L1 | |
| 5 | 0.2 | 1.067 | 32 | v2: logo x2 (POP); counter v2 | | pop@hit -10 (lp 1100), slot_tick@hit -12 (n=3, dur=0.133) | epiano note | L1 ends 1.90 | |
| 6 | 1.0 | 2.133 | 64 | pin 2 "Aur bara." + logo x3; counter v3 | pin tick | pin_thock@hit 0, slot_tick -12, whoosh_fast@hit -8 | bar 1: Bb pad + hats 8ths -9 | gap | |
| 7 | 1.0+3/16 | 2.233 | 67 | hook lockup + scrim exit (in_cubic 0.35 s, gone f78) | | | | | |
| 8 | 1.1 | 2.667 | 80 | **splice frame**: everything identical in hook A and B from here | | | | L2 2.75-4.15 "Theek hai. Ho jayega." | on |
| 9 | 1.2 | 3.200 | 96 | pin 3 "Thora left."; logo slides -72 | pin tick | pin_thock_dark -6, slot_tick -12, swish_small -10 (lp 1100) | | L2 | |
| 10 | 2.0 | 4.267 | 128 | pin 4 "Thora aur pop karo": saturation spike, GOLD NEW burst at f130 | **L3** push 0.5 | pin_thock 0, flash_hit -4 (L3), pop -6 @4.333 (pitch to D) | bar 2: F; + string ostinato 16ths LP 1100 | L3 4.40-6.30 "Pop karo. Matlab? Kisi ko nahi pata." | on |
| 11 | 3.0 | 6.400 | 192 | pin 5 (2 lines): cream fills the ad rect (12 f); dark inks | pin tick | pin_thock 0, downlifter -10, slot_tick -12 | bar 3: C; hats out ("clean" bar), pad LP 1300 | L4 6.60-7.00 "Clean." | |
| 12 | 3.2 | 7.467 | 224 | pin 6 "Bhaap nazar nahi aa rahi": steam outline | pin tick | pin_thock 0, toggle_on -10, slot_tick -12 | taiko 16th fill 7.467 -> 8.533 | gap | |
| 13 | 4.0 | 8.533 | 256 | pin 7 "Music thora energetic": 5 px beat shake starts | pin tick | pin_thock 0, impact_soft -6, slot_tick -12 | **bar 4: drums in** (kick 1 & 3, clap on 4&, hats 8ths); Dm | L5 8.65-9.25 "Energetic." | |
| 14 | 4.2 | 9.600 | 288 | pin 8 "Glass thora chamkao": 4 sparkles | pin tick | pin_thock 0, sparkle -6, slot_tick -12 | | gap | |
| 15 | 5.0 | 10.667 | 320 | pin 9 "Font fun wala karo": parody garam wobbles | pin tick | pin_thock 0, bubble_pop -6, slot_tick -12 | bar 5: Bb; + 808 | L6 10.80-11.10 "Fun." | |
| 16 | 5.2 | 11.733 | 352 | pin 10 "Har cheez pe shadow daalo": drop shadows | pin tick | pin_thock 0, card_slide -8, slot_tick -12 | | gap | |
| 17 | 6.0 | 12.800 | 384 | **RE-HOOK**: Mummy's GOLD pin; thread card 1 "Mujhe pasand nahi aaya."; glitter border | **D7** full | pin_thock_mummy 0, glitch_short -6 + whip -8 (D7 pair), slot_tick -12 | bar 6: F; drums + 808 out for 2 beats, shimmer layer | L7 12.90-14.75 "Ab Mummy bhi review karengi." | on |
| 18 | 6.1 | 13.333 | 400 | thread card 2: cream back to dark | pin tick | pin_thock_mummy_dark -6, whoosh_slow -12 (lp 1000), slot_tick -14 | | L7 | |
| 19 | 6.2 | 13.867 | 416 | thread card 3: glitter x2 | pin tick | pin_thock_mummy_dark -6, shimmer -12 (hp 5500), slot_tick -14 | drums + 808 back | L7 | |
| 20 | 6.3 | 14.400 | 432 | thread card 4: logo x1.25 | pin tick | pin_thock_mummy_dark -6, pop -12 (lp 1100), slot_tick -14 | 1-beat taiko fill | L7 ends 14.75 | |
| 21 | 7.0 | 14.933 | 448 | pin 15 "Thora cinematic": letterbox, flares, slow-mo steam; **tile in: street_sunglasses** | **L3** push 0.6 | pin_thock 0, braam@hit -4 (dur 2.0, root 36.71), flash_hit -6 (L3) | bar 7: C; half-time "cinematic" bar (kick on 1, clap on 3), strings an octave down | L8 15.05-16.10 "Cinematic. Bilkul." | |
| 22 | 7.2 | 16.000 | 480 | pin 16 "Price bhi daal do": 50% OFF SLAM | pin tick | pin_thock_dark -6, card_slide -8 (lp 1100), slot_tick -12 | | L8 | |
| 23 | 7.3 | 16.533 | 496 | pin 17 "Bhaap aur zyada": steam x3 | pin tick | pin_thock 0, whoosh_slow -10, slot_tick -12 | | gap | |
| 24 | 7.3+⅜ | 16.733 | 502 | tile exit (10 f, in_cubic, y +24) | | | | | |
| 25 | 8.0 | 17.067 | 512 | pin 18 "Sab kuch thora bara": every element x1.2 (the 50 % pattern break) | **L3** push 0.4 | pin_thock 0, air_zoom -6, flash_hit -8 (L3) | bar 8: Dm; full time, +2 dB, strings 8ve up, trailer_hit on 1 & 3 | gap | |
| 26 | 8.2 | 18.133 | 544 | pin 19 "Call now bhi likho": CALL NOW SLAM | pin tick | pin_thock 0, card_slide -4, slot_tick -12 | | gap | |
| 27 | 9.0 | 19.200 | 576 | pin 20 "Aur pop.": burst 2; clock chip "3:47 AM" | pin tick | pin_thock 0, pop -8, clock_tick@hit -16 (n=8, bpm=225) | bar 9: Bb; + hats 16ths | L9 "Aur ek." 19.25 | |
| 28 | 9.1 | 19.733 | 592 | pin 21 "Logo aur bara." | pin tick | pin_thock 0, whoosh_fast -10, slot_tick -14 | | "Aur ek." 19.78 | |
| 29 | 9.2 | 20.267 | 608 | pin 22 "Shadow kam karo" | pin tick | pin_thock 0, swish_small -12 (pan -0.3), slot_tick -14 | | "Aur ek." 20.31-20.75 | |
| 30 | 9.3 | 20.800 | 624 | pin 23 "Shadow wapas." | pin tick | pin_thock 0, swish_small -12 (pan +0.3), slot_tick -14 | | gap | |
| 31 | 10.0 | 21.333 | 640 | pin 24 "Aur energetic": 8 px shake; version drawer in (rows v24, v25) | **D7** full | pin_thock 0, glitch_short -6 + whip -8 (D7), card_slide -8 @21.400, shepard_riser@hit -10 ending 23.467 (duration 2.067) | bar 10: F; peak clutter, second drum layer | gap (no VO 20.75-23.50) | |
| 32 | 10.1 | 21.867 | 656 | pin 25 "Thora left."; row v26 | pin tick | pin_thock 0, slot_tick -12, card_slide -14 | | | |
| 33 | 10.2 | 22.400 | 672 | pin 26 "Thora right."; row v27; **counter v27** | pin tick | pin_thock 0, slot_tick -12, card_slide -14 | | | |
| 34 | 10.3+½ | 23.200 | 696 | drawer + clock chip exit (8 f in_cubic, y +40) | | | | | |
| 35 | 11.0 | 23.467 | 704 | the last pin hovers, undecided; shake fades to 0 by 24.0 | | ui_hover -12 (hp 5000), heartbeat_build@hit -8 (lp 1200) ending 25.067 (duration 1.6, bpm0 70, bpm1 140) | bar 11: C; drums out, shepard ends | L10 23.50-24.95 "Phir aakhri message aaya." | on |
| 36 | 11.1 | 24.000 | 720 | hover continues | | | strings out | L10 | |
| 37 | 11.2 | 24.533 | 736 | hover continues | | | 808 out (pad only) | L10 | |
| 38 | 11.3 | 25.067 | 752 | **DROP-OUT**: marker freezes, steam x0.2, push continues (~1 %/s) | | true silence 8 f (f752-f759) | music, SFX bed gated (4 ms) | none | |
| 39 | 11.3+½ | 25.333 | 760 | held breath | | clock_tick@hit -14 (n=1); bed back at -40 | | | |
| 40 | 12.0 | **25.600** | **768** | **PAYOFF**: marker slams on the glass; card "Pehle wala hi theek tha." | **L3** push 1.0 | pin_thock_big 0, sub_drop -4 (lp 120, dur 1.6), flash_hit -3 (L3) = **loudest moment** | bar 12: Dm; full clutter for 1 beat | none | |
| 41 | 12.1 | 26.133 | 784 | Ctrl+Z press: "Ctrl+Z ×26" chip POPs; world still live 6 f | **D9** t0 (pre 48, post 2) | typing@hit -6 (n=2, cps=8) (D9) | `tape_stop_fx(music, 26.133, 0.4)`, silent after | none | |
| 42 | 12.1+⅜ | 26.333 | 790 | rewind: `W_core(tau)` accelerating back v27 -> v2, desat 30 %, zoom blur 0.02, counter spinning down, pins un-landing | D9 | tape_rewind (custom) -6 (lp 3000) 26.333-27.733; ui_tick -14 (hp 4000) at each of the 26 version crossings | silent | none | |
| 43 | 13.0 | **27.733** | **832** | **RESTORE**: v1 pristine (= frame-0 world), chip Approved, counter v1; PO1 rises per glyph; Ctrl+Z chip exits | D9 cut + push 0.6 | impact_soft 0 (D9), glass_tap -8 (pitch 0.546 -> D6 1174.7 Hz) | bar 13 = score bar 0 (Dm, v1 motif, warm chord) | gap | |
| 44 | 13.0+¼ | 27.867 | 836 | **tile in: street_smirk** | | | | | |
| 45 | 13.0-13.1 | 27.833-28.483 | 835-854 | PO2 rises; underline draws 27.983-28.483 | | swish_small@start -12 (hp 5000) @27.983; shimmer -10 (hp 5500) @28.20 | | L11 28.05-31.00 "Har editor jaanta hai: v1 hi final hota hai." | on |
| 46 | 13.1+7/16 | 28.500 | 855 | **cover frame** (all settled) | | | | L11 | |
| 47 | 13.3+⅜ | 29.533 | 886 | payoff lockup + tile exit (10 f, in_cubic) | | | | L11 | |
| 48 | 14.0 | 29.867 | 896 | **END CARD** t0 over the v1 world (+ player dim) | | endcard.cues: swish_small@start -12 @29.967, shimmer -10 @30.437, glass_tap -12 @30.617 | bar 14 = score bar 1 (Bb, hats -12) | L11 ends 31.00 | on |
| 49 | 15.0 | 32.000 | 960 | card settled (31.717-33.773, hold 2.057 s) | | | bar 15 = score bar 3 (C, VII) turnaround into Dm | L12 32.55-34.05 "...aur phir client ne bola" | on |
| 50 | 15.3+5/16 | 33.773 | 1013 | card exit + caption fade (to f1023) + loop push rising | `card.post_kw` | reverse_swell@hit -8 (duration 0.8) ending 34.1333 | | L12 tail ends <= 34.093 | fading |
| 51 | 16.0 | 34.133 | 1024 = f0 | loops to frame 0 | frame-0 push | impact_soft at t=0 | -> bar 0 Dm downbeat | -> L1 at 0.10 | |

### 7.1 Hook A, frame by frame (0-80)

| frames | what the viewer gets | channel |
|---|---|---|
| f0 | a premium chai ad in a dark review player, "Approved", v1; steam moving, bokeh drifting, glass yaw drifting, product push already running (started at -0.4 s); caps "BAS EK" beginning to rise; impact_soft + Dm downbeat. Works as a still with sound off (frame-0 rules: motion running, no black, no fade, a transient on f0) | picture + sound |
| f3 | VO "Bas..." starts (0.10 s, <= 0.30 rule) | voice |
| f5-f8 | the client marker falls; lands on the logo at f8 (thock, dark variant under the word) + chroma tick; card "Logo thora bara?" pops | text 1 |
| f12 | chip flips to "Changes requested" (rewatch trigger: the client approved v1 first) | UI |
| f4-f16 | key glyphs rise; lockup readable by f16 (0.533 s, beat 1) | text 2 |
| f32 | logo swells x2 on beat 2; counter v2 with its tick | escalation |
| f57 | spoken hook done by ~1.90 s (5 words, <= 7, lands before 2.7 s) | voice |
| f64 | pin "Aur bara." on bar 1; logo x3; counter v3 (open loop: the counter is now a clock) | escalation |
| f67-f78 | lockup and scrim exit (gone by 2.6 s) | |
| f80 | splice frame | |

### 7.2 Hook B (Trial), frame by frame (`pehle_wala_hookb.py`, frames 0-79 only)

| frames | picture | sound / VO |
|---|---|---|
| f0-f39 | scene A = `W_core` frozen at state 23.0 (v27: logo x5.4, two bursts, 50% OFF, CALL NOW, glitter, shadows, letterbox, flares, counter v27, chip Changes requested), ambient clock live; HB lockup over a **focus panel**: inside a feathered rect x 120-960, y 640-1120 (Gaussian feather sigma 24) the picture is replaced by itself blurred (sigma 18 px) x 0.08 linear, ramping in over f0-f8 (inout_sine) so f0 shows the raw mess; a plain multiplicative dim is not enough here (proof: white ad text still read through a 0.95 linear dim; blur + 0.08 hides it, `brief_proof/F4_hookB_crop.jpg`); key "26" rises from t0 -0.1, caps at 0.2, underline 0.35-1.05; exit from 1.6 s, the panel ramps out with it | glitch_short@hit -4 + trailer_hit -6 at f0; shimmer -10 (hp 5500) at 0.40; VO "Chhabbees revision baad, client ne kaha..." 0.10-2.30 |
| f40-f79 | **D1** scrub `X.TX['D1']` (pre 30, post 10), cut c = f70 (2.3333): pull into the generic NLE over 10 f; the monitor shows scene A at state `s(src) = 23.0 - (src - 1.6667) * 19.8` (the mess un-clutters at 12 Hz), then scene B = `W_core(t)` (the body world WITHOUT hook A's lockup and scrim) at 1.333-2.333 (v2 -> v3), SNAP onto the marker at f70, push in, full frame at f80. Scene A = `W_core(s=sA(t), a=t)` with `sA = 23.0` for t <= 1.6667, else `23.0 - (t - 1.6667) * 19.8`; the focus panel and HB lockup are drawn inside A | D1 cues: timeline_scrub@start -8 (duration 0.667, speed 2.5) replacing slider_drag (bible "scrub"), ui_tick -12 @2.0, ui_click 0 @2.333, impact_soft -4 @2.667; music dropped out under the scrub |
| f80 | splice: the body (identical to hook A) | VO L2 at 2.75 |

Hook B loop note: its last frame is the v1 world, its frame 0 is the v27 mess. That is intended (Trial variant;
the seamless loop is hook A's).

### 7.3 Loop bridge (last 1.5 s)

- Picture: the payoff world is `W_core(t - DUR)`, so the world under the end card at f1023 is exactly one frame
  before frame 0 (same steam, yaw, bokeh, push start at -0.4 s). No crossfade needed; `E.loop_world` is not used.
- Type: the end card exits over the last 0.36 s (`EndCard` internal), the captions fade with the same in_cubic
  ramp (`cap.draw(cv, t, opacity=1 - K.ramp(t, 33.7733, 34.1, 'in_cubic'))`), the extra player dim fades with the
  card; frame 0 starts with HA1 caps rising.
- Light: `card.post_kw(t, 29.8667, 34.1333)` pushes into the last frame; frame 0 carries `cuts=[(0.0, 0.6)]`.
- Audio: L12 "...aur phir client ne bola" ends at word end + 40 ms <= 34.093, rising, no final cadence; the score
  bar 15 (C) resolves into frame 0's Dm downbeat; `reverse_swell` ends exactly at 34.1333; frame 0's
  `impact_soft` lands. No fade to black or silence.
- QA: `E.seam_report(lambda t: render.render_still(mod, t, 1), DUR)`; render `--stills 0,34.1` and flip.

---------------------------------------------------------------------------------------------------------------

## 8. Transitions (catalogue ids from the bible §3; code from `jawad_tx.py`)

| id | name | where (cut c) | frames | call | sfx (automatic `plan.cues()`) | notes |
|---|---|---|---|---|---|---|
| L3 | exposure-push flash frame (glue) | 4.2667 (f128), 14.9333 (f448), 17.0667 (f512), 25.6 (f768) | 0 + 4 | `('L3', c, dict(push_gain=g))`, g = 0.5 / 0.6 / 0.4 / 1.0 | flash_hit 0 (re-gained in §11) | A = B = the world (a push on a change, not a scene change) |
| D7 | RGB-split chroma shock | 12.8 (f384), 21.3333 (f640) | 0 + 3 | `('D7', c)` | glitch_short -6, whip -8 | full strength twice only (bible §6.5); other pins get the quarter-strength pin tick in `post` |
| D9 ✂ | undo / Ctrl+Z rewind (signature) | **27.7333 (f832)**; press at 26.1333 (f784) | **48 + 2** (window f784-f833) | `('D9', 27.7333, dict(pre=48, post=2, press=6, R=26.1333, keys_y=-2000.0))`, scenes A = `W_core` (state = tau), B = `P` (payoff world) | typing(n=2, cps=8) -6 @26.1333; reverse_swell (dur 1.4, lp 3000, alt tape_rewind) -6 ending 27.7333 -> **replaced** by the custom tape_rewind (§11); impact_soft 0 @27.7333 | `_tx_undo`: tau = 26.1333 - 26.1333 * in_cubic(u), u over 26.3333 -> 27.7333; desat 30 %, zoom blur 0.02; samples 5; push 0.6 at the restore. 48 f is longer than the bible's 18-30: SLATE locks 1.6 s for 26 versions. `keys_y=-2000` hides the built-in keycaps (verified); the reel draws UI7 instead |
| D1 ✂ | timeline playhead scrub | hook B only: 2.3333 (f70) | 30 + 10 (f40-f79) | `X.Plan([('D1', 70/30, dict(pre=30, post=10))])` in `pehle_wala_hookb.py` | slider_drag -> swapped for timeline_scrub (§11), ui_tick, ui_click, impact_soft | body world from f80 |

Plan for `pehle_wala.py` (verified: windows f128-132, f384-387, f448-452, f512-516, f640-643, f768-772, f784-834,
no overlap):

```python
import jawad_kit                                  # FIRST
from jawad_kit import K, T, ui, F, S3, SFX, J
import jawad_grade as G                           # registers 'inferno' (K.background KeyError without it)
import jawad_tx as X
GR = X.Grid(112.5)
PLAN = X.Plan([('L3', GR.at(2), dict(push_gain=0.5)), ('D7', GR.at(6)), ('L3', GR.at(7), dict(push_gain=0.6)),
               ('L3', GR.at(8), dict(push_gain=0.4)), ('D7', GR.at(10)), ('L3', GR.at(12), dict(push_gain=1.0)),
               ('D9', GR.at(13), dict(pre=48, post=2, press=6, R=GR.at(12, 1), keys_y=-2000.0))])
SCENES = [W, W, W, W, W, W, W_core_rewind_source, P]   # 7 transitions -> 8 scenes (W for the cut-only ones)
```

Budget check: features = D7, D7, D9 (hook A) and D1, D7, D7, D9 (hook B) <= 4; premium ★ = 0; spacing D1 (f40-79)
-> D7 f384 -> D7 f640 -> D9 f784: every gap > 2 bars (128 f). One family (D) + L3 glue. Luma flips <= 2 per second.

---------------------------------------------------------------------------------------------------------------

## 9. VO beat plan (Vlad, `elevenlabs_v4`, Devanagari text; recipe `vo_config.json`; narrator "har editor", never "main")

Target words: **49** (hook A track); hard cap per line sums to **60**, inside the playbook's 80-90 ceiling for 34 s.
Reason for the lower count: the dialogue lives in 27 pins (88 words of pin text). The comedy is read; the narrator
only deadpans. Measured Vlad rate 2.6-2.75 words/s (stretched to ~160 wpm by `vo_chain`).

| id | window (s) | Roman Urdu draft (house spelling) | meaning | words / max | the on-screen moment it explains |
|---|---|---|---|---|---|
| L1 | 0.10-1.90 | Bas ek chhota sa change. | Just one small change. | 5 / 7 | the pin + lockup (hook A); ends < 2.7 s |
| L1B | 0.10-2.30 | Chhabbees revision baad, client ne kaha... | After twenty-six revisions, the client said... | 5 / 7 | hook B: the v27 mess + "26 REVISIONS BAAD" |
| L2 | 2.75-4.15 | Theek hai. Ho jayega. | OK. It'll be done. | 4 / 5 | v3 logo x3, v4 slides left (the editor complies). Starts after f80 so both hooks share it |
| L3 | 4.40-6.30 | Pop karo. Matlab? Kisi ko nahi pata. | Make it pop. Meaning? Nobody knows. | 7 / 8 | v5: the editor's guess (saturation + NEW burst) |
| L4 | 6.60-7.00 | Clean. | Clean. | 1 / 2 | v6: cream background kills the cinematic look |
| L5 | 8.65-9.25 | Energetic. | Energetic. | 1 / 2 | v8: the player shakes, drums kick in |
| L6 | 10.80-11.10 | Fun. | Fun. | 1 / 2 | v10: parody font |
| L7 | 12.90-14.75 | Ab Mummy bhi review karengi. | Now Mummy reviews too. | 5 / 6 | v12-v15: Mummy's message thread |
| L8 | 15.05-16.10 | Cinematic. Bilkul. | Cinematic. Absolutely. | 2 / 3 | v16: letterbox, flares, sunglasses JD |
| L9 | 19.25-20.75 | Aur ek. Aur ek. Aur ek. | One more. One more. One more. | 6 / 6 | v21-v23: each "Aur ek" onset 2-3 f after a pin (19.25, 19.78, 20.31) |
| L10 | 23.50-24.95 | Phir aakhri message aaya. | Then the last message came. | 4 / 5 | the hovering, undecided pin |
| L11 | 28.05-31.00 | Har editor jaanta hai: v1 hi final hota hai. | Every editor knows: v1 is the final one. | 8 / 9 | v1 restored, "Approved", `pehle wala HI THEEK THA` |
| L12 | 32.55-34.05 | ...aur phir client ne bola | ...and then the client said | 5 / 5 | end card; completes into L1 at frame 0 (rising, no cadence, cut at word end + 40 ms <= 34.093). SLATE's 32.3-33.8 shifted +0.25 s so no pause sits on the loop (hooks §3.3); captions fade with the card (§7.3) |

Rules: VO onset 0.10 s; hero hits stay in VO gaps (f768 payoff, f832 restore, f448 braam all in gaps); no VO in
25.067-28.05 (drop-out, payoff read, rewind). Spoken numbers: "chhabbees" (hook B only), "v1" spoken
वी वन. Pronunciation test before the full run (about 2.5 credits a take): छब्बीस, मम्मी, सिनेमैटिक, एनर्जेटिक,
वी वन, फ़ाइनल. Generate per line or per 2-3 lines (L9 as one take, then each "Aur ek" placed on its pin);
budget for this reel about 10 credits plus re-takes. Process every take with
`nice -n 10 python3 -I vo_chain.py process <take> --dev dev.txt --rom rom.txt` and assemble reel-timed tracks:
`<WS>/pehle_wala/vo/pehle_wala_vo_A.wav` + `pehle_wala_vo_A.words.json` (hook A) and `..._B.*` (hook B), times in
reel seconds.

---------------------------------------------------------------------------------------------------------------

## 10. Captions plan (`snake_captions.py`, inside the module, after the transitions, before post)

```python
import snake_captions as SC
TILE = (70, 952, 430, 1280)                         # tile + label tab
def cap_avoid(t):
    r = [(80, 236, 1000, 1268)]                     # never over the player (pins, ad, UI)
    if 14.9 <= t < 17.1 or 27.8 <= t < 29.9:
        r.append(TILE)
    if 26.1 <= t < 27.95:
        r.append((335, 1340, 745, 1436))            # Ctrl+Z chip (no VO then anyway)
    return r
CAP = SC.Captions(WS + '/pehle_wala/vo/pehle_wala_vo_A.words.json', band='lower', y=1400, avoid=cap_avoid,
                  hide=[(0.0, 2.6667)])             # hook lockup shows the same words
# draw: CAP.draw(cv, t, opacity=1 - K.ramp(t, 33.7733, 34.1, 'in_cubic'))   (loop-safe exit, §7.3)
# env PW_CAPTIONS=0 skips captions (cover render)
```

| VO | chunks (target; the solver may merge) | keyword per chunk (`*word` in the Roman token track) |
|---|---|---|
| L2 | Theek hai / Ho jayega | Theek / jayega |
| L3 | Pop karo / Matlab? / Kisi ko nahi pata | Pop / Matlab? / pata |
| L4 L5 L6 | Clean / Energetic / Fun | each word (a lone keyword is allowed) |
| L7 | Ab Mummy bhi / review karengi | Mummy / review |
| L8 | Cinematic / Bilkul | Cinematic / Bilkul |
| L9 | Aur ek (x3) | ek |
| L10 | Phir aakhri / message aaya | aakhri / message |
| L11 | Har editor / jaanta hai / v1 hi / final hota hai | editor / jaanta / v1 / final |
| L12 | ...aur phir / client ne bola... | (none) / client |

Hook B track: hide 0-2.6667 as well. QA: `CAP.check() == []`, `CAP.report()` all ok, `CAP.save_srt(...)`; no chunk
ink inside the player rect or the tile rect while it shows; house spelling (hai, nahi, theek, thora, bara, mein,
bohat). Measured in the proof: chunks sit at ink y 1302-1474, x 198-821.

---------------------------------------------------------------------------------------------------------------

## 11. SFX cue list (`pehle_wala_sfx.py`; build the mix itself, render with `--no-sfx-build --audio`)

Custom sounds registered in `pehle_wala_sfx.py` (audio.py and epic_sfx.py stay untouched; call
`epic_sfx.register()` first):

| name | recipe | hit | level |
|---|---|---|---|
| `pin_thock` | `glass_tap(pitch=1.0926)` (f0 ~2350 Hz = D7) at -8 dB + `impact_soft` at 0 dB, transients aligned (glass leads by 2 ms), `lp` 6000 | 0.006 | 0 |
| `pin_thock_dark` | `pin_thock` with lp 1100 (for landings inside VO words) | 0.006 | -6 |
| `pin_thock_mummy` | `glass_tap(pitch=0.8186)` (~1760 Hz = A6, the fifth) -8 + `impact_soft` 0 + `sub_drop(dur=0.6)` -14 lp 120 | 0.006 | 0 |
| `pin_thock_mummy_dark` | `pin_thock_mummy` with lp 1100 | 0.006 | -6 |
| `pin_thock_big` | `glass_tap(pitch=0.5463)` (~1175 Hz = D6) -6 + `impact_big` 0 | 0.006 | 0 |
| `tape_rewind` (processing) | granular OLA of the reel's own music + SFX mix (not the VO): 25 ms Hann grains every 8 ms, read position = tau(t) of D9 (`tau = 26.1333 - 26.1333 * in_cubic((t - 26.3333) / 1.4)`), grains reversed, rate = abs(d tau / dt), LP 3000, -6 dB, 26.3333-27.7333 | end 27.7333 | -6 |

Pitches are measured with the bible's `f0_of`/`pitch_to` (§4.2) and must land within ±30 cents of D or A. Fallback
if `tape_rewind` fails QA: `vinyl_rewind(dur=1.4)` ending 27.7333 at -8.

Cue rules: the pin landings and counter ticks are listed in the beat sheet (§7, column SFX) and are binding;
in table form for the builder:

| t (s) | cues |
|---|---|
| 0.000 | impact_soft -6 |
| 0.267 | pin_thock_dark -6 |
| 0.400 | ui_click -10 hp 4000 |
| 0.533 | shimmer -10 hp 5500 |
| 1.067 | pop -10 lp 1100 · slot_tick@hit -12 (n=3, dur=0.133) |
| 2.133 | pin_thock 0 · slot_tick -12 · whoosh_fast -8 |
| 3.200 | pin_thock_dark -6 · slot_tick -12 · swish_small -10 lp 1100 |
| 4.267 | pin_thock 0 · flash_hit -4 (L3) · slot_tick -12 · pop -6 @4.333 |
| 6.400 | pin_thock 0 · downlifter -10 · slot_tick -12 |
| 7.467 | pin_thock 0 · toggle_on -10 · slot_tick -12 |
| 8.533 | pin_thock 0 · impact_soft -6 · slot_tick -12 |
| 9.600 | pin_thock 0 · sparkle -6 · slot_tick -12 |
| 10.667 | pin_thock 0 · bubble_pop -6 · slot_tick -12 |
| 11.733 | pin_thock 0 · card_slide -8 · slot_tick -12 |
| 12.800 | pin_thock_mummy 0 · glitch_short -6 · whip -8 (direction 1) · slot_tick -12 |
| 13.333 | pin_thock_mummy_dark -6 · whoosh_slow -12 lp 1000 · slot_tick -14 |
| 13.867 | pin_thock_mummy_dark -6 · shimmer -12 hp 5500 · slot_tick -14 |
| 14.400 | pin_thock_mummy_dark -6 · pop -12 lp 1100 · slot_tick -14 |
| 14.933 | pin_thock 0 · braam -4 (dur 2.0, root 36.71) · flash_hit -6 (L3) · slot_tick -12 |
| 16.000 | pin_thock_dark -6 · card_slide -8 lp 1100 · slot_tick -12 |
| 16.533 | pin_thock 0 · whoosh_slow -10 · slot_tick -12 |
| 17.067 | pin_thock 0 · air_zoom -6 · flash_hit -8 (L3) · slot_tick -12 |
| 18.133 | pin_thock 0 · card_slide -4 · slot_tick -12 |
| 19.200 | pin_thock 0 · pop -8 · clock_tick -16 (n=8, bpm=225) · slot_tick -14 |
| 19.733 / 20.267 / 20.800 | pin_thock 0 · whoosh_fast -10 / swish_small -12 pan -0.3 / swish_small -12 pan +0.3 · slot_tick -14 |
| 21.333 | pin_thock 0 · glitch_short -6 · whip -8 · slot_tick -12 · card_slide -8 @21.400 · shepard_riser -10 (duration 2.067) ending 23.467 |
| 21.867 / 22.400 | pin_thock 0 · slot_tick -12 · card_slide -14 |
| 23.467 | ui_hover -12 hp 5000 · heartbeat_build -8 lp 1200 (duration 1.6, bpm0 70, bpm1 140) ending 25.067 |
| 25.067-25.333 | true silence (SFX bed list window gain -60, fade 0.004) |
| 25.333 | clock_tick -14 (n=1) · bed -40 to 25.6 |
| 25.600 | pin_thock_big 0 · sub_drop -4 lp 120 (dur 1.6) · flash_hit -3 (L3) |
| 26.133 | typing -6 (n=2, cps=8) |
| 26.333-27.733 | tape_rewind -6 · 26 x ui_tick -14 hp 4000 at the tau crossings of each change frame (merge ticks closer than 25 ms) |
| 27.733 | impact_soft 0 · glass_tap -8 (pitch 0.5463) |
| 27.983 | swish_small@start -12 hp 5000 |
| 28.200 | shimmer -10 hp 5500 |
| 29.867 + | `card.cues(29.8667, 34.1333)` (swish_small, shimmer, glass_tap, reverse_swell ending at DUR) |

Notes: `slot_tick` lands on the change frame (`align='hit'`, n=3, dur=0.133); a `slot_tick` starts 4 f before its
instant, so no instant has more than 3 starts (checked per row). Bed: `BED = [{'name': 'edit_suite', 't0': 0,
't1': 25.067, 'gain_db': -32}, {'name': 'edit_suite', 't0': 25.067, 't1': 25.333, 'gain_db': -60, 'fade': 0.004},
{'name': 'edit_suite', 't0': 25.333, 't1': 25.6, 'gain_db': -40, 'fade': 0.004}, {'name': 'edit_suite', 't0': 25.6,
't1': 34.1333, 'gain_db': -32, 'fade': 0.05}]`. Hook B head cues (0-2.667): glitch_short -4, trailer_hit -6 at
0.0; shimmer -10 at 0.40; timeline_scrub@start -8 (duration 0.667, speed 2.5) at 1.6667; ui_tick -12 at 2.0;
ui_click 0 at 2.3333; impact_soft -4 at 2.6667. SFX stem -18 LUFS, TP <= -2.0.

---------------------------------------------------------------------------------------------------------------

## 12. Music plan (`pehle_wala_music.py`, original, `epic_music` instruments as a library)

Do **not** call `EM.render('dark_pulse', ...)` as is (its arrangement, `_common_fx` hits and 1.2 s end fade break the
version-by-version build and the loop). Compose with its building blocks (`Song`, `pad_chord`, `string_note`,
`epiano`, `kick`, `clap`, `hat`, `bass808`, `A.sound('trailer_hit')`, `epic_sfx.tape_stop_fx`), D minor, 112.5 BPM,
`Song(dur=34.1333, bpm=112.5, key='D')`, stems drums / bass / harmony / lead / fx, no end fade.

| bar | t (s) | chord | layers (the music clutters with the frame) |
|---|---|---|---|
| 0 | 0.000 | Dm | v1 motif: pad LP 700, epiano motif (dark_pulse `motif`), soft kick on f0 |
| 1 | 2.133 | Bb | + hats 8ths -9 |
| 2 | 4.267 | F | + string ostinato 16ths LP 1100 |
| 3 | 6.400 | C | hats out ("clean"), pad LP 1300; taiko 16th fill 7.467 -> 8.533 |
| 4 | 8.533 | Dm | **drums in on the "energetic" pin**: kick 1 & 3, clap on 4&, hats 8ths |
| 5 | 10.667 | Bb | + 808 |
| 6 | 12.800 | F | drums + 808 out for 2 beats (Mummy enters), shimmer pad layer; back at 13.867; taiko fill on beat 3 |
| 7 | 14.933 | C | half-time "cinematic" bar: kick on 1, clap on 3, strings an octave down (braam is SFX) |
| 8 | 17.067 | Dm | full time, +2 dB, strings octave up, trailer_hit on 1 & 3 |
| 9 | 19.200 | Bb | + hats 16ths |
| 10 | 21.333 | F | peak clutter: second drum layer (16th kick fill on beat 4) |
| 11 | 23.467 | C | thinning: drums out 23.467, strings out 24.0, 808 out 24.533, pad only; **gate 25.067-25.600** (fade 4 ms after reverbs) |
| 12 | 25.600 | Dm | the full clutter for one beat (all layers): the reveal's first full bar |
| 12.1 | 26.133 | - | `tape_stop_fx(music, 26.1333, 0.4)` on every stem: the music literally undoes; silent through the rewind |
| 13 | 27.733 | Dm | restart = score bar 0 (v1 motif) + a clean warm Dm chord |
| 14 | 29.867 | Bb | score bar 1 (hats -12) under the end card |
| 15 | 32.000 | C | score bar 3 material as the turnaround (VII), resolving into frame 0's Dm downbeat |

Hook B music: bars 0-0.5 (0-1.333) = the bar-10 clutter; gated with a 0.3 s tail fade by 1.633; silent under the
scrub; the body music gated in at 2.6667 with a 10 ms fade-in (identical to hook A after 2.677 s).
Outputs: `<WS>/pehle_wala/audio/pehle_wala_music_A.wav`, `..._B.wav` (+ stems), -18 LUFS alone, beat grid check
(`EM.beatgrid`) tempo 112.5 ±0.2, phase ±15 ms. Mix with `epic_mix.mix_reel('pehle_wala_A', dur=34.1333,
vo=..._vo_A.wav, sfx=..._sfx_A_stem.wav, music=..._music_A.wav, out_dir=<WS>/pehle_wala/audio, vo_offset=0.0)` (VO
files are already reel-timed) and the same for B; Version B = VO + SFX only. Audio name on Instagram: "Original audio
· Bas ek chhota sa change · @jawad_mp4".

---------------------------------------------------------------------------------------------------------------

## 13. 3D prop spec (blender-3d-artist)

| field | value |
|---|---|
| builder | new `pipeline/jawad_reels/assets3d_pehle_wala.py` (the lead's per-reel file naming; SLATE §3.1 said `assets3d_jawad.py`) (imports `assets3d_hero as H`, `assets3d_icons as I` helpers; own token table; CLI `pw_chai_glass [--preview] [--samples N]`, `sheet`, `selftest`); never edit another builder |
| asset | `pw_chai_glass`: a cutting-chai glass (small fluted tumbler, 12 shallow vertical facets, height 9.0 cm, rim diameter 6.6 cm, base diameter 5.2 cm, base 1.2 cm thick, wall 3.5 mm, slight rim flare) filled 78 % with milky chai, a thin cream foam ring at the surface, a small meniscus; no saucer, no table, no ground plane |
| materials | glass: Principled BSDF transmission 1.0, IOR 1.50, roughness 0.04, base colour #FFF1E2 (barely warm); chai: base colour #A0582A (sRGB), roughness 0.25, subsurface weight 0.3, radius (1.0, 0.5, 0.25) cm; foam ring #D9A06A roughness 0.6. Film transparent with transparent glass (`film_transparent_glass = True`) so the 2D plate shows through the walls |
| lighting (night/inferno) | key: soft area card top-left-front, 3200 K, ratio 1.0; fill: front-right card at 0.15; rims: two emissive cards behind, left FLAME #FF6A1A and right RED #F2312B at ratio 2.5 (they draw the glass edges and backlight the chai); a soft top strip for the lip highlight; world #170A07 at 0.02. Lights out of glossy rays (cards only) |
| camera | 85 mm, 7 degrees above the rim plane (the chai surface reads as an ellipse), yaw 0 front; one fixed camera for all frames; the glass fills ~80 % of the frame height |
| frames | mode `yaw`, **13 frames, yaw -6 ... +6 deg (1 deg step)**, `yaw_range [-6, 6]` in meta.json |
| resolution | 960 x 1280 RGBA 8-bit straight alpha, sRGB, view transform Standard, look None |
| render | Cycles CPU, `threads = 2`, 64 samples adaptive + OpenImageDenoise (albedo + normal), fixed seed, `use_animated_seed = False`; preview first (`--preview`: frames 0, 6, 12 at half size, 16 samples) |
| output | `<WS>/pehle_wala/assets3d/pw_chai_glass/inferno_yaw/0000.png ... 0012.png` + `meta.json` LAST (anchor = base centre feature `base`, features `rim` (rim centre), `surface` (chai surface centre)) |
| load | `S3.Asset3D('pw_chai_glass', 'inferno', mode='yaw', root='/home/user/100/workspace/jawad_reels/pehle_wala/assets3d')`, `.at_yaw(yaw(t), interp='flow')` |
| on-screen size | 440 px tall at push 1.00, up to ~660 px (push 1.245 x v19 1.2); 1280 px render covers 2x |
| budget | about 2-3 min per frame on 2 threads: 26-40 min; queue after C11's props (SLATE §4.2); check `df -h` first |
| verify | 13 PNGs + meta.json; uint8 4 channels; composite over the v1 plate at 440 px and over cream at v6 and read both; contact sheet |

Everything else in the ad (logo plate, starbursts, ribbon, pill, glitter, sparkles, steam, shadows) is 2D in the
module (palette only; never `chat_bubble`, `star_badge` or any old prop).

---------------------------------------------------------------------------------------------------------------

## 14. Face plan (face-compositor writes `pipeline/jawad_reels/pehle_wala_faces.py`)

```python
FACES = [
  dict(t0=14.9333, t1=17.0667, pose='street_sunglasses', look='A', tile=(70, 980, 430, 1280), scale=0.40,
       eye_mid_tile=(190, 160), rim_dir=(0.8, -0.5), enter=('POP', 6), exit=('in_cubic', 10, 'y+24'),
       note='v16 "Thora cinematic": JD puts on the sunglasses face'),
  dict(t0=27.8667, t1=29.8667, pose='street_smirk', look='A', tile=(70, 980, 430, 1280), scale=0.40,
       eye_mid_tile=(190, 160), rim_dir=(0.8, -0.5), enter=('POP', 6), exit=('in_cubic', 10, 'y+24'),
       note='v1 restored: hero smirk, cover frame 855'),
]
```

| rule | value (measured on the cut-outs' metadata) |
|---|---|
| look | A rim: `FA.fade_open(FA.rim_light(plain, FA.depth(pose), light=(0.8, -0.5)))`, rim on the screen-right edge (the ad's ember glow side); skin protection from `G.finish`; no relight |
| tile | glass card 360 x 300 r 26 inferno; inside: NIGHT_1 -> NIGHT_0 gradient + `K.radial(480, FLAME x0.35)` at the tile's top-right; cut-out clipped to the card |
| placement | scale 0.40 (<= 1.0); eye_mid at tile (190, 160) = screen (260, 1140). street_smirk: hair top y 1008, face box y 1074-1240, bust bottom 1367 (covers the tile bottom); street_sunglasses: hair top 1020, face box 1089-1249 |
| spacing | face box >= 74 px below the label tab (y 1000) and >= 140 px below the payoff caps (y 921); the caption solver keeps ink >= 28 px below the tile while it shows (measured ink top 1313); never under the like column (x <= 430) |
| motion | `FA.idle(t, seed=16)` (<= 0.4 % breathing at 0.3 Hz, 0.5 deg sway, 3 px drift); no camera move, no warp, no swap inside a showing; enter POP (scale 0.92 -> 1, opacity inout_sine 6 f); exit 10 f in_cubic |
| on-screen time | sunglasses f448-f511 = 2.133 s; smirk f836-f895 = 2.000 s (both <= 3.5 s) |
| not in the rewind | the tile is drawn outside `W_core`, so D9 never flashes a face |
| QA | halo <= +6 code values (3 px ring vs plate), black level within 2 code values of the tile, stills at f448, f480, f511, f836, f855, f895, plus every frame ±0.4 s around each entry/exit |

---------------------------------------------------------------------------------------------------------------

## 15. Shot list (cinematic-director template; World Bible lines in §3)

Shot ids match `packet.yaml` (scenes S1-S6 + S1B). Scene axis: the player faces the viewer; JD's tile looks screen-right toward the ad (sunglasses face turned
screen-left is fine inside the tile: he looks at the viewer-side edge, no mirroring). Light plot: §3 light logic.

| Shot | Purpose | Size | Lens | Move (speed, easing) | Action (gesture-level) | Cast / Props | Light (source, side, shadows) | Atmosphere | Uncomposed element | Dur (s) | Sound | Transition out | Anchor / Start-from |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| S1-01 hook A | reveal | full player, product medium | ortho UI + 85 mm product | locked; product push 2 %/bar from -0.4 s | the client's pin drops onto a perfect ad; the chip flips; the logo swells | CLIENT pin, CHAI_GLASS, UBAAL logo, counter | ember backlight behind the glass; flame rims on the UI | steam, bokeh, embers in the void | the chip's "Approved" for 12 frames before anyone reads it | 2.667 | thock, chip click, Dm downbeat | splice (hard, f80) | anchor; start_from S6-02 (loop seam) |
| S1B-01 hook B | reveal | full player | as above | D1 scrub pull-out and push-in | the v27 mess scrubs back to v3 | as above | as above | flares, glitter | the counter v27 | 2.667 | glitch, scrub chatter | D1 into S2 | anchor (scene S1B) |
| S2-01 escalation | change | full player | as above | locked; shake from f256 | eleven notes obeyed literally (v3-v11) | CLIENT pins, glass, logo, garam | cream gag v6-v12 inside the ad only | steam (outlined from v7) | the logo cropped by the ad edge | 10.133 | thock + slot tick per pin, drums arrive with "energetic" | D7 cut | anchor |
| S3-01 re-hook | change | full player | as above | locked | Mummy's messages arrive one by one | MUMMY pins, glitter | gold glitter twinkle | - | her thread covering the client's dots | 2.133 | Mummy thock (a fifth lower), drums out 2 beats | L3 cut | anchor |
| S4-01 cinematic | inform | player + JD tile | as above + webcam bust | locked; tile POP in/out | JD in sunglasses watches the flares overload | JD, flares, ribbon | anamorphic flares inside the ad; tile rim from the ad side | slow-mo steam | the letterbox hiding half the giant logo | 2.133 | parody braam | L3 cut | anchor |
| S4-02 chaos | build | full player | as above | locked; shake 8 px from f640 | everything bigger, call now, left, right; filenames pile up | CLIENT pins, drawer, clock chip | 3:47 AM | - | `v27_ab_pakka_final.mp4` | 6.4 | barrage, clock ticks, shepard (D7 at f640 inside the shot) | cut | - |
| S5-01 hover | atmosphere | full player | as above | locked; shake fades | a pin hovers, undecided, then the world holds its breath | CLIENT marker | - | steam slows to 0.2x | the marker freezing mid-air | 2.133 | heartbeat build, 8 f of silence, one tick | L3 cut | - |
| S5-02 payoff | reveal | full player | as above | locked | "Pehle wala hi theek tha." lands on the glass | CLIENT pin | clean landing, no chroma | - | 26 dots on the frame | 0.533 | loudest hit | D9 | anchor; start_from S5-01 |
| S5-03 rewind | change | full player | as above | rewind of the state clock (in_cubic) | Ctrl+Z x26: every version un-happens, the counter spins down | all | desaturated 30 % | zoom blur 0.02 | pins flying back up | 1.6 | tape rewind of the reel's own sound | D9 restore cut (match) | start_from S5-02 |
| S6-01 v1 | reveal (single image) | full player + JD tile | as above | locked | the pristine ad, "Approved", JD smirks; `pehle wala` rises | JD smirk, glass, logo | as S1 | steam, embers | the chip "Approved" again | 2.133 | warm chord, motif restarts | end card layer | **anchor** (cover f855); start_from S5-03 |
| S6-02 end card | inform | full player under the card | as above | locked | the JD ring draws on; "US CLIENT KO bhejo"; @jawad_mp4 | end card | world dimmed x0.58, player x0.35 | steam | the ad still breathing under the card | 4.267 | card shimmer, turnaround, reverse swell into f0 | loop_seam into S1-01 | start_from S6-01 |

Rhythm map: a visible note every 0.53-2.13 s (accelerating to every 0.53 s at bars 9-10), the hover slows it,
8 frames of silence stop it, the payoff hits at 75 %, the rewind runs it backwards in 1.6 s, then 6.4 s of calm
v1 into the loop. Hook (0-2 s): on screen a perfect ad being marked up; heard "Bas ek chhota sa change"; withheld:
how many changes, and the client's last message.

---------------------------------------------------------------------------------------------------------------

## 16. Engineering contract

Files (this reel only; shared modules are read-only):

| file | owner | contents |
|---|---|---|
| `pipeline/jawad_reels/pehle_wala.py` | motion-timeline-builder | `DUR = 34.1333333`, `LOOK = 'inferno'`, `BPM = 112.5`, `draw(t)` pure, `post(cv, t)`, `samples(t)`, `cues()` (delegates to `pehle_wala_sfx.cues()`), `prewarm()` |
| `pipeline/jawad_reels/pehle_wala_hookb.py` | motion-timeline-builder | imports `pehle_wala`; overrides `draw`, `samples`, `post`, `cues` for t < 80/30 (hook B head + D1); same DUR/LOOK/BPM |
| `pipeline/jawad_reels/pehle_wala_faces.py` | face-compositor | `FACES`, `draw_tile(cv, t)` |
| `pipeline/jawad_reels/pehle_wala_sfx.py` | sound-designer | custom sounds, `cues(hook='A'|'B')`, `build` CLI writing the SFX stems |
| `pipeline/jawad_reels/pehle_wala_music.py` | music-supervisor | the score, A/B heads, stems, `mix` CLI (epic_mix) |
| `pipeline/jawad_reels/assets3d_pehle_wala.py` | blender-3d-artist | `pw_chai_glass` |
| `<WS>/pehle_wala/` | all | `vo/`, `audio/`, `assets3d/`, `captions/`, `out/main`, `out/hookb`, `qa/`, `brief_proof/` (WS = `/home/user/100/workspace/jawad_reels`) |

Module structure (`pehle_wala.py`):
- Imports: `jawad_kit` first, then `jawad_grade as G` (registers inferno), `jawad_tx as X`, `endcard as E`,
  `snake_captions as SC`, `sprites3d as S3`, `pehle_wala_faces as PF`, faces tools path for `faces.py`.
- `VERSIONS`: the §6.3 table as data (land frame, change frame, reviewer, text, marker, card, change params).
  `state(s)` returns the ad state at state time s (counter value with odometer roll, logo scale and x, flags,
  cream amount, shake amplitude, pin card states, history dots). Pure.
- `W_core(s, a=None)`: world + player + ad (`state(s)`, ambient `a = s`) + pins + counter + status/clock chips.
  No faces, no lockups, no captions, no Ctrl+Z chip. Defined for negative s (v1, Approved).
- `W(t) = W_core(t)` + hook A overlay (t < 2.6667) ; `P(t) = W_core(t - DUR)` + payoff lockup + end card (+ extra
  player dim during the card).
- `draw(t)`: `cv = PLAN.draw(t, SCENES)`; then the Ctrl+Z chip (f784-f838), the face tile (`PF.draw_tile`), the
  captions (unless `PW_CAPTIONS=0`). Shake is inside `W_core` (player layer) so it rewinds too.
- `post(cv, t)`: `G.tx_finish(cv, t, LOOK, cuts=[(0.0, 0.6)], push=kw.get('push', 0) + card_push, rgb_split=
  kw.get('rgb_split', 0) + pin_tick(t), **rest)` where `kw = PLAN.post_kw(t)` and `card_push =
  CARD.post_kw(t, 29.8667, DUR).get('push', 0)`. Nothing else.
- `samples(t)`: `PLAN.samples(t)` (5 inside D9), 5 on SLAM/POP landings of banners (2 f), else 3.
- Local helpers (shared code stays untouched; see SHARED_REQUESTS.md): `KeyFirstTitle` (jw_key_core glyph rise +
  jw_key_halo + `J.underline` + jw_caps line below), the extra `CHANGE` line under the hook HouseTitle, the D9
  keycap suppression by `keys_y=-2000.0`, the loop-safe caption fade, the extra player dim under the end card
  (`k = 0.65 * K.ramp(u, 0, 0.5, 'inout_sine') * (1 - exit)`, `rgb *= 1 - k` on the player rect x 80-1000, y 236-1268,
  u = t - 29.8667, exit = the card's own exit ramp; it keeps the dimmed 'UBAAL CHAI' wordmark from fighting the JD ring).
- Parody font file: copy `Caveat-Bold.ttf` to `<WS>/fonts/pw_parody_fun.ttf` and `OFL-Caveat.txt` to
  `<WS>/fonts/OFL-pw_parody_fun.txt` (source: `/root/.claude/plugins/synced/.../skills/animation-studio/engine/fonts/`).

Render (always through heavy.sh; outputs land in the reel workspace via symlinks):
```bash
cd /home/user/100/pipeline/jawad_reels
ln -sfn /home/user/100/workspace/jawad_reels/pehle_wala/out/main  /home/user/100/workspace/jawad_reels/out/pehle_wala
ln -sfn /home/user/100/workspace/jawad_reels/pehle_wala/out/hookb /home/user/100/workspace/jawad_reels/out/pehle_wala_hookb
tools/heavy.sh python3 render.py pehle_wala --sheet 16 --samples 1 --workers 1 --no-audio
tools/heavy.sh python3 render.py pehle_wala --stills 0,0.533,2.133,4.267,6.6,12.8,14.933,17.067,21.333,22.4,25.6,26.9,27.733,28.5,31.6,34.1 --workers 1 --no-audio
tools/heavy.sh python3 render.py pehle_wala --range 25.2 28.2 --workers 1 --no-audio     # payoff + D9
tools/heavy.sh python3 render.py pehle_wala --preview --workers 1 --no-audio
python3 pehle_wala_sfx.py build A && python3 pehle_wala_music.py mix A                  # audio (heavy.sh for the music render)
FOSTER_NICE=10 tools/heavy.sh python3 render.py pehle_wala --workers 2 --no-sfx-build --audio <WS>/pehle_wala/audio/pehle_wala_A_mix.wav
tools/heavy.sh python3 render.py pehle_wala_hookb --range 0 2.6667 --workers 1 --no-audio
PW_CAPTIONS=0 tools/heavy.sh python3 render.py pehle_wala --stills 28.5 --workers 1 --no-audio   # cover
```
Hook B splice (delivery-packager): decode hook B frames 0-79 and the main master's frames 80-1023, concat, encode to
the delivery spec, mux `pehle_wala_B..._mix.wav`; verify 1,024 frames and that decoded frames >= 80 match the
main master's (mean abs diff 0 on the lossless intermediates).

Ops: one heavy job at a time from each agent; `--workers 1` while iterating, `--workers 2` for the master; Blender
threads 2; `df -h` before big outputs; keep `<WS>/pehle_wala` under 2 GB (delete preview frames, keep masters,
stems, the 3D set and the proof stills); never write into another reel's folders.

---------------------------------------------------------------------------------------------------------------

## 17. Post: cover, caption, hashtags, comment prompt, AI label

| field | value |
|---|---|
| cover | frame 855 (28.500 s), captions off: v1 ad, "Approved", `*pehle wala* / HI THEEK THA` (keyword box y 595-745, inside the 3:4 crop y 240-1680), JD smirk tile |
| caption L1 (54 characters, counted) | `POV: bas ek chhota sa change... editing ki asli kahani` (restates the hook; search keyword "editing"; "POV" labels the skit) |
| caption body | `v1 se v27 tak. Aur phir client ne bola: pehle wala hi theek tha.` |
| comment prompt (last line) | `Tumhare client ya boss ka 'bas ek chhota sa change' kya tha? Ek line mein.` |
| hashtags (4) | `#videoediting #editorlife #freelancerlife #jawadmp4` |
| audio name | `Original audio · Bas ek chhota sa change · @jawad_mp4` |
| AI label | turn on Instagram's "AI info" label: the voice is synthetic (Higgsfield Vlad) and the character-sheet imagery may be AI-generated (SLATE §7.1 default: label) |
| posting slot | Tue 13 Oct 2026, 7:00 PM PKT / 7:30 PM IST (SLATE §4 hypothesis, low confidence); hook B as a Trial Reel only if the account is eligible |
| truth | fictional brand "Ubaal Chai" (web check 2026-10-08 passed; trademark check by the lead / Jawad before posting), fictional client, POV label, no claims about Jawad |

---------------------------------------------------------------------------------------------------------------

## 18. QA acceptance checklist (measurable; motion-qa-reviewer runs both lenses, each major finding verified)

Format and timing
- [ ] ffprobe: 1080x1920, 30/1 fps CFR, nb_frames 1,024, duration 34.133 s (±1 frame) for hook A and hook B masters.
- [ ] Every event frame of §6.3 and §7 is exact: pin landings f8, 64, 96, 128, 192, 224, 256, 288, 320, 352, 384,
      400, 416, 432, 448, 480, 496, 512, 544, 576, 592, 608, 624, 640, 656, 672, 768 (marker tip touches its point
      on that frame, card visible from that frame); change frames equal the land frames except v2 (f32).
- [ ] Counter: v1 on f0-f31 (roll f28-f31), v2 f32-f63, ..., v27 from f672 to f783; spins down f790-f831; v1 from
      f832. Chip: Approved f0-f11 and f832-f1023, Changes requested f12-f831.
- [ ] Hook B frames 80-1023 identical to hook A (lossless intermediates mean abs diff 0).

Hook and story
- [ ] Frame 0: mean luma YAVG >= 25 (8-bit), motion present (frame 0 vs 1 mean abs diff > 0.5), no black/fade.
- [ ] VO onset <= 0.30 s (first sample above -40 dBFS on the VO stem); spoken hook <= 7 words ending <= 2.70 s;
      on-screen hook <= 6 words; lockup keyword glyphs >= 80 % opacity by f16 (measured on the stock HouseTitle with
      t0 -0.1: max alpha 1.0 in all 8 glyph slices at f16; 0.70-1.0 at f12).
- [ ] Payoff pin lands f768 (75.0 % of DUR); the rewind shows a visibly different state on every frame f790-f831.
- [ ] End card settled hold >= 1.5 s (2.057 s by construction); signature present 30.867-34.1.
- [ ] Loop: `E.seam_report` seam <= 1.5x a normal frame step; last 0.5 s audio RMS > -40 dBFS (no fade).

Copy, layout, legibility
- [ ] Every string in §6 matches exactly (spelling, case, punctuation), measured widths <= 940 px (<= 780 px for any
      line centred in y 1050-1700).
- [ ] Ink bboxes: all copy inside x 70-1010, y 230-1480; none at x > 930 for y 1050-1700; nothing below y 1620
      except `@jawad_mp4` at y 1575 (end card); `garam` right edge <= 914 (with shadow) and <= 922 (with shake).
- [ ] Never more than 2 text blocks (§5.3), sampled at 10 fps.
- [ ] Pin text 44 px (payoff 56 px), UI >= 34 px, filenames 40 px, window title 28 px flat; contrast >= 4.5:1
      measured on rendered frames for every pin card, chip, banner and the cream-gag keyword.
- [ ] Captions: `CAP.check() == []`; hidden 0-2.667; no chunk ink inside the player rect or the tile rect; SRT matches
      the VO tokens; house spelling.
- [ ] Underline appearances <= 3 per version (hook, payoff, end card); at least one serif keyword moment on a downbeat
      (PO1 at f832).

Motion and finish
- [ ] Transitions exactly at: L3 f128, f448, f512, f768; D7 f384, f640; D9 window f784-f833 (cut f832); hook B D1
      f40-f79 (cut f70). No keycaps anywhere; "Ctrl+Z ×26" chip f784-f838.
- [ ] No `K.flash`, `K.fade` or `post(flash=)` in any pehle_wala file (grep); 1st-percentile luma at push frames
      within ±2 code values of the previous frame.
- [ ] Exits >= 0.2 s (pin collapse 6 f, tile 10 f, lockups 10 f / 0.35 s, drawer 8 f); no one-frame jumps.
- [ ] Shake <= 8 px; luma flips <= 3 per second.
- [ ] Faces: tile on screen 2.133 s and 2.000 s; halo <= +6 code values; face box >= 60 px from any copy; scale 0.40.
- [ ] Colour (`python3 jawad_grade.py verify <master> inferno`): red-orange >= 60 % of saturated pixels, YMIN 16-22,
      cream area <= 35 % of the frame (30.8 % by geometry), FLAME/RED emissive <= 3x linear.

Audio
- [ ] Mix A: -14.0 ±0.5 LUFS, TP <= -2.0 dBTP (wav) and <= -1.5 after AAC, LRA 5-9; VO stem -16 LUFS; speech >= 8 LU
      over the music (median of voiced frames); SFX in VO windows >= 6 LU under speech.
- [ ] max momentary loudness within ±0.2 s of 25.600; RMS < -60 dBFS over 25.067-25.333; one held-breath tick at 25.333.
- [ ] Pin thock onsets within ±1 frame of the land frames; music tape-stop starts 26.133 ±1 f; music restart 27.733
      ±1 f; `EM.beatgrid` tempo 112.5 ±0.2, phase ±15 ms; <= 3 sound starts on any instant; tonal SFX within ±30
      cents of D or A.
- [ ] Version B (VO + SFX) delivered for both hooks; stems sum to the mix.

Brand, truth, ops
- [ ] Nothing from Organic Fostering / Floret; no old props; no typing dots; no ERROR/unsaved dialogs; no hearts; no
      currency, phone numbers, URLs or real logos; POV in the header and caption L1.
- [ ] Spoken and shown numbers: v1 -> v27, 26 change pins, "Ctrl+Z ×26", "chhabbees" (hook B only).
- [ ] AI info label noted for posting; Ubaal Chai trademark check logged.
- [ ] `du -sh <WS>/pehle_wala` < 2 GB at hand-off.

---------------------------------------------------------------------------------------------------------------

## 19. Work orders (run in this order; heavy jobs through heavy.sh, one at a time per agent)

1. **viral-strategist**: script gate on §9 (hook A and B) against this brief; then red-team the first full preview
   (frame-0 luma, VO onset, change gaps, phone-scale text) -> `brand_reels/design/reels/pehle_wala/viral_*.md`.
2. **hinglish-scriptwriter**: final VO lines from §9 drafts (Devanagari TTS track, Roman token track with `*keyword`,
   max words per line, windows); pronunciation test (छब्बीस, मम्मी, सिनेमैटिक, एनर्जेटिक, वी वन, फ़ाइनल); generate on
   Vlad within ~10 credits + re-takes; `vo_chain.py process`; assemble reel-timed `pehle_wala_vo_{A,B}.wav` +
   `.words.json` in `<WS>/pehle_wala/vo/`; timing table measured on the takes.
3. **blender-3d-artist**: `assets3d_pehle_wala.py` -> `pw_chai_glass` (§13), preview then finals, after C11's queue.
4. **face-compositor**: `pehle_wala_faces.py` (§14), stills and the measurements listed.
5. **motion-timeline-builder**: `pehle_wala.py` + `pehle_wala_hookb.py` (§5-§8, §10, §16) on a labelled glass
   stand-in until `meta.json` of `pw_chai_glass` appears; sheet -> stills -> range renders -> preview.
6. **sound-designer**: `pehle_wala_sfx.py` (§11): custom sounds with `A.qc(...) == []`, cue sheets A and B, stems.
7. **music-supervisor**: `pehle_wala_music.py` (§12): score A/B heads, tape-stop, restart, no end fade; mixes A
   (full) and B (VO + SFX) for both hooks with `epic_mix`; loudness and sync report.
8. **colorist**: inferno check on stills (cream gag, flares <= 3x, skin in the tile, hue budget), `G.verify` on the
   master; no per-shot grain.
9. **caption-designer**: verify the in-module snake captions (§10), `CAP.check()`, SRT export, cover render with
   `PW_CAPTIONS=0`.
10. **motion-qa-reviewer**: both lenses against §18 with a skeptical verifier per major finding -> `<WS>/pehle_wala/qa/`.
11. **delivery-packager**: masters A and hook-B splice, share and preview encodes, cover JPG, stems, audio Version
    B, ffprobe report -> `reel/jawad_reels/`.
12. (optional) **motion-toolkit-engineer**: the requests in `SHARED_REQUESTS.md` (none blocks this reel).

---------------------------------------------------------------------------------------------------------------

## 20. Open questions (SLATE §7 defaults applied; none blocks the build)

| # | question | default used here |
|---|---|---|
| 1 | AI label | on (synthetic voice; possibly AI-generated character sheets) |
| 2 | "Mummy" vs "Ammi" | "Mummy" (pin name "Owner ki Mummy", VO L7) |
| 3 | "Ubaal Chai" trademark | built as fictional; lead or Jawad runs IP India / IPO Pakistan before posting |
| 4 | "JD · editor" nameplate | used (labelled POV skit) |
| 6 | Trial Reels eligibility | hook B rendered anyway; posted as a Trial only if eligible |
| 7 | house spelling | prior SRT (bari, bohat): here "bara", "thora", "nahi", "hai" |

(SLATE §7.5 concerns C08 only.)

Shared-module requests (worked around locally): `SHARED_REQUESTS.md` in this folder.
