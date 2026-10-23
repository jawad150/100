"""Voiceover for "Three CV Mistakes (IC London)": a calm, conversational read with natural pauses (Kokoro, local).

Each line is built from short phrases joined by hand-set pauses, so the rhythm breathes instead of running on.
Every phrase keeps its natural decay (low-threshold trim, generous tail) and gets a soft fade so no word is cut.
Voice: a blend of af_heart (warm, gentle) and bf_emma (British), phonemised as en-gb, slightly slower than default.

Usage: python3 vo_su.py [speed]
"""
import os, sys, json
import numpy as np
import soundfile as sf
from kokoro_onnx import Kokoro

S = os.environ.get('REEL_WORKDIR', os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'workspace_cv')))
T = f'{S}/tts'
BLEND = (('af_heart', 0.6), ('bf_emma', 0.4))

# (phrase, pause after it in seconds). Advice grounded in the National Careers Service and Prospects CV guides.
LINES = {
    'hook': [('Your CV might be holding you back.', 0.0)],
    'intro': [('Here are three common mistakes', 0.08), ('that could cost you an interview.', 0.0)],
    'm1': [('One. Vague achievements.', 0.4), ("Don't just list duties,", 0.14), ('show what you did, with real examples.', 0.0)],
    'm2': [('Two. Irrelevant information.', 0.4), ("Tailor every line to the job you're applying for.", 0.0)],
    'm3': [('Three. Poor formatting.', 0.4), ('Use clear headings, bullet points,', 0.14), ('and one consistent style.', 0.0)],
    'cta': [('Make your next application count.', 0.0)],                 # CTA exactly as briefed
}


def tidy(a, sr):
    """Trim only true silence (keeps breaths and word decays), then fade the edges softly."""
    env = np.convolve(np.abs(a), np.ones(int(0.01 * sr)) / int(0.01 * sr), mode='same')
    nz = np.where(env > 0.004 * env.max())[0]
    a = a[max(0, nz[0] - int(0.03 * sr)): min(len(a), nz[-1] + int(0.22 * sr))]
    fi, fo = int(0.012 * sr), int(0.14 * sr)
    a[:fi] *= np.linspace(0, 1, fi)
    a[-fo:] *= np.linspace(1, 0, fo) ** 1.5
    return a


if __name__ == '__main__':
    speed = float(sys.argv[1]) if len(sys.argv) > 1 else 0.95
    k = Kokoro(f'{T}/kokoro-v1.0.onnx', f'{T}/voices-v1.0.bin')
    style = sum(k.get_voice_style(v) * w for v, w in BLEND).astype(np.float32)
    os.makedirs(f'{T}/lines', exist_ok=True)
    info = {}
    for name, phrases in LINES.items():
        parts = []
        for text, pause in phrases:
            a, sr = k.create(text, voice=style, speed=speed, lang='en-gb', trim=False)
            parts.append(tidy(np.asarray(a, np.float32), sr))
            if pause:
                parts.append(np.zeros(int(pause * sr), np.float32))
        line = np.concatenate(parts)
        line = line / max(1e-6, np.abs(line).max()) * 0.9
        sf.write(f'{T}/lines/{name}.wav', line, sr)
        info[name] = round(len(line) / sr, 3)
        print(f'{name:9s} {info[name]:5.2f}s  ' + ' / '.join(p for p, _ in phrases))
    json.dump({'blend': BLEND, 'speed': speed, 'sr': sr, 'dur': info}, open(f'{T}/lines/info.json', 'w'), indent=1)
    print('total', round(sum(info.values()), 2))
