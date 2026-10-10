"""reel1 "Every market": procedural neon electro score + final mix (music supervisor). Map and key: MUSIC_reel1.md.

Source: procedural, synthesised here in numpy with audio.py helpers (no library track, no AI music tool in this
workspace). Nothing licensed, nothing to archive: the wav is rebuilt from this file.

Style (distinct from reel2's cinematic clock score): 124 BPM four-on-the-floor electro / synthwave. Kick-pumped
supersaw pads, off-beat saw bass, claps on 2 and 4, off-beat open hats, a 16th pluck arp under the market list.
Key F minor (Aeolian): Fm7 | Dbmaj7 | Ab | Eb loop, build on Eb sus, resolving to Ab add9 (relative major) on the
end card. Bass roots F1-Eb2 (44-78 Hz) stay below the male VO fundamental; pads low-passed <= 2.4 kHz; the mix dips
the music 6 dB plus a further 6 dB in 2-5 kHz under the VO.

    nice -n 10 python3 reel1_music.py          # music wav + final mix + measurements
Writes <WS>/audio/reel1_music.wav (-16 LUFS, <= -3 dBTP), reel1_mix.wav (+ _mix_stem, _music_stem; 48 kHz 24-bit,
exactly DUR). Needs <WS>/audio/reel1_sfx_stem.wav (python3 reel1_sfx.py) and reel1_vo.wav.
Render with:  --audio <WS>/audio/reel1_mix.wav

The helpers (chord, sine_note, kick/clap/hat/snare, noise_swell, build_mix, measure) take the buffer length from
their arguments, so reel3_music.py reuses them.
"""
import os
import numpy as np
from scipy import signal
from scipy.ndimage import uniform_filter1d
import audio as A

SR = A.SR
TAU = 2 * np.pi
hz = lambda m: 440.0 * 2 ** ((m - 69) / 12.0)
R = np.random.default_rng(20261)


# ---- generic synth helpers (buffer-length agnostic) ---------------------------------------------------------------
def add(buf, x, t0):
    A._add(buf, A._st(x), t0)


