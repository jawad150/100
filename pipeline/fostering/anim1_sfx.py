"""anim1_sfx.py: SFX for ANIM 1 "DAY IN THE LIFE" (SFX only, no music) on the 100 BPM grid.

The toolkit catalog (audio.py) has no paper, pencil, bus, kitchen, block or switch sounds, so this module
synthesises them with audio.py's own DSP building blocks and REGISTERS them into audio.SOUNDS at import (same
calibration via audio._finish: max momentary loudness = -20 LUFS + level), so the toolkit mixer (duck_under, room
send, glue, bed, loudness + true-peak limiter) mixes them like catalog sounds:

    type_thump(weight)       stamped type: felt thump + paper slap          hit = transient
    paper_rustle(dur)        crinkly sheet handling                         hit = 0.3 * dur
    paper_slide(dur)         sheet sliding over sheet, soft landing "thup"   hit = END (lands on t)
    paper_flip(dur)          page flipped up and away (flap + crinkle + air) hit = flap peak
    pencil_scribble(dur)     graphite looping on paper                      align='start'
    pen_write(dur, rate)     felt-tip handwriting                           align='start'
    marker_swipe(dur)        felt marker swish with a faint squeak          align='start'
    backpack_thud            fabric bag landing + zip-pull jingle           hit = transient
    zip(dur)                 short zip                                      align='start'
    bus_pass(dur)            toy bus putters past (doppler, pan) + friendly double beep; hit = the pass
    bowl_clink               ceramic bowl clink + whisk-wire rattle          hit = transient
    flour_puff               soft puff of air / flour                       hit = transient
    cupcake_plop             soft squishy landing                           hit = transient
    oven_ding                kitchen-timer bell                             hit = transient
    block_clack(pitch)       toy block knock                                hit = transient
    clock_tick(n)            tick-tock                                      hit = first tick
    clock_rattle(dur)        brief alarm-bell rattle                        hit = transient
    light_switch             two-stage switch click                         hit = the snap

    cues() -> the reel's cue list (anim1.cues() returns it)
    build(out_dir=None) -> report: mixes workspace3/audio/anim1_sfx.wav + anim1_sfx_stem.wav (48 kHz 24-bit),
        -18 LUFS integrated, <= -2.0 dBTP (the toolkit default ceiling is -1.5; this brief asks for -2.0).
    Importing also wraps audio.build_reel so that render.py's automatic mix of 'anim1' uses tp_ceiling=-2.0.

    python3 anim1_sfx.py build      -> writes the mix + stem, prints the loudness report, mix overview PNG
    python3 anim1_sfx.py play NAME  -> out/selftest/anim1_sfx_<NAME>.wav
"""
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)
import audio as A  # noqa: E402
from audio import SR, _t, _ar, _rng, _unit, bp, lp, hp, osc, modal, _finish, reverb, pan, decorrelate, \
    _sat, _taper, _st, bass_enhance, reson  # noqa: E402

BPM = 100
BEAT = 0.6


def B(n):
    return n * BEAT


def _n(d):
    return int(round(d * SR))


def _crinkle(d, rng, rate, lo=1500.0, hi=9500.0, env=None):
    """Paper crinkle: Poisson clicks (lognormal amplitudes) band-passed into tiny crackles."""
    n = _n(d)
    imp = np.zeros(n)
    k = max(1, rng.poisson(rate * d))
    pos = rng.integers(0, n, k)
    amp = rng.lognormal(0, 0.9, k) * rng.choice([-1.0, 1.0], k)
    if env is not None:
        amp = amp * env[pos]
    np.add.at(imp, pos, amp)
    x = bp(imp, lo, hi, 2)
    x = x + 0.5 * reson(imp * 0.3, rng.uniform(2500, 4200), 6.0)
    return x


def _reg(cat, char, use, send=None):
    def deco(fn):
        if fn.__name__ not in A.SOUNDS:
            A._register(cat, char, use, send)(fn)
        return fn
    return deco


