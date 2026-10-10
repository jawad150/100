"""reel3 "Peace of mind": procedural airy future-garage score + final mix (music supervisor). Map: MUSIC_reel3.md.

Source: procedural, synthesised here in numpy with audio.py helpers (synth helpers and the mix law are shared with
reel1_music.py). Nothing licensed, nothing to archive: the wav is rebuilt from this file.

Style (distinct from reel1's 4/4 electro and reel2's cinematic clock): 110 BPM 2-step / future-garage, soft kick on
1 and the "and" of 3, rimshot on 2 and 4, swung 16th hats, warm sine sub, airy detuned pads and an FM e-piano/bell
arp, long hall. Key D major: Bm7 hook (dark drop on "crashes"), Gmaj7 -> A sus lifting into a Dmaj9 bloom on "zero",
Dmaj9 | Bm9 | Gmaj9 groove, lift at bar 5 (10.909), A sus build, Dmaj9 resolve at 15.273 on the end card.

    nice -n 10 python3 reel3_music.py          # music wav + final mix + measurements
Writes <WS>/audio/reel3_music.wav, reel3_mix.wav (+ _mix_stem, _music_stem; 48 kHz 24-bit, exactly DUR).
Needs <WS>/audio/reel3_sfx_stem.wav (python3 reel3_sfx.py) and reel3_vo.wav.
Render with:  --audio <WS>/audio/reel3_mix.wav
"""
import numpy as np
import audio as A
from reel1_music import (SR, TAU, hz, R, add, chord, sine_note, kick, hat, crash, noise_swell, dips,
                         build_music, build_mix, report)

BPM, DUR = 110, 21.5
B = 60.0 / BPM                                   # 0.5455 s beat, 2.182 s bar
N = int(round(DUR * SR))
bt = lambda n: n * B
CRASH = 1.40                                     # "crashes" (VO-pinned)
ZERO = 5.26                                      # "zero." slam (VO-pinned)
GROOVE = bt(10)                                  # 5.455: the beat starts on the beat after "zero"
LIFT = bt(20)                                    # 10.909 lift ("Trade with total peace of mind" 11.12)
BUILD = bt(26)                                   # 14.182 A sus build ("Confidence" 14.33)
RES = bt(28)                                     # 15.273 Dmaj9 resolve (plate full 15.15, CTA 15.30)
FADE0, FADE1 = 18.80, 21.35

BM7 = [47, 54, 57, 62]                           # B2 F#3 A3 D4
GMA7 = [43, 50, 54, 59, 62]                      # G2 D3 F#3 B3 D4
ASUS = [45, 52, 57, 62, 64]                      # A2 E3 A3 D4 E4
DMA9 = [38, 50, 57, 61, 64]                      # D2 D3 A3 C#4 E4
BM9 = [47, 54, 57, 61, 62]                       # B2 F#3 A3 C#4 D4
GMA9 = [43, 50, 54, 57, 59]                      # G2 D3 F#3 A3 B3
# groove bars: (t0, t1, pad notes, sub root midi)
BARS = [(ZERO, bt(12), DMA9, 38), (bt(12), bt(16), BM9, 35), (bt(16), bt(20), GMA9, 31),
        (bt(20), bt(24), DMA9, 38), (bt(24), bt(26), GMA9, 31)]


def ep(buf, m, t0, amp, d=0.9, p=0.0):
    """FM e-piano / bell: 1:2 carrier:modulator, index decaying, soft attack."""
    n = int(d * SR); u = np.arange(n) / SR; f = hz(m)
    x = np.sin(TAU * f * u + 1.6 * np.exp(-u / 0.12) * np.sin(TAU * 2 * f * u)) * np.exp(-u / 0.35) \
        * np.clip(u / 0.004, 0, 1) * np.clip((d - u) / 0.05, 0, 1)
    add(buf, A.pan(x * amp, p), t0)


def rim(buf, t0, amp):
    n = int(0.25 * SR); u = np.arange(n) / SR
    x = 0.7 * np.sin(TAU * 820 * u) * np.exp(-u / 0.018) + A.bp(R.standard_normal(n), 1500, 6000) * np.exp(-u / 0.03)
    add(buf, x * amp, t0)


