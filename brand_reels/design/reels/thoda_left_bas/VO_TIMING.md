# VO_TIMING · Thoda Left... Bas Bas! (@jawad_mp4)

2026-10-11, sound-designer + music-supervisor, `pipeline/jawad_reels/thoda_left_bas_vo.py assemble` (measured). Voice: Higgsfield preset Vlad, `elevenlabs_v4`, the paid takes in `brand_reels/assets/thoda_left_bas/vo_raw/` (none regenerated, no paid call). Chain `vo_chain.py` per vo_config: trim to 40 ms, internal pauses capped per line (shouts 0.12-0.30 s, speech 0.45 s; table in section 4), rubberband 1.06-1.10x (formant preserved; the gentlest speed that fits its slot), HPF 70 Hz, de-ess, 2.5:1 compression, loudnorm -16 LUFS / -2 dBTP; word timings faster-whisper small (DEV prompt, numpy input) aligned to the DEV tokens, snapped to the voiced onsets. LEAD_DECISIONS 3: picture beats move to the VO (section 3).

- **Stem A** `workspace/jawad_reels/thoda_left_bas/vo/vo_stem.wav`: 1728000 samples (36.000 s) at 48000 Hz, -16.00 LUFS integrated, -2.10 dBTP, LRA 4.4 LU, VO 0.070-35.130 s, 26.93 s voiced, 61 words (12 keywords), 100 % of word starts on voice; gain +0.90 dB, limiter on; lines V1-V15.
- **Stem B** `workspace/jawad_reels/thoda_left_bas/vo/vo_stem_B.wav`: 1728000 samples (36.000 s) at 48000 Hz, -16.00 LUFS integrated, -2.10 dBTP, LRA 5.5 LU, VO 0.070-35.130 s, 24.96 s voiced, 56 words (11 keywords), 100 % of word starts on voice; gain +1.00 dB, limiter on; lines V1+V3+V4+V5+V7+V8+V10+V11+V12+V14+V15.
- Hook B (Trial Reel) has no take of its own: stem B = stem A without V2 (the TV-lock line); V1 reads the client bubble. Identical to A from the f144 splice (r1 f72).
- Words: `workspace/jawad_reels/thoda_left_bas/vo/words.json` (A) / `words_B.json` (B), reel time, snake_captions format (+ line, i, dev, heard, ok, start_f, end_f). Copies (FLAC 24-bit + json): `brand_reels/assets/thoda_left_bas/vo_final/thoda_left_bas_vo_{A,B}.flac` / `.words.json`, `placement.json`, `takes.json`.
- Lines not in the VO (ladder F4): V6, V9, V13 (their captions carry them; takes processed and kept).
- Minimum gap between lines: 0.120 s (rule >= 0.12 s).

## 1. Line timing (hook A)

