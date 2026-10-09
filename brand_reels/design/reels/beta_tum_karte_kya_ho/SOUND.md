# SOUND · Reel 4 · C02 "Beta, tum karte kya ho?" (`beta_tum_karte_kya_ho`)

Date 2026-10-09 · Owner: sound-designer · Module `pipeline/jawad_reels/beta_tum_karte_kya_ho_sfx.py` · Status: **SFX stems A + B
built, rough mixes A + B built and measured** (final mix = music-supervisor run 2, BRIEF 6.14).

Binding: SLATE 3.4 + 5.1 (motif = the message pop `notif_ping` + the typing-dot tick; one drop-out at the reveal; <= 3
sounds on one instant; nothing busy in 1-4 kHz under words; -14 LUFS, TP <= -2 dBTP, VO >= 8 LU over the bed) → BRIEF r2
6.2 (frame-exact events), 6.3 (hooks), 6.7 (VO), 6.12 (cue list), 6.13 / `MUSIC.md` (D minor, chords per bar), 6.14 + 8.13
(mix QA). Word timings: the FINAL Vlad VO (`vo/words.json` + `vo/vo_stem.wav`; B: `words_B.json` + `_vo_B.wav`), not the
brief's estimated slots. Nobody on the team can listen: every statement below is a measurement or a look at a spectrogram.

## 1. Hand-off

