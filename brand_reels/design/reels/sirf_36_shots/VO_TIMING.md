# VO_TIMING · Sirf 36 Shots (@jawad_mp4)

2026-10-12, sound-designer + music-supervisor, `pipeline/jawad_reels/sirf_36_shots_vo.py assemble` (measured). Voice: Higgsfield preset Vlad, `elevenlabs_v4`, the paid takes in `brand_reels/assets/sirf_36_shots/vo_raw/` (none regenerated, no paid call). Chain `vo_chain.py` per vo_config: trim to 40 ms, internal pauses capped per take (table in section 4), rubberband 1.06-1.10x (formant preserved; the gentlest speed that fits every line of the take), HPF 70 Hz, de-ess, 2.5:1 compression, loudnorm -16 LUFS / -2 dBTP; word timings faster-whisper small (DEV prompt, numpy input) aligned to the DEV tokens, snapped to the voiced onsets. Combined takes (C07C08, C11C13, C14C15) are cut in the middle of the silence between their lines so each line sits on its own beat. P (the client) carries a light voice-note colour (HP 220 Hz / LP 6.2 kHz, loudness-matched). Every line is ridden to the same speech loudness (-16.3 LUFS K-weighted over its voiced span = the median line, before the stem gain; column `ride dB`): the C14C15 t2 take came out 4.5 dB under the rest. LEAD_DECISIONS 3: picture beats move to the VO (section 3).

- **Stem A** `workspace/jawad_reels/sirf_36_shots/vo/vo_stem.wav`: 1728000 samples (36.000 s) at 48000 Hz, -16.00 LUFS integrated, -2.30 dBTP, LRA 2.2 LU, VO 0.030-35.790 s, 27.73 s voiced, 67 words (17 keywords), 100 % of word starts on voice; gain +8.80 dB, limiter on; lines C1 C2 C3 C4 C6 C7 C8 C9 C10 C11 C12 C13 C14 C15 P C16 Q.
- **Stem B** `workspace/jawad_reels/sirf_36_shots/vo/vo_stem_B.wav`: 1728000 samples (36.000 s) at 48000 Hz, -16.00 LUFS integrated, -2.30 dBTP, LRA 2.2 LU, VO 0.030-35.790 s, 26.97 s voiced, 63 words (17 keywords), 100 % of word starts on voice; gain +8.80 dB, limiter on; lines HB C3 C4 C6 C7 C8 C9 C10 C11 C12 C13 C14 C15 P C16 Q.
- Hook B (Trial Reel): `HB_t1.mp3` ("Hilna mat! Aankh mat jhapkana.") replaces C1 + C2; identical to A from C3 on (the flash pops after the hook in both).
- Words: `workspace/jawad_reels/sirf_36_shots/vo/words.json` (A) / `words_B.json` (B), reel time, snake_captions format (+ line, i, dev, heard, ok, start_f, end_f). Copies (FLAC 24-bit + json): `brand_reels/assets/sirf_36_shots/vo_final/sirf_36_shots_vo_{A,B}.flac` / `.words.json`, `placement.json`, `takes.json`.
- Every SCRIPT line is in the VO (no line dropped). Minimum gap between lines: 0.120 s (rule >= 0.12 s).

## 1. Line timing (hook A)