| line | take | speed | start → end (s) | frames | script f (r1 +72 after the hook) | Δ start f | words (reel s) | CER | aligned |
|---|---|---|---|---|---|---|---|---|---|
| V1 | `V01_t1.mp3` | 1.10 | 0.067 → 2.877 | f2.0-f86.3 | f3-f34 | -1.0 | Thoda 0.08 **left...** 0.48 thoda 1.72 right... 2.17 | 0.200 | 4/4 |
| V2 | `V02_t1.mp3` | 1.10 | 2.997 → 5.067 | f89.9-f152.0 | f38-f62 | +51.9 | Bas 3.01 bas! 3.50 Ab 4.22 **theek** 4.44 hai! 4.75 | 0.111 | 5/5 |
| V3 | `V03_t1.mp3` | 1.08 | 5.187 → 7.647 | f155.6-f229.4 | f146-f204 | +9.6 | **Aaya?** 5.19 Nahi! 5.94 Thoda 6.75 left... 7.04 | 0.000 | 4/4 |
| V4 | `V04_t1.mp3` | 1.06 | 7.800 → 8.730 | f234.0-f261.9 | f235-f262 | -1.0 | **Kiska** 7.80 left?! 8.19 | 0.000 | 2/2 |
| V5 | `V05_t1.mp3` | 1.10 | 9.020 → 12.400 | f270.6-f372.0 | f272-f320 | -1.4 | Thoda 9.02 **aur...** 9.73 nahi 10.42 nahi, 11.31 wapas! 11.76 | 0.000 | 5/5 |
| V7 | `V07_t1.mp3` | 1.06 | 12.700 → 15.540 | f381.0-f466.2 | f380-f446 | +1.0 | Ab 12.70 **theek** 13.04 hai!... 13.57 Arre, 14.40 phir 14.93 se?! 15.16 | 0.100 | 6/6 |
| V8 | `V08_t2.mp3` | 1.10 | 15.667 → 17.887 | f470.0-f536.6 | f452-f512 | +18.0 | Yeh 15.68 scene 15.97 kabhi 16.43 **khatam** 16.77 nahi 17.17 hua. 17.45 | 0.083 | 6/6 |
| V10 | `V10_t1.mp3` | 1.10 | 18.007 → 22.087 | f540.2-f662.6 | f542-f607 | -1.8 | Thoda 18.01 left... 18.37 thoda 19.55 right... 20.06 **nahi,** 20.90 pehle 21.41 wala. 21.70 | 0.118 | 7/7 |
| V11 | `V11_t1.mp3` | 1.06 | 22.267 → 23.627 | f668.0-f708.8 | f614-f644 | +54.0 | Dialogue 22.29 **wahi** 22.88 hai. 23.18 | 0.143 | 3/3 |
| V12 | `V12_t1.mp3` | 1.06 | 24.000 → 26.110 | f720.0-f783.3 | f722-f752 | -2.0 | Bas 24.00 bas! 24.35 Ab 25.23 **theek** 25.44 hai! 25.80 | 0.111 | 5/5 |
| V14 | `V14_t1.mp3` | 1.06 | 27.733 → 30.043 | f832.0-f901.3 | f830-f907 | +2.0 | Hum 27.80 aaj 27.99 bhi 28.40 **antenna** 28.75 ghuma 29.21 rahe 29.50 hain. 29.74 | 0.154 | 7/7 |
| V15 | `V15_t1.mp3` | 1.06 | 32.567 → 35.107 | f977.0-f1053.2 | f977-f1047 | +0.0 | Aap 32.60 ke 32.77 ghar 32.97 **antenna** 33.58 kaun 34.18 ghumata 34.41 tha? 34.86 | 0.286 | 7/7 |

## 2. Word frames (stem A; f = reel frame at 30 fps)

