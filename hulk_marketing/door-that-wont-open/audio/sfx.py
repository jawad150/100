"""sfx.py: the film's sound design (PDF: street bustle, a dull thud on the push, a faint looping "loading" tick,
her sigh, the other door's cheerful bell, a rewind whoosh, then a clean "click" as the door opens), plus the UI
sounds of the SaaS layer. Every cue time comes from film.js (HITS, key times) and audio/steps.json (heel strikes).

    python3 audio/sfx.py            (from hulk_marketing/door-that-wont-open)  ->  audio/sfx.wav (+ sfx_cues.json)

Catalog sounds come from the repo's pipeline/fostering/audio.py (levels pre-balanced, hit-aligned); the street bed,
heel steps, door thud, sigh, shop bell, sliding door and latch click are synthesised here.
"""
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
FILM = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(FILM, '..', '..', 'pipeline', 'fostering'))
import audio as A  # noqa: E402
import music_synth as MS  # noqa: E402

SR = A.SR
DUR = 36.5
rng = np.random.default_rng(7)
N = int(DUR * SR)


def place(buf, x, t, gain_db=0.0, pan=0.0, hit=0.0):
    x = A._st(np.asarray(x, dtype=np.float64))
    if pan:
        x = A.pan(x, pan)
    i0 = int(round((t - hit) * SR))
    j0 = max(0, -i0)
    i0 = max(0, i0)
    n = min(len(x) - j0, len(buf) - i0)
    if n > 0:
        buf[i0:i0 + n] += x[j0:j0 + n] * A.undb(gain_db)


def cat(name, **p):
    s = A.sound(name, **p)
    return np.asarray(s, dtype=np.float64), s.hit


def env(n, a, d):
    t = np.arange(n) / SR
    return np.minimum(1, t / max(a, 1e-4)) * np.exp(-np.maximum(0, t - a) / d)


# ------------------------------------------------------------------ custom sounds
def heel(seed, soft=1.0):
    r = np.random.default_rng(seed)
    n = int(0.16 * SR)
    noise = r.standard_normal(n)
    click = A.bp(noise, 1800, 6500) * env(n, 0.0008, 0.012) * 0.9
    body = A.bp(noise, 140, 600) * env(n, 0.002, 0.03) * 1.4
    scuff = A.bp(r.standard_normal(n), 2500, 8000) * env(n, 0.01, 0.04) * 0.15
    x = (click + body + scuff) * soft
    return A._peaknorm(x, 0.5)


def door_thud(seed=0):
    # a glass door held by its lock: low knock + frame rattle + glass buzz
    r = np.random.default_rng(seed)
    n = int(0.9 * SR)
    t = np.arange(n) / SR
    knock = np.sin(2 * np.pi * 92 * t) * env(n, 0.002, 0.07) + 0.6 * np.sin(2 * np.pi * 165 * t) * env(n, 0.001, 0.05)
    hit = A.bp(r.standard_normal(n), 200, 1800) * env(n, 0.0015, 0.025) * 1.2
    rattle = A.bp(r.standard_normal(n), 900, 4500) * env(n, 0.004, 0.09) * 0.35 * (1 + 0.6 * np.sin(2 * np.pi * 31 * t))
    glass = sum(np.sin(2 * np.pi * f * t) * env(n, 0.001, d) * a for f, d, a in ((1420, 0.12, 0.05), (2310, 0.08, 0.035), (3170, 0.06, 0.02)))
    return A._peaknorm(knock + hit + rattle + glass, 0.6)


def _formants(x):
    return A.bp(x, 650, 1300) * 0.9 + A.bp(x, 1000, 2600) * 0.45 + A.bp(x, 2400, 3400) * 0.15


def sigh():
    # breathy exhale: noise through 'ah' -> 'h' formants, falling level and brightness, plus a soft voiced layer
    # (a glottal pulse train falling 135 -> 105 Hz through the same formants, ~10 dB under the breath) so it
    # reads as a human sigh rather than an air puff. Peaks ~0.12-0.2 s after the cue, decays over ~0.6 s.
    n = int(1.05 * SR)
    t = np.arange(n) / SR
    x = rng.standard_normal(n)
    ah = _formants(x)
    e = np.minimum(1, t / 0.12) ** 1.5 * np.exp(-np.maximum(0, t - 0.18) / 0.32)
    tilt = A.lp(ah, 2400) * (t < 0.45) + A.lp(ah, 1400) * (t >= 0.45)
    y = tilt * e
    f0 = 135.0 - 30.0 * np.clip(t / 0.6, 0, 1)
    ph = np.cumsum(f0) / SR
    pulses = np.maximum(0, np.sin(2 * np.pi * ph)) ** 6           # soft glottal pulses (rich in harmonics)
    pulses = pulses - pulses.mean()
    ve = np.minimum(1, t / 0.08) * np.exp(-np.maximum(0, t - 0.12) / 0.2)   # voicing fades faster than the air
    voiced = A.lp(_formants(pulses) + 0.3 * A.bp(pulses, 100, 400), 2200) * ve
    voiced *= A.undb(-10) * np.sqrt(np.mean(y ** 2)) / (np.sqrt(np.mean(voiced ** 2)) + 1e-12)
    return A._peaknorm(A.lp(y + voiced, 3000), 0.35)


