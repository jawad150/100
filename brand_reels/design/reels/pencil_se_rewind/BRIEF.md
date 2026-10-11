# BRIEF · Bijli series #1 · Pencil Se Rewind (@jawad_mp4)

Version 1, 2026-10-11. Pre-production (content strategist + script writer + creative director). Binding: 
`brand_reels/design/BIJLI_SERIES.md` (hard rules, format), `pipeline/jawad_reels/BRAND.md`, the
`jawad-brand-reels` skill. Companion files here: **SCRIPT.md / script.json** (every on-screen line in frames, optional
VO), **SHOTS.md** (shot list + the three hand-offs: Blender props, sound, UI/type).

Notation: `f` = frame at 30 fps. **112.5 BPM = 16 f per beat, 64 f per bar** (frame-locked, `X.Grid(112.5)`).
Bar n starts at f 64n. `RWS` = `workspace/jawad_reels/pencil_se_rewind`.

## 0. Deliverable

| item | value |
|---|---|
| format | 1080x1920, 30 fps, **DUR = 1024 f = 34.133 s** (16 bars) |
| module | `pipeline/jawad_reels/pencil_se_rewind.py` (+ `_world.py`, `_sfx.py`, `_music.py`); 3D: `assets3d_pencil_se_rewind.py` |
| contract | `DUR, LOOK, BPM = 1024 / 30, 'ember', 112.5`; `assets()`, `prewarm()`, pure `draw(t)`, `post(cv, t)` -> `G.tx_finish(cv, t, LOOK, cuts=CUTS, **PLAN.post_kw(t))`, `samples(t)`, `cues() = []` (stems muxed with `--audio`, render `--no-sfx-build`) |
| audio | original music on the grid + SFX; `_ig.mp4` (music + SFX), `_ig_songready.mp4` (SFX only); VO is an optional later layer (credits not approved) |
| delivery | `reel/jawad_reels/pencil_se_rewind/` per `tools/deliver_reel.py` (series format list) |
| no-go | no Jawad face, character sheet or JD profile shot (the profile-photo badge inside `profile_outro.py` is the only photo); **no humans or hands** (objects move by themselves); no paid generation; no brand names or logos on any prop (no Sony / TDK / Natraj / Reynolds marks); nothing from Organic Fostering / Floret |

## 1. Strategy (content strategist: viral-strategist + trend-researcher)

**Concept.** The 90s / 2000s desi kid rewound cassettes with a pencil in the sprocket to save the walkman battery,
hunted for a song "by andaza" (rewind, play, wrong spot, again), and rescued chewed tape with the same pencil.
Twist: that was our first scrub. Today the playhead does it. Payoff: **"Pehla editing tool? Pencil."**

**Hook structure (the callback).** The hook and the payoff share one lockup shape: `REWIND BUTTON? / *Pencil.*`
(f0) and `PEHLA EDITING TOOL? / *Pencil.*` (f768). The audience hears the joke twice, the second time it lands on
the editor, and the shape makes the loop feel designed.

**Send sentence.** A 25-38 year old Pakistani or Indian viewer sends it to the sibling or cousin they shared a walkman
with ("yeh tu karta tha"); editors and creators send it to editor friends ("pehla scrub tool, lol"). Two audiences,
one object: nostalgia gives reach, the editor twist gives Jawad's niche a reason to follow.

**Why saved / shared.** Shared: identity + amusement ("yeh hamara bachpan"), cross-border (the cassette, pencil and
walkman are the same on both sides; no film or team names on screen). Saved: weaker by nature; the cover (pencil in a
cassette) is a collectible "90s object" frame, and the payoff line is a quotable for editors.

**Comment bait.** (1) the outro asks for their first cassette (people name albums and soundtracks: specific, warm,
long comments); (2) the key line **"Pencil ya pen?"** starts a low-friction debate (many used a hex ballpoint: free
replies); (3) easter egg: a tooth-dented AA battery beside the walkman in S2 ("battery chaba ke chalate the" comments).

