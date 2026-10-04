"""Denoised dialogue track on the reel timeline (48 kHz stereo WAV)."""
import subprocess, sys, types
import numpy as np
m = types.ModuleType("torchaudio.backend.common")
class AudioMetaData: pass
m.AudioMetaData = AudioMetaData
sys.modules["torchaudio.backend.common"] = m
import torch
from df.enhance import enhance, init_df
from scipy.signal import fftconvolve
import audio as au
import reel_sukkar as R

SR = 48000
raw = R.dialogue_bus().buf.astype(np.float32)          # unprocessed bites, placed on the timeline
model, st, _ = init_df(model_base_dir="models/DeepFilterNet3", log_level="ERROR")
mono = raw.mean(axis=1)                                  # interview audio is dual-mono
x = torch.from_numpy(mono[None].copy())
y = enhance(model, st, x, atten_lim_db=32).numpy()[0]
# latency check (enhance pads/compensates; verify)
ref, got = mono[: SR * 12], y[: SR * 12]
c = fftconvolve(got, ref[::-1], mode="full")
lag = int(np.argmax(c[len(ref) - 1: len(ref) - 1 + 4800]))
if lag:
    y = np.concatenate([y[lag:], np.zeros(lag, np.float32)])
print(f"denoiser latency {lag} samples ({lag/48:.1f} ms) compensated")
# tone + dynamics: high-pass, gentle presence, compression, de-ess
p = subprocess.run(["ffmpeg", "-v", "error", "-f", "f32le", "-ar", str(SR), "-ac", "1", "-i", "-", "-af",
                    "highpass=f=80,equalizer=f=180:t=q:w=1.0:g=-1.5,equalizer=f=3200:t=q:w=1.2:g=1.5,"
                    "deesser=i=0.35,acompressor=threshold=-20dB:ratio=2:attack=8:release=120:makeup=1",
                    "-f", "f32le", "-"], input=y.astype(np.float32).tobytes(), capture_output=True, check=True)
z = np.frombuffer(p.stdout, np.float32)
z = np.concatenate([z, np.zeros(max(0, len(y) - len(z)), np.float32)])[: len(y)]
# latency of the ffmpeg chain (compressor/de-esser have none, but verify)
c = fftconvolve(z[: SR * 12], y[: SR * 12][::-1], mode="full")
lag2 = int(np.argmax(c[SR * 12 - 1: SR * 12 - 1 + 4800]))
if lag2:
    z = np.concatenate([z[lag2:], np.zeros(lag2, np.float32)])
print(f"eq/comp latency {lag2} samples compensated")
# soft downward expander keyed to the speech level: below (speech - 24 dB) expand 1:2, max -20 dB
hop = 240
k = len(z) // hop
env = np.sqrt((z[: k * hop].reshape(k, hop) ** 2).mean(1) + 1e-12)
db = 20 * np.log10(env)
speech_db = np.median(db[db > np.percentile(db[db > -100], 60)])
thr = speech_db - 24
gain_db = np.clip(np.minimum(db - thr, 0) * 1.0, -20, 0)
g = np.zeros_like(gain_db); v = 0.0
for i, t in enumerate(gain_db):
    a = 0.7 if t > v else 0.06          # open fast, close slowly (~80 ms)
    v += a * (t - v); g[i] = v
gain = np.repeat(10 ** (g / 20), hop)
gain = np.concatenate([gain, np.full(len(z) - len(gain), gain[-1])])
z = z * gain.astype(np.float32)
print(f"speech ~{speech_db:.1f} dB, expander threshold {thr:.1f} dB")
st2 = np.stack([z, z], 1)
subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "f32le", "-ar", str(SR), "-ac", "2", "-i", "-", "-c:a", "pcm_s24le",
                "out/dialogue_clean_raw.wav"], input=np.clip(st2, -1, 1).astype(np.float32).tobytes(), check=True)
# noise floor before/after (in a pause between bites)
def floor(sig, t0, t1):
    s = sig[int(t0 * SR): int(t1 * SR)]
    return 20 * np.log10(np.sqrt((s ** 2).mean()) + 1e-12)
hop2 = 480
def frames(sig):
    kk = len(sig) // hop2
    return 20 * np.log10(np.sqrt((sig[: kk * hop2].reshape(kk, hop2) ** 2).mean(1)) + 1e-12)
fr, fz = frames(mono), frames(z)
inside = fr > -100
sp = inside & (fr > -30)
q = inside & (fr < -36)
snr0 = np.mean(fr[sp]) - np.percentile(fr[inside], 10)
snr1 = np.mean(fz[sp]) - np.percentile(fz[inside], 10)
print(f"speech-to-noise-floor gap: before {snr0:.1f} dB  ->  after {snr1:.1f} dB")
