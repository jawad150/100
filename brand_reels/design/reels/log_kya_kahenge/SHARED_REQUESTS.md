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

## R4 · `vo_chain.edit_pauses`: the tail trim cuts an audible decay (no fade at the trim edges)

- **Why:** `edit_pauses` keeps `runs[-1][1] + pad` (40 ms after the voiced end found with `max(floor + 10 dB, peak - 45 dB)` on
  the raw take) and cuts there with no fade. On a breathy sentence-final word the decay is still sounding at that point; after
  the compressor and loudnorm the processed file ends at -33 to -37 dBFS sample peak in its last 5 ms (measured 2026-10-09:
  `proc/lkk_V7_t1_1.10.wav` -34.1, `lkk_V7_t2_1.10.wav` -33.0, `lkk_V5_t1_1.10.wav` -36.1, `lkk_V1B_t1_1.10.wav` -42.9 dBFS),
  i.e. a click and a clipped tail wherever the file edge is not covered by other audio. The raw V7 t1 take decays to -63 dB only
  ~70 ms after the cut.
- **Ask:** extend the kept tail until the 20 ms RMS falls below peak - 60 dB (or add `tail=` seconds), and apply a short
  raised-cosine fade (in 5 ms / out 20-30 ms) at the lead and tail trim edges. Same for the lead edge.
- **Local workaround now:** `log_kya_kahenge_vo.edge_fades()` puts a 5 ms fade-in and a 30 ms fade-out on every processed line
  before it is placed (filed by the hinglish-scriptwriter, VO run 2026-10-09).

## R5 · `core.god_rays` / `jawad_grade.finish`: a ray-source hold-out (`rays_holdout=`)

- **Why:** `K.god_rays` smears every pixel above the bright-pass knee (threshold 0.3, knee 0.2) away from the rays centre. In
  S3-01 (rays 0.22 from the floodlight bank) JD's white tee, hand, watch and trainers become ray sources: a faint light trail
  runs down-left of his legs (stand-in world, 2026-10-09: +1.1-1.2 code values mean, p99 +6, max +9 in the floor band beside
  him; with the plain cut-out +10 mean / p99 +40). A person is not a light source; it reads as a glow stuck to the cut-out.
- **Ask:** `G.finish(..., rays_holdout=None)` (and `K.god_rays(..., holdout=None)`): an optional (H, W) 0..1 mask multiplied
  into the bright-pass source only (the rays are still added everywhere). Default unchanged.
