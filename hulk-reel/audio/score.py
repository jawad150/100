# /// script
# requires-python = ">=3.10"
# dependencies = ["librosa>=0.10", "numpy", "scipy", "soundfile"]
# ///
"""Hulk Marketing reel score: 128 bpm, F minor, 8 bars = 15.0 s.

  bars 0-1  (beats 0-8)   hook: tight kick + hats + plucked bass pulse, the dot's bounces ride on top
  bar  2    (beats 8-12)  the flex: clap roll speeding up, riser, filter opening, half-beat silence
  bars 3-6  (beats 12-28) the drop: driven "muscle" bass, clap on 2 and 4, chord stabs, pluck hook
  bar  7    (beats 28-32) end card: one held chord on a kick + sub + crash, then the tail

Run:  MOTION_REEL_SKILL=<skill> uv run hulk-reel/audio/score.py
Writes hulk-reel/audio/music.wav and hulk-reel/beats.json (grid measured on the drum stem).
"""
import json
import os
import sys
from pathlib import Path

import numpy as np
import soundfile as sf

sys.path.insert(0, str(Path(os.environ["MOTION_REEL_SKILL"]) / "scripts"))
import dsp  # noqa: E402
from dsp import SR, Bus, bass_note, clap, crash, filt, hat, kick, measure_beats, note_name, midi, \
    pad_chord, pluck, reverb, riser, sidechain, sub_drop  # noqa: E402

FILM = Path(__file__).resolve().parent.parent
BPM, DUR = 128.0, 15.0
BEAT = 60 / BPM
N_BEATS = 32
DROP, LAST = 12, 28
dsp.seed(20261012)

# F minor: i  VI  III  VII  (Fm  Db  Ab  Eb)
ROOTS = ["F2", "Db2", "Ab1", "Eb2"]
CHORDS = [["F3", "Ab3", "C4", "F4"], ["Db3", "F3", "Ab3", "Db4"],
          ["C3", "Eb3", "Ab3", "C4"], ["Eb3", "G3", "Bb3", "Eb4"]]
HOOK = ["C5", "Eb5", "F5", "Ab5", "G5", "F5", "Eb5", "C5"]   # pluck hook over the drop, 8ths

drums, bass, music, fx = (Bus(DUR, BPM) for _ in range(4))


def muscle_bass(note, length):
    """Driven saw bass: bass_note through a soft clipper, with a short filter blip on the attack."""
    x = bass_note(note, length, 1400)
    x = np.tanh(2.6 * x) * 0.75
    sub = np.sin(2 * np.pi * dsp.hz(note) / 2 * dsp.tvec(len(x))) * np.exp(-dsp.tvec(len(x)) / 0.4)
    return x + 0.5 * sub * (1 - np.exp(-dsp.tvec(len(x)) / 0.003))


for b in range(N_BEATS):
    bar = b // 4
    ch, root = CHORDS[bar % 4], ROOTS[bar % 4]
    if b < 8:                                  # hook bars: tight and dry, leaves room for SFX
        drums.add(kick(), b, 0.85)
        drums.add(hat(), b + 0.5, 0.22, pan=0.25)
        drums.add(hat(), b + 0.75, 0.08, pan=-0.3)
        if b % 2 == 1:
            drums.add(clap(tight=True), b, 0.32)
        for h in (0, 0.5):
            bass.add(bass_note(root.replace("2", "3").replace("1", "2"), BEAT / 2 * 0.6, 700), b + h, 0.42)
    elif b < DROP:                             # the flex: build
        drums.add(kick(soft=True), b, 0.6)
        steps = 2 if b < 10 else 4
        for k in range(steps):
            if b == 11 and k >= 2:
                continue                       # half-beat hole before the drop
            g = 0.18 + 0.25 * ((b - 8) * steps + k) / 16
            drums.add(clap(tight=True), b + k / steps, g, pan=0.1 * (-1) ** k)
    elif b < LAST:                             # the drop
        drums.add(kick(), b, 1.0)
        if b % 2 == 1:
            drums.add(clap(), b, 0.5, pan=0.05)
        drums.add(hat(), b + 0.5, 0.26, pan=0.25)
        for s in (0.25, 0.75):
            drums.add(hat(), b + s, 0.07, pan=-0.3)
        if b % 4 == 3:
            drums.add(hat(open_=True), b + 0.5, 0.12, pan=0.3)
        for h in (0, 0.5):
            n = root if h == 0 else note_name(midi(root) + 12)
            bass.add(muscle_bass(n, BEAT / 2 * 0.85), b + h, 0.55)
        for h, nt in zip((0, 0.5), HOOK[(b % 4) * 2:(b % 4) * 2 + 2]):
            if (b - DROP) >= 4:                # the hook comes in one bar after the drop
                music.add(pluck([nt], 0.2, 3600), b + h, 0.2, pan=0.2)
    if b % 4 == 0 and b < LAST:                # chords each bar
        L = 4 * BEAT + 0.1
        if b < 8:
            music.add(pad_chord(ch, L, (500, 1100), attack=0.05), b, 0.16)
        elif b < DROP:
            music.add(pad_chord(ch, L, (600, 4200), attack=0.4), b, 0.22)
        else:
            for s in (0, 1.5, 3):              # stabs: 1, the "and" of 2, 4
                music.add(pad_chord(ch, BEAT * 0.45, 3800, attack=0.004, release=0.12), b + s, 0.3)
            music.add(pad_chord(ch, L, 1200, attack=0.2), b, 0.12)

