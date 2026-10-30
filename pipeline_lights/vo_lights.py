"""Expressive voiceover for BMHC "Lights On" (people version), Kokoro local TTS.

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

S = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'workspace_lights'))
T = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'workspace_ic', 'tts'))
OUT = f'{S}/tts'
BLEND = (('am_michael', 0.45), ('bm_george', 0.35), ('am_fenrir', 0.2))      # warm, energetic male narrator

# line -> [(text, pause_after, speed, pitch)]   pitch > 1 = brighter / smiling / rising
LINES = {
    'l1': [('Every day,', 0.12, 1.0, 1.04), ('people walk through these gates.', 0.0, 1.0, 1.03)],
    'l2': [('This building went up in eighteen forty-three,', 0.08, 1.0, 1.03), ('as a college.', 0.0, 0.97, 1.03)],
    'l3': [("Today, it's still a place of learning!", 0.0, 0.98, 1.07)],
    'l4': [('Before sunrise,', 0.1, 0.94, 1.0), ('the first lights come on for Fajr.', 0.0, 0.94, 1.01)],
    'l5': [('Then the classrooms,', 0.06, 1.02, 1.04), ('for Koran classes,', 0.05, 1.02, 1.04), ('and G C S E Islamic Studies.', 0.0, 1.02, 1.04)],
    'l6': [('The sports hall,', 0.06, 1.04, 1.05), ('for taekwondo!', 0.0, 1.0, 1.08)],
    'l7': [('The studio,', 0.06, 1.02, 1.04), ('where Heritage Radio broadcasts,', 0.04, 1.03, 1.04), ('twenty-four hours a day.', 0.0, 1.0, 1.05)],
    'l8': [('The youth club.', 0.12, 1.02, 1.07), ('The scouts.', 0.0, 1.0, 1.08)],
    'l9': [('Open days, for neighbours of every faith,', 0.08, 1.0, 1.05), ('and none.', 0.0, 0.96, 1.05)],
    'l10': [('And every Friday,', 0.06, 0.98, 1.03), ('a khutbah in English.', 0.0, 0.96, 1.03)],
    'l11': [('Your donations help the Centre carry on,', 0.06, 0.98, 1.03), ('all of it.', 0.0, 0.94, 1.04)],
    'l12': [('Help keep the lights on.', 0.0, 0.94, 1.06)],
    'l13': [('Become a Friend of the Centre.', 0.0, 0.94, 1.07)],
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