| line | word | start s | end s | start f | end f | keyword | heard |
|---|---|---|---|---|---|---|---|
| V1 | Thoda | 0.077 | 0.483 | 2.3 | 14.5 |  | तोड़ा |
| V1 | left... | 0.483 | 1.417 | 14.5 | 42.5 | yes | लेफट... |
| V1 | thoda | 1.717 | 2.174 | 51.5 | 65.2 |  | तोड़ा |
| V1 | right... | 2.174 | 2.847 | 65.2 | 85.4 |  | राइट... |
| V2 | Bas | 3.007 | 3.358 | 90.2 | 100.7 |  | बस! |
| V2 | bas! | 3.503 | 3.831 | 105.1 | 114.9 |  | बस! |
| V2 | Ab | 4.217 | 4.440 | 126.5 | 133.2 |  | अब |
| V2 | theek | 4.440 | 4.749 | 133.2 | 142.5 | yes | ठीक |
| V2 | hai! | 4.749 | 4.912 | 142.5 | 147.4 |  | है! |
| V3 | Aaya? | 5.187 | 5.601 | 155.6 | 168.0 | yes | आया? |
| V3 | Nahi! | 5.937 | 6.507 | 178.1 | 195.2 |  | नहीं! |
| V3 | Thoda | 6.747 | 7.037 | 202.4 | 211.1 |  | तोड़ा |
| V3 | left... | 7.037 | 7.648 | 211.1 | 229.4 |  | लेफट... |
| V4 | Kiska | 7.800 | 8.194 | 234.0 | 245.8 | yes | किसका |
| V4 | left?! | 8.194 | 8.609 | 245.8 | 258.3 |  | लेफट? |
| V5 | Thoda | 9.020 | 9.727 | 270.6 | 291.8 |  | तोड़ा |
| V5 | aur... | 9.727 | 10.418 | 291.8 | 312.5 | yes | और |
| V5 | nahi | 10.418 | 11.309 | 312.5 | 339.3 |  | नहीं |
| V5 | nahi, | 11.309 | 11.570 | 339.3 | 347.1 |  | नहीं |
| V5 | wapas! | 11.760 | 12.200 | 352.8 | 366.0 |  | वापस |
| V7 | Ab | 12.700 | 13.038 | 381.0 | 391.1 |  | अब |
| V7 | theek | 13.038 | 13.567 | 391.1 | 407.0 | yes | ठीक |
| V7 | hai!... | 13.567 | 13.831 | 407.0 | 414.9 |  | है! |
| V7 | Arre, | 14.400 | 14.661 | 432.0 | 439.8 |  | अरे, |
| V7 | phir | 14.930 | 15.161 | 447.9 | 454.8 |  | फिर |
| V7 | se?! | 15.161 | 15.557 | 454.8 | 466.7 |  | से?! |
| V8 | Yeh | 15.677 | 15.974 | 470.3 | 479.2 |  | ये |
| V8 | scene | 15.974 | 16.307 | 479.2 | 489.2 |  | सीन |
| V8 | kabhi | 16.427 | 16.774 | 492.8 | 503.2 |  | कभी |
| V8 | khatam | 16.774 | 17.174 | 503.2 | 515.2 | yes | ख़त्म |
| V8 | nahi | 17.174 | 17.447 | 515.2 | 523.4 |  | नहीं |
| V8 | hua. | 17.447 | 17.797 | 523.4 | 533.9 |  | हुआ। |
| V10 | Thoda | 18.007 | 18.369 | 540.2 | 551.1 |  | तोड़ा |
| V10 | left... | 18.369 | 19.551 | 551.1 | 586.5 |  | लेफट... |
| V10 | thoda | 19.551 | 20.060 | 586.5 | 601.8 |  | तोड़ा |
| V10 | right... | 20.060 | 20.697 | 601.8 | 620.9 |  | राइट... |
| V10 | nahi, | 20.897 | 21.257 | 626.9 | 637.7 | yes | नहीं, |
| V10 | pehle | 21.407 | 21.696 | 642.2 | 650.9 |  | पहले |
| V10 | wala. | 21.696 | 22.096 | 650.9 | 662.9 |  | वाला। |
| V11 | Dialogue | 22.287 | 22.879 | 668.6 | 686.4 |  | डायलॉग |
| V11 | wahi | 22.879 | 23.180 | 686.4 | 695.4 | yes | वही |
| V11 | hai. | 23.180 | 23.417 | 695.4 | 702.5 |  | है। |
| V12 | Bas | 24.000 | 24.347 | 720.0 | 730.4 |  | बस |
| V12 | bas! | 24.347 | 24.932 | 730.4 | 748.0 |  | बस! |
| V12 | Ab | 25.230 | 25.442 | 756.9 | 763.3 |  | अब |
| V12 | theek | 25.442 | 25.800 | 763.3 | 774.0 | yes | ठीक |
| V12 | hai! | 25.800 | 25.970 | 774.0 | 779.1 |  | है! |
| V14 | Hum | 27.803 | 27.986 | 834.1 | 839.6 |  | हम |
| V14 | aaj | 27.986 | 28.401 | 839.6 | 852.0 |  | आज |
| V14 | bhi | 28.401 | 28.643 | 852.0 | 859.3 |  | भी |
| V14 | antenna | 28.753 | 29.212 | 862.6 | 876.4 | yes | एंटीना |
| V14 | ghuma | 29.212 | 29.495 | 876.4 | 884.9 |  | गूमा |
| V14 | rahe | 29.495 | 29.573 | 884.9 | 887.2 |  | रहे |
| V14 | hain. | 29.741 | 30.099 | 892.2 | 903.0 |  | हैं। |
| V15 | Aap | 32.597 | 32.765 | 977.9 | 982.9 |  | आपके |
| V15 | ke | 32.765 | 32.972 | 982.9 | 989.2 |  | आपके |
| V15 | ghar | 32.972 | 33.447 | 989.2 | 1003.4 |  | गर |
| V15 | antenna | 33.577 | 34.097 | 1007.3 | 1022.9 | yes | आंटीना |
| V15 | kaun | 34.177 | 34.406 | 1025.3 | 1032.2 |  | कौन |
| V15 | ghumata | 34.406 | 34.859 | 1032.2 | 1045.8 |  | घुमाता |
| V15 | tha? | 34.859 | 35.029 | 1045.8 | 1050.9 |  | था? |

## 3. Picture beats that move to the VO (proposed frames for the motion designer)

