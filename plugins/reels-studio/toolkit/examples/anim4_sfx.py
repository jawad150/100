"""anim4_sfx.py: extra synthesised SFX for anim4 (ANIM 4 "£447.60: BUT WHAT IS IT FOR?") + its mix. SFX only.

The audio.py catalog lacks a few sounds this reel needs; they are built here from audio.py's own DSP blocks and
registered into audio.SOUNDS at runtime (register(); audio.py itself is not modified), so cues can name them like
any catalog sound and the mixer's levels / room send / limiter treat them the same way:

    zip_pull       backpack zip: accelerating teeth clicks + friction band, stop tick at the end (hit = the stop)
    fabric_swish   soft cloth swish with a light rustle (hit = the swish peak)
    bus_pass       friendly little bus passing L -> R: engine harmonics with doppler, tyre air, short two-note toot
                   (hit = the closest pass; dur)
    ball_bounce    rubber ball bounce: low thump + hollow 'pock' (pitch; hit = contact)
    paint_dab      wet paint splotch + tiny bubble (hit = contact)
    basket_drop    wicker creak / rustle + soft thud of items landing (hit = the thud)
    house_pop      playful wooden knock + round pop (house / home pop; hit = transient)
    coin_clinks    n sparse coin clinks thinning out over dur (coins pouring into a collector; hit = first clink)
    soft_chime     gentle two-note glassy bell E5 -> B5 with air (end chime; hit = first note)
    airy_bed       light airy bed: soft high air, faint warm body, slow breathing; seamless loop (BED)

    register()                 -> idempotent; called by anim4.cues()
    build(tp=-2.3)             -> mixes anim4.cues() (+ BED) at -18 LUFS, <= -2.3 dBTP (margin for AAC) ->
                                  workspace3/audio/anim4_sfx.wav (24-bit) + anim4_sfx_stem.wav (48 kHz 24-bit)
    python3 anim4_sfx.py build      the reel mix (+ overview PNG in workspace3/out/anim4/)
    python3 anim4_sfx.py audition   every custom sound in sequence -> workspace3/out/anim4/anim4_sfx_audition.wav
    python3 anim4_sfx.py selftest   spectrogram sheet of the custom sounds -> out/selftest/anim4_sfx_sheet_1.png
No side effects on import.
"""
import math
import os
import sys

import numpy as np

import audio as A
from audio import SR, TWO_PI, _t, _n, _rng, _ar, _swell, _taper, _unit, _st, _add, _finish, _sat, osc, pan, bp, \
    lp, hp, modal, fm_bell, reverb, decorrelate, noise_band, colored

CUSTOM = ('zip_pull', 'fabric_swish', 'bus_pass', 'ball_bounce', 'paint_dab', 'basket_drop', 'house_pop',
          'coin_clinks', 'soft_chime', 'airy_bed')


# ------------------------------------------------------------------------------------------- sounds
def zip_pull(seed=0, dur=0.42):
    """Zip (~dur s): teeth clicks accelerating 55 -> 150 Hz over a rising friction band; stop tick. hit = end."""
    r = _rng(seed, 'zip_pull')
    d = dur + 0.25
    N = _n(d)
    x = np.zeros(N)
    tt = 0.0
    k = 0
    while tt < dur:
        p = tt / dur
        rate = 55.0 + 95.0 * p ** 1.3
        g = _t(0.006)
        cl = _unit(bp(r.standard_normal(len(g)), 2200 + 2600 * p, 8500)) * _ar(g, 0.0002, 0.0012)
        cl *= (0.5 + 0.5 * r.random()) * (0.6 + 0.4 * math.sin(math.pi * p))
        _add(x, cl, tt)
        tt += 1.0 / rate * r.uniform(0.85, 1.15)
        k += 1
    t = _t(d)
    fr = noise_band(d, r, [(0, 1700), (dur / d, 3600), (1, 3000)], 0.55)
    fr = fr * np.clip(np.sin(np.pi * np.clip(t / dur, 0, 1)), 0, 1) ** 1.5 * 0.10
    x = x * 0.55 + fr
    stop = _unit(bp(r.standard_normal(_n(0.02)), 1500, 7000)) * _ar(_t(0.02), 0.0002, 0.003) * 0.6
    _add(x, stop, dur)
    st = reverb(pan(x, np.linspace(-0.25, 0.25, N)), 'room', wet_db=-16)
    return _finish(st, dur, -6.0, 'zip_pull', fin=0.0003)


