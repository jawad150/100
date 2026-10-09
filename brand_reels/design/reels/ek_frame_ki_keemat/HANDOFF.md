# HANDOFF: Reel 3 · C08 · Ek Frame ki Keemat · `ek_frame_ki_keemat` → motion-timeline-builder

Date 2026-10-09 · Author: creative-director · For: the motion-timeline-builder, who writes `pipeline/jawad_reels/ek_frame_ki_keemat.py`
and `pipeline/jawad_reels/ek_frame_ki_keemat_hookb.py` next.

**Read order:** this file, then `BRIEF.md` r2 (§7 geometry and cameras, §8 strings, §10 samples, §17 contract are still the
spec), then `FACES.md` §2 and §8, then `SOUND.md` §0 and §6. **Where this file and BRIEF r2 / `packet.yaml` differ, this file
wins** (r3 deltas, §2). LEAD_DECISIONS (binding): 1 LRA 2.0-9 LU, 2 YMIN as Y p0.5 >= 16, 3 picture moves to the VO, 5 "VO · AI
voice" lane label yes, 6 hook B is a bonus, 7 speed over gold-plating.

Inputs used: `BRIEF.md` r2, `VO_TIMING.md` (FINAL, measured 07:20), `words.json` + `ek_frame_ki_keemat_hookb_vo.words.json`
(re-read today), `FACES.md`, `SOUND.md`, `MUSIC_ek_frame_ki_keemat.md`, `SHARED_REQUESTS.md`, LEAD_DECISIONS, SLATE §3.3 / §5.
Measured today: word times from words.json, `endcard.EndCard` boxes and hold (both CTAs), `X.Plan` with the two steps (cues),
a dry run of `SC.Captions` on the real words (three instances, `check() == []`), imports of every picture-side module.

Conventions: `f = floor(30 t)` (the frame during which an event starts; picture events are put on frame starts `f/30`);
`<RW>` = `/home/user/100/workspace/jawad_reels/ek_frame_ki_keemat`; `<P>` = `/home/user/100/pipeline/jawad_reels`;
`<D>` = `/home/user/100/brand_reels/design/reels/ek_frame_ki_keemat`. Grid `X.Grid(100)`: beat 0.6 s (18 f), bar 2.4 s (72 f);
DUR 14 bars = 33.6 s = 1,008 frames (f0-f1007).

---------------------------------------------------------------------------------------------------------------

## 1. Readiness at a glance

| item | status | note |
|---|---|---|
| VO stems A / B / `usey` fallback + word timings | **READY** | final, 61 + 6 words, every check PASS (VO_TIMING §1); 3 LISTEN words (§11 R3) |
| faces module `ek_frame_ki_keemat_faces.py` | **READY** | imports; `face_layers()`, `draw_layer`, `pane`, `layer_clock`, `eye_screen`; stills viewed (FACES §6) |
| 3D props | **none needed** | BRIEF §13: every element is a toolkit plane |
| picture-side shared modules | **READY** | `jawad_kit`, `jawad_tx` (C3, C8, C6 present), `jawad_grade` (`ember` in `ALL_LOOKS`), `endcard`, `snake_captions` import (1.3 s) |
| captions plan | **READY** | dry run on the real words: C1 / C2 / C3 `check() == []` (§6) |
| transitions, end card, loop | **READY** | `X.Plan` builds; card hold 1.99 s measured (§7-§9) |
| SFX module `ek_frame_ki_keemat_sfx.py` | READY (code, imports) | its stems must be **rebuilt** with your `SFX_EVENTS` (§3.3) on the rebuilt kit |
| music module `ek_frame_ki_keemat_music.py` | **BLOCKED** on the sound kit | `import` fails: `No module named 'epic_sfx'` (kit rebuild running; `KIT_READY` absent) |
| bed, SFX stem, final mix | **BLOCKED** (mix stage) | `<RW>/audio/` and `<RW>/music/` do not exist in this container; regenerated on the rebuilt kit (§4.4) |
| reel module, hook-B module | **TO BUILD (you)** | none exists; gate stills (§10) before animating |
| master, splice, QA, delivery | BLOCKED on the module and the mix | previews can run on the VO stem alone (§10) |

---------------------------------------------------------------------------------------------------------------

## 2. What changed since BRIEF r2 (r3 decisions, made here; LEAD_DECISIONS 3: the picture moves to the VO)

