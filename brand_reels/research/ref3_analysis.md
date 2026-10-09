# Ref 3: "If you're dreaming of charging $200 a reel..." (personal-brand pitch reel). Reverse-engineered for @jawad_mp4

Role: reels-studio `reference-analyst`. This is a spec of reusable **devices** for learning the craft, not a licence to
copy. Jawad's reels keep his own story, copy, props and palette (FLAME orange to RED on near-black, IVORY type, serif
italic keyword, `@jawad_mp4`). Nothing here comes from the "Organic Fostering" or "Floret" toolkit examples: no
`neon` / `amber` / `airy` looks, no fostering props or copy.

Unless a line is marked *(inferred)* or *(eyeballed)*, every number below comes from a command run on the file. The
evidence is in `workspace/brand_reels/refs/ref3_analysis/` (git-ignored) and is listed in section 18.

---------------------------------------------------------------------------------------------------------------
## 0. TL;DR

**What it is.** A 21.1 s vertical pitch reel aimed at video editors. One male English **voiceover** (not lyrics)
runs a tight funnel: a call-out hook ("If you're dreaming of charging $200 a reel"), a mirror of the viewer's pain
(an empty profile), a reversal ("then stop dreaming"), the rule (good money needs a great-looking personal brand),
the benefit plus a joke enemy ("the guy sliding in their DM"), the method (high-quality relatable content turns
viewers into customers), and a keyword CTA ("Comment ROADMAP"). It has **12 visual worlds in 21 s** (median
1.79 s each). Each world is a different medium: a warm AI or 3D room, a cut-out on black, a grungy paper mock-up, a
photo wall, a sunlit hands plate, a glowing UI card, an editorial split panel, a neon street, a film-border frame, a
3D gem, and the gem in close-up. **Designed type lands on almost every spoken word.**

**The 5 strongest devices (all can be adapted):**
1. **Type is the caption, designed per world.** About 45 type arrivals in 21 s (about 2.1 per s), so roughly 85 % of
   spoken words appear as designed type. Each world changes the type voice: huge serif italic over tiny caps,
   heavy grotesk italic, navy condensed serif, editorial Swiss, lowercase white grotesk, display serif with RGB
   split, serif caps, techno display.
2. **Before/after mirror.** "Your page looks like this" shows an empty profile ("Unknown Editor / No posts yet").
   Five seconds later the same profile layout returns as a glowing cyan UI card with highlights and a pitch line.
   Pain and gain share one layout.
3. **Word-locked cuts.** All 11 world changes fall within -0.09 to +0.28 s of a VO word onset, and 9 of 11 fall
   within ±0.13 s. Four cuts land 0.05-0.09 s *before* the first word of a phrase (a pre-lap). Picture follows
   the voice, not a beat.
4. **Literal visual pun at about 60 % of runtime.** "...instead of the guy sliding in their DM" shows a figure
   doing a knee slide down a neon street (11.5-13.9 s), with "DM" in serif tucked behind him. It is a humour beat
   exactly where retention usually sags.
5. **Frame-stutter interleaves.** At 1.07-1.40 s, 6.77-6.94 s, 9.14 s and 14.95 s, single frames of a different
   treatment (a negative, an over-exposed version, or the next shot) alternate with the current shot. They act as
   pattern interrupts that cost no screen time. *(Flicker risk: see 16.)*

