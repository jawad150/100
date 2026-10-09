# MUSIC · Reel 1 · C26 · Pehle Wala Hi Theek Tha (music map, run 1)

Date 2026-10-08 · Author: music-supervisor · Plan: `BRIEF.md` §12 (binding; §0, §7, §11 for the grid, cues and SFX) ·
Code: `pipeline/jawad_reels/pehle_wala_music.py`

Nobody on the team can listen, me included. Everything below is measured, not heard.

## Source and licence
- **Source:** a procedural numpy score written for this reel, in the `dark_pulse` grammar of
  `workspace/brand_reels/sfx/epic_music.py`. It uses the epic_music instruments (`pad` recipe, `string_note`,
  `epiano`, `kick`, `clap`, `hat`, `bass808`), the epic_sfx `trailer_hit` and `tape_stop_fx`, and four small
  instruments defined in the module (ember pad with legato release, sine sub root, short taiko, glitter shimmer).
  `EM.render('dark_pulse')` is not called (BRIEF §12: its `_common_fx` hits and 1.2 s end fade would break the
  version-by-version build and the loop). There are no song samples, no AI model and no trending audio. ACE-Step was
  not needed: the procedural bed meets every point of the brief.
- **Licence:** original work for @jawad_mp4, safe for organic posts, Trial Reels, ads and cross-posting. Audio name:
  "Original audio · Bas ek chhota sa change · @jawad_mp4".
