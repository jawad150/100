# thoda_left_bas: SOUND

This is a VO-led mix (LEAD_DECISIONS 1 and 3, Bijli convention). The deliverables are:
- `_ig` = VO + SFX + music (mix_A);
- `_ig_songready` = VO + SFX (mix_B);
- VO, SFX and music stems.

Owners: sound-designer and music-supervisor, 2026-10-12. Every check below is a measurement or a rendered image. Nobody has listened to this mix.

## 1. Files and rebuild

| what | path |
|---|---|
| VO chain and placement | `pipeline/jawad_reels/thoda_left_bas_vo.py` (`process`, then `assemble`). It writes `workspace/jawad_reels/thoda_left_bas/vo/vo_stem.wav` and `words.json` (plus `_B` versions for hook B) and `brand_reels/assets/thoda_left_bas/vo_final/` (FLAC + json). The table is in `VO_TIMING.md`. |
| music and the signal clock | `pipeline/jawad_reels/thoda_left_bas_music.py` (`build`, `curves`, `verify`). It writes `audio/music.wav` and `audio/signal_curves_{A,B}.json/.csv`. The picture imports `TM.yaw / TM.sig / TM.sig_c` from it. |
| SFX and mixes | `pipeline/jawad_reels/thoda_left_bas_sfx.py`. The frame cue table (`CUE_TABLE`, `BED_TABLE`, `STATIC_TABLE`) is at the top. `build` makes the SFX bus, the VO-floored SFX, the music rides, mix_A, mix_B, the stems, the AAC check and runs verify. Other modes: `cues`, `audition`, `verify`. |
| outputs | `workspace/jawad_reels/thoda_left_bas/audio/`: `mix_A.wav`, `mix_B.wav`, `stems/stem_{vo,sfx,music}.wav`, `sfx.wav` (with `sfx_fx.wav` and `sfx_bed.wav`), `sfx_vo.wav`, `music.wav`, `music_mix.wav`, `mix_summary.json`, `sound.verify.json`, `music.verify.json`, `mix_A_overview.png`, `mix_B_overview.png`, `sfx_overview.png`, `music_overview.png`, `audition/*.png` |

Rebuild (heavy jobs only):

```
cd pipeline/jawad_reels
tools/heavy.sh python3 thoda_left_bas_vo.py process     # cached; run one process at a time (whisper RSS grows: one run was OOM-killed at 14 GB and resumed from the cache)
tools/heavy.sh python3 thoda_left_bas_vo.py assemble
tools/heavy.sh python3 thoda_left_bas_sfx.py build      # rebuilds music.wav when the music module or words.json is newer
```

Render with `--no-sfx-build --audio workspace/jawad_reels/thoda_left_bas/audio/mix_A.wav` for `_ig`, and with `mix_B.wav` for `_ig_songready`. `BED = None` in the SFX module, so render.py must not rebuild this layer.

## 2. The VO-led grid: 1008 → 1080 frames (deviation from SHOTS.md; the motion designer must adopt it)

The measured Vlad takes do not fit the r1 picture plan. This holds at the fastest allowed speed (1.10x) and with tight pause caps (0.12 s for the shouts):
- **Hook.** V1 "Thoda left... thoda right..." alone is 2.80 s, and V2 "Bas bas! Ab theek hai!" is 1.95 s. "Bas" can land no earlier than f90, so the hook needs two bars.
- **Whole reel.** The 15 lines total about 34.6 s of voice for a 33.6 s reel.

LEAD_DECISIONS 3 says the picture moves to the VO, and a beat that cannot fit gets shortened. Two changes follow:
- **One bar is inserted at f72.** The reel becomes **1080 f = 36.0 s**, the format maximum.
- **Ladder F4 drops V6, V9 and V13** (Bijli V9 / pencil V9 precedent). Their captions carry them, and the takes stay processed in `proc/`.

Every r1 frame ≥ 72 moves +72 unless the VO moved it.

Structural landmarks on the new grid:
- the re-hook M3 lands on f504 (46.7 %);
- the payoff lands on f828 (76.7 %);
- the locks are f90, f378 and f720;
- the drop-out is f810–f827;
- the profile outro starts at `T_END = 954 / 30`.

Proposed BRIEF §6 values for the module:
- `DUR = 1080 / 30`;
- `CUTS = [(0, .6), (144/30, .5), (270/30, .3), (378/30, .6), (558/30, .3), (720/30, .5)]`, plus the beat cut f342 (S3 → S4);
- `PLAN = M3 504 / M2 792 / M3 936`.

