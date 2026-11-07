"""mix.py: voice + music + SFX -> the master mix and stems (PDF: voice about -16 LUFS, master -14 LUFS).

    python3 audio/mix.py            (from hulk_marketing/door-that-wont-open)

Writes audio/mix.wav (48 kHz 24-bit, -14 LUFS integrated, <= -1 dBTP) and audio/mix_novo.wav (music + SFX only,
same levels, for captions-only use), plus stems/ (vo, music as ducked in the mix, sfx) at the master's level.
Music ducks 12 dB under the voice (25 ms attack, 350 ms release); the voice itself is never pushed past -16 LUFS
by more than the final trim (printed).
"""
import os
import sys

import numpy as np
import soundfile as sf

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', '..', 'pipeline', 'fostering'))
import audio as A  # noqa: E402

SR = A.SR
DUR = 36.5
N = int(DUR * SR)


def load(name):
    x = sf.read(os.path.join(HERE, name), dtype='float64')[0]
    x = A._st(x)
    return x[:N] if len(x) >= N else np.vstack([x, np.zeros((N - len(x), 2))])


def speech_lufs(x, vo):
    # loudness of x over the voiced parts only (where the VO stem is active)
    lvl = np.sqrt(np.convolve((vo[:, 0] ** 2), np.ones(2400) / 2400, 'same'))
    m = lvl > 10 ** (-45 / 20)
    return A.loudness(x[m].astype(np.float32))


def main():
    vo, music, sfx = load('vo.wav'), load('music.wav'), load('sfx.wav')
    # tame the voice's peaks without changing its level
    vo = vo * A.limiter_gain(vo, ceiling_db=-3.0)[:, None]
    print(f'voice: {speech_lufs(vo, vo):.1f} LUFS over speech')
    music_d = A.sidechain(music, vo, depth_db=12.0, attack=0.025, release=0.35, thresh_rel_db=-32)
    gm, gs = A.undb(0.5), A.undb(2.0)       # music bed about -17.5 LUFS, SFX about -19.5 LUFS before the master trim
    bus = vo + music_d * gm + sfx * gs
    novo = music * gm * A.undb(2.0) + sfx * gs
    trim_db = 0.0
    for name, x in (('mix.wav', bus), ('mix_novo.wav', novo)):
        y = x.copy()
        for it in range(8):
            I = A.loudness(y.astype(np.float32))
            y = y * A.undb(-14.0 - I)
            g = A.limiter_gain(y, ceiling_db=-1.2)
            y = y * g[:, None]
            if abs(A.loudness(y.astype(np.float32)) + 14.0) < 0.1 and A.true_peak(y) <= -1.0:
                break
        nf = int(0.25 * SR)
        y[-nf:] *= np.linspace(1, 0, nf)[:, None]
        A._write_wav(os.path.join(HERE, name), y.astype(np.float32), bits=24)
        print(f'{name}: {A.loudness(y.astype(np.float32)):.2f} LUFS  TP {A.true_peak(y.astype(np.float32)):.2f} dBTP')
        if name == 'mix.wav':
            trim = A.loudness(y.astype(np.float32)) - A.loudness(bus.astype(np.float32))
            trim_db = trim
            print(f'  music {A.todb(gm) if hasattr(A, "todb") else 20 * np.log10(gm):+.1f} dB, sfx {20 * np.log10(gs):+.1f} dB, final trim {trim:+.2f} dB'
                  f' -> voice ~{speech_lufs(vo * A.undb(trim), vo):.1f} LUFS over speech')
    # stems at the master's level: vo + music + sfx sum to mix.wav (before its peak limiter, which only touches peaks)
    k = A.undb(trim_db)
    os.makedirs(os.path.join(HERE, 'stems'), exist_ok=True)
    A._write_wav(os.path.join(HERE, 'stems', 'vo_stem.wav'), (vo * k).astype(np.float32), bits=24)
    A._write_wav(os.path.join(HERE, 'stems', 'music_stem.wav'), (music_d * gm * k).astype(np.float32), bits=24)
    A._write_wav(os.path.join(HERE, 'stems', 'sfx_stem.wav'), (sfx * gs * k).astype(np.float32), bits=24)
    print('-> audio/mix.wav, audio/mix_novo.wav, audio/stems/')


if __name__ == '__main__':
    main()