- **Local workaround now:** `log_kya_kahenge_faces.s3_rays(cv, t, centre, 0.22)` before the finish (same `K.god_rays` call,
  the look's threshold / length and tint, source multiplied by `1 - LF.jd_alpha(t)`), then the finish with `rays=0` for
  9.6-12.8 s. Measured after: +0.04-0.06 mean (noise), and the S3 halo ring after the finish drops from +6.6-7.6 to +0.4-0.7.
  Filed by the face-compositor, 2026-10-09.

## R5 · `workspace/brand_reels/sfx/epic_mix.py`: mono VO crash, hero hits flattened by the bus glue, seam not loop-safe

Filed 2026-10-09 by the sound-designer (SFX run 2, real Vlad VO). Measured on C15; numbers in `SOUND.md` §4-5.
- **(a) A mono VO crashes `mix_reel`.** `load()` keeps a mono wav as (N, 1); `mix_reel` then runs
  `np.concatenate([np.zeros((n, 2)), v])`, which raises a ValueError, even with `vo_offset=0`. The VO stems from `vo_chain`
  (`lkk_vo_A.wav`, `lkk_vo_B.wav`, `vo_stem.wav`) are mono. So `log_kya_kahenge_music.py mix` fails as it stands.
  **Ask:** `load()` returns 2 channels (a mono file duplicated to L = R). **Local workaround:** feed a stereo copy
  (`np.repeat(x, 2, axis=1)`), as `log_kya_kahenge_sfx.rough()` does.
- **(b) The bus glue flattens hero hits.** `master()` puts a 2:1 compressor on the bus. Its threshold is the
  98th-percentile 10 ms level - 3 dB, which the VO sets. Measured on C15 with the brief's levels: the glue took
  4.7-5.3 dB off the reveal (16.05-16.2 s) and 0.8-1.75 dB off the VO hook. So V1's VO at 0.35 s (-9.64 LUFS momentary)
  was louder than the reveal (-10.26), which fails BRIEF §18 ("max momentary within ±0.2 s of 16.0").
  **Ask:** `master(..., protect=[(t0, t1)])` (no glue inside the hero windows), or a `glue=` threshold/ratio option.
  **Local workaround (in place):** a flatter, denser reveal in the SFX stem (impact_big -8 dB sat 8, braam +4 dB sat 12).
  The reveal is now the maximum: -8.47 against -9.39 LUFS (A) and -8.82 against -9.51 (B). The margins (0.9 / 0.7 LU)
  are thin.
- **(c) `mix_reel` is not loop-safe.** The sidechains, glue and limiter all start from rest at t = 0. At 35.2 s the music
  is still ducked 9 dB after V7, but at 0.0 s it is not ducked. Measured sample step at the seam: 0.0708 against a median
  of 0.0048, a click on every Instagram loop. **Ask:** `mix_reel(..., loop=True)`: pad each input circularly, run the
  chain, crop. **Local recipe (verified):** `log_kya_kahenge_sfx.py rough --loop` (`_loop_mix`, 3 s pads) gives a seam
  step of 0.0074 against a median of 0.0051, at -14.00 LUFS / -2.21 dBTP (A).

## Numbering note (creative-director, 2026-10-09)

Two entries above are headed R5. `HANDOFF.md` §12 keeps R5 for the god-ray hold-out (face-compositor) and calls the
`epic_mix` entry (sound-designer; `SOUND.md` R5a/b/c) **R6** (a/b/c). No new request from the handoff.

## R6 status (music-supervisor, 2026-10-09): all three worked around in `log_kya_kahenge_mix.py`, plus one new finding

- **(a) mono VO:** `load_exact()` reads each input and copies a mono file to L = R (it also refuses any input that is not
  exactly 1,689,600 samples at 48 kHz, instead of padding it silently).
- **(b) glue on hero hits:** the glue's gain reduction is capped at 1.5 dB inside 15.97-16.40 s, and the score is ducked a
  further 10 dB under the SFX reveal (15.99-16.33). Measured: the reveal is 3.2 LU over the next loudest moment in mix A
  (r1: 0.7-1.0), and the limiter stays ≤ 3.35 dB (> 3 dB for 0.02 s, on two VO plosives). With no glue at all on the reveal the
  limiter did 6.1 dB there for 0.32 s, which is why the cap is 1.5 dB and not 0.
- **(c) loop seam:** every input is padded circularly by 4 s, processed, then cropped. The processed audio after 35.2 s
  equals the cropped start to < -240 dBFS. Seam step 1.29-1.36x the local median.
- **(d) new: `mix_reel`'s stems do not sum to mix A.** It writes `stem_* = x · gain · limiter` but mix A also went through
  `glue()`, so the stems are missing the glue's gain curve (up to 3.6 dB on C15). **Ask:** apply the same glue curve to the
  stems. **Local workaround:** `log_kya_kahenge_mix.py` multiplies each stem by the whole bus curve (glue · gain · limiter).
  Measured residual of the sum against A: -138.5 dBFS (24-bit rounding).

## R7 · `jawad_tx` L3 (and every `_tx_cut` transition): step options crash the cut (motion-timeline-builder, 2026-10-09, session 3)

- **Why:** `Tx.__call__` strips only `pre` / `post` and passes the remaining step options to `self.fn`. L3 / L4 / D7 use
  `_tx_cut(t, w, A, B)`, which takes no keyword arguments, but their post functions read options (`_l3_post` reads
  `push_gain`). So `X.Plan([('L3', 12.8, dict(push_gain=0.5))]).draw(t, scenes)` raises
  `TypeError: _tx_cut() got an unexpected keyword argument 'push_gain'` on the 4 frames after every L3 cut (window pre 0,
  post 4). Reproduced in this reel at 12.8 s (f384); any reel that sets `push_gain` on an L3 hits it.
- **Ask:** `def _tx_cut(t, w, A, B, **_o)` (the cut ignores its options; `post_kw` keeps reading them). Default behaviour unchanged.
- **Local workaround now:** `log_kya_kahenge.plan_draw()` draws every window whose `fn is X._tx_cut` itself as the plain
  HALF-rule cut (`X.side_b(t, c)`); windows, samples and `plan.post_kw` (the push) are untouched.

## R8 · `jawad_tx` O2 (`_tx_smoke`): the smoke scrolls by `np.roll` over a non-tileable fbm (motion-timeline-builder, 2026-10-09, session 3)

- **Why:** `_tx_smoke` advects the smoke with `np.roll(n, -sh, axis=0)` / `np.roll(n2, -2 * sh, axis=0)` (jawad_tx.py ~l.1707),
  but `fbm()` is not periodic, so the rolled rows meet the first rows in a hard horizontal line that travels up through the smoke
  as `sh` grows (seen in this reel's O2 at 9.6 s and in hook B's at 2.4 s).
- **Ask:** generate the fbm `extra` rows taller than H4 (rise / 4 + margin) and slice `[sh:sh + H4]` instead of rolling (or make
  `fbm` tileable in y). Default look unchanged.
- **Local workaround now:** `log_kya_kahenge._fbm_tall()` + `o2_smoke()` (a copy of `_tx_smoke` reading the slice), called from
  `plan_draw()` for every O2 window; window, samples and post unchanged.
