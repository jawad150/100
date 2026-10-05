"""Sound design for the Dr. Sukkar reel: SFX only (no music), timed to the edit.

Every sound is synthesised (whooshes, whips, hits, swells, shutter ticks, metal clinks,
latex snaps, fabric rustle, heart-monitor beeps), so the track carries no noise floor.
Times come from the reel's own edit list, so each cue lands on its frame.
Writes out/sfx.wav (48 kHz stereo, float).
"""
import numpy as np
from scipy import signal

import reel_sukkar as R

SR = 48000
DUR = R.TOTAL
N = int(np.ceil(DUR * SR)) + SR
rng = np.random.default_rng(2026)
bus = np.zeros((N, 2), np.float32)


def db(x):
    return 10 ** (x / 20)


def T(d):
    return np.arange(int(d * SR)) / SR


def place(x, t0, gain_db=0.0, pan=0.0):
    """Add mono (constant-power pan) or stereo x at time t0."""
    if x.ndim == 1:
        l, r = np.cos((pan + 1) * np.pi / 4), np.sin((pan + 1) * np.pi / 4)
        x = np.stack([x * l, x * r], 1) * np.sqrt(2)
    i = int(round(t0 * SR))
    if i < 0:
        x, i = x[-i:], 0
    n = min(len(x), N - i)
    if n > 0:
        bus[i:i + n] += (x[:n] * db(gain_db)).astype(np.float32)


def butter(x, kind, f, order=2):
    if kind == "band":
        f = [max(20, f[0]), min(f[1], SR / 2 * 0.98)]
    else:
        f = min(max(20, f), SR / 2 * 0.98)
    sos = signal.butter(order, f, kind, fs=SR, output="sos")
    return signal.sosfilt(sos, x, axis=0)


def norm(x):
    return x / (np.abs(x).max() + 1e-12)


# ------------------------------------------------------------ reverb
def make_ir(length, decay, bright=6000, predelay=0.012, seed=1):
    g = np.random.default_rng(seed)
    n = int(length * SR)
    t = np.arange(n) / SR
    env = np.exp(-t * 6.9 / decay)
    ir = g.standard_normal((n, 2)) * env[:, None]
    ir = butter(ir, "low", bright)
    pd = int(predelay * SR)
    ir = np.vstack([np.zeros((pd, 2)), ir])
    return ir / np.sqrt((ir ** 2).sum(0, keepdims=True))


IR_ROOM = make_ir(1.2, 0.9, 7000, 0.010, 1)
IR_HALL = make_ir(3.5, 2.8, 5000, 0.025, 2)


def verb(x, ir=IR_ROOM, wet=0.25):
    if x.ndim == 1:
        x = np.stack([x, x], 1)
    y = np.stack([signal.fftconvolve(x[:, c], ir[:, c]) for c in range(2)], 1)
    out = np.zeros_like(y)
    out[:len(x)] = x * (1 - wet)
    return out + y * wet * 0.6


# ------------------------------------------------------------ building blocks
def moving_band(noise, fc, bw_oct=1.0, nfft=1024, hop=256):
    """Band-pass white noise whose centre frequency follows fc(t) (array, per sample)."""
    f, t, Z = signal.stft(noise, SR, nperseg=nfft, noverlap=nfft - hop)
    centers = np.interp(t, np.arange(len(fc)) / SR, fc)
    lf = np.log2(np.maximum(f, 1.0))[:, None]
    lc = np.log2(centers)[None, :]
    mask = np.exp(-0.5 * ((lf - lc) / (bw_oct / 2.355)) ** 2)
    _, y = signal.istft(Z * mask, SR, nperseg=nfft, noverlap=nfft - hop)
    return y[:len(noise)]


def env_ar(n, peak_pos, attack_pow=2.2, release_pow=1.6):
    p = np.linspace(0, 1, n)
    return np.where(p < peak_pos, (p / peak_pos) ** attack_pow, ((1 - p) / (1 - peak_pos)) ** release_pow)


