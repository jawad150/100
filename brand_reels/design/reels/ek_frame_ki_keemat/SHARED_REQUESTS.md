# Shared-module requests from C08 · Ek Frame ki Keemat (creative-director, 2026-10-08)

Shared modules are read-only for this reel. Each request below has a local workaround already written into `BRIEF.md`, so
nothing blocks the build. Owners decide; please do not change behaviour that other reels rely on.

## R1 · `endcard.EndCard`: signature x position (`x_sig=`)
- **Need:** C08 frames JD bottom-left (face box x 242-564, y 1120-1564). The card draws `J.signature` at `x = K.CX` (540), which
  puts `@jawad_mp4` (box x 411-669, y 1563-1587) on his chin.
- **Ask:** an optional `x_sig=K.CX` argument used by `_draw_type` and `boxes()`.
- **Workaround (in the brief):** `EndCard(..., handle=False)` and the reel module draws `J.signature(cv, 760, 1575,
  opacity=ramp(t, t0 + 1.0, t0 + 1.45, 'inout_sine') * (1 - ramp(t, t0 + dur - 0.36, t0 + dur - 1/30, 'in_cubic')))`, which
  mirrors the card's own envelope. Box x 631-889 (inside the x 930 column).

## R2 · `jawad_tx`: `push_gain` cannot reach the transitions that read it
- **Found:** the post functions of C2, C8, M1, D9, O4, O6, L1 and L3 read `o.get('push_gain', ...)`, but `Tx.__call__` passes
  every option except `pre`/`post` to the transition function, and none of those eight functions takes `**kw` (checked with
  `inspect.signature`). Measured: `X.TX['C8'](26.39, 26.4, A, B, push_gain=1.0)` -> `TypeError: _tx_crash() got an unexpected
  keyword argument 'push_gain'`.
- **Ask:** strip `push_gain` in `Tx.__call__` (as it does for `pre`/`post`), or give the transition functions `**_`.
- **Workaround (in the brief):** C8 keeps its default push 0.4 and the extra 0.6 comes from `cuts=[..., (26.4, 0.6)]` in
  `G.tx_finish`.

## R3 · `epic_mix.mix_reel(sfx_cues=...)`: no way to turn off the SFX tail fade
- **Found:** the `sfx_cues` path calls `A.mix(...)` with the default `tail_fade=0.4`, which fades the last 0.4 s of the SFX stem.
  A looping reel's swell must end at full level exactly on DUR (it is frame 0's pre-lap).
- **Ask:** pass a `tail_fade=` argument through (default unchanged).
- **Workaround (in the brief):** the reel's `_sfx.py` builds the stem itself with `A.mix(..., tail_fade=0.0)` and passes the file
  as `sfx=` to `mix_reel`.

## R4 · `epic_music.render`: per-style options (mute a stem, skip the common fx)
- **Need:** C08 wants `desi_epic` without the sitar lead, without dholak rolls and without `_common_fx`'s frame-0 `trailer_hit`
  and drop braam, with shortened risers, and with no end fade inside DUR.
- **Ask (optional):** `render(..., mute=('lead',), fx=False)` or similar.
- **Workaround (in the brief):** a local copy of `style_desi_epic` registered at runtime as `EM.STYLES['c08_epic']`, rendered at
  36.0 s and cropped to 33.6 s (the module's 1.2 s end fade then lies outside the reel).

## R5 · `audio.read_wav` / `audio._write_wav`: 24-bit round trip is not lossless (music-supervisor, 2026-10-08)
- **Found:** `read_wav` scales 24-bit codes by 1/8388608 but `_write_wav` multiplies by 8388607, so reading a 24-bit file and
  writing it back moves some samples by 1 code (measured: max 1 LSB = 1.19e-7 on the C08 hook-B splice test).
- **Ask:** use the same factor in both directions (8388608 on write, clipped to [-8388608, 8388607]).
- **Workaround:** none needed; `ek_frame_ki_keemat_music.mix(hook='B')` documents that the B body equals A to 1 LSB.

## R6 · `vo_chain.snap_to_voice`: a word can stay glued across a real pause (hinglish-scriptwriter, 2026-10-09)
- **Found (final VO takes):** whisper put a word's start inside the voiced tail of the previous word, 0.14-0.48 s before a
  0.21-0.37 s pause, and the tail-fragment rule (`frag=0.10`) did not catch it: `efk_V7_t1` "teen" 1.67 s while the voice
  resumes after "second..." at 2.16 s; `efk_V9_t2` "banane" 0.52 s straddling the pause 0.79-1.00 s ("Keemat..." really
  ends 0.79). `--realign` agreed with the mapped times (same whisper bias), so the report showed no disagreement.
- **Ask:** after snapping, a word that straddles a voiced-run gap >= 0.12 s should move to the side that holds more of it
  (after the gap when the previous token ends a clause), the previous word ending on the voice offset.
- **Workaround (local):** `ek_frame_ki_keemat_vo.fix_gap_words()` applies exactly that rule to every placed clip before
  placement; checked against the spectrograms (`<RW>/vo/asr/spec_V9.png`).

## R7 · `epic_mix.load` / `mix_reel`: a mono VO wav raises (sound-designer, 2026-10-09)
- **Found (final VO, real run):** the FINAL VO stems are 48 kHz 24-bit **mono**. `audio.read_wav` returns them as `(N, 1)`, and
  `audio._st` passes any 2-D array through unchanged, so `epic_mix.load()` hands `mix_reel` a `(N, 1)` array and line 118
  (`np.concatenate([np.zeros((_n(vo_offset), 2)), v])`) raises `ValueError: ... size 2 and ... size 1`. The music-supervisor's
  `ek_frame_ki_keemat_music.py mix` calls `mix_reel` with `<RW>/vo/ek_frame_ki_keemat_vo.wav`, so the final mix will fail the
  same way (it was tested on stereo placeholders only, MUSIC_ek_frame_ki_keemat.md "Run 2").
- **Ask:** in `epic_mix.load`, expand a 1-column array to stereo (`x = np.repeat(x, 2, 1) if x.ndim == 2 and x.shape[1] == 1`),
  or have `audio._st` treat `(N, 1)` as mono.
- **Workaround (local, no shared edit):** `ek_frame_ki_keemat_sfx.rough()` writes dual-mono stereo copies of the VO stems
  (identical L/R samples) to a temporary folder, passes those, and deletes them. The music-supervisor can pass the same kind of
  copy with `--vo` / `--vo-b` until the loader is fixed.
