# UI · Thoda Left... Bas Bas! (@jawad_mp4, Bijli series #2)

2026-10-12, UI/UX designer (caption-designer + brand-kit-builder roles). Module: `pipeline/jawad_reels/thoda_left_bas_ui.py`
(pure draw functions `fn(cv, t, ...)`, house canvas, look `gold_hour`). Continued from the previous team's committed
module (lockups, CRT picture, glass UI, phone, outro, cover were there; this pass made it VO-led, fixed the layout and
legibility over the real 3D plates, and added the ink scan + SRT). Selftest:

    cd pipeline/jawad_reels && tools/heavy.sh python3 thoda_left_bas_ui.py selftest [stills] [ink] [srt]
    -> workspace/jawad_reels/thoda_left_bas/ui_selftest/  (43 PNGs + _contact_360px.png, cover*.png, thoda_left_bas_{A,B}.srt)

Every PNG was looked at full size and at phone size (contact sheet); the fixes are in section 5.

## 1. VO-led timing (LEAD_DECISIONS 3)
All beats are parameters in reel frames, one table `UI.TM`. Three layers:
- `TIMING_SCRIPT` = SCRIPT.md r1 (1008 f, 72-f hook) = script.json (`check_script()` verifies words and plan frames).
- `TIMING_GRID` = that plan on the live grid. **The VO cut (VO_TIMING.md, 2026-10-11 23:01) is 1080 f with a 144-f hook**
  (V1 + V2 need 2 bars; everything after the hook +72). `set_grid(splice)` handles both; `vo_grid()` picks 144 when the
  measured V3 `Aaya?` starts after f120. `R(f)` maps an r1 frame. `NF`, `DUR`, `SPLICE`, `T_END` follow.
- `TM` = live: `derive_vo_timing()` at import from `workspace/jawad_reels/thoda_left_bas/vo/words.json` (else
  `brand_reels/assets/thoda_left_bas/vo_final/thoda_left_bas_vo_A.words.json`).

Rules: in-frame = floor(onset of the anchor word) - 1 (slams: the onset frame); kept at the grid frame if that leads the
word by <= 2 f (VO_TIMING 3); structural frames stay while the word follows within 12 f (H2 / C9 / C14 locks, R4 slam,
P1 payoff hit). Hold kept, extended to the last shown word + 6 f, cut to the next lockup (instant swap), min 14 f.
Captions without a VO line (R3, C7, C8, C12, C15) take the next free slot or are dropped (`TM[cid] = None`).
UI beats follow their words (T1 / X1 / P1b / P1c on V10, T2 = C14, E1 = C15, B0 = H3 + 9); edit-world shot starts
`S7` = min(C12, T1), `S8` = X1 + 9, `S9` = P1c + 18 (script relations).

    UI.retime(C9=310)                 # move a lockup, hold kept (t0, exit, jolt, M3 exit follow)
    UI.retime(C9=(310, 345))          # (in, last)
    UI.retime(C8=(360, 377))          # bring back a dropped caption
    UI.retime(SPLIT=(648, 666, 684, 702), S9=600, T_END=954)
    UI.retime(**UI.derive_vo_timing())    # back to the VO;  env TLB_UI_TIMING=script -> the r1 plan
    UI.vo_report()                    # lockup in-frame vs VO onset (printed by the selftest)

