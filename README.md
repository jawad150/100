# IC London — "Three CV Mistakes" (version 2, sample-inspired)

A 30 s vertical reel that takes ideas from the client's sample edit and makes them its own. It is a cinematic, footage-led cut of IC London's website photography with slow pushes and a cool filmic grade. Other elements:
- Heavy condensed (Anton) captions in the lower left, with a spaced-caps line and a red accent.
- A "MISTAKE 0X" label beside a CV-strength meter whose bars fill as each mistake is fixed.
- UI cards fixing each mistake on top of the shot.
- Blind-strip transitions, vertical side labels and a red staircase line.
- A cream panel CTA "Make your next application count." and a logo badge end card.

The voiceover is the brief's script, with a calm, natural read and a gentle fade-out.

**Final:** [`reel/ic_london/ic_london_cv_mistakes_v2.mp4`](reel/ic_london/ic_london_cv_mistakes_v2.mp4) · [`…_share.mp4`](reel/ic_london/ic_london_cv_mistakes_v2_share.mp4). Pipeline: `pipeline_cv2/`.

---

# IC London — "Three CV Mistakes That Could Cost You an Interview"

A 30 s vertical reel (1080×1920, 30 fps, -15 LUFS). It is deliberately unlike the law reel: a bright, editorial "recruiter's desk" look instead of the dark navy route map. One 3D paper CV is shot from cinematic angles, marked up live with a red marker (circles, strike-throughs, scribbles and handwritten notes), then fixed mistake by mistake under big serif numerals: 01 vague achievements, 02 irrelevant information, 03 poor formatting. It ends with "Make your next application count." It uses Blender props (red marker, magnifier, paperclip), a warm piano-led soundtrack with desk sound effects, and the calm natural voiceover with a gentle fade-out.

**Final:** [`reel/ic_london/ic_london_cv_mistakes.mp4`](reel/ic_london/ic_london_cv_mistakes.mp4) · [`…_share.mp4`](reel/ic_london/ic_london_cv_mistakes_share.mp4)

