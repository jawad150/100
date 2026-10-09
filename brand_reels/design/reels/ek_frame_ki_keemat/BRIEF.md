# BRIEF: Reel 3 · C08 · Ek Frame ki Keemat (the exploded frame)

Date 2026-10-08 · Author: creative-director · **Revision r2** (applies the viral gate r1 verdict FIX, `GATE.md` fixes 1-5;
see the CHANGELOG at the end) · Status: **READY TO BUILD** (gate: the exploded-stack still gate in §7.5 runs before any full
render; the end-card spelling `USKO YEH` waits for the lead's OK, §20 Q6, and blocks only TTS take T3 and one string) ·
Packet: `packet.yaml` (same folder) · Script: `SCRIPT.md` + `script.json` (hinglish-scriptwriter) · Shared change requests:
`SHARED_REQUESTS.md` (same folder).

Binding sources, in order: `brand_reels/design/SLATE.md` §0, §2, §3.3 (lines 218-262), §4, §5 (SERIES BIBLE); the
`jawad-brand-reels` skill; `pipeline/jawad_reels/TOOLKIT.md` and the shared modules' docstrings (`jawad_kit`, `jawad_tx`,
`jawad_grade`, `endcard`, `snake_captions`, `vo_chain`, `sfx_jawad`); `brand_reels/research/transitions_sound_music_bible.md`;
`brand_reels/research/face_assets.md`; `brand_reels/research/hooks_retention_captions.md`; panel memos (context only).

Every on-screen line below was measured with the real sprites (`T.measure`, `J.HouseTitle`, `E.EndCard.boxes()`) and placed on
previs stills built with the real kit (ember backdrop, the `suit_threequarter` cut-out with rim look A, house type, end card,
12-pane stack, corridor), which I looked at: `workspace/jawad_reels/ek_frame_ki_keemat/previs/` (`B1_f0*.png`, `B2_payoff.png`,
`B3_card*.png`, `F1_cover_5p1_safe.png`, `F2_fly_7p8_safe.png`, `F3_rehook_13p2_safe.png`, `sheet_final.jpg`, `sheet_3d.jpg`,
`sheet_fly300.jpg`, `sheet_corr.jpg`, `B6_rehook_*.png` (early explorations: `B4_*`, `sheet_3d.jpg`), and the two
scratch scripts `board.py` / `camspec.py` that made them; the `*_safe.png` files carry the safe-zone overlay). r2 adds
`previs/R2_*` (push + rack sequence, rack apertures, C3 portal frames, hidden-JD glint, `USKO YEH` card) and their scripts in
`previs/r2/` (`p8.py`, `rack.py`, `capcheck*.py`, `card.py`); `camspec.py` now carries the r2 P8 push. Every camera key
in §7 was checked by projecting all 48 pane corners with `K.Cam` (`camspec.py`). All times are frame-exact at 30 fps:
`f` = frame index, `t = f / 30`, `[bar.beat]` counts from frame 0 (beat = 18 f, bar = 72 f).

---------------------------------------------------------------------------------------------------------------

## What changed from SLATE §3.3, and why (nothing else changes)

| # | SLATE says | this brief | why |
|---|---|---|---|
| 1 | VO lines: "Lekin is ek frame mein... baarah layers hain." / "Aur ek layer... jo aap ko dikhi hi nahi." + "Iske bina frame zinda nahi lagta." / "Aur awaaz ki teen tracks." / "Ek frame ki keemat... woh jaanta hai, jis ne use banaya." / "Aur jo kehta hai 'editing mein kya hai'... usse yeh bhejo." | (r2, the script-gated lines) V2 **SLATE wording kept**: "Lekin is ek frame mein... baarah layers hain." / **"Aur ek layer... jiske bina frame zinda nahi lagta."** / **"Aur awaaz ke teen tracks."** / **"Keemat... banane wala jaanta hai."** / **"Jo kehta hai 'editing mein kya hai', usko bhejo."** (all other SLATE lines unchanged) | Time. At Vlad's processed rate SLATE's spine puts 32 words into 12.0-20.4 s and 22 words into 26.7-33.5 s: it cannot be spoken. The trims keep every number and every meaning (the payoff keeps its sense: the one who makes it knows its worth); the picture carries the rest ("jo dikhi hi nahi" is shown by the near-invisible pane and its late tag; "EK FRAME KI *keemat*" stays on screen, and the VO "Keemat..." completes it as one sentence across text and voice). V8 "ke": track is masculine on both sides of the border (SCRIPT C2). V2 went back to SLATE's wording in r2 because the scriptwriter's syllable model lands "baarah" on 4.80 with it (SCRIPT C1). Total VO = **62 words** (hook A), see §9. The `usko` spelling is row 8. |
| 2 | the 360 corridor 16.8, "360 lands 20.4", "Aur awaaz ki teen tracks" at 14.4-16.8 | anchors kept (C3 at 16.8, 360 at 20.4); the **three audio lanes move into the corridor (21.9-24.3)** as NLE audio tracks lying on the corridor floor, while V8 "Aur awaaz ke teen tracks." is spoken | with the merged re-hook line there is no room for V8 before 16.8; in the corridor the lanes read as the timeline under the 30 frames, and the VO lane pulses with the very words being said |
| 3 | "fly-through 6.0-11.0, one tag per layer, >= 1 s each" | fly-through **6.0-12.0**, one tag per layer on the beats 6.0 ... 12.0; layers 09 and 10 (keyword core and halo, one word) share **one two-line tag block** at 10.8 | 12 tags of >= 1 s with at most 2 text blocks on screen need >= 6 s and an even beat spacing; 12 panes on the 11 beat slots 6.0-12.0 need one shared slot |
| 4 | cover 5.5 s | **cover 5.1 s (f153)** | the side-on hold is 4.8-5.4; at 5.5 the camera is already swooping into the fly-through |
| 5 | (end card) signature at x = 540 | `EndCard(..., handle=False)` + `J.signature` drawn by the module at **(760, 1575)** | at x 540 the `@jawad_mp4` signature sits on JD's chin (face box x 242-564, y 1120-1564); request R1 filed |
| 6 | (none) | end-card **sub line** `jo kehta hai "editing mein kya hai?"` and payoff **sub line** `banane wala jaanta hai` | muted viewers get the whole CTA and the whole payoff without subtitles over JD's face (captions are hidden in both windows) |
| 7 | "seams glow 0.6, separate 0.9" | as SLATE, plus: the HUD timecode chip fades out 0.80-1.07 s, before the frame pulls back | the chip is HUD, not a frame layer (it must never become a 13th layer, see §7.2) |
| 8 | (r2) end-card CTA `USSE YEH / *bhejo*` (§3.3 and the §5.1 lock) | **`USKO YEH / *bhejo*`** (455.5 px at jw_caps 86, fits), VO V10 "...उसको भेजो।" (Roman `usko`). **Needs the lead's OK** (§20 Q6). Fallback if the lead keeps the lock: card `USSE YEH`, VO उसे, Roman token and SRT `usey` | viral gate fix 5: the VO says उसे ("to him") but in Roman Urdu, and in this project's own playbook (`hooks_retention_captions.md` line 186, "Aapka video *usse* sasta dikhata hai"), "usse" reads as उससे ("from / than him"). Pakistani readers can misread the send line, and sends are this reel's main reach driver. "usko" is unambiguous on both sides |
| 9 | (r2) hidden JD in layer 03, "visible on frame 0 and in the side-on stack" | as SLATE, plus **one 2-frame glint at f846-f847 (28.2 s, beat 3 of bar 11)**: the glyph's own emission x0.35 -> x1.20 -> x0.70 -> x0.35, no SFX (§7.2) | viral gate fix 3: a bonus beat in the 7.2 s post-payoff tail and a visible rewatch trigger. The light comes from layer 03 itself while the frame plays, so it adds no 13th layer and keeps the truth rule |
| 10 | (r2) comment prompt "Is frame mein JD chhupa hai. Mila?" (answer pinned after 24 h) | as SLATE, plus: **pinned as the first comment when posting**, and moved to **caption line 2** (it was line 7) | viral gate fix 3: the Reels viewer cuts the caption at about 55-60 characters [secondhand], so line 7 was never seen |

SLATE open questions are resolved with SLATE §7 defaults: **AI label ON** (§16); house spelling = the prior SRT (bari / bohat /
hai / nahi / mein); Trial-Reel eligibility unknown (hook B is rendered anyway, §6.2). Q5 (C08 VO lane label) has no stated default:
it resolves to **"VO · AI voice"**, the honest label that matches the Q1 default; the lead can change one string (§8, id T-L1).
Mummy/Ammi, Ubaal Chai and the JD nameplate do not concern this reel.

---------------------------------------------------------------------------------------------------------------

## 0. Deliverables

