# ref1 — "Showreel 2026" (Nour Aldin Seyam): a craft teardown

> **Read this first.** We study this reel for its craft only. Jawad's page is different from this reel: different
> brand (orange to red on black), different format (vertical 9:16, a Hinglish / Roman Urdu voiceover story),
> different audience (Pakistan + India). Nothing here is to be copied: not the layouts, copy, logos, illustrations,
> landmarks, characters, green / blue palette or music. Section 7 turns each technique into an original, on-brand
> device built with the Reels Studio toolkit or Blender. Do not use the Organic Fostering / Floret looks
> (`neon` / `amber` / `airy`) or their props for these devices.

Analyst role: reels-studio `reference-analyst`. Every number below comes from a command; anything marked
*(observed)* comes from looking at frames, and *(inferred)* marks an inference.

---

## 1. Source

| field | value |
|---|---|
| file | `/home/user/100/workspace/brand_reels/refs/ref1.mp4` (supplied locally, full video, analysed 2026-10-08) |
| duration | 73.86 s container; 2214 video frames at 30 fps (73.8 s); audio ends at ~72.0 s |
| video | H.264, **1276x718 (16:9, horizontal)**, 1.36 Mb/s |
| audio | AAC 44.1 kHz stereo, 72 kb/s |
| genre | motion-design showreel: a montage of client pieces (SaaS UI, 3D type, glass icons, explainer illustration, AI-image collage) bookended by the author's name lockup |
| access / confidence | full video, high confidence on visuals and measured audio. Music identity unknown; nobody listened (all audio claims are measured) |

Working media (git-ignored) is in `/home/user/100/workspace/brand_reels/refs/ref1_analysis/`:
`sheets3/s_01..14.jpg` (4x4 contact sheets, 3 fps, 360 px tiles, timestamped), `strips/tr_00..05.jpg`
(10-frame strips around every transition), `keyframes/k_*.jpg` (full-res frames), `hook_10fps.jpg`, `end_8fps.jpg`,
`spec_annot.png` (spectrogram + RMS + onsets + edit points), `spec_hook.png`, `spec_dive.png`, `spec_end.png`,
`audio_analysis.json`, `framestats2.json` (per-frame luma / colour / diff), `flow.json` (optical flow),
`whisper_small.json`, `cuts_0.2/0.3/0.4.txt`, `edits_manual.txt`. The 3 fps frames are in `../ref1_frames/`.

---

## 2. Numbers

| metric | value | how |
|---|---|---|
| ffmpeg scene cuts | 54 / 49 / 42 at thresholds 0.2 / 0.3 / 0.4 | `select='gt(scene,T)',showinfo` |
| merged cut clusters (0.3, within 0.4 s) | 29 edits | the 49 raw detections include strobe flicker inside transitions |
| **edit points (verified on strips)** | **42 edits → 43 shots** | scene 0.3 plus the soft morphs / wipes it misses |
| shot length | **mean 1.72 s, median 1.57 s**, min 0.50 s, max 5.79 s (end card) | |
| edits per 10 s | 5.7 | |
| cuts in first 3 s | **0** (only a 2-frame poster flick at 0.07 s; the first real transition is at 4.47 s) | |
| by section | intro 0–7.47: 1 edit (3.7 s per shot) · act 1 7.47–37.47: 16 edits (1.76 s) · act 2 37.47–68.07: 22 edits (1.33 s) · end card 5.8 s | |
| shot length in beats | median 3.3 beats at 127 BPM | |
| **tempo** | **127 BPM** | comb fit on the kick-band and full onset envelopes (both best at 127.0). Cross-check: a narrow synth tone at 1.87 kHz pulses at 8.46 Hz (= 16ths at 127) and 4.23 Hz (= 8ths) |
| onsets | 366 (spectral flux), about 5 per s; density per 2 s: 2–7 in the intro, 11–15 in act 1, 7–13 in act 2 | |
| cut-to-beat sync | hard cuts within 1 frame (34 ms) of any onset: 48 % (random-time null 52 %); within 67 ms of a top-15 % onset: 20 % (null 16 %) | **no measurable accent sync**. The 16th-note groove is so dense that any cut "feels" on beat |
| loudness | **−14.2 LUFS integrated**, LRA 6.7 LU, **true peak +0.3 dBTP** (overs) | `ebur128=peak=true` |
| stereo width (side/mid RMS) | intro 0.57 · body 0.29–0.31 · outro 0.66 | wide atmospheric bookends, narrow driving body |
| speech | **none**. Silero VAD: 0 speech regions at thresholds 0.5 and 0.35 | see section 4 |
| frame polarity | 45 % dark frames (mean luma < 60), 26 % light (> 170), 29 % mid | 2 fps sampling |
| black level | 1st-percentile luma of dark frames = 0 (true crushed black, no lifted blacks) | |

---

## 3. Palette (k-means in OpenCV, 2 fps frames)

