# BRIEF · Reel 2 · C11 · Bijli Chali Gayi (@jawad_mp4)

Production brief, **version 2 (r2: viral-gate fixes applied)**, 2026-10-08. Author: creative-director. Status:
**ready for build**. Binding sources: `brand_reels/design/SLATE.md` §0, §2, §3.2, §4, §5 (this brief resolves
everything SLATE leaves open with its defaults) and the concept + script gate `GATE.md` (verdict FIX; its fixes 1-5
and minor 6-9 are in this version, see §11 CHANGELOG). Every other agent builds exactly what is written here;
anything not written here is not in the reel. Companion files in this folder: `packet.yaml` (Jawad's
cinematic-director Production Packet), `SCRIPT.md` / `script.json` (hinglish-scriptwriter), `GATE.md`
(viral-strategist) and `SHARED_REQUESTS.md` (two shared-module bugs found while verifying this brief; both have local
workarounds).

Layout proofs (stand-in props, real house type, real cut-outs, real end card, real snake captions, `dusk` finish)
were rendered and checked: `workspace/jawad_reels/bijli_chali_gayi/out/brief_proofs/` (`p0`-`p9`, `*_zones.png`
show the safe zones, `proof_report.json` holds the measurements quoted below). **r2 proofs** (the real 3D room plate
and props from `RWS/assets3d/`, the bold CRT edit, the S5 monitor, a rooftop stand-in, the 86 px payoff, all through
`G.tx_finish(..., 'dusk', cuts=CUTS)`, each also saved at 360 px): `out/brief_proofs_r2/` (`sheet_360.png`,
`proof_report_r2.json`). Stand-ins (fan, rooftop planes, monitor) prove layout and luminance targets only; they are
not production art.

