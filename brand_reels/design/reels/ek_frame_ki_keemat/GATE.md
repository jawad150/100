# GATE: Reel 3 · C08 · Ek Frame ki Keemat: concept + script gate (r1)

Date 2026-10-08 · Author: viral-strategist · Stage: concept + script, before any TTS take.
Read: `SLATE.md` §0, §2, §3.3, §4, §5 (bible) · `BRIEF.md` (21:47) · `SCRIPT.md` + `script.json` (draft v1, 22:11) ·
`research/hooks_retention_captions.md` · `panel_viral.md` §4.5 · the previs stills in
`workspace/jawad_reels/ek_frame_ki_keemat/previs/`, which I looked at at 360 px and 210 px wide (phone and grid size).
Tools I ran: `script.json` checks, `T.measure`, `sfx_jawad.fit_under_vo` on the planned cues, `signalstats` on the stills.

## Verdict: FIX

All four gates pass: Hook 8, Share 7, Truth pass, Brand 9. It is FIX, not SHIP, for three reasons:
- One hook-audio problem is measured, and it would also stop the mix build (fix 1).
- Two windows are soft, though neither is a dead 3 s window: 14.5-16.3 s and the post-payoff tail.
- The brief and the script disagree on caption keywords and on four VO lines.

None of this needs a new concept. TTS takes T1, T2, T4 and T5 can go now. T3 waits only for the lead's call on fix 5.
From the viral side I approve script changes C1-C5. C6 is approved with fix 4.

---------------------------------------------------------------------------------------------------------------

## 1. Scores (0-10, one line of evidence each)

| axis | score | evidence |
|---|---|---|
| Hook | **8** | Frame 0 is the finished house frame: JD rim-lit, `AAP NE ISE / 0.03 sec / DEKHA` already set. Next come the pause click (0.3), the seam glint (0.6) and the layers splitting (0.9). The VO is 6 words, 0.10 to an estimated 2.37 s. It works muted. Not a 9: the spoken line is a statement (the picture carries the gap), and the f0 hit sits on "Aap" (fix 1). |
| Relatability | 7 | Editors and designers all hear "editing mein kya hai". But that line only arrives at 29.6 s. The middle is craft awe, not "yeh toh main hoon". |
| Share trigger | **7** | Indirect message plus pride: the skeptic is named on the end card. Editors also send it to each other as in-group awe ("360 layers, dekh"). This is at the gate's edge, not above it. |
| Novelty | 8 | An exploded frame with an honest flat face pane, then a 30-frame corridor, is new for his page and for the desi feed. VFX breakdowns exist. The big serif number lockup also opens C26's hook B, two posts earlier. |
| Truth | **PASS** | Every number is true by construction: 12 layers (`len(FRAME) == 12`), 3 stems, 30 fps, 12 x 30 = 360, 1/30 s rounds to 0.03 s, `00:00:00:01`. Nothing is claimed about Jawad. The AI voice is labelled. A pedant may say 360 is "12 layers drawn 30 times". That is exactly what the VO says ("har second"), so it passes. |
| Loop | 9 | The frame plays straight into f0 (`tl = t - 33.6`). The lockup and chip cross-fade back from 33.0. The reverse swell and cymbal end on 33.6. Hook B's loop jumps (accepted in BRIEF §6.2). |
| Feasibility | 9 | Toolkit planes only, no Blender. The corridor is billboards of one pre-flattened sprite. The master budget is 35-45 min. 5 takes cost at most 12.5 credits. |
| Brand | **9** | `ember` look, serif `keemat` on the bar-11 downbeat with its underline, IVORY type, `@jawad_mp4` at (760, 1575). There is no centred play ring and nothing from fostering or Floret. The diagonal god rays are not his "younger self" top spotlight. |

Gates: Hook 8 >= 8 · Share 7 >= 7 · Truth pass · Brand 9 >= 7. **All pass.**

---------------------------------------------------------------------------------------------------------------

## 2. Three-channel hook test

### 2.1 Hook A (public)