def fabric_swish(seed=0, dur=0.38):
    """Cloth swish (~dur s): band noise sweeping 800 -> 2.4k -> 1.3k Hz, soft swell, light rustle. hit = peak."""
    r = _rng(seed, 'fabric_swish')
    d = dur + 0.2
    t = _t(d)
    tp = 0.45 * dur
    sw = noise_band(d, r, [(0, 800), (tp / d, 2400), (dur / d, 1300), (1, 1100)], 0.9, width=0.4)
    env = _swell(t, tp, k=2.0, tau=0.07)
    x = sw * env[:, None] * 0.45
    cr = A._crackle(d, r, 900, 1500, 6000, env=lambda p: np.interp(p, [0, tp / d, dur / d, 1], [0, 1, 0.2, 0]),
                    gdur=(0.001, 0.004), spread=0.5) * 0.25
    x = x + cr
    st = reverb(x, 'room', wet_db=-18)
    return _finish(st, tp, -7.0, 'fabric_swish', fin=0.002)


def bus_pass(seed=0, dur=1.6):
    """Friendly bus passing L -> R (~dur s): engine harmonics (doppler), tyre air, two-note toot. hit = closest."""
    r = _rng(seed, 'bus_pass')
    d = dur + 0.4
    t = _t(d)
    tc = 0.5 * dur
    u = (t - tc) / (0.32 * dur)
    dop = 1.0 + 0.055 * (-np.tanh(u * 1.6))                  # pitch drops as it passes
    prox = 1.0 / (1.0 + u * u)                                # closeness
    f0 = 52.0 * dop * (1 + 0.04 * np.sin(TWO_PI * 3.1 * t))
    eng = np.zeros(len(t))
    for h, a in ((1, 1.0), (2, 0.7), (3, 0.5), (4, 0.32), (6, 0.18), (8, 0.1)):
        eng += a * osc(f0 * h)
    eng = _sat(lp(eng * 0.4, 1100, 2), 2.2) * prox ** 1.2
    air = noise_band(d, r, 1100, 1.1) * prox ** 1.6 * 0.5
    x = eng * 0.7 + air
    # short friendly toot-toot (cheerful major third), early in the pass
    for k, (f, t0) in enumerate(((392.0, 0.18 * dur), (494.0, 0.18 * dur + 0.14))):
        g = _t(0.12)
        sq = np.sign(np.sin(TWO_PI * f * g)) * 0.5 + np.sin(TWO_PI * f * g)
        sq = lp(sq, 2200, 2) * _ar(g, 0.006, 0.05) * 0.35
        _add(x, sq, t0)
    x = _taper(x * np.clip(t / 0.05, 0, 1), 0.2)
    st = pan(x, np.tanh(u * 1.3) * 0.85)
    st = reverb(st, 'outdoor', wet_db=-14)
    return _finish(st, tc, -4.0, 'bus_pass', fin=0.01)


def ball_bounce(seed=0, pitch=1.0):
    """Rubber ball bounce (~0.4 s): low thump + hollow pock + contact tick. hit = contact."""
    r = _rng(seed, 'ball_bounce')
    d = 0.45
    t = _t(d)
    f = (95.0 + 90.0 * np.exp(-t / 0.012)) * pitch
    thump = _sat(osc(f) * _ar(t, 0.001, 0.07), 1.8)
    pock = modal(d, [520 * pitch, 1240 * pitch, 2010 * pitch], [0.035, 0.018, 0.01], [1.0, 0.45, 0.2], r,
                 contact=0.0006)
    tick = _unit(bp(r.standard_normal(len(t)), 2500, 8000)) * _ar(t, 0.0002, 0.0015) * 0.15
    x = thump * 0.9 + pock * 0.5 + tick
    st = reverb(_st(x), 'room', wet_db=-15)
    return _finish(st, 0.001, -4.0, 'ball_bounce', fin=0.0003)


