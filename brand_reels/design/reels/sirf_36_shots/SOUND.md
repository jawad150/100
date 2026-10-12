# sirf_36_shots: SOUND

This is a VO-led mix (LEAD_DECISIONS 1 and 3, the Bijli convention). The deliverables are:
- `_ig` = VO + SFX + music (mix_A);
- `_ig_songready` = VO + SFX (mix_B);
- VO, SFX and music stems.

Owners: sound-designer and music-supervisor, 2026-10-12. Every check below is a measurement or a rendered image. Nobody has listened to this mix.

## 1. Files and rebuild

| what | path |
|---|---|
| VO chain and placement | `pipeline/jawad_reels/sirf_36_shots_vo.py` (`process`, then `assemble`). It writes `workspace/jawad_reels/sirf_36_shots/vo/vo_stem.wav` + `words.json` (and the `_B` hook versions) and `brand_reels/assets/sirf_36_shots/vo_final/` (FLAC + json). The timing table is `VO_TIMING.md`. |
| music | `pipeline/jawad_reels/sirf_36_shots_music.py` (`build`, `verify`). It writes `audio/music.wav`, `audio/stems/music_{piano,bass,drums,keys,fx}.wav`, `music.json`, `music.verify.json`, `music_spectrogram.png`. |
| SFX and mixes | `pipeline/jawad_reels/sirf_36_shots_sfx.py`. The frame cue table (`CUE_TABLE`, `BED_TABLE`) is at the top of the file. `build` makes the SFX bus, the VO-floored SFX, the VO and music rides, mix_A, mix_B, the stems and the AAC check, then runs verify. Other modes: `cues`, `audition`, `verify`, `mix`. |
| outputs | `workspace/jawad_reels/sirf_36_shots/audio/`: `mix_A.wav`, `mix_B.wav`, `stems/stem_{vo,sfx,music}.wav`, `sfx.wav` (+ `sfx_fx.wav`, `sfx_bed.wav`), `sfx_vo.wav`, `music.wav`, `music_mix.wav`, `sfx_cues.json`, `mix.json`, `mix_summary.json`, `sound.verify.json`, `mix_A_overview.png`, `mix_B_overview.png`, `sfx_overview.png`, `music_spectrogram.png`, `audition/*.wav/.png` |

Rebuild (container: heavy jobs only, through `tools/heavy.sh`; on the Windows node run the same Python commands with `sys.executable` / `py -3`):

```
cd pipeline/jawad_reels
tools/heavy.sh python3 sirf_36_shots_vo.py assemble      # only if the VO placement changes (process is cached)
tools/heavy.sh python3 sirf_36_shots_music.py build      # the SFX build also rebuilds it when it is stale
tools/heavy.sh python3 sirf_36_shots_sfx.py build        # SFX, mixes, stems, AAC check, verify (exit 0 = all checks pass)
```

All three are deterministic (fixed seeds, numpy / scipy, ffmpeg only for the measurements). No new voice take, no paid service, no sample of any song.

Render the masters with `--no-sfx-build --audio workspace/jawad_reels/sirf_36_shots/audio/mix_A.wav` for `_ig`, and with `mix_B.wav` for `_ig_songready`. `BED = None` in the SFX module, so render.py never rebuilds this layer.

## 2. The VO-led grid (36.000 s = 1,080 f, 120 BPM, beat 15 f, bar 60 f, key D minor)

The picture follows the measured VO (VO_TIMING.md section 3). Sound already sits on these frames:

| event | SHOTS f | sound f | why |
|---|---|---|---|
| FLASH POP (shutter + xenon + body; music stinger) | 60 | **100** | C1 + C2 need 3.25 s. `FLASH_F = 100` in the VO module. The VO_TIMING row "f97" is the word-end rule; f100 is the frame the VO was placed around ("jao!" ends f94.5, "Har" starts f104.3). **Use f100.** |
| C1 whip up into the canister | 150 | whip peak **f166**, cut f167 | after C3 "tha." (`WHIP_F = 167`) |
| album hard cut | 420 | **405** | C9 "Phir" f405.3 |
| 4 CAMERAS slam + CAM A-D taps | 570 | **582** (+4 f each: 586 / 590 / 594) | C12 "chaar" f582.7 |
| 3,000 TAKES slam + hard cut + take counter | 600 | **615** (counter rolls f615-f659) | C13 "teen" f614.94 (moved 614 -> 615 in this pass, to match VO_TIMING) |
| toast slides up + typing dots | 795 | 782 (silent) | P "Bhai..." f782.3 owns the drop-out; no SFX |

