import json, os, sys
from faster_whisper import WhisperModel
import soundfile as sf, numpy as np
from math import gcd
from scipy.signal import resample_poly
def load16(fn):
    x, sr = sf.read(fn, dtype='float32')
    if x.ndim > 1: x = x.mean(1)
    g = gcd(16000, sr); return resample_poly(x, 16000 // g, sr // g).astype(np.float32)
B = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
m = WhisperModel('base.en', device='cpu', compute_type='int8')
lines = json.load(open(os.path.join(B, 'audio', 'vo', 'lines.json')))
for key, L in lines.items():
    segs, _ = m.transcribe(load16(os.path.join(B, 'audio', 'vo', f'{key}.wav')), language='en', word_timestamps=True, beam_size=5)
    words = [{'w': w.word.strip(), 's': round(w.start, 3), 'e': round(w.end, 3)} for s in segs for w in s.words]
    L['asr'] = words
    print(key, '|', L['text'], '\n    ->', ' '.join(w['w'] for w in words))
json.dump(lines, open(os.path.join(B, 'audio', 'vo', 'lines.json'), 'w'), indent=1)
