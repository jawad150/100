# VO_TIMING · Reel 4 · C02 · "Beta, tum karte kya ho?"

Measured 2026-10-09 07:32 UTC on the final processed Vlad takes (Higgsfield `elevenlabs_v4`, preset Vlad, provider defaults) after `vo_chain` (trim to 40 ms, pause caps, rubberband, HPF / de-ess / comp, loudnorm). Written by `pipeline/jawad_reels/beta_tum_karte_kya_ho_vo.py assemble`; replaces the ESTIMATED table of `SCRIPT.md` section 3.

Grid 85.714 BPM (beat 0.7 s = 21 f, bar 2.8 s = 84 f), DUR 36.4 s. Placement: each line's first voiced onset (vo_chain voiced runs, peak - 45 dB) on its `start_target`, sample-exact (L11: the SCRIPT 7 onset ladder, 34.90 down to 34.70). Limit = min(end_target + 0.15, hard limit (L1 2.69, L1B 2.45, L11 36.35), next onset - 0.15). CER = faster-whisper small / medium (language hi, no prompt) on the placed processed take vs the DEV text actually sent (Latin loans mapped back; nukta, chandrabindu, half nasal = anusvara, cluster virama and the spoken forms वह/वो, पर/पे, लिये/लिए folded); a line fails ASR only when BOTH models give CER > 0.15 or both mis-hear a keyword / SCRIPT 6 risk word.

## Per line (placed)

| line | words (ROM) | take · ladder step | slot (s) | voice on (vs slot) | voice off | end vs target (s) | speech (s) | onset bar.beat | words | w/s | caption keyword @ t | CER small / medium | gap to next (s) | flags |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| L1 | Yeh sawaal client nahi poochta. | `btk_L1-F_t1` 1.08 | 0.10-2.69 | 0.100 (+0.000) | 2.430 | -0.260 | 2.33 | 0.0+3f | 5 | 2.15 | - | 0.143 / 0.048 | 0.52 | fallback |
| L1B | Mummy ke liye, cartoon. | `btk_L1B-R_t1` 1.08 | 0.10-2.40 | 0.100 (+0.000) | 2.050 | -0.350 | 1.95 | 0.0+3f | 4 | 2.05 | - | 0.067 / 0.067 | 0.90 | MISS end -0.35 s (early); prosody |
| L2 | Jawab ka translation... | `btk_L2_t3` 1.10 | 2.95-4.15 | 2.950 (+0.000) | 4.370 | +0.220 | 1.42 | 1.0+4f | 3 | 2.11 | *translation...* @ 3.56 (1.1+2f, +0.07 to 8th) | 0.067 / 0.000 | 0.73 | OVER limit 4.30 |
| L3 | Jitna samjhao, ulta. | `btk_L3-J_t1` 1.08 | 5.10-6.95 | 5.100 (+0.000) | 7.090 | +0.140 | 1.99 | 1.3+6f | 3 | 1.51 | *ulta.* @ 6.52 (2.1+7f, -0.13 to 8th) | 0.286 / 0.071 | 3.86 | fallback |
| L4 | Seedha jawab: | `btk_L4_t2` 1.10 | 10.95-11.70 | 10.950 (+0.000) | 12.000 | +0.300 | 1.05 | 3.3+13f | 2 | 1.90 | *Seedha* @ 10.98 (3.3+14f, +0.13 to 8th) | 0.375 / 0.125 | 2.15 | end +0.30 s: on the 0.3 s line; OVER limit 11.85 |
| L5 | Phir... haar maan li. | `btk_L5-C_t1` 1.08 | 14.15-16.15 | 14.150 (+0.000) | 16.130 | -0.020 | 1.98 | 5.0+4f | 4 | 2.02 | *haar* @ 14.98 (5.1+8f, -0.07 to 8th) | 0.091 / 0.000 | 0.82 | prosody |
| L6 | Mahine baad... | `btk_L6-F_t1` 1.10 | 16.95-17.95 | 16.950 (+0.000) | 18.110 | +0.160 | 1.16 | 6.0+4f | 2 | 1.72 | - | 0.000 / 0.125 | 1.64 | OVER limit 18.10; fallback |
| L7 | Phir ek din family group mein... ek reel forward hoti hai. | `btk_L7-O_t1` 1.10 | 19.75-24.27 | 19.750 (+0.000) | 23.930 | -0.340 | 4.18 | 7.0+4f | 11 | 2.63 | *reel* @ 22.45 (8.0+1f, +0.05 to 8th) | 0.079 / 0.158 | 0.52 | MISS end -0.34 s (early); ASR; prosody |
| L8 | Sab ki nazar... Mummy pe. | `btk_L8_t1` 1.08 | 24.45-27.12 | 24.450 (+0.000) | 27.270 | +0.150 | 2.82 | 8.2+20f | 5 | 1.77 | *nazar...* @ 25.09 (8.3+18f, -0.11 to 8th) | 0.077 / 0.077 | 0.98 | ok |
| L9 | Ab woh sab ko khud samjhaati hain... humse behtar. | `btk_L9_t1` 1.08 | 28.25-31.97 | 28.250 (+0.000) | 32.090 | +0.120 | 3.84 | 10.0+8f | 9 | 2.34 | - | 0.241 / 0.138 | 0.46 | ok |
| L10 | Isko family group mein bhejo. | `btk_L10_t2` 1.08 | 32.55-34.40 | 32.550 (+0.000) | 34.350 | -0.050 | 1.80 | 11.2+10f | 5 | 2.78 | - | 0.143 / 0.238 | 0.38 | ok |
| L11 | Ab Nani ki baari. | `btk_L11_t2` 1.10 | 34.90-36.35 | 34.730 (-0.170) | 36.350 | +0.000 | 1.62 | 12.1+13f | 4 | 2.47 | - | 0.000 / 0.000 | 0.15 (loop seam) | ok |

