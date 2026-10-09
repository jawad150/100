# VO_TIMING · Reel 2 · C11 · Bijli Chali Gayi (@jawad_mp4)

2026-10-09, hinglish-scriptwriter, `pipeline/jawad_reels/bijli_chali_gayi_vo.py assemble` (measured; replaces the estimates of SCRIPT section 4). Voice: Higgsfield preset Vlad, `elevenlabs_v4`, Devanagari text; chain `vo_chain.py` per vo_config. Targets: BRIEF r2 section 6.7 (bold = may not move, the rest +-0.25 s).

- **Stem A** `workspace/jawad_reels/bijli_chali_gayi/vo/vo_stem.wav`: 1664000 samples (34.667 s) at 48000 Hz, -16.00 LUFS integrated, -2.00 dBTP, LRA 6.6 LU, VO 0.090-34.120 s, 22.16 s of voiced speech, 62 words (12 keywords), 100 % of word starts on voice; gain +0.40 dB, limiter on.
- **Stem B** `workspace/jawad_reels/bijli_chali_gayi/vo/vo_stem_B.wav`: 1664000 samples (34.667 s) at 48000 Hz, -16.00 LUFS integrated, -2.00 dBTP, LRA 6.6 LU, VO 0.300-34.120 s, 22.04 s of voiced speech, 61 words (11 keywords), 100 % of word starts on voice; gain +0.60 dB, limiter on.
- Words: `workspace/jawad_reels/bijli_chali_gayi/vo/words.json` (A), `words_B.json` (B), and the BRIEF 6.14 names `bijli_chali_gayi_vo_A.words.json` / `_B.words.json`; reel time, offset 0.
- V2 "Yaad hai?" measured 0.730 s (onset of याद to the end of है? + 20 ms): GATE fix-5 fallback 1.550 (lead OK needed).

## Per-beat timing vs BRIEF r2 6.7

| line | brief window (s) | placed t0 → t1 (s) | anchor word @ placed (target, Δ) | beat @ anchor | words · syl | speech s | w/s | speed | CER (best) | misses > 0.3 s / bold |
|---|---|---|---|---|---|---|---|---|---|---|
| V1 | 0.100-1.300 | 0.085 → 1.305 | Bijli @ 0.085 (0.100, -0.015) | 0.13 (f2.6) | 3 · 6 | 1.22 | 2.46 | 1.10 | 0.000 | none |
| V2 | 1.550-2.000 | 1.545 → 2.255 | Yaad @ 1.545 (1.550, -0.005) | 2.32 (f46.3) | 2 · 2 | 0.71 | 2.82 | 1.10 | 0.000 | BOLD end passed by 0.255 s |
| V1B | 0.300-1.950 | 0.300 → 2.347 | Yeh @ 0.300 (0.300, +0.000) | 0.45 (f9.0) | 4 · 5 | 1.80 | 2.22 | 1.10 | 0.000 | ends 0.397 s after the window |
| V3a | 3.000-4.000 | 2.920 → 4.000 | Light @ 2.920 (3.000, -0.080) | 4.38 (f87.6) | 3 · 5 | 1.08 | 2.78 | 1.08 | 0.000 | none |
| V3b | 4.200-6.450 | 4.260 → 6.430 | chhat @ 5.351 (5.400, -0.049) | 8.03 (f160.5) | 7 · 11 | 2.17 | 3.23 | 1.08 | 0.077 | none |
| V4 | 6.600-7.850 | 6.550 → 7.850 | Jab @ 6.550 (6.600, -0.050) | 9.82 (f196.5) | 4 · 6 | 1.30 | 3.08 | 1.08 | 0.000 | none |
| V5 | 11.000-12.650 | 10.882 → 12.612 | bachche @ 11.333 (11.333, +0.000) | 17.00 (f340.0) | 5 · 8 | 1.73 | 2.89 | 1.08 | 0.100 | none |
| V6 | 13.150-14.600 | 13.130 → 14.540 | editor @ 13.367 (13.367, +0.000) | 20.05 (f401.0) | 4 · 7 | 1.41 | 2.84 | 1.08 | 0.000 | none |
| V7 | 16.400-18.830 | 16.400 → 19.260 | Aur @ 16.400 (16.400, +0.000) | 24.60 (f492.0) | 8 · 12 | 2.86 | 2.80 | 1.10 | 0.000 | ends 0.430 s after the window |
| V8 | 18.950-22.390 | 19.380 → 23.080 | Ctrl+S @ 21.467 (21.333, +0.134) | 32.20 (f644.0) | 9 · 17 | 3.70 | 2.43 | 1.10 | 0.000 | ends 0.690 s after the window; BOLD anchor 21.467 outside 20.667-21.333 (+0.134 s) |
| V10 | 23.680-26.300 | 23.990 → 26.190 | Bijli @ 24.000 (24.000, +0.000) | 36.00 (f720.0) | 6 · 13 | 2.20 | 2.73 | 1.10 | 0.000 | none |
| V11 | 27.300-28.200 | 27.313 → 28.473 | sabr @ 27.333 (27.333, +0.000) | 41.00 (f820.0) | 2 · 4 | 1.16 | 1.72 | 1.10 | 0.000 | none |
| V12 | 31.650-34.100 | 31.420 → 34.100 | Aap @ 31.430 (31.667, -0.237) | 47.14 (f942.9) | 9 · 12 | 2.68 | 3.36 | 1.06 | 0.000 | none |
| V9 | 22.510-23.320 | dropped (ladder F4) | - | - | 3 · 4 | - | - | - | 0.000 (measured on `T4_r3.mp3`) | not in the VO |

