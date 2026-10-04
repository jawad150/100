"""Verify lip sync: for each on-camera interview shot, correlate the horizontal camera's own
audio (at the source frames shown) with the final mix at the same output time."""
import subprocess, sys, numpy as np
from scipy.signal import fftconvolve
import reel_sukkar as R
SR = 16000
def load(path, t0, dur):
    raw = subprocess.run(["ffmpeg","-v","quiet","-ss",f"{t0:.4f}","-t",f"{dur:.4f}","-i",path,"-map","0:a:0","-ac","1","-ar",str(SR),"-f","f32le","-"],capture_output=True).stdout
    return np.frombuffer(raw, np.float32)
mix = sys.argv[1] if len(sys.argv) > 1 else "out/mix.wav"
prev = 0.0
for end_s, spec, trans in R.TL:
    if spec.get("kind") == "th":
        start = prev
        dur = end_s - start - 0.1
        cam = load(spec["src"], spec["t"], dur)          # what the picture's own mic heard
        out = load(mix, start - 0.25, dur + 0.5)         # what the reel plays at that time
        cam = (cam - cam.mean()) / (cam.std() + 1e-9); out = (out - out.mean()) / (out.std() + 1e-9)
        c = fftconvolve(out, cam[::-1], mode="valid") / len(cam)
        k = int(np.argmax(c)); lag_ms = (k / SR - 0.25) * 1000
        print(f"{spec['label']:22s} out {start:6.2f}-{end_s:6.2f}s  offset {lag_ms:+6.1f} ms  (corr {c[k]:.2f})  -> {'IN SYNC' if abs(lag_ms) <= 21 else 'CHECK'}")
    prev = end_s
