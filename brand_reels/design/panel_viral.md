# Panel memo, judge 1 of 3: retention + shareability (viral-strategist)

**Client:** Jawad, @jawad_mp4 (nickname JD), video editor and motion designer, Pakistani + Indian audience.
**Stage:** concept gate for the 5-reel set (30-40 s, 1080x1920, 30 fps, Hinglish / Roman Urdu VO).
**Date:** 2026-10-08. **Voice:** Higgsfield preset "Vlad" (elevenlabs_v4, Devanagari input). It is an AI TTS voice,
deep (median f0 ~100 Hz) and expressive, with a measured 142.8 wpm before the planned 1.06-1.10x stretch, so plan on
about 2.6-2.75 spoken words per second (`pipeline/jawad_reels/vo_config.json`, `tts/hf_dl/vlad/eval_vlad.json`).
**Inputs read:** `brand_reels/research/` cinematic_casebook_concepts (sections 0, 1, 3, 4, 5, 6, 7),
hooks_retention_captions, trends_india_pakistan, niche_competitors, repo100_audit, transitions_sound_music_bible
(cheat card + family allocation), ref1/ref2/ref3 analyses, studio_setup; `.claude/skills/jawad-brand-reels/SKILL.md`;
the character-sheet crops (`workspace/brand_reels/charsheet/contact_sheet.jpg`) and the prior covers.

> 1M views is a stretch goal, never a forecast. Nothing here says "will go viral". Reach also depends on
> distribution, timing and luck. This memo only stacks the odds: hook, hold, send, loop.

---------------------------------------------------------------------------------------------------------------

## 0. The verdict on one screen

**Recommended slate (five emotions, five hook mechanisms, five looks, five send targets, five transition families):**

| # | concept | emotion | hook mechanism | look | send target (who sends to whom) | transition family / signature device | wardrobe | score /100 |
|---|---|---|---|---|---|---|---|---|
| 1 | **C26 Pehle Wala Hi Theek Tha** (new, card in section 3) | exasperation, then laughter | relatable pain + open loop (a client quote) | `inferno` | colleague to colleague, editor to client ("yeh tum ho") | digital / editor-native: the reel under revision, then a Ctrl+Z rewind to v1 | streetwear (smirk, sunglasses, 3/4) | **88.1** |
| 2 | **C02 Beta, tum karte kya ho?** | amusement, then tenderness | dialogue / scene | `gold_hour` | sibling to sibling, or into the family group / to Mummy | match / morph: the "Mummy translate" misunderstanding renderer | suit (confused, shocked, neutral, hand-on-chest) | **85.4** |
| 3 | **C11 Bijli Chali Gayi** | nostalgia, then quiet pride | pattern interrupt (the reel's own power dies) | `dusk` | childhood friend / cousin to cousin ("yaad hai?") | light: diegetic power (brownout, CRT collapse, torch beam, power-on bloom) | suit (profile, smiling) | **85.3** |
| 4 | **C15 Log Kya Kahenge** | fear, then liberation | question / identity callout | `noir_ember` | friend to the friend held back by "log" | organic + type: depth-stacked judgements, edge-on cardboard reveal, ember disintegration | streetwear (3/4 turn full body, chin-up gaze) | **84.6** |
| 5 | **C08 Ek Frame ki Keemat** | awe, respect | specificity / number ("0.03 sec") | `ember` | editor / designer to the friend or relative who says "editing mein kya hai" | camera: exploded frame (orbit, fly-through, reassembly slam) | suit (3/4, smirk) | **80.5** |

Reserves: **C09 Client is typing** (81.6; takes slot 1 if C26 is rejected, same `inferno` slot) and **C24 Do Jawad**
(74.3).

**Verdict at this gate: FIX, then go to brief.** Every pick clears the gates (Hook >= 8, Share >= 7, Truth pass,
Brand >= 7) only with the framing fixes in section 4. None of them needs a re-concept. Ranked fixes, by expected
retention impact:

1. **Spoken hooks <= 7 words, landing by 2.7 s** (C08, C02 and C15 drafts ran 9-13 words, about 3.5-4.8 s at Vlad's
   rate). Owner: hinglish-scriptwriter. Lines are in section 4.
2. **Frame-0 and first-change rules.** C11's blackout keeps the glowing keyword on screen (no more than 4 frames of
   empty near-black). C15 opens already lit, on the crowd's head-snap, not on a spotlight clunk over a lone figure:
   that is the "Meeting my younger self" composition. C08 shows a pause click by 0.4 s and cracks by 1.0 s. C26's pin
   lands by 0.2 s. Owner: motion-timeline-builder, plus the colorist for C11 and C15 frame brightness (YAVG).
3. **Truth reframes.** Remove the invented hours from C08. Rewrite first-person memories as "hum / har desi editor /
   aap" in C11, C15 and C02. Exact line edits are in section 4. Owner: hinglish-scriptwriter. This is a gate.
4. **Lock every spoken number to the build before the VO is recorded:** C08's 12 layers, 3 tracks, 30 fps and 360
   layers per second; C26's 27 versions; C15's "5,000" if hook B is used. Owner: creative-director (brief), verified
   by motion-qa-reviewer.
5. **Pronunciation test of the hook words in Vlad** before the full VO run (about 2.5 credits per take). Test फ़्रेम
   in C08: the casting take's ASR heard लाइफ़ as "लाइप", so "frame" could come out as "prem". Also test ज़िंदा,
   कंट्रोल एस, मम्मी and सिनेमा. Fallback words are in section 4. Owner: hinglish-scriptwriter.

**Brand blockers to keep out of the brief.** No ERROR dialogs: that is the Yaadein cover device. No hearts in C02's
wedding parody. None of the banned old props: `chat_bubble`, `star_badge`, `pin_phone`, `question`, `logo_mark3d`,
`heart`. Bubbles, pins, badges and phones are new `ui.py` or `assets3d_jawad.py` builds. No split-screen "original vs
AI". No "Comment JD". Owner: creative-director, blender-3d-artist.

---------------------------------------------------------------------------------------------------------------

## 1. Method

**Gates** (from my brief): Hook >= 8, Share trigger >= 7, Truth pass, Brand >= 7. A concept below a gate goes back
with the fix.

**Composite /100** = 2.0·Hook + 2.0·Share + 1.5·Relatability + 1.5·Retention + 0.8·Novelty + 0.5·Loop +
1.0·Feasibility + 0.4·Brand + 0.3·Voice-fit (each axis 0-10), minus a risk adjustment of 0-10 for truth,
sensitivity or repeat issues that survive the reframe.
- **Retention** = second-by-second reason-to-stay potential: is there a visible change every 2.5 s, new information
  every 6 s, an open loop from 3 s to after 70 %, a re-hook between 12 and 18 s, and a rewatch trigger?
- **Feasibility** = buildable *today* with *zero mistakes*: local toolkit, Blender on CPU, character-sheet 2.5D
  cut-outs only (no lip-sync), procedural SFX and synthesized beds, about 18 min to render 35 s on one worker.
- **Voice-fit** = does it work with a warm AI narrator? Concepts that need a raw, intimate real voice score low, as
  instructed.
- Share and Hook carry double weight because sends per reach and the 3 s hold decide non-follower reach (section 7).

**Three-channel hook test:** picture, first spoken words and on-screen text all stop the thumb by 1.5 s, and still
work muted. **Hook lab** (0-2 each): Gap, Specificity, Fit (<= 8 spoken words, <= 6 on-screen words, lands by 3 s),
Voice (sounds like Hinglish, not translated English); Truth and Pull are pass/fail.

**Truth rule applied:** nothing about Jawad's family, first payment, father's wishes, earnings, clients, hours or
history. The only safe facts (repo audit section 4) are: handle @jawad_mp4, first name Jawad, nickname JD, video
editor / motion designer, does client work (generically), makes AI video, face permitted. Personal-memory concepts are
reframed as universal ("har editor", "hum", "aap", POV) or dropped.

---------------------------------------------------------------------------------------------------------------

## 2. Scoreboard: all 11 candidates plus my new concept

### 2.1 Ranked table