# ============================================================================================ sounds
@_reg('impact', 'stamped type: felt thump + paper slap', 'type stamps / slams on paper (anim1)', send=-24)
def type_thump(seed=0, weight=1.0):
    r = _rng(seed, 'type_thump')
    d = 0.7
    t = _t(d)
    th = A._thump(d, 64.0 + 14.0 / weight, 55.0, 0.022, 0.06 + 0.03 * weight, r, attack=0.0015, drive=2.4,
                  noise=0.35, noise_lp=650.0)
    slap = _unit(bp(r.standard_normal(len(t)), 900, 5200)) * _ar(t, 0.0004, 0.010) * 0.20
    paper = _crinkle(d, r, 900, env=_ar(t, 0.001, 0.03)) * 0.05
    x = bass_enhance(th * min(weight, 1.6), 1.0, fc=110.0, band=(170.0, 700.0), drive=5.0) * 0.8 + slap + paper
    st = reverb(decorrelate(x, r, 0.15), 'room', wet_db=-17)
    return _finish(st, 0.0015, -5.0 + 2.0 * (weight - 1.0), 'type_thump')


@_reg('texture', 'crinkly paper handling: crackles + soft friction', 'sheet settles, paper moves (anim1)', send=-20)
def paper_rustle(seed=0, dur=0.7):
    r = _rng(seed, 'paper_rustle')
    t = _t(dur)
    env = np.sin(np.pi * np.clip(t / dur, 0, 1)) ** 1.5
    cr = _crinkle(dur, r, 700, env=env)
    fr = _unit(bp(r.standard_normal(len(t)), 700, 4500)) * env * 0.06
    x = _st(cr * 0.5 + fr)
    x = decorrelate(x, r, 0.4)
    return _finish(x, 0.3 * dur, -12.0, 'paper_rustle')


@_reg('transition', 'sheet slides over sheet, landing thup', 'paper slide transitions (anim1)', send=-20)
def paper_slide(seed=0, dur=0.34):
    r = _rng(seed, 'paper_slide')
    d = dur + 0.35
    t = _t(d)
    u = np.clip(t / dur, 0, 1)
    env = (u ** 1.2) * (1 - u) ** 0.35 * (t < dur)
    env = A._smooth(env, 0.004)
    fr = noise = _unit(bp(r.standard_normal(len(t)), 500, 5200)) * env * 0.35
    fr = fr + _unit(bp(r.standard_normal(len(t)), 150, 600)) * env * 0.12
    cr = _crinkle(d, r, 260, env=env) * 0.25
    land = A._thump(d, 90.0, 40.0, 0.01, 0.035, r, attack=0.002, drive=1.6, noise=0.5, noise_lp=900.0)
    land = np.roll(land, _n(dur)) * 0.5
    land[:_n(dur)] = 0
    pad = _unit(bp(r.standard_normal(len(t)), 300, 2500)) * _ar(t, 0.001, 0.02, dur) * 0.15
    x = pan(_st(fr + cr + land + pad), np.linspace(0.6, -0.1, len(t)))
    x = reverb(x, 'room', wet_db=-18)
    return _finish(x, dur, -8.0, 'paper_slide')


@_reg('transition', 'page flipped up and away: flap, crinkle, air', 'page flips (anim1)', send=-18)
def paper_flip(seed=0, dur=0.5):
    r = _rng(seed, 'paper_flip')
    d = dur + 0.3
    t = _t(d)
    tp = 0.4 * dur
    sw = A._swell(t, tp, k=1.6, tau=0.09)
    flap = _unit(lp(r.standard_normal(len(t)), 1400, 2)) * sw * (0.75 + 0.25 * np.sin(TWO * 18 * t)) * 0.35
    air = _unit(bp(r.standard_normal(len(t)), 900, 7000)) * sw * 0.12
    cr = _crinkle(d, r, 500, env=_ar(t, 0.01, 0.12)) * 0.3
    x = pan(_st(flap + air + cr), np.linspace(-0.2, 0.3, len(t)))
    x = reverb(x, 'room', wet_db=-16)
    return _finish(x, tp, -8.0, 'paper_flip')


TWO = 2 * np.pi


def _stroke_env(t, rate, rng, smooth=0.006):
    ph = TWO * np.cumsum(rate * (1 + 0.12 * np.sin(TWO * 0.9 * t + rng.uniform(0, 6)))) / SR
    e = np.abs(np.sin(ph)) ** 0.7
    return A._smooth(e, smooth)