| # | what | BRIEF r2 | r3 (binding) | why |
|---|---|---|---|---|
| 1 | side-on lands, counter `12` settles, L3 push 0.3 | 4.80 (f144) | **5.2333 (f157)**; orbit 2.4 -> 5.2333; counter roll 3.0 -> 5.2333 | "12" spoken at 5.230 |
| 2 | cover frame | f153 | **f165 (5.5 s)** | at f153 the counter would still be rolling |
| 3 | counter exit / swoop to fly-through | exit 5.4-5.65, swoop 5.4-6.0 | **exit 5.9-6.15 (f177-f184), swoop 5.9-6.8 (f177-f204)**, gap 120 -> 300 over the swoop, `whoosh_slow` pass 6.3 | "layers hain." runs to 6.65; pane 01 must arrive on "Andhera" |
| 4 | tag / pane arrivals 01-11 (C6) | every 0.6 s, 6.0-11.4 | **f204, f217, f230, f259, f268, f278, f288, f300, f333, f343** (§3.2) | each tagged word arrives on its spoken word |
| 5 | tags 05 + 06 | two tags | **one 2-line tag block** `05 · rim light` / `06 · saaya` from f268 (camera passes 06 at f278 with its tick) | 05-07 must fit the 9.30-9.72 pause; one block keeps every tag >= 0.75 s at <= 2 blocks |
| 6 | tag 08 `lafz` / 09+10 `chamak` | 10.2 / 10.8 | **f300 (on "lafz" 10.005) / f333 (on "chamak" 11.124)** | VO_TIMING proposed "Har" onsets; the tag names the noun, so it lands on the noun |
| 7 | flick 2 OFF / final ON (+ sparkle) | f414 / f432 | **f422 (bina 14.051) / f446 (zinda 14.869)**; flick 1 f396 and ON f405 unchanged | flicks on "bina" / "zinda" |
| 8 | P8 push toward the portal, rack 15.0-15.8, C3 at 16.0 | 14.6 / 15.0-15.8 / 16.0 | **unchanged** | keeps the measured 16.0 camera and the C3 `center` / `r0`; the push now starts 0.27 s before the final flick (minor, §11 R6) |
| 9 | `360` lands, camera brake, L3 push 0.5 | 20.40 (f612) | **20.6 (f618)**; surge 18.6 -> 20.6; roll 18.9 -> 20.6 | "teen" at 20.590 |
| 10 | 360 lockup exit / lanes rise | 21.9-22.15 / to 22.2 | **exit 22.0-22.25 (f660-f667); lanes rise 22.2-22.5 (f666)** | "layers." ends 22.21; V8 starts 22.35 |
| 11 | lanes sink | 24.0-24.3 | **24.3-24.6 (f729-f738)**; the S3-04 rush still starts 24.0 | the legend stays while "3 tracks." is said (to 24.36) |
| 12 | caption windows | C1 to 16.25, C2 to 20.8, C3 to 24.7 | C1 `clear=[(16.25, 16.9)]` (early exit 16.0-16.25), C2 words 16.9-20.5 + `clear=[(20.6, 22.3)]`, C3 hold 0.15 (gone 24.81) | V5 ends 16.07 (est. 15.70); "teen" is a hidden word |
| 13 | re-hook VO silence | 0.44 s | **0.126 s (11.924-12.05), accepted** | VO is final; the stop is carried by the picture (stop + push 0.35 + `impact_soft`, ducked -6 by `fit_under_vo`) |
| 14 | `CUTS` | `[(0,0.6),(4.8,0.3),(12,0.35),(20.4,0.5),(26.4,0.6)]` | **`[(0.0, 0.6), (5.2333, 0.3), (12.0, 0.35), (20.6, 0.5), (26.4, 0.6)]`** | items 1, 9 |

Unchanged: hook A f0-f89 (V1A ends 2.22 <= 2.70), hook B (V1B ends 2.63), re-hook stop f360, swing 12.6, fold to 13.2, C3 cut
f504, corridor S3-01 16.8, drop-out 25.8-26.4, play click f782, C8 f788-f797, payoff f792, sub line 27.7, glint f846-f847,
lockup exit 29.1-29.45, end card 29.4, loop crossfade 33.0-33.6.

---------------------------------------------------------------------------------------------------------------

## 3. The final beat table

### 3.1 Beat by beat, with the measured VO (words.json; on = voiced onset, end = last voiced sample)

