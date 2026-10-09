# VO_TIMING: Reel 5 · C15 · Log Kya Kahenge (Vlad · elevenlabs_v4)

Status: **MEASURED (Vlad takes)** · generated 2026-10-09 06:53 by `pipeline/jawad_reels/log_kya_kahenge_vo.py assemble` · takes: `workspace/jawad_reels/log_kya_kahenge/vo/raw`

Stems (35.200 s, 48 kHz 24-bit mono): `workspace/jawad_reels/log_kya_kahenge/vo/vo_stem.wav` (= hook A; also `lkk_vo_A.wav`), `lkk_vo_B.wav` (hook B). Words: `words.json`
(= A), `lkk_vo_A.words.json`, `lkk_vo_B.words.json` (reel time, `keyword`, `line`, `i`, `hide` per BRIEF section 15). QA image:
`vo_timeline.png` (same folder).

| stem | LUFS (target -16) | TP dBTP (<= -2) | LRA | first voice | last voice | loop seam (V7 end -> V1 start) | words ok | checks |
|---|---|---|---|---|---|---|---|---|
| A | -16.03 | -2.14 | 6.5 | 0.090 | 35.080 | 0.227 s | 61/61 | PASS |
| B | -16.02 | -2.14 | 6.4 | 0.090 | 35.080 | 0.227 s | 60/60 | PASS |

## For the lead (decisions and open items)

- **Total VO**: A 21.95 s of speech (61 words) from 0.100 to 35.073 s; B 21.97 s (60 words). Every line is placed on its beat-table onset except V7.
- **V2 = the 14-word BRIEF fallback** (overrun rule): the 15-word take ran 6.51 s at 1.10x (~6.34 s with the 0.30 s pause; window 6.03 s). Now "Hum zindagi unke hisaab se edit karte hain... jo poori video dekhte bhi nahi." (5.21 s, ends 14.01). script.json is updated (v3); still to update by their owners: BRIEF section 15 V2 chunk `Hum apni` -> `Hum zindagi`, BRIEF section 9 / packet.yaml V2 text, and IG caption line 2 if it should quote the VO exactly.
- **V7 onset 31.433 s (f943) instead of 31.600 (f948)**: six V7 recordings (two alone, four inside two-sentence takes) span 3.95-4.30 s raw; the fastest (V7 t1, 3.95 s) still runs 3.64 s at the 1.10x ceiling (3 processed: 3.64-3.72 s), so from 31.600 the last word would end at 35.24 s, past the 35.100 limit and 40 ms from the loop seam. No BRIEF rule is left (V7 never shortens, never above 1.10x), so the onset moved to the latest frame that ends by 35.100 (end 35.073; loop seam to V1 0.227 s). "Us dost ko" now starts 0.12 s before the CTA caps rise (31.55); *bhejo* lands at 32.158 s. Also 1.10x is outside the gate band 1.00-1.06x. Alternative if the picture must keep f948: accept the tail clipped at the 35.2 s seam (not recommended) or widen the V7 window.
- **V5 part 1 ends 23.510 s** (window 23.467, +0.043 s) at 1.10x: "Log busy hain..." trails off on the held "hain"; the fastest of the 7 V5 recordings (part 1 spans 1.25-1.63 s raw). The O6-complete hit at 23.600 is still inside the pause (part 2 at 23.667; pause 0.157 s).
- **Context takes**: per-line takes of Vlad read short lines at 3.1-3.5 syll/s (the casting paragraph: 4.35), so V1, V1B, V4, V6 and V7 overran even at 1.10x with the allowed pause cuts. vo_config allows 1-3 sentences per take, so they were also recorded in two- or three-sentence takes and cut at the sentence pause (`raw/cuts/cuts.json`): V1, V1B, V4, V5 part 1 and V6 come from those. V5 part 2 comes from the per-line take V5 t1 (its part 2 is the only one within 1.78 s); the two parts are separate segments with a pause between them.
- **Speeds**: V1, V1B, V2, V3, V4, V5 at 1.10x; V6 1.05x; V7 1.10x. V4 at 1.10x (the rule: 1.06x ended 22.333).
- **Edge fades** (local workaround, SHARED_REQUESTS.md R4): vo_chain cuts sentence-final decays at -33 to -37 dBFS; each processed line gets a 5 ms fade-in / 30 ms fade-out before placement.
- **By ear before posting**: z / f in ज़िंदगी, बिज़ी, नज़र, फ़ोन, फ़्लैट (spectrograms say z and f; ASR cannot); V1 whisper writes "kahenge?" (BRIEF wants no rise on V1: a listener should confirm); V7 ends on a full stop (the BRIEF hoped for no final cadence; elevenlabs_v4 takes no delivery tags, so only a listener can judge it).
- **Timing measure**: segment on / off = 20 ms RMS above the segment's peak - 35 dB (`speech_runs`); the stem checks (no-VO windows, first / last voice) use vo_chain's stricter runs (peak - 45 dB on the stem).


