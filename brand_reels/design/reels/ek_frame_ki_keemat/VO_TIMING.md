# VO_TIMING: Reel 3 · C08 · Ek Frame ki Keemat (Vlad · elevenlabs_v4) · FINAL VO, measured

Date 2026-10-09 07:20 UTC · hinglish-scriptwriter · status **FINAL VO delivered (measured)**; picture anchors that the voice cannot meet are listed in section 4 for the creative-director (retime the picture to the voice) and the lead (optional copy trims). Built by `pipeline/jawad_reels/ek_frame_ki_keemat_vo.py final` (and `final --v10 usey` for the fallback card).

## 1. Deliverables and loudness

| file (`workspace/jawad_reels/ek_frame_ki_keemat/vo/`) | what | dur | LUFS | TP dBTP | first voice | last voice | words |
|---|---|---|---|---|---|---|---|
| `vo_stem.wav` = `ek_frame_ki_keemat_vo.wav` | hook A + body, V10 "usko" (BRIEF build value) | 33.600 s | -16.03 | -2.22 | 0.090 | 32.790 | 61 |
| `ek_frame_ki_keemat_hookb_vo.wav` | hook B, 0-3.000 s (V1B), A-stem gain | 3.000 s | -16.16 | -2.36 | 0.090 | 2.660 | 6 |
| `ek_frame_ki_keemat_vo_usey.wav` (+ `_hookb_vo_usey`) | fallback if the lead keeps the card USSE YEH: V10 "usey" (उसे) | 33.600 s | -16.04 | -2.22 | 0.090 | 33.070 | 61 |

All 48 kHz, 24-bit, mono. Word timings (reel time, `snake_captions.load_words` format + `line`, `i`, `dev`, `heard`, `ok`, `hide`): `words.json` (= `vo_stem.words.json` = `ek_frame_ki_keemat_vo.words.json`), `ek_frame_ki_keemat_hookb_vo.words.json`, `ek_frame_ki_keemat_vo_usey.words.json`. QA image: `vo_timeline.png`. Machine-readable: `final.json`, `final_usey.json`, `cands.json` (every take), `verify.json`, `verify_lines.json`, `credits.json`.

**Total VO (hook A):** 61 words (62 in the script minus the dropped "Dhuaan."), 26.61 s of spoken line spans, first word 0.090 s, last word ends 32.790 s, loop seam (VO-free across 33.6 -> 0) 0.90 s. Hook B: 6 words, 2.53 s, ends 2.630 s.

Checks (all PASS): duration exact, 48 kHz / 24-bit / mono, A -16.0 LUFS (+-0.1), true peak <= -2.0 dBTP, VO onset <= 0.15 s, no voice in 2.70-3.03 s (hook splice), body >= 3.03 s, every voice-to-voice gap >= 0.15 s, last voice <= 33.35 s, words monotone, word count = script tokens - 1. Fails: none.

## 2. Per-beat timing (measured, reel time) vs the brief targets

target on / end limit / hard = `script.json` lines (`start_target`, `end_target`, `hard_end`; V3 / V4 parts: their tag onsets and the next tag). "on" = voiced onset of the first word, "end" = last voiced sample. Speed = pitch-preserving rubberband in `vo_chain`.