Picture-synced tables follow automatically (`_apply_picture_sync`): the yaw clock (hook swing 2 f before the H1b flip,
LOCK on H2, slip on B0; the f342-f413 gust/slip block rides with C10, the big swing with C11's M3 exit), the client
clock (X1 nudge, v27 lock = T2), revision arrivals, split words. `TLB_UI_TIMING=script` reproduces r1 exactly
(tested: TM, YAW_SEGS, WOBBLE, CLIENT identical).

### Live table (VO assemble 23:01, 1080-f grid)
| key | r1 | grid | live | VO word (onset f) | note |
|---|---|---|---|---|---|
| H1 / H1b | 0 / 18-35 | 0 / 36-70 | 0 / **64-88** | V1 `right...` 65.2 | chant holds to the H2 slam |
| H2 | 36-53 | 72-106 | **90-124** | V2 `Bas` 90.2 | LOCK + slam (peak capped, section 3) |
| H3 | 54-71 | 126-143 | **125-143** | V2 `Ab` 126.5 | tears out f135-f144 (L-cut: `hai!` crosses the splice) |
| B0 | 63 | 135 | **134** | | slip + client pill |
| R1 | 72-98 | 144-170 | **154-176** | V3 `Aaya?` 155.6 | |
| R2 (far) | 99-134 | 171-206 | **177-233** | V3 `Nahi!` 178.1 | |
| R3 (far) | 135-161 | 207-233 | **dropped** | (no VO line) | V3 runs to f229, V4 at f234: no slot |
| R4 | 162-197 | 234-269 | **234-268** | V4 `Kiska` 234.0 | slam stays |
| C5 / C6 | 198 / 225 | 270 / 297 | **269-310 / 311-372** | V5 `Thoda` 270.6 / `nahi` 312.5 | C6 holds through `wapas!` |
| C7 / C8 (far) | 252 / 288 | 324 / 360 | **dropped** | (V6 not in the VO) | V5 now covers S4: no slot |
| C9 | 306-341 | 378-413 | **378-421** | V7 `Ab` 381.0 | LOCK stays |
| C10 | 351-377 | 423-449 | **431-468** | V7 `Arre,` 432.0 | |
| C11 | 378-431 | 450-503 | **469-540** | V8 `Yeh` 470.3 | M3 exit f523-f540 |
| C12 | 432-467 | 504-539 | **541-576** | (V9 not in the VO) | rides over the T1 toast (different band) |
| T1 / X1 | 468 / 477 | 540 / 549 | **539 / 548** | V10 `Thoda` 540.2 | |
| P1b / P1c | 490 / 504 | 562 / 576 | **585 / 625** | V10 `thoda` 586.5 / `nahi,` 626.9 | phone S8 from f557 |
| S9 / C13 | 522 / 540 | 594 / 612 | **643 / 667-709** | V11 `Dialogue` 668.6 | |
| SPLIT (S10) | 576-647 | 648-719 | **None** | | no room between C13 (ends f709) and C14 (f720): see 6 |
| C14 / T2 | 648 | 720 | **720** | V12 `Bas` 720.0 | LOCK stays |
| C15 / E1 | 684 / 684-716 | 756 / 756-788 | 756 / 756-788 | (V13 not in the VO) | |
| P1 | 756-863 | 828-935 | **828-935** | V14 `Hum` 834.1 | payoff hit stays, the VO follows 6 f later |
| T_END / B1 | 882 / 990 | 954 / 1062 | 954 / 1062 | V15 `Aap` 977.9 | outro question under the VO |

## 2. Captions = designed on-screen text, not a transcript
The lockups stay as designed (SCRIPT 3, house type, two voices). With the VO the words are heard and read at once, so
no snake captions are added (SCRIPT 4: "the lockups already show the words"). The reel's `.srt` deliverable is the
transcript: `UI.save_srt(path, hook)` writes sentence mode from the measured VO words (one cue per line, <= 2 balanced
lines of <= 42 chars, phrase breaks preferred, 1-6 s, no overlaps): A 12 cues, B 11 cues, in house spelling.

## 3. Legibility + safe zones (measured)
The real Blender plates (previews, `RWS/out/preview3d`) are bright: golden-hour sky, cream distemper wall. Over them the
old lockups were unreadable (flame keyword additive glow vanishes on a bright sky; ASH far caps invisible). Fixes:
- **Ink bed** `bed(cv, layer, x0, y0)` under every lockup, the hook chant, far lines, split words and the cover: a
  shadow built from the glyph cores (dilated ~14 px, soft falloff + a wide 36 px skirt), darkness per pixel from the
  smoothed plate luminance so the plate under the glyph edges reaches linear 0.045 (0.30 grounding shadow on dark worlds,
  0.95 max). Invisible as a shape on dark worlds, a soft smoke shadow on bright ones.
- **Adaptive box scrim** (same SMOKE, rises with plate luminance, capped 0.55, wider feather) and a **plate-aware
  keyword halo** (`plate_halo`: 1.0 on dark worlds down to 0.2 on a bright sky, where it only lifts the plate).
- Contrast at the glyph edge (finished frame, `footage=1`, rays 0.12; core vs the 5-15 px ring): see the table in
  section 7.
- **Ink scan, every frame** (captions alone, hooks A + B, alpha > 0.1, glow cores included, scrims / beds excluded):
  see section 7. Fixed on the way: the H2 / C14 slam peak (1.14 x 846 px) reached x 64 -> the slam peak is capped at
  900 px wide; far lines started their rise at y 1480 (glyph bottoms y 1497) -> they rise 30 px into their line; the far
  scrim was counted as ink (scrim_k not passed through `captions()`).
- **Glass UI column** (x > 930 in y 1050-1700, the like / share column): rims and shadows of the full-width cards reached
  x 935-1020 -> viewer / timeline 0.78, rows 0.90, export 0.96, hook-B viewer 0.78, split viewer 0.72: 0 violations.

## 4. Layout (deviations from SHOTS c, all for the reasons given)
| element | SHOTS c | now | why |
|---|---|---|---|
| Viewer | 960 x 600 at (540, 780) | x 0.78 at (540, 870): y 636-1104, x 166-914 | every S7-S11 lockup (y 236-600) sat on the viewer header (`wahi hai.` on `Program 00:00`, `BAS BAS!` on the chips) |
| Timeline | 960 x 360 at (540, 1290) | x 0.78, same centre | right column |
| Revision rows | 560 x 64, y 1150-1450 | 780 x 60 at x 0.90, pitch 64, y 1150-1460 | right column; the existing row art |
| Export E1 | (540, 1250) | (540, 1280) x 0.96 | under the viewer |
| Toast T1 | drops to y 420 | drops 380 -> 505 | C12 now shares its window (VO cut) |
| X readout | jw_mono 30, chip 170 x 46 | jw_mono 36, chip 188 x 54 (card px) | the X 540 -> 538 nudge is a story beat; readable at 0.78 |
| C15 | caps 300 / key 460 / body 600 | 285 / 440 / 578 | body cleared the viewer top |
| H1 | caps 360 / key 535 | 330 / 505 (= H3 / C5 rhythm) | the keyword sat on the CRT shell top in the real A5 framing |
| H2 | y 470 | y 440 | `BAS BAS!` rested on the shell top |
| B0 (S1) | top right (790, 300) | lower left (330, 1440) on the CRT control strip | it crowded `AB` of H3 (the B1 copy over the outro stays top right) |
| Hook B viewer | (540, 1180) x 1 | (540, 1150) x 0.78 | right column |
| Split S10 | mini viewer (540, 1330) x 0.875, bubble (590, 1040) | (540, 1372) x 0.72, bubble (590, 1052) | bubble sat on the viewer header; right column |
| Cover | THODA 390 / key 565, pill top right, BAS BAS! 1500 | = frame 0 (330 / 505), pill on the snow half (700, 850), BAS BAS! 1490, @jawad_mp4 1580, ink bed | pill crowded THODA; signature unreadable on the lace |

## 5. Fixed after looking at the PNGs
1. Edit-world collisions (table above). 2. Unreadable type on the bright plates (section 3). 3. Payoff bed was a dark
blob behind `antenna` (wide halo fed the mask; box scrim at 0.85) -> glyph-core mask, scrim cap 0.55. 4. Hook chant
left a 12-f hole before the slam in the 144-f hook -> holds to H2 - 2. 5. SRT orphan words (`pehle | wala.`) ->
balanced phrase-break wrap. 6. Cover redone as frame 0 (section 4).

## 6. Open points for the lead / motion designer
1. **Grid:** the VO module (uncommitted, sound designer) moved the reel to 1080 f / 144-f hook; `thoda_left_bas_sfx.py`
   and `_music.py` still say 1008 f in their headers. This module follows the VO automatically (and `TLB_UI_SPLICE=72`
   forces r1). Please confirm the grid with the sound designer before stage 3.
2. **S10 TAB / AB split has no room** in the VO cut (V10 540-662 toast / phone, V11 668-709 C13, V12 720 C14): `SPLIT = None`
   (split_ui draws nothing, v23-v26 stack in S9). Options: (a) drop S10; (b) run the split on V10's own words
   (`thoda left / thoda right / nahi, pehle wala`) instead of the phone: `UI.retime(SPLIT=(540, 586, 626, 644), ...)`
   plus moving S8; (c) lengthen the cut.
3. **Dropped captions:** R3 `ULTA! DOOSRA LEFT!` and C7 / C8 `HAAN... HAAN...` / `BAS! BAS!` have no slot (no VO line;
   V3 and V5 now fill S2 / S4). `UI.retime(C8=(a, b))` brings one back if the picture is re-cut.
4. **C11 vs V8 words:** the lockup reads `YEH SCENE / khatam / nahi hua...`, Vlad says "Yeh scene **kabhi** khatam nahi
   hua." The lockup is designed text (kept as script.json), the SRT has the spoken line. Script writer to confirm.
5. **Grade:** draw captions after the world, before the finish (GRADE.md 1); bright full-bleed plates want
   `footage=1`; keep `gold_hour` rays <= 0.12 while a lockup is up (the default 0.26 veils the type by ~50 sRGB levels,
   beds included). Selftest uses exactly that (`PLATE_POST`, `PLATE_RAYS`).
6. The selftest composites the Blender **previews** with a plain homography into the screen quad (no stmap / refl /
   spill): layout and contrast only. The world module does the real passes; nothing changes here when finals land
   (`plate3d` prefers `RWS/assets3d/<name>/<variant>/` with meta.json).

## 7. Measurements (selftest 2026-10-12, VO grid)
- `script.json check: OK` (all caption / outro words; plan frames = r1). Timing mode `vo`, 61 VO words, grid 1080 f /
  splice 144 / T_END f954. Every anchored lockup lands 0-3 f before its VO word, except P1 (payoff hit f828 stays, V14
  `Hum` f834.1) - `selftest` prints the table (`VO <id> in f.. onset f.. lead ..`).
- **Ink scan, every frame, captions** (hooks A f0-f953 + B f0-f143): ink x 91-984, y 239-1461; max x in y 1050-1700:
  883; **0 violations** of x 70-1010 / y 230-1480 / column; max 2 text blocks at once. Exempt (designed): C11's M3 exit
  slides out of frame left f536-f540.
- **Ink scan, glass UI** (hook B + B0 + S7-S11 every 3 f, alpha > 0.25): max x in y 1050-1700: 922, **0 column
  violations** (x 119-984 overall; the y up to 1675 is the timeline sliding out at S9).
- **Edge contrast** (finished frame, previews + `footage=1`, rays 0.12; glyph core vs the 5-15 px ring around it):

  | frame | part | contrast |
  |---|---|---|
  | S12 f850 payoff | caps `HUM AAJ BHI` | 6.35:1 |
  | S12 f900 payoff | body `ghuma rahe hain.` | 3.65:1 |
  | S12 f850 payoff | key `antenna` (250 px) | 1.94:1 |
  | S2 f166 | key `Aaya?` (230 px) | 2.01:1 |
  | S6 f495 | caps `YEH SCENE` / key `khatam` | 6.80:1 / 2.05:1 |

  White caps pass 4.5:1. The flame keyword core itself is only linear L 0.36 (brand FLAME), so on the ungraded bright
  sky it reads by hue + the dark edge, but stays under the 3:1 hero target, and the payoff body line sits at 3.65:1
  over the brightest part of the sky. Visually clear at phone size (sheets), but **the S2 / S6 / S12 world grade should
  bring the sky behind the type band down about 1 stop** (motion designer / colorist); everything here adapts to it
  automatically. Dark worlds (CRT room at night, edit void, outro) are far above target.
- SRT A 12 cues / B 11 cues (VO words). Draw cost per caption frame 0.2-1.1 s at 2 threads (bed + band layers).

## 8. Interfaces for the motion designer (stage 3)
- `UI.captions(cv, t, hook='A')` every caption at t (draw after the world, before the finish); `UI.near / UI.far` single.
- `UI.tv_picture(t, sig, gdir, ...)` / `UI.tv_picture_at(t)` (810 x 1080 picture for the A5 / A6 stmap); `UI.sig(t)`,
  `UI.yaw(t)`, `UI.gdir(t)`, `UI.client(t)`, `UI.sig_c(t)` (live grid).
- `UI.edit_ui(layer, t)` + `UI.plane_warp(layer)` (S7 / S9 / S11), `UI.phone_screen(t)` (A7 stmap), `UI.split_ui(cv, t)`,
  `UI.hook_b(cv, t)` + `UI.snow_tear(cv, t)`, `UI.anachronism(cv, t)` (B0 at TM['B0']).
- `UI.outro()` -> `PO.ProfileOutro('Aap ke ghar antenna kaun ghumata tha?', key='Papa, bhai ya aap?', dur=4.2)`;
  `UI.outro_layer(cv, t)` draws it at `UI.T_END` + B1. `UI.cover(cv)` over `UI.cover_picture()` in the A5 screen;
  `UI.grid_crop(img)` (3:4 = y 240-1680; `cover_guides.png` shows crop, safe zone and column).
- Timing: `UI.TM`, `UI.retime(...)`, `UI.lockup_windows(hook)`, `UI.NF`, `UI.DUR`, `UI.SPLICE`.
- SRT: `UI.save_srt(path, hook)`.
