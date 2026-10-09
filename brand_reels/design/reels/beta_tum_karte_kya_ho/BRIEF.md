# BRIEF · Reel 4 (slot 4) · C02 · "Beta, tum karte kya ho?"

Date 2026-10-08 · Author: creative-director · Status: **production brief r2, binding for every agent on this reel**
(r2 = the viral gate's fixes from `GATE.md` §8 plus the approved script v1 lines; what changed is listed in the
CHANGELOG at the end).
Module `beta_tum_karte_kya_ho` · look `gold_hour` · BPM 85.714 (code: `BPM = 600 / 7`) · DUR 36.4 s = 1,092 frames.
Machine-readable twin: `packet.yaml` (same folder). Layout proof (real assets, measured) in
`workspace/jawad_reels/beta_tum_karte_kya_ho/brief_proof/`: r1 stills + `proof.json` + `layout_proof.py`; r2 stills
`r2_*.jpg` (each with a `_360.png` phone-size tile), `proof_r2.json` and `layout_proof_r2.py`, which holds a reference
implementation of every r2 change (window states, parody grounds, stamp, table, phone, creep, edge glow, count pill,
reel thumb, Nani pill, sun swell). Lift its code; do not import it from the module.

Binding sources, in order: `brand_reels/design/SLATE.md` §0, §2, §3.4, §4, §5 (series bible) → this brief → the
toolkit docs (`pipeline/jawad_reels/TOOLKIT.md`, module docstrings). Where this brief changes SLATE it says so in §10
with the reason. Brand rules: `.claude/skills/jawad-brand-reels/SKILL.md`. Never anything from Organic Fostering /
Floret, never the old prop library, never Jawad's own earlier devices listed in SLATE §5.1 "Banned everywhere".

---------------------------------------------------------------------------------------------------------------

## 0. Deliverables

| item | spec |
|---|---|
| Version A (public) | 1080x1920, 30 fps, **1,092 frames = 36.400 s**, hook A (f0-f83) + body (f84-f1091) |
| Version B (Trial Reel) | identical from **f84** (splice frame, 2.8 s); f0-f73 = hook B, f74-f83 = A's frames 74-83 without captions |
| Encodes (each version) | H.264 High 2-pass ~22 Mbps, +faststart, AAC 320k 48 kHz (< 100 MB); CRF 14 master; ~7 Mbps preview (< 30 MB) |
| Audio (each version) | full mix (VO + SFX + music) and no-music mix (VO + SFX only, for an in-app song), stems VO / SFX / music 48 kHz 24-bit |
| Cover | JPG of f30 (1.000 s) rendered **without the caption layer** (§6.17) |
| Captions file | SRT of the Roman VO track (`cap.save_srt`) for accessibility / upload |
| Audio name | "Original audio · Beta, tum karte kya ho? · @jawad_mp4" |
| Placement | organic Reel (not a paid ad): standard safe zones; no ad-zone version needed |
| AI label | Meta "AI info" **ON** (synthetic voice; character-sheet imagery possibly AI-generated). SLATE §7.1 default |

## 1. Brand (copied from `project.json` / SLATE §5.1; never re-derived)

| token | hex | job in this reel |
|---|---|---|
| NIGHT_0 / NIGHT_1 | #070404 / #170A07 | the room's darks, card windows behind stamp ink, 70-85 % of every frame |
| SMOKE | #2A1A15 | glass-card tint, input fields |
| FLAME | #FF6A1A | rims, card edges, keyword glow, M2 bridge colour, typing-dot glow |
| RED / EMBER | #F2312B / #B3120E | stamp ink (RED ×1.25 emissive), counter-rim, cartoon window ground (EMBER) |
| GOLD / AMBER | #FF9F1C / #FFB547 | sun disc core, sender chips (AMBER), wedding chrome, dots (≤ 5 % of frame) |
| IVORY / ASH | #FFF3E6 / #A8978C | all white type (never pure white) / field labels, POV label, "Forwarded" |

Type styles (jawad_kit): `jw_key` (Instrument Serif Italic flame keyword), `jw_caps` / `jw_caps_bold` (Poppins
SemiBold/Bold caps +6 %), `jw_body` (Poppins SemiBold), `jw_mono` (JetBrains Mono Medium), `jw_handle`. Parody-only
fonts (never brand type): `c02_parody_wedding` = Cinzel Bold 700 (OFL), `c02_parody_cartoon` = Bungee Regular (OFL),
already copied into `<WS>/fonts/` (licences in `workspace/jawad_reels/beta_tum_karte_kya_ho/licences/`).
Mark: JD monogram + `@jawad_mp4` only via `endcard.EndCard`. Measured contrasts: IVORY on SMOKE 15.3:1, ASH on SMOKE
5.9:1, AMBER on SMOKE 9.5:1, FLAME on SMOKE 5.8:1, RED on NIGHT_0 5.1:1 (RED on SMOKE is 4.2:1: never use it).

## 2. Verified copy + Do not claim

Source column: S = SLATE §3.4 (approved), B = this brief (new, universal POV, no facts about Jawad). Status: all
`verified` against SLATE or `brief copy - lead OK` (new lines need no client fact).

| id | exact text | style | source | status |
|---|---|---|---|---|
| H1 | BETA, TUM / *karte kya* / HO? | caps / key / caps | S | verified |
| H2 | MOTION DESIGNER / *cartoon?* | caps / key | S (hook B) | verified |
| P1 | MERA BETA / *cinema* / BANATA HAI | caps / key / caps | S | verified |
| E1 | GROUP MEIN / *bhejo* | EndCard caps / key | S | verified |
| U1 | POV · har desi ghar | jw_mono | S (truth framing) | verified |
| U2 | Mummy · Nani · Chachi · Mamu · Chachu (sender chips) | jw_body | S (Mummy, Nani); B (relatives, religion-neutral, both countries) | brief copy |
| U3 | Mummy translate · Aap ne kaha · Mummy ne suna | jw_body / jw_mono | S ("Mummy translate"); B (labels) | brief copy |
| U4 | Video editor · Motion designer · Content creator · Brands ke liye cinematic reels | jw_body | S | verified |
| U5 | Shaadi wala? · Cartoon? | jw_key | S | verified |
| U6 | Happy Wedding (parody) · MOTION (parody) | parody fonts | S | verified |
| U7 | PHONE PE LAGE / REHTE HO. (stamp) | jw_caps_bold | S ("Phone pe lage rehte ho.") | verified |
| U8 | Achha. / Naukri kab lagegi? | jw_body | S | verified |
| U9 | Kuch mahine baad | jw_mono | S | verified |
| U10 | Khandaan · Forwarded · Kamaal! · Wah! · Mummy is typing | jw_body / jw_mono | S | verified |
| U11 | Khandaan · 12 → 47 → 99+ (count pill on the face-down phone's chip) | jw_mono + `T.Counter` | B (gate fix 1; a fictional unread count) | brief copy |
| VO | the 12 VO lines of §6.7 (A: L1-L11; B: L1B + L2-L11) | captions | S (L1, L5, L7, L9 locked) + script v1 (L2-L4, L6, L8, L10) + gate (L1B, L11) | verified / brief copy; **L1B needs the lead's OK** (it replaces a SLATE-locked line) |

**Do not claim / never show:** that this is Jawad's family, mother, relatives or history (it is "POV · har desi
ghar"); any view count, client name, earning, number of followers or "viral"; Mummy's face, hands or voice; a real
messaging app (no WhatsApp green, double ticks, doodle wallpaper, "Seen", app logos); religious words or greetings
(no "Mubarak", no MashaAllah / Bhagwan), currency, phone numbers, city or country names, flags, cricket cues;
first-person "main" about Jawad; "Comment JD"; "watch full video". The only numbers on screen are the group's fictional
unread count (12, 47, 99+, U11); never a view, like, follower or money figure, and the reel thumb (§6.4 S8) shows no
count or duration.

## 3. References and devices

- **Influences (director-styles, three rows):** the Daniels (viral comedy with heart: commit fully to the absurd
  wrong-genre parodies, then turn sincere), Spielberg (the reaction lives on the face, lit by what it sees: JD lit by
  the phone, the payoff lands on his hand-on-chest), Wes Anderson (artifice declared openly: frontal centred
  deadpan busts, UI cards as chapter cards). Principles only, never their shots.
- **Devices used:** signature *Mummy-translate misunderstanding renderer* (SLATE); chat-bubble POV (hooks research
  "dialogue / scene"); sentence + visual loop (hooks §3.3: VO L11 "Ab Nani ki baari." is completed by frame 0's
  question); drop-out before the reveal (bible §4.4); one desi voice = tabla (bible §4.7); snake captions (Jawad's
  caption signature); house lockup `J.HouseTitle`; rewatch easter egg (the reel forwarded into the family group is
  this reel: its own cover is the thumbnail).
- **Killed obvious versions:** the "beta engineer ban jao" skit; "my parents think I play games"; the son showing his
  mother a view count; a crying-mother montage. **Contradiction:** a premium cinematic frame hosting deliberately
  cheap, fully committed genre parodies inside a card window (≤ 40 % of the frame).

## 4. Global craft rules (Standards + this reel's resolutions)

- **Safe zones 1080x1920:** key copy x 70-1010, y 230-1480 (CTA to 1600; signature at y ~1575); nothing textual at
  x > 930 for y 1050-1700; bottom 300 px (y > 1620) free of text; profile grid crop 3:4 = y 240-1680.
- **Sizes:** hero ≥ 130 px, H2 80-120, UI ≥ 34 px (tags in motion ≥ 40), every line ≤ 940 px (≤ 780 in y 1050-1700).
- **Text-block rule (≤ 2 at once), defined for this reel:** one block = a designed lockup (all lines), OR one UI
  widget's text (a chat bubble incl. its sender chip, the translate card incl. labels/fields/output/parody window, the
  chat panel incl. all its messages, a chip), OR one caption chunk, OR the end card (CTA + monogram + signature as
  one unit). The 34 px POV status label is chrome. The per-window budget is §6.6.
- **Reading:** ≥ words/3 s settled (+0.3 s above 3 words); every designed string passes (§6.5 last column).
- **Grid:** 21 f/beat, 84 f/bar. 8th notes are 10.5 frames: **always quantise 8ths UP** (21k + 11); never call
  `G.at(..., sub=0.5)` (Python rounds half to even: 0.35 s → f10 but 2.45 s → f74).
- **Finish:** `post = G.tx_finish(cv, t, LOOK, cuts=..., rays=0.0, **kw)`; **`rays=0.0` is binding** (the gold_hour
  default 0.26 streaks every bright type/UI pixel and turns the centred end-card monogram into a radial burst = his
  OpenArt device; measured in the layout proof). No `K.flash` / `K.fade` / `post(flash=)`; exposure pushes only.
- **Motion:** exits ease out ≥ 0.2 s; brand type gets no bounce or JELLY (rise / fade with `out_cubic`); UI cards may
  POP; parody type may JELLY / SLAM. Motion blur never crosses a cut (jawad_tx cut rule). 3 samples default,
  5-7 inside transition windows (`plan.samples(t)`).
- **Faces:** 2.5D cut-outs only, no lip-sync, no warps, hard-cut swaps, eyes locked, ≤ 3.5 s per still pose, display
  scale ≤ 1.0 (§6.10). Never cover a face with UI.
- **Depth:** every shot has ≥ 3 layers (room plate + bokeh / subject or card / foreground dust motes `J.embers`).
- **Finish rules from SLATE §5.1** (grain only from `G.finish`, halation on practicals, bokeh off type) apply.

## 5. Assets

| asset | source | notes |
|---|---|---|
| suit_confused, suit_shocked, suit_neutral, suit_hand_on_chest | `workspace/brand_reels/charsheet/cutouts/*.png` + `_depth.png` + `.json` via `faces.py` | 2x masters 764x1122 / 812x1122 / 812x1112 / 710x1122; display ≤ 1.0 |
| room / window world | `K.background('gold_hour', t, cam, bokeh=0.6)` (jawad_grade look) | horizon band + sun core sit low-centre behind JD |
| glass UI | `ui.glass_card(w, h, r, look='gold_hour')`, `ui.icon('globe' / 'arrow_right')`, `T.render`, `T.Counter` | built once in `assets()` |
| parody fonts | `<WS>/fonts/c02_parody_wedding.ttf` (Cinzel 700), `c02_parody_cartoon.ttf` (Bungee) | OFL 1.1, sha256 recorded in `licences/` folder |
| 3D props | **none** (SLATE §3.4) | wooden table, face-down phone, sun disc = 2D numpy sprites built once (reference: `table_tex`, `phone_sprite`, `phone_glow_sprite` in `layout_proof_r2.py`) |
| REEL_THUMB | this reel's own cover canvas (`draw(1.0)` without captions, before post), downscaled to 300x533 | built once in `assets()`; fallback REEL_THUMB_ALT (§6.4 S8) |
| SFX | `audio.py` catalog + `epic_sfx.register()` (notif_ping, tabla_hit) | all 56 cue names verified in `A.names()` |
| music | per-reel arrangement on `epic_music` building blocks (§6.13) | not `EM.render('lofi_desi')` as is |
| VO | Higgsfield Vlad (`vo_config.json`) → `vo_chain.py` | ≤ 30 credits for this reel (12 takes) |

---------------------------------------------------------------------------------------------------------------

## 6. The reel

### 6.0 Director's pass (compact)