| seg | text | beat | target on | on | d on | end limit (hard) | end | d end | dur | words | w/s | syl/s | serif keyword @ |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| V1A | Aap ne ise palak jhapakte dekha. | [0.0] +3 f | 0.10 | 0.100 | +0.00 | 2.37 (2.70) | 2.220 | -0.15 | 2.12 | 6 | 2.83 | 5.66 | palak 1.030 |
| V1B | Ek second. Teen sau saath layers. | [0.0] +3 f | 0.10 | 0.100 | +0.00 | 2.61 (2.70) | 2.630 | +0.02 | 2.53 | 6 | 2.37 | 3.95 | - |
| V2 | Lekin is ek frame mein... 12 layers hain. | [1.1] +2 f | 3.07 | 3.070 | +0.00 | 5.91 (5.95) | 6.650 | **+0.74** | 3.58 | 8 | 2.23 | 3.07 | 12 5.230 |
| V3.0 | Andhera. | [2.3] +6 f | 6.00 | 6.800 | **+0.80** | 6.70 (6.70) | 7.530 | **+0.83** | 0.73 | 1 | 1.37 | 4.11 | - |
| V3.2 | Roshni. | [3.0] +14 f | 7.30 | 7.680 | **+0.38** | 7.85 (7.85) | 8.490 | **+0.64** | 0.81 | 1 | 1.23 | 3.70 | - |
| V3.3 | Chehra. | [3.2] +7 f | 7.90 | 8.640 | **+0.74** | 8.36 (8.45) | 9.270 | **+0.91** | 0.63 | 1 | 1.59 | 4.76 | Chehra 8.640 |
| V4a | Har lafz. | [4.0] +4 f | 10.03 | 9.720 | **-0.31** | 10.90 (10.90) | 10.720 | -0.18 | 1.00 | 2 | 2.00 | 3.00 | - |
| V4b | Har chamak. | [4.2] +2 f | 10.95 | 10.870 | -0.08 | 11.61 (11.70) | 11.900 | +0.29 | 1.03 | 2 | 1.94 | 3.88 | chamak 11.124 |
| V5 | Aur ek layer... jiske bina frame zinda nahi lagta. | [5.0] +2 f | 12.05 | 12.050 | +0.00 | 15.79 (15.85) | 16.050 | +0.26 | 4.00 | 9 | 2.25 | 4.25 | layer 12.820, zinda 14.869 |
| V6 | Ek second mein 30 frames. | [7.0] +4 f | 16.95 | 16.950 | +0.00 | 18.75 (18.85) | 18.830 | +0.08 | 1.88 | 5 | 2.66 | 3.72 | 30 17.960 |
| V7 | Yaani har second... teen sau saath layers. | [7.3] +11 f | 18.90 | 18.980 | +0.08 | 21.99 (21.99) | 22.200 | +0.21 | 3.22 | 7 | 2.17 | 3.42 | - |
| V8 | Aur awaaz ke 3 tracks. | [9.1] +4 f | 22.15 | 22.350 | +0.20 | 24.04 (24.15) | 24.360 | **+0.32** | 2.01 | 5 | 2.49 | 3.48 | awaaz 22.555 |
| V9 | Keemat... banane wala jaanta hai. | [11.0] +10 f | 26.75 | 26.750 | +0.00 | 29.50 (29.85) | 29.160 | -0.34 | 2.41 | 5 | 2.07 | 4.56 | Keemat 26.750 |
| V10 | Jo kehta hai "editing mein kya hai", usko bhejo. | [12.1] +6 f | 29.60 | 29.600 | +0.00 | 33.24 (33.35) | 32.790 | -0.45 | 3.19 | 9 | 2.82 | 5.02 | bhejo 32.376 |

Gaps voice to voice (s): V1A->V2 0.85, V2->V3.0 0.15, V3.0->V3.2 0.15, V3.2->V3.3 0.15, V3.3->V4a 0.45, V4a->V4b 0.15, V4b->V5 0.15, V5->V6 0.90, V6->V7 0.15, V7->V8 0.15, V8->V9 2.39, V9->V10 0.44.

## 3. Picture anchors (measured word onsets vs the brief)

| anchor | brief t (tol) | measured | d | picture event |
|---|---|---|---|---|
| V2 "12" | 4.80 (+-0.10) | 5.230 | **+0.43** | "12" counter lands, side-on stack (f144, L3 push) |
| V5 "layer..." | 12.45 (+-0.20) | 12.820 | **+0.37** | caption C1 *layer...* on the pane-12 stop |
| V5 "bina" | 13.80 (+-0.15) | 14.051 | +0.25 | flick OFF f414 on "bina" |
| V5 "zinda" | 14.45 (+-0.20) | 14.869 | **+0.42** | flick ON f432 on "zinda" |
| V7 "teen" | 20.45 (+-0.10) | 20.590 | +0.14 | counter 360 lands 20.4 (glass_truth, L3 push 0.5) |
| V9 "Keemat..." | 26.75 (+-0.05) | 26.750 | +0.00 | "Keemat" >= 0.30 s after the 26.4 hit; keyword glyphs rise from 26.62 |
| V9 "banane" | 27.70 (+-0.10) | 27.710 | +0.01 | sub "banane wala jaanta hai" rises 27.7; JD glint 28.2 |
| V10 "bhejo." | 29.75 (+-2.00) | 32.376 | +2.63 | card title from 29.75; "bhejo" inside the card (settled 31.25-33.24) |

