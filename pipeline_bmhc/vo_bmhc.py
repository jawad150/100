"""Expressive voiceover for BMHC "The First Word" (people + heritage version), Kokoro local TTS.

Each phrase gets its own delivery: speed, and a pitch lift for smiling / rising moments (generated slower, then resampled
up, so the tempo stays right while the voice brightens). Phrases are split at every word that pops something on screen,
so the pop time is exactly the phrase onset.

Usage: python3 vo_sqe.py
"""
import os, json
import numpy as np
import soundfile as sf
from scipy import signal
from kokoro_onnx import Kokoro

S = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'workspace_bmhc'))
T = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'workspace_ic', 'tts'))
OUT = f'{S}/tts'
BLEND = (('am_michael', 0.45), ('bm_george', 0.35), ('am_fenrir', 0.2))      # warm, energetic male narrator

# line -> [(text, pause_after, speed, pitch)]   pitch > 1 = brighter / smiling / rising
LINES = {
    'l1': [('Every day,', 0.12, 1.0, 1.03), ('people walk through these gates,', 0.1, 1.02, 1.03), ('in Whalley Range.', 0.0, 1.0, 1.02)],
    'l2': [('Into a place of learning,', 0.1, 1.0, 1.03), ("that's stood since eighteen forty-three.", 0.0, 1.02, 1.03)],
    'l3': [("But here's a question.", 0.25, 1.0, 1.06), ('What was the very first word of the Koran,', 0.06, 1.0, 1.04),
           ('to be revealed?', 0.0, 0.97, 1.06)],
    'l4': [('Pray?', 0.12, 1.0, 1.06), ('Fast?', 0.12, 1.0, 1.06), ('Read?', 0.12, 1.0, 1.06), ('Give?', 0.3, 1.0, 1.06),
           ('Take a guess!', 1.1, 1.0, 1.08)],
    'l5': [('It was Iqraa.', 0.22, 0.92, 1.05), ('Read.', 0.3, 0.9, 1.03), ('Revealed to the Prophet Muhammad,', 0.05, 0.98, 1.02),
           ('peace be upon him.', 0.0, 0.94, 1.0)],
    'l6': [('Read!', 0.25, 0.86, 1.0), ('In the name of your Lord,', 0.15, 0.86, 1.0), ('who created.', 0.0, 0.84, 0.99)],
    'l7': [('Who taught,', 0.12, 0.88, 1.0), ('by means of the pen.', 0.0, 0.88, 1.01)],
    'l8': [('And that pen drew a line,', 0.1, 1.02, 1.04), ("through Baghdad's House of Wisdom,", 0.08, 1.03, 1.03),
           ('where al Kwaarizmee gave us algebra,', 0.06, 1.04, 1.04), ('and the algorithm!', 0.0, 1.02, 1.06)],
    'l9': [('To Fez,', 0.08, 1.0, 1.03), ('where Fatima al Fihri founded al Qarawiyeen,', 0.06, 1.03, 1.03),
           ('in eight fifty-nine.', 0.12, 1.0, 1.03), ("And it's still teaching today!", 0.0, 1.0, 1.07)],
    'l10': [('And to Manchester,', 0.06, 1.02, 1.04), ('eighteen forty-three,', 0.08, 1.02, 1.03),
            ('where this building opened as Lancashire Independent College.', 0.0, 1.05, 1.03)],
    'l11': [("Today, it's the British Muslim Heritage Centre.", 0.15, 1.02, 1.05), ('Koran classes,', 0.06, 1.06, 1.05),
            ('study circles,', 0.06, 1.06, 1.05), ('exhibitions,', 0.06, 1.06, 1.05), ('and youth clubs.', 0.15, 1.04, 1.06),
            ('Welcoming over a hundred and thirty thousand visitors a year!', 0.0, 1.04, 1.07)],
    'l12': [('It all began with one word.', 0.3, 0.96, 1.04), ('So,', 0.06, 1.0, 1.06), ('what will you read next?', 0.0, 0.98, 1.08)],
    'l13': [('Find a class at', 0.04, 1.0, 1.05), ('B M H C dot org dot UK.', 0.0, 0.96, 1.05)],
}


def tidy(a, sr):
    env = np.convolve(np.abs(a), np.ones(int(0.01 * sr)) / int(0.01 * sr), mode='same')
    nz = np.where(env > 0.004 * env.max())[0]
    a = a[max(0, nz[0] - int(0.03 * sr)): min(len(a), nz[-1] + int(0.2 * sr))]
    fi, fo = int(0.012 * sr), int(0.12 * sr)
    a[:fi] *= np.linspace(0, 1, fi)
    a[-fo:] *= np.linspace(1, 0, fo) ** 1.5
    return a


def brighten(a, sr, p):
    """Raise pitch by factor p (tempo compensated upstream) and add a touch of 'smile' presence."""
    if abs(p - 1) > 1e-3:
        up, down = 1000, int(round(1000 * p))
        a = signal.resample_poly(a, up, down)
    if p > 1.03:
        sos = signal.butter(2, [2500, 6000], 'band', fs=sr, output='sos')
        a = a + (p - 1) * 3.0 * signal.sosfilt(sos, a)
    return a.astype(np.float32)


if __name__ == '__main__':
    k = Kokoro(f'{T}/kokoro-v1.0.onnx', f'{T}/voices-v1.0.bin')
    style = sum(k.get_voice_style(v) * w for v, w in BLEND).astype(np.float32)
    os.makedirs(f'{OUT}/lines', exist_ok=True)
    info, phr = {}, {}
    for name, phrases in LINES.items():
        parts, t, ons = [], 0.0, []
        for text, pause, speed, pitch in phrases:
            a, sr = k.create(text, voice=style, speed=speed * 1.06 / pitch, lang='en-gb', trim=False)
            a = tidy(brighten(np.asarray(a, np.float32), sr, pitch), sr)
            ons.append((round(t + 0.03, 3), round(len(a) / sr, 3), text))
            parts.append(a)
            t += len(a) / sr
            if pause:
                parts.append(np.zeros(int(pause * sr), np.float32))
                t += pause
        line = np.concatenate(parts)
        line = line / max(1e-6, np.abs(line).max()) * 0.9
        sf.write(f'{OUT}/lines/{name}.wav', line, sr)
        info[name] = round(len(line) / sr, 3)
        phr[name] = ons
        print(f'{name} {info[name]:5.2f}s  ' + ' / '.join(p[0] for p in phrases))
    json.dump({'blend': BLEND, 'dur': info, 'phrases': phr}, open(f'{OUT}/lines/info.json', 'w'), indent=1)
    print('total', round(sum(info.values()), 2))
