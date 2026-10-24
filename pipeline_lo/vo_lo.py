"""Voiceover for "Leave the Light On": a calm, conversational read with natural pauses (Kokoro, local).

Each line is built from short phrases joined by hand-set pauses, so the rhythm breathes instead of running on.
Every phrase keeps its natural decay (low-threshold trim, generous tail) and gets a soft fade so no word is cut.
Voice: a warm British male blend (bm_george / bm_lewis / am_michael), phonemised as en-gb, slower than default.

Usage: python3 vo_su.py [speed]
"""
import os, sys, json
import numpy as np
import soundfile as sf
from kokoro_onnx import Kokoro

S = os.environ.get('REEL_WORKDIR', os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'workspace_lo')))
T = f'{S}/tts'
BLEND = (('bm_george', 0.55), ('bm_lewis', 0.25), ('am_michael', 0.2))   # warm, calm British male

# (phrase, pause after it in seconds). Concept script, phrased for the ear.
LINES = {
    'call': [('Sometimes a child needs somewhere safe…', 0.5), ('tonight.', 0.0)],
    'ready': [('Emergency foster carers', 0.14), ('get ready at short notice…', 0.0)],
    'never': [('and with advice outside normal hours,', 0.22), ("you're never on your own.", 0.0)],
    'cta': [('Could you leave the light on?', 0.45), ('Start the conversation with Organic Fostering.', 0.0)],
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