| channel | content | lands | verdict |
|---|---|---|---|
| Visual | Frame 0 is the playing hero frame: embers rising, JD idle, a bottom-left bust with flame rim, the chip `▶ 00:00:00:01` at (760, 1282). Then: 0.3 pause (embers freeze, chip ▶ to ❚❚ with a local flare), 0.6 seam glint, 0.9 layers separate as the camera pulls back. | f0; first change 0.3; first big change 0.9 | PASS. Measured on the previs frame 0 (`B1_f0.png`): YAVG 46.9, YHIGH 91, YMIN 16. That is not dark or empty (the dark-empty test is YAVG < 25 and YHIGH < 100). |
| On-screen text | `AAP NE ISE / 0.03 sec / DEKHA`: 5 tokens, one serif keyword, already set on f0 | f0 | PASS. It reads at 360 px and at 210 px (3:4 crop test, §6). |
| Spoken | **"Aap ne ise palak jhapakte dekha."** (आप ने इसे पलक झपकते देखा।) | 6 words, 0.10 to 2.37 s estimated (+10 % = 2.61 <= 2.70) | PASS. The idiom works on both sides of the border, and no फ़्रेम word sits in the first 3 s (SLATE §2.9). |
| Sound | BRIEF §11 puts `trailer_hit` -6 at 0.000 under "Aap" at 0.10 | 0.0 | **FAIL as written.** `trailer_hit` is a HERO impact. I ran `fit_under_vo([...trailer_hit t=0.0...], V1A words)` and it raised `HeroOnWordError ... overlaps speech [(0.1, 2.37)] (nearest legal hit 2.49)`. The same call with `impact_soft` -8 at 0.0 passes with no ducking. See fix 1. |

Two more tests:
- **Muted:** "You saw THIS for 0.03 sec", then the pause icon, then the frame breaks into slices. The idea gets through without sound.
- **Sound only:** a click, "aap ne ise palak jhapakte dekha", then glass sliding. This gets through too.

Text and VO are parallel, not a transcript: the number is on screen, the human idiom is in the voice.

### 2.2 Hook B (Trial Reel, frames 0-89)

- **Visual:** frame 0 is the corridor mid-surge, with 7 motion-blur samples. Many tiny copies of the hook title sit behind a NIGHT_0 scrim. PASS.
- **Text:** `360 / LAYERS · 1 SECOND` (864 px). PASS.
- **Spoken:** "Ek second. Teen sau saath layers." 6 words, estimated to end at 2.25. PASS.
- **Sound:** `impact_soft` at 0.0 is not a HERO, so there is no conflict.
- **Risks:**
  - साठ heard as सात = 307, a truth problem (SCRIPT risk 1; T5 tests it).
  - It spends the 20.4 s number and the corridor up front.
  - Its loop jumps from hook A's world to the corridor.
- **Measure B on skip rate only.** Do not judge it on watch time or replays.

### 2.3 Hook lab (scored 0-2: Gap, Specificity, Fit, Voice; Truth* and Pull* are pass/fail)

| id | mechanism | on screen | spoken | words | Gap | Spec | Truth | Fit | Voice | Pull | /8 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| **A** | specificity + self-referential gap | `AAP NE ISE / *0.03 sec* / DEKHA` | Aap ne ise palak jhapakte dekha. | 6 | 2 | 2 | P | 2 | 2 | P | **8** |
| **B** | result first (number) | `*360* / LAYERS · 1 SECOND` | Ek second. Teen sau saath layers. | 6 | 1 | 2 | P | 2 | 2 | P | **7** |
| C | curiosity | `EK FRAME KE *andar*` | Ek frame ke andar kya hota hai? | 7 | 2 | 1 | P | 2 | 1 (फ़्रेम in 3 s) | P | 6 |
| D | contrarian | `EDITING *aasaan* HAI?` | Sab kehte hain editing aasaan hai. | 6 | 1 | 0 | P | 2 | 2 | P | 5 |
| E | relatable callout | `EDITING MEIN *kya* HAI?` | "Editing mein kya hai?" Yeh dekho. | 6 | 2 | 0 | P | 2 | 2 | P | 6 |
| F (new) | pattern interrupt (the reel pauses itself) | `RUKO. / *0.03 sec*` | Ruko. Ise ek pal ke liye dekho. | 7 | 2 | 1 | P | 2 | 1 (instructional) | P | 6 |
| G (new) | POV / quoted pain | `"BAS *5 minute* KA KAAM"` | "Bas paanch minute ka kaam hai na?" | 7 | 2 | 1 | P* (a quote, but it puts a minutes figure on screen against the do-not-claim list) | 2 | 2 | P | 7* |
| H (new) | number answer first | `IS FRAME MEIN / *12* / LAYERS` | Is ek tasveer mein baarah layers hain. | 7 | 0 | 2 | P | 2 | 2 | P | 6 |

