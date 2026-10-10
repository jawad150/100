"""reel2 "Blink": procedural cinematic-hybrid score + final mix (music supervisor). Map and key: MUSIC_reel2.md.

Source: procedural, synthesised here in numpy with audio.py helpers (no library track, no AI music tool in this
workspace). Nothing licensed, nothing to archive: the wav is rebuilt from this file.

Key D minor (Aeolian), cadencing Bb (12.10 lift) -> C7sus (13.50 build) -> F add9 (14.50 end card), i.e. it lands
in the relative major. Bass roots sit at D2 73 Hz / Bb1 58 Hz / F1 44 Hz, below a male VO fundamental; pads are
low-passed (<= 1.8 kHz) and the 2-5 kHz band is dipped dynamically under the VO in the mix.

    nice -n 10 python3 reel2_music.py          # music wav + final mix + measurements
Writes <WS>/audio/reel2_music.wav (-16 LUFS, <= -3 dBTP), reel2_mix.wav (+ _mix_stem, _music_stem; 48 kHz 24-bit,
exactly DUR). Needs <WS>/audio/reel2_sfx_stem.wav (python3 reel2_sfx.py) and reel2_vo.wav.
Render with:  --audio <WS>/audio/reel2_mix.wav
"""
import os
import numpy as np
from scipy import signal
import audio as A

SR, BPM, DUR = A.SR, 120, 21.5
B = 60.0 / BPM                                   # 0.5 s beat, 2.0 s bar
N = int(round(DUR * SR))
t = np.arange(N) / SR
TAU = 2 * np.pi
hz = lambda m: 440.0 * 2 ** ((m - 69) / 12.0)
R = np.random.default_rng(20262)

# ---- events (s), matched to reel2.py ------------------------------------------------------------------------------
GAP0, GAP1 = 0.94, 1.04          # lids shut: near-silence
HIT = 3.00                       # the hit (cut B)
DRIVE0, DRIVE1 = 5.50, 11.50     # order window (cut C -> cut D)
LIFT = 12.10                     # "lag." slam
BUILD = 13.50                    # 2-beat build
WHIP = 14.50                     # whip peak, end card
BLOOM = 16.00                    # logo lands (crossfade to logo_full 15.95-16.25)
FADE0, FADE1 = 18.80, 21.35      # tail fade, silent by 21.35

# harmony: (t0, t1, notes MIDI)
DM = [38, 45, 50, 53]                   # D2 A2 D3 F3
DM9 = [38, 45, 50, 53, 57]              # + A3
BBMA7 = [34, 46, 50, 53, 57]            # Bb1 Bb2 D3 F3 A3
GM9 = [43, 46, 50, 53, 57]              # G2 Bb2 D3 F3 A3
BBMA9 = [34, 46, 53, 57, 60]            # Bb1 Bb2 F3 A3 C4
C7SUS = [36, 48, 55, 58, 62]            # C2 C3 G3 Bb3 D4
FADD9 = [41, 48, 55, 57, 60]            # F2 C3 G3 A3 C4


def seg(a, b, fa=0.03, fb=0.03):
    return np.clip((t - a) / max(fa, 1e-4), 0, 1) * np.clip((b - t) / max(fb, 1e-4), 0, 1)


def ramp(pts):
    """Piecewise-linear curve over absolute time from [(t, v), ...]."""
    p = np.asarray(pts, float)
    return np.interp(t, p[:, 0], p[:, 1])


def add(buf, x, t0):
    A._add(buf, A._st(x), t0)


