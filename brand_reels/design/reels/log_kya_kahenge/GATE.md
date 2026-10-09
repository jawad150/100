# GATE: Reel 5 · C15 · Log Kya Kahenge: concept and script gate (viral-strategist, r1)

Date 2026-10-08 · Author: viral-strategist · Stage: concept + script (before any TTS credit is spent) · Status: **FIX**

Read for this gate: `SLATE.md` §0, §2, §3.5 (lines 312-363), §4, §5 (series bible); `BRIEF.md` (all sections); `SCRIPT.md` and
`script.json` (script v1); `MUSIC_log_kya_kahenge.md`; `SHARED_REQUESTS.md`; `panel_viral.md` §0 and §4.4; research
`hooks_retention_captions.md` §0-3, §5-7; the `jawad-brand-reels` skill; `prior/prior_covers.jpg` and the layout proofs
`workspace/jawad_reels/log_kya_kahenge/layout_proofs/p1, p4, p5` (viewed). Measured here: the end-card sub alternatives
with `T.measure` (house style `jw_body`), the orbit yaw at each V3 word (`out_cubic`), the caption L1 character count and the
V6/V7 durations at 1.00-1.10x. No picture exists yet, so this gate judges the plan; the still gate (BRIEF §7.4) and the preview
red-team judge the pixels.

---------------------------------------------------------------------------------------------------------------

## 0. Verdict on one screen

**FIX.** Every gate passes (Hook 8, Share 9, Truth pass, Brand 8), and none of the fixes needs a re-concept. The script may go to
TTS once fixes 3-5 are folded into `SCRIPT.md` / `script.json` (they change two lines' words (V4, V7), three onsets or windows (V5, V6, V7) and the speed plan,
not the number of takes). Fixes 1-2 are picture and brief changes; they can run in parallel with the takes.