**Recommended: A public and B as the Trial Reel**, as locked in SLATE. The two differ only in frames 0-89, and the body is shared from the f90 splice.
**Keep for a later re-cut:**
- E: the non-editor audience.
- G: the same audience. It is strong, but the lead must first decide whether a quoted "5 minute" breaks the minutes lock. My view: as a quote it is fine; as a cover number it is not.

---------------------------------------------------------------------------------------------------------------

## 3. Script against the binding sources

| rule | source | status | evidence |
|---|---|---|---|
| Spoken hook <= 7 words, done by 2.7 s | SLATE §3, §2.9 | PASS | V1A: 6 words, ends 2.37. V1B: 6 words, ends 2.25. Both have a zero-credit fit ladder. |
| The hook drops फ़्रेम; no centred play ring; hidden JD in layer 03 from frame 0 | SLATE §2.9 | PASS | The chip is a 330x72 pill to the right of the face. I viewed the hidden JD on the frame-0 crop at 1:1: faint, and findable when you look for it. |
| VO onset <= 0.3 s | bible §5.1 | PASS | 0.10 in both hooks. |
| Spoken-number lock | SLATE §4 | PASS | baarah, tees, teen sau saath, teen. "ek" means one frame or one second. Nothing else. |
| Truth lock (no hours, rates, clients, "main", per-layer times) | SLATE §3.3, BRIEF §2 | PASS | The narrator speaks as aap or in the third person; JD is not voiced. |
| Re-hook at bar 5 with VO silence | SLATE §3.3 | PASS | Silence 11.61-12.05 (0.44 s). Stop at 12.0 with a 0.35 push. |
| Second break around 50 % | playbook rule 5 | PASS | The C3 portal into the corridor at 16.8 (50.0 %). |
| Payoff at 65-80 %, on a downbeat, with the keyword | playbook §3.4 | PASS | 26.4 (78.6 %) on bar 11. Keyword glyphs from 26.62; "Keemat" spoken at 26.75. |
| End card: one true CTA <= 5 words, settled >= 1.5 s, over the moving world | bible §5.1 | PASS (spelling: fix 5) | `USSE YEH / bhejo`, settled 31.25-33.24 (1.99 s), world dimmed x0.58. |
| Loop: last frame into frame 0 | bible §5.1 | PASS | `tl = t - 33.6`; `E.loop_world` from 33.0; swell ends 33.6. |
| <= 2 text blocks | bible §5.1 | PASS with one note | During 12.0-16.0 the frontal view shows three readable strings: caption C1, the `12 · finish ON` tag, and the frame's own title at 0.63 scale (`F3_rehook_13p2_safe.png`). The title is a callback the viewer recognises rather than reads, so I accept it. Do not add anything there. |
| Captions hidden under designed type | bible §5.1 | PASS | Hidden 0-12.0, 20.13-21.99, 26.4-33.6. |
| One serif keyword per chunk; keyword per line | snake_captions, playbook rule 3 | PASS with fix 4 | Every line has a keyword. V5's flame word sits on "zinda" (14.43), not on the re-hook word at 12.05. |
| Pan-desi words | playbook §2.5 | PASS, one exception | All VO words are daily speech on both sides. Only the card spelling "USSE" is a problem (fix 5). |
| House spelling | prior SRT | PASS | nahi / mein / hai. |
| TTS hygiene | vo_config | PASS (checked) | No Latin letters or digits in any of the 11 DEV strings. DEV and ROM token counts are equal on every line (`script.json`). |
| Word budget against DUR | playbook §3.1 | PASS | 62 words; 20.83 s of speech at 1.08x; 23.64 s of placed spans (70 %). The reel is led by picture by design, and every VO-free window is busy. |
| AI disclosure | skill rule 4 | flagged | AI info ON, caption says "Voice: AI (TTS)", lane label `VO · AI voice`. Lead's open question Q5. |

