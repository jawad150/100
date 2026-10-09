# MUSIC · Reel 2 · C11 · Bijli Chali Gayi (music map, run 1)

Date 2026-10-08 · Author: music-supervisor · Plan: `BRIEF.md` §0, §6.11, §8 (binding), SLATE §3.2 and §5.2 · Code:
`pipeline/jawad_reels/bijli_chali_gayi_music.py`

Nobody on the team can listen, me included. Everything below is measured, not heard.

## Policy: no music bed
C11 has **no music bed and no score**. Five sources say so:
- SLATE §3.2: "No beat bed (this keeps C11's sound world apart from the four scored reels)".
- SLATE §5.2: the C11 bed is "diegetic appliances + harmonium".
- BRIEF §6.11: "Style: none. No `epic_music` style, no score.py bed, no beat bed, no tape-stop".
- packet.yaml: "No music bed and no score".
- BRIEF §8 QA: "no music bed".

The 90-BPM grid is carried by the sound-designer's diegetic cues: the backup beeps (beats 2 and 3 of bar 0), the keycap
thocks (quarters in bar 7, 8ths in bar 8) and the fan's 13.5 Hz blade pass.

The reel's only music is **the one desi voice**: a harmonium swell, rendered here as the music layer so that it can be
placed, measured and switched (mix FULL vs mix DRY) on its own. No `epic_music` bed was made and ACE-Step was not used.
Either would break the binding plan and fail QA.

## Source and licence
- **Source:** `epic_sfx.harmonium_swell` from `workspace/brand_reels/sfx/epic_sfx.py`. It is pure numpy/scipy
  synthesis on the toolkit's `audio.py` (two band-limited pulse reeds per note at +-2.5 cents, bellows pumping, reed air,
  room reverb), seed 0. It uses no samples, no song, no AI model and no trending audio.
- **Licence:** original work for @jawad_mp4, with no third-party material (no sample, no song, no model). Audio name (BRIEF
  §6.11): "Original audio · Bijli chali gayi · @jawad_mp4".
- **Regeneration:** the output is deterministic and bit-identical across processes.
  - Built four times, including once from an empty folder. Each build gave music_full.wav sha256
    `8d9a65f5…dfc927d7e0`.
  - `verify` re-renders the file in memory and finds 0 differing int24 samples.
  - The hashes of the git-ignored dependencies (`audio.py`, `epic_sfx.py`) are stored in `music_full.json`.

```bash
cd pipeline/jawad_reels
tools/heavy.sh python3 bijli_chali_gayi_music.py build    # ~4 s: music_full.wav + stems + music_full.json
tools/heavy.sh python3 bijli_chali_gayi_music.py verify   # format, ebur128, determinism, silence, placement, pitch, PNGs
python3 bijli_chali_gayi_music.py grid <wav> [--t0 --t1]  # run 2: 90-BPM grid fit of the SFX stem / mixes
```

## Files (`<RW>` = `workspace/jawad_reels/bijli_chali_gayi`)
| file | spec |
|---|---|
| `<RW>/music/music_full.wav` | 48 kHz, 24-bit PCM, stereo, exactly 1,664,000 samples (34.667 s = 1,040 f), -16.0 LUFS integrated, -5.0 dBTP, no limiter |
| `<RW>/music/stems/music_stem_harmonium.wav` | the only stem; same format and bytes as music_full.wav (sum of stems = mix, difference 0) |
| `<RW>/music/music_full.json` / `music_full.verify.json` | map, events, placement, render numbers, hashes / every measurement below |
| `<RW>/music/music_full_spectrogram.png`, `music_zoom_payoff.png` | full spectrogram with bar lines; zoom of bar 9 beat 2 to bar 11 beat 1 (drop-out, swell, f880) |

## Key
- **D major, Sa = D3 146.83 Hz.** The harmonium chord is D3 A3 D4 F#4 (MIDI 50 57 62 66), A440 equal temperament.
- Tonal SFX already sit in D (BRIEF §6.11):
  - `backup_beep` at D7 2349.3 Hz.
  - The end-card `glass_tap` can be pitched to D6 1174.7 Hz (optional).
  - The mains hum is 100 Hz (G2 +35 c), not tuned to the key. It never plays with the harmonium: the harmonium plays
    from 26.667 to 28.554 s, and the mains bed plays at 0-0.467 s and 29.4-34.667 s.

