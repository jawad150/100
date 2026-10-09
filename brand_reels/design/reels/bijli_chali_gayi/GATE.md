# GATE: Reel 2 · C11 · Bijli Chali Gayi: concept + script gate (r1)

Date 2026-10-08 · Author: viral-strategist · Stage: concept + script, before any TTS take.

**What I read:**
- `SLATE.md` §0, §2, §3.2, §4 and §5 (the series bible)
- `BRIEF.md` (21:30)
- `SCRIPT.md` + `script.json` (draft v1, 21:47)
- `packet.yaml`
- `research/hooks_retention_captions.md`
- `panel_viral.md` §3 and §4.3
- the prior SRT `workspace/brand_reels/prior/captions_roman_urdu.srt`

**What I looked at.** The brief proofs (`out/brief_proofs/p0-p9`) and the finished 3D room plates (`out/sheets3d/bcg_finals_room_{lit,torch}.png`). I viewed them at 360 px wide (a phone at arm's length) and at 210 px wide inside the 3:4 grid crop.

**What I ran:**
- token-parity checks on `script.json`: DEV/ROM 1:1, NFC, no Latin in DEV, no first person in ROM
- `T.measure` on the lockups and the CTA
- `signalstats` on the plates
- the syllable-rate model in SCRIPT §5, re-run on the proposed trims
- two WebSearch re-checks of algorithm claims (§9)

## Verdict: FIX

All four gates pass: **Hook 8 · Share trigger 8 · Truth PASS · Brand 8**. The concept stands and needs no new idea. The
verdict is FIX, not SHIP, for three reasons:
1. **The VO does not fit its windows at Vlad's normal pace.** 69 words in 20.6 s of speaking windows need his fastest
   delivery at the maximum 1.10x on every line. At his average rate the dense block 16.4-26.3 s runs 1.17 s over. A rushed
   narrator over the twist, the joke and the turn into the payoff is the biggest swipe risk after the hook. Three
   zero-credit trims fix it before T2 and T4 are generated (fix 1).
2. **One real drop-risk window: 5.5-8.0 s on the rooftops.** It is the only 3 s stretch with no picture event, it sits
   on the darkest set, and its VO is exposition (fix 3).
3. **The hook's open loop is visual only, and frame 0's brightness is not proven yet.** The stand-in proof p0 measured
   YAVG 29.4 (limited range), under the brief's own fail line of 30. The real lit plate measures 46.3 (full range),
   so this is a gate-still check plus one legibility change, not a redesign (fix 2).

Hooks A and B stay as locked (A public, B Trial Reel; they differ only in f0-f79).

---------------------------------------------------------------------------------------------------------------

## 1. Scores (0-10, one line of evidence each)

| axis | score | evidence |
|---|---|---|
| Hook | **8** | **Hook A:** the reel loses its own power at 0.333-0.467 s. *Bijli* glows from 0.5 s, the torch clicks on at 0.667 s, `CHALI GAYI.` is readable by about 1.0 s and the VO starts at 0.1 s. All three channels land by 1.5 s, and it reads muted. **Why not 9:** frame 0 is an ordinary lit room, and the on-screen text repeats the VO word for word. A muted non-follower gets an event ("the power went"), not a question. "Yaad hai?" is spoken only. |
| Relatability | 9 | The things on screen are shared Lahore/Karachi and Delhi/Lucknow childhood: power cuts, the whole mohalla on the chhat, the street-wide "AA GAYI!", the backup-box double beep, homework by candle. Anyone who has lost a file knows the Ctrl+S reflex. |
| Share trigger | **8** | **Main send:** shared nostalgia plus amusement (the gag where the power dies again). Grown-up desi kids send it to the cousin or school friend they shared those rooftops with. **Second send:** in-group code (render drained to 0 %, Ctrl+S on 8ths), from editors to editor friends. Not 9: after 13 s the second half narrows to editors. |
| Novelty | 8 | New to his page and to the desi feed: the reel obeys electricity (power-cut grammar: brownouts only darken, the camera drifts while the power is off and locks when it is on, the power returns at the end). Familiar: "90s kids yaad hai" montages and the UPS-beep meme, which the brief's Director's pass already killed. Nothing from his Genjutsu, Yaadein-delete, OpenArt or spotlight covers. |
| Truth | **PASS** | Narrator is "hum / har desi editor / aap" (grep: no main / meri / mujhe / mera). Nothing about Jawad's childhood, home, PC or clients. "Har tees second" is a joke, spoken as a word and never shown as a digit. No utility, city or country names, no money, no UPS or inverter label, no laptop, no ERROR or unsaved dialog. ⚑ low risk: JD's profile sits under "Bijli ne humein…", so some viewers will read it as his own memory. The collective "humein" is the SLATE's accepted framing, but the lead should confirm Jawad is comfortable with it. |
| Loop | 9 | The V12 question "Aap ke ghar light jaane pe kya hota tha?" is answered on replay by V1 "Bijli chali gayi.". S8b is the frame-0 composition on the same clock (fan angle, CRT playhead). The `reverse_swell` releases into the f0 `impact_soft`, and on replay the power dies again at 0.333 s. B's seam (lit to torch-lit) is a deliberate cut: "the power dies at the seam". |
| Feasibility | 8 | The 3D finals are already rendered: the lit room plate measures YAVG 46.3 / YHIGH 108, the torch plate 19.6 / 27. Everything else is 2D sprites, masks and the toolkit. VO is 7 takes, about 17.5 credits. Risks: the VO fit (fix 1) and the rooftop reading at phone size (fix 3). |
| Brand | **8** | Serif flame keywords at the hook, payoff and end card (*Bijli* / *sabr* / *batao*), white grotesk caps, warm black, JD with a flame rim, `@jawad_mp4` card. The `dusk` look keeps red-orange in the top 5 %. f0's lime-wash room is grey for 0.47 s by design. See §6 for the cover's indigo window. |

Gates: Hook 8 ≥ 8 (on the line) · Share 8 ≥ 7 · Truth pass · Brand 8 ≥ 7. **All pass.**

---------------------------------------------------------------------------------------------------------------

## 2. Three-channel hook test

### 2.1 Hook A (public), f0-f79

| channel | what lands | when | verdict |
|---|---|---|---|
| visual | f0: the lit 2000s room, fan at 4.5 rev/s with 5-sample blur, CRT with a playhead, `impact_soft` transient. Brownout at f10, CRT collapses to a dot f12-f15, torch at f20, beam sweeps to the box f24-f38, LED pulses at f40 and f60 | first change 0.333 s (rule ≤ 1.0) | PASS, if f0 really reads bright (fix 2). Stand-in p0 is YAVG 29.4 limited (fail < 30); the real plate is 46.3 full range before the finish |
| on-screen text | `*Bijli* / CHALI GAYI.` (3 words, ≤ 6). H1 glows 0.35 → 0.70 over f15-f24, H2 rises f18-f36 | readable by about 1.0 s | PASS. At 360 px and at 210 px (grid crop) both lines read. One note: it is a transcript of the VO, not a headline (research §0 rule 2), which is acceptable here because the picture carries the stop |
| spoken | "Bijli chali gayi." 0.100-1.150 · beeps 1.333 / 2.000 · "Yaad hai?" 2.200-2.600 = **5 words, done by 2.6 s** | onset 0.1 s (rule ≤ 0.3) | PASS (≤ 7 words by 2.7 s). The risk is length, not words: V1 must end before the beep at 1.333 and V2 before f79 (2.633), with 0.43 s for a rising "hai?" (fix 5) |
| muted | the room dies and the keyword glows, then a searching torch and a blinking LED | | PASS. The searching torch is a visual micro-loop |
| open loop by 3 s | for followers: "what does this have to do with editing?" For non-followers only the picture carries it: the CRT dies *with something on it* | 0.4-0.5 s | weak. Make the CRT's edit legible (fix 2) |

### 2.2 Hook B (Trial Reel), f0-f79

| channel | what lands | verdict |
|---|---|---|
| visual | f0 is a torch-lit room with the LED pulsing on f0 and f4, and the HB lockup already mid-rise | PASS. Text on f0 offsets the dark (stand-in p8: YAVG 38.3 limited) |
| text | `YEH / *awaaz* / YAAD HAI?` (4 words), readable by about 0.9 s | PASS |
| spoken | "Yeh awaaz... yaad hai?" 0.300-1.950 (4 words). The beep on f0 is the subject, and the f40 beep fills the "..." | PASS |
| muted | the text names a sound a muted viewer cannot hear; the LED blink is the only stand-in for it | weaker than A muted. The LED has to read at 360 px (minor fix 7) |

**A/B:** this is a clean test of the mechanism: a pattern interrupt (A) against a sound memory (B), with a frame-identical
body from f80 (2.667 s). Judge on skip rate first, then on sends per reach. Trial eligibility is unconfirmed (§9).

### 2.3 Hook lab (0-2 each: Gap, Specificity, Fit, Voice; Truth* and Pull* are pass/fail)

| # | mechanism | on screen | spoken | Gap | Spec | Truth* | Fit | Voice | Pull* | /8 | call |
|---|---|---|---|---|---|---|---|---|---|---|---|
| A | pattern interrupt (the reel's own power dies) | `*Bijli* / CHALI GAYI.` | "Bijli chali gayi. … Yaad hai?" | 1 | 2 | P | 2 | 2 | P | **7** | **recommended (public)**. Gap goes to 2 with fix 2 |
| B | sound memory / curiosity | `YEH / *awaaz* / YAAD HAI?` | "Yeh awaaz... yaad hai?" | 2 | 1 | P | 2 | 2 | P | **7** | **A/B alternate (Trial)**. Spec is 1 muted (an unlabelled box, a sound you cannot see) |
| R1 | editor pain | `LIGHT GAYI · *Ctrl+S?*` | "Light chali gayi. Ctrl+S dabaya tha?" | 2 | 2 | P | 2 | 1 | P | 7 | reserve: editor-only at f0, and कंट्रोल-एस inside the hook is a pronunciation risk |
| R2 | relatable callout | `CHHAT PE *raatein*?` | "Agar bachpan chhat pe guzra hai..." | 1 | 1 | P | 2 | 2 | P | 6 | reserve |
| N1 | contrarian | `PEHLA *teacher*: BIJLI` | "Har desi editor ka pehla teacher? Bijli." | 2 | 1 | P | 2 | 2 | P | 7 | later editor-only cut. It drops the slate's pattern-interrupt mechanism and narrows reach at f0 |
| N2 | result first | `AA *gayi!*` over lit rooftops | "Aa gayi!... aur phir chali gayi." | 2 | 2 | P | 2 | 2 | P | 8 on paper | rejected: it spends the 8.0 s re-hook gag in the first second, and the bright → dark device then plays twice |
| N3 | stakes / specificity | `RENDER *63%*` | "Render tirsath pe tha. Bijli chali gayi." | 2 | 2 | P | 1 | 2 | P | 7 | rejected: f0 would need the modern desk, which breaks the 2000s → now order. It is also close to the rejected C05 "Render 99%" |
| N4 | POV | `POV: *bijli* GAYI` | "POV: do hazaar paanch, aur bijli abhi gayi hai." | 1 | 1 | P | 1 | 1 | P | 4 | rejected: a year that is not everyone's year, and 9 words |

---------------------------------------------------------------------------------------------------------------

## 3. Script against the binding sources

| check | source | result |
|---|---|---|
| SLATE §2.8: cheer = text slam + wordless CC0 cheer + appliance chorus, no synthesised voices | BRIEF §6.10 | PASS: `crowd_cheer_real` -10 dB at 8.033 and -8 dB at 29.5; QA runs whisper for words (§8) |
| SLATE §2.8: a desktop PC that dies at once, never a laptop "unsaved" dialog | BRIEF §2, §6.2 S5 | PASS: the monitor collapses and the HUD drains to 0 %, with no dialog |
| SLATE §2.8: re-hook at 16.0 s (bar 6) | BRIEF §6.5 | PASS: 46 % of the runtime, inside the 12-18 s rule |
| SLATE §2.6: end card ≥ 4.0 s, settled ≥ 1.5 s | BRIEF §6.5 | PASS: dur 4.0 (f920), settled 1.79 s (32.5-34.3). The 4.0 s is the toolkit's floor; V12 runs over the card, so it is not dead time |
| Hooks ≤ 7 spoken words by about 2.7 s; ≤ 6 on-screen words; splice f80 | SLATE §3 preamble | PASS: A 5 words / 3 on screen; B 4 / 4 |
| Typing dots are C02's; keycaps are C11's; Ctrl+Z is not C11's | SLATE §2.3, §3.1 | PASS |
| Faces: `suit_profile` (3.33 s ≤ 3.5), `suit_smiling` (1.33 s); not used in any other reel | SLATE §5.2 | PASS |
| Underline ≤ 3; features ≤ 4 (≤ 2 ★), never two within 2 bars | bible §5.1 | PASS: 2 underlines; L7 ★, L8, L4 ★ spaced 3 and 4 bars apart |
| Voice: never "main"; JD not voiced; VO onset ≤ 0.3 s | bible §5.1 | PASS (grep on ROM) |
| Banned list: ERROR/unsaved/delete, laptop, UPS/inverter label, money, place names, flags, cricket, domes or minarets, spotlight-clunk opens | bible §5.1, BRIEF §2 | PASS on paper; the 3D plates show no legible text or logos |
| **Truth** | brand skill rule 4 | **PASS** (see §1). The only number is "tees", spoken as a word |
| **Cross-border** | research §2.5 | **PASS.** Every word is everyday on both sides: bijli, light, mohalla, chhat, bachche, dushman, desi, ungli, khud, sabr, ghar. Nukta forms ख़ुद and आवाज़ are kept for Pakistani ears. "Load-shedding" (a Pakistani political term) is correctly avoided. Rooftops: bare heads, no religious or national markers |
| **Word budget vs DUR** | research §3.1; SCRIPT §4-6 | **FIX.** 69 words (A) / 68 (B) is far under the 90 cap, but about 14 s of this reel is designed VO-free (beeps, slam and cheer, render silence, power return). The windows add up to 20.6 s, i.e. 3.35 words/s or 5.6 syllables/s, which is Vlad's neutral pace at maximum speed-up on every line. At his average pace (4.95 syllables/s after 1.10x), the dense block 16.4-26.3 needs 10.71 s against 9.54 s available, and the rooftop block is 0.08 s over. Fix 1 brings A to **65 words / 107 syllables**: the dense block then needs 9.29 s (0.25 s spare, and it fits at 1.08x average, a warmer read) and the rooftop block 2.22 s of the 2.35 s available |
| **Keyword per line** | bible §5.1 captions | PASS with one change. Bijli, Yaad, awaaz, sabr and ghar are hidden behind designed text; Light, chhat, wapas, bachche, editor, dushman, tees and editing are good. Change V8 *ungli* → *khud*, the word the delivery note itself stresses ("khud with a wink"). The glowing word should sit on the spoken stress (minor fix 6) |
| **House spelling** | prior SRT | **FIX.** Jawad's SRT writes "dikhai" (दिखाई), with the doubled vowel only in a stressed first syllable ("aaya", "aata", "baad"). So सिखाई / सिखाया are "sikhai / sikhaya", not "sikhaayi / sikhaaya". The payoff caps line `BIJLI NE SIKHAAYA` is the most-read text after the hook (fix 4) |
| **CTA** | bible §5.1 | PASS: `COMMENT MEIN / *batao*` (734 / 407 px), sub `Chhat ya candle?` (502 px), V12 spoken on the hold. That is one ask, it is true, and it fits a nostalgia reel (research §3.5: "comment a memory"). The sub gives a one-word A/B answer and V12 the open version. Not "Comment JD" |

---------------------------------------------------------------------------------------------------------------

## 4. Retention map (one row per second; times from BRIEF §6.1-6.10 and SCRIPT §4, estimates until the takes exist)

Loops: **L1** (macro) is opened by the dead CRT and "Yaad hai?" (where does this go, and what did the dark leave us?) and
closed by *sabr* at 26.667 s (77 %). **L2** "jab wapas aati thi…" runs 6.6 → 8.0. **L3** "what happened to the kids?"
runs 11.0 → 13.37. **L4** "render 63 %: will it finish?" runs 13.33 → 16.0. **L5** "what does the editor do now?" runs
18.67 → 23.67. **Q** is the end-card question, answered by frame 0.

| s | picture change | new information | open loop state | audio event | reason to stay | risk |
|---|---|---|---|---|---|---|
| 0 | f0 lit room (fan, CRT playhead, tube light); 0.333 brownout; 0.40-0.50 CRT collapses to a dot; 0.5 *Bijli* glows; 0.667 torch clicks on; 0.8 beam starts to sweep | the power just died, inside the reel | L1 opens (an edit dies on the CRT) | `impact_soft` f0; VO "Bijli chali gayi." 0.1; tube_flicker, crt_off, relay_click, fan wind-down, shimmer, torch click | pattern interrupt | f0 must read bright (fix 2). Six SFX onsets sit under the first 3 words: check them with whisper on the mix (note 9) |
| 1 | beam reaches the box (1.27); LED pulses f40/f44; `CHALI GAYI.` settled | the backup box | L1 open | **backup_beep** 1.333 | recognition of the beep | the unlabelled box must read as "the backup box" when muted |
| 2 | LED pulses f60/f64 (cover frame); dust in the beam; lockup exits 2.40-2.63 | "Yaad hai?" | L1 open + memory invite | beep 2.0; VO "Yaad hai?" 2.2-2.6 | the nostalgia question | "Yaad hai?" has 0.43 s before the f79 splice (fix 5) |
| 3 | 2.667 hard cut: a match flares and a candle catches; 3.333 the pankhi swings in | the candle ritual | L1 open | match_strike 2.667; leaf_rustle 3.333; VO "Light jaati thi," 3.0-4.0 | warmth, the next memory | V3a's 0.75 s window needs 6.7 syllables/s; let it run to 4.0 (SCRIPT §4) |
| 4 | pankhi swing 4.0; homework copy by the candle; 4.667 swing + tilt up begins | homework by candlelight | L1 open | leaf_rustle; VO "toh poora mohalla…" from about 4.3 | detail | exposition starts |
| 5 | 5.333 the tilt through the ceiling lands on the night rooftops (settles 5.33-6.0) | "chhat pe" | L1 open | whoosh_slow 5.333; crickets + night air up | world change | **the rooftop is the darkest set** (stand-in p9: YAVG 12.4 full / 26.6 limited, black with dots at 360 px) |
| 6 | rooftops: drift, neighbours fanning, parapet candles | the whole mohalla on the roof | L1 open | VO "…chhat pe hota tha." to 6.45; V4 from 6.6 | recognition | **DROP RISK 5.5-8.0** (fix 3): no picture event between 6.0 and 8.0 |
| 7 | (nothing new planned; fix 3 adds a false-start flicker at 7.333) | "Aur jab wapas aati thi…" | **L2 opens** (6.6) | V4 ends ≤ 7.85 | the hanging sentence | V4 runs 0.08 s long at average pace (fix 1) |
| 8 | 8.0 bulbs cascade far → near; camera locks; **AA GAYI!** slams | the power is back | **L2 closed** | power_thunk, impact_soft, cheer -10, fans up, tube_light_on | **re-hook 1**: laughter and relief, the most-sent memory | the slam is 832 px wide (inside 940) |
| 9 | bulbs blooming, fans spinning, cheer; the slam static from 8.6 | | | cheer tail | the cheer | 1.4 s of static text (fine) |
| 10 | 10.0 everything dies again, the cheer cut dead; 10.27-11.03 L7 torch-beam sweep | the gag | | power_thunk off; distant beep 10.333; L7 whoosh + shimmer | the laugh; the rule "the reel obeys electricity" lands | |
| 11 | old room by torch; the torch finds the homework copy (11.33-12.2); slow push | "Phir woh bachche bare hue." | **L3 opens** | VO V5 11.0-12.5 | the turn, a new chapter | |
| 12 | torch to the dead CRT and the box | | L3 open | beep 12.667 | callback to the hook | |
| 13 | 13.333 lights on: modern edit desk, render 63 %, cut on the word "editor" | "Kuch editor ban gaye." | **L3 closed**; **L4 opens** | power_thunk lp 1100; edit_suite bed | the twist. Easter egg: the monitor shows the rooftop still (the editor is cutting this memory) | non-editors may feel "not for me" here |
| 14 | 14.667 63 → 64 % | | L4 open | ui_tick; VO ends about 14.4 | the render ticking | soft: no VO for 1.6-2.0 s (14.4-16.4) on a locked desk |
| 15 | 15.667 brownout dip | a warning (the viewer now knows the grammar) | L4 at its peak | tube_flicker | anticipation | |
| 16 | **16.0 the power dies mid-render**: monitor collapses to a line, HUD drains 64 → 0 % in RED (16.2-17.33); 0.4 s VO silence | the enemy | **L4 closed** (the render dies) | power_thunk 0 dB, crt_off, sub_drop; silence; V7 from 16.4 | **re-hook 2** (46 %): pain plus a callback to f0 | |
| 17 | 0 % pulses red at 1.5 Hz; dark desk; drift | "…sab se bari dushman." | | V7; slot_tick | ouch | |
| 18 | 18.37-18.93 L8 iris closes on the dead desk (f560 only is black) and opens on the Ctrl + S keycaps | the habit | **L5 opens** | camera_shutter, ui_click, reverse_swell (inside V7) | new world (macro) | f560 is the reel's only black frame (designed) |
| 19 | 19.333 first press + a `Saved` chip | the reflex | L5 open | keycap thocks; V8 from 19.33 | rhythm | |
| 20 | presses on quarters (20.0, 20.667); chips stack | | | thocks, ticks | rhythm | |
| 21 | 21.333 presses go to 8ths, a chip every 0.33 s | "…khud Ctrl+S dabati hai." | | V8 "Ctrl+S" near 21.33 | speed-up equals the laugh | कंट्रोल-एस pronunciation (SCRIPT risk 2) |
| 22 | 8ths continue; up to 3 chips at once | | | | dense, rewatchable (count the saves) | dense block over at average pace (fix 1) |
| 23 | last presses about 23.67 | "Har tees second." | **L5 closed** | V9 22.97-23.67 | punchline | |
| 24 | 24.0 power off: cut to the candle macro; 24.667 JD profile by candlelight | "Bijli ne humein editing nahi sikhaayi…" | **L1 re-asked**: then what did it teach? | impact_soft lp; V10 24.02-26.3 | JD's first appearance; the reversal | |
| 25 | profile holds; flame flicker, sparks | | L1 open | V10 continues | sincerity | 2.0 s of one pose (24.667-26.667), carried by V10 |
| 26 | 26.333-26.667 **drop-out**; 26.667 the payoff lockup rises on the bar downbeat | the lesson | | room tone -48, then impact_soft + heartbeat; harmonium from 26.667 | the held breath | |
| 27 | *sabr* settles glyph by glyph; underline 27.23-27.93 | "…sabr sikhaaya." | **L1 closed (77 %)** | harmonium peak + "sabr" 27.333 (beat 41) | **payoff** | सब्र pronunciation (SCRIPT risk 1); "SIKHAAYA" spelling (fix 4) |
| 28 | 28.0 cut to the candle macro under the lockup | | | riser from 28.133 | | the classic exit point after a payoff: no VO 28.05-31.8 |
| 29 | **29.333 L4: the power returns**: warm halation, tube strikes, fan spins up, JD smiles | the power is back (callback to 8.0) | bonus | power_thunk, sub_drop, appliance chorus, cheer at 29.5 (loudest moment) | relief, the bonus beat | must be warm halation, never a grey veil (BRIEF §8) |
| 30 | 30.667 end card starts over the lit room (the frame-0 composition) | CTA | | swish, shimmer | | |
| 31 | card animating; sub `Chhat ya candle?` | "Aap ke ghar light jaane pe…" | **Q opens** | glass_tap 31.417; V12 from 31.8 | the question | |
| 32 | settled from 32.5; fan and playhead running | "…kya hota tha?" | Q open | V12 | comment | |
| 33 | hold | | Q open | V12 ends ≤ 34.1 (rising, no breath) | | |
| 34 | 34.31 card exits with the loop push; 34.667 = f0 | | **Q answered by f0** | reverse_swell ends on DUR → f0 impact_soft | replay: the power dies again at 0.333 | |

**Picture-change gaps (on paper):** the longest are 6.0 → 8.0 (2.0 s, rooftops), 24.667 → 26.667 (2.0 s, JD profile)
and 32.5 → 34.31 (1.8 s, end-card hold). None is over 2.5 s, and new information arrives at least every 3.2 s.

**Drop-risk 3 s windows:**
- **5.5-8.0** (fix 3).
- Soft: 14.4-16.0 (the brownout at 15.67 rescues it), 24.7-26.7 (V10 carries it) and the post-payoff tail 28.05-31.8, where
  the power return is the bonus.

At the preview stage, re-measure the dark stretches with the scene-change probe: `select='gt(scene,0.08)'` under-counts
changes in near-black shots, so confirm those events on the 360 px sheets as well.

**Rewatch triggers:**
1. The monitor at 13.33 shows the rooftop still (the editor is cutting this very memory).
2. Eleven `Saved` chips in 4.3 s ("ginti karo").
3. On replay the lit room dies again.
4. With fix 2: the CRT at f0 dies with an edit on it, and the same timeline returns on the modern monitor.

---------------------------------------------------------------------------------------------------------------

## 5. Open loops and the loop bridge

- **Opened by 3 s:** yes, but quietly. For anyone who knows the page, the hook asks "what has this got to do with editing?".
  For a non-follower the only forward pull before 3 s is the searching torch and a screen that died with something on it.
  Fix 2 makes that "something" legible (an edit on the CRT). L1 then reads as "the dark took our edit, so what did it give
  us?", and *sabr* closes it at 77 % (rule: after 70 %).
- **Micro-loops:** L2-L5 above. A new one opens at least every 6 s from 6.6 s to 23.7 s, and each closes within 1.4-5 s.
- **Loop bridge:** this is a question-and-answer loop (V12 → V1), combined with a visual match (S8b = f0 on a shared clock),
  an audio loop (reverse_swell → f0 impact) and a story loop (on replay the power dies again). It is the strongest loop on
  the slate. Keep V12's tail trimmed to the word end + 40 ms, with a rising "tha?" and no breath (BRIEF §6.7).

---------------------------------------------------------------------------------------------------------------

## 6. Share, comment, packaging

- **Send sentence:** "A 22-35-year-old who grew up in a desi home with power cuts sends this to the cousin, sibling or
  school friend they spent those chhat nights with, because the AA GAYI! beat *is* their shared childhood ('yeh hum the').
  An editor sends it to editor friends because the 0 % render and the Ctrl+S reflex are their in-group pain."
- **Comment prompt (pinned, same as the card):** "Aap ke ghar light jaane pe kya hota tha? Chhat ya candle?" It is an
  open memory plus a one-word choice, with low friction and no keyword-DM (no automation exists).
- **CTA:** `COMMENT MEIN / *batao*`. One ask, true. This is the only comment CTA of the five, which gives the set some variety.
- **Cover:** f60 (2.000 s) of version A. Torch beam, `*Bijli* / CHALI GAYI.` (ink y 283-809, inside the 3:4 crop y
  240-1680), LED mid-pulse. **Readable at 210 px in the grid crop** (checked on proof p1).
  - Minor (7): at f60, H1 has settled to 0.75 opacity. Export the cover as a dedicated still with H1 at full glow.
  - Minor (7): keep the indigo window (x 720-1010, y 300-900) low in value beside the keyword. In the grid this reel
    should read flame-on-black, not like his violet "yaadein" cover.
- **Caption L1 (49 characters, counted):** `Bijli chali gayi: har video editor ki pehli class`. It restates the hook and carries
  "video editor" inside the 55 characters the Reels viewer shows. PASS.
  - Body: restate "Bijli ne humein editing nahi sikhai, sabr sikhaya." (spelling per fix 4).
  - Hashtags (4): #videoediting #nostalgia #editorlife #jawadmp4. PASS (3-5, no country tags).
  - The first 3 s carry no spoken craft keyword ("editor" arrives at 13.4 s). Search relies on caption L1 and the
    audio name. Accepted.
- **Audio:** original. VO + diegetic SFX + one harmonium swell. No song is baked in, and mix DRY allows an in-app track
  from 29.333 s. Audio name: "Original audio · Bijli chali gayi · @jawad_mp4".
- **AI label:** on, for both versions (synthetic voice; the character-sheet imagery may be AI-generated). Flagged, not
  skipped.

---------------------------------------------------------------------------------------------------------------

## 7. Fixes (ranked by expected retention impact)

### 1. VO fit: trim before T2 and T4 are generated (3.0-7.85 s and 16.4-26.3 s). Owner: hinglish-scriptwriter (copy change: the lead OKs it, creative-director mirrors it in BRIEF §2/§6.7)

**Evidence.** SCRIPT §4-6: every window needs 5.0-5.7 syllables/s, which is Vlad's fastest delivery at maximum speed-up.
The dense block is 53 syllables, 10.71 s at average pace against 9.54 s available. The rooftop block is 0.08 s over. A
rushed narrator over the twist and the payoff turn reads as robotic, and the brief's own F3/F4 would cut "humein" or the
"Har tees second" laugh.

**Change (0 credits, applied before the takes, so no retakes):**

| line | new Roman (caption tokens) | new Devanagari (TTS) |
|---|---|---|
| V8 (T-b, approved) | `Har desi editor ki ungli *khud Ctrl+S dabati hai.` | हर देसी एडिटर की उंगली ख़ुद कंट्रोल-एस दबाती है। |
| V7 (new) | `Aur bijli ban gayi sab se bari *dushman.` | और बिजली बन गई सब से बड़ी दुश्मन। |
| V4 (T-a, approved) | `Jab *wapas aati thi...` | जब वापस आती थी... |

- **Why V7 drops "editor ki":** V6 has just said "editor", and the picture is an editor's render dying. "Editor" would
  otherwise be spoken three times in 6 s.
- **Result:** A 65 words / 107 syllables, B 64. The dense block needs 46 syllables = 9.29 s at average pace (0.25 s spare);
  it also fits at 1.08x average, so there is no need for the maximum 1.10x. The rooftop block needs 2.22 s of 2.35 s.
  "Humein" and "Har tees second" both survive.
- **Files to update:** the take DEV/ROM for T2 and T4, `script.json` tokens, and the timing table.

### 2. Frame 0 has to read bright, and the CRT has to die with an edit on it (0.0-0.5 s, echoed at 13.33 and 16.0 s). Owner: creative-director (BRIEF §6.3, §6.9 CRT image, §7 gates)

**Evidence.**
- The hook only works if the room is visibly lit before it dies. Stand-in p0 measured **YAVG 29.4 limited (full 15.6)**,
  under the brief's fail line of 30, and reads as a dark brown room at 360 px.
- The real lit plate measures YAVG 46.3 / YHIGH 108 (full range, before the finish), so it can pass, but nothing yet proves
  the result after `dusk`.
- The CRT's mini-timeline (60 px/s playhead) is the hook's only forward loop for non-followers. At 360 px the CRT glass is
  about 113 × 80 px, and its blocks will not read as an edit.

**Change:**
1. Add to the §7 gate: the f0 still after `G.tx_finish` has YAVG ≥ 35 limited, the brightest 1 % ≥ 200, and the tube,
   fan and CRT read in a 360 px thumbnail.
2. Draw the CRT image bold: 3 clip tracks at least 36 px tall each at 1080 px, an IVORY playhead at least 6 px wide, FLAME
   and EMBER blocks, so a phone viewer sees an edit die at 0.40-0.50 s.
3. Give S5's monitor (13.33) the same timeline layout next to the rooftop still, so the 16.0 s death reads as "it's still
   happening".
4. Check the f0, f9 and f15 stills at 360 px before any full render.

### 3. Rooftop drop-risk window (5.5-8.0 s). Owner: creative-director (BRIEF §6.2 S3, §6.9 rooftops, §6.10)

**Evidence.**
- This is the only 3 s window in the reel without a picture event: the tilt settles at 6.0 and the slam comes at 8.0, with
  only drift and fanning silhouettes in between.
- It is the darkest set (stand-in p9: YAVG 12.4 full / 26.6 limited, black with dots at 360 px).
- The VO over it is exposition at maximum pace. panel_viral §4.3 flagged the same 4-7 s window.

**Change:**
1. Add one beat-locked tease at **f220 (7.333 s, beat 11)** under "…jab wapas aati thi…". A far window's tube light false-starts:
   2 frames snapped on, then dead, which is legal under the World Bible's "mains light snaps on, flickers darker, or dies".
   The near child's silhouette turns its head toward it.
2. Keep the tease visual only, or add at most a low 100 Hz hum blip: nothing in 1-4 kHz under V4.
3. Make the rooftops read at 360 px: warm candle pools on the charpai, the parapet and the silhouettes' rims (AMBER, the
   candle side), and a horizon band lifted enough that the skyline separates from the sky. No moon, no cold blue.
4. Hold the §8 floor on every frame: YAVG ≥ 18, ≥ 2,000 px above luma 90.

The tease also makes the 8.0 s payoff a three-step joke: setup, false start, AA GAYI!.

### 4. House spelling of the payoff (26.667-29.0 s lockup; V10/V11 captions). Owner: creative-director (P1 in BRIEF §2, §6.6) with hinglish-scriptwriter (ROM tokens)

**Evidence.**
- Jawad's own SRT writes "dikhai" (दिखाई) and doubles the vowel only in a stressed first syllable ("aaya", "aata", "baad").
- `SIKHAAYA` in 82 px caps is the most-read line after the hook, and the doubled "AA" makes readers stumble on both sides.
- Measured with `T.measure` (jw_caps): `BIJLI NE SIKHAAYA` is 819 px at 82 px; `BIJLI NE SIKHAYA` is 755 px at 82 px and
  792 px at the house 86 px. The caps can go back to the house size with 144 px side margins.

**Change:** P1 becomes `BIJLI NE SIKHAYA`, V10 `…editing nahi sikhai...`, V11 `*sabr sikhaya.` The DEV text and the takes
do not change. "jaati" and "aati" stay, because they follow "aata".

### 5. Hook VO safety: "Yaad hai?" placement (2.2-2.633 s). Owner: hinglish-scriptwriter (placement; a SLATE deviation needs the lead's OK)

**Evidence.** V2 has 0.43 s between the end of the second beep (2.203) and the f79 splice (2.633). two syllables at Vlad's measured
rates take 0.35-0.46 s after 1.10x (neutral to emphatic; SCRIPT §5), and the casting take stretched sentence-final words to about 0.44 s. Trimming
the rise would flatten the very word that invites the memory.

**Change:**
- If TA's processed V2 measures > 0.43 s, place it at **1.55 s**, between the beeps (beep 1 ends 1.537, beep 2 starts at
  2.000), instead of trimming it.