| # | f | t (s) | picture (r3) | push | VO (measured) | captions |
|---|---|---|---|---|---|---|
| 1 | 0 | 0.000 | S1 the frame PLAYING 1:1, lockup `AAP NE ISE / 0.03 sec / DEKHA` settled, chip `▶ 00:00:00:01` | 0.6 (loop) | V1A "Aap" 0.100 | hidden 0-3.0 |
| 2 | 9 | 0.300 | PAUSE: layer clock frozen at tl 0.3 until f792; chip ▶ -> ❚❚ | - | "ne ise" 0.329-0.830 | - |
| 3 | 18 | 0.600 | seam glint sweep 0.6-0.9 | - | (pause 0.83-1.03) | - |
| 4 | 27 | 0.900 | gap 0 -> 120 (to 2.4), pull-back; chip fades f24-f32 | - | "palak" 1.030, "jhapakte" 1.292, "dekha." to 2.220 | - |
| 5 | 72 | 2.400 | S2-02 orbit to side-on starts (yaw 0 -> 52, pitch 0 -> 8, easy_ease **to 5.2333**) | - | (gap 2.22-3.07) | - |
| 6 | 90 | 3.000 | **SPLICE**; counter `00 LAYERS` rises; panes light 01 -> 12 as it rolls **to 5.2333** | - | V2 "Lekin" 3.070 ... "mein..." to 4.950 | hidden 3.0-12.0 |
| 7 | **157** | **5.2333** | **side-on lands, counter `12` settles** | **L3 0.3** | "12" 5.230, "layers" 5.785, "hain." to 6.650 | - |
| 8 | **165** | **5.500** | **COVER** (side-on, `12 / LAYERS`) | - | - | - |
| 9 | **177** | **5.900** | counter exits (to 6.15, in_cubic); swoop to the fly-through pose (to 6.8), gap 120 -> 300 | - | - | - |
| 10 | **204** | **6.800** | S2-03 fly-through: pane 01 in focus, tag `01 · andhera` | C6 | V3 "Andhera." 6.800-7.570 | - |
| 11 | **217** | **7.2333** | pane 02, tag `02 · dhuaan` (no VO word; "Dhuaan." was dropped) | C6 | - | - |
| 12 | **230** | **7.6667** | pane 03 `03 · roshni` (hidden JD lives here) | C6 | "Roshni." 7.680-8.520 | - |
| 13 | **259** | **8.6333** | pane 04 `04 · chehra` (JD face pane; FACES §8 DOF note) | C6 | "Chehra." 8.640-9.300 | - |
| 14 | **268** | **8.9333** | pane 05, 2-line tag `05 · rim light` / `06 · saaya` | C6 | (pause 9.30-9.72) | - |
| 15 | **278** | **9.2667** | camera passes pane 06 (tick; the 05/06 block stays) | C6 | - | - |
| 16 | **288** | **9.600** | pane 07 `07 · chingaariyan` | C6 | V4 "Har" 9.720 | - |
| 17 | **300** | **10.000** | pane 08 `08 · lafz` | C6 | "lafz." 10.005-10.790 | - |
| 18 | **333** | **11.100** | panes 09 + 10, 2-line tag `09 · keyword` / `10 · chamak` | C6 | "Har" 10.870, "chamak." 11.124-11.924 | - |
| 19 | **343** | **11.4333** | pane 11 `11 · lakeer` | C6 | - | - |
| 20 | 360 | 12.000 | **RE-HOOK**: stop on pane 12, tag `12 · finish  ON`; swing frontal 12.6, fold to gap 30 by 13.2 | **L3 0.35** | (VO gap 0.126 s) V5 "Aur" 12.050, "layer..." 12.820-13.390 | C1 from 12.0 |
| 21 | 396 | 13.200 | settled frontal; flick 1 OFF | - | (pause 13.39-13.64) | C1 |
| 22 | 405 | 13.500 | flick ON | - | "jiske" 13.640 | C1 |
| 23 | **422** | **14.0667** | flick 2 OFF | - | "bina" 14.051 | C1 |
| 24 | 438 | 14.600 | P8 push toward the portal starts (unchanged) | - | "frame" 14.324 | C1 |
| 25 | **446** | **14.8667** | flick ON, **resolved "with"** (frame alive, sparkle) | - | "zinda" 14.869 | C1 |
| 26 | 450-474 | 15.0-15.8 | rack focus to pane 03 (aperture 0 -> 900) | - | "nahi" 15.378, "lagta." to 16.070 | C1 exits 16.0-16.25 |
| 27 | 480 | 16.000 | C3 approach into the portal disc (screen 719.4, 1267.5) | C3 ★ pre 24 f | - | - |
| 28 | 504 | 16.800 | **S3-01 corridor**, light wave 16.9-18.6 | C3 cut | V6 "Ek" 16.950, "30" 17.960, "frames." to 18.860 | C2 16.9-20.6 |
| 29 | 558 | 18.600 | S3-02 surge **to 20.6** | - | V7 "Yaani" 18.980, "second..." to 20.340 | C2 |
| 30 | 567 | 18.900 | counter rolls up with `LAYERS · 1 SECOND`, **to 20.6** | - | - | C2 |
| 31 | **618** | **20.600** | **`360` lands**, camera brakes | **L3 0.5** | "teen" 20.590, "sau saath layers." to 22.210 | hidden (C2 early exit by 20.6) |
| 32 | **660** | **22.000** | 360 lockup exits (to 22.25) | - | - | - |
| 33 | **666** | **22.200** | S3-03 three lanes rise (to 22.5), legend `VO · AI voice / SFX / MUSIC` | - | V8 "Aur" 22.350, "awaaz" 22.555, "3" 23.490, "tracks." to 24.360 | C3 22.3-24.81 |
| 34 | 720 | 24.000 | S3-04 rush: the 29 stacks fly back into the live stack (to 25.5); push in to 0.97 | - | (VO-free 24.36-26.75) | C3 |
| 35 | **729** | **24.300** | lanes sink (to 24.6) | - | - | - |
| 36 | 774 | 25.800 | DROP-OUT (frozen stack, 1 %/s) | - | - | - |
| 37 | 782 | 26.0667 | play click; layers slam (gap 60 -> 0, in_expo, to 26.4) | - | - | - |
| 38 | 788 | 26.2667 | C8 punch-in about (465, 1282) | C8 pre 4 f | - | - |
| 39 | 792 | 26.400 | **PAYOFF**: frame PLAYING; lockup `EK FRAME KI / keemat` (HouseTitle t0 26.4) | C8 + 0.4 + 0.6 | V9 "Keemat..." 26.750 | hidden 26.4-33.6 |
| 40 | 828 | 27.600 | sub `banane wala jaanta hai` rises 27.7-28.1 | - | "banane" 27.710 | - |
| 41 | 846-847 | 28.200 | hidden-JD glint (x1.20, x0.70), silent | - | "wala" 28.191-28.469 | - |
| 42 | 873 | 29.100 | payoff lockup exits (to 29.45) | - | "hai." ends 29.173 | - |
| 43 | 882 | 29.400 | END CARD (§8) over the dimmed playing frame | - | V10 "Jo" 29.600 ... "usko" 32.100, "bhejo." 32.376-32.790 | - |
| 44 | 937 | 31.250 | card settled, hold to 33.24 | - | - | - |
| 45 | 990 | 33.000 | `E.loop_world` crossfade (0.6 s) brings back the hook lockup + chip | loop push | (VO-free 32.79 -> 0.10: 0.91 s) | - |
| 46 | 997 | 33.240 | card type exits (0.36 s) | - | - | - |

