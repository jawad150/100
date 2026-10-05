"""Lip-sync check for the 9:16 speaker panel: correlate each segment's own camera audio
(at the source frames shown) with the reel's dialogue track at the same output time."""
import subprocess, sys
import numpy as np
from scipy.signal import fftconvolve
sys.path.insert(0, ".")
_argv, sys.argv = sys.argv, [sys.argv[0]]
import reel916 as V
sys.argv = _argv
SR = 16000


def load(path, t0, dur):
    raw = subprocess.run(["ffmpeg", "-v", "quiet", "-ss", f"{t0:.4f}", "-t", f"{dur:.4f}", "-i", path, "-map", "0:a:0",
                          "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"], capture_output=True).stdout
    return np.frombuffer(raw, np.float32)


ref_path = sys.argv[1] if len(sys.argv) > 1 else "out/v3_dialogue.wav"
prev = 0.0
for end_s, spec, trans in V.TS:
    if spec is not None:
        a, b = max(prev, 0.0), end_s
        a = max(a, V.PANEL[0][0] if a < 15 else V.PANEL[1][0])
        dur = b - a
        cam = load(spec["src"], spec["t"] + (a - prev), dur)
        out = load(ref_path, a - 0.25, dur + 0.5)
        if len(cam) < SR * 0.3 or np.std(cam) < 1e-6:
            print(f"{spec['label']:20s} no camera audio")
        else:
            cam = (cam - cam.mean()) / (cam.std() + 1e-9)
            out = (out - out.mean()) / (out.std() + 1e-9)
            c = fftconvolve(out, cam[::-1], mode="valid") / len(cam)
            k = int(np.argmax(c))
            lag = (k / SR - 0.25) * 1000
            print(f"{spec['label']:20s} out {a:6.2f}-{b:6.2f}s  offset {lag:+6.1f} ms (corr {c[k]:.2f})  "
                  f"{'IN SYNC' if abs(lag) <= 21 else 'CHECK'}")
    prev = end_s