def inhale():
    # a soft nasal in-breath before the sigh: high-ish noise swelling up over ~0.3 s, cut off by the hold
    n = int(0.42 * SR)
    t = np.arange(n) / SR
    x = A.bp(rng.standard_normal(n), 900, 4200) * 0.7 + A.bp(rng.standard_normal(n), 2500, 6000) * 0.3
    e = np.sin(np.pi / 2 * np.clip(t / 0.3, 0, 1)) ** 2 * np.clip((0.42 - t) / 0.1, 0, 1)
    return A._peaknorm(x * e, 0.3)


def shop_bell():
    # the cheerful bell on the door: a small brass bell shaken by its clapper, 6 quick strikes over ~0.6 s.
    # Each strike = a 2-4 ms metal clapper tick (band-passed noise, 2-8 kHz) + the bell's ring. Strikes are detuned
    # by about +-20 cents (a swinging bell is never struck twice the same way) and each re-strike damps what is
    # still ringing from the previous one, so strikes no longer cancel each other. Short ring (decay 0.25), and
    # the whole bell fades out by 0.98 s (cue 15.92 -> silent by ~16.9), well inside its 1.2 s buffer (no hard cut).
    n = int(1.2 * SR)
    out = np.zeros(n)
    r = np.random.default_rng(31)
    strikes = [(0.0, 'E6', 0.8, +18), (0.09, 'G#6', 0.6, -20), (0.2, 'E6', 0.55, -15), (0.31, 'G#6', 0.45, +22),
               (0.44, 'E6', 0.35, +12), (0.6, 'G#6', 0.25, -16)]
    ring = []
    for i, (dt, note, v, cents) in enumerate(strikes):
        b = np.array(MS.bell(MS.midi(note) + cents / 100.0, vel=v, kind='hand', hardness=0.75, decay=0.25, seed=i))
        i0 = int(dt * SR)
        seg = np.zeros(n)
        m = min(len(b), n - i0)
        seg[i0:i0 + m] = b[:m]
        nk = int(r.uniform(0.002, 0.004) * SR)                       # clapper tick
        tick = A.bp(r.standard_normal(nk + 400), 2000, 8000)[400:] * np.exp(-np.arange(nk) / (0.0009 * SR))
        tick *= 0.9 * v / (np.max(np.abs(tick)) + 1e-9)
        seg[i0:i0 + nk] += tick
        ring.append((i0, seg))
    for k, (i0, seg) in enumerate(ring):
        if k + 1 < len(ring):                                        # damped (not cancelled) by the next strike
            j0 = ring[k + 1][0]
            u = np.arange(n - j0) / SR
            seg[j0:] *= 0.35 + 0.65 * np.exp(-u / 0.03)
        out += seg
    t = np.arange(n) / SR
    out *= 0.5 + 0.5 * np.cos(np.pi * np.clip((t - 0.7) / 0.28, 0, 1))  # ring fades out 0.70 -> 0.98 s
    return A._peaknorm(out, 0.5)


def slide_door():
    # automatic sliding door: soft motor hum + air, 0.45 s
    n = int(0.75 * SR)
    t = np.arange(n) / SR
    e = np.sin(np.pi * np.clip(t / 0.5, 0, 1)) ** 1.5
    hum = (np.sin(2 * np.pi * 118 * t) + 0.4 * np.sin(2 * np.pi * 236 * t)) * 0.25
    air = A.bp(rng.standard_normal(n), 400, 2600) * 0.5
    thunk = np.sin(2 * np.pi * 70 * t) * env(n, 0.002, 0.05) * (t > 0.48) * 0.0
    return A._peaknorm((hum + air) * e + thunk, 0.4)


def latch_click():
    # the clean click of a latch releasing + a light spring
    n = int(0.35 * SR)
    t = np.arange(n) / SR
    c1 = A.bp(rng.standard_normal(n), 2500, 9000) * env(n, 0.0004, 0.006)
    c2 = np.zeros(n); k = int(0.028 * SR); c2[k:] = (A.bp(rng.standard_normal(n), 1500, 7000) * env(n, 0.0004, 0.008))[:n - k]
    tone = sum(np.sin(2 * np.pi * f * t) * env(n, 0.0005, d) * a for f, d, a in ((2900, 0.05, 0.12), (4350, 0.03, 0.06), (880, 0.06, 0.1)))
    return A._peaknorm(c1 + 0.7 * c2 + tone, 0.6)


