# reel2 "Blink": music map

- **Source:** a procedural score synthesised in numpy by `reel2_music.py` with the toolkit's audio.py helpers. There is no library track and no AI music tool, so nothing needs a licence or an archive. The wav is rebuilt from code: `nice -n 10 python3 reel2_music.py`.
- **Tempo:** 120 BPM, the edit's grid. A beat is 0.5 s and a bar (4 beats) is 2.0 s, with beat n at n x 0.5 s. Measured on `reel2_music.wav`: 120.00 BPM, beat phase -0.010 s.
- **Key:** D minor (Aeolian). The end card cadences into the relative major: Bb (lift) -> C7sus (build) -> F add9 (end card).
  - Bass roots are D2 73 Hz, Bb1 58 Hz and F1 44 Hz, below a male VO fundamental.
  - Pads are low-passed to 2.2 kHz or less. Under the VO the mix ducks the music 6 dB and dips its 2-5 kHz band by a further 6 dB.
  - There is no melodic line. Harmony comes from pads, the clock motif and percussion.
- **Tonal SFX** are pitched into the key (see `reel2_sfx.py`):
  - glass_tap: C7, D7 and A6.
  - check_ding: F6 then C7.
  - toast_chime: G5 then D6.
  - logo_sting: an F5 bell, the root of the final F add9.

| section | bars (beats) | t0-t1 s | edit events | music events |
|---|---|---|---|---|
| Hook | 1 (b0-2) | 0.00-0.94 | "Blink." in focus, lids close 0.62-0.94 | Open-fifth D/A drone (LP 420 Hz). Clock tick-tock on beats 0.0 and 0.5. The SFX heartbeat (0.02, 0.52) is the low pulse here. |
| Blink gap | (b2) | 0.94-1.04 | lids shut, flare on the seam 0.98 | Near-silence: the whole score is down 42 dB, so only the SFX flash_hit is heard. |
| Hook 2 | 1-2 (b2-6) | 1.04-3.00 | price 67,420 ▲, "already *moved*" | Dm pad swells back in. Clock ticks on 8ths from 1.5. Low D1 pulses at 1.5, 2.0, 2.5 and 2.75. A noise swell and the pad filter (450 Hz -> 2.3 kHz) build 2.0-2.94, followed by a 55 ms suck-out. |
| **HIT** | bar 2 line (b6) | 3.00 | cut B, candles whip past | D1 sub boom (_thump) plus a Dm braam whose filter sweeps 2.4 kHz -> 350 Hz, plus a low noise burst and hall reverb. |
| Post-hit | 2-3 (b6-11) | 3.00-5.50 | "Every *millisecond* counts." | Dm pad (LP 700 Hz). Clock ticks on 8ths. Sub pulses at 4.0 and 5.0. A hi-passed swell 4.75-5.5 leads into the drive. |
| Drive | 3-6 (b11-23) | 5.50-11.50 | trade window, chips 6.50/8.45, BUY 9.50, toast 9.75, MT5 10.10 | Kick on every beat. 16th bass ostinato pumped by the kick. Clock ticks become the 16th hats, with an open hat on the off-8ths. Harmony: Dm9 (5.5-8.0), Bbmaj7 (8.0-10.0), Gm9 (10.0-11.5). |
| Cut D | (b23-24) | 11.50-12.10 | line chart starts, "Eliminate" | Drums drop out. The Gm9 pad darkens (LP 600 Hz) over a G1 hold. The SFX reverse_swell carries the run-up. |
| **LIFT** | 6-7 (b24-27) | 12.10-13.50 | "*lag.*" slam 12.10, light sweep, "Seize..." 13.00 | Bb1 tom/sub hit plus a short Bb braam. The Bbmaj9 pad opens bright (LP 1.6 kHz), an air layer opens and the clock ticks on 8ths. A half-time kick lands at 13.0. |
| Build | (b27-29) | 13.50-14.50 | "...market opportunity", whip 14.30-14.70 | C7sus pad with its filter opening (1.0 -> 2.8 kHz) and level rising. Snare roll in 8ths, then 16ths, then 32nds, with a crescendo. Pulsing C2 bass in 16ths and a rising noise swell, followed by a 50 ms suck-out before 14.50. |
| **Resolve** | bar 7 (b29) | 14.50 | whip peak, logo_sting 14.62 | The F add9 chord (F2 C3 G3 A3 C4) lands, with a soft F1 sub thump. |
| Logo bloom | (b31-33) | 15.80-16.30 | mark glides 15.45-16.00, logo_full 15.95-16.25 | The pad blooms (+3 dB, filter 800 Hz -> 1.7 kHz) and a glassy F5/C6/G5 top fades in from 15.9. |
| Tail | 8-10 (b33-43) | 16.30-21.50 | settled end card, VO ends 17.66 | F add9 sustains, darkening, and eases down from 17.2. Cos² fade 18.80-21.35, so the music is silent by 21.35. DUR is 21.5. |

## Mix (`reel2_music.py` build_mix)

- **Inputs:** VO `reel2_vo.wav`, placed in edit time and normalised to -15 LUFS on the bus. SFX `reel2_sfx_stem.wav` at -18 LUFS. Music at -17 LUFS before the duck.
- **Ducking:**
  - The music ducks 3 dB under SFX hero hits (attack 10 ms, release 250 ms).
  - Under the VO the music ducks 6 dB broadband with a smooth 60 ms attack and 450 ms release.
  - On the same envelope, a zero-phase 2-5 kHz band cut of up to 6 dB keeps the music out of the consonant band.
- **Master:** the bus is gained to -14 LUFS through a true-peak limiter at -2.3 dB, with a 10 ms end fade. Output is 48 kHz, 24-bit and exactly 21.5 s (1,032,000 samples).
- **Measured (pyloudnorm, 4x-oversampled TP):**
  - mix: -14.06 LUFS and -2.30 dBTP. ffmpeg ebur128 reads I -14.0 and LRA 6.3.
  - Music under the VO: 8.5 LU (median short-term).
  - VO over music: 11.4 dB broadband and 27 dB in 2-5 kHz (median; 10th percentile 12.6 dB).
- **Render:** `--audio /home/claude/100/workspace_oktrum/audio/reel2_mix.wav`
