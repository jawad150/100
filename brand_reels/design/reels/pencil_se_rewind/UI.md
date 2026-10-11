# UI · Pencil Se Rewind (@jawad_mp4, Bijli series #1)

2026-10-11, UI/UX designer (caption-designer + brand-kit-builder roles). Module: `pipeline/jawad_reels/pencil_se_rewind_ui.py`
(pure draw functions `fn(cv, t, ...)`, house canvas, look `ember`). Selftest: `cd pipeline/jawad_reels &&
tools/heavy.sh python3 pencil_se_rewind_ui.py selftest` -> `workspace/jawad_reels/pencil_se_rewind/ui_selftest/`
(86 PNGs + `sheet_{lockups,snake,nle,outro}.png`, `cover*.png`, `pencil.png`, `snake_captions.srt`). Every PNG was looked at
at phone size; fixes below.

## 1. VO-led timing (LEAD_DECISIONS 3)
The approved Vlad VO is final, so the captions follow it. All beats live in one table, `UI.TM` (frames, inclusive).
At import it is **derived from the measured VO words** (`vo_final/pencil_se_rewind_vo_{A,B}.words.json`, or the newer
workspace `vo/words*.json`) by `UI.derive_vo_timing()`: a designed word lands on the floor of its VO onset frame, and
structural beats never move. So a VO re-assemble moves the type automatically. If needed:

    UI.retime(L12=(648, 656, 664, 672), HA_key=44)    # motion designer override (unknown keys raise)
    UI.retime(**UI.derive_vo_timing())                # back to the VO
    PSR_UI_TIMING=static | script                      # the frozen TIMING_VO table | the text-led SCRIPT plan

| key | frame (VO assemble 21:26) | VO word (onset f) | note |
|---|---|---|---|
| HA_key | **43** | V1 `Pencil.` 46.2 | hit leads the word by 0.1 s, same frame as the SFX hit (SOUND: VO keeps 8 LU) |
| HA_ul / HA_out | 45-57 / 62-69 | | the lockup leaves across the f64 cut and is gone before L2 `Walkman` (f70) |
| HB_key / HB_out | 32 / 58-65 | V1B `khatam?` 32.0 | |
| L5_in / L5_key | 240 / 253 | `Sirf` 240.3 / `andaza.` 253.1 | SIRF now enters in S4 (label), 16 f before the D8 ramp |
| L6_play / galat / phir | 320 / 347 / 376 | 320.0 / 347.3 / 376.1 | same frames as the PLAY / STOP / REW keys in SOUND |
| L6_out | 391-394 | | instant swap: `Mil gaya!` pops as the stack leaves |
| L7_in / L7_out | 395 / 423-428 | `Mil` 395.0 | gone before L8 `Aur` (430.7) |
| L9_in / L9_key | 448 / 464 | (`Cassette` 466.6) | structure: the eat + re-hook slam + D7 do not move |
| L12 | 648 / 656 / 664 / 672 | V9 not in the VO (ladder F4) | one 8th later than SHOTS (V8 `hain.` ends f642); = NLE scrub jumps, CUT f672 |
| L12_out | 691-697 | | gone before L13 `Bas` (698.3) |
| L14_in | 768 | (`Pehla` 777.7) | structure: payoff hit |
| L14_key = NLE_snap | **832** | V11 `Pencil.` 832.6 | key rise + pencil-playhead snap together (SFX ui_tick f832) |
| L15_l1 / L15_l2 | 852 / 878 | `Scrubbing` 852.7 / `cassette` 878.4 | |
| L14_out = L15_out | 884-895 | | both leave at the D2 razor (see deviation 1) |

`python3 pencil_se_rewind_ui.py selftest lockups` prints the VO alignment table. All designed words land within 1 f of their
VO onset; HA is a deliberate -3 f; the structural rows are marked.

## 2. Snake captions = the VO words
`UI.captions(hook)` feeds the measured VO words (stem A or B) into `snake_captions`, the same as Bijli. The text is exactly
what Vlad says, in house spelling. Lines that a lockup or the outro already show are never snake text (two-layer rule):
V1, V1B, `Sirf andaza.`, V4, `Mil gaya!`, V6, V11, V12, V13. Bands: upper (baseline y 410) L2 L3 L8 L10, lower
(y 1380) L4, top (y 330) L11 L13. Each band clears for the lockup windows, the drop-out f752-f767 and the other bands'
lines. A new VO line always beats the previous caption's hold. The upper band also clears for the f192 cut.
Keywords per SCRIPT.md (battery, ghumate, Gaana, pencil, wahi, badal; L8 none).

| f | chunk | scale | f | chunk | scale |
|---|---|---|---|---|---|
| 70-91 | Walkman ki | 1.00 | 512-552 | Saans rok ke | 1.00 |
| 91-140 | *battery* bachani thi | 1.00 | 552-569 | *pencil* se | 1.00 |
| 140-162 | toh pencil se | 1.00 | 569-593 | wapas | 1.00 |
| 162-192 | *ghumate* the | 1.00 | 594-611 | Aaj bhi | 1.00 |
| 196-210 | *Gaana* (lower) | 0.85 | 611-647 | *wahi* karte hain | 1.00 |
| 210-239 | dhoondna ho? (lower) | 1.00 | 698-723 | Bas tool | 1.00 |
| 429-447 | Aur phir... | 1.00 | 723-752 | *badal* gaya | 1.00 |

