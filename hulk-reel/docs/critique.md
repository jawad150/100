# Critique log: hulk-reel (9x16)

## Round 1
| hook | read | motion | variety | brand | sync | min |
|  6   |  8   |   8    |    9    |   9   |  8   |  6  |

Worst three (most damaging first):
1. [beat 0-1] Frame 0 is mostly empty cream: tiny dots popping and half a word under its mask. It
   doesn't stop a thumb. -> sceneHook: open with a camera at 1.9x on the hero dot pulling back to 1x
   (spring 90/16) so frame 0 is already big shapes in motion; keep the headline out of the zoom.
2. [beat 24-24.25] The dot falls from y=-80, so the first 6 frames after the flip to forest are
   empty and read as a dropout. -> sceneLogo: start the fall at y=330, so the dot is on screen from
   the first forest frame.
3. [beat 4-7] The words were all sized to fit STRATEGY, so "AI" was a small word in a big field.
   -> wordGeom: fit each word on its own (max 290 px); AI now lands huge and the dot scales with it.
   Also (sync) the CTA pop and URL tick were inaudible under the end chord: boosted to pop+click 0.5
   and blip+click 0.3. The riser now ends on the burst (12), with a swell on the squeeze.

Checks failed: none (longest gap without an event: beats 10-11.6, 0.75 s)
Verdict: ANOTHER ROUND

## Round 2
| hook | read | motion | variety | brand | sync | min |
|  8   |  8   |   7    |    9    |   9   |  9   |  7  |

Round 1's fixes hold: frame 0 is now big grey dots pulling back, and the dot is on screen from the
first forest frame at beat 24.

Worst three:
1. [beat 25-25.3] The flood and the H slam overlap, so one frame shows a green H inside a forest
   hole (muddled). -> iconFill timing: flood 25-25.22, then the H slams from 25.24.
2. [beat 12-14] "Marketing / with" sits in the top half for two beats while the bottom half of the
   green field is empty. -> muscleText: the block starts 150 px lower (centred) and springs up to
   make room as MUSCLE. lands on 14 (snappy).
3. [beat 16-19] The card name pills (30 px) and the "DIFFERENT WORLDS." label (32 px) are near the
   limit at phone size. -> pills 34 px / 66 px tall, label 36 px.

Checks failed: none
Verdict: ANOTHER ROUND

## Round 3
| hook | read | motion | variety | brand | sync | min |
|  8   |  8   |   8    |    9    |   9   |  9   |  8  |

Round 2's fixes hold: the "Marketing / with" block sits centred and makes room as MUSCLE. lands, the
H slams cleanly after the flood, and the pills read at phone size. Sync: 33/38 hits within 20 ms
(median 2.5 ms); the five outside are a whoosh that peaks on its hit, a riser and swell that end
on theirs, and the soft-attack boing, all by design. Mix: -14.0 LUFS, -1.2 dBTP.

Remaining (not blocking):
1. [beat 4-7] Each bounce word gets one beat (0.47 s); it reads, but only just on first view. A
   16-second cut could give each word 1.5 beats.
2. [beat 24-25] The H stroke draw is quick (0.6 beat); a hair slower would show off the pen move.
3. [beat 28-32] The end-card lockup (icon + wordmark) is small against the tagline; it could take
   about 15% more width if the CTA moves down 40 px.

Checks failed: none. Longest gap without an event: beats 10-11.6 (0.75 s). End card holds 1.9 s.
Verdict: READY
