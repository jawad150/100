"""reel1 "Every market": final SFX cue sheet (sound designer). BRIEF.md §6.1 / §8, music map in MUSIC_reel1.md.

Builder adopts it in reel1.py with:   from reel1_sfx import cues, BED, BED_GAIN_DB

All cues align='hit' except the counter's slot_tick (align='start', motion length). Times come from reel1.py (W,
WHIPS, T_TUN, T_ZERO, T_GLOBE2, E0, TC). The music drop is at 3.871 (beat 8, the whip into the globe).
Tonal cues are pitched into the score's key (F minor, resolving to Ab major on the end card):
  glass_tap ~2150 Hz -> chips rise Ab6 Bb6 C7 Eb7 F7; coin_ring 2750 -> F7; check_ding E6/B6 -> Eb6/Bb6;
  logo_sting C5 -> Eb5 (the fifth of the Ab add9 resolve).
No bed: the score runs wall to wall.

Build the stem (-18 LUFS, <= -2.0 dBTP):   nice -n 10 python3 reel1_sfx.py
The final mix (VO + SFX + music) is built by reel1_music.py: render with --audio <WS>/audio/reel1_mix.wav.
"""
import os

BED, BED_GAIN_DB = None, -30.0

GT = 2150.0                                            # glass_tap base pitch
CHIP_PITCH = [1661.2 / GT, 1864.7 / GT, 2093.0 / GT, 2489.0 / GT, 2793.8 / GT]   # Ab6 Bb6 C7 Eb7 F7
COIN_F7 = 2793.8 / 2750.0
DING_EB = 1244.5 / 1318.5                              # check_ding E6 -> Eb6 (B6 -> Bb6)
STING_EB = 622.25 / 523.25                             # logo_sting C5 -> Eb5


def cues():
    import reel1 as M                                   # lazy: reel1 imports this module
    W, WH = M.W, M.WHIPS
    c = [
        # hook: four word slams (impact on each word), whips on beats 2/4/6/8
        dict(t=W['forex'] - 0.10, name='whoosh_fast', gain_db=-3),           # coin_usd flies in from depth
        dict(t=W['forex'], name='impact_big', gain_db=-2),
        dict(t=WH[0], name='whip', params=dict(direction=1), pan=-0.2, gain_db=-3),
        dict(t=W['gold'], name='impact_big', gain_db=-2),
        dict(t=W['gold'] + 0.02, name='coin_ring', params=dict(pitch=COIN_F7), gain_db=-7),   # gold bar rim
        dict(t=WH[1], name='whip', params=dict(direction=1), pan=0.2, gain_db=-3),
        dict(t=W['bitcoin'] - 0.12, name='coin_flip', gain_db=-4),           # coin_btc flips in
        dict(t=W['bitcoin'], name='impact_big', gain_db=-2),
        dict(t=WH[2], name='whip', params=dict(direction=1), pan=-0.2, gain_db=-3),
        dict(t=W['nvidia'], name='impact_big', gain_db=-2),
        # drop 3.871: whip into the globe (riser end + whip + sub = 3)
        dict(t=WH[3], name='riser', params=dict(duration=0.65), gain_db=-6),
        dict(t=WH[3], name='whip', params=dict(direction=1), pan=0.2, gain_db=-2),
        dict(t=WH[3], name='sub_drop', params=dict(dur=1.6), gain_db=-5),
        dict(t=4.50, name='impact_soft', gain_db=-4),                         # objects burst into the sphere
        dict(t=4.70, name='shimmer', params=dict(dur=1.2), gain_db=-7),      # sphere assembles 4.30-5.10
    ]
    for (_, k), p in zip(M.CHIPS, CHIP_PITCH):                                # one glass chip per spoken market
        c.append(dict(t=W[k], name='glass_tap', params=dict(pitch=p), gain_db=-7))
    c += [
        dict(t=8.78, name='reverse_swell', params=dict(duration=0.45), gain_db=-7),   # zoom-through the sphere
        dict(t=8.78, name='air_zoom', gain_db=-3),
        dict(t=W['mt5'], name='shimmer', params=dict(dur=1.0), gain_db=-9, hp=4000),  # "Powered by MT5" sweep
        dict(t=M.T_TUN + 0.15, name='whoosh_by', params=dict(direction=1), gain_db=-4),  # card tunnel rush
        dict(t=W['zero'], name='slot_tick', align='start',
             params=dict(dur=round(W['two'] - W['zero'], 3), ease='out'), gain_db=-7),  # counter 2.0 -> 0.2
        dict(t=W['two'], name='check_ding', params=dict(pitch=DING_EB), gain_db=-3),    # counter lands 11.71
        dict(t=M.T_ZERO, name='whip', params=dict(direction=-1), gain_db=-3),           # whip down 12.52
        dict(t=W['zero_fees'], name='impact_big', gain_db=-1),                           # "0%" slam 12.69
        dict(t=W['zero_fees'], name='glitch_short', gain_db=-5),                         # fee tag shatters
        dict(t=W['hidden'], name='swish_small', gain_db=-8),
        dict(t=W['fees'], name='swish_small', gain_db=-8),
        dict(t=M.T_GLOBE2, name='impact_soft', gain_db=-4),                   # globe returns 14.03 (beat 29)
        dict(t=W['oktrum'], name='shimmer', params=dict(dur=1.2), gain_db=-7),   # wordmark 14.24
        dict(t=16.40, name='shimmer', params=dict(dur=0.8), gain_db=-9, hp=4000),  # light sweep 16.40-16.95
        dict(t=M.E0 + 0.05, name='whoosh_fast', gain_db=-8),                  # type exits, globe flies up
        dict(t=M.E0 + 0.25, name='logo_sting', params=dict(tone=STING_EB)),   # 17.05 mark resolves
        dict(t=W['cta'], name='pop', gain_db=-3),                             # button pops 17.24
        dict(t=M.TC, name='ui_click', gain_db=-2),                            # cursor press 17.68
        dict(t=M.TC + 0.03, name='toggle_on', gain_db=-3),
    ]
    return c


def build():
    import audio as A, reel1 as M
    name = 'reel1'
    os.makedirs(os.path.join(A.OUT, name), exist_ok=True)
    rep = A.mix(cues(), M.DUR, os.path.join(A.AUDIO, name + '_sfx.wav'), os.path.join(A.AUDIO, name + '_sfx_stem.wav'),
                bed=BED, bed_gain_db=BED_GAIN_DB, tp_ceiling=-2.0, split_stems=True)
    A.mix_overview(rep, os.path.join(A.OUT, name, name + '_sfx_overview.png'), name + ' SFX')
    return rep


if __name__ == '__main__':
    import audio as A
    print(A.report_text(build()))