def whoosh(t_peak, dur=0.55, f_lo=180, f_hi=2600, gain_db=-14, pan=(-0.7, 0.7), peak_pos=0.62, air=0.6, body=0.6, ir=IR_ROOM, wet=0.22):
    """Cinematic whoosh peaking at t_peak: swept band-passed noise (air) + low body + stereo motion."""
    n = int(dur * SR)
    p = np.linspace(0, 1, n)
    # centre frequency rises to the peak then falls (doppler-like)
    up = np.clip(p / peak_pos, 0, 1)
    dn = np.clip((p - peak_pos) / (1 - peak_pos), 0, 1)
    fc = np.where(p < peak_pos, f_lo * (f_hi / f_lo) ** up ** 1.3, f_hi * (f_lo * 1.6 / f_hi) ** dn ** 0.9)
    a = moving_band(rng.standard_normal(n), fc, 1.1)
    b = butter(rng.standard_normal(n), "low", 260)
    e = env_ar(n, peak_pos)
    x = norm(a) * air * e + norm(b) * body * env_ar(n, peak_pos, 1.6, 1.2)
    pans = np.linspace(pan[0], pan[1], n)
    st = np.stack([x * np.cos((pans + 1) * np.pi / 4), x * np.sin((pans + 1) * np.pi / 4)], 1) * np.sqrt(2)
    st = verb(norm(st), ir, wet)
    place(st, t_peak - peak_pos * dur, gain_db)


def whip(t_peak, gain_db=-11, pan=(0.8, -0.8)):
    whoosh(t_peak, dur=0.30, f_lo=500, f_hi=6500, gain_db=gain_db, pan=pan, peak_pos=0.55, air=1.0, body=0.35, wet=0.12)


def hit(t, size=1.0, gain_db=-8, ir=IR_HALL, wet=0.35, sub_f=(70, 34)):
    """Cinematic impact: pitched sub drop + punch + transient crack, with a room/hall tail."""
    d = 1.6 + 1.6 * size
    tt = T(d)
    f = sub_f[1] + (sub_f[0] - sub_f[1]) * np.exp(-tt * 7)
    sub = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-tt * (2.6 / size))
    punch = butter(rng.standard_normal(len(tt)), "low", 900) * np.exp(-tt * 28)
    crack = butter(rng.standard_normal(len(tt)), "high", 3000) * np.exp(-tt * 120)
    x = norm(sub) * 1.0 + norm(punch) * 0.45 + norm(crack) * 0.18
    x = x * np.clip(tt / 0.002, 0, 1)
    place(verb(norm(x), ir, wet), t, gain_db)


def boom(t, gain_db=-7):
    d = 5.0
    tt = T(d)
    f = 30 + 34 * np.exp(-tt * 3.2)
    sub = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-tt * 0.95)
    rumble = butter(rng.standard_normal(len(tt)), "low", 180) * np.exp(-tt * 1.6)
    click = butter(rng.standard_normal(len(tt)), "band", (1500, 7000)) * np.exp(-tt * 160)
    x = norm(sub) + norm(rumble) * 0.35 + norm(click) * 0.10
    x = x * np.clip(tt / 0.003, 0, 1)
    place(verb(norm(x), IR_HALL, 0.4), t, gain_db)


def swell(t_end, dur=0.8, gain_db=-14, bright=True):
    """Reverse-reverb style swell that rushes into t_end (then stops)."""
    n = int(dur * SR)
    p = np.linspace(0, 1, n)
    x = butter(rng.standard_normal(n), "high", 2500 if bright else 600)
    x = moving_band(x, 1200 * (9 ** p), 2.0)
    x = norm(x) * p ** 3.2
    st = np.stack([x, np.roll(x, 37)], 1)
    place(st, t_end - dur, gain_db)


def shimmer(t, dur=2.2, gain_db=-20, f_lo=2500, f_hi=8500):
    tt = T(dur)
    x = np.zeros(len(tt))
    for k in range(18):
        f = rng.uniform(f_lo, f_hi)
        x += np.sin(2 * np.pi * f * tt + rng.uniform(0, 6)) * (0.55 + 0.45 * np.sin(2 * np.pi * rng.uniform(3, 9) * tt + rng.uniform(0, 6)))
    x = x * np.exp(-tt * 2.0) * np.clip(tt / 0.03, 0, 1)
    place(verb(norm(x), IR_HALL, 0.55), t, gain_db)


def riser(t0, t1, gain_db=-16):
    n = int((t1 - t0) * SR)
    p = np.linspace(0, 1, n)
    nz = moving_band(rng.standard_normal(n), 300 * (25 ** p ** 1.8), 1.6)
    f = 110 * (6 ** (p ** 1.7))
    tone = np.sin(2 * np.pi * np.cumsum(f) / SR) + 0.5 * np.sin(2 * np.pi * np.cumsum(f * 1.498) / SR)
    x = (norm(nz) * 0.9 + norm(tone) * 0.35) * p ** 2.4
    st = np.stack([x, np.roll(x, 211)], 1)
    place(st, t0, gain_db)