**Whole reel (k=8):** `#060709` 39.1 % (background black) · `#EFF0F6` 17.6 % (white backgrounds of light scenes) ·
`#C2C3B9` 11.0 % (paper grey, illustration) · `#483941` 8.7 % (plum shadow) · `#9F6161` 7.8 % (dusty red, illustration) ·
`#07288D` 5.9 % (cobalt, fintech scene) · `#3BB7D1` 4.9 % (cyan glow) · `#C9B142` 4.9 % (ochre / gold).

**Per section, which matters more:**

| section | clusters | reading |
|---|---|---|
| intro + end card (author brand) | `#040306` 84.8 % bg · `#0C2B1D` 8.0 % glow falloff · `#156342` 4.8 % glow body · `#737E7C` 1.2 % chrome shadow · `#C7CFCE` 0.8 % chrome type · `#34CF91` 0.5 % mint accent | **85 % black, about 13 % glow, under 3 % type and accent.** The brand frame is mostly darkness |
| orange rim-light UI, 18.5–22.8 s | `#040102` 75.6 % · `#231105` 16.1 % · `#50290C` 6.3 % · `#C7905A` 1.0 % · `#5D5C8A` 1.0 % | **the scene closest to Jawad's palette.** 76 % near-black, 22 % deep ember brown glow, 1 % hot highlight |
| act 1 (SaaS / 3D) | `#050408` 48 % · `#F7F2F9` 13 % · `#0931A4` 9 % · `#071A60` 7 % · `#B1CDDE` 6 % · `#1CB3E9` 6 % … | dark base, **one saturated hue family per scene** (green → blue → lime → orange → cobalt → violet) *(observed)* |
| act 2 (illustration) | `#EFF1F5` 27 % · `#D3C6B7` 16 % · `#59354C` 14 % · `#A75859` 14 % · `#7DBDB6` 9 % · `#DEA660` 9 % · `#191F10` 8 % · `#8CC50A` 3 % | light, warm, flat, varied; off-brand for Jawad |

Grade per section (mean CIE L\*a\*b\*): intro L\* 8 (a −3, b 0); act 1 L\* 31–37 (the cobalt scenes have b −25);
orange UI L\* 4 (a +2.6, b +3.2); illustration L\* 66 (a +6, b +10, warm); end card L\* 4.

---

## 4. Transcript and audio

### Transcript: no voiceover, no lyrics, music and SFX only
- faster-whisper `small`, int8, word timestamps, auto language: detected **`nn` with p = 0.38** (a meaningless guess)
  and returned **one hallucinated segment**, `[66.90–69.24]`, of phonetic garbage
  ("ən ʻɸər ʻɲɪn ʻɹəm …"), avg_logprob −0.93, **no_speech_prob 0.82**. Nothing else was transcribed.
- Silero VAD (the faster-whisper VAD): **0 speech regions** at threshold 0.5 and at 0.35.
- **Verdict: instrumental music bed plus designed SFX. No VO, no sung words.** The only "words" in the reel are on
  screen: English and Arabic labels, about 6 words at most at once, apart from fine print.

### Music and SFX layers (from the spectrograms `spec_annot.png`, `spec_hook.png`, `spec_end.png`)

| time | measured | inferred layer |
|---|---|---|
| 0.0–2.0 | 85 % rolloff at 100–140 Hz, sub < 100 Hz at −17 to −20 dB, a bright transient at 0 | deep sub-boom / drone on the black open; the letters land on it |
| 2.0–2.5 | rolloff jumps to 3 kHz, broadband | **whoosh**, on the brush slash through "SHOW" |
| 2.5–4.0 | **> 8 kHz energy falls to −87 to −94 dB**, sub falls to −34 to −40 dB | **hard low-pass "underwater" hold**: tension while the title card holds |
| 4.0–5.0 | air returns (−40 dB), sub back to −19 dB | filter opens plus a **whoosh-hit on the 4.47 negative strobe** |
| 5.5–7.0 | rolloff falls to 65 Hz, sub swells | **sub swell / pitch-drop pre-drop** |
| ~7.27 (beat at 7.49) | full band, dense harmonic lines from 500 Hz to 1.5 kHz, 8th-note kick | **DROP**: the first content cut (Senbit, 7.47) lands on it |
| 7.5–37.5 | sub −20 dB, onsets 11–15 per 2 s; a narrow 1.87 kHz tone gated in 16ths | full groove: four-on-the-floor-style kick in 8ths, 16th-note synth ostinato, chord stabs |
| ~15.7 | broadband transient, diagonal glide at 100–500 Hz around 15.5–16.5 | whoosh plus pitch glide into "Connected World" / "ZED" |
| 37.5–66.7 | **sub 13–16 dB lower** (−33 to −37 dB), air steady | lighter breakdown arrangement under the illustration act. The cut rate *rises* as the bass thins |
| 65.5–67.9 | **sub removed (−45 → −70 dB)**, air rises (rolloff 7.4–7.8 kHz), 16th stutter at 67.4–67.9, tone drop-out at 67.6–67.9 | **high-pass riser + gate stutter + a 0.3 s drop-out** before the logo |
| ~67.9–68.0 | sub back at −17 to −20 dB, broadband | **logo impact**, on the 6-frame dip to black |
| 68–71.5 | decaying tail; > 8 kHz gone by 70 s | long reverb / boom tail under the end card |
| 72.0–73.86 | digital silence | 1.9 s of silent end card hold |

