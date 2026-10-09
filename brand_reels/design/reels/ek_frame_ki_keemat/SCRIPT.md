# SCRIPT: Reel 3 · C08 · Ek Frame ki Keemat (VO + caption tokens)

Date 2026-10-08 · Author: hinglish-scriptwriter · Status: **v2 after the viral-strategist script gate r1 (verdict FIX, `GATE.md`): fix 4 applied, the script half of fix 5 applied pending the lead (T3 on HOLD); no TTS rendered yet** (every time below is an ESTIMATE from a syllable model calibrated on the Vlad casting take; re-measure on the real takes).
Machine-readable twin: `script.json` (same folder): lines, 1:1 token table, takes, anchors, fit ladder, risks.

Binding sources: `SLATE.md` §0, §2, §3.3, §4, §5; `BRIEF.md` §2, §5, §6, §8, §9, §15 (this reel); house spelling from `workspace/brand_reels/prior/captions_roman_urdu.srt`; voice recipe `pipeline/jawad_reels/vo_config.json`; processing `vo_chain.py`.

Voice: Higgsfield preset **Vlad** (`e5666b9c-99a2-4fac-8b4e-abee078b186d`), `elevenlabs_v4`, Devanagari text exactly as in the DEV column, provider-default settings. Narrator: "aap" (the viewer, then the friend the reel is sent to) + third person ("banane wala"); never "main / meri / mera"; JD is not voiced in this reel: the "Is frame mein JD chhupa hai. Mila?" prompt is post copy (pinned first comment + IG caption line 2, gate r1 fix 3) and the 28.2 s glint of the hidden JD is picture only.

---------------------------------------------------------------------------------------------------------------

## 0. At a glance

| item | value |
|---|---|
| spoken words | **A 62**, B 62 (V1A and V1B are 6 words each); syllables A 98, B 95 |
| lead model (2.7 words/s raw, before the speed-up) | 22.96 s raw speech; 21.66 s at 1.06x; 20.88 s at 1.10x |
| syllable model (calibrated, A) | speech only 22.50 s raw / 21.23 s at 1.06 / 20.83 s at 1.08 / 20.45 s at 1.10; with the holds inside lines 26.85 s raw, 24.86 s at 1.08 |
| placed VO (A, at 1.08) | 23.64 s of line spans inside 33.6 s; first word 0.10 s, last word ends 32.82 s, VO-free tail 0.78 s |
| takes | 5 (T1 = pronunciation test AND production), 25-137 characters each: <= 2.5 credits per take (vo_config: ~2.5 per ~520-char take), <= 12.5 total, cap 20 incl. retakes (BRIEF §9); T1, T2, T4, T5 GO now, T3 HOLD (C7) |
| tightest fits (est, at 1.08) | V1A ends 2.37 (hard 2.70) · V5 ends 15.70 (target 15.79) · V9 + V10 end 32.82 (card exit 33.24) |
| needs lead OK | **C7 V10 "usko" + card `USKO YEH / bhejo` (gate fix 5; T3 waits for it)** · C1 V2 back to the SLATE wording · C2 V8 "ke" (grammar) · C3 V9 "Keemat..." (C1-C5 approved by the viral gate; see §9) |
| number lock (SLATE §4) | the DEV strings contain only these number words: एक (V1B V2 V5 V6), तीन (V1B V7 V8), सौ (V1B V7), साठ (V1B V7), बारह (V2), तीस (V6) ("एक" = one frame / one second / one more layer); spoken: baarah (12), tees (30), teen sau saath (360), teen (3); nothing else (scanned) |

**v2: viral gate r1 fixes** (`GATE.md` §7; scores Hook 8, Share 7, Truth pass, Brand 9):

| fix | owner | what | in this script |
|---|---|---|---|
| 1 | creative-director | f0 trailer_hit -> impact_soft -8 dB (cue-level dur=0.25) | no script text change; the loop note now says impact_soft |
| 2 | creative-director | 14.6-16.0 push toward pane 03 + 15.0-15.8 rack focus | no script change; V5 still ends est 15.70, caption C1 last exit est 16.15 (< 16.25); the C1 bbox check against the pushed frame top edge is the creative-director's |
| 3 | creative-director | 28.2 s JD glint in layer 03 + pinned comment / caption line 2 | no VO change; narrator and caption notes updated (the glint lands on "banane") |
| 4 | hinglish-scriptwriter | V5 keywords *layer...* + *zinda* | APPLIED: lines[V5].roman_marked / caption_keyword, tokens V5 i=2 keyword, takes[T1].rom, C6; chunks C1 `Aur ek *layer...* / jiske bina / frame *zinda* / nahi lagta` |
| 5 | creative-director + hinglish-scriptwriter (needs the lead) | card USKO YEH / bhejo; V10 उसको / usko | APPLIED pending the lead (C7): lines[V10], tokens V10 i=7, takes[T3] (HOLD) with takes[T3].alt = उसे / usey |

Brief sync (creative-director): the creative-director copies V2 (C1), V8 "ke" (C2), V9 "Keemat..." (C3), V10 with a comma (C4) and "usko" (C7, if approved) plus the C1-C3 chunks of C6 into BRIEF 2, 5, 8 (E-1), 9, 15 and 16.

---------------------------------------------------------------------------------------------------------------

## 1. Hooks (ranked; A and B are SLATE-locked, only the first 3 s differ)

