# SCRIPT · Reel 2 · C11 · Bijli Chali Gayi (@jawad_mp4)

Script v2, 2026-10-08, hinglish-scriptwriter. Status: **v2 applies the viral-strategist gate r1 (`GATE.md`, verdict FIX)
fixes owned by the scriptwriter: 1, 4 (caption tokens), 5 and 6. No TTS has been rendered**, so every timing below is an
estimate. Machine-readable copy: `script.json` in this folder, built from the same data as these tables.

Binding sources: SLATE §0, §2, §3.2, §4, §5; BRIEF §2 (verified copy), §6.3-6.7 (hook frames, VO beat plan, overrun
ladder), §6.14 (captions), §8 (QA); GATE §7 (fixes). The lines are the SLATE/BRIEF lines with the gate's three approved
trims (V4, V7, V8) and its caption spelling (V10, V11). Those are copy changes: the lead OKs them, and the
creative-director mirrors them in BRIEF §2, §6.6 and §6.7 (list in §0).

- **Voice.** Higgsfield preset Vlad, `elevenlabs_v4`, voice_id `e5666b9c-99a2-4fac-8b4e-abee078b186d`, Devanagari text
  (`vo_config.json`). Send the `dev` text exactly as written. Use no audio tags, brackets, digits, Latin or emoji.
  Stability and similarity stay at the provider default unless a take comes out flat (try 0.35) or unstable (try 0.55).
- **Narrator.** "hum / har desi editor / aap". There is no "main / meri / mujhe" anywhere, and nothing about Jawad's own
  childhood, home, PC or habits. JD is not voiced in this reel.
- **Totals.** Version A: **65 words**, 107 syllables (v1: 69 / 115). Version B: **64 words**, 104 syllables (v1: 68 /
  112). The cap is 90 words. The spoken hook is 5 words (A) or 4 words (B), both under the 7-word limit.
- **Estimated speech time.** At the task's 2.7 words/s before speed-up: A **24.07 s** raw, 22.71 s at 1.06x, 21.89 s at
  1.10x; B **23.70 s** raw, 22.36 s, 21.55 s. Syllable model (§5), Vlad's average pace after 1.10x: A 21.63 s, B 21.02 s
  (fast pace: 18.78 / 18.26 s). The VO windows in BRIEF §6.7 add up to 20.6 s (A) / 20.8 s (B). The difference is
  absorbed by lines with free space next to them (V3a, V6, V7, V11, V12). The two blocks that cannot absorb it are in §4.

## 0. What changed in v2 (GATE r1 §7)