Flags: lines above 3.2 words/s: V3b, V12.

## Takes, CER and keywords

CER = character error rate of the free transcript (no initial prompt, so the ASR is not told the text) against the DEV text sent, after folding nuktas / candrabindu and spaces and mapping Latin loan words (whisper writes "editing" for एडिटिंग). Retake rule: best CER > 0.15 or the keyword not heard.

| line | take (source) | DEV sent | heard (whisper medium, no prompt) | CER small / medium / best | keyword heard | aligned | retake |
|---|---|---|---|---|---|---|---|
| V1 | `TA_r2.mp3` (group) | बिजली चली गई। | विजली चली गई | 0.000 / 0.143 / 0.000 | small: बिजली (3.00), medium: विजली (0.76) | 3/3 | no |
| V2 | `TA_r2.mp3` (group) | याद है? | याद हैं। | 0.000 / 0.000 / 0.000 | small: याद (3.00), medium: याद (3.00) | 2/2 | no |
| V1B | `V1Bc_r1.mp3` (line) | ये आवाज़, याद है? | यह आवाज याद है? | 0.000 / 0.143 / 0.000 | small: आवाज (3.00), medium: आवाज (3.00) | 4/4 | no |
| V3a | `T2m_r1.mp3` (group) | लाइट जाती थी, | light जाती थी | 0.167 / 0.000 / 0.000 | small: लाइट (3.00), medium: लाइट (3.00) | 3/3 | no |
| V3b | `T2m_r2.mp3` (group) | तो पूरा मुहल्ला छत पे होता था। | तो पूरा मुहला च्छत पे होता था। | 0.154 / 0.077 / 0.077 | small: च्हत्पे (0.76), medium: च्छत (3.00) | 7/7 | no |
| V4 | `T2m_r2.mp3` (group) | जब वापस आती थी... | जब वापस आती थी। | 0.125 / 0.000 / 0.000 | small: वापस (3.00), medium: वापस (3.00) | 4/4 | no |
| V5 | `V5_r1.mp3` (line) | फिर वो बच्चे बड़े हुए। | फिर वो बच्चे बड़े हुए हैं। | 0.100 / 0.100 / 0.100 | small: बच्छे (1.20), medium: बच्चे (3.00) | 5/5 | no |
| V6 | `T3_r1.mp3` (group) | कुछ एडिटर बन गए। | कुछ एडिटर बन गए। | 0.200 / 0.000 / 0.000 | small: एटिटर (0.76), medium: एडिटर (3.00) | 4/4 | no |
| V7 | `T4_r2.mp3` (group) | और बिजली बन गई सब से बड़ी दुश्मन। | और बिजली बन गई सब से बड़ी दुश्मन। | 0.111 / 0.000 / 0.000 | small: बड़ीतुष्मन (0.76), medium: दुश्मन। (3.00) | 8/8 | no |
| V8 | `T4_r3.mp3` (group) | हर देसी एडिटर की उंगली ख़ुद कंट्रोल-एस दबाती है। | हर देसी एडिटर की उंग्ली खुद कंट्रोल-S दबाती हैं. | 0.042 / 0.000 / 0.000 | small: खुद (3.00), medium: खुद (3.00) | 9/9 | no |
| V9 | `T4_r3.mp3` (group) | हर तीस सेकंड। | हर तीस सेकंड। | 0.429 / 0.000 / 0.000 | small: ती (0.76), medium: तीस (3.00) | 3/3 | no |
| V10 | `T5_r2.mp3` (group) | बिजली ने हमें एडिटिंग नहीं सिखाई... | बिजली ने हमें एडिटिंग नहीं सिखाई। | 0.000 / 0.000 / 0.000 | small: एडिटिंग (3.00), medium: एडिटिंग (3.00) | 6/6 | no |
| V11 | `T5_r2.mp3` (group) | सब्र सिखाया। | सब्र सिखाया। | 0.000 / 0.000 / 0.000 | small: सब्र (3.00), medium: सब्र (3.00) | 2/2 | no |
| V12 | `V12_r1.mp3` (line) | आप के घर लाइट जाने पे क्या होता था? | आपके घर लाइट जाने पे क्या होता था? | 0.250 / 0.000 / 0.000 | small: गर (1.20), medium: घर (3.00) | 9/9 | no |

