# MUSIC: Reel 3 · C08 · Ek Frame ki Keemat (music map, source, measured bed)

Owner: music-supervisor · 2026-10-08 · Plan: `BRIEF.md` §12 (+ §4, §5, §11, §18) · Code: `pipeline/jawad_reels/ek_frame_ki_keemat_music.py`
· Bed: `workspace/jawad_reels/ek_frame_ki_keemat/music/music_full.wav` (+ `stems/`, `music_full.json`, `music_full.verify.json`, `qa/*.png`).

## Source and licence
- **Procedural, original.** The score is written in `ek_frame_ki_keemat_music.py` (style `c08_epic`, registered at runtime as
  `EM.STYLES['c08_epic']`). It uses epic_music's instruments (`string_note`, `hat`, `bass808`, and `kick` only as the inaudible
  sidechain key) and the epic_sfx sounds `harmonium_swell`, `dhol_hit`, `trailer_hit`, `shepard_riser` and `reverse_cymbal`.
  No samples of any song, no AI model and no trending audio are used. It is an original work for @jawad_mp4 with no third-party
  licence. Version A can be used for organic posts, ads and cross-posting.
- The source order in the agent spec does not apply here. There is no client track, and Higgsfield, Magnific and the other paid
  generators are off-limits for music. ACE-Step was not needed because the procedural bed meets the brief. This bed is the
  project's chosen first choice (`research/sound_design.md` §5), not a placeholder.
- AI disclosure: the music is not generative-AI audio. The AI label stays because of the VO.
- Deterministic: two renders give byte-identical files. sha256 of `music_full.wav` is `08bafc44…cb794`; every stem's hash is in
  `music_full.json`.

