# Ref 2: "Creativity is..." (Axteredits). Reverse-engineered for @jawad_mp4

Role: reels-studio `reference-analyst`. This is a spec of reusable **devices** for learning the craft. It does not
license copying. Jawad's reels keep his own story, copy, props and palette (fiery orange to red on deep black). They
use nothing from the "Organic Fostering" / "Floret" toolkit examples: no `neon`, `amber` or `airy` looks, no
fostering props.

Unless a line is marked *(inferred)* or *(eyeballed)*, every number below comes from a command run on the file.
The evidence lives in `workspace/brand_reels/refs/ref2_analysis/` (git-ignored) and is listed in section 15.

---------------------------------------------------------------------------------------------------------------
## 0. TL;DR

**What it is.** A 35 s vertical motion-typography essay. One male English **voiceover** asks a riddle, knocks down
two false answers, reveals the truth, calls back to the opening metaphor and closes on an aphorism. Under it runs a
beatless, sub-heavy cinematic score with a designed hit on every world change. The footage is AI-style imagery and
3D props, graded low-key with cream highlights. Type is staged in 3D depth, with defocus, flares and a dirty-glass
overlay on top.

**The 5 strongest devices (all can be adapted):**
1. **Two-voice type lockup.** Small, tight lowercase grotesk "carrier" words sit on the shoulder of a huge serif- or
   script-italic keyword that is 1.65-2.6x their height. This is Jawad's house style already: steal the *motion*,
   not the look.
2. **Outline-then-fill write-on.** The keyword appears as a glinting thin outline, then a solid fill wipes left to
   right with sparks on the wipe front (`book`, `reading it`, `clock`, `frustrating`, `mind`).
3. **Light is the transition.** Every new world is born from black by a light turning on: a lamp at 0.3 s, a window
   igniting at 2.1 s, an anamorphic streak at 27.0 s, the helmet lights-on at 30.0 s. Only 5 of 13 transitions are
   true cuts at scene threshold 0.3.
4. **Depth stack.** When a new line arrives, the old line is pushed back in z, so it shrinks, dims and defocuses.
   Ghost "echo" copies of a word float at several depths, and "HONESTY" has a floor reflection.
5. **The narrative turn is a grade flip plus a flash.** At "...nothing like that / In all honesty" the whole look
   jumps from warm amber to teal, punctuated by a 1-frame white flash (11.467 s) and a sub hit 0.11 s later.

