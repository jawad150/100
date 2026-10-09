# MUSIC · Reel 5 · C15 · Log Kya Kahenge (music map, run 1)

Date 2026-10-08 · Author: music-supervisor · Plan: `BRIEF.md` §12 (binding) · Code: `pipeline/jawad_reels/log_kya_kahenge_music.py`

Nobody on the team can listen, me included. Everything below is measured, not heard.

## Source and licence
- **Source:** a procedural numpy score, written for this reel. It uses the shared instruments in
  `workspace/brand_reels/sfx/epic_music.py` (`kick`, `hat`, `pad_chord`, `epiano`) and two `epic_sfx` textures
  (`dark_drone` seamless bed, `tension_drone`). There are no song samples, no AI model and no trending audio. ACE-Step
  was not needed.
- **Licence:** original work for @jawad_mp4, safe for organic posts, ads and cross-posting. Audio name: "Original
  audio · Log kya kahenge · @jawad_mp4".
- **Regeneration:** the output is deterministic. A fresh process gives a bit-identical file:
  - music_full.wav sha256 `21c3c3b2…7b632e13`.
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

The `epic_mix` final mix re-levels this file to -18 LUFS under the VO, so one file serves both levels.

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
| C warm | 8-10 | 25.6-35.2 (768-1055) | **payoff f768** (the clunk), the gag f876-f888 (tap f888), end card f936, V6, V7, loop | no drums · warm pad (1400 Hz cutoff) **Bbmaj7** enters on 25.6 · **F/A** bar 9 · **Dm(add9)** bar 10, released by 35.2 · EP motif A4 26.4 · F4 28.0 · D4 30.4 · C4 31.2 · A3 32.8 · D4 34.4 (ends 35.15). The notes inside V6 and V7 sit 6 dB down · 29.6 (the tap) stays empty · `dark_drone` fades back in 33.6 → 35.2 at loop position (t-35.2) mod 24, so the sample after 35.2 is frame 0's drone |

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

## Final mix (run 2: when the VO and SFX stems exist)
```bash
tools/heavy.sh python3 log_kya_kahenge_music.py mix --hook A   # vo/lkk_vo_A.wav + audio/log_kya_kahenge_sfx_stem.wav
tools/heavy.sh python3 log_kya_kahenge_music.py mix --hook B   # vo/lkk_vo_B.wav + audio/log_kya_kahenge_hookb_sfx_stem.wav
# override paths with --vo / --sfx / --music; render flag: --no-sfx-build --audio <RW>/audio/log_kya_kahenge_mix.wav
```
- **What `mix` does:**
  - It calls `epic_mix.mix_reel`: the music at -18 LUFS, ducked 3 dB under SFX hits and 9 dB under the VO.
  - It writes A (the full mix) and B (VO + SFX) at -14 LUFS / -2.3 dBFS TP, plus stems.
  - It also reports the music stem's level in the drop-out and where the loudest momentary falls.
- **Code-path smoke test (scratch, deleted):**
  - Inputs: a stand-in Kokoro audition as the VO, and no SFX.
  - Result: A -14.0 LUFS / -2.3 dBTP (ffmpeg), VO 10.4 LU over the music, music stem in the drop-out -240 dBFS.
- **Not yet verified:** the real VO and SFX stems do not exist yet, so the speech-over-bed check and the cue
  alignment are still to come.

## Open questions
None blocks this deliverable.
- The score's two dependency modules live in the git-ignored `workspace/brand_reels/sfx/` (`sound_design.md` §7 item
  5). To make the score rebuildable from git alone, the lead should copy them into the repo.
- No human has auditioned the bed. Priority listen: the `tension_drone` texture at 12-15.2 s, and the felt pulse on
  phone speakers.
