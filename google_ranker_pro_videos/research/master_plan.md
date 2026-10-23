# Master plan: 15 real-life videos for Google Ranker Pro / Hulk Marketing

Lead creative director's synthesis, 22 Oct 2026. British English. Built on the winning pitch **A "Show the receipt"** (`concept_A-proof.md`), with films grafted from **B "Every call is a fare"** (`concept_B-story.md`: videos 1, 2, 5, 6, 8, 10, 15) and **C "Filmed on a phone"** (`concept_C-social.md`: video 3 and the social packaging), and every weakness the judge named fixed (§11).

> **Note:** this is the planning document. Where it differs from the production pack in `pack/` (durations, line wording, fixes from two review rounds), follow the pack.

**Sources of truth.** Every number traces to `assets/gsc/gsc_data.json` and the six PNGs in `assets/gsc/` (crop rectangles from `gsc_story.md` §4), the live sites captured 22 Oct 2026 (`client_*.md`, `assets/sites/`), or a public record (Companies House). Prompt rules follow `production_rules.md`, which distils the user's own `human-realism`, `production-consistency`, `cinedance-higgsfield` and `higgsfield-production` skills. The structured twin of this file is `master_plan.json` (same content, same IDs).

**The user's brief, in their words:** *"make sure to follow the realism in the prompts. it must not feel like ai, cgi or plastic effect or 3d game render it must look like a real life shot, videos."*

**What the user generates:** raw footage only, on Higgsfield (Seedance 2.5 video; Soul ID and Nano Banana Pro for character sheets and anchor stills). No text, captions, logos, graphics or titles in any generation. We do the whole edit: the real Search Console and Business Profile receipts, the before-and-after, titles, captions, sound.

---

## 0. The plan in one paragraph

Fifteen short documentaries from one wet October week in the Midlands. Every film is built around **one real number shown as a receipt**: an exact crop of the client's own Search Console or Business Profile screenshot, with its source and date underneath. The people are **witnesses, not salespeople**: taxi owners, a fostering-agency director, an SEO specialist, a reporting lead and the founder, each saying in their own approved words and their own voice what the number meant. The footage looks like a small documentary crew, or the person's own phone, followed them: a parked car before sunrise, a kitchen table after the last run, a dispatch room on a Saturday night, a desk by a rainy window. The recurring image is **a phone lighting up face-up, its screen never readable**. Web films (1, 2, 5, 6, 13, 15) run problem → turn → result with the first receipt at about 65–75% of the runtime; every social cut has its number on screen by 0.8 s. Where the data is weak we say so out loud ("that's an average", "October's only half a month", "no earlier period to compare yet"). That honesty is the differentiator, and it matches the agency's own lines "See the change. Not just the claim." and "No ranking guarantees".

**Budget:** 86 first takes (41 at 16:9, 45 at 9:16; 832 s of footage), with a 1.5× retake budget (about 129). Eight Mode B character sheets (F1, T1, T2 and five client witnesses), one Mode A sheet (N1) only if a fallback is triggered, one optional (F2).

---

## 1. Series grammar (all 15)

### 1.1 Witness, evidence, context
1. **Witness:** a real person (or, in a fallback, real hands and real places) in their real world.
2. **Evidence:** the receipt (below). It is never redrawn, re-typed or animated from estimates.
3. **Context:** one honest line that keeps the number fair: "average position", "19 Jul–18 Oct 2026", "October is a part month", "no earlier period to compare yet".

### 1.2 The receipt (the only proof device; edit-only, never generated)
- **Source:** the real PNG cropped at the rectangle listed per video (x, y, w, h in original pixels). A single GSC row *n* sits at `24, 904 + round((n−1)×49.1), 1318, 49`.
- **Treatment:** the crop sits on a navy `#0B1628` card with a 12 px radius. One thin orange `#F7931E` underline draws under the one figure that matters, with a soft tick SFX. A slow 3–4 s push-in from 102% to 108% with a light grain match to the footage.
- **Source line (always on, Inter 500, `#BDCBDC`):** e.g. `Google Search Console · goldenlinetaxiswarwick.co.uk · 19 Jul–18 Oct 2026`.
- **Context strip** under the source line when needed: `Average position over 3 months. Positions 1–10 are page one.` / `October is a part month.` / `Business name confirmed by [client], [date].`
- **Banned in the edit:** "No.1", "#1", "first", "just hit", "now" (as a claim), "growth", "+x%", up-arrows, count-ups to numbers we don't hold, charts rebuilt from pixel estimates, Google logos or colours on our graphics. The screenshots' own Search Console UI stays as evidence, never as our branding.
- **Other devices** (all carrying receipts, never replacing them): B's green-laptop push-in to full frame (1, 2, 13, 15); C's duet (2's 9:16 cut); stitches 3 → 9 and 1 → 15; the green-screen effect for 14; the live-footer push-in for 1; the month-by-month mask reveal for 4; the 16:9 "phone clip beside receipts" layout when 3, 8 and 9 are reused on case-study pages.

### 1.3 Disclosure labels (persistent, small, lower-left above the safe zone)
| Footage type | Label |
|---|---|
| Real person, Mode B re-creation | `AI re-creation made with [Name]'s permission. Their words, their voice. Real data.` |
| Real voice over faceless footage | `Dramatised visuals. Real voice, real data.` |
| Labelled AI presenter (fallback only) | `AI presenter. Real client data. Not a client testimonial.` |
| No-face generated b-roll | `Illustrative footage. Real data.` (video 4: `Dramatised reconstruction · Real data`) |

Set the TikTok AIGC, YouTube altered/synthetic and Meta AI-info toggles on every post. The user and their adviser confirm the final wording.

### 1.4 Words in people's mouths
- **Clients (1–6, 9):** we supply **questions and the facts they may hear on screen**, never their sentences. Their answers are recorded as voice memos, transcribed, and approved by them; only then do those exact words go into Seedance, with their memo as `@Audio`. Lines in this plan are marked **DRAFT FOR CLIENT APPROVAL** and `[their words]`. Owners quote no numbers: the numbers are ours, on screen and sourced.
- **Agency people (7, 8, 10–15):** we draft; they edit, approve and record.
- **Numbers spoken aloud** are written as words in the prompt and must match the receipt exactly. One approved line per 5–8 s talking stage.

### 1.5 Claim and copy rules (apply everywhere)
- Impressions are **"times shown"**, never "people saw" or "people searched".
- The window is **"19 Jul–18 Oct 2026"** or **"the last three months"**, never "last quarter".
- Write **"15.9K"**, never "15,900".
- October is a **part month**: never a dip, fall or decline.
- Leam Taxis: **"September: 25 calls, the best of the six months shown."** and **"114 calls May–Oct 2026 (October part month)."** Never "best month since May"; never "114 since May" inside a September report.
- No "No.1", "#1", "first", "just hit", "now", growth percentages or up-arrows until a Compare export or a dated SERP exists. Position 1.8 is **"top two on average (brand searches)"**; 6.0 and 6.7 are **"page one on average"**.
- No invented specifics: no "four am run to Birmingham", no clock stamps on generated footage, no "He'll ring me in about ten minutes", no first-person client text the client did not say and approve.
- Founder commentary says **"Here's what we did. Here's what Google shows now."** No causal verbs (made, drove, caused) without both the work log and a comparison period. A sitemap lastmod is "dated", not "built". "Hardly anyone got that far down" is deleted (that query earned 12 clicks).
- Coventry Business Profile context lists only **calls, chat clicks, bookings and website clicks** (the profile has no Directions tab).
- The only lines presented as the site's own: **"No ranking guarantees"** and **"See the change."**
- Any Heathrow tip is **"a page for the inbound direction"** (Coventry already has a Heathrow page and a published £249 saloon fare).
- **Never use:** the duplicated "Ali" reviews or a generated "Ali"; York reviewers' names in agency ads; site self-claims (15,000+, 4.6, the Slough 4.9/202 widget, Zentro's 4.8/2,560+); Hulk's portfolio percentage ranges; Organic Fostering allowance figures; prices from the GRP pricing page.

### 1.6 Brand on screen
Google Ranker Pro on googlerankerpro.com placements (homepage: 13, 1, 2; service pages: 5, 6, 10; case studies: 1, 2, 4, 15). Hulk Marketing on UK social (3, 7, 8, 9, 11, 12, 14) and in client-facing lines. Relationship verified from public records: Hulk Marketing Ltd is the UK company (Companies House 15931335, incorporated 2 Sep 2024, directors Hassan Pasha and Muhammad Sajid), set up 'to bring that experience, talent and infrastructure directly to UK businesses' (hulkmarketing.co.uk/about); Google Ranker Pro is the older international group brand ('since 2012', self-declared, unverified). Proposed end-card lockup 'Hulk Marketing · part of Google Ranker Pro': the user decides. Brand marks appear only in the edit, never in a generation. Golden Line's end card may say 'Website by Hulk Marketing Ltd' (live footer 'Made with ❤ by Hulk Marketing Ltd'). No 'we built' line for Coventry until the SMEK footer question is settled (smek.co.uk lists Hassan Pasha as CEO), and none for York Cars (footer: Xoom Media), Leam Taxis (Hulk portfolio only), Organic Fostering (rebuild unconfirmed) or Zentro (no credit anywhere) until each client confirms in writing. The only lines we may present as the site's own are 'No ranking guarantees' and 'See the change.'

---

## 2. World Bible: "One wet October week"

Every prompt in the set pastes these blocks **verbatim**, chosen by scene type. This is what makes 86 generations read as one real shoot.

