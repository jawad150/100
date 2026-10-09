# SCRIPT: Reel 5 · C15 · Log Kya Kahenge (VO, Vlad · elevenlabs_v4)

Date 2026-10-08 · Author: hinglish-scriptwriter · Status: **script v3 (measured, see the v3 section and VO_TIMING.md)**; v2 = v1 + the viral gate r1 fixes owned by the scriptwriter (`GATE.md`
§7 fixes 3, 4, 5; verdict FIX) and the gate's sign-offs (V3 cut, V6 fallback, all of V1B hidden). Windows match BRIEF r2 §5/§9. Timings are
ESTIMATES (no take exists yet), calibrated on Vlad's casting take (§4). Machine-readable twin: `script.json` (same folder).

Sources (binding): `BRIEF.md` r2 §2, §5, §6, §8, §9, §15 (this folder); `GATE.md` §4 and §7; SLATE §3.5 + §4 + §5.1; the `jawad-brand-reels`
skill; house spelling `workspace/brand_reels/prior/captions_roman_urdu.srt`; voice recipe `pipeline/jawad_reels/vo_config.json`; token rules
of `vo_chain.py` (DEV and ROM tokens 1:1 by whitespace, `*word` = caption keyword) and `snake_captions.py` (chunking, hide).

Narrator: **hum** (we) plus friendly **tum** imperatives (*bhejo*), the register of the end card and the pinned comment. No "main /
mera / meri", nothing about Jawad's life, no counts, "JD" not spoken. Every line is SLATE/BRIEF copy, a cut of it, or gate-r1 copy.

---------------------------------------------------------------------------------------------------------------

## v3 · MEASURED (2026-10-09, Vlad takes; the full table is `VO_TIMING.md`, this folder)

The final VO exists: `workspace/jawad_reels/log_kya_kahenge/vo/vo_stem.wav` (= hook A, also `lkk_vo_A.wav`), `lkk_vo_B.wav`
(hook B), 35.200 s, 48 kHz 24-bit mono, -16.0 LUFS, TP -2.14 dBTP; word timings `words.json` (= A) / `lkk_vo_B.words.json`.
What changed against v2 (each a binding rule outcome, or flagged for the lead):

| line | v2 plan | measured v3 | why |
|---|---|---|---|
| V2 | 15 words, ends 14.441 (est) | **14-word BRIEF fallback** "Hum zindagi unke hisaab se edit karte hain... jo poori video dekhte bhi nahi.", 8.800 -> 14.010 at 1.10x | overrun rule: the 15-word take ran 6.51 s at 1.10x (~6.34 s with the 0.30 s pause; window 6.03 s). Token table: V2 has 14 tokens (`apni` removed, indices shifted), 67 tokens in all; 61 words (A) / 60 (B) |
| V7 | 31.600 at 1.00x | **31.433 (f943) -> 35.073 at 1.10x** | the six V7 recordings are 3.95-4.30 s raw; the fastest is still 3.64 s at 1.10x: from f948 the last word would end 35.24 s. The onset moved to the latest frame that ends by 35.100: **lead decision** (VO_TIMING "For the lead") |
| V5 | parts at 1.08x | part 1 22.400 -> 23.510 (+0.043 s over 23.467), part 2 23.667 -> 25.327, both 1.10x | "hain..." trails; part 1 from the fastest recording (two-sentence take G2 t2), part 2 from V5 t1 |
| V4 | 1.06x, ends 22.127 (est) | 19.333 -> 22.213 at 1.10x | rule: 1.06x ended 22.333 |
| V6 | 1.05x, ends 28.769 (est) | 26.000 -> 28.950 at 1.05x | as planned |
| V1 / V1B / V3 | 1.10x | V1 0.100 -> 2.520 (comma cut to 0.10 s by its rule), V1B 0.100 -> 2.540, V3 16.367 -> 17.707 + *Cardboard* 18.200 -> 18.940 | as planned |

Calibration lesson: Vlad reads a short line on its own at 3.1-3.5 syllables/s (the casting paragraph: 4.35), so the v2 estimates
were 10-25 % short. Lines read inside a two- or three-sentence take (vo_config allows 1-3 sentences per take) run faster when they
come first; V1, V1B, V4, V5 part 1 and V6 are cut from such takes (`vo/raw/cuts/cuts.json`). Pronunciation test (batch 1): every
§6 primary spelling kept, no fallback needed (details in VO_TIMING "Pronunciation test"). CER per line (whisper small, best of small /
medium): V1 0.000, V1B 0.100, V2 0.065, V3 0.000, V4 0.125, V5 0.000, V6 0.000, V7 0.053. Credits: 11.50 (34 jobs).

---------------------------------------------------------------------------------------------------------------

## 0. Decisions on one screen (v2; each measured in §4)

