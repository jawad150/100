"""Dialogue for OF "Can I add a page?" -> workspace_page/tts/vo.wav + info.json (words with absolute times, speaker).
Voices: free Microsoft neural voices via edge-tts (ElevenLabs is at its monthly limit): young person = Thomas (lifted),
carer = Libby. Lines are placed on the brief's timeline; word times come from faster-whisper per line.
"""
import os, json, subprocess, sys
import numpy as np
import soundfile as sf

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
T = f'{ROOT}/workspace_page/tts'
SR = 48000
# line id, speaker, start (s), text
LINES = [('yp1', 'yp', 0.55, 'Can I put something on this page?'),
         ('c1', 'carer', 4.25, 'Course. We made this so you could get to know us.'),
         ('yp2', 'yp', 10.55, 'I watch City with my brother. We always text when they score.'),
         ('c2', 'carer', 18.45, "What time's kick-off?"),
         ('yp3', 'yp', 21.35, "Three. I've already checked.")]
DUR = 34.0


def load(path):
    x = np.frombuffer(subprocess.run(['ffmpeg', '-v', 'error', '-i', path, '-ac', '1', '-ar', str(SR), '-f', 'f32le', '-'],
                                     capture_output=True, check=True).stdout, np.float32)
    return x


def lead(x, thr=0.01):
    i = np.argmax(np.abs(x) > thr)
    return i / SR


if __name__ == '__main__':
    from faster_whisper import WhisperModel
    m = WhisperModel('small.en', device='cpu', compute_type='int8')
    out = np.zeros(int(DUR * SR), np.float32)
    words, lines = [], []
    for lid, spk, t0, txt in LINES:
        x = load(f'{T}/{lid}.mp3')
        ld = lead(x)
        x = x[max(0, int((ld - 0.03) * SR)):]
        i0 = int(t0 * SR)
        out[i0:i0 + len(x)] += x[:len(out) - i0]
        a16 = np.frombuffer(subprocess.run(['ffmpeg', '-v', 'error', '-i', f'{T}/{lid}.mp3', '-ac', '1', '-ar', '16000', '-f', 'f32le', '-'],
                                           capture_output=True).stdout, np.float32)
        segs, _ = m.transcribe(a16, word_timestamps=True, beam_size=5)
        off = t0 - (ld - 0.03)
        ws = [(w.word.strip(), round(w.start + off, 3), round(w.end + off, 3), spk) for s in segs for w in s.words]
        words += ws
        lines.append((lid, spk, t0, round(t0 + len(x) / SR, 3), txt))
        print(lid, ' '.join(f'{w}@{a:.2f}' for w, a, b, _ in ws))
    sf.write(f'{T}/vo.wav', out, SR)
    json.dump({'words': words, 'lines': lines}, open(f'{T}/info.json', 'w'), indent=1)
    print('vo written')
