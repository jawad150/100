"""Reel 2 audio: original result audio + SFX (no music)."""
import numpy as np, wave
import audio as A
DUR = 34.0
A.N = int(A.SR * DUR)
A.sfx = np.zeros((A.N, 2))
A.music = np.zeros((A.N, 2))
from audio import *  # noqa

A.impact(0.02, 0.9); A.whoosh(0.0, 0.7, 180, 3000, 0.45)
for k, tw in enumerate([0.42, 0.49, 0.56, 0.62, 0.69, 0.76]):
    A.tick(tw, 0.12, 2600 + k * 150)
A.pop(0.85, 0.3, 350, 1100)
A.pop(1.1, 0.3, 260, 850, pan=0.5); A.pop(1.2, 0.28, 300, 900, pan=-0.5); A.pop(1.35, 0.25, 320, 1000, pan=0.4)
A.shimmer(1.4, 1.2, 0.12); A.whoosh(1.3, 0.35, 800, 5000, 0.15)
# ending
A.rev_swell(28.0, 0.7, 0.3)
A.whoosh(27.9, 0.9, 200, 3000, 0.5, 0.0, 0.0, peak=0.7)
A.impact(28.85, 0.7); A.shimmer(28.9, 1.8, 0.16)
A.whoosh(29.0, 0.6, 600, 4000, 0.25, -0.6, 0.2)
for k in range(4):
    A.tick(29.4 + k * 0.08, 0.1, 2600 + 150 * k)
for k in range(6):
    A.tick(29.5 + k * 0.06, 0.08, 2400 + 120 * k)
A.pop(29.9, 0.35, 260, 900)
for k, tp in enumerate([29.8, 29.9, 30.0, 30.1]):
    A.pop(tp, 0.2, 280 + 30 * k, 950 + 50 * k, pan=[-0.6, 0.6, -0.5, 0.5][k])

orig = A.load_original()
o = np.zeros((A.N, 2))
n = min(len(orig), A.at(28.04))
seg = orig[:n].copy()
f = int(0.5 * A.SR)
seg[-f:] *= np.linspace(1, 0, f)[:, None]
o[:n] = seg
# normalise original to a solid level, then SFX on top
o *= 10 ** (-17 / 20) / (np.sqrt(np.mean(o[:n] ** 2)) + 1e-9)
mix = o + A.sfx * 0.45
fo = A.at(DUR - 0.4)
mix[fo:] *= np.linspace(1, 0, A.N - fo)[:, None] ** 1.5
mix = A.hp(mix, 25)
mix = np.tanh(mix * 1.1) / np.tanh(1.1)
mix *= 0.93 / np.abs(mix).max()
pcm = (np.clip(mix, -1, 1) * 32767).astype(np.int16)
with wave.open(A.S + '/out/audio2.wav', 'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(A.SR); w.writeframes(pcm.tobytes())
print('audio2 written', 20 * np.log10(np.sqrt(np.mean(mix ** 2))))
