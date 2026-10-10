# reel3 "Peace of mind": music map

- **Source:** a procedural score synthesised in numpy by `reel3_music.py`. Its synth helpers and the mix law are shared with `reel1_music.py`. There is no library track and no AI music tool, so nothing needs a licence or an archive. The wav is rebuilt from code: `nice -n 10 python3 reel3_music.py`.
- **Style:** airy 2-step / future garage, calm and trustworthy, unlike reel1's 4/4 electro and reel2's cinematic clock.
  - Drums: a soft kick on 1 and the "and" of 3, a rimshot on 2 and 4, and swung 16th hats.
  - Tone: a warm sine sub, detuned pads, an FM e-piano / bell arp and a long hall.
- **Tempo:** 110 BPM, the edit's grid. A beat is 0.5455 s and a bar is 2.182 s. Measured on `reel3_music.wav`: 110.00 BPM, beat phase -0.010 s, onset strength x2.9.
- **Key:** D major.
  - The hook sits on Bm7 (vi), with a dark drop on "crashes".
  - It then goes Gmaj7 -> A sus -> a Dmaj9 bloom on "zero", then a Dmaj9 | Bm9 | Gmaj9 groove.
  - The build is on A sus, resolving to Dmaj9 on the end card.
  - Sub roots run G1-D2 (49-73 Hz). Pads are low-passed to 2.2 kHz or less.
- **Tonal SFX** are pitched into the key (see `reel3_sfx.py`):
  - glass_tap: D7 on "zero" and A6 on the PCI badge.
  - logo_sting: D5, the root of the Dmaj9 resolve.

| section | bars (beats) | t0-t1 s | edit events | music events |
|---|---|---|---|---|
| Hook | 0 (b0-2.6) | 0.00-1.40 | falling red candle, "What if the market" | Airy Bm7 pad (1.5 kHz, closing) with e-piano notes F#5, A5 and D5 on b0-2. |
| Crash | (b2.6-4) | 1.40-2.18 | candle punches through on "crashes" (VO-pinned 1.40), balance plunges | The pad is cut. A dark B1/F#2/B2 drone (LP 320 Hz) and a B1 sub take over; the SFX impact and downlifter carry the hit. |
| Light returns | 1 (b4-8) | 2.18-4.36 | "With Oktrum," 2.66, the camera follows the counter down | Gmaj7 pad fades in, with a quiet 8th e-piano arp from b5 (2.73). |
| Lift to zero | 2 (b8-9.6) | 4.36-5.26 | "...never go below *zero*", counter stops at 5.26 | The A sus pad rises (1.3 -> 2.2 kHz) and a soft swell ends on "zero". |
| **Zero** | (b9.6) | 5.26 | shield slams, counter 0.00 (VO-pinned) | The Dmaj9 pad blooms with a D1 sub swell; the padlock click follows at 5.65. |
| Journey | 2-4 (b10-20) | 5.45-10.91 | shield + light trail, cards at 6.32, 8.40 and 9.90, PCI badge 10.55 | The 2-step groove starts on b10. Chords: Dmaj9, then Bm9 (6.55), then Gmaj9 (8.73), with the e-piano arp in 8ths. |
| **Lift** | bar 5 line (b20) | 10.909 | gather 11.12, "peace of mind" 11.98 | Dmaj9, brighter (2 kHz, 5 voices). A soft crash, louder hats with off-beat open hats, a bigger sub. |
| Plate | 6 (b24-26) | 13.09-14.18 | navy plate grows 13.01, "Trade With" 13.88 | Gmaj9 groove. |
| Build | (b26-28) | 14.18-15.27 | "Confidence" 14.33, plate full 15.15 | The kick drops out. A sus opens (1.3 -> 2.6 kHz). A rim roll goes from 8ths to 16ths over a swell, followed by a 30 ms suck-out. |
| **Resolve** | bar 7 line (b28) | 15.273 | CTA 15.30, logo_full 15.55, press 15.82 | Dmaj9 with a D1 boom, a long soft crash, and e-piano bells (D6 A5 E6 C#6 A5 D6) over b28-35. |
| Tail | (b28-39) | 15.27-21.50 | settled end card, VO ends 17.16 | The Dmaj9 darkens (1.9 -> 0.9 kHz). Cos² fade 18.80-21.35, so the music is silent by 21.35. DUR is 21.5. |

## Mix (`reel1_music.build_mix`, the same law as reel1/reel2)

- **Inputs:** VO at -15 LUFS on the bus, SFX stem at -18 LUFS, music at -17 LUFS before the duck.
- **Ducking:** 3 dB under SFX hits. Under the VO, 6 dB broadband plus up to 6 dB more in 2-5 kHz.
- **Master:** a -2.3 dB true-peak limiter, gained to -14 LUFS. Output is 48 kHz, 24-bit and exactly 21.5 s (1,032,000 samples).
- **Measured:**
  - mix: -14.07 LUFS and -2.30 dBTP. ffmpeg ebur128 reads I -14.0 and LRA 8.9.
  - Music under the VO: 9.0 LU.
  - VO over music: 11.1 dB broadband and 21.1 dB in 2-5 kHz (median; 10th percentile 7.8 dB).
- **Render:** `--audio /home/claude/100/workspace_oktrum/audio/reel3_mix.wav`