@_reg('texture', 'graphite pencil scribbling on paper', 'pencil scribble (anim1 HOMEWORK)', send=-22)
def pencil_scribble(seed=0, dur=0.75, rate=7.0):
    r = _rng(seed, 'pencil_scribble')
    d = dur + 0.05
    t = _t(d)
    gate = np.clip(t / 0.02, 0, 1) * np.clip((dur - t) / 0.05, 0, 1)
    e = _stroke_env(t, rate, r) * gate
    scratch = _unit(bp(r.standard_normal(len(t)), 2200, 9000)) * e * 0.30
    grain = _crinkle(d, r, 3500, lo=3000, hi=11000, env=e) * 0.10
    body = _unit(bp(r.standard_normal(len(t)), 250, 900)) * e * 0.06
    x = decorrelate(_st(scratch + grain + body), r, 0.2)
    return _finish(x, 0.0, -11.0, 'pencil_scribble', keep_until=dur)


@_reg('texture', 'felt-tip handwriting: soft glides', 'handwritten write-ons (anim1)', send=-22)
def pen_write(seed=0, dur=1.0, rate=5.5):
    r = _rng(seed, 'pen_write')
    d = dur + 0.05
    t = _t(d)
    gate = np.clip(t / 0.03, 0, 1) * np.clip((dur - t) / 0.06, 0, 1)
    e = _stroke_env(t, rate, r, 0.012) * gate
    glide = _unit(bp(r.standard_normal(len(t)), 900, 5200)) * e * 0.25
    sq = reson(r.standard_normal(len(t)) * e, 2600 + 300 * np.sin(TWO * 0.7 * t).mean(), 18) * 0.02
    x = decorrelate(_st(glide + sq), r, 0.2)
    return _finish(x, 0.0, -15.0, 'pen_write', keep_until=dur)


@_reg('transition', 'felt marker swish with a faint squeak', 'highlighter swipe (anim1)', send=-18)
def marker_swipe(seed=0, dur=0.32):
    r = _rng(seed, 'marker_swipe')
    d = dur + 0.1
    t = _t(d)
    env = A._swell(t, dur * 0.55, k=1.4, tau=0.06)
    sw = _unit(bp(r.standard_normal(len(t)), 700, 6500)) * env * 0.3
    f = 1900 + 900 * np.clip(t / dur, 0, 1)
    squeak = osc(f) * env * 0.03 * (1 + 0.5 * np.sin(TWO * 33 * t))
    x = pan(_st(sw + squeak), np.linspace(-0.5, 0.5, len(t)))
    return _finish(x, 0.0, -10.0, 'marker_swipe', keep_until=dur)


@_reg('impact', 'fabric bag landing + zip-pull jingle', 'backpack drop (anim1)', send=-22)
def backpack_thud(seed=0):
    r = _rng(seed, 'backpack_thud')
    d = 0.8
    t = _t(d)
    th = A._thump(d, 58.0, 45.0, 0.02, 0.09, r, attack=0.003, drive=2.0, noise=0.6, noise_lp=500.0)
    fab = _unit(bp(r.standard_normal(len(t)), 300, 3200)) * _ar(t, 0.002, 0.05) * 0.22
    jing = np.zeros(len(t))
    for k in range(4):
        t0 = 0.02 + k * r.uniform(0.025, 0.05)
        jing += modal(d, [r.uniform(3800, 4600), r.uniform(6200, 7400)], [0.03, 0.015], [0.5, 0.3], r, t0=t0) * 0.2
    x = bass_enhance(th, 1.0, fc=100.0, band=(160.0, 650.0), drive=5.0) * 0.8 + fab + jing * 0.5
    st = reverb(decorrelate(x, r, 0.2), 'room', wet_db=-16)
    return _finish(st, 0.003, -4.0, 'backpack_thud')


