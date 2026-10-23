# Character sheets: the AI presenter and the incidental people (N1_AI_PRESENTER, EXTRA_MODE_C)

This file covers the two cast members who are **not real, named people**. **N1** is an invented woman: a clearly labelled AI presenter. She is used **only** if a fallback is triggered in V01 (Version B2: the Golden Line owner takes no part at all) or V15 (Version B: Hassan declines). She is designed once from words (Mode A), you approve her once, and from then on every prompt treats her like a real person (Mode B, no face description). She never quotes a client, never says "we", is never named, and carries `AI presenter. Real client data. Not a client testimonial.` on screen the whole time. **EXTRA_MODE_C** is everyone incidental: a driver's hands on a wheel, a passenger seen from behind, a dispatcher in soft focus. They are nobody, so they are **never identifiable**, never shown with a face, and never presented as a client, a client's driver or customer, or agency staff. They need no sheet and no Soul: two lines of skin and wardrobe (the SKIN-C lock) and one of the six descriptions below. Most of the "make today" shots (BR01, BR02, BR04, V04, V08 and the V11 hands) use them, so get them right first.

**Before you start**
- **Settings for N1's sheet:** Nano Banana Pro · 3:2 · 4k · count 4 (pick the best of the four). On the Higgsfield MCP, load the `character-sheet` workflow first.
- **Make N1 only when a fallback is triggered** (or as an optional test, see `00_START_HERE.md` §2). Her generations are **not** in the 86-take count.
- **No sheet, no Soul, no crops for extras.** Their continuity comes from the anchor still of each set-up and the fixed imperfection in the table in step 8.

---

## N1_AI_PRESENTER · Labelled AI case-study presenter (invented, not a real person) · Mode A once, then Mode B

### 1. Who she is, where she appears, and the fallback

She is an invented woman of about 55: a practical Midlands woman who has run a busy office most of her working life. She is deliberately ordinary, so she is **unlike the five polished GRP service presenters** and the 30 sample portraits on googlerankerpro.com. She sits in a cluttered back room (L10) that is **no particular business**. She tells a real case study in the third person, using real Golden Line data.

| Video | Generation IDs (proposed; fallback only, not in the 86) | What she does |
|---|---|---|
| V01 The Four O'Clock Phone, **Version B2** (the owner takes no part) | `v01_N1-01_16x9` (12 s, medium, lines 1–2), `v01_N1-02_16x9` (10 s, close, line 3), `v01_N1-01_9x16` (12 s, for the 45 s cut) | Introduces Golden Line and hands over to the receipts. The film becomes a **case-study explainer** and is described that way, never as a testimonial |
| V15 What Moved in Warwick, **Version B** (Hassan declines) | `v15_N1-01_16x9` (15 s), `v15_N1-02_16x9` (12 s), `v15_N1-03_16x9` (14 s close), `v15_N1-01_9x16` (15 s), `v15_N1-03_9x16` (14 s) | Narrates the same plates in the third person: "the agency", never "we". **No green screen in her frame.** Her data goes full frame in the edit |

**She is in V01 and V15 only, nowhere else.** She is never in V02–V14. V02, V06, V09, V13 and V14 explicitly forbid an AI narrator.

