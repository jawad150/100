# SCRIPT · Reel 1 · C26 · Pehle Wala Hi Theek Tha (v1 se v27 tak) · `pehle_wala`

Author: hinglish-scriptwriter · Date: 2026-10-08 · Machine twin: `script.json` (same folder; every number in this
file is generated from it). Binding inputs: `BRIEF.md` §0, §5.3, §7, §9, §10, §11, §17; `SLATE.md` §0, §2, §3.1, §4,
§5; `pipeline/jawad_reels/vo_config.json`; house spelling `workspace/brand_reels/prior/captions_roman_urdu.srt`.

**Status: ESTIMATED timings.** No Vlad take exists yet. Every start/end below comes from two estimators (§4) and is
replaced by measured onsets after the TTS run. Nothing here is a fact about Jawad: fictional client, fictional brand,
labelled POV skit. Narrator = "har editor" (never "main"); JD is not voiced.

**Revision r2 (viral gate r1, `GATE.md` §8, fixes 2 and 4; no Devanagari prompt changed, so the TTS run can start).**
- Fix 2: L2 "Ho jayega." moves 2.933 -> **3.267 (f98)**, two frames after pin 3 "Thora left." lands (3.200), so it is
  the editor's reply to a visible note in both hooks (in hook B it is no longer heard as the client finishing "client ne
  kaha..."). Expected end 4.055, conservative 4.128 (hard end 4.25); L3 stays at 4.40. Pin 3's 3.200 cue
  returns to full `pin_thock` 0 dB. Caption chunk 0 re-solves to 3.22-4.35. L1B's hard end is **2.70 s** (was 2.78):
  expected 2.564, conservative 2.731 -> the fallback chain in §4 (estimated 2.53 s after step 2).
- Fix 4: L11 and L12 carry no caption keyword (Roman token track and `T3.rom.txt` only). After the payoff only
  *pehle wala* (27.7-29.5) and the CTA *bhejo* (29.9-34.1) glow; chunks 17 "final hota hai" and 19 "client ne bola"
  render all-white.
- Re-checked: word budget (unchanged: 45 / 46 tokens), hook lengths (A 5, B 6 spoken words, first word 0.10 s),
  SLATE §4 number lock (only छब्बीस and वी-वन are spoken; v1 -> v27, 26, Ctrl+Z ×26 stay on screen).
- Not mine, for the creative-director: fix 1 (client marker under L12 from 32.633, `ui_hover` listed in §8), fix 3
  (hook B panel), fix 5 (BRIEF §7/§9/§10/§11 and `packet.yaml` 212, 319-327 synced to this file; BRIEF §11 row 3.200
  -> `pin_thock` 0), and fix 4's *garam* dim (×0.35 under the card and on cover frame 855).

---------------------------------------------------------------------------------------------------------------

## 0. One screen

| field | value |
|---|---|
| voice | Higgsfield `elevenlabs_v4`, preset **Vlad** (`e5666b9c-99a2-4fac-8b4e-abee078b186d`), Devanagari prompts, stability omitted (0.55 if the echo words come out animated, 0.35 if L1/L11 come out flat). No brackets, audio tags, emoji or Latin digits in any prompt |
| grid | 112.5 BPM, 16 f/beat, 64 f/bar, DUR 34.1333 s (1,024 f) |
| hook A (public) | **"Bas ek chhota sa change."** बस एक छोटा सा चेंज। · 5 words · 0.100 -> 1.63 s expected (1.93 conservative) |
| hook B (Trial) | **"Chhabbees revision baad client ne kaha..."** छब्बीस रिविज़न बाद क्लाइंट ने कहा... · 6 words · 0.100 -> 2.56 s (2.73); hard end **2.70** (gate), fallbacks §4; captions show "26" |
| re-hook | L7 "Ab Mummy bhi review karengi." at 12.867 s (37.7 %), with Mummy's pin and the D7 |
| payoff | the pin "Pehle wala hi theek tha." at 25.600 is READ, not spoken (drop-out, then Ctrl+Z ×26); the spoken moral L11 "Har editor jaanta hai, v1 hi final hota hai." at 28.133 |
| loop | L12 "...aur phir client ne bola" ends 34.050 -> frame 0 "Bas ek chhota sa change." (gap 0.18 s across the seam) |
| words | hook A track **45 tokens** (46 spoken words: "v1" = vee one); hook B track 46 (47). Brief target 49, cap 60 |
| duration at ~2.7 words/s | A: 16.67 s raw -> 15.72 s at 1.06x / 15.15 s at 1.10x. B: 17.04 -> 16.07 / 15.49 s |
| per-line model (1.08x) | speech A 16.86 s expected / 17.99 s conservative; B 17.79 / 18.79 s. Higher than words/2.7 because the one-word sentences (Pop? Clean. Fun.) take 0.5-0.7 s each. VO covers 51 % of the reel; the rest is pins, SFX and music by design (BRIEF §9: "the comedy is read; the narrator only deadpans") |
| takes | 4 takes, about 10 credits if Higgsfield bills per take (~2.5 each); run order T1 -> T4 -> T2 -> T3 (riskiest words first) |
| keywords | one serif keyword per line in L1-L10 (`*` in the token track); **L11 and L12 none** (gate fix 4): after the payoff only *pehle wala* and *bhejo* glow |

---------------------------------------------------------------------------------------------------------------

## 1. Hooks (A and B are locked by the SLATE; C-E are the alternatives considered, ranked)