@_reg('texture', 'short zip', 'bags (anim1)', send=-20)
def zip(seed=0, dur=0.3):
    r = _rng(seed, 'zip')
    d = dur + 0.05
    t = _t(d)
    rate = 90 + 160 * np.clip(t / dur, 0, 1)
    ph = np.cumsum(rate) / SR
    teeth = (np.diff(np.floor(ph), prepend=0) > 0).astype(np.float64)
    teeth *= r.lognormal(0, 0.3, len(t))
    x = bp(teeth, 2000, 7500) * (t < dur)
    x = x + _unit(bp(r.standard_normal(len(t)), 1500, 6000)) * 0.03 * (t < dur)
    return _finish(_st(x), 0.0, -13.0, 'zip', keep_until=dur)


@_reg('transition', 'toy bus putters past with doppler + a friendly double beep', 'school bus (anim1)', send=-18)
def bus_pass(seed=0, dur=1.15, beep=True):
    r = _rng(seed, 'bus_pass')
    d = dur + 0.4
    t = _t(d)
    tp = 0.5 * dur
    # doppler: pitch ratio falls through the pass
    dop = 1.0 + 0.08 * np.tanh((tp - t) / 0.12)
    f0 = 26.0 * dop
    ph = TWO * np.cumsum(f0) / SR
    pulses = np.maximum(np.sin(ph), 0) ** 8
    eng = lp(pulses, 900, 2) + 0.4 * bp(pulses, 200, 1800)
    eng = _unit(eng)
    rum = _unit(lp(r.standard_normal(len(t)), 220, 2)) * 0.5
    env = np.exp(-((t - tp) / (0.36 * dur)) ** 2)
    tyre = _unit(bp(r.standard_normal(len(t)), 600 * dop.mean(), 3500)) * env * 0.12
    x = (eng * 0.6 + rum * 0.25) * env + tyre
    x = _sat(x / (np.max(np.abs(x)) + 1e-9) * 0.9, 1.6)
    st = pan(_st(x), np.clip((t - tp) / (0.45 * dur), -0.85, 0.85))
    if beep:
        bt = np.zeros(len(t))
        for k, (tb, f) in enumerate(((tp - 0.30, 523.0), (tp - 0.16, 659.0))):
            u = t - tb
            g = (u >= 0) & (u < 0.085)
            env_b = np.where(g, np.sin(np.pi * np.clip(u / 0.085, 0, 1)) ** 0.3, 0.0)
            tone = np.sign(np.sin(TWO * f * u)) * 0.5 + np.sin(TWO * f * 2 * u) * 0.2
            bt += lp(tone * env_b, 2400, 2) * 0.22
        st = st + pan(_st(bt), -0.2)
    st = reverb(st, 'room', wet_db=-15)
    return _finish(st, tp, -7.0, 'bus_pass')


@_reg('impact', 'ceramic bowl clink + whisk wire rattle', 'mixing bowl lands (anim1)', send=-16)
def bowl_clink(seed=0):
    r = _rng(seed, 'bowl_clink')
    d = 1.2
    t = _t(d)
    cer = modal(d, [1180, 2960, 4710, 6640], [0.32, 0.16, 0.09, 0.05], [0.55, 0.35, 0.22, 0.12], r, split=2.0,
                contact=0.0006)
    knock = A._thump(d, 140.0, 60.0, 0.01, 0.03, r, attack=0.001, drive=1.5, noise=0.3, noise_lp=1200.0) * 0.4
    wires = np.zeros(len(t))
    for k in range(7):
        t0 = 0.012 + k * r.uniform(0.012, 0.03)
        wires += modal(d, [r.uniform(5200, 7600), r.uniform(8800, 11000)], [0.02, 0.01], [0.4, 0.2], r, t0=t0)
    x = cer * 0.6 + knock + wires * 0.12
    st = reverb(decorrelate(x, r, 0.2), 'room', wet_db=-14)
    return _finish(st, 0.0006, -7.0, 'bowl_clink')


@_reg('texture', 'soft puff of air / flour', 'flour puffs, morph poofs (anim1)', send=-18)
def flour_puff(seed=0):
    r = _rng(seed, 'flour_puff')
    d = 0.55
    t = _t(d)
    x = _unit(lp(r.standard_normal(len(t)), 1700, 2)) * _ar(t, 0.006, 0.08) * 0.4
    x += _unit(bp(r.standard_normal(len(t)), 2000, 7000)) * _ar(t, 0.01, 0.12) * 0.08
    st = decorrelate(_st(x), r, 0.5)
    return _finish(st, 0.006, -12.0, 'flour_puff')