---

## 5. Breakdown

### 5.1 Hook (0–2 s)
- **Frames 0–1 (67 ms): a "poster frame"** showing the finished "SHOW Reel 2026" lockup, then black at 0.07 s.
  Any auto-thumbnail (link previews, some players) therefore shows the designed cover *(inferred purpose)*.
- 0.10–0.47: **letters pop one at a time, about 3 frames per letter** (S 0.13 → SH 0.2 → SHO 0.3 → SHOW 0.4), each
  arriving large and settling smaller (scale-down settle, with a slight 3D twist) on the sub boom.
- 0.6–1.0: a **script word is written on** in a mint gradient across the caps' baseline. 1.3: a **glass pill "2026"**
  slides in from the left. 1.8–2.4: a two-line secondary block wipes in on the right (mint + white semibold).
- Background: true black, an off-centre green **fluid ribbon glow**, dot-matrix particles at the frame edges, and a heavy
  vignette (radial luma 55–135 at the centre → 1–2 at the corners).
- **Assessment:** it is a polish hook, not a curiosity hook. There is no question or promise, and the lockup is
  complete at 2.0 s and then *holds* until 4.47 under a low-passed bed. That works for a portfolio link but would
  bleed retention on IG Reels. Lesson for Jawad: keep the polish and put the hook *line* in the first 0.5 s.

### 5.2 Story structure
No narrative and no VO. It is a **technique montage in two phrase-length acts, bookended by brand lockups**:
1. **Intro (0–7.47):** title lockup → 3D keycap with orbiting text ("ideas / stories" copy), then the drop.
2. **Act 1, "3D / UI / glass" (7.47–37.47, 16 edits):** glass pill + cursor, nav menu, glowing map with tags,
   particle globe, extruded 3D logo, orange rim-lit app window, defocus landmark cards, star icon + context
   menu, holo phone, 3D shield, diagonal river of AI images, glass icon tiles with a portrait reveal, glow-card
   carousel, cyan HUD cube.
3. **Act 2, "illustration and story clips" (37.47–68.07, 22 edits):** ink-drawn bullying vignette, tiger lunge,
   flat globe with parcels, flying phone, AI-painted historical figure collage, year counter, camel rider, top-down
   kitchen, arches tunnel with an Arabic word list, family car, cultural dancers, pocket watch, rice pan,
   graduation party, pixel-art museum card.
4. **End card (68.07–73.86):** the same lockup system with the author's name, role, copyright and email.

Act 1 → act 2 is about 30 s after the drop, and act 2 → outro another ~30 s: roughly **16 bars at 127 BPM each,
within about half a beat** *(inferred: sections are phrase-locked even though single cuts are not)*.

### 5.3 Typography *(observed; sizes as a % of frame height, 718 px)*

| role | style | size | animation |
|---|---|---|---|
| title caps ("SHOW", name) | condensed bold grotesk, all caps (Anton / Bebas-like), chrome white-to-grey vertical gradient, light bevel | cap ≈ 14 % H | per-letter pop every ~0.1 s, big → settled (scale-down), a light slash cuts through |
| title script | monoline connected script, mint gradient, overlaps the caps' baseline | x-height ≈ 8 % H | write-on in ~0.35 s |
| tag pill | glass capsule, green emissive edge, white bold numerals | ≈ 5 % H | slides in from the left in ~0.2 s with motion blur |
| secondary block | geometric semibold sans (Clash / Gilroy-like), mint line + white line, normal tracking | cap ≈ 2.8 % H | wipe / type-on L→R |
| product word in a pill ("Senbit") | geometric sans medium, white with a slight vertical gradient | cap ≈ 10 % H | slides in with blur; exits by **erasing right → left (~18 letters/s)** while the pill collapses into a glow blob |
| orbit text | white semibold grotesk round a 3D ring; back-side glyphs dimmer and mirrored | ≈ 4 % H | the ring rotates at roughly 90°/s |
| UI labels | geometric sans: header 4 % H, sub 2.4 % H light grey | | staggered row reveals at ~0.15 s |
| glass tags on the map | white text in frosted pills | ≈ 4 % H | drift / orbit, HUD micro-coordinates next to them |
| hero 3D word ("ZED") | extruded glass / chrome, lime-yellow, heavy bloom | 60 % H → 35 % H | letters flip and overlap into place, camera pulls back |
| counter ("1973 → 1978") | heavy condensed numerals, extruded grey, drop shadow | ≈ 32 % H | odometer tick, smoke wisps |
| word list (Arabic) | bold sans with underline bars | ≈ 5 % H | one word every ~0.3 s |

There is **no serif italic in this reel.** Jawad's glowing orange serif italic keyword is his differentiator and should stay.