- **Emotional core:** amusement, then tenderness. **Whose experience:** the son's phone (we live it through chat).
- **Human truth:** every desi parent asks what you do, and translates the answer into something they already know.
- **Single image (anchor, f900 / 30.0 s):** Mummy's chat bubble glowing above JD's hand-on-chest bust in gold
  backlight, reading MERA BETA / *cinema* / BANATA HAI.
- **Story:** the question (hook) → three wrong translations (escalating comedy) → the honest answer meets "Naukri kab
  lagegi?" (the killer line) → giving up → months later the phone on the table starts buzzing as the family group
  explodes (Khandaan · 12 → 99+) → a reel lands in the group (this reel) → Mummy explains it better than you → Nani
  starts typing, "Ab Nani ki baari." (loop: frame 0 asks the question again).

### 6.1 World Bible (verbatim lines; every scene and prompt obeys them)

```
WORLD BIBLE: C02 Beta, tum karte kya ho?
Palette: night #070404, flame #FF6A1A, gold #FF9F1C (accents red #F2312B, amber #FFB547, type ivory #FFF3E6)
Light logic: two sources only: the low sun through the window behind JD (gold backlight, FLAME rim strongest
  camera-right) and the phone screen below frame (soft amber from below on JD's face); glass UI glows only from its
  own rim. No top light, no spotlight, no god rays.
Lens set: 50 mm phone-held for the room and the UI; 85 mm for JD's busts (shallow, aperture 24); 100 mm macro for the
  typing-dot push into the payoff.
Camera law: phone-held intimacy: UI floats with a <= 4 px handheld drift; JD only gets slow push-ins (1.2 %/s) and
  hard-cut punch-ins on reactions; never a dissolve between faces, never an orbit, never a whip on JD.
Texture: gold_hour finish, brown-black floor, soft contrast, film grain 0.018 at 1.6 px, halation on the sun and type
  glow only, no god rays.
Sound motif: the message pop (notif_ping tuned to A6) and the typing-dot tick.
Recurring symbol: the three typing dots.
Forbidden: Mummy on screen (face, hands, voice); hearts; shehnai; ERROR dialogs; WhatsApp look (green, ticks,
  doodles, "Seen"); real app UIs or logos; centred ring with radial rays; god rays; religious, national, currency,
  phone-number or city markers; first-person "main" about Jawad; JELLY or bounce on brand type; cross-dissolves
  between faces; the old prop library (chat_bubble, pin_phone, heart, house ...); full-frame flashes.
```

- **Cast block JD** (identity locked, cut-outs only): the suit sheet: black three-piece suit, white shirt, black tie,
  fuller side-swept dark hair, full beard; frontal busts. Gestures: confused (knitted brows, mouth open mid-word),
  shocked (wide eyes, raised brows, mouth shut), neutral (level stare to lens), hand-on-chest (hand flat on chest,
  eyes up-right). One wardrobe for the whole reel (suit).
- **Location HOME_GOLDEN:** a brown-black desi room at golden hour; anchors: (1) the window glow low-centre behind JD
  (gold_hour horizon band y ≈ 1500, sun core behind his chest), (2) warm bokeh discs in the upper half (kept off
  type), (3) a dark wooden table in the time-skip shot: planks running away from camera, a gold window-light band with
  one mullion shadow crawling across it. No décor that names a religion, country or brand.
- **Props (2D / UI):** TRANSLATE_CARD (small parody window in S1, big window from M6 to the fold), MUMMY_BUBBLE
  (typing pill → message bubble), FAMILY_CHAT ("Khandaan"), PHONE_FACE_DOWN (glossy back, camera bump, flame light
  leaking from under it), COUNT_PILL ("Khandaan · 12 → 99+", in the chip rect), SUN_DISC, REEL_THUMB (this reel's own
  cover, f30 without captions), three PARODY windows.
- **Continuity ledger:** eye midpoint (540, 1280) in every JD shot; rim camera-right in every JD shot; card rect
  (90, 296)-(990, 1176) identical in S1/S2/S4/S5 and the chat panel in S8; parody window big state (110, 590)-(970,
  1160) from f147 to its fade at f372-f377 (S2, S4, S5; continuous across c3 and c4 so the card never changes layout
  across a cut); chip / count pill rect (310, 302)-(770, 378) through S7; sender chips at (160, 252) above incoming
  bubbles; POV label right-aligned at (1000, 252) in hook and UI scenes and with the Nani pill from 35.0; the Nani pill
  rect (147, 280)-(467, 420) is the frame-0 pill rect and is drawn by the same function over S11 and S12 (pixel-continuous
  across c12); the sun is behind JD in S0/S9/S10 and sinks in S11; time of day only moves forward (golden → setting).

### 6.2 Grid and master beat table (frame-exact)

`G = X.Grid(600 / 7)` → `G.fpb == 21.0`, `G.locked` True. Bar n = frame 84n. 13 bars = 1,092 frames = 36.400 s.
Splice frame f84. Payoff 28.0 s = 76.9 %. Re-hooks 11.2 s (31 %) and 19.6 s (54 %).

| f | t (s) | bar.beat | event | owner notes |
|---|---|---|---|---|
| 0 | 0.000 | 0.0 | HOOK A: JD suit_confused + "Mummy" typing pill + POV label | f0 rules §6.3 |
| 3 | 0.100 | 0.0+3f | VO L1 starts | |
| 8-12 | 0.267-0.400 | | pill expands to the message bubble; lockup H1 fades in f9-f12 | legible ≥ 96 % at f11 |
| 11 | 0.367 | first 8th | message lands: notif_ping | |
| 74 | 2.467 | 0.3+11f | (hook B only) hard cut to A's f74 | |
| **84** | **2.800** | **1.0** | **c1 cut (L3) → S1 translate card (SPLICE)** | |
| 98-116 | 3.267-3.867 | | input "Video editor" types | |
| 126 | 4.200 | 1.2 | output "Shaadi wala?" pops (small layout, as taught in S1) | caption layer clear by f126 (§6.11) |
| 135-141 | 4.500-4.700 | | "Mummy ne suna" label, output field and arrow fade out (in_cubic 0.2 s) | r2, fix 2 |
| 135-147 | 4.500-4.900 | | parody window grows (130, 836)-(950, 1136) → (110, 590)-(970, 1160) (out_cubic) | r2, fix 2 |
| 135-158 | 4.500-5.267 | | **M6 ★ window** (c2 = f147 = 4.900, beat 7) word rides the new path into the window; absorbed into the spark f147-f153 | path §6.8 |
| 153-165 | 5.100-5.500 | | "Happy Wedding" wipes in L→R (96 px, centre (540, 875)); sparkle burst at the spark landing f159 | |
| 180-189 | 6.000-6.300 | | wedding parody wipes out (parody total 1.4 s); window stays big and idle | |
| 190-205 | 6.333-6.833 | | input "Motion designer" types | |
| 210 | 7.000 | 2.2 | "Cartoon?" output pill POPs at the window top + halftone ground + MOTION (180 px) rubber-hose wobble | caption layer clear by f210 |
| 221 | 7.367 | 2.2+11f | boing 2 | |
| **231** | **7.700** | **2.3** | **c3 cut (L3) → S3 suit_shocked punch-in** | |
| **252** | **8.400** | **3.0** | **c4 cut (L3) → S4 card returns (big window) pre-filled "Content creator" + stamp SLAM (76 px)** | §10 change 2 |
| 294 | 9.800 | 3.2 | camera accent: 2 % push + 6 px nudge on the card (out_cubic 0.7 s) | |
| 327-344 | 10.900-11.467 | | **M3 window** (c5 = f336 = 11.200, bar 4) card swipes left, card B (big window, idle) arrives pre-filled | RE-HOOK 1 |
| 364-371 | 12.133-12.400 | | loading dots in the window centre (540, 875) | |
| 372-377 | 12.400-12.567 | | window fades out (in_cubic) | |
| 378 | 12.600 | 4.2 | KILLER: Mummy bubble "Achha. / Naukri kab lagegi?"; music silent from here | |
| 410-419 | 13.667-13.967 | | card folds away (rx 0→80°); killer bubble glides up to (150, 280)-(930, 520) | |
| **420** | **14.000** | **5.0** | **c6 cut (L3) → S6 suit_neutral; killer bubble persists to f449, exits f450-f458** | |
| 462 | 15.400 | 5.2 | window light starts dimming (-15 % over 1.4 s): time begins to pass | |
| **504** | **16.800** | **6.0** | **c7 cut (L3) → S7 time skip: wooden table, glossy face-down phone, chip "Kuch mahine baad" POPs, buzz 1** (haptic pulses 16.8 + 17.0: shake + 6 px creep each; flame edge glow switches on) | r2, fix 1 |
| 516 | 17.200 | 6.0+12f | buzz 1's own ping (sound pre-roll 0.40 s): edge-glow pulse | |
| 540-545 | 18.000-18.167 | | chip text "Kuch mahine baad" rises 12 px and fades (in_cubic 0.2 s); L6 has ended (est. 17.98) | |
| **546** | **18.200** | **6.2** | **count pill "Khandaan · 12" rises in (out_cubic 0.2 s) in the same rect; buzz 2** (haptic 18.2 + 18.4: shake + 6 px creep each) | r2, fix 1 |
| 558 | 18.600 | | buzz 2's own ping: edge-glow pulse | |
| 567 | 18.900 | 6.3 | ping: count rolls 12 → 47 (f567-f573, out_cubic); phone jolt + 5 px creep | |
| 578 | 19.267 | 6.3+11f | ping: count rolls 47 → 99 (f578-f582); jolt + 5 px creep | |
| 583 | 19.433 | 6.3+16f | ping: "+" fades on (f583-f587) → "99+"; jolt + 5 px creep; edge glow climbing to its peak at f588 | |
| 582-593 | 19.400-19.767 | | **M2 window** (c8 = f588 = 19.600, bar 7) hue bridge → S8 "Khandaan" floods; groove returns | RE-HOOK 2 |
| 651 | 21.700 | 7.3 | forwarded reel bubble lands: REEL_THUMB = this reel's own cover (300x533) | r2, fix 3 |
| 672 / 693 | 22.400 / 23.100 | 8.0 / 8.1 | "Kamaal!" / "Wah!" | |
| 756 | 25.200 | 9.0 | "Mummy is typing" pill | |
| 777 / 798 | 25.900 / 26.600 | 9.1 / 9.2 | typing stops / resumes | |
| 819 | 27.300 | 9.3 | **drop-out** starts (music gated 21 f = 1 beat) | |
| 825-854 | 27.500-28.467 | | **M1 ★ window** (c9 = f840 = 28.000, bar 10): push into typing dot 3 → sun disc | |
| **840** | **28.000** | **10.0** | **PAYOFF**: hit stack; Mummy bubble + lockup P1 builds from f840 | |
| **861** | **28.700** | **10.1** | **c10 cut (L3) → S10 suit_hand_on_chest punch-in** (lockup persists) | |
| 924-939 | 30.800-31.300 | 11.0 | sun swell behind JD (world intensity +35 %, sun glow ×1.3, out_cubic 0.5 s) under "humse behtar" and the chord change | r2, note 6 |
| 955-965 | 31.833-32.167 | | payoff lockup + bubble exit | |
| **966** | **32.200** | **11.2** | **c11 cut (L3) → S11 end-card world; EndCard t0** | |
| 1021 | 34.033 | | end card settled (t0 + 1.85) | |
| **1050** | **35.000** | **12.2** | **"Nani" chip + typing pill POP over the end-card world in the frame-0 pill rect; POV label fades in; notif_ping A6; VO L11 "Ab Nani ki baari." from ≈ 34.95** | r2, fix 4 |
| **1071** | **35.700** | **12.3** | **c12 cut (L3) → S12 = hook scene at t − 36.4: suit_confused; the Nani pill carries across the cut** | |
| 1081-1091 | 36.04-36.37 | | end-card type exits into the loop push; L11's last word ends ≤ 36.36 | |
| 1092 = 0 | 36.400 | 13.0 | loop to frame 0 (its bubble completes "Ab Nani ki baari." with the question) | |

### 6.3 Hook 0-2.8 s, frame by frame

**Frame-0 rules (SLATE §2 / hooks §2.1):** motion already running (JD push starts at t = −0.7 via the pre-roll
scene, dots pulsing, motes drifting); no black, no fade, no logo, no greeting; works as a muted still; spoken line
by f3; on-screen text ≤ 6 words, legible by f11 (≤ 0.5 s); no centred ring with rays.
**r2 (gate note 8):** no light ramps in on the first frames: the room plate, the horizon band behind JD, the pill's rim
and the dots' AMBER glow render at their f11 levels from f0. Dot scale `s_i(τ) = 0.85 + 0.15·cos(2π(τ − 0.1 i)/0.6)`,
i = 0, 1, 2, τ = local hook time (t at f0-f83, t − 36.4 in S11/S12), so dot 1 peaks at f0 and the S12 → f0 seam
stays continuous.

**Hook A**

