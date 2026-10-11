# BRIEF · Bijli series #3 · Sirf 36 Shots (@jawad_mp4)

v1, 2026-10-11 · pre-production (content strategist + script writer + creative director). Binding: 
`brand_reels/design/BIJLI_SERIES.md` (hard rules), `LEAD_DECISIONS.md`, house brand (`pipeline/jawad_reels/BRAND.md`,
`.claude/skills/jawad-brand-reels/SKILL.md`). Companions: `SCRIPT.md` + `script.json` (captions, optional VO, hooks),
`SHOTS.md` (frame shot list + Blender / Sound / UI-type hand-offs). Reference build copied for format only:
`brand_reels/design/reels/bijli_chali_gayi/*`, `pipeline/jawad_reels/bijli_chali_gayi.py`.

Notation: `f` = frame at 30 fps (f0 = 0.000 s). 120 BPM: beat = 15 f, bar = 60 f, bar n starts at f60n.
`RWS` = `workspace/jawad_reels/sirf_36_shots`. Module `pipeline/jawad_reels/sirf_36_shots.py`, 3D builder
`assets3d_sirf_36_shots.py`, sound `sirf_36_shots_sfx.py` / `_music.py`.

## 0. Deliverables
| item | value |
|---|---|
| format | 1080x1920, 30 fps, **36.000 s = 1,080 f = 18 bars at 120 BPM** (easter egg: a 36-second reel about 36 shots) |
| versions | A (public). B = Trial Reel, differs only in f0-f59 (bonus, only if it passes the same QA, LEAD #6) |
| audio | text-led: kinetic captions + SFX + original music. Optional VO layer written (SCRIPT §3), not recorded (no paid credits) |
| delivery | `reel/jawad_reels/sirf_36_shots/` per `tools/deliver_reel.py`: `_ig.mp4`, `_ig_songready.mp4`, `_master.mp4`, stems, `_cover.jpg`, `_cover_grid_3x4.jpg`, `_caption.txt`, `.srt`, README.md; each file < 95 MB; -14 LUFS, TP <= -2.0 dBTP wav / <= -1.5 after AAC |
| on screen | **no Jawad face, no character sheet, no humans.** 3D Blender props (photoreal) + house type + glass UI. Only face-adjacent element: the @jawad_mp4 badge inside the profile outro (allowed) |

## 1. Strategy (viral-strategist + trend-researcher, condensed; no web research run, baseline Oct 2026 in trend-researcher.md)
**Human truth.** A film roll made every click precious ("sirf ek photo bachi, sab ready ho jao"); you waited days, half
the prints had eyes shut or a thumb in the corner, and you still kept every one. Today an editor gets 2 TB, 4 cameras,
3,000 takes and still hears "ek achha shot nahi hai".

**Send sentence.** (1) A 25-40-year-old sends it to a sibling / cousin / school friend: "hamari album bhi aisi thi"
(nostalgia + identity). (2) An editor / videographer sends it to their crew or tags the shoot director: "yeh har shoot
ki kahani hai" (in-group pain, social currency). Two senders = two reach paths; Bijli worked on path 1.
**Save trigger.** Weaker than send; the closer line "Tab 36 kaafi the" is the screenshot / save line.
**Comment bait.** Naming a camera model is the easiest comment on Instagram (zero effort, nostalgic flex): question
"Ghar ka pehla camera kaunsa tha?" + choice line "Roll wala ya digital?". Pinned comment adds the second prompt
(funniest print: thumb wali ya aankhein band wali?).

**Scores (0-10, gates Hook >= 8, Share >= 7, Truth pass, Brand >= 7).**
| axis | score | evidence |
|---|---|---|
| Hook | 8 | f0: a glowing frame counter mid-tick + `SIRF / ek / PHOTO BACHI.`; number + stakes, reads muted; tension resolves in a flash pop at 2.0 s |
| Relatability | 9 | film roll / studio wait / thumb print are pan-South-Asian 80s-2000s; editor twist is daily life |
| Share trigger | 8 | two senders (above) |
| Novelty | 7 | same series spine as Bijli (nostalgia -> editor twist) by design; new world (photo, film), new device (the counter) |
| Truth | pass | no Jawad facts; 36-exposure roll, days-long wait, 2 TB / 4 cams / 3,000 takes are a generic labelled-by-context scene, not his project |
| Loop | 8 | ends on the same counter macro at "35"; the wheel ratchet across the seam turns it to "36" at f15 |
| Feasibility | 8 | ~10 photoreal props, mostly stills + 4 short sequences; CPU ~2 h (SHOTS §A) |
| Brand | 8 | flame keyword serif + white grotesk, warm dark world, `noir_ember` look (one red-orange practical per shot) |

**Retention map (open loop, re-hooks).**
| s | event | why stay |
|---|---|---|
| 0-2.0 | counter ticks 35->36, flash charges, `Sab ready ho jao!` -> flash pop f60 | open loop 1: the last shot |
| 2-5 | camera after the flash, rewind crank spins by itself, `Har click ginti mein tha.` | escalation |
| 5-8 | canister whips up, spins; `studio jaata tha...` | new world every 2-3 s |
| 8-10 | counter top: light jumps day/day/night; `3 din ka intezaar.` | time passes (cut on beats) |
| 10-14 | envelope opens, prints fan; `aankhein band, ... thumb.` | comic beat (closes loop 1: that last shot was a thumb) |
| 14-16 | album, sleeve seals; `Phir bhi har photo sambhaali.` | warm turn |
| **16.0 (44 %)** | **RE-HOOK: snap zoom, sub drop, drives; `Aur aaj?`** | open loop 2: the present |
| 18-26 | `2 TB footage, 4 cameras, 3,000 takes`, media bin scrolls, `Har take dekha.`, `Disk full.` | numbers slam on beats, escalate |
| 26-27 | **drop-out f780-f809**: freeze + typing dots | silence pulls |
| **27.0 (75 %)** | **PAYOFF f810: `"EK ACHHA SHOT / nahi hai."`** (loudest moment) | closes loop 2 |
| 30-32 | portal back into the counter window, `Tab 36 kaafi the.` | screenshot line, loop bridge |
| 32-36 | profile outro over the dimmed counter world; seam f1079 -> f0 | question, follow |
Visual change <= 2.5 s everywhere (SHOTS §1 lists every change); rewatch triggers: the reel is 36 s, the date stamp
`'98 10 11` on every print, the negatives strip shows frame numbers 34 35 36, the take counter stops on 3,000.

## 2. Look, world, family
| key | value |
|---|---|
| LOOK | **`noir_ember`** (kit look, lead decision 2026-10-11; siblings: Bijli `dusk`, pencil_se_rewind `ember`, thoda_left_bas `gold_hour`): near-monochrome warm black, ONE red-orange practical per shot, non-red colours desaturated in post, deep crush, grain 0.022. The darkroom-safelight memory: tungsten/flash/safelight are the practicals, the yellow canister label and the print colours read as muted amber (intended: memory, not catalogue). Present section (f480-f899) = same look with `exposure=-0.15` and the drive LEDs + glass UI as its practicals. Hue budget `share`: red-orange >= 60 % of saturated px (keep the yellow label area small on screen) |
| world | past = a warm tungsten home + a photo studio counter by day/night; present = a dark edit desk lit by monitor glow and drive LEDs |
| symbol | the frame counter (f0, cover, closer, loop) + the amber flash-ready LED |
| signature device | **the count**: every section is a counter (frame counter 35-36, 3 days, 3,000 takes, 2.00 TB) |
| transition family | **camera / flash** (jawad_tx, lead decision): C1 f150, C6 f300, C8 f480, C3 f900 (1 premium); glue = L3 exposure push on every flash and hard cut. Siblings: Bijli light, pencil_se_rewind editor, thoda_left_bas match |
| hero type | `jw_key` serif keyword, `jw_caps` / `jw_caps_bold` lines, `jw_mono` UI readouts; no snake captions (no VO); designed 2-3 line lockups |
| BPM | 120 (past: half-time feel, 60 BPM groove; present: full time, 8ths). Siblings: Bijli 90, thoda_left_bas 100, pencil_se_rewind 112.5 |

## 3. Copy and do-not-claim
All copy is in `SCRIPT.md` (house spelling, Roman Urdu, sentence case for VO, caps lockups on screen). Do not claim:
Jawad's own shoots, clients, gear, takes, sizes; any camera / film brand (no Kodak, Fuji, Konica, Yashica marks or
their trade dress: our canister has its own layout); no "real" client names (the toast says only `Client`).