Hook B (frames 0-89): unchanged from BRIEF §6.2; V1B "Ek" 0.100, "second." to 0.930, "Teen" 1.230, "saath" 1.634, "layers." to
2.630 (<= 2.70). Body identical from f90.

### 3.2 Tag blocks (<= 2 blocks on screen; block k fades out over the 0.2 s that end when block k+2 arrives)

| block | in (f) | out (fade end) | visible |
|---|---|---|---|
| 01 andhera | 204 | 7.6667 | 0.87 s |
| 02 dhuaan | 217 | 8.6333 | 1.40 s |
| 03 roshni | 230 | 8.9333 | 1.27 s |
| 04 chehra | 259 | 9.600 | 0.97 s |
| 05 rim light / 06 saaya | 268 | 10.000 | 1.07 s |
| 07 chingaariyan | 288 | 11.100 | 1.50 s |
| 08 lafz | 300 | 11.4333 | 1.43 s |
| 09 keyword / 10 chamak | 333 | 12.000 | 0.90 s |
| 11 lakeer | 343 | 12.200 (fade 12.0-12.2) | 0.77 s |
| 12 finish ON / OFF | 360 | 15.9 (BRIEF r2) | - |

C6 rack: 9 f focus ramp before each arrival (every interval is >= 9 f; f333 -> f343 is 10 f).

### 3.3 Put this in the reel module (the SFX module reads it; keys exist in `ek_frame_ki_keemat_sfx.EV`)

```python
F = lambda f: round(f / 30.0, 4)
SFX_EVENTS = dict(
    land12=F(157),                      # 5.2333 (the 00 -> 12 slot_tick then lasts 2.2333 s automatically)
    swoop=6.3,                          # whoosh pass in the 5.9-6.8 swoop
    tags=(F(204), F(217), F(230), F(259), F(268), F(278), F(288), F(300), F(333), F(343)),   # 01..08, 09/10, 11
    flicks=(F(396), F(405), F(422), F(446)),
    alive=F(446),
    land360=F(618),                     # 20.6
    lanes=F(666),                       # 22.2
)
```
Every other EV key stays (BRIEF r2 values). `events()` raises on an unknown key or a DUR mismatch.

---------------------------------------------------------------------------------------------------------------

## 4. Every asset, with its path (each checked with `ls` today)

### 4.1 VO (final; `<RW>/vo/`)
| file | use |
|---|---|
| `vo_stem.wav` (= `ek_frame_ki_keemat_vo.wav`, byte-identical) | hook A + body, V10 "usko"; 48 kHz 24-bit **mono**, 33.600 s |
| `words.json` (= `vo_stem.words.json` = `ek_frame_ki_keemat_vo.words.json`) | 61 words, reel time; carries `hide` flags, but `SC.load_words` drops them (use the windows of §6) |
| `ek_frame_ki_keemat_hookb_vo.wav` + `.words.json` | hook B 0-3.0 s, 6 words |
| `ek_frame_ki_keemat_vo_usey.wav` + `.words.json`, `ek_frame_ki_keemat_hookb_vo_usey.*` | fallback if the card stays `USSE YEH` (V10 ends 33.07) |
| `final.json`, `verify.json`, `cands.json`, `credits.json`, `raw/` | provenance (VO_TIMING §7). `vo_timeline.png` and `asr/` were not restored (not needed) |