| shot | r1 f | new f | beats on the new grid (VO word in brackets) |
|---|---|---|---|
| S1 hook A | 0–71 | **0–143** | H1 f0; yaw "right" move f56–66 and H1b `*right...*` f65 ("right..."); **LOCK + H2 `BAS BAS!` f90** ("Bas"); H3 `AB *theek hai!*` f126 ("Ab"); slip + B0 bubble f136 (during "theek hai!"); splice f144 (V2 "hai!" tail runs to f152, an L-cut) |
| S1B hook B | 0–71 | 0–143 | bonus (LEAD_DECISIONS 6). VO stem B carries V1 only in the hook. Hook-B music and SFX are not rebuilt (§7) |
| S2 roof day | 72–197 | **144–269** | R1 `*Aaya?*` f155; R2 far `NAHI! THODA LEFT...` f178 ("Nahi!"); mast jerks f180–185 and f190–198; **R4 `*kiska* left?!` + tape stop f234** ("Kiska"); music halts f234–251; mast back f252–269 |
| S3 CRT room | 198–251 | **270–341** (+1 beat) | C5 f270 ("Thoda"); overshoot into snow f304; C6 `NAHI NAHI, *wapas!*` f312 ("nahi"); V5 ends f372 inside S4 |
| S4 clamp macro | 252–305 | **342–377** (2 beats) | clamp ticks f342 / f351 (8ths); **marks align + C8 `BAS! BAS!` f360** (bar-5 downbeat). C7 `HAAN... HAAN...` has no slot (V6 is F4): drop it, or it overlaps V5 "wapas!" |
| S5 CRT lock | 306–377 | **378–449** | **LOCK + C9 f378** (V7 "Ab" f381); sitar run f387; gust f414; slip f418–430; C10 `ARRE, *phir se?!*` f432 ("Arre") |
| S6 roof wind | 378–431 | **450–503** | C11 f470 ("Yeh"), held across M3 to about f535 (V8 L-cut); big swing f486–503 |
| S7 timeline | 432–485 | **504–557** | **M3 f504**; C12 `20 SAAL BAAD` f504–539 (text only, V9 is F4); T1 toast f540 ("Thoda"); X 540 → 538 click f551 ("left...") |
| S8 phone | 486–521 | **558–593** | buzz f584; P1b bubble `thoda right...` f586 ("thoda") |
| S9 avalanche | 522–575 | **594–647** | rows every 3 f from f594; X jitter on the 8ths; P1c `nahi, pehle wala` f626 ("nahi,"), now a bubble over the avalanche rather than on the phone |
| S10 TAB / AB split | 576–647 | **648–719** | moves f648 / 666 / 684 / 702; C13 `DIALOGUE / *wahi* hai.` f668–708 over the split (V11) |
| S11 client lock | 648–719 | **720–791** | **LOCK + C14 / T2 f720** (V12 "Bas"); C15 + export f756–788 (V13 is F4, text-led); render complete f788 |
| S12 sunset | 720–863 | **792–935** | **M2 f792**; **drop-out f810–827**; **PAYOFF f828** (V14 "Hum" f834); P1 out about f918; 2° nudge f900 |
| S13 CRT loop | 864–1007 | **936–1079** | **M3 f936**; profile outro f954 (V15 f978–1051); B1 bubble f1062; loop seam → f0 |

Word-level frames for every line: `VO_TIMING.md` sections 2–3. The signal clock in `thoda_left_bas_music.py` (`YAW_MOVES`, `WOBBLE`, `LOCKS`, `SIG_C_ON`, `SHOTS`, `GAPS`) is already on this grid, as are `signal_curves_A.json` and the SFX cue table.

## 3. Policy and design

- **Music** is original and procedural at 100 BPM (18 f per beat, 72 f per bar), 15 bars. It is in D minor, with F major at the payoff.
  - Bar 1 is the inserted hook bar: Dm, riff B, lock kick + tabla dha on f90.
  - The signature tuning filter (`TM.lofi`, driven by `TM.sig`) opens on each lock frame. The measured band edges follow it: 294 Hz–2.1 kHz in the hook snow, full range on the locks (`music.verify.json` filter_check).
  - The VO pocket (-3 dB bell at 2 kHz) now follows the measured words.
- **Every SFX cue has an on-screen cause.** "Typing" from SHOTS §b was cut because nothing on screen types. Custom sounds are local to the SFX module, built with numpy only, and all pass `A.qc`; their spectrograms are in `audio/audition/`.

  | sound | what it is |
  |---|---|
  | `tlb_tv_lock` | static gated out on the hit + CRT thunk + a D6 ping: the lock "rhyme" at f90, f378 and f720 |
  | `tlb_creak` | GI pipe stick-slip in the strap clamp, about 47 Hz pulses on 520 Hz / 1.25 kHz / 2.2 kHz modes |
  | `tlb_clamp_tick` | clamp click |
  | `tlb_gust` | wind gust |
  | `tlb_buzz` | phone buzz, 170 Hz motor plus wood |
  | `tlb_payoff` | dhol + impact_soft + sub_drop, saturated for a low crest |
  | `tlb_static`, `tlb_wind`, `tlb_fan` | seamless 7.2 s beds. Each seam step is under the loop's own p99 sample step |

