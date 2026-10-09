# Shared requests from reel C02 (beta_tum_karte_kya_ho)

Filed 2026-10-08 by creative-director. Neither request blocks this reel: both have a local workaround written into
`BRIEF.md`. Owners: motion-toolkit-engineer (jawad_tx.py), colorist (jawad_grade.py).

## 1. jawad_tx: options meant for a transition's post function crash its draw function

- **What:** `Tx.__call__` forwards every option except `pre` / `post` to the draw function. Options that only the
  post function reads therefore raise inside `Plan.draw`:
  - `X.Plan([('L3', 2.0, dict(push_gain=0.5))])` → `TypeError: _tx_cut() got an unexpected keyword argument 'push_gain'`
  - `X.TX['M2'](t, c, A, B, look='gold_hour')` → `TypeError: _tx_hue() got an unexpected keyword argument 'look'`
  (reproduced on 2026-10-08; `Plan.post_kw` itself accepts both).
- **Suggested fix:** in `Tx.__call__`, drop the option names a transition's post function consumes (`push_gain`,
  `look`) before calling `fn`, or give `_tx_cut` / `_tx_hue` a `**_` sink.
- **C02 workaround:** L3 entries carry no options; glue push gains go through `finish(cuts=[(c, gain), ...])`;
  M2 runs without `look` (gold_hour and the default look both have exposure 0.0, so the bridge is identical).

## 2. jawad_grade: gold_hour god rays streak type and UI, and burst around centred marks

- **What:** `G.finish(cv, 'gold_hour', t)` applies `K.god_rays` (strength 0.26, threshold 0.30) to the whole finished
  canvas, so every bright type / UI pixel throws streaks (chat bubble, caption words, the POV label). On the end card
  the rays radiate from the centred JD monogram ring and the CTA: a centred ring with radial rays, which is the banned
  OpenArt cover device (SLATE §5.1). Seen in the C02 layout proof
  (`workspace/jawad_reels/beta_tum_karte_kya_ho/brief_proof/sheet1_rays_default.jpg`, `sheet2_rays_default.jpg` vs `sheet3_rays0.jpg`).
- **Suggested fix:** compute the rays from the world layer only (before type / UI is drawn), or mask them to the
  backdrop's sun band, or default `rays=0` whenever an EndCard is on screen.
- **C02 workaround:** `G.tx_finish(..., rays=0.0)` on every frame of this reel (binding in BRIEF §4 / §6.16).
