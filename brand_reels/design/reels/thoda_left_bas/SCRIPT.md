# SCRIPT · Bijli series #2 · Thoda Left... Bas Bas! (`thoda_left_bas`)

r1, 2026-10-11, script writer (hinglish-scriptwriter + script-hook-writer). Machine-readable twin: `script.json`
(captions, UI copy, outro, VO lines + 1:1 token table). **Text-led:** the captions below ARE the story; no VO in the
delivered cut. Grid 100 BPM, 18 f / beat, 72 f / bar, DUR 1008 f (33.6 s). Keyword per line between `*...*` =
glowing Instrument Serif Italic (`jw_key`); the rest is white grotesk (`jw_caps` / `jw_caps_bold` / `jw_body`).
House spelling: hai, nahi, bohat, bari, wahi, theek. Widths measured with `T.measure` (2026-10-11); every line ≤ 940 px
(≤ 780 px where it sits in y 1050-1700).

## 1. Hooks

| rank | id | mechanism | on-screen (f0-f71) | frame 0 | muted? |
|---|---|---|---|---|---|
| 1 | **A** (public) | relatable callout + pattern interrupt | `THODA *left...*` → `*right...*` (f18) → `BAS BAS!` (f36, picture locks) → `AB *theek hai!*` (f54) → slip + client bubble (f63) | snowy CRT macro, ghost picture sliding, lockup mid-rise | yes: snow → lock by 1.2 s |
| 2 | **B** (Trial Reel) | result-first editor pain | `YEH FEEDBACK / *suna suna* / lagta hai?` over the glass viewer: client bubble "thoda left...", title nudges 540 → 538 "-2 px"; f62-f71 snow tear wipes into the roof | viewer + bubble mid-pop | yes |
| reserve | | POV callout | `POV: aap neeche TV ke saamne ho` | | |
| reserve | | curiosity cold open | `*kiska* left?!` (R4 as f0) | | |

Both versions are identical from the splice f72. Banned openers avoided (no greeting, no logo, no "is video mein").

## 2. Story (one row per beat group)

| part | f | what the viewer reads | job |
|---|---|---|---|
| Hook | 0-71 | the shout, the lock, the slip, a chat bubble that should not exist in 1998 | stop + open loop |
| Turn | 72-197 | roof vs downstairs: "Aaya?" / "NAHI! THODA LEFT..." / "ULTA! DOOSRA LEFT!" / "*kiska* left?!" | the two voices, the gag |
| Escalation | 198-431 | "thoda *aur*..." / "NAHI NAHI, *wapas*!" / ticks "HAAN... HAAN..." / "BAS! BAS!" / lock "AB *theek hai!*" / wind "ARRE, *phir se?!*" / "YEH SCENE *khatam* nahi hua..." | build, release, break |
| Re-hook (46 %) | 432-503 | "20 SAAL BAAD" → the client sends "thoda left..." | the twist |
| Escalation 2 | 504-719 | "nahi, pehle wala" / revision avalanche / "DIALOGUE *wahi* hai." / TAB-AB split in sync / client "BAS BAS!" / "27 *revision* baad..." | proof by rhyme |
| Payoff (75 %) | 756-863 | **HUM AAJ BHI / *antenna* / ghuma rahe hain.** | the line people send |
| CTA + loop | 882-1007 | outro: "Aap ke ghar antenna kaun ghumata tha?" / *Papa, bhai ya aap?* → bubble "thoda left..." → f0 "THODA *left...*" | comment + seamless loop |

## 3. On-screen captions (house type; frame timings)

Voice key: **near** = big house lockup, top band; **far** = small `jw_caps` 64 px ASH with two echoes, rising from
y 1480 (downstairs voice heard on the roof); **narrator** = house lockup, no ghost. Positions = text-box centre (x, y).