def paint_dab(seed=0):
    """Wet paint splotch (~0.35 s): squelchy low-passed noise, resonant downward sweep, tiny bubble. hit = 0.004."""
    r = _rng(seed, 'paint_dab')
    d = 0.4
    t = _t(d)
    nz = lp(r.standard_normal(len(t)), 1900, 2) * _ar(t, 0.002, 0.045)
    sweep = noise_band(d, r, [(0, 1300), (0.3, 420), (1, 300)], 0.35) * _ar(t, 0.003, 0.06)
    bub = osc(700 + 900 * (1 - np.exp(-np.maximum(t - 0.05, 0) / 0.02))) * _ar(t, 0.001, 0.025, t0=0.05) * 0.3
    x = _unit(nz) * 0.35 + sweep * 0.45 + bub
    st = reverb(_st(x), 'room', wet_db=-16)
    return _finish(st, 0.004, -7.0, 'paint_dab', fin=0.001)


def basket_drop(seed=0):
    """Wicker creak / rustle + soft thud of items landing (~0.6 s). hit = the thud (0.03 s)."""
    r = _rng(seed, 'basket_drop')
    d = 0.7
    t = _t(d)
    cr = A._crackle(d, r, 1400, 1200, 5500, env=lambda p: np.exp(-p / 0.35), gdur=(0.0015, 0.006), spread=0.6)
    th = A._thump(d, 78.0, 70.0, 0.02, 0.08, r, noise=0.4, noise_lp=400.0, click=0.5)
    knock = modal(d, [310, 690, 1180], [0.05, 0.03, 0.015], [1.0, 0.5, 0.25], r, contact=0.001, t0=0.03)
    x = cr * 0.45 + _st(th * 0.8) + _st(knock * 0.35)
    st = reverb(x, 'room', wet_db=-16)
    return _finish(st, 0.03, -5.0, 'basket_drop', fin=0.001)


def house_pop(seed=0):
    """Playful home pop (~0.5 s): round pop chirp + wooden knock + soft low thump. hit = 0.002."""
    r = _rng(seed, 'house_pop')
    d = 0.6
    t = _t(d)
    f = 300 + 520 * (1 - np.exp(-t / 0.018))
    pp = osc(f) * _ar(t, 0.0015, 0.05) + 0.2 * osc(f * 2.01) * _ar(t, 0.001, 0.025)
    knock = modal(d, [230, 470, 960, 1480], [0.06, 0.04, 0.02, 0.012], [1.0, 0.6, 0.3, 0.15], r, contact=0.0008)
    th = A._thump(d, 70.0, 60.0, 0.02, 0.09, r, noise=0.2)
    x = pp * 0.6 + knock * 0.45 + th * 0.55
    st = reverb(_st(x), 'studio', wet_db=-14)
    return _finish(st, 0.002, -3.0, 'house_pop', fin=0.0004)


def coin_clinks(seed=0, n=7, dur=0.9):
    """n sparse coin clinks thinning out over dur (coins dropping into a collector). hit = first clink."""
    r = _rng(seed, 'coin_clinks')
    d = dur + 0.8
    out = np.zeros((_n(d), 2))
    for k in range(int(n)):
        t0 = 0.0 if k == 0 else min(dur, r.exponential(dur * 0.35))
        f0 = math.exp(r.uniform(math.log(2900), math.log(5200)))
        x = A._coin_ring(0.8, r, f0, tau0=r.uniform(0.08, 0.22), hard=r.uniform(0.9, 1.3), split=r.uniform(2, 7))
        g = r.uniform(0.4, 1.0) * math.exp(-t0 / (dur * 0.6))
        _add(out, pan(x * g, r.uniform(-0.6, 0.6)), t0)
    st = reverb(out, 'plate', wet_db=-15)
    return _finish(st, 0.0005, -9.0, 'coin_clinks', fin=0.0008)