| # | line | before (v1 / BRIEF r1) | v2 | source and why |
|---|---|---|---|---|
| 1 | V7 + end-card sub | "Us dost ko bhejo jo 'log' ki wajah se ruka hai." (11 words); sub `jo 'log' ki wajah se ruka hai` | **"Us dost ko bhejo jise 'log' ka darr rokta hai."** (10 words, 13 syllables); sub **`jise 'log' ka darr rokta hai`** | gate fix 4: gender-neutral ("ruka" was masculine; the friend is as often a sister), drops वजह, and *darr* echoes V1's *darr* across the seam (verbal loop). Sub re-measured here with `T.measure(..., 'jw_body')`: **632.8 px at 50 px (x 223.6-856.4, 73.6 px clear of x 930)**, 708.7 px at 56 px (35.6 px clear): keep the 50 px override |
| 2 | V7 | onset 32.000 (f960), 1.10x | onset **31.600 (f948)**, **1.00x**, last word <= 35.100 | gate fix 3: "Us dost ko *bhejo*" is heard while the CTA caps and keyword rise; est end 34.926 s (+0.17); the VO gap after the payoff drops from 3.36 s to 2.83 s |
| 3 | V6 | window to 28.667, 1.10x (+0.02 s) | window to **29.100** (may cross the f864 cut), **1.05x** | gate fix 3 (band 1.04-1.06x): est end 28.769 s (+0.33); stays >= 0.1 s clear of the 29.2 swish. Words unchanged: the BRIEF fallback "Kisi aur ki nazar mein, hum bhi 'log' hain." (gate-approved) |
| 4 | V4 | "Asli log toh peeche baithe hain, apne phone mein." (9), 1.10x (+0.08 s) | **"Asli log peeche baithe hain, apne phone mein."** (8), **1.06x** | gate fix 5a: the BRIEF fallback by default; est end 22.127 s, +0.11 s to 22.233 (f667: my gap rule, >= 0.15 s before V5 at 22.400) and +0.17 s to the BRIEF window f669 |
| 5 | V5 | parts at 22.500 / 23.700, 1.10x (+0.01 s) | parts at **22.400 (f672) / 23.667 (f710)**, **1.08x** (1.10x pass as the free fallback) | gate fix 5b: part 1 starts on the bar-7 downbeat with the O6 start and the kick, so *busy* lands at ~22.61 s; part 2 est end 25.393 s at 1.08x, 25.361 s at 1.10x; overrun rule in §2 (fix 5c) |
| 6 | V1, V5 | no overrun rule | explicit rules (§2) | gate fix 5c: V1 > 2.60 s -> comma pause 0.10 s, hard ceiling 2.850 s; V5 part 2 > 1.78 s -> one retake with "," and part 2 at 23.650, never past 25.48 |
| 7 | speeds | every take at 1.10x | **per line**: V1, V1B, V2, V3 1.10x · V4 1.06x · V5 1.08x · V6 1.05x · V7 1.00x | the payoff lines leave the 1.10x ceiling (gate fixes 3, 5). `vo_chain` takes one speed per run, so each take is processed once per speed (local, no credits) and each line is cut from the pass at its speed (§5) |
| 8 | V3 | "Gaur se dekho." cut (needed sign-off) | **approved** (gate r1; BRIEF r2 change 8) | "Gaur se dekho:" stays in IG caption line 3 |
| 9 | V1B captions | hide "Yeh 'log'" (BRIEF r1); rest suggested | **all six V1B tokens hidden** | gate sign-off; BRIEF r2 §6.2 |
| 10 | V5 count | BRIEF §9 says 7 words | 8 words (same text) | counting error in BRIEF §9 ("Log busy hain apne log kya kahenge mein" = 8) |

Totals (hook A): **62 words**, 91 syllables, 1.76 words/s over 35.2 s (hook B: 61 words, 88 syllables). Calibrated speech 20.45 s, line
spans 22.54 s (pauses and placed beats included) inside 23.90 s of windows; the lead's 2.7 w/s model gives 23.0 s raw, 20.9-21.7 s after
1.10-1.06x. Low on purpose (GATE §4 accepts it): 3.2-8.8 s is read, not spoken (the judgement lines), and 29.1-31.6 s is the silent gag.

---------------------------------------------------------------------------------------------------------------

## 1. Hooks (A public, B Trial Reel; only frames 0-89 differ, splice f90)

| rank | id | mechanism | VO (Roman) | DEV (TTS) | words | first word | est end (target 2.70, ceiling) | on screen (muted read) |
|---|---|---|---|---|---|---|---|---|
| 1 | **A** · public | identity question + the search phrase | Sab se bara darr, log kya kahenge. | सब से बड़ा डर, लोग क्या कहेंगे। | 7 | 0.1 s (f3) | 2.485 s (2.700, 2.850) | `LOG KYA / kahenge?` |
| 2 | **B** · Trial Reel (frames 0-89, splice f90) | curiosity gap | Yeh 'log'... asal mein hain kaun? | ये 'लोग'... असल में हैं कौन? | 6 | 0.1 s (f3) | 2.094 s (2.700, 2.700) | `YEH / log / HAIN KAUN?` |

Recommended: **A** (the phrase is the share hook and the search term; the head-snap answers "log" visually by 0.6 s; gate score 7/8).
A/B alternate: **B** (curiosity gap; BRIEF r2 gives it its own head-snap at 135 mm; same picture from 3.0 s). Both: first syllable at
0.10 s, <= 7 spoken words (SLATE), <= 4 on-screen words, readable muted through the lockup. Considered, not used:

| mechanism | line | why not |
|---|---|---|
| result-first | "Yeh crowd asli nahi hai." | spends the 16 s reveal in the first second; no lockup designed; reserve only |
| contrarian | "Log kuch nahi kehte." | spoils the payoff (viral panel: Pull F) |
| number | "Paanch hazaar log. Ek hi sawaal." | banned: no crowd counts (BRIEF §2) |
| POV callout | "POV: tum ruke ho... 'log' ki wajah se." | repeats the CTA phrase; weaker gap |

