"""mix.py: voice + music + SFX -> the master mix and stems (PDF: voice about -16 LUFS, master -14 LUFS).

    python3 audio/mix.py            (from hulk_marketing/door-that-wont-open)

Writes audio/mix.wav (48 kHz 24-bit, -14 LUFS integrated, <= -1 dBTP) and audio/mix_novo.wav (music + SFX only,
same levels, for captions-only use), plus stems/ (vo, music as ducked in the mix, sfx) at the master's level: the
three stems sum to mix.wav before its peak limiter (asserted: stem-sum loudness within 0.1 LU of mix.wav).
Voice: "open." (4.99-5.40) clip-gained +4.5 dB; a subtle even-harmonic exciter adds the air the TTS lacks above
~7.5 kHz (8-12 kHz about -38 dB re the voice's 1-4 kHz band). Music ducks 12 dB under a look-ahead voice-activity
key built from vo_words.json (each line from its first word - 0.08 s to its last word + 0.15 s, smoothed 20 ms;
25 ms attack, 350 ms release), held down after the last word so it never swells back into the final chord. The
last 0.9 s (from 35.6) fade exponentially on the bus, so the stems carry the fade too.
"""
import json
import os
import sys

import numpy as np
import soundfile as sf
from scipy.ndimage import uniform_filter1d

HERE = os.path.dirname(os.path.abspath(__file__))
FILM = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(HERE, '..', '..', '..', 'pipeline', 'fostering'))
import audio as A  # noqa: E402

SR = A.SR
DUR = 36.5
N = int(DUR * SR)
T = np.arange(N) / SR
FADE_T0 = 35.6          # exponential end fade: 0 dB at 35.6 -> -30 dB at the last sample


def load(name):
    x = sf.read(os.path.join(HERE, name), dtype='float64')[0]
    x = A._st(x)
    return x[:N] if len(x) >= N else np.vstack([x, np.zeros((N - len(x), 2))])


def speech_lufs(x, vo):
    # loudness of x over the voiced parts only (where the VO stem is active)
    lvl = np.sqrt(np.convolve((vo[:, 0] ** 2), np.ones(2400) / 2400, 'same'))
    m = lvl > 10 ** (-45 / 20)
    return A.loudness(x[m].astype(np.float32))


def clip_gain(x, t0, t1, gain_db, ramp=0.04):
    # raised-cosine ramps centred on t0 / t1
    up = 0.5 - 0.5 * np.cos(np.pi * np.clip((T - (t0 - ramp / 2)) / ramp, 0, 1))
    dn = 0.5 + 0.5 * np.cos(np.pi * np.clip((T - (t1 - ramp / 2)) / ramp, 0, 1))
    return x * A.undb(gain_db * up * dn)[:, None]


def exciter(x, gain_db=-21.0, drive=2.0):
    """Stopgap air for the band-limited TTS: high-pass 3.5 kHz -> level-independent soft saturation, full-wave
    (even harmonics: 4-6 kHz -> 8-12 kHz) -> high-pass 7.5 kHz (8th order) -> gentle 13 kHz roll-off, mixed in low."""
    h = A.hp(x, 3500, 4)
    env = np.sqrt(np.maximum(uniform_filter1d(h ** 2, int(0.004 * SR), axis=0), 0)) + 1e-6
    s = np.abs(np.tanh(drive * h / env) / np.tanh(drive) * env)
    e = A.lp(A.hp(A.hp(s, 7500, 4), 7500, 4), 13000, 2)
    return x + e * A.undb(gain_db)


def vad_key():
    """0/1 voice-activity key from vo_words.json: each line from first word - 0.08 s to last word + 0.15 s (the last
    line is held to the end, so the duck never releases into the final chord), smoothed ~20 ms."""
    w = json.load(open(os.path.join(FILM, 'vo_words.json')))['words']
    lines = {}
    for x in w:
        a, b = lines.get(x['line'], (1e9, -1e9))
        lines[x['line']] = (min(a, x['s']), max(b, x['e']))
    spans = sorted(lines.values())
    k = np.zeros(N)
    for i, (a, b) in enumerate(spans):
        k[(T >= a - 0.08) & (T < (DUR if i == len(spans) - 1 else b + 0.15))] = 1.0
    k = uniform_filter1d(k, int(0.02 * SR))
    return k, spans


def end_fade():
    u = np.clip((T - FADE_T0) / (DUR - FADE_T0), 0, 1)
    return A.undb(-30.0 * u)[:, None]


def main():
    vo, music, sfx = load('vo.wav'), load('music.wav'), load('sfx.wav')
    vo = clip_gain(vo, 4.99, 5.40, 4.5)        # the cue word "open." sits ~6 LU under "door" / "won't"
    vo = exciter(vo)
    # tame the voice's peaks without changing its level
    vo = vo * A.limiter_gain(vo, ceiling_db=-3.0)[:, None]
    print(f'voice: {speech_lufs(vo, vo):.1f} LUFS over speech')
    key, spans = vad_key()
    music_d = A.sidechain(music, key, depth_db=12.0, attack=0.025, release=0.35, thresh_rel_db=-32)
    gm, gs = A.undb(0.5), A.undb(2.0)       # music bed about -17.5 LUFS, SFX about -19.5 LUFS before the master trim
    fade = end_fade()
    vo, music_d, sfx = vo * fade, music_d * fade, sfx * fade
    bus = vo + music_d * gm + sfx * gs
    novo = music * fade * gm * A.undb(2.0) + sfx * gs
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
        A._write_wav(os.path.join(HERE, name), y.astype(np.float32), bits=24)
        print(f'{name}: {A.loudness(y.astype(np.float32)):.2f} LUFS  TP {A.true_peak(y.astype(np.float32)):.2f} dBTP')
        if name == 'mix.wav':
            master = y
            trim = A.loudness(y.astype(np.float32)) - A.loudness(bus.astype(np.float32))
            trim_db = trim
            print(f'  music {20 * np.log10(gm):+.1f} dB, sfx {20 * np.log10(gs):+.1f} dB, final trim {trim:+.2f} dB'
                  f' -> voice ~{speech_lufs(vo * A.undb(trim), vo):.1f} LUFS over speech')
    # stems at the master's level: vo + music + sfx sum to mix.wav (before its peak limiter, which only touches peaks)
    k = A.undb(trim_db)
    stems = {'vo_stem.wav': vo * k, 'music_stem.wav': music_d * gm * k, 'sfx_stem.wav': sfx * gs * k}
    os.makedirs(os.path.join(HERE, 'stems'), exist_ok=True)
    for name, x in stems.items():
        A._write_wav(os.path.join(HERE, 'stems', name), x.astype(np.float32), bits=24)
    ssum = sum(sf.read(os.path.join(HERE, 'stems', n), dtype='float64')[0] for n in stems)
    l_sum, l_mix = A.loudness(ssum.astype(np.float32)), A.loudness(master.astype(np.float32))
    print(f'stem sum {l_sum:.2f} LUFS vs mix.wav {l_mix:.2f} LUFS ({l_sum - l_mix:+.2f} LU)')
    assert abs(l_sum - l_mix) <= 0.1, f'stems do not sum to the master: {l_sum:.2f} vs {l_mix:.2f} LUFS'
    print('-> audio/mix.wav, audio/mix_novo.wav, audio/stems/')


if __name__ == '__main__':
    main()
