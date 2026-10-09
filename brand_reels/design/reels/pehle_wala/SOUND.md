# SOUND · Reel 1 · C26 · Pehle Wala Hi Theek Tha · `pehle_wala`

Author: sound-designer · 2026-10-09 · Code: `pipeline/jawad_reels/pehle_wala_sfx.py` · Binding: BRIEF.md r2 §6.3, §7, §9, §11;
SLATE §3.1 + §5.1; MUSIC_pehle_wala.md (D minor, one chord per bar); VO_TIMING.md (measured Vlad words).
Nobody on the team can listen, me included: every statement below is a measurement or a rendered-image check.

## 0. Hand-off

- Builder line (`pehle_wala.py` must not draft its own cues): `from pehle_wala_sfx import cues, BED, BED_GAIN_DB`.
  `cues()` returns the fitted hook-A sheet (`cues('B')` the Trial hook); `BED`/`BED_GAIN_DB` are only the audio.mix fallback.
  **Never let render.py rebuild the SFX** (audio.mix has no loop wrap, drop-out gate, press tape-stop or carve windows):
  render with `python3 render.py pehle_wala --no-sfx-build --audio <final mix wav>`.
- Rebuild after any VO or timing change: `tools/heavy.sh python3 pehle_wala_sfx.py build --hook AB` then `... rough --hook AB`
  (about 25 s + 25 s each on 2 threads). `cues` prints the sheet, `audition` re-checks the local sounds.