**Concept scores (viral-strategist §1, 0-10).** Hook 8 (instant object recognition muted + a 2-word answer) · 
Relatability 9 · Share trigger 8 (identity + amusement) · Novelty 7 (series format, new object, editor-native reveal) ·
Truth PASS (no claim about Jawad; a shared childhood habit) · Loop 8 (outro world = frame 0, rotation loop divides DUR) ·
Feasibility 8 (6 hero renders, CPU budget in SHOTS §A) · Brand 8. Gates met.

**Retention map (per bar; change every <= 2.13 s, new info every <= 4.3 s).**

| bar | f | picture change | new info / loop state | risk + mitigation |
|---|---|---|---|---|
| 0 | 0-63 | macro: pencil spinning in the cassette hub, already lit at f0 | hook: "Rewind button? Pencil." Open loop: why is an editor showing this? | none: lit, moving, text at f0 |
| 1 | 64-127 | walkman + orange-foam headphones + batteries | why: save the battery | easter egg (bitten battery) |
| 2 | 128-191 | hub close-up, tape moving in the window | "pencil se ghumate the" | |
| 3 | 192-255 | handwritten label "Mix '98 · Side A" | new goal: find the song | |
| 4 | 256-319 | D8 speed-ramp into a fast rewind | "Sirf andaza." | |
| 5 | 320-383 | walkman keys clack by themselves | Play / Galat! / Phir se. (8th-note build) | rewatch beat |
| 6 | 384-447 | walkman playing, spools turning | "Mil gaya!" then "Aur phir..." (tease) | |
| 7 | 448-511 | **RE-HOOK (f464 = 45.3 %)**: walkman eats the tape, lid pops, ribbon spills | "Cassette phans gayi!" stakes peak | loudest stress point |
| 8 | 512-575 | rescue: pencil winds the crinkled loop back | "Saans rok ke, pencil se wapas." | hushed sound keeps tension |
| 9 | 576-639 | **reveal**: camera pulls back, the cassette is a clip in a glass NLE viewer | "Aaj bhi wahi karte hain." loop half-closed | |
| 10 | 640-703 | playhead scrubs on 8ths, viewer scrubs the cassette | Peeche. Aage. Peeche. Yahan. | rewatch beat |
| 11 | 704-767 | timeline close; drop-out f752-f767, the playhead becomes the pencil | "Bas tool badal gaya." | 0.53 s of silence is designed |
| 12-13 | 768-895 | **PAYOFF (f768 = 75.0 %)** lockup over the timeline, pencil snaps to a cut f800 | "Pehla editing tool? Pencil." + tag | |
| 14-15 | 896-1023 | D2 razor cut to the frame-0 macro world, profile outro | question + "Pencil ya pen?"; loop to f0 | outro settled hold 1.9 s |

Rewatch triggers: the 8th-note "Play / Galat / Phir se" and "Peeche / Aage" builds; the viewer in S10 scrubs the
reel's own frame-0 shot; the NLE timecode equals the reel's real timecode; the bitten battery.

**Caption (IG, first line <= 125 chars):** `Rewind button tha, par battery bachani thi. Pehla scrub tool? Pencil. #videoediting`
(84 chars). Hashtags (5): `#videoediting #editorlife #90skids #cassette #nostalgia`. Pinned comment: `Pencil ya pen? Sach batana.`
AI info: 3D renders of objects only, no person, no AI voice (text-led) -> AI label not required; if a TTS / AI VO is
added later, turn on "AI info" (open question for the lead).

## 2. Look and world (creative director)

- **LOOK = `ember`** (kit look via `jawad_grade.FIN['ember']`): warm near-black void, flame key, gold-white cores,
  grain 0.016. Chosen because the series siblings use `dusk` (Bijli) and `gold_hour` (thoda_left_bas). Post =
  `G.tx_finish(..., 'ember', cuts=CUTS, **PLAN.post_kw(t))` only.
- **World:** a 90s homework desk at night. One practical: a tungsten desk lamp (warm, top-left, off-frame) making a
  hot pool on worn sheesham-veneer wood; everything outside the pool falls to NIGHT_0. FLAME rim from back-right on
  every prop (house rim light). Realism carries the reel: few hero props, shot macro with real depth of field.