**End vs target beyond 0.3 s:** L1B -0.35 s, L4 +0.30 s, L7 -0.34 s (early = the line ends before its slot end: no conflict).

## Pronunciation check (step 1: 11 carriers, `vo/pron_check_*.json`)

| carrier | text | small heard | medium heard | verdict |
|---|---|---|---|---|
| P0 | ये सवाल क्लाइंट नहीं पूछता। | ये सवाल प्लैंट नहीं पूछता | ये सवाल प्लाइंट नहीं पूछता. | FAIL: both models hear a p-onset (प्लैंट / प्लाइंट) -> spelling क्लायंट |
| P1 | ये सवाल क्लायंट नहीं पूछता। | ये सवाल ख्लान्त नहीं पुछता | ये सवाल क्लाइंट नहीं पूछता. | use: medium hears क्लाइंट exactly (small ख्लान्त, its usual k-aspiration habit) |
| P2 | मम्मी बोलीं, कार्टून। | मम्मी बोली कार्टून | मम्मी बोलीं कार्टुन | keep मम्मी (medium exact for both spellings) |
| P3 | ममी बोलीं, कार्टून। | ममी बोली कार्टून | मम्मी बोली कार्टुन | ममी not needed |
| P4 | पहले इसका ट्रांसलेशन करो। | पहले इसका ट्रान्सलेशिन करो | पहले इसका ट्रांसलेशन करो। | keep ट्रांसलेशन (medium exact) |
| P6 | फ़ैमिली ग्रुप में भेजो। | फामली ग्रुपने बेजो | फामिली गूप ने भेजो। | keep फ़ैमिली (heard फामली / फामिली for both spellings); भेजो exact (medium) |
| P7 | फ़ेमिली ग्रुप में भेजो। | फामली गुरुप में भेजो | फामिली ग्रूप में भेजो। | फ़ेमिली no better |
| P8 | एक रील फ़ॉरवर्ड हुई। | तेख रील पववड हुई | देख रिल फोवड हुई। | forward heard r-less (पववड / फोवड): see the human-listen flags |
| P9 | सब उल्टा है, सब सीधा है। | सब उर्टा है सब सीदा है | सब उल्ता है, सब सीधा है | keep उल्टा, सीधा (medium exact) |
| P10 | सब की नज़र उन पे, वो ख़ुद हमसे बेहतर हैं। | सब की नजर उन पे वो खुद हम से बहतर है | सब की नजर उन पे वो खुद हम से बहतर हैं | keep नज़र, ख़ुद, हमसे; बेहतर heard बहतर (colloquial spelling) |
| P11 | अब नानी की बारी आई। | अब नानी की बारी आई | अब नानी की बारी आई। | keep नानी, बारी (both exact; not भारी) |
| P5 | पहले इसका ट्रैन्सलेशन करो। | - | - | not generated (429 rate limit, no job, not charged); not needed: P4 passed |

## Human-listen flags (ASR cannot judge stress / accent)