def soft_chime(seed=0):
    """Gentle two-note glassy chime E5 -> B5 with an airy shimmer (~2.5 s). hit = first note."""
    r = _rng(seed, 'soft_chime')
    d = 3.0
    x = fm_bell(d, 659.25, ratio=2.0, index=0.9, tau=1.2, tau_index=0.2, attack=0.004)
    x += 0.8 * fm_bell(d, 987.77, ratio=2.0, index=0.8, tau=1.1, tau_index=0.2, attack=0.004, t0=0.13)
    x += 0.25 * fm_bell(d, 1318.5, ratio=3.0, index=0.5, tau=0.7, tau_index=0.15, attack=0.003, t0=0.13)
    sh = A._grains(d, r, 40, 3500, 9000, 0.02, 0.09, density=lambda p: np.exp(-p / 0.25)) * 0.05
    st = decorrelate(_st(x * 0.5), r, 0.3) + sh
    st = reverb(st, 'hall', wet_db=-9)
    return _finish(st, 0.004, -6.0, 'soft_chime', fin=0.002)


def airy_bed(dur=16.0, seed=0):
    """Light airy bed: soft high air (3-9 kHz), faint warm body, slow breathing; seamless loop. hit = 0."""
    r = _rng(seed, 'airy_bed')
    L = _n(dur)
    x = np.stack([colored(L, r, -3.0, 40, 14000), colored(L, r, -3.0, 40, 14000)], 1)
    x[:, 1] = 0.3 * x[:, 0] + math.sqrt(1 - 0.3 ** 2) * x[:, 1]

    def g(f):
        f = np.maximum(f, 8)
        air = 0.55 * np.exp(-0.5 * (np.log2(f / 5200.0) / 0.9) ** 2)
        body = 0.18 * np.exp(-0.5 * (np.log2(f / 260.0) / 0.7) ** 2)
        sub = 1 / np.sqrt(1 + (70.0 / f) ** 4)
        return (air + body) * sub
    x = A._spec_filter(x, g)
    tl = np.arange(L) / SR
    x *= (1 + 0.18 * A._periodic_lfo(tl, dur, r, 3))[:, None]
    x = A.reverb_circular(x, 'air', wet_db=-6)
    return A._bed_finish(x, 'airy_bed')


_META = dict(
    zip_pull=('ui', 'accelerating zip teeth + friction, stop tick', 'backpack zip (anim4)', -16),
    fabric_swish=('transition', 'soft cloth swish with light rustle', 'clothes sliding (anim4)', -18),
    bus_pass=('transition', 'friendly bus pass L->R with doppler and a short toot', 'bus drives past (anim4)', -14),
    ball_bounce=('ui', 'rubber ball bounce: thump + hollow pock', 'football bounces (anim4)', -16),
    paint_dab=('texture', 'wet paint splotch + tiny bubble', 'paint dab (anim4)', -16),
    basket_drop=('impact', 'wicker rustle + soft thud', 'basket / items landing (anim4)', -16),
    house_pop=('ui', 'playful wooden knock + round pop', 'house / home pop (anim4)', -14),
    coin_clinks=('money', 'sparse coin clinks thinning out', 'coins pouring into a collector (anim4)', -14),
    soft_chime=('texture', 'gentle two-note glassy chime with air', 'end chime (anim4)', -12),
    airy_bed=('bed', 'light airy bed: high air, faint warm body, slow breathing; seamless', 'anim4 bed', None),
)


def register():
    """Register the custom sounds into audio.SOUNDS (idempotent; does not modify audio.py)."""
    g = globals()
    for name in CUSTOM:
        if name in A.SOUNDS and A.SOUNDS[name].get('fn') is g[name]:
            continue
        cat, ch, use, send = _META[name]
        A._register(cat, ch, use, send=send)(g[name])


