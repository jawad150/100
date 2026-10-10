"""Generate the voiceover lines with Kokoro (local, British female voice) and report durations.

Usage: python3 vo_of.py [voice] [speed]
"""
import os, sys, json
import numpy as np
import soundfile as sf
from kokoro_onnx import Kokoro

S = os.environ.get('REEL_WORKDIR', os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'workspace_of')))
T = f'{S}/tts'

# Brand voice: calm, plain, kind. One idea per line. British English, no exclamation marks.
LINES = [
    ('hook', 'Where does a fostering allowance really go?'),
    ('money', 'From four hundred and forty-seven pounds sixty a week, for each child.'),
    ('big', "Sometimes, it's not the big things."),
    ('day', "It's school shoes by the door. A bag packed for the day."),
    ('breakfast', "It's breakfast at the table."),
    ('night', 'A goodnight at bedtime.'),
    ('asking', 'Someone asking, how was your day?'),
    ('message', 'Sometimes, ordinary moments help create extraordinary change.'),
    ('end', 'Organic Fostering. Room to grow, roots to keep.'),
]

if __name__ == '__main__':
    voice = sys.argv[1] if len(sys.argv) > 1 else 'bf_emma'
    speed = float(sys.argv[2]) if len(sys.argv) > 2 else 0.92
    k = Kokoro(f'{T}/kokoro-v1.0.onnx', f'{T}/voices-v1.0.bin')
    os.makedirs(f'{T}/lines', exist_ok=True)
    info = {}
    for name, text in LINES:
        audio, sr = k.create(text, voice=voice, speed=speed, lang='en-gb')
        audio = np.asarray(audio, np.float32)
        # trim leading/trailing silence
        thr = 0.01 * np.abs(audio).max()
        nz = np.where(np.abs(audio) > thr)[0]
        audio = audio[max(0, nz[0] - int(0.02 * sr)): nz[-1] + int(0.08 * sr)]
        sf.write(f'{T}/lines/{name}.wav', audio, sr)
        info[name] = round(len(audio) / sr, 3)
        print(f'{name:10s} {info[name]:5.2f}s  {text}')
    json.dump({'voice': voice, 'speed': speed, 'sr': sr, 'dur': info}, open(f'{T}/lines/info.json', 'w'), indent=1)
    print('total speech', round(sum(info.values()), 2))
