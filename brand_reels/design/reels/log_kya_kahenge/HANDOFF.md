# HANDOFF: Reel 5 · C15 · Log Kya Kahenge → motion-timeline-builder

Date 2026-10-09 · Author: creative-director · For: the motion-timeline-builder, who builds `pipeline/jawad_reels/log_kya_kahenge.py`
(+ `log_kya_kahenge_crowd.py`, `log_kya_kahenge_hookb.py`) next.

**Read order:** this file, then `BRIEF.md` r2 (§5-§8, §10, §17 are still the geometry, string and contract spec), then `FACES.md` §2
and §7 (API and wiring), then `SOUND.md` §0. **Where this file and BRIEF r2 / `packet.yaml` v2 differ, this file wins** (r3 deltas, §2).

Inputs used (all read for this handoff): `BRIEF.md` r2, `SCRIPT.md` v3 + `script.json`, `GATE.md` r1, `VO_TIMING.md` (MEASURED 06:53),
`FACES.md` r2, `SOUND.md` run 2, `MUSIC_log_kya_kahenge.md`, `SHARED_REQUESTS.md`, SLATE §0/§2/§3.5/§4/§5, the props report (none),
the music, VO, faces and SFX reports. Everything below marked "measured" I re-measured today from the files themselves
(VO envelope, words.json, `T.measure`, `EndCard`, `LF.cam_s3` / `LF.jd_rect`, a dry run of `SC.Captions` on the real words).

Conventions: `f = floor(30 t)` (the frame during which an event starts); `<RW>` = `/home/user/100/workspace/jawad_reels/log_kya_kahenge`;
`<P>` = `/home/user/100/pipeline/jawad_reels`; `<D>` = `/home/user/100/brand_reels/design/reels/log_kya_kahenge`.

---------------------------------------------------------------------------------------------------------------

## 1. Readiness at a glance

| item | status | note |
|---|---|---|
| VO stems A/B + word timings | **READY** | measured, 61/60 words aligned, every CER ≤ 0.125, all no-VO windows clean |
| faces module (`log_kya_kahenge_faces.py`) | **READY** | S3-01 + S5-01, `jd_rect`, `s3_rays`, `key_gain`; stills viewed |
| music bed (`music_full.wav` + 5 stems) | **READY** | rebuilt 2026-10-09 with the EP ducks on the measured VO windows (§11 risk 4 resolved) |
| SFX stems A/B + cue lists | **READY** | refitted to the measured VO |
| 3D props | **none needed** | BRIEF §13: the crowd is procedural numpy (`log_kya_kahenge_crowd.py`, yours) |
| captions plan | **READY** | dry-run on the real words: 20 chunks (A), `cap.check() == []` (§6) |
| crowd module, reel module, hook-B module | **TO BUILD (you)** | none exists yet; §7.4 still gate first |
| final audio mix (`log_kya_kahenge_mix.wav`, `_hookb_mix.wav`) | **READY** 2026-10-09 | `log_kya_kahenge_mix.py` → `<RW>/audio/final/` (links at the §4 paths); -14.0 LUFS, -2.3 dBTP, loop-safe. Open: LRA of version A (§11 risk 5, lead) |
| master render, splice, QA, delivery | **BLOCKED** on the module | |

---------------------------------------------------------------------------------------------------------------

## 2. What changed since BRIEF r2 (r3 decisions, made here; nothing else changes)

| # | what | BRIEF r2 | r3 (binding) | why |
|---|---|---|---|---|
| 1 | V2 wording | "Hum **apni** zindagi unke hisaab se edit karte hain... jo poori video dekhte bhi nahi." (15) | "**Hum zindagi** unke hisaab se edit karte hain... jo poori video dekhte bhi nahi." (14) | BRIEF §9 overrun rule (15-word take ran 6.34 s against 6.03 s). Captions follow words.json automatically |
| 2 | IG caption line 2 | quotes the 15-word V2 | `Hum zindagi unke hisaab se edit karte hain... jo poori video dekhte bhi nahi.` | the post copy quotes the VO exactly |
| 3 | V7 onset | 31.600 (f948) | **31.433 segment / 31.443 first word (f943)**; last voice 35.070 | V7 at the 1.10x ceiling still runs 3.64 s; from 31.6 it would end 35.24 > 35.10. VO moved, **picture does not** (§3.2) |
| 4 | gag silence | 29.10-31.60 | **28.96-31.44** (measured, no voice) | follows #3 and V6's measured end |
| 5 | S3-01 camera | `CAM_RISE` level pedestal 700 → 2600 mm `easy_ease`, pitch 0 | **`LF.cam_s3(t)`**: pedestal 1100 → 1420 mm linear + tilt -3 → +3° `inout_sine`, yaw 0, roll 0, focal 1280, aperture 10, focus 4114 | face-compositor limits (FACES §4.1): the r2 move slid a flat cut-out 9-62 %/s against the tiers (limit 3 %/s). **Approved.** The whole S3 world renders with this camera |
| 6 | S5-01 placement | bust bottom (470, 964) at screen (700, 1926) | **pinned at the beard: cut-out (470, 615) → screen (700, 1617)**, scale 0.750 → 0.7725 | at r2's anchor the beard fell to y ~1664 (inside the bottom 300 px). **Approved.** Use `LF.jd_rect(t)` for avoid rects, never the r2 fixed rect |
| 7 | S3 rays | the finish's rays 0.22 | `LF.s3_rays(cv, t, centre, r)` before the finish, then `rays=0` in the finish for 9.6-12.8 | JD's white tee / trainers became ray sources (R5) |
| 8 | captions | §15 r2 | adds `keep_pairs=(('log', 'kya'),)` and `clear=[(25.6, 25.9)]`; scroller avoid rect from the crowd module | keeps "apne log kya · *kahenge mein*" as written; no caption crosses the f768 cut + clunk (§6) |
| 9 | card flaps (S6-02) | "f960-~f1020, row by row" | each row flips up in **7 f**, landing on **f967 (rows 0-1), f975 (2), f982 (3), f984 (4, the 2-f-late row), f989 (5), f996 (6-7), f1004 (8), f1011 (9)** | locks the picture to the sound-designer's measured thups (`card_slide` 32.233 / 32.733 / 33.200 / 33.700 = f967 / f982 / f996 / f1011) |
| 10 | hook-B render folder | `<WS>/out/log_kya_kahenge_hookb` → `<RW>/out` (shared with A) | → **`<RW>/out_hookb`** (changed today) | render.py writes `sheet.jpg`, `cues.json`, `render_stats.json`, `parts_range/` with module-agnostic names: A and B would overwrite each other |
| 11 | QA checklist | BRIEF §18 r2 | §13 below (r3) | items 3-9 |