def tick(t, gain_db=-20, f=3400, pan=0.0):
    """Shutter-like tick: filtered click + tiny metallic tone."""
    tt = T(0.09)
    a = butter(rng.standard_normal(len(tt)), "band", (1800, 9000)) * np.exp(-tt * 380)
    b = np.sin(2 * np.pi * f * tt) * np.exp(-tt * 140) * 0.5
    c = butter(rng.standard_normal(len(tt)), "band", (1800, 9000)) * np.exp(-np.maximum(tt - 0.022, 0) * 420) * (tt > 0.022) * 0.6
    x = norm(a) + b + norm(c) * 0.5 if c.any() else norm(a) + b
    place(verb(norm(x), IR_ROOM, 0.12), t, gain_db, pan)


def flashpop(t, gain_db=-17):
    """Camera-flash pop: bright burst + quick rising whine + soft thump."""
    tt = T(0.45)
    burst = butter(rng.standard_normal(len(tt)), "high", 2500) * np.exp(-tt * 45)
    f = 1800 + 5200 * (1 - np.exp(-tt * 16))
    whine = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-tt * 9) * 0.25
    thump = np.sin(2 * np.pi * 95 * tt) * np.exp(-tt * 30) * 0.5
    x = norm(burst) + whine + thump
    place(verb(norm(x), IR_ROOM, 0.3), t, gain_db)


def clink(t, gain_db=-19, pitch=1.0, pan=0.0, n_hits=1):
    """Surgical-steel clink: inharmonic modal partials with fast decays."""
    tt = T(0.55)
    modes = np.array([2210, 3480, 5120, 6870, 8930, 11200]) * pitch * rng.uniform(0.97, 1.03, 6)
    amps = np.array([1.0, 0.75, 0.55, 0.35, 0.22, 0.12])
    decs = np.array([9, 12, 16, 22, 30, 40]) * rng.uniform(0.85, 1.15, 6)
    x = np.zeros(len(tt))
    for k in range(n_hits):
        off = int(k * rng.uniform(0.045, 0.075) * SR)
        y = np.zeros(len(tt))
        for f, a, d in zip(modes, amps, decs):
            y += a * np.sin(2 * np.pi * f * tt + rng.uniform(0, 6)) * np.exp(-tt * d)
        y += butter(rng.standard_normal(len(tt)), "high", 4000) * np.exp(-tt * 300) * 0.8
        x[off:] += (y * (0.65 ** k))[:len(x) - off]
    place(verb(norm(x), IR_ROOM, 0.18), t, gain_db, pan)


def snap(t, gain_db=-18, pan=0.0):
    """Latex glove snap: rubbery band burst + thump."""
    tt = T(0.25)
    burst = butter(rng.standard_normal(len(tt)), "band", (900, 5500)) * np.exp(-tt * 70)
    rubber = np.sin(2 * np.pi * 520 * tt * (1 - 0.3 * tt)) * np.exp(-tt * 45) * 0.5
    thump = np.sin(2 * np.pi * 140 * tt) * np.exp(-tt * 40) * 0.7
    x = (norm(burst) + rubber + thump) * np.clip(tt / 0.0015, 0, 1)
    place(verb(norm(x), IR_ROOM, 0.15), t, gain_db, pan)


def stretch(t, dur=0.35, gain_db=-24, pan=0.0):
    """Latex stretch / squeak."""
    tt = T(dur)
    f = 700 + 500 * np.sin(np.pi * tt / dur)
    sq = np.sin(2 * np.pi * np.cumsum(f) / SR) * (0.5 + 0.5 * np.sin(2 * np.pi * 38 * tt))
    fr = butter(rng.standard_normal(len(tt)), "band", (1500, 6000)) * 0.4
    x = (sq * 0.6 + norm(fr) * 0.5) * np.sin(np.pi * tt / dur) ** 1.5
    place(verb(norm(x), IR_ROOM, 0.15), t, gain_db, pan)


def rustle(t, dur=0.9, gain_db=-22, lo=1200, hi=7500, density=60, pan=0.0, grain=(0.004, 0.03)):
    """Fabric / paper rustle: dense random grains of band-passed noise under a soft envelope."""
    tt = T(dur)
    x = np.zeros(len(tt))
    for _ in range(int(density * dur)):
        s = rng.integers(0, len(tt) - 1)
        L = int(rng.uniform(*grain) * SR)
        g = rng.standard_normal(L) * np.hanning(L) * rng.uniform(0.3, 1.0)
        x[s:s + L] += g[:len(x) - s]
    x = butter(x, "band", (lo, hi))
    x = norm(x) * np.sin(np.pi * np.clip(tt / dur, 0, 1)) ** 0.8
    place(verb(x, IR_ROOM, 0.15), t, gain_db, pan)


