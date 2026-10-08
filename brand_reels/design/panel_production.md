# Concept panel, judge 3 of 3: production feasibility and finish quality

Date: 2026-10-08 · Role: reels-studio motion-timeline-builder (the person who has to build and render these today) ·
Client: Jawad (@jawad_mp4, "JD")

Inputs read: `.claude/agents/motion-timeline-builder.md`, `workspace/brand_reels/wf/ctx.txt`, the `jawad-brand-reels`
skill, `pipeline/jawad_reels/TOOLKIT.md`, `jawad_kit.py`, `jawad_grade.py` and `jawad_tx.py` docstrings,
`vo_config.json`, `.claude/agents/face-compositor.md` and `blender-3d-artist.md`, `brand_reels/research/studio_setup.md`,
`sound_design.md` (SFX catalogue and music-bed section), `cinematic_casebook_concepts.md` sections 4-6 (all 25 cards),
the character-sheet contact sheet and the face test board, and the five look charts. The Director's memo
(`panel_director.md`) was read only for its N01 card, so this panel can give a production read on it.

---------------------------------------------------------------------------------------------------------------

## 0. Verdict: the slate I can ship today with zero mistakes

| # | reel | look | transition family | signature device | Blender jobs | est. master (1 worker) | buildability /100 |
|---|---|---|---|---|---|---|---|
| 1 | **C08 Ek Frame ki Keemat** | `ember` | camera (C3 portal push, C6 rack-focus, C8 snap) | exploded frame: the frame's real compositing layers pulled apart in 3D | 0 | 35-45 min (heaviest) | **86** |
| 2 | **C09 Client is typing...** | `inferno` | match (M1 circle match on the dots, M3 momentum, M6 carry-over) | UI as monster: three typing dots that breathe and throw red light | 0 | ~22 min | **84** |
| 3 | **C11 Bijli Chali Gayi** | `dusk` | light (L7 beam sweep, L8 iris, L4 bloom-out, L3 push) | power-cut grammar: the reel obeys electricity | 7-8 static renders | 25-30 min | **78** |
| 4 | **C01 J · K · L** | `noir_ember` | editor (D1 scrub, D8 speed ramp, D9 rewind) | shuttle-speed world: the world's clock obeys the key pressed | 4 (3 keycaps + 1 keyboard plate) | 20-25 min | **87** |
| 5 | **C19 Kal se pakka** | `gold_hour` | type (Y1 zoom through a serif counter as the Droste engine, Y3 slam, Y5 underline) | Droste calendar that never reaches tomorrow, broken by a tear | 1 (desk calendar) | 20-23 min | **82** |

- Five worlds (glass void, red horror void, a dark desi home by torchlight, a macro keyboard landscape, a paper
  calendar at sunrise), five looks, five transition families (organic stays unused), five signature devices,
  five hook mechanisms (number, question, pattern interrupt, bold claim, self-call-out), five different sends.
- Average buildability 83. All five run on toolkit pieces that are already built and tested: house type, glass
  UI, counters, embers, 2.5D cut-outs with rim light, the colorist's five looks and the transition kit. Two
  reels need no Blender at all. Every music bed can come from sound design (pulses, drones, pads), the part of
  `epic_music.py` that synthesises well. None of them needs a whisper, melodrama or an intimate confession from
  the TTS voice.
- Total render: about 2-2.5 h of one worker for the five masters, or about 1.1-1.3 h on two. Blender: about 12-13
  static Cycles jobs, 45-70 min on one 2-thread slot, running while the timelines are built on stand-ins.
- **What this slate gives up:** a family or tenderness reel. The production-safe heart swap is the Director's N01
  (section 5), but only if its cooker whistle passes a blind listen. Otherwise use C02 in POV framing.

Swap-ins in order: **C24 Do JD** for C09 (76, if the lead wants both wardrobes on screen), **C15 Log Kya Kahenge** for C01
(72, only after its one-shot gate in section 4.4), **N01 Ek Awaaz** for C19 (74, gated on sound), **C05 Render 99%**
(80, only if C08 is dropped, because the two would look like the same glass world).

---------------------------------------------------------------------------------------------------------------

## 1. How I scored

**Buildability-at-premium (/100)** answers one question: can this reel be finished today on this machine with
this kit at a finish that holds up beside the reference reels, with zero mistakes? It weighs:

