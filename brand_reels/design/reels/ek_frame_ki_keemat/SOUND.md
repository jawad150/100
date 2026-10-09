# SOUND: Reel 3 · C08 · Ek Frame ki Keemat (SFX layer, cue sheet, rough mix)

Date 2026-10-09 · Owner: sound-designer · Status: **SFX stems A + B built on the FINAL VO; rough mixes measured.** Picture events
are BRIEF r2 §5 (the reel module does not exist yet); the cue-against-frame check waits for the master (§7).

Code: `pipeline/jawad_reels/ek_frame_ki_keemat_sfx.py` (no shared module edited). Binding: BRIEF r2 §4, §5, §6, §10, §11, §18;
SLATE §3.3 (motif = the pause click: mouse click + glass) and §5.1. Key/harmony: MUSIC_ek_frame_ki_keemat.md (D Phrygian-dominant).
Words: `<RW>/vo/ek_frame_ki_keemat_vo.words.json` (= `words.json`, 61 words) + the VO audio (`vo_stem.wav`, speech activity used
for the hero test and the carve).

```bash
cd pipeline/jawad_reels; H=tools/heavy.sh
$H python3 ek_frame_ki_keemat_sfx.py build     # A + B stems, cues/qa-cues json, report, overview png (~20 s)
$H python3 ek_frame_ki_keemat_sfx.py rough     # rough mixes A / B / hook B through the music-supervisor's chain + measurements
$H python3 ek_frame_ki_keemat_sfx.py verify    # mixer == audio.mix check, stem checks, onsets
$H python3 ek_frame_ki_keemat_sfx.py cues      # fitted cue table (--hook B for the Trial hook)
```
Render flag: `--no-sfx-build --audio <RW>/audio/ek_frame_ki_keemat_mix.wav` (the music-supervisor's final mix of this stem).
Builder: keep `cues(): return []` and `BED = None` in `ek_frame_ki_keemat.py` (BRIEF 17.2). To move sounds with a picture
retime, define `SFX_EVENTS = dict(land12=5.23, ...)` in the reel module (keys = `EV` in the sfx module); `events()` reads it, then
re-run `build` and the final mix.

## 1. Files (all 48 kHz, 24-bit, stereo, 1,612,800 samples = 33.600 s)

| file (`workspace/jawad_reels/ek_frame_ki_keemat/audio/`) | what |
|---|---|
| `ek_frame_ki_keemat_sfx_stem.wav` | **SFX stem, hook A** (-18.0 LUFS, -2.2 dBTP). sha256 `36183fbb…b7ef` |
| `ek_frame_ki_keemat_hookb_sfx_stem.wav` | SFX stem, hook B: B cues 0-3.0 s + the A body at A's exact gains (the music module splices it at 3.000 s). sha256 `1ce28e8d…aea` |
| `ek_frame_ki_keemat_cues.json`, `_qa_cues.json`, `_sfx_report.json` | fitted cues (A, B), `qa_measure.py cues` format, per-cue placement / duck / limiter numbers |
| `ek_frame_ki_keemat_sfx_overview.png`, `_hookb_sfx_overview.png` | spectrogram + loudness curve + cue ticks (viewed) |
| `qa_sfx/*.png` | zooms: reveal 24-28 s (mix and stem), hook 0-3 s, C3 15.5-18 s, loop seam (viewed) |
| `rough/ek_frame_ki_keemat_{mix,vo_sfx,hookb_mix,hookb_vo_sfx}.wav`, `_stem_{vo,sfx,music}.wav`, `_mix.png`, `_mix.json`, `_rough_report.json` | **rough mixes** (version A full, version B VO + SFX, both hooks) and stems at mix gains. Rough only: the final names in `audio/` belong to the music-supervisor |

## 2. Cue sheet, hook A (and the body of hook B)

`brief` = BRIEF §11 gain; `module` = gain written in the module (LV, §4); `VO` = what `sfx_jawad.fit_under_vo` / the carve did;
`stem` = gain after `audio.duck_under` (the level actually rendered). `align` hit unless noted. Instants (25 ms): 4.798/4.8 (3),
12.0 (2), 16.8 (2), 20.398/20.4 (3), 26.397/26.4 (3): **never more than 3** (the sparkles 30 ms later are their own instant).

| t (s) | f | sound | params | brief | module | VO treatment | stem | event it serves |
|---|---|---|---|---|---|---|---|---|
| 0.000 | 0 | impact_soft | align start, cue `dur` 0.25 | -8 | -8 | tail carved -8 under "Aap" (from 0.085 s) | -8.0 | f0 transient + loop release; stops before the pause |
| 0.300 | 9 | **jd_mouse_click** | pan +0.2 (chip x 760) | +4 | -2 | inside "Aap": -8 (MID) | -11.5 | **MOTIF: pause click** |
| 0.600 | 18 | jd_glass_slide | dur 0.3 (starts on the click) | -2 | -2 | inside "ise": -8 | -10.0 | **MOTIF part 2: glass on glass**, lands on the seam glint |
| 0.900 | 27 | card_slide | lp 1100 | -8 | -8 | -6 | -14.0 | layers separate |
| 1.600 | 48 | whoosh_slow | dir +1 | -10 | -10 | -6, lp 1100 | -16.0 | pull-back |
| 2.400 | 72 | whoosh_slow | dir -1, pan +0.3 | -8 | -8 | body before the pass carved -8 under "jhapakte dekha", tail under V2 | -8.0 | orbit starts |
| 3.000 | 90 | slot_tick | align start, n 12, dur 1.8, **hp 4500** | -12 | -12 | -8 | -23.8 | counter 00 → 12 (lands 4.8) |
| 4.798 / 4.800 / 4.830 | 144 | glass_truth: ui_click (A6) / glass_tap (D7) / sub_drop 0.8 lp 120 / jd_sparkle | | stack | stack | inside "mein...": -8 / -8 / -6 / -6 hp 5500 | -18.9 / -14.5 / -16.0 / -20.3 | "12" lands, side-on stack |
| 5.700 | 171 | whoosh_slow | dir +1 | -6 | -6 | -6, lp 1100 | -12.0 | swoop into the fly-through |
| 6.0 … 11.4 (10×) | 180 … 342 | jd_ui_tick | pitch D8 1.4265 / A8 2.1374 alternating | -14 | -14 | 9 of 10 inside words: -6, hp 5500 (9.6: free, tail carved) | -20.0 (9.6: -14.0) | tags 01-08, 09/10, 11 |
| 12.000 | 360 | impact_soft | | -8 | -8 | "Aur" starts 12.05: -6, lp 1100 | -14.0 | **RE-HOOK**: stop on pane 12 |
| 12.000 | 360 | glass_tap | pitch Eb7 1.1874 | -10 | -10 | -8 | -21.8 | the near-invisible pane |
| 12.600 | 378 | whoosh_slow | dir -1 | -10 | -10 | -6, lp 1100 | -16.0 | swing to frontal |
| 13.200 / 13.800 | 396 / 414 | jd_ui_click | pitch G6 1.0846 | -6 | -6 | -8 | -14.0 | flick OFF |
| 13.500 | 405 | toggle_on | | -8 | -8 | in the 13.39-13.64 gap; tail carved -8 | -8.0 | flick ON |
| 14.400 | 432 | toggle_on | | -6 | -6 | -8 | -15.7 | flick ON, resolved "with" |
| 14.430 | 433 | jd_sparkle | | -12 | -12 | -6, hp 5500 | -18.0 | the frame comes alive |
| 16.733 | 502 | reverse_swell | **0.603 s** (plan 0.733), starts 16.130 | -3 | -7 | shortened to start after "lagta." (speech to 16.130) | -8.4 | C3 approach into the portal disc (plan cue) |
| 16.800 | 504 | air_zoom | | -6 | -9 | tail carved -8 under "Ek second" | -13.2 | **C3 portal cut** (plan cue) |
| 16.800 | 504 | impact_soft | **sat 4** | -1 | -5 | tail carved -8 | -5.0 | C3 cut, corridor (plan cue) |
| 16.900 | 507 | jd_sparkle | | -12 | -12 | -6, hp 5500 | -19.5 | light wave |
| 18.900 | 567 | slot_tick | align start, n 29, dur 1.5, **hp 4500** | -10 | -10 | -8 | -21.8 | counter 12 → 360 (lands 20.4) |
| 19.200 / 19.800 | 576 / 594 | whoosh_by | dur 1.4, dir ±1, pan ∓0.4 | -6 | -6 | -6, lp 1100 | -12.0 | surge passes |
| 20.398 / 20.400 / 20.430 | 612 | glass_truth: ui_click (A6) / glass_tap (A6 0.8396) / sub_drop 0.8 / jd_sparkle | | stack | stack | in V7's pause (20.34-20.59): -8 / -8 / -6 / free, tail carved | -18.9 / -14.5 / -16.0 / -14.3 | "360" lands |
| 21.900 | 657 | bar_grow | align start, 0.3 s, pitch Bb4 0.9792 | -10 | -10 | -8 | -18.0 | three lanes rise |
| 24.300 / 24.750 / 25.200 | 729 / 742.5 / 756 | whoosh_by | dur 1.0, dir +1/-1/+1, pan -0.5/+0.5/-0.5 | -6/-6/-8 | -10/-10/-12 | 24.3 inside "tracks.": -6 lp 1100 | -16.0 / -10.0 / -12.0 | rush |
| 25.800 (ends) | 774 | riser | 1.2 s (24.6-25.8), stops dead | -4 | -8 | free | -8.0 | into the drop-out |
| **25.800-26.067** | 774-781 | **drop-out** | pre-drop bus cut at 25.796-25.800, stays cut | | | | digital 0 | true silence, 8 frames |
| 26.067 | 782 | **jd_mouse_click** | | +4 | -11 | free | -11.0 | **MOTIF: the play click** (held breath) |
| 26.367 | 791 | whip | dir +1 | -6 | -16 | tail carved -8 | -19.5 | C8 punch-in (plan cue) |
| 26.397 | 792 | flash_hit | **sat 3** | -3 | -15 | tail carved -14 under "Keemat" | -18.5 | REVEAL transient (ember_slam) |
| 26.400 | 792 | **impact_big** (HERO) | **sat 8** | 0 | 0 | hero test OK (speech 24.36 / 26.75); tail carved -14 under V9-V10 | -3.5 | **REVEAL: the slam** |
| 26.400 | 792 | sub_drop | dur 1.6, lp 120 | -4 | -4 | tail carved -14 | -7.5 | reveal sub |
| 26.620 | 799 | shimmer | hp 5500 | -10 | -10 | tail carved -8 | -11.5 | payoff keyword rises |
| 29.500 | 885 | swish_small | align start | -12 | -12 | -6, hp 5500 | -18.0 | card: monogram ring |
| 29.970 | 899 | shimmer | | -10 | -10 | -6, hp 5500 | -16.0 | card: CTA keyword |
| 30.150 | 904.5 | glass_tap | pitch D7 1.1207 (card default 1.0) | -12 | -12 | -8 | -20.0 | card: monogram settles |
| 33.600 (ends) | 1008 | reverse_swell | **0.75 s** (card 0.8), starts 32.850 | -8 | -8 | shortened to start after "bhejo." | -8.0 | loop bridge into f0 |

No cue at 28.2 (the hidden-JD glint is silent by design). No SFX bed. Hero test (`fit_under_vo`, words + VO audio): only
`flash_hit` 26.397 and `impact_big` 26.4 are heroes; both pass (≥ 120 ms clear before, ≥ 300 ms after: next speech 26.75).

**Hook B head (0-3.0 s, fitted against the hook-B VO "Ek second. Teen sau saath layers.", 0.10-2.63):** impact_soft 0.0 align
start -6 (not ducked) · whoosh_by 0.2 dir +1 -4 → -6 lp 1100 (stem -11.5) · whoosh_by 0.6 dir -1 -6 → -12.0 lp 1100 ·
whoosh_by 1.2 dir +1 -8 → -14.0 lp 1100 · jd_reverse_swell 1.2 s ending 3.000, -8 → span -6 lp 1100 (it cannot be shortened
to clear "layers." and still last 0.5 s). From 3.0 s the body above. The B stem differs from A after 3.0 s only by the tails of
hook A's own cues (the 2.4 s whoosh to 6.14 s); the music module takes B before 3.000 s and A after.

## 3. Motif, drop-out, loop

- **Motif (SLATE): the pause click** = `jd_mouse_click` on f9 + `jd_glass_slide` starting on the same click and landing on the
  seam glint (f18): click + glass creak. The **play click** at f782 is the same micro-switch, alone after 8 frames of silence.
  Inside "Aap" the pause click is ducked -8 dB, yet it reads as the event: in rough mix A the 2-9 kHz band jumps **+13.9 dB** at
  0.300 s (the click lands in the /p/ closure of "Aap": VO 2-9 kHz in that 11 ms window is -49.5 dBFS vs the click's -9.7 dBFS
  in the SFX stem); the spectrogram (`qa_sfx/mix_hook_0-3.png`) shows a clean broadband line on the cyan marker.
- **Drop-out (one per reel, at the reveal):** everything that starts before 25.800 (with its room send) is cut dead at
  25.796-25.800; the riser ends there (the "suck"). Measured: SFX stem digital zero **25.80000-26.06673 s** (f774-f781 exactly);
  mix A f774-f781 **-300 dBFS** (VO, music and SFX all 0.0); first SFX sample after 25.8 = **26.0667** (the play click), first music
  sample **26.392** (its gate); f782-f791 RMS -22.6 dBFS = the click, its release, the whip lead-in and the flash_hit suck.
- **Loop:** circular mix: tails past 33.6 wrap onto t = 0 (no tail fade); the card swell ends exactly on 33.600; frame 0's
  impact_soft is the release. Mix A: last 50 ms -13.5 dBFS RMS, first 50 ms -11.3; sample step across the seam 0.040 against a
  median of 0.013 and a 99th percentile of 0.206 (no click); `qa_sfx/mix_loop_seam.png`: swell + cymbal rise into the seam, f0
  continues.

## 4. Levels: why they differ from the brief (measured, not by ear)

The brief's levels were set before any stem existed. Two facts drove every change, both measured:
1. **epic_mix places the SFX stem by its integrated loudness** (-18 LUFS). In this sparse stem the integrated is set by a few
   loud, VO-free events (C3, rush, riser, reveal). Every duck or carve under the VO lowers the integrated and so raises the gain
   on everything else; the balance between VO-free events has to be set inside the stem.
2. **Crest factors.** `jd_mouse_click` 21.9 dB, `whip` 15.5, `flash_hit` 14.5, `impact_big` 9.9 dB (true peak minus max
   momentary). At the brief's levels the -18 LUFS stem limited the play click by 10 dB and made C3 the loudest moment.

What the module does (all numbers from `mix_loop` + the final chain, variants run in a scratch harness and deleted):
- **Transient saturation** (`sat_transient`: alias-safe `sfx_jawad.shape`, 8x oversampled, only on the first 0.3 s, loudness-
  matched, tail from 0.5 s untouched): impact_big drive 8 (peak-to-loudness 9.9 → 4.7 dB), flash_hit drive 3 (14.5 → 8.3), C3
  impact_soft drive 4 (9.8 → 3.7). The reveal is dense instead of spiky, so it survives the master's glue + limiter.
- **Carve** (`assign_carve`): tails and pre-hit bodies of cues not already ducked are pulled down where the VO speaks (words +
  measured VO activity, 15 ms lead, 30 ms ramps, never within -20/+30 ms of the hit): -14 dB for the reveal stack, -8 dB for the
  rest. Before it, "Keemat..." sat **under** the boom's bloom (word level -0.5 dB in a test mix).
- **Gains** (`LV`): pause click +4 → -2, play click +4 → -11, C3 swell / air / hit -3 / -6 / -1 → -7 / -9 / -5, rush -6/-6/-8 →
  -10/-10/-12, riser -4 → -8 (bible 4.5: ≥ 4 LU under the hit), flash_hit -3 → -15 and whip -6 → -16 (their cracks stack with
  impact_big's in one limiter event), impact_big 0 (kept).
- **Swells shortened** to start after speech (bible 4.5, risers never over words): C3 0.733 → 0.603 s, loop 0.8 → 0.75 s.
- **1-4 kHz under words:** slot_tick rolls (12 and 29 ticks under V2 and V7) get hp 4500; tag ticks are tuned to D8 / A8
  (4.7 / 7.0 kHz) instead of 3.3 / 3.7 kHz, and fit_under_vo's hp 5500 keeps them above the voice.

Tonal SFX in the bar's harmony (`TUNE`, dominant partial measured, bible 4.2): glass_tap D7 at 4.8 (bar 2, i) and 30.15 (bar 12,
bVI), A6 at 20.4 (bar 8, i), **Eb7 at 12.0** (bar 5 is bII = Eb G Bb; the brief's D would sit a semitone under its root);
ui_click A6; flick clicks G6 (3rd of bII); lanes bar_grow Bb4 (bar 9, bVI); ticks D8 / A8. The music's 8th grid and taiko onsets
coincide with 4.8, 12.0, 14.4, 16.8, 19.2-25.2 and the dhol with 26.4 (music map).

## 5. Measurements

**SFX stems** (`build`, `verify`):

| stem | I (BS.1770 / ffmpeg) | TP | LRA | max momentary | limiter max GR | glue | notes |
|---|---|---|---|---|---|---|---|
| A | -18.01 / -18.0 LUFS | -2.20 dBTP | 21.0 LU | -6.1 LUFS (reveal) | **4.0 dB at 26.3964** (> 1 dB for 1.9 % of the time) | 3.1 dB | silence 25.800-26.067; no `hit before 0 s`; only intended wraps |
| B | -17.91 / -17.9 | -2.20 | 21.1 | -6.1 | 4.0 dB at 26.3964 | 3.1 dB | rendered at A's gains (so it is not re-normalised); body = A after 6.14 s |

- `mix_loop` with gate, wrap, saturation and carve off is **bit-identical to `audio.mix`** on the same cues (max |diff| 0.0).
- The limiter's 4.0 dB is one event: the stacked cracks of flash_hit (26.397) and impact_big (26.400). Elsewhere ≤ 3.2 dB (rush
  24.75 3.2, loop swell 2.7, C3 swell 2.4, toggle 13.5 2.3). Getting the reveal event under 3 dB needs flash_hit and whip at
  about -30 (inaudible) or a quieter reveal, which costs the "loudest moment" margin below; I kept 4.0 dB on the hero crack.
- Onsets on the A stem (first +9 dB rise of the 2 ms envelope, vs the hit): pause click -0.8 ms, glass_truth 4.8 -3.3 (its
  ui_click leads by 2 ms), re-hook 12.0 -2.9, flicks -1.3/-1.4/-1.3/-1.4, C3 -0.2, 20.4 -9.7 (the sub_drop's 10 ms pre-roll), play
  click -0.9, impact_big -3.1 (flash_hit leads by 3 ms): all within 1 frame. f0: attack from 6 ms, envelope peak 33.5 ms (f1),
  +25.3 dB over the first 2 ms (QA asks for an onset in f0-f2). The card glass_tap (30.15, -20 under "hai") has no separable onset.
- Spectrograms (viewed): every cue tick has energy; no hiss floor; sub only on 4.8, 20.4 (0.8 s each) and the reveal stack (the
  designed impact_big + sub_drop pair), no two sub tails from different events overlap; the drop-out is a black column; the
  reveal tail steps down under "Keemat" (the carve) and continues under the line.

**Rough mixes** (`rough`: `ek_frame_ki_keemat_music.mix(hook='B')` = `epic_mix.mix_reel`, real VO (dual-mono copy, R7) + these
stems + `music_full.wav`):

| mix | I (ffmpeg) | TP (wav) | LRA | master limiter GR | max momentary |
|---|---|---|---|---|---|
| A full, hook A | **-14.0** LUFS (-14.04) | **-2.3** dBTP | **1.7** LU | 3.07 dB | **-9.26 LUFS, window 26.35-26.75 (centre 26.55 = 26.4 + 0.15)**; next loudest -10.35 at 16.74 (C3): margin 1.09 LU |
| B VO + SFX, hook A | -14.1 (-14.05) | -2.3 | 1.8 | 2.46 dB | -8.87, centre 26.53; next -10.32 at 21.10 (VO): margin 1.45 LU |
| A full, hook B | -14.0 (-13.98) | -2.3 | 1.6 | | |
| B VO + SFX, hook B | -14.0 (-13.95) | -2.3 | 1.7 | | |

VO clarity, mix A:

| measure | VO over music | VO over SFX | VO over bed (music + SFX) |
|---|---|---|---|
| epic_mix report (median, voiced frames) | **11.4 LU** | 20.3 LU | |
| 400 ms momentary, voiced frames: median / p10 / min | 12.3 / 6.6 / -1.8 | 22.1 / 8.8 / -8.4 | 11.3 / 4.7 |
| **word level** (K-weighted energy over each of the 61 words): median / min | 13.1 / 2.2 | **23.4 / 6.4** (no word under 6) | 11.0 / 2.1 |

- The 400 ms SFX minimum (-8.4 at 26.75) is window smear: a window centred on "Keemat" (0.35 s after the hit) still holds the
  slam. Word level, every word is ≥ 6.4 dB over the SFX under it (lowest: "Aur" 6.4, "Aap" 6.4, "Ek" 6.6, "mein..." 7.2,
  "Keemat..." 8.3).
- **Under 8 dB against the music (word level): V9 only** ("Keemat..." 6.8, "banane" 6.4, "jaanta" 6.2, "hai." 2.2; "hain." 8.0):
  the drop bar (dhol chaal, 808, strings LP 1500) under the payoff line. Music-supervisor item (§8).
- Phone check (`A.hp(x, 250, 4)`): the reveal loses **3.2 dB** (≤ 7). Mix A's spectrogram (`rough/ek_frame_ki_keemat_mix.png`)
  and the zooms were viewed.

## 6. Picture vs the final VO (for the creative-director and the builder)

The cues sit on BRIEF r2's picture events. With the final VO several picture beats no longer meet their words (VO_TIMING.md §4):
"12" is spoken at 5.230 (the counter lands 4.8, so its glass_truth falls in "mein..."), the tags 6.0-11.4 no longer meet
"Andhera / Roshni / Chehra / lafz / chamak", the flicks 13.8 / 14.4 meet "jiske" / "frame" instead of "bina" / "zinda", the
re-hook stop at 12.0 now has a 0.126 s VO gap (11.924-12.05) instead of 0.44 s, so its impact_soft is ducked -6. If the picture
follows the voice, set `SFX_EVENTS` in the reel module (e.g. `land12=5.23`, `tags=(...)`, `flicks=(13.2, 13.5, 14.051, 14.869)`,
`land360=20.59`) and re-run `build` + the final mix; `fit_under_vo` re-ducks everything against the words automatically.
None of these is a hero; the only heroes (26.397 / 26.4) sit in the 24.36-26.75 VO gap either way.

## 7. Not done yet / needs the master

- **Cue against frame:** `python3 plugins/reels-studio/skills/reels-production-playbook/qa_measure.py cues <master.mp4>
  <RW>/audio/ek_frame_ki_keemat_qa_cues.json` and frames n-1, n, n+1 at f9, f144, f360, f504, f612, f782, f792 once the master
  exists. Master loudness after AAC (≤ -1.5 dBTP, I within 0.3 LU) belongs to the final mux.
- Nobody has listened. "jhapakte / lafz / chamak" still need the human listen VO_TIMING.md asks for (no SFX sits on them louder
  than -6 dB).

## 8. Open items for others

1. **Music-supervisor / lead: mix LRA 1.6-1.8 LU** against BRIEF §18's 5-9 LU (all four rough mixes). The mix is VO-led and the
   final chain (VO -16 LUFS, glue, -14 LUFS master) sets it; the SFX stem alone has 21 LU. Same finding as C15's SOUND.md.
2. **Music-supervisor: V9 vs the drop** (word level 2.2-6.8 dB, §5). A deeper VO duck on bar 11's strings / 808 during
   26.75-29.17 would fix it without touching the 26.4 drop.
3. **R7 in SHARED_REQUESTS.md:** `epic_mix.mix_reel` raises on the mono FINAL VO (`(N, 1)` from `audio.read_wav`); the final
   `ek_frame_ki_keemat_music.py mix` will hit it. Workaround used here: dual-mono copies.
4. `USKO` / `USSE` (BRIEF §20 Q6) does not change the SFX: the fallback `vo_usey` stem ends V10 at 33.07, the loop swell would then
   start after it (its `clear_spans` rule re-solves on `build`).