| line | take | speed | ride dB | start → end (s) | frames | SCRIPT VO window f | Δ start f | words (reel s) | CER (take) | aligned (take) |
|---|---|---|---|---|---|---|---|---|---|---|
| C1 | `C01_t1.mp3` | 1.10 | +2.3 | 0.033 → 2.023 | f1.0-f60.7 | f3-f40 | -2.0 | Sirf 0.04 **ek** 0.58 photo 0.86 bachi 1.29 hai. 1.57 | 0.000 | 5/5 |
| C2 | `C02_t1.mp3` | 1.08 | +0.2 | 2.143 → 3.293 | f64.3-f98.8 | f46-f72 | +18.3 | Sab 2.17 **ready** 2.43 ho 2.72 jao! 2.89 | 0.091 | 4/4 |
| C3 | `C03_t1.mp3` | 1.10 | -0.2 | 3.467 → 5.467 | f104.0-f164.0 | f78-f130 | +26.0 | Har 3.48 **click** 3.94 ginti 4.17 mein 4.61 hota 4.79 tha. 5.06 | 0.048 | 6/6 |
| C4 | `C04_t1.mp3` | 1.08 | -0.1 | 5.667 → 7.547 | f170.0-f226.4 | f166-f215 | +4.0 | Phir 5.72 roll 6.13 **studio** 6.43 jaata 6.84 tha... 7.19 | 0.000 | 5/5 |
| C6 | `C06_t1.mp3` | 1.06 | +0.1 | 8.167 → 9.837 | f245.0-f295.1 | f245-f290 | +0.0 | Teen 8.20 din 8.51 ka 8.71 **intezaar.** 8.96 | 0.143 | 4/4 |
| C7 | `C07C08_t1.mp3` | 1.06 | -0.8 | 10.033 → 11.583 | f301.0-f347.5 | f316-f358 | -15.0 | Aadhi 10.03 mein 10.41 **aankhein** 10.69 band, 11.13 | 0.174 | 7/7 |
| C8 | `C07C08_t1.mp3` | 1.06 | +0.3 | 11.703 → 13.113 | f351.1-f393.4 | f376-f410 | -24.9 | aadhi 11.70 mein 12.11 **thumb.** 12.53 | 0.174 | 7/7 |
| C9 | `C09_t1.mp3` | 1.06 | +1.1 | 13.500 → 15.930 | f405.0-f477.9 | f421-f466 | -16.0 | Phir 13.51 bhi 13.74 har 14.49 photo 14.78 **sambhaali.** 15.31 | 0.000 | 5/5 |
| C10 | `C10_t1.mp3` | 1.06 | +0.1 | 16.200 → 17.210 | f486.0-f516.3 | f486-f505 | +0.0 | Aur 16.21 **aaj?** 16.57 | 0.000 | 2/2 |
| C11 | `C11C13_t1.mp3` | 1.06 | -0.3 | 18.033 → 19.303 | f541.0-f579.1 | f541-f566 | +0.0 | Do 18.03 **TB** 18.32 footage, 18.76 | 0.161 | 7/8 |
| C12 | `C11C13_t1.mp3` | 1.06 | -0.6 | 19.423 → 20.373 | f582.7-f611.2 | f571-f592 | +11.7 | **chaar** 19.42 camera, 19.77 | 0.161 | 7/8 |
| C13 | `C11C13_t1.mp3` | 1.06 | -1.2 | 20.493 → 21.843 | f614.8-f655.3 | f601-f640 | +13.8 | teen 20.50 **hazaar** 20.77 takes. 21.32 | 0.161 | 7/8 |
| C14 | `C14C15_t2.mp3` | 1.06 | +4.3 | 22.533 → 23.833 | f676.0-f715.0 | f676-f716 | +0.0 | Har 22.53 take 22.78 **dekha...** 23.04 | 0.118 | 5/5 |
| C15 | `C14C15_t2.mp3` | 1.06 | +4.5 | 24.533 → 25.543 | f736.0-f766.3 | f736-f762 | +0.0 | disk 24.52 **full.** 24.99 | 0.118 | 5/5 |
| P | `P_t1.mp3` | 1.06 | -0.1 | 26.067 → 29.167 | f782.0-f875.0 | f812-f868 | -30.0 | Bhai... 26.08 ek 27.28 achha 27.73 shot 28.15 **nahi** 28.43 hai. 28.81 | 0.158 | 6/6 |
| C16 | `C16_t1.mp3` | 1.10 | -0.0 | 30.120 → 32.000 | f903.6-f960.0 | f913-f950 | -9.4 | Tab 30.13 **chhattees** 30.34 kaafi 31.05 the. 31.58 | 0.000 | 4/4 |
| Q | `Q_t1.mp3` | 1.06 | +0.0 | 33.333 → 35.783 | f1000.0-f1073.5 | f1000-f1050 | +0.0 | Ghar 33.34 ka 33.64 pehla 33.99 **camera** 34.34 kaunsa 35.05 tha? 35.45 | 0.100 | 6/6 |
| HB (B) | `HB_t1.mp3` | 1.06 | +0.3 | 0.033 → 2.533 | f1.0-f76.0 | f0-f70 | +1.0 | Hilna 0.03 **mat!** 0.42 Aankh 1.13 mat 1.47 **jhapkana.** 1.84 | 0.167 | 5/5 |

