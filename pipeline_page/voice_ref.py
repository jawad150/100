"""Narration for the reference-style OF reel ("It lives in the small things"): edge-tts en-GB Ryan, one file per line,
silences trimmed and re-spaced like the reference's pacing -> workspace_page/tts2/vo.wav + info.json (lines + words)."""
import os, json, subprocess
import numpy as np
import soundfile as sf

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
T = f'{ROOT}/workspace_page/tts2'
SR = 48000
GAPS = [0.12, 0.45, 0.45, 0.5, 0.42, 0.65, 0.35, 0.35, 0.5, 0.12, 0.42, 0.6, 0.85, 0.0]   # pause after each line
START = 0.55


def load(p):
    return np.frombuffer(subprocess.run(['ffmpeg', '-v', 'error', '-i', p, '-ac', '1', '-ar', str(SR), '-f', 'f32le', '-'],
                                        capture_output=True, check=True).stdout, np.float32)


def trim(x, thr=0.008):
    idx = np.where(np.abs(x) > thr)[0]
    a, b = max(0, idx[0] - int(0.02 * SR)), min(len(x), idx[-1] + int(0.06 * SR))
    return x[a:b]


if __name__ == '__main__':
    from faster_whisper import WhisperModel
    m = WhisperModel('small.en', device='cpu', compute_type='int8')
    clips = [trim(load(f'{T}/l{i}.mp3')) for i in range(1, 15)]
    total = START + sum(len(c) / SR for c in clips) + sum(GAPS)
    out = np.zeros(int((total + 3.5) * SR), np.float32)
    t = START
    lines, words = [], []
    texts = [l.strip() for l in open(f'{T}/script.txt')]
    for i, c in enumerate(clips):
        i0 = int(t * SR)
        out[i0:i0 + len(c)] += c
        a16 = c[::3].copy()
        segs, _ = m.transcribe(a16, word_timestamps=True, beam_size=5)
        ws = [(w.word.strip(), round(w.start + t, 3), round(w.end + t, 3), i) for s in segs for w in s.words]
        words += ws
        lines.append((i, round(t, 3), round(t + len(c) / SR, 3), texts[i]))
        print(i + 1, f'{t:.2f}-{t + len(c) / SR:.2f}', ' '.join(f'{w}@{a:.2f}' for w, a, b, _ in ws))
        t += len(c) / SR + GAPS[i]
    sf.write(f'{T}/vo.wav', out, SR)
    json.dump({'lines': lines, 'words': words, 'dur': round(len(out) / SR, 2)}, open(f'{T}/info.json', 'w'), indent=1)
    print('dur', len(out) / SR)
