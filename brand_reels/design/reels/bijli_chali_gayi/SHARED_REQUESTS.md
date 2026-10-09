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
