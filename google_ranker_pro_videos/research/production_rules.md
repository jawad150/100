# Production rules: real-life footage on Higgsfield (Seedance 2.5)

Rulebook for every prompt writer on the Google Ranker Pro / Hulk Marketing 15-video plan. Written 22 Oct 2026.

**What we are making.** The user generates **raw footage only** on Higgsfield: Nano Banana Pro or Soul for stills and character sheets, Seedance 2.5 for video. We do the whole edit: real Search Console and Business Profile overlays, before-and-after comparisons, titles, captions, music and the mix.

**The user's brief, in their words:** "it must not feel like ai, cgi or plastic effect or 3d game render it must look like a real life shot, videos."

**Sources ranked.** Where sources disagree, the user's own skills win: `cinedance-higgsfield`, `human-realism`, `production-consistency`, which supersedes `higgsfield-production`, and `cinematic-director`. Higgsfield's own documentation comes next, then third-party blogs. Every conflict is listed in section 12.

---

## 0. The ten rules (read these if you read nothing else)

1. **Realism comes from light, texture, behaviour and physics, never from adjectives.** Strip every hype token (section D.6). Name one real light source, one capture device, one imperfection and the physics. Paste the texture line verbatim.
2. **Pick one capture mode per video** (section D.1): PHONE-REAR, PHONE-SELFIE or DOC-CAM. Never mix two modes inside one generation.
3. **Real people are Mode B.** The face comes from their own photos, used with written permission. The words come from a script they approved. The voice comes from their own voice memo. Never write face prose for a real person.
4. **Never invent a face for a real, named client.** A generated face attached to a real name or a real quote is a fabricated testimonial. That is banned under the DMCC Act 2024 and the CAP Code. If no real person is available, the fallback is a clearly labelled AI presenter narrating the real case study.
5. **No text in any generation:** no captions, subtitles, logos, readable signs, readable number plates or invented liveries. We add all text in the edit.
6. **Screens never show content.** A screen is angled away, defocused, or filled with flat uniform green for replacement. The real data goes in during the edit.
7. **Audio:** British English. Only approved lines are spoken. No background music. Ambience and foley are welcome. Leave at least 1 s of ambience-only handle at the head and the tail.
8. **Resolution is set to 1080p in the UI on every generation.** Words in the prompt do not change resolution. Set the aspect ratio in the UI as well.
9. **Stills first, then video.** Make an anchor still per scene, QC it, then animate. Use one camera move per stage, with every timeline stage in whole seconds and ending in a visible end state.
10. **QC every clip at full resolution before the next one.** Log PASS or FAIL with the reason, and never retry silently (section 10).

---

## A. The pipeline

```
1 CONSENT        written permission (likeness, voice, words, platforms, term)  ──┐
2 CAPTURE        24 to 30 phone photos + voice memo per person (A.2, A.3)          │
3 IDENTITY       Soul ID training (20+ photos)  and/or  character sheet on         │ per person, once
                 Nano Banana Pro from 3 to 6 best photos (section B)               │
4 WORLD BIBLE    capture mode, light logic, texture line, wardrobe line,         ──┘
                 location block, Forbidden list (per video, section D)  
5 ANCHOR STILL   one still per scene: Soul 2.0 (soul_2) or Nano Banana Pro
                 (nano_banana_pro) with the identity refs, at the deliverable
                 aspect ratio, in the capture mode's look. QC it hard.
6 VIDEO          Seedance 2.5, reference mode: @Image identity refs + anchor
                 still + location still, @Audio = the person's own voice memo
                 for their line (real people only). Prompt = section C skeleton.
                 Resolution 1080p, aspect set in UI, duration from the shot list.
7 FIX / GROW     region edit, shot re-generate, extend forward/backward,
                 transition (cinedance edit/extend/transition architectures)
8 HAND BACK      user downloads raw clips (MP4, or MOV where offered) and sends
                 them to us with the shot ID in the file name (section 9)
9 EDIT (us)      real data overlays, titles, captions, music, mix, AI disclosure
```

### A.1 Identity route per person

Stop at the first rule that matches (production-consistency, identity lock decision):

| Situation | Route |
|---|---|
| One real person, many solo shots (founder, a client owner, one team member) | **Soul ID**. Train on 20 to 30 of their photos. Higgsfield's help centre asks for 20+ (up to 80), and the skill says 5 to 20, so 20 to 30 satisfies both. Anchor stills come from `soul_2`. Per Higgsfield's help centre, a Soul ID also appears as an Element for Seedance video. Confirm that in the UI. |
| Two people in one frame, a person plus a real vehicle or premises, or no Soul | **Character sheet on Nano Banana Pro** (`nano_banana_pro`, not `nano_banana_2`, which is the lesser tier) built from their photos (section B). Crop the sheet into single-view images and attach them as @Image references. |
| A clearly labelled AI presenter (honesty fallback only) | **Mode A character sheet** (section B.3): one invented person, approved once, then treated as Mode B for every later prompt. |
| Incidental person (hands on a keyboard, a blurred passer-by) | **Mode C**: two lines only (section D.4). They must never be presented as a named client or as staff. |

Ask before training a Soul. Never train on anyone's photos without their written permission.

### A.2 Photo-capture checklist (send this to the client or team member)

**Before you shoot**
- Sign the consent form first. It covers your likeness, your voice, the approved script, where the videos appear, how long they run, and your right to withdraw. Your face and voice are personal data, so we store them securely and delete them on request.
- Have someone else take the photos. Use the phone's **rear main camera**, wipe the lens, and turn off Portrait mode, beauty mode and filters. Use no flash. Shoot head-and-shoulders photos at **2x zoom from about 1.5 m**, which avoids wide-angle nose stretch. Shoot full-body photos at 1x from about 3 m.
- Use window daylight. Stand facing a window at about 45°, or outdoors in open shade on an overcast day. Avoid direct midday sun, harsh overhead office tubes on their own, ring-light shine and coloured LEDs.
- Stand in front of a plain, uncluttered wall: mid-tone, not white, and not green. Nobody else should be in frame, and there should be no posters or text behind you.
- Look as you will look in the videos: the same hairstyle, beard length and glasses (if you always wear them, wear them in every photo). Use photos taken today, or at least within the last 4 to 5 months. No sunglasses, hats or scarves over the face, no heavy makeup, no edits.
- **Wardrobe:** wear the exact outfit for the shoot, in plain mid-tone colours, with **no logos or printed text**. Avoid fine stripes and small checks, which shimmer on video. Avoid head-to-toe pure white or black, and avoid green, which clashes with screen replacement. If you will wear two outfits across the videos, photograph both.
- Send the original files at full size by AirDrop, Google Drive or email "actual size". Do not send them over WhatsApp, which compresses them.