Notation: `f` = frame at 30 fps, frame 0 = 0.000 s. Bar n starts at frame 80n. Beat k = frame 20k. `RWS` =
`/home/user/100/workspace/jawad_reels/bijli_chali_gayi` (this reel's heavy outputs, keep < 2 GB). `WS` =
`/home/user/100/workspace/jawad_reels`. Toolkit folder = `pipeline/jawad_reels/`.

---------------------------------------------------------------------------------------------------------------

## 0. Deliverables

| item | value |
|---|---|
| reel | slot 2 of 5 (posting order), concept C11 "Bijli Chali Gayi", look `dusk` |
| format | 1080x1920, 9:16, 30 fps, **DUR = 1040 / 30 = 34.667 s = 1,040 frames** (13 bars at 90 BPM) |
| versions | **A** public (hook A, blackout) and **B** Trial Reel (hook B, no blackout). Frame-identical from the **splice frame 80 (2.667 s)**: the body is rendered once; hook B renders only f0-f79 and is spliced frame-exactly. |
| audio policy | VO (Vlad, Higgsfield `elevenlabs_v4`) + SFX + diegetic beds + one desi voice (harmonium sting). **No music bed and no `epic_music` style** (SLATE §3.2: keeps C11's sound world apart from the four scored reels). Two mixes (the bible's "version A / B" audio, renamed here so they never collide with the hook versions): **mix FULL** = VO + SFX + harmonium; **mix DRY** = VO + SFX without the harmonium (for an optional in-app track). Hook A gets FULL and DRY; hook B gets FULL. |
| loudness | final -14 LUFS integrated ±0.5, true peak ≤ -2.0 dBTP (wav), ≤ -1.5 dBTP after AAC, LRA 5-9 LU; VO stem -16 LUFS; SFX stem -18 LUFS |
| encodes | H.264 High yuv420p bt709, 2-pass ~22 Mbps, +faststart, AAC 320k 48 kHz; CRF 14 master; preview ~7 Mbps (< 30 MB); 48 kHz 24-bit stems (VO, SFX, mix FULL, mix DRY); cover JPG |
| paid ads | no (organic + Trial Reel). Organic safe zones apply (§4). |
| posting | slot 2: starting hypothesis Thu 15 Oct 2026, 7:00 PM PKT = 7:30 PM IST (SLATE §4, low confidence) |
| delivery names | `reel/jawad_reels/jawad_c11_bijli_chali_gayi_{A,B}.mp4` and the matching `_preview`, `_cover.jpg`, stems (delivery-packager naming, project.json `deliver`) |

## 1. Brand (copied from SLATE §5.1 and `pipeline/jawad_reels/BRAND.md`; never re-derive)

- **Palette (project.json tokens only):** NIGHT_0 #070404 · NIGHT_1 #170A07 (70-85 % of every frame near-black or
  dark warm) · FLAME #FF6A1A (10-20 %) · RED #F2312B · EMBER #B3120E · GOLD #FF9F1C / AMBER #FFB547 (≤ 5 %) ·
  SMOKE #2A1A15 · PLUM #4A0E08 · IVORY #FFF3E6 (type, never pure white) · ASH #A8978C. `dusk` adds indigo-violet
  shadows (#171431, the look's split-tone colour): the brightest 5 % of saturated pixels must be red-orange (≥ 60 %)
  and violet ≤ 45 % of saturated pixels (`jawad_grade` BUDGET 'top5'). Emissive FLAME / RED ≤ 3× linear.
- **Type:** `jw_key` (Instrument Serif Italic flame keyword), `jw_caps` / `jw_caps_bold` (Poppins SemiBold / Bold
  caps), `jw_body`, `jw_mono` (JetBrains Mono), `jw_handle`. House lockups via `J.HouseTitle`, underline via
  `J.underline` (≤ 3 per reel: this reel uses 2 in version A, 2 in version B).
- **Mark and handle:** derived JD monogram ring (endcard.Monogram, never stretched or recoloured), `@jawad_mp4`
  via `J.signature` at y 1575.
- **Look:** `LOOK = 'dusk'` from `jawad_grade.py`; the only post call is `G.tx_finish(...)` (§7). Never `neon`,
  `amber`, `airy` or their footage grades. Grain only from the look's finish (0.020, 1.7 px).

## 2. Verified copy and Do not claim

Source for every line: SLATE §3.2 (approved concept, truth-safe framing) unless noted. Status "verified" = approved
in SLATE; "brief" = UI/microcopy introduced here (no claim content); "panel" = from `panel_viral.md` §4.3 (approved
line the SLATE spine leaves implicit).

| id | exact text | style / where | source | status |
|---|---|---|---|---|
| H1 | `Bijli` | jw_key, hook A | SLATE 3.2 hook A | verified |
| H2 | `CHALI GAYI.` | jw_caps, hook A | SLATE 3.2 hook A | verified |
| HB1 / HB2 / HB3 | `YEH` / `awaaz` / `YAAD HAI?` | hook B | SLATE 3.2 hook B | verified |
| R1 | `AA GAYI!` | jw_caps_bold slam, 8.0 s | SLATE 3.2 spine | verified |
| U1 | `RENDERING` | jw_mono HUD | brief | brief |
| U2 | `63%` → `64%` → drains → `0%` | jw_mono HUD | SLATE 3.2 ("render 63 %", "drains to 0 %") | verified |
| U3 | `Saved` | ui.chip | SLATE 3.2 ("Saved" chips) | verified |
| U3F | `Saved · har 30 sec` | ui.chip, only if VO V9 is dropped (§6.7 fallback F4) | brief | brief |
| K1 / K2 | `Ctrl` / `S` | 3D keycap legends | SLATE 3.2 (keycap ×2 legends) | verified |
| P1 / P2 | `BIJLI NE SIKHAYA` / `sabr` | J.HouseTitle payoff | SLATE 3.2 payoff; spelling per GATE fix 4 (house SRT: "dikhai", doubled vowel only in a stressed first syllable) | verified (r2 spelling) |
| E1 / E2 / E3 | `COMMENT MEIN` / `batao` / `Chhat ya candle?` | EndCard | SLATE 3.2 end card | verified |
| E4 / E5 | `@jawad_mp4` / `JD` | EndCard signature / monogram | series bible | verified |
| V1-V12, V1B | the VO lines in §6.7 | VO + snake captions | SLATE 3.2 (V4: panel); V4, V7, V8 trimmed and V10/V11 caption spelling per GATE fixes 1 and 4 | verified; the r2 trims are copy changes the lead signs off before takes T2 and T4 (§10) |

**Do not claim (hard):** nothing about Jawad's own childhood, home, power cuts, first PC, editing start, habits or
clients (the narrator is "hum / har desi editor / aap", never "main"; JD on screen is the face of "an editor", not a
memoir) · "har tees second" is a joke about a habit, never a statistic (no on-screen "every 30 s" claim except the
F4 fallback chip, which repeats the joke) · no utility, government, company, city or country names, no
"load-shedding" politics · no UPS / inverter label or brand, no logo on any prop · no money on screen · no real app
UI, no laptop, no "unsaved" / ERROR / delete dialog · no synthesised voices; crowd sounds are wordless CC0 samples ·
no flags, domes, minarets, temples, cricket cues or team colours on the rooftops · no "Comment JD" · 1M views is
never mentioned.

## 3. References, Director's pass and World Bible

**Devices taken (never layouts or audio):** ref2 "light is the transition" (L7 beam, L4 bloom-out), J-cut pre-laps
of 0.2-0.3 s, a sub-weight hit on world changes; ref3 the light-beam sweep (as L7); ref1 low-pass-hold-then-drop
is NOT used (no music). Jawad's covers: serif-italic flame keyword + white grotesk caps + glowing underline;
red-orange rim on the subject.

**Director's pass (compact):** emotional core = nostalgia that turns into quiet pride. Killed: a sepia flashback of
a child doing homework; a "90s kids yaad hai?" object montage; the UPS-beep meme with a reaction face. Point of
view: the reel is a house on the grid, it loses power itself. Contradiction: the darkest reel of the set is lit like
luxury cinema; a power cut is the most beautiful light. Human truth: "light jaati thi toh poora mohalla chhat pe
hota tha", and for editors, the finger that presses Ctrl+S by itself. **Single image:** black; a torch beam cuts
through dust and finds the orange LED of a power-backup box blinking, while the word *Bijli* glows as the only
thing still on battery (the cover, f60).

**World Bible (verbatim in `packet.yaml`):**
- Palette: night #070404, torch and tube-light ivory #FFF3E6, LED flame #FF6A1A, candle amber #FFB547, drain red
  #F2312B, dusk indigo shadow #171431. (#171431 is a shadow colour only, never a light.)
- Light logic: every light is a battery (torch, candle, the backup box's LED) until the power returns; then every
  mains practical (tube light, bulbs, CRT, monitor) blooms locally at once. Mains light never fades: it snaps on,
  flickers darker, or dies.
- Lens set: 28 mm for rooms and rooftops; 85 mm for JD and the tabletop; 100 mm macro for the candle, LED and keycaps.
- Camera law: handheld "torch operator" drift while the power is off; locked off the instant it is on.
- Texture: `dusk` finish, fine warm grain 0.020 at 1.7 px, halation on every practical, indigo-violet shadows,
  crushed but legal blacks.
- Sound motif: the backup box's double beep (two 70 ms piezo pulses at D7, 4 frames apart).
- Symbol: the blinking orange LED.
- Forbidden: more than 4 frames of empty near-black; white frames or full-frame flashes; flicker that brightens;
  utility, government or city names; UPS or inverter labels; money; a laptop or any unsaved / ERROR dialog;
  synthesised voices; cold blue moonlight; religious or national markers on rooftops; cricket cues; mirrored JD;
  cross-dissolved faces; anything from Organic Fostering or Floret; the old prop library.

## 4. Global craft rules (Standards, apply to every frame)

- **Safe zones 1080x1920:** key copy inside x 70-1010, y 230-1480 (CTA to 1600); bottom 300 px free of text
  (nothing textual below y 1620); never copy at x > 930 for y 1050-1700; profile grid crop 3:4 = y 240-1680 (cover
  keyword inside it). Lines in y 1050-1700 ≤ 780 px wide, elsewhere ≤ 940 px. At most 2 text blocks at once (the
  end card's lockup + sub + handle is the standard card).
- **Sizes:** hero ≥ 130 px; H2 80-120 px; UI ≥ 34 px (tags read in motion ≥ 40 px); contrast ≥ 4.5:1 (measured on
  the end card proof: keyword 6.4:1, caps 19.7:1, sub 19.8:1, monogram 6.2:1, handle 16.7:1).
- **Finish:** no `K.flash`, `K.fade` or `post(flash=)`; exposure pushes only (multiplicative). Motion blur never
  crosses a cut (HALF rule, `X.side_b`). Exits ease out ≥ 0.2 s (no one-frame jump). Animated-to-static hand-offs
  are continuous. Camera tracks have no jumps. 5-7 samples on fast moves. Particles and bokeh never over type.
- **Faces:** 2.5D cut-outs only, display scale ≤ 1.0 of the 2x master, ≤ 3.5 s on one still pose, hard-cut swaps,
  no cross-dissolve, no mirroring, no lip-sync, natural skin (human-realism / photo-realism), bust bottoms below the
  frame, never covered by a prop or text.
- **Delivery:** as §0; verify duration, fps and frame count with ffprobe (nb_frames = 1040).
- **QA:** two independent lenses (A copy/layout/legibility/safe zones; B motion/transitions/finish/audio sync), a
  skeptical verifier per major finding, 5 fps sheets plus every frame within ±0.4 s of each transition and each
  power event, measured numbers only (§8).
- **Ops:** heavy jobs only through `pipeline/jawad_reels/tools/heavy.sh <cmd>` (2-slot semaphore, nice 10, 2
  threads); Blender `threads = 2`; render.py `--workers 1` while iterating, 2 for the master; `df -h` before big
  writes; RWS < 2 GB, delete intermediates (preview frames, audition wavs) after use. Agents never commit.

## 5. Assets and ledger

| asset | owner | path | status |
|---|---|---|---|
| 8 Blender asset folders (§6.12): `desk_plate`, `crt_room`, `tower_room`, `box_room`, `pankhi`, `candle`, `keycap_ctrl`, `keycap_s` | blender-3d-artist | builder `pipeline/jawad_reels/assets3d_bijli_chali_gayi.py` → `RWS/assets3d/<name>/passes/` | to build (critical path, start first) |
| 2D sprites: ceiling fan (3 blades + hub), tube-light glow, rooftop layers + silhouettes (with the r2 haze band, candle pools, rims, the far window and the child's two head paths), bulbs, homework copy (S2), modern monitor UI (r2: the same edit + 9:16 rooftop viewer), render HUD, CRT mini-timeline image (r2: bold `crt_image`) | motion-timeline-builder (in the module, `lru_cache`d) | `pipeline/jawad_reels/bijli_chali_gayi.py` | to build |
| JD cut-outs `suit_profile`, `suit_smiling` (look A rim) | face-compositor | `pipeline/jawad_reels/bijli_chali_gayi_faces.py` (FACES list + builders) | to build |
| custom SFX (12) + cue sheet + beds | sound-designer | `pipeline/jawad_reels/bijli_chali_gayi_sfx.py` → `RWS/audio/` | to build |
| VO takes (Vlad), DEV/ROM token tables, processed stems, words JSON | hinglish-scriptwriter | `RWS/vo/` (+ script `RWS/vo/bijli_chali_gayi_script.md`) | to write + generate |
| harmonium placement, mixes A FULL / A DRY / B FULL, loudness | music-supervisor | `pipeline/jawad_reels/bijli_chali_gayi_music.py` → `RWS/audio/` | to build |
| captions config | caption-designer | inside the module (`SC.Captions`), SRT to `RWS/captions/` | to build |
| `dusk` look checks | colorist | `jawad_grade.py` (shared; read-only for this reel) | exists |

Existing inputs: cut-outs + depth + metadata in `workspace/brand_reels/charsheet/cutouts/`; `faces.py` helper;
`epic_sfx.py` (registers `harmonium_swell`, `crowd_cheer_real`, `edit_suite`, `keyboard_burst`, `mouse_click`...);
the `dusk` LUT `pipeline/jawad_reels/luts/dusk_33.cube`.

## 6. The reel

**Title** Bijli Chali Gayi · **Goal** shares cousin to cousin, school friend to school friend ("yeh hamara
bachpan") and comments ("Chhat ya candle?") · **DUR** 34.667 s (1,040 f) · **BPM** 90 (20 f/beat, 80 f/bar, fully
frame-locked) · **LOOK** `dusk` · **Signature device** power-cut grammar (the reel obeys electricity) ·
**Transition family** light (L7 ★, L8, L4 ★, L3 glue) · **Hero face** `suit_profile` · **Payoff keyword** *sabr* ·
**Symbol** the blinking orange LED.

### 6.1 Beat grid (frames; total = 1,040 = DUR)

| bar | start f | start s | beat frames (1-4) | section |
|---|---|---|---|---|
| 0 | 0 | 0.000 | 0 20 40 60 | HOOK (A blackout / B torch-lit), splice at f80 |
| 1 | 80 | 2.667 | 80 100 120 140 | candle, pankhi, homework; tilt up f140-f159 |
| 2 | 160 | 5.333 | 160 180 200 220 | night rooftops; **f220 tease: a far tube light false-starts** (r2) |
| 3 | 240 | 8.000 | 240 260 280 300 | **re-hook 1: power back, AA GAYI!**; f300 dies again (gag) |
| 4 | 320 | 10.667 | 320 340 360 380 | L7 into the old room by torch |
| 5 | 400 | 13.333 | 400 420 440 460 | lights on: modern edit desk, render 63 % |
| 6 | 480 | 16.000 | 480 500 520 540 | **re-hook 2 (46 %): power dies mid-render**, 0.4 s VO silence |
| 7 | 560 | 18.667 | 560 580 600 620 | L8 iris into Ctrl+S keycaps (quarters) |
| 8 | 640 | 21.333 | 640 660 680 700 | keycaps on 8ths, Saved chips |
| 9 | 720 | 24.000 | 720 740 760 780 | candle macro, JD profile by candlelight |
| 10 | 800 | 26.667 | 800 820 840 860 | drop-out f790-f799; **PAYOFF (77 %)** *sabr* |
| 11 | 880 | 29.333 | 880 900 920 940 | **power returns (loudest), L4**; end card f920 (beat 46) |
| 12 | 960 | 32.000 | 960 980 1000 1020 | end card hold; loop into frame 0 at f1040 |

Power timeline (drives lights, camera law and the beds): ON f0-f13 · OFF f14-f239 · ON f240-f299 · OFF
f300-f399 · ON f400-f479 · OFF f480-f559 · ON f560-f719 (keycaps, monitor glow) · OFF f720-f879 · ON f880-f1039.
Camera: locked while ON; handheld drift while OFF (§6.9).

### 6.2 Shot list (Jawad's shot-list template; World Bible lines apply to every shot)

| Shot | f (s) | Purpose | Size | Lens | Move (speed, easing) | Action (gesture-level) | Cast / Props | Light (source, side, shadows) | Atmosphere | Uncomposed element | Sound | Transition out | Anchor |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| S1A hook A | 0-79 (0-2.633) | change | wide room | 28 mm | locked f0-f19; drift from f20 | the fan turns, the CRT shows a bold 3-track edit with its playhead crawling (§6.9); at f10 the room browns out, f12-f15 the CRT collapses to a dot, the keyword glows, f20 a torch clicks on and finds the box | CRT, TOWER, BOX, FAN, TUBE | tube light top-left, CRT spill; then only the LED, the CRT dot and the torch from camera-right low | dust in the torch beam | the tower half-hidden under the table edge | §6.3 | cut at the splice | **anchor (single image = f60)** |
| S1B hook B (trial) | 0-79 | change | wide room | 28 mm | drift from f0 | the LED blinks with a beep on f0; the beam drifts from the box up to the dead CRT | BOX, CRT | torch only, camera-right low | dust in the beam | an unplugged cable drooping off the table | §6.4 | cut at the splice | start_from S1A |
| S2 candle | 80-159 (2.667-5.300) | atmosphere | tabletop | 85 mm | drift; tilt up f140-f159 (in_cubic, +900 px) | a match flares and lights a candle on a steel saucer; a pankhi swings in from the right on beats f100/f120/f140; a homework copy (kraft-brown cover) lies open by the candle | CANDLE, PANKHI, COPY | the candle flame only, from frame centre; shadows fall away from it | candle haze, faint smoke from the match | the match stick, burnt, left on the saucer rim | match_strike f80, leaf_rustle | hard cut + push 0.25 (tilt continues) | |
| S3 rooftops | 160-319 (5.333-10.633) | reveal | wide | 28 mm | tilt settles f160-f180 (out_cubic); drift; LOCKS at f240; drift again from f300 | neighbours on charpais and parapets fan themselves; **f220-f221 a far window's tube light snaps on, f222 it is dead; f224-f230 the near child turns its head toward it** (r2); at f240 every bulb cascades on, `AA GAYI!` slams, the street cheers; at f300 it all dies again | ROOFTOPS, BULBS, silhouettes, FAR_WINDOW | stars, a warm dust-haze band behind the far skyline, parapet candles with warm pools on the parapet, charpai and the silhouettes' candle-side rims; f240-f299 bulbs as local blooms | night haze, distant stars | one bulb lights a frame late and buzzes | far hum blip f220, cheer, power_thunk ×2 | L7 at f320 | |
| S4 old room by torch | 320-399 (10.667-13.300) | inform | wide room | 28 mm | drift; slow push 1.00 → 1.04 (easy_ease) | the torch finds the homework copy on the table, then the dead CRT and the box | COPY, CRT, BOX | torch only | dust in the beam | the pankhi lying on the table, left where it fell | beep f380 | hard cut + push 0.8 (lights on, on-word) | |
| S5 modern desk | 400-559 (13.333-18.633) | change | medium desk | 28 mm | locked f400-f479; drift from f480 | the monitor shows the same 3-track edit as the 2000s CRT (playhead parked where the CRT died) next to a 9:16 still of the rooftops (§6.9); a render sits at 63 %, ticks to 64 %, the room browns out once (f470) and dies at f480: the monitor collapses to a line, the HUD drains 64 → 0 % in RED | MONITOR, HUD | desk lamp top-left + monitor glow; then only the red HUD | none | a cold cup of chai at the right edge, a ring stain under it | power_thunk, crt_off, sub_drop | L8 at f560 | |
| S6 keycaps | 560-719 (18.667-23.967) | move | macro | 100 mm | locked | Ctrl and S are pressed together on quarters (f580, f600, f620) then 8ths (f640-f710); each press pops a `Saved` chip | KEYCAP_CTRL, KEYCAP_S | monitor glow from above-front, legends glow FLAME on each press | none | a crumb between the keys | keycap_thock ×22, ui_tick ×11 | hard cut + push 0.3 | |
| S7a candle macro | 720-739 (24.0-24.633) | atmosphere | macro | 100 mm | drift (amp 0.5) | a candle burns on the saucer; the flame leans and recovers | CANDLE | the flame only | heat shimmer above the flame | a wax drip running down one side | impact_soft lp 900 | hard cut + push 0.2 | |
| S7b JD profile | 740-839 (24.667-27.967) | change | MCU | 85 mm | drift (amp 4 px, 0.3°) | JD in profile watches the candle, lips pressed, breathing; drop-out f790-f799, the lockup rises from f800 | JD (suit_profile), CANDLE | candle screen-right at eye height: warm rim on his face, the far side falls into indigo dark | sparks drift up from the flame (kept off the type) | a loose hair at the crown catching the rim | drop-out, harmonium, velvet hit | hard cut f840 | **anchor of the payoff** |
| S7c candle macro + lockup | 840-879 (28.0-29.300) | atmosphere | macro | 100 mm | drift (amp 0.5) | the flame steadies under `BIJLI NE SIKHAYA / sabr` | CANDLE | the flame only | heat shimmer | the wick curling | riser into f880 | **L4 at f880** | |
| S8a power returns | 880-919 (29.333-30.633) | change | MCU | 85 mm | locked | the tube light strikes, the fan spins up behind him, JD smiles | JD (suit_smiling), TUBE, FAN, CRT | tube light top-left key, CRT glow behind his head as a rim | none | the fan still accelerating | the appliance chorus (loudest) | hard cut + push 0.3 | |
| S8b end-card room | 920-1039 (30.667-34.633) | move | wide room | 28 mm | locked (= frame-0 composition) | the lit room as at frame 0: fan turning, CRT playhead crawling | CRT, TOWER, BOX, FAN, TUBE | as frame 0 | none | as frame 0 | end card, reverse_swell into f0 | **loop seam to f0** | start_from S1A f0 |

Rhythm map: 2.7 / 2.7 / 5.3 / 2.7 / 5.3 / 5.3 / 0.7 / 3.3 / 1.3 / 1.3 / 4.0 s; the single image lands at f60 (cover);
the payoff anchor is S7b; the loop seam is f1039 → f0. Hook (0-2 s): on screen a lit room that dies, **with an edit
on the CRT that dies with it** (the forward open loop for non-followers, GATE fix 2), and a glowing *Bijli* | heard
the fan winding down, the relay, two beeps | withheld what an editor has to do with it (answered at 13.33 s, when the
same edit is back on a modern monitor). Product moment (the craft):
S6, Ctrl+S on the beat.

### 6.3 Hook A, frame by frame (SLATE §2 frame-0 rules: never more than 4 frames of empty near-black; keyword lit by 0.5 s)

| f | t (s) | picture | text | VO | sound |
|---|---|---|---|---|---|
| 0 | 0.000 | CAM_ROOM **lit**: desk_plate `lit` + props `room` passes; tube light on (IVORY core); CRT on with the **bold mini-timeline** (§6.9: 3 clip tracks 48 px tall, FLAME / EMBER blocks, IVORY playhead 6 px wide crawling 60 px/s); ceiling fan at full speed (4.5 rev/s, 5 samples, blades dark against the lit ceiling, §6.9); LED steady AMBER 30 %; camera locked; frame 0 carries the loop push `cuts=[(0.0, 0.6)]`. **Gate (§7):** after `G.tx_finish`, f0 and f9 YAVG ≥ 35 (limited), luma p99 ≥ 200 (limited); tube, fan and CRT edit readable at 360 px (r2 proof on the real plate: f0 49.0 / p99 234, f9 38.2 / p99 224) | none | (V1 starts f3) | impact_soft -8 lp 900; beds room_mains -24, crickets -38 |
| 3 | 0.100 | same | | **V1 "Bijli chali gayi."** 0.100-1.150 | |
| 10 | 0.333 | brownout: mains-lit layers ×0.45 (tube, CRT image, room fill; never the LED, never type) | | | tube_flicker -12 |
| 11 | 0.367 | mains ×0.80 | | | |
| 12 | 0.400 | mains ×0.35; CRT image squeezes vertically to 40 % | | | crt_off -8 |
| 13 | 0.433 | mains ×0.15; CRT image 6 % tall | | | |
| 14 | 0.467 | **mains 0**: plate switches to `practicals` pass; CRT is a **8 px** bright line (the collapsed image ×2.5 with an AMBER ×1.2 phosphor core; never thinner on this frame) shrinking in width; LED switches to battery (FLAME 60 % steady) | | | relay_click -10; fan_wind down (3.0 s) start; mains bed off; crickets up to -32 |
| 15 | 0.500 | CRT = 12 px dot (AMBER ×2.5, decays τ 0.35 s); **H1 `Bijli` glows** at (540, 520), opacity 0.35 → 0.70 (inout_sine) by f24 | H1 in | | shimmer -12 hp 5500 |
| 18-36 | 0.600-1.200 | fan blades slow visibly (rate decays τ 1.0 s); **H2 `CHALI GAYI.`** rises at (540, 720): opacity inout_sine 13 f, y +28 → 0 out_cubic 18 f, blur 6 → 0 | H2 in | V1 ends ≤ f35 | |
| 20 | 0.667 (beat 1) | **torch clicks on**: hotspot on the wall behind H1 at (560, 600); H1 boosted to 1.0 under the beam; handheld drift starts (amplitude 0 → 1 over 15 f) | | | mouse_click -10 |
| 24-38 | 0.800-1.267 | the beam sweeps (inout_sine) down-right to the box (830, 1300); H1 settles to 0.75 | | | |
| 40, 44 | 1.333 (beat 2) | LED pulses: FLAME ×3 on f40-41 and f44-45 | | | **backup_beep** 0 |
| 41-59 | 1.367-1.967 | the beam holds on the box with drift; 60 dust motes (J.embers, dim) masked by the beam cone | | | |
| 60, 64 | 2.000 (beat 3) | LED pulses f60-61, f64-65. **Cover frame (f60)**; the delivered cover is a dedicated still of this frame with H1 at 1.0 (§6.15, r2) | | | **backup_beep** 0 |
| 66 | 2.200 | | | **V2 "Yaad hai?"** 2.200-2.600 (SLATE placement, kept when TA's processed V2 is ≤ 0.43 s). **Fallback (GATE fix 5, needs the lead's OK: SLATE deviation):** if V2 runs > 0.43 s, place it at **1.550-≤ 2.000 (f47-f60)**, between the double beeps (beep 1 ends 1.537, beep 2 starts 2.000), so the second beep answers the question; never trim the rising "hai?" | |
| 72-79 | 2.400-2.633 | H1 + H2 exit: opacity in_cubic, 8 px up, blur 0 → 6 (8 frames, 0.27 s) | out | | |
| 80 | 2.667 (bar 1) | **splice**: hard cut to S2, the match flares (exposure push 0.5) | | | match_strike 0 |

Every frame f14-f79 has a lit element (CRT line/dot, keyword, LED, beam): QA requires max luma ≥ 150 and ≥ 2,000
pixels above luma 90 on every one of these frames (§8). f14 is the thinnest: on the real practicals plate (r2 proof)
a 6 px line gave only 2,090 px above luma 90 (limited), an 8 px line 2,770 px, hence the 8 px line. f14's YAVG
measured 17.4 (limited): as the instant the mains die it is the designed blackout and is exempt from the YAVG ≥ 18
floor only (§8), never from the 2,000 px / max-luma rule. f15 (dot + *Bijli* at 0.35) gave 21,339 px, YAVG 19.5.

### 6.4 Hook B (Trial Reel), f0-f79

| f | t (s) | picture | text | VO | sound |
|---|---|---|---|---|---|
| 0 | 0.000 | CAM_ROOM **dark, torch-lit**: plate `practicals`, props `key_r` passes × beam mask; hotspot on the box (830, 1300), the whole box silhouette inside the beam; drift already running; LED pulses f0-1 and f4-5 (each pulse = box `emit` ×3 + a FLAME ×3 disc r 5 px with `K.glow(sigmas=(4, 12, 30))`, so the bloom above luma 90 is ≥ 40 px wide at 1080 and the LED reads at 360 px: r2 proof 60 × 24 px, `hookB_f00_led_360.png`; GATE minor 7) | **HB lockup mid-rise**: `J.HouseTitle('YEH', 'awaaz', caps_px=96, key_px=240, underline=False).draw(cv, t, 540, 520, t0=-0.1, out_t0=2.267)` | | **backup_beep** 0 (the f0 transient); beds crickets -32, room_tone -34 |
| 9 | 0.300 | | | **V1B "Yeh awaaz... yaad hai?"** 0.300-1.950 (the "..." pause holds the f40 beep) | |
| 11-29 | 0.367-0.967 | **HB3 `YAAD HAI?`** jw_caps 96 at (540, 700) rises (t0 0.35, 0.6 s, as a caps line) | HB3 in | | |
| 30-70 | 1.0-2.333 | the beam drifts from the box up to the dead CRT glass (a reflection slides across it) | | | |
| 40, 44 | 1.333 | LED pulses | | | **backup_beep** 0 |
| 68-78 | 2.267-2.617 | HB lockup + HB3 exit (in_cubic 0.35 s) | out | | |
| 80 | 2.667 | splice into the shared body (match strike) | | | |

Version B's loop seam (lit end card → torch-lit f0) is a deliberate hard cut: on replay the power "dies" at the seam.

### 6.5 Re-hooks, reveal, payoff, end card, loop bridge

- **Tease, f220 (7.333 s, beat 11), r2 (GATE fix 3):** under "...wapas aati thi...", a far window's tube light
  snaps on for 2 frames (f220-f221) and is dead on f222 (legal: mains light snaps on or dies, it never fades); the
  near child's silhouette turns its head toward it over f224-f230 and holds there until the slam. With f240 it makes a
  three-step joke: setup, false start, AA GAYI! Spec in §6.9; sound: one low hum blip (§6.10).
- **Re-hook 1, f240 (8.000 s, bar 3):** power back. Bulbs ignite far → near, two per frame over f240-f245, each a
  local bloom (AMBER core ≤ 3× linear) with a soft pool on its wall; distant windows light (IVORY ×0.4); the camera
  locks; exposure push 0.5; `AA GAYI!` slams. **f300 (10.000 s, beat 15):** the gag, everything dies again, near → far
  over f300-f302, the cheer is cut dead.
- **Re-hook 2, f480 (16.000 s, bar 6, 46 % of the runtime):** the power dies mid-render: monitor collapse (f480-f485),
  HUD drains 64 → 0 % (f486-f520, in_cubic, turns RED below 20 %), 0.4 s of VO silence (16.000-16.400), then V7.
- **Reveal / payoff, f800 (26.667 s, bar 10, 77 %):** after the drop-out f790-f799 (everything silent except room
  tone held at about -45 LUFS), the payoff lockup rises (§6.6 P1/P2) and the harmonium peaks on "sabr" (f820).
- **Loudest moment, f880 (29.333 s, bar 11):** the power returns via L4: the candle flame floods into red-orange
  halation, resolves on JD smiling in the lit room; the appliance chorus (thunk, sub, fan spin-up, tube strike, CRT
  degauss, the neighbourhood cheering again).
- **End card, f920-f1039 (30.667-34.633 s, starts on beat 46):** `E.EndCard('COMMENT MEIN', 'batao', sub='Chhat ya
  candle?', monogram='JD', dur=4.0, y_mono=360.0, y_key=730.0, y_sub=965.0, y_sig=1575.0)`; `T_END = DUR - card.dur`
  (frame 920; pass the literal 4.0, see SHARED_REQUESTS #2). Settled at +1.85 s (f975.5), held 1.79 s (≥ 1.5), exits
  over the last 0.36 s with the loop push. The lockup sits higher than the default (y_mono 560 / y_key 930 / y_sub 1165)
  so the CRT screen (y 1050-1290) is never behind the keyword: proof `p7_endcard_33s_zones.png`, contrast measured
  ≥ 6.2:1 on every element. Spoken CTA V12 31.650-34.100 during the hold (r2 window, §6.7).
- **Loop bridge:** S8b's world is the frame-0 world: every time-varying element of S8b reads the hook's lit-room
  clock at `t - DUR` (fan angle, CRT playhead, tube flicker), so frame 1039 is frame -1 of the lit room and
  `E.loop_world(world, t, DUR, d=0.6)` cross-fades identical content (no ghosting). Audio: room_mains bed runs to DUR
  with fade 0.004 and restarts at f0 at the same gain; the end card's `reverse_swell` ends exactly on DUR and the
  f0 `impact_soft` is its release; V12's question is answered by V1 "Bijli chali gayi." On replay of version A, the
  power dies again at f10.

### 6.6 On-screen text (measured with `T.measure`; positions = centre of the text box unless noted)

| id | string | style | px | width × height (px) | position | in | out | animation |
|---|---|---|---|---|---|---|---|---|
| H1 | `Bijli` | jw_key | 250 | 394 × 180 (+ descender) | (540, 520) | f15 | f72-f79 | self-glow (opacity 0.35 → 0.70 f15-f24, inout_sine), torch boost to 1.0 f20-f30, settles 0.75 by f38; `T.render('Bijli', 'jw_key', px=250).draw(cv, 540, 520, opacity=o)`; exit opacity in_cubic + 8 px up + blur 0 → 6 |
| H2 | `CHALI GAYI.` | jw_caps | 96 | 618 × 67 | (540, 720) | f18 | f72-f79 | caps rise (opacity inout_sine 0.42 s, y +28 → 0 out_cubic 0.6 s, blur 6 → 0), exit with H1 |
| HB1-2 | `YEH` / `awaaz` | jw_caps / jw_key | 96 / 240 | 192 × 67 / 579 × 173 | keyword centre (540, 520), caps centre y 328 | t0 -0.1 (mid-rise at f0) | out_t0 2.267 | `J.HouseTitle('YEH', 'awaaz', caps_px=96, key_px=240, underline=False)` |
| HB3 | `YAAD HAI?` | jw_caps | 96 | 552 × 67 | (540, 700) | f11 | 2.267-2.617 | caps rise t0 0.35; exit in_cubic 0.35 s |
| R1 | `AA GAYI!` | jw_caps_bold | 170 | 832 × 120 | (540, 620) | f240 | f300-f305 | `T.Glyphs('AA GAYI!', 'jw_caps_bold', px=170).slam(cv, t, 540, 620, t0=8.0)` (SLAM spring), static `T.render` draw from 8.6 s; exit = the power dying: opacity per frame f300..f305 = 0.35, 0.80, 0.15, 0.45, 0.05, 0 (darken-only flicker, 6 f) |
| U1 | `RENDERING` | jw_mono | 40 | 222 × 29 | left edge x 130, centre y 1030 | f400-f405 (out_cubic) | iris f551-f558 | static; ASH |
| U2 | `63%` / `64%` / … / `0%` | jw_mono | 72 | 132 × 53 (`64%`) | **right edge x 900**, centre y 1030 | f400 | iris f551-f558 | `63%` f400-f439, `64%` f440-f485, drain f486-f520: value = round(64 × (1 - in_cubic(u))), IVORY → RED below 20; `0%` RED f520-f550 pulsing ±15 % at 1.5 Hz. Bar: track x 130-900, y 1080-1094 (SMOKE), fill FLAME → RED gradient, width = value / 100 × 770 |
| U3 | `Saved` | ui.chip(size=36, h=76, look='dusk') | 36 | chip 184 × 76 | chip centre (780, 640); older chips shift up 92 px | each press + 2 f: f582, 602, 622, 642, 652, 662, 672, 682, 692, 702, 712 | each 0.9 s after its spawn, or when a 4th arrives; in_cubic 6 f; last gone by f719 | POP spring scale 0.85 → 1, newest `sel=1.0` (flame edge), older `sel=0`; max 3 visible |
| U3F | `Saved · har 30 sec` | ui.chip | 36 | chip 400 × 76 | (780, 640) | f712 (last chip) | f719 | fallback only (§6.7 F4) |
| K1 / K2 | `Ctrl` / `S` | 3D keycap legends (Poppins SemiBold shine-through) | cap height ≥ 40 on screen | n/a | Ctrl keycap centre (330, 1050) at 330 px wide; S keycap centre (720, 860) at 270 px wide | f561 (iris open) | f719 | pressed in 2D: +16 px down and ×0.985 in 2 f (in_cubic), hold 2 f, POP-spring release; legend flare 1.0 → 1.8 → 1.0 (impulse, decay 9); Ctrl leads S by 1 f |
| P1 / P2 | `BIJLI NE SIKHAYA` / `sabr` | jw_caps / jw_key | **86** / 260 | 792 × 60 / 419 × 187 | keyword centre (540, 520); caps centre y 318; underline y 707; ink incl. halo (125, 250)-(948, 783) (r2 proof) | t0 26.667 (f800) | out_t0 29.0 (gone by f880) | `J.HouseTitle('BIJLI NE SIKHAYA', 'sabr', caps_px=86, key_px=260).draw(cv, t, 540, 520, t0=26.667, out_t0=29.0)`: caps rise f800-f818, keyword rises per glyph from f807 (settled ~f824), underline f817-f838 |
| E1-E5 | `COMMENT MEIN` / `batao` / `Chhat ya candle?` / `@jawad_mp4` / `JD` | jw_caps 86 / jw_key 200 / jw_body 56 / jw_handle 34 / monogram | | 734 × 60 / 407 × 144 / 502 × 39 / 258 × 24 / ring Ø 240 | boxes (measured): caps 173-907 × 538-598, keyword 337-743 × 658-882, sub 289-791 × 945-985, handle 411-669 × 1563-1587, monogram 420-660 × 240-480 | f920 | f1029-f1039 | `E.EndCard(...)` §6.5 |

Margins: every line ≥ 40 px inside x 70-1010; the payoff caps are back at the house 86 px (r2: `BIJLI NE SIKHAYA` is
792 px, text box x 144-936, 144 px from each frame edge). Copy within 40 px of a safe-zone edge: the end-card monogram
ring top (y 240, 10 px below y 230; it is a mark, not copy) and the payoff caps' halo top (y 250, 20 px below y 230;
the caps' text box starts at y 288). No copy right of x 930 in y 1050-1700 (U2's right edge is 900).

### 6.7 VO beat plan (Vlad, `elevenlabs_v4`, Devanagari text; house Roman spelling for captions)

**Rate model (r2, GATE fix 1).** Windows are now laid at Vlad's **measured average pace after 1.10x: 4.95
syllables/s = 0.202 s per syllable** (SCRIPT §5, casting take), not at his fastest delivery (5.70 syl/s), so the
narrator never has to rush the twist, the Ctrl+S joke or the turn into the payoff. A faster take simply ends each
line earlier and the slack becomes pause. Per-line or per-beat takes (vo_config policy), each processed with
`vo_chain.py process` (speed clamp 1.00-1.10; pass the speed explicitly, SCRIPT §5), then placed at the start times
below on a 34.667 s VO track (re-normalised to -16 LUFS integrated). Lines may move by ±0.25 s to fit real word
timings (bible §5.5); bold targets may not move. After the takes, the scriptwriter's measured table (SCRIPT §4)
replaces these estimates. **Total: 65 words / 107 syllables (version A), 64 words / 104 syllables (B); cap 90.**

| id | Roman (captions) | meaning | window (s) | frames | words · syl | the picture that explains it |
|---|---|---|---|---|---|---|
| V1 (A) | Bijli chali gayi. | The power's gone. | **0.100**-1.300 (a matter-of-fact read of ≤ 1.20 s, SCRIPT §9; must end before the beep at 1.333) | 3-39 | 3 · 6 | brownout f10, CRT collapse f12-f15, H1 glows f15 |
| V2 (A) | Yaad hai? | Remember? | 2.200-**2.600**; fallback 1.550-≤ 2.000 between the beeps (§6.3, lead OK) | 66-78 (fallback 47-60) | 2 · 2 | torch on the blinking LED; beeps at f40, f60 |
| V1B (B) | Yeh awaaz... yaad hai? | This sound... remember? | **0.300**-1.950 | 9-59 | 4 · 5 | LED pulse + beep on f0; beep f40 in the "..." pause |
| V3a | Light jaati thi, | When the power used to go, | 3.000-4.000 (the start may move to 2.850) | 90-120 | 3 · 5 | the match lights the candle |
| V3b | toh poora mohalla chhat pe hota tha. | the whole neighbourhood was up on the roof. | 4.200-6.450, **"chhat" onset 5.350-5.450 (f160.5-f163.5, never before f160)** | 126-194 | 7 · 11 | tilt up through the ceiling (f140), rooftops (f160) |
| V4 | Jab wapas aati thi... | When it came back... | 6.600-**7.850** | 198-236 | 4 · 6 | rooftops waiting, bulbs dark; the far window false-starts at f220 under "...aati thi..."; ends ≥ 0.15 s before the f240 slam |
| V5 | Phir woh bachche bare hue. | Then those kids grew up. | 11.000-12.650 | 330-380 | 5 · 8 | the torch finds the homework copy, then the dead CRT |
| V6 | Kuch editor ban gaye. | Some of them became editors. | 13.150-14.600, **"editor" onset 13.367 (f401)** | 395-438 | 4 · 7 | on-word cut f400: lights on, the modern desk, render 63 %, the same edit as the CRT's |
| V7 | Aur bijli ban gayi sab se bari dushman. | And the power cut became the biggest enemy. | **16.400**-18.830 | 492-565 | 8 · 12 | monitor collapse, HUD drains 64 → 0 %, the dark desk, L8 closes |
| V8 | Har desi editor ki ungli khud Ctrl+S dabati hai. | Every desi editor's finger presses Ctrl+S by itself. | 18.950-22.390, **"Ctrl+S" onset inside f620-f640** (20.667-21.333: on the last quarter press at a fast pace, f629 at the average pace, f640 if the take allows) | 569-672 | 9 · 17 | Ctrl+S presses on quarters, then 8ths from f640; Saved chips |
| V9 | Har tees second. | Every thirty seconds. | 22.510-23.320 | 675-700 | 3 · 4 | the 8th presses and chips (last press f710) |
| V10 | Bijli ne humein editing nahi sikhai... | The power cuts didn't teach us editing... | 23.680-**26.300** ("Bijli" on the f720 cut when the take is ≤ 2.30 s; otherwise it pre-laps the cut by ≤ 0.33 s as a J-cut) | 710-789 | 6 · 13 | candle macro, then JD in profile by candlelight |
| V11 | sabr sikhaya. | they taught us patience. | 27.300-28.200, **"sabr" onset 27.333 (f820)** | 819-846 | 2 · 4 | `BIJLI NE SIKHAYA / sabr` + underline; the harmonium peak |
| V12 | Aap ke ghar light jaane pe kya hota tha? | What used to happen at your home when the power went? | 31.650-**34.100** | 950-1023 | 9 · 12 | end card `COMMENT MEIN / batao`, sub `Chhat ya candle?` |

Budgets at the average pace: rooftop block "chhat pe hota tha" + V4 = 11 syllables = 2.22 s of speech, plus a
0.15 s gap, inside the 2.50 s from "chhat" (≥ 5.35) to 7.85 (0.13 s spare); dense block V7-V10 = 46 syllables = 9.29 s of speech inside the 9.54 s
left between 16.400 and 26.300 after three 0.12 s gaps (0.25 s spare, which the windows give to the V9 → V10 breath);
the dense block also fits at 1.08x on the average take (9.47 s), so the maximum 1.10x is not needed. The V11 tokens
carry no leading "..." (the ellipsis sits on V10's last token, SCRIPT §3).

No VO at 8.0-10.667 (the slam and the cheer carry it), 14.6-16.4 (render ticking; the 0.4 s silence after f480 is
designed), 28.2-31.65 (power return, loudest moment). V12 ends ≥ 0.5 s before the seam; trim its tail to the
word end + 40 ms, rising pitch, no breath.

**Devanagari (hinglish-scriptwriter finalises in `script.json`; DEV and ROM must stay 1:1 token for token, `vo_chain`
raises otherwise):** V1 बिजली चली गई। · V2 याद है? · V1B ये आवाज़... याद है? · V3 लाइट जाती थी, तो पूरा मोहल्ला छत पे होता
था। · V4 जब वापस आती थी... · V5 फिर वो बच्चे बड़े हुए। · V6 कुछ एडिटर बन गए। · V7 और बिजली बन गई सब से बड़ी दुश्मन। (write
"सब से" as two tokens to match "sab se") · V8 हर देसी एडिटर की उंगली ख़ुद कंट्रोल-एस दबाती है। ("कंट्रोल-एस" is one token,
like जे-डी, to match the ROM token "Ctrl+S") · V9 हर तीस सेकंड। · V10 बिजली ने हमें एडिटिंग नहीं सिखाई... · V11 सब्र
सिखाया। · V12 आप के घर लाइट जाने पे क्या होता था? ("आप के" two tokens). The r2 trims (V4 drops और, V7 drops एडिटर की,
V8 drops इसलिए) cost 0 credits because T2 and T4 have not been generated; the V10/V11 spelling change is ROM-only (the
DEV text and take T5 do not change). **Pronunciation test before the full run (≈ 2.5 credits a take):** कंट्रोल-एस,
एडिटर, एडिटिंग, सेकंड, मोहल्ला, सब्र (must not come out as "sabar" stretched into two beats; accept सबर if ASR hears it
cleanly). Credit estimate for this reel: 7 takes + retakes ≈ 15-20 of the 187 remaining.

**Overrun ladder** (only if a measured take still runs past its window at 1.10x; apply in order; never move V7's
start or V10's end; the zero-credit trims T-a, T-b and the V7 trim are already in the copy, T-c is superseded): F1
`--speed 1.10` on V7-V10 · F2 inter-line gaps down to 0.12 s (the V9 → V10 breath first) · F3 V10 → "Bijli ne editing
nahi sikhai..." (a re-take of T5) · F4 drop V9 from the VO and show U3F `Saved · har 30 sec` as the last chip
(f712-f719). Report which step was used.

### 6.8 Transitions (catalogue ids from the bible §3; `jawad_tx` calls)

| cut | frame (s) | id | family | window (frames) | call | notes |
|---|---|---|---|---|---|---|
| hook → S2 | 80 (2.667) | L3 glue | light | push f80-f84 | hard cut inside the scene with `X.side_b(t, 80/30)`; push via `cuts=[(80/30, 0.5)]` | the match flare is the push; splice frame |
| S2 → S3 | 160 (5.333) | L3 glue | light | f160-f164 | `side_b` + `cuts=[(160/30, 0.25)]` | the tilt continues across the cut (S2 ends moving up in_cubic, S3 settles out_cubic); 5 samples f150-f170 |
| S3 → S4 | **320 (10.667)** | **L7 ★** light-beam sweep | light | **f308-f331** | `X.Plan` step `('L7', 320/30, dict(src=(540, -900), a0=-40, a1=40, width=2.2, haze=0.45, rays=0.0))` | the beam crosses frame centre on the bar-4 downbeat; 4 samples inside; cues whoosh_slow -6, shimmer -8 |
| S4 → S5 | 400 (13.333) | L3 glue | light | f400-f404 | `side_b` + `cuts=[(400/30, 0.8)]` | on-word cut 1 f before "editor"; lights on |
| S5 → S6 | **560 (18.667)** | **L8** aperture iris | light | **f551-f570**, closed on f560 only | `('L8', 560/30, dict(n=7, black=0))` | 7 flame-rimmed blades close on the dead desk, open on the keycaps. `black=0` (not the bible's 2) so only f560 is fully closed: SLATE keeps the hook blackout as the reel's only designed dip, and f560 sits inside a power-off stretch (tested: mean linear 0.0015 on f560, 0.014 on f559, 0.020 on f561). SLATE's "L8 iris for the CRT/monitor collapse" is read as: the collapses themselves are diegetic in-scene effects (§6.9) and L8 closes the collapse chapter; its cues fall inside V7 (to 18.830) and the V8 onset (18.950): camera_shutter -10, ui_click -14, reverse_swell -12 (override the defaults 0 / -8 / -8) |
| S6 → S7a | 720 (24.000) | L3 glue | light | f720-f724 | `side_b` + `cuts=[(720/30, 0.3)]` | power off again (keycap glow → candle) |
| S7a → S7b | 740 (24.667) | L3 glue | light | | `side_b` + `cuts=[(740/30, 0.2)]` | |
| S7b → S7c | 840 (28.000) | hard cut | | | `side_b`, no push | lockup continues over the cut (overlay) |
| S7c → S8a | **880 (29.333)** | **L4 ★** halation bloom-out | light | **f870-f889** | `('L4', 880/30)` (no options) | bloom k = sin²(πu); the candle flame (A, (540, 1240)) and JD's warm-lit face with the CRT rim behind it (B, centre x 540) share the frame centre; blacks never lift |
| S8a → S8b | 920 (30.667) | L3 glue | light | f920-f924 | `side_b` + `cuts=[(920/30, 0.3)]` | end card starts on the cut |
| f1039 → f0 | loop | loop push | | last 3 f | `card.post_kw` push + `cuts=[(0.0, 0.6)]` | |

Feature transitions: 3 (L7, L8, L4), 2 of them ★, spaced 3 and 4 bars apart (rule: ≤ 4, ≤ 2 ★, never two within
2 bars). In-shot light events (brownouts, CRT/monitor collapse, bulb cascade, power deaths) are scene content, not
transitions. **Plan:** `PLAN = X.Plan([L7, L8, L4 steps above])` with four scene functions `WORLD_A` (hook + S2 + S3,
valid for t up to 11.07), `WORLD_B` (S4 + S5), `WORLD_C` (S6 + S7a-c), `WORLD_D` (S8a + S8b with `E.loop_world`);
every other cut is made inside those functions with `X.side_b` (never pass `push_gain` to a Plan step:
SHARED_REQUESTS #1). Ownership: transitions and pushes are the timeline builder's; their SFX are in §6.10.

### 6.9 Light, camera and effect specs (so nothing is guessed)

- **Camera law:** `drift(t) = A(t) · (K.wiggle(t, 0.35, 7, 11), K.wiggle(t, 0.30, 5, 12), roll K.wiggle(t, 0.25, 0.5, 13))`
  px / degrees, applied as a `K.Cam` offset (planes parallax). A(t) ramps 0 → 1 over 15 f (inout_sine) after each
  power-off frame and 1 → 0 over 4 f (out_cubic) at each power-on frame. JD shot S7b caps the amplitude at 4 px / 0.3°.
- **Torch (2D):** operator off-frame bottom-right (1150, 2100). Hotspot = soft ellipse r 230 px, colour IVORY ×0.9 +
  AMBER ×0.25, ≤ 0.55 linear on lit surfaces; spill ring to 2.2 r at 15 %; volumetric cone from the operator to the
  hotspot at 6-10 % alpha; 60 dust motes (`J.embers(60, seed=21, bright=0.5)`) multiplied by the cone. Lit surfaces =
  plate `practicals` + cone mask ⊙ plate `lit` × 0.55; props = mix(`key_l`, `key_r`) by w_r = clamp((beam_x -
  prop_x) / 400 + 0.5) × beam mask at the prop. Paths (`K.Track`, inout_sine): hook A f20 (560, 600) → f24-f38 to
  (830, 1300); hook B f0 (830, 1300) → f30-f70 to (470, 1170); S4 f320 (160, 1345) → f340-f366 to (470, 1170).
- **Brownout / power-off:** multiplicative factor on mains-lit layers only (tube, bulbs, CRT image, monitor, room
  fill, `lit` pass weight): hook f10-f14 = 0.45, 0.80, 0.35, 0.15, 0.0; S5 f470-f472 = 0.6, 0.9, 1.0 (a dip only);
  f480-f482 = 0.4, 0.1, 0.0. Never brightens; never touches the LED, torch, candle or type.
- **CRT / monitor collapse:** phase 1 vertical size → **8 px** (in_cubic) while brightness × (1 + 1.5u), the line
  carrying an AMBER ×1.2 phosphor core (r2: the old 0.012 scale gave a 3 px line, too thin for the f14 floor, §6.3);
  phase 2 horizontal scale 1 → 0.02 (in_cubic) at 8 px tall; then a 12 px dot (AMBER ×2.5) decaying exp(-t / 0.35).
  Hook: phase 1 f12-f14, phase 2 f14-f15, dot from f15. S5 monitor (the whole card content, edit + viewer): f480-f483,
  f483-f485, dot from f485.
- **CRT image (2000s), drawn bold (r2, GATE fix 2):** a fictional edit (no real app, no text, no logo) that a phone
  viewer reads as "an edit" at 360 px, so the hook's screen dies *with something on it*. One `lru_cache`d function
  `crt_image(t, sx=1.0)` → a 340 × 240 sprite for the glass (screen quad x 300-640, y 1050-1290 = `crt_room`
  `screen_quad_frame`), added (emissive) inside the `screen_mask` pass. In glass px: background NIGHT_1 ×1.6; ruler
  y 14-30 with ASH ×0.55 ticks every 20 px (6 px tall, every 5th 12 px); **three clip tracks** y 40-88, 98-146,
  156-204 (**48 px tall each**, rule ≥ 36 px; 16 px at 360 px), lanes SMOKE ×1.2 over x 14-326; clip blocks with 6 px
  cut gaps, track 1 FLAME ×1.0 at x 14-92, 98-190, 196-250, 256-326; track 2 EMBER ×1.0 at 14-60, 66-170, 176-286,
  292-326; track 3 FLAME ×0.7 / EMBER / FLAME ×0.7 at 14-120, 126-214, 220-326; each block's top 3 px = half block
  colour + AMBER ×0.5 (the clip edge). **Playhead IVORY ×1.0, 6 px wide** (rule ≥ 6), y 14-204, with an 18 × 16 px
  head at the top; x = 14 + ((136 + 60 t) mod 312) on the frame-0 clock (x 150 at f0, 178 at f14; S8b reads it at
  t - DUR). Scanlines: every other row ×0.75; barrel vignette ×(1 - 0.30 r²). All values ≤ 1.0 linear (well inside the
  3× emissive cap). Same image under S1, S8 (lit) and as the dead-glass reflection base in S4. r2 proof on the real
  plate: `brief_proofs_r2/f00_room_lit_360.png`, `f09_room_lit_360.png` (the three tracks and the playhead read at
  360 px).
- **Modern monitor (S5), r2 (GATE fix 2):** `ui.glass_card(880, 520, r=28, look='dusk')` at (540, 700) (card x
  100-980, y 440-960). Left: **the same edit as the CRT**, `crt_image(t, sx=1.75)` without scanlines or vignette
  (same ruler, the same three 48 px tracks and block pattern stretched to 546 px wide) at x 128-688, y 590-830, its
  IVORY playhead **parked** where the CRT's playhead stood when it died on f14 (glass x 178 → monitor x ≈ 440; a render
  is running, nothing plays). Right: a **9:16 viewer** 236 × 420 at x 716-952, y 480-900 showing a pre-rendered still of
  the S3 rooftops (the editor is cutting this very memory). Desk lamp = 2D radial AMBER ×0.35 at (150, 200); desk
  surface SMOKE from y 1150. At f480 the whole card content collapses exactly as the CRT did, so the 16.0 s death reads
  as a callback to the hook. r2 proof `brief_proofs_r2/s5_monitor_14s_360.png`: edit and viewer read at 360 px.
- **Bulbs (S3):** 12 bare bulbs on stairwell walls and parapets; ignite far → near f240-f245 (2 per frame), local
  bloom core ≤ 3× linear; die near → far f300-f302 with one 1-frame relight on the nearest (darken-only overall).
- **Rooftops (S3), made to read at 360 px (r2, GATE fix 3):** 6 planes. Sky gradient NIGHT_0 → #171431 ×0.30 at the
  horizon plus **a warm dust-haze band behind the far skyline** (SMOKE ×2.0 linear at its peak, Gaussian σ 120 px
  centred about 30 px above the far roof tops, y ≈ 1010; warm, no moon, no cold blue), 80 star dots with 5 % twinkle;
  far skyline (roof tops y 1010-1065: water tanks, stairwell rooms, TV antennas) as flat NIGHT_0 against the band; mid
  roofs (tops y 1170-1230) NIGHT_1 ×0.5 with clotheslines; near parapet (top y 1500) with a charpai (top y 1440-1470),
  an adult sitting on it (head about (290, 1250)) and a child with a pankhi standing at the parapet (head about
  (720, 1335)). Silhouettes are flat NIGHT_0 SVG paths (`ui.parse_path` + `ui.fill_mask`) with a **2 px AMBER ×0.9
  rim on the candle side**; bare heads, no religious or national markers. 8 parapet candles (flame core AMBER ×2.6)
  never go out and each lights **a warm pool** on the surfaces around it (Gaussian, AMBER, linear peak): near candles
  on the parapet top ×0.30 (rx 230, ry 34 px) and the wall face below ×0.18 (rx 160, ry 90), the one by the charpai
  on its woven top ×0.30 (rx 200, ry 60); mid candles on their parapet faces ×0.16 (rx 110, ry 45). Silhouettes stay
  in front of the pools (dark, rim only). r2 stand-in, finished, measured at 360 px (`f219_rooftops_360.png`): sky
  band just above the far tops (y 945-996) mean luma 33.3 (full range) against far roofs 1.2 and the child's body 2.0;
  YAVG 26.8 (limited); 54,006 px above luma 90; red-orange 99.7 % of saturated pixels, violet 0.05 %, top-5 % 98.4 %.
- **Far-window false start (S3, f220-f222), r2 (GATE fix 3):** one window of a far stairwell room, 22 × 30 px, centred
  about (330, 1040) (left of centre, across the frame from the child, so the head turn reads), NIGHT_0 until f219;
  **f220 and f221 IVORY ×0.9** with `K.glow(sigmas=(4, 12), strength=0.8)`, identical on both frames (snapped on, no
  fade-in); **f222 dark again** (no fade-out, no afterglow); it stays dark until f240, when it lights with the distant
  windows (IVORY ×0.4). The near child's head path changes from three-quarter back to a profile facing screen-left
  over f224-f230 (out_cubic morph of the SVG path) and holds until f300. The camera keeps drifting (the power is still
  off). Mean frame luma rises by ≤ 1 code value on f220-f221 (r2 proof: 12.6 → 12.8, full range).
- **Candle flame (S2, S7):** procedural 2D teardrop (core AMBER ×2.6, edge FLAME, soft halo), height 150 px (macro)
  / 70 px (S7b); sway from `K.wiggle` at 1.5 / 4 Hz (amp 3° / 1°), flicker ±8 % brightness, no frame-to-frame boiling;
  anchored on the candle asset's `wick_tip` feature. Light from the flame = a radial warm pool (AMBER, falloff r 600).
- **Tilt through the ceiling (f140-f170):** S2's frame translates down 900 px over f140-f159 (in_cubic) past a dark
  ceiling slab (NIGHT_1) with the dead fan's silhouette rim-lit by the candle below; the candle glow stays in the
  bottom 15 % of frame until f159 and the S3 stars and parapet candles are visible from f160 (so no frame is empty);
  S3 continues the same downward screen motion: its content starts 300 px high (offset -300 px) and settles down to
  0 out_cubic over f160-f180. 5 samples f150-f170.
- **Candle sparks (S7b):** `J.embers(20, seed=31)` emitted at the flame, each rising ≤ 280 px and fully faded before
  y 850, so none reaches the payoff lockup (ink ends at y 783) or crosses JD's face box.
- **Ceiling fan:** 2D sprite (3 dark wood blades, hub, down-rod) hub at (540, 60), rotation with 5-sample blur
  while > 1 rev/s; speed 4.5 rev/s lit, decays τ 1.0 s after a power-off, spins up over 2.5 s (out_cubic) after a power-on.
  r2, so it reads at 360 px on the lit frames: blades are dark silhouettes against the tube-lit ceiling (colour NIGHT_1
  + #3B2A22 ×0.12, 2 px AMBER ×0.10 underside edge from the tube), blade plane radius 445 px flattened to ×0.30
  vertically, tip width 64 px, hub Ø 72 px, down-rod NIGHT_1 x 532-548, y 0-60; the render's own 5 samples at the 180°
  shutter smear each blade 27° at 4.5 rev/s and the three stay distinct (r2 proof f0 / f9 at 360 px).

### 6.10 SFX cue list (sound-designer; `bijli_chali_gayi_sfx.py`, built with `--no-sfx-build` per TOOLKIT §11.14)

All cues `align='hit'` unless marked start. Gains are before `fit_under_vo` (bible §4.1), which the module runs on
the VO words (in VO windows: -6 dB, MID -2 more, AIR `hp` 5500, DARK `lp` 1100). Validated: every name is in
`audio.names()` (after `epic_sfx.register()`) or in the custom list below; ≤ 3 sounds start on any instant;
nothing starts inside the drop-out; hook-only cues end before f80. 90 cues (r1 count; r2 adds the f220 hum blip)
= 2.6 events/s with the keycap percussion (33 cues), 1.6/s without it: denser than the bible's 0.6-1.0/s on purpose (no music bed; the detail cues
sit at -12 to -16 dB). Each hook version is mixed in full (no audio splice): mixes share every body cue.

| t (s) | f | name | params | gain dB | align | version | note |
|---|---|---|---|---|---|---|---|
| 0.000 | 0 | impact_soft | lp 900 | -8 | hit | A | f0 transient = the loop landing |
| 0.000 | 0 | backup_beep |  | 0 | hit | B | f0 transient |
| 0.333 | 10 | tube_flicker |  | -12 | hit | A | brownout |
| 0.400 | 12 | crt_off |  | -8 | hit | A | CRT collapse |
| 0.467 | 14 | relay_click |  | -10 | hit | A | backup box switches to battery |
| 0.467 | 14 | fan_wind | mode down, duration 3.0 | -14 | start | A | ceiling fan winds down |
| 0.500 | 15 | shimmer | hp 5500 | -12 | hit | A | keyword glows |
| 0.667 | 20 | mouse_click |  | -10 | hit | A | torch click |
| 1.333 | 40 | backup_beep |  | 0 | hit | A, B | beat 2 |
| 2.000 | 60 | backup_beep |  | 0 | hit | A | beat 3 (cover) |
| 2.667 | 80 | match_strike |  | 0 | hit | A+B | ignition on the splice cut |
| 3.333 / 4.000 / 4.667 | 100 / 120 / 140 | leaf_rustle |  | -14 | hit | A+B | pankhi swings |
| 5.333 | 160 | whoosh_slow | lp 1100 | -10 | hit | A+B | tilt, loudest pass on the cut |
| 7.333 | 220 | tube_flicker | lp 250 | -24 | hit | A+B | r2: the far window's false start, a low 100 Hz hum blip only (under V4: nothing added in 1-4 kHz, §8) |
| 8.000 | 240 | power_thunk | on 1 | -3 | hit | A+B | power back |
| 8.000 | 240 | impact_soft |  | -4 | hit | A+B | AA GAYI! slam |
| 8.033 | 241 | crowd_cheer_real | cue dur 1.967 | -10 | hit | A+B | wordless CC0 cheer (SLATE: about -10 dB), cut dead at 10.000 |
| 8.067 | 242 | fan_wind | mode up, duration 1.9 | -12 | start | A+B | rooftop fans |
| 8.100 | 243 | tube_light_on |  | -12 | hit | A+B | distant tube lights |
| 10.000 | 300 | power_thunk | on 0 | -2 | hit | A+B | dies again (gag) |
| 10.033 | 301 | fan_wind | mode down, duration 2.0 | -14 | start | A+B | |
| 10.333 | 310 | backup_beep | far 1 | -8 | hit | A+B | distant beep from downstairs |
| 10.667 | 320 | whoosh_slow / shimmer |  | -6 / -8 | hit | A+B | `PLAN.cues()` L7 |
| 12.667 | 380 | backup_beep |  | -6 | hit | A+B | the box in the room (between V5 and V6) |
| 13.333 | 400 | power_thunk | on 1, lp 1100 | -6 | hit | A+B | lights on (on-word cut) |
| 14.667 | 440 | ui_tick |  | -12 | hit | A+B | 63 → 64 % |
| 15.667 | 470 | tube_flicker |  | -14 | hit | A+B | brownout dip |
| 16.000 | 480 | power_thunk | on 0 | 0 | hit | A+B | re-hook 2 |
| 16.000 | 480 | crt_off |  | -6 | hit | A+B | monitor collapse |
| 16.000 | 480 | sub_drop | lp 120 | -6 | hit | A+B | re-hook weight |
| 16.033 | 481 | fan_wind | mode down, duration 1.5 | -16 | start | A+B | PC fans |
| 16.200 | 486 | slot_tick | n 10, dur 1.133, hp 5500 | -16 | start | A+B | HUD drains |
| 18.633 / 18.700 / 19.033 | 559 / 561 / 571 | camera_shutter / ui_click / reverse_swell (0.3) |  | **-10 / -14 / -12** | hit | A+B | `PLAN.cues()` L8, gains overridden (inside V7 / the V8 onset) |
| press − 1 f | 579, 599, 619, 639, 649, 659, 669, 679, 689, 699, 709 | keycap_thock | pitch 0.94 | -8 | hit | A+B | Ctrl down |
| press | 580, 600, 620, 640, 650, 660, 670, 680, 690, 700, 710 | keycap_thock | pitch 1.0 | -6 | hit | A+B | S down (quarters, then 8ths from f640) |
| press + 2 f | 582 … 712 | ui_tick | hp 5500 | -16 | hit | A+B | Saved chip |
| 24.000 | 720 | impact_soft | lp 900 | -10 | hit | A+B | cut to the candle |
| 26.667 | 800 | impact_soft |  | -2 | hit | A+B | payoff lockup lands (velvet hit) |
| 26.667 | 800 | heartbeat | n 1 | -8 | hit | A+B | velvet hit |
| 27.333 | 820 | harmonium_swell | duration 0.926, notes (50, 57, 62, 66) | -6 | hit (= peak) | A+B | starts f800; peaks on "sabr"; in mix FULL only, omitted in mix DRY |
| 27.217 | 817 | swish_small | hp 5500 | -16 | start | A+B | underline draws on |
| 29.333 | 880 | riser | duration 1.2 | -8 | hit (ends) | A+B | starts 28.133 |
| 29.333 | 880 | power_thunk | on 1 | 0 | hit | A+B | **power returns (loudest)** |
| 29.333 | 880 | sub_drop | lp 120 | -3 | hit | A+B | |
| 29.333 | 880 | shimmer / reverse_swell (0.333) |  | -8 / -6 | hit | A+B | `PLAN.cues()` L4 |
| 29.367 | 881 | impact_soft |  | -2 | hit | A+B | |
| 29.367 | 881 | fan_wind | mode up, duration 2.5 | -6 | start | A+B | ceiling fan spins up |
| 29.400 | 882 | tube_light_on |  | -8 | hit | A+B | tube strikes |
| 29.433 | 883 | crt_on |  | -8 | hit | A+B | CRT degauss |
| 29.500 | 885 | crowd_cheer_real | cue dur 1.6 | -8 | hit | A+B | the neighbourhood cheers again (wordless); louder than at 8.0 so f880-f898 stays the reel's peak |
| 30.767 / 31.237 / 31.417 | 923 / 937 / 943 | swish_small (start) / shimmer / glass_tap |  | -12 / -10 / -12 | | A+B | `card.cues(T_END, DUR)` as returned (tuning glass_tap to D6 1174.7 Hz is optional, bible §4.2) |
| 34.667 | 1040 | reverse_swell | duration 0.8 | -8 | hit (ends) | A+B | `card.cues()`: ends on frame 0 |

Use `PLAN.cues()` and `card.cues()` as they are (gains above) except the L8 overrides; there are no L3 entries in
the Plan, so no `flash_hit` anywhere (C11 is diegetic).

**V1 intelligibility (r2, GATE minor 9):** six onsets sit under V1 (tube_flicker, crt_off, relay_click, fan_wind,
shimmer, the torch click, 0.333-0.667 s), and the median "speech ≥ 8 LU" check cannot catch a masked first word. On
mix A FULL, faster-whisper `hi` must return बिजली चली गई inside 0-1.3 s with every word at probability ≥ 0.5; if not,
pull crt_off's 3-9 kHz static and the relay_click down 4 dB and re-check.

**Beds** (a `BED` list; every segment gets `'offset': t0` so a bed split into windows stays phase-continuous; mix
with `A.mix(cues, DUR, bed=BEDS, target_lufs=-18.0, tp_ceiling=-2.0, split_stems=True, tail_fade=0.0)`: the default
`tail_fade=0.4` would fade the loop):

| name | t0-t1 (s) | gain dB | fade | version |
|---|---|---|---|---|
| room_mains | 0.000-0.333 / 0.333-0.367 / 0.367-0.400 / 0.400-0.433 / 0.433-0.467 | -24 / -32 / -26 / -34 / -30 | 0.004 | A |
| night_crickets | 0.000-0.467 · 0.467-2.667 | -38 · -32 | 0.004 (the +6 dB step hides under the relay click and the fan wind-down) | A |
| night_crickets · room_tone | 0.000-2.667 | -32 · -34 | 0.004 | B |
| night_crickets · room_tone | 2.667-5.333 | -32 · -34 | 0.004 (continues across the splice) | A+B |
| night_crickets · night_air | 5.333-10.667 | -24 · -30 | 0.05 | A+B |
| room_tone · night_crickets | 10.667-13.333 | -34 · -32 | 0.1 | A+B |
| edit_suite | 13.333-16.000 | -28 | 0.004 | A+B |
| room_tone | 16.000-18.667 | -36 | 0.004 | A+B |
| edit_suite | 18.667-24.000 | -30 | 0.05 | A+B |
| room_tone · night_crickets | 24.000-26.333 | -32 · -32 | 0.004 | A+B |
| room_tone (held breath of the drop-out) | 26.333-26.667 | -48 | 0.004 | A+B |
| room_tone · night_crickets | 26.667-29.333 | -32 · -34 | 0.004 | A+B |
| room_mains · night_crickets | 29.400-34.667 · 29.333-34.667 | -24 · -38 | 0.004 | A+B |

**Custom sounds** (register idempotently into `A.SOUNDS` from `bijli_chali_gayi_sfx.py`, built on audio.py /
epic_sfx helpers, each passing `A.qc(...) == []` with a spectrogram check; nothing sampled from a song):

| name | hit | level | recipe |
|---|---|---|---|
| backup_beep(far=0) | onset of pulse 1 | -8 | two 70 ms sine pulses at 2349.3 Hz (D7) + 3rd harmonic -20 dB (piezo), 4 ms raised-cosine edges, pulse 2 onset +0.133 s; `reverb('room', -26)`; far=1: lp 2600 + `reverb('room', -14)` |
| match_strike | ignition (0.06 s) | -6 | 55 ms sandpaper scratch (`_grains` 2-7 kHz) → ignition crackle burst + noise_band flare 900 → 2800 Hz (0.25 s) + low whoomp (`_thump` 90 Hz, 40 ms) + sizzle tail (`_crackle` rate 300, 2-8 kHz, 0.5 s) |
| relay_click | 0.0 | -10 | `_click` 2-6 kHz τ 1.5 ms + `_thump` 120 Hz 15 ms |
| power_thunk(on=1) | 0.0 | -4 | `_thump` 55 Hz 50 ms drive 2 + mechanical click 1.5-5 kHz; on=1 adds a 100 + 200 Hz hum swell (0.15 s up, settles -18 dB over 0.6 s); on=0 adds a hum falling 100 → 60 Hz, dead in 0.25 s |
| crt_off | 0.0 | -6 | "thoomp" `_thump` 70 Hz 60 ms + static burst `_crackle` 3-9 kHz 0.12 s + the 15.625 kHz line whine (-30 dB) that stops at the hit (0.15 s pre-roll) |
| crt_on | 0.0 | -8 | degauss thunk `_thump` 60 Hz 40 ms + 50/100 Hz hum "bwong" decaying 0.45 s + static "tsss" noise_band 5 kHz 0.35 s + whine at -30 dB |
| tube_light_on | the lighting click | -10 | two starter "tinks" 0.18 s apart before the hit (modal pings 2.1 kHz τ 20 ms), then a 100 Hz buzz settling to -20 dB |
| tube_flicker | 0.0 | -12 | three 25 ms buzz stutters (100 Hz + harmonics), 40 ms apart |
| fan_wind(mode, duration) | start | -12 | noise_band 250-800 Hz amplitude-modulated at the blade-pass rate (3 blades × 4.5 rev/s = 13.5 Hz; down: exponential to 0 with τ = duration / 3; up: 0 → 13.5 Hz out_cubic over duration) + motor hum 100 Hz at -24 only while powered |
| keycap_thock(pitch) | 0.0 | -6 | `keyboard_burst(n=1)` (epic_sfx mechanical "thock") + `_thump` 160 Hz 25 ms body, resampled by pitch |
| room_mains (bed, 8 s loop) | bed | bed | fan_wind run (13.5 Hz AM, exactly 108 cycles per loop) + tube buzz 100 Hz -30 + CRT whine 15.625 kHz -42 + `room_tone`; seamless |
| night_crickets (bed, 20 s loop) | bed | bed | 6 field-cricket voices: 4.2-4.9 kHz sine carriers, chirps of 3-4 pulses (18 ms on, 30 ms period) at 1.8-3.0 chirps/s, slow detune drift, pans -0.7 … 0.7, distance lp; + `night_air` at -10 rel; seamless |

### 6.11 Music plan (music-supervisor)

- **Style: none.** No `epic_music` style, no score.py bed, no beat bed, no tape-stop (C26 owns it). SLATE §3.2 binds
  C11 to a diegetic bed; the 90-BPM grid is carried by the beeps (beats 2 and 3 of bar 0), the keycap percussion
  (quarters in bar 7, 8ths in bar 8) and the fan blade-pass.
- **The one desi voice:** `harmonium_swell(duration=0.926, notes=(50, 57, 62, 66))` = D3 A3 D4 F#4 (D major, Sa = D,
  146.83 Hz), cued with its peak on f820 so it starts exactly at the end of the drop-out (f800). Key of the reel = D:
  backup_beep at D7, end-card glass_tap pitched to D6 (bible §4.2 `pitch_to`).
- **Sections (bars):** 0 hook (mains hum → silence → crickets) · 1-2 candle and rooftops (crickets, night air) ·
  3 power back (appliance chorus, cheer) · 4 the old room (room tone) · 5 edit suite hum · 6 dead room (re-hook) ·
  7-8 keycap rhythm · 9 candle (room tone) · 10 **drop-out f790-f799** then harmonium + velvet hit · 11 **power returns
  (loudest)** · 11.2-13 end card (mains hum, reverse swell into frame 0).
- **Mixes:** mix FULL = VO stem + SFX stem (with the harmonium); mix DRY = VO + SFX without the harmonium (an in-app
  nostalgic track may enter at 29.333 s at 10-20 % on the platform side). Files: `RWS/audio/bijli_chali_gayi_mix_A_full.wav`,
  `_mix_A_dry.wav`, `_mix_B_full.wav` (48 kHz 24-bit) + stems `_vo_A.wav`, `_vo_B.wav`, `_sfx_A.wav`, `_sfx_B.wav`. Final -14 LUFS ±0.5, TP ≤ -2.0 dBTP,
  speech ≥ 8 LU above the SFX/bed stem (median over voiced frames), SFX in VO windows ≥ 6 LU below speech. Name the
  audio "Original audio · Bijli chali gayi · @jawad_mp4".

### 6.12 3D props (blender-3d-artist; builder `pipeline/jawad_reels/assets3d_bijli_chali_gayi.py`)

Spec: Blender 5.2 bpy, Cycles CPU, `threads = 2`, run through `heavy.sh`; view transform **Standard**, look None,
gamma 1; PNG RGBA 8-bit straight alpha sRGB (sprites3d spec); mode `static`, one folder `passes/`, frames in the
order of `labels` in meta.json, `H.write_meta` for anchor / bbox / features. Samples: lit passes 96 (room) / 128
(macro) adaptive (threshold 0.02) + OpenImageDenoise, fixed seed; `emit` and `screen_mask` passes 1 sample,
emission only, no denoise. Root `RWS/assets3d/`; load with
`S3.Asset3D(name, 'passes', root=RWS + '/assets3d').by_label('key_l')`. Preview sheet first (`--preview`, 16 spp,
half res), then finals. Budget ≈ 26 PNGs, 45-60 min on 2 threads. Hex below are sRGB; convert to linear for
Blender (`K.hexlin`): e.g. SMOKE (0.0232, 0.0103, 0.0075), FLAME (1.0, 0.1441, 0.0103), AMBER (1.0, 0.4621, 0.063),
IVORY (1.0, 0.8963, 0.7913), ASH (0.3916, 0.3095, 0.2623).

**CAM_ROOM** (shared by `desk_plate`, `crt_room`, `tower_room`, `box_room`): 28 mm, sensor 36 mm fitted vertically,
1080x1920, eye-level slightly above the table looking at the back wall. Screen-space targets (verify with a box
overlay, tolerance ±20 px): ceiling slab y 0-230 (fan down-rod mount at (540, 0-40)); tube-light fixture x 90-380,
y 250-275; window with iron grille x 720-1010, y 300-900 (sky card #171431 at low strength, no moon); blank
switchboard x 120-250, y 760-900; table top front edge y 1380, apron to 1500; **CRT body x 250-690, y 1010-1380,
glass x 300-640, y 1050-1290**; **backup box on the table x 760-960, y 1230-1380, LED at (800, 1265)**; tower on the
floor under the table x 740-960, y 1520-1900; homework copy (kraft-brown cover AMBER ×0.4, open, ruled pages, no
legible text) on the table x 70-240, y 1310-1380; floor from y 1700. These positions keep the hook lockup (y
283-809) and the raised end card (y 240-985) over plain wall (proofs `p1`, `p7`).

| asset | camera | size | passes (`labels`) | features (meta) | materials (brand palette) | used in |
|---|---|---|---|---|---|---|
| desk_plate | CAM_ROOM | 1080x1920, opaque | `lit` (tube-light area light at the fixture, IVORY; faint CRT spill AMBER; window spill #171431), `practicals` (only a 0.5 W FLAME point at the LED; near-black) | tube_xy, crt_slot, box_slot | wall = lime-wash mix(SMOKE, ASH, 0.35) with stains; ceiling NIGHT_1; table dark teak mix(NIGHT_1, EMBER, 0.15) with water rings; grille NIGHT_0 paint; switchboard mix(ASH, IVORY, 0.3), dirty, blank | S1, S4, S8 |
| crt_room | CAM_ROOM, saved cropped to alpha bbox + 24 px | crop | `room` (plate's lit rig + shadow catcher), `key_l`, `key_r` (torch: one spot 35° above, cone 25°, soft r 0.05 m, IVORY ×0.85 + AMBER ×0.15, from screen-left / screen-right), `screen_mask` (glass area, white emission), `emit` (power LED FLAME) | frame_xy (crop top-left in the 1080x1920 frame), screen_quad (4 corners) | housing aged dark warm plastic #3B2A22 roughness 0.55 + fine noise bump, vents; bezel SMOKE; glass #0C0807 convex 6 mm, roughness 0.04, coat 1.0 | S1, S4, S8 |
| tower_room | CAM_ROOM, cropped | crop | `room`, `key_l`, `key_r`, `emit` (HDD LED RED) | frame_xy | body SMOKE, bezel NIGHT_1, 5.25" tray #3B2A22, floppy slot, power-button ring; no logos | S1, S4, S8 |
| box_room | CAM_ROOM, cropped | crop | `room`, `key_l`, `key_r`, `emit` (LED FLAME, ≤ 3× linear) | frame_xy, led_xy | matte powder-coated metal #120C0A roughness 0.6, side vents, rocker switch, one round LED, rubber feet; **no text, no logo, no UPS/inverter marks** | S1, S4, S8 |
| pankhi | 85 mm, front 3/4 (yaw 20°), object-centred | 900x1100 | `key_l` (candle side), `key_r` | pivot (handle end), anchor | woven straw leaf Ø 300 mm: two-tone weave AMBER ×0.55 and EMBER bands, RED fabric piping, bamboo handle 250 mm mix(NIGHT_1, AMBER, 0.25); no motifs or symbols | S2 |
| candle | 100 mm macro, 8° above, object-centred | 600x1400 | `self` (point light at the wick tip +12 mm, AMBER, r 4 mm: lights its own wax), `key_l`, `key_r` | wick_tip, base | paraffin IVORY, SSS weight 0.6 radius (1.0, 0.45, 0.25) scale 0.004, drips, charred 2 mm wick NIGHT_0; steel saucer ASH metallic roughness 0.35 with a wax pool | S2, S7a-c |
| keycap_ctrl | 100 mm macro, 35° above, yaw 15° | 900x900 | `key_l`, `key_r` (soft warm top light = monitor glow from left / right), `emit` (legend shine-through FLAME) | legend_centre, contact | OEM profile 1.25u, PBT #0E0908 roughness 0.45 fine texture; legend "Ctrl" Poppins SemiBold, engraved #2A1A15 in key passes | S6 |
| keycap_s | same camera as keycap_ctrl | 900x900 | `key_l`, `key_r`, `emit` | legend_centre, contact | OEM profile 1u, same material; legend "S" | S6 |

Done when: every pass exists with meta.json written last; a contact sheet of all passes is Read and checked
(no text or logos on props, LEDs not clipped to white, palette held, room props land on the targets ±20 px).

### 6.13 Face plan (face-compositor; `pipeline/jawad_reels/bijli_chali_gayi_faces.py`)

```python
FACES = [
  dict(t0=740/30, t1=840/30, pose='suit_profile', P=(440, 1210), width=710,   # eye_mid on screen, scale 1.0
       cam_keys='drift amp 4 px / 0.3 deg (power off)', rim_dir=(0.85, -0.15), rim_gain=2.0, look='A',
       swap_on_beat=False, note='faces screen-right toward the candle flame at (800, 1130); candle light = soft '
       'horizontal gradient multiply 0.55 (back of head) -> 1.0 (face front) + warm tint (1.0, 0.86, 0.70) on the lit '
       'side; never a depth relight; FA.fade_open(); FA.idle(seed=5)'),
  dict(t0=880/30, t1=920/30, pose='suit_smiling', P=(540, 1150), width=710,
       cam_keys='locked (power on)', rim_dir=(-0.6, -0.8), rim_gain=2.4, look='A', swap_on_beat=False,
       note='appears on the L4 cut (no dissolve); tube light top-left key, CRT glow behind the head as rim; '
       'FA.fade_open(); FA.idle(seed=6)'),
]
```

Measured (proof `p5`, `p6`): profile bust bottom y 1930 (≥ 1920), head box (159, 846, 571, 1506), face box (222, 1069,
508, 1473); smiling bust bottom y 1936, face box (333, 984, 681, 1410). On screen 3.33 s and 1.33 s (≤ 3.5 s). Rim
look A (`FA.rim_light`) for both (hero shots); no cine look D in this reel (there is no narration shot of JD). One
wardrobe (suit), no mirroring, no lip-sync, skin natural (human-realism / photo-realism), halo ≤ +6 code values,
eye position ±6 px of P. No prop, spark or text crosses either face (the payoff lockup ends at y 783, above the
profile head top y 846).

### 6.14 Captions (`snake_captions.py`, inside the module; caption-designer checks)

```python
cap = SC.Captions(RWS + '/vo/bijli_chali_gayi_vo_A.words.json', band='auto', avoid=avoid_at, white_px=64,
                  key_px=128, hide=[(0.0, 80/30), (800/30, 880/30), (920/30, DUR)])
```
- Words JSON from `vo_chain` in reel time (the assembled VO track, offset 0). Version B uses `_vo_B.words.json`; the
  hook window is hidden in both, so the body captions are identical across versions.
- Hidden: the hook (designed text carries it), the payoff V11 (the lockup shows *sabr*), the end card V12 (the card
  shows the CTA). No VO in 8.0-10.7, so the slam never shares the screen with a caption.
- Keywords (`*word` in the ROM tokens of `script.json`; one per line, as the script gate accepted, r2): V3a *Light* ·
  V3b *chhat* · V4 *wapas* · V5 *bachche* · V6 *editor* · V7 *dushman* · V8 ***khud*** (r2, GATE minor 6: the glow sits
  on the spoken stress; *Ctrl+S* is already on the keycaps, so it stays white) · V9 *tees* · V10 *editing*. V10's
  caption reads "...editing nahi sikhai..." (r2 spelling); V11 is hidden behind the lockup.
- `avoid_at(t)` (rects in px): S2 2.667-5.333 → (60, 1150, 1020, 1660) and the flame (440, 780, 640, 1020) (captions go
  to the upper band) · S3 5.333-8.0 (r2) → the far window (290, 995, 370, 1085) and the child's head + pankhi (650,
  1280, 870, 1430), so the f220 tease and the head turn are never covered · S4 10.667-13.333 → CRT (250, 1010, 690, 1380) · S5 13.333-18.667 → monitor (100, 440, 980,
  960), HUD (110, 990, 920, 1110) · S6 18.667-24.0 → Ctrl (165, 900, 495, 1200), S (585, 720, 855, 990), chips (600,
  380, 960, 720) · S7a 24.0-24.667 → flame (380, 600, 700, 1300) · S7b 24.667-28.0 → JD head (159, 846, 571, 1506),
  candle (700, 1040, 900, 1560). Proofs `p3`, `p4` show chunks clear of the HUD and keycaps.
- `cap.check() == []`; `cap.save_srt(RWS + '/captions/bijli_chali_gayi_A.srt')`; house spelling of
  `prior/captions_roman_urdu.srt` (bari, nahi, hai; sentence case).

### 6.15 Cover, IG post, AI label

- **Cover:** the frame-60 (2.000 s) composition of version A: torch beam, glowing `Bijli / CHALI GAYI.`, LED
  mid-pulse; keyword inside the 3:4 crop (lockup y 283-809 incl. halo). **r2 (GATE minor 7): a dedicated still, not
  the master frame**, because H1 has settled to 0.75 opacity by f60: the module honours `JAWAD_C11_COVER=1` (H1 at
  1.0, everything else exactly as f60); render it with `JAWAD_C11_COVER=1 tools/heavy.sh python3 render.py
  bijli_chali_gayi --stills 2.0 --workers 1 --jpg` and the delivery-packager writes it over the `_cover.jpg` that
  `package.py` extracts from the master. The indigo window (x 720-1010, y 300-900) stays low beside the keyword: mean
  luma ≤ 10 (full range) in the cover (r2 proof on the real practicals plate: 7.8), never lifted, so the grid reads
  flame-on-black, not violet.
- **Caption line 1 (49 characters):** `Bijli chali gayi: har video editor ki pehli class`
- **Body:** 2-3 short lines restating "Bijli ne humein editing nahi sikhai, sabr sikhaya." (no claims; r2 house
  spelling).
- **Hashtags (4):** #videoediting #nostalgia #editorlife #jawadmp4
- **Comment prompt (pinned):** "Aap ke ghar light jaane pe kya hota tha? Chhat ya candle?"
- **AI label:** turn "AI info" on (synthetic voice; the character-sheet imagery may be AI-generated) - SLATE §7.1
  default, applied to both versions.
- **Audio name:** "Original audio · Bijli chali gayi · @jawad_mp4".

## 7. Engineering contract

- **Files (this reel only):** `pipeline/jawad_reels/bijli_chali_gayi.py` (timeline; motion-timeline-builder),
  `bijli_chali_gayi_faces.py` (face-compositor), `bijli_chali_gayi_sfx.py` (sound-designer),
  `bijli_chali_gayi_music.py` (music-supervisor: final mixes A FULL, A DRY, B FULL), `assets3d_bijli_chali_gayi.py` (blender-3d-artist).
  Shared modules are read-only (jawad_kit, jawad_grade, jawad_tx, snake_captions, endcard, vo_chain, core, type3d,
  ui, audio, render, sprites3d, demo_foundation, TOOLKIT.md).
- **Module contract:** `import jawad_kit` first; then `jawad_grade as G`, `jawad_tx as X`, `endcard as E`,
  `snake_captions as SC`, `sprites3d as S3`, `bijli_chali_gayi_faces as BF`. `DUR = 1040 / 30`, `LOOK = 'dusk'`,
  `BPM = 90`, `HOOK = os.environ.get('JAWAD_C11_HOOK', 'A')`. `draw(t)` pure: `cv = PLAN.draw(t, [WORLD_A, WORLD_B,
  WORLD_C, WORLD_D])`, then overlays that span cuts (payoff lockup), then `cap.draw(cv, t)`, then `card.draw(cv, t,
  T_END)`. `post(cv, t)`: `kw = PLAN.post_kw(t); kw['push'] = kw.get('push', 0.0) + card.post_kw(t, T_END,
  DUR).get('push', 0.0); return G.tx_finish(cv, t, LOOK, cuts=CUTS, **kw)` with `CUTS = [(0.0, 0.6), (80/30, 0.5),
  (160/30, 0.25), (240/30, 0.5), (400/30, 0.8), (720/30, 0.3), (740/30, 0.2), (920/30, 0.3)]`. `samples(t)`:
  `max(PLAN.samples(t), 5 if t is in f0-f9 (fan blur), f150-f170 (tilt), f240-f246 (bulbs) or f880-f900 (fan spin-up)
  else 3)`. `cues()` and `BED` come from `bijli_chali_gayi_sfx` (render with `--no-sfx-build --audio <mix>`).
  `prewarm()` builds every static sprite (type, chips, HUD frames, CRT image, rooftop layers, faces, end card,
  captions) in `lru_cache`d functions.
- **Outputs:** before the first render, `ln -sfn RWS/out WS/out/bijli_chali_gayi` so render.py's `<WS>/out/<reel>/`
  lands in RWS; audio in `RWS/audio/`; VO in `RWS/vo/`; 3D in `RWS/assets3d/`.
- **Commands (all through heavy.sh, from `pipeline/jawad_reels`):**
  - gate stills (r2 adds f0, f9, f15, the rooftops, the f220 tease and the S5 monitor): `tools/heavy.sh python3
    render.py bijli_chali_gayi --stills 0.0,0.3,0.5,2.0,6.5,7.3334,8.1,14.0,16.1,27.6,29.4,33.0 --workers 1`
    (7.3334 lands on f220 under floor or round), then save a 360 × 640 INTER_AREA copy of each still and Read those too.
  - sheet: `tools/heavy.sh python3 render.py bijli_chali_gayi --sheet 16 --samples 1 --workers 1`
  - hook B: `JAWAD_C11_HOOK=B tools/heavy.sh python3 render.py bijli_chali_gayi --range 0 2.6667 --no-audio`, move
    its output to `RWS/out/hookB/` at once (same output names as A), keep frames 0-79, splice them onto frames
    80-1039 of A with ffmpeg (frame-exact, re-encode once), then mux mix B FULL.
  - master: `FOSTER_NICE=10 tools/heavy.sh python3 render.py bijli_chali_gayi --workers 2 --no-sfx-build --audio RWS/audio/bijli_chali_gayi_mix_A_full.wav`
  - delivery: `python3 package.py bijli_chali_gayi c11_bijli_chali_gayi_A --cover 2.0` (→ `reel/jawad_reels/jawad_c11_bijli_chali_gayi_A*.mp4`;
    the packager copies the stems from `RWS/audio/`, not `<WS>/audio/`; then the dedicated cover still of §6.15 replaces the extracted `_cover.jpg`), and the spliced B file as `jawad_c11_bijli_chali_gayi_B.mp4`.
- **Gates before any full render (SLATE §4 + GATE fixes 2-3):** (1) the 3D contact sheet (done: finals in
  `out/sheets3d/`); (2) one beam-mask still at f20 and the sequence f12-f20 (keyword lit by f15, no empty near-black
  frame; f14 ≥ 2,000 px above luma 90); **(2b) the f0, f9 and f15 stills after `G.tx_finish`, Read at 360 px: f0 and
  f9 YAVG ≥ 35 (limited) and luma p99 ≥ 200 (limited); the tube light, the fan's three blades and the CRT edit (three
  tracks + playhead) readable at 360 px; f15 *Bijli* and the CRT dot readable** (r2 proof on the real plate: f0 49.0 /
  234, f9 38.2 / 224); **(2c) the rooftops at 6.5 s and 7.3334 s (f220) Read at 360 px: the skyline separates from the
  haze band, candle pools and rims read, the far window is lit on f220; the S5 monitor at 14.0 s Read at 360 px: the
  same edit as the CRT plus the rooftop viewer**; (3) stills at 8.1 (bulbs + slam), 27.6 (payoff), 29.4 (L4 resolve),
  33.0 (end card); Read every image before going on.

## 8. QA acceptance checklist (measurable; motion-qa-reviewer lenses A and B + verifier)

**Format**
- [ ] ffprobe: 1080x1920, 30/1 fps, nb_frames = 1040, duration 34.667 s ±1 frame, both versions; A and B frames
      80-1039 bit-identical before encode (hash per frame of the PNG renders).

**Copy, layout, legibility (lens A)**
- [ ] Every on-screen string matches §6.6 exactly (spelling, case, punctuation); no other text anywhere (props carry
      no legible text or logos).
- [ ] Ink bboxes (incl. halo) inside x 70-1010, y 230-1480 (CTA ≤ 1600); nothing textual below y 1620; nothing at
      x > 930 in y 1050-1700; widths ≤ 940 (≤ 780 in y 1050-1700).
- [ ] At most 2 text blocks at once outside the end card (captions count as one).
- [ ] Contrast ≥ 4.5:1 for every text element on its local background (p50 text vs p90 background luminance).
- [ ] Captions: `cap.check() == []`, no chunk inside a face rect, hidden in [0, 2.667), [26.667, 29.333), [30.667, DUR];
      caption words = VO ROM tokens.
- [ ] Payoff caps read `BIJLI NE SIKHAYA` at 86 px (r2), V10 caption "...editing nahi sikhai..."; no "SIKHAAYA" or
      "sikhaayi" anywhere (grep the SRT and the module).
- [ ] Captions never cover the far window or the child's head in 5.333-8.0 s (§6.14 avoid rects).
- [ ] Cover: the dedicated `JAWAD_C11_COVER=1` still at 2.0 s, keyword inside y 240-1680, H1 at full glow, window
      mean luma ≤ 10 (full range).

**Picture, light, motion (lens B)**
- [ ] **Frame 0 and frame 9 (A), r2 gate:** after `G.tx_finish`, YAVG ≥ 35 on both (limited range, as signalstats on
      the encode; fail below 35); luma p99 ≥ 200 (limited); in the 360 px thumbnails of f0, f9 and f15 the tube light,
      the fan's three blades and the CRT edit (three tracks, playhead) read, and on f15 *Bijli* and the CRT dot read.
- [ ] CRT image (debug dump of `crt_image(0)`): three tracks ≥ 36 px tall (spec 48), playhead ≥ 6 px wide, FLAME and
      EMBER blocks; the S5 monitor shows the same block pattern and its playhead parked at x ≈ 440 (± 4 px).
- [ ] Every power-off frame (f14-f239, f300-f399, f480-f559, f720-f879): YAVG ≥ 18, max luma ≥ 150 and ≥ 2,000
      pixels above luma 90 (never empty); the only fully dark frame is the L8 closed frame f560. f14 (the instant the
      mains die, the designed blackout) is exempt from the YAVG floor only (r2 proof 17.4); its 8 px line keeps it
      above 2,000 px.
- [ ] **Rooftops at 360 px (r2):** on f170, f200, f219 and f310 the sky band just above the far roof tops is ≥ 25 mean
      luma (full range) and ≥ 20 code values above the far roofs; the silhouettes stay ≤ 10 inside with the candle-side
      rim visible; candle pools visible on the parapet and the charpai; no moon, no blue sky (hue rule below).
- [ ] **Tease (r2):** the far window is lit on f220 and f221 only (IVORY, identical frames), dark on f219 and f222-f239;
      mean frame luma on f220-f221 ≤ f219 + 1 code value; the child's head turns over f224-f230 and holds to f300.
- [ ] Blacks legal: luma p1 16-22, below-16 share ≤ 0.5 % per frame (`jawad_grade.py verify`).
- [ ] Brownouts and power deaths only darken: no frame's mean luma in f10-f14, f300-f305, f470-f472, f480-f485
      exceeds that of the last steady frame before the event (f9, f299, f469, f479).
- [ ] L4 f870-f889 is warm halation, never a grey veil or a white frame: on the peak f880, luma p10 ≤ 40 (full
      range) and the darkest 20 % of pixels keep at least f869's mean chroma; by f889 p10 is back within 3 levels
      of f869's; share of pixels at luma ≥ 250 ≤ 2 % on every frame. (Measured on a candle test scene with the real
      `jawad_tx` L4 + `dusk` finish: p10 2 → 32 at the peak → 2 at f889; ≥ 250 share 0.03 %.)
- [ ] Emissive FLAME / RED ≤ 3× linear in pre-post canvases at 0.6, 2.0, 8.1, 16.1, 27.6, 29.4 s (debug dump).
- [ ] Hue: `dusk` 'top5' rule passes (brightest 5 % of saturated px ≥ 60 % red-orange; violet ≤ 45 %).
- [ ] Camera: locked (0 px frame-to-frame offset) from 4 frames after each power-on frame until the next power-off;
      drift ≤ 7 px amplitude when off; no jumps (frame-to-frame camera delta ≤ 3 px except inside the tilt f140-f180).
- [ ] Faces: profile on screen f740-f839 only, smiling f880-f919 only; bust bottoms ≥ 1920; halo ≤ +6 code values;
      no cross-dissolve; no mirroring.
- [ ] Transitions: L7 beam crosses x 540 on f320 ±1; L8 fully closed on f560 only; L4 cut on f880; every
      other cut on its §6.8 frame; motion blur never crosses a cut.
- [ ] Loop: `E.seam_report(...)['ok']` is True; f1039 vs f0 composition identical (fan angle and playhead from the
      shared clock).

**Audio (lens B)**
- [ ] Every mix (A FULL, A DRY, B FULL): -14.0 LUFS ±0.5 integrated, TP ≤ -2.0 dBTP (wav), ≤ -1.5 after AAC, LRA 5-9;
      VO stem -16 LUFS ±0.5.
- [ ] Speech ≥ 8 LU above the SFX/bed stem (median over voiced frames); SFX in VO windows ≥ 6 LU below speech.
- [ ] VO onset ≤ 0.13 s (A) / ≤ 0.33 s (B); V1 ends ≤ 1.30 s; hook VO ends ≤ f79; "chhat" onset ≥ 5.334 s (after
      f160); V4 ends ≤ 7.85 s; "editor" onset 13.33-13.40 s; V7 starts ≥ 16.40 s; "Ctrl+S" onset 20.667-21.333 s
      (f620-f640, r2); V10 ends ≤ 26.30 s; "sabr" onset 27.30-27.37 s; V12 ends ≤ 34.17 s.
- [ ] Drop-out f790-f799: RMS over f791-f798 ≤ -45 dBFS and peak ≤ -30 dBFS (only the held room tone); harmonium
      peak at f820 ±1.
- [ ] Max momentary loudness of the reel inside 29.333-29.933 s (the power return).
- [ ] Sync ±1 frame: beeps ↔ LED pulse frames (f40, f60; B also f0), keycap thocks ↔ press frames, power_thunk ↔
      power frames (f240, f300, f400, f480, f880), match_strike ↔ f80.
- [ ] V1 intelligibility (r2): faster-whisper `hi` on mix A FULL returns बिजली चली गई inside 0-1.3 s, every word at
      probability ≥ 0.5 (else crt_off static and relay_click -4 dB, §6.10).
- [ ] The f220 hum blip adds nothing in 1-4 kHz under V4: SFX-stem band level (1-4 kHz) over 7.30-7.50 s ≤ its level
      over 7.10-7.30 s + 1 dB.
- [ ] If V2 uses the r2 fallback (1.550 s), it ends ≤ 2.000 s and the lead's OK is recorded in SCRIPT §12.
- [ ] ≤ 3 sounds start on any instant (cue-sheet check); no `flash_hit`, no music bed, no words in any crowd sample
      (faster-whisper small, hi and en, on 8.0-10.0 and 29.5-31.1: no word with probability ≥ 0.5).
- [ ] Loop audio: no fade at the end (bed level in the last 0.5 s within 1 dB of the first 0.5 s); the reverse_swell
      ends on DUR ±10 ms.

**Brand and truth**
- [ ] Nothing from Organic Fostering / Floret, none of the old props, no ERROR/unsaved dialog, no laptop, no UPS or
      inverter label, no money, no place or utility names, no religious or national markers.
- [ ] VO never says "main" / "meri"; every line matches §6.7 (ROM) and the spoken-number lock ("har tees second" only).
- [ ] `@jawad_mp4` end card settled ≥ 1.5 s (f975.5-f1029); CTA `COMMENT MEIN / batao` is the only CTA.
- [ ] AI info on; audio named per §6.15.

## 9. Work orders (who runs next, on what)

| # | agent | work order | done when |
|---|---|---|---|
| 1 | blender-3d-artist (+ `blender-pro-reference`) | **done (finals in `RWS/assets3d/`, `out/sheets3d/`)**: `assets3d_bijli_chali_gayi.py`, the 8 asset folders of §6.12; r2 needs no 3D change (see §10 item 8 for one open note) | contact sheet Read and passing §6.12 checks |
| 2 | hinglish-scriptwriter | **r2:** apply GATE fixes 1, 4, 5 and minor 6 in `SCRIPT.md` / `script.json` (V4, V7, V8 DEV + ROM trims; V10/V11 ROM `sikhai` / `sikhaya`; V8 keyword *khud*; V2 fallback placement) and the §6.7 r2 windows; then the pronunciation test, the 7 Vlad takes (T2 and T4 with the trimmed DEV only), `vo_chain` processing, assembled A and B VO tracks + words JSON in reel time | timings inside §6.7 windows (or the ladder step reported) |
| 3 | viral-strategist | script gate done (`GATE.md`, FIX → applied in r2); later red-team of the preview (re-measure the 5.5-8.0 s window and the hook's 360 px read) | PASS / FIX list |
| 4 | face-compositor | `bijli_chali_gayi_faces.py` per §6.13, two looks built once, test stills at 25.5 s and 29.6 s | stills Read; limits met |
| 5 | motion-timeline-builder | `bijli_chali_gayi.py` per §6-7 on the real 3D finals; r2: the bold `crt_image` (§6.9), the S5 monitor with the same edit + 9:16 viewer, the rooftops' haze band / pools / rims, the f220 tease and head turn, the fan readable at 360 px, the 8 px f14 line, the 86 px payoff, the `JAWAD_C11_COVER` still; gates §7 (2b, 2c); then master A and hook B | gate stills Read at full size and at 360 px; §8 lens-B picture items pass |
| 6 | sound-designer | `bijli_chali_gayi_sfx.py`: 12 custom sounds, cue sheet §6.10 (r2: + the f220 `tube_flicker` lp 250 blip), beds, `fit_under_vo`, SFX stems for hook A and hook B, each with and without the harmonium cue; the V1 whisper check on the A mix | `A.qc == []`, cue checks pass |
| 7 | music-supervisor | `bijli_chali_gayi_music.py`: harmonium placement and tuning, final mixes A FULL, A DRY, B FULL, loudness report | §8 audio items pass |
| 8 | caption-designer | captions config §6.14 (r2: one keyword per line, V8 *khud*, S3 avoid rects), SRT, check | `cap.check() == []` |
| 9 | colorist | `dusk` verify on the preview and master (frame 0, dark stretches at 360 px, L4, hue budget) | `verify.json` passes |
| 10 | motion-qa-reviewer (lens A, lens B) + verifier | §8 on the master, both versions | every box ticked or a verified defect filed |
| 11 | delivery-packager | encodes, the dedicated cover still (§6.15, r2) over the extracted `_cover.jpg`, caption post §6.15, names §0 (no commit; the lead commits) | files in `reel/jawad_reels/` |
| - | motion-toolkit-engineer | `SHARED_REQUESTS.md` items 1-2 (not blocking) | fixed in the shared modules |

## 10. Open questions (resolved with SLATE §7 defaults; none blocks the build)

1. AI label: **on** for both versions (default). 2. Trial Reels eligibility (1,000+ followers): unconfirmed; hook B
is built anyway and posted only if eligible. 3. House spelling: the prior SRT (bari, nahi, hai; r2: sikhai / sikhaya,
GATE fix 4). 4. "Mummy/Ammi", "Ubaal Chai", the C26 nameplate and the C08 lane label do not apply to this reel.

**r2 items for the lead (from `GATE.md`):**
5. **Copy sign-off, GATE fix 1:** V4 `Jab wapas aati thi...`, V7 `Aur bijli ban gayi sab se bari dushman.`, V8 `Har desi
   editor ki ungli khud Ctrl+S dabati hai.` are written into this brief (§2, §6.7). They are copy changes: the lead
   records the OK (SCRIPT §12 item 1) before takes T2 and T4 are generated; if refused, the r1 lines and the r1 overrun
   ladder return.
6. **SLATE deviation, GATE fix 5:** the V2 fallback at 1.550 s (between the beeps) applies only if TA's processed "Yaad
   hai?" runs > 0.43 s, and only with the lead's OK; otherwise V2 stays at 2.200 s.
7. **Truth ⚑ (GATE minor 8):** JD's profile sits under "Bijli ne humein…", so some viewers will read it as his own
   memory. The VO is the collective "humein" (SLATE's accepted framing) and claims nothing about him; the lead confirms
   Jawad is comfortable with it.
8. **3D note (not a gate fix; found while proofing):** the finals' `key_l` / `key_r` passes add a warm back rim
   opposite the torch (builder `_rim`, energy 7), which lights the visible left faces of the box and the tower flat
   orange in `key_r` (`out/sheets3d/bcg_finals_room_torch.png`). §6.12 asked for the torch only. The timeline builder
   applies the passes only under the beam mask (§6.9), which limits it; the lead decides whether the 3D artist
   re-renders `key_r` without the rim.

## 11. CHANGELOG

- **r2 (2026-10-08, creative-director): viral gate FIX applied** (`GATE.md`; proofs `out/brief_proofs_r2/`).
  - Fix 1 (mirrored from hinglish-scriptwriter): V4 drops "Aur", V7 drops "editor ki", V8 drops "Isliye". A is now
    65 words / 107 syllables, B 64 / 104 (§2, §6.7). The §6.7 windows are re-laid at Vlad's average pace (0.202 s per
    syllable). V3a runs to 4.0, "chhat" lands at 5.35-5.45, "Ctrl+S" lands in f620-f640, and V10 may pre-lap the f720
    cut by ≤ 0.33 s. Bold targets are unchanged. The ladder is now a fallback only (T-c superseded). Lead sign-off: §10.5.
  - Fix 2: frame-0 gate (f0 and f9 YAVG ≥ 35 limited, p99 ≥ 200, 360 px read of the tube, fan and CRT; §6.3, §7 2b, §8).
    The CRT edit is drawn bold (3 tracks × 48 px, a 6 px IVORY playhead, FLAME / EMBER; §6.9). The S5 monitor shows the
    same edit, parked where the CRT died, next to a 9:16 rooftop viewer. The fan reads as a silhouette. The f14 line is
    8 px (it measured 2,770 px above luma 90); f14 is exempt from the YAVG floor only (17.4).
  - Fix 3: f220 tease (a far window false-starts for 2 frames, the child turns its head f224-f230). The `tube_flicker`
    lp 250 blip is at -24 dB. The rooftops get a haze band, candle pools and 2 px rims, with 360 px targets (§6.2, §6.5,
    §6.9, §6.10, §6.14 avoid rects, §7 2c, §8).
  - Fix 4: P1 `BIJLI NE SIKHAYA` at the house 86 px (792 px wide, ink 125-948 × 250-783). Captions use `sikhai` /
    `sikhaya`. The caption body is respelled (§2, §6.6, §6.15).
  - Fix 5 (mirrored): V2 fallback at 1.550-2.000 s between the beeps, lead OK required (§6.3, §6.7, §10.6).
  - Minor 6-9: V8 keyword *khud* and one keyword per line (§6.14). Hook B LED bloom ≥ 40 px (§6.4). The cover is a
    dedicated still with H1 at 1.0 and a low window (§6.15). Truth ⚑ goes to the lead (§10.7). V1 whisper check (§6.10, §8).
  - Also: L8 cue note (now V7 / V8 onset) and work orders (§9).
- **r1 (2026-10-08):** first brief from SLATE §0, §2, §3.2, §4, §5.
