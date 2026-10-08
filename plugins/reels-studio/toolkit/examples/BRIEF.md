# Organic Fostering: three cinematic SaaS-style reels

This is the creative brief and engineering contract. Every agent working on this project reads it first.

## 0. Deliverables
- Three vertical reels for Instagram, TikTok and Facebook: **1080×1920, 30 fps, 22–28 s each**. Encode as H.264 High, yuv420p, bt709 tags, AAC 320 kbps at 48 kHz.
- **AUDIO = SFX ONLY. NO MUSIC.** The client will add music later. Build a rich, cinematic sound-design layer instead: whooshes, whips, impacts, sub drops, risers, reverse swells, UI clicks, pops, check dings, coins, shimmer, heartbeat, leaf rustles and room-tone ambience beds. Do not use melodic or musical loops, chord pads or beats. Single tonal stingers inside SFX are fine (a bell ding on a check, a logo shimmer). Leave headroom for the client's music: normalise the SFX mix to **−18 LUFS integrated, ≤ −1.5 dBTP**. Also export each reel's SFX as a separate 48 kHz 24-bit WAV stem. Each reel keeps a fixed **BPM cut grid**, so music at that tempo will lock to the edit.
- The style is **cinematic SaaS motion graphics** (see the reference notes in §2). It combines the client's real footage with 3D-rendered elements, glass UI, 3D, deep-glow and light-sweep typography, fast montage hooks, a virtual camera and real motion blur.
- **The three reels must look and feel clearly different from each other.** §5 gives each one its own look, palette dominance, tempo, transitions and hero devices.
- The bar is "max quality". Every frame should look like a premium After Effects/C4D agency piece, not a template.

## 1. Brand (from organicfostering.co.uk, verified)
| token | sRGB hex | use |
|---|---|---|
| MAGENTA | `#B7006E` (logo `#A6055E`) | primary brand, glows, "Organic" |
| HOT_PINK | `#FF3D9A` | magenta glow core / highlights only |
| ORANGE | `#FF6411` (logo `#F46308`) | secondary brand, "Fostering", energy |
| AMBER | `#FFB15C` | orange highlight, coin gold |
| LEAF | `#64A60B` | logo leaves, check marks, growth |
| LEAF_HI | `#A8E04A` | leaf highlight |
| PLUM | `#5B174F` | dark brand purple |
| INK | `#321F35` | dark text on light scenes |
| NIGHT_0 / NIGHT_1 | `#0B0310` / `#1C0822` | dark scene background gradient |
| IVORY | `#FCF8F5` | light scenes, text on dark |
| PEACH | `#FFD4BA` | soft warm light |
| LAVENDER | `#F6EAF3` | soft light-scene tint |

The **signature gradient** runs MAGENTA → ORANGE at 35°, like the brand's sunset. Use it for hero accents, light trails and button fills.

**Logo** (`workspace3/brand/`):
- `logo_full.png`: the logo on light backgrounds.
- `logo_full_onDark.png`: the magenta is swapped to near-white so it reads on dark.
- `logo_mark.png`: the OF emblem with the children and leaves.
- `logo_wordmark.png`: "Organic / Fostering".
- `logo_tagline.png`: NURTURE • DEVELOP • GROW.
- `organic-fostering-final-logo-2026-09-25.svg` and `favicon.svg`: the vectors, used for 3D extrusion.

Never recolour the logo except through the provided onDark variant, and never stretch it.

**Fonts** (`workspace3/fonts/`):
- **Nunito** (Black, ExtraBold, Bold, SemiBold, Regular, Black/ExtraBold Italic) is the brand font. Its rounded forms match the logo. Use it for display and hero type.
- **Poppins** (Regular to Black) matches the client's ad creatives. Use it for UI and body text.
- **Caveat Bold** is an optional handwritten accent, used at most once per reel.

