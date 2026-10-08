"""Slices the sound effects out of the caption-style reference video.

The reference audio is first split with Demucs (htdemucs, two stems) so the voice is removed;
the SFX are then cut from the no-vocals stem at the hand-picked event times below."""
import os, sys
import numpy as np
from scipy.io import wavfile

# name: (start, end) in seconds of the reference
SLICES = {
    'click_a': (0.00, 0.26), 'click_b': (8.08, 8.42), 'tick': (11.12, 11.55),
    'pop_a': (14.27, 14.72), 'pop_hit': (15.21, 15.70), 'swish_s': (3.93, 4.42),
    'hit_c': (1.70, 2.25), 'boom': (12.02, 13.05), 'boom_b': (30.66, 31.40),
    'ding': (5.56, 6.78), 'whoosh_a': (9.50, 10.60), 'whoosh_b': (13.25, 14.05),
    'whoosh_c': (18.50, 19.30), 'whoosh_d': (24.75, 25.55), 'whoosh_e': (31.36, 32.40),
    'blip_a': (19.90, 20.42), 'blip_b': (23.25, 23.85), 'blip_c': (33.88, 34.45),
}


def main(stem, out_dir):
    sr, a = wavfile.read(stem)
    a = a.astype(np.float32)
    if a.dtype != np.float32 or np.abs(a).max() > 2:
        a /= 32768.0
    os.makedirs(out_dir, exist_ok=True)
    for name, (s, e) in SLICES.items():
        seg = a[int(s * sr):int(e * sr)].copy()
        n = len(seg)
        fi, fo = int(0.004 * sr), int(min(0.12, (e - s) * 0.3) * sr)
        env = np.ones(n, np.float32)
        env[:fi] = np.linspace(0, 1, fi)
        env[-fo:] = np.linspace(1, 0, fo) ** 2
        seg *= env[:, None] if seg.ndim > 1 else env
        seg /= max(np.abs(seg).max(), 1e-6) / 0.7
        wavfile.write(f'{out_dir}/{name}.wav', sr, (seg * 32767).astype(np.int16))
    print('wrote', len(SLICES), 'sfx to', out_dir)


if __name__ == '__main__':
    main(*sys.argv[1:3])