## Pronunciation batch (SCRIPT 9 risk words in carrier phrases)

| take | text sent | risk word | heard (medium) · CER | heard (small) · CER | verdict |
|---|---|---|---|---|---|
| `P0.mp3` | ये शब्द है सब्र। सब्र सिखाया। | सब्र (sabr (primary)) | ये शब्द है सब्र, सब्र सिखाया · 0.000 | ये शब्द है, सब्र, सब्र सिखाया · 0.000 | ok: heard सब्र by both models; kept |
| `P1.mp3` | ये शब्द है सबर। सबर सिखाया। | सबर (sabr (fallback)) | ये शब्द है सबर, सबर सिखाया। · 0.000 | ये शब्द है, सबर, सबर सिखाया · 0.000 | ok, not needed |
| `P2.mp3` | ये शब्द है कंट्रोल-एस। ख़ुद कंट्रोल-एस दबाती है। | कंट्रोल-एस / ख़ुद (Ctrl+S (hyphen) + khud (nukta)) | ये शब्ध है कुंट्रोल -ऐस। खुद कुंट्रोल -ऐस दबाती है। · 0.182 | ये शब्द है कुट्रूल एस खुट कुट्रूल एस दबाती है · 0.182 | ok: longest silence inside कंट्रोल-एस 0.055 s (< 0.12); ख़ुद heard खुद (medium) / खुट (small); kept both |
| `P3.mp3` | ये शब्द है कंट्रोल एस। खुद कंट्रोल एस दबाती है। | कंट्रोल एस / खुद (P-ctrl fallback + khud fallback) | ये शब्ध है खुट -कुंट्रोल -एस दबाती है। · 0.311 | ये शब्द है कंट्रोल एस कुत कंट्रोल एस दबाती है · 0.044 | worse: 0.090-0.095 s gaps inside कंट्रोल एस; खुद heard कुत (small): fallbacks rejected |
| `P4.mp3` | ये शब्द है आवाज़। ये आवाज़ याद है? | आवाज़ (awaaz (nukta z)) | ये शब्द है आवाज, ये आवाज याद है? · 0.062 | ये शब्द है, आवाज ये आवाज याज है? · 0.094 | ok: ASR folds the nukta (आवाज), the spectrogram shows continuous frication to the end of the word, no closure/burst (z, not j) |
| `P5.mp3` | ये शब्द है एडिटिंग। हमें एडिटिंग नहीं सिखाई। | एडिटिंग (editing) | ये शब्द है एडिटिंग। हमें एडिटिंग नहीं सिखाई। · 0.000 | ये शब्द है, एदिटिं, हमें एदिटिं नहीं सिखाई · 0.095 | ok: heard एडिटिंग exactly (medium) |
| `P6.mp3` | ये शब्द है मोहल्ला। पूरा मोहल्ला छत पे था। | मोहल्ला (mohalla) | ये शब्द है मुहल्ला पूरा मुहल्ला च्छत पे था। · 0.100 | ये शब्द है, महल्ला पूरा महल्ला चथपे ता · 0.150 | carrier ok (medium: मुहल्ला, double l kept), but in the line context all three takes were heard महला / मौल्ला (V3b CER 0.172): SCRIPT 9 fallback मुहल्ला used for V3b (T2m, V3bm) |
| `P7.mp3` | ये शब्द है सेकंड। हर तीस सेकंड। | सेकंड / तीस (second / tees) | ये शब्द है सेकिंड, हर तीस सेकिंड। · 0.069 | ये शब्द है, सेकिन्ट, हर ती सेकिन्ट · 0.310 | ok: heard सेकिंड with its final stop, तीस (medium) |
| `P8.mp3` | ये शब्द है दुश्मन। सब से बड़ी दुश्मन। | दुश्मन / बड़ी (dushman / bari) | ये शब्द है दुष्मन, सब से बड़ी दुष्मन। · 0.057 | ये शब्द है दूश्मन, सब से बड़ी दूश्मन · 0.057 | ok: दुष्मन (same sound), बड़ी |