| fix | line | v1 | v2 (Roman caption tokens · Devanagari TTS) | effect |
|---|---|---|---|---|
| 1 (T-a) | V4 | `Aur jab *wapas aati thi...` | `Jab *wapas aati thi...` · जब वापस आती थी... | -1 word, -1 syl; rooftop block fits at the average pace |
| 1 (new) | V7 | `Aur bijli ban gayi editor ki sab se bari *dushman.` | `Aur bijli ban gayi sab se bari *dushman.` · और बिजली बन गई सब से बड़ी दुश्मन। | -2 words, -4 syl; "editor" is no longer spoken 3 times in 6 s (V6 and the picture already say whose enemy) |
| 1 (T-b) + 6 | V8 | `Isliye har desi editor ki *ungli khud Ctrl+S dabati hai.` | `Har desi editor ki ungli *khud Ctrl+S dabati hai.` · हर देसी एडिटर की उंगली ख़ुद कंट्रोल-एस दबाती है। | -1 word, -3 syl; "Har desi editor... / Har tees second." anaphora; the keyword moves to *khud*, the spoken stress |
| 4 | V10 | `...nahi sikhaayi...` | `Bijli ne humein *editing nahi sikhai...` (DEV unchanged) | house spelling ("dikhai" in Jawad's SRT) |
| 4 | V11 | `*sabr sikhaaya.` | `*sabr sikhaya.` (DEV unchanged) | house spelling; matches the new lockup `BIJLI NE SIKHAYA` |
| 5 | V2 | placed 2.200 only | fallback 1.550 between the beep pairs if the processed take is > 0.43 s (lead OK) | the rising "hai?" is never trimmed |

Takes: **T2 and T4 change their DEV and ROM** (generate them only with the v2 text, after the lead's OK on fix 1, so the
trims cost no credits). **T5 changes its ROM only**; TA, TB, T3 and T6 are unchanged. "Humein" and "Har tees second" both
stay.

For the creative-director to mirror (their files, not mine): BRIEF §2 P1 `BIJLI NE SIKHAAYA` → `BIJLI NE SIKHAYA` (also
§6.2 S7c, §6.6 P1, §6.15 body line); BRIEF §6.7 rows V4, V7, V8, V10, V11, the totals (65 / 64), the F3 text and the
Devanagari draft; `packet.yaml` audio lines S3-01, S5-01, S6-01, S7-02 and the S7 action text; the payoff row in
`MUSIC_bijli_chali_gayi.md`. BRIEF §6.10: the L8 cues at 18.633-19.033 no longer sit inside V7, which now ends about
18.5-18.9 s.

## 1. Hooks (ranked; A and B are locked, the two reserves are not built)

| rank | id | mechanism | on screen | spoken (Roman) | TTS (Devanagari) | words | first word | muted read |
|---|---|---|---|---|---|---|---|---|
| 1 | **A** (public, recommended) | pattern interrupt: the reel itself loses power | `*Bijli* / CHALI GAYI.` | "Bijli chali gayi." … (beep, beep) … "Yaad hai?" | बिजली चली गई। … याद है? | 5 | 0.100 s | the room dies, the keyword glows: works with no sound |
| 2 | **B** (Trial Reel, f0-f79 only) | sound memory / curiosity (the beep on f0) | `YEH / *awaaz* / YAAD HAI?` | "Yeh awaaz... yaad hai?" | ये आवाज़... याद है? | 4 | 0.300 s | a torch on a blinking LED plus the question |
| 3 | R1 (reserve) | editor pain (panel_viral §4.3 hook C, 7/8) | `LIGHT GAYI · *Ctrl+S?*` | "Light chali gayi. Ctrl+S dabaya tha?" | लाइट चली गई। कंट्रोल-एस दबाया था? | 6 | - | editor-only reach, and f0 would need a desk |
| 4 | R2 (reserve) | relatable callout (panel_viral §4.3 hook D, 6/8) | `CHHAT PE *raatein*?` | "Agar bachpan chhat pe guzra hai..." | अगर बचपन छत पे गुज़रा है... | 6 | - | a weaker gap and a slower stop |

Recommendation: post **A** publicly and run **B** as the alternate. They differ only before the splice frame f80
(2.667 s). Hook A's spoken part ends by 2.6 s, or by 2.0 s with the fix-5 fallback (§4). Both hand back into the loop:
the V12 question "Aap ke ghar light jaane pe kya hota tha?" is answered on replay by V1 "Bijli chali gayi." (A), or by
the beep and "Yeh awaaz... yaad hai?" (B).

## 2. Story (one line per beat of the 90 BPM grid; 20 frames per beat, a bar is 2.667 s)

| part | time (s) | line (Roman captions) | meaning | picture it rides |
|---|---|---|---|---|
| Hook | 0-2.67 | A: **Bijli chali gayi.** … **Yaad hai?** · B: **Yeh awaaz... yaad hai?** | The power's gone. Remember? | brownout f10, CRT collapse, *Bijli* glows f15, torch f20, LED beeps f40/f60 |
| Turn | 3.0-7.85 | **Light jaati thi, toh poora mohalla chhat pe hota tha. Jab wapas aati thi...** | When the power went, the whole neighbourhood was up on the roof. When it came back... | match and candle, tilt up, rooftops (f160), the far tube light's false start f220 (gate fix 3); then the AA GAYI! slam at 8.0 with no VO |
| Escalation | 11.0-14.6 | **Phir woh bachche bare hue. Kuch editor ban gaye.** | Then those kids grew up. Some became editors. | old room by torch, then the on-word cut f400 to the modern desk at 63 % |
| Re-hook (46 %) | 16.4-18.9 | **Aur bijli ban gayi sab se bari dushman.** | And the power became the biggest enemy. | the power dies mid-render, then 0.4 s of VO silence, then the HUD drains to 0 %; "dushman" as the L8 iris starts closing |
| Escalation | 19.3-23.7 | **Har desi editor ki ungli khud Ctrl+S dabati hai. Har tees second.** | Every desi editor's finger presses Ctrl+S by itself. Every thirty seconds. | Ctrl+S keycaps on quarter notes, then eighths from f640; Saved chips |
| Payoff (77 %) | 24.0-28.3 | **Bijli ne humein editing nahi sikhai... sabr sikhaya.** | The power cuts didn't teach us editing... they taught us patience. | candle, JD in profile, drop-out f790-f799, `BIJLI NE SIKHAYA / *sabr*`, harmonium on "sabr" (f820) |
| CTA + loop | 31.6-34.1 | **Aap ke ghar light jaane pe kya hota tha?** | What used to happen at your place when the power went? | end card `COMMENT MEIN / *batao*`, sub "Chhat ya candle?"; the lit room is frame 0 |

There is no VO in 8.0-10.667 (slam and cheer), 14.6-16.4 (render ticking, then the designed silence) or 28.3-31.6
(power returns, the loudest moment).

## 3. The lines (Roman = captions in house spelling; Devanagari = the TTS text; `*` = the line's serif keyword)

| id | Roman (caption tokens) | Devanagari (TTS) | keyword | delivery |
|---|---|---|---|---|
| V1 (A) | `*Bijli chali gayi.` | बिजली चली गई। | Bijli | matter-of-fact, level, falling end; under 1.2 s |
| V2 (A) | `*Yaad hai?` | याद है? | Yaad | softer, a half smile, quick rise; ≤ 0.43 s at 2.200, else the 1.550 fallback (§4) |
| V1B (B) | `Yeh *awaaz... yaad hai?` | ये आवाज़... याद है? | awaaz | intimate; a real pause on "..." (the beep answers it); rising "hai?" |
| V3a | `*Light jaati thi,` | लाइट जाती थी, | Light | remembering, warm, comma lift |
| V3b | `toh poora mohalla *chhat pe hota tha.` | तो पूरा मोहल्ला छत पे होता था। | chhat | remembering; a smile on "chhat" |
| V4 | `Jab *wapas aati thi...` | जब वापस आती थी... | wapas | anticipation, rising, left hanging for the slam |
| V5 | `Phir woh *bachche bare hue.` | फिर वो बच्चे बड़े हुए। | bachche | the turn, slower, a little proud |
| V6 | `Kuch *editor ban gaye.` | कुछ एडिटर बन गए। | editor | plain; "editor" clean (on-word cut) |
| V7 | `Aur bijli ban gayi sab se bari *dushman.` | और बिजली बन गई सब से बड़ी दुश्मन। | dushman | dry, wry, brisk, no commas |
| V8 | `Har desi editor ki ungli *khud Ctrl+S dabati hai.` | हर देसी एडिटर की उंगली ख़ुद कंट्रोल-एस दबाती है। | khud | amused, brisk; the stress and the wink on "khud" |
| V9 | `Har *tees second.` | हर तीस सेकंड। | tees | deadpan tag, tight after V8 |
| V10 | `Bijli ne humein *editing nahi sikhai...` | बिजली ने हमें एडिटिंग नहीं सिखाई... | editing | quiet, sincere; the "..." is a held breath |
| V11 | `*sabr sikhaya.` | सब्र सिखाया। | sabr | warm, final; "sabr" as one clean syllable on f820 |
| V12 | `Aap ke *ghar light jaane pe kya hota tha?` | आप के घर लाइट जाने पे क्या होता था? | ghar | inviting question, rising "tha?", no breath at the end |

Notes:
- **Cross-border read of the new lines.** "Jab wapas aati thi...", "Aur bijli ban gayi sab se bari dushman." and "Har desi
  editor ki ungli khud Ctrl+S dabati hai." are everyday speech in Lahore, Karachi, Delhi and Mumbai. *Bari* agrees with
  the feminine *bijli*, which is how both sides say it.
- **V11 tokens carry no leading "..."** (BRIEF §6.7 wrote "...sabr sikhaaya."). The ellipsis sits on V10's last
  token, so `*sabr` keeps the keyword mark as its first character, the snake captions never show a stray "...", and
  `vo_chain` still keeps the dramatic pause when V10 and V11 are rendered in one take. The wording is unchanged.
- **Captions hide** V1, V2 and V1B (0-2.667), V11 (26.667-29.333) and V12 (30.667-DUR), as BRIEF §6.14 sets out. The
  `*` on those lines is metadata only.
- **One keyword per line.** BRIEF §6.14 listed extra chunk keywords (*mohalla*, V7 *bijli*, *desi*, *Ctrl+S*). I kept
  one per line, which comes to two at most per scene except S6 (*dushman*, *khud*, *tees* across about 5 s).
  *Ctrl+S* is already on the 3D keycaps (two-layer rule). V8's keyword is *khud* since v2 (gate fix 6): it is the word
  the voice stresses, and the glowing word should sit on the spoken stress. The caption-designer can add the brief's
  extras back if wanted; the tokens do not change.
- **House spelling.** Jawad's SRT writes "dikhai" and doubles a vowel only in a long stressed first syllable ("aaya",
  "aata", "baad"). So v2 writes *sikhai / sikhaya* and keeps *jaati, aati, poora, jaane, Yaad*. *awaaz* (hook B, hidden
  in captions, verified lockup HB2) is unchanged.