## 2. Word frames (stem A; f = reel frame at 30 fps)

| line | word | start s | end s | start f | end f | keyword | heard |
|---|---|---|---|---|---|---|---|
| C1 | Sirf | 0.043 | 0.433 | 1.3 | 13.0 |  | सिर्फ |
| C1 | ek | 0.583 | 0.857 | 17.5 | 25.7 | yes | एक |
| C1 | photo | 0.857 | 1.293 | 25.7 | 38.8 |  | फ़ोटो |
| C1 | bachi | 1.293 | 1.566 | 38.8 | 47.0 |  | बची |
| C1 | hai. | 1.566 | 1.953 | 47.0 | 58.6 |  | है। |
| C2 | Sab | 2.173 | 2.427 | 65.2 | 72.8 |  | सब |
| C2 | ready | 2.427 | 2.723 | 72.8 | 81.7 | yes | रेडी |
| C2 | ho | 2.723 | 2.890 | 81.7 | 86.7 |  | हो |
| C2 | jao! | 2.890 | 3.149 | 86.7 | 94.5 |  | जाओ! |
| C3 | Har | 3.477 | 3.807 | 104.3 | 114.2 |  | हर |
| C3 | click | 3.937 | 4.173 | 118.1 | 125.2 | yes | क्लिक |
| C3 | ginti | 4.173 | 4.610 | 125.2 | 138.3 |  | गिनती |
| C3 | mein | 4.610 | 4.792 | 138.3 | 143.8 |  | में |
| C3 | hota | 4.792 | 5.064 | 143.8 | 151.9 |  | होता |
| C3 | tha. | 5.064 | 5.282 | 151.9 | 158.5 |  | था |
| C4 | Phir | 5.717 | 6.037 | 171.5 | 181.1 |  | फिर |
| C4 | roll | 6.127 | 6.433 | 183.8 | 193.0 |  | रोल |
| C4 | studio | 6.433 | 6.841 | 193.0 | 205.2 | yes | स्टूडियो |
| C4 | jaata | 6.841 | 7.193 | 205.2 | 215.8 |  | जाता |
| C4 | tha... | 7.193 | 7.457 | 215.8 | 223.7 |  | था... |
| C6 | Teen | 8.197 | 8.505 | 245.9 | 255.1 |  | तीन |
| C6 | din | 8.505 | 8.713 | 255.1 | 261.4 |  | दिन |
| C6 | ka | 8.713 | 8.958 | 261.4 | 268.7 |  | का |
| C6 | intezaar. | 8.958 | 9.667 | 268.7 | 290.0 | yes | इंतज़ार। |
| C7 | Aadhi | 10.033 | 10.409 | 301.0 | 312.3 |  | आधी |
| C7 | mein | 10.409 | 10.692 | 312.3 | 320.8 |  | में |
| C7 | aankhein | 10.692 | 11.126 | 320.8 | 333.8 | yes | आखें |
| C7 | band, | 11.126 | 11.466 | 333.8 | 344.0 |  | बंद, |
| C8 | aadhi | 11.703 | 12.110 | 351.1 | 363.3 |  | आधी |
| C8 | mein | 12.110 | 12.453 | 363.3 | 373.6 |  | में |
| C8 | thumb. | 12.533 | 12.978 | 376.0 | 389.4 | yes | तंब |
| C9 | Phir | 13.510 | 13.743 | 405.3 | 412.3 |  | फिर |
| C9 | bhi | 13.743 | 14.230 | 412.3 | 426.9 |  | भी |
| C9 | har | 14.490 | 14.781 | 434.7 | 443.4 |  | हर |
| C9 | photo | 14.781 | 15.309 | 443.4 | 459.3 |  | फ़ोटो |
| C9 | sambhaali. | 15.309 | 15.860 | 459.3 | 475.8 | yes | संभाली। |
| C10 | Aur | 16.210 | 16.566 | 486.3 | 497.0 |  | और |
| C10 | aaj? | 16.566 | 17.019 | 497.0 | 510.6 | yes | आज? |
| C11 | Do | 18.033 | 18.324 | 541.0 | 549.7 |  | तो |
| C11 | TB | 18.324 | 18.758 | 549.7 | 562.8 | yes | ती-बी |
| C11 | footage, | 18.758 | 19.173 | 562.8 | 575.2 |  | फ़ुटेज, |
| C12 | chaar | 19.423 | 19.769 | 582.7 | 593.1 | yes | चार |
| C12 | camera, | 19.769 | 20.240 | 593.1 | 607.2 |  | कैमरे, |
| C13 | teen | 20.498 | 20.769 | 615.0 | 623.1 |  | तीन |
| C13 | hazaar | 20.769 | 21.316 | 623.1 | 639.5 | yes | हज़ार |
| C13 | takes. | 21.316 | 21.843 | 639.5 | 655.3 |  | टेक्स। |
| C14 | Har | 22.533 | 22.776 | 676.0 | 683.3 |  | हर |
| C14 | take | 22.776 | 23.040 | 683.3 | 691.2 |  | टेक |
| C14 | dekha... | 23.040 | 23.833 | 691.2 | 715.0 | yes | देखा... |
| C15 | disk | 24.518 | 24.992 | 735.6 | 749.8 |  | डिस्क |
| C15 | full. | 24.992 | 25.543 | 749.8 | 766.3 | yes | फ़ुल। |
| P | Bhai... | 26.077 | 26.905 | 782.3 | 807.1 |  | भाई... |
| P | ek | 27.277 | 27.627 | 818.3 | 828.8 |  | एक |
| P | achha | 27.727 | 28.150 | 831.8 | 844.5 |  | अच्छा |
| P | shot | 28.150 | 28.433 | 844.5 | 853.0 |  | शॉट |
| P | nahi | 28.433 | 28.811 | 853.0 | 864.3 | yes | नहीं |
| P | hai. | 28.811 | 29.150 | 864.3 | 874.5 |  | है। |
| C16 | Tab | 30.130 | 30.345 | 903.9 | 910.4 |  | तब |
| C16 | chhattees | 30.345 | 31.054 | 910.4 | 931.6 | yes | छत्तीस |
| C16 | kaafi | 31.054 | 31.581 | 931.6 | 947.4 |  | काफ़ी |
| C16 | the. | 31.581 | 31.940 | 947.4 | 958.2 |  | थे। |
| Q | Ghar | 33.343 | 33.643 | 1000.3 | 1009.3 |  | गर |
| Q | ka | 33.643 | 33.893 | 1009.3 | 1016.8 |  | का |
| Q | pehla | 33.993 | 34.341 | 1019.8 | 1030.2 |  | पहला |
| Q | camera | 34.341 | 34.913 | 1030.2 | 1047.4 | yes | कैमरा |
| Q | kaunsa | 35.053 | 35.454 | 1051.6 | 1063.6 |  | कौनसा |
| Q | tha? | 35.454 | 35.643 | 1063.6 | 1069.3 |  | था? |