| item | value |
|---|---|
| reel module line | `from beta_tum_karte_kya_ho_sfx import cues, BED, BED_GAIN_DB` (cues() = version A, VO-fitted) |
| hook-B module | its audio is the first 2.8 s of the version-B full mix (BRIEF 7); `cues('B')` gives the full-length B set |
| render flag | `--no-sfx-build --audio <full mix wav>` (A: music-supervisor's run-2 mix of `audio/beta_tum_karte_kya_ho_sfx_stem.wav`; until then `audio/rough/beta_tum_karte_kya_ho_mix.wav`). Never let render.py rebuild: `audio.mix` has no drop-out gate and no loop fold (its fallback build of these cues runs clean, -18.02 LUFS / -2.20 dBTP, but cuts the tails at 36.4 s instead of folding them onto frame 0) |
| SFX stems (48 kHz, 24-bit) | `workspace/jawad_reels/beta_tum_karte_kya_ho/audio/beta_tum_karte_kya_ho_sfx_stem.wav` (A) and `..._hookb_sfx_stem.wav` (B), each with `_fx.wav` (cues + room send) and `_bed.wav` (room tone + street) splits that sum to it |
| cue sheets / report | `audio/beta_tum_karte_kya_ho_cues_{A,B}.json`, `audio/beta_tum_karte_kya_ho_sfx_report.json`, overviews `audio/beta_tum_karte_kya_ho_sfx_overview_{A,B}.png`, zooms `audio/beta_tum_karte_kya_ho_sfx_zooms.png` |
| rough mixes (`epic_mix.mix_reel`) | `audio/rough/beta_tum_karte_kya_ho_mix.wav` (A full), `..._vo_sfx.wav` (A without music), `..._hookb_mix.wav`, `..._hookb_vo_sfx.wav` (B), stems `*_stem_{vo,sfx,music}.wav`, `*_mix.png`, `rough_report.json` |
| rebuild | `cd pipeline/jawad_reels && tools/heavy.sh python3 beta_tum_karte_kya_ho_sfx.py all` (build + rough, ~2 min); `python3 beta_tum_karte_kya_ho_sfx.py cues|table|verify` (light) |
| picture retime | the module reads `beta_tum_karte_kya_ho.SFX_EVENTS` (keys of `EV` / `EV_B`) when the reel module defines it; re-run `all` after any event moves |

## 2. Design in one paragraph

The phone is the instrument. Mummy's message sound (`notif_ping`, tuned to A6 = the Dm9 5th; C#7 / D7 where the bar
asks) marks every message: the hook bubble (0.367), the killer (12.6, in the music's silence), the time-skip pings that
count 12 → 47 → 99+, the family flood, "Kamaal!" / "Wah!" and Nani's pill (35.0) that loops into frame 0. The typing-dot
tick is the second half of the motif (f0, loading dots, "Mummy is typing", the held breath at 27.3, Nani's dots). The
three wrong-genre gags get a comic palette (pop, tuned bubble_pop boings, whip + soft impact + tabla 'ge' on the
punch-in, the stamp's impact + tabla 'ta'), the transitions their matched whooshes (M6 whoosh_by, M3 whoosh_fast under
"Seedha jawab", M2 reverse swell + shimmer + whoosh), and the payoff one tonal hit: tabla 'dha' on Sa = D over the bed's
D add9, with impact body and a sub dive, after the only drop-out (27.3-28.0, room tone + one tick). Beds: room tone all
through (it carries both music silences) and the street outside the window (`desi_city`, out for the drop-out). The
end card keeps `endcard.EndCard.cues` (ring swish, keyword shimmer, ring-close glass tap tuned to D7) and its reverse
swell ends exactly on 36.400 = frame 0, where the loop-landing impact releases it.

## 3. Cue sheet, version A (57 cues; final values after the VO fit)

"gain dB set -> after VO fit": the level this module sets -> the level after `sfx_jawad.fit_under_vo` (words + VO audio).
`audio.duck_under` (cluster auto-gain inside the mixer) trims a further 0-5 dB on dense instants; the per-cue result is
`placed[].gain_db` in the report. Seeds are fixed per cue so A and B carry identical bodies. **hero** = timing-critical
hit checked against the words with the bible clearances (120 ms before, 300 ms after an impact / 150 ms after anything
else).

| # | t (s) | f | name | params | align | gain dB set -> after VO fit | filters | VO fit | event |
|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.0000 | 0 | impact_soft | seed 0 | hit | -8 -> -8 | tail duck -8 dB from hit+0.10 s (ramp 0.05 s) | - | loop landing: the end card swell ends on 36.4 = f0 |
| 2 | 0.0000 | 0 | ui_tick | seed 0 | hit | -12 -> -12 | hp 5000 | - | typing dots on the Mummy pill (motif, part 2) |
| 3 | 0.3667 | 11 | notif_ping | pitch 1.1225, seed 0 | hit | -4 -> -12 | - | -8.0 dB | Mummy's message lands, H1 legible (motif) |
| 4 | 3.1000 | 93 | card_slide | dur 0.42, seed 0 | hit | -6 -> -12 | lp 1100 | -6.0 dB, lp 1100 | translate card lands (slide from the c1 cut) |
| 5 | 3.2667 | 98 | typing | n 12, cps 20, seed 0 | hit | -14 -> -22 | lp 1100 | -8.0 dB; busy under a word: lp 1100 | input "Video editor" types (f98-f116) |
| 6 | 4.2000 | 126 | pop | pitch 0.82, seed 0 | hit | -4 -> -12 | - | -8.0 dB | output "Shaadi wala?" pops (A5) |
| 7 | 4.9000 | 147 | shimmer | dur 1.2, seed 0 | hit | -8 -> -8 | hp 5500 | body under speech 0.96 s: hp 5500 | wedding parody: sparkle wipe |
| 8 | 4.9000 | 147 | whoosh_by **hero** | dur 0.8, direction 1, seed 0 | hit | -8 -> -8 | pan +0.1 | - | M6 carry-over: the word flies into the window (fastest point) |
| 9 | 5.3000 | 159 | sparkle | seed 0 | hit | -8 -> -14 | hp 5500 | -6.0 dB, hp 5500 | M6 spark lands, "Happy Wedding" wipes in |
| 10 | 6.3333 | 190 | typing | n 15, cps 30, seed 0 | hit | -16 -> -16 | lp 1100 | busy under a word: lp 1100 | input "Motion designer" types (f190-f205) |
| 11 | 7.0000 | 210 | bubble_pop | pitch 0.97, seed 0 | hit | -2 -> -10 | - | -8.0 dB | "Cartoon?" pill POPs + MOTION wobble, boing 1 (D6) |
| 12 | 7.3667 | 221 | bubble_pop | pitch 0.77, seed 0 | hit | -6 -> -6 | - | - | boing 2 (Bb5, the droop) |
| 13 | 7.6667 | 230 | whip | direction 1, seed 0 | hit | -9 -> -9 | - | - | punch-in whip (c3 - 1 f) |
| 14 | 7.7000 | 231 | impact_soft **hero** | seed 0 | hit | -8 -> -8 | - | - | c3 punch-in to suit_shocked |
| 15 | 7.7000 | 231 | tabla_hit | stroke ge, pitch 1.0, seed 0 | hit | -7 -> -7 | - | - | comic bass bend (tabla 'ge'; the bed's theka rests here) |
| 16 | 8.4000 | 252 | impact_soft **hero** | seed 1 | hit | -8 -> -8 | - | - | stamp SLAM on the bar-3 downbeat |
| 17 | 8.4000 | 252 | swish_small | seed 0 | hit | -10 -> -10 | - | - | card returns (c4) |
| 18 | 8.4000 | 252 | tabla_hit | stroke ta, pitch 1.0, seed 0 | hit | -9 -> -9 | - | - | stamp: dry slap (tabla 'ta') |
| 19 | 11.2000 | 336 | whoosh_fast | direction -1, seed 0 | hit | -3 -> -9 | lp 1100, pan -0.4 | -6.0 dB, lp 1100 | M3 momentum swipe left (re-hook 1; under "Seedha jawab" by design) |
| 20 | 11.5000 | 345 | card_slide | dur 0.3, seed 0 | hit | -8 -> -14 | lp 1100 | -6.0 dB, lp 1100 | card B lands pre-filled |
| 21 | 12.1333 | 364 | ui_tick | seed 0 | hit | -14 -> -14 | - | - | loading dots |
| 22 | 12.6000 | 378 | impact_soft | seed 2 | hit | -10 -> -10 | - | - | killer weight |
| 23 | 12.6000 | 378 | notif_ping **hero** | pitch 1.1225, seed 0 | hit | -4 -> -4 | - | - | KILLER bubble "Achha. Naukri kab lagegi?" (music silent; A6) |
| 24 | 13.6667 | 410 | swish_small | seed 1 | hit | -8 -> -8 | - | - | card folds away |
| 25 | 14.0000 | 420 | impact_soft | seed 3 | hit | -10 -> -10 | - | - | c6 cut to suit_neutral |
| 26 | 15.0000 | 450 | swish_small | seed 2 | hit | -14 -> -20 | hp 5500 | -6.0 dB, hp 5500 | killer bubble exits |
| 27 | 16.8000 | 504 | btk_haptic | seed 0 | hit | -4 -> -4 | - | - | buzz 1: haptic pulses = the 6 px creeps at 16.8 / 17.0 |
| 28 | 16.8000 | 504 | pop | pitch 0.82, seed 0 | hit | -10 -> -10 | - | - | chip "Kuch mahine baad" POPs (A5) |
| 29 | 17.2000 | 516 | notif_ping | pitch 1.1225, seed 1 | hit | -10 -> -18 | - | -8.0 dB | buzz 1's ping: edge-glow pulse (A6) |
| 30 | 18.2000 | 546 | btk_haptic | seed 1 | hit | -4 -> -4 | - | - | buzz 2: count pill rises, creeps at 18.2 / 18.4 |
| 31 | 18.6000 | 558 | notif_ping | pitch 1.1225, seed 2 | hit | -10 -> -10 | - | - | buzz 2's ping: edge-glow pulse (A6) |
| 32 | 18.9000 | 567 | notif_ping | pitch 1.4142, seed 0 | hit | -12 -> -12 | - | - | ping: count 12 -> 47 (C#7, over A7b9) |
| 33 | 19.2667 | 578 | notif_ping | pitch 1.1225, seed 3 | hit | -12 -> -12 | - | - | ping: count 47 -> 99 (A6) |
| 34 | 19.4333 | 583 | notif_ping | pitch 1.4142, seed 1 | hit | -12 -> -12 | - | - | ping: "+" -> 99+ (C#7, the leading tone into D) |
| 35 | 19.6000 | 588 | reverse_swell | duration 0.3, seed 0 | hit | -9 -> -9 | - | - | M2: the suck into the hue bridge (ENDS on the cut) |
| 36 | 19.6000 | 588 | shimmer | dur 1.0, seed 0 | hit | -10 -> -10 | hp 5500 | body under speech 0.81 s: hp 5500 | M2 hue bridge into the gold group scene |
| 37 | 19.6000 | 588 | whoosh_fast **hero** | direction 1, seed 0 | hit | -9 -> -9 | - | - | "Khandaan" floods (scroll) |
| 38 | 21.7000 | 651 | notif_ping | pitch 1.1225, seed 0 | hit | -6 -> -14 | - | -8.0 dB | the forwarded reel bubble lands (A6) |
| 39 | 22.4000 | 672 | notif_ping | pitch 1.4983, seed 0 | hit | -8 -> -16 | - | -8.0 dB | "Kamaal!" (D7 over Bbmaj7) |
| 40 | 23.1000 | 693 | notif_ping | pitch 1.1225, seed 1 | hit | -8 -> -16 | - | -8.0 dB | "Wah!" (A6) |
| 41 | 25.2000 | 756 | pop | pitch 0.82, seed 0 | hit | -10 -> -18 | - | -8.0 dB | "Mummy is typing" pill (A5) |
| 42 | 25.2000 | 756 | ui_tick | seed 1 | hit | -14 -> -20 | hp 5500 | -6.0 dB, hp 5500 | typing dots |
| 43 | 26.6000 | 798 | ui_tick | seed 2 | hit | -14 -> -20 | hp 5500 | -6.0 dB, hp 5500 | typing resumes |
| 44 | 27.3000 | 819 | ui_tick | seed 3 | hit | -16 -> -16 | - | - | held breath: the only start in the drop-out (27.3-28.0) |
| 45 | 28.0000 | 840 | impact_soft **hero** | seed 0 | hit | -3 -> -3 | tail duck -8 dB from hit+0.25 s (ramp 0.05 s) | - | payoff body |
| 46 | 28.0000 | 840 | sub_drop | dur 1.6, seed 0 | hit | -6 -> -6 | lp 120, tail duck -8 dB from hit+0.25 s (ramp 0.05 s) | - | payoff sub (the bed has no kick / 808 here) |
| 47 | 28.0000 | 840 | tabla_hit **hero** | stroke dha, pitch 1.0, seed 0 | hit | +0 -> +0 | tail duck -8 dB from hit+0.25 s (ramp 0.05 s) | - | PAYOFF: M1 tonal hit (tabla 'dha' on Sa = D over D add9) |
| 48 | 28.2333 | 847 | shimmer | dur 1.5, seed 0 | hit | -8 -> -14 | hp 5500 | -6.0 dB, hp 5500 | *cinema* starts rising |
| 49 | 28.7000 | 861 | swish_small | seed 3 | hit | -12 -> -18 | hp 5500 | -6.0 dB, hp 5500 | c10 punch-in to hand_on_chest |
| 50 | 31.8333 | 955 | swish_small | seed 0 | hit | -12 -> -18 | hp 5500 | -6.0 dB, hp 5500 | payoff lockup + bubble exit |
| 51 | 32.3000 | 969 | swish_small | seed 1 | start | -12 -> -12 | - | - | end card: monogram ring draws on (align start) |
| 52 | 32.7700 | 983 | shimmer | seed 0 | hit | -10 -> -16 | hp 5500 | -6.0 dB, hp 5500 | end card: keyword *bhejo* rises |
| 53 | 32.9500 | 989 | glass_tap | pitch 1.12, seed 0 | hit | -12 -> -20 | - | -8.0 dB | end card: ring closes (D7 over Bbmaj7) |
| 54 | 35.0000 | 1050 | notif_ping | pitch 1.1225, seed 2 | hit | -8 -> -16 | - | -8.0 dB | Nani's chip + typing pill: Mummy's message sound (A6) |
| 55 | 35.8000 | 1074 | ui_tick | seed 0 | hit | -15 -> -21 | hp 5500 | -6.0 dB, hp 5500 | Nani typing dots |
| 56 | 36.1000 | 1083 | ui_tick | seed 1 | hit | -15 -> -21 | hp 5500 | -6.0 dB, hp 5500 | Nani typing dots |
| 57 | 36.4000 | 1092 | reverse_swell | duration 0.8, seed 0 | hit | -8 -> -14 | lp 1100 | span -6.0 dB, lp 1100 | loop swell, ENDS on 36.4 = frame 0 (endcard.cues) |

**Version B (Trial hook, 60 cues)** = these 6 hook-B cues + every A cue with t >= 2.8 (A's three hook cues dropped),
mixed at A's exact gains:

| # | t (s) | f | name | params | align | gain dB set -> after VO fit | filters | VO fit | event |
|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.0000 | 0 | bubble_pop | pitch 1.15, seed 0 | hit | -4 -> -4 | - | - | hook B f0: MOTION mid-wobble (boing, F6) |
| 2 | 0.0000 | 0 | impact_soft | seed 0 | hit | -8 -> -8 | tail duck -8 dB from hit+0.10 s (ramp 0.05 s) | - | hook B f0 weight |
| 3 | 0.7000 | 21 | bubble_pop | pitch 0.97, seed 0 | hit | -8 -> -16 | - | -8.0 dB | hook B boing 2 (JELLY re-trigger, D6) |
| 4 | 1.4000 | 42 | swish_small | seed 0 | hit | -10 -> -16 | hp 5500 | -6.0 dB, hp 5500 | hook B MOTION droops and squashes |
| 5 | 2.1000 | 63 | tabla_hit | stroke na, pitch 1.0, seed 0 | hit | -8 -> -16 | - | -8.0 dB (band mid) | hook B *cartoon?* halo flare (tabla 'na', Sa = D) |
| 6 | 2.4667 | 74 | notif_ping | pitch 1.1225, seed 0 | hit | -6 -> -6 | - | - | hook B hard cut to A's f74: Mummy's bubble (A6) |

**Beds** (`BED`, `BED_GAIN_DB = -32`): `room_tone` 0-36.4 (0 dB) + `desi_city` 0-27.3 (-8 dB, 0.3 s fade out into 27.3)
and 28.0-36.4 (-8 dB, 4 ms back in on the payoff); both rendered as seamless loops exactly 36.4 s long (`params
dur=36.4`, street `offset` = t0), so the street is continuous across its gap and across the loop seam. Bed in the stem:
-42.0 LUFS integrated, sidechained 5 dB under the SFX.

## 4. Changes from BRIEF 6.12 (each one measured)

| # | cue(s) | brief | here | why (measurement) |
|---|---|---|---|---|
| 1 | buzz 1 / buzz 2 (16.8 / 18.2) | `notif_ping buzz=1` align start, -10 | `btk_haptic` (-4) at 16.8 / 18.2 + `notif_ping` A6 (-10) at 17.2 / 18.6 | the two parts are separate picture events (creeps 16.8 / 17.0, edge-glow pings 17.2 / 18.6). `btk_haptic` = the same notif_ping buzz=1 samples cut before the ping (bit-identical to 0.345 s, qc clean). Its haptic alone is -34.6 LUFS momentary at 0 dB, 10 dB under the ping, so at the brief's -10 the buzz that moves the phone sat 6.6 dB under the chip pop: raised to -4. The 17.2 ping alone lands in "Mahine" and is ducked to -18; the haptic (165 Hz) is not |
| 2 | pings 18.9 and 19.433 | D7 (1.4983) | C#7 (1.4142) | MUSIC.md 2: they fall in bar 6's A7b9 half, where D is a sus4 clash; C#7 is a chord tone and the leading tone into the flood's D minor at 19.6 |
| 3 | bubble_pop 7.0 / 7.367 | pitch 1.0 / 0.8 | D6 (0.97) / Bb5 (0.77), seed 0 | bar 2 = Gm9; the brief's droop becomes a falling major third on chord tones (x0.794). Tuned on the chirp's ridge (`ridge_hz`): the bible's f0_of jumps between bubble_pop's reverb modes (1379 / 1504 / 2079 Hz) as pitch moves. Hook B: F6 (1.15) -> D6 (0.97) over Dm9 |
| 4 | glass_tap 32.95 (card.cues) | no pitch (C7) | D7 (1.12) | bar 11 = Bbmaj7; C is not a chord tone |
| 5 | pop x3 | pitch_to(880) | 0.82, seed 0 | f0_of gives A5 -3.0 cents at seed 0; the mixer's seed variation would move it by up to +68 cents (seed 2: 913.7 Hz), so the seed is fixed |
| 6 | 7.667 whip / 7.7 impact_soft / 7.7 tabla 'ge' | -6 / -2 / -4 | -9 / -8 / -7 | BRIEF 8.13 + MUSIC.md watch item: the loudest (music + SFX) moment must be in 28.0-28.4. With the brief's levels the punch-in tied the payoff; whip crest 15.5 dB drove the stem limiter |
| 7 | 8.4 impact_soft / tabla 'ta' | 0 / -6 | -8 / -9 | same: stamp window -10.6 LUFS vs payoff -8.8; 'ta' crest 17 dB |
| 8 | 4.9 whoosh_by | -4 | -8 | crest 15 dB; limiter |
| 9 | 12.6 killer notif_ping / impact_soft | 0 / -8 | -4 / -10 | it sounds in the music's silence and was the loudest momentary of music + SFX (-8.0 vs payoff -9.3); now -9.21 vs -8.83 |
| 10 | 19.6 reverse_swell / whoosh_fast | -6 / -8 | -9 / -9 | crest 15.5 dB; flood window now -9.48 |
| 11 | payoff stack 28.0 (tabla 'dha', sub_drop, impact_soft) | gains kept (0 / -6 / -3) | + tail duck -8 dB from 28.20 to 28.25 (`env`) | measured per word: L9 "Ab" (28.25) had the SFX only 1.6 LU under the VO (BRIEF 8.13 needs >= 6). The transient and the first 200 ms bloom are untouched; "Ab" is now 7.9 LU clear |
| 12 | f0 impact_soft (A and B) | -8 | -8 + tail duck -8 dB from 0.05 to 0.10 | L1 "Yeh" (0.12) had the SFX 4.6 LU under the VO, B's "Mummy" 5.0; now >= 8.2 (worst word under it: "sawaal") / 11.0 |
| 13 | typing 3.267 / 6.333 | -14 / -16, no filter | + lp 1100 | 52 % of their energy is 1-4 kHz key clicks and both run under words ("ka translation", "ulta.") |
| 14 | shimmer 4.9 / 19.6 | no filter | + hp 5500 | their hits are clear of words but their bodies run 0.96 / 0.81 s under L3 / L7 (20 % of a shimmer is 1-4 kHz) |
| 15 | tabla 'na' 2.1 (hook B) | -8 | -16, no filter | `fit_under_vo` classes epic_sfx `tabla_hit` as AIR and would hp it at 5.5 kHz (it is 87 % 250-1000 Hz): treated as MID (-8 dB under a word). Filed as SHARED_REQUESTS 5 |

Consequences of the VO overruns (VO_TIMING.md: L2 ends 4.37 > 4.30, L3 "ulta." ends 7.05-7.09 against the brief's "ends
before the 7.0 pop"): the "Shaadi wala?" pop (4.2) and the "Cartoon?" boing 1 (7.0) now land on the tail of a word and
`fit_under_vo` ducks them 8 dB (-12 / -10). Boing 2 (7.367, -6) is clear and carries the gag. Moving them would break
picture sync; re-timing L2 / L3 is the scriptwriter's call.

## 5. VO fit and hero clearances (version A; B identical after 2.8 s)

- Speech = words + VO audio activity (`sfx_jawad.hero_windows`, source "words+audio").
- Hero hits and their clearance: 4.9 whoosh_by, 7.7 impact_soft, 8.4 impact_soft, 12.6 notif_ping, 19.6 whoosh_fast,
  28.0 tabla 'dha' all pass the bible rule. **One stated exception:** 28.0 impact_soft has 0.250 s before L9's first word
  (28.25; audio activity 28.2579) against the bible's 0.300 s for impacts. Picture (bar 10, M1 cut) and VO slot are both
  locked and BRIEF 6.7 sets exactly this 250 ms. Its -12 dB point is at +0.248 s, its energy is 100 % below 1 kHz, and
  the tail duck (item 11) drops it 8 dB before the word.
- Ducked under words (-6 dB, AIR + hp 5500, DARK + lp 1100, MID -8 dB): 25 cues in A, plus 3 carved without a gain change
  (typing 6.333 lp 1100, shimmer 4.9 / 19.6 hp 5500) (table, "VO fit" column). 11.2's M3 swipe sits under "Seedha
  jawab" by design (BRIEF) and is ducked + lp 1100.
- <= 3 sounds starting within one frame everywhere (max 3 at 7.667-7.700 and 8.4 and 28.0; swells that END on an
  instant are not counted). No cue starts in 27.305-27.995 (the drop-out); the 27.3 tick is the only start there.

## 6. Measurements

**SFX stems** (python BS.1770 / ffmpeg ebur128):

| stem | integrated | true peak | LRA | max momentary | limiter | glue |
|---|---|---|---|---|---|---|
| A | -18.02 LUFS / ffmpeg -18.0 | -2.20 dBTP / ffmpeg -2.2 | 15.2 LU | -10.65 LUFS | max 4.4 dB, > 1 dB for 867 ms (2.4 %), > 3 dB for 175 ms | max 2.4 dB |
| B (A's gains) | -17.76 / ffmpeg -17.8 | -2.20 / ffmpeg -2.2 | 14.3 LU | -10.65 | same peaks | 2.4 dB |

- Limiter: the 4.4 dB peaks are the hero transients (payoff 4.4, stamp 3.8, punch-in 3.4, M6 3.4, M2 3.1). This is
  structural: a sparse cue list normalised to -18 LUFS integrated puts its hits 10-15 dB over the gated mean. Every trim of
  a competing hit raised the bus gain and moved the reduction to the next hit (4.1 -> 4.2 -> 4.4 dB across the three
  rebalances). Lowering it further means a lower stem target; epic_mix re-levels the stem to -18 LUFS anyway.
- Drop-out (27.31-27.98): the cue bus holds only the 27.3 tick (peak -24.3 dBFS) and its room-send tail (-34.2 dBFS after
  27.33); room tone peaks at -33.8 dBFS; the payoff stack starts at 27.990-27.998 (its pre-hit attacks). Everything that
  hits before 27.3 is gated with its room send at 27.296-27.300 (it had already decayed to -92 dBFS: the gate is a
  guarantee, not an audible cut).
- Tails past 36.4: 35.0 notif_ping and 36.1 tick fold onto 0 s ("tail wrapped"); nothing is lost past 40.4 s (-240 dBFS).
- Splice: B equals A to the sample from 5.344 s to the last frame (max difference 3e-8 = float rounding). 2.8-5.34 s
  differs only by the hook-B tails (hook-B notif_ping at 2.4667); the last 25 ms differ because each version loops into
  its own head.
- Loop seam: the step from the last to the first sample of the stem (0.159) is the attack of frame 0's ui_tick, a
  designed transient (the same tick at 12.133 makes a 0.369 step); every other f0 cue is continuous across the seam
  (impact_soft step 0.0006 before gain). Zoom: `audio/beta_tum_karte_kya_ho_sfx_zooms.png`, viewed.
- Spectrograms viewed (overview A/B, zooms): every cue tick has energy; sub only at the payoff (sub_drop, lp 120) and
  at the haptic pulses (165 Hz); no constant hiss above 2 kHz (beds sit below ~1 kHz); the loudest bursts are the hero
  hits; the drop-out column holds only room tone and the tick; the swell rises into the seam and the f0 impact lands on it.

**Rough mixes** (`epic_mix.mix_reel`, VO + this stem + `music/music_full.wav`; all from `audio/rough/rough_report.json`):

| check | A | B | target |
|---|---|---|---|
| full mix, ffmpeg ebur128 | I -14.0 LUFS, TP -2.3 dBFS, LRA 2.4 LU | I -14.0, TP -2.3, LRA 2.4 | -14 +- 0.5, <= -2.0, LRA 5-9 |
| no-music mix (VO + SFX) | I -14.1, TP -2.3, LRA 3.1 | I -14.1, TP -2.3, LRA 3.1 | -14 +- 0.5, <= -2.0 |
| after AAC 320k (no re-normalisation) | TP -2.3 (mix), -2.2 (no-music) | TP -2.3 | <= -1.5 |
| bus limiter (epic_mix) | 2.25 dB max | 2.06 dB | - |
| VO over music, median (epic_mix) | 10.8 LU | 10.6 LU | >= 8 |
| VO over music per word (53 words) | median 11.3, p10 8.5, min 7.1 | median 11.4, min 7.2 | - |
| SFX under VO per word | min 6.2 ("mein..." 21.7, the reel-forwarded ping), p10 9.3, median 19.7 | min 6.6 | >= 6 LU |
| L11 "Ab Nani ki baari." vs 35.0 ping, 35.7 'tin', loop swell | SFX >= 10.7 LU under, music >= 10.3 LU under | >= 11.1 / 10.4 | >= 6 LU |
| music bus 12.62-13.98 and 27.31-27.99 | digital zero (-240 dBFS) both | same | <= -60 dBFS |
| room tone in the silences (bed stem at the mix's SFX gain, +1.9 dB) | -41.2 LUFS (killer silence), -40.6 (drop-out) | -41.2 / -40.6 | -45 +- 5 |
| max momentary, music + SFX | 28.2 s, -8.83 LUFS (next: 12.4-12.9 -9.21, 7.5-8.0 -9.32, 19.4-20.0 -9.48, 8.2-8.7 -10.57) | 28.2 s, -8.94 | in 28.0-28.4 |
| loop seam (mix) | last frame -20.6 dBFS RMS, first frame -9.9 | -19.5 / -10.1 | louder than -40 |
| cue sync in the mix's SFX stem (own waveform, normalised cross-correlation, +-60 ms) | 0.367, 4.9, 7.7, 8.4, 12.6, 16.8 pop, 17.2, 18.2, 18.6, 18.9, 19.267, 19.433, 19.6, 28.0 x2, 35.0: lag 0.00-0.06 ms | same + 2.4667 | +-1 frame |

- 16.8 haptic: the correlation reports +24.3 ms, exactly 4 periods of its 165 Hz carrier, because the 16.8 chip pop
  overlaps it. Measured on the 130-200 Hz band envelope instead, both haptics start at the same offset from their cue
  (16.8: -2.9 ms, 18.2: -2.4 ms; pulse 2 at -2.8 / -2.9 ms from +0.2 s): on the frame.
- Words under 8 LU of VO over music: "pe." 26.88 (7.4), "ko" 29.07 (7.4), "hain..." 30.22 (7.1), "bhejo." 33.96 (7.2):
  the bed's ducking (epic_mix: 9 dB under VO), for the music-supervisor's run 2.

## 7. Open items

1. **Music-supervisor (run 2):** LRA of the full mix is 2.4 LU against SLATE 5.1's 5-9 LU (epic_mix's VO 3:1 compression +
   bus glue on a VO-led reel); four words sit 7.1-7.4 LU over the music (median 10.8 passes). epic_mix crashes on this
   reel's mono VO wavs: use a dual-mono copy (SHARED_REQUESTS 4).
2. **Scriptwriter / lead:** L2 and L3 overrun (VO_TIMING), so the 4.2 and 7.0 gag pops are ducked 8 dB under word tails.
3. **QA:** the payoff impact's 250 ms clearance is the brief's stated exception (section 5). The stem limiter peaks at
   4.4 dB on hero transients (section 6).
4. **Builder:** adopt the import line; expose `SFX_EVENTS` if any picture event moves; render with `--no-sfx-build --audio`.