**Loop (now verbal):** V7 "...jise 'log' ka **darr** rokta hai." -> frame 0 V1 "Sab se bara **darr**, log kya kahenge." The same word on
both sides of the seam; est gap 0.37 s across it (V7 ends ~34.93 s, V1 starts 0.10 s), filled by the whisper-wall swell and the
card's reverse swell into the f0 hit.

---------------------------------------------------------------------------------------------------------------

## 2. Beat table (75 BPM, 24 f/beat, bar = 3.2 s; `*word` = caption keyword; the **keyword** column = the line's serif-italic word)

| id | beat / shot | grid onset | target start -> end (hard) | Roman (house spelling) | DEV (Vlad, elevenlabs_v4) | words | keyword | speed | delivery | est end (slack) |
|---|---|---|---|---|---|---|---|---|---|---|
| V1 | HOOK A · S1-01 | bar 0 beat 1 +3 f (f3) | 0.100 -> 2.700 (2.850) | Sab se bara *darr, log kya kahenge. | सब से बड़ा डर, लोग क्या कहेंगे। | 7 | *darr* | 1.10x | low, close, almost confiding; no rise at the end | 2.485 (+0.22) |
| V1B | HOOK B (Trial Reel) · S1-01B | bar 0 beat 1 +3 f (f3) | 0.100 -> 2.700 | Yeh 'log'... asal mein hain *kaun? | ये 'लोग'... असल में हैं कौन? | 6 | *kaun* | 1.10x | curious, slightly amused on 'kaun' | 2.094 (+0.61) |
| V2 | RE-HOOK 1: JD alone -> heads tilt · S3-01/S3-02 | bar 2 beat 4 (f264) | 8.800 -> 14.833 | Hum apni *zindagi unke hisaab se *edit karte hain... jo poori *video dekhte bhi *nahi. | हम अपनी ज़िंदगी उनके हिसाब से एडिट करते हैं... जो पूरी वीडियो देखते भी नहीं। | 15 | *edit* | 1.10x | wry on 'edit', a small smile on 'dekhte bhi nahi' | 14.441 (+0.39) |
| V3 | REVEAL (orbit) · S4-01 | bar 5 beat 1 +11 f (f491) | 16.367 -> 19.133 | Yeh crowd *flat hai. *Cardboard. | ये क्राउड फ़्लैट है। कार्डबोर्ड। | 5 | *Cardboard* | 1.10x | quiet discovery; 'Cardboard.' dry, flat, a beat on its own | 19.003 (+0.13) |
| V4 | THE SINGLE IMAGE (focus pull) · S4-02 | bar 6 beat 1 +4 f (f580) | 19.333 -> 22.233 | Asli log peeche baithe hain, apne *phone mein. | असली लोग पीछे बैठे हैं, अपने फ़ोन में। | 8 | *phone* | 1.06x | matter-of-fact, gentle | 22.127 (+0.11) |
| V5 | O6 BURN · S4-03/S4-04 | bar 7 beat 1 (f672) | 22.400 -> 25.400 (25.480) | Log *busy hain... apne log kya *kahenge mein. | लोग बिज़ी हैं... अपने 'लोग क्या कहेंगे' में। | 8 | *busy* | 1.08x | the quotable line: slow, warm, a smile in the voice; the pause holds 23.6 s (O6 complete) | 25.393 (+0.01) |
| V6 | PAYOFF · S5-01 (may cross the f864 cut into S6-01) | bar 8 beat 1 +12 f (f780) | 26.000 -> 29.100 | Kisi aur ki *nazar mein, hum bhi *'log' hain. | किसी और की नज़र में, हम भी 'लोग' हैं। | 9 | *'log'* | 1.05x | soft realisation, falling cadence | 28.769 (+0.33) |
| V7 | END CARD + LOOP · S6-02 (end card from f936) | bar 9 beat 4 +12 f (f948) | 31.600 -> 35.100 | Us dost ko *bhejo jise 'log' ka darr rokta hai. | उस दोस्त को भेजो जिसे 'लोग' का डर रोकता है। | 10 | *bhejo* | 1.00x | warm, direct; no final fall if the take allows; "darr" hands over to V1's "darr" at frame 0 (the loop line) | 34.926 (+0.17) |

Placement inside a line (the assembler splits the take at these sentence ends; everything else is one segment):
- **V3**: "Yeh crowd flat hai." at 16.367 (est to 17.55; the board creak at 17.6 sits in the gap) · "Cardboard." at **18.200** (f546;
  allowed 18.0-18.3 so it ends <= 19.133; the orbit is at 68 of 70 degrees: backs, tape and struts on screen).
- **V5**: "Log busy hain..." at **22.400** (f672, bar 7 beat 1: O6 start, crackle and kick; est to 23.232, must end <= 23.467) · the pause
  holds the O6-complete hit at 23.600 (f708) · "apne 'log kya kahenge' mein." at **23.667** (f710; est 1.726 s long -> 25.393).
- **V6**: onset 26.000 (f780, the 8th after the clunk); ends <= 29.100 (f873); "hum bhi 'log' hain" may run over the f864 cut into the warm
  wide (the stands full of phone-lit people: a picture match for "we are 'log' too").
- **V7**: onset **31.600** (f948, bar 9 beat 4 +12 f, the 8th grid), under the end card (from f936); last word <= 35.100 (f1053).