- **Spoken-number lock (SLATE §4):** "tees" is written as a word in both tracks, never "30". On screen a digit would read
  as a statistic, and BRIEF §2 says the line is a joke about a habit, not a stat. The U3F chip "Saved · har 30 sec"
  exists only under ladder step F4. v2 adds no number: no digit in any ROM line, none in any DEV line.

## 4. Timing table (estimated: no TTS yet)

Windows and bold targets come from BRIEF §6.7; every line may move ±0.25 s, but bold targets may not. "est raw @2.7
w/s" is the task's rate before speed-up. The syllable model uses Vlad's measured rates (§5): "fast" is his neutral
phrases ×1.10, "avg" is his whole-take average ×1.10. "needs syl/s" is the rate the window demands: Vlad's fast
maximum after 1.10x is 5.70, his average 4.95 (4.86 after 1.08x).

| id | ver | part | start → end (s) | bold | anchor (word @ s, f, beat) | Roman (caption) | words | syl | est raw @2.7 w/s | est post 1.06 / 1.10 | syl-model post 1.10 fast / avg | window | needs syl/s |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| V1 | A | hook | 0.100 → 1.150 | start | Bijli @ 0.100, f3, b0.15 | Bijli chali gayi. | 3 | 6 | 1.11 | 1.05 / 1.01 | 1.05 / 1.21 | 1.05 | 5.71 |
| V2 | A | hook | 2.200 → 2.600 (fallback 1.550 → ≤ 2.000) | end | Yaad @ 2.200, f66, b3.3 (fallback 1.550, b2.33) | Yaad hai? | 2 | 2 | 0.74 | 0.70 / 0.67 | 0.35 / 0.40 | 0.40 (0.45) | 5.00 |
| V1B | B | hook | 0.300 → 1.950 | start | yaad @ 1.667, f50, b2.5 | Yeh awaaz... yaad hai? | 4 | 5 | 1.48 | 1.40 / 1.35 | 0.88 / 1.01 | 1.65 | 3.03 |
| V3a | AB | turn | 3.000 → 3.750 |  | Light @ 3.000, f90, b4.5 | Light jaati thi, | 3 | 5 | 1.11 | 1.05 / 1.01 | 0.88 / 1.01 | 0.75 | 6.67 |
| V3b | AB | turn | 4.450 → 6.450 |  | chhat @ 5.400, f162, b8.1 | toh poora mohalla chhat pe hota tha. | 7 | 11 | 2.59 | 2.45 / 2.36 | 1.93 / 2.22 | 2.00 | 5.50 |
| V4 | AB | turn | 6.600 → 7.850 | end | aati ≈ 7.17-7.20 (next to the f220 tease) | Jab wapas aati thi... | 4 | 6 | 1.48 | 1.40 / 1.35 | 1.05 / 1.21 | 1.25 | 4.80 |
| V5 | AB | escalation | 11.000 → 12.500 |  | bachche @ 11.333, f340, b17 | Phir woh bachche bare hue. | 5 | 8 | 1.85 | 1.75 / 1.68 | 1.40 / 1.62 | 1.50 | 5.33 |
| V6 | AB | escalation | 12.950 → 14.250 | anchor | editor @ 13.367, f401, b20.05 | Kuch editor ban gaye. | 4 | 7 | 1.48 | 1.40 / 1.35 | 1.23 / 1.42 | 1.30 | 5.38 |
| V7 | AB | re-hook | 16.400 → 19.210 | start | Aur @ 16.400, f492, b24.6 | Aur bijli ban gayi sab se bari dushman. | 8 | 12 | 2.96 | 2.80 / 2.69 | 2.11 / 2.43 | 2.81 | 4.27 |
| V8 | AB | escalation | 19.330 → 22.840 |  | Ctrl+S @ 21.333, f640, b32 | Har desi editor ki ungli khud Ctrl+S dabati hai. | 9 | 17 | 3.33 | 3.14 / 3.03 | 2.98 / 3.44 | 3.51 | 4.84 |
| V9 | AB | escalation | 22.970 → 23.670 |  | tees @ 23.333, f700, b35 | Har tees second. | 3 | 4 | 1.11 | 1.05 / 1.01 | 0.70 / 0.81 | 0.70 | 5.71 |
| V10 | AB | payoff | 24.020 → 26.300 | end | Bijli @ 24.000, f720, b36 | Bijli ne humein editing nahi sikhai... | 6 | 13 | 2.22 | 2.10 / 2.02 | 2.28 / 2.63 | 2.28 | 5.70 |
| V11 | AB | payoff | 27.300 → 28.050 | anchor | sabr @ 27.333, f820, b41 | sabr sikhaya. | 2 | 4 | 0.74 | 0.70 / 0.67 | 0.70 / 0.81 | 0.75 | 5.33 |
| V12 | AB | cta+loop | 31.800 → 34.100 | end | Aap @ 31.667, f950, b47.5 | Aap ke ghar light jaane pe kya hota tha? | 9 | 12 | 3.33 | 3.14 / 3.03 | 2.11 / 2.43 | 2.30 | 5.22 |

