"""Voiceover prep: decode the ElevenLabs takes (workspace/tts/*.mp3), tighten long pauses,
polish (HPF, presence, gentle compression) and write workspace/tts/clean/<name>.wav (48 kHz mono)
plus workspace/tts/clean/segs.json with the speech segments (seconds, in the cleaned file).

python3 vo.py
"""
import os, glob, json, subprocess
import numpy as np
from scipy import signal

S = os.environ.get('REEL_WORKDIR', os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'workspace')))
SR = 48000
# max pause kept inside a line (s); per-line overrides for deliberate dramatic pauses
MAX_PAUSE = 0.26
KEEP = {'r1_1': 0.42, 'r3_0': 0.55, 'r2_0': 0.30}


def load(f):
    raw = subprocess.run(['ffmpeg', '-loglevel', 'error', '-i', f, '-ac', '1', '-ar', str(SR), '-f', 'f32le', '-'],
                         capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.float32).astype(np.float64)


def envelope(x, win=0.01):
    n = int(win * SR)
    return np.sqrt(np.convolve(x ** 2, np.ones(n) / n, 'same'))


def segments(x, gap=0.12):
    env = envelope(x)
    th = max(env.max() * 0.04, 0.004)
    idx = np.where(env > th)[0]
    segs, st, prev = [], idx[0], idx[0]
    for k in idx[1:]:
        if k - prev > gap * SR:
            segs.append([st, prev]); st = k
        prev = k
    segs.append([st, prev])
    return segs


def tighten(x, segs, max_pause):
    """Rebuild the take with inter-segment silences capped at max_pause (short crossfades)."""
    pre, post = int(0.04 * SR), int(0.06 * SR)
    out, new_segs = [], []
    pos = 0
    for i, (a, b) in enumerate(segs):
        a0 = max(0, a - pre)
        b1 = min(len(x), b + post)
        if i > 0:
            pa, pb = segs[i - 1]
            gap = (a - pb) / SR
            keep = min(gap, max_pause)
            sil = int(max(0.0, keep - (pre + post) / SR) * SR)
            out.append(np.zeros(sil)); pos += sil
        chunk = x[a0:b1].copy()
        f = int(0.008 * SR)
        chunk[:f] *= np.linspace(0, 1, f); chunk[-f:] *= np.linspace(1, 0, f)
        new_segs.append([(pos + (a - a0)) / SR, (pos + (b - a0)) / SR])
        out.append(chunk); pos += len(chunk)
    return np.concatenate(out), new_segs


def polish(x):
    b, a = signal.butter(2, 85 / (SR / 2), 'high'); x = signal.lfilter(b, a, x)
    # presence + air
    b, a = signal.butter(2, [2600 / (SR / 2), 6500 / (SR / 2)], 'band'); x = x + 0.28 * signal.lfilter(b, a, x)
    b, a = signal.butter(1, 9000 / (SR / 2), 'high'); x = x + 0.12 * signal.lfilter(b, a, x)
    # low-mid warmth
    b, a = signal.butter(2, [120 / (SR / 2), 260 / (SR / 2)], 'band'); x = x + 0.18 * signal.lfilter(b, a, x)
    # compression (soft knee, ~3:1 above threshold) with smoothed gain
    env = envelope(x, 0.012)
    th = 0.09
    g = np.where(env > th, (th / (env + 1e-9)) ** (1 - 1 / 3.0), 1.0)
    b, a = signal.butter(1, 30 / (SR / 2)); g = signal.filtfilt(b, a, g)
    x = x * g
    return x / (np.abs(x).max() + 1e-9) * 0.95


if __name__ == '__main__':
    os.makedirs(S + '/tts/clean', exist_ok=True)
    info = {}
    import wave
    for f in sorted(glob.glob(S + '/tts/r*_*.mp3')):
        name = os.path.basename(f)[:-4]
        x = load(f)
        segs = segments(x)
        y, ns = tighten(x, segs, KEEP.get(name, MAX_PAUSE))
        y = polish(y)
        tail = np.zeros(int(0.08 * SR))
        y = np.concatenate([y, tail])
        with wave.open(f'{S}/tts/clean/{name}.wav', 'wb') as w:
            w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
            w.writeframes((np.clip(y, -1, 1) * 32767).astype(np.int16).tobytes())
        info[name] = {'dur': round(len(y) / SR, 3), 'segs': [[round(a, 3), round(b, 3)] for a, b in ns]}
        print(f'{name}: {len(x) / SR:.2f}s -> {len(y) / SR:.2f}s  segs={info[name]["segs"]}')
    json.dump(info, open(S + '/tts/clean/segs.json', 'w'), indent=1)