Kept on their SHOTS frames (the VO already fits them): f0 hook, f15 detent, f240 tin land, f255 / f270 light cuts, f300 rack + flap, f375 thumb slap ("thumb" f376), f480 re-hook, f540 2 TB ("Do" f541), f660 zoom, f735 DISK FULL ("disk" f735.6), f772-f780 tape stop, f780-f809 drop-out, f810 payoff ("ek" f818.3), f900 portal, f960 outro.

**Deviation to approve (lead / motion designer):** VO_TIMING row C7 proposes "C7 caption + P1 lands" at f301. The sound keeps the prints on SHOTS frames: P1 lands f315, P2 f320 (on "aankhein" f320.8, the eyes-shut joke), P3 f330, negatives f338. Only the C7 caption should move to f301. The flap opens over f300-f315, so P1 cannot land on f301 unless the flap is cut.

## 3. Policy and design

- Bed: SFX plus an original procedural score. Every SFX cue has an on-screen cause; the full cue table is at the top of `sirf_36_shots_sfx.py`.
- **Music** (`sirf_36_shots_music.py`): felt piano, upright bass, brushed half-time kit (past, f120-f479), a cold 8th-note synth pulse with a filter that opens over 5 bars, a full kit (present, f480-f779), santoor shimmer and vinyl crackle. Chords Dm9 - Bbmaj7 - F/A - C. The payoff is a Bbmaj7(9) piano and sub swell on f810. Events:
  - f100 flash stinger;
  - **f375-f389 digital silence** (the thumb joke);
  - f750 snare-roll build;
  - f772 tape stop;
  - **f780-f809 digital silence** (drop-out);
  - f810 payoff;
  - f900 the hook motif returns soft;
  - the closer rings across the loop seam (loop-exact).

  Licence: original work for @jawad_mp4, no AI model, no samples of songs.
- **Drop-out f780-f809:** the music is digital silence and every SFX cue is gated to exact zero. Only a -50 / -51 LUFS spindle and room-tone bed stays. The client's "Bhai..." (P, voice-note EQ) is alone there.
- **Payoff f810:** `jd_stack_velvet_hit` + toast chime (both pass the gate), keeping 250 ms in the clear before "ek" f818.
- **Re-hook f480:** `s36_rehook` = whip (f479) + impact + sub drop + glitch + air zoom, bounced into one designed sound (SHOTS: five layers -> one bounce).
- **Custom sounds** are local to the SFX module. Each passes `audio.qc() == []` at its used params; the spectrograms are in `audio/audition/`. The sounds:
  - s36_wind
  - s36_flash_charge
  - s36_flash_pop
  - s36_rewind
  - s36_tin_land
  - s36_clock_tick
  - s36_paper_plap
  - s36_paper_flap
  - s36_print_slide
  - s36_sticky_peel
  - s36_hdd_spinup
  - s36_error
  - s36_rehook
  - s36_hdd (a bed: 4 spindles, seek ticks on 8ths, seamless 12 s loop)
- **Beds:**
  - `jd_room_night_home` -42 (f900 -> across the seam -> f240);
  - outdoor_birds -40 (studio by day, f240-f270);
  - room_tone -46 / -45 (darkroom, table);
  - s36_hdd -37 (edit desk, f480-f780);
  - s36_hdd -50 and room_tone -51 in the drop-out;
  - s36_hdd -43 under the payoff.

  The beds are sidechained 3 dB under the SFX.

### VO and ducking (LEAD_DECISIONS 1)

- **VO >= 8 LU over the bed on EVERY word.** This pass drops the house 7 LU tolerance for one-syllable words. The rule is applied in three places:
  - the SFX word floor (`word_floor_curve`): the SFX stays 12.5 LU under each word, with a maximum cut of 18 dB;
  - the music word top-up in `epic_mix.mix_reel` (spec `check_word_one_syllable_lu = 8`);
  - verify (`WORD_LU = 8.0`).
- **Music in the VO mixes.** The music sits 3 dB under the spec's -18 LUFS. It is ducked 9 dB under the VO (40 / 400 ms) and 1.5 dB under the SFX. The payoff band f810-f840 gets a +3 dB ride.
- **VO rides** (gentle, per line or word, 40 ms ramps in the gaps):

  | line | ride dB | why |
  |---|---|---|
  | P | +1 | keeps the payoff line on top |
  | P word 0 "Bhai..." | -3.5 (net -2.5) | alone in the drop-out |
  | C16 | -2.5 | soft closer, widens the LRA |
  | Q | -2.5 | outro question, widens the LRA |

  The VO crest cap is 10 dB over integrated.
- **Hero transients next to words.** These sit in the word gaps by design and keep their first 35 ms through the floor:
  - flash f100, between "jao!" and "Har";
  - thumb slap f375, on "thumb";
  - re-hook f480, between "sambhaali." and "Aur";
  - payoff f810, between "Bhai..." and "ek".

  `cues` lists them as fit_under_vo warnings.