**Pacing:** 14 visual worlds, median 2.88 s, mean 2.51 s, 3.7 transitions per 10 s, 2 transitions in the first
3 s (0.77, 1.95). There is **no measurable BPM**: low-band onset periodicity is <= 0.15 in every section. **Audio:**
-14.1 LUFS integrated, LRA 4.7 LU, true peak -0.6 dBTP. **Palette:** 82.6 % of pixels sit in two near-black
clusters (#0E0F0F, #21201C), and the highlights are cream (#E3DBBD), never white.

---------------------------------------------------------------------------------------------------------------
## 1. Source

| field | value |
|---|---|
| file | `workspace/brand_reels/refs/ref2.mp4` (local copy supplied by the lead; analysis only, never in a deliverable) |
| access | full video and audio, high confidence |
| container | H.264 yuv420p bt709, **718x1280**, 30/1 fps, 1050 frames, 35.130 s; AAC 44.1 kHz stereo |
| bitrate | video 656 kb/s (Instagram-grade). Fine grain and detail were destroyed by encoding (see 9) |
| scale | pixel numbers below are re-scaled to a 1080-wide canvas (x 1.504) |
| accessed | 2026-10-08 |

---------------------------------------------------------------------------------------------------------------
## 2. Numbers

| metric | value | how |
|---|---|---|
| scene cuts @0.3 | 5 (0.767, 11.467, 15.700, 17.967, 32.867) | ffmpeg `select=gt(scene,0.3)` |
| scene cuts @0.2 / @0.4 | 7 / 3 | same |
| **visual worlds (manual, checked on 10 fps strips + per-frame luma/diff)** | **14** | `transitions_manual.txt` |
| shot length (worlds) | mean 2.51 s, **median 2.88 s**, min 0.55 s ("or.."), max 5.90 s (inset card) | pacing script |
| transitions per 10 s | 3.7 (manual) / 1.4 (scene-detect only) | |
| transitions in first 3 s | 2 (0.77 bokeh blow-out, 1.95 whip + dip) + light-on at 0.3 s | |
| transitions that are true hard cuts | 5 of 13. The rest are dips to black, flashes, defocus-throughs, whips and light-ons | |
| BPM | **none**: low-band onset autocorrelation strength 0.10-0.15 in every section; full-mix "best lag" changes per section (62-146 BPM) | numpy AC |
| VO rate | 95 words / 31.94 s = **2.97 words/s** | faster-whisper word stamps |
| on-screen text events | ~60 word groups, about 1.7 per s, a new one every ~0.6 s *(eyeballed from 3 fps + 10 fps sheets)* | |
| loudness | **-14.1 LUFS** I, LRA 4.7 LU, **TP -0.6 dBFS**; mid -17.3 LUFS, side -29.1 LUFS | ffmpeg ebur128 |
| designed SFX events | 14 sub impacts (>= 9 dB rise in 150 ms) and 16 air risers (>= 8 dB over 0.5 s), about 0.85 per s | numpy STFT |
| onset density | full mix 2.08/s, low band 2.11/s, high band 1.62/s | spectral flux |
| flash frames | 1 full-white frame at 11.467 s (mean luma 247/255, diff 228). A bright cut at 15.70 s (luma 39 to 197) | per-frame stats |
| black floor | 1st-percentile luma median 9/255; 456/1050 frames >= 10 (milky, lifted blacks) | per-frame stats |
| vignette | corner luma about 32 % of centre luma (median) | per-frame stats |

---------------------------------------------------------------------------------------------------------------
## 3. Transcript: voiceover, not lyrics

**Classification: spoken voiceover.** English, faster-whisper `small` int8, language auto, p(en) = 0.965. The
evidence:
- It has conversational prosody, rhetorical questions and irregular pauses (no sung sustained vowels, no rhyme).
- The voice is centred mono: mid -17.3 LUFS against side -29.1 LUFS, and the side spectrogram has no speech
  harmonics.
- The voice is male: YIN median F0 117 Hz, IQR 100-128 Hz *(only 90 clean voiced frames under the music: low
  confidence)*.

The music underneath is **beatless ambient score** with designed SFX.

Verbatim, with segment times (word stamps are about +-0.2 s):

| t (s) | line |
|---|---|
| 0.00-1.92 | What do you think creativity is? |
| 2.18-4.84 | Is it like a book that you can understand without reading it? |
| 5.00-8.46 | Or is it like a clock that tells you everything before time? |
| 8.80-10.82 | I mean, it's nothing like that. |
| 11.24-15.52 | In all honesty, it's just putting in the work to attain a certain level of knowledge. |
| *15.52-17.68* | *(2.16 s VO pause: sky freefall shot)* |
| 17.68-20.72 | You cannot understand a book without reading it, can you? |
| 21.04-22.32 | When you try to learn a craft, |
| 22.60-26.60 | you put an enormous amount of time to get some spectacular results. |
| 27.08-29.48 | It may be frustrating at start, but keep in mind, |
| 29.48-31.94 | great things takes time. *(sic; whisper confidence lower here: logprob -0.48)* |

Key word stamps: creativity 0.78, book 2.72, reading 4.22, Or 5.00, clock 6.18, time 8.06, nothing 9.66,
honesty 11.56, work 13.10, knowledge 15.18, You 17.68 (visual cut at 17.97 = **0.29 s audio pre-lap**), book
19.28, craft 22.00, spectacular 25.32, results 25.80, frustrating 27.60, mind 29.14, things 30.24, time 31.50.
Pauses longer than 0.25 s fall after 1.92, 8.46, 10.82, 15.52 (2.16 s), 20.72, 22.32 and 26.60.

---------------------------------------------------------------------------------------------------------------
## 4. Timed beat table

Type sizes are text-block heights (ascender to descender) on a 1080 x 1920 canvas. Colours are the measured mean
of the text pixels.

| t0-t1 | world / shot | VO | type (size, style, colour) | device | transition out | audio event (measured) |
|---|---|---|---|---|---|---|
| 0.00-0.77 | S1 dark room, silhouetted man, practical lamp | "What do you think" | "what" bold lowercase grotesk, 105 px block, #A89D83, centred at 50 % H; "do", "you think" pop word by word (0.3-0.5) | text on frame 0; lamp/window light switches on at ~0.3 s (luma 36 to 62) | **bokeh blow-out** 0.77 (diff 38.6, luma 88) | sub boom from 0.17; air riser peaks 0.64 (+35 dB) |
| 0.77-1.95 | S2 "Creativity" over a blurred red-pink foreground form + silhouette | "creativity is?" | **"Creativity"** condensed Didone italic, 248 px block, 702 px wide (65 % W) at 35 % H, #B8A792; "is" grotesk pops at ~1.4 | rack-focus resolve from the blown highlight in 6-7 frames; old line pushed back in z and defocused | whip left + dip to black 1.9-2.07 (luma 14) | low onsets 1.18, 1.46, 1.61, 1.86 |
| 2.07-5.00 | S3 window glowing fire-orange, silhouetted books flying, god rays | "Is it like a book ... without reading it?" | carriers 71-77 px #D6C8AB; script keywords "book" 138 px, "reading it" 182 px (58 % W), #C5B797 to #C9B694 | **outline then fill write-on** with sparkle glints; window "ignites" from frame left | defocus + dip to black about 4.9 | sub hit 3.47; air riser 3.81 |
| 5.00-5.55 | S4 black void | "Or" (5.00) | "or.." bold grotesk with ghost copies at several depths | **echo field** | slide/hard cut 5.53 (black edge bar visible) | VO lands exactly on the cut |
| 5.55-8.67 | S5 same window world, reframed closer, pages fluttering | "is it like a clock ... before time?" | script "clock", "time"; grotesk "that tells you everything" tracks in with motion blur | rays sweep | fade to black 8.5-8.7 (luma 8.5) | air riser 7.10; sub 7.86 |
| 8.67-11.47 | S6 abstract warm bokeh (defocused embers) | "I mean, it's nothing like that." | grotesk italic "I mean"; script "nothing" / "that" with a burning ember edge, dissolving to sparks | defocused world = doubt | dip to dark teal 11.0-11.4, then **1-frame white flash at 11.467** | sub hits 8.83 (world start), 9.31; air riser 9.11 |
| 11.47-12.45 | S7 teal void | "In all honesty, it's just" | **"HONESTY"** quirky display serif caps, 167 px block (55 % W), teal-white #AFD0CC; large echo copies at 10-25 % + floor reflection + horizontal light streak | **grade flips warm to teal** | 3D tilt-away of the text plane + light-leak wipe 12.3-12.6 | sub hit 11.58 + air riser 11.62 (+15 dB) punctuate the flash |
| 12.45-15.70 | S8 dim green-teal interior, light leak arcing in from top right | "putting in the work ... level of knowledge" | thin monoline script "the work", "knowledge" with a slash stroke; light grotesk "to attain a / certain level of" | light leak + lens flare drift | leak bloom + defocus, then **hard cut 15.70** (diff 158) | loudest-region sub hit 13.66 (-18.6 dB) at leak peak; air riser 13.95 |
| 15.70-17.97 | S9 bright sky, figure in freefall, red petals, sun flare, rainbow lens halo | **no VO (2.16 s breath)** | none | radial/zoom blur settles in ~0.4 s; slow upward drift | hard cut to dark 17.97 (diff 70) | bass drops out (sub -46.6 dB at 16.5); soft low hit 16.91; tonal pad ~300-400 Hz visible |
| 17.97-20.95 | S10 dark; an old leather book (3D) swings in; HUD crosshair lines; micro-paragraph | "You cannot understand a book ... can you?" (**VO starts 0.29 s before the cut**) | grotesk 63 px; Didone italic "book" 117 px; micro-paragraph 74 px block (3 lines, ~20 px x-height) at 83 % H with RGB split | **3D prop occludes the type**; HUD registration marks | horizontal whip 20.1-20.4, fade to black 20.6-21.0 | air riser 18.15 (cut); sub hit 20.18 (whip) |
| 20.95-26.85 | S11 **inset rounded card** (film gate) on black; desaturated scissors cutting paper | "When you try to learn a craft ... spectacular results." | grotesk inside the card; "SPECTACULAR" serif caps + "results" | card fades in from black; scissors flare; VHS tracking glitch + RGB split (about 23.3) | card dissolves, leaving the scissors on black (26.5-26.9) | air riser 21.53 (+21 dB) on scissors flare; sub hits 22.41, 25.62 (paper cut), **26.78 (-17.6 dB, loudest hit)** as the card leaves |
| 26.85-29.90 | S12 dark teal; **anamorphic flare streak** ignites left of centre | "It may be frustrating at start, but keep in mind," | grotesk "it may be" 72 px; script "frustrating" 119 px (52 % W), copper outline to warm-white fill; "mind..." | the streak is the baseline the words sit on | streak slides off left, fade to black 29.5-29.9 | air riser 27.39 (+16 dB) on ignition |
| 29.90-32.87 | S13 helmet figure (gold visor), olive/teal haze | "great things takes time." | serif italic "Great" and "time", grotesk "things" and "takes", RGB-split | visor glint in darkness, then **lights flood in 30.0-30.3**; **liquid-glass melt / disintegration** 31.3-32.6 | defocus + cut 32.87 (diff 52) | sub hit 29.85 (reveal); air riser 31.52 (+20 dB) into the melt |
| 32.87-35.13 | S14 end card on near-black | none | "a creative by" grotesk 32 px block + "Axteredits" serif 102 px block + a small orange leaf | focus-pull resolve, faint flare | end | everything above 5 kHz falls to -117 dB at 33.0 (low-passed tail); sub drop-out 33.12 |

---------------------------------------------------------------------------------------------------------------
## 5. Hook (0.0-2.0 s), frame by frame (10 fps strip `sheets/transitions_1.jpg`, rows 1-3)

- **Frame 0 already has a word** ("what", centre-frame, cream). No black lead-in, no logo.
- 0.17 s: sub boom. 0.3 s: the practical lamp and window light switch on (frame luma 36 to 62, warm flare), and
  "you think." pops in word by word.
- 0.6-0.8 s: a 0.5 s air riser peaks at 0.64. At 0.77 the whole frame **blows out into bokeh** (luma 88) as
  "Creativity" arrives defocused from above.
- 0.8-1.0 s: the keyword **racks into focus**. The previous line is pushed back and down in depth, behind a
  blurred red-pink foreground form.
- 1.4-1.5 s: "is" and "?" pop. 1.8-2.07 s: a whip left and a dip to black. 2.1 s: the next world ignites from the
  left.
- **Count in the first 2 s:** 5 text events, 2 transitions, 1 light-on, 1 sub hit, 1 riser.
- **Hook type:** an open-loop question ("What do you think creativity is?") that the viewer answers in their head.
  The answer is withheld for 11 s.

---------------------------------------------------------------------------------------------------------------
## 6. Story structure

**Riddle, two false answers, negation, truth reveal, breath, callback, craft and time, empathy, aphorism,
signature.**

| beat | t | function |
|---|---|---|
| Riddle | 0-1.9 | question hook, direct "you" |
| False answer 1 | 2.1-4.9 | absurd metaphor (a book understood without reading) |
| Pivot "Or..." | 5.0-5.5 | 0.55 s single-word shot: the quickest beat, which resets attention |
| False answer 2 | 5.6-8.6 | second absurd metaphor (a clock that tells the future) |
| Negation | 8.8-10.8 | "it's nothing like that": a defocused, doubtful world |
| **Truth reveal** | 11.2-15.5 | flash + grade flip + uppercase serif: the visual climax of the first half |
| Breath | 15.5-17.7 | 2.16 s without words on the only bright, open image |
| **Callback** | 17.7-20.7 | the book metaphor returns, now as proof ("...can you?") |
| Craft and time | 21-26.6 | process imagery (scissors cutting paper) inside a framed "memory" card |
| Empathy | 27-29.5 | "it may be frustrating at start": acknowledges the viewer's pain |
| Aphorism | 29.5-31.9 | "great things take time" on a hero figure that literally erodes |
| Signature | 32.9-35.1 | maker's card, no verbal CTA |

The callback is what makes the essay feel "complete": the opening absurdity is reused as the logical proof.

---------------------------------------------------------------------------------------------------------------
## 7. Typography system

| role | face (identified by eye) | measured size @1080 | case / tracking | colour |
|---|---|---|---|---|
| carrier | neo-grotesk bold (Helvetica / Neue-Haas-like) | 63-105 px block (cap height about 45-75 px) | lowercase; **extreme negative tracking**, word spaces almost removed ("isitlikea", "itmaybe") | cream #D6C8AB-#D9C7A7, top-lit gradient, soft glow |
| keyword A | formal copperplate-style connected **script italic** | 119-182 px block, 52-58 % of frame width | lowercase | cream-gold fill, copper/gold glittering outline |
| keyword B | condensed high-contrast **Didone italic** | 117-248 px block, up to 65 % W | sentence case | warm cream #B8A792-#C0B4A2 |
| keyword C | quirky display serif caps | 167 px block (55 % W) | UPPERCASE | tinted to scene light (teal-white #AFD0CC) |
| micro | small grotesk paragraph | 74 px block for 3 lines | sentence case | olive-cream with RGB split: decoration, not information |
| signature | grotesk "a creative by" + serif wordmark | 32 px + 102 px | | muted cream |

- **Keyword to carrier ratio:** 1.65-2.6x block height (138/77, 182/71, 117/63, 119/72, 248/105).
- **Lockup:** two lines with negative leading (about 0.7), left-weighted. The carrier sits top-left on the
  keyword's shoulder, and lockups are offset left or right, never perfectly centred.
- **Placement:** every lockup centre falls between 35 % and 62 % of the frame height, inside the safe box
  (`sheets/safezones.jpg`). Only the decorative micro-paragraph drops to 83 % H, just above the 1620 px UI band.
- **In:**
  - Carriers pop or track in per word (2-3 frames, motion blur, slight scale-down).
  - Script keywords **draw on**: the outline is visible first, then a fill wipes left to right over 0.3-0.5 s with
    sparkle glints on the edge.
  - Didone keywords arrive **through a blown-out defocus**.
  - In-sync: keywords land within about +-2 frames of the spoken word (book 2.72 to 2.8, clock 6.18 to 6.0-6.3,
    honesty 11.56 to 11.47 flash).
- **Out:** the line is pushed back in z (dims, shrinks, defocuses) under the next line, dissolves into sparks
  ("nothing"), tilts away in 3D ("HONESTY"), or is swallowed by a dip to black.
- **Colour:** type takes the colour of the scene's light and is never pure white (top 2 % highlight #E3DBBD).
- **Effects:** soft top-lit gradient, specular glints, a mirror floor reflection (HONESTY), ghost echoes (or..,
  HONESTY), RGB split (micro-paragraph, the final line), DOF blur on far copies, and motion blur on every move.

---------------------------------------------------------------------------------------------------------------
## 8. Transitions catalogue (13)

| t | type |
|---|---|
| 0.77 | bokeh/exposure blow-out into a rack-focus reveal |
| 1.95 | whip left + dip to black + light-on reveal |
| 5.00 | defocus + dip to black, then a hard cut on the VO word "Or" |
| 5.55 | horizontal slide/hard cut back into the window world |
| 8.67 | fade to black, then a bokeh world fades up |
| 11.47 | dip to teal + **1-frame white flash** (grade flip) |
| 12.45 | 3D tilt-away of the text plane + light-leak wipe |
| 15.70 | leak bloom + defocus, then a **hard cut to bright** with a radial/zoom blur settle |
| 17.97 | hard cut bright to dark (J-cut: VO already running) |
| 20.95 | whip blur (20.1-20.4) + fade to black + inset card fades in |
| 26.85 | card dissolve leaves one object on black, then the flare streak ignites |
| 29.90 | streak slides off + fade to black, then the visor glint and a lights-on reveal |
| 32.87 | disintegration + defocus, then a cut to the end card |

Pattern: **dark, light-born, dark**. Seven transitions pass through near-black (luma < 15). They read as
"cinematic breaths", not cuts.

---------------------------------------------------------------------------------------------------------------
## 9. Camera, 3D and imagery

- **Camera:** almost locked-off. Optical flow gives about 0 px/s pan on every shot except the sky (about +15 /
  -36 px/s upward drift) and slow scale drifts of -4 % to +2 % per s *(flow is biased to 0 by the static overlay:
  low confidence)*. **The motion lives in the type, light and particles, not in the camera.**
- **Depth:** type is staged on 3D planes with DOF: far echoes blur, and older lines recede in z. Foreground
  elements (the red-pink form at 1 s, the book at 18-20 s) occlude the type.
- **3D / AI elements** *(inferred: source tools are not visible)*: silhouetted flying books and a window world
  (2-8.6 s), a sky freefall with petals (AI video), a leather book prop that swings in (3D or AI still with a 2.5D
  move), scissors cutting paper (AI video), and a helmet figure (AI still/video). Individually they look like
  generated stock. The edit makes them premium through grade, texture, type and sound.

---------------------------------------------------------------------------------------------------------------
## 10. Colour grade (k-means, k = 6 overall, k = 5 per section, 2 fps samples)

| section | clusters (hex share) | top-2 % highlight |
|---|---|---|
| **ALL** | #0E0F0F 60.8 %, #21201C 21.8 %, #473D34 6.1 %, #A5A08C 4.3 %, #747061 3.6 %, #DACFB2 3.4 % | #E3DBBD |
| A hook | #141312 60.2, #34231F 22.4, #653F37 8.5, #9A7663 4.6, #C5BDA6 4.4 | #CECFB8 |
| B fire window | #161413 76.9, #342119 15.8, #6E3C29 3.7, #B48860 1.8, #E9E0BC 1.8 | #E7DAB4 |
| C bokeh | #0B0A08 48.4, #201C17 31.0, #3A2D26 16.0, #6F4B3D 3.9, #C3A99A 0.7 | #9B7565 |
| D teal truth | #0E1515 72.0, #24312B 15.2, #5D5D4D 5.3, #A1967F 4.0, #E1E2D7 3.6 | #EDEFE9 |
| E sky | #C3B69B 30.2, #949E8E 23.3, #E2D3AF 21.9, #658178 13.8, #2F5858 10.7 | #F6F1C9 |
| F book HUD | #0E0E10 84.1, #241C19 9.6, #5A3F32 3.1, #8E7E65 1.9, #BEBD99 1.3 | #B4B08C |
| G card | #161614 41.4, #080909 41.4, #292823 13.2, #5B5045 2.9, #A18D80 1.1 | #8D7A6D |
| H flare | #090B0B 52.3, #121819 33.2, #283130 9.9, #61645C 2.7, #B1B0A1 1.9 | #AFAE9F |
| I helmet | #0C0E0D 43.6, #232722 25.2, #ACA595 11.2, #827C71 10.2, #525245 9.8 | #C4BCAB |
| J end card | #0F1112 43.1, #0A0A0B 38.6, #17191A 14.4, #37382D 2.6, #6D685D 1.3 | #5F5B51 |

Roles: #0E0F0F / #21201C are the **background void**, #473D34 / #6E3C29 are **warm practical-light falloff**,
#A5A08C / #DACFB2 are **text and highlight cream**, and the teal-blacks (#0E1515, #121819) are the "truth" world.
- **Grade:** low-key (median frame luma 20-40/255 except the sky at about 165), lifted milky blacks (black floor
  about 9/255), desaturated mid-tones, cream-clipped highlights, heavy vignette (corners about 32 % of centre).
- **Temperature arc:** warm amber/rust (myth, 0-11 s), teal (truth, 11.5-15.6), bright open sky (release),
  warm-dark (callback), neutral grey card (process), teal (empathy), olive/teal with an orange visor accent
  (aphorism). **Colour temperature carries the narrative turn.**

---------------------------------------------------------------------------------------------------------------
## 11. Texture and finish

- **Static "dirty glass" overlay.** A temporal median of 278 dark frames, high-passed, shows fixed smudges, dust
  and a scratched top edge on every frame (std 1.76 levels, `static_overlay_hp.png`). This one layer glues mixed
  AI, 3D and type sources into one "shot on a lens" world.
- **Grain:** only 0.60 levels residual std in dark areas after Instagram compression. Fine grain does **not**
  survive the IG encode, while large-scale texture (smudges, dust, halation) does.
- **Bloom / halation** around every practical light; **anamorphic streaks** (HONESTY at 11.5-12 s, the 27-29.9 s
  bar).
- **Light leaks** (12.5-15.6 s, top-right arcs), a **rainbow lens halo** (sky, 16.6-17.0 s).
- **Chromatic aberration / RGB split** on the micro-paragraph, the final line and the VHS-glitch card (about 23.3).
- **DOF everywhere**, plus motion blur on every type move and whip.

---------------------------------------------------------------------------------------------------------------
## 12. Audio layers (measured from `audio/spec_full.png`, `audio/spec_side.png` and the band envelopes)

| layer | evidence | notes |
|---|---|---|
| VO (male, English) | speech harmonics 250 Hz-4 kHz in mid only; side has none | centred, dry-ish; about 10 dB above the bed in the voice band (voice band -44 dB with VO vs -54 dB in the 15.5-17.5 s pause) |
| score bed | wide stereo sub/low (20-120 Hz strong in mid **and** side), pad tone about 300-400 Hz at 15.5-18 s | **beatless** (AC strength <= 0.15), dark-ambient |
| sub impacts | 0.17, 3.47, 7.86, 8.83, 9.31, 11.58, 13.66, 16.91, 20.18, 22.41, 25.62, **26.78**, 29.85 | each lands within about 0.1-0.2 s of a world change or a light event |
| air risers / whooshes | 0.64 (+35 dB), 3.81, 7.10, 9.11, 11.62, 13.95, 18.15, 19.85, 20.73, 21.53 (+21), 23.0, 23.8, 25.08, 27.39 (+16), 31.52 (+20), 34.91 | lead into flashes, flares and reveals |
| bass drop-outs | 2.27, 3.24, 9.0, 9.54, 14.08, **16.49 (sky breath)**, 22.26, 23.02, 24.28, 26.3, 33.12 | negative space before a hit |
| ending | HF band falls from -60 to -117 dB at 33.0 | low-passed tail under the end card |

Loudness: -14.1 LUFS I, LRA 4.7 LU, TP -0.6 dBFS, which is a little hot. Use -14 LUFS / <= -1.0 dBTP for Jawad.

---------------------------------------------------------------------------------------------------------------
## 13. Pacing against the audio

- **One sentence per world.** 10 VO sentences map onto 14 worlds; the extra ones are "or..", the breath, the
  aphorism split and the end card.
- **Transitions sit in the VO gaps.** A transition follows the end of a phrase by 0.03-0.65 s (median about
  0.22 s): 1.92 to 1.95, 4.84 to 5.00, 8.46 to 8.67, 10.82 to 11.47, 15.52 to 15.70, 20.72 to 20.95, 26.60 to
  26.85. The two deliberate exceptions are "Or" landing **on** the cut (5.00) and the **J-cut** at 17.68 to 17.97.
- **Shape:** quick front (0.77, 1.18 and 0.55 s worlds), steady middle (about 3 s), one long contemplative card
  (5.9 s), then a 3 s aphorism and a 2.3 s card. The edit accelerates and then decelerates.
- **Sound designed, not scored to a beat.** Hits mark meaning (new world, truth, card exit), not a grid.

---------------------------------------------------------------------------------------------------------------
## 14. Ending / CTA

There is no verbal or on-screen CTA. The aphorism lands on the hero, the hero disintegrates ("time"), and a
2.26 s signature card ("a creative by" + wordmark + leaf) resolves from defocus while the highs are low-passed.
It is a strong *brand* close but leaves reach on the table. **For Jawad:** keep the signature card (house
underline + @jawad_mp4) and add one soft Roman-Urdu CTA line *before* it (e.g. a save or comment prompt in his
voice). Test whether a follow prompt helps the 1M target.

---------------------------------------------------------------------------------------------------------------
## 15. Steal like an artist: 15 techniques adapted for Jawad's ember brand

Brand tokens to add in the project's `project.json` `palette` (core reads it via `PALETTE_HEX.update`):
`EMBER #FF5A1F`, `FLAME #FF8A2A`, `BLOOD #D4161C`, `CRIMSON_DEEP #5A0A0C`, `SOOT #0B0807`, `ASH #2A2220`,
`CREAM #F4E7CF` *(proposal)*.

Define **new** finishing looks (e.g. `K.LOOKS['ember']`, `K.LOOKS['ash']`). Never use the shipped `neon`, `amber`
or `airy`.

Fonts (all OFL, downloadable from the google/fonts GitHub repo into the project fonts dir):
- serif italic: Playfair Display Italic / Instrument Serif Italic
- script: Pinyon Script or Great Vibes
- carrier: Inter Tight Bold

*(Font picks are a proposal: the reference's exact faces are unidentified.)*

| # | technique | why it works | build it (Reels Studio toolkit / Blender) |
|---|---|---|---|
| 1 | **Two-voice lockup**: cream grotesk carrier + **ember-to-blood serif-italic keyword** at 2-2.6x, negative leading, offset left or right | the eye reads the keyword first and the VO supplies the rest. It is Jawad's house style, now animated | carrier `T.render('kya sach mein', T.style('flat', font='InterTight-Bold', px=76, tracking=-0.03, fill='CREAM'))`; keyword `T.render('editing', T.style('gold', font='PlayfairDisplay-Italic', px=200, fill=((0,'#FFE2B8'),(0.5,'#FF7A1F'),(1,'#D4161C')), rim=0.5, rim_color=('EMBER',1.4)))`. Check widths with `T.measure` <= 940 px. **Keep normal word spaces**: Roman Urdu needs them |
| 2 | **Outline-then-fill write-on with a spark front** | the keyword "arrives" exactly on the spoken word, and the sparks give a hit point for SFX | outline sprite: `T.style(..., face=False, stroke=0.02, stroke_color=('EMBER',1.6), glow=0.4)`; fill: `T.Glyphs(word, fill_style).wipe(cv, t, x, y, t0=tw, dur=0.45, angle=0, soft=0.08, edge=1.0)`; sparks: `K.Particles` or `K.disc` sprites in 'add' mode at the wipe front; glint: `ts.draw(..., sweep=K.ramp(t, tw, tw+0.5, 'inout_sine'))`; SFX `shimmer` (align='start') + `sparkle` |
| 3 | **Blown-bokeh rack-focus reveal** for the hook keyword | a 0.25 s overexposed blur gives the brain a "flash of light" and then rewards it with sharp type | `ts.draw_plane(cv, cam, P, blur=K.lerp(70, 0, K.ramp(t, t0, t0+0.25, 'out_cubic')))` + `K.post(..., exposure=1.5*(1-u))`, or move the word's z through `Cam(aperture=60, focus_dist=...)`; SFX `reverse_swell` (duration 0.6) ending on the resolve + `impact_soft` |
| 4 | **Depth stack**: the old line recedes in z (dims, defocuses) as the new one lands | continuity: the viewer sees the thought build instead of being replaced | `K.Scene(cam)` with each line as `sc.custom(...)` calling `ts.draw_plane(cv, cam, (x, y, z(t)))`; drive z with `K.Track` (+0 to +600) and opacity 1 to 0.35. `Cam(aperture=34)` blurs it for free |
| 5 | **Echo field + floor reflection** on one power word | makes a single word feel monumental and 3D without a 3D render | 3-4 copies of the same TextSprite at z +500/+900/+1400, scale 1.6-2.4, opacity 0.08-0.2; reflection = a **copy** flipped with `np.flipud`, gradient-masked, opacity 0.25, under the baseline; plus `K.anamorphic(cv, 0.9, 0.3, K.hexlin('#FF6A2A'))` |
| 6 | **Light is the transition**: each world is born from black by a lamp, window or flare igniting | hides cuts, reads as cinema, and gives a reliable "new beat" every 2-3 s | `K.god_rays(cv, (x, y), strength=K.ramp(t, t0, t0+0.3, 'in_cubic'))`, `K.light_leak(cv, t, colors=[C['EMBER'], C['FLAME']], sweep=u)`. In Blender (bpy, CPU): keyframe Area/Spot `energy` 0 to peak over 6-8 frames, EEVEE or low-sample Cycles. SFX `riser` ending on the light-on + `impact_soft` |
| 7 | **Ember anamorphic bar** that the type sits on | a strong horizontal baseline reads as "cinematic lens" and anchors small type | `K.streak(1400, 26, color=K.hexlin('#FF5A1F')*2.5, core=K.hexlin('#FFE0B0')*4)` drawn `mode='add'` at y about 0.5 H, travelling in x over about 3 s; `K.anamorphic` on the hot core; SFX `whoosh_slow` |
| 8 | **Narrative turn = grade flip + safe flash.** "Myth" in desaturated **ash** (near-monochrome), "truth" erupts in **ember orange-red** | the turn becomes visible *and* the brand colour is earned at the climax | two custom looks cross-faded at the turn word; `K.post(cv, 'ember', t, flash=0.6*K.impulse(t, t0, decay=16), flash_color=K.hexlin('#FF9A55'))`: a 2-3 frame warm bloom, **not** a 1-frame pure white; SFX `flash_hit` + `impact_big` (hit 0.1 s after the flash, as measured) |
| 9 | **One finishing stack for mixed sources**: static dirty-glass smudge overlay + lifted soot blacks + heavy vignette + halation | glues Blender renders, character stills and UI into one lens world; large texture survives IG compression where fine grain does not | define `K.LOOKS['ember'] = dict(bloom=0.5, bloom_threshold=0.5, bloom_radii=(8,26,70,170), bloom_tint=(1.0,0.55,0.3), halation=0.16, vignette=0.5, chroma=1.2, grain=0.022, black_tint=(0.0025,0.0009,0.0004))`; build the smudge plate once (procedural `K.gblur` of random strokes/blobs, or a Blender dirty-glass render) and screen it at about 5 % in `post` |
| 10 | **3D prop swings through the type** (occlusion + HUD registration marks) | proves the type lives in a real space. The book becomes **his** object: a film reel, a cinema camera, a clapperboard or a timeline clip block | Blender bpy builder in the `assets3d_*` pattern (CPU, spin/yaw sequence, red-orange rim light), loaded with `S3.get('<prop>', 'night', mode='spin')`, then `sc.billboard(...)` depth-sorted with the type planes. HUD: 1 px cream lines with '+' ticks drawn into a sprite, `K.chroma` on micro text only |
| 11 | **Inset "program monitor" card**: the scene shrinks into a rounded card (an editor's viewer) with tracking glitches | a frame-within-frame says "this is a memory / the edit", perfect for a video editor's brand | `ui.glass_card(880, 1240, r=56)` + `ui.media_face(card, frame)` with ember tint; glitch: per-band horizontal offsets + `K.whip_blur` on a band + `K.chroma`; SFX `glitch_short`, `card_slide` |
| 12 | **Wordless breath beat** (1.5-2.2 s) mid-reel on the brightest, most open image, with the bass dropped | resets attention before the callback; the reference uses the only bright shot here | e.g. Jawad's character falling through an orange-red sky, or his timeline exploding into 3D clips. Audio: duck or low-pass the bed, `downlifter` in, `sub_drop` / `impact_big` re-entry on the next VO word. Leave a VO gap in the TTS timeline |
| 13 | **Callback structure**: riddle, two absurd answers, "nahi yaar" negation, truth, callback, aphorism | makes 35 s feel like a complete essay, and the callback triggers rewatches | write **original** Hinglish copy in the same shape. *Illustrative only:* "Log sochte hain editing ek button hai? Ya AI sab khud kar dega? Sach bolun? ..." Then call back to "button" as proof at about 60 % |
| 14 | **J-cuts and on-word cuts**: next line starts 0.2-0.3 s before the picture cut; one cut lands exactly on a one-word line | the voice pulls the viewer into the next world, so no dead air at cuts | schedule VO segments in the timeline with a -0.25 s pre-lap; put a hard cut on a single stressed word ("Ya..."); keep other transitions 0.1-0.3 s after phrase ends |
| 15 | **Disintegration ending into a signature card** | "time" is shown, not told; the low-passed tail feels final | hero (Jawad character still) broken by an animated `cv2.remap` displacement driven by `K._noise_tile` flow inside a growing radial mask + `K.chroma`, then defocus. Card: "an edit by" carrier + "@jawad_mp4" serif italic in ember with his glowing orange underline stroke, focus-pull in; audio `riser` into the melt, `logo_sting`, low-pass the mix above 5 kHz over the last 2 s (`audio.py` `lp`) |

**Sound recipe (all procedural, toolkit `cues()`):** aim for about 0.8 designed events per second. Every world
change gets a sub hit within +-0.15 s (`impact_big`, `sub_drop`, `impact_soft`), every light event gets a riser or
whoosh that *ends* on it (`riser`, `reverse_swell`, `whoosh_slow`), and keyword write-ons get `shimmer` /
`sparkle`. The toolkit is SFX-only, so the beatless dark-ambient bed must be synthesised (`audio.py`
`osc`/`noise_band` + `reverb('air'|'hall')`) or properly licensed. Never rip the reference's score.

---------------------------------------------------------------------------------------------------------------
## 16. Devices to avoid (or fix when adapting)

1. **1-frame pure-white flash** (11.467 s, luma 247): jarring and a photosensitivity risk. Use a 2-3 frame warm
   bloom at <= 70 %.
2. **Word spaces deleted by extreme tracking** ("isitlikea", "itmaybe"): Hinglish and Roman Urdu spellings are
   already unfamiliar, so keep tracking at -0.02 to -0.04 em with real spaces.
3. **Low-contrast type on bright plates** ("Great" measured at about #6E756E over haze) and **micro-paragraphs**
   (about 20 px x-height after scaling, RGB-split): illegible on phones. Keyword contrast should be >= 4.5:1, with
   a scrim if needed.
4. **Long dips to near-black early** (2.0 s, 5.0 s, 8.7 s): risky for the swipe. In Jawad's first 3 s keep any dip
   at <= 4 frames.
5. **Grammar slip in copy** ("great things takes time"): proofread every Roman-Urdu / English caption.
6. **True peak -0.6 dBTP**: master at -14 LUFS, <= -1.0 dBTP.
7. **No CTA**: add one line in Jawad's voice before the signature.

---------------------------------------------------------------------------------------------------------------
## 17. Do not copy

The reference's script and lines (creativity, book, clock, scissors, "great things take time"), its imagery (fire
window with flying books, sky freefall, leather book, scissors, helmet figure), its exact lockup layouts, its fonts
if licensed, its score and SFX, and the Axteredits wordmark and leaf. Also copy nothing from the toolkit's
fostering/Floret examples. Steal the **mechanisms** in section 15 and rebuild them in ember orange-red on soot black
with Jawad's own story, character and props.

---------------------------------------------------------------------------------------------------------------
## 18. Evidence, method and confidence

All files are in `/home/user/100/workspace/brand_reels/refs/`:

| what | file |
|---|---|
| 3 fps frames (105 PNG, full-res 718x1280) | `ref2_frames/f_001.png` ... `f_105.png` (frame n is at t = (n-1)/3 s) |
| 4x4 contact sheets, 360 px tiles, timestamped | `ref2_analysis/sheets/sheet3fps_01..07.jpg` |
| 10 fps transition strips (15 windows) | `ref2_analysis/sheets/transitions_1.jpg`, `transitions_2.jpg`, `ref2_analysis/cuts/w_*.png` |
| full-res key frames, pairs, type crops | `ref2_analysis/full/t_*.png`, `pair_*.jpg`, `quad_a.jpg`, `type_crops.jpg` |
| safe-zone overlays | `ref2_analysis/sheets/safezones.jpg`, `full/safe_*.png` |
| cuts | `ref2_analysis/cuts_0.2.txt`, `cuts_0.3.txt`, `cuts_0.4.txt`, `transitions_manual.txt`, `scene_all.txt` |
| per-frame luma / diff / hist-corr / RGB | `ref2_analysis/frame_stats.json`, `yavg.txt` |
| palette swatches | `ref2_analysis/palette_swatches.png` |
| static overlay map | `ref2_analysis/static_overlay_hp.png` |
| audio | `ref2_analysis/audio/ref2_44k.wav`, `mid.wav`, `side.wav`, `spec_full.png`, `spec_side.png`, `whisper_small.json`, `audio_stats.json` |

Analysis scripts (not deliverables) are in the session scratchpad. All Python that read the reference ran with
`python3 -I`, at `nice -n 10` with <= 2 threads.

**Confidence:**
- High: transcript, timings, loudness, cuts, palette and type sizes.
- Medium: font identification, SFX layer roles and the AI-vs-3D source guess.
- Low: voice F0 (music bleed) and camera flow (the static overlay biases it to 0).
- Not knowable from the file: the exact fonts, the generators used, and whether the VO is human or TTS.