## Music map (90 BPM, beat = 20 f = 0.667 s, bar = 80 f = 2.667 s, 13 bars)
| section | bars | t0-t1 s | edit events (BRIEF §6.1) | music events |
|---|---|---|---|---|
| hook | 0 | 0.000-2.667 | A blackout / B torch-lit; beeps f40, f60; splice f80 | none (mains hum → silence → crickets are SFX) |
| candle, rooftops | 1-2 | 2.667-8.000 | candle, pankhi, homework; tilt f140-f159; rooftops | none |
| re-hook 1 | 3 | 8.000-10.667 | power back f240, AA GAYI!, cheer; dies again f300 | none (appliance chorus) |
| old room | 4 | 10.667-13.333 | L7 torch beam f320 | none |
| edit desk | 5 | 13.333-16.000 | lights on f400, render 63 % | none |
| re-hook 2 | 6 | 16.000-18.667 | power dies mid-render f480 | none |
| keycaps | 7-8 | 18.667-24.000 | L8 iris f560; Ctrl+S on quarters, 8ths from f640 | none (keycap thocks are the percussion) |
| candle, JD profile | 9 | 24.000-26.667 | candle macro, JD profile; **drop-out f790-f799** | none; music is digital silence through the drop-out |
| **payoff** | 10 | 26.667-29.333 | `BIJLI NE SIKHAAYA / sabr`; "sabr" onset f820 | **harmonium swell: starts f800 (beat 40, bar-10 downbeat), peaks f820 (beat 41), tail out by 28.554 s (f856.6)** |
| power returns | 11 | 29.333-32.000 | f880 loudest (L4); end card f920 | none (riser, chorus, cheer are SFX) |
| end card | 12 | 32.000-34.667 | hold; loop into f0 at f1040 | none: the seam is silent in this layer; the SFX mains bed carries the loop |

**Harmonium cue (exact):** `harmonium_swell(duration=20/30/0.72 = 0.925926 s, notes=(50, 57, 62, 66), seed=0)`. The
BRIEF writes 0.926; the exact value puts the start on sample 1,280,000 (f800) and the peak on sample 1,312,000 (f820). The
sound-designer's cue sheet uses 0.926 and starts 0.05 ms earlier, which makes no measurable difference. The sound is
1.887 s long (swell 0.667 s, release, room tail).

## Verification (from `music_full.verify.json`)
| check | result |
|---|---|
| format (ffprobe) | pcm_s24le, 48,000 Hz, 2 ch, duration_ts 1,664,000 (34.666667 s) |
| loudness (ffmpeg ebur128) | I **-16.0 LUFS**, true peak **-5.0 dBFS**. Toolkit: -16.000 LUFS, -5.016 dBTP, max momentary -12.59 LUFS. The gated integrated value is the sting's own loudness. LRA 13.4 LU only describes one 1.9 s swell in silence; the 5-9 LU spec is for the final mixes |
| drop-out f790-f799 | **digital silence** (every sample 0). All samples before f800 are 0 |
| start | first non-zero int24 sample 1,280,009 = f800 + 0.19 ms (the swell rises from zero). -40 dB point 26.702 s (f801.0), -20 dB point 26.796 s (f803.9) |
| peak | 10 ms RMS envelope maximum **27.3343 s = f820.03 = beat 41.001**, +0.96 ms from f820. 400 ms momentary maximum centred at 27.31 s |
| onsets (spectral flux, blind) | 26.909 / 27.121 / 27.226 / **27.356 s** (strongest, f820.7). These are soft onsets from the rising swell and the 0.9 Hz bellows pumping. The swell has no hard attack; nothing fires before f800 |
| tempo | **Cannot be estimated from this file, by design:** the layer is one sustained event. Measured instead: start on beat 40.000, peak on beat 41.001 of the 90-BPM grid. The grid itself is checked in run 2 on the SFX stem (`grid`, below) |
| pitch (power centroid, +-20 c) | in the chord: D3 +0.13 c, A3 -0.12 c, D4 +2.89 c, F#4 +0.07 c. Solo renders: +0.13 / +0.01 / -0.89 / +0.11 c. D4's +2.9 c in the chord comes from D3's 2nd harmonic, which sits on D4's two reed frequencies; it lies inside the +-2.5 c reed spread. Pitch classes: D 0.45, F# 0.25, A 0.22 (chord tones **0.92**), then E 0.04 (the 9th harmonic of D) |
| band energy over the sting | < 120 Hz 0.0000 (about -61 dB) · 120-250 Hz 0.37 · 250 Hz-1 kHz 0.54 · 1-4 kHz 0.088 · > 4 kHz 0.003. No sub build-up, and little energy in the speech band |
| loop seam | first 0.5 s and last 0.5 s are digital silence; the layer is silent from 28.553 s to DUR, so there is no fade and no tail across the seam |
| determinism | 0 differing samples in a fresh re-render; stems sum to the mix with difference 0 |

