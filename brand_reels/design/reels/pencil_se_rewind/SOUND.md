# pencil_se_rewind: SOUND

This is a VO-led mix (LEAD_DECISIONS 1 and 3). The deliverables are:
- `_ig` = VO + SFX + music (mix_A);
- `_ig_songready` = VO + SFX (mix_B);
- VO, SFX and music stems.

Every check below is a measurement. Nobody has listened to this mix.

## Files and rebuild

| what | path |
|---|---|
| VO chain and placement | `pipeline/jawad_reels/pencil_se_rewind_vo.py` (`process`, then `assemble`). It writes `workspace/.../vo/vo_stem.wav` and `words.json`, plus `brand_reels/assets/pencil_se_rewind/vo_final/`. |
| music | `pipeline/jawad_reels/pencil_se_rewind_music.py` (`build`, `verify`). It writes `workspace/.../audio/music.wav`. |
| SFX and mixes | `pipeline/jawad_reels/pencil_se_rewind_sfx.py` (`build` = SFX, the VO-ducked SFX, the music ride, mix_A, mix_B, stems, AAC check and verify). Other modes: `cues`, `audition`, `verify`. |
| outputs | `workspace/jawad_reels/pencil_se_rewind/audio/`: `mix_A.wav`, `mix_B.wav`, `stems/stem_{vo,sfx,music}.wav`, `sfx.wav` (with `sfx_fx.wav` and `sfx_bed.wav`), `sfx_vo.wav`, `music_mix.wav`, `mix_summary.json`, `sound.verify.json`, `mix_A_overview.png`, `mix_B_overview.png` |

Rebuild (heavy jobs only):

```
cd pipeline/jawad_reels
tools/heavy.sh python3 pencil_se_rewind_vo.py assemble
tools/heavy.sh python3 pencil_se_rewind_sfx.py build
```

The SFX build rebuilds the music if it is stale.

Render with `--no-sfx-build --audio workspace/jawad_reels/pencil_se_rewind/audio/mix_A.wav` for `_ig`, and with `mix_B.wav` for `_ig_songready`.

## Policy

- The bed is SFX plus a music loop. The music uses the reel grid of 112.5 BPM (16 frames per beat).
- Every SFX cue has an on-screen cause. The frame cue table is at the top of `pencil_se_rewind_sfx.py`.
- The drop-out f752–f767 is real silence: the music is digital silence, and only a -48 dB room tone remains.
- The payoff (f768) is a single saturated `psr_payoff` hit (key + impact_soft + impact_big + sub_drop, soft-clipped) to keep its crest low. The payoff is the loudest moment.
- Custom sounds are local to the SFX module and all pass `A.qc`: psr_ratchet, psr_key, psr_motor, psr_lid_pop, psr_crinkle, psr_rehook, psr_payoff and psr_hiss (bed). Their spectrograms are in `audio/audition/`.

## Cue summary (frames at 30 fps)

| frame | event | sounds |
|---|---|---|
| 0 | open | psr_ratchet (one revolution), impact_soft lp |
| 43 | `Pencil.` slam (on the VO) | impact_soft (hero), shimmer hp |
| 128, 192 | pencil turns, paper | psr_ratchet, leaf_rustle |
| 256 | D8 | riser, whoosh_fast, impact_soft, fast ratchet (ducked under "andaza", by design) |
| 320 / 347 / 376 / 392 | PLAY / STOP ("Galat!") / REW ("Phir se") / PLAY 2 | psr_key down/up, psr_motor |
| 452–464 | lid pop, crinkle, re-hook | psr_lid_pop, psr_crinkle, psr_rehook (hero) |
| 512–600 | slow wind, reveal | psr_ratchet 0.5x, reversed crinkle, riser, whoosh_slow, glass_tap |
| 648 / 656 / 664 / 672 | scrub jumps, cut | jd_timeline_scrub ±, ui_click, pop |
| 724 | exit into drop-out | whoosh_slow |
| 752–767 | drop-out | silence (room tone at -48) |
| 768 | payoff | reverse_swell into psr_payoff (hero) |
| 832 | `Pencil.` key | ui_tick, pop |
| 896–941 | outro card, question | ui_click, card_slide, ratchet, swish_small, glass_tap, shimmer |
| 1024 | tail | reverse_swell |