@_reg('impact', 'soft squishy landing', 'cupcake drop (anim1)', send=-22)
def cupcake_plop(seed=0):
    r = _rng(seed, 'cupcake_plop')
    d = 0.5
    t = _t(d)
    th = A._thump(d, 110.0, 70.0, 0.015, 0.04, r, attack=0.002, drive=1.6, noise=0.5, noise_lp=1100.0)
    sq = _unit(bp(r.standard_normal(len(t)), 500, 2500)) * _ar(t, 0.004, 0.03) * 0.15
    x = th * 0.7 + sq
    return _finish(reverb(_st(x), 'room', wet_db=-17), 0.002, -9.0, 'cupcake_plop')


@_reg('ui', 'kitchen-timer bell ding', 'oven timer (anim1 BAKING)', send=-12)
def oven_ding(seed=0):
    r = _rng(seed, 'oven_ding')
    d = 2.2
    t = _t(d)
    bell = modal(d, [2093, 2093 * 2.76, 2093 * 5.4], [0.9, 0.35, 0.15], [0.6, 0.25, 0.1], r, split=3.0,
                 contact=0.0004)
    click = _unit(bp(r.standard_normal(len(t)), 2500, 9000)) * _ar(t, 0.0002, 0.002) * 0.15
    st = reverb(_st(bell + click), 'room', wet_db=-14)
    return _finish(st, 0.0004, -10.0, 'oven_ding')


@_reg('impact', 'toy block knock (plastic / wood)', 'block stacks (anim1)', send=-20)
def block_clack(seed=0, pitch=1.0):
    r = _rng(seed, 'block_clack')
    d = 0.5
    t = _t(d)
    m = modal(d, [720 * pitch, 1650 * pitch, 2900 * pitch, 4300 * pitch], [0.05, 0.03, 0.018, 0.01],
              [0.6, 0.4, 0.25, 0.12], r, contact=0.0004)
    clk = _unit(bp(r.standard_normal(len(t)), 2000, 8000)) * _ar(t, 0.0002, 0.003) * 0.25
    body = A._thump(d, 105.0 * pitch, 50.0, 0.01, 0.03, r, attack=0.001, drive=1.8, noise=0.3, noise_lp=800.0)
    x = m * 0.7 + clk + body * 0.5
    st = reverb(decorrelate(x, r, 0.15), 'room', wet_db=-16)
    return _finish(st, 0.0004, -6.0, 'block_clack')


@_reg('ui', 'clock tick-tock', 'alarm clock, routine (anim1)', send=-20)
def clock_tick(seed=0, n=4, interval=0.3):
    r = _rng(seed, 'clock_tick')
    d = n * interval + 0.2
    t = _t(d)
    x = np.zeros(len(t))
    for k in range(n):
        f = 3300 if k % 2 == 0 else 2700
        x += modal(d, [f, f * 1.9], [0.012, 0.006], [0.5, 0.25], r, t0=k * interval, contact=0.0002)
        x += _unit(bp(r.standard_normal(len(t)), 3000, 9000)) * _ar(t, 0.0001, 0.0015, k * interval) * 0.08
    return _finish(reverb(_st(x), 'room', wet_db=-18), 0.0002, -13.0, 'clock_tick', keep_until=d - 0.2)


@_reg('ui', 'brief alarm-bell rattle', 'alarm clock landing (anim1)', send=-16)
def clock_rattle(seed=0, dur=0.45):
    r = _rng(seed, 'clock_rattle')
    d = dur + 0.6
    t = _t(d)
    x = np.zeros(len(t))
    k = 0
    tt = 0.0
    while tt < dur:
        f = 2350 if k % 2 == 0 else 2610
        x += modal(d, [f, f * 2.7], [0.09, 0.03], [0.5, 0.15], r, t0=tt, contact=0.0002) * (1 - 0.6 * tt / dur)
        tt += 1.0 / 26.0
        k += 1
    st = reverb(decorrelate(x, r, 0.2), 'room', wet_db=-15)
    return _finish(st, 0.0002, -14.0, 'clock_rattle')