**Script change log (SCRIPT §9), viral view:**
- **C1, approve.** "Lekin is ek frame mein..." puts the turn word on 3.07, the first beat after the skip window, and "ek" echoes EK FRAME.
- **C2, approve.** "awaaz ke teen tracks": track is masculine on both sides.
- **C3, approve.** "Keemat... banane wala jaanta hai" finishes the on-screen `EK FRAME KI` as one sentence across text and voice. This is the best three-channel moment in the reel.
- **C4 and C5, approve.**
- **C6:** digits as in the house SRT, approve. "One keyword per line" is stricter than the tool's rule of one keyword per chunk, and it costs the re-hook its flame word (fix 4).

The creative-director must bring BRIEF §2, §5, §9 and §15 in line with the approved lines. The brief still has "Is frame mein...", "ki teen tracks", "Iski keemat..." and "...".

---------------------------------------------------------------------------------------------------------------

## 4. Retention map (one row per second; times from BRIEF §5 and SCRIPT §4, estimates until the takes exist)

| s | picture change | new information | open loop state | audio event | reason to stay | risk |
|---|---|---|---|---|---|---|
| 0 | f0 frame playing, embers, chip ▶; **0.3 pause** (embers freeze, ▶ to ❚❚ with flare); 0.6 seam glint; 0.8 chip fades | "you saw this for 0.03 s" | **L1 opened by the picture:** what is inside 1/30 s, and what is it worth? | f0 transient; VO 0.10 "Aap ne ise..."; 0.3 pause click; 0.6 glass slide | the reel paused itself | HERO hit under "Aap" (fix 1) |
| 1 | 0.9 layers separate in z; pull back; the frame becomes an object | it is built in layers | L1 | card_slide; "palak jhapakte"; whoosh 1.6 | the image comes apart | - |
| 2 | pull back; 2.4 orbit starts | - | L1 | VO ends ~2.37; whoosh 2.4 | depth | hook B splice at f90 must not show |
| 3 | counter `00 LAYERS` rises; panes light one by one | counting | how many? | slot ticks x12; V2 3.07 "Lekin is ek frame mein..." | the count runs | - |
| 4 | 4.8 side-on lands, `12` settles, push 0.3 | **12 layers** | count answered; L1 continues as "what are they, what is it worth" | glass_truth; "baarah" 4.80 | spectacle | the glass tap is auto-ducked to -8 dB under "baarah": check by ASR on the mix |
| 5 | side-on hold (cover f153); 5.4 counter exits, swoop | - | **L2 opened:** which layers? | "layers hain" ends 5.84; whoosh 5.7 | the single image | - |
| 6 | fly-through: `01 · andhera` 6.0, `02 · dhuaan` 6.6, rack focus | names | L2 closing one per beat | tick per beat; "Andhera. Dhuaan." | rhythm | tags are 44 px, about 15 px tall at phone size: readable, not lingering |
| 7 | `03 · roshni` (hidden-JD pane), `04 · chehra` (flat face pane) | his face is a flat layer | L2 | "Roshni. Chehra." | honest 2.5D | - |
| 8 | `05 · rim light`: the rim alone, a hand's width from his face | light is its own layer | L2 | tick; VO ends 8.36 | the strongest "did you see that" image | - |
| 9 | `06 · saaya` 9.0, `07 · chingaariyan` 9.6 (frozen embers) | - | L2 | ticks; harmonium swell; no VO | picture only | low: 1.67 s with no voice inside 6 s of the same device |
| 10 | `08 · lafz` 10.2 | - | L2 | "Har lafz." | - | - |
| 11 | `09 · keyword / 10 · chamak` 10.8, `11 · lakeer` 11.4 | - | 11 of 12 named | "Har chamak." ends 11.61; silence to 12.05 | where is the 12th? | 6 s of one device (list fatigue) |
| 12 | **RE-HOOK:** stop on the near-invisible pane 12, `12 · finish ON`, push 0.35; swing to frontal; stack folds | a layer you cannot see | **L3 opened:** which one, and why does it matter? | impact_soft + glass_tap; V5 12.05 "Aur ek layer..." | mystery | caption chunk has no flame word now (fix 4) |
| 13 | frontal 13.2; flick OFF 13.2 / ON 13.5 / OFF 13.8 | with vs without | L3 closing | clicks and toggles; "jiske bina" | compare | 3 readable strings (accepted, §3) |
| 14 | 14.4 ON, resolved "with"; sparkle | the finish makes it alive | **L3 closed** | toggle_on + sparkle; "frame zinda" | proof | nothing new after 14.43 |
| 15 | near-still frontal frame, 1 %/s push; caption "nahi lagta" | - | **nothing open** | strings only; VO ends 15.70 | weak | **SOFT DROP RISK 14.5-16.3** (fix 2) |
| 16 | 16.0 C3 approach to the portal disc (visible from about 16.3); 16.8 C3 cut | through a point of light | midpoint break | reverse_swell 16.0-16.8; air_zoom + impact_soft 16.8 | new world | - |
| 17 | corridor of 30 frames; light wave 16.9-18.6 | 30 frames a second | **L4 opened:** how many in one second? | V6 16.95 "Ek second mein tees frames"; sparkle | scale | caption C2 over busy billboards: check at preview |
| 18 | 18.6 surge (7 samples); 18.9 counter `012` rolls | the counter runs | climbing | V7 18.90 "Yaani har second..."; whoosh_by 19.2 | where will it stop? | - |
| 19 | surge; counter rolling | - | climbing | slot ticks; whoosh_by 19.8 | - | - |
| 20 | 20.4 **`360` lands**, brake, push 0.5 | **360 a second** | **L4 closed** | glass_truth; "teen sau saath" 20.45 | number shock | glass tap auto-ducked under "teen": check by ASR on the mix |
| 21 | 360 holds (1 %/s); 21.9 lockup exits, lanes rise | - | - | V7 ends 21.52; bar_grow 21.9 | read the number | 1.5 s hold, OK |
| 22 | three lanes pulse with the real stems; legend `VO · AI voice / SFX / MUSIC` | 3 sound tracks | - | V8 22.15 "Aur awaaz ke teen tracks" | the voice draws its own waveform | - |
| 23 | lanes scroll | - | build | VO ends 23.39 | - | VO-free 23.39-26.75 by design |
| 24 | 24.0 RUSH: 29 stacks fly back into one; lanes sink; push in | it all converges | build to the payoff | whoosh_by 24.3 / 24.75; riser from 24.6 | tension | - |
| 25 | rush ends 25.5; **25.8 drop-out** freeze | - | at its peak | silence 25.8-26.067 | held breath | - |
| 26 | 26.067 play click, slam; 26.267 C8; **26.4 the frame PLAYS**; `EK FRAME KI / keemat` builds | its worth | **L1 closed (79 %)** | ember_slam + dhol drop; V9 26.75 "Keemat..." | release | loudest moment must be within ±0.2 s of 26.4 |
| 27 | glyphs and underline; sub `banane wala jaanta hai` 27.7-28.1 | the maker knows | - | "banane wala jaanta hai" | the quotable line | - |
| 28 | frame playing, lockup set | - | - | dhol chaal | - | **no bonus beat** (fix 3) |
| 29 | 29.1 lockup exits; 29.4 END CARD over the dimmed playing frame; ring 29.5 | the ask | - | V10 29.60 "Jo kehta hai..." | send setup | - |
| 30 | CTA title from 29.75; signature 30.4; sub ~30.55 | the send target is named | - | "editing mein kya hai" | "yeh toh woh hai" | the USSE spelling (fix 5) |
| 31 | card settled 31.25 | - | - | "usse bhejo", ends 32.82 | - | - |
| 32 | settled hold over the playing world | - | - | VO-free from 32.82 | - | no rewatch cue on screen (fix 3) |
| 33 | 33.0 loop cross-fade: hook lockup and chip return; 33.233 card exits; push into f0 | - | the loop | reverse swell + cymbal end 33.6, into f0 | seamless replay | hook B master jumps here (accepted) |