### 4.2 Faces
`<P>/ek_frame_ki_keemat_faces.py` (`FF`, read-only from the reel); stills `<RW>/faces_test/` (`stills.json`, f0000 ... f1007,
pane04-06); `<RW>/qa/faces_check.png` (overwrite with the real f0); sources `workspace/brand_reels/charsheet/cutouts/
suit_threequarter.{png,json}`, `_depth.png`, `crops/suit_threequarter{,_2x}.png`.

### 4.3 3D / sprites
No Blender props. Your module caches `<RW>/sprites/stack_flat.npz` (BRIEF §7.3) and the layer sprites; `<RW>/sprites/` does not
exist yet (create it).

### 4.4 Audio (the mix stage regenerates all of it; **old LUFS / gain numbers are void**)
| what | module | output |
|---|---|---|
| music bed + stems | `<P>/ek_frame_ki_keemat_music.py` (`render`, `mix`) | `<RW>/music/music_full.wav` (+ stems), final mix `<RW>/audio/ek_frame_ki_keemat_mix.wav` (+ hook B) |
| SFX stems A / B | `<P>/ek_frame_ki_keemat_sfx.py` (`build`, reads your `SFX_EVENTS`) | `<RW>/audio/ek_frame_ki_keemat_sfx_stem.wav`, `_hookb_sfx_stem.wav`, `_cues.json`, `_qa_cues.json` |

The bed and the SFX stem are rebuilt on the rebuilt sound kit (`epic_sfx` / `epic_music` / `epic_mix` in `<P>`, ready once
`workspace/brand_reels/wf/KIT_READY` exists; check `kit_reel_issues.json` then). The -18 / -14 LUFS, cue gains and LRA values in
SOUND.md / MUSIC_*.md were measured on the old kit: re-measure after the rebuild. Your module: `BED = None`, `cues(): return []`.

---------------------------------------------------------------------------------------------------------------

## 5. Module build notes (on top of BRIEF §7, §8, §10, §17)

- Contract as BRIEF §17.2 with `CUTS` from §2 item 14 and `SFX_EVENTS` from §3.3. Keep `CTA = 'USKO YEH'` (matches the VO
  stem) until the lead answers (§11 R1).
- Camera keys to re-time (all in-shot `K.Cam` moves): orbit end 5.2333; swoop 5.9-6.8; fly-through poses arrive at the frames of
  §3.2 (an arrival table, not a 0.6 s cadence); surge 18.6-20.6 and the brake at 20.6. The P8 push (14.6-16.0) and every camera
  from 12.0-16.8 and 24.0 onwards stay as BRIEF r2.
- Samples (BRIEF §10, shifted): 2 for 0-0.9, 13.2-16.0, 20.6-24.0, 25.6-26.267, 26.6-33.6; 3 for 0.9-5.9 (5 for the orbit peak
  3.3-4.6) and 16.8-18.6 after the C3 settle; **7 for the swoop 5.9-6.8**, 18.6-20.6, 24.0-25.6; 5 for 6.8-13.2; the plan's
  policy inside the C3 and C8 windows.
- Faces: `FF.draw_all(cv, FF.layer_clock(t))` in assembled states, `FF.pane(i, bg)` in exploded ones; the focus pane 04 at f259
  and 05 at f268 draw with `dof=False` or `focus_dist = cam.depth(pane centre)` (FACES §8). C8 centre `FF.eye_screen()` =
  (465.7, 1282.0).
- `camspec.py` and `<RW>/previs/` were lost with the workspace. The C3 numbers (centre (719.4, 1267.5), disc r 38.2, `r0` 41.0)
  must be re-derived in your `--selftest` from `cam.project` of the pane-03 disc (frame px (812, 1120), r 58) at the 16.0
  camera; if the projection differs by > 0.5 px, use the projected centre and `r0 = r + 2.8`, and note it.
- Text-block log (BRIEF §17.5) with the r3 times: counter 3.0-6.15; tags 6.8-12.2 (§3.2); 360 counter 18.9-22.25; legend
  22.2-24.6; captions per §6.

---------------------------------------------------------------------------------------------------------------

## 6. Captions plan (`snake_captions`; dry run on the real words today: `check() == []` for all three)

Words: `SC.load_words('<RW>/vo/words.json')`, selected by time window (the loader drops `line` and `hide`). Captions only where
no designed type says the line. `max_words=3`.