Flags (lines that need more than 3.2 words/s, or more than Vlad's average 4.95 syl/s after 1.10x, in their window):
- **v2 relieves V4 (5.60 → 4.80 syl/s), V7 (5.69 → 4.27) and V8 (5.70 → 4.84).** V1, V3b, V5, V6, V9, V10, V11 and V12 still
  need 5.2-5.7 syl/s (V3a 6.7, V2 5.0) inside their own windows; lines with free space next to them absorb a slower take through
  the ±0.25 s rule. The two places that cannot are the blocks below.
- **V3a** (0.75 s window, needs 6.67 syl/s): let it run 3.00 → about 4.00 s. Its end is not bold.
- **Rooftop block: "chhat" on f162 (5.400) and V4 ending ≤ 7.85.** "chhat pe hota tha" (5 syl), a 0.15 s gap and V4 (6
  syl) must fit in 2.30 s of speech (2.33 s if "chhat" lands on f161). Fast: 1.93 s. Average at 1.10: **2.22 s, fits**
  (V4 ends 7.77, 0.08 s spare). Average at 1.08: 2.26 s, fits with 0.035 s spare, but then "Light" on f90 and "chhat" on
  f162 leave only a 0.14 s comma pause after "thi,". So T2 runs at 1.10, or at 1.08 with V3a starting about 2.90.
- **Dense block 16.40 (bold) → 26.30 (bold): V7, V8, V9, V10.** 46 syllables (v1: 53) in 9.54 s of speech after three
  0.12 s gaps. Fast: 8.07 s. Average: **9.30 s at 1.10, 9.47 s at 1.08, fits as a block** (v1: 10.71 s, 1.17 s over).
  **But one line still binds: V10** (13 syl, not touched by fix 1). At the average pace it needs 2.63 s (1.10), and its
  window runs from 24.02 (23.77 with the -0.25 rule) to the bold 26.30, which is 2.53 s at most. See §4.1.
- **V1:** 1.05-1.21 s from 0.10, so it ends at 1.15-1.31, just before the beep at 1.333. Keep the take matter-of-fact
  and process at 1.08-1.10.
- **V2 (gate fix 5):** 0.35-0.46 s after 1.10x. Measure the processed take from the onset of याद to the end of है? plus
  the 20 ms tail. **≤ 0.43 s:** keep the SLATE placement, 2.200 (f66), ending ≤ 2.633 (the f79 splice). **> 0.43 s:**
  place it at **1.550**, between the beep pairs (pair 1 ends 1.537, pair 2 starts 2.000). The beep then answers the
  question, and the spoken hook ends by 2.0 s, clear of the splice. Never trim the rising "hai?". This departs from
  SLATE §3.2 ("after the second beep"), so it needs the lead's OK. **> 0.45 s:** re-process TA at 1.10 and re-measure;
  if it is still long, the lead chooses between one TA re-take (about 2.5 credits) and letting the decaying tail sit
  under the f60 pulse.
- **V12:** 2.11-2.43 s. Start at f950 (31.667, an eighth note). If the take is slower, start as early as 31.35: the
  cheer ends at 31.1 and the end-card cues are small. The end must stay ≤ 34.10.
- **V6:** start wherever "editor" lands on 13.367 (f401); "Kuch" takes about 0.2 s, so the start is about 13.15-13.18.
  It ends around 14.4-14.6, after the 14.25 window end, but nothing follows until 16.4.
- **V11:** "sabr" at f820. It ends around 28.0-28.25 (fast to emphatic), at or a little past the 28.05 window end,
  which is harmless (the riser starts quietly at 28.133).

### 4.1 Placement plan for the dense block (syllable model; replace with measured values after T4 and T5)

Rule used: V7 starts on the bold 16.400. V10 ends on the bold 26.300 and starts no later than 24.02. V9 puts "tees" on the
f700 press if it can, else earlier. V8 starts on the first press f580 if it can, else earlier. Gaps ≥ 0.12 s.

| pace (T4 / T5 speed) | V7 | V8 ("Ctrl+S" @) | V9 ("tees" @) | V10 | inside the ±0.25 s rule? |
|---|---|---|---|---|---|
| fast, 1.10 / 1.10 | 16.400-18.506 ("dushman" 18.16) | 19.333-22.317 (21.09) | 23.157-23.860 (23.333, f700) | 24.018-26.300 | **yes**: every briefed anchor holds |
| average, 1.08 / 1.10 (recommended speeds) | 16.400-18.871 ("dushman" 18.46) | 19.109-22.609 (21.17), shift -0.22 | 22.729-23.552 (22.94, near the f690 press), shift -0.24 | **23.672**-26.300, shift -0.35 | **no, V10 only** (J-10 below) |
| average, 1.10 / 1.10 | 16.400-18.826 | 19.187-22.624 (21.21), shift -0.14 | 22.744-23.552 (22.95), shift -0.23 | 23.672-26.300, shift -0.35 | no, V10 only |
| average, 1.08 / 1.08 | 16.400-18.871 | 19.060-22.560, shift -0.27 | 22.680-23.504, shift -0.29 | 23.624-26.300, shift -0.40 | no (V8, V9, V10): keep T5 at 1.10 |

So the gate's trims fix the block, but at Vlad's average pace V10 can hold its bold end only by starting about 0.35 s
before its window, i.e. on the last keycap press f710 (23.667), with the VO leading the 24.0 candle cut. The cost: the "Har
tees second." tag keeps only about 0.12 s of air before V10. **V10 decision rule after T5** (T5 is generated first; d10 = the
processed V10 from the onset of बिजली to the end of सिखाई, without the "..." pause):