| rank | id | mechanism | on screen (f0) | spoken (Roman) | DEV (TTS) | words | ends (est) | status |
|---|---|---|---|---|---|---|---|---|
| 1 | **A** | specificity / number + curiosity gap: the frame's own title says how long you looked at it | `AAP NE ISE / *0.03 sec* / DEKHA (settled on f0; chip 00:00:00:01)` | Aap ne ise palak jhapakte dekha. | आप ने इसे पलक झपकते देखा। | 6 | 2.37 s (hard 2.70) | LOCKED (SLATE 3.3 hook A): public version |
| 2 | **B** | result-first number spectacle | `*360* / LAYERS · 1 SECOND (corridor mid-surge)` | Ek second. Teen sau saath layers. | एक सेकंड। तीन सौ साठ लेयर्स। | 6 | 2.25 s (hard 2.70) | LOCKED (SLATE 3.3 hook B): Trial Reel, frames 0-89 only |
| 3 | - | curiosity gap (viral hook lab C) | `EK FRAME KE *andar*` | Ek frame ke andar kya hota hai? | - | 7 | - | not built: no number, weaker specificity (viral 6/8); needs a new lockup |
| 4 | - | contrarian (viral hook lab D) | `EDITING *aasaan* HAI?` | Sab kehte hain editing aasaan hai. | - | 6 | - | not built: reads as a complaint (viral 5/8); the payoff already answers it |
| 5 | - | relatable callout (new) | `EDITING MEIN *kya* HAI?` | "Editing mein kya hai?" Yeh dekho. | - | 6 | - | not built: spends the send line in the hook and has no number; keep for a later re-cut aimed at non-editors |

**Recommended:** A public, B as the Trial Reel (SLATE §3.3). Both put the first word at 0.10 s and read muted on their own: the number is on screen, the voice adds the human idiom (A) or the scale (B). The body is identical from the splice (f90, 3.0 s); V2 never starts before 3.03 s.

**Loop:** V10 "...usko bhejo." (est end 32.82 s) → V1A "Aap ne ise palak jhapakte dekha." (0.10 s). The friend who receives the send is the "aap" of the hook: "send it to him" -> "you saw this in the blink of an eye"; VO-free 0.78 s before 33.6 while E.loop_world brings back the playing frame, the lockup and the chip; the card swell ends on 33.6 into the f0 impact_soft (gate r1 fix 1: no HERO hit under "Aap" at 0.10).

---------------------------------------------------------------------------------------------------------------

## 2. Story on the grid (100 BPM, beat 0.6 s, bar 2.4 s, 14 bars)

| part | time (s) | lines | job |
|---|---|---|---|
| hook | 0-3.0 | V1A, V1B | stop the thumb: you gave this frame 0.03 s |
| turn | 3.0-8.4 | V2, V3 | the stakes in one image: one frame = 12 real layers, named as the camera flies through |
| escalation | 9.9-24.0 | V4, V5, V6, V7, V8 | every word, every glow; re-hook 12.0: the invisible layer that makes it alive; 30 frames a second; 360 layers; 3 tracks of sound |
| payoff | 26.4-29.5 | V9 | on the drop (79 %): "Keemat... banane wala jaanta hai." with the lockup EK FRAME KI keemat |
| cta + loop | 29.4-33.6 | V10 | send it to the "editing mein kya hai" person; loops into the hook |

Re-hook at 12.0 (bar 5, 36 %): V4 ends ~11.61, so the voice is silent 0.44 s before "Aur ek layer..." on the stop at pane 12. Payoff at 26.4 (bar 11, 79 %): the voice waits 0.35 s after the hit.

---------------------------------------------------------------------------------------------------------------

## 3. The script

Roman = the caption track (house spelling, digits on screen, sentence case). DEV = the exact TTS text. `*` marks the line's serif keyword token; "keyword" is the serif-italic word the viewer sees for that line (often designed type, not a caption).

| id | part | start [bar.beat] | window (hard) | Roman (caption) | spoken as | DEV (TTS, Vlad) | keyword | words | delivery |
|---|---|---|---|---|---|---|---|---|---|
| **V1A** (A) | hook | 0.10 [0.0] +3 | 0.10-2.37 (2.70) | `Aap ne ise *palak jhapakte dekha.` | = | आप ने इसे पलक झपकते देखा। | *0.03 sec* | 6 | intimate, a small smile in the voice, as if pointing at the frame; level, falling end on "dekha" |
| **V1B** (B) | hook | 0.10 [0.0] +3 | 0.10-2.61 (2.70) | `Ek second. Teen sau saath layers.` | = | एक सेकंड। तीन सौ साठ लेयर्स। | *360* | 6 | matter-of-fact, the number almost under the breath; "saath" with a clear aspirated retroflex (60, never "saat" = 7) |
| **V2** (AB) | turn | 3.07 [1.1] +2 | 3.07-5.91 (5.95) | `Lekin is ek frame mein... *12 layers hain.` | Lekin is ek frame mein... baarah layers hain. | लेकिन इस एक फ़्रेम में... बारह लेयर्स हैं। | *12* | 8 | the turn: quiet, stress on "ek", a held breath on "mein...", then plain and sure on "baarah layers hain" |
| **V3** (AB) | turn | 6.00 [2.2] | 6.00-8.36 (8.45) | `Andhera. Dhuaan. Roshni. *Chehra.` | = | अंधेरा। धुआँ। रोशनी। चेहरा। | *chehra* | 4 | hushed naming, one word per beat, each with a short falling end (no list rise) |
| **V4** (AB) | escalation | 10.03 [4.0] +13 | 10.03-11.61 (11.70) | `Har lafz. Har *chamak.` | = | हर लफ़्ज़। हर चमक। | *chamak* | 4 | hushed, a small lift on "chamak" |
| **V5** (AB) | re-hook | 12.05 [5.0] +2 | 12.05-15.79 (15.85) | `Aur ek *layer... jiske bina frame *zinda nahi lagta.` | = | और एक लेयर... जिसके बिना फ़्रेम ज़िंदा नहीं लगता। | *layer... / zinda* | 9 | re-hook: a lift and a hang on "layer...", then lower and slower on "zinda nahi lagta" |
| **V6** (AB) | escalation | 16.95 [7.0] +4 | 16.95-18.84 (18.85) | `Ek second mein *30 frames.` | Ek second mein tees frames. | एक सेकंड में तीस फ़्रेम्स। | *30* | 5 | plain wonder, unhurried |
| **V7** (AB) | escalation | 18.90 [7.3½] | 18.90-21.99 (21.99) | `Yaani har second... teen sau saath layers.` | = | यानी हर सेकंड... तीन सौ साठ लेयर्स। | *360* | 7 | awe under the breath; the number slower and lower, the three words separate |
| **V8** (AB) | escalation | 22.15 [9.0] +16 | 22.15-24.04 (24.15) | `Aur *awaaz ke 3 tracks.` | Aur awaaz ke teen tracks. | और आवाज़ के तीन ट्रैक्स। | *awaaz* | 5 | light, almost a smile |
| **V9** (AB) | payoff | 26.75 [11.0] +10 | 26.75-29.50 (29.85) | `*Keemat... banane wala jaanta hai.` | = | क़ीमत... बनाने वाला जानता है। | *keemat* | 5 | slow, proud, not boastful; "Keemat..." low and quiet, a full breath, then the answer plainly |
| **V10** (AB) | cta+loop | 29.60 [12.1] +6 | 29.60-33.24 (33.35) | `Jo kehta hai "editing mein kya hai", usko *bhejo.` | = | जो कहता है "एडिटिंग में क्या है", उसको भेजो। | *bhejo* | 9 | friendly and warm, not salesy; the quote in a light shrugging tone; "usko bhejo" with a smile |

