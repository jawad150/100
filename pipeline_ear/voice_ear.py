"""Fit the ElevenLabs takes into the reel's slots.
presenter.mp3 -> 'Assalamu alaikum, Manchester.' slot; narrator.mp3 (whole script, one take) is split by whisper into
its lines and each line placed at its slot start. Writes tts/vo_nar.wav, tts/vo_pres.wav, tts/info.json (word timings).
Missing narrator take -> only the presenter is written (preview).
"""
import os, sys, json, subprocess, re
import numpy as np
import soundfile as sf

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
S = os.path.abspath(os.path.join(HERE, '..', 'workspace_ear', 'tts'))
SR = 44100
DUR = 34.0
SLOTS = [(0.35, 'Manchester, can you name this place by ear?', 'nar'), (4.45, 'First clue.', 'nar'), (10.25, 'Second clue.', 'nar'),
         (16.2, 'Last one.', 'nar'), (18.75, 'Assalamu alaikum, Manchester.', 'pres'), (27.2, 'Three sounds. One address.', 'nar'),
         (29.35, 'The British Muslim Heritage Centre, Whalley Range.', 'nar')]


def rd(f):
    return np.frombuffer(subprocess.run(['ffmpeg', '-v', 'error', '-i', f, '-ac', '1', '-ar', str(SR), '-f', 'f32le', '-'],
                                        capture_output=True, check=True).stdout, np.float32)


def whisper(f):
    from faster_whisper import WhisperModel
    a = np.frombuffer(subprocess.run(['ffmpeg', '-v', 'error', '-i', f, '-ac', '1', '-ar', '16000', '-f', 'f32le', '-'],
                                     capture_output=True, check=True).stdout, np.float32)
    m = WhisperModel('small.en', device='cpu', compute_type='int8')
    return [(w.word.strip(), w.start, w.end) for s in m.transcribe(a, word_timestamps=True, beam_size=5)[0] for w in s.words]


def place(buf, x, t0):
    i = int(t0 * SR)
    n = min(len(x), len(buf) - i)
    buf[i:i + n] += x[:n]


words = []
# presenter
p = rd(f'{S}/presenter.mp3')
pw = whisper(f'{S}/presenter.mp3')
a0 = max(0, pw[0][1] - 0.05)
seg = p[int(a0 * SR):int((pw[-1][2] + 0.25) * SR)]
pres = np.zeros(int(DUR * SR), np.float32)
st = SLOTS[4][0]
place(pres, seg, st)
for (w, b, e), tw in zip(pw, SLOTS[4][1].split()):
    words.append([tw, round(st + b - a0, 3), round(st + e - a0, 3), 'pres'])
sf.write(f'{S}/vo_pres.wav', pres, SR)

nar_p = f'{S}/narrator.mp3'
if os.path.exists(nar_p):
    n = rd(nar_p)
    nw = whisper(nar_p)
    norm = lambda s: re.sub(r'[^a-z]', '', s.lower())
    nar = np.zeros(int(DUR * SR), np.float32)
    i = 0
    for st, text, spk in SLOTS:
        if spk != 'nar':
            continue
        target = text.split()
        seg_w = nw[i:i + len(target)]
        i += len(target)
        b0 = max(0, seg_w[0][1] - 0.05)
        b1 = seg_w[-1][2] + 0.18
        x = n[int(b0 * SR):int(b1 * SR)].copy()
        f = int(0.01 * SR)
        x[:f] *= np.linspace(0, 1, f)
        x[-f:] *= np.linspace(1, 0, f)
        place(nar, x, st)
        for (w, b, e), tw in zip(seg_w, target):
            words.append([tw, round(st + b - b0, 3), round(st + e - b0, 3), 'nar'])
    sf.write(f'{S}/vo_nar.wav', nar, SR)
    words.sort(key=lambda w: w[1])
    json.dump({'words': words}, open(f'{S}/info.json', 'w'), indent=0)
    print('narrator placed;', ' '.join(f'{w[0]}@{w[1]:.2f}' for w in words))
else:
    print('presenter placed; narrator take missing (preview)')
