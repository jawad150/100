# BRIEF: Reel 5 · C15 · Log Kya Kahenge (the cardboard stadium)

Date 2026-10-08 · Author: creative-director · **Revision r2** (viral gate r1 = FIX, `GATE.md`: fixes 1-5 and the
creative-director's smaller items applied; every change is listed in the **CHANGELOG** at the end) · Status: **READY TO BUILD**
(gate: the crowd still gate in §7.4, now with the 360 px head-snap check, runs before any full render) · Packet: `packet.yaml`
(same folder, version 2) · Shared change requests: `SHARED_REQUESTS.md` (same folder).

Binding sources, in order: `brand_reels/design/SLATE.md` §0, §2, §3.5 (lines 312-363), §4, §5 (SERIES BIBLE); the
`jawad-brand-reels` skill; `pipeline/jawad_reels/TOOLKIT.md` and the shared modules' docstrings (`jawad_kit`, `jawad_tx`,
`jawad_grade`, `endcard`, `snake_captions`, `vo_chain`); `brand_reels/research/transitions_sound_music_bible.md`;
`brand_reels/research/face_assets.md`; panel memos `brand_reels/design/panel_*.md` (context only).

Every on-screen line below was measured with the real sprites (`T.measure`, `J.HouseTitle`, `E.EndCard.boxes()`) and
placed on mock-up stills, which I looked at: `workspace/jawad_reels/log_kya_kahenge/layout_proofs/` (`p1`-`p6` JPG +
`layout_report.json`, produced by the scratch script described in §17.6). All times are frame-exact at 30 fps; `f` = frame
index, `t = f / 30`.

---------------------------------------------------------------------------------------------------------------

## What changed from SLATE §3.5, and why (nothing else changes)