## Per-beat timing (measured voiced onset / offset in reel time vs the BRIEF r2 section 9 windows)

Onsets are placed on the grid onsets (first voiced sample of each segment). "target end" = the window end (V3a: 0.15 s before
*Cardboard*; V5a: 23.467). w/s and syll/s are per LINE (all its segments' voiced time; syllables approximate).

| seg | beat | target on | on | d on | target end | end | slack | speed | dur | words | line w/s | line syll/s | keyword @ t | flags |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| V1 | HOOK A | 0.100 | 0.100 | +0.000 | 2.700 | 2.520 | +0.180 | 1.10x | 2.420 | 7 | 2.89 | 4.13 | *darr* @ 0.933 | ok |
| V2 | RE-HOOK 1: JD alone -> heads tilt | 8.800 | 8.800 | +0.000 | 14.833 | 14.010 | +0.823 | 1.10x | 5.210 | 14 | 2.69 | 5.37 | *zindagi* @ 9.015, *edit* @ 10.742, *video* @ 12.633, *nahi* @ 13.615 | ok |
| V3a | REVEAL (orbit) | 16.367 | 16.367 | +0.000 | 18.050 | 17.707 | +0.343 | 1.10x | 1.340 | 4 | 2.40 | 4.33 | *flat* @ 17.064 | ok |
| V3b | REVEAL (orbit) | 18.200 | 18.200 | +0.000 | 19.133 | 18.940 | +0.193 | 1.10x | 0.740 | 1 | 2.40 | 4.33 | *Cardboard* @ 18.200 | ok |
| V4 | THE SINGLE IMAGE (focus pull) | 19.333 | 19.333 | +0.000 | 22.233 | 22.213 | +0.020 | 1.10x | 2.880 | 8 | 2.78 | 4.86 | *phone* @ 21.678 | ok |
| V5a | O6 BURN | 22.400 | 22.400 | +0.000 | 23.467 | 23.510 | -0.043 | 1.10x | 1.110 | 3 | 2.89 | 4.69 | *busy* @ 22.687 | ends +0.043 s after the window |
| V5b | O6 BURN | 23.667 | 23.667 | +0.000 | 25.400 | 25.327 | +0.073 | 1.10x | 1.660 | 5 | 2.89 | 4.69 | *kahenge* @ 24.577 | ok |
| V6 | PAYOFF | 26.000 | 26.000 | +0.000 | 29.100 | 28.950 | +0.150 | 1.05x | 2.950 | 9 | 3.05 | 3.73 | *nazar* @ 26.846, *'log'* @ 28.276 | ok |
| V7 | END CARD + LOOP | 31.600 | 31.433 | -0.167 | 35.100 | 35.073 | +0.027 | 1.10x | 3.640 | 10 | 2.75 | 3.85 | *bhejo* @ 32.158 | onset moved -0.167 s (rule note below) |
| V1B | HOOK B (Trial Reel) | 0.100 | 0.100 | +0.000 | 2.700 | 2.540 | +0.160 | 1.10x | 2.440 | 6 | 2.46 | 2.87 | *kaun* @ 2.125 | ok |

Speech in A: 21.95 s (61 words). Gaps (voice to voice, A): V1->V2 6.280, V2->V3a 2.357, V3a->V3b 0.493, V3b->V4 0.393, V4->V5a 0.187, V5a->V5b 0.157, V5b->V6 0.673, V6->V7 2.483.
Beats that miss their targets by > 0.3 s: none

## CER per line (faster-whisper int8, language hi, NO prompt; CER after nukta / punctuation normalisation, in brackets with English
words whisper wrote in Latin mapped back to the DEV spelling; whisper medium is run as a second ear only when small flags the line)