## 4. Beats that miss their targets by more than 0.3 s, and the fix

Cause (measured, not a take defect): Vlad reads these short dramatic lines slower than the syllable model the script and brief were timed with. Measured line spans after the stretch vs the script estimates: V2 3.58 vs 2.77 s, V5 4.00 vs 3.65, V6 1.88 vs 1.24, V7 3.22 vs 2.62, V8 2.01 vs 1.24; the V3 words run 0.63-0.81 s each (est 0.46-0.69), the V4 phrases 1.00 / 1.03 s (est ~0.6). The tight lines were rendered 2-3 times each (single-line takes, the running-context takes T1 / T2 / T3, comma variants); renderings differ by 1-18 % and the fastest clean one is used (V4 excepted: its 18 % faster T2 rendering says "lavz"), so a retake does not buy the time back. Inside the binding rules (speed <= 1.10x, no pitch change, holds >= 0.25 s on "...", >= 0.15 s between sentences, hook <= 2.70 s, body >= 3.03 s, V5 on the 12.05 stop, V10 inside the card) the 3.07-11.90 block needs 8.53 s of voice plus minimum gaps for 8.83 s: it runs with 0.15 s gaps and "Dhuaan." dropped (SCRIPT section 7 zero-credit ladder step; tag 02 still shows the word), V4 is pinned back from the V5 stop, and the picture anchors in 4.8-11.0 slip. The 12.05-24.15 block lands within 0.32 s; the payoff and CTA land on their marks.

Misses > 0.3 s (measured): V2 ends 6.650 vs 5.91 (+0.74 s; hard 5.95); V3.0 onset 6.800 vs 6.00 (+0.80 s); V3.0 ends 7.530 vs 6.70 (+0.83 s; hard 6.70); V3.2 onset 7.680 vs 7.30 (+0.38 s); V3.2 ends 8.490 vs 7.85 (+0.64 s; hard 7.85); V3.3 onset 8.640 vs 7.90 (+0.74 s); V3.3 ends 9.270 vs 8.36 (+0.91 s; hard 8.45); V4a onset 9.720 vs 10.03 (-0.31 s); V8 ends 24.360 vs 24.04 (+0.32 s; hard 24.15); anchor V2 "12" 5.230 vs 4.80 (+0.43 s): "12" counter lands, side-on stack (f144, L3 push); anchor V5 "layer..." 12.820 vs 12.45 (+0.37 s): caption C1 *layer...* on the pane-12 stop; anchor V5 "zinda" 14.869 vs 14.45 (+0.42 s): flick ON f432 on "zinda".

**Recommended fix: the picture follows the voice** (creative-director; timelines are on placeholders, the VO is final). Move these events to the measured word onsets:

| event (BRIEF) | brief | move to (VO) | frame |
|---|---|---|---|
| side-on stack lands + counter `12` settles + L3 push 0.3 (`glass_truth` at 4.8) | 4.80 | 5.230 | f157 |
| tag 01 `andhera` | 6.00 | 6.800 | f204 |
| tag 02 `dhuaan` (no VO word now; keep it between 01 and 03) | 6.75 | between 6.80 and 7.68 (e.g. 7.25) | f217 |
| tag 03 `roshni` | 7.30 | 7.680 | f230 |
| tag 04 `chehra` (JD face pane) | 7.90 | 8.640 | f259 |
| tag 08 `lafz` (caps words) | 10.03 | 9.720 | f292 |
| tags 09/10 `chamak` (keyword core + halo) | 10.95 | 10.870 | f326 |
| flick OFF on "bina" (f414) | 13.80 | 14.051 | f422 |
| flick ON on "zinda" (f432) | 14.45 | 14.869 | f446 |
| counter 360 lands (20.4; inside the 0.3 s rule but outside +-0.10) | 20.40 | 20.590 | f618 |