| d10 | placement | needs |
|---|---|---|
| ≤ 2.28 s | start 24.02, as briefed | nothing |
| 2.28-2.53 s | start 26.30 - d10 (23.77-24.02) | nothing (inside the rule) |
| 2.53-2.64 s | **J-10**: start 26.30 - d10 (23.66-23.77, about the last press f710), the VO leads the candle cut; V8 and V9 move up to -0.25 s with 0.12 s gaps | the lead's OK (beyond ±0.25 s) |
| longer | brief F3: re-take T5 without "humein" | about 2.5 credits; loses "humein" |

## 5. Rate model (measured, not assumed)

The only Vlad audio in the repo is `workspace/brand_reels/tts/hf_dl/vlad/vlad_v4_r1_DEV.mp3` (the casting take, the
`texts.py` DEV sentences). Method: voiced phrases from `vo_chain.voiced_runs`, word onsets from faster-whisper small
int8 (`hi`, run through `tools/heavy.sh`), and 85 syllables counted by hand over its 53 words.

| measure | value |
|---|---|
| articulation (voiced phrases only, 18.90 s) | **2.80 words/s, 4.50 syl/s**, 1.60 syl/word |
| neutral narrative phrases ("एडिटर की लाइफ़ में…", "रेंडर आज रात…", "और मोशन ग्राफ़िक्स…") | 3.08 words/s, **5.18 syl/s** |
| emphatic phrases ("बस थोड़ा सा…", "रात के तीन बज गए", "इन्हीं रातों ने…") | 2.60 words/s, **3.99 syl/s** |
| whole take including pauses | 2.37 words/s (142.8 wpm, as `vo_config` says) |
| pauses in that take (between voiced phrases) | after "," 0.20-0.40 s · "..." 0.50 s · "।" / "?" / "!" 0.54-0.71 s (`vo_chain` caps them at 0.45 s, or 0.9 s after "...") |

The task's 2.7 words/s matches Vlad's articulation rate. This script averages 1.65 syl/word (107 / 65), a little denser
than the casting text, so the syllable model is the better predictor here. **`vo_chain --speed auto` lands about 160 wpm
and clamps to 1.00-1.10x.** On brisk takes it would choose 1.00, so pass the speed explicitly (§7).

## 6. Fit ladders (apply in order; report the step used)

**Dense block 16.4-26.3 (V7-V10).** The v2 copy is already in the T4 text (46 syllables). F1-F4 are the brief's own
steps; J-10 is my proposal and needs the lead's OK.

| step | action | dense block after the step (average model) | cost |
|---|---|---|---|
| v2 copy | gate fix 1: V7 and V8 trimmed before T4 is generated | 9.47 s (T4 1.08) of 9.54 s; V10 still needs §4.1 | 0 |
| F1 | `--speed 1.08` on T4 (1.10 if V7-V9 measure longer than the model), `--speed 1.10` on V10 (T5) | as above | 0 |
| F2 | inter-line gaps down to 0.12 s; V8 and V9 may start up to 0.25 s early ("Ctrl+S" within 0.25 s of f640, "tees" on the f690 or f700 press) | fits if d10 ≤ 2.53 s | 0 |
| **J-10** | V10 starts up to 0.36 s before 24.02 (≥ 23.66, about the last press f710 = 23.667) so it still ends by 26.30 | fits if d10 ≤ 2.64 s (V9 cannot start before 22.72) | 0, lead OK |
| F3 | V10 without "humein": `Bijli ne *editing nahi sikhai...` / बिजली ने एडिटिंग नहीं सिखाई... | 2 syl less | a re-take of T5 (cutting हमें mid-line is not clean) |
| F4 | drop V9 from the VO; chip U3F `Saved · har 30 sec` f712-f719 | 4 syl less | 0 |

The v1 proposals are settled: T-b (no "Isliye") and T-a (no "Aur" in V4) are applied; T-c (V7 without "Aur") is
replaced by the gate's V7, which keeps "Aur" and drops "editor ki".

**Rooftop block 3.0-7.85 (V3a, V3b, V4).** The v2 copy (V4 = "Jab wapas aati thi...") is already in the T2 text.
`--speed 1.10` on T2 (1.08 if V3a may start about 2.90). V3a may start 2.75-3.00 and end by 4.00. Place "chhat" at f162
(never before f160). If V4 still cannot end ≤ 7.85: let "chhat" land on f161 (5.367) and close the V3b → V4 gap to
0.12 s.