**Pacing:** 12 worlds, median 1.79 s, mean 1.76 s, 5.2 world changes per 10 s. Scene detection at 0.3 finds 12
"cuts", 4 of them in the first 3 s (1.07, 1.23, 1.33, 2.67), but three of those are one glitch transition. There is
**no measurable BPM**: autocorrelation strength is 0.11 or lower in every band, so the edit is VO-driven.
**Audio:** -14.1 LUFS integrated, LRA 2.4 LU, true peak -0.8 dBTP. VO is centred (mid -17.4 / side -29.2 LUFS) and
sits about 10.6 dB above the bed in the pauses. **Palette:** 42 % near-black (#0B0D0F) plus a **teal/orange split**
of the saturated pixels: teal 47.0 %, orange 39.9 %, red 9.6 %. It is bright overall: 21 % of pixels have V > 200
(white paper and gem worlds).

---------------------------------------------------------------------------------------------------------------
## 1. Source

| field | value |
|---|---|
| file | `workspace/brand_reels/refs/ref3.mp4` (local copy supplied by the lead; analysis only, never in a deliverable) |
| access | full video and audio, high confidence |
| container | H.264, **718x1280**, 29.97 fps (2997/100), 629 frames, 21.106 s; AAC 44.1 kHz stereo, 70 kb/s |
| bitrate | video 772 kb/s (Instagram grade). Fine grain is destroyed (see 11) |
| cadence | **24p material in a 30p file**: 150 of 629 frames are near-duplicates, and the commonest gap between duplicates is 5 frames (93 times). It was cut on a 24 fps timeline and exported at 29.97 |
| scale | pixel numbers below are re-scaled to a 1080-wide canvas (x 1.504) |
| accessed | 2026-10-08 |

---------------------------------------------------------------------------------------------------------------
## 2. Numbers

| metric | value | how |
|---|---|---|
| scene cuts @0.3 | 12: 1.068, 1.235, 1.335, 2.669, 4.338, 4.404, 6.773, 6.940, 9.142, 13.881, 16.884, 18.986 | ffmpeg `select=gt(scene,0.3)` |
| scene cuts @0.2 / @0.4 | 19 / 9 | same |
| scene-detect shots @0.3 | 13 shots, mean 1.62 s, median 1.67 s, min 0.07 s (flicker frames), max 4.74 s | pacing script |
| **visual worlds (manual, checked on 30 fps strips and per-frame stats)** | **12**: boundaries 1.068, 2.669, 4.338, 5.506, 8.442, 9.176, 11.545, 13.881, 14.982, 16.884, 18.986 | `transitions_manual.txt` |
| world length | lengths 1.07, 1.60, 1.67, 1.17, 2.94, 0.73, 2.37, 2.34, 1.10, 1.90, 2.10, 2.12 s; **mean 1.76 s, median 1.79 s** | |
| world changes per 10 s | 5.2 (manual) / 5.7 (scene-detect @0.3, inflated by flicker frames) | |
| changes in the first 3 s | the glitch at 1.07-1.40 (one transition, three detections) and the white wipe at 2.67 | |
| hard cuts vs designed transitions | 3 plain hard cuts (13.88, 16.88, 18.99). The other 8 are glitches, wipes, whips, dissolves or stutters | section 8 |
| BPM | **none**: onset-envelope autocorrelation is 0.10-0.16 in the full, low, high and side bands; "best lags" disagree (0.46-0.51 s) | numpy AC |
| VO rate | 70 words in 20.88 s = **3.35 words/s**. Per sentence: 3.2 / 3.9 / **4.9** / 3.1 / 3.0 | faster-whisper word stamps |
| VO pauses > 0.15 s | 6: 0.24 s (4.16), 0.32 (5.28), 0.32 (7.46), 0.52 (9.92), 0.32 (13.30), 0.40 (18.52) | |
| on-screen type arrivals | about 45, so about 2.1 per s; about 60 of 70 spoken words shown *(eyeballed from 3 and 10 fps strips)* | |
| loudness | **-14.1 LUFS** I, **LRA 2.4 LU**, **TP -0.8 dBFS**; mid -17.4 LUFS, side -29.2 LUFS | ffmpeg ebur128 |
| speech vs bed | word RMS -18.0 dB vs pause RMS -28.6 dB (medians), about **10.6 dB** | 100 Hz HP RMS |
| designed low-end hits | 9 stereo booms (side-channel sub peaks) at 0.27, 1.59, 2.98, 5.93, 9.39, 12.02, 14.30, 15.41, 17.10 s, about one per 2.3 s | STFT band envelopes |
| air / whoosh events | 23 side-channel air peaks (6-16 kHz), about 1.1 per s | same |
| onset density | full 3.05/s, low (< 150 Hz) 3.95/s, high (> 5 kHz) 2.38/s, side 1.95/s | spectral flux |
| flash frames | 1.068-1.401 (6-frame black/negative alternation, luma 8 to 106); 2.669 (white, luma 246, held: start of the paper world); 6.773 / 6.840 (over-exposed interleave, luma 81 to 169); **9.142 (1-frame bright negative, luma 24 to 212 to 45)**; 14.948 (1-frame interleave of the next shot) | per-frame stats |
| black floor | YMIN median 17, YLOW (10th pct) median 30. Letterbox and film-border sections reach YMIN 0 (super-black bars); the paper world never goes below YMIN 36 | ffmpeg signalstats |
| letterbox | 9.18-11.51 s: bars grow from 283 to 332 rows each (of 1280), so the window closes from 718x714 to 718x616 (a slow squeeze) | row-mean scan |
| bright pixels | 21.2 % of all sampled pixels V > 200; 42.0 % V < 40 | HSV at 2 fps |

---------------------------------------------------------------------------------------------------------------
## 3. Transcript: voiceover, not lyrics

**Classification: spoken voiceover.** The evidence:
- faster-whisper `small` int8, language auto: **en, p = 0.997**, avg_logprob -0.15 on every segment, no_speech 0.02.
- Prosody is conversational: conditional sentences, no rhyme, no sustained sung vowels.
- The voice is centred mono: mid -17.4 LUFS against side -29.2 LUFS, and the side spectrogram has no speech
  harmonics (`audio/spec_side.png`).
- The voice is male: autocorrelation F0 median 127 Hz, lower quartile 112 Hz (the upper quartile of 201 Hz is
  octave errors from music bleed).
- Delivery is fast, confident and "coach" toned. Whether it is human or TTS cannot be known from the file.

| # | start-end (s) | text (faster-whisper; on-screen wording in brackets where it differs) |
|---|---|---|
| 1 | 0.00-5.28 | If you're dreaming of charging $200 a reel and your page looks like this, then stop dreaming. |
| 2 | 5.60-9.92 | If you want to charge your clients good money, then you need a great looking personal brand. [screen: "if you wanna charge your clients"] |
| 3 | 10.44-13.30 | This will make them trust you instead of the guy sliding in their DM. |
| 4 | 13.62-17.50 | And that's possible by posting high quality relatable content which turns your |
| 5 | 17.50-20.88 | viewers into customers. Comment roadmap and I'll show you how. [screen: "just comment "ROADMAP" ... I'll show you how"] |

Word stamps (s): If 0.00 · you're 0.22 · **dreaming 0.36** · of 0.68 · charging 0.90 · **$200 1.26** · a 1.82 · reel 2.24 ·
and 2.54 · your 2.88 · **page 3.00** · looks 3.26 · like 3.52 · this 3.80-4.16 | then 4.40 · stop 4.56 · **dreaming 4.86-5.28** |
If 5.60 · you 5.70 · want 5.82 · to 5.94 · **charge 6.02** · your 6.28 · clients 6.48 · **good 6.86** · money 7.14-7.46 | then 7.78 ·
you 7.90 · need 8.04 · a 8.18 · **great 8.32** · looking 8.60 · **personal 8.90** · brand 9.46-9.92 | This 10.44 · will 10.56 ·
make 10.70 · them 10.86 · **trust 11.02** · you 11.32 · instead 11.60 · of 11.94 · the 12.08 · **guy 12.18** · sliding 12.36 · in 12.64 ·
their 12.88 · **DM 12.98-13.30** | And 13.62 · that's 13.74 · **possible 13.94** · by 14.40 · posting 14.60 · high 14.88 · **quality 15.24** ·
relatable 15.70 · content 16.14 · which 16.80 · **turns 17.08** · your 17.34 · viewers 17.50 · into 17.80 · **customers 18.02-18.52** |
Comment 18.92 · roadmap 19.30 · and 19.70 · I'll 20.22 · show 20.36 · you 20.54 · how 20.70-20.88.
(**Bold** = a designed low-end boom lands within about 0.3 s, see 12.) Raw output: `audio/transcript_small.json`.

---------------------------------------------------------------------------------------------------------------
## 4. Timed beat table

Px values are cap heights on a 1080-wide canvas *(eyeballed against pixel rulers, `full/type_*.jpg`, ±10 %)*.

| t0-t1 (s) | world / shot | VO | on-screen type (px, style) | device | transition out | audio event |
|---|---|---|---|---|---|---|
| 0.00-1.07 | warm abandoned concrete room, god rays from a window, figure frozen mid-backflip (slow motion), warm grade | If you're dreaming of charging | "IF YOU'RE" / "OF CHARGING" white grotesk caps **33-35 px**; "**Dreaming**" white high-contrast serif italic, **cap 175 px, 825 px wide**, behind the figure | text visible on **frame 0**; subject occludes the keyword; exposure lift over the first 6 frames (luma 92 to 105) | **glitch interleave** 1.068-1.401: hook frames alternate with black frames carrying a cyan-negative "Dreaming", then smear-dissolve | VO + boom at 0.27 (first audio at 0.12 s) |
| 1.40-2.67 | the same figure, cut out with an ivory outline, on black; rides a rising orange-red line; ghost copy below-left; defocused red type far back | $200 a reel and | "$200 / a reel" handwritten-italic white, twice along the line (about 45 px) | cut-out on a price curve; echo trail; RGB fringe on the line | white smear wipe up from the bottom (2.636), then a **3-frame white card with a line and a ring-slash icon** (2.669-2.736) | boom 1.59 |
| 2.67-4.34 | grungy white photocopy "paper" with burnt edges and dust: a mock social profile, "Unknown Editor / Cheap video editing services", 4 grey highlight circles, "No posts yet" | your page looks like this | profile text bold italic grotesk about 30 px; "**this...**" cyan (#32BCD1) bold italic grotesk about 80 px; "No posts yet" black bold about 55 px; cyan hand scribbles | **pain mirror**; elements rack-focus in one after another (3.0, 3.33, 3.67 blur, 4.0 sharp) | **diagonal black bar wipe** (1 frame at 4.304) into a defocused landing | boom 2.98 ("page"); whoosh peaks 3.60, 4.12 |
| 4.34-5.47 | tilted wall of film-strip frames (stills of the hook room), a black type band across it, an orange curve through the band | then stop dreaming | "then" / "stop" white grotesk lowercase about 30 px; "**Dreaming!**" heavy grotesk italic **cap 84 px**; script "d r e a m i n g" with wide tracking above and below at 40 % | **callback** to the hook as a contact sheet; **typeface switch** serif "Dreaming" to grotesk "Dreaming!"; the wall rotates about 0.3 deg/frame | **skew/whip blur** of the band (5.405-5.472) into a light beam | whoosh 4.63, 5.15 |
| 5.51-8.44 | grey wall, diagonal sun beam, two reaching hands (a "Creation of Adam" homage), one holding cash; thin construction circles and "+" registration marks; blurred micro-type block at the bottom | If you want to charge your clients good money, then you need a great | "if you wanna / **charge your** / clients" navy (#162139) grotesk, bold italic middle line (x-height about 45 px); "then you need a" navy bold x-height about 38 px; "**Good Money**" navy condensed serif, **cap about 80 px**, x 420-1015 | text block fades in as one (5.6-5.8) *ahead* of the VO; "Good" (6.7) and "Money" (7.0) arrive word by word about 0.15 s *before* the word; ghost-grey "need" before it fills | **over-exposed interleave** 6.773-6.940 (3 bright frames), then the image snaps sharper and the geometry appears; out: **lights-off dissolve** 8.21-8.44 | boom 5.93 ("charge"); whoosh 6.08, 6.39, 6.92 |
| 8.44-9.18 | black void; glowing cyan "profile" card (star icon, "Apex Editor", 3 pitch lines, 4 ring buttons, 3 tiles) pushes in about 3x in 0.55 s *(eyeballed)* | looking personal | UI text about 35 px with heavy bloom and starburst rays | **after state of the mirror**: same profile anatomy, now lit | **horizontal whip** (9.01-9.11) plus a **1-frame bright negative preview** of the next layout (9.142) | |
| 9.18-11.55 | letterbox window (slowly closing) with an editorial white panel sliding in from the left; 3D phone with the glowing card on the right; giant blurred letters behind | brand. This will make them trust you | "**Personal Brand**" black Swiss bold grotesk, tight, **cap about 72 px**, from x about 32; the part of "Personal" over the dark side turns white (split-colour type); definition paragraph italic grotesk x-height about 16 px; "this will make them" about 22 px; "*trust you*" italic about 50 px, ghost-grey then ink | **split panel**; **colour-crossing type**; hairline scribble curves; letterbox squeeze | **horizontal whip right** (11.44-11.51), motion-blurred landing | boom 9.39 ("brand"); 0.3 s low-band drop at 10.0-10.3 (breath before the benefit) |
| 11.55-13.88 | neon night street (teal fog, red-orange window neon, katakana sign, wet ground): a figure knee-slides toward camera with spray | instead of the guy sliding in their DM. And that's | white bold grotesk lowercase, x-height about 51 px, at y about 1160-1240: "instead of" / "the guy" / "sliding in their"; the next word sits ghost-grey until spoken; "**DM**" white high-contrast serif about 150 px partly behind the figure | **literal pun** on "sliding"; occlusion; defocus pulse on "DM" (12.98) | **horizontal glitch slices** (13.847), then a hard cut to black | boom 12.02 ("guy"); dip at 13.3-13.6 (pre-drop silence) |
| 13.88-14.98 | black **film-border template** (medium-format edge print with stock name, frame numbers, arrows); teal smoke ribbons | possible by posting | "**Possible**" cream (#FCEAD5) display serif with swash, **cap about 270 px**, 805 px wide, arrives from the left with motion blur and **RGB split**; "by posting" white bold grotesk x-height 42 px | film frame as a "chapter" marker; huge serif over small grotesk (6.4x) | **1-frame stutter interleave** of the next shot (14.948), then cut | boom 14.30 ("possible"), the loudest low end after a 0.3 s gap |
| 14.98-16.88 | pale seamless with a dark teal light falloff; small dark faceted 3D gem centred | high quality relatable content | "HIGH / QUALITY" **rust serif caps** about 45 px; "RELATABLE / CONTENT" dark teal serif italic caps about 45 px, opposite corner | per-letter blur-in; **light band sweeps off** (15.75), 0.35 s dark, light rises back from the bottom (16.2) | **hard punch-in cut** on the same gem (16.884) | boom 15.41 ("quality") |
| 16.88-18.99 | gem close-up tilted about 35 deg, chromatic dispersion edges; giant blurred serif letters ("QUAL..." top, "...BLE" bottom) as foreground/background depth echoes | which turns your viewers into customers | "WHICH TURNS YOUR / VIEWERS INTO" dark teal condensed bold caps, **cap about 39 px**, word spaces almost removed; "**CUSTOMERS**" light high-contrast serif italic caps **cap about 105 px** (2.7x), orange fringe | **ghost-ahead word build** that trails the VO by 0.2-0.4 s (`cuts/customers_build.jpg`); depth echo type | **hard cut** to black film frame (18.986) | boom 17.10 ("turns"); **bed drops out 18.6-19.0** (M -27.1 LUFS) |
| 18.99-21.11 | black film-border frame again (bookend), drifting dust | Comment roadmap and I'll show you how. | "just comment" small teal about 25 px; "**"ROADMAP"**" teal (#89BEA6) squared techno display, **cap about 68 px**, glow; "I'll show you how" teal about 30 px | letters **decode / scramble in** (19.2-20.3) while the line drifts right; the video ends 0.22 s after the last word, mid-motion | (loops to the hook) | lighter bed, no boom; ends with no tail |

---------------------------------------------------------------------------------------------------------------
## 5. Hook (0.0-2.0 s), frame by frame (`sheets/sheet3fps_01.jpg`, `cuts/strip_0.90.jpg`)

| t (s) | what the viewer gets |
|---|---|
| 0.000 | **The full message is already on screen**: "IF YOU'RE **Dreaming** OF CHARGING" over a cinematic room with a body in mid-air. No black first frame and no build-in. Luma 92 rises to 105 by 0.2 s (a soft light-on) |
| 0.12 | VO starts at full level together with the first low boom (0.27) |
| 0.00-1.03 | essentially one still: the backflip in slow motion, the figure covering the middle of "Dreaming". The eye reads the 825 px keyword, then the small caps |
| 1.068-1.401 | **pattern interrupt**: 6 frames alternate between black with a cyan-negative "Dreaming" and the hook (luma 8 / 96 / 8 / 97), then a smear-dissolve into black |
| 1.43-2.0 | the same figure returns as a **cut-out sticker** on black, riding a glowing red-orange curve, with "$200 a reel" annotations exactly when the VO says "$200" (1.26-1.82); boom at 1.59 |

**Hook formula:** a conditional call-out of a desire ("If you're dreaming of [price]") plus the viewer's current
reality ("and your page looks like this") plus a command reversal ("then stop dreaming"). The first 4 words of the VO
are on screen at frame 0, so the hook works with the sound off. The 2 s window contains 2 world states and 2 booms.

---------------------------------------------------------------------------------------------------------------
## 6. Story structure (21 s funnel)

| beat | time | % of runtime | job |
|---|---|---|---|
| 1. Call-out hook (desire) | 0.0-2.7 | 0-13 % | name the dream with a concrete number |
| 2. Mirror (pain) | 2.7-4.3 | 13-20 % | show *their* empty profile, so the viewer recognises themselves |
| 3. Reversal | 4.3-5.5 | 20-26 % | "stop dreaming": callback to the hook imagery, now flattened into a contact sheet |
| 4. Rule | 5.5-9.9 | 26-47 % | good money needs a great-looking personal brand: the mirror is answered by the glowing "after" profile |
| 5. Benefit + enemy (humour) | 10.4-13.3 | 49-63 % | trust vs "the guy sliding in their DM" (a visual pun at the mid-point sag) |
| 6. Method | 13.6-18.5 | 64-88 % | post high-quality relatable content, which turns viewers into customers (the "how" is withheld) |
| 7. CTA (lead magnet) | 18.9-20.9 | 90-99 % | comment a keyword to get the roadmap by DM; ends 0.22 s after the last word, so the loop starts at once |

Three micro-dropouts in the bed (about 0.3-0.5 s at 10.0, 13.4 and 18.7 s) sit right before beats 5, 6 and 7. The
picture world always changes with the beat, and the type voice changes with the world.

---------------------------------------------------------------------------------------------------------------
## 7. Typography system

**Principle:** there is no single caption style. Every world has its own type voice, but four rules hold throughout:

1. **Two-voice lockup with an extreme size ratio**: a small grotesk carrier plus one huge serif keyword. Measured
   keyword-to-carrier ratios: hook "Dreaming" 175 px vs caps 34 px (**5.1x**); "Possible" cap 270 px vs "by posting"
   x-height 42 px (**6.4x**); "CUSTOMERS" 105 px vs caps 39 px (**2.7x**); "Good Money" 80 px vs 38 px (**2.1x**).
2. **The keyword is the word the VO stresses**, and it is the word the boom lands on (Dreaming, $200, page, Good
   Money, Personal Brand, DM, Possible, quality, customers, ROADMAP).
3. **Ghost-ahead reveal**: the next word appears at about 25-35 % opacity in grey, then fills to full ink or white as
   it is spoken. Seen at "trust you", "sliding in their", "then you need", "WHICH TURNS YOUR / VIEWERS INTO". Sync is
   within about ±0.3 s: on the money plate the type **leads** the VO by about 0.15 s; on the gem close-up it
   **trails** by 0.2-0.4 s.
4. **Every arrival is a focus event**: blur to sharp (rack focus) or motion-blur slide. Nothing pops in at full
   sharpness. Exits blur out or are taken by the transition.

**Faces seen** *(identification inferred; the exact fonts are unknowable)*:

| role | look | where |
|---|---|---|
| high-contrast serif italic, display weight | "Dreaming", "DM" | hook, street |
| display serif with swash (didone-like) | "Possible" | film frame |
| condensed light serif, roman and italic caps | "Good Money", "HIGH QUALITY", "CUSTOMERS" | money plate, gem |
| neo-grotesk bold / bold italic, tight tracking (about -0.04 em) | "Dreaming!", "charge your", "Personal Brand", "sliding in their", "WHICH TURNS YOUR" | everywhere |
| condensed light italic grotesk (body) | the definition paragraph | split panel |
| squared techno display | "ROADMAP" | CTA |
| handwritten script with extreme tracking | "d r e a m i n g" echoes, "$200 a reel" | filmstrip, price line |

**Colour of type** follows the world: white or cream on dark, navy on the slate plate, ink and rust on the pale gem
world, teal on the CTA. Contrast (WCAG): "Possible" 10.8:1, "CUSTOMERS" 9.2:1, "ROADMAP" 8.3:1, "HIGH QUALITY"
about 5.5:1, but "Good Money" only **1.5:1**, "charge your" **1.3:1** and "this..." **1.8:1** (see 16).

**Layout:** key type sits in the middle band (y about 870-1290 on 1080x1920) almost every time. The lower third is
empty except the street lines (y 1160-1240) and decorative micro-type (y about 1540-1590). Safe-zone breaches
(`sheets/safezones.jpg`): "Good Money" reaches x about 1015 at y 1205-1290, inside the right-hand like/comment
column; "Personal Brand" starts at x about 32, outside the 70 px margin.

---------------------------------------------------------------------------------------------------------------
## 8. Transitions catalogue (11 world changes plus 2 in-world events)

| t (s) | type | build | VO alignment |
|---|---|---|---|
| 1.068-1.401 | glitch interleave: 1-frame alternation with a black/cyan-negative frame, then smear-dissolve | 6 frames | inside "charging" (+0.17 s) |
| 2.636-2.736 | white smear wipe from the bottom plus a 3-frame graphic card (line, then ring-slash icon) | 4 frames | 0.13 s after "and" |
| 4.304-4.338 | diagonal black bar wipe (1 frame), defocused landing | 1-2 frames | **-0.06 s before "then"** |
| 5.405-5.506 | skew + whip blur of the type band | 3 frames | **-0.09 s before "If"** |
| (6.773-6.940) | in-world over-exposed interleave, focus snap | 5 frames | under "clients/good" |
| 8.208-8.442 | **lights-off dissolve**: the beam plate darkens while the glowing UI fades up | 7 frames | on "great" (+0.12) |
| 9.009-9.176 | horizontal whip plus a 1-frame bright negative preview | 5 frames | on "personal" (+0.28) |
| 11.444-11.545 | horizontal whip right, motion-blurred landing | 3 frames | **-0.05 s before "instead"** |
| 13.847-13.881 | horizontal glitch slices, hard cut | 1 frame | **-0.06 s before "possible"** |
| 14.948-14.982 | 1-frame stutter interleave of the incoming shot, then cut and light bloom-in | 2 frames | on "high" (+0.10) |
| (15.75-16.25) | in-world light-band sweep off and back on (0.35 s near-dark) | 15 frames | under "relatable" |
| 16.884 | **hard punch-in cut** (same object, closer) | 0 | on "which" (+0.08) |
| 18.986 | hard cut to the bookend film frame | 0 | on "Comment" (+0.07) |

Transitions are short (median 3 frames). They never use a full cross-dissolve, and most of them carry motion blur
in the direction of the next layout.

---------------------------------------------------------------------------------------------------------------
## 9. Camera, 3D and imagery

**Sources** *(inferred)*: AI-generated or 3D-rendered stills and short clips (hook room, hands plate, neon street), a
3D phone and a 3D faceted gem (refraction plus dispersion fringes), and 2D/2.5D motion graphics (mock profile,
filmstrip wall, film border, UI card).

**Camera language** *(eyeballed from 10 and 30 fps strips; optical-flow medians are about 0 because static black or
overlay areas dominate, so they are not used)*:
- Mostly **locked plates with something moving inside**: a slow-motion flip, a figure riding a line, hands reaching,
  a knee slide, a gem tilting.
- Push-ins: the UI card scales about 3x in 0.55 s; the gem gets a cut-based punch-in.
- One rotating 2.5D move: the filmstrip wall at about 0.3 deg/frame plus parallax.
- **Rack focus is the main "camera" tool.** Almost every text or element arrival is a defocus-to-sharp, and the
  street has a defocus pulse on "DM".
- Depth: three layers in nearly every world (blurred far type or bokeh, the subject, sharp near type), plus giant
  defocused letters as foreground/background echoes on the gem.

**3D devices worth noting:** the subject occludes the keyword (hook, "DM"); the type sits *in* the space; the gem has
chromatic dispersion; the phone is shown at an angle with an emissive screen.

---------------------------------------------------------------------------------------------------------------
## 10. Colour grade (k-means at 2 fps; `palette_swatches.png`)

Overall, k = 8: **#0B0D0F 41.5 %** (near-black, background), **#2D3439 20.4 %** (slate shadows), **#C8CDC4 12.0 %** and
**#F2F4ED 10.4 %** (pale paper/seamless whites, cool-tinted), #446D75 4.9 % and #8AA2A2 4.7 % (teal fog/gem),
#724A33 3.9 % and #D09D69 2.3 % (warm room / hook highlights).

Saturated pixels (S > 90, V > 60) are 13.9 % of the frame. Of those, **teal/cyan 47.0 %, orange 39.9 %, red 9.6 %**,
blue 3.2 %: a teal-and-orange film split, but distributed **by world**, not within a frame.

| world | dominant clusters (k = 4) | temperature |
|---|---|---|
| hook room | #734A31 33 %, #3D2920 31 %, #CB8D5B 19 %, #EDCC92 17 % | hot amber, lifted blacks (YLOW 49) |
| $200 cut-out | #0E0E10 89 %, #40201F 8 % | black + red-orange accent |
| paper profile | #ECEFE7 65 %, #FEFEFD 20 %, #AABEB9 13 % | cold white, cyan accent |
| filmstrip wall | #191918 60 %, #563F33 17 %, #A27455 12 %, #E8D9AC 11 % | warm (callback to the hook) |
| money beam | #3C4045 46 %, #282B30 37 %, #EDECE7 11 % | neutral slate, navy type |
| UI card | #0C0E0E 89 %, #21393B 7 %, #97D6D7 2 % | black + cyan glow |
| split panel | #050606 67 %, #E7EFEB 13 %, #273739 13 % | black / white / teal |
| neon street | #13161C 67 %, #253B4A 22 %, #537582 8 % | teal night, red neon |
| film frame | #060706 83 %, #252B26 9 % | black + cream type |
| gem wide / close | #C0C5BF 39 %, #061116 35 %, #184955 14 % / #C9CEC8 58 %, #87A5A7 18 % | pale + deep teal |
| CTA | #050607 56 %, #0A1012 40 % | black-teal |

**Grade logic:** "dream / past" moments are warm amber (hook, callback wall); "reality / method" moments are cold
teal and slate. The temperature flip carries the story as much as the words do.

---------------------------------------------------------------------------------------------------------------
## 11. Texture and finish

- **Grain:** essentially gone after encoding. High-pass noise std in flat areas is 0.12-0.51 8-bit levels. Texture is
  carried by **large overlays** that survive compression: grungy photocopy borders and dust on the paper world,
  drifting dust specks on the CTA, the film-border template, hand scribbles, smoke ribbons.
- **Halation / bloom:** strong on the UI card (starburst rays from text) and on "Possible"; the hook has soft window
  bloom and god rays.
- **Chromatic aberration:** used as an accent, not globally: on the price line, "Possible", the gem edges,
  "CUSTOMERS" (orange fringe) and the micro-type blocks.
- **Light leaks:** none in the classic sense. Light is shaped in-scene instead: the sun beam, the light band on the
  gem, the window rays.
- **Vignette:** content-driven. The paper world uses burnt dark edges (corner/centre luma 0.88-0.95); the dark worlds
  carry 0.13-0.45 corner/centre ratios.
- **Motion blur:** heavy on every arrival and transition. Whips use 3-5 frames of directional smear.
- **Blacks:** legal-ish in content (YMIN about 17) but **super-black (YMIN 0)** in the letterbox bars and film border.

---------------------------------------------------------------------------------------------------------------
## 12. Audio layers (`audio/spec_full.png`, `audio/spec_side.png`, `audio/bands.json`)

| layer | evidence | role |
|---|---|---|
| VO (male, about 127 Hz F0, centred) | speech harmonics only in the mid; mid -17.4 vs side -29.2 LUFS | carries the edit; about 10.6 dB over the bed |
| bed: sustained pad / drone | side channel holds a steady 200-600 Hz band with partials around 1-3 kHz for the whole reel; no periodic transients | mood, no beat (autocorrelation 0.11 or lower) |
| low-end booms (stereo sub hits / impacts) | side-sub peaks of -16 to -23 dB at 0.27, 1.59, 2.98, 5.93, 9.39, 12.02, 14.30, 15.41, 17.10 s, against a -40 to -60 dB floor | keyword punctuation, one per about 2.3 s |
| air whooshes / textures | 23 side-air (6-16 kHz) peaks, about 1.1 per s, clustered at transitions (4.12/4.63, 9.39, 11.34, 13.91, 14.25) | sell whips and glitches |
| micro-dropouts | low bands fall 15-25 dB for about 0.3-0.5 s at 10.0-10.3, 13.3-13.6 and 18.6-19.0 (M -27.1 LUFS at 19.0) | "breath" before each section turn; the biggest is right before the CTA |
| a possible light pulse | 5 side-air peaks about 0.51-0.52 s apart from 3.6 to 5.15 s (about 117 BPM) and none after 7 s | *low confidence: may be a ticking texture, not a beat* |

The mix is loud and flat: -14.1 LUFS, LRA only 2.4 LU, TP -0.8 dBTP. The end has **no tail**: the last word ends at
20.88 s and the file ends at 21.106 s.

---------------------------------------------------------------------------------------------------------------
## 13. Pacing against the audio

- **Cuts follow words, not beats.** Offsets from the nearest word onset are: -0.09, -0.06, -0.06, -0.05 (four
  pre-laps on phrase starts), +0.07, +0.08, +0.10, +0.12, +0.13, +0.17 and +0.28 s.
- **Booms follow keywords, not cuts.** For example, the cut lands at 13.88 and the boom at 14.30 ("possible"); the
  cut lands at 14.98 and the boom at 15.41 ("quality"). The boom marks meaning, and the transition marks structure.
- **Speed follows the argument.** VO speeds up to 4.9 words/s on the punchline sentence (benefit + joke) and slows
  to about 3 words/s on the method and the CTA, where comprehension matters.
- **Dropouts mark turns.** The bed drops for 0.3-0.5 s before the benefit, the method and the CTA.
- **Hold lengths:** the longest world (2.94 s) is the "rule" beat, which needs the most reading; the shortest
  (0.73 s) is the glowing profile, a reveal flash.

---------------------------------------------------------------------------------------------------------------
## 14. Ending / CTA

The CTA is a **comment-keyword lead magnet** ("Comment ROADMAP and I'll show you how"), implying a DM automation. It
is staged in the **same film-border frame as "Possible"** (a visual bookend between method and ask). The keyword
decodes letter by letter in a techno face, and the reel **cuts out 0.22 s after the last word**, before the type
fully settles, so the autoplay loop returns to the hook immediately. There is no logo card and no handle.

**For Jawad:** borrow the bookend frame, the dropout before the ask and the decode, but keep the house end card:
`@jawad_mp4` settled for at least 1.5 s (brand rule). Use a keyword CTA only if his DM automation really exists
("Comment JD" or a new keyword). For the loop, match the last frame's darkness and colour to frame 0 instead of
cutting the end card short.

---------------------------------------------------------------------------------------------------------------
## 15. Steal like an artist: 15 techniques adapted for Jawad's flame/ember brand

Brand system (from `pipeline/jawad_reels/project.json` and the `jawad-brand-reels` skill): NIGHT_0 #070404 /
NIGHT_1 #170A07 world, SMOKE #2A1A15, PLUM #4A0E08, **FLAME #FF6A1A**, **RED #F2312B**, EMBER #B3120E, GOLD #FF9F1C,
AMBER #FFB547, **IVORY #FFF3E6** type, ASH #A8978C secondary. Keyword `jw_key` (Instrument Serif Italic, flame
gradient and glow), carriers `jw_caps` / `jw_caps_bold` (Poppins), UI `jw_mono`. Looks: `ember`, `noir_ember` (in
`jawad_kit`) plus the colorist's `jw_*` keys. Never `neon` / `amber` / `airy`, never the fostering props.

**The colour translation of this reference:** it flips warm (dream) to teal (reality). Jawad's version flips
**`noir_ember` (near-mono warm black, the "before")** to **`ember` (full flame and red, the "after")**. This keeps
red-orange at 60 % or more of saturated pixels and drops teal entirely, or keeps it as a 10 % or smaller cool accent
taken from the violet darks of his "yaadein" cover.

| # | technique | why it works | build it (Reels Studio toolkit / Blender) |
|---|---|---|---|
| 1 | **Frame-0 hook card with the subject occluding a huge serif keyword**: Jawad's cut-out in a warm dark room, the keyword behind him, tiny IVORY caps carriers, and no build-in | the whole hook reads on frame 1 with the sound off; occlusion proves depth | keyword `T.render(word, 'jw_key', px=240-280)` drawn first (`ts.draw_plane` at z +200), then Jawad's alpha cut-out (face-compositor `faces25d` from `charsheet/crops/street_fullbody_powerpose.png`, FLAME rim) in front, carriers `jw_caps` about 34-40 px. Room: Blender bpy (concrete box, window area light at 2 threads, CPU) or `K.background('ember')` + `K.god_rays(cv, window_xy, strength=0.5)`. Light-on: `K.post(..., exposure=K.lerp(0.85, 1.0, K.ramp(t, 0, 0.2, 'out_cubic')))`. House ratio is 1.3-1.8x; push to about 3x **only on the hook card** (creative director to approve) |
| 2 | **Stutter interleave (≤ 3 alternations) as a pattern interrupt**: single frames of a treated or next shot alternate with the current one | interrupts without spending screen time; gives SFX a hit point | pure-function switch in `draw(t)`: `n = round(t * 30); if t0 <= t < t0 + 0.2 and n % 2: return treated(t)`; treated = an ember-negative (luminance-inverted, mapped NIGHT to FLAME) + `K.chroma(cv, 2.0)`. **Keep luminance swings ≤ about 20 %** and 3 flashes/s or fewer (see 16). SFX `glitch_short` per flip |
| 3 | **Cut-out riding a glowing curve with ghost echoes** (the "$200 a reel" device) | a number or goal becomes a path the hero climbs; echoes show the travel | curve: `ui.stroke_mask` of a spline + `ui.trim_polyline(p, 0, u)` for the draw-on, FLAME core with `K.glow` (or `J.underline` geometry with `arc`); hero = Jawad cut-out with a 3 px IVORY outline (dilate the alpha) moved along the polyline by arc length; ghosts = the same sprite at earlier `u` with opacity 0.25 / 0.12; annotations in `jw_key` about 60 px. Truth: no real prices unless Jawad gives them; label a hypothetical as "POV" or "socho agar" |
| 4 | **Before/after profile mirror**: the viewer's "empty" page (cold, broken, `noir_ember`) answered 4-5 s later by the same layout re-lit in flame | instant self-recognition, then a visible promise; one layout means zero re-reading | `ui.app_window(header=..., title=..., look='noir_ember')` with grey `ui.chip` circles and an empty grid, then the same window in `'ember'` with `win.face_at(sweep=(t * 0.4) % 1)` comet edges, lit chips and a play-head. Generic UI only: no Instagram logo or clone, invented neutral handle, **no fake view counts**. Replace the white paper world with **charred paper on black** (procedural burnt edge: `K._noise_tile` threshold + EMBER glow on the burn line) |
| 5 | **Callback contact-sheet wall**: the hook's frames come back as a tilted wall of stills behind the reversal line | rewards attention; for an editor the "timeline wall" is native and on brand | render 6-9 earlier frames, load them with `F.still(...)`, place them as `sc.plane` cards in a `K.Scene` grid with `rot=(0, 0, -14)` and a slow `K.Cam.orbit` roll; type band = a black `K.rrect_alpha` plane with `T.Glyphs(line, 'jw_caps_bold').slam`; tracked script echoes above and below at 40 % (`T.render(..., 'jw_key', tracking=0.6)`) |
| 6 | **Typeface switch that carries meaning**: the same word first in dreamy serif, later slammed in heavy grotesk | the change of voice *is* the reversal ("dream" to "reality") | first `T.render(word, 'jw_key')` with `J.underline`; later `T.Glyphs(word + '!', 'jw_caps_bold', px=120).slam(cv, t, x, y, t0=...)` with `K.spring` overshoot; SFX `impact_big` on the slam |
| 7 | **Ghost-ahead word build** (two-state karaoke) for VO-synced type | the eye pre-reads the line and the voice "confirms" each word; it works with faster-whisper stamps | per word: `opacity = 0.3 + 0.7 * K.ramp(t, ws, ws + 0.12, 'out_cubic')`, fill ASH to IVORY, `blur = K.lerp(6, 0, same ramp)`; the keyword ends in FLAME (`jw_key`). Lead the VO by about 0.1 s on reading-heavy lines and trail it by about 0.2 s on punchlines. Timings come from the hinglish-scriptwriter's token table mapped to Roman caption tokens. Keep real word spaces |
| 8 | **Lights-off reveal transition** | the outgoing world loses its light while an emissive object ignites in the dark; it feels like cinema, not an edit | outgoing: `K.post(cv, look, t, exposure=1 - 0.9 * u)` over 7 frames ('inout_sine'); incoming: UI or prop with `K.glow(..., K.C['FLAME'], (8, 28, 80))` opacity on the same ramp. Blender: keyframe light `energy` to 0 while an emission strength ramps up. SFX `downlifter` ending on the dark, `ui_tick` + `shimmer` on the ignite |
| 9 | **Split panel with colour-crossing type** (and a slow letterbox squeeze) | an "explainer" beat feels editorial and premium; the type crossing the edge links two worlds | panel = `ui.glass_card(...)` in SMOKE / PLUM glass (not white) sliding in with `K.Track`; the headline is rendered twice (FLAME and IVORY fills) and composited with complementary masks split at the panel edge `x_edge(t)`; bars = two NIGHT_0 rects with height `K.lerp(220, 260, K.ramp(t, t0, t1, 'inout_sine'))`. **Body text 28 px or larger**; no fake definitions-as-texture |
| 10 | **Literal visual pun on the VO's idiom at about 55-65 % of runtime** | humour at the retention sag; makes the line quotable and shareable | write the Hinglish line around a physical idiom, then stage it literally with Jawad's character (face-compositor expression swap: `suit_shocked`, `street_smirk`) or a Blender proxy figure (bpy armature-less pose, a few keyframes, 2 threads). The idiom must come from the hinglish-scriptwriter, not from the reference's "sliding in DMs" |
| 11 | **His own film-border template as a chapter marker / bookend** | the frame says "this is cinema" and marks method to CTA; it becomes a series signature | build once as a sprite: thin IVORY rules + sprocket ticks + edge print in `jw_mono` FLAME (e.g. "JAWAD 500T · 24 · @jawad_mp4", timecodes); draw in `post` at about 85 % opacity. **No Kodak or other stock trademarks.** Pair with `K.chroma` on the hero word only |
| 12 | **Hero 3D object + giant depth-echo type + punch-in cut** | one premium object anchors the method beat; defocused giant letters make it feel monumental; the punch-in cut on a keyword is cheaper than a camera move | new prop in `assets3d_jawad.py` (blender-3d-artist; e.g. an obsidian "edit key", a lens element or a film-reel puck in black gloss + emissive FLAME, CPU Cycles with low samples + denoise; Cycles glass **dispersion** for orange/red fringes) via `S3.get(name, 'night', mode='spin')`; echoes = `T.render(word, 'jw_key')` at z -400 and +1200 with `Cam(aperture=60)`; punch-in = hard cut to `scale x 2.2` of the same billboard on the keyword onset, with defocus landing (`blur` 12 to 0 over 4 frames) |
| 13 | **In-world light-band sweep** instead of a cut (≤ 0.35 s dark) | resets the eye while keeping the world; a soft "breath" between two lines | `K.light_leak(cv, t, colors=[K.C['FLAME'], K.C['RED']], sweep=u, angle=-60)` + a moving `K.radial` key light; or animate the seamless's light falloff in Blender (area-light location keyframes). Pair with a 0.3 s bed duck (see 15) |
| 14 | **Decode/scramble CTA in a bookend frame, then the house end card** | the decode makes the keyword the last thing the eye solves; the bookend links it to the method | `T.Glyphs(keyword, 'jw_caps_bold', px=96).scramble(cv, t, 540, 1000, t0=..., dur=0.8)` + `J.underline` draw-on, then `J.signature(cv, 540, 1560)` held at least 1.5 s settled; dust = `J.embers(n=80)`; last-frame luma and colour matched to frame 0 for a seamless loop. CTA text only if it is true (DM automation exists) |
| 15 | **Word-locked edit + keyword booms + pre-turn dropouts** (the sound and edit grid) | picture and sound obey the voice, so every cut feels motivated even without a beat | from faster-whisper word stamps: `t_cut = phrase_first_word.s - 0.06` for phrase-start cuts, `word.s + 0.08` for on-word punch-ins; `cues()`: `impact_soft` / `sub_drop` on each keyword onset (about one per 2-2.5 s), `whip` / `whoosh_fast` on transitions, `glitch_short` on interleaves, `riser` ending on the CTA; bed ducked by 15-20 dB for 0.3-0.5 s before each section turn. Mix target per brand: -14 LUFS, TP -2.0 dBTP or lower, speech 8 LU or more above the bed (the reference measures about 10.6 dB) |

**Sound recipe (procedural, toolkit `cues()` + `audio.py`):** about 1.5 designed events per second. Keyword booms
come every 2-2.5 s on stressed words, whooshes on every whip (about 1 per s), and glitch ticks on interleaves. The
bed is a beatless warm drone (synthesised with `audio.py` `osc` / `noise_band` + `reverb('hall')`, or licensed
through music-supervisor) with dropouts before the turns. Never rip the reference's score.

**Story skeleton to adapt (structure only, not copy):** call-out of a desire with a concrete stake, then a mirror
of the viewer's current reality, a one-line reversal, the rule, the benefit plus a funny enemy, the method, and a
true CTA. 21 s here; at Jawad's 30-40 s, double the method beat with a proof moment (his real work, his real
numbers only).

---------------------------------------------------------------------------------------------------------------
## 16. Devices to avoid (or fix when adapting)

1. **Full-white worlds and white flashes**: the paper world (2.67-4.33, mean luma about 230) and the pale gem world
   (luma about 160) break Jawad's rule that 70-85 % of every frame is near-black. The 1-frame bright negative at
   9.142 s (luma 24 to 212 to 45) breaks the "no full-frame white flashes" rule.
2. **Flicker interleave at about 15 Hz with large luminance swings** (1.068-1.401: luma 8 / 96 / 8 / 97 over 6
   frames). This is a photosensitivity risk (WCAG 2.3.1 allows at most 3 general flashes per second). Cap at 3
   alternations with ≤ 20 % luminance change.
3. **Low-contrast copy**: navy on slate ("Good Money" 1.5:1, "charge your" 1.3:1) and cyan on paper ("this..."
   1.8:1). Jawad's keyword contrast should be 4.5:1 or higher.
4. **Illegible micro-type as decoration**: the definition paragraph at about 16 px x-height, the blurred micro blocks
   at y about 1540-1590. Use 28 px or more, or leave it out.
5. **Tracking that deletes word spaces** ("WHICHTURNS", "VIEWERSINTO", "thenyouneed"): Roman Urdu needs real spaces.
6. **Copy in the like/comment column** ("Good Money" to x about 1015 at y 1205-1290) and **outside the left margin**
   ("Personal Brand" from x about 32).
7. **Unverifiable claims on screen** ("Generated over 100M+ views"): Jawad's numbers only, from Jawad.
8. **24p material in a 30p file** (every 5th frame duplicated): render natively at 30 fps.
9. **Super-black bars** (YMIN 0 in the letterbox and film border): keep blacks legal (brand YMIN 16-22).
10. **CTA unresolved at the last frame / no end card**: conflicts with the `@jawad_mp4` 1.5 s end card rule.
11. **Third-party marks**: the Kodak stock edge print and a social-network profile clone. Build generic, own-brand
    versions.

---------------------------------------------------------------------------------------------------------------
## 17. Do not copy

- The script and its lines: "If you're dreaming of charging $200 a reel...", "stop dreaming", "sliding in their DM",
  "high quality relatable content", the "ROADMAP" keyword.
- Its imagery: the backflip figure in the concrete room, the hands-and-cash plate, the "Unknown Editor" / "Apex
  Editor" profile mock-ups, the neon street slide, the faceted gem, the Kodak-style frame.
- Its exact lockup layouts, its fonts if licensed, and its score and SFX.
- Anything from the toolkit's fostering / Floret examples.

Steal the **mechanisms** in section 15 and rebuild them in flame and red on near-black with Jawad's own story,
character, props and Hinglish voice.

---------------------------------------------------------------------------------------------------------------
## 18. Evidence, method and confidence

All files are in `/home/user/100/workspace/brand_reels/refs/`:

| what | file |
|---|---|
| 3 fps frames (63 JPG, full-res 718x1280) | `ref3_frames/f_001.jpg` ... `f_063.jpg` (frame n is at t = (n-1)/3 s) |
| 4x4 contact sheets, 360 px tiles, timestamped | `ref3_analysis/sheets/sheet3fps_01..04.jpg` |
| per-frame (30 fps) transition strips | `ref3_analysis/cuts/strip_*.jpg` (12 windows), `beam_build.jpg`, `customers_build.jpg`, `pb_crop.jpg`, `cta_crop.jpg` |
| full-res key frames and type crops with 1080-scale rulers | `ref3_analysis/full/f_*.jpg`, `full/type_*.jpg` |
| safe-zone overlays | `ref3_analysis/sheets/safezones.jpg`, `safe/safe_*.jpg` |
| cuts | `ref3_analysis/cuts_0.2.txt`, `cuts_0.3.txt`, `cuts_0.4.txt`, `transitions_manual.txt`, `scene_all.txt` |
| per-frame luma / diff / vignette / letterbox / sharpness | `ref3_analysis/frame_stats.json`; `ymin.txt`, `ylow.txt` (signalstats); `flow.json` (not used, see 9) |
| palette | `ref3_analysis/palette_swatches.png`, 2 fps samples in `ref3_analysis/f2/` |
| audio | `ref3_analysis/audio/ref3_stereo.wav`, `ref3_16k.wav`, `spec_full.png`, `spec_side.png`, `wave.png`, `bands.json`, `M.txt`, `transcript_small.json` |

Analysis scripts (not deliverables) are in the session scratchpad. All Python that read the reference ran with
`python3 -I`, at `nice -n 10` with 2 threads or fewer. faster-whisper was fed a numpy array because the installed PyAV
rejects its `metadata_errors` argument.

**Confidence:**
- High: transcript and word timings, loudness, cuts and world boundaries, flash frames, palette, letterbox and black
  levels, VO-to-cut alignment.
- Medium: type sizes (eyeballed, ±10 %), boom and whoosh roles, bed description, voice F0.
- Low: the possible 117 BPM pulse at 3.6-5.2 s, camera moves (eyeballed; optical flow is biased by static areas),
  AI-vs-3D source guesses.
- Not knowable from the file: the exact fonts, the generators used, whether the VO is human or TTS, and whether the
  abrupt end is intentional (loop bait) or a trimmed export.
