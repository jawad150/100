# Shared-module change requests from log_kya_kahenge (C15)

Owner of the shared modules: motion-toolkit-engineer (jawad_tx, endcard) and the sound team (epic_music). This reel works around
every item locally (BRIEF.md §10.3, §8, §12); nothing here blocks the build. Filed 2026-10-08 by the creative-director.

## R1 · `jawad_tx` O6: restrict the disintegration to a layer (`mask=` / `spawn=`)

- **Why:** `_tx_embers` draws its 20 px burning edge across the whole frame wherever the erosion front is, and samples particle
  spawn points from the luminance of the whole A frame (`_ember_seed`). In C15 only the cardboard layer may burn: the edge line must
  not cross JD, the phone-lit people or empty air, and phones / eyes / the floodlight must not emit embers.
- **Ask:** two optional arguments on `TX['O6']`: `mask=fn(t) -> (H, W) 0..1` (the edge glow and the erosion apply only inside it;
  1/4-res is fine) and `spawn=fn(t0) -> canvas` (the frame whose luminance seeds the particles; default A). Default behaviour unchanged.
- **Local workaround now:** `o6_cards(t)` in `log_kya_kahenge.py`, a copy of `_tx_embers` with those two edits, using the shared
  helpers read-only; window, ease and samples taken from `X.TX['O6']`.

## R2 · `endcard.EndCard`: a `sub_px=` argument

- **Why:** the sub line is fixed at 56 px unless it exceeds 760 px. Since BRIEF r2 (viral gate fix 4) C15's sub is "jise 'log' ka darr
  rokta hai": 708.7 px at 56 px (x 186-894), under the 760 px trigger, so EndCard keeps 56 px and the line ends only 36 px from the x 930
  like/share column (y 1050-1700; the brief wants ≥ 40 px). At 50 px it is 632.8 px (x 224-856, 74 px clear). (r1's sub, "jo 'log' ki
  wajah se ruka hai", was 754 px at 56 px, 13 px from x 930.) Measured with `T.measure(..., 'jw_body')`, 2026-10-08.
- **Ask:** `EndCard(..., sub_px=56.0)` (default unchanged). A lower auto-shrink threshold would no longer catch this line.
- **Local workaround now:** after construction, `card.sub = T.render(SUB, 'jw_body', px=50.0); card._settled = None`.

## R3 · `workspace/brand_reels/sfx/epic_music.py`: render without the end fade

- **Why:** `render()` multiplies the last 1.2 s by a cos² fade to zero. The series loop rule (SLATE §5.1) says the last bar resolves into
  frame 0 and never fades to silence; any reel whose score must loop cannot use `render()` as is.
- **Ask:** `render(..., fade_out=True)` with `fade_out=False` skipping the fade (and the matching stem fade), plus an optional
  `styles=` hook so a reel can pass its own arrangement function.
- **Local workaround now:** `log_kya_kahenge_music.py` builds an `EM.Song` with the shared instruments and its own copy of the bus
  without the fade.
