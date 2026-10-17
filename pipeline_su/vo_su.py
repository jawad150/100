"""Voiceover lines for "Support Update Available" (Kokoro, British female voice), with durations.

Usage: python3 vo_ff.py [voice] [speed]
"""
import os, sys, json
import numpy as np
import soundfile as sf
from kokoro_onnx import Kokoro

S = os.environ.get('REEL_WORKDIR', os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'workspace_su')))
T = f'{S}/tts'

# Condensed from the concept script to fit a 20 s cut: calm, warm, friendly.
LINES = [
    ('hook', 'Already a foster carer? Is your support up to date?'),
    ('check', 'Quick check. Do you have all of this?'),
    ('included', "At Organic Fostering, it's all included."),
    ('care', 'We focus on continuity of care for the children you look after.'),
    ('install', 'Explore a transfer, with no immediate commitment.'),
    ('cta', "Already fostering? Let's talk."),
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