- The music-supervisor makes the final mix from `pehle_wala_sfx_{A,B}_stem.wav` (-18 LUFS, loop-exact). Its
  `epic_mix.mix_reel` raises a ValueError on the mono VO wavs (SHARED_REQUESTS #11): pass a stereo copy, or use `rough()`,
  which already does the loop-padded epic_mix run.

| file (`<RW>` = `workspace/jawad_reels/pehle_wala`) | what |
|---|---|
| `<RW>/audio/pehle_wala_sfx_A_stem.wav`, `..._B_stem.wav` | SFX stem per hook, 48 kHz 24-bit stereo, 1,638,400 samples, -18.0 LUFS, -2.2 dBTP, loop-exact (tails past DUR wrap to t = 0) |
| `..._sfx_{A,B}_stem_fx.wav`, `..._stem_bed.wav` | the cue bus and the edit_suite bed at stem gain (they sum to the stem) |
| `..._sfx_{A,B}_overview.png`, `_cues.json`, `_report.json` | spectrogram + loudness strip, every placed cue (start / hit / gain / duck / carve / measured onset), all measurements |
| `<RW>/audio/pehle_wala_{A,B}_rough_mix.wav` | rough Version A (VO + SFX + music), -14.0 LUFS, <= -2.3 dBTP |
| `<RW>/audio/pehle_wala_{A,B}_rough_vo_sfx.wav` | rough Version B (VO + SFX, for an in-app song), -14.0 LUFS |
| `<RW>/audio/pehle_wala_{A,B}_rough_stem_{vo,sfx,music}.wav`, `_rough.json`, `_rough_mix.png` | stems at mix gain, measurements, overview |
| `<RW>/audio/audition/*.wav`, `*.png`, `audition.json` | the six local sounds, spectrograms, qc, pitch in cents |

## 1. Sound motif and local sounds

The motif is the pin **thock** (SLATE §3.1): a glassy tick tuned to D7 two milliseconds ahead of a felt thump, on every client
note, with `slot_tick` rolling the version counter on every step (26 steps, v2 -> v27). Mummy's notes are the same thock a
fifth lower (A6) with a small sub. The payoff note is the big one (D6 glass over `impact_big`).

| sound | recipe | hit (s) | Mmax (LUFS) | qc | pitch (bible f0_of) |
|---|---|---|---|---|---|
| `pin_thock` | `glass_tap(pitch=1.1207)` -8 dB, 2 ms ahead of `impact_soft` 0 dB, lp 6000 | 0.006 | -22.9 | clean | D7 2349.6 Hz, +0.2 c |
| `pin_thock_dark` | `pin_thock`, lp 1100 (landings inside a word) | 0.006 | -23.0 | clean | (glass removed) |
| `pin_thock_mummy` | `glass_tap(0.8396)` -8 + `impact_soft` 0 + `sub_drop(dur 0.6)` -14 lp 120 | 0.008 | -22.8 | clean | A6 1760.0 Hz, +0.0 c |
| `pin_thock_mummy_dark` | the Mummy thock, lp 1100 | 0.008 | -22.9 | clean | - |
| `pin_thock_big` | `glass_tap(0.5603)` -6 + `impact_big` 0 | 0.006 | -16.0 | clean | D6 1174.6 Hz, -0.1 c |
| `pw_tape_rewind` | D9 as sound: hook A's music + SFX (never the VO) read BACKWARDS by 25 ms Hann grains every 8 ms from `tau_a(t) = 26.1333 - 26.1333 u^3` (u over 26.3333 -> 27.7333), each grain resampled by abs(dtau/dt) (0 -> 56x), amplitude sqrt(min(rate, 1)), lp 3000, partial leveller (ratio 0.6, -3 .. +12 dB); hit = END | 1.400 | -23.0 | clean | - |

Pitch note: the brief's multipliers (1.0926 / 0.8186 / 0.5463) assumed `glass_tap` f0 = 2150 Hz; it measures 2096.3 Hz, so
1.0926 lands on 2290.2 Hz = **D7 -44 cents** (outside the ±30 c rule). Recomputed: D7 1.1207, A6 0.8396, D6 0.5603.
Other tonal cues: `pop` D6 (1.0962, +2.7 c) on Dm/Bb bars and C6 (0.9766, +1.9 c) on the F bar; `ui_click` A6 (1.0643, -4.6 c;
its default 1653.6 Hz is the tritone G#6 against Dm); rewind `ui_tick` A7 (0.9292, +4.1 c); `bubble_pop` D6 (0.78, -5.0 c; it
is a chirp, its FFT peak jumps with pitch, not in the bible's tonal list); `toggle_on` C6 +7.3 c on the C bar (default);
end-card `glass_tap` D7 on the Bb bar. All within ±30 c of a chord tone of their bar.

The D9 audio clock is the picture's minus its 0.2 s press offset: jawad_tx `_tx_undo` uses `tau = t_r - R u^3` with
`t_r = 26.3333` (the world stays live 6 frames after the press), so the picture's first rewind frames read 26.33 -> 26.13,
which in the music is the tape-stop. The audio reads `tau - 0.2` (exactly the BRIEF §11 formula), so it never reads the stop.
The rewind ticks use the picture's clock: 26 version crossings between 27.078 and 27.698 s, 19 ticks after merging those
closer than 25 ms (BRIEF rule).

## 2. Decisions taken against the measured VO (VO_TIMING.md)

- **Pins inside a measured word** (word window ±60 ms) are `*_dark` at -6 dB: 0.267 "Bas", 2.133 "change." (new: L1 runs to
  2.270), 4.267 (40 ms after "jayega."), 7.467 "Clean." (VO_TIMING fallback), 9.600 (30 ms after "Energetic.", fallback),
  13.333 / 13.867 / 14.400 (Mummy thread inside L7), 16.000 "cinematic.", 19.200 "Aur", 19.733 / 20.267 / 20.800 (L9), and
  21.333 inside the last "ek." of L9 at **-8** (at -6 that word sat only 5.3 LU over the SFX). **6.400 is back to the full
  thock** (L3 ended 6.117, early). 16.533 stays full (L8 ends 16.42).
- **Hero hits are never inside a word.** Three sit in VO gaps but less than 300 ms before the next word (pre-laps fixed by the
  picture and the script): `flash_hit` 4.267 (gap 4.242-4.400), `braam` + `flash_hit` 14.933 ("Bilkul" at 14.997), hook B's
  `trailer_hit` at f0 ("26" at 0.100). Their hit stays whole; from 50 ms after the hit their tail is carved -10 dB with a
  600 Hz low-pass crossfade for as long as the speech lasts (bridged over pauses < 1 s). The payoff (25.600) and the restore
  (27.733) are clear: no VO 24.93-28.13.
- **Gap cues with a word right after** (the "editor answers the note" pins at 3.200, 8.533, 10.667, 12.800, 14.933, and the
  cues landing with them) keep 30 ms of transient and are carved the same way under the word ("Ho" went from 1.6 to 12.0 LU
  over the SFX, "Ab" from 3.7 to 13.7). 42 cues carry carve windows (listed in `_report.json`).
- Everything not designed for the voice went through `sfx_jawad.fit_under_vo` (20 cues: on-word -6 dB, air hp 5500,
  dark lp 1100, mid -8). The brief's r2 VO-aware values are kept as written (`designed` in the cue table).
- **L9 / D7 (VO_TIMING §5 decision for the creative director):** the sound takes option (a) "keep it": the full D7 at 21.333
  lands inside "ek.", so its pin, glitch, whip and drawer slide are ducked; the Shepard riser now starts after the word.
  If the creative director picks (b) (D7 >= 21.733), re-run `build`: the pin becomes a full gap thock automatically.

## 3. Cue sheet

Gains are final (after the VO fit and audio.duck_under; "cluster" = the duck_under share). Times are reel seconds, frame =
t x 30. Visual events: BRIEF §6.3 / §7 / §8. Starts per instant: <= 3 everywhere (bible 4.2 definition, the score counted as
one source). Pan follows the element's screen x (`0.4 (x - 540) / 540`; counter +0.30).

#### hook A (125 cues)

| t (s) | frame | sound | align | gain dB | params / filter / pan | VO handling | visual event |
|---|---|---|---|---|---|---|---|
| 0.000 | 0.0 | `impact_soft` | hit | -6 | - | brief pre-lap: VO onset 0.10 (<= 0.3 rule); carve 0.085-2.330 | f0 transient: v1 ad + the marker mid-glide (loop landing) |
| 0.267 | 8.0 | `pin_thock_dark` | hit | -6 | pan -0.05 | pin in word | pin 1 "Logo thora bara?" (inside "Bas") |
| 0.400 | 12.0 | `ui_click` | hit | -11.5 (cluster -1.5) | pitch=1.0643; hp 4000; pan +0.20 | hp 4000 under "Bas ek" | chip Approved -> Changes requested |
| 0.533 | 16.0 | `shimmer` | hit | -11.5 (cluster -1.5) | hp 5500 | hp 5500 under "ek" | lockup BAS EK / chhota sa / CHANGE readable |
| 1.067 | 32.0 | `pop` | hit | -12.3 (cluster -2.3) | pitch=1.0962; lp 1100 | lp 1100 under "chhota" | v2: logo x2 (POP) |
| 1.067 | 32.0 | `slot_tick` | hit | -20 | n=3, dur=0.133; pan +0.30 | -8.0 dB | counter v2 |
| 2.133 | 64.0 | `pin_thock_dark` | hit | -6 | pan +0.01 | pin in word | pin 2 "Aur bara." v3 (inside "change.") |
| 2.133 | 64.0 | `slot_tick` | hit | -25.1 (cluster -5.1) | n=3, dur=0.133; pan +0.30 | -8.0 dB | counter v3 |
| 2.133 | 64.0 | `whoosh_fast` | hit | -17.8 (cluster -3.8) | lp 1100; pan +0.10 | -6.0 dB, lp 1100 | pin 2: logo x3, wordmark runs off the ad |
| 3.200 | 96.0 | `pin_thock` | hit | +0 | pan +0.01 | pin in gap; carve 3.250-4.900 | pin 3 "Thora left." v4 |
| 3.200 | 96.0 | `slot_tick` | hit | -17.1 (cluster -5.1) | n=3, dur=0.133; pan +0.30 | carve 3.250-4.303 | counter v4 |
| 3.200 | 96.0 | `swish_small` | hit | -13.8 (cluster -3.8) | lp 1100; pan -0.10 | carve 3.250-4.303 | pin 3: logo slides -72 px |
| 4.267 | 128.0 | `flash_hit` | hit | -6.3 (cluster -2.3) | - | carve 4.385-6.177 | L3 push 0.5 on pin 4 (saturation spike) |
| 4.267 | 128.0 | `pin_thock_dark` | hit | -8.3 (cluster -2.3) | pan -0.02 | pin in word; carve 4.385-6.177 | pin 4 "Thora aur pop karo" v5 (inside "jayega.") |
| 4.267 | 128.0 | `slot_tick` | hit | -25.1 (cluster -5.1) | n=3, dur=0.133; pan +0.30 | -8.0 dB; carve 4.385-4.900 | counter v5 |
| 4.333 | 130.0 | `pop` | hit | -17.4 (cluster -3.4) | pitch=1.0962; pan +0.25 | -8.0 dB; carve 4.385-4.900 | GOLD NEW burst POPs in (f130) |
| 6.400 | 192.0 | `downlifter` | hit | -13.8 (cluster -3.8) | dur=0.3; pan -0.20 | carve 6.710-9.630 | cream fills the ad (f192-f204) |
| 6.400 | 192.0 | `pin_thock` | hit | +0 | pan -0.21 | pin in gap; carve 6.710-7.593 | pin 5 "Background white kar do" v6 |
| 6.400 | 192.0 | `slot_tick` | hit | -17.1 (cluster -5.1) | n=3, dur=0.133; pan +0.30 | carve 6.710-7.593 | counter v6 |
| 7.467 | 224.0 | `pin_thock_dark` | hit | -6 | pan -0.02 | pin in word | pin 6 "Bhaap nazar nahi aa rahi" v7 (inside "Clean.") |
| 7.467 | 224.0 | `slot_tick` | hit | -23.8 (cluster -3.8) | n=3, dur=0.133; pan +0.30 | -8.0 dB | counter v7 |
| 7.467 | 224.0 | `toggle_on` | hit | -23.1 (cluster -5.1) | - | -8.0 dB | steam gets its cartoon outline |
| 8.533 | 256.0 | `impact_soft` | hit | -8.3 (cluster -2.3) | - | carve 8.585-9.630 | pin 7: beat shake starts, drums in |
| 8.533 | 256.0 | `pin_thock` | hit | -2.3 (cluster -2.3) | - | pin in gap; carve 8.585-9.630 | pin 7 "Music thora energetic" v8 |
| 8.533 | 256.0 | `slot_tick` | hit | -17.1 (cluster -5.1) | n=3, dur=0.133; pan +0.30 | carve 8.585-9.630 | counter v8 |
| 9.600 | 288.0 | `pin_thock_dark` | hit | -6 | pan +0.04 | pin in word; carve 10.766-11.614 | pin 8 "Glass thora chamkao" v9 (inside "Energetic.") |
| 9.600 | 288.0 | `slot_tick` | hit | -23.8 (cluster -3.8) | n=3, dur=0.133; pan +0.30 | -8.0 dB | counter v9 |
| 9.600 | 288.0 | `sparkle` | hit | -17.1 (cluster -5.1) | hp 5500; pan +0.05 | -6.0 dB, hp 5500; carve 10.766-11.614 | four sparkles appear on the glass |
| 10.667 | 320.0 | `bubble_pop` | hit | -11.1 (cluster -5.1) | pitch=0.78; pan +0.25 | carve 10.766-11.614 | garam -> parody font, wobble |
| 10.667 | 320.0 | `pin_thock` | hit | +0 | pan +0.12 | pin in gap; carve 10.766-11.614 | pin 9 "Font fun wala karo" v10 |
| 10.667 | 320.0 | `slot_tick` | hit | -15.8 (cluster -3.8) | n=3, dur=0.133; pan +0.30 | carve 10.766-11.614 | counter v10 |
| 11.733 | 352.0 | `card_slide` | hit | -13.1 (cluster -5.1) | pan +0.30 | - | hard drop shadows on every ad graphic |
| 11.733 | 352.0 | `pin_thock` | hit | +0 | pan +0.20 | pin in gap; carve 12.839-14.729 | pin 10 "Har cheez pe shadow" v11 |
| 11.733 | 352.0 | `slot_tick` | hit | -15.8 (cluster -3.8) | n=3, dur=0.133; pan +0.30 | - | counter v11 |
| 12.800 | 384.0 | `glitch_short` | hit | -12.0 (cluster -6.0) | dur 0.1 | carve 12.850-14.729 | D7 RGB shock (re-hook) |
| 12.800 | 384.0 | `pin_thock_mummy` | hit | +0 | pan -0.29 | pin in gap; carve 12.850-14.729 | RE-HOOK Mummy "Mujhe pasand nahi aaya." v12 |
| 12.800 | 384.0 | `slot_tick` | hit | -17.1 (cluster -5.1) | n=3, dur=0.133; pan +0.30 | carve 12.850-14.729 | counter v12 |
| 12.800 | 384.0 | `whip` | hit | -11.8 (cluster -3.8) | direction=1 | carve 12.850-14.729 | D7 RGB shock (re-hook) |
| 13.333 | 400.0 | `pin_thock_mummy_dark` | hit | -6 | pan -0.29 | pin in word | Mummy card 2 v13 (inside "Mummy") |
| 13.333 | 400.0 | `slot_tick` | hit | -19.1 (cluster -5.1) | n=3, dur=0.133; pan +0.30 | brief -14 under L7/L9 | counter v13 |
| 13.333 | 400.0 | `whoosh_slow` | hit | -15.8 (cluster -3.8) | lp 1000 | lp 1000 under "Mummy" | cream eases back to dark |
| 13.867 | 416.0 | `pin_thock_mummy_dark` | hit | -6 | pan -0.29 | pin in word | Mummy card 3 "Aur glitter." v14 (inside "review") |
| 13.867 | 416.0 | `shimmer` | hit | -17.1 (cluster -5.1) | hp 5500; pan -0.20 | hp 5500 under "review" | glitter x2 |
| 13.867 | 416.0 | `slot_tick` | hit | -17.8 (cluster -3.8) | n=3, dur=0.133; pan +0.30 | brief -14 under L7/L9 | counter v14 |
| 14.400 | 432.0 | `pin_thock_mummy_dark` | hit | -6 | pan -0.29 | pin in word | Mummy card 4 "Logo bhi bara." v15 (inside "karengi.") |
| 14.400 | 432.0 | `pop` | hit | -17.1 (cluster -5.1) | pitch=0.9766; lp 1100 | lp 1100 under "karengi" | logo x1.25 |
| 14.400 | 432.0 | `slot_tick` | hit | -17.8 (cluster -3.8) | n=3, dur=0.133; pan +0.30 | brief -14 under L7/L9 | counter v15 |
| 14.911 | 447.3 | `braam` | start | -7.1 (cluster -3.1) | dur=2.0 | carve 15.001-16.492, 19.218-21.743 | pin 15 "Thora cinematic": letterbox, flares, slow-mo (hero). Cued at its START: its energy begins at its own t=0 (onset 14.913 = -20 ms), designed hit +18 ms, brass blat peak +110 ms of f448; the f448 cluster (pin_thock + flash_hit crack) reads +12 ms in qa_measure |
| 14.933 | 448.0 | `flash_hit` | hit | -9.3 (cluster -3.4) | - | carve 14.983-16.492 | L3 push 0.6 on "Thora cinematic" |
| 14.933 | 448.0 | `pin_thock` | hit | -3.4 (cluster -3.4) | pan -0.02 | pin in gap; carve 14.983-16.492 | pin 15 "Thora cinematic" v16 |
| 14.933 | 448.0 | `slot_tick` | hit | -17.9 (cluster -5.8) | n=3, dur=0.133; pan +0.30 | carve 14.983-16.492 | counter v16 |
| 16.000 | 480.0 | `card_slide` | hit | -13.1 (cluster -5.1) | lp 1100; pan +0.40 | lp 1100 under "cinematic" | 50% OFF ribbon SLAMs in |
| 16.000 | 480.0 | `pin_thock_dark` | hit | -6 | pan +0.22 | pin in word | pin 16 "Price bhi daal do" v17 (inside "cinematic.") |
| 16.000 | 480.0 | `slot_tick` | hit | -23.8 (cluster -3.8) | n=3, dur=0.133; pan +0.30 | -8.0 dB | counter v17 |
| 16.533 | 496.0 | `pin_thock` | hit | +0 | pan -0.02 | pin in gap | pin 17 "Bhaap aur zyada" v18 |
| 16.533 | 496.0 | `slot_tick` | hit | -17.1 (cluster -5.1) | n=3, dur=0.133; pan +0.30 | - | counter v18 |
| 16.533 | 496.0 | `whoosh_slow` | hit | -13.8 (cluster -3.8) | - | carve 15.333-16.492, 19.218-21.743 | steam x3, rising |
| 17.067 | 512.0 | `air_zoom` | hit | -11.1 (cluster -5.1) | - | - | pin 18 "Sab kuch thora bara": everything x1.2 |
| 17.067 | 512.0 | `flash_hit` | hit | -10.3 (cluster -2.3) | - | - | L3 push 0.4 (the 50 % pattern break) |
| 17.067 | 512.0 | `pin_thock` | hit | -2.3 (cluster -2.3) | - | pin in gap | pin 18 "Sab kuch thora bara" v19 |
| 17.067 | 512.0 | `slot_tick` | hit | -18.0 (cluster -6.0) | n=3, dur=0.133; pan +0.30 | - | counter v19 |
| 18.133 | 544.0 | `card_slide` | hit | -9.1 (cluster -5.1) | - | - | CALL NOW pill SLAMs in |
| 18.133 | 544.0 | `pin_thock` | hit | +0 | - | pin in gap; carve 19.218-21.743 | pin 19 "Call now bhi likho" v20 |
| 18.133 | 544.0 | `slot_tick` | hit | -15.8 (cluster -3.8) | n=3, dur=0.133; pan +0.30 | - | counter v20 |
| 19.200 | 576.0 | `pin_thock_dark` | hit | -6 | pan -0.21 | pin in word; carve 19.250-21.743 | pin 20 "Aur pop." v21 (inside "Aur") |
| 19.200 | 576.0 | `pop` | hit | -21.1 (cluster -5.1) | pitch=1.0962; pan -0.25 | -8.0 dB; carve 19.250-21.743 | second starburst POPs in |
| 19.200 | 576.0 | `slot_tick` | hit | -17.8 (cluster -3.8) | n=3, dur=0.133; pan +0.30 | brief -14 under L7/L9; carve 19.250-21.743 | counter v21 |
| 19.467 | 584.0 | `clock_tick` | hit | -19.5 (cluster -1.5) | n=7, bpm=225.0; hp 4500 | -18 hp 4500 under L9 | clock chip "3:47 AM" ticking (from the 2nd 8th: f576 already has 3 starts) |
| 19.733 | 592.0 | `pin_thock_dark` | hit | -6 | pan -0.10 | pin in word | pin 21 "Logo aur bara." v22 (inside "ek,") |
| 19.733 | 592.0 | `slot_tick` | hit | -19.1 (cluster -5.1) | n=3, dur=0.133; pan +0.30 | brief -14 under L7/L9 | counter v22 |
| 19.733 | 592.0 | `whoosh_fast` | hit | -19.8 (cluster -3.8) | lp 1100 | -6.0 dB, lp 1100 | pin 21: logo x1.2 |
| 20.267 | 608.0 | `pin_thock_dark` | hit | -6 | pan +0.19 | pin in word | pin 22 "Shadow kam karo" v23 (inside "ek,") |
| 20.267 | 608.0 | `slot_tick` | hit | -19.1 (cluster -5.1) | n=3, dur=0.133; pan +0.30 | brief -14 under L7/L9 | counter v23 |
| 20.267 | 608.0 | `swish_small` | hit | -21.8 (cluster -3.8) | hp 5500; pan -0.30 | -6.0 dB, hp 5500 | pin 22: shadows to alpha 0.42 |
| 20.800 | 624.0 | `pin_thock_dark` | hit | -6 | pan +0.19 | pin in word | pin 23 "Shadow wapas." v24 (inside "ek,") |
| 20.800 | 624.0 | `slot_tick` | hit | -19.1 (cluster -5.1) | n=3, dur=0.133; pan +0.30 | brief -14 under L7/L9 | counter v24 |
| 20.800 | 624.0 | `swish_small` | hit | -21.8 (cluster -3.8) | hp 5500; pan +0.30 | -6.0 dB, hp 5500 | pin 23: shadows back |
| 21.333 | 640.0 | `glitch_short` | hit | -20.2 (cluster -6.2) | dur 0.15 | -8.0 dB | D7 RGB shock (peak clutter) |
| 21.333 | 640.0 | `pin_thock_dark` | hit | -8 | - | pin in word | pin 24 "Aur energetic" v25 (D7) (inside "ek.") |
| 21.333 | 640.0 | `slot_tick` | hit | -25.1 (cluster -5.1) | n=3, dur=0.133; pan +0.30 | -8.0 dB | counter v25 |
| 21.333 | 640.0 | `whip` | hit | -19.8 (cluster -3.8) | direction=-1 | -8.0 dB | D7 RGB shock (peak clutter) |
| 21.400 | 642.0 | `card_slide` | hit | -17.8 (cluster -3.8) | lp 1100; pan +0.35 | -6.0 dB, lp 1100 | version drawer slides in (rows v24, v25) |
| 21.867 | 656.0 | `card_slide` | hit | -19.1 (cluster -5.1) | pan +0.35 | - | drawer row v26 |
| 21.867 | 656.0 | `pin_thock` | hit | +0 | pan -0.10 | pin in gap; carve 23.485-24.991 | pin 25 "Thora left." v26 |
| 21.867 | 656.0 | `slot_tick` | hit | -15.8 (cluster -3.8) | n=3, dur=0.133; pan +0.30 | - | counter v26 |
| 22.400 | 672.0 | `card_slide` | hit | -19.1 (cluster -5.1) | pan +0.35 | - | drawer row v27 |
| 22.400 | 672.0 | `pin_thock` | hit | +0 | pan -0.10 | pin in gap; carve 23.485-24.991 | pin 26 "Thora right." v27 |
| 22.400 | 672.0 | `slot_tick` | hit | -15.8 (cluster -3.8) | n=3, dur=0.133; pan +0.30 | - | counter v27 |
| 23.467 | 704.0 | `shepard_riser` | hit | -10 | duration=1.7 | body in the VO gap 21.683-23.5; tail carved under "Phir"; carve 23.517-24.991 | into the hover; starts after "...aur ek." (21.683) |
| 23.467 | 704.0 | `ui_hover` | hit | -14.3 (cluster -2.3) | hp 5000 | hp 5000 at "Phir"; carve 23.517-24.991 | the last pin hovers, undecided |
| 24.667 | 740.0 | `heartbeat_build` | hit | -8 | duration=1.2, bpm0=100.0, bpm1=160.0; lp 1200 | lp 1200 dark under L10; carve 24.717-24.991 | hover: 3 accelerating beats from 23.467, last lub on f740; its dub decays to -15 dB by the drop-out gate |
| 25.333 | 760.0 | `clock_tick` | hit | -14 | n=1, bpm=60.0 | - | held breath: one tick in the drop-out |
| 25.600 | 768.0 | `flash_hit` | hit | -3.6 (cluster -3.6) | sat 3.0 | - | PAYOFF L3 push 1.0 |
| 25.600 | 768.0 | `pin_thock_big` | hit | +0.4 (cluster -3.6) | sat 3.0 | carve 28.118-32.053 | PAYOFF: "Pehle wala hi theek tha." slams on the glass |
| 25.600 | 768.0 | `sub_drop` | hit | -5.6 (cluster -3.6) | dur=1.6; lp 120 | - | PAYOFF sub |
| 26.133 | 784.0 | `typing` | hit | -6 | n=2, cps=8.0 | - | Ctrl+Z press: "Ctrl+Z x26" chip POPs |
| 27.078 | 812.3 | `ui_tick` | hit | -16.2 (cluster -2.2) | pitch=0.9292; hp 4000; pan +0.30 | - | rewind: counter v27 -> v26 (the f672 step undone) |
| 27.110 | 813.3 | `ui_tick` | hit | -17.3 (cluster -3.3) | pitch=0.9292; hp 4000; pan +0.30 | - | rewind: counter v26 -> v25 (the f656 step undone) |
| 27.140 | 814.2 | `ui_tick` | hit | -17.7 (cluster -3.7) | pitch=0.9292; hp 4000; pan +0.30 | - | rewind: counter v25 -> v24 (the f640 step undone) |
| 27.168 | 815.0 | `ui_tick` | hit | -17.5 (cluster -3.5) | pitch=0.9292; hp 4000; pan +0.30 | - | rewind: counter v24 -> v23 (the f624 step undone) |
| 27.194 | 815.8 | `ui_tick` | hit | -17.2 (cluster -3.2) | pitch=0.9292; hp 4000; pan +0.30 | - | rewind: counter v23 -> v22 (the f608 step undone) |
| 27.241 | 817.2 | `ui_tick` | hit | -16.6 (cluster -2.6) | pitch=0.9292; hp 4000; pan +0.30 | - | rewind: counter v21 -> v20 (the f576 step undone) |
| 27.285 | 818.5 | `ui_tick` | hit | -16.6 (cluster -2.6) | pitch=0.9292; hp 4000; pan +0.30 | - | rewind: counter v20 -> v19 (the f544 step undone) |
| 27.324 | 819.7 | `ui_tick` | hit | -16.9 (cluster -2.9) | pitch=0.9292; hp 4000; pan +0.30 | - | rewind: counter v19 -> v18 (the f512 step undone) |
| 27.361 | 820.8 | `ui_tick` | hit | -17.1 (cluster -3.1) | pitch=0.9292; hp 4000; pan +0.30 | - | rewind: counter v17 -> v16 (the f480 step undone) |
| 27.395 | 821.9 | `ui_tick` | hit | -17.3 (cluster -3.3) | pitch=0.9292; hp 4000; pan +0.30 | - | rewind: counter v16 -> v15 (the f448 step undone) |
| 27.427 | 822.8 | `ui_tick` | hit | -17.5 (cluster -3.5) | pitch=0.9292; hp 4000; pan +0.30 | - | rewind: counter v14 -> v13 (the f416 step undone) |
| 27.458 | 823.7 | `ui_tick` | hit | -17.7 (cluster -3.7) | pitch=0.9292; hp 4000; pan +0.30 | - | rewind: counter v12 -> v11 (the f384 step undone) |
| 27.486 | 824.6 | `ui_tick` | hit | -17.8 (cluster -3.8) | pitch=0.9292; hp 4000; pan +0.30 | - | rewind: counter v11 -> v10 (the f352 step undone) |
| 27.514 | 825.4 | `ui_tick` | hit | -17.8 (cluster -3.8) | pitch=0.9292; hp 4000; pan +0.30 | - | rewind: counter v10 -> v9 (the f320 step undone) |
| 27.540 | 826.2 | `ui_tick` | hit | -17.7 (cluster -3.7) | pitch=0.9292; hp 4000; pan +0.30 | - | rewind: counter v9 -> v8 (the f288 step undone) |
| 27.565 | 827.0 | `ui_tick` | hit | -17.3 (cluster -3.3) | pitch=0.9292; hp 4000; pan +0.30 | - | rewind: counter v8 -> v7 (the f256 step undone) |
| 27.613 | 828.4 | `ui_tick` | hit | -16.6 (cluster -2.6) | pitch=0.9292; hp 4000; pan +0.30 | - | rewind: counter v6 -> v5 (the f192 step undone) |
| 27.657 | 829.7 | `ui_tick` | hit | -17.2 (cluster -3.2) | pitch=0.9292; hp 4000; pan +0.30 | - | rewind: counter v5 -> v4 (the f128 step undone) |
| 27.698 | 830.9 | `ui_tick` | hit | -18.1 (cluster -4.2) | pitch=0.9292; hp 4000; pan +0.30 | - | rewind: counter v3 -> v2 (the f64 step undone) |
| 27.718 | 831.5 | `pw_tape_rewind` | hit | -2.0 (cluster -2.0) | hook=A | - | D9 rewind v27 -> v1 (stops 15 ms before the cut so the restore transient rises from silence) |
| 27.733 | 832.0 | `glass_tap` | hit | -13.7 (cluster -5.7) | pitch=0.5603 | carve 28.118-29.787 | RESTORE tonal tail (D6) |
| 27.733 | 832.0 | `impact_soft` | hit | +0 | - | carve 28.118-29.787 | RESTORE: v1 pristine, chip Approved |
| 27.983 | 839.5 | `swish_small` | start | -12 | hp 5000 | hp 5000 into "Har"; carve 28.173-29.787 | payoff underline draws on (27.983) |
| 28.200 | 846.0 | `shimmer` | hit | -10.4 (cluster -0.5) | hp 5500 | hp 5500 under "Har" | payoff lockup settles |
| 29.967 | 899.0 | `swish_small` | start | -18 | hp 5500 | -6.0 dB, hp 5500 | end card: JD ring draws on |
| 30.437 | 913.1 | `shimmer` | hit | -16 | hp 5500 | -6.0 dB, hp 5500 | end card: CTA keyword "bhejo" rises |
| 30.617 | 918.5 | `glass_tap` | hit | -16 | pitch=1.1207 | r2 -16 under "hi" | end card: monogram tap |
| 32.633 | 979.0 | `ui_hover` | hit | -14 | hp 5000; pan +0.25 | hp 5000 under "...aur" | the client's marker re-enters (loop) |
| 34.133 | 1024.0 | `reverse_swell` | hit | -8 | duration=0.8; lp 1000 | r2 lp 1000 under "client ne bola" | card exit + loop swell into frame 0 |

#### hook B (123 cues)

| t (s) | frame | sound | align | gain dB | params / filter / pan | VO handling | visual event |
|---|---|---|---|---|---|---|---|
| 0.000 | 0.0 | `glitch_short` | hit | -7.8 (cluster -3.8) | dur 0.1 | carve 0.085-2.640 | hook B f0: the raw v27 mess (glitch) |
| 0.000 | 0.0 | `trailer_hit` | hit | -6 | - | carve 0.085-4.900 | hook B f0: the raw v27 mess |
| 0.400 | 12.0 | `shimmer` | hit | -10 | hp 5500 | hp 5500 under "26" | hook B: focus panel + "26" key rising |
| 1.667 | 50.0 | `timeline_scrub` | start | -8 | duration=0.667, speed=2.5; hp 5000 | hp 5000 under "client ne kaha" | hook B: D1 scrub v27 -> v3 |
| 2.000 | 60.0 | `ui_tick` | hit | -18 | pitch=0.9292; hp 5500 | -6.0 dB, hp 5500 | hook B: D1 playhead tick |
| 2.333 | 70.0 | `ui_click` | hit | -6 | pitch=1.0643; hp 4000 | hp 4000 under "kaha..." | hook B: D1 snap onto the marker (cut f70) |
| 2.667 | 80.0 | `impact_soft` | hit | -4 | - | carve 3.248-4.302 | hook B: splice f80, full frame on the body |

Hook B shares everything from the splice (f80, 2.667 s) on with hook A (same pins, rewind source, end card); only its head
differs (the 7 rows above, BRIEF §7.2). Its pins at f8 / f64 and slot ticks at f32 / f64 do not exist (frozen v27 + D1 scrub).

## 4. Bed, drop-out, press, loop

- **Bed** `edit_suite` (epic_sfx), exact levels on a circular loop (0.5 s equal-power splice, seamless at the reel seam):
  -32 (0-25.067), **off** (25.067-25.333), -40 held breath (25.333-25.600), -32 (25.6-DUR, 50 ms in under the payoff);
  anchor as audio.mix (bed gain g sits at -18 + g + 8 LUFS), sidechained 5 dB under the SFX. Measured: bed -43.9 LUFS in the
  stem. `BED` (list, relative to `BED_GAIN_DB = -32`) is the audio.mix approximation only.
- **Drop-out (the one per reel)** 25.0667-25.3333 = f752-f759: every SFX that started before it, and its room reverb, is gated
  with a 4 ms raised cosine that ENDS on 25.0667; the bed is off; the music is gated (MUSIC map); the VO is silent. Measured:
  **exact digital zeros 25.0667-25.3313 in both stems and both rough mixes**. The held breath is one `clock_tick` (n=1) at
  25.3333 plus the bed at -40. The hover heartbeat (3 accelerating beats from 23.467, last lub f740 = 24.667, its dub has decayed to
  -22.6 dB re its peak when the gate closes) and the riser stop dead with the music.
- **Payoff 25.600**: `pin_thock_big` +4, `sub_drop` -2 lp 120, `flash_hit` 0, the two hit layers through a loudness-matched
  tanh drive 3 (same max momentary, lower crest). With the brief's 0 / -4 / -3 the hook's VO ("Bas ek", -9.9 LUFS momentary at
  0.35 s) was the loudest moment of the rough mix and the payoff only -11.3 (epic_mix's bus glue takes ~2 dB off it). Now
  the payoff is the max: -9.11 at 25.80 (the 400 ms window that starts on the hit), next -9.99 at 0.35 s.
- **Press 26.1333**: everything that started in the drop-out / payoff (tick, payoff stack, their room) is tape-stopped with
  the music (`epic_sfx.tape_stop_fx`, 0.4 s): the payoff's 6 s boom tail no longer drones under the rewind.
- **Rewind 26.333-27.718** at 0 dB (the brief's -6 was set before the sound existed; at -6 the rewind window sat at -22.7
  LUFS against -13.1 for the music bar before the drop): now -15.8 LUFS. It stops 15 ms before the restore so the restore
  transient rises from silence (the qa-style onset went from +41.7 ms, a 60 Hz ripple, to -3.3 ms, rise 18 dB).
- **Loop**: tails past DUR (the marker's `ui_hover`) wrap to t = 0; frame 0's `impact_soft` pre-roll (6 ms) sits at the end;
  the end card's `reverse_swell` ends exactly on DUR. Hook A seam step 0.0023 vs a median sample step of 0.0037 (continuous).
  Hook B's frame 0 is the v27 mess with its `trailer_hit`, so its seam is a designed hit (step 0.0074).

## 5. Measurements

| check | hook A | hook B | target |
|---|---|---|---|
| SFX stem integrated (internal / ffmpeg ebur128) | -18.00 / -18.0 LUFS | -18.00 / -18.0 LUFS | -18.0 ±0.1 |
| SFX stem true peak (circular 4x / ffmpeg) | -2.22 / -2.2 dBTP | -2.22 / -2.2 dBTP | <= -2.0 |
| stem limiter max GR / glue max GR | 1.55 dB at 25.625 / 2.76 dB | 1.57 dB / 2.76 dB | < ~3 dB |
| rough mix A (VO + SFX + music) integrated, TP (internal / ffmpeg) | -14.00 LUFS, -2.36 dBTP / -14.0, -2.3 | -14.00, -2.32 / -14.0, -2.3 | -14 ±0.5, <= -2.0 |
| rough Version B (VO + SFX) | -14.00, -2.27 / -14.0, -2.2 | -14.00, -2.26 / -14.0, -2.2 | same |
| max momentary of mix A | -9.11 at 25.80 (payoff) | -9.12 at 25.80 | reveal ±0.2 s |
| VO over music, speech frames (median / p10) | 11.8 / 3.8 LU | 12.0 / 4.5 LU | >= 8 (median) |
| VO over music per word, K-weighted over the word (min) | 7.1 ("ek." 21.27) | 7.7 ("ek." 21.27) | (music-supervisor) |
| VO over SFX per word (min / median) | 6.6 ("review") / 19.3 LU | 6.8 / 20.6 LU | >= 6 |
| SFX under VO in 1-4 kHz per word (min) | 12.8 dB under | 13.1 dB under | nothing busy under words |
| drop-out 25.0667-25.3313, mix + stems | exact zeros | exact zeros | true silence |
| loudness range mix A / Version B (ffmpeg) | 2.3 / 3.2 LU | 2.3 / 3.2 LU | SLATE 5-9 (see §7) |
| stems in mix A: VO / music / SFX | -14.2 / -20.7 / -16.6 LUFS | -14.1 / -21.0 / -16.5 | - |
| rewind window 26.63-27.68 vs music bar 11 | -15.8 vs -13.2 LUFS | same | no dead air |
| cue timing (isolated render of every cue vs its event frame) | 0 CHECK of 125 | 0 CHECK of 123 | ±1 frame |
| qa_measure-style onsets at the heroes (argmax 5 ms rise) | flash 4.267 +3 ms, f448 cluster +12 ms, 17.067 +3 ms, payoff 0 ms, restore -3 ms | + trailer_hit f0 +10 ms | ±33 ms |
| starts per instant (score = 1 source) | max 3 | max 3 | <= 3 |
| phone check: payoff through hp 250 Hz (4th order) | -3.1 dB | - | <= 7 dB |
| sub < 60 Hz within 10 dB of its peak | only 4.29-4.43, 17.11-17.27 and the payoff 25.62-26.50 | - | no stacked sub tails |
| local sounds `audio.qc` | 6 of 6 clean | - | [] |

The stricter "transients landing" count (whoosh passes and the slot-tick landing clicks included) reaches 5 at 12.8, 17.067
and 21.333 (pin + slot_tick + whip/air_zoom + glitch/flash + score); by the bible's definition (sounds STARTING) every instant
is <= 3. The `braam` is cued `align='start'` at 14.911 because its energy starts at its own t = 0 (40 ms before its
designed hit): onset -20 ms, designed hit +18 ms, brass peak +110 ms of f448; qa_measure skips start-aligned cues and reads
the f448 cluster (pin + flash crack) at +12 ms.

Spectrogram checks (`*_overview.png`, plus zooms of 0-4.6, 12.5-17.5, 22.8-29.0 and 32.0-34.1 s, viewed): every cue tick has
energy; the drop-out is a black column; the payoff is the brightest full-band column; the tape stop bends the payoff's partials
down at 26.13; the rewind shows accelerating rising chirps 26.9-27.7 with the tick column on top; nothing hisses constantly;
the bed is invisible under the cues (-43.9 LUFS).

## 6. Deviations from BRIEF §11 (all measured reasons above)

1. Pin variants re-decided on the measured words (2.133 dark, 6.400 full, 21.333 dark at -8).
2. Pitch multipliers recomputed (brief values 44 c flat); `pop`, `ui_click`, `ui_tick`, `bubble_pop`, end-card tap pitched too.
3. Payoff stack +4 / -2 / 0 with loudness-matched saturation (brief 0 / -4 / -3) so the reveal is the loudest moment.
4. `shepard_riser` 1.70 s (brief 2.067) so it starts after "ek." (21.683); `heartbeat_build` 1.2 s, 100 -> 160 bpm, last lub
   f740 (brief: 1.6 s ending on 25.067 would put the last lub ON the gate and cut it at its transient).
5. `clock_tick` (3:47 AM chip) starts on the second 8th (f584, n=7): at f576 it made 4 starts with pin + pop + score.
6. `glitch_short` truncated (0.10 s at f384 and hook B f0, 0.15 s at f640) and `downlifter` dur 0.3 (cream fill, 12 f) so
   their bodies do not run under the next word.
7. `pw_tape_rewind` at 0 dB, ending 15 ms before f832, source = hook A's body for both hooks (the picture rewinds `W_core`).
8. The payoff's tails tape-stop with the music at the press (the brief only stops the music).
9. No swish on the reaction-cam tile exit (f502): `air_zoom`'s rise (16.447 -> 17.067) already covers that move.

## 7. Open items

- **Music-supervisor / lead:** the rough mix's loudness range is 2.3 LU (Version B 3.2) against SLATE §5.1's 5-9. The SFX
  cannot move it: a VO-led reel (57 % speech, VO at -16 LUFS into a -14 master) with the music ducked 9 dB under the voice
  reads as one steady level in 3 s windows. Either the target is relaxed for VO reels or the final mix rides the intimate
  v1 bars and the end card down. Also per word, "ek." (21.27, bar-10 peak clutter) is 7.1 LU over the ducked music (median
  11.8 LU passes the >= 8 rule).
- **Creative director:** L9 / D7 option (a) is what is built (see §2). Hero pre-laps at 4.267, 14.933 and hook B f0 are
  carved, not moved (the picture owns those frames).
- **QA (no master exists yet: `pehle_wala.py` is not built):** after the render, run
  `python3 $QA cues <master.mp4> <RW>/audio/pehle_wala_sfx_A_cues.json` and check frames n-1, n, n+1 at f8, f448, f512,
  f768, f784, f832, f896, f979, and the D9 tick crossings against the counter (BRIEF §7 rows 40-43). Expect no CHECK
  except possibly 27.733 if the music restart masks the restore (measured on the stem: -3.3 ms).
- **Shared modules:** SHARED_REQUESTS #10 (`audio._write_wav` silently writes a half-length stereo file from an (N, 1)
  array, which `audio.read_wav` returns for mono wavs) and #11 (`epic_mix.mix_reel` raises on a mono VO).