| item | spec |
|---|---|
| reel | 1080x1920, 30 fps, **DUR 33.6 s = 1,008 frames = 14 bars at 100 BPM** (18 f/beat, 72 f/bar, 9 f/8th), H.264 High yuv420p bt709 |
| versions | **A** public (hook A); **B** Trial Reel (hook B frames 0-89 spliced onto A's frames 90-1007, §6.2) |
| audio | mix A (VO + SFX + score) and mix B (VO + SFX only) for each hook version; 48 kHz 24-bit stems (VO, SFX, music); -14 LUFS ±0.5, TP ≤ -2.0 dBTP wav, ≤ -1.5 after AAC |
| encodes | master CRF 14 (Git LFS); share 2-pass ~22 Mbps +faststart, AAC 320k (< 100 MB); preview ~7 Mbps (< 30 MB); cover JPG (frame 153); SRT of the captions |
| deliver to | `reel/jawad_reels/` with prefix `jawad`, e.g. `jawad_03_ek_frame_ki_keemat_A.mp4` |
| platform | Instagram Reels, organic (not a paid ad: the organic safe zone applies) |
| AI label | "AI info" ON at upload (synthetic voice; character-sheet imagery may be AI-generated) |

---------------------------------------------------------------------------------------------------------------

## 1. Brand for this reel (tokens from project.json; never re-derive)

| token | hex | job in C08 |
|---|---|---|
| NIGHT_0 / NIGHT_1 | #070404 / #170A07 | the void around the frame (canvas fill NIGHT_0 x 0.6 linear) and the frame's own dark background; 70-85 % of every frame |
| SMOKE / PLUM | #2A1A15 / #4A0E08 | haze (layer 02), tag scrims, lane glass, chip body |
| FLAME | #FF6A1A | keyword glow, rim light (layer 05), seams, leader lines, VO lane, chip stroke |
| RED / EMBER | #F2312B / #B3120E | counter-rim (layer 05), MUSIC lane, playhead |
| GOLD / AMBER | #FF9F1C / #FFB547 | hot cores (keyword, embers), SFX lane, hidden JD glyph (<= 5 % of the frame) |
| IVORY / ASH | #FFF3E6 / #A8978C | all type (never pure white) / seam lines, secondary readouts |

Fonts (project.json): Instrument Serif Italic (`jw_key`, `jw_key_core`, `jw_key_halo`), Poppins (`jw_caps`, `jw_body`, `jw_handle`),
JetBrains Mono (`jw_mono`). Logo: the derived JD monogram via `endcard.Monogram` only (never stretched or recoloured).
Look: **`ember`** (jawad_kit), finished only by `G.tx_finish(cv, t, 'ember', ...)` (§17.2). Emissive FLAME/RED <= ~3x linear.

---------------------------------------------------------------------------------------------------------------

## 2. Verified copy table and Do-not-claim

Status: `verified` = locked in SLATE §3.3 or a true count by construction; `new (lead OK)` = written here from SLATE material,
true, no claim about Jawad.

| id | exact text | source | status | used in |
|---|---|---|---|---|
| H-A1 | `AAP NE ISE` / `0.03 sec` / `DEKHA` | SLATE §3.3 hook A | verified (0.03 s = 1/30 s rounded) | f0-f26 (frame layers 08-11), the loop |
| H-A2 | `00:00:00:01` | SLATE §3.3 (timecode chip) | verified (one frame) | HUD chip f0-f31 and the loop |
| H-B1 | `360` / `LAYERS · 1 SECOND` | SLATE §3.3 hook B | verified (12 x 30) | hook B f0-f68; body 18.9-22.15 |
| C-1 | `12` / `LAYERS` | SLATE §3.3 ("12 LAYERS") | verified (the module's layer count) | 3.0-5.65 |
| T-01..T-12 | `01 · andhera`, `02 · dhuaan`, `03 · roshni`, `04 · chehra`, `05 · rim light`, `06 · saaya`, `07 · chingaariyan`, `08 · lafz`, `09 · keyword` + `10 · chamak` (one 2-line block), `11 · lakeer`, `12 · finish` | SLATE §3.3 locked layer list, named in Roman Urdu | new (lead OK) | fly-through 5.9-12.9; T-12 to 15.9 |
| T-12s | `ON` / `OFF` (state suffix of T-12: `12 · finish  ON`) | this brief | new (lead OK) | 13.2-15.9 |
| T-L1..3 | `VO · AI voice`, `SFX`, `MUSIC` | SLATE §3.3 ("VO · AI voice" if labelled) | verified (the master's 3 real stems; Q5 default) | 21.9-24.3 |
| P-1 | `EK FRAME KI` / `keemat` | SLATE §3.3 payoff | verified | 26.4-29.45 |
| P-2 | `banane wala jaanta hai` | SLATE logline ("its worth is known to the one who made it") | new (lead OK) | 27.7-29.45 |
| E-1 | `USKO YEH` / `bhejo` | SLATE §3.3 / §5.1 CTA `USSE YEH / bhejo`, respelled (viral gate fix 5) | **changed from the SLATE lock: lead OK required** (§20 Q6); fallback `USSE YEH` (verified) | end card 29.4-33.6 |
| E-2 | `jo kehta hai "editing mein kya hai?"` | SLATE §3.3 send target | new (lead OK) | end card sub |
| E-3 | `@jawad_mp4`, `JD` | brand | verified | end card |
| V1-V10 | the VO lines in §9 (= `SCRIPT.md` §3 after the script gate, with fixes 4 and 5) | SLATE §3.3 (trimmed, see the change log) | verified / new (lead OK); V10 `usko` lead OK (§20 Q6) | VO + captions |
| IG-2 | `Is frame mein JD chhupa hai. Mila? 👇` | SLATE §3.3 comment prompt | verified (the hidden JD exists in layer 03) | IG caption line 2 + the first comment, pinned at posting (§16) |

**Do not claim (truth lock, SLATE §3.3 + §4):** no hours, minutes, days, rates, prices, client names, view counts or "main ne
ise kai ghante diye"; no per-layer times; no "this reel took X"; no first-person memory ("main", "meri"); no real NLE names,
logos or UI clones; no number other than **12 layers, 3 audio tracks, 30 fps, 360 layers per second, 0.03 sec, 00:00:00:01**.
"VO · AI voice" stays honest. The hidden JD must really exist in layer 03 (the comment prompt promises it).

---------------------------------------------------------------------------------------------------------------

## 3. Director's Pass and World Bible (cinematic-director format)

**Director's Pass (from the panel, kept):** core = awe that turns into respect ("ab samjhe?"). Killed: a VFX-breakdown
before/after wipe; an editor at a desk with a spinning clock; a rate card. POV: the frame itself, the 1/30 s a thumb gives it.
Contradiction: cathedral scale on 33 milliseconds; stillness inside a medium made of motion. Human truth: "Jo cheez aasaan
dikhti hai, us ke peeche kisi ka kaam hota hai" (everyone has heard "bas 5 minute ka kaam hai" about their work).
**Single image (anchor, cover):** side-on, one paused frame pulled apart into a loaf of glowing glass slices; one slice holds
JD's face, the slice beside it holds only his rim light, separated from him by a hand's width of darkness (`previs/F1_cover_5p1_safe.png`).

**World Bible (verbatim lines, also in `packet.yaml`):**
- Palette: near-black NIGHT_0 #070404, flame FLAME #FF6A1A, hot cores AMBER #FFB547, labels IVORY #FFF3E6 and ASH #A8978C, accent RED #F2312B.
- Light logic: the void is lit only by the frame's own layers; the frame lights the room it sits in.
- Lens set: 35 mm corridor, 85 mm side-on stack and fly-through, 100 mm frontal re-hook (f_px = mm / 36 x 1920: 1867, 4533, 5333).
- Camera law: the camera moves only while the frame is paused; when it plays, the camera locks.
- Texture: ember finish: crushed warm blacks, halation on highlights, fine grain 0.016 at 1.8 px, no full-frame flash.
- Sound motif: the pause click (a mouse micro-switch, then glass on glass).
- Recurring symbol: the pause / timecode chip `00:00:00:01`.
- Forbidden: hours, rates, clients or any invented fact; a 13th layer or any light that does not come from the 12 layers;
  particles outside the frame's layers; real NLE logos or UI clones; a large centred play/pause ring (his OpenArt cover);
  ERROR / unsaved / delete dialogs; keycaps or Ctrl+Z (C11 / C26 devices); white flashes or fades; anything from Organic
  Fostering / Floret; hearts or the old prop library; mirroring the cut-out.

**References and devices (devices only; never layouts, copy or audio):** ref2 "light is the transition" and rack-focus
reveals (here: C6 in-shot racks, the portal through a point of light); ref3 crystal + rack focus (C6); ref1 nested frames (here
the 30-frame corridor, our own geometry); casebook "exploded layers" device (C08's signature, true by construction).

---------------------------------------------------------------------------------------------------------------

## 4. Global craft rules (series constants, SLATE §5.1, applied here)

- Safe zones 1080x1920: key copy inside x 70-1010, y 230-1480; nothing textual at x > 930 for y 1050-1700; bottom 300 px
  (y > 1620) free of text; cover title inside y 285-1480 (3:4 grid crop y 240-1680). At most **2 text blocks** at any frame
  (§17.5 lists them). Hero >= 130 px; H2 80-120 px; mono tags 44 px in screen space (never shrunk by perspective); UI >= 40 px.
- Type is IVORY, never pure white; one serif keyword per block; keyword reveals `out_cubic` / `easy_ease` 0.4-0.7 s, no
  bounce or JELLY on brand type; the underline appears **twice** (hook lockup, payoff lockup) plus the end card's own.
- Finish: `post` = `G.tx_finish` only. No `K.flash`, `K.fade`, `post(flash=)`. Exposure pushes only (§10). Motion blur never
  crosses a cut (HALF rule, `jawad_tx`). Exits ease >= 0.2 s. <= 4 feature transitions (here 2: C3 ★, C8), never two within 2 bars.
- JD: `suit_threequarter` only, rim look A, display scale <= 1.0 of the 2x master (0.90 here; the C8 punch reaches 1.09 for
  frames 789-791 under zoom blur, accepted), no warp, no mirroring, no talking, natural skin (human-realism / photo-realism).
- Loop: the last frame resolves into frame 0 (picture and audio); never a fade to black or silence.
- Loudness: -14 LUFS ±0.5, TP <= -2.0 dBTP (wav), <= -1.5 (AAC), LRA 5-9; VO stem -16 LUFS; speech >= 8 LU over the bed; <= 3
  SFX starting on one instant; one drop-out (25.8-26.4) before the reveal; heroes only in VO gaps.

---------------------------------------------------------------------------------------------------------------

## 5. The grid and the frame-exact beat table

`X.Grid(100)`: beat 0.6 s (18 f), bar 2.4 s (72 f), 8th 0.3 s (9 f); locked. DUR 14 bars = 33.6 s = 1,008 frames (f0-f1007).
Key D (Sa = D4 293.66 Hz), Phrygian-dominant colour (`epic_music` PHRYG_DOM). Arc: awe build -> one drop at bar 11 (79 %) -> resolve
-> loop bar. Family: **camera** (signature C3 ★; C6 in-shot; C8; L3 glue). Desi voice: **dhol** (harmonium drone counts as the drone).

| # | [bar.beat] | t (s) | f | picture (shot) | transition / push | SFX (§11) | music (§12) | VO (§9) | captions (§15) |
|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.0 | 0.000 | 0 | **S1** the finished frame PLAYING, screen-locked 1:1: JD rim-lit bottom-left, lockup `AAP NE ISE / 0.03 sec / DEKHA` settled, chip `▶ 00:00:00:01` right of his eyes, embers rising | push 0.6 (loop seam) | `impact_soft` -8, cue-level `dur=0.25` (it ends before the pause = the frame's sound stops) | bar 0: harmonium drone swell | V1A onset 0.10 | hidden 0-3.0 |
| 2 | 0.0½ | 0.300 | 9 | **PAUSE**: every layer clock freezes (embers stop mid-air); chip icon ▶ -> ❚❚, chip stroke flashes (local) | - | pause motif: `jd_mouse_click` +4 | - | "Aap ne ise..." | - |
| 3 | 0.1 | 0.600 | 18 | seams glint: alpha-edge glow sweeps the layers (diagonal, 0.6-0.9) | - | `jd_glass_slide` (dur 0.3) lands 0.6 | - | "...palak..." | - |
| 4 | 0.1½ | 0.900 | 27 | layers separate in z (gap 0 -> 120 by 2.4); camera pulls back (85 mm, the frame shrinks to 0.55, centred y 1150); chip fades f24-f32 | - | `card_slide` -8 | - | "...jhapakte dekha." ends <= 2.37 (hard 2.70) | - |
| 5 | 1.0 | 2.400 | 72 | **S2-02** orbit to side-on starts (yaw 0 -> 52, pitch 0 -> 8, easy_ease, to 4.8) | - | `whoosh_slow` -8 | strings 8ths enter (LP 900) | (gap) | - |
| 6 | 1.1 | 3.000 | 90 | **SPLICE (A/B identical from here)**. Counter `00` + `LAYERS` rises in at top; panes light one by one 01 -> 12 as the counter rolls | - | `slot_tick` n 12 dur 1.8 -12 (start) | - | V2 onset 3.07 "Lekin is ek frame mein..." | hidden (counter is the headline) |
| 7 | 2.0 | 4.800 | 144 | **side-on lands; counter `12` settles** (the single image) | **L3 push 0.3** | `glass_truth` (D) | - | "...baarah" onset 4.80 ±0.10 | - |
| 8 | 2.0½ | 5.100 | 153 | **COVER frame** (side-on, `12 / LAYERS`) | - | - | - | "...layers hain." ends ~5.84 (hard 5.95) | - |
| 9 | 2.1 | 5.400 | 162 | counter exits (to 5.65); camera swoops to the fly-through pose (to 6.0); gap 120 -> 300 | - | `whoosh_slow` -6 (pass 5.7) | - | - | hidden 3.0-12.0 |
| 10 | 2.2 | 6.000 | 180 | **S2-03 fly-through** back to front: pane 01 in focus, tag `01 · andhera` | C6 rack (in-shot) | `jd_ui_tick` -14 | - | V3 "Andhera." 6.00 (one word per tag arrival) | - |
| 11 | 2.3 | 6.600 | 198 | pane 02 `02 · dhuaan` | C6 | `jd_ui_tick` -14 | - | "Dhuaan." 6.75 | - |
| 12 | 3.0 | 7.200 | 216 | pane 03 `03 · roshni` (the hidden JD is in this pane) | C6 | `jd_ui_tick` -14 | - | "Roshni." 7.30 | - |
| 13 | 3.1 | 7.800 | 234 | pane 04 `04 · chehra` (JD's flat face pane) | C6 | `jd_ui_tick` -14 | - | "Chehra." 7.90 | - |
| 14 | 3.2 | 8.400 | 252 | pane 05 `05 · rim light` (his rim alone, a hand's width from him) | C6 | `jd_ui_tick` -14 | - | (gap 8.36-10.03) | - |
| 15 | 3.3 | 9.000 | 270 | pane 06 `06 · saaya` | C6 | `jd_ui_tick` -14 | harmonium swell | - | - |
| 16 | 4.0 | 9.600 | 288 | pane 07 `07 · chingaariyan` | C6 | `jd_ui_tick` -14 | - | - | - |
| 17 | 4.1 | 10.200 | 306 | pane 08 `08 · lafz` | C6 | `jd_ui_tick` -14 | - | V4 10.03 "Har lafz." (lafz ~10.23) | - |
| 18 | 4.2 | 10.800 | 324 | panes 09 + 10, one 2-line tag `09 · keyword` / `10 · chamak` | C6 | `jd_ui_tick` -14 | - | "Har chamak." 10.95 (chamak ~11.15), ends 11.61 | - |
| 19 | 4.3 | 11.400 | 342 | pane 11 `11 · lakeer` | C6 | `jd_ui_tick` -14 | - | (re-hook silence 11.61-12.05) | - |
| 20 | 5.0 | 12.000 | 360 | **RE-HOOK** (36 %): the camera stops on pane 12, nearly invisible, tag `12 · finish  ON`; then swings frontal (100 mm) while the stack folds to gap 30 (to 13.2) | **L3 push 0.35** | `impact_soft` -8 + `glass_tap` -10 | strings thin (-9) for bar 5 | V5 12.05 "Aur ek layer..." | C1 (upper band) |
| 21 | 5.2 | 13.200 | 396 | camera settled frontal; **flick 1 OFF** (pane 12 hidden; tag `OFF`) | - | `jd_ui_click` -6 | - | (pause) | - |
| 22 | 5.2½ | 13.500 | 405 | flick ON | - | `toggle_on` -8 | - | "jiske bina..." | - |
| 23 | 5.3 | 13.800 | 414 | flick 2 OFF | - | `jd_ui_click` -6 | - | "...bina" | - |
| 24 | 6.0 | 14.400 | 432 | flick ON: **resolved "with"** (the frame comes alive) | - | `toggle_on` -6 + `jd_sparkle` -12 | strings back to -5 | "...frame zinda..." (zinda ~14.43) | - |
| 24a | 6.0+6 f | 14.600 | 438 | (r2) **the push toward the portal starts**: the dolly rate ramps 1 -> 4.5 %/s over 14.6-14.9, ~6 % closer by 16.0 (§7.3 P8); the frame stays paused | - | - | - | "...nahi lagta." ends ~15.70 | - |
| 24b | 6.1 | 15.000 | 450 | (r2) **rack focus to pane 03** (aperture 0 -> 900, inout_cubic, to 15.8): the title, embers and finish go soft, JD and the portal disc stay sharp (§7.3 P8) | - | - | - | - | - |
| 25 | 6.2+12 f | 16.000 | 480 | C3 approach: A (its 16.0 camera held static, racked) zooms into the portal bokeh disc of pane 03 (screen 719.4, 1267.5; disc r 38.2, C3 r0 41.0) | **C3 ★** pre 24 f | `reverse_swell` -3, 0.733 s, ends 16.733 (plan cue) | - | (VO gap ~15.70-16.95) | C1 gone by 16.25 |
| 26 | 7.0 | 16.800 | 504 | **S3-01 corridor**: 29 frame-stacks + the live stack at the end; light wave runs down the corridor (16.9-18.6) | C3 cut, settle to 17.067 | `air_zoom` -6, `impact_soft` -1 (plan cues) | strings LP opens 900 -> 1200 | V6 16.95 "Ek second mein tees frames." | C2 (lower) |
| 27 | 7.3 | 18.600 | 558 | **S3-02 surge** down the corridor (35 mm, 7 samples) | - | `whoosh_by` 19.2 / 19.8 -6 | taiko pulse beats 1+3 from bar 8 | - | - |
| 28 | 7.3½ | 18.900 | 567 | counter `012`... rolls up with `LAYERS · 1 SECOND` (top) | - | `slot_tick` n 29 dur 1.5 -10 (start) | - | V7 18.90 "Yaani har second..." | C2 (lower) |
| 29 | 8.2 | 20.400 | 612 | **`360` lands**; camera brakes in front of the live stack | **L3 push 0.5** | `glass_truth` (A) | - | "...teen sau saath layers." (teen 20.45) | hidden 20.13-21.99 |
| 30 | 9.0½ | 21.900 | 657 | 360 lockup exits (to 22.15); **S3-03 three audio lanes rise** on the corridor floor (to 22.2), legend `VO · AI voice / SFX / MUSIC` | - | `bar_grow` 0.3 s -10 (start) | - | V8 22.15 "Aur awaaz ke teen tracks." | C3 (upper) |
| 31 | 10.0 | 24.000 | 720 | **S3-04 rush**: the 29 frame-stacks fly back into the live stack (to 25.5); lanes sink (to 24.3); camera pushes in to 0.97 | - | `whoosh_by` 24.3 / 24.75 / 25.2 | shepard 24.2-26.4 (gated) | (VO-free ~23.39-26.75) | - |
| 32 | 10.1 | 24.600 | 738 | (rush continues) | - | `riser` 1.2 s ends 25.8 (ember_slam) -4 | reverse_cymbal 25.2-26.4 | - | - |
| 33 | 10.3 | 25.800 | 774 | **DROP-OUT** (1 beat): the single stack hangs frozen, 1 %/s push | - | true silence 8 f | **gate 25.8-26.4** | - | - |
| 34 | 10.3+8 f | 26.067 | 782 | the play click; the layers slam together (gap 60 -> 0, in_expo, to 26.4) | - | `jd_mouse_click` +4 (held-breath element) | - | - | - |
| 35 | 10.3+14 f | 26.267 | 788 | C8 punch-in on A (1 -> 1.25 about JD's eye 465,1282) | **C8** pre 4 f | `whip` -6 at 26.367 | - | - | - |
| 36 | 11.0 | 26.400 | 792 | **PAYOFF (79 %)**: hard cut to the frame PLAYING again (B settles 1.1 -> 1.0, 6 f); lockup `EK FRAME KI / keemat` builds (HouseTitle t0 26.4) | C8 cut + **push 0.4 + 0.6 = 1.0** | `flash_hit` -3 @26.397, `impact_big` 0, `sub_drop` -4 | **DROP**: `dhol_hit` + dhol chaal + 808 | VO waits | hidden 26.4-33.6 |
| 37 | 11.0+11 f | 26.767 | 803 | - | - | - | - | V9 26.75 "Keemat..." | - |
| 38 | 11.2 | 27.600 | 828 | sub line `banane wala jaanta hai` rises in (27.7-28.1) | - | - | - | "...banane wala jaanta hai." ("banane" 27.70), ends ~29.44 | - |
| 38a | 11.3 | 28.200 | 846 | (r2) **bonus beat: the hidden JD glints** in layer 03 at (836, 330), f846 x1.20, f847 x0.70, then x0.35 again (§7.2); the frame is playing, lockup and sub settled | - | none (silent on purpose) | - | inside "banane" (est 27.70-28.34): the maker glints as the voice says "banane wala" | - |
| 39 | 12.0+9 f | 29.100 | 873 | payoff lockup exits (to 29.45) | - | - | resolve: dhol at -8 | - | - |
| 40 | 12.1 | 29.400 | 882 | **END CARD** `EndCard('USKO YEH', 'bhejo', sub, monogram='JD', dur=4.2)` (lead OK; fallback `USSE YEH`) over the dimmed playing frame; signature at (760, 1575) | - | card cues (§11) | - | V10 29.60 "Jo kehta hai..." | - |
| 41 | 13.0+1.5 f | 31.250 | 938 | card settled; holds to 33.24 (1.99 s) | - | - | bar 13: loop bar (cold drone) | "...usko bhejo." ends ~32.82 (33.02 if "usko" takes 3 syllables; target <= 33.24, hard 33.35) | - |
| 42 | 13.3 | 33.000 | 990 | `E.loop_world` crossfade (0.6 s) brings back the hook lockup and the chip | loop push rises | `reverse_swell` 0.8 s ends 33.6 -8 | `reverse_cymbal` ends 33.6 -8 | - | - |
| 43 | 13.3+7 f | 33.233 | 997 | card type exits (0.36 s, in_cubic) | - | - | - | - | - |
| 44 | 14.0 | 33.600 | 1008 | = frame 0 of the next loop (the last frame is f1007) | push 0.6 at f0 | `impact_soft` at f0 | bar 0 | V1A | - |

Notes. The re-hook falls at 36 % (SLATE-locked bar 5); the C3 corridor at 50 % is the second pattern break. Payoff 79 %
(26.4/33.6). Nothing is static for > 2 s: the longest still holds are 25.8-26.067 (designed freeze) and the end-card hold over a
playing world. Every cut and every hero hit sits on the grid; the play click (f782) is placed by the 8-frame silence rule.
r2: the former soft window 14.43-16.3 (1 %/s, nothing open after the flick) now carries the push toward the portal from 14.6
(4.5 %/s) and the rack to pane 03 over 15.0-15.8, which hand straight over to the C3 zoom (per-frame scale steps: push
0.16 % at 16.0, then C3 0.48 % on its first frame and 0.16, 0.21, 0.28, 0.38 %..., so the move does not stall at 16.0). The post-payoff tail gets one new event, the 28.2 glint (row 38a). The push
start (14.6) and the rack end (15.8) are camera eases, not hits, so they are not on the 8th grid (like the C3 approach at 16.0).

---------------------------------------------------------------------------------------------------------------

## 6. Hook 0-3 s, frame by frame

### 6.1 Hook A (public)

Frame-0 rules (SLATE §2 item 9 + hooks playbook): motion on f0 (embers rise, JD idle breathing, bokeh drift), text readable on
f0 (the lockup is already settled: it is the frame's own layers 08-11), VO onset <= f3, a transient on f0, no fade-in, no logo,
no large centred play/pause ring, the hidden JD already present in layer 03. Spoken hook 6 words, ends by 2.37 s (hard 2.70).

| f | t | picture | text | VO | sound |
|---|---|---|---|---|---|
| 0 | 0.000 | the frame plays at 1:1 (camera locked): ember backdrop, haze + god rays from top-right, bokeh, JD bottom-left (`suit_threequarter`, rim look A, side-eye screen-right), embers rising | lockup settled (caps 441-501, keyword 564-716, underline y 791, DEKHA 854-915); chip `▶ 00:00:00:01` at (760, 1282) | - | `impact_soft` -8 (cue-level `dur=0.25`, `align='start'`: hit 0.006 s, inside f0), push 0.6 |
| 3 | 0.100 | - | - | "Aap" onset | - |
| 9 | 0.300 | **pause**: layer clock tl frozen at 0.300 until f792; chip ▶ -> ❚❚ and its FLAME stroke flares x2.2 -> x1.4 over 6 f (local glow) | - | "...ne ise" | pause motif `jd_mouse_click` (+4; `fit_under_vo` ducks it -8 dB because 0.3 lies inside V1A, so it plays at -4); the f0 impact already ended at 0.25 (50 ms fade) |
| 18 | 0.600 | seam glint: `|∇alpha|` edges of layers 04, 08, 09, 11 glow FLAME x1.6 under a 35° sweep (`X.sweep_mask`, out_cubic 0.6-0.9), decaying to x0.35 by 1.2 | - | "palak" | `jd_glass_slide` (dur 0.3) lands 0.600 |
| 24 | 0.800 | chip starts fading (opacity 1 -> 0 by f32, in_cubic) | - | - | - |
| 27 | 0.900 | gap 0 -> 120 (inout_cubic, to 2.4), camera pull-back starts (§7.3 P2) | - | "jhapakte" | `card_slide` -8 (lp 1100) |
| 36-60 | 1.2-2.0 | the frame becomes an object in the void (scale 1.0 -> 0.6), seams visible, spill glow under it | lockup panes separate in depth | "dekha." ends ~2.37 | `whoosh_slow` -10 @1.6 |
| 72 | 2.400 | orbit begins (§7.3 P3) | - | (gap) | `whoosh_slow` -8 |
| 89 | 2.967 | last hook frame; identical to hook B's f89 by construction (§6.2) | - | - | - |

### 6.2 Hook B (Trial Reel; frames 0-89 only)

| f | t | picture | text | VO | sound |
|---|---|---|---|---|---|
| 0 | 0.000 | the 30-stack corridor mid-surge (S3 world, camera = the body's surge pose at t = 19.5 s), 7 samples, frame-stacks streaking past | `360` (jw_key 240) / `LAYERS · 1 SECOND` (jw_caps 86) settled at top (y 294-550) | - | `impact_soft` -6 at 0.0; `whoosh_by` 0.2 -4 |
| 3 | 0.100 | surge continues | - | V1B "Ek second." | `whoosh_by` 0.6 (dir -1) -6 |
| 54 | 1.800 | the 29 billboard stacks rush back into the live stack (same code as the body rush, 1.8-2.7); camera pose blends to `cam_A(t) + (0, 0, 10470)` (easy_ease 1.8-2.9: position, yaw, pitch, focal) | lockup exits 2.0-2.3 (in_cubic) | "Teen sau saath layers." ends <= 2.70 | `jd_reverse_swell` 1.2 s ends 3.0 -8 |
| 87-89 | 2.9-2.967 | exactly hook A's world: exploded stack gap 120 mid-orbit, no chip | - | - | - |

Build: module `ek_frame_ki_keemat_hookb.py` (thin wrapper, §17.1); render `--range 0 3.0`, splice at f90 (video and audio; 5 ms
audio crossfade at 3.000). The B master loops into hook A's frame-0 state and then cuts to its corridor f0 (accepted: SLATE §3
renders the body once).

### 6.3 Re-hooks, reveal, payoff, end card, loop

- **Micro-hooks:** a new event every <= 0.6 s from 3.0 to 12.0 (counter steps, pane light-ups, one tag per beat).
- **Re-hook 12.0 (bar 5):** 0.44 s VO silence (11.61-12.05) + the stop on the near-invisible pane 12 + push 0.35 + a new
  question ("Aur ek layer...", its caption keyword on *layer*); the flick demonstrates the answer (13.2-14.4).
- **The bridge to the break (r2, 14.6-16.8):** once the flick resolves, the camera pushes toward the portal disc (from 14.6,
  4.5 %/s) and racks focus to pane 03 (15.0-15.8): the title melts, the disc stays crisp and becomes the obvious next place to
  go, and C3 flies into it. The frame stays paused; only the camera moves (camera law).
- **Second break 16.8 (50 %):** C3 portal through a point of light into the 30-frame corridor.
- **Reveal / drop 26.4 (bar 11):** drop-out 25.8-26.4, play click at 26.067, layers slam, C8 + push 1.0, music drop, payoff
  lockup. The loudest moment of the reel must be within ±0.2 s of 26.4.
- **Bonus beat 28.2 (r2, bar 11 beat 3):** the hidden JD glints for 2 frames in layer 03 (f846-f847), silent: a reward for the
  viewers who read the pinned comment and a reason to rewatch.
- **End card 29.4-33.6 (bar 12 beat 1, dur 4.2):** CTA `USKO YEH / bhejo` (lead OK; fallback `USSE YEH`) + sub; hold
  31.25-33.24 (1.99 s >= 1.5).
- **Loop bridge:** the frame plays on with its layer clock `tl = t - 33.6` (so f1007 is the instant before f0), `E.loop_world`
  crossfades the hook lockup and the chip back in over 33.0-33.6, the card exits in the last 0.36 s, the loop push rises into
  f1007 and `cuts=[(0.0, 0.6)]` carries it over f0; audio: card `reverse_swell` and music `reverse_cymbal` end exactly at 33.6,
  frame 0's `impact_soft` is the release.

---------------------------------------------------------------------------------------------------------------

## 7. Shot list, world and geometry (shot-list template; World Bible applies to every row)

### 7.1 Shot list

| shot | purpose | size | lens | move (speed, easing) | action | cast / props | light | atmosphere | uncomposed element | dur (s) | sound | out | anchor / start |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| S1-01 0-0.9 | reveal | medium (the whole frame) | screen-locked (85 mm eq.) | locked; frame plays then pauses at 0.3 | embers rise, then stop mid-air at the click | JD, THE FRAME, THE CHIP | top-right flame key inside the frame; rim from top-right | haze + god rays (layer 02) | one bokeh disc in layer 03 cut by the frame's top edge | 0.9 | soft impact (cut at 0.25), pause click, glass | match | - |
| S2-01 0.9-2.4 | change | wide (frame in the void) | 85 mm | pull back D 4533 -> 8300, easy_ease | the layers drift apart in depth | THE FRAME | the frame's own light; spill glow below | dark void | layer 06's shadow lags 1 frame behind the face pane | 1.5 | card slide, whoosh | match | start_from S1-01 |
| S2-02 2.4-5.4 | reveal | wide side-on | 85 mm | orbit yaw 0 -> 52, pitch 0 -> 8, easy_ease, then 1 %/s | panes light one by one as the counter rolls to 12 | JD, THE FRAME, COUNTER | each pane emits its own light | void | the rim pane sits a hand's width from the face pane | 3.0 | slot ticks, glass truth | match | **anchor (single image, cover f153)** |
| S2-03 5.4-12.0 | inform | medium on each pane | 85 mm | swoop 5.4-6.0, then beat-stepped track (inout_sine per beat) back to front, rack focus per beat | each pane comes into focus and gets its tag | THE FRAME, TAGS | the current pane sharp and bright, neighbours soft | void | pane 07's embers frozen in mid-flight | 6.6 | ticks per beat | match | start_from S2-02 |
| S2-04 12.0-16.0 | change | medium (frame at 0.63 -> 0.68) | 85 -> 100 mm | swing to frontal 12.0-13.2 easy_ease, then 1 %/s push; from 14.6 the push ramps to 4.5 %/s toward the portal disc (to 16.0); rack focus to pane 03 15.0-15.8 (aperture 0 -> 900, inout_cubic) | the stack folds back to a frame; pane 12 flicks off/on; then the title melts out of focus while the portal disc stays crisp | JD, THE FRAME, TAG 12 | the finish layer adds vignette, halation, grain | void | the tag's leader line catches the frame edge | 4.0 | click / toggle | object_wipe (C3) | start_from S2-03 |
| S3-01 16.8-18.6 | atmosphere | wide corridor | 35 mm | glide z -700 -> 300, easy_ease | 30 frames light up near to far | THE CORRIDOR | each frame-stack glows; void between | depth fog to the void | one stack sprite is a frame late to light | 1.8 | air zoom, sparkle | match | - |
| S3-02 18.6-21.9 | inform | wide corridor | 35 mm | surge z 300 -> 7070 (inout_sine), brake on 20.4 | the counter rolls 12 -> 360 | CORRIDOR, COUNTER | streaks of flame from passing stacks | motion blur 7 samples | a stack passes so close it fills a frame edge | 3.3 | whoosh-bys, slot ticks, glass truth | match | start_from S3-01 |
| S3-03 21.9-24.0 | inform | wide, low | 35 mm | hold, 1 %/s push | three lanes rise on the floor, waveforms pulse with the real stems | CORRIDOR, AUDIO LANES | lane fills glow FLAME / AMBER / RED | void | the MUSIC lane is one frame behind its neighbours as it rises | 2.1 | bar grow | match | start_from S3-02 |
| S3-04 24.0-26.4 | change | medium (stack 0.97) | 35 mm | push in (in_cubic), freeze 25.8, slam | the frames rush back into one; silence; click; layers slam | THE FRAME (live stack) | the stack's own light | void | - | 2.4 | whoosh-bys, riser, silence, click, whip | cut (C8) | start_from S3-03 |
| S4-01 26.4-29.4 | reveal | medium (the whole frame) | screen-locked | locked (C8 settle 1.1 -> 1.0) | the frame plays again; payoff lockup builds | JD, THE FRAME | as S1 | as S1 | as S1 | 3.0 | slam, dhol drop | cut | - |
| S4-02 29.4-33.6 | inform | medium (the whole frame, dimmed) | screen-locked | locked | the end card builds and holds over the playing frame; the hook lockup returns | JD, THE FRAME, END CARD | as S1, dimmed x0.58 | as S1 | as S1 | 4.2 | card cues, reverse swell into f0 | loop_seam | start_from S4-01, ends on S1-01 |

Rhythm map: 0.3 s pause, 0.6 s glint, 1.5 s explode, 2.4 s orbit, 0.6 s steps x 10 (accelerating information, constant
tempo), 4 s re-hook (decelerate: one question, then a 2.2 s push and rack that accelerate into the portal), 1.8 s glide, 1.8 s surge, 2.1 s lanes, 1.8 s rush, 0.6 s silence, slam, 3 s
payoff, 4.2 s card. Hook: on screen the playing frame + its own title; heard "Aap ne ise palak jhapakte dekha" + the pause
click; withheld: what is inside 1/30 s.

### 7.2 The frame and its 12 layers (true by construction)

The frame is a **list of exactly 12 layer draw functions** `FRAME[i](cv, tl, lock)`, i = 1..12, in this order (back to front).
In assembled states they draw onto one canvas in order (no intermediate buffers); in exploded states each is rendered once to a
cached 1080x1920 RGBA sprite (at tl = 0.300, the pause) and drawn as a plane. HUD (chip, counter, tags, leader lines, seams,
lanes, captions, end card) is **annotation**, never a frame layer. QA asserts `len(FRAME) == 12` and that every exploded scene
draws exactly 12 frame planes. Layer clock: `tl = t` for t < 0.3; `tl = 0.3` for 0.3 <= t < 26.4; `tl = t - 33.6` for t >= 26.4
(the frame plays straight into frame 0). `lock` = `'hook'` (t < 26.4 and t < 0 in the loop), `'pay'` (26.4 <= t < 29.45),
`None` after.

| # | layer (tag) | content (frame px) | draw |
|---|---|---|---|
| 01 | background void (`andhera`) | `K.background('ember', tl, bokeh=0.0)` (opaque) | base |
| 02 | haze + god rays (`dhuaan`) | warm haze: `X.up(X.fbm(11, 5.0))` x 0.20 x (0.35 + 0.65 (1 - y/1920)), rgb SMOKE x1.8, alpha = same; 5 god-ray shafts from (1060, 60) at 200-228°, blurred σ 32 px, FLAME x0.10 emissive, fading to the bottom | over |
| 03 | bokeh (`roshni`) | kit bokeh `jawad_kit._draw_bokeh(L, 'ember', tl, None, 1.8, 3, 1.0)` masked to 0.15 inside the copy rects (hook lockup 220-860 x 420-935, payoff lockup 190-890 x 420-915, chip 575-945 x 1226-1338, face box 242-564 x 1120-1564; 40 px feather); **portal disc**: FLAME bokeh disc r 58 px at (812, 1120), brightness 0.45 (the C3 aperture); **hidden JD**: `T.render('JD', 'jw_key_core', px=80)` at (836, 330), blurred σ 2.5 px, emissive gain `g` x the sprite, alpha 0 (previs `hiddenjd_variants.png`: legible when looked for, a faint mark at phone size). `g = 0.35` on every frame except the r2 **glint**: `g = {-162: 1.20, -161: 0.70}.get(round(tl * 30), 0.35)`, i.e. f846 x1.20 and f847 x0.70 (tl = t - 33.6 there; keyed on the rounded frame so the motion-blur sub-samples, ±0.25 f, agree; the hook clock and the loop's t < 0 world never reach -162). The light is layer 03's own (no 13th layer, no SFX). Measured on the payoff previs (`R2_glint_*`): glyph peak 0.32 -> 1.09 linear (under the ~3x emissive cap); mean luma of its bbox +18.7 -> +42.3 code values over the local background | over (emissive) |
| 04 | JD cut-out (`chehra`) | `suit_threequarter` base = `FA.rim_light(plain, dep, light=(0.8, -0.5), gain=0, halo_strength=0)`, `FA.fade_open(('left','right'))`, drawn at (330, 1926), scale 0.90, anchor = bust bottom-centre (`FA.anchor_at`); idle `FA.idle(tl, seed=4)` only while playing | over |
| 05 | rim light (`rim light`) | rgb of `rim_light(..., halo_strength=0)` minus the base, alpha 0 (emissive), same placement | over (adds light) |
| 06 | contact glow / shadow (`saaya`) | shadow: cut-out alpha blurred σ 28 px, offset (-24, +18), black at 0.45, multiplied by (1 - cut-out alpha); plus the halo = rgb of the full look A minus the no-halo look (alpha 0) | over |
| 07 | embers (`chingaariyan`) | `J.embers(150, seed=7).draw(L, K.Cam(aperture=24), tl)` | over (adds) |
| 08 | caps words (`lafz`) | hook: `AAP NE ISE` (caps of `J.HouseTitle('AAP NE ISE', '0.03 sec', caps_px=86, key_px=210)` at key centre (540, 640)) + `DEKHA` (jw_caps 86) centred (540, 884.5); pay: caps of `HouseTitle('EK FRAME KI', 'keemat', 86, 210)` + sub `banane wala jaanta hai` (jw_body 56) at (540, 874) | over |
| 09 | keyword core (`keyword`) | `jw_key_core` of the keyword (`0.03 sec` / `keemat`), 210 px, centre (540, 640) | over |
| 10 | keyword halo (`chamak`) | `jw_key_halo` of the same, same anchor | over |
| 11 | underline (`lakeer`) | `J.underline(ul_len)` from the HouseTitle: x 220-860 (hook, ul_len 641) / 225-856 (pay, ul_len 631) at y 791 | over |
| 12 | finish (`finish`) | one RGBA sprite: vignette (black, alpha 0.62 x smoothstep(0.50, 1.15, r), r = hypot((x-540)/540, (y-960)/960)), halation (FLAME x0.22 x blur σ 22 px of the luminance > 0.9 of layers 05 + 09, alpha 0), grain (σ 0.8 px noise ±0.02: positive part emissive, negative part as black alpha x0.6). Calibrated by the colorist: with/without mean-luma change **8-20 %** on f396 vs f395 | over |

In playing states (t < 0.3 and t >= 26.4) layers 08-11 animate: hook lockup settled (no animation; it is the frame's title);
payoff `HouseTitle.draw` split exactly as above with `t0 = 26.4`, `out_t0 = 29.1`; the sub line rises 16 px and fades in
27.7-28.1 (out_cubic / inout_sine) and leaves with the lockup. Layer 03's hidden JD glints at f846-f847 (above; at 1:1 it sits
at screen (836, 330), above the payoff caps box y 441-501 and inside the safe zone). In paused states (0.3 <= t < 26.4) no
layer's content changes (pane 12's flick only hides and shows it): the r2 push and rack of §7.3 P8 are camera only.

### 7.3 Cameras and stack spacing (world units = px at the frame plane; checked with `camspec.py`)

Pane i sits at `z_i = (6.5 - i) * gap(t)`, centred on the frame (frame px (x, y) -> world (x - 540, y - 960, z_i)).
`cam = K.Cam.orbit(target, D, yaw, pitch, focal=F)`; F85 = 4533, F100 = 5333, F35 = 1867.

| phase | t | gap | camera | screen result (measured) |
|---|---|---|---|---|
| P1 | 0-0.9 | 0 | target (0,0,0), D 4533, yaw 0, pitch 0, F85 (identical to 1:1) | frame fills the screen |
| P2 | 0.9-2.4 | 0 -> 120 (inout_cubic) | u = easy_ease: D 4533 -> 8300, target y 0 -> -347.9 | stack bbox at 2.4: x 220-860, y 597-1736 |
| P3 | 2.4-4.8 | 120 | u = easy_ease: yaw 0 -> 52, pitch 0 -> 8, D 8300 -> 9400, target y -347.9 -> -265 | bbox y >= 598 throughout (counter clear); at 4.8 x 125-956, y 600-1649 |
| P4 | 4.8-5.4 | 120 | hold, D x (1 - 0.01 (t - 4.8)) | cover f153 |
| P5 | 5.4-6.0 | 120 -> 300 (inout_cubic) | easy_ease blend of every pose parameter to FLY(01) | samples 7 |
| P6 | 6.0-12.0 | 300 | FLY(k): target = LOOK_k (world, pane k), D 4920, yaw 32, pitch 3, F85; between arrivals inout_sine; arrivals 6.0 (01), 6.6, 7.2, 7.8, 8.4, 9.0, 9.6, 10.2, 10.8 (09/10, target pane 09), 11.4, 12.0 (12) | pane scale 0.92 at focus |
| P7 | 12.0-13.2 | 300 -> 30 (easy_ease) | easy_ease blend FLY(12) -> FRONT: target (0, -306.4, 0) (the stack centre is always z 0), D 8600, yaw 0, pitch 0, F100 | at 13.2 frame bbox x 199-881, y 547-1761 (scale 0.63) |
| P8 (r2) | 13.2-16.0 | 30 | FRONT, `D = 8600 (1 - p(t))`, `p = 0.01 (t - 13.2) + 0.035 S(t - 14.6)` (push toward the portal; below); rack from 15.0 (below); from 16.0 the camera (and its aperture / focus) is held static as C3's scene A | at 16.0: D 7982.9 (5.9 % closer than at 14.6, the frame x1.062; x1.077 since 13.2, scale 0.68); stack bbox x 172-908, y 514-1824 (pane 01, the opaque plate: x 187-893, y 532-1789); **portal disc (719.4, 1267.5), disc r 38.2 px** |
| C-A | 16.8-18.6 | live stack 120 | `K.Cam(pos=(0, -40, z))`, z -700 -> 300 (easy_ease), looking at (0, -40, 10470), F35, aperture 30 | corridor entrance (`sheet_corr.jpg` 1) |
| C-B | 18.6-20.4 | 120 | z 300 -> 7070 (inout_sine), look-at y -40 -> -346 (stack centred at screen y 1150), samples 7 | brake on 20.4 (stack scale 0.55) |
| C-C | 20.4-24.0 | 120 | hold, 1 %/s push | lanes 21.9-24.3 |
| C-D | 24.0-25.8 | 120 -> 60 (inout_sine, 24.0-25.5) | z 7070 -> 8545 (in_cubic), look-at y -346 -> 0 | frame plane scale 0.97 at gap 0 |
| C-E | 25.8-26.4 | 60 -> 0 (in_expo, 26.067-26.4) | near-freeze (1 %/s) | JD eye at ~(467, 1272) when gap = 0 |

LOOK_k (frame px) and tag anchors (frame px, the leader line's reticle; the tag's left-middle sits at the projected anchor +
offset, clamped into the safe zone):

| pane | look-at | tag anchor | offset | | pane | look-at | tag anchor | offset |
|---|---|---|---|---|---|---|---|---|
| 01 | (760, 520) | (300, 500) | (+36, -36) | | 07 | (600, 1120) | (760, 1250) | (+36, -36) |
| 02 | (760, 600) | (760, 600) | (+36, -36) | | 08 | (540, 680) | (800, 471) | (+36, -40) |
| 03 | (640, 760) | (812, 1120) | (+36, -36) | | 09/10 | (540, 640) | (830, 640) | (+30, -60) |
| 04 | (440, 1300) | (600, 1180) | (+36, -36) | | 11 | (540, 791) | (870, 791) | (+30, -40) |
| 05 | (440, 1300) | (590, 1010) | (+36, -36) | | 12 | (540, 960) | (60, 60) | (+36, +30) |
| 06 | (420, 1460) | (640, 1560) | (+36, -60) | | | | | |

**P8 push and rack (r2, viral gate fix 2).** The push: `S(x) = 0` for x <= 0; `x / 2 - (0.15 / π) sin(π x / 0.3)` for
0 < x < 0.3; `x - 0.15` for x >= 0.3 (the integral of an inout_sine rate ramp, so the dolly rate rises smoothly from 1 %/s at
14.6 to 4.5 %/s at 14.9; no velocity step). Measured scale rate: 1.01 %/s to 14.6, 2.80 at 14.75, 4.60 at 14.9, 4.85 at 16.0
(0.162 % per frame); the C3 zoom then takes over with per-frame steps of 0.48 % (the kit's first in_expo frame, under the
iris), 0.16, 0.21, 0.28, 0.38 %..., so the move never stalls at 16.0. The target stays (0, -306.4, 0) (the push
scales the frame about the screen centre, so the disc drifts from (708.6, 1249.2) at 14.4 to (719.4, 1267.5) at 16.0); a target
shift toward the disc was rejected because it lifts the frame top into caption C1. The rack: `aperture = 900 x
inout_cubic((t - 15.0) / 0.8)` (0 before 15.0, 900 from 15.8), `focus_dist` = the camera depth of pane 03 (the portal disc's
plane, z = +105) at every frame. CoC at 16.0: pane 01 2.2, 02 1.1, 03 0, 04 (JD) 1.1, 05 2.2, 06 3.3, 07 4.5, 08 5.6, 09 6.8,
10 7.9, 11 9.1, 12 10.3 px: the title, embers and grain melt while JD and the disc stay sharp (previs
`R2_rack_apertures_0_400_900_1400.jpg`, `R2_rack_title_crops.jpg`, `R2_push_rack_14p4-16p0_safe.jpg`, `R2_rehook_16p0.png`). The
gate's "~200" was measured too: at gap 30 and D ~8000 it gives <= 2.2 px CoC, an invisible rack, hence 900 (1400 blurs
`AAP NE ISE` past easy reading). Cost: panes 06-12 `dof=True` (7 slabs, <= 8), panes 01-05 sharp (their CoC <= 2.2 px). No layer
animates: the frame stays paused (§7.2). Caption C1 clears the moving frame top (§15).

Rack focus (C6, in-shot, the bible's rack-focus build): during P6 `focus_dist` = camera depth of the current LOOK point,
ramped `inout_cubic` over the 9 frames before each arrival; aperture 420 (adjacent panes ~9 px CoC, two away ~18 px).
Cost control: <= 8 DOF slabs; slabs half-res (540x960 sprites at width 1080) except the in-focus pane and pane 04; a slab whose
CoC > 40 px is drawn `dof=False` with `blur=` its CoC/2 from a quarter-res sprite.

Seams (annotation): each pane's 1080x1920 outline projected per frame (`cam.project` of its 4 corners), drawn in screen space
at half res as a 2 px line, ASH x0.22 + FLAME x0.12, blurred by the pane's CoC, opacity = smoothstep(40, 100, gap) (none in
the gap-30 re-hook view, full at 120 and 300); pane k flares
FLAME x1.8 -> x0.4 over 0.3 s when the counter reaches k (3.0-4.8). Spill: one `K.radial` FLAME x0.06 sprite behind the stack,
centred on its projected bbox, 1.4 x its height. No particles outside the frame's layers.

Corridor world (S3): billboard j = 0..28 at (±600, 0, 900 + 330 j) (even j left, odd j right), width 820, `dof=False`, opacity
x clamp((9500 - depth) / 4000, 0.15, 1); sprite = ONE pre-flattened stack sprite: the exploded stack (gap 120, hook lock, tl 0.3)
rendered once from `Cam.orbit((0,0,0), 9000, yaw=30, pitch=4, focal=4533)` on a transparent canvas, alpha-cropped (~811x1064 px),
cached as `<RW>/sprites/stack_flat.npz`. The 30th frame is the **live stack** (12 planes) at (0, 0, 10470). Light wave: billboard j
flares x1.6 -> x1.0 over 0.4 s at 16.9 + j x 0.0607. Rush: billboard j flies to (0, 0, 10470) with in_expo over
[24.0 + 0.02 (28 - j), 25.5], opacity -> 0 over its last 4 frames; 7 samples 24.0-25.6.

Audio lanes (S3-03): three floor planes (rot x 90°) at y +620, x centres -260 / 0 / +260, width 180, from z_cam + 400 to 9770;
each plane's texture (2048x256, rebuilt per frame) = SMOKE glass x0.6 (alpha 0.7) with the stem's RMS envelope drawn as a filled
waveform (VO FLAME, SFX AMBER, MUSIC RED, emissive x1.6), the near end = now, 30 px per audio frame receding (the next 6 s);
rise y +900 -> +620 21.9-22.2 (out_cubic), sink 24.0-24.3 (in_cubic). Playhead: a 3 px RED screen-space line across the near
ends. Legend (screen space): swatch 22 px + `jw_mono` 40 px label at (90, 1330), (90, 1385), (90, 1440). Envelopes:
`<RW>/audio/ek_frame_ki_keemat_env.json` = {fps: 30, vo: [...], sfx: [...], music: [...]} RMS dBFS per frame of the final mix
stems (music-supervisor writes it; the module falls back to a labelled placeholder and prints a warning; the master needs the
real file).

### 7.4 HUD chip

330x72 px pill, r 18, fill SMOKE x0.9, 2 px FLAME x1.4 stroke + `K.glow` (σ 6/16, 0.35); icon at left (play triangle f0-f8,
two 8x34 px pause bars from f9, at pill x 20-50; drawn shapes, not glyphs) IVORY; `00:00:00:01` jw_mono 38 px IVORY (258.4 px wide)
from pill x 54 to 312 (18 px right padding). Centre (760, 1282): pill box x 595-925, y 1246-1318 (right edge 5 px inside the
x 930 column; face box ends at x 564). Visible f0-f31 and t < 0 (loop).

### 7.5 GATE before animating (SLATE §4, binding)

Render one exploded-stack still at 4.8 and 5.1 (`--stills 4.8,5.1 --samples 1 --workers 1`) and one at 7.8 (fly, pane 04 in
focus), 13.2 (frontal) and 16.0 (r2: pushed and racked). Pass: 12 frame planes counted by the module; the hidden JD visible in
pane 03 at 5.1 (>= 30 px tall); JD's face pane and the rim pane read as two slices; counter and stack do not overlap; tags >= 44
px; nothing textual outside the safe zones; at 16.0 the title is soft but JD and the portal disc are sharp and the stack bbox is
x 172-908, y 514-1824 (±2 px). Compare with `previs/F1_cover_5p1_safe.png`, `F2_fly_7p8_safe.png`, `F3_rehook_13p2_safe.png`,
`R2_rehook_16p0.png` (final camera keys) and `sheet_fly300.jpg`. Only then animate.

---------------------------------------------------------------------------------------------------------------

## 8. Every on-screen string (house spelling; measured; <= 2 text blocks at any frame)

Widths are `T.measure` at the given px. Positions are centres unless "left". Frames are inclusive in-out.

| id | text | style, px | measured w x h | position / box | in -> out (f) | animation |
|---|---|---|---|---|---|---|
| H-A1a | `AAP NE ISE` | jw_caps 86 | 493.8 x 60.3 | box 293-787 x 441-501 | f0-f26 (frame layer; separates with its pane after f27); loop f990+ | settled at f0 (frame content; no entrance) |
| H-A1b | `0.03 sec` | jw_key 210 (core + halo) | 556.9 x 151.2 | centre (540, 640), box 262-819 x 564-716 | as H-A1a | settled |
| H-A1c | underline | J.underline 641 | - | x 220-860, y 791 | as H-A1a | settled |
| H-A1d | `DEKHA` | jw_caps 86 | 308.3 x 60.3 | box 386-694 x 854-915 | as H-A1a | settled |
| H-A2 | `00:00:00:01` (+ icon) | jw_mono 38 in the chip | 258.4 x 27.7 | chip box 595-925 x 1246-1318 (text x 649-907) | f0-f31 (fade f24-f32); loop | icon swap f9 |
| C-1a | `12` (odometer `00` -> `12`) | `T.Counter('jw_key', prefix='', decimals=0, sep='', min_int=2, px=230)` | 168.4 x 165.6 | centre (540, 380), box 456-624 x 297-463 | f90-f169 | rises 24 px + fades in f90-f94 (out_cubic); roll `K.Track([(3.0, 0, 'out_cubic'), (4.8, 12)])` with `vel`; exit 5.4-5.65 (in_cubic, fade + 12 px rise) |
| C-1b | `LAYERS` | jw_caps 86 | 334.8 x 60.3 | centre (540, 518), box 373-708 x 488-548 | f90-f169 | with C-1a |
| T-01..T-12 | see §2 | jw_mono 44, IVORY on a SMOKE scrim pill (alpha 0.55, r 10, pad 14) + FLAME reticle (6 px ring) + 1.5 px FLAME leader line | 244.6-462.9 x 32.1 (09/10 block 326.5 x 84) | projected anchor + offset (§7.3), clamped: x 80..(1010 - w) for y < 1050, x 80..(930 - w) for y >= 1050, y 250..1440 | tag k: (arrival - 0.1 s) -> (arrival + 0.9 s), i.e. 01 f177-f206, 02 f195-f224, 03 f213-f242, 04 f231-f260, 05 f249-f278, 06 f267-f296, 07 f285-f314, 08 f303-f332, 09/10 f321-f350, 11 f339-f368; 12 f357-f477 | fade 4 f in (inout_sine), leader draws 6 f; out 4 f (in_cubic). Max 2 tags at once |
| T-12s | `12 · finish  ON` / `12 · finish  OFF` | jw_mono 44 (`ON` FLAME tint, `OFF` ASH) | 408.3 / 435.6 x 32.1 | from 13.2: anchor pane-12 frame px (60, 60) -> screen (236.5, 584.7) + (36, +30); with the r2 push the anchor drifts to (214.2, 557.1) by 15.9: box x 250-708, y 571-631 over 13.2-15.9 (safe) | f396-f477 | the suffix switches on the flick frames f396 / f405 / f414 / f432 |
| H-B1a | `360` (body: odometer `012` -> `360`) | `T.Counter('jw_key', prefix='', decimals=0, sep='', min_int=3, px=240)` | 301.9 x 172.8 | centre (540, 380), box 389-691 x 294-467 | body f567-f664; hook B f0-f68 | body: fade in f567-f571, roll `K.Track([(18.9, 12, 'inout_sine'), (20.4, 360)])` with `vel`; exit 21.9-22.15 (in_cubic). Soft NIGHT_0 radial scrim (alpha 0.5) behind it while billboards streak |
| H-B1b | `LAYERS · 1 SECOND` | jw_caps 86 | 863.9 x 60.3 | centre (540, 520), box 108-972 x 490-550 | with H-B1a | with H-B1a |
| T-L1..3 | `VO · AI voice`, `SFX`, `MUSIC` | jw_mono 40 + 22 px swatch | 321.6 / 73.6 / 123.2 x 29.2 | left at x 122 (swatch at 90), y 1330 / 1385 / 1440 | f657-f729 | fade in 21.9-22.1, out 24.0-24.2 |
| P-1a | `EK FRAME KI` | jw_caps 86 | 561.6 x 60.3 | box 259-821 x 441-501 | f792-f884 | `J.HouseTitle` t0 26.4: caps rise 0.6 s, keyword rise from 26.62, underline 26.95-27.65, out_t0 29.1 (0.35 s in_cubic) |
| P-1b | `keemat` | jw_key 210 | 547.7 x 151.2 | centre (540, 640), box 266-814 x 564-716 | f799-f884 | per-glyph rise (HouseTitle) |
| P-1c | underline | J.underline | - | y 791 | f809-f884 | draw-on 0.7 s |
| P-2 | `banane wala jaanta hai` | jw_body 56 | 680 x 39 | centre (540, 874), box 200-880 x 854-894 | f831-f884 | rise 16 px + fade 27.7-28.1, out with P-1 |
| E-1 | `USKO YEH` / `bhejo` (lead OK; fallback `USSE YEH`, 429.1 px, caps box 325-755) | EndCard caps 86 / key 200 | 455.5 / 379.4 | caps box 312-768 x 523-583; keyword box 350-730 x 643-867 | f882-f1007 | EndCard (t_title 0.35, settle 1.85 s, exit last 0.36 s) |
| E-2 | `jo kehta hai "editing mein kya hai?"` | EndCard sub, jw_body 56 auto-shrunk to 760 px wide (~43 px) | 760 x ~30 | box 160-920 x 907-937 | sub in at 29.4 + 1.15 s | EndCard sub |
| E-3 | `JD` monogram | EndCard Monogram r 112 | - | centre (540, 365), box 420-660 x 245-485 | ring from 29.5 | EndCard |
| E-4 | `@jawad_mp4` | jw_handle 34 via `J.signature(cv, 760, 1575, opacity=...)` | 257.7 x 23.7 | box 631-889 x 1563-1587 | opacity = ramp(t, 30.4, 30.85, 'inout_sine') x (1 - ramp(t, 33.24, 33.567, 'in_cubic')) | (EndCard `handle=False`) |
| CAP | snake captions | snake_captions (Poppins 64 white + serif keyword 128) | solver | §15 | §15 | §15 |

`EndCard('USKO YEH', 'bhejo', sub='jo kehta hai "editing mein kya hai?"', handle=False, monogram='JD', dur=4.2, y_mono=365,
y_key=715, y_sub=922)`: measured hold 1.99 s (both spellings); previs `B3_card_safe.png` (USSE) and `R2_card_usko_safe.png` (USKO)
show every element inside the safe zones and clear of JD's face (hair top y 987, face box 242-564 x 1120-1564).

---------------------------------------------------------------------------------------------------------------

## 9. VO beat plan (Vlad, `elevenlabs_v4`, Devanagari text; per-line takes placed at the target onsets)

r2: the lines below are the script-gated lines of `SCRIPT.md` §3 / `script.json` v2 (the scriptwriter owns the final DEV and the
token table), with the viral gate's fixes 4 (V5 caption keywords) and 5 (V10 `usko`, pending the lead). Times are the
scriptwriter's syllable-model estimates at 1.08x (±10 % per line until the takes exist; SCRIPT §5), not the r1 2.65 words/s
word model. Lines may move ±0.25 s and stretch <= 3 % (bible §5.5). **Total 62 words** (hook A: V1A + V2-V10; hook B: V1B +
V2-V10 = 62). Speech only: 20.83 s at 1.08x; placed line spans 23.64 s (70 % of the reel; the rest is designed silence: tags
05-07, the 0.44 s re-hook gap, the corridor, the rush and drop-out 23.4-26.75, the payoff breath). Why not 80-90 words: 80 words
at 2.75 words/s are 29.1 s of pure speech plus >= 2.5 s of pauses in a 33.6 s reel that also needs the drop-out, a >= 0.3 s
silence after the hero hit, the re-hook silence and VO-free picture for the tags and the build.

| id | Roman caption track (house spelling; `*` = serif keyword) | spoken as | DEV (TTS; the scriptwriter's final) | meaning | words | target start - end (est) | explains on screen |
|---|---|---|---|---|---|---|---|
| V1A | `Aap ne ise *palak jhapakte dekha.` | = | आप ने इसे पलक झपकते देखा। | You saw this in the blink of an eye. | 6 | 0.10 - 2.37 (hard 2.70) | the playing frame, the pause, lockup `AAP NE ISE 0.03 sec DEKHA` |
| V1B | `Ek second. Teen sau saath layers.` | = | एक सेकंड। तीन सौ साठ लेयर्स। | One second. Three hundred and sixty layers. | 6 | 0.10 - ~2.25 (hard 2.70; hook B only) | corridor + `360 / LAYERS · 1 SECOND` |
| V2 | `Lekin is ek frame mein... *12 layers hain.` | Lekin is ek frame mein... baarah layers hain. | लेकिन इस एक फ़्रेम में... बारह लेयर्स हैं। | But in this one frame... there are twelve layers. | 8 | 3.07 - ~5.84 (hard 5.95); "baarah" 4.80 ±0.10 | counter 00 -> 12, panes light one by one; side-on lands on "baarah" |
| V3 | `Andhera. Dhuaan. Roshni. *Chehra.` | = | अंधेरा। धुआँ। रोशनी। चेहरा। | Darkness. Smoke. Light. Face. | 4 | per word on its tag: 6.00 / 6.75 / 7.30 / 7.90, ends ~8.36 (hard 8.45) | tags 01-04 |
| V4 | `Har lafz. Har *chamak.` | = | हर लफ़्ज़। हर चमक। | Every word. Every glow. | 4 | per phrase 10.03 / 10.95 ("lafz" ~10.23, "chamak" ~11.15), ends ~11.61 (hard 11.70) | tags 08 and 09/10 |
| V5 | `Aur ek *layer... jiske bina frame *zinda nahi lagta.` | = | और एक लेयर... जिसके बिना फ़्रेम ज़िंदा नहीं लगता। | And one more layer... without which the frame doesn't feel alive. | 9 | 12.05 - ~15.70 (hard 15.85); "layer..." ~12.45, "bina" ~13.83, "zinda" ~14.43 | stop on pane 12 + tag; flick OFF on "bina" (13.8), ON on "zinda" (14.4); then the push and rack toward the portal |
| V6 | `Ek second mein *30 frames.` | Ek second mein tees frames. | एक सेकंड में तीस फ़्रेम्स। | Thirty frames in one second. | 5 | 16.95 - ~18.19 (hard 18.85; >= 0.15 s after the C3 cut) | corridor of 30 frames, light wave |
| V7 | `Yaani har second... teen sau saath layers.` | = | यानी हर सेकंड... तीन सौ साठ लेयर्स। | So every second... three hundred and sixty layers. | 7 | 18.90 - ~21.52 (hard 21.99); "teen" 20.45 ±0.10 | surge, counter 12 -> 360 lands 20.4 |
| V8 | `Aur *awaaz ke 3 tracks.` | Aur awaaz ke teen tracks. | और आवाज़ के तीन ट्रैक्स। | And three tracks of sound. | 5 | 22.15 - ~23.39 (hard 24.15: the riser starts 24.6) | three lanes, the VO lane pulsing with these words |
| V9 | `*Keemat... banane wala jaanta hai.` | = | क़ीमत... बनाने वाला जानता है। | Worth... the one who makes it knows. | 5 | 26.75 - ~29.44 (hard 29.85; >= 0.30 s after the 26.4 hit); "banane" 27.70 ±0.10 | payoff lockup `EK FRAME KI keemat` + sub `banane wala jaanta hai`; the 28.2 glint lands inside "banane" |
| V10 | `Jo kehta hai "editing mein kya hai", usko *bhejo.` | = | जो कहता है "एडिटिंग में क्या है", उसको भेजो। | Whoever says "what's in editing", send it to them. | 9 | max(29.60, V9 end + 0.15) - ~32.82 (33.02 worst case; target <= 33.24 card exit, hard 33.35) | end card `USKO YEH bhejo` + sub (lead OK; fallback below) |

Delivery (casting brief for the takes): warm, measured, quietly proud; the contradiction: huge numbers said almost under the
breath. V2 the turn: stress on "ek", a held breath on "mein..."; V3 one word per beat (short stops, no list intonation); V5 lift
and hang on "layer...", lower and slower on "zinda nahi lagta"; V9 "Keemat..." low and quiet, a full breath, then the answer
plainly; V10 friendly, not salesy. **V10 spelling (fix 5, lead OK, §20 Q6):** the Roman token `usko` maps to DEV `उसको` ("to
him/her", spelled and read the same in India and Pakistan) and matches the card `USKO YEH`. If the lead keeps the SLATE card
`USSE YEH`: record T3 with `उसे` (`takes[T3].alt`) and write the Roman / words.json / SRT token as `usey`, never `usse` (which
Roman Urdu reads as उससे, "from / than him"). Pronunciation test first (SLATE §4 step 1): फ़्रेम, ज़िंदा, तीन सौ साठ, लफ़्ज़,
क़ीमत, एडिटिंग (fallback for frame: "tasveer" = तस्वीर; never in the hook). Takes (SCRIPT §7): T1 V5-V8, T2 V2-V4, T3 V9-V10
(**on HOLD** until the lead's call on fix 5), T4 V1A, T5 V1B = 5 takes ≈ 12.5 credits, budget <= 20 credits incl. retakes.
Fix 4 costs nothing: the V5 rom carries two `*` marks (`Aur ek *layer... jiske bina frame *zinda nahi lagta.`), re-run
`vo_chain.py process` with that `--rom`; the audio is unchanged. Pipeline: `vo_chain.py process` per take -> place each line at
its target start -> one reel-time stem `<RW>/vo/ek_frame_ki_keemat_vo.wav` (48 kHz 24-bit mono, -16 LUFS) +
`ek_frame_ki_keemat_vo.words.json` (reel time) and the hook B stem `ek_frame_ki_keemat_hookb_vo.wav` (0-3.0 s). Spoken numbers
lock: baarah (12), tees (30), teen sau saath (360), teen (3 tracks); nothing else.

---------------------------------------------------------------------------------------------------------------

## 10. Transitions (catalogue ids from the bible §3; <= 4 features, <= 2 ★, never two features within 2 bars)

| id | name | where | frames | jawad_tx call | params | SFX (paired) |
|---|---|---|---|---|---|---|
| **C3 ★** | push-in through object (portal) | cut 16.8 [7.0]: re-hook stack -> corridor | pre 24 (f480-f503), post 8 (f504-f511); samples 7 in the last 10 pre frames and the settle | `X.Plan` step `('C3', 16.8, dict(center=(719.4, 1267.5), r0=41.0, rim=False))` (r2); scene A = the P8 stack world with its 16.0 camera (pushed, aperture 900, focus pane 03) held static; scene B = the corridor | `center` = `cam.project` of the portal disc (pane 03, frame px (812, 1120), r 58) at the r2 16.0 camera, measured with `camspec.py`; `r0` = its projected radius 38.2 + 2.8 px, so the window (3 px soft edge) covers the disc's bright rim: at r0 = 38.2 the rim survives as an orange ring that grows to a large, near-centred ring by f500 (`previs/R2_c3_portal_crops_r38_ring.png`; never a centred ring), at 41.0 it is gone (`R2_c3_portal_crops_r41.png`, `R2_c3_f480-504_r41.jpg`); `rim=False` (no kit ring) | the plan's cues as `PLAN.cues()` emits them today: `reverse_swell` -3, 0.733 s, ending 16.733 (2 f before the cut), `air_zoom` -6 and `impact_soft` -1 on 16.8 |
| **C8** | crash / snap zoom | cut 26.4 [11.0]: slammed stack -> playing frame | pre 4 (f788-f791), post 6 (f792-f797); samples 5 | step `('C8', 26.4, dict(center=(465.0, 1282.0), s1=1.25, b0=1.1))` | push: plan's C8 post 0.4 + `cuts` 0.6 = 1.0 (C8 cannot take `push_gain`: request R2) | `whip` -6 at 26.367 (plan); the plan's `impact_soft` at 26.4 is **removed** and replaced by the ember_slam stack (§11) |
| C6 | rack-focus hand-off | 10 arrivals 6.6-12.0 (in-shot; 6.0 is reached by the swoop) | 9 f ramp before each arrival | not a `Plan` step: `K.Cam(..., focus_dist=...)` per §7.3 (the bible's C6 rack-focus build); `X.TX['C6']` (blur-swap) is not used | aperture 420 | `jd_ui_tick` -14 per arrival |
| L3 | exposure push (glue) | 0.0 (0.6), 4.8 (0.3), 12.0 (0.35), 20.4 (0.5), 26.4 (0.6) | impulse decay 16 | `cuts=` of `G.tx_finish` | - | covered by §11 |

Cut rule: HALF switch (`X.side_b`) at 16.8 and 26.4; frames f503/f504 and f791/f792 show no blur across. Orbit, fly-through,
corridor glide, surge and rush are in-shot `K.Cam` moves, not transitions.

Samples (`samples(t)`): 2 for 0-0.9, 13.2-16.0, 20.4-24.0, 25.6-26.267 and 26.6-33.6; 3 for 0.9-5.4 (except the orbit peak 3.2-4.4:
5) and 16.8-18.6 after the C3 settle; 5 for 6.0-12.0 (fly steps) and 12.0-13.2; 7 for 5.4-6.0, 18.6-20.4 and 24.0-25.6; the plan's
policy inside the C3 and C8 windows (`max` of the two when both apply).

---------------------------------------------------------------------------------------------------------------

## 11. SFX cue list (`ek_frame_ki_keemat_sfx.py`; audio.py + epic_sfx + sfx_jawad catalogs; `align='hit'` unless stated)

`import sfx_jawad as SJ` (the cue helpers live there, not on `J` = `jawad_kit`: r2 sync); `SJ.register()` and `epic_sfx.register()`
first; then `SJ.fit_under_vo(cues, '<RW>/vo/ek_frame_ki_keemat_vo.words.json')`
(raises if a HERO lands on a word). r2, measured on the planned V1A words (0.10-2.37): the f0 `impact_soft` passes with no
ducking (its hit, 0.006 s, lies before the padded speech window 0.04-2.43); the 0.3 click and the 0.6 glass slide are ducked
-8 dB (MID band, inside V1A), so the click plays at -4 dB: the sound-designer checks on the mix that it still reads as the
hook's sound event. The r1 `trailer_hit` at 0.0 raised `HeroOnWordError` (nearest legal hit 2.49 s), and
`trailer_hit` takes only `seed` / `pitch` (`params=dict(dur=...)` raises `TypeError`): truncation is always the cue-level
`dur`. Mix with `A.mix(cues, 33.6, ..., target_lufs=-18, tp_ceiling=-2.0, tail_fade=0.0)` (no tail fade: the loop needs the
swell into f0) and pass the stem to the final mix as a file. Tonal SFX tuned with `pitch_to` to D
(293.66 Hz octaves) or A (220/440 Hz). No SFX bed (the void is silent apart from the score).

| t (s) | f | name | gain dB | params / align | job |
|---|---|---|---|---|---|
| 0.000 | 0 | `impact_soft` | -8 | cue-level `dur=0.25` (truncated with a 50 ms fade; not inside `params`), `align='start'` (hit 0.006 s, the whole attack on f0) | frame-0 transient and the loop's release; it ends before the pause, so the frame's sound stops there (r2: replaces the HERO `trailer_hit`, gate fix 1) |
| 0.300 | 9 | `jd_mouse_click` | +4 | - | **motif: pause click** |
| 0.600 | 18 | `jd_glass_slide` | -2 | `dur=0.3` (hit = end = 0.600) | motif part 2: glass on glass, lands on the seam glint |
| 0.900 | 27 | `card_slide` | -8 | lp 1100 | layers separate |
| 1.600 | 48 | `whoosh_slow` | -10 | `direction=1` | pull-back |
| 2.400 | 72 | `whoosh_slow` | -8 | `direction=-1`, pan +0.3 | orbit starts |
| 3.000 | 90 | `slot_tick` | -12 | `n=12, dur=1.8`, align start | counter 00 -> 12 |
| 4.800 | 144 | `SJ.glass_truth(4.8, pitch=pitch_to('glass_tap', 587.33))` | stack | ui_click -6 (4.798), glass_tap 0, sub_drop 0.8 -10, jd_sparkle -10 (4.83) | "12" lands |
| 5.700 | 171 | `whoosh_slow` | -6 | `direction=1` (pass at 5.7) | swoop into the fly-through |
| 6.0, 6.6, 7.2, 7.8, 8.4, 9.0, 9.6, 10.2, 10.8, 11.4 | 180 ... 342 | `jd_ui_tick` | -14 | `pitch` alternating 1.0 / 1.12 | one tick per tag: 10 ticks for panes 01-11 (the 10.8 slot carries 09/10); pane 12 gets the 12.0 hit |
| 12.000 | 360 | `impact_soft` | -8 | - | the stop on pane 12 (re-hook, in the VO gap) |
| 12.000 | 360 | `glass_tap` | -10 | `pitch=pitch_to('glass_tap', 293.66)` | the near-invisible pane |
| 12.600 | 378 | `whoosh_slow` | -10 | `direction=-1` | swing to frontal |
| 13.200 | 396 | `jd_ui_click` | -6 | - | flick OFF |
| 13.500 | 405 | `toggle_on` | -8 | - | flick ON |
| 13.800 | 414 | `jd_ui_click` | -6 | - | flick OFF |
| 14.400 | 432 | `toggle_on` | -6 | - | resolved ON |
| 14.430 | 433 | `jd_sparkle` | -12 | - | the frame comes alive |
| 16.800 | 504 | C3 plan cues | - | as `PLAN.cues()` emits them: `reverse_swell` -3 (0.733 s, ends 16.733), `air_zoom` -6, `impact_soft` -1 | portal (no extra SFX for the r2 push and rack 14.6-16.0: the swell starts at 16.0) |
| 16.900 | 507 | `jd_sparkle` | -12 | - | light wave starts |
| 19.200 / 19.800 | 576 / 594 | `whoosh_by` | -6 | `dur=1.4, direction=1 / -1`, pan -0.4 / +0.4 | surge passes |
| 18.900 | 567 | `slot_tick` | -10 | `n=29, dur=1.5`, align start | counter 12 -> 360 |
| 20.400 | 612 | `SJ.glass_truth(20.4, pitch=pitch_to('glass_tap', 440.0))` | stack | as at 4.8 | "360" lands (in V7's pause) |
| 21.900 | 657 | `bar_grow` | -10 | `duration=0.3`, align start | lanes rise |
| 24.300 / 24.750 / 25.200 | 729 / 742.5 / 756 | `whoosh_by` | -6 / -6 / -8 | `dur=1.0`, direction ±1, pan ±0.5 | the rush |
| 24.6 -> 26.4 | 738 / 792 | `SJ.ember_slam(26.4, bpm=100, riser_beats=2, gap_beats=1)` | stack | riser 1.2 s ends 25.8 (-4); `flash_hit` -3 at 26.397; `impact_big` 0 (HERO) at 26.4; `sub_drop` -4 lp 120 dur 1.6 | the reveal: loudest moment |
| 26.067 | 782 | `jd_mouse_click` | +4 | - | **motif: the play click** (the held-breath element after 8 f of silence) |
| 26.367 | 791 | `whip` | -6 | `direction=1` (plan cue) | C8 punch |
| 26.620 | 799 | `shimmer` | -10 | hp 5500 | payoff keyword rises (caption-SFX 1 of max 3) |
| 29.500 | 885 | `swish_small` | -12 | align start (card cue) | monogram ring |
| 29.970 | 899 | `shimmer` | -10 | card cue | CTA keyword |
| 30.150 | 904.5 | `glass_tap` | -12 | card cue | monogram settles |
| 33.600 | 1008 | `reverse_swell` | -8 | `duration=0.8` (card cue; ends exactly on the loop) | loop bridge into f0's `impact_soft` |

Drop-out: after `A.mix`, gate the SFX stem 25.800-26.067 (4 ms fades; this also cuts the room-send tails of the 25.2 whoosh) so
f774-f781 are truly silent; the play click at 26.067 is the only sound until the slam. `pitch_to` is the bible §4.2 helper
(write it in the module). Instants with > 1 start: 4.8 (3 + sparkle 30 ms later), 12.0 (2), 16.8 (2: the plan's swell now ends 2 f earlier), 20.4 (3 + sparkle), 26.4 (`flash_hit`, `impact_big`,
`sub_drop` = 3; the music's `dhol_hit` is in the music stem). Hook B replaces 0-3.0 with: `impact_soft` -6 at 0.0, `whoosh_by`
0.2 (-4, dir 1), 0.6 (-6, dir -1), 1.2 (-8, dir 1), `jd_reverse_swell` (duration 1.2) ending 3.0 at -8; from 3.0 the body cues.
r2: no new SFX for the push and rack (14.6-16.0) or for the 28.2 glint (a silent visual reward; it sits under the VO "banane");
the only cue change is f0 (`impact_soft` for `trailer_hit`).

---------------------------------------------------------------------------------------------------------------

## 12. Music plan (`ek_frame_ki_keemat_music.py`, original, `epic_music` desi_epic variant, D, 100 BPM, 14 bars)

Source: `workspace/brand_reels/sfx/epic_music.py` (read-only; copy `style_desi_epic` into the reel module as `style_c08`, register
it as `EM.STYLES['c08_epic']` at runtime). Render `EM.render('c08_epic', dur=36.0, bpm=100, key='D', drop_bar=11, seed=8)`
(one extra bar so the module's 1.2 s end fade lies after 33.6), crop to 33.600 s, then gate 25.800-26.400 (4 ms fades, after the
reverbs). Changes from desi_epic: **no sitar** (the lead stem stays empty), **no dholak rolls** (one desi voice: the dhol),
**no `trailer_hit` at 0** (the f0 transient is the SFX stem's `impact_soft` since r2), **no braam at the drop** (the hero belongs to the SFX), strings start at
bar 1, the shepard and reverse-cymbal into the drop are shortened so no riser overlaps a word.

| bars | t (s) | section | strings (8ths, PHRYG_DOM ostinato) | harmonium (Sa-Pa-Sa drone swells, even bars) | percussion / bass | fx |
|---|---|---|---|---|---|---|
| 0 | 0-2.4 | cold (frame plays, pauses) | - | swell bars 0-1 (peak 3.456) -3 | - | - |
| 1-4 | 2.4-12.0 | explode, orbit, fly-through | enter at 2.4, LP 900, -5 | swells bars 2, 4 | - | - |
| 5 | 12.0-14.4 | re-hook | LP 900, -9 (thin) | (bar 4 swell) | - | - |
| 6 | 14.4-16.8 | resolved "with" | LP 900 -> 1200, -5 | swell bar 6 | - | - |
| 7-10 | 16.8-26.4 | corridor, surge, lanes, rush | LP 1200 -> 1500 by bar 10, -5 -> -3 | swells bars 8, 10 | `trailer_hit` pitch 0.9 on beats 1 and 3 of bars 8-10, -14 -> -8 | `shepard_riser` (duration 2.2) ends 26.4, -10; `reverse_cymbal` (duration 1.2) ends 26.4, -6 |
| gate | 25.8-26.4 | **drop-out** | silent | silent | silent | silent |
| 11 | 26.4-28.8 | **DROP** | LP 1500, -3 | (bar 10 swell continues) | `dhol_hit` 0 at 26.4; dhol chaal (1, 2&, 3, 4&) as desi_epic; hats 8ths -6; 808 root D -6 | - |
| 12 | 28.8-31.2 | resolve (end card) | LP 1200, -5 | swell bar 12, -6 | dhol chaal -8, no hats; 808 -9 | - |
| 13 | 31.2-33.6 | loop bar (cold colour returns) | LP 900, -7 | - | - | `reverse_cymbal` (duration 2.4) ends 33.6, -8 (into f0) |

Exports: `<RW>/music/ek_frame_ki_keemat_music.wav` (48 kHz 24-bit) + stems + `.json` (beatgrid 100 ±0.2 BPM, phase ±15 ms).
Final mix: `epic_mix.mix_reel('ek_frame_ki_keemat', 33.6, vo=<VO stem>, sfx=<SFX stem file>, music=<music wav>, out_dir=<RW>/audio)`
-> `_mix.wav` (A), `_vo_sfx.wav` (B), stems; then write `ek_frame_ki_keemat_env.json` (§7.3) from the stems at the mix gains;
then `epic_mix.mux`. Hook B audio: its own 0-3.0 (VO B + SFX B + the same music) + the body from 3.000 (5 ms crossfade).
No tape-stop in this reel (that is C26's device). No trending audio baked in. Audio name: "Original audio · Aap ne ise 0.03
sec dekha · @jawad_mp4".

---------------------------------------------------------------------------------------------------------------

## 13. 3D props

**None** (SLATE §3.3). No Blender work order for this reel. Every 3D element is a toolkit plane: 12 frame panes, the pre-flattened
stack sprite as 29 billboards, three lane planes. The blender-3d-artist has nothing to build here.

---------------------------------------------------------------------------------------------------------------

## 14. Face plan (`ek_frame_ki_keemat_faces.py`, face-compositor)

| item | spec |
|---|---|
| crop | `suit_threequarter` only (764x1112 2x master; face box 284.6-641.6 x 217.0-709.3; eye_mid (532.8, 396.4); open sides b l r). No swaps, no other pose. |
| look | **rim look A** split into three frame layers: 04 base (`FA.rim_light(plain, dep, light=(0.8, -0.5), gain=0, halo_strength=0)`), 05 rim (look without halo minus base, emissive), 06 halo (full look minus no-halo look, emissive) + the soft shadow (§7.2). `FA.fade_open(('left','right'))` on all three (the bust bottom runs off the frame). Cine look D: not used (no narration shot of JD). |
| placement | `K.draw(cv, spr, 330, 1926, scale=0.90, anchor=FA.anchor_at(plain, look, (plain.shape[1] / 2, plain.shape[0])))`: on screen face box x 242-564, y 1120-1564; eye mid (465, 1282); hair top y 987; head box x 172-634 |
| motion | `FA.idle(tl, seed=4)` (dx, dy, rot, scale) on layers 04-06 together, **only while playing** (t < 0.3 and t >= 26.4); frozen otherwise. Never warped; in the exploded views the pane is an honest flat card (seen up to 52° yaw by design: it is a layer, not a person). |
| scale | 0.90 of the 2x master (<= 1.0); the C8 punch reaches 1.09 for f789-f791 under zoom blur (accepted); B settles 1.1 x 0.90 = 0.99 |
| in / out | in every frame as pane 04 (and inside the corridor sprite); a readable "person" only in S1 (0-0.9 s) and S4 (26.4-33.6 s: 3.0 s before the end card dims the world, <= 3.5 s rule) |
| captions | never over the face: the captions are hidden in S1 and S4; avoid rects in §15 |
| realism | skin texture kept, no smoothing or relight (human-realism / photo-realism); `G.tx_finish` skin protection on; check halo and fringe on the ember background (`previs/B1_f0.png` shows the intended result) |
| outputs | `face_layers()` -> dict(base, rim, halo, shadow, anchor, boxes) cached; `<RW>/qa/faces_check.png` (the f0 composite, 1:1) |

---------------------------------------------------------------------------------------------------------------

## 15. Captions plan (`snake_captions.py`, caption-designer)

Words: `<RW>/vo/ek_frame_ki_keemat_vo.words.json` (reel time, offset 0). Captions show only where no designed type already says
the line (two-layer rule). Three `SC.Captions` instances, one per window (a chunk of one instance never overlaps a chunk of
another: each instance is fully gone before the next one's first word, checked by `cap.report()` times), `max_words=3`,
keyword = the word marked `*`:

| inst | window (s) | words | chunks (`*` = keyword) | band / y | avoid rects (x0, y0, x1, y1) | notes |
|---|---|---|---|---|---|---|
| C1 | 12.0-16.25 | V5 | `Aur ek *layer*...` / `jiske bina` / `frame *zinda*` / `nahi lagta` (r2, gate fix 4: two keywords in the line, one per chunk; rom `Aur ek *layer... jiske bina frame *zinda nahi lagta.`) | upper, `y=420` | r2: `avoid=lambda t: [stack_rect(max(t, 13.2)), (245, 565, 715, 635)]`: `stack_rect(t)` = the bbox of the 48 projected pane corners at the scene camera of t, mapped through the C3 A-side affine for t >= 16.0 (the module exposes it); the second rect is tag 12 over 13.2-15.9 | `hold=0.15`: the last chunk must be gone by 16.25 (the C3 zoom carries the opaque frame top past y 496 at ~16.28). t is clamped to 13.2 because during the 12.0-13.2 swing the first chunk sits over the moving, folding stack, as in r1 (gate §3 accepted the re-hook view) |
| C2 | 16.9-20.8 | V6 + V7 first half | `Ek second mein` / `*30* frames` / `Yaani har second...` (digits on screen as in the house SRT; SCRIPT C6) | lower (baseline ~1270) | from 18.9 the counter (100, 280, 980, 560), passed as `avoid=lambda t: [...]` | one instance so the V6 and V7 chunks never overlap; `hide=[(20.13, 21.99)]` (the counter says "360 LAYERS") |
| C3 | 22.1-24.7 | V8 | `Aur *awaaz* ke` / `3 tracks` | upper, `y=420` | lane legend (80, 1300, 470, 1470) | the 360 lockup is gone by 22.15 |

Verified with the real solver (`snake_captions.Captions`) on estimated word times, r2 (`previs/r2/capcheck2.py`): **C1**
`check() == []` on three timings: the scriptwriter's estimate (V5 ends 15.70), the r1 plan (15.79) and a late case (15.85, the
hard window end). Chunk bboxes: `Aur ek layer...` and `frame zinda` y 320-506, `jiske bina` y 366-496, `nahi lagta` y 326-456 (the
solver lifts it as the frame grows); last exit 16.15 / 16.24 / 16.30. Clearance to the moving frame top over each chunk's
life: >= 29.6 px to the all-pane bbox and >= 46.1 px to pane 01 (the opaque plate) for the first three chunks; `nahi lagta`
47.8 / 66.1 px (estimate), 38.4 / 56.9 px (r1 plan), 24.9 / 43.7 px in the late case (it is fading out by then). The frame top (all panes): y 546.8 at
13.2, 535.2 at 15.0, 514.1 at 16.0, 498.4 at 16.2, 489.7 at 16.25 (pane 01: 562.3, 551.6, 532.2, 516.8, 508.3). **C2**
`check() == []`, bboxes y 1167-1356, x 155-880 (x <= 930 in the like column band), last exit 20.60. **C3** `check() == []`,
bboxes y 310-506, last exit 24.04. The caption-designer re-runs this on the real words.json.

Hidden windows (no captions): 0-3.0 (hook lockup), 3.0-12.0 (counter and tags carry V2-V4), 20.13-21.99, 26.4-33.6 (payoff lockup
+ sub, end card + sub). `cap.check() == []` for every instance; `cap.save_srt(<RW>/captions/ek_frame_ki_keemat.srt)` from the
union of instances (sentence case, house spelling). No caption SFX beyond the one `shimmer` at 26.62. The SRT holds only the
three caption windows; V10's Roman token in `words.json` follows §9 (`usko`, or `usey` under the fallback; never `usse`).

---------------------------------------------------------------------------------------------------------------

## 16. Cover, post copy and labels

- **Cover:** frame 153 (5.1 s): the side-on stack with `12 / LAYERS` (title y 297-548, inside y 285-1480 and the 3:4 crop
  y 240-1680). Thumbnail test at 240 px wide: "12" must stay readable. Alternative (lead's choice): frame 0 (JD + `AAP NE ISE 0.03
  sec DEKHA`).
- **IG caption** (L1 = 49 characters, counted; r2: the comment prompt moves up to **line 2**, 36 characters, so it sits next to
  the hook instead of at line 7, which the Reels viewer cuts off at about 55-60 characters [secondhand]):

```
Ek frame mein kitni layers? Video editing ka sach
Is frame mein JD chhupa hai. Mila? 👇
Aap ne ise 0.03 sec dekha. Is ek frame mein 12 layers hain, aur har second mein 360.

Andhera, dhuaan, roshni, chehra, rim light, chingaariyan, har lafz ki chamak.
Aur ek layer jo dikhti hi nahi.

Video editing, motion graphics, compositing: sab ek frame ke andar.
Usko bhejo jo kehta hai "editing mein kya hai".

Voice: AI (TTS)
#videoediting #motiongraphics #videoeditor #jawadmp4
```

  The send line follows the lead's call on fix 5 (§20 Q6): "Usko bhejo ..." with the `USKO YEH` card, "Usey bhejo ..." if the
  card stays `USSE YEH` (never "Usse").
- **Hashtags:** 4, including #jawadmp4.
- **Comment prompt (r2, gate fix 3):** right after publishing, @jawad_mp4 posts **"Is frame mein JD chhupa hai. Mila? 👇"** as the
  first comment and pins it. After 24 h, reply to it with the answer, **"Layer 03, top right, roshni ke beech. Aur 'keemat'
  ke baad ek pal ke liye chamakta bhi hai."** (both facts true by construction: layer 03 at (836, 330); the f846-f847 glint
  after the `keemat` lockup; no new number in the post copy, so the number lock of §2 holds), and pin that reply too
  (if the app does not allow pinning a reply, post the answer as a new comment and pin that). Whoever publishes the reel does
  both; the delivery-packager puts the two comment texts in the hand-off. The end card asks only for the send.
- **AI label:** "AI info" ON (synthetic voice; the character sheets may be AI-generated). The caption says "Voice: AI (TTS)".
- **Audio name:** "Original audio · Aap ne ise 0.03 sec dekha · @jawad_mp4". **Alt text:** "A video editor's frame splits into its
  12 glowing layers in a dark void; JD in a black suit with a flame rim light; text: Aap ne ise 0.03 sec dekha."

---------------------------------------------------------------------------------------------------------------

## 17. Engineering contract

### 17.1 Files (only these; never touch another reel's files; shared modules are read-only)

| path | owner | content |
|---|---|---|
| `pipeline/jawad_reels/ek_frame_ki_keemat.py` | motion-timeline-builder | the reel module (`build(hook='A')` + module-level contract for A) |
| `pipeline/jawad_reels/ek_frame_ki_keemat_hookb.py` | motion-timeline-builder | `from ek_frame_ki_keemat import build, DUR, LOOK, BPM; draw, post, samples, cues, prewarm = build('B')` |
| `pipeline/jawad_reels/ek_frame_ki_keemat_faces.py` | face-compositor | `face_layers()` (§14) |
| `pipeline/jawad_reels/ek_frame_ki_keemat_sfx.py` | sound-designer | `cues(hook='A')`, `build()` -> SFX stem files |
| `pipeline/jawad_reels/ek_frame_ki_keemat_music.py` | music-supervisor | `style_c08`, `render()`, `mix()`, `envelopes()` |
| `<RW>` = `workspace/jawad_reels/ek_frame_ki_keemat/` | all | `vo/`, `audio/`, `music/`, `captions/`, `sprites/`, `gate/`, `qa/`, `previs/` (done), `out/` and `out_hookb/` (render.py writes there: `<WS>/out/ek_frame_ki_keemat` -> `<RW>/out`, `<WS>/out/ek_frame_ki_keemat_hookb` -> `<RW>/out_hookb`, symlinks created) |

### 17.2 Module contract (`ek_frame_ki_keemat.py`)

```python
import jawad_kit                                  # FIRST
from jawad_kit import K, T, ui, J
import jawad_tx as X, jawad_grade as G, endcard as E, snake_captions as SC
DUR, LOOK, BPM = 33.6, 'ember', 100               # 14 bars; X.Grid(100).at(14) == 33.6
BED = None                                        # no SFX bed (audio is built by the sfx/music modules)
CUTS = [(0.0, 0.6), (4.8, 0.3), (12.0, 0.35), (20.4, 0.5), (26.4, 0.6)]
PLAN = X.Plan([('C3', 16.8, dict(center=(719.4, 1267.5), r0=41.0, rim=False)),        # r2 (P8 push, §7.3 / §10)
               ('C8', 26.4, dict(center=(465.0, 1282.0), s1=1.25, b0=1.1))])
CTA = 'USKO YEH'                                 # r2, lead OK pending (§20 Q6); 'USSE YEH' if the lead keeps the lock
CARD = E.EndCard(CTA, 'bhejo', sub='jo kehta hai "editing mein kya hai?"', handle=False, monogram='JD',
                 dur=4.2, y_mono=365.0, y_key=715.0, y_sub=922.0)        # build in assets(); T_END = 29.4
# scenes: S_STACK(t) (S1 + S2, 0-16.8), S_CORR(t) (S3, 16.8-26.4), S_PLAY(t) (S4, 26.4-33.6 and t < 0)
# r2: S_STACK's camera for t >= 13.2 = FRONT with D = 8600 (1 - p(min(t, 16.0))), aperture / focus per §7.3 P8 (rack 15.0-15.8,
#     panes 06-12 dof=True); stack_rect(t) for caption C1 (§15); FRAME[3] carries the f846-f847 hidden-JD glint (§7.2)
# world(t) = PLAN.draw(t, [S_STACK, S_CORR, S_PLAY]) ; HUD (chip, counters, tags, seams, lanes) inside the scenes
# draw(t): cv = E.loop_world(world, t, DUR, d=0.6); captions (3 instances) ; CARD.draw(cv, t, 29.4) ; signature ; return cv
# post(cv, t): kw = merge(PLAN.post_kw(t), CARD.post_kw(t, 29.4, DUR))     # merge: sum 'push', multiply 'bloom_scale'
#              return G.tx_finish(cv, t, LOOK, cuts=CUTS, **kw)
# samples(t): §10 ; cues(): [] (the sfx module builds the mix; render with --no-sfx-build --audio <mix>)
# prewarm(): frame layer sprites at tl 0.3 (both locks), stack_flat sprite, faces, type, card, captions
```

Self-test (`python3 ek_frame_ki_keemat.py --selftest`): `len(FRAME) == 12`; 12 frame planes in every exploded scene; `X.Grid(100)`
times of §5; the camera bbox checks of §7.3 (counter clear 3.0-5.4); every text box of §8 inside the safe zones; at most 2 text
blocks per frame (from the module's text registry, sampled every frame); `CARD.hold >= 1.5`; hidden JD present in layer 03.
r2 additions: the P8 camera at 16.0 gives stack bbox x 172-908, y 514-1824 and the portal disc at (719.4, 1267.5), r 38.2 (±0.5
px), equal to the C3 step's `center` (r0 = r + 2.8); the push rate is continuous (no frame-to-frame scale step > 0.2 % in
13.2-16.0); aperture 0 before 15.0 and 900 from 15.8; the hidden-JD gain is 0.35 on every frame except f846 (1.20) and f847
(0.70), including under 2-5 motion-blur samples; no frame layer's sprite changes between f9 and f791 (pane 12's flick only
hides it).

### 17.3 Commands (all heavy work through the semaphore; run from `pipeline/jawad_reels`)

```bash
H=tools/heavy.sh; RW=/home/user/100/workspace/jawad_reels/ek_frame_ki_keemat
$H python3 ek_frame_ki_keemat.py --selftest
$H python3 render.py ek_frame_ki_keemat --stills 4.8,5.1,7.8,13.2,16.0 --samples 1 --workers 1     # GATE (§7.5)
$H python3 render.py ek_frame_ki_keemat --stills 0,0.3,0.6,1.5,2.4,6.0,12.0,13.5,14.6,15.4,16.0,16.5,16.8,19.5,20.4,23.0,25.9,26.267,26.4,28.167,28.2,28.233,28.267,31.5,33.567 --samples 1 --workers 1
$H python3 render.py ek_frame_ki_keemat --sheet 24 --samples 1 --workers 1
$H python3 render.py ek_frame_ki_keemat --preview --workers 1 --no-sfx-build --audio $RW/audio/ek_frame_ki_keemat_mix.wav
FOSTER_NICE=10 $H python3 render.py ek_frame_ki_keemat --workers 2 --no-sfx-build --audio $RW/audio/ek_frame_ki_keemat_mix.wav
$H python3 render.py ek_frame_ki_keemat_hookb --range 0 3.0 --workers 1 --no-audio                    # hook B frames
$H python3 ek_frame_ki_keemat_music.py render && $H python3 ek_frame_ki_keemat_sfx.py build && $H python3 ek_frame_ki_keemat_music.py mix
```

### 17.4 Budgets

Render: half-res slabs, <= 8 DOF slabs, samples per §10: target 35-45 min for the master on 2 workers (production panel);
abort and re-plan if the gate stills exceed 6 s/frame at 1 sample. Memory: ~2 GB per worker. Disk: `<RW>` <= 2 GB; delete
render intermediates and preview files after the master and the B splice are verified; keep stems, the masters, the cover and
`qa/`. CPU: one heavy job per agent, `tools/heavy.sh` only; Blender none.

### 17.5 Text-block log (at most 2 at any frame)

0-0.9: lockup (frame) + chip · 0.9-3.0: lockup panes (separating) · 3.0-5.65: counter · 5.9-12.0: <= 2 tags · 12.0-16.25: tag 12
(to 15.9) + caption C1 (from 15.0 the frame's own title melts out of focus, r2) · 16.9-18.9: caption C2 · 18.9-21.9: counter + caption C2 (to ~20.8) · 21.9-24.7: lane legend (to 24.2) + caption C3 · 26.4-29.45:
payoff lockup (with its sub; the 28.2 glint of the hidden JD is picture, not a block) · 29.4-33.6: end card (one block) · loop 33.0-33.6: hook lockup fading in + card exiting.
The frame's own title inside the exploded stack and inside the corridor sprites is picture (it is the object being shown and
named by the tags), not a text block; it is never larger than the tags it sits behind except in the frontal re-hook view.

---------------------------------------------------------------------------------------------------------------

## 18. Reel-specific QA acceptance checklist (measurable; two lenses + an independent verifier per major finding)

**Format and truth**
- [ ] ffprobe: 1080x1920, 30/1 fps, **1,008 frames**, video duration 33.600 s; audio 48 kHz, 33.600 s.
- [ ] `len(FRAME) == 12` and 12 frame planes per exploded scene (self-test log); no light, particle or text inside the frame
  that is not one of the 12 layers; HUD is listed as annotation.
- [ ] Spoken and shown numbers are only 12, 3, 30, 360, 0.03 sec, 00:00:00:01 (VO words.json + §8 strings). No hours, rates,
  clients. Lane label reads exactly `VO · AI voice`.
- [ ] Hidden JD legible as "JD" in f0 at 100 % when looked for, present in f153 (projected >= 30 px tall); mean luma over its
  90x70 px bbox 3-25 code values above the local background (previs measured +18.5: findable, not obvious).
- [ ] r2 glint: f846 and f847 are the only frames whose hidden-JD bbox differs from f845 / f848; on f846 its mean luma is 30-55
  code values above the local background (previs +42.3); f848 is back to the f845 level; no SFX starts at 28.2.

**Hook and structure**
- [ ] f0: lockup ink present and inside the safe zone; the `impact_soft` transient on f0 (onset detection on the mix, within
  f0-f2) and no HERO sound in 0-2.43; VO onset <= 0.15 s; V1A ends <= 2.70 s; V1B ends <= 2.70 s.
- [ ] Pause at f9: the ember layer is pixel-identical between any two frames in 0.3-26.4 s rendered with the same camera (assert
  `tl == 0.3`); chip icon is ▶ on f0-f8 and ❚❚ from f9.
- [ ] Re-hook at f360 with VO silence >= 0.3 s around it; C3 cut at f504; reveal hit at f792; end card from f882; hold >= 1.5 s.
- [ ] r2 push and rack: the stack bbox measured on f438 and f480 matches §7.3 (f480: x 172-908, y 514-1824, ±2 px); f474-f480
  show the title panes soft and JD and the portal disc sharp; the C3 window opens exactly on the disc (no orange ring around
  the window on f486-f503); f478-f483 stepped side by side show no stall at the hand-off (scale steps ~0.16 % per frame; C3's
  first in_expo frame, f481, steps ~0.5 % under the iris, as designed).
- [ ] Flick: state changes exactly on f396, f405, f414, f432; <= 3 changes in any 30-frame window; mean-luma change with vs
  without between 8 % and 20 % (f395 vs f396).

**Layout and type**
- [ ] Ink scan of every designed string (§8): inside x 70-1010, y 230-1480; x <= 930 when y is in 1050-1700; nothing textual at
  y > 1620. Tags 44 px in screen space; each tag visible >= 1.0 s; never more than 2 tags.
- [ ] <= 2 text blocks at every frame (registry log + 5 fps sheet review).
- [ ] Captions: `cap.check() == []` for C1-C3; no caption over the face rects; highlight on word onset ±1 frame; no doubled words
  with designed type; SRT exported. C1's keywords are *layer* and *zinda* (one per chunk); C1 is gone before the opaque frame
  top reaches its bbox (§15); C2 shows `30`, C3 `3` as digits.
- [ ] Type IVORY (no pixel of designed type at pure white 255,255,255 after the finish).

**Motion and finish**
- [ ] No full-frame flash: the 1st-percentile luma of each push frame is within ±2 code values of its neighbours; YMIN 16-22 on
  void frames (signalstats).
- [ ] Cut rule: f503/f504 and f791/f792 show no blur across the cut.
- [ ] Camera bbox checks (§7.3) hold on the rendered stills: the counter and the stack never overlap (3.0-5.65).
- [ ] Hue budget: red-orange >= 60 % of saturated pixels (`jawad_grade.py verify <mp4> ember`).
- [ ] Face: `suit_threequarter` only, never warped or mirrored; display scale <= 1.0 except f789-f791 (<= 1.09); no halo or
  fringe artefacts on the ember background.
- [ ] Loop: `E.seam_report(...)['ok']` is True; f1007 -> f0 step <= 1.5x a normal step; the frame-0 lockup and chip are back by f1007.

**Sound**
- [ ] Mix A: -14 ±0.5 LUFS, TP <= -2.0 dBTP (wav), <= -1.5 dBTP after AAC, LRA 5-9; mix B (VO + SFX) same targets.
- [ ] VO >= 8 LU over the music (median, voiced frames); SFX in VO windows >= 6 LU under the VO; `SJ.fit_under_vo` raised nothing.
- [ ] Drop-out: RMS < -60 dBFS over f774-f781 (8 frames); between f782 and f791 only the play click, the C8 whip's lead-in
  (hit f791) and the `flash_hit` suck (0.1 s before 26.397).
- [ ] Max momentary loudness within ±0.2 s of 26.4; the phone check (`A.hp(x, 250, 4)`) loses <= 7 dB on the reveal.
- [ ] Beatgrid of the music: 100 ±0.2 BPM, phase ±15 ms; drop on 26.4; loop: the last 50 ms are not silent and the reverse swell
  ends on 33.600.
- [ ] Every cue name resolves in `audio.names()` after `sfx_jawad.register()` + `epic_sfx.register()`; no instant with > 3 SFX starts.

**Delivery**
- [ ] A and B masters, share encodes (< 100 MB), preview (< 30 MB), cover JPG f153, SRT, stems, `_vo_sfx` version; B frames 90-1007
  are byte-identical in content to A's (frame diff 0 before encoding).
- [ ] IG caption L1 49 characters with "Video editing", L2 = the comment prompt; the pinned-comment texts (§16) in the hand-off;
  4 hashtags incl. #jawadmp4; AI info ON; end card, V10 token and the caption's send line use the same spelling (`usko`, or the
  `USSE` / `usey` fallback); `<RW>` <= 2 GB (`du -sh`).

---------------------------------------------------------------------------------------------------------------

## 19. Work orders (who runs next, on what)

r2 status: the script gate ran (`GATE.md`, verdict FIX); `SCRIPT.md` / `script.json` v2 already carry fixes 4 and 5 (pending).
1. **hinglish-scriptwriter**: T1, T2, T4, T5 can be recorded now; **T3 waits for the lead's call on `USKO` (§20 Q6)**: approved ->
   उसको / `usko`, refused -> `takes[T3].alt` (उसे / `usey`). Pronunciation test in T1; `vo_chain.py process` (V5 rom with two `*`);
   place lines at the target onsets; reel-time VO stem + words.json (A) and the hook B stem.
2. **viral-strategist**: red-team on the preview (the r2 window 14.4-16.8 and the 28.2 glint at phone size included).
3. **face-compositor**: `ek_frame_ki_keemat_faces.py` (§14) + `qa/faces_check.png`.
4. **colorist**: layer-12 finish calibration (8-20 % with/without), `ember` check on the gate stills and the master (hue budget,
   YMIN, skin), confirm `G.tx_finish` with the push list.
5. **motion-timeline-builder**: `ek_frame_ki_keemat.py` + `_hookb.py` on placeholder audio; selftest; **gate stills (§7.5, now
   incl. 16.0) before animating**; then stills, sheet, preview; master after the mix exists. r2 deltas: P8 push + rack (§7.3),
   C3 `center` / `r0` (§10), the layer-03 glint (§7.2), `stack_rect(t)` for C1 (§15), `CTA` string (§17.2).
6. **sound-designer**: `ek_frame_ki_keemat_sfx.py` (§11), A and B stems (tail_fade 0), `fit_under_vo` report. r2 delta: f0 is
   `impact_soft` -8 with cue-level `dur=0.25` (no `trailer_hit` anywhere in hook A); check the ducked 0.3 click on the mix.
7. **music-supervisor**: `ek_frame_ki_keemat_music.py` (§12): score, gate, mix A/B, stems, `env.json`, mux, loudness report (no r2
   change to the score).
8. **caption-designer**: three `SC.Captions` instances (§15: r2 chunks and C1's moving `avoid`), SRT.
9. **motion-qa-reviewer**: two lenses on §18 + an independent verifier per major finding.
10. **delivery-packager**: A/B splice at f90, encodes, cover, caption text and the two pinned-comment texts (§16).
11. **blender-3d-artist**: no work (§13).

---------------------------------------------------------------------------------------------------------------

## 20. Open questions (none blocks the build; defaults set)

1. AI label: ON (SLATE default). 2. VO lane label "VO · AI voice": ON (honest default; one string to change). 3. Trial-Reel
eligibility for hook B: unknown; render it anyway. 4. Cover: f153 (side-on `12 / LAYERS`) or f0 (JD + lockup): default f153.
5. Comment prompt: pinned as the first comment at posting; after 24 h the reply "Layer 03, top right, roshni ke beech. Aur
'keemat' ke baad ek pal ke liye chamakta bhi hai." is pinned too (§16).
6. **(r2, needs the lead) End-card spelling, viral gate fix 5:** `USKO YEH / bhejo` with V10 उसको / `usko` (this brief's build
value) instead of SLATE §5.1's locked `USSE YEH / bhejo`. It blocks only TTS take T3 (V9 + V10) and the one `CTA` string; every
other take and the build can go now. If the lead keeps the lock: `CTA = 'USSE YEH'`, T3 with उसे, Roman / SRT token `usey`, IG
send line "Usey bhejo ...", and §8 E-1 back to 429.1 px (caps box 325-755). Note for the lead: SLATE §5.1 lists every reel's CTA,
so the change touches only C08's row there (the other reels' CTAs, e.g. `US CLIENT KO`, `US DOST KO`, already use "ko").

---------------------------------------------------------------------------------------------------------------

## CHANGELOG

- **r2 (2026-10-08, creative-director), after the viral gate r1 (`GATE.md`, verdict FIX, fixes 1-5):**
  - Fix 1 (§5 rows 1 + 44, §6.1, §6.3, §7.1 S1-01, §11, §12): f0 `trailer_hit` -6 (a HERO under "Aap"; `fit_under_vo` raised
    `HeroOnWordError`; `params=dict(dur=0.30)` raised `TypeError`) -> `impact_soft` -8 with cue-level `dur=0.25`, `align='start'`.
    Re-measured: no violation, no ducking of the f0 hit; the 0.3 pause click stays the hook's sound event (ducked to -4).
  - Fix 2 (§5 rows 24a/24b/25, §7.1 S2-04, §7.3 P8, §7.5, §10 C3, §15 C1): push toward the portal from 14.6 (rate ramp 1 -> 4.5
    %/s over 14.6-14.9, ~6 % closer by 16.0), rack to pane 03 over 15.0-15.8 with aperture 900 (the gate's ~200 measured <= 2.2
    px CoC at gap 30: invisible), camera static from 16.0 as C3's scene A. Re-measured with `camspec.py`: C3 `center`
    (711.4, 1253.9) -> (719.4, 1267.5), disc r 36.5 -> 38.2, `r0` = 41.0 (disc + 2.8 px; at 38.2 the disc's rim showed as a
    growing orange ring, seen in the previs). Caption C1 re-solved against the moving frame top (`stack_rect` avoid): clear on
    three VO timings. No layer animates.
  - Fix 3 (§2 IG-2, §5 row 38a, §6.3, §7.2 layer 03, §16, §18): 2-frame glint of the hidden JD in layer 03 at f846-f847 (x0.35 ->
    1.20 -> 0.70 -> 0.35), no SFX; previs +18.7 -> +42.3 code values. Comment prompt pinned at posting and moved to caption
    line 2; the 24 h answer is pinned too and points at the glint.
  - Fix 4 brief sync (§2, §5, §9, §15, SLATE-change row 1): the script-gated lines (V2 "Lekin is ek frame mein...", V8 "ke", V9
    "Keemat...", V10 with a comma), the scriptwriter's timings (V3 per word from 6.00, V4 10.03, V7 18.90, V9 "banane" 27.70,
    V10 29.60), 62 words; caption chunks C1 `Aur ek *layer*...` / `jiske bina` / `frame *zinda*` / `nahi lagta`, C2 `Ek second
    mein` / `*30* frames` / `Yaani har second...`, C3 `Aur *awaaz* ke` / `3 tracks`; all three re-verified with the solver.
  - Fix 5 (§2 E-1, §5 rows 40-41, §6.3, §8, §9, §16, §17.2, §20 Q6; SLATE-change row 8): card `USKO YEH` (455.5 px, fits; hold
    1.99 s unchanged) and V10 `usko` / उसको, **pending the lead's OK**; full fallback written out.
  - Sync, no design change: the C3 plan cues as `jawad_tx` emits them today (`reverse_swell` -3 ending 16.733, `air_zoom` -6,
    `impact_soft` -1); the SFX helpers are `SJ.fit_under_vo` / `SJ.glass_truth` / `SJ.ember_slam` from `sfx_jawad` (r1 wrote
    `J.`, which has no such attributes); tag 12's drift under the push (§8); the §17 self-test and still lists; the §19 work
    orders; a bare `|∇alpha|` that split a §6.1 table row is now in backticks.
- **r1 (2026-10-08, creative-director):** first brief from SLATE §3.3.