**Pronunciation fallback that changes tokens (P-ctrl).** If कंट्रोल-एस comes out with a gap or a "dash", re-take T4 with
`कंट्रोल एस` as two tokens and ROM `Ctrl S`: V8 becomes `Har desi editor ki ungli *khud Ctrl S dabati hai.` /
हर देसी एडिटर की उंगली ख़ुद कंट्रोल एस दबाती है। (10 tokens). The keycaps on screen show Ctrl and S apart, so the caption
still matches the picture.

## 7. Takes (generate in this order; the risky takes go first and double as the pronunciation test)

Each take is one Higgsfield request with the `dev` text below. Process it with `vo_chain.py process <take> --dev "<dev>"
--rom "<rom>" --speed <x>`, then cut it into lines at the token ranges in `script.json` → `takes[].token_ranges` and
place each line on its target. Pauses after "..." are kept up to 0.9 s automatically (V1B, V10).

| take | order | now? | lines | DEV text to send | chars | ROM tokens (vo_chain --rom) | speed | tests |
|---|---|---|---|---|---|---|---|---|
| T5 | 1 | yes (DEV unchanged) | V10, V11 | बिजली ने हमें एडिटिंग नहीं सिखाई... सब्र सिखाया। | 48 | `Bijli ne humein *editing nahi sikhai... *sabr sikhaya.` | 1.10 on V10; V11 may be cut from the raw take and processed alone at 1.06 (warmer) | सब्र, एडिटिंग, हमें, the "..." held pause; **d10 decides §4.1** |
| T4 | 2 | **after the lead's OK on fix 1** | V7, V8, V9 | और बिजली बन गई सब से बड़ी दुश्मन। हर देसी एडिटर की उंगली ख़ुद कंट्रोल-एस दबाती है। हर तीस सेकंड। | 96 | `Aur bijli ban gayi sab se bari *dushman. Har desi editor ki ungli *khud Ctrl+S dabati hai. Har *tees second.` | 1.08 (1.10 if V7-V9 measure longer than the model) | कंट्रोल-एस, ख़ुद (now the stress word), एडिटर, सेकंड, देसी, दुश्मन, बड़ी |
| TB | 3 | yes | V1B | ये आवाज़... याद है? | 19 | `Yeh *awaaz... yaad hai?` | 1.06-1.08 | आवाज़ (nukta z), "..." pause length, rising "है?" |
| TA | 4 | yes | V1, V2 | बिजली चली गई। याद है? | 21 | `*Bijli chali gayi. *Yaad hai?` | 1.08-1.10 | V1 ≤ 1.20 s; V2 ≤ 0.43 s keeps 2.200, 0.43-0.45 s moves it to 1.550 (lead OK) |
| T2 | 5 | **after the lead's OK on fix 1** | V3a, V3b, V4 | लाइट जाती थी, तो पूरा मोहल्ला छत पे होता था। जब वापस आती थी... | 62 | `*Light jaati thi, toh poora mohalla *chhat pe hota tha. Jab *wapas aati thi...` | 1.10 (1.08 if V3a may start about 2.90) | मोहल्ला, छत, V4's onset "जब" without "और" |
| T3 | 6 | yes | V5, V6 | फिर वो बच्चे बड़े हुए। कुछ एडिटर बन गए। | 39 | `Phir woh *bachche bare hue. Kuch *editor ban gaye.` | 1.06-1.08 | बड़े, "editor" onset placement |
| T6 | 7 | yes | V12 | आप के घर लाइट जाने पे क्या होता था? | 35 | `Aap ke *ghar light jaane pe kya hota tha?` | 1.06-1.10 to land the end ≤ 34.10 | rising final "था?" |

7 takes in total (6 for A, plus TB for B), 320 characters (v1: 338). At the casting take's cost (about 2.5 credits per
take up to ~520 characters) that is about 17.5 credits, inside the brief's 15-20 estimate. It costs less if billing is
per character, but leaves little room for retakes if billing is per take. Check the balance before each take and never
resubmit blindly (`vo_config` policy). Recommended: listen to, or at least whisper-check, T5 and T4 before rendering T2,
T3, T6 and TA. Never generate T2 or T4 from the v1 text: the trims are free only before generation.

## 8. TTS spelling decisions (word → spelling, and why)

| word | TTS spelling | why |
|---|---|---|
| awaaz | आवाज़ | nukta z: Urdu-natural on both sides; "awaaj" would sound rural |
| khud | ख़ुद | nukta kh as the default; खुद is an accepted fallback (natural on both sides). Now V8's stress word and keyword |
| bare / bari | बड़े / बड़ी | retroflex flap (stored NFC as ड + ़); captions use the house "bare / bari" |
| editor / editing | एडिटर / एडिटिंग | English loan words in Devanagari phonetics; एडिटर was recognised in the casting take |
| Ctrl+S | कंट्रोल-एस (one token) | one TTS token for the one caption token "Ctrl+S"; the hyphen keeps it one word for the 1:1 rule |
| second | सेकंड | spoken form; fallback सेकेंड |
| tees | तीस | numbers as words (spoken-number lock) |
| light | लाइट | as spoken on both sides; never "बिजली" twice in one line |
| yeh / woh | ये / वो | colloquial spoken forms (not यह / वह) |
| sab se / aap ke | सब से / आप के | written as two tokens to match "sab se" / "Aap ke" 1:1 |
| pe | पे | spoken "pe", not पर, matching the captions |
| sabr | सब्र | the Urdu/Hindi word; fallback सबर (DEV only, captions keep "sabr") |
| sikhai / sikhaya | सिखाई / सिखाया | DEV unchanged in v2; only the Roman spelling follows the house "dikhai" |
| sentence ends | । ? ... , | danda for a stop, "?" for a rise, "..." for a held pause, "," for a short lift; all behaved as expected in the casting take |