## Credits (Higgsfield, voice generation only)

- 58 requests submitted, **15.41 credits** of the reel budget 25 (each preflighted with get_cost: 0.23 credits up to 50 characters, 0.46 for 51-100); 11 balance checks, lowest 6927.96 (guard 6800). Ledger: `workspace/jawad_reels/bijli_chali_gayi/vo/credits.json`; every request with its job id and exact text: `workspace/jawad_reels/bijli_chali_gayi/vo/requests.json`.

## Ladder steps used (BRIEF 6.7 overrun ladder)

- **F1 (speed):** every line measured at 1.10x first; V3a, V3b, V4, V5, V6 fit at 1.08x and V12 at 1.06x (gentler), V1, V2, V1B, V7, V8, V10, V11 need 1.10x. Nothing above 1.10x, no pitch shift.
- **F2 (gaps):** 0.12 s minimum between lines (measured at -55 dBFS, 20 ms RMS, on the mastered lines).
- **F3 (V10 without humein) tested, not used:** takes `T5f3_r1/r2` give V10 2.02 s instead of 2.20-2.25 s. The dense block at Vlad's measured pace is V7 2.86 + V8 3.61-3.70 + V9 1.26 + V10 2.02 + 3 x 0.12 = 10.10-10.20 s against the 9.90 s between the bold V7 start (16.400) and the bold V10 end (26.300): still 0.20-0.30 s over, so F3 alone cannot fix it.
- **F4 (drop V9) used:** `Har tees second.` is not in the VO. Timeline: show U3F `Saved · har 30 sec` as the last chip (f712-f719); the spoken-number lock (SLATE 4) allows that chip only under F4. With V9 out, V10 keeps "humein" and lands "Bijli" exactly on the f720 candle cut (24.000), ending 26.190. V9's best take (`T4_r3`, CER 0.000 medium) is processed and kept if the lead wants to trade something else for it.
- Why the windows overrun: the chosen lines run 3.8-5.4 syllables/s before the speed-up (median 4.3; the dense block's V7 3.8 and V8 4.2), against the 4.5 the BRIEF 6.7 windows assume (4.95 after 1.10x). 30 single-line takes and 19 grouped takes were measured (plus 9 pronunciation carriers); grouped takes (SCRIPT 7) read faster than single lines and supplied 10 of the 13 placed lines.

## Lead decisions needed

- **V2 "Yaad hai?" (hook A):** 0.70-0.77 s after 1.10x in all 8 takes (TA x5, single x3), so neither the SLATE slot (<= 0.43 s at 2.200) nor the GATE fix-5 fallback (<= 0.45 s at 1.550) can hold it. Placed at the fallback, 1.545 → 2.255: "Yaad" sits between the beep pairs and "hai?" (1.90-2.255) runs under the f60/f64 pulses (2.000-2.070, 2.133-2.203). Needs the lead OK (SLATE 3.2 deviation) plus a sound call: drop or duck the f60/f64 pair in version A, or accept the overlap. The SLATE slot (2.200 → ~2.91) would cross the f79 splice by ~0.28 s: not used.
- **V8 "Ctrl+S" (bold f620-f640):** lands at 21.467 (f644), +0.134 s. It cannot land earlier: V7 starts on the bold 16.400 and runs 2.86 s, then the 0.12 s gap and 2.09 s from "Har" to "Ctrl+S". The nearest keycap presses are f640 (21.333) and f650 (21.667); the timeline builder can start the 8th-note presses on the word (f644) or keep f640.
- **V7 end 19.26 (+0.43 s):** "dushman" (18.62-19.26) now overlaps the L8 iris cues of BRIEF 6.10 (18.633-19.033) again.
- **V1B (hook B, trial):** DEV punctuation `ये आवाज़,` instead of `ये आवाज़...` (the ellipsis made Vlad drawl "ye awaaz" to 1.42-1.57 s; with a comma 1.09-1.12 s); the caption tokens are unchanged (`awaaz...`). "Ye awaaz" runs 0.300-1.420, so its final z overlaps the first f40 pulse (1.333-1.403); the f44 pulse (1.467-1.537) sits in the pause. "yaad" is on f50 (1.667) and the line ends 2.347 (+0.40 s after the 1.950 window end, before the HB lockup exit ends at 2.617 and the splice at 2.633). Alternative: "yaad" at 1.567 ends 2.247.
- **V3b spelling:** DEV `मुहल्ला` (SCRIPT 9 fallback) because `मोहल्ला` was heard महला / मौल्ला in every context take (V3b_r1 CER 0.231, V3b_r2 0.154). The caption stays `mohalla`. Whisper still writes a single l (मुहला); the lateral lasts about 0.1 s on the spectrogram: listener check.
- **V1 "Bijli":** whisper small hears बिजली on every take; whisper medium hears विजली on 4 of the 5 takes that fit before the f40 beep (CER 0.143). The spectrogram shows a prevoiced /b/ with a release burst. The one take medium hears as बिजली (`TA_r3`) runs 1.35 s, 0.10 s into the beep. Listener check; GATE minor 9's mix test should expect either spelling or use whisper small.

## Other measured deviations (< 0.3 s)

- V11 ends 28.473 (+0.273 s after 28.200); the riser starts quietly at 28.133, the power return is at 29.333.
- V12 starts 31.420 (-0.23 s, inside the +-0.25 s rule; the cheer ends at 31.1) and ends on the bold 34.100.
- V3a starts 2.920 (-0.08), V3b "chhat" onset 5.351 (f160.5, never before f160), V4 ends exactly 7.850 (>= 0.15 s before the f240 slam), V5 "bachche" 11.333 (f340), V6 "editor" 13.367 (f401), V10 "Bijli" 24.000 (f720), V11 "sabr" 27.333 (f820): every bold anchor except V8 is on its frame.

## Notes and checks

- V2 measures 0.730 s (> 0.43): placed at the GATE fix-5 fallback 1.550 between the beep pairs (needs the lead OK, a SLATE 3.2 deviation); > 0.45 s: retake or accept (lead)
- V1 re-processed at 1.10x (ladder F1)
- V1B re-processed at 1.10x (ladder F1)
- ladder F4: V9 dropped from the VO (BRIEF 6.7; U3F `Saved · har 30 sec` carries it on screen)
- V11 re-processed at 1.10x (ladder F1)
- V8 re-processed at 1.10x (ladder F1)
- V7 re-processed at 1.10x (ladder F1)
- soft window ends dropped to fit: V11, V8, V7
- warning: V2: BOLD end passed by 0.255 s
- warning: V1B: ends 0.397 s after the window
- warning: V7: ends 0.430 s after the window
- warning: V8: ends 0.690 s after the window; BOLD anchor 21.467 outside 20.667-21.333 (+0.134 s)
- warning: hook B: the beep pair 1.333-1.537 is not inside the "..." pause (1.420-1.667)
- warning: A: voice in 28.450-31.350 (power return, the loudest moment): [(27.32, 28.47)]
- warning: B: voice in 28.450-31.350 (power return, the loudest moment): [(27.32, 28.47)]
- Stem checks pass (format, length, loudness, true peak, gaps >= 0.12 s, monotone words, starts on voice, designed silence 16.000-16.400).
- Nukta sounds (आवाज़, ख़ुद) cannot be judged by ASR (whisper folds the nukta): a listener confirms them.