LEAD_DECISIONS 3: the picture follows the measured VO. Proposed frame = the onset frame of the VO word (rounded down, so the visual leads the word by at most 1 frame). |Δ| <= 2 f, or a structural frame (cut / lock / slam marked "stays"): keep the planned frame.

| line | word | event (SHOTS / SCRIPT) | planned f | VO onset f | proposed f | Δ f |
|---|---|---|---|---|---|---|
| V1 | Thoda | H1 `THODA *left...*` (mid-rise on f0) | f0 | 2.3 | **f0** (stays) | +0 |
| V1 | right... | H1b keyword flip `*right...*` + yaw +9 (r1 f18) | f18 | 65.2 | **f65** | +47 |
| V2 | Bas | H2 `BAS BAS!` SLAM + picture LOCK + tv_lock (r1 f36; bar 1 beat 1) | f90 | 90.2 | **f90** (stays) | +0 |
| V2 | Ab | H3 `AB *theek hai!*` (r1 f54) | f54 | 126.5 | **f126** | +72 |
| V3 | Aaya? | R1 `*Aaya?*` (S2 cut f144 = r1 f72) | f144 | 155.6 | **f155** | +11 |
| V3 | Nahi! | R2 far `NAHI! THODA LEFT...` (r1 f99) | f171 | 178.1 | **f178** | +7 |
| V4 | Kiska | R4 `*kiska* left?!` SLAM + tape_stop (r1 f162) | f234 | 234.0 | **f234** (stays) | +0 |
| V5 | Thoda | C5 `thoda *aur...*` (S3 cut f270 = r1 f198) | f270 | 270.6 | **f270** | +0 |
| V5 | nahi | C6 `NAHI NAHI, *wapas!*` (r1 f225) | f297 | 312.5 | **f312** | +15 |
| V7 | Ab | C9 `AB *theek hai!*` LOCK + TV sting (r1 f306) | f378 | 381.0 | **f378** (stays) | +0 |
| V7 | Arre, | C10 `ARRE, *phir se?!*` (r1 f351; gust f414, slip f418-f430) | f423 | 432.0 | **f432** | +9 |
| V8 | Yeh | C11 `YEH SCENE / *khatam* / nahi hua...` (S6 cut f450 = r1 f378) | f450 | 470.3 | **f470** | +20 |
| V10 | Thoda | T1 toast `thoda left...` (r1 f468) | f540 | 540.2 | **f540** | +0 |
| V10 | left... | X 540 -> 538 click + `-2 px` (r1 f477) | f549 | 551.1 | **f551** | +2 |
| V10 | thoda | P1b phone bubble `thoda right...` (r1 f490) | f562 | 586.5 | **f586** | +24 |
| V10 | nahi, | P1c phone bubble `nahi, pehle wala` (r1 f504) | f576 | 626.9 | **f626** | +50 |
| V11 | Dialogue | C13 `DIALOGUE / *wahi* hai.` (r1 f540) | f612 | 668.6 | **f668** | +56 |
| V12 | Bas | C14 `BAS BAS!` + T2 + tv_lock + impact_big (r1 f648) | f720 | 720.0 | **f720** (stays) | +0 |
| V14 | Hum | P1 PAYOFF lockup (hit f828 = r1 f756) | f828 | 834.1 | **f828** (stays) | +0 |
| V15 | Aap | outro question on the card (PO from f954 = r1 f882) | f977 | 977.9 | **f977** (stays) | +0 |

Frames above are on the NEW 1080-f grid. Caption lockups whose word moved: H1b f18 -> f65; H3 f54 -> f126; R1 f144 -> f155; R2 f171 -> f178; C6 f297 -> f312; C10 f423 -> f432; C11 f450 -> f470; X f549 -> f551; P1b f562 -> f586; P1c f576 -> f626; C13 f612 -> f668. The music (thoda_left_bas_music.py) and the SFX cue table (thoda_left_bas_sfx.py) already follow these frames; the full new shot grid is in SOUND.md section 2.

## 4. Takes (CER = faster-whisper small and medium, no prompt, on the processed line vs the DEV text; best of the two; nukta / candrabindu folded, Latin loan words mapped)

