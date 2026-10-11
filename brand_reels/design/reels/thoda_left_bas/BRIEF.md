# BRIEF · Bijli series #2 · Thoda Left... Bas Bas! (`thoda_left_bas`)

r1, 2026-10-11. Pre-production team: content strategist (viral-strategist + trend-researcher), script writer
(hinglish-scriptwriter + script-hook-writer), creative director. Binding: `brand_reels/design/BIJLI_SERIES.md`
(hard rules, format), then this folder: **BRIEF.md** (strategy, look, grid) · **SCRIPT.md / script.json** (every
on-screen word, frame timings, optional VO) · **SHOTS.md** (shot list in frames + the BLENDER / SOUND / UI-TYPE
handoffs). If they disagree: SCRIPT owns words, SHOTS owns frames and assets, BRIEF owns everything else.
Reference build copied for patterns only: `bijli_chali_gayi` (BRIEF r2, packet, script.json, SOUND, module docstring).
Notation: `f` = frame at 30 fps; 100 BPM = **18 f per beat, 72 f per bar** (fully frame-locked, `X.Grid(100)`).

## 0. Deliverables

| item | value |
|---|---|
| format | 1080x1920, 30 fps, **DUR = 1008 f = 33.600 s** (14 bars at 100 BPM) |
| versions | **A** public (hook A: snowy CRT). **B** Trial Reel (hook B: client chat first), frame-identical from the **splice f72** (bar 1); hook B renders f0-f71 only |
| voice | **text-led, no VO in the delivered cut** (series rule: paid VO not approved). Optional VO lines are in SCRIPT §4 (Roman + Devanagari); the mix keeps a 1-4 kHz pocket for them |
| audio | original music on the 100 BPM grid + SFX (+ signal-driven TV static); `_ig.mp4` (music + SFX) and `_ig_songready.mp4` (SFX only) |
| loudness | -14 LUFS integrated ±0.5, TP ≤ -2.0 dBTP wav, ≤ -1.5 dBTP after AAC |
| delivery | `reel/jawad_reels/thoda_left_bas/` per `tools/deliver_reel.py`: `_ig.mp4`, `_ig_songready.mp4`, `_master.mp4`, stems, `_cover.jpg`, `_cover_grid_3x4.jpg`, `_caption.txt`, `.srt`, README.md; every file < 95 MB |
| no-go | no Jawad face / character sheet / JD profile shot anywhere (the profile-photo badge inside `profile_outro.py` is the only photo); no humans at all; no paid generation; no Organic Fostering / Floret look, prop or copy |

## 1. Strategy (content strategist)

**The moment.** Sunday afternoon, 90s/2000s: one person on the roof twists the GI-pipe antenna mast, another
downstairs shouts at a snowy CRT: "thoda left... thoda right... BAS BAS! ab theek hai!" The picture locks, and the
wind turns the antenna again. Every Pakistani and Indian household over ~25 lived it (the antenna, the doily on the
TV, "kiska left?"). It is border-neutral, apolitical, no cricket teams, no channel logos.