## 4. Cue summary (frames at 30 fps; gains after the VO fit; full table in the module)

| frame | event | sounds |
|---|---|---|
| 1076 (wraps) - 15 | thumb wheel advances, dial lands 36 | s36_wind (5 pawl clicks + detent), impact_soft lp 900 at f0 |
| 15-98 | flash charging | s36_flash_charge (hit = ready, f98) |
| **100** | FLASH POP | camera_shutter 0, s36_flash_pop -2, jd_hit_soft -6 (+ music stinger) |
| 125-161, 146 | rewind crank, flash recharge | s36_rewind, s36_flash_charge (quiet) |
| 166 | C1 whip into the canister | whip |
| 177 / 195 / 212, 228 | canister spins, tips and falls | swish_small x3, whoosh_fast (start) |
| 240 / 255 / 270 | tin lands, DIN 2, DIN 3 safelight + envelope | s36_tin_land + impact_soft, s36_clock_tick, ui_click + s36_paper_plap |
| 300 | rack hand-off, flap opens | ui_hover, s36_paper_flap |
| 315 / 320 / 330 / 338 | P1 / P2 / P3 / negatives | s36_print_slide (seeds 0-2, 4) |
| **375** | THUMB slap (music stops f375-f389) | s36_print_slide slap, impact_soft |
| 405 / 407 / 435 | album cut, adhesive, sleeve | impact_soft, s36_sticky_peel, card_slide |
| **480** | RE-HOOK snap zoom; drives spin up | s36_rehook, s36_hdd_spinup; HDD bed starts |
| 540 | 2 TB slam, HUD, bar fills | jd_hit_soft, ui_click, bar_grow (25 f) |
| 582 / 586 / 590 / 594 | 4 CAMERAS slam, CAM A-D | jd_hit_soft, glass_tap D7 F7 A7 C8 (Dm7 in key) |
| **615** | 3,000 TAKES slam, scroll, counter | jd_hit_soft, whoosh_slow, slot_tick (23 ticks, 44 f) |
| 660 | in-scene snap zoom | whoosh_fast |
| 735 | DISK FULL | s36_error (D3 + D2 buzz), glitch_short |
| 772-780 | bin slows and freezes | jd_tape_stop, jd_riser (lands f780) |
| 780-809 | drop-out | gate: exact zero (bed at -50) |
| **810** | PAYOFF | jd_stack_velvet_hit 0, toast_chime -2 |
| 898 / 900 | C3 portal | reverse_swell, air_zoom, impact_soft |
| 963 / 997.5 / 1005 | profile outro: pill, card, question | swish_small, glass_tap, shimmer |
| 1035-1080 | loop seam | reverse_swell into f0 |

Maximum sounds on one frame: 3 (f100).

## 5. Measurements (final build, 2026-10-12)