def score():
    t = np.arange(N) / SR
    pad, low, drums, tops = (np.zeros((N, 2)) for _ in range(4))
    kk = np.zeros(N)

    # hook 0-2.18: airy Bm7 + two e-piano notes; on "crashes" the pad is cut and a dark B drone holds to bar 1
    chord(pad, BM7, 0.0, CRASH - 0.03, 0.55, lambda tt: 1500 - 500 * tt / CRASH, a=0.25, r=0.03)
    for b, m in ((0.0, 78), (bt(1), 81), (bt(2), 74)):
        ep(tops, m, b, 0.16, p=0.2)
    chord(pad, [35, 42, 47], CRASH, bt(4) + 0.2, 0.7, 320.0, a=0.03, r=0.4)
    sine_note(low, hz(35), CRASH, 1.0, 0.45, tau=0.5)

    # 2.18-5.26: light returns, Gmaj7 then A sus, quiet 8th e-piano from beat 5 (~"With Oktrum" 2.66),
    # a soft swell ending on "zero"
    chord(pad, GMA7, bt(4), bt(8), lambda tt: 0.3 + 0.35 * np.clip((tt - bt(4)) / B, 0, 1), 1300.0, a=0.6, r=0.05)
    chord(pad, ASUS, bt(8), ZERO - 0.02, lambda tt: 0.6 + 0.3 * (tt - bt(8)) / (ZERO - bt(8)),
          lambda tt: 1300 + 900 * (tt - bt(8)) / (ZERO - bt(8)), a=0.08, r=0.02)
    sine_note(low, hz(31), bt(4), bt(8) - bt(4), 0.3, a=0.2)
    sine_note(low, hz(33), bt(8), ZERO - bt(8), 0.3, a=0.05)
    for k, b in enumerate(np.arange(bt(5), ZERO - 0.05, B / 2)):
        ch = GMA7 if b < bt(8) else ASUS
        ep(tops, ch[(1, 2, 3, 4, 3, 2)[k % 6]] + 12, b, 0.10 + 0.04 * (b - bt(5)) / (ZERO - bt(5)), p=0.25 * (-1) ** k)
    noise_swell(tops, bt(8), ZERO - 0.01, 900, 6000, 0.12, power=2.5, hp_hz=800)

    # zero 5.26 -> 14.18: Dmaj9 blooms on "zero"; 2-step groove from beat 10; lift at bar 5 (10.909)
    sine_note(low, hz(26), ZERO, 1.6, 0.45, tau=0.6)                    # D1 bloom under the shield slam
    for t0, t1, ch, root in BARS:
        lifted = t0 >= LIFT
        chord(pad, ch, t0, t1 - 0.01, 0.75 if lifted else 0.65, 2000.0 if lifted else 1400.0,
              a=0.05 if t0 != ZERO else 0.03, r=0.03, voices=5 if lifted else 3)
        sine_note(low, hz(root), t0, t1 - t0, 0.42 if lifted else 0.36, a=0.03)
    for b in np.arange(bt(10), BUILD - 0.01, B):
        beat = round(b / B) % 4                                          # position in the bar
        for off, hit in ((0.0, beat == 0), (0.5, beat == 2)):
            if hit:
                kick(kk, b + off * B, 0.8, f_end=48.0, f_drop=80.0, tau=0.22)
        if beat in (1, 3):
            rim(drums, b, 0.30)
        for s in range(4):                                               # swung 16ths
            amp = (0.07, 0.035, 0.05, 0.035)[s] * (1.4 if b >= LIFT else 1.0)
            hat(tops, b + s * B / 4 + (0.06 * B if s % 2 else 0.0), amp, tau=0.02)
        if b >= LIFT:
            hat(tops, b + B / 2, 0.08, tau=0.09)                          # open hat on the off-beats after the lift
    for k, b in enumerate(np.arange(GROOVE, BUILD - 0.01, B / 2)):      # e-piano arp, chord tones
        ch = next(c for a0, a1, c, _ in BARS if a0 - 1e-6 <= b < a1)
        ep(tops, ch[(2, 3, 4, 3)[k % 4]] + 12, b, 0.09 if b < LIFT else 0.11, p=0.3 * (-1) ** k)
    noise_swell(tops, bt(19), LIFT - 0.01, 1500, 9000, 0.14, power=2.0, hp_hz=1500)
    crash(tops, LIFT, 0.14, tau=1.2)

    # build 14.18-15.27: A sus, kick out, rim 8ths -> 16ths, swell; 30 ms suck-out; Dmaj9 resolve + bell top
    chord(pad, ASUS, BUILD, RES - 0.03, lambda tt: 0.6 + 0.35 * np.clip((tt - BUILD) / (RES - BUILD), 0, 1),
          lambda tt: 1300 + 1300 * np.clip((tt - BUILD) / (RES - BUILD), 0, 1), a=0.04, r=0.02, voices=5)
    sine_note(low, hz(33), BUILD, RES - BUILD, 0.36, a=0.03)
    for b in list(np.arange(BUILD, bt(27), B / 2)) + list(np.arange(bt(27), RES - 0.04, B / 4)):
        rim(drums, b, 0.12 + 0.25 * (b - BUILD) / (RES - BUILD))
    noise_swell(tops, BUILD, RES - 0.03, 700, 6000, 0.22, power=2.0)

    sine_note(low, hz(26), RES, 3.0, 0.45, tau=1.2)
    crash(tops, RES, 0.12, tau=1.6)
    swell = lambda tt: 0.8 * (1 - 0.4 * np.clip((tt - 17.0) / 1.8, 0, 1))
    chord(pad, DMA9, RES, FADE1 - 0.2, swell, lambda tt: 1900 - 1000 * np.clip((tt - 16.5) / 3.5, 0, 1),
          a=0.06, r=0.2, voices=5)
    sine_note(low, hz(38), RES, FADE1 - RES, 0.3, a=0.05, tau=3.0)
    for k, (b, m) in enumerate(((RES, 86), (RES + B, 81), (RES + 2 * B, 88), (RES + 3 * B, 85), (RES + 5 * B, 81),
                                (RES + 7 * B, 86))):
        ep(tops, m, b, 0.11 * (1 - 0.1 * k), d=1.4, p=0.3 * (-1) ** k)

    pad = A.sidechain(pad, kk, depth_db=4, attack=0.006, release=0.2)
    low = A.sidechain(low, kk, depth_db=5, attack=0.004, release=0.15)
    mus = 0.32 * A.lp(pad, 2200) + 0.5 * A.hp(low, 30) + 0.4 * drums + 0.3 * tops + 0.7 * kk[:, None]
    mus = A.hp(mus, 28, 2)
    mus = A.reverb(mus, 'hall', wet_db=-11, send_hp=200)[:N]
    g = dips(t, [(RES - 0.03, RES, -12.0, 0.008)])
    fade = np.where(t < FADE0, 1.0, np.cos(np.clip((t - FADE0) / (FADE1 - FADE0), 0, 1) * np.pi / 2) ** 2)
    return mus * (g * fade)[:, None]


if __name__ == '__main__':
    mus = build_music('reel3', score)
    report('reel3', DUR, BPM, mus, build_mix('reel3', DUR))
