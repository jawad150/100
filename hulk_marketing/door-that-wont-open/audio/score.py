"""score.py: the film's original music, composed in code (repo's music_synth.py instruments), 120 bpm.

    python3 audio/score.py          (from hulk_marketing/door-that-wont-open)  ->  audio/music.wav

Arrangement (seconds = beats / 2, bar = 2 s):
  0.0-8.0   light pulse, A minor (Am F C G): soft kick, shaker, muted pluck arps, sub bass
  8.0-13.0  silence: the waiting beat (the PDF: "drops to silence for the waiting beat")
  13.0-18.0 the pulse comes back lighter while she crosses the road (Am F C)
  18.0-21.0 reveal: drums out, pad Fmaj7 -> E (tension)
  21.0-25.2 the point: sub drop on the hard cut, Am(add9) pad (carries to the 25.2 cut), a slow heartbeat kick,
            felt-piano notes
  24.6-25.2 reverse swell into the rewind
  25.2-26.2 rewind: the 13-21 s music played backwards on a spinning tape (1.0 s)
  26.2-27.0 pad lift under "We build sites that are..."
  27.0-35.0 the fix + end card, C major (C G Am F): four-on-the-floor, claps, bright plucks
  35.2-36.5 final C(add9) chord after "...au-dit." (35.15): struck, then it decays out inside the film (sub bass
            gone by ~36.05, pad by ~36.4); no end fade here (mix.py fades the master's last 0.9 s)
"""
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', '..', 'pipeline', 'fostering'))
import audio as A  # noqa: E402
import music_synth as MS  # noqa: E402

SR = A.SR
DUR = 36.5
BPM = 120
B = 60 / BPM          # beat (s)
S16 = B / 4
T_REW, T_REW1 = 25.2, 26.2   # the rewind (film.js T.rew0 .. T.rew1): hard cut in at 25.2, out at 26.2
T_END = 35.2                 # final chord, after "audit." (VO ends ~35.15)


def arp(tr, chord_notes, t0, t1, cutoff, vel=0.55, gain_db=0.0, pattern=(0, 1, 2, 3, 2, 1, 0, 2), pan=0.15):
    i = 0
    t = t0
    while t < t1 - 1e-6:
        n = chord_notes[pattern[i % len(pattern)] % len(chord_notes)]
        x = MS.pluck_synth(n, dur=0.16, vel=vel * (1.0 if i % 2 == 0 else 0.8), cutoff=cutoff, decay=0.11, seed=i)
        tr.add(x, t, gain_db, pan=pan if i % 2 else -pan)
        t += B / 2
        i += 1


# hits softened under a spoken word: the 5.0 downbeat lands on the cue word "open." (4.99-5.37)
SOFT_HITS = {5.0: -4.0}


def bass(tr, root, t0, t1, gain_db=0.0, every=2):
    t = t0
    while t < t1 - 1e-6:
        tr.add(MS.sub_bass(root, dur=B * 0.9, vel=0.75), t, gain_db + SOFT_HITS.get(round(t, 3), 0.0))
        t += B * every


def kicks(tr, t0, t1, gain_db=0.0, every=1, vel=0.8):
    t = t0
    while t < t1 - 1e-6:
        tr.add(MS.soft_kick(vel=vel, punch=0.45, decay=0.28), t, gain_db + SOFT_HITS.get(round(t, 3), 0.0))
        t += B * every


def shakers(tr, t0, t1, gain_db=0.0):
    n = int(round((t1 - t0) / S16))
    acc = (1.0, 0.45, 0.75, 0.5)
    for i in range(n):
        tr.add(MS.shaker(vel=0.6 * acc[i % 4], seed=i % 4), t0 + i * S16, gain_db, pan=0.25)