**Overrun rules** (decided on the measured, processed take; the only allowed moves; never above 1.10x, never pitch-shift):
- **V1**: processed > 2.60 s (ends > 2.700): cut the comma pause to 0.10 s; hard ceiling: ends <= 2.850 s (<= 2.75 s long; the lockup is gone by 2.9 s); still over -> one T1 retake (reserve); never above 1.10x.
- **V1B**: processed > 2.60 s: cut the "..." pause to 0.30 s; still over -> one T1 retake.
- **V2**: processed > 6.03 s with the "..." pause cut to 0.30 s: one T2 retake with the 14-word BRIEF fallback.
- **V3**: part 1 > 1.45 s or "Cardboard" > 1.10 s (onset 18.0-18.3, ends <= 19.133): retake only that word with its §6 fallback spelling.
- **V4**: processed > 2.900 s at 1.06x (ends after f667 = 22.233, i.e. < 0.15 s before V5 at 22.400): the 1.10x pass of the same take; still over -> one T2 retake of V4.
- **V5**: part 1 > 1.067 s (ends > 23.467) or part 2 > 1.733 s at 1.08x (ends > 25.400): the 1.10x pass; at 1.10x part 2 up to 1.78 s is accepted (ends <= 25.447, inside the 25.48 clunk guard); part 2 > 1.78 s at 1.10x: one retake with "हैं..." written "हैं," (ROM "hain..." -> "hain,") and part 2 placed at 23.650; never past 25.480, never move the clunk.
- **V6**: processed > 3.10 s at 1.05x (ends > 29.100, < 0.1 s before the 29.2 swish): the 1.10x pass; still over -> onset 25.933 (f778, <= 3.167 s); never earlier (the clunk guard ends 25.90); the comma is always cut to 0.20 s.
- **V7**: processed > 3.50 s at 1.00x (last word after 35.100): the slowest of the 1.03x / 1.06x passes that ends by 35.100; over at 1.06x -> the 1.10x pass (outside the gate band: tell the lead); over at 1.10x -> one retake of V7.
- Approved originals kept on record (not recorded): V3 "Gaur se dekho. Yeh crowd flat hai. Cardboard. (SLATE / BRIEF r1, 8 words; not recorded)"; V4 "Asli log toh peeche baithe hain. Apne phone mein. (SLATE / BRIEF r1, 9 words; not recorded)"; V6 "Aur kisi aur ki nazar mein, hum bhi 'log' hain. (SLATE / BRIEF r1, 10 words; not recorded)"; V7 "Us dost ko bhejo jo 'log' ki wajah se ruka hai. (SLATE §3.5 / BRIEF r1, 11 words; replaced)".

---------------------------------------------------------------------------------------------------------------

## 3. Token table (Roman caption token <-> Devanagari TTS token, 1:1 in order; `vo_chain.tokens()` checked: counts equal)

