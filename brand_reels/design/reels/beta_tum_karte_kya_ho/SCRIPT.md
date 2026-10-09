# SCRIPT · Reel 4 (slot 4) · C02 · "Beta, tum karte kya ho?"

Date 2026-10-08 (re-verified 2026-10-09) · Author: hinglish-scriptwriter · Status: **script v2 (viral gate r1 fixes 4b
+ 5 applied), timings ESTIMATED** (no TTS rendered yet; the pronunciation test take in §6 comes first). 2026-10-09
re-check against the gate, BRIEF r2 and SLATE §4: token parity, word budget, hook length, slot gaps incl. the loop
seam and the number lock all pass (`script.json` → `checks`); no line changed. Machine-readable twin: `script.json`
(same folder, generated from one source table; DEV/ROM token parity, slot gaps incl. the loop seam, word cap, hook
length and w/s limits asserted by the generator).

Binding sources: `SLATE.md` §0, §2, §3.4, §4, §5 → `BRIEF.md` §6.2, §6.3, §6.7, §6.11 → `vo_config.json`. Voice:
Higgsfield preset **Vlad** (`elevenlabs_v4`, voice_id `e5666b9c-99a2-4fac-8b4e-abee078b186d`), Devanagari text,
provider default settings. Narrator = "har editor / hum / aap" (universal POV · har desi ghar): no "main", no fact
about Jawad, his family or his history; "JD" is not voiced in this reel (the end card carries the JD monogram).

Module `beta_tum_karte_kya_ho` · look `gold_hour` · BPM 85.714 (600/7, 21 f/beat, bar 2.8 s) · DUR 36.4 s = 1,092 f ·
splice f84 (2.8 s).

---------------------------------------------------------------------------------------------------------------

## 0. Decisions in this script (changes against BRIEF §6.7, each with its reason)

v2 applies the two viral-gate r1 fixes this role owns (`GATE.md` §8): **fix 5** (hook B line) and **fix 4b** (new loop line L11). Fixes 1, 2, 3 and 4a are picture and sound (creative-director); where they touch the VO they are listed in §9.

| line | BRIEF draft | final | reason |
|---|---|---|---|
| L1B (hook B) | Motion designer? Mummy ke liye: cartoon. (SLATE-locked) | **Mummy ke liye, cartoon.** (v2, gate fix 5) | The locked line is estimated at 3.07-3.19 s after the 1.06-1.10x speed-up for a 2.30 s slot (ends ~3.23 s at 1.08x; even with zero pauses at 1.10x it ends at 2.49 s), past the QA limit 2.45 s and into L2 at 2.95 s. v1 cut it to "Motion designer? Cartoon." (gate hook lab 7/8: it reads the H2 lockup `MOTION DESIGNER / *cartoon?*` word for word and drops Mummy, the main character, from the audio). v2 keeps "Mummy ke liye" and drops "Motion designer", which the lockup already shows: the voice adds who is reading the job title (8/8), 4 words, est. end 1.80 s (1.77-1.83 s across 1.10-1.06x), 0.6 s spare before the f74 cut. Picture unchanged. **Needs the lead's OK (replaces a SLATE-locked line).** |
| L2 | Aur jawab ka translation... | **Jawab ka translation...** | BRIEF fallback: the 4-word line is est. 1.40-1.45 s for a 1.20 s slot (> 0.15 s over); 3 words = 1.20-1.24 s. |
| L3 | Jitna samjhao... utna ulta. | **Jitna samjhao, utna ulta.** | vo_chain keeps a pause after "..." up to 0.9 s; with "..." the line ends ~7.1-7.6 s, on top of the "Cartoon?" bubble_pop at 7.0 (−2 dB, not ducked). A comma beat capped at 0.20 s (`cap=0.2`) ends it at ~6.91 s. The correlative "jitna..., utna..." is naturally said with a comma beat. |
| L4 | सीधा जवाब: | DEV **सीधा जवाब,** (Roman keeps "Seedha jawab:") | The line is a lead-in to card B; a trailing comma asks for a continuation lift, the colon is outside the house punctuation set. |
| L8 | Ab sab ki nazar... Mummy pe. | **Sab ki nazar... Mummy pe.** | The locked L9 three seconds later opens "Ab woh sab ko..."; two "Ab ... sab" openings back to back sound like a loop in the writing. 5 words. |
| L11 (new) | — (BRIEF: no VO after L10; Nani chip only at 35.7) | **Ab Nani ki baari.** / अब नानी की बारी। (gate fix 4b) | A sentence loop: the Nani twist was a 36 px chip for 0.7 s that most viewers miss. L11 starts at 34.90 s (3 f before beat 12.2, where the Nani chip + typing pill now pop, fix 4a), est. end 36.27 s (36.25-36.30 s across 1.10-1.06x) against the gate's hard limit 36.36 s; slot end 36.35 keeps ≥ 0.15 s to L1 (0.10 s) across the seam. No breath tail, so frame 0's bubble `BETA, TUM / *karte kya* / HO?` completes it. Captions hidden (end-card window). Fallback "Ab Nani." |