@_reg('ui', 'two-stage light-switch click', 'window lights up (anim1)', send=-18)
def light_switch(seed=0):
    r = _rng(seed, 'light_switch')
    d = 0.3
    t = _t(d)
    pre = _unit(bp(r.standard_normal(len(t)), 1500, 7000)) * _ar(t, 0.0002, 0.002) * 0.12
    snap = modal(d, [1850, 3900, 6100], [0.012, 0.006, 0.003], [0.6, 0.3, 0.15], r, t0=0.014, contact=0.0002)
    snap += _unit(bp(r.standard_normal(len(t)), 2000, 9000)) * _ar(t, 0.0001, 0.003, 0.014) * 0.3
    thock = A._thump(d, 170.0, 60.0, 0.006, 0.02, r, attack=0.0008, drive=1.4, noise=0.2, noise_lp=900.0)
    thock = np.roll(thock, _n(0.014)) * 0.3
    x = pre + snap + thock
    return _finish(reverb(_st(x), 'room', wet_db=-17), 0.014, -8.0, 'light_switch')


# ============================================================================================ cue sheet
def cues():
    c = []

    def q(t, name, gain_db=0.0, pan_=0.0, align='hit', **params):
        c.append(dict(t=round(float(t), 4), name=name, gain_db=gain_db, pan=pan_, align=align, params=params))

    # ---- FRAME 1: hook (stamped words), brackets, swipe + light streak, handwriting, alarm clock
    q(0.0, 'paper_rustle', -4, 0.0, 'start', dur=0.6)
    for k, (tb, w, p) in enumerate(((B(0), 1.25, -0.2), (B(0.5), 1.0, 0.15), (B(1), 1.5, 0.0),
                                    (B(1.5), 0.95, -0.15), (B(1.75), 0.9, 0.1), (B(2), 1.1, 0.2))):
        q(tb, 'type_thump', 0.0, p, weight=w)
    q(B(1), 'impact_soft', -5)
    q(B(0), 'impact_soft', -8)
    q(B(2.5) + 0.02, 'ui_click', -3, -0.45)
    q(B(2.5) + 0.05, 'ui_click', -4, 0.45, pitch=1.12)
    q(B(3), 'marker_swipe', 0, 0.0, 'start', dur=0.32)
    q(B(3) + 0.15, 'shimmer', -9)
    q(B(4), 'pen_write', 0, -0.1, 'start', dur=1.15, rate=5.0)
    q(B(4) + 0.15, 'clock_rattle', 0, 0.05)            # the alarm clock's bells rattle once
    q(B(4) + 0.9, 'clock_tick', -5, 0.05, n=6, interval=0.3)
    q(3.62, 'pen_write', -2, 0.25, 'start', dur=0.4, rate=7.0)
    # slide to sheet B
    q(5.40, 'paper_slide', 0, 0.0, dur=0.34)
    # ---- FRAME 2: list + props
    q(B(9), 'type_thump', 0, -0.2, weight=1.15)
    q(5.70, 'backpack_thud', 0, -0.35)
    q(5.86, 'zip', -4, -0.35, 'start', dur=0.22)
    q(5.72, 'pen_write', -8, -0.2, 'start', dur=0.85, rate=4.0)   # dashed route drawn on
    q(6.52, 'bus_pass', 0, 0.0, dur=1.15)
    q(B(12), 'type_thump', 0, -0.1, weight=1.1)
    q(7.38, 'backpack_thud', -5, 0.35)
    q(7.38, 'paper_rustle', -8, 0.35, 'start', dur=0.35)
    q(7.50, 'pencil_scribble', 0, 0.3, 'start', dur=0.75, rate=7.5)
    q(B(14), 'type_thump', 0, 0.0, weight=1.15)
    q(8.55, 'bowl_clink', 0, -0.35)
    q(8.56, 'flour_puff', -2, -0.3)
    q(8.85, 'cupcake_plop', 0, 0.35)
    q(B(16), 'oven_ding', -1, 0.3)
    # ---- FRAME 3: list out, morph, blocks, headline, rows
    for k in range(3):
        q(B(17) + 0.05 * k + 0.05, 'swish_small', -5, -0.3 + 0.3 * k)
    for g in range(3):
        tm = B(17) + 0.6 * g + 0.24
        q(tm - 0.1, 'swish_small', -3, 0.0)
        q(tm, 'flour_puff', 0, -0.2 + 0.2 * g)
        q(tm + 0.01, 'sparkle', -12, 0.0)
        q(B(18 + g), 'block_clack', 1.0 if g == 2 else 0.0, 0.0, pitch=(1.0, 1.08, 0.94)[g])
    q(B(18) - 0.04, 'swish_small', -6, 0.2)
    q(B(19) - 0.04, 'swish_small', -6, -0.2)
    q(B(20), 'type_thump', 1, 0.0, weight=1.4)
    q(B(20), 'impact_soft', -6)
    for k in range(3):
        q(B(21 + k), 'pop', -4, -0.35)
        q(B(21 + k) + 0.06, 'ui_tick', -2, 0.1)
    q(B(22) + 0.1, 'clock_tick', -2, -0.3, n=5, interval=0.3)
    # flip to sheet C (evening)
    q(15.42, 'paper_flip', 0, 0.0, dur=0.55)
    # ---- FRAME 4: headline, house, window, handwriting, end card
    for k, tb in enumerate((B(26), B(26.75), B(27.5))):
        q(tb + 0.02, 'swish_small', -6, (-0.2, 0.0, 0.2)[k])
        q(tb + 0.10, 'type_thump', -3, 0.0, weight=0.9 + 0.15 * k)
    q(B(28.25) + 0.15, 'backpack_thud', -3, 0.0)
    q(B(28.25) + 0.15, 'block_clack', -9, 0.0, pitch=0.8)
    q(B(29.75), 'swish_small', -4, 0.0)
    q(B(30) + 0.2, 'whoosh_fast', -12, 0.0)
    q(B(31), 'light_switch', 0, 0.15)
    q(B(31) + 0.03, 'shimmer', -12, 0.0, dur=1.6)
    q(B(31) + 0.02, 'pen_write', -1, 0.0, 'start', dur=0.55, rate=6.0)
    q(19.08, 'pen_write', -3, 0.2, 'start', dur=0.28, rate=8.0)
    q(B(31.5) + 0.15, 'logo_sting', -5)
    q(19.07, 'pop', -4, 0.0)
    return c