| id | f in-out | shot | voice | roman (keyword `*...*`) | lockup (style px @ x,y · measured w×h) |
|---|---|---|---|---|---|
| H1 | 0-17 | S1 | near | `THODA *left...*` | caps 96 @540,360 · 360×67 / key 240 @540,535 · 417×173 (mid-rise on f0, t0 -0.1) |
| H1b | 18-35 | S1 | near | `THODA *right...*` | keyword swap only · 579×173 (slides in from the left with the picture) |
| H2 | 36-53 | S1 | near | `BAS BAS!` | caps_bold 170 @540,470 · 846×120 · SLAM; picture locks f36 |
| H3 | 54-71 | S1 | near | `AB *theek hai!*` | caps 96 @540,330 / key 220 @540,500 · 779×158; tears out f63-f71 |
| HB1 | 0-71 | S1B | narrator | `YEH FEEDBACK / *suna suna* / lagta hai?` | caps 96 @540,330 · 757×67 / key 200 @540,495 · 751×144 / body 72 @540,650 · 367×50 (hook B only) |
| R1 | 72-98 | S2 | near (roof) | `*Aaya?*` | key 230 @540,470 · 510×166 |
| R2 | 99-134 | S2 | far | `NAHI! THODA LEFT...` | caps 64 @540,1420 · 704×45 |
| R3 | 135-161 | S2 | far | `ULTA! DOOSRA LEFT!` | caps 64 @540,1420 · 704×45 |
| R4 | 162-197 | S2 | near (roof) | `*kiska* left?!` | key 230 @450,480 · 446×166 + body 72 @790,520 · 181×50; SLAM |
| C5 | 198-224 | S3 | near | `thoda *aur...*` | caps `THODA` 96 @540,330 / key 230 @540,500 · 445×166 |
| C6 | 225-251 | S3 | near | `NAHI NAHI, *wapas!*` | caps 96 @540,330 · 569×67 / key 240 @540,505 · 617×173 |
| C7 | 252-287 | S4 | far | `HAAN... HAAN...` | caps 64 @540,1420 · 538×45 (second word on f270) |
| C8 | 288-305 | S4 | far, loud | `BAS! BAS!` | caps_bold 110 @540,1390 · 596×78, IVORY |
| C9 | 306-341 | S5 | near | `AB *theek hai!*` | as H3, crisp (locked) |
| C10 | 351-377 | S5 | near | `ARRE, *phir se?!*` | caps 96 @540,330 · 260×67 / key 230 @540,500 · 712×166 |
| C11 | 378-431 | S6 | narrator | `YEH SCENE / *khatam* / nahi hua...` | caps 96 @540,380 · 555×67 / key 240 @540,550 · 684×173 / body 72 @540,705 · 381×50; exits on the M3 track |
| C12 | 432-467 | S7 | narrator | `20 SAAL BAAD` | caps 96 @540,300 · 734×67 |
| C13 | 540-575 | S9 | narrator | `DIALOGUE / *wahi* hai.` | caps 96 @540,300 · 516×67 / key 250 @480,470 · 458×180 + body 72 @790,505 |
| C14 | 648-683 | S11 | near (client: the one house-type exception, the rhyme with H2) | `BAS BAS!` | as H2 |
| C15 | 684-719 | S11 | narrator | `27 / *revision* / baad...` | caps 96 @540,300 / key 220 @540,460 · 635×158 / body 72 @540,600 · 251×50 |
| **P1** | **756-863** | S12 | narrator, PAYOFF | `HUM AAJ BHI / *antenna* / ghuma rahe hain.` | caps 96 @540,380 · 675×67 / key 250 @540,560 · 774×180 / body 72 @540,770 · 655×50; underline ON; out_t0 846 |

Reading check: every lockup ≤ 6 words; settled holds ≥ words / 3 s except the hook chant H1-H3 and R4 (familiar
shouts at slam pacing, 0.6 s per state, allowed by the single-word-slam rule). ≤ 2 text blocks at once (far voice +
near lockup never overlap in time). Keywords per scene ≤ 2.

### UI copy (glass UI and phone screen, not house type; details in SHOTS §c)

| id | f | where | text |
|---|---|---|---|
| B0 | 63-71 | S1 anachronism bubble @790,300 | `Client` / `thoda left...` |
| T1 | 468-485 | S7 toast | `Client` / `thoda left...` |
| X1 | 477-485 | S7 viewer readout | `X 540` → `X 538`, flash `-2 px`, chip `v2` |
| P1b / P1c | 490 / 504-521 | S8 phone bubbles | `thoda right...` / `nahi, pehle wala` |
| L1 | 522-575 | S9 revision list | `trailer_v3.mp4` … `trailer_v26_final_final.mp4` |
| S1-S4 | 576 / 594 / 612 / 630 | S10 split, both halves at once | `thoda left...` / `thoda right...` / `nahi, pehle wala!` / `thoda sa...` |
| T2 | 648-683 | S11 bubble | `BAS BAS! ab theek hai!` |
| E1 | 684-719 | S11 export | `Exporting v27_final_FINAL.mp4` 0 → 100 % |
| B1 | 990-1007 | S13 = B0, exits with the outro | `Client` / `thoda left...` |

### Outro (profile_outro, f882-1007)