| f | t | picture | sound |
|---|---|---|---|
| 0 | 0.000 | JD `suit_confused` (look A) at eyes (540, 1280), scale 0.9277 (push from 0.92 at t = −0.7, +1.2 %/s), phone glow under the chin. "Mummy" chip (AMBER jw_body 36, left x 160, cy 252); typing pill (147, 280)-(467, 420) r 40 with 3 AMBER dots r 14 at x 263/307/351, cy 350, pulsing (scale 0.7↔1.0, 0.6 s cycle, 0.1 s phase per dot). POV label right x 1000, cy 252. Room: gold_hour plate, bokeh 0.6, `J.embers(60, seed=21, bright=0.4)` in front | impact_soft −8 (loop landing), ui_tick −12; music bar 0 downbeat (tabla + EP) |
| 2 | 0.067 | first caption chunk "Sab se" starts entering (upper band, y ≈ 880) | |
| 3 | 0.100 | — | VO L1 "Sab se mushkil sawaal client nahi poochta." starts |
| 8-12 | 0.267-0.400 | pill rect expands to the bubble (147, 280)-(933, 740) r 44 (out_cubic; one cached glass card per frame size f8-f12); dots fade f8-f9 | |
| 9-12 | 0.300-0.400 | lockup H1 fades in (opacity out_cubic) + rises 14 px: `BETA, TUM` cy 350.0, *karte kya* cy 518.7, `HO?` cy 687.4 (static HouseTitle sprites, underline off) | |
| 11 | 0.367 | H1 ≥ 96 % opacity: legible | notif_ping (pitch 1.1225 = A6) −4 → ducked under VO |
| 12-83 | 0.4-2.8 | hold; JD push continues; caption chunks "mushkil sawaal", "client nahi poochta" (white, no keyword) | |
| 42 | 1.400 | keyword halo flare ×1.3 (0.3 s inout_sine) on beat 2: the second visual event | tabla accent in the music |
| 78-83 | 2.600-2.767 | hook caption layer fades out (in_cubic) so no caption crosses the splice | VO L1 ends ≤ 2.69 (≤ 2.75 limit) |
| 84 | 2.800 | cut c1 (L3, push 0.5) → S1 | card_slide (lands 3.1) |

**Hook B (Trial; module `beta_tum_karte_kya_ho_hookb`, frames f0-f83)**

| f | t | picture | sound |
|---|---|---|---|
| 0 | 0.000 | Lockup H2 static from f0: `MOTION DESIGNER` jw_caps 86 cy 351.3 (855.6 px), *cartoon?* jw_key 210 cy 520 (663.6 px), no underline. Compact card (90, 700)-(990, 1176) r 48: globe icon (152, 752) + "Mummy translate" jw_body 50 left x 186 cy 752; window (130, 800)-(950, 1136) on EMBER with FLAME halftone dots, "MOTION" (c02_parody_cartoon 150 px, IVORY + 10 px NIGHT_0 outline + FLAME shadow 8,8) mid-wobble at cy 968. POV label. Captions hidden | bubble_pop −4, impact_soft −8 at 0.0 |
| 3 | 0.100 | — | VO L1B **"Mummy ke liye, cartoon."** (4 words, est. end 1.77-1.83 s, slot ends 2.40, QA ≤ 2.45). Picture unchanged: the H2 lockup is the headline, the voice adds whose reading it is (hooks rule 2). **Needs the lead's OK** (replaces the SLATE-locked line, which cannot land by 2.45 s); if refused, script v1 "Motion designer? Cartoon." |
| 21 | 0.700 | boing 2 (JELLY re-trigger) | bubble_pop pitch 0.8 −8 |
| 42 | 1.400 | MOTION letters droop and squash (rubber-hose collapse, 0.35 s) | swish_small −10 |
| 63 | 2.100 | *cartoon?* halo flare ×1.3 | tabla_hit 'na' −8 |
| 74 | 2.467 | hard cut (L3, push 0.5) to A's frame 74 (JD + Mummy bubble H1), **no caption layer** | notif_ping A6 −6 |
| 84 | 2.800 | body (identical to A) | |

B's loop is not seamless (its last frame is A's Nani pre-roll, its frame 0 is the card): accepted for a Trial.

### 6.4 Scene layout specs (screen px; all rects (x0, y0)-(x1, y1))

**S0 Hook / S12 pre-roll (f0-f83, f1071-f1091).** As §6.3. S12 is literally `scene_hook(t - 36.4, sender='Nani')`
for t ≥ 35.7: same pill, "Nani" chip (84.7 px) instead of "Mummy", no bubble expansion (it never reaches t ≥ 0.3).
The seam f1091 → f0 differs only in the chip word. **r2:** the Nani chip + pill + POV label already enter at 35.0 over
S11 (§6.4 S11), drawn by the same `hook_ui(τ = t − 36.4, sender='Nani')` overlay that S12 uses, so they do not
change at the c12 cut.

**Translate card (S1, S2, S4, S5).** `ui.glass_card(900, 880, r=48, look='gold_hour')` centred (540, 736) = rect
(90, 296)-(990, 1176), entering at 2.7-3.2 from y+520 (POP; already moving at f84), handheld float on the whole card
(dx = `K.wiggle(t, 0.3, 4, 11)`, dy = `K.wiggle(t, 0.25, 3, 12)`, rot = `K.wiggle(t, 0.2, 0.35, 13)` deg).
- header: `ui.icon('globe', 44, AMBER)` at (152, 352); "Mummy translate" jw_body 50 IVORY, left x 186, cy 352 (456.8 px).
- "Aap ne kaha" jw_mono 34 ASH left x 130 cy 436; input field (130, 462)-(950, 562) r 24 (SMOKE glass); input
  text jw_body 46 IVORY left x 162 cy 512; caret 3x46 px FLAME blinking 2 Hz while typing.
- `ui.icon('arrow_right', 44, FLAME)` rotated 90° at (540, 600).
- "Mummy ne suna" jw_mono 34 ASH left x 130 cy 640; output field (130, 666)-(950, 806) r 24; output word jw_key 130
  centred (540, 736) (SETTLE spring scale 0.9→1 + opacity over 4 f; no bounce on brand type).
- **Two window states (r2, gate fix 2).** *Small* (S1 only, f84-f134): parody window (130, 836)-(950, 1136) r 24 =
  820x300 px, idle (NIGHT_1 glass), under the arrow, label and output field: S1 teaches the app. *Big* (from M6 to the
  fold): the label, the output field and the arrow fade out f135-f141 (in_cubic 0.2 s) and never return, and the window
  grows f135-f147 (rect lerp, out_cubic) to **(110, 590)-(970, 1160) r 24 = 860x570 px = 23.6 % of the frame** (≤ 40 %
  SLATE cap), centre (540, 875). The input field (130, 462)-(950, 562) stays readable 28 px above it. The big state
  holds through S2, S4 and S5 (same card, same layout on both sides of c3 and c4) until the window fades out f372-f377.
  Between parodies (f190-f209) the window is idle NIGHT_1 glass. Proof: `r2_card_m6_4p8 / 5p0 / 5p2`,
  `r2_card_idle_6p5`.
- Input text dims to ×0.5 while a parody plays (f147-f189, f210-f230); full while "Motion designer" types.

**P1 Wedding parody (big window, f147-f189, 1.4 s).** Ground (r2): radial PLUM ×1.6 at the window centre → NIGHT_1
at the edges (radius 0.62 of the window, falloff power 1.3) + ~74 AMBER glitter stars (K.disc r 2-5 + GOLD glow,
opacity 0.25-0.8, twinkling), fading in f147-f159 (out_cubic) under the carried word. Reference `wedding_ground` in
`layout_proof_r2.py`. The r1 GOLD→AMBER→EMBER ground at 0.55 is dropped: at 23.6 % of the frame it put gold title on a
gold field (illegible in the r2 test render) and broke the GOLD/AMBER ≤ 5 % budget. Title "Happy Wedding"
`T.style('gold', font='c02_parody_wedding', px=96)` = **806.0 px** wide, centred (540, 875) (27 px clear of each window
side; 100 px = 839.6 px left 10 px, too tight for the bevel); built in with `T.Glyphs('Happy Wedding', <that style>,
px=96).wipe(cv, t, 540, 875, t0=5.1, dur=0.4)` (soft L→R mask wipe with a bright leading edge, f153-f165) + sparkle
particles; hold; wipe out f180-f189 (exit `out_t0=6.0`). `ts.draw(sweep=u)` is a light-sweep glint, not a reveal (r1
had this wrong); one glint may cross the settled title after f165. It is the only element allowed above 3× linear (proof
f156 peak 4.35 linear for 0.4 s, gold, 0.01 % of window pixels ≥ 245 on all channels). No hearts, no shehnai, no mehndi,
no religious motifs, no "Mubarak".
**M6 carrier:** jawad_tx draws its default ember spark (`sprite=None`, trail 6) along the path **`((540, 736), (625,
772), (615, 858), (540, 875))`** (r2: ends at the big window's centre; curve bbox x 540-631, so the 638 px word stays
inside the card); the spark has no opacity control, so the word rides with it as a screen-space overlay drawn after
`PLAN.draw`: position = `X._path_at(X._catmull(PATH), K.EASE['inout_cubic'](u))` with u = (t − 4.5) / (23 / 30) clamped
(the same u as `Win.u`), the `T.render('Shaadi wala?', 'jw_key', px=130)` sprite at scale 1.0 → 0.85 (inout_cubic
f135-f147), then 0.85 → 0.5 with opacity 1 → 0 (in_cubic) **f147-f153**: the word is absorbed into the spark at its
fastest point, and the title wipe starts at f153 after the word is gone, so the two words never overlap (r1's f151-f158
fade stacked "Shaadi wala?" on "Happy Wedding": unreadable in the r2 test). The scene stops drawing the static output
word from f135. The spark lands on f158; from f159 the B scene fires a 0.3 s sparkle burst at (540, 875) so the
spark's end reads as the burst (no bare pop; paired with the `sparkle` cue at 5.3).

**P2 Cartoon parody (big window, f210-f230 on screen).** All of it POPs at f210 (4 f): ground EMBER ×0.85 + FLAME ×0.9
halftone dots (grid 26 px, dot radius 2 → 9 px toward the bottom-right; no sunburst, no radial rays; reference
`cartoon_ground`); the **output pill** = the collapsed output field, glass r 69 at (282, 607)-(798, 745) holding
"Cartoon?" jw_key 130 (426.9 px) centred (540, 676) (UI POP on the pill, SETTLE on the word: no bounce on brand type);
"MOTION" c02_parody_cartoon **180 px = 779.8 px** (≈ 806 px with the stroke) IVORY + NIGHT_0 stroke 0.068 em + FLAME
drop shadow (0.053, 0.053) em, centred (540, 952), so the ±6° glyph wobble stays inside the 860 px window (190 px =
823 px + stroke = 849 px would leave ~5 px a side). Rubber-hose wobble per glyph: y-scale = 1 + 0.25 × (1 −
`X.spring(t − 7.0 − 0.05 i, 'JELLY')`), rot = 6° × sin(2π·2.5(t − 7.0) + i); second boing at f221. At peak stretch the
glyphs stay inside y 855-1033 whichever scale anchor is used (< 1050). Proof `r2_card_cartoon_7p2_180` (and `_190` for the rejected size).

**S3 Shocked punch-in (f231-f251).** JD `suit_shocked` look D, eyes (540, 1280), scale 0.92 × push × `FA.swap_push`.
Room plate only. No text.

**S4 Gag 3 (f252-f335).** Card returns in the big state with input "Content creator" pre-filled (372.1 px) and the
big window darkened by a NIGHT_0 scrim at 0.75 (×0.25, over 2 f) under the stamp. **Stamp U7 (r2: 76 px for the bigger
stage):** "PHONE PE LAGE" (618.6 px) / "REHTE HO." (415.5 px) jw_caps_bold 76, line pitch 95 px, fill RED ×1.25, ink
distress = `X.fbm(seed=9)` threshold 0.25 (≈ 15 % dropouts), double border (7 px + 2 px RED rrects, the inner one 17 px
in, 33 px padding: border box 685x215), block centred (540, 875) rotated −7° (rotated bbox ≈ (187, 726)-(893, 1024)),
SLAM from scale 1.5 → 1.0 (`X.spring(t − 8.4, 'SLAM')`, settles f265), card shake 6 px damped 0.25 s. Settled hold
f265-f326 = 2.06 s ≥ 1.97. Reference `stamp_sprite`; proof `r2_card_stamp_9p6`.

**M3 re-hook (f327-f344).** `MOVE = K.Track([(10.9, (540, 0), 'in_cubic'), (11.2, (140, 0), 'out_cubic'), (11.5,
(-260, 0))])`; card A draws at x = move.x, card B at x = move.x + 800 (both rest at 540 outside the window).
Velocity at c5 = 4,000 px/s on both sides. `K.whip_blur` 66 px horizontal on the card layer only for |k| ≤ 3 frames.
Card B (big state, window idle): input "Brands ke liye cinematic reels" pre-filled (697.0 px at 46 px), readable
11.3-13.67 s.

**S5 Killer (f364-f419).** Loading dots (3 AMBER dots r 10, centred (540, 875) in the big window) f364-f371; the
window fades out f372-f377 (in_cubic); f378 the card dims ×0.55 (inout_sine 6 f) and the killer bubble POPs: chip
"Mummy" left x 186 cy 612; bubble (150, 640)-(930, 880) r 44; "Achha." jw_body 60 IVORY left x 190 cy 712;
"Naukri kab lagegi?" (570.1 px) left x 190 cy 802. f410-f419: the card folds (Panel.plane rx 0→80°, drops 300 px,
in_cubic) while the bubble glides (easy_ease) to (150, 280)-(930, 520) with the chip at (186, 252).

**S6 Neutral (f420-f503).** JD `suit_neutral` look D. The killer bubble stays in screen space at (150, 280)-(930,
520) until f449, exits f450-f458 (in_cubic, +20 px rise). Window light −15 % from f462.