Tags 05-07 (silent) then sit in 9.27-9.72 s, where the VO pauses 0.45 s. V8 ends 24.360 s, 0.21 s past its hard 24.15 and 0.24 s before the riser (24.6). If the picture cannot move, the zero-credit alternatives all need the lead (copy): `V2-brief` "Is frame mein... baarah layers hain." (one 0.23-credit take; saves about 0.5 s in 3.07-6.65) and/or dropping "Andhera." as well.

## 5. CER per line

Metric = the casting metric (`vo_config` cer_whisper_small_hi): faster-whisper int8, language `hi`, **no prompt**, beam 5, audio decoded by ffmpeg to 16 kHz numpy (no PyAV path); nukta, chandrabindu, punctuation and spaces folded; digits and Latin loanwords mapped to the DEV spelling (module `cer()` / `devify()`). "final" = the line cut from the FINAL stem; "take" = the chosen take's 1.08x pass; "others" = best CER of the other takes of the line. "norm" = final small CER after also folding whisper's Devanagari spellings of the English loanwords (सेकिंड/सेकिन्ट/सेकिन/सेकंट -> सेकंड, लेर्ज/लेयर्ज/लेएर्ज/लेयाज/लेज -> लेयर्स, तींसो/तीन्सो -> तीन सौ, सो -> सौ, एदिटिंग -> एडिटिंग, तींट्रैक्स -> तीन ट्रैक्स); the number word साठ is never folded.

| line | take (source, speed) | final small | final medium | norm | take small / best | others best | heard (final, small / medium) | verdict |
|---|---|---|---|---|---|---|---|---|
| V1A | `efk_V1A_t1.mp3` (single-line take, 1.08x) | 0.143 | 0.071 | 0.143 | 0.143 / 0.071 | 0.071 | आपने इसे पलक जबकते देखा / आपने इसे पलक जपकते देखा। | ok |
| V1B | `efk_V1B_t2.mp3` (single-line retake, 1.10x) | 0.500 | 0.286 | 0.071 | 0.571 / 0.286 | 0.143, 0.214, 0.214 | एक सेकिन्ट, तींसो साथ लेज / एक सेकिंड तींसो साथ लेएर्ज। | ASR loanword spelling (see norm; 4 takes measured) |
| V2 | `efk_V2_t1.mp3` (single-line take, 1.10x) | 0.105 | 0.105 | 0.000 | 0.105 / 0.105 | 0.158 | लिकिन इस एक फ्रेम में, बारह लेर्ज है। / लेकिन इस एक फ्रेम में बारह लेर्ज हैं। | ok |
| V3 | `efk_V3_t2.wav` (cut from running take T2, 1.10x) | 0.111 | 0.111 | 0.111 | 0.273 / 0.182 | 0.273, 0.182 | अंदेरा रोशनी चहरा / अन्धेरा रोश्नी चहरा | ok |
| V4 | `efk_V4_t1.mp3` (single-line take, 1.10x) | 0.100 | 0.200 | 0.100 | 0.000 / 0.000 | 0.100, 0.200 | हर लाफ़, हर चमक / हर लफ़, हर जमक | ok |
| V5 | `efk_V5_t2.wav` (cut from running take T1, 1.10x) | 0.091 | 0.045 | 0.091 | 0.045 / 0.045 | 0.091 | और एक लेयर, जिसके बिना फ्रेम जिन्दा नहीं लकता. / और एक लैयर, जिसके बिना फ्रेम जिन्दा नहीं लगता। | ok |
| V6 | `efk_V6_t2.wav` (cut from running take T1, 1.10x) | 0.167 | 0.167 | 0.083 | 0.083 / 0.083 | 0.167 | एक सेकिन में, तीस व्रेम्स / एक सेकिन्ट में 30 फ्रेम्स | ASR loanword spelling (see norm; 2 takes measured) |
| V7 | `efk_V7_t2.wav` (cut from running take T1, 1.10x) | 0.312 | 0.125 | 0.125 | 0.188 / 0.125 | 0.125 | यानी हर सेकिन्ट, तीन सो सार्ट लेयर्ज / यानी हर सेकंड तीन सो साथ लेयर्ज। | ok |
| V8 | `efk_V8_t2.wav` (cut from running take T1, 1.10x) | 0.083 | 0.000 | 0.000 | 0.083 / 0.083 | 0.083 | और आवाज के तींट्रैक्स / और आवाज के तीन ट्रैक्स। | ok |
| V9 | `efk_V9_t2.wav` (cut from running take T3, 1.08x) | 0.000 | 0.000 | 0.000 | 0.000 / 0.000 | 0.000 | कीमत बनाने वाला जानता है / कीमत बनाने वाला जानता है। | ok |
| V10 | `efk_V10_t2.wav` (cut from running take T3, 1.08x) | 0.056 | 0.000 | 0.000 | 0.056 / 0.056 | 0.056 | जो कहता है, एदिटिंग में क्या है, उसको भेजो. / जो कहता है एडिटिंग में क्या है उसको भेजो | ok |

