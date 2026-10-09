# HANDOFF · Reel 1 · C26 · Pehle Wala Hi Theek Tha · `pehle_wala` → motion-timeline-builder

Author: creative-director · 2026-10-09 (08:23-08:45 UTC) · For: reels-studio:motion-timeline-builder, who writes
`pipeline/jawad_reels/pehle_wala.py` and `pipeline/jawad_reels/pehle_wala_hookb.py` next.

**Binding order:** SLATE §0, §2, §3.1, §4, §5 → `BRIEF.md` r2 → **this file** (it re-times BRIEF r2 to the measured VO
and to the real Blender glass; where they differ, this file wins and says so) → `SCRIPT.md` / `VO_TIMING.md` for VO
text and word times → `SOUND.md`, `MUSIC_pehle_wala.md`, `FACES.md` for their own layers. Everything below was measured
in this session with the real files (scripts and proof images in
`/home/user/100/workspace/jawad_reels/pehle_wala/brief_proof/r3/`). Nobody on the team can listen; every audio
statement is a measurement.

---------------------------------------------------------------------------------------------------------------

## 0. Readiness on one screen

| layer | state | where |
|---|---|---|
| 3D prop `pw_chai_glass` | **READY** (13 frames + meta.json, loads via `S3.Asset3D`) | §3.1 |
| faces (`pehle_wala_faces.py`) | **READY** (API + 2 shots built; stills were on a stand-in world, re-shoot after your build) | §3.2 |
| VO (hook A + hook B stems, word JSON) | **READY** (measured; L9 decision taken here, §1 D1) | §2.2, §3.3 |
| SFX (`pehle_wala_sfx.py`, stems) | READY for previews; **one re-cue needed** after this hand-off (drawer move, §1 D2) | §3.4 |
| music (`music_full.wav`, `music_hookb.wav`, stems) | **READY** (16/16 checks) | §3.5 |
| final mix (Version A/B, both hooks) | **BLOCKED**: not built (music-supervisor run 2); LRA 2.3 vs SLATE 5-9 needs the lead (§10 R2) | §3.6 |
| captions plan | **READY** (solved on the measured words, `check() == []` for A and B) | §5 |
| transitions, end card, loop | **READY** (plan windows, post values and card numbers verified) | §6-§8 |
| `pehle_wala.py` / `pehle_wala_hookb.py` | **NOT STARTED** (your job) | §9 |

---------------------------------------------------------------------------------------------------------------

## 1. Decisions taken in this hand-off (changes against BRIEF r2, each measured)