**The 27 photos**

| # | Framing | Angle and expression |
|---|---|---|
| 1-4 | Head and shoulders, eye level | Front: neutral; soft natural smile; mid-word, as if talking; genuine laugh |
| 5-8 | Head and shoulders | Three-quarter left; three-quarter right; profile left; profile right (all neutral) |
| 9-12 | Head and shoulders | Chin slightly up; chin slightly down; looking off camera left; looking off camera right |
| 13-17 | Waist up | Front; three-quarter left; three-quarter right; seated as you would be filmed (desk or chair); talking with hands, mid-gesture |
| 18-20 | Full body, head to feet | Front; back; three-quarter |
| 21-22 | Hands | Both hands, backs and palms; holding your phone naturally |
| 23 | Wardrobe detail | Collar, fabric and buttons, close up |
| 24-26 | **Front-camera selfies** at arm's length | Neutral; talking; smiling. These are only needed if you appear in selfie-style clips (videos 3, 7, 9, 12 and 14). A selfie camera changes face proportions, and the generated selfie footage must match how you really look on a front camera |
| 27 | In your own setting | Where you will be "filmed": your desk, your shop, beside your car |

Expressions should be natural, not posed grins. One clean photo beats three blurry ones, because a small set of clean, varied photos outperforms a large inconsistent one.

**Premises and vehicles (videos 5, 11 and 12, plus taxi B-roll):** take 6 to 10 wide photos of the real space from the corners, at standing eye height, in daylight with the lights as normal. Add 2 or 3 photos of any vehicle in its **real livery** from the front three-quarter, side and rear three-quarter. Only these photos may put a real livery or real premises on screen (section F).

### A.3 Voice memo checklist (real people who speak)

- Record **each approved line separately**. Make three takes per line and keep each line to 5 to 8 seconds when spoken. Write numbers as words in the script ("one thousand clicks", not "1,000"). Expand abbreviations ("S-E-O" or "search", decided once and kept).
- Record in a quiet room with soft furnishings (a bedroom or a lounge, not a kitchen or a stairwell). Hold the phone about 30 cm from the mouth, slightly off-axis to avoid pops. Use no music, no TV and no echo.
- Use the Voice Memos app on its uncompressed or lossless setting where available, or any 44.1 or 48 kHz recorder. Use mono and one voice. Aim for peaks around -6 to -3 dBFS. If any take clips, re-record it, because clipping cannot be repaired.
- Speak with real energy, the way you would on the phone to a customer, not as if reading.
- We trim each take to the line plus about 0.3 s, and keep every audio reference **under 30 s in total per generation**.
- **Be honest about what this does.** Seedance treats the @Audio reference as guidance for timbre, pace and style. Practitioners report near-verbatim results only in close-up, low-action talking shots, and a regenerated voice elsewhere. If a generated voice does not sound like the person, it fails QC. The fix order is in section G.1.

---

## B. Character sheet prompts (Higgsfield, Nano Banana Pro)

**Model:** `nano_banana_pro` (Nano Banana Pro). **Aspect:** 3:2. **Resolution:** 4k, because this is a hero reference. **Variants:** `count` 4, pick one.

On the Higgsfield MCP, load the `character-sheet` workflow (`get_workflow_instructions`) first. It orchestrates the tools. The wording below is what goes into the prompt.

**Layout (fixed for every person in the set, so the sheets look like one shoot):** a 4 × 3 grid of twelve equal panels with thin plain mid-grey gutters and **no labels or text**.

| Row | Panel 1 | Panel 2 | Panel 3 | Panel 4 |
|---|---|---|---|---|
| 1 Head | Front, neutral | Three-quarter left | Three-quarter right | Left profile |
| 2 Body | Full body front | Full body back | Full body three-quarter | Both hands, backs and palms |
| 3 Detail | Expression: relaxed half-smile | Expression: mid-word, talking | Expression: thinking, eyes off camera | Wardrobe detail: collar and fabric close-up |