Sources:
- [National Careers Service, CV sections](https://nationalcareers.service.gov.uk/careers-advice/cv-sections): tailor your CV to the job advert, a clear font at size 11 or bigger, headings and bullet points, and the same style throughout.
- [Prospects, How to write a CV](https://www.prospects.ac.uk/careers-advice/cvs-and-cover-letters/how-to-write-a-cv): evidence instead of generic claims, the rewritten achievement (Prospects' own example), removing irrelevant details (date of birth, photo, generic hobbies), and a maximum of two A4 pages.

The candidate "Alex Morgan" and their CV are fictional.

Pipeline (`pipeline_cv/`):
- `vo_cv.py` generates the voiceover.
- `blender_cv.py` renders the props.
- `reel_cv.py` is the compositor and reuses helpers from `pipeline_ic/reel_ic.py`.
- `audio_cv.py` builds the soundtrack.
- `render_cv.py` renders and encodes.

---

# IC London — "No Law Degree? You May Still Have a Route into Law"

A 30 s vertical reel (1080×1920, 30 fps, -15 LUFS) for IC London (Innovate College London). The concept is a career "route planner". A montage of IC London's own website photography asks "Think you need a law degree to become a solicitor?". The "Law degree required?" toggle flips to "Not necessarily", the planner recalculates, and the camera travels a tilted 3D route map through the SRA's SQE requirements to "Qualified solicitor". It then shows IC London's SQE course and the call to action.

**Final:** [`reel/ic_london/ic_london_no_law_degree.mp4`](reel/ic_london/ic_london_no_law_degree.mp4) · [`…_share.mp4`](reel/ic_london/ic_london_no_law_degree_share.mp4)

Sources for every on-screen fact:
- SRA, [sra.org.uk/become-solicitor/sqe](https://www.sra.org.uk/become-solicitor/sqe/): a degree in any subject or an equivalent level 6 qualification, passing SQE1 and SQE2, two years' full-time-equivalent QWE, and character and suitability.
- SRA, [QWE for candidates](https://www.sra.org.uk/become-solicitor/sqe/qualifying-work-experience-candidates/): up to four organisations, paid or volunteer, before, during or after the SQE.
- IC London, [SQE course page](https://iclondon.co.uk/courses/solicitors-qualifying-examination-sqe-prep/): complete SQE1 and SQE2 coverage, mock exams and practice tests, career guidance and QWE support, and expert solicitor-tutors.

Brand (from iclondon.co.uk): logo navy #00247D and red #CF142B, with the site fonts Inter and Cardo. Pipeline (`pipeline_ic/`):
- `vo_ic.py` generates the voiceover.
- `blender_ic.py` renders the navy/red 3D icons.
- `reel_ic.py` is the compositor.
- `audio_ic.py` builds the soundtrack.
- `render_ic.py` renders and encodes.

---

# Organic Fostering — "Your Year in Fostering"

A 30 s vertical reel (1080×1920, 30 fps, -14 LUFS) built from the "Your Year in Fostering" concept. It borrows the year-in-review story format to picture a foster carer's year, then shows the support behind it, and ends with "Start your story".

**Final:** [`reel/organic_fostering/organic_fostering_year_in_fostering.mp4`](reel/organic_fostering/organic_fostering_year_in_fostering.mp4) · [`…_share.mp4`](reel/organic_fostering/organic_fostering_year_in_fostering_share.mp4)

| Time | Scene |
|---|---|
| 0–3 s | 3D phone: "Your Year in Fostering is ready" notification with a 3D gift, then a tap on Play bursts into the magenta-to-orange gradient. Title: "What if this was your 2027?" |
| 3–16.25 s | Story cards (cube swipes, story progress bar): the first 'goodnight' (rising 3D moon), "Can we have pizza tonight?" (beat-synced waveform, 3D pizza), Bedtime stories (book stack, counter spins to "Lost count"), your team (4 avatars), and a slot-machine roll to "From £447.60 a week*" |
| 16.25–21.6 s | The glowing card that holds longest: "A safe home. Everyday care. A place to belong." with a 3D house, light rays and a heart |
| 21.6–25.5 s | The cards fan out into a grid and shuffle into "Your 2027 story · Not started yet" (3D 2027), with a pulsing "Start your story" button |
| 25.5–30 s | Tap, the card flips to "Enquiry started", then the logo end card with the enquiry, phone, web, Ofsted rating and small print, followed by a gentle fade |

Voiceover: the same calm, natural voice as the Support Update reel (af_heart/bf_emma blend, en-gb), built phrase by phrase with soft tails. The last word ends before the 1.25 s fade.

Pipeline (`pipeline_yf/`):
- `vo_yf.py` generates the voiceover.
- `blender_yf.py` renders the pizza, books, gift and 3D "2027".
- `reel_yf.py` is the compositor and reuses the phone, glass and type helpers from `reel_su.py`.
- `audio_yf.py` builds the 120 BPM pop bed, swipe whooshes, reveal dings and Foley.
- `render_yf.py` renders and encodes.

---

# Organic Fostering — "Support Update Available"

A 30 s vertical reel (1080×1920, 30 fps, -14 LUFS) for foster carers who are already approved elsewhere. It follows the "Support Update Available" concept script, its timing and its 14-panel storyboard, read as a calm, conversational voiceover. The voice is a blend of af_heart and bf_emma with en-gb pronunciation, built phrase by phrase with natural pauses and soft tails, and the reel ends with a gentle 1.3 s fade-out. A phone notification ("Fostering Support: update available") becomes a system check of six support questions. The release notes show it's all included, a chat raises continuity of care, and "Install" turns into "Explore a transfer". The look is night neon: plum, magenta-edged glass, orange buttons, green checks and Poppins.

**Final:** [`reel/organic_fostering/organic_fostering_support_update.mp4`](reel/organic_fostering/organic_fostering_support_update.mp4) · [`…_share.mp4`](reel/organic_fostering/organic_fostering_support_update_share.mp4)

| Time | Scene |
|---|---|
| 0–1 s | Glitch-cut montage from the OF footage: "Already a foster carer?" |
| 1–4.25 s | 3D phone arcs in: lock screen 9:14, buzz, notification drop ("This one's for you."), cursor tap, "Checking your support…" |
| 4.25–10.25 s | System check: one question per beat-pair as glass cards with 3D clay icons and spinners, with the newest one spotlit |
| 10.25–16.5 s | Release notes: loaders turn into green checks on the beat, the Ofsted badge pins in, "All included.", then "Independent agency · Rated Good by Ofsted" |
| 16.5–22.5 s | Night-bedroom shot, then hands-and-seedling shot, with the chat: "But what about the children I look after?" / "We focus on continuity of care for them." and "Thinking of moving? Start with a conversation." |
| 22.5–26.5 s | The Install button flips to "Explore a transfer", then tap, progress and the toast "Conversation requested · No immediate commitment." |
| 26.5–30 s | Leafy ivory end card: logo, "Already fostering? Let's talk.", phone, web and the Ofsted rating |

Pipeline (`pipeline_su/`):
- `vo_su.py` generates the voiceover with Kokoro.
- `blender_su.py` renders the clock, book, group and update-arrow clay icons on top of the `pipeline_ff` toolkit.
- `reel_su.py` is the compositor.
- `audio_su.py` builds the bed, phone buzz and UI SFX, with ducking.
- `render_su.py` renders and encodes.

---

# Organic Fostering — "The Fostering Flow"

A 33 s vertical reel (1080×1920, 30 fps, -14 LUFS) built from the "Fostering Flow" animation concept. It shows becoming a foster carer as an app onboarding flow: five steps and one progress bar, from "Start" to "Approved". The voiceover is the warm British female read from the concept.

The visual style is deliberately different from the earlier glassy OF reels. It uses bold colour-blocked SaaS design: cream cards with thick plum outlines and hard offset shadows, extruded 3D Poppins titles with light sweeps, and one flat brand colour per step. The colours run plum → berry → magenta → orange → peach → cream, so the journey goes from dark to light. 3D clay icons rendered in Blender sit on every step.

**Final:** [`reel/organic_fostering/organic_fostering_fostering_flow.mp4`](reel/organic_fostering/organic_fostering_fostering_flow.mp4) · [`…_share.mp4`](reel/organic_fostering/organic_fostering_fostering_flow_share.mp4)

| Time | Scene |
|---|---|
| 0–4 s | Hook: fast montage from the "Day in the life" footage ("Thinking about fostering?"), then a cursor clicks "Start your fostering journey" |
| 4–6.5 s | The app window opens: 5 steps, 0% |
| 6.5–21.5 s | Steps 1–4: informal chat bubbles; house drop, calendar flips to "Booked" and a pin lands on Manchester; the form fills itself and training cards tick off; the profile card builds with four tags. A persistent stepper fills 20% per tick, each on the beat |
| 21.5–25 s | Panel: the ring fills to 100%, the OF emblem appears with a leaf burst, and an "Approved foster carer" toast slides in with small print about the final decision |
| 25–28 s | Colour-blocked bento of support, including the allowance from £447.60 a week* |
| 28–33 s | CTA: "Start your enquiry" click, logo, phone number, website, Ofsted rating and small print |

Pipeline (`pipeline_ff/`):
- `vo_ff.py` generates the voiceover with Kokoro.
- `blender_ff.py` renders the clay icons and reuses `pipeline_of/blender_of.py`.
- `reel_ff.py` is the compositor.
- `audio_ff.py` builds a 120 BPM bed with SFX and ducking.
- `render_ff.py` renders and encodes.

Rebuild: put Poppins into `workspace_ff/fonts` and `logo_full.png` / `emblem.png` into `workspace_ff/src`. Then link `workspace_of/frames` and the OF leaf/coin assets, and run `python3 pipeline_ff/render_ff.py`.

---

# Bodyrade — three pre-workout reels

Three vertical reels (1080×1920, 30 fps, -14 LUFS sound) in Bodyrade's yellow (#FDCF09) / black brand with the Jost font. The style is SaaS motion graphics with cinematic 3D, including Blender turntables of the three pouches, the 3D chevron and "5in1", and tumbling fruit and ice.

| Reel | Length | Story |
|---|---|---|
| [`bodyrade_fresh.mp4`](reel/bodyrade/bodyrade_fresh.mp4) | 28.5 s | Hook montage "STOP PRE-MIXING." → freshness dashboard (air / moisture / light) → "ONLY MIX IT FRESH." → 4 steps (load, insert, add water, open & shake) → benefits → "LOCKED IN FRESH." |
| [`bodyrade_five.mp4`](reel/bodyrade/bodyrade_five.mp4) | 26.5 s | 3D "5in1" hook "WHAT'S IN ONE SCOOP?" → 10 g gauge → five actives with mg counters filling a stacked serving bar → "9.4g of actives in every 10g scoop." → "5 IN 1 BLEND." |
| [`bodyrade_flavour.mp4`](reel/bodyrade/bodyrade_flavour.mp4) | 25.0 s | Pouch/colour flicker hook "THREE FLAVOURS. WHICH ONE ARE YOU?" → Orange & Mango, Sour Raspberry and Sweet Pear, each in its own colour world with 3D fruit at depth → "PICK YOUR FLAVOUR." |

Pipeline (`pipeline_br/`):
- `prep_br.py` cuts out the pack shots.
- `blender_br.py` renders the 3D assets and reuses `pipeline_of/blender_of.py`.
- `reel_br.py` is the compositor (`REEL=fresh|five|flavour`) and reuses `pipeline/engine.py` plus the SaaS helpers in `pipeline_of/reel_of.py`.
- `audio_br.py` synthesises a 120 BPM F-minor track with SFX locked to each reel.

Rebuild: put pack shots, site images and Jost fonts into `workspace_br/src`, `site` and `fonts`. Then run `prep_br.py` and the Blender assets, and finally `python3 pipeline_br/render_br.py fresh five flavour`.

---

# Organic Fostering — "Day in the life" reel

19-second vertical reel (1080×1920, 30 fps, -14 LUFS sound), cinematic AI footage + SaaS-style motion graphics in the Organic Fostering brand (plum / magenta / orange / green, Nunito).

**Final:** [`reel/organic_fostering/organic_fostering_day_in_the_life.mp4`](reel/organic_fostering/organic_fostering_day_in_the_life.mp4) (master, ~30 Mbps) · [`…_share.mp4`](reel/organic_fostering/organic_fostering_day_in_the_life_share.mp4) (12 Mbps) · [`cover.jpg`](reel/organic_fostering/cover.jpg)

| Time | Scene | What happens |
|---|---|---|
| 0.0–0.8 s | Hook | Flash montage of the whole day with a "A day in the life" pill |
| 0.8–2.7 s | The allowance | 3D £ coin + 3D "£447.60", "Weekly fostering allowance", typed "Where does it go?", coin bursts into four glowing orbs |
| 2.7–5.1 s | Child's bedroom | "Sometimes, / it's not the / big things." (blur-in words, glow, light sweep); live clock chip starts at 7:00 am |
| 5.1–8.4 s | Morning light → shoes → school bag | Each orb flies in and lands as a glass tag: "School shoes ✓", "Books & packed lunch ✓" |
| 8.4–11.0 s | Warm kitchen | "It's breakfast / at the table." + "Breakfast ✓" tag, 3D heart |
| 11.0–14.1 s | Bedroom at night | Clock rolls to 7:30 pm, "A goodnight / at bedtime.", "Someone asking," + chat bubble "How was your day?" |
| 14.1–16.8 s | The message | Plum stage: "Sometimes, ordinary moments / help create / **extraordinary** (3D) / change." over the hands-and-seedling clip |
| 16.8–19.0 s | End card | Logo, three-colour bar, organicfostering.co.uk, small print on the allowance |

Pipeline (`pipeline_of/`): Higgsfield keyframes (`gpt_image_2_5`) animated with `seedance_2_5` at 1080p; `blender_of.py` renders the 3D brand elements; `reel_of.py` is the compositor timeline (reuses `pipeline/engine.py`); `audio_of.py` synthesises the score and SFX; `render_all.py` renders in parallel and muxes. Rebuild: put clips into `workspace_of/gen/clip1..7.mp4`, extract frames to `workspace_of/frames/cN/`, add fonts (Nunito static instances) and `src/logo_full.png`, run the Blender assets, then `python3 pipeline_of/render_all.py`.

---

# Higgsfield Genjutsu — orange × black SaaS reel

A 30-second vertical reel (1080×1920, 30 fps, with sound design). It shows a Higgsfield Genjutsu motion-transfer result and walks through how it was made, in a cinematic orange-and-black SaaS motion-graphics style.

**Latest (v3, SFX only, no voiceover):** [`reel/higgsfield_genjutsu_reel_v3.mp4`](reel/higgsfield_genjutsu_reel_v3.mp4)

**v2 (with voiceover, 32 s, voiceover + SFX, profile ending):** [`reel/higgsfield_genjutsu_reel_v2.mp4`](reel/higgsfield_genjutsu_reel_v2.mp4)

**v1:** [`reel/higgsfield_genjutsu_reel.mp4`](reel/higgsfield_genjutsu_reel.mp4) (10 Mbps master) · [`reel/higgsfield_genjutsu_reel_share.mp4`](reel/higgsfield_genjutsu_reel_share.mp4) (7 Mbps, under 30 MB) · cover frame [`reel/cover.jpg`](reel/cover.jpg)

## Storyboard

| Time | Scene | What happens |
|---|---|---|
| 0.0–6.9 s | **Hook: the result** | The split-screen result (ORIGINAL on top, GENJUTSU below) flies in on 3D-tilted glass cards, cutting from the close-up face swap to the crowd chaos with a whip-pan. Headline "I PUT MYSELF INTO A MOVIE" with a CTA pill "WATCH FULL VIDEO FOR THE GUIDE". |
| 6.9–8.6 s | **"HERE'S HOW"** | Letter slams with camera shake, light rays, a perspective grid floor, and orange/black 3D blob mascots popping in. |
| 8.6–21.6 s | **4 steps (screen recording)** | Floating 3D browser window with zooms that follow the action, 3D cursor clicks with ripples, and a step progress bar: **01** Open Genjutsu · **02** Pick a motion video → Recreate · **03** Add your character · **04** 1080p → Generate. |
| 16.2–18.0 s | **Character-sheet clone** | The character sheet flies out of the upload slot, splits into 9 clone cards that fan out in 3D, then all fly back into the upload tile. |
| 21.6–24.2 s | **Payoff** | Generate shockwave and flash, then the Genjutsu output in a big 4:5 card with the original shown picture-in-picture. "ONE CHARACTER. ANY SCENE." |
| 24.2–26.0 s | **Clone wall** | Camera pulls back through a tilted wall of clones (character-sheet angles and Genjutsu frames). "CLONE YOURSELF INTO ANY VIDEO". |
| 26.0–30.0 s | **Outro** | 3D extruded Higgsfield logo rotates in, surrounded by blob mascots; "WATCH THE FULL VIDEO FOR THE COMPLETE GUIDE". |

## How it's built

Everything is rendered from code; no editor project is involved.

- `pipeline/blender_assets.py` renders the 3D elements with Blender (the `bpy` module, Cycles). These are glossy orange/black blob mascots, a torus, capsule, cube, chrome sphere, 3D cursor, 3D arrow, and the extruded Higgsfield logo, which is traced from `logo.png`. They come out as transparent PNG sequences.
- `pipeline/engine.py` is a small 2.5D compositor built on numpy and OpenCV. It does:
  - perspective 3D planes and rounded glass cards with glow and shadow
  - kinetic type, pills, light streaks and particles
  - bloom, grain, vignette and chromatic aberration
- `pipeline/reel.py` holds the timeline and scenes. Motion blur is real: each frame averages 6 sub-frame renders across a 0.55 shutter.
- `pipeline/audio.py` generates the soundtrack: the score (pulse, bass, pad, arpeggio), whooshes, impacts, risers, UI clicks and blob pops. The original scene audio sits underneath at low level.
- `pipeline/render_all.py` renders in parallel chunks, then concatenates them, muxes the audio and does the final H.264 encode.

## Rebuild

```bash
pip install bpy numpy "opencv-python-headless==4.10.0.84" pillow scipy imageio-ffmpeg
# put screenrec.mp4, result_split.mp4, charsheet.png, logo.png into workspace/src/
python3 pipeline/prep_sources.py          # fonts, logo vectorization, frame extraction
python3 pipeline/blender_assets.py blob_drop blob_bear blob_flower blob_cube torus rcube capsule sphere cursor3d arrow3d logo3d
python3 pipeline/render_all.py            # -> workspace/out/higgsfield_genjutsu_reel.mp4
```

To preview single frames, run `python3 pipeline/reel.py still 1.8,12.9,22.8`. Set `REEL_WORKDIR` to use a different workspace folder.