### 5.4 Transitions (≈ counts across the 42 edits, checked on the strips)
- **~22 hard cuts**, many of them **polarity flips** (dark ↔ white in one frame: 11.0, 12.8, 22.77, 24.77, 32.9, 34.93, 37.47, 65.13).
- **6 negative / invert flickers** (inverted-luminance frames, white or cold blue): 4.47–4.90 (5 frames negative, 5 dark,
  2 negative), 15.47–15.90 (same pattern), 31.10 and 31.30 (single white frames), 44.6, 46.97 / 47.17, 49.1.
  The flips land within ±55 ms of the 127 BPM 8th-note grid. Their rate stays at **≤ 2 flashes in 0.43 s**.
- **4 object / shape wipes:** a giant shield passes the lens (29.7), a green phone slab flies across (42.5),
  a tablecloth swipes (52.5), a red paint shape sweeps (60.0).
- **3 morph / collapse:** pill + text erase → glow blob → menu (9.3); star → 4 chrome petals (26.9); a glass lens
  bubble flies over the tiles and leaves a portrait inside (33.6–34.3).
- **3 pixel / mosaic:** keycap pixel-dissolves into the drop (7.3–7.47); a white page builds pixel blocks (65.1–66.1);
  pixel art resolves to an HD image (66.1–66.9).
- **2 whips:** a white light-streak whip (54.3–54.6) and a rotational whip (62.27).
- 1 organic **blob reveal** from a dot (58.2–58.5), 1 **defocus → focus** resolve (22.77–23.6),
  1 **slide-push** (46.63), 1 **6-frame dip to black** into the end card (67.9–68.1).

### 5.5 Camera *(Farneback optical flow per shot at 160 px width; "div" > 0 means push in)*
- Almost every shot moves a little: about **0.1–0.6 px/frame at 160 px (≈ 1–5 px/frame at 1276)**. Nothing is fully static except the end card and the cards.
- **Pull-outs on reveals:** ZED (div −0.24), Dubai cards (−0.18), year counter (−0.28), kitchen (−0.41),
  **arches tunnel (−0.98)**, car interior (−0.36).
- **Push-ins on impact:** holo phone (+0.13), shield (+0.15), **tiger lunge (+0.39)**, party / cake (+0.49 to +0.57).
- **Lateral tracks:** the AI-image river (pan_x +1.6), glass tiles (+1.8), carousel (−0.37).
- **Rolls / rotation:** green map (−0.09), flying phone (−0.72), rice pan (+0.47), pixel museum (−0.47).
- 3D window rotation with a **rack focus** on the title (18.5–22.8), and DOF bokeh on most glass scenes.

### 5.6 3D elements *(observed)*
A glass keycap with an emissive glyph · a glass ring with orbit text · an extruded chrome / glass 3D logotype with bloom ·
a particle globe and a glowing terrain map · glossy glass app icons (chat, profile, mail, folder) · a glass lens
sphere · a holographic phone · a 3D shield emblem · an isometric glass cube · a 3D year counter. Act 2 is mostly
2D / 2.5D (flat illustration, parallax collage, AI paintings).

### 5.7 Texture and finishing (measured unless marked)
- **Grain:** none on the dark brand and SaaS scenes (high-pass σ in flat areas 0.25–0.41, i.e. compression-clean);
  the UI scenes sit at 0.75–1.38; the illustration act carries paper texture (2.3–2.4).
- **Vignette:** very heavy on the bookends (centre 55–135 → corners 1–2 luma), working like a spotlight; moderate on the
  dark UI scenes; none on the light scenes.
- **Chromatic aberration:** no global CA (R/B outer-ring shift ≤ 0.5 px). There is a *local* RGB split on the fast-moving
  card edges at 31–33 s *(observed)*.
- **Bloom / halation:** strong bloom on emissive elements (keycap, ZED, glow blobs, rim lights) *(observed)*.
- **Light leaks:** no film-style leaks. Graphic light streaks instead (33–34 s blue streaks, the 54.3 s white streak) *(observed)*.
- **Overlays:** dot-matrix / halftone inside the green glows, a thin grid floor in the SaaS backdrops, HUD
  micro-text and bounding boxes *(observed)*.
- **Blacks:** true 0 black, nothing lifted. Flashes go to white or an inverted frame, never to grey.

### 5.8 Pacing against audio
- The intro is slow (1 edit in 7.5 s) and **the first content cut lands on the drop** (7.27–7.49 → 7.47).
- Act 1 averages 1.76 s per shot, act 2 1.33 s. The edit gets *faster* while the music gets *lighter* (sub −13 to −16 dB),
  so overall energy is carried by the picture.
- Individual cuts are **not** locked to accents (48 % vs a 52 % null), but strobes and flips fall near the 8th grid and the
  section changes are phrase-length. **The big structural moments are synced; the small ones float on the groove.**
- The outro gets **high-pass + stutter + a 0.3 s drop-out**, then the impact and the dip to black. It is the most
  deliberate sync point in the reel.

### 5.9 Ending / CTA
The name lockup rebuilds with the opener's animation system (bookend recall), plus the role line
"Art Director & Motion Designer", a copyright / year line and an email. **The CTA is the contact info only; there is
no verbal or written ask.** The card holds 5.8 s, the last 1.9 s in silence.

---

## 6. Timed beat table