Keyword sources: V1A `0.03 sec`: lockup `AAP NE ISE / 0.03 sec / DEKHA` settled on f0 (frame layers 08-11) · V1B `360`: hook B text `360 / LAYERS · 1 SECOND` settled on f0 · V2 `12`: counter `12` (jw_key 230) settles as the side-on stack lands (L3 push 0.3) · V3 `chehra`: tag `04 · chehra` (JD's flat face pane), jw_mono · V4 `chamak`: tag `09 · keyword / 10 · chamak` (jw_mono) · V5 `layer... / zinda`: caption C1 (upper band, two serif keywords, one per chunk): *layer...* on the re-hook stop at pane 12, *zinda* as the flick resolves ON (f432, 14.4) · V6 `30`: caption C2 (lower band) serif "30" · V7 `360`: counter `360` (jw_key 240) lands, L3 push 0.5 · V8 `awaaz`: caption C3 (upper band) serif "awaaz"; the VO lane pulses with these words · V9 `keemat`: payoff lockup `EK FRAME KI / keemat`: keyword glyphs rise from 26.62; sub `banane wala jaanta hai` rises 27.7-28.1 · V10 `bhejo`: end card `USKO YEH / bhejo` (C7, gate r1 fix 5, needs the lead's OK; locked SLATE card `USSE YEH / bhejo`) (title from 29.75, settled 31.25-33.24).

---------------------------------------------------------------------------------------------------------------

## 4. Timing table (ESTIMATED at 1.08x; re-measure with `vo_chain.py` + faster-whisper on the real takes)

| line | t0 | t1 | beat of t0 | words | syl | w/s | syl/s | keyword @ t | anchors: word target → est | placement | gap after (A) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| V1A | 0.10 | 2.37 | [0.0] +3 | 6 | 11 | 2.64 | 4.84 | 0.03 sec @ 0.00 | Aap 0.10 → 0.10 | whole line | 0.70 |
| V1B | 0.10 | 2.25 | [0.0] +3 | 6 | 8 | 2.79 | 3.72 | 360 @ 0.00 | Ek 0.10 → 0.10 | whole line | 0.82 |
| V2 | 3.07 | 5.84 | [1.1] +2 | 8 | 11 | 2.89 | 3.98 | 12 @ 4.80 | Lekin 3.07 → 3.07; baarah 4.80 → 4.80 | by anchors | 0.16 |
| V3 | 6.00 | 8.36 | [2.2] | 4 | 9 | 1.69 | 3.81 | chehra @ 7.90 | Andhera 6.00 → 6.00; Dhuaan 6.75 → 6.75; Roshni 7.30 → 7.30; Chehra 7.90 → 7.90 | per word | 1.67 |
| V4 | 10.03 | 11.61 | [4.0] +13 | 4 | 6 | 2.52 | 3.79 | chamak @ 11.20 | Har 10.03 → 10.03; Har 10.95 → 10.95 | per phrase | 0.44 |
| V5 | 12.05 | 15.70 | [5.0] +2 | 9 | 15 | 2.47 | 4.11 | layer... / zinda @ 12.45 / 14.43 | Aur 12.05 → 12.05; bina 13.80 → 13.83; zinda 14.45 → 14.43 | whole line | 1.25 |
| V6 | 16.95 | 18.19 | [7.0] +4 | 5 | 6 | 4.04 | 4.85 | 30 @ 17.76 | Ek 16.95 → 16.95 | whole line | 0.71 |
| V7 | 18.90 | 21.52 | [7.3½] | 7 | 10 | 2.67 | 3.82 | 360 @ 20.40 | Yaani 18.90 → 18.90; teen 20.45 → 20.45 | by anchors | 0.63 |
| V8 | 22.15 | 23.39 | [9.0] +16 | 5 | 6 | 4.04 | 4.85 | awaaz @ 22.35 | Aur 22.15 → 22.15 | whole line | 3.36 |
| V9 | 26.75 | 29.44 | [11.0] +10 | 5 | 10 | 1.86 | 3.72 | keemat @ 26.75 | Keemat 26.75 → 26.75; banane 27.70 → 27.70 | by anchors | 0.16 |
| V10 | 29.60 | 32.82 | [12.1] +6 | 9 | 14 | 2.80 | 4.35 | bhejo @ 29.75 | Jo 29.60 → 29.60 | whole line | 0.78 |

Flags: V6 and V8 run above 3.2 words/s only because their words are monosyllables (tees, frames, teen, tracks); their syllable rate (4.85 / 4.85 syl/s) is Vlad's normal processed pace and both have ~0.65 s of slack in their windows, so the voice may take them slower. No other line exceeds 3.2 words/s. Every placed gap between lines is >= 0.15 s; the V3 words sit 0.06-0.14 s apart by design (one word per 0.6 s tag).