- The beep then "answers" the question, and the spoken hook completes by **2.0 s** instead of 2.6 s, well inside the 3 s
  skip window and clear of the splice.
- Keep the SLATE placement ("after the second beep") if the take fits.

### Minor (not ranked in the top 5)

6. **(hinglish-scriptwriter)** V8 caption keyword *ungli* → *khud* (already written into fix 1's tokens).
7. **(creative-director)**
   - Hook B: the LED must read at 360 px, with at least 2 visible pulses before 1.5 s and a bloom about 40 px wide at 1080.
     The box silhouette must sit inside the beam on f0.
   - The cover is a dedicated still with H1 at 1.0 opacity, and the indigo window stays low beside the keyword.
8. **(creative-director)** Truth ⚑: confirm with Jawad that his profile under "Bijli ne humein…" is fine. It is the
   collective "we", not a memoir claim.
9. **(creative-director, for the sound team)** Six SFX onsets sit under V1 (0.333-0.667 s): tube_flicker, crt_off,
   relay_click, fan_wind, shimmer and the torch click. The median "speech ≥ 8 LU" check will not catch a masked first word.
   On the A mix, faster-whisper `hi` must return बिजली चली गई in 0-1.3 s at word probability ≥ 0.5. If not, pull crt_off's
   3-9 kHz static and the relay click down 4 dB.

---------------------------------------------------------------------------------------------------------------

## 8. What can proceed now

- **Can be generated now** (their DEV text does not change):
  - **T5** (V10, V11: the pronunciation test for सब्र and एडिटिंग). Fix 4 changes only the ROM tokens.
  - **TB**, **TA**, **T3** and **T6**.
- **Waits for the lead's OK on fix 1:** **T2** (V3-V4) and **T4** (V7-V9, the कंट्रोल-एस test). Generate them with the
  trimmed DEV text, so the trims cost no retake credits.
- **Picture fixes 2-3** go into the brief before the timeline builder's gate stills (the 3D plates are already final and
  need no change).