| line | take | CER small / medium | best | aligned (vo_chain) | heard | keywords | verdict |
|---|---|---|---|---|---|---|---|
| V1 | lkk_V1_cH1t2_t1.wav | 0.071 (0.071) / 0.000 (0.000) | 0.000 | 7/7 | small: सब से बड़ाटर, लोग क्या कहेंगे? / medium: सब से बडा डर लोग क्या कहेंगे? | *darr* aligned "डर,", free small "बड़ाटर," 0.47, medium "डर" 3.00 -> ok | ok |
| V1B | lkk_V1B_cG1bt1_t1.wav | 0.100 (0.100) | 0.100 | 6/6 | small: ये लोग आसल में हैं कोन? | *kaun* aligned "कौन?", free small "कोन?" 1.20 -> ok | ok |
| V2 | lkk_V2_t2.mp3 | 0.065 (0.065) | 0.065 | 14/14 | small: हम जिन्दगी उनके हिसाप से एडिट करते है जो पूरी विडियो देखते भी नहीं | *zindagi* aligned "जिन्दगी", free small "जिन्दगी" 1.20 -> ok; *edit* aligned "एडिट", free small "एडिट" 3.00 -> ok; *video* aligned "वीडियो", free small "विडियो" 1.20 -> ok; *nahi* aligned "नहीं।", free small "नहीं" 3.00 -> ok | ok; z/f by ear: zindagi |
| V3 | lkk_V3_t1.mp3 | 0.267 (0.267) / 1.200 (0.000) | 0.000 | 5/5 | small: ये क्राउट फलाट है काट बोर्ट / medium: ये Crowdflat है, Cardboard | *flat* aligned "फलाट", free small "फलाट" 1.20, medium "क्राउड फ्लैट" 0.47 -> ok; *Cardboard* aligned "कार्डबोर्ड।", free small "काटबोर्ट" 0.47, medium "कार्डबोर्ड" 3.00 -> ok | ok; z/f by ear: flat |
| V4 | lkk_V4_cG2t2_t1.wav | 0.125 (0.125) | 0.125 | 8/8 | small: असली लोग पीचे बेटे हैं अपने फोन में | *phone* aligned "फ़ोन", free small "फोन" 3.00 -> ok | ok; z/f by ear: phone |
| V5 | lkk_V5_cG2t2_t1.wav | 0.000 (0.000) | 0.000 | 8/8 | small: लोग बिजी है, अपने लोग क्या कहेंगे में? | *busy* aligned "बिज़ी", free small "बिजी" 3.00 -> ok; *kahenge* aligned "कहेंगे", free small "कहेंगे" 3.00 -> ok | ok; z/f by ear: busy |
| V5b | lkk_V5_t1.mp3 | 0.000 (0.000) | 0.000 | 8/8 | small: लोग बिजी है, अपने लोग क्या कहेंगे में? | *busy* aligned "बिज़ी", free small "बिजी" 3.00 -> ok; *kahenge* aligned "कहेंगे", free small "कहेंगे" 3.00 -> ok | ok; z/f by ear: busy |
| V6 | lkk_V6_cG3t1_t1.wav | 0.000 (0.000) | 0.000 | 9/9 | small: किसी और की नजर में हम भी लोग है | *nazar* aligned "नज़र", free small "नजर" 3.00 -> ok; *'log'* aligned "लोग", free small "लोग" 3.00 -> ok | ok; z/f by ear: nazar |
| V7 | lkk_V7_t1.mp3 | 0.053 (0.053) | 0.053 | 10/10 | small: उस दोस्त को भेजो जिसे लोग का दर रोकता है | *bhejo* aligned "भेजो", free small "भेजो" 3.00 -> ok | ok |

## Rules applied (BRIEF r2 section 9 / SCRIPT v2 section 2)