---------------------------------------------------------------------------------------------------------------

## 5. Rate model (measured for this script)

- Source: `workspace/brand_reels/tts/hf_dl/vlad/vlad_v4_r1_DEV.mp3 (Vlad, elevenlabs_v4, texts.py DEV), measured for this script with vo_chain.voiced_runs + faster-whisper small int8 (language hi) word times`.
- Measured: 22.60 s, 53 words, 82 syllables, 18.64 s voiced in 11 runs → articulation **2.84 words/s, 4.40 syl/s**; whole take 2.35 words/s; phrase rates 3.17-5.58 syl/s; pauses: comma 0.20-0.52 s, sentence end 0.54-0.71 s, "..." 0.50 s.
- Model (raw take): 4.6 syl/s mid-phrase, 4.0 on a sentence-final word, 4.3 before a comma; a one-word sentence >= 0.45 s; holds after vo_chain's caps: "," 0.35, "।" 0.45, "..." 0.55 s; V9 delivered 1.06x slower; then / speed (1.08 baseline). On the casting text the model gives 18.23 s of voiced speech vs 18.64 s measured (-2.2 %).
- Why syllables and not words for the fit decisions: both models agree on the whole reel (A: 22.50 s vs 22.96 s raw speech) but not per line: the brief's V9 "Iski keemat... banane wala jaanta hai" has 2.0 syllables per word (word model 2.06 s at 1.08, syllable model 3.17 s with its hold), V2 "Lekin is ek frame mein" has 1.2. Uncertainty +-10 % per line until the takes exist; every tight line has a zero-credit fit ladder.

| version | words | syl | lead model raw @2.7 w/s | @1.06 | @1.10 | syllable model speech raw | @1.06 | @1.08 | @1.10 | placed spans @1.08 |
|---|---|---|---|---|---|---|---|---|---|---|
| A | 62 | 98 | 22.96 | 21.66 | 20.88 | 22.50 | 21.23 | 20.83 | 20.45 | 23.64 |
| B | 62 | 95 | 22.96 | 21.66 | 20.88 | 21.91 | 20.67 | 20.29 | 19.92 | 23.52 |

Per line both estimates are in `script.json` (`est_s`: `raw_take_s`, `post_1p06/1p08/1p10`, `lead_model_*`). 62 words fill 70 % of the reel with speech: the rest is designed silence (tags 05-07, the 0.44 s re-hook gap, the corridor, the rush and drop-out 24.0-26.75, the payoff breath).

---------------------------------------------------------------------------------------------------------------

## 6. Token table (1:1, caption-designer and `vo_chain.py`)

`vo_chain` aligns whisper's Devanagari words to the DEV tokens and copies the Roman token of the same index into `words.json`; the counts are equal per line and per take (checked with `vo_chain.tokens`). "caption" = the token falls in a caption window (C1-C3, BRIEF §15) at its estimated time; every other token is hidden because designed type already shows it. No 1:n splits: `360` is spoken as three tokens (teen / sau / saath), always hidden (hook B text, body counter); `12`, `30`, `3` are one token each.

| line | i | roman | dev (tts) | keyword | est start | caption |
|---|---|---|---|---|---|---|
| V1A | 0 | Aap | आप |  | 0.10 | hidden |
| V1A | 1 | ne | ने |  | 0.30 | hidden |
| V1A | 2 | ise | इसे |  | 0.50 | hidden |
| V1A | 3 | palak | पलक | yes | 0.91 | hidden |
| V1A | 4 | jhapakte | झपकते |  | 1.31 | hidden |
| V1A | 5 | dekha. | देखा। |  | 1.91 | hidden |
| V1B | 0 | Ek | एक |  | 0.10 | hidden |
| V1B | 1 | second. | सेकंड। |  | 0.30 | hidden |
| V1B | 2 | Teen | तीन |  | 1.18 | hidden |
| V1B | 3 | sau | सौ |  | 1.38 | hidden |
| V1B | 4 | saath | साठ |  | 1.58 | hidden |
| V1B | 5 | layers. | लेयर्स। |  | 1.78 | hidden |
| V2 | 0 | Lekin | लेकिन |  | 3.07 | hidden |
| V2 | 1 | is | इस |  | 3.47 | hidden |
| V2 | 2 | ek | एक |  | 3.67 | hidden |
| V2 | 3 | frame | फ़्रेम |  | 3.88 | hidden |
| V2 | 4 | mein... | में... |  | 4.08 | hidden |
| V2 | 5 | 12 | बारह | yes | 4.80 | hidden |
| V2 | 6 | layers | लेयर्स |  | 5.20 | hidden |
| V2 | 7 | hain. | हैं। |  | 5.61 | hidden |
| V3 | 0 | Andhera. | अंधेरा। |  | 6.00 | hidden |
| V3 | 1 | Dhuaan. | धुआँ। |  | 6.75 | hidden |
| V3 | 2 | Roshni. | रोशनी। |  | 7.30 | hidden |
| V3 | 3 | Chehra. | चेहरा। | yes | 7.90 | hidden |
| V4 | 0 | Har | हर |  | 10.03 | hidden |
| V4 | 1 | lafz. | लफ़्ज़। |  | 10.23 | hidden |
| V4 | 2 | Har | हर |  | 10.95 | hidden |
| V4 | 3 | chamak. | चमक। | yes | 11.15 | hidden |
| V5 | 0 | Aur | और |  | 12.05 | shown |
| V5 | 1 | ek | एक |  | 12.25 | shown |
| V5 | 2 | layer... | लेयर... | yes | 12.45 | shown |
| V5 | 3 | jiske | जिसके |  | 13.42 | shown |
| V5 | 4 | bina | बिना |  | 13.83 | shown |
| V5 | 5 | frame | फ़्रेम |  | 14.23 | shown |
| V5 | 6 | zinda | ज़िंदा | yes | 14.43 | shown |
| V5 | 7 | nahi | नहीं |  | 14.83 | shown |
| V5 | 8 | lagta. | लगता। |  | 15.24 | shown |
| V6 | 0 | Ek | एक |  | 16.95 | shown |
| V6 | 1 | second | सेकंड |  | 17.15 | shown |
| V6 | 2 | mein | में |  | 17.55 | shown |
| V6 | 3 | 30 | तीस | yes | 17.76 | shown |
| V6 | 4 | frames. | फ़्रेम्स। |  | 17.96 | shown |
| V7 | 0 | Yaani | यानी |  | 18.90 | shown |
| V7 | 1 | har | हर |  | 19.30 | shown |
| V7 | 2 | second... | सेकंड... |  | 19.50 | shown |
| V7 | 3 | teen | तीन |  | 20.45 | hidden |
| V7 | 4 | sau | सौ |  | 20.65 | hidden |
| V7 | 5 | saath | साठ |  | 20.85 | hidden |
| V7 | 6 | layers. | लेयर्स। |  | 21.05 | hidden |
| V8 | 0 | Aur | और |  | 22.15 | shown |
| V8 | 1 | awaaz | आवाज़ | yes | 22.35 | shown |
| V8 | 2 | ke | के |  | 22.75 | shown |
| V8 | 3 | 3 | तीन |  | 22.96 | shown |
| V8 | 4 | tracks. | ट्रैक्स। |  | 23.16 | shown |
| V9 | 0 | Keemat... | क़ीमत... | yes | 26.75 | hidden |
| V9 | 1 | banane | बनाने |  | 27.70 | hidden |
| V9 | 2 | wala | वाला |  | 28.34 | hidden |
| V9 | 3 | jaanta | जानता |  | 28.77 | hidden |
| V9 | 4 | hai. | है। |  | 29.19 | hidden |
| V10 | 0 | Jo | जो |  | 29.60 | hidden |
| V10 | 1 | kehta | कहता |  | 29.80 | hidden |
| V10 | 2 | hai | है |  | 30.20 | hidden |
| V10 | 3 | "editing | "एडिटिंग |  | 30.41 | hidden |
| V10 | 4 | mein | में |  | 31.01 | hidden |
| V10 | 5 | kya | क्या |  | 31.21 | hidden |
| V10 | 6 | hai", | है", |  | 31.41 | hidden |
| V10 | 7 | usko | उसको |  | 31.95 | hidden |
| V10 | 8 | bhejo. | भेजो। | yes | 32.35 | hidden |

