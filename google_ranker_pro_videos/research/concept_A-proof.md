# Concept A: "Show the receipt"

**A proof-first, data-led documentary series for Google Ranker Pro / Hulk Marketing. 15 videos.**

Pitch by Creative Director A, 22 Oct 2026. British English. The source of truth for every number is `assets/gsc/gsc_data.json`, the PNGs in `assets/gsc/`, the live sites (captured 22 Oct 2026) and the research files in this folder. Production rules are in `production_rules.md`, which distils the user's `human-realism`, `production-consistency`, `cinedance-higgsfield` and `higgsfield-production` skills. This pitch follows those rules and never overrides them.

---

## 0. The idea in one paragraph

The agency's own site already says it best: **"See the change. Not just the claim."** and **"A number needs its context."** So every one of the 15 videos is built around **one real number that the edit reveals as a receipt**: an uncropped, unredrawn crop of the real Search Console or Business Profile screenshot, with its source and date range printed underneath. The people are **witnesses, not salespeople**. A taxi owner, a fostering-agency manager, an SEO specialist and the founder each say, in their own approved words and their own voice, what the number meant on the ground. The footage looks like a small documentary crew (or the person's own phone) followed them through one wet October week in the Midlands: pre-dawn airport runs, a dispatch office radiator ticking, a laptop turned towards the owner, rain on the windscreen. Nothing is glossy. **Nothing on screen is a claim the screenshots can't back.** Where the data is weak, the video says so out loud ("that's an average", "October's only half a month"). In a category full of "+300%!" graphics, that honesty is the differentiator.

### Why it works
- **It is the only fully honest way to use AI footage for client proof.** The data is real and comes from the client's own Google accounts, and the people are real (Mode B, consented). The footage is clearly labelled re-creation.
- **Realism follows from the genre.** Documentary means available light, handheld operators, real rooms, real weather and people who pause. That is exactly the opposite of the "polished stock presenter" look of the five existing service videos (`agency_googlerankerpro.md` §8), which the user said must not happen again.
- **The numbers do the selling,** and each number is in the first 2 seconds of the social cuts (TikTok and Shorts search autoplays the opening; see `creative_ideas.md`).

---

## 1. The series grammar (applies to all 15)

### 1.1 Witness, Evidence, Context
Every video, whatever its length, has three beats:
1. **Witness:** a real person (or, in fallback, real hands and real places) in their real world.
2. **Evidence:** the receipt, a real screenshot crop pushed in on, with one highlight rule. It is never redrawn, re-typed or animated from estimates.
3. **Context:** one honest line that keeps the number fair: "average position", "last 3 months", "part month", "no earlier period to compare yet".

### 1.2 The receipt (edit device, never generated)
- **Source:** the real PNG crop at the rectangle listed per video (x, y, w, h in original pixels, from `gsc_story.md` §4). Single GSC row *n* is at `24, 904 + round((n−1)×49.1), 1318, 49`.
- **Treatment:** the crop sits on a navy `#0B1628` card with 12 px radius. A thin orange `#F7931E` underline draws under the one figure that matters. Use a slow 3 to 4 s push-in (102% to 108%) with a light paper-grain match to the footage. Add a soft tick SFX on the underline, and nothing else.
- **Source line (always on, Inter 500, `#BDCBDC`):** e.g. `Google Search Console · goldenlinetaxiswarwick.co.uk · last 3 months to 18 Oct 2026`.
- **Context strip** when needed, small, under the source line: `Average position across the period, not a single ranking.` / `October is a part month.` / `Business name confirmed by [client], [date].`
- **Banned in the edit:** "No.1", "#1", "growth", "+x%", ▲ arrows, count-up animations to numbers we don't hold, re-built charts from pixel estimates, Google logos or Google brand colours on our graphics. The screenshots naturally contain Search Console UI; keep them as evidence, never as our branding.

### 1.3 Disclosure labels (persistent, lower-left, small)
| Footage type | Label |
|---|---|
| Real person, Mode B re-creation | `AI re-creation made with [Name]'s permission. Their words, their voice. Real data.` |
| Labelled AI narrator (fallback only) | `AI presenter. Real client data. Not a client testimonial.` (adapted from the site's own wording) |
| No-face generated b-roll | `Illustrative footage. Real data.` |
Also set the platform AI-content toggles (TikTok AIGC, YouTube altered/synthetic, Meta AI info). Final wording to be confirmed with the user (`production_rules.md` §9).

### 1.4 Words in people's mouths
- **Client witnesses (videos 1 to 6, 9):** we supply **questions and the facts they may quote**, never their sentences. Their answer is transcribed from their own voice memo, they approve the transcript, and that exact text goes into the Seedance timeline with their memo as `@Audio`. The lines shown below are placeholders for structure only and are marked `[their words]`.
- **Agency people (7, 8, 10 to 15):** we draft scripts, and they edit and approve them before recording.
- **Numbers spoken aloud** are written as words in the prompt ("five point three", "a hundred and fourteen") and must match the receipt exactly.

### 1.5 Brand on screen
- googlerankerpro.com placements (homepage, service pages, case studies) use **Google Ranker Pro**.
- UK social and anything the user's plan calls "Hulk" uses **Hulk Marketing**.
- Possible end-card lockup: "Hulk Marketing · part of Google Ranker Pro". The user decides (agency research §1, §11).
- Coventry Airport Taxis 247's footer credits **SMEK** (Hassan Pasha's company). Before any video says "we did this", the user confirms which name to use, and ideally updates that footer.

---

## 2. Brand allocation: one anchor number per video

| # | Video | Brand featured | The anchor number (receipt) | Source file and crop |
|---|---|---|---|---|
| 1 | Testimonial 60 to 90 s | **Leam Taxis** (leamingtonspa-taxis.co.uk) | **114 calls** from the Business Profile, May to Oct 2026; **25 in September** | `leamingtonspa_gbp_calls_may-oct2026.png` headline+chart `15,165,910,310`; Sept tooltip `735,278,100,55` |
| 2 | Results walkthrough 30 to 45 s | **Golden Line Taxis Warwick** | **312 clicks · 18.2K impressions · 744 searches** in 3 months; airport terms on page one (5.3 / 6.1 / 7.1) | `goldenlinetaxiswarwick_gsc_3m.png` totals `24,201,720,110`; rows 6, 7, 20; pagination `930,2135,410,40` |
| 3 | Milestone 15 to 20 s | **Coventry Airport Taxis 247** | **"coventry airport transfers": average position 6.0, page one, 10.5% CTR** | `coventryairporttaxis247_gsc_3m_full.png` row 4 `24,1051,1318,49` |
| 4 | Before and after 20 to 30 s | **Coventry Airport Taxis 247** (Business Profile) | Interactions: **May near 0 → Aug 32** (79 total, May to Oct) | `coventry_gbp_interactions_may-oct2026.png` headline+chart `40,175,890,310` |
| 5 | Premises tour 30 s | **York Cars** | **2,695 Google reviews** (site review widget, 22 Oct 2026) | Fresh dated capture of the widget on https://yorkcars.co.uk/ (to take, see §7) |
| 6 | Client FAQ 20 to 30 s | **Organic Fostering** | **32 plain-English guides** on a rebuilt site (61 URLs in the sitemap, lastmod 13 Sep 2026) | `https://organicfostering.co.uk/sitemap.xml` + `assets/sites/organicfostering/now_desktop_full.png` |
| 7 | "What I learned" selfie 20 s | Team (SEO specialist), about **Golden Line** | **Four ways to say "Kenilworth taxi", four different positions:** 6.7 / 8.5 / 8.6 / 16.4 | Golden Line rows 4, 19, 14, 13 |
| 8 | Screen recording + VO 30 s | **Golden Line** (team voice) | **"airport taxi warwick": average position 5.3** (not "3": no row sits at 3) | Golden Line row 20 `24,1837,1318,49`; row 6 `24,1150,1318,49` |
| 9 | Reaction 15 s | **Leam Taxis** | **September 2026: 25 calls, the best month** | Leam GBP tooltip `735,278,100,55` |
| 10 | Meet the team 30 s each | Agency team | One real number per person, from a client they actually worked on (user verifies) | Per person (see video 10) |
| 11 | Behind the scenes 20 s | **Zentro** (audit) | **13 repair pages** (10 laptop brands + 3 phone brands) and **no data yet** | Live site nav, 22 Oct 2026; `assets/sites/zentro/now_desktop_full.png` |
| 12 | Day in the life 30 s | Team member delivering **Leam Taxis'** month-end report | **114 calls, May to Oct** (the report that video 9 opens) | Leam GBP headline `20,165,240,80` |
| 13 | Founder intro 45 to 60 s | Agency (founder) | **Hulk Marketing Ltd, company no. 15931335, incorporated 2 Sep 2024** (public record), then a montage of the receipts from 1, 2 and 4 | Companies House page (saved: `assets/sites/hulkmarketing_dl/ch.html`; recapture as PNG) |
| 14 | SEO tip of the week 30 s | Founder; Ep 1 uses **Golden Line** | **"taxi warwick": 665 impressions at position 10.7, 0.9% CTR**: the edge of page one | Golden Line row 5 `24,1100,1318,49` |
| 15 | Founder commentary 30 to 45 s | **Coventry Airport Taxis 247** | **"coventry airport transfers" 6.0 at 10.5% CTR; "coventry airport taxi" 7.0**; location pages added 6 to 8 Jun 2026 (sitemap); next prize "airport transfers coventry" 607 impr at 22.0 | Coventry rows 3, 4, 2 (`24,1002…`, `24,1051…`, `24,953…`); chart plate `coventryairporttaxis247_gsc_3m_chart.png` `0,121,1300,355` |