**S7 Time skip (f504-f587), r2 (gate fix 1: the drop-risk window must build and inform).** All layers are 2D, in
screen space; reference implementation `table_tex`, `table_frame`, `phone_sprite`, `phone_glow_sprite`, `creep`,
`edge_glow`, `skip_frame`, `counter` in `layout_proof_r2.py`; proof `r2_skip_17p2 / 18p3 / 18p95 / 19p5`.
- **Table (world, built once):** dark wood in table space 1400x2400: planks 232 px wide running away from camera,
  ring grain `0.5 + 0.5 sin(2π((x + plank offset)/26 + 1.6·warp))` ^2.2 (warp = smooth noise stretched along the plank),
  fine fibre noise ±0.10, plank tint ±0.10, 3 px dark seams (×0.2); albedo #1A0F0A → #3A2416; one short pale scratch
  lower-left (the uncomposed element); warped to the screen by the homography (0, 0)/(1400, 0)/(1400, 2400)/(0, 2400)
  → (70, −90)/(1010, −90)/(1330, 2010)/(−250, 2010) (30° look-down: seams converge upward); vignette 1 − 0.55·r²
  (floor 0.25).
- **Window-light band (per frame):** a 340 px band at 28° with 60 px soft edges and one mullion shadow (9 px, ×0.15)
  40 px inside it; its centre line sweeps x 340 → 740 (−200 → +200 about 540) over f504-f587 (linear: time passing).
  Light = albedo × (1.35 + 9.0 × band × GOLD/max(GOLD)): the grain stays visible inside the band (measured band mean
  64.9-69.7 vs 36.8-37.7 outside, limited-range luma) and the whole S7 frame now measures YAVG 35.0-37.0 / YHIGH 68-70
  (signalstats on the sRGB still) against r1's 32.8 / 74, so it is no longer the darkest frame of the reel (f0 = 33.9).
  Dust motes in the band (`J.embers(40, seed=17, bright=0.5)`, kept off the chip) = the third depth layer.