| rank | id | concept | 3-channel hook at 1.5 s (picture / text / voice / muted) | original hook lab: Gap, Spec, Fit, Voice; Truth; Pull | reason-to-stay potential | send (who to whom) | H | R | S | N | L | F | B | RT | V | risk adj. | **/100** | verdict |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | C26 | Pehle Wala Hi Theek Tha (new) | yes / yes / yes / yes | 2,1,2,2; pass; pass (7/8) | a visible revision every 1.1-2.1 s by construction, counter as a clock, payoff at 75 %, dense rewind | colleague to colleague, editor to client | 8 | 10 | 9 | 7 | 10 | 9 | 9 | 9 | 8 | 0 | **88.1** | SHIP to brief (my own concept: discount for author bias) |
| 2 | C02 | Beta, tum karte kya ho? | yes / yes / yes (line too long) / yes | 2,2,1,2; pass after POV; pass (7/8) | a new genre world every ~3 s, killer line at 13.8 s, family-group re-hook, Nani loop | sibling to sibling, into the family group | 8 | 10 | 9 | 6 | 9 | 8 | 8 | 9 | 8 | 0 | **85.4** | FIX (POV reframe) |
| 3 | C11 | Bijli Chali Gayi | yes / yes / yes / yes | 2,2,2,2; pass after reframe; pass (8/8) | blackout, torch reveals, "AA GAYI" gag, editor-era callback, Ctrl+S rhythm, power-on loop | cousin to cousin, school friend to school friend | 9 | 9 | 8 | 8 | 10 | 7 | 8 | 9 | 9 | 0 | **85.3** | FIX (universal "hum") |
| 4 | C15 | Log Kya Kahenge | yes / yes / yes / yes | 2,1,2,2; pass after reframe; pass (7/8) | judgement depth-stack, mid-reel reveal at 16-19 s, ember dissolve | friend to the friend held back | 9 | 10 | 9 | 6 | 7 | 7 | 9 | 8 | 9 | 0 | **84.6** | FIX ("hum", lit open) |
| 5 | C09 | Client is typing... | yes / yes / weak (TTS whisper) / yes | 2,2,2,1; pass; pass (7/8) | suspense open loop, jump-scare rhythm, double payoff | freelancer to freelancer | 8 | 8 | 8 | 7 | 9 | 9 | 8 | 9 | 6 | 0 | **81.6** | RESERVE 1 (same emotion as C26) |
| 6 | C08 | Ek Frame ki Keemat | yes / yes / yes (line too long) / yes | 2,2,1,1; FAIL as written (hours), pass after fix; pass (6/8) | exploded stack, a tag per beat, invisible-layer re-hook, 360 counter, reassembly slam | editor to "editing mein kya hai" friend | 8 | 7 | 8 | 7 | 10 | 9 | 10 | 8 | 8 | 0 | **80.5** | FIX (no hours, lock N); in slate for awe + process proof |
| 7 | C24 | Do Jawad | yes / yes / yes / yes | 1,2,2,1; pass as "har freelancer"; pass (6/8) | alternating bubbles, revolving swap re-hook | freelancer tags freelancer | 8 | 8 | 8 | 6 | 7 | 6 | 8 | 8 | 6 | -1 | **74.3** | RESERVE 2 |
| 8 | C01 | J · K · L | partly / yes / jargon / partly | 1,2,1,2; pass; pass (6/8) | shuttle-speed world, 1 s silence on K | editor to the friend "on 8x" | 6 | 6 | 7 | 8 | 9 | 8 | 10 | 8 | 8 | 0 | **72.3** | KILL for this set (hook gate: J/K/L jargon in the first 3 s); revive as a series episode |
| 9 | C14 | Dor | yes / yes / no (11 words) / yes | 2,1,1,2; pass after reframe; pass (6/8) | snap and tumble at 3 s, then a long string-follow that can sag | child to parent or mentor | 7 | 7 | 8 | 8 | 8 | 6 | 10 | 6 | 9 | -2 | **70.6** | KILL for October (hook gate, off-season, Basant string-injury sensitivity); revive for 14 Jan / Basant |
| 10 | C10 | Unsent Voice Note (Abbu) | yes / yes / AI voice as a son's voice note / yes | 2,1,2,0; FAIL as written; pass (5/8) | slow 60 BPM flyover, one big sunrise | child to father, sibling to sibling | 7 | 9 | 9 | 8 | 8 | 6 | 8 | 6 | 3 | -6 | **69.0** | KILL as written (truth + AI-voice impersonation of an intimate first-person message) |
| 11 | C07 | Prompt: a reel like @jawad_mp4 | partly / no (8 words) / no (12 words) / yes | 2,2,0,1; FAIL as written ("3 saal"); pass (5/8) | AI mock, diff view, human layers | editor to editor (debate) | 7 | 6 | 8 | 6 | 7 | 7 | 9 | 7 | 4 | -3 | **66.6** | KILL for this set (hook gate; near his Genjutsu "original vs AI" device; argued in an AI voice) |
| 12 | C23 | Ek Shot, Teen Kahaniyan | no (generic corridor) / yes / yes / **fails muted** | 2,1,1,2; pass; pass sound-on only (6/8) | three identical replays = visual stasis 8-20 s | creator to creator | 6 | 5 | 7 | 6 | 7 | 5 | 9 | 6 | 9 | 0 | **62.1** | KILL (hook gate, muted fail; procedural micro-scores must be excellent, which is the riskiest thing to promise today) |

Axes: H hook, R relatability, S share trigger, N novelty, L loop, F feasibility today, B brand, RT retention
potential, V voice-fit.

### 2.2 One line of evidence per axis

**C26 Pehle Wala Hi Theek Tha (new)**
- H 8: a polished ad frame plus a review pin landing by 0.2 s, lockup BAS EK *chhota sa* CHANGE by 0.5 s, and the logo swells at 1.0 s. All three channels by 1.5 s, and it works muted.
- R 10: "bas thoda sa change" is the #1 pain in the niche research (R5 x S5 = 25), and every desi with a boss, client, teacher or parent knows it.
- S 9: an indirect message (the strongest desi send driver, hooks §3.7): "send it to the client / the colleague who has the same boss".
- N 7: the revision meme is common. The device is not: the reel itself gets revised in front of you, with a live version counter and a Ctrl+Z rewind into frame 0.
- Truth: pass. It is POV, with a fictional client and a fictional brand, and says nothing about Jawad.
- L 10: v1 is frame 0. The sentence loop ("...aur phir client ne bola" into "Bas ek chhota sa change") and the "Approved" chip on frame 0 make it seamless.
- F 9: one parametric frame plus one Blender prop (a chai glass). The comedy lives in text pins, so the single TTS narrator never has to act.
- B 9: inferno warm black, a flame keyword *pehle wala*, a glass review UI.

**C02 Beta, tum karte kya ho?**
- H 8: a phone-glow close-up with a "Mummy" bubble and typing dots at f0, and the question in text by 0.3 s. The original spoken hook is 13 words: cut it to 7.
- R 10: the #1 desi trigger (parents' approval), the same in both countries.
- S 9: identity plus an indirect message to parents; tagging siblings; the family group.
- N 6: the "parents don't get my job" meme is common. Rendering each wrong guess as a full wrong-genre mini-scene is the fresh part.
- Truth: fails as written ("khala ne meri reel forward ki"). Passes as universal POV: "Sab se mushkil sawaal client nahi poochta. Mummy poochti hain."
- L 9: Nani's bubble "Beta, tum karte kya ho?" restarts it.
- F 8: UI-led (chat, translate card), suit expressions all exist; no hands, no Mummy on screen.
- B 8: gold_hour warmth plus a flame keyword *cinema*. The gaudy wedding parody must stay at or under 2 s and be ember-tinted.

**C11 Bijli Chali Gayi**
- H 9: the strongest pattern interrupt in the pool (the reel dies at 0.4 s). Text by 0.6 s, torch by 0.7 s.
- R 9: load-shedding in Pakistan, power cuts in Indian childhoods; the UPS/inverter beep is shared.
- S 8: shared nostalgia sent to cousins and school friends; memory comments.
- N 8: the reel obeying electricity is new; power-cut nostalgia alone is not.
- Truth: fails as written ("main ne editing shuru ki", "meri ungli"). Passes as "Phir woh bachche bare hue. Kuch editor ban gaye." plus "har desi editor".
- L 10: the power returns at the end, and on replay it dies again at 0.4 s.
- F 7: 4-5 Blender props, a torch mask and a layered crowd "aa gayi" cheer (Kokoro voices locally, or a text slam with a murmur bed as fallback).
- B 8: dusk torch and candle warmth. Dark frames need the colorist's YAVG check.

**C15 Log Kya Kahenge**
- H 9: thousands of silhouettes snap their heads toward you, plus the 3-word phrase both countries know.
- R 10: universal; the phrase is itself searched.
- S 9: inspiration sent to one named friend; low preachiness if the reveal carries it.
- N 6: a crowded motivational theme. The edge-on cardboard reveal (native to 2.5D planes) and "log busy hain apne 'log kya kahenge' mein" are new.
- Truth: fails as written ("Saalon tak main ne..."). Passes with "Hum saalon tak apni zindagi un logon ke hisaab se edit karte hain".
- L 7: the empty stadium refills and the heads face away again at the end, so the head-snap replays.
- F 7: tiers as silhouette strips on `K.Scene` planes; the reveal is a 70° orbit (planes go edge-on). No 5,000-object Blender render needed.
- B 9: noir_ember, one flame floodlight, and the brand colour blooms only at liberation.

**C09 Client is typing...**
- H 8: three red typing dots throbbing in a dark room. Frame 0 risks being too dark.
- R 8: freelancers, and "boss is typing" for office workers.
- S 8: freelancer to freelancer.
- N 7: horror grammar on UI is fresh; the "seen / typing" joke is known.
- Truth: pass.
- L 9: the closing dots are the opening dots.
- F 9: very cheap.
- B 8: inferno red.
- Why it is not in the slate: same emotion and same send target as C26. C26's indirect message is broader and its loop is tighter.

**C08 Ek Frame ki Keemat**
- H 8: frame 0 is a finished frame whose own lockup is the hook, with a pause click at 0.4 s and layer cracks by 1.0 s. The original 11-word line becomes 7.
- R 7: the craft angle reaches non-editors only through the payoff ("editing mein kya hai").
- S 8: social currency and pride; creatives send it to the people who undervalue their work.
- N 7: VFX layer breakdowns exist; the house-style exploded frame with an honest flat face pane does not.
- Truth: fails as written ("main ne ise kai ghante diye", "rim light · 25 min"). Passes with layer counts that are true by construction.
- L 10: the reassembled frame is frame 0.
- F 9: toolkit planes only; the corridor uses pre-flattened stack sprites.
- B 10: the house frame is the subject.

