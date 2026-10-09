# SOUND · Reel 2 · C11 · Bijli Chali Gayi (@jawad_mp4)

2026-10-09 · sound-designer (Reels Studio) · code `pipeline/jawad_reels/bijli_chali_gayi_sfx.py` · binding plan BRIEF r2
§6.1-6.11 + §8, SLATE §3.2 / §5.1, VO_TIMING.md, MUSIC_bijli_chali_gayi.md. Nobody on the team can listen, me included:
every statement below is a measurement or a rendered image (Read), never "it sounds good".

## 1. Hand-off (what the next agents do)

| who | action |
|---|---|
| timeline builder | Use the event frames in the cue sheet (§5) and §8.3. Keep the module's own `cues()` empty, or import with `from bijli_chali_gayi_sfx import cues, BED, BED_GAIN_DB` only for reference. `BED = None`: render.py's automatic `audio.build_reel` cannot rebuild this layer (loop mixer, per-frame beds, drop-out gate). Render with `python3 render.py bijli_chali_gayi --no-sfx-build --audio <mix.wav>` (FOSTER_NICE=10 for the master). |
| music-supervisor | Final mixes (run 2). The rough mixes in §7.2 already meet -14 LUFS, TP -2.3 dBTP and the loudest-moment rule, and use music_full.wav at a static -0.5 dB (one harmonium source only: the SFX stems contain no harmonium). Open: LRA (§8.1) and the mono-VO level (SHARED_REQUESTS #5). |
| lead | Decide §8.2 (V2 under the f60 beep, V1B "awaaz" on the f40 beep) and accept the changes in §4. |
| QA (lens B) | After the master exists, run `qa_measure.py cues` on it with `<RW>/audio/bijli_chali_gayi_sfx_A_cues.json`; the wav-level checks are in §7. |

Rebuild (deterministic: a fresh render of both stems matches the saved files within 2 LSB of 24-bit; ~1 min each;
re-run after any VO or event-time change):
```bash
cd pipeline/jawad_reels
tools/heavy.sh python3 bijli_chali_gayi_sfx.py audition        # local sounds + spectrograms + qc
tools/heavy.sh python3 bijli_chali_gayi_sfx.py build --hook AB # SFX stems (-18 LUFS, TP -2.2 dBTP, loop-exact)
tools/heavy.sh python3 bijli_chali_gayi_sfx.py rough --hook AB # rough mixes (-14 LUFS)
tools/heavy.sh python3 bijli_chali_gayi_sfx.py verify          # faster-whisper: cheer wordless, crowd segments, V1
python3 bijli_chali_gayi_sfx.py cues --hook A                  # fitted cue table
```

## 2. Files (`<RW>` = `workspace/jawad_reels/bijli_chali_gayi`, all 48 kHz 24-bit stereo, 1,664,000 samples)

| file | what |
|---|---|
| `<RW>/audio/bijli_chali_gayi_sfx_A.wav` / `_sfx_B.wav` | SFX stems (hook A / hook B), -18.0 LUFS, no harmonium; `_fx.wav` + `_bed.wav` splits sum to each stem |
| `<RW>/audio/bijli_chali_gayi_sfx_{A,B}_cues.json` | every placed cue: start, hit, gain after VO fit and cluster duck, filters, carve, isolated onset / peak / end |
| `<RW>/audio/bijli_chali_gayi_sfx_{A,B}_report.json` | stem measurements (loudness, limiter, drop-out, seam, instants, sync, hum blip, loop bed, sections) |
| `<RW>/audio/bijli_chali_gayi_sfx_{A,B}_overview.png` | spectrogram + momentary loudness with bar lines, power state, VO words, drop-out, cue ticks |
| `<RW>/audio/bijli_chali_gayi_rough_A_full.wav`, `_rough_A_dry.wav`, `_rough_B_full.wav` (+ `.json`, `.png`) | rough mixes: VO stem + SFX stem (+ music_full.wav harmonium in FULL), -14 LUFS |
| `<RW>/audio/bijli_chali_gayi_verify.json` | faster-whisper results |
| `<RW>/audio/audition/*.png`, `qc.json` | spectrogram and QC of every local sound (the audition wavs were deleted: they rebuild in seconds) |

## 3. Sound world (policy)

- **No music bed** (SLATE §3.2, BRIEF §6.11). The 90-BPM grid is carried by diegetic sound: the backup beeps (beats 2 and
  3 of bar 0), the keycap thocks (quarters in bar 7, 8ths in bar 8) and the fan blade-pass. The only music is the
  harmonium swell in the music-supervisor's `music_full.wav` (starts f800, peaks f820 on "sabr").
- **Sound motif:** `backup_beep`, two 70 ms piezo pulses at D7 2349.32 Hz (+ 3rd harmonic -20 dB), the second +4 frames,
  exactly on the LED's pulse frames (f40/f44, f60/f64; hook B f0/f4, f40/f44), a far one through a wall at f310 and
  the box in the old room at f380. Never labelled UPS or inverter. Key D: the end-card `glass_tap` is tuned to D7 too.
- **Power-cut grammar in sound:** every power-on frame starts the mains world (thunk, hum, tube buzz, fans, the CRT
  whine), every power-off frame kills it on the frame (thunk with a hum falling 100 -> 60 Hz, fans winding down with the
  picture's tau 1.0 s, beds switching with 4 ms ramps). While the power is off only battery, flame and night sounds
  exist (crickets, room tone, the beep).
- **One drop-out** f790-f799: everything that started before it fades to zero over the 30 ms before 26.333 s; only the
  room tone remains (-45.8 LUFS, RMS -47.3 dBFS in the mix); the payoff hit, the heartbeat and the harmonium start
  exactly on f800.
- **Loop:** hook A's last frame is frame -1 of the lit room: the room_mains bed is phase-locked so f1039 -> f0 is
  continuous, cue tails past DUR wrap onto t = 0 (circular mixer), the end-card reverse swell ends on DUR and the f0
  `impact_soft` is its release. Hook B's seam is the brief's deliberate hard cut (lit room -> torch-lit f0).

## 4. Changes from BRIEF §6.10 (each measured; the lead should accept or reverse them)

| # | brief | built | why (measurement) |
|---|---|---|---|
| 1 | `crowd_cheer_real` at f241 and f885 | `mohalla_cheer` (granular re-synthesis of the same CC0 recording) | The sample is not wordless: faster-whisper small hears "Oh my God, look at that! It's just that!" (4 words at p 0.62-0.69), medium "Oh my God!" (p 0.82 / 0.52). The re-synthesis: small hears no word in any language (§7.3). SHARED_REQUESTS #4. |
| 2 | `leaf_rustle` x3 (pankhi) | `pankhi_swing` (air swish + palm-leaf crackle on one swell, hit = loudest pass) | leaf_rustle's loudest 30 ms window measured +93 ms and +63 ms after the beats f100 / f140 (random crackle grains); pankhi_swing peaks on the frame (timing check 0 flags). |
| 3 | `slot_tick` n 10 from 16.2 s | 10 `ui_tick` cues on the HUD's own thresholds, pitch 0.985 -> 0.85, last one (0 %) +3 dB | slot_tick's ticks decelerate; the HUD drain is in_cubic (accelerates): ticks now land where the value passes 64 - 6.4 k %, t = 16.2 + 1.133 (k/10)^(1/3). |
| 4 | `tube_light_on` with 2 starter tinks before the hit | `tinks=0` at f243 and f882 | The tinks would sound 0.18-0.36 s before the power-on frame: no visible cause. |
| 5 | `tube_flicker` n 3 at f220, f470 | n 2 | f220-f221 is a 2-frame false start, f470-f472 a 2-frame dip. |
| 6 | `fan_wind` down 3.0 s at f14 | duration 2.2 s, tau 1.0 s (= the picture's blade decay) | "Hook-only cues end before f80": -40 dB end measured 2.395 s (< 2.667). The f15 shimmer is truncated to 2.1 s (end 2.56 s). |
| 7 | `riser` 1.2 s ending f880 (starts 28.133) | 0.8 s (starts 28.533) | V11 now ends 28.445 s (VO activity): a 1.2 s riser would sit on "sikhaaya" and fit_under_vo would low-pass the whole riser. |
| 8 | end-card `reverse_swell` 0.8 s | 0.5 s (starts 34.167) | V12's measured speech ends 34.111 s; a 0.8 s swell would overlap it and be low-passed. |
| 9 | payoff `impact_soft` + `heartbeat` align hit at f800 | align start at f800 (hit +6 ms) | With hit-alignment both started 6 ms inside the drop-out. Now nothing starts in f790-f799 (fx bus is digital silence there). |
| 10 | levels as written | rebalanced (all in the table): match_strike 0 -> -8, hook beeps 0 -> -6, power_thunk f240 -5 / f300 -6 / f480 -3, impact_soft f240 -6 / f800 -7 / f881 -4, heartbeat -10, sub_drop f480 -9 / f880 -8, L7 whoosh_slow -9, Ctrl keycap -16 (S -8), presses after V8 4 dB under the rest; loudness-matched alias-safe saturation (`sat 3`, same momentary loudness, lower crest) on the 13 power / impact / swell hits marked in the table (12 in B) | At the brief's levels the stem limiter took 11.9 dB off the match strike and 3.9-7.8 dB off the power events, the f40 beep was the loudest moment of the stem, and the power return tied the payoff. Now: limiter max 2.85 dB (A) / 3.04 dB (B), loudest moment = the power return in the stem and in every mix (§7.1-§7.2). |
| 11 | Ctrl thock 1 f before S at -8 / S -6 | Ctrl -16, S -8 (Ctrl = grace note) | With a 2 dB difference the music-supervisor's grid fit read the beat 32 ms early (the Ctrl flam); with 8 dB it reads tempo 90.000 BPM, phase +3.0 ms, strength 6.26: ok. |
| 12 | glass_tap optional D6 | D7 (pitch 1.1207, seed 0) | glass_tap's measured partial is 2096.3 Hz; D6 needs pitch 0.56 (-10 st, a dull bell); D7 (+2 st) keeps the glass and echoes the beep motif. |
| 13 | beds at "-48" drop-out, 5 dB sidechain | drop-out room tone tuned to the brief's "about -45 LUFS" (-45.8 LUFS / RMS -47.3 dBFS in the mixes); bed sidechain 2 dB | Beds here are exact levels (bed alone = -18 + level + 8 LUFS). A 5 dB duck pumped the room under every keycap and made the loop's first 0.3 s 2.3 dB quieter than its last; with 2 dB the difference is 0.68 dB. |
| 14 | brownout bed step f13 at -30 | -40.5 | The f10-f13 room_mains levels follow the picture's mains factors 0.45 / 0.80 / 0.35 / 0.15 (-24 + 20 log10 factor); -30 on f13 would brighten while the picture darkens. |
| 15 | PC fans `fan_wind` down 1.5 s (ceiling-fan defaults) at f481 | rate 40 Hz, fc 700 Hz, lp 1500 | Small PC fans have a faster blade pass than the 13.5 Hz ceiling fan; the cue runs 1.2 s into V7, so its band stays under 1.5 kHz (nothing busy in 1-4 kHz under words). |
| 16 | power_thunk at f480 / f880 + sub_drop lp 120 | kept, but sub_drop gains lowered and both saturated | Two sub layers stack at f480 and f880 (agent rule); the sub_drop is now 6-8 dB under the thunk. |

VO-driven (fit_under_vo + local rules, automatic, see the "VO fit" column): 55 cues ducked in A (47 in B), keycaps under
words low-passed at 1.8 kHz (18 cues), 25 tails carved -6 dB (heroes -10 dB) under later speech, hook B's f40 beep
ducked -8 dB because it lands on the measured tail of "awaaz" (VO activity to 1.381 s, word end 1.244 s), hook A's
f40 beep restored to full level (it starts 56 ms after V1's measured speech end; only the 60 ms ducking pad caught it).

## 5. Cue sheet, hook A (final, as rendered; 97 cues)

Columns: t (s) / f = event time and frame (align='hit' puts the designed hit there: transient, loudest pass or the END
of risers and reverse swells; align='start' = the motion start); gain = final dB after the VO fit and the cluster duck;
duck = audio.duck_under's share of it; filters / sat; VO fit = what fit_under_vo or the local VO rules did; carve =
tail attenuation under later speech. The harmonium (music_full.wav) starts f800 and is not in the SFX stem.

| t | f | sound | params | align | pan | gain | duck | filters | VO fit / carve | event |
|---|---|---|---|---|---|---|---|---|---|---|
| 0.000 | 0 | `impact_soft` |  | hit | 0 | -8.0 | 0 | lp 900; sat 3 |  | f0 transient = the loop landing (release of the end-card swell) |
| 0.333 | 10 | `tube_flicker` |  | hit | -0.30 | -20.2 | -2.2 | lp 1100 | -6.0 dB, lp 1100 | brownout f10-f13 (mains x0.45, 0.80, 0.35, 0.15) |
| 0.400 | 12 | `crt_off` |  | hit | -0.15 | -14.0 | 0 | lp 1100 | -6.0 dB, lp 1100 | CRT collapse (phase 1 f12-f14) |
| 0.467 | 14 | `fan_wind` | mode down, duration 2.2, tau 1 | start | 0 | -22.2 | -2.2 | lp 1100 | -6.0 dB, lp 1100 | ceiling fan winds down (tau 1.0 s, gone by f80) |
| 0.467 | 14 | `relay_click` |  | hit | +0.40 | -23.0 | -5.0 |  | -8.0 dB | mains 0: the backup box switches to battery |
| 0.500 | 15 | `shimmer` |  | hit | 0 | -21.1 | -3.1 | hp 5500 | -6.0 dB, hp 5500 | H1 "Bijli" glows (truncated so it is gone by f80) |
| 0.667 | 20 | `mouse_click` |  | hit | +0.50 | -19.5 | -1.5 |  | -8.0 dB | torch clicks on (beat 1) |
| 1.333 | 40 | `backup_beep` |  | hit | +0.45 | -6.0 | 0 |  |  | LED pulses f40 / f44 (beat 2) |
| 2.000 | 60 | `backup_beep` |  | hit | +0.45 | -14.0 | 0 |  | -8.0 dB | LED pulses f60 / f64 (beat 3, cover frame) |
| 2.667 | 80 | `match_strike` |  | hit | 0 | -8.0 | 0 |  | carve 2.86-3.98 -6 | splice f80: the match ignites (flare = exposure push) |
| 3.333 | 100 | `pankhi_swing` |  | hit | +0.30 | -18.0 | 0 | lp 1100 | -6.0 dB, lp 1100 | pankhi swings in from the right |
| 4.000 | 120 | `pankhi_swing` |  | hit | +0.30 | -12.0 | 0 |  | carve 4.20-7.91 -6 | pankhi swing |
| 4.667 | 140 | `pankhi_swing` |  | hit | +0.30 | -18.0 | 0 | lp 1100 | -6.0 dB, lp 1100 | pankhi swing (tilt starts) |
| 5.333 | 160 | `whoosh_slow` |  | hit | 0 | -16.0 | 0 | lp 1100 | -6.0 dB, lp 1100 | tilt through the ceiling: loudest pass on the f160 cut |
| 7.333 | 220 | `tube_flicker` | n 2 | hit | -0.40 | -30.0 | 0 | lp 250 | -6.0 dB, lp 250 | far window false start f220-f221 (hum blip only) |
| 8.000 | 240 | `impact_soft` |  | hit | 0 | -8.3 | -2.3 | sat 3 |  | "AA GAYI!" slams (SLAM spring) **(hero)** |
| 8.000 | 240 | `power_thunk` | on 1 | hit | 0 | -7.3 | -2.3 | sat 3 |  | power back: bulbs cascade f240-f245 **(hero)** |
| 8.033 | 241 | `mohalla_cheer` | dur 1.9667, cut 1 | hit | 0 | -15.2 | -5.2 |  | carve 10.85-12.55 -6 | the street cheers (wordless), cut dead at f300 |
| 8.067 | 242 | `fan_wind` | mode up, duration 1.9, hold 0.0333, release 0.03 | start | 0 | -16.0 | -4.0 |  |  | rooftop fans spin up (held until the f300 death) |
| 8.100 | 243 | `tube_light_on` | tinks 0 | hit | -0.35 | -15.1 | -3.1 | lp 2500 |  | distant tube lights / windows snap on |
| 10.000 | 300 | `power_thunk` | on 0 | hit | 0 | -6.0 | 0 | sat 3 |  | the gag: everything dies again (beat 15) **(hero)** |
| 10.033 | 301 | `fan_wind` | mode down, duration 2 | start | 0 | -17.1 | -3.1 |  | carve 10.85-12.55 -6 | rooftop fans wind down |
| 10.333 | 310 | `backup_beep` | far 1 | hit | -0.30 | -9.5 | -1.5 |  | carve 10.85-12.55 -6 | a backup box beeps downstairs (far) |
| 10.667 | 320 | `shimmer` |  | hit | 0 | -10.3 | -2.3 |  | carve 10.85-14.60 -6 | L7 beam glints |
| 10.667 | 320 | `whoosh_slow` |  | hit | 0 | -9.0 | 0 |  | carve 10.85-14.60 -6 | L7 torch-beam sweep crosses frame centre (bar 4) |
| 12.667 | 380 | `backup_beep` |  | hit | +0.45 | -6.0 | 0 |  | carve 13.07-14.60 -6 | the box in the old room (between V5 and V6) |
| 13.333 | 400 | `power_thunk` | on 1 | hit | 0 | -12.0 | 0 | lp 1100 | -6.0 dB, lp 1100 | lights on: the modern desk (on-word cut) |
| 14.667 | 440 | `ui_tick` |  | hit | +0.30 | -12.0 | 0 |  |  | render 63 -> 64 % |
| 15.667 | 470 | `tube_flicker` | n 2 | hit | -0.50 | -14.0 | 0 |  |  | brownout dip f470-f472 (desk lamp, monitor) |
| 16.000 | 480 | `crt_off` | whine 0 | hit | 0 | -9.6 | -3.6 | sat 3 | carve 16.34-23.12 -6 | the monitor collapses (f480-f485) |
| 16.000 | 480 | `power_thunk` | on 0 | hit | 0 | -6.6 | -3.6 | sat 3 | carve 16.34-23.12 -10 | re-hook 2: the power dies mid-render **(hero)** |
| 16.000 | 480 | `sub_drop` |  | hit | 0 | -12.6 | -3.6 | lp 120; sat 3 | carve 16.34-23.12 -6 | re-hook weight |
| 16.033 | 481 | `fan_wind` | mode down, duration 1.5, rate 40, fc 700 | start | 0 | -21.0 | -5.0 | lp 1500 | carve 16.34-23.12 -6 | PC fans wind down |
| 16.726 | 501.78 | `ui_tick` | pitch 0.985 | hit | +0.30 | -22.0 | 0 | hp 5500 | -6.0 dB, hp 5500 | HUD drains 64 -> 58 % |
| 16.863 | 505.88 | `ui_tick` | pitch 0.97 | hit | +0.30 | -22.0 | 0 | hp 5500 | -6.0 dB, hp 5500 | HUD drains 58 -> 51 % |
| 16.959 | 508.76 | `ui_tick` | pitch 0.955 | hit | +0.30 | -22.5 | -0.5 | hp 5500 | -6.0 dB, hp 5500 | HUD drains 51 -> 45 % |
| 17.035 | 511.05 | `ui_tick` | pitch 0.94 | hit | +0.30 | -23.2 | -1.2 | hp 5500 | -6.0 dB, hp 5500 | HUD drains 45 -> 38 % |
| 17.100 | 512.99 | `ui_tick` | pitch 0.925 | hit | +0.30 | -23.6 | -1.6 | hp 5500 | -6.0 dB, hp 5500 | HUD drains 38 -> 32 % |
| 17.156 | 514.68 | `ui_tick` | pitch 0.91 | hit | +0.30 | -23.9 | -1.9 | hp 5500 | -6.0 dB, hp 5500 | HUD drains 32 -> 26 % |
| 17.206 | 516.19 | `ui_tick` | pitch 0.895 | hit | +0.30 | -24.2 | -2.2 | hp 5500 | -6.0 dB, hp 5500 | HUD drains 26 -> 19 % |
| 17.252 | 517.56 | `ui_tick` | pitch 0.88 | hit | +0.30 | -24.4 | -2.5 | hp 5500 | -6.0 dB, hp 5500 | HUD drains 19 -> 13 % |
| 17.294 | 518.83 | `ui_tick` | pitch 0.865 | hit | +0.30 | -24.4 | -2.5 | hp 5500 | -6.0 dB, hp 5500 | HUD drains 13 -> 6 % |
| 17.333 | 520 | `ui_tick` | pitch 0.85 | hit | +0.30 | -20.7 | -1.7 | hp 5500 | -6.0 dB, hp 5500 | HUD drains 6 -> 0 % |
| 18.633 | 559 | `camera_shutter` |  | hit | 0 | -18.8 | -0.8 |  | -8.0 dB | L8 iris blades close (f551-f559) |
| 18.700 | 561 | `ui_click` |  | hit | 0 | -22.8 | -0.8 |  | -8.0 dB | L8 iris opens on the keycaps |
| 19.033 | 571 | `reverse_swell` | duration 0.3 | hit | 0 | -18.0 | 0 | lp 1100 | span -6.0 dB, lp 1100 | L8 iris fully open (ends f571) |
| 19.300 | 579 | `keycap_thock` | pitch 0.94 | hit | -0.30 | -25.6 | -1.6 | lp 1800 | -8.0 dB | Ctrl keycap down (leads S by 1 f: a grace note, 8 dB under S so S stays the beat) |
| 19.333 | 580 | `keycap_thock` |  | hit | +0.25 | -18.1 | -2.1 | lp 1800 | -8.0 dB | S keycap down (quarter) |
| 19.400 | 582 | `ui_tick` |  | hit | +0.30 | -22.8 | -0.8 | hp 5500 | -6.0 dB, hp 5500 | "Saved" chip pops (x 780) |
| 19.967 | 599 | `keycap_thock` | pitch 0.94 | hit | -0.30 | -25.6 | -1.6 | lp 1800 | -8.0 dB | Ctrl keycap down (leads S by 1 f: a grace note, 8 dB under S so S stays the beat) |
| 20.000 | 600 | `keycap_thock` |  | hit | +0.25 | -18.1 | -2.1 | lp 1800 | -8.0 dB | S keycap down (quarter) |
| 20.067 | 602 | `ui_tick` |  | hit | +0.30 | -22.8 | -0.8 | hp 5500 | -6.0 dB, hp 5500 | "Saved" chip pops (x 780) |
| 20.633 | 619 | `keycap_thock` | pitch 0.94 | hit | -0.30 | -25.6 | -1.6 | lp 1800 | -8.0 dB | Ctrl keycap down (leads S by 1 f: a grace note, 8 dB under S so S stays the beat) |
| 20.667 | 620 | `keycap_thock` |  | hit | +0.25 | -18.1 | -2.1 | lp 1800 | -8.0 dB | S keycap down (quarter) |
| 20.733 | 622 | `ui_tick` |  | hit | +0.30 | -22.8 | -0.8 | hp 5500 | -6.0 dB, hp 5500 | "Saved" chip pops (x 780) |
| 21.300 | 639 | `keycap_thock` | pitch 0.94 | hit | -0.30 | -25.6 | -1.6 | lp 1800 | -8.0 dB | Ctrl keycap down (leads S by 1 f: a grace note, 8 dB under S so S stays the beat) |
| 21.333 | 640 | `keycap_thock` |  | hit | +0.25 | -18.1 | -2.1 | lp 1800 | -8.0 dB | S keycap down (8th) |
| 21.400 | 642 | `ui_tick` |  | hit | +0.30 | -22.8 | -0.8 | hp 5500 | -6.0 dB, hp 5500 | "Saved" chip pops (x 780) |
| 21.633 | 649 | `keycap_thock` | pitch 0.94 | hit | -0.30 | -25.6 | -1.6 | lp 1800 | -8.0 dB | Ctrl keycap down (leads S by 1 f: a grace note, 8 dB under S so S stays the beat) |
| 21.667 | 650 | `keycap_thock` |  | hit | +0.25 | -18.1 | -2.1 | lp 1800 | -8.0 dB | S keycap down (8th) |
| 21.733 | 652 | `ui_tick` |  | hit | +0.30 | -22.8 | -0.8 | hp 5500 | -6.0 dB, hp 5500 | "Saved" chip pops (x 780) |
| 21.967 | 659 | `keycap_thock` | pitch 0.94 | hit | -0.30 | -25.6 | -1.6 | lp 1800 | -8.0 dB | Ctrl keycap down (leads S by 1 f: a grace note, 8 dB under S so S stays the beat) |
| 22.000 | 660 | `keycap_thock` |  | hit | +0.25 | -18.1 | -2.1 | lp 1800 | -8.0 dB | S keycap down (8th) |
| 22.067 | 662 | `ui_tick` |  | hit | +0.30 | -22.8 | -0.8 | hp 5500 | -6.0 dB, hp 5500 | "Saved" chip pops (x 780) |
| 22.300 | 669 | `keycap_thock` | pitch 0.94 | hit | -0.30 | -25.6 | -1.6 | lp 1800 | -8.0 dB | Ctrl keycap down (leads S by 1 f: a grace note, 8 dB under S so S stays the beat) |
| 22.333 | 670 | `keycap_thock` |  | hit | +0.25 | -18.1 | -2.1 | lp 1800 | -8.0 dB | S keycap down (8th) |
| 22.400 | 672 | `ui_tick` |  | hit | +0.30 | -22.8 | -0.8 | hp 5500 | -6.0 dB, hp 5500 | "Saved" chip pops (x 780) |
| 22.633 | 679 | `keycap_thock` | pitch 0.94 | hit | -0.30 | -25.6 | -1.6 | lp 1800 | -8.0 dB | Ctrl keycap down (leads S by 1 f: a grace note, 8 dB under S so S stays the beat) |
| 22.667 | 680 | `keycap_thock` |  | hit | +0.25 | -18.1 | -2.1 | lp 1800 | -8.0 dB | S keycap down (8th) |
| 22.733 | 682 | `ui_tick` |  | hit | +0.30 | -22.8 | -0.8 | hp 5500 | -6.0 dB, hp 5500 | "Saved" chip pops (x 780) |
| 22.967 | 689 | `keycap_thock` | pitch 0.94 | hit | -0.30 | -25.6 | -1.6 | lp 1800 | -8.0 dB | Ctrl keycap down (leads S by 1 f: a grace note, 8 dB under S so S stays the beat) |
| 23.000 | 690 | `keycap_thock` |  | hit | +0.25 | -18.1 | -2.1 | lp 1800 | -8.0 dB | S keycap down (8th) |
| 23.067 | 692 | `ui_tick` |  | hit | +0.30 | -22.8 | -0.8 | hp 5500 | -6.0 dB, hp 5500 | "Saved" chip pops (x 780) |
| 23.300 | 699 | `keycap_thock` | pitch 0.94 | hit | -0.30 | -21.6 | -1.6 |  | carve 23.94-26.17 -6 | Ctrl keycap down (leads S by 1 f: a grace note, 8 dB under S so S stays the beat) |
| 23.333 | 700 | `keycap_thock` |  | hit | +0.25 | -14.1 | -2.1 |  | carve 23.94-26.17 -6 | S keycap down (8th) |
| 23.400 | 702 | `ui_tick` |  | hit | +0.30 | -16.8 | -0.8 | hp 5500 |  | "Saved" chip pops (x 780) |
| 23.633 | 709 | `keycap_thock` | pitch 0.94 | hit | -0.30 | -21.6 | -1.6 |  | carve 23.94-26.17 -6 | Ctrl keycap down (leads S by 1 f: a grace note, 8 dB under S so S stays the beat) |
| 23.667 | 710 | `keycap_thock` |  | hit | +0.25 | -14.1 | -2.1 |  | carve 23.94-26.17 -6 | S keycap down (8th) |
| 23.733 | 712 | `ui_tick` |  | hit | +0.30 | -16.8 | -0.8 | hp 5500 | carve 23.94-26.17 -6 | "Saved" chip pops (x 780) |
| 24.000 | 720 | `impact_soft` |  | hit | 0 | -16.0 | 0 | lp 900 | -6.0 dB, lp 900 | cut to the candle macro (power off again) |
| 26.667 | 800 | `heartbeat` | n 1 | start | 0 | -12.3 | -2.3 |  | carve 27.27-28.42 -6 | velvet hit (starts on f800) |
| 26.667 | 800 | `impact_soft` |  | start | 0 | -9.3 | -2.3 | sat 3 | carve 27.27-28.42 -10 | PAYOFF lockup lands (velvet hit, bar 10); starts on f800, after the drop-out **(hero)** |
| 27.233 | 817 | `swish_small` |  | start | 0 | -22.0 | 0 | hp 5500 | -6.0 dB, hp 5500 | underline draws on (f817-f838) |
| 29.333 | 880 | `power_thunk` | on 1 | hit | 0 | -3.1 | -3.1 | sat 3 |  | POWER RETURNS (loudest moment, bar 11) **(hero)** |
| 29.333 | 880 | `reverse_swell` | duration 0.333 | hit | 0 | -11.6 | -5.6 | sat 3 |  | L4 bloom into the cut (ends f880) |
| 29.333 | 880 | `riser` | duration 0.8 | hit | 0 | -15.1 | -7.1 |  |  | into the power return (starts f856, clear of V11) |
| 29.333 | 880 | `shimmer` |  | hit | 0 | -14.1 | -6.1 |  | carve 31.37-34.08 -6 | L4 halation bloom-out peaks |
| 29.333 | 880 | `sub_drop` |  | hit | 0 | -11.2 | -3.1 | lp 120; sat 3 | carve 31.37-34.08 -6 | power return weight |
| 29.367 | 881 | `fan_wind` | mode up, duration 2.5, hold 0.3, release 0.6 | start | 0 | -13.0 | -7.0 |  | carve 31.37-34.08 -6 | ceiling fan spins up 2.5 s (out_cubic), hands over to the room_mains bed |
| 29.367 | 881 | `impact_soft` |  | hit | 0 | -7.0 | -3.0 | sat 3 |  | JD smiling in the lit room |
| 29.400 | 882 | `tube_light_on` | tinks 0 | hit | -0.35 | -13.9 | -6.0 |  |  | the tube light strikes |
| 29.433 | 883 | `crt_on` |  | hit | 0 | -8.8 | -0.8 |  |  | CRT degauss behind his head |
| 29.500 | 885 | `mohalla_cheer` | dur 1.6, cut 0 | hit | 0 | -10.2 | -2.2 |  | carve 31.37-34.08 -6 | the neighbourhood cheers again (wordless) |
| 30.767 | 923 | `swish_small` |  | start | 0 | -12.0 | 0 |  | carve 31.37-34.08 -6 | end card: JD monogram ring draws on |
| 31.237 | 937.1 | `shimmer` |  | hit | 0 | -10.0 | 0 |  | carve 31.37-34.08 -6 | end card: keyword "batao" rises |
| 31.417 | 942.5 | `glass_tap` | pitch 1.1207 | hit | 0 | -20.0 | 0 |  | -8.0 dB | end card: monogram lands (glass tap tuned to D7) |
| 34.667 | 1040 | `reverse_swell` | duration 0.5 | hit | 0 | -8.0 | 0 | sat 3 |  | loop swell into frame 0 (ends on DUR) |
### 5.1 Hook B (Trial Reel) differences

Hook B drops the nine hook-A-only cues (f0 impact, f10-f60 blackout cues) and adds two; the body (f80 onward) is the
same 88 cues, re-fitted to the B VO (`words_B.json`, `vo_stem_B.wav`), 90 cues in all.

| t | f | sound | params | align | pan | gain | duck | filters | VO fit / carve | event |
|---|---|---|---|---|---|---|---|---|---|---|
| 0.000 | 0 | `backup_beep` |  | hit | +0.45 | -6.0 | 0 |  | carve 0.24-1.30 -6 | LED pulses f0 / f4 (the f0 transient) |
| 1.333 | 40 | `backup_beep` |  | hit | +0.45 | -14.0 | 0 |  | speech tail -8.0 dB; carve 1.61-2.26 -6 | LED pulses f40 / f44 |
## 6. Beds and local sounds

### 6.1 Beds (exact levels: a bed alone integrates at -18 + level + 8 LUFS in the stem; loop phase = t - ref)

| bed | t (s) | level | ramps | why |
|---|---|---|---|---|
| `room_mains` (A) | 0-0.333 / f10 / f11 / f12 / f13 / off at f14 | -24 / -30.9 / -25.9 / -33.1 / -40.5 / off | 4 ms | lit room; brownout follows the picture's mains factors 0.45, 0.80, 0.35, 0.15 |
| `room_tone` (B) | 0-2.667 | -34 | 4 ms | hook B: torch-lit dead room |
| `night_crickets` | A 0-0.467 -38, 0.467-2.667 -32 (B 0-2.667 -32) · 2.667-5.333 -32 · 5.333-10.667 -24 · 10.667-13.333 -32 · 13.333-24.0 off · 24.0-26.333 -32 · drop-out off · 26.667-29.333 -34 · 29.333-DUR -38 | | 4 ms | one 34.667 s loop (ref 0), so it is seamless at the seam |
| `room_tone` | 2.667-5.333 | -34 | 4 ms / 50 ms | candle (S2) |
| `night_air` | 5.333-10.667 | -30 | 50 / 100 ms | rooftops (S3) |
| `room_tone` | 10.667-13.333 | -34 | 100 ms / 4 ms | old room by torch (S4) |
| `edit_suite` | 13.333-16.000 | -28 | 4 ms | the modern desk, power on (S5) |
| `room_tone` | 16.000-18.667 | -36 | 4 ms | the dead desk (re-hook 2) |
| `edit_suite` | 18.667-24.000 | -30 | 50 ms / 4 ms | keycaps, power on |
| `room_tone` | 24.000-26.333 · **drop-out 26.333-26.667** · 26.667-29.333 | -32 · **-37** · -32 | 4 ms | candle; the drop-out holds only this room tone |
| `room_mains` | f882 (29.400) -> 31.867 -> DUR | -36 -> -24 (ramp while the fan reaches speed) -> -24 | 4 ms in | the lit room again; ref = DUR, so f1039 -> f0 continues the same loop |

Bed bus: sidechained 2 dB under the SFX bus (circular). Bed loudness in the stem: -37.5 LUFS (A) / -37.4 (B).

### 6.2 Local sounds (registered by `register()`; every render audio.qc() == [], sfx_jawad guard filter + -1 dBTP cap)

Measured on the audition renders (`<RW>/audio/audition/qc.json`, spectrograms viewed):

| sound | category | hit (s) | Mmax at gain 0 (LUFS) | TP (dBTP) | energy 1-4 kHz | < 60 Hz | used at |
|---|---|---|---|---|---|---|---|
| `backup_beep` | ui | 0.000 | -28.0 | -26.4 | 98.9 % | 0.0 % | f40, f60 (A), f0, f40 (B), f310 (far=1), f380 |
| `match_strike` | impact | 0.060 | -26.0 | -14.3 | 32.1 % | 0.1 % | f80 |
| `relay_click` | ui | 0.000 | -30.0 | -9.8 | 8.3 % | 1.4 % | f14 |
| `power_thunk` on=1 / on=0 | impact | 0.000 | -24.0 | -13.3 / -11.7 | 0.0 / 0.1 % | 62.8 / 70.3 % | f240, f400, f880 / f300, f480 |
| `crt_off` (whine 1 / 0) | impact | 0.150 | -26.0 | -12.0 | 6.8 % | 0.1 % | f12 / f480 |
| `crt_on` | impact | 0.000 | -28.0 | -14.2 | 0.4 % | 39.6 % | f883 |
| `tube_light_on` (tinks 0) | transition | 0.000 | -30.0 | -19.4 | 8.1 % | 0.6 % | f243, f882 |
| `tube_flicker` (n 3 / 2) | transition | 0.000 | -32.0 | -19.6 / -17.8 | 0.2 % | 1.5 % | f10 / f220, f470 |
| `fan_wind` down 2.2 s, tau 1.0 | transition | 0.000 (start) | -32.0 | -21.0 | 4.6 % | 0.0 % | f14 (and down 2.0 s at f301) |
| `fan_wind` up 2.5 s, hold 0.3, release 0.6 | transition | 0.000 (start) | -32.0 | -22.5 | 7.7 % | 0.0 % | f881 (up 1.9 s at f242) |
| `fan_wind` PC (rate 40, fc 700) | transition | 0.000 (start) | -32.0 | -21.4 | 23.0 % | 0.0 % | f481 (lp 1500) |
| `keycap_thock` (pitch 1 / 0.94) | ui | 0.000 | -26.0 | -12.4 / -12.6 | 5.9 / 2.7 % | 0.3 % | f579-f710 |
| `pankhi_swing` | transition | 0.220 | -32.0 | -11.9 | 56.1 % | 0.0 % | f100, f120, f140 |
| `mohalla_cheer` (cut / natural) | texture | 0.030 | -26.0 | -15.8 / -16.2 | 17.7 / 18.0 % | 0.0 % | f241 (cut dead at f300) / f885 |
| `room_mains` (bed, 8 s) | bed | - | -19.3 (I -20) | -8.5 | 5.9 % | 2.5 % | seam ratio 0.54 (seamless) |
| `night_crickets` (bed, 34.667 s) | bed | - | -18.9 (I -20) | -9.4 | 0.3 % | 0.3 % | seam ratio 0.13 (seamless) |

Toolkit / shared sounds used as they are: `impact_soft`, `heartbeat`, `sub_drop`, `shimmer`, `whoosh_slow`,
`swish_small`, `riser`, `reverse_swell`, `ui_tick`, `ui_click`, `camera_shutter`, `glass_tap` (audio.py),
`mouse_click` (epic_sfx), beds `room_tone`, `night_air` (audio.py), `edit_suite` (epic_sfx). No `flash_hit`, no
`crowd_cheer_real`, no music bed, nothing from the Organic Fostering / Floret examples.

## 7. Measurements

### 7.1 SFX stems (circular, loop-exact)

| check | hook A | hook B | target |
|---|---|---|---|
| integrated (toolkit / ffmpeg ebur128) | -18.01 / -18.0 LUFS | -18.01 / -18.0 LUFS | -18.0 +-0.1 |
| true peak (toolkit, circular / ffmpeg) | -2.20 / -2.2 dBTP | -2.20 / -2.2 dBTP | <= -2.0 |
| limiter max GR | 2.85 dB at 29.513 s (0.8 % of samples > 1 dB) | 3.04 dB at 29.513 s (0.9 %) | under about 3 dB |
| glue max GR | 3.59 dB | 3.56 dB | - |
| max momentary | -9.22 LUFS at 29.45 s (the power return) | -9.16 LUFS at 29.45 s | inside 29.333-29.933 |
| "hit before 0 s" warnings | none | none | none |
| cue timing vs event (isolated renders: onset / loudest pass / end) | 0 CHECK flags of 97 | 0 of 90 | <= 1 frame |
| sync on the fx stem (largest 5 ms rise near each brief sync event: beeps, match f80, power f240/f300/f400/f480/f880, 22 keycap presses) | all within -10.0 ... +3.3 ms | all within -10.0 ... +5.0 ms | +-1 frame (33 ms) |
| 90-BPM grid fit on the keycaps (music-supervisor's `grid`, bars 7-8) | 90.000 BPM, phase +3.0 ms, strength 6.26: ok | (same cues) | tempo +-0.2, phase +-15 ms |
| sounds starting in one 30 fps frame (measured onsets, incl. the harmonium start) | max 3 (f14: relay_click, fan_wind, shimmer; f800: harmonium, impact_soft, heartbeat; f880: power_thunk, sub_drop, shimmer) | max 3 | <= 3 |
| onsets within 25 ms of each other | max 3 | max 3 | - |
| hero hits vs speech (words + measured VO activity, 120 ms before / 300 ms after) | 6 heroes clear: 8.000 (x2), 10.000, 16.000, 26.673, 29.333 | same | no violation |
| drop-out f790-f799 | fx bus digital silence (-240 dBFS); stem RMS -48.2 dBFS, -46.6 LUFS (room tone only); nothing starts inside | same | only the held room tone |
| hook-only cues end (-40 dB) before f80 (2.667 s) | latest: shimmer 2.560, fan_wind 2.395, f60 beep 2.328 | f40 beep 1.661 | < 2.667 |
| f220 hum blip, 1-4 kHz band 7.30-7.50 s vs 7.10-7.30 s | -48.4 vs -46.9 dB | same | <= +1 dB |
| loop bed level, last vs first | 0.3 s: -37.6 vs -38.2 dB (0.7 dB); 0.5 s: -37.3 vs -39.5 dB (the first 0.5 s contains the designed brownout f10-f14) | hard cut by design | within 1 dB |
| loop swell | ends at 34.6667 s (-40 dB end = hit = DUR) | same | DUR +-10 ms |
| seam (sample step f1039 -> f0 vs median step of the last 50 ms) | 0.0136 vs 0.172 (continuous) | 0.0072 vs 0.174 | no click |

Overview images viewed: `bijli_chali_gayi_sfx_A_overview.png` (and B). Every cue tick has energy; the beep pairs show
as short 2.35 kHz lines at f40/f60; the keycaps as a vertical comb on the beat (low thocks only while V8 speaks); the
sub (< 60 Hz) appears only under power events, with the sub_drop 6-8 dB under the thunk; nothing hisses constantly
(the crickets are pulsed chirps at 4.2-4.9 kHz); the drop-out band is empty; the loudest burst is f880.

### 7.2 Rough mixes (`rough`: VO stem re-normalised to -16 LUFS as equal-power centre, SFX stem -18 LUFS sidechained
-4 dB under the VO (epic_mix SPEC), music_full.wav at a static -0.5 dB in FULL, gain + 4x true-peak limiter on a loop
to -14 LUFS; no bus glue, see 8.1)

| check | A FULL | A DRY | B FULL | target (BRIEF 8) |
|---|---|---|---|---|
| integrated (toolkit / ffmpeg) | -14.01 / -14.0 | -14.01 / -14.0 | -14.01 / -14.0 | -14.0 +-0.5 |
| true peak (toolkit circular / ffmpeg) | -2.30 / -2.3 | -2.30 / -2.3 | -2.30 / -2.3 | <= -2.0 dBTP |
| LRA (ffmpeg) | 3.0 | 2.9 | 3.0 | 5-9 LU: **not met, see 8.1** |
| limiter max GR | 1.76 dB | 1.91 dB | 1.79 dB | - |
| max momentary | -8.63 LUFS at 29.40 s (f882) | -8.58 at 29.40 | -8.58 at 29.40 | inside 29.333-29.933 |
| loudest momentary elsewhere (> 0.2 s outside) | -9.60 | -9.46 | -9.79 | below the power return |
| speech over SFX + bed (+ harmonium), median over voiced frames | 17.5 LU | 18.2 LU | 18.4 LU | >= 8 LU |
| per line, median (lowest) | V11 8.7 LU (harmonium peak), V2 9.8, V1 13.0 | V2 9.8 | V11 8.9 | >= 8 LU |
| SFX in VO windows, per-line median | >= 9.8 LU everywhere (V2) | same | >= 13.5 | >= 6 LU below speech |
| SFX in VO windows, 10th percentile | 6.0 LU overall; V1 -2.0 and V2 2.7 at their onsets (the f0 loop landing and the f60 beep pair, see 8.2) | same | 6.5 overall; V1B 2.7 | (info) |
| drop-out f791-f798 | RMS -47.26 dBFS, -45.8 LUFS, harmonium silent | -47.11 / -45.7 | -47.23 / -45.8 | RMS <= -45 dBFS, peak <= -30; "about -45 LUFS" |
| harmonium 10 ms-RMS peak | f820.03 | - | f820.03 | f820 +-1 |
| VO / SFX / harmonium loudness in the mix | -14.34 / -17.01 / -14.94 LUFS (harmonium gated over its 1.9 s) | -14.19 / -16.91 / - | -14.30 / -16.92 / -14.93 | - |
| harmonium gain | -0.5 dB static (search: loudest gain keeping V11 >= 8.5 LU: A -0.5, B -0.25) | - | -0.5 dB | V11 >= 8 LU |
| seam | step 0.0157, continuous | 0.0159 | 0.0083 (hard cut by design) | no click |

### 7.3 faster-whisper checks (`verify`, `<RW>/audio/bijli_chali_gayi_verify.json`)

| check | result | target |
|---|---|---|
| `mohalla_cheer` renders (f241 cut, f885 natural), small, auto / hi / en | no word in any run | no word p >= 0.5 |
| same, medium | only "for watching!" (en, p 0.69-0.95) and a repeated "लिए" / one garbled token (hi): the same output medium gives on pure pink noise and on `room_tone` ("Thanks for watching!", p 0.83-0.95, control run) | hallucination baseline |
| mix A FULL and B FULL, 8.0-10.0 s and 29.5-31.1 s, small, hi and en (BRIEF 8) | no word p >= 0.5 in any of the 8 runs | none |
| raw `crowd_cheer_real` (for the record) | small: "Oh my God, look at that! It's just that!"; medium: "Oh my God!" | (why it is not used) |
| V1 in mix A FULL, 0-1.4 s, small `hi` (GATE minor 9) | बिज्ली 0.00-0.58 (p 0.69), चली 0.58-0.90 (p 0.84), गई 0.90-1.14 (p 0.68) | the three words inside 0-1.3 s, every p >= 0.5: **pass** (बिज्ली is बिजली written with a halant) |
| same, medium `hi` | विजली (p 0.84), चली (0.89), गई (0.83) | medium also writes विजली on the raw VO (VO_TIMING), so the SFX add nothing |

## 8. Open items

### 8.1 LRA 5-9 LU is not reachable by mixing (music-supervisor / lead)
The three rough mixes read LRA 2.9-3.0 LU. The VO is almost continuous (22.2 s of speech in 34.7 s; the VO stem alone
reads 6.4 LU only because of its gaps), and the 3 s short-term loudness of the mix stays between about -17 and -12.7
LUFS for the whole reel, so the 10th-95th percentile spread is 2.9 LU. Measured on hook A: with epic_mix's bus glue
LRA 2.9, without glue 3.1, SFX stem at -17 or -20 LUFS 3.1, VO sidechain 8 dB 3.1. Reaching 5 LU would need longer
quiet stretches in the edit (or a much quieter SFX layer between lines, which would break the loudest-moment rule).
The rough mixes therefore run without bus glue (it took 4.4 dB off the power return and tied it with the loudest VO
word). Recommend the lead relaxes this reel's LRA line to >= 3 LU or accepts it as measured.

### 8.2 Lead decisions carried from VO_TIMING
- **V2 "Yaad hai?" (hook A, fallback 1.545-2.255 s)** runs under the f60/f64 beep pair (2.000-2.203 s). Built: the
  beep stays on its LED frames, ducked -8 dB (mid band) by fit_under_vo; V2's speech-over-SFX median is 9.8 LU, its 10th
  percentile 2.7 LU (the beep pair itself). Alternatives: drop that pair in hook A, or re-place V2 (lead).
- **V1B "Yeh awaaz..." (hook B)**: "awaaz" ends on the f40 pulse (VO activity to 1.381 s). Built: that beep ducked -8 dB
  (speech-tail rule). If V1B is re-timed so the f40 beep sits in the pause, the beep returns to -6 dB automatically.
- **V8 "Ctrl+S" lands f644** (21.467 s): the 8th-note presses still start on f640 (on the grid, grid fit ok). If the
  builder moves them to f644, re-run `build` (cue times come from `PRESSES`).
- **V1 onset**: the f0 loop landing (`impact_soft` lp 900, -8 dB, saturated) sits 85 ms before "Bijli". The 10th
  percentile of speech-over-SFX in V1 is -2.0 LU (those first momentary windows); the brief's intelligibility test passes
  (§7.3), so nothing was pulled down. If QA wants more room, `impact_soft` f0 to -11 dB is the first knob.

### 8.3 For the builder (`bijli_chali_gayi.py`, not written yet)
- Every cue time here comes from BRIEF §6.1-6.9 frames (`F(f)` in the module, `PRESSES`, `DROP`, `T_END`, the Plan
  windows from `jawad_tx` and the card cues from `endcard`). If an event moves, change it in `raw_cues()` and rebuild;
  nothing reads the timeline module.
- Event frames the picture must hit for this sound to stay in sync: LED pulses f40/f44, f60/f64 (B: f0/f4, f40/f44);
  match ignition f80; power ON f240 / f400 / f880, OFF f14 / f300 / f480; far window f220-f221; HUD 63 -> 64 % at f440,
  drain f486-f520 (in_cubic); keycaps Ctrl p-1 / S p for p in 580, 600, 620, 640 ... 710, chips p+2; payoff f800;
  tube strike f882, CRT on f883; end card from f920.

### 8.4 Shared requests filed
SHARED_REQUESTS.md #4 (crowd_cheer_real speaks English) and #5 (mono VO +3.01 LU when duplicated to stereo).