## Key and grid (pitch your tonal SFX here)
- **D, Phrygian-dominant colour** (D Eb F# G A Bb C, `EM.PHRYG_DOM`). Sa = D4 **293.66 Hz**, Pa = A.
- Pitch targets for tonal SFX: D (73.42 / 146.83 / 293.66 / 587.33 Hz) or A (55 / 110 / 220 / 440 Hz). The `pitch_to` targets in
  BRIEF §11 (587.33, 440, 293.66) all fit.
- Pitched drums are tuned into the key: the dhol to D2 (`pitch` 1.266) and the taiko to A1 (`pitch` 0.887).
- The pitch classes measured on the bed match the plan:

| section | measured pitch classes (strongest first) |
|---|---|
| bar 0 | D, A |
| bars 1-2 | D, Eb, F# |
| bar 5 | Eb, F#, G |
| bar 10 | C, D |
| bar 13 | C, D, Eb |
| drop | A, D, Eb (808 peak 73.3 Hz) |

- Grid: 100 BPM. A beat is 0.6 s (18 f), a bar is 2.4 s (72 f), an 8th is 0.3 s (9 f). 14 bars = 33.6 s = 1,612,800 samples
  = 1,008 frames. Bar 0 = frame 0.

## Music map
| section | bars | t0-t1 s | f | edit events (BRIEF §5) | music events | harmony |
|---|---|---|---|---|---|---|
| cold | 0 | 0.0-2.4 | 0-71 | frame plays, pause click 0.3, seams 0.6, explode 0.9 | harmonium Sa-Pa-Sa (D3 A3 D4) swell -3 dB, peak 3.456. The loop bar's seam drone is already sounding at f0 (folded, peak 0.72) | drone D |
| explode / orbit / fly-through | 1-4 | 2.4-12.0 | 72-359 | orbit 2.4, splice 3.0, "12" lands 4.8, cover 5.1, tags 6.0-11.4 | string 8th ostinato enters 2.4 (LP 900, -6). Swells on bars 2 and 4 | i i bVI i |
| re-hook | 5 | 12.0-14.4 | 360-431 | stop on pane 12 (12.0), flicks 13.2-14.4 | strings thin to -9, LP 900 | bII (Eb): the question |
| resolved "with" | 6 | 14.4-16.8 | 432-503 | frame comes alive 14.4, C3 approach 16.0 | strings -5 (a 1 dB lift), LP 900 → 1200. Swell on bar 6 | i: the answer |
| corridor / surge / lanes / rush | 7-10 | 16.8-25.8 | 504-773 | C3 cut 16.8, "360" 20.4, lanes 21.9, rush 24.0 | LP 1200 → 1500 and -5 → -3 by 24.0. Felt taiko (A1, LP 1500) on beats 1 and 3 of bars 8-10, -14 → -8: 19.2 20.4 21.6 22.8 24.0 25.2. Swells on bars 8 and 10. `shepard_riser` 2.2 s (-10) and `reverse_cymbal` 1.2 s (-6), both aimed at 26.4 and cut dead at 25.8 | bVI i bVI bVII |
| **drop-out** | 10.75-11 | 25.8-26.4 | 774-791 | stack frozen, play click 26.067 (SFX) | **digital silence 25.800-26.392** (peak 0.0). 4 ms edges at 25.796-25.800 and 26.392-26.396 | - |
| **DROP** | 11 | 26.4-28.8 | 792-863 | payoff cut + C8, `EK FRAME KI keemat` | **dhol_hit 0 dB at 26.400** (D2). Dhol chaal on 2&, 3, 4& (-4 / -3 / -6). Hats on 8ths -6. 808 on D2 -6. Strings LP 1500, -3. The bar 10 harmonium swell continues (peak 27.456) | i |
| resolve | 12 | 28.8-31.2 | 864-935 | lockup exits 29.1, end card 29.4 | chaal at -8 (1) / -10 / -9 / -12. 808 -9. No hats. Strings LP 1200, -5. Swell -6 | bVI |
| loop bar | 13 | 31.2-33.6 | 936-1007 | card holds, `loop_world` 33.0-33.6 | strings LP 900, -7. Harmonium seam drone (starts 30.0, peaks 0.72 s after the seam). `reverse_cymbal` 2.4 s (-8) **ends exactly on 33.600**. Nothing fades | bVII → i across the seam |

The hero hit stays in the SFX stem (`ember_slam`, `impact_big` at 26.4). The music's own transient there is the dhol. There is
no braam, no sitar, no dholak and no `trailer_hit` at f0 in the music.

## What differs from BRIEF §12, and why

**Loop and drop-out**
- **The tails are folded back, not cropped.** I render two extra bars and add everything past 33.6 back onto the start, which is
  a circular render. The loop bar's drone and reverb continue into frame 0, and no fade lies inside the reel. A crop would cut
  the tails dead at the seam.
- **The gate edges sit outside the drop-out.** The gate closes at 25.796-25.800, so f774-f781 (25.800-26.067) are digital
  silence, which the §18 check needs. It opens at 26.392-26.396, before the drop dhol's first sample at 26.397, so the attack is
  untouched.
- **A seam drone fills bar 13.** A harmonium swell starts at 30.0 and peaks 0.72 s into the next loop. This is §5 row 41's
  "loop bar (cold drone)". Without it, frame 0 opened at -30 LUFS, close to silence; it now opens at -24.8.

**Tuning**
- **The dhol is retuned to D2.** desi_epic's pitches (1.0 / 1.25) put the dagga on Bb and a shell mode on F3, an F natural
  against the scale's F#. The first render measured F as the strongest pitch class in the drop.
- **The taiko is at pitch 0.887 instead of 0.9.** That is the brief's 0.9 moved 22 cents onto A1.
- **The taiko is low-passed at 1.5 kHz.** This keeps its anvil ring out of the 1-4 kHz band under V7 and V8.

**Strings**
- **The ostinato is one octave above desi_epic's.** Every string fundamental is at or above 233 Hz (Bb3), so the strings sit
  above the male VO's F0 (bible §5.3).
- **Beat accents:** +2 dB on the downbeat and +1 dB on the other beats.
- **Harmony per bar:** bII at the re-hook resolves to i on "zinda". The bars before the drop run bVI-bVII-i, and the loop bar
  goes bVII → i across the seam.
- **Bars 1-4 are at -6 instead of the brief's -5.** Bar 6's "alive" lift and the build then read as an arc: intro -17 to -19
  LUFS per bar, build -16 to -14.5, drop -10.9 (bible §5.4: lower the intro, not the drop).

**Bus**
- **Perc peak shave of 6 dB.** Without it, the bus limiter took up to 6.4 dB off the drop.
- **Sidechain 3 dB instead of epic_music's 5.** The drop's strings stay forward.
- **True peak is at or below -3.0 dBTP.** The bus limiter ceiling is -3.3. This is stricter than the -2.0 asked for, and it is
  the bed spec in sound_design.md §5.4.

## Measured
| check | result |
|---|---|
| format (ffprobe) | pcm_s24le, 48,000 Hz, 2 ch, 1,612,800 samples = **33.600000 s** |
| loudness (ffmpeg ebur128) | **I -16.0 LUFS**, **TP -3.3 dBTP**, LRA 7.2 LU. The Python BS.1770 cross-check gives -16.005 / -3.30 / 7.18 |
| limiter | gain +10.25 dB; max gain reduction 3.16 dB; more than 1 dB for 1.25 s in total, on the taiko hits and the drop bar only |
| tempo / phase (spectral-flux grid fit) | whole file **100.00 BPM, phase -7 ms**, strength x6.0. String section 2.4-25.8: 100.00 BPM, -7 ms. `EM.beatgrid`: 100.00 BPM, -10 ms. The -7 ms is the STFT method's early bias (sound_design.md reports -10 ms on every style) |
| drop-window fit (26.4-31.2) | 100.1 BPM, locked to the off-beat 8th (-7 ms; on/off 0.89). This is the chaal's syncopated 2& and 4& strokes and is by design; the per-event onsets below confirm the downbeats |
| event onsets on the stems | 13 string downbeats (bars 1-13): -0.2 to +0.5 ms. 6 taiko hits: -4.5 to +8.1 ms. Drop dhol: -2.9 ms. 7 chaal strokes: -2.7 to -5.2 ms (dhol_hit's stick crack is 3 ms ahead of its hit point by design) |
| event onsets in the mix | the same events: max \|error\| 7.9 ms, median -2.1 ms. All are within ±15 ms and within a quarter frame |
| blind onsets | 101 of 110 spectral-flux peaks fall within 20 ms of the 8th grid (median -1.2 ms). The other 9 are taiko decays, the cymbal end (33.56) and chaal tails |
| drop-out | 25.800-26.392: peak 0.0 (digital silence). f774-f781 RMS: silent |
| drop | max momentary -8.8 LUFS in the window centred on 26.72, the first full window after the gate. Bar 11 measures -10.9 LUFS against -14.7 for bar 10 |
| per-bar loudness (LUFS) | bar 0: -24.8 · bars 1-4: -17.4 / -19.1 / -17.4 / -19.1 · bar 5: -19.9 · bar 6: -18.1 · bars 7-10: -16.2 / -16.2 / -14.5 / -14.7 · gate · bar 11: -10.9 · bar 12: -13.7 · bar 13: -18.6 |
| phone check (`hp` 250 Hz, 4th order) | loses 3.9 dB at the reveal (26.4-26.8). Bar 11's energy below 120 Hz sits 8.7 LU under the full band: no sub build-up |
| band balance (Welch, relative to total) | sub < 60 Hz: -21.5 · 60-250: -3.7 · 250-1k: -2.6 · 1-4k: -17.6 · 4-8k: -31.3 · > 8k: -24.6 dB. The 1-4 kHz band is kept clear for the voice |
| loop seam | last 50 ms -24.3 dBFS RMS (not silent). First 50 ms -28.1. Sample step across the seam 0.0045, against a median step of 0.0031 and a 99th percentile of 0.038: no click. Cymbal peak at 33.564; it ends on 33.600 |
| stems | strings + harmonium + perc + bass + fx = `music_full.wav` to within 2.4e-7 (24-bit rounding) |

**Spectrogram** (`qa/music_full_spectrogram.png`, `qa/music_zoom_drop.png`, `qa/music_loop_seam.png`, `qa/music_stems_loudness.png`, all
viewed):
- **Bar 0:** only the harmonium drone, a sustained band at 140-600 Hz with harmonics.
- **From bar 1:** the string 8ths show as a regular comb of short notes at 233-1500 Hz, accented on the beats. The harmonium
  swells breathe at 100-300 Hz every two bars. The faint dark notches in the drone are the instrument's own two-reed beating, not
  an edit.
- **Bars 8-10:** the taiko adds broadband low-mid columns below 1.5 kHz on beats 1 and 3. The shepard shows as a faint line rising
  at 1-2 kHz during 24.2-25.8, and the cymbal as haze above 5 kHz.
- **25.8-26.4:** a clean black column across the whole band.
- **26.4:** everything returns at once. There is a dense low end at 40-100 Hz (808 and dhol on D2), dhol strokes, hat columns at
  7-12 kHz on every 8th of bar 11 only, and strings up to about 1.5 kHz.
- **Bar 12:** thinner, with no hats.
- **Bar 13:** the strings fade back to LP 900, the reverse cymbal rises at 4-12 kHz into 33.6, and the drone runs straight
  through the seam into bar 0.
- Nothing extends past 33.6 and nothing fades inside the reel.

## Run 2 (after the VO and the SFX stem exist)
```bash
cd pipeline/jawad_reels; H=tools/heavy.sh
$H python3 ek_frame_ki_keemat_music.py render          # only if the bed must be rebuilt (deterministic)
$H python3 ek_frame_ki_keemat_music.py mix --hook B      # A + B: epic_mix.mix_reel -> <RW>/audio/ek_frame_ki_keemat_{mix,vo_sfx}.wav,
                                                         #   _stem_{vo,sfx,music}.wav, _mix.json/.png; hook B -> ..._hookb_{mix,vo_sfx}.wav
$H python3 ek_frame_ki_keemat_music.py envelopes         # <RW>/audio/ek_frame_ki_keemat_env.json (fps 30, 1,008 frames; vo/sfx/music RMS dBFS)
```
- **Inputs it expects.** The defaults are below; override them with `--vo / --sfx / --vo-b / --sfx-b`:
  - `<RW>/vo/ek_frame_ki_keemat_vo.wav` and `<RW>/vo/ek_frame_ki_keemat_hookb_vo.wav`
  - `<RW>/audio/ek_frame_ki_keemat_sfx_stem.wav` and `<RW>/audio/ek_frame_ki_keemat_hookb_sfx_stem.wav`
- **How hook B is built.** The hook-B VO and SFX run 0-3.0 s and are spliced onto the A inputs. The result is mixed, then
  crossfaded into the A mix at 3.000 s (5 ms). The B body equals A to 1 LSB.
- **Render flag:** `--no-sfx-build --audio <RW>/audio/ek_frame_ki_keemat_mix.wav`.
- **Tested so far only on synthetic placeholder VO and SFX in a scratch folder.** That run gave:
  - A: -14.0 LUFS, -2.3 dBTP
  - B: -14.0 LUFS, -2.8 dBTP
  - VO over music: 12.3 LU
  - env.json: music f774-f781 = -90 dBFS
  - hook-B body vs A: 1 LSB
- None of those numbers are claims about the real mix. Run 2 must re-measure them, including the §18 checks: max momentary
  within ±0.2 s of 26.4, and AAC ≤ -1.5 dBTP after `epic_mix.mux`.

## Notes for the sound designer and timeline
- **Every music event is on the grid.** No cut needs to move for the music.
- **Instants where the music adds an onset to SFX cues:**
  - 4.8, 12.0, 14.4 and 16.8: string downbeats
  - 19.2-25.2: taiko pulse, beats 1 and 3
  - 26.4: dhol drop
  - 27.3, 27.6 and 28.5: chaal
- **The 26.4 stack.** The music's dhol plus the SFX's `flash_hit`, `impact_big` and `sub_drop` give 3 SFX starts plus 1 music
  hit. `epic_mix` ducks the music 3 dB under the SFX.
- **Tonal SFX** go in D or A (see above).

## Open questions
- None on licensing.
- Nobody has listened to the bed. Everything above is measured.
- The in-app trending-audio path (version B, VO + SFX) still depends on Jawad's account type (sound_design.md §7.1).
