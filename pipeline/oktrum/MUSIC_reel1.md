# reel1 "Every market": music map

- **Source:** a procedural score synthesised in numpy by `reel1_music.py` with the toolkit's audio.py helpers. There is no library track and no AI music tool, so nothing needs a licence or an archive. The wav is rebuilt from code: `nice -n 10 python3 reel1_music.py`.
- **Style:** neon four-on-the-floor electro / synthwave, deliberately unlike reel2's cinematic clock score. It has kick-pumped supersaw pads, an off-beat saw bass, claps on 2 and 4, off-beat open hats and a 16th pluck arp under the market list.
- **Tempo:** 124 BPM, the edit's grid. A beat is 0.4839 s and a bar is 1.935 s. Measured on `reel1_music.wav`: 124.00 BPM, beat phase -0.009 s, on-grid onset strength x3.7.
- **Key:** F minor (Aeolian). The loop is Fm7 | Dbmaj7 | Ab | Eb, with an Eb sus build that resolves to Ab add9, the relative major, on the end card.
  - Bass roots run F1-Eb2 (44-78 Hz), below the male VO.
  - Pads are low-passed to 2.4 kHz or less.
- **Tonal SFX** are pitched into the key (see `reel1_sfx.py`):
  - glass_tap chips: Ab6, Bb6, C7, Eb7 and F7.
  - coin_ring: F7.
  - check_ding: Eb6 then Bb6.
  - logo_sting: Eb5, the fifth of Ab add9.

| section | bars (beats) | t0-t1 s | edit events | music events |
|---|---|---|---|---|
| Hook | 0-1 (b0-8) | 0.00-3.87 | word slams Forex 0.26, Gold 1.19, Bitcoin 2.10, Nvidia 3.17; whips on beats 2/4/6/8 | Filtered F pulse in 8ths, opening 350 Hz -> 1.6 kHz. Half-time kicks on beats 0/2/4/6, off-beat hats. A 16th snare roll and noise riser run over b6-8, then a 45 ms suck-out. |
| **DROP** | bar 2 line (b8) | 3.871 | whip into the globe, sphere assembles | Full groove: F1 boom, crash, 4/4 kick, clap, hats, off-beat bass and pumped Fm7 supersaw. |
| Markets | 3-4 (b12-20) | 5.81-9.68 | chips 6.12-8.33, zoom-through 8.78 | Dbmaj7, then Ab. A 16th pluck arp on the chord tones runs 5.81-10.20. |
| MT5 / tunnel | 5 (b20-24) | 9.68-11.61 | "Powered by MT5", tunnel 10.20, counter 11.00-11.71 | Eb. The arp stops at the cut at 10.20. |
| Fill | 6 (b24-26) | 11.61-12.58 | counter lands 11.71, whip down 12.52 | Fm7. Snare 8ths, then 16ths, plus a hi-passed swell. The kick keeps going. |
| Re-hit | (b26) | 12.58 | inside the whip down, 0.11 s before the "0%" slam at 12.69 | Crash. The groove continues on Fm7 under "Zero hidden fees". |
| Globe return | 7 (b28-32) | 13.55-15.48 | globe 14.03, Oktrum 14.24, "Trade the global markets" | Dbmaj7, with a crash at 13.55. The arp returns from 14.03. |
| Build | (b32-35) | 15.48-16.94 | "...with precision", light sweep 16.40, type exits at 16.80 | The kick drops out. The Eb sus pad opens (700 Hz -> 2.9 kHz) and rises in level. A snare roll goes 8ths -> 16ths -> 32nds over a riser, followed by a 40 ms suck-out. |
| **Resolve** | (b35) | 16.935 | mark resolves 16.95, logo_sting 17.05, CTA 17.24, press 17.68 | Ab add9 (Ab2 Eb3 Bb3 C4 Eb4) with an Ab1 boom and a long crash. A slow 8th sparkle arp runs until 19.0. |
| Tail | (b35-45) | 16.94-22.00 | settled end card, VO ends 18.51 | Ab add9 darkens (2.0 -> 0.9 kHz). Cos² fade 19.40-21.85, so the music is silent by 21.85. DUR is 22.0. |

Off-grid edit points are pinned to the VO and left as they are. The music hits the nearest beat instead: the "0%" slam (12.69) gets the crash on b26 (12.58), and the end card (16.80) gets the resolve on b35 (16.935).

## Mix (`reel1_music.py` build_mix, the same law as reel2)

- **Inputs:** VO `reel1_vo.wav` at -15 LUFS on the bus. SFX `reel1_sfx_stem.wav` at -18 LUFS. Music at -17 LUFS before the duck.
- **Ducking:**
  - The music ducks 3 dB under SFX hits (attack 10 ms, release 250 ms).
  - Under the VO it ducks 6 dB broadband (attack 60 ms, release 450 ms).
  - A further zero-phase 2-5 kHz cut of up to 6 dB keeps the music out of the consonant band.
- **Master:** a true-peak limiter at -2.3 dB, gained to -14 LUFS, with a 10 ms end fade. Output is 48 kHz, 24-bit and exactly 22.0 s (1,056,000 samples).
- **Measured (pyloudnorm, 4x-oversampled TP):**
  - mix: -14.05 LUFS and -2.30 dBTP. ffmpeg ebur128 reads I -14.0, LRA 3.6 and peak -2.3.
  - Music under the VO: 8.0 LU (median short-term).
  - VO over music: 9.8 dB broadband and 25.7 dB in 2-5 kHz (median; 10th percentile 10.6 dB).
- **Render:** `--audio /home/claude/100/workspace_oktrum/audio/reel1_mix.wav`