def saw_voice(f, u, fc, nmax=7000.0):
    """Band-limited additive saw on local time u, with a 4-pole-like spectral roll-off at fc (scalar or array)."""
    y = np.zeros(len(u))
    fcm = float(np.max(fc))
    for k in range(1, int(min(nmax, 3.5 * fcm) // f) + 1):
        g = (1.0 / k) / np.sqrt(1 + (k * f / fc) ** 4)
        y += g * np.sin(TAU * k * f * u + R.uniform(0, TAU))
    return y


def chord(buf, notes, t0, t1, amp, fc, a=0.15, r=0.4, det=0.0035, wid=0.6):
    """Detuned 3-voice saw pad over [t0, t1 + r]; amp, fc: scalars or callables of absolute time."""
    i0, i1 = int(t0 * SR), min(N, int((t1 + r) * SR))
    tt = t[i0:i1]; u = tt - t0
    env = np.clip(u / a, 0, 1) ** 1.5 * np.clip((t1 + r - tt) / r, 0, 1) ** 2
    env = env * (amp(tt) if callable(amp) else amp)
    fcv = fc(tt) if callable(fc) else fc
    out = np.zeros((len(tt), 2))
    for n in notes:
        for d, p in ((-det, -wid), (0.0, 0.0), (det, wid)):
            v = saw_voice(hz(n) * (1 + d), u, fcv) * env / len(notes)
            th = (p + 1) * np.pi / 4
            out[:, 0] += v * np.cos(th); out[:, 1] += v * np.sin(th)
    buf[i0:i1] += out


def sine_note(buf, f, t0, d, amp, a=0.01, tau=None, h2=0.25):
    """Sub/bass sine (+2nd harmonic so phones hear it). tau: exp decay, else sustained over d with 0.1 s release."""
    n = int(d * SR); u = np.arange(n) / SR
    env = np.clip(u / a, 0, 1) * (np.exp(-u / tau) if tau else np.clip((d - u) / 0.1, 0, 1))
    x = (np.sin(TAU * f * u) + h2 * np.sin(TAU * 2 * f * u)) * env * amp
    add(buf, x, t0)


def tick(buf, t0, hi=True, amp=1.0, bright=False):
    """Clock tick/tock: woody modal click (1.25 / 0.94 kHz) + an airy top click above 6 kHz."""
    d = 0.09; n = int(d * SR); u = np.arange(n) / SR
    f = 1250.0 if hi else 940.0
    body = (np.sin(TAU * f * u) + 0.4 * np.sin(TAU * f * 2.71 * u)) * np.exp(-u / 0.012)
    air = A.hp(R.standard_normal(n), 6500, 2) * np.exp(-u / (0.006 if not bright else 0.02))
    x = (0.6 * body + (0.5 if not bright else 0.8) * air) * amp
    add(buf, A.pan(x, 0.18 if hi else -0.18), t0)


def hat(buf, t0, amp, tau=0.03):
    n = int(0.25 * SR); u = np.arange(n) / SR
    x = A.hp(R.standard_normal((n, 2)), 7500, 2) * np.exp(-u / tau)[:, None]
    add(buf, x * amp, t0)


def snare(buf, t0, amp):
    n = int(0.35 * SR); u = np.arange(n) / SR
    body = np.sin(TAU * 185 * u) * np.exp(-u / 0.05)
    nz = A.bp(R.standard_normal(n), 400, 3500) * np.exp(-u / 0.07)
    add(buf, (0.7 * body + 0.5 * nz) * amp, t0)


def thump(buf, t0, f_end, f_drop, tau, amp, d=2.5, noise=0.35, click=0.0, enhance=0.6):
    x = A._thump(d, f_end, f_drop, 0.05, tau, R, attack=0.004, drive=1.8, noise=noise, noise_lp=450, click=click)
    if enhance:
        x = A.bass_enhance(x, enhance)
    add(buf, x * amp, t0)


def noise_swell(buf, t0, t1, f0, f1, amp, power=2.0, hp_hz=None):
    """Filtered-noise swell from t0 to t1 (band centre f0 -> f1, level ^power), ends abruptly at t1 (5 ms)."""
    d = t1 - t0
    x = A.noise_band(d, R, [(0, f0), (1, f1)], bw=1.2, width=0.7)
    u = np.arange(len(x)) / SR
    env = (u / d) ** power * np.clip((d - u) / 0.005, 0, 1)
    x = x * env[:, None]
    if hp_hz:
        x = A.hp(x, hp_hz)
    add(buf, x * amp / max(1e-9, np.max(np.abs(x))), t0)


def score():
    pad, hits, bass, drums, tops = (np.zeros((N, 2)) for _ in range(5))

    # A hook 0-3.0: open-fifth drone, tick-tock clock on beats, the blink gap, ticks on 8ths, build into the hit
    chord(pad, [38, 45], 0.0, GAP0 - 0.05, 0.55, 420.0, a=0.02, r=0.05)
    for b in (0.0, 0.5):
        tick(tops, b, hi=(b == 0.0), amp=0.8)
    chord(pad, DM, GAP1, HIT - 0.06, lambda tt: 0.35 + 0.65 * np.clip((tt - 1.6) / 1.34, 0, 1) ** 2,
          lambda tt: 450 + 1900 * np.clip((tt - 1.6) / 1.34, 0, 1) ** 2, a=0.35, r=0.02)
    for k, b in enumerate(np.arange(1.5, HIT - 0.01, B / 2)):
        tick(tops, b, hi=(k % 2 == 0), amp=0.55 + 0.35 * (b - 1.5) / 1.5)
    for b in (1.5, 2.0, 2.5, 2.75):                                      # low pulse into the hit
        sine_note(bass, hz(26), b, 0.4, 0.55 if b < 2.75 else 0.4, tau=0.14)
    noise_swell(tops, 2.0, HIT - 0.06, 500, 4000, 0.22, power=2.5)

    # B the hit 3.0: sub boom + braam (Dm, filter sweeping 2.4 kHz -> 350 Hz) + low noise burst; clock continues
    thump(hits, HIT, hz(26), 45, 0.9, 1.0, d=3.5, noise=0.45, click=0.25)
    chord(hits, [38, 45, 50, 53], HIT, HIT + 1.2,
          lambda tt: np.exp(-(tt - HIT) / 1.4), lambda tt: 350 + 2050 * np.exp(-(tt - HIT) / 0.35), a=0.008, r=1.3)
    n = int(1.5 * SR); u = np.arange(n) / SR
    add(hits, A.lp(R.standard_normal((n, 2)), 1400) * np.exp(-u / 0.25)[:, None] * 0.6, HIT)
    chord(pad, DM, HIT + 0.3, DRIVE0 - 0.05, 0.6, 700.0, a=0.8, r=0.1)
    for k, b in enumerate(np.arange(HIT + 0.5, DRIVE0 - 0.01, B / 2)):
        tick(tops, b, hi=(k % 2 == 0), amp=0.6)
    for b in (4.0, 5.0):
        sine_note(bass, hz(26), b, 0.5, 0.45, tau=0.18)
    noise_swell(tops, 4.75, DRIVE0, 2000, 9000, 0.12, power=3.0, hp_hz=2500)

    # C driving pulse 5.5-11.5: kick on beats, 16th bass ostinato (Dm | Bbmaj7 | Gm9), 16th ticks, offbeat hats
    for tt0, tt1, ch, fc in ((DRIVE0, 8.0, DM9, 950.0), (8.0, 10.0, BBMA7, 1050.0), (10.0, DRIVE1, GM9, 1150.0)):
        chord(pad, ch, tt0, tt1, 0.7, fc, a=0.06 if tt0 == DRIVE0 else 0.2, r=0.2)
    kick = np.zeros(N)
    for b in np.arange(DRIVE0, DRIVE1 - 0.01, B):
        x = A._thump(0.5, 55.0, 95.0, 0.03, 0.17, R, drive=1.8, noise=0.2, click=0.3)
        A._add(kick, x, b)
    root = lambda b: 38 if b < 8.0 else (34 if b < 10.0 else 43)
    vel = (1.0, 0.5, 0.75, 0.55)
    for k, b in enumerate(np.arange(DRIVE0, DRIVE1 - 0.01, B / 4)):
        m = root(b); nn = int(0.13 * SR); u = np.arange(nn) / SR
        x = saw_voice(hz(m), u, 250 + 700 * np.exp(-u / 0.04)) * np.exp(-u / 0.07) * vel[k % 4]
        x += 0.6 * np.sin(TAU * hz(m) * u) * np.exp(-u / 0.08) * vel[k % 4]
        add(bass, x * 0.7, b)
        tick(tops, b, hi=(k % 2 == 0), amp=0.3 + 0.2 * (k % 4 == 0))
        if k % 4 == 2:
            hat(tops, b, 0.12, tau=0.05)
    pump = A.sidechain(np.stack([bass[:, 0], bass[:, 1]], 1), kick, depth_db=5, attack=0.004, release=0.14)
    bass[:] = pump
    drums[:, 0] += kick * 0.8; drums[:, 1] += kick * 0.8

    # D 11.5-12.1 drums out, pad darkens; LIFT 12.1: Bbmaj9 opens bright + tom/sub hit; half-time pulse
    chord(pad, GM9, DRIVE1, LIFT - 0.02, 0.5, 600.0, a=0.02, r=0.08)
    sine_note(bass, hz(31), DRIVE1, LIFT - DRIVE1, 0.35)                # G1 hold under the cut
    thump(hits, LIFT, hz(34), 60, 0.7, 0.85, d=2.5, noise=0.5, click=0.3)
    chord(hits, [34, 46, 53], LIFT, LIFT + 0.6, lambda tt: np.exp(-(tt - LIFT) / 0.9),
          lambda tt: 400 + 1600 * np.exp(-(tt - LIFT) / 0.3), a=0.01, r=0.8)
    chord(pad, BBMA9, LIFT, BUILD, 0.7, 1600.0, a=0.05, r=0.08)
    sine_note(bass, hz(34), LIFT, BUILD - LIFT + 0.02, 0.3)
    for b in (13.0,):
        thump(drums, b, 55.0, 80, 0.2, 0.55, d=0.6, noise=0.2, enhance=0)
    for k, b in enumerate(np.arange(12.5, BUILD - 0.01, B / 2)):
        tick(tops, b, hi=(k % 2 == 0), amp=0.45)
    n = int((BUILD - LIFT) * SR); u = np.arange(n) / SR                   # air layer opens on the lift
    add(tops, A.hp(R.standard_normal((n, 2)), 7000) * (0.025 * np.clip(u / 0.3, 0, 1) * np.clip((n / SR - u) / 0.2, 0, 1))[:, None], LIFT)

    # build 13.5-14.5 on C7sus: snare 8ths -> 16ths -> 32nds, rising noise, pad filter opening, then a 50 ms suck
    chord(pad, C7SUS, BUILD, WHIP - 0.05, lambda tt: 0.75 + 0.9 * (tt - BUILD), lambda tt: 1000 + 1800 * (tt - BUILD),
          a=0.03, r=0.02)
    for b in np.arange(BUILD, WHIP - 0.06, B / 4):
        sine_note(bass, hz(36), b, 0.12, 0.45 + 0.35 * (b - BUILD), tau=0.06)
    roll = list(np.arange(BUILD, 14.0, B / 2)) + list(np.arange(14.0, 14.25, B / 4)) + list(np.arange(14.25, WHIP - 0.06, B / 8))
    for b in roll:
        snare(drums, b, 0.35 + 0.9 * (b - BUILD))
    noise_swell(tops, BUILD, WHIP - 0.05, 600, 5000, 0.4, power=2.0)

    # E resolve on the end card: F add9 lands with the whip (14.5) / logo_sting (14.62), blooms as the logo lands
    # (15.8-16.3), sustains, fades out by 21.35
    thump(hits, WHIP, hz(29), 40, 1.1, 0.4, d=3.0, noise=0.3, click=0.0)
    bloom = lambda tt: (0.7 + 0.35 * np.clip((tt - 15.8) / 0.5, 0, 1)) * (1 - 0.45 * np.clip((tt - 17.2) / 1.3, 0, 1))
    chord(pad, FADD9, WHIP, FADE1 - 0.2, bloom, lambda tt: 800 + 900 * np.clip((tt - 15.8) / 0.5, 0, 1)
          - 600 * np.clip((tt - 17.5) / 3.5, 0, 1), a=0.12, r=0.2)
    sine_note(bass, hz(29), WHIP, FADE1 - WHIP, 0.33, a=0.08, tau=2.6)
    sine_note(bass, hz(41), WHIP, FADE1 - WHIP, 0.12, a=0.3, h2=0.0)
    i0 = int(15.9 * SR); u = t[i0:] - 15.9                                  # glassy top of the chord on the logo
    gl = np.clip(u / 0.4, 0, 1) * np.exp(-np.maximum(u - 0.4, 0) / 2.5)
    top = sum(np.sin(TAU * hz(m) * u + R.uniform(0, TAU)) * a for m, a in ((77, 0.5), (84, 0.35), (79, 0.25)))
    tops[i0:, 0] += 0.05 * top * gl; tops[i0:, 1] += 0.05 * np.roll(top, 240) * gl

    # stems -> bus: pad and hits darker below 2 kHz, reverb, then the global gap / suck-outs / tail fade
    mus = 0.30 * A.lp(pad, 2200) + 0.55 * hits + 0.42 * bass + 0.45 * drums + 0.20 * tops
    mus = A.hp(mus, 28, 2)
    mus = A.reverb(mus, 'hall', wet_db=-13, send_hp=180)[:N]
    g = np.ones(N)
    for a, b, depth, f in ((GAP0, GAP1, -42.0, 0.03), (HIT - 0.055, HIT, -20.0, 0.008), (WHIP - 0.05, WHIP, -10.0, 0.008)):
        dip = np.clip(np.minimum((t - (a - f)) / f, ((b + 0.004) - t) / 0.004), 0, 1)
        g *= A.undb(depth * dip)
    fade = np.where(t < FADE0, 1.0, np.cos(np.clip((t - FADE0) / (FADE1 - FADE0), 0, 1) * np.pi / 2) ** 2)
    return mus * (g * fade)[:, None]


def build_music():
    mus = score()
    mus *= A.undb(-16 - A.loudness(mus))
    mus = mus * A.limiter_gain(mus, -3.0)[:, None]
    A._write_wav(os.path.join(A.AUDIO, 'reel2_music.wav'), mus, 24)
    return mus


# ---- final mix ----------------------------------------------------------------------------------------------------
def _env(key, depth_db, attack, release, thresh_rel_db=-26.0):
    """Smooth 0..1 ducking amount from a key (50 ms RMS, ballistics), same law as A.sidechain."""
    k = A._mono(np.abs(A._st(key)))
    from scipy.ndimage import uniform_filter1d
    lvl = A.db(np.sqrt(np.maximum(uniform_filter1d(k ** 2, int(0.05 * SR)), 1e-20)))
    amt = np.clip((lvl - (lvl.max() + thresh_rel_db)) / (-6.0 - thresh_rel_db), 0, 1)
    return -A._ballistics(-depth_db * amt, attack, release) / depth_db


def build_mix(mus=None):
    P = lambda f: os.path.join(A.AUDIO, 'reel2' + f)
    def fit(p):
        x = A._st(A.read_wav(p)[0])[:N]
        return np.pad(x, ((0, N - len(x)), (0, 0)))
    sfx, vo = fit(P('_sfx_stem.wav')), fit(P('_vo.wav'))
    if mus is None:
        mus = fit(P('_music.wav'))
    mus = mus * A.undb(-17 - A.loudness(mus))
    mus = A.sidechain(mus, sfx, depth_db=3, attack=0.01, release=0.25)          # let SFX hero hits through
    amt = _env(vo, 1.0, attack=0.06, release=0.45)                               # VO duck, 0..1, smooth
    sos = signal.butter(2, [2000, 5000], 'bandpass', fs=SR, output='sos')
    band = signal.sosfiltfilt(sos, mus, axis=0)                                  # zero-phase 2-5 kHz band
    mus = (mus - band * (1 - A.undb(-6.0 * amt))[:, None]) * A.undb(-6.0 * amt)[:, None]
    sfx = sfx * A.undb(-18 - A.loudness(sfx))
    vo = vo * A.undb(-15 - A.loudness(vo))
    bus = mus + sfx + vo
    g = -14 - A.loudness(bus)
    for _ in range(10):
        gl = A.limiter_gain(bus * A.undb(g), -2.3)
        y = bus * A.undb(g) * gl[:, None]
        L = A.loudness(y)
        if abs(L + 14) < 0.05:
            break
        g += -14 - L
    y[-int(0.01 * SR):] *= np.linspace(1, 0, int(0.01 * SR))[:, None]
    A._write_wav(P('_mix.wav'), y, 24)
    A._write_wav(P('_mix_stem.wav'), y, 24)
    A._write_wav(P('_music_stem.wav'), mus * A.undb(g) * gl[:, None], 24)
    return dict(mix=y, mus=mus * A.undb(g) * gl[:, None], vo=vo * A.undb(g) * gl[:, None],
                sfx=sfx * A.undb(g) * gl[:, None], amt=amt)


def measure(r):
    import pyloudnorm as pyln
    meter = pyln.Meter(SR)
    tp = lambda x: 20 * np.log10(np.max(np.abs(signal.resample_poly(x, 4, 1, axis=0))) + 1e-12)
    out = {}
    for k in ('mix', 'mus', 'vo', 'sfx'):
        out[k] = (meter.integrated_loudness(r[k]), tp(r[k]))
    # VO intelligibility: 2-5 kHz band and broadband level, VO vs music, in 50 ms frames where the VO speaks
    sos = signal.butter(4, [2000, 5000], 'bandpass', fs=SR, output='sos')
    hop = int(0.05 * SR); nf = N // hop
    fr = lambda x: 10 * np.log10(np.mean(x[:nf * hop].mean(1).reshape(nf, hop) ** 2, 1) + 1e-14)
    vb, mb = fr(signal.sosfilt(sos, r['vo'], axis=0)), fr(signal.sosfilt(sos, r['mus'], axis=0))
    vf, mf = fr(r['vo']), fr(r['mus'])
    on = vf > vf.max() - 30
    out['band_snr_med'] = float(np.median((vb - mb)[on]))
    out['band_snr_p10'] = float(np.percentile((vb - mb)[on], 10))
    out['broad_snr_med'] = float(np.median((vf - mf)[on]))
    _, lv = A.loudness_curve(r['vo']); _, lm = A.loudness_curve(r['mus'])
    out['music_under_vo_lu'] = float(np.median((lv - lm)[lv > lv.max() - 15]))
    out['duck_db_max'] = float(6.0 * r['amt'].max())
    return out


if __name__ == '__main__':
    mus = build_music()
    print('music  %.2f LUFS  %.2f dBTP' % (A.loudness(mus), A.true_peak(mus)))
    r = build_mix()
    m = measure(r)
    x, sr = A.read_wav(os.path.join(A.AUDIO, 'reel2_mix.wav'))
    print('mix wav: %d samples (%.4f s) @ %d Hz' % (len(x), len(x) / sr, sr))
    for k in ('mix', 'mus', 'vo', 'sfx'):
        print('%-4s pyloudnorm %.2f LUFS   true peak (4x) %.2f dBTP' % ((k,) + m[k]))
    print('VO vs music: broadband median %.1f dB, 2-5 kHz median %.1f dB (p10 %.1f), music under VO %.1f LU, '
          'duck max %.1f dB' % (m['broad_snr_med'], m['band_snr_med'], m['band_snr_p10'], m['music_under_vo_lu'],
                                m['duck_db_max']))
