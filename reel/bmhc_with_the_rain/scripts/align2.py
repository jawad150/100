"""Word timings for the guide VO: faster-whisper ASR, mapped onto the script words."""
import json, os
from faster_whisper import WhisperModel
import soundfile as sf, numpy as np
from math import gcd
from scipy.signal import resample_poly
B = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
def load16(fn):
    x, sr = sf.read(fn, dtype='float32')
    if x.ndim > 1: x = x.mean(1)
    g = gcd(16000, sr); return resample_poly(x, 16000 // g, sr // g).astype(np.float32)
DISPLAY = {'L9': "Imam Counselling at BMHC."}
m = WhisperModel('small.en', device='cpu', compute_type='int8')
lines = json.load(open(os.path.join(B, 'audio', 'vo', 'lines.json')))
for key, L in lines.items():
    segs, _ = m.transcribe(load16(os.path.join(B, 'audio', 'vo', f'{key}.wav')), language='en', word_timestamps=True, beam_size=5)
    asr = [{'w': w.word.strip(), 's': round(w.start, 3), 'e': round(w.end, 3)} for s in segs for w in s.words]
    L['asr'] = asr
    script = DISPLAY.get(key, L['text']).split()
    if key == 'L9':
        # "B. M. H. C." is read as letters: BMHC starts at the first letter after "at"
        i = next(j for j, w in enumerate(asr) if w['w'].lower().strip('.,') == 'at')
        st = [asr[0]['s'], asr[1]['s'], asr[i]['s'], asr[i + 1]['s'] if i + 1 < len(asr) else asr[i]['e']]
        mode = 'letters'
    elif len(asr) == len(script):
        st = [w['s'] for w in asr]; mode = 'exact'
    else:
        # proportional by character count across the voiced span
        a0, a1 = asr[0]['s'], asr[-1]['e']
        c = np.cumsum([0] + [len(w) + 1 for w in script]); st = list(a0 + (a1 - a0) * c[:-1] / c[-1]); mode = 'prop'
    L['words'] = [{'w': w, 's': round(float(s), 3)} for w, s in zip(script, st)]
    print(key, mode, '|', ' '.join(f"{w['w']}@{w['s']}" for w in L['words']))
    if mode != 'exact': print('    asr:', ' '.join(w['w'] for w in asr))
json.dump(lines, open(os.path.join(B, 'audio', 'vo', 'lines.json'), 'w'), indent=1)