- **The CRT static follows the picture.** Its stem level = base + 14 dB × `TM.sig(f)`:
  - CRT shots: base -49 (S1, S13) and -46 (S3, S5);
  - the roof: -54 constant.

  S1 and S13 use the same level, so the loop seam is continuous.
- **The drop-out f810–f827 is real.**
  - The music is digital silence there.
  - SFX: only wind at -50, then a 0.25 s reverse cymbal into the payoff.
  - Mix A momentary loudness: **-46.1 LUFS** over f811–f819, -18.9 LUFS in the f821–f827 swell, against -13.5 LUFS just before.
- **Under the VO** (Bijli / pencil chain):
  - The `fit_under_vo` step drops non-hero cues inside words by 3–4 dB and carves them with hp 5.5 kHz or lp 1.1 kHz.
  - `sfx_vo.wav` holds the SFX 12.5 LU under each word (maximum cut 16.9 dB, no re-level). It sits in the mix at -23.2 LUFS.
  - epic_mix ducks the music 9 dB under the VO, plus the 8 LU per-word floor.
  - The VO stays 4 dB over the SFX via the sidechain.
- **VO rides** (gentle, per line; LEAD_DECISIONS 1):

  | line | ride | why |
  |---|---|---|
  | V1 | -1 dB | shouted hook line |
  | V2 | -4 dB | the shouted "Bas bas!" lines measured louder than the payoff window (per-stem momentary: VO -11.0 LUFS at f96 against -15.8 at the payoff) |
  | V12 | -3 dB | same reason as V2 |
  | V14 | +1 dB | the payoff line |
  | V15 | -1 dB | outro; widens the LRA |

  The VO peak tamer (true peak ≤ integrated + 10 dB) reaches 1.4 dB GR at most.
- **Music rides:**
  - payoff band +3 dB, f828–f852, with a 60 ms attack ramp that keeps the boost off the hit transient. +5 dB was tried and pushed V14's words under the floor;
  - outro card -1.5 dB, f954–f1068, back to 0 dB by f1077.
- **The f90 lock is not a hero cue.** The shout owns that frame. With hero status its 35 ms protected transient left V2 "Bas" 6.9 LU over the bed, below the 7 LU rule.

## 4. Cue summary (frames on the 1080 grid; full table at the top of `thoda_left_bas_sfx.py`)

| frame | event | sounds |
|---|---|---|
| 0 | loop release | impact_soft lp 900 |
| 56 / 66 | picture slides right / keyword flip | tlb_creak, swish_small |
| **90** | LOCK 1 `BAS BAS!` | tlb_tv_lock |
| 136 | slip + B0 bubble | glitch_short, notif_ping |
| 180 / 190 / 252 | mast jerks / back | tlb_creak |
| **234** | `kiska left?!` | tape_stop (hero, align start) |
| 304 | overshoot to snow | glitch_short |
| 342 / 351 / **360** | clamp ticks / marks align | tlb_clamp_tick (+2, +5 st), slot_tick |
| **378** | LOCK 2, the film starts | tlb_tv_lock (hero), sitar_pluck + harmonium_swell (hp 300, lp 4 k: TV speaker) |
| 414 / 420 | gust / tear | tlb_gust, glitch_short |
| 486 / **504** / 512 | swing / M3 / settle | tlb_creak, whoosh_fast, card_slide |
| 540 / 551 | toast / X nudge | notif_ping, mouse_click + ui_tick |
| 584 / 586 | phone buzz / bubble | tlb_buzz, bubble_pop |
| 594–639 / 626 | avalanche / P1c | slot_tick ×18, ui_tick 8ths, bubble_pop |
| 648 / 666 / 684 / 702 | split moves | tlb_creak + bubble_pop + ui_tick (3 per instant, the maximum) |
| **720** | LOCK 3, client `BAS BAS!` | tlb_tv_lock (hero), impact_big |
| 788 / **792** | export 100 % / M2 | render_complete (pitch 0.891), reverse_swell, shimmer |
| 810–827 | drop-out | wind -50, reverse_cymbal 0.25 s (passes the gate) |
| **828** | PAYOFF | tlb_payoff (hero) |
| 900 / **936** / 944 | nudge / M3 / settle | tlb_clamp_tick, whoosh_fast, card_slide |
| 957 / 991.5 / 999 | outro pill / card / question | swish_small, glass_tap, shimmer (PO timings) |
| 1062 / 1080 | B1 bubble / loop swell | notif_ping, reverse_swell (ends on f1080 = f0) |

