"""Voiceover for IC London "Why do you want to be a solicitor?": a clear, neat, professional British male read
(Kokoro, local). Lines are built from short phrases with hand-set pauses; each phrase keeps its natural decay and gets
a soft fade so no word is cut.

Usage: python3 vo_sol.py [speed]
"""
import os, sys, json
import numpy as np
import soundfile as sf
from kokoro_onnx import Kokoro

S = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'workspace_sol'))
T = f'{S}/tts'
BLEND = (('bm_george', 0.7), ('bm_daniel', 0.3))      # clear, neutral British male

LINES = {
    'hook': [('Why do you want to be a solicitor?', 0.4), ("Don't just say you love law.", 0.0)],
    'generic': [("It's too generic,", 0.12), ("and it won't stand out.", 0.0)],
    'three': [('Instead, build your answer on three key things.', 0.0)],
    'motiv': [('One.', 0.05), ('Your motivation.', 0.22), ("Explain what really drives you.", 0.0)],
    'exp': [('Two.', 0.05), ('Relevant experience.', 0.22), ('Link your skills, studies or work experience', 0.05),
            ("to what you've learned.", 0.0)],
    'goals': [('Three.', 0.05), ('Your long-term goals.', 0.22), ('Show how becoming a solicitor', 0.04),
              ('fits into your future.', 0.0)],
    'cta': [('Connect all three,', 0.16), ('and prepare with purpose.', 0.0)],
}


def tidy(a, sr):
    env = np.convolve(np.abs(a), np.ones(int(0.01 * sr)) / int(0.01 * sr), mode='same')
    nz = np.where(env > 0.004 * env.max())[0]
    a = a[max(0, nz[0] - int(0.03 * sr)): min(len(a), nz[-1] + int(0.22 * sr))]
    fi, fo = int(0.012 * sr), int(0.14 * sr)
    a[:fi] *= np.linspace(0, 1, fi)
    a[-fo:] *= np.linspace(1, 0, fo) ** 1.5
    return a


if __name__ == '__main__':
    speed = float(sys.argv[1]) if len(sys.argv) > 1 else 1.0
    k = Kokoro(f'{T}/kokoro-v1.0.onnx', f'{T}/voices-v1.0.bin')
    style = sum(k.get_voice_style(v) * w for v, w in BLEND).astype(np.float32)
    os.makedirs(f'{T}/lines', exist_ok=True)
    info, phr = {}, {}
    for name, phrases in LINES.items():
        parts, t, ons = [], 0.0, []
        for text, pause in phrases:
            a, sr = k.create(text, voice=style, speed=speed, lang='en-gb', trim=False)
            a = tidy(np.asarray(a, np.float32), sr)
            ons.append((round(t + 0.03, 3), text))
            parts.append(a)
            t += len(a) / sr
            if pause:
                parts.append(np.zeros(int(pause * sr), np.float32))
                t += pause
        line = np.concatenate(parts)
        line = line / max(1e-6, np.abs(line).max()) * 0.9
        sf.write(f'{T}/lines/{name}.wav', line, sr)
        info[name] = round(len(line) / sr, 3)
        phr[name] = ons
        print(f'{name:8s} {info[name]:5.2f}s  ' + ' / '.join(p for p, _ in phrases))
    json.dump({'blend': BLEND, 'speed': speed, 'sr': sr, 'dur': info, 'phrases': phr},
              open(f'{T}/lines/info.json', 'w'), indent=1)
    print('total', round(sum(info.values()), 2))