| axis | weight | what costs points |
|---|---|---|
| Build load | 25 | new 3D props, new mini-styles, custom transitions not in `jawad_tx` (C4, C5, D5, D6, O3 and others are spec-only), sets that must look photoreal |
| Premium ceiling with this kit on CPU | 25 | worlds that need real geometry (rooms, landscapes, crowds in 3D) instead of light, glass, type and planes; hands or other people; walking or turning Jawad |
| Render cost | 15 | full-res plane stacks with DOF, split screens (two worlds per frame), 7-15 sample windows, animated Cycles sequences |
| Failure risk | 20 | uncanny faces (relighting, more than 3.5 s on one still, too many swaps), unreadable type (half-width splits, tilted mono), muddy grade, sync (music that must obey the picture), sound that *is* the content |
| Voice and truth fit | 15 | needs a raw, intimate or acted human voice (Vlad is a warm AI narrator); a private fact is the spine of the story and the universal reframe guts it; India-Pakistan sensitivities |

Virality is not my axis: the casebook's W scores and the Director's panel cover it. Where my slate differs from
theirs, I give the gate that would make their pick safe.

---------------------------------------------------------------------------------------------------------------

## 2. Measured evidence (today, shared box, `nice -n 10`, 1 process)

**Plane cost.** These drive the C08 and C05 budgets. Ember background with an orbit camera at aperture 34:

| test | time per sample |
|---|---|
| 14 full-res (1080x1920) planes with DOF | **4.97 s** (about 15 s/frame at 3 samples, so a 12 s fly-through would take about 90 min on its own) |
| 14 half-res (540x960) planes with DOF | 1.43 s |
| 8 half-res planes with DOF | 1.11 s |
| 14 half-res planes without DOF | 0.47 s |
| 10 crowd strips (2400x320) at stadium distance with DOF (C15) | 0.13 s (the crowd is cheap; its risk is artistic) |
| `K.background('ember')` | 39 ms |
| 300 embers | 4 ms |
| `G.finish` per look | ember 283, noir_ember 329, inferno 263, gold_hour 296, dusk 268 ms |

**Width of the hook lines.** `T.measure`, safe width 940 px:

| line | style, px | width | |
|---|---|---|---|
| Editing ke / *3 button* | jw_caps 86 / jw_key 210 | 471 / 618 | ok |
| Aap ne ise / *0.03 second* | 86 / 200 | 499 / 809 | ok |
| SAB SE / *darawni* | 86 / 220 | 314 / 695 | ok |
| BIJLI / *chali gayi* | 86 / 210 | 212 / 734 | ok |
| KAL SE / *pakka* | 86 / 230 | 302 / 543 | ok |
| Log kya / *kahenge?* | 86 / 210 | 365 / 702 | ok |
| client ke saamne vs 3 baje (C24) | jw_caps 60 | 896 | spans both halves of a split; it cannot sit in one half |
| final_FINAL_v7_REAL.mp4 (C09) | jw_mono 44 | 627 | ok, and still >= 40 px after a 10 % perspective loss |
| -1x  -2x  0x  2x  8x (C01 HUD) | jw_mono 56 | 693 | ok |
| Same shot. Teen kahaniyan. (C23) | jw_caps 70 | **1111** | over: two lines or 58 px |
| *1,024* (C08) | jw_key 240 | 423 | ok |

**Grade.** The look charts show two risks:
- Emissive FLAME above about 3x linear turns lemon-yellow, and RED above about 4x turns salmon-pink after the
  finish's blackbody roll-off.
- Cap the flame and red hero glows at about 3x. Get the "hot" feel from the AMBER/GOLD cores, not from pushing
  RED. This matters most for `inferno` (C09) and the power-on bloom in C11.

**Faces.**
- All 15 crops are flat, front-lit studio photos on grey. The 2x versions are 710-940 px wide; the full-body
  sources are 469-480 px wide, so faces on those are small.
- Rim plus a cinematic grade works on the test board (A_rim, D_cine).
- Hard side light (candle, monitor glow from one side) has to be faked with a soft gradient multiply and a warm
  rim. A 3D relight from the depth map is too risky for zero mistakes.

**Voice.**
- Vlad (elevenlabs_v4) measures 142.8 wpm, stretched to 155-165 wpm, with an f0 spread of 6.3 semitones: a
  warm, even narrator.
