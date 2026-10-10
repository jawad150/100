"""reel3 "Peace of mind": final SFX cue sheet (sound designer). BRIEF.md §6.3 / §8, music map in MUSIC_reel3.md.

Builder adopts it in reel3.py with:   from reel3_sfx import cues, BED, BED_GAIN_DB

All cues align='hit' except the counter's slot_tick and the plate's grow_swell (align='start', motion length).
Times come from reel3.py constants (T_CRASH, T_ZERO, T_LOCK, MOVES, T_NEG/BANK/EXP/PCI, T_PEACE, T_OKT2, T_CONF,
T_FULL, T_CTA, T_CLICK). Tonal cues are pitched into the score's key (D major; hook on Bm, resolve Dmaj9 at 15.273):
  glass_tap ~2150 Hz -> D7 on "zero", A6 on the PCI badge; logo_sting C5 -> D5 (root of the Dmaj9 resolve).
No bed: the score runs wall to wall; the airy page stays clean (no busy detail under the VO).

Build the stem (-18 LUFS, <= -2.0 dBTP):   nice -n 10 python3 reel3_sfx.py
The final mix (VO + SFX + music) is built by reel3_music.py: render with --audio <WS>/audio/reel3_mix.wav.
"""
import os

BED, BED_GAIN_DB = None, -30.0

GT = 2150.0
D7, A6 = 2349.3 / GT, 1760.0 / GT
STING_D = 587.33 / 523.25                              # logo_sting C5 -> D5


def cues():
    import reel3 as M                                   # lazy: reel3 imports this module
    mv = M.MOVES
    return [
        # hook: the red candle is already falling at frame 0, accelerates, punches through the chart on "crashes"
        dict(t=0.05, name='whoosh_slow', gain_db=-11),
        dict(t=M.T_CRASH - 0.18, name='whoosh_fast', gain_db=-6),
        dict(t=M.T_CRASH, name='impact_big', gain_db=-6),                      # crash slot + "crashes" slam
        dict(t=M.T_CRASH, name='downlifter', gain_db=-8),                      # balance plunges
        dict(t=M.T_WITH + 0.04, name='swish_small', gain_db=-7),               # headline fades in, camera follows
        # zero: counter accelerates to 0.00, shield slams on "zero", padlock clicks shut
        dict(t=M.T_YOUR, name='slot_tick', align='start',
             params=dict(dur=round(M.T_ZERO - M.T_YOUR, 3)), gain_db=-9),
        dict(t=M.T_ZERO, name='impact_soft', gain_db=-3),
        dict(t=M.T_ZERO, name='glass_tap', params=dict(pitch=D7), gain_db=-4),
        dict(t=M.T_ZERO, name='sub_drop', params=dict(dur=1.4), gain_db=-6),
        dict(t=M.T_LOCK, name='ui_click', gain_db=-5),
        dict(t=M.T_LOCK + 0.02, name='toggle_on', gain_db=-4),
        # journey: shield leads the light trail; whoosh pass at the fastest point of each move, card pops
        dict(t=round((mv[0][0] + mv[0][1]) / 2, 3), name='whoosh_by', params=dict(dur=0.9, direction=1),
             pan=0.25, gain_db=-6),
        dict(t=M.T_NEG, name='pop', gain_db=-5),
        dict(t=M.T_NEG + 0.2, name='shimmer', params=dict(dur=1.0), gain_db=-12, hp=4000),
        dict(t=round((mv[1][0] + mv[1][1]) / 2, 3), name='whoosh_by', params=dict(dur=0.9, direction=-1),
             pan=-0.25, gain_db=-6),
        dict(t=M.T_BANK, name='pop', gain_db=-5),
        dict(t=round((mv[2][0] + mv[2][1]) / 2, 3), name='whoosh_by', params=dict(dur=0.9, direction=1),
             pan=0.25, gain_db=-6),
        dict(t=M.T_EXP, name='pop', gain_db=-5),
        dict(t=M.T_PCI, name='glass_tap', params=dict(pitch=A6), gain_db=-7),  # "PCI DSS" badge
        # gather: cards fly into a ring round the shield, "peace of mind"
        dict(t=11.65, name='whoosh_slow', gain_db=-7),
        dict(t=M.T_PEACE, name='shimmer', params=dict(dur=1.2), gain_db=-9),
        # navy plate grows out of the shield 13.01 -> fills 15.15; mark swirls in; "Confidence" slam 14.33
        dict(t=M.T_OKT2, name='grow_swell', align='start', params=dict(duration=round(M.T_FULL - M.T_OKT2, 3)),
             gain_db=-8),
        dict(t=M.T_OKT2 + 0.04, name='shimmer', params=dict(dur=1.0), gain_db=-10),
        dict(t=M.T_CONF, name='impact_soft', gain_db=-4),
        dict(t=15.05, name='whoosh_fast', gain_db=-11),                        # headline leaves 14.95-15.25
        # end card: button springs in, logo crossfade, cursor press
        dict(t=M.T_CTA, name='pop', gain_db=-4),
        dict(t=M.T_RISK, name='logo_sting', params=dict(tone=STING_D), gain_db=-2),       # mark -> logo_full 15.55
        dict(t=M.T_CLICK, name='ui_click', gain_db=-5),
        dict(t=M.T_CLICK + 0.02, name='toggle_on', gain_db=-4),
    ]


def build():
    import audio as A, reel3 as M
    name = 'reel3'
    os.makedirs(os.path.join(A.OUT, name), exist_ok=True)
    rep = A.mix(cues(), M.DUR, os.path.join(A.AUDIO, name + '_sfx.wav'), os.path.join(A.AUDIO, name + '_sfx_stem.wav'),
                bed=BED, bed_gain_db=BED_GAIN_DB, tp_ceiling=-2.0, split_stems=True)
    A.mix_overview(rep, os.path.join(A.OUT, name, name + '_sfx_overview.png'), name + ' SFX')
    return rep


if __name__ == '__main__':
    import audio as A
    print(A.report_text(build()))
