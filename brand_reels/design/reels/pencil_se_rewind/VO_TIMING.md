# VO_TIMING · Pencil Se Rewind (@jawad_mp4)

2026-10-11, sound-designer + music-supervisor, `pipeline/jawad_reels/pencil_se_rewind_vo.py assemble` (measured). Voice: Higgsfield preset Vlad, `elevenlabs_v4`, the paid takes in `brand_reels/assets/pencil_se_rewind/vo_raw/` (none regenerated). Chain `vo_chain.py` per vo_config: trim to 40 ms, pauses capped 0.45 s (0.9 s after the dramatic beats V1 "button?" and V11 "tool?"), rubberband 1.06-1.10x (formant preserved; the gentlest speed that fits its slot), HPF 70 Hz, de-ess, 2.5:1 compression, loudnorm -16 LUFS / -2 dBTP; word timings faster-whisper small (DEV prompt) aligned to the DEV tokens, snapped to the voiced onsets. LEAD_DECISIONS 3: picture beats move to the VO (section 3).

- **Stem A** `workspace/jawad_reels/pencil_se_rewind/vo/vo_stem.wav`: 1638400 samples (34.133 s) at 48000 Hz, -16.00 LUFS integrated, -2.20 dBTP, LRA 4.3 LU, VO 0.090-33.170 s, 24.02 s voiced, 60 words (14 keywords), 100 % of word starts on voice; gain +1.60 dB, limiter on.
- **Stem B** `workspace/jawad_reels/pencil_se_rewind/vo/vo_stem_B.wav`: 1638400 samples (34.133 s) at 48000 Hz, -16.00 LUFS integrated, -2.20 dBTP, LRA 4.3 LU, VO 0.480-33.170 s, 23.75 s voiced, 59 words (14 keywords), 100 % of word starts on voice; gain +1.50 dB, limiter on.
- Words: `workspace/jawad_reels/pencil_se_rewind/vo/words.json` (A) / `words_B.json` (B), reel time, snake_captions format (+ line, i, dev, heard, ok, start_f, end_f). Copies (FLAC 24-bit + json): `brand_reels/assets/pencil_se_rewind/vo_final/pencil_se_rewind_vo_{A,B}.flac` / `.words.json`.
- Minimum gap between lines: 0.120 s (rule >= 0.12 s).

## 1. Line timing (hook A order; V1B = hook B only)

