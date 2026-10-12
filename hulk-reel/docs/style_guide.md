# Style guide (from the attached reference reel, 720×1280, 9.3 s)

## Rhythm
Median shot 0.43 s, 4.3 cuts / 10 s (cuts.json), but all four hard cuts sit in the first 1.7 s:
the background flips white↔blue every ~0.4 s, once per bounce of the dot. After that it never
hard-cuts again. Every change is carried by the one shape on screen (the dot grows into a circle
that wipes the frame, the stroke writes the logo). It holds on the finished lockup for about 1.5 s.
On our grid (128 bpm, 0.469 s/beat) one reference flip is one beat.

## Motion vocabulary
- Entrances: a single pill/dot drops in with squash on landing; text writes on one word per bounce;
  logo letters are drawn by a moving stroke, a letter every ~2 frames.
- Exits: the dot shrinks to a point and then grows into a full-frame circle (iris wipe); the end
  lockup leaves on a horizontal speed-line whip.
- Easing: landings are `SPRING.bouncy` (about 10% overshoot, settles in 8–10 frames). Wipes are
  `E.inOutCubic` growing to `E.outExpo`, and nothing moves linearly.
- Camera: locked off and flat, with no parallax. Scale comes from the shapes, not from the camera.
- Signature move: one small character (the dot) carries the whole story. It bounces, writes, swells
  into the wipe and becomes part of the logo.

## Composition
Centred, with lots of negative space: one small element on a huge flat field. The type is small and
tracked (it sits at about 25% of the frame width), and the logo lockup is centred at about 60% width.

## Colour + texture
Two large flat fields alternate (brand blue / white) with a single accent (orange in the logo). There
are no gradients, grain or shadows. Mapped to Hulk:
- deep forest `#111A16` (main field, the site's dark canvas)
- cream `#F4F2E9` (the alternate field, the site's paper)
- Hulk green `#9DEF69` (the one accent, sampled from the logo: the dot, the wipe, the logo)
- forest ink `#20392E` for type on cream or green

## Type in motion
Reference: small, bold, all-caps sans, written on word by word. Ours: Inter Tight (the site's
headline face) for display, set heavy (800–900) with tight tracking; Hanken Grotesk (the site's UI
face) for small caps labels and the CTA. Words arrive per glyph, each one rising under a mask.

## Do / don't
- Do: let one shape lead every transition. The green dot is the camera.
- Do: flip fields on the beat in the hook, then stop flipping once the story starts.
- Do: keep everything flat and graphic, with real logo paths and real work photos only.
- Don't: use a gradient background, a glow, or particle bursts.
- Don't: fade anything in. Things land, wipe, or get drawn.
- Don't: set more than one line of type moving at once. One idea per beat.
