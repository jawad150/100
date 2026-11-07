# Style guide (from the client's reference reel, WhatsApp 2026-11-04, 44.6 s, 1080×1080, 24 fps)

The reference is a Hulk Marketing local-SEO reel: AI night footage of a garage with a SaaS UI layer on top.
We take its motion and composition, and the brand keeps its own colours and type (hulkmarketing.co.uk, dark theme).
Our piece is pure motion graphics (no footage): the high street is drawn as a flat vector set in the same palette.

## Rhythm
- Only 4 hard cuts in 44.6 s (cuts.json); everything else changes inside the shot: a new title, card, pill or
  camera move every 2-3 s. We keep that: hard cuts only at the two structural moments (beat 6 cut to black,
  beat 7 rewind), everything else is camera moves (push-in, pull-back, pan, whip) inside one continuous set.
- Holds: a finished title + UI state holds ~1.0-1.5 s before the next change.

## Motion vocabulary
- **Title entrance (signature):** a 60×5 px lime rule grows from its centre (6 frames), the white caps rise
  ~24 px and land (snappy spring, a hair of overshoot), then the lime italic words type on letter by letter
  (~22 chars/s) with a lime caret that blinks twice and leaves.
- **Title exit:** the block lifts 16 px and fades in 6-8 frames (in_cubic). Never a hard pop.
- **UI pills:** dark glass pill + icon; spring in from 0.85 scale with 12 px rise; status flips (✗ red-muted to
  ✓ lime) with a 4-frame colour cross-fade and a small scale bump. Connector lines are dotted.
- **Cards:** dark glass rounded rect (r 28), 1.5 px border `#2A3328`, inner top highlight, soft shadow; rows tick
  on one by one, check circles pop in lime.
- **Counters:** forest-black pill, lime digits, each tick is a 1-frame roll (digit slides up 10 px).
- **Cursor:** white arrow with dark outline glides on an eased arc, press = scale 0.9 + lime ripple ring.
- **Typed URL line** on the end card, character by character with UI ticks.
- **Camera:** slow tracking on walks; log-space push-ins (constant-rate dolly); whip pans with both shots on screen.
- Easing character: `snappy` for UI, `gentle` for camera and big type, `bouncy` only for pops.

## Composition
- Centred titles at the top of the safe area (PDF safe area: text in y 270-1240, x 60-960). Small lime rule above.
- The set sits in the lower-middle of the frame; UI floats over it, never over a face or the door handle.
- End card stacked: shot card → headline → CTA card (label, lime pill, URL · phone) → real logo.

## Colour + texture
- Canvas `#0A0B0A` lifted to forest `#111A16` in the middle; faint rounded-tile grid (`#1A211C`, 1 px) like the
  reference's map blocks; lime horizontal rules (`#9DEF69`, 3 px, with a darker under-line) frame the stage.
- One accent: lime `#9DEF69` (glow `#78E930` only for light spill on the spinner/tick). Shop A deep green
  (`#2C5A43` paint), shop B plum (`#5A2346`), coat red `#C8453A` (character only, never UI).
- Warm interior light (`#F2C27A`) is light, not UI. Fine grain in post, gentle vignette.

## Type in motion
- Display: **Inter Tight 800**, caps, tracking +0.5 px, 66-84 px (the PDF's "Inter Tight ExtraBold captions").
- Accent: **Fraunces Italic 600** in lime, ~1.1× the caps size, for the one cue word per caption.
- UI: **Hanken Grotesk** 500-700, 26-40 px (the site's body face).
- Captions = the voiceover, word for word, one lime cue word each (PDF).

## Do / don't
- Do: keep every caption inside x 60-960, y 270-1240; check it on the phone sheet.
- Do: draw ↗ and ✓ as vector icons (none of the three faces has those glyphs).
- Do: keep shops blank (no names, no signs), the competitor plain and unnamed.
- Don't: glow on UI chrome, particle bursts, full-frame flashes on cuts, speed scores or any statistic.
- Don't: use the site's demo scores (47/62/55/71) or invent client results.
- Don't: show a browser or platform's own spinner; the spinner is Hulk's lime ring.