| inst | words (start in) | params | chunks (measured, in -> gone) | bbox (px) |
|---|---|---|---|---|
| C1 | 12.0-16.25 (V5) | `band='upper', y=420, hold=0.15, clear=[(16.25, 16.9)]`, `avoid=lambda t: [stack_rect(max(t, 13.2)), (245, 565, 715, 635)]` (2nd rect = tag 12, to 15.9) | `Aur ek *layer*...` 12.0-13.59 · `jiske bina` 13.59-14.27 · `frame *zinda*` 14.27-15.33 · `nahi lagta` 15.33-16.25 (early exit) | y 280-466, x 241-875 |
| C2 | 16.9-20.5 (V6 + V7 to "second...") | `band='lower', hold=0.15, clear=[(20.6, 22.3)]`, `avoid=lambda t: [(100, 280, 980, 560)] if t >= 18.9 else []` | `Ek second mein` 16.9-17.91 · `*30* frames` 17.91-18.93 · `Yaani har second...` 18.93-20.60 (early exit) | y 1167-1356, x 155-880 |
| C3 | 22.1-24.7 (V8) | `band='upper', y=420, hold=0.15, avoid=[(80, 1300, 470, 1470)]` | `Aur *awaaz* ke` 22.30-23.44 · `3 tracks` 23.44-24.81 | y 310-506, x 234-882 |

The dry run used a static stand-in for `stack_rect` ((172, 495, 908, 1824)); re-run `check()` with the module's real
`stack_rect(t)`. Hidden: 0-12.0, 20.6-22.3, 26.4-33.6. SRT: `cap.save_srt('<RW>/captions/ek_frame_ki_keemat.srt')` from the
union (sentence case, house spelling, V10 token `usko`). Keywords: *layer*, *zinda*, *30*, *awaaz*.

---------------------------------------------------------------------------------------------------------------

## 7. Transitions (`jawad_tx`; <= 4 features, <= 2 ★)

| id | where | call | notes |
|---|---|---|---|
| **C3 ★** | cut 16.8 (f504), pre 24 f, post 8 f | `X.Plan` step `('C3', 16.8, dict(center=(719.4, 1267.5), r0=41.0, rim=False))` | plan cues: `reverse_swell` -3 ends 16.7333, `air_zoom` -6 + `impact_soft` -1 at 16.8 (measured today) |
| **C8** | cut 26.4 (f792), pre 4 f, post 6 f | step `('C8', 26.4, dict(center=(465.0, 1282.0), s1=1.25, b0=1.1))` | plan cues: `whip` -6 at 26.3667, `impact_soft` 0 at 26.4 (the sfx module replaces it with the reveal stack); push 0.4 + `cuts` 0.6 (R2) |
| C6 | 10 arrivals f204-f343 (in-shot) | `K.Cam(..., focus_dist=...)`, aperture 420, 9 f ramp | `X.TX['C6']` not used |
| L3 | 0.0, 5.2333, 12.0, 20.6, 26.4 | `CUTS` in `G.tx_finish` | glue |

`post(cv, t)`: `kw = merge(PLAN.post_kw(t), CARD.post_kw(t, 29.4, DUR))`; `G.tx_finish(cv, t, 'ember', cuts=CUTS, **kw)`. Half
switch (`X.side_b`) at 16.8 and 26.4; no blur across f503/f504 and f791/f792.

---------------------------------------------------------------------------------------------------------------

## 8. End card (measured today with `endcard.EndCard`)

`CARD = E.EndCard('USKO YEH', 'bhejo', sub='jo kehta hai "editing mein kya hai?"', handle=False, monogram='JD', dur=4.2,
y_mono=365.0, y_key=715.0, y_sub=922.0)`, `T_END = 29.4`. settle 1.85 s, **hold 1.99 s (31.25-33.24)**, exit 0.36 s.
Boxes: monogram 420-660 x 245-485; caps 312.2-767.8 x 522.7-583.0 (`USSE YEH`: 325.4-754.6); keyword 350.3-729.7 x 643-867;
sub 160-920 x 907-937. Signature drawn by the reel (R1): `J.signature(cv, 760, 1575, opacity=ramp(t, 30.4, 30.85, 'inout_sine')
* (1 - ramp(t, 33.24, 33.5667, 'in_cubic')))`, ink 257.7 x 23.7 px -> box 631-889 x 1563-1587 (x < 930). "bhejo" (32.376) is
spoken inside the hold.

## 9. Loop bridge

The frame plays on with `tl = t - 33.6` from 26.4 (f1007 is the instant before f0); `E.loop_world(world, t, DUR, d=0.6)`
crossfades the hook lockup + chip back in over 33.0-33.6; card exits 33.24-33.6; the loop push rises into f1007 and
`cuts=[(0.0, 0.6)]` carries it over f0. Audio: card `reverse_swell` and the music `reverse_cymbal` end on 33.600, frame 0's
`impact_soft` (cue `dur=0.25`) is the release. VO-free across the seam 0.91 s (32.79 -> 0.10). Check `E.seam_report(...)['ok']`.