---------------------------------------------------------------------------------------------------------------

## 7. Takes, processing and placement

| take | order | status | lines | DEV (send exactly this) | ROM for `--rom` (`*` = keyword) | chars | tokens | tests |
|---|---|---|---|---|---|---|---|---|
| T1 | 1 | **GO** | V5, V6, V7, V8 | और एक लेयर... जिसके बिना फ़्रेम ज़िंदा नहीं लगता। एक सेकंड में तीस फ़्रेम्स। यानी हर सेकंड... तीन सौ साठ लेयर्स। और आवाज़ के तीन ट्रैक्स। | `Aur ek *layer... jiske bina frame *zinda nahi lagta. Ek second mein *30 frames. Yaani har second... teen sau saath layers. Aur *awaaz ke 3 tracks.` | 137 | 26 | pronunciation test AND production: साठ, फ़्रेम / फ़्रेम्स, लेयर / लेयर्स, ज़िंदा, सेकंड, आवाज़, ट्रैक्स; the two "..." holds |
| T2 | 2 | **GO** | V2, V3, V4 | लेकिन इस एक फ़्रेम में... बारह लेयर्स हैं। अंधेरा। धुआँ। रोशनी। चेहरा। हर लफ़्ज़। हर चमक। | `Lekin is ek frame mein... *12 layers hain. Andhera. Dhuaan. Roshni. *Chehra. Har lafz. Har *chamak.` | 89 | 16 | फ़्रेम again, बारह, the four one-word sentences, लफ़्ज़ |
| T3 | 3 | **HOLD** | V9, V10 | क़ीमत... बनाने वाला जानता है। जो कहता है "एडिटिंग में क्या है", उसको भेजो। | `*Keemat... banane wala jaanta hai. Jo kehta hai "editing mein kya hai", usko *bhejo.` | 74 | 14 | क़ीमत, the payoff hold "...", एडिटिंग, the quote, उसको |
| T4 | 4 | **GO** | V1A | आप ने इसे पलक झपकते देखा। | `Aap ne ise *palak jhapakte dekha.` | 25 | 6 | झपकते; hook A alone so it gets a fresh first-line read |
| T5 | 5 | **GO** | V1B | एक सेकंड। तीन सौ साठ लेयर्स। | `Ek second. Teen sau saath layers.` | 28 | 6 | साठ in the first 3 s of the Trial Reel |

**T3 status:** HOLD until the lead decides gate r1 fix 5 (C7): approved -> record dev as written (उसको); card kept USSE -> record alt.dev (उसे) with alt.rom (usey). Fallback `T3-keep` (only if the lead keeps the locked card `USSE YEH / bhejo`): DEV `क़ीमत... बनाने वाला जानता है। जो कहता है "एडिटिंग में क्या है", उसे भेजो।` · ROM `*Keemat... banane wala jaanta hai. Jo kehta hai "editing mein kya hai", usey *bhejo.` (73 chars, 14 tokens; V10 est end 32.82).

Process (from `pipeline/jawad_reels`, `<RW>` = `workspace/jawad_reels/ek_frame_ki_keemat`; write `takes[].dev` / `takes[].rom` to the two text files first):