- **Palette in picture:** chocolate-brown tape, smoked-amber cassette shell, chrome-yellow pencil leaning orange
  (`#E3A21A`), **orange foam headphone pads** (on-brand FLAME accent), brushed-aluminium walkman lid. Hue budget
  ('share': red-orange >= 60 % of saturated px): the yellow pencil is the risk; the colorist checks `G.verify` on
  S1 / S3 / S12 and may pull the pencil hue toward 38-40 deg.
- **Signature device: the pencil is the playhead.** The hex pencil appears as the reel's scrub tool in the cassette,
  then literally replaces the NLE playhead (f752-f800). Not used by any earlier reel.
- **Transition family: editor** (siblings: Bijli = light, thoda_left_bas = match). Features: **D8** speed-ramp f256,
  **D7** RGB shock f464 (in-scene, the tape-eat), **D2** razor f896 (into the outro). The f576 reveal is an
  in-scene pull-back that reuses D1's NLE chrome (`X._nle_bg`, `X._nle_timeline`), not a catalogue window.
  Everything else = beat cuts + **L3** exposure push. Never two features within 2 bars (f256 / f464 / f896).
- **Camera language:** macro 100 mm slow pushes (2.5D zoom on the rendered plates, 1.00 -> 1.06), locked shots for the
  keys (things move by themselves), one big pull-back (f576), a push into the timeline (f704-f767).

## 3. Grid (112.5 BPM, 16 f / beat, 64 f / bar; total 1024 f)

| bar | f | section |
|---|---|---|
| 0 | 0 | HOOK A (B = trial, f0-f63 only, splice at f64) |
| 1-3 | 64 / 128 / 192 | turn: battery, pencil, the hunt for the song |
| 4 | 256 | D8 speed-ramp, "Sirf andaza." |
| 5-6 | 320 / 384 | the play / wrong / again build, "Mil gaya!", tease |
| 7 | 448 | **RE-HOOK**: tape eaten, slam f464 (45.3 %) |
| 8 | 512 | rescue |
| 9 | 576 | reveal pull-back into the NLE |
| 10-11 | 640 / 704 | scrub build; drop-out f752-f767 |
| 12-13 | 768 / 832 | **PAYOFF f768 (75.0 %)**, snap f800, tag |
| 14-15 | 896 / 960 | D2 razor, **profile outro** f896-f1023, loop seam f1023 -> f0 |

`CUTS = [(0.0, 0.6), (64/30, 0.5), (128/30, 0.25), (192/30, 0.3), (320/30, 0.4), (384/30, 0.3), (448/30, 0.5), (512/30, 0.2), (768/30, 0.6)]`
`PLAN = X.Plan([('D8', 256/30), ('D2', 896/30)])`; D7 is applied in-scene via `X.TX['D7'].post_kw(t, 464/30)` merged into post.

## 4. Outro

`card = PO.ProfileOutro('Aap ki pehli cassette kaunsi thi?', key='Pencil ya pen?', dur=128/30)` with
`T_END = 896/30` (literal frame, SHARED_REQUESTS #2 of Bijli). Settled at f956, hold 1.9 s, exit 0.36 s into the
loop push. World under it: the frame-0 macro (pencil spinning in the hub, R1 loop, one revolution per beat), dimmed
by the card (dim 0.74). Reserve question if the lead prefers one line: `Pencil se rewind kiya hai kabhi?`.

## 5. Cover

Dedicated still: R1 frame 0 rendered at full 1080x1920 (128 spp) + hook lockup `REWIND BUTTON? / *Pencil.*` at full
opacity with the underline settled. Grid crop 3:4 (y 240-1680) holds the lockup (y 340-720) and the hub/pencil
(y 820-1420). Keyword 250 px reads ~49 px tall at 210 px thumbnail width. Alternate cover (test later): the payoff
frame f810 (pencil as playhead).

## 6. Open questions (none blocks pre-production)

1. Lead: confirm `ember` + editor family + 112.5 BPM against series reel #3 (`sirf_36_shots`).
2. "Pencil ya pen?" as the outro key line (vs a single-question outro).
3. If a VO is approved later: the voice, and the AI-info toggle.