**C24 Do Jawad**
- H 8: a mirrored split in two wardrobes.
- R 8.
- S 8: tagging.
- N 6: split-identity skits are common.
- Truth: passes as "har freelancer", but the title "Do Jawad" and "3 baje" imply his own habits, and the search bar "cinematic kaise banate hain" undercuts his expertise with clients (-1).
- L 7.
- F 6: the streetwear sheet has no shocked or despairing expressions; comedy timing would rest on a deep TTS voice.
- B 8.

**C01 J · K · L**
- H 6: J/K/L is editor jargon in the first 3 s (the niche rule says never).
- R 6.
- S 7.
- N 8.
- Truth: pass.
- L 9.
- F 8.
- B 10.

**C14 Dor**
- H 7: the kite is pretty but not a stop; the contrarian line is 11 words.
- R 7: kite culture is regional, and October is off-season.
- S 8: gratitude to parents.
- N 8: underline = kite string is brand-native.
- Truth: fixable ("Ammi ki duayein" becomes generic).
- L 8.
- F 6: no hands are available, and the rooftops and string physics are costly.
- B 10.
- Risk -2: Basant 2026 string deaths and injuries (TechJuice, cited in the casebook).

**C10 Unsent Voice Note**
- H 7.
- R 9.
- S 9.
- N 8: the waveform landscape is novel.
- Truth: fails at the premise. A first-person voice note to "Abbu" voiced by an AI is both a private-fact claim and an AI voice standing in for a real son's intimate message, which carries the AI-label expectation for realistic voices attributable to a person (section 7).
- L 8.
- F 6.
- B 8.
- V 3.
- Risk -6.

**C07 Prompt: a reel like @jawad_mp4**
- H 7: @jawad_mp4 in the prompt means nothing to a stranger.
- R 6.
- S 8: debate.
- N 6: the AI-vs-human frame is crowded, and the compare view sits close to his Genjutsu "ORIGINAL vs AI" split.
- Truth: fails as written ("3 saal ki mehnat"); fixable.
- L 7.
- F 7: the "AI version" mock must look generic yet not cheap, which is hard to judge.
- B 9.
- V 4: an argument for human craft narrated by an AI voice is a credibility trap. The only honest way out is the twist "Yeh awaaz bhi AI ki hai. Kahani meri hai."
- Risk -3.

**C23 Ek Shot, Teen Kahaniyan**
- H 6: a generic corridor, and it fails muted.
- R 5.
- S 7.
- N 6: "same scene, different music" is a known film-school demo.
- Truth: pass.
- L 7.
- F 5: the content *is* three micro-scores, and ours are procedural synths.
- B 9.

### 2.3 What the killed ideas would need

- **C10:** a universal "unsent message" told in second person, with the message as on-screen text and the narrator as
  a narrator, not as the son. Or Jawad records it himself. Without one of these it should not ship in an AI voice.
- **C07:** a slate slot for a debate reel, plus the honest twist that the voice is AI. It is better next month, when
  the AI-label decision is settled.
- **C23:** a licensed or human-composed set of three micro-scores and a muted fallback (a grade shift per version).
  Not a today job.
- **C01, C14:** strong series episodes later (C14 for 14 January / Basant). Do not use them as hooks for cold
  non-followers now.

---------------------------------------------------------------------------------------------------------------

## 3. New concept: C26 · Pehle Wala Hi Theek Tha (v1 se v27 tak)

*Archetype:* A12 satire + A15 meta (the reel itself is the deliverable under revision).
*Emotion:* exasperated recognition, then laughter.
*Look:* `inferno`.
*Length:* 34.13 s (16 bars at 112.5 BPM; bar 2.133 s = 64 frames).
*Wardrobe:* streetwear cut-outs (smirk, sunglasses, 3/4 turn).

**Logline.** A beautiful 3-second chai ad gets "bas ek chhota sa change" 26 times. The reel degrades on screen, version
by version, until the client's last message rewinds everything to v1, which is frame 0.

**Why I think it beats C09, C24, C01, C14, C10, C07 and C23.** It is built on the highest-scoring pain in the research:
- "bas thoda sa change" is #1 in `niche_competitors.md` §2 (R5 x S5);
- hook #1 in `hooks_retention_captions.md` §2.7 (29/30).

It turns that pain into a device only an editor would make: the frame obeys every request, live. It has:
- a visible change on every bar by construction;
- a payoff at 75 %;
- a dense rewatch beat;
- a seamless loop with a story reason.

It needs one Blender prop and no lip-sync. The dialogue lives in text pins, so the single AI narrator never has to act
a second character. It is also the cheapest reel in the set. Author bias: I wrote it, so the other two judges should
discount my score.

**Hook A (recommended)**
- Picture: f0 is the finished chai ad (3D glass, steam, the keyword *garam*) inside a dark glass review player. A
  status chip reads "Approved" for frames 0-9, then flips to "Changes requested". A review pin thocks onto the frame at
  0.2 s ("Logo thora bara?"). The logo plate swells at 1.07 s.
- Text: `BAS EK / *chhota sa* / CHANGE` (4 words) by 0.5 s.
- Spoken: "Bas ek chhota sa change." (5 words, 0.1-2.0 s).

**Hook B (Trial Reel; only the first 3 s differ)**
- Picture: f0 is the v27 mess (giant logo, flares, starburst, banners) with the counter on "v27". At 2.6 s a fast
  rewind to v1 joins the body at 3.2 s.
- Text: `*27* REVISIONS BAAD` (3 words).
- Spoken: "Sattaees revision baad, client ne kaha..." (5 words).

**Beats (bars at 0, 2.13, 4.27, 6.40, 8.53, 10.67, 12.80, 14.93, 17.07, 19.20, 21.33, 23.47, 25.60, 27.73, 29.87,
32.00, 34.13).** Each request is obeyed literally on the same parametric frame, and the counter (`jw_mono`) ticks:

| version | request (pin) | what happens to the frame |
|---|---|---|
| v2 | "Logo thora bara?" | logo plate x2 |
| v3 | "Aur bara." | logo covers 35 % of the ad |
| v5 | "Thora aur pop karo" | saturation spike + starburst "NEW" (new 2D shape, not `star_badge`) |
| v6 | "Background white kar do, clean lagega" | **only the player interior** eases to cream over 0.4 s; the outer world stays dark |
| v8 | "Music thora energetic" | the player shakes on every beat |
| v10-11 | "Font fun wala" | the keyword swaps to a bubbly face |
| v12 (re-hook, 12.8 s) | new pin avatar "Owner ki Ammi": "Mujhe pasand nahi aaya" | glitter border |
| v16 | "Thora cinematic" | letterbox, flare overload, slow-mo steam; Jawad swaps to sunglasses |
| v17 | "Price bhi daal do" | a "50% OFF" banner (no currency) |
| v19 | "Sab kuch thora bara" | every element x1.2 |
| v20-26 | "CALL NOW" banner; half-bar pins | a "3:47 AM" chip; a version strip of thumbnails with filenames (`final_final_v7_REAL.mp4`, `ab_pakka_final.mp4`) |
| v27 (25.6 s, downbeat) | after typing dots and a near-silence: **"Pehle wala hi theek tha."** | the payoff |

Then:
- **26.0-27.6:** Ctrl+Z x26 rewind through every version.
- **27.73:** v1 is pristine, the chip reads "Approved", the lockup `*pehle wala* / HI THEEK THA` rises, and Jawad
  smirks.
- **28-30.6:** VO "Har editor jaanta hai: v1 hi final hota hai."
- **31.4:** bonus pin "Bas logo thora bara?".
- **32.0-34.13:** end card over the v1 world, with the VO loop line "...aur phir client ne bola—".

**Signature device.** *The reel under revision*:
- review pins land on the frame (thock motif);
- a live version counter;
- every note is rendered literally on one parametric frame;
- closed by a Ctrl+Z rewind of 26 versions in 1.6 s into frame 0.

**Transition family.** Digital / editor-native: D9 Ctrl+Z rewind (signature), a D7 RGB shock on each pin landing,
and L3 exposure-push glue. No other family.

**SFX.** Pin thock (motif), slot ticks on the counter, a drum fill for "energetic", a parody braam for "cinematic",
near-silence 25.1-25.6 s, tape-rewind for Ctrl+Z, a clean warm chord on v1.

**Music.** An original 112.5 BPM hybrid pulse that gets more cluttered with each version, as the frame does. It
collapses to near-silence, rewinds, and returns as a clean v1 motif. A trending song cannot follow the revisions; any
in-app song goes only under the end card.

**3D / UI.**
- Blender: one chai glass with steam (new prop in `assets3d_jawad.py`).
- `ui.app_window(title='chai_ad_v1.mp4', header='Review')`.
- New pin and chip designs: not the old `chat_bubble` or `star_badge`.
- `T.Counter(prefix='v')`.
- Jawad's streetwear cut-outs, lower-left, as the editor's reaction; captions kept off his face.

**Send sentence.** An editor, designer or anyone with a boss sends this to the colleague who suffers the same client
or boss (or, bravely, to the client) because it says "pehle wala hi theek tha" for them. That is an indirect message
plus "yeh tum ho".

**Comment prompt.** "Tumhare client ya boss ka 'bas ek chhota sa change' kya tha? Ek line mein." (fill-the-blank,
low friction).

**CTA pill.** "Us client ko bhejo" (4 words). No keyword CTA: there is no DM automation.