| rank | time | fix (short) | owner |
|---|---|---|---|
| 1 | 0.0-0.6 s | make the head-snap readable at phone size without the eye dots: tonal flip between the two states, plus a 360 px check in the still gate | creative-director |
| 2 | 3.2-8.8 s | judgement lines: speed up and escalate instead of four identical 1.6 s fly-outs over 5.6 s with no VO | creative-director |
| 3 | 26.0-32.0 s | after the payoff: V6 window to 29.10 s, V7 onset at 31.6 s, both at 1.00-1.06x; this closes the 3.4 s VO gap after the payoff | hinglish-scriptwriter (+ creative-director for the windows) |
| 4 | 31.6-35.2 s | V7 + end-card sub: "jise 'log' ka *darr* rokta hai" (no gender, echoes the hook's *darr* across the seam) | hinglish-scriptwriter (+ creative-director, SLATE copy) |
| 5 | 19.3-25.5 s, 0.1-2.9 s | slack and contingencies: V4 fallback by default, V5 onset on the bar-7 downbeat, explicit V1 and V5 overrun rules | hinglish-scriptwriter |

Sign-offs that the script asked for (SCRIPT §0 and §7): **V3 cut approved**; **V6 fallback approved**; **hide all of V1B** in hook
B's captions; V2 keeps 15 words; nothing in the script makes a claim about Jawad (truth pass).

---------------------------------------------------------------------------------------------------------------

## 1. Concept and hook scores (0-10, one line of evidence each)

| axis | score | evidence |
|---|---|---|
| Hook | **8** | All three channels land by 0.6 s: the head-snap wave runs 0.2-0.6 s, `LOG KYA / kahenge?` is readable at 0.6 s and settled at 0.83 s, and the VO starts at 0.10 s ("darr" at ~0.94 s, the full phrase spoken by ~2.49 s). Two points come off. The snap's legibility at 24 mm is unproven: heads are 22-61 px, and eye discs of r = 0.035 × head width are 1.5-4 px across (fix 1). The spoken line is also a familiar motivational framing that the viewer may pattern-match to the genre; hook B hedges that. |
| Relatability | **10** | "Log kya kahenge" is the shared Hindi/Urdu phrase for fear of social judgement (Wikipedia, read 2026-10-08: a 1982 Indian film and two Pakistani TV series carry the title). The judgement lines ("Yeh bhi koi kaam hai?", "Naukri kab karoge?") are what desi creators actually hear. |
| Share trigger | **9** | An indirect message plus inspiration: the viewer sends "nobody is really watching, go" without having to say it. The CTA names one person ("us dost ko"). One point off: "ruka hai" is grammatically masculine (fix 4). |
| Novelty | **7** | The theme is crowded (motivational "log kya kahenge" reels). New here: a crowd that is itself a 2.5D trick, exposed by the camera, from an editor's eye; the edge-on line of light; "Log busy hain... apne 'log kya kahenge' mein". It shares no layout with his covers (Yaadein, Younger Self, OpenArt) or the Genjutsu reel. |
| Truth | **PASS** | No facts about Jawad, no counts, no "main". Every claim is a metaphor inside the reel ("cardboard", "peeche baithe hain") or a rhetorical idiom ("sab se bara darr"). AI label ON (synthetic voice). |
| Loop | **8** | The visual reset is strong: flaps rise, heads face away, the floodlight returns and frame 0 is the same pose, so the head-snap replays. The audio seam is clean (the score measured 0.54 dB across 35.2 → 0.0). The sentence loop is thematic only ("...ruka hai" → "Sab se bara darr"); fix 4 makes it verbal (*darr* → *darr*) for 9. |
| Feasibility | **7** | No Blender: a procedural numpy crowd on `K.Scene` planes, one in-shot orbit and a masked O6. The real risk is whether the crowd reads as people, and the still gate plus reserve C01 already cover it. Two hook renders (A, and B's 0-3.0 s range). |
| Brand | **8** | Serif keywords *kahenge?* / *busy* / *bhejo*, the flame held back until the warm turn (noir_ember), the `@jawad_mp4` end card. S3-01 (JD alone in the arena) stays clear of his "Meeting my younger self" cover: no spotlight cone, no light pool, crowd context, the flat floodlight (cover viewed). |

**Gates:** Hook ≥ 8 ✓ (8, provided fix 1 passes the still gate) · Share ≥ 7 ✓ · Truth pass ✓ · Brand ≥ 7 ✓.

---------------------------------------------------------------------------------------------------------------

## 2. Hook

### 2.1 Three-channel test (SLATE: spoken ≤ 7 words, landing by 2.7 s; on-screen ≤ 6 words)

| channel | Hook A (public) | Hook B (Trial Reel, frames 0-89) |
|---|---|---|
| visual | f0: lit tiers, heads turned away, caps already rising; snap wave 0.2-0.6 s from the centre out, amber catch-light eyes; first change 0.2 s ✓ (≤ 1.0) | f0: 135 mm rows **already staring**, locked; first change is the caps rise. The O2 haze wipe to the wide runs 1.9-2.77 s ✓ |
| on-screen text | `LOG KYA / kahenge?`: 3 words ✓, readable 0.6 s, gone by 2.9 s | `YEH / log / HAIN KAUN?`: 4 words ✓, settled 0.83 s, gone by 2.1 s |
| spoken | "Sab se bara darr, log kya kahenge.": **7 words** ✓, onset 0.10 s ✓, est. end 2.485 s ✓ (worst case 2.83 s, see fix 5) | "Yeh 'log'... asal mein hain kaun?": **6 words** ✓, onset 0.10 s, est. end 2.094 s ✓ (worst case 2.30 s) |
| muted | works: picture + lockup + captions "Sab se" · "bara *darr*" (2 blocks) | works: the lockup carries the whole question (hide all V1B captions, see §4) |
| search phrase spoken in the first 3 s | "log kya kahenge" spoken 1.33-2.49 s ✓ | "log" spoken at 0.39 s; the phrase itself is not spoken (acceptable for the Trial) |

### 2.2 Hook lab (Gap, Specificity, Fit, Voice 0-2; Truth*, Pull* pass/fail)

| # | mechanism | spoken (words) | on-screen | Gap | Spec | Truth* | Fit | Voice | Pull* | /8 |
|---|---|---|---|---|---|---|---|---|---|---|
| **A** | identity question + the search phrase | "Sab se bara darr, log kya kahenge." (7) | LOG KYA / *kahenge?* | 2 (with the stare: who are they?) | 1 | P | 2 | 2 | P | **7** |
| **B** | curiosity gap | "Yeh 'log'... asal mein hain kaun?" (6) | YEH / *log* / HAIN KAUN? | 2 | 1 | P | 2 | 2 | P | **7** |
| C | rhyme / proverb | "Sab se bara rog: kya kahenge log." (6) | LOG KYA / *kahenge?* | 1 | 1 | P | 2 | 2 | P | 6: I could not verify that the couplet is widely known (search 2026-10-08), and it adds a cliché risk |
| D | stakes callout | "Kitne saal 'log' ke liye ruke rahoge?" (6) | KITNE SAAL / *ruke* / RAHOGE? | 1 | 1 | P | 2 | 2 | P | 6: lecture tone, against the brief's "never a lecture" |
| E | POV | "POV: tumhara sapna... aur poora stadium dekh raha hai." (8) | POV: / *sapna* / VS STADIUM | 2 | 1 | P | 1 | 1 | P | 5 |
| F | result first | "Yeh crowd asli nahi hai." (5) | YEH CROWD / *asli* / NAHI | 2 | 2 | P | 2 | 2 | **F** | spends the 16 s reveal in the first second |
| G | contrarian | "Log kuch nahi kehte." (4) | LOG KUCH / *nahi* / KEHTE | 1 | 1 | P | 2 | 2 | **F** | spoils the payoff |
| H | number | "Paanch hazaar log. Ek hi sawaal." (6) | *5,000* LOG | 2 | 2 | **F** | 2 | 2 | P | banned: no crowd counts |
| I | send-first callout | "Jo 'log' ki wajah se ruka hai... yeh dekho." (8) | — | 1 | 1 | P | 1 | 2 | P | 5: repeats the CTA and asks before it gives |

**Recommended: A** (the phrase is the share hook and the search term, and the head-snap makes "log" literal by 0.6 s).
**A/B alternate: B** as the Trial Reel (frames 0-89 differ, splice f90). B hedges A's motivational-cliché risk with a real
question, and its 135 mm framing makes faces readable. Optional, creative-director's call: give B its own snap (heads away
on f0, turning f3-f12 at 135 mm, where heads are ~100 px) instead of "already staring". That puts motion on frame 0 and
makes the strongest version of the device the Trial's opening. Judge skip rate first, then sends per reach.

---------------------------------------------------------------------------------------------------------------

## 3. Compliance with the SLATE §2 fixes and the series bible

| rule | status | evidence |
|---|---|---|
| §2.7 no floodlight clunk at the open; one clunk only, at 25.6 | ✓ | BRIEF §11: f0 = `impact_soft` lp 1100; the clunk stack (`ui_click` + `impact_soft` + `sub_drop`) only at f768; QA §18 asserts exactly one |
| §2.7 dim catch-light eyes AMBER ≤ 1.5× linear | ✓ (but see fix 1: at 24 mm the eyes alone are too small to carry the snap) | BRIEF §1, §7.1 |
| §2.7 hook B `YEH *log* HAIN KAUN?`, no crowd count | ✓ | BRIEF §2 H2a/H2k/H2b; SCRIPT V1B |
| §2.7 payoff keyword *busy*, not "apni kahani khud likho" | ✓ | BRIEF §8 P1 |
| §2.7 no first-person "Main editor hoon" | ✓ | SCRIPT narrator "hum" + "tum" imperatives; no "main/mera/meri" in 70 tokens |
| §2.6 end card ≥ 4.0 s, settled hold ≥ 1.5 s | ✓ | 31.2-35.2 s; settled at f992 (33.05 s; EndCard settle 1.85 s) and held to f1045 = **1.77 s** (inside the 1.5-2.5 s target) |
| §2.11 / §5.1 CTA true, imperative, ≤ 5 words, never "Comment JD" | ✓ | `US DOST KO / *bhejo*` (4 words) |
| §5.1 VO onset ≤ 0.3 s | ✓ | 0.10 s (f3) in A and B |
| §5.1 one drop-out, at the reveal | ✓ | 15.2-16.0 s (digital zero in the score, measured) |
| §5.1 ≤ 2 text blocks | ✓ planned | the hook (lockup + caption), judgements (front + receding line, no captions), J4 + caption 8.8-9.4, payoff (lockup + caption), end card (card only) |
| §5.1 caption L1 48-55 characters with the search keyword | ✓ | "Log kya kahenge? Har creator, har editor ka darr" = **48** characters (counted) |
| §5.1 cover keyword inside y 240-1680 | ✓ | f45; keyword ink y 476-682 |
| §5.2 one value per reel (emotion, look, mechanism, device, family, BPM, faces) | ✓ | fear → liberation, noir_ember, identity question, cardboard reveal, organic (O6 ★, O2), 75 BPM, street threequarter + chin-up |
| banned: India-Pakistan flashpoints, cricket, religious/regional markers, currency | ✓ | an amphitheatre with no pitch, flags or team colours; silhouettes with no headwear or markers; "Paise milte hain?" names no currency |
| banned: a lone figure under a top spotlight, a spotlight-clunk cold open | ✓ guarded | S3-01: the same flat floodlight as the stands, no cone, no pool; open already lit |
| AI disclosure | flagged ✓ | "AI info" ON (synthetic voice; the sheets may be AI-generated); BRIEF §16 |

---------------------------------------------------------------------------------------------------------------

## 4. Script audit (SCRIPT v1 / script.json)

**Word budget against DUR.** 64 words (A) / 63 (B) in 35.2 s. That is 1.8 words/s overall, against the research budget of
~80-90 for 34 s. The low total is by design: 3.2-8.8 s is read, not spoken, and 28.8-31.2 s is a silent gag. The total is not
the problem. The distribution is: the lines after the reveal all sit at the 1.10x ceiling with +0.01 to +0.17 s of slack (V4
+0.08, V5 +0.01, V6 +0.02, V7 +0.17), while the narration is silent for 6.3 s after the hook and 3.4 s after the payoff.
Fixes 3 and 5 move time to where the words are.

| line | window | words | est. end / slack @1.10x | keyword (serif / caption) | cross-border | truth | gate note |
|---|---|---|---|---|---|---|---|
| V1 | 0.10-2.70 | 7 | 2.485 / +0.22 (worst 2.83) | *darr* | ✓ (house "bara") | rhetorical idiom ✓ | add an overrun rule (fix 5) |
| V1B | 0.10-2.70 | 6 | 2.094 / +0.61 | *kaun* | ✓ | ✓ | hide all of V1B in the captions: the lockup holds the whole question until 2.1 s and "hain kaun?" is spoken ~1.7-2.1 s |
| V2 | 8.80-14.83 | 15 | 14.441 / +0.39 | *zindagi*, *edit*, *video*, *nahi* (one per chunk, ≤ 2 per shot) | ✓ | ✓ | the best line in the reel: editor metaphor plus a punchline on the head tilt at 12.8 |
| V3 | 16.37-19.13 | 5 | 19.003 / +0.13 | *flat*, *Cardboard* | ✓ | metaphor ✓ | **cut approved** (below) |
| V4 | 19.33-22.30 | 9 | 22.219 / +0.08 | *phone* | ✓ | metaphor ✓ | record the 8-word fallback by default (fix 5) |
| V5 | 22.50-25.40 | 8 | 25.394 / +0.01 | *busy*, *kahenge* | ✓ | ✓ | the quotable line, planned at the speed ceiling; move the onset to 22.4 (fix 5) |
| V6 | 26.00-28.67 | 9 | 28.643 / +0.02 | *nazar*, *'log'* | ✓ | ✓ | **fallback approved** (drops "Aur", avoids "aur ... aur"); window to 29.10 (fix 3) |
| V7 | 32.00-35.13 | 11 | 34.961 / +0.17 | *bhejo* | ✓ ("ruka" is masculine) | ✓ | new copy + onset 31.6 (fixes 3, 4) |

**V3 cut ("Gaur se dekho." removed): approved.** It loses no meaning, and the remaining line syncs with the orbit (`out_cubic`, yaw
measured): "Yeh" 16.37 s at 22°, "crowd" 16.66 s at 35°, ***flat*** **16.96 s at 46°** (the cards are visibly thinning),
"hai" 17.25 s at 54°, ***Cardboard*** **18.20 s at 68°** (the backs, tape and struts are on screen). The instruction would have
landed after the braam had already started the reveal, so it had stopped working as an instruction. Keep "Gaur se dekho:" in IG
caption line 3. Do not move it into the 15.2-16.0 drop-out: that silence is the reel's only pattern break and should stay empty.

**V6 fallback ("Kisi aur ki nazar mein, hum bhi 'log' hain."): approved.** It reads better and lands the stressed "Ki-" on the 8th.

**Keyword per line:** every line has one (V1 *darr*, V1B *kaun*, V2 *edit*, V3 *Cardboard*, V4 *phone*, V5 *busy*, V6 *'log'*, V7
*bhejo*). The payoff keyword *busy* is spoken at ~22.70 s and shown at 25.83 s (the lockup keyword rises), so the reel says it
twice, 3 s apart. During the payoff the lockup reads `LOG busy HAIN.` while V6 is heard. That is acceptable: the lockup titles the
previous line, captions carry V6 for muted viewers, and "LOG ... HAIN" echoes "'log' hain". Fix 3 gives V6 room so it does not
fight the keyword settling at 26.43 s.

**Pronunciation:** SCRIPT §6 is complete and testing T0 first is right. Fix 4 removes वजह (risk 7) and adds only words already in
the hook (डर). The z/f sounds (बिज़ी, नज़र, फ़्लैट, फ़ोन, ज़िंदगी) need a human ear, because ASR normalises nuktas. That is an open
question for the lead.

---------------------------------------------------------------------------------------------------------------

## 5. Retention map (hook A as planned today; the fix numbers show where each risk is handled)

| s | picture change | new information | open loop state | audio event | reason to stay | risk |
|---|---|---|---|---|---|---|
| 0 | f0 lit tiers, heads away, caps rising; 0.2-0.6 head-snap wave from the centre out | the crowd is watching *you* | **OPENED**: who are these "log"? | `impact_soft` f0 (loop landing); VO "Sab" 0.10; swish 0.3; whisper swell peak 0.4; shimmer 0.6 | the uncanny stare + the phrase | snap legibility at 24 mm (fix 1) |
| 1 | keyword `kahenge?` settles 0.83; cards sway; dust | "the biggest fear" | open | "bara *darr*," ~0.5-1.2; "log" 1.33 | voice and text say the same thing | low |
| 2 | stare holds; lockup exits 2.53-2.9 | the phrase spoken in full | open | "kya kahenge." ends ~2.49 | — | 1.3-2.5 static stare (1.2 s, fine) |
| 3 | 3.0 splice; 3.2 J1 `Yeh bhi koi / kaam hai?` flies out of the crowd | what "log" say #1 | open | whisper burst 3.2; whoosh_by 3.47; tension_drone enters | recognition ("yeh mujhe bhi bola tha") | the narration stops until 8.8 |
| 4 | J1 front; 4.8 J2 `Paise milte hain?` arrives, J1 recedes | #2 | open | burst 4.8; whoosh 5.07 | recognition | — |
| 5 | J2 front | — | open | drones rising | — | — |
| 6 | 6.4 J3 `Log hasenge.` | #3 | open | burst 6.4; whoosh 6.67 | — | **habituation**: same device, same 1.6 s tempo, no VO (fix 2) |
| 7 | J3 front | — | open | — | — | **DROP RISK 6.4-8.8** (fix 2) |
| 8 | 8.0 J4 `Naukri kab karoge?`; 8.8 captions return | #4; the narrator returns | open | burst 8.0; whoosh 8.27; V2 8.8 "Hum apni..." | the narrator's turn | — |
| 9 | 9.6 O2 haze carries J4 away → JD alone, small, crowd behind; level pedestal rise starts | "we edit our lives for them" | open | whoosh_slow 9.6; "*zindagi*" 9.33 | **re-hook 1**: new world, JD appears | — |
| 10 | rise; O2 clears (impact_soft 10.2) | the editor metaphor | open | "unke hisaab se *edit* karte hain..." 9.87-11.47 | wry recognition | — |
| 11 | rise continues; JD idle breath | — | open | "hain..." pause ~11.5-12.1 | — | mild: a slow move plus a VO pause (trim the ellipsis to 0.30 s as SCRIPT allows) |
| 12 | 12.8 hard cut to 135 mm rows; every head tilts 9° in sync | punchline | open | "jo poori *video*" 12.1-12.74; board creak + impact_soft 12.8 | laugh beat | — |
| 13 | heads tilted (one 2 f late) | "...dekhte bhi nahi" | open | "dekhte bhi *nahi*." to ~14.44 | — | — |
| 14 | heads straighten 14.6-15.0 | — | open | VO ends ~14.44 | — | — |
| 15 | 15.2 **DROP-OUT**: the crowd leans in 1.00 → 1.025 | something is coming | open, tension at its peak | reverse_swell into 15.2; music gated; heartbeat 15.6 | **re-hook 2** (silence) | — |
| 16 | 16.0 **REVEAL**: the orbit is already moving, the rows thin | the crowd is flat | **TURNING** | braam + impact_big 16.0 (loudest); the pulse starts; "Yeh crowd *flat* hai." 16.37-17.5 | the reveal | — |
| 17 | slivers; cardboard backs, tape, struts appear | — | turning | board flex 17.6 | detail | — |
| 18 | yaw 68°: backs readable | "Cardboard." | first answer | "*Cardboard*." 18.2 | — | — |
| 19 | 19.2 edge-on: lines of light; real people behind with phones (the single image) | the real people sit behind | turning | whoosh 19.2; V4 19.33 | the anchor image | — |
| 20 | 20.0-20.8 focus pull to one scroller | they are in their phones | turning | "peeche baithe hain," | — | — |
| 21 | the scroller's glow flickers; 21.33 one person looks up for 6 f (Easter egg); taps 21.6/21.8/22.0 | — | turning | "apne *phone* mein." ~21.15-22.2 | rewatch detail ("did you see him look up?") | — |
| 22 | 22.4 O6: the cards burn from the lowest tier up | the fear burns away | closing | crackle 22.4; V5 "Log *busy* hain..." 22.5-23.3 | the quotable line | V5 at the 1.10x ceiling (fix 5) |
| 23 | 23.6 O6 complete; embers rise | "...apne 'log kya kahenge' mein" | closing | impact_soft + sub_drop 23.6 in the pause; part 2 23.7-25.4 | — | +0.01 s to the clunk guard (fix 5) |
| 24 | busy rows; the last embers die | — | closing | hats on the off-8ths | — | — |
| 25 | 25.6 **PAYOFF**: cut to JD's chin-up gaze; warm low light (the first flame); `LOG / busy / HAIN.` | the "log" are busy | **CLOSED (72.7 %)** | the one clunk 25.6; warm pad Bbmaj7 | liberation | — |
| 26 | keyword settles 26.43; underline 26.87 | "in someone else's eyes..." | second turn | V6 26.0 "Kisi aur ki *nazar* mein," | the twist begins | V6 +0.02 s slack (fix 3) |
| 27 | push-in 1.00 → 1.03 | "...we are 'log' too" | **CLOSED (the story loop)** | "hum bhi *'log'* hain." ~27.44-28.64 | the twist | — |
| 28 | lockup exits 28.43; 28.8 cut to the warm wide: emptied stands, phone dots | — | — | VO ends ~28.64; impact_soft 28.8 | — | post-payoff exit starts (fix 3) |
| 29 | 29.2 the last card tips; 29.6 tap | the gag | — | swish 29.2; card_slide + impact_soft 29.6 | bonus laugh | — |
| 30 | hold on the wide; nothing new | — | — | pad; EP D4 30.4 | — | **DROP RISK 29.6-31.6** (no VO since 28.64 s; fix 3) |
| 31 | 31.2 end card: the world dims; JD ring draws 31.3; CTA caps rise 31.55 | the ask | — | swish 31.3; shimmer 31.77; glass_tap 31.95 | the CTA | — |
| 32 | 32.0 flaps rise row by row; sub 32.35 | send it | **RE-OPENING** (the crowd is coming back) | V7 32.0 "Us dost ko *bhejo*..."; card_slide 32.25 | the send | — |
| 33 | card settled 33.05; light hands back toward the floodlight from 33.6 | — | re-opening | card_slide 33.21/33.69; whisper wall fades in from 33.6 | — | — |
| 34 | heads away, crowd refilled = the frame-0 pose | — | — | V7 ends ~34.96 | the replay set-up | — |
| 35 | 34.83-35.2 the card exits into the exposure push → f0 | — | **LOOP** | reverse_swell ends on 35.2 → impact_soft f0 | the head-snap again | — |

**Visual-change gaps.** Counting discrete events plus the caption-chunk changes, the largest gap is 0.83 → 2.53 s (1.7 s) and the
next is 29.6 → 31.2 s (1.6 s). The 9.6-12.8 s pedestal and the 16.0-19.2 s orbit are continuous moves. **No gap exceeds 2.5 s.**
Tighten BRIEF §18's QA line from "events ≤ 3.0 s apart" to "a visible change ≤ 2.5 s apart" (the series rule): BRIEF §5's own
event list has f6 → f96 = 3.0 s, which passes only because the lockup settle and exit sit in between.

**Drop-risk windows (3 s with no reason to stay):** **6.4-8.8 s** (the third and fourth repeat of one device with no narration:
fix 2) and **29.6-31.6 s** (after the payoff and the gag, before the CTA: fix 3). A mild one at 10.8-12.4 s (JD small, slow
rise, ellipsis pause): trim the V2 ellipsis to 0.30 s as SCRIPT already allows.

**Open loop and loop bridge.** The loop opens by 0.6 s ("who are these log?": the stare). It turns at 16.0-19.2 (cardboard,
45-55 %), closes at 25.6 s (`LOG busy HAIN.`, 72.7 %) and closes a second time at ~28 s ("hum bhi 'log' hain", ~80 %): a
layered loop, closed after 70 % ✓. The re-hooks fall at 12.8 (tilt), 15.2 (drop-out) and 16.0 (reveal), inside 12-18 s ✓. The
bridge: the flaps rise and the heads turn away (the frame-0 pose), the floodlight returns, the drone and whisper wall come back at
frame 0's level, and a reverse swell resolves into the f0 hit. Rewatch triggers: the scroller who looks up (21.33 s, 6 f), the
leaning narrow card in row 6, the seat holding only a phone glow, the late-tilting head.

---------------------------------------------------------------------------------------------------------------

## 6. Share, comment, packaging

- **Send sentence:** "A desi viewer (student, creator, anyone with a plan on hold) sends this to the one friend or sibling who keeps
  postponing the channel, the career switch or the thing they love because of 'log kya kahenge', because it says 'nobody is
  really watching, go' without them having to say it." Trigger: indirect message + inspiration (research §3.7 #2 and #7).
- **CTA:** `US DOST KO / *bhejo*`, spoken once on the end card ✓. One ask: the comment prompt lives in the pinned comment, not in
  the caption ✓.
- **Comment prompt (pinned by @jawad_mp4):** "Agar 'log' kuch na kehte, toh tum kya karte? Ek lafz mein." ✓ (an opinion, low
  friction, one word; "lafz" is understood on both sides). No keyword CTA (no DM automation).
- **Cover:** **f45 (1.5 s)** of version A, the staring stadium + `LOG KYA / *kahenge?*`, keyword ink y 476-682 inside the 3:4
  crop y 240-1680 ✓. At a 210 px tile the keyword is ~136 px wide (readable). The 86 px caps fall to ~17 px, borderline,
  so check the downscale at 210 px and 240 px. Open for the lead: the five covers' keyword bands are not at one common height
  (research §6.5 grid rhythm).
- **Caption line 1:** "Log kya kahenge? Har creator, har editor ka darr" (48 characters ✓, the search phrase first, "creator / editor"
  for the page's niche). Line 4 follows fix 4: "Us dost ko bhejo jise 'log' ka darr rokta hai." Hashtags: #logkyakahenge #contentcreator
  #editorlife #jawadmp4 (4 ✓). An optional 5th is #videoediting for the page's search niche.
- **Audio:** original VO + SFX + score ✓ (no trending track; mix B is ready for an in-app song). Name: "Original audio · Log kya
  kahenge · @jawad_mp4" ✓.
- **AI label:** ON (synthetic voice; the character sheets may be AI-generated) ✓. This stays an open question for the lead to
  confirm at upload.

---------------------------------------------------------------------------------------------------------------

## 7. Fixes, ranked by expected retention impact

### Fix 1 · 0.0-0.6 s · owner **creative-director** (BRIEF §7.1 front texture, §7.4 still gate)
- **Evidence:** at `CAM_WIDE`, heads are 22 px (row 9) to 61 px (row 0) (BRIEF §7.1). The eye discs (r = 0.035 × head width)
  come to ~1.5-4 px across, and both states use the same grey (`mix(SMOKE, ASH, 0.35)`). So the snap is carried almost
  entirely by sub-5 px amber dots. At a 360 px phone tile they fall below a pixel, and the IG encode smears them. The head-snap
  is the thumb-stopper. If it reads as "a grey texture flickered", hook A loses its visual channel.
- **Change:**
  - Give the states a **tonal flip**. Turned = a darker hair mass (head ×0.75-0.8 luminance, a darker crown). Front = a
    lighter face plate (+30-40 % luminance on the face oval, still ≤ ASH) + the eyes. The wave then reads as a sweep of
    heads going dark → light, even where the eyes vanish.
  - Clamp the eye-disc radius to ≥ 1.5 px on rows 0-5 (AMBER stays ≤ 1.5× linear).
  - Add to the §7.4 gate: stills at **0.10 s and 0.70 s**, each also downscaled to 360 px wide. The snap must be obvious
    there: mean head-pixel luma changes ≥ 15 % between the two, and frame 0 reads as a crowd, not a texture.
  - If it still fails, frame hook A's wide tighter (focal 1280 → ~1600 px) so the front rows' heads reach ~75 px.

### Fix 2 · 3.2-8.8 s · owner **creative-director** (BRIEF §5, §8 J1-J4, §11 rows 5-6)
- **Evidence:** four judgement lines use the identical fly-out at a fixed 1.6 s interval while the VO is silent from 2.49 s to
  8.8 s (6.3 s). This is the steepest part of a retention curve, and by the third repeat (6.4 s) the device has become
  predictable.
- **Change:**
  - **Accelerate and escalate.** J1 at 3.2 (f96), J2 at 4.8 (f144), **J3 at 6.0 (f180)**, **J4 at 7.2 (f216)**, all on the
    8th grid. J4 holds as the last and loudest line until the O2 at 9.6, with V2 joining at 8.8.
  - Each arrival is faster: 10 / 8 / 6 / 6 f to the hold depth, `out_expo`.
  - The whisper bursts step -10 / -8 / -6 / -4 dB.
  - The crowd leans in 1.00 → 1.03 across 3.2-9.6 (sprite scale; the camera stays locked).
  - Keep ≤ 2 legible lines. Move the matching cues (whisper_burst and whoosh_by) with the lines.
  - J4 stays at 84 px: it is already 822 px wide, so it does not escalate by size.

### Fix 3 · 26.0-32.0 s · owner **hinglish-scriptwriter** (+ creative-director for BRIEF §5/§9 windows)
- **Evidence:** V6 ends ~28.64 s with +0.02 s slack at 1.10x, and V7 does not start until 32.0 s. The result is a **3.36 s gap
  with no VO** right after the payoff, broken only by the tip and tap at 29.2-29.6 s. That is the classic post-payoff exit.
  V7 also lags the CTA text: the caps rise at 31.55 s, but "bhejo" is spoken at ~32.6 s. V6 and V7 are cast as "soft
  realisation" and "warm, direct", and the speed ceiling works against both.
- **Change:**
  - **V6 window end 28.667 → 29.10 s.** The line may cross the f864 cut into the S6-01 wide, where "hum bhi 'log' hain" plays
    over the stands full of phone-lit people, a picture match. Stay ≥ 0.1 s clear of the swish at 29.2.
  - Record V6 at 1.04-1.06x (est. 2.74-2.79 s → ends 28.74-28.79 s).
  - **V7 onset 32.0 → 31.6 s (f948)**, so "Us dost ko *bhejo*" is heard while the CTA caps and keyword rise (31.55-32.3).
    Record at 1.00-1.06x, last word ≤ 35.10 s. The whisper-wall swell and the card's 0.8 s reverse swell carry the
    remaining ~0.5 s into frame 0.
  - The VO gap after the payoff drops from 3.36 s to ~2.8 s, and the silent gag stays silent.
  - The music-supervisor's EP duck window moves with V7 (the C4 at 31.2 now sits under the VO).

### Fix 4 · 31.6-35.2 s · owner **hinglish-scriptwriter** (+ creative-director: this is SLATE §3.5 copy)
- **Evidence:**
  - "Us dost ko bhejo jo 'log' ki wajah se ruka hai" is grammatically masculine ("ruka"). The people most held back by "log kya
    kahenge" are as often sisters and female friends, so a gender-neutral line widens the send target at no cost.
  - The current loop is only thematic.
- **Change:**
  - V7 = **"Us dost ko bhejo jise 'log' ka darr rokta hai."** DEV **उस दोस्त को भेजो जिसे 'लोग' का डर रोकता है।** That is 10
    words and 13 syllables, against 11 and 14 today.
  - End-card sub = **`jise 'log' ka darr rokta hai`**, measured with `T.measure(..., 'jw_body')`: **632.8 px at 50 px** (x
    224-856, 74 px clear of x 930) and 708.7 px at 56 px (x 186-894, 36 px clear). Keep the 50 px local override.
  - Effect on the loop: "...ka **darr** rokta hai." → frame 0 "Sab se bara **darr**, log kya kahenge." That is a verbal sentence
    loop on the same word.
  - It drops वजह (pronunciation risk 7) and adds only डर (already in the hook).
  - The same edit goes into IG caption line 4, BRIEF §2 E1s/V7, §15 (V7 stays hidden) and the token table (10 tokens; the
    caption keyword stays *bhejo*).

### Fix 5 · 19.3-25.5 s and 0.1-2.9 s · owner **hinglish-scriptwriter**
- **Evidence:** V4 (+0.08 s) and V5 (+0.01 s) are planned at the 1.10x ceiling. V5 is the quotable line, cast "slow, warm, a
  smile in the voice", and has no fallback. V1 has no overrun rule (worst case 2.83 s against the 2.70 s target).
- **Change:**
  - (a) **Record V4 as the BRIEF fallback "Asli log peeche baithe hain, apne phone mein."** It drops "toh", loses no meaning and
    frees +0.28 s, so V4 runs at ≤ 1.06x.
  - (b) **Move the V5 part 1 onset 22.5 → 22.4 s (f672)**, the bar-7 downbeat with the O6 start and the kick, so *busy* lands
    near the beat. Place part 2 at 23.667.
  - (c) Contingencies for the measured takes:
    - V1 > 2.60 s: cut the comma pause to 0.10 s; hard ceiling 2.85 s (the lockup is gone by 2.9 s).
    - V5 part 2 > 1.78 s: one retake with the "..." written as "," and part 2 placed at 23.65 s. Never past 25.48 s (the clunk
      guard), and never move the clunk.

### Smaller items (not ranked; same owners)
- Hook B: hide **all** of V1B in the captions (BRIEF §15 `HIDE`); optional head-snap at 135 mm (§2.2). Owner: creative-director.
- BRIEF §18: QA "events never > 3.0 s apart" → "a visible change ≤ 2.5 s apart". Owner: creative-director.
- The lead decides whether to add #videoediting as a 5th hashtag.

---------------------------------------------------------------------------------------------------------------

## 8. Claims I could not verify (checked 2026-10-08)

- **Ranking signals** (watch time, sends per reach, likes per reach; sends weigh most for non-follower reach). I found these only
  as secondhand 2026 vendor posts repeating Mosseri's January 2025 framing, and no primary statement from 2026. Skip-rate
  thresholds ("< 30-40 % healthy") are vendor figures, not Instagram's. Treat them as hypotheses for Jawad's own Insights.
  Sources: [eclincher](https://www.eclincher.com/articles/how-the-instagram-algorithm-works-in-2026),
  [posteverywhere](https://posteverywhere.ai/blog/how-the-instagram-algorithm-works),
  [inro.social](https://www.inro.social/blog/instagram-reels-insights).
- **Trial Reels eligibility.** Most sources say a public professional account with 1,000+ followers; Sirency and Outfy report 200
  for professional accounts. The Trial toggle in the composer is the final word. Sources:
  [Social Media Today](https://www.socialmediatoday.com/news/instagram-expands-access-trial-reels/752895/),
  [Sirency](https://www.sirency.com/blog/instagram-trial-reels), [Outfy](https://outfy.com/blog/instagram-trial-reels).
- **"Sabse bada rog, kya kahenge log"** (hook lab C): I found no source showing that the couplet is a widely known saying, so it
  is not recommended.
- **The phrase is shared across the border:** verified. [Wikipedia: Log Kya Kahenge](https://en.wikipedia.org/wiki/Log_Kya_Kahenge)
  (a Hindi/Urdu colloquialism; a 1982 Indian film; Pakistani TV series in 2019 and 2020).
- **Timings:** every VO time here is SCRIPT's estimate (Kokoro-calibrated); no Vlad take exists yet. **Pronunciation:** the z/f
  nukta sounds cannot be checked by ASR and need a listener. **Picture:** the head-snap legibility and "reads as people / reads as
  cardboard" are unproven until the §7.4 stills.

## Hand-back

- **Verdict:** FIX, with fixes 1-5 above (owners creative-director and hinglish-scriptwriter).
- **Next gate:** the viral-strategist red-teams the 15 fps preview, measuring frame 0, change events and the 360 px tiles.
- **No commits.**
