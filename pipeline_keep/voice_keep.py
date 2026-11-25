"""Place the voice lines (owner = en-GB Sonia, interviewer = en-GB Thomas; free neural TTS while ElevenLabs is at its
limit) into the film's slots, trimming silence; word timings from whisper for the subtitles.
-> workspace_keep/tts/vo.wav + info.json"""
import os, json, subprocess
import numpy as np
import soundfile as sf
S = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'workspace_keep', 'tts'))
SR, DUR = 44100, 33.0
SLOTS = [('o1', 0.5, 'own', 'That last line has nothing to do with cooking.'),
         ('q1', 3.45, 'int', 'Who gave you this?'),
         ('o2', 5.15, 'own', 'My nani. She wrote it out for me, the week I left home.'),
         ('q2', 9.55, 'int', 'What do you remember about her, when you look at it?'),
         ('o3', 12.95, 'own', 'Her kitchen always smelled of cardamom.'),
         ('o4', 15.75, 'own', 'She never measured anything... so she drew little spoons instead.'),
         ('o5', 20.6, 'own', 'And always make enough... for one more.'),
         ('o6', 24.7, 'own', 'That was her.')]


def rd(f):
    return np.frombuffer(subprocess.run(['ffmpeg', '-v', 'error', '-i', f, '-ac', '1', '-ar', str(SR), '-f', 'f32le', '-'],
                                        capture_output=True, check=True).stdout, np.float32)


def trim(x, thr=0.01):
    env = np.convolve(np.abs(x), np.ones(441) / 441, mode='same')
    idx = np.where(env > thr)[0]
    a, b = max(0, idx[0] - 600), min(len(x), idx[-1] + 2200)
    return x[a:b]


from faster_whisper import WhisperModel
M = WhisperModel('small.en', device='cpu', compute_type='int8')
vo = np.zeros(int(DUR * SR), np.float32)
words = []
for name, st, spk, text in SLOTS:
    x = trim(rd(f'{S}/{name}.mp3'))
    i = int(st * SR)
    vo[i:i + len(x)] += x[:len(vo) - i]
    import scipy.signal as sg
    a16 = sg.resample_poly(x, 16000, SR).astype(np.float32)
    ws = [(w.word.strip(), w.start, w.end) for s_ in M.transcribe(a16, word_timestamps=True)[0] for w in s_.words]
    tw = text.replace('...', '…').split()
    for (w, b, e), t_ in zip(ws, tw):
        words.append([t_, round(st + b, 3), round(st + e, 3), spk])
    print(name, round(st, 2), '->', round(st + len(x) / SR, 2))
sf.write(f'{S}/vo.wav', vo, SR)
json.dump({'words': words, 'slots': SLOTS}, open(f'{S}/info.json', 'w'), indent=0)