V3 is scored against "अंधेरा। रोशनी। चेहरा।" (the stem has no "Dhuaan."). Lines whose best final CER is above 0.15: V6 (0.167), V1B (0.286). V1B was re-taken twice more for this (t3 default, t4 stability 0.55: best 0.214 / 0.214 vs t1 0.143, t2 0.286); all four takes give the same whisper spellings of "second" and "layers", so the CER is an ASR transliteration effect, not the take; t2 is kept (it fits the 2.70 s hook end with 0.07 s to spare and its isolated "teen sau saath" reads "360" in whisper medium). V6: the "second" spelling plus small's "व्रेम्स" for फ़्रेम्स (medium hears फ्रेम्स; the /f/ is visible on the spectrogram of the same T1 take in V5).

Word timing cross-check (independent): every line re-aligned on its own window of the final stem (whisper small, DEV prompt, snapped) vs `words.json`: 61 words, median 0.010 s, mean 0.026 s, 2 words over 0.1 s: V5 "jiske" (realign 13.204 vs 13.640) and V9 "banane" (27.240 vs 27.710); in both whisper glues the word across a real pause (spectrograms `asr/spec_stem_V5.png`, `asr/spec_V9.png` show the voice resuming at 13.64 / 27.71), so `words.json` keeps the voiced onsets. Hook B: 6/6, max 0.014 s.

## 6. Pronunciation (SCRIPT section 8 risks): carriers P1-P4, then the line takes

| word | verdict | evidence |
|---|---|---|
| साठ saath (V1B, V7) | OK: 60, never 7 | never heard as सात in P1, 4 V1B takes, 2 V7 takes; the number cut out alone: whisper medium "360" (P1, V1B t2, V1B t4, V7 t2), small "सार्ट" (retroflex) every time |
| फ़्रेम / फ़्रेम्स (V2, V5, V6) | OK, spelling kept | ASR फ्रेम/फ्रेम्स in every line; spectrograms show a 150-170 ms /f/ frication with no stop closure (P1, V2, V5); fallback फ्रेम (no nukta) not needed |
| ज़िंदा zinda (V5) | OK | continuous voiced /z/ frication ~150 ms, no closure, vs the affricate in "bhejo" (P2, P4, V5 spectrograms); ASR writes जिन्दा (whisper drops nuktas) |
| झपकते jhapakte (V1A) | LISTEN | whisper (small and medium) writes जपकते/जबकते in P2, V1A t1 and V1A t2: the breathy release is weak; affricate release + frication present. A retake would read the same (3 renderings). The script fallback "Aap ne ise ek pal mein dekha." needs the lead |
| क़ीमत keemat (V9) | OK | कीमत in every pass; released t + a "..." breath, then 0.21 s silence before "banane" |
| लेयर / लेयर्स | OK (English "layers") | heard लेर्ज/लेयर्ज: the English diphthong + z, not an extra vowel |
| लफ़्ज़ lafz (V4) | OK, LISTEN | take t1 (used): small "लफज" on its 1.08x pass; on the final stem small "लाफ़" / medium "लफ़" (final z soft); the T2-context take t2 was rejected ("लव्ज") |
| चमक chamak (V4 keyword) | OK, LISTEN | small "चमक" (take pass and final stem); final-stem medium "जमक"; spectrogram: 50 ms voiceless affricate frication after the release (unlike the short /dʒ/ in "bhejo"); the comma variant t3 was rejected ("जमग") |
| ट्रैक्स, आवाज़, एडिटिंग, उसको | OK | V8 t2 "आवाज" (t1 "अवास" rejected), medium "ट्रैक्स"; medium "एडिटिंग"; "उसको"/"उसे" clean |
| धुआँ dhuaan (V3) | dropped | whisper heard "दूमा/दुमा/दुआ" in all three V3 renderings; dropped anyway by the V3 fit ladder (tag 02 carries it) |