# ------------------------------------------------------------------------------------------- build
def build(tp=-2.3, verbose=True, overview=True):
    """Mix anim4.cues() + BED into workspace3/audio/anim4_sfx.wav (+ _stem.wav), -18 LUFS, <= tp dBTP."""
    import core as K
    import anim4
    register()
    os.makedirs(K.AUDIO, exist_ok=True)
    cues = anim4.cues()
    rep = A.mix(cues, anim4.DUR, os.path.join(K.AUDIO, 'anim4_sfx.wav'), os.path.join(K.AUDIO, 'anim4_sfx_stem.wav'),
                bed=anim4.BED, bed_gain_db=anim4.BED_GAIN_DB, tp_ceiling=tp, verbose=False)
    if verbose:
        print('anim4 SFX: %.2f LUFS  %.2f dBTP  (%d cues)  -> %s' % (
            rep['integrated_lufs'], rep['true_peak_dbtp'], len(cues), os.path.join(K.AUDIO, 'anim4_sfx.wav')))
        for pl in rep.get('placed', []):
            if pl.get('warn'):
                print('   cue warning: %s at %.2fs: %s' % (pl.get('name'), pl.get('t', 0.0), pl['warn']))
    if overview:
        d = os.path.join(K.OUT, 'anim4')
        os.makedirs(d, exist_ok=True)
        try:
            A.mix_overview(rep, os.path.join(d, 'anim4_sfx_overview.png'), 'anim4 SFX')
        except Exception as e:                      # overview is a nicety
            print('overview failed:', e)
    return rep


def audition():
    import core as K
    register()
    seq = [('zip_pull', {}), ('fabric_swish', {}), ('bus_pass', {}), ('ball_bounce', {}),
           ('ball_bounce', dict(pitch=1.15)), ('paint_dab', {}), ('basket_drop', {}), ('house_pop', {}),
           ('coin_clinks', {}), ('soft_chime', {})]
    parts = []
    for nm, kw in seq:
        x = np.asarray(A.sound(nm, **kw), np.float64)
        st = A.stats(x, A.sound(nm, **kw).hit)
        print('%-13s dur %.2f  peak %.1f dBFS  Mmax %.1f  env_peak %.3f  hit %.3f  qc %s' % (
            nm, st['dur'], st['peak_db'], st['mmax_lufs'], st['env_peak_t'], A.sound(nm, **kw).hit,
            A.qc(x, A.sound(nm, **kw).hit) or 'ok'))
        parts += [x, np.zeros((_n(0.35), 2))]
    out = np.concatenate(parts, 0)
    bed = np.asarray(A.sound('airy_bed'), np.float64)
    out = np.concatenate([out, bed[:_n(6.0)]], 0)
    d = os.path.join(K.OUT, 'anim4')
    os.makedirs(d, exist_ok=True)
    p = os.path.join(d, 'anim4_sfx_audition.wav')
    A._write_wav(p, out, 24)
    print('->', p)
    return p


def _write(p, x):
    from scipy.io import wavfile
    y = np.clip(x, -1, 1)
    wavfile.write(p, SR, (y * 32767).astype(np.int16))


def selftest():
    """Spectrogram grid of the custom sounds -> workspace3/out/selftest/anim4_sfx_sheet.png (+ QC printout)."""
    import core as K
    register()
    os.makedirs(K.SELFTEST, exist_ok=True)
    items = [(nm, A.sound(nm)) for nm in CUSTOM]
    paths = A.catalog_sheets(items, os.path.join(K.SELFTEST, 'anim4_sfx_sheet_%d.png'))
    for nm, x in items:
        print('%-13s %s' % (nm, A.qc(np.asarray(x, np.float64), x.hit) or 'ok'))
    print('->', paths)
    return paths


if __name__ == '__main__':
    cmd = sys.argv[1] if len(sys.argv) > 1 else 'build'
    if cmd == 'build':
        build()
    elif cmd == 'audition':
        audition()
    elif cmd == 'selftest':
        selftest()
    else:
        print(__doc__)