# build + drop + end landings
fx.add(riser(4 * BEAT), DROP - 4.0, 0.35)
fx.add(crash(0.9)[::-1] * 0.7, DROP - 0.9 / BEAT, 0.22)
drums.add(sub_drop(1.2, 80, 30), DROP, 0.7)
drums.add(crash(1.6), DROP, 0.28)
fx.add(crash(0.9)[::-1] * 0.7, LAST - 0.9 / BEAT, 0.2)
end_ch = ["F3", "C4", "Ab4", "C5", "Eb5"]
music.add(pad_chord(end_ch, 4 * BEAT + 1.0, (5200, 1300), attack=0.005, release=0.8), LAST, 0.55)
bass.add(muscle_bass("F1", 1.6) * np.exp(-dsp.tvec(int(1.6 * SR)) / 0.7)[: int(1.6 * SR)], LAST, 0.5)
drums.add(kick(), LAST, 1.0)
drums.add(crash(2.2), LAST, 0.3)
drums.add(sub_drop(1.4, 70, 28), LAST, 0.55)

N = drums.n
duck = sidechain([i * BEAT for i in range(DROP, LAST)], drums.x.shape[1], 0.55, 0.11)
mix = drums.x + fx.x + (bass.x + reverb(music.x, 0.32)) * duck
mix = mix[:, :N]
fade = int(0.35 * SR)
mix[:, -fade:] *= np.linspace(1, 0, fade) ** 2
mix *= 10 ** (-3 / 20) / (np.abs(mix).max() + 1e-9)

grid = measure_beats(drums.x[:, :N].mean(axis=0).astype(np.float32), SR, BPM, n_beats=N_BEATS + 1)
grid["beats"] = [b for b in grid["beats"] if b < DUR + 0.5]
grid["downbeats"] = grid["beats"][::4]
grid["sections"] = [{"name": "hook", "beat": 0}, {"name": "build", "beat": 8},
                    {"name": "main", "beat": DROP}, {"name": "end", "beat": LAST}]
mono = mix.mean(axis=0)
bar_s = grid["period"] * 4
grid["bar_energy"] = [round(float(np.sqrt(np.mean(mono[int((grid["offset"] + i * bar_s) * SR):int((grid["offset"] + (i + 1) * bar_s) * SR)] ** 2) + 1e-12)), 4) for i in range(8)]
grid["duration"] = DUR
grid["source"] = "audio/score.py: synth F minor 128 bpm, grid measured on the drum stem"
sf.write(FILM / "audio" / "music.wav", mix.T, SR, subtype="PCM_24")
(FILM / "beats.json").write_text(json.dumps(grid, indent=1))
print(grid["source"])
print(f"grid: {grid['bpm']} bpm, offset {grid['offset'] * 1000:.1f} ms, {len(grid['beats'])} beats, "
      f"fit {grid['fit_inliers']} inliers, rms {grid['fit_residual_ms']} ms; bar energy {grid['bar_energy']}")