## 3. Picture beats that move to the VO (proposed frames for the motion designer)

LEAD_DECISIONS 3: the picture follows the measured VO. Proposed frame = the onset frame of the VO word (rounded down, so the visual leads the word by at most 1 frame); "after" events follow the END of the word (+2 f). |Δ| <= 2 f, or a structural frame marked "stays": keep the planned frame.

| line | word | event (SHOTS / SCRIPT) | planned f | VO f | proposed f | Δ f |
|---|---|---|---|---|---|---|
| C1 | Sirf | C1 `SIRF / *ek* / PHOTO BACHI.` (mid-rise on f0) | f0 | 1.3 | **f0** (stays) | +0 |
| C2 | Sab | C2 `SAB / *ready* / HO JAO!` | f45 | 65.2 | **f65** | +20 |
| C2 | jao! | FLASH POP + hard cut + L3 push (S2); the kit enters | f60 | 94.5 (end) | **f97** | +37 |
| C3 | Har | C3 `HAR / *click* / GINTI MEIN THA.` | f75 | 104.3 | **f104** | +29 |
| C3 | tha. | C1 whip up into the canister (S3) | f150 | 158.5 (end) | **f161** | +11 |
| C4 | Phir | C4 `PHIR ROLL / *studio* / JAATA THA...` | f165 | 171.5 | **f171** | +6 |
| C6 | Teen | C6 `3 DIN KA / *intezaar.*` (S4 cut f240 stays) | f243 | 245.9 | **f245** | +2 |
| C7 | Aadhi | C7 `AADHI MEIN / *aankhein* / BAND,` + P1 lands | f315 | 301.0 | **f301** | -14 |
| C8 | thumb. | P4 THUMB print SLAP + C8 `*thumb.*` slam (music stop f375-f389) | f375 | 376.0 | **f375** (stays) | +0 |
| C9 | Phir | hard cut f420 album page + C9 `PHIR BHI HAR PHOTO / *sambhaali.*` | f420 | 405.3 | **f405** | -15 |
| C10 | Aur | C10 `AUR / *aaj?*` (C8 snap f480 stays) | f486 | 486.3 | **f486** | +0 |
| C11 | Do | 2 TB slam + storage HUD (C11) | f540 | 541.0 | **f540** (stays) | +0 |
| C12 | chaar | 4 CAMERAS slam (C12) + CAM A-D labels (every 4 f after) | f570 | 582.7 | **f582** | +12 |
| C13 | teen | 3,000 TAKES slam + hard cut to the bin (C13) + take counter roll | f600 | 615.0 | **f615** | +15 |
| C14 | Har | C14 `HAR TAKE / *dekha.*` | f675 | 676.0 | **f675** | +0 |
| C15 | disk | DISK FULL: bar red + chip + glitch (C15) | f735 | 735.6 | **f735** | +0 |
| P | Bhai... | toast slides up + typing dots (drop-out) | f795 | 782.3 | **f782** | -13 |
| P | ek | PAYOFF stack + lockup (f810) | f810 | 818.3 | **f810** (stays) | +0 |
| C16 | Tab | C16 `TAB / *36* / KAAFI THE.` | f909 | 903.9 | **f903** | -6 |
| Q | Ghar | outro question on the card (PO from f960) | f999 | 1000.3 | **f999** (stays) | +0 |