Quotes: kept on single words (`'log'`), dropped from the quoted phrase in V5 (BRIEF §15). DEV keeps the quote marks (they mark the
quoted *log* for the TTS; risk 6 in §6). 1:n merges expected from faster-whisper (handled by vo_chain's DP alignment): सब से -> "सबसे",
कार्डबोर्ड -> "कार्ड बोर्ड". No 1:n split is needed in the script itself (every caption token is one TTS token). hide = BRIEF §15 HIDE
window (V1 "log kya kahenge" under the hook-A lockup; all of V1B under the hook-B lockup; V7 under the end card, 31.2-35.2).
est = estimated reel time of the word onset at the line's planned speed.

**Dry run (v2).** The three take texts were synthesised with the local Kokoro hm_psi voice (scratch, never a take) and run through
`vo_chain.py process --speed 1.00` (faster-whisper alignment to these DEV/ROM tokens): T0 32/32, T1 13/13, T2 23/23; all `ok` = true, so the new V4 and V7 tokens
align. Whisper wrote बिजी / नजर without the nukta (expected normalisation) and heard कार्डबोर्ड as "कार्बोर्ड" on the Kokoro read (risk 1).

| line | i | roman | dev | key | hide | est |
|---|---|---|---|---|---|---|
| V1 | 0 | Sab | सब |  |  | 0.10 |
| V1 | 1 | se | से |  |  | 0.31 |
| V1 | 2 | bara | बड़ा |  |  | 0.52 |
| V1 | 3 | darr, | डर, | key |  | 0.94 |
| V1 | 4 | log | लोग |  | hide | 1.33 |
| V1 | 5 | kya | क्या |  | hide | 1.56 |
| V1 | 6 | kahenge. | कहेंगे। |  | hide | 1.79 |
| V1B | 0 | Yeh | ये |  | hide | 0.10 |
| V1B | 1 | 'log'... | 'लोग'... |  | hide | 0.39 |
| V1B | 2 | asal | असल |  | hide | 1.14 |
| V1B | 3 | mein | में |  | hide | 1.52 |
| V1B | 4 | hain | हैं |  | hide | 1.71 |
| V1B | 5 | kaun? | कौन? | key | hide | 1.90 |
| V2 | 0 | Hum | हम |  |  | 8.80 |
| V2 | 1 | apni | अपनी |  |  | 8.98 |
| V2 | 2 | zindagi | ज़िंदगी | key |  | 9.33 |
| V2 | 3 | unke | उनके |  |  | 9.87 |
| V2 | 4 | hisaab | हिसाब |  |  | 10.22 |
| V2 | 5 | se | से |  |  | 10.58 |
| V2 | 6 | edit | एडिट | key |  | 10.76 |
| V2 | 7 | karte | करते |  |  | 11.11 |
| V2 | 8 | hain... | हैं... |  |  | 11.47 |
| V2 | 9 | jo | जो |  |  | 12.10 |
| V2 | 10 | poori | पूरी |  |  | 12.31 |
| V2 | 11 | video | वीडियो | key |  | 12.74 |
| V2 | 12 | dekhte | देखते |  |  | 13.38 |
| V2 | 13 | bhi | भी |  |  | 13.80 |
| V2 | 14 | nahi. | नहीं। | key |  | 14.02 |
| V3 | 0 | Yeh | ये |  |  | 16.37 |
| V3 | 1 | crowd | क्राउड |  |  | 16.66 |
| V3 | 2 | flat | फ़्लैट | key |  | 16.96 |
| V3 | 3 | hai. | है। |  |  | 17.25 |
| V3 | 4 | Cardboard. | कार्डबोर्ड। | key |  | 18.20 |
| V4 | 0 | Asli | असली |  |  | 19.33 |
| V4 | 1 | log | लोग |  |  | 19.71 |
| V4 | 2 | peeche | पीछे |  |  | 19.89 |
| V4 | 3 | baithe | बैठे |  |  | 20.27 |
| V4 | 4 | hain, | हैं, |  |  | 20.64 |
| V4 | 5 | apne | अपने |  |  | 21.02 |
| V4 | 6 | phone | फ़ोन | key |  | 21.57 |
| V4 | 7 | mein. | में। |  |  | 21.85 |
| V5 | 0 | Log | लोग |  |  | 22.40 |
| V5 | 1 | busy | बिज़ी | key |  | 22.61 |
| V5 | 2 | hain... | हैं... |  |  | 23.02 |
| V5 | 3 | apne | अपने |  |  | 23.67 |
| V5 | 4 | log | 'लोग |  |  | 24.10 |
| V5 | 5 | kya | क्या |  |  | 24.31 |
| V5 | 6 | kahenge | कहेंगे' | key |  | 24.53 |
| V5 | 7 | mein. | में। |  |  | 25.18 |
| V6 | 0 | Kisi | किसी |  |  | 26.00 |
| V6 | 1 | aur | और |  |  | 26.38 |
| V6 | 2 | ki | की |  |  | 26.57 |
| V6 | 3 | nazar | नज़र | key |  | 26.76 |
| V6 | 4 | mein, | में, |  |  | 27.13 |
| V6 | 5 | hum | हम |  |  | 27.51 |
| V6 | 6 | bhi | भी |  |  | 27.83 |
| V6 | 7 | 'log' | 'लोग' | key |  | 28.14 |
| V6 | 8 | hain. | हैं। |  |  | 28.45 |
| V7 | 0 | Us | उस |  | hide | 31.60 |
| V7 | 1 | dost | दोस्त |  | hide | 31.86 |
| V7 | 2 | ko | को |  | hide | 32.11 |
| V7 | 3 | bhejo | भेजो | key | hide | 32.37 |
| V7 | 4 | jise | जिसे |  | hide | 32.88 |
| V7 | 5 | 'log' | 'लोग' |  | hide | 33.39 |
| V7 | 6 | ka | का |  | hide | 33.65 |
| V7 | 7 | darr | डर |  | hide | 33.90 |
| V7 | 8 | rokta | रोकता |  | hide | 34.16 |
| V7 | 9 | hai. | है। |  | hide | 34.67 |

Caption chunk targets for the caption-designer (the chunker decides; one keyword per chunk at most; BRIEF §15 rows to update are marked r2):
V1 `Sab se` · `bara *darr*` (then hidden: `log kya kahenge`) · V1B all hidden · V2 `Hum apni` · `*zindagi*` · `unke hisaab se` ·
`*edit* karte hain...` · `jo poori *video*` · `dekhte bhi *nahi*` · V3 (r2) `Yeh crowd` · `*flat* hai` · `*Cardboard*` · V4 (r2) `Asli log` ·
`peeche baithe hain` · `apne *phone* mein` · V5 `Log *busy* hain...` · `apne log kya` · `*kahenge* mein` · V6 (r2) `Kisi aur ki` · `*nazar* mein` ·
`hum bhi *'log'* hain` (*ki* may not open a chunk) · V7 hidden (end card; the caption keyword stays *bhejo* in the ROM track).

---------------------------------------------------------------------------------------------------------------

## 4. Timing (estimated; replace with measured values after the takes)

**Measured rate of the voice.** `workspace/brand_reels/tts/hf_dl/vlad/vlad_v4_r1_DEV.mp3` (the casting take, 22.60 s, 52 words) through
faster-whisper small int8 (word stamps) and `vo_chain.voiced_runs`: **2.30 words/s raw including pauses (vo_config 142.8 wpm), 4.35
syllables/s voiced**, phrases 3.17-5.58 syll/s; sentence-final phrases run slowest. Pauses: comma 0.20 / 0.32 / 0.40 s, "..." 0.50 s,
full stop / ? / ! 0.54-0.71 s (vo_chain caps them at 0.45 s; after "..." up to 0.9 s). Words/s misjudges this script, whose words are
mostly one syllable, so the table also gives syllables/s.

**Calibrated model.** Every phrase was synthesised with the local Kokoro hm_psi voice (scratch timing only, never a take) and measured
with the same voiced-run detector; v2 re-ran the new V7 and three unchanged phrases (identical durations: the model is deterministic).
Vlad/Kokoro duration ratio on the 9 casting phrases: 0.84-0.94 mid-sentence (central 0.89), 1.09-1.36 before a full stop (central 1.09),
0.84 before ? or !. Estimate = Kokoro phrase x ratio + measured pause, divided by the line's speed. "worst" = the largest measured
ratios and pauses (a pessimistic bound, not a forecast), at the planned speed and at 1.10x. New V7 in Kokoro: 3.36 s against 3.29 s for
the old line: one syllable fewer but +0.07 s (डर and रोकता carry long stops), so the new copy does not save time; the earlier onset does.

| line | target start -> end | window | words | syll | 2.7 w/s raw -> after 1.10-1.06x | calibrated speech | speed | est end | slack | worst end @speed / @1.10 | w/s | syll/s | keyword @ t |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| V1 | 0.100 -> 2.700 | 2.60 | 7 | 10 | 2.59 -> 2.36-2.45 | 2.20 s | 1.10x | 2.485 | +0.22 | 2.83 / 2.83 | 3.18 | 4.54 | *darr* @ 0.94 |
| V1B | 0.100 -> 2.700 | 2.60 | 6 | 7 | 2.22 -> 2.02-2.10 | 1.54 s | 1.10x | 2.094 | +0.61 | 2.29 / 2.29 | 3.90 **>3.2** | 4.55 | *kaun* @ 1.90 |
| V2 | 8.800 -> 14.833 | 6.03 | 15 | 27 | 5.56 -> 5.05-5.24 | 5.19 s | 1.10x | 14.441 | +0.39 | 15.27 / 15.27 | 2.89 | 5.21 | *edit* @ 10.76 |
| V3 | 16.367 -> 19.133 | 2.77 | 5 | 6 | 1.85 -> 1.68-1.75 | 1.98 s | 1.10x | 19.003 | +0.13 | 19.20 / 19.20 | 2.52 | 3.03 | *Cardboard* @ 18.20 |
| V4 | 19.333 -> 22.233 | 2.90 | 8 | 12 | 2.96 -> 2.69-2.80 | 2.61 s | 1.06x | 22.127 | +0.11 | 22.49 / 22.37 | 3.07 | 4.61 | *phone* @ 21.57 |
| V5 | 22.400 -> 25.400 | 3.00 | 8 | 12 | 2.96 -> 2.69-2.80 | 2.56 s | 1.08x | 25.393 | +0.01 | 25.82 / 25.78 | 3.13 | 4.69 | *busy* @ 22.61 |
| V6 | 26.000 -> 29.100 | 3.10 | 9 | 11 | 3.33 -> 3.03-3.14 | 2.58 s | 1.05x | 28.769 | +0.33 | 29.15 / 29.01 | 3.49 **>3.2** | 4.27 | *'log'* @ 28.14 |
| V7 | 31.600 -> 35.100 | 3.50 | 10 | 13 | 3.70 -> 3.37-3.49 | 3.33 s | 1.00x | 34.926 | +0.17 | 35.46 / 35.11 | 3.01 | 3.91 | *bhejo* @ 32.37 |
| **A** | | 23.90 | **62** | 91 | 22.96 -> 20.88-21.66 | 20.45 s | | spans 22.54 s | | | | | |
| **B** | | 23.90 | **61** | 88 | 22.59 -> 20.54-21.31 | 19.79 s | | spans 22.15 s | | | | | |

Speed alternatives (same model; the overrun rules pick among them on the measured take):

| line | alternative | speed | start | est end | slack |
|---|---|---|---|---|---|
| V4 | 8 words at 1.10x (the overrun pass) | 1.10x | 19.333 | 22.025 | +0.21 |
| V4 | 8 words at 1.00x | 1.00x | 19.333 | 22.294 | -0.06 |
| V4 | v1 plan: 9 words with toh, comma, 1.10x | 1.10x | 19.333 | 22.219 | +0.01 |
| V5 | 1.10x pass (the overrun step) | 1.10x | 22.400 | 25.361 | +0.04 |
| V5 | 1.06x | 1.06x | 22.400 | 25.425 | -0.03 |
| V5 | v1 plan: 22.500 / 23.700 at 1.10x | 1.10x | 22.500 | 25.394 | +0.01 |
| V6 | 1.04x | 1.04x | 26.000 | 28.795 | +0.30 |
| V6 | 1.06x | 1.06x | 26.000 | 28.743 | +0.36 |
| V6 | 1.10x pass (the overrun step) | 1.10x | 26.000 | 28.643 | +0.46 |
| V6 | approved 10 words at 1.05x (record only) | 1.05x | 26.000 | 28.913 | +0.19 |
| V7 | 1.03x | 1.03x | 31.600 | 34.830 | +0.27 |
| V7 | 1.06x | 1.06x | 31.600 | 34.738 | +0.36 |
| V7 | 1.10x pass (emergency step) | 1.10x | 31.600 | 34.624 | +0.48 |
| V7 | old 11-word line from 31.600 at 1.00x (record only) | 1.00x | 31.600 | 34.857 | +0.24 |

Read-out: every line fits its window at the central estimate; tightest: V5 +0.01 s, V4 +0.11 s, V3 +0.13 s, V7 +0.17 s. V5's
+0.01 s is at 1.08x against the BRIEF's 25.400; its 1.10x pass ends 25.361 s and the hard limit is the 25.48 clunk guard (+0.09 s at 1.08x).
The >3.2 w/s flags (V1B, V6) are monosyllable artefacts: their syllable rates (V1B 4.55, V6 4.27) are below Vlad's measured
4.35 syll/s x the line's speed (4.79, 4.57), so they will not sound rushed. Gaps between lines: V1->V2 6.32 s, V2->V3 1.93 s, V3->V4 0.33 s, V4->V5 0.27 s, V5->V6 0.61 s, V6->V7 2.83 s (all >= 0.15 s).
No VO word falls in 15.85-16.30 (drop-out to reveal) or 25.48-25.90 (the clunk) at the central estimate. Post-payoff VO gap: 2.83 s
(was 3.36 s); across the loop seam: 0.37 s (no dead air > 0.4 s).
V7 cross-check from the dry run (§3): in context the Kokoro V7 spans 3.33 s (3.36 s standalone) and *bhejo* starts 0.98 s after "Us",
so at 1.00x *bhejo* lands at ~32.57 s (the syllable split in §3 says 32.37). "Us dost ko" (31.60-~32.46) overlaps the CTA rise (31.55-32.3) and
*bhejo* follows while the card keyword is still settling (settled 33.05 s); no speed in the gate band moves it before 32.5 s.

---------------------------------------------------------------------------------------------------------------

## 5. Takes (Higgsfield `generate_audio`, Vlad preset, provider defaults; one job each, never resubmitted blindly)

| take | lines | purpose | DEV text (exact) | chars | `vo_chain` passes (speed: lines) |
|---|---|---|---|---|---|
| T0 | V3, V5, V6, V7 | pronunciation test + production (every risk word: V3, V5, V6; plus V7, the loop line) | ये क्राउड फ़्लैट है। कार्डबोर्ड। लोग बिज़ी हैं... अपने 'लोग क्या कहेंगे' में। किसी और की नज़र में, हम भी 'लोग' हैं। उस दोस्त को भेजो जिसे 'लोग' का डर रोकता है। | 159 | 1.10: V3, V5 (overrun step), V6 (overrun step); 1.08: V5; 1.06: V7 (overrun step); 1.05: V6; 1.03: V7 (overrun step); 1.00: V7 |
| T1 | V1, V1B | hooks | सब से बड़ा डर, लोग क्या कहेंगे। ये 'लोग'... असल में हैं कौन? | 60 | 1.10: V1, V1B |
| T2 | V2, V4 | body | हम अपनी ज़िंदगी उनके हिसाब से एडिट करते हैं... जो पूरी वीडियो देखते भी नहीं। असली लोग पीछे बैठे हैं, अपने फ़ोन में। | 115 | 1.10: V2, V4 (overrun step); 1.06: V4 |

ROM for `vo_chain.py process --rom` = the lines' `roman_marked` strings joined in the same order (`script.json` -> `takes[].rom`).
Run `process` once per listed speed on the same downloaded take (`--speed 1.08` etc.; 1.00 skips the stretch), then cut each line from the
pass at its own speed; overrun passes only when a rule in §2 needs them. Order: **T0 first** (pronunciation test and production at once),
then T1, T2. Credits: 3 jobs + 1 retake reserve, <= 2.5 each = <= 10 of the reel's 12 (project balance 187.29); passes are free.

Go / no-go per take (processed durations at the line's planned speed; then §2's overrun rules):
- T0: faster-whisper (hi) finds every risk word with vo_chain `ok` = true (कार्डबोर्ड, फ़्लैट, क्राउड, बिज़ी, नज़र); V3 part 1 <= 1.45 s and
  "Cardboard" <= 1.10 s (onset 18.0-18.3, ends <= 19.133); V5 part 1 <= 1.067 s and part 2 <= 1.733 s at 1.08x (1.10x: part 2 <= 1.78 s);
  V6 <= 3.10 s at 1.05x with the comma cut to 0.20 s; V7 <= 3.50 s at 1.00x; no pause > 0.45 s inside a line except V5's (placed).
  A failed word -> retake only that line with its fallback spelling (§6).
- T1: V1 <= 2.60 s (comma at 0.20 s; rule: 0.10 s, ceiling 2.850 s end), V1B <= 2.60 s.
- T2: V2 <= 6.03 s (ellipsis pause may be cut to 0.30 s); V4 <= 2.900 s at 1.06x (comma at 0.20 s), else its 1.10x pass.
- Whisper normalises nuktas, so z/j and f/p **cannot be verified by ASR**: a human ear (Jawad or the lead) should hear T0 before T1/T2.

---------------------------------------------------------------------------------------------------------------

## 6. Pronunciation risks (test in T0 first)

| rank | DEV | Roman | line | risk | fallback |
|---|---|---|---|---|---|
| 1 | कार्डबोर्ड | Cardboard | V3 | two r + retroflex clusters on the reveal word; a flat read blurs to "kaarbord" | कार्ड-बोर्ड / गत्ता (Gatta: Hindustani for cardboard, used on both sides) |
| 2 | फ़्लैट | flat | V3 | f + cluster; the casting ASR heard लाइफ़ as "लाइप", so f may come out as p ("plat") | फ्लैट (no nukta) / टू-डी (2D), caption "2D" |
| 3 | बिज़ी | busy | V5 | z must not become j ("biji"); payoff keyword | Latin "busy" inside the DEV text (only if the take proves it better) |
| 4 | नज़र | nazar | V6 | z vs j ("najar"); Pakistani ear notices | none needed if z is heard; "najar" is acceptable to Indian ears |
| 5 | क्राउड | crowd | V3 | cluster kr + au diphthong may get an epenthetic vowel ("karaud") | drop the word: "Yeh flat hai. Cardboard." |
| 6 | 'लोग' | 'log' | V5/V6/V7 | quote marks may add a hiccup pause or nothing; the stress on log must survive | remove the quotes from the DEV text |
| 7 | ज़िंदगी | zindagi | V2 | z vs j ("jindagi") | none (common word; check by ear) |
| 8 | फ़ोन | phone | V4 | f vs p ("pone") | फोन (no nukta) |

v2: वजह (old risk 7) left the script with the old V7. The new V7 words (जिसे, का, डर, रोकता) carry no nukta and no English cluster; डर is
already in the hook. Evidence from the casting take's ASR: लाइफ़ -> "लाइप", क्लाइंट -> "ख्लाईट", डेडलाइन -> "देडलाईन", मोशन -> "मोशिन"
(ASR or voice: unknown without a listener). TTS spelling choices: ये (not यह, which reads "yah"), ज़/फ़ written with the nukta (decomposed,
as in the casting text), English loans in Devanagari (क्राउड, फ़्लैट, कार्डबोर्ड, बिज़ी, एडिट, वीडियो, फ़ोन), no digits, no JD, no tags or brackets.

---------------------------------------------------------------------------------------------------------------

## 7. Flags and open questions (for the lead)

1. **Listener**: can Jawad listen to T0 (about 13 s) before T1/T2? z/f sounds (बिज़ी, नज़र, फ़्लैट, फ़ोन, ज़िंदगी) are invisible to the ASR check.
2. **V7 cadence**: the BRIEF wants no final fall; elevenlabs_v4 through Higgsfield takes no delivery tags, so the line ends with "।". The loop is
   now verbal (*darr* -> *darr*). If the take sounds too final, the only lever is "है..." (a trailing read) in a retake.
3. **V6 copy**: with the 29.100 window the approved 10-word line ("Aur kisi aur ki nazar mein...") would now fit (est 28.913 s at 1.05x),
   but the gate and BRIEF r2 keep the 9-word line (reads better, "Ki-" on the 8th). Recorded as 9 words.
4. **Per-line speeds** mean 2-4 local `vo_chain` passes per take (§5): the lead (or the TTS owner) runs them; no extra credits.
5. **Handover** (BRIEF r2 and packet v2 already carry the v2 words, windows and IG line 4 "Us dost ko bhejo jise 'log' ka darr rokta hai."):
   (a) BRIEF r2 §9 scales V7 from v1 by syllables (~3.0 s at 1.00x, ends ~34.45-34.65); the calibrated estimate here is 3.33 s at 1.00x
   (ends 34.926 s, still inside 35.100): the new line is not shorter in time (§4). (b) V4: this script plans to f667 (22.233), 2 frames inside
   the BRIEF's f669, so the gap to V5 at 22.400 stays >= 0.15 s. (c) Music-supervisor: the EP C4 at 31.2 (to ~31.95) now overlaps V7's
   first words from 31.6, and V6 can run to 29.10: move the duck windows to V6 26.0-29.1 and V7 31.6-35.1 (gate fix 3).
6. **AI label** ON at upload (BRIEF §16 default: synthetic voice).
7. No `[VERIFY]` items: the script states nothing about Jawad, no numbers, no claims.

## 8. Self-check

- Hook spoken from 0.10 s, 7 words (A) / 6 (B), <= 7 (SLATE); lockups 3-4 words; readable muted (B: all captions hidden, the lockup
  carries the question); A/B differ only in frames 0-89; V1 lands by 2.485 s (target 2.700, ceiling 2.850, worst bound 2.831).
- Word budget: 62 words (A) in 35.2 s = 1.76 w/s overall; line spans 22.54 s inside 23.90 s of windows; every line fits at the central
  estimate with a rule for every overrun; one breath per phrase: V2 is two breaths around its "..." (9 + 6 words), every other line <= 10.
- Number lock (SLATE §4: "C15 no counts"): no digit, number word or count in any VO line, caption token, end-card line or IG line 4.
- Every line is SLATE/BRIEF copy, a cut of it, or gate-r1 copy (V7); no "main / mera / meri"; no politics, religion, rivalry, counts or claims.
- Cross-border read: *zindagi, hisaab, asli, peeche, busy, nazar, dost, jise, darr, rokta, asal, kaun* are daily words on both sides;
  *bara* and *nahi* follow the house SRT. Gender: V7 is now neutral ("darr rokta hai" agrees with *darr*, not with the friend).
- CTA: the end card's `US DOST KO / *bhejo*` (4 words) is the CTA; V7 speaks it plus the loop clause (SLATE-approved form, 10 words).
- Token table complete: 68 tokens, DEV and ROM counts equal per line and per take; one serif keyword per line, <= 1 per chunk, <= 2 per shot.

## 9. Changelog

- v3 (measured, 2026-10-09): Vlad takes recorded and assembled; V2 -> the 14-word BRIEF fallback (overrun rule); V7 onset
  31.433 (lead decision); measured timings in VO_TIMING.md and `script.json` -> `lines[].measured`.
- v2 (gate r1): V7 + sub new copy (fix 4); V7 onset 31.600 at 1.00x, V6 window 29.100 at 1.05x (fix 3); V4 8-word fallback at 1.06x,
  V5 parts 22.400 / 23.667 at 1.08x, V1 and V5 overrun rules (fix 5); per-line speeds and passes; V3 cut and V6 fallback marked
  approved; all of V1B hidden; वजह risk removed; totals 62 / 61 words (A / B), was 64 / 63.
- v1: first script for the gate (all lines at 1.10x).