- V1: 2.670 s > 2.60 s: pause after "darr," 0.350 -> 0.100 s (overrun rule)
- V2: pause after "hain..." 0.500 -> 0.300 s
- V4: pause after "hain," 0.280 -> 0.200 s
- V4: 1.06x ends 22.333 > 22.233: next pass
- V5: 1.08x: part 1 1.120 s (ends 23.520, max 23.467), part 2 1.690 s (max 1.733): next pass
- V5: 1.10x: part 1 1.110 s (ends 23.510, max 23.467), part 2 1.660 s (max 1.780): next pass
- **V5 FAIL**: part 1 1.110 s ends 23.510 > 23.467 at 1.10x (no rule left; the pause still holds 23.600: yes)
- V6: pause after "mein," 0.370 -> 0.200 s
- V7: 1.00x ends 35.580 > 35.100: next pass
- V7: 1.03x ends 35.470 > 35.100: next pass
- V7: 1.06x ends 35.370 > 35.100: next pass
- V7: 1.10x ends 35.240 > 35.100: next pass
- V7: onset moved 31.600 -> 31.433 s (f943, -0.167 s) so the last word ends by 35.100: decision for the lead
- V7: 1.10x is outside the gate band 1.00-1.06x: tell the lead
- **V7 FAIL**: ends 35.240 > 35.100 at 1.10x even after the retakes: no rule left (V7 never shortens, never above 1.10x)

## Pronunciation test

Batch 1 (carriers `lkk_P1..P5_t1.mp3`, `vo/pron_check.json`): every risk word in its script spelling, whisper small +
medium per sentence. P1 `ये क्राउड फ़्लैट है। ये कार्डबोर्ड है।` medium heard "Crowdflat ... Cardboard" (the English words), per
sentence "ये Crowdflat है।" / "ये कार्टबोर्ड है।"; P2 (fallbacks कार्ड-बोर्ड, फ्लैट without nukta) came out worse ("कार्टबोड",
small "ख्लाट"); P3 बिज़ी / नज़र / ज़िंदगी / फ़ोन all heard (medium CER 0.043); P4 both sentences spoken (whisper drops the repeat), the
quoted 'लोग' has no gap > 80 ms and runs 0.2 s longer than the plain one (the stress survives); P5 Latin "busy" is not better than
बिज़ी and गत्ता is heard "गता". ASR normalises nuktas, so z / f were checked on spectrograms: बिज़ी, नज़र, ज़िंदगी are continuous
4-6 kHz frication with an unbroken voicing bar (no stop closure = z, not j); फ़ोन, फ़्लैट are broadband frication with no closure
silence before it (= f, not ph). Verdict: every primary spelling kept, no fallback needed. A human ear should still confirm z / f
before the post (SCRIPT section 7.1).

## Word timings cross-check (independent whisper pass on each whole stem, no snapping)

- A: matched 61/61; within-phrase word starts differ from `words.json` by mean 0.025 / median 0.014 / max 0.190 s. Over 0.15 s: V1 "log" 1.330 vs 1.520, V2 "Hum" 8.800 vs 8.320, V3 "Yeh" 16.357 vs 15.920, V7 "Us" 31.443 vs 30.980 (words right after a silence: whisper puts their start inside the silence, or late on the vowel for a soft onset such as l; words.json keeps the voiced onset, checked on the 20 ms envelope). Keywords (words.json vs independent): darr 0.933 / 0.920, zindagi 9.015 / 9.000, edit 10.742 / 10.720, video 12.633 / 12.620, nahi 13.615 / 13.620, flat 17.064 / 17.020, Cardboard 18.200 / 18.060, phone 21.678 / 21.660, busy 22.687 / 22.680, kahenge 24.577 / 24.580, nazar 26.846 / 26.860, 'log' 28.276 / 28.260, bhejo 32.158 / 32.180.
- B: matched 60/60; within-phrase word starts differ from `words.json` by mean 0.022 / median 0.013 / max 0.110 s. Over 0.15 s: V2 "Hum" 8.800 vs 8.260, V3 "Yeh" 16.357 vs 15.840, V7 "Us" 31.443 vs 30.980 (words right after a silence: whisper puts their start inside the silence, or late on the vowel for a soft onset such as l; words.json keeps the voiced onset, checked on the 20 ms envelope). Keywords (words.json vs independent): kaun 2.125 / 2.140, zindagi 9.015 / 9.020, edit 10.742 / 10.700, video 12.633 / 12.620, nahi 13.615 / 13.620, flat 17.064 / 17.020, Cardboard 18.200 / 18.060, phone 21.678 / 21.660, busy 22.687 / 22.680, kahenge 24.577 / 24.580, nazar 26.846 / 26.860, 'log' 28.276 / 28.260, bhejo 32.158 / 32.180.

## Takes used