def street_bed():
    # dusk high street: distant traffic rumble + murmur of people + far car passes + a soft wind
    t = np.arange(N) / SR
    rumble = A.lp(rng.standard_normal(N), 260) * (1 + 0.35 * np.sin(2 * np.pi * 0.07 * t))
    murmur = A.bp(rng.standard_normal(N), 300, 2200)
    syl = np.clip(np.convolve(rng.standard_normal(N // 480 + 2), np.ones(3) / 3, 'same'), -2, 2)
    syl_env = np.interp(t, np.arange(len(syl)) * 0.01, np.abs(syl))
    murmur = A.lp(murmur * (0.35 + 0.65 * syl_env), 1800) * 0.25
    mono = rumble * 0.8 + murmur
    st = np.stack([mono, np.roll(mono, int(0.011 * SR))], 1)
    return st


def build():
    buf = np.zeros((N, 2))
    cues = []

    def cue(t, name, gain_db=0.0, pan=0.0, **p):
        x, h = cat(name, **p)
        place(buf, x, t, gain_db, pan, h)
        cues.append(dict(t=round(t, 3), name=name, gain_db=gain_db))

    def custom(t, label, x, gain_db=0.0, pan=0.0, hit=0.0):
        place(buf, x, t, gain_db, pan, hit)
        cues.append(dict(t=round(t, 3), name=label, gain_db=gain_db))

    # street bed: under the street scenes, out on the hard cut, back for the replay, low under the end card
    bed = street_bed()
    lvl = np.zeros(N)
    t = np.arange(N) / SR
    lvl += (t < 21.0)
    lvl += ((t >= T_REW) & (t < 30.6)) * 0.9
    lvl += (t >= 30.6) * np.clip(1 - (t - 30.6) / 0.8, 0.35, 1) * 1.0
    lvl = np.convolve(lvl, np.ones(int(0.04 * SR)) / int(0.04 * SR), 'same')
    bedx = bed * lvl[:, None]
    bedx *= A.undb(-34 - A.loudness(bedx.astype(np.float32)))
    for tc, d in ((2.2, 1), (11.0, -1), (16.8, 1), (28.4, -1)):
        x, h = cat('whoosh_by', dur=2.2, speed=40.0, dist=4.0, direction=d)
        place(bedx, A.lp(x, 2500), tc, -20, 0, h)

    # footsteps (heel strikes from the film's walk cycle) + her step back from the door
    # steps.json is read at run time (re-probed from the street rig); the two hand-placed step-back heels are
    # only used where the probe has no heel strike within 0.12 s of them, so they are never doubled.
    steps = json.load(open(os.path.join(HERE, 'steps.json')))
    for i, s in enumerate(steps):
        g = -13 if not s['inside'] else -17
        custom(s['t'], 'heel', heel(i, 1.0), g, pan=-0.1 + 0.2 * (s['x'] > 600))
    for tt in (12.66, 12.86):
        if any(abs(s['t'] - tt) < 0.12 for s in steps):
            continue
        custom(tt, 'heel', heel(40 + int(tt * 10), 0.8), -15)

    # beat 1: found + wants to buy
    cue(0.35, 'pop', -4, 0.15, pitch=1.25); cue(0.55, 'sparkle', -12, 0.15)
    cue(1.95, 'bubble_pop', -5, 0.1, pitch=1.1)
    # beat 2: the push-in, the pushes, the spinner
    cue(3.9, 'air_zoom', -10)
    custom(4.45, 'door_thud', door_thud(1), -4)
    custom(6.17, 'door_thud', door_thud(2), -3)
    cue(4.99, 'toggle_on', -14)     # under "open." (4.99-5.37): kept low, no ui_hover breath
    # the faint looping loading tick, from the spinner's appearance to the cut
    tick = cat('ui_tick', pitch=1.6)[0]
    tt = 5.25
    k = 0
    while tt < 21.0:
        g = -21 if 8.0 <= tt < 13.0 else -25
        place(buf, tick, tt, g, 0.05 if k % 2 else -0.05)
        tt += 0.25; k += 1
    cues.append(dict(t=5.25, name='loading tick loop (4 Hz) to 21.0', gain_db=-25))
    # beat 3: pull back, counter ticks, watch, sigh
    cue(7.95, 'whoosh_slow', -14, 0, direction=-1)
    for s in (9.0, 10.0, 11.0):          # the counter stops at 0:03
        cue(s, 'ui_click', -6, 0.35, pitch=0.9)
    cue(9.3, 'leaf_rustle', -24, dur=0.4)
    custom(11.62, 'inhale', inhale(), -20, 0, 0.0)     # shoulders rise 11.6-11.95
    custom(11.97, 'sigh', sigh(), -9, 0, 0.0)          # exhale peaks ~12.1 on the visible slump (12.0-12.4)
    # beat 4: across the road; shop B's door glides, its bell rings
    door_b = 16.22 - 0.42
    custom(door_b, 'slide_door', slide_door(), -13, 0.2)
    custom(door_b + 0.12, 'shop_bell', shop_bell(), -17, 0.25)
    cue(16.3, 'ripple', -18, 0.2)   # route ring at arrival
    # beat 5: whip back, the browser builds
    cue(18.22, 'whip', -6, 0, direction=-1)
    cue(18.6, 'swish_small', -16)
    for s, p in ((18.9, 1.0), (19.02, 1.12), (19.1, 1.25), (19.3, 0.9)):
        cue(s, 'ui_click', -12, -0.2, pitch=p)
    cue(19.4, 'shimmer', -24, dur=1.4)
    # beat 6: hard cut to black
    cue(21.0, 'sub_drop', -5, dur=2.0); cue(21.0, 'impact_soft', -9)
    # the spinner stalls and reverses (from 24.75) -> hard cut to the rewind at 25.2 (25.2-26.2)
    cue(T_REW, 'reverse_swell', -10, duration=0.55)
    cue(T_REW, 'glitch_short', -14)
    for d, tc in ((-1, 25.5), (1, 25.85)):
        cue(tc, 'whoosh_fast', -11, 0, direction=d)
    cue(26.2, 'downlifter', -17, dur=0.6)
    # beat 7: the door opens the instant she touches it
    cue(27.02, 'glass_tap', -14, pitch=1.2)
    custom(T_FAST, 'latch_click', latch_click(), -3)
    cue(T_FAST + 0.02, 'check_ding', -7, 0, pitch=1.0)
    cue(T_FAST + 0.05, 'whoosh_slow', -15, 0.2, direction=1)
    cue(27.4, 'swish_small', -14, -0.2)
    cue(27.74, 'pop', -10, -0.2, pitch=1.3)
    cue(27.92, 'check_ding', -12, 0, pitch=1.12)
    cue(28.64, 'check_ding', -12, 0.2, pitch=1.26)
    cue(28.75, 'ui_hover', -16)     # the Core Web Vitals line fades in 28.75-29.05
    # beat 8: shrink to the card, CTA, typing, logo, click
    cue(31.0, 'whoosh_slow', -11, 0, direction=-1)    # peak on the fastest shrink frames (30.93-31.07)
    cue(31.35, 'card_slide', -14)
    cue(31.93, 'typing', -22, n=10, cps=8.0)
    cue(33.0, 'card_slide', -12)
    cue(33.18, 'pop', -9, 0, pitch=1.15)
    cue(33.4, 'typing', -18, n=34, cps=36.0)
    cue(T_AUDIT + 0.15, 'logo_sting', -9)   # 34.94: the logo lands on "audit."
    cue(34.0, 'ui_hover', -18)
    cue(T_AUDIT, 'ui_click', -4, 0.1, pitch=1.0); cue(T_AUDIT + 0.01, 'toggle_on', -16)

    # the bed and the tick loop sit under the voice
    import soundfile as sf
    vo = sf.read(os.path.join(HERE, 'vo.wav'), dtype='float64')[0]
    vo = vo[:N] if len(vo) >= N else np.vstack([vo, np.zeros((N - len(vo), 2))])
    bedx = A.sidechain(bedx, vo, depth_db=10, attack=0.03, release=0.4)
    out = buf + bedx
    out *= A.undb(-21 - A.loudness(out.astype(np.float32)))
    g = A.limiter_gain(out, ceiling_db=-3.0)
    out *= g[:, None]
    return out.astype(np.float32), cues


T_FAST, T_AUDIT = 27.18, 34.79
T_REW = 25.2        # hard cut to the rewind (film.js T.rew0); the rewind runs 25.2-26.2

if __name__ == '__main__':
    x, cues = build()
    A._write_wav(os.path.join(HERE, 'sfx.wav'), x, bits=24)
    json.dump(cues, open(os.path.join(HERE, 'sfx_cues.json'), 'w'), indent=0)
    print(f'-> audio/sfx.wav  {len(cues)} cues  {A.loudness(x):.1f} LUFS  TP {A.true_peak(x):.1f} dBTP')