**If you do not approve an N1** (or would rather not use one):
- **V01:** prefer B1 (the owner's real voice over faceless footage) if he will give a voice memo. If he gives nothing, use A's Leam Taxis film, but only if Gate G3 clears. Otherwise V01 waits.
- **V15:** if Hassan declines and there is no N1, V15 waits. Our suggestion, which needs your OK: a receipts-only explainer over the real Warwick dashcam drive (RF07), with captions and no presenter.
- **Never** swap in a real person's look-alike, a client, or a generated "Ali".

### 2. Approvals and licences (she has no consent form, so get these in writing instead)
- **Your one-time approval of her look:** you sign off the chosen sheet once (date, file name `SHEET_N1_AI_PRESENTER_v1.png`). After that her face is never redesigned, only reused.
- **She is nobody real:** she is built from words only. No real person's photo, no stock photo and no "looks like [name]" was used, and she passes the resemblance check in step 3 (no likeness to the five GRP presenters, the 30 sample portraits, any client, any staff member or any public figure).
- **Voice licence:** her voice is a new synthetic voice designed from the casting brief in step 7, or a stock synthetic voice whose licence allows commercial use with AI disclosure. It is never a clone of anyone. If you hire a human voice actor instead, they sign a consent covering synthetic use, platforms, term and withdrawal.
- **The client's permission:** Golden Line's written permission to be named and to have its Search Console figures shown. This is still needed even though the owner does not appear. "Hulk Marketing built its website" rests on the verified footer credit. Every V15 "what the agency did" line needs the work log (Gate G7).
- **Approved words only:** you approve every line before generation. She speaks in the third person, never says "we", never quotes or paraphrases a client, and says only numbers from `gsc_data.json` with the plan's wording ("times shown", "average", "page one on average", no "No.1", "first", "now" or growth).
- **Labels and platforms:** `AI presenter. Real client data. Not a client testimonial.` stays on screen throughout. The TikTok AIGC, YouTube altered or synthetic and Meta AI-info settings are on for every post. Placement: the Golden Line case study and its social cut. Never the homepage testimonial slot.
- **Term and withdrawal:** keep a list of every published clip she is in. If Golden Line withdraws permission, or anyone says she resembles them, her clips come down within an agreed number of days [7] and she is retired.

### 3. Reference set (she has no photo shoot: about 20 minutes on Higgsfield)

| Step | Time | What you do |
|---|---|---|
| 1 | 2 min | Open Nano Banana Pro: 3:2, 4k, count 4. Attach **nothing**. She is made from the words alone |
| 2 | 5 min | Run the sheet prompt (step 4, prompt 1). Pick the one variant out of four that looks most like an ordinary photographed woman, not a model. Save it as `SHEET_N1_AI_PRESENTER_v1.png` |
| 3 | 3 min | Cut the five crops (step 6) from the chosen sheet |
| 4 | 5 min | Run the detail check (prompt 2) with `CROP_N1_AI_PRESENTER_front.png` attached (never the whole sheet). Zoom to 100%: pores, fine lines, the scar's texture and individual brow hairs must be there. Then run the approval still (prompt 3) at 16:9 with the crops attached. She must read as a real woman filmed in a real room |
| 5 | 3 min | **Resemblance check:** put the front crop beside the five GRP service presenters and the 30 sample portraits on googlerankerpro.com. Optional: run the front crop through a reverse image search. Any close likeness to anyone means you regenerate from step 2 |
| 6 | 2 min | Approve, then log it: `APPROVED N1 [date] SHEET_N1_AI_PRESENTER_v1.png`. From now on, **no face prose ever again** |

**Optional location photos for her back room (L10):** 6–10 photos of an ordinary real back room you have permission to use, taken from the corners at standing eye height in overcast daylight. A real room as the location reference makes her clips far less render-like. Clear or turn away anything identifying first: signs, certificates, papers, photos of people, and anything readable through the window. Name the files `LOC_L10_01.jpg` … `LOC_L10_10.jpg`. **Never use a client's premises or the agency room.** She is no particular business.

**Avoid:** uploading any real person's photo, any "in the style of" or "looks like" wording, beauty or skin-smoothing tools, upscaling the sheet, and redesigning her after approval. She never appears in a selfie shot, so she needs no front-camera views.

### 4. Higgsfield prompts

**Prompt 1: the character sheet (Mode A, human-realism 13 blocks).**
Settings: **Nano Banana Pro · 3:2 · 4k · count 4.** No attachments.
Tightened from master_plan §3.2. The broken capillaries are gone, because the age ladder puts them at 70+, not 55. A dry patch by the nostril (the skill's pale-skin cue) replaces them. Her hands are described, so the hands panel holds up. The eye sentence names her iris colour. There is one lived-in clothing detail. The far side of her face gets the light's falloff on three features. Her brows have a few stray hairs but no grey, because the age ladder puts sparse, greying brows at about 65, not 55.

```
Character reference sheet of one invented woman, photographed as twelve equal panels in a 4 by 3 grid with thin plain mid-grey gutters and no labels, no text, no numbers. Row one, head and shoulders at eye level: front facing with a calm neutral expression; three-quarter view turned to her left; three-quarter view turned to her right; left profile. Row two: full body front, head to feet; full body from behind; full body three-quarter view; both hands held up, backs in one and palms in the other. Row three, head and shoulders: a relaxed half-smile; mid-word as if talking, lips slightly parted; thinking, eyes looking just off camera to the left; close-up of the collar and knit of her cardigan. Around 55 years old, a practical woman who has run a busy office most of her working life, but clearly someone who still laughs easily at the end of a long day. White British, fair, warm-toned skin with redness around the nostrils, grey-green eyes, natural brows with a few stray hairs. Chin-length ash-brown hair with grey coming through at the parting, tucked behind one ear, flyaways at the crown and a cowlick at the front hairline. A small pale scar through her left eyebrow. Thin tortoiseshell reading glasses pushed up into her hair. Maximum realism (skin AND hair): moderate wrinkles, horizontal forehead lines, crow's feet, deepening nasolabial folds, faint under-eye hollows with darker circles, early vertical lip lines, a slightly softened jawline, visible pores, uneven pigmentation and mild darker patches, a few sun spots, a small dry patch beside one nostril, peach fuzz along the jaw and upper lip. Do not smooth, soften, rejuvenate or beautify her skin. Detailed grey-green irises with visible fibre texture, natural moisture, tiny visible vessels in the sclera, authentic catchlights. Individual hair strands, eyebrow hairs and eyelashes sharply visible. Her hair looks genuinely grown from the scalp, never painted or artificially perfect. The scar has realistic healed tissue texture and slight tonal variation. Her hands show natural knuckle creases, faint veins and short plain nails, five fingers on each hand. She carries herself plainly and without fuss. No obvious makeup. Wearing a moss-green wool cardigan over a cream crew-neck T-shirt, dark jeans, reading glasses pushed up into her hair; no logos, no printed text, in every panel. The cardigan is a little bobbled at the cuffs; plain flat dark shoes, scuffed at the toes. Seamless neutral mid-grey background (#8C8C8C) in every panel. One large soft light overhead and slightly to camera-left with even soft fill, gentle natural shadow under the chin and nose, the same light in every panel; the far side of her face falls a little darker, with soft shadow in the nasolabial fold, under the cheekbone and beneath the brow. Head panels framed like an 85mm portrait lens, body panels like a 50mm lens, no wide-angle distortion. Fine natural photographic grain.
```

The words "artificially perfect" are part of human-realism's fixed hair sentence (block 11), which tells the model what to avoid. They are not a hype token, so leave them in.

If it comes back glossy or waxy, **remove the sentence "Do not smooth, soften, rejuvenate or beautify her skin." first** (on Nano Banana Pro it can read as noise), then regenerate. Never add hype words to fix it.

**Prompt 2: detail check (optional, 2 minutes).** Nano Banana Pro · 1:1 · 2k · count 1. Attach `CROP_N1_AI_PRESENTER_front.png` only (cut in step 3), never the whole sheet.

```
Extreme close up of her left eyebrow, the small scar through it and her left eye, in this exact position and light. Slight natural imperfections, low exposure.
```

**Prompt 3: approval still (she is now Mode B, no face prose).** Nano Banana Pro · 16:9 · 2k · count 4. Attach `CROP_N1_AI_PRESENTER_front.png`, `_34left.png`, `_34right.png` and `_body.png`, plus `LOC_L10` photos if you took them.

```
The woman in the attached reference images, 100% matching her face, hair, build and proportions, sits at a cluttered desk in a small back room on an overcast late-October afternoon, half-turned towards someone just off camera-left, mid-word, her left hand resting beside a plain cream mug with a tea ring and faint steam rising from it. Wearing a moss-green wool cardigan over a cream crew-neck T-shirt, dark jeans, reading glasses pushed up into her hair; no logos, no printed text. Behind her: a radiator with chipped paint under a window camera-left showing a wet grey yard, box files with blank spines on a shelf, a coat on a hook, a cable trailing across the floor to a socket, a blind hanging slightly crooked. A laptop at the frame edge with its lid angled away. Dust drifts in the window light. Soft overcast daylight from a large window camera-left is the only key; the right side of the face falls a stop darker with soft shadow under the cheekbone; the overhead office lights are on but weak, adding a faint cooler top light; the window itself is slightly overexposed. Natural skin from the references, visible pores and fine texture, unretouched. Muted, lived-in indoor colour as it really looks: off-white and pale grey walls, worn wood and grey laminate, cool daylight at the window, a warm pocket of light from a lamp or ceiling bulb; people in navy, grey and mid-blue everyday clothes; nothing saturated. No on-screen text, captions or subtitles. All signs, labels, mugs, clothing, papers and screens are plain or turned away, with no readable words, logos or numbers. Number plates are not readable. Exactly one person visible. No extra people. Filmed on a handheld documentary video camera in available light: natural colour with a restrained grade, fine even digital grain, soft highlight roll-off on bright windows, real depth of field with a gently soft background.
```

The approval still is a test, not a video anchor. Each N1 shot still gets its own anchor still from the video file.

### 5. Soul ID training note
- **Default: no Soul for N1. Use the sheet crops.** She has at most 8 fallback generations, all solo, all in Seedance 2.5, which takes the crops as @Image references. A Soul trained on generated images can also lock in any AI smoothness.
- **Train a Soul only if her anchor stills drift** between set-ups, even with the crops attached. If you do: generate 20–30 varied stills of her on Nano Banana Pro from the crops (front, three-quarters, profiles, waist up, full body; neutral, talking, laughing; her back room by day and by lamp). Keep **only stills that pass the skin check** in step 9, name them `N1_TRAIN_01.png` … `N1_TRAIN_30.png`, and train a Soul named `N1_AI_PRESENTER`.
- **A Soul works only on `soul_2` and `soul_cinematic`.** Use `soul_2` for her anchor stills (the documentary look), with **one Soul per generation**.
- **Multi-person shots use Reference Elements, not a Soul.** She never shares a frame in the plan. If an edit ever puts her beside anyone, that shot uses Elements built from her crops.

### 6. Crops to cut from the sheet

Cut along the gutters so each crop is one panel with no grid lines. Keep the native resolution (no upscaling) and save as PNG. **Attach the crops, never the whole grid.** She has one outfit, so there is no suffix.

| Panel on the sheet | File name |
|---|---|
| Row 1, panel 1 (front head) | `CROP_N1_AI_PRESENTER_front.png` |
| Row 1, panel 2 (three-quarter left) | `CROP_N1_AI_PRESENTER_34left.png` |
| Row 1, panel 3 (three-quarter right) | `CROP_N1_AI_PRESENTER_34right.png` |
| Row 2, panel 1 (full body front) | `CROP_N1_AI_PRESENTER_body.png` |
| Row 2, panel 4 (hands) | `CROP_N1_AI_PRESENTER_hands.png` |

**Order in each video prompt's asset map:** front, three-quarter left, three-quarter right, then body (medium shots only), then the anchor still, then the L10 location still. **No @Audio** for her (production_rules §C: an invented presenter's prompt describes delivery only).

### 7. Voice: synthetic, labelled, one locked voice

She records no memos, so there are **no `MEMO_` files**. Her voice is designed once and then locked.

**Casting brief** (paste into Higgsfield's voice creation or ElevenLabs Voice Design; three adjectives plus one contradiction, age and region; never "the voice of" anyone):

```
A woman in her mid-fifties from Coventry or Warwickshire, with a soft West Midlands accent. Warm, unhurried and dry, faintly gravelly, plain-spoken but with a hint of a smile in the voice. She talks like someone explaining something useful to a neighbour across a kitchen table: steady pace, short sentences, a small settle at the end of each point. Recorded close in a small quiet room.
```

**How the voice is used**
- Generate 3 auditions and pick one. Save its voice ID as `VOICE_N1_AI_PRESENTER` and never change it.
- Generate each approved line separately: 3 takes, 5–8 s each, numbers written as words. Name the files `VO_N1_AI_PRESENTER_<video>_line<n>_t1.wav` (`_t2`, `_t3`). We keep the best take as `VO_N1_AI_PRESENTER_<video>_line<n>.wav`.
- In Seedance she voices the line from the delivery words only (pace and warmth, not timbre). **In the edit we lay the locked voice in as the final track**, so she sounds identical in every clip. If sync slips, we run a lip-sync repair to the locked voice (production_rules G.1, step 3) and QC it hard.
- **On-screen label, throughout:** `AI presenter. Real client data. Not a client testimonial.` Small, lower-left, above the safe zone. Also mention "AI presenter" in the post text.

**Lines (agency drafts, third person; you approve each one before generation)**

| File | Line (draft) | Gen ID, start second |
|---|---|---|
| `VO_N1_AI_PRESENTER_v01_line1` | "This is Golden Line Taxis in Warwick. Hulk Marketing built its website." | `v01_N1-01` (both ratios), 1 s |
| `VO_N1_AI_PRESENTER_v01_line2` | "Here's what Google shows for the last three months." | `v01_N1-01`, 7 s |
| `VO_N1_AI_PRESENTER_v01_line3` | "These are the last three months, and the positions are averages. There's no earlier period to compare yet." *(proposed closing line; the clicks, times shown and searches are three-month totals, so only the positions are called averages)* | `v01_N1-02`, 1 s |
| `VO_N1_AI_PRESENTER_v15_line1` | "Golden Line Taxis, Warwick. Here's what the agency did, and here's what Google shows now." | `v15_N1-01` (both ratios), 1 s |
| `VO_N1_AI_PRESENTER_v15_line2` | "The agency built the site, with pages for the airports and the towns around Warwick." **Blocked until the work log confirms it (G7)** | `v15_N1-01`, 7 s |
| `VO_N1_AI_PRESENTER_v15_line3` | "Over the last three months, the airport searches average page one. Five point three, six point one, seven point one." | `v15_N1-02`, 1 s |
| `VO_N1_AI_PRESENTER_v15_line4` | "And Kenilworth taxis: six point seven." | `v15_N1-02`, 8 s |
| `VO_N1_AI_PRESENTER_v15_line5` | "The next job is the big one: taxi Warwick, and the ways people type it." | `v15_N1-03` (both ratios), 1 s |
| `VO_N1_AI_PRESENTER_v15_line6` | "Fifteen hundred and twenty-two times shown, averaging ten point seven to twelve point six. The edge of page one." | `v15_N1-03`, 6 s |

Every V15 number traces to `goldenlinetaxiswarwick_gsc_3m.png`: rows 20, 6 and 7 (5.3, 6.1, 7.1), row 4 (6.7), and rows 5, 9 and 3 (665 + 486 + 371 = 1,522 times shown at 10.7, 12.6 and 11.5).

### 8. Wardrobe and props continuity

| Video · Gen IDs | Outfit | Wardrobe line (paste exactly) | Props that must not change |
|---|---|---|---|
| V01 B2 · `v01_N1-01_16x9`, `v01_N1-02_16x9`, `v01_N1-01_9x16` | The one outfit | `a moss-green wool cardigan over a cream crew-neck T-shirt, dark jeans, reading glasses pushed up into her hair; no logos, no printed text` | Glasses always pushed up into her hair (never on her nose, never in her hand); a plain cream mug with a tea ring; laptop lid angled away (SCREEN-AWAY) |
| V15 B · `v15_N1-01_16x9`, `v15_N1-02_16x9`, `v15_N1-03_16x9`, `v15_N1-01_9x16`, `v15_N1-03_9x16` | The one outfit | same line, verbatim | The same mug, the same glasses, the same L10 room and dressing (radiator, box files, coat on the hook, the crooked blind) |

- **One accessory only:** the glasses. No watch, rings, earrings or lanyard. A second accessory starts to read as costume.
- **No orange mug in her room.** The orange mug is the agency's object, and she is never agency staff.
- **No chroma-green screen anywhere in her frame**, because of her green cardigan. Screens are angled away (SCREEN-AWAY) or soft (SCREEN-SOFT). Her data goes full frame in the edit.
- **One light set-up for both videos:** L-OFFICE + PAL-INT + DOC-CAM in L10, with no AGENCY ADD-ON. The face is the same, the room is the same and the light is the same, so her V01 and V15 clips cut together.

### 9. Sheet QC (check before cutting any crops)

| Check | Pass if | First fix if it fails (production_rules D.7) |
|---|---|---|
| 1. Resemblance | **She looks like no real person**, and the twelve panels are clearly the same woman: the same scar, cowlick, grey parting and glasses | **Identity drift across panels:** pick another of the four variants, or regenerate with the prompt unchanged. **Likeness to anyone real:** regenerate from scratch and log why |
| 2. Skin not smoothed | Pores, crow's feet, forehead lines, sun spots and peach fuzz are visible at 100%, with no waxy sheen and no de-ageing (she must read as 55, not 40) | **Plastic skin:** remove the "Do not smooth…" sentence first. Then add a faint rim light, then check the age ladder. Change one thing per retry |
| 3. No text or logos on clothes | Cardigan, T-shirt, jeans and shoes are plain everywhere: no labels, tags or lettering | **Gibberish text:** regenerate. If one panel is otherwise perfect, region-edit the mark out |
| 4. Consistent light | One soft light from overhead and camera-left in all 12 panels, the same grey, and the far cheek a little darker | **Game-render look** (shadowless, everything equally sharp): re-paste the light sentence exactly and regenerate |
| 5. Hands | Five fingers on each hand, with knuckle creases, faint veins and short plain nails | Regenerate (count 4, choose the best). If the hands still fail, cut the body crop only and let the video files keep her hands below frame or in soft focus |

Log it: `QC [date] N1_AI_PRESENTER sheet v[n] / Verdict PASS|FAIL / Failure: symptom > fix`.

---

## EXTRA_MODE_C · Incidental people: hands, backs of heads, passengers from behind (nobody) · Mode C

### 1. Who they are, where they appear, and the fallback

They are generated people who are **never identifiable**: they are small, soft-focus, partly cropped, seen from behind or from the chest down. They are never a named client, a client's driver or customer, or agency staff, and no caption ever says or implies who they are.

| Video | Gen IDs | Who the extra is | Description |
|---|---|---|---|
| Shared bank (V01 open) | `BR01_16x9` | A driver's hand taking a phone off the dash, pre-dawn | none (SKIN-C Lock B only; the hand enters at 4 s) |
| Shared bank (V01 open, V12 payoff) | `BR01_9x16` | A driver's hand on the gear knob, then pulling the phone from a vent mount | none (SKIN-C Lock B only; V01.md writes the hand) |
| Shared bank (V01 problem) | `BR02_16x9` | A driver from behind, lifting a wheelie case into a boot under a street lamp | C2 |
| Shared bank (V02 tail) | `BR04_16x9` | A driver and a passenger, chest down, handing over a case at a drop-off kerb (**two people**) | C3 |
| V04 May vs August | `v04_P-01_9x16`, `v04_P-02_9x16`, `v04_P-01_16x9`, `v04_P-02_16x9` | One driver, chest down, hands on the wheel; lifts the phone | C1 |
| V04 | `v04_B-01_9x16` | The same driver's hand turns a face-down phone face-up on the dash | none; its own anchor still (`ANCHOR_v04_B-01_9x16.png`), Lock A |
| V05 Night Shift, York | `v05_W-02_16x9`, `v05_W-02_9x16` | A dispatcher at the back of the room, from behind, soft focus (the manager is the second person) | C5 |
| V05 | `v05_B-01_16x9`, `v05_B-01_9x16` | The dispatcher's hands on a radio handset and a keyboard | C6 |
| V08 One in Ten | `v08_P-01_9x16`, `v08_P-03_9x16` | A hand on a laptop trackpad (illustrative; T1's real voice is the soundtrack) | C6 + the V08 sleeve swap |
| V11 Day One of an Audit | `v11_O-02_9x16` | Hands pressing blank Post-its onto a monitor bezel | C6 |
| Fallbacks only | V01 B1 voice-only (hands on the wheel, back of the head against the side window, keys); V02 voice-only (shots from behind the shoulder, if the owner has not ticked "back of head and hands"); V03 no-face POV walk (`v03_P-01_9x16`: **nobody in frame**, so no extra) | A stand-in who is never presented as the owner | C1, C4 |
| Fallback · V01 B1, box c only | `v01_B1-01C_16x9`, `v01_B1-02C_16x9`, `v01_B1-03C_16x9` (the Mode C swaps in V01.md) | Anonymous hands and back of head, never his | C1, C4 · **Lock B** |
| Fallback · V02, box c only | `v02_A-01C_16x9`, `v02_V-01C_16x9`, `v02_V-01C_9x16` (saved with a `C` on the shot) | An unidentifiable stand-in from behind, never the owner | C4 · **Lock C** |
| Fallback · V06 Version B, no hands consent | `v06_B-01C_16x9`, `v06_B-01C_9x16` | Anonymous hands with a pen on a blank page, never the director | as V06.md writes it · **Lock C** (ink mark) |
| Fallback · V07, voice-only T1 | `v07_P-01_9x16` | Anonymous hands in a dark rain-jacket cuff typing on a phone | as V07.md writes it · **Lock B** |
| Fallback · V09 Version B2, box c only | `v09_H-01C_9x16`, `v09_B-01C_9x16` (the Mode C swap in V09.md) | Anonymous hands on the wheel, never the owner | as V09.md writes it · **Lock B** |
| Fallback · V11 Version B1 twins | `v11_O-01C_9x16`, `v11_O-03C_9x16` | Anonymous hands at the whiteboard and the cards, never T2 or T1 | O-01C: as V11.md writes it · **Lock C**; O-03C: C6 with the mid-blue cuff · **Lock B** |
| Fallback · V12 Version B, voice-only T2 | `v12_A-02C_9x16`, `v12_A-03C_9x16`, `v12_B-01C_9x16`, `v12_B-02C_9x16`, `v12_B-03C_9x16` (the Mode C swap in V12.md) | Anonymous hands, never T2 | as V12.md writes it · **Lock C** |

**If a generated extra fails QC twice:**
- Film the real thing on a phone. A consenting colleague's real hands beat any generated hands (the plan prefers this for V08 and V09).
- Or cut the person out: objects only (a phone on the dash, a case at the boot) or an empty frame, as BR03 does.

### 2. Consent and honesty rules (5 points)
- **Generated extras are nobody, so no consent form is needed. That only holds while they stay unidentifiable:** no face, no tattoo, no distinctive jewellery or watch, and no readable lanyard, name badge or number plate.
- **Never presented as anyone:** not a named client, not a client's driver or customer, not agency staff. Captions never name them. In fallbacks where an owner's real voice plays over Mode C hands, the label reads `Dramatised visuals. Real voice, real data.` and nothing implies the hands are his.
- **Each video's own label stays on:** `Dramatised visuals. Real voice, real data.` (V08); `Illustrative footage. Real data.` (V11 hands, and V06's anonymous `v06_B-01C` hands); `Dramatised reconstruction · Real data` (V04); inside a Mode B film (V01, V02, V05, V12) that film's label covers the BR and Mode C clips, and nothing says the hands are the client's.
- **Never built from a real face:** no client's, driver's, customer's or reviewer's photo, and never a look-alike. Never a generated "Ali".
- **If you use real hands as a reference** (step 3, optional), that person signs a short written OK first: hands only, AI use, the listed videos and platforms, the term, withdrawal by email, and never named or captioned.

### 3. Photo shoot: none needed. Optional real-hands reference (10 minutes)

Generated hands are the weakest part of AI footage. An optional real reference makes them far more convincing. Use only a consenting colleague (or yourself) after the written OK above.

| # | Photo (rear camera, 1x, about 60 cm away, overcast window light) |
|---|---|
| 1–2 | Both hands, backs, then palms, against a plain mid-grey surface |
| 3 | Both hands on the lower half of a steering wheel, in a parked car with the engine off, shot from the passenger seat at chest height |
| 4 | One hand lifting a phone out of a vent mount, with the screen turned away |
| 5 | One hand on a laptop trackpad, two fingers scrolling |
| 6 | Fingers pressing a blank sticky note onto a monitor bezel |
| 7 | One hand gripping the handle of a plain dark wheelie case |
| 8 | Hands typing on a keyboard, sleeves at the wrists |

**Optional car interior for V04 (L4):** 3–4 photos of an ordinary car interior from the passenger seat at chest height in overcast light: charcoal dashboard, grey seat fabric, rain on the windscreen. Cover the badge on the steering wheel with tape. Name them `LOC_L4_car_01.jpg` … `_04.jpg`. It is presented as a reconstruction, not as anyone's car.

**Avoid:** any face in frame, tattoos, rings or a watch with a visible logo, nail varnish or nail art, logos on sleeves, filters, beauty mode, Portrait mode and harsh sun. Keep real imperfections (a plaster, a chipped nail). Name the files `REF_HANDS_C_01.jpg` … `REF_HANDS_C_08.jpg`, send them full size and never over WhatsApp. In a video prompt, a hands reference goes in the asset map as `@Image n: hand shape, skin texture and proportions only; not an identity; ignore any background.`

### 4. The SKIN-C lock and the six incidental-person descriptions (paste into Seedance prompts)

**The two-line SKIN-C lock.** Paste it in LIGHTING, straight after the light line. There are three versions, and each one carries exactly one imperfection. Step 8 says which version each generation uses, so the same anonymous person keeps the same imperfection across clips. In a one-hand shot (V08 P-01 and P-03, V11 O-01C) the first line reads "on the back of the hand" instead of "on the backs of the hands", so the model doesn't add a second hand.

Lock A (plaster):
```
Real skin texture with visible pores and fine hairs on the backs of the hands; a plaster on one knuckle.
Plain dark everyday clothes; no logos, no printed text. Each incidental person is only partly in frame, seen from behind or from the chest down, and their face is never seen.
```

Lock B (chipped nail):
```
Real skin texture with visible pores and fine hairs on the backs of the hands; a slightly chipped nail on one thumb.
Plain dark everyday clothes; no logos, no printed text. Each incidental person is only partly in frame, seen from behind or from the chest down, and their face is never seen.
```

Lock C (ink mark):
```
Real skin texture with visible pores and fine hairs on the backs of the hands; a faint ink mark on the side of one finger.
Plain dark everyday clothes; no logos, no printed text. Each incidental person is only partly in frame, seen from behind or from the chest down, and their face is never seen.
```

**The six descriptions.** Paste the matching one into FIRST FRAME AND SPATIAL BLOCKING. Each says only who is where in frame one; every movement goes in the video file's TIMELINE at its second, and contact physics goes in PHYSICS.

**C1 · A driver's hands in a parked car** (V04 P-01 and P-02, V01 B1 fallback)
```
The driver is seen only from the chest down, sitting in the driver's seat of the parked car: a plain dark everyday jacket with the cuffs pushed back a little at the wrists, both bare hands resting on the lower half of the steering wheel, five fingers on each hand, knuckle creases and veins visible. Their face stays above the top edge of the frame and never enters it. The seatbelt is off and hangs slack; the jacket creases where the forearms rest, and the seat fabric dips under their weight.
```

**C2 · A driver from behind at an open boot** (BR02)
```
The driver is seen from behind and a little to one side, from the shoulders to the knees, standing at the open boot: plain dark everyday clothes, no logos or printed text, the back of the head soft and cut by the top edge of the frame. One hand rests on the handle of a plain dark grey hard-shell wheelie case with a scuffed corner, standing on the kerb beside the boot. They never turn towards the camera.
```

**C3 · A passenger and a driver at a drop-off kerb** (BR04, two people)
```
Two people, both seen only from the chest down, stand at the open boot of a plain parked car at a drop-off kerb: the driver at the boot and the passenger facing them, both in plain dark everyday clothes, no logos or printed text, the passenger's coat a shade lighter grey. The driver's right hand holds the extended handle of a plain dark grey hard-shell wheelie case with a scuffed corner, standing upright on the kerb between them; the passenger's hands hang at their sides. Neither face enters the frame.
```

**C4 · The back of a head, from behind** (V01 B1 and V02 voice-only fallbacks)
```
One person is seen from directly behind and slightly to one side: the back of the head, the collar of a plain dark everyday jacket and one shoulder fill the near edge of the frame, soft and out of focus, while the focus sits on what they are looking at beyond them. Only the edge of one ear is visible. They never turn towards the camera.
```

**C5 · A dispatcher at the back of the room, soft focus** (V05 W-02)
```
At the back of the room, one dispatcher sits at a desk with their back to the camera, small in frame and softly out of focus: plain dark everyday clothes, no logos or printed text, a radio headset over one ear, a lanyard turned round so only the plain back of the card shows. They lean a little towards a monitor that faces away; a radio handset stands on its charger within reach. Their face is never seen.
```

**C6 · Hands at a desk** (V05 B-01, V08 P-01 and P-03, V11 O-02)
```
Only one person's bare hands and forearms are in frame, close, entering from the bottom edge: the cuffs of plain dark everyday sleeves at the wrists, no logos or printed text, five fingers on each hand, knuckle creases and veins visible. The shoulders and face stay out of frame. The fingertips press and flatten slightly on whatever they touch, and the forearm takes its weight on the edge of the desk.
```

**V08 sleeve swap.** In `v08_P-01_9x16` and `v08_P-03_9x16`, replace C6's sleeve wording ("the cuffs of plain dark everyday sleeves at the wrists") with the line below. It matches the team file, so the desk reads as the same agency desk. The hand is still illustrative and is never captioned as T1.
```
the cuff of a plain mid-blue overshirt at each wrist
```

Also swap Lock B's second line to:
```
The cuff of a plain mid-blue overshirt; no logos, no printed text. The person is only partly in frame, and their face is never seen.
```

**V11 twins, the same swap.** `v11_O-03C_9x16` uses that mid-blue line too. `v11_O-01C_9x16` (and V12's Mode C swaps) wear T2's navy knit, so their Lock C second line becomes:
```
The sleeve of a plain navy knit jumper, pushed up; no logos, no printed text. The person is only partly in frame, and their face is never seen.
```

**V07 hands, the same swap.** `v07_P-01_9x16` wears T1's rain-jacket cuffs over the mid-blue overshirt (it plays under T1's real voice and is never captioned as T1), so its Lock B second line becomes:
```
Dark rain-jacket cuffs over plain mid-blue overshirt cuffs; no logos, no printed text. The person is only partly in frame, and their face is never seen.
```

**Audio lock for extras.** Paste it in AUDIO for every clip with an extra. V05 also keeps its "radio crackle with no intelligible words".
```
The incidental people do not speak. Any voices are distant and unintelligible, with no words that can be made out.
```

**People count.** Extras count in PEOPLE-COUNT: BR04 `Exactly two people visible, both seen only from the chest down. No extra people.`; V05 W-02 `Exactly two people visible. No extra people.`; every other extra shot is one person.

### 5. Soul ID training note
- **Never train a Soul, make a sheet or create an Element for an extra.** They have no identity to lock, and locking one would make them identifiable.
- **Continuity comes from the anchor still.** V04's four P plates come from the same anchor still (one per ratio); `v04_B-01_9x16` has its own anchor still (`ANCHOR_v04_B-01_9x16.png`). All five use Lock A. The BR01 and BR02 pre-dawn driver shares Lock B and the same dark jacket. BR02 and BR04 use the same scuffed grey case.
- **Shots with a real person and an extra** (V05 W-02: the York manager plus a dispatcher): the manager is attached by their own crops or Soul. The dispatcher is prose only (C5) and is never given an @Image. A Soul still means one per generation.

### 6. Crops

**None.** Extras have no sheet, so there are no `CROP_EXTRA_MODE_C_*` files. Attach these instead:
- the set-up's **anchor still** (from the video file), which carries the hands' look and position from frame one;
- optionally `REF_HANDS_C_##.jpg` (step 3) with the "hand shape, skin texture and proportions only; not an identity" job line;
- optionally `LOC_L4_car_##.jpg` for V04's car.

### 7. Voice

**None.** Extras never speak intelligibly. They record no memos and have no synthetic voice. Ambience and foley come from their actions: the finger taps on the wheel, the boot thunk, the trolley rattle, the chair creak, the radio crackle. Use the audio lock in step 4.

### 8. Wardrobe and props continuity

| Gen IDs | Who | Wardrobe | SKIN-C lock | Props that must stay the same |
|---|---|---|---|---|
| `v04_P-01_9x16`, `v04_P-02_9x16`, `v04_P-01_16x9`, `v04_P-02_16x9`, `v04_B-01_9x16` | The V04 driver (one person in all five) | `plain dark everyday clothes; no logos, no printed text` (a plain dark jacket, cuffs pushed back) | **A** (plaster) | The same phone in the vent mount (screen edge-on), a charging cable looped over the gear lever, a parking ticket face-down on the dash, the wiper parked mid-glass, engine off |
| `BR01_16x9`, `BR01_9x16`, `BR02_16x9` | The pre-dawn driver (BR01 and BR02 read as one person) | same line | **B** (chipped nail) | The phone, which lights face-up with its screen edge-on; the wiper parked mid-glass; a plain dark grey hard-shell wheelie case with a scuffed corner (BR02) |
| `BR04_16x9` | A driver and a passenger | same line, with the passenger's coat a shade lighter grey | **B** on the driver's hand | The **same scuffed grey case as BR02**; the boot open; no signage anywhere |
| `v05_W-02_16x9`, `v05_W-02_9x16`, `v05_B-01_16x9`, `v05_B-01_9x16` | The York dispatcher | same line (a plain dark sweatshirt) | **C** (ink mark) | The radio handset on its charger, the headset, the lanyard turned round, a tea-stained mug, keys on hooks, monitors facing away |
| `v08_P-01_9x16`, `v08_P-03_9x16` | An illustrative hand at the agency desk | C6 with the **mid-blue cuff swap** | **B** (chipped nail) | The same laptop (flat green, four corner dots); the **orange enamel mug with the chipped rim** that `v08_P-02` shows |
| `v11_O-02_9x16` | An illustrative pair of hands at the agency desk | `plain dark everyday clothes; no logos, no printed text` | **C** (ink mark) | Three blank orange-and-yellow Post-its; the monitor soft (SCREEN-SOFT) |

- **No watch, rings or keys on a branded fob** on any extra. The keys in fallback shots are on a plain ring.
- **The same person keeps the same lock.** Never change an imperfection between clips of one set-up.

### 9. QC (on the anchor still first, then on every clip)

| Check | Pass if | First fix if it fails (production_rules D.7) |
|---|---|---|
| 1. Not identifiable (this replaces "resemblance") | No face, profile or reflection of a face anywhere, including in the windscreen, the side glass or a dark screen. No tattoo, distinctive jewellery or readable lanyard. Nothing makes them look like a client, a driver we know, or staff | **Extra people or a face appears:** state the exact count and "seen only from the chest down", then remove any person from the location still. If a face shows in a reflection, reframe the anchor still |
| 2. Skin not smoothed | Pores, fine hairs, knuckle creases and the one imperfection are visible on the hands. No waxy or rubbery sheen | **Plastic skin:** strip any hype words and check the anchor still was not glossy (remake it if it was). Only then add the earned skin lock |
| 3. No text or logos on clothes | Sleeves, jackets, the case, the lanyard and the keys are plain, and number plates are not readable | **Gibberish text:** paste the TEXT-LOCK, name the object as plain ("a plain dark grey case"), then region-edit or blur it in the edit |
| 4. Consistent light | The hands sit in the set's one named light (L-CAR-DAY, L-TAXI, L-STREET-NIGHT, L-PREMISES or L-OFFICE), with falloff and the same direction as the rest of the shot | **Game-render look:** name the one light source with falloff, add two dressing anchors and one uncomposed element, add atmosphere (rain on glass, steam, breath) |
| 5. Hands | Five fingers on each hand, nothing fused or bent backwards, real weight in every touch (fingertips flatten, the case drags the arm down) | **Floaty or wrong hands:** add the physics (weight, contact, settle), one action per stage, a shorter clip. Then use a real-hands reference (step 3) or film real hands on a phone |

Log it: `QC [date] grp_[ID] t[n] [seedance_2_5] / Verdict PASS|FAIL / Checks realism identity text/screens motion audio honesty / Failure: symptom > broken lock > fix`. Change one thing per retry and never retry silently.