Moves: C2 f45 -> f65; FLASH f60 -> f97; C3 f75 -> f104; C1 f150 -> f161; C4 f165 -> f171; C6 f243 -> f245; C7 f315 -> f301; hard f420 -> f405; 4 f570 -> f582; 3,000 f600 -> f615; toast f795 -> f782; C16 f909 -> f903. Fixed by sound (the music and SFX already follow): FLASH POP f100 (was f60), C1 whip f167 (was f150). Caption lockups enter on their word onset (rows above); exits stay as SHOTS unless the next lockup now enters earlier. The music (sirf_36_shots_music.py) and the SFX cue table (sirf_36_shots_sfx.py) follow these frames; SOUND.md section 2 has the full grid.

## 4. Takes (CER = faster-whisper small and medium, no prompt, on the processed take vs the DEV text; best of the two; nukta / candrabindu folded, Latin loan words mapped)

| unit (lines) | pause caps (s) | take | mean CER (1.06/1.08/1.10) | span @1.08 s | heard @ placed speed (small / medium) | chosen |
|---|---|---|---|---|---|---|
| C1 (C1) | 0.25 / 0.30 | `C01_t1.mp3` | 0.000 | 2.030 | सर्फ एक फोटो बची है / सिर्फ एक फोटो बची है। | yes |
| C2 (C2) | 0.20 / 0.25 | `C02_t1.mp3` | 0.091 | 1.150 | सब रेडी हुजाो / सब रेडि हो जाओ | yes |
| C3 (C3) | 0.45 / 0.60 | `C03_t1.mp3` | 0.064 | 2.040 | और क्लिक गिन्ती में हुता ता / हर क्लिक गिन्ती में होता था। | yes |
| C4 (C4) | 0.45 / 0.60 | `C04_t1.mp3` | 0.000 | 1.880 | फिर रोल स्टुड्यो जाता ता / फिर रोल स्टूडियो जाता था। | yes |
| C6 (C6) | 0.45 / 0.60 | `C06_t1.mp3` | 0.095 | 1.630 | तीन दिनका इन्तजार / 3 दिन का इंतजार | yes |
| C7C8 (C7+C8) | 0.45 / 0.60 | `C07C08_t1.mp3` | 0.188 | 3.290 | आदी में आखे बन्द, आदी में तंब / आधि में आखें बंद, आधि में तंब। | yes |
| C9 (C9) | 0.30 / 0.35 | `C09_t1.mp3` | 0.000 | 2.380 | फिर भी हर फोटो संभाली / फिर भी हर फोटो संभाली। | yes |
| C10 (C10) | 0.45 / 0.60 | `C10_t1.mp3` | 0.000 | 0.980 | और आज / और आज? | yes |
| C11C13 (C11+C12+C13) | 0.45 / 0.60 | `C11C13_t1.mp3` | 0.097 | 4.130 | तो तीबी फुटछ, चार कम्रे, तीन हसार टेक्स / दो टीबी फूटटज, चार कैम्रे, तीन हासार टेक्स | yes |
| C14C15 (C14+C15) | 0.45 / 0.60 | `C14C15_t1.mp3` | 0.176 | 2.540 | हर टिक दिख हा, दिस्क फुल / हर टिक देखा, दिस्क फूल। |  |
| C14C15 (C14+C15) | 0.45 / 0.60 | `C14C15_t2.mp3` | 0.118 | 2.560 | हर टेख देखा दिस्क फोल / हर टेक देखा दिस्क फूल। | yes |
| P (P) | 0.45 / 0.55 | `P_t1.mp3` | 0.158 | 3.060 | बाई एक अच्छा शोर्ट नहीं है / बाई, एक अच्छा शॉर्ट नहीं है। | yes |
| C16 (C16) | 0.45 / 0.60 | `C16_t1.mp3` | 0.000 | 1.910 | तब 36 काफी थे / तब 36 काफी थे। | yes |
| Q (Q) | 0.45 / 0.60 | `Q_t1.mp3` | 0.100 | 2.410 | गर का पहला केम्रा कोंसा ता? / गर का पहला कैम्रा कौनसा था? | yes |
| HB (HB1+HB2) | 0.30 / 0.35 | `HB_t1.mp3` | 0.167 | 2.450 | हिलना मत, आख मत जबकाना / हिलना मत आक मत जपकाना | yes |

## 5. Notes

- C16: start pulled 0.113 s earlier to end by its hard limit 32.000 s (f960.0)
- Rebuild: `cd pipeline/jawad_reels && tools/heavy.sh python3 sirf_36_shots_vo.py process && tools/heavy.sh python3 sirf_36_shots_vo.py assemble` (deterministic; PLAN / CAPS / FLASH_F / WHIP_F at the top of the module hold the slots), then `tools/heavy.sh python3 sirf_36_shots_sfx.py build` (music, SFX, mixes).