`packet.yaml` v2 still carries the r2 V2 text, V7 31.6 and `CAM_RISE` (lines 175, 184, 328, 346, 357, 362, 363, 388): superseded by
this table (non-blocking; the creative-director updates it at the next brief revision).

---------------------------------------------------------------------------------------------------------------

## 3. The final beat table (75 BPM: beat 24 f, bar 96 f = 3.2 s; DUR 35.2 s = 1,056 frames)

### 3.1 Bar by bar, with the measured VO

VO words = `<RW>/vo/lkk_vo_A.words.json` (= `words.json`) start times in reel seconds, `*` = caption keyword. "voice" = measured
envelope of `lkk_vo_A.wav` (20 ms RMS above peak - 45 dB). Caption times = the dry run in §6 (chunk enters → fully gone).

| bar · f (s) | shot · camera | picture (frame-exact) | on-screen text | VO (measured) | captions | SFX / music anchors | r3 |
|---|---|---|---|---|---|---|---|
| 0 · f0-95 (0.000-3.167) | S1-01 · `CAM_WIDE` locked | f0 tiers lit, heads **turned** (dark hair masses), cards sway ±0.3°; head-snap wave f6-f18, `t_s(x) = 0.200 + 0.400·|x-540|/540`, 3-f flip dark → light + eyes; f45 cover; f90 splice | `J.HouseTitle('LOG KYA', 'kahenge?', caps_px=86, key_px=210, underline=False)` at (540, 560), `t0=-0.1, out_t0=2.533`; gone f87 | V1 voice 0.100-2.520: Sab 0.090 · se 0.460 · bara 0.660 · \*darr 0.933 · log 1.330 · kya 1.755 · kahenge 1.955 | `Sab se` 0.04 → 0.61 · `bara *darr` 0.61 → 1.80 · "log kya kahenge" hidden | impact_soft f0 · swish_small 0.300 · lkk_whisper_swell peak 0.400 · shimmer 0.600 · wall -24 · dark_drone at loop pos 0 | none |
| 1 · f96-191 (3.200-6.367) | S2-01 · `CAM_WIDE` locked | J1 in f96 (at hold depth f106), J2 in f144 (f152), J3 in f180 (f186); crowd lean `1 + 0.03·in_sine((t-3.2)/6.4)` about each card's seat line | `c15_judge` 84 px at (540, 980), ≤ 2 lines visible | none | none | bursts 3.2 / 4.8 / 6.0 (-10 / -8 / -6) · whoosh_by 3.467 / 5.000 / 6.133 · wall -20 → -18 · tension_drone from 3.2 | none |
| 2 · f192-287 (6.400-9.567) | S2-01 | J4 in f216 (f222), holds 2.4 s; J3 gone f240; lean 1.030 at f287; O2 window f270-f305 | `c15_judge4` J4 until the smoke covers it (~f282) | V2 from 8.800: Hum 8.800 · \*zindagi 9.015 | `Hum *zindagi unke` 8.75 → 10.04 (scale 0.78, y 1390; dodges JD) | burst -4 7.2 · whoosh_by 7.333 · wall -26 from 8.95 | none |
| 3 · f288-383 (9.600-12.767) | S3-01 · **`LF.cam_s3(t)`** | O2 c f288 (smoke reveals JD); JD via `LF.draw_s3` inside the scene; lamp bank enters the top edge at ~10.8-11 s | none | unke 9.633 · hisaab 10.087 · se 10.487 · \*edit 10.742 · karte 11.051 · hain... 11.415 · jo 12.070 · poori 12.287 · \*video 12.633 | `hisaab se *edit` 10.04 → 11.00 · `karte hain...` 11.00 → 12.02 · `jo poori *video` 12.02 → 12.91 | whoosh_slow 9.6 · impact_soft 10.2 · rays via `LF.s3_rays` | camera (#5) |
| 4 · f384-479 (12.800-15.967) | S3-02 · `CAM_ROWS` ψ = 0 | L3 cut f384 (push 0.5); heads tilt 9° f384-f396, back f438-f450; drop-out lean 1.00 → 1.025 f456-f479 | none | dekhte 12.960 · bhi 13.487 · \*nahi 13.615; voice ends 14.040 | `dekhte bhi *nahi` 12.91 → 14.67 | board_flex + impact_soft 12.8 · reverse_swell ends 15.2 · wall cut 15.2 · heartbeat 15.6 · **music gated 15.2-16.0** | none |
| 5 · f480-575 (16.000-19.167) | S4-01 · `CAM_ROWS` orbit | ψ = 70·out_cubic((t-16)/3.2) f480 → f576; push 0.8 at 16.0 | none | V3: Yeh 16.357 (ψ 20.9°) · crowd 16.610 · \*flat 17.064 (ψ 49.2°) · hai 17.373 · \*Cardboard 18.200 (ψ 67.9°) | `Yeh crowd` 16.31 → 17.01 · `*flat hai` 17.01 → 18.15 · `*Cardboard` 18.15 → 19.28 | **braam + impact_big 16.0** (reveal, loudest) · board_flex 17.6 · pulse starts, Dm | none |
| 6 · f576-671 (19.200-22.367) | S4-02 · `CAM_ROWS` ψ 70 locked | single image f576-f599; focus pull f600-f624 (`inout_cubic`) to the scroller; one person looks up f640-f646; taps f648 / f654 / f660 | none | V4: Asli 19.333 · log 19.739 · peeche 20.067 · baithe 20.521 · hain 20.848 · apne 21.373 · \*phone 21.678 · mein 21.950; voice ends 22.250 | `Asli log` 19.28 → 20.02 · `peeche baithe hain` 20.02 → 21.32 · `apne *phone mein` 21.32 → 22.35 | whoosh_slow 19.2 · ui_tick 21.6 / 21.8 / 22.0 · Bb | none |
| 7 · f672-767 (22.400-25.567) | S4-03 / S4-04 · `CAM_ROWS` | O6 on the card layer f672-f719, c f708, `'btt'`; people never look up; last embers die f720-f767 | none | V5: Log 22.400 · \*busy 22.687 · hain... 23.051 (voice to 23.510) · pause · apne 23.667 · log 23.977 · kya 24.317 · \*kahenge 24.577 · mein 25.013; voice ends 25.330 | `Log *busy hain...` 22.35 → 23.62 · `apne log kya` 23.62 → 24.53 · `*kahenge mein` 24.53 → **25.60** (early exit, clear window) | ember_crackle 22.4 · whoosh_slow 23.0 · impact_soft + sub_drop 23.6 · reverse_swell → 25.6 · Gm/D, hats 22.8 / 23.6 / 24.4 | captions (#8) |
| 8 · f768-863 (25.600-28.767) | S5-01 · `CAM_JD` plate + `LF.draw_s5` | L3 cut f768 (push 0.6) + the one clunk; warm key `LF.key_gain(t)` (f768 0.6, f769 0.3, f770 0.9, f771 0.95, f772 1.0); push 1.00 → 1.03 | `J.HouseTitle('LOG', 'busy', caps_px=86, key_px=210)` at (430, 560), `t0=25.6, out_t0=28.433` + `HAIN.` (430, 781.3); keyword settled f793, underline done f806, gone f863 | V6: Kisi 25.970 · aur 26.293 · ki 26.693 · \*nazar 26.846 · mein 27.227 · hum 27.895 · bhi 28.104 · \*'log' 28.276 · hain 28.600; voice ends 28.960 (crosses f864) | `Kisi aur ki` 25.92 → 26.80 · `*nazar mein` 26.80 → 27.85 · `hum bhi` 27.85 → 28.23 · `*'log' hain` 28.23 → 29.64 (y 980, holds its place across f864) | clunk stack 25.597 / 25.600 · shimmer 25.833 · swish_small 26.167 · Bbmaj7, EP A4 26.4, F4 28.0 | placement (#6) |
| 9 · f864-959 (28.800-31.967) | S6-01 → S6-02 · `CAM_WIDE` locked | L3 cut f864 (push 0.4); warm low light from screen-left; last card tips f876-f888, tap f888; end card from **f936** | `E.EndCard` from 31.2 (§9) | silence 28.96-31.44; V7: Us 31.443 · dost 31.613 · ko 32.031 · \*bhejo 32.158 | none (hidden from 31.2) | impact_soft 28.8 · swish_small 29.2 · card_slide + lkk_card_tap 29.6 · end card swish 31.3 · shimmer 31.77 · glass_tap 31.95 · F/A, EP D4 30.4, C4 31.2 | V7 onset (#3) |
| 10 · f960-1055 (32.000-35.167) | S6-02 · `CAM_WIDE` | flaps (#9) f960-f1011, heads turned; warm light hands back to the floodlight f1008-f1050; rays ramp 0 → 0.22 over 33.6-35.0; card settled f992, exit f1045-f1055; `E.loop_world` f1041-f1055 | end card held f992-f1045 | jise 32.793 · 'log' 33.158 · ka 33.893 · darr 34.031 · rokta 34.377 · hai 34.795; **voice ends 35.070** | none | card_slide f967 / f982 / f996 / f1011 · wall back from 33.6 · reverse_swell ending 35.2 · Dm(add9), drone back 33.6 | flaps (#9) |

Hook B (frames 0-89 only; splice f90): BRIEF §6.2 unchanged. V1B measured: Yeh 0.090 · 'log'... 0.343 · asal 1.390 · mein 1.652 ·
hain 1.888 · \*kaun 2.125; voice 0.100-1.115 and 1.400-2.540 (ends ≤ 2.70, f81); lockup out_t0 1.733 →
gone f63; every V1B word hidden. B's words from 8.800 on are identical to A (checked).

Retention (series rule: a visible change ≤ 2.5 s apart): with the measured VO and the caption chunks above, the largest gap is
29.64 → 31.20 s (1.56 s; the tap at 29.6 sits just before it); 3.2-8.8 s has an event every ≤ 1.4 s (lines, hold-depth arrivals,
bursts) on top of the continuous lean.

### 3.2 VO vs picture: which visual beats move

**No picture event moves.** Every anchor was checked against the measured VO:

| anchor | BRIEF r2 plan | measured | decision |
|---|---|---|---|
| V1 end vs hook lockup exit (out_t0 f76 = 2.533) | V1 ≤ 2.70 | voice ends 2.520 | keep |
| V2 onset under J4's hold | 8.800 (f264) | 8.800 | keep |
| "jo poori video dekhte bhi nahi" on the tilt f384-f396 | lands on 12.8-13.2 | *video* 12.633, *dekhte* 12.960 | keep (the tilt lands between them) |
| V2 end before the heads straighten f438 | ≤ 14.833 | 14.040 | keep |
| V3 ≥ 300 ms after the reveal hit 16.0 | 16.367 | 16.370 (+370 ms) | keep |
| *flat* / *Cardboard* on the orbit | 16.96 at 46° / 18.2 at 68° | 17.064 at 49.2° / 18.200 at 67.9° | keep |
| focus pull f600-f624 on "peeche baithe" | 20.0-20.8 | 20.067-20.848 | keep |
| taps f648-f660 on "apne *phone* mein" | 21.6-22.0 | 21.373-22.223, *phone* 21.678 | keep |
| V5 on the bar-7 downbeat with the O6 start | 22.400 | 22.400 | keep |
| O6 c f708 inside V5's pause | 23.600 in the pause | pause 23.510-23.667 | keep (part 1 is 0.043 s past its 23.467 target; the pause still holds 23.6) |
| V5 end before the clunk guard 25.48 | ≤ 25.40 | 25.330 | keep |
| V6 ≥ 300 ms after the clunk 25.597 | 26.000 | 25.975 envelope / 25.970 word (+373 ms) | keep (VO_TIMING's 26.000 is the placed onset; words.json and the envelope say 25.97) |
| V6 end ≤ 29.10 and ≥ 0.1 s before the swish 29.2 | ≤ 29.10 | 28.960 | keep |
| V7 onset | f948 (31.600) | **f943 (31.433-31.443)** | **VO moved, picture kept**: the end card stays at f936 (bar 9 beat 3, SLATE); "Us dost ko" (31.443-32.158) now plays under the CTA caps rising (31.55-32.15), *bhejo* 32.158 as the keyword settles; the sub `jise 'log' ka darr rokta hai` fades in from 32.35, before "jise" (32.793) |
| V7 end ≤ 35.10 | ≤ 35.100 | 35.070 (loop gap to V1 0.227 s) | keep |

Measured no-VO windows (envelope): 2.85-8.80 none · 14.10-16.30 none · 15.85-16.30 none · 25.48-25.90 none · 29.10-31.43 none.

---------------------------------------------------------------------------------------------------------------

## 4. Every asset, with its path (each one checked with `ls` on 2026-10-09)

| asset | path | spec / use |
|---|---|---|
| VO stem, hook A | `<RW>/vo/lkk_vo_A.wav` (= `<RW>/vo/vo_stem.wav`) | pcm_s24le 48 kHz mono, 1,689,600 samples; -16.03 LUFS, -2.14 dBTP |
| VO stem, hook B | `<RW>/vo/lkk_vo_B.wav` | same format; -16.02 LUFS |
| word timings A / B | `<RW>/vo/lkk_vo_A.words.json` (= `<RW>/vo/words.json`), `<RW>/vo/lkk_vo_B.words.json` | list of `{word, start, end, keyword, line, i, hide, ...}`; `hide` is informational: `SC.load_words` ignores it, so build `HIDE` windows (§6) |
| VO QA picture | `<RW>/vo/vo_timeline.png` | |
| music bed | `<RW>/music/music_full.wav` (+ alias `<RW>/music/lkk_music.wav`) | pcm_s24le 48 kHz stereo, 1,689,600 samples, -16.0 LUFS, -3.3 dBTP, loop-exact, no end fade |
| music stems | `<RW>/music/stems/music_stem_{drums,bass,harmony,lead,fx}.wav` | sum to the mix within -132.5 dBFS |
| music metadata | `<RW>/music/music_full.json`, `<RW>/music/music_full.verify.json` | 33 events, measurements |
| SFX stem A / B | `<RW>/audio/log_kya_kahenge_sfx_stem.wav`, `<RW>/audio/log_kya_kahenge_hookb_sfx_stem.wav` | stereo 48 kHz, -18 LUFS, ≤ -2.0 dBTP, loop-exact |
| SFX cue lists | `<RW>/audio/log_kya_kahenge_cues.json`, `<RW>/audio/log_kya_kahenge_hookb_cues.json` | for `qa_measure.py cues` on the master |
| preview audio (until the final mix) | `<RW>/audio/log_kya_kahenge_roughloop_mix.wav`, `<RW>/audio/log_kya_kahenge_hookb_roughloop_mix.wav` | real VO + SFX + score through epic_mix, loop-padded: -14.00 LUFS, -2.21 dBTP, seam clean. **Previews only** |
| final mixes | `<RW>/audio/final/log_kya_kahenge{,_hookb}_{mix,vo_sfx,stem_vo,stem_sfx,stem_music}.wav` (+ `_mix.json`, `_mix.png`, `_zooms.png`); links `<RW>/audio/log_kya_kahenge_mix.wav`, `_vo_sfx.wav`, `_hookb_mix.wav`, `_hookb_vo_sfx.wav` → `final/` | written 2026-10-09; 48 kHz 24-bit stereo, 1,689,600 samples; rebuild: `tools/heavy.sh python3 log_kya_kahenge_mix.py all --hook AB` |
| faces module | `<P>/log_kya_kahenge_faces.py` (`import jawad_kit` first, then `import log_kya_kahenge_faces as LF`) | API in FACES.md §2 |
| face cut-outs (read by LF) | `/home/user/100/workspace/brand_reels/charsheet/cutouts/street_threequarter_turn.png` (+ `_depth.png`, `.json`), `.../cutouts/street_chinup_gaze.png` (+ `_depth.png`, `.json`) | never load them directly; LF does |
| SFX module | `<P>/log_kya_kahenge_sfx.py` | the reel module adopts nothing: `cues()` returns `[]` |
| music module | `<P>/log_kya_kahenge_music.py` | `build` / `verify` / `mix` |
| VO module | `<P>/log_kya_kahenge_vo.py` | rebuilds the stems; not imported by the reel |
| 3D props | none | BRIEF §13; no `assets3d_log_kya_kahenge.py`, no `<RW>/props/` |
| layout proofs (mock, r2 geometry) | `<RW>/layout_proofs/p1_hookA_cover_1.5s.jpg` … `p6_S3_jd_small_9.8s.jpg`, `layout_report.json` | ink boxes for every string |
| face test stills (stand-in worlds) | `<RW>/faces_test/stills/lkk_faces_f0288.png` … `lkk_faces_f0863.png`, `<RW>/faces_test/strip_beats.jpg` | the look reference for S3 / S5 |
| shared modules (read-only) | `<P>/jawad_kit.py`, `<P>/jawad_tx.py`, `<P>/jawad_grade.py`, `<P>/endcard.py`, `<P>/snake_captions.py`, `<P>/core.py`, `<P>/type3d.py`, `<P>/render.py`, `<P>/TOOLKIT.md` | |
| semaphore | `<P>/tools/heavy.sh` | every render / heavy job |
| QA tool | `/home/user/100/plugins/reels-studio/skills/reels-production-playbook/qa_measure.py` | probe, cues |
| render output folders | `/home/user/100/workspace/jawad_reels/out/log_kya_kahenge` → `<RW>/out`; `/home/user/100/workspace/jawad_reels/out/log_kya_kahenge_hookb` → `<RW>/out_hookb` (#10) | |
| to create (you) | `<P>/log_kya_kahenge.py`, `<P>/log_kya_kahenge_crowd.py`, `<P>/log_kya_kahenge_hookb.py`, `<RW>/gate/GATE.md`, `<RW>/captions/` | |

---------------------------------------------------------------------------------------------------------------

## 5. Module build notes (on top of BRIEF §7, §8, §10, §17)

**Scenes** (BRIEF §10.1): `SCENES = [S_A, S_B, S_C, S_D, S_E]`; `STEPS = [('O2', 9.6, dict(pre=18, post=18, seed=37, rise=320.0)),
('L3', 12.8, dict(push_gain=0.5)), ('L3', 25.6, dict(push_gain=0.6)), ('L3', 28.8, dict(push_gain=0.4))]`; `PLAN = X.Plan(STEPS)`.
Hook B: `[('O2', 2.4, dict(pre=15, post=12, seed=31, rise=260.0))] + STEPS`, scenes `[S_HB] + SCENES`.

**Cameras.** `CAM_WIDE = K.Cam(pos=(0, -1500, 2000), pitch=10, focal=1280, aperture=6, focus_dist=9000)` (lamp bank (5200, -13500,
15500) projects to (972.8, 171.5), checked). S3-01: **`LF.cam_s3(t)`** for the whole shot world (tiers, backdrop, bank); the bank's
projection runs (929.8, -73.8) at 9.6 → (920.0, 2.1) at 10.8 → (901.6, 153.1) at 12.767. `CAM_ROWS = K.Cam.orbit((3215, -2630, 8833),
16000, yaw=ψ, pitch=3, focal=7200, aperture=60, focus_dist=16000)`. `CAM_JD` per BRIEF §7.1. Focal-1600 fallback only if the §7.4
snap check fails (BRIEF §7.1).

**JD.** S3-01: `sc.custom(LF.S3_FEET, lambda c, cm: LF.draw_s3(c, cm, t))` inside the shot's `K.Scene`, floor drawn before him, haze
behind him only. S5-01: `LF.draw_s5(cv, t)` after the 85 mm plate, before the payoff lockup and captions; drive the plate's warm light
with `LF.key_gain(t)`. `LF.prewarm()` in `prewarm()`. No embers or particles in front of his face.

**O6 on the cards only** (BRIEF §10.3; request R1): split the scene renderer from the dispatcher so `o6_cards` never recurses:
`S_C_layers(t, part)` with `part in ('all', 'cards', 'nocards')` renders layers only; `S_C(t)` = `o6_cards(t)` inside
`X.TX['O6'].win(23.6, pre=36, post=12).inside(t)`, else `S_C_layers(t, 'all')`. `o6_cards` uses A = `S_C_layers(t, 'all')`,
B = `S_C_layers(t, 'nocards')`, spawn from `cards_t0()` (`@functools.lru_cache(1)`, `S_C_layers(22.4, 'cards')`), edge × card alpha.

**post** (FACES §2 wiring merged with BRIEF §17.2):
```python
CUTS = [(0.0, 0.6), (16.0, 0.8)]
def post(cv, t):
    r, c = rays(t), rays_centre(t)
    if LF.S3_T0 <= t < LF.S3_T1:              # 9.6-12.8: JD must not emit rays
        LF.s3_rays(cv, t, c, r); r = 0.0
    kw = merge(PLAN.post_kw(t), X.TX['O6'].post_kw(t, 23.6, pre=36, post=12, push_gain=0.3), card.post_kw(t, 31.2, DUR))
    return G.tx_finish(cv, t, LOOK, cuts=CUTS, rays=r, rays_center=c, **kw)   # merge: sum 'push', multiply 'bloom_scale'
```
`rays(t)`: 0.22 for 0-9.6 (`CAM_WIDE`, centre (973, 172)) and 9.6-12.8 (centre `LF.cam_s3(t).project(bank)`); 0 for 12.8-33.6;
`0.22·K.ramp(t, 33.6, 35.0, 'inout_sine')` for 33.6-35.2 at (973, 172). `noir_ember`'s own preset has `rays=0.0`, so pass it every frame.

**samples(t)**: BRIEF §10.2 (3 default; Plan windows; 7 for f480-f503, 5 for f504-f575; O6 `X.TX['O6'].samples_at(t, 23.6, pre=36, post=12)`;
card tip f876-f888 5; flaps f960-f1011 5).

**Flaps (#9):** row i lands at `L = (967, 967, 975, 982, 984, 989, 996, 996, 1004, 1011)[i]`, flips up over frames L-7 → L
(`in_cubic` up, a 2-frame settle, no bounce), heads turned. All cards up by f1011; the light hand-back f1008-f1050 then makes
S6-02 at f1041-f1055 match S1-01 at f0 (crowd up, heads away, floodlight on, rays 0.22, no text).

**Debug switches:** `LKK_NOTEXT=1` skips every text overlay and captions; `LKK_DEBUG=1` logs text blocks per frame (BRIEF §17.5).
`cues()` returns `[]`.

---------------------------------------------------------------------------------------------------------------

## 6. Captions plan (verified by a dry run of `SC.Captions` on the real words, hooks A and B: `cap.check() == []` for both)

```python
import snake_captions as SC
WORDS = '<RW>/vo/lkk_vo_A.words.json'        # hook B: lkk_vo_B.words.json
HIDE_A = ((1.28, 3.0), (31.2, 35.2))         # V1 "log" starts 1.330 - 0.05; end card (all of V7 starts >= 31.443)
HIDE_B = ((0.0, 2.52), (31.2, 35.2))         # all of V1B (last word ends 2.470 + 0.05)
cap = SC.Captions(WORDS, band='lower', avoid=avoid, hide=HIDE_A, keep_pairs=(('log', 'kya'),), clear=[(25.6, 25.9)])
```
Build the HIDE windows from the `hide` flags in words.json (as above); pass tuples (load_words is lru-cached). `avoid(t)` returns a list:
hook A lockup `(161, 332, 921, 710)` for t < 2.9 (hook B: `(234, 333, 847, 814)` for t < 2.1); `LF.jd_rect(t)` for 9.6-12.8 and
25.6-28.8; the scroller's projected head + phone bbox + 28 px for 20.0-22.4 (export `scroller_rect(t)` from the crowd module; the dry
run used a stand-in (512, 962, 708, 1198) around the BRIEF target (600, 1080)); the payoff lockup `(224, 332, 669, 841)` for
25.6-29.7, plus the held S5 rect `LF.jd_rect(28.7667)` = (329, 1149, 1074, 1916) for 28.8-29.7 (the last V6 chunk is gone at 29.64).

Chunks from the dry run (A; B is identical from 8.75 on and has no V1B chunk):

| chunk | in → gone (s) | y · scale | keyword |
|---|---|---|---|
| `Sab se` | 0.04 → 0.61 | 1270 · 1.00 | |
| `bara *darr` | 0.61 → 1.80 | 1270 · 1.00 | darr |
| `Hum *zindagi unke` | 8.75 → 10.04 | 1390 · 0.78 | zindagi |
| `hisaab se *edit` | 10.04 → 11.00 | 1270 · 0.85 (x 82-607, left of JD) | edit |
| `karte hain...` | 11.00 → 12.02 | 1270 · 1.00 | |
| `jo poori *video` | 12.02 → 12.91 | 1270 · 0.85 | video |
| `dekhte bhi *nahi` | 12.91 → 14.67 | 1270 · 1.00 | nahi |
| `Yeh crowd` · `*flat hai` · `*Cardboard` | 16.31 → 17.01 · → 18.15 · → 19.28 | 1270 · 1.00 | flat, Cardboard |
| `Asli log` · `peeche baithe hain` · `apne *phone mein` | 19.28 → 20.02 · → 21.32 · → 22.35 | 1270 / 1310 / 1350 | phone |
| `Log *busy hain...` · `apne log kya` · `*kahenge mein` | 22.35 → 23.62 · → 24.53 · → 25.60 | 1350 / 1270 / 1270 | busy, kahenge |
| `Kisi aur ki` · `*nazar mein` · `hum bhi` · `*'log' hain` | 25.92 → 26.80 · → 27.85 · → 28.23 · → 29.64 | 940 / 980 / 940 / 980 (band 841-1149) | nazar, 'log' |

Every chunk ink box sits inside x 70-930 and above y 1458 (lowest: `Hum *zindagi unke` y 1304-1458). Draw `cap.draw(cv, t)` after
`PLAN.draw` and the overlays, before `post`; `cap.prewarm()` in `prewarm()`. Save SRTs to `<RW>/captions/log_kya_kahenge_A.srt` /
`_B.srt` with `cap.save_srt`. Re-run `cap.report()` once `scroller_rect(t)` is real (only the three V4 chunks can move).

---------------------------------------------------------------------------------------------------------------

## 7. Transitions (jawad_tx names; ≤ 4 features, here O2 + O6★ public, + O2 in the Trial)

| # | id | window · cut | call |
|---|---|---|---|
| T0 | O2 smoke wipe (hook B only) | f57-f83, c f72 (2.4) | `('O2', 2.4, dict(pre=15, post=12, seed=31, rise=260.0))` → `X.TX['O2']` (`_tx_smoke`) |
| T1 | O2 smoke wipe | f270-f305, c f288 (9.6) | `('O2', 9.6, dict(pre=18, post=18, seed=37, rise=320.0))` |
| T2 | L3 exposure-push cut | c f384 (12.8), push 0.5 | `('L3', 12.8, dict(push_gain=0.5))` (`_tx_cut` + `_l3_post`) |
| T3 | in-shot orbit + push | f480-f576, push 0.8 at 16.0 | `K.Cam.orbit(...)` with `yaw=70*K.EASE['out_cubic'](K.clamp((t-16.0)/3.2))`; push via `CUTS` |
| T4 | O6 ember disintegration ★ (cards only) | f672-f719, c f708 (23.6), `'btt'` | local `o6_cards(t)` from `X._tx_embers` + `X.grid4, X.fbm, X.up, X.mix_mask, X._gl, X._emit, X._ember_ramp, X._inv_inout_sine, X.side_b`; post `X.TX['O6'].post_kw(..., push_gain=0.3)`; never `X.TX['O6'].cues()` |
| T5 | L3 cut + clunk | c f768 (25.6), push 0.6 | `('L3', 25.6, dict(push_gain=0.6))` |
| T6 | L3 cut | c f864 (28.8), push 0.4 | `('L3', 28.8, dict(push_gain=0.4))` |
| T7 | loop bridge | f1041-f1055 | `E.loop_world(world, t, DUR, d=0.5)`, `card.post_kw(t, 31.2, DUR)`, frame 0 `CUTS (0.0, 0.6)` |

Motion blur never crosses a cut: the Plan's HALF rule handles T1/T2/T5/T6; S_C's internal shot changes have no cuts.

---------------------------------------------------------------------------------------------------------------

## 8. End card (measured today with `endcard.EndCard`)

```python
SUB = "jise 'log' ka darr rokta hai"
card = E.EndCard('US DOST KO', 'bhejo', sub=SUB, monogram='JD', dur=4.0)
card.sub = T.render(SUB, 'jw_body', px=50.0); card._settled = None      # local sub_px override (request R2)
card.draw(cv, t, 31.2)                                                   # in draw(), after captions are hidden (31.2-35.2)
```
Start f936 (31.2); monogram from 31.3; CTA caps rise 31.55; keyword rises from 31.77; sub fades in 32.35-32.80; signature 32.2-32.65;
settled 33.05 (f992); hold 1.79 s to 34.84 (f1045); exit 34.84 → gone on f1055. Boxes: monogram 420-660 x 440-680; caps 262-818 x
738-798; keyword 350-730 x 858-1082; sub at 50 px 632.8 px wide (x 224-856, 74 px clear of x 930; at the default 56 px it would be
708.7 px, x 186-894, only 36 px clear); signature 411-669 x 1563-1587. The world under it is dimmed ×0.58 by the card.

---------------------------------------------------------------------------------------------------------------

## 9. Loop bridge

- Picture: `cv = E.loop_world(world, t, DUR, d=0.5)` with `world = lambda tt: PLAN.draw(tt, SCENES)`; t < 0 falls to `S_A`, which
  must render pre-snap state for t in [-0.5, 0): heads turned, cards up, floodlight on, lean 1.00, no text (overlays use the real t).
  Rays reach 0.22 by 35.0; `card.post_kw` pushes into the last 3 frames and frame 0 carries `(0.0, 0.6)`. Gate:
  `E.seam_report(lambda t: render.render_still(mod, t, 1), 35.2)['ok']`.
- Sound: the VO gap across the seam is 0.227 s (V7 voice ends 35.070, V1 starts 0.100); V7's *darr* (34.031) is answered by V1's
  *darr* (0.933). The SFX and music stems are loop-exact; the final mix must be loop-padded (R6c).

---------------------------------------------------------------------------------------------------------------

## 10. Commands (from `<P>`; **every** render.py call carries `--no-sfx-build` and either `--no-audio` or `--audio`)

Without them render.py's `ensure_sfx` builds `<WS>/audio/<reel>_sfx.wav` from `cues()` (empty here). Never run A and hook-B
renders at the same time.
```bash
H=tools/heavy.sh; RW=/home/user/100/workspace/jawad_reels/log_kya_kahenge; df -h /home/user/100   # 8.2 GB free today
$H python3 render.py log_kya_kahenge --stills 0.1,0.7,1.5,17.6,19.6 --workers 1 --no-sfx-build --no-audio      # gate (§7.4)
LKK_NOTEXT=1 $H python3 render.py log_kya_kahenge --stills 0.1,0.7 --workers 1 --no-sfx-build --no-audio      # snap numbers
$H python3 render.py log_kya_kahenge_hookb --stills 0.0,0.6 --workers 1 --no-sfx-build --no-audio
$H python3 render.py log_kya_kahenge --range 16.0 19.2 --workers 1 --no-sfx-build --no-audio                  # orbit gate
$H python3 render.py log_kya_kahenge --stills 9.6,11.2,12.7667,25.6,25.6333,25.7333,27.2,28.7667 --workers 1 --no-sfx-build --no-audio   # face re-measure (FACES §7)
$H python3 render.py log_kya_kahenge --sheet 24 --samples 1 --workers 1 --no-sfx-build --no-audio
$H python3 render.py log_kya_kahenge --preview --workers 1 --no-sfx-build --audio $RW/audio/log_kya_kahenge_roughloop_mix.wav
# after the music-supervisor's final mix exists:
$H python3 render.py log_kya_kahenge --workers 2 --no-sfx-build --audio $RW/audio/log_kya_kahenge_mix.wav     # master A
$H python3 render.py log_kya_kahenge_hookb --range 0 3.0 --workers 1 --no-sfx-build --no-audio                # hook-B frames
```
Splice B (frames 0-89 of `<RW>/out_hookb/log_kya_kahenge_hookb_0.00-3.00.mp4` + frames 90-1055 of `<RW>/out/log_kya_kahenge.mp4`,
one CRF 14 re-encode, muxed with `log_kya_kahenge_hookb_mix.wav`), then `qa_measure.py probe <mp4> --dur 35.2 --fps 30 --size 1080x1920`.

---------------------------------------------------------------------------------------------------------------

## 11. Open risks (owner · what to do)

1. **The crowd is unproven** (you). Nothing renders it yet; the §7.4 gate (snap ≥ 15 % head luma at 360 px, reads as people at 1.5 s,
   as cardboard at 19.6 s, clean orbit) runs before any animation. Two failed iterations → the lead swaps in reserve 2 (SLATE §3.5).
2. **S3 is a smaller move than the slate's "rise"** (you + viral-strategist): `cam_s3` rises 320 mm and tilts 6°; the stands slide
   ~160-180 px and the bank enters at ~10.8 s. Check on the 15 fps preview that it still reads as a rise.
3. ~~No final mix yet~~ **RESOLVED 2026-10-09** (music-supervisor): `log_kya_kahenge_mix.py` (deterministic; mono VO loaded L = R;
   4 s circular pad, so the crop is the steady-state loop) writes `<RW>/audio/final/` (versions A + B, stems) for both hooks.
   Numbers: `MUSIC_log_kya_kahenge.md` run 2 and `<RW>/audio/final/<name>_mix.json`.
4. ~~Music duck windows are stale~~ **RESOLVED 2026-10-09**: the score reads the windows from the VO stems at build time (V6
   25.970-28.990, V7 31.430-35.080); the C4 at 31.2 dips from 31.31 to -6 dB at 31.37 (measured -6.00 dB). `verify` re-run.
5. **LRA** (lead decision): final version A 3.4 LU (hook B 3.2), version B 5.7 (5.4) vs 5-9 (SLATE §5.1; `sound_design.md` §6 says
   2-8). Reaching 5 in A needs the music -12 dB in every no-VO gap (measured 5.3), muting the build's climax and the gag: not applied.
6. ~~Thin reveal margin~~ **RESOLVED 2026-10-09**: glue capped at 1.5 dB on 15.97-16.40 (R6b locally) + score -10 dB under the SFX
   reveal: the reveal (window 16.0-16.4) is 3.2 LU over the next loudest in mix A (4.1-4.9 in the others); limiter ≤ 3.35 dB.
7. ~~VO over the bed under V3 / V4~~ **RESOLVED 2026-10-09**: per-line top-up duck of the music (V3 +4.3, V4 +1.2, V5 +0.7 dB):
   every line ≥ 8.5 LU over music + SFX (lowest V3 8.51; overall 10.0).
8. **Listen before posting** (lead / Jawad): z/f in ज़िंदगी, बिज़ी, नज़र, फ़ोन, फ़्लैट (spectrograms say yes; ASR cannot tell); V1 may rise on
   "kahenge?" (BRIEF wants no rise); V7 ends on a full stop; V7 runs at 1.10x (outside the gate's 1.00-1.06x band). No listener exists in
   the pipeline.
9. **S5 rim outline** (face-compositor / colorist): on the stand-in stills I viewed (`lkk_faces_f0816.png`) the look-A outline glows as
   strongly on the right (dark) side of his hair and shoulder as on the lit left, which reads close to a sticker edge and softens the
   "right cheek falls off" light plot. Check on the real plate; if it reads as an outline, lower the right-side outline.
10. **`Hum *zindagi unke` at 0.78 scale** (50 px white words) to clear JD: legible, but the smallest chunk; QA lens (a) checks it at phone size.
11. **Whisper-wall ASR** (QA verifier): 2 of 12 transcriptions return Whisper's end-of-clip "Thanks for watching!"; the control shows the
    same on pink noise (SOUND §5): accept on that evidence.
12. **Disk and CPU**: 8.2 GB free on the shared disk; the full-render parts are CRF 8 yuv444p. Budget ≤ 1.2 s per sample-frame; ~3,700
    sample-frames on average 3.5 samples means roughly 35-45 min with 2 workers on a free box, longer under the shared load. Keep `<RW>`
    ≤ 2 GB (442 MB today).

---------------------------------------------------------------------------------------------------------------

## 12. Shared requests (`SHARED_REQUESTS.md`; every one is worked around locally, none blocks)

| id | module | ask | local workaround |
|---|---|---|---|
| R1 | `jawad_tx` O6 | `mask=` / `spawn=` | `o6_cards(t)` (§5) |
| R2 | `endcard.EndCard` | `sub_px=` | `card.sub = T.render(SUB, 'jw_body', px=50.0); card._settled = None` |
| R3 | `epic_music.render` | `fade_out=False` | own bus in `log_kya_kahenge_music.py` (done) |
| R4 | `vo_chain.edit_pauses` | tail extension + edge fades | `log_kya_kahenge_vo.edge_fades()` (done) |
| R5 | `core.god_rays` / `G.finish` | `rays_holdout=` | `LF.s3_rays` (§5) |
| R6 | `epic_mix.mix_reel` (filed as a second "R5", SOUND.md calls it R5a/b/c) | (a) mono VO, (b) glue protect windows, (c) `loop=True` | (a) stereo copy, (b) denser reveal in the SFX stem, (c) `_loop_mix` |

No new shared request from this handoff (the render-folder clash was local and is fixed, §2 #10).

---------------------------------------------------------------------------------------------------------------

## 13. QA acceptance checklist (r3; supersedes BRIEF §18 where they differ; two lenses + an independent verifier per major finding)

**Format and timing**
- [ ] ffprobe: 1080x1920, 30/1, `nb_frames` 1056, 35.200 s (±1 frame); audio 48 kHz, same duration; bt709.
- [ ] Cuts exactly at f288 (O2 c), f384, f768, f864 (frame n all-B, n-1 all-A); O6 c f708; end card starts f936.
- [ ] Hook B: frames 90-1055 of A and B bit-identical after decode (or PSNR ≥ 50 dB).

**Hook and structure**
- [ ] Frame 0: YAVG ≥ 38, ≥ 1 % of pixels Y ≥ 200 (lamp bank), motion on f0 (mean |blur(f1) - blur(f0)| > 0.15, Gaussian σ 3 px).
- [ ] Hook A caps ink by f15, keyword by f18, gone by f87; hook B text gone by f63.
- [ ] Head-snap: `LKK_NOTEXT=1` frames 3 and 21 (A), 0 and 18 (B) at 360 px: mean head-pixel luma change ≥ 15 % (eyes masked).
- [ ] Judgement lines start f96 / f144 / f180 / f216, sharp at hold depth by f106 / f152 / f186 / f222; ≤ 2 lines with opacity > 0.02;
      J3 gone by f240; lean 1.03 ±0.002 at f287, 1.00 from f288.
- [ ] **VO (measured r3 values)**: first voice ≤ 0.100 s; V1 voice ends ≤ 2.70 (2.520); V2 8.805-14.040; V3 from 16.370; V4 19.330-22.250;
      V5 22.400-25.330 with its pause containing 23.6; V6 from 25.975, ends ≤ 29.10 (28.960); **V7 from 31.440, last voice ≤ 35.10 (35.070)**;
      no voice in 15.85-16.30, 25.48-25.90 or **29.10-31.43**.
- [ ] A visible change ≤ 2.5 s apart everywhere (largest planned gap 1.56 s, 29.64 → 31.2).

**Copy, layout, legibility**
- [ ] Ink inside x 70-1010, y 230-1480 (end card to 1600); nothing at x > 930 in y 1050-1700; nothing textual below y 1620; boxes within
      ±6 px of BRIEF §8 and §8 here.
- [ ] ≤ 2 text blocks on every frame (`LKK_DEBUG` log); no caption inside a lockup or `LF.jd_rect`; contrast ≥ 4.5:1 per block.
- [ ] Captions = the §6 chunk list (V2 shows `Hum *zindagi unke`, never "apni"); **no chunk visible across f768**; `*'log' hain` keeps its
      position across f864; no V1B chunk in hook B; nothing from 31.2; `cap.check() == []`; highlight within ±1 frame of each onset.
- [ ] Spelling exactly as BRIEF §2 (house: bara, hai, nahi, mein, hain); IG line 2 = the r3 V2 text.

**Crowd, faces, light, colour**
- [ ] Gate stills passed, numbers signed in `<RW>/gate/GATE.md`.
- [ ] JD only f288-f383 and f768-f863; S3 camera = `LF.cam_s3` (yaw 0, roll 0, pitch -3 → +3°, pedestal 1100 → 1420 mm); S5 face bottom
      ≤ y 1617.3; halo over black ≤ +6 code values after the finish; no ray trail beside his legs; skin hue 8-29° on S5 face pixels.
- [ ] O6 masked: ≥ 98 % of particles start inside the card alpha; nothing else erodes.
- [ ] YMIN 16-22 on every 5 fps sample; no YAVG jump > 25 except at the pushes f384 / f480 / f768 / f864 (YMIN not rising there).
- [ ] `python3 jawad_grade.py verify <mp4> noir_ember`: red-orange ≥ 60 % of saturated pixels; mean SATAVG f768-f863 ≥ 1.5 × f480-f767.
- [ ] Flaps land on f967 / f975 / f982 / f984 / f989 / f996 / f1004 / f1011 (±1 frame vs the `card_slide` cues).
- [ ] No cricket / flag / religious / regional cue in any 5 fps sample.

**Sound** (on the final mixes, not the rough ones)
- [ ] -14.0 ±0.5 LUFS, TP ≤ -2.0 dBTP wav (≤ -1.5 after AAC); VO stem -16 LUFS; speech ≥ 8 LU over music (median voiced frames); LRA
      per the lead's decision (risk 5).
- [ ] Max momentary within ±0.2 s of 16.0; the 25.6 clunk ≥ 2 LU below it; one clunk only.
- [ ] Drop-out 15.2-16.0: music and wall ≤ -60 dBFS; ≤ 8 frames of digital silence.
- [ ] Hero onsets within ±1 frame (`qa_measure.py cues <master> <RW>/audio/log_kya_kahenge_cues.json`); EP notes inside V6/V7 dipped
      (measured windows, risk 4).
- [ ] Loop: no click at the seam (step ≤ 2× the local median); last vs first 50 ms RMS within 6 dB. (Music-supervisor, 2026-10-09: final
      mixes 1.29-1.36× the median; last vs first 50 ms +10.4 to +13.3 dB because the frame-0 `impact_soft` (SOUND cue 1) lands there;
      the score alone -1.1 dB. Open question for the lead in `MUSIC_log_kya_kahenge.md`.)

**Loop and end card**
- [ ] `E.seam_report(...)['ok']`; frame 1055 vs frame 0: crowd up, heads away, floodlight on, no text.
- [ ] End card settled by f992, held ≥ 45 f to f1045, exit in the last 0.36 s; sub at 50 px (632.8 px, x 224-856); `@jawad_mp4` present.
- [ ] Cover f45: keyword inside y 240-1680, legible at 240 and 210 px wide.

**Ops**
- [ ] `du -sh <RW>` ≤ 2 GB; intermediates deleted; only the §4 "to create" files written; no shared module edited; no commit.

---------------------------------------------------------------------------------------------------------------

## 14. Who runs next

1. **motion-timeline-builder**: `log_kya_kahenge_crowd.py` (+ `head_mask`, `eye_mask`, `scroller_rect`), `log_kya_kahenge.py`,
   `log_kya_kahenge_hookb.py`; gate stills + 360 px snap check + orbit range first; then sheet, preview (rough-loop audio).
2. ~~**music-supervisor** (in parallel): risks 3, 4, 7 → `log_kya_kahenge_mix.wav` / `_hookb_mix.wav` (loop-padded), `verify`.~~ Done 2026-10-09 (risks 3, 4, 6, 7).
3. **viral-strategist**: red-team the 15 fps preview (frame 0, change events, 360 px snap tiles, the S3 move).
4. **colorist**: noir_ember on the real frames (snap after the finish, the warm turn, rays, S5 skin and rim outline: risk 9).
5. **caption-designer**: re-run §6 with the real `scroller_rect`, SRTs.
6. Then the master A, hook-B range + splice, **motion-qa-reviewer** (§13), **delivery-packager**.
