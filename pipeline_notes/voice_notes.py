"""Lay the two ElevenLabs takes (caller = Kerry, team member = British Warm Friendly) onto the film's beats.
-> workspace_notes/tts/vo_caller.wav, vo_team.wav (film-length), info.json (words with speaker + film times, phone flag)
"""
import json, subprocess, os
import numpy as np
import soundfile as sf

S = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'workspace_notes', 'tts'))
SR = 44100
DUR = 34.0
FIX = {'inquiry': 'enquiry', 'organic': 'Organic', 'fostering.': 'Fostering.', 'Okay,': 'Okay.'}

# (speaker, take start, take end, film start, phone)   take times from whisper (+ small pads)
SEGS = [
    ('caller', 0.00, 3.95, 1.00, False),      # I'd typed the same question three times that week.
    ('caller', 4.78, 11.05, 6.60, False),     # Can I ask something? What happens ... with me?
    ('team', 0.00, 2.10, 13.35, True),        # You'll have a supervising social worker.
    ('team', 2.58, 7.35, 16.30, True),        # We can talk you through ... outside normal hours.  (longer pause before)
    ('caller', 11.22, 14.48, 21.75, False),   # Okay. Can I ask about training as well?
    ('team', 8.68, 14.40, 26.75, False),      # Start your enquiry with Organic Fostering. We'll talk ... obligation.
]


def rd(f):
    return np.frombuffer(subprocess.run(['ffmpeg', '-v', 'error', '-i', f, '-ac', '1', '-ar', str(SR), '-f', 'f32le', '-'],
                                        capture_output=True, check=True).stdout, np.float32)


takes = {'caller': rd(f'{S}/caller.mp3'), 'team': rd(f'{S}/team.mp3')}
words_t = {k: json.load(open(f'{S}/{k}_words.json')) for k in ('caller', 'team')}
outs = {k: np.zeros(int(DUR * SR), np.float32) for k in ('caller', 'team')}
words = []
for spk, a0, a1, f0, phone in SEGS:
    x = takes[spk][int(a0 * SR):int(a1 * SR)].copy()
    n = int(0.012 * SR)
    x[:n] *= np.linspace(0, 1, n)
    x[-n:] *= np.linspace(1, 0, n)
    i0 = int(f0 * SR)
    outs[spk][i0:i0 + len(x)] += x[:len(outs[spk]) - i0]
    for w, b, e in words_t[spk]:
        if b >= a0 - 0.02 and e <= a1 + 0.05:
            words.append([FIX.get(w, w), round(b - a0 + f0, 3), round(e - a0 + f0, 3), spk, phone])
for k, y in outs.items():
    sf.write(f'{S}/vo_{k}.wav', y, SR)
words.sort(key=lambda w: w[1])
words[0][0] = "I'd"
for i in range(1, len(words)):
    if words[i - 1][0] == 'Okay.' and words[i][0] == 'can':
        words[i][0] = 'Can'
json.dump({'words': words, 'segs': SEGS, 'dur': DUR}, open(f'{S}/info.json', 'w'), indent=0)
print(' '.join(f'{w[0]}@{w[1]:.2f}' for w in words))