- **PHONE_FACE_DOWN (sprite built once, 300x620 r 52 + 6 px pad):** glossy back = vertical gradient #2C1B15 → #100705,
  a broad specular band (IVORY ×0.10, σ 46 px) plus a thin hot line (×0.05) at 62°, a 6 px bevel lit top-left (ASH
  ×0.55 + FLAME ×0.10); camera bump top-left = rounded island 146x156 r 40 (#24160F, ASH ×0.45 edge) with three lenses
  (r 28, 28, 21: NIGHT_0 disc, #1B0E14 inner, ASH ×0.75 ring 4 px, IVORY ×0.9 catch-light) and an AMBER ×0.55 flash dot
  r 8. Drawn with scale (1.0, 0.92) (foreshortening) and rot 12° (clockwise), centre **(522, 896)** at f504. At 360 px
  the bump and lenses read (tile `r2_skip_17p2_360.png`). No logo, no brand shape.
- **Creep and buzz (gate 1c):** direction 20° below +x (right and slightly down). Each haptic pulse of a buzz (16.8,
  17.0, 18.2, 18.4 s; notif_ping buzz=1 plays two pulses 0.2 s apart) = shake `K.shake(t, 5, 30)` under a 0.13 s sine
  envelope + **6 px creep** (out_cubic 0.13 s) + 0.4° rotation, so **12 px per buzz**; each ping at 18.9, 19.267, 19.433
  = 2 px jolt (0.10 s) + 5 px creep + 0.25°. Total 39 px and +2.35° by f587 (centre (559, 909), rot 14.35°); phone body
  bbox over the shot (316, 586)-(775, 1223).
- **Flame edge glow (gate 1a):** `K.glow` of the phone's alpha (σ 6/18/48, FLAME, include=False) drawn 'add' UNDER
  the phone with opacity 1.6 × g(t): g = 0.18·ramp(16.8, 17.0, out_cubic) + 0.22·ramp(17.2, 18.9, inout_sine) +
  0.60·ramp(18.9, 19.6, in_cubic) + Σ pulses 0.5·e^(−(t − p)/0.22) (2 f attack) at the pings 17.2, 18.6, 18.9, 19.267,
  19.433, clamped to 1. On from buzz 1 (0.18), 0.34 at 18.3, 0.89 at 18.95, 1.0 from 19.45 to the M2 cut (f587 and f588
  both carry the FLAME highlight the M2 bridge needs). Linear peak in the frame 2.13 (≤ 3×).
- **Chip → COUNT_PILL (gate 1b):** glass pill (310, 302)-(770, 378) r 38 throughout. "Kuch mahine baad" jw_mono 40
  IVORY centred (540, 340), POP f504-f512; rises 12 px and fades f540-f545 (in_cubic 0.2 s), after L6 ends. From f546
  (18.2, buzz 2) in the same pill: "Khandaan · " jw_mono 40 IVORY left x 366.8 (`'Khandaan · 99+'` = 346.4 px, so the
  full string is centred) + `T.Counter('jw_mono', px=40, fill='AMBER', prefix='', suffix='', decimals=0, sep='')` left
  x 639.0 (= 366.8 + 11 × 24.74 px mono advance), both rising 12 px in f546-f552 (out_cubic 0.2 s). Value track
  `K.Track([(18.9, 12, 'out_cubic'), (19.1, 47), (19.267, 47, 'out_cubic'), (19.4, 99)])`, `vel=trk.vel(t)` (odometer
  blur). "+" (jw_mono 40 AMBER) fades on at x 688.5 f583-f587 → "Khandaan · 99+". No green, no badge circle, no app
  icon, no ticks: same glass as every other pill (proof crop: `r2_skip_18p3`, `r2_skip_19p5`). Something changes at
  most 0.7 s apart from 18.2 to the cut: 18.2 pill + buzz 2, 18.6 glow pulse, 18.9 → 47, 19.27 → 99, 19.43 → 99+.
- One text block in S7 (the chip / pill); captions are hidden 16.85-18.2 and there is no VO 18.0-19.75.

**S8 Family chat (f588-f839).** Panel = card rect (90, 296)-(990, 1176); header: avatar disc r 30 (FLAME→RED
gradient, "K" jw_body 34 IVORY) at (156, 352); "Khandaan" jw_body 48 IVORY left x 202 cy 352. Message column clipped
to y 400-1150, messages stack from the bottom (newest at y 1150), each arrival pushes the stack up by its height +
20 px (out_cubic 0.25 s). f588-f609: a flood of older textless placeholder bubbles scrolls up fast (out_expo).
- f651 reel bubble (Chachi), **r2 (gate fix 3): 356x660 r 36, left x 130** (lands at (130, 490)-(486, 1150)): chip
  "Chachi" AMBER jw_body 36 left x 158 cy +40; "Forwarded" row cy +80 = `ui.icon('arrow_right', 28, ASH)` at x 172 +
  jw_mono 34 ASH left x 194; **REEL_THUMB 300x533 r 20 at (158, +104) = this reel's own cover**: in `assets()`, build
  the cover canvas once (the layers `cover()` draws at t = 1.0: world, `suit_confused`, Mummy chip, bubble, H1 lockup,
  POV label; no captions) **before post** (linear, so the S8 frame's own `tx_finish` grades it exactly once, no double
  grain), downscale with `cv2.INTER_AREA` to 300x533 (×0.2778), ×0.92 exposure (a screen inside a screen), rounded mask
  r 20; play triangle 36x40 px IVORY ×0.9 with a soft NIGHT shadow (σ 4) at its **bottom-left** (x 20, bottom 20 px up),
  never a centred ring, no view count, no duration. S8 never draws at t = 1.0, so there is no recursion. At 360 px the
  confused face and "BETA, TUM *karte kya* HO?" read in the thumb (tile `r2_chat_22p0_360.png`): muted viewers see it
  is his reel, it looks like cinema (flame type, rim-lit bust) before Mummy says *cinema*, and it is a rewatch easter
  egg (the reel in the family group is this reel; the CTA "GROUP MEIN *bhejo*" asks for exactly that).
  **Fallback REEL_THUMB_ALT** (if the lead rejects the meta idea): full-bleed gold_hour room (t 30.0) with the sun disc
  r 150 (glow σ 14/44/120) at (395, 1000), `suit_neutral` as a NIGHT_0 silhouette with a 9 px FLAME ×1.4 edge, scale
  1.5, eye midpoint at (600, 1150) (both shoulders run off the frame, so no cut-out edge shows), 150 px NIGHT_0
  letterbox bars, same downscale, mask and play triangle (reference `reel_thumb_alt`; proof `r2_chat_22p0_altthumb`:
  the silhouette reads as a man in a suit at 360 px; weaker than the cover).
- f672 "Kamaal!" bubble (Mamu) 340x120; f693 "Wah!" bubble (Chachu) 270x120 (chips inside, AMBER jw_body 36 at cy +34;
  text jw_body 50 IVORY at cy +82).
- Stack with the r2 bubble (clip y 400, 12 px feather): after f672 the reel bubble sits at y 350-1010 (the chip row,
  cy 390, slides under the header; "Forwarded" and the whole thumb visible); after f693 at y 210-870 (chip and
  "Forwarded" under the header, thumb top 86 px clipped, face and lockup visible); after f756 at y 120-780 (thumb top
  176 px clipped: the face stays). "Chachi" reads 21.7-22.4 s (0.7 s, one word), "Forwarded" 21.7-23.1 s (1.4 s).
  Proof `r2_chat_22p0 / 23p5 / 25p5`.
- f756 typing pill (130, 1080)-(600, 1150): "Mummy is typing" jw_body 36 ASH left x 160 cy 1115 + dots r 9 at x
  510 / 536 / 562 (cy 1115); dots freeze and dim to 60 % f777-f797, resume f798, slow pulse f819-f824.
- POV label right x 1000 cy 252 throughout.

**M1 (f825-f854).** `X.TX['M1']` with `a = callable` returning the drawn pose of dot 3, (562, 1115, 9) after the
scroll; `match = (540, 1260, 180)`; `b = (540, 1260, 110)` = SUN_DISC: `K.glow(K.disc(110, AMBER × 1.3), FLAME,
sigmas=(12, 36, 90), strength=0.9)` drawn 'add' at (540, 1260) over the gold_hour room (keep emissive ≤ 3× linear;
gold, never white). QA: HoughCircles on f839 / f840, centres ≤ 2 px apart, radii within 2 %.

**S9-S10 Payoff (f840-f965).** Bubble (147, 280)-(933, 790) r 44 POPs from f840, chip "Mummy" (160, 252).
`J.HouseTitle('MERA BETA', 'cinema', caps_px=86, key_px=210, underline=True).draw(cv, t, 540, 518.7, t0=28.0,
out_t0=31.8333)` → caps cy 350.0 (513.8 px), *cinema* cy 518.7 (567.4 px), underline at y 669.9 (652 px). Third line
"BANATA HAI" jw_caps 86 (566.9 px) at cy 731.9, entering like the caps line (rise 28 px + opacity, out_cubic 0.6 s)
from 28.45 s; exits with the lockup (opacity follows HouseTitle's out ramp). f861 hard cut to JD
`suit_hand_on_chest` (look A) in front of the sun (the disc is hidden behind his head; only the glow rims him).
**Sun swell (r2, gate note 6), f924-f939:** on the bar-11 downbeat (30.8 s, the Bbmaj7 chord change, under "humse
behtar") `u = K.ramp(t, 30.8, 31.3, 'out_cubic')`; the room plate draws with `K.background(LOOK, t, intensity=1 +
0.35 u)` and the SUN_DISC glow strength becomes 0.9 × (1 + 0.3 u); both hold to the c11 cut. No rays, no scale
punch-in (the pose is at 0.987 of the 1.0 cap). Measured on `r2_payoff_31p4_swell` vs `_noswell`: world pixels
outside the bust +13 % above black (limited-range mean 37.1 → 39.9), frame YAVG 56.1 → 58.4, linear peak unchanged
2.55 (≤ 3×). A glow-only +20 % was tested and rejected: +1.2 %, invisible (the disc is behind his head). This ends the
2.78 s static hold (29.05-31.83) at 1.75 s.

**S11 End-card world (f966-f1070).** The same room; SUN_DISC sinks (540, 1420) → (540, 1520), r 100, intensity
1.0 → 0.6 (linear) so its glow stays below the CTA (keyword box y 858-1082); slow push 1 %/s; motes.
`card = E.EndCard('GROUP MEIN', 'bhejo', monogram='JD', dur=4.2)`; `card.draw(cv, t, 32.2)` after the captions.
Boxes (measured): monogram (420, 440)-(660, 680), caps (251, 738)-(829, 798), keyword (350, 858)-(730, 1082),
signature (411, 1563)-(669, 1587). Settle 1.85 s, hold 1.99 s ≥ 1.5.
**Nani pill (r2, gate fix 4a), f1050-f1070, then carried by S12:** at 35.0 s (beat 12.2) the `hook_ui(τ = t − 36.4,
sender='Nani')` overlay pops over the end-card world, drawn after the end card: "Nani" chip (AMBER jw_body 36, left x
160, cy 252) + typing pill (147, 280)-(467, 420) r 40, scale 0.6 → 1 (`K.spring(t − 35.0, 2.6, 0.55)`, UI POP) and
opacity out_cubic over 5 f, dots per §6.3; POV label fades in 35.0-35.2 (out_cubic, ×0.85). The pill clears the
monogram box by 20 px (420 vs 440) and the POV label (600-1000, 235-270) clears everything (proof `r2_end_nani_35p2`).
At c12 (35.7) the same overlay continues over S12, so chip, pill and dots do not change at the cut; the confused pose
still totals 3.5 s (0.7 + 2.8). Sound: notif_ping A6 (Mummy's message sound) at 35.0, not a pop (§6.12). VO L11 "Ab
Nani ki baari." runs from ≈ 34.95 to ≤ 36.36 under it (§6.7). Text blocks f1050-f1091: end card + Nani widget = 2.

### 6.5 Every on-screen string (house spelling; measured with `T.measure`)

| id | text | style | px | width | position (anchor) | in → out (frames) | animation | reading |
|---|---|---|---|---|---|---|---|---|
| U1 | POV · har desi ghar | jw_mono ASH ×0.85 | 34 | 399.8 | right x 1000, cy 252 | f0-83, 84-419, 588-839, 1050-1091 (hook B f0-83) | static with its scene; fades in 35.0-35.2 with the Nani pill | chrome |
| U2a | Mummy (chip) | jw_body AMBER | 36 | 153.4 | left x 160, cy 252 | f0-83; f840-965; killer f378-458 at (186, 612)→(186, 252) | with its bubble | chrome |
| U2b | Nani (chip) | jw_body AMBER | 36 | 84.7 | left x 160, cy 252 | f1050-1091 (r2: from 35.0, across c12) | with the pill POP | chrome |
| H1 | BETA, TUM / karte kya / HO? | jw_caps / jw_key / jw_caps | 86/210/86 | 482.7 / 706.4 / 185.8 | x 540; cy 350.0 / 518.7 / 687.4 | f9 → cut f84 | fade + 14 px rise f9-f12 out_cubic; halo flare f42 | 2.4 s ≥ 1.97 |
| H2 | MOTION DESIGNER / cartoon? | jw_caps / jw_key | 86/210 | 855.6 / 663.6 | x 540; cy 351.3 / 520 | B f0 → cut f74 | static from f0; halo flare f63 | 2.47 s ≥ 1.0 |
| U3a | Mummy translate | jw_body IVORY | 50 | 456.8 | left x 186, cy 352 (B: cy 752) | f84-419 (B f0-73) | with the card | chrome |
| U3b | Aap ne kaha / Mummy ne suna | jw_mono ASH | 34 | 231.2 / 273.4 | left x 130, cy 436 / 640 | with the card (r2: Mummy ne suna fades out f135-141 with the output field) | — | chrome |
| U4a | Video editor | jw_body IVORY | 46 | 283.5 | left x 162, cy 512 | typed f98-116 → f179 | 20 cps type-on | ✓ |
| U4b | Motion designer | jw_body | 46 | 378.0 | same | typed f190-205 → f230 | 30 cps | ✓ |
| U4c | Content creator | jw_body | 46 | 372.1 | same | pre-filled f252 → f335 | — | ✓ |
| U4d | Brands ke liye cinematic reels | jw_body | 46 | 697.0 | same (card B) | pre-filled f336 → fold f419 | — | 2.37 s ≥ 1.97 |
| U5a | Shaadi wala? | jw_key | 130 | 638.2 | centre (540, 736) → M6 path to (540, 875) | f126 → carried f135-153 (absorbed f147-153) | SETTLE pop 4 f, then M6 | 0.7 s ≥ 0.67 |
| U5b | Cartoon? | jw_key | 130 | 426.9 | centre (540, 676) in the output pill (282, 607)-(798, 745) | f210 → f230 | pill POP + word SETTLE 4 f | 0.7 s ≥ 0.33 |
| U6a | Happy Wedding | c02_parody_wedding 'gold' | 96 | 806.0 | centre (540, 875) | f153 → f189 | Glyphs.wipe in f153-165, out f180-189 | 1.0 s ≥ 0.67 (from half-wiped f159) |
| U6b | MOTION | c02_parody_cartoon (+0.068 em stroke) | 180 (B: 150) | 779.8 (B: 649.8) | centre (540, 952) (B: 968) | f210 → f230 (B f0-73) | JELLY per glyph | ✓ |
| U7 | PHONE PE LAGE / REHTE HO. | jw_caps_bold RED ×1.25 | 76 | 618.6 / 415.5 | block centre (540, 875), rot −7° | f252 → swipe f327-335 | SLAM 1.5→1.0 | settled 2.06 s ≥ 1.97 |
| U8 | Achha. / Naukri kab lagegi? | jw_body IVORY | 60 | 214.7 / 570.1 | left x 190, cy 712 / 802 → glides to cy 352 / 442 | f378 → exit f450-458 | POP (UI), glide f410-419 | 2.4 s ≥ 1.63 |
| U9 | Kuch mahine baad | jw_mono IVORY | 40 | 396.0 | centre (540, 340) in pill | f504 → out f540-545 | POP in f504-512; out: 12 px rise + fade (in_cubic) | 1.2 s ≥ 1.0 |
| U11 | Khandaan · 12 → 47 → 99+ | jw_mono IVORY + `T.Counter` jw_mono AMBER | 40 | 346.4 (at 99+) | left x 366.8 / digits x 639.0 / + x 688.5, cy 340, same pill | f546 → cut f588 | rise in f546-552; rolls f567-573, f578-582; + f583-587 | 1.4 s ≥ 1.0 |
| U10a | Khandaan | jw_body IVORY | 48 | 257.2 | left x 202, cy 352 | f588-839 | with the panel | chrome |
| U10b | Chachi · Forwarded | jw_body AMBER 36 · jw_mono ASH 34 | | 131.3 · 189.0 | in reel bubble | f651 → f839 | POP | ✓ |
| U10c | Mamu · Kamaal! | jw_body 36 AMBER · 50 IVORY | | 118.3 · 218.8 | reply bubble | f672 → f839 | POP + stack push | ✓ |
| U10d | Chachu · Wah! | jw_body 36 · 50 | | 145.1 · 135.8 | reply bubble | f693 → f839 | POP + stack push | ✓ |
| U10e | Mummy is typing | jw_body ASH | 36 | 318.5 | left x 160, cy 1115 | f756 → M1 push | dots pulse / freeze / resume | ✓ |
| P1 | MERA BETA / cinema / BANATA HAI | jw_caps / jw_key / jw_caps | 86/210/86 | 513.8 / 567.4 / 566.9 | x 540; cy 350.0 / 518.7 / 731.9; underline y 669.9 | f840 → out f955-965 | HouseTitle rise per glyph, underline draw-on | 3.4 s ≥ 1.97 |
| E1 | GROUP MEIN / bhejo + JD + @jawad_mp4 | EndCard | 86/200/34 | 578.0 / 379.4 / 257.7 | EndCard defaults | f966 → f1091 | EndCard | hold 1.99 s ≥ 1.5 |
| CAP | snake captions | snake_captions | 64 / 128 | ≤ 780 lower, ≤ 940 upper | §6.11 | per VO word | glide / pop / settle | per VO |

Underline uses: P1 + E1 = 2 (≤ 3). Every width ≤ 940; lower-band strings ≤ 780; nothing textual at x > 930 in y
1050-1700; nothing textual below y 1620 (the signature at y 1563-1587 sits in the allowed CTA zone).

### 6.6 Text-block budget per window (≤ 2)

| frames | blocks |
|---|---|
| f0-8 | typing pill · caption chunk (from f2) |
| f9-83 | H1 bubble · caption |
| f84-230 | translate card (incl. parody window / output pill) · caption (L2, L3; layer clear at f126 and f210, §6.11) |
| f231-251 | none (JD reaction) |
| f252-377 | card + stamp / card B · caption (L4 from f327) |
| f378-419 | card B (dimmed) · killer bubble (no VO, no caption) |
| f420-458 | killer bubble · caption L5 |
| f459-503 | caption L5 |
| f504-587 | chip → count pill (one widget; L6 caption hidden; no VO after 17.98) |
| f588-839 | chat panel · caption (L7, L8) |
| f840-965 | P1 bubble · caption (L9, no keyword) |
| f966-1049 | end card (L10 caption hidden) |
| f1050-1070 | end card · Nani chip + pill (L11 caption hidden; POV label = chrome) |
| f1071-1091 | end card · Nani chip + pill (continuous across c12) |
| hook B f0-73 | H2 · card (captions hidden) |

### 6.7 VO beat plan (Vlad, `elevenlabs_v4`, Devanagari; ~2.7 words/s after `vo_chain`)

Total A = 55 words, B = 54 (cap 80-90: comedy lives in bubbles; never pad). Locked = SLATE wording, do not edit.
Every line has its on-screen explanation in the last column. Hero hits never sit on a word (payoff hit 28.0 →
VO 28.25 = 250 ms clear).

| id | slot (s) | max w | Roman Urdu (caption track; *keyword*) | meaning | Devanagari draft (scriptwriter finalises) | on-screen moment that explains it |
|---|---|---|---|---|---|---|
| L1 (locked) | 0.10-2.69 (end ≤ 2.75) | 7 | Sab se mushkil sawaal client nahi poochta. (no caption keyword) | The hardest question isn't asked by a client. | सब से मुश्किल सवाल क्लाइंट नहीं पूछता। | Mummy's bubble: BETA, TUM *karte kya* HO? |
| L1B (locked, B) | 0.10-2.40 | 6 | Motion designer? Mummy ke liye: cartoon. (captions hidden) | Motion designer? To Mummy: cartoon. | मोशन डिज़ाइनर? मम्मी के लिए: कार्टून। | card: MOTION DESIGNER → *cartoon?* + wobbling MOTION |
| L2 | 2.95-4.15 | 4 (fallback 3: drop "Aur") | Aur jawab ka *translation*... | And the answer's translation... | और जवाब का ट्रांसलेशन... | "Mummy translate" card; "Video editor" typed |
| L3 | 5.10-6.95 | 4 | Jitna samjhao... utna *ulta*. | The more you explain... the more upside-down. | जितना समझाओ... उतना उल्टा। | "Happy Wedding" parody; "Motion designer" being typed |
| L4 | 10.95-11.70 | 2 | *Seedha* jawab: | The straight answer: | सीधा जवाब: | card B pre-filled "Brands ke liye cinematic reels" |
| L5 (locked) | 14.15-16.15 | 4 | Phir... *haar* maan li. | Then... gave up. | फिर... हार मान ली। | JD neutral stare under "Naukri kab lagegi?" |
| L6 | 16.95-17.95 | 3 | Kuch mahine baad... (captions hidden: chip) | A few months later... | कुछ महीने बाद... | chip "Kuch mahine baad", phone face-down |
| L7 (locked) | 19.75-24.27 | 11 | Phir ek din family group mein... ek *reel* forward hoti hai. | Then one day in the family group... a reel gets forwarded. | फिर एक दिन फ़ैमिली ग्रुप में... एक रील फ़ॉरवर्ड होती है। | "Khandaan" floods; the "Forwarded" reel bubble lands at 21.7 |
| L8 (optional; cut first if long) | 24.45-27.12 | 6 | Ab sab ki *nazar*... Mummy pe. | Now all eyes... on Mummy. | अब सब की नज़र... मम्मी पे। | "Kamaal!", "Wah!", then "Mummy is typing" (25.2) |
| L9 (locked) | 28.25-31.97 | 9 | Ab woh sab ko khud samjhaati hain... humse behtar. (no caption keyword) | Now she explains it to everyone herself... better than us. | अब वो सब को ख़ुद समझाती हैं... हमसे बेहतर। | MERA BETA *cinema* BANATA HAI; JD hand on chest |
| L10 | 32.55-34.40 | 5 | Isko family group mein bhejo. (captions hidden: end card) | Send this to the family group. | इसको फ़ैमिली ग्रुप में भेजो। | end card GROUP MEIN *bhejo* |

Casting brief: warm, unhurried, wry; a narrator who smiles without laughing. Delivery: L1 plain statement, no
pause; "..." = 0.45 s (L5's "Phir..." may hold to 0.6 s, L9's to 0.45 s for the bonus laugh); L10 friendly, not
salesy. Pronunciation test before the run (≈ 2.5 credits): मम्मी, क्लाइंट, ट्रांसलेशन, फ़ैमिली ग्रुप, फ़ॉरवर्ड.
Generation: one take per line (11 takes incl. L1B), `jobs_wait`, never blind re-submits; budget ≤ 30 credits incl.
one retake round. Process each take with `vo_chain.py process` (python3 -I), then place lines at their slot starts
(first voiced onset = slot start ± 1 frame) into `beta_tum_karte_kya_ho_vo_A.wav` / `_vo_B.wav` (DUR long,
−16 LUFS) and write the reel-time word list `beta_tum_karte_kya_ho.words.json` (Roman tokens, `keyword` flags as above,
`start`/`end` in reel seconds). If a line overruns its slot by > 0.15 s: cut words (fallbacks above), never speed
beyond 1.10x, never move the picture events.

### 6.8 Transitions (family: match; 4 features, 2 ★, ≥ 2 bars apart)

```python
import jawad_tx as X
# glue cuts (L3) with their exposure-push gains: c1 card, c3 punch-in, c4 stamp, c6 neutral, c7 time skip,
# c10 punch-in, c11 end-card world, c12 Nani pre-roll
GLUE = [(2.8, 0.5), (7.7, 0.7), (8.4, 0.4), (14.0, 0.6), (16.8, 0.4), (28.7, 0.7), (32.2, 0.3), (35.7, 0.3)]
M6_OPTS = dict(pre=12, post=12, path=((540, 736), (610, 800), (600, 900), (540, 986)))   # default ember spark carrier
MOVE = K.Track([(10.9, (540, 0), 'in_cubic'), (11.2, (140, 0), 'out_cubic'), (11.5, (-260, 0))])
M3_OPTS = dict(pre=9, post=9, move=MOVE)
M1_OPTS = dict(pre=15, post=15, a=dot3_pose, b=(540.0, 1260.0, 110.0), match=(540.0, 1260.0, 180.0))
FEATURES = [('M6', 4.9, M6_OPTS),                 # c2 ★ word -> wedding title   (f147, window f135-f158)
            ('M3', 11.2, M3_OPTS),                # c5 momentum swipe, re-hook   (f336, window f327-f344)
            ('M2', 19.6, dict(pre=6, post=6)),    # c8 hue bridge into the group (f588, window f582-f593)
            ('M1', 28.0, M1_OPTS)]                # c9 ★ typing dot -> sun       (f840, window f825-f854)
PLAN = X.Plan([('L3', c) for c, g in GLUE] + FEATURES)   # 12 cuts, 13 scenes S0..S12 (sorted by time)

def post(cv, t):
    kw = {}
    for tid, c, o in FEATURES:                     # feature post (M2 exposure bridge, M1 push); NOT PLAN.post_kw
        for k, v in X.TX[tid].post_kw(t, c, **o).items():
            kw[k] = kw.get(k, 0.0) + v if k == 'push' else v
    kw['push'] = kw.get('push', 0.0) + CARD.post_kw(t, 32.2, DUR).get('push', 0.0)
    return G.tx_finish(cv, t, LOOK, cuts=[(0.0, 0.6)] + GLUE, rays=0.0, **kw)
```
**Do not pass `push_gain=` to an L3 or `look=` to M2 inside the Plan:** `Tx.__call__` forwards every option to the
draw function and `_tx_cut` / `_tx_hue` raise TypeError (tested 2026-10-08; filed in `SHARED_REQUESTS.md`). The glue
gains go through `cuts=` instead (`X.push_at` takes `(c, gain)`); M2's exposure post is identical for gold_hour and
the default look (both exposure 0.0). This exact plan was smoke-tested (draw, samples, post kw at 15 times).

| id | cut | frames | function | role | spacing |
|---|---|---|---|---|---|
| M6 ★ object carry-over | 4.900 (beat 7) | f135-f158 | `X.TX['M6']` = `_tx_carry` | the output word flies into its mini-scene and becomes its title | — |
| M3 motion match | 11.200 (bar 4) | f327-f344 | `X.TX['M3']` = `_tx_motion_match`, scenes take `move=` | re-hook swipe | +6.3 s |
| M2 colour match / hue bridge | 19.600 (bar 7) | f582-f593 | `X.TX['M2']` = `_tx_hue` (+ its exposure post) | phone glow → gold group scene | +8.4 s |
| M1 ★ shape match (circle) | 28.000 (bar 10) | f825-f854 | `X.TX['M1']` = `_tx_shape_match` | typing dot → the sun (payoff light) | +8.4 s |
| L3 glue (×8) | c1 c3 c4 c6 c7 c10 c11 c12 | c to c+3 f | `X.TX['L3']` = `_tx_cut` (no options); push via `cuts=GLUE` | beat cuts | — |

`draw`: `world(t) = PLAN.draw(t, SCENES)`; overlays after it in this order: screen-space lockups / persisting bubbles
→ captions → end card. `samples(t) = PLAN.samples(t)` (M6 7 near c / 5, M3 7 for k ≥ −3, M1 5, M2 3, else 3).
Do **not** use `PLAN.cues()` (its L3 flash_hits and M1 glass_tap are replaced by §6.12). Hook B module:
`X.Plan([('L3', 74 / 30)])`, post `cuts=[(74 / 30, 0.5)]`.

### 6.9 Shot list (cinematic-director template)

World Bible lines (verbatim in every entry): palette, light logic, lens set, camera law, texture, forbidden = §6.1.

| Shot | Purpose | Size | Lens | Move (speed, easing) | Action (gesture-level) | Cast / Props | Light | Atmosphere | Uncomposed element | Dur (s) | Sound | Transition out | Anchor / Start-from |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| S0 | reveal | medium close-up bust | 85 mm | push +1.2 %/s linear | JD frozen mid-word, brows knitted, eyes on lens; the typing dots pulse above him | JD confused · MUMMY_BUBBLE | window backlight, rim camera-right; phone glow from below | dust motes in the window glow | one bokeh disc drifting past the bubble edge | 2.8 | dots tick, message pop, VO L1 | L3 cut (beat) | start_from S12 (loop) |
| S1 | inform | insert, card fills width | 50 mm | card POP up, handheld float 4 px | the card answers itself: "Video editor" types, "Shaadi wala?" pops | TRANSLATE_CARD | rim of the glass only, room defocused | motes | the caret blinks once after typing ends | 2.1 | card_slide, typing, pop | M6 (word carried) | — |
| S2 | change | same | 50 mm | float | the word becomes a gaudy wedding title; then "Motion designer" → "Cartoon?" and MOTION wobbles | TRANSLATE_CARD · PARODY 1, 2 | sparkles light the window only | sparkle dust | one sparkle lands outside the window frame | 2.8 | whoosh_by, shimmer, boings | L3 punch-in | start_from S1 |
| S3 | change | MCU bust | 85 mm | swap push 1.00→1.03 out_cubic | JD stares wide-eyed, mouth shut | JD shocked | as S0 | motes | — | 0.7 | whip + impact + tabla ge | L3 cut | — |
| S4 | change | insert | 50 mm | SLAM shake, 2 % push at 9.8 | "Content creator" is already typed; a red stamp slams across the answer | TRANSLATE_CARD · STAMP | glass rim; window darkened | — | stamp ink missing in patches | 2.8 | stamp impact + tabla ta | M3 swipe | — |
| S5 | change | insert | 50 mm | card B swipes in, then folds away rx 0→80° in_cubic | the honest answer sits there; loading dots; Mummy replies "Achha. Naukri kab lagegi?" | TRANSLATE_CARD · MUMMY_BUBBLE | card dims ×0.55 under the bubble | music dies (tape stop) | the empty lower card | 2.8 | ticks, killer ping in silence | L3 cut | — |
| S6 | change | MCU bust | 85 mm | swap push, then +1.2 %/s | JD holds a level stare at the lens; the reply still hangs above him | JD neutral · MUMMY_BUBBLE | window light dims −15 % from 15.4 | motes slow | — | 2.8 | soft thud; VO L5 | L3 cut | — |
| S7 | atmosphere | high angle on a table | 50 mm | locked; light band sweeps | a phone lies face-down; light crawls across the wood; the phone buzzes twice | PHONE_FACE_DOWN | window band GOLD 25 %; FLAME leak from under the phone | dust in the light band | a scratch in the wood grain | 2.8 | buzzes, pings accelerate | M2 hue bridge | — |
| S8 | move | insert, panel fills width | 50 mm | float; message stack pushes up | the family group floods; a reel is forwarded; relatives react; Mummy starts typing, stops, starts | FAMILY_CHAT · REEL_THUMB | panel rim; dots glow | motes | one reply bubble slightly wider than the rest | 8.4 | pings in key; drop-out from 27.3 | M1 push into dot 3 | — |
| S9 | reveal | wide on the sun | 100 mm macro → 50 mm (pull back) | pull back out_expo 0.5 s | the dot becomes the low sun; Mummy's bubble arrives with the answer | SUN_DISC · MUMMY_BUBBLE | the sun is the key | haze glow | — | 0.7 | payoff hit stack + warm chord | L3 punch-in | start_from S8 (match) |
| S10 | change (anchor) | MCU bust | 85 mm | swap push, then +1.2 %/s | JD's hand rests on his chest, eyes up-right, under Mummy's words | JD hand_on_chest · MUMMY_BUBBLE · SUN_DISC (hidden) | sun backlight, rim both sides | motes in the sun glow | — | 3.5 | VO L9 | L3 cut | **anchor (single image, f900)** |
| S11 | atmosphere | wide room | 50 mm | push 1 %/s | the sun sinks; the end card writes itself over the room | SUN_DISC | setting sun | motes | — | 3.5 | card cues, VO L10 | L3 cut | — |
| S12 | move (loop) | MCU bust | 85 mm | push +1.2 %/s (continues into f0) | Nani starts typing above the same confused JD | JD confused · MUMMY_BUBBLE ("Nani") | as S0 | motes | — | 0.7 | dots ticks; loop swell | loop seam | start_from S0 at t − 36.4 |

IDs: `packet.yaml` groups these 13 shots into scenes: S0 = S1-01, S1 = S2-01, S2 = S2-02, S3 + S4 = S3-01, S5 = S3-02,
S6 = S4-01, S7 = S5-01, S8 = S6-01, S9 = S7-01, S10 = S7-02, S11 = S8-01, S12 = S8-02, hook B = HB-01.

Rhythm map: 2.8 · 2.1 · 2.8 · 0.7 · 2.8 · 2.8 · 2.8 · 2.8 · 8.4 · 0.7 · 3.5 · 3.5 · 0.7 s (long, long, SHORT punch,
then the long chat build, the short match, the held payoff). Single image at 30.0 s (S10). Loop seam S12 → S0.
Hook (0-2 s): on screen = confused JD + "Mummy" typing, then the question; heard = "Sab se mushkil sawaal client nahi
poochta."; withheld = what she will make of the answer. Product moment = S9/S10: the job, named by Mummy as *cinema*.

### 6.10 Face plan (face-compositor → `beta_tum_karte_kya_ho_faces.py`)

All shots: `EYES = (540.0, 1280.0)` = the eye midpoint (`meta['eye_mid']`), `S0 = 0.92`, `PUSH = 0.012` per s;
`scale(t) = S0 * (1 + PUSH * (t - t_push0)) * (FA.swap_push(t, t_cut) if punch_in else 1)`. Draw
`K.draw(cv, hero, *EYES, scale=s, anchor=FA.anchor_at(plain, hero, meta['eye_mid']))` plus `FA.idle(t, seed)`
(≤ 0.4 % breathing, 0.5° sway, 3 px bob). Looks built once (`lru_cache`), then `FA.fade_open`.
Look A = `FA.rim_light(plain, FA.depth(n), light=(0.8, -0.5))`; look D = same light with `gain=1.4,
halo_strength=0.35, base=FA.cine_grade(plain)`. Phone glow (S0, S3, S6, S12): `K.radial(900, AMBER × 0.08)` 'add' at
(540, 1720), masked by the bust alpha (no relight of features).

| shot | frames | pose | look | t_push0 | punch-in | scale range | face rect (measured) | head top | bust bottom |
|---|---|---|---|---|---|---|---|---|---|
| S0 + S12 | f0-83, f1071-1091 | suit_confused | A (hero, cover) | −0.7 (S12 = t − 36.4) | no (continuous across the loop) | 0.9200-0.9583 | (368, 1119)-(697, 1556) | 997 | ≥ 2007 |
| S3 | f231-251 | suit_shocked | D | 7.7 | yes (7.7) | 0.920-0.955 | (369, 1121)-(690, 1542) | 998 | ≥ 1999 |
| S6 | f420-503 | suit_neutral | D | 14.0 | yes (14.0) | 0.920-0.979 | (367, 1117)-(692, 1546) | 976 | ≥ 1959 |
| S10 | f861-965 | suit_hand_on_chest | A (payoff hero) | 28.7 | yes (28.7) | 0.920-0.987 | (365, 1139)-(652, 1524) | 1035 | ≥ 2049 |

Limits checked in the proof: display scale ≤ 0.987 (cap 1.0); bust bottom always ≥ 1926 (never visible); face x ≤
697 (like column clear), face bottom ≤ 1556 (bottom 300 px clear); pose time: confused 2.8 + 0.7 across the loop =
3.5 s, shocked 0.7, neutral 2.8, hand-on-chest 3.5 (all ≤ 3.5); no mirroring; no cross-dissolve; no lip motion.
Skin: human-realism / photo-realism rules (texture kept, no smoothing; colorist skin protection 0.70). Captions pass
the head rect `(head_x0, head_top, head_x1, 1920)` as an avoid rect; UI never overlaps the face rect.

### 6.11 Captions plan (`snake_captions.py`; caption-designer prepares the words, the module draws)

```python
CAP_HOOK = SC.Captions(words_L1, band='upper', y=880, avoid=lambda t: AVOID(min(t, 2.79)))      # version A only
CAP_BODY = SC.Captions(words_L2_to_L10, band='upper', y=880, avoid=lambda t: AVOID(max(t, 2.8)),
                       hide=[(16.85, 18.2), (32.2, 36.4)])
draw: if t < 2.8: CAP_HOOK.draw(cv, t, opacity=1 - K.ramp(t, 2.6, 2.8, 'in_cubic'))   # never crosses the splice
      else:       CAP_BODY.draw(cv, t, opacity=1 - K.ramp(t, 32.0, 32.25, 'in_cubic'))
hook B: no CAP_HOOK at all.
```
`AVOID(t)` returns: S0 head rect + bubble (147, 280)-(933, 740) + chip (147, 232)-(320, 272) + POV (600, 235)-(1000,
270); card scenes and S8: card (90, 296)-(990, 1176) + POV; S3/S6/S10: head rect (S6 also the killer bubble (150,
252)-(930, 520) until 15.3); S7: chip (310, 302)-(770, 378) + phone (390, 640)-(690, 1160); S9: payoff bubble (147,
280)-(933, 790) + chip + sun (430, 1150)-(650, 1370); S10: payoff bubble + chip + head rect.
Keywords (one per line, chunker gives ≤ 1 per chunk): L2 *translation*, L3 *ulta*, L4 *Seedha*, L5 *haar*, L7 *reel*,
L8 *nazar*; L1 and L9 none (a lockup keyword is on screen), L6/L10 hidden. No caption SFX.
Proof with synthetic timings: `cap.check() == []` for both objects; chunks land at baseline ≈ 880 above JD (S0, S6,
S10) and ≈ 1310 under the card (UI scenes), all at scale 1.0. Re-run `check()` on the real `words.json`.

### 6.12 SFX cue list (sound-designer → `beta_tum_karte_kya_ho_sfx.py`; `epic_sfx.register()` first)

55 cues (1.5/s, 29 designed events ≥ −8 dB = 0.8/s); no instant has > 3 starts; every name verified in `A.names()`.
`pitch_to(880)` = the bible §4.2 helper (A5). notif_ping pitch 1.1225 = A6, 1.4983 = D7 (key D minor; Sa = D:
`tabla_hit pitch 1.0` = D4). Duck and carve with the shared `sfx_jawad.fit_under_vo(cues, words_json)` (the bible
§4.1 helper; `hero='raise'`; none of these cues is a HERO sound) against the real `words.json`. Call
`epic_sfx.register()` (and `sfx_jawad.register()` if its helpers are used) before `A.mix`. Render with
`--no-sfx-build` (TOOLKIT pitfall 14).

| t (s) | f | name | params | align | gain dB | under VO | event |
|---|---|---|---|---|---|---|---|
| 0.0000 | 0 | impact_soft | {} | hit | −8 | | loop landing (end card swell ends at 36.4) |
| 0.0000 | 0 | ui_tick | {} | hit | −12 (hp 5000) | | typing dots (0.3 s rhythm from the pre-roll) |
| 0.3667 | 11 | notif_ping | pitch 1.1225 | hit | −4 | yes | Mummy's message lands |
| 3.1000 | 93 | card_slide | dur 0.42 | hit | −6 | yes | translate card lands |
| 3.2667 | 98 | typing | n 12, cps 20 | hit | −14 | yes | "Video editor" |
| 4.2000 | 126 | pop | pitch_to(880) | hit | −4 | | "Shaadi wala?" |
| 4.9000 | 147 | whoosh_by | dur 0.8, direction 1 (pan +0.1) | hit | −4 | | M6 fastest point |
| 4.9000 | 147 | shimmer | dur 1.2 | hit | −8 | | wedding sparkle wipe |
| 5.3000 | 159 | sparkle | {} | hit | −8 | yes | M6 landing |
| 6.3333 | 190 | typing | n 15, cps 30 | hit | −16 | yes | "Motion designer" |
| 7.0000 | 210 | bubble_pop | pitch 1.0 | hit | −2 | | "Cartoon?" + boing 1 |
| 7.3667 | 221 | bubble_pop | pitch 0.8 | hit | −6 | | boing 2 |
| 7.6667 | 230 | whip | direction 1 | hit | −6 | | punch-in (c3 − 1 f) |
| 7.7000 | 231 | impact_soft | {} | hit | −2 | | punch-in |
| 7.7000 | 231 | tabla_hit | stroke 'ge', pitch 1.0 | hit | −4 | | comic bass bend |
| 8.4000 | 252 | impact_soft | {} | hit | 0 | | stamp SLAM (bar 3) |
| 8.4000 | 252 | tabla_hit | stroke 'ta' | hit | −6 | | dry slap |
| 8.4000 | 252 | swish_small | {} | hit | −10 | | card returns |
| 11.2000 | 336 | whoosh_fast | direction −1 (pan −0.4) | hit | −3 | yes | M3 swipe |
| 11.5000 | 345 | card_slide | dur 0.3 | hit | −8 | yes | M3 landing |
| 12.1333 | 364 | ui_tick | {} | hit | −14 | | loading dots |
| 12.6000 | 378 | notif_ping | pitch 1.1225 | hit | 0 | | KILLER (music silent) |
| 12.6000 | 378 | impact_soft | {} | hit | −8 | | killer weight |
| 13.6667 | 410 | swish_small | {} | hit | −8 | | card folds |
| 14.0000 | 420 | impact_soft | {} | hit | −10 | | cut to neutral |
| 15.0000 | 450 | swish_small | {} | hit | −14 | yes | killer bubble exits |
| 16.8000 | 504 | notif_ping | pitch 1.1225, buzz 1 | **start** | −10 | (ping 17.2 yes) | buzz 1 (haptic from 16.8) |
| 16.8000 | 504 | pop | pitch_to(880) | hit | −10 | | chip |
| 18.2000 | 546 | notif_ping | pitch 1.1225, buzz 1 | **start** | −10 | | buzz 2 |
| 18.9000 | 567 | notif_ping | pitch 1.4983 | hit | −12 | | ping |
| 19.2667 | 578 | notif_ping | pitch 1.1225 | hit | −12 | | ping |
| 19.4333 | 583 | notif_ping | pitch 1.4983 | hit | −12 | | ping |
| 19.6000 | 588 | reverse_swell | duration 0.3 | hit (ends) | −6 | | M2 |
| 19.6000 | 588 | shimmer | dur 1.0 | hit | −10 | | M2 |
| 19.6000 | 588 | whoosh_fast | direction 1 | hit | −8 | | flood scroll |
| 21.7000 | 651 | notif_ping | pitch 1.1225 | hit | −6 | yes | reel forwarded |
| 22.4000 | 672 | notif_ping | pitch 1.4983 | hit | −8 | yes | "Kamaal!" |
| 23.1000 | 693 | notif_ping | pitch 1.1225 | hit | −8 | yes | "Wah!" |
| 25.2000 | 756 | pop | pitch_to(880) | hit | −10 | yes | typing pill |
| 25.2000 | 756 | ui_tick | {} | hit | −14 | yes | dots |
| 26.6000 | 798 | ui_tick | {} | hit | −14 | yes | typing resumes |
| 27.3000 | 819 | ui_tick | {} | hit | −16 | | held breath (drop-out) |
| 28.0000 | 840 | tabla_hit | stroke 'dha', pitch 1.0 | hit | 0 | | PAYOFF (M1 tonal hit) |
| 28.0000 | 840 | sub_drop | dur 1.6 (lp 120) | hit | −6 | | payoff sub |
| 28.0000 | 840 | impact_soft | {} | hit | −3 | | payoff body |
| 28.2333 | 847 | shimmer | dur 1.5 | hit | −8 | | *cinema* starts rising |
| 28.7000 | 861 | swish_small | {} | hit | −12 | yes | punch-in |
| 31.8333 | 955 | swish_small | {} | hit | −12 | yes | lockup exits |
| 32.3000 | 969 | swish_small | {} | start | −12 | | `card.cues`: ring draw-on |
| 32.7700 | — | shimmer | {} | hit | −10 | yes | `card.cues`: keyword |
| 32.9500 | — | glass_tap | {} | hit | −12 | yes | `card.cues`: ring closes |
| 35.7000 | 1071 | pop | pitch_to(880) | hit | −10 | | Nani pill |
| 35.8000 | 1074 | ui_tick | {} | hit | −15 | | dots |
| 36.1000 | 1083 | ui_tick | {} | hit | −15 | | dots |
| 36.4000 | 1092 | reverse_swell | duration 0.8 | hit (ends) | −8 | | `card.cues`: loop swell → f0 |

Version B cue set = the hook-B cues of §6.3 (bubble_pop 0.0 −4, impact_soft 0.0 −8, bubble_pop 0.7 pitch 0.8 −8,
swish_small 1.4 −10, tabla_hit 'na' 2.1 −8, notif_ping A6 2.4667 −6) + every A cue with t ≥ 2.8 (A's three hook cues
are dropped). Both sets keep the end-card swell that ends on 36.4.

Beds: `BED = [dict(name='room_tone', t0=0, t1=36.4, gain_db=0, fade=0.3), dict(name='desi_city', t0=0, t1=27.3,
gain_db=-8, fade=0.3), dict(name='desi_city', t0=28.0, t1=36.4, gain_db=-8, fade=0.004)]`, `BED_GAIN_DB = -32`
(room tone carries the music silences 12.6-14.0 and 27.3-28.0 at ≈ −45 LUFS). Drop-out: no SFX starts 27.31-27.99.

### 6.13 Music plan (music-supervisor → `beta_tum_karte_kya_ho_music.py` + `MUSIC.md` in this folder)

Style: `lofi_desi` re-arranged on `epic_music` building blocks (`EM.Song(36.4, 600/7, 'D', seed)`, `EM.epiano`,
`EM.kick`, `EM.clap`, `EM.bass808`, `s.sfx('drums', 'tabla_hit', ...)` with `EM.KAHARWA` 8ths, swing 0.06 beat,
`E._crackle` vinyl 0.02). **Not** `EM.render('lofi_desi')`: it adds harmonium swells and a sitar lead (second desi
voice), a tape stop at its end and a 1.2 s fade-out (breaks the loop). Key D minor, Sa = D. One desi voice: tabla.

| bars | t (s) | chord(s) | layers | notes |
|---|---|---|---|---|
| 0 | 0.0-2.8 | Dm9 | tabla theka + EP | hit on frame 0 = EP chord + tabla 'dha' |
| 1-3 | 2.8-11.2 | Bbmaj7, Gm9, A7b9 | + soft kick on 1 and 2.5 (lp 1800, −4 dB) | comedy groove, no clap, no 808 |
| 4 | 11.2-12.6 | Dm9 | groove; `tape_stop_fx(music, 12.15, dur=0.45)` | music dies INTO the killer line (silent from 12.6) |
| — | 12.6-14.0 | — | silence (room tone only) | |
| 5-6 | 14.0-19.6 | Bbmaj7 / Gm9 (2 beats) A7b9 (2 beats) | EP only, lp 1500, −6 dB; single tabla 'tin' at 16.8 | sad-comic |
| 7-9 | 19.6-27.3 | Dm9, Bbmaj7, Gm9 | full: tabla + kick (1, 2.5) + clap (2, 4) + 808 root + EP | the group floods (re-hook 2 drop) |
| — | 27.3-28.0 | — | gate after the reverbs, 4 ms fades | the drop-out (1 beat) |
| 10 | 28.0-30.8 | D major add9 (D2 / D3 F#3 A3 E4) | warm EP + soft pad struck at 28.0, held; tabla re-enters −6 dB at 29.4 | the single warm chord on the payoff |
| 11 | 30.8-33.6 | Bbmaj7 | tabla + EP, no kick | under VO L9 / end card |
| 12 | 33.6-36.4 | A7b9 | tabla + EP; thin to EP + one 'tin' at 35.7 | dominant resolves into bar 0's Dm9 on the loop |

No tail fade; render DUR + 2.0 s and fold the overhang (reverb tails) onto the head (circular), then cut to exactly
36.4 s. Stem −18 LUFS (VO present), ≤ −3 dBTP, `level_rider(amount=0.3)`. Verify `EM.beatgrid`: tempo 85.71 ± 0.1,
|phase| ≤ 5 ms. Max momentary loudness of music + SFX (VO excluded) falls in 28.0-28.4 s (the payoff is the loudest
moment); the 19.6-27.3 groove stays ≥ 3 LU below it.

### 6.14 Mix and loudness (music-supervisor run 2: `epic_mix.mix_reel`)

`mix_reel('beta_tum_karte_kya_ho', dur=36.4, vo=VO_A, sfx=SFX_STEM, music=MUSIC, out_dir=<reel audio>, vo_offset=0)`
and the same with `VO_B` (version B), each also rendered without music (the no-music mix = VO + SFX only). Targets:
−14.0 ± 0.5 LUFS integrated, TP ≤ −2.0 dBTP (wav) / ≤ −1.5 after AAC, LRA 5-9 LU, VO stem −16 LUFS, speech ≥ 8 LU
above music (median over voiced frames), SFX inside VO windows ≥ 6 LU below VO. Mux with `epic_mix.mux` (two-pass
loudnorm, verify).

### 6.15 3D props: **none** (SLATE §3.4). No work order for blender-3d-artist.

### 6.16 Grade and finish (colorist)

`gold_hour` via `G.tx_finish(..., rays=0.0)` everywhere (binding). Skin protection default 0.70 on the four suit
cut-outs; wedding chrome stays ember-gold (hue ≤ 45°); hue budget 'share' (red-orange ≥ 60 % of saturated pixels);
YMIN 16-22; frame 0 YAVG ≥ 40 (limited range; proof frame measured 45.2), face mean ≥ 70 (proof 85).

### 6.17 Cover, post copy, label, posting

- **Cover:** f30 (1.000 s) without captions (module `cover()` = `draw(1.0)` minus the caption layer, same post).
  3:4 crop y 240-1680 holds the bubble (280-740) and the face (1119-1556). Proof: `brief_proof/A_cover_f030.jpg`.
- **IG caption** (line 1 = 50 characters, measured):
  ```
  Beta, tum karte kya ho? Har video editor ka sawaal
  POV: har desi ghar. Job title kuch bhi bolo, Mummy ka translation kuch aur hi hota hai.
  Aap ki mummy aap ke kaam ko kya kehti hain?
  #videoeditor #editorlife #desifamily #jawadmp4
  ```
- **Hashtags:** #videoeditor #editorlife #desifamily #jawadmp4 (4, incl. #jawadmp4).
- **Comment prompt** (pin it): "Aap ki mummy aap ke kaam ko kya kehti hain?"
- **AI label:** "AI info" ON at upload (synthetic voice; possibly AI-generated character imagery).
- **Audio name:** "Original audio · Beta, tum karte kya ho? · @jawad_mp4"; upload the full mix; keep the no-music mix for an in-app song.
- **Posting (SLATE §4 hypothesis, low confidence):** slot 4, Thu 22 Oct 2026, 7:00 PM PKT = 7:30 PM IST; hook A public,
  hook B as a Trial Reel if the account is eligible (1,000+ followers, unconfirmed).

---------------------------------------------------------------------------------------------------------------

## 7. Engineering contract

| file (pipeline/jawad_reels/) | owner | contents |
|---|---|---|
| `beta_tum_karte_kya_ho.py` | motion-timeline-builder | `DUR = 36.4`, `LOOK = 'gold_hour'`, `BPM = 600 / 7`, `FPS = 30`, `SPLICE_F = 84`; scenes S0-S12, `PLAN`, `draw(t)`, `post(cv, t)`, `samples(t)`, `prewarm()`, `cues()` = delegate to the sfx module, `frame(t, version='A')`, `cover()`, `blocks(t)` (debug: active text blocks + bboxes for QA) |
| `beta_tum_karte_kya_ho_hookb.py` | motion-timeline-builder | `DUR = 2.8`; f0-f73 hook B scene, f74-f83 = main `frame(t, 'B')` (no caption layer); own `cues()` for B |
| `beta_tum_karte_kya_ho_ui.py` | motion-timeline-builder | pill / bubble / chip / translate card / chat panel / stamp builders (cached) |
| `beta_tum_karte_kya_ho_parody.py` | motion-timeline-builder | P1-P3 window renderers (type3d + ui only, brand palette, ≤ 1.4 s each) |
| `beta_tum_karte_kya_ho_faces.py` | face-compositor | `FACES` table (§6.10), `look(name)`, `draw_face(cv, shot, t)`, `head_rect(shot, t)` |
| `beta_tum_karte_kya_ho_sfx.py` | sound-designer | `cues()` (§6.12), `BED`, `BED_GAIN_DB`, `build` CLI (A and B cue sets) |
| `beta_tum_karte_kya_ho_music.py` | music-supervisor | §6.13 arrangement, writes wav + stems + json + png |
| `beta_tum_karte_kya_ho_vo.py` | hinglish-scriptwriter | assembles processed takes at their slots → VO A / B wavs + `words.json` |
| `vo/beta_tum_karte_kya_ho_script.md`, `vo/beta_tum_karte_kya_ho.json` | hinglish-scriptwriter | script, token table, timing table |

Rules: `import jawad_kit` first, then `jawad_grade as G`, `jawad_tx as X`, `snake_captions as SC`, `endcard as E`,
`faces as FA` (sys.path += charsheet/tools). Shared modules are read-only. `draw(t)` pure; all sprites in
`lru_cache`d `assets()`; never per-frame rebuilds. Outputs: `<WS>/out/beta_tum_karte_kya_ho/` is a symlink to
`workspace/jawad_reels/beta_tum_karte_kya_ho/out/` (also `..._hookb`); audio and VO intermediates in
`workspace/jawad_reels/beta_tum_karte_kya_ho/audio/`; keep the reel workspace < 2 GB, delete render intermediates.
All heavy jobs through `pipeline/jawad_reels/tools/heavy.sh` (2 global slots, nice 10, 2 threads):

```bash
cd /home/user/100/pipeline/jawad_reels
tools/heavy.sh python3 render.py beta_tum_karte_kya_ho --sheet 24 --samples 1 --workers 1
tools/heavy.sh python3 render.py beta_tum_karte_kya_ho --stills 0,0.367,1.0,4.9,8.4,12.6,14.5,19.6,28.0,30.0,34.5,36.367
tools/heavy.sh python3 render.py beta_tum_karte_kya_ho --range 27.0 29.0 --workers 1          # M1 + payoff
tools/heavy.sh python3 beta_tum_karte_kya_ho_sfx.py build
tools/heavy.sh python3 beta_tum_karte_kya_ho_music.py
tools/heavy.sh python3 render.py beta_tum_karte_kya_ho --workers 2 --no-sfx-build --audio <version A full mix wav>
tools/heavy.sh python3 render.py beta_tum_karte_kya_ho_hookb --workers 1 --no-sfx-build --audio <version B full mix wav, first 2.8 s>
```
Version B splice (delivery-packager): concat(hookb frames 0-83, master A frames 84-1091) re-encoded once with the
delivery settings + version B's full mix; verify 1,092 frames. Gates before the master (SLATE §4): the translate card with one
parody as a still (f160) and a `--range 4.4 6.4` clip.

## 8. QA acceptance checklist (reel-specific, measurable)

1. ffprobe A and B: 1080x1920, 30/1 fps, 1,092 frames, 36.400 s. Frame-accurate splice: SSIM(B[f], A[f]) ≥ 0.98 for
   f = 84, 85, 500, 1091 and SSIM(B[84], A[84]) > SSIM(B[84], A[83]) (no off-by-one).
2. Frame 0 (A): JD + "Mummy" pill + POV label present; YAVG ≥ 40; face-rect mean ≥ 70; no frame in f0-f9 is > 70 %
   near-black.
3. H1 legible at f11: keyword-box mean luma at f11 ≥ 90 % of its value at f30. Hook B: H2 present at f0.
4. VO: first voiced onset ≤ 0.30 s (A and B); L1 ends ≤ 2.75 s; L1B ends ≤ 2.45 s; every line inside its slot ±
   0.15 s; total words A ≤ 60.
5. Safe zones from `blocks(t)` at 5 fps: all text bboxes in x 70-1010, y 230-1480 (end-card signature 1563-1587
   allowed), none at x > 930 for y 1050-1700, none below y 1620; widths ≤ 940 (≤ 780 in y 1050-1700).
6. ≤ 2 text blocks at every frame (`blocks(t)` against §6.6); captions hidden in 16.85-18.2 and 32.2-36.4 and absent in
   hook B; no caption keyword while H1 or P1 is on screen.
7. `CAP_HOOK.check() == []` and `CAP_BODY.check() == []` on the real words; hook captions fully transparent at f84.
8. Reading holds per §6.5 (stamp settled ≥ 1.97 s, killer ≥ 1.63 s, P1 ≥ 1.97 s, end card hold ≥ 1.5 s).
9. Faces: max display scale ≤ 1.0 (expected 0.987); bust bottom ≥ 1926 every frame; eye midpoint within 6 px of
   (540, 1280) in every JD shot; per-pose on-screen time ≤ 3.5 s (incl. across the loop); halo ring ≤ +6 code
   values; no face pixel under UI.
10. Transitions: exactly 4 features (M6, M3, M2, M1), spacing ≥ 168 frames; cut rule (frame c−1 all A, c all B) at
   all 12 cuts; M1 HoughCircles f839 vs f840 centre ≤ 2 px, radius ≤ 2 %; M3 card velocity f335 vs f336 within 10 %;
   M2 FLAME highlight present on f587 and f588.
11. Loop: `E.seam_report` ok; mean |Δ| last→first frame ≤ 1.5 × a normal frame step; the only text difference is
   the chip word (Nani → Mummy); audio: no gap at the seam (−40 dBFS RMS or louder across f1091-f0).
12. Finish: every post call passes `rays=0.0` (code check) and f1030 shows no streaks around the monogram (side by side
   with `brief_proof/end_34p5.jpg`); the sun never clips white (max 8-bit value inside the disc < 250 on f850).
13. Audio: −14 ± 0.5 LUFS, TP ≤ −2.0 dBTP wav and ≤ −1.5 after AAC, LRA 5-9 LU; speech ≥ 8 LU over music; SFX in VO
   windows ≥ 6 LU below VO; music bus ≤ −60 dBFS in 12.62-13.98 and 27.31-27.99 while room tone measures −45 ± 5
   LUFS short-term; music RMS drops ≥ 30 dB from 12.10 to 12.62 (tape stop); max momentary (music + SFX) in
   28.0-28.4; beatgrid 85.71 ± 0.1, |phase| ≤ 5 ms; every hero cue (4.9, 7.7, 8.4, 11.2, 12.6, 19.6, 28.0) within ±1
   frame of its picture event (`qa_measure.py cues`).
14. Palette / grade: red-orange ≥ 60 % of saturated pixels; YMIN 16-22; IVORY type never pure white; no saturated
   hue 90-170° (green / WhatsApp) above 0.2 % of any frame.
15. Brand: no hearts, shehnai, ERROR dialog, real logos, Mummy's face or hands, centred ring with rays; replies
   religion-neutral; POV label visible in the hook and every UI scene; underline used exactly twice (P1, E1).
16. Delivery: 2-pass ~22 Mbps + faststart < 100 MB, AAC 320k; CRF 14 master; stems 48 kHz 24-bit; cover = f30
   without captions; preview < 30 MB; reel workspace ≤ 2 GB (`du -sh`).

## 9. Agent work orders

| # | agent | order | inputs → outputs | gate |
|---|---|---|---|---|
| 1 | hinglish-scriptwriter | finalise L1-L10 + L1B (§6.7) in Roman + Devanagari with token table; run the 5-word pronunciation test; after the takes, measure and assemble | §6.7 → `vo/beta_tum_karte_kya_ho_script.md`, `.json`, `beta_tum_karte_kya_ho_vo.py`, VO A/B wavs, `words.json` | slots ± 0.15 s |
| 2 | viral-strategist | script gate on the final lines (hook ≤ 7 words by 2.7 s, re-hooks, send line) | script → `viral/` note | pass/fix |
| 3 | lead (Higgsfield TTS) | generate 11 takes with Vlad per `vo_config.json`, ≤ 30 credits | Devanagari lines → `workspace/brand_reels/tts/hf_dl/beta_tum_karte_kya_ho/` | jobs_wait, no blind resubmits |
| 4 | face-compositor | build looks A/D for the 4 poses, `beta_tum_karte_kya_ho_faces.py` per §6.10, stills at each shot start / mid / end and ±0.4 s of each punch-in | cut-outs → faces module + stills | halo, eye offset, scale |
| 5 | colorist | verify `gold_hour` with `rays=0.0` on the proof stills and the first sheet; skin on 4 poses; hue budget; frame-0 luma | stills → `GRADE` note in this folder | §8 items 2, 12, 14 |
| 6 | motion-timeline-builder | build the main module + hook B + `_ui` + `_parody` per §6.2-6.11 and §7; gates: f160 still and 4.4-6.4 range first | brief → modules, sheets, stills | §8 items 1-12 |
| 7 | caption-designer | turn `words.json` into the two caption objects' inputs (keywords, hides), run `check()`, export SRT | words.json → `captions/`, SRT, check report | `check() == []` |
| 8 | sound-designer | `beta_tum_karte_kya_ho_sfx.py` per §6.12 (A and B cue sets), spectrogram + ebur128 report | cue table → SFX stems | names, ≤ 3 starts, timing |
| 9 | music-supervisor | run 1: `MUSIC.md` + `beta_tum_karte_kya_ho_music.py` per §6.13; run 2: full and no-music mixes for versions A and B per §6.14 | music + stems → mix wavs | §8 item 13 |
| 10 | motion-qa-reviewer | two lenses (copy/layout/safe zones; motion/transitions/finish/audio sync) + skeptical verifier per finding | masters → `qa/` report | §8 all |
| 11 | delivery-packager | encodes A and B (splice at f84), cover, stems, preview, verify | masters → `reel/jawad_reels/` | §8 items 1, 16 |
| — | blender-3d-artist | **none** (no 3D in this reel) | — | — |

Order: 1 → 2 → 3 → (4, 5, 6 on placeholder VO timings in parallel) → 7 → 8 → 9 → preview → 10 → fixes → 11.

## 10. Changes from SLATE (and why) · open questions

1. **Loop gag:** Nani's bubble shows her chip and the typing dots, not the question text. The end card holds its CTA
   to 36.04 s, 5 words cannot be read in 0.7 s, and frame 0 completes the question (by f11), so the seam differs only
   by the chip word and the loop is seamless.
2. **Gag 3 at 8.4 s (bar 3) instead of 9.8 s:** the 5-word stamp needs ≥ 1.97 s settled before the M3 window opens at
   10.9 s; the card returns pre-filled and the stamp slams on the downbeat (the three gags accelerate: typed, typed
   fast, instant). The stamp's animated parody (SLAM, shake, ink settle) runs 8.4-9.8 s = 1.4 s (SLATE's parody cap);
   the settled stamp then stays on the card until the swipe so it can be read. The killer bubble now persists over the
   first second of the neutral shot (reading 2.4 s).
3. **Card B arrives pre-filled** with "Brands ke liye cinematic reels" (reading 2.37 s).
4. **Phone buzz:** buzz 1 at 16.8 s with the chip (SLATE), then pings accelerate 18.2-19.43 s into the M2.
5. **`rays=0.0`** on gold_hour for this reel (artefact and banned radial burst measured in the proof); request filed in
   `SHARED_REQUESTS.md`.
6. **VO:** SLATE's locked lines kept verbatim; L2-L4, L6, L8, L10 are new (universal POV); L2 is SLATE's example line
   shortened to fit 1.2 s.
7. **Music:** lofi_desi re-arranged per reel (no harmonium/sitar, no end tape stop or fade); the tape stop moves into
   the killer line as SLATE's sting asks.

Open questions (defaults applied, none blocks): AI label ON; "Mummy" (not "Ammi"); relatives' chips Chachi / Mamu /
Chachu OK?; parody fonts Cinzel / Bungee (OFL) OK?; Trial Reels eligibility unknown (hook B is produced anyway);
house spelling = prior SRT.