## 4. Outro and cover
- **Outro** (f960-f1079, 4.0 s): `PO.ProfileOutro('Ghar ka pehla camera kaunsa tha?', key='Roll wala ya digital?', dur=4.0)`,
  `T_END = 960` (bar 16). Draft "Aap ki pehli camera kaunsi thi?" improved: "camera" is masculine in both Urdu and
  Hindi (pehla / kaunsa), "ghar ka" includes everyone whose family owned one camera, the key line turns it into a
  one-tap choice. World behind it: the counter macro at "35", dimmed (dim 0.74).
- **Cover** (dedicated still, `JAWAD_S36_COVER=1`): counter macro at "36" (tick sequence frame 15), flash-ready LED lit,
  lockup `J.HouseTitle('SIRF', '36 shots', caps_px=110, key_px=250)` caps centre y 400, keyword y 590, underline y 740.
  Everything (lockup y 330-790, counter window y 1120 +- 150) inside the 3:4 grid crop y 240-1680. Readable at 210 px.
- **IG post.** Caption line 1 (88 chars): `Sirf 36 shots, 3 din ka intezaar. Aaj 2 TB footage aur phir bhi "ek achha shot nahi hai"`.
  Body: `Tab har photo album mein jaati thi, thumb wali bhi. Editors, aap ki kahani?` Hashtags (5): #videoediting
  #editorlife #filmcamera #nostalgia #jawadmp4. Pinned: `Album ki sab se funny photo kaunsi thi? Thumb wali ya aankhein band wali?`
  AI info: ON (LEAD #5). Audio name: `Original audio · Sirf 36 shots · @jawad_mp4`.

## 5. Craft rules (house Standards, apply to every frame)
Safe zones: key copy x 70-1010, y 230-1480; no copy x > 930 in y 1050-1700; bottom 300 px clear. Hero >= 130 px,
caps lines 72-110 px, UI >= 34 px. No full-frame flash or fade: the camera flash is a local bloom + exposure push via
`G.tx_finish(..., cuts=CUTS)` (L3). Frame 0 never dark (the lit counter + type). Every caption holds >= words/3 s and
>= 0.8 s; max 2 text blocks at once; captions clear 1 f before every transition window. Motion blur never crosses a cut.
Contract: `DUR=36.0, LOOK='noir_ember', BPM=120, assets(), prewarm(), draw(t)` pure, `post(cv,t) -> G.tx_finish`,
`samples(t)`, `cues()=[]` (BED None; mixed stem muxed with `render.py ... --no-sfx-build --audio <mix.wav>`). Heavy jobs
via `tools/heavy.sh`, render.py `--workers 1`.

## 6. Open questions (defaults applied, none blocks)
1. Look / BPM / family collisions: resolved by the lead 2026-10-11 (`noir_ember`, 120 BPM, camera/flash family).
2. VO layer: only if Jawad approves credits; captions stand alone.
3. Hook B (`Hilna mat!`) as Trial Reel: bonus after A passes QA.