| # | t0–t1 (s) | shot / content | type (size, style) | device / camera | transition out | audio event |
|---|---|---|---|---|---|---|
| 0 | 0.00–0.07 | finished title lockup (poster frame, 2 frames) | full lockup | thumbnail trick | hard cut to black | sub boom starts |
| 1 | 0.07–4.47 | title build on black + green fluid ribbon, dot particles | caps 14 % H chrome; script; pill; 2-line block | per-letter pop (3 fr / letter), slash, write-on, pill slide; slight pull-back, then hold | **negative strobe 4.47–4.90** (5 neg / 5 dark / 2 neg) | boom 0–2; whoosh 2.0–2.5; **low-pass hold 2.5–4.0**; whoosh-hit 4.47 |
| 2 | 4.47–7.47 | glass keycap "go" in a glass ring, orbit text | orbit text 4 % H | ring spins ~90°/s, roll drift | **pixel-dissolve** 7.3–7.47 | sub swell / pitch-drop 5.5–7.0; **DROP ~7.27–7.49** |
| 3 | 7.47–9.30 | blue glass pill "Senbit" + cyan glow blob, cursor flies in and clicks | 10 % H geometric sans | element motion, static cam | text erase R→L + pill collapses to a blob | groove: 8th kick, 16th synth |
| 4 | 9.30–11.00 | blob → app tile + nav list (Portfolio / Motion / Samples / Projects) | 2.5 % H | stagger list | **polarity flip** to white | — |
| 5 | 11.00–12.80 | Arabic headline in a pink pill + 3D pink flower pop | Arabic bold | spring pop | polarity flip to black | — |
| 6 | 12.80–15.47 | glowing green circuit map, 6 frosted word tags + HUD coordinates | tags 4 % H | slow roll | **negative strobe 15.47–15.90** | — |
| 7 | 15.47–16.53 | particle globe, "Connected World" | bold sans ~6 % H | push + roll | hard cut to a warm gradient | whoosh ~15.7, pitch glide |
| 8 | 16.53–18.50 | extruded glass "ZED" logotype, bokeh, lime → orange floor | 60 % → 35 % H 3D | **pull-out**, letters flip in | hard cut to black (red pixel blocks) | — |
| 9 | 18.50–22.77 | **dark glass app window, orange rim light**, sidebar, rows Safer / On-Cloud / Chat / Faster, title "Smart Control" | header 4 %, sub 2.4 % | **3D Y-rotation side → front + rack focus** | polarity flip to blurred white | — |
| 10 | 22.77–24.77 | landmark photo: **defocus → focus**, resolves into a glass card carousel | — | pull-out + lateral slide | hard cut to dark | — |
| 11 | 24.77–26.90 | glowing 4-point star + construction circles, context menu | micro caps | static | star splits into 4 chrome petals | — |
| 12 | 27.43–29.80 | holographic phone, wallet icon, crypto glyphs, scan streaks | — | push-in | **giant shield passes the lens** (object wipe) | — |
| 13 | 29.80–31.10 | 3D shield emblem, concentric outlines | — | push-in + roll | 1-frame white flashes at 31.10 / 31.30 | — |
| 14 | 31.10–32.90 | **diagonal river of AI-image cards**, HUD boxes + lines, RGB-split edges | small label | lateral track (pan +1.6) | polarity flip to white | — |
| 15 | 32.90–34.93 | glossy glass icon tiles on white, blue streaks; **glass lens reveals a portrait in a card** | — | lateral parallax | polarity flip to black | — |
| 16 | 34.93–36.50 | **frosted card carousel, a coloured emissive glow behind each card** | card title 5 %, sub 2.6 % | carousel shift | hard cut to cyan | — |
| 17 | 36.50–37.47 | cyan isometric HUD cube + light streak | — | — | hard cut / polarity flip (act change) | ~16 bars after the drop *(inferred)* |
| 18 | 37.47–39.13 | B&W ink: man grows as taunting speech bubbles pop around him | Arabic bubbles | character morph, corner brackets | hard cut | **sub −13 to −16 dB** from here (lighter arrangement) |
| 19 | 39.13–40.33 | panther → **tiger lunges** with manga speed lines | — | push-in +0.39 | polarity flip to white | — |
| 20 | 40.33–41.87 | flat green globe spinning, parcels orbiting | — | — | hard cut | — |
| 21 | 41.87–43.80 | man with bags, flying money → **green phone slab wipes across** → winged phone on lime | — | object wipe + rotation | hard cut | — |
| 22 | 43.80–46.63 | AI-painted scholar → **negative-blue flash** → collage (circular text ring, skyline, name pill, torn paper) | Arabic ring text | collage reveal | slide-push | — |
| 23 | 46.63–49.10 | ship + compass (negative flashes 46.97 / 47.17) → building + **3D year counter 1973 → 1978** + smoke | counter 32 % H | pull-out | negative flash 49.1 | — |
| 24 | 49.10–50.27 | painted camel rider over a photo collage, caption pill | — | — | hard cut | — |
| 25 | 50.27–52.50 | top-down kitchen table, items pop on in a stagger | — | slow pull-out | **tablecloth object wipe** | — |
| 26 | 52.50–54.27 | purple bg, frying pan with flames | — | — | **white light-streak whip** | — |
| 27 | 54.27–56.13 | golden arches tunnel on magenta + an Arabic word list (1 word / ~0.3 s) with underline bars | ≈ 5 % H | **strong pull-out (div −0.98)** | hard cut | — |
| 28 | 56.13–58.20 | cartoon car → family interior (56.63) | — | bouncy cam | **organic blob reveal from a dot** | — |
| 29 | 58.20–60.77 | paper-cut dancer on orange → **red paint swipe** → second dancer on crimson | — | — | hard cut | — |
| 30 | 60.77–62.27 | pocket watch swinging over clouds (time passing) | — | — | **rotational whip** | — |
| 31 | 62.27–63.77 | top-down rice pan rotating, flames | — | rotation | hard cut | — |
| 32 | 63.77–65.13 | graduation party → push-in to the cake and a phone notification | — | push-ins | polarity flip to white | — |
| 33 | 65.13–66.13 | "Museum of the Future – Dubai" typed with a pixel cursor | small sans | — | pixel-mosaic build | **high-pass riser** (sub −45 → −70 dB) |
| 34 | 66.13–68.07 | pixel art → HD card, info fields typed in | small sans | pull-out | **6-frame dip to black** | stutter 67.4–67.9, **0.3 s drop-out**, impact ~67.9–68.0 |
| 35 | 68.07–73.86 | name lockup rebuilds (letters 68.13–68.5, script 68.75–69.1, pills), role + email | same system as #1 | static hold | end | tail decays to 71.5; **silence 72.0–73.86** |

