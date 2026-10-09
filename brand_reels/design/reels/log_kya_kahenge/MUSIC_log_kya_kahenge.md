# MUSIC · Reel 5 · C15 · Log Kya Kahenge (music map run 1 · run 2: measured EP ducks + final mix)

Date 2026-10-08 (run 1) · 2026-10-09 (run 2) · Author: music-supervisor · Plan: `BRIEF.md` §12 (binding), `HANDOFF.md` r3 ·
Code: `pipeline/jawad_reels/log_kya_kahenge_music.py` (score), `pipeline/jawad_reels/log_kya_kahenge_mix.py` (final mix)

Nobody on the team can listen, me included. Everything below is measured, not heard.

## Source and licence
- **Source:** a procedural numpy score, written for this reel. It uses the shared instruments in
  `workspace/brand_reels/sfx/epic_music.py` (`kick`, `hat`, `pad_chord`, `epiano`) and two `epic_sfx` textures
  (`dark_drone` seamless bed, `tension_drone`). There are no song samples, no AI model and no trending audio. ACE-Step
  was not needed.
- **Licence:** original work for @jawad_mp4, safe for organic posts, ads and cross-posting. Audio name: "Original
  audio · Log kya kahenge · @jawad_mp4".
- **Regeneration:** the output is deterministic. A fresh process gives a bit-identical file:
  - music_full.wav sha256 `41421a08…bd03c1` (run 2; run 1 was `21c3c3b2…7b632e13`). The EP dips now follow the
    measured VO stems, whose sha256 are recorded in `music_full.json` (`vo_windows.provenance`).
  - The dependency hashes are in `music_full.json`. The score depends on the git-ignored `epic_music.py` and
    `epic_sfx.py`. If either changes, the hash changes too.

```bash
cd pipeline/jawad_reels
tools/heavy.sh python3 log_kya_kahenge_music.py build     # ~15 s: music_full.wav + stems + music_full.json
tools/heavy.sh python3 log_kya_kahenge_music.py verify    # onsets, grid fits, ebur128, seam, harmony, PNGs
```

## Files (`<RW>` = `workspace/jawad_reels/log_kya_kahenge`)
| file | spec |
|---|---|
| `<RW>/music/music_full.wav` (+ `lkk_music.wav` symlink, the name in BRIEF §12) | 48 kHz, 24-bit PCM, stereo, exactly 1,689,600 samples (35.200 s), -16.0 LUFS, -3.3 dBTP |
| `<RW>/music/stems/music_stem_{drums,bass,harmony,lead,fx}.wav` | same format and gain chain. The five stems sum to the mix to within -132.5 dBFS (24-bit rounding) |
| `<RW>/music/music_full.json` / `music_full.verify.json` | the event list (33 events: time, frame, bar.beat), gains and render numbers / every measurement below |
| `<RW>/music/music_full_spectrogram.png`, `music_zoom_dropout_seam.png` | full spectrogram with bar lines; zooms of the drop-out and the loop seam |

The final mix (`log_kya_kahenge_mix.py`) re-levels this file to -18 LUFS under the VO, so one file serves both levels.

## Key
- **D minor, Sa = D** (D3 146.83 Hz). The sub and the braam root are **D1 36.71 Hz**.
- Chords per bar: drone D/A (bars 0-4) · Dm · Bb · Gm/D (bars 5-7) · Bbmaj7 · F/A · Dm(add9) (bars 8-10).
- Tonal SFX:
  - Pitch them to D or A: `shimmer`, `glass_tap` (end-card cues) and the clunk's `ui_click`, if it is pitched.
  - Optional: `lkk_flood_hum` sits at 100 Hz, which falls between G2 and Ab2 and rubs against the A2/Bb2 pads from
    25.6 s. At -30 dB this is the sound-designer's call: either keep it (realistic 50 Hz mains) or tune its
    fundamental to 110 Hz (A2, in key).

