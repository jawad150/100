"""reel2 "Blink": final SFX cue sheet (sound designer). BRIEF.md §6.2 / §8, music map in MUSIC_reel2.md.

Builder adopts it in reel2.py with:   from reel2_sfx import cues, BED, BED_GAIN_DB

All cues align='hit' (the transient / whoosh pass / riser end sits on t), times imported from reel2.py constants.
Tonal cues are pitched into the score's key (D minor, resolving to F major on the end card):
  glass_tap ~2150 Hz -> C7 (x0.973), D7 (x1.093), A6 (x0.819); check_ding E6/B6 -> F6/C7 (x1.0595);
  toast_chime G5/D6 (as is); logo_sting C5 -> F5 (tone x1.3348).
No bed: the procedural score (reel2_music.py) carries the room, and the blink gap 0.94-1.04 stays near-silent
apart from the lid-seam flash.

Build the stem (-18 LUFS, <= -2.0 dBTP):   nice -n 10 python3 reel2_sfx.py
The final mix (VO + SFX + music) is built by reel2_music.py: render with --audio <WS>/audio/reel2_mix.wav.
"""
import os

BED, BED_GAIN_DB = None, -30.0

# pitch ratios that put the catalog's tonal sounds into the key
C7, D7, A6 = 2093.0 / 2150, 2349.3 / 2150, 1760.0 / 2150
F_DING = 1396.9 / 1318.5          # check_ding E6 -> F6 (second note B6 -> C7)
F_STING = 698.46 / 523.25         # logo_sting C5 -> F5


def cues():
    import reel2 as M                                   # lazy: reel2 imports this module
    return [
        # A  hook: heartbeat on the 120 grid (0.02, 0.52), the blink, the price tick
        dict(t=0.02, name='heartbeat', params=dict(n=2, bpm=120), gain_db=-2),
        dict(t=M.T_SWAP - 0.01, name='flash_hit', gain_db=-5.5),                  # cyan flare on the lid seam 0.98
        dict(t=M.BL1 - 0.38, name='ui_tick', gain_db=-5),                       # 1.04 lids reopen on 67,420
        dict(t=1.30, name='whoosh_slow', gain_db=-11),                          # anamorphic streak + focus rack
        # B  the hit (riser end + sub + impact = 3 at 3.00), candles whip past the lens 3.00-3.45
        dict(t=M.CUT_B, name='riser', params=dict(duration=1.4), gain_db=-8),
        dict(t=M.CUT_B, name='sub_drop', params=dict(dur=2.0), gain_db=-3),
        dict(t=M.CUT_B, name='impact_soft', gain_db=-3),
        dict(t=M.CUT_B + 0.18, name='whoosh_by', params=dict(dur=1.0, direction=1), pan=0.3, gain_db=-5),
        # C  glass trade window: chips, hover, BUY press, light pulse, toast, MT5
        dict(t=M.T_CHIP1, name='glass_tap', params=dict(pitch=C7), gain_db=-7),
        dict(t=M.T_CHIP2, name='glass_tap', params=dict(pitch=D7), gain_db=-7),
        dict(t=M.T_HOVER, name='ui_hover', gain_db=-8),
        dict(t=M.T_PRESS, name='ui_click', gain_db=-4),
        dict(t=M.T_PRESS + 0.07, name='whoosh_fast', gain_db=-9, pan=0.4),     # cyan pulse out of frame
        dict(t=M.T_TOAST, name='check_ding', params=dict(pitch=F_DING), gain_db=-3),
        dict(t=M.T_TOAST + 0.05, name='toast_chime', gain_db=-7),
        dict(t=M.T_MT5, name='glass_tap', params=dict(pitch=A6), gain_db=-6),   # "Powered by MetaTrader 5"
        # D  cut 11.50 swells into the "lag." slam; light sweep; seize line
        dict(t=M.T_LAG, name='reverse_swell', params=dict(duration=0.6), gain_db=-9),
        dict(t=M.T_LAG, name='impact_big', gain_db=-3),
        dict(t=12.45, name='shimmer', params=dict(dur=0.8), gain_db=-10, hp=4000),  # sweep 12.45-13.25
        dict(t=M.T_SEIZE, name='swish_small', gain_db=-7),
        # E  whip to the end card, logo, CTA button, logo settle
        dict(t=M.WHIP, name='whip', params=dict(direction=-1), gain_db=-3.5),
        dict(t=M.WHIP + 0.12, name='logo_sting', params=dict(tone=F_STING)),
        dict(t=M.T_CTA, name='pop', gain_db=-4),                                # button springs in 15.15
        dict(t=M.T_CLICK, name='ui_click', gain_db=-3),                                   # cursor press 15.75
        dict(t=M.T_CLICK + 0.02, name='toggle_on', gain_db=-3),
        dict(t=16.0, name='shimmer', params=dict(dur=1.5), gain_db=-9),         # sphere -> logo_full 15.95-16.25
    ]


def build():
    import audio as A, reel2 as M
    name = 'reel2'
    os.makedirs(os.path.join(A.OUT, name), exist_ok=True)
    rep = A.mix(cues(), M.DUR, os.path.join(A.AUDIO, name + '_sfx.wav'), os.path.join(A.AUDIO, name + '_sfx_stem.wav'),
                bed=BED, bed_gain_db=BED_GAIN_DB, tp_ceiling=-2.0, split_stems=True)
    A.mix_overview(rep, os.path.join(A.OUT, name, name + '_sfx_overview.png'), name + ' SFX')
    return rep


if __name__ == '__main__':
    import audio as A
    rep = build()
    print(A.report_text(rep))