**Verified copy you may use** (do not invent statistics, prices or claims):
- "Become a Foster Carer" · "Could you be a foster carer?" · "Open your home and change a child's life" · "With full training and ongoing support" · "No previous experience needed!" (these last four are from the client's ads)
- "Offer a child a safe home, everyday care and a place to belong" · "A small beginning can change the direction of a life" · "Nurture. Develop. Grow." · "You do not need to arrive with all the answers" · "Support is part of the role." · "Your circumstances deserve a conversation."
- Eligibility: "a suitable spare bedroom, time and flexibility, the right to work in the UK, willingness to complete assessment, checks and training. You may be single or in a relationship, and rent or own your home."
- Trust: "Independent Fostering Agency" · "Cultural Matching Specialists" · "Informal First Conversation" · "Rated Good by Ofsted · Inspected May 2025"
- Support: "Your supervising social worker" · "Preparation and ongoing learning" · "Advice outside normal hours for approved carers" · "Contact with other foster carers" · "Help navigating a child's education and health needs"
- Matching: "Culture, faith, language, relationships and identity matter."
- Weekly allowance per child: **0–4 yrs £447.60 · 5–10 yrs £473.17 · 11–14 yrs £515.52 · 15+ yrs £554.02**. Example: **£23,275.20** for 52 weeks, one child aged 0–4. Disclaimer: "Rates may vary by region and are subject to change." "Recognition for a skilled role."
- Types: Short-term · Long-term · Emergency · Respite · Siblings · Teenagers. Their one-liners are "A safe home while the next steps are planned", "Steady care and a sense of belonging over time", "A calm welcome when a child needs care at short notice", "Short breaks that support children and their carers", "Helping brothers and sisters stay together" and "Care that makes room for growing independence".
- Journey: 01 Start a conversation · 02 Initial/home visit · 03 Apply & train · 04 Assessment · 05 Panel/approval
- CTA: **"Start your enquiry"** · **0161 241 1332** · **organicfostering.co.uk** · "Discuss your estimate"
- Do NOT use "24/7", "guaranteed", "£2,500" (the unit of the ad's £2,500 figure is unclear), invented child statistics, or the Ofsted logo itself. A generic star/shield badge with the text is fine.

## 2. Style reference: a SaaS motion showreel (the user's reference)
The reference video has these looks. Reuse the devices; don't copy them.
- Near-black void with **large soft volumetric colour glows** (an off-centre blob of light, like an aurora), drifting dust particles and a faint dot or grid texture.
- **3D chrome/extruded titles** with a white-hot face, gradient-lit sides, and a **light sweep** passing across. Light-leak streaks.
- **Curved orbit text** circling a glossy 3D object (a "go" keycap). Text wraps in 3D, so the back half is mirrored, dimmer and blurred.
- **Glass UI**: a perspective-tilted app window with a neon-lit edge (orange/magenta rim light running along the border), a left sidebar of icons and rows of list items with coloured app icons. The camera dollies across it with rack focus.
- **Dock of glass tiles**: rounded-square glass cards with a glowing coloured icon, a title and a subtitle. The focused tile enlarges and lights up, and coloured glow blobs sit behind the tiles.
- **A 3D map/globe with floating tag labels** around it.
- **A diagonal stack/wall of photo cards** flying through 3D space with chromatic aberration.
- Light sections: a white/ivory background with soft colour gradients and glossy 3D app icons.
- Glossy 3D icons in phone mockups, plus a shield with a logo.
- Transitions: whip pans, zoom-throughs, iris/ring wipes, light flashes and morphs.

## 3. Global craft rules (apply everywhere)
1. **Legibility first.** Text never overlaps other text or busy footage without a backing, which can be a scrim gradient, a frosted-glass card or a dark/light radial falloff. Aim for a contrast of at least 4.5:1. Size minimums at 1080 wide: hero 130–240 px, H2 80–120 px, UI body 34–46 px, fine print ≥ 28 px.
2. **Safe zones** (Instagram Reels UI). Key copy goes inside x ∈ [70, 1010], y ∈ [230, 1480]. CTA buttons may reach y 1600. Keep the bottom 300 px free of text. Avoid x > 930 for y ∈ [1050, 1700], where the like/share buttons sit.
3. **Motion.** Nothing moves linearly. Use expo/quint ease-out for entrances, spring overshoot for pops, and an AE-style "easy ease" (influence 70–85 %) for camera moves. Add a subtle constant drift: every shot breathes with a slow push or float. There must be real **motion blur** (sub-frame accumulation, 180° shutter) on every moving element and camera move. Use 3 samples normally and 5–7 on whips.
4. **Depth.** Every shot has at least three depth layers: a background glow or blurred plate, the subject layer, and foreground particles or bokeh or a blurred near element. Add depth-of-field blur on non-focused planes and parallax on camera moves.
5. **Finishing.** Bloom/halation on highlights, a gentle vignette, chromatic aberration only near the frame edges and during whips, fine film grain (amount ≈ 0.018) and a grade consistent with the reel's look.
6. **Rhythm.** Cut and slam on the reel's BPM grid. There is no music in our mix, but the client will add music at that tempo, so beat times must stay exact. The hook happens in the first 0.0–2.5 s and must stop the scroll: fast montage, flash frames and a bold question or statement.
7. **Footage.** Always grade it into the reel's look. Punch-in and drift so footage is never static. Use speed ramps (1.0 → 0.4 slow-mo at emotional beats, and fast at montage). Crop to faces sensibly. `c13` has a dark blurred occluder on its left 35 %, so crop to the right.
8. **Brand.** Use the brand colours, but the reel's look decides how much of each (§5). Leaves and hearts from the logo recur as motifs.

## 4. Footage (`workspace3/frames/cXX/%05d.jpg`, manifest in `workspace3/frames/manifest.json`)
4K sources are pre-scaled to **1920 px tall**, so any of them can be cropped to a full-bleed 1080×1920 frame. 1080p sources are 1080 px tall. Use them in cards, or full-bleed only in fast montage flashes or behind blur/scrims, because a 1.78× upscale is soft.

| id | content | src fps / dur | notes |
|---|---|---|---|
| c00 | dad and daughter in a cosy indoor tent with a cup | 25 / 10.4 | 1080p, warm |
| c01 | two women hug a smiling girl, faces to camera | 24 / 16.8 | **4K hero**, joyful |
| c02 | toddler stacks wooden blocks with a dad | 24 / 15.8 | 2K, tower at 1–5 s |
| c03 | counsellor with notepad and two kids holding teddies | 25 / 11.9 | 1080p, support |
| c04 | counsellor meets a family of 3 on a modern sofa | 25 / 14.7 | **4K**, family smiles at 1–4 s |
| c05 | family on sofa with teddy, then paperwork close-up | 25 / 11.8 | 1080p; family 0–7 s, signing 8–11 s |
| c06 | two dads and a boy on a sofa with a laptop | 25 / 10.4 | 1080p wide |
| c07 | yard: man, woman and child meeting outdoors | 25 / 5.5 | **4K**, first meeting |
| c08 | woman piggybacks a smiling girl, VERTICAL | 25 / 9.8 | **native 1080×1920** hero |
| c09 | child with backpack and teddy arrives, welcomed and hugged | 25 / 17.9 | 1080p; arrival 4–8 s, hug 13–17 s |
| c10 | dad and daughter cuddle on a blue sofa, then smile to camera | 25 / 24.2 | 1080p; hug ≈10 s, smiles 14–22 s |
| c11 | mum hugs a small child with a big teddy | 25 / 6.0 | 1080p close, tender |
| c12 | woman and boy laughing on a sofa | 24 / 25.2 | **4K**, joy |
| c13 | two dads and a child with a tablet | 25 / 10.2 | crop right 65 % |
| c14 | two mums play with a baby, baby lifted | 29.97 / 15.8 | 1080p; lift 9–12 s |
| c15 | two women gently hold a baby on a blanket | 25 / 10.8 | **4K**, soft window light |
| c16 | woman and child pet a dog through a kennel fence | 25 / 8.0 | **4K**, foreground leaves |
| c17 | woman and girl with a teddy on a park bench | 25 / 20.0 | 1080p, calm outdoor |
| c18 | woman explains a document to a child and her mother | 25 / 15.0 | 1080p, process |

Site photos (`workspace3/site_img/`): `03-short-term…`, `04-long-term…`, `05-emergency…`, `06-respite…`, `07-siblings…` and `08-teenagers…` (1344×1800, one per fostering type), plus `hero-children-sunset…` and `balanced-home-*`.

## 5. The three reels

### REEL 1: "COULD YOU?" (recruitment) · ≈26 s · 120 BPM (beat 0.5 s)
**Look: NIGHT NEON.** A NIGHT_0/1 void with MAGENTA-dominant volumetric glows, an orange rim light and a faint dot grid. Glass UI has neon magenta edges. The footage grade is rich contrast, warm skin, plum shadows and magenta/orange split-toning.
**Sound (SFX only):** heartbeat cold open, whip/flash hits on every montage cut, a sub-drop and boom on the question, soft glass UI ticks and check dings on the beat, card whooshes, a riser into the end card, and a final logo shimmer and impact with a reverb tail. A low warm room tone sits underneath.
1. **0.0–0.45 Cold open.** Black, a heartbeat thump, and a thin magenta light-ring iris opens on c01 (a smiling face), pushing in.
2. **0.45–2.45 HOOK MONTAGE.** Eight beat-synced flashes of 0.25 s, full-bleed: c12, c10, c08, c14 (lift), c00, c16, c02, c11. Transitions are whip blur, flash frames, light-leak sweeps and chromatic aberration. Four slammed 3D words with deep glow, one per 0.5 s, with camera shake on each: **"A SAFE HOME." → "EVERYDAY CARE." → "A PLACE" → "TO BELONG."** Ivory faces, magenta glow, a dark scrim behind each word.
3. **2.45–5.3 THE QUESTION.** Smash to the void. A glossy 3D **"?"** spins in from depth with motion blur. Type builds as **"Could YOU / be a / Foster Carer?"**: "YOU" is 3D-extruded in the MAGENTA→ORANGE gradient with a light sweep, and "Foster Carer?" has a deep orange glow. Far behind, c01 sits in a tilted glass card with bokeh depth blur. The camera orbits slowly (yaw 8° → −4°) and pushes in.
4. **5.3–11.6 "AM I ELIGIBLE?" SaaS checklist.** The camera whips down to a floating glass app window, perspective-tilted, with a neon magenta edge and a left icon sidebar. Its header reads "Am I eligible to foster?". Rows tick on the beats, 0.75 s apart, each with a 3D green check pop, a cursor click and a soft SFX: **"A spare bedroom" · "Time & flexibility" · "Single or in a relationship" · "Rent or own your home" · "No previous experience needed"**. Then a progress ring fills to 100 % and a toast appears: **"You could be a great fit"**. The camera dollies along the rows with rack focus, then pulls back.
5. **11.6–18.4 SUPPORT DOCK.** The headline **"Support is part of the role."** sits above three glass tiles that slide in as a carousel, each with a glossy 3D icon. The focused tile enlarges, plays footage inside and gets a light sweep:
   - grad cap: **Full Training**, "Preparation & ongoing learning" (c03)
   - chat bubble: **Ongoing Support**, "Your supervising social worker" (c04)
   - £ coin: **Weekly Allowance**, "From £447.60 a week per child" (c10 smiles)
   The camera trucks past the tiles horizontally, and coloured glow blobs sit behind them.
6. **18.4–21.0 PAYOFF.** Full-bleed c08 (vertical) in slow motion at 0.6×, with a warm grade. Light-sweep type reads **"Open your home."** then **"Change a child's life."** over a bottom gradient scrim.
7. **21.0–26.0 END CARD.** The 3D logo mark rotates in with a light sweep and a magenta/orange glow ring. The wordmark builds and the tagline "Nurture • Develop • Grow" appears. A gradient pill button **"Start your enquiry →"** is clicked by the cursor (ripple, press). Below it: **0161 241 1332 · organicfostering.co.uk** and a small "Rated Good by Ofsted" star badge. Hold at least 1.5 s.

### REEL 2: "FINANCIAL SUPPORT" (allowance) · ≈24 s · 128 BPM (beat 0.469 s)
**Look: AMBER DASHBOARD.** Darker and warmer: NIGHT with **ORANGE/AMBER-dominant** glows, gold-orange glossy 3D coins, data visualisation and isometric/perspective dashboards. Magenta is only an accent (≈20 %). The footage grade is golden-hour warm with teal-free shadows.
**Sound (SFX only):** coin flip and ring, card whoosh-bys in the tunnel, slot-digit ticks, a cash "ka-ching" on the totals, chip clicks, a slider drag, bar-grow swells, an impact on the title, orbit whooshes and a coin-flip logo sting.
1. **0.0–2.2 HOOK.** A 3D £ coin flips toward the camera, fills the frame and whips. Then a **flying card tunnel**: footage cards (c12, c04, c09, c14, c05, c13…) rush past the camera in 3D with chromatic aberration and flashes. Slot-machine digits roll with motion blur, and the title slams as 3D-extruded **"Financial Support"** in amber gold with a light sweep, with "for foster carers" below.
2. **2.2–5.0 THE NUMBER.** A huge counter rolls **£0 → £447.60**, with "/ week per child" and a glass chip "Ages 0–4". 3D coins orbit the number in an ellipse, depth-sorted and blurred at the back. The camera pushes in.
3. **5.0–12.6 ALLOWANCE CALCULATOR APP.** A perspective glass window titled "Allowance calculator". Age chips [0–4] [5–10] [11–14] [15+] are clicked in turn on the beats. A 3D glossy bar chart (orange gradient) grows to **£447.60 · £473.17 · £515.52 · £554.02**, with the active bar glowing and the values counting up. Then a "Weeks of care" slider drags to **52**, and the total counts up to **£23,275.20**, labelled "Estimated allowance · 52 weeks · one child aged 0–4". Fine print, legible: "Rates may vary by region and are subject to change." The camera makes isometric-to-front moves with rack focus.
4. **12.6–17.6 SUPPORT ORBIT.** A glossy 3D house sits at the centre. A tilted elliptical **orbit ring of glass tags** circles it, depth-sorted, with the back blurred: "Supervising social worker" · "Ongoing training" · "Advice outside normal hours" · "Foster carer community" · "Education & health help". The headline reads **"Plus support around your household"**. The camera orbits.
5. **17.6–20.4 HEART BEAT.** Full-bleed c12 (laughing), slow motion, warm. Light-sweep type reads **"Recognition for a skilled role."**
6. **20.4–24.0 END.** A 3D coin flips and, mid-flip, its face becomes the logo mark, which settles on the end card. A pill CTA reads **"Discuss your estimate →"** (cursor click), with the phone and URL below. Tiny disclaimer.

### REEL 3: "NURTURE · DEVELOP · GROW" (brand story) · ≈26 s · 92 BPM (beat 0.652 s)
**Look: LIGHT & ORGANIC.** An IVORY/PEACH daylight world with soft magenta and orange gradient blooms (like the reference's white sections), glossy green 3D leaves, airy depth of field and drifting leaf particles. It ends in a warm MAGENTA→ORANGE sunset gradient. Text is INK on light, or white on footage with scrims. The footage grade is bright, airy, soft-contrast and warm.
**Sound (SFX only):** a seed drop with a water-like plip and soft thud, a ripple shimmer, an organic growth swell with rustling leaves, soft paper and glass UI taps, gentle whooshes, zoom-through air, a puzzle click, a tag pop, a birdsong/outdoor ambience bed (subtle), and a warm shimmer sting at the end.
1. **0.0–2.0 HOOK.** A glowing 3D seed (a warm orb) falls in slow motion onto an ivory surface and makes an impact ripple ring. A burst montage (six flashes of 0.2 s: c01, c08, c12, c15, c10, c17) appears inside a circular iris that grows from the seed. The type **"A small beginning"** is 3D with a soft ink shadow.
2. **2.0–5.5 GROWTH.** A 3D sprout grows from the seed point (Blender growth animation), with the camera craning up along the stem. The type completes: **"can change the direction of a life."** Leaves unfold and drift.
3. **5.5–15.5 THREE CHAPTERS.** Each chapter gets a UI pill "01 / 03" and leaf accents.
   - 5.5–8.8 **"NURTURE"** is a giant word (Nunito Black, about 250 px) with **footage playing inside the letters** (c11). Then the camera **zooms through the letter "U"** into full-frame footage. Sub: "A safe home & everyday care".
   - 8.8–12.1 **"DEVELOP"** uses video-in-type with c02. The sub "Matching that sees the whole child" appears, chips pop **Culture · Faith · Language · Identity**, and a pair of 3D puzzle pieces clicks together under the label "Cultural Matching Specialists".
   - 12.1–15.5 **"GROW"** uses video-in-type with c17 and c16. Sub: "Steady care and a sense of belonging".
4. **15.5–20.5 KINDS OF CARE.** The headline reads **"Different children need different kinds of care"**. A glossy 3D heart (or house) sits at the centre, with a tilted 3D orbit ring of six glass tags: Short-term · Long-term · Emergency · Respite · Siblings · Teenagers. Each tag carries a small rounded thumbnail from the matching site photo. The tags are depth-sorted, the back ones blurred, and the camera orbits. This must look different from Reel 2's orbit: here the scene is light, the tags are image tags and the ring is tilted the other way.
5. **20.5–22.4 TRUST.** Three glass pills stack in with check icons: **"Independent Fostering Agency" · "Cultural Matching Specialists" · "Rated Good by Ofsted"**, alongside a 3D shield.
6. **22.4–26.0 END.** The sprout's two leaves fly into the logo's leaves, and the logo assembles on ivory as a sunset gradient blooms up from the bottom. The tagline "Nurture • Develop • Grow" types on. CTA pill **"Start your enquiry"**, plus the phone and URL.

## 6. Engineering contract
- Code lives in `pipeline/fostering/` and is committed. Data lives in `workspace3/`, which is git-ignored: `frames/`, `fonts/`, `brand/`, `site_img/`, `assets3d/`, `audio/`, `out/`. Resolve paths from `pipeline/fostering/core.py`'s `WS` constant (`<repo>/workspace3`, overridable by the env `FOSTER_WS`).
- Python 3.13 with numpy, opencv-python-headless, pillow, scipy, bpy 5.2 (Blender as a module, Cycles CPU only, no GPU) and cairosvg. There are only **4 CPU cores**, so be frugal: cache aggressively with `functools.lru_cache` and precomputed sprites, and keep cv2 threads at 1–2 per worker.
- **Pixel convention:** canvases and sprites are premultiplied **linear-light** float32 RGBA arrays `(H, W, 4)`. Convert sRGB hex to linear with `core.hexlin()` and convert back only at encode. Canvas size is `W, H = 1080, 1920`, `FPS = 30`.
- **Modules:**
  - `core.py`: paths, colour, easing/keyframes/springs/noise, compositing, sprite draw (2D affine with sub-pixel accuracy and mip-mapped downscale), 3D camera, perspective plane draw, blur, glow/bloom, light leaks, particles, grain, vignette, chromatic aberration, the motion-blur render loop and the ffmpeg writer.
  - `footage.py`: `Clip` time-remapped frame access with frame blending, the grade looks (`'neon'`, `'amber'`, `'airy'`), cover/crop helpers and the `Clip` LRU cache.
  - `type3d.py`: typography (3D extrude/bevel, deep glow, light sweep, gradient fill, neon, glass pill text, video-in-type masks, per-glyph kinetic layout, orbit/curved text).
  - `ui.py`: the SaaS UI kit (glass card and app window, checklist row and checkbox, toggle, chips, pill button with press and ripple, 3D cursor, bar chart, slider, counter digits/slot roll, progress ring, toast, dock tile, orbit-tag ring).
  - `assets3d.py` (Blender renderer) and `sprites3d.py` (runtime loader for the rendered RGBA sequences, indexed by frame or by yaw angle).
  - `audio.py`: the synthesized SFX library (no music), the cue-sheet mixer, loudness normalisation and stem export.
  - `reel1.py`, `reel2.py`, `reel3.py`: the timelines.
  - `render.py`: parallel chunked rendering, preview mode (half-res, single sample), stills and contact sheets, mux.
- Every module starts with a docstring that documents its public API with short examples. Other agents rely on that docstring.
- Each module must be importable without side effects and runnable standalone with a self-test that writes PNGs to `workspace3/out/selftest/<module>_*.png`.