---------------------------------------------------------------------------------------------------------------

## 10. Commands (from `<P>`; heavy work only through the semaphore, `--workers 1`)

```bash
H=tools/heavy.sh; RW=/home/user/100/workspace/jawad_reels/ek_frame_ki_keemat
$H python3 ek_frame_ki_keemat.py --selftest
$H python3 render.py ek_frame_ki_keemat --stills 5.2333,5.5,8.6333,13.2,16.0 --samples 1 --workers 1 --no-audio      # GATE
$H python3 render.py ek_frame_ki_keemat --stills 0,0.3,0.6,1.5,2.4,6.3,6.8,9.2667,11.1,12.0,13.5,14.0667,14.8667,15.4,16.0,16.5,16.8,19.5,20.6,22.2,23.0,25.9,26.267,26.4,28.167,28.2,28.233,28.267,31.5,33.567 --samples 1 --workers 1 --no-audio
$H python3 render.py ek_frame_ki_keemat --sheet 24 --samples 1 --workers 1 --no-audio
$H python3 render.py ek_frame_ki_keemat --preview --workers 1 --no-sfx-build --audio $RW/vo/vo_stem.wav               # until the mix exists
# after KIT_READY + the mix stage:
$H python3 ek_frame_ki_keemat_sfx.py build && $H python3 ek_frame_ki_keemat_music.py render && $H python3 ek_frame_ki_keemat_music.py mix
$H python3 render.py ek_frame_ki_keemat --workers 1 --no-sfx-build --audio $RW/audio/ek_frame_ki_keemat_mix.wav
$H python3 render.py ek_frame_ki_keemat_hookb --range 0 3.0 --workers 1 --no-audio
```
Disk: 24 GB free on `/` today; keep `<RW>` <= 2 GB (BRIEF §17.4).

---------------------------------------------------------------------------------------------------------------

## 11. Open risks (owner · what to do)

1. **CTA spelling (lead).** SLATE §5.1 locks `USSE YEH / bhejo`; BRIEF r2 builds `USKO YEH` and the default VO stem says "usko".
   LEAD_DECISIONS does not settle it. Build `USKO`; the fallback is three swaps (`CTA`, `vo_usey` stem + words, SRT / IG token
   `usey`), no credits.
2. **Re-hook silence 0.126 s (viral-strategist, on the preview).** VO is final (LEAD 3); if the stop does not read, the only
   picture-side lever is a stronger stop (push 0.35 -> 0.45), never moving V5.
3. **LISTEN words jhapakte / lafz / chamak (lead, one human listen).** A re-take is allowed only for a mispronounced word, max 5
   credits this session (`<RW>/vo/credits_s3.json` does not exist yet: 0 spent).
4. **Sound kit (music-supervisor / mix stage).** The music module does not import until `epic_sfx` exists; R7 (mono VO in
   `epic_mix.mix_reel`) must be handled in the reel's mix (dual-mono copy) unless the rebuilt kit fixes it.
5. **C3 numbers without `camspec.py`** (you): re-derive in the self-test (§5).
6. **Minor:** the P8 push starts at 14.6, 0.27 s before the final flick ON (kept to protect the C3 numbers); C1's last chunk
   exits while "lagta" (to 16.07) is still spoken; V2 "layers hain." runs into the swoop start. List, do not re-render (LEAD 7).
7. **LRA (music-supervisor):** rough mixes were 1.6-1.8 LU on the old kit; LEAD 1 floor is 2.0 LU: try a gentle level ride.

## 12. Shared requests (`SHARED_REQUESTS.md`; each worked around locally, none blocks)

R1 `EndCard x_sig` (local signature, §8) · R2 `push_gain` on C8 (extra 0.6 via `cuts`) · R3 `mix_reel` SFX tail fade (the sfx
module renders the stem with `tail_fade=0`) · R4 `epic_music` per-style options (local `c08_epic` style) · R5 24-bit round trip
(1 LSB, documented) · R6 `snap_to_voice` glued words (local `fix_gap_words`) · R7 mono VO in `epic_mix` (dual-mono copy). No new
request from this hand-off (`SC.load_words` dropping `hide` is by design; the windows of §6 cover it).

---------------------------------------------------------------------------------------------------------------

## 13. QA acceptance checklist (r3; supersedes BRIEF §18 where they differ; two lenses + an independent verifier per major finding)

**Format and truth**
- [ ] ffprobe: 1080x1920, 30/1 fps, 1,008 frames, 33.600 s; audio 48 kHz, 33.600 s.
- [ ] `len(FRAME) == 12`, 12 planes per exploded scene (self-test log); spoken / shown numbers only 12, 3, 30, 360, 0.03 sec,
  00:00:00:01; lane label exactly `VO · AI voice`.