| line | take | speed | start → end (s) | frames | planned f | Δ f | words (reel s) | CER | aligned |
|---|---|---|---|---|---|---|---|---|---|
| V1 | `V01_t2.mp3` | 1.08 | 0.100 → 2.060 | f3.0-f61.8 | f3 | +0.0 | Rewind 0.09 button? 0.72 **Pencil.** 1.54 | 0.000 | 3/3 |
| V1B | `V01B_t1.mp3` | 1.06 | 0.484 → 1.744 | f14.5-f52.3 | f3 | +11.5 | Battery 0.49 **khatam?** 1.07 | 0.167 | 2/2 |
| V2 | `V02_t1.mp3` | 1.06 | 2.333 → 6.203 | f70.0-f186.1 | f70 | +0.0 | Walkman 2.34 ki 2.91 **battery** 3.10 bachani 3.53 thi, 3.98 toh 4.72 pencil 4.85 se 5.28 **ghumate** 5.45 the. 5.89 | 0.000 | 10/10 |
| V3 | `V03_t1.mp3` | 1.06 | 6.600 → 9.090 | f198.0-f272.7 | f198 | +0.0 | **Gaana** 6.60 dhoondna 7.04 ho? 7.38 Sirf 8.01 **andaza.** 8.44 | 0.167 | 5/5 |
| V4 | `V04_t1.mp3` | 1.10 | 10.667 → 13.037 | f320.0-f391.1 | f320 | +0.0 | Play. 10.67 **Galat!** 11.58 Phir 12.54 se. 12.72 | 0.125 | 4/4 |
| V5 | `V05_t1.mp3` | 1.06 | 13.167 → 15.187 | f395.0-f455.6 | f386 | +9.0 | **Mil** 13.17 gaya! 13.50 Aur 14.36 phir... 14.62 | 0.000 | 4/4 |
| V6 | `V06_t1.mp3` | 1.08 | 15.533 → 16.843 | f466.0-f505.3 | f466 | +0.0 | Cassette 15.55 **phans** 15.96 gayi! 16.36 | 0.000 | 3/3 |
| V7 | `V07_t1.mp3` | 1.10 | 16.967 → 19.677 | f509.0-f590.3 | f516 | -7.0 | Saans 16.97 rok 17.45 ke, 17.74 **pencil** 18.45 se 18.83 wapas. 19.03 | 0.167 | 6/6 |
| V8 | `V08_t1.mp3` | 1.06 | 19.800 → 21.600 | f594.0-f648.0 | f590 | +4.0 | Aaj 19.83 bhi 20.17 **wahi** 20.41 karte 20.79 hain. 21.20 | 0.000 | 5/5 |
| V10 | `V10_t1.mp3` | 1.08 | 23.267 → 24.997 | f698.0-f749.9 | f708 | -10.0 | Bas 23.28 tool 23.64 **badal** 24.16 gaya. 24.48 | 0.000 | 4/4 |
| V11 | `V11_t1.mp3` | 1.10 | 25.933 → 28.283 | f778.0-f848.5 | f770 | +8.0 | Pehla 25.92 editing 26.39 tool? 27.04 **Pencil.** 27.75 | 0.250 | 4/4 |
| V12 | `V12_t1.mp3` | 1.06 | 28.403 → 30.553 | f852.1-f916.6 | f818 | +34.1 | Scrubbing 28.42 toh 28.98 **cassette** 29.28 pe 29.75 sikhi 29.88 thi. 30.20 | 0.000 | 6/6 |
| V13 | `V13_t1.mp3` | 1.06 | 31.000 → 33.150 | f930.0-f994.5 | f930 | +0.0 | Aap 31.01 ki 31.28 pehli 31.75 **cassette** 32.07 kaunsi 32.41 thi? 32.85 | 0.000 | 6/6 |

## 2. Word frames (stem A; f = reel frame of the word onset, 30 fps)