| # | SLATE says | this brief | why |
|---|---|---|---|
| 1 | VO "≤ 15 words 8.8-14.8": "Hum saalon tak apni zindagi unke hisaab se edit karte hain... jo poori video dekhte bhi nahi." | **"Hum apni zindagi unke hisaab se edit karte hain... jo poori video dekhte bhi nahi."** (15 words) | the SLATE line is 17 words: at Vlad's processed ~2.67 words/s plus the "..." beat it needs ~6.8 s, the window is 6.0 s. Dropping "saalon tak" keeps every meaning word and the punchline. Fallback in §9. |
| 2 | "camera rises behind `street_threequarter_turn`" (9.6) | the camera **pedestals up in front of him, level (pitch 0)** while the crowd stays behind him; JD on screen 9.6-12.8 only; a cut at 12.8 to the 135 mm rows for the head tilt | the cut-out has no back view, a 2.5D plane may not be seen off-axis (face-compositor limit: yaw ≤ 4°, pitch ≤ 3°; a level pedestal keeps the plane parallel to the sensor, so it never distorts), and one still pose may hold ≤ 3.5 s |
| 3 | orbit "70° glide" | yaw 0 → 70° with `out_cubic` over exactly one bar (16.0-19.2): the camera is already moving on the reveal hit and settles edge-on on the bar line (catalogue C5 grid rule: edge-on = beat 1, start one bar earlier) | a `glide` start barely moves for the first beat, so the loudest hit of the reel would land on a still frame |
| 4 | O6 on "the rows" | O6 runs on the **card layer only** (a local masked copy, §10.3) | the shared `TX['O6']` draws its burning edge across the whole frame and spawns embers from every bright pixel (phones, eyes, floodlight); request filed |
| 5 | end-card sub "jo 'log' ki wajah se ruka hai" | **r2: "jise 'log' ka darr rokta hai"**, drawn at **50 px** (EndCard default 56 px) | gate fix 4: "ruka hai" is grammatically masculine, and the friend held back by "log" is as often a sister or a female friend, so the gender-neutral line widens the send target; *darr* echoes V1's "Sab se bara **darr**" across the loop seam. Measured (`T.measure`, `jw_body`): 632.8 px at 50 px (x 224-856, 74 px clear of x 930); 708.7 px at 56 px (x 186-894, only 36 px clear), so the 50 px local override stays (request R2) |
| 6 | (none) | hook-A text appears from `t0 = -0.1 s` (caps already rising on frame 0) | research rule "motion on frame 0, text readable by 0.5 s"; SLATE "text by 0.6 s" is met (caps settled 0.5 s, keyword readable 0.6 s, fully settled 0.833 s) |
| 7 | V7 "Us dost ko bhejo jo 'log' ki wajah se ruka hai." at the end card | **r2: "Us dost ko bhejo jise 'log' ka darr rokta hai."** (10 words), onset **31.600 s (f948)** instead of 32.0 | gate fixes 3-4: the same edit as the sub; the earlier onset puts "Us dost ko *bhejo*" under the CTA caps and keyword rising (31.55-32.3 s) and, with V6's longer window (row 10), cuts the post-payoff VO gap from 3.36 s to about 2.8 s (2.5 s if V6 runs to its 29.10 s limit) |
| 8 | V3 "Gaur se dekho... yeh crowd flat hai. Cardboard." | **r2: "Yeh crowd flat hai. Cardboard."** (5 words) | script v1 estimated (Kokoro-calibrated, no take yet) an end of ~20.25 s at 1.10x for the 8-word line against a 19.133 s window; gate approved the cut (the instruction would land after the braam has already started the reveal). "Gaur se dekho:" stays in IG caption line 3 |
| 9 | V4 "Asli log toh peeche baithe hain. Apne phone mein." | **r2: "Asli log peeche baithe hain, apne phone mein."** (8 words) | gate fix 5a: the brief's own fallback by default; it frees ~0.28 s so V4 runs at ≤ 1.06x instead of the 1.10x ceiling |
| 10 | V6 "Aur kisi aur ki nazar mein... hum bhi 'log' hain." (window to 28.667) | **r2: "Kisi aur ki nazar mein, hum bhi 'log' hain."** (9 words), window end **29.100 s** | script v1 + gate fix 3: the approved 10 words are estimated to overrun even at 1.10x (~28.78 s); the fallback also drops the "aur ... aur" double; the longer window lets V6 run at 1.04-1.06x and cross the f864 cut into the warm wide |
| 11 | spine: "four judgement lines ... 1.6 s each" | **r2: accelerating cadence** J1 3.2 · J2 4.8 · J3 6.0 · J4 7.2 s (gaps 1.6 / 1.2 / 1.2 s), arrivals 10 / 8 / 6 / 6 f, whisper bursts -10 / -8 / -6 / -4 dB, the crowd leans in 1.00 → 1.03; J4 holds 2.4 s into the O2 | gate fix 2: four identical fly-outs every 1.6 s with no VO from 2.49 to 8.8 s made 6.4-8.8 s the main drop-risk window |
| 12 | hook B "f0 = 135 mm compressed rows already staring" | **r2: heads turned away on f0, a head-snap wave f3-f15 at 135 mm**, then staring | gate §2.2 (the creative-director's call): it puts the reel's device into the Trial's first half second at the size where it reads best (heads ~100 px), and the Trial's own loop seam (last frame: heads away) now cuts to heads away instead of a stare |

SLATE open questions are resolved with SLATE §7 defaults: AI label ON (§16), house spelling = the prior SRT (bari / bohat / hai /
nahi / mein), Trial-Reel eligibility unknown (hook B is rendered anyway, §6.2). Mummy/Ammi, Ubaal Chai, JD nameplate and the C08 VO
label do not concern this reel.

---------------------------------------------------------------------------------------------------------------

## 0. Deliverables

| item | spec |
|---|---|
| reel | 1080x1920, 30 fps, **DUR 35.2 s = 1,056 frames = 11 bars at 75 BPM** (24 f/beat, 96 f/bar), H.264 High yuv420p bt709 |
| versions | **A** public (hook A); **B** Trial Reel (hook B frames 0-89 spliced onto A's frames 90-1055, §6.2) |
| audio | mix A (VO + SFX + score) and mix B (VO + SFX only) for each hook version; 48 kHz 24-bit stems (VO, SFX, music); -14 LUFS ±0.5, TP ≤ -2.0 dBTP wav, ≤ -1.5 after AAC |
| encodes | master CRF 14 (Git LFS); share 2-pass ~22 Mbps +faststart, AAC 320k (< 100 MB); preview ~7 Mbps (< 30 MB); cover JPG (frame 45); SRT of the captions |
| deliver to | `reel/jawad_reels/` with prefix `jawad` (project.json `deliver`), e.g. `jawad_05_log_kya_kahenge_A.mp4` |
| platform | Instagram Reels (organic; not a paid ad, so the organic safe zone applies; the Meta ad zone is not needed) |
| AI label | "AI info" ON at upload (synthetic voice; character-sheet imagery may be AI-generated) |

---------------------------------------------------------------------------------------------------------------

## 1. Brand for this reel (tokens from project.json; never re-derive)

| token | hex | job in C15 |
|---|---|---|
| NIGHT_0 / NIGHT_1 | #070404 / #170A07 | sky, roof, field floor, shadows (70-85 % of every frame) |
| SMOKE | #2A1A15 | cardboard figure base, barrier wall, people silhouettes |
| ASH | #A8978C | floodlit card rims and the edge-on "lines of light", judgement-line secondary tone |
| FLAME | #FF6A1A | keyword glow; after 25.6 s the warm low light (first full flame colour of the reel) |
| RED / EMBER | #F2312B / #B3120E | judgement-line halo (EMBER), ember particles (O6 ramp) |
| AMBER / GOLD | #FFB547 / #FF9F1C | catch-light eyes (≤ 1.5x linear), phone glows (1.8x), floodlight lamp cores (2.6x); ≤ 5 % of the frame |
| IVORY | #FFF3E6 | all type (never pure white) |

Look **`noir_ember`** (kit look + colorist finish `G.finish`): near-monochrome warm black, one red-orange light, mono 0.85 on
everything not orange/red, crush (0.018, 0.024, 0.030), grain 0.022 at 1.7 px. Type styles: `jw_caps`, `jw_key`, `jw_body`,
`jw_handle` (no `jw_mono` string in this reel). Signature `@jawad_mp4` via `J.signature` (end card). Wardrobe: **streetwear only**.

---------------------------------------------------------------------------------------------------------------

## 2. Verified copy table and Do-not-claim

Status key: `verified` = quoted from SLATE §3.5 (approved concept) or a measured fact; `edit` = changed here for the reason given.

| id | exact text | source | status | used in |
|---|---|---|---|---|
| H1c | `LOG KYA` | SLATE §3.5 hook A | verified | hook A lockup caps |
| H1k | `kahenge?` | SLATE §3.5 hook A | verified | hook A keyword |
| H2a | `YEH` | SLATE §3.5 hook B | verified | hook B caps |
| H2k | `log` | SLATE §3.5 hook B | verified | hook B keyword |
| H2b | `HAIN KAUN?` | SLATE §3.5 hook B | verified | hook B caps line 3 |
| J1 | `Yeh bhi koi` / `kaam hai?` (two lines) | SLATE §3.5 spine | verified (line break added for width) | judgement 1 |
| J2 | `Paise milte hain?` | SLATE §3.5 | verified | judgement 2 |
| J3 | `Log hasenge.` | SLATE §3.5 | verified | judgement 3 |
| J4 | `Naukri kab karoge?` | SLATE §3.5 | verified | judgement 4 |
| P1c | `LOG` | SLATE §3.5 payoff | verified | payoff caps |
| P1k | `busy` | SLATE §3.5 payoff | verified | payoff keyword |
| P1b | `HAIN.` | SLATE §3.5 payoff | verified | payoff caps line 3 |
| E1c | `US DOST KO` | SLATE §3.5 / §5.1 | verified | end-card CTA caps |
| E1k | `bhejo` | SLATE §3.5 / §5.1 | verified | end-card keyword |
| E1s | `jise 'log' ka darr rokta hai` | SLATE §3.5 sub, edited by gate fix 4 (r2) | **edit** (approved here; gender-neutral, echoes V1's *darr*) | end-card sub |
| SIG | `@jawad_mp4` | brand | verified | end card |
| V1 | `Sab se bara darr, log kya kahenge.` | SLATE §3.5 (colon → comma for the TTS) | verified | VO hook A |
| V1B | `Yeh 'log'... asal mein hain kaun?` | SLATE §3.5 | verified | VO hook B |
| V2 | `Hum apni zindagi unke hisaab se edit karte hain... jo poori video dekhte bhi nahi.` | SLATE §3.5 | **edit** (row 1 above) | VO |
| V3 | `Yeh crowd flat hai. Cardboard.` | SLATE §3.5, cut by script v1 (gate-approved, r2) | **edit** (row 8 above) | VO |
| V4 | `Asli log peeche baithe hain, apne phone mein.` | SLATE §3.5, brief fallback by default (gate fix 5a, r2) | **edit** (row 9 above) | VO |
| V5 | `Log busy hain... apne 'log kya kahenge' mein.` | SLATE §3.5 | verified | VO |
| V6 | `Kisi aur ki nazar mein, hum bhi 'log' hain.` | SLATE §3.5, brief fallback (script v1, gate-approved, r2) | **edit** (row 10 above) | VO |
| V7 | `Us dost ko bhejo jise 'log' ka darr rokta hai.` (DEV `उस दोस्त को भेजो जिसे 'लोग' का डर रोकता है।`) | SLATE §3.5, edited by gate fix 4 (r2) | **edit** (row 7 above) | VO end card |
| IG1 | `Log kya kahenge? Har creator, har editor ka darr` (48 characters, counted) | SLATE §3.5 | verified | IG caption line 1 |
| IG4 | `Us dost ko bhejo jise 'log' ka darr rokta hai.` | = V7 (r2) | **edit** | IG caption line 4 |
| CP | `Agar 'log' kuch na kehte, toh tum kya karte? Ek lafz mein.` | SLATE §3.5 | verified | pinned comment |

**Do not claim / never show:** any count of people ("5,000", "hazaar"); anything first-person about Jawad's life ("main",
"mera", "meri", "Main editor hoon"); real reviews, real people or faces in the crowd; any cricket cue (pitch, wickets, stumps,
scoreboard, jerseys, team colours, flags, trophies); religious, regional or national markers on any silhouette (no caps, topi,
turban, dupatta, hijab, tilak, flags); slurs, booing or obscene gestures; words inside the whisper wall; a promise of views or
results; "Comment JD"; "watch full video"; anything from Organic Fostering or Floret; the old prop library.

---------------------------------------------------------------------------------------------------------------

## 3. Director's Pass and World Bible (cinematic-director format)

**Director's Pass (decision record).**
1. Emotional core: **fear, then liberation** (the release is the payoff, never a lecture).
2. Killed (everyone's first ideas): a man ringed by whispering shadow faces; chains snapping or a bird leaving a cage; a sunrise
   "ignore the haters" speech (panel_director C15).
3. Point of view: **the compositor's eye**: an editor knows how a flat card fakes depth, so the camera itself discovers the crowd is
   2.5D. The reel is made of exactly the trick it exposes.
4. Contradiction: a roaring stadium inside a private thought; the vast crowd is paper-thin.
5. Human truth: "Jin logon ke darr se hum ruke hain, woh khud apne 'log kya kahenge' mein ruke hue hain." Everyone is someone else's "log".
6. **Single image (anchor):** at the end of the orbit (19.2-20.0 s, 135 mm), the tiers have turned edge-on into razor-thin lines of
   floodlight; behind each line a row of real people sits heads-down, faces lit only by their own phones.
7. What we refuse: a spotlight cone on a lone figure, a clunk cold open, any count, any face in the crowd, a lecture line.

**World Bible (verbatim; every shot obeys it).**
- Palette: warm black #070404, smoke grey #2A1A15 cardboard, ash #A8978C floodlit edges, amber #FFB547 eyes and phones; flame #FF6A1A only after the turn (25.6 s).
- Light logic: one hard top floodlight (interrogation, from the lamp bank top-right) until 25.6 s; after it, one low warm light from screen-left at the field's edge. Phones are the only other light, and they appear only after the reveal.
- Lens set: 24 mm amphitheatre (focal 1280 px), 135 mm compressed rows (7200 px), 85 mm JD (4533 px). Formula: focal_px = f_mm x 1920 / 36.
- Camera law: locked off while the crowd judges; one rise (9.6-12.8 s), one 70° orbit (16.0-19.2 s, the reveal); never handheld; the focus pull at 20.0 s is a lens move, not a camera move.
- Texture: noir_ember finish, fine grain 0.022 at 1.7 px, halation on the floodlight and the phones, mono except flame and amber.
- Sound motif: the whisper wall (wordless, from pitched-down reversed CC0 crowd samples).
- Recurring symbol: the edge-on card (a thin line of light).
- Forbidden: see §2 Do-not-claim, plus: more than one floodlight clunk; a spotlight cone or a lone figure under a top spotlight (his "Meeting my younger self" cover); full-frame flashes or fades; ERROR / delete dialogs; blob mascots; a centred play ring with rays; JD mirrored, warped or lip-synced.

---------------------------------------------------------------------------------------------------------------

## 4. Global craft rules (series constants, SLATE §5.1, applied here)

- **Safe zones (1080x1920):** key copy inside x 70-1010, y 230-1480 (a CTA may reach y 1600); nothing textual below y 1620; nothing
  at x > 930 for y 1050-1700; profile crop 3:4 = y 240-1680 (the cover keyword sits inside it).
- **Sizes:** hero ≥ 130 px; H2 80-120 px; every line ≤ 940 px wide (≤ 780 px in y 1050-1700); ≤ 2 text blocks on screen at once
  (designed text + caption chunk count as two).
- **Finish:** `post = G.tx_finish(...)` only; no `K.flash`, `K.fade`, `post(flash=)`; exposure pushes only; motion blur never crosses a
  cut (jawad_tx HALF rule); exits ease out ≥ 0.2 s; ≥ 3 depth layers per shot; keyword glow / underline ≤ 3 underlines per reel (here:
  payoff + end card = 2).
- **Faces:** 2.5D only; ≤ 3.5 s per still pose; display scale ≤ 1.0 of the 2x master; hard-cut swaps only; skin natural
  (`human-realism` / `photo-realism`: keep pores and beard texture, no smoothing, exposure correct for his skin tone).
- **Sound:** -14 LUFS, TP ≤ -2.0 dBTP; VO stem -16 LUFS; speech ≥ 8 LU over the music; ≤ 3 sounds start on one instant; one drop-out
  (15.2-16.0); hero hits only in VO gaps (≥ 120 ms clear before, ≥ 300 ms after an `impact_big`/`braam`).
- **Ops:** heavy jobs only through `pipeline/jawad_reels/tools/heavy.sh` (2-slot semaphore, nice 10, 2 threads); render.py
  `--workers 1` while iterating (≤ 2 for the master); check `df -h` before big writes; this reel's workspace ≤ 2 GB; no commits.

---------------------------------------------------------------------------------------------------------------

## 5. The grid and the frame-exact beat table

`GR = X.Grid(75)`: beat 24 f (0.8 s), 8th 12 f, 16th 6 f, bar 96 f (3.2 s). **Bar n starts at f = 96 n.** 11 bars: f0-f1055,
DUR 35.200 s. Beatless until f480 (the grid times the picture; the score's pulse enters on f480).

| bar | frames | s | section | picture | VO | music |
|---|---|---|---|---|---|---|
| 0 | 0-95 | 0.000-3.167 | HOOK (splice f90) | S1-01 wide, lit tiers, head-snap wave f6-f18, lockup `LOG KYA / kahenge?` | V1 f3-≤f81 | dark_drone bed (beatless) |
| 1 | 96-191 | 3.200-6.367 | JUDGEMENT (accelerating) | J1 f96, J2 f144, **J3 f180** fly out as 3D type, each faster (10 / 8 / 6 f); the crowd starts leaning in (1.00 → 1.03 by f288, same locked wide) | none (the lines are the voice) | + tension_drone from f96 (rises to f456); whisper bursts step up per line |
| 2 | 192-287 | 6.400-9.567 | JUDGEMENT (peak) | **J4 f216** (6 f, the last and loudest line) holds to the O2; O2 smoke wipe window f270-f305 | V2 starts f264 | wall + drones; ducks under VO |
| 3 | 288-383 | 9.600-12.767 | RE-HOOK 1: JD alone | S3-01 24 mm, JD small, level pedestal rise f288-f383 | V2 | drones |
| 4 | 384-479 | 12.800-15.967 | TILT + DROP-OUT | S3-02 cut f384 to 135 mm rows; heads tilt f384-f396, back f438-f450; **drop-out f456-f479** | V2 ends ≤ f445 | drones stop dead f456; silence floor |
| 5 | 480-575 | 16.000-19.167 | **REVEAL** (45 %) | S4-01 orbit yaw 0 → 70° f480-f576 (`out_cubic`) | V3 f491-≤f574 | braam hit f480 (loudest moment); 75 BPM pulse starts |
| 6 | 576-671 | 19.200-22.367 | THE SINGLE IMAGE | edge-on lines + phone-lit people; focus pull f600-f624 to the scroller | V4 f580-≤f669 | pulse + dark pad |
| 7 | 672-767 | 22.400-25.567 | O6 BURN | O6 on the card layer f672-f719 (cut f708); people stay busy f720-f767 | V5 **f672**-≤f762, pause holds f708, part 2 f710 | pulse + 8th ticks from f672 |
| 8 | 768-863 | 25.600-28.767 | **PAYOFF** (72.7 %) | S5-01 85 mm `street_chinup_gaze`; one floodlight clunk f768, warm light on; `LOG / busy / HAIN.` | V6 f780-≤**f873** (29.100 s; may cross the f864 cut) | warm pad Bbmaj7 + EP motif |
| 9 | 864-959 | 28.800-31.967 | GAG + END CARD | S6-01 warm wide (V6's tail plays over it to ≤ 29.10); last card tips f876-f888 (tap f888); end card from **f936** | V6 tail ≤ f873; gag in silence 29.10-31.60; **V7 from f948** | F/A pad, EP |
| 10 | 960-1055 | 32.000-35.167 | END CARD + LOOP | flaps rise f960-~f1020; light returns to the floodlight f1008-f1050; `loop_world` f1041-f1055 | V7 to ≤ f1053 (last word ends ≤ 35.100 s) | Dm(add9) + dark_drone back in → frame 0 |

Retention events (series rule, r2: **a visible change ≤ 2.5 s apart everywhere**; picture events, caption-chunk changes, VO turns and
hits all count, and the pedestal rise f288-f383 and the orbit f480-f575 are continuous moves): f0, f6, f18, f25 (keyword settled), f76
(lockup exit), f96, f144, f180, f216, f264 (V2), f288, f384, f438 (heads straighten), f456, f480, f576, f600, f648, f672, f720, f768,
f806 (underline), f853 (lockup exit), f864, f876, f888, f936, f948 (V7), f960, f1056 (= f0). Largest gaps between listed events:
f384 → f438 (1.8 s; V2's caption chunks change inside it) and f25 → f76 (1.7 s); the long stretches f288-f383, f480-f575 and
f960-f1055 are continuous moves (rise, orbit, flaps + light hand-back).
Midpoint break 15.2-16.0 (43-45 %); payoff 25.6 s (72.7 %); end card settled by f992.

---------------------------------------------------------------------------------------------------------------

## 6. Hook 0-3 s, frame by frame

Frame-0 rules (SLATE §2 item 7 and the research checklist): **the tiers are already lit on frame 0, no clunk at the open**; motion
already running; text readable by 0.5-0.6 s; first VO syllable by f3; a transient on f0; frame 0 must work as a silent still.

### 6.1 Hook A (public)

| f | t | picture | text | VO | sound |
|---|---|---|---|---|---|
| 0 | 0.000 | S1-01 24 mm wide, locked; tiers lit by the top floodlight (lamp bank screen x 880-1060, y 150-300, god rays down-left); ~9-10 rows of grey cardboard figures, **heads turned away**; floodlight dust drifting; cards micro-sway ±0.3° | caps `LOG KYA` already 0.1 s into its rise (HouseTitle t0 = -0.1) | (silence 3 f) | `impact_soft` -6 (frame-0 transient = loop landing); whisper wall bed running |
| 3 | 0.100 | same | caps rising | V1 onset "Sab" | |
| 6 | 0.200 | **head-snap wave starts at the centre column (x 540)** | | | `swish_small` -14 hp 5500 at f9 |
| 6-18 | 0.200-0.600 | each head snaps at `t_s(x) = 0.200 + 0.400 abs(x - 540) / 540` s: **turned (dark hair mass) → front (light face plate)** over 3 f (SNAP spring, 2 px jolt), so the wave reads as a sweep of heads going **dark → light** (§7.1, r2); two catch-light eyes fade in over the same 3 f (AMBER ≤ 1.5x linear, radius ≥ 1.5 px on rows 0-5) | caps settled f15 (0.5 s); keyword glyphs rising from f4 | "Sab se bara darr," | `lkk_whisper_swell` peak (hit) at **f12 (0.400)**, -8, hp 4500 |
| 18 | 0.600 | wave complete: the whole stadium stares at the lens | keyword readable | | `shimmer` -12 hp 5500 |
| 25 | 0.833 | | `kahenge?` fully settled (no underline in the hook) | "log kya kahenge." | |
| 45 | 1.500 | **cover frame** (stadium staring + lockup) | | | |
| 76 | 2.533 | | lockup exit starts (`out_t0`, in_cubic 0.35 s) | VO ends ≤ f81 (2.700) | |
| 87 | 2.900 | stare holds; cards sway | lockup gone (f86.5) | | |
| 90 | 3.000 | **splice frame**: A and B identical from here | none | none | wall only |
| 96 | 3.200 | J1 flies out of the crowd | | | §11 |

Ink boxes (measured): caps `LOG KYA` x 347-737, y 360-425 (86 px, 397.8 px wide); keyword `kahenge?` x 189-893, y 476-682 (210 px,
701.6 px wide); lockup centre: keyword text-box centre (540, 560), caps centre (540, 391.3). Margins ≥ 117 px. Cover crop ✓.

**Snap legibility at phone size (r2, gate fix 1).** At `CAM_WIDE` the heads are 23-61 px at 1080 px wide (projected, θ = 0: row 0 61.0,
row 3 39.5, row 5 32.0, row 9 23.2 px), so on a 360 px phone tile they are 8-20 px and an eye disc of 0.035 x head width is ≤ 1.4 px
across. The snap therefore must be carried by **luminance**, not by the eyes: every head goes from a dark hair mass to a light face
plate (§7.1), and the §7.4 gate measures it on 360 px downscales (stills 0.10 s = all turned, 0.70 s = all front). The eyes stay as
the second cue at full size.

### 6.2 Hook B (Trial Reel; frames 0-89 only)

| f | t | picture | text | VO | sound |
|---|---|---|---|---|---|
| 0 | 0.000 | S1-01B: the 135 mm compressed rows of S3-02 (pivot section, §7.1 `CAM_ROWS` at ψ = 0), locked; **heads turned away** (turned state, r2), cards micro-sway ±0.3° | caps `YEH` 0.1 s into its rise | | `impact_soft` -6 |
| 3 | 0.100 | **head-snap wave starts at the centre column**: each head snaps at `t_s(x) = 0.100 + 0.300 abs(x - 540) / 540` s, the same 3-frame turned → front flip as hook A (dark → light, eyes in; heads ~100 px, eye r ≈ 3.5-4.3 px) | | V1B onset "Yeh 'log'..." | |
| 6 | 0.200 | wave running | | | `swish_small` -14 hp 5500 |
| 12 | 0.400 | last heads start (frame edges) | | | `lkk_whisper_swell` peak (hit) -8 hp 4500 |
| 15 | 0.500 | wave complete: the rows stare at the lens | | | |
| 25 | 0.833 | | `YEH / log / HAIN KAUN?` settled | | `shimmer` -12 hp 5500 at f18 |
| 52 | 1.733 | | lockup exit (`out_t0` 1.733 → gone f63) | | |
| 57-83 | 1.900-2.767 | **O2 smoke wipe** (c = f72 2.400, pre 15, post 12) from the 135 mm rows to the S1-01 wide (B side = `S_A(t)`, post-snap, no hook-A lockup) | | V1B ends ≤ f81 | `whoosh_slow` -12 lp 1100 at f72; `impact_soft` -10 at f84 |
| 84-89 | 2.800-2.967 | wide clear, staring | none | | |
| 90 | 3.000 | splice: identical to A | | | |

Hook B lockup: `HouseTitle('YEH', 'log', underline=False)` at keyword centre (540, 560) + `T.render('HAIN KAUN?', 'jw_caps', px=86)`
centred at **(540, 752)** (rises with the caps animation starting at t0 + 0.35 s; same exit). Measured ink: x 262-819, y 361-786
(565.3 px widest line; line 3 spans y 720-786, 38 px below the keyword's descender at y 682). Build: module `log_kya_kahenge_hookb.py` (thin wrapper, §17.2); render `--range 0 3.0`, splice at f90.
Loop note: the Trial version's last frame bridges into the wide (hook A's frame 0); its own frame 0 is the 135 mm, so the seam is a
cut there. Accepted for the Trial only. Since r2 both sides of that cut show heads turned away (the end pose and B's frame 0), so the
cut changes the lens, not the crowd's state, and B's snap replays on every loop like A's. Captions: all of V1B is hidden (§15); the
lockup carries the whole question for muted viewers.

---------------------------------------------------------------------------------------------------------------

## 7. Shot list, world and geometry (shot-list template; World Bible applies to every row)

### 7.1 World (starting geometry, verified by projection with `K.Cam`; units mm; x right, y down, z away from the hook camera)

- Bowl centre F = (0, 0, 0). Tier row i = 0..9: radius `R_i = 7000 + 800 i`, seat height `h_i = 500 + 560 i` (y = -h_i), arc
  θ ∈ [-75°, +60°] (θ = 0 straight ahead of the hook camera, + to screen-right). Low barrier wall at radius 6600, 800 high (SMOKE,
  ASH top edge). Field floor y = 0 (NIGHT_1 with a soft floodlit pool). No pitch, no lines, no markings.
- **Cardboard strips** (the crowd): planes of 4 seated figures (2080 x 1100: bottom at `h_i - 150`, head tops at `h_i + 950`), each
  strip yawed to face F. 8-12 strip variants (randomised order and horizontal flips). Front texture: printed grey silhouettes
  (`mix(SMOKE, ASH, 0.35)`, top-down floodlight gradient), **two states with a tonal flip** (r2, gate fix 1; the snap must read at
  phone size without the eyes):
  - *turned* (back of head): a **dark hair mass**: the whole head at **x0.75** of the print grey, darkening further toward the crown
    (a linear ramp from x0.75 at 45 % of the head height, measured from the top, to **x0.60** at 15 % and above); no eyes.
  - *front* (face blank): a **light face plate**: an oval 0.72 head width x 0.80 head height, centred 6 % of the head height below the
    head centre, at **+40 %** luminance (soft 1 px edge), the hair around it at x1.0; every channel clamped ≤ ASH (the plate peaks at
    ~0.085 linear luminance against ASH's 0.32, so the clamp never bites); plus two catch-light eyes: discs 0.36 head width apart at
    eye height (2 % of the head height above the head centre), AMBER at 1.2-1.5x linear (**never above 1.5x**), radius
    **max(0.035 x head width, 1.5 px) on rows 0-5** in `CAM_WIDE` screen px (rows 6-9 keep 0.035 x head width: their heads are
    23-29 px and the tonal flip carries them). Strip textures are shared by every instance and camera, so draw the eyes as a separate
    per-instance layer (2 discs per figure, radius from that instance's `CAM_WIDE` scale); in `CAM_ROWS` (heads ~100 px) the same layer
    gives r ≈ 3.5-4.3 px.
  - The snap is a per-head state blend (3 f): turned → front multiplies the head's mean luminance by 1.73 (0.712 → 1.230 of the print
    grey, area-weighted over the head oval; the face plate covers 58 % of it) before the finish. On a noir_ember mock of this wide
    (scratch, see CHANGELOG r2: the 153 on-screen figures of the 475 in the arc, drawn as simple seated silhouettes at their projected
    sizes over the noir_ember backdrop, `G.finish` + `to_srgb8`, viewed at 360 px) the head pixels' mean 8-bit luma
    (eyes masked out) rises **25.1 % at full size and 25.6 % on the 360 px tile** (58.0 → 72.8), against **0.1 %** for the r1 spec (same
    grey in both states, eyes only). The gate threshold is in §7.4.
  A bright cut-edge band along every silhouette outline (12 mm of board, i.e. 6 px of a 0.5 px/mm texture; ASH x1.6 front, warm brown
  x1.4 back) so near-edge-on cards collapse into bright slivers. **Its opacity follows the card's obliquity** (r2): 0.4 when the card faces
  the camera (`|dot(view_dir, card_normal)| ≥ 0.95`, every card in the hook wide), rising linearly to 1.0 at `|dot| ≤ 0.60` (the orbit).
  At full strength in the wide it is a constant bright ring round every small head in both states and dilutes the flip (mock with the
  first-pass values x0.775 / +35 %: 17.9 % at full strength, 21.5 % at half strength, 29.8 % without it). **Edge-on
  rendering:** a plane draws nothing at exactly 90°, so when `|dot(view_dir, card_normal)| < 0.2` also draw the board's 12 mm cut edge
  as an emissive line sprite on the card's projected vertical axis (width 3-5 px, height = the card's projected height, ASH x1.4 with a
  2 px glow, opacity `1 - |dot| / 0.2`): these are the **lines of light** (vertical, because the cards stand upright and the orbit turns
  about a vertical axis). From the side the real people behind each row read in profile, heads bowed over glowing phones.
  Back texture (shown when `dot(normal, cam->card) > 0`, mirrored): corrugated board `K.mix(SMOKE, GOLD, 0.30) x 1.2` with vertical
  flutes every 8 mm (±6 % luminance), 2-3 strips of packing tape per card (48 mm, AMBER-tinted, +25 % luminance), and one wooden
  easel strut per figure (a 40 mm plank plane perpendicular to the card, from 60 % height to the seat 450 mm behind;
  `K.mix(SMOKE, GOLD, 0.45)` with grain lines). Silhouette rules: head + shoulders seated; hair shapes varied (crop, side part, longer
  to the jaw, a bun in the turned state); **no** headwear, scarves, flags, jerseys, logos or any religious / regional marker.
- **Crowd lean** (r2, gate fix 2): in S2-01 every card plane (and its eye layer) is scaled about its own bottom-centre (the seat line)
  by `s(t) = 1 + 0.03 * K.EASE['in_sine'](clamp((t - 3.2) / 6.4))`: 1.000 at 3.2, 1.007 at 6.0, 1.013 at 7.2, 1.024 at 8.8, 1.030 at 9.6
  (row 0 head tops rise ~9 px, row 9 ~3 px). Camera, barrier, floor and lamp bank stay put. It holds at 1.03 to the O2 cut (f288); S3-01
  and S3-02 start at 1.00 again (a different camera, behind the smoke), and S3-02 runs its own drop-out lean 1.00 → 1.025.
- **Real people** (hidden behind the cards until the reveal): a strip 350 mm behind each card row, seats 100 mm lower, ~70 % of
  seats occupied, figures heads-bowed (top at `h_i + 700`, so the card in front hides them from every pre-reveal camera), each holding a
  phone: emissive rectangle 70 x 140 mm, AMBER x1.8, a soft underlight on the bowed face; everything else SMOKE / NIGHT_1. No eyes,
  no features, no colours other than amber.
- **The scroller**: one person in row 2, θ ≈ +19°, the focus-pull target; screen target after the pull ≈ (600, 1080); phone glow
  flickers 15 % at ~2.5 Hz (scrolling).
- **The last card**: row 9, θ ≈ +11° (hook-camera screen ≈ (820, 690-790)); it survives O6 and tips over at 29.2-29.6 s.
- **Floodlight bank**: 6 rectangular lamps on the roof edge at world ≈ (5200, -13500, 15500) → hook-camera screen ≈ (973, 172);
  lamp cores AMBER x2.6 + FLAME glow; `K.background(LOOK, t, cam, center=(0.86, 0.10))` puts the look's single key glow on the bank.
  After 25.6 s the bank is dark and the key moves screen-left: `center=(0.06, 0.50), boost=0.3` + a warm FLAME haze at the left edge.
- **Cameras** (`K.Cam`, focal in px):
  - `CAM_WIDE` (hook, judgement, S6): pos (0, -1500, 2000), pitch +10°, focal 1280, aperture 6, **focus_dist 9000** (set it: `K.Cam` defaults to the distance to the world
    origin, which is behind this camera). Projection check: row 9 card tops
    y ≈ 682, row 0 card bottoms y ≈ 1502, barrier top y ≈ 1370-1420, head sizes ≈ 23 px (row 9) to 61 px (row 0); field floor below.
    Re-projected for r2 (head width 233 mm, θ = 0): heads row 0-9 = 61.0 / 51.7 / 44.8 / 39.5 / 35.4 / 32.0 / 29.3 / 26.9 / 24.9 /
    23.2 px; natural eye radius (0.035 x head) 2.14 / 1.81 / 1.57 / 1.38 / 1.24 / 1.12 px on rows 0-5, so the 1.5 px floor lifts rows 3-5.
    **Fallback (only if the §7.4 snap check fails after the first crowd iteration; gate fix 1 (4)):** `CAM_WIDE` focal **1280 → 1600**
    in every shot that uses it (S1-01, S2-01, S6-01, S6-02: the loop needs one identical wide). Measured at 1600: heads 76.2 px (row 0)
    to 29.0 px (row 9); row 9 card tops y ≈ 613, row 0 card bottoms y ≈ 1638, barrier top y ≈ 1500-1564; the last card ≈ (884-889,
    600-734). The lamp bank would leave the frame (it projects to (1081, -26)), so move it to world **(4200, -11600, 15800)**, which
    projects to (978, 173); keep `center=(0.86, 0.10)`, and the rays centre stays `cam.project(bank)` (now (978, 173)). The S2 judgement hold plane moves
    to camera depth 1600 (1 unit = 1 px at scale 1). Re-measure the §6.1 cover and the §8 J boxes on the real frames.
  - `CAM_RISE` (S3-01): pos (193, -h, -1614), pitch 0, yaw 0, focal 1280, aperture 10, focus_dist 4114 (JD); JD plane at (900, 0, 2500) (feet), 1800 tall.
    h = 700 → 2600 (`easy_ease`, f288-f384): JD feet screen (760, 1178) → (760, 1769), head top 618 → 1209; rows y 491-1012 → 645-1294.
  - `CAM_ROWS` (S1-01B, S3-02, S4): `K.Cam.orbit(P, 16000, yaw=ψ, pitch=3, focal=7200, aperture=60, focus_dist=16000)` with pivot
    **P = (3215, -2630, 8833)** (row 3 at θ = +20°). ψ = 0 frames ~6-7 rows, heads ~100 px; at ψ = 70° the pivot cards are exactly
    edge-on (ψ + θ_p = 90°). At ψ = 70° the line of sight crosses the right flank: cull card and people planes with camera depth < 5500
    (they would be frame-filling blur) and keep 5500-9000 as the blurred cardboard-backs foreground. Tune θ-span / pitch (≤ 8° down)
    only to meet the gate numbers in §7.4.
  - `CAM_JD` (S5-01): pos (1100, -1500, -500), yaw -6°, pitch +12°, 85 mm (focal 4533), aperture 70, focus_dist 2500: the emptied
    stands fill the upper ~60 % of the frame as bokeh (tiers, phone dots), the warm light enters from the left; JD is a 2D bust over this plate.

### 7.2 Shot list

| Shot | frames (s) | Purpose | Size | Lens | Move (speed, easing) | Action (gesture-level) | Cast / Props | Light (source, side, shadows) | Atmosphere | Uncomposed element | Dur | Sound | Transition out | Anchor / Start-from |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| S1-01 | 0-95 (0.0-3.2) | inform (the judging crowd) | extreme wide | 24 mm | locked | heads turned away (dark hair masses); a wave of heads snaps to the lens from the centre out (f6-f18), each head flipping dark → light (face plate + eyes); then they stare | CROWD-CARD (front/turned), FLOOD-BANK | hard top floodlight from the bank top-right; short shadows under every head; eyes catch amber | dust in the floodlight cone; haze | one figure in row 6 is a narrower card leaning 3° off true | 3.2 | whisper wall, swell peak f12 | continuous | anchor of scene 1 |
| S1-01B | 0-89 (hook B) | inform | compressed rows | 135 mm | locked | heads turned away on f0; a head-snap wave from the centre out f3-f15 (r2); then the rows stare | CROWD-CARD | same floodlight | haze | one card's eyes 2 px lower than its neighbours | 2.8 + O2 | V1B | O2 smoke wipe (c f72) | start_from S3-02 framing |
| S2-01 | 96-287 (3.2-9.6) | change (pressure builds) | extreme wide | 24 mm | locked (the crowd leans in, the camera does not) | four judgement lines fly out of the crowd toward the lens, **faster each time** (f96 / f144 / f180 / f216; arrivals 10 / 8 / 6 / 6 f), each pushing the previous one back into depth; the whole crowd leans in 1.00 → 1.03 (card scale, `in_sine`); J4 holds as the last line until the O2 | CROWD-CARD, JUDGE-TYPE | same | haze thickens slightly with the wall | a single card sways later than its row | 6.4 | whisper bursts stepping -10 / -8 / -6 / -4 dB + whoosh_by per line | **O2** smoke wipe c f288 | anchor of scene 2; start_from S1-01 |
| S3-01 | 288-383 (9.6-12.8) | reveal character (JD alone) | wide, full body | 24 mm | level pedestal up 1900 mm, `easy_ease` | JD stands 3/4 to camera facing screen-left, motionless except idle breath; the crowd behind him stares | JD (`street_threequarter_turn`), CROWD-CARD | the same flat floodlight that lights the stands (SLATE: **no spotlight cone, no light pool around him**): a gentle crown-to-feet falloff, a small dark contact shadow under the trainers | haze between JD and the tiers | his contact shadow falls slightly left (the bank is right) | 3.2 | V2; drones | hard cut + L3 push 0.5 (f384) | anchor of scene 3 |
| S3-02 | 384-479 (12.8-16.0) | change (absurdity, then held breath) | compressed rows | 135 mm | locked | every head tilts 9° in sync on the cut (f384-f396), straightens f438-f450; during the drop-out the crowd leans in 1.00 → 1.025 | CROWD-CARD | same | haze | one head tilts 2 f late | 3.2 | board creak f384; drop-out f456-f479; heartbeat f468 | continuous (the orbit starts in the same shot) | |
| S4-01 | 480-575 (16.0-19.2) | **reveal** | compressed rows | 135 mm | orbit ψ 0 → 70°, `out_cubic` (already moving on f480) | the rows thin into slivers; near-side cards show cardboard backs, tape, struts; behind every row, people with bowed heads and phones appear | CROWD-CARD (back), REAL-PEOPLE, PHONES | floodlight rakes the card edges → lines of light; phones under-light faces | haze, embers none yet | one strip of tape has peeled at a corner and catches the light | 3.2 | braam + impact_big f480; creak f528; whoosh f576 | continuous | start_from S3-02 |
| S4-02 | 576-671 (19.2-22.4) | inform (they are busy) | compressed rows | 135 mm | locked; focus pull f600-f624 (`inout_cubic`) from the card lines to the scroller | edge-on lines hold; the scroller's thumb scrolls (glow flicker), 3 taps | REAL-PEOPLE, SCROLLER, PHONES | phones the brightest practicals; floodlight on the edges | phone glows bloom | one person two seats left looks up from his phone for 6 frames (f640-f646), then back down | 3.2 | taps f648/654/660 | O6 inside the shot | **ANCHOR (single image) f576-f599**; start_from S4-01 |
| S4-03 | 672-719 (22.4-24.0) | change (the fear burns away) | compressed rows | 135 mm | locked | the cardboard layer erodes from the lowest tier up into rising embers; the people do not react | CROWD-CARD → embers, REAL-PEOPLE | embers add warm light upward | embers rising -46 px/s | a few embers drift sideways against the rise | 1.6 | ember crackle, impact_soft f708 in V5's pause | continuous | start_from S4-02 |
| S4-04 | 720-767 (24.0-25.6) | atmosphere | compressed rows | 135 mm | locked | rows of busy people, amber dots; last embers die above | REAL-PEOPLE, PHONES | phones + dying floodlight | thin smoke | an empty seat in row 1 | 1.6 | pulse; reverse swell into f768 | hard cut + L3 0.6 + the clunk (f768) | start_from S4-03 |
| S5-01 | 768-863 (25.6-28.8) | **payoff** (liberation) | medium close-up bust | 85 mm | push-in 1.00 → 1.03 (`easy_ease`) | JD's chin lifts toward the warm light up-left; the lockup rises where he looks | JD (`street_chinup_gaze`) | the floodlight is off; one low warm FLAME light from screen-left: rim on the left of his face and hair, right side falls off; phone dots behind | warm haze at the left edge | one out-of-focus phone glow behind his right shoulder | 3.2 | clunk f768, warm pad, EP; V6 (from f780; may run past the cut to ≤ f873) | hard cut + L3 0.4 (f864) | **anchor of scene 5** |
| S6-01 | 864-935 (28.8-31.2) | atmosphere + gag | extreme wide | 24 mm (CAM_WIDE) | locked | the emptied stands in warm light, phone dots scattered; the last card tips backward (f876-f888) and lands with a soft tap | REAL-PEOPLE, LAST-CARD | warm low light from screen-left rakes the tiers | haze | one seat in row 2 holds only a phone glow, no person | 2.4 | V6's tail ≤ 29.10 (r2); swish f876; tap f888; no VO 29.10-31.60 | continuous | anchor of scene 6 |
| S6-02 | 936-1055 (31.2-35.2) | move (CTA + loop) | extreme wide | 24 mm | locked | end card builds over the world; cards rise back on their hinges row by row (f960-~f1020), heads away; the warm light hands back to the floodlight (f1008-f1050) | CROWD-CARD (turned), FLOOD-BANK | warm → top floodlight | haze | row 4 rises 2 f late | 4.0 | card.cues; flap thups; V7 from f948 (r2); wall returns | **loop seam** into S1-01 frame 0 | start_from S6-01 |

**Rhythm map:** 3.2 · 6.4 · 3.2 · 3.2 · [3.2 reveal] · 3.2 · 1.6 · 1.6 · [3.2 payoff] · 2.4 · 4.0. Long, long, then the reveal; short
burn; hold the payoff; the gag; the loop. Inside S2-01 the lines accelerate (r2): 1.6 · 1.2 · 1.2, then J4 holds 2.4 s while V2 enters. The single image lands at f576 (54.5 %) and holds 0.8 s untouched.

**Hook (0-2 s):** on screen, a lit stadium of grey figures turning their heads at you | heard, a wordless whisper swell and "Sab
se bara darr, log kya kahenge." | withheld, that they are cardboard and that nobody is really watching.

### 7.3 Layers per shot (≥ 3 depth layers each)

S1/S2/S6: far (sky haze + floodlight bank + bokeh, `K.background(LOOK, cam, center, bokeh=0.4)`), mid (tiers, cards, people), near
(barrier wall, dust motes `K.Particles` ASH x0.6 in the cone, judgement type in S2). S3-01: tiers, JD plane + contact shadow, near dust.
S3-02/S4: far rows (blurred), pivot rows (sharp), near flank backs (blurred), embers (S4-03). S5-01: stands plate (85 mm blur), phone
bokeh, JD bust, lockup.

### 7.4 GATE before animating (SLATE §3.5, binding)

Render with `heavy.sh python3 render.py log_kya_kahenge --stills 0.1,0.7,1.5,17.6,19.6 --workers 1`,
`heavy.sh python3 render.py log_kya_kahenge_hookb --stills 0.0,0.6 --workers 1` and
`heavy.sh python3 render.py log_kya_kahenge --range 16.0 19.2 --workers 1` (crowd + cameras + light only; type and faces may be
stand-ins; render the 0.0-0.7 s snap stills a second time with `LKK_NOTEXT=1`, §17.5, so the lockup's glow cannot touch the
numbers). Look at the stills (Read them) and measure:
- **Head-snap at phone size (r2, gate fix 1).** Downscale the 0.10 s (all heads turned) and 0.70 s (all front) stills to **360 x 640**
  (`cv2.INTER_AREA`) and Read both at that size. The snap must be obvious there: **mean head-pixel luma changes ≥ 15 %** between them,
  at full size and at 360 px. Head pixels = `log_kya_kahenge_crowd.head_mask(cam, t)` (a pure helper: the union of the visible,
  occlusion-aware head ovals of rows 0-9 in screen px), minus the eye discs dilated by 1 px, so the eyes cannot carry the number; luma =
  BT.709 Y of the 8-bit sRGB frame; at 360 px the mask is area-downscaled and thresholded at 0.5. Also measured: eye radius ≥ 1.5 px on
  every visible row 0-5 head (from the eye layer's geometry), eye cores ≤ 1.5x AMBER linear, and the card band opacity 0.4 in this
  wide. **Frame 0 must read as a crowd** at 360 px (seated people in rows, not a texture). The mock in §7.1 gave 25.6 %; the r1 spec
  gave 0.1 %. Hook B: the same check on 0.0 / 0.6 s of `log_kya_kahenge_hookb` (heads ~100 px). If the wide fails after the first crowd
  iteration, apply the `CAM_WIDE` focal fallback (§7.1) and re-run this check; the two-iteration rule below still applies.
- 1.5 s (wide): it reads as **a crowd of people**: ≥ 9 rows, heads 23-61 px, every front head shows two eye dots with local contrast
  ≥ 2:1 against its face; no visible repetition pattern within 3 neighbouring strips; nothing reads as a sports ground.
- 17.6 s (mid-orbit): slivers + the first backs visible; ≥ 1 tape strip and ≥ 1 strut readable.
- 19.6 s (edge-on): it reads as **cardboard**: the centre third of the frame shows ≥ 3 near-vertical bright lines ≤ 12 px wide
  (edge-on cards) with ≥ 1 strut visible behind a card, ≥ 2 rows of phone-lit bowed heads (in profile) beside them, ≥ 60 % of the frame shows the pivot section (≤ 25 % foreground blur).
- The 3.2 s range: no plane pops, no near-plane flythrough, motion blur clean (samples 7 for f480-f503, 5 to f575).
Pass → animate. Fail → iterate the crowd design (it is cheap: ~0.13 s per sample for 10 strips). Still failing after two iterations →
the lead swaps in reserve 2 (C01) for this slot (SLATE §3.5).

---------------------------------------------------------------------------------------------------------------

## 8. Every on-screen string (house spelling; measured; ≤ 2 text blocks at any frame)

| id | text | style, px | position (centre unless stated) | ink box (measured) | in → settled → out (frames) | animation |
|---|---|---|---|---|---|---|
| H1c + H1k | `LOG KYA` / `kahenge?` | `jw_caps` 86 / `jw_key` 210 | keyword centre (540, 560); caps centre (540, 391.3) | 189-893 x 360-682 | -3 → 25 → out 76-87 | `J.HouseTitle('LOG KYA', 'kahenge?', caps_px=86, key_px=210, underline=False).draw(cv, t, 540, 560, t0=-0.1, out_t0=2.533)` (hook A only) |
| H2a + H2k + H2b | `YEH` / `log` / `HAIN KAUN?` | `jw_caps` 86 / `jw_key` 210 / `jw_caps` 86 | keyword (540, 560); caps (540, 391.3); line 3 (540, 752) | 262-819 x 361-786 | -3 → 26 → out 52-63 | HouseTitle (underline=False, t0 = -0.1, out_t0 = 1.733) + line 3 rising like the caps (`K.ramp(t, 0.25, 0.85, 'out_cubic')`, 28 px rise, 6 px blur-in, same exit) (hook B only) |
| J1 | `Yeh bhi koi` / `kaam hai?` | `c15_judge` 84 (two lines, 1.18 em leading) | hold screen centre (540, 980) | 310-767 x 894-1060 | in 96, at hold depth f106 (**10 f**), front to 144, recede 144-153, fade 153-168 (gone f168) | 3D plane in CAM_WIDE (`ts.draw_plane(..., dof=False, blur=b)`, hold plane at camera depth 1280 so 1 unit = 1 px at scale 1): flies from the crowd (screen scale 0.35, DOF-blurred) to the hold depth (scale 1.0, sharp, b = 0) in its arrival time, `out_expo`; when the **next** line starts it recedes up/back to (540, 800), scale 0.72, opacity 0.45, b = 6 px (`inout_cubic`, 9 f), then fades to 0 by next start + 24 f (`inout_sine`). r2 cadence (gate fix 2): starts f96 / f144 / f180 / f216 (all on the 8th grid), arrivals **10 / 8 / 6 / 6 f**, so each line lands harder than the last; never more than 2 lines visible (checked frame by frame f90-f300: max 2) |
| J2 | `Paise milte hain?` | `c15_judge` 84 | (540, 980) | 184-900 x 944-1011 | in 144, at hold depth f152 (**8 f**), front to 180, recede 180-189, gone **f204** | same |
| J3 | `Log hasenge.` | `c15_judge` 84 | (540, 980) | 263-819 x 947-1033 | in **180**, at hold depth f186 (**6 f**), front to 216, recede 216-225, gone **f240** | same |
| J4 | `Naukri kab karoge?` | `c15_judge4` 84 (same size, hotter halo) | (540, 980) | 130-952 x 944-1033 | in **216**, at hold depth f222 (**6 f**), holds as the last and loudest line (2.4 s) until the O2 smoke covers it (~f282) | same; never enlarged (already 831 px text box at 84 px); the loudest burst (-4 dB) + the crowd's lean peak carry the escalation; the O2 wipe carries it away |
| P1 | `LOG` / `busy` / `HAIN.` | `jw_caps` 86 / `jw_key` 210 / `jw_caps` 86 | keyword centre (430, 560); caps (430, 391.3); underline at y 711.2 (412 px); `HAIN.` centre (430, 781.3) | 252-641 x 360-813 | 768 → keyword settled f793, underline done f806 → out 853-863 | `J.HouseTitle('LOG', 'busy', caps_px=86, key_px=210).draw(cv, t, 430, 560, t0=25.6, out_t0=28.433)`; `HAIN.` rises like the caps from t0 + 0.35 s (0.6 s `out_cubic`, 28 px), exits with the title |
| E1 | `US DOST KO` / `bhejo` / `jise 'log' ka darr rokta hai` (r2) / JD monogram / `@jawad_mp4` | `jw_caps` 86 / `jw_key` 200 / `jw_body` **50** / ring r 112 / `jw_handle` 34 | EndCard defaults: monogram (540, 560), keyword (540, 930), sub (540, 1165), signature (540, 1575) | monogram 420-660 x 440-680; caps 262-818 x 738-798; keyword 350-730 x 858-1082; sub **224-856** x 1148-1183 (text box at 50 px, 632.8 px wide, 74 px clear of x 930; glow ink alpha > 0.25: 223-855 x 1142-1197); signature 411-669 x 1563-1587 | 936 → settled 992 → hold to 1045 → exit 1045-1055 | `card = E.EndCard('US DOST KO', 'bhejo', sub=SUB, monogram='JD', dur=4.0)`, then `card.sub = T.render(SUB, 'jw_body', px=50.0); card._settled = None` (local override, request filed); `card.draw(cv, t, 31.2)` |
| CAP | VO captions | snake captions (white 64 / key 128) | lower band, solved off every avoid rect | see §15 | per word | §15 |

`c15_judge` = `T.style('jw_body', name='c15_judge', px=84, glow=0.35, glow_color=('EMBER', 0.9), scrim=0.8)` (ember halo = the
hostile voices; the dark scrim keeps contrast ≥ 4.5:1 over the grey crowd). `c15_judge4` (J4 only, r2) = the same with `glow=0.5`
(text box unchanged: 831.0 x 58.9 px for both, measured). Text blocks at once: hook (lockup + one caption chunk),
3.2-8.8 (front line + one receding line, no captions; J4 alone 8.0-8.8), 8.8-9.4 (J4 + caption), payoff (lockup + caption), end card (card only;
captions hidden). Lines within 40 px of a safe edge: **none** (closest: J4 at 58 px; the end-card signature sits at the house
position y 1575, 33 px above the 1620 text floor, by design).

---------------------------------------------------------------------------------------------------------------

## 9. VO beat plan (Vlad, `elevenlabs_v4`, Devanagari text; per-beat takes; placed at the target onsets) · r2

r2 folds in the script gate (GATE.md fixes 3-5 and the approved script-v1 cuts). The hinglish-scriptwriter owns the takes, the token
table and the measured timings (`SCRIPT.md`, `script.json`); the windows, words and rules below are binding for them.

Rate model: measured on Vlad's casting take (SCRIPT v1 §4): 4.35 syllables/s voiced, comma 0.20-0.40 s, "..." 0.50 s, full stop
0.54-0.71 s (trimmed in assembly as stated per line). **Total 62 words** (hook A version; 61 with hook B), under the ~80-90 budget on
purpose: 3.2-8.8 s is read, not spoken (the four judgements are the crowd's voice), and 29.1-31.6 s is a silent gag.

| id | Roman Urdu (TTS meaning) | English meaning | words | target start → end (frames) | speed (vo_chain) | explains this on-screen moment | delivery |
|---|---|---|---|---|---|---|---|
| V1 | Sab se bara darr, log kya kahenge. | The biggest fear: what will people say. | 7 | 0.100 → ≤ 2.700 (f3-f81); **hard ceiling 2.850** | ≤ 1.10x | the stadium snapping its heads at you + `LOG KYA kahenge?` | low, close, almost confiding; no rise at the end |
| V1B | Yeh 'log'... asal mein hain kaun? | These 'people'... who are they really? | 6 | 0.100 → ≤ 2.700 | ≤ 1.10x | the rows snapping round to stare + `YEH log HAIN KAUN?` | curious, slightly amused on "kaun" |
| V2 | Hum apni zindagi unke hisaab se edit karte hain... jo poori video dekhte bhi nahi. | We edit our lives to suit them... who don't even watch the full video. | 15 | 8.800 → ≤ 14.833 (f264-f445); the "..." pause trimmed to **0.30 s** in assembly | ≤ 1.10x | J4 still hanging in the air (8.8-9.4), then JD alone in the arena with the crowd at his back (9.6-12.8); "jo poori video dekhte bhi nahi" lands on the heads tilting in sync (12.8-13.2) | wry on "edit", a small smile on "dekhte bhi nahi" |
| V3 | Yeh crowd flat hai. Cardboard. | This crowd is flat. Cardboard. | 5 | part 1 at 16.367 (f491); "Cardboard." at **18.200 (f546)** (allowed 18.0-18.3); ends ≤ 19.133 (f574) | ≤ 1.10x | the orbit (`out_cubic`, measured yaw): "Yeh" 22°, ***flat*** 16.96 s at 46° as the cards thin, ***Cardboard*** 18.20 s at 68° on the backs, tape and struts | quiet discovery; "Cardboard." dry, flat, a beat on its own |
| V4 | Asli log peeche baithe hain, apne phone mein. | The real people sit behind, in their own phones. | 8 | 19.333 → ≤ 22.300 (f580-f669) | **≤ 1.06x** | the people behind the lines; "apne phone mein" on the focused scroller and his taps (21.6-22.0) | matter-of-fact, gentle |
| V5 | Log busy hain... apne 'log kya kahenge' mein. | People are busy... in their own 'what will people say'. | 8 | **22.400 (f672**, the bar-7 downbeat with the O6 start and the kick) → ≤ 25.400 (f762); part 1 "Log busy hain..." ends ≤ 23.467 (f704); the pause contains **23.600 (f708)**; part 2 at **23.667 (f710)** | ≤ 1.10x | the cards burning away while the people never look up; *busy* lands near the downbeat | the quotable line: slow, warm, a smile in the voice |
| V6 | Kisi aur ki nazar mein, hum bhi 'log' hain. | In someone else's eyes, we are 'log' too. | 9 | 26.000 (f780) → **≤ 29.100 (f873)**; may cross the f864 cut into S6-01; ≥ 0.1 s clear of the swish at 29.200 | **1.04-1.06x** (est. end 28.74-28.79) | JD's gaze ("nazar") lifting into the warm light under `LOG busy HAIN.`; "hum bhi 'log' hain" may land on the cut to the warm wide of phone-lit people (a picture match) | soft realisation, falling cadence |
| V7 | Us dost ko bhejo jise 'log' ka darr rokta hai. | Send it to the friend whom the fear of 'log' holds back. | 10 | **31.600 (f948)** → last word ends **≤ 35.100 (f1053)** | **1.00-1.06x** | the end card: "Us dost ko *bhejo*" under the CTA caps and keyword rising (31.55-32.3), the sub `jise 'log' ka darr rokta hai` from 32.35 | warm, direct, unfinished-feeling pitch (no final cadence: it hands over to frame 0, where "Sab se bara **darr**" answers its *darr*) |

DEV for the changed lines: V3 `ये क्राउड फ़्लैट है। कार्डबोर्ड।` · V4 `असली लोग पीछे बैठे हैं, अपने फ़ोन में।` · V6 `किसी और की नज़र में, हम भी 'लोग' हैं।` · V7
`उस दोस्त को भेजो जिसे 'लोग' का डर रोकता है।` (10 words, 13 syllables; it drops वजह, pronunciation risk 7, and adds only डर, already in the
hook). V7 estimate, scaled by syllables from SCRIPT v1's calibration (11 words / 14 syllables = 2.96 s at 1.10x): ~3.0 s at 1.00x,
~2.85 s at 1.06x, so it ends ~34.45-34.65 s; the scriptwriter replaces this with the measured take.

**Overrun rules (only these, decided on the measured take):**
- V1 > 2.60 s after processing: cut its comma pause to 0.10 s; hard ceiling 2.85 s (the lockup is gone by 2.9 s); above it, one retake.
- V2 > 6.03 s with the 0.30 s pause: retake with "Hum zindagi unke hisaab se edit karte hain... jo poori video dekhte bhi nahi." (14).
- V4 and V6 are already their short versions: if one overruns at its speed above, take it up to 1.10x; never shorten further.
- V5 part 2 > 1.78 s: one retake with the "..." written as "," and part 2 placed at **23.650**; it never ends past **25.48 s** (the clunk
  guard), and the clunk never moves.
- V7 never shortens: if it overruns at 1.06x, take it up to 1.10x; the last word still ends ≤ 35.10 s.

Rules: no "main / mera / meri"; "JD" not spoken in this reel. Loanwords in Devanagari phonetics for the TTS: क्राउड (crowd), फ़्लैट (flat),
कार्डबोर्ड (cardboard), बिज़ी (busy), एडिट (edit), वीडियो (video), फ़ोन (phone). Pronunciation test first (the T0 take with कार्डबोर्ड,
बिज़ी, फ़्लैट, नज़र, क्राउड); credits for this reel ≤ 12 (3 takes plus one retake, SCRIPT §5). The z/f nukta sounds cannot be checked by ASR:
a listener (Jawad or the lead) hears T0 before T1/T2 (open question, §20). The VO stem is assembled sample-accurately at the onsets above:
`<RW>/vo/lkk_vo_A.wav` (+ `lkk_vo_B.wav`, 35.2 s each, 48 kHz 24-bit, -16 LUFS) and the merged word timings `lkk_vo_A.words.json` /
`lkk_vo_B.words.json` (reel time, keyword marks). `<RW>` = `workspace/jawad_reels/log_kya_kahenge`.

Casting brief (cinematic-director format): warm, low, unhurried; a friend who has been there; **contradiction:** he names the fear in
a near-whisper but says the truth in plain daylight. Silence sits at 15.2-16.0 (the drop-out) and 29.1-31.6 (the gag).

---------------------------------------------------------------------------------------------------------------

## 10. Transitions (catalogue ids from the bible §3; ≤ 4 features, ≤ 2 ★, never two features within 2 bars)

| # | id | frames (window; cut c) | from → to | jawad_tx call | notes |
|---|---|---|---|---|---|
| T0 | **O2** smoke wipe (hook B only) | f57-f83; c = f72 (2.400) | S1-01B 135 mm → S1-01 wide | `X.Plan([('O2', 2.4, dict(pre=15, post=12, seed=31, rise=260)), ...])` | clear by 2.8 s (SLATE); B side = `S_A(t)` without the hook-A lockup |
| T1 | **O2** smoke wipe | f270-f305; c = **f288 (9.600, bar 3)** | S2-01 → S3-01 | `('O2', 9.6, dict(pre=18, post=18, seed=37, rise=320))` | the floodlight haze carries J4 away; 36 f window (bible 24-36 f) |
| T2 | L3 exposure-push cut (glue) | c = f384 (12.800, bar 4), push 0.5 | S3-01 → S3-02 | `('L3', 12.8, dict(push_gain=0.5))` | cut on action (the heads start tilting on f384) |
| T3 | (in-shot) C5-style orbit + L3 push accent | f480-f576 (no cut); push 0.8 at f480 | S3-02 → S4-01 continuous | `K.Cam.orbit(P, 16000, yaw=70*K.EASE['out_cubic'](K.clamp((t-16.0)/3.2)), pitch=3, focal=7200, ...)`; push via `cuts=[(16.0, 0.8)]` in the finish | camera move, not a catalogue transition (C5 is spec-only in jawad_tx) |
| T4 | **O6** ember disintegration ★ (card layer only) | f672-f719; c = **f708 (23.600)**, pre 36, post 12, direction `'btt'` | S4-02 cards → S4-04 no cards (same camera) | local `o6_cards(t)` (§10.3) using `X.TX['O6']`'s window, eases and samples | starts on bar 7 (22.4), completes on an 8th inside V5's pause, embers rise over B to 24.0 |
| T5 | L3 cut (glue) + the clunk | c = f768 (25.600, bar 8), push 0.6 | S4-04 → S5-01 | `('L3', 25.6, dict(push_gain=0.6))` | the warm light switches on with the cut (4-frame ignition, local only) |
| T6 | L3 cut (glue) | c = f864 (28.800, bar 9), push 0.4 | S5-01 → S6-01 | `('L3', 28.8, dict(push_gain=0.4))` | |
| T7 | loop bridge | f1041-f1055 world crossfade; push into f0 | S6-02 → S1-01 (frame 0) | `E.loop_world(world, t, DUR, d=0.5)`; `card.post_kw(t, 31.2, 35.2)`; frame 0 `cuts=[(0.0, 0.6)]` | `world = lambda tt: PLAN.draw(tt, SCENES)` (negative t → `S_A`) |

Features: O2 (+ O2 in the Trial) and O6 ★ = 2 public / 3 Trial; spacing ≥ 7.2 s (T0 c 2.4 → T1 c 9.6; T1 → T4 14 s). No whips, no
light leaks, no Y5 wipe in this reel (organic family only, SLATE §5.2).

### 10.1 Plan

```python
GR = X.Grid(75)
STEPS = [('O2', 9.6, dict(pre=18, post=18, seed=37, rise=320.0)), ('L3', 12.8, dict(push_gain=0.5)),
         ('L3', 25.6, dict(push_gain=0.6)), ('L3', 28.8, dict(push_gain=0.4))]
SCENES = [S_A, S_B, S_C, S_D, S_E]          # S_A 0-9.6 (hook + judgements), S_B 9.6-12.8 (rise), S_C 12.8-25.6 (rows,
                                            # orbit, focus pull, O6, people), S_D 25.6-28.8 (payoff), S_E 28.8-35.2 (wide)
# hook B module: [('O2', 2.4, dict(pre=15, post=12, seed=31, rise=260.0))] + STEPS, scenes [S_HB] + SCENES
# S_HB = CAM_ROWS at psi = 0 with the r2 head-snap (heads turned on f0, wave f3-f15, section 6.2)
```

### 10.2 Samples

`samples(t)`: 3 default; inside the O2 windows 3 (Plan); **7 for f480-f503, 5 for f504-f575** (orbit; measure px/frame with
`cam.project` and keep ≤ ~6 px between sub-samples); O6 window `X.TX['O6'].samples_at(t, 23.6, pre=36, post=12)` (5 before c, 4
after); the card tip f876-f888 5; flaps f960-f1020 5.

### 10.3 O6 on the card layer only (local workaround; request R1 in SHARED_REQUESTS.md)

`S_C(t, part='all' | 'cards' | 'nocards')`. In `log_kya_kahenge.py` write `o6_cards(t)`: a copy of `jawad_tx._tx_embers` (read it;
call the shared helpers `X.grid4, X.fbm, X.up, X.mix_mask, X._gl, X._emit, X._ember_ramp, X._inv_inout_sine, X.side_b`) with
direction `'btt'`, n 4000, seed 5, life 1.2, band 20, noise 120, A = `S_C(t, 'all')`, B = `S_C(t, 'nocards')`, and two edits:
(1) the burning edge is multiplied by the card layer's alpha at t (1/4 res, dilated 2 px) so it never crosses JD, people, phones or
air; (2) particles spawn from the luminance of `S_C(t0, 'cards')` only (the frozen card layer at the window start). Window, ease and
samples stay those of `X.TX['O6']` (`pre=36, post=12`). Freeze the card source once per worker (`@functools.lru_cache(1) def cards_t0(): return S_C(22.4, 'cards')`): `X._frozen` caches by function identity, so never pass it a fresh lambda. Its post push: `X.TX['O6'].post_kw(t, 23.6, pre=36, post=12)` with
`push_gain=0.3` (softer than the default 0.5: it lands inside a VO pause). Do not call the shared O6's `cues()`; §11 has the cues.

---------------------------------------------------------------------------------------------------------------

## 11. SFX cue list (`log_kya_kahenge_sfx.py`; audio.py catalog + epic_sfx + 7 local sounds; `align='hit'` unless stated)

Local sounds (registered by `log_kya_kahenge_sfx.register()`, idempotent; each must pass `A.qc(...) == []` + a spectrogram check):
- `lkk_whisper_wall` (bed, seamless 12 s loop): sources `crowd_cheer_real` (CC0 crowd speaking ambience) + `crowd_ahh_real` (PD):
  **reversed**, resampled to -5 semitones (rate 0.75), band-pass 300-3000 Hz, then a granular layer (60 ms Hann grains, 40 grains/s,
  random positions, ±3 semitones) so no word survives; plus a breath layer `noise_band(fc 4500, bw 1.0)` with a random 5-9 Hz syllabic
  envelope (depth 0.7) at -8 dB. **Never `crowd_ooh` / `crowd_ooh_real`, never words.** QA: faster-whisper on the wall stem alone returns
  no word with probability ≥ 0.5.
- `lkk_whisper_swell` (hit = peak at 65 % of 0.6 s) and `lkk_whisper_burst` (hit = 0.1 s, 0.5 s long): envelopes of the wall source.
- `lkk_board_flex` (hit = start, 0.35 s): cardboard creak: 20-40 band-passed clicks (600-1800 Hz, Q 3) with stick-slip spacing
  8-25 ms + a low flex thump (noise 150-400 Hz).
- `lkk_ember_crackle(dur)` (align start): `_crackle(rate=120, lo=1500, hi=8000)` + lognormal pops 6/s + a low roar
  `noise_band(fc 180, bw 1.4)` at -14 (bible §4.8 recipe).
- `lkk_flood_hum` (bed): 100 Hz mains hum + 200/300/400 Hz at -6/-12/-18 dB, 0.3 Hz wobble, 0.25 s attack (the warm lamp).
- The clunk is a cue stack, not a new sound (below).

| # | t (s) | f | name | gain dB | params / mixer keys | event |
|---|---|---|---|---|---|---|
| 1 | 0.000 | 0 | `impact_soft` | -6 | lp 1100 | frame-0 transient = loop landing |
| 2 | 0.300 | 9 | `swish_small` | -14 | hp 5500 | head-snap wave (air) |
| 3 | 0.400 | 12 | `lkk_whisper_swell` | -8 | hp 4500 | peak on the snap |
| 4 | 0.600 | 18 | `shimmer` | -12 | hp 5500 | hook text readable |
| 5 | 3.200 / 4.800 / **6.000 / 7.200** | 96/144/**180/216** | `lkk_whisper_burst` | **-10 / -8 / -6 / -4** | | each judgement line, louder each time (r2) |
| 6 | 3.467 / **5.000 / 6.133 / 7.333** | 104/**150/184/220** | `whoosh_by` | -12 | dur **0.6 / 0.5 / 0.4 / 0.4**, direction 1, lp 4000 | each line's fly-in pass: hit 2 f before the line reaches its hold depth (f106 / f152 / f186 / f222) |
| 7 | 9.600 | 288 | `whoosh_slow` | -12 | lp 1100 | O2 (under V2) |
| 8 | 10.200 | 306 | `impact_soft` | -16 | lp 1100 | O2 clears |
| 9 | 12.800 | 384 | `lkk_board_flex` | -14 | lp 1100, align start | heads tilt (first cardboard hint) |
| 10 | 12.800 | 384 | `impact_soft` | -16 | lp 1100 | L3 cut accent |
| 11 | 15.200 | 456 | `reverse_swell` | -8 | duration 0.367, lp 1100 (ends here) | the suck into the drop-out |
| 12 | 15.600 | 468 | `heartbeat` | -12 | n 1, lp 900 | held breath in the drop-out |
| 13 | 16.000 | 480 | `braam` | 0 | root 36.71 Hz (D1), dur 3.2 | **reveal: the loudest moment** |
| 14 | 16.000 | 480 | `impact_big` | -2 | | reveal body + hall tail |
| 15 | 17.600 | 528 | `lkk_board_flex` | -16 | lp 1100, align start | cards flexing in the orbit (under V3) |
| 16 | 19.200 | 576 | `whoosh_slow` | -12 | lp 1100 | edge-on pass |
| 17 | 21.600 / 21.800 / 22.000 | 648/654/660 | `ui_tick` | -20 | hp 5500 | scroller taps |
| 18 | 22.400 | 672 | `lkk_ember_crackle` | -12 | duration 1.6, align start, hp 5000 | O6 erosion |
| 19 | 23.000 | 690 | `whoosh_slow` | -14 | lp 1100 | O6 midpoint |
| 20 | 23.600 | 708 | `impact_soft` | -8 | lp 1100 | O6 complete (inside V5's pause) |
| 21 | 23.600 | 708 | `sub_drop` | -10 | lp 120, dur 1.0 | |
| 22 | 25.600 | 768 | `reverse_swell` | -10 | duration 0.2, lp 1100 (ends here) | into the payoff |
| 23 | 25.597 | 768 | `ui_click` | -6 | rate 0.55 | **clunk transient (leads 3 ms)** |
| 24 | 25.600 | 768 | `impact_soft` | 0 | lp 2500 | clunk body |
| 25 | 25.600 | 768 | `sub_drop` | -6 | lp 120, dur 1.0 | clunk sub (the one floodlight clunk) |
| 26 | 25.833 | 775 | `shimmer` | -12 | hp 5500 | keyword `busy` rises |
| 27 | 26.167 | 785 | `swish_small` | -16 | hp 5500, align start | underline draws (under V6) |
| 28 | 28.800 | 864 | `impact_soft` | -12 | lp 1100 | L3 cut to the wide (r2: may sit under V6's tail; `fit_under_vo` applies) |
| 29 | 29.200 | 876 | `swish_small` | -16 | hp 5500, align start | the last card starts to fall |
| 30 | 29.600 | 888 | `card_slide` | -8 | | **the tap** |
| 31 | 29.600 | 888 | `impact_soft` | -14 | lp 900 | |
| 32 | 31.300 / 31.770 / 31.950 / 35.200 | 939/953/958/1056 | `card.cues(31.2, 35.2)` | (as returned) | swish_small, shimmer, glass_tap, reverse_swell 0.8 s ending on DUR | end card + audio loop (r2: shimmer and glass_tap now sit under V7 from 31.6; `fit_under_vo` applies, air hp 5500) |
| 33 | 32.250 / 32.730 / 33.210 / 33.690 | 967/982/996/1011 | `card_slide` | -22 | lp 2000 | flaps rising (rows 0-1, 3-4, 6-7, 9) |

Beds (bed-list, `{'name', 't0', 't1', 'gain_db', 'fade'}`): `lkk_whisper_wall` 0.0-3.2 at -24, 3.2-6.0 at -20, **6.0-8.8 at -18** (r2:
the wall swells with the faster J3/J4; fade 0.3 at each step), 8.8-15.2 at -26 (cut dead: fade 0.004 at 15.2); `room_tone` 15.2-16.0 at -40 (the drop-out floor, ~ -45 LUFS short-term), 16.0-35.2 at -34;
`lkk_flood_hum` 25.65-35.0 at -30 (fade in 0.25, out 1.4 from 33.6); `lkk_whisper_wall` 33.6-35.2 fading in to -24 at 35.2 (equals the
level at 0.0: audio loop). Under VO the sound-designer applies the bible's `fit_under_vo` (detail -6 dB, dark lp 1100, air hp 5500,
mid -2 extra); hero cues 13-14 sit in the VO gap (V2 ends ≤ 14.833, V3 starts 16.367). ≤ 3 sounds start on any instant (f480: braam +
impact_big + the score's first pulse; f768: ui_click + impact_soft + sub_drop; the reverse swells end there and do not count).
Hook B (Trial, frames 0-89 only; r2) replaces cues 2-4 with its own snap cues: `swish_small` -14 hp 5500 at 0.200 (f6),
`lkk_whisper_swell` -8 hp 4500 peak (hit) at 0.400 (f12), `shimmer` -12 hp 5500 at 0.600 (f18), plus the §6.2 O2 cues (`whoosh_slow`
-12 lp 1100 at f72, `impact_soft` -10 at f84); cue 1 (`impact_soft` -6 at f0) is shared.
Density: 47 one-shot cues forming 34 designed events in 35.2 s (~0.97 events/s; bible target 0.6-1.0). Mix the SFX stem with `A.mix(..., target_lufs=-18,
tp_ceiling=-2.0)` and render with `--no-sfx-build --audio <final mix>` (TOOLKIT pitfall 14).

---------------------------------------------------------------------------------------------------------------

## 12. Music plan (`log_kya_kahenge_music.py`, original, D minor, Sa = D, 75 BPM, 11 bars, no desi voice)

None of the four `epic_music` styles fits (drone → pulse → warm pad), and `EM.render()` fades the last 1.2 s to silence, which
breaks the loop rule. So: build an `EM.Song(35.2, 75, 'D', seed)` and arrange it with the shared instruments (`EM.kick`, `EM.pad_chord`,
`EM.epiano`, `EM.string_note`, `Song.sfx` for epic_sfx sounds), then your own bus (copy of `EM.render`'s bus: sidechain, studio reverb
-18, level rider 0.3, loudness to -18 LUFS for the VO version / -16 without, limiter -3 dBTP) **without the end fade**. Output
`<RW>/music/lkk_music.wav` (+ stems) exactly 1,689,600 samples (35.2 s at 48 kHz).

| bars (s) | section | content |
|---|---|---|
| 0-4.75 (0-15.2) | A beatless | `dark_drone` loop (epic_sfx bed) under everything, read at loop position `t mod 24`; `tension_drone` cue at 3.2 `align='start'`, `duration=12.0`, `root=36.71` (Hz, D1; it ends exactly at 15.2) |
| 15.2-16.0 | **drop-out** | gate the whole music bus (4 ms fades); nothing but the SFX floor |
| 5-7 (16.0-25.6) | B pulse | felt pulse on every beat (`EM.kick(r, 0.5)`, lp 160 Hz) f480 … f744 (12 hits); sub D1 (36.7 Hz) + D2 sustained, lp 120; dark pad (`pad_chord`, cutoff 700): bar 5 Dm (D3 F3 A3), bar 6 Bb (Bb2 D3 F3), bar 7 Gm/D (D3 G3 Bb3); from 22.4 a soft closed hat on the off-8ths (-12, hp 7000); last pulse 24.8; 25.2-25.6 pad only |
| 8-10 (25.6-35.2) | C warm | no drums. Pad warm (cutoff 1400): bar 8 Bbmaj7 (Bb2 D3 F3 A3) entering on the clunk, bar 9 F/A (A2 C3 F3 A3), bar 10 Dm(add9) (D3 F3 A3 E4). Sparse EP motif (`EM.epiano`, bright 0.6, lp 2200, -6 under VO): A4 26.4, F4 28.0, D4 30.4, C4 31.2, A3 32.8, D4 34.4 (0.75 s, ends 35.15). Beat 1 of bar 9 (29.6, the tap) stays empty. `dark_drone` fades back in 33.6-35.2 at loop position `(t - 35.2) mod 24`, so its sample at 35.2 equals its sample at 0.0 |

**r2 duck windows (gate fix 3):** the EP notes that sit "-6 under VO" follow the new VO windows: V6 26.0-29.1 (the F4 at 28.0 is inside;
the D4 at 30.4 stays free) and **V7 31.6-35.1** (the C4 at 31.2, which rings to ~31.95, is now ducked from 31.6; A3 32.8 and D4 34.4 as
before). The music-supervisor rebuilds the score with these windows; nothing else in the score changes.

No tape-stop in this reel (the drop-out is a hard gate). Music ducks 9 dB under VO and 3 dB under SFX hits in `epic_mix`. Mixes:
`M.mix_reel('log_kya_kahenge', dur=35.2, vo=lkk_vo_A.wav, sfx=<sfx stem>, music=lkk_music.wav, out_dir=<RW>/audio)` → A full mix and B VO
+ SFX; repeat with `lkk_vo_B.wav` for the Trial. Audio name: "Original audio · Log kya kahenge · @jawad_mp4".

---------------------------------------------------------------------------------------------------------------

## 13. 3D props

**None** (SLATE §3.5): the crowd, backs, struts, people and phones are procedural numpy sprites on `K.Scene` planes, built once in
`log_kya_kahenge_crowd.py` (lru_cached, read-only). No Blender job, no `assets3d_log_kya_kahenge.py`; the blender-3d-artist has no work order.

---------------------------------------------------------------------------------------------------------------

## 14. Face plan (`log_kya_kahenge_faces.py`, face-compositor; cut-outs from `workspace/brand_reels/charsheet/cutouts/`)

| shot | cut-out | look | frames | placement and scale | light | motion | caption avoid rect |
|---|---|---|---|---|---|---|---|
| S3-01 | `street_threequarter_turn` (820x2048, faces screen-left) | **D cine**: `FA.rim_light(p, FA.depth(n), light=(0.35, -0.95), gain=1.4, halo_strength=0.35, base=FA.cine_grade(p))` + a gentle vertical multiply 1.0 (crown) → 0.8 (feet) (the stadium's flat floodlight; no cone, no light pool) | in f288 (under the O2 smoke) → out f383 (cut at f384): **96 f = 3.2 s** | a plane at world (900, 0, 2500), 1800 mm tall (= 560 px at f288, scale 0.284 of the 2x master), `FA.feet_anchor`; parallel to the sensor (pedestal only, yaw = pitch = 0): screen feet (760, 1178) → (760, 1769) | top floodlight from top-right | `FA.idle` breathing only; `FA.contact_shadow` (dark, 0.9 x body width, offset 12 px to the left: the bank is right) | `jd_rect(t)` = projected plane alpha bbox + 28 px; at f288 ≈ (662, 590, 863, 1206), at f383 ≈ (662, 1181, 863, 1797) |
| S5-01 | `street_chinup_gaze` (940x964, chin up, looking up screen-left) | **A rim**: `FA.rim_light(p, FA.depth(n), light=(-0.9, -0.3))`; sides closed, no `fade_open`; bottom anchored below the frame | in f768 → out f863 (cut f864): **96 f = 3.2 s** | 2D bust, bottom-mid of the cut-out (470, 964) at screen (700, 1926); scale 0.750 → 0.7725 (`easy_ease`, ≤ 8 %/s); measured at 0.75: face 557-813 x 1304-1622, eye-mid (641, 1419), hair crest y 1238 | warm low FLAME key from screen-left (+ the noir_ember key moved left, §7.1); the right cheek falls off; no top light | `FA.idle` + push-in; the warm light ignites with the clunk (key gain 0.6 f768, 0.3 f769, 0.9 f770, 1.0 f772) | (330, 1190, 1073, 1954) for f768-f863 |

Rules: one wardrobe (streetwear); no mirroring; no other expressions; hard cuts only; skin natural under noir_ember (`G.finish` skin
protection 0.70; the colorist checks skin hue 8-29° on S5-01); halo over black ≤ +6 code values; never cover the face with type or
embers (O6 is masked to the cards; the payoff has no particles in front of the face). Export `jd_rect(t)` for the captions.

---------------------------------------------------------------------------------------------------------------

## 15. Captions plan (`snake_captions.py`, caption-designer)

`cap = SC.Captions('<RW>/vo/lkk_vo_A.words.json', band='lower', avoid=avoid_fn, hide=HIDE)`; `cap.prewarm()` in `prewarm()`;
`cap.draw(cv, t)` after `PLAN.draw` and the overlays, before `post`. Hook B uses `lkk_vo_B.words.json`.

Keywords are marked in the ROM tokens (`*word`); quotes are dropped from phrases in the caption track, kept on single words.

| VO | expected chunks (1-3 words; the chunker decides, these are the targets) | keyword per chunk |
|---|---|---|
| V1 | `Sab se` · `bara *darr*` · (`log kya kahenge` hidden) | darr |
| V1B | **all hidden** (r2, gate: the lockup `YEH / log / HAIN KAUN?` shows the whole question until 2.1 s while it is spoken) | |
| V2 | `Hum apni` · `*zindagi*` · `unke hisaab se` · `*edit* karte hain...` · `jo poori *video*` · `dekhte bhi *nahi*` | zindagi, edit, video, nahi |
| V3 | `Yeh crowd` · `*flat* hai` · `*Cardboard*` | flat, Cardboard |
| V4 | `Asli log` · `peeche baithe hain` · `apne *phone* mein` | phone |
| V5 | `Log *busy* hain...` · `apne log kya` · `*kahenge* mein` | busy, kahenge |
| V6 | `Kisi aur ki` · `*nazar* mein` · `hum bhi *'log'* hain` (*ki* may not open a chunk) | nazar, 'log' |
| V7 | hidden (the end card shows it) | |

`HIDE` (reel time): the V1 words "log kya kahenge" (from their start - 0.05 to 3.0; the hook lockup shows them); **all V1B words**
(0.0 to the last V1B word's end + 0.05; r2); everything from 31.2 to 35.2 (end card; V7 starts at 31.6 and stays hidden).
`avoid_fn(t)`: hook A lockup (161, 332, 921, 710) for t < 2.9; hook B lockup (234, 333, 847, 814) for t < 2.1; `jd_rect(t)` for 9.6-12.8;
the scroller's projected head + phone bbox + 28 px for 20.0-22.4; the payoff lockup (224, 332, 669, 841) and the bust rect (330, 1190,
1073, 1954) for 25.6-28.8. With these the V6 chunks settle between y ~ 850 and 1180 (measured free band 841-1190). **r2: V6 may run to 29.10 s across the f864
cut**, so the 25.6-28.8 avoid rects stay in force until the last V6 chunk has gone (≤ 29.10 + its tail): a chunk that spans the cut keeps
its position instead of jumping when the avoid set changes; in the S6-01 wide that band is clear (stands and barrier, no face, no type). No captions exist
3.2-8.8 (no VO). Checks: `cap.check() == []`; `cap.report()` shows no chunk inside an avoid rect; highlight within ±1 frame of each word
onset; save the SRT (`cap.save_srt`) for delivery.

---------------------------------------------------------------------------------------------------------------

## 16. Cover, post copy and labels

- **Cover:** frame **45 (1.5 s)** of version A: the staring stadium + `LOG KYA / kahenge?` (keyword band y 476-682, inside the 3:4 crop
  y 240-1680 and legible when the cover is downscaled to 240 px and to 210 px wide; check both: the keyword is ~136 px wide at 210 px,
  the 86 px caps fall to ~17 px, borderline, gate §6). Export JPG q 92 from the master.
- **IG caption** (line 1 = 48 characters, restates the hook with the search keyword "log kya kahenge"):

```
Log kya kahenge? Har creator, har editor ka darr
Hum apni zindagi unke hisaab se edit karte hain... jo poori video dekhte bhi nahi.
Gaur se dekho: log busy hain, apne 'log kya kahenge' mein.
Us dost ko bhejo jise 'log' ka darr rokta hai.
#logkyakahenge #contentcreator #editorlife #jawadmp4
```

- **Hashtags (4):** #logkyakahenge #contentcreator #editorlife #jawadmp4 (the gate suggests #videoediting as an optional 5th for the
  page's search niche: the lead's call, §20).
- **Comment prompt** (posted by @jawad_mp4 as the pinned first comment, so the caption's only ask stays the send): "Agar 'log' kuch na
  kehte, toh tum kya karte? Ek lafz mein."
- **Audio name:** "Original audio · Log kya kahenge · @jawad_mp4".
- **AI label:** turn **"AI info" ON** (synthetic voice; the character sheets may be AI-generated); SLATE §7.1 default for all five.
- Posting slot (SLATE §4): 5th of the set, Tue 27 Oct 7:00 PM PKT / 7:30 PM IST (low-confidence hypothesis). Hook B as a Trial Reel only
  if the account is eligible.

---------------------------------------------------------------------------------------------------------------

## 17. Engineering contract

### 17.1 Files (only these; never touch another reel's files; shared modules are read-only)

| path | owner | what |
|---|---|---|
| `pipeline/jawad_reels/log_kya_kahenge.py` | motion-timeline-builder | the reel module (§17.2) |
| `pipeline/jawad_reels/log_kya_kahenge_hookb.py` | motion-timeline-builder | `from log_kya_kahenge import build, DUR, LOOK, BPM; draw, post, samples, cues, prewarm = build('B')` |
| `pipeline/jawad_reels/log_kya_kahenge_crowd.py` | motion-timeline-builder | procedural crowd: strips, states (r2 tonal flip), per-instance eye layer, backs, struts, people, phones, the last card, the lean scale, `head_mask` / `eye_mask` for the §7.4 check (lru_cached, pure) |
| `pipeline/jawad_reels/log_kya_kahenge_faces.py` | face-compositor | the two looks, placements, `jd_rect(t)` |
| `pipeline/jawad_reels/log_kya_kahenge_sfx.py` | sound-designer | local sounds, `register()`, `cues()`, `beds()`, `build` CLI → SFX stem |
| `pipeline/jawad_reels/log_kya_kahenge_music.py` | music-supervisor | the score (§12) + `mix` CLI (epic_mix A/B) |
| `pipeline/jawad_reels/log_kya_kahenge_vo.py` | hinglish-scriptwriter | assembles the processed takes at the onsets → `lkk_vo_A/B.wav` + merged words.json |
| `brand_reels/design/reels/log_kya_kahenge/vo/` | hinglish-scriptwriter | `dev_*.txt`, `rom_*.txt` (token-aligned), `script.md` |
| `<RW>` = `workspace/jawad_reels/log_kya_kahenge/` | all | `vo/`, `audio/`, `music/`, `captions/`, `gate/`, `out/` (render.py writes here: `<WS>/out/log_kya_kahenge` and `<WS>/out/log_kya_kahenge_hookb` are symlinks to `<RW>/out`), `layout_proofs/` |

### 17.2 Module contract (`log_kya_kahenge.py`)

```python
import jawad_kit                                  # FIRST
from jawad_kit import K, T, J
import jawad_tx as X, jawad_grade as G, endcard as E, snake_captions as SC
DUR, LOOK, BPM = 35.2, 'noir_ember', 75
GR = X.Grid(75)
def build(hook='A'):                              # returns draw, post, samples, cues, prewarm (pure functions of t)
    ...
draw, post, samples, cues, prewarm = build('A')
# draw(t): cv = E.loop_world(world, t, DUR, d=0.5) where world = lambda tt: PLAN.draw(tt, SCENES);
#          overlays (hook lockup, payoff lockup + HAIN.) ; card.draw(cv, t, 31.2) ; cap.draw(cv, t) ; return cv
# post(cv, t): G.tx_finish(cv, t, LOOK, cuts=[(0.0, 0.6), (16.0, 0.8)], **merge(PLAN.post_kw(t), o6_post_kw(t),
#              card.post_kw(t, 31.2, DUR)), rays=rays(t), rays_center=rays_centre(t))   # merge: sum 'push', multiply 'bloom_scale'
#   rays(t): 0.22 while the floodlight bank is in a wide frame (0-9.6 CAM_WIDE: centre (973, 172); 9.6-12.8 CAM_RISE: centre =
#            cam.project(bank), y ~3 -> ~145 as the camera rises), 0 in the 135/85 mm shots and 25.6-33.6, ramping 0 -> 0.22
#            over 33.6-35.0 in CAM_WIDE (frame 0 matches)
# cues(): [] (the sound-designer's module builds the mix; render with --no-sfx-build --audio <mix>)
```

### 17.3 Commands (all heavy work through the semaphore; run from `pipeline/jawad_reels`)

```bash
H=/home/user/100/pipeline/jawad_reels/tools/heavy.sh
$H python3 render.py log_kya_kahenge --stills 1.5,17.6,19.6 --workers 1            # GATE stills (§7.4)
$H python3 render.py log_kya_kahenge --range 16.0 19.2 --workers 1                 # GATE orbit range
$H python3 render.py log_kya_kahenge --sheet 24 --samples 1 --workers 1            # layout / timing sheet
$H python3 render.py log_kya_kahenge --preview --workers 1                         # 15 fps motion check (viral red-team)
$H python3 log_kya_kahenge_sfx.py build ; $H python3 log_kya_kahenge_music.py build ; $H python3 log_kya_kahenge_music.py mix
$H python3 render.py log_kya_kahenge --workers 2 --no-sfx-build --audio <RW>/audio/log_kya_kahenge_mix.wav   # master A
$H python3 render.py log_kya_kahenge_hookb --range 0 3.0 --workers 1 --no-audio                              # hook B frames
```
Splice B: frames 0-89 of the hook-B range + frames 90-1055 of master A (ffmpeg select by frame number, re-encode once at CRF 14),
muxed with the hook-B mix. Verify both with `python3 /home/user/100/plugins/reels-studio/skills/reels-production-playbook/qa_measure.py probe <mp4> --dur 35.2 --fps 30 --size 1080x1920` (frame count 1056, bt709, AAC 48 kHz, faststart, loudness).

### 17.4 Budgets

Render: target ≤ 1.2 s per sample-frame average (`render_stats.json`); crowd planes ≤ 60 on screen; type and crowd sprites built in
`prewarm`. Memory ≤ 2 GB per worker. Workspace `<RW>` ≤ 2 GB (`du -sh`), delete render parts and superseded takes/stills.

### 17.5 Text-block log

`draw` keeps a debug list (env `LKK_DEBUG=1`) of the text blocks drawn per frame; QA asserts ≤ 2 everywhere. With env `LKK_NOTEXT=1`
`draw` skips every text overlay (hook lockups, J lines, payoff lockup, end-card type, captions) for the §7.4 snap measurement; the
crowd module exports the pure helper `head_mask(cam, t) -> (1920, 1080) float32` (visible head ovals, occlusion-aware) and
`eye_mask(cam, t)` for it.

### 17.6 Layout proof (done for this brief)

Scratch script `lkk_layout_proof.py` (creative-director scratchpad) rasterised every string at its planned size and place, measured ink
boxes (alpha > 0.25) and rendered 6 mock stills on a plain `noir_ember` world; results in `<RW>/layout_proofs/layout_report.json` and
`p1-p6 *.jpg`. Builders re-measure on the real frames (QA §18).

---------------------------------------------------------------------------------------------------------------

## 18. Reel-specific QA acceptance checklist (measurable; two lenses + an independent verifier per major finding)

**Format and timing**
- [ ] ffprobe: 1080x1920, 30/1 fps, `nb_frames` = 1056, duration 35.200 s (±1 frame); audio 48 kHz, same duration.
- [ ] Every cut at its frame: f288 (O2 c), f384, f768, f864 (frame n all-B, n-1 all-A); O6 c = f708; end card starts f936; mean |Δ| of
      frame pairs shows the cut exactly there.
- [ ] Hook B splice: frames 90-1055 of A and B are bit-identical after decode (or PSNR ≥ 50 dB).

**Hook and structure**
- [ ] Frame 0: YAVG ≥ 38 (8-bit), ≥ 1 % of pixels Y ≥ 200 (the lamp bank), mean |blur(frame1) - blur(frame0)| > 0.15 code values with a Gaussian σ 3 px blur that removes the grain (motion on f0).
- [ ] Hook A text: caps ink present by f15, keyword by f18; gone by f87. Hook B text gone by f63.
- [ ] Head-snap (r2): the §7.4 snap check holds on the master too: frames 3 and 21 of A (0.10 / 0.70 s; `LKK_NOTEXT=1` re-render) at
      360 px wide show a mean head-pixel luma change ≥ 15 % (eyes masked); B the same on frames 0 and 18.
- [ ] Judgement lines (r2): starts f96 / f144 / f180 / f216 exact; each line sharp at its hold depth by f106 / f152 / f186 / f222; never
      more than 2 lines with opacity > 0.02; J3 gone by f240; J4 alone 8.0-8.8 s; crowd lean scale 1.03 ±0.002 at f287 (row 0 head
      tops ~9 px higher than at f95) and 1.00 at f288 onwards.
- [ ] VO: first word onset ≤ f3 (hard ≤ f9); V1/V1B last word ends ≤ 2.70 s (hard ceiling 2.85 s); each line inside its §9 window
      ±0.1 s (V5 from 22.400, V6 to ≤ 29.100, V7 from 31.600 with its last word ≤ 35.100); V5's pause contains 23.6 s; no VO word in
      15.85-16.30, 25.48-25.90 (hero hits clear) or **29.10-31.60** (the gag stays silent; ≥ 0.1 s before the 29.2 swish).
- [ ] **A visible change ≤ 2.5 s apart** everywhere (series rule, r2; picture change, caption-chunk change, VO turn or hit; continuous
      camera moves count); payoff at 25.6 s (72.7 %).

**Copy, layout, legibility**
- [ ] Ink scan (alpha / luma diff vs a no-text render) inside x 70-1010, y 230-1480 (end card to 1600); nothing at x > 930 in y 1050-1700;
      nothing textual below y 1620. Measured boxes within ±6 px of §8.
- [ ] ≤ 2 text blocks on every frame (`LKK_DEBUG` log); captions never overlap a designed lockup or a face rect.
- [ ] Contrast ≥ 4.5:1 for every text block against its local background (judgement lines with scrim; captions with snake scrim).
- [ ] Spelling exactly as §2 (house: bara, hai, nahi, mein, hain).

**Crowd, faces, light, colour**
- [ ] Gate stills passed (§7.4), signed in `<RW>/gate/GATE.md` with the measured numbers.
- [ ] JD on screen only f288-f383 and f768-f863 (each 96 f ≤ 105 f); scale ≤ 1.0; plane parallel to the sensor in S3-01 (pitch = yaw = 0);
      no mirroring; halo over black ≤ +6 code values; skin hue 8-29° on S5-01 face pixels.
- [ ] O6 masked: ≥ 98 % of spawned particles start inside the card alpha; outside the card layer, frames f672-f719 differ from the
      no-card scene only by additive ember light (no erosion, no edge line over people / JD / air).
- [ ] Blacks: YMIN 16-22 on every 5 fps sample; no frame-to-frame YAVG jump > 25 except at the pushes f384/f480/f768/f864, where YMIN does
      not rise (no lifted blacks, no full-frame flash).
- [ ] Hue budget (`python3 jawad_grade.py verify <mp4> noir_ember`): red-orange ≥ 60 % of saturated pixels.
- [ ] The warm turn: mean SATAVG(f768-f863) ≥ 1.5 x mean SATAVG(f480-f767) (first full flame colour at the payoff).
- [ ] No cricket / flag / religious / regional cue in any 5 fps sample (visual check of the sheet).

**Sound**
- [ ] Mix A and B: -14.0 ±0.5 LUFS integrated, TP ≤ -2.0 dBTP (wav), ≤ -1.5 after AAC; LRA 5-9 LU; VO stem -16 LUFS; speech ≥ 8 LU over
      music (median of voiced frames).
- [ ] Max momentary loudness within ±0.2 s of 16.0 s; the 25.6 s clunk's momentary peak ≥ 2 LU below it; exactly one clunk (no other
      `ui_click`+`impact_soft`+`sub_drop` stack).
- [ ] Drop-out 15.2-16.0: music stem ≤ -60 dBFS; whisper wall ≤ -60 dBFS; true digital silence ≤ 8 frames; floor ≈ -45 LUFS short-term.
- [ ] Whisper wall: faster-whisper on its stem returns no word with probability ≥ 0.5.
- [ ] Every hero cue onset within ±1 frame of its picture frame (`qa_measure.py cues`); `X.check_cues` / catalog names all known.
- [ ] Loop: the score ends exactly at 1,689,600 samples with no fade; last 50 ms vs first 50 ms RMS within 6 dB; no click at the seam.

**Loop and end card**
- [ ] `E.seam_report(lambda t: render.render_still(mod, t, 1), 35.2)['ok']` is True; frame 1055 vs frame 0: crowd up, heads away,
      floodlight on, no text.
- [ ] End card: settled by f992, held ≥ 45 f (1.5 s) to f1045, exit in the last 0.36 s; CTA `US DOST KO / bhejo`; sub `jise 'log' ka
      darr rokta hai` drawn at 50 px (632.8 px wide, x 224-856: ≤ 780 px wide, right edge ≤ 930); `@jawad_mp4` present.
- [ ] Captions (r2): no V1B chunk is drawn in hook B; no caption chunk changes position inside its own display time (V6 across f864).
- [ ] Cover (f45) keyword inside y 240-1680; legible at 240 px wide.

**Ops**
- [ ] `du -sh <RW>` ≤ 2 GB; intermediates deleted; nothing written outside the paths in §17.1; no shared module edited; no commit.

---------------------------------------------------------------------------------------------------------------

## 19. Work orders (who runs next, on what) · r2

1. **hinglish-scriptwriter**: script v2 per §9 r2 (gate fixes 3-5: V4 short version, V5 onset 22.400 / part 2 23.667, V6 window to
   29.100 at 1.04-1.06x, new V7 from 31.600 at 1.00-1.06x, the overrun rules, all V1B tokens hidden), DEV + token-aligned ROM with
   `*keywords` (V7: 10 tokens, keyword *bhejo*), pronunciation test, Vlad takes (≤ 12 credits), `vo_chain.py process` per take,
   `log_kya_kahenge_vo.py` assembly → `lkk_vo_A/B.wav` + words.json.
2. **viral-strategist**: confirm script v2 against GATE.md fixes 3-5 before TTS; red-team on the 15 fps preview (frame 0, change
   events, the 360 px tiles of the snap).
3. **motion-timeline-builder**: `log_kya_kahenge_crowd.py` (r2 tonal flip, eye layer, obliquity-scaled cut-edge band, lean, `head_mask`),
   `log_kya_kahenge.py` (r2 J cadence, `c15_judge4`, `LKK_NOTEXT`), `log_kya_kahenge_hookb.py` (B snap); **gate stills + 360 px snap
   check + orbit range first** (§7.4); then sheet, preview, master A, hook-B range.
4. **face-compositor**: `log_kya_kahenge_faces.py` (§14) with `jd_rect(t)`; edge and skin checks. (No r2 change.)
5. **colorist**: noir_ember on this reel: frame-0 brightness, the snap's dark → light read after the finish, the warm turn at f768, rays,
   skin on S5-01, hue budget, YMIN; notes in `<RW>/GRADE_NOTES.md`.
6. **sound-designer**: `log_kya_kahenge_sfx.py` (7 local sounds, §11 r2 cues and beds: bursts -10/-8/-6/-4 at f96/144/180/216,
   whoosh_by at f104/150/184/220, the wall step at 6.0, hook B snap cues) → SFX stem -18 LUFS.
7. **music-supervisor**: rebuild `log_kya_kahenge_music.py` with the r2 EP duck windows (V6 26.0-29.1, V7 31.6-35.1; §12) + epic_mix A/B
   for both hooks + mux.
8. **caption-designer**: captions per §15 r2 (words.json, all V1B hidden, V6 avoid rects held across f864), SRT.
9. **blender-3d-artist**: none (no 3D props).
10. **motion-qa-reviewer**: §18 r2, two lenses + verifier; **delivery-packager**: §0 encodes, cover (240 and 210 px checks), stems,
    Trial splice.

---------------------------------------------------------------------------------------------------------------

## 20. Open questions

None blocks the build. Resolved with SLATE §7 defaults: AI label ON; house spelling = prior SRT; Trial eligibility unknown (hook B
rendered regardless). Shared-module requests (R1 O6 mask, R2 EndCard `sub_px`, R3 `epic_music` render without the end fade) are in
`SHARED_REQUESTS.md`; this reel works around all three locally. For the lead (r2): (1) the z/f nukta sounds (बिज़ी, नज़र, फ़्लैट, फ़ोन,
ज़िंदगी) cannot be verified by ASR: can Jawad or the lead listen to the T0 take before T1/T2? (2) add #videoediting as a 5th hashtag or
not; (3) the five covers' keyword bands are not at one common height (gate §6, a set-level decision).

---------------------------------------------------------------------------------------------------------------

## CHANGELOG

- **r1** 2026-10-08: first brief from SLATE §3.5.
- **r2** 2026-10-08: viral gate r1 = FIX (`GATE.md`).
  - Fix 1, head-snap (§6.1, §7.1, §7.4, §18): tonal flip (turned x0.75, crown x0.60 / front face plate +40 % + eyes), eye radius ≥ 1.5 px
    on rows 0-5, cut-edge band 0.4 while a card faces the camera, 360 px snap check (≥ 15 % head luma, eyes masked) at 0.10 / 0.70 s
    (B 0.0 / 0.6 s), focal 1600 fallback with the lamp bank moved. Scratch noir_ember mock: 25.6 % at 360 px (r1 spec: 0.1 %).
  - Fix 2, judgement lines (§5, §7, §8, §11): f96 / f144 / f180 / f216, arrivals 10 / 8 / 6 / 6 f, bursts -10 / -8 / -6 / -4 dB,
    whoosh_by moved, wall -18 from 6.0, crowd lean 1.00 → 1.03, J4 holds 2.4 s (`c15_judge4`, same size); max 2 lines (checked).
  - Fix 3 (§5, §9, §12, §15): V6 to ≤ 29.10 s at 1.04-1.06x (captions hold across f864); V7 from 31.6 s at 1.00-1.06x; EP ducks moved.
  - Fix 4 (§2, §8, §9, §16): V7 / sub "jise 'log' ka darr rokta hai" (sub 632.8 px at 50 px, re-measured); IG line 4; R2 updated.
  - Fix 5 (§9): V4 short version, V5 at 22.400 / part 2 23.667, V1 and V5 overrun rules.
  - Script v1 cuts approved by the gate folded in (V3 5 words, V6 9 words, V2 "..." 0.30 s; 62 / 61 words); hook B gets its own
    135 mm head-snap and hides all V1B captions; QA rule "a visible change ≤ 2.5 s apart"; cover checked at 210 px too.
  - `packet.yaml` → version 2.
- **r3** 2026-10-09 (handoff, measured VO): see `HANDOFF.md` §2, which supersedes this brief where they differ: V2 = the 14-word
  fallback "Hum zindagi ..." (and IG line 2); V7 onset 31.433 s (f943), picture unchanged; S3-01 camera = `LF.cam_s3`; S5-01 pinned at
  the beard; captions `keep_pairs` + `clear=[(25.6, 25.9)]`; flap landing frames; hook-B render folder `<RW>/out_hookb`; QA §18 → HANDOFF §13.