## 5. Measurements (final build)

| check | target | measured |
|---|---|---|
| mix_A (ffmpeg ebur128) | -14 LUFS ±0.5, TP ≤ -2.0 | **-14.0 LUFS, -2.3 dBTP, LRA 2.2 LU** |
| mix_B (ffmpeg ebur128) | same | **-14.0 LUFS, -2.3 dBTP, LRA 2.4 LU** |
| AAC 320 k check | TP ≤ -1.5, I ±0.5 | A: -14.0 LUFS / -2.3 dBTP; B: -14.0 LUFS / -2.2 dBTP |
| LRA | 2.0–9 LU (LEAD_DECISIONS 1) | A 2.16 (epic_mix) / 2.2 (ebur128); B 2.39 / 2.4 |
| VO over the bed, per word (A) | ≥ 8 LU (7 on one syllable) | 61 words: minimum 7.1 (one-syllable "Bas"), median 12.8; minimum over the music alone 9.3 |
| VO over the music, per line (A) | ≥ 8 LU | V1 12.6, V2 14.0, V3 11.2, V4 17.1, V5 12.3, V7 11.0, V8 14.8, V10 13.3, V11 14.4, V12 16.0, V14 12.2, V15 20.0 |
| loudest moment | the payoff | A: momentary maximum -9.92 LUFS at f833 (payoff); next loudest -10.38 (f720 lock 3). B: -9.23 at f833 against -10.38 |
| limiter (A) | ≤ 3 dB GR outside heroes; over-3 dB total ≤ 0.1 s | maximum 4.48 dB, 0.080 s, all inside the f828 payoff window; no off-hero spans. B: maximum 2.98 dB |
| hero sync (SFX stem onsets) | ≤ 1 frame | f0 +0.79 (envelope rise), f90 -0.40, f136 -0.34, f342 -0.40, f360 -0.40, f378 -0.92, f551 -0.37, f720 -0.99, f828 -0.32 |
| loop seam (A) | step ≤ 1.5 × local p99 | step 0.0136 against p99 0.368; momentary last / first 0.4 s: -13.8 / -13.9 LUFS |
| stems | sum = A | residual -138.5 dBFS |
| sfx.wav | -18 LUFS or GR cap | -19.6 LUFS, -2.3 dBTP (stem limiter capped at 3 dB GR: a sparse, VO-led layer) |
| music.wav | -16 LUFS, ≤ -3 dBTP | -16.0 LUFS, -3.3 dBTP, beat grid 99.98 BPM (phase -5 ms), drop-out digital silence |
| VO stems | -16 LUFS, ≤ -2 dBTP | A and B: -16.00 LUFS, -2.1 dBTP |
| format | 48 kHz 24-bit stereo, 1,728,000 samples | all mixes and stems |

Stems are at the A mix gains (house convention, `deliver_reel.py`). Only the mixes carry the -2 dBTP limit: `stem_vo.wav` peaks at -1.6 dBTP on its own (pencil: -1.8).

## 6. Spectrogram review (`mix_A_overview.png`, `sfx_overview.png`, `music_overview.png`)

- Every cue tick has energy in the SFX overview.
- The drop-out is a clear dark band.
- Low-end bursts sit only at the locks and the payoff.
- The 5–12 kHz static wash from f936 to the end was lowered 3 dB (S1 and S13 at the same level). It is the CRT snow of the loop world, by design.
- The music overview shows the tape stop at f234, the drop-out at f810 and the lo-fi curve following the signal clock.

## 7. Open items for the next stage

- **Motion designer:** adopt the 1080-f grid (§2) and the VO_TIMING §3 frames, including P1c over the avalanche, C13 over the split, and C7 dropped. The music, SFX and signal clock already follow them.
- **Hook B (bonus):** `vo_stem_B.wav` / `words_B.json` exist (V1 in the hook, no V2). `music_hookB.wav` and hook-B SFX cues were not rebuilt for the 1080 grid. `thoda_left_bas_music.py build --hook B` is ready; the SFX module builds hook A only.
- **V15 CER 0.286:** the ASR hears घर as "गर" and था as "ता", i.e. weak aspiration in the TTS. All 7 tokens aligned. A re-take would be paid (max 5 credits per reel, LEAD_DECISIONS 3), so none was made; listen-check at QA.
- **V1 CER 0.200:** थोड़ा heard as तोड़ा (the same aspiration); aligned 4/4.
- The previous team's uncommitted `sfx_library_LICENSES.md` edit (a per-container library re-fetch log) was left untouched.