| line | word | start s | end s | start f | end f | keyword | heard |
|---|---|---|---|---|---|---|---|
| V1 | Rewind | 0.090 | 0.717 | 2.7 | 21.5 |  | रिवाइंड |
| V1 | button? | 0.717 | 0.995 | 21.5 | 29.9 |  | बटन? |
| V1 | Pencil. | 1.540 | 2.060 | 46.2 | 61.8 | yes | पेंसिल। |
| V1B | Battery | 0.494 | 1.067 | 14.8 | 32.0 |  | बैटरी |
| V1B | khatam? | 1.067 | 1.557 | 32.0 | 46.7 | yes | ख़त्म? |
| V2 | Walkman | 2.343 | 2.907 | 70.3 | 87.2 |  | वॉकमैन |
| V2 | ki | 2.907 | 3.095 | 87.2 | 92.9 |  | की |
| V2 | battery | 3.095 | 3.529 | 92.9 | 105.9 | yes | बैटरी |
| V2 | bachani | 3.529 | 3.982 | 105.9 | 119.5 |  | बचानी |
| V2 | thi, | 3.982 | 4.246 | 119.5 | 127.4 |  | थी, |
| V2 | toh | 4.723 | 4.850 | 141.7 | 145.5 |  | तो |
| V2 | pencil | 4.850 | 5.284 | 145.5 | 158.5 |  | पेंसिल |
| V2 | se | 5.284 | 5.454 | 158.5 | 163.6 |  | से |
| V2 | ghumate | 5.454 | 5.888 | 163.6 | 176.7 | yes | घुमाते |
| V2 | the. | 5.888 | 6.183 | 176.7 | 185.5 |  | थे। |
| V3 | Gaana | 6.600 | 7.042 | 198.0 | 211.3 | yes | गाना |
| V3 | dhoondna | 7.042 | 7.381 | 211.3 | 221.4 |  | डून्ना |
| V3 | ho? | 7.381 | 7.589 | 221.4 | 227.7 |  | हो? |
| V3 | Sirf | 8.010 | 8.438 | 240.3 | 253.1 |  | सिर्फ |
| V3 | andaza. | 8.438 | 8.985 | 253.1 | 269.5 | yes | अंदाज़ा? |
| V4 | Play. | 10.667 | 11.257 | 320.0 | 337.7 |  | प्ले। |
| V4 | Galat! | 11.577 | 12.083 | 347.3 | 362.5 | yes | ग़लत! |
| V4 | Phir | 12.537 | 12.720 | 376.1 | 381.6 |  | पिर |
| V4 | se. | 12.720 | 13.038 | 381.6 | 391.1 |  | से। |
| V5 | Mil | 13.167 | 13.504 | 395.0 | 405.1 | yes | मिल |
| V5 | gaya! | 13.504 | 14.077 | 405.1 | 422.3 |  | गया! |
| V5 | Aur | 14.357 | 14.618 | 430.7 | 438.5 |  | और |
| V5 | phir... | 14.618 | 15.184 | 438.5 | 455.5 |  | पिर... |
| V6 | Cassette | 15.553 | 15.957 | 466.6 | 478.7 |  | कैसेट |
| V6 | phans | 15.957 | 16.365 | 478.7 | 491.0 | yes | फँस |
| V6 | gayi! | 16.365 | 16.661 | 491.0 | 499.8 |  | गई! |
| V7 | Saans | 16.967 | 17.445 | 509.0 | 523.3 |  | साँस |
| V7 | rok | 17.445 | 17.736 | 523.3 | 532.1 |  | रोक |
| V7 | ke, | 17.736 | 18.117 | 532.1 | 543.5 |  | के, |
| V7 | pencil | 18.447 | 18.827 | 553.4 | 564.8 | yes | पेंसिल |
| V7 | se | 18.827 | 19.027 | 564.8 | 570.8 |  | से |
| V7 | wapas. | 19.027 | 19.691 | 570.8 | 590.7 |  | वापस। |
| V8 | Aaj | 19.830 | 20.167 | 594.9 | 605.0 |  | आज |
| V8 | bhi | 20.167 | 20.412 | 605.0 | 612.4 |  | भी |
| V8 | wahi | 20.412 | 20.789 | 612.4 | 623.7 | yes | वही |
| V8 | karte | 20.789 | 21.205 | 623.7 | 636.2 |  | करते |
| V8 | hain. | 21.205 | 21.400 | 636.2 | 642.0 |  | हैं। |
| V10 | Bas | 23.277 | 23.644 | 698.3 | 709.3 |  | बस |
| V10 | tool | 23.644 | 24.163 | 709.3 | 724.9 |  | टूल |
| V10 | badal | 24.163 | 24.478 | 724.9 | 734.3 | yes | बदल |
| V10 | gaya. | 24.478 | 24.793 | 734.3 | 743.8 |  | गया |
| V11 | Pehla | 25.923 | 26.385 | 777.7 | 791.6 |  | पहला |
| V11 | editing | 26.385 | 27.039 | 791.6 | 811.2 |  | एडिटिंग |
| V11 | tool? | 27.039 | 27.294 | 811.2 | 818.8 |  | टूल? |
| V11 | Pencil. | 27.753 | 28.312 | 832.6 | 849.4 | yes | पेंसिल। |
| V12 | Scrubbing | 28.423 | 28.977 | 852.7 | 869.3 |  | स्क्रबिंग |
| V12 | toh | 28.977 | 29.279 | 869.3 | 878.4 |  | तो |
| V12 | cassette | 29.279 | 29.750 | 878.4 | 892.5 | yes | कैसेट |
| V12 | pe | 29.750 | 29.882 | 892.5 | 896.5 |  | पे |
| V12 | sikhi | 29.882 | 30.203 | 896.5 | 906.1 |  | सीखी |
| V12 | thi. | 30.203 | 30.483 | 906.1 | 914.5 |  | थी। |
| V13 | Aap | 31.010 | 31.282 | 930.3 | 938.5 |  | आप |
| V13 | ki | 31.282 | 31.600 | 938.5 | 948.0 |  | की |
| V13 | pehli | 31.750 | 32.074 | 952.5 | 962.2 |  | पहली |
| V13 | cassette | 32.074 | 32.414 | 962.2 | 972.4 | yes | कैसेट |
| V13 | kaunsi | 32.414 | 32.848 | 972.4 | 985.4 |  | कौनसी |
| V13 | thi? | 32.848 | 33.055 | 985.4 | 991.6 |  | थी? |