| line | take | recorded as | speed | CER (best) | matched |
|---|---|---|---|---|---|
| V1 | `lkk_V1_cH1t2_t1.wav` | sentence 2 of 2 of `lkk_H1_t2.mp3` (cut 4.390-7.811 s) | 1.10x | 0.000 | 7/7 |
| V1B | `lkk_V1B_cG1bt1_t1.wav` | sentence 1 of 2 of `lkk_G1b_t1.mp3` (cut 0.000-2.925 s) | 1.10x | 0.100 | 6/6 |
| V2 | `lkk_V2_t2.mp3` | its own take | 1.10x | 0.065 | 14/14 |
| V3 | `lkk_V3_t1.mp3` | its own take | 1.10x | 0.000 | 5/5 |
| V4 | `lkk_V4_cG2t2_t1.wav` | sentence 1 of 2 of `lkk_G2_t2.mp3` (cut 0.000-3.570 s) | 1.10x | 0.125 | 8/8 |
| V5 | `lkk_V5_cG2t2_t1.wav` | sentence 2 of 2 of `lkk_G2_t2.mp3` (cut 3.570-7.967 s) | 1.10x | 0.000 | 8/8 |
| V5 part 2 | `lkk_V5_t1.mp3` | its own take | 1.10x | 0.000 | 8/8 |
| V6 | `lkk_V6_cG3t1_t1.wav` | sentence 1 of 2 of `lkk_G3_t1.mp3` (cut 0.000-3.610 s) | 1.05x | 0.000 | 9/9 |
| V7 | `lkk_V7_t1.mp3` | its own take | 1.10x | 0.053 | 10/10 |

## Every candidate take scored (`log_kya_kahenge_vo.py cands`; segment end = reel time at the rule-chosen speed)

