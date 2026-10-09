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

## 3. vo_chain: short, peaky takes come out below -16 LUFS (filed 2026-10-09 by hinglish-scriptwriter)

- **What:** `vo_chain.stretch_and_master` runs `loudnorm` (linear) and then `alimiter` at -2.3 dBFS. On short takes with
  a high peak-to-loudness ratio the true-peak target wins and the take stays quiet: measured on this reel's processed
  takes `btk_L1B-R_t1_1.08.wav` -18.9 LUFS, `btk_L5-C_t1_1.08.wav` -17.6, `btk_L3-J_t1_1.08.wav` -16.8, while the
  other nine lines land on -16.0 (ffmpeg ebur128). Placed side by side, L1B was 3 LU quieter than the body.
- **Suggested fix:** after the two-pass loudnorm, measure the output and, if it is more than 0.5 LU under the target,
  raise it with a lookahead limiter at the TP ceiling (or report it in `report['loudness']` so callers can level-match).
- **C02 workaround (local):** `beta_tum_karte_kya_ho_vo.load_clip` level-matches each processed take to -16 LUFS before
  placement; the stem's master limiter (-2.6 dBFS, latency-compensated) then holds TP at -2.46 dBTP with gain reduction
  above 1 dB on 0.8 % of the loud 10 ms windows (max 2.1 dB). Per-line loudness in the stem is now -15.2 to -16.1 LUFS.