---------------------------------------------------------------------------------------------------------------

## 9. Claims I could not verify (dated)

| claim | status (checked 2026-10-08) |
|---|---|
| Trial Reels eligibility | Sources conflict: 1,000+ followers for creator/business accounts ([Storrito](https://storrito.com/resources/how-instagram-trial-reels-work-72-hours/), [Social Samosa](https://www.socialsamosa.com/news-2/instagram-introduces-wider-access-trial-reels-9493132)) vs 200 (professional) / 1,000 (personal) ([Sirency](https://www.sirency.com/blog/instagram-trial-reels), [Outfy](https://outfy.com/blog/instagram-trial-reels)), all secondhand. Jawad's account type and follower count are unknown, so hook B posts only if the in-app toggle shows. |
| Sends as the strongest signal for non-follower reach; watch time and likes per reach are the other two | Traced to Mosseri, Jan 2025, only through vendor blogs ([PostEverywhere](https://posteverywhere.ai/blog/how-instagram-algorithm-works), [eClincher](https://www.eclincher.com/articles/how-the-instagram-algorithm-works-in-2026), [ContentGrip](https://www.contentgrip.com/instagram-influencer-marketing/)). No newer primary statement found. The "3-5x likes" weights are vendor estimates. |
| Skip rate = swipes in the first 3 s (Reels Insights since Aug 2025) | Secondhand (research doc, Social Media Today / Metricool). |
| A 31 Dec 2025 Mosseri memo favouring human-made over AI content | Seen in one 2026 guide only and not confirmed. It matters here because the VO is synthetic: AI label on. |
| Reels viewer shows about 55-60 caption characters | Secondhand (research doc). L1 is 49, safe either way. |
| `crowd_cheer_real` is CC0 and wordless | Not checked here; BRIEF §8 QA runs whisper on 8.0-10.0 and 29.5-31.1. |
| Jawad grew up with power cuts | Not claimed (collective "humein"). ⚑ The lead confirms he is comfortable with his profile on that line. |

1M views is a stretch goal, never a forecast. Reach also depends on distribution, timing and luck. This gate only stacks
the odds.