- **Regeneration:** deterministic. A fresh process gives bit-identical files (checked twice: an in-memory re-render
  inside `verify`, and a separate build to a scratch folder compared by sha256).
  - `music_full.wav` sha256 `229bfe5f566b8705565a29d9e730a485a0313ba06bbb91768d090b17634147ae`
  - `music_hookb.wav` sha256 `72844bc6aa4aa98ed1a045f5f60e59948fc416d3ac28aaf513f7f0f0a2a81b74`
  - The dependency hashes (this module, `audio.py`, `epic_music.py`, `epic_sfx.py`) are in `music_full.json`.
    `epic_music.py` and `epic_sfx.py` are git-ignored under `workspace/` (SHARED_REQUESTS #7).

```bash
cd pipeline/jawad_reels
tools/heavy.sh python3 pehle_wala_music.py build    # wavs + stems + music_full.json + the BRIEF-name symlinks
tools/heavy.sh python3 pehle_wala_music.py verify   # format, bit identity, ebur128, grid, onsets, PNGs
# (no argument = both, about 50 s of CPU on 2 threads)
```

## Files (`<RW>` = `workspace/jawad_reels/pehle_wala`)
| file | spec |
|---|---|
| `<RW>/music/music_full.wav` (hook A) | 48 kHz, 24-bit PCM (`pcm_s24le`), stereo, exactly 1,638,400 samples (34.1333 s = 1,024 frames), **-16.0 LUFS** integrated, **-3.3 dBTP** (ffmpeg ebur128: I -16.0, TP -3.2, LRA 5.4) |
| `<RW>/music/stems/music_stem_{drums,bass,harmony,lead,fx}.wav` | same format and gain chain; the five stems sum to the mix to -132.5 dBFS (24-bit rounding) |
| `<RW>/music/music_hookb.wav` + `stems_hookb/music_hookb_stem_*.wav` (hook B, Trial) | same format; -15.75 LUFS (ebur128 -15.8), -3.3 dBTP; sample-identical to hook A from 2.6767 s |
| `<RW>/audio/pehle_wala_music_A.wav`, `pehle_wala_music_B.wav` | relative symlinks to the two files above (the names in BRIEF §12) |
| `<RW>/music/music_full.json` / `music_full.verify.json` | the 420 scored events (time, frame, bar.beat, stem, gain), sections, bus numbers, hashes / every measurement below |
| `<RW>/music/music_full_spectrogram.png`, `music_full_zooms.png` | full spectrogram with bar lines, chords and the silent windows; six zooms (hook A, drums in, drop-out → restart, loop seam, hook B, peak clutter) |

Level: the lead's spec is -16 LUFS for this file. `epic_mix.mix_reel` re-levels the music to -18 LUFS before it
ducks it (BRIEF §12's "-18 LUFS alone"), so one file serves both.

## Key
- **D minor, Sa = D3 146.83 Hz.** i-VI-III-VII, one chord per bar: **Dm · Bb · F · C**.
- Bass roots: sub-root sine D2 73.4 / Bb1 58.3 / F2 87.3 / C2 65.4 Hz (bars 0-4, 13-15); 808 D2 73.4 / Bb1 58.3 /
  F1 43.7 / C2 65.4 Hz (bars 5-11). Pads are voiced from A3 (220 Hz) up, so nothing sits in the VO's F0 band.
- Motif (epic_music `dark_pulse`, epiano, one note per 2 beats): D5 F5 | G5 F5 | D5 A4 | Bb4 A4. It ends on A (the
  5th) in bar 15 and resolves to frame 0's D: the loop is the cadence.

## Music map (112.5 BPM; beat = 0.5333 s = 16 f; bar = 2.1333 s = 64 f; bar n starts at f 64n)
Levels are the measured momentary loudness of `music_full.wav` (max / median per bar, LUFS).

| section | bar | t0-t1 s (frames) | edit events (BRIEF §7) | music events (as built) | M max / med |
|---|---|---|---|---|---|
| hook A, v1 | 0 | 0.000-2.133 (0-63) | v1 ad, pin 1 f8, chip f12, lockup, v2 f32 | ember pad **Dm** LP 700 + sub root D2; **soft kick on f0**; motif D5 on f0, F5 on beat 2 (1.067) | -17.7 / -19.4 |
| v3 | 1 | 2.133-4.267 (64-127) | pin "Aur bara", splice f80, VO L2 | **Bb**; + hats 8ths -9 dB | -17.8 / -19.1 |
| v4-v5 | 2 | 4.267-6.400 (128-191) | L3 push, NEW burst | **F**; + string ostinato 16ths (root-root-3rd-root) LP 1100 | -15.9 / -17.3 |
| v6-v7 "clean" | 3 | 6.400-8.533 (192-255) | cream fill, steam outline | **C**; hats out, pad LP 1300; **taiko 16th fill 7.467 → 8.533** (8 hits, +10 dB crescendo) | -14.5 / -17.2 |
| v8 "energetic" | 4 | 8.533-10.667 (256-319) | pin 7 "Music thora energetic", shake | **Dm**; **drums in on the pin**: kick 1 & 3, clap on 4&, hats 8ths (open on the off-8ths of 2 and 4) | -13.2 / -15.9 |
| v9-v10 | 5 | 10.667-12.800 (320-383) | sparkles, parody font | **Bb**; + 808 (the sub root hands over) | -13.6 / -15.0 |
| **re-hook** | 6 | 12.800-14.933 (384-447) | D7, Mummy's pins | **F**; drums + 808 out for 2 beats, **shimmer** (glitter) in; drums + 808 back 13.867; 1-beat taiko fill 14.4 | -12.9 / -15.8 |
| v16 "cinematic" | 7 | 14.933-17.067 (448-511) | L3 push, braam (SFX), letterbox | **C**; half-time: kick on 1, clap on 3, strings an octave down; 808 high-passed at 120 Hz so the braam owns the sub | -13.0 / -15.1 |
| pattern break | 8 | 17.067-19.200 (512-575) | "Sab kuch thora bara", L3 push | **Dm**; full time, tonal layers +1.5 dB (measured **+1.9 LU** over bar 7), strings and motif an octave up (+ doubled), **trailer_hit on 1 and 3** | -11.9 / -13.2 |
| 3:47 AM | 9 | 19.200-21.333 (576-639) | "Aur ek" x3 | **Bb**; + hats 16ths | -13.1 / -14.7 |
| peak clutter | 10 | 21.333-23.467 (640-703) | D7, version drawer, v27 | **F**; taiko 8ths (second drum layer), strings doubled at the octave, **16th kick fill on beat 4** | -13.2 / -13.6 |
| hover | 11 | 23.467-25.067 (704-751) | last pin hovers, heartbeat (SFX), L10 | **C**; drums out 23.467, strings out 24.0, 808 out 24.533, pad only | -14.9 / -18.0 |
| **drop-out** | 11.3 | **25.067-25.600 (752-767)** | marker freezes | the whole music bus gated after the reverbs (4 ms edge): **digital silence, 0 in every sample of the mix and all stems** | – |
| **payoff** | 12 | 25.600-26.133 (768-783) | pin "Pehle wala hi theek tha.", L3 push 1.0 | **Dm**, the full clutter for one beat: pad (attack 6 ms), strings x2 octaves, motif D6 + D5, hats 16ths, kick, taiko, shimmer, 808 high-passed at 120 Hz (the SFX `sub_drop` owns the sub). **The music's loudest moment: max momentary -11.45 LUFS at 25.8 s** | -11.5 / – |
| Ctrl+Z | 12.1 | 26.133-26.533 (784-795) | D9 press (typing) | `tape_stop_fx` at 26.1333 over 0.4 s on every stem: centroid 3.7 kHz → 250 Hz, level -14.8 → -22.9 dBFS, then zero | – |
| rewind | – | **26.533-27.733 (796-831)** | D9 rewind, 26 ticks | digital silence (the SFX `tape_rewind` reads `music_full.wav` at tau ≤ 26.133, which the stop does not touch) | – |
| **restore = v1** | 13 | 27.733-29.867 (832-895) | v1 pristine, `*pehle wala*`, L11 | score bar 0 again: **Dm** pad LP 700 + sub root, **soft kick on f832**, motif D5 / F5, **a warm EP Dm chord** (A3 D4 F4 A4, 12 ms strum). Onset measured 0.54 ms after 27.7333 | -17.5 / -18.6 |
| end card | 14 | 29.867-32.000 (896-959) | EndCard in, L11 | score bar 1: **Bb**, hats 8ths -12 dB | -17.9 / -19.2 |
| loop bar | 15 | 32.000-34.133 (960-1023) | card settled, L12, card exit | score bar 3 material: **C** (VII), pad LP 1300, strings -9 dB, motif Bb4 / A4; no fade; the tails past 34.133 wrap onto frame 0 | -17.1 / -18.3 |

**Bus** (all in the module docstring): kicks softened at the onset (`audio.transient` -4 dB), a fast drum tamer
(3.5:1, 7 dB over the drums' active RMS, max 5.0 dB on the kick transients), harmony + lead + fx sidechained 5 dB
to the kick and the bass 3 dB, studio reverb -18 dB per stem (+ hall -22 dB on harmony, lead and fx), the three
section groups processed apart (bars 0-11 gated at the drop-out, bar 12 tape-stopped, bars 13-15 folded circularly
onto the head), -16.0 LUFS, then a circular 4x true-peak limiter at -3.3 dBFS (release 50 ms). Limiter: max 3.5 dB,
more than 2 dB for 0.20 s in total (the kick transients of bars 5-10), more than 0.5 dB for 1.9 s. No level rider:
the intimate v1 (-19 LUFS median) against the clutter (-13.6) is the joke; music LRA 5.4 LU.

## Verification (`music_full.verify.json`, all 16 checks pass)
- **Format:** ffprobe `pcm_s24le`, 48000 Hz, 2 ch, `duration_ts` 1,638,400 (= 1,024 frames x 1,600), for A and B.
- **Loudness:** internal BS.1770 -16.00 LUFS, -3.30 dBTP; ffmpeg `ebur128=peak=true` I -16.0 LUFS, TP -3.2 dBTP,
  LRA 5.4 LU. Hook B -15.8 LUFS / -3.2 dBTP. Every stem TP ≤ -2.87 dBTP.
- **Tempo and phase** (`EM.beatgrid`, the music-supervisor's spectral-flux fit): mix 112.50 BPM, phase -8.3 ms,
  strength x7.1; drums stem 112.50, -8.3 ms, x8.8. A click track exactly on the grid reads -13.3 ms with the same
  method (its STFT bias), so the beats sit +5 ms from ideal clicks by that measure (attack shape), inside ±15 ms.
- **Onsets, blind:** spectral-flux onsets of the mix (1 ms hop, click-calibrated bias -7.3 ms): 102 strong onsets,
  97 within ±10 ms of the 16th grid (median deviation 3.0 ms). The other 5 (10.428, 12.562, 14.695, 18.962,
  21.095 s) are all the claps on 4&: `EM.clap` is three bursts at 0 / 11 / 22 ms and the peak picker takes the last.
- **Onsets, scheduled:** each drum instant (41 instants, 50 hits) re-rendered and matched against the drums stem
  (high-passed matched filter): every one within **0.15 ms** of its frame-exact time. A line fit through those
  measured times gives **112.50007 BPM**, beat 0 at +0.007 ms. The 30 motif onsets (epiano tine, above 5 kHz) sit
  0.4-0.8 ms after their times (the 3 ms attack ramp).
- **Downbeats:** kicks on the bar lines of bars 0, 4, 5, 7, 8, 9, 10, 12 and 13 measure within ±0.04 ms. Blind, per
  beat position in the bar: the low-band (30-200 Hz) rise is 6.8 dB on beat 1 vs 0.4 / 3.2 / 0.9 dB on beats 2-4,
  and the harmonic change (chroma distance) is 0.49 on beat 1 vs 0.12 / 0.27 / 0.10: **the bar line is the strongest
  position on both**. The drums' low band is 7.3 dB stronger on bar lines than on beats 2 and 4 (bars 4-10).
- **Chords:** the top three pitch classes of the harmony stem match the scored triad in all 16 bars.
- **Drop-out and rewind:** 25.0667-25.6000 and 26.5333-27.7333 are exact zeros in the mix and in every stem; the
  payoff onset lands 0.1 ms after 25.6000.
- **Loop seam:** last bar -20.2 dBFS RMS, last 100 ms -21.0 (no fade), first 100 ms -17.7; the step across the seam
  (0.0030) is below the median sample step (0.0073). Chroma C-E-G on the last beat, D-F-A on the first: VII → i.
  The tails of bar 15 wrap onto the head (folded overhang: -27.3 dBFS RMS in the first 100 ms, 9.6 dB under the
  head; below -46 dBFS after 1 s); on the very first play that is a faint C-chord release under the Dm downbeat.
- **Hook B:** head = hook A's 21.333-22.666 s sample for sample, raised-cosine fade 1.333-1.633, zeros 1.633-2.667,
  10 ms fade-in at 2.6667, identical to hook A from 2.6767 s.
- **Spectrogram (viewed):** hats appear as the HF comb from bar 1, vanish in bar 3 (the clean bar) and return with
  the drums in bar 4; the taiko fill reads as a rising row of low-mid strikes into 8.533. Bar 6 starts with a dark sub
  band for 2 beats (drums + 808 out); its glitter layer (fx stem, -32.3 LUFS in bar 6, -37 to -38 after) is too
  faint to read on the full spectrogram. Bar 7's sub below 60 Hz is dark after the
  kick (room for the braam). Bars 8-10 are the densest columns (16th hats, taiko, doubled strings and motif). Bar 11
  thins: hats stop at 23.467 and the sub goes dark from 24.533. Then a black column (drop-out), one bright full-band
  beat, the harmonics bending down to ~250 Hz over 0.4 s (the tape stop), black to 27.733, and bars 13-15 repeat the
  sparse look of bars 0-1 with hats only in bar 14. No energy past 34.133 (the file ends there); no sub build-up
  in the payoff beat: below 60 Hz it holds only the kick and taiko strikes (the drums stem carries all of that band,
  the high-passed 808 0.3 %), -5.0 dB of the beat's total energy, decaying within the beat.

## Hand-off
- **Sound designer** (tonal SFX in key; the music leaves room for the hero hits):
  - `pin_thock` D7, `pin_thock_mummy` A6 (bar 6 = F: chord tone), `pin_thock_big` D6 at 25.6 (Dm) and the restore
    `glass_tap` D6 at 27.733 (Dm) are all in key. D over the F and C bars reads as an added 6th / 9th.
  - **Braam 14.933 (root D1 36.71 Hz) sits on the C bar.** The bar-7 808 is high-passed at 120 Hz, so the braam owns
    the sub. D is the 9th of C (in key, not a chord tone); C1 32.70 Hz would be the chord root if you want one.
  - **Payoff 25.6:** the music's 808 is high-passed at 120 Hz in that beat, so `sub_drop` (lp 120) owns the sub.
  - **End card `glass_tap` at 30.617 falls in bar 14 = Bb (Bb-D-F):** pitch it to D or F. An A would rub a half
    step against the Bb. Any tonal cue in bar 15 (32.0-34.133): C, E, G or D.
  - `tape_rewind` (D9): read `music_full.wav` (or the stems) at tau ≤ 26.1333; the tape stop and the silence start
    after that point.
- **Final mix (run 2, after the SFX stem and the VO):** `epic_mix.mix_reel('pehle_wala_A', dur=1024/30,
  vo=..._vo_A.wav, sfx=..._sfx_A_stem.wav, music=<RW>/audio/pehle_wala_music_A.wav, out_dir=<RW>/audio,
  vo_offset=0.0)`, and the same for B with `pehle_wala_music_B.wav`. It re-levels the music to -18 LUFS and ducks
  it 9 dB under VO and 3 dB under SFX. Check then that the reel's max momentary lands at 25.6 ±0.2 s (the music's own
  maximum is at 25.8 s) and that speech sits ≥ 8 LU over the ducked bed.
- **Off-grid cuts:** none. Every music event is on a 16th (4 frames), except the 12 ms strum of the restore's EP chord.
- **Open licence questions:** none for the music (original, procedural, not AI-generated audio). The AI label
  question in SLATE §7.1 is about the voice and the character sheets.
