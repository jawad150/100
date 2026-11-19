"""Voice timing for BMHC "AI can recreate this building".

The brief's script, line by line. Until the ElevenLabs take exists, `plan` writes an estimated word timeline (marked
placeholder) so the film can be built; `real <take.mp3>` replaces it with whisper word timings of the real voice,
re-spacing the lines onto the film's beats by cutting/adding silence between them -> workspace_ai/tts/vo.wav + info.json.
"""
import os, sys, json, re
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
S = os.path.abspath(os.path.join(HERE, '..', 'workspace_ai'))
os.makedirs(f'{S}/tts', exist_ok=True)

LINES = [  # (text, earliest start in the film, seconds of air after it)
    ("AI can recreate a building in seconds.", 0.9, 0.5),
    ("Every window.", 0.0, 0.3),
    ("Every brick.", 0.0, 0.3),
    ("Every detail.", 0.0, 0.7),
    ("But it can't recreate what happens inside.", 0.0, 1.15),
    ("The friendships formed.", 0.0, 0.5),
    ("The knowledge passed on.", 0.0, 0.5),
    ("The young people finding their confidence.", 0.0, 0.55),
    ("The conversations that bring communities together.", 0.0, 0.85),
    ("Because heritage isn't only what we preserve.", 0.0, 0.45),
    ("It's what we keep alive.", 0.0, 1.0),
    ("British Muslim Heritage Centre.", 0.0, 0.45),
    ("More than a building.", 0.0, 0.35),
    ("A living community.", 0.0, 0.75),
    ("Come and experience it.", 0.0, 0.0),
]


def syl(w):
    w = re.sub(r'[^a-z]', '', w.lower())
    return max(1, len(re.findall(r'[aeiouy]+', w)) - (1 if w.endswith('e') and len(w) > 3 else 0))


def plan():
    t = 0.0
    words = []
    for text, start, gap in LINES:
        t = max(t, start)
        for w in text.split():
            d = 0.12 + 0.115 * syl(w)
            words.append([w, round(t, 3), round(t + d, 3)])
            t += d + 0.03
        t += gap
    json.dump({'placeholder': True, 'words': words, 'dur': t}, open(f'{S}/tts/info.json', 'w'), indent=0)
    print('placeholder timeline, voice ends at', round(t, 2))


def norm(w):
    return re.sub(r"[^a-z']", '', w.lower().replace('’', "'"))


def real(take):
    """Whisper the take, find each script line in it, and lay the lines out with the planned air between them."""
    import subprocess
    import soundfile as sf
    from faster_whisper import WhisperModel
    sr = 44100
    a = np.frombuffer(subprocess.run(['ffmpeg', '-v', 'error', '-i', take, '-ac', '1', '-ar', str(sr), '-f', 'f32le', '-'],
                                     capture_output=True, check=True).stdout, np.float32)
    a16 = np.frombuffer(subprocess.run(['ffmpeg', '-v', 'error', '-i', take, '-ac', '1', '-ar', '16000', '-f', 'f32le', '-'],
                                       capture_output=True, check=True).stdout, np.float32)
    m = WhisperModel('small.en', device='cpu', compute_type='int8')
    segs, _ = m.transcribe(a16, word_timestamps=True, beam_size=5)
    ws = [(w.word.strip(), w.start, w.end) for s_ in segs for w in s_.words]
    print(' '.join(f'{w}@{b:.2f}' for w, b, e in ws))
    # walk the script and match words in order (whisper may merge/split; match on normalised text)
    i = 0
    out_audio = []
    words = []
    t = 0.0
    for text, start, gap in LINES:
        target = [norm(x) for x in text.split()]
        n = len(target)
        # find the best start index j >= i
        best, bj = -1, i
        for j in range(i, min(len(ws), i + 40)):
            sc = sum(1 for k in range(n) if j + k < len(ws) and norm(ws[j + k][0]) == target[k])
            if sc > best:
                best, bj = sc, j
        seg = ws[bj:bj + n]
        i = bj + n
        a0 = max(0.0, seg[0][1] - 0.06)
        a1 = seg[-1][2] + 0.12
        t = max(t, start)
        if out_audio:
            pass
        lead = t - (sum(len(x) for x in out_audio) / sr)
        if lead > 0:
            out_audio.append(np.zeros(int(lead * sr), np.float32))
        clip = a[int(a0 * sr):int(a1 * sr)].copy()
        f = int(0.01 * sr)
        clip[:f] *= np.linspace(0, 1, f)
        clip[-f:] *= np.linspace(1, 0, f)
        base = sum(len(x) for x in out_audio) / sr
        for (w, b, e), tw in zip(seg, text.split()):
            words.append([tw, round(base + b - a0, 3), round(base + e - a0, 3)])
        out_audio.append(clip)
        t = base + (a1 - a0) + gap
    y = np.concatenate(out_audio)
    sf.write(f'{S}/tts/vo.wav', y, sr)
    json.dump({'placeholder': False, 'words': words, 'dur': len(y) / sr}, open(f'{S}/tts/info.json', 'w'), indent=0)
    print('vo.wav', round(len(y) / sr, 2), 's')


if __name__ == '__main__':
    if sys.argv[1] == 'plan':
        plan()
    else:
        real(sys.argv[2])
