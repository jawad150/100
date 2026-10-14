"""Voiceover lines for "The Fostering Flow" (Kokoro, British female voice), with durations.

Usage: python3 vo_ff.py [voice] [speed]
"""
import os, sys, json
import numpy as np
import soundfile as sf
from kokoro_onnx import Kokoro

S = os.environ.get('REEL_WORKDIR', os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'workspace_ff')))
T = f'{S}/tts'

# Script from the concept doc (about 70 words): calm, warm, friendly.
LINES = [
    ('hook', "Thinking about fostering? Here's the whole journey, in thirty seconds."),
    ('flow', "Five steps, and we're with you on every one."),
    ('chat', 'It starts with an informal chat.'),
    ('visit', 'Then we visit you at home.'),
    ('train', 'You apply, and we train you.'),
    ('assess', 'Your assessment is about getting to know you.'),
    ('panel', 'Then panel, and approval.'),
    ('support', "And once you're approved, the support keeps going."),
    ('cta', 'Step one is just a conversation. Start yours with Organic Fostering.'),
]

if __name__ == '__main__':
    voice = sys.argv[1] if len(sys.argv) > 1 else 'bf_emma'
    speed = float(sys.argv[2]) if len(sys.argv) > 2 else 1.0
    k = Kokoro(f'{T}/kokoro-v1.0.onnx', f'{T}/voices-v1.0.bin')
    os.makedirs(f'{T}/lines', exist_ok=True)
    info = {}
    for name, text in LINES:
        audio, sr = k.create(text, voice=voice, speed=speed, lang='en-gb')
        audio = np.asarray(audio, np.float32)
        thr = 0.01 * np.abs(audio).max()
        nz = np.where(np.abs(audio) > thr)[0]
        audio = audio[max(0, nz[0] - int(0.02 * sr)): nz[-1] + int(0.08 * sr)]
        sf.write(f'{T}/lines/{name}.wav', audio, sr)
        info[name] = round(len(audio) / sr, 3)
        print(f'{name:8s} {info[name]:5.2f}s  {text}')
    json.dump({'voice': voice, 'speed': speed, 'sr': sr, 'dur': info}, open(f'{T}/lines/info.json', 'w'), indent=1)
    print('total speech', round(sum(info.values()), 2))