```bash
cd /home/user/100/pipeline/jawad_reels; RW=/home/user/100/workspace/jawad_reels/ek_frame_ki_keemat; mkdir -p $RW/vo/takes
python3 -c "import json;d=json.load(open('/home/user/100/brand_reels/design/reels/ek_frame_ki_keemat/script.json'));[open('/home/user/100/workspace/jawad_reels/ek_frame_ki_keemat/vo/takes/%s.%s.txt'%(t['id'],k),'w').write(t[k]) for t in d['takes'] for k in ('dev','rom')]"
tools/heavy.sh python3 -I vo_chain.py process $RW/vo/takes/T1.mp3 --dev $RW/vo/takes/T1.dev.txt --rom $RW/vo/takes/T1.rom.txt --speed 1.08 --realign --out $RW/vo/takes/T1.wav    # same for T2-T5
```

Placement (reel time): each line at `start_target`; lines with two `place` anchors are placed by their anchor words and split at the "..." hold only if the take misses the anchor by more than its tolerance (V2 "baarah" 4.80 ±0.10, V7 "teen" 20.45 ±0.10, V9 "banane" 27.70 ±0.10); V3 per word (6.00 / 6.75 / 7.30 / 7.90), V4 per phrase (10.03 / 10.95); V10 at max(29.60, V9 end + 0.15). Hook stems: V1A alone in the A stem, V1B alone in `ek_frame_ki_keemat_hookb_vo.wav` (0-3.0). Never start body VO before 3.03 s (the splice).

**Fit ladder** (zero-credit steps first; apply only what the measured take needs):

