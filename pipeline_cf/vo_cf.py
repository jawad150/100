"""Expressive voiceover for Organic Fostering "Can I Foster If…?" v2 (PDF script, word for word), Kokoro local TTS.

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

S = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'workspace_cf'))
T = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'workspace_ic', 'tts'))
OUT = f'{S}/tts'
BLEND = (('bm_george', 0.55), ('bm_lewis', 0.25), ('am_michael', 0.2))   # the same warm British narrator as earlier OF reels

# line -> [(text, pause_after, speed, pitch)]   pitch > 1 = brighter / smiling / rising
LINES = {
    'l1': [('Thinking about fostering?', 0.3, 1.0, 1.05), ("You've probably wondered:", 0.18, 1.0, 1.03),
           ('can I foster if...', 0.0, 0.94, 1.04)],
    'l2': [('Here are the honest answers.', 0.0, 1.0, 1.05)],
    'l3': [('Pets?', 0.16, 1.0, 1.06), ('Usually.', 0.2, 0.96, 1.05), ("They're assessed for temperament", 0.04, 1.02, 1.03),
           ('and safety.', 0.0, 1.0, 1.03)],
    'l4': [('Retired?', 0.16, 1.0, 1.06), ('Yes!', 0.2, 0.96, 1.08), ("There's no fixed upper age limit.", 0.0, 1.02, 1.05)],
    'l5': [('Already have children?', 0.16, 1.0, 1.05), ('Yes!', 0.2, 0.96, 1.08),
           ('Their views are part of the assessment.', 0.0, 1.02, 1.04)],
    'l6': [('Working?', 0.16, 1.0, 1.05), ('Possibly.', 0.22, 0.95, 1.03), ('It depends on your hours,', 0.05, 1.02, 1.03),
           ('flexibility', 0.05, 1.02, 1.03), ('and support.', 0.0, 1.0, 1.03)],
    'l7': [('A health condition?', 0.18, 1.0, 1.04), ("It doesn't automatically rule you out.", 0.0, 0.98, 1.05)],
    'l8': [("Your question's not on the list?", 0.25, 1.0, 1.05), ('Your circumstances deserve a conversation.', 0.0, 0.96, 1.05)],
    'l9': [('Send your question', 0.04, 1.0, 1.06), ('to a real person', 0.03, 1.0, 1.05), ('in our Manchester team.', 0.25, 1.0, 1.05),
           ('No pressure,', 0.08, 0.96, 1.04), ('no obligation.', 0.0, 0.95, 1.04)],
    'l10': [('Organic Fostering.', 0.0, 0.95, 1.05)],
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