def build():
    tr = MS.Track(DUR)
    # ---------------------------------------------------------- 0-8: light pulse in A minor
    prog1 = [('Am', 'A1'), ('F', 'F1'), ('C', 'C2'), ('G', 'G1')]
    for k, (ch, root) in enumerate(prog1):
        t0 = 2 * k
        notes = MS.chord(ch, octave=4)
        arp(tr, notes, t0, t0 + 2, cutoff=900 + 150 * k, vel=0.5, gain_db=-4)
        bass(tr, root, t0, t0 + 2, gain_db=-5)
        tr.add(MS.pad(MS.chord(ch, octave=3), dur=1.9, vel=0.4, wave='warm', attack=0.3, release=0.4, cutoff=1200), t0, -15)
    kicks(tr, 0.0, 8.0, gain_db=-8, vel=0.7)
    shakers(tr, 0.0, 8.0, gain_db=-17)
    for i in range(8):
        tr.add(MS.hat(vel=0.5, seed=i), 0.25 + i * 1.0 - 0.0 + 0.0, -18)
        tr.add(MS.hat(vel=0.4, seed=i + 3), 0.75 + i * 1.0, -20)
    # ---------------------------------------------------------- 8-13: silence (the tails die naturally)
    # ---------------------------------------------------------- 13-18: lighter pulse while she crosses
    prog2 = [('Am', 'A1', 13.0, 15.0), ('F', 'F1', 15.0, 17.0), ('C', 'C2', 17.0, 18.0)]
    for ch, root, t0, t1 in prog2:
        notes = MS.chord(ch, octave=4)
        arp(tr, notes, t0, t1, cutoff=1100, vel=0.45, gain_db=-6)
        bass(tr, root, t0, t1, gain_db=-7)
    shakers(tr, 13.0, 18.0, gain_db=-19)
    kicks(tr, 15.0, 18.0, gain_db=-12, vel=0.6, every=2)
    # ---------------------------------------------------------- 18-21: reveal, tension pad
    tr.add(MS.pad(MS.chord('Fmaj7', octave=3), dur=1.6, vel=0.55, wave='warm', attack=0.15, release=0.6, cutoff=1400), 18.0, -9)
    tr.add(MS.pad(MS.chord('E', octave=3), dur=1.3, vel=0.55, wave='warm', attack=0.2, release=0.3, cutoff=1300), 19.6, -10)
    tr.add(MS.sub_bass('F1', dur=1.5, vel=0.7), 18.0, -8)
    tr.add(MS.sub_bass('E1', dur=1.3, vel=0.7), 19.6, -8)
    # ---------------------------------------------------------- 21-25: the point
    tr.add(MS.pad(MS.chord('A', 'madd9', octave=3), dur=4.0, vel=0.6, wave='warm', attack=0.05, release=0.3, cutoff=1500, sweep=0.2), 21.0, -9)
    tr.add(MS.sub_bass('A1', dur=1.6, vel=0.8, glide_from='A2', glide=0.25), 21.0, -5)
    for tt in (21.0, 23.0):
        tr.add(MS.soft_kick(vel=0.7, punch=0.3, decay=0.4), tt, -10)
    for tt, n, d in ((22.0, 'E5', 0.9), (23.0, 'C5', 0.9), (24.0, 'B4', T_REW - 24.0)):   # the last one rings to the cut
        tr.add(MS.felt_piano(n, dur=d, vel=0.5), tt, -14)
    rs = MS.reverse_swell(dur=0.6, vel=0.7, notes=MS.chord('C', octave=4))
    tr.add(rs, T_REW - 0.6, -10)            # ends on the hard cut to the rewind
    # ---------------------------------------------------------- 26.2-27: lift
    tr.add(MS.pad(MS.chord('G', 'sus4', octave=3), dur=0.75, vel=0.5, wave='warm', attack=0.4, release=0.2, cutoff=1800), 26.2, -12)
    tr.add(MS.riser(dur=0.8, vel=0.5), 27.0 - 0.8, -16)
    # ---------------------------------------------------------- 27-36.5: the fix, C major
    prog3 = [('C', 'C2', 27.0, 29.0), ('G', 'G1', 29.0, 31.0), ('Am', 'A1', 31.0, 33.0), ('F', 'F1', 33.0, 35.0)]
    for ch, root, t0, t1 in prog3:
        notes = MS.chord(ch, octave=4)
        arp(tr, notes + [notes[0] + 12], t0, t1, cutoff=2000, vel=0.55, gain_db=-5, pattern=(0, 2, 1, 3, 2, 4, 3, 1))
        bass(tr, root, t0, t1, gain_db=-5, every=1)
        tr.add(MS.pad(MS.chord(ch, octave=3), dur=1.95, vel=0.45, wave='warm', attack=0.2, release=0.4, cutoff=1700), t0, -14)
    kicks(tr, 27.0, 35.0, gain_db=-7, vel=0.8)
    for i in range(16):
        if i % 2:
            tr.add(MS.clap(vel=0.6, seed=i), 27.0 + i * B, -13)
    shakers(tr, 27.0, 35.0, gain_db=-16)
    for i in range(16):
        tr.add(MS.hat(vel=0.5, seed=i), 27.25 + i * B, -17)
    tr.add(MS.glockenspiel('E6', vel=0.6), 27.0, -12)
    tr.add(MS.glockenspiel('G6', vel=0.5), 27.25, -14)
    tr.add(MS.glockenspiel('C7', vel=0.5), 27.5, -15)
    # final chord after "-dit" (35.15): struck, then decaying out inside the film. The sub bass is short with a
    # long smooth release (gone by ~36.05) so nothing low is left to stop at the end; pad and piano release by ~36.4.
    tr.add(MS.pad(MS.chord('C', 'add9', octave=3), dur=0.5, vel=0.6, wave='warm', attack=0.05, release=0.7, cutoff=2000), T_END, -9)
    for n in MS.chord('C', 'add9', octave=4):
        tr.add(MS.felt_piano(n, dur=0.6, vel=0.5, release=0.6), T_END, -13)
    tr.add(MS.sub_bass('C2', dur=0.3, vel=0.7, release=0.55), T_END, -6)
    tr.add(MS.soft_kick(vel=0.8), T_END, -7)
    x = np.asarray(tr)
    # gentle room so it sits as one bed
    x = A.reverb(x, 'studio', wet_db=-16)[:len(x)]
    # ---------------------------------------------------------- 25.2-26.2: tape rewind of 13-21 s
    seg = x[int(13.0 * SR):int(21.0 * SR)][::-1].copy()
    rew = T_REW1 - T_REW
    n_out = int(rew * SR)
    tau = np.arange(n_out) / SR
    rate = 2.5 + 8.0 * np.sin(np.pi * np.clip(tau / rew, 0, 1)) ** 1.2      # spin up, then slow into the stop
    pos = np.cumsum(rate)
    pos = pos / pos[-1] * (len(seg) - 2)
    i0 = np.floor(pos).astype(int)
    fr = (pos - i0)[:, None]
    tape = seg[i0] * (1 - fr) + seg[i0 + 1] * fr
    tape = A.hp(tape, 300)
    env = np.minimum(1, tau / 0.06) * np.minimum(1, (rew - tau) / 0.1)
    tape *= (0.55 * env)[:, None]
    i25 = int(T_REW * SR)
    x[i25:i25 + n_out] = x[i25:i25 + n_out] * 0.15 + tape
    # silence the waiting beat (keep the 8.0 s tails short and clean)
    a, b = int(8.0 * SR), int(13.0 * SR)
    fade = np.linspace(1, 0, int(0.35 * SR))[:, None]
    x[a:a + len(fade)] *= fade
    x[a + len(fade):b] = 0
    # level: -18 LUFS bed, true peak <= -3 dBTP before the mix
    x = x * A.undb(-18 - A.loudness(x.astype(np.float32)))
    g = A.limiter_gain(x, ceiling_db=-3.0)
    x = x * g[:, None]
    return x.astype(np.float32)


if __name__ == '__main__':
    x = build()
    out = os.path.join(HERE, 'music.wav')
    A._write_wav(out, x, bits=24)
    print(f'-> {out}  {len(x) / SR:.2f} s  {A.loudness(x):.1f} LUFS  TP {A.true_peak(x):.1f} dBTP')