## Music map (75 BPM; beat = 0.8 s = 24 f; bar = 3.2 s = 96 f; bar n starts at f = 96n)
| section | bars | t0-t1 s (frames) | edit events (BRIEF §5) | music events (as built) |
|---|---|---|---|---|
| A hook | 0 | 0.0-3.2 (0-95) | lit tiers, head-snap wave f6-f18, `LOG KYA kahenge?`, V1 | `dark_drone` at loop position 0 on frame 0: beatless, sound already moving. The music has no hit here (the SFX `impact_soft` owns f0) |
| A build | 1-4.75 | 3.2-15.2 (96-455) | J1-J4 fly-outs, O2 at f288, JD rise, the head tilt at f384, V2 8.8-14.8 | `tension_drone` from 3.2 (root D1, 12.0 s, its hit on 15.2), with a crescendo of -9×(1-p²) dB on top. From 11.2 the `dark_drone` gives way (-8 dB by 15.2), so the build is still rising when it is cut |
| **drop-out** | 4.75-5 | **15.2-16.0 (456-479)** | picture holds, heartbeat f468 (SFX) | the whole music bus is gated after the reverb: digital silence, 4 ms edges. The drones stop dead on 15.2 |
| B pulse | 5-7 | 16.0-25.6 (480-767) | **reveal f480**, orbit, single image f576, focus pull, O6 f672-f719, V3-V5 | felt kick (punch 0.5, lp 160 Hz) on every beat, 16.0 … 24.8 (12 hits; downbeats +2.5 dB) · sub D1+D2 (lp 120) 16.0-25.2 · dark pad (700 Hz cutoff) **Dm** bar 5 · **Bb** bar 6 · **Gm/D** bar 7, cross-fading on the bar lines · closed hat on the off-8ths 22.8 / 23.6 / 24.4 · from 25.2 to 25.6 the pad plays alone |
| C warm | 8-10 | 25.6-35.2 (768-1055) | **payoff f768** (the clunk), the gag f876-f888 (tap f888), end card f936, V6, V7, loop | no drums · warm pad (1400 Hz cutoff) **Bbmaj7** enters on 25.6 · **F/A** bar 9 · **Dm(add9)** bar 10, released by 35.2 · EP motif A4 26.4 · F4 28.0 · D4 30.4 · C4 31.2 · A3 32.8 · D4 34.4 (ends 35.15). The notes inside the MEASURED V6 / V7 windows sit 6 dB down; the C4 dips from 31.31 to -6 dB at 31.37 (run 2) · 29.6 (the tap) stays empty · `dark_drone` fades back in 33.6 → 35.2 at loop position (t-35.2) mod 24, so the sample after 35.2 is frame 0's drone |

- **Bus:** this is the chain from `EM.render` without its end fade (SHARED_REQUESTS R3), made loop-safe:
  1. a sidechain to the kick (5 dB, 5/160 ms; the sub is included so the low end stays clear);
  2. studio reverb at -18 dB by circular convolution (the tail wraps onto the start, as in a steady-state loop);
  3. the drop-out gate;
  4. a circular level rider (amount 0.3, with the drop-out excluded);
  5. -16 LUFS;
  6. a 4× true-peak limiter at -3.3 dBFS.
- **Hand-off rules:**
  - The hero hits (braam and impact_big at 16.0, the clunk at 25.6) belong to the SFX stem and are not doubled in
    the music.
  - At 16.0 the score adds only its first pulse, so 3 sounds start on that instant (braam, impact_big, pulse).