No spelling change was needed (`spelling_fixes` empty). Three words carry a LISTEN flag (jhapakte, lafz, chamak): ASR cannot judge aspiration or a final voiced fricative; they need one human listen before the master.

## 7. Takes, processing, credits

- Voice: Higgsfield preset Vlad `e5666b9c-99a2-4fac-8b4e-abee078b186d`, `elevenlabs_v4`, Devanagari exactly as `script.json` (provider defaults; stability 0.55 only on V1B t4). Raw takes: `vo/raw/efk_<id>_t<n>.mp3` (+ the per-line cuts `efk_<line>_t2.wav` of the running takes T1-T3, cut in their 0.34-0.53 s inter-line silences).
- Chosen: V1A `efk_V1A_t1.mp3` 1.08x, V1B `efk_V1B_t2.mp3` 1.10x, V2 `efk_V2_t1.mp3` 1.10x, V3 `efk_V3_t2.wav` 1.10x, V4 `efk_V4_t1.mp3` 1.10x, V5 `efk_V5_t2.wav` 1.10x, V6 `efk_V6_t2.wav` 1.10x, V7 `efk_V7_t2.wav` 1.10x, V8 `efk_V8_t2.wav` 1.10x, V9 `efk_V9_t2.wav` 1.08x, V10 `efk_V10_t2.wav` 1.08x.
- `vo_chain.process` (trim to 40 ms, pauses <= 0.45 s / dramatic 0.9 s, rubberband 1.08x or 1.10x formant-preserved, HPF 70 Hz, de-ess, 2.5:1 compression, -16 LUFS) per take; then per line: word edges fixed against the real silences (`fix_gap_words`, shared request R6), lead-in / tail after the last voice cut (V10 t2 ended on a -22 dBFS click 0.17 s after "bhejo"), 5 ms / 20 ms edge fades, pause caps (V5 "layer..." 0.31 -> 0.25 s, V6 "mein" 0.20 -> 0.12 s, V7 "second..." 0.27 -> 0.25 s), each line re-levelled to -16 LUFS, placed, stem gain +0.20 dB with a 3 ms look-ahead limiter at -2.5 dBFS (it engages on the boosted lines: V1A +3.1 dB, V8 +1.4 dB).
- Credits (own spend, sum of the get_cost preflights of the 25 submitted jobs, 0.23 per started 50 characters): **7.13 of 25** (carriers 1.38, line takes 2.76, running takes + variants 2.53, V1B retakes 0.46). Account balance 6978.56 at the start, 6926.35 at the end (the difference includes the owner's and the other reels' work); the 6800 guard was never reached.

## 8. Open items for the lead

1. C7 / fix 5: the stem uses V10 "usko" (BRIEF build value). If the card stays `USSE YEH`, swap in `ek_frame_ki_keemat_vo_usey.wav` + its words (V10 "usey" ends 33.050 s, still inside the card) - no new credits.
2. Picture retime list in section 4 (creative-director), or approve `V2-brief` (0.23 credits) to buy back ~0.5 s in 3-7 s.
3. One listen for jhapakte / lafz / chamak (section 6).
4. AI disclosure stays on the defaults (synthetic voice).