**Spectrogram (viewed):** `music_full_spectrogram.png` is black for bars 0-9 and 11-12. The one event sits at bar 10. Its
left edge is exactly on the f800 line, where the blue drop-out band ends. `music_zoom_payoff.png` shows:
- The drop-out band (f790-f799) is empty.
- The swell fades in from f800 and the waveform is widest on the f820 line.
- There is a steady harmonic stack: D3 147 Hz is the brightest line, with A3, F#4 and D4 above it and harmonics up to
  about 3 kHz. Above 3.2 kHz the stack rolls off (the 3.2 kHz low-pass).
- A faint reed-air haze runs up to about 10 kHz. Below 100 Hz there is only a -60 dB-or-lower wash.
- Nothing remains after about 28.55 s, so the layer is clear of the f880 power return by 0.78 s.

## Hand-off notes
- **Sound-designer:**
  - Keep tonal SFX in D (see Key).
  - Use **one harmonium source only**. Either:
    - mix FULL = VO + SFX stem *without* the harmonium + `music_full.wav`, or
    - the SFX stem *with* the harmonium cue, and no music layer.
  - Never use both, or the harmonium doubles (+6 dB, phase-locked).
  - Mix DRY never has the harmonium.
- **Run 2, final mixes A FULL, A DRY and B FULL** (BRIEF §6.11 names: `RWS/audio/bijli_chali_gayi_mix_A_full.wav`,
  `_mix_A_dry.wav`, `_mix_B_full.wav`):
  - Bring the harmonium in as one static gain, with no VO sidechain. A duck would flatten the designed peak on "sabr"
    (V11 starts at 27.30 s and runs to 28.05 s, right over the peak). Set the gain so that speech is >= 8 LU above
    harmonium + SFX over V11's voiced frames.
  - The harmonium carries only 8.8 % of its energy in 1-4 kHz, so no VO-pocket EQ is needed.
  - Then check: -14 LUFS +-0.5, TP <= -2.0 dBTP, drop-out RMS f791-f798 <= -45 dBFS, harmonium peak f820 +-1 in the
    mix.
  - Check the grid with `bijli_chali_gayi_music.py grid <SFX stem or mix>`. The default window is bars 7-8 (keycaps).
    Pass: tempo within 0.2 BPM of 90, phase within +-15 ms.
  - The fit subtracts its own method bias, measured on a click track that is exactly on the grid (-12.7 ms for this
    window). On synthetic keycap stand-ins it read -2.0 ms for exactly-on-grid clicks and +8.0 ms for clicks 10 ms late,
    at 90.000 BPM.
- **Edit:** no off-grid cuts to report. The only music event sits on f800 and f820, both on the beat grid.

## Open questions
- The workflow task asked for an "original music bed via `epic_music.py`" with -16 LUFS stems. That conflicts with the
  binding SLATE §3.2 / BRIEF §6.11 / QA §8 ("no music bed"), so the delivered music layer is the harmonium only. If the
  lead wants a bed after all, it is a SLATE change, and the creative director must re-issue §6.11 and §8 first.