## 3. Picture beats that move to the VO (proposed frames for the motion designer)

LEAD_DECISIONS 3: the picture follows the measured VO. Proposed frame = the onset frame of the VO word (rounded down, so the visual leads the word by at most 1 frame). |Δ| <= 2 f: keep the planned frame.

| line | word | event (SHOTS / SCRIPT) | planned f | VO onset f | proposed f | Δ f |
|---|---|---|---|---|---|---|
| V1 | Pencil. | `Pencil.` slam (HA key) | f16 | 46.2 | **f46** | +30 |
| V1B | khatam? | `khatam?` slam (HB key) | f32 | 32.0 | **f32** | +0 |
| V2 | Walkman | L2 snake in | f70 | 70.3 | **f70** | +0 |
| V2 | toh | L3 snake in ("toh") | f134 | 141.7 | **f141** | +7 |
| V3 | Gaana | L4 snake in | f198 | 198.0 | **f198** | +0 |
| V3 | Sirf | L5 `SIRF` in | f262 | 240.3 | **f240** | -22 |
| V3 | andaza. | `andaza.` glyph rise | f268 | 253.1 | **f253** | -15 |
| V4 | Play. | PLAY key + `Play.` slam | f320 | 320.0 | **f320** | +0 |
| V4 | Galat! | `Galat!` slam + STOP key (STOP was f336) | f328 | 347.3 | **f347** | +19 |
| V4 | Phir | `Phir se.` slam + REW key + motor (REW was f340) | f336 | 376.1 | **f376** | +40 |
| V5 | Mil | 2nd PLAY key + cut to S7 + `Mil gaya!` slam | f384 | 395.0 | **f395** | +11 |
| V5 | Aur | L8 `Aur phir...` in | f420 | 430.7 | **f430** | +10 |
| V6 | Cassette | `CASSETTE` rise | f448 | 466.6 | **f448** (stays) | +0 |
| V6 | phans | `phans gayi!` SLAM + D7 (re-hook) | f464 | 478.7 | **f464** (stays) | +0 |
| V7 | Saans | L10 snake in | f514 | 509.0 | **f509** | -5 |
| V8 | Aaj | L11 snake in | f588 | 594.9 | **f594** | +6 |
| V10 | Bas | L13 snake in | f706 | 698.3 | **f698** | -8 |
| V11 | Pehla | L14 caps (payoff hit f768) | f768 | 777.7 | **f768** (stays) | +0 |
| V11 | Pencil. | pencil snaps to the cut + `Pencil.` key rise | f800 | 832.6 | **f832** | +32 |
| V12 | Scrubbing | L15 tag in | f816 | 852.7 | **f852** | +36 |
| V12 | cassette | `cassette` inline key | f816 | 878.4 | **f878** | +62 |
| V13 | Aap | outro question text lands (card f896 + t_q 1.3 s) | f935 | 930.3 | **f935** (stays) | +0 |

Structure that does NOT move: f64 splice, f256 D8, f320 PLAY key, f448 eat, f464 re-hook slam, f576 reveal, f752-f767 drop-out, f768 payoff, f896 D2 razor + profile outro (128 f). Moves inside shots (all on the measured VO; the sound files already follow them): HA `Pencil.` slam f16 -> f43/f46; S6 STOP key f336 -> f347 (on "Galat!", music wrong-spot snippet f322-f346), REW key + motor f340 -> f376 (on "Phir se."), 2nd PLAY key + cut to S7 f384 -> f392, `Mil gaya!` slam f395; L8 f420 -> f430; S11 scrub jumps one 8th later f648 / f656 / f664 / f672 (CUT marker f672; V8 "hain." ends f648; music stutters follow); S13 pencil snap + `Pencil.` key f800 -> the V11 "Pencil." onset; L15 tag f816 -> the V12 onset, held to the V12 end (across the razor; the outro question lands f935 and V13 reads it from f930); `Pencil.` slam f43 (0.1 s before the word, so the word keeps 8 LU over the hit). V9 is not in the VO (ladder F4): L12 `Peeche. Aage. Peeche. Yahan.` stays text-led on the scrub jumps.