To avoid shrinking, two lines are split ("split, don't shrink"): `Gaana` / `dhoondna ho?` (the lower band is 820 px wide)
and `pencil se` / `wapas` (the reveal's viewer avoid rect starts at f576). `snake check: OK`, `blocks check: OK`
(no snake chunk overlaps a lockup or the drop-out by more than 1 f, hooks A and B).

## 3. QA measurements
- **Ink scan, every frame** (lockups alone, hook A f0-f1023 + hook B; alpha > 0.1, glow cores included):
  ink x 109-980, y 235-843; nothing in the y 1050-1700 column; **0 violations** of x 70-1010 / y 230-1480.
  Fixed on the way: slam peaks of wide keywords left the safe zone (`phans gayi!` 38-1048 px at f465, `khatam?`
  57-1025). `key_slam` now caps the peak so the word stays at or below 860 px wide (`phans gayi!` 1.24 -> 1.06). The `Yahan.` slam
  touched y 221, so L12 moved from y 330 to y 344.
- Snake chunks: SC's own safe-zone solve (x 70-1010, y 230-1480, right column) passes for every chunk.
- Outro boxes (PO): pill y 586-814, question 882-1051, key 1077-1166, button 1249-1353, all in the safe zone.
- NLE draw cost 115-320 ms / frame at 2 threads (zoomed strips are pre-built at both scales).

## 4. What was fixed after looking at the PNGs
1. L15 tag rode across the razor onto the outro's profile badge (f913/f918, unreadable). It now leaves with L14 at f884-f895.
2. L12 `Peeche. / Aage.` overlapped for 3 f at every swap ("PAagee"). They are now instant swaps: the new word's slide + slam is the
   transition (caption rule).
3. The L12 words and the big `Yahan.` sat on the viewer card's top edge, the CUT chip butted against the card bottom, and the
   viewer slid up through the top caption band at f704-f727 (on top of `Bas tool`). Viewer: 580 x 720 at (540, 838)
   (media 560 x 700, top y 478, bottom y 1198); the exit is now a 70 px lift + fade (f704-f717).
4. The viewer header ran the file name into the timecode at the new width: jw_mono 24 / 28 now.
5. Payoff: the tag sat on the panel top (y 872) and `cassette` had no space before `pe`. The HouseTitle moved up to
   y 520 (caps 320, underline 660, tag 728 / 800), and there is now a real word space after the inline keyword.
6. The A1 waveform was a loud gold mass next to the hero `Pencil.`. It is calmer now (peak 0.40, RMS 0.85 x GOLD).
7. Crash: `solid()` could not take a per-pixel colour (the stand-in hub). Fixed.
8. 3D backdrops: the selftest now shows each caption over its own shot's Blender plate with SHOTS' 2.5D framing
   (S1 hub, S2/S6 walkman, S3 hub crop x1.43, S4 label, S7 lid window x1.38, S8 walkman_eat, S9 hub_rescue). The GPU
   finals are not on this machine yet, so `_asset()` falls back to the Blender **preview** renders
   (`RWS/out/preview3d`, upscaled; layout only). The procedural stand-in is the last resort. With the finals in
   `RWS/assets3d/<name>/passes/meta.json` nothing changes in code.

## 5. Deviations from SHOTS.md / SCRIPT.md (lead / motion designer please note)
1. **L15 leaves at the razor (f884-f895)**, not "held to the V12 end across the razor" (VO_TIMING 3): at f899 the
   outro's profile pill pops exactly where the tag sits. The V12 tail `sikhi thi.` (f896-f915) plays under the razor
   with no text. Alternative if the lead wants the words: let the motion designer delay the card by about 20 f (not recommended:
   the outro hold and the loop seam are timed).
2. HA exit f62-f69 crosses the f64 splice by 6 f (the VO-led `Pencil.` lands f43, so the old f56 exit left only 13 f).
3. Viewer 580 x 720 at (540, 838) instead of 660 x 820 at (540, 830); its exit is a lift + fade instead of the slide up and
   out; S10-S12 avoid rect is now (250, 470, 830, 1205).
4. L12 at y 344 instead of 330; payoff block 40 px higher (key y 520 instead of 560).
5. L12 / scrub jumps and the CUT marker sit one 8th later (f648-f672), and the pencil snap is at f832, as in VO_TIMING / SOUND.

## 6. Interfaces for the motion designer (stage 3)
- `UI.lockups(cv, t, HOOK)`, `UI.captions(HOOK).draw(cv, t)`, `UI.nle(cv, t, media=...)` (default media = hub_loop at the
  scrubbed source time), `card = UI.outro()` + `card.draw(cv, t, UI.T_END)`, `card.post_kw(t, UI.T_END, UI.DUR)`,
  `card.cues(UI.T_END, UI.DUR)`; `UI.cover(cv)` over `hub_cover` + `UI.grid_crop(img)` (3:4 = y 240-1680: the lockup
  y 340-720 and the hub y 820-1420 are both inside, checked on `cover_guides.png`).
- `UI.prewarm()` from the reel's `prewarm()`. `UI.state(t)` exposes the NLE state (playhead x, timecode, morph, pencil
  x) if the reel wants to drive SFX or QA from it.
- `UI.lockup_windows(hook)` replaces the old `LOCKUP_WINDOWS` dict (it follows `retime`). `UI.captions()` now takes the
  hook (`'A'` default).
- SRT: `UI.captions(hook).save_srt(path)` writes the snake chunks; the lockup lines are not in it. If delivery needs a full
  transcript SRT, build it from the VO words (all 60 words) in sentence mode.