Locked SLATE lines L1, L5, L7, L9 are verbatim. Totals: **version A 57 words**, version B 54 words (v1: 53 / 49; BRIEF: 55 / 54; gate after fixes 4-5: 57 / 54; QA cap A ≤ 60). Estimated speech at 1.08x: A 22.3 s of 36.4 s (61 %), B 21.5 s: the comedy lives in the bubbles, never pad.

## 1. Hooks (only f0-f83 differ; body from f84 is shared)

| rank | id | status | mechanism | on screen (≤ 6 words) | spoken (Roman) | Devanagari (TTS) | words | est end (1.08x) |
|---|---|---|---|---|---|---|---|---|
| 1 | A | LOCKED (SLATE 3.4), public version | dialogue / scene | `BETA, TUM / *karte kya* / HO?` | Sab se mushkil sawaal client nahi poochta. | सब से मुश्किल सवाल क्लाइंट नहीं पूछता। | 7 | 2.54 s |
| 2 | B | Trial Reel; gate r1 fix 5 wording (replaces a SLATE-locked line: lead's OK needed) | result-first | `MOTION DESIGNER / *cartoon?*` | Mummy ke liye, cartoon. | मम्मी के लिए, कार्टून। | 4 | 1.80 s |
| 3 | C | reserve (not produced) | contrarian | `*client* NAHI, MUMMY` | Sab se mushkil client nahi. Mummy hain. | — | 7 | — |
| 4 | D | reserve (not produced) | relatable callout | `GHAR WALE: *ye karta kya hai?*` | Ghar walon ko aaj tak samajh nahi aaya. | — | 7 | — |

- **Recommended: A** (public). Frame 0 = confused JD + "Mummy" typing pill; the question `BETA, TUM *karte kya* HO?` is legible by f11 (0.367 s) and works muted; VO starts at f3 (0.10 s) and is est. to end at 2.54 s (limit 2.69 s; 2.49-2.58 s across 1.10-1.06x). SLATE fallback if the take runs long: "Yeh sawaal client nahi poochta."
- **A/B alternate: B** (Trial Reel, differs only in f0-f83): result-first, the answer before the question. The lockup shows the job title and Mummy's reading (`MOTION DESIGNER / *cartoon?*`); the voice adds whose reading it is: plain "Mummy ke liye", a short comma beat, then a dry, flat "cartoon" from ~1.39 s, ending ~1.80 s with ~0.67 s of air before the hard cut + notif_ping at 2.467 s. Known cost (gate §3.2): B viewers see the "Motion designer → Cartoon?" gag again at 7.0 s, so judge the A/B on skip rate first. Kept in `script.json` for the record: the SLATE wording as `L1B_SLATE` (cannot fit; generate only as proof) and the v1 wording as `L1B.previous.v1` / `hooks[B].v1_roman`.
- C and D are reserves from the viral panel (§4.2), not produced.

## 2. Story: line table

Caption keyword = `{word}` (serif-italic flame word of the caption chunk). "lockup" = the keyword is already on screen in a designed lockup, so the caption line has none.

| id | ver | part | slot (s) | onset bar.beat | Roman caption track (house spelling) | Devanagari TTS (Vlad, elevenlabs_v4) | words | delivery | on screen at that moment | captions |
|---|---|---|---|---|---|---|---|---|---|---|
| L1 | A | Hook | 0.10-2.69 | 0.0+3f | Sab se mushkil sawaal client nahi poochta. | सब से मुश्किल सवाल क्लाइंट नहीं पूछता। | 7 | plain statement, no pause, flat landing on "poochta" | Mummy bubble: BETA, TUM / *karte kya* / HO? | shown (CAP_HOOK, upper band; no caption keyword: lockup H1 *karte kya* is on screen) |
| L1B | B (gate fix 5) | Hook (Trial) | 0.10-2.40 | 0.0+3f | Mummy ke liye, cartoon. | मम्मी के लिए, कार्टून। | 4 | plain on "Mummy ke liye", a short comma beat, then a dry, flat "cartoon" (final fall, no smile) | MOTION DESIGNER / *cartoon?* + "Mummy translate" card, MOTION wobbling | hidden (hook B has no captions) |
| L2 | A+B | Turn | 2.95-4.15 | 1.0+4f | Jawab ka {translation}... | जवाब का ट्रांसलेशन... | 3 | trails off on "translation..." so the pop at 4.2 answers it | "Mummy translate" card; "Video editor" types 3.27-3.87; "Shaadi wala?" pops 4.2 | shown |
| L3 | A+B | Turn | 5.10-6.95 | 1.3+6f | Jitna samjhao, utna {ulta}. | जितना समझाओ, उतना उल्टा। | 4 | dry; a short comma beat, "ulta" flat and final (ends before the "Cartoon?" pop at 7.0) | "Happy Wedding" parody (4.9-6.3), then "Motion designer" types (6.33-6.83) | shown |
| L4 | A+B | Escalation (re-hook 1) | 10.95-11.70 | 3.3+13f | {Seedha} jawab: | सीधा जवाब, | 2 | determined lead-in with a slight lift (not a final fall); "jawab" rides the M3 swipe at 11.2 | M3 swipe 11.2; card B pre-filled "Brands ke liye cinematic reels"; killer bubble 12.6 | shown |
| L5 | A+B | Escalation | 14.15-16.15 | 5.0+4f | Phir... {haar} maan li. | फिर... हार मान ली। | 4 | "Phir..." held up to 0.6 s, then "haar maan li" soft and falling | JD suit_neutral under "Achha. / Naukri kab lagegi?" | shown |
| L6 | A+B | Escalation (time skip) | 16.95-17.95 | 6.0+4f | Kuch mahine baad... | कुछ महीने बाद... | 3 | soft, unhurried: time passing | chip "Kuch mahine baad"; phone face-down buzzes | hidden (chip "Kuch mahine baad" shows the words) |
| L7 | A+B | Escalation (re-hook 2) | 19.75-24.27 | 7.0+4f | Phir ek din family group mein... ek {reel} forward hoti hai. | फिर एक दिन फ़ैमिली ग्रुप में... एक रील फ़ॉरवर्ड होती है। | 11 | storyteller, rising; brighten on "ek reel" | "Khandaan" floods 19.6; forwarded reel bubble lands 21.7 | shown |
| L8 | A+B | Escalation (suspense) | 24.45-27.12 | 8.2+20f | Sab ki {nazar}... Mummy pe. | सब की नज़र... मम्मी पे। | 5 | hushed, leaning in; "Mummy pe" lands just after the typing pill (25.2) | "Kamaal!", "Wah!", then "Mummy is typing" 25.2 (stops 25.9, resumes 26.6) | shown |
| L9 | A+B | Payoff | 28.25-31.97 | 10.0+8f | Ab woh sab ko khud samjhaati hain... humse behtar. | अब वो सब को ख़ुद समझाती हैं... हमसे बेहतर। | 9 | warm; a small smile on "humse behtar" | Mummy bubble MERA BETA / *cinema* / BANATA HAI; JD hand-on-chest from 28.7 | shown (no caption keyword: lockup P1 *cinema* is on screen) |
| L10 | A+B | CTA | 32.55-34.40 | 11.2+10f | Isko family group mein bhejo. | इसको फ़ैमिली ग्रुप में भेजो। | 5 | friendly, not salesy; "bhejo" clear and aspirated | end card GROUP MEIN / *bhejo* + JD + @jawad_mp4 (settles 34.03); then L11 over the Nani pill (35.0) | hidden (end card GROUP MEIN / *bhejo*) |
| L11 | A+B | Loop (button) | 34.90-36.35 | 12.1+18f | Ab Nani ki baari. | अब नानी की बारी। | 4 | light and knowing, a small smile on "Nani"; "baari" falls and stops dead: no breath, no tail (frame 0's bubble completes the sentence) | end card GROUP MEIN / *bhejo* settled; "Nani" chip + typing pill pop at 35.0 in the f0 pill position (gate fix 4a, creative-director) and carry across the c12 cut (35.7) to frame 0 | hidden (inside the end-card hide window 32.2-36.4; the "Nani" chip + typing pill show it) |

Arc: **hook** (the question, 0-2.8) → **turn** (the translate game, three wrong genres, 2.8-8.4) → **re-hook 1** at 11.2 ("Seedha jawab:" + the swipe) → the killer bubble "Achha. Naukri kab lagegi?" at 12.6 in silence (no VO, by design) → "Phir... haar maan li." → time skip → **re-hook 2** at 19.6 (family group floods, "...ek reel forward hoti hai.") → suspense ("Sab ki nazar... Mummy pe." over the typing dots) → drop-out 27.3-28.0 → **payoff** 28.0 (bubble MERA BETA *cinema* BANATA HAI; VO from 28.25, 250 ms clear of the hit) → **CTA** 32.55 "Isko family group mein bhejo." → **loop button** 34.90 "Ab Nani ki baari." as the Nani chip + typing pill pop over the settled end card (35.0) and carry across the c12 cut (35.7) → frame 0's bubble completes her question (`BETA, TUM *karte kya* HO?`) and L1 starts again, so the last spoken line hands straight to the hook and sending the reel to the group is literally what restarts it. (Version B loops into the card hook instead: accepted for a Trial, BRIEF §6.3.)

## 3. Timing table (ESTIMATED: no take exists yet)

Rate model: words / 2.7 w/s before the speed-up, cross-checked by syllables / 4.56 syl/s (the larger wins). Measured on `vlad_v4_r1_DEV.mp3: 53 words, 83 syllables, 22.27 s incl. 10 pauses (4.05 s) -> 2.38 words/s gross, 2.91 words/s and 4.56 syllables/s net (faster-whisper small)`. Pauses: "," 0.30 s, "?" 0.45 s, "..." 0.45 s (L5 "Phir..." 0.60 s), as capped by `vo_chain` (`cap` / `keep_cap` per line in the JSON). Rule: raw = max(words / 2.7, syllables / 4.56) + mid-line pauses; final = raw / speed; overrun > 0.15 s => cut words (BRIEF 6.7).

| line | slot t0-t1 (s) | slot len | words | syl | raw W / S (s) | at 1.06 / 1.08 / 1.10x (s) | est end @1.08 | w/s @1.08 | keyword @ t (nearest grid) | fit | gap to next |
|---|---|---|---|---|---|---|---|---|---|---|---|
| L1 | 0.10-2.69 | 2.59 | 7 | 12 | 2.59 / 2.63 | 2.48 / 2.44 / 2.39 | 2.54 | 2.87 | lockup / card *karte kya* | ok | 0.26 |
| L1B | 0.10-2.40 | 2.30 | 4 | 7 | 1.78 / 1.84 | 1.73 / 1.70 / 1.67 | 1.80 | 2.35 | lockup / card *cartoon?* | ok | 0.55 |
| L1B_SLATE | 0.10-2.40 | 2.30 | 6 | 12 | 2.97 / 3.38 | 3.19 / 3.13 / 3.07 | 3.23 | 1.92 | lockup / card *cartoon?* | OVER | 0.55 |
| L2 | 2.95-4.15 | 1.20 | 3 | 6 | 1.11 / 1.32 | 1.24 / 1.22 / 1.20 | 4.17 | 2.46 | *translation* 3.56 (beat 1.1, +0.06 s) | ok | 0.95 |
| L3 | 5.10-6.95 | 1.85 | 4 | 8 | 1.68 / 1.95 | 1.84 / 1.81 / 1.78 | 6.91 | 2.21 | *ulta* 6.50 (8th 2.1+11f, -0.17 s) | ok | 4.00 |
| L4 | 10.95-11.70 | 0.75 | 2 | 4 | 0.74 / 0.88 | 0.83 / 0.81 / 0.80 | 11.76 | 2.46 | *Seedha* 10.95 (8th 3.3+11f, +0.08 s) | ok (within the 0.15 s tolerance) | 2.45 |
| L5 | 14.15-16.15 | 2.00 | 4 | 4 | 2.08 / 1.48 | 1.96 / 1.93 / 1.89 | 16.08 | 2.08 | *haar* 15.05 (8th 5.1+11f, -0.02 s) | ok | 0.80 |
| L6 | 16.95-17.95 | 1.00 | 3 | 5 | 1.11 / 1.10 | 1.05 / 1.03 / 1.01 | 17.98 | 2.92 | — (captions hidden) | ok | 1.80 |
| L7 | 19.75-24.27 | 4.52 | 11 | 15 | 4.52 / 3.74 | 4.27 / 4.19 / 4.11 | 23.94 | 2.63 | *reel* 22.43 (beat 8.0, +0.03 s) | ok | 0.18 |
| L8 | 24.45-27.12 | 2.67 | 5 | 7 | 2.30 / 1.99 | 2.17 / 2.13 / 2.09 | 26.58 | 2.35 | *nazar* 24.94 (8th 8.3+11f, +0.07 s) | ok | 1.13 |
| L9 | 28.25-31.97 | 3.72 | 9 | 13 | 3.78 / 3.30 | 3.57 / 3.50 / 3.44 | 31.75 | 2.57 | lockup / card *cinema* | ok | 0.58 |
| L10 | 32.55-34.40 | 1.85 | 5 | 9 | 1.85 / 1.97 | 1.86 / 1.83 / 1.79 | 34.38 | 2.74 | lockup / card *bhejo* | ok | 0.50 |
| L11 | 34.90-36.35 | 1.45 | 4 | 6 | 1.48 / 1.32 | 1.40 / 1.37 / 1.35 | 36.27 | 2.92 | — (captions hidden) | ok (tight: hard end 36.36) | 0.15 |

- No line is above 3.2 w/s (max 2.92, L6 and L11). Every gap between lines is ≥ 0.15 s (min 0.18 s, L7 → L8); across the loop seam L11 → L1 the gap is 0.15 s by slot (36.35 → 36.4 + 0.10) and 0.23 s at the 1.08x estimate.
- End card (32.2-36.4): L10 (CTA) 32.55-34.40, 0.50 s of air (34.40-34.90, lets "bhejo" land before the Nani pop), then L11 34.90-36.35. The settled CTA hold (34.03-36.04, ≥ 1.5 s) is unchanged in picture; v1 had 2.0 s without speech here, v2 trades it for the loop button (gate fix 4b).
- Tight lines (within ±0.1 s of the slot; decide on the measured take): L2, L3, L4, L6, L10, L11. Remedies in order: speed up to 1.10x (never beyond), then the line's `fallback` in the JSON (L11: onset earlier, never before 34.70, then "Ab Nani."). Never move a picture event.
- L6 now also gates a picture event: the "Kuch mahine baad" chip gives way to the `Khandaan · 12` count pill when L6 ends (gate fix 1, ~18.0 s). L6 est. end 17.98 s at 1.08x (18.00 s at 1.06x): the creative-director places the swap at the measured end + 1 frame, or L6 is processed at 1.10x.
- Long VO silences are designed, not dead air: 6.95-10.95 (gags 2-3: boings, punch-in, stamp slam), 11.70-14.15 (the killer bubble lands in music silence at 12.6), 16.15-16.95 and 17.95-19.75 (buzzes, pings, the count pill rolls 12 → 47 → 99+).
- After the takes: measure each processed line (`ffprobe` duration + faster-whisper word onsets), place its first voiced onset at `start_target` ± 1 frame, and replace this table with measured values.

## 4. Token table (caption token ↔ TTS token, 1:1 in order)

`vo_chain` splits both texts on whitespace and pairs token i with token i (it raises if the counts differ); the ROM string for it is `rom_chain` (keyword marked `*word`). faster-whisper may merge or split words (list below); `vo_chain.align_tokens` handles 1:2 / 2:1 moves and `norm_dev` strips nuktas before matching.

| line | i | roman | tts | keyword |
|---|---|---|---|---|
| L1 | 0 | Sab | सब |  |
| L1 | 1 | se | से |  |
| L1 | 2 | mushkil | मुश्किल |  |
| L1 | 3 | sawaal | सवाल |  |
| L1 | 4 | client | क्लाइंट |  |
| L1 | 5 | nahi | नहीं |  |
| L1 | 6 | poochta. | पूछता। |  |
| L1B | 0 | Mummy | मम्मी |  |
| L1B | 1 | ke | के |  |
| L1B | 2 | liye, | लिए, |  |
| L1B | 3 | cartoon. | कार्टून। |  |
| L2 | 0 | Jawab | जवाब |  |
| L2 | 1 | ka | का |  |
| L2 | 2 | translation... | ट्रांसलेशन... | yes |
| L3 | 0 | Jitna | जितना |  |
| L3 | 1 | samjhao, | समझाओ, |  |
| L3 | 2 | utna | उतना |  |
| L3 | 3 | ulta. | उल्टा। | yes |
| L4 | 0 | Seedha | सीधा | yes |
| L4 | 1 | jawab: | जवाब, |  |
| L5 | 0 | Phir... | फिर... |  |
| L5 | 1 | haar | हार | yes |
| L5 | 2 | maan | मान |  |
| L5 | 3 | li. | ली। |  |
| L6 | 0 | Kuch | कुछ |  |
| L6 | 1 | mahine | महीने |  |
| L6 | 2 | baad... | बाद... |  |
| L7 | 0 | Phir | फिर |  |
| L7 | 1 | ek | एक |  |
| L7 | 2 | din | दिन |  |
| L7 | 3 | family | फ़ैमिली |  |
| L7 | 4 | group | ग्रुप |  |
| L7 | 5 | mein... | में... |  |
| L7 | 6 | ek | एक |  |
| L7 | 7 | reel | रील | yes |
| L7 | 8 | forward | फ़ॉरवर्ड |  |
| L7 | 9 | hoti | होती |  |
| L7 | 10 | hai. | है। |  |
| L8 | 0 | Sab | सब |  |
| L8 | 1 | ki | की |  |
| L8 | 2 | nazar... | नज़र... | yes |
| L8 | 3 | Mummy | मम्मी |  |
| L8 | 4 | pe. | पे। |  |
| L9 | 0 | Ab | अब |  |
| L9 | 1 | woh | वो |  |
| L9 | 2 | sab | सब |  |
| L9 | 3 | ko | को |  |
| L9 | 4 | khud | ख़ुद |  |
| L9 | 5 | samjhaati | समझाती |  |
| L9 | 6 | hain... | हैं... |  |
| L9 | 7 | humse | हमसे |  |
| L9 | 8 | behtar. | बेहतर। |  |
| L10 | 0 | Isko | इसको |  |
| L10 | 1 | family | फ़ैमिली |  |
| L10 | 2 | group | ग्रुप |  |
| L10 | 3 | mein | में |  |
| L10 | 4 | bhejo. | भेजो। |  |
| L11 | 0 | Ab | अब |  |
| L11 | 1 | Nani | नानी |  |
| L11 | 2 | ki | की |  |
| L11 | 3 | baari. | बारी। |  |

Total: 61 tokens (version A 57 + hook B 4; `L1B_SLATE` is reference only). Expected ASR merges/splits: सब से -> सबसे (L1: 2 roman tokens, 1 heard word); हमसे -> हम से (L9: split); इसको -> इस को (L10: split); वो -> वह (L9); पे -> पर (L8); nukta dropped by whisper (फैमिली, फॉरवर्ड, खुद, नजर): vo_chain.norm_dev strips it; लिए -> लिये (L1B: spelling variant, same skeleton in vo_chain.skel); मम्मी -> मामी / ममी (L1B, L8: ASR confusion; check by ear, never "fix" the caption to Mami); बारी -> भारी (L11: check).
Display: snake_captions keeps ? ! ... and drops , . and the danda; "translation..." chunk alone (602.6 px at 128 px key size, <= 780).

Caption keywords: L2 *translation*, L3 *ulta*, L4 *Seedha*, L5 *haar*, L7 *reel*, L8 *nazar* (one per line, ≤ 12 characters, ≤ 2 per scene: S8 has *reel* + *nazar*). None on L1 (lockup H1 *karte kya*) and L9 (lockup P1 *cinema*). Hidden: L6 (16.85-18.2, the chip shows it), L10 and L11 (32.2-36.4, the end card shows `GROUP MEIN / *bhejo*`, the Nani chip + pill show L11), hook B (no captions f0-f83). Gate note 7 for the caption-designer: the chunks "translation..." (L2, est end 4.17) and "utna *ulta*" (L3) must be gone before "Shaadi wala?" pops at 4.20 and "Cartoon?" at 7.00: add hide windows from 4.20 and from 7.00 on the real words.json (L3 est end 6.91).

## 5. TTS spelling decisions (Devanagari for ElevenLabs v4 Hindi)

- **Nuktas where Urdu or English needs them:** फ़ैमिली, फ़ॉरवर्ड (English f), नज़र (z), ख़ुद (kh). None on जवाब, सवाल, मुश्किल, बेहतर, नानी, बारी (no nukta sound) or on फिर (native aspirated "phir", said that way on both sides). डिज़ाइनर left the VO with the v1 hook B line.
- **English loans in Devanagari phonetics:** क्लाइंट, कार्टून, ट्रांसलेशन, फ़ैमिली ग्रुप, रील, फ़ॉरवर्ड. No Latin script in any TTS line (no audition has shown Vlad reads Latin better for these words).
- **Spoken forms, not book forms:** वो (not वह), पे (not पर), हमसे, इसको, सब से (two tokens to match the Roman "Sab se"), के लिए (not के लिये), मम्मी / नानी (family words as said at home on both sides).
- **Punctuation = prosody:** "..." only where a long beat is wanted (L5, L7, L8, L9 mid-line; L2, L6 trailing off); "," for short beats (L3 capped 0.2 s, L1B's beat before "cartoon" capped 0.3 s) and for L4's lead-in lift; "।" ends a sentence (L11: a dead stop, no trailing "..." so no breath tail before the seam). No "?" is left in the VO (v1's was in the old hook B). No colons, brackets, emoji, digits, symbols or tags in any TTS text.
- No numbers or symbols occur in this script (SLATE §4 spoken-number lock for C02: none). The only numeral token is
  एक "ek", twice in the SLATE-locked L7 ("ek din", "ek reel" = one day / a reel): the indefinite article, not a count.
  The `Khandaan · 12 → 47 → 99+` count pill of gate fix 1 is picture only and is never spoken. "JD" is not voiced.
- Unicode NFC (nukta as the combining U+093C); the JSON `dev` and `tts` fields are identical.

## 6. Pronunciation-risk words: test these first

Evidence from the Vlad audition (`hf_dl/vlad/vlad_v4_r1_DEV.mp3`, faster-whisper small): भाई → "बाई" (bh lost its aspiration), क्लाइंट → "ख्लाईट", लाइफ़ → "लाइप" (f → p), डेडलाइन → "देडलाईन" (retroflex → dental), मोशन → "मोशिन", सच → "सज". Whisper errors are partly the ASR's own, so ranks 1-6 need a human listen, not only CER.

| rank | word | Roman | line(s) | why it is at risk | fallback spelling / swap |
|---|---|---|---|---|---|
| 1 | क्लाइंट | client | L1 | hook A, first 3 s; the Vlad audition was heard as "ख्लाईट" (aspirated k, nasal + t blurred) | क्लायंट |
| 2 | मम्मी | Mummy | L1B, L8 | now the FIRST word of hook B and the main character; stress must be on the first syllable (MUM-mee), not "mam-MEE"; whisper may write मामी (a different relative), so judge it by ear | ममी |
| 3 | भेजो | bhejo | L10 | the CTA word; audition de-aspirated भ ("भाई" heard as "बाई"), so it may come out "bejo" | retake with stability 0.55; else accept (the end card spells it) |
| 4 | ट्रांसलेशन | translation | L2 | caption keyword; retroflex cluster ट्र may go dental | ट्रैन्सलेशन |
| 5 | फ़ैमिली ग्रुप | family group | L7, L10 | said twice; audition turned फ़ into प at "लाइफ़" ("लाइप") | फ़ेमिली ग्रुप |
| 6 | कार्टून | Cartoon | L1B | hook B punchline, now the line's last word after the comma beat; retroflex ट may go dental; it must land dry and flat (final fall) | कार्टून with stability 0.55 |
| 7 | फ़ॉरवर्ड | forward | L7 | word-initial फ़ (see rank 5) and the r cluster | फ़ॉर्वर्ड |
| 8 | उल्टा | ulta | L3 | caption keyword with a retroflex cluster ल्ट | swap the word: "Jitna samjhao, utna galat." (ग़लत, keyword galat) |
| 9 | सीधा | Seedha | L4 | caption keyword; aspirated ध may flatten to "seeda" | accept (caption spells it) or "Sach bataya:" (सच बताया,) |
| 10 | पूछता | poochta | L1 | hook A last word; audition voiced च ("सच" heard as "सज") | retake once (no better spelling exists) |
| 11 | ख़ुद / नज़र | khud / nazar | L9, L8 | nukta fricatives (Urdu-natural); low risk: check they are not over-hissed | खुद / नजर (no nukta) |
| 12 | बेहतर | behtar | L9 | last word of the payoff line; "eh" may split into "be-ha-tar" | retake once (बेहतर is the standard spelling) |
| 13 | नानी / बारी | Nani / baari | L11 | low risk (long vowels, no retroflex); check बारी is not heard as भारी ("bhaari", heavy) and that the take stops dead after it (no breath: the line ends 0.05-0.2 s before the loop seam) | retake once; else the fallback "Ab Nani." |

**Test take (one request, 289 characters, roughly 1.4 credits at the vo_config rate; v2 text: hook B line and L11 in, "मोशन डिज़ाइनर" out):** every word above in its real line, read as one paragraph, so the same take also gives a first rate measurement per line:

```
सब से मुश्किल सवाल क्लाइंट नहीं पूछता। मम्मी के लिए, कार्टून। जवाब का ट्रांसलेशन... जितना समझाओ, उतना उल्टा। सीधा जवाब। फिर एक दिन फ़ैमिली ग्रुप में... एक रील फ़ॉरवर्ड होती है। सब की नज़र... मम्मी पे। अब वो सब को ख़ुद समझाती हैं... हमसे बेहतर। इसको फ़ैमिली ग्रुप में भेजो। अब नानी की बारी।
```

Check: faster-whisper (hi) on the take; listen to ranks 1-6 by ear; then measure each line's duration against its slot. A spelling fallback goes into the final run only if the test shows the problem. Gate condition (note 9): L1 is generated only after क्लाइंट passes ASR **and** one human listen (fallback क्लायंट, then "Yeh sawaal client nahi poochta.").

## 7. Generation and assembly (for the lead and the VO assembler)

- **Takes:** 12 requests, one per line: L1, L1B, L2-L11 (`dev` field as the prompt, Vlad preset, default settings). Characters: version A 292 + L1B 22 = 314. `L1B_SLATE` (37 characters) only if the lead wants proof that the locked hook B cannot fit. `jobs_wait`, never a blind resubmit; BRIEF budget ≤ 30 credits incl. one retake round.
- **Processing:** `vo_chain.process(take, dev, rom_chain, speed=1.08, cap=<vo_chain.cap>, keep_cap=<vo_chain.keep_cap>)` through the Python API (the CLI has no cap/keep_cap flags): L3 `cap=0.2`; L1B `cap=0.3` (the comma beat); L5 `keep_cap=0.6`; L7, L8, L9 `keep_cap=0.45` (the 0.9 s default would let the "..." beats run long); L11 at the slowest of 1.06-1.10x whose processed take is ≤ 1.45 s (34.90 → 36.35), tail trimmed to 40 ms (check `tail_trim` and listen: no breath after "baari"); speed 1.06-1.10x only.
- **Placement:** first voiced onset at `start_target` ± 1 frame; hard limits L1 end ≤ 2.69 s (QA ≤ 2.75), L1B end ≤ 2.45 s, L11 onset 34.90 (f1047, never later than 34.95) and end ≤ 36.35 (gate hard limit 36.36; nothing of L11 may cross 36.4), every other line ≤ `end_target` + 0.15 s; VO A = L1 + L2-L11, VO B = L1B + L2-L11 (identical from 2.8 s). Loop check: play the last 2 s of VO A into its first 3 s: "...Ab Nani ki baari. | Sab se mushkil sawaal..." with 0.15-0.30 s between them.
- **Words file:** reel-time `beta_tum_karte_kya_ho.words.json` from the per-line words (ROM tokens, keyword flags from `*`), then `CAP_HOOK` / `CAP_BODY` `check() == []` (BRIEF §6.11).

## 8. Self-check

- [x] Hook A spoken from f3 (0.10 s), est. end 2.54 s; the bubble text carries it muted; 7 spoken words (≤ 7). Hook B spoken from f3, 4 words, est. end 1.80 s (≤ 2.40 slot, ≤ 2.45 QA); its lockup carries it muted.
- [x] Every line traces to SLATE §3.4 or BRIEF §6.7; universal POV; no first-person "main"; no fact about Jawad (no `[VERIFY]` item needed); CTA "Isko family group mein bhejo." is true (sending is a real action, no automation implied). L11 and the new L1B are inside the labelled POV skit (Nani and Mummy are generic, never Jawad's family).
- [x] Both sides of the border: sawaal, jawab, mushkil, samjhao, ulta, seedha, haar, mahine, nazar, khud, samjhaati, behtar, bhejo, Mummy, Nani, "ke liye", "ki baari", family group, reel are daily words in Lahore and in Delhi; nothing Sanskritised or heavily Persianised; no religion, politics, region, rivalry or stereotype.
- [x] House spelling (prior SRT): hai, hain, nahi, mein, woh, phir, kuch, sab; "baari" (turn) spelled with aa so it never reads as the house "bari" (big); English words in English; sentence case.
- [x] Number lock (SLATE §4, C02: none): no number in any VO line (L7's locked "ek" is the indefinite article); the
  fix-1 count pill is picture only.
- [x] Token table complete: 61 tokens, DEV count = ROM count per line (asserted); ≤ 1 caption keyword per line.
- [x] Word budget: A 57 words (≤ 60), B 54, in ~22.3 s / 21.5 s of speech at 1.08x (61 % of the reel), every line ≤ 3.2 w/s; the loop line L11 hands to frame 0's bubble and L1.
- [x] Measured timings: done 2026-10-09, see §10 and `VO_TIMING.md` (the §3 table stays as the estimate it was).

## 9. Open questions and flags for the lead

1. **Hook B wording** ("Mummy ke liye, cartoon.", gate fix 5, instead of the SLATE-locked "Motion designer? Mummy ke liye: cartoon."): needs the lead's OK. The locked line cannot fit (est. end ~3.2 s, after L2 starts at 2.95 s). If the lead keeps "Motion designer" in the audio, v1 "Motion designer? Cartoon." is the fallback (7/8).
1b. **L11 on the end card:** the CTA is still spoken once (L10) and held on screen ≥ 1.5 s, but the last words of the reel are now the loop button, and the end card has 0.5 s without speech instead of 2.0 s (gate's trade). On the loop the voice says "Nani" and frame 0's chip says "Mummy" (BRIEF §10.1: the seam differs only by the chip word): accepted unless the creative-director wants it otherwise.
1c. **VO touch-points of the picture fixes:** fix 1: the chip → `Khandaan · 12` swap waits for L6's measured end (§3). Fix 3: the enlarged reel thumb (this reel's cover, with the H1 lockup inside) is on screen under L7 "ek *reel*" (~22.4 s): add the thumb rect to `AVOID` and count it in the 2-block budget. Fix 4a: the Nani notif_ping at 35.0 lands on "Ab" and the reverse_swell (35.6-36.4) plus the 35.7 tin sit under "ki baari": keep them ≥ 6 LU under the VO.
2. **AI label:** synthetic voice in every line, so Meta "AI info" ON (SLATE §7.1 default).
3. **"Mummy" vs "Ammi":** Mummy kept (cross-border default); Jawad's call. It is now also hook B's first word; with "Ammi" the line becomes "Ammi ke liye, cartoon." / अम्मी के लिए, कार्टून। (same syllables and timing).
4. **Nobody can judge pronunciation by ear in the pipeline:** whisper CER flags gross errors only; ranks 1-6 of §6 (incl. मम्मी as hook B's first word) need one human listen (Jawad or the lead) before the final run.
5. **L4 as a 2-word take** may come out with a final fall; if so retake once with "सीधा जवाब:" or fold it into the swipe as silence (the card B text says the honest answer anyway).
6. Words that may still sound wrong after the test: भेजो (de-aspiration), ट्रांसलेशन / कार्टून (dental instead of retroflex), फ़ैमिली (f → p), मम्मी (stress), बारी (heard as भारी). Fallbacks are in §6 and in each line's `fallback`.
7. **Twins out of sync (not this role's files; creative-director):** BRIEF r2 §6.7 still lists L1B as the SLATE line,
   has no L11 row and says "Total A = 55 words" and "11 takes"; `packet.yaml` line 376 has the SLATE L1B, no L11 row
   and `total_words: {A: 55, B: 54}`. This script is the source: A 57 / B 54, 12 takes (L1, L1B, L2-L11). BRIEF §6.2
   and §6.4 place L11 "from ≈ 34.95"; the script uses 34.90 (f1047), because a 34.95 onset ends at 36.35 s at 1.06x
   (0.01 s under the 36.36 s hard limit).

## 10. Recorded VO (measured 2026-10-09; `VO_TIMING.md` has every number)

The VO is recorded (Vlad, `elevenlabs_v4`, 32 line takes incl. retakes and variants + 11 pronunciation carriers (the L1 fallback take is carrier P1), 10.81 credits) and
assembled: `workspace/jawad_reels/beta_tum_karte_kya_ho/vo/vo_stem.wav` (= `beta_tum_karte_kya_ho_vo_A.wav`),
`beta_tum_karte_kya_ho_vo_B.wav`, `words.json` / `words_B.json`. `script.json` → `vo_final` holds the recorded text per
line; where it differs from §2 it wins for the VO, the captions and QA.

**Why text moved:** isolated Vlad lines run 25-40 % slower than the §3 rate model (L1 measured 3.28 s of voice for a 2.59 s
slot; L3 2.52-2.62 s for 1.85 s), so the BRIEF 6.7 ladder (1.10x, tighter pause caps, then the fallbacks) was applied:

| line | recorded (Roman) | change | status |
|---|---|---|---|
| L1 | Yeh sawaal client nahi poochta. | SLATE 3.4 fallback (5 words) | needs the lead's OK (SLATE-locked line; the locked wording cannot fit) |
| L1B | Mummy ke liye, cartoon. | TTS spelling कारटून (both ASR models heard काटून, r dropped) | words unchanged |
| L3 | Jitna samjhao, *ulta*. | word cut: "utna" dropped (4 words could not fit; ends 7.09) | needs the lead's OK (not locked; "Samjhao toh ulta." was tried: it came out as a question) |
| L5 | Phir... *haar* maan li. | TTS "फिर," instead of "फिर..." ("Phir..." was drawn to 1.0 s) | words unchanged |
| L6 | Mahine baad... | script.json fallback ("Kuch" dropped; the chip still reads "Kuch mahine baad") | ends 18.11 (0.01 s past the tolerance) |
| L7 | Phir ek din family group mein... ek *reel* forward hoti hai. | TTS comma beat instead of "..." + spelling फ़ोरवर्ड | words unchanged (SLATE-locked wording kept) |
| all | client | TTS spelling क्लायंट (carrier P0 with क्लाइंट was heard प्लैंट / प्लाइंट by both models) | words unchanged |

**Still over the slot after all retakes (reported, picture not moved):** L2 ends 4.37 (target 4.15, +0.22; 3 takes all
1.42-1.47 s), L4 ends 12.00 (target 11.70, +0.30; 2 takes), L6 18.11 (+0.16). L11 starts 34.73 (SCRIPT 7 onset ladder)
and ends 36.35, loop seam 0.15 s. **Human listen before publishing:** "forward" is non-rhotic in every take and spelling
(4 takes, 3 spellings), client (gate note 9), Mummy stress, bhejo.