| rank | id | mechanism | on screen (designed lockup) | spoken (Roman) | Devanagari | words | ends (exp / cons) | status |
|---|---|---|---|---|---|---|---|---|
| 1 | A | relatable pain + the client quote everyone has heard (open loop: how small is "small"?) | BAS EK / chhota sa / CHANGE (designed lockup, readable by f16) | Bas ek chhota sa change. | बस एक छोटा सा चेंज। | 5 | 1.63 / 1.93 s | LOCKED (SLATE 3.1) - public post |
| 2 | B | result first (a number) + curiosity gap ("client ne kaha..." withholds the punchline until 25.6 s) | 26 / REVISIONS BAAD (designed lockup over the v27 mess) | Chhabbees revision baad client ne kaha... | छब्बीस रिविज़न बाद क्लाइंट ने कहा... | 6 | 2.56 / 2.73 s | LOCKED (SLATE 2.1, 3.1) - Trial Reel |
| 3 | C | number, shorter | (B's lockup) | Chhabbees revision. Ek client. | छब्बीस रिविज़न। एक क्लाइंट। | 4 | - | considered, not produced (fallback for B only if T4 cannot land by 2.70 s after the section 4 fallbacks): loses the "client ne kaha..." open loop that the payoff pays off |
| 4 | D | curiosity gap on the chip flip | (A's lockup) | Yeh ad approved tha. Phir... | यह ऐड अप्रूव्ड था। फिर... | 5 | - | not produced: the "Approved -> Changes requested" chip already says it in picture; no sentence loop with L12; "approved" is a pronunciation risk in the first second |
| 5 | E | relatable callout | (A's lockup) | Har editor ne yeh suna hai. | हर एडिटर ने यह सुना है। | 6 | - | not produced: delays the quote to after 1.5 s and spends L11's "har editor" line in the first second |

Recommendation: **A** public, **B** as the Trial Reel (it differs only in frames 0-79; both share every line from L2).
Both put the first word at 0.10 s, both read muted (the lockups carry them), both stay under 7 spoken words. B drops
the SLATE's comma after "baad" so the line is one breath and lands by the gate's 2.70 s (expected 2.56 s): with a
0.3 s comma it would run to about 2.9-3.0 s. In both hooks the next voice is L2 at 3.267, after pin 3 lands, so B's
"client ne kaha..." stays open until the payoff pin (25.6 s).

---------------------------------------------------------------------------------------------------------------

## 2. Story map (what each line does)

| part | time (s) | lines | job |
|---|---|---|---|
| Hook | 0.10-2.6 | L1 (A) / L1B (B) | the quote everyone has heard over a perfect ad that is about to die / the result first |
| Turn | 3.27-7.4 | L2 "Ho jayega." · L3 "Pop? Kisi ko nahi pata." · L4 "Clean." | the editor answers pin 3 "Thora left." (call and response); the first absurd note is echoed and judged; the narrator's rule is set: he repeats the buzzword, flat |
| Escalation | 8.6-16.4 | L5 "Energetic." · L6 "Fun." · **L7 re-hook "Ab Mummy bhi review karengi."** · L8 "Bilkul cinematic." | rule of three echoes, then a new reviewer at 37.7 %, then the echo with a twist |
| Pattern break | 16.4-19.2 | (VO silence) | the 50 % pin "Sab kuch thora bara" lands at 17.067 with no voice (research §3.1: VO silence at the midpoint) |
| Barrage | 19.2-20.9 | L9 "Aur ek, aur ek, aur ek." | one fragment per pin, the narrator gives up counting; then 2.6 s of pure visual chaos (filenames, 3:47 AM) |
| Suspense | 23.5-24.8 | L10 "Phir aakhri message..." | the hovering pin; then true silence from 25.067 |
| Payoff | 25.6 / 28.13-31.4 | (pin read) · L11 "Har editor jaanta hai, v1 hi final hota hai." | the screenshot line is the client's pin; the voice gives the send-worthy moral after the rewind |
| CTA + loop | 29.87-34.13 | (end card `US CLIENT KO / bhejo`, not spoken) · L12 "...aur phir client ne bola" | the unfinished sentence hands back to frame 0's "Bas ek chhota sa change." |

---------------------------------------------------------------------------------------------------------------

## 3. The lines (estimated; `(!)` = the conservative estimate crosses the hard end, see the fallback in §4)

| id | hook | part | beat (bar.beat+f) | start -> end target (s) | cons. end | hard end | Roman (caption track) | Devanagari (TTS) | keyword |
|---|---|---|---|---|---|---|---|---|---|
| L1 | A | Hook A (public) | 0.0+3f (f3) | 0.100 -> 1.631 | 1.930 | 2.600 | Bas ek chhota sa change. | बस एक छोटा सा चेंज। | *chhota* |
| L1B | B | Hook B (Trial) | 0.0+3f (f3) | 0.100 -> 2.564 | 2.731 (!) | 2.700 | Chhabbees revision baad client ne kaha... | छब्बीस रिविज़न बाद क्लाइंट ने कहा... | *26* |
| L2 | A+B | Turn | 1.2+2f (f98) | 3.267 -> 4.055 | 4.128 | 4.250 | Ho jayega. | हो जाएगा। | *jayega* |
| L3 | A+B | Turn | 2.0+4f (f132) | 4.400 -> 6.547 | 6.564 | 6.583 | Pop? Kisi ko nahi pata. | पॉप? किसी को नहीं पता। | *Pop* |
| L4 | A+B | Escalation | 3.0+10f (f202) | 6.733 -> 7.304 | 7.412 | 7.450 | Clean. | क्लीन। | *Clean* |
| L5 | A+B | Escalation | 4.0+2f (f258) | 8.600 -> 9.468 | 9.476 | 9.550 | Energetic. | एनर्जेटिक। | *Energetic* |
| L6 | A+B | Escalation | 5.0+4f (f324) | 10.800 -> 11.330 | 11.397 | 11.700 | Fun. | फ़न। | *Fun* |
| L7 | A+B | Re-hook (37.7 %) | 6.0+2f (f386) | 12.867 -> 14.785 | 14.917 (!) | 14.900 | Ab Mummy bhi review karengi. | अब मम्मी भी रिव्यू करेंगी। | *Mummy* |
| L8 | A+B | Escalation | 7.0+2f (f450) | 15.000 -> 16.367 | 16.502 (!) | 16.500 | Bilkul cinematic. | बिल्कुल सिनेमैटिक। | *cinematic* |
| L9 | A+B | Barrage | 9.0+1f (f577) | 19.233 -> 20.880 | 20.969 | 21.100 | Aur ek, aur ek, aur ek. | और एक, और एक, और एक। | *ek* |
| L10 | A+B | Suspense | 11.0+1f (f705) | 23.500 -> 24.777 | 24.870 | 24.950 | Phir aakhri message... | फिर आख़री मैसेज... | *aakhri* |
| L11 | A+B | Payoff (spoken moral) | 13.0+12f (f844) | 28.133 -> 31.361 | 31.421 | 32.350 | Har editor jaanta hai, v1 hi final hota hai. | हर एडिटर जानता है, वी-वन ही फ़ाइनल होता है। | none (all-white, gate fix 4) |
| L12 | A+B | Loop | 15.1+3f (f979) | 32.639 -> 34.050 | 34.050 | 34.053 | ...aur phir client ne bola | और फिर क्लाइंट ने बोला | none (all-white, gate fix 4) |

Caption track notes: L11 and L12 have no keyword (all-white chunks, gate fix 4). L1 and L1B are hidden (0-2.667 s) because the lockups show them; L1B's caption tokens are
`26 revision baad client ne kaha...` (digits on screen, house rule) while the voice says "chhabbees". "v1" shows as
`v1` and is spoken वी-वन. Display drops trailing `, . ।` and keeps `? ...` (snake_captions house style).

Delivery notes (for choosing between takes; ElevenLabs gets no tags):
- **L1**: matter-of-fact, mid pitch: the quote every editor knows; no smile, no build-up. On screen: f0 v1 ad, chip "Approved"; pin "Logo thora bara?" lands f8 (pin_thock_dark under "ek"); lockup BAS EK / chhota sa / CHANGE readable by f16.
- **L1B**: result first, flat, one breath (no comma), trailing off on "kaha...". On screen: f0 v27 mess + lockup 26 / REVISIONS BAAD; D1 scrub f40-f79 back to v3.
- **L2**: resigned, the vendor reply to the note that just landed; it answers pin 3 in both hooks (in hook B it can no longer be heard as the client finishing "client ne kaha..."). On screen: pin 2 "Aur bara." (v3, logo x3, 2.133); pin 3 "Thora left." lands 3.200 (f96, full pin_thock) and the logo slides -72 px over 6 f; the voice enters 2 frames later (f98).
- **L3**: "Pop?" dry, one word echoing the pin (placed 0.25 s beat after it), then the flat verdict. On screen: pin 4 "Thora aur pop karo" 4.267 (pop SFX 4.333, then the voice says "Pop?"); saturation spike + NEW burst; the tail crosses pin 5 (6.400, cream fill).
- **L4**: flat, falling; its vowel lands as the cream fill completes (f204). On screen: v6 cream background (pin 5 "Background white kar do, clean lagega").
- **L5**: flat, on the drums arriving (2 frames after the downbeat). On screen: v8 pin 7 "Music thora energetic" 8.533: the player starts shaking, drums in.
- **L6**: flatter still (third echo). On screen: v10 pin 9 "Font fun wala karo" 10.667: parody garam wobbles.
- **L7**: a small sigh carried by the words (no audio tags); respectful plural "karengi". On screen: D7 + Mummy's gold pin 12.800 ("Mujhe pasand nahi aaya."); her thread 13.333 / 13.867 / 14.400.
- **L8**: dry, one breath, the keyword last. On screen: v16 pin 15 "Thora cinematic" 14.933 (braam): letterbox, flares, JD in sunglasses.
- **L9**: a tired count, each fragment cut from the take and placed 1 frame after its pin. On screen: pins v21 "Aur pop." 19.200, v22 "Logo aur bara." 19.733, v23 "Shadow kam karo" 20.267 (one per beat).
- **L10**: lower, trailing off; then nothing until 28.133 (drop-out, payoff read, rewind). On screen: bar 11: the last pin hovers, undecided; true silence from 25.067; the payoff pin lands 25.600.
- **L11**: warm, knowing, unhurried; comma beat placed at 0.15 s. On screen: v1 restored 27.733, chip "Approved", pehle wala / HI THEEK THA, JD smirk tile; end card from 29.867.
- **L12**: rising, unfinished: cut from take T3, which continues ", बस एक छोटा सा चेंज।", so "bola" keeps a continuation contour. On screen: end card settled 31.717-33.773; frame 0 completes the sentence: "Bas ek chhota sa change.".

---------------------------------------------------------------------------------------------------------------

## 4. Timing (ESTIMATED; replace with measured onsets after the Vlad run)

How the numbers were made (both estimators are in `script.json` per phrase):
1. **Model fitted on Vlad.** The Vlad v4 audition (`hf_dl/vlad/vlad_v4_r1_DEV.mp3`) was transcribed with
   faster-whisper word timestamps and split into its 11 voiced runs (`vo_chain.voiced_runs`). A least-squares fit
   over 10 phrases (the dramatic post-ellipsis phrase excluded) gives **raw s = 0.20 × syllables + 0.13**, rms error
   0.19 s. One-syllable sentences get a 0.50 s raw floor (Vlad's "भाई," was 0.53 s). Divided by 1.08 (the speed-up).
2. **Scratch take.** The four takes of §6 were synthesised locally with Kokoro `hm_psi` (free, scratchpad only, never
   used in the reel), run through `vo_chain.py process` and aligned; phrase spans were normalised to 1.08x and
   multiplied by 1.076 (Vlad's speech time / Kokoro's on the same audition text).
3. **expected** = the mean of 1 and 2; **conservative** = the larger. Internal pauses are not left to the TTS: the
   assembler places them (`,` 0.15 s, `?` 0.25 s, sentence 0.35 s). Vlad's raw rate on the audition was 142.8 wpm
   (2.38 words/s with pauses); the vo_config speed-up of 1.06-1.10x is fixed at **1.08** for every take here so the
   voice tempo does not change between lines.

| id | words | syl | est. dur (s) | w/s | syl/s | keyword @ (s) | gap after (A / B) | phrase estimates: model / Kokoro x1.076 -> plan (s) |
|---|---|---|---|---|---|---|---|---|
| L1 | 5 | 6 | 1.53 | 3.27 (>3.2, monosyllables) | 3.92 | chhota @ 0.61 | 1.64 / - | "Bas ek chhota sa change." 1.23 / 1.83 -> 1.53 |
| L1B | 6 | 11 | 2.46 | 2.44 | 4.47 | 26 @ 0.10 | - / 0.70 | "26 revision baad client ne kaha..." 2.30 / 2.63 -> 2.46 |
| L2 | 2 | 4 | 0.79 | 2.54 | 5.07 | jayega @ 3.46 | 0.34 / 0.34 | "Ho jayega." 0.86 / 0.72 -> 0.79 |
| L3 | 5 | 8 | 2.15 | 2.33 | 4.22 | Pop @ 4.40 | 0.19 / 0.19 | "Pop?" 0.46 / 0.47 -> 0.46; "Kisi ko nahi pata." 1.42 / 1.45 -> 1.43 |
| L4 | 1 | 1 | 0.57 | 1.75 | 1.75 | Clean @ 6.73 | 1.30 / 1.30 | "Clean." 0.46 / 0.68 -> 0.57 |
| L5 | 1 | 4 | 0.87 | 1.15 | 4.61 | Energetic @ 8.60 | 1.33 / 1.33 | "Energetic." 0.86 / 0.88 -> 0.87 |
| L6 | 1 | 1 | 0.53 | 1.89 | 1.89 | Fun @ 10.80 | 1.54 / 1.54 | "Fun." 0.46 / 0.60 -> 0.53 |
| L7 | 5 | 9 | 1.92 | 2.61 | 4.69 | Mummy @ 13.08 | 0.21 / 0.21 | "Ab Mummy bhi review karengi." 1.79 / 2.05 -> 1.92 |
| L8 | 2 | 6 | 1.37 | 1.46 | 4.39 | cinematic @ 15.46 | 2.87 / 2.87 | "Bilkul cinematic." 1.23 / 1.50 -> 1.37 |
| L9 | 6 | 6 | 1.65 | 3.64 (>3.2, monosyllables) | 3.72 | ek @ 20.59 | 2.62 / 2.62 | "Aur ek," 0.49 / 0.54 -> 0.51; "aur ek," 0.49 / 0.55 -> 0.52; "aur ek." 0.49 / 0.67 -> 0.58 |
| L10 | 3 | 5 | 1.28 | 2.35 | 3.91 | aakhri @ 23.75 | 3.36 / 3.36 | "Phir aakhri message..." 1.19 / 1.37 -> 1.28 |
| L11 | 9 | 15 | 3.23 | 2.79 | 4.87 | - (all-white) | 1.28 / 1.28 | "Har editor jaanta hai," 1.42 / 1.49 -> 1.46; "v1 hi final hota hai." 1.60 / 1.64 -> 1.62 |
| L12 | 5 | 7 | 1.41 | 3.54 (>3.2, monosyllables) | 4.96 | - (all-white) | 0.18 / 0.18 | "...aur phir client ne bola" 1.42 / 1.41 -> 1.41 |

w/s above 3.2 is flagged only where a line is all one-syllable words (L1, L9, L12): their syllable rate (3.7-5.0
syl/s) is the voice's normal rate (Vlad audition phrases 4.2-5.6 syl/s before the speed-up), so they are not rushed.

Hard ends and why: L1 lockup exit 2.60 · L1B 2.70 (gate: the spoken hook lands by 2.7 s; L2 is now 0.57 s later) ·
L2 before L3 (4.25) · L3 before L4 (6.583) · L4 before pin 6's thock 7.467 (7.45) · L5 before pin 8's thock 9.600
(9.55) · L6 before 11.733 · L7 before the braam hit 14.933 (14.90) · L8 before pin 17's thock 16.533 (16.50) · L9
before the D7 at 21.333 · L10 before the true silence at 25.067 (24.95) · L11 before L12 · L12 last word end + 40 ms
<= 34.093.

Placement rules for the assembler (both hooks share everything from L2, so the burned captions match both mixes):
- first word of each line on `start_target` (L12: last word END on 34.050, onset = 34.050 - measured duration);
- L2 onset never before 3.233 (f97): the pin must land first, or "Ho jayega" turns back into the client's line in hook B;
- hook A is voice-free 1.63-3.27 s (1.64 s, was 1.30): pin 2 "Aur bara." + whoosh (2.133), the lockup
  exit, the splice and pin 3 (3.200) fill it, one event at least every 1.07 s, music under; nothing to add;
- L4 onset = max(6.733, L3 end + 0.15);
- L9: fragments `Aur ek,` / `aur ek,` / `aur ek.` on 19.233 / 19.767 / 20.300 (1 frame after pins v21-v23), never
  overlapping (onset = max(placement, previous end + 0.03));
- gaps between lines >= 0.15 s (expected plan: smallest gap 0.18 s, L12 -> frame 0); no VO in 25.067-28.133;
- fallbacks if a measured line crosses its hard end (all reuse the same take, except L1B's last resort). L1B's chain,
  estimated: step 1 only shortens the audio after the measured word end (it matters if Vlad's drawl outlasts
  whisper's word end); step 2, on a read with the Kokoro scratch's two 0.15 s gaps, saves 0.20 s
  (conservative end 2.53); step 3 (कहा।, no drawl) models at 2.26 s:
  - **L1**: none expected; the brief targets <= 1.90 s, the hook rule allows <= 2.70 s, the lockup exits by 2.60 s
  - **L1B**: hard end 2.70 s (gate r1), measured on the last word end. Over: (1) trim the "kaha..." release to 40 ms; (2) close silent inter-word gaps > 0.10 s to 0.06 s at measured word boundaries (silence only, never inside a word; the Kokoro scratch had two 0.15 s gaps; closing both saves about 0.20 s at Vlad scale); (3) re-take T4 with "कहा।" (no drawl, model about -0.14 s). Same words, same order, prompt text otherwise unchanged
  - **L2**: over 4.25: onset 3.233 (f97, still after the pin); still over: L3 slides later by the overrun (at most +0.067 s, to 4.467) and L3's own fallback (the "?" beat at 0.15 s) absorbs it
  - **L3**: over 6.583: place the "?" beat at 0.15 s; still over: L4 moves later (rule in L4)
  - **L4**: onset = max(6.733, L3 end + 0.15); if it then ends after 7.45 the 7.467 thock becomes pin_thock_dark
  - **L5**: ends after 9.55: the 9.600 thock becomes pin_thock_dark
  - **L6**: none
  - **L7**: over 14.90 (braam hit 14.933): use the sub-span "Mummy bhi review karengi." placed at 13.000
  - **L8**: over 16.50: the 16.533 thock becomes pin_thock_dark; worst case the sub-span "Cinematic."
  - **L9**: planned: the pins 19.733 / 20.267 / 20.800 land on the "ek" of the fragment before them, so they use pin_thock_dark (-6, lp 1100); the line must end before the D7 at 21.333. Fragments never overlap: each onset = max(its placement, previous fragment end + 0.03 s)
  - **L10**: hard limit 24.95: trim the drawl
  - **L11**: over 32.35: place the comma beat at 0.08 s (the SLATE line keeps every word)
  - **L12**: end-anchored: onset = 34.050 - measured duration (word end + 40 ms <= 34.093)

---------------------------------------------------------------------------------------------------------------

## 5. Token table (Roman caption token <-> Devanagari TTS token, 1:1; `yes` = the line's serif keyword)

Every line was checked with `vo_chain.tokens()`: DEV and ROM counts are equal for every line and every take; L1-L10
have exactly one keyword each, L11 and L12 none (gate fix 4). No 1:n splits: "v1" <-> `वी-वन` and "26" <-> `छब्बीस` are single tokens
(whisper may hear `वी-वन` as two words; vo_chain's aligner merges 2:1). The ROM files mark keywords with `*`.

| line | i | roman (caption token) | dev (TTS token) | keyword |
|---|---|---|---|---|
| L1 | 0 | Bas | बस |  |
| L1 | 1 | ek | एक |  |
| L1 | 2 | chhota | छोटा | yes |
| L1 | 3 | sa | सा |  |
| L1 | 4 | change. | चेंज। |  |
| L1B | 0 | 26 | छब्बीस | yes |
| L1B | 1 | revision | रिविज़न |  |
| L1B | 2 | baad | बाद |  |
| L1B | 3 | client | क्लाइंट |  |
| L1B | 4 | ne | ने |  |
| L1B | 5 | kaha... | कहा... |  |
| L2 | 0 | Ho | हो |  |
| L2 | 1 | jayega. | जाएगा। | yes |
| L3 | 0 | Pop? | पॉप? | yes |
| L3 | 1 | Kisi | किसी |  |
| L3 | 2 | ko | को |  |
| L3 | 3 | nahi | नहीं |  |
| L3 | 4 | pata. | पता। |  |
| L4 | 0 | Clean. | क्लीन। | yes |
| L5 | 0 | Energetic. | एनर्जेटिक। | yes |
| L6 | 0 | Fun. | फ़न। | yes |
| L7 | 0 | Ab | अब |  |
| L7 | 1 | Mummy | मम्मी | yes |
| L7 | 2 | bhi | भी |  |
| L7 | 3 | review | रिव्यू |  |
| L7 | 4 | karengi. | करेंगी। |  |
| L8 | 0 | Bilkul | बिल्कुल |  |
| L8 | 1 | cinematic. | सिनेमैटिक। | yes |
| L9 | 0 | Aur | और |  |
| L9 | 1 | ek, | एक, |  |
| L9 | 2 | aur | और |  |
| L9 | 3 | ek, | एक, |  |
| L9 | 4 | aur | और |  |
| L9 | 5 | ek. | एक। | yes |
| L10 | 0 | Phir | फिर |  |
| L10 | 1 | aakhri | आख़री | yes |
| L10 | 2 | message... | मैसेज... |  |
| L11 | 0 | Har | हर |  |
| L11 | 1 | editor | एडिटर |  |
| L11 | 2 | jaanta | जानता |  |
| L11 | 3 | hai, | है, |  |
| L11 | 4 | v1 | वी-वन |  |
| L11 | 5 | hi | ही |  |
| L11 | 6 | final | फ़ाइनल |  |
| L11 | 7 | hota | होता |  |
| L11 | 8 | hai. | है। |  |
| L12 | 0 | ...aur | और |  |
| L12 | 1 | phir | फिर |  |
| L12 | 2 | client | क्लाइंट |  |
| L12 | 3 | ne | ने |  |
| L12 | 4 | bola | बोला |  |

---------------------------------------------------------------------------------------------------------------

## 6. TTS run (for the lead / TTS owner; this agent does not spend credits)

| order | take | lines (token span) | chars | tokens | Higgsfield prompt (Devanagari) | rom.txt |
|---|---|---|---|---|---|---|
| 1 | T1 | L1 0-4, L2 5-6, L3 7-11, L4 12-12, L5 13-13, L6 14-14 | 75 | 15 | बस एक छोटा सा चेंज। हो जाएगा। पॉप? किसी को नहीं पता। क्लीन। एनर्जेटिक। फ़न। | `Bas ek *chhota sa change. Ho *jayega. *Pop? Kisi ko nahi pata. *Clean. *Energetic. *Fun.` |
| 2 | T4 | L1B 0-5 | 36 | 6 | छब्बीस रिविज़न बाद क्लाइंट ने कहा... | `*26 revision baad client ne kaha...` |
| 3 | T2 | L7 0-4, L8 5-6, L9 7-12, L10 13-15 | 85 | 16 | अब मम्मी भी रिव्यू करेंगी। बिल्कुल सिनेमैटिक। और एक, और एक, और एक। फिर आख़री मैसेज... | `Ab *Mummy bhi review karengi. Bilkul *cinematic. Aur ek, aur ek, aur *ek. Phir *aakhri message...` |
| 4 | T3 | L11 0-8, L12 9-13, L1alt 14-18 | 87 | 19 | हर एडिटर जानता है, वी-वन ही फ़ाइनल होता है। और फिर क्लाइंट ने बोला, बस एक छोटा सा चेंज। | `Har editor jaanta hai, v1 hi final hota hai. ...aur phir client ne bola, Bas ek *chhota sa change.` |

Files written for `vo_chain.py`: `/home/user/100/workspace/jawad_reels/pehle_wala/vo/takes/T{1,2,3,4}.dev.txt` and
`.rom.txt` (one line each, tokens 1:1). Downloads go to `workspace/brand_reels/tts/hf_dl/pehle_wala/` (vo_config).

Per take:
```bash
cd /home/user/100/pipeline/jawad_reels
nice -n 10 python3 -I vo_chain.py process /home/user/100/workspace/brand_reels/tts/hf_dl/pehle_wala/T1.mp3 \
  --dev /home/user/100/workspace/jawad_reels/pehle_wala/vo/takes/T1.dev.txt \
  --rom /home/user/100/workspace/jawad_reels/pehle_wala/vo/takes/T1.rom.txt \
  --speed 1.08 --out /home/user/100/workspace/jawad_reels/pehle_wala/vo/takes/T1.wav
```
- **Alignment check (measured problem, SHARED_REQUESTS #6).** `T1.report.json` -> `unmatched` must be empty. With the
  DEV text as whisper's `initial_prompt`, the Kokoro scratch of T2 lost its whole first sentence (11/16 matched);
  re-aligning without the prompt gave 16/16, but no prompt alone was worse on T3 (7/19) and T4 (4/6). So: if
  `unmatched` is not empty, run `vo_chain.align('<T>.wav', dev, rom, prompt=' ')` and take each token from whichever
  pass has `ok=true`. A token unmatched in both passes is a mispronunciation: re-take that line only.
- **Cut and place** per §4 with 40 ms pads at word boundaries (from `<T>.words.json`). T3: L12 = tokens 9-13, cut at
  the end of `बोला` + 40 ms (the comma pause and tokens 14-18 are not part of L12); tokens 14-18 are an alternate L1
  recorded as the completion of L12: A/B it against T1's L1 by flipping the loop seam (`--stills 0,34.1` plus audio).
- Deliver `<WS>/pehle_wala/vo/pehle_wala_vo_A.wav` + `.words.json` (L1, L2-L12) and `pehle_wala_vo_B.wav` +
  `.words.json` (L1B, L2-L12) in reel seconds, -16 LUFS (BRIEF §9). Then re-run this timing table on the measured
  words and send the deltas to the sound designer.

---------------------------------------------------------------------------------------------------------------

## 7. Pronunciation risks (test first; T1 carries the top two)

| # | word | line / take | listen for | evidence so far | fallback spelling |
|---|---|---|---|---|---|
| 1 | पॉप? (Pop?) | L3 / T1 | "pop" with a short open o and a small question rise; not "paap", "poop" or "baap" | local Kokoro scratch take: whisper heard "बआप्द" / "बाप्द" (the only token that failed alignment in T1) | keep पॉप? in dev.txt for alignment but send Latin "Pop?" in the Higgsfield prompt; never पाप (= sin) |
| 2 | फ़न। (Fun.) | L6 / T1 | /f/ (lips on teeth), one clean syllable "fun"; not "phan" (फन = a snake hood) and no extra consonant | Kokoro scratch: heard "फ़न्ध" / "फन्द" (a stray consonant on a one-word sentence) | Latin "Fun." in the prompt (dev.txt keeps फ़न।) |
| 3 | छब्बीस (26 (spoken chhabbees)) | L1B / T4 | crisp "chhab-bees" as the first word of hook B (doubled b, long ee) | Kokoro scratch: heard correctly; first word of a take is where ElevenLabs is least predictable | re-take only (the hook B wording is locked by the SLATE) |
| 4 | रिविज़न (revision) | L1B / T4 | "ri-vi-zan" / "ri-vi-zhan" (nukta z), not "ri-vi-jan" | Kokoro scratch: heard रिविज़न (OK) | रिवीज़न |
| 5 | सिनेमैटिक (cinematic) | L8 / T2 | "si-ne-MAI-tik" (ae); stress on the third syllable | Kokoro scratch: heard सिनेमाटेक / सिनेमाटिक (aa instead of ae) | सिनेमेटिक, or Latin "cinematic" in the prompt |
| 6 | एनर्जेटिक (Energetic) | L5 / T1 | "e-ner-JE-tik" with the r audible | Kokoro scratch: heard एनरजेटिक / एन्जेटिक (r weak) | एनर्जैटिक |
| 7 | वी-वन (v1) | L11 / T3 | "vee-one" (van/wun) as one unit, no pause at the hyphen | Kokoro scratch: aligned OK | वीवन (still one token) |
| 8 | फ़ाइनल (final) | L11 / T3 | /f/ (nukta), "fai-nal" | Kokoro scratch: OK | Latin "final" in the prompt |
| 9 | आख़री (aakhri) | L10 / T2 | two syllables "aakh-ri"; /x/ (Urdu) or /kh/ both fine; not a dragged "aa-khi-ree" | Kokoro scratch: heard आखरी (OK) | आख़िरी (standard Hindi spelling, +1 syllable, about +0.1 s) |
| 10 | रिव्यू (review) | L7 / T2 | "ri-vyoo", the i audible | Kokoro scratch: heard रव्यू (i reduced) | रिव्यु |
| 11 | क्लाइंट (client) | L1B, L12 / T4, T3 | "klaa-int" with the n; not "khlaait" | Vlad v4 audition (vo_config take): whisper heard ख्लाईट | क्लायंट |
| 12 | मम्मी (Mummy) | L7 / T2 | "mum-mee" | Kokoro scratch: OK | none |

If a Latin fallback is used in a prompt, keep the Devanagari token in `dev.txt` (alignment is Devanagari) and note it
in the take log. The nickname JD is not spoken in this reel (if it ever is: `जे-डी`).

---------------------------------------------------------------------------------------------------------------

## 8. Hand-offs: sound and captions

**Sound designer** (pins that now sit under words; BRIEF §11 rule "pins inside VO words use the dark variants"):

| t (s) | brief cue now | change | why |
|---|---|---|---|
| 3.200 | pin_thock_dark -6 · slot_tick -12 · swish_small -10 lp 1100 (pin 3 "Thora left.") | pin_thock 0 (full; gate r1 fix 2); slot_tick and swish_small unchanged | L2 moved to 3.267 (f98): the note lands, then the editor answers. Measured on the BRIEF recipe (glass_tap -8 + impact_soft 0, lp 6000): the 1-4 kHz tail sits 21.6 dB under the hit at 67-200 ms and 29.6 dB under at 200-500 ms, the same grammar as pin 4 -> "Pop?" (133 ms) |
| 6.400 | pin_thock 0 (pin 5, cream fill) | pin_thock_dark -6 | inside L3 "...nahi pata" (expected 6.14-6.55) |
| 19.733 | pin_thock 0 (pin 21) | pin_thock_dark -6 | lands on the "ek" of the first "Aur ek" (expected end 19.75) |
| 20.267 | pin_thock 0 (pin 22) | pin_thock_dark -6 | lands on the "ek" of the second fragment (expected end 20.29) |
| 20.800 | pin_thock 0 (pin 23) | pin_thock_dark -6 | lands on the last "ek" (expected end 20.88) |
| 2.333 | hook B: ui_click 0 | -6 or hp 4000 | under "kaha..." of L1B (expected 0.10-2.56, hard end 2.70) |
| 1.667 | hook B: timeline_scrub -8 (0.667 s) | lp 1100 or hp 5000 variant | scrub chatter in 1-4 kHz under "client ne kaha" |
| 30.617 | end card glass_tap -12 | hp 5000 or -16 | tonal tap under "final hota" (L11 28.13-31.36) |
| 32.633 | (new, gate r1 fix 1, creative-director) ui_hover -14 hp 5000: the client marker re-enters | none from the script | lands on "...aur" of L12 (onset 32.639 expected / 32.633 conservative); hp 5000 keeps it out of the word band |
| 33.333 | end card reverse_swell -8 (0.8 s to 34.133) | lp <= 1000 or hp >= 5000 | under "client ne bola" (L12 32.64-34.05) |
| - | pins at 13.333, 13.867, 14.400, 16.000 (dark variants) | none | already dark in the brief; confirmed inside L7 and L8 |
| - | hero hits 14.933 braam, 25.600 payoff, 27.733 restore | none | all in VO gaps (L7 ends 14.79 expected / 14.92 conservative -> fallback; L10 ends 24.78; L11 starts 28.133) |

**Caption designer.** Snake captions solved on the expected timings with the BRIEF §10 settings (`band='lower',
y=1400`, `avoid=cap_avoid`, `hide=[(0, 2.6667)]`):

| chunk | on screen (s) | text | serif keyword | scale | ink bbox (x0, y0, x1, y1) |
|---|---|---|---|---|---|
| 0 | 3.22-4.35 | Ho jayega | jayega | 0.92 | (277, 1303, 756, 1476) |
| 1 | 4.35-5.07 | Pop? | Pop? | 1.00 | (357, 1298, 661, 1474) |
| 2 | 5.07-5.68 | Kisi ko | - | 1.00 | (361, 1345, 672, 1479) |
| 3 | 5.68-6.68 | nahi pata | - | 1.00 | (307, 1345, 711, 1476) |
| 4 | 6.68-7.95 | Clean | Clean | 0.92 | (346, 1304, 686, 1473) |
| 5 | 8.55-10.12 | Energetic | Energetic | 0.92 | (272, 1304, 747, 1472) |
| 6 | 10.75-11.98 | Fun | Fun | 1.00 | (373, 1296, 660, 1478) |
| 7 | 12.82-13.67 | Ab Mummy bhi | Mummy | 0.92 | (173, 1301, 846, 1474) |
| 8 | 13.67-14.95 | review karengi | - | 1.00 | (226, 1299, 809, 1444) |
| 9 | 14.95-17.02 | Bilkul cinematic | cinematic | 0.85 | (189, 1309, 830, 1469) |
| 10 | 19.18-19.72 | Aur ek | - | 1.00 | (361, 1345, 672, 1479) |
| 11 | 19.72-20.25 | aur ek | - | 1.00 | (363, 1347, 655, 1474) |
| 12 | 20.25-21.53 | aur ek | ek | 1.00 | (351, 1306, 683, 1479) |
| 13 | 23.45-25.43 | Phir aakhri message... | aakhri | 0.85 | (105, 1309, 914, 1470) |
| 14 | 28.08-28.91 | Har editor | - | 0.92 | (316, 1348, 716, 1474) |
| 15 | 28.91-29.69 | jaanta hai | - | 1.00 | (298, 1345, 721, 1476) |
| 16 | 29.69-30.30 | v1 hi | - | 1.00 | (395, 1347, 637, 1477) |
| 17 | 30.30-32.01 | final hota hai | - | 1.00 | (249, 1344, 769, 1477) |
| 18 | 32.59-32.99 | ...aur phir | - | 1.00 | (312, 1303, 722, 1441) |
| 19 | 32.99-34.70 | client ne bola | - | 1.00 | (245, 1343, 774, 1478) |

`check()` = [] on hook A expected timings.
`check()` = [], unplaced chunks = 0 on `gen2_B_exp.words.json`.
`check()` = [], unplaced chunks = 0 on `gen2_A_cons.words.json`.
`check()` = [], unplaced chunks = 0 on `gen2_B_cons.words.json`.

Rendered and inspected (inferno background, player and tile stand-ins; r2 proofs at 3.25, 3.8, 29.0, 30.4-31.6, 33.2,
33.55-34.1 s): every chunk sits in the lower band under the player, the widest ("Phir aakhri message...", scale 0.85)
ends at x 914 (< 930), "Bilkul cinematic" clears the JD tile. r2: chunk 0 "Ho *jayega*" now enters at 3.22 (after pin
3); chunks 17 "final hota hai" and 19 "client ne bola" are all-white at scale 1.00 (ink x 249-769 and 245-774), so the
captions add no serif word under the end card and *bhejo* stays the one glowing ask. Chunk 19 runs past DUR by design:
the loop-safe fade of SHARED_REQUESTS #3 takes it out with the end card.

---------------------------------------------------------------------------------------------------------------

## 9. Changes from BRIEF §9 (its windows were set before any take existed; at Vlad's measured rate several did not fit)

- L1B: the comma after "baad" is dropped (one breath). 6 spoken words (SLATE counted 5). Hard end 2.70 s on the measured last word (gate r1 fix 2; was 2.78): expected 2.56, conservative 2.73 -> fallback chain in section 4.
- L2: "Theek hai. Ho jayega." (1.4-1.7 s measured/modelled) cannot fit between the splice and "Pop?" while keeping hook B clear; now "Ho jayega." at 3.267 (f98, gate r1 fix 2; r1 had 2.933), two frames after pin 3 "Thora left." lands, so it is the editor's reply to a visible note in both hooks and never the client's answer to "client ne kaha...". Expected end 4.06, conservative 4.13 (hard end 4.25); L3 stays at 4.40. Pin 3's 3.200 cue returns to full pin_thock 0 dB.
- L3: "Pop karo. Matlab? Kisi ko nahi pata." is about 3.2-3.7 s at Vlad's rate (window 1.9 s); now "Pop? Kisi ko nahi pata." (4.400-6.55): the echo keeps the buzzword audible, the verdict keeps the joke. Its tail crosses pin 5 (6.400): dark thock there.
- L4: 6.60 -> 6.733 (f202) so its vowel lands as the cream fill completes (f204) and it clears L3.
- L5: 8.65 -> 8.600 (2 frames after the drums arrive).
- L7: 12.90 -> 12.867 (one-word lines and this line ran slower than the brief assumed; must end before the braam hit at 14.933).
- L8: "Cinematic. Bilkul." (about 1.7-1.9 s with the sentence break; window 1.05 s) -> "Bilkul cinematic." one breath at 15.000 (1.2-1.5 s).
- L9: periods -> commas (a running count is faster and steadier than three sentences); fragments placed 1 frame after their pins (19.233, 19.767, 20.300).
- L10: "Phir aakhri message aaya." -> "Phir aakhri message..." (the pin has not landed yet, so "aaya" was premature, and the 25.067 true silence needs margin: expected end 24.78).
- L11: colon -> comma (shorter beat); onset 28.05 -> 28.133 (f844) so its first caption chunk enters after the Ctrl+Z chip avoid window (27.95 + the solver's 0.1 s look-back). Expected end 31.36 (brief 31.00).
- L12: end-anchored at 34.050 (onset about 32.64); generated inside T3 so "bola" keeps a continuation contour.
- Keywords: one serif keyword per VO line in L1-L10 (brief section 10 marked one per chunk); L11 and L12 carry none (gate r1 fix 4), so after the payoff only *pehle wala* (27.7-29.5) and the CTA *bhejo* (29.9-34.1) glow. Chunks without a keyword render all-white, which snake_captions supports (keywords come only from explicit marks, load_words line 142-143).

---------------------------------------------------------------------------------------------------------------

## 10. Self-check

- [x] Hook spoken from 0.10 s (<= 0.30), <= 7 words (A 5, B 6), readable muted (lockups); A lands 1.63 s (1.93 cons),
      B 2.56 s (2.73 cons, gate hard end 2.70 via §4 fallbacks); banned openers absent.
- [x] Read aloud as a Pakistani viewer and as an Indian viewer: every word is shared everyday Hindustani or a creator
      loanword (ho jayega, kisi ko nahi pata, bilkul, aur ek, phir, aakhri, jaanta, client, review, final, message,
      cinematic, energetic). No Sanskritised or Persianised register, no word only one side uses. "Mummy" per the
      SLATE default; "karengi" is the respectful plural (no mocking of elders).
- [x] Never: politics, religion, India-Pakistan cues, abuse, stereotypes, "bhai log". No first-person "main".
- [x] Truth: no fact about Jawad; fictional client and brand in a labelled POV skit; numbers match the SLATE lock
      (v1 -> v27, 26 requests, "chhabbees" in hook B only, Ctrl+Z ×26 is on screen only).
- [x] House spelling: hai, nahi, kisi, jaanta, aakhri, sentence case, English words in English spelling, digits on screen.
- [x] Devanagari: nuktas where Urdu-natural (रिविज़न, फ़न, फ़ाइनल, आख़री), English loans phonetic, number spelled
      (छब्बीस), v1 as वी-वन, pauses by `, ? । ...` only; no brackets, emoji, URLs, hashtags.
- [x] Token table complete and 1:1 for every line and take (`vo_chain.tokens`); at most one keyword per line (one in
      L1-L10, none in L11/L12 after gate fix 4), each <= 12 characters.
- [x] Word budget fits (r2 re-check, unchanged): hook A 45 tokens / 46 spoken words, B 46 / 47 (target 49, cap 60), longest
      line 9 tokens (<= 12), expected VO 17.3 s of line spans in a 34.13 s reel; no expected line crosses its hard end;
      conservative overruns (L1B +0.031 s vs the gate's 2.70, L7 +0.017 s, L8 +0.002 s) have no-cost fallbacks (L1B's
      last resort is a 6-word re-take, about 2.5 credits).
- [x] Number lock (SLATE §4): spoken numbers are only छब्बीस (hook B) and वी-वन; on screen v1 -> v27, 26, Ctrl+Z ×26.
      "Aur ek" ×3 is "one more", not a count.
- [x] Loop: L12 is generated as the first half of "...bola, bas ek chhota sa change." so it ends on a continuation
      contour; it ends 0.18 s before frame 0's first word.
- [ ] After the Vlad run: measured onsets, w/s and the pronunciation list re-checked against the takes.

---------------------------------------------------------------------------------------------------------------

## 11. Open questions (for the lead)

- AI disclosure: the VO is a synthetic voice (Vlad). Default per BRIEF section 17: Instagram "AI info" label ON. Confirm with Jawad.
- Spoken CTA: DECIDED at the gate (GATE r1 section 2): no spoken CTA; the end card carries `US CLIENT KO / *bhejo*` and the VO keeps "...aur phir client ne bola" on the seam.
- Creative-director items that touch the script (not changed here): fix 1 adds the client marker under L12 from 32.633 (its ui_hover is in the SFX hand-off); fix 4 also needs the local end-card player dim to take the ad's *garam* to x0.35 under the card and on cover frame 855; fix 5 syncs BRIEF sections 7, 9, 10, 11 and packet.yaml lines 212 and 319-327 to this file (BRIEF section 11 row 3.200 -> full pin_thock).
- Higgsfield billing: per take or per character? If per character, per-line takes cost far less than the 4-take plan and give cleaner re-takes; if per take (~2.5 credits), the 4-take plan is about 10 credits.
- "Mummy" vs "Ammi" (SLATE section 7.2 default Mummy, cross-border neutral). The VO uses Mummy to match the pin "Owner ki Mummy".
- House spelling: "aakhri" (Pakistani) is used; Indian readers also read it. "jaanta" (double a) over "janta" (which also reads as "public").