**Truth.** It is POV and universal. The client and brand are fictional (search-check the name; no real app UI, logos
or currency). The client stays likable: business owners are the clients Jawad wants.

**Risks.**
- The joke is a known meme, so the frame must look premium at v1 and the degradation must be funny, not just ugly.
- At most 2 text blocks at once: the pin plus the caption, and the hook lockup only in the first 2.6 s.
- Pins must be at least 42 px and readable at 360 px wide.
- "Owner ki Ammi" is a PK-leaning word ("Mummy" is the cross-border neutral; Jawad's call).

**Scores.** H 8 · R 10 · S 9 · N 7 · L 10 · F 9 · B 9 · RT 9 · V 8 → **88.1**.

---------------------------------------------------------------------------------------------------------------

## 4. The slate, reel by reel

Shared rules for all five:
- VO onset by 0.3 s.
- Spoken hook <= 7 words, landing by 2.7 s.
- A visible change at least every 2.5 s.
- Payoff at 70-80 %, on a downbeat, with the keyword.
- End card 1.5-2.5 s, over the living world, never on black.
- Last frame = frame 0.
- At most 2 text blocks.
- Captions drop words that a designed lockup already shows.
- No full-frame white flashes (use exposure pushes).
- Speech >= 8 LU above any bed; -14 LUFS; TP <= -2 dBTP.
- Deliver a VO + SFX stem so Jawad can lay an in-app song.

### 4.1 Reel 1 · C26 Pehle Wala Hi Theek Tha (`inferno`, 34.13 s, 112.5 BPM)

**Hook lab**

| hook | mechanism | text (<= 6) | spoken (<= 8) | Gap | Spec | Truth | Fit | Voice | Pull | /8 |
|---|---|---|---|---|---|---|---|---|---|---|
| **A** | relatable pain + open loop | BAS EK *chhota sa* CHANGE | "Bas ek chhota sa change." | 2 | 1 | P | 2 | 2 | P | 7 |
| **B** (Trial) | result-first + number | *27* REVISIONS BAAD | "Sattaees revision baad, client ne kaha..." | 2 | 2 | P | 2 | 2 | P | 8 |
| C | callout | CLIENT KI *favourite* LINE | "Har client ki favourite line." | 2 | 1 | P | 2 | 2 | P | 7 |
| D | contrarian | *v1* HI FINAL HAI | "V1 hi final hota hai." | 1 | 1 | P | 2 | 2 | **F** (spoils the payoff) | - |
| E | POV | POV: *feedback* AAYA | "POV: client ka feedback aaya." | 1 | 0 | P | 2 | 1 | P | 4 |

A is recommended, even though B scores one point higher on specificity:
- A's frame 0 is a beautiful frame, not a mess.
- A carries the seamless sentence loop.
- "Bas ek chhota sa change" is the phrase everyone already owns.

B may win the 3 s hold, so test it as a Trial Reel (section 7 on Trial Reels eligibility).

**Framing fix (truth-safe).** None needed beyond the card: POV, fictional client and brand, the narrator is "har
editor", not Jawad's memory. Keep "27" consistent with the counter.

**Retention map** (s = second index; 112.5 BPM bars at 0, 2.13, 4.27 ...)

| s | picture change | new information | open loop state | audio event | reason to stay | risk |
|---|---|---|---|---|---|---|
| 0 | f0 v1 chai ad in the review player; chip "Approved" (f0-f9) flips to "Changes requested"; pin thocks on at 0.2; lockup by 0.5 | a client wants "one small change" | OPENED: how small? (counter v1) | VO 0.1 "Bas ek chhota sa change."; pin thock; low pulse | instant recognition | without the pin by f6 it reads as "just an ad" |
| 1 | logo plate swells x2 on the beat (1.07); counter v2 | every request is obeyed literally | open | slot tick + whoosh | the rule of the game | - |
| 2 | 2.13 pin "Aur bara."; logo covers 35 %; v3; Jawad smirk | it is never one change | open, counter = clock | VO "Logo bara. Theek hai." | escalation | the lockup must exit by 2.6 (2-block cap) |
| 3 | 3.2 logo nudged again (v4, "thora left") | - | open | tick | micro-gag | low |
| 4 | 4.27 pin "Thora aur pop karo": saturation spike + "NEW" starburst (v5) | absurd request | open | pop; VO "Pop. Matlab? Kisi ko nahi pata." (4.3-6.2) | laugh | starburst must be a new shape |
| 5 | starburst wobble, sparkles | - | open | sparkle | motion | low |
| 6 | 6.4 pin "Background white kar do, clean lagega": player interior eases to cream (v6) | the cinematic look dies | open | VO "Clean." | visual shock | ease 0.4 s, inside the player only (no full-frame flash) |
| 7 | steam vanishes on cream; Jawad 3/4 turn (looks away) | - | open | deflate | gag | - |
| 8 | 8.53 pin "Music thora energetic": player shakes on every beat (v8) | - | open | drum fill; VO "Energetic." | physical comedy | shake <= 12 px, no blur on text |
| 9 | shake continues; v9 | - | open | drums | rhythm | - |
| 10 | 10.67 pin "Font fun wala karo": keyword swaps to a bubbly face (v10-11) | - | open | boing-lite | gag | - |
| 11 | font wobble; counter v11 | - | open | ticks | - | mild window: keep the counter moving |
| 12 | **RE-HOOK** 12.8: new pin avatar "Owner ki Ammi": "Mujhe pasand nahi aaya" (v12) | a new reviewer enters | escalated | sting; VO "Ab Ammi bhi review kar rahi hain." (12.9-14.6) | new character | Ammi/Mummy word choice |
| 13 | glitter border around the ad (v13-14) | - | open | shimmer | escalation | border must not be religious decor |
| 14 | 14.93 pin "Thora cinematic": letterbox + flare overload + slow-mo steam (v16); Jawad sunglasses | - | open | parody braam; VO "Cinematic. Bilkul." | the best gag | flares local, no full-frame lift |
| 15 | flare sweep | - | open | braam tail | spectacle | - |
| 16 | 16.0 pin "Price bhi daal do": "50% OFF" banner (v17) | - | open | stamp | - | no currency |
| 17 | 17.07 pin "Sab kuch thora bara": everything x1.2, crowding (v19) | - | open | whoosh | escalation | - |
| 18 | "CALL NOW" banner (v20) | - | open | stamp | - | no real phone number |
| 19 | 19.2 clock chip "3:47 AM"; pins every half bar (v21-23) | time is passing | open | ticks speed up; VO "Aur ek. Aur ek." | acceleration | - |
| 20 | version strip slides in under the player with filenames | easter eggs | open | card slide | rewatch fodder | filenames >= 34 px |
| 21 | 21.33 chaos peak: the ad unreadable | - | MAX tension | VO "Phir aakhri message aaya." (21.6-23.0); riser starts | what was the message? | - |
| 22 | filenames scroll | - | max | riser | anticipation | - |
| 23 | 23.47 typing dots in the pin thread; frame freezes | - | max | riser thins | suspense | - |
| 24 | dots stop ... restart; Jawad faces camera (3/4) | - | max | bed thins to room tone | suspense | hold is ok: dots are moving |
| 25 | 25.6 pin lands **"Pehle wala hi theek tha."** | the punchline | **CLOSED (75 %)** | near-silence 25.1-25.6, sub hit | payoff | - |
| 26 | Ctrl+Z x26: all versions rewind (26.0-27.6), counter spins back | - | - | tape-rewind, RGB shock last 3 frames | the dense rewatch beat | <= 3 luma flips/s |
| 27 | 27.73 v1 pristine; chip "Approved"; lockup `*pehle wala* HI THEEK THA`; Jawad smirk | v1 was the one | - | warm chord, clean v1 motif | keyword on the downbeat | - |
| 28 | underline draws | the lesson | - | VO "Har editor jaanta hai: v1 hi final hota hai." (28.0-30.6) | the quotable line | - |
| 29 | 29.87 embers; light sweep on keyword | - | - | shimmer | - | mild window |
| 30 | steam curls back (the ad lives again) | - | - | soft air | detail | - |
| 31 | 31.4 tiny pin drops: "Bas logo thora bara?" | the loop starts again | re-opened (loop) | thock | laugh | - |
| 32 | 32.0 end card over the v1 world: J mark, @jawad_mp4, pill "Us client ko bhejo" | CTA | - | VO "...aur phir client ne bola—" (32.3-33.8, rising) | sentence loop | VO tail trimmed to word end + 40 ms |
| 33 | camera glides to the frame-0 pose; chip "Approved" | - | - | pulse resolves into the f0 drone | seamless replay | - |
| 34 | 34.0-34.13 card lifts (exposure push) into frame 0 | - | - | - | loop | - |

**Drop-risk windows:** none over 2.5 s without a change. Mild at 11 s and 29-30 s (keep the counter and steam
moving).

**Rewatch triggers:**
- The "Approved" chip on frames 0-9: the client approved v1 before the first pin.
- The filenames in the version strip.
- The 1.6 s rewind.

**Cover:** 28.5 s (`*pehle wala* HI THEEK THA`, v1 ad, smirk) inside y 285-1480.
**Caption L1 (55 chars):** `Bas ek chhota sa change... video editing ki asli kahani`.
**Hashtags:** #videoediting #editorlife #freelancerlife #jawadmp4.
**Audio:** original only, with the stem delivered. Rename the audio "Bas ek chhota sa change · @jawad_mp4".

### 4.2 Reel 2 · C02 Beta, tum karte kya ho? (`gold_hour`, 35.2 s, 150 BPM felt as 75; bar 1.6 s)

**Hook lab**

| hook | mechanism | text | spoken | Gap | Spec | Truth | Fit | Voice | Pull | /8 |
|---|---|---|---|---|---|---|---|---|---|---|
| **A** | dialogue / scene | bubble: BETA, TUM *karte kya* HO? | "Sab se mushkil sawaal client nahi poochta." | 2 | 2 | P | 2 | 2 | P | 8 |
| **B** (Trial) | result-first | MOTION DESIGNER = *cartoon?* | "Mummy ki zubaan mein: motion designer, matlab cartoon." | 2 | 2 | P | 1 | 2 | P | 7 |
| C | relatable callout | GHAR WALE: *ye karta kya hai?* | "Ghar walon ko aaj tak samajh nahi aaya." | 2 | 1 | P | 1 | 2 | P | 6 |
| D | contrarian | *client* NAHI, MUMMY | "Sab se mushkil client nahi. Mummy hain." | 2 | 1 | P | 2 | 2 | P | 7 |

**Framing fix (truth-safe).** Universal POV. Line edits:

| draft line | replace with |
|---|---|
| "Har editor se sab se mushkil sawaal client nahi poochta. Ammi poochti hain." | "Sab se mushkil sawaal client nahi poochta." + "Mummy poochti hain." |
| "Phir main ne haar maan li." | "Phir... haar maan li." (no subject) |
| "khala ne meri reel family group mein forward kar di" | "Phir ek din family group mein... ek reel forward hoti hai." |
| "Mujh se behtar." | "...humse behtar." |

Staging and design:
- Mummy is never shown: bubbles only, no 3D hands.
- No ERROR dialog: the translate card folds away instead.
- No hearts in the wedding parody: use a sparkle wipe and a page curl, at most 2 s, ember-tinted gold chrome.
- Relatives' replies are religion-neutral ("Kamaal!", "Wah!").
- The phone is a `ui.py` mock, not `pin_phone`.

**Word choice:** "Mummy" is used in both countries; "Ammi" is PK-leaning. India's audience is about 15x Pakistan's.
Jawad decides.

**Device upgrade.** A "Mummy translate" SaaS card (input: his job title; output: her reading) feeds the
misunderstanding renderer: "Video editor" becomes "Shaadi wala?", "Motion designer" becomes "Cartoon?", "Content
creator" becomes "Phone pe lage rehte ho."

**Retention map** (bars at 0, 1.6, 3.2, 4.8 ...)

| s | picture change | new information | open loop state | audio event | reason to stay | risk |
|---|---|---|---|---|---|---|
| 0 | f0 phone glow on Jawad (suit_confused, large); "Mummy" bubble sliding in with dots; text by 0.3 | the question | OPENED: how will he explain? | VO 0.1 "Sab se mushkil sawaal client nahi poochta." (to 2.7); message pop | recognition | bubble must not cover the face |
| 1 | 1.6 slow push-in | - | open | pad | - | - |
| 2 | dots pulse on the bubble | - | open | tick | - | mild |
| 3 | 3.2 "Mummy translate" card slides up | the game | open | VO "Mummy poochti hain." (2.9-3.9); card slide | new UI | - |
| 4 | 4.8 input types "Video editor" | - | open | typing | - | - |
| 5 | 5.2 output "Shaadi wala?" morphs into the gaudy wedding title | misunderstanding #1 | open | shehnai sting; VO "Video editor bola. Suna: shaadi wala." (5.0-7.0) | genre whiplash | <= 2 s, no hearts, ember-tinted |
| 6 | 6.6 page-curl gag | - | open | paper flip | laugh | - |
| 7 | 7.6 snap back, zoom blur | - | open | whoosh | - | - |
| 8 | 8.0 input "Motion designer", output "Cartoon?" (8.4) | #2 | open | VO "Motion designer? Matlab cartoon." (8.6-10.4) | - | - |
| 9 | 9.6 MOTION wobbles rubber-hose and collapses; suit_shocked snap-zoom 9.8 | - | open | boing | laugh | the shocked face is subtle: sell it with the zoom and the sting |
| 10 | hold on the face | - | open | - | - | - |
| 11 | 11.2 input "Content creator", stamped "Phone pe lage rehte ho." (11.6) | #3 | open | stamp | laugh | - |
| 12 | **RE-HOOK** 12.8 input "Brands ke liye cinematic reels"; output loading "..." | - | escalated | loading ticks | what now? | - |
| 13 | 13.8 bubble: "Achha. Naukri kab lagegi?" | the killer line | max | one low piano note | the biggest laugh | - |
| 14 | 14.4 suit_neutral stare; translate card folds away | - | turns | VO "Phir... haar maan li." (14.6-15.8) | empathy | - |
| 15 | clock ticks; phone face down | time passes | open | tick, room tone | quiet before the turn | mild window: keep the clock hand moving |
| 16 | 16.0 chip "Kuch mahine baad"; phone vibrates on wood | - | open | vibration | something is coming | - |
| 17 | 17.6 family group "Khandaan" floods: "Yeh apna beta hai na??" + "Forwarded many times" | a reel is going around | re-opened: what will Mummy say? | pings; VO "Phir ek din family group mein..." (17.2-19.0) | new world | generic UI, no WhatsApp clone |
| 18 | "Kamaal!", "Wah!" bubbles stack | - | open | pings rising | - | religion-neutral replies |
| 19 | 19.2 the forwarded reel bubble glows | - | open | VO "...ek reel forward hoti hai." (19.0-20.4) | - | thumbnail generic |
| 20 | 20.8 "Mummy is typing..." | - | max | ticks | suspense | - |
| 21 | typing stops | - | max | silence tick | - | - |
| 22 | 22.4 typing again | - | max | strings swell | - | - |
| 23 | Jawad looks at the phone (suit_neutral) | - | max | swell | - | - |
| 24 | 24.0 bed thins | - | max | near-silence 24.8-25.6 | - | - |
| 25 | 25.6 bubble lands "Mera beta *cinema* banata hai." | the turn | **CLOSED (73 %)** | warm chord on the downbeat | payoff | - |
| 26 | 26.0 suit_hand_on_chest | - | - | - | emotion | - |
| 27 | 27.2 bubble glow | - | - | VO "Ab woh sab ko khud samjhaati hain." (26.6-28.6) | warmth | - |
| 28 | 28.8 "Seen" chip | - | - | VO "...humse behtar." (28.6-29.4) | bonus laugh | - |
| 29 | embers rise, light warms | - | - | swell | - | mild |
| 30 | 30.4 end card: J mark, @jawad_mp4, pill "Comment mein batao" | CTA | - | VO "Aap ki mummy aap ke kaam ko kya kehti hain?" (30.4-32.8) | the comment question | - |
| 31 | hold | - | - | - | - | - |
| 32 | 32.8 card lifts | - | - | - | - | - |
| 33 | 33.6 new bubble: "Nani: Beta, tum karte kya ho?"; suit_confused | the loop twist | re-opened | pop | laugh + replay | - |
| 34 | glide to the frame-0 composition | - | - | pad resolves | - | - |
| 35 | 35.0-35.2 frame 0 | - | - | - | loop | - |

**Drop-risk windows:** 14.6-16.0 (quiet beat), covered by the clock and the "kuch mahine baad" chip at 16.0. Mild
at 29 s.

**Send sentence.** Anyone with a job their parents never understood sends it to a sibling, or posts it into the
family group, because it says "yeh hum hain" and quietly asks the parents to be proud.

**Comment prompt.** "Aap ki mummy aap ke kaam ko kya kehti hain?"

**Cover:** 1.0 s (bubble plus confused face, `BETA, TUM *karte kya* HO?`).
**Caption L1 (50):** `Beta, tum karte kya ho? Har video editor ka sawaal`.
**Hashtags:** #videoeditor #editorlife #desifamily #jawadmp4.

### 4.3 Reel 3 · C11 Bijli Chali Gayi (`dusk`, 34.67 s, 90 BPM; bar 2.667 s)

**Hook lab**

| hook | mechanism | text | spoken | Gap | Spec | Truth | Fit | Voice | Pull | /8 |
|---|---|---|---|---|---|---|---|---|---|---|
| **A** | pattern interrupt | *Bijli* CHALI GAYI | "Bijli chali gayi." ... (beep) ... "Yeh awaaz yaad hai?" | 2 | 2 | P | 2 | 2 | P | 8 |
| **B** (Trial) | nostalgia question, no blackout | YEH *awaaz* YAAD HAI? | "Yeh awaaz... har desi ghar ne suni hai." | 2 | 2 | P | 2 | 2 | P | 8 |
| C | editor pain | LIGHT GAYI · *Ctrl+S?* | "Light chali gayi. Ctrl+S dabaya tha?" | 2 | 2 | P | 2 | 1 | P | 7 (editor-only breadth) |
| D | callout | CHHAT PE *raatein*? | "Agar bachpan chhat pe guzra hai..." | 1 | 1 | P | 2 | 2 | P | 6 |

**Framing fix (truth-safe).** Line edits:

| draft line | replace with |
|---|---|
| "Phir main ne editing shuru ki. Aur bijli meri sab se bari dushman ban gayi." | "Phir woh bachche bare hue. Kuch editor ban gaye. Aur bijli ban gayi editor ki sab se bari dushman." |
| "Tab se meri ungli khud Ctrl+S dabati hai." | "Isliye har desi editor ki ungli khud Ctrl+S dabati hai. Har tees second." |
| "Bijli ne mujhe ... sabr sikhaaya." | "Bijli ne humein editing nahi sikhaayi. *Sabr* sikhaaya." |

Keep it nostalgic, not political:
- no government, utility or city names;
- no "UPS" or "inverter" label: the beep says it;
- use a desktop PC (it dies instantly in a power cut) rather than a laptop.

**Retention map** (bars at 0, 2.67, 5.33, 8.0, 10.67, 13.33, 16.0, 18.67, 21.33, 24.0, 26.67, 29.33, 32.0)

| s | picture change | new information | open loop state | audio event | reason to stay | risk |
|---|---|---|---|---|---|---|
| 0 | f0 bright 2000s room (tube light, fan, warm CRT, desktop PC). 0.4 brownout flicker; 0.55 CRT collapses to a dot; 0.6 keyword glows in the dark; 0.7 torch clicks on | the power is gone | OPENED: what has this got to do with editing? | VO 0.1 "Bijli chali gayi."; fan winds down; CRT zap 0.55 | pattern interrupt | **the dark window 0.55-0.7 must keep the glowing keyword; <= 4 frames of empty near-black** |
| 1 | torch sweeps to a box blinking orange | - | open | beep 1.4, 1.9 (motif) | nostalgia trigger | no label |
| 2 | torch passes a dead desktop monitor (2.4: plant) | - | open | VO "Yeh awaaz yaad hai?" (2.0-3.1) | - | - |
| 3 | 2.67 a match strikes, the candle pool grows; hand fan, homework copy | objects | open | match strike | warmth | - |
| 4 | camera tilts up through the ceiling | - | open | VO "Light jaati thi, toh poora mohalla chhat pe hota tha." (4.0-6.6) | world change | - |
| 5 | 5.33 night rooftops: charpai silhouettes, neighbours' candles, stars | shared memory | open | crickets | recognition | the sky must hold some value (not crushed) |
| 6 | kids' silhouettes with hand fans; homework by candle | - | open | fan flaps | detail | - |
| 7 | anticipation pose | - | open | VO "Aur jab wapas aati thi..." (7.0-8.2) | setup | mild |
| 8 | 8.0 every rooftop bulb pops on in a cascade; slam AA GAYI! | the street-wide cheer | open | crowd cheer; VO "...poori gali cheekhti thi." (8.3-9.6) | laugh | the cheer must sound human: layered Kokoro voices, or a text slam with a murmur bed as fallback |
| 9 | fans spin up | - | open | cheer tail | - | - |
| 10 | 10.0 the power dies AGAIN | - | open | crowd groan | the gag | - |
| 11 | 10.67 back inside by torch | - | open | VO "Phir woh bachche bare hue." (11.0-12.3) | the turn | - |
| 12 | lights on: the desktop shows a timeline, render 63 % | editors were made here | **plant paid** | VO "Kuch editor ban gaye." (12.5-13.6) | new chapter | - |
| 13 | 13.33 modern edit desk (ember); render 63-64 % | - | escalated | render ticks | stakes | - |
| 14 | **RE-HOOK** 14.4 the power dies, monitor collapses (callback) | - | max | beep; VO "Aur bijli ban gayi..." (14.6-15.8) | callback | - |
| 15 | torch on the frozen grey render bar | - | - | VO "...editor ki sab se bari dushman." (15.8-17.2) | pain | "bari" spelling (ड़) |
| 16 | 16.0 the bar drains to 0 % | the loss | - | low boom | ouch | - |
| 17 | 17.2-17.6 silence; a keycap rises in the dark | - | - | room tone | breath | mild |
| 18 | 18.67 Ctrl + S keycaps (Blender) press on the beat | the habit | - | thock motif | rhythm | - |
| 19 | presses on every beat | - | - | VO "Isliye har desi editor ki ungli..." (19.0-21.0) | - | - |
| 20 | presses on 8ths | - | - | thocks | build | - |
| 21 | 21.33 "Saved" chip pings | - | - | VO "...khud Ctrl+S dabati hai. Har tees second." (21.3-23.6) | laugh | test कंट्रोल एस pronunciation |
| 22 | saved after every tiny action (chip flashes) | - | - | ticks | gag | - |
| 23 | keycaps settle into candlelight | - | - | swell | transition | - |
| 24 | 24.0 candlelit Jawad (suit_profile), flame rim | - | final turn | VO "Bijli ne humein editing nahi sikhaayi..." (24.3-26.5) | emotion | face edges clean, no halo |
| 25 | candle flicker, embers | - | - | - | - | - |
| 26 | 26.67 keyword *sabr* + underline on the downbeat | the lesson | **CLOSED (77 %)** | VO "...sabr sikhaaya."; warm hit | payoff | - |
| 27 | suit_smiling swap | - | - | - | - | - |
| 28 | hold | - | - | VO "Aur har cheez save karna." (28.0-29.2) | bonus laugh | - |
| 29 | 29.33 the power returns: every lamp blooms locally, fan spins up | - | - | distant "aa gayi" callback | relief | local bloom, no white lift |
| 30 | the bright room = the frame-0 world | - | - | - | - | - |
| 31 | hold | - | - | VO "Aap ke ghar light jaane pe kya hota tha?" (30.4-32.0) | comment prompt | - |
| 32 | 32.0 end card over the bright room: J mark, @jawad_mp4, pill "Chhat ya candle? Batao" | CTA | - | harmonium pad | - | - |
| 33 | glide to the frame-0 pose | - | - | - | - | - |
| 34 | 34.4-34.67 card lifts into frame 0 (on replay the power dies again at 0.4) | - | - | - | the gag loop | - |

**Drop-risk windows:** 4-7 s (exposition: keep the tilt-up moving) and 17 s (a short silence, by design). The torch
and candle stretch (0.6-24 s) is mostly dark, so the colorist checks frame brightness at 360 px.

**Send sentence.** Anyone who grew up in a desi home sends it to a cousin, sibling or school friend because "yeh
hamara bachpan hai".

**Comment prompt.** "Aap ke ghar light jaane pe kya hota tha? Chhat ya candle?"

**Cover:** 2.0 s (torch beam, glowing `*Bijli* CHALI GAYI`, the blinking box).
**Caption L1 (49):** `Bijli chali gayi: har video editor ki pehli class`.
**Hashtags:** #videoediting #nostalgia #editorlife #jawadmp4.
**Audio:** a nostalgic in-app track may enter at 29 s, under the stem.

### 4.4 Reel 4 · C15 Log Kya Kahenge (`noir_ember`, 35.2 s, 75 BPM; bar 3.2 s; beatless until the reveal)

**Hook lab**

| hook | mechanism | text | spoken | Gap | Spec | Truth | Fit | Voice | Pull | /8 |
|---|---|---|---|---|---|---|---|---|---|---|
| **A** | identity question | LOG KYA *kahenge*? | "Sab se bara darr: log kya kahenge." | 2 | 1 | P | 2 | 2 | P | 7 |
| **B** (Trial) | number specificity | *5,000* LOG · EK SAWAAL | "Paanch hazaar log. Ek hi sawaal." | 2 | 2 | P (only if the build really has ~5,000) | 2 | 2 | P | 8 |
| C | curiosity | YEH *log* HAIN KAUN? | "Yeh 'log' asal mein hain kaun?" | 2 | 1 | P | 2 | 2 | P | 7 |
| D | contrarian | LOG KUCH *nahi* KEHTE | "Sach bataun? Log kuch nahi kehte." | 1 | 1 | P | 2 | 2 | **F** (spoils) | - |

A is recommended because the phrase is the share hook and the search term. B may win the hold.

**Framing fix (truth-safe).** Line edits:

| draft line | replace with |
|---|---|
| "Saalon tak main ne apni zindagi un logon ke liye edit ki..." | "Hum saalon tak apni zindagi un logon ke hisaab se edit karte hain... jo poori video dekhte bhi nahi." |
| "Phir main ne gaur se dekha." | "Ab gaur se dekho." |

Opening and content guards:
- Open on the crowd's head-snap, already lit.
- Do not open on a spotlight clunk over a standing figure: that is the "Meeting my younger self" cover composition.
- Judgement lines are generic ("Yeh bhi koi kaam hai?", "Paise milte hain?", "Log hasenge.", "Naukri kab karoge?",
  "Pagal hai.").
- No religious or regional markers on the silhouettes.

**Retention map** (bars at 0, 3.2, 6.4, 9.6, 12.8, 16.0, 19.2, 22.4, 25.6, 28.8, 32.0)

| s | picture change | new information | open loop state | audio event | reason to stay | risk |
|---|---|---|---|---|---|---|
| 0 | f0 tiers of grey cardboard silhouettes, one flame floodlight already on, heads away; 0.1-0.5 head-snap wave toward camera; text by 0.5 | the crowd is judging you | OPENED: who are they? | VO 0.1 "Sab se bara darr..."; whisper swell; floodlight clunk 0.15 | uncanny stare | frame 0 must be lit (YAVG check) |
| 1 | crowd stares; slow push | - | open | whispers | - | - |
| 2 | push continues | - | open | VO "...log kya kahenge." (1.5-2.7) | - | - |
| 3 | 3.2 the first judgement flies out as 3D type: "Yeh bhi koi kaam hai?" | the voices | open | whisper burst | - | <= 2 legible lines at once |
| 4 | it recedes in depth; "Paise milte hain?" | - | open | burst | stack | - |
| 5 | "Log hasenge." | - | open | burst | - | - |
| 6 | 6.4 "Naukri kab karoge?" | - | open | whisper wall builds | pressure | - |
| 7 | "Pagal hai." | - | open | wall | - | - |
| 8 | lines swirl and clear: Jawad small at centre field in one spot (street_threequarter_turn) | you, alone | open | wall drops | contrast | - |
| 9 | 9.6 camera rises behind him; the crowd towers | - | open | VO "Hum saalon tak apni zindagi..." (8.8-10.8) | - | - |
| 10 | crowd leans in (sprite scale) | - | open | - | - | - |
| 11 | rise continues | - | open | VO "...un logon ke hisaab se edit karte hain..." (10.8-12.8) | the editor metaphor | - |
| 12 | 12.8 the crowd's heads tilt in sync | - | open | VO "...jo poori video dekhte bhi nahi." (12.8-14.6) | recognition laugh | - |
| 13 | camera holds high | - | open | - | - | mild: keep the rise moving |
| 14 | **RE-HOOK** 14.6-15.4 silence; the floodlight swings | - | open | silence | attention reset | - |
| 15 | spot settles | - | open | VO "Ab gaur se dekho." (15.4-16.4) | instruction | - |
| 16 | 16.0 crane + 70° orbit: silhouettes go edge-on, paper-thin cardboard on sticks | **they are cardboard** | turning | cardboard creak; rack focus | reveal | - |
| 17 | behind them: real people, heads down, faces lit by phones | they are busy | turning | phone ticks | second reveal | - |
| 18 | phone glows dot the stands like stars | - | turning | soft shimmer | "did you see it" | - |
| 19 | 19.2 hold on the reveal | - | turning | - | - | **drop risk 18.5-20.4: fix with a rack focus at 20.4 to one phone-lit silhouette scrolling** |
| 20 | 20.4 rack focus to one scroller | - | turning | VO "Log kuch nahi kehte." (20.0-21.4) | - | - |
| 21 | scroller's glow flickers (scrolling) | - | turning | - | - | - |
| 22 | 22.4 the cardboard crowd disintegrates into rising embers from the lowest tier up (O6) | - | closing | ember crackle; VO "Log busy hain... apne 'log kya kahenge' mein." (22.4-25.0) | the quotable insight | - |
| 23 | embers rise | - | closing | - | - | - |
| 24 | seats empty | - | closing | - | - | - |
| 25 | 25.6 empty stadium; the floodlight warms noir to ember (first full colour) | - | **CLOSED (71 %)** | piano returns | release | - |
| 26 | street_chinup_gaze swap (looking up) | - | - | - | hope | - |
| 27 | 27.2 lockup "Apni *kahani* khud likho." on the beat | the payoff | - | VO (26.6-28.6) | keyword moment | - |
| 28 | 28.8 underline draws | - | - | piano | - | - |
| 29 | one last cardboard figure in the stands tips over with a soft "tap" | - | - | tap | gag / rewatch | - |
| 30 | camera drifts down | - | - | VO "Us dost ko bhejo jo 'log' ki wajah se ruka hua hai." (30.0-32.6) | CTA | - |
| 31 | - | - | - | - | - | - |
| 32 | 32.0 end card: J mark, @jawad_mp4, pill "Us dost ko bhejo" | - | - | - | - | - |
| 33 | cardboard flaps rise back; seats refill | - | re-opening | flaps | loop setup | - |
| 34 | crowd refilled, heads away (the frame-0 pose) | - | - | whisper bed | - | - |
| 35 | 35.0-35.2 card lifts into frame 0, then the head-snap again | - | loop | - | loop | - |

**Drop-risk windows:** 18.5-20.4 (fixed by the rack focus), and mild at 13 s.

**Send sentence.** Someone sends it to the friend who keeps holding back "log kya kahenge ke darr se", because it says
"go for it" without a lecture.

**Comment prompt.** "Agar 'log' kuch na kehte, toh tum kya karte? Ek lafz mein." This is aspirational and avoids
inviting complaints about real people.

**Cover:** 1.5 s (full stadium staring, `LOG KYA *kahenge*?`).
**Caption L1 (48):** `Log kya kahenge? Har creator, har editor ka darr`.
**Hashtags:** #logkyakahenge #contentcreator #editorlife #jawadmp4.
**Audio:** a moody in-app track may replace the bed only after 25.6 s (the drop-out must stay).

### 4.5 Reel 5 · C08 Ek Frame ki Keemat (`ember`, 33.6 s, 100 BPM; bar 2.4 s)

**Hook lab**

| hook | mechanism | text | spoken | Gap | Spec | Truth | Fit | Voice | Pull | /8 |
|---|---|---|---|---|---|---|---|---|---|---|
| **A** | specificity | AAP NE ISE / *0.03 sec* / DEKHA (the frame's own lockup) | "Yeh frame aap ne palak jhapakte dekha." | 2 | 2 | P (1/30 s at 30 fps) | 2 | 1 (test फ़्रेम) | P | 7 |
| **B** (Trial) | number + spectacle | *360* LAYERS · 1 SECOND | "Ek second mein teen sau saath layers." | 2 | 2 | P (only if 12 x 30 is the build) | 2 | 2 | P | 8 |
| C | curiosity | EK FRAME KE *andar* | "Ek frame ke andar kya hota hai?" | 2 | 1 | P | 2 | 1 | P | 6 |
| D | contrarian | EDITING *aasaan* HAI? | "Sab kehte hain editing aasaan hai." | 1 | 0 | P | 2 | 2 | P | 5 |

**Hook B picture:** f0 is the 30-stack corridor mid-surge, cutting to the separating stack at 3.0 s, where it joins
the body.
**Fallback if फ़्रेम fails the test:** "Yeh tasveer aap ne palak jhapakte dekhi."

**Framing fix (truth-safe).**
- Remove "main ne ise kai ghante diye" and every per-layer minute.
- **Lock this layer list in the brief:** 01 background void, 02 haze + god rays, 03 bokeh, 04 cut-out (flat: honest
  2.5D), 05 rim light, 06 contact glow / shadow, 07 embers, 08 caps words, 09 keyword core, 10 keyword halo,
  11 underline, 12 finish (grain + halation + vignette) = **12 layers**; plus **3 audio tracks** (VO, SFX, music).
  12 x 30 = **360 layers per second**.
- If a VO lane is labelled, label it honestly ("VO · AI voice"): lead's call.
- The hidden "JD" bokeh glint (the easter egg) must exist in layer 03.
- Payoff and CTA lines:
  - "Ek frame ki keemat... woh jaanta hai, jis ne use banaya."
  - "Aur jo kehta hai 'editing mein kya hai'... usse yeh bhejo."

**Retention map** (bars at 0, 2.4, 4.8, 7.2, 9.6, 12.0, 14.4, 16.8, 19.2, 21.6, 24.0, 26.4, 28.8, 31.2)

| s | picture change | new information | open loop state | audio event | reason to stay | risk |
|---|---|---|---|---|---|---|
| 0 | f0 hero frame (suit_threequarter, flame rim, embers moving, lockup set, timecode chip 00:00:00:01); 0.4 pause icon | you saw this for 1/30 s | OPENED: what is inside? | VO 0.1 "Yeh frame aap ne palak jhapakte dekha." (to 2.6); soft impact f0; pause click 0.4 | a frame gets stopped | must read as a finished reel frame, not a title card |
| 1 | 0.6-1.0 seams glow; 1.0 panes separate in z | it is built in layers | open | glass creak | the image breaks | - |
| 2 | 2.4 orbit begins | - | open | whoosh_slow | depth | - |
| 3 | panes light one by one; counter 0 to 12 | - | narrowing | ui tick per pane; VO "Lekin is ek frame mein... baarah layers hain." (3.0-5.2) | counting | number = build |
| 4 | 4.8 side-on: 12 panes + "12 LAYERS" | the count | - | sub hit | spectacle | - |
| 5 | settle (cover candidate) | - | - | air | - | 1 s hold is fine |
| 6 | fly-through, back to front; tag "01 · andhera" | names | OPEN #2: which one matters? | VO "Andhera. Dhuaan. Roshni. Chehra." (6.0-8.4) | rhythm | tags >= 34 px |
| 7 | 7.2 tags 02 dhuaan, 03 bokeh | - | open | ticks | - | - |
| 8 | 04 chehra (the flat face pane), 05 rim light | - | open | ticks | honesty | the face pane must not warp |
| 9 | 9.6 tags 08-11 | - | open | VO "Har lafz. Har chamak." (8.8-10.2) | - | - |
| 10 | 07 embers · 140 | - | open | sparkle | - | - |
| 11 | camera slows | - | open | VO "Aur ek layer..." (11.0-11.8) | - | - |
| 12 | **RE-HOOK** 12.0 stop at pane 12 (finish), nearly invisible | - | mini-mystery | VO "...jo aap ko dikhi hi nahi." (11.8-13.2); 0.3 s drop | why does it matter? | - |
| 13 | flick with / without pane 12, x2 | practical value | closing #2 | glitch_short per flick; VO "Iske bina frame zinda nahi lagta." (13.4-15.2) | learn something | <= 3 flips/s, <= 20 % luma change; test ज़िंदा |
| 14 | 14.4 resolves to "with" | - | CLOSED #2 | shimmer | - | - |
| 15 | audio lanes rise under the stack: "awaaz · 3 tracks" | - | open | VO "Aur awaaz ki teen tracks." (15.4-16.8) | - | mild: lanes must move |
| 16 | 16.8 lanes pulse with the real VO envelope | - | open | - | - | - |
| 17 | the stack duplicates into a corridor | - | open | whoosh | scale | pre-flattened sprites (render cost) |
| 18 | corridor recedes | - | open | VO "Ek second mein tees frames." (17.6-19.0) | - | - |
| 19 | 19.2 surge down the corridor; counter 12 to 360 | - | open | slot ticks | build | - |
| 20 | 20.8 "360" lands | the number | open | VO "Yaani har second... teen sau saath layers." (19.6-22.0) | number shock | - |
| 21 | 21.6 flyby | - | open | riser starts | - | - |
| 22 | corridor converges toward the lens | - | max | riser | - | - |
| 23 | panes rush back | - | max | riser | - | - |
| 24 | 24.0 the rush accelerates | - | max | riser | - | - |
| 25 | 25.6-26.4 near-silence | - | max | breath | tension | - |
| 26 | 26.4 SLAM reassembly + exposure push; lockup morphs to EK FRAME KI *keemat*; suit_smirk | - | **CLOSED (79 %)** | sub drop on the downbeat | payoff | - |
| 27 | settle | value | - | VO "Ek frame ki keemat..." (26.8-28.0) | - | - |
| 28 | 28.8 light sweep on the keyword | - | - | VO "...woh jaanta hai, jis ne use banaya." (28.0-29.6) | the quotable line | - |
| 29 | embers swirl | - | - | VO "Aur jo kehta hai, 'editing mein kya hai'..." (29.8-31.6) | send setup | - |
| 30 | 30.2 hidden "JD" bokeh glint (2 frames) | easter egg | - | - | rewatch | must exist in layer 03 |
| 31 | 31.2 end card: J mark, @jawad_mp4, pill "Us dost ko bhejo" | CTA | - | VO "...usse yeh bhejo." (31.6-32.6) | - | - |
| 32 | the lockup cross-fades back to AAP NE ISE *0.03 sec* DEKHA; camera returns to the f0 pose | - | - | swell resolves | - | - |
| 33 | 33.3-33.6 card lifts into frame 0 | - | - | - | seamless loop | - |

**Drop-risk windows:** 15-17 s (audio lanes are less visual: keep them moving). Nothing else over 2.5 s.

**Send sentence.** Editors, designers and creators send it to the friend or relative who says "editing mein kya rakha
hai" because it proves the invisible work without an argument (social currency + pride).

**Comment prompt.** "Is frame mein 'JD' chhupa hai. Mila?" (hidden-frame, drives rewatches; it must exist). Pin the
answer after 24 h.

**Cover:** 5.5 s (side-on stack, `12 LAYERS` + keyword).
**Caption L1 (49):** `Ek frame mein kitni layers? Video editing ka sach`.
**Hashtags:** #videoediting #motiongraphics #behindthescenes #jawadmp4.

---------------------------------------------------------------------------------------------------------------

## 5. Today's build reality (premium but buildable, zero mistakes)

- **Suggested build order:**

  | # | reel | build | Blender | heavy part / mitigation |
  |---|---|---|---|---|
  | 1 | C26 | one parametric frame + review UI | 1 prop (chai glass) | none |
  | 2 | C08 | toolkit planes only | none | the corridor, as pre-flattened sprites |
  | 3 | C02 | UI-led | none: the phone is a `ui.py` mock | - |
  | 4 | C15 | silhouette strips (numpy or a single Blender silhouette set) | optional | - |
  | 5 | C11 | 4-5 props | CRT, desktop tower, keycaps, candle, hand fan | the most work |

  Render: about 18 min per 35 s on one worker at 3 samples, so about 1.5-2 h of final renders plus 1-sample
  previews, `nice -n 10`, at most 2 threads.
- **Single-voice advantage.** In C26 and C02 every other character speaks in text (pins and bubbles). The one AI
  narrator never has to act a second person, and comedy timing lives in the picture, not in TTS delivery.
- **Faces.** The sheet expressions are subtle (suit_shocked is wide eyes with the mouth closed). Every reaction beat
  needs a large headshot (at least 40 % of frame width) plus a snap-zoom and a sting; the face alone will not sell it
  at phone size.
- **Wardrobe spread.**

  | wardrobe | reel | crops |
  |---|---|---|
  | suit | C02 | confused, shocked, neutral, hand-on-chest |
  | suit | C08 | three-quarter, smirk |
  | suit | C11 | profile, smiling |
  | streetwear | C26 | smirk, sunglasses, 3/4 turn |
  | streetwear | C15 | 3/4 turn full body, chin-up gaze |

  C26 and C02 are both comic: C26 stages Jawad small in a lower corner as a reaction cam; C02 stages him large in
  phone glow.
- **VO credits.** Each reel is about 50-80 words. Per-beat takes at about 2.5 credits per ~520 characters, with
  retakes, come to about 40-60 credits for all five, inside the 187 left.
- **Dark-frame QA** (red-team stage): run the frame-0 YAVG/YHIGH probe on every reel. Watch the C11 torch stretch and
  C15 noir at 360 px.

---------------------------------------------------------------------------------------------------------------

## 6. Posting and testing (advice, not a forecast)

- **Order:** C26 (broadest send, tightest loop) → C11 (strongest stop) → C08 (authority, process proof) → C02 (ahead
  of the Nov-Dec shaadi season, when "beta kya karte ho" peaks) → C15. Two per week.
- **Time:** Tue-Thu at 7:00 PM PKT / 7:30 PM IST as a starting hypothesis (vendor data, low confidence,
  `trends_india_pakistan.md` P1).
- **A/B:** post hook A publicly and hook B as a Trial Reel (body identical; cut where both share the picture). Judge
  skip rate first, then sends per reach, then the retention curve, against Jawad's own median.
- **Cut-downs:** a 15 s cut-down per reel is worth testing later. viral.app's single-vendor data puts 16-30 s and
  31-60 s Reels below <= 15 s for breakout rate (2026-10-02).

---------------------------------------------------------------------------------------------------------------

## 7. Platform claims re-checked today (2026-10-08) and what I could not verify

| claim | status today | source (date) |
|---|---|---|
| Watch time, likes per reach and sends per reach are the top Reels signals; sends weigh more for non-followers | Repeated in Sep 2026 coverage, but it traces to Mosseri's Jan 2025 statement. **No primary 2026 Mosseri post found**: secondhand. | [kompozy](https://kompozy.io/news/instagram-mosseri-ranking-signals-guidance) (2026-09-25), [posteverywhere](https://posteverywhere.ai/blog/how-the-instagram-algorithm-works), [socialync](https://www.socialync.io/blog/adam-mosseri-shares-instagram-algorithm-2026), [Social Media Today](https://www.socialmediatoday.com/news/instagram-shares-algorithm-insights-2025/738034/) (2025-01-22) |
| A send is worth 3-5x a like | **Unverified**; no original source | same searches |
| Realistic AI voice / imagery of a person should carry Meta's "AI info" label | Consistent across guides. One outlet says that since 30 Apr 2026 Reels with *substantially* AI voice need the label and unlabelled detected content is demoted (**single source**). An "AI-generated profile" label exists for accounts featuring AI-generated people (Sep 2026, secondhand). | [howsociable](https://howsociable.com/news/2026/04/instagram-ai-content-labels-required-april-2026) (2026-04), [techwyse](https://www.techwyse.com/?p=78112), [gradually.ai](https://www.gradually.ai/en/instagram-ai-label/), [kompozy guide](https://kompozy.io/guides/instagram-ai-content-detection-and-labeling) |
| Trial Reels need 1,000+ followers and a public account | Vendor + press. **Jawad's follower count is unknown**, so check eligibility before planning the A/B. | `trends_india_pakistan.md` A6 |
| ~55-60 caption characters show in the Reels viewer | Vendor, unverified. All five L1 lines here are 48-55 characters. | `hooks_retention_captions.md` §1 |
| Vlad mispronounces फ़ as "p" | **Unverified by ear.** The casting take's ASR read लाइफ़ as "लाइप"; it may be an ASR error. Test before the full VO. | `eval_vlad.json` (2026-10-08) |

**AI disclosure (open question for the lead; flagged, not skipped).** All five reels use a realistic synthetic
Hinglish voice. Jawad's character sheets may themselves be AI-generated (`trends_india_pakistan.md` §13 calls the
likeness "AI-generated character-sheet likeness"). Recommendations:
- Apply the in-app AI disclosure on all five.
- Never caption the voice as "meri awaaz".
- Keep the narrator as "har editor / hum", not as a first-person account of Jawad's private life.

---------------------------------------------------------------------------------------------------------------

## 8. Open questions for the lead

1. Accept C26 (my concept) in slot 1, or fall back to C09 (the same `inferno` slot and client theme)?
2. "Mummy" (cross-border neutral) or "Ammi" (PK-leaning, Jawad's register) in C02 and C26?
3. AI-info label on all five? Would Jawad accept a visible "VO · AI voice" lane in C08 (honest process proof)?
4. Does @jawad_mp4 have 1,000+ followers (Trial Reels)? No DM automation means no keyword CTAs.
5. Fictional chai brand name for C26: search-check it before render so it is not a real business.