| # | what changes | from (BRIEF r2) | to (build this) | why (measured) |
|---|---|---|---|---|
| D1 | L9 / D7 (VO_TIMING §5 asked the CD) | - | **option (a): keep the D7 at f640 (21.333)**; the pins stay on the 16-frame grid | Vlad's shortest valid count runs 19.233-21.683 (6 takes, 4 prompt forms; no fragment under ~0.70 s). The full D7 lands 63 ms after the onset of the last "ek." (21.270): the chroma shock punctuates the end of the count on the bar-10 downbeat (drums, 8 px shake). The three fragments still follow pins: "Aur" +1 f after pin 20 (f576), "aur" 0.7 f before pin 22 (f608), "aur" +5.2 f after pin 23 (f624); pins 21 (f592) and 24 (f640) land inside an "ek" (dark thocks in SOUND.md). The SFX are already built for (a) |
| D2 | **version drawer entry** | slides in at **f640** (21.333) with rows v24, v25; row v26 at f656 | slides in at **f656 (21.867)** with rows **v24, v25, v26** already in; row v27 still slides in at f672; exit unchanged f696-f704 | L9 now ends 21.683, so a caption chunk is on screen at f640: pin card + drawer + caption = 3 text blocks (rule: ≤ 2). Moving the drawer one beat (to pin 25's landing) fixes it with the caption clear window D3 |
| D3 | **caption clear window** | none | `clear=[(21.8667, 23.40)]`: chunk 12 "aur *ek*" exits 21.617-21.867 (in_cubic 0.25 s) and is gone on f656 | built-in `snake_captions` clear rule; `CAP.check() == []` with it (hook A and B) |
| D4 | **glass placement** (one of the two prop layout numbers) | base centre at screen (515, **1210**), "440 px tall" | base centre (anchor) at **(515, 1190)**; contact shadow (515, **1192**); steam rises from the rim opening (515, **768**) and still fades out by y 560 | the real sprite's foot reaches 55.2 sprite px (25.0 screen px) below the anchor: at 1210 the foot ends at y 1235, past the ad rect bottom (1228), so frame 0's premium ad had a cut foot (proof `glass_anchor_A1210_B1190.jpg`, left). At 1190 the foot ends at 1215 (13 px inside) at push 1.0 |
| D5 | **glass scale** (the other prop layout number) | "440 px" (the faces proof used 440 / (base - rim centre) = 0.4732) | **k = 440 / 969.8 = 0.453702** (meta `glass_height_px`: base centre to the top of the alpha bbox = rim back lip). Screen size at push 1.0: 317 x 465 px (x 356-673, y 750-1215) | "440 px tall" means base to the top of the glass (BRIEF §5.2 "top ~770" at base 1210 = 440 px). 0.4732 makes the glass 4.3 % too big |
| D6 | **ad keyword *garam* size** | `jw_key` **120 px**, right edge x 900, centre y 1150 (ink x 601-897) | `jw_key` **100 px**, same right edge and centre: ink **x 651-898, y 1125-1207**; parody (v10+) `pw_parody_fun` **112 px** (was 130) | at 120 px the "g" sits on the glass's base edge for every yaw (902 px of overlap; proof `garam120_collision_crop.jpg`). At 100 px the gap to the union of all 13 yaw frames is 16.2 px at push 1.0, ≥ 8 px to push 1.04 (s 3.9 s), ≥ 3 px to push 1.08 (s 8.1 s); contact from push ≈ 1.10 (s ≈ 10.3 s, the clutter phase: parody font from 10.667, letterbox from 14.933) - accepted. Shadow (+14) right edge 912 ≤ 914, shake (+8) 920 ≤ 922 (rule x ≤ 930) |

Everything else in BRIEF r2 stands. **Beats checked against the measured VO and NOT moved** (each verified): hook A
lockup exit 2.233-2.583 (L1 ends 2.270, "change." 1.709-2.270 is spoken while CHANGE is on screen); pin 2 f64 lands
inside "change." (dark thock, picture unchanged); pin 3 f96 then L2 "Ho" f98 (the editor answers the note); L4 "Clean."
starts f202 as the cream completes (f204); pin 6 f224 inside "Clean." (dark thock); L7 ends 14.657 before the braam
(14.933); tile S4-01 f448 under "Bilkul" (15.000); the hover f704 with L10 "Phir" f705; L10 ends 24.930 before the
drop-out (25.067); no VO 24.930-28.133 (payoff, rewind, restore clear); L11 now ends 31.993 (was 31.361) under the
end card (no element depends on it); client marker re-entry **f979 stays** (L12 "...aur" starts f978, 32.600, 1 frame
before it); L12 ends 34.050 (DUR - 0.083 s).

---------------------------------------------------------------------------------------------------------------

## 2. Final beat table (frame-exact; 112.5 BPM, 16 f/beat, 64 f/bar; DUR 34.1333 s = 1,024 f; hook A body)

Columns: f = frame (t × 30); grid = bar.beat (+ frames); VO = measured words (`vo/words.json`); cap = caption chunk
from §5; SFX/music = the anchor sounds for sync QA (the full sheet is `pehle_wala_sfx.cues()`, SOUND.md §3; never
draft cues in the module). **Bold** = changed by this hand-off.

| f | t (s) | grid | picture | transition | VO (measured) | cap | SFX / music anchor |
|---|---|---|---|---|---|---|---|
| 0 | 0.000 | 0.0 | v1 ad (glass at base (515, 1190), *garam* 100 px), chip Approved, counter v1, HA1 caps rising (t0 -0.1), client marker mid-glide at (618, 443) | frame-0 push `cuts=[(0.0, 0.6)]` | - | hidden 0-2.667 | impact_soft; score bar 0 Dm, soft kick f0 |
| 3 | 0.100 | 0.0+3 | - | | L1 "Bas" 0.100-0.468 | | |
| 5 | 0.167 | 0.0+5 | marker reaches (470, 424), hands over to pin 1's own 48 px fall | | | | |
| 8 | 0.267 | 0.0+8 | pin 1 lands on the logo, card "Logo thora bara?" | pin tick (rgb_split 0.25) | inside "Bas" | | pin_thock_dark |
| 12 | 0.400 | 0.0+12 | chip → "Changes requested" (POP) | | "ek" 0.468-0.870 | | ui_click |
| 16 | 0.533 | 0.1 | lockup readable (keys from 0.12 s), underline 0.45-1.15 | | | | shimmer |
| 32 | 1.067 | 0.2 | v2: logo ×2 (POP), counter v2 | | "chhota" 1.000-1.524 | | pop, slot_tick |
| 64 | 2.133 | 1.0 | pin 2 "Aur bara.", logo ×3, counter v3 | pin tick | inside "change." 1.709-2.270 | | pin_thock_dark, whoosh_fast; bar 1 Bb + hats |
| 67-78 | 2.233-2.583 | 1.0+3 | hook lockup + scrim exit (in_cubic 0.35 s) | | L1 ends 2.270 | | |
| 80 | 2.667 | 1.1 | **splice frame** (hook A = hook B from here) | | gap 2.270-3.267 | live from 2.667 | |
| 96 | 3.200 | 1.2 | pin 3 "Thora left.", logo -72 px | pin tick | L2 "Ho" 3.267 (f98) | 0 "Ho *jayega*" in 3.217 | pin_thock (full) |
| 128 | 4.267 | 2.0 | pin 4: saturation spike; GOLD NEW burst POPs f130 | **L3** push 0.5 (f128-f131) | "jayega." ended 4.227; L3 "Pop?" 4.400 (f132) | 1 "*Pop?*" 4.350 | flash_hit, pin_thock_dark; bar 2 F + strings |
| 192 | 6.400 | 3.0 | pin 5: cream fills the ad rect f192-f204 | pin tick | gap (L3 ended 6.117) | 4 "*Clean*" 6.683 | pin_thock (full), downlifter; bar 3 C, hats out |
| 202 | 6.733 | 3.0+10 | cream completes f204 | | L4 "Clean." 6.733-7.533 | | |
| 224 | 7.467 | 3.2 | pin 6: steam cartoon outline | pin tick | inside "Clean." | | pin_thock_dark; taiko fill 7.467-8.533 |
| 256 | 8.533 | 4.0 | pin 7: 5 px beat shake starts | pin tick | L5 "Energetic." 8.600-9.570 | 5 "*Energetic*" 8.550 | pin_thock, impact_soft; bar 4 drums in |
| 288 | 9.600 | 4.2 | pin 8: 4 sparkles | pin tick | 30 ms after "Energetic." | | pin_thock_dark, sparkle |
| 320 | 10.667 | 5.0 | pin 9: *garam* → parody **112 px**, wobble ±4° | pin tick | L6 "Fun." 10.800-11.550 | 6 "*Fun*" 10.750 | bubble_pop, pin_thock; bar 5 Bb + 808 |
| 352 | 11.733 | 5.2 | pin 10: hard drop shadows | pin tick | gap | | card_slide, pin_thock |
| 384 | 12.800 | 6.0 | **RE-HOOK**: Mummy pin, thread card 1, glitter border | **D7** full (f384-f386) | L7 "Ab" 12.867 (f386) | 7 "Ab *Mummy* bhi" 12.817 | glitch_short, whip, pin_thock_mummy; bar 6 F, drums out 2 beats |
| 400 | 13.333 | 6.1 | thread card 2: cream back to dark | pin tick | inside "Mummy" 13.131-13.594 | 8 "review karengi" 13.692 | pin_thock_mummy_dark |
| 416 | 13.867 | 6.2 | thread card 3: glitter ×2 | pin tick | inside "review" 13.742-14.057 | | pin_thock_mummy_dark |
| 432 | 14.400 | 6.3 | thread card 4: logo ×1.25 | pin tick | inside "karengi." 14.057-14.657 | | pin_thock_mummy_dark |
| 448 | 14.933 | 7.0 | pin 15: letterbox, flares, slow steam; tile S4-01 `street_sunglasses` f448-f511 | **L3** push 0.6 (f448-f451) | L8 "Bilkul" 15.000 (f450) | 9 "Bilkul *cinematic*" 14.950 (scale 0.78) | braam (start 14.911), flash_hit, pin_thock; bar 7 C half-time |
| 480 | 16.000 | 7.2 | pin 16: 50% OFF SLAM | pin tick | inside "cinematic." 15.590-16.420 | | pin_thock_dark, card_slide |
| 496 | 16.533 | 7.3 | pin 17: steam ×3 | pin tick | gap | | pin_thock, whoosh_slow |
| 502-511 | 16.733-17.033 | 7.3+6 | tile exit (in_cubic, y +24; gone by f511.5) | | | | |
| 512 | 17.067 | 8.0 | pin 18: everything ×1.2 (50 % pattern break) | **L3** push 0.4 (f512-f515) | gap | | air_zoom, flash_hit, pin_thock; bar 8 Dm +1.9 LU |
| 544 | 18.133 | 8.2 | pin 19: CALL NOW SLAM | pin tick | gap | | card_slide, pin_thock |
| 576 | 19.200 | 9.0 | pin 20: burst 2; clock chip "3:47 AM" POPs | pin tick | L9 "Aur" 19.233 (f577) | 10 "Aur ek" 19.183 | pin_thock_dark; clock_tick from f584; bar 9 Bb |
| 592 | 19.733 | 9.1 | pin 21: logo ×1.2 | pin tick | inside "ek," 19.564-20.213 | | pin_thock_dark |
| 608 | 20.267 | 9.2 | pin 22: shadows to 0.42 | pin tick | "aur" 20.243 (fragment 2) | 11 "aur ek" 20.193 | pin_thock_dark |
| 624 | 20.800 | 9.3 | pin 23: shadows back | pin tick | inside "ek," 20.525-20.943 | 12 "aur *ek*" 20.923 | pin_thock_dark |
| 640 | 21.333 | 10.0 | pin 24: shake 8 px; **no drawer yet** | **D7** full (f640-f642) | inside "ek." 21.270-21.683 (D1) | 12 | glitch_short, whip, pin_thock_dark -8; bar 10 F peak |
| 648-656 | 21.617-21.867 | 10.0+8 | **chunk 12 early exit (clear window)** | | VO gap 21.683-23.500 | gone on f656 | |
| 656 | 21.867 | 10.1 | pin 25 "Thora left."; **drawer slides in (up 40 px + POP) with rows v24, v25, v26** | pin tick | | | pin_thock, slot_tick, card_slide (**= drawer entry, re-cue**) |
| 672 | 22.400 | 10.2 | pin 26 "Thora right."; row v27 slides in (x +60, 6 f); **counter v27** | pin tick | | | pin_thock, card_slide |
| 696-704 | 23.200-23.467 | 10.3+8 | drawer + clock chip exit (8 f, in_cubic, y +40) | | | | |
| 704 | 23.467 | 11.0 | the last pin hovers, undecided; shake fades by 24.0 | | L10 "Phir" 23.500 (f705) | 13 "Phir *aakhri* message..." 23.450 | shepard_riser, ui_hover, heartbeat (last lub f740); bar 11 C thinning |
| 748 | 24.930 | 11.2+12 | | | L10 ends ("message..." 24.380-24.930) | 13 holds to 25.280 | |
| 752 | 25.067 | 11.3 | **DROP-OUT**: marker freezes, steam ×0.2 | | none | 13 exits 25.280-25.580 | digital zeros f752-f759 (mix + stems, measured) |
| 760 | 25.333 | 11.3+8 | held breath | | | | clock_tick, bed -40 |
| 768 | 25.600 | 12.0 | **PAYOFF**: marker slams on the glass (515, 900); card "Pehle wala hi theek tha." (56 px) | **L3** push 1.0 (f768-f771) | none | none | pin_thock_big, sub_drop, flash_hit (max momentary of the rough mix -9.11 LUFS at 25.80) |
| 784 | 26.133 | 12.1 | Ctrl+Z press, chip "Ctrl+Z ×26" POPs; world live f784-f789 | **D9** window f784-f833 | none | none | typing; music tape-stop 26.133 (0.4 s) |
| 790-831 | 26.333-27.700 | 12.1+6 | rewind `W_core(tau)`, desat 30 %, zoom blur 0.02, counter spinning down, pins un-landing (§6) | D9 | none | | pw_tape_rewind (hit 27.718) + 19 ui_ticks 27.078-27.698 |
| 832 | 27.733 | 13.0 | **RESTORE** = `P(t)`: v1 pristine, Approved, v1; PO1 rises per glyph; Ctrl+Z chip exits f832-f838 | D9 cut + push 0.6 | none | | impact_soft, glass_tap (D6); bar 13 = score bar 0 |
| 836 | 27.867 | 13.0+4 | tile S6-01 `street_smirk` f836-f895 | | | | |
| 835-854 | 27.833-28.483 | 13.0+3 | PO2 rises; underline 27.983-28.483; *garam* dims to ×0.35 over 27.733-28.233 | | L11 "Har" 28.133 (f844) | 14 "Har editor" 28.083 | swish_small, shimmer |
| 855 | 28.500 | 13.1+7 | **cover frame** (render with `PW_CAPTIONS=0`) | | "editor" 28.408-28.889 | (off for the cover) | |
| 886-895 | 29.533-29.833 | 13.3+6 | payoff lockup + tile exit | | "hai," 29.371-29.723 | 15 "jaanta hai" | |
| 896 | 29.867 | 14.0 | **END CARD** t0 (`EndCard`, §7) + local player dim | | "v1" 29.873 (f896) | 16 "v1 hi" 29.823 | card cues; glass_tap -16 at 30.617 under "hi"; bar 14 Bb |
| 952 | 31.717 | 14.3+8 | card settled (hold 2.057 s to 33.773) | | L11 ends 31.993 ("hai." 31.639-31.993) | 17 "final hota hai" 30.700-32.463 | |
| 978-979 | 32.600-32.633 | 15.1+2 | **client marker re-enters f979** (§6.3.1 of the brief, unchanged) | | L12 "...aur" 32.600 (f978) | 18 "...aur phir" 32.550 | ui_hover -14 hp 5000 at 32.633 |
| 1013 | 33.773 | 15.3+5 | card exit (0.36 s) + caption fade + marker glide toward the logo | | "client" 33.042-33.431, "ne", "bola" 33.579-34.050 | 19 "client ne bola" (faded by the loop ramp) | reverse_swell ends on DUR |
| 1021-1023 | 34.033-34.100 | 15.3+13 | loop push 0 / 0.075 / 0.6 (`CARD.post_kw`) | | L12 ends 34.050 (f1021.5) | | |
| 1024 = 0 | 34.133 | 16.0 | loops to f0 (marker one frame step on) | frame-0 push | → L1 at 0.100 | | → impact_soft, bar 0 Dm |

Hook B head (`pehle_wala_hookb.py`, f0-f79; BRIEF §7.2 unchanged): raw v27 mess f0-f11, focus panel f12-f20, key "26"
from f9, caps 0.50-1.10, D1 f40-f79 cut f70 (2.333). Measured L1B words: "26" 0.100-0.625 · "revision" 0.625-1.051 ·
"baad" 1.051-1.580 · "client" 1.640-1.980 · "ne" 1.980-2.129 · "kaha..." 2.129-2.580 (≤ 2.70 gate; the D1 cut f70
lands inside "kaha..."). L2 "Ho" at 3.267 (f98) after the splice, so it cannot read as the client's words.

### 2.1 Text blocks per window (replaces BRIEF §5.3; UI chrome not counted; a pin card handing over to the next pin card is ONE block slot)

| window (s) | blocks |
|---|---|
| 0-2.667 | pin card + hook lockup (captions hidden) |
| 2.667-12.8 | pin card + captions |
| 12.8-14.933 | Mummy thread + captions |
| 14.933-21.333 | pin card + captions |
| **21.333-21.867** | **pin card + captions (chunk 12, exits by f656)** |
| **21.867-23.467** | **pin card + version drawer** |
| 23.467-25.6 | captions only (chunk 13 gone by 25.580) |
| 25.6-26.133 | payoff pin card |
| 26.133-27.733 | Ctrl+Z chip + at most one rewinding pin card (or the Mummy thread) |
| 27.733-29.867 | payoff lockup + captions |
| 29.867-34.133 | end card + captions |

### 2.2 Measured VO words, hook A (`vo/words.json`, = `pehle_wala_vo_A.words.json`; all 45 tokens `ok`)

| line | word | key | start s | end s | start f | end f | grid |
|---|---|---|---|---|---|---|---|
| L1 | Bas |  | 0.100 | 0.468 | 3.0 | 14.0 | 0.0+3.0 |
| L1 | ek |  | 0.468 | 0.870 | 14.0 | 26.1 | 0.0+14.0 |
| L1 | chhota | yes (hidden) | 1.000 | 1.524 | 30.0 | 45.7 | 0.1+14.0 |
| L1 | sa |  | 1.524 | 1.709 | 45.7 | 51.3 | 0.2+13.7 |
| L1 | change. |  | 1.709 | 2.270 | 51.3 | 68.1 | 0.3+3.3 |
| L2 | Ho |  | 3.267 | 3.523 | 98.0 | 105.7 | 1.2+2.0 |
| L2 | jayega. | yes | 3.523 | 4.227 | 105.7 | 126.8 | 1.2+9.7 |
| L3 | Pop? | yes | 4.400 | 4.840 | 132.0 | 145.2 | 2.0+4.0 |
| L3 | Kisi |  | 5.090 | 5.340 | 152.7 | 160.2 | 2.1+8.7 |
| L3 | ko |  | 5.340 | 5.488 | 160.2 | 164.6 | 2.2+0.2 |
| L3 | nahi |  | 5.488 | 5.673 | 164.6 | 170.2 | 2.2+4.6 |
| L3 | pata. |  | 5.673 | 6.117 | 170.2 | 183.5 | 2.2+10.2 |
| L4 | Clean. | yes | 6.733 | 7.533 | 202.0 | 226.0 | 3.0+10.0 |
| L5 | Energetic. | yes | 8.600 | 9.570 | 258.0 | 287.1 | 4.0+2.0 |
| L6 | Fun. | yes | 10.800 | 11.550 | 324.0 | 346.5 | 5.0+4.0 |
| L7 | Ab |  | 12.867 | 13.131 | 386.0 | 393.9 | 6.0+2.0 |
| L7 | Mummy | yes | 13.131 | 13.594 | 393.9 | 407.8 | 6.0+9.9 |
| L7 | bhi |  | 13.594 | 13.742 | 407.8 | 412.3 | 6.1+7.8 |
| L7 | review |  | 13.742 | 14.057 | 412.3 | 421.7 | 6.1+12.3 |
| L7 | karengi. |  | 14.057 | 14.657 | 421.7 | 439.7 | 6.2+5.7 |
| L8 | Bilkul |  | 15.000 | 15.590 | 450.0 | 467.7 | 7.0+2.0 |
| L8 | cinematic. | yes | 15.590 | 16.420 | 467.7 | 492.6 | 7.1+3.7 |
| L9 | Aur |  | 19.233 | 19.564 | 577.0 | 586.9 | 9.0+1.0 |
| L9 | ek, |  | 19.564 | 20.213 | 586.9 | 606.4 | 9.0+10.9 |
| L9 | aur |  | 20.243 | 20.525 | 607.3 | 615.8 | 9.1+15.3 |
| L9 | ek, |  | 20.525 | 20.943 | 615.8 | 628.3 | 9.2+7.8 |
| L9 | aur |  | 20.973 | 21.270 | 629.2 | 638.1 | 9.3+5.2 |
| L9 | ek. | yes | 21.270 | 21.683 | 638.1 | 650.5 | 9.3+14.1 |
| L10 | Phir |  | 23.500 | 23.880 | 705.0 | 716.4 | 11.0+1.0 |
| L10 | aakhri | yes | 23.940 | 24.380 | 718.2 | 731.4 | 11.0+14.2 |
| L10 | message... |  | 24.380 | 24.930 | 731.4 | 747.9 | 11.1+11.4 |
| L11 | Har |  | 28.133 | 28.408 | 844.0 | 852.2 | 13.0+12.0 |
| L11 | editor |  | 28.408 | 28.889 | 852.2 | 866.7 | 13.1+4.2 |
| L11 | jaanta |  | 28.889 | 29.371 | 866.7 | 881.1 | 13.2+2.7 |
| L11 | hai, |  | 29.371 | 29.723 | 881.1 | 891.7 | 13.3+1.1 |
| L11 | v1 |  | 29.873 | 30.490 | 896.2 | 914.7 | 14.0+0.2 |
| L11 | hi |  | 30.490 | 30.750 | 914.7 | 922.5 | 14.1+2.7 |
| L11 | final |  | 30.750 | 31.305 | 922.5 | 939.1 | 14.1+10.5 |
| L11 | hota |  | 31.305 | 31.639 | 939.1 | 949.2 | 14.2+11.1 |
| L11 | hai. |  | 31.639 | 31.993 | 949.2 | 959.8 | 14.3+5.2 |
| L12 | ...aur |  | 32.600 | 32.783 | 978.0 | 983.5 | 15.1+2.0 |
| L12 | phir |  | 32.783 | 33.042 | 983.5 | 991.3 | 15.1+7.5 |
| L12 | client |  | 33.042 | 33.431 | 991.3 | 1002.9 | 15.1+15.3 |
| L12 | ne |  | 33.431 | 33.579 | 1002.9 | 1007.4 | 15.2+10.9 |
| L12 | bola |  | 33.579 | 34.050 | 1007.4 | 1021.5 | 15.2+15.4 |

`words_B.json` equals `words.json` from 3.0 s on (checked); only L1 → L1B differs (§2 hook B line). Hook A is voice-free
2.270-3.267; VO total 57 % of the reel; loop seam L12 end → DUR → L1 onset = 0.183 s.

---------------------------------------------------------------------------------------------------------------

## 3. Assets and paths (all verified with `ls` on 2026-10-09; `<RW>` = `/home/user/100/workspace/jawad_reels/pehle_wala`)

### 3.1 Prop: `pw_chai_glass` (blender-3d-artist, `pipeline/jawad_reels/assets3d_pehle_wala.py`)

| item | value |
|---|---|
| frames | `<RW>/props/pw_chai_glass/inferno_yaw/0000.png` … `0012.png` + `meta.json` (8.5 MB); `<RW>/assets3d/pw_chai_glass` is a symlink to `../props/pw_chai_glass` (one copy on disk) |
| format | 960 × 1280 RGBA 8-bit straight alpha, sRGB; mode `yaw`, 13 frames, -6 … +6° (1° steps), frame 6 = yaw 0; `loop: false` |
| load (verified) | `GLASS = S3.Asset3D('pw_chai_glass', 'inferno', mode='yaw', root='/home/user/100/workspace/jawad_reels/pehle_wala/assets3d', scale=0.75)` → folder `inferno_yaw`, `fallback False`, n 13, size (720, 960) with `scale=0.75` |
| frame for t | `GLASS.at_yaw(float(yaw(a)), interp='flow')`, `yaw(a) = 5.0 * math.sin(2 * math.pi * a / 8.533333)` (a = ambient clock; period 4 bars, so yaw(a - DUR) = yaw(a)). **Pass a Python float**: a `numpy.float64` crashes `_flow_interp` in `cv2.convertMaps` (measured; SHARED_REQUESTS #12). Flow cost measured ~0.05 s per call at 960 px once a pair's flow is cached (first call per pair ~0.5-0.7 s): build the 10 pairs between -5° and +5° in `prewarm()` (`GLASS.at_yaw(i + 0.5, 'flow')` for i in -5..4) |
| draw | `K.draw(ad, img, 515 - 120, 1190 - 468, scale=0.604936 * z * e19, anchor=(0.5, 0.856875))` in ad-local px (ad-local = screen - (120, 468)); 0.604936 = 0.453702 / 0.75; anchor fraction = meta anchor (480, 1096.8) / (960, 1280). With `scale=0.75` the largest draw scale (push 1.2437 × v19 1.2) is 0.903 ≤ 1 (no upscaling) |
| anchor / pivot | base centre (sprite 480, 1096.8) → **screen (515, 1190)** at push 1.0 (D4) |
| features → screen (k 0.453702, base at (515, 1190), push 1.0) | rim centre (515, 768.2) · rim front lip (515, 787.0) · rim back lip (515, 750.5) · rim left / right x 357.3 / 672.7 at y 776.3 · chai surface (515, 849.4) · base front (515, 1217.7) · visible foot bottom y 1215 (alpha union, all yaws) |
| measured screen extent (union of 13 yaws, alpha > 0.03) | x 356-673, y 750-1215 (317 × 465 px) |
| what changes from BRIEF §13 on purpose (artist) | glass tint per surface crossing #FFFBF7 (so the 4-crossing tumbler transmits the brief's #FFF1E2), chai/foam albedos calibrated so the RENDER matches #A0582A / #D9A06A, PNG alpha = max(alpha, max(rgb)) to keep glass highlights; folder `props/` + symlink `assets3d/` |
| product push | unchanged: plate + glass + steam + reflection scale about **(515, 990)** by `z(s) = 1 + 0.02 * max(0, s + 0.4) / 2.1333` for s ≤ 25.6, held after (graphics do not push). v19 ×1.2 scales the glass about its base first, then the push applies. The foot passes the ad rect bottom from z ≈ 1.058 (s ≈ 5.8 s): a natural push crop, accepted |
| other glass-relative layout | ember backlight (515, 980) unchanged; contact shadow **(515, 1192)** 300 × 40 ×0.6 (BRIEF: base + 2); steam emitter on the rim opening **(515, 768)** (±120 px in x), rising, faded out by y 560 (keeps clear of the UBAAL CHAI wordmark, x ≤ 465, y 504-556); floor reflection from the foot line y 1215 (clipped by the ad rect: a 13 px sliver at push 1.0, keep it at ×0.22) |
| pin targets on the glass (unchanged, re-checked at base 1190) | pin 4 (515, 1000) glass body · pin 6 / 17 (515, 690) steam · pin 8 (600, 980) glass body (edge x ≈ 650) · pin 15 (515, 790) = rim front lip 787 · payoff (515, 900) chai body · sparkles (440, 860), (610, 900), (470, 1080), (590, 1150) all on the glass · flares y 790 (rim) and 1140 (base) |
| sheets | `<RW>/props/sheets/pw_chai_glass_final_{frames,ad440}.jpg`, `..._final_mid_black_flame.png`; log `<RW>/props/pw_chai_glass_3d.log` (1,816 s, 125 s/frame) |
| layout proofs (this hand-off) | `<RW>/brief_proof/r3/glass_anchor_A1210_B1190.jpg`, `garam_120_vs_100_base1190_yaw-6_0_+6.jpg`, `garam120_collision_crop.jpg` (scripts next to them) |

### 3.2 Faces: `pipeline/jawad_reels/pehle_wala_faces.py` (face-compositor; FACES.md)

- `import pehle_wala_faces as PF` after `jawad_kit` and `jawad_grade`; `PF.prewarm()` in `prewarm()` (~2.6 s/worker);
  `PF.draw_tile(cv, t)` after `PLAN.draw` and the Ctrl+Z chip, **before** the captions (in place; draws nothing outside
  f448-f511 and f836-f895; never inside `W_core`, so D9 never shows a face).
- `PF.avoid_rect(t)` → (70, 952, 430, 1284) while the tile shows, else None (captions `avoid`, §5).
- Shots: S4-01 `street_sunglasses` f448-f511, S6-01 `street_smirk` f836-f895 (cover f855); rim look A; scale 0.40.
- Cut-outs it reads (read-only): `/home/user/100/workspace/brand_reels/charsheet/cutouts/`, helper
  `/home/user/100/workspace/brand_reels/charsheet/tools/faces.py`.
- The tile (x 70-430, y ≥ 980) covers the glass's left edge (x 357-430) while it shows, cover frame included: accepted
  (a docked cam over the player, BRIEF §5.1).

### 3.3 VO (hinglish-scriptwriter; VO_TIMING.md)

| file | spec |
|---|---|
| `<RW>/vo/pehle_wala_vo_A.wav` (= `vo_stem.wav`, same sha256) | hook A, 48 kHz 24-bit **mono**, 1,638,400 samples, -16.00 LUFS, TP -2.8 dBTP |
| `<RW>/vo/pehle_wala_vo_B.wav` (= `vo_stem_B.wav`) | hook B (L1B + L2-L12), same format |
| `<RW>/vo/pehle_wala_vo_A.words.json` (= `words.json`), `pehle_wala_vo_B.words.json` (= `words_B.json`) | reel-second word times on the Roman caption tokens (`word, start, end, keyword, line, dev, heard, ok`); `SC.load_words` reads them as they are |
| `<RW>/vo/vo_timeline.png`, `timing.json`, `verify.json` | measurement artefacts |

The VO is mono: never pass it through `audio._write_wav(read_wav(...))` or `epic_mix.mix_reel` as is
(SHARED_REQUESTS #10, #11).

### 3.4 SFX (sound-designer; `pipeline/jawad_reels/pehle_wala_sfx.py`, SOUND.md)

- Module line: `from pehle_wala_sfx import cues, BED, BED_GAIN_DB` (verified: 125 cues hook A, `cues('B')` 123,
  `BED_GAIN_DB` -32.0). `cues()` in `pehle_wala.py` returns `pehle_wala_sfx.cues()`; the hook B module returns
  `pehle_wala_sfx.cues('B')`. Never draft cues in the timeline module.
- Stems: `<RW>/audio/pehle_wala_sfx_A_stem.wav`, `pehle_wala_sfx_B_stem.wav` (48 kHz 24-bit stereo, 1,638,400
  samples, -18.0 LUFS, -2.2 dBTP, loop-exact); cue logs `<RW>/audio/pehle_wala_sfx_{A,B}_cues.json`.
- **Re-cue after this hand-off (D2):** drop the `card_slide` at 21.400 (old drawer entry); the existing `card_slide` at
  21.867 becomes the drawer entry (no VO there: "ek." ends 21.683, so it can return toward the brief's -8 dB). Then
  `tools/heavy.sh python3 pehle_wala_sfx.py build --hook AB` and `... rough --hook AB`. Starts at 21.867 stay 3.
- Render rule: always `--no-sfx-build --audio <mix wav>` (render.py's own SFX build lacks the loop wrap, drop-out gate,
  press tape-stop and carve windows).

### 3.5 Music (music-supervisor; `pipeline/jawad_reels/pehle_wala_music.py`, MUSIC_pehle_wala.md)

- `<RW>/music/music_full.wav` (hook A) and `<RW>/music/music_hookb.wav` (hook B): 48 kHz 24-bit stereo, 1,638,400
  samples, -16.0 LUFS, TP -3.2 dBTP, LRA 5.4; stems in `<RW>/music/stems/` and `<RW>/music/stems_hookb/` (five each).
- The BRIEF names `<RW>/audio/pehle_wala_music_A.wav` / `_B.wav` are relative symlinks to those two files.
- Grid: 112.50 BPM, phase -8.3 ms by the method (a grid click reads -13.3 ms); drop-out 25.067-25.600 and rewind
  26.533-27.733 are digital zeros; tape-stop 26.133 (0.4 s); restart onset 0.54 ms after 27.7333; no end fade; bar 15
  (C, VII) resolves into frame 0's Dm.

### 3.6 Mixes

- Rough (for previews now): `<RW>/audio/pehle_wala_A_rough_mix.wav`, `pehle_wala_B_rough_mix.wav` (Version A),
  `pehle_wala_{A,B}_rough_vo_sfx.wav` (Version B), stems `pehle_wala_{A,B}_rough_stem_{vo,sfx,music}.wav`. Measured
  here (ffmpeg ebur128): A and B I -14.0 LUFS, TP -2.3 dBFS, **LRA 2.3 LU**; f752-f759 max abs 0.0; last 0.5 s RMS
  -17.8 dBFS, first 0.1 s -17.7 (no fade).
- Final (master): **not built yet** (music-supervisor run 2 after the SFX re-cue). Name it in the render command when it
  exists.

### 3.7 Fonts and toolkit

- Parody face: **not yet in `<WS>/fonts`**. Copy
  `/root/.claude/plugins/synced/52e39fd9-fc02-4eeb-bd0a-78be55c219f4_9d49974d-76ce-4345-a26f-8cb895a77bfd/82436e8d-b5bb-4da5-b372-0309f771299f/skills/animation-studio/engine/fonts/Caveat-Bold.ttf`
  → `/home/user/100/workspace/jawad_reels/fonts/pw_parody_fun.ttf` and `OFL-Caveat.txt` →
  `/home/user/100/workspace/jawad_reels/fonts/OFL-pw_parody_fun.txt`; use `font='pw_parody_fun'` (no "Caveat" in the
  name: project.json `font_map` remaps Caveat to the serif). Expected ink width of "garam" at 112 px ≈ 246 px (PIL on the
  source file: 242 at 110, 264 at 120); confirm with `T.measure('garam', 'flat', px=112, font='pw_parody_fun')`.
- Shared, read-only: `jawad_kit.py`, `jawad_grade.py` (registers `inferno`; its backdrop has `rim=None, dots=0.0`),
  `jawad_tx.py`, `endcard.py`, `snake_captions.py`, `sprites3d.py`, `type3d.py`, `ui.py`, `core.py`, `audio.py`,
  `render.py`, `TOOLKIT.md` in `/home/user/100/pipeline/jawad_reels/`; `tools/heavy.sh` for every heavy job.

---------------------------------------------------------------------------------------------------------------

## 4. Ad canvas numbers that change (BRIEF §5.2 / §6.2; everything else there stands)

| element | BRIEF r2 | build |
|---|---|---|
| glass base (anchor) | (515, 1210) | **(515, 1190)** |
| glass scale at push 1.0 | "440 px" | **0.453702 × sprite** (0.604936 with `scale=0.75`) |
| glass top (rim back lip) | ~770 | **750.5** |
| contact shadow | (515, 1212) | **(515, 1192)** |
| steam origin | rim (515, 790) | **rim opening (515, 768)**, top still y 560 |
| AD2 *garam* | jw_key 120 px, box x 602-900 | **jw_key 100 px, ink x 651-898, y 1125-1207**, right-aligned at x 900, centre y 1150 |
| AD2 parody (v10+) | 130 px | **112 px** (`pw_parody_fun`) |
| AD2 cream-gag fill, v11 shadow, v19 ×1.2 about the right edge, focus dim g(t) | as BRIEF | unchanged (shadow right edge 912 ≤ 914; shake 920 ≤ 922) |

---------------------------------------------------------------------------------------------------------------

## 5. Captions plan (`snake_captions.py`, inside the module, after the face tile, before `post`)

```python
import snake_captions as SC
import pehle_wala_faces as PF
VO_A = '/home/user/100/workspace/jawad_reels/pehle_wala/vo/pehle_wala_vo_A.words.json'
def cap_avoid(t):
    r = [(80, 236, 1000, 1268)]                       # the player: pins, ad, UI
    a = PF.avoid_rect(t)                               # (70, 952, 430, 1284) while the tile shows
    if a:
        r.append(a)
    if 26.1 <= t < 27.95:
        r.append((335, 1340, 745, 1436))              # Ctrl+Z chip (no VO then anyway)
    return r
CAP = SC.Captions(VO_A, band='lower', y=1400, avoid=cap_avoid, hide=[(0.0, 2.6667)],
                  clear=[(21.8667, 23.40)])           # D3: chunk 12 gone by the drawer entry f656
# draw (unless os.environ.get('PW_CAPTIONS') == '0'):
#   CAP.draw(cv, t, opacity=1 - K.ramp(t, 33.7733, 34.1, 'in_cubic'))   # loop-safe exit with the card
# prewarm: CAP.prewarm()
# SRT: CAP.save_srt('<RW>/captions/pehle_wala.srt'); for the upload SRT build a second instance WITHOUT hide= so the
#   hook line is in it (hook B: the same from pehle_wala_vo_B.words.json -> pehle_wala_hookb.srt)
```

Solved here on the measured words (hook A; hook B identical from chunk 0; `CAP.check() == []` for both, with and
without the clear window). One serif keyword per VO line L2-L10; L11 and L12 all-white (gate fix 4).

| chunk | text | serif keyword | in s (f) | exit starts s (f) | gone s (f) | scale | ink bbox x0, y0, x1, y1 | note |
|---|---|---|---|---|---|---|---|---|
| 0 | Ho jayega | jayega | 3.217 (96.5) | 4.230 (126.9) | 4.350 (130.5) | 0.92 | 277, 1303, 757, 1476 |  |
| 1 | Pop? | Pop? | 4.350 (130.5) | 4.920 (147.6) | 5.040 (151.2) | 1.00 | 357, 1298, 662, 1475 |  |
| 2 | Kisi ko | - | 5.040 (151.2) | 5.398 (161.9) | 5.438 (163.1) | 1.00 | 362, 1346, 673, 1479 |  |
| 3 | nahi pata | - | 5.438 (163.1) | 6.467 (194.0) | 6.587 (197.6) | 1.00 | 308, 1346, 711, 1476 |  |
| 4 | Clean | Clean | 6.683 (200.5) | 7.883 (236.5) | 8.183 (245.5) | 0.92 | 346, 1304, 687, 1474 |  |
| 5 | Energetic | Energetic | 8.550 (256.5) | 9.920 (297.6) | 10.220 (306.6) | 0.92 | 272, 1304, 747, 1472 |  |
| 6 | Fun | Fun | 10.750 (322.5) | 11.900 (357.0) | 12.200 (366.0) | 1.00 | 374, 1297, 660, 1479 |  |
| 7 | Ab Mummy bhi | Mummy | 12.817 (384.5) | 13.652 (409.6) | 13.692 (410.8) | 0.92 | 174, 1302, 846, 1474 |  |
| 8 | review karengi | - | 13.692 (410.8) | 14.830 (444.9) | 14.950 (448.5) | 1.00 | 227, 1300, 809, 1445 |  |
| 9 | Bilkul cinematic | cinematic | 14.950 (448.5) | 16.770 (503.1) | 17.070 (512.1) | 0.78 | 211, 1318, 808, 1464 | shrunk by the tile avoid |
| 10 | Aur ek | - | 19.183 (575.5) | 20.073 (602.2) | 20.193 (605.8) | 1.00 | 362, 1346, 672, 1479 |  |
| 11 | aur ek | - | 20.193 (605.8) | 20.803 (624.1) | 20.923 (627.7) | 1.00 | 363, 1348, 656, 1474 |  |
| 12 | aur ek | ek | 20.923 (627.7) | 21.617 (648.5) | 21.867 (656.0) | 1.00 | 351, 1307, 683, 1480 | early exit (D3) |
| 13 | Phir aakhri message... | aakhri | 23.450 (703.5) | 25.280 (758.4) | 25.580 (767.4) | 0.85 | 105, 1309, 914, 1470 | gone 1 frame before the payoff |
| 14 | Har editor | - | 28.083 (842.5) | 28.719 (861.6) | 28.839 (865.2) | 0.92 | 317, 1348, 717, 1475 |  |
| 15 | jaanta hai | - | 28.839 (865.2) | 29.703 (891.1) | 29.823 (894.7) | 1.00 | 298, 1346, 721, 1476 |  |
| 16 | v1 hi | - | 29.823 (894.7) | 30.590 (917.7) | 30.700 (921.0) | 1.00 | 395, 1347, 638, 1478 |  |
| 17 | final hota hai | - | 30.700 (921.0) | 32.343 (970.3) | 32.463 (973.9) | 1.00 | 250, 1344, 769, 1478 |  |
| 18 | ...aur phir | - | 32.550 (976.5) | 32.883 (986.5) | 32.992 (989.8) | 1.00 | 313, 1303, 723, 1441 |  |
| 19 | client ne bola | - | 32.992 (989.8) | 34.400 (1032.0) | 34.700 (1041.0) | 1.00 | 245, 1344, 774, 1478 | cut by the loop-safe ramp 33.773-34.1 |

All ink is inside x 105-914, y 1297-1480 (safe zone x 70-1010, y 230-1480; x ≤ 930 in y 1050-1700; nothing below 1620);
the client marker (y ≤ 609) and the end-card boxes (key y ≤ 1082, signature y ≥ 1563) never meet it.

---------------------------------------------------------------------------------------------------------------

## 6. Transitions (`jawad_tx`; plan verified: windows do not overlap, `X.check_cues(PLAN.cues()) == []`)

```python
GR = X.Grid(112.5)
PLAN = X.Plan([('L3', GR.at(2), dict(push_gain=0.5)), ('D7', GR.at(6)), ('L3', GR.at(7), dict(push_gain=0.6)),
               ('L3', GR.at(8), dict(push_gain=0.4)), ('D7', GR.at(10)), ('L3', GR.at(12), dict(push_gain=1.0)),
               ('D9', GR.at(13), dict(pre=48, post=2, press=6, R=GR.at(12, 1), keys_y=-2000.0))])
SCENES = [W, W, W, W, W, W, W_core_rewind_source, P]
```

| id | catalogue name | `jawad_tx` draw fn / post | cut | window (measured) | post values (measured `PLAN.post_kw`) | samples |
|---|---|---|---|---|---|---|
| L3 | exposure-push flash frame (glue) | `_tx_cut` + `_l3_post` | f128, f448, f512, f768 | f128-f131, f448-f451, f512-f515, f768-f771 | push 0.5 / 0.6 / 0.4 / 1.0 on the cut frame, decaying (f129 0.293, f131 0.101 for 0.5) | 3 |
| D7 | RGB-split chroma shock | `_tx_cut` + `_d7_post` | f384, f640 | f384-f386, f640-f642 | rgb_split 1.0 / 0.264 (f+2) / 0.135 (f+3) | 3 |
| D9 ✂ | undo / Ctrl+Z rewind (signature, once) | `_tx_undo` + `_push_post(0.6)` | f832 (press f784) | f784-f833 | push 0.6 on f832, 0.352 on f833, 0.206 on f834 | 5 (f784-f833) |
| D1 ✂ | timeline playhead scrub (hook B only) | `_tx_scrub` (samples `_d1_samples`) | f70 | f40-f79 (`X.Plan([('D1', 70/30, dict(pre=30, post=10))])`) | - | 7-9 on the pull/push frames, 3 mid-scrub |

D9 exactly as the shared code runs it (BRIEF §11's formula is 0.2 s off; the code is the truth): `t_r = 26.3333`
(f790); f784-f789 show the live `W_core(t)`; from f790 `tau = 26.3333 - 26.1333 * in_cubic((t - 26.3333) / 1.4)`, so the
last rendered rewind frame f831 shows tau 2.02 s (v2 state), and the v2 → v1 step falls between f831 and f832 (the cut
to `P` shows v1). `keys_y=-2000.0` hides the keycaps (verified r1); the reel draws the "Ctrl+Z ×26" chip f784-f838.
Ambient (steam, yaw) inside the rewind follows tau. Pin ticks (rgb_split 0.25 impulse) are added in `post` for every
landing except f384, f640 (full D7) and f768 (clean). Budget: features D7, D7, D9 (+ D1 in hook B), gaps > 2 bars.

---------------------------------------------------------------------------------------------------------------

## 7. End card (verified by building it)

`CARD = E.EndCard('US CLIENT KO', 'bhejo', monogram='JD', dur=4.2667)`; draw `CARD.draw(cv, t, 29.8667)` in `P(t)`.

| param | value |
|---|---|
| t0 / end | 29.8667 (f896) / 34.1334 (= DUR) |
| settle / settled hold / exit | 1.85 s (settled 31.717) / **2.0567 s** (≥ 1.5) / 0.36 s (33.7733-34.1333) |
| boxes (screen px) | monogram 420-660 × 440-680 · caps 229-851 × 738-798 · keyword 350-730 × 858-1082 · signature 411-669 × 1563-1587 |
| y | mono 560, key 930, signature 1575; world dim 0.58 (inside the card) + the local player dim (k 0.65 envelope, BRIEF §16) + *garam* ×0.35 |
| post | `CARD.post_kw(t, 29.8667, DUR)` → push 0 / 0.075 / 0.6 on f1021 / f1022 / f1023 (`E.loop_push`, verified) |
| cues | in `pehle_wala_sfx.cues()` already (swish_small 29.967, shimmer 30.437, glass_tap 30.617 at -16, reverse_swell ending DUR with lp 1000) |

---------------------------------------------------------------------------------------------------------------

## 8. Loop bridge (BRIEF §6.3.1 + §7.3 stand; measured VO added)

- Picture: `P(t) = W_core(t - DUR, garam=g(t))` + player dim + payoff lockup + `CARD` + `pre1(t - DUR)` on top; frame 0's
  world is exactly one frame on from f1023 (no crossfade; `E.loop_world` not used). The client marker: entry f979-f988
  from (784, 196), hover around (850, 560), glide from 33.773 through (715, 500), (600, 436) to (470, 424) on f5, fall
  to (470, 472) on f8; it is (656, 465) on f1023 and (618, 443) on f0; 5 motion-blur samples from f1014 to the seam and
  on f0-f8.
- Voice: L12 "...aur phir client ne bola" 32.600-34.050 (end-anchored, rising, no cadence) → frame 0 "Bas" 0.100: a
  0.183 s seam gap.
- Type: card exit 33.773-34.133; captions fade with `1 - K.ramp(t, 33.7733, 34.1, 'in_cubic')`; frame 0 opens with HA1
  caps rising (t0 -0.1).
- Light: card push into f1023 (0.6) and frame 0 `cuts=[(0.0, 0.6)]`.
- Sound: `ui_hover` at 32.633; `reverse_swell` ends on DUR; tails past DUR wrap to t = 0 in the SFX stem; music bar 15
  (C) → frame 0 Dm; rough mix RMS -17.8 dBFS over the last 0.5 s (no fade).
- QA: `E.seam_report(lambda t: render.render_still(mod, t, 1), DUR)` ok (seam ≤ 1.5 × step + 2); stills 0 and 34.1 show
  the marker one frame step apart.

---------------------------------------------------------------------------------------------------------------

## 9. Build notes (module contract = BRIEF §16, with these deltas)

1. `GLASS` loaded once at import with `scale=0.75`; `yaw()` on `math.sin`; `float()` before `at_yaw` (§3.1).
2. Ad: base (515, 1190), contact shadow (515, 1192), steam from (515, 768), *garam* 100 px / parody 112 px (§4).
3. `state(s)`: drawer flag on from **f656** (not f640) with rows v24-v26 present on entry; v27 row from f672; the rest as
   BRIEF §6.3.
4. Captions as §5 (clear window, `PF.avoid_rect`).
5. `cues()` → `pehle_wala_sfx.cues()`; `BED`, `BED_GAIN_DB` from the same module.
6. `prewarm()`: `PF.prewarm()`, `CAP.prewarm()`, the 10 glass flow pairs, static sprites (window, chips, pin cards, drawer
   rows, logo plate, bursts, ribbon, pill) in `lru_cache`.
7. Copy the parody font first (§3.7). Make the out symlinks before the first render:
   `ln -sfn <RW>/out/main /home/user/100/workspace/jawad_reels/out/pehle_wala` and
   `ln -sfn <RW>/out/hookb /home/user/100/workspace/jawad_reels/out/pehle_wala_hookb` (neither exists yet).
8. Render ladder (BRIEF §16), every job through `tools/heavy.sh`, `--workers 1` while iterating: sheet → stills
   (`0,0.267,0.533,2.133,4.267,6.6,12.8,14.933,17.067,21.333,21.867,22.4,25.6,26.9,27.733,28.5,31.6,34.1`) → range
   25.2-28.2 → preview with `--no-sfx-build --audio <RW>/audio/pehle_wala_A_rough_mix.wav` → master with the final mix.
   Then re-shoot the face stills listed in FACES.md §5.
9. Disk: `/` had 7.1 GB free (82 % used) at 08:23 UTC; the reel workspace is 365 MB. Check `df -h` before the master
   and delete preview frames after.

---------------------------------------------------------------------------------------------------------------

## 10. Open risks

| # | risk | owner | blocks |
|---|---|---|---|
| R1 | Final mix does not exist; previews use the rough mix (it still has the old 21.400 drawer slide until the SFX re-cue) | music-supervisor (after sound-designer's re-cue) | master audio only |
| R2 | **LRA 2.3 LU** (rough A and B, measured) vs SLATE §5.1's 5-9. Recommendation: music-supervisor tries a ride first (v1 bars 0-1 and 13-15 down, payoff bar up); if it cannot reach 5 without losing speech ≥ 8 LU, the lead decides a VO-led exception (series constant, not this reel's call) | music-supervisor → lead | final audio sign-off |
| R3 | "ek." (21.270-21.683) is 7.1 LU over the ducked bar-10 music (median speech 11.8 LU passes) | music-supervisor (duck bar 10 under that word) | no |
| R4 | SFX re-cue for D2 not done yet | sound-designer | no (previews) |
| R5 | Nobody can listen: L1B take t5's "client" reads with a /p/ in 3 of 8 ASR passes (alternate t1 ends 2.760, 2 f past the gate); L9 t4 was prompted with "!" and may sound punchier than the scripted tired count | lead (human listen before posting) | posting |
| R6 | Face stills were shot on a stand-in world at the wrong glass scale (0.4732, base 1210) | face-compositor re-shoot after your build | no |
| R7 | `at_yaw` float64 crash in shared `sprites3d` (worked around) | motion-toolkit-engineer (SHARED_REQUESTS #12) | no |
| R8 | Push crops the glass foot from s ≈ 5.8 s and *garam* touches the pushed glass from s ≈ 10.3 s (both by design in the clutter phase); QA must not flag them after those times | QA | no |
| R9 | Pin-1 card hides part of the ×2 logo at v2; v7 steam outline (3 px) and the hover marker must read at 360 px (GATE §8) | builder + viral-strategist red-team | no |
| R10 | AI label, "Ubaal Chai" trademark check, Trial Reels eligibility | lead / Jawad | posting |
| R11 | `epic_music.py` / `epic_sfx.py` are git-ignored (SHARED_REQUESTS #7): the score cannot be rebuilt from a clean clone | lead | reproducibility |

---------------------------------------------------------------------------------------------------------------

## 11. SHARED_REQUESTS

`SHARED_REQUESTS.md` (this folder) now holds 12 requests; none blocks the build. New in this hand-off: **#12**
`sprites3d.Asset3D._flow_interp` crashes on a `numpy.float64` yaw (workaround: pass a Python float). Still relevant to
you: #1 (D9 keycaps, workaround `keys_y=-2000`), #2 (`KeyFirstTitle` and the `CHANGE` line built locally), #3 (loop-safe
caption fade), #4 (local player dim under the card), #5 (out symlinks), #10/#11 (mono VO in shared audio code).

---------------------------------------------------------------------------------------------------------------

## 12. QA acceptance checklist (BRIEF §18 with this hand-off's changes; measure, do not eyeball)

Format and timing
- [ ] ffprobe: 1080x1920, 30/1 CFR, nb_frames 1,024, 34.133 s, for the hook A master and the hook B splice.
- [ ] Pin landings exact: f8, 64, 96, 128, 192, 224, 256, 288, 320, 352, 384, 400, 416, 432, 448, 480, 496, 512, 544,
      576, 592, 608, 624, 640, 656, 672, 768 (marker tip on its point, card visible from that frame); v2 change f32.
- [ ] Counter v1 f0-f31, v2 f32 …, v27 f672-f783, spins down f790-f831, v1 from f832. Chip Approved f0-f11 and
      f832-f1023, "Changes requested" f12-f831.
- [ ] **Drawer**: absent f640-f655, slides in from f656 with rows v24, v25, v26; row v27 from f672; gone by f704.
- [ ] Hook B frames 80-1023 identical to hook A (lossless intermediates, mean abs diff 0).

Glass and ad (new)
- [ ] Glass base centre at (515, 1190 ± 1) on f0 and f832 (alpha-bbox bottom 1215 ± 2, top 750 ± 2, x 356-673 ± 2
      at yaw ≈ 0); foot fully inside the ad rect on f0-f79 and f832-f1023.
- [ ] *garam* ink x 651-898, y 1125-1207 (± 2) on f0 and f832; no pixel of *garam* ink over glass alpha > 0.03 on
      f0-f80 and f832-f1023 (gap ≥ 10 px measured).
- [ ] `at_yaw` gets Python floats (grep: no `np.sin` in `yaw()`), no `cv2.error` in any render log.

Hook and story
- [ ] f0 YAVG ≥ 25, f0 vs f1 mean abs diff > 0.5, no black or fade.
- [ ] VO onset 0.100 s (first sample above -40 dBFS on the VO stem ≤ 0.30); hook B's last word ends ≤ 2.70 (2.580
      measured); lockup keyword glyphs ≥ 80 % opacity by f16.
- [ ] Payoff pin f768 (75.0 %); consecutive-frame mean abs diff > 0.5 on every frame f791-f831 (desat/zoom ramps
      carry the slow start of the in_cubic rewind).
- [ ] End card settled hold ≥ 1.5 s (2.057 by construction); signature present 30.867-34.1.
- [ ] Loop: `E.seam_report` ok; last 0.5 s audio RMS > -40 dBFS; marker (656, 465) on f1023 and (618, 443) on f0
      (± 2 px), absent from f784-f833, clear of the monogram (while ≥ 20 % visible), caps, keyword and signature boxes;
      f4 → f5 step ≤ 10 px; `ui_hover` onset 32.633 ± 1 f.
- [ ] *garam* focus dim: `g(28.5) == 0.35`, `g(1023/30) == 1.0`, `g(t) == 1` for t < 27.733.
- [ ] Hook B: no lockup text f0-f8; panel weight 0 at f12, 1 at f20; at 360 px nothing reads "26% OFF"; lockup
      ≥ 4.5:1 at p90.

Copy, layout, legibility
- [ ] Every string exactly as BRIEF §6 (spelling, case, punctuation), widths ≤ 940 (≤ 780 centred in y 1050-1700).
- [ ] Ink inside x 70-1010, y 230-1480 (CTA to 1600); nothing at x > 930 for y 1050-1700; nothing below 1620 except
      `@jawad_mp4` (1563-1587); *garam* right edge ≤ 914 with shadow, ≤ 922 with shake.
- [ ] ≤ 2 text blocks at 10 fps sampling, per §2.1 (a pin card handing over to the next counts once); specifically
      f640-f655 = pin card + chunk 12, f656-f703 = pin card + drawer.
- [ ] Captions: `CAP.check() == []`; chunk windows within ± 1 f of §5; chunk 12 gone on f656; chunk 13 gone by f767;
      no caption keyword after 27.7 s; hidden 0-2.667; SRT matches the tokens; house spelling.
- [ ] Underline ≤ 3 per version; serif keyword moment on a downbeat (PO1 at f832).

Motion and finish
- [ ] Transitions at L3 f128, f448, f512, f768; D7 f384, f640; D9 f784-f833 (cut f832); hook B D1 f40-f79 (cut f70).
      No keycaps; "Ctrl+Z ×26" chip f784-f838.
- [ ] No `K.flash`, `K.fade` or `post(flash=)` in any pehle_wala file; 1st-percentile luma at push frames within ± 2
      code values of the previous frame.
- [ ] Exits ≥ 0.2 s (pin collapse 6 f, tile 10 f, lockups, drawer 8 f, chunk 12's early exit 0.25 s); no one-frame jumps.
- [ ] Shake ≤ 8 px; luma flips ≤ 3 per second.
- [ ] Faces: tile 2.133 s and 2.000 s, halo ≤ +6, scale 0.40, face box ≥ 60 px from copy (FACES.md §4 re-measured on
      the real reel).
- [ ] Colour: `python3 jawad_grade.py verify <master> inferno` (red-orange ≥ 60 % of saturated px, YMIN 16-22, cream
      ≤ 35 % of the frame, emissive ≤ 3× linear).

Audio (on the final mix; the rough mix numbers in §3.6 are not a pass)
- [ ] -14.0 ± 0.5 LUFS, TP ≤ -2.0 dBTP (wav), ≤ -1.5 after AAC; LRA per the lead's R2 decision; VO stem -16 LUFS;
      speech ≥ 8 LU over the music (median), "ek." at 21.27 checked; SFX ≥ 6 LU under speech in VO windows.
- [ ] Max momentary within ± 0.2 s of 25.600; exact zeros f752-f759; one tick at 25.333.
- [ ] Thock onsets ± 1 f of the land frames; tape-stop 26.133 ± 1 f; restart 27.733 ± 1 f; drawer `card_slide` at
      21.867 ± 1 f and none at 21.400; ≤ 3 starts per instant; tonal SFX ± 30 cents of their bar's chord tones.
- [ ] Version B (VO + SFX) for both hooks; stems sum to the mix.

Brand, truth, ops
- [ ] Nothing from Organic Fostering / Floret, no old props, no typing dots, no ERROR / unsaved dialogs, no hearts, no
      currency, phone numbers, URLs or real logos; "POV" in the header and caption L1.
- [ ] Numbers: v1 → v27, 26 change pins, "Ctrl+Z ×26", "chhabbees" (hook B only).
- [ ] `du -sh <RW>` < 2 GB at hand-off; no files written into another reel's folders.

---------------------------------------------------------------------------------------------------------------

## 13. Paths verified (ls, 2026-10-09)

Design: `brand_reels/design/SLATE.md`; `brand_reels/design/reels/pehle_wala/{BRIEF,SCRIPT,GATE,VO_TIMING,FACES,SOUND,
MUSIC_pehle_wala,SHARED_REQUESTS}.md`, `script.json`, `packet.yaml`. Code: `pipeline/jawad_reels/{pehle_wala_faces,
pehle_wala_faces_proof,pehle_wala_sfx,pehle_wala_music,pehle_wala_vo,assets3d_pehle_wala}.py`, `tools/heavy.sh`,
`render.py`. Workspace `<RW>`: `props/pw_chai_glass/inferno_yaw/{0000..0012.png,meta.json}`, `assets3d/pw_chai_glass`
(symlink), `props/sheets/`, `vo/pehle_wala_vo_{A,B}.wav`, `vo/pehle_wala_vo_{A,B}.words.json`, `vo/words.json`,
`vo/words_B.json`, `audio/pehle_wala_sfx_{A,B}_stem.wav`, `audio/pehle_wala_{A,B}_rough_mix.wav`,
`audio/pehle_wala_{A,B}_rough_vo_sfx.wav`, `audio/pehle_wala_music_{A,B}.wav` (symlinks), `music/music_full.wav`,
`music/music_hookb.wav`, `music/stems/`, `music/stems_hookb/`, `out/main/`, `out/hookb/`, `captions/`,
`qa/faces/`, `brief_proof/r3/`. Fonts: the Caveat source and `OFL-Caveat.txt` (path in §3.7). Not existing yet (yours):
`pipeline/jawad_reels/pehle_wala.py`, `pehle_wala_hookb.py`, `<WS>/fonts/pw_parody_fun.ttf`, `<WS>/out/pehle_wala`,
`<WS>/out/pehle_wala_hookb`.