- [ ] Hidden JD in f0 at 100 % when looked for; present in the cover f165 (>= 30 px tall); luma +3 to +25 over its local
  background; glint: only f846 / f847 differ from f845 / f848, f846 +30 to +55; no SFX starts at 28.2.

**Hook and structure (r3 frames)**
- [ ] f0 lockup ink inside the safe zone; `impact_soft` onset in f0-f2; no hero in 0-2.43; VO onset <= 0.15 s; V1A ends 2.22, V1B 2.63 (<= 2.70).
- [ ] Pause at f9: ember layer pixel-identical across 0.3-26.4 at equal camera; chip ▶ on f0-f8, ❚❚ from f9.
- [ ] Counter `12` settled on f157 (±1 f) and the L3 push peaks there; counter and stack never overlap 3.0-6.15.
- [ ] Tag arrivals on f204, f217, f230, f259, f268, f288, f300, f333, f343 (±1 f); <= 2 tag blocks on every frame; every block
  visible >= 0.75 s; tags 44 px in screen space.
- [ ] Re-hook stop f360 (VO gap 0.126 s accepted); flicks change on f396, f405, f422, f446 exactly; <= 3 changes in any 30 f;
  with/without luma change 8-20 % (f395 vs f396).
- [ ] P8: f480 stack bbox x 172-908, y 514-1824 (±2 px); f474-f480 titles soft, JD + disc sharp; no orange ring around the C3
  window f486-f503; no stall f478-f483.
- [ ] C3 cut f504; `360` lands f618 with its push; lockup gone by f667; lanes up f666-f675, down f729-f738; C8 f788-f797; payoff f792; card from f882, hold >= 1.5 s (1.99).

**Layout and type**
- [ ] Ink scan of every designed string: x 70-1010, y 230-1480; x <= 930 for y 1050-1700; nothing textual below y 1620.
- [ ] <= 2 text blocks on every frame (registry + 5 fps sheet).
- [ ] Captions: `check() == []` for C1-C3 with the real `stack_rect`; C1 gone by 16.25, C2 gone by 20.6, C3 gone by 24.81;
  highlight on word onset ±1 f; never over the face; SRT exported; `30` and `3` as digits.
- [ ] Type IVORY (no designed-type pixel at 255,255,255 after the finish).

**Motion and finish**
- [ ] No full-frame flash (1st-percentile luma of push frames within ±2 of neighbours); blacks Y p0.5 >= 16 on the encoded master (LEAD 2).
- [ ] No blur across f503/f504 and f791/f792.
- [ ] Hue budget: `jawad_grade.py verify <mp4> ember` red-orange >= 60 %.
- [ ] Face `suit_threequarter` only, never warped or mirrored; scale <= 1.0 except f789-f791 (<= 1.09); no halo / fringe.
- [ ] Loop: `E.seam_report(...)['ok']`; f1007 -> f0 step <= 1.5x a normal step; lockup + chip back by f1007.

**Sound (re-measured on the rebuilt kit; the old numbers are void)**
- [ ] Mix A: -14 ±0.5 LUFS, TP <= -2.0 dBTP (wav), <= -1.5 after AAC, **LRA 2.0-9 LU** (LEAD 1); VO >= 8 LU over the bed on
  every word (7 on one-syllable words); SFX in VO windows >= 6 LU under the VO; `fit_under_vo` raised nothing.
- [ ] Cues follow `SFX_EVENTS` (`qa_measure.py cues <master> <RW>/audio/ek_frame_ki_keemat_qa_cues.json`; frames n-1/n/n+1 at
  f9, f157, f360, f504, f618, f782, f792).
- [ ] Drop-out RMS < -60 dBFS over f774-f781; loudest momentary within ±0.2 s of 26.4; phone check loses <= 7 dB on the reveal.
- [ ] Music 100 ±0.2 BPM, drop on 26.4; last 50 ms not silent; the reverse swell ends on 33.600; <= 3 SFX starts per instant.

**Delivery**
- [ ] A master (+ B only if it passes the same QA, LEAD 6; B frames 90-1007 identical to A), share encode < 100 MB, preview
  < 30 MB, cover JPG **f165**, SRT, stems; AI info ON; end card, V10 token and IG send line use one spelling; `<RW>` <= 2 GB.

## 14. Who runs next

1. **motion-timeline-builder**: `ek_frame_ki_keemat.py` + `_hookb.py` per this file; self-test; gate stills (§10) and LOOK at
   them before animating; then stills, sheet, VO-only preview.
2. **sound-designer / music-supervisor (mix stage, after KIT_READY)**: `_sfx.py build` with `SFX_EVENTS`, music render + mix,
   re-measure everything.
3. **caption-designer**: the three instances of §6 with the real `stack_rect`.
4. **lead**: R1 (CTA) and R3 (one listen).
5. **motion-qa-reviewer**: §13.