Background: seamless neutral mid-grey (#8C8C8C). Light: large soft source overhead and slightly camera-left, with even soft fill, gentle natural shadow under the chin and the nose, and no hard shadows. Lens: 85mm-equivalent framing for the heads and 50mm for the bodies, so the face is not distorted.

**After generation:** crop the sheet into **separate single-view images**: front head, three-quarter left, three-quarter right, full body front and hands. Upload those as the @Image identity references. Seedance can copy a whole grid into frame if it receives one, and one subject per image is the most reliable input (cinedance).

### B.1 Wording rules (human-realism)

- Mode B (a real person, with photos attached): **no face prose at all.** No jawline, skin tone, eye colour, hair or age description. The photos carry the face, and prose fights the conditioning. Use one texture note, the lighting paragraph, the wardrobe line verbatim and the layout.
- Mode A (an invented presenter): the full 13-block spec, the age ladder and precise skin-tone wording. On Nano Banana Pro, **drop** the closing "Ultra-realistic…" hype sentence. Keep the anti-beautification line only until a result comes back glossy, then remove it first.
- Never: 8K, HDR, ultra-realistic, photorealistic, masterpiece, flawless, perfect skin, "no AI look", camera or lens brands, or ISO. Negative-prompt fields are ignored by Nano Banana.

### B.2 Mode B skeleton: from real photos (paste, fill the brackets)

```
Character reference sheet of the person in the attached photos, 100% matching their face, hair, build and proportions. Twelve equal panels in a 4 by 3 grid with thin plain mid-grey gutters and no labels, no text, no numbers. Row one, head and shoulders at eye level: front facing with a neutral expression; three-quarter view turned to their left; three-quarter view turned to their right; left profile. Row two: full body front, head to feet; full body from behind; full body three-quarter view; both hands held up, backs in one and palms in the other. Row three, head and shoulders: a relaxed half-smile; mid-word as if talking, lips slightly parted; thinking, eyes looking just off camera to the left; close-up of the collar and fabric of their clothing. Wearing [WARDROBE LINE VERBATIM, e.g. "a plain navy crew-neck jumper over a white collared shirt, dark grey chinos, brown leather shoes; no logos, no printed text"] in every panel. Visible pores and natural skin texture, unretouched; [ONE IMPERFECTION, e.g. "a few stray hairs at the temple"]. Seamless neutral mid-grey background (#8C8C8C) in every panel. One large soft light overhead and slightly to camera-left with even soft fill, gentle natural shadow under the chin and nose, the same light in every panel. Head panels framed like an 85mm portrait lens, body panels like a 50mm lens, no wide-angle distortion. Fine natural photographic grain.
```

### B.3 Mode A skeleton: invented AI presenter (honesty fallback only)

Use this only when the video is a clearly labelled AI presenter narrating a **real** case study. The presenter is never named as a client, never quotes a client as their own experience, and is labelled on screen in the edit ("AI presenter. Real client data."). The wording below uses the human-realism 13-block order with the grid wrapped around it. Pick the age bracket from the human-realism age ladder.

```
Character reference sheet of one invented woman, twelve equal panels in a 4 by 3 grid with thin plain mid-grey gutters and no labels, no text, no numbers. [Same panel list as Mode B.]
Around [42] years old, an office professional with an easy, practical manner, but clearly someone who spends most of her day on the phone to customers. [IDENTITY: "British Pakistani heritage, warm light-brown skin with mild darker patches across the upper cheeks, dark brown eyes, full dark eyebrows with a few stray hairs."] [HAIR: "Shoulder-length dark brown hair tucked behind one ear, a few flyaways at the crown and baby hairs at the hairline."] [ONE FEATURE: "a small mole below the left eye."] [ONE ACCESSORY: "small plain gold stud earrings."]
Maximum realism (skin AND hair): [AGE-LADDER LIST VERBATIM for 36 to 49: "early lines only when expressive, faint forehead lines, the first crow's feet, faint under-eye hollows, enlarged pores on nose and cheeks, early uneven pigmentation, one or two small dark spots, natural sheen"]. Do not smooth, soften, idealise or beautify her skin, and do not lighten her skin tone. Detailed irises with visible fibre texture, natural moisture, tiny visible vessels in the sclera, authentic catchlights. Individual hair strands, eyebrow hairs and eyelashes sharply visible. Her hair looks genuinely grown from the scalp, never painted or artificially perfect. She carries herself calmly; no obvious makeup.
Wearing [WARDROBE LINE VERBATIM; no logos, no printed text] in every panel. Seamless neutral mid-grey background (#8C8C8C). One large soft light overhead and slightly camera-left with even soft fill, gentle natural shadow under the chin and nose, the same light in every panel. Head panels framed like an 85mm portrait lens, body panels like a 50mm lens. Fine natural photographic grain.
```

Once approved, that sheet **is** the presenter's identity. Every later prompt treats them as Mode B, with no face prose.

---

## C. Seedance 2.5 prompt skeleton (cinedance architecture)

**UI settings, which are not written in the prompt:**
- Model: Seedance 2.5.
- Mode: reference or omni-reference for any shot with people; extend or edit modes for fixes.
- Aspect ratio: 9:16, 16:9 or 3:4.
- **Resolution 1080p.**
- Duration in whole seconds.
- Audio on.

**Higgsfield selectors:**
- Era: 2020s.
- Physics: realistic.
- Emotional tone: calm or warm.
- Genre: leave unset, or "documentary" if it is offered. Never choose a blockbuster or action genre.
- Lens selector: 24mm for phone modes, 50mm or 85mm for DOC-CAM, matched to the OPTICS block.

If a selector is set, the prompt **does not restate or contradict it**.

**Section order matters.** Keep the spine below. Omit any section the UI already controls. Spatial rules come before camera style, and optics come before aesthetics. Write in plain, concrete English and use no scene numbers. Never use "same as before", "previous" or "continues from".

```
ASSET MAP
@Image 1: identity of [PERSON ROLE, e.g. the taxi firm owner] (face, hair, build, [wardrobe line]). 100% matches the reference.
@Image 2: same person, three-quarter view; identity only.
@Image 3: anchor still for this shot: framing, light direction, wardrobe and room layout in frame one; do not copy any screen content or text.
@Image 4: geography and materials of [LOCATION, e.g. the dispatch office] only; do not copy its camera angle; ignore any signs or printed text in it.
@Audio 1: [PERSON]'s own voice for the line at second [N] only; ignore its background noise.
[Real people only for @Audio. Invented presenter: omit @Audio, describe delivery only.]

SCENE CONTEXT
[One or two sentences: who, where, doing what, in this shot only. For clips over 10 s, name the arc: starts with X, turns on Y, ends on Z.]

LOCATION MAP
Camera at [position, height], facing [direction]. Foreground: [object]. Midground: [subject position]. Background: [landmarks, window position]. Window light from [camera-left/right]. [Two or three dressing anchors that stay put: e.g. "a radiator under the window screen-left, a mug with a chipped rim on the desk, a wall calendar turned face to the wall".]

FIRST FRAME AND SPATIAL BLOCKING
The first visible frame already contains [PERSON] in position; no empty establishing frame. [PERSON] sits [exact position: "screen-left third, 1 metre behind the desk edge"], torso facing [X], eyes [on lens | past camera-right toward the interviewer]. [Hands: "left hand resting on the desk, right hand loose".] [Any second subject: exact position, facing, gaze.]

FORMAT MODE
SINGLE CONTINUOUS TAKE. [Or: CONTROLLED MULTI-SHOT SEQUENCE with HARD CUT at second N, each shot defined. Default single take.]

OPTICS
[Paste ONE block from section D.2 for the capture mode.]

CAMERA
[Operator behaviour: height, distance, side, subject size, one move per stage, focus behaviour, handheld quality. Paste the capture-mode camera lines from section D.3.]

TIMELINE
0-1s: [Ambience only. PERSON already in frame, settles, small breath before speaking. End state: lips parted, about to speak.]
1-[N]s: At second 1, [@Image 1 PERSON] says, in natural British English, "[APPROVED LINE, numbers written as words]", [delivery: pace, volume, emotion; never timbre when @Audio is bound]. [One gesture.] End state: [visible state].
[N]-[M]s: [Next beat: one main change per stage; stages of 3 to 10 s.] End state: [...].
[M]-[TOTAL]s: [Last line ends at least 1 s before TOTAL.] [Final second: PERSON holds, small natural movement, ambience only.]

PHYSICS
[Body weight and contact: "weight shifts onto the left elbow on the desk, the chair creaks and settles"; cloth delay; hair delay; anything handled has mass. Vehicles: "suspension dips as the door shuts, tyres press into wet tarmac".]

LIGHTING
[Paste the light-logic line from section D.5: source, direction, where shadows fall, exposure priority, mixed colour temperature, rim line if dark.]
[Paste the skin line: "Natural skin from the references, visible pores and fine texture, unretouched."]

AUDIO
Ambience: [one line for the whole clip, e.g. "small office room tone, a radiator ticking, distant road traffic through the window"].
Foley: [tied to visible causes, with seconds].
Dialogue: only the quoted line(s), spoken by [PERSON] at the stated seconds, in natural British English; lips still when not speaking; no other voices.
[Capture-mode audio line from section D.3.]
No background music. No subtitles. At least 1 second of ambience-only before the first word and after the last word.

FINAL FRAME
[What the last second shows and whether the camera holds: "PERSON looking just past camera-right, half-smile fading, camera holding."]

POSITIVE CONSTRAINTS
[TEXTURE LINE VERBATIM from section D.1.]
[Text lock from section F.] [Screen lock from section E if a screen is in frame.] No extra people. [Any one local failure lock earned by a previous failure, from section D.7.]
```

**Density.** Spend the detail on blocking, gaze, hands, timing, light and physics. Do not decorate. When references carry identity and look, the prompt gets **shorter**.

**Edit, extend and transition prompts** use the cinedance architectures:
- `EDIT TARGET: Edit @Video 1, seconds X-Y only. CHANGE: … PROTECT: identity, face, voice, lip movement, camera, light, sound; everything outside X-Y unchanged.`
- `EXTEND: Extend @Video 1 forward by N seconds… CONTINUITY: [last-frame state]… Do not re-establish the location or restart the action.`

---

## D. The realism kit

### D.1 Capture modes and their texture lines (pick one per video, paste verbatim in every prompt of that video)

| Mode | Use for | TEXTURE LINE (verbatim, last line of the prompt) |
|---|---|---|
| **PHONE-SELFIE** | 3, 7, 9, 12 (to-camera parts), 14 | `Filmed handheld on a smartphone front camera at arm's length: small-sensor look with deep focus, slight edge over-sharpening, faint sensor noise in the shadows, auto exposure and auto white balance as recorded, ungraded colour.` |
| **PHONE-REAR** | 5 (walk-round), 8, 11 (phone BTS), 12 (b-roll), premises and taxi b-roll | `Filmed handheld on a smartphone main camera: small-sensor look with deep focus, slight edge over-sharpening, faint sensor noise in the shadows, auto exposure and auto white balance as recorded, ungraded colour.` |
| **DOC-CAM** | 1, 2, 6, 10, 13, 15 (interviews, observational b-roll) | `Filmed on a handheld documentary video camera in available light: natural colour with a restrained grade, fine even digital grain, soft highlight roll-off on bright windows, real depth of field with a gently soft background.` |

**Grain line.** Grain is already inside each texture line. **Do not add any other grain or film-stock wording.** In particular, avoid 35mm, Kodak or halation, which read as "film look", not as real phone or documentary footage. In finishing, apply one grain value per video (section 9).

### D.2 Optics blocks (degree language, matched to the lens selector)

- **PHONE-SELFIE (selector 24mm):** `About 80° diagonal field of view, phone front-camera perspective, lens 40 to 55 cm from the face at arm's length, slightly above eye level. The face sits close and slightly enlarged at the centre, background visible to the frame edges and mostly in focus, straight lines stay straight, no portrait bokeh.`
- **PHONE-REAR (selector 24mm):** `About 80° diagonal field of view, phone main-camera perspective, held at chest height 1 to 2 metres from the subject. Environment visible to the frame edges, deep edge-to-edge focus, no telephoto compression, no creamy bokeh.`
- **DOC-CAM interview (selector 50mm):** cinedance 47° block: `47° diagonal field of view, standard normal lens character, camera 2 to 3 metres from the subject, natural human-eye perspective, zero obvious distortion, natural face proportions, background readable but softly out of focus.` (The cinedance distance of 3 to 5 m is shortened for interiors.)
- **DOC-CAM close interview (selector 85mm):** cinedance 29° block: `29° diagonal field of view, short telephoto portrait lens character, camera 3 to 4 metres from the subject, face sharp, background compressed and softly out of focus, close framing through lens reach, not proximity.`
- **DOC-CAM observational wide (selector 24mm):** cinedance 84° block, without the "slight low angle".

Never write focal lengths, f-stops, ISO, or camera or lens brands as the main control. Depth of field must agree with the lens. A phone with creamy bokeh reads as fake.

### D.3 Camera and capture-realism lines

Use **3 or 4 per prompt, no more.** Stacking more realism language cancels itself out (production-consistency).

**PHONE-SELFIE (front camera)**
- `The phone is held in the speaker's own outstretched right hand; the frame moves with their arm: slight handheld micro-shake, small drifts as they gesture with the other hand, a natural re-grip once.`
- `Auto exposure breathes slightly when the window behind them comes into frame, then settles.`
- `Their eyes flick between the lens and the screen image of themselves, as people do on a front camera.`
- `Framing is casual and a little off-centre; the top of the head is nearly touching the top of the frame.`
- Audio: `Sound recorded by the phone's built-in microphone at arm's length: close voice with a little room reflection, faint handling noise when the grip shifts.`

**PHONE-REAR (someone else filming, or a walk-round)**
- `Handheld by a person walking slowly: gentle vertical bob with each step, small horizon tilts corrected by hand, no gimbal smoothness.`
- `Autofocus hunts once, briefly, as the subject moves closer, then locks.`
- `A mild lens flare and a slight veil of haze appear when the lens points towards the bright window.`
- `Exposure lifts and drops a little as the camera moves between the bright doorway and the darker room.`
- Audio: `Sound from the phone's microphone: room tone, footsteps, slight wind rumble outdoors; voices further away sound thinner.`

**DOC-CAM (professional documentary operator)**
- `Handheld on the operator's shoulder: subtle breathing rhythm, small weight shifts, gentle human reframes when the subject leans; never gimbal-smooth, never shaky.`
- `Focus stays on the eyes; one small natural focus correction when the subject sits back.`
- `Locked-off on a tripod with the faint micro-movement of a real head` (sit-down interviews only).
- Audio: `Clean close dialogue as if from a clip-on microphone, natural room tone underneath, no echo.`

**Behaviour (all modes):** people do things imperfectly. They blink naturally, glance away to think, restart a gesture, adjust a sleeve, rest an elbow, swallow, take a breath before a line, and finish with a small involuntary smile or nod. Write **gestures, not emotions** ("rubs the back of his neck and half-laughs", never "looks happy"). Never write "standing confidently".

### D.4 Skin, face and hands

- **Mode B (every real person and every approved presenter):** `Natural skin from the references, visible pores and fine texture, unretouched.` Add one imperfection if the shot is a close-up. **Nothing else about the face.**
- **Mode C (incidental hands or blurred background people):** `Real skin texture with visible pores and fine hairs; [one imperfection: a plaster on one knuckle, a slightly chipped nail, a faint ink mark].` Incidental people stay small, soft-focus or partly cropped, and are never identifiable.
- Hands: `hands relaxed with natural knuckle creases and veins; five fingers each, fingers not touching the face during speech`. Keep hands away from the mouth while the person is talking, because hands over the mouth break lip-sync.

### D.5 Light-logic lines (one per scene, verbatim across all shots of that scene)

The rule: one named source, its direction and quality, where the shadows fall, and what exposure protects. UK realism defaults are below.

- **UK office daylight:** `Soft overcast daylight from a large window camera-left is the only key; the right side of the face falls a stop darker with soft shadow under the cheekbone; the overhead office lights are on but weak, adding a faint cooler top light; the window itself is slightly overexposed.`
- **Mixed colour (evening office or home):** `Cool blue-grey daylight from the window camera-right mixed with a warm tungsten desk lamp camera-left; the two colour temperatures meet on the face; background falls into soft darkness with a faint rim from the window on the hair.`
- **Shop or premises interior:** `Light from the open shopfront behind camera plus fluorescent ceiling tubes; flat-ish but real, slight green-cyan cast from the tubes, darker corners at the back of the room.`
- **Outdoor UK overcast:** `Flat overcast sky as a huge soft source from above; soft shadows under the eyes and chin; wet tarmac reflects the grey sky; no direct sun.`
- **Outdoor low sun (golden hour, use sparingly):** `Low late-afternoon sun from behind camera-left, warm on one side of the face, long soft shadows on the pavement; the other side stays cool from the sky.`
- **Phone-screen glow (see section E):** `The phone screen faces away from the camera; its cool white glow lights the face from below, brighter on the chin and under the nose.`
- **Dark sets** always add: `a faint rim of window light separates the head and shoulders from the dark background.`
- **Deep skin tones** add: `exposed correctly for deep brown skin so the highlights show natural sheen and the shadow side keeps detail.`

Never write "cinematic lighting", "studio lighting", "beauty light", "three-point lighting", "perfectly lit" or "ring light". Real places are lit by windows, ceiling fittings, lamps, screens and the sky.

**Imperfection is texture.** Every set gets two or three real-world dressing anchors and one uncomposed element. Examples:
- A coat on the back of a chair.
- Cables under the desk.
- A half-drunk mug of tea.
- A radiator with chipped paint.
- A sticky note on the monitor bezel, kept blank.
- A blind slightly crooked.
- A car-park puddle.
- A passer-by half-cropped at the frame edge.

Perfect surfaces read as a render. Add atmosphere between the camera and the subject: dust in the window light, breath in cold air, rain on glass, steam from a mug.

### D.6 STRIP list: never in any prompt (stills or video)

| Category | Strip |
|---|---|
| Hype tokens | 8K, 4K, HDR, ultra-realistic, photorealistic, hyperrealistic, hyper-detailed, masterpiece, award-winning, stunning, epic, breathtaking, flawless, perfect, pristine, crisp, high quality, best quality, trending |
| Polish cues (pull towards ads and renders) | cinematic, cinematic lighting, film look, polished, professional, high-end, commercial, glossy, studio, beauty shot, editorial, symmetrical, perfectly framed |
| Smooth-camera cues | gimbal, stabilised, steadicam, dolly, slider, crane, drone, smooth tracking (unless a shot truly needs it) |
| Gear metadata | camera bodies and brands (ARRI, RED, Sony FX, Canon, iPhone 15 Pro and so on), lens brands (Cooke, Zeiss, Sigma, Helios, Laowa), ISO, shutter, f-stops as primary control |
| Aesthetic negations | "no AI look", "not CGI", "no plastic skin", "not a render", "realistic not fake". These read as noise and pull towards the failure. The only exception is the earned skin lock in section D.7 |
| Face prose in Mode B | jawline, skin tone, eye colour, hair description, age, "handsome", "beautiful" |
| Stale context | scene numbers, "same as before", "previous", "continues", unused @tags, people not in this shot |
| Resolution words | 4K, 1080p, ultra-HD in the prompt (set them in the UI) |
| Brands and IP | Google (logo or styling), real companies, recognisable songs, any wording that would make the model draw a logo |

### D.7 Failure-fix table (change one thing per retry and log it)

| Symptom | First fix | Then |
|---|---|---|
| **Plastic, waxy or airbrushed skin** | Strip hype and polish tokens. Confirm Mode B (no face prose). Check the source still was not glossy, and regenerate the still if it was | Add the earned skin lock: `natural skin from the references, visible pores and fine texture, no smoothing.` On the still, remove the anti-beautification line, then add a rim light, then cut one accessory, then check the age ladder |
| **Looks like a 3D game render** (even shadowless light, everything sharp, clean surfaces, rigid motion) | Name one real light source with falloff. Add two dressing anchors and one uncomposed element. Add atmosphere | Switch to the DOC-CAM texture line. Add the physics lines. As a last resort add `No game-engine look, no CG gloss.` next to the light line |
| **CGI vehicles** (taxi looks like a game asset) | `The car has real weight: suspension settles after it stops, tyres flex on the kerb, road grime along the sills, rain beads on the bonnet, reflections of the grey sky distort across the panels.` | Use a real vehicle photo as a prop reference. Shorten the shot. Keep the camera static while the car moves |
| **Floaty or weightless motion** | Physics lines: heel contact, weight transfer, cloth and hair delay, what settles afterwards | One action per stage. Shorter duration |
| **Gimbal-smooth camera** | Paste the capture-mode handheld line | Remove any move words. Say "handheld" plus the operator behaviour |
| **Too shaky (cheap fake shake)** | Replace "shaky" with micro-shake plus operator breath | DOC-CAM tripod line |
| **Dead stare, no blinks, frozen face** | Behaviour line: natural blinks, glance away mid-sentence, small nods | Shorter line. The talking stage ends with a micro-reaction |
| **Identity drift over the clip** | Fewer words about the person. Identity @Images first in the asset map. Add a three-quarter view reference | Shorter clip (8 to 15 s). Regenerate the anchor still. Soul instead of the sheet, or the reverse |
| **Mouth mush or late lip-sync** | Medium close-up with the mouth visible, steady camera during speech, one short line of 5 to 8 s, numbers as words | Name the speaker and the start second. Re-record the voice memo cleaner (mono, dry, -6 dBFS peaks) |
| **Voice not like the person** | Use the best take as @Audio, with the shot as a static close-up | See section G.1 |
| **Gibberish text appears** (signs, mugs, laptop stickers, plates) | Text lock (section F). Name the objects as plain ("plain white mug") | Region edit on the text area. Blur in the edit |
| **Screen shows fake UI** | Screen lock (section E): angle away or green fill | Region edit to flat green. Replace in the edit |
| **Music appears** | `No background music.` in AUDIO | Mute it in the edit and rebuild the ambience. The baked track cannot be removed, only muted |
| **Over-saturated or "ad" colour** | Remove colour words. Say `ungraded colour` (phone) or `restrained grade` (DOC-CAM) | Grade in the edit, never with prompt words |
| **Extra people or duplicates** | `No extra people.` and an exact count of visible people | Remove the crowd from the location still |
| **Empty or late first frame** | First-frame occupancy lines | Use the anchor still as the first frame where the UI allows it |

---

## E. Screen handling

Generated screens show gibberish UI and fake numbers. **No readable screen content is ever generated.** All Search Console, Business Profile, report and website visuals are real captures that we composite in the edit.

| Situation | Write this |
|---|---|
| Screen not needed for the story | `The laptop screen is angled away from the camera; only the back of the lid is visible.` |
| Screen visible but unimportant | `The monitor sits out of focus in the background, its picture a soft blur of light with no readable detail.` |
| **We will insert the real screen** (videos 2, 4, 8, 9, 15) | `The [laptop/monitor/phone] screen shows a flat, uniform, matte chroma-green fill from edge to edge, evenly lit, with no interface, no text, no reflections and no glare; all four corners and the bezel stay visible.` Keep the camera **static or very slow**, and keep fingers and hands off the screen area except for one brief tap if the story needs it. Keep the green screen dim, so the face is not lit green: `the screen gives off almost no light`. |
| Reaction lit by a screen (9, 2) | `The screen faces away from the camera; its cool white glow lights the face softly from below; no part of the screen's picture is visible.` |
| Phone in hand, filmed over the shoulder (8) | Green fill as above, phone held steady at chest height, `thumb resting on the side of the phone, not on the screen`. |

Edit notes for us:
- Track the four corners and keep corner pins clean. We add a slight screen-glare pass and grain matching, so the insert sits in the shot.
- Our inserted screens must show **only real data** from `assets/gsc/` or live sites, with dates visible or captioned.

---

## F. No-text rule (and taxis)

**In every prompt with a person, a place or a vehicle**, paste this verbatim in POSITIVE CONSTRAINTS:

```
No on-screen text, captions or subtitles. All signs, labels, mugs, clothing, papers and screens are plain or turned away, with no readable words, logos or numbers. Number plates are not readable.
```

Our rules:
- No captions, subtitles, titles, logos, watermarks or brand marks, and no readable signage, posters, document text or product labels. **Never a Google logo or Google brand colours.** The agency is independent and not affiliated with Google, so implying endorsement is a problem.
- Clothing is plain, with no logos.
- Paper on desks is blank or face down. Wall boards are blank or turned to the wall.
- Shopfront and street signs are out of focus, angled away, or out of frame.
- The edit adds every word on screen.

**Taxis and private-hire cars (Leamington Spa Taxis, York Cars, Golden Line Warwick, Coventry Airport Taxis):**
- **Default:** generic and unbranded. `A plain [black/silver/white] saloon or people carrier with no livery, no door lettering, no roof sign text, no decals.` Do not invent firm names, phone numbers or colour schemes.
- **Plates:** `the front and rear number plates are angled away from the camera, out of focus, or hidden behind a foreground object`. Prefer three-quarter rear angles with shallow focus on the driver or passenger, or plates blocked by a kerb bollard, a passenger or a wheelie case.
- Never readable registration characters. Never council licence-plate numbers. No invented private-hire badges.
- **A real livery appears only** when the user supplies real photos of the firm's car (section A.2). It goes in as an @Image prop reference: `@Image 5: the firm's real car (shape, colour, livery placement); do not alter or redraw any lettering.` Even then, check every letter in QC. If any lettering is warped, prefer plates and lettering kept soft or angled, and composite a real logo in the edit.
- Taxi physics and realism lines: see the CGI-vehicles row in section D.7. Add UK street truth: double yellow lines, wet kerbs, a bus shelter (no readable advert), drizzle on the windscreen, a wiper parked mid-glass.
- **Do not imply facts we have not verified.** That includes fleet size, airport rank access and premises. Any premises shot of a real client uses their real photos. Without photos, use generic b-roll that is not presented as their business.

---

## G. Audio rules

1. **British English**, written into each dialogue line: `in natural British English`. Accent and region come from the person's own voice memo, never from text describing their voice.
2. **Dialogue only from approved scripts.** Quote lines verbatim, with numbers as words. Each line has its speaker's @tag and its start second. `Only the quoted line is spoken. No extra words, no ad-libs, no names unless scripted. Lips are still when not speaking. No off-screen voices.`
3. **One line per talking stage, 5 to 8 s.** Split longer answers across stages or generations. Keep one language per segment.
4. **No background music, ever, in generation.** Write `No background music.` We add licensed music in the edit. Seedance's baked score can only be muted, so prevent it.
5. **No subtitles.** Write `No subtitles.`
6. **Ambience and foley: yes, always.** Write one ambience line for the whole clip and foley tied to visible causes at named seconds. Dead silence reads as artificial, so keep room tone even under speech. Useful examples:
   - Office: keyboard, chair creak, kettle, radiator tick.
   - Taxi office: radio dispatch crackle with **no intelligible words**.
   - Street: tyres on wet road, indicator ticks, a car door thunk.
7. **Edit handles:** **at least 1 s of ambience-only at the head and 1 s at the tail.** The person is already in frame and visibly about to speak. Speech starts at second 1 at the earliest, and the last word ends at least 1 s before the end. This sits alongside the lip-sync advice to avoid long lead-ins: keep the handle at exactly 1 s, and name the start second.
8. **Capture-mode audio line** from section D.3: phone microphone or clip-on microphone character.
9. **@Audio references:** real people only, their own recorded voice, with their consent. Keep each clip 2 to 15 s and under 30 s in total per generation. Write `ignore its background noise`. Never use a voice reference of anyone who has not consented, and never a famous voice.
10. **AI presenter (fallback):** a synthetic voice, labelled in the edit. Give a casting brief only (three adjectives plus one contradiction, age range, British accent region). Never ask for "the voice of [real person]".

### G.1 When the generated voice is not the person's voice

The order of fixes:
1. Regenerate as a static medium close-up with a cleaner memo.
2. Generate with that person's own memo audio laid in as the final track in the edit, with the generated mouth already close to the line because @Audio drove it. Then check sync frame by frame.
3. As a repair only, use a lip-sync pass (Magnific `video_speak`, Lipsync 2.0) to their real memo. Practitioners find it can sound "dubbed", so QC it hard.

**Never ship a voice that the person has not heard and approved.**

---

## H. Durations, splitting, aspect ratios and resolution

### H.1 Per-generation length

Seedance 2.5 does **4 to 30 s** per generation. Thirty seconds is a ceiling, not a target. Production-consistency notes that longer clips multiply drift, and lip-sync guidance favours short lines.

| Shot type | Generate at |
|---|---|
| Talking head with 1 or 2 lines | **8 to 15 s** |
| B-roll (hands, premises, taxis, office) | **5 to 10 s** |
| Walk-and-talk or premises tour, single take, little dialogue | 15 to 30 s, 4 to 7 stages |
| Reaction (video 9) | 8 to 12 s |

### H.2 Splitting 45 to 90 s videos (1, 13, 15 and the longer cuts of 2 and 6)

Build each long video from **A-roll talking segments plus B-roll cutaways**, the way a real documentary is cut. Example for a 75 s testimonial (video 1): 5 talking generations of 10 to 15 s, one or two lines each, plus 4 B-roll generations of 6 to 8 s. The edit hides every join on a cutaway or a change of shot size.

Continuity rules across generations:
- Use the **same identity references in the same order**: the same anchor still per set-up, the same wardrobe line, light-logic line, texture line and location block, all verbatim. One set-up has one light direction and one time of day.
- **Alternate shot sizes** between generations (medium, then close, then medium) so a jump cut reads as a deliberate edit. Keep the camera side (axis) the same.
- **Chain continuous action:** use extend forward from the previous clip, or extract its last frame and use it as the next anchor still. State the carried-over position, gaze, hands and light in the CONTINUITY line. Practitioner reports put a cap of roughly 90 s on extend chains. That is unverified, so plan for less.
- **Batch by scene.** Generate all shots of one set-up in the same session with the exact text loaded.
- Each segment keeps its own 1 s head and tail handles.

### H.3 Aspect ratio and resolution (set in the UI every time)

| Use | Generate at | Deliver |
|---|---|---|
| Social: Reels, TikTok, Shorts (3, 7, 8, 9, 11, 12, 14) | **9:16** | 1080×1920 |
| Homepage hero and case studies (13, 1, 2, 4, 15) | **16:9** | 1920×1080, plus a 9:16 cut-down generated separately if needed |
| Service pages (5, 6, 10) | 16:9 (also 9:16 if posted) | as above |
| 4:5 feed (optional) | **3:4**, which crops to 4:5 with minimal loss. Higgsfield's Seedance 2.5 list (auto, 21:9, 16:9, 4:3, 1:1, 3:4, 9:16) has no 4:5 | 1080×1350 |

- Design for one ratio. A 16:9 composition rarely survives a crop to 9:16. If a video needs both, generate both from ratio-specific anchor stills.
- **Resolution: 1080p, set explicitly on every generation.** Seedance on Higgsfield silently defaults low. If the live UI offers only 480p or 720p for 2.5 (a practitioner catalogue check in August 2026 showed 720p as the maximum), use 720p and tell us. We then upscale once in finishing with one setting for the whole set: Higgsfield `upscale_video` with the `ugc` preset for phone modes and `aigc` for DOC-CAM, or Magnific `magnific_precision` with one `smartGrain` value. Never upscale intermediate stills that will be animated.
- Locked tasks (edit, extend) inherit the source aspect ratio, so do not fight it.

---

## 9. Hand-back and finishing (what the user sends us)

- **File name:** `grp_v[01-15]_[setup]-[shot]_t[take]_[ratio].mp4`, for example `grp_v03_A-02_t2_9x16.mp4`. Download at the generated resolution, in MOV where offered.
- Send the passing takes **and** the near-misses. A near-miss with a good first half is still usable.
- Send the anchor stills and character-sheet crops, so we can match continuity and grain.
- Note the resolution setting used and any selectors set.
- **Finish sheet (us):** one upscale mode, one grain value and one sharpen value per video. Grade in the edit. Social loudness is -14 LUFS. Captions sit inside the 9:16 safe zones (top 12%, bottom 20%).
- **Disclosure (us):** the agency's site already labels AI presenters ("AI-generated presenters and voices. Service explanations, not client testimonials."). Mode B footage of a real client is still synthetic footage, so label it in the edit, for example "AI-recreated with [Name]'s permission. Words and results are theirs." Set the platform AI-content labels (TikTok AIGC, YouTube altered or synthetic content, Meta AI info) for realistic generated people. This is a recommendation; confirm wording with the user and their adviser.

---

## 10. QC before the next generation (production-consistency and cinematic-director screening)

View every clip at **full resolution with sound**, never as a thumbnail.

- [ ] **Realism:** skin has pores, people blink and move imperfectly, light has one direction and real falloff, and the set has wear. Nothing is too clean, too symmetrical or too sharp everywhere.
- [ ] **Not game or CGI:** weight, contact and settle are right. Cars have mass. The camera behaves like a hand, a shoulder or a tripod.
- [ ] **Identity:** the person would recognise themselves. Check against the real photos, not the sheet.
- [ ] **Text and marks:** no readable text, gibberish lettering, logos or plates. No Google marks.
- [ ] **Screens:** angled away, defocused or flat green, with four clean corners if green.
- [ ] **Audio:** only approved words, British English, the right voice, no music, no subtitles, 1 s handles at the head and tail, believable room tone.
- [ ] **Honesty:** no invented face for a real client, no claim that does not trace to `assets/gsc/`, the live site or a cited source, and no implied premises, fleet or results we have not verified.
- [ ] **Spec:** aspect ratio, 1080p (or flagged 720p), duration, first frame occupied, final frame as written.

Log every generation in this format:

```
QC [date] grp_v03_A-02 t2 [seedance_2_5]
Verdict: PASS | FAIL
Checks: realism [ok|x] identity [ok|x] text/screens [ok|x] motion [ok|x] audio [ok|x] honesty [ok|x]
Failure: [symptom] > [broken lock] > [fix applied]
```

---

## 11. Per-video capture plan

The scripts and real-person availability come from the user. Unverified items stay unverified.

| # | Video | Capture mode | Who is on screen | Notes |
|---|---|---|---|---|
| 1 | Testimonial 60-90 s | DOC-CAM, sit-down interview + PHONE-REAR or DOC-CAM b-roll | Mode B client owner (photos, consent, approved words, own voice) | Split per H.2. Without a consenting owner: labelled AI presenter narrating the real case + real data. No client face |
| 2 | Results walkthrough 30-45 s | DOC-CAM over-the-shoulder | Mode B client | Laptop in flat green; we insert real GSC footage |
| 3 | Milestone 15-20 s | PHONE-SELFIE | Mode B client | Their own words, e.g. "first page one" only if true for their site (check gsc_story.md) |
| 4 | Before and after 20-30 s | Mostly our screen composites; generated plates are PHONE-REAR hands-and-laptop with green screen | Mode C hands, or nobody | Old and new sites from real captures only |
| 5 | Premises tour 30 s | PHONE-REAR walk-round | Mode B owner | Real premises photos as the location reference. Generic taxis unless a real livery photo is supplied |
| 6 | Client FAQ 20-30 s | DOC-CAM | Mode B owner | Approved Q&A only |
| 7 | "What I learned" 20 s | PHONE-SELFIE | Mode B client or team member | Casual, one restart allowed if scripted |
| 8 | Screen + voiceover 30 s | PHONE-REAR filming a laptop or phone in flat green | Mode C hands; VO in a real team member's own voice | We insert the real keyword-position capture |
| 9 | Reaction 15 s | PHONE-SELFIE propped on the desk | Mode B client | Screen faces away, glow on the face |
| 10 | Meet the team 30 s | DOC-CAM at the desk | Mode B, one consenting person per clip | Never the 30 sample profiles on googlerankerpro.com |
| 11 | Behind the scenes 20 s | DOC-CAM observational or PHONE-REAR | Mode B team; anyone else soft-focus Mode C | Real office photos only. Do not imply a large fitted HQ |
| 12 | Day in the life 30 s | PHONE-SELFIE + PHONE-REAR b-roll | Mode B one team member | UK or Pakistan location is unverified and must come from the user |
| 13 | Founder intro 45-60 s | DOC-CAM | Mode B founder (Hassan Pasha, with consent) | Split per H.2. Own voice memo |
| 14 | SEO tip 30 s | PHONE-SELFIE or a phone on a desk tripod | Mode B founder | One tip per clip |
| 15 | Founder commentary 30-45 s | DOC-CAM + data inserts | Mode B founder | Only real wins traceable to `assets/gsc/` |

---

## 12. Conflicts found, and how we resolved them

| Topic | Skill says | Web or blog says | Ruling |
|---|---|---|---|
| Nano Banana Pro id | higgsfield-production: `nano_banana_2` | n/a | **production-consistency supersedes it: `nano_banana_pro`.** `nano_banana_2` is the lesser tier |
| Soul ID photo count | production-consistency: 5 to 20 | Higgsfield help centre: 20+, up to 80, recent, one full-body, no sunglasses or hats, no group shots | Shoot 27, train on 20 to 30. This satisfies both |
| Max resolution, 2.5 on Higgsfield | Skills: pass 1080p explicitly | Higgsfield blog: 480p, 720p and 1080p, plus a 4K upscale. A practitioner catalogue check in Aug 2026: 480p and 720p only. fal: 480p and 720p | Always select 1080p. If it is not offered, use 720p, flag it, and upscale once in finishing |
| Start and end frame on 2.5 | production-consistency: `start_image` and `end_image` roles | Aug 2026 catalogue check: no frame pinning on 2.5 (2.0 has it). fal: an end frame on 2.5 | Use a start-frame slot if the UI shows one. Otherwise attach the anchor still as @Image with the job "frame one matches this". For exact loops, use Seedance 2.0 first and last frame (15 s cap) |
| Elements on 2.5 | production-consistency: Elements are for `seedance_2_0`, not 2.5 | Higgsfield help centre: a Soul ID appears as an Element for Seedance | Use plain @Image references, which work either way. Use a Soul Element if the UI offers it |
| Reference limits | cinedance: 30 images, 10 videos, 10 audio (50) | Higgsfield blog: "up to 50"; one API blog: 5 per run | Write to the skill. Use one subject per image and usually 3 to 6 references. Audio under 30 s in total |
| "Filmed with iPhone" cue | Skills: strip camera bodies and brands | Phone-look blog: "Filmed with iPhone" is the key cue | **Skills win:** use the generic "smartphone front or main camera" texture lines. A brand cue is allowed only as a logged single-variable QC test |
| Negations | human-realism and production-consistency: negations are noise (images) | cinedance: short local functional locks are fine. Blogs use "no music, no text" | Functional locks (no subtitles, no music, no readable text, no extra people) are **in**. Aesthetic negations are **out**, except the earned skin lock or game-look lock after a logged failure |
| Lead-in silence vs lip-sync | cinedance: at least 1 s of silence before and after each line, when needed | Lip-sync blog: lead-in silence makes the mouth start late | Exactly a 1 s handle, speaker visibly about to speak, start second named |
| @Audio reproduces the voice | cinedance: an audio reference carries the voice | Practitioner test: guides timbre and pace; near-verbatim only in close-ups | Use @Audio for close-up talking shots. QC the voice. Fall back per G.1 |
| Clip length | cinedance: up to 30 s | production-consistency: 4 to 8 s is most reliable | Use the per-shot table in H.1 |

---

## 13. Sources

**Skills read in full:**
- `cinedance-higgsfield/SKILL.md`
- `human-realism/SKILL.md`
- `production-consistency/SKILL.md` and `references/` (higgsfield-models, prompt-shapes, consistency-playbooks, finishing-and-delivery, magnific-tools)
- `higgsfield-production/SKILL.md`
- `cinematic-director/SKILL.md`, plus references skimmed: sound-and-voice, world-bible, commercial-craft, film-grammar, screening-qc

The `human-realism/references/` folder (realism-blocks.md, chiaroscuro-series.md) is not present in this install. The 13-block wording above is taken from SKILL.md itself.

**Web (fetched 22 Oct 2026):**
- Higgsfield: Seedance 2.5 on Higgsfield. https://higgsfield.ai/blog/seedance-2-5-on-higgsfield-2026
- Higgsfield help centre, Soul ID. https://higgsfield.ai/creator-hub/help-center/ai-models/how-do-i-create-and-use-a-soul-id-character
- Higgsfield, character reference sheets. https://geo.higgsfield.ai/blog/specific-character-reference-sheets-video-generation
- AI Video Sensei, Seedance 2.5 Higgsfield settings (catalogue checked 7 Aug 2026). https://aivideosensei.com/guides/seedance-2-5-higgsfield-settings
- fal, Seedance 2.5 vs 2.0. https://fal.ai/learn/devs/seedance-2-5-vs-seedance-2-0
- videoai.me, Seedance iPhone-look prompts. https://videoai.me/blog/seedance-2-0-iphone-look
- Wireflow, real voice in Seedance 2.5. https://www.wireflow.ai/blog/real-voice-seedance-2-5
- seedance.tv, Seedance 2.5 lip-sync issues. https://www.seedance.tv/blog/seedance-2-5-lip-sync-issues
- Runware, Seedance 2.5 multi-reference guide (@Image1 / @Audio1 numbering). https://runware.ai/docs/models/bytedance-seedance-2-5/guides/multi-reference-production

Everything about the live Higgsfield UI (resolution list, frame slots, Soul-as-Element) changes often. **Check it in the UI before the first generation**, and update section 12 if it differs.