**Measured rules:**
- **Frame 0 striking:** PASS. First visual change 0.3 s, a big one at 0.9. VO onset 0.10.
- **A visible change every 2.5 s or less:** PASS. Longest gaps:
  - 14.43 to about 16.3: 1.9 s.
  - 31.25 to 33.0: 1.75 s (the end-card hold, over a moving world).
  - 20.4 to 21.9: 1.5 s.
- **New information every 6 s or less:** PASS. The longest stretch is 22.15 to 26.4 (4.25 s), and it is escalation.
- **One open loop by 3 s, closed after 70 %:** PASS, but implicitly. The picture opens L1 at 0.9-2.4 and the payoff closes it at 26.4 (79 %). The count itself is answered at 4.8, so the middle is held by the nested loops L2, L3 and L4.
- **Re-hook between 12 and 18 s:** PASS, at 12.0 and 16.8.

**Drop-risk windows** (3 s windows with no reason to stay):
- None fully dead.
- **14.5-16.3 is soft**: at 43-48 %, after L3 closes, no loop is open, the picture is near-still and the voice stops at 15.70 (fix 2).
- **26.4-33.6 is soft**: the post-payoff tail is 7.2 s (21 %) with no new information after the send target, and the hidden JD sits only on caption line 7 (fix 3).
- 6.0-12.0 carries a low list-fatigue risk.