| line | take | CER small (best) | matched | speed | segments: dur -> end | rule fails | used |
|---|---|---|---|---|---|---|---|
| V1 | `lkk_V1_cG1bt1_t1.wav` | 0.071 (0.000) | 7/7 | 1.10x | V1 2.480 -> 2.580 | - |  |
| V1 | `lkk_V1_cH1t2_t1.wav` | 0.071 (0.000) | 7/7 | 1.10x | V1 2.420 -> 2.520 | - | yes |
| V1 | `lkk_V1_cH1t1_t1.wav` | 0.071 (0.071) | 7/7 | 1.10x | V1 2.640 -> 2.740 | - |  |
| V1 | `lkk_V1_t4.mp3` | 0.071 (0.000) | 7/7 | 1.10x | V1 2.770 -> 2.870 | ends 2.870 > hard 2.850: retake |  |
| V1B | `lkk_V1B_cG1bt1_t1.wav` | 0.100 (0.100) | 6/6 | 1.10x | V1B 2.440 -> 2.540 | - | yes |
| V1B | `lkk_V1B_cG1at1_t1.wav` | 0.100 (0.100) | 6/6 | 1.10x | V1B 2.580 -> 2.680 | - |  |
| V1B | `lkk_V1B_t2.mp3` | 0.100 (0.100) | 6/6 | 1.10x | V1B 2.680 -> 2.780 | ends 2.780 > hard 2.700: retake |  |
| V2 | `lkk_V2_t2.mp3` | 0.065 (0.065) | 14/14 | 1.10x | V2 5.210 -> 14.010 | - | yes |
| V2 | `lkk_V2_t3.mp3` | 0.065 (0.065) | 14/14 | 1.10x | V2 5.240 -> 14.040 | - |  |
| V3 | `lkk_V3_t1.mp3` | 0.267 (0.000) | 5/5 | 1.10x | V3a 1.340 -> 17.707; V3b 0.740 -> 18.940 | - | yes |
| V4 | `lkk_V4_cG2t2_t1.wav` | 0.125 (0.125) | 8/8 | 1.10x | V4 2.880 -> 22.213 | - | yes |
| V4 | `lkk_V4_cG2t1_t1.wav` | 0.125 (0.125) | 8/8 | 1.10x | V4 2.980 -> 22.313 | ends 22.313 > 22.233 at 1.10x: retake V4 |  |
| V4 | `lkk_V4_cH3t1_t1.wav` | 0.125 (0.125) | 8/8 | 1.10x | V4 2.980 -> 22.313 | ends 22.313 > 22.233 at 1.10x: retake V4 |  |
| V5 | `lkk_V5_cG2t2_t1.wav` | 0.000 (0.000) | 8/8 | 1.10x | V5a 1.110 -> 23.510; V5b 2.150 -> 25.817 | part 2 2.150 s > 1.78 s at 1.10x: retake with "हैं," and part 2 at 23.650; part 1 1.110 s ends 23.510 > 23.467 at 1.10x (no rule left; the pause still holds 23.600: yes); part 2 ends 25.817 > 25.480 (clunk guard) | yes |
| V5 | `lkk_V5_cG2t1_t1.wav` | 0.000 (0.000) | 8/8 | 1.10x | V5a 1.220 -> 23.620; V5b 2.080 -> 25.747 | part 2 2.080 s > 1.78 s at 1.10x: retake with "हैं," and part 2 at 23.650; part 1 1.220 s ends 23.620 > 23.467 at 1.10x (no rule left; the pause still holds 23.600: NO); part 2 ends 25.747 > 25.480 (clunk guard) |  |
| V5 | `lkk_V5_cH3t1_t1.wav` | 0.000 (0.000) | 8/8 | 1.10x | V5a 1.220 -> 23.620; V5b 2.050 -> 25.717 | part 2 2.050 s > 1.78 s at 1.10x: retake with "हैं," and part 2 at 23.650; part 1 1.220 s ends 23.620 > 23.467 at 1.10x (no rule left; the pause still holds 23.600: NO); part 2 ends 25.717 > 25.480 (clunk guard) |  |
| V5 | `lkk_V5_t1.mp3` | 0.000 (0.000) | 8/8 | 1.10x | V5a 1.490 -> 23.890; V5b 1.660 -> 25.327 | part 1 1.490 s ends 23.890 > 23.467 at 1.10x (no rule left; the pause still holds 23.600: NO) | yes |
| V6 | `lkk_V6_cG3t1_t1.wav` | 0.000 (0.000) | 9/9 | 1.05x | V6 2.950 -> 28.950 | - | yes |
| V6 | `lkk_V6_cG3t2_t1.wav` | 0.000 (0.000) | 9/9 | 1.10x | V6 3.040 -> 29.040 | - |  |
| V7 | `lkk_V7_t1.mp3` | 0.053 (0.053) | 10/10 | 1.10x | V7 3.640 -> 35.073 | ends 35.240 > 35.100 at 1.10x even after the retakes: no rule left (V7 never shortens, never above 1.10x) | yes |
| V7 | `lkk_V7_t2.mp3` | 0.105 (0.105) | 10/10 | 1.10x | V7 3.700 -> 35.100 | ends 35.300 > 35.100 at 1.10x even after the retakes: no rule left (V7 never shortens, never above 1.10x) |  |
| V7 | `lkk_V7_cH1t2_t1.wav` | 0.053 (0.053) | 10/10 | 1.10x | V7 3.720 -> 35.087 | ends 35.320 > 35.100 at 1.10x even after the retakes: no rule left (V7 never shortens, never above 1.10x) |  |

## Higgsfield credits (Vlad, elevenlabs_v4; own get_cost preflights, ledger `vo/credits.json`)

Spent **11.50** of the reel budget 25 in 34 jobs (P1 0.23, P2 0.23, P3 0.46, P4 0.23, P5 0.23, V1_t1 0.23, V1B_t1 0.23, V2_t1 0.46, V3_t1 0.23, V4_t1 0.23, V5_t1 0.23, V6_t1 0.23, V7_t1 0.23, V1_t2 0.23, V1_t3 0.23, V1_t4 0.23, V1B_t2 0.23, V2_t2 0.46, V2_t3 0.46, V4_t3 0.23, V5_t2 0.23, V6_t2 0.23, V7_t2 0.23, G1a_t1 0.46, G1b_t1 0.46, G2_t1 0.46, G2_t2 0.46, G3_t1 0.46, G3_t2 0.46, H1_t1 0.46, H1_t2 0.46, H2_t1 0.46, H2_t2 0.46, H3_t1 0.69). Balance checks: 6978.56 (before batch 1 (pronunciation carriers)); 6973.73 (before batch 2 (line takes V1..V7, t1)); 6965.68 (before batch 3 (retakes for the timing overruns and the V2 fallback)); 6962.92 (before batch 4 (two-sentence context takes); drop since batch 3 = 2.76 = exactly my batch-3 jobs); 6956.94 (before batch 5 (context takes with the overrunning line first)); 6933.02 (after the run (no further jobs); the drop since batch 5 beyond my 2.53 is other spend on the account).