def saw_voice(f, u, fc, nmax=7000.0, rng=R):
    """Band-limited additive saw on local time u, with a steep spectral roll-off at fc (scalar or array)."""
    y = np.zeros(len(u))
    fcm = float(np.max(fc))
    for k in range(1, int(min(nmax, 3.5 * fcm) // f) + 1):
        y += (1.0 / k) / np.sqrt(1 + (k * f / fc) ** 4) * np.sin(TAU * k * f * u + rng.uniform(0, TAU))
    return y


def chord(buf, notes, t0, t1, amp, fc, a=0.15, r=0.4, det=0.0045, wid=0.7, voices=3):
    """Detuned saw pad over [t0, t1 + r]; amp, fc: scalars or callables of absolute time."""
    N = len(buf)
    i0, i1 = int(t0 * SR), min(N, int((t1 + r) * SR))
    tt = np.arange(i0, i1) / SR; u = tt - t0
    env = np.clip(u / a, 0, 1) ** 1.5 * np.clip((t1 + r - tt) / r, 0, 1) ** 2
    env = env * (amp(tt) if callable(amp) else amp)
    fcv = fc(tt) if callable(fc) else fc
    dets = ((-det, -wid), (0.0, 0.0), (det, wid)) if voices == 3 else \
        ((-det, -wid), (-det / 3, -wid / 3), (det / 3, wid / 3), (det, wid), (0.0, 0.0))
    out = np.zeros((len(tt), 2))
    for n in notes:
        for d, p in dets:
            v = saw_voice(hz(n) * (1 + d), u, fcv) * env / (len(notes) * len(dets) / 3)
            th = (p + 1) * np.pi / 4
            out[:, 0] += v * np.cos(th); out[:, 1] += v * np.sin(th)
    buf[i0:i1] += out


def sine_note(buf, f, t0, d, amp, a=0.01, tau=None, h2=0.25):
    """Sine (+2nd harmonic so phones hear it). tau: exp decay (30 ms end fade), else sustained, 0.1 s release."""
    n = int(d * SR); u = np.arange(n) / SR
    env = np.clip(u / a, 0, 1) * (np.exp(-u / tau) * np.clip((d - u) / 0.03, 0, 1) if tau
                                  else np.clip((d - u) / 0.1, 0, 1))
    add(buf, (np.sin(TAU * f * u) + h2 * np.sin(TAU * 2 * f * u)) * env * amp, t0)


def pluck(buf, m, t0, amp, d=0.28, fc0=3200.0, tau=0.09, p=0.0):
    n = int(d * SR); u = np.arange(n) / SR
    x = saw_voice(hz(m), u, 400 + fc0 * np.exp(-u / 0.035)) * np.exp(-u / tau) * np.clip(u / 0.002, 0, 1)
    add(buf, A.pan(x * amp, p), t0)


def kick(buf1, t0, amp=1.0, f_end=50.0, f_drop=110.0, tau=0.2):
    A._add(buf1, A._thump(0.5, f_end, f_drop, 0.028, tau, R, drive=2.0, noise=0.15, click=0.35) * amp, t0)


def clap(buf, t0, amp):
    n = int(0.4 * SR); u = np.arange(n) / SR
    env = sum(np.exp(-np.maximum(u - o, 0) / 0.009) * (u >= o) for o in (0.0, 0.011, 0.022)) * 0.4 \
        + np.exp(-np.maximum(u - 0.03, 0) / 0.11) * (u >= 0.03)
    x = A.bp(R.standard_normal((n, 2)), 900, 7000) * env[:, None]
    add(buf, x * amp, t0)


def hat(buf, t0, amp, tau=0.03):
    n = int(0.3 * SR); u = np.arange(n) / SR
    add(buf, A.hp(R.standard_normal((n, 2)), 7500, 2) * np.exp(-u / tau)[:, None] * amp, t0)


def snare(buf, t0, amp):
    n = int(0.35 * SR); u = np.arange(n) / SR
    body = np.sin(TAU * 190 * u) * np.exp(-u / 0.05)
    nz = A.bp(R.standard_normal(n), 400, 5000) * np.exp(-u / 0.08)
    add(buf, (0.6 * body + 0.6 * nz) * amp, t0)


def crash(buf, t0, amp, tau=0.9):
    n = int(3 * tau * SR); u = np.arange(n) / SR
    add(buf, A.hp(R.standard_normal((n, 2)), 4500, 2) * (np.exp(-u / tau) * np.clip(u / 0.003, 0, 1))[:, None] * amp, t0)


def noise_swell(buf, t0, t1, f0, f1, amp, power=2.0, hp_hz=None):
    """Filtered-noise swell from t0 to t1 (band centre f0 -> f1, level ^power), ends abruptly at t1 (5 ms)."""
    d = t1 - t0
    x = A.noise_band(d, R, [(0, f0), (1, f1)], bw=1.2, width=0.7)
    u = np.arange(len(x)) / SR
    x = x * ((u / d) ** power * np.clip((d - u) / 0.005, 0, 1))[:, None]
    if hp_hz:
        x = A.hp(x, hp_hz)
    add(buf, x * amp / max(1e-9, np.max(np.abs(x))), t0)


def dips(t, spec):
    """Gain curve with short suck-outs: spec = [(t_a, t_b, depth_db, fade_in)], back to 0 dB in 4 ms after t_b."""
    g = np.ones(len(t))
    for a, b, depth, f in spec:
        g *= A.undb(depth * np.clip(np.minimum((t - (a - f)) / f, ((b + 0.004) - t) / 0.004), 0, 1))
    return g


# ---- reel1 score --------------------------------------------------------------------------------------------------
BPM, DUR = 124, 22.0
B = 60.0 / BPM                                   # 0.4839 s beat, 1.935 s bar
N = int(round(DUR * SR))
bt = lambda n: n * B
DROP = bt(8)                                     # 3.871 whip into the globe
FILL = bt(24)                                    # 11.613 fill bar into the whip down / "0%"
HIT2 = bt(26)                                    # 12.581 crash in the whip down (12.52) before the 12.69 slam
BUILD = bt(32)                                   # 15.484 Eb sus build
RES = bt(35)                                     # 16.935 Ab add9 resolve (mark resolves 16.95, sting 17.05)
FADE0, FADE1 = 19.40, 21.85

FM7 = [41, 48, 51, 56, 60]                       # F2 C3 Eb3 Ab3 C4
DBMA7 = [37, 48, 53, 56, 60]                     # Db2 C3 F3 Ab3 C4
AB = [44, 48, 51, 56, 63]                        # Ab2 C3 Eb3 Ab3 Eb4
EB = [39, 46, 51, 55, 58]                        # Eb2 Bb2 Eb3 G3 Bb3
EBSUS = [39, 46, 51, 56, 58]                     # Eb2 Bb2 Eb3 Ab3 Bb3
ABADD9 = [44, 51, 58, 60, 63]                    # Ab2 Eb3 Bb3 C4 Eb4
# bars (t0, t1, pad notes, bass root midi)
BARS = [(bt(8), bt(12), FM7, 29), (bt(12), bt(16), DBMA7, 37), (bt(16), bt(20), AB, 32), (bt(20), bt(24), EB, 39),
        (bt(24), bt(28), FM7, 29), (bt(28), bt(32), DBMA7, 37)]


def score():
    t = np.arange(N) / SR
    pad, hits, bass, drums, tops = (np.zeros((N, 2)) for _ in range(5))
    kk = np.zeros(N)

    # hook 0-3.871 (2 bars): filtered F pulse in 8ths opening up, half-time kicks on the whip beats 0/2/4/6,
    # a 16th snare roll + noise riser over beats 6-8, 45 ms suck-out before the drop
    chord(pad, [41, 48, 53], 0.0, DROP - 0.05, lambda tt: 0.35 + 0.4 * tt / DROP,
          lambda tt: 350 + 1300 * (tt / DROP) ** 2, a=0.02, r=0.02)
    for k in range(16):
        b = bt(k / 2); nn = int(0.2 * SR); u = np.arange(nn) / SR
        fc = 300 + 900 * (b / DROP) ** 1.5
        x = saw_voice(hz(41), u, fc + 600 * np.exp(-u / 0.03)) * np.exp(-u / 0.09) * (1.0 if k % 2 == 0 else 0.7)
        add(bass, x * 0.55, b)
    for k in (0, 2, 4, 6):
        kick(kk, bt(k), 0.75)
    for k in range(1, 8, 2):
        hat(tops, bt(k), 0.10)
    for b in np.arange(bt(6), DROP - 0.03, B / 4):
        snare(drums, b, 0.15 + 0.55 * ((b - bt(6)) / (2 * B)) ** 1.5)
    noise_swell(tops, bt(5), DROP - 0.045, 500, 7000, 0.4, power=2.5)

    # drive 3.871-15.484: 4/4 kick, clap 2+4, off-beat open hat, 16th closed hats, off-beat saw bass,
    # kick-pumped supersaw pads; 16th pluck arp over the market list (5.806-10.2) and again from 14.03
    crash(tops, DROP, 0.35)
    sine_note(hits, hz(29), DROP, 1.4, 0.7, tau=0.5)                                    # F1 drop boom
    for t0, t1, ch, root in BARS:
        chord(pad, ch, t0, t1 - 0.01, 0.75, 2100.0 if t0 < FILL else 2400.0, a=0.01, r=0.02, voices=5)
        for k in range(4):
            b = t0 + k * B
            kick(kk, b, 1.0)
            if k % 2 == 1:
                clap(drums, b, 0.45)
            hat(tops, b + B / 2, 0.16, tau=0.07)
            for s in (1, 3):
                hat(tops, b + s * B / 4, 0.06)
            nn = int(0.22 * SR); u = np.arange(nn) / SR                           # off-beat bass, octave up
            x = saw_voice(hz(root + 12), u, 260 + 900 * np.exp(-u / 0.05)) * np.exp(-u / 0.12)
            x += 0.7 * np.sin(TAU * hz(root + 12) * u) * np.exp(-u / 0.14)
            add(bass, x * 0.6, b + B / 2)
    for ts, te in ((bt(12), 10.20), (14.03, BUILD)):
        for k, b in enumerate(np.arange(ts, te - 0.01, B / 4)):
            ch = next(c for a0, a1, c, _ in BARS if a0 <= b + 1e-6 < a1)
            seq = [ch[2] + 12, ch[3] + 12, ch[4] + 12, ch[3] + 12]
            pluck(tops, seq[k % 4], b, 0.22 if k % 4 == 0 else 0.15, p=0.25 * (1 if k % 2 else -1))
    # fill bar 11.613-12.581: snare 8ths -> 16ths over beats 24-26 (kick keeps going), crash in the whip down
    for b in list(np.arange(bt(25), bt(25.5), B / 2)) + list(np.arange(bt(25.5), HIT2 - 0.02, B / 4)):
        snare(drums, b, 0.2 + 0.4 * (b - bt(25)) / B)
    noise_swell(tops, bt(25), HIT2 - 0.03, 1500, 8000, 0.18, power=2.0, hp_hz=1200)
    crash(tops, HIT2, 0.30)
    crash(tops, bt(28), 0.22)                                                            # 13.548 bar line

    # build 15.484-16.935: kick drops, Eb sus pad filter opening + rising, snare 8ths -> 16ths -> 32nds, riser,
    # 40 ms suck-out before the resolve
    chord(pad, EBSUS, BUILD, RES - 0.04, lambda tt: 0.55 + 0.45 * np.clip((tt - BUILD) / (RES - BUILD), 0, 1),
          lambda tt: 700 + 2200 * np.clip((tt - BUILD) / (RES - BUILD), 0, 1) ** 1.5, a=0.03, r=0.02, voices=5)
    for b in np.arange(BUILD, RES - 0.05, B / 2):
        sine_note(bass, hz(39), b, 0.2, 0.45, tau=0.08)
    roll = list(np.arange(BUILD, bt(33), B / 2)) + list(np.arange(bt(33), bt(34), B / 4)) \
        + list(np.arange(bt(34), RES - 0.04, B / 8))
    for b in roll:
        snare(drums, b, 0.2 + 0.6 * ((b - BUILD) / (RES - BUILD)) ** 1.3)
    noise_swell(tops, BUILD, RES - 0.04, 600, 7000, 0.45, power=2.2)

    # resolve 16.935: Ab add9 lands with a soft boom + crash; slow 8th sparkle arp until 19.0; fade by 21.85
    sine_note(hits, hz(32), RES, 2.5, 0.55, tau=0.9)
    crash(tops, RES, 0.25, tau=1.4)
    ab = lambda tt: 0.8 * (1 - 0.4 * np.clip((tt - 18.0) / 1.5, 0, 1))
    chord(pad, ABADD9, RES, FADE1 - 0.2, ab, lambda tt: 2000 - 1100 * np.clip((tt - 17.6) / 3.0, 0, 1),
          a=0.04, r=0.2, voices=5)
    sine_note(bass, hz(32), RES, FADE1 - RES, 0.35, a=0.02, tau=2.8)
    for k, b in enumerate(np.arange(RES + B, 19.0, B / 2)):
        m = (68, 75, 80, 82, 84, 80)[k % 6]
        pluck(tops, m, b, 0.12 * (1 - 0.6 * (b - RES) / (19.0 - RES)), d=0.5, fc0=2200, tau=0.2,
              p=0.3 * (1 if k % 2 else -1))

    # bus: pump pads/bass/arp off the kick, reverb, suck-outs, tail fade
    pad = A.sidechain(pad, kk, depth_db=8, attack=0.004, release=0.16)
    bass = A.sidechain(bass, kk, depth_db=6, attack=0.004, release=0.12)
    tops_p = A.sidechain(tops, kk, depth_db=3, attack=0.004, release=0.12)
    mus = 0.30 * A.lp(pad, 2400) + 0.55 * hits + 0.42 * A.hp(bass, 35) + 0.40 * drums + 0.22 * tops_p \
        + 0.85 * kk[:, None]
    mus = A.hp(mus, 28, 2)
    mus = A.reverb(mus, 'hall', wet_db=-15, send_hp=250)[:N]
    g = dips(t, [(DROP - 0.045, DROP, -18.0, 0.008), (RES - 0.04, RES, -12.0, 0.008)])
    fade = np.where(t < FADE0, 1.0, np.cos(np.clip((t - FADE0) / (FADE1 - FADE0), 0, 1) * np.pi / 2) ** 2)
    return mus * (g * fade)[:, None]


def build_music(name='reel1', fn=score):
    mus = fn()
    mus *= A.undb(-16 - A.loudness(mus))
    mus = mus * A.limiter_gain(mus, -3.0)[:, None]
    A._write_wav(os.path.join(A.AUDIO, name + '_music.wav'), mus, 24)
    return mus


# ---- final mix (same law as reel2_music.py) -----------------------------------------------------------------------
def _env(key, depth_db, attack, release, thresh_rel_db=-26.0):
    """Smooth 0..1 ducking amount from a key (50 ms RMS, ballistics), same law as A.sidechain."""
    k = A._mono(np.abs(A._st(key)))
    lvl = A.db(np.sqrt(np.maximum(uniform_filter1d(k ** 2, int(0.05 * SR)), 1e-20)))
    amt = np.clip((lvl - (lvl.max() + thresh_rel_db)) / (-6.0 - thresh_rel_db), 0, 1)
    return -A._ballistics(-depth_db * amt, attack, release) / depth_db


def build_mix(name, dur, mus=None, mus_lufs=-17.0):
    n = int(round(dur * SR))
    P = lambda f: os.path.join(A.AUDIO, name + f)
    def fit(p):
        x = A._st(A.read_wav(p)[0])[:n]
        return np.pad(x, ((0, n - len(x)), (0, 0)))
    sfx, vo = fit(P('_sfx_stem.wav')), fit(P('_vo.wav'))
    mus = fit(P('_music.wav')) if mus is None else mus[:n]
    mus = mus * A.undb(mus_lufs - A.loudness(mus))
    mus = A.sidechain(mus, sfx, depth_db=3, attack=0.01, release=0.25)          # let SFX hero hits through
    amt = _env(vo, 1.0, attack=0.06, release=0.45)                               # VO duck, 0..1, smooth
    band = signal.sosfiltfilt(signal.butter(2, [2000, 5000], 'bandpass', fs=SR, output='sos'), mus, axis=0)
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
    k = A.undb(g) * gl[:, None]
    A._write_wav(P('_mix.wav'), y, 24)
    A._write_wav(P('_mix_stem.wav'), y, 24)
    A._write_wav(P('_music_stem.wav'), mus * k, 24)
    return dict(mix=y, mus=mus * k, vo=vo * k, sfx=sfx * k, amt=amt)


def measure(r):
    import pyloudnorm as pyln
    meter = pyln.Meter(SR)
    tp = lambda x: 20 * np.log10(np.max(np.abs(signal.resample_poly(x, 4, 1, axis=0))) + 1e-12)
    out = {k: (meter.integrated_loudness(r[k]), tp(r[k])) for k in ('mix', 'mus', 'vo', 'sfx')}
    sos = signal.butter(4, [2000, 5000], 'bandpass', fs=SR, output='sos')
    n = len(r['mix']); hop = int(0.05 * SR); nf = n // hop
    fr = lambda x: 10 * np.log10(np.mean(x[:nf * hop].mean(1).reshape(nf, hop) ** 2, 1) + 1e-14)
    vb, mb = fr(signal.sosfilt(sos, r['vo'], axis=0)), fr(signal.sosfilt(sos, r['mus'], axis=0))
    vf, mf = fr(r['vo']), fr(r['mus'])
    on = vf > vf.max() - 30
    out['band_snr_med'] = float(np.median((vb - mb)[on]))
    out['band_snr_p10'] = float(np.percentile((vb - mb)[on], 10))
    out['broad_snr_med'] = float(np.median((vf - mf)[on]))
    _, lv = A.loudness_curve(r['vo']); _, lm = A.loudness_curve(r['mus'])
    out['music_under_vo_lu'] = float(np.median((lv - lm)[lv > lv.max() - 15]))
    return out


def beatgrid(x, bpm):
    """Tempo / beat phase of a wav (spectral flux on a 5 ms hop), as in the music-supervisor playbook."""
    x = A._st(x).mean(1)
    _, tt, Z = signal.stft(x, SR, nperseg=2048, noverlap=2048 - 240)
    fl = np.maximum(np.diff(np.log1p(np.abs(Z) * 100), axis=1), 0).sum(0); hop = 240 / SR
    def sc(b, off):
        i = np.round((off + np.arange(0, tt[-1] - off, 60 / b)) / hop).astype(int); return fl[i[i < len(fl)]].mean()
    s, b, off = max((sc(b, o), b, o) for b in bpm * np.arange(.97, 1.03, .0025) for o in np.arange(0, 60 / b, .005))
    off = (off + 30 / b) % (60 / b) - 30 / b
    return b, off, s / fl.mean()


def report(name, dur, bpm, mus, r):
    m = measure(r)
    x, sr = A.read_wav(os.path.join(A.AUDIO, name + '_mix.wav'))
    print('music  %.2f LUFS  %.2f dBTP' % (A.loudness(mus), A.true_peak(mus)))
    print('beatgrid music: %.2f BPM, phase %+.3f s, strength x%.1f' % beatgrid(mus, bpm))
    print('mix wav: %d samples (%.4f s, DUR %.2f) @ %d Hz' % (len(x), len(x) / sr, dur, sr))
    for k in ('mix', 'mus', 'vo', 'sfx'):
        print('%-4s pyloudnorm %.2f LUFS   true peak (4x) %.2f dBTP' % ((k,) + m[k]))
    print('VO vs music: broadband median %.1f dB, 2-5 kHz median %.1f dB (p10 %.1f), music under VO %.1f LU'
          % (m['broad_snr_med'], m['band_snr_med'], m['band_snr_p10'], m['music_under_vo_lu']))


if __name__ == '__main__':
    mus = build_music()
    report('reel1', DUR, BPM, mus, build_mix('reel1', DUR))