| check | target | measured |
|---|---|---|
| mix_A (ffmpeg ebur128) | -14 LUFS ±0.5, TP ≤ -2.0 | **-14.0 LUFS, -2.3 dBTP, LRA 2.1 LU** |
| mix_B (ffmpeg ebur128) | same | **-14.0 LUFS, -2.3 dBTP, LRA 2.2 LU** |
| AAC 320 k check (ffmpeg 6.1 native aac) | TP ≤ -1.5, I ±0.5 | A: -14.0 LUFS / -2.3 dBTP; B: -14.0 LUFS / -2.3 dBTP |
| LRA (epic_mix) | 2.0–9 LU | A 2.05, B 2.19 |
| VO over the bed, per word (A) | **≥ 8 LU on every word** | 67 words: minimum 8.0, median 13.1; minimum over the music alone 9.4. One word topped up ("ek" f818, +1.5 dB extra music duck). |
| VO over the music, per line (A) | ≥ 8 LU | C1 16.6, C2 26.3, C3 13.3, C4 13.5, C6 16.0, C7 14.5, C8 15.1, C9 13.2, C10 15.9, C11 13.2, C12 14.6, C13 14.1, C14 12.0, C15 11.4, P 11.2, C16 17.9, Q 21.1 |
| VO over SFX (mix_B bed) | ≥ 8 LU per word | sfx_vo.wav keeps ≥ 12.5 LU under every word (word floor maximum cut 11.9 dB) |
| loudest moment | the payoff | A: payoff window -10.83 LUFS momentary, rest -11.17. The overall maximum, -10.62 at f843, is the payoff line "achha shot" itself, 3 f after the window. B: -11.30 against -11.23 (within the 0.2 LU rule). |
| limiter (A) | ≤ 3 dB GR outside heroes | maximum 3.16 dB for 6 ms at 20.533 s, inside the f615 hero window (3,000 slam + "teen" + a kick on beat 41); no off-hero spans. B: maximum 3.11 dB, same spot. |
| hero sync (SFX stem onsets) | ≤ 1 frame | f0 -0.04, f15 -0.40, f100 -0.42, f240 -0.40, f375 -0.40, f479 -0.75, f540 -0.39, f615 -0.32, f810 -0.39, f900 -0.09, f1076 -0.06 |
| drop-out | music digital silence, bed ≤ -40 | music exact zero f780-f809; bed (music + SFX) -48.5 LUFS momentary against -17.1 before; mix_A with "Bhai..." -12.2 |
| loop seam (A) | step ≤ 1.5 × local 2 ms max | step 0.0105 against 0.255 (0.15 of local p99) |
| stems | sum = A | residual -138.5 dBFS |
| sfx.wav | -18 LUFS or GR cap | -24.0 LUFS, -2.3 dBTP. The stem limiter is capped at 3 dB GR (a sparse, VO-led layer); in the mixes the SFX sits at -22.7 LUFS. |
| music.wav | -16 LUFS, ≤ -3 dBTP | -16.0 LUFS, -3.2 dBTP, LRA 6.4. Grid 120.00 BPM, phase +6 ms (past and present). Payoff maximum at f816.6. Stops f375-f389 and f780-f809 are digital silence. Seam passes. |
| VO stems | -16 LUFS, ≤ -2 dBTP | A and B: -16.0 LUFS, -2.3 dBTP, LRA 2.2. vo_final FLAC = the stems bit-exact; words.json = vo_final words. |
| stems in the mix | | stem_vo -14.2 LUFS / -2.1 dBTP, stem_sfx -22.5 / -3.8, stem_music -26.3 / -7.5 |
| format | 48 kHz 24-bit stereo, 1,728,000 samples | all mixes and stems |

The stems are pre-limiter slices at the A mix gains (house convention). `stem_vo` alone peaks at -2.1 dBTP; only the mixes carry the -2 dBTP limit.

### VO verification (this pass)

- `vo_stem.wav` / `vo_stem_B.wav`: 1,728,000 samples, -16.0 LUFS, -2.3 dBTP (ffmpeg ebur128).
- The vo_final FLACs decode bit-exact to the stems.
- words.json matches vo_final (67 / 63 words).
- Every word onset has voice energy.
- All 17 lines are present: C1-C4, C6-C16, P, Q. There is no C5 in the script.
- One alignment flag: C11 "Do" is heard as तो (both whisper models). Listener check needed.
- Raw takes are untouched and no new take was made.
- **VO wording differs from the caption text** (UI / lead):
  - C1: VO "Sirf ek photo bachi **hai**.";
  - C3: VO "Har click ginti mein **hota** tha.";
  - P: VO "**Bhai...** ek achha shot nahi hai."

## 6. Spectrogram review (`mix_A_overview.png`, `sfx_overview.png`, `music_spectrogram.png`, `audition/*.png`)

- Every cue tick in the SFX overview has energy.
- Low-end bursts sit only on the hero and slam frames: f100, f240, f375, f480, f540, f582, f615, f810 and f900.
- The constant low lines from f480 to f780 are the HDD spindles (90 Hz + harmonics), the edit-desk bed by design. They do not stack across hits.
- Nothing hisses constantly. The flash charge is the only long high tone (1.8 -> 7 kHz, f15-f98, under C1 / C2).
- The drop-out f780-f809 is a dark band in the music and SFX, with only the VO in mix_A.
- The momentary curve of mix_A stays between about -11 and -20 LUFS with the VO bars on top.

## 7. Notes and open items

- **AAC encoder.** The ffmpeg 6.1 native AAC encoder overshot to +4.2 dBTP on one frame (18.93 s) of a -2.3 dBTP mix_A in an earlier build. The same wav 0.1 dB lower encoded to -2.4 dBTP: an encoder event, not a mix property. The build retries with the limiter ceiling 0.1 dB lower (no retry was needed in the final build). The Windows master must be ebur128-verified after the mux (`deliver_reel.py` does this).
- No master has been rendered yet (stage 3). Frame checks of the hero cues against picture (frames n-1, n, n+1) and `qa_measure.py cues` on the master are still open. Sync is verified on the SFX stem only.
- For the lead: approve the P1-stays-f315 deviation (section 2), and the use of f100 for the flash.
- Listener checks: C11 "Do" (heard तो), C8 "thumb" (heard तंब).
- Hook B mixes are not built. Only `vo_stem_B.wav` and `words_B.json` exist.