### 2.1 Palette
**Setting truth:** one wet October week, late October 2026, the week after the data window closed (19 Jul–18 Oct 2026). Warwick, Leamington Spa, Kenilworth and Coventry, plus York (video 5) and Old Trafford (video 6), plus the agency's real workplace(s). Autumn: wet tarmac, leaves in gutters, heating on, condensation on car windows, dark by half five. Paste exactly one palette line per prompt, chosen by scene type.
- **PAL-EXT** (exteriors only, verbatim): 'Muted autumn colour as it really looks: wet slate greys, an overcast white sky, wet black tarmac, red-brick terraces and cream stucco, cold white LED and older amber street light; people in navy, grey and mid-blue everyday clothes; nothing saturated.'
- **PAL-INT** (rooms: offices, kitchens, back offices, dispatch rooms; verbatim; never any tarmac, street-lamp or stucco tokens): 'Muted, lived-in indoor colour as it really looks: off-white and pale grey walls, worn wood and grey laminate, cool daylight at the window, a warm pocket of light from a lamp or ceiling bulb; people in navy, grey and mid-blue everyday clothes; nothing saturated.'
- **PAL-CAR** (inside a parked car; verbatim): 'Muted colour inside a parked car as it really looks: a charcoal dashboard and grey seat fabric, rain beads on the glass, the world outside soft and grey; people in navy, grey and mid-blue everyday clothes; nothing saturated.'
- **AGENCY ADD-ON** (agency rooms only, pasted after PAL-INT): 'One small warm orange object in frame, such as a mug or a notebook.'
- **Brand colours** (GRP orange #F7931E and blue #3FA9F5, Hulk lime #C6FA61, every client colour) live only in edit overlays.

### 2.2 Light logic
One named source per shot, pasted verbatim across every shot of that set-up. No golden hour or low sun anywhere in the set; both video 4 plates stay overcast.
- **L-OFFICE** (agency room and client offices by day): 'Soft overcast daylight from a large window camera-left is the only key; the right side of the face falls a stop darker with soft shadow under the cheekbone; the overhead office lights are on but weak, adding a faint cooler top light; the window itself is slightly overexposed.'
- **L-HOME** (client kitchens and back offices at dusk or night): 'A warm tungsten ceiling bulb or lamp camera-left is the key; cool blue-grey dusk from a window camera-right; the two colour temperatures meet on the face; corners of the room fall into soft shadow.'
- **L-TAXI** (pre-dawn and dawn inside a parked car): 'Blue-grey early daylight through the car windows mixed with the warm amber of street lamps outside; the dashboard stays dark; the face is lit softly from the side window and falls off into shadow on the far cheek; rain beads on the glass catch small points of light.'
- **L-CAR-DAY** (inside a parked car by day): 'Flat overcast daylight through the windscreen is the only key, soft and slightly cool; the side window camera-right adds a brighter edge on that cheek; the cabin roof and footwell fall into soft shadow; the windscreen itself is slightly overexposed.'
- **L-STREET** (exteriors by day): 'Flat overcast sky as a huge soft source from above; soft shadows under the eyes and chin; wet tarmac reflects the grey sky; no direct sun.'
- **L-STREET-NIGHT** (exteriors after dark): 'Cold white LED street lamps mixed with one older amber lamp further down the street are the only light; wet pavement reflects both; the face is lit from one side by the nearest lamp and falls into shadow on the other; a faint rim of lamp light separates the head and shoulders from the dark street.'
- **L-PREMISES** (dispatch room): 'Fluorescent ceiling tubes are the key, flat-ish but real with a slight green-cyan cast; the dark window adds nothing; darker corners at the back of the room; the monitors face away and give off almost no light.'
- **GLOW** (reaction lit by a phone, screen facing away): 'The phone screen faces away from the camera; its cool white glow lights the face from below, brighter on the chin and under the nose.'
- **Always add for deep skin tones**: 'exposed correctly for deep brown skin so the highlights show natural sheen and the shadow side keeps detail.'
- **Always add for dark sets**: 'a faint rim of window light separates the head and shoulders from the dark background.'
- **Every set**: two or three dressing anchors that stay put, one uncomposed element (a half-cropped passer-by, a crooked blind, a cable across the floor, a parking ticket face-down on the dash), and atmosphere between lens and subject (breath in cold air, steam from a mug, drizzle, rain on glass, a smeared windscreen with the wiper parked mid-glass).

### 2.3 Capture modes and texture lines
One capture mode per video, pasted verbatim as the last line of every prompt; never two modes inside one generation (mixing between generations is the documentary texture).
- **DOC-CAM** (1, 2, 6, 10, 13, 15, and the observational inserts of 1, 2, 6, 10, 13, 15): 'Filmed on a handheld documentary video camera in available light: natural colour with a restrained grade, fine even digital grain, soft highlight roll-off on bright windows, real depth of field with a gently soft background.'
- **PHONE-SELFIE** (3, 7, and 12's to-camera beats): 'Filmed handheld on a smartphone front camera at arm's length: small-sensor look with deep focus, slight edge over-sharpening, faint sensor noise in the shadows, auto exposure and auto white balance as recorded, ungraded colour.'
- **PHONE-REAR** (4, 8, 11, 12's b-roll, 5's walk-round, dash-mounted POV shots): 'Filmed handheld on a smartphone main camera: small-sensor look with deep focus, slight edge over-sharpening, faint sensor noise in the shadows, auto exposure and auto white balance as recorded, ungraded colour.'
- **PROPPED** front-camera shots (9, 14, and any dash- or tripod-mounted selfie): see the propped-camera test (phone_realism_line; master_plan.md §2.4); run the logged single-variable test before the first propped generation and keep whichever line passes QC.

### 2.4 Phone realism and the propped-camera test
PROPPED-CAMERA TEST (one logged single-variable test on v09_R-01 before any other propped shot; keep whichever passes QC for 9, 14 and every mounted selfie).
- **TEST A**: 'Filmed on a smartphone front camera propped in a mount at chest height: small-sensor look with deep focus, slight edge over-sharpening, faint sensor noise in the shadows, auto exposure and auto white balance as recorded, ungraded colour.'
- **CONTROL**: the verbatim PHONE-SELFIE line.
- **Propped camera lines** (3–4 at most per prompt): 'The phone is propped in a mount or against an object at chest height, 50 to 70 cm from the face; the frame is static except for faint vibration when the surface is touched or a car door closes.' 'Framing is a little off-centre, slightly low, the top of the head close to the top edge.' 'Their eyes go to the screen image of themselves as often as to the lens.'
- **Handheld selfie lines**: 'The phone is held in the speaker's own outstretched right hand; the frame moves with their arm: slight handheld micro-shake, small drifts as they gesture with the other hand, a natural re-grip once.' 'Auto exposure breathes slightly when the window behind them comes into frame, then settles.'
- **Phone-rear lines**: 'Handheld by a person walking slowly: gentle vertical bob with each step, small horizon tilts corrected by hand, no gimbal smoothness.' 'Autofocus hunts once, briefly, as the subject moves closer, then locks.'
- **Phone audio**: 'Sound recorded by the phone's built-in microphone at arm's length: close voice with a little room reflection, faint handling noise when the grip shifts.'

### 2.5 Lock library (paste verbatim where the scene needs it)
- **TEXT-LOCK:** `No on-screen text, captions or subtitles. All signs, labels, mugs, clothing, papers and screens are plain or turned away, with no readable words, logos or numbers. Number plates are not readable.`
- **SCREEN-GREEN:** `The [laptop/monitor/phone] screen shows a flat, uniform, matte chroma-green fill from edge to edge, evenly lit, with no interface, no text, no reflections and no glare; all four corners and the bezel stay visible, with one small dark dot in each corner of the green. The screen gives off almost no light. (Camera static or very slow while the screen is in frame; thumb resting on the side of the phone, not on the screen; at most one brief tap if the story needs it.)`
- **SCREEN-AWAY:** `The laptop screen is angled away from the camera; only the back of the lid is visible.`
- **SCREEN-SOFT:** `The monitor sits out of focus in the background, its picture a soft blur of light with no readable detail.`
- **VEHICLE:** `The car has real weight: suspension settles after it stops, tyres flex on the kerb, road grime along the sills, rain beads on the bonnet, reflections of the grey sky distort across the panels.`
- **TAXI:** `A plain [black/silver/grey] saloon or people carrier with no livery, no door lettering, no roof sign text, no decals. The front and rear number plates are angled away from the camera, out of focus, or hidden behind a foreground object. It waits at a kerb, a driveway or a drop-off zone, never on a rank.`
- **SKIN-B:** `Natural skin from the references, visible pores and fine texture, unretouched.`
- **SKIN-C:** `Real skin texture with visible pores and fine hairs; [one imperfection: a plaster on one knuckle / a slightly chipped nail / a faint ink mark].`
- **HANDS:** `Hands relaxed with natural knuckle creases and veins; five fingers each, fingers not touching the face during speech.`
- **BEHAVIOUR:** `They blink naturally, glance away to think, restart a gesture, adjust a sleeve, take a breath before a line, and finish with a small involuntary nod. (Write gestures, never emotions.)`
- **AUDIO-CLOSE:** `Dialogue: only the quoted line(s), spoken by [PERSON] at the stated seconds, in natural British English; lips still when not speaking; no other voices. No background music. No subtitles. At least 1 second of ambience-only before the first word and after the last word.`
- **DOC-AUDIO:** `Clean close dialogue as if from a clip-on microphone, natural room tone underneath, no echo.`
- **PEOPLE-COUNT:** `Exactly [N] people visible. No extra people.`

### 2.6 Forbidden in every generation
- Hype and polish tokens (production_rules D.6): cinematic, film look, 8K, 4K, HDR, ultra-realistic, photorealistic, hyperrealistic, masterpiece, award-winning, stunning, epic, flawless, perfect, pristine, crisp, polished, professional, high-end, commercial, glossy, studio, beauty shot, editorial, symmetrical, perfectly framed
- Camera bodies, lens brands, ISO, shutter or f-stops as the main control; resolution words in the prompt (set 1080p in the UI)
- Aesthetic negations such as 'no AI look', 'not CGI', 'no plastic skin' (only the earned skin lock or game-look lock after a logged failure)
- Readable text of any kind: signs, number plates, mugs, clothing, papers, lanyards, screens; no captions, subtitles, titles, watermarks
- Logos, liveries, roof signs, licence badges, invented firm names or phone numbers; any Google logo or Google brand colours
- Generated screen content: every screen is angled away, defocused, or flat matte green with four small dark corner dots
- Background music in any generation; subtitles
- Face prose for any real person (Mode B); a generated face standing in for a real named client; a generated 'Ali'
- More than two identities in one generation (three-person moments become a two-shot plus hands inserts)
- Private-hire cars on a hackney or station rank, roof signs or 'TAXI' lights, yellow New-York-style cabs; a car pulling away during a call; anyone on a phone or talking to camera while driving
- Golden hour or low sun anywhere; sunny blue-sky 'advert' weather; studio, black-background, ring-light, beauty or three-point light
- Gimbal, steadicam, dolly, slider, crane or drone moves; slow motion; speed ramps; chair spins; inverted-focus shots unless a test clip passes QC
- Creamy bokeh on phone modes
- Hands over the mouth while talking; more than one approved line per 5–8 s talking stage
- Children of any kind for Organic Fostering; carers; case files; names on whiteboards
- Glass-walled corporate HQs, a London skyline, or a serviced office dressed as a large fitted HQ
- Look-alikes of the five existing polished GRP presenters; the 30 sample portraits on googlerankerpro.com; the founders' black-studio portrait look
- Generated client premises, fleet or livery without the client's own photos; generated landmarks presented as evidence; trams on Chester Road (Old Trafford gets a bus on the A56)
- Clock or time stamps on generated footage; fake comment bubbles; edit-built notifications that show numbers

### 2.7 Grain and finishing
Grain lives only inside the capture-mode texture line. No other grain or film-stock words (no 35mm, Kodak, halation). Finishing (us): one grain value, one sharpen value and one upscale route per video: Higgsfield upscale_video with the ugc preset for phone modes and aigc for DOC-CAM, applied once and only if the Seedance 2.5 UI capped at 720p (flagged by the user). Never upscale stills that will be animated. Light grade in the edit only (lift the shadows a touch, never teal-and-orange). Social masters at −14 LUFS; captions inside the 9:16 safe zones (clear of the top 12% and bottom 20%).

### 2.8 Prompt hygiene (production_rules §C, D.6, §10)
- Write every generation to the §C skeleton, in this order: ASSET MAP → SCENE CONTEXT → LOCATION MAP → FIRST FRAME AND SPATIAL BLOCKING → FORMAT MODE (SINGLE CONTINUOUS TAKE) → OPTICS (one D.2 block) → CAMERA (3–4 lines at most) → TIMELINE (whole seconds, each stage ending in a visible end state) → PHYSICS → LIGHTING (one named source + SKIN line) → AUDIO → FINAL FRAME → POSITIVE CONSTRAINTS (palette, TEXT-LOCK, screen lock if any, people count, texture line last).
- UI, not prompt: Seedance 2.5, reference mode, **1080p** (720p only if that is the cap, flagged), aspect ratio, whole-second duration, audio on; Era 2020s, Physics realistic, Tone calm or warm, Genre unset or documentary, Lens 24 mm for phone modes and 50 or 85 mm for DOC-CAM. If a selector is set, the prompt does not restate it.
- **Anchor still first** (Soul 2.0 or Nano Banana Pro, at the deliverable ratio, in the capture mode's look), QC it hard, then animate. Ratio-specific anchor stills for every ×2 shot.
- **QC every clip at full resolution with sound** and log `QC [date] grp_vNN_[setup]-[shot] t[n] [seedance_2_5] / Verdict PASS|FAIL / Checks realism identity text/screens motion audio honesty / Failure: symptom > broken lock > fix`. Change one thing per retry (D.7 failure-fix table). Never retry silently.
- **Durations:** talking 8–12 s (15 s ceiling), one approved line per 5–8 s stage, medium or close framing for lip-sync, hands away from the mouth; b-roll 5–8 s; reactions 6–10 s; walk-and-talks split into generations of 12–16 s at most, cutting on a doorway. Nothing in this plan exceeds 15 s.

### 2.9 Real footage before generation
Real phone footage beats any generated landmark: locals spot wrong architecture instantly. Ask the user (or the client) for these first; a landmark is generated only from the user's own photo as the location reference, with signage out of frame, and is never presented as evidence.

| ID | Real footage (8–10 s phone clips, overcast, plates soft) | Used in |
|---|---|---|
| RF01 | Warwick: the river side of Castle Bridge; Market Place early morning | 1, 15 |
| RF02 | Leamington Spa: The Parade at first light | 3, 9 (optional cutaways) |
| RF03 | Kenilworth: town centre / Abbey Fields car park | 3 (fallback), 7 |
| RF04 | York: Station frontage and the Minster at night | 5 |
| RF05 | Coventry: ring-road slip road at blue hour | 2, 4 |
| RF06 | Old Trafford: Chester Road (A56) in drizzle with a **bus** passing (never a tram) | 6 |
| RF07 | One dashcam drive per town: into Warwick (A46 / Coten End), Leamington, the Coventry ring road, York | 1, 2, 15 |
| RF08 | Organic Fostering's 19 real Drive clips (check each for superseded figures) | 6 |

### 2.10 Location anchors (one anchor still per set-up, reused)
| ID | Place | Videos | Source |
|---|---|---|---|
| L1 | Agency room: a real desk by a window, monitor, kettle within earshot | 8, 10, 11, 12 (if UK office), 13, 14, 15 | User photos of the real workspace (the four listed addresses are serviced offices: never dress one as a big fitted HQ) |
| L1-TIP | Fixed tip-of-the-week desk in L1: window camera-left, orange mug, plant, coat on the chair | 14 (every episode) | One reused anchor still |
| L2 / L2b | Golden Line owner's own car on a Warwick terraced street; his back office or kitchen | 1 | His photos (plates hidden) |
| L3 | Coventry owner's kitchen table | 2 | His photos |
| L4 | A generic parked car on a wet Coventry kerb | 4 | Generated, no identity; presented as a reconstruction |
| L5 | York Cars' yard and dispatch office | 5 | **York Cars' own photos required** |
| L6 | Organic Fostering office, Beaumont House, Old Trafford | 6 | Client photos |
| L7 / L7b | Leam owner's own car on a Leamington terraced street (never a rank); his street and front door at night | 3, 9 | His photos |
| L8 | T2's real home, street and desk (UK or Pakistan) | 12 (10 if their desk) | **Confirmed location and real photos** |
| L9 | The street outside T1's real workplace | 7 | T1's photos |
| L10 | N1's back room (fallback only) | 1 (B2), 15 (B) | Generated, presented as no particular business |

**Private-hire truth.** Cars are generic, unbranded saloons or people carriers, plates hidden, no roof-sign text. Never on a hackney or station rank: only kerbs, driveways and drop-off zones. B's rank shots (the old v9 location, v13 B-01, L4) are deleted. The VEHICLE lock goes in every prompt with a car exterior; nobody is ever on a phone or talking to camera while driving.

---

## 3. Cast

Every real person is **Mode B**: identity from their own 27-photo set (production_rules A.2, including the three front-camera selfies for anyone in a selfie shot), trained as a Soul ID (20–30 photos) and/or a Nano Banana Pro character sheet built with the B.2 skeleton; written consent covering likeness, voice, approved words, platforms and term; their own voice memos (A.3). **No face prose, ever**: only the wardrobe line (verbatim), behaviour, light and one texture note. Crop each sheet into single-view images (front head, three-quarter left, three-quarter right, full body front, hands) and attach those as `@Image` references, never the whole grid.

| ID | Role | Type / mode | Videos | Look | Wardrobe (verbatim) | Voice | Notes |
|---|---|---|---|---|---|---|---|
| **F1_HASSAN** | Hassan Pasha, CEO & Co-Founder, Hulk Marketing Ltd (Companies House director since 2 Sep 2024). Fronts the founder strand and closes the meet-the-team set. | founder; B: Soul ID trained on a fresh 27-photo window-light set (production_rules A.2) in both outfits, plus a Nano Banana Pro sheet (B.2 skeleton); written consent covering likeness, voice, approved words, platforms and term. | V10, V13, V14, V15 | Identity from his own fresh daylight photos only. Do not use his black-background studio portraits, the owner portrait or the 10 s hulkmarketing.co.uk founder clip as look references: they pull Seedance towards a glossy studio portrait. No face prose. Documentary, not studio: a real desk by a rainy window, a mug in hand, sleeves slightly creased; one imperfection per close-up (a stray thread at the cuff or a creased collar). | 13 and 15 (verbatim): 'a navy wool suit jacket over an open-collar white shirt, no tie, dark trousers, his own watch; no logos, no printed text'. 13 exterior beats add: 'a navy wool overcoat over the same'. 10 and 14, the weekly desk look (verbatim): 'a plain navy crew-neck jumper over a white T-shirt, dark trousers, his own watch; no logos, no printed text'. | His own voice memos, one approved line per take, 5–8 s each, numbers as words (production_rules A.3). Bound as @Audio for close talking shots and laid in as the final track wherever sync allows (G.1). Accent never described in text. Fresh memos needed: the existing founder clips are silent. | No AI founder, ever. If he declines to be recreated: 13 becomes his real voice over hands-and-places b-roll; 14 passes to T1 (a real person); 15 passes to N1 in the third person. Client-visit b-roll only if the visit really happens and the client agrees, at a kerb or yard, never at a rank. |
| **F2_SAJID** | Sajid Armughan, Co-Founder & Managing Director (Companies House lists 'Muhammad SAJID'; confirm how to caption him). Optional. | founder; B (only if he consents); Nano Banana Pro sheet for any two-shot with F1. | V10 (optional extra clip), V13 (optional two-shot b-roll) | From his own daylight photos; no face prose; not the black-studio look of his founder clip. | 'a dark unstructured jacket over an open white shirt, no tie, dark trousers; no logos, no printed text' | His own voice memo if he speaks. | No generations budgeted in the base plan. Adds 4 first takes (V10) or 1 (V13 two-shot) if confirmed. |
| **T1_SEO** | SEO specialist who does the search work on Golden Line and Coventry (candidate from the Hulk team page: Muhammad Ali, SEO Specialist; identity, role, client work and consent all to be confirmed by the user). | team; B: Soul ID from 27 photos including the three front-camera selfies; written consent. | V02 (real voice from the laptop; fallback presenter), V07, V08 (hands and real recorded voice), V10, V11 | From their own photos; no face prose. Lived-in, not corporate: the person who actually does the work. Hands: a plaster or a chipped nail is fine. | Desk (verbatim): 'a mid-blue overshirt over a plain white T-shirt, dark jeans; no logos, no printed text'. Outdoors in V07 (verbatim): 'a plain dark rain jacket, open, over a mid-blue overshirt and a plain white T-shirt, dark jeans; no logos, no printed text'. The orange enamel mug on their desk is the one brand-orange object. | Their own recordings. In V02 and V08 the voice is the real recording laid in by us, never generated. In V07 and V10 their memo is @Audio and the final track where sync allows. | If the real T1 is Muhammad Ali, never caption or place them so they could be confused with the 'Ali' named in Golden Line and Coventry customer reviews. Only work the user confirms T1 really did may be named. |
| **T2_REPORTING** | Reporting / delivery lead who builds the monthly client reports, including Leam Taxis' (candidates: Javaid Ahmad, Senior Project Manager; Momna Imran, Communications & Audit; unverified). UK or Pakistan location UNVERIFIED: the user tells us. | team; B: Soul ID from 27 photos including selfies; written consent. | V10, V11, V12 | From their own photos; no face prose; their real commute, real desk and real tea or chai only. | 'a navy knit jumper with the sleeves pushed up, plain dark trousers; no logos, no printed text' (adjusted to the person's own style and modesty preferences, photographed on the day). | Own memos, own accent, never described in text. | Day-in-the-life details must be true of their real day and real place; a UK/PKT time pill only if true. If T2 does not really deliver Leam Taxis' report, V12 switches to the client T2 really reports for, with that client's permission and data. |
| **CLIENT_GOLDENLINE_OWNER** | Owner or operator of Golden Line Taxis, Warwick (name, surname and role unverified; do not assume he is the 'Ali' in the reviews unless he confirms it). | real_client; B: 27 photos plus 2–3 photos of his real car (plates hidden) and 6–10 photos of his back office or kitchen; written consent; Soul ID. | V01, V15 (his approved V01 line stitched into the 9:16 cut), V03 (fallback only) | From his own photos; no face prose. Real working hands, keys on a fob, tired eyes before sunrise. | 'his own dark quilted jacket over a plain grey fleece, as photographed; no logos, no hi-vis lettering' | His voice memos answering our questions; we transcribe, he approves, the exact words go into Seedance with his memo as @Audio; the real memo is laid in wherever sync allows. He quotes no numbers. | Never use the duplicated 'Ali' reviews (Sarah Byrd, Louise Jones, also on Coventry with the brand swapped); never generate an 'Ali'. If Golden Line, Leam Taxis and Coventry are one operator group, one consenting person may witness for each, captioned with exactly how the businesses connect. |
| **CLIENT_COVENTRY_OWNER** | Owner or manager of Coventry Airport Taxis 247 (unverified; site footer credits SMEK). | real_client; B: 27 photos plus 6–10 photos of his kitchen or back office; written consent. | V02, V04 (optional real voice line over the end only) | From his own photos; no face prose. Kitchen table after a shift: reading glasses only if he really wears them, tea, a charger cable. | 'a plain navy jumper with the sleeves pushed up, as photographed; no logos, no printed text' | Own memo for one approved line (V02); optional voice-only line in V04. | Before any Coventry capture appears on camera: fix the Slough (Global Cars 247, 4.9/202) review widget, settle the SMEK footer, fix 'Qoute' and 'Relaible'. |
| **CLIENT_LEAM_OWNER** | Owner or operator of Leam Taxis (leamingtonspa-taxis.co.uk), a private-hire firm 'operating in Leamington Spa, Warwick and other areas in Mid Warwickshire since 2014' (site's own claim); name unverified. | real_client; B: 27 photos including front-camera selfies, plus photos of his own car and front door; written consent. | V03, V09 | From his own photos; no face prose. | 'a dark fleece zipped to the chin, as photographed; no logos, no printed text' | Own memos (V03 lines, optional one-word V09 reaction). | Gate G3: the 114-calls Business Profile must be confirmed as Leam Taxis' (the site's map embed names a profile 'Leamington Spa Taxis - Airport Transfers', but the screenshot shows no name). Private hire: kerbs and driveways only, never a hackney or station rank. Preferred for V09: he films the real moment on his own phone. |
| **CLIENT_YORK_MANAGER** | York Cars owner or operations manager (nobody named publicly). | real_client; B: 27 photos plus 6–10 wide photos of the real yard and dispatch office (and 2–3 of a real car if any livery is to appear); written consent. | V05 | From their own photos; no face prose. Night-shift energy: a radio earpiece, a lanyard turned round, keys. | 'a dark work jacket over a plain sweatshirt, as photographed; no logos, no company lettering' (a hi-vis vest only if they really wear one in the yard). | Own memo answering our two questions; never described in text. | No premises video at all without York Cars' own photos. Footer credits Xoom Media; Hulk's portfolio lists York Cars. Never York reviewers' names in agency ads. |
| **CLIENT_OF_DIRECTOR** | Organic Fostering director or registered manager (nobody named publicly). | real_client; B: 27 photos plus 6–10 photos of the office at Beaumont House; written consent. | V06 | From their own photos; no face prose. Calm, unhurried; tea that is actually drunk. | 'a soft grey knit cardigan over a plain top, as photographed; lanyard card turned to face the body; no logos, no printed text' | Own memo answering one question; approved transcript. | Adults only: no carers, no children, no case files, no names. No allowance figures at all. The client's 19 real Drive clips may be intercut after a check for superseded figures. |
| **N1_AI_PRESENTER** | Labelled AI case-study narrator: an invented person, approved once by the user. Fallback only, for V01 (B2) and V15. | ai_presenter; A once (Nano Banana Pro sheet, human-realism 13-block order; master_plan.md §3.2), then locked and treated as Mode B with no face prose. | V01 (fallback B2 only), V15 (fallback only) | Around 55, a practical Midlands woman who has run a busy office most of her working life and still laughs easily at the end of a long day. White British, fair warm-toned skin with redness around the nostrils and a few broken capillaries, grey-green eyes, natural brows greying at the tails, chin-length ash-brown hair with grey at the parting, flyaways and a cowlick, a small pale scar through the left eyebrow, thin tortoiseshell reading glasses pushed up into her hair. Deliberately unlike the five polished GRP service presenters: a real cluttered back room, lived-in clothes, no obvious makeup. | 'a moss-green wool cardigan over a cream crew-neck T-shirt, dark jeans, reading glasses pushed up into her hair; no logos, no printed text' | Synthetic, labelled. Casting brief only: warm, unhurried, dry, faintly gravelly; Coventry/Warwickshire accent; mid-fifties; plain-spoken but with a hint of a smile. Never 'the voice of' anyone real. | On screen throughout: 'AI presenter. Real client data. Not a client testimonial.' Third person only; never says 'we'; never quotes a client; never named as a client or as agency staff. Never in 3, 6, 7, 9, 10, 12, 13 or 14. Because her cardigan is green, no chroma-green screen is ever in her frame; her data goes full-frame in the edit. The only presenter in the set (the cap of two is not used). |
| **EXTRA_MODE_C** | Incidental people: drivers' and passengers' hands, a passenger seen from behind, a soft-focus dispatcher, half-cropped passers-by. | extra; C: two lines only (SKIN-C lock). | V01, V02, V04, V05, V11, B-roll bank | 'Real skin texture with visible pores and fine hairs; [one imperfection].' Small, soft-focus or partly cropped; never identifiable. | 'plain dark everyday clothes; no logos, no printed text' | None, or no intelligible words. | Never presented as a named client, a client's driver or customer, or agency staff. |

**If Leam Taxis, Golden Line and Coventry turn out to be one operator group** (Coventry's booking iframe runs on Leam Taxis' dispatch system with the same `site_key`; Golden Line and Coventry share duplicated "Ali" reviews and a phone number: UNVERIFIED), one consenting person may witness for each business. Each clip names only the business whose data is on screen, and the caption says exactly how they connect (e.g. "Owner, Leam Taxis and Golden Line Taxis").

### 3.1 Mode B sheet (all real people)
Use production_rules B.2 verbatim (Nano Banana Pro, 3:2, 4k, count 4; 4 × 3 grid, mid-grey #8C8C8C background, one large soft light overhead and camera-left, 85 mm-style heads and 50 mm-style bodies, "Visible pores and natural skin texture, unretouched" plus one imperfection), filling in the person's wardrobe line above. Build Hassan's from **fresh window-light photos**, not his studio portraits.

### 3.2 N1 sheet (Mode A; only if a fallback in video 1 or 15 is triggered)
```
Character reference sheet of one invented woman, twelve equal panels in a 4 by 3 grid with thin plain mid-grey gutters and no labels, no text, no numbers. Row one, head and shoulders at eye level: front facing with a calm neutral expression; three-quarter view turned to her left; three-quarter view turned to her right; left profile. Row two: full body front, head to feet; full body from behind; full body three-quarter view; both hands held up, backs in one and palms in the other. Row three, head and shoulders: a relaxed half-smile; mid-word as if talking, lips slightly parted; thinking, eyes looking just off camera to the left; close-up of the collar and knit of her cardigan.
Around 55 years old, a practical woman who has run a busy office most of her working life, but clearly someone who still laughs easily at the end of a long day. White British, fair, warm-toned skin with redness around the nostrils and a few broken capillaries on the cheeks, grey-green eyes, natural brows greying at the tails. Chin-length ash-brown hair with grey coming through at the parting, tucked behind one ear, flyaways at the crown and a cowlick at the front hairline. A small pale scar through her left eyebrow. Reading glasses with thin tortoiseshell frames pushed up into her hair.
Maximum realism (skin AND hair): moderate wrinkles, horizontal forehead lines, crow's feet, deepening nasolabial folds, faint under-eye hollows with darker circles, early vertical lip lines, a slightly softened jawline, visible pores, uneven pigmentation and mild darker patches, a few sun spots, peach fuzz along the jaw and upper lip. Do not smooth, soften, rejuvenate or beautify her skin. Detailed irises with visible fibre texture, natural moisture, tiny visible vessels in the sclera, authentic catchlights. Individual hair strands, eyebrow hairs and eyelashes sharply visible. Her hair looks genuinely grown from the scalp, never painted or artificially perfect. The scar has realistic healed tissue texture and slight tonal variation. She carries herself plainly and without fuss; no obvious makeup.
Wearing a moss-green wool cardigan over a cream crew-neck T-shirt, dark jeans, reading glasses pushed up into her hair; no logos, no printed text, in every panel. Seamless neutral mid-grey background (#8C8C8C). One large soft light overhead and slightly to camera-left with even soft fill, gentle natural shadow under the chin and nose, the same light in every panel. Head panels framed like an 85mm portrait lens, body panels like a 50mm lens, no wide-angle distortion. Fine natural photographic grain.
```
If it comes back glossy, remove the "Do not smooth…" sentence first (human-realism, Nano Banana Pro). Once the user approves her, every later prompt treats N1 as Mode B: no face prose. She never appears beside a chroma-green screen (green cardigan).

---

## 4. Brand allocation at a glance

| # | Title | Brand | Placement | Length | Ratios | First takes |
|---|---|---|---|---|---|---|
| V01 | The Four O'Clock Phone | Golden Line Taxis, Warwick (goldenlinetaxiswarwick.co.uk) | Homepage, Case study: Golden Line Taxis | 75 s master at 16:9; 45 s cut at 9:16 | 16:9, 9:16 | 12 |
| V02 | Kitchen Table, Tuesday Night | Coventry Airport Taxis 247 (coventryairporttaxis247.co.uk) | Homepage, Case study: Coventry Airport Taxis 247 | 40 s at 16:9; 40 s duet at 9:16 | 16:9, 9:16 | 7 |
| V03 | A Hundred and Fourteen | Leam Taxis, Leamington Spa (leamingtonspa-taxis.co.uk) | Social: Reels, TikTok, Shorts | 18 s | 9:16 | 3 |
| V04 | May vs August | Coventry Airport Taxis 247 (Google Business Profile) | Case study: Coventry Airport Taxis 247, Social (9:16 version) | 25 s | 9:16, 16:9 | 5 |
| V05 | Night Shift, York | York Cars (yorkcars.co.uk) | Service page: Local SEO | 30 s | 16:9, 9:16 | 7 |
| V06 | The Question | Organic Fostering, Manchester (organicfostering.co.uk) | Service page | 25 s | 16:9, 9:16 | 5 |
| V07 | Four Ways to Say Kenilworth Taxi | Hulk Marketing (team), using Golden Line Taxis data | Social: Reels, TikTok, Shorts | 20 s | 9:16 | 2 |
| V08 | One in Ten | Coventry Airport Taxis 247 (filmed by the agency) | Social: Reels, TikTok, Shorts | 30 s | 9:16 | 3 |
| V09 | Twenty-Five | Leam Taxis, Leamington Spa | Social: Reels, TikTok, Shorts | 15 s | 9:16 | 2 |
| V10 | Hands First | Hulk Marketing / Google Ranker Pro (agency) | Service pages | 30 s per person; three clips to start (T1, T2, then F1 last) | 16:9, 9:16 | 12 |
| V11 | Day One of an Audit Has No Numbers | Zentro (zentro.co.uk), with a Golden Line audit as the fallback subject | Social: Reels, TikTok, Shorts | 20 s | 9:16 | 4 |
| V12 | Month-End | Hulk Marketing (agency), delivering Leam Taxis' September report | Social: Reels, TikTok, Shorts | 30 s | 9:16 | 5 |
| V13 | Why I Show Clients the Real Numbers | Hulk Marketing / Google Ranker Pro (Hassan Pasha) | Homepage hero | 55 s at 16:9; 30 s cut at 9:16 | 16:9, 9:16 | 10 |
| V14 | Tip of the Week, Ep 1: The Edge of Page One | Hulk Marketing (Hassan Pasha); Ep 1 uses Golden Line Taxis data | Social: Reels, TikTok, Shorts | 30 s per episode | 9:16 | 3 |
| V15 | What Moved in Warwick | Golden Line Taxis, Warwick (commentary by Hassan Pasha) | Case study: Golden Line Taxis, Social (9:16 cut) | 40 s at 16:9 and 9:16 | 16:9, 9:16 | 6 |

**Spread:** Golden Line 1, 7, 14, 15 (plus T1's number in 10) · Coventry 2, 4, 8 · Leam Taxis 3, 9, 12 · York Cars 5 · Organic Fostering 6 · Zentro 11 (Golden Line audit as the fallback) · Agency 10, 13. **Not featured:** airporttaxis247.co.uk (not in the client list; avg position 72.6; a separate business on the evidence).

---

## 5. The 15 videos

Generation IDs follow the hand-back naming `grp_v[NN]_[setup]-[shot]_t[take]_[ratio].mp4` (production_rules §9); the ratio suffix is part of the ID here (`v01_A-01_16x9`). `BR` IDs are the shared b-roll bank, generated once and reused. Light, palette and lock names refer to §2. Every generation has a 1 s ambience-only handle at the head and tail.

### V01 · The Four O'Clock Phone

**Client video: testimonial (60–90 s)** · **Brand:** Golden Line Taxis, Warwick (goldenlinetaxiswarwick.co.uk) · **Placement:** Homepage, Case study: Golden Line Taxis · **Length:** 75 s master at 16:9; 45 s cut at 9:16 · **Ratios:** 16:9, 9:16 · **Cast:** CLIENT_GOLDENLINE_OWNER, EXTRA_MODE_C, N1_AI_PRESENTER

**Concept.** A Warwick taxi owner, parked up before sunrise, tells us in his own words what it was like when Google sent no work his way, what changed, and what's different now. Problem (his own car, pre-dawn) → turn (his own back office, laptop open with a green screen; at about 38 s the live footer credit 'Made with ❤ by Hulk Marketing Ltd' is pushed in as proof of the work) → result (the first data receipt lands at 49 s, 65% of the runtime, pushed from his laptop into full frame). The series motif opens and closes it: a phone lighting up face-up on a dark dashboard, its screen never readable. He quotes no numbers: the numbers are ours, on screen and sourced. Golden Line is the only client with a verified Hulk footer credit and an attributed Search Console screenshot.

**Hook.** 16:9: black; a wiper thunks once; a phone lights up face-up on a dark dashboard and buzzes against the plastic (BR01); over it, the first sentence of his real answer about the early runs; no title for 6 s. 9:16 cut: the same image with the totals receipt (312 clicks · 18.2K times shown) on screen by 0.8 s.

**Version A (preferred).** CLIENT_GOLDENLINE_OWNER, Mode B: 27 photos, written consent, our four questions answered as voice memos, transcribed and approved by him; those exact words go into Seedance with his memo as @Audio, and the real memo is laid in as the final track wherever sync allows. DOC-CAM parked-car interview (camera in the passenger seat) and sit-down interview in his real back office, with his own photos as location references.

**Version B (fallback).** B1 (preferred fallback): his real, unaltered voice memo over faceless footage (hands on the wheel, the back of his head against the side window, keys, BR bank), labelled 'Dramatised visuals. Real voice, real data.' B2 (no client participation): N1 tells the case in the third person in her back room ('This is Golden Line Taxis in Warwick. Hulk Marketing built its website. Here's what Google shows for the last three months.'), labelled 'AI presenter. Real client data. Not a client testimonial.'; no quote, no testimonial framing, never 'we'; it becomes a case-study explainer and is described that way. Alternate subject only if Golden Line declines and G3 clears: A's Leam Taxis film (114 calls May–Oct 2026, 25 in September).

**Script.** DRAFT FOR CLIENT APPROVAL. We supply questions, not sentences; every [his words] is replaced by his transcribed, approved answer. Q1 'Before you worked with Hulk, where did your bookings come from, and what was missing?' Q2 'What changed when the new site went live? Say it the way you'd tell another driver.' Q3 'What's different now, day to day?' Q4 'If another taxi firm asked you about it, what would you tell them?' He mentions no numbers, no 'number one', no review wording. TIMING: 0–6 s [his words: first sentence of Q1, voice only over BR01]. 6–24 s v01_A-01 then A-02 [his words: Q1, two lines of 5–8 s]. 24–44 s v01_A-03 [his words: Q2, two lines; only work the G7 log confirms, e.g. 'the new website', which the footer verifies]; footer push-in at ~38 s. 44–66 s v01_A-04 [his words: Q3, two lines] under the receipts. 66–75 s v01_A-05 [his words: Q4, one line], a nod, the phone lights up, BR03 the car pulls away, ambience.

**Seedance 2.5 generations**

| Gen ID | Purpose | Location | Who | Camera / mode | s | Ratio | Prompt essentials |
|---|---|---|---|---|---|---|---|
| `v01_A-01_16x9` | Problem answer, medium (Q1, lines 1–2) | L2 his own car, parked on a Warwick terraced street, pre-dawn | CLIENT_GOLDENLINE_OWNER | DOC-CAM handheld by an operator in the passenger seat; about 60° field, camera 70–90 cm from his face; subtle breathing rhythm; focus on the eyes | 15 | 16:9 | First frame: owner already in the driver's seat of his own parked car, engine off, filling the right half, left hand on top of the wheel, eyes just past camera-left to the interviewer. 0–1 s ambience, breath; 1–7 s line 1 (@Audio 1), glances at the wheel once; 7–8 s pause, thumb rubs the wheel; 8–13 s line 2 (@Audio 2), small nod; 13–15 s looks out at the street, ambience. Phone face-down in the dash mount, parking ticket face-down on the dash, rain beads on the side glass. Light L-TAXI; palette PAL-CAR; TEXT-LOCK; one person; DOC-CAM texture. Worked to B §6.1. |
| `v01_A-02_16x9` | Problem continues, head-and-shoulders (the size change hides the join) | L2 his car, pre-dawn | CLIENT_GOLDENLINE_OWNER | DOC-CAM handheld from the passenger seat, about 47° field, camera 90 cm away leaning against the passenger door; never gimbal-smooth | 12 | 16:9 | Same car, same axis, tighter: head and shoulders from the passenger seat. 0–1 s ambience; 1–7 s line 3 (@Audio), exhales, eyes to the windscreen mid-line; 7–12 s silent: rubs the back of his neck, half-laugh, settles; final second ambience. L-TAXI, PAL-CAR, TEXT-LOCK, DOC-CAM. |
| `v01_A-03_16x9` | Turn answer, seated medium; laptop with green screen at frame edge (Q2) | L2b his own back office, dusk | CLIENT_GOLDENLINE_OWNER | DOC-CAM locked off on a tripod with micro-movement, 47° block (50 mm selector), 2.5 m away; eye-line just past camera-left | 15 | 16:9 | Worked prompt §9.1 of master_plan.md. Owner at the table in his own back office at dusk, laptop open at frame-left with SCREEN-GREEN (four corner dots), mug with a tea ring, phone face-down, radiator under the window, coat on a hook, calendar turned to the wall. Lines at 1 s and 8 s; two-finger tap; sits back. L-HOME; PAL-INT; one person; DOC-CAM. |
| `v01_A-04_16x9` | Result answer, close (Q3) | L2b his back office, dusk | CLIENT_GOLDENLINE_OWNER | DOC-CAM tripod, 29° block (85 mm selector), 3–4 m away, background compressed | 12 | 16:9 | Same room, same axis, close-up. 0–1 s ambience; 1–7 s line (@Audio), eyes drop to the laptop off-frame once and back; 7–11 s silent half-smile, small nod, reaches for the mug and drinks; final second ambience. One imperfection (stubble shadow or a creased collar). L-HOME, PAL-INT, DOC-CAM. |
| `v01_A-05_16x9` | Closing line in the car at first light (Q4) | L2 his car, first light | CLIENT_GOLDENLINE_OWNER | DOC-CAM handheld from the passenger seat, about 60° field | 10 | 16:9 | Back in the parked car, engine now running, first grey light. 0–1 s ambience; 1–6 s last line (@Audio); 6–9 s nod, both hands to the wheel; the phone in the vent mount lights up face-up with its screen edge-on and unreadable, its glow on his fingers; 9–10 s ambience. Car does not move. L-TAXI, PAL-CAR, DOC-CAM. |
| `v01_B-03_16x9` | Hands on the trackpad, green laptop, tea steam (the reveal surface for the receipts) | L2b his back office | CLIENT_GOLDENLINE_OWNER | DOC-CAM static on a tripod, 47° block | 6 | 16:9 | Static close of his right hand resting on the trackpad, laptop SCREEN-GREEN filling two thirds of frame with all four corners and corner dots visible, steam rising from the mug in the soft foreground; one slow scroll gesture with two fingers, then still. No face. SKIN-B for his hand (Mode B). L-HOME, PAL-INT, DOC-CAM. |
| `v01_A-01_9x16` | 9:16 version of the problem answer, from its own 9:16 anchor still | L2 his car, pre-dawn | CLIENT_GOLDENLINE_OWNER | DOC-CAM handheld from the passenger seat | 15 | 9:16 | As v01_A-01 recomposed for vertical: head and chest in the upper two thirds, wheel at the bottom edge, side window behind. Same lines, same timings, same locks. |
| `v01_A-04_9x16` | 9:16 version of the result answer | L2b his back office | CLIENT_GOLDENLINE_OWNER | DOC-CAM tripod, 85 mm selector | 12 | 9:16 | As v01_A-04, vertical close-up with headroom for captions kept clear of the top 12%. |
| `BR01_16x9` | SHARED BANK, series motif: a phone lights up face-up on a dark dashboard pre-dawn (V01 open) | Generic parked car interior, pre-dawn | EXTRA_MODE_C | DOC-CAM static, 47° block | 6 | 16:9 | Camera low across a dark dashboard; a phone lies face-up with its screen edge-on to the lens; at 1 s it lights and buzzes against the plastic, glow on the roof lining; wiper parked mid-glass; rain on the windscreen; 4 s a hand enters and lifts it (Mode C, SKIN-C). Nobody else. L-TAXI, PAL-CAR, TEXT-LOCK, DOC-CAM. |
| `BR01_9x16` | SHARED BANK, the same motif for 9:16 cuts (V01 cut, V12 payoff) | Generic parked car interior, pre-dawn | EXTRA_MODE_C | PHONE-REAR static on the passenger seat | 6 | 9:16 | As BR01_16x9, recomposed vertical; phone in a vent mount, glow on the driver's fingers; nobody's face. |
| `BR02_16x9` | SHARED BANK: wheelie case lifted into a boot under a street lamp (V01 problem) | Generic red-brick terraced street, pre-dawn | EXTRA_MODE_C | DOC-CAM handheld on the shoulder, 47° block | 8 | 16:9 | A's worked prompt 8.2 verbatim structure with the fixes: PAL-EXT, L-STREET-NIGHT, TAXI and VEHICLE locks; driver seen from behind, boot lid hides the plate, suspension dips as the case lands; one person. |
| `BR03_16x9` | SHARED BANK: a plain saloon pulls away from the kerb, plates hidden (V01 close, V15) | Generic Warwick-type terraced street, early morning | nobody | DOC-CAM static on a tripod | 7 | 16:9 | B's worked prompt 6.2: camera static at waist height; a parked hatchback's corner hides the plate; exhaust vapour; indicator; pulls away and turns out of frame; empty wet street. PAL-EXT, L-STREET, TAXI, VEHICLE, no people. |

**Edit plan.** Receipt grammar only (exact crops of the real PNG on a navy #0B1628 card, 12 px radius, one orange #F7931E underline, source and date line, context strip, slow push-in from 102% to 108% over 3–4 s, a soft tick SFX, no redraws, no count-ups, no up-arrows, no Google marks). 0–6 s BR01_16x9 under his first sentence. ~38 s footer push-in: a fresh dated capture of the live footer on goldenlinetaxiswarwick.co.uk ('Made with ❤ by Hulk Marketing Ltd'), source line with the capture date. 49 s: totals crop 24,201,720,110 corner-pinned into v01_B-03's green laptop, pushed to full frame (B's green-laptop push-in); 52 s pagination crop 930,2135,410,40 underlined '744' ('744 different searches'); 56 s brand pill from row 1 (24,904,1318,49): 'brand searches: top two on average (1.8)'; 60 s at most two airport chips: row 20 (24,1837,1318,49) 'airport taxi warwick · avg 5.3' and row 6 (24,1150,1318,49) 'warwick airport taxi · avg 6.1 · 13% click-through' (the airport cluster is V15's win). Source line: 'Google Search Console · goldenlinetaxiswarwick.co.uk · 19 Jul–18 Oct 2026'. Context strip: 'Average position over 3 months. Positions 1–10 are page one.' Impressions are written '18.2K times shown'. Mode B label lower-left throughout: 'AI re-creation made with [Name]'s permission. Their words, their voice. Real data.' End card: 'Website by Hulk Marketing Ltd' + brand per placement. No music under his answers (one sparse licensed bed under the b-roll only). Real dashcam drive into Warwick (RF07) for the result b-roll; fallback generated only from the user's own photo. 9:16 cut: 45 s, number by 0.8 s, captions inside safe zones, −14 LUFS. Never show the site's 'No.1 Taxi Hire' headline; site test pages and re-attributed quotes fixed before any site capture appears.

**Data used (every number traces here).**
- goldenlinetaxiswarwick_gsc_3m.png totals tile crop 24,201,720,110: 312 clicks, 18.2K impressions (19 Jul–18 Oct 2026)
- goldenlinetaxiswarwick_gsc_3m.png pagination crop 930,2135,410,40: '1–25 of 744' queries
- goldenlinetaxiswarwick_gsc_3m.png row 1 (24,904,1318,49): 'golden line taxis warwick' avg position 1.8, 23.3% CTR
- goldenlinetaxiswarwick_gsc_3m.png row 20 (24,1837,1318,49): 'airport taxi warwick' avg 5.3
- goldenlinetaxiswarwick_gsc_3m.png row 6 (24,1150,1318,49): 'warwick airport taxi' avg 6.1, 13% CTR
- Live footer on goldenlinetaxiswarwick.co.uk: 'Made with ❤ by Hulk Marketing Ltd' (client_goldenlinetaxiswarwick.md; recapture dated on publish day)

---

### V02 · Kitchen Table, Tuesday Night

**Client video: results walkthrough (30–45 s)** · **Brand:** Coventry Airport Taxis 247 (coventryairporttaxis247.co.uk) · **Placement:** Homepage, Case study: Coventry Airport Taxis 247 · **Length:** 40 s at 16:9; 40 s duet at 9:16 · **Ratios:** 16:9, 9:16 · **Cast:** CLIENT_COVENTRY_OWNER, T1_SEO

**Concept.** After the last airport run the owner sits at his kitchen table, opens the laptop and sees his three months of Google numbers for the first time. T1's real recorded voice talks him through it from the laptop speaker. One person on camera; his reactions are cut to exact chart moments. It is framed as a 'first look at three months', never as growth, because there is no comparison period. For the first 26 s the data is seen only through his world (corner-pinned on the green laptop); full-frame receipts land from 26 s (65%). Honest close: 'airport transfers coventry' is shown 607 times but averages 22.0, so that's the next one.

**Hook.** 16:9: his face lit by the window and a warm pendant, pulling the laptop closer; T1's voice from the speaker: 'Right, so this is your last three months.' 9:16 duet: top half the real totals tile ('224 clicks', '15.9K') on screen by 0.8 s; bottom half his face leaning in.

**Version A (preferred).** CLIENT_COVENTRY_OWNER, Mode B, on camera with one approved line of his own, plus T1's real recorded voice laid in from the laptop (no generated voice for T1). One identity per generation.

**Version B (fallback).** T1 presents the data (A's Version B): T1 to camera at their own desk (v02_T-01, 15 s, two lines) and turning the laptop towards the lens with a green screen (v02_T-02, 8 s); no owner face, no owner words. If the owner consents to voice only: his real voice memo over R-shots framed from behind his shoulder. No N1 in this video.

**Script.** T1 voice-over from the laptop (agency draft; T1 edits, approves and records it for real): 0–8 s 'Right, so this is your last three months on Google.' 8–16 s 'Two hundred and twenty-four clicks. Shown fifteen point nine thousand times. Five hundred and eight different searches.' 16–22 s 'Top one's airport taxi Coventry: fifteen clicks.' 22–28 s 'Coventry airport taxi is averaging seven. That's page one.' 36–40 s 'Airport transfers Coventry: shown six hundred and seven times, but averaging twenty-two. That's the next one.' OWNER (DRAFT FOR CLIENT APPROVAL): 28–36 s [his words, one line, prompted by 'Which of those searches is the job you want most?'; no numbers].

**Seedance 2.5 generations**

| Gen ID | Purpose | Location | Who | Camera / mode | s | Ratio | Prompt essentials |
|---|---|---|---|---|---|---|---|
| `v02_A-01_16x9` | Over-the-shoulder wide: he sits and pulls the laptop in (the corner-pin surface) | L3 his kitchen table, night | CLIENT_COVENTRY_OWNER | DOC-CAM handheld behind his right shoulder, 47° block, settles static | 10 | 16:9 | First frame: owner already pulling out the chair at his kitchen table at night, kettle behind, car keys in hand. 1–5 s sits, drops the keys beside the laptop, pulls the laptop closer; 5–10 s still, reading; the laptop shows SCREEN-GREEN with four corner dots, camera settles static once it is in place. L-HOME, PAL-INT, TEXT-LOCK, one person, DOC-CAM. |
| `v02_R-01_16x9` | Reaction close: reads, eyebrows lift, leans in | L3 | CLIENT_COVENTRY_OWNER | DOC-CAM tripod, 29° block | 8 | 16:9 | Close-up; screen faces away, GLOW from below kept faint. 0–1 s reading; 1–4 s leans in, eyebrows lift; 4–7 s breathes out through his nose, small nod; final second still. No dialogue. L-HOME + GLOW, PAL-INT, DOC-CAM. |
| `v02_R-02_16x9` | Reaction: small laugh through the nose, rubs his jaw, points at the screen with a pen | L3 | CLIENT_COVENTRY_OWNER | DOC-CAM tripod, 47° block | 6 | 16:9 | Medium close, same axis. Silent: a short laugh through the nose, rubs his jaw with his left hand, picks up a pen and points it towards the screen (screen out of frame), sets it down. L-HOME, PAL-INT, DOC-CAM. |
| `v02_A-02_16x9` | His one approved line, close | L3 | CLIENT_COVENTRY_OWNER | DOC-CAM tripod, 29° block | 10 | 16:9 | Close-up; 0–1 s ambience; 1–7 s his approved line (@Audio), glancing from the screen to the interviewer past camera-left; 7–9 s half-closes the laptop lid, picks up his tea; final second ambience. L-HOME, PAL-INT, DOC-CAM. |
| `v02_D-01_9x16` | Duet bottom half: reads and reacts, silent | L3 | CLIENT_COVENTRY_OWNER | DOC-CAM tripod, 47° block, ratio-specific anchor still | 10 | 9:16 | Vertical, framed head-and-shoulders in the lower half with the top half plain kitchen wall (it is covered by the real screen recording). 1–4 s leans in; 4–7 s eyebrows lift, slow exhale; 7–10 s rubs the back of his neck. L-HOME + GLOW, PAL-INT, DOC-CAM. |
| `v02_D-02_9x16` | Duet bottom half: his approved line | L3 | CLIENT_COVENTRY_OWNER | DOC-CAM tripod | 10 | 9:16 | As D-01 framing; his approved line at 1 s (@Audio); small nod; final second ambience. |
| `BR04_16x9` | SHARED BANK: airport drop-off kerb handover (V02 tail, V15) | Generic airport drop-off kerb, overcast morning | EXTRA_MODE_C | DOC-CAM handheld, 47° block | 8 | 16:9 | Generic airport drop-off zone, no logos or signage: a passenger's hand takes a wheelie-case handle from a driver's hand at an open boot; door thunk; trolley rattle off-screen. Both people seen from the chest down or behind. PAL-EXT, L-STREET, TAXI, VEHICLE, TEXT-LOCK, two people (Mode C). |

**Edit plan.** 16:9: 0–26 s the real data appears only on v02_A-01's green laptop, corner-pinned (glare pass, grain match): a slow real scroll of coventryairporttaxis247_gsc_3m_chart.png (cards + chart 0,121,1300,355), then _full.png rows. Reactions R-01 and R-02 are placed on the exact moments each tile or row appears. From 26 s (65%) full-frame receipts: totals crop 0,121,718,110 ('224 clicks · 15.9K times shown'), pagination 930,2135,410,40 ('508 different searches'), row 1 (24,904,1318,49) 'airport taxi coventry · 15 clicks, top search', row 3 (24,1002,1318,49) 'coventry airport taxi · avg 7.0'; close on row 2 (24,953,1318,49) 'airport transfers coventry · 607 times shown · avg 22.0' as 'the next one'. Row 4's 'one in ten' is left to V08. Labels: 'First look at three months', source line 'Google Search Console · coventryairporttaxis247.co.uk · 19 Jul–18 Oct 2026', context strip 'Average position over 3 months. Positions 1–10 are page one.' On-screen text writes '15.9K', never '15,900'. T1's real recorded VO laid in as if from the laptop speaker (slight speaker EQ). Real Coventry ring-road footage (RF05) and BR04 for the tail. 9:16: duet (C): top half a real slow scroll of the same captures; bottom half D-01/D-02; split at 50%; number by 0.8 s. Mode B label throughout. Gates before release: owner consent, Coventry credit (SMEK footer), Slough review widget removed from the site, typos fixed.

**Data used (every number traces here).**
- coventryairporttaxis247_gsc_3m_chart.png cards + chart 0,121,1300,355; totals 0,121,718,110: 224 clicks, 15.9K impressions, 1.4% CTR, avg position 18.4 (19 Jul–18 Oct 2026)
- coventryairporttaxis247_gsc_3m_full.png pagination 930,2135,410,40: '1–25 of 508'
- coventryairporttaxis247_gsc_3m_full.png row 1 (24,904,1318,49): 'airport taxi coventry' 15 clicks, 343 impressions, avg 13.6
- coventryairporttaxis247_gsc_3m_full.png row 3 (24,1002,1318,49): 'coventry airport taxi' 8 clicks, 95 impressions, 8.4% CTR, avg 7.0
- coventryairporttaxis247_gsc_3m_full.png row 2 (24,953,1318,49): 'airport transfers coventry' 12 clicks, 607 impressions, avg 22.0

---

### V03 · A Hundred and Fourteen

**Client video: milestone (15–20 s)** · **Brand:** Leam Taxis, Leamington Spa (leamingtonspa-taxis.co.uk) · **Placement:** Social: Reels, TikTok, Shorts · **Length:** 18 s · **Ratios:** 9:16 · **Cast:** CLIENT_LEAM_OWNER, EXTRA_MODE_C

**Concept.** At the end of a night shift the owner walks from his parked car to his front door, filming himself on his front camera, and says the number in his own words. A cumulative count is the only milestone the data proves without a comparison period: 114 calls made from the Business Profile, May–Oct 2026, with September the best of the six months shown at 25. It sets up V09's stitch.

**Hook.** Frame 1: front camera already on his face mid-step, a second phone buzzing in his pocket (sound). The '114' headline crop is on screen by 0.8 s with its source line.

**Version A (preferred).** CLIENT_LEAM_OWNER, Mode B selfie walk with his own memo as @Audio; split into two generations of 10 s or less (C's 14 s walk was too long), cutting on his arrival at the door.

**Version B (fallback).** If G3 fails (the 114-calls profile is not Leam Taxis'): B's Golden Line Kenilworth selfie (CLIENT_GOLDENLINE_OWNER at a Kenilworth car park, signage out of frame, one 12 s PHONE-SELFIE generation plus real Kenilworth footage RF03), reworded without 'now' or 'first': on screen 'kenilworth taxis: page one on average, 6.7 over the last three months' (row 4). No-face version: a phone-in-hand POV walk from the car to a front door with his real voice note.

**Script.** DRAFT FOR CLIENT APPROVAL (line shapes only; he rewrites in his own words and records them; numbers as words). v03_S-01, 1–8 s: [his words, e.g. 'A hundred and fourteen calls off our Google listing, May to October.']. v03_S-02, 1–6 s: [his words, e.g. 'September was the best of the lot. Twenty-five.'], then a small laugh. Not allowed: 'first', 'now', 'just hit', 'number one', 'best month since May', growth.

**Seedance 2.5 generations**

| Gen ID | Purpose | Location | Who | Camera / mode | s | Ratio | Prompt essentials |
|---|---|---|---|---|---|---|---|
| `v03_S-01_9x16` | Selfie walk from the parked car along a wet terraced street at night, line 1 | L7b Leamington terraced street, night, drizzle | CLIENT_LEAM_OWNER | PHONE-SELFIE handheld walking, 24 mm selector, about 80° field, arm's length, gentle step bob, one re-grip | 10 | 9:16 | First frame: his face close in the front camera, mid-step, wet Leamington-type terraced street behind (Regency stucco, house numbers and signs soft or out of frame). 0–1 s footsteps, breath visible; 1–8 s line 1 (@Audio), eyes flick between lens and screen; a phone buzzes in his pocket at 3 s; 8–10 s keeps walking, ambience. L-STREET-NIGHT, PAL-EXT, TEXT-LOCK, one person, PHONE-SELFIE handheld lines. |
| `v03_S-02_9x16` | Stopped under his porch light at the front door, line 2 ('twenty-five') | L7b his front door, night | CLIENT_LEAM_OWNER | PHONE-SELFIE handheld, standing, auto exposure breathes as the porch light enters frame | 8 | 9:16 | First frame: he has stopped at his front door under a porch light, keys in his free hand. 1–6 s line 2 (@Audio); small laugh through the nose; 6–8 s turns the key, ambience. Porch light is the key (warm), street lamp behind; no house number visible. PAL-EXT, TEXT-LOCK, PHONE-SELFIE. |
| `v03_B-01_9x16` | His hand shuts the car door; key fob; indicators blink once | L7b kerb outside his house, night | CLIENT_LEAM_OWNER | PHONE-REAR handheld at chest height | 5 | 9:16 | Close on a plain dark saloon's driver door at the kerb; his hand pushes it shut (thunk, the body rocks); he presses the fob; the orange indicators blink once on the wet paint; plate out of frame. Mode B hand (SKIN-B). PAL-EXT, L-STREET-NIGHT, TAXI, VEHICLE, TEXT-LOCK. |

**Edit plan.** 0–0.8 s: the '114' headline crop (20,165,240,80) full width with the source line 'Calls made from your Business Profile · May–Oct 2026 · October part month'. Then the chart crop (15,165,910,310) mask-reveals left to right in the upper half under his walk (a reveal of the real pixels, no redraw). Punch-in to 120% on the September tooltip crop (735,278,100,55) on his word 'twenty-five'; caption 'September: 25 calls, the best of the six months shown.' Jump cut at the S-01/S-02 join with a 108% punch. B-01 at 0.5 s as a 0.6 s flash cut, or as the last beat. Handles trimmed from the social cut; captions inside the safe zones; −14 LUFS; Mode B label. V09 stitches 1.5 s of the 'twenty-five' moment. Reuse on case-study pages in the 16:9 'phone clip beside receipts' layout.

**Data used (every number traces here).**
- leamingtonspa_gbp_calls_may-oct2026.png headline crop 20,165,240,80: 114 calls made from the Business Profile, May–Oct 2026 (October part month)
- leamingtonspa_gbp_calls_may-oct2026.png chart crop 15,165,910,310 and Sept tooltip 735,278,100,55: 25 calls, September 2026 (exact)
- Fallback only: goldenlinetaxiswarwick_gsc_3m.png row 4 (24,1051,1318,49): 'kenilworth taxis' avg 6.7, 291 impressions

---

### V04 · May vs August

**Client video: before and after (20–30 s)** · **Brand:** Coventry Airport Taxis 247 (Google Business Profile) · **Placement:** Case study: Coventry Airport Taxis 247, Social (9:16 version) · **Length:** 25 s · **Ratios:** 9:16, 16:9 · **Cast:** EXTRA_MODE_C

**Concept.** Twin plates from one anchor still, hands only, identical overcast light, so the eye reads the difference as activity, not weather. 'May': a parked car on a wet Coventry kerb, the phone dark in its vent mount, fingers drumming on the wheel, a wiper sweep. 'August': the same frame, the phone lighting up twice, the hand lifts it from the mount; the car stays parked. Then the real Business Profile chart rises between them, revealed month by month in sync with the cuts, the May and August points ringed. It counts interactions, not calls, and it says honestly that the line settled after August. Labelled 'Dramatised reconstruction · Real data'.

**Hook.** 0–2 s split screen with edit labels 'May 2026' / 'Aug 2026' and the hook card 'May: almost nothing. August: 32.' (32 is the gridline the August marker sits on).

**Version A (preferred).** No face needed: Mode C hands in both plates, so A and B are the same film. Optional: CLIENT_COVENTRY_OWNER's real voice memo line over the last 3 s (no generation).

**Version B (fallback).** Same plates with no voice. Optional add-on 4b (C): a vertical wipe from York Cars' old homepage (Wayback snapshot 20250916232610, captured by the user in a normal browser) to the live site (assets/sites/yorkcars/now_mobile_full.png), only once York Cars confirms who did the November 2025 rebuild (footer credits Xoom Media). Never a mocked-up 'before'.

**Script.** No dialogue in the plates. Optional owner voice line (DRAFT FOR CLIENT APPROVAL): [his words about the summer, recorded as a voice memo; e.g. 'August was busy.']; never 'it kept climbing'.

**Seedance 2.5 generations**

| Gen ID | Purpose | Location | Who | Camera / mode | s | Ratio | Prompt essentials |
|---|---|---|---|---|---|---|---|
| `v04_P-01_9x16` | 'May' plate: phone dark in the mount, fingers drum, one wiper sweep | L4 generic parked car on a wet Coventry kerb near a ring-road slip road, overcast | EXTRA_MODE_C | PHONE-REAR static, 24 mm selector | 8 | 9:16 | Worked prompt §9.3. Generate the anchor still first. Camera static, wedged on the passenger seat at chest height, looking across at the driver's hands on the wheel and a phone in a vent mount, its screen edge-on to the lens. 0–1 s ambience; 1–5 s fingers drum on the wheel; 5–6 s the wiper sweeps once; 6–8 s hands still. Driver seen from chest down (Mode C, SKIN-C). L-CAR-DAY, PAL-CAR, TEXT-LOCK, engine off. |
| `v04_P-02_9x16` | 'August' plate: same anchor still; the phone lights up twice; the hand lifts it from the mount | L4 same | EXTRA_MODE_C | PHONE-REAR static, same position | 8 | 9:16 | Built from the identical v04_P-01 anchor still (same framing, same overcast light, same rain). 0–1 s ambience; 1–2 s the phone lights and buzzes, glow on the fingers and the dash (screen edge-on, unreadable); 3–4 s lights again; 4–7 s the hand lifts it out of the mount towards the driver's ear, out of frame top; the car stays parked, engine off. L-CAR-DAY, PAL-CAR, TEXT-LOCK. |
| `v04_P-01_16x9` | 'May' plate for the case-study cut | L4 | EXTRA_MODE_C | PHONE-REAR static | 8 | 16:9 | As v04_P-01_9x16 from its own 16:9 anchor still: wider, wheel, mount and windscreen with the wiper in frame. |
| `v04_P-02_16x9` | 'August' plate for the case-study cut | L4 | EXTRA_MODE_C | PHONE-REAR static | 8 | 16:9 | As v04_P-02_9x16 from the identical 16:9 'May' anchor still. |
| `v04_B-01_9x16` | End beat: a hand turns a face-down phone face-up on the dash | L4 | EXTRA_MODE_C | PHONE-REAR handheld, near-static | 5 | 9:16 | Close: phone face-down on the dashboard; a hand turns it face-up (screen edge-on, glow only); rain on the windscreen behind. Mode C. L-CAR-DAY, PAL-CAR, TEXT-LOCK. |

**Edit plan.** 0–2 s split screen, P-01 left / P-02 right (anchor-matched), labels 'May 2026' / 'Aug 2026' and hook card. 2–14 s the plates play (dissolve on the identical composition in the 16:9 version). 14–22 s the real chart crop (40,175,890,310) rises between them; a vertical mask reveals it month by month in sync with the cuts; orange rings on the May and August markers; '79' headline crop (40,175,210,80) underlined; the time-period selector crop (367,58,246,50) as proof of the dates. Card: '79 Business Profile interactions, May–Oct 2026'. Context strip: 'Interactions = calls, chat clicks, bookings and website clicks, not just calls. Peaked in August, then settled. October is a part month.' Only 79 and the 32 gridline are typed; other months are never stated (pixel estimates). 22–25 s v04_B-01. Label 'Dramatised reconstruction · Real data'. Gate G3: the profile must be confirmed as Coventry Airport Taxis 247's, and we ask for the Calls tab and per-type breakdown. −14 LUFS for the 9:16.

**Data used (every number traces here).**
- coventry_gbp_interactions_may-oct2026.png headline + chart 40,175,890,310: 79 interactions May–Oct 2026; May near 0; August marker on the 32 gridline
- coventry_gbp_interactions_may-oct2026.png '79' crop 40,175,210,80 and time-period selector 367,58,246,50
- Optional 4b: Wayback snapshot 20250916232610 of yorkcars.co.uk (to be captured by the user) and assets/sites/yorkcars/now_mobile_full.png

---

### V05 · Night Shift, York

**Client video: premises / team tour (30 s)** · **Brand:** York Cars (yorkcars.co.uk) · **Placement:** Service page: Local SEO · **Length:** 30 s · **Ratios:** 16:9, 9:16 · **Cast:** CLIENT_YORK_MANAGER, EXTRA_MODE_C

**Concept.** On a wet Saturday night the York Cars manager walks us from the yard, through the door, into dispatch, where York's night runs through one room. Built only from York Cars' own photos of the yard and office; without them there is no premises video. The payoff is context, not an agency result: 2,695 Google reviews shown on the site, and a page for each of 15 suburbs and villages and 13 airports.

**Hook.** A car door thunks in a wet yard; the manager is already mid-stride, looking back at the camera, first line.

**Version A (preferred).** CLIENT_YORK_MANAGER, Mode B, with York Cars' own premises photos as @Image location references and, if a livery is to appear, a real car photo as an @Image prop (every letter checked in QC; composite the real logo if any letter warps). Walk-and-talk split into two generations of 14 s, cutting on the doorway.

**Version B (fallback).** No York Cars photos: no premises video at all (B). Photos but the manager will not appear: a POV walk-round with only hands in frame and their real voice memo. Never generic footage presented as York Cars' office or fleet.

**Script.** DRAFT FOR CLIENT APPROVAL. Questions only; they answer in a voice memo, we transcribe, they approve: Q1 'What does a Saturday night look like here?' (line 1, W-01) Q2 'What do customers ask for most?' (line 2, W-02). They mention no numbers, no 'largest fleet', no 'number one'.

**Seedance 2.5 generations**

| Gen ID | Purpose | Location | Who | Camera / mode | s | Ratio | Prompt essentials |
|---|---|---|---|---|---|---|---|
| `v05_W-01_16x9` | Walk-and-talk, yard to the doorway, line 1 | L5 York Cars' real yard (client photos), night, drizzle | CLIENT_YORK_MANAGER | PHONE-REAR handheld, walking a step behind and to the side (not backwards), gentle step bob, autofocus hunts once | 14 | 16:9 | First frame: the manager mid-stride across the wet yard, glancing back at camera; a generic dark people carrier with its door just shut behind (plates hidden, no livery unless from their photo). 1–7 s line 1 (@Audio); 7–12 s keeps walking, reaches the office door, pulls it open; 12–14 s light spills out, ambience. Yard lamp is the key (L-STREET-NIGHT), PAL-EXT, TAXI, VEHICLE, TEXT-LOCK, one person. |
| `v05_W-02_16x9` | Walk-and-talk, inside the doorway to the dispatch room, line 2 | L5 York Cars' real dispatch office (client photos) | CLIENT_YORK_MANAGER, EXTRA_MODE_C | PHONE-REAR handheld, slow walk then stop | 14 | 16:9 | First frame: just inside the door, the manager turning back to camera, dispatch room ahead: radios on chargers, keys on hooks, monitors facing away (SCREEN-SOFT), a kettle, a coat on a chair; one dispatcher seen from behind in soft focus (Mode C). 1–7 s line 2 (@Audio); 7–12 s stops by the desk, rests a hand on it; 12–14 s ambience: radio crackle with no intelligible words. L-PREMISES, PAL-INT, TEXT-LOCK, two people. |
| `v05_W-01_9x16` | 9:16 version of the yard walk | L5 yard | CLIENT_YORK_MANAGER | PHONE-REAR handheld | 14 | 9:16 | As v05_W-01_16x9 from its own 9:16 anchor still. |
| `v05_W-02_9x16` | 9:16 version of the dispatch-room walk | L5 dispatch office | CLIENT_YORK_MANAGER, EXTRA_MODE_C | PHONE-REAR handheld | 14 | 9:16 | As v05_W-02_16x9 from its own 9:16 anchor still. |
| `v05_B-01_16x9` | Insert: dispatcher's hands on a radio handset and keyboard, monitors soft | L5 dispatch office | EXTRA_MODE_C | PHONE-REAR handheld, near-static | 6 | 16:9 | Close on hands: one lifts a radio handset from its charger, the other types; monitors behind are SCREEN-SOFT; a tea-stained mug. Mode C. L-PREMISES, PAL-INT, TEXT-LOCK. |
| `v05_B-01_9x16` | 9:16 version of the dispatcher insert | L5 | EXTRA_MODE_C | PHONE-REAR handheld | 6 | 9:16 | As v05_B-01_16x9, vertical. |
| `v05_B-02_16x9` | Insert: the manager opens a car's rear door in the yard, checks the child seat, closes it | L5 yard | CLIENT_YORK_MANAGER | PHONE-REAR handheld | 8 | 16:9 | Three-quarter rear (plates hidden): opens the rear door, presses the child seat's base, shuts the door; the suspension settles. PAL-EXT, L-STREET-NIGHT, TAXI, VEHICLE, TEXT-LOCK. |

**Edit plan.** Problem/turn/result for a premises film: 0–14 s W-01; 14–20 s W-02 to the doorway line; first receipt at 20 s (67%) over v05_B-01: a fresh dated capture of the review widget on yorkcars.co.uk showing '2,695' Google reviews ('Google reviews shown on yorkcars.co.uk, captured [date]'); 24–30 s real York night footage (RF04: York Station frontage, the Minster soft and far) with a capture of the site navigation: 'A page for each of 15 suburbs and villages, and 13 airports'. Caption on both: 'Context, not an agency result.' No star average; no 'largest fleet' or 'Happy Users' claims; no York reviewers' names; no clock stamps; no livery unless from their photos. Mode B label. Gates: Xoom Media vs Hulk credit, which address is the dispatch office, York Cars' photos and consent.

**Data used (every number traces here).**
- yorkcars.co.uk review widget: 2,695 Google reviews (client_yorkcars.md, verified 22 Oct 2026; recapture dated on publish day)
- yorkcars.co.uk navigation: 15 suburb/village pages (Haxby, Fulford, Heworth, Heslington, Rawcliffe, Huntington, Clifton, Rufforth, Acomb, Copmanthorpe, Bishopthorpe, Wigginton, Strensall, Stamford Bridge, Riccall) and 13 airport pages (client_yorkcars.md)

---

### V06 · The Question

**Client video: client FAQ (20–30 s)** · **Brand:** Organic Fostering, Manchester (organicfostering.co.uk) · **Placement:** Service page · **Length:** 25 s · **Ratios:** 16:9, 9:16 · **Cast:** CLIENT_OF_DIRECTOR

**Concept.** One plain question on screen, 'What was it actually like working with Hulk?', answered by the director or registered manager at the office table in Beaumont House, a bus passing soft in the window on the A56 behind. Adults only. The evidence is structural and true: real captures of the rebuilt site (postcode check, guides index) and the card '61 pages · 32 plain-English guides'. No performance data exists, so no traffic or enquiry claim, and no allowance figures at all.

**Hook.** A plain question card (never a fake comment bubble) over real Chester Road footage with a bus passing in drizzle.

**Version A (preferred).** CLIENT_OF_DIRECTOR, Mode B, at their real office (client photos as location references), own memo as @Audio. The client's 19 real Drive clips may be intercut after a check for superseded figures.

**Version B (fallback).** The manager's approved two-sentence written statement shown as text over b-roll (RF06 Chester Road, v06_B-01 hands, the client's Drive clips); no face, no voice. Context line 'Site structure, not traffic results.' B's Version C (N1 saying 'what we built') is deleted.

**Script.** DRAFT FOR CLIENT APPROVAL. One question, answered in their own words in a voice memo, transcribed and approved: 'What was it actually like working with Hulk?' Part 1 (A-01, two lines of 5–8 s): [their words]. Part 2 (A-02, one line): [their words]. They may mention the guides and the postcode check; no income or allowance figures, no '24/7', no Ofsted grade unless the report PDF has been checked.

**Seedance 2.5 generations**

| Gen ID | Purpose | Location | Who | Camera / mode | s | Ratio | Prompt essentials |
|---|---|---|---|---|---|---|---|
| `v06_A-01_16x9` | Answer part 1, medium, window behind with a bus passing soft | L6 office, Beaumont House, Old Trafford (client photos) | CLIENT_OF_DIRECTOR | DOC-CAM tripod with micro-movement, 47° block | 14 | 16:9 | First frame: seated at the office table, mug of tea in hand, eyes just past camera-left; window behind onto a wet main road, a bus passing soft at 9 s (no readable livery or destination). 1–7 s line 1 (@Audio), sets the mug down; 7–13 s line 2 (@Audio); final second ambience. Plain notebook, plant that needs water, lanyard turned round. L-OFFICE, PAL-INT, TEXT-LOCK, one person, DOC-CAM. |
| `v06_A-02_16x9` | Answer part 2, close, half-smile, sip of tea | L6 | CLIENT_OF_DIRECTOR | DOC-CAM tripod, 29° block | 9 | 16:9 | Close-up, same axis. 1–6 s final line (@Audio); 6–8 s half-smile, small nod, sip of tea; final second ambience. L-OFFICE, PAL-INT, DOC-CAM. |
| `v06_A-01_9x16` | 9:16 version of part 1 | L6 | CLIENT_OF_DIRECTOR | DOC-CAM tripod | 14 | 9:16 | As v06_A-01_16x9 from its own 9:16 anchor still; window and bus above the shoulder. |
| `v06_A-02_9x16` | 9:16 version of part 2 | L6 | CLIENT_OF_DIRECTOR | DOC-CAM tripod | 9 | 9:16 | As v06_A-02_16x9, vertical close. |
| `v06_B-01_16x9` | Hands: pen on a blank notebook page, a mug | L6 | CLIENT_OF_DIRECTOR | DOC-CAM static, 29° block | 5 | 16:9 | Close on their hands writing on a blank page (no readable words), mug steaming in the foreground. SKIN-B hands. L-OFFICE, PAL-INT, TEXT-LOCK. |

**Edit plan.** 0–2 s plain question card over real Chester Road footage with a bus (RF06; never a tram). 2–16 s A-01. 16–20 s (64%) real site scroll insert from assets/sites/organicfostering/now_desktop_full.png and now_mobile.png (postcode check, guides index), then the card '61 pages · 32 plain-English guides' with source 'organicfostering.co.uk/sitemap.xml · lastmod 13 Sep 2026' and context 'Site structure, not traffic results.' 20–25 s A-02. Organic Fostering brand colours only on its own receipt card. Client Drive clips may replace RF06. No allowance figures (neither the superseded £447.60 nor the live rate). Mode B label. Gates: who built the Sept 2026 rebuild (Hulk's portfolio lists the GoHighLevel enquiry platform), permission to name Hulk, Ofsted grade only after checking the report PDF.

**Data used (every number traces here).**
- organicfostering.co.uk/sitemap.xml: 61 URLs including 32 blog guides, lastmod 13 Sep 2026 (client_organicfostering.md)
- assets/sites/organicfostering/now_desktop_full.png and now_mobile.png (captured 22 Oct 2026)

---

### V07 · Four Ways to Say Kenilworth Taxi

**UGC: 'What I learned from SEO' selfie (20 s)** · **Brand:** Hulk Marketing (team), using Golden Line Taxis data · **Placement:** Social: Reels, TikTok, Shorts · **Length:** 20 s · **Ratios:** 9:16 · **Cast:** T1_SEO

**Concept.** T1 walks out of their real workplace in drizzle and tells their phone the most useful thing they learned this month: in the same three months, on the same taxi site, four ways of typing 'Kenilworth taxi' sat at four different average positions (6.7, 8.5, 8.6, 16.4). Tiny wording differences behave like separate searches, so you check every variant. Each number gets a punch-in and its own receipt as it is spoken.

**Hook.** The row 4 receipt 'kenilworth taxis · 6.7' is on screen by 0.5 s, then row 13 '16.4' snaps in beside it; T1 is already mid-step on the front camera.

**Version A (preferred).** T1_SEO, Mode B, walking selfie outside their real workplace, own memo as @Audio. Two generations of 12 s or less.

**Version B (fallback).** T1's real recorded voice over hands typing the four variants into a notes app on a phone with a green screen (one 8 s PHONE-REAR generation, only if used); no face. No AI version.

**Script.** Agency draft (T1 edits, approves and records; numbers as words). v07_A-01: 1–6 s 'Thing I learned this month. Same taxi firm, same town, same three months.' 6–11 s 'Kenilworth taxis: six point seven. Kenilworth taxi, no S: sixteen point four.' v07_A-02: 1–5 s 'Taxi Kenilworth: eight point six. Taxis Kenilworth: eight point five.' 5–9 s 'Four ways to say it. Four different searches. So I check every one.'

**Seedance 2.5 generations**

| Gen ID | Purpose | Location | Who | Camera / mode | s | Ratio | Prompt essentials |
|---|---|---|---|---|---|---|---|
| `v07_A-01_9x16` | Walking selfie, lines 1–2 | L9 street outside T1's real workplace, drizzle | T1_SEO | PHONE-SELFIE handheld walking, 24 mm selector, gentle step bob | 12 | 9:16 | First frame: T1's face close in the front camera, mid-step on a wet pavement outside their real workplace, a bus shelter behind with an unreadable advert. 1–6 s line 1 (@Audio); 6–11 s line 2 (@Audio), eyes flick to the screen; re-grip once at 6 s; final second ambience. L-STREET, PAL-EXT, TEXT-LOCK, one person, PHONE-SELFIE handheld lines. |
| `v07_A-02_9x16` | Stopped at a crossing, lines 3–4; the crossing beeps; small laugh | L9 same street | T1_SEO | PHONE-SELFIE handheld, standing; auto exposure breathes as the bright sky enters frame | 10 | 9:16 | First frame: stopped at a pedestrian crossing, face close, traffic soft behind. 1–5 s line 3; 5–9 s line 4; the crossing beeps at 9 s, a small laugh, steps off; final second ambience. L-STREET, PAL-EXT, TEXT-LOCK, PHONE-SELFIE. |

**Edit plan.** Number by 0.5 s (row 4 receipt). Each variant gets a 105–108% punch-in on the word and its own receipt stacked in the upper third, position cell ringed: row 4 (24,1051,1318,49) 6.7; row 13 (24,1493,1318,49) 16.4; row 14 (24,1542,1318,49) 8.6; row 19 (24,1788,1318,49) 8.5. Context strip: 'Average positions · Golden Line Taxis Warwick · Google Search Console · 19 Jul–18 Oct 2026.' Real Kenilworth footage (RF03) as a 1.5 s cutaway under the numbers. Captions word-timed inside the safe zones; −14 LUFS; Mode B label. No AI version.

**Data used (every number traces here).**
- goldenlinetaxiswarwick_gsc_3m.png row 4 (24,1051,1318,49): 'kenilworth taxis' avg 6.7
- goldenlinetaxiswarwick_gsc_3m.png row 13 (24,1493,1318,49): 'kenilworth taxi' avg 16.4
- goldenlinetaxiswarwick_gsc_3m.png row 14 (24,1542,1318,49): 'taxi kenilworth' avg 8.6
- goldenlinetaxiswarwick_gsc_3m.png row 19 (24,1788,1318,49): 'taxis kenilworth' avg 8.5

---

### V08 · One in Ten

**UGC: screen recording with voiceover (30 s)** · **Brand:** Coventry Airport Taxis 247 (filmed by the agency) · **Placement:** Social: Reels, TikTok, Shorts · **Length:** 30 s · **Ratios:** 9:16 · **Cast:** T1_SEO, EXTRA_MODE_C

**Concept.** T1 films their own laptop on their phone at the agency desk and talks through one honest idea: 'coventry airport transfers' is averaging position 6.0 over three months, and about one in ten times it's shown, someone clicks. Small numbers, said candidly. The user's 'this keyword just hit position 3' becomes 'is averaging': no row sits at 3 and there is no comparison period. The voice is T1's real phone recording; only the picture is generated.

**Hook.** 0–0.8 s the real row pops full width: 'coventry airport transfers · avg 6.0 · 10.5% CTR'.

**Version A (preferred).** Faceless by design: T1's hands (Mode C wording) and T1's real recorded voice. Any consenting team member's real voice can stand in.

**Version B (fallback).** If Coventry is not cleared: A's Golden Line version on rows 20, 6 and 7 ('airport taxi warwick' averaging 5.3; 'warwick airport taxi' 6.1 at 13% CTR), with no invented specifics. Optional upgrade preferred over generation: the user films the real laptop on a real phone.

**Script.** Agency draft (T1 edits, approves and records on their phone; numbers as words): 0–6 s 'Coventry airport transfers. Averaging position six over the last three months.' 6–12 s 'That's page one. And about one in ten times it's shown, someone clicks.' 12–18 s 'Small numbers: seventy-six times shown. Eight clicks.' 18–24 s 'Coventry airport taxi, averaging seven.' 24–30 s 'No just hit here. These are three-month averages.'

**Seedance 2.5 generations**

| Gen ID | Purpose | Location | Who | Camera / mode | s | Ratio | Prompt essentials |
|---|---|---|---|---|---|---|---|
| `v08_P-01_9x16` | Phone filming the laptop: green screen with corner dots, hand scrolls slowly | L1 agency desk by the window | EXTRA_MODE_C | PHONE-REAR handheld near-static at chest height, autofocus hunts once | 14 | 9:16 | Over-the-shoulder phone view of a laptop on the agency desk, SCREEN-GREEN with four corner dots filling the middle of frame; a hand on the trackpad scrolls slowly twice; the orange mug's edge in the foreground; rain on the window beyond. Mode C hand (SKIN-C). L-OFFICE, PAL-INT + AGENCY ADD-ON, TEXT-LOCK, no faces. |
| `v08_P-02_9x16` | Tilt off the laptop to the rainy window and the mug | L1 | nobody | PHONE-REAR handheld tilt | 6 | 9:16 | Starts on the laptop's green lower edge, tilts up and right to the window (rain, grey sky, slight flare and haze) and the orange mug with a chipped rim. PAL-INT + AGENCY ADD-ON, L-OFFICE, TEXT-LOCK. |
| `v08_P-03_9x16` | Close on the laptop's lower half, green, one finger tap | L1 | EXTRA_MODE_C | PHONE-REAR handheld, held still | 8 | 9:16 | Close on the lower half of the green screen and keyboard; one finger taps the trackpad once at 4 s; static. SCREEN-GREEN, L-OFFICE, PAL-INT. |

**Edit plan.** 0–0.8 s row 4 receipt (24,1051,1318,49). 1–20 s: P-01's green replaced by a real slow scroll of coventryairporttaxis247_gsc_3m_full.png (header + top 5, 24,847,1318,303), row 4 highlighted, with C's keying spec: corner pin on the four dots, a glare pass, a 1–2 px chromatic edge, faint moiré, grain match. 20–26 s P-03 with row 3 (24,1002,1318,49) 'coventry airport taxi · avg 7.0' keyed. 26–30 s P-02. Context strip: 'Average position over 3 months, 19 Jul–18 Oct 2026. No earlier period to compare, so no "just hit".' Label 'Illustrative footage. Real data. Real voice.' Captions word-timed; −14 LUFS. Gate: Coventry credit (SMEK) before any 'we' wording; the VO itself claims no credit.

**Data used (every number traces here).**
- coventryairporttaxis247_gsc_3m_full.png row 4 (24,1051,1318,49): 'coventry airport transfers' 8 clicks, 76 impressions, 10.5% CTR, avg 6.0
- coventryairporttaxis247_gsc_3m_full.png row 3 (24,1002,1318,49): 'coventry airport taxi' avg 7.0
- coventryairporttaxis247_gsc_3m_full.png header + top 5 crop 24,847,1318,303

---

### V09 · Twenty-Five

**UGC: reaction clip (15 s)** · **Brand:** Leam Taxis, Leamington Spa · **Placement:** Social: Reels, TikTok, Shorts · **Length:** 15 s · **Ratios:** 9:16 · **Cast:** CLIENT_LEAM_OWNER

**Concept.** The owner, parked on a Leamington terraced street between jobs (never on a rank), opens the monthly report T2 sends in V12 on his phone. His dash-mounted phone films him. The reaction is understated: reads, scrolls back, one breath of a laugh, maybe one word, looks out at the rain. Labelled as a re-creation. Best of all, the owner films the real moment himself next month and we use that instead.

**Hook.** A 1.5 s stitch of V03 ('…twenty-five') with the September tooltip receipt on screen by 0.8 s, then a hard cut into his car.

**Version A (preferred).** CLIENT_LEAM_OWNER, Mode B, front camera propped on the dash (the propped-camera texture test runs on this shot first), own memo for an optional one-word reaction.

**Version B (fallback).** Preferred over generation: the owner's own phone clip of the real moment. Otherwise hands only: his phone on the steering wheel (green screen), the real tooltip keyed in, his real voice reacting off-screen or no voice. Never an AI narrator.

**Script.** DRAFT FOR CLIENT APPROVAL: optional reaction in his own words, e.g. [one word: 'Twenty-five.'], recorded as a voice memo. Never 'best month since May'.

**Seedance 2.5 generations**

| Gen ID | Purpose | Location | Who | Camera / mode | s | Ratio | Prompt essentials |
|---|---|---|---|---|---|---|---|
| `v09_R-01_9x16` | Reaction in the parked car, phone propped on the dash | L7 his own car parked on a Leamington terraced street, afternoon drizzle | CLIENT_LEAM_OWNER | PHONE-SELFIE propped in a dash mount at chest height, static, faint vibration only | 10 | 9:16 | Worked prompt §9.2 (runs the propped-camera test: TEST A vs CONTROL, logged). He reads a phone held low (screen away, GLOW), scrolls back, short laugh, optional word at 5 s, rubs the back of his neck, looks out at the rain. Engine off, seatbelt off. L-CAR-DAY + GLOW, PAL-CAR, TEXT-LOCK, one person. |
| `v09_B-01_9x16` | Insert: phone held on the wheel, green screen, thumb scrolls once | L7 | CLIENT_LEAM_OWNER | PHONE-REAR over the shoulder, held still | 5 | 9:16 | Over the shoulder: his phone held at the top of the steering wheel, SCREEN-GREEN with four corner dots, thumb on the side of the phone, one scroll at 2 s; rain on the windscreen beyond. SKIN-B hands. L-CAR-DAY, PAL-CAR, TEXT-LOCK. |

**Edit plan.** 0–1.5 s stitch of V03's 'twenty-five' with the Sept tooltip crop (735,278,100,55) by 0.8 s. 1.5–2.3 s an edit-built, neutral notification 'New email · September report' (no figures, no Google UI). 2.3–9 s R-01. 9–13 s the tooltip receipt keyed into B-01's phone, then full frame with source 'Calls made from your Business Profile · September 2026'. 13–15 s end card: the real headline and chart crop (15,165,910,310) with its own range 'May–Oct 2026 (October part month)', caption 'September: 25 calls, the best of the six months shown.' Never '114 calls since May' after a September report. Label: 'Re-creation made with [Name]'s permission. Real data.' Gate G3. −14 LUFS. Reuse on case-study pages in the 16:9 'phone clip beside receipts' layout.

**Data used (every number traces here).**
- leamingtonspa_gbp_calls_may-oct2026.png Sept tooltip 735,278,100,55: 25 calls, September 2026 (exact)
- leamingtonspa_gbp_calls_may-oct2026.png headline + chart 15,165,910,310: 114 calls May–Oct 2026 (October part month)

---

### V10 · Hands First

**Team video: meet the team (30 s per person)** · **Brand:** Hulk Marketing / Google Ranker Pro (agency) · **Placement:** Service pages · **Length:** 30 s per person; three clips to start (T1, T2, then F1 last) · **Ratios:** 16:9, 9:16 · **Cast:** T1_SEO, T2_REPORTING, F1_HASSAN

**Concept.** A fixed template so the set reads as one shoot: 0–4 s hands doing their real job, no face; 4–24 s a medium shot at their own desk naming themselves, their role and one true task for a named client (with that client's permission); 24–30 s a short tail moment (a laugh, a sip, back to the screen), then one real number from a client they actually worked on, shown as a receipt. The founder comes last and is just another person at a desk: his hands-first shot is making the tea for everyone.

**Hook.** Hands mid-task (typing a Business Profile post, sketching a site map on blank paper, pouring tea), with the person's receipt number by 0.8 s on the 9:16 cut.

**Version A (preferred).** T1_SEO, T2_REPORTING and F1_HASSAN, each Mode B with their own memo. Add more consenting staff later on the same template (4 first takes each).

**Version B (fallback).** A person who won't appear is simply left out. No AI stand-ins for named staff, ever; never the 30 sample portraits from googlerankerpro.com; no chair-spin montage.

**Script.** Agency drafts; each person edits, approves and records. T1, A-01: 1–7 s 'I'm [name]. I do the search side: the pages, the titles, the Business Profile.' 7–12 s 'For Golden Line Taxis in Warwick, I [one true task from the work log].' Receipt: 744 different searches. T2, A-01: 1–6 s 'I'm [name]. I build the monthly reports.' 6–12 s 'For Leam Taxis, that means the calls that come straight from Google.' Receipt: 25 calls in September. F1, A-01: 1–6 s 'I'm Hassan. I started Hulk Marketing, and I make the tea.' 6–12 s 'Every client gets their real numbers, with the context next to them.' Receipt: one number the user picks from a client he worked on (e.g. Golden Line, 312 clicks in three months). No 'even the October dip', no 'last quarter'.

**Seedance 2.5 generations**

| Gen ID | Purpose | Location | Who | Camera / mode | s | Ratio | Prompt essentials |
|---|---|---|---|---|---|---|---|
| `v10_T1_H-01_16x9` | T1 hands at work | L1 T1's real desk | T1_SEO | DOC-CAM, 29° block, static | 5 | 16:9 | Close on T1's hands typing on a laptop whose screen is SCREEN-AWAY or SCREEN-SOFT; the orange mug; a blank sticky note on the bezel. L-OFFICE, PAL-INT + AGENCY ADD-ON, TEXT-LOCK. |
| `v10_T1_A-01_16x9` | T1 intro lines and tail moment | L1 | T1_SEO | DOC-CAM tripod with micro-movement, 47° block | 15 | 16:9 | First frame: T1 mid-task at the desk, turns from the screen to the interviewer past camera-left. 1–7 s line 1 (@Audio); 7–12 s line 2 (@Audio); 12–15 s tail: small laugh, sip from the orange mug, turns back to the screen. L-OFFICE, PAL-INT + AGENCY ADD-ON, TEXT-LOCK, one person, DOC-CAM. |
| `v10_T1_H-01_9x16` | T1 hands at work, vertical | L1 | T1_SEO | DOC-CAM static | 5 | 9:16 | As the 16:9 hands shot from a vertical anchor still. |
| `v10_T1_A-01_9x16` | T1 intro, vertical | L1 | T1_SEO | DOC-CAM tripod | 15 | 9:16 | As v10_T1_A-01_16x9 from a vertical anchor still. |
| `v10_T2_H-01_16x9` | T2 hands at work: labelling a plain report folder, sketching a chart outline on blank paper | L1 or L8 T2's real desk | T2_REPORTING | DOC-CAM static, 29° block | 5 | 16:9 | Close on T2's hands writing on blank paper (no readable marks) beside a closed plain folder; laptop SCREEN-AWAY. L-OFFICE, PAL-INT + AGENCY ADD-ON, TEXT-LOCK. |
| `v10_T2_A-01_16x9` | T2 intro lines and tail moment | L1 or L8 | T2_REPORTING | DOC-CAM tripod, 47° block | 15 | 16:9 | As T1's template: turns from the screen, line 1 at 1 s, line 2 at 7 s, tail 12–15 s (pushes the sleeves up, small nod, back to work). Deep-skin exposure line if it applies. L-OFFICE, PAL-INT + AGENCY ADD-ON, DOC-CAM. |
| `v10_T2_H-01_9x16` | T2 hands, vertical | L1 or L8 | T2_REPORTING | DOC-CAM static | 5 | 9:16 | Vertical version of T2's hands shot. |
| `v10_T2_A-01_9x16` | T2 intro, vertical | L1 or L8 | T2_REPORTING | DOC-CAM tripod | 15 | 9:16 | Vertical version of T2's intro. |
| `v10_F1_H-01_16x9` | F1 hands first: making the tea at the office kettle | L1 office kettle corner | F1_HASSAN | DOC-CAM, 29° block, static | 6 | 16:9 | Close on his hands: the kettle clicks off, steam, he pours into two plain mugs (one is the orange one), stirs, sets the spoon down; his watch visible. No face. Two mugs only. L-OFFICE, PAL-INT + AGENCY ADD-ON, TEXT-LOCK. |
| `v10_F1_A-01_16x9` | F1 intro lines and tail moment, at his desk with the mug | L1 | F1_HASSAN | DOC-CAM tripod, 47° block | 15 | 16:9 | First frame: Hassan sets a mug down at his desk and turns to the interviewer past camera-left (weekly-desk wardrobe). 1–6 s line 1 (@Audio), dry; 6–12 s line 2 (@Audio); 12–15 s tail: small laugh, sips, turns back to the screen. L-OFFICE, PAL-INT + AGENCY ADD-ON, DOC-CAM. |
| `v10_F1_H-01_9x16` | F1 tea hands, vertical | L1 | F1_HASSAN | DOC-CAM static | 6 | 9:16 | Vertical version of the tea shot. |
| `v10_F1_A-01_9x16` | F1 intro, vertical | L1 | F1_HASSAN | DOC-CAM tripod | 15 | 9:16 | Vertical version of F1's intro. |

**Edit plan.** Fixed template per person: 0–4 s H-01; 4–24 s A-01 (name and role lower third from the edit, client named only with that client's permission); 24–30 s A-01's tail, then the person's receipt with source line: T1 = pagination crop 930,2135,410,40 '744 different searches · Golden Line Taxis · Google Search Console · 19 Jul–18 Oct 2026'; T2 = Sept tooltip 735,278,100,55 '25 calls · Leam Taxis · Google Business Profile · September 2026' (G3); F1 = the user's pick from a client he worked on (e.g. Golden Line totals crop 24,201,720,110, 312 clicks). F1's clip runs last. No chair spins, no montage of several people in one clip. Mode B labels. 9:16 cuts at −14 LUFS for posting.

**Data used (every number traces here).**
- goldenlinetaxiswarwick_gsc_3m.png pagination 930,2135,410,40: 744 queries (T1)
- leamingtonspa_gbp_calls_may-oct2026.png Sept tooltip 735,278,100,55: 25 calls (T2)
- goldenlinetaxiswarwick_gsc_3m.png totals 24,201,720,110: 312 clicks (F1, if the user picks it)

---

### V11 · Day One of an Audit Has No Numbers

**Team video: behind the scenes (20 s)** · **Brand:** Zentro (zentro.co.uk), with a Golden Line audit as the fallback subject · **Placement:** Social: Reels, TikTok, Shorts · **Length:** 20 s · **Ratios:** 9:16 · **Cast:** T1_SEO, T2_REPORTING, EXTRA_MODE_C

**Concept.** An honest behind-the-scenes: every case study starts with no numbers, just a site map. Hands lead: a marker squeaks out boxes and arrows with no words, blank Post-its go on a monitor bezel, blank index cards are laid out as a tree beside a green laptop. Then one medium-wide two-shot of T1 and T2 at the whiteboard. The green laptop gets Zentro's real navigation: 10 laptop brands and 3 phone brands, each with its own repair page. End line: 'Ask us again in three months.'

**Hook.** Text card by 0.8 s 'Day one. No numbers yet.' over the marker squeak.

**Version A (preferred).** T1_SEO and T2_REPORTING (Mode B), at most two people per frame, in the real agency room.

**Version B (fallback).** Hands only (O-01 to O-03), no faces. If Zentro won't confirm Hulk's role or permission to be named: switch the subject to a Golden Line audit (relationship verified) with the same shots; the green laptop shows Golden Line's real town and airport navigation, and the end line becomes one that the work log supports. Anonymous version: 'a Manchester repair business', only the whiteboard as the receipt.

**Script.** No dialogue (an unintelligible murmur in O-04 only). End-card line (edit text): 'Ask us again in three months.'

**Seedance 2.5 generations**

| Gen ID | Purpose | Location | Who | Camera / mode | s | Ratio | Prompt essentials |
|---|---|---|---|---|---|---|---|
| `v11_O-01_9x16` | Marker squeak: boxes and arrows, no letters | L1 agency room | T2_REPORTING | PHONE-REAR handheld close | 5 | 9:16 | Close on T2's hand drawing a box and an arrow on a whiteboard with a dark marker, no letters or numbers anywhere; squeak at 1 s and 3 s. L-OFFICE, PAL-INT + AGENCY ADD-ON, TEXT-LOCK. |
| `v11_O-02_9x16` | Blank Post-its pressed onto a monitor bezel; one curls off | L1 | EXTRA_MODE_C | PHONE-REAR handheld close | 4 | 9:16 | Hands press three blank orange-and-yellow Post-its onto a monitor bezel (monitor SCREEN-SOFT); one curls and drops at 3 s. Mode C. L-OFFICE, PAL-INT, TEXT-LOCK. |
| `v11_O-03_9x16` | Blank index cards laid in rows beside a green laptop | L1 | T1_SEO | PHONE-REAR held still above the table | 6 | 9:16 | Top-down-ish: T1's hands lay blank index cards in rows like a tree and slide one sideways; a laptop beside them shows SCREEN-GREEN with four corner dots; camera still while the screen is in frame. L-OFFICE, PAL-INT + AGENCY ADD-ON. |
| `v11_O-04_9x16` | Medium-wide two-shot at the whiteboard: T2 draws, T1 points | L1 | T1_SEO, T2_REPORTING | PHONE-REAR handheld by a colleague, gentle drift | 8 | 9:16 | First frame: T2 at the whiteboard drawing a box (no letters), T1 beside pointing at a gap; a short unintelligible exchange; T1 laughs once; kettle click off-screen at 6 s. Medium-wide so faces stay small. L-OFFICE, PAL-INT + AGENCY ADD-ON, TEXT-LOCK, exactly two people. |

**Edit plan.** Cuts every 1.5–2 s, hands first. O-03's green laptop gets a real scroll of assets/sites/zentro/now_desktop_full.png, then the real nav: the ten laptop-brand and three phone-brand items highlighted one by one on the real capture (no counter animation), card '10 laptop brands · 3 phone brands · a page each' with source 'zentro.co.uk navigation, captured 22 Oct 2026'. Context 'No performance data yet.' End line 'Ask us again in three months.' No Zentro self-claims (5,000+, 4.8/5, 2,560+ reviews), no Zentro reviews. Label 'Illustrative footage. Real data.' for the hands shots and the Mode B label for O-04. Gates: Hulk's role on Zentro, and permission to name it.

**Data used (every number traces here).**
- zentro.co.uk navigation (client_zentro.md, 22 Oct 2026): laptop repair for 10 brands (Apple MacBook, Dell, HP, Lenovo, ASUS, Acer, Microsoft Surface, Samsung, MSI, Razer); mobile repair for 3 brands (Apple iPhone, Samsung Galaxy, Google Pixel)
- assets/sites/zentro/now_desktop_full.png

---

### V12 · Month-End

**Team video: day in the life (30 s)** · **Brand:** Hulk Marketing (agency), delivering Leam Taxis' September report · **Placement:** Social: Reels, TikTok, Shorts · **Length:** 30 s · **Ratios:** 9:16 · **Cast:** T2_REPORTING

**Concept.** T2's real month-end in five beats: arrive, pull the export, check the number twice, call the client, log off. The report T2 sends is the one the owner opens in V09. Selfie beats bookend phone-rear b-roll. Filmed only at the location the user confirms (UK or Pakistan), with only details true of that place and that person.

**Hook.** Frame 1: T2's selfie at the door, coat on, first line; the '25' receipt teased by 0.8 s in the corner.

**Version A (preferred).** T2_REPORTING, Mode B, own memos. Separate UK and Pakistan versions only if both are real; a UK/PKT time pill only if true.

**Version B (fallback).** Hands-only beats (A-02, A-03) plus T2's real voice memo as VO, no face.

**Script.** Agency draft (T2 edits, approves and records). v12_A-01: 1–6 s 'Month-end. One of my taxi clients. Let's see what September did.' v12_A-04 (phone call, one side only, no client voice): 1–7 s 'Morning. Your report's in your inbox. September was a good one.' v12_A-05: 1–6 s 'Report's sent. Twenty-five calls from Google in September. Logging off.' No 'He'll ring me in about ten minutes', no '114 since May'.

**Seedance 2.5 generations**

| Gen ID | Purpose | Location | Who | Camera / mode | s | Ratio | Prompt essentials |
|---|---|---|---|---|---|---|---|
| `v12_A-01_9x16` | Morning selfie at the entrance, line 1 | L8 T2's real entrance or street (UK or Pakistan, as confirmed) | T2_REPORTING | PHONE-SELFIE handheld, 24 mm selector | 8 | 9:16 | First frame: T2's face close in the front camera at their real entrance, coat on, door behind. 1–6 s line 1 (@Audio); 6–8 s pushes the door open, ambience. Light per real place (L-STREET for UK overcast; the confirmed real light for Pakistan). PAL-EXT, TEXT-LOCK, PHONE-SELFIE handheld lines. |
| `v12_A-02_9x16` | Kettle or tea, laptop lid opens (screen away) | L8 T2's real desk and kitchen | T2_REPORTING | PHONE-REAR handheld | 6 | 9:16 | Hands: kettle or chai pan steam, mug filled; the laptop lid lifts, SCREEN-AWAY. SKIN-B hands. L-OFFICE, PAL-INT + AGENCY ADD-ON, TEXT-LOCK. |
| `v12_A-03_9x16` | Over the shoulder: green laptop, finger traces the trackpad, pause, re-check | L8 real desk | T2_REPORTING | PHONE-REAR static on a phone stand | 8 | 9:16 | Over T2's shoulder at a laptop with SCREEN-GREEN and four corner dots; a finger traces the trackpad, stops, a pause, scrolls back and checks again; camera static on a phone stand. L-OFFICE, PAL-INT + AGENCY ADD-ON. |
| `v12_A-04_9x16` | Phone call at the window, the report line | L8 real workplace window | T2_REPORTING | PHONE-REAR propped on a shelf, static | 10 | 9:16 | T2 standing at a window, phone to the ear (screen away), half-turned to camera; 1–7 s line (@Audio); 7–9 s listens, laughs once, nods; final second ambience. L-OFFICE, PAL-INT, TEXT-LOCK, one person, no other voices. |
| `v12_A-05_9x16` | End-of-day selfie, line 2, lights off | L8 real desk, evening | T2_REPORTING | PHONE-SELFIE handheld | 8 | 9:16 | Selfie at the desk, coat going on, the window dark behind (dark-set rim line). 1–6 s line (@Audio); 6–8 s reaches off-frame, the desk lamp clicks off, ambience. L-HOME (lamp) or the real evening light, PAL-INT, PHONE-SELFIE. |

**Edit plan.** Real clock times only, as edit text, and only if true. A-03's green keyed at an angle with the real Leam chart crop (15,165,910,310), the September tooltip (735,278,100,55) ringed. After the call, a 1 s cut of BR01_9x16 (a phone lighting up on a dash) as the link to V09. Payoff card at ~24 s: '25 calls from Google in September' = tooltip crop with source 'Calls made from your Business Profile · September 2026' (G3). End card 'Watch the client open it →' linking V09. Mode B label. −14 LUFS. Gate G8 (location), G3, and confirmation that T2 really delivers Leam Taxis' report.

**Data used (every number traces here).**
- leamingtonspa_gbp_calls_may-oct2026.png Sept tooltip 735,278,100,55: 25 calls, September 2026
- leamingtonspa_gbp_calls_may-oct2026.png chart crop 15,165,910,310 (keyed on the laptop)

---

### V13 · Why I Show Clients the Real Numbers

**Founder video: founder intro (45–60 s)** · **Brand:** Hulk Marketing / Google Ranker Pro (Hassan Pasha) · **Placement:** Homepage hero · **Length:** 55 s at 16:9; 30 s cut at 9:16 · **Ratios:** 16:9, 9:16 · **Cast:** F1_HASSAN, F2_SAJID

**Concept.** A sit-down documentary interview at Hassan's real workplace, deliberately not his black-studio look: who Hulk helps, why he started it, what clients actually get, and what he will never promise. Problem/turn/result: the human story first, then the receipts at about 62–70% of the runtime: the Companies House record (Hulk Marketing Ltd, 15931335, incorporated 2 Sep 2024) and a 6 s montage of three real receipts on his green laptop. It closes on 'no ranking guarantees' and him picking up a ringing phone at the window.

**Hook.** 16:9: walking in out of the rain at his real building's entrance, folding an umbrella, first line on the cut to the medium. 9:16: a selfie cold open in drizzle in the car park ('If you run a local business and people can't find you on Google, this is why we exist.').

**Version A (preferred).** F1_HASSAN, Mode B, DOC-CAM sit-down interview at his real workplace (no serviced office dressed as a big HQ), own memos. Optional F2_SAJID two-shot only if he consents.

**Version B (fallback).** If he declines to be recreated: his real voice over b-roll of his hands and real places (still Mode B for hands). No AI founder and no N1 in this film.

**Script.** Questions for a 10-minute voice-memo interview we transcribe; he approves the cut lines. Q1 'Who do you help, in one sentence?' Draft: 'Taxi firms, a fostering agency, local businesses where one phone call matters.' (clients by type; named only with permission). Q2 'Why did you start it?' [his real reason, transcribed]. Q3 'What does a client actually get from you every month?' Draft: 'Every month you get your own Google numbers. The good months and the quiet ones, with the context next to them.' Q4 'What will you never promise?' Draft: 'A ranking. No ranking guarantees. Just the work, and the real numbers.' 9:16 cold open draft: 'If you run a local business and people can't find you on Google, this is why we exist.' 'Google Ranker Pro since 2012' only if he wants it, captioned as self-declared.

**Seedance 2.5 generations**

| Gen ID | Purpose | Location | Who | Camera / mode | s | Ratio | Prompt essentials |
|---|---|---|---|---|---|---|---|
| `v13_A-01_16x9` | Interview medium: who we help | L1 his real workplace | F1_HASSAN | DOC-CAM tripod with micro-movement, 47° block | 15 | 16:9 | Seated by the window camera-left, eyes to an interviewer off camera-left; mug on the side table, coat over a chair back, cables under the desk. Lines at 1 s and 8 s (@Audio); final second ambience. L-OFFICE, PAL-INT + AGENCY ADD-ON, TEXT-LOCK, one person, DOC-CAM. |
| `v13_A-02_16x9` | Interview close: why I started | L1 | F1_HASSAN | DOC-CAM tripod, 29° block | 14 | 16:9 | Close-up, same axis; his transcribed reason in two lines (@Audio); one glance away to think mid-line; small nod. One imperfection (creased collar). L-OFFICE, PAL-INT, DOC-CAM. |
| `v13_A-03_16x9` | Interview medium: what clients get | L1 | F1_HASSAN | DOC-CAM tripod, 47° block | 14 | 16:9 | Medium; two lines (@Audio); counts on two fingers once; sits back. L-OFFICE, PAL-INT + AGENCY ADD-ON, DOC-CAM. |
| `v13_A-04_16x9` | Close: what I'll never promise | L1 | F1_HASSAN | DOC-CAM tripod, 29° block | 10 | 16:9 | Close; one line (@Audio) at 1 s; a small nod; holds. L-OFFICE, PAL-INT, DOC-CAM. |
| `v13_B-01_16x9` | Walking in from the rain, folding an umbrella, at his real entrance | His real building entrance, drizzle | F1_HASSAN | DOC-CAM handheld on the shoulder, 84° observational block | 8 | 16:9 | Overcoat over the 13 wardrobe; shakes water off the umbrella, folds it, pushes the door; signage soft or out of frame; breath faintly visible. L-STREET, PAL-EXT, TEXT-LOCK, one person. |
| `v13_B-02_16x9` | On a phone call at the window, back three-quarter; ends the film | L1 | F1_HASSAN | DOC-CAM, 29° block, observational | 8 | 16:9 | Picks up a ringing phone from the desk, walks two steps to the window, back three-quarter to camera, listening, rain on the glass. No intelligible dialogue. L-OFFICE, PAL-INT, TEXT-LOCK. |
| `v13_B-03_16x9` | Hands writing in a plain notebook with an orange pen | L1 | F1_HASSAN | DOC-CAM static, 29° block | 5 | 16:9 | Close on his hands writing on a blank page (no readable marks), watch visible, mug in the foreground. L-OFFICE, PAL-INT + AGENCY ADD-ON. |
| `v13_B-04_16x9` | Over the shoulder at a laptop, green screen (montage surface) | L1 | F1_HASSAN | DOC-CAM static, 47° block | 6 | 16:9 | Over his shoulder, laptop SCREEN-GREEN with four corner dots, his hand still on the trackpad; static. L-OFFICE, PAL-INT. |
| `v13_S-01_9x16` | Social cold open: selfie in drizzle in the car park | Car park outside his real workplace | F1_HASSAN | PHONE-SELFIE handheld, 24 mm selector | 10 | 9:16 | Front camera at arm's length, overcoat collar up, drizzle on the lens edge, car park behind (plates soft). 1–8 s cold-open line (@Audio); final second ambience. L-STREET, PAL-EXT, TEXT-LOCK, PHONE-SELFIE handheld lines. |
| `v13_A-03_9x16` | Interview medium: what clients get, vertical | L1 | F1_HASSAN | DOC-CAM tripod | 14 | 9:16 | As v13_A-03_16x9 from its own 9:16 anchor still. |

**Edit plan.** 16:9 (55 s): 0–6 s B-01; 6–20 s A-01; 20–34 s A-02 with B-03 cutaways; 34–37 s (62%) Companies House receipt: a fresh dated PNG of the company page ('Hulk Marketing Ltd · company no. 15931335 · incorporated 2 Sep 2024'), recaptured from assets/sites/hulkmarketing_dl/ch.html; 37–43 s a 6 s montage on B-04's green laptop, pushed to full frame: Golden Line pagination '744 different searches', Leam '114 calls May–Oct 2026 (October part month)' (G3), Coventry interactions chart '79, May–Oct 2026' (G3), each with its source line; 43–50 s A-03; 50–55 s A-04 and B-02. Close card: 'No ranking guarantees.' (the only line called the site's own). Client-visit b-roll only if the visit is real. 9:16 (30 s): S-01 cold open, A-03_9x16, the montage, end card. No 'results shown are not typical' line attributed to the site. Mode B label. −14 LUFS for the 9:16.

**Data used (every number traces here).**
- Companies House: Hulk Marketing Ltd, company no. 15931335, incorporated 2 Sep 2024, directors Hassan Pasha and Muhammad Sajid (assets/sites/hulkmarketing_dl/ch.html; agency_googlerankerpro.md §1)
- goldenlinetaxiswarwick_gsc_3m.png pagination 930,2135,410,40: 744 queries
- leamingtonspa_gbp_calls_may-oct2026.png headline 20,165,240,80: 114 calls May–Oct 2026
- coventry_gbp_interactions_may-oct2026.png headline + chart 40,175,890,310: 79 interactions May–Oct 2026
- googlerankerpro.com honesty line 'No ranking guarantees' (agency_googlerankerpro.md)

---

### V14 · Tip of the Week, Ep 1: The Edge of Page One

**Founder video: SEO tip of the week (30 s, weekly series)** · **Brand:** Hulk Marketing (Hassan Pasha); Ep 1 uses Golden Line Taxis data · **Placement:** Social: Reels, TikTok, Shorts · **Length:** 30 s per episode · **Ratios:** 9:16 · **Cast:** F1_HASSAN

**Concept.** One practical tip per week from Hassan to a phone on a desk tripod, the same desk, framing and wardrobe every week (one reused anchor still), so it reads as a real habit. In the edit he is segmented from his real room over the real Search Console row (the green-screen effect; no physical green screen), pointing up and behind him. Ep 1 teaches the method on one row: 'taxi warwick' is shown 665 times at an average 10.7 with a 0.9% click-through, the edge of page one, so fix the page that's already there. V15 later reports the whole Warwick cluster as the plan.

**Hook.** A myth line in the first second, with the row receipt 'taxi warwick · 665 times shown · avg 10.7' keyed behind him by 0.8 s.

**Version A (preferred).** F1_HASSAN, Mode B, PHONE-SELFIE propped on a desk tripod (uses whichever propped texture line passed the V09 test), weekly-desk wardrobe, own memos.

**Version B (fallback).** T1 presents the tip (a real person) on the same set. No AI narrator for 'from you to camera'.

**Script.** Agency draft (Hassan edits, approves and records; numbers as words). v14_A-01: 1–5 s 'Myth: you need more content to rank. Usually you don't.' 5–11 s 'Find a search with loads of impressions sitting around position ten.' v14_A-02: 1–7 s 'One Warwick taxi firm: taxi warwick. Shown six hundred and sixty-five times in three months, averaging ten point seven.' 7–11 s 'That's the edge of page one, and fewer than one in a hundred got a click.' v14_A-03: 1–8 s 'Don't write a new blog. Fix the page that's already there: the title, local proof, links from your other pages.' [Optional, only if true: 'That's the one we're on next.']

**Seedance 2.5 generations**

| Gen ID | Purpose | Location | Who | Camera / mode | s | Ratio | Prompt essentials |
|---|---|---|---|---|---|---|---|
| `v14_A-01_9x16` | Myth line and the method; points up and behind | L1-TIP fixed tip desk | F1_HASSAN | PHONE-SELFIE propped on a desk tripod at chest height, static | 12 | 9:16 | Fixed series set: his desk, window camera-left, orange mug at the frame edge, a plant, coat on the chair; framed with headroom in the top third for the keyed row. 1–5 s line 1 (@Audio); at 5 s points up and behind himself over his right shoulder; 5–11 s line 2; final second ambience. L-OFFICE, PAL-INT + AGENCY ADD-ON, TEXT-LOCK, one person, propped camera lines. |
| `v14_A-02_9x16` | The real example | L1-TIP | F1_HASSAN | PHONE-SELFIE propped, static | 12 | 9:16 | Same anchor still; slightly closer as he leans in at 7 s. Lines at 1 s and 7 s (@Audio); hands kept below the chin while talking. L-OFFICE, PAL-INT + AGENCY ADD-ON. |
| `v14_A-03_9x16` | The fix and sign-off | L1-TIP | F1_HASSAN | PHONE-SELFIE propped, static | 10 | 9:16 | Same anchor still; line at 1 s (@Audio) counting three things on his fingers below chin height; small shrug and nod; reaches to stop the recording at 9 s (the frame vibrates faintly). L-OFFICE, PAL-INT + AGENCY ADD-ON. |

**Edit plan.** Green-screen effect: a segmentation matte cuts Hassan out of his real room; row 5 (24,1100,1318,49) 'taxi warwick · 6 clicks · 665 impressions · 0.9% CTR · 10.7' sits behind him at a slight angle in the top third, impressions and position cells ringed as he speaks them. Context strip: 'Average position, Google Search Console, 19 Jul–18 Oct 2026.' Number by 0.8 s. Impressions are 'times shown', never 'people'. Captions word-timed inside the safe zones; −14 LUFS; Mode B label. EPISODE BANK (3 first takes each, same set, real rows only): Ep 2 'Own your name': Golden Line row 1 'golden line taxis warwick' 1.8, 23.3% CTR, said as 'top two on average'. Ep 3 'Publish your prices': York Cars' airport fares page (Leeds Bradford from £55, Manchester from £125), only with York Cars' permission, no performance claim. Ep 4 'Your Business Profile is a phone line': Leam 114 calls May–Oct 2026 (October part month), after G3. Ep 5 'Answer the questions people ask': Organic Fostering's 32 guides, no traffic claim, after the credit gate. Ep 6 'Click-through beats position': Coventry row 7 'coventry airport taxis' 26.3% CTR at 8.2, 'small numbers: 19 times shown'. Ep 7 'A page for the inbound direction': Coventry row 25 'heathrow airport to coventry' 307 times shown at avg 44.9 while row 16 'airport transfer coventry to heathrow' averages 5.3; Coventry already has a Heathrow page and fare, so the tip is the inbound-direction page; '307 times shown', never '307 people'. Ep 8 'A page per brand people search': Zentro, with permission.

**Data used (every number traces here).**
- goldenlinetaxiswarwick_gsc_3m.png row 5 (24,1100,1318,49): 'taxi warwick' 6 clicks, 665 impressions, 0.9% CTR, avg 10.7
- Episode bank: Golden Line row 1; yorkcars.co.uk/airport-taxi-york fares (22 Oct 2026); Leam GBP 114; organicfostering.co.uk sitemap; Coventry rows 7, 16 (24,1640,1318,49) and 25 (24,2082,1318,49)

---

### V15 · What Moved in Warwick

**Founder video: founder commentary on results (30–45 s)** · **Brand:** Golden Line Taxis, Warwick (commentary by Hassan Pasha) · **Placement:** Case study: Golden Line Taxis, Social (9:16 cut) · **Length:** 40 s at 16:9 and 9:16 · **Ratios:** 16:9, 9:16 · **Cast:** F1_HASSAN, CLIENT_GOLDENLINE_OWNER, N1_AI_PRESENTER

**Concept.** Hassan stands at a wall monitor (green) and explains one real client win in the order 'Here's what we did. Here's what Google shows now.' What we did comes only from the Golden Line work log (G7), shown as dated captures of the work itself: the live footer credit and the site's list of town and airport pages. What Google shows now: the airport searches average page one (5.3; 6.1 at 13% click-through; 7.1) and 'kenilworth taxis' 6.7. The honest next prize: 1,522 times shown across 'taxi warwick', 'warwick taxi' and 'warwick taxis', averaging 10.7–12.6, the edge of page one. No causal verbs (made, drove, caused): there is no comparison period.

**Hook.** 16:9: Hassan already at the monitor, turning to camera. 9:16: a 2 s stitch of the Golden Line owner's approved line from V01, then '13% click-through' (row 6) on screen by 0.8 s after the stitch.

**Version A (preferred).** F1_HASSAN, Mode B, DOC-CAM at a green wall monitor in his real workplace, own memos.

**Version B (fallback).** N1 narrates the same plates in the third person ('the agency', never 'we'), labelled 'AI presenter. Real client data. Not a client testimonial.'; no green screen in her frame. A's Coventry version (location pages dated June 2026 in the sitemap; next prize 'airport transfers coventry' 607 times shown at 22.0) becomes a later episode, but only if the work log confirms the build.

**Script.** Agency draft (Hassan edits, approves and records; numbers as words; 'what we did' lines only from the G7 work log). v15_A-01: 1–7 s 'Golden Line Taxis, Warwick. Here's what we did, and here's what Google shows now.' 7–13 s 'We built the site, with pages for the airports and the towns around Warwick.' [ONLY WHAT G7 CONFIRMS] v15_A-02: 1–7 s 'Last three months, the airport searches average page one. Five point three, six point one, seven point one.' 7–11 s 'And Kenilworth taxis: six point seven.' v15_A-03: 1–6 s 'The next job is the big one: taxi Warwick, and the ways people type it.' 6–11 s 'Fifteen hundred and twenty-two times shown, averaging ten point seven to twelve point six. The edge of page one.' 9:16 stitch: the owner's approved V01 line, DRAFT FOR CLIENT APPROVAL, his words only.

**Seedance 2.5 generations**

| Gen ID | Purpose | Location | Who | Camera / mode | s | Ratio | Prompt essentials |
|---|---|---|---|---|---|---|---|
| `v15_A-01_16x9` | At the wall monitor (green, four corners), pointing to the upper third, then turning to camera; lines 1–2 | L1 his real workplace | F1_HASSAN | DOC-CAM handheld, 47° block, three-quarter angle, near-static | 15 | 16:9 | First frame: Hassan standing three-quarter to camera beside a wall monitor showing SCREEN-GREEN with four corner dots, pen in hand pointing at the upper third. 1–7 s line 1 (@Audio), turns from the monitor to the interviewer; 7–13 s line 2; 13–15 s holds, ambience. Camera still while the screen is in frame. L-OFFICE, PAL-INT + AGENCY ADD-ON, TEXT-LOCK, one person, DOC-CAM. |
| `v15_A-02_16x9` | Medium to camera: what Google shows now | L1 | F1_HASSAN | DOC-CAM tripod with micro-movement, 47° block | 12 | 16:9 | Medium, monitor soft at frame edge. Lines at 1 s and 7 s (@Audio); counts the three positions on his fingers below chin height; small nod. L-OFFICE, PAL-INT + AGENCY ADD-ON. |
| `v15_A-03_16x9` | Close: the next prize | L1 | F1_HASSAN | DOC-CAM tripod, 29° block | 12 | 16:9 | Close-up. Lines at 1 s and 6 s (@Audio); a slight wince-smile on 'the edge of page one'; holds. L-OFFICE, PAL-INT. |
| `v15_B-02_16x9` | Hand on the mouse, monitor green, mug | L1 | F1_HASSAN | DOC-CAM static, 29° block | 5 | 16:9 | Close on his hand on the mouse, desktop monitor SCREEN-GREEN behind, orange mug in the foreground; one click. L-OFFICE, PAL-INT + AGENCY ADD-ON. |
| `v15_A-01_9x16` | Vertical version at the monitor | L1 | F1_HASSAN | DOC-CAM handheld, near-static | 15 | 9:16 | As v15_A-01_16x9 from its own 9:16 anchor still; monitor in the upper half. |
| `v15_A-03_9x16` | Vertical close: the next prize | L1 | F1_HASSAN | DOC-CAM tripod | 12 | 9:16 | As v15_A-03_16x9, vertical. |

**Edit plan.** 16:9 (40 s): 0–14 s A-01 with dated captures of the work (the live footer credit; the site's town and airport page list from the live navigation/sitemap), labelled 'What we did · from the work log'; 14–26 s A-02 with B-02 and v01's real dashcam drive (RF07); first result receipt at 26 s (65%) on the monitor then full frame: rows 20 (24,1837,1318,49) 5.3, 6 (24,1150,1318,49) 6.1 · 13%, 7 (24,1199,1318,49) 7.1, 4 (24,1051,1318,49) 6.7, stacking; 26–37 s A-03 with rows 5 (24,1100,1318,49) 665 · 10.7, 9 (24,1297,1318,49) 486 · 12.6, 3 (24,1002,1318,49) 371 · 11.5 and the sum card '1,522 times shown · avg 10.7–12.6'; 37–40 s close on the totals source line. Context strip: 'Average positions, 19 Jul–18 Oct 2026. No earlier period to compare yet.' Title framing: 'Here's what we did. Here's what Google shows now.' Never 'last quarter', never 'people saw', never 'made it ring'. 9:16: 2 s stitch of the owner's approved V01 line, row 6 receipt by 0.8 s after it, A-01_9x16, A-03_9x16, receipts in the upper third. Labels per footage type. Gate G7 (work log), owner consent for the stitch.

**Data used (every number traces here).**
- goldenlinetaxiswarwick_gsc_3m.png rows 20, 6, 7, 4: avg 5.3; 6.1 at 13% CTR; 7.1; 6.7
- goldenlinetaxiswarwick_gsc_3m.png rows 5, 9, 3: 665 + 486 + 371 = 1,522 impressions at avg 10.7, 12.6, 11.5
- goldenlinetaxiswarwick_gsc_3m.png totals 24,201,720,110 (source line)
- Live footer 'Made with ❤ by Hulk Marketing Ltd' and live town/airport navigation on goldenlinetaxiswarwick.co.uk (dated captures)
- Golden Line work log (G7, to be supplied by the user)

---


---

## 6. Gates before generation (● blocks a video)

| Gate | What must be true | Blocks |
|---|---|---|
| ● G1 Consent | Written consent, 27 photos and voice memos from each person on camera or on voice | Every Version A |
| ● G2 Agency credit | Golden Line: verified (footer "Made with ❤ by Hulk Marketing Ltd"). Coventry: footer says SMEK (smek.co.uk lists Hassan Pasha as CEO). York Cars: footer says Xoom Media; Hulk's portfolio lists York Cars. Leam Taxis: Hulk's portfolio only. Organic Fostering's Sept 2026 rebuild and Zentro: unconfirmed | 2, 3, 4, 5, 6, 8, 9, 11, 12, 14 episodes |
| ● G3 Business Profile owner | Neither GBP screenshot shows a name. Confirm 114 calls = Leam Taxis, 79 interactions = Coventry Airport Taxis 247; send the Coventry Calls breakdown | 3, 4, 9, 10 (T2's number), 12, 13 montage |
| G4 No "No.1" | No "No.1", "#1" or "first" anywhere; 1.8 is "top two on average" | All |
| G5 No growth | One period only; growth needs a Compare export | 2, 8, 15 |
| ● G6 Real places | Client premises, office or livery only from the client's own photos; the agency room only from photos of a real workspace | 5, 6, 10–15 |
| ● G7 Work log | "What we did" lines only from the agency's records | 1 (turn), 10 (T1's task), 15 |
| ● G8 Team location | T2's real location (UK or Pakistan) from the user | 12 |
| G9 Before captures | An old-site design only from real Wayback or client captures; never mocked up | 4b (optional) |
| G10 Duplicate reviews | The "Ali" reviews (Sarah Byrd, Louise Jones) appear on Golden Line and Coventry with the brand swapped: never used, and never a generated "Ali" | 1, 2, 15 |
| G11 Site fixes | Coventry's Slough review widget, SMEK footer, "Qoute"/"Relaible"; Golden Line's sitemap test pages and re-attributed quotes; Organic Fostering's reels showing the superseded £447.60 | Any site capture on screen |

---

## 7. Production order, totals and hand-back

**Totals (Version A):** 86 first takes (41 at 16:9, 45 at 9:16), of which 5 are the shared b-roll bank (BR01 ×2, BR02, BR03, BR04). Retake budget 1.5× ≈ 129. Tip-of-the-week episodes after Ep 1 add 3 each. Both ratios are generated separately, from ratio-specific anchor stills, **only** for 1, 2, 4, 5, 6, 10, 13 and 15; everything else is 9:16 only. Fallback generations (V02 T-01/T-02, V03 Golden Line selfie, V07 hands, N1 scenes) are not in the count and are made only if triggered.

| Video | 16:9 | 9:16 | Total |
|---|---|---|---|
| V01 | 9 | 3 | 12 |
| V02 | 5 | 2 | 7 |
| V03 | 0 | 3 | 3 |
| V04 | 2 | 3 | 5 |
| V05 | 4 | 3 | 7 |
| V06 | 3 | 2 | 5 |
| V07 | 0 | 2 | 2 |
| V08 | 0 | 3 | 3 |
| V09 | 0 | 2 | 2 |
| V10 | 6 | 6 | 12 |
| V11 | 0 | 4 | 4 |
| V12 | 0 | 5 | 5 |
| V13 | 8 | 2 | 10 |
| V14 | 0 | 3 | 3 |
| V15 | 4 | 2 | 6 |
| **All** | **41** | **45** | **86** |

**Order (cheapest risk first):**
1. **Week 0, paperwork and evidence:** consents, 27-photo sets and memos; GBP ownership; credits; work logs; T2's location; real footage RF01–RF08; dated captures we take ourselves with the scratchpad Playwright script (the Golden Line footer and navigation, the York review widget and navigation, the Organic Fostering sitemap, the Zentro navigation, the Companies House page).
2. **Start now, without anyone's consent:** the shared b-roll bank (BR01–BR04), V04's plates, the hands shots in V08 (P-01 to P-03) and V11 (O-01 to O-03). **QC the World Bible on the b-roll first:** if a car looks like a game asset, fix the blocks (VEHICLE lock, one named light source with falloff, dressing anchors, atmosphere) before any person is generated. Run the propped-camera texture test as soon as the Leam owner's identity is ready (V09), or on F1 at the tip desk if F1 is ready first.
3. **Agency people** (F1, T1, T2): the fastest consent. Videos 7, 8 (voice), 10, 11, 12, 13, 14, 15, and T1's voice for 2.
4. **Clients, as their consent arrives:** Golden Line 1 (and the stitch in 15); Coventry 2; Leam Taxis 3 and 9; York Cars 5; Organic Fostering 6.
5. **Batch by location, not by video number** (same session, exact text loaded): the agency room (L1) carries about half the set (8, 10, 11, 13, 14, 15, and 12 if T2 works there); then Warwick (1), Coventry (2, 4), Leamington (3, 9), York (5), Old Trafford (6), T2's location (12).

**Hand-back (from the user):** `grp_v[NN]_[setup]-[shot]_t[take]_[ratio].mp4` at the generated resolution (MOV where offered); passing takes **and** near-misses; the anchor stills and sheet crops; a note of the resolution and selectors used.

---

## 8. Prompt kit

Templates: A §8.1 and §8.2, B §6.1 and §6.2, C §8.1, all with the fixes applied (interior palette in rooms, propped-camera texture test, four corner dots, "gives off almost no light"). The three prompts below are the standard every generation in the set meets.

### 8.1 v01_A-03_16x9: the owner's "turn" answer (Mode B, DOC-CAM, interior)
UI: Seedance 2.5, reference mode, 16:9, 1080p (720p flagged if capped), 15 s, audio on. Era 2020s, Physics realistic, Tone calm, Genre unset or documentary, Lens 50 mm.
```
ASSET MAP
@Image 1: identity of the taxi firm owner (face, hair, build, wardrobe: his own dark quilted jacket over a plain grey fleece). 100% matches the reference.
@Image 2: same person, three-quarter view; identity only.
@Image 3: anchor still for this shot: framing, light direction, wardrobe and room layout in frame one; do not copy any screen content or text.
@Image 4: geography and materials of his own back office only; do not copy its camera angle; ignore any signs or printed text in it.
@Audio 1: the owner's own voice for the line at second 1 only; ignore its background noise.
@Audio 2: the owner's own voice for the line at second 8 only; ignore its background noise.

SCENE CONTEXT
At dusk in late October, the owner of a small Warwick taxi firm sits at the table in his own back office with a laptop open beside him and tells an interviewer what changed when his new website went live. It starts settled, turns on a glance at the laptop, and ends with him leaning back.

LOCATION MAP
Camera at seated eye height on a tripod, 2.5 metres away across the room, facing the owner and the back wall. Foreground: the corner of the table, out of focus. Midground: the owner seated at the table; a laptop open at the left edge of frame, its screen turned partly towards camera. Background: a radiator with chipped paint under a window camera-right showing blue-grey dusk, a coat on a hook, a wall calendar turned face to the wall. A mug with a tea ring by his right hand; a phone face-down beside it.

FIRST FRAME AND SPATIAL BLOCKING
The first visible frame already contains the owner in position; no empty establishing frame. He sits centre-right, forearms on the table edge, torso angled slightly towards camera-left, eyes just past camera-left towards the interviewer. The laptop at the left edge of frame is on his right-hand side; right hand loose beside the mug on that side, left hand resting flat on the table.

FORMAT MODE
SINGLE CONTINUOUS TAKE.

OPTICS
47° diagonal field of view, standard normal lens character, camera 2 to 3 metres from the subject, natural human-eye perspective, zero obvious distortion, natural face proportions, background readable but softly out of focus.

CAMERA
Locked-off on a tripod with the faint micro-movement of a real head. Focus stays on the eyes; one small natural focus correction when he sits back.

TIMELINE
0-1s: Ambience only. He takes a small breath in. End state: lips parted, about to speak.
1-7s: At second 1, @Image 1 the owner says, in natural British English, "[APPROVED LINE 1 FROM HIS TRANSCRIPT, numbers written as words]", unhurried, glancing once at the laptop mid-sentence and back. End state: eyes back on the interviewer.
7-8s: A short pause; he swallows and gives one small nod. End state: lips parted again.
8-13s: At second 8, @Image 1 the owner says, in natural British English, "[APPROVED LINE 2]", and taps the table once with two fingers on the last word. End state: he sits back in the chair.
13-15s: He holds, breathing, a half-smile fading; ambience only.

PHYSICS
The chair takes his weight and creaks as he sits back; his sleeve drags slightly on the table; the tea in the mug shivers when he taps the table; the mug stays where it is.

LIGHTING
A warm tungsten ceiling bulb or lamp camera-left is the key; cool blue-grey dusk from a window camera-right; the two colour temperatures meet on the face; corners of the room fall into soft shadow. The laptop screen gives off almost no light.
Natural skin from the references, visible pores and fine texture, unretouched.

AUDIO
Ambience: a small back-office room tone, a radiator ticking, light rain on the window, a distant car on a wet road.
Foley: a two-finger tap on the table at 12 seconds; a chair creak at 13 seconds.
Dialogue: only the quoted lines, spoken by the owner at seconds 1 and 8, in natural British English; lips still when not speaking; no other voices.
Clean close dialogue as if from a clip-on microphone, natural room tone underneath, no echo.
No background music. No subtitles. At least 1 second of ambience-only before the first word and after the last word.

FINAL FRAME
The owner leaning back, eyes on the interviewer, half-smile fading, camera holding.

POSITIVE CONSTRAINTS
Muted, lived-in indoor colour as it really looks: off-white and pale grey walls, worn wood and grey laminate, cool daylight at the window, a warm pocket of light from a lamp or ceiling bulb; people in navy, grey and mid-blue everyday clothes; nothing saturated.
No on-screen text, captions or subtitles. All signs, labels, mugs, clothing, papers and screens are plain or turned away, with no readable words, logos or numbers. Number plates are not readable.
The laptop screen shows a flat, uniform, matte chroma-green fill from edge to edge, evenly lit, with no interface, no text, no reflections and no glare; all four corners and the bezel stay visible, with one small dark dot in each corner of the green. The screen gives off almost no light.
Exactly one person visible. No extra people.
Filmed on a handheld documentary video camera in available light: natural colour with a restrained grade, fine even digital grain, soft highlight roll-off on bright windows, real depth of field with a gently soft background.
```

### 8.2 v09_R-01_9x16: the reaction, propped on the dash (Mode B, the logged texture test)
UI: 9:16, 1080p, 10 s, audio on; Lens 24 mm; Era 2020s; Physics realistic; Tone calm. Generate twice from the same anchor still, changing **only** the last line (TEST A vs CONTROL), and log both.
```
ASSET MAP
@Image 1: identity of the taxi firm owner (face, hair, build, wardrobe: a dark fleece zipped to the chin). 100% matches the reference.
@Image 2: same person, front-camera selfie view; identity only.
@Image 3: anchor still for this shot: framing, light direction, wardrobe and car-interior layout in frame one; do not copy any screen content or text.
@Image 4: geography and materials of his own car interior only; do not copy its camera angle; ignore any badges or printed text.
@Audio 1: the owner's own voice for the word at second 5 only; ignore its background noise.

SCENE CONTEXT
On a wet afternoon the owner of a Leamington taxi firm sits in his own parked car, engine off, between jobs, reading his monthly report on the phone in his hands. He starts reading, turns on a small laugh, and ends looking out at the rain.

LOCATION MAP
Camera: a phone propped in a dashboard mount at chest height, about 55 centimetres from his face, facing the driver's seat. Foreground: the soft top edge of the steering wheel. Midground: the owner in the driver's seat, seatbelt off. Background: the driver's side window with rain beads and a wet terraced street, soft and grey, beyond it. A parking ticket face-down on the dash at the frame edge; a charging cable looped over the gear lever.

FIRST FRAME AND SPATIAL BLOCKING
The first visible frame already contains the owner in the driver's seat, head and shoulders in the lower two thirds of frame, a little off-centre to the left, holding a phone low in both hands with its screen facing away from camera, eyes down on it.

FORMAT MODE
SINGLE CONTINUOUS TAKE.

OPTICS
About 80° diagonal field of view, phone front-camera perspective, lens 50 to 60 centimetres from the face, a little below eye level. The face sits close at the centre, background visible to the frame edges and mostly in focus, straight lines stay straight, no portrait bokeh.

CAMERA
The phone is propped in a mount at chest height, 50 to 70 cm from the face; the frame is static except for faint vibration when the surface is touched or a car door closes.
Framing is a little off-centre, slightly low, the top of the head close to the top edge.
Auto exposure breathes slightly when he lifts his head towards the bright side window, then settles.

TIMELINE
0-1s: Ambience only. He reads, thumb still. End state: eyes on the phone.
1-4s: His thumb scrolls up once, he pauses, scrolls back down and reads again. End state: still, reading.
4-6s: He breathes out through his nose in a short laugh and, at second 5, @Image 1 the owner says quietly, in natural British English, "[HIS APPROVED WORD, e.g. Twenty-five.]". End state: lips still, a half-smile.
6-9s: He rubs the back of his neck with his left hand, then looks out through the side window at the rain. End state: eyes on the street.
9-10s: He holds; ambience only.

PHYSICS
The seat creases under his weight when he shifts; his fleece sleeve drags across the steering wheel; the car rocks very slightly as he leans; rain beads slide down the side glass.

LIGHTING
Flat overcast daylight through the windscreen is the only key, soft and slightly cool; the side window camera-right adds a brighter edge on that cheek; the cabin roof and footwell fall into soft shadow; the windscreen itself is slightly overexposed. The phone screen faces away from the camera; its cool white glow lights the face from below, brighter on the chin and under the nose.
Natural skin from the references, visible pores and fine texture, unretouched.

AUDIO
Ambience: rain on the car roof, a distant car passing on a wet road.
Foley: a fleece rustle at 6 seconds as he lifts his hand.
Dialogue: only the quoted word, spoken by the owner at second 5, in natural British English; lips still when not speaking; no other voices.
Sound recorded by the phone's built-in microphone: close voice with a little car-cabin reflection.
No background music. No subtitles. At least 1 second of ambience-only before the first word and after the last word.

FINAL FRAME
The owner looking out of the side window at the rain, the phone lowered to his lap, camera static.

POSITIVE CONSTRAINTS
Muted colour inside a parked car as it really looks: a charcoal dashboard and grey seat fabric, rain beads on the glass, the world outside soft and grey; people in navy, grey and mid-blue everyday clothes; nothing saturated.
No on-screen text, captions or subtitles. All signs, labels, mugs, clothing, papers and screens are plain or turned away, with no readable words, logos or numbers. Number plates are not readable.
The engine is off and the car is parked. Exactly one person visible. No extra people.
[TEST A] Filmed on a smartphone front camera propped in a mount at chest height: small-sensor look with deep focus, slight edge over-sharpening, faint sensor noise in the shadows, auto exposure and auto white balance as recorded, ungraded colour.
[CONTROL, separate generation] Filmed handheld on a smartphone front camera at arm's length: small-sensor look with deep focus, slight edge over-sharpening, faint sensor noise in the shadows, auto exposure and auto white balance as recorded, ungraded colour.
```

### 8.3 v04_P-01_9x16: the "May" plate (no identity; generate the anchor still first, then build "August" from the identical still)
UI: 9:16, 1080p, 8 s, audio on; Lens 24 mm; Era 2020s; Physics realistic; Tone calm.
```
ASSET MAP
@Image 1: anchor still for this shot: framing, light direction and car-interior layout in frame one; frame one matches this exactly; do not copy any text.

SCENE CONTEXT
On an overcast, drizzly day, a private-hire driver sits in a parked car on a wet Coventry kerb waiting for work; his phone sits dark in its vent mount and his fingers drum on the wheel.

LOCATION MAP
Camera wedged on the passenger seat at chest height, facing across the cabin towards the driver's side. Foreground: the soft edge of the passenger seat. Midground: the driver's hands on the lower half of the steering wheel and a phone in a vent mount beside it, its screen edge-on to the lens. Background: the windscreen with drizzle, a wiper parked mid-glass, a wet grey kerb and a slip road beyond, soft. A parking ticket face-down on the dash; a charging cable looped over the gear lever.

FIRST FRAME AND SPATIAL BLOCKING
The first visible frame already shows the driver from the chest down, both hands resting on the wheel at the bottom of frame, the phone dark in its mount at frame right, the wiper parked mid-glass. His face is out of frame.

FORMAT MODE
SINGLE CONTINUOUS TAKE. Camera static.

OPTICS
About 80° diagonal field of view, phone main-camera perspective, 1 metre from the wheel. Environment visible to the frame edges, deep edge-to-edge focus, no telephoto compression, no creamy bokeh.

TIMELINE
0-1s: Ambience only. Hands still on the wheel. End state: still.
1-5s: The fingers of his right hand drum slowly on the wheel, stop, start again. End state: fingers resting.
5-6s: The wiper makes one slow sweep across the windscreen and parks again. End state: wiper parked mid-glass.
6-8s: Hands still; the phone stays dark; ambience only. End state: unchanged frame.

PHYSICS
His fingertips press slightly into the leather of the wheel; the wiper drags water in a smeared arc; drizzle beads gather again on the glass after the sweep; the car does not move.

LIGHTING
Flat overcast daylight through the windscreen is the only key, soft and slightly cool; the side window camera-right adds a brighter edge; the cabin roof and footwell fall into soft shadow; the windscreen itself is slightly overexposed.
Real skin texture with visible pores and fine hairs on the backs of his hands; a plaster on one knuckle.

AUDIO
Ambience: drizzle on the car roof, traffic passing on a wet road nearby.
Foley: soft finger taps on the wheel from 1 second; the wiper's rubber squeak and thunk at 5 seconds.
No dialogue. No background music. No subtitles.
Sound from the phone's microphone: close cabin sound, faint road noise outside.

FINAL FRAME
The driver's hands resting on the wheel, the phone dark in its mount, drizzle on the windscreen, camera static.

POSITIVE CONSTRAINTS
Muted colour inside a parked car as it really looks: a charcoal dashboard and grey seat fabric, rain beads on the glass, the world outside soft and grey; people in navy, grey and mid-blue everyday clothes; nothing saturated.
No on-screen text, captions or subtitles. All signs, labels, mugs, clothing, papers and screens are plain or turned away, with no readable words, logos or numbers. Number plates are not readable.
The phone's screen is never visible face-on. The engine is off and the car is parked. Exactly one person, seen only from the chest down.
Filmed handheld on a smartphone main camera: small-sensor look with deep focus, slight edge over-sharpening, faint sensor noise in the shadows, auto exposure and auto white balance as recorded, ungraded colour.
```
For **v04_P-02** ("August"): the same anchor still and every block identical, except the TIMELINE (1–2 s the phone lights and buzzes, glow on his fingers and the dash; 3–4 s it lights again; 4–7 s his hand lifts it from the mount up towards his ear, out of the top of frame; the car stays parked) and the matching foley (two buzzes against the plastic). The light line does not change.

---

## 9. Edit grammar (us)

- **The receipt is the only proof device** (§1.2): exact crops at the listed rectangles, on a navy card, one orange underline, a source and date line, a context strip, a slow 102% → 108% push-in. No redraws, no count-ups to numbers we don't hold, no up-arrows, no Google marks.
- **Devices:** the green-laptop push-in to full frame (1, 2, 13, 15); the duet for 2's 9:16 cut; stitches 3 → 9 and 1 → 15; the green-screen (segmentation) effect for 14; the footer push-in for 1; the month-by-month mask reveal for 4; the 16:9 "phone clip beside receipts" layout (the 9:16 clip in a rounded phone frame on the left third, receipts building on the right two thirds) when 3, 8 and 9 are reused on case-study pages.
- **Screen keys:** corner-pin on the four dots; a glare pass; grain match; for "phone filming a laptop" (8, and 11's laptop) add a 1–2 px chromatic edge and faint moiré.
- **Pacing:** social, a cut or 105–110% punch-in every 1.5–2.5 s, payoff at 60–70%; web, 3–5 s holds on faces, first receipt at 65–75%. Trim the 1 s handles off social cuts (or lay the hook card over them) so frame 1 is never dead air.
- **Sound:** keep Seedance's native room tone and foley; lay the real voice memos in wherever sync allows; no music under testimonial answers (1, 6, 13 work without music); otherwise one sparse licensed bed under −20 LU behind speech; no trending copyrighted audio; social masters at −14 LUFS.
- **Finishing:** captions word-timed, white with a soft shadow, inside the 9:16 safe zones (clear of the top 12% and bottom 20%); one upscale route, one grain value and one sharpen value per video; grade lightly in the edit only. Brand colours appear only in our graphics: Inter type; GRP orange `#F7931E` / blue `#3FA9F5` on `#0B1628` for googlerankerpro.com placements, Hulk lime `#C6FA61` on `#121C17` if the user picks Hulk for social; Organic Fostering colours only on its own receipt card.
- **Labels** (§1.3) stay on screen throughout; platform AI toggles on every post.

---

## 10. Open questions for the user (● blocks a video)

1. ● Consent and assets: written consent, 27 photos (production_rules A.2) and voice memos from each person: the Golden Line owner, the Coventry Airport Taxis 247 owner, the Leam Taxis owner, the York Cars manager, the Organic Fostering director or manager, Hassan Pasha, T1 and T2 (and Sajid if wanted). Who are the real T1 (SEO specialist) and T2 (reporting lead)?
2. ● Which business owns each Business Profile screenshot: is the 114-calls profile Leam Taxis' and the 79-interactions profile Coventry Airport Taxis 247's? Please also send the Coventry Calls tab and the per-type breakdown.
3. ● Agency credit per client: Coventry's footer says SMEK (smek.co.uk lists Hassan Pasha as CEO): which name do we use, and will the footer be updated? York Cars' footer says Xoom Media while Hulk's portfolio lists York Cars: what did Hulk do? Leam Taxis appears only in Hulk's portfolio. Who built Organic Fostering's Sept 2026 rebuild? What is Hulk's role on Zentro? May we name each client?
4. ● The Golden Line work log (for V01's 'what changed', T1's task in V10, and V15), and the Coventry work log if the June 2026 location pages should become a later V15 episode.
5. ● T2's real location (UK or Pakistan) and photos of the real workplace(s); the four listed office addresses are serviced offices. Does T2 really deliver Leam Taxis' monthly report?
6. ● York Cars' own premises photos, and which address is the dispatch office (Blossom Street or Unit 2 Heritage Park, YO19 5UP). Without them there is no V05.
7. Are Leam Taxis, Golden Line and Coventry Airport Taxis 247 (and Global Cars 247) one operator group, and is the 'Ali' in the reviews one person? If so, one consenting person witnesses, captioned with exactly how the businesses connect.
8. Search Console 'Compare' exports (previous 3 months, or the 16-month view) for Golden Line and Coventry. With them we can make honest growth versions of V02, V08 and V15; without them we never say growth, 'just hit' or 'now'.
9. Dated query reports or SERP captures for any 'No.1' claim (Leam Taxis, York Cars). Until then, no 'No.1', '#1' or 'first' anywhere.
10. Brand on screen per placement: Google Ranker Pro, Hulk Marketing, or the lockup 'Hulk Marketing · part of Google Ranker Pro'? And is Hassan the founder for 13–15 (and does Sajid join)?
11. Real phone footage before we generate any landmark: 8–10 s clips of Castle Bridge and Market Place (Warwick), The Parade (Leamington), Kenilworth, York Station and the Minster, the Coventry ring road, Chester Road (Old Trafford, with a bus), plus one dashcam drive per town. May we reuse Organic Fostering's 19 Drive clips?
12. Higgsfield UI check before the first generation: is 1080p offered for Seedance 2.5 (or only 720p), is there a start-frame slot, and does a Soul ID appear as an Element?
13. Optional: Wayback captures from your own browser (yorkcars.co.uk snapshot 20250916232610 for the V04 'b' wipe; Coventry before June 2026).
14. Client-side fixes before any site appears on camera: Coventry's Slough (Global Cars 247) review widget, SMEK footer and 'Qoute'/'Relaible' typos; Golden Line's test pages in the sitemap and its re-attributed review quotes; Organic Fostering's delivered reels that still show the superseded £447.60.
15. Disclosure wording sign-off (you and your adviser) for the three on-screen label tiers, plus the TikTok AIGC, YouTube altered/synthetic and Meta AI-info toggles on every post.
16. Permissions for the tip-of-the-week episode bank: York Cars' fares page (Ep 3) and Zentro (Ep 8); Organic Fostering's Ofsted grade only after the report PDF is checked.

---

## 11. Fix log: every weakness the judge named, and where it is fixed

| Judge's point | Fix in this plan |
|---|---|
| A v10 "even the October dip" | F1's line rewritten (V10); October is a part month everywhere (§1.5) |
| A v9/v12 "114 calls since May" inside a September report | V09 end card shows the real crop with its own range "May–Oct 2026 (October part month)"; V12 pays off "25 calls from Google in September" |
| A v8 invented "four am run to Birmingham" | V08 rebuilt on B's "One in Ten" with candid copy; no invented specifics (§1.5) |
| A v15 "Six hundred people saw it… hardly anyone got that far down"; sitemap lastmod as a "verifiable driver" | V15 moved to Golden Line; "times shown"; the line deleted; no causal verbs; lastmod is "dated"; A's Coventry version kept only as a later episode if the work log confirms the build |
| A v1 rests on the unnamed Leam GBP screenshot | V01 is Golden Line (verified footer, attributed GSC); A's Leam version is the alternate only if G3 clears and Golden Line declines |
| A's generated landmarks; trams on Chester Road | Real footage list RF01–RF08 first (§2.9); landmarks generated only from the user's photo, never as evidence; a bus on the A56 |
| A: 20 s walk-and-talk through a doorway; two identities in v02/v11; three mugs | V05 split into two 14 s generations cut on the doorway (walking beside, not backwards); V02 has one identity on camera; V11 keeps a single medium-wide two-shot; F1 pours two mugs |
| A: exterior palette pasted into interiors; "handheld… arm's length" used for propped shots | PAL-EXT / PAL-INT / PAL-CAR (§2.1); the logged propped-camera test (§2.4, §8.2) |
| A: v4 strip lists "directions"; v13 misattributes a site line; Ali reviews not flagged | V04 context lists only calls, chat clicks, bookings, website clicks; only "No ranking guarantees" and "See the change." are called the site's own; G10 |
| A: the same push-in on all 15; web pieces open cold on data | Web films open on a person and land the first receipt at 65–75%; social devices vary (duet, stitch, green-screen effect, footer push-in, month-by-month reveal) |
| B: private-hire car on the Leamington station rank | Rank shots deleted; V09 is a parked car on a terraced street; TAXI lock forbids ranks |
| B: "best month since May"; "665 people… last quarter"; "312 clicks last quarter"; "on the first page… now" | §1.5 rules; V03 and V09 wording; V10 T1 line has no "last quarter"; V15 "times shown, 19 Jul–18 Oct" |
| B: N1 spread over six fallbacks; v6 Version C "what we built" | N1 only in V01 (B2) and V15, third person, never "we"; V06 Version C deleted |
| B: 123 first takes; v11 three people; v5 walking backwards; warm-sun "August" plate | 86 first takes; ×2 ratios only where the judge allows; V11 at most two; V05 not backwards; both V04 plates overcast from one anchor still |
| B: v7 on Zentro and v14 on York prices with no data | V07 is "Four ways to say Kenilworth taxi" on real rows; York prices move to tip Ep 3 with permission and no performance claim |
| B: "Golden Line and Coventry share booking keys" | Corrected (§3): Coventry shares Leam Taxis' booking `site_key`; Golden Line and Coventry share duplicated reviews and a phone number |
| C: "15,900 times Google showed us"; "307 people searched this"; "people searching his name"; "here's what made it ring"; "03:04" stamp | "15.9K"; "times shown"; "brand searches: top two on average"; "Here's what we did. Here's what Google shows now."; no clock stamps |
| C v14 "one proper page for that journey" | Heathrow tip (Ep 7) reframed as "a page for the inbound direction" |
| C v10 chair-spin montage | V10 is one person per clip, "Hands First"; no spins |
| C overrode §11 capture modes; inverted focus | Capture modes follow production_rules §11 as the judge set them; no inverted focus unless a test passes |
| C v12 York reviewer names; v9 AI-NARR reaction; owner letting a call ring; car pulling away; fostering allowance figures | No reviewer names; no AI reaction (owner's own clip preferred); no call-ignoring; cars stay parked during calls; no allowance figures |