## Measurements (`music_full.verify.json`)
| check | result | target |
|---|---|---|
| format (ffprobe) | pcm_s24le, 48000 Hz, 2 ch, duration_ts 1,689,600 (35.200000 s) | exact |
| loudness (ffmpeg ebur128) | **I -16.0 LUFS, true peak -3.3 dBFS, LRA 5.4 LU** (numpy BS.1770: -16.002 / -3.30 dBTP) | -16 LUFS, ≤ -2.0 dBTP |
| limiter | max gain reduction 1.03 dB; more than 0.5 dB for only 0.076 s | light |
| tempo, kicks (band-envelope onsets in the mix, least squares over 12 hits) | **75.0001 BPM**, residual ≤ 1.9 ms | ±0.2 BPM |
| beat phase, kicks | +5.6 ms, which is the kick's own attack rise. The same detector on isolated reference kicks placed exactly on the grid reads +4.5 to +4.8 ms, so the net offset is about +1 ms | ±15 ms |
| grid fit (spectral flux), 20-250 Hz, B section | 75.037 BPM, phase -7.1 ms. The same fit on the exact-grid reference kicks reads the same: 75.037, -7.1 ms (method bias), so the net offset is 0 | ±15 ms |
| grid fit, full band, bars 5-6 | 75.075 BPM, -6.7 ms (strength ×3.2) | on grid |
| grid fit, full band, whole of B (the agent's `beatgrid`) | 75.00 BPM, phase 0.39 s, which is half a beat. It locks onto the off-8th hats in bar 7 (×36.6 in the 6-16 kHz band at +390 ms), the brightest transients. As designed | see note |
| downbeats | the downbeat kick is the loudest of its bar in bars 5, 6 and 7. Chord changes sit on the bar lines (chroma below) | bar lines |
| hats (6-16 kHz envelope) | +0.1 / +0.3 / +0.4 ms | ±1 frame |
| EP notes (harmonic-bin flux in the mix) | -7.5 to 0.0 ms. On the lead stem the envelope reads +2.3 to +4.2 ms | ±1 frame |
| blind onsets in the metered part (≥ 16.0 s) | 0 strong onsets more than 15 ms off the 8th-note grid. The only strong onsets before 16.0 are the comb sweeps of the beatless build's texture (13.5-15.1 s), which by design follow no grid | 0 |
| harmony (100-400 Hz chroma on the chord stem) | 8/8 bars match: D/A · D/A · Dm · Bb · Gm/D · Bbmaj7 · F/A · Dm(add9) | match |
| drop-out 15.200-15.996 | **max |x| = digital zero (-240 dBFS)**; -14.7 dBFS RMS in the 200 ms before, -7.5 dBFS in the 200 ms after | ≤ -60 dBFS |
| sections (LUFS integrated / max momentary) | A hook -19.3 / -18.5 · A build -17.0 / -12.9 (rising to its peak in the last 0.4 s) · **B -14.2 / -10.4** · C -16.6 / -13.6 | lowest at the hook, peak at the reveal |
| loudest momentary | **16.2 s** (the pulse entry after the drop-out) | at the reveal |
| loop seam | last 50 ms vs first 50 ms: **0.54 dB**. Sample step at the seam is 0.00103 (the median step there is 0.00283). Energy above 6 kHz at the seam is +1.9 dB over its median (no click). The only onset within 100 ms of the seam is the drone's texture at +79 ms, strength 7.9, below the excerpt's median of 9.2. There is no fade | ≤ 6 dB, no click |
| determinism | build in a fresh process: identical sha256 for the mix and all 5 stems | identical |

Phone translation: in B, 71 % of the energy is below 60 Hz (the felt kick and the D1 sub). Phone speakers lose that
band. There the pulse still reads in two ways: the pad pumps on every beat (a 5 dB sidechain), and the hats come in
for bar 7.

## What I saw in the spectrogram (`music_full_spectrogram.png`, zooms viewed)
- **0-15.2 s:** a dense, beatless drone. The energy sits under 1 kHz with a faint air band at 2-6 kHz. A slow low-pass
  opening and comb sweeps build through bars 3-4. The waveform grows into 15.2 and ends in a vertical cut.
- **15.2-16.0 s:** a fully black gap.
- **16.0-25.6 s:** a bright sub-100 Hz burst on every beat, the pad pumping between them, and three thin vertical hat
  lines up to 16 kHz in bar 7. The sub ends at 25.2 and the pad plays alone into 25.6.
- **25.6-35.2 s:** the band under 100 Hz goes dark. Warm pad harmonics reach about 6 kHz, and the EP notes show as
  brighter partials at 220-440 Hz. The drone's low band returns over the last 1.6 s.
- **Seam zoom:** continuous across 35.2 → 0.0, with no vertical line and no level step.

## Run 2 (2026-10-09): EP duck windows from the measured VO

- **Windows** (`vo_windows()`, read at build time from `<RW>/vo/lkk_vo_{A,B}.wav` + `.words.json`; per line the earlier of
  the first word and the first voiced sample, the later of the last word and the last voiced sample, 20 ms RMS > peak -
  45 dB, union of hooks A and B): **V6 25.970-28.990, V7 31.430-35.080** (r1 used the BRIEF r2 targets 26.0-28.667 and
  32.0-35.133). Fallback constants (the HANDOFF r3 measurements) only when a stem is missing.
- **Rule** (`ep_duck_plan` / `ep_gain_curve`): fully -6 dB 60 ms before the first voiced sample, after a 60 ms
  raised-cosine ramp; a note that starts inside a window is -6 dB whole; no note swells back up inside itself.
- **Plan and measurement** (`music_full.verify.json` → `ep_duck`, raw lead stem against the same score composed without
  dips): A4 26.4 whole -6.00 dB · F4 28.0 whole -6.00 · D4 30.4 free 0.00 (ends 31.15, before V7) · **C4 31.2: 0.00 dB
  before the ramp, -6.00 dB after 31.37** (bussed lead stem: -8.0 dB step across the duck point against -1.1 dB natural
  decay) · A3 32.8 whole -6.00 · D4 34.4 whole -6.00.
- **Everything else re-verified unchanged:** -16.0 LUFS (ffmpeg) / -3.3 dBTP / LRA 5.4; kicks 75.0000 BPM, phase +5.6 ms
  (detector bias +4.5 to +4.8 ms), residual 1.9 ms; harmony 8/8 bars; drop-out 15.2-15.996 digital zero; 0 strong
  onsets > 15 ms off the 8th grid after 16.0; seam step 0.00103 vs median 0.00285, last vs first 50 ms 0.54 dB; stems
  sum to the mix within -132.5 dBFS. Spectrogram viewed: drop-out black, pulse on the bar lines, no sub in C until the
  drone returns at 33.6, no end fade.

## Final mix (run 2): `log_kya_kahenge_mix.py` (replaces `log_kya_kahenge_music.py mix`, which now delegates to it)

```bash
cd pipeline/jawad_reels
tools/heavy.sh python3 log_kya_kahenge_music.py build && tools/heavy.sh python3 log_kya_kahenge_music.py verify  # score
tools/heavy.sh python3 log_kya_kahenge_mix.py all --hook AB          # ~80 s: both hooks, versions A + B, stems, verify
tools/heavy.sh python3 log_kya_kahenge_mix.py determinism --hook AB  # rebuild in scratch, sha256 compare (passed)
# render flag: --no-sfx-build --audio <RW>/audio/log_kya_kahenge_mix.wav  (a link to final/; hook B: ..._hookb_mix.wav)
```
- **Inputs:** `<RW>/vo/lkk_vo_{A,B}.wav` (mono → L = R), `<RW>/audio/log_kya_kahenge[_hookb]_sfx_stem.wav`, this score.
  Each must be exactly 1,689,600 samples at 48 kHz (no silent padding).
- **Outputs** (`<RW>/audio/final/`, 48 kHz 24-bit stereo, 1,689,600 samples): `<name>_mix.wav` (version A: VO + SFX +
  music), `<name>_vo_sfx.wav` (version B: VO + SFX, for a song added in-app), `<name>_stem_{vo,sfx,music}.wav` at A's exact
  gains (they sum to A within -138.5 dBFS = 24-bit rounding), `<name>_mix.json`, `<name>_mix.png`, `<name>_zooms.png`;
  `name` = `log_kya_kahenge` (hook A) / `log_kya_kahenge_hookb`. Links at the HANDOFF paths `<RW>/audio/<name>_mix.wav`
  and `<name>_vo_sfx.wav`.
- **Chain:** the epic_mix series spec (VO polish -16 LUFS; SFX -18, -4 dB under VO; music -18, -3 under SFX, -9 under
  VO; glue 2:1; limiter -2.3 dBFS; -14 LUFS) with the C15 fixes:
  1. **Loop-safe (R6c):** every input is padded circularly by 4 s, processed, cropped. The processed audio after 35.2 s
     equals the cropped start to < -240 dBFS (the crop is the steady-state loop).
  2. **Mono VO (R6a):** loaded as L = R.
  3. **Reveal contrast (R6b):** the glue is capped at 1.5 dB inside 15.97-16.40, and the score is ducked a further 10 dB
     under the SFX reveal 15.99-16.33 (its first pulse and D1 sub stacked on the braam's D1 and drove the limiter to
     6.1 dB). V3's ducks take over from 16.18.
  4. **VO per line (risk 7):** a per-line top-up duck of the music, measured after the bus and iterated until every line
     sits ≥ 8.5 LU over music + SFX: V3 +4.34 dB, V4 +1.15, V5 +0.65 (hook B: V3 +4.62, V4 +1.10, V5 +0.60).

| measured (hook A / hook B) | version A (full) | version B (VO + SFX) | target |
|---|---|---|---|
| integrated, ffmpeg (numpy) | -14.0 (-14.005) / -14.0 (-14.006) | -14.0 (-14.005) / -14.0 (-14.004) | -14 ±0.5 |
| true peak wav, ffmpeg | -2.3 / -2.3 dBTP | -2.3 / -2.3 | ≤ -2.0 |
| true peak after AAC 320k (render.py's encode, no loudnorm) | -2.1 / -2.1 | -2.0 / -1.7 | ≤ -1.5 |
| LRA, ffmpeg | **3.4 / 3.2** | 5.7 / 5.4 | 5-9 (SLATE) · 2-8 (sound_design.md §6) |
| VO over music + SFX, median voiced frames | 10.0 / 9.9; lowest line V3 8.51 / 8.57 | 22.8 / 22.9; lowest line V3 12.5 / 12.2 | ≥ 8 |
| VO over music alone | 10.75 / 10.79; lowest line V4 8.68 / 8.69 | n/a | ≥ 8 |
| loudest momentary | -6.10 LUFS, window 16.0-16.4 / -6.08 | -5.57 / -5.56, 16.0-16.4 | within ±0.2 s of 16.0 |
| reveal over the next loudest | **3.23 LU** (V1 hook, 0.35 s) / 4.16 LU (V2, 10.4 s) | 4.05 / 4.90 LU | > 0 (r1: 0.7-1.0) |
| the 25.6 clunk below the reveal | 7.58 / 7.40 LU | | ≥ 2 |
| limiter | max 3.33 dB; > 3 dB for 0.021 s (two VO plosives, 11.35 and 21.43 s) / 3.35 dB, 0.022 s | 3.19 dB, 0.007 s / 3.22, 0.008 s | > 3 dB < 0.1 s |
| drop-out 15.2-15.996 | music stem digital zero; 0 silent frames; momentary (15.2-15.6) -44.1 / -43.8 LUFS; 11.2 / 10.9 LU under the programme | | ≤ -60 dBFS, ≤ 8 frames, ≈ -45 |
| loop seam | step 0.00700 vs local median 0.00516 (1.36x) / 1.34x; continuity < -240 dBFS; 6 kHz+ at the seam -15.0 dB re median | 1.31x / 1.29x | ≤ 2x, no click |
| last vs first 50 ms RMS | +10.4 / +10.6 dB (the f0 impact_soft lands at 0.000) | +13.3 / +13.3 dB | 6 dB (see open question) |
| hero onsets (qa_measure method on the wavs) | impact_big 0 ms, braam -10 (its 16.010 cue reads the 16.000 hit), ui_click -2, impact_soft -5, sub_drop -5, card_slide 0, lkk_card_tap 0 | identical | ±1 frame |
| grid (B section 16.0-25.6) | mix 20-250 Hz flux fit 75.112 BPM, phase 0.0 ms; music stem kicks 74.9998 BPM, +5.4 ms (detector bias +4.5-4.8), residual 2.3 ms (11 of 12 kicks: at 16.8 a duck release fools the envelope detector) | | ±0.2 BPM, ±15 ms |
| stems at A's gains | VO -14.1 LUFS (TP -1.7), SFX -17.8 (TP -1.6), music -21.4 (TP -4.1) | | sum = A |
| determinism | rebuild in a scratch folder: identical sha256 for all 10 files | | identical |

Pictures viewed: `final/log_kya_kahenge_mix.png` (A spectrogram with bar lines and VO spans, loudness lanes, B
spectrogram), `final/log_kya_kahenge_zooms.png` (drop-out + reveal, clunk, both seams with a ±12 ms sample plot: smooth
through the seam), the hook-B pair, and `final/log_kya_kahenge_mix_qaspec.png` (qa_measure `audio --spec`). The drop-out is
a dark band with only the room tone and heartbeat; the reveal is the one full-band burst; no vertical line at either seam.

**LRA (HANDOFF risk 5), measured options:** A's gaps (2.8-8.5, 14.3-16.1, 29.2-31.2 s) are filled by the score at its
unducked level. A trim of the music in those gaps gives LRA(A) 4.3 at -4 dB, 4.8 at -8 dB and 5.3 at -12 dB
(`GAP_TRIM` in the mix module, off by default): reaching 5 LU means muting the build's climax into the drop-out and the
gag. I left it off; version B passes (5.4-5.7).

## Open questions
- **LRA of version A (lead):** 3.4 LU (hook A), 3.2 LU (hook B) against SLATE §5.1's 5-9. The research mix spec
  (`sound_design.md` §6) says 2-8 and the reference reels measure 2.4-6.7. Waive for version A, or accept the -12 dB gap
  trim (one constant in `log_kya_kahenge_mix.py`).
- **Last vs first 50 ms (QA, HANDOFF §13):** the +10-13 dB difference is the sound-designer's frame-0 `impact_soft` (the
  loop landing), not a level jump: the seam step is 1.3x the local median and the processed audio is continuous through
  it. BRIEF §18 applies the 6 dB rule to the score, which passes (-1.1 dB). If the lead wants the mix rule met literally,
  the sound-designer would have to lift the end of the loop swell (cue 47) after V7 ends.
- The score's two dependency modules live in the git-ignored `workspace/brand_reels/sfx/` (`sound_design.md` §7 item
  5). To make the score rebuildable from git alone, the lead should copy them into the repo.
- No human has auditioned the bed or the mix. Priority listen: the `tension_drone` texture at 12-15.2 s, the felt pulse
  on phone speakers, and the reveal 16.0-16.4 (limiter ≤ 3 dB there, glue ≤ 1.5 dB).
