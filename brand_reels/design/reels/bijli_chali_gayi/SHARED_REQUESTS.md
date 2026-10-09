# Shared-module requests from reel C11 Bijli Chali Gayi

Raised by the creative director while writing `BRIEF.md` (2026-10-08). Each item has a local workaround that the
C11 modules use today, so none of them blocks this reel. Owner of the shared modules: motion-toolkit-engineer.

## 1. `jawad_tx.Plan` crashes when a step passes an option to L3 / L4 / D7 (reproduced)

- **What happens.** `X.Plan([('L3', 2.0, dict(push_gain=0.5))]).draw(2.0 + 1/30, [A, B])` raises
  `TypeError: _tx_cut() got an unexpected keyword argument 'push_gain'`. `Tx.__call__` forwards every option except
  `pre` / `post` to the transition function, and `_tx_cut(t, w, A, B)` takes no keywords, although `_l3_post` reads
  `o.get('push_gain', 1.0)`. The same applies to every transition built on `_tx_cut` (L3, L4, D7) and to any option
  meant only for a `post_fn` (for example `push_gain` on O4 / O6 / D9 through `_push_post`).
- **Request.** Give `_tx_cut` (and the other `fn`s whose options are post-only) a `**_post_only` catch-all, or have
  `Tx.__call__` drop the keys that only the `post_fn` uses.
- **C11 workaround.** The C11 `Plan` holds only the three feature transitions (L7, L8, L4) with options that their
  functions accept. All glue cuts are hard cuts made inside the scene functions with `X.side_b(t, c)`, and their
  exposure pushes go through `cuts=[(c, gain), ...]` in the finish call.

## 2. `endcard.EndCard(dur=DUR - T_END)` rejects a 4.0 s card by float rounding (reproduced)

- **What happens.** With `DUR = 1040 / 30` and `T_END = 920 / 30`, `DUR - T_END` is `3.9999999999999964`, and
  `EndCard` raises `ValueError: end card should run 4.5-5 s (got 4.00)` because its check is `4.0 <= dur`.
  The message also still says "4.5-5 s" while the check accepts 4.0-6.0 s.
- **Request.** Compare with a tolerance (`dur >= 4.0 - 1e-6`), or quantise `dur` to whole frames, and make the
  message say 4.0-6.0 s.
- **C11 workaround.** Pass the literal `dur=4.0` and derive `T_END = DUR - card.dur` (frame 920 by the cut rule).

## 3. `vo_chain.voiced_runs` measures a cut-out line shorter than the same audio inside a stem (found by the scriptwriter, 2026-10-09)

- **What happens.** The threshold is `max(10th percentile + 10 dB, peak - 45 dB)`. On a line cut tightly out of a
  grouped take there is almost no silence, so the 10th percentile sits inside the speech and the threshold rises: the
  same V7 measured 2.38-2.45 s as a cut clip and 2.86 s in the stem (TA's V1: 1.07 vs 1.24 s). Placement built on the
  clip spans then under-estimates every line.
- **Request.** An optional absolute threshold (`voiced_runs(x, thr_db=-55)`) or a minimum-silence padding before the
  percentile, so a mastered line and the stem it goes into are measured alike.
- **C11 workaround.** `bijli_chali_gayi_vo.py` measures clips and stems with its own `runs_abs` at -55 dBFS (20 ms RMS,
  the same windows and gap closing) and splits grouped takes at -45 dBFS gaps (`SPLIT_DBFS`).

## 4. `epic_sfx.crowd_cheer_real` is not wordless (found by the sound-designer, 2026-10-09)

- **What happens.** faster-whisper on the registered 5.0 s render (`opengameart/crowd_shouting/crowd_shouting_0.ogg`,
  "Crowd shouting/speaking ambience", CC0) hears English: small, auto/en: "Oh my God, look at that! It's just that!"
  (word probabilities 0.02-0.69; "God,", "look", "that!", "It's" >= 0.5); medium, auto/en: "Oh my God!" ("my" 0.82,
  "God!" 0.52). SLATE 2.8 / BRIEF 6.10 and
  QA 8 require a *wordless* cheer.
- **Request (owner of `workspace/brand_reels/sfx/epic_sfx.py` / its LICENSES.md).** Re-label the sample's catalog line
  ("real crowd shouting / cheering") as containing English speech, or register a de-worded variant.
- **C11 workaround.** `bijli_chali_gayi_sfx.mohalla_cheer` re-synthesises the same CC0 recording granularly (reversed
  60-100 ms grains, random positions, +-1.5 st, 80 grains/s). faster-whisper small (auto / hi / en) hears no word on
  either cue render; medium returns only its noise hallucination ("Thanks for watching!", p 0.83-0.95), which it
  also returns on pink noise and on `room_tone` (control in SOUND.md).

## 5. A mono VO stem reads +3.01 LU once duplicated to stereo (sound-designer, 2026-10-09)

- **What happens.** `vo_stem.wav` is mono, -16.00 LUFS. `audio.read_wav` returns it as (N, 1); `epic_mix.load` keeps
  that shape (`_st` only widens 1-D arrays), and duplicating it to two equal channels measures -13.0 LUFS (BS.1770
  sums the channel powers). A mix built that way puts the VO 3 dB hotter than the -16 LUFS spec relative to the
  -18 LUFS SFX stem.
- **Request (`epic_mix.py` owner / music-supervisor).** After converting a mono VO to stereo, re-normalise it to
  `SPEC['vo_lufs']` (equal-power centre), or load mono with `-ac 2` plus a -3.01 dB pan law.
- **C11 workaround.** `bijli_chali_gayi_sfx.rough()` duplicates the mono stem and re-normalises it to -16.00 LUFS
  before the mix.

## 6. `endcard.EndCard` exit puts most of the dim lift on the reel's last frame (timeline builder, 2026-10-09)

- **What happens.** The exit ramps `ex = K.ramp(t, t0 + dur - exit_dur, t_last, 'in_cubic')`, and the background dim
  (0.58) is released by `1 - ex`: on C11 (1 sample, finished) the step f1037 -> f1038 is mean |diff| 5.7 levels, but
  f1038 -> f1039 is 15.3 levels (16.4 % of pixels > 25 levels). The loop seam itself is clean (f1039 -> f0: 3.6 levels,
  1.1 % > 25), so it reads as the designed push into the loop rather than a glitch.
- **Request (endcard owner).** Optional: release the dim on `inout_sine` (or end the in_cubic one frame earlier) so the
  last-frame step matches its neighbours.
- **C11 workaround.** None needed for delivery (listed as minor, LEAD_DECISIONS 7); no change in `bijli_chali_gayi.py`.