---------------------------------------------------------------------------------------------------------------

## 5. Open loops and the loop bridge

- **L1** (what is inside 0.03 s / what is it worth): opened by the picture at 0.9-2.4, turned by "Lekin" at 3.07, closed by "Keemat..." at 26.75.
- **Nested loops:**
  - L2, the names: 5.4-11.4.
  - L3, the invisible layer: 12.0-14.4.
  - L4, how many in a second: 16.8-20.4.
- **Bridge:** "...usse bhejo." (ends about 32.82) leads into "Aap ne ise palak jhapakte dekha." (0.10). The friend you send it to becomes the "aap" of the hook, so this is a story loop, not a sentence loop. It works because the picture and audio loop is exact: the frame plays through, the hook lockup and chip return, and the swell is released by the f0 transient.
  - After fix 1, that transient is `impact_soft`, not the HERO `trailer_hit`. The loop logic is unchanged.
- **Rewatch triggers:**
  - The rim-light pane standing alone (8.4).
  - The 0.6 s tag run.
  - The 360 odometer.
  - The hidden JD. Today it is static and mentioned only on caption line 7, so almost nobody is told to look (fix 3).

---------------------------------------------------------------------------------------------------------------

## 6. Share, comment, packaging

- **Send sentence:** a video editor, designer or motion artist sends this to the friend or relative who once said "editing mein kya hai?" Trigger: an indirect message plus pride ("one frame of my work has 12 layers, ab samjhe?"). Second sender: editor to editor, as in-group awe ("har second 360 layers"). Both answers are concrete, so reach is not capped.
- **CTA:** `USSE YEH / bhejo` + sub `jo kehta hai "editing mein kya hai?"`, with V10 spoken. One ask, named recipient, true, imperative. Spelling: fix 5.
- **Comment prompt:** "Is frame mein JD chhupa hai. Mila?" A low-effort find, and true by construction: layer 03, (836, 330). Fix 3: pin it as the first comment when posting and move it to caption line 2. The answer is pinned after 24 h. No "Comment JD" (there is no DM automation).
- **Cover:** f153 (5.1 s), the side-on stack with `12 / LAYERS`.
  - The title (y 297-548) is inside the 3:4 crop (y 240-1680).
  - At 210 px wide, "12 LAYERS" reads clearly (my test: previs F1 / B1 / B2 cropped to y 240-1680 and scaled to 210 px). The face is about 10 px, so its emotion does not read. That is acceptable: the object is the hero, and the tile stands out in the grid.
  - It is the darkest of the candidates: YAVG 28.3 against 46.9 for f0 and 47.3 for the payoff.
  - The lead's alternative, f0, is the full house formula and reads well at 210 px. Keep f153 as the default.
- **Caption line 1:** `Ek frame mein kitni layers? Video editing ka sach`. 49 characters, counted. It carries the search keyword "Video editing" inside the ~55 characters the Reels viewer shows, and it is a question that invites guesses.
- **Hashtags:** 4: #videoediting #motiongraphics #videoeditor #jawadmp4.
- **Audio:** original VO + SFX + score, no trending track baked in. Version B (VO + SFX) exists for an in-app song. Audio name: "Original audio · Aap ne ise 0.03 sec dekha · @jawad_mp4".
- **Search note:** the first 3 s of speech contain no search keyword. This is by design (SLATE §2.9 moved फ़्रेम out of the hook). Caption line 1, the alt text and the audio name carry the keyword instead, and "frame" is spoken at about 3.9 s.
- **AI disclosure:** synthetic voice, and the character sheet may be AI-generated. Meta's "AI info" is ON by default. The lane label `VO · AI voice` and the caption line "Voice: AI (TTS)" are honest. This is the lead's open question Q5, not skipped.

