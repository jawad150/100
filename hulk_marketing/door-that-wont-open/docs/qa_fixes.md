# QA round 1: findings and fixes

An independent QA pass of v1 ran five lenses: copy and brand, layout and readability, motion, audio, and story and style.
Each finding was adversarially verified. It confirmed 40 findings and refuted 4. This file lists what changed for each.
Finding ids are the reviewers' own.

## Blocker
| Finding | Fix |
|---|---|
| Cursor parks on the phone number for the whole end-card hold (copy-brand, layout, story-style) | The cursor slides in from off-frame at button height and clicks in the empty gap between "Audit" and ↗. It then eases up and away and fades by 35.54. The URL line and the logo are never crossed, and the final hold and the poster (36.2) are clean. |

## Picture
| Finding | Fix |
|---|---|
| motion-shopB-legs-vanish (her legs vanish entering shop B, then she turns see-through) | street.js: she walks a smooth path up over B's threshold. She is drawn after the pavement, clipped to the doorway plus everything below the ground line, once her feet are on the step. No alpha fade. |
| motion-warm-light-box (a warm rectangle travels with her and stays in doorway A) | The `source-atop` fillRect is removed, and her own paints are tinted toward the interior light instead. |
| motion-conversions-caption-hold, copy-brand-key-line-hold, layout-readability-stage-caption-exit-too-early | "conversions." types at 23.84-24.14 and has no exit. The rewind now starts at 25.2, and that cut removes the line, 0.76 s after the word ends. |
| layout-readability-cwv-line-contrast-and-duration, copy-brand-cwv-contrast, story-style-cwv-flash | The Core Web Vitals line sits on a dark glass chip. It fades in at 28.75-29.05 and is gone by 30.57, about 1.4 s at full opacity. |
| layout-readability-endcard-cta-stack-spacing | End card restacked: card 272-682, headline 703-875, CTA panel 918-1150 (sized to its content and centred), URL 26 px under the button, logo about 1176-1234 (inside y 1240), bottom rule 1270. |
| story-style-endcard-order | The logo lands on "audit." (34.94), after the click, as in the reference. |
| layout-readability-headline-over-shrinking-card | The headline is drawn before the card and clipped below its bottom edge, so the rising edge wipes it on. |
| layout-readability-safe-area-overshoots | Title fit width = 2 × (960 − 540) = 840 by default, so beat 7 refits. Beat 5 top moves 318 → 328. |
| layout-readability-rewind-pill-caption-collision, motion-rewind-ui-exit | The ⏪ pill fades out by 26.06. The playhead freezes at the rewind's end instead of jumping to the far end. |
| copy-brand-counter-0-04, story-style-counter-0-04 | The counter stops at 0:03, and the 12.0 tick (picture and SFX) is removed. |
| motion-count-captions-exit, motion-caret-ghosting (beat 3) | "ONE SECOND. / TWO. / Three." stack as one block with one 0.24 s exit at 12.55. |
| motion-caret-ghosting | The caret follows the fading-in letter continuously, so motion-blur sub-samples no longer split it in two. |
| layout-readability-across-caret-wedged | The caret shows only while typing when the lime word is mid-line (fixed in source before v1; confirmed in the new render). |
| copy-brand-straight-apostrophes | Curly ’ in WON’T and THAT’S (also fixed in source before v1). |
| motion-foot-skate | New leg rig: the stance boot moves linearly with her travel, with two-bone IK and plant points, so drift is about 1-2 px per step (was 40-45). Her step back is now a real step. |
| motion-camera-dead-stop | The follow pan eases to rest (outCubic 15.6-17.03) instead of clamping. |
| motion-stepped-blur | 40 sub-samples on the whip, 32 in the rewind's fastest stretch, 24 on the tick flight. |
| motion-cursor-pop, layout-readability-cursor-entry-in-ig-rail | The cursor starts off-frame at y 960 (above Instagram's right rail) and fades in. |
| story-style-bag-reads-padlock | The bag icon is redrawn as a tote with two thin strap loops and a fold band. |
| story-style-browser-chrome-invisible | Window dots are now muted grey (about 7:1 on the bar); the URL pill is lighter with a lime hairline; the skeleton address is lighter. |
| story-style-wait-acting-small | Weight shift 18 px at the hips plus a 0.04 lean; the feet stay planted. |
| copy-brand-lime-drift | The button's hover tint decays after the click, so the final hold shows brand lime. The vignette's gentle edge dimming is kept, as the style guide asks. |

## Audio
| Finding | Fix |
|---|---|
| audio-bell-loudest-tonal | The bell now has a clapper transient per strike and ±12-22 cent detune, and each strike damps the previous one. Decay is 0.25 with a fade by 16.9. It is cued at -17 dB (about -17.8 LUFS over 100 ms) and the door slide at -20 dB. |
| audio-ending-chop | The final chord starts at 35.2 (after "-dit") and decays in the film: sub bass gone by about 36.05, and the duck holds after the last word. An even fade in dB from 35.6 takes the 100 ms RMS from -15 to -55 dBFS by 36.45. |
| audio-open-masked | "open." is clip-gained +4.5 dB. The street bed and music duck on a look-ahead voice key. The 5.0 kick and bass are 4 dB softer, toggle_on drops to -14 dB with a 2 kHz high-pass, and the ui_hover is dropped. |
| audio-sigh-early | The sigh is cued at 11.97, so the exhale lands on her slump. A soft inhale sits at 11.62 and a breathy voiced layer is added. |
| audio-shrink-whoosh-early | whoosh_slow moves 30.75 → 31.0, onto the fastest frames of the shrink. |
| audio-duck-late-shallow | The duck is driven by a voice-activity key from vo_words.json (first word − 0.08 s to last word + 0.15 s). The VO sits ≥ 10.9 dB over the music on every line. |
| audio-vo-bandlimited-8k | Stopgap exciter on the VO, which takes the 8-12 kHz band from -57 to -37 dB relative to the voice's 1-4 kHz. A full-band re-generation would re-time the film. |
| audio-stems-pretrim | Stems are written at master level, and mix.py asserts that their sum is within 0.1 LU of the master. |
| (found while fixing) logo sting on "audit." | The sting's air above 300 Hz is ducked 12 dB under the voice. Whisper confidence on "audit." went back from 0.48 to 0.91. |
| Footsteps | Re-probed from the new rig. The stale hand-placed step-back heels are replaced by soft set-down taps at 3.95 and 17.35. |

The voice sits at about -14.2 LUFS over speech in the -14 LUFS master. The PDF suggests about -16; it is kept hotter on purpose so it stays clear on phone speakers.