- L7: both models hear फ़ोरवर्ड (small "फोवर्ड", medium "फौवड"); every take and spelling tried gave the same (L7: 4 takes, 3 spellings) -> the voice says it non-rhotic ("fo-ward"): listen; if it reads wrong, the only further lever is Latin "forward" in the TTS text (untested).
- L1 क्लायंट ("client"): medium hears क्लाइंट, small ख्लांट (gate note 9 asks one human listen before publishing).
- L1B / L8 मम्मी: stress must fall on the first syllable (MUM-mee); ASR cannot tell. L8 heard ममी (same word).
- L10 भेजो ("bhejo", the CTA): small exact, medium भहझो (aspiration present, odd vowel): listen.
- L9 समझाती: both models write संजाती (m -> n before jh, the common spoken assimilation); listen.

## Text changes against script.json (measured necessity)

- L1 (`btk_L1-F_t1`, fallback): DEV `ये सवाल क्लायंट नहीं पूछता।` · ROM "Yeh sawaal client nahi poochta." · why: SLATE 3.4 fallback; the locked line measured 3.28 s of voice (limit 2.59 s from 0.10)
- L1B (`btk_L1B-R_t1`, prosody): DEV `मम्मी के लिए, कारटून।` · ROM "Mummy ke liye, cartoon." · why: both ASR models heard कार्टून as काटून (r dropped) in both takes; full र spelling
- L3 (`btk_L3-J_t1`, fallback): DEV `जितना समझाओ, उल्टा।` · ROM "Jitna samjhao, *ulta." · why: word cut (alternative to L3-S): drops "utna"
- L5 (`btk_L5-C_t1`, prosody): DEV `फिर, हार मान ली।` · ROM "Phir... *haar maan li." · why: "Phir..." was drawn out to 1.0 s; a comma beat is shorter
- L6 (`btk_L6-F_t1`, fallback): DEV `महीने बाद...` · ROM "Mahine baad..." · why: script.json L6 fallback (2 words)
- L7 (`btk_L7-O_t1`, prosody): DEV `फिर एक दिन फ़ैमिली ग्रुप में, एक रील फ़ोरवर्ड होती है।` · ROM "Phir ek din family group mein... ek *reel forward hoti hai." · why: both ASR models heard फ़ॉरवर्ड / फ़ॉर्वर्ड as फोवर्ड (first r dropped) in 3 takes; ो + full र (the कारटून fix brought the r back in L1B) + the L7-C comma beat that fits the slot
- Spelling: क्लाइंट -> क्लायंट (pronunciation carriers P0 / P1: whisper small and medium both heard P0 as प्लैंट / प्लाइंट, i.e. a p-onset; P1 was heard क्लाइंट by medium). All other SCRIPT 6 spellings kept (मम्मी, ट्रांसलेशन, फ़ैमिली, कार्टून, उल्टा, सीधा, पूछता, ख़ुद, नज़र, बेहतर, नानी, बारी: see `vo/pron_check_small.json`, `vo/pron_check_medium.json`).

## Stems and words

- Workspace `workspace/jawad_reels/beta_tum_karte_kya_ho/vo/`: `vo_stem.wav` = `beta_tum_karte_kya_ho_vo_A.wav` (L1 + L2-L11), `beta_tum_karte_kya_ho_vo_B.wav` (L1B + L2-L11, same static gain; body identical after 2.8 s: True, max diff 0.0e+00). 48 kHz 24-bit mono, 36.400 s.
- A: -16.04 LUFS integrated (ebur128 -16.0), TP -2.46 dBTP, LRA 4.8 LU. B: -16.10 LUFS, TP -2.46 dBTP. Master chain on the placed takes (each -16 LUFS from vo_chain): [{"lufs": -16.5, "tp": -0.7, "gain_db": 0.5, "limiter_db": -2.6}, {"lufs": -16.04, "tp": -2.46}]. Per-line loudness in the stem (LUFS): L1 -15.5, L2 -15.6, L3 -15.4, L4 -15.2, L5 -15.5, L6 -15.7, L7 -15.5, L8 -15.6, L9 -16.1, L10 -15.6, L11 -15.5, L1B -15.9; lines more than 1.5 LU from the median: none. Onset error of every line in the written stem: max 0.0000 s.
- Speech A: 24.19 s of voice, first onset 0.100 s, last offset 36.350 s; 53 words. Loop seam (L11 end -> 36.4 -> L1 onset): A 0.150 s, B 0.150 s.
- `words.json` = `beta_tum_karte_kya_ho.words.json` (version A, reel seconds; `snake_captions.load_words` format plus line / i / dev / heard / ok / hide), `words_B.json` (version B). 53 words, 53 aligned ok by vo_chain.
- Checks: all pass. Over the line limit (no take fits; reported, not fixed): L2 ends 4.370 > limit 4.300; L4 ends 12.000 > limit 11.850; L6 ends 18.110 > limit 18.100. Notes: L11 onset 34.730 moved from the slot start 34.90 (ladder).
- Credits (this reel, sum of its own get_cost preflights for submitted requests): 10.81 of 25.
- Visual checks: `vo/vo_timeline.png` (slots vs measured voice on the beat grid), `vo/vo_lines.png` (per line spectrogram, envelope, word starts).