- At about 2.6 words/s, a 35 s reel holds about 75-85 words including its silences.
- 187 credits are left; five reels in per-beat takes with re-takes need about 50.

**Sound.**
- The audio.py library (45 sounds) plus `epic_sfx` (40 sounds) already covers horror, editor UI, clocks,
  rewinds, tape stops, risers, braams, real CC0 crowd cheers and rain.
- `epic_music.py` has four on-grid styles: `dark_pulse` 120, `desi_drill` 142, `lofi_desi` 84, `desi_epic` 100.
- Weakest areas: the synthetic `crowd_ooh`, plucked and bowed acoustic instruments (piano, cello, guitar,
  rubab, shehnai), and anything nobody has judged by ear yet.

---------------------------------------------------------------------------------------------------------------

## 3. Scoreboard: all 25 cards

"Build" = what has to be made. "Render" = master estimate on one worker (3 samples, 35 s). Truth = the lines
that still imply a private fact and the reframe they need.

| rank | id | concept | build | premium ceiling on this kit | render | main failure risks | truth / voice | **score** |
|---|---|---|---|---|---|---|---|---|
| 1 | C01 | J · K · L | 3 keycaps (black gloss, emissive legends; static renders, the press animated in 2D), 1 keyboard-macro plate, jw_mono HUD, glass light-streak cards; the world runs on a remapped clock w(t) (free, because draw(t) is pure); faces: street 3/4 with a directional smear, suit neutral, then smiling | very high: product-shot keycaps in noir, ember particles frozen and reversed | 20-25 min | the K dolly toward a still must stay within the face limits (push <= 8 %/s); J/K/L is abstract unless labelled in the first 3 s; synthetic piano (use EP/pad) | clean ("har editor"); warm narrator fits | **87** |
| 2 | C08 | Ek Frame ki Keemat | one hero frame built from real layers (bg, haze, rim-lit JD cut-out, keyword, glow, embers, UI), exploded into slabs; tags; pre-flattened stack sprite reused for the 30-stack corridor and the 1,024 skyline; reassembly slam; no Blender | very high: the set *is* the kit, and the cut-out is honestly a layer | 35-45 min **if** slabs are half-res and samples drop to 1-2 on slow moves (full-res would be about 90 min for the fly-through alone) | render budget; near-plane culling while flying through slabs; tags must hold >= 1 s at >= 40 px; a pause icon would echo C01's K | the card's minute tags ("rim light · 25 min") and "kai ghante" are invented hours: use layer names, the real layer count and the true arithmetic (30 frames per second, the reel's real frame count) | **86** |
| 3 | C09 | Client is typing... | red void, one glass chat window, the dots as a creature (local red radial light on the face), title cards, 3D wall file names, warm-light reveal; no Blender | high: dark plus one red source is forgiving; the duotone face test already reads | ~22 min | red-on-red copy (IVORY on RED is only 3.66:1); RED glow gain > 3x drifts salmon; flicker must only darken | POV, kind client, no amount, no app branding; Vlad cannot whisper, so use low suspense narration | **84** |
| 4 | C19 | Kal se pakka | 1 desk-calendar prop + a flat page sprite for the nested levels; Droste zoom (4-5 nested draws, exponential scale, seamless loop); T.Counter 1-365; custom paper tear (O3 is spec-only in jawad_tx) with an ember edge (O6 exists); AAJ sunrise | high: paper, ember edges and gold rays | 20-23 min | paper must look tactile (fibre texture, bevel, contact shadow), never clip-art; Droste seam; the tear sound must convince | clean (universal); avoid festival names (one-sided) | **82** |
| 5 | C05 | Render 99% | glass corridor bar, flame fill, readout, toasts, O4 shatter (exists) | high | ~30 min | fly-through plane cost (see C08); familiar metaphor; same glass world as C08 | "mera render wahin ka wahin" becomes "har editor ka" | **80** |
| 6 | C11 | Bijli Chali Gayi | lit desk-corner plate (lit and unlit passes), 5-6 static props each rendered under two light directions so the torch beam can move the lighting, beam mask plus haze cone (L7), CRT collapse, procedural candle, local power-on blooms (L4); Ctrl+S as a HUD, not keycaps | high: darkness hides set limits | 25-30 min | the most Blender work in the slate (start it first); designed blackout and flicker must never go white (YMIN rule) and text must land by 0.6 s; `dusk` violet shadows plus orange haze can go muddy brown; candle-side relight of a front-lit photo | "Phir main ne editing shuru ki" and "meri ungli" become "Phir editing aayi" and "har editor ki ungli"; load-shedding stays nostalgic, with no utility or government names | **78** |
| 7 | C24 | Do JD | mirrored split, revolving divider (planes), tabs, call UI, bubbles, chai, clock; 8-10 face swaps | high | ~30 min (two worlds per frame, about 1.6x) | half-width copy (~470 px); swap count; one narrator voicing both sides makes comic timing hard (bubbles must carry it muted) | clean ("har freelancer") | **76** |
| 8 | C03 | Rishtedaar Boss Fight | fighting-game HUD (bars, combo counter, ROUND/K.O.), fairy-light bokeh, 2D relative silhouettes | high for the HUD; the bokeh is a kit strength | ~20 min | HUD clutter and small type; silhouettes must carry no religion markers | "Abbu ne sirf ek sawaal poocha" becomes "phir ghar ka bara ek sawaal poochta hai"; seasonal | **74** |
| 9 | C06 | Views ginta raha, calls nahi | desk plate (lamp, phone), T.Counter odometer, toasts, light-meter HUD, one push | medium-high: restraint exposes every frame | ~20 min | the dimming lamp needs a face relight; a 30 s oner versus the 3.5 s-per-pose limit; a third dark room in a slate that has C09 and C11 | "Us raat main ne views band kiye... call wapas ki" needs POV; the counter must not imply his real views | **74** |
| 10 | N01 | Ek Awaaz (Director's) | glass console strips in perspective, 6 static props, steam, meters driven by the real SFX envelopes, JD profile and hand-on-chest | high visually | 22-25 min | the reel is only as good as six synthesised household sounds, so "ek bhi recording nahi" rules out the CC0 samples; the dark channel can read as bereavement | clean; the call home is never voiced, so the TTS is safe | **74** |
| 11 | C15 | Log Kya Kahenge | procedural silhouette strips (8-12 tier planes; measured cheap), floodlight rays, haze, a 3D type depth stack, small suit full-body in a spotlight, a custom orbit/crane (C5 is spec-only) with cardboard backs when a strip faces away, ember dissolve (O6) | high if the crowd design is good | 28-35 min | the whole reel rides on one reveal shot reading as "cardboard"; the crowd can look clip-art; the whisper wall (the synthetic crowd is mush; pitched real crowd samples are needed) | "Saalon tak main ne..." becomes "Hum saalon tak..." | **72** |
| 12 | C13 | Day 1 vs Day 1000 | split, comparison table, graph, kintsugi seam, a deliberately bad Day-1 edit | medium | ~22 min | half-width type; the "ugly" side must read as intended; showreel framing | day count symbolic; "main khud chilla deta tha" becomes "har editor" | **70** |
| 13 | C20 | Pause | chaos montage, frozen world, keycaps; drop the sculpted coffee splash | high for the freeze | ~22 min | duplicates C01's K freeze | burnout story and "neend · 4 ghante" tags are private stats: POV | **70** |
| 14 | C21 | Dear Algorithm | monolith (planes or one static), pre-folded paper-plane spin sequence, sticker peels, mono reply | high | ~22 min | the folding animation (skip it); filmi melodrama needs acting the TTS cannot give | "sirf do sau logon" is a reach claim, use "kuch logon"; the send CTA reads as engagement bait | **70** |
| 15 | C22 | Mera Laptop Bolta Hai | hero laptop modelled in bpy (1-2 h), dust, grille macro, box, shelf; headshots lit by screen glow | high (product-shot laptop; the most natural use of stills) | ~22 min | modelling time; no brand marks | "Main Jawad ka laptop hoon", "Paanch saal... teen baar gira" and "rakh liya" are his history; "ek editor ka laptop" loses the hook | **70** |
| 16 | C16 | Is reel ko scroll mat karna | whole-canvas dodge (spring), glowing thumb, countdown, a 3 a.m. suite set | medium | ~25 min (fast moves need 7-11 samples) | black frame edges on dodges; engagement-bait demotion | "teen din" claim | **68** |
| 17 | C02 | Beta, tum karte kya ho? | chat UI, three genre-parody mini-scenes (wedding VHS, cartoon, error), phone and chai props | medium: each parody is its own style | ~20 min | parody must look deliberately cheap inside a premium reel; Ammi's hands (drop them); synthetic shehnai | khala's forward and "ab woh sab ko samjhaati hain" are private: POV | **66** |
| 18 | C07 | Prompt: make a reel like @jawad_mp4 | prompt UI, a locally faked "AI version" (faceless: no smoothing his likeness), diff panel, glitch (D6 is spec-only) | medium | ~22 min | faking "AI gloss" without AI images; two synthetic scores | "3 saal ki mehnat" is his history; never claim a real model made it | **64** |
| 19 | C04 | Pehli Payment | banking card, time-dilation spinner, converter roll, 3 props; drop the hands | medium-high | ~20 min | currency exposes a country; no bank or app marks | **built on a banned private fact** (first payment, charger, borrowed wifi, family's verdict); the universal version loses its izzat payoff | **62** |
| 20 | C12 | 4:3 se 9:16 tak | 5 era mini-styles with invented "old edits", CRT and tower props, a score that "grows up" to orchestral | medium | ~22 min | five styles to build; synthetic orchestral | "mera pehla edit... purane computer pe", the cyber cafe | **60** |
| 21 | C14 | Dor | kite spin sequence, sky and rooftop layers, string = underline, hand-keyed kite physics; drop the hands on the spool | medium | ~25 min | acoustic rubab/guitar bed; string-injury sensitivity (Basant 2026); best posted in January | "Ammi ki duayein. Abbu ka 'soch lo beta'" implies his parents: "har ghar ki duayein" | **58** |
| 22 | C18 | Pehla Client, Pehla Dost | credits roll (easy), motorbike silhouette, chai glasses | medium | ~20 min | generic montage | **the whole story is a private fact**; the universal version loses the point | **58** |
| 23 | C23 | Ek Shot, Teen Kahaniyan | a corridor door shot (animated Cycles about 1-2 h, or a 2D light spill), waveform X-ray; JD cannot "turn" from a still | medium | ~22 min | three micro-scores are the content; synthetic piano and cello have never been judged by ear; one weak version breaks the experiment | clean | **55** |
| 24 | C17 | Editor ki Shayari | light-calligraphy strokes, slice cuts, dunes, chiragh (visually cheap) | medium-high | ~20 min | needs a native Urdu poet's review today; AI TTS cannot carry poetic cadence | clean but voice-bound | **48** |
| 25 | C10 | Unsent Voice Note | waveform terrain flyover (animated Cycles CPU = hours, or no real mesh renderer in the compositor), a full-body JD "walking" a ridge (impossible from a still) | low today | hours | the most expensive shot in the casebook | **father's wishes are a banned private fact**; an intimate letter in a synthetic voice | **38** |
| 26 | C25 | Bol ka Edit | song chosen on posting day, lyric rights | n/a | n/a | cannot be finished today; leaves the VO spine | n/a | **35** |

---------------------------------------------------------------------------------------------------------------

## 4. The slate, reel by reel (what to build, how it stays premium, how it fails)

### 4.1 C08 Ek Frame ki Keemat · `ember` · camera family · 86

- **Hook (0-2.5 s).** Picture: a finished house frame (rim-lit JD street_smirk cut-out, a flame keyword, embers,
  a small glass UI card) stops under a playhead marker `FRAME 0417` (not a pause icon: K belongs to C01), then
  cracks along its layer seams. Text `Aap ne ise / *0.03 second* dekha.` VO: "Yeh frame aap ne sirf 0.03 second
  dekha..."
- **Build.**
  - Build the hero frame once in `assets()` as named layers: bg, haze, god rays, cut-out torso, cut-out head,
    rim, keyword core, keyword halo, underline, embers, UI card, grain.
  - The explode puts each layer on a plane at its own z.
  - Slabs are half-res (540x960) except the one in focus.
  - At most 8 slabs with DOF are visible; the rest are drawn without DOF or culled.
  - The 30-stack corridor and the 1,024 skyline are billboards of ONE pre-flattened stack sprite.
- **Premium levers.** The camera arc uses easy_ease (C3 portal push between slabs, C6 rack-focus hand-offs). Each
  tag is a jw_mono label pinned to its slab with a thin flame leader line. The reassembly slam lands on a bar
  line with a local exposure push and no white flash.
- **Render budget.** Measured: 14 full-res DOF planes = 5 s per sample, so the fly-through must not use them.
  Plan 1-2 samples on slow moves and 5 only on the reassembly. That gives about 35-45 min. Render this master
  first or on the second worker.
- **Failure modes.**
  - Plane corners crossing the near plane mid-fly-through: keep the camera between slabs, never through a slab
    face unless C3 is the cut.
  - Tags unreadable while moving: hold each >= 1 s, >= 40 px after perspective.
  - Heavy grain on half-res slabs: the finish adds grain once over everything.
- **Truth fix.** No minute or hour tags. Tags carry layer names (`01 · andhera`, `02 · dhuaan`, `03 · roshni`,
  `04 · chehra` ...) and the real count of this frame's layers. Spoken arithmetic only where true: "Ek second
  mein tees frame" and the reel's real frame count (set DUR to make it exact, e.g. 34.133 s = 1,024 frames).
  "0.03 second" is 1/30 s rounded; fine.

### 4.2 C09 Client is typing... · `inferno` · match family · 84

- **Hook.** Picture: black void, one dark-glass chat window, three typing dots pulsing like a heartbeat, red light
  falling on JD (suit_shocked). Text `*Sab se darawni* / CHEEZ?` VO (low suspense narration, not a whisper):
  "Raat ke 11:58. File bhej di. Aur phir..."
- **Build (no Blender).**
  - Glass chat window from `ui` on the inferno glass look.
  - The dots are three emissive discs with breathing scale. Their light on the face is a local radial RED term
    added over the cut-out: no relight, which is why it is safe.
  - Horror title cards (`Music change kar do`, `Logo thora bara`, `Thora aur *pop* karo`) in jw_caps with a jw_key
    word.
  - File names as 3D wall text (`final.mp4`, `final_final.mp4`, `final_FINAL_v7_REAL.mp4`, 44 px mono).
  - Dutch angles: roll <= 2 degrees on face shots (face limits); stronger roll only on UI and type shots.
  - Reveal: the lights warm (exposure plus a warmer bloom on the window), JD swaps to suit_smiling on a hard cut.
- **Transitions.** M1 circle match (a dot becomes the next scene's circular light), M3 momentum cuts on the whips,
  M6 carry-over of a dot into the reveal. No flicker family (that belongs to C11).
- **Sound.** All in the library except one custom violin-like screech stinger (resonant noise sweep):
  tension_drone, heartbeat_build, notif_ping, typing, glitch_corrupt, braam, tape_stop.
- **Failure modes.**
  - Red-on-red copy: keep copy IVORY on near-black; RED only as light.
  - RED glow above about 3x turns salmon in the finish.
  - Black-frame jump scares: an exposure push on the next frame, never a white frame.
  - Three poses only (shocked, confused, smiling), each <= 3.5 s.
- **Truth fix.** POV framing, kind client, no amount, no real chat-app look or sounds. The ending "Bas ek choti si
  cheez..." is the loop.

### 4.3 C11 Bijli Chali Gayi · `dusk` · light family · 78

- **Hook.** Frame 0: a warm desk corner (CRT glow, UPS LED, table fan, laptop). At 0.4 s a brownout dims it and
  the CRT collapses to a dot. Text by 0.6 s `*Bijli* / CHALI GAYI.` lit by the torch beam at 0.7 s. VO after the
  UPS beep: "Har desi ghar ki sab se famous awaaz..."
- **Build (start the Blender queue with this reel).**
  - One desk-corner plate, rendered twice: lit, and practicals-only.
  - Static props: hand fan, candle, homework copy, CRT, UPS, laptop. Each prop gets two light passes (key from
    left and from right); the beam position cross-fades them, so the torch seems to move the light. About 2-3 min
    CPU per render at 2 threads.
  - Torch: a soft moving light mask plus a haze cone (L7).
  - Candle flame: procedural, noise-warped, with no boiling between frames.
  - Power-on: local blooms on each practical (L4), not a full-frame lift.
  - Ctrl+S: a jw_mono HUD plus "Saved" toasts that pulse on the beat (keycaps belong to C01).
- **Faces.** street_chinup_gaze toward the bulb at the power return (the right pose for it) and suit_smiling in
  candlelight. Candle light is a soft gradient multiply plus a warm rim; never a depth-map relight.
- **Sound.** UPS beep (sine), crowd_cheer_real for "aa gayi!", laptop_fan wind-down, CRT zap (glitch plus sub),
  harmonium_swell, a `lofi_desi` 84 bed or a pad.
- **Failure modes.**
  - The designed blackout is the only allowed YMIN dip; flicker only darkens.
  - `dusk` violet shadows plus orange haze turn brown and muddy: keep the beam ivory-warm and the haze thin.
  - The Blender queue is the critical path: props first, timeline on labelled stand-ins.
  - The VO is long on the card: trim to about 80 words.
- **Truth fix.** "Phir editing aayi" (not "main ne editing shuru ki"), "har editor ki ungli Ctrl+S dabati hai",
  "har desi ghar". Nostalgic, no utility or government names, no money on screen.

### 4.4 C01 J · K · L · `noir_ember` · editor family · 87

- **Hook.** Macro of a black-gloss K keycap slamming down by itself; every ember freezes mid-air; HUD `0x`. Text
  `Editing ke / *3 button*` plus a mono strip `J peeche · K ruko · L aage` by 1.5 s (this labelling is mandatory
  for non-editors). VO: "Har editor ki zindagi teen button pe chalti hai: J, K aur L."
- **Build.**
  - 3 keycaps (rounded box, black clear-coat, emissive FLAME legend), static front and 3/4 renders; the press
    happens in 2D (y offset plus squash on contact, spring from the contact frame).
  - One keyboard-macro plate with a shallow-DOF Cycles render: the world is a dark keyboard landscape, not the
    C08 void.
  - The world clock is w(t): J runs it backwards, L at 2x/4x/8x, K freezes it. Because `draw(t)` is pure, every
    particle, light streak and glass card obeys the key for free.
  - HUD readout in jw_mono, turning RED at 8x.
- **Faces.** street_threequarter_turn under an 8x directional smear (blur on a rigid cut-out is safe), suit_neutral
  for the K dolly (push <= 8 %/s, parallax <= 3 %/s), a hard-cut swap to suit_smiling.
- **Sound and sync.** keyboard thock (`typing_modelm_real` / `mouse_click`), vinyl_rewind on J, shepard_riser across
  the L taps, tape_stop into true silence on K. The bed (pad or EP, not piano) is time-mapped by the **same w(t)**
  in numpy, so music and picture cannot drift. This is the one custom-sync reel; its sync is by construction,
  not by hand.
- **Failure modes.**
  - 8x smears must use 7 samples or a per-layer K.whip_blur over exactly that window.
  - Keycap legends must not share the glow colour of the keycap rim (contrast rule).
  - Ember bokeh must stay off the type.
- **Truth fix.** Already universal. Change the closing lockup from "Aaj *K* dabao" to "Ek minute *ruko*": the word
  "aaj" belongs to C19's payoff and must not appear in both reels.

### 4.5 C19 Kal se pakka · `gold_hour` · type family · 82

- **Hook.** A 3D desk-calendar page reads `KAL`. The camera zooms through the counter of the serif "a" (Y1) and
  finds another calendar page that says KAL. Text `KAL SE / *pakka*.` VO: "Kal se gym. Kal se course. Kal se apna
  channel."
- **Build.**
  - One Blender desk calendar (static, about 5 min) for the hero establishing frame.
  - The nested levels use a matched flat page sprite (paper fibre noise, spiral holes, soft bevel, contact
    shadow) so the Droste zoom is 4-5 scaled draws per frame, seamless by construction.
  - Excuses on the nested pages (`Monday se`, `Naye saal se`, `Shaadi season ke baad`), T.Counter 1 -> 365 with
    blur_cap.
  - The tear: a noise-edged mask that opens along a path, an ember edge (O6 code), paper fibres at the edge.
  - Behind it, `*AAJ*` in jw_key over a gold_hour sunrise with rays.
- **Faces.** suit_confused and suit_shocked swapped on counter beats (same sheet, easy eye alignment), suit_smirk at
  AAJ.
- **Sound.** clock_tick with accel, a page-flip flurry and the tear (custom noise-burst synthesis; the one sound to
  gate), whoosh into AAJ, trailer_hit, a `desi_epic` 100 or `dark_pulse` bed.
- **Failure modes.**
  - A clip-art paper look: the texture and contact shadow are the premium.
  - A visible seam in the Droste scale.
  - gold_hour's softer contrast lifting blacks: check YMIN.
- **Truth fix.** Universal already. No festival names (keep it neutral across both countries).

### 4.6 Gate for the riskiest swap-in (C15), if the panel overrides me

Before committing C15, render one hero still (crowd at full scale, the floodlight, JD small in the spotlight)
and a 3 s `--range` of the orbit reveal. Ship it only if both pass:
- At the still, the crowd reads as people, not clip-art.
- At the end of the orbit, the backs read as cardboard: brown board, tape and wooden struts drawn when a strip
  faces away.

Replace the "thousands of heads snap" with **"thousands of eyes open"** (two FLAME dots per head appearing in a
wave): it is cheaper and reads at distance. Build the whisper wall from the real crowd samples pitched down,
reversed and band-passed, not from `crowd_ooh`. The measured crowd cost is low (0.13 s per sample for 10 strips),
so the risk is artistic, not render time.

---------------------------------------------------------------------------------------------------------------

## 5. Production read on the Director's slate and N01

| Director pick | my view | condition |
|---|---|---|
| C11, C08 | agree | the budgets and fixes above |
| C24 Do JD | buildable (76) but costlier than C09 | split = about 1.6x render; 8-10 swaps; comic timing with one TTS narrator; keep each half's copy <= 470 px or span the divider |
| C15 | the highest single-shot risk in his slate (72) | the gate in 4.6 |
| N01 Ek Awaaz | visually very buildable (glass console strips, 6 static props at 1-2 min each, steam particles, meters driven by the real SFX envelopes so picture and sound cannot drift); score 74 | the reel claims "ek bhi recording nahi", so the CC0 samples are out and six synthesised household sounds must convince. The library has never been judged by ear. Gate: a blind listen of the cooker whistle, the doorbell and the cycle bell before any picture work; drop N01 if one fails |

---------------------------------------------------------------------------------------------------------------

## 6. Today's build and render plan (machine-wide cap: <= 4 render workers; a Blender job counts as one)

1. **Now, in parallel.**
   - VO per reel (per-beat takes, about 10 credits each).
   - The Blender queue, one job at a time at 2 threads: C11 plate plus props, then C01 keycaps plus keyboard,
     then the C19 calendar. About 45-70 min in total.
   - Timelines for C09 and C08 (no Blender), then C01, C19 and C11 on labelled stand-ins that switch
     automatically when `meta.json` appears.
2. **Iterate cheap.**
   - `--sheet 16 --samples 1`, then stills at every hero beat, then `--range` across every transition.
   - `--preview` (15 fps, 1 sample, about 4-5 min per reel per worker).
   - Read every image; check the type width table and the face limits.
3. **Masters on two workers.** C08 first (longest, 35-45 min), then C09, C01, C19, C11 (20-30 min each). About
   1.1-1.3 h of wall time on two workers.
4. **Gates before delivery.**
   - YMIN/YAVG per cut; the only allowed dip is C11's designed blackout.
   - Camera snap check on every move.
   - Safe-zone recorder.
   - Face halo <= +6 code values, eye offset <= 6 px at swaps, no pose > 3.5 s.
   - Emissive caps (FLAME and RED <= about 3x linear).
   - Hue budget (red-orange >= 60 % of saturated pixels).
   - Mix: -14 LUFS, <= -2.0 dBTP, speech >= 8 LU over the bed.
   - Captions off the faces.
   - `@jawad_mp4` end card held >= 1.5 s.

---------------------------------------------------------------------------------------------------------------

## 7. Open questions for the lead

1. **AI disclosure.** Every reel uses an AI voice (Vlad). Meta's AI label is an open question for Jawad; it is not
   skipped.
2. **Family reel.** The production slate has no family or tenderness piece. Should N01 (after the sound gate) or
   C02 (POV) replace C19?
3. **C08 frame count.** C08 says the reel's real frame count on screen. The brief must lock DUR so that the number
   is exact (34.133 s = 1,024 frames at 30 fps).
4. **C09 end card.** The CTA must be true. "Comment JD" only works if Jawad's DM automation exists; otherwise use
   "Apne editor dost ko bhejo".