## 4. Takes (CER = faster-whisper small, no prompt, on the processed line vs the DEV text; nukta / candrabindu folded, Latin loan words mapped)

| line | take | mean CER (1.06/1.08/1.10) | span @1.08 s | heard @ placed speed | chosen |
|---|---|---|---|---|---|
| V1 | `V01_t1.mp3` | 0.100 | 1.970 | रिवाईद बाटन वेन्सल / रिवाइंट बटन? पेंसल? |  |
| V1 | `V01_t2.mp3` | 0.067 | 1.960 | रीवाईद बाटन पेन्सल / रिवाइंड बटन? पेंसल? | yes |
| V1B | `V01B_t1.mp3` | 0.167 | 1.240 | बाटरी हतन? / बैटरी खतन। | yes |
| V2 | `V02_t1.mp3` | 0.000 | 3.800 | वोख में की बाट्री बचानी ती तो पेंसल से गूमाते ते / Walkman की battery बचानी थी तो pencil से घूमाते थे। | yes |
| V2 | `V02_t2.mp3` | 0.032 | 3.820 | वाख में की बाट्री बचानी थी तो पेंसल से गूमाते ते / Walkman की बैटरी बचानी थी तो pencil से गुमाते थे। |  |
| V3 | `V03_t1.mp3` | 0.139 | 2.450 | गाना दून्ना हो, सिर्फ अंदाजा? / गाना ढूँनना हो, सिर्फ अन्दाजा! | yes |
| V4 | `V04_t1.mp3` | 0.167 | 2.410 | प्ले गलत पिर्से / प्ले घलत फिर से | yes |
| V5 | `V05_t1.mp3` | 0.042 | 1.980 | मिल्गा और पिर / मिल गया और फिर। | yes |
| V6 | `V06_t1.mp3` | 0.000 | 1.310 | के सेट फ़स गयी / कैसेट फस गई | yes |
| V7 | `V07_t1.mp3` | 0.083 | 2.760 | सास रोके पेंसल से वाबस / सास रोग के पेंसल से वाबस | yes |
| V8 | `V08_t1.mp3` | 0.000 | 1.760 | आज भी वही करते हैं / आज भी वही करते हैं। | yes |
| V9 | `V09_t1.mp3` | 0.167 | 2.670 | बीचे आगे यहाँ / पीचे आगे यहां | dropped (F4) |
| V10 | `V10_t1.mp3` | 0.000 | 1.730 | बस तूल बदल गया / बस टूल बदल गया। | yes |
| V11 | `V11_t1.mp3` | 0.139 | 2.400 | वहला एदिटिंक तूल, वेन्सल / वहला अइडिटिंग टूल, पेंसिल | yes |
| V12 | `V12_t1.mp3` | 0.077 | 2.110 | श्क्रोबिंग तो क्यासेट पे सीखी ती / स्क्रबिंग तो कैसेट पे सीखी थी. | yes |
| V13 | `V13_t1.mp3` | 0.000 | 2.110 | अपकी बहली कसेट कोन सी ती / आपकी पहली कसेट कौनसी थी? | yes |

## 5. Notes

- V11: runs 0.003 s into the next line's planned start; V12 moves later
- ladder F4: V9 dropped from the VO (S11 scrub (L12): DROPPED, ladder F4 (captions + scrub SFX carry it)); best take `V09_t1.mp3` processed and kept in proc/
- Rebuild: `cd pipeline/jawad_reels && tools/heavy.sh python3 pencil_se_rewind_vo.py process && tools/heavy.sh python3 pencil_se_rewind_vo.py assemble` (deterministic; the PLAN table at the top of the module holds the slots).