| line | pause caps (s) | take | mean CER (1.06/1.08/1.10) | span @1.08 s | heard @ placed speed (small / medium) | chosen |
|---|---|---|---|---|---|---|
| V1 | 0.12 / 0.18 | `V01_t1.mp3` | 0.200 | 2.860 | तोड़ा लेफ्ट, तोड़ा रइट / तोड़ा लेफ्ट, तोड़ा राइट | yes |
| V2 | 0.12 / 0.18 | `V02_t1.mp3` | 0.111 | 2.100 | बस बस अप फीक है / बस, बस, अब फीक है। | yes |
| V3 | 0.30 / 0.40 | `V03_t1.mp3` | 0.000 | 2.460 | आया? नहीं, तोड़ लेफ्ट. / आया नहीं थोड़ा लेफ्ट | yes |
| V4 | 0.45 / 0.60 | `V04_t1.mp3` | 0.000 | 0.900 | किस्का लेफ्ट? / किसका लेफ्ट | yes |
| V5 | 0.25 / 0.30 | `V05_t1.mp3` | 0.000 | 3.450 | तोड़ा और नहीं नहीं वापस / थोड़ा और नहीं नहीं वापस | yes |
| V6 | 0.45 / 0.60 | `V06_t1.mp3` | 0.000 | 2.830 | अग... अग... बस अग... / हाँ हाँ बस। | dropped (F4) |
| V6 | 0.45 / 0.60 | `V06_t2.mp3` | 0.000 | 2.560 | आग, अँ बस / हाँ, हाँ, बस। | dropped (F4) |
| V7 | 0.30 / 0.45 | `V07_t1.mp3` | 0.100 | 2.790 | अब थीक है, औरे फिर से / अब तीक है, अरे फिर से? | yes |
| V8 | 0.45 / 0.60 | `V08_t1.mp3` | 0.195 | 2.270 | ये सीं कभी खद नहीं हूँ / ये सीम कभी खतन नहीं हुआ |  |
| V8 | 0.45 / 0.60 | `V08_t2.mp3` | 0.083 | 2.260 | ये सीं कभी खदन नहीं हूँ / ये सीन कभी खतन नहीं हुआ | yes |
| V9 | 0.30 / 0.30 | `V09_t1.mp3` | 0.111 | 1.310 | भी साल बाद / बीस साल बाद | dropped (F4) |
| V9 | 0.30 / 0.30 | `V09_t2.mp3` | 0.000 | 1.480 | भी साल बाद / बीस साल बाद | dropped (F4) |
| V10 | 0.20 / 0.25 | `V10_t1.mp3` | 0.039 | 4.160 | तोडा लेफ्ट, तोडा रहीट, नहीं बहलेवाला / तोड़ा लेफ्ट, तोड़ा राइट, नहीं पहले वाला. | yes |
| V11 | 0.45 / 0.60 | `V11_t1.mp3` | 0.095 | 1.340 | डालोग वही है / दायलोग वही है। | yes |
| V12 | 0.12 / 0.18 | `V12_t1.mp3` | 0.074 | 2.070 | बस बस अप फीख है / बस बस अब टीक है। | yes |
| V13 | 0.30 / 0.30 | `V13_t1.mp3` | 0.121 | 2.460 | सत्ताइस, रेविशिन बाद / 27. रिविजिन बाद | dropped (F4) |
| V14 | 0.45 / 0.60 | `V14_t1.mp3` | 0.154 | 2.270 | हम आज भी अंटीना गूमा रहे हैं / हम आज भी अन्टीना गुमा रहे हैं। | yes |
| V15 | 0.45 / 0.60 | `V15_t1.mp3` | 0.214 | 2.490 | आपके गर अंटीना कों गूमाता ता? / आपके गर अन्टीना कौन गोमाता था? | yes |

## 5. Notes

- V2: runs 0.120 s into the next line's planned start; V3 moves later
- V5: start pulled 0.047 s earlier to end by its hard limit 12.400 s (f372.0)
- V8: runs 0.007 s into the next line's planned start; V10 moves later
- ladder F4: V6 dropped from the VO; best take `V06_t2.mp3` processed and kept in proc/
- ladder F4: V9 dropped from the VO; best take `V09_t2.mp3` processed and kept in proc/
- ladder F4: V13 dropped from the VO; best take `V13_t1.mp3` processed and kept in proc/
- Rebuild: `cd pipeline/jawad_reels && tools/heavy.sh python3 thoda_left_bas_vo.py process && tools/heavy.sh python3 thoda_left_bas_vo.py assemble` (deterministic; PLAN / CAPS at the top of the module hold the slots), then `tools/heavy.sh python3 thoda_left_bas_sfx.py build` (music, SFX, mixes).