## All candidates (take x ladder step)

| line | take | kind | step | voice (s) | end (s) | fits | CER small / medium | misheard by both | heard (small) | heard (medium) | pick |
|---|---|---|---|---|---|---|---|---|---|---|---|
| L1 | `btk_L1-F_t1` | fallback | 1.08 | 2.330 | 2.430 | yes | 0.143 / 0.048 | - | ये सवाल ख्लांट नहीं पुछता | ये सवाल क्लाइंट नहीं पूछता। | **picked** (ASR ok + fits) |
| L1 | `btk_L1-F_t1` | fallback | 1.10 | 2.290 | 2.390 | yes | 0.238 / 0.048 | - | ये सवाल ख्लाँट नहीं पुच्टा | ये सवाल क्लाइंट नहीं पूछता. |  |
| L1 | `btk_L1_t1` | script | 1.08 | 3.280 | 3.380 | no (+0.69) | 0.138 / 0.138 | - | सब से मुशकिल सवाल ख्लाईट नहीं पुछता | सबसे मुष्किल सवाल क्लाइंट नहीं पूँचता |  |
| L1 | `btk_L1_t1` | script | 1.10 | 3.220 | 3.320 | no (+0.63) | 0.103 / 0.172 | - | सब से मुशकिल सवाल ख्लांट नहीं पुछता | सबसे मुष्किल सवाल खलाइंट नहीं पूँचता |  |
| L1 | `btk_L1_t1` | script | 1.10t | 3.110 | 3.210 | no (+0.52) | 0.138 / 0.138 | - | सब से मुष्किल सवाल ख्लाएंट नहीं पुछता | सबसे मुष्किल सवाल खलाइंट नहीं पूचता |  |
| L1B | `btk_L1B-R_t1` | prosody | 1.08 | 1.950 | 2.050 | yes | 0.067 / 0.067 | - | ममी के लिए कार्टून | मम्मी के लिए कार्टुन | **picked** (ASR ok + fits) |
| L1B | `btk_L1B-R_t1` | prosody | 1.10 | 1.910 | 2.010 | yes | 0.067 / 0.067 | - | ममी के लिए कार्टून | मम्मी के लिए कार्टुन |  |
| L1B | `btk_L1B_t1` | script | 1.08 | 1.990 | 2.090 | yes | 0.067 / 0.133 | कार्टून | मम्मी के लिए काटून | मम्मी के लिए काटुन |  |
| L1B | `btk_L1B_t1` | script | 1.10 | 1.970 | 2.070 | yes | 0.067 / 0.133 | कार्टून | मम्मी के लिए काटून | मम्मी के लिए काटुन |  |
| L1B | `btk_L1B_t2` | script | 1.08 | 1.880 | 1.980 | yes | 0.133 / 0.133 | कार्टून | ममी के लिए काटून | मम्मी के लिए काटुन |  |
| L1B | `btk_L1B_t2` | script | 1.10 | 1.850 | 1.950 | yes | 0.133 / 0.133 | कार्टून | ममी के लिए काटून | मम्मी के लिए काटुन |  |
| L2 | `btk_L2-C_t1` | prosody | 1.08 | 1.510 | 4.460 | no (+0.16) | 0.133 / 0.067 | - | जबाब का ट्रान्सलेशिन | जबाब का translation |  |
| L2 | `btk_L2-C_t1` | prosody | 1.10 | 1.470 | 4.420 | no (+0.12) | 0.133 / 0.067 | - | जबाब का ट्रान्स्लेशिन | जबाब का translation |  |
| L2 | `btk_L2-C_t1` | prosody | 1.10t | 1.470 | 4.420 | no (+0.12) | 0.133 / 0.067 | - | जबाब का ट्रान्स्लेशिन | जबाब का translation |  |
| L2 | `btk_L2_t1` | script | 1.08 | 1.470 | 4.420 | no (+0.12) | 0.067 / 0.000 | - | जवाब का ट्रान्स्लेशिन | जवाब का translation |  |
| L2 | `btk_L2_t1` | script | 1.10 | 1.450 | 4.400 | no (+0.10) | 0.067 / 0.000 | - | जवाब का ट्रान्सलेशिन | जवाब का translation |  |
| L2 | `btk_L2_t1` | script | 1.10t | 1.450 | 4.400 | no (+0.10) | 0.067 / 0.000 | - | जवाब का ट्रान्सलेशिन | जवाब का translation |  |
| L2 | `btk_L2_t2` | script | 1.08 | 1.480 | 4.430 | no (+0.13) | 0.067 / 0.000 | - | जवाब का ट्रान्सलेशिन | जवाब का translation |  |
| L2 | `btk_L2_t2` | script | 1.10 | 1.460 | 4.410 | no (+0.11) | 0.067 / 0.000 | - | जवाब का ट्रान्सलेशिन | जवाब का translation |  |
| L2 | `btk_L2_t2` | script | 1.10t | 1.460 | 4.410 | no (+0.11) | 0.067 / 0.000 | - | जवाब का ट्रान्सलेशिन | जवाब का translation |  |
| L2 | `btk_L2_t3` | script | 1.08 | 1.450 | 4.400 | no (+0.10) | 0.067 / 0.000 | - | जवाब का ट्रान्सलेशिन | जवाब का translation |  |
| L2 | `btk_L2_t3` | script | 1.10 | 1.420 | 4.370 | no (+0.07) | 0.067 / 0.000 | - | जवाब का ट्रान्स्लेशिन | जवाब का translation | **picked** (NO candidate fits: the ASR-ok one with the smallest overrun) |
| L2 | `btk_L2_t3` | script | 1.10t | 1.420 | 4.370 | no (+0.07) | 0.067 / 0.000 | - | जवाब का ट्रान्स्लेशिन | जवाब का translation |  |
| L3 | `btk_L3-J_t1` | fallback | 1.08 | 1.990 | 7.090 | yes | 0.286 / 0.071 | - | जितना सम्जहाँ उल्टा | जितना सम्झाओ उल्टा | **picked** (ASR ok + fits) |
| L3 | `btk_L3-J_t1` | fallback | 1.10 | 1.970 | 7.070 | yes | 0.214 / 0.071 | - | जितना सम्जाउ उल्टा | जितना सम्झाओ उल्टा |  |
| L3 | `btk_L3-N_t1` | prosody | 1.08 | 2.570 | 7.670 | no (+0.57) | 0.167 / 0.056 | - | जितना सम्जाउ उतना उल्टा | जितना सम्झाओ उतना उल्टा |  |
| L3 | `btk_L3-N_t1` | prosody | 1.10 | 2.520 | 7.620 | no (+0.52) | 0.222 / 0.056 | - | जितना समज्हाू उतना उल्ता | जितना सम्झाओ उतना उल्टा |  |
| L3 | `btk_L3-N_t1` | prosody | 1.10t | 2.520 | 7.620 | no (+0.52) | 0.222 / 0.056 | - | जितना समज्हाू उतना उल्ता | जितना सम्झाओ उतना उल्टा |  |
| L3 | `btk_L3-S_t1` | fallback | 1.08 | 1.740 | 6.840 | yes | 0.182 / 0.182 | - | समजाो तो उल्टा? | सम्जाओ तो उल्टा? |  |
| L3 | `btk_L3-S_t1` | fallback | 1.10 | 1.710 | 6.810 | yes | 0.182 / 0.182 | - | समजाो तो उल्टा? | सम्जाओ तो उल्टा? |  |
| L3 | `btk_L3_t1` | script | 1.08 | 2.620 | 7.720 | no (+0.62) | 0.111 / 0.056 | - | जितना समजहाओ उतना उल्टा | जितना सम्झाओ, उतना उल्टा |  |
| L3 | `btk_L3_t1` | script | 1.10 | 2.570 | 7.670 | no (+0.57) | 0.167 / 0.056 | - | जितना सम्जाउ उतना उल्टा | जितना सम्झाओ उतना उल्टा |  |
| L3 | `btk_L3_t1` | script | 1.10t | 2.570 | 7.670 | no (+0.57) | 0.167 / 0.056 | - | जितना सम्जाउ उतना उल्टा | जितना सम्झाओ उतना उल्टा |  |
| L4 | `btk_L4_t1` | script | 1.08 | 1.100 | 12.050 | no (+0.20) | 0.375 / 0.000 | - | सीद हजबाब | सीधा जवाब |  |
| L4 | `btk_L4_t1` | script | 1.10 | 1.090 | 12.040 | no (+0.19) | 0.250 / 0.125 | - | सीद हजवाब | सीदा जवाब |  |
| L4 | `btk_L4_t1` | script | 1.10t | 1.090 | 12.040 | no (+0.19) | 0.250 / 0.125 | - | सीद हजवाब | सीदा जवाब |  |
| L4 | `btk_L4_t2` | script | 1.08 | 1.060 | 12.010 | no (+0.16) | 0.375 / 0.125 | - | सीद हा जबाब | सीथा जवाब |  |
| L4 | `btk_L4_t2` | script | 1.10 | 1.050 | 12.000 | no (+0.15) | 0.375 / 0.125 | - | सीद हा जबाब | सीथा जवाब | **picked** (NO candidate fits: the ASR-ok one with the smallest overrun) |
| L4 | `btk_L4_t2` | script | 1.10t | 1.050 | 12.000 | no (+0.15) | 0.375 / 0.125 | - | सीद हा जबाब | सीथा जवाब |  |
| L5 | `btk_L5-C_t1` | prosody | 1.08 | 1.980 | 16.130 | yes | 0.091 / 0.000 | - | फिर हार्मान्ली | फिर हार मान ली। | **picked** (ASR ok + fits) |
| L5 | `btk_L5-C_t1` | prosody | 1.10 | 1.940 | 16.090 | yes | 0.091 / 0.182 | - | फिर हार्मान्ली | फिर हार मान लिए। |  |
| L5 | `btk_L5_t1` | script | 1.08 | 2.500 | 16.650 | no (+0.35) | 0.091 / 0.182 | - | फिर हार्मान्ली | फिर हार मान लिए |  |
| L5 | `btk_L5_t1` | script | 1.10 | 2.450 | 16.600 | no (+0.30) | 0.000 / 0.182 | - | फिर हार मानली | फिर हार मान लिए |  |
| L5 | `btk_L5_t1` | script | 1.10t | 2.350 | 16.500 | no (+0.20) | 0.091 / 0.182 | - | फिर हार्मान्ली | फिर हार मान लिए |  |
| L6 | `btk_L6-C_t1` | prosody | 1.08 | 1.360 | 18.310 | no (+0.21) | 0.000 / 0.091 | - | कुछ महीने बाद | कुछ महिने बाद |  |
| L6 | `btk_L6-C_t1` | prosody | 1.10 | 1.340 | 18.290 | no (+0.19) | 0.091 / 0.091 | - | कुच महीने बाद | कुछ महिने बाद |  |
| L6 | `btk_L6-C_t1` | prosody | 1.10t | 1.340 | 18.290 | no (+0.19) | 0.091 / 0.091 | - | कुच महीने बाद | कुछ महिने बाद |  |
| L6 | `btk_L6-F_t1` | fallback | 1.08 | 1.180 | 18.130 | no (+0.03) | 0.000 / 0.125 | - | महीने बाद | महिने बाद |  |
| L6 | `btk_L6-F_t1` | fallback | 1.10 | 1.160 | 18.110 | no (+0.01) | 0.000 / 0.125 | - | महीने बाद | महिने बाद | **picked** (NO candidate fits: the ASR-ok one with the smallest overrun) |
| L6 | `btk_L6-F_t1` | fallback | 1.10t | 1.160 | 18.110 | no (+0.01) | 0.000 / 0.125 | - | महीने बाद | महिने बाद |  |
| L6 | `btk_L6-F_t2` | fallback | 1.08 | 1.200 | 18.150 | no (+0.05) | 0.000 / 0.125 | - | महीने बाद | महिने बाद |  |
| L6 | `btk_L6-F_t2` | fallback | 1.10 | 1.190 | 18.140 | no (+0.04) | 0.000 / 0.125 | - | महीने बाद | महिने बाद |  |
| L6 | `btk_L6-F_t2` | fallback | 1.10t | 1.190 | 18.140 | no (+0.04) | 0.000 / 0.125 | - | महीने बाद | महिने बाद |  |
| L6 | `btk_L6_t1` | script | 1.08 | 1.360 | 18.310 | no (+0.21) | 0.000 / 0.091 | - | कुछ महीने बाद | कुछ महिने बाद |  |
| L6 | `btk_L6_t1` | script | 1.10 | 1.340 | 18.290 | no (+0.19) | 0.000 / 0.091 | - | कुछ महीने बाद | कुछ महिने बाद |  |
| L6 | `btk_L6_t1` | script | 1.10t | 1.340 | 18.290 | no (+0.19) | 0.000 / 0.091 | - | कुछ महीने बाद | कुछ महिने बाद |  |
| L7 | `btk_L7-C_t1` | prosody | 1.08 | 3.940 | 23.690 | yes | 0.158 / 0.184 | ग्रुप, फ़ॉर्वर्ड | फिर एक दिन फामली गुप में एक रील फोवर्ट होती है | फिर एक दिन फामली गूप में एक रील फौवड होती है। |  |
| L7 | `btk_L7-C_t1` | prosody | 1.10 | 3.870 | 23.620 | yes | 0.105 / 0.132 | फ़ॉर्वर्ड | फिर एक दिन फामली ग्रुप में एक रील फोवर्ड होती है | फिर एक दिन फामिली गूप में एक रील फौवर्ड होती है। |  |
| L7 | `btk_L7-O_t1` | prosody | 1.08 | 4.250 | 24.000 | yes | 0.132 / 0.132 | ग्रुप, फ़ोरवर्ड | फिर एक दिन फामली गुप में एक रील फोवर्ट होती है | फिर एक दिन फामिली गूप में एक रील फोवड होती है। |  |
| L7 | `btk_L7-O_t1` | prosody | 1.10 | 4.180 | 23.930 | yes | 0.079 / 0.158 | फ़ोरवर्ड | फिर एक दिन फामली ग्रुप में एक रील फोवर्ड होती है | फिर एक दिन फामिली गूप में एक रील फौवड होती है। | **picked** (fits, but no fitting take passes ASR (both models mis-hear फ़ोरवर्ड): human listen) |
| L7 | `btk_L7_t1` | script | 1.08 | 4.820 | 24.570 | no (+0.27) | 0.105 / 0.158 | फ़ॉरवर्ड | फिर एक दिन फामली ग्रुप में एक रील फोवर्ड होती है | फिर एक दिन, फामिली गूप में एक रील फौवड होती है। |  |
| L7 | `btk_L7_t1` | script | 1.10 | 4.730 | 24.480 | no (+0.18) | 0.132 / 0.132 | फ़ॉरवर्ड | फिर एक दिन फामली ग्रुप में एक रील फोवर्ट होती है | फिर एक दिन फामिली गूप में एक रील फौवर्ड होती है। |  |
| L7 | `btk_L7_t1` | script | 1.10t | 4.570 | 24.320 | no (+0.02) | 0.105 / 0.132 | फ़ॉरवर्ड | फिर एक दिन फामली ग्रुप में एक रील फोवर्ड होती है | फिर एक दिन फामिली गूप में एक रील फौवर्ड होती है। |  |
| L7 | `btk_L7_t2` | script | 1.08 | 4.880 | 24.630 | no (+0.33) | 0.105 / 0.132 | फ़ॉरवर्ड | फिर एक दिन फामली ग्रुप में एक रील फोवर्ड होती है | फिर एक दिन फामिली गूप में एक रील फौवर्ड होती है। |  |
| L7 | `btk_L7_t2` | script | 1.10 | 4.790 | 24.540 | no (+0.24) | 0.132 / 0.132 | ग्रुप, फ़ॉरवर्ड | फिर एक दिन फामली गुप में एक रील फोवर्ड होती है | फिर एक दिन फामिली गूप में एक रील फौवर्ड होती है। |  |
| L7 | `btk_L7_t2` | script | 1.10t | 4.670 | 24.420 | no (+0.12) | 0.105 / 0.132 | फ़ॉरवर्ड | फिर एक दिन फामली ग्रुप में एक रील फोवर्ड होती है | फिर एक दिन फामिली गूप में एक रील फौवर्ड होती है। |  |
| L8 | `btk_L8_t1` | script | 1.08 | 2.820 | 27.270 | yes | 0.077 / 0.077 | - | सब की नजर ममीपे | सब की नजर ममी पे | **picked** (ASR ok + fits) |
| L8 | `btk_L8_t1` | script | 1.10 | 2.760 | 27.210 | yes | 0.077 / 0.077 | - | सब की नजर ममीपे | सब की नजर ममी पे। |  |
| L9 | `btk_L9_t1` | script | 1.08 | 3.840 | 32.090 | yes | 0.241 / 0.138 | - | अब वो सब को हुड सवन्जाती है हम से बहतर | अब वो सब को खुट संजाती हैं, हम से बहतर। | **picked** (ASR ok + fits) |
| L9 | `btk_L9_t1` | script | 1.10 | 3.780 | 32.030 | yes | 0.138 / 0.138 | - | अब वो सब को खुद संजाती है हमसे बहतर | अब वो सब को खुट संजाती हैं, हम से बहतर। |  |
| L9 | `btk_L9_t2` | script | 1.08 | 3.990 | 32.240 | no (+0.12) | 0.172 / 0.138 | ख़ुद | अब वो सब को खुट समजहाती है हम से बहतर | अब वो सब को खुट सम्जाती हैं, हम से बहतर। |  |
| L9 | `btk_L9_t2` | script | 1.10 | 3.910 | 32.160 | no (+0.04) | 0.172 / 0.069 | ख़ुद | अब वो सब को खुछ समजहाती है हमसे बहतर | अब वो सब को खुट समझाती हैं, हम से बहतर। |  |
| L9 | `btk_L9_t2` | script | 1.10t | 3.780 | 32.030 | yes | 0.172 / 0.069 | ख़ुद | अब वो सब को खुछ समजहाती है हम से बहतर | अब वो सब को खुट समझाती हैं, हम से बहतर। |  |
| L10 | `btk_L10_t1` | script | 1.08 | 1.750 | 34.300 | yes | 0.190 / 0.143 | ग्रुप | इसको फामेली गुरुक में भेजो | इसको फामिली गूप में भेजो। |  |
| L10 | `btk_L10_t1` | script | 1.10 | 1.720 | 34.270 | yes | 0.143 / 0.143 | ग्रुप | इसको फामिली गुरुक में भेजो. | इसको फामिली गूप में भेजो। |  |
| L10 | `btk_L10_t2` | script | 1.08 | 1.800 | 34.350 | yes | 0.143 / 0.238 | - | इसको फामली गुरुप में भेजो | इसको फैमली गूप में भहझो। | **picked** (ASR ok + fits) |
| L10 | `btk_L10_t2` | script | 1.10 | 1.770 | 34.320 | yes | 0.238 / 0.095 | - | इसको फामली गुरुपने भेजो | इसको family group में भहझो। |  |
| L11 | `btk_L11-F_t1` | fallback | 1.06 | 1.370 | 36.270 | yes | 0.000 / 0.000 | - | अब नानी | अब नानी? |  |
| L11 | `btk_L11-F_t1` | fallback | 1.08 | 1.350 | 36.250 | yes | 0.000 / 0.000 | - | अब नानी | अब नानी? |  |
| L11 | `btk_L11-F_t1` | fallback | 1.10 | 1.320 | 36.220 | yes | 0.000 / 0.000 | - | अब नानी | अब नानी? |  |
| L11 | `btk_L11_t1` | script | 1.06 | 1.730 | 36.430 | no (+0.08) | 0.000 / 0.000 | - | अब नानी की बारी | अब नानी की बारी। |  |
| L11 | `btk_L11_t1` | script | 1.08 | 1.700 | 36.400 | no (+0.05) | 0.000 / 0.000 | - | अब नानी की बारी | अब नानी की बारी। |  |
| L11 | `btk_L11_t1` | script | 1.10 | 1.670 | 36.370 | no (+0.02) | 0.083 / 0.000 | - | अब नानी कि बारी | अब नानी की बारी। |  |
| L11 | `btk_L11_t1` | script | 1.10t | 1.670 | 36.370 | no (+0.02) | 0.083 / 0.000 | - | अब नानी कि बारी | अब नानी की बारी। |  |
| L11 | `btk_L11_t2` | script | 1.06 | 1.690 | 36.390 | no (+0.04) | 0.000 / 0.000 | - | अब नानी की बारी | अब नानी की बारी। |  |
| L11 | `btk_L11_t2` | script | 1.08 | 1.660 | 36.360 | no (+0.01) | 0.083 / 0.000 | - | अब नानी कि बारी | अब नानी की बारी। |  |
| L11 | `btk_L11_t2` | script | 1.10 | 1.620 | 36.350 | yes | 0.000 / 0.000 | - | अब नानी की बारी | अब नानी की बारी। | **picked** (ASR ok + fits) |