Beds:
- room_tone at -40 (seed-1 layer at -42 for f464–512);
- -48 in the drop-out;
- psr_hiss at -44 from f896.

## Deviations from SHOTS

- **VO-led frame moves.** See VO_TIMING.md section 3. The music and SFX already use the new frames:
  - STOP f347;
  - REW f376;
  - PLAY 2 f392;
  - L8 f430;
  - scrub f648/656/664/672;
  - `Pencil.` slams f43 and f832.
- **V9 dropped** (ladder F4, the Bijli precedent). Otherwise V10 runs into the drop-out.
- **SFX under the VO.** `sfx_vo.wav` is the SFX bus with a per-word floor: the SFX stays 12.5 LU under every word, with a maximum cut of 18 dB and no re-level afterwards. It sits in the mix at -23.6 LUFS (-18.5 before the floor).
- **Stem limiter.** The SFX stem limiter is capped at 3 dB GR, so the stem loudness follows from the cap (sfx.wav is -19.6 LUFS, not -18).
- **VO rides** (gentle, per line, no squash):

  | line | ride | why |
  |---|---|---|
  | V2 | -0.5 | keeps the payoff loudest |
  | V5 | -1 | keeps the payoff loudest |
  | V7 | -2.5 | the whisper line |
  | V10 | -2.5 | keeps the payoff loudest |
  | V11 | +0.5 | margin for "Pencil." over the bed |
  | V13 | -1 | its plosive "Aap" hit the master limiter outside any hero window |

- **Music.**
  - +3 dB ride on f768–790;
  - -3 dB overall;
  - ducked 1.5 dB under the SFX;
  - ducked under the VO windows from words.json.

## Measurements (ebur128; latest build)

| file | I (LUFS) | TP (dBTP) | LRA (LU) |
|---|---|---|---|
| mix_A.wav | -14.0 | -2.3 | 2.2 |
| mix_B.wav | -14.0 | -2.3 | 3.3 |
| mix_A AAC | -14.0 | -2.2 | |
| mix_B AAC | -14.0 | -2.3 | |
| stem_vo | -14.0 | -1.8 | 3.5 |
| stem_sfx | -23.3 | -2.2 | 15.7 |
| stem_music | -24.6 | -6.1 | 8.6 |
| music.wav | -16.0 | -3.3 | 6.5 |
| sfx.wav | -19.6 | -2.3 | 19.8 |

stem_vo peaks at -1.8 dBTP because the stems are pre-limiter slices of mix_A. The stems sum back to mix_A with a residual of -138.5 dBFS.

Other checks:
- **VO over the bed, per word (mix_A).** Minimum 8.0 LU, median 13.4 LU. No word is below the rule. The mix_reel `words` check passes.
- **Loudest moment.** The payoff, at -9.5 LUFS momentary (f774). The re-hook peaks at -10.7 and everything else at -10.2 or below.
- **Drop-out.** mix_A momentary is -44.0 LUFS at f752–764, against -16.2 just before. The music is digital silence there.
- **Master limiter (mix_A).** Max GR 4.1 dB. GR is above 3 dB for 0.067 s in total, all inside the payoff hero window, with no off-hero spans. mix_B limiter passes.
- **mix_reel checks.** All pass: A and B lufs, tp, lra and limiter; vo_over_music; vo_over_sfx; words; stems_sum.
- **Music verify.** Chords, seam and silences pass.

## Open items

- Listener checks:
  - V11 पहला: both whisper models hear it as वहला.
  - V9 पीछे is heard as पीचे. V9 is dropped, but this matters if it is restored.
- The lead must approve the V9 drop and the frame moves in VO_TIMING.md section 3.
- Hook B mixes are not built. Only `vo_stem_B.wav` and `words_B.json` exist.