- **V1A (processed > 2.60 s):** --speed 1.10 on T4 (est 2.24 s) → retake T4 once (stability 0.55 if it drags); hard end 2.70.
- **V2 ("baarah" not within 4.70-4.90):** split at the "..." hold and place "baarah" at 4.80 (hold >= 0.25 s) → if "Lekin is ek frame mein..." alone exceeds 1.45 s: retake T2 with the brief text "Is frame mein..." placed at 3.66 (alternate V2-brief).
- **V3 (a word overlaps the next):** --speed 1.10 on T2 → drop "Dhuaan." (tag 02 carries it); zero credits.
- **V4 (ends > 11.70):** move "Har chamak." to 10.90 → --speed 1.10 on T2.
- **V5 (ends > 15.85, or C1 not gone by 16.25):** --speed 1.10 on T1 (est end 15.63) → cap the "layer..." hold at 0.45 s: process T1 with "," in place of that "..." in --dev/--rom (the audio is unchanged; only vo_chain's dramatic-pause cap changes) → start at 12.00 (still >= 0.3 s after V4) → caption C1 hold 0.0.
- **V9 + V10 (V9 end + 0.15 + V10 > 33.24):** --speed 1.10 on T3 → V10 start up to 29.85 (needs V9 end <= 29.70) → cap the V9 hold at 0.45 s (same "," trick) → P2, zero credits: cut "Keemat..." at its hold and start "banane wala jaanta hai." at 26.75 (V9 26.75-28.49, V10 back to 29.50).

Alternates measured with the same model (at 1.08): `V9-brief` "Iski keemat... banane wala jaanta hai." 26.75-29.92; `V9-P2` "Banane wala jaanta hai." 26.75-28.49; `V10-ellipsis` "Jo kehta hai "editing mein kya hai"... usko bhejo." 29.60-33.02 (the brief's held "..." with the v2 words); `V10-keep` "Jo kehta hai "editing mein kya hai", usey bhejo." 29.60-32.82 (only if the lead keeps the USSE card); `V10-usko-worst` "Jo kehta hai "editing mein kya hai", usko bhejo." 29.60-33.02 ("usko" counted as 3 syllables (worst case)); `V2-brief` "Is frame mein... 12 layers hain." 3.07-5.25; `V2-brief-anchored` "Is frame mein... 12 layers hain." 3.66-5.84.

---------------------------------------------------------------------------------------------------------------

## 8. Pronunciation risks (test in T1 first; T1 is also production)

| rank | DEV | Roman | lines (take) | risk | accept if | fallback |
|---|---|---|---|---|---|---|
| 1 | साठ (तीन सौ साठ) | saath | V7, V1B (T1, T5) | heard as "saat" (सात = 7): "teen sau saat" = 307, a wrong spoken number (truth lock) | whisper (hi) returns साठ (or 360) AND by ear an aspirated retroflex "th" at the end | the number exists in T1 and T5: splice the good "teen sau saath" into the other (same voice, zero credits) → retake the failing take with stability 0.55 |
| 2 | फ़्रेम / फ़्रेम्स | frame / frames | V2, V5, V6 (T1, T2) | f -> p ("prem"; the casting ASR heard लाइफ़ as "लाइप") or an inserted vowel ("farem"); it is the concept word | a real /f/ and one syllable "frem"; ASR फ्रेम / फ़्रेम / फ्रेम्स | retake with फ्रेम (no nukta) → तस्वीर (tasveer, feminine): V2 "Lekin is ek tasveer mein...", V5 "...jiske bina tasveer zinda nahi lagti", V6 "Ek second mein tees tasveerein"; captions follow; never in the hook (it has no frame word by design) |
| 3 | झपकते | jhapakte | V1A (T4) | blurred to "japakte" / "jhapkate" inside the first 3 s | aspirated jh; "jha-pak-te" or "jhap-kte" | retake T4 → lead OK: "Aap ne ise ek pal mein dekha." (6 words, same timing) |
| 4 | ज़िंदा | zinda | V5 (T1) | "jinda": fine for many Indian ears, wrong for Pakistani ears on an Urdu word; it is the re-hook keyword | a clear /z/ | retake T1 lines V5 only → spelling ज़िन्दा |
| 5 | क़ीमत | keemat | V9 (T3) | an over-hard uvular q or a glottal catch on the payoff word; "kheemat" | "qeemat" or "keemat", one smooth word | कीमत (no nukta) |
| 6 | लेयर / लेयर्स | layer / layers | V1B, V2, V5, V7 (T1, T2, T5) | "le-yar-se" (an extra vowel) or "lair" | "leyar" / "leyars", two syllables | singular लेयर after the numerals ("baarah layer hain", grammatical in both); captions follow, designed type stays LAYERS |
| 7 | लफ़्ज़ | lafz | V4 (T2) | "lafj" or "laphz" | "lafz" or "lafaz" | लफ़ज़ (lafaz) |
| 8 | ट्रैक्स | tracks | V8 (T1) | "ta-ra-kes" | "traiks" / "tracks", one syllable | ट्रैक (singular after a numeral; caption "3 track") |
| 9 | एडिटिंग | editing | V10 (T3) | "edeeting" (low: the casting take read एडिटर cleanly) | any desi "editing" | none needed |
| 10 | धुआँ | dhuaan | V3 (T2) | "dhua" without the nasal (harmless) | "dhuaan" or "dhuan" | drop "Dhuaan." (V3 fit ladder) |

Spellings applied for the TTS: frame → फ़्रेम (nukta f), frames → फ़्रेम्स, zinda → ज़िंदा, lafz → लफ़्ज़, keemat → क़ीमत, awaaz → आवाज़, layer(s) → लेयर / लेयर्स, second → सेकंड, tracks → ट्रैक्स, editing → एडिटिंग, 12 → बारह, 30 → तीस, 360 → तीन सौ साठ, 3 → तीन, usko → उसको (to him / her; C7: if the lead keeps the USSE card, उसे with the Roman token "usey", never "usse" = उससे); "Aap ne" and "jiske" kept as separate / joined words so DEV and Roman stay 1:1. Unicode NFC (combining nukta), as in the casting text Vlad read cleanly.

---------------------------------------------------------------------------------------------------------------

## 9. Changes from BRIEF §9 (the brief lets the scriptwriter own the final DEV; copy changes need the lead)

| id | line | BRIEF | this script | lead OK | why |
|---|---|---|---|---|---|
| C1 | V2 | `Is frame mein... baarah layers hain.` | `Lekin is ek frame mein... baarah layers hain.` | yes (SLATE 3.3 wording, differs from BRIEF 9) | the brief trimmed it with a 2.65 w/s word model that overrates short words: with the brief text started at 3.07, "baarah" lands ~4.2 s (not 4.80), or the start must wait to 3.66 (a 1.3 s VO hole after the hook). SLATE's line fills 3.07-4.29 plus a natural ~0.5 s hold and puts "baarah" on 4.80 with no split; "Lekin" is the turn word and "ek" echoes EK FRAME |
| C2 | V8 | `Aur awaaz ki teen tracks.` | `Aur awaaz ke teen tracks.` | yes (one letter of SLATE copy) | ट्रैक is masculine in Hindi and Urdu usage ("naya track", "yeh track acha hai"): "awaaz ke teen tracks"; "ki" reads as a gender slip on both sides |
| C3 | V9 | `Iski keemat... banane wala jaanta hai.` | `Keemat... banane wala jaanta hai.` | yes | the brief text runs to ~29.92 s (syllable model) and then V10 cannot end by 33.24 at 1.08; "Keemat..." is said while the keyword glyphs rise (26.62+), "banane" lands with the sub line (27.7) and the line ends ~29.44 with the lockup exit; the meaning is unchanged |
| C4 | V10 | `Jo kehta hai "editing mein kya hai"... usse bhejo.` | `Jo kehta hai "editing mein kya hai", usko bhejo.` | no (punctuation only; the word "usko" is C7) | a comma instead of the held "..." after the quote: V10 3.22 s instead of 3.42 s; the VO ends ~32.82, leaving 0.78 s VO-free for the loop seam |
| C5 | placement | `V3 6.10, V4 9.85, V7 19.00, V10 29.50` | `V3 per word 6.00 / 6.75 / 7.30 / 7.90; V4 per phrase 10.03 / 10.95; V7 18.90; V9 "banane" 27.70; V10 29.60` | no (within the brief's +-0.25 s rule) | V7 on the 8th f567 with the counter roll-in lands "teen" on 20.45 without a split; V10 must start >= V9 end + 0.15; V3 words last 0.46-0.69 s, so they start on their tag arrivals |
| C6 | captions | `BRIEF 15 chunks: Aur ek *layer*... / jiske *bina* / frame *zinda*; Ek *second* mein / *tees* frames; Aur *awaaz* ki / *teen* tracks` | `one serif keyword per caption chunk, <= 2 per instance (v2, gate r1 fix 4): C1 "Aur ek *layer...* / jiske bina / frame *zinda* / nahi lagta"; C2 "Ek second mein / *30* frames / Yaani har second..."; C3 "Aur *awaaz* ke / 3 tracks"; digits on screen ("30 frames", "3 tracks")` | no (house rules; viral gate r1 approved C6 with fix 4) | the re-hook chunk at 12.05 now carries its flame word (*layer...*, as in BRIEF 15 and previs F3) and *zinda* stays on the flick; "jiske bina" stays white so no chunk has two keywords and C1 stays at the 2-per-scene maximum; the prior SRT writes numbers as digits ("3 bari wajahain") |
| C7 | V10 + end card | `Jo kehta hai "editing mein kya hai"... usse bhejo. + card USSE YEH / bhejo` | `Jo kehta hai "editing mein kya hai", usko bhejo. + card USKO YEH / bhejo` | YES, needed (SLATE 5.1 locks the CTA; gate r1 fix 5); T3 is on HOLD until the call | "usse" is how Roman Urdu writes उससे ("from / than him"; the project playbook uses it that way, hooks_retention_captions.md line 186), so the send line can read "send this from him" to Pakistani viewers while the VO says उसे ("to him"); "usko" (उसको) is spelled and read the same on both sides and matches the series' CTA grammar (C26 `US CLIENT KO / bhejo`, C15 `US DOST KO / bhejo`); same syllable count (us-ko / u-se), est end 32.82 s (33.02 s if Vlad gives it a third syllable) vs the card exit at 33.24; the gate measured `USKO YEH` at 455.5 px (jw_caps 86) vs 429.1 px, so it fits. If the lead keeps USSE: VO उसे, Roman / SRT token "usey" (takes[T3].alt) |

Words: 61 → 62 (C1 +2, C3 -1; C7 swaps one word, उसे → उसको, same 2 syllables; C6 moves no words). Spoken numbers unchanged: baarah, tees, teen sau saath, teen ("ek" = one frame / one second / one more layer, as before).

---------------------------------------------------------------------------------------------------------------

## 10. Caption notes (for the caption-designer)

- Visible caption words (est): C1 = V5 (12.05-15.70), C2 = V6 + "Yaani har second..." (16.95-19.97), C3 = V8 (22.15-23.39); every other token is hidden (designed type says it) - see tokens[].caption_visible.
- C1: with V5 ending ~15.70 and hold 0.15, the last chunk is gone ~16.15 (< 16.25).
- Keyword flags in takes[].rom (*word): one per line, except V5 with two (*layer... and *zinda, one per chunk; gate r1 fix 4) and V1B / V7 with none (their serif word is the designed 360, 3 spoken tokens). vo_chain.words_json accepts any number of * per line; snake_captions allows one per chunk (check()).
- Chunk preview (snake_captions.chunk_words, max_words 3, band widths of BRIEF 15, on the estimated times; * = serif keyword): C1 "Aur ek *layer...* / jiske bina / frame *zinda* / nahi lagta" (keywords per chunk [1, 0, 1, 0]); C2 "Ek second mein / *30* frames / Yaani har second..." ([0, 1, 0]); C3 "Aur *awaaz* ke / 3 tracks" ([1, 0]): one serif word per chunk at most, <= 2 per instance, none doubled with designed type.
- End-card spelling (C7, gate r1 fix 5, needs the lead): the VO says उसको with the Roman token "usko", and the card should read `USKO YEH / bhejo`. "usse" reads as उससे ("from / than him") in Roman Urdu. If the lead keeps the card USSE: record T3 with उसे (takes[T3].alt) and write the Roman / SRT token as "usey". The IG caption line "Usse bhejo jo kehta hai ..." (BRIEF 16, creative-director) should follow the same call ("Usko bhejo ..." or "Usey bhejo ...").
- "banane wala" can echo "the Creator" in old film songs; here the lockup pins it to the maker of the frame. No religious reading intended or needed.
- Gate r1 fix 3 (creative-director): the 2-frame glint of the hidden JD at f846-f847 (28.20-28.23 s) falls inside "banane" (est 27.70-28.34), just before "wala" (est 28.34): the maker in the frame glints while the voice says "banane wala". No VO or caption change is needed (captions are hidden 26.4-33.6); once the real T3 word times exist the builder may move the glint to the "wala" onset (within 1 beat of 28.2) if the lead wants that sync.

---------------------------------------------------------------------------------------------------------------

## 11. VERIFY and open questions (for the lead)

- PRE-RECORD (SLATE 4 spoken-number lock): the module self-test must show len(FRAME) == 12, 30 fps and the three stems (VO, SFX, MUSIC) before T1 is generated; the VO says baarah (12), tees (30), teen sau saath (360), teen (3) and nothing else.
- No facts about Jawad are claimed (no clients, income, hours, tools, history); nothing needs [VERIFY].

1. Gate r1 fix 5 / C7: approve the card `USKO YEH / bhejo` with the VO उसको ("usko")? T3 (V9 + V10) is on HOLD until this call; T1, T2, T4 and T5 can be recorded now (gate 8). If no: record T3 with उसे (takes[T3].alt) and the Roman token "usey", never "usse".
2. Approve C1 (V2 back to the SLATE wording), C2 (V8 "ke") and C3 (V9 "Keemat...")? The viral gate r1 approved C1-C5 from its side. Fallbacks: V2-brief (retake, placed at 3.66), V8 "ki" (retake of T1), V9-brief (fits only with T3 at 1.10 and V10 from ~30.0).
3. AI disclosure stays on the defaults (AI info ON, lane label "VO · AI voice" while V8 is spoken, IG caption "Voice: AI (TTS)").
4. If फ़्रेम fails the T1 test twice: approve "tasveer" (feminine forms in V2, V5, V6)?

---------------------------------------------------------------------------------------------------------------

## 12. Self-check

- [x] hook by 0.3 s and readable muted: yes: "Aap" / "Ek" at 0.10 s; the lockups read alone.
- [x] every line traces to SLATE 3.3 / BRIEF 9: yes; no hypotheticals needed; numbers are true by construction.
- [x] both sides of the border: checked word by word: palak jhapakte, lekin, andhera, dhuaan, roshni, chehra, lafz, chamak, zinda, yaani, awaaz, keemat, banane wala, kehta, usko, bhejo are daily words in Pakistan and India; tech words stay English; "usse" (reads as उससे in Roman Urdu) is gone from the Roman track.
- [x] token table: 68 tokens (A 62 + V1B 6); DEV and ROM token counts equal per line and per take (vo_chain.tokens); <= 1 serif keyword per caption chunk and <= 2 per caption instance (snake_captions.chunk_words on the estimated times; V5 carries 2: layer, zinda).
- [x] number lock: the DEV strings contain only these number words: एक (V1B V2 V5 V6), तीन (V1B V7 V8), सौ (V1B V7), साठ (V1B V7), बारह (V2), तीस (V6) ("एक" = one frame / one second / one more layer); spoken: baarah (12), tees (30), teen sau saath (360), teen (3); nothing else (scanned).
- [x] hook: V1A 6 words / 11 syllables, first word 0.10, est end 2.37 (hard 2.70); V1B 6 words, est end 2.25.
- [x] TTS hygiene: no digits, Latin, brackets, tags or emoji in any DEV string (asserted); NFC.
- [x] fit: every line ends inside its window by the syllable model at 1.08; tight lines: V1A (0.33 s to hard), V5 (0.15 s), V9+V10 (0.42 s to the card exit; 0.22 s if "usko" takes a third syllable).
- [x] loop: yes: "usko bhejo" -> "Aap ne ise...".
- [x] narrator: aap / third person only; no main / meri; JD not voiced.
