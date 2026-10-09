# GATE · Reel 1 · C26 · Pehle Wala Hi Theek Tha (v1 se v27 tak) · `pehle_wala` · concept + script, r1

Author: viral-strategist · Date: 2026-10-08 · Stage: concept + script gate, before the Vlad TTS run.
Red-teamed: `BRIEF.md`, `SCRIPT.md`, `script.json`, `packet.yaml` (this folder) against `SLATE.md` §0, §2, §3.1, §4,
§5 (series bible) and `research/hooks_retention_captions.md`. Looked at: `<WS>/pehle_wala/brief_proof/*.jpg` at full
size, at 360 px (phone at arm's length) and the cover at 210 px inside the 3:4 crop; the rendered `pw_chai_glass` sheet.
`pehle_wala.py` does not exist yet, so frame 0 itself could not be rendered; proof frames stand in (measured below).

---------------------------------------------------------------------------------------------------------------

## 0. Verdict on one screen

**FIX.** Every gate passes (Hook 8, Share 8, Truth PASS, Brand 8). Five fixes remain, ranked by expected retention
impact (§8). **None of them changes a Devanagari prompt, so the TTS run can go ahead now**; fixes 2 and 4 change
placement and the Roman keyword marks only.

| # | fix | time | owner |
|---|---|---|---|
| 1 | the client's marker hovers on frame 0 and re-enters under "...aur phir client ne bola" (visual loop + kills the 31.4-32.6 dead window) | 32.6-34.13, 0-0.27 | creative-director |
| 2 | L2 "Ho jayega." moves to 3.267 (answers pin 3); L1B hard end 2.70 | 2.56-4.25 | hinglish-scriptwriter |
| 3 | hook B shows the v27 mess before the focus panel covers it | 0-1.6 (hook B) | creative-director |
| 4 | one flame-serif word at the CTA: no caption keyword in L11 / L12 | 28.1-34.13 | hinglish-scriptwriter |
| 5 | BRIEF §7/§9/§10/§11 + `packet.yaml` still carry the old VO lines: sync to SCRIPT | whole reel | creative-director |

---------------------------------------------------------------------------------------------------------------

## 1. Scores (0-10, one line of evidence each)

| axis | score | evidence |
|---|---|---|
| **Hook** (gate >= 8) | **8** PASS | Three channels by 0.53 s: client pin lands f8, lockup `BAS EK / *chhota sa* / CHANGE` readable f16, VO "Bas ek chhota sa change." 0.10-1.63 s (1.93 cons). Reads muted (lockup + pin). Minus: frame 0 shows only half-risen caps and no pin (marker appears f5); the glass sits under the 0.6 scrim; text = VO transcript |
| Relatability | 9 | "bas ek chhota sa change" is the top pain in the niche research (hook #1, 29/30); reaches designers, marketers and anyone with a boss; "Owner ki Mummy" is the desi twist every freelancer has lived |
| **Share trigger** (gate >= 7) | **8** PASS | Indirect message + identity ("yeh tum ho") + amusement. Sender: an editor/designer; receiver: the colleague with the same client or boss (or the client, as a dare). End card names the person (`US CLIENT KO / *bhejo*`) |
| Novelty | 7 | The "client notes ruin the design" format and the "pehle wala hi theek tha" ending are known memes; new here: the frame obeys each note live with a version counter, the Mummy reviewer, Ctrl+Z ×26 rewinding into frame 0, Hinglish. No device from his Genjutsu, Yaadein, OpenArt or "younger self" reels |
| **Truth** (gate) | **PASS** | Labelled POV ("Review · POV", caption "POV:"), fictional client and brand, narrator "har editor", no fact about Jawad. Numbers consistent: 26 change pins (v2-v27), v1 + 26 = v27, "Ctrl+Z ×26", "chhabbees" in hook B only. "Ubaal Chai": no brand found (web search 2026-10-08); trademark registries still open |
| Loop | 9 | Sentence loop (L12 ends 34.050, frame 0's L1 at 0.10: 0.18 s across the seam), picture identity (`P(t) = W_core(t - DUR)`), reverse_swell into the f0 impact, story loop (approved v1 -> "bas ek chhota sa change" again). Hook B does not loop (by design) |
| Feasibility | 9 | Chai glass already rendered (13 yaw frames, 1,816 s on 2 threads), score rendered, one local module; ~10 Higgsfield credits for VO. Risks: ~27 ad states in one `state(s)`, one-word TTS echoes |
| **Brand** (gate >= 7) | **8** PASS | `inferno`, serif keyword at hook / payoff / CTA, `@jawad_mp4`, flame on near-black. The ugly middle (cream ≤ 30.8 % of the frame, GOLD glitter) costs a point by design. Nothing from Organic Fostering / Floret: the fostering examples' `app_window` is a 3D-tilted form ("Am I eligible to foster?", "Allowance calculator", neon/amber); this is a flat inferno video-review player with different content |

---------------------------------------------------------------------------------------------------------------

## 2. Gate checklist (the items this gate was asked to test)

| check | result | evidence |
|---|---|---|
| Three-channel hook, hook A | PASS | visual: v1 ad + pin f8 + chip flip f12 + logo ×2 f32; text: 5 words readable f16; spoken: 5 words 0.10-1.63 (1.93) s |
| Three-channel hook, hook B | PASS with fix 3 | visual: f0 raw v27 mess, then blurred by f8 (proof F at 360 px: text over an orange blur); text: `*26* / REVISIONS BAAD` 3 words; spoken: 6 words |
| Spoken hook <= 7 words, lands by 2.7 s | A PASS · B CONDITIONAL | A 5 words, 1.63 / 1.93 s. B 6 words, 2.564 expected / **2.731 conservative** (SCRIPT's hard end is 2.78; this gate's is 2.70) -> fix 2 |
| On-screen hook <= 6 words | PASS | A 5, B 3 |
| VO onset <= 0.3 s | PASS | 0.10 s (f3) both hooks |
| Visual change gap <= 2.5 s | PASS | a pin every 0.53-2.13 s through 25.6 s; longest gap 4.333 (NEW burst) -> 6.400 = 2.07 s; end card has events at 29.87-31.72, 32.59, 32.99, 33.77 |
| New information <= 6 s | PASS | every pin is a new note; re-hooks 12.8 (Mummy) and 17.067 (everything ×1.2) |
| Open loop by 3 s, closed after 70 % | PASS | A: chip "Approved" -> "Changes requested" + counter v1 -> v3 by 2.13 s ("how far will 'chhota sa' go?"); B: "client ne kaha..." Closed 25.600 = 75.0 % |
| Re-hook 12-18 s | PASS | 12.800 (37.5 %, D7 + Mummy + VO) and 17.067 (50 %, scale break, VO silence) |
| Payoff on a downbeat with the keyword | PASS | pin on bar 12 (25.600), `*pehle wala*` on bar 13 (27.733) |
| End card 1.5-2.5 s | DEVIATION (accepted) | 4.267 s, forced by `endcard.EndCard` (4.0-6.0, SLATE §2.6); settled hold 2.057 s. Mitigated by fix 1 |
| Loop bridge | PASS (A) | see Loop above; fix 1 adds the picture half of the sentence loop |
| Rewatch trigger | PASS | "Approved" for f0-f11, 26 littered dots, `v27_ab_pakka_final.mp4`, "3:47 AM", left-then-right, the 1.6 s rewind |
| Share trigger + send sentence | PASS | §6 |
| Truth rule | PASS | §1 |
| Cross-border neutrality | PASS | every VO word is shared Hindustani or a creator loanword (ho jayega, kisi ko nahi pata, bilkul, aur ek, phir, aakhri, jaanta, client, review, final); "Mummy" (SLATE default), respectful "karengi"; chai, "ubaal", "garam" shared; no currency (50% OFF), no phone number (CALL NOW), no flags, cricket, religion, city or politics; glitter border non-religious; Mummy is affectionate (she even fixes the cream gag) |
| Word budget vs DUR | PASS | 45 tokens / 46 spoken words (A), 47 (B) in 34.13 s; speech 16.9 s expected (51 %). Below the playbook's 80-90 on purpose: 27 pins carry 88 words and the narrator only deadpans. Every expected line ends before its hard end; two conservative overruns (L7 +0.017 s, L8 +0.002 s) have free fallbacks |
| Keyword per line | PASS with fix 4 | one `*` keyword per line, each <= 12 chars; L11/L12 keywords collide with the payoff lockup and the CTA glow |
| CTA | PASS | one ask on the card, true, verb-last Hinglish imperative `US CLIENT KO / *bhejo*` (623 / 379 px); no "Comment JD" (no DM automation). Decision on SCRIPT §11 Q2: **no spoken CTA** (it would say "client" twice in 2 s and push L12 off the seam) |
| Cover | PASS | f855 (28.500 s), captions off; at 210 px in the 3:4 crop `*pehle wala*`, HI THEEK THA, "Approved" and the smirk all read; keyword box y 595-745 inside y 240-1680 |
| Caption L1 | PASS (note) | "POV: bas ek chhota sa change... editing ki asli kahani" = 54 characters, restates the hook, keyword "editing", POV label. Optional: "POV: bas ek chhota sa change... video editing ki kahani" (55) carries the exact search phrase |
| SLATE §2 fixes for C26 | PASS | §2.1 hook B `*26* / REVISIONS BAAD` + "Chhabbees revision baad..." (6 words, SLATE says 5; comma dropped by SCRIPT); §2.3 no typing dots, the last pin hovers; §2.6 end card 4.2667 s; §2.10 bonus pin dropped, cream inside the ad rect, v6-v12 only (eases out at v13); §2.11 CTA split into caps + keyword |
| Series bible | PASS | narrator never "main", JD not voiced, ≤ 2 text blocks (BRIEF §5.3), captions hidden 0-2.667 s, ≤ 4 feature transitions (D7, D7, D9; + D1 in hook B), underline 3× per version, no flash/fade, AI label on, banned list clean |
| AI disclosure | FLAG | synthetic voice (Higgsfield Vlad, ElevenLabs v4) and possibly AI-generated character-sheet imagery: Meta's AI info label ON (BRIEF §17 default); the lead confirms with Jawad |

---------------------------------------------------------------------------------------------------------------

## 3. Hook lab (0-2 each; * = pass/fail)

| id | mechanism | spoken (Roman) | on screen | Gap | Spec | Truth* | Fit | Voice | Pull* | /8 | status |
|---|---|---|---|---|---|---|---|---|---|---|---|
| **A** | relatable pain + the client quote | Bas ek chhota sa change. | BAS EK / *chhota sa* / CHANGE | 2 | 1 | P | 2 | 2 | P | **7** | **public** (carries the sentence loop; frame 0 is the beautiful v1) |
| **B** | result first + curiosity gap | Chhabbees revision baad client ne kaha... | *26* / REVISIONS BAAD | 2 | 2 | P | 1 (2.73 s cons) | 2 | P | **7** | **Trial Reel** (differs only in f0-f79; fix 2 brings Fit to 2) |
| C | number, shorter | Chhabbees revision. Ek client. | (B's lockup) | 1 | 2 | P | 2 | 1 | P | 6 | fallback for B only |
| D | curiosity on the chip | Yeh ad approved tha. Phir... | (A's lockup) | 2 | 1 | P | 2 | 1 | P | 6 | no: "approved" is a TTS risk in second 1; the chip already says it |
| E | relatable callout | Har editor ne yeh suna hai. | (A's lockup) | 1 | 0 | P | 2 | 2 | P | 5 | no: spends L11's "har editor" |
| F | stakes / irony | Approved tha. Phir client ne dekha. | *approved* / THA | 2 | 1 | P | 2 | 1 | P | 6 | no: breaks the L12 -> L1 sentence loop |
| G | POV | POV: client ko bas "pop" chahiye. | POV: / *pop* / KARO | 1 | 1 | P | 2 | 1 | P | 5 | no: spoils the 4.27 s gag, weaker gap |

**Recommended: A public, B as the Trial Reel** (as locked). Both share every frame from f80 and every line from L2.
Judge B on skip rate first, then sends per reach, against Jawad's own median; no view forecast.

---------------------------------------------------------------------------------------------------------------

## 4. Retention map (hook A; one row per second; times from BRIEF §6.3/§7 and SCRIPT §3 expected timings)

| s | picture change | new information | open loop state | audio event | reason to stay | risk |
|---|---|---|---|---|---|---|
| 0 | f0 v1 ad (glass, steam, ember backlight, *garam*), chip Approved, v1, caps BAS EK rising; f8 pin "Logo thora bara?" on the logo; f12 chip -> Changes requested; f16 lockup readable | an approved ad; the client wants "one small change" | OPENED: how far will "chhota sa" go? | impact_soft + Dm downbeat f0; VO "Bas ek chhota sa change." 0.10-1.63; pin_thock_dark 0.267; ui_click 0.4; shimmer 0.533 | instant recognition | f0: no readable text, no pin until f5 (fix 1); glass under the lockup scrim |
| 1 | f32 logo ×2 (v2), counter v2; underline completes 1.15 | the frame obeys every note literally | open | pop + slot_tick | the rule of the game | pin-1 card (x 494-930, y 481-599) hides ~45 % of the doubled logo (x 154-776) |
| 2 | f64 "Aur bara.": logo ×3 runs off the ad, v3; lockup exits 2.23-2.60; splice f80 | it is never one change | open; counter = clock | pin_thock, whoosh_fast, hats enter | escalation | hook B: "kaha..." then "Ho jayega." 0.37 s later reads as the client's answer (fix 2) |
| 3 | f96 "Thora left.": logo slides -72 px (v4); captions start | the editor complies | open | VO "Ho jayega." (2.93 now; 3.27 after fix 2); slot_tick | call and response | pin 3 now lands mid-word |
| 4 | f128 "Thora aur pop karo": saturation spike + L3 push; NEW burst f130 (v5) | the classic vague note | open | flash_hit, pop 4.333, string ostinato; VO "Pop?" 4.40 | laugh | "Pop?" TTS (scratch heard बाप) |
| 5 | burst settles; captions "Kisi ko" / "nahi pata" | nobody knows what "pop" means | open | VO "Kisi ko nahi pata." to 6.55 | the joke lands | - |
| 6 | f192 two-line pin "Background white kar do, clean lagega": cream fills the ad in 12 f (v6) | the cinematic look dies | open | dark thock under the VO tail, downlifter; VO "Clean." 6.73 | visual shock | cream stays in the ad rect |
| 7 | f224 "Bhaap nazar nahi aa rahi": steam gets a cartoon outline (v7) | - | open | toggle_on; taiko fill 7.47-8.53 | micro-gag | a 3 px outline is ~1 px on a phone (preview check) |
| 8 | f256 "Music thora energetic": the player shakes on beats (v8) | the music obeys too | open | drums in; VO "Energetic." 8.60 | physical comedy | - |
| 9 | f288 "Glass thora chamkao": 4 sparkles (v9) | - | open | sparkle | escalation | - |
| 10 | f320 "Font fun wala karo": *garam* -> parody face, wobble (v10) | - | open | bubble_pop, 808 in; VO "Fun." 10.80 | third echo | "Fun" must not become फन (snake hood) |
| 11 | f352 "Har cheez pe shadow daalo": hard drop shadows (v11) | - | open | card_slide | - | MILD 10.7-12.8: sixth gag of one formula |
| 12 | f384 RE-HOOK: D7, GOLD "M" pin "Mujhe pasand nahi aaya.", glitter border (v12) | a new reviewer: Owner ki Mummy | escalated | pin_thock_mummy, glitch + whip, drums out 2 beats; VO "Ab Mummy bhi review karengi." 12.87 | desi twist, new character | - |
| 13 | f400 "Background wapas dark karo" (cream out, v13); f416 "Aur glitter." (v14) | Mummy overrules the client | escalated | dark Mummy thocks, whoosh, shimmer | she is funnier than the client | - |
| 14 | f432 "Logo bhi bara." (v15); f448 "Thora cinematic": letterbox, flares, slow-mo steam, JD tile in sunglasses | JD appears | open | braam + L3 push; VO "Bilkul cinematic." 15.00 | the best gag | - |
| 15 | flares sweep, slow steam, tile holds | - | open | braam tail; VO to 16.37 | spectacle | - |
| 16 | f480 "Price bhi daal do": 50% OFF slam (v17); f496 steam ×3 (v18); f502 tile exits | - | open | card_slide, whoosh_slow | escalation | - |
| 17 | f512 (50 %) "Sab kuch thora bara": everything ×1.2 + L3 push (v19) | midpoint scale break | open | air_zoom, trailer_hit, music +1.9 LU; no VO 16.4-19.2 | pattern break | - |
| 18 | f544 "Call now bhi likho": CALL NOW slam (v20) | - | open | card_slide | - | - |
| 19 | f576 "Aur pop." burst 2 + "3:47 AM" chip; f592 "Logo aur bara." (v21-22) | it is 3:47 AM | open | clock ticks; VO "Aur ek, aur ek..." 19.23 | acceleration | - |
| 20 | f608 "Shadow kam karo", f624 "Shadow wapas." (v23-24) | the client contradicts himself | open | swishes L/R; VO "...aur ek." to 20.88 | laugh | pins every 0.53 s: unreadable on purpose (rewatch) |
| 21 | f640 D7, "Aur energetic" 8 px shake; drawer v24_final / v25_FINAL (v25) | filenames | MAX | glitch + whip, shepard riser, 2nd drum layer | easter eggs | - |
| 22 | f656 "Thora left." + v26_final_final; f672 "Thora right." + v27_ab_pakka_final; counter v27 | left, then right: back where it was | MAX | ticks, card slides | rewatch fodder | - |
| 23 | f696 drawer + clock exit; f704 the last pin hovers, undecided | the last message is coming | MAX | ui_hover, heartbeat build, drums out; VO "Phir aakhri message..." 23.50 | what will it say? | - |
| 24 | the hover keeps moving | - | MAX | heartbeat accelerates; strings out 24.0, 808 out 24.53 | suspense | the hover is the only motion: keep the marker ≥ 44 px |
| 25 | f752 freeze; silence 25.067-25.333; f768 PAYOFF pin "Pehle wala hi theek tha." + L3 push 1.0 | the punchline | CLOSED (75.0 %) | true silence -> pin_thock_big + sub_drop (loudest) | payoff | read, not voiced (the lockup repeats it at 27.7) |
| 26 | f784 "Ctrl+Z ×26" chip; f790 rewind v27 -> v2, pins fly up, counter spins down | the editor obeys this note too | resolving | typing, tape_stop, tape_rewind, 26 ticks | dense rewatch beat | - |
| 27 | f832 v1 pristine, Approved, *pehle wala* rises; f836 JD smirk | v1 was the final | resolved | impact_soft + glass_tap D6; v1 motif restarts | keyword on the downbeat | - |
| 28 | HI THEEK THA + underline 27.98-28.48; cover f855 | the moral | resolved | VO "Har editor jaanta hai," 28.13 | quotable line | *garam* glows beside *pehle wala* |
| 29 | f886 lockup + tile exit; f896 end card: JD ring draws on | - | - | VO "...v1 hi final hota hai." | - | - |
| 30 | CTA rises `US CLIENT KO / *bhejo*`, signature | the ask | - | card swish / shimmer / glass_tap; VO ends 31.36 | send | caption *final* + *bhejo* + JD + *garam* = 4 flame-serif words (fix 4) |
| 31 | card settled 31.717 | - | - | silence 31.36-32.64 | - | **DROP RISK 31.4-32.6**: nothing new, caption gone at 32.01 (fix 1) |
| 32 | captions "...aur phir" 32.59, "client ne bola" 32.99 | the story restarts | RE-OPENED | VO "...aur phir client ne bola" 32.64-34.05, rising | sentence loop | - |
| 33 | card exit 33.773-34.133 + exposure push | - | re-opened | reverse_swell into f0 | seamless replay | - |
| 34 | f1023 = one frame before f0 | - | - | f0 impact_soft; "Bas ek chhota sa change." completes L12 | loop | hook B does not loop (by design) |

**Drop-risk windows:** 0-0.17 s (frame 0 carries no readable text and no pin), 10.7-12.8 s (mild: formula fatigue,
still a change every 1.07 s; the Mummy re-hook rescues it), 31.4-32.6 s (end card settled, no VO, no caption).
No visual-change gap exceeds 2.5 s anywhere.

---------------------------------------------------------------------------------------------------------------

## 5. Script red-team (line by line)

| line | verdict | note |
|---|---|---|
| L1 "Bas ek chhota sa change." | keep | the phrase everyone owns; loop-ready (no "client ne bola" in it) |
| L1B "Chhabbees revision baad client ne kaha..." | keep, retime gate | one breath, 6 words; must end ≤ 2.70 s measured (fix 2) |
| L2 "Ho jayega." | keep, move to 3.267 | the editor's reply to "Thora left." (fix 2) |
| L3 "Pop? Kisi ko nahi pata." | keep | the best line in the body; if Vlad cannot say पॉप cleanly in two takes, use the Latin "Pop?" in the prompt (SCRIPT §7) rather than ship a बाप |
| L4-L6 "Clean." "Energetic." "Fun." | keep | rule-of-three deadpan echoes; pick the flattest takes; if "Fun." keeps a stray consonant, drop L6 and let the parody font + bubble_pop carry v10 (the third echo is the weakest) |
| L7 "Ab Mummy bhi review karengi." | keep | re-hook line; respectful plural |
| L8 "Bilkul cinematic." | keep | |
| L9 "Aur ek, aur ek, aur ek." | keep | placed 1 frame after each pin |
| L10 "Phir aakhri message..." | keep | "aaya" correctly removed (the pin has not landed) |
| L11 "Har editor jaanta hai, v1 hi final hota hai." | keep text, drop the caption keyword (fix 4) | the quotable, send-worthy line |
| L12 "...aur phir client ne bola" | keep text, drop the caption keyword (fix 4) | rising contour, cut at word end + 40 ms |
| payoff pin (read) | keep silent | the drop-out makes the read land; the lockup repeats it 2.1 s later |

---------------------------------------------------------------------------------------------------------------

## 6. Share, comment, packaging

- **Send sentence:** An editor, designer or anyone who answers to a client or boss sends this to the colleague who sat
  through the same "bas ek chhota sa change" rounds (or, as a dare, to the client) because it says "pehle wala hi theek
  tha" for them: an indirect message plus "yeh tum ho".
- **Comment prompt (keep):** "Tumhare client ya boss ka 'bas ek chhota sa change' kya tha? Ek line mein." Optional
  pinned follow-up with a lower-friction number answer: "Aur record? Kitne version tak gaye ho?"
- **Cover:** f855 (28.500 s), captions off. Checked at 210 px in the 3:4 crop: reads. Dim *garam* on this frame with
  the same local player dim (fix 4 note).
- **Caption L1:** keep "POV: bas ek chhota sa change... editing ki asli kahani" (54). Body line 1 "v1 se v27 tak. Aur
  phir client ne bola: pehle wala hi theek tha." spoils the payoff for anyone who opens "more" mid-watch; suggested
  "v1 se v27 tak. Aur phir aakhri message aaya..." (creative-director's call). Hashtags (4): #videoediting
  #editorlife #freelancerlife #jawadmp4.
- **Audio:** original score + SFX + VO; Version B (VO + SFX) for an in-app song; audio name "Original audio · Bas ek
  chhota sa change · @jawad_mp4". No trending track baked in.
- **AI label:** ON (synthetic voice; possibly AI-generated character sheets). Open for the lead with Jawad.
- **Comment risk to expect (not a fix):** muted viewers will see "26" over a "v27" counter in hook B and some will
  comment "27 hai". The arithmetic is right (v1 + 26 changes); pin a one-line reply if it happens.

---------------------------------------------------------------------------------------------------------------

## 7. Measurements behind this gate

| what | value | how |
|---|---|---|
| proof frame luma (YAVG / YHIGH, 8-bit) | hook A t0.70 35.7 / 88 · hook B t0.40 30.7 / 69 · v27 t22.6 42.0 / 110 · cover t28.5 40.4 / 98 · end card t31.6 23.1 / 59 | `ffprobe ... signalstats` on `brief_proof/*.jpg`; none of the hook frames is "dark and empty" (YAVG < 25 and YHIGH < 100); the end card is dim by design. Frame 0 itself must be measured on the first render (BRIEF §18: YAVG ≥ 25) |
| phone legibility (360 px wide) | hook A lockup and pin read; *garam* competes; the glass is barely visible under the scrim · hook B "26 REVISIONS BAAD" reads, the mess does not (blur) · v27: pins, 50% OFF, NEW, filenames read | `ffmpeg scale=360:-2`, viewed |
| cover at 210 px (3:4 crop y 240-1680) | *pehle wala*, HI THEEK THA, Approved, smirk read | `crop=1080:1440:0:240,scale=210:-2`, viewed |
| caption L1 | 54 characters (alt 55) | `len()` |
| word counts | hook A 5 spoken / 5 on screen; hook B 6 / 3; track A 45 tokens = 46 words | SCRIPT + `script.json` totals |
| pin-1 card vs logo ×2 | card x 494-930, y 481-599; logo at ×2 x 154-776, y 504-608: 282 of 622 px hidden | BRIEF §5.2 and §6.3 geometry |
| stale copy | BRIEF lines 342, 344, 355, 369, 467-475, 510-516 and `packet.yaml` 212, 319-327 carry the pre-script VO | `grep` |

---------------------------------------------------------------------------------------------------------------

## 8. Fixes, ranked by expected retention impact

**1 · Frame-0 marker and the loop tail (creative-director) · 32.6-34.133 s and 0-0.267 s**
- Evidence: frame 0 shows the v1 ad with half-risen caps; the key glyphs start at 0.12 s and the client marker only
  appears at f5 (L-3), so the first 5 frames carry no story element. The end card is settled from 31.717 with VO
  silent 31.36-32.64 and the last L11 chunk gone at 32.01: 1.2 s with nothing new, the reel's only dead window. The
  loop is verbal only; the picture never says "here it comes again".
- Change: give pin 1's marker (the FLAME "C" disc, no card, no text) a pre-landing life inside `state(s)` for
  s in [-1.5, 0.167): it enters from above the player at s = -1.5 (t = 32.633, on "...aur phir client ne bola"),
  hovers with the 23.467 hover grammar in the ad's top-right, clear of the JD ring (x 420-660, y 440-680), the CTA
  boxes and the signature (e.g. around (850, 560) ± 30 px), glides during the card exit (s -0.36 -> 0) to (470, 424)
  and falls its existing 48 px onto the logo at f5-f8. Because `P(t) = W_core(t - DUR)`, f1023 and f0 show the same
  marker: the picture half of the sentence loop, a moving "uh-oh" on frame 0, and an event inside the end-card hold.
  Draw it after the local end-card player dim at ≥ 0.8 opacity; keep it out of the D9 rewind source (clamp the hover
  to the payoff / end-card world). SFX: `ui_hover` -14 hp 5000 at 32.633 (it sits under L12). Verify: `--stills 0,34.1`
  flip, `E.seam_report`, f0 YAVG ≥ 25, no overlap with the monogram, CTA or signature boxes.

**2 · L2 call-and-response + hook B landing (hinglish-scriptwriter) · 2.56-4.25 s**
- Evidence: L2 "Ho jayega." at 2.933 sits 0.37 s after hook B's "...client ne kaha..." (2.564 expected) while the card
  on screen reads "Client: Aur bara." The ear files "Ho jayega" as the client's quote and hook B's open loop gets a
  wrong answer inside the 3-second skip window. In hook A, pin 3 lands at 3.200 in the middle of the word (dark thock).
  L1B's conservative end 2.731 s misses this gate's 2.70 s.
- Change: place L2 at **3.267 (f98)**, two frames after pin 3 "Thora left." lands, so it is the editor's reply to a
  visible note in both hooks; expected end 4.06, conservative 4.13 (< hard end 4.25; L3 at 4.40 unchanged). Pin 3's
  cue at 3.200 goes back to full `pin_thock` 0 dB; caption chunk 0 re-solves to about 3.22-4.35. Set L1B's hard end
  to **2.70** and apply SCRIPT §4's fallbacks (trim the "kaha..." release to 40 ms, then re-take with कहा।) until
  the measured last word ends ≤ 2.70 s. No prompt text changes.

**3 · Hook B shows its mess (creative-director) · 0-1.6 s, hook B only**
- Evidence: proof F at 360 px: the focus panel (x 120-960, y 640-1120, blur sigma 18, ×0.08) covers ~63 % of the ad
  from f8, so at the swipe decision the "v27 mess" is an orange blur; only the cropped giant-logo strip, glitter edges
  and the v27 counter still say "revisions". The Trial's picture stops proving its number.
- Change: keep f0-f11 raw (the "26" key is still rising), ramp the panel in over f12-f20 instead of f0-f8; drop the
  blur to sigma ~8 and lift the multiplier from 0.08 to ~0.25 so NEW, 50% OFF and CALL NOW stay recognisable as
  shapes and colours while their letters cannot be read through the lockup. Measure the lockup ≥ 4.5:1 on the
  rendered still and re-proof F at 0.4 s and 1.2 s at 360 px.

**4 · One flame-serif word at the CTA (hinglish-scriptwriter) · 28.1-34.133 s**
- Evidence: SCRIPT §8 chunk 17 "final hota hai" (*final*, 30.30-32.01) and chunk 19 "client ne bola" (*bola*,
  32.99-34.13) glow while the end card draws the JD monogram and *bhejo*, with the ad's *garam* still glowing
  underneath (proof E: four flame-serif words on one screen). Chunks 14-16 run under the *pehle wala* lockup. The one
  ask (send) loses its focus at the exact moment it is made.
- Change: remove the `*` keyword from L11 and L12 in the Roman token track (Devanagari untouched; all-white chunks are
  supported by `snake_captions`). After the payoff only *pehle wala* (27.7-29.5) and *bhejo* (29.9-34.1) glow. Note
  for the creative-director: the local player dim under the card must take *garam* to ×0.35 as BRIEF §16 specifies;
  dim it the same way on the cover frame.

**5 · Sync the locked docs to the script (creative-director) · whole reel**
- Evidence: BRIEF §7 (rows 8, 10, 21, 27-29, 35, 45, 49), §9 and §10, and `packet.yaml` (212, 319-327) still carry "Theek hai. Ho
  jayega." 2.75-4.15, "Pop karo. Matlab? Kisi ko nahi pata.", "Cinematic. Bilkul.", "Aur ek." with periods, "Phir
  aakhri message aaya.", L11 with a colon at 28.05 and L12 at 32.55; BRIEF §10's chunk plan ("Theek hai / Ho jayega",
  "Pop karo / Matlab?", "message aaya"); BRIEF §11 still has full thocks at 6.400, 19.733, 20.267 and 20.800 (SCRIPT
  §8 makes them dark); SLATE §3.1 counts L1B as 5 words (it is 6). A builder reading the LOCKED brief would cue
  captions and SFX on words that moved, which breaks gags by a beat.
- Change: state in BRIEF §0 and §9 that `SCRIPT.md` / `script.json` own VO text, windows and caption chunks; update
  BRIEF §7 VO column, §9, §10 and §11 (including fix 2's L2 move and pin 3's level), and the packet's VO strings.

**Preview red-team checks carried forward (not fixes yet):** f0 YAVG ≥ 25 and motion on f0; the pin-1 card hides
282 of 622 px of the ×2 logo (consider collapsing card 1 at f30 if v2 does not read at 360 px); the v7 steam outline
(3 px) must read at 360 px; *garam* under the hook scrim; speech ≥ 8 LU over the bed in the 17.067 (+1.9 LU) bar;
the hover marker 23.5-25.1 must read at phone size.

---------------------------------------------------------------------------------------------------------------

## 9. Claims I could not verify (checked 2026-10-08)

| claim | status | source |
|---|---|---|
| Trial Reels eligibility | sources disagree: 1,000 followers (Publer help, refreshed June 2026; PostFast) vs 200 for professional accounts (Sirency, Outfy). The in-app toggle is the test | [Publer guide](https://publer.com/blog/instagram-trial-reels-guide/), [Sirency](https://www.sirency.com/blog/instagram-trial-reels), [Outfy](https://outfy.com/blog/instagram-trial-reels), [PostFast](https://postfa.st/blog/instagram-trial-reels) (vendor blogs) |
| Skip rate = exits in the first 3 s, in Reels Insights since Aug 2025; "healthy" < 30-40 % | secondhand; benchmarks unofficial; a diagnostic, not a documented ranking input | [Metricool](https://metricool.com/instagram-reel-analytics/), [Social Samosa](https://www.socialsamosa.com/news-2/instagram-retention-chart-skip-rate-new-performance-metrics-reels-9730992), [Babbleboxx](https://www.babbleboxx.com/post/instagram-adds-reels-retention-skip-rate-what-influencer-marketers-should-do-next) |
| Sends per reach drive non-follower reach (Mosseri, Jan 2025); "3-5× likes" | the Jan 2025 statement is reported widely but secondhand; no new 2026 statement found; the multiplier is unverified | [Sociality](https://sociality.io/blog/instagram-reels-analytics/), [Metricool guide](https://metricool.com/blog/instagram-reels-guide/) |
| Mosseri year-end memo favouring human-made over AI-generated posts in 2026 | reported by vendor blogs only; relevant to the AI-label decision, not verified | [eclincher](https://www.eclincher.com/articles/how-the-instagram-algorithm-works-in-2026) |
| "Ubaal Chai" is not a real brand | no brand found in a web search on 2026-10-08 (nearest: Urbal Tea, Milwaukee); IP India / IPO Pakistan registries not searched | web search, 2026-10-08 |
| ~55-60 caption characters show in the Reels viewer | secondhand (research §1) | `research/hooks_retention_captions.md` §1 |

Never a view forecast: 1M is a stretch goal; reach also depends on distribution, timing and luck.