Question **`Aap ke ghar antenna kaun ghumata tha?`** · key line **`*Papa, bhai ya aap?*`** (draft was "Ghar mein antenna
kaun ghumata tha?": "aap ke ghar" makes it personal, the key turns it into a three-way choice = the easiest comment).

## 4. Optional VO layer (not generated; Roman for captions, Devanagari for TTS)

One voice reads both sides (shouts at caption frames). Rate ≤ 3.0 w/s for speech lines; shout lines (V1, V2, V12)
are monosyllabic and checked in syllables (≤ 6 syl/s). Lines may slip ±0.25 s to land the stressed syllable on the beat.

| id | f in-out | roman | devanagari | captions | emotion |
|---|---|---|---|---|---|
| V1 | 3-34 | Thoda *left...* thoda right... | थोड़ा लेफ़्ट... थोड़ा राइट... | H1/H1b | shout, playful |
| V2 | 38-62 | Bas bas! Ab *theek* hai! | बस बस! अब ठीक है! | H2/H3 | relief, loud |
| V3 | 74-132 | *Aaya?* Nahi! Thoda left... | आया? नहीं! थोड़ा लेफ़्ट... | R1/R2 | roof call, far answer |
| V4 | 163-190 | *Kiska* left?! | किसका लेफ़्ट?! | R4 | indignant |
| V5 | 200-248 | Thoda *aur...* nahi nahi, wapas! | थोड़ा और... नहीं नहीं, वापस! | C5/C6 | urgent |
| V6 | 254-300 | Haan... haan... *bas!* | हाँ... हाँ... बस! | C7/C8 | building |
| V7 | 308-374 | Ab *theek* hai!... Arre, phir se?! | अब ठीक है!... अरे, फिर से?! | C9/C10 | joy, then despair |
| V8 | 380-440 | Yeh scene kabhi *khatam* nahi hua. | ये सीन कभी ख़त्म नहीं हुआ। | C11 | warm, knowing |
| V9 | 438-464 | Bees saal *baad...* | बीस साल बाद... | C12 | calm |
| V10 | 470-535 | Thoda left... thoda right... *nahi,* pehle wala. | थोड़ा लेफ़्ट... थोड़ा राइट... नहीं, पहले वाला। | T1/P1b/P1c | reading the client, dry |
| V11 | 542-572 | Dialogue *wahi* hai. | डायलॉग वही है। | C13 | deadpan |
| V12 | 650-680 | Bas bas! Ab *theek* hai! | बस बस! अब ठीक है! | C14/T2 | same melody as V2 |
| V13 | 686-716 | Sattaees *revision* baad... | सत्ताईस रिविज़न बाद... | C15 | tired smile |
| V14 | 758-835 | Hum aaj bhi *antenna* ghuma rahe hain. | हम आज भी एंटीना घुमा रहे हैं। | P1 | payoff, slow |
| V15 | 905-975 | Aap ke ghar *antenna* kaun ghumata tha? | आप के घर एंटीना कौन घुमाता था? | outro | question, rising |

70 words. Tight: V10 (3.2 w/s): fallback "Thoda left... *nahi,* pehle wala." (5 words). TTS spellings: लेफ़्ट / राइट
(phonetic English), ख़त्म (nukta), सत्ताईस for "27", एंटीना. Token table (70 tokens, 1:1 Roman ↔ Devanagari) in
`script.json → vo.tokens`. If VO is added, the lockups already show the words: no extra snake captions.

## 5. Post caption

First line (92 chars): `Thoda left... thoda right... BAS BAS! Bachpan mein antenna, ab client. Video editing life.` ·
context: `Har editor ka client wahi neeche wala hai jo TV ke saamne khara hota tha.` · pinned comment:
`Usse tag karo jo chhat pe jaata tha.` · `#videoediting #editorlife #90skids #desinostalgia #motiongraphics`.

## 6. Self-check

- Muted hook lands by 1.2 s (H2 + picture lock); every line is a shout, a story time jump or UI; no fact about Jawad,
  no years, no brands, no channel names, no cricket teams; narrator never says "main".
- Read as a Pakistani and as an Indian viewer: aaya, ulta, kiska, wapas, phir se, khatam, wahi, Papa: shared words.
- One keyword per line; payoff keyword *antenna* lands on a downbeat (f756, beat 42).
- Loop: B1 "thoda left..." + ping at f990 → f0 `THODA *left...*`.
- Open: lead OK on the "nahi, pehle wala" bubble (overlap with the earlier `pehle_wala` reel, BRIEF §7).