## 9. Pronunciation-risk words: test these first (in takes T5, T4, TB)

| rank | word (TTS) | caption | line / take | risk | fallback | accept if |
|---|---|---|---|---|---|---|
| 1 | सब्र | sabr | V11 / T5 | the payoff word on f820 may come out "sa-bar" (two beats, late peak) or get swallowed after the long pause | सबर | ASR hears सब्र or सबर, and it is one stressed beat ≤ 0.35 s |
| 2 | कंट्रोल-एस | Ctrl+S | V8 / T4 | the hyphen read as a pause or a "dash"; wrong stress on "kan-trol"; "एस" clipped | P-ctrl: कंट्रोल एस, ROM `Ctrl S` | heard as कंट्रोल एस with no gap > 0.12 s |
| 3 | आवाज़ | awaaz | V1B / TB | the nukta lost ("awaaj"); the casting take lost the f in लाइफ़ (ASR heard लाइप) | one re-take at stability 0.55, else accept | the z is audible |
| 4 | ख़ुद | khud | V8 / T4 | a plain aspirated kh instead of the fricative; as the new stress word and keyword it must not be swallowed between उंगली and कंट्रोल-एस | खुद | either kh; reject a clipped "kud" or an unstressed "khud" |
| 5 | एडिटिंग | editing | V10 / T5 | not tested on Vlad yet; risk of "edi-tang" | एडीटिंग | ASR hears एडिटिंग |
| 6 | याद है? | Yaad hai? | V2 / TA | length, not sound: it must fit 0.43 s with a rise | the 1.550 placement (gate fix 5, lead OK); 1.10x | ≤ 0.43 s (placed 2.200, ends ≤ 2.633) or ≤ 0.45 s (placed 1.550, ends ≤ 2.000) |
| 7 | बिजली चली गई। | Bijli chali gayi. | V1 / TA | a dramatic read runs into the beep at 1.333 | 1.10x; keep "।" (no ellipsis) | ends ≤ 1.30 when placed at 0.100 |
| 8 | मोहल्ला | mohalla | V3b / T2 | a single l ("mohala") | मुहल्ला | ASR hears मोहल्ला |
| 9 | सेकंड | second | V9 / T4 | the final d swallowed before the stop | सेकेंड | ASR hears सेकंड or सेकेंड |
| 10 | बड़ी / बड़े | bari / bare | V7, V5 | the flap flattened (low risk) | none | any natural flap |

## 10. Token table (every caption token → its TTS token; `vo_chain` maps whisper words through this)

There are no 1:n splits: every Roman token has exactly one Devanagari token. "Ctrl+S" ↔ "कंट्रोल-एस" is one token on
each side; whisper may hear two words (कंट्रोल / एस), and `vo_chain`'s 2:1 merge handles that. The only planned
split is the P-ctrl fallback (§6), where both sides have two tokens. KEY marks the line's caption keyword.

| line | i | roman | dev (TTS) | keyword | syl |
|---|---|---|---|---|---|
| V1 | 0 | Bijli | बिजली | KEY | 2 |
| V1 | 1 | chali | चली |  | 2 |
| V1 | 2 | gayi. | गई। |  | 2 |
| V2 | 0 | Yaad | याद | KEY | 1 |
| V2 | 1 | hai? | है? |  | 1 |
| V1B | 0 | Yeh | ये |  | 1 |
| V1B | 1 | awaaz... | आवाज़... | KEY | 2 |
| V1B | 2 | yaad | याद |  | 1 |
| V1B | 3 | hai? | है? |  | 1 |
| V3a | 0 | Light | लाइट | KEY | 2 |
| V3a | 1 | jaati | जाती |  | 2 |
| V3a | 2 | thi, | थी, |  | 1 |
| V3b | 0 | toh | तो |  | 1 |
| V3b | 1 | poora | पूरा |  | 2 |
| V3b | 2 | mohalla | मोहल्ला |  | 3 |
| V3b | 3 | chhat | छत | KEY | 1 |
| V3b | 4 | pe | पे |  | 1 |
| V3b | 5 | hota | होता |  | 2 |
| V3b | 6 | tha. | था। |  | 1 |
| V4 | 0 | Jab | जब |  | 1 |
| V4 | 1 | wapas | वापस | KEY | 2 |
| V4 | 2 | aati | आती |  | 2 |
| V4 | 3 | thi... | थी... |  | 1 |
| V5 | 0 | Phir | फिर |  | 1 |
| V5 | 1 | woh | वो |  | 1 |
| V5 | 2 | bachche | बच्चे | KEY | 2 |
| V5 | 3 | bare | बड़े |  | 2 |
| V5 | 4 | hue. | हुए। |  | 2 |
| V6 | 0 | Kuch | कुछ |  | 1 |
| V6 | 1 | editor | एडिटर | KEY | 3 |
| V6 | 2 | ban | बन |  | 1 |
| V6 | 3 | gaye. | गए। |  | 2 |
| V7 | 0 | Aur | और |  | 1 |
| V7 | 1 | bijli | बिजली |  | 2 |
| V7 | 2 | ban | बन |  | 1 |
| V7 | 3 | gayi | गई |  | 2 |
| V7 | 4 | sab | सब |  | 1 |
| V7 | 5 | se | से |  | 1 |
| V7 | 6 | bari | बड़ी |  | 2 |
| V7 | 7 | dushman. | दुश्मन। | KEY | 2 |
| V8 | 0 | Har | हर |  | 1 |
| V8 | 1 | desi | देसी |  | 2 |
| V8 | 2 | editor | एडिटर |  | 3 |
| V8 | 3 | ki | की |  | 1 |
| V8 | 4 | ungli | उंगली |  | 2 |
| V8 | 5 | khud | ख़ुद | KEY | 1 |
| V8 | 6 | Ctrl+S | कंट्रोल-एस |  | 3 |
| V8 | 7 | dabati | दबाती |  | 3 |
| V8 | 8 | hai. | है। |  | 1 |
| V9 | 0 | Har | हर |  | 1 |
| V9 | 1 | tees | तीस | KEY | 1 |
| V9 | 2 | second. | सेकंड। |  | 2 |
| V10 | 0 | Bijli | बिजली |  | 2 |
| V10 | 1 | ne | ने |  | 1 |
| V10 | 2 | humein | हमें |  | 2 |
| V10 | 3 | editing | एडिटिंग | KEY | 3 |
| V10 | 4 | nahi | नहीं |  | 2 |
| V10 | 5 | sikhai... | सिखाई... |  | 3 |
| V11 | 0 | sabr | सब्र | KEY | 1 |
| V11 | 1 | sikhaya. | सिखाया। |  | 3 |
| V12 | 0 | Aap | आप |  | 1 |
| V12 | 1 | ke | के |  | 1 |
| V12 | 2 | ghar | घर | KEY | 1 |
| V12 | 3 | light | लाइट |  | 2 |
| V12 | 4 | jaane | जाने |  | 2 |
| V12 | 5 | pe | पे |  | 1 |
| V12 | 6 | kya | क्या |  | 1 |
| V12 | 7 | hota | होता |  | 2 |
| V12 | 8 | tha? | था? |  | 1 |