**Spread:**
- Leam Taxis: 1, 9, 12.
- Golden Line: 2, 8, plus the 7 and 14 references.
- Coventry Airport Taxis 247: 3, 4, 15.
- York Cars: 5, plus tip episode 3.
- Organic Fostering: 6, plus tip episode 5.
- Zentro: 11, plus tip episode 4.
- Agency team and founder: 7, 10, 12, 13, 14.

Every results-led video (1, 2, 3, 4, 8, 9, 15) sits on a brand that has a real screenshot. York Cars, Organic Fostering and Zentro have no performance data, so they get honest **structure** stories (reviews, guides, page architecture) with no traffic claims.

**Not featured:** airporttaxis247.co.uk (a separate Bracknell business on the evidence, average position 72.6).

---

## 3. Cast

All real people are **Mode B**: identity comes from their own 27-photo set (`production_rules.md` A.2), trained as a Soul ID (20 to 30 photos), plus a Nano Banana Pro character sheet (B.2 skeleton, no face prose). They give written consent covering likeness, voice, approved words, platforms and term. They provide their own voice memos (A.3), one approved line per take. **No face prose is ever written for them.** Only wardrobe, behaviour, light and one texture note go in the prompt.

| ID | Role | Videos | Mode | Look and wardrobe direction (prompt wardrobe line, no logos, no printed text) | Voice / accent | Real-life realism notes |
|---|---|---|---|---|---|---|
| **W1** | Leam Taxis owner (name TBC; nobody is named publicly) | 1, 9 | B | Their real working clothes, photographed on the day. Default line if they have nothing specific: "a dark navy quilted gilet over a grey long-sleeve polo shirt, dark work trousers, black trainers; no logos, no printed text" | Their own memo (Warwickshire, or wherever they're from; never described in text) | Shot where they really work: a cab-office desk, a kitchen table at 4 am, the driver's seat **parked with the engine off** (never on a phone while driving; that's illegal in the UK and reads as fake) |
| **W2** | Golden Line owner or dispatch lead (reviews name "Ali"; role and surname unverified) | 2 | B | Real clothes. Default: "a black zip-neck fleece over a white T-shirt, dark jeans; reading glasses folded in the chest pocket only if he really wears them" | Own memo | A real dispatch-desk habit: a two-way radio handset, a paper diary, a phone on charge |
| **W3** | Coventry Airport Taxis 247 owner-driver (TBC) | 3 (voice optional in 4) | B | Real driving clothes. Default: "a plain charcoal crew-neck jumper over a collared shirt, dark trousers" | Own memo | Parked-car selfie after a real drop-off: seatbelt off, keys in hand |
| **W4** | York Cars owner or operations manager (TBC; nobody is named publicly) | 5 | B | Real clothes; a hi-vis vest only if they really wear one in the yard | Own memo (Yorkshire, if that's them) | Real office and yard photos are required. Hulk's portfolio says it did York Cars' fleet photography, so ask Hulk's own records first |
| **W5** | Organic Fostering registered manager or director (TBC; nobody is named publicly) | 6 | B | Real office clothes. Default: "a soft grey knit cardigan over a plain blouse, lanyard card turned to face the body" | Own memo (Manchester, if that's them) | **Adults only.** No carers, no children, no case files, no whiteboards with names. Office at Beaumont House, Old Trafford, from real photos |
| **F1** | **Hassan Pasha**, CEO & Co-Founder (Companies House director) | 13, 14, 15, end-twist of 10 | B | Keep his recognisable look, but documentary, not studio. **13 and 15:** "a navy suit jacket over an open-collar white shirt, no tie, dark trousers; a steel or gold watch on the left wrist" (matches his site portraits without the pocket-square studio gloss). **14 (weekly, casual):** "a plain navy crew-neck jumper over a white T-shirt" | Own memo. The existing founder videos are 10 s silent studio portraits, so we need fresh memos | His public portraits are hard-lit black-background studio shots. **Do not use them as the look reference.** Train identity on a fresh 27-photo window-light set; studio frames pull the output towards a glossy portrait |
| **F2** | Sajid Armughan, Co-Founder & MD (optional) | 10 (optional), 13 (optional two-shot) | B | Real clothes: "a dark unstructured jacket over an open white shirt" | Own memo | Only if he consents. The Companies House name is "Muhammad Sajid"; confirm how to caption him |
| **T1** | SEO specialist (candidate from the Hulk team page: Muhammad Ali, SEO Specialist; consent required) | 7, 8 (hands and real voice), 10, 11, and 2 (fallback) | B | "a mid-blue overshirt over a plain white T-shirt, dark jeans; an orange enamel mug on the desk" (the one brand-orange object) | **Real recorded voice for VO** (video 8 needs no generated voice at all) | Real workplace only. If the team works remotely, film the real home desk. Do not imply a fitted HQ in Tower 42 |
| **T2** | Delivery or reporting lead (candidates: Javaid Ahmad, Senior Project Manager; Momna Imran, Communications & Audit; consent required). **UK or Pakistan location is unverified; the user tells us** | 12, 10, 11 | B | "a navy knit jumper with sleeves pushed up, plain dark trousers", or what they really wear; no logos | Own memo, own accent, never described | If Pakistan: only details that are true of their real day (their real office, their real commute, their real tea). If UK: same rule. Time-zone captions only if true |
| **N1** | **Labelled AI narrator, fallback only** | Fallback for 1 and 15 only | **A** (invented, approved once as a sheet, then treated as Mode B) | An invented woman, about 52, white British, the plain-spoken Midlands manager type: "short ash-brown hair greying at the temples with a few flyaways, reading glasses pushed up on her head, a charcoal wool jumper over a pale blue collared shirt". Full human-realism 13-block spec on the sheet only (50 to 65 age ladder, "fair, warm-toned skin with a few sun spots"; anti-beautification line; drop the hype sentence on Nano Banana Pro) | Synthetic. Casting brief: "warm, dry, unhurried, but never slow; Coventry accent" | **Never** named as a client, never says "we" or "my firm", always carries the AI presenter label. Deliberately unlike the five glossy service presenters: real-room light, lived-in clothes, glasses smudge |
| **C** | Incidental people: drivers' and passengers' hands, colleagues in soft focus, passers-by | Throughout | **C** | Two lines only: real skin texture, one imperfection (a plaster on a knuckle, a chipped nail) | None, or unintelligible background | Never identifiable, never presented as a named client's staff or customer |

**If W1, W2 and W3 turn out to be one operator group** (shared booking `site_key`, partner blocks and "Ali" in reviews across all three sites suggest it, but this is UNVERIFIED): one consenting person can witness for all three. Each clip still names only the business whose data is on screen, and the caption says how they're connected (e.g. "Owner, Leam Taxis and Golden Line Taxis"), so nobody is misled.

---

## 4. World Bible: "One wet October week"

Every generation in the set carries these blocks **verbatim**. This is what makes 15 videos from about 71 generations look like one real shoot.

**Setting truth.** Late October 2026, the week after the data window closed. The Midlands (Leamington, Warwick, Kenilworth, Coventry), plus York and Old Trafford for one video each, plus the agency's real workplace(s). Autumn: wet tarmac, leaves in gutters, heating on, condensation on car windows, dark by half five.

**Palette line (paste verbatim):**
`Muted autumn palette as it really looks: wet slate greys, overcast white sky, black tarmac, red-brick and cream stucco, cold white LED and older amber street light; people in navy, grey and mid-blue everyday clothes.`
Agency scenes add: `One small warm orange object in frame, such as a mug or a notebook.` (This echoes the brand orange without a graphic.)

**Light logic (one named source per shot, from `production_rules.md` D.5, verbatim per scene):**
- Interiors: overcast daylight from one window as the key, weak ceiling panels, the window slightly overexposed.
- Pre-dawn and night exteriors: cold white LED street lamps mixed with an older amber lamp, headlight spill, phone or dashboard glow on faces from below.
- Screens never light faces green: "the screen gives off almost no light".
- No "cinematic", "studio", "ring light" or "three-point" anywhere. Deep skin tones get the correct-exposure line.

**Capture mode per video (texture line verbatim from `production_rules.md` D.1, last line of every prompt):**
| Mode | Videos |
|---|---|
| **DOC-CAM** (handheld documentary camera; tripod for sit-down interviews) | 1, 2, 5, 6, 10, 13, 15, and all observational b-roll in those videos |
| **PHONE-SELFIE** | 3, 7, 9, 12 (to-camera beats), 14 |
| **PHONE-REAR** | 4, 8, 11, 12 (b-roll) |
Never mix two modes inside one generation. The docs-and-phone mix *between* generations is the documentary texture.

**Set-dressing anchors (two or three per location, kept in place across every shot of that set-up):**
- Cab office: two-way radio handset on its charger, a paper bookings diary, a coat on a hook, a radiator with chipped paint, a mug with a tea ring.
- Car interior: phone cradle on the vent, a parking ticket face down on the dash, a wiper parked mid-glass, rain beads on the windscreen.
- Agency desk: cables under the desk, a blank sticky note on the monitor bezel, the orange mug, a half-closed blind.
- Fostering office: tea, a plain notebook, a lanyard turned round, a plant that needs water.
- **Uncomposed element in every shot:** a half-cropped passer-by, a car door at the frame edge, a mug handle.

**Behaviour line (all modes):** people blink, glance away to think, restart a gesture, adjust a sleeve, take a breath before speaking, and finish with a small involuntary nod. Write gestures, never emotions.

**Forbidden in generations:**
- Readable text of any kind: signs, plates, mugs, clothes, papers, screens, lanyards.
- Logos and liveries, unless the user supplies a real livery photo as an `@Image` prop reference.
- Google logos or colours.
- Invented firm names or phone numbers.
- Screen content (screens are green, angled away or defocused).
- Background music, subtitles, captions.
- Faces for real named people built from prose.
- Any child (Organic Fostering) other than none.
- Hype or polish words (`production_rules.md` D.6).
- Gimbal, drone or dolly moves.
- Shallow bokeh on phone modes.
- Golden-hour glow as a default (overcast is the house light; low sun at most once per video).
- Driving while on the phone.
- "Premises" shots of a client without their real photos.
- Yellow New-York-style cabs (UK private hire is silver, white, black or grey hybrid saloons, people carriers and minibuses).

**Finish lock:**
- One grain value per video and one upscale route for the whole set: Higgsfield `upscale_video`, `ugc` preset for phone modes, `aigc` for DOC-CAM, applied once and only if the UI capped at 720p.
- Grade in the edit (lift the shadows slightly, never teal-and-orange).
- Mix at −14 LUFS for social.
- Captions sit inside the 9:16 safe zones.

**UI settings on every generation:**
- Seedance 2.5, reference mode, **1080p** (720p if that's the cap; flag it), aspect ratio set in the UI, whole-second durations, audio on.
- Selectors: Era 2020s, Physics realistic, Tone calm or warm, Genre unset (or documentary), Lens matched to the mode (24 mm for phone; 50 or 85 mm for DOC-CAM).

---

## 5. The 15 videos

Generation IDs follow `grp_v[NN]_[setup]-[shot]`. The A-codes are A-roll (talking or reacting) and the B-codes are b-roll. "BR" codes come from the shared b-roll bank (§6), which is generated once and reused. Every generation has a 1 s ambience-only handle at the head and tail.

---

### Video 1: Testimonial. "Every call is a fare" (Leam Taxis)
- **Duration and format:** 75 s, **16:9** master (homepage, case study). Optional 9:16 45 s cut built from separately generated 9:16 versions of A3, B1 and B4.
- **Anchor:** 114 calls from the Business Profile, May to Oct 2026; 25 in September (the peak). Attribution gate: the screenshot shows no business name, so the user confirms it is Leam Taxis' profile before release.
- **Hook (0 to 4 s):** black screen, a phone vibrating on a dashboard at 4 am, rain. A hand takes it. Under it, the owner's own voice from their memo: `[their words about the early calls]`. Cut to the title card "114".
- **Structure:**
  - Problem (0:04 to 0:22).
  - What changed (0:22 to 0:45).
  - The receipt: the chart's six monthly points appear one by one as the owner speaks; the Sept tooltip lands on their result line (0:45 to 1:02).
  - Close: the owner's last line, then the car pulling away into the dark (1:02 to 1:15).
- **Interview questions (the owner answers in their own words; we transcribe, they approve):**
  1. "What was the phone like before?"
  2. "What did you notice change, and when?"
  3. "What does a call from Google mean to you?"
  4. "What would you tell another firm owner?"
  They may quote "a hundred and fourteen calls" and "twenty-five in September" (and nothing else numeric). No "number one" until a dated proof exists (`client_leamingtonspa-taxis.md` verdict).
- **Version A (preferred):** W1, Mode B, sit-down DOC-CAM interview in their real setting, plus their own voice memo as `@Audio`.
- **Version B (fallback):**
  - **B1 (voice only):** the owner consents to their voice but not their face. The memo plays over no-face b-roll (B1 to B4, BR01 to BR03, BR06). Caption: "[Name], Leam Taxis (voice)".
  - **B2 (no owner at all):** N1, the labelled AI narrator, tells the case in the third person ("Leam Taxis has run in Mid Warwickshire since 2014…", which is on their About page) with the real receipt, plus the same b-roll. No client quote is used, and the site testimonials are never used (undated, unverified).
- **Generations (Version A):**
  | ID | Purpose | Location | Who | Camera and mode | Length |
  |---|---|---|---|---|---|
  | v01_A-01 | Interview medium: the problem, 1 or 2 lines | Owner's real office or kitchen table (photo 27 plus 6 to 10 location photos as `@Image`) | W1 | DOC-CAM tripod, 50 mm block, eye-line just past camera-left to an off-screen interviewer | 15 s |
  | v01_A-02 | Interview close: what changed | Same | W1 | DOC-CAM tripod, 85 mm block, same axis | 15 s |
  | v01_A-03 | Interview medium: the result line (quotes the number in words) | Same | W1 | DOC-CAM, 50 mm | 12 s |
  | v01_A-04 | Interview close: advice and closing line, ends on a small nod | Same | W1 | DOC-CAM, 85 mm | 12 s |
  | v01_B-01 | Owner at the desk at night writing a booking in a paper diary, phone face-up beside them, its screen glow tilted away from camera; one radio crackle (no words) | Same office, lamp on, window black | W1 | DOC-CAM handheld observational, 50 mm | 8 s |
  | v01_B-02 | Over the shoulder: owner looking at a phone in hand, **flat green screen** with four visible corners, thumb on the side of the phone | Same | W1 (back of head and shoulder, Mode B) | DOC-CAM, static, 50 mm | 8 s |
  | BR01, BR02, BR03, BR06 | Shared b-roll: dashboard phone pre-dawn; suitcase into boot; M40 pre-dawn; The Parade at first light | see §6 | C / none | DOC-CAM or PHONE-REAR per bank | 8 to 10 s each |
- **Edit, data reveal:**
  - From 0:45, a full-frame receipt of the Leam GBP chart (crop `15,165,910,310`): mask-reveal the real line left to right in five steps synced to the owner's cadence. This is a reveal of the real pixels, not a redraw.
  - The Sept tooltip crop (`735,278,100,55`) punches in 120% on the word "September".
  - Context strip: `Calls made from the Business Profile · May–Oct 2026 · October is a part month.`
  - v01_B-02's green screen gets the same chart, corner-pinned, as a second angle.
- **Realism notes:** the interview is off-axis (eyes to the interviewer, never into the lens), with one restart of a sentence left in. Room tone is a radiator tick plus distant road hiss.

---

### Video 2: Results walkthrough. "The first time he saw it" (Golden Line Taxis Warwick)
- **Duration and format:** 40 s, **16:9** (homepage, case study).
- **Anchor:** 312 clicks · 18.2K impressions · 1.7% CTR · average position 18.9, and "1–25 of **744**" searches, 19 Jul to 18 Oct 2026. The page-one airport cluster: "airport taxi warwick" 5.3, "warwick airport taxi" 6.1 at 13% CTR, "airport transfers warwick" 7.1. The Golden Line footer credits "Made with ❤ by Hulk Marketing Ltd", the strongest attribution in the set.
- **Hook:** cold open on the real totals tiles (crop `24,201,720,110`), the "744" pagination underlined. Cut to the owner's face lit by the laptop.
- **Concept:** an agency specialist (T1) turns the laptop towards the owner (W2) at the dispatch desk. We watch him read his own numbers. He says two short things in his own words. The screen is green throughout and replaced with a real scroll of the PNG.
- **Version A:** W2 (Mode B) and T1 (Mode B) together. Two identities, so each gets a character sheet and the crops go in as `@Image`.
- **Version B:** T1 alone walks through the client's real data to camera. **This is honest without any AI presenter, because T1 is a real agency person.** No owner face, no owner words.
- **Generations:**
  | ID | Purpose | Location | Who | Camera and mode | Length |
  |---|---|---|---|---|---|
  | v02_A-01 | Two-shot over T1's shoulder: T1 turns the laptop (green screen, four corners visible) towards W2; W2 leans in, glasses on | Real Golden Line office (photos needed) or a neutral back room that is **not** presented as the premises | W2, T1 | DOC-CAM handheld, 50 mm, gentle reframe as W2 leans | 12 s |
  | v02_A-02 | W2 close, reading the screen; line 1 `[their words]`; two-finger tap on the desk | Same | W2 | DOC-CAM tripod, 85 mm; laptop back in soft foreground | 12 s |
  | v02_A-03 | W2 close, sits back, line 2 `[their words]`, half-smile | Same | W2 | DOC-CAM tripod, 85 mm | 10 s |
  | v02_A-04 | Insert: T1's hand on the trackpad scrolling, green screen steady | Same | T1 hands (Mode C wording) | DOC-CAM static, 50 mm | 6 s |
  | BR04, BR05 | Airport drop-off kerbside; Warwick Castle Bridge with a generic saloon crossing | §6 | C | — | 8 s each |
  Version B replaces A-01 to A-03 with **v02_T-01** (T1 to camera at their own desk, 15 s, 2 lines) and **v02_T-02** (T1 turns the laptop towards the lens, green, 8 s).
- **Edit, data reveal:**
  - The green screen gets a real vertical scroll of `goldenlinetaxiswarwick_gsc_3m.png`: totals, then the chart, then the table.
  - At 0:18, full-frame receipts of row 20 "airport taxi warwick 5.3" (`24,1837,1318,49`), row 6 "warwick airport taxi 6.1 / 13%" (`24,1150,1318,49`) and row 7 "airport transfers warwick 7.1" (`24,1199,1318,49`) stack one by one.
  - Context: `Average position over 3 months. Positions 1–10 are page one.`
  - Close on the pagination "1–25 of 744" crop, with the line "744 different searches found them."
- **Realism notes:**
  - The laptop screen "gives off almost no light", so the face is lit by the window.
  - The radio handset hisses once with no words.
  - Never show the site's own "No.1 Taxi Hire" headline.

---

### Video 3: Milestone. "Page one" (Coventry Airport Taxis 247)
- **Duration and format:** 18 s, **9:16** (Reels, TikTok, Shorts).
- **Anchor:** "coventry airport transfers": **average position 6.0 (page one)**, 8 clicks from 76 impressions, **10.5% CTR**. Secondary: "coventry airport taxi" 7.0.
- **Hook (0 to 1.5 s):** the receipt first. Row 4 crop full-width, with the query underlined and "6.0" ringed by the orange rule. Then a hard cut to the owner's selfie.
- **Concept:** the owner, parked up after a real early drop-off (engine off, seatbelt off), films one line to their phone. It is understated, as people really are.
- **Line:** `[their words, e.g. what being on page one for that search means to them]`. The words "number one" are not allowed; "page one" is fine because 6.0 is page one on average.
- **Version A:** W3, Mode B selfie, own memo.
- **Version B:** no face. A PHONE-REAR shot from the dashboard of hands resting on a parked wheel, rain on the glass, indicator ticking; then BR04. The data card carries the story with no voice, or with the owner's voice only if they consent to voice alone.
- **Generations:**
  | ID | Purpose | Location | Who | Camera and mode | Length |
  |---|---|---|---|---|---|
  | v03_A-01 | Selfie line, parked in a lay-by; airport traffic soft behind through the side window; re-grip once | Inside a plain dark people carrier, wet morning | W3 | PHONE-SELFIE, 24 mm, arm's length, auto-exposure breathing as the window comes into frame | 12 s |
  | v03_B-01 | Through the windscreen: A45 at dawn, wipers on intermittent, motorway-style signs unreadable | Car interior (camera on the dash), road ahead | none | PHONE-REAR, static on the dash | 6 s |
  | BR04 | Kerbside handover of a wheelie case | §6 | C | — | (reuse) |
- **Edit:** 0 to 1.5 s receipt; 1.5 to 13 s selfie; 13 to 16 s b-roll, with a second receipt (row 3 "coventry airport taxi 7.0", `24,1002,1318,49`); 16 to 18 s end card. Context strip: `Average position, last 3 months to 18 Oct 2026.`
- **Realism notes:** a front camera, so the face sits close and slightly enlarged, with deep focus. Eyes flick between the lens and the screen. The condensation line on the windscreen stays.

---

### Video 4: Before and after. "May vs August" (Coventry Airport Taxis 247, Business Profile)
- **Duration and format:** 25 s, **9:16** (social) and **16:9** (case study), each generated separately as a matched pair.
- **Anchor:** the real Business Profile chart. Interactions **near 0 in May, 32 in August** (the marker sits on the 32 gridline), **79 in total** May to Oct 2026. Context, honestly: it then settled (about 20 in Sept, about 13 in a part-month October).
- **Gates:**
  - The user confirms the profile is Coventry's (the name is not on screen).
  - Ask for the **Calls** tab and the per-type breakdown, so the plates don't imply "calls" if the interactions were mostly website clicks.
- **Why a data before-and-after:** no "before" website capture exists (the Internet Archive is unreachable from the sandbox; see `wayback_before.md`). We never mock up an old site. If the user later sends real archive captures (the rebuild is around Oct 2024; location pages were added in June 2026), a website wipe becomes a 10 s add-on.
- **Concept: twin plates, identical framing.** The left half is "May": a phone in a dashboard cradle, screen dark, a hand drumming on the wheel, rain. The right half is "August": the same car, same framing, the phone's glow pulsing from behind (screen faces away), and the hand takes it. Then the real chart wipes up between them, and its May and Aug points are ringed.
- **Version A / B:** no face is needed (Mode C hand), so this video is the same in both versions. An optional W3 voice line can go over the end.
- **Generations:**
  | ID | Purpose | Location | Who | Camera and mode | Length |
  |---|---|---|---|---|---|
  | v04_A-01 (9:16) | "May" plate: phone dark in its cradle, fingers drum, the wiper sweeps once | Parked car interior, overcast, rain | C hand | PHONE-REAR, static on the passenger seat headrest, 24 mm | 8 s |
  | v04_A-02 (9:16) | "August" plate: **same anchor still, same framing**; the phone glow pulses, the hand lifts the phone out of the cradle | Same | C hand | Same | 8 s |
  | v04_A-01w / A-02w (16:9) | Same pair for the case-study cut | Same | C | Same | 8 s each |
  | BR07 | Coventry ring road slip road at blue hour, generic saloons | §6 | none | — | (reuse) |
- **Continuity:** generate the "May" anchor still first, then build "August" from the identical still (use the same `@Image` anchor). Only the phone and the hand change. The light stays overcast in both, so the eye reads the difference as activity, not weather.
- **Edit:** 0 to 2 s, split screen with the labels "May 2026" and "Aug 2026" (edit text); 2 to 14 s, the plates play; 14 to 22 s, the real chart crop `40,175,890,310` rises between them with the orange ring on the May and Aug markers and the "79" headline underlined. Context: `Business Profile interactions (calls, chats, bookings, directions, website clicks). October is a part month.`

---

### Video 5: Premises tour. "2,695 reviews start here" (York Cars)
- **Duration and format:** 30 s, **16:9** (service page), plus a 9:16 version from a separate walk-and-talk generation.
- **Anchor:** **2,695 Google reviews**, as shown in the review widget on yorkcars.co.uk on 22 Oct 2026. We capture it fresh and dated, with no star average because none is shown numerically. **It is presented as context, not as an agency result.** Hulk's own York Cars page publishes no booking or ranking uplift.
- **Gates:**
  - Written confirmation from York Cars that the agency worked on the site and reputation (the footer says "Designed by Xoom Media").
  - Which address is the dispatch office.
  - Real premises and fleet photos (Hulk's portfolio lists fleet photography, so check Hulk's records).
  - W4's consent.
- **Concept:** a single-take walk-and-talk. The owner leads the camera from the dispatch room (radios, screens defocused, a night-shift coat on a chair) out to the yard, where a car's door is open. Two lines from the owner: `[their words about what reviews mean to a 24/7 firm]`.
- **Version A:** W4 Mode B, with real premises photos as the `@Image` location reference and a real livery photo as the `@Image` prop (lettering re-checked in QC; composite the real logo if any letter warps).
- **Version B:** no premises, no face. York city b-roll (BR08 York Station at blue hour, BR11 the Minster west front at blue hour) with a generic unbranded private-hire car, the label "Illustrative footage of York", and the real widget receipt. **Never presented as York Cars' fleet or office.**
- **Generations (Version A):**
  | ID | Purpose | Location | Who | Camera and mode | Length |
  |---|---|---|---|---|---|
  | v05_A-01 | Walk-and-talk, office to yard, 2 lines, 5 stages | Real York Cars office and yard (photo refs) | W4, plus 1 dispatcher in soft focus (C) | DOC-CAM handheld walking backwards, 24 mm observational block, exposure lifts at the doorway | 20 s |
  | v05_A-02 | Dispatcher's hands on a radio handset and keyboard; monitors defocused | Same | C | DOC-CAM, 50 mm | 6 s |
  | v05_A-03 | Owner opens a car's rear door in the yard, checks the child seat, closes it; suspension settles | Yard, drizzle | W4 | DOC-CAM, 50 mm, three-quarter rear (plates hidden) | 8 s |
  | BR08 | York Station frontage at blue hour | §6 | none | — | (reuse) |
- **Edit:** the receipt (widget crop with the capture date) at 0:02 and again at the end. Context: `Google reviews shown on yorkcars.co.uk, 22 Oct 2026.` The site's "largest fleet" and "Happy Users" claims stay out.

---

### Video 6: Client FAQ. "Was it worth it?" (Organic Fostering)
- **Duration and format:** 25 s, **16:9** (service page) plus a 9:16 cut from a separate 9:16 A-01.
- **Anchor:** **32 plain-English guides** on a site rebuilt in Sept 2026 (61 URLs in the sitemap, lastmod 13 Sep 2026), plus the live allowance calculator and postcode check. **No traffic or enquiry claim** (no GSC supplied; Hulk's "+58% / −70%" has no source and is banned).
- **Gate:** who built the Sept 2026 rebuild (Hulk's portfolio lists the GoHighLevel enquiry platform; confirm the site and guides).
- **Concept:** one on-screen question (edit text): "Was it worth it?" The manager answers in a single take: `[their words]`. They may mention the guides and the calculator, but not income figures. If the allowance is mentioned, it must be the **live** £400.72 (ages 0 to 4) with the site's "rates may vary" disclaimer. The superseded £447.60 in the repo's reels must never be used.
- **Safeguarding:** adults only, no children, no case details, no names on screen, no "24/7", no "£2,500".
- **Version A:** W5 Mode B at their real desk in Beaumont House.
- **Version B:** a written answer. The manager writes or approves a two-sentence statement shown as text over BR09 (Chester Road, Old Trafford) and a hands-only shot. No face, no voice.
- **Generations:**
  | ID | Purpose | Location | Who | Camera and mode | Length |
  |---|---|---|---|---|---|
  | v06_A-01 | Answer, medium, 2 lines; mug of tea in hand at the start, set down | Real office (photo refs), window onto the A56 | W5 | DOC-CAM tripod, 50 mm | 14 s |
  | v06_A-02 | Close: final line, small nod | Same | W5 | DOC-CAM, 85 mm | 8 s |
  | v06_B-01 | Hands scrolling a phone with a **green screen**, tea steam in the foreground | Same desk | W5 hands | DOC-CAM, 50 mm, static | 6 s |
  | BR09 | Chester Road, Old Trafford, a tram passing in drizzle | §6 | none | — | (reuse) |
- **Edit:** green screen replaced with a real scroll of `organicfostering/now_mobile_full.png` (the guides list and calculator). Receipt: the sitemap count (a screen recording of the real sitemap with the guide URLs highlighted). Context: `Site structure, not traffic results.` Use OF brand colours only on its own receipt card, never in the footage.

---

### Video 7: "What I learned from SEO". "Four ways to say Kenilworth taxi" (team, Golden Line data)
- **Duration and format:** 20 s, **9:16**.
- **Anchor (the lesson):** in the same 3 months, Golden Line's site averaged:
  - **6.7** for "kenilworth taxis" (row 4, `24,1051,1318,49`)
  - **8.5** for "taxis kenilworth" (row 19, `24,1788,1318,49`)
  - **8.6** for "taxi kenilworth" (row 14, `24,1542,1318,49`)
  - **16.4** for "kenilworth taxi" (row 13, `24,1493,1318,49`)

  The honest takeaway: tiny wording differences behave like separate searches, so you check every variant.
- **Script (T1 drafts and approves):** "Thing I learned this month. One Warwick taxi site, same town, same three months. 'Kenilworth taxis': six point seven. 'Kenilworth taxi', no S: sixteen point four. Same words. Different search. So now I check every version people actually type."
- **Version A:** T1 Mode B selfie walking from their real workplace, own memo.
- **Version B:** T1's real recorded voice over hands typing the four variants into a notes app (green phone screen), no face.
- **Generations:**
  | ID | Purpose | Location | Who | Camera and mode | Length |
  |---|---|---|---|---|---|
  | v07_A-01 | Walking selfie, lines 1 to 3, re-grip once, passes a bus stop (advert unreadable) | Street outside T1's real workplace, drizzle | T1 | PHONE-SELFIE, gentle step bob | 12 s |
  | v07_A-02 | Stopped at a crossing, the last line; the crossing beeps; a small laugh | Same street | T1 | PHONE-SELFIE | 8 s |
  | BR10 | Kenilworth town centre at dusk, generic car passing (cutaway under the numbers) | §6 | none | — | (reuse) |
- **Edit:** the four receipts stack as the numbers are spoken, each row's position cell ringed. Context: `Average positions, Golden Line Taxis Warwick, Search Console, 3 months to 18 Oct 2026.`

---

### Video 8: Screen recording with voiceover. "Position five point three" (Golden Line)
- **Duration and format:** 30 s, **9:16**.
- **Anchor:** **"airport taxi warwick": average position 5.3** (row 20). Supporting: "warwick airport taxi" 6.1 at **13% CTR** (row 6). The user's plan line "just hit position 3" changes to the true value, and "just hit" changes to "is averaging", because there's no earlier period to prove movement.
- **Concept:** a phone-filmed-off-the-laptop look. The real capture is keyed onto a generated green laptop screen with a slight angle, glare and moiré, so it feels like someone filmed their screen to show a mate. The VO is **T1's real recorded voice. No generated voice at all.**
- **Script (T1 approves):** "This is a small taxi firm in Warwick. People searching 'airport taxi Warwick': they're averaging position five point three. Page one. And 'Warwick airport taxi' gets clicked thirteen per cent of the time. That's the search that books a four am run to Birmingham."
- **Version A / B:** the same, faceless by design (T1's hands, real voice). If T1 won't record, any consenting team member's real voice can do it. Fallback: N1's labelled synthetic VO.
- **Generations:**
  | ID | Purpose | Location | Who | Camera and mode | Length |
  |---|---|---|---|---|---|
  | v08_A-01 | Phone filming a laptop, **green screen, four corners visible**; a hand scrolls the trackpad once; a mug edge in the foreground | Agency desk (real), window light | T1 hands | PHONE-REAR, handheld at chest height, autofocus hunts once | 10 s |
  | v08_A-02 | Phone in hand with a green screen, held steady, thumb on the side; rain on the window behind | Same desk | T1 hands | PHONE-REAR over the shoulder | 8 s |
  | BR04, BR05 | Airport kerbside; Warwick Castle Bridge | §6 | — | — | (reuse) |
- **Edit:** the GSC table keyed on with screen glare. Row 20 ringed at "five point three", row 6's CTR ringed at "thirteen per cent". The b-roll lands on "four am run". Context: `Average position, last 3 months to 18 Oct 2026.`

---

### Video 9: Reaction. "Twenty-five" (Leam Taxis)
- **Duration and format:** 15 s, **9:16**.
- **Anchor:** **September 2026: 25 calls**, the best month (tooltip crop `735,278,100,55`).
- **Concept:** an understated re-creation of the owner opening the monthly report (the one T2 sends in video 12) on their phone, between jobs, propped on the dashboard. A quiet reaction: they read it, scroll back, show the phone to nobody, laugh once. Big gasps read fake, and are banned. The edit's opening: a real-looking notification built in the edit, "Your September report", which cuts into the reaction.
- **Line (optional, own words):** `[e.g. a one-word reaction]`.
- **Honesty:** this is a re-creation of a moment the owner confirms happened (or happens monthly), and it is labelled.
- **Version A:** W1 Mode B, phone propped on the dashboard (PHONE-SELFIE, static).
- **Version B:** hands only. Hands hold the phone (green screen) on the steering wheel, the real tooltip is keyed in, and the owner's voice memo reaction plays, or no voice.
- **Generations:**
  | ID | Purpose | Location | Who | Camera and mode | Length |
  |---|---|---|---|---|---|
  | v09_A-01 | Reaction: reads the phone (screen faces away, glow from below), scrolls back, a small laugh, rubs the back of their neck | Parked car on a Leamington terrace street, afternoon drizzle | W1 | PHONE-SELFIE propped on the dash, static, slight auto-exposure breath | 10 s |
  | v09_A-02 | Insert: phone held on the wheel, green screen, thumb scrolls once | Same | W1 hands | PHONE-REAR over the shoulder | 5 s |
- **Edit:** 0 to 1 s the notification (edit-built, neutral, no Google UI); 1 to 9 s the reaction; 9 to 13 s the tooltip receipt keyed into A-02, then full frame; 13 to 15 s "114 calls since May" as the end line. Context: `Business Profile calls. October is a part month.`

---

### Video 10: Meet the team. "Name, job, receipt" (agency)
- **Duration and format:** 30 s per person, **9:16** (social) and **16:9** (service pages), with each ratio generated separately. Start with three clips: T1, T2 and the founder twist (F1). Add more people as they consent.
- **Anchor:** each person ends on **one real number from a client they personally worked on**, chosen with the user:
  - T1: "744 searches" (Golden Line)
  - T2: "114 calls tracked" (Leam Taxis)
  - F1: the founder twist, "every client gets the real numbers, even the October dip"
- **Concept:** a documentary "caught at work" opening. The person is mid-task (headset on, scrolling, writing), notices the camera, turns, and introduces themselves: name, role, what they actually do for a client. The founder twist: the last clip in the set is F1 making the tea for everyone (a P19-style plot twist, kept dry).
- **Script (per person, they approve):** "I'm [name]. I [one plain verb sentence about the job]. Last month that meant [one task]. [The number] is the bit I'm proud of."
- **Never use** the 30 "sample portraits" from googlerankerpro.com.
- **Version A:** Mode B per person.
- **Version B:** a person who won't appear on camera is simply left out. No AI stand-ins for named staff, ever.
- **Generations (per person, ×3):**
  | ID | Purpose | Location | Who | Camera and mode | Length |
  |---|---|---|---|---|---|
  | v10_[P]_A-01 | Caught mid-task, turns to camera, 2 lines | Their real desk | T1 / T2 / F1 | DOC-CAM handheld, 50 mm, one gentle reframe as they turn | 15 s |
  | v10_[P]_B-01 | Working: hands, monitor defocused, orange mug | Same | same | DOC-CAM, 50 mm | 6 s |
  | v10_[P]_B-02 | Detail: their own habit (notebook, headset off, glasses cleaned) | Same | same | DOC-CAM, 85 mm | 5 s |
  F1's twist clip: **v10_F1_A-01** at the office kettle, carrying three mugs, 12 s.
- **Edit:** a lower third with their name and role from the edit, then the receipt crop for their number with its source line.

---

### Video 11: Behind the scenes. "Day one of an audit has no numbers" (Zentro)
- **Duration and format:** 20 s, **9:16**.
- **Anchor:** **13 repair pages: 10 laptop brands and 3 phone brands**, each with its own page (counted on the live site, 22 Oct 2026). Also stated: **no Search Console data yet.** That honesty is the hook: "Every case study starts like this. No numbers. Just a site map."
- **Gates:**
  - Zentro's permission to be named.
  - Whether the agency built or audits it (there's no footer credit).
  - Otherwise: an anonymous "a Manchester repair shop" version, and the receipt shows only the agency's whiteboard.
- **Concept:** fast observational cuts of T1 and T2 mapping the site on a whiteboard (boxes and arrows, no words), marker squeaks, a kettle, the laptop screens green or defocused.
- **Version A:** T1 and T2, Mode B, soft-focus colleagues Mode C.
- **Version B:** hands-only (marker, sticky notes, keyboard), with no faces.
- **Generations:**
  | ID | Purpose | Location | Who | Camera and mode | Length |
  |---|---|---|---|---|---|
  | v11_A-01 | Whiteboard: T2 draws a box tree (no letters), T1 points, a short unintelligible exchange | Real agency room (photo refs) | T1, T2 | PHONE-REAR handheld, a colleague filming | 8 s |
  | v11_A-02 | Over the shoulder at two monitors: one **green**, one defocused | Same | T1 | PHONE-REAR | 6 s |
  | v11_A-03 | Blank sticky notes pressed onto a monitor bezel, one curls off | Same | hands (C) | PHONE-REAR close | 4 s |
- **Edit:** the green monitor gets a real scroll of `zentro/now_desktop_full.png`, then the nav. The receipt counts the brand pages by highlighting the real nav items (not a counter animation). End line: "Ask us again in three months." Context: `No performance data yet.`

---

### Video 12: Day in the life. "Month-end" (team member delivering Leam Taxis' report)
- **Duration and format:** 30 s, **9:16**.
- **Anchor:** **114 calls from the Business Profile, May to Oct**. This is the report T2 builds and sends, and the one W1 opens in video 9, so the two videos link.
- **Gate:** the **UK or Pakistan location is unverified**. The user tells us where T2 really works, and the day is filmed there, with only details true to that place and that person. Time-zone captions only if true.
- **Concept:** a real day in five beats: arrive → pull the export → check the number twice → call the client → log off. Selfie beats bookend phone-rear b-roll.
- **Script (T2 approves):**
  - Opening selfie: "Month-end. One of my taxi clients. Let's see what September did."
  - Closing selfie: "Report's sent. Hundred and fourteen calls since May. He'll ring me in about ten minutes."
- **Version A:** T2 Mode B.
- **Version B:** hands-only beats plus T2's real voice memo as VO, with no face.
- **Generations:**
  | ID | Purpose | Location | Who | Camera and mode | Length |
  |---|---|---|---|---|---|
  | v12_A-01 | Morning selfie, line 1, arriving; door, coat | T2's real street or entrance | T2 | PHONE-SELFIE | 8 s |
  | v12_A-02 | Kettle or tea, laptop lid opens (screen angled away) | T2's real desk | T2 (C wording, hands) | PHONE-REAR | 6 s |
  | v12_A-03 | Over the shoulder, **green laptop screen**, a finger traces a line on the trackpad, a pause, then a re-check | Same | T2 | PHONE-REAR, static on a phone stand | 8 s |
  | v12_A-04 | On a call with a headset, nodding, laughing once; laptop green | Same | T2 | PHONE-REAR | 8 s |
  | v12_A-05 | End-of-day selfie, line 2, lights going off | Same | T2 | PHONE-SELFIE | 8 s |
- **Edit:** time stamps (edit text, only if true); A-03's green screen gets the real Leam GBP crop (`15,165,910,310`) keyed at an angle; the "114" headline (`20,165,240,80`) ringed. End card: "Watch the client open it →" (links to video 9).

---

### Video 13: Founder intro. "Why I show clients the real numbers" (Hassan Pasha)
- **Duration and format:** 55 s, **16:9** (homepage), plus a 30 s 9:16 cut from separately generated 9:16 A-roll.
- **Anchor:** the public record **Hulk Marketing Ltd, company no. 15931335, incorporated 2 September 2024** (Companies House). Then the founder's promise, proven by a 6 s montage of three real receipts: Leam 114 calls, Golden Line 744 searches, the Coventry May-to-Aug chart. The self-declared "since 2012 / 700+ projects" figures are only used if the user wants them, attributed as "Google Ranker Pro group figures".
- **Script beats (F1 approves; draft):**
  1. Who we help: "Taxi firms, repair shops, a fostering agency. Businesses where one phone call matters."
  2. Why I started: `[his real reason, from a 10-minute voice memo interview we transcribe]`.
  3. What clients get: "Every month you get your own Google numbers. The good ones and the dips. A number needs its context."
  4. Close: "If you want to see yours, ring us."
- **Version A:** F1 Mode B, sit-down DOC-CAM interview at his **real** workplace (do not dress a serviced office as a big HQ), plus the b-roll library.
- **Version B:** if he won't appear on camera, the video becomes his voice only over b-roll of his hands and places, still Mode B. **No AI narrator for a founder intro:** a synthetic founder would be misleading.
- **Generations:**
  | ID | Purpose | Location | Who | Camera and mode | Length |
  |---|---|---|---|---|---|
  | v13_A-01 | Interview medium: beat 1 | His real office, window camera-left | F1 | DOC-CAM tripod, 50 mm, eyes to an interviewer off camera-left | 15 s |
  | v13_A-02 | Interview close: beat 2 | Same | F1 | DOC-CAM, 85 mm | 15 s |
  | v13_A-03 | Interview medium: beat 3 | Same | F1 | DOC-CAM, 50 mm | 14 s |
  | v13_A-04 | Close: beat 4, a small nod | Same | F1 | DOC-CAM, 85 mm | 10 s |
  | v13_B-01 | Walking in from the rain, folding an umbrella, at his real building's entrance (signage out of focus) | Real entrance | F1 | DOC-CAM handheld, 24 mm observational | 8 s |
  | v13_B-02 | On the phone to a client by the window, pacing two steps | Office | F1 | DOC-CAM, 50 mm, observational | 8 s |
  | v13_B-03 | At a client's rank or yard, talking with a driver seen from behind (C); a car's boot open | **Only if this visit is real**; a client location with their permission | F1, C | DOC-CAM, 50 mm | 8 s |
  | v13_B-04 | Hands writing in a plain notebook, an orange pen | Office | F1 hands | DOC-CAM, 85 mm | 5 s |
  | v13_B-05 | Over the shoulder at a laptop, **green screen** | Office | F1 | DOC-CAM, 50 mm, static | 6 s |
- **Edit:** the Companies House receipt (a fresh PNG of the company page, dated capture) at 0:03 under "who we are"; B-05's green screen carries the three-receipt montage. Context: `Results shown are individual client data, not typical outcomes. No ranking guarantees.` (the site's own honesty line).

---

### Video 14: SEO tip of the week. Episode 1, "The edge of page one" (founder; Golden Line data)
- **Duration and format:** 30 s, **9:16**, a weekly series. **The same desk, framing and wardrobe every week** (reuse one anchor still), so the series reads as one real ongoing habit.
- **Anchor (Ep 1):** **"taxi warwick": 665 impressions at average position 10.7, 0.9% CTR** (row 5, `24,1100,1318,49`). It's being seen, at the bottom of page one and top of page two.
- **Script (F1 approves; draft):** "Tip of the week. Look for searches with loads of impressions sitting around position ten. One Warwick taxi firm: 'taxi warwick', six hundred and sixty-five impressions, position ten point seven. That's the edge of page one. Don't write a new blog. Fix the page that's already there. Title, local proof, links from your other pages. That's the one we're working on next."
- **Version A:** F1 Mode B.
- **Version B:** T1 presents the tip (a real person). An AI narrator is not used for "from you to camera".
- **Generations (per episode):**
  | ID | Purpose | Location | Who | Camera and mode | Length |
  |---|---|---|---|---|---|
  | v14_E1_A-01 | To camera, lines 1 to 3, phone on a desk tripod | Founder's real desk (fixed series set: window camera-left, orange mug, plant) | F1 | PHONE-SELFIE, static on a tripod, slight auto-exposure breath | 14 s |
  | v14_E1_A-02 | To camera, lines 4 to 6, leans in on "fix the page" | Same | F1 | Same | 12 s |
  | v14_E1_B-01 | Insert: phone held up to the lens with a green screen | Same | F1 hand | PHONE-SELFIE | 5 s |
- **Episode bank (all from real data):**
  - **Ep 2:** "Own your name." Golden Line "golden line taxis warwick" 1.8, 23.3% CTR. Say "top two", not "number one".
  - **Ep 3:** "Publish your prices." York Cars' real airport-fares page, e.g. Leeds Bradford from £55 (live site, 22 Oct 2026). No ranking claim.
  - **Ep 4:** "A page for every model people search." Zentro's per-brand repair pages (with permission).
  - **Ep 5:** "Answer the questions people ask." Organic Fostering's 32 guides (no traffic claim).
  - **Ep 6:** "Click-through beats position." Coventry "coventry airport taxis" 26.3% CTR at 8.2 (row 7).
  - **Ep 7:** "Your Business Profile is a phone line." Leam 114 calls.
- **Edit:** the receipt keyed into B-01's phone, then full frame, with the impressions and position cells ringed. Context: `Average position, Search Console, 3 months to 18 Oct 2026.`

---

### Video 15: Founder commentary on results. "What moved Coventry" (Coventry Airport Taxis 247)
- **Duration and format:** 40 s, **16:9** (case study), plus an optional 9:16 cut.
- **Anchor:**
  - **"coventry airport transfers": average position 6.0, 10.5% CTR** (row 4) and **"coventry airport taxi" 7.0** (row 3).
  - **What drove it, verifiable:** the site's sitemap shows location pages added **6 to 8 June 2026**.
  - **The honest next prize:** "airport transfers coventry", **607 impressions at 22.0** (row 2).
- **Gates:**
  - The user's activity log confirms the agency built those pages.
  - Which brand name to claim (the footer says SMEK).
  - The home-page review widget that shows Slough's reviews is **never shown and should be fixed**.
- **Script (F1 approves; draft):**
  - "Coventry Airport Taxis. In June we built a proper page for every place they actually pick up from."
  - "Three months on, 'Coventry airport transfers' averages position six. And one in ten people who see it, click."
  - "But here's the honest bit: 'airport transfers Coventry', the same words in a different order, is at twenty-two. Six hundred people saw it. Hardly anyone got that far down. That's next."
- **Version A:** F1 Mode B at a monitor (green), pointing.
- **Version B:** N1 (labelled AI narrator) delivers the same third-person analysis with "the agency", never "we", plus the AI presenter label.
- **Generations:**
  | ID | Purpose | Location | Who | Camera and mode | Length |
  |---|---|---|---|---|---|
  | v15_A-01 | Standing at a wall monitor (**green, four corners**), pointing to the upper third, line 1 | Founder's real office | F1 | DOC-CAM handheld, 50 mm, three-quarter angle | 14 s |
  | v15_A-02 | Close, turning from the monitor to the interviewer: line 2 | Same | F1 | DOC-CAM, 85 mm | 12 s |
  | v15_A-03 | Close: line 3, a slight wince-smile on "that's next" | Same | F1 | DOC-CAM, 85 mm | 12 s |
  | BR07 | Coventry ring road at blue hour | §6 | none | — | (reuse) |
  | BR03 | Motorway pre-dawn towards the airport (signs unreadable) | §6 | none | — | (reuse) |
- **Edit:**
  - The monitor gets `coventryairporttaxis247_gsc_3m_chart.png` (cards and chart `0,121,1300,355`).
  - Then full-frame receipts: row 4, row 3, then row 2 with "22.0" ringed.
  - The sitemap lastmod lines are shown as a real screen capture of `/page-sitemap.xml` with the June dates highlighted.
  - Context: `Average positions, last 3 months to 18 Oct 2026. No earlier period to compare yet.` The position line visibly sits higher from mid-September, but we **don't** state it as a number.

---

## 6. Shared b-roll bank (generate once, reuse)

All are no-face or Mode C, generic, unbranded, with plates hidden, and **never presented as a specific client's car, driver or premises**. Each uses the World Bible blocks verbatim.

| ID | Shot | Mode | Length | Used in |
|---|---|---|---|---|
| BR01 | Pre-dawn: a phone vibrating in a dashboard cradle (screen faces away, glow on the roof lining), wiper parked mid-glass, rain, a hand takes it | PHONE-REAR, static | 8 s | 1 |
| BR02 | A wheelie case lifted into the boot of a silver hybrid saloon under a cold LED street lamp, terraced street, wet kerb; the suspension dips; plates hidden by the open boot lid | DOC-CAM, 50 mm, three-quarter rear | 8 s | 1, 3 |
| BR03 | Through the windscreen on a dark motorway before dawn: rain, wipers, red tail-lights, gantry signs too far to read | PHONE-REAR on the dash | 10 s | 1, 15 |
| BR04 | Airport drop-off kerbside (no logos): a passenger's hand takes a case handle from a driver's hand, a door thunk, a trolley rattle | DOC-CAM, 50 mm | 8 s | 2, 3, 8 |
| BR05 | Warwick, the river side of Castle Bridge at morning: a generic grey saloon crosses, the castle soft behind, leaves on the pavement | DOC-CAM, 24 mm observational | 8 s | 2, 8 |
| BR06 | Leamington Spa, The Parade at first light: cream stucco, wet road, one private-hire people carrier passes | DOC-CAM, 24 mm | 8 s | 1 |
| BR07 | Coventry ring road slip road at blue hour: generic saloons, light rain, a cathedral spire far and soft | DOC-CAM, 24 mm, tripod | 6 s | 4, 15 |
| BR08 | York Station frontage and rank at blue hour, generic cars, people with cases (C, small) | DOC-CAM, 24 mm | 6 s | 5 |
| BR09 | Chester Road, Old Trafford, drizzle: a tram passes in the background, people with umbrellas (C) | DOC-CAM, 24 mm | 6 s | 6 |
| BR10 | Kenilworth town centre at dusk, a generic car passes, shop signs out of focus | PHONE-REAR | 6 s | 7 |
| BR11 | York Minster west front at blue hour from Duncombe Place, a generic private-hire car passes | DOC-CAM, 24 mm | 6 s | 5 (Version B) |

**Vehicle realism lock** (paste into every BR prompt with a car): `The car has real weight: suspension settles after it stops, tyres flex on the kerb, road grime along the sills, rain beads on the bonnet, reflections of the grey sky distort across the panels.` Plus the taxi wording from `production_rules.md` §F.

**Landmark honesty:** real landmarks are generated as generic views with no readable signage. They are allowed as "place" establishing shots, not as evidence of anything.

---

## 7. Production order and totals

**Totals (Version A):**
- About **71 Seedance generations**: 60 video-specific (A-roll, inserts and the three-person team set) plus 11 shared b-roll. Episodes after Ep 1 of video 14 add 3 each.
- **About 10 character sheets / Soul IDs:** W1 to W5, F1, (F2), T1, T2, and N1 (fallback only).
- About 20 anchor stills: one per set-up.

**Order (cheapest risk first):**
1. **Week 0, paperwork and evidence.**
   - Consent forms; 27-photo sets and voice memos (A.2, A.3).
   - Confirm GBP ownership (Leam, Coventry).
   - Credits: Coventry (SMEK), York (Xoom), Organic Fostering rebuild, Zentro.
   - The Ali / operator-group question; T2's location; the founder's activity log for 15.
   - **A Search Console "Compare: previous 3 months" export for Golden Line and Coventry.** This is the single biggest upgrade available: it would let us show real growth honestly.
   - A dated Leam Taxis query report if the "no.1" story is wanted.
   - We capture the York review widget, the Companies House page and the Coventry sitemap as dated PNGs (Playwright script `grp_shot.js` in the scratchpad).
2. **Shared b-roll bank** (no identities needed). This QCs the World Bible early: if BR02 looks like a game asset, fix the blocks before any person is generated.
3. **Agency people** (F1, T1, T2): we control them, so they're the fastest consent. Videos 7, 8, 10 to 15.
4. **Client witnesses** as consent arrives: 1, 9 (Leam); 2 (Golden Line); 3 (Coventry); 5 (York); 6 (Organic Fostering). Video 4 needs no witness.
5. **Batch by set-up** (all shots of one location and person in one session, exact text loaded), and QC every clip at full resolution before the next (`production_rules.md` §10).

**Hand-back naming:** `grp_v[NN]_[setup]-[shot]_t[take]_[ratio].mp4`, e.g. `grp_v02_A-02_t1_16x9.mp4`.

---

## 8. Two worked prompts (to show the standard)

### 8.1 v02_A-02: owner reads his numbers (Seedance 2.5; UI: reference mode, 16:9, 1080p, 12 s, audio on; Era 2020s, Physics realistic, Tone calm, Lens 85 mm)

```
ASSET MAP
@Image 1: identity of the taxi firm owner (face, hair, build, wardrobe). 100% matches the reference.
@Image 2: same person, three-quarter view; identity only.
@Image 3: anchor still for this shot: framing, light direction, wardrobe and room layout in frame one; do not copy any screen content or text.
@Image 4: geography and materials of the dispatch office only; do not copy its camera angle; ignore any signs or printed text in it.
@Audio 1: the owner's own voice for the line at second 1 only; ignore its background noise.

SCENE CONTEXT
The owner of a small Warwick taxi firm sits at his own dispatch desk reading a laptop that an agency colleague has just turned towards him, and says one quiet line about what he sees.

LOCATION MAP
Camera at seated eye height, 3 metres away across the desk, facing the owner and the back wall. Foreground: the back of a laptop lid, out of focus, lower left of frame. Midground: the owner behind the desk. Background: a cork board with every paper turned to the wall, a coat on a hook, a radiator with chipped paint under a window. Window light from camera-left. A two-way radio handset on its charger by his right elbow, a mug with a tea ring on the desk.

FIRST FRAME AND SPATIAL BLOCKING
The first visible frame already contains the owner in position: seated centre-right, forearms on the desk edge, torso turned slightly towards the laptop at camera-left, eyes down on the screen. Right hand near the mouse, left hand loose on the desk.

FORMAT MODE
SINGLE CONTINUOUS TAKE.

OPTICS
29° diagonal field of view, short telephoto portrait lens character, camera 3 to 4 metres from the subject, face sharp, background compressed and softly out of focus, close framing through lens reach, not proximity.

CAMERA
Locked-off on a tripod with the faint micro-movement of a real head. Focus stays on the eyes; one small natural focus correction when he sits back.

TIMELINE
0-1s: Ambience only. He reads the screen and takes a small breath in. End state: lips parted, about to speak.
1-6s: At second 1, @Image 1 the owner says, in natural British English, "[APPROVED LINE, numbers written as words]", quietly, half to himself, unhurried. He taps the desk once with two fingers. End state: he glances up past camera-left at the colleague.
6-10s: He sits back, rubs his jaw with his left hand, gives a short nod and a small involuntary half-smile; lips still. End state: leaning back, eyes back on the screen.
10-12s: He holds, breathing; ambience only.

PHYSICS
The office chair takes his weight and creaks as he sits back; his sleeve drags slightly on the desk; the mug stays where it is.

LIGHTING
Soft overcast daylight from a large window camera-left is the only key; the right side of his face falls a stop darker with soft shadow under the cheekbone; the overhead office lights are on but weak, adding a faint cooler top light; the window itself is slightly overexposed. The laptop screen faces away from camera and gives off almost no light.
Natural skin from the references, visible pores and fine texture, unretouched.

AUDIO
Ambience: small office room tone, a radiator ticking, distant traffic on a wet road.
Foley: two-finger tap on the desk at 4s; chair creak at 6s; a short hiss from the radio handset with no intelligible words at 8s.
Dialogue: only the quoted line, spoken by the owner at second 1, in natural British English; lips still when not speaking; no other voices.
Clean close dialogue as if from a clip-on microphone, natural room tone underneath, no echo.
No background music. No subtitles. At least 1 second of ambience only before the first word and after the last word.

FINAL FRAME
The owner leaning back, looking at the screen, half-smile fading, camera holding.

POSITIVE CONSTRAINTS
Muted autumn palette as it really looks: wet slate greys, overcast white sky, black tarmac, red-brick and cream stucco, cold white LED and older amber street light; people in navy, grey and mid-blue everyday clothes.
No on-screen text, captions or subtitles. All signs, labels, mugs, clothing, papers and screens are plain or turned away, with no readable words, logos or numbers. Number plates are not readable.
No extra people.
Filmed on a handheld documentary video camera in available light: natural colour with a restrained grade, fine even digital grain, soft highlight roll-off on bright windows, real depth of field with a gently soft background.
```

### 8.2 BR02: suitcase into a boot (no identity; UI: 16:9, 1080p, 8 s, audio on; Lens 50 mm)

```
SCENE CONTEXT
Before dawn on a wet terraced street, a private-hire driver lifts a passenger's wheelie case into the boot of a silver hybrid saloon.

LOCATION MAP
Camera at standing height on the pavement, 3 metres behind and to the right of the car's rear corner, facing up the street. Foreground: a wet kerb with fallen leaves. Midground: the open boot, lid up, hiding the rear number plate. Background: red-brick terraced houses with dark windows and no house numbers in frame, one cold white LED street lamp and one older amber lamp further down.

FIRST FRAME AND SPATIAL BLOCKING
The first visible frame already contains the driver at the open boot, seen from behind and the side, case handle in his right hand, case resting on the kerb; his face is turned away from camera.

FORMAT MODE
SINGLE CONTINUOUS TAKE.

OPTICS
47° diagonal field of view, standard normal lens character, camera 2 to 3 metres from the subject, natural human-eye perspective, zero obvious distortion, background readable but softly out of focus.

CAMERA
Handheld on the operator's shoulder: subtle breathing rhythm, small weight shifts, gentle human reframes when the driver bends; never gimbal-smooth, never shaky.

TIMELINE
0-1s: Ambience only. The driver grips the case handle. End state: knees bending.
1-4s: He lifts the case with both hands into the boot; the car's rear dips under the weight and settles. End state: case inside, his hands on the boot lid.
4-7s: He brings the lid down; it shuts with a solid thunk; the reflection of the street lamp slides across the wet paintwork. End state: boot shut, plate area dark and out of focus.
7-8s: He steps towards the driver's door, out of frame left; ambience only.

PHYSICS
The case has real weight: his shoulders take the strain and the wheels drag on the kerb edge. The car has real weight: suspension dips as the case lands and settles, tyres flex on the kerb, road grime along the sills, rain beads on the bonnet, reflections of the sky distort across the panels.

LIGHTING
Cold white LED street light from above camera-right is the key; a faint amber lamp further down the street adds warm spill on the wet road; the inside of the boot is lit by its own small courtesy light; deep soft shadow under the boot lid.
Real skin texture with visible pores and fine hairs on the back of his hands; a plaster on one knuckle.

AUDIO
Ambience: quiet residential street before dawn, light rain on car roofs, a distant main road.
Foley: case wheels scrape on the kerb at 1s; the case thumps into the boot at 3s; the boot shuts at 6s; footsteps on wet pavement at 7s.
No dialogue. No background music. No subtitles.
Clean close sound as if from a camera-mounted microphone, natural street ambience underneath.

FINAL FRAME
The closed boot of the silver saloon, rain on the lid, driver gone from frame, camera holding.

POSITIVE CONSTRAINTS
[Palette line verbatim.]
A plain silver saloon with no livery, no door lettering, no roof sign text, no decals. [Text lock verbatim.] Exactly one person visible.
Filmed on a handheld documentary video camera in available light: natural colour with a restrained grade, fine even digital grain, soft highlight roll-off on bright windows, real depth of field with a gently soft background.
```

---

## 9. Open questions for the user (blocking items marked ●)

1. ● **Consent and assets:** the owners of Leam Taxis, Golden Line, Coventry Airport Taxis 247 and York Cars, the Organic Fostering manager, the founder(s) and two team members: names, written consent, 27 photos and voice memos each.
2. ● **Which business owns each Business Profile screenshot** (Leamington calls; Coventry interactions)? Neither shows the name. Also send the Coventry **Calls** breakdown.
3. ● **Agency credit:** Coventry's footer says SMEK, York's says Xoom Media, and Organic Fostering's and Zentro's sites show no credit. Which brand do we claim, and may we name each client?
4. ● **Video 15's activity log:** did the agency build Coventry's June 2026 location pages?
5. **Search Console "Compare" exports** (previous 3 months, or the 16-month view) for Golden Line and Coventry. With these we could honestly say "up from…". Without them we never say growth.
6. **"No.1" proof** for Leam Taxis and York Cars: a dated query report or search recording naming the keyword. Until then neither appears.
7. Are Leam, Golden Line and Coventry one operator group, and is "Ali" one person? (It changes the cast from three witnesses to one.)
8. Where does T2 really work (UK or Pakistan), and which team members agree to appear?
9. Brand on screen: Google Ranker Pro, Hulk Marketing, or a joint lockup, per placement.
10. Old-site captures from the user's own connection (the Wayback steps are in `wayback_before.md`). They are optional, because this concept's before-and-after is data-led.

**Flag for the user (not this concept's job, but found on the way):**
- Coventry's home-page review widget shows another business's reviews (Global Cars 247, Slough, 4.9/202).
- Golden Line's quotes appear under different names on different pages.
- Golden Line's sitemap has test pages in it.
- Organic Fostering's delivered reels 2 and anim4 show superseded allowance figures (£447.60; live is £400.72).
- Fix all of these before any of these sites appears on camera.