# ============================================================================================ build
OUT_NAME = 'anim1'
TP_CEILING = -2.0


def build(out_dir=None, overview=True):
    import anim1
    out_dir = out_dir or A.AUDIO
    os.makedirs(out_dir, exist_ok=True)
    rep = A.mix(cues(), float(anim1.DUR), os.path.join(out_dir, OUT_NAME + '_sfx.wav'),
                os.path.join(out_dir, OUT_NAME + '_sfx_stem.wav'), bed=anim1.BED, bed_gain_db=anim1.BED_GAIN_DB,
                tp_ceiling=TP_CEILING, verbose=True)
    if overview:
        try:
            A.mix_overview(rep, os.path.join(A.OUT, 'anim1', 'anim1_sfx_mix.png'), 'anim1 SFX')
        except Exception as e:   # the overview is a nicety
            print('overview failed:', e)
    return rep


# render.py mixes '<reel>_sfx.wav' through audio.build_reel when the module is newer than the wav; route anim1's
# automatic mix through the -2.0 dBTP ceiling the brief asks for (other reels are untouched).
_orig_build_reel = getattr(A.build_reel, '_anim1_orig', A.build_reel)


def _build_reel(reel, out_dir=None, **kw):
    if reel == OUT_NAME:
        kw.setdefault('tp_ceiling', TP_CEILING)
    return _orig_build_reel(reel, out_dir, **kw)


_build_reel._anim1_orig = _orig_build_reel
A.build_reel = _build_reel


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'build':
        build()
    elif len(sys.argv) > 2 and sys.argv[1] == 'play':
        x = A.sound(sys.argv[2])
        p = os.path.join(A.SELFTEST, 'anim1_sfx_%s.wav' % sys.argv[2])
        A._write_wav(p, np.asarray(x), 24)
        print(p, x.dur, x.hit, A.stats(np.asarray(x, np.float64), x.hit) if hasattr(A, 'stats') else '')
