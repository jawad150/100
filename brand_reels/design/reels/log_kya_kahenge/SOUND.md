# SOUND · Reel 5 · C15 · Log Kya Kahenge (SFX layer, run 2: real Vlad VO)

Date 2026-10-09 · Author: sound-designer · Code: `pipeline/jawad_reels/log_kya_kahenge_sfx.py` · Plan: `BRIEF.md` r2 §4, §5-6, §11, §18
(binding), `SLATE.md` §3.5 (sound motif = the whisper wall, ONE floodlight clunk at 25.6 s) and §5.1. Key: D minor (from
`MUSIC_log_kya_kahenge.md`). VO: `VO_TIMING.md` (MEASURED, 06:53).

Nobody on the team can listen, me included. Everything below was measured: ebur128 (ffmpeg and numpy BS.1770), onset finders,
spectrograms (I opened them), and ASR. Run 1 (2026-10-08) was fitted to a labelled stand-in VO. This run is fitted to the real
VO word timings (`vo/words.json`, `lkk_vo_B.words.json`) and the VO audio activity.

## 0. Hand-off

| what | where / value |
|---|---|
| builder (`log_kya_kahenge.py`) | adopts nothing from this module. `cues()` stays `[]` (BRIEF §17.2): `audio.mix` cannot reproduce the loop-exact beds, so this module builds the stem itself (`mix_loop`). `BED, BED_GAIN_DB = None, -30` are kept only for compatibility |
| render flag | `--no-sfx-build --audio <RW>/audio/log_kya_kahenge_mix.wav` (music-supervisor's final mix; Trial: `..._hookb_mix.wav`) |
| SFX stems for the music-supervisor | `<RW>/audio/log_kya_kahenge_sfx_stem.wav` (hook A), `<RW>/audio/log_kya_kahenge_hookb_sfx_stem.wav` (hook B): 48 kHz, 24-bit, stereo, exactly 1,689,600 samples, -18 LUFS, ≤ -2.0 dBTP, loop-exact. Split: `*_sfx_stem_fx.wav` + `*_sfx_stem_bed.wav` (they sum to the stem). `*_sfx.wav` is the same audio under the name render.py muxes |
| cue lists | `<RW>/audio/log_kya_kahenge_cues.json`, `..._hookb_cues.json` (`placed`: start, hit, gain after ducking, filters, carve, event) |
| reports | `<RW>/audio/log_kya_kahenge[_hookb]_sfx_report.json` (stem), `..._rough_mix.json` (mix), `..._roughloop_mix.json` (loop-safe mix) |
| images (viewed) | `..._sfx_overview.png` (stem: spectrogram + cue ticks + loudness), `..._rough_mix.png`, `..._roughloop_mix.png`, `log_kya_kahenge_rough_zooms.png` (drop-out and loop seam), `audio/audition/*.png` (each local sound) |
| rough mixes (for checks only) | `<RW>/audio/log_kya_kahenge[_hookb]_rough_{mix,vo_sfx,stem_vo,stem_sfx,stem_music}.wav` (plain epic_mix) and `..._roughloop_*` (loop-padded epic_mix) |
| rebuild | `cd pipeline/jawad_reels; H=tools/heavy.sh; $H python3 log_kya_kahenge_sfx.py build --hook AB; $H python3 log_kya_kahenge_sfx.py rough --hook AB [--loop]` (~25 s + ~20 s). Re-run whenever the VO or an event time moves |
| other commands | `python3 log_kya_kahenge_sfx.py cues [--hook A/B]` (fitted cue table), `audition` (local sounds: wav + png + qc), `verify` (whisper-wall ASR) |

`<RW>` = `workspace/jawad_reels/log_kya_kahenge`.

## 1. Policy and motif

- **With music.** The score is `log_kya_kahenge_music.py`. The SFX stay sparse over the pulse (16.0-25.6 s). Tonal SFX are
  pitched into D minor. Measured: glass_tap D7 +0 c, the clunk's ui_click A5 +0 c, the scroller ticks A7 +4 c, the flood hum A2.
- **Motif: the whisper wall** (`lkk_whisper_wall`). It is built from CC0/PD crowd samples (the `crowd_cheer_real` and
  `crowd_ahh_real` sources), reversed, pitched down 4.98 semitones, band-passed 300-3000 Hz, then granulated and mixed with a
  breath layer. It never uses words and never `crowd_ooh`. It runs 0-15.2 s, is cut dead at 15.2 s, and returns for the loop
  from 33.6 s.
- **One clunk only**: ui_click + impact_soft + sub_drop at 25.6 s. No other stack of those three sounds exists.
- **One drop-out**, 15.2-16.0 s (BRIEF §5): the wall and the score stop dead. A heartbeat plays over a -40 room-tone floor.
- **At most 3 sounds start on one instant** (measured, §4).
- **Under the VO** (`sfx_jawad.fit_under_vo`, VO first):
  - detail cues on a word are ducked -6 dB: air sounds get hp 5500, dark sounds lp 1100, mid sounds -8 dB;
  - spans over speech get -6 dB and lp 1100;
  - hero hits need ≥ 120 ms of no speech before them and ≥ 300 ms after them (150 ms for non-impacts), counting both the
    words and the measured VO audio;
  - hero tails are carved under later speech: -15 dB for the reveal, -10 dB for the clunk.

## 2. Cue sheet, hook A (47 cues; all names in `audio.names()`; no fuzzy fallbacks)

How to read the table:
- **gain**: the brief's cue gain, then (after the arrow) the gain actually placed, after `fit_under_vo` and audio.mix's
  cluster `duck_under`.
- **measured**: each cue rendered alone and placed in the reel.
  - *onset*: first 2 ms bin within 20 dB of the cue's peak, against the cue time.
  - *peak*: centre of the loudest 30 ms. Whooshes, swells and bursts peak broadly; each one is within 1.5 dB of its peak at
    the designed hit.
  - *end*: for spans that end on the cue time.
- **Hero** cues are in bold.

| # | t (s) | f | sound | align | gain dB (brief → placed) | keys / VO fit | measured | visual event |
|---|---|---|---|---|---|---|---|---|
| 1 | 0.000 | 0 | impact_soft | hit | -6 → -6.0 | lp 1100 | onset -4 ms | frame-0 transient = the loop landing |
| 2 | 0.300 | 9 | swish_small | hit | -14 → -21.5 | under V1: -6, hp 5500 | peak -5 ms | head-snap wave (air) |
| 3 | 0.400 | 12 | lkk_whisper_swell | hit | -8 → -14.0 | under V1: -6, hp 4500 | peak -3 ms | the swell peaks on the snap |
| 4 | 0.600 | 18 | shimmer | hit | -12 → -18.0 | under V1: -6, hp 5500 | onset -14 ms | wave complete, hook text readable |
| 5 | 3.200 | 96 | lkk_whisper_burst | hit | -10 → -10.0 | - | peak -11 ms | J1 flies out of the crowd |
| 6 | 3.467 | 104 | whoosh_by | hit | -12 → -12.0 | lp 4000, dur 0.6 | peak +11 ms | J1 fly-in pass (hold depth f106) |
| 7 | 4.800 | 144 | lkk_whisper_burst | hit | -8 → -8.0 | - | peak -23 ms | J2 |
| 8 | 5.000 | 150 | whoosh_by | hit | -12 → -12.0 | lp 4000, dur 0.5 | peak -2 ms | J2 pass (f152) |
| 9 | 6.000 | 180 | lkk_whisper_burst | hit | -6 → -6.0 | - | peak -21 ms | J3 |
| 10 | 6.133 | 184 | whoosh_by | hit | -12 → -12.0 | lp 4000, dur 0.4 | peak +1 ms | J3 pass (f186) |
| 11 | 7.200 | 216 | lkk_whisper_burst | hit | -4 → -4.0 | - | peak -3 ms | J4, the last and loudest line |
| 12 | 7.333 | 220 | whoosh_by | hit | -12 → -12.0 | lp 4000, dur 0.4 | peak -1 ms | J4 pass (f222) |
| 13 | 9.600 | 288 | whoosh_slow | hit | -12 → -18.0 | under V2: -6, lp 1100 | peak -39 ms (-0.56 dB at hit) | O2 smoke wipe, S2 → S3 |
| 14 | 10.200 | 306 | impact_soft | hit | -16 → -22.0 | under V2: -6, lp 1100 | onset -2 ms | O2 clears, JD alone |
| 15 | 12.800 | 384 | lkk_board_flex | start | -14 → -22.3 | under V2: -6, lp 1100 | onset +6 ms | heads tilt in sync (first cardboard hint) |
| 16 | 12.800 | 384 | impact_soft | hit | -16 → -24.3 | under V2: -6, lp 1100 | onset 0 ms | L3 cut to the 135 mm rows |
| 17 | 15.200 | 456 | reverse_swell | hit (end) | -8 → -8.0 | lp 1100, 0.367 s, no room send | end -0.7 ms | the suck into the drop-out |
| 18 | 15.600 | 468 | heartbeat | hit | -12 → **-18** (run 2) | lp 900, n 1 (dub at f474) | onset +6 ms | held breath in the drop-out |
| 19 | **16.000** | **480** | **impact_big** | hit | -2 → **-8** (run 2) → -9.2 | sat 8, tail 0.6; carve -15 from 16.342 | onset -3 ms | **REVEAL** transient + hall |
| 20 | **16.010** | **480** | **braam** | start | 0 → **+4** (run 2) → +2.8 | root D1 36.71 Hz, dur 1.0, sat 12; carve -15 from 16.342 | onset 0 ms | **REVEAL** body (+10 ms after the transient) |
| 21 | 17.600 | 528 | lkk_board_flex | start | -16 → -22.0 | under V3: -6, lp 1100 | onset +4 ms | cards flexing mid-orbit |
| 22 | 19.200 | 576 | whoosh_slow | hit | -12 → -12.0 | lp 1100 | peak -45 ms (-0.65 dB at hit) | edge-on pass, the single image |
| 23-25 | 21.600 / 21.800 / 22.000 | 648 / 654 / 660 | ui_tick | hit | -20 → -26.0 | under V4: -6, hp 5500, pitch → A7, pan +0.1 | onset 0 ms | scroller taps |
| 26 | 22.400 | 672 | lkk_ember_crackle | start | -12 → -18.0 | under V5: -6, hp 5000, dur 1.6 | onset +26 ms (soft build, by design) | O6 erosion starts |
| 27 | 23.000 | 690 | whoosh_slow | hit | -14 → -20.0 | under V5: -6, lp 1100 | peak -123 ms (-0.90 dB at hit) | O6 midpoint |
| 28 | 23.600 | 708 | impact_soft | hit | -8 → -16.3 | -6, lp 1100 (V5 pause 23.51-23.667) | onset -2 ms | O6 complete |
| 29 | 23.600 | 708 | sub_drop | hit | -10 → -18.3 | -6, lp 120, dur 1.0 | onset -8 ms | O6 complete, sub |
| 30 | 25.600 | 768 | reverse_swell | hit (end) | -10 → -15.1 | lp 1100, 0.2 s | end 0 ms | into the payoff |
| 31 | **25.597** | **768** | **ui_click** | hit | -6 → -10.4 | rate 0.5322 (A5); carve -10 from 25.955 | onset -0.9 ms | **THE floodlight clunk**, transient 3 ms early |
| 32 | **25.600** | **768** | **impact_soft** | hit | 0 → -2.3 | lp 2500; carve -10 | onset -4 ms | **clunk body**, warm light on |
| 33 | **25.600** | **768** | **sub_drop** | hit | -6 → -8.3 | lp 120, dur 1.0; carve -10 | onset -8 ms | **clunk sub** |
| 34 | 25.833 | 775 | shimmer | hit | -12 → -13.5 | hp 5500 (before V6 at 25.97) | onset -20 ms | keyword *busy* rises |
| 35 | 26.167 | 785 | swish_small | start | -16 → -22.0 | under V6: -6, hp 5500 | peak at +0.14 s, -1 ms | underline draws |
| 36 | 28.800 | 864 | impact_soft | hit | -12 → -18.0 | under V6: -6, lp 1100 | onset -2 ms | L3 cut to the warm wide |
| 37 | 29.200 | 876 | swish_small | start | -16 → -16.0 | hp 5500, pan +0.35 (0.21 s after V6) | peak at +0.14 s, +1 ms | the last card starts to fall |
| 38 | **29.600** | **888** | **card_slide** | hit | -8 → -11.8 | pan +0.35 | peak +14 ms | **THE TAP**, the last card lands |
| 39 | **29.600** | **888** | **lkk_card_tap** | hit | (impact_soft -14) → **-13** (run 2) | pan +0.35 | onset -1.5 ms | **tap body** (cardboard slap) |
| 40 | 31.300 | 939 | swish_small | start | EndCard → -18.0 | under V7: -6, hp 5500 | peak +1 ms | end card, monogram ring draws |
| 41 | 31.770 | 953.1 | shimmer | hit | EndCard → -16.0 | under V7: -6, hp 5500 | onset -18 ms | CTA keyword *bhejo* rises |
| 42 | 31.950 | 958.5 | glass_tap | hit | EndCard → -20.0 | under V7: -8 (mid), pitch → D7 | onset -0.5 ms | monogram lands (EndCard's own time, between f958 and f959) |
| 43-46 | 32.233 / 32.733 / 33.200 / 33.700 | 967 / 982 / 996 / 1011 | card_slide | hit | -22 → -28.0 | under V7: -6, lp 2000 | peak +14 to +16 ms | flaps rise; rows 0-1, 3-4, 6-7, 9 land |
| 47 | 35.200 | 1056 = f0 | reverse_swell | hit (end) | EndCard → -14.0 | span over V7's tail: -6, lp 1100, 0.8 s | end 0 ms | audio loop swell into frame 0 |

**Hook B (Trial; frames 0-89; 49 cues).** Cue 1 is shared. Cues 2-4 are replaced, the O2 pair is added, and from f90 on the
cues are identical to hook A. The fit uses `lkk_vo_B.words.json` (V1B 0.09-2.47 s).

| t (s) | f | sound | gain dB (brief → placed) | keys | event |
|---|---|---|---|---|---|
| 0.200 | 6 | swish_small | -14 → -21.5 | under V1B: -6, hp 5500 | head-snap wave starts (135 mm rows) |
| 0.400 | 12 | lkk_whisper_swell | -8 → -14.0 | under V1B: -6, hp 4500 | swell peaks (the last heads start) |
| 0.600 | 18 | shimmer | -12 → -18.0 | under V1B: -6, hp 5500 | wave complete |
| 2.400 | 72 | whoosh_slow | -12 → -18.0 | under V1B: -6, lp 1100 | O2 smoke wipe, 135 mm → wide |
| 2.800 | 84 | impact_soft | -10 → -10.0 | - | O2 clears to the wide |

**Beds** (exact automation in `BEDS`, mixed by `mix_loop`; level L in the brief's scale, -30 = felt):

| bed | breakpoints | job | measured in the stem (bed bus, LUFS) |
|---|---|---|---|
| lkk_whisper_wall | 0-3.05: -24 · 3.35-5.85: -20 · 6.15-8.65: -18 · 8.95-15.196: -26 · cut dead at 15.2 | the judging crowd. It steps up with J1 and J3, sits under V2 at -26, and is cut dead for the drop-out | 0.2-3.0: -33.6 · 3.4-5.8: -30.8 · 6.2-8.6: -31.5 · 9.0-15.1: -35.6 |
| room_tone | 15.2-15.95: -40 · 16.0-33.6: -34 · fades out by 35.2 | the drop-out floor, then the open stadium | 15.25-15.95: -51.2 · 16.1-25.5: -44.7 |
| lkk_flood_hum (A2 110 Hz) | 25.65 → 25.9: up to -30 · -30 until 33.6 · out by 35.0 | the warm lamp after the clunk | 26.0-33.5: -38.9 (with room tone) |
| lkk_whisper_wall | 33.6 → 35.2: up to -24, loop position 0 at 35.2 | the wall returns for the loop: same level and same sample at the seam | 34.6-35.2: -36.1 |

**Local sounds** (`register()`, idempotent). `audition` checks each one with `A.qc == []`, a spectrogram and the mono fold-down
loss. Files: `<RW>/audio/audition/<name>.wav/.png`, `audition.json`.

| sound | hit | length | qc | mono loss | notes |
|---|---|---|---|---|---|
| lkk_whisper_wall | 0 (bed) | 12.00 s loop | clean | 0.88 dB | -20.0 LUFS. Loop seam step 0.033 against a median of 0.0135 (< 4×) |
| lkk_whisper_swell | 0.39 s (65 %) | 1.20 s | clean | 0.83 dB | |
| lkk_whisper_burst | 0.10 s | 1.10 s | clean | 0.84 dB | |
| lkk_board_flex | 0 | 0.81 s | clean | 0.16 dB | stick-slip clicks 600-1800 Hz plus a flex thump |
| lkk_ember_crackle | 0 (align start) | 1.83 s | clean | 0.46 dB | |
| lkk_flood_hum | 0 (bed) | 10.00 s loop | clean | 0.04 dB | 110.0 Hz = A2. Seam step 0.0018 against a median of 0.0017 |
| **lkk_card_tap** (new, run 2) | 0.0015 s | 0.59 s | clean | 0.10 dB | slap 400-3200 Hz (tau 22 ms) + air puff < 700 Hz + damped 140 Hz thud (tau 28 ms). Its max momentary is within 1 dB of the impact_soft it replaces |

## 3. What run 2 changed, and why (measured through the final chain)

The music-supervisor's `log_kya_kahenge_music.py mix` calls `epic_mix.mix_reel`, and `rough()` uses the same chain:
- VO goes to -16 LUFS;
- the SFX stem goes to -18 LUFS, with a -4 dB sidechain under the VO;
- the music goes to -18 LUFS, ducked -3 dB under the SFX and -9 dB under the VO;
- the master applies a 2:1 bus glue, gain and a 4× true-peak limiter at -2.3 dBTP.

The variants below were run through the same chain in memory (scratch harness, now deleted). "max" is the loudest momentary
loudness of mix A (400 ms windows, labelled by window centre):

| variant | reveal (15.8-16.2) | loudest elsewhere | stem limiter GR | verdict |
|---|---|---|---|---|
| brief levels (run 1 module, real VO) | -10.26 @ 16.2 | **-9.64 @ 0.35 (V1's VO)** | 5.11 dB | fails BRIEF §18. The glue took 4.7-5.3 dB off the reveal but only 0.8-1.75 dB off the VO hook |
| braam +3 only | -10.02 | -9.53 @ 0.35 | 5.75 dB | the stem limiter eats it |
| hook SFX -4 dB only | -10.28 | -9.64 @ 0.35 | 4.95 dB | no effect: the 0.35 s peak is the VO itself (SFX there sits ~11 LU lower) |
| judgement SFX -4 dB (for LRA) | -9.07 to -9.50 | -9.82 | 6.9-7.2 dB | LRA 2.43-2.76 (no gain); the stem limiter got worse. Rejected |
| no bus glue at all (diagnostic) | -9.53 | -9.18 @ 0.2 | 5.11 dB | LRA 2.65: the low LRA is structural, not caused by the glue |
| impact_big -6 sat 8, braam +4 sat 12 | -8.63 | -9.45 | 3.26 dB | works, but the limiter is over ~3 dB |
| **chosen: impact_big -8 sat 8, braam +4 sat 12** (+ carve, heartbeat, tap) | **-8.47** (rough A) | **-9.39** | **2.19 dB** | max at the reveal, 0.92 LU over the rest |

The other run-2 changes:
- **Hero carve.** Each carve now starts 15 ms before the measured speech (words plus VO activity) instead of 60 ms before it,
  so the reveal keeps its full 400 ms window before V3. The reveal tails carve -15 dB under V3 (`REVEAL_CARVE_DB`); the
  clunk tails stay at -10 dB.
- **Heartbeat -12 → -18 dB.** The drop-out momentary went from -17/-22 LUFS (3-6 LU under the programme) to -24/-28 LUFS.
- **Tap body: impact_soft → lkk_card_tap.**
  - impact_soft's tonal body (65 Hz, and ~230 Hz even with hp 150) makes a 15 ms ripple in qa_measure's 5 ms envelope.
    The tool read the tap at +55 ms, a CHECK line.
  - With lkk_card_tap the onset reads 0 ms on the stem and on both mixes.

## 4. Measurements

**SFX stems** (`build`; circular mix, loop-exact):

| stem | I (LUFS) | TP (dBTP) | ffmpeg I / TP / LRA | max momentary | limiter max GR | glue GR | bed bus | seam (last vs first 50 ms; step vs median) |
|---|---|---|---|---|---|---|---|---|
| A | -17.99 | -2.20 | -18.0 / -2.2 / 22.1 | -5.76 @ 16.2 s | 2.19 dB @ 16.010 (0.28 % of time > 1 dB) | 2.47 dB | -35.6 LUFS | -27.9 / -14.1 dB (the f0 transient); step 0.0060 vs 0.0043: continuous |
| B | -18.02 | -2.20 | -18.0 / -2.2 / 22.0 | -5.73 @ 16.2 s | 2.54 dB @ 16.010 | 2.52 dB | -35.7 LUFS | step 0.0060 vs 0.0044 |

Inside the drop-out (15.2-16.0) of the stem: the whisper wall reads -240 dBFS (digital zero, cut dead), the SFX peak is
-13.1 dBFS (heartbeat), and 0 frames are digital silence (the room tone floor runs throughout). No `hit before 0 s` warnings.
Tails that run past 35.2 s wrap onto t = 0 by design.

**Rough mixes** (epic_mix, real VO + the stem + `music_full.wav`):

| mix | I (LUFS) | TP wav (dBTP) | AAC 320k: I / TP | LRA (ffmpeg) | master limiter GR |
|---|---|---|---|---|---|
| A full, hook A | -14.0 | -2.3 | -14.1 / -2.2 | **2.9** | 3.36 dB |
| B VO + SFX, hook A | -14.0 | -2.3 | -14.1 / -2.2 | **4.9** | 3.43 dB |
| A full, hook B | -14.0 | -2.3 | -14.1 / -2.2 | **2.7** | 3.38 dB |
| B VO + SFX, hook B | -14.0 | -2.3 | (not encoded) | **4.6** | 3.49 dB |
| A full, hook A, loop-padded (`--loop`) | -14.00 | -2.21 | -14.0 / -1.9 | 2.7 | (padded run) |
| B, hook A, loop-padded | -14.00 | -2.19 | (not encoded) | 4.7 | |

The VO against the bed, hook A mix A: medians over voiced frames, momentary loudness.

| | overall | V1 | V2 | V3 | V4 | V5 | V6 | V7 |
|---|---|---|---|---|---|---|---|---|
| VO over bed (music + SFX) | **9.7** | 12.3 | 10.4 | **5.9** | **7.6** | 8.1 | 11.0 | 11.4 |
| VO over music | **10.4** | 13.3 | 10.7 | 7.4 | 7.7 | 8.2 | 11.6 | 11.7 |
| VO over SFX | 23.0 | 19.5 | 22.4 | 12.8 | 29.6 | 26.0 | 25.5 | 24.7 |

Hook B gives the same numbers within 0.3 LU; V1B is 12.0 over the bed. Under V3 and V4 the shortfall comes from the score's
B-section pulse and pad, not from the SFX (§6).

## 5. BRIEF §18 sound checklist and the task's rules

| check | result | |
|---|---|---|
| -14.0 ±0.5 LUFS, TP ≤ -2.0 dBTP (wav), ≤ -1.5 after AAC | A -14.0 / -2.3 (AAC -14.1 / -2.2); B -14.0 / -2.3 (AAC -14.1 / -2.2) | PASS |
| LRA 5-9 LU | A 2.9 · B 4.9 (hook A); A 2.7 · B 4.6 (hook B) | **FAIL**: structural, see §6 |
| VO stem -16 LUFS | -16.03 (VO_TIMING) | PASS |
| speech ≥ 8 LU over the bed (music), median of voiced frames | 10.4 over music, 9.7 over music + SFX | PASS overall. Per line, V3 (5.9) and V4 (7.6) are under 8 against music + SFX |
| max momentary within ±0.2 s of 16.0 | A: -8.47 LUFS, window 16.0-16.4 (centre 16.2; ffmpeg labels it 16.4, the window end), 0.92 LU over the next loudest (V1, 0.35 s) · B: -8.82, 0.69 LU · hook-B mixes: 1.74 / 1.50 LU · loop-padded: 1.03 / 0.79 LU | PASS (thin margin) |
| the 25.6 s clunk ≥ 2 LU below the reveal; exactly one clunk | clunk alone (window centres 25.40-25.77, before V6 at 25.97): -13.47 LUFS = **5.0 LU** below. The old 25.4-26.2 search caught V6's first words (-11.38, still 2.9 LU below). One ui_click + impact_soft + sub_drop stack | PASS |
| drop-out 15.2-16.0: music ≤ -60 dBFS; wall ≤ -60 dBFS; digital silence ≤ 8 frames; floor ≈ -45 LUFS | music -240 dBFS (15.2-15.996; the score's own 4 ms fade-in edge 15.996-16.0 reaches -27.7); wall -240 dBFS; 0 silent frames; floor -43.9 LUFS momentary (window 15.2-15.6); heartbeat -28.4 to -25.3; the loudest drop-out window sits 11.3 LU under the programme | PASS |
| whisper wall: faster-whisper finds no word with p ≥ 0.5 | `verify` (small + medium; hi / en / auto; the 24 s loop ×2 and the bed stem 0-15.2 s; `whisper_wall_asr.json`): 10 of 12 transcriptions return 0 words. medium/en and medium/auto(en) on the 24 s loop return "Thanks for watching!" ('for' p 0.72, 'watching!' p 0.93), both words zero-length at 23.98 s, the clip's last 20 ms. `verify-control` (`whisper_wall_asr_control.json`): the same phrase appears on pink noise (300-3000 Hz, no voice possible) at its end (p 0.94); it follows the clip end (20 s cut: at 19.98); the 6 s-rotated loop returns no words. This is Whisper's end-of-audio hallucination, not content | literal criterion FAILS on 2 of 12 runs; content PASS (control) |
| hero cue onsets within ±1 frame (`qa_measure.py cues` method) | stem: impact_big 0 ms, braam -10 ms, ui_click -2, impact_soft -5, sub_drop -5, card_slide / lkk_card_tap 0 ms (rise 16.6 dB). Mix A and mix B: identical (0 / -2 / -5 / 0 ms) | PASS |
| hero hits clear of words (≥ 120 ms before, ≥ 300 ms after) | reveal 16.000: speech ends 14.02, next speech 16.357 (+357 ms; the braam's blat peak at 16.05 is +307 ms) · clunk 25.597: speech ends 25.32 (-277 ms), next 25.97 (+370 ms) · tap 29.600: speech ends 28.99, next 31.443 | PASS |
| ≤ 3 sounds start on one instant | max 3: 16.0 (impact_big + braam + the score's first pulse), 23.6 (impact_soft + sub_drop + the score's hat), 25.597 (ui_click + impact_soft + sub_drop; the reverse swell ends there and does not count) | PASS |
| one drop-out, at the reveal | 15.2-16.0 only | PASS |
| loop: no click at the seam | stem: continuous (step 0.0060 vs 0.0043). Plain epic_mix: **step 0.0708 vs 0.0048 (a click)**. Loop-padded epic_mix: 0.0074 vs 0.0051 | stem PASS; mix needs `--loop` (R5c) |
| sound names known (`audio.names()`) | 47 / 49 cues, 4 beds: all known, no fallback warnings | PASS |

## 6. Open items

**For the music-supervisor (final mix):** items 1-4 and 6 were resolved on 2026-10-09 by `log_kya_kahenge_mix.py` and the
re-built score (final mixes in `<RW>/audio/final/`; numbers in `MUSIC_log_kya_kahenge.md` run 2). Item 5 is still open for the lead:
LRA of the final version A is 3.4 LU, version B 5.7 LU.
1. **Mono VO crash (SHARED_REQUESTS R5a).** `mix` passes the mono `lkk_vo_A.wav` to `epic_mix.mix_reel`, which raises a
   ValueError at its `np.concatenate`. Feed a stereo copy (`np.repeat(x, 2, axis=1)`), as `rough()` does.
2. **Seam click (R5c).** The plain epic_mix leaves a step at the loop seam: at 0.0 s the music is unducked, at 35.2 s it is
   still ducked after V7. Use the loop-padded recipe (`_loop_mix` in `log_kya_kahenge_sfx.py`: pad 3 s circularly, mix,
   crop, one gain trim). Verified: step 0.0074 vs 0.0051, -14.00 LUFS, -2.21 dBTP.
3. **VO over music per line.** V3 7.4 LU and V4 7.7 LU. The B-section pulse and pad stay loud under V3-V5 even with the 9 dB
   duck (overall 10.4 passes).
4. **V7 timing.** V7 now starts at 31.443 s (VO_TIMING), not 31.6. The C4 EP note at 31.2 (rings to ~31.95) needs its "-6 under
   VO" duck window from about 31.38 s.

**For the lead:**
5. **LRA 5-9 LU is not reachable from the SFX layer.**
   - Measured: A 2.7-2.9 LU, B 4.6-4.9 LU.
   - The VO covers 62 % of the runtime and the bed fills the gaps, so the 3 s short-term loudness stays within about
     -16 to -13 LUFS.
   - Neither a 4 dB quieter judgement section (2.4-2.8) nor removing the bus glue (2.65) moved it.
   - Reaching 5 LU would need, for example, the 3-8.8 s and 29-31.4 s stretches about 5 LU under the VO sections (a creative
     call), or a looser spec for VO-led reels.
6. **Max-momentary margin.** It is thin: 0.69-0.92 LU (hook A), 1.5-1.7 LU (hook B). Any change to the final chain (glue,
   levels) can flip it back to V1's VO at 0.35 s. Re-run `rough` and read `reveal_vs_rest_*` after every change. The real fix
   is R5b (no glue on the hero window).
7. **Picture check pending.** No `log_kya_kahenge.py` timeline exists yet, so every cue time comes from the BRIEF §5-6 / §11
   beat table and the EndCard's own `cues(31.2, 35.2)`. The frame checks are still to do on the master: frames n-1, n, n+1
   for f480, f768 and f888, and `qa_measure.py cues <master> <RW>/audio/log_kya_kahenge_cues.json`.
8. **CHECK lines on non-hero cues (looked at).** qa_measure's method reports these on the mixes:
   - ui_tick at 21.6 / 22.0 (-45 / -60 ms) and impact_soft at 28.8 (-45 ms): they sit 20+ dB under V4 / V6, and the finder
     locks onto syllables.
   - glass_tap at 31.95 (+55 ms): under V7.
   - impact_soft at 2.8 (hook B only, +55 ms): its 65 Hz body ripple (as in §3).
   - impact_soft at 0.0 (mix B, +55 ms): the same ripple. qa_measure skips t = 0 anyway.

   Rendered alone, every one of these lands within 1 frame (onsets -2 to 0 ms; table in §2).
9. **Whisper-wall ASR, literal reading.** BRIEF §18 asks for "no word with p ≥ 0.5". Two of the 12 `verify` transcriptions
   return Whisper's canned "Thanks for watching!" at the very end of the clip. The control shows Whisper produces the same
   phrase on pink noise, and the phrase follows the clip end, not the wall's content (§5). The QA verifier should accept it on
   this evidence or re-run `verify-control`.
