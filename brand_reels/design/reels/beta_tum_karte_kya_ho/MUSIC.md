# MUSIC · Reel 4 · C02 "Beta, tum karte kya ho?" (`beta_tum_karte_kya_ho`)

Date 2026-10-08 · Owner: music-supervisor (run 1: map, key, source, bed) · Plan: `BRIEF.md` §6.13 (binding), SLATE §3.4 + §5.

## 1. Source and licence

| item | value |
|---|---|
| source | **procedural score, original**: `pipeline/jawad_reels/beta_tum_karte_kya_ho_music.py` (numpy/scipy). Uses the in-repo `epic_music` building blocks (`EM.epiano`, `EM.kick`, `EM.clap`, `EM.bass808`, `EM.KAHARWA`), `epic_sfx.tabla_hit` (synthesised, Sa = D4), `epic_sfx.tape_stop_fx` and the toolkit's crackle grains |
| licence | original work made for @jawad_mp4; no sample of any song, no trending or copyrighted material, no stock loop, no AI model (ACE-Step not used: the procedural bed meets the brief) |
| AI disclosure | the bed is **not** AI-generated audio (the reel's AI label is still ON for the voice, per the brief) |
| regenerate | `cd pipeline/jawad_reels && tools/heavy.sh python3 beta_tum_karte_kya_ho_music.py` (build + verify, under a minute). Deterministic: two separate builds gave bit-identical files |
| music_full.wav sha256 | `15eb36304138cfb00cf9384b00815e1bbbec8a26bcb603dd2efd27dba1a56c67` |

Files (`workspace/jawad_reels/beta_tum_karte_kya_ho/music/`):
- `music_full.wav`: 48 kHz, 24-bit, stereo, 1,747,200 samples = 36.400 s.
- `stems/music_stem_{tabla,kit,bass,keys,pad,fx}.wav`: same format. kit = kick + clap, bass = 808, keys = EP,
  fx = vinyl crackle. They sum to the mix (residual -132.5 dBFS).
- `music_full.json`: score (189 events with time, frame, bar.beat, stem, gain), section map and bus numbers.
- `music_full.verify.json`: every measurement below.
- `music_full_spectrogram.png`, `music_full_zooms.png`: the spectrograms, viewed.

## 2. Key, tempo, grid

- **Key D minor, Sa = D** (tabla tuned to D4). The progression is i9, VImaj7, iv9, V7b9 (Dm9, Bbmaj7, Gm9, A7b9).
  The payoff is a Picardy **D major add9**.
- **85.714 BPM** (600/7). One beat = 0.7 s = 21 frames; one bar = 2.8 s = 84 frames. 13 bars = 36.4 s.
- Off-8ths swing by 0.06 beat (42 ms late, the epic_music lofi value). Every beat and bar line is exact.
- Chord voicings (EP left-hand root | right hand; the top line runs E4 D4 D4 E4 into E4):
  - Dm9: D3 | F3 A3 C4 E4
  - Bbmaj7: Bb2 | F3 A3 D4
  - Gm9: G2 | F3 A3 Bb3 D4
  - A7b9: A2 | G3 Bb3 C#4 E4
  - D add9 (brief voicing): D2 | D3 F#3 A3 E4
  - The shared `EM.style_lofi_desi` table voices "Bbmaj7" as Bb D F A C# (a #9, not a maj7). It is not used here.
- **For the sound designer (tonal SFX):** the chords per bar are in §3.
  - These pitches assume the brief's mapping (pitch 1.1225 = A6, so pitch 1.0 = G6).
  - Of the BRIEF §6.12 cues with a stated pitch, every one lands on a chord tone of its bar except two: the
    `notif_ping` D7 (pitch 1.4983) pings at **18.9 s and 19.433 s**. They fall in bar 6's **A7b9** half (18.2-19.6),
    where D7 is a sus4 clash.
  - Suggestion for those two: C#7 (pitch 1.4142, the leading tone that resolves up to D on the 19.6 flood downbeat),
    or A6 (1.1225) or E7 (1.6818).
  - The pitched cues that fit: notif_ping A6 / D7, `pop` pitch_to(880) = A5, and the payoff `tabla_hit` 'dha' at
    pitch 1.0 = D4 over D add9.
  - Tabla strokes stay on Sa = D in the bed and in the SFX alike, also over A7b9 (the 8.4 'ta'). That is idiomatic
    tabla.
  - `bubble_pop` and `glass_tap` have no pitch in the brief: tune them to a chord tone of their bar.

## 3. Music map (beat table; t = bar x 2.8 + beat x 0.7, frames = t x 30)

| section | bars | t0-t1 s | frames | edit events (BRIEF §6.2) | music events |
|---|---|---|---|---|---|
| hook | 0 | 0.0-2.8 | 0-83 | f0 JD confused + Mummy pill; message lands 0.367 (notif A6); halo flare 1.4; splice f84 | **frame 0 = EP Dm9 + tabla 'dha'** (strum up from D3 at exactly 0.000); kaharwa theka on 8ths; **'dha' accent on beat 2 (1.4 s)** for the keyword flare; no kick |
| comedy groove | 1-3 | 2.8-11.2 | 84-335 | translate card 2.8; "Shaadi wala?" 4.2; M6 4.9; "Cartoon?" 7.0; punch-in 7.7; **stamp SLAM 8.4 (bar 3)** | Bbmaj7, Gm9, A7b9; theka + **soft kick** on beat 0 and the swung 2.5 (lp 1800, 4 dB under the flood kick); EP upper-voice stab on the swung 2.5; no clap, no 808. **The theka rests at 7.7** (bar 2's 'dhin'), so the punch-in's SFX tabla 'ge' owns the instant and the same Sa-tuned stroke does not stack on it |
| groove into the killer | 4 | 11.2-12.6 | 336-377 | **M3 re-hook 11.2 (bar 4)**; loading dots 12.13 | Dm9 + theka + soft kick on beat 0; **tape stop 12.15 -> 12.6** (`tape_stop_fx`, 0.45 s; pitch and speed to 0, highs closing). The theka's last stroke is the 'tin' at 12.292, inside the stop |
| silence | - | 12.6-14.0 | 378-419 | **KILLER 12.6** "Achha. Naukri kab lagegi?"; card folds | **digital silence** (room tone comes from the SFX bed) |
| sad-comic | 5-6 | 14.0-19.6 | 420-587 | cut to neutral 14.0; time skip + buzz 16.8; pings 18.2-19.43 | EP only, lp 1500 Hz, 6 dB under the groove EP: Bbmaj7 (bar 5), Gm9 for 2 beats + A7b9 for 2 beats (bar 6). **One tabla 'tin' at 16.8** (bar 6 downbeat, with the buzz) |
| the group floods | 7-9 | 19.6-27.3 | 588-818 | **M2 re-hook 2 at 19.6 (bar 7)**; reel forwarded 21.7; Kamaal 22.4; Wah 23.1; Mummy typing 25.2 | Dm9, Bbmaj7, Gm9. **Full groove:** tabla + kick (beat 0 and the swung 2.5) + clap (beats 1 and 3) + 808 root (D2, Bb1, G1; ducked 6 dB under the kick) + EP + stab |
| drop-out | - | 27.3-28.0 | 819-839 | held breath 27.3 (ui_tick) | **gate after the reverbs, 4 ms edge**: digital silence for exactly 1 beat. The 808 and the reverb tails are cut ("the suck"). No clap at 27.3 |
| PAYOFF | 10 | 28.0-30.8 | 840-923 | **M1 payoff 28.0 (bar 10)**; P1 lockup; hand-on-chest 28.7 | **one warm chord: D add9**. EP (D2 / D3 F#3 A3 E4) + warm saw pad (D3 F#3 A3 D4 E4, lp 1400, 60 ms attack, sinking about 8 dB over the bar), struck at 28.000. **Tabla re-enters 6 dB down at 29.4.** No kick, no 808 (the SFX sub_drop owns the low end) |
| end card | 11 | 30.8-33.6 | 924-1007 | lockup exits 31.8; **EndCard t0 = 32.2** | Bbmaj7 EP (1.5 dB softer) + theka 3 dB down; no kick |
| loop bar | 12 | 33.6-36.4 | 1008-1091 | end card settled 34.03; Nani pill 35.7; exit into the loop push | A7b9 EP + theka for beats 0-1.5, then **thins**: the dominant is re-struck softly at 35.0, and **one 'tin' at 35.7**. V7b9 resolves into bar 0's Dm9 on the loop. Overhang past 36.4 is folded onto the head (circular); no fade |

Interpretations of the brief (stated so the timeline and the sound designer read them the same way):
- "kick on 1 and 2.5" = beat offsets 0 and 2.5 from the bar line. That is epic_music's lofi pattern; the 2.5 swings
  like every off-8th, at 1.792 s into the bar.
- "tabla re-enters -6 dB" = the theka's strong strokes at -6 dB and its weak strokes at -9 dB, keeping the theka's
  3 dB accent.
- The EP stabs, the soft turnaround re-strike at 35.0, the bar-0 accent and the 7.7 rest are comping choices inside
  the brief's layers. They add no new instrument and no second desi voice.

## 4. Levels and bus

- Bed delivered at **-16.0 LUFS integrated** with a true peak of **-3.3 dBTP**, as the task asked.
  - BRIEF §6.13 asks for the stem at -18 LUFS when VO is present. `epic_mix.mix_reel` re-levels the bed to -18 LUFS
    under VO anyway, so either level works.
  - The limiter ceiling of -3.3 dBFS meets both "<= -3 dBTP" (brief) and "<= -2 dBTP" (task).
- Chain, in order:
  1. Tabla slap tamer.
  2. Keys, pad and crackle sidechained 4 dB to the kick (5 ms / 160 ms). The 808 is sidechained 6 dB.
  3. 'studio' reverb at -18 dB, per stem.
  4. 24 Hz subsonic high-pass.
  5. Section groups: tape stop on bars 0-4, drop-out gate on bars 5-9, circular fold on bars 10-12.
  6. Loop-safe level rider (amount 0.3, `EM.level_rider` with wrap-around windows).
  7. epic_mix's 2:1 glue.
  8. 4x true-peak limiter.
- Measured on the bus:
  - limiter: at most 1.03 dB of gain reduction, and only 0.29 s in total above 0.5 dB;
  - glue: at most 3.0 dB;
  - rider x glue: -3.7 to +4.5 dB;
  - tabla tamer: at most 2.4 dB;
  - DC: 4e-5;
  - energy below 20 Hz: -54.6 dBFS RMS.
- Max momentary loudness per section (music alone, 400 ms windows lying inside each span):

  | span | max LUFS | window centre (s) |
  |---|---|---|
  | hook 0-2.8 | -13.44 | 0.22 |
  | comedy 2.8-12.15 | -13.89 | 8.6 |
  | sad 14.0-19.6 | -16.12 | 17.0 |
  | flood 19.6-27.3 | -13.24 | 19.8 |
  | **payoff 28.0-28.4** | **-11.81** | **28.24** |
  | end card 30.8-33.6 | -14.71 | 31.01 |
  | loop bar 33.6-36.4 | -13.66 | 33.82 |

  The payoff is the loudest moment of the bed, 1.4 LU over the flood groove. The loop bar is within 0.2 LU of the
  hook, so the level does not jump at the loop.
- LRA is 6.5 LU. It comes from the planned dynamics: the sad-comic bars sit 6 dB down and there are two silences.

## 5. Verification (measured; `music_full.verify.json`)

| check | result |
|---|---|
| format (ffprobe) | pcm_s24le, 48,000 Hz, 2 ch, 1,747,200 samples = 36.400000 s ✓ |
| loudness | python BS.1770: **-16.00 LUFS**, **-3.30 dBTP**, LRA 6.47 · ffmpeg ebur128: **I -16.0 LUFS, LRA 6.5, true peak -3.3 dBFS** ✓ |
| stems | 6 stems, same format; their sum equals the mix (residual -132.5 dBFS) ✓ |
| silence after the killer | 12.62-13.98: peak and RMS **-240 dBFS** (digital zero). The exact 12.600-14.000 window is also zero ✓ |
| drop-out | 27.31-27.99: **-240 dBFS** (digital zero). The exact 27.300-28.000 window is also zero ✓ |
| tape stop | RMS at 12.10 s is -16.8 dBFS and at 12.62 s -73.7 dBFS: a **56.9 dB** drop (brief: >= 30) ✓ |
| tempo / phase, blind (EM.beatgrid, as the brief names it) | 85.71 BPM, phase -10 ms, strength x3.6. The same function on an exact click grid at the same beats reads -15 ms, so its STFT bias corrected phase is **+5 ms** (5 ms search steps) ✓ |
| tempo / phase, blind fine fit (same spectral flux at 1 ms frames, 0.5 ms phase steps) | **85.7143 BPM**, phase -4.0 ms against -7.0 ms for the click reference, so **+3.0 ms** corrected. The residual is an attack-shape bias: the 3 ms EP attack against the 1 ms click ✓ |
| **onset analysis: every scored event in its clean stem** (matched filter with the event's own waveform through the stem's linear chain, ±30 ms search) | tabla 74/74 within **±0.04 ms**, the 'ge'/'ke' bayan strokes included (the 12.292 stroke inside the tape stop is not timed) · kick + clap 18/18 at **0.000 ms** · 808 3/3 at **0.000 ms** · EP notes 92/92 via their tine band: 90 at **0.000 ms**, and 2 match exactly **one tine cycle** early (25.2 G2 -0.729 ms = 1/1,372 Hz; 28.0 D2 -0.958 ms ≈ 1/1,028 Hz), where the kick sidechain and the glue reshape the 20 ms tine; both downbeats sit at -0.042 and 0.000 ms in the mix · pad onset +0.21 ms ✓ |
| **onset analysis: every on-beat moment in the MIX** (matched filter, 1-14 kHz) | 42 beats. Line fit: **85.7143 BPM, phase -0.018 ms**, residual 0.017 ms rms. 41/42 beats are within **0.042 ms**. The 42nd (30.1 s, the soft 'dhin' re-entry under the payoff pad) is masked in the mix's high band (ncc 0.22) but sits at its exact sample in the tabla stem ✓ |
| **downbeats** (bars 0-12 in the mix) | all **13** found within **-0.042 to 0.000 ms** of 2.8 n s (ncc 0.80-0.99) ✓ |
| harmony (chroma of keys + pad per chord span) | all 14 spans: the top-3 pitch classes are chord tones, with 96-100 % of the energy on chord tones ✓. The mix adds the tabla's Sa (D) over the A7b9 bars: the drone note stays on Sa, as tabla practice does |
| loop seam | RMS of the last frame (f1091) -28.8 dBFS and of the first frame (f0) -15.0 dBFS: no gap ✓. Sample step across the seam 0.00012, below the median sample step of the last 0.1 s (0.0015). Nothing is lost past DUR + 2 s (-206 dB) |
| sub check | 20-60 Hz RMS per bar: -39 (hook), -25 (comedy, felt kick), -55/-49 (sad-comic, none), -22.5 (flood, kick + ducked 808), -38/-42/-44 (bars 10-12). No build-up, and no sub on the payoff where the SFX sub_drop sits |

**Spectrogram (viewed: `music_full_spectrogram.png` + `music_full_zooms.png`).**
- **Bars 0-4:** the tabla shows as vertical broadband strokes on every 8th, with the swung off-8ths visibly late. The
  EP chords are horizontal partials at 100-1,100 Hz. The dayan's D partials (about 294, 588, 884 and 1,179 Hz) ring as
  short lines, and the soft kick shows as low-end streaks on beat 0 and the swung 2.5. Crackle is a faint speckle at
  1.5-9 kHz.
- **Tape stop (12.15-12.6):** every partial bends downward and the top closes. It reaches black exactly at the 12.6
  beat line and stays black until the bar-5 line at 14.0.
- **Bars 5-6:** the energy sits only below about 1.5 kHz (low-passed EP) under the crackle, with no sub. The single
  'tin' shows at 16.8.
- **Bars 7-9:** the 808 roots and the kick light the band below 100 Hz. The claps are wide vertical noise bands from
  1 to 10 kHz on beats 1 and 3.
- **Drop-out (27.3-28.0):** a black column with a hard vertical edge where the gate cuts the 808 and kick tail.
- **Bar 10:** the densest harmonic stack of the reel, with the pad's saw partials up to about 3.5 kHz over the D add9
  EP. It thins visibly over the bar, and the tabla strokes return at 29.4.
- **Bars 11-12:** no low-end streaks. Bar 12 empties after its last theka stroke at 34.69, except the 35.0 re-strike
  and the 35.7 'tin'.
- **Loop seam zoom:** the waveform and the spectrum run continuously from 36.4 into the Dm9 strike at 0.0.

## 6. Hand-off to run 2 (mix, BRIEF §6.14) and to the sound designer

- Run 2: `epic_mix.mix_reel(...)` with `music=<ws>/music/music_full.wav`. It re-levels the bed to -18 LUFS and ducks
  it 3 dB under SFX and 9 dB under VO. Keep the no-music mix (VO + SFX) for the in-app song. The stems are here for
  re-balancing.
- **Watch item: "max momentary of music + SFX falls in 28.0-28.4".** This is an estimate, not a deliverable.
  - How it was made: I rendered the 55 cues of §6.12 with `A.mix` at -18 LUFS, without `fit_under_vo`. I then added
    this bed at -18 LUFS, ducked 3 dB under the SFX and 9 dB under the §6.7 VO slots.
  - With the VO ducking: the max lands at **28.21 s** (-10.08 LUFS). The 7.7 s punch-in window is 0.67 LU lower and the
    flood groove 5.6 LU lower.
  - Without the VO ducking: the max is again at 28.21 s, 4.6 LU over the groove.
  - Before the 7.7 rest, the bed's own tabla stroke at 7.7 stacked coherently on the SFX tabla 'ge'. That made the two
    windows tie within 0.2 LU.
  - The SFX stack alone still puts the 7.7 punch-in within 0.1 LU of the payoff (-10.83 against -10.76 LUFS), so the
    margin is thin. Trimming impact_soft at 7.7 from -2 to -4 dB in the SFX stem would widen it; check it in run 2.
- The sound designer's tonal cues: see §2 for the two D7 pings over A7b9.
- No timing changes are needed. Every cut in BRIEF §6.2 sits on a beat or on a quantised 8th, and the bed's bar lines
  match the grid to under 0.05 ms.
- Open licence questions: none.