**The twist.** Twenty years later the editor hears the exact same dialogue from the client: "thoda left... thoda
right... nahi, pehle wala" while a title moves 2 px on a timeline from v1 to `v27_final_FINAL.mp4`. Payoff:
**"Hum aaj bhi *antenna* ghuma rahe hain."** The joke never closes: the outro hands straight back to "thoda left..."
at f0 (the feedback loop is the reel's loop).

**Send sentence.** "A 25-40 year old desi sends it to the sibling or cousin who was always sent up to the roof
('yeh tum the'); an editor or designer sends it to another editor, or to the client, because the client is the guy
downstairs." Triggers: identity + nostalgia (primary), amusement (the 'kiska left?' gag, the 1:1 dialogue match),
social currency for creators. Saves are secondary (re-watch for the TAB / AB split).

**Hook (muted-proof, 0-1.5 s).** Frame 0 is already bright and moving: a snowy CRT macro with a ghost picture sliding
sideways and the house lockup `THODA *left*...` mid-rise; the keyword flips to `*right*...` on f18 as the picture
slides back; `BAS BAS!` slams on f36 and the picture snaps clean. Three shouts everyone can hear in their head, no
sound needed. Forward open loop: on f63 the antenna slips again and a modern chat bubble ("Client: thoda left...")
pops into the 90s frame for 9 frames (anachronism, answered at f468). Hook scores (viral-strategist rubric, 0-2):
A = Gap 2, Specificity 2, Truth pass, Fit 2, Voice 2, Pull pass. Hook B (Trial Reel) = result first: the client's
"thoda left..." bubble + a 2 px nudge + `YEH FEEDBACK / *suna suna* / lagta hai?`, then the roof.

**Retention map (compressed; frames).**
| window | picture change | new information | open loop | risk / fix |
|---|---|---|---|---|
| 0-71 | snow, slide, lock, slip, bubble | the shout, the lock | why a client bubble in 1998? | 4 text states in 2.4 s: familiar chant, single keyword swaps, OK |
| 72-179 | rooftop, antenna jerks wrong way | two voices (roof big, downstairs small) | "kiska left?!" gag f162 | none: motion every 18-36 f |
| 198-305 | CRT room, clamp macro clicks on 8ths | chalk mark on the pipe = "sahi jagah" | will it lock? | none |
| 306-431 | lock + TV sting, wind, snow, big swing | "phir se?!", "YEH SCENE khatam nahi hua..." | bridge to now | none |
| **432-503 re-hook (45 %)** | M3 into a glass timeline, `20 SAAL BAAD`, ping f468, 2 px nudge | the client = the guy downstairs | closed the f63 bubble loop | none |
| 504-647 | phone macro, revision avalanche, TAB/AB split in sync | same words, both eras | how does it end? | split must read at 360 px (SHOTS UI §c) |
| 648-719 | client "BAS BAS!" = the TV lock sound, export v27 | final X = 538 = v2 (easter egg) | | |
| 720-755 | sunset roof, **drop-out f738-755** | | | |
| **756 payoff (75 %)** | `HUM AAJ BHI / *antenna* / ghuma rahe hain.` | the identity line | | hold 3.0 s |
| 864-1007 | CRT world dimmed, profile outro f882, bubble f990 | comment prompt | loop: "thoda left..." again at f0 | |

Rewatch triggers: the TAB/AB split (bar 8), the approved X 538 equals v2 in the revision list, the antenna nudging
2° by itself under the payoff (f828), the anachronism bubble at f63 / f990.

**Comment bait.** Outro question **"Aap ke ghar antenna kaun ghumata tha?"** with the keyword line
**"Papa, bhai ya aap?"** (a three-way choice: the lowest-friction comment; "Papa" works on both sides of the border).
Pinned comment: "Usse tag karo jo chhat pe jaata tha." Secondary debate the reel plants: "kiska left?".

**Caption (IG, first line ≤ 125 chars):** `Thoda left... thoda right... BAS BAS! Bachpan mein antenna, ab client. Video editing life.`
(92 chars) · context line: "Har editor ka client wahi neeche wala hai jo TV ke saamne khara hota tha." · 5 hashtags:
`#videoediting #editorlife #90skids #desinostalgia #motiongraphics` · "Turn on AI info": per the deliver convention
(no AI voice or AI imagery of a person in this reel; the lead decides the toggle).

**Trend check (no new web research; baseline in `trend-researcher.md`, as of Oct 2026, mostly vendor sources):**
text-led kinetic type locked to the beat and restrained 3D are the current recommendation; match cuts rising,
"every cut on a spike" templated (we use 3 match transitions and plain beat cuts); DM sends lead ranking (secondhand).
Re-check after 2027-01-11.

## 2. Look and world (creative director)

- **LOOK = `gold_hour`** (`jawad_grade.LOOKS`): brown-black floor, gold/amber horizon glow + god rays, softer
  contrast, grain 0.018 / 1.6 px. Why: the memory is a golden Sunday afternoon on a roof; the payoff is a sunset
  silhouette of the antenna; Bijli used `dusk` (night), so the series stays apart. `rays_center` per shot: rooftop
  day (0.30, 0.42), sunset (0.55, 0.62), CRT room window (0.08, 0.30); rays 0 on UI shots (S7-S11 except the split's
  top half). Only post call: `G.tx_finish(cv, t, 'gold_hour', cuts=CUTS, **PLAN.post_kw(t))`. Note: `gold_hour` was
  also the look of the earlier set's `beta_tum_karte_kya_ho`; the world here (rooftop, CRT, antenna) is unrelated.
- **Palette in picture:** sun / rays / sky glow GOLD-AMBER, rims and UI edges FLAME, snow is warm ivory (never pure
  white, never full-frame: always inside the CRT glass), edit-suite UI on SMOKE glass, 70-85 % of each frame dark
  warm. Red-orange ≥ 60 % of saturated px (budget 'share').
- **Signature device: the signal grammar.** One function `sig(t)` (0 = locked, 1 = no signal) from the antenna yaw
  error drives *everything*: CRT snow amount, the ghost offset and horizontal roll of the TV picture, the static bed
  gain, the music's band-limit filter (lo-fi when off, full-range when locked), and a faint ghost-double on the
  near-voice keyword while `sig > 0.3`. In the edit world the same grammar runs on the client's mood: the title in
  the viewer carries the ghost-double until "BAS BAS!", and the lock uses the identical `tv_lock` sound (the rhyme).
- **Two-voice caption grammar (no humans):** the voice *near* the camera = the house lockup, big, top band
  (y 300-650); the voice *far away* = small `jw_caps` 64 px ASH with a 2-step echo, entering from the edge it comes
  from (the downstairs voice rises y 1480 → 1420 in rooftop shots; nobody is ever shown). The client speaks only in UI
  (chat bubbles, toasts), never in house type, until the payoff.
- **Transition family: match** (M3 ★ f432 and f864, M2 f720); everything else is beat cuts + L3 push (glue). Max 3
  feature transitions, none premium, ≥ 2 bars apart. Camera language: locked macro for the CRT, low-angle handheld
  drift for the roof (amp 3 px), locked 2.5D push for UI.
- **Realism (Jawad 2026-10-11):** every 3D element is a photoreal PBR render tied to the story (aged aluminium, GI
  pipe rust, weathered plaster, curved CRT glass, wood-grain vinyl, worn knobs), shot as a few high-detail heroes in
  macro / close-up with real DOF rather than many simple props. Full spec: SHOTS §a.

## 3. Grid (100 BPM, 18 f / beat, 72 f / bar; total 1008 f)

| bar | f | section | key frames |
|---|---|---|---|
| 0 | 0-71 | HOOK (A CRT / B chat), splice f72 | f18 keyword flip · **f36 BAS BAS! lock** · f63 slip + bubble |
| 1 | 72-143 | roof: "Aaya?" / far "NAHI! THODA LEFT..." | f108 antenna jerks the wrong way |
| 2 | 144-215 | f135 far "ULTA! DOOSRA LEFT!" · f162 "*kiska* left?!" · f198 CRT room "thoda *aur*..." | f214 overshoot (snow) |
| 3 | 216-287 | f225 "NAHI NAHI, *wapas*!" · f252 clamp macro, ticks on 8ths, far "HAAN... HAAN..." | |
| 4 | 288-359 | f288 chalk marks align "BAS! BAS!" · **f306 lock + TV sting** · f342 wind | |
| 5 | 360-431 | "ARRE, *phir se*?!" · f378 roof "YEH SCENE *khatam* nahi hua..." | f414 big swing |
| 6 | 432-503 | **M3 f432 → timeline, `20 SAAL BAAD`, ping f468 (re-hook 46 %)**, nudge f477, phone f486 | |
| 7 | 504-575 | "nahi, pehle wala" f504 · revision avalanche on 8ths f522 · "DIALOGUE *wahi* hai." f540 | |
| 8 | 576-647 | TAB / AB split, sync moves on beats f576 / 594 / 612 / 630 | |
| 9 | 648-719 | **client "BAS BAS!" f648 = tv_lock** · export v27 f684 · "27 *revision* baad..." | |
| 10 | 720-791 | M2 f720 → sunset roof · **drop-out f738-755** · **PAYOFF f756 (75.0 %)** | |
| 11 | 792-863 | payoff hold, antenna nudges 2° f828, lockup out f846-863 | |
| 12 | 864-935 | M3 f864 → CRT (frame-0 world), **profile outro f882** (beat 49) | |
| 13 | 936-1007 | outro hold, bubble + ping f990, exit f996-1007, loop seam → f0 | |

## 4. Outro

`PO.ProfileOutro('Aap ke ghar antenna kaun ghumata tha?', key='Papa, bhai ya aap?', dur=4.2)`, `T_END = 882 / 30`
(literal frame, as Bijli's SHARED_REQUESTS #2). Settled +2.0 s (f942), hold 1.84 s (≥ 1.5), exit f996-1007 into the
loop push `cuts=[(0.0, 0.6)]`. World under it: the frame-0 CRT macro on the `t - DUR` clock, dimmed by the card
(dim 0.74). Its cues come from `card.cues(T_END, DUR)`.

## 5. Cover

Dedicated still (not a video frame): CRT macro, the screen **half snow / half locked** split by a rolling horizontal
tear at y ≈ 1010, the locked half showing the `SUNDAY KI FILM` card; lockup above `THODA` (caps 96, y 360) /
`*left*...` (key 250, y 540) with the underline; `BAS BAS!` (jw_caps_bold 150, y 1500) below the TV; the small client
bubble "thoda left..." at (790, 300) as the twist tease; `@jawad_mp4` signature y 1580. Everything inside the 3:4
grid crop (y 240-1680); readable at 210 px wide. Grid crop file = the same still cropped y 240-1680.

## 6. Engineering contract (motion-timeline-builder)

Module `pipeline/jawad_reels/thoda_left_bas.py` (+ `thoda_left_bas_world.py` for the 3D composites, `_ui.py` for the
glass UI, `_sfx.py`, `_music.py`; 3D builder `assets3d_thoda_left_bas.py`, outputs `RWS/assets3d/`, `RWS =
workspace/jawad_reels/thoda_left_bas`). `DUR, LOOK, BPM = 1008 / 30, 'gold_hour', 100`; `assets()`, `prewarm()`,
pure `draw(t)`, `post(cv, t)` → `G.tx_finish`, `samples(t)` → `PLAN.samples`, `cues()` → `thoda_left_bas_sfx.cues()`.
`PLAN = X.Plan([('M3', 432/30, dict(move=TRACK_432)), ('M2', 720/30), ('M3', 864/30, dict(move=TRACK_864))])`;
`CUTS = [(0, .6), (72/30, .5), (198/30, .3), (306/30, .6), (486/30, .3), (648/30, .5)]`. Env: `TLB_HOOK=A|B`,
`TLB_COVER=1`. Heavy jobs only through `tools/heavy.sh`, `render.py --workers 1`.

## 7. Open questions (for the lead; none blocks pre-production)

1. **Overlap with `pehle_wala` (earlier set):** that reel already uses v1 → v27 revisions and the payoff "Pehle wala
   hi theek tha". Here "nahi, pehle wala" is only one client bubble among four, the payoff is the antenna line, the
   approval gag is X 538 (not "v1 approved"), and no Ctrl+Z / pin markers are used. Lead OK, or swap the bubble to
   "nahi, wapas wala" and the filename to `v27_final_FINAL` only (kept, as the coordinator specified).
2. **Look collision:** `sirf_36_shots` (#3) also drafted `gold_hour` (its alternate `ember` is taken by
   `pencil_se_rewind`). Families do not collide (#1 editor, #2 match, #3 camera). Proposal: #2 keeps `gold_hour` (a
   literal sunlit roof + sunset payoff); #3 takes `noir_ember` (the darkroom red safelight is its natural practical).
   If the lead gives `gold_hour` to #3, this reel's fallback is `inferno` with rays added in 2D on the roof shots
   (S2, S6, S12) and the sunset kept amber; nothing else in these docs changes.
3. `20 SAAL BAAD` is a story time jump (no claim about Jawad); `TAB / AB` chips avoid real years on purpose.
4. AI-info toggle at upload (no AI imagery of a person, no AI voice in the delivered cut).