---

## 7. Steal like an artist: 15 techniques adapted to Jawad's brand

The brand frame for everything below is **deep black / very dark warm brown (`#070302`–`#1A0A04`) with a fiery orange → red
glow (`#FF8A1E` → `#FF4A12` → `#E01B1B`)**, white bold uppercase grotesk, a glowing orange **serif italic** keyword with
glowing underline strokes, and the `@jawad_mp4` signature. Register a project-local `'ember'` look once rather than
reusing `neon` / `amber`: add `K.C['EMBER_*']` colours, `K._BG_LOOKS['ember']` (dark top / bottom, 2–3 orange and red blobs,
`rim=0`, a low `dots` value), `K.LOOKS['ember']` (bloom tint `(1.0, 0.55, 0.30)`, halation about 0.14 with the default orange
tint, vignette 0.5–0.6, `black_tint` a hair warm) and `ui.LOOKS['ember']` (a copy of the dark look's tokens recoloured).
Target the ratio measured in ref1's orange scene: **~75 % near-black, ~20 % ember glow, ≤ 2 % hot highlight and type.**

| # | technique (seen at) | why it works | Jawad adaptation | build |
|---|---|---|---|---|
| 1 | **Bookend lockup system** (0–2.4 / 68–70) | the same animation grammar opens and closes, so the brand registers twice | the close card: white grotesk caps "JAWAD" pop in per letter, the orange **serif italic** keyword ("editor", "kahani") writes on, glowing underline, a glass pill tag ("2026" / "EDITS"), `@jawad_mp4` beneath | `T.Glyphs('JAWAD', <white grotesk style>, px≈200).slam(...)` with ~0.1 s letter stagger; serif italic word = `T.render(word, 'deep_glow', font=<serif italic>, glow_color=('#FF5A1F', 2.4))` revealed with `T.Glyphs(...).wipe`; pill `T.render('2026', 'glass_pill')`; underline = `K.streak` + `K.glow`; SFX `pop` per letter, `whoosh_fast` on the slash, `logo_sting` on the settle |
| 2 | **Per-letter "scale-settle" pop at ~3 frames per letter** (0.1–0.47) | fast enough to read as one gesture and slow enough to feel crafted; it hits on a boom | the hook word in the first 0.5 s (e.g. "KUCH" caps), then the serif keyword lands as payoff on the VO stress | `T.Glyphs(...).slam(t0=..)` with a per-glyph offset of 0.1 s; scale 2.2 → 1 `out_expo`; `samples(t)=5` during the slam; `impact_soft` on the last letter |
| 3 | **Low-pass hold → drop on the first content cut** (2.5–7.5) | starving the high frequencies builds pressure; the drop *is* the cut | under the VO hook, keep the music bed low-passed (≈ 400 Hz) and open the filter + sub drop exactly on the first "turn" line / first big visual | `audio.py` has `lp` / `hp` / `eq`: render the bed in segments (or a short crossfade between a filtered and an open copy); cue `sub_drop` + `reverse_swell` (align end) on the cut. Our own or licensed music only, **never** the ref's track |
| 4 | **Negative / polarity strobe at a whoosh** (4.47, 15.47, 44.6) | the inverted frames register as a camera flash and reset the eye | a **warm negative** (inverted luminance mapped to a cream → orange duotone, never cold white): 4 frames negative, 4 dark, 2 negative, at most twice per reel, **≤ 3 flashes/s** (photosensitivity) | custom post step after `K.post`: `inv = 1 - to_srgb(cv)`, remap luma through an ember duotone, back to linear; or `K.flash(cv, amt, color=K.hexlin('#FFE2C4'))` for single frames; SFX `flash_hit` + `glitch_short` |
| 5 | **Orbit-text ring round a glowing 3D object** (4.5–7.4) | the text has depth (front bright, back dim); the hero object stays readable | an orange glass **"REC" / play-button keycap or playhead** with Roman Urdu orbit text "KAHANI • JAZBAAT • EDIT • " | `T.OrbitText('KAHANI • JAZBAAT • EDIT • ', 'flat', px=56, fill='#FFF1E6')`: draw `part='back'`, then the hero sprite, then `part='front'`; hero = a Blender bevelled cube (glass BSDF + emissive orange glyph), 72-frame spin rendered to a sprite sequence (CPU, low samples, `nice -n 10`) |
| 6 | **Rim-light comet on a dark glass app window + 3D swing + rack focus** (18.5–22.8) | the closest thing in ref1 to Jawad's palette; it reads as "premium software" | a dark **NLE timeline window** (clips, waveform, playhead) with an orange-red comet running round its edge; it swings from a 70° side view to frontal while the title racks into focus | `ui.app_window(look='ember', header='Timeline', ...)`; `win.face_at(sweep=phase, sweep_color='#FF5A1F')`; `win.plane(cv, cam, P, w, rot=(0, Track(70 → 8), 0))`; title drawn with `blur=K.lerp(14, 0, u)`; SFX `whoosh_slow` + `ui_hover` |
| 7 | **Glass pill + cursor click → morph** (7.5–9.4) | a micro-interaction viewers know from software, with a satisfying click | a search-bar pill ("how to edit like…" / "jawad.mp4"); the cursor clicks, a ripple, then the pill collapses into an orange glow blob that becomes the next scene | `ui.search_bar` / `ui.button`, `ui.draw_cursor(..., press=K.impulse(t, tc, 9), click=t - tc)`, `ui.click_ring`; collapse = x-scale squash + `K.glow`; text erase R→L with `T.Glyphs(...).wipe` reversed; SFX `ui_click`, `swish_small` |
| 8 | **Frosted card carousel with per-card emissive glows** (34.9–36.5) | colour coding without clutter; the focus card swaps on the beat | 4 cards (Reels / Ads / AI Video / Motion, or "raw → cut → grade → sound") with glows stepping **amber → orange → red → crimson** | `ui.glass_card` + `ui.media_face(card, thumb)` + a `K.radial(...)` glow behind each (mode `'add'`); `ui.carousel` index on `K.beat_index`; SFX `card_slide` per shift |
| 9 | **Diagonal river of image cards with HUD boxes** (31.1–32.9) | shows volume ("I've made a lot") in 1.8 s; the HUD makes it feel technical | Jawad's own AI-video frames streaming up the 9:16 diagonal with orange HUD boxes and "FRAME 0042" labels | `K.Scene` planes on a 3D diagonal, camera tracking (`Cam` x/y moving), `aperture≈30`; thin HUD lines drawn in a custom `sc.custom`; edge split `K.chroma(cv, 3)` only while moving; SFX `whoosh_by` |
| 10 | **Lens bubble reveals the portrait inside a glass tile** (33.6–34.3) | a personal-brand intro with a "magic" beat | a glass lens sweeps across a row of dark glass icons (camera, timeline, AI); where it passes, the centre tile becomes **Jawad's headshot from his character sheet** (smirk), with an orange rim | `ui.glass_card` + `ui.media_face(card, headshot)` revealed through a circular mask whose centre follows the lens path; lens = a Blender glass-sphere sprite or `K.disc` + local `K.zoom_blur`; SFX `glass_tap` + `shimmer` |
| 11 | **Defocus → focus "eyes open" resolve** (22.77–23.6) | a cinematic breath that also hides the cut | open a scene in orange bokeh and resolve it onto his face or title in 0.6 s while pulling back | `Cam(aperture 80 → 20)` with `focus_dist` animated, or `K.draw(..., blur=K.lerp(30, 0, ramp(t, a, b, 'out_cubic')))`; SFX `air_zoom` |
| 12 | **Giant object crossing the lens as the wipe** (29.7, 42.5, 52.5, 60.0) | motivated transitions; the object is the cut | on-brand for an editor: a **clapperboard, film strip or timeline clip block** in orange sweeps across the frame | full-frame sprite (Blender clapper or a `K.rrect_alpha` slab with perforations) moved `inout_expo` over 8–10 frames; `K.whip_blur(cv, px, angle)`; `samples(t)=7` in the wipe; SFX `whip` / `whoosh_fast` |
| 13 | **Pixel-mosaic → HD resolve + typed info fields** (65.1–66.9) | a perfect metaphor for "average edit → Jawad edit" | a frame starts as 64 px blocks and steps 64 → 32 → 16 → 8 → 4 → 1 on 8th notes, then caption fields type in ("Edit: Jawad · Time: 3 din") | per frame `cv2.resize` down (INTER_AREA) then up (INTER_NEAREST) with a quantised block size; `T.Glyphs(...).typewriter`; SFX `ui_tick` per step, `typing` |
| 14 | **3D stat counter / odometer** (47.3–48.7) | numbers are proof, and motion makes them land | e.g. "0 → 1,000,000 views" or "Day 1 → Day 365" in white numerals with an ember glow (not the fostering `gold` preset) | `T.Counter(<custom white / ember style>, px≈220)` with `K.Track([(t0, 0, 'out_expo'), (t1, v)])` and `vel=trk.vel(t)`; SFX `slot_tick` (align='start', dur) + `impact_soft` on the land |
| 15 | **Nested-frame pull-out tunnel + staggered list with underline bars** (54.3–56.1) | strong depth plus a readable list at a calm 0.3 s per word | pull back through nested **video frames / screens** (the editor inside the edit) while "HOOK • STORY • EDIT • SOUND" rises one word per beat with glowing orange underlines (his house underline) | `K.Scene` with N `K.rrect` outline planes (emissive orange) at stepped z; camera z `out_cubic` back; `T.Glyphs(...).rise` stagger; underline `K.streak` + `K.glow`; SFX `whoosh_slow` + `ui_tick` per word |

**Structure lessons to carry over (not a device each):**
- **One hue family per scene, on true black.** Ref1 changes hue every scene; Jawad keeps one family (orange → red) and
  varies *heat* instead: amber for warm memories, orange for the present, red for tension or error.
- **Phrase-locked sections, groove-floating cuts.** Put the big moments (act turn, CTA, logo) on the music phrase and VO
  stress; small cuts can float. For VO reels, cut on the VO phrase ends and SFX hits.
- **The edit speeds up as the music thins** (act 2). For VO reels: when the VO gets intimate, drop the bed and raise the
  visual rhythm, or the reverse.
- **Outro grammar:** high-pass the bed under the last line → a 0.3 s drop-out → a 6-frame dip to black → impact + `logo_sting`
  on the `@jawad_mp4` lockup → hold 2–3 s. Unlike ref1, put a *spoken and written* CTA before the logo
  (e.g. "Follow karo, agla reel aur bhi crazy hai").
- **Poster frame:** make frame 0 the designed cover (hook text already visible), so auto-thumbnails and shares show the
  cover; then animate from it. Keep it ≤ 2 frames, or simply open on the resolved frame.

---

## 8. Devices to avoid

- **The horizontal composition.** Ref1 is 16:9, and its lockups and carousels span about 50–70 % of the width. A 9:16 centre
  crop keeps only 404 / 1276 px (32 %). Every device must be **re-composed vertically**: stack the lockups, run the
  carousels in depth or vertically, run the rivers on the 9:16 diagonal. Key copy stays in x 70–1010, y 230–1480.
- **Title-card hook with a 2.4 s hold:** on IG that is a swipe-away risk. Open on the VO hook line or a visual payoff in the first 0.5 s.
- **True peak +0.3 dBTP:** master to about −14 LUFS but **≤ −1.0 dBTP**.
- **Strobes above 3 flashes/s** or white flashes on large areas: keep ref1's ≤ 2 flashes per 0.43 s, at most twice per reel.
- **36 unrelated visual worlds:** this works for a showreel but dilutes a personal brand. Keep one world (ember on black) across each reel.
- **Long runs of white backgrounds** (act 2): they break Jawad's dark cinematic identity. Flip polarity only briefly, and to warm cream.
- **Microtext at 2–2.5 % of frame height** (HUD coordinates, UI subs): unreadable on a phone. Minimum 28–34 px at 1080 width.
- **Insult speech bubbles, cultural costume dances and real landmarks used as decoration:** sensitive or irrelevant for his
  audience; never mock appearance.

## 9. Do not copy

The "SHOW Reel" / name lockup design, the green fluid ribbon, the "Ideas in motion / Stories in every frame" copy, client
names and logos (Senbit, ZED, Smart Control, QAREN…), the UI copy ("Safer than your bank"…), the map, landmark photos,
illustrations, characters, AI paintings and the music track. Ref1 media stays in the git-ignored workspace and never goes
into a deliverable.

## 10. Open issues for the lead

- **Fonts:** no serif italic suitable for Jawad's keyword is installed (only Liberation Serif / FreeSerif Italic). Fetch an OFL
  serif italic (e.g. Instrument Serif Italic, Playfair Display Italic or Fraunces Italic) into the toolkit `WS/fonts`. Inter
  Display Black / ExtraBold is installed system-wide for the white grotesk caps.
- **Music:** the toolkit's `audio.py` makes SFX and beds only (no music). Ref1's power comes from a 127 BPM bed with a filtered
  intro, a drop and an outro riser, so Jawad's reels need an original or properly licensed bed (freesound and pixabay are blocked here).
- **The toolkit looks are Organic Fostering's** (`neon` / `amber` / `airy`) and its fonts default to Nunito / Poppins. Register the
  project-local `'ember'` look and fonts as described in section 7; do not ship the fostering looks.