## 11. Self-check (v2)

- [x] Hook A is spoken from 0.100 s (QA ≤ 0.13) and hook B from 0.300 s (QA ≤ 0.33). Both read muted through the
      designed lockups (`*Bijli* / CHALI GAYI.`, `YEH / *awaaz* / YAAD HAI?`). Hook A: 5 words, ending by 2.6 s (2.0 s
      with the fix-5 fallback); hook B: 4 words. Both are under the 7-word limit by 2.7 s.
- [x] Every line is the SLATE/BRIEF approved text, or the gate's approved trim of it (§0). The only hypothetical is
      the generic "woh bachche"; there are no facts about Jawad, no main/meri, no numbers except the "har tees second"
      joke, no politics, utility, city or country names, no UPS/inverter, no load-shedding.
- [x] Number lock (SLATE §4): "tees" is a word in both tracks; no digit in any ROM or DEV line (checked by script).
- [x] Cross-border read: bijli, light, mohalla, chhat, bachche, dushman, desi, ungli, khud, sabr, humein and "aap ke
      ghar" are everyday words in both Lahore/Karachi and Delhi/Mumbai. No one-sided word, no Sanskritised or heavy
      Persianised vocabulary. "Editor" is now spoken twice (V6, V8), not three times in 6 s.
- [x] House spelling (prior SRT): hai, nahi, bari, bare, woh, yeh, kuch, phir, aur; *sikhai / sikhaya* like "dikhai".
      Sentence case, with lower case for clause continuations (toh…, sabr…).
- [x] Token table complete: 69 rows (65 A + 4 B-only). DEV and ROM are 1:1 per line and per take, checked with
      `vo_chain.tokens` and `vo_chain.words_json`; every take's DEV/ROM is the join of its lines and its token ranges
      match. One keyword per line, each ≤ 12 characters. DEV is NFC with no Latin, digits or brackets.
- [x] The loop line V12 hands back to the hook (the question is answered by "Bijli chali gayi." on replay).
- [x] Word budget: 65 words (A) / 64 (B) against the 90 cap. The rooftop block fits at the average pace, and the dense
      block fits as a block (9.30-9.47 s of 9.54 s).
- [ ] V10 at the average pace still needs J-10 (lead OK) or F3. Measure T5 first (§4.1).

## 12. Open questions and [VERIFY] items for the lead

1. **Fix 1 copy (V4, V7, V8): OK before T2 and T4 are generated?** The trims are free only if those two takes are
   generated from the v2 text. T5, TB, TA, T3 and T6 do not depend on it and can go now.
2. **Fix 5: OK to place "Yaad hai?" at 1.550, between the beep pairs, if TA measures over 0.43 s?** It departs from
   SLATE §3.2 ("after the second beep"). If the take fits, the SLATE placement stays.
3. **J-10: if T5's V10 measures 2.53-2.64 s, may it start up to 0.36 s before the 24.0 candle cut** (beyond the ±0.25 s
   rule; about on the last keycap press f710)? The alternative is the brief's F3, which costs a re-take and "humein".
4. **Speed at generation.** Does the Higgsfield `elevenlabs_v4` request accept a speed parameter? Generating at
   1.05-1.10 sounds cleaner than rubberband. `vo_config` lists only stability and similarity_boost. T2 and V10 use
   the brief's 1.10 ceiling, above my own 1.08 default; T4 now needs only 1.08.
5. **AI label:** on for both versions (SLATE §7.1 default). The VO claims nothing about Jawad and JD is not voiced.
6. **Truth flag (gate minor 8, creative-director):** JD's profile sits under "Bijli ne humein…". It is the collective
   "we", not a memoir claim; the lead confirms Jawad is comfortable with it.
7. No [VERIFY] facts: the script states nothing about Jawad's clients, income, views, tools or history.
8. Words that still sound wrong in auditions: **none known yet**. No take of this script has been rendered. From the
   casting take: एडिटर is good; the f in लाइफ़ was heard as "p" (a nukta-fricative risk for आवाज़ and ख़ुद); sentence-final
   words stretch (गए। took about 0.44 s).