---------------------------------------------------------------------------------------------------------------

## 7. Fixes (ranked by expected retention impact)

### 1. f0 transient: 0.0-0.4 s, hook audio. Owner: creative-director (BRIEF §5 row 1, §6.1, §6.3, §11)

**Evidence:**
- BRIEF §11 cues `trailer_hit` -6 at 0.000, a HERO impact in `sfx_jawad.HERO`. V1A says "Aap" at 0.10.
- The mandated `J.fit_under_vo` raises `HeroOnWordError` (nearest legal hit 2.49 s). I measured it with the planned word times.
- Even with `hero='warn'`, a 0.3 s impact body would mask the first word of the hook for every sound-on viewer.
- Separately, `trailer_hit` accepts only `seed` and `pitch`: `params=dict(dur=0.30)` raises `TypeError`. `dur` must be a cue-level key.

**Change:**
- Replace the f0 hit with `impact_soft` (dark band) at -8 dB, cue-level `dur=0.25`. I measured it: it passes `fit_under_vo` with no ducking.
- Keep the pause click at 0.3 as the hook's real sound event.
- Keep the music's harmonium swell as the bed.
- The loop bridge (swell into the f0 release) is unchanged.
- In BRIEF §6.3, "frame 0's `trailer_hit` is the release" becomes "frame 0's `impact_soft`".

### 2. The soft window at 14.5-16.3 s. Owner: creative-director (BRIEF §7.3 P8, §10 C3 params)

**Evidence:**
- After the flick resolves at 14.4, the frontal view only pushes 1 % per second (`D x (1 - 0.01 (t - 13.2))`, aperture 0).
- L3 is closed, and the voice ends at 15.70.
- The C3 approach is under 3 % until 16.25, so the next visible change comes at about 16.3. That is 1.9 s near-still, at 43-48 % of the runtime, where curves usually sag.

**Change** (legal, because the frame is still paused and the camera may move):
- From 14.6, push toward the portal disc at about 4-5 % per second (`D x (1 - 0.045 (t - 14.6))`, about 6 % by 16.0).
- Over 15.0-15.8, rack focus from the front panes to pane 03 (aperture 0 to ~200, `inout_cubic`). The portal disc then blooms into the obvious next place to go, and C3 flies into it.
- Do not animate any layer: the frame stays frozen.
- Re-measure `center`/`r0` for C3 at the new 16.0 camera with `camspec.py`.
- Re-check that caption C1's bboxes (y 276-496) stay above the frame's top edge (now about y 505 by my estimate).

### 3. A bonus beat and a visible rewatch trigger: 28.2 s and the post. Owner: creative-director (BRIEF §7.2 layer 03, §16)

**Evidence:**
- After 26.4 there are 7.2 s (21 %) with no new information, and there is no bonus beat (playbook §3.4: two payoffs beat one).
- The only rewatch device, the hidden JD, is static and appears only on caption line 7. The Reels viewer shows about 55-60 characters [2nd], so viewers never see the prompt.

**Change:**
- Add a 2-frame glint of the hidden JD inside layer 03 at f846-f847 (28.2 s, beat 3 of bar 11), emissive x0.35 to about x1.2 and back.
  - This is legal: the frame is playing (t >= 26.4), and the light comes from layer 03 itself, so there is still no 13th layer.
  - The payoff lockup and sub line are settled by 28.1, and (836, 330) sits above the lockup box (y >= 441).
  - No SFX for it.
- In the post:
  - Pin "Is frame mein JD chhupa hai. Mila? 👇" as the first comment when posting.
  - Move it to caption line 2.
  - After 24 h, reply with the answer ("Layer 03, top right, roshni ke beech") and pin that reply.

### 4. Re-hook caption keyword, and one source of truth: 12.0-16.25 s. Owner: hinglish-scriptwriter

**Evidence:**
- SCRIPT C6 allows one keyword per line, so V5's flame word lands on "zinda" at 14.43. The caption at the re-hook instant (12.05, "Aur ek layer...") would be plain white.
- `snake_captions` only needs one keyword per chunk (its `check()` flags more than one in a chunk), and `vo_chain` takes any number of `*` marks per line.
- BRIEF §15 and the previs `F3_rehook_13p2_safe.png` show the flame on "layer..."
- The brief and the script also disagree on V2, V8 ("ki"/"ke"), V9, V10 and on the C2/C3 chunks.