def beep(t, gain_db=-28, f=960):
    """Patient-monitor beep: soft-edged sine with a faint octave."""
    tt = T(0.16)
    e = np.clip(tt / 0.006, 0, 1) * np.clip((0.12 - tt) / 0.02, 0, 1)
    x = (np.sin(2 * np.pi * f * tt) + 0.15 * np.sin(2 * np.pi * 2 * f * tt)) * e
    place(verb(x, IR_ROOM, 0.2), t, gain_db, 0.15)


def heartbeat(t, gain_db=-15):
    """Lub-dub: two low thumps."""
    for off, g in ((0.0, 0.0), (0.24, -4.0)):
        tt = T(0.35)
        f = 48 + 30 * np.exp(-tt * 25)
        x = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-tt * 14) * np.clip(tt / 0.004, 0, 1)
        x += butter(rng.standard_normal(len(tt)), "low", 220) * np.exp(-tt * 30) * 0.3
        place(verb(norm(x), IR_ROOM, 0.15), t + off, gain_db + g)


# ------------------------------------------------------------ the cue sheet
def cues():
    # boundaries of every shot, straight from the edit list
    bounds, prev = [], 0.0
    for end_s, spec, trans in R.TL:
        bounds.append((prev, end_s, spec, trans))
        prev = end_s
    cut = [b[0] for b in bounds]      # start time of each shot
    # --- cold open: one accent per flash cut
    # hands, loupes, instruments, ceiling light, IV, monitor, tray, OR lamp, hands, loupes, monitor, drape
    kinds = ["clink", "tick", "clink", "flash", "tick", "beep", "clink", "flash", "clink", "tick", "beep", "whoosh"]
    riser(0.0, 2.15, gain_db=-18)
    for i, k in enumerate(kinds):
        t = cut[i]
        pan = (-0.35, 0.3, -0.2, 0.25, -0.3, 0.35)[i % 6]
        if k == "snap":
            snap(t + 0.01, -11, pan=-0.2)
        elif k == "tick":
            tick(t, -15, f=rng.uniform(2800, 4200), pan=pan)
        elif k == "clink":
            clink(t + 0.01, -15, pitch=rng.uniform(0.9, 1.15), pan=pan)
        elif k == "flash":
            flashpop(t, -13)
        elif k == "beep":
            beep(t + 0.01, -20)
        elif k == "whoosh":
            swell(2.22, dur=0.32, gain_db=-11)
    # cut to the breath (dip into the IV drip): the hit's tail is the space
    hit(cut[12], size=1.0, gain_db=-9)
    heartbeat(cut[12] + 0.55, gain_db=-16)
    # section 1: monitor heartbeat motif + gentle accents
    t = cut[12] + 0.75
    while t < R.T["b2a"] - 0.3:
        fade = np.interp(t, [cut[12] + 0.75, R.T["b1"] + 1.0, R.T["b2a"] - 1.2, R.T["b2a"] - 0.3], [-36, -31, -31, -38])
        beep(t, fade)
        t += 0.91
    # C8893 -> C9016 dissolve: a soft air move
    whoosh(cut[13], dur=1.0, f_lo=150, f_hi=1500, gain_db=-29, pan=(-0.4, 0.4), peak_pos=0.5, air=0.5, body=0.4)
    # section 2: into / out of the interview, hands, team
    th1 = next(i for i, b in enumerate(bounds) if b[2].get("kind") == "th")
    whoosh(cut[th1], dur=0.62, gain_db=-17, pan=(-0.6, 0.6))
    hit(cut[th1] + 0.02, size=0.35, gain_db=-21, ir=IR_ROOM, wet=0.25, sub_f=(90, 45))
    whoosh(cut[th1 + 1], dur=0.55, gain_db=-19, pan=(0.6, -0.6))
    clink(cut[th1 + 2] + 0.08, -23, pitch=0.95, pan=0.3)
    th2 = th1 + 4
    # the OR keeps breathing under the B-roll between the two interview shots
    t = cut[th1 + 1] + 0.35
    while t < cut[th2] - 0.15:
        beep(t, -37)
        t += 0.91
    whoosh(cut[th2], dur=0.55, gain_db=-18, pan=(-0.5, 0.5))
    # section 3: whip into the montage, accents on every cut, riser into the flash
    whip(cut[th2 + 1], gain_db=-12)
    mont = ["tick", "clink", "whoosh", "tick", "tick", "clink", "clink2"]
    for j, k in enumerate(mont):
        t = cut[th2 + 2 + j]
        pan = (0.3, -0.3, 0.2, -0.25, 0.35, -0.2, 0.0)[j]
        if k == "tick":
            tick(t, -18, f=rng.uniform(3000, 4300), pan=pan)
        elif k == "clink":
            clink(t + 0.02, -18, pitch=rng.uniform(0.9, 1.2), pan=pan)
        elif k == "clink2":
            clink(t + 0.02, -17, pitch=1.0, pan=pan, n_hits=2)
        elif k == "whoosh":
            whoosh(t, dur=0.35, f_lo=300, f_hi=4200, gain_db=-20, pan=(-0.5, 0.5), peak_pos=0.5, air=0.9, body=0.3)
    fl = next(i for i, b in enumerate(bounds) if b[3][0] == "flash")
    riser(cut[th2 + 2 + 3] - 0.1, cut[fl] - 0.02, gain_db=-17)
    swell(cut[fl] + 0.02, dur=0.6, gain_db=-14)
    flashpop(cut[fl], -16)
    hit(cut[fl] + 0.03, size=0.7, gain_db=-14, sub_f=(60, 32))
    shimmer(cut[fl], dur=2.6, gain_db=-22)
    # section 4: the facility -- airy, open, a little movement on each dissolve
    for k in range(fl + 1, fl + 5):
        whoosh(cut[k], dur=1.0, f_lo=220, f_hi=2200, gain_db=-25, pan=((-0.5, 0.5) if k % 2 else (0.5, -0.5)), peak_pos=0.5, air=0.7, body=0.25, ir=IR_HALL, wet=0.3)
    curtain = fl + 2
    rustle(cut[curtain] + 0.25, dur=1.2, gain_db=-24, lo=300, hi=3200, density=140, pan=-0.3, grain=(0.03, 0.09))
    # section 5: dip back into the OR, gloving, the mask
    dip = next(i for i, b in enumerate(bounds) if b[3] == ("dip", 14))
    swell(cut[dip], dur=0.9, gain_db=-19, bright=False)
    hit(cut[dip] + 0.02, size=0.8, gain_db=-14, sub_f=(55, 30))
    heartbeat(cut[dip] + 0.45, gain_db=-17)
    stretch(cut[dip] + 0.55, dur=0.35, gain_db=-24, pan=-0.2)
    snap(cut[dip] + 1.65, -18, pan=0.15)
    mask = dip + 1
    rustle(cut[mask] + 0.25, dur=1.1, gain_db=-24, lo=400, hi=4200, density=120, pan=0.25, grain=(0.02, 0.07))
    snap(cut[mask] + 1.45, -24, pan=0.3)
    # section 6: hero -- the monitor returns and carries us out
    hero = mask + 1
    whoosh(cut[hero], dur=0.9, f_lo=150, f_hi=1500, gain_db=-28, pan=(-0.4, 0.4), peak_pos=0.5, air=0.5, body=0.4)
    t = cut[hero] + 0.3
    card = len(bounds) - 1
    while t < cut[card] - 0.5:
        lvl = np.interp(t, [cut[hero], R.T["b6"] + 0.5, R.END_HOLD - 1.0, R.END_HOLD + 0.4, cut[card] - 0.5], [-35, -31, -26, -27, -33])
        beep(t, lvl)
        t += 0.91
    # end card: the title lands
    boom(cut[card] + 0.15, gain_db=-8)
    shimmer(cut[card] + 0.15, dur=3.0, gain_db=-24, f_lo=3000, f_hi=9500)
    tick(cut[card] + 0.78, -27, f=4800)


if __name__ == "__main__":
    import subprocess
    cues()
    out = bus[: int(DUR * SR)]
    peak = np.abs(out).max()
    print(f"sfx peak {20*np.log10(peak):.1f} dBFS before trim")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "f32le", "-ar", str(SR), "-ac", "2", "-i", "-",
                    "-c:a", "pcm_f32le", "out/sfx.wav"], input=out.astype(np.float32).tobytes(), check=True)
    print("wrote out/sfx.wav")