**Change (zero credits):**
- Set the T1/V5 rom to `Aur ek *layer... jiske bina frame *zinda nahi lagta.` The chunks become `Aur ek *layer*...` / `jiske bina` / `frame *zinda*` / `nahi lagta`.
- Re-run `vo_chain process` with the new `--rom` after the take. The audio does not change.
- Update `script.json` `caption_keyword`.
- The creative-director copies the approved lines (C1-C5) and these chunks into BRIEF §2, §5, §9 and §15, so the builder and the caption-designer read one version.

### 5. End-card spelling for both sides: 29.4-33.6 s. Owner: creative-director (card text) with the hinglish-scriptwriter (T3)

**Evidence:**
- The card says `USSE YEH bhejo`, but the VO says उसे.
- In Roman Urdu, and in this project's own playbook ("Aapka video *usse* sasta dikhata hai", hooks_retention_captions.md line 186), "usse" means उससे, "from/than him". A Pakistani reader can parse the send line as "send this from him".
- Sends are this reel's main reach driver.

**Change (needs the lead's OK, because SLATE §5.1 locks the CTA):**
- Card `USKO YEH / bhejo`: measured 455.5 px at `jw_caps` 86, against 429.1 px for the locked line, so it fits.
- V10 DEV `...उसको भेजो।`, Roman token `usko`: +1 syllable, estimated end about 33.0 s, still before the card exit at 33.24.
- If the lead keeps "USSE", keep the VO at उसे and write "usey" in the SRT.

**Not ranked (checks for the VO and preview stages):**
- (a) Number intelligibility. "baarah" (4.80) and "teen" (20.45) start 0-50 ms after a glass tap. `fit_under_vo` ducks the tap to -8 dB, which I measured. Acceptance: faster-whisper run on the **mix** returns बारह and तीन सौ साठ.
- (b) Check caption C2 (16.9-20.8, y 1159-1356) for legibility over the busy corridor at the preview.
- (c) Optional: the 29 billboards are identical copies. Two or three pre-flattened variants (different `tl`) would make "30 frames" read as a second of video rather than a freeze. Cheap, and it adds a rewatch detail.
- (d) For the lead, outside this reel: `pehle_wala/BRIEF.md` hook B also lists `trailer_hit` at f0 with VO at 0.10. The same `fit_under_vo` raise probably applies there.

---------------------------------------------------------------------------------------------------------------

## 8. What can proceed now

- **TTS:** T1 (V5-V8, the pronunciation test), T2 (V2-V4), T4 (V1A) and T5 (V1B) as written in SCRIPT §7. Fix 4 changes only the rom flags, at zero credits.
- **T3** (V9 + V10) waits for the lead's call on fix 5. If the lead says no, record T3 as written.
- **Builder:** fixes 1-3 are BRIEF edits by the creative-director and do not block the stills gate (§7.5).
- **Next gate:** red-team the preview (`<RW>/out/*_preview.mp4`): measure frame 0, VO onset, change events, phone tiles and loudness, and check this map against the real word times.

## 9. Claims I could not verify (dated)

- **Platform claims** [2nd]: sends per reach weigh most for non-followers; skip rate is the first 3 s; the Reels viewer shows about 55-60 caption characters; Trial Reels need 1,000+ followers; the 5-hashtag cap. All come from `hooks_retention_captions.md`, checked on 2026-10-08 against vendor and trade sources. I did not re-check them today.
- **Account:** @jawad_mp4's Trial Reels eligibility is unknown.
- **Vlad's pronunciation** of साठ, फ़्रेम, ज़िंदा, झपकते, क़ीमत: untested until T1/T4 (2026-10-08).
- **VO timings:** every one is a syllable-model estimate (±10 % per line) until the real takes are processed.
- **Hidden JD findability:** previs only. The BRIEF measured +18.5 code values; I viewed the frame-0 crop at 1:1.
- **"usse" for Pakistani readers:** my language judgement plus the project's own usage. It has not been tested with readers.
- **No forecast:** 1M views is a stretch goal. Reach also depends on distribution, timing and luck.
