"""pehle_wala_sfx.py - SFX layer of Reel 1 / C26 "Pehle Wala Hi Theek Tha (v1 se v27 tak)". Owner: sound-designer.

Binding plan: brand_reels/design/reels/pehle_wala/BRIEF.md r2 section 11 (cue list, custom sounds, bed), section 7 (frame-exact
beat sheet), section 6.3 / 6.3.1 (pin landings, the client's marker in the loop), section 9 (VO rules: hero hits in VO gaps, no
VO 25.067-28.133); SLATE section 3.1 (sound motif = the pin "thock" + slot_tick on the counter) and section 5.1 (-14 LUFS,
TP <= -2.0 dBTP, VO >= 8 LU over the bed, <= 3 sounds on one instant, one drop-out at the reveal); MUSIC_pehle_wala.md (D minor,
i-VI-III-VII one chord per bar; tonal SFX pitched to chord tones). Measured VO: VO_TIMING.md / <RW>/vo/*.words.json (the r2
"measured-VO dependents" of BRIEF section 11 are decided here from the real Vlad words). Cue sheet + numbers: SOUND.md.

What this module owns
    register()          adds the 6 local sounds to audio.SOUNDS (idempotent) + epic_sfx and sfx_jawad sounds
    raw_cues(hook)      the brief's cue list ('A' public hook, 'B' Trial hook), frame-exact, pins chosen from the measured words
    cues(hook='A')      raw_cues -> VO fit (sfx_jawad.fit_under_vo for every cue not already designed for the voice) + the
                        hero/tail carve windows from the measured speech. This is what a timeline module imports.
    BED, BED_GAIN_DB    audio.mix fallback form of the bed (edit_suite at -32; drop-out off; held breath -8 rel.)
    mix_loop(...)       audio.mix's chain on a LOOP (tails past DUR land on t = 0, cues before 0 on the loop end, no tail
                        fade), plus: exact bed levels (circular edit_suite, 4 ms gates), the drop-out gate (every SFX that
                        started before 25.0667 is cut there, with its room tail), per-cue carve windows (gain + low-pass
                        crossfade under later speech). build() uses it; never audio.mix for this reel.
    build(hook)         SFX stem -> <RW>/audio/pehle_wala_sfx_<hook>_stem.wav (+ _fx / _bed, overview PNG, cues.json, report)
    rough(hook)         epic_mix.mix_reel (VO + SFX stem + music) on a loop-padded copy -> <RW>/audio/pehle_wala_<hook>_rough_*.wav
    audition()          local sounds -> <RW>/audio/audition/*.wav + spectrogram PNG + qc + pitch in cents

Local sounds (BRIEF 11; pitches measured with the bible's f0_of on the rendered sound, chord tones of D minor)
    pin_thock            glass_tap pitched to D7 (2349.3 Hz) at -8 dB leading impact_soft (0 dB) by 2 ms, lp 6000. hit 0.006
    pin_thock_dark       pin_thock low-passed at 1100 Hz (pins that land inside a spoken word)
    pin_thock_mummy      glass_tap -> A6 (1760 Hz) -8 + impact_soft 0 + sub_drop(dur 0.6) -14 lp 120 (Owner ki Mummy's pins)
    pin_thock_mummy_dark the Mummy thock low-passed at 1100 Hz
    pin_thock_big        glass_tap -> D6 (1174.7 Hz) -6 + impact_big 0: the payoff landing "Pehle wala hi theek tha."
    pw_tape_rewind       the D9 rewind as SOUND (BRIEF: processing of the reel's own music + SFX, not the VO): 25 ms Hann grains
                         every 8 ms read BACKWARDS from tau_a(t) = 26.1333 - 26.1333 * u^3 (u over 26.3333 -> 27.7333, the
                         jawad_tx D9 curve minus its 0.2 s press offset so the read never enters the tape-stop), each grain
                         resampled by |dtau/dt| (0 -> 56x), amplitude sqrt(min(rate, 1)), lp 3000; hit = END (27.7333)
    The brief's pitch multipliers (1.0926 / 0.8186 / 0.5463) assumed glass_tap f0 = 2150 Hz; it measures 2096.3 Hz, so they
    land 44 cents flat. The multipliers here are recomputed from the measurement (audition() prints the cents).

CLI (run in pipeline/jawad_reels; heavy runs through tools/heavy.sh)
    python3 pehle_wala_sfx.py cues [--hook A|B]       cue table after the VO fit
    python3 pehle_wala_sfx.py audition                local sounds -> <RW>/audio/audition/
    python3 pehle_wala_sfx.py build [--hook A|B|AB]   SFX stem(s), -18 LUFS, TP <= -2.0 dBTP, loop-exact
    python3 pehle_wala_sfx.py rough [--hook A|B|AB]   rough mix with the VO and music -> -14 LUFS, TP <= -2.0 dBTP
Render the picture with  render.py pehle_wala --no-sfx-build --audio <final mix wav>  (music-supervisor's mix, or the rough).
"""
import argparse
import functools
import hashlib
import json
import math
import os
import subprocess
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, '..', '..'))
SFXDIR = os.path.join(REPO, 'workspace', 'brand_reels', 'sfx')
for _p in (SFXDIR, HERE):                       # HERE first: `audio` is this project's toolkit copy
    if _p in sys.path:
        sys.path.remove(_p)
    sys.path.insert(0, _p)

import audio as A  # noqa: E402
from audio import SR, _n, _st, _finish, _fade, undb, db, lp  # noqa: E402
import epic_sfx as ES  # noqa: E402  (shared, read-only)
import sfx_jawad as SJ  # noqa: E402  (shared, read-only: fit_under_vo, hero_windows)

MODULE = 'pehle_wala'
FPS, BPM = 30, 112.5
DUR = 1024 / FPS                                # 34.1333 s = 16 bars (BRIEF 0)
N = _n(DUR)
assert N == 1638400


def F(f):
    """frame -> seconds"""
    return f / FPS


RW = os.path.join(REPO, 'workspace', 'jawad_reels', MODULE)
AUD = os.path.join(RW, 'audio')
VO_DIR = os.path.join(RW, 'vo')
VO = {'A': os.path.join(VO_DIR, 'pehle_wala_vo_A.wav'), 'B': os.path.join(VO_DIR, 'pehle_wala_vo_B.wav')}
WORDS = {'A': os.path.join(VO_DIR, 'pehle_wala_vo_A.words.json'), 'B': os.path.join(VO_DIR, 'pehle_wala_vo_B.words.json')}
MUSIC = {'A': os.path.join(RW, 'music', 'music_full.wav'), 'B': os.path.join(RW, 'music', 'music_hookb.wav')}
MUSIC_JSON = os.path.join(RW, 'music', 'music_full.json')

TARGET_LUFS, TP_CEILING = -18.0, -2.0           # SFX stem (bible 4.1); the final mix is -14 / -2.0 (epic_mix)
TARGET_FINAL = -14.0
SPLICE = F(80)                                  # hook A and B are frame-identical from here
T_DROP0, T_DROP1 = F(752), F(760)               # 25.0667-25.3333: true silence (BRIEF 7 row 38)
T_PAYOFF = F(768)                               # 25.6000 (bar 12): the reveal, loudest moment
T_PRESS = F(784)                                # 26.1333: Ctrl+Z press (D9 window start)
T_REW0 = T_PRESS + 6 / FPS                      # 26.3333: rewind starts (jawad_tx t_r = t0 + press frames)
T_RESTORE = F(832)                              # 27.7333: v1 restored (D9 cut)
R_REW = T_PRESS                                 # D9 R = 26.1333 (BRIEF 8)
T_CARD = F(896)                                 # 29.8667: end card
GATE_EDGE = 0.004                               # drop-out edges (bible 4.4: 4 ms)

# ------------------------------------------------------------------------------------------------- pitch (measured)
GT_F0 = 2096.3                                  # glass_tap f0 at pitch 1.0 (f0_of, 2026-10-09)
POP_F0, CLICK_F0, TICK_F0, BUB_F0 = 1071.6, 1653.6, 3788.4, 1504.0
HZ = dict(D6=1174.66, D7=2349.32, A6=1760.00, A7=3520.00, C6=1046.50, F6=1396.91)
GT_D7 = round(HZ['D7'] / GT_F0, 4)              # 1.1207  pin_thock, end-card tap (bar 14 = Bb: D is a chord tone)
GT_A6 = round(HZ['A6'] / GT_F0, 4)              # 0.8396  Mummy's thock (bar 6 = F: A is a chord tone)
GT_D6 = round(HZ['D6'] / GT_F0, 4)              # 0.5603  payoff + restore taps (Dm)
POP_D6 = round(HZ['D6'] / POP_F0, 4)            # 1.0962  pops on Dm / Bb bars
POP_C6 = round(HZ['C6'] / POP_F0, 4)            # 0.9766  pop on the F bar (C is the 5th)
CLICK_A6 = round(HZ['A6'] / CLICK_F0, 4)        # 1.0643  chip click on the Dm bar (1653.6 Hz = G#6 would be the tritone)
TICK_A7 = round(HZ['A7'] / TICK_F0, 4)          # 0.9292  rewind ticks (ui_tick 3788 Hz -> A7)
BUB_D6 = 0.78                                   # bubble_pop is a chirp (not in the bible's tonal list): its FFT peak jumps
                                                # with pitch; 0.78 puts it on D6 -5 c (seed 0; Bb bar: D is a chord tone)


# =============================================================================================== local sounds
def _place(buf, x, start):
    i = _n(start)
    x = np.asarray(x, dtype=np.float64)
    buf[i:i + len(x)] += x[:len(buf) - i]


def _layered(parts, hit, name, lp_hz=None):
    """parts: [(sound name, params, gain_db, hit time inside the result, lp)] -> Sfx at its natural level (the layer gains
    are the recipe). Every layer is placed so its own designed hit sits at its time; the result is shifted so no layer
    starts before 0 (the returned hit moves with it)."""
    snd = [(A.sound(nm, **p), g, h, f) for nm, p, g, h, f in parts]
    shift = max(0.0, max(x.hit - h for x, g, h, f in snd))
    L = max(_n(h + shift - x.hit) + len(x) for x, g, h, f in snd) + _n(0.02)
    out = np.zeros((L, 2))
    for x, g, h, f in snd:
        y = np.asarray(x, dtype=np.float64) * undb(g)
        if f:
            y = lp(y, f, 2)
        _place(out, y, h + shift - x.hit)
    if lp_hz:
        out = lp(out, lp_hz, 2)
    return _finish(out, hit + shift, A.momentary_max(out) - A.REF_LUFS, name)


def pin_thock(seed=0):
    """The sound motif: a glassy D7 tick 2 ms ahead of a felt thump. hit = the glass transient (0.006 s)."""
    return _layered([('glass_tap', dict(pitch=GT_D7, seed=seed), -8.0, 0.006, None),
                     ('impact_soft', dict(seed=seed), 0.0, 0.008, None)], 0.006, 'pin_thock', lp_hz=6000.0)


def pin_thock_dark(seed=0):
    """pin_thock under a spoken word: low-passed at 1100 Hz (cue it at -6 dB)."""
    x0 = pin_thock(seed)
    y = lp(np.asarray(x0, dtype=np.float64), 1100.0, 2)
    return _finish(y, x0.hit, A.momentary_max(y) - A.REF_LUFS, 'pin_thock_dark')


def pin_thock_mummy(seed=0):
    """Owner ki Mummy's pin: the thock a fifth lower (A6) with a short sub. hit 0.006."""
    return _layered([('glass_tap', dict(pitch=GT_A6, seed=seed), -8.0, 0.006, None),
                     ('impact_soft', dict(seed=seed), 0.0, 0.008, None),
                     ('sub_drop', dict(dur=0.6, seed=seed), -14.0, 0.008, 120.0)], 0.006, 'pin_thock_mummy',
                    lp_hz=6000.0)


def pin_thock_mummy_dark(seed=0):
    x0 = pin_thock_mummy(seed)
    y = lp(np.asarray(x0, dtype=np.float64), 1100.0, 2)
    return _finish(y, x0.hit, A.momentary_max(y) - A.REF_LUFS, 'pin_thock_mummy_dark')


def pin_thock_big(seed=0):
    """The payoff landing: D6 glass over impact_big (hit 0.006 = the glass transient, the boom 2 ms later)."""
    return _layered([('glass_tap', dict(pitch=GT_D6, seed=seed), -6.0, 0.006, None),
                     ('impact_big', dict(seed=seed), 0.0, 0.008, None)], 0.006, 'pin_thock_big')


# ------------------------------------------------------------------------------------------------- D9 rewind
def tau_picture(t):
    """jawad_tx _tx_undo: tau = t_r - R * in_cubic(u), u = (t - t_r) / (c - t_r) (the picture's rewind clock)."""
    u = np.clip((np.asarray(t, dtype=np.float64) - T_REW0) / (T_RESTORE - T_REW0), 0, 1)
    return T_REW0 - R_REW * u ** 3


def tau_audio(t):
    """The rewind's read clock: the picture's minus its 0.2 s press offset (BRIEF 11: tau = 26.1333 - 26.1333 u^3), so the
    read stays at or before the music's tape-stop point 26.1333."""
    return tau_picture(t) - (T_REW0 - T_PRESS)


VERSION_FRAMES = [32, 64, 96, 128, 192, 224, 256, 288, 320, 352, 384, 400, 416, 432, 448, 480, 496, 512, 544, 576, 592,
                  608, 624, 640, 656, 672]          # v2 .. v27: the counter steps (BRIEF 6.3)
assert len(VERSION_FRAMES) == 26


def rewind_ticks(merge=0.025):
    """Reel times where the picture's rewind clock crosses each version step (26 crossings, v27 -> v1); ticks closer
    than `merge` are merged (the earlier one is kept)."""
    out = []
    for f in sorted(VERSION_FRAMES, reverse=True):
        c = F(f)
        u = ((T_REW0 - c) / R_REW) ** (1.0 / 3.0)
        t = T_REW0 + u * (T_RESTORE - T_REW0)
        if out and t - out[-1][0] < merge:
            continue
        out.append((t, f))
    return out


def _rewind_source(hook):
    """The reel's own music + SFX (not the VO) as heard before the press, each at -18 LUFS (their mix balance)."""
    m = _stereo_n(MUSIC[hook], N)
    m = m * undb(-18.0 - A.loudness(m))
    cl = [c for c in cues(hook, _with_rewind=False) if float(c['t']) < T_PRESS + 0.5]
    s = np.zeros((N + _n(8.0), 2))
    for c in cl:
        c = A._norm_cue(c)
        y, hit = A._render_cue(c, None)
        start = float(c['t']) - (hit if c['align'] == 'hit' else 0.0)
        if start < 0:
            y, start = y[_n(-start):], 0.0
        _place(s, y, start)
    s = s[:N]
    s = s * undb(-18.0 - A.loudness(s))
    return m + s


@functools.lru_cache(maxsize=4)
def _rewind_render(hook, seed):
    src = _rewind_source(hook)
    r = np.random.default_rng(1000 + seed)
    d = T_RESTORE - T_REW0
    L = _n(d)
    gl, hop = _n(0.025), _n(0.008)
    win = np.hanning(gl)
    out = np.zeros((L + gl, 2))
    norm = np.zeros(L + gl)
    for o in range(0, L, hop):
        oo = int(np.clip(o + r.integers(-_n(0.002), _n(0.002) + 1), 0, L - 1))
        tc = T_REW0 + (oo + gl / 2) / SR
        u = min(max((tc - T_REW0) / d, 0.0), 1.0)
        p = T_PRESS - R_REW * u ** 3                       # tau_audio at the grain centre
        rate = min(R_REW * 3 * u * u / d, 64.0)
        idx = np.clip(p * SR - (np.arange(gl) - gl / 2) * rate, 0, len(src) - 1)   # read backwards around p
        g = np.stack([np.interp(idx, np.arange(len(src)), src[:, ch]) for ch in (0, 1)], 1)
        out[oo:oo + gl] += g * (win * math.sqrt(min(rate, 1.0)))[:, None]
        norm[oo:oo + gl] += win
    out = out / np.maximum(norm, 1e-3)[:, None]
    out = out[:L]
    out = lp(out, 3000.0, 4)
    # partial leveller (tape rewinds get louder, not quieter, as they speed up): the reversed payoff beat at the start is
    # ~10 dB over the version clutter it then races through; 120 ms RMS, ratio 0.6, gain -3 .. +12 dB, silence stays silent
    from scipy.ndimage import uniform_filter1d
    env = np.sqrt(uniform_filter1d(np.square(out).mean(1), _n(0.12)) + 1e-12)
    gdb = np.clip(-0.6 * (20 * np.log10(env / env.max())), -3.0, 12.0)
    out = out * undb(uniform_filter1d(gdb, _n(0.05)))[:, None]
    out[-_n(0.004):] *= np.linspace(1, 0, _n(0.004))[:, None]      # hard stop at the D9 cut, 4 ms
    out = np.concatenate([out, np.zeros((_n(0.02), 2))])
    return out


def pw_tape_rewind(seed=0, hook='A'):
    """The D9 Ctrl+Z rewind built from this reel's music + SFX read backwards (hit = the END, 27.7333 in the reel)."""
    x = _rewind_render(hook, int(seed))
    return _finish(x, T_RESTORE - T_REW0, -3.0, 'pw_tape_rewind', fin=0.02, fout=0.004,
                   keep_until=T_RESTORE - T_REW0)


META = dict(   # name: (category, character, use, send)
    pin_thock=('impact', 'glass tick in D7 2 ms ahead of a felt thump', 'every client pin landing (the sound motif)', -18),
    pin_thock_dark=('impact', 'pin_thock low-passed 1100 Hz', 'pin landings inside a spoken word', -22),
    pin_thock_mummy=('impact', 'pin thock a fifth lower (A6) + short sub', "Owner ki Mummy's pins", -18),
    pin_thock_mummy_dark=('impact', 'Mummy thock low-passed 1100 Hz', 'Mummy pins inside a spoken word', -22),
    pin_thock_big=('impact', 'D6 glass over impact_big', 'the payoff pin (loudest moment)', -22),
    pw_tape_rewind=('transition', "the reel's own music+SFX rewound (granular, accelerating backwards)", 'D9 Ctrl+Z x26',
                    -24),
)
LOCAL = tuple(META)


def register():
    ES.register(samples=False)
    SJ.register()
    for n, (cat, ch, use, send) in META.items():
        if n not in A.SOUNDS:
            A._register(cat, ch, use, send=send)(globals()[n])
    return list(LOCAL)


# =============================================================================================== VO words
def _stereo_n(path, n):
    x = np.asarray(A.read_wav(path)[0], dtype=np.float64)
    x = _st(x)
    return np.pad(x[:n], ((0, max(0, n - len(x))), (0, 0)))


@functools.lru_cache(maxsize=4)
def _words(hook):
    with open(WORDS[hook]) as fh:
        w = json.load(fh)
    return tuple((float(x['start']), float(x['end']), x['word']) for x in w)


def word_at(t, hook='A', pad=0.06):
    """The spoken word whose (padded) window contains t, else None."""
    for a, b, wd in _words(hook):
        if a - pad <= t <= b + pad:
            return wd
    return None


# =============================================================================================== cue sheet
PINS = [   # (frame, kind, marker-tip x, event) BRIEF 6.3 (pin 27 = the payoff)
    (8, 'client', 470, 'pin 1 "Logo thora bara?"'), (64, 'client', 560, 'pin 2 "Aur bara." v3'),
    (96, 'client', 560, 'pin 3 "Thora left." v4'), (128, 'client', 515, 'pin 4 "Thora aur pop karo" v5'),
    (192, 'client', 250, 'pin 5 "Background white kar do" v6'), (224, 'client', 515, 'pin 6 "Bhaap nazar nahi aa rahi" v7'),
    (256, 'client', 540, 'pin 7 "Music thora energetic" v8'), (288, 'client', 600, 'pin 8 "Glass thora chamkao" v9'),
    (320, 'client', 700, 'pin 9 "Font fun wala karo" v10'), (352, 'client', 810, 'pin 10 "Har cheez pe shadow" v11'),
    (384, 'mummy', 150, 'RE-HOOK Mummy "Mujhe pasand nahi aaya." v12'), (400, 'mummy', 150, 'Mummy card 2 v13'),
    (416, 'mummy', 150, 'Mummy card 3 "Aur glitter." v14'), (432, 'mummy', 150, 'Mummy card 4 "Logo bhi bara." v15'),
    (448, 'client', 515, 'pin 15 "Thora cinematic" v16'), (480, 'client', 840, 'pin 16 "Price bhi daal do" v17'),
    (496, 'client', 515, 'pin 17 "Bhaap aur zyada" v18'), (512, 'client', 540, 'pin 18 "Sab kuch thora bara" v19'),
    (544, 'client', 540, 'pin 19 "Call now bhi likho" v20'), (576, 'client', 260, 'pin 20 "Aur pop." v21'),
    (592, 'client', 400, 'pin 21 "Logo aur bara." v22'), (608, 'client', 800, 'pin 22 "Shadow kam karo" v23'),
    (624, 'client', 800, 'pin 23 "Shadow wapas." v24'), (640, 'client', 540, 'pin 24 "Aur energetic" v25 (D7)'),
    (656, 'client', 400, 'pin 25 "Thora left." v26'), (672, 'client', 400, 'pin 26 "Thora right." v27'),
]
PAN_K = 0.4                                     # pan = PAN_K * (x - 540) / 540 (screen x of the element)
PAN_COUNTER = 0.3                               # the version counter chip sits top-right (x 838-978)
SLOT = dict(n=3, dur=0.133)                     # the counter's roll: 3 ticks over 4 frames, landing on the step


def _pan(x):
    return round(PAN_K * (x - 540.0) / 540.0, 3)


def raw_cues(hook='A'):
    """BRIEF 11 cue list for the hook, frame-exact; pins dark where they land inside a measured word ('designed' = the
    level/filter already accounts for the voice, so the VO fit leaves it alone)."""
    c = []

    def add(t, name, g=0.0, ev='', **kw):
        d = dict(t=round(float(t), 4), name=name, gain_db=float(g), ev=ev)
        d.update(kw)
        c.append(d)
    # ---------------------------------------------------------------------------------------------- the pins + counter
    for f, kind, x, ev in PINS:
        t = F(f)
        if hook == 'B' and t < SPLICE:
            continue                                # hook B's head is the frozen v27 + D1 scrub (below)
        inside = word_at(t, hook)
        base = 'pin_thock_mummy' if kind == 'mummy' else 'pin_thock'
        if inside:
            add(t, base + '_dark', -6, ev + ' (inside "%s")' % inside, pan=_pan(x), designed='pin in word')
        else:
            add(t, base, 0, ev, pan=_pan(x), designed='pin in gap')
    for f in VERSION_FRAMES:
        t = F(f)
        if hook == 'B' and t < SPLICE:
            continue
        g = -14 if (F(400) <= t <= F(432) or F(576) <= t <= F(624)) else -12
        kw = dict(designed='brief -14 under L7/L9') if g == -14 else {}
        add(t, 'slot_tick', g, 'counter v%d' % (VERSION_FRAMES.index(f) + 2), params=dict(SLOT), pan=PAN_COUNTER, **kw)
    # ---------------------------------------------------------------------------------------------- hook heads
    if hook == 'A':
        add(0.0, 'impact_soft', -6, 'f0 transient: v1 ad + the marker mid-glide (loop landing)',
            designed='brief pre-lap: VO onset 0.10 (<= 0.3 rule)')
        add(F(12), 'ui_click', -10, 'chip Approved -> Changes requested', hp=4000, pan=0.2,
            params=dict(pitch=CLICK_A6), designed='hp 4000 under "Bas ek"')
        add(F(16), 'shimmer', -10, 'lockup BAS EK / chhota sa / CHANGE readable', hp=5500, designed='hp 5500 under "ek"')
        add(F(32), 'pop', -10, 'v2: logo x2 (POP)', lp=1100, params=dict(pitch=POP_D6), designed='lp 1100 under "chhota"')
        add(F(64), 'whoosh_fast', -8, 'pin 2: logo x3, wordmark runs off the ad', pan=0.1)
    else:
        add(0.0, 'trailer_hit', -6, 'hook B f0: the raw v27 mess', hero=True)
        add(0.0, 'glitch_short', -4, 'hook B f0: the raw v27 mess (glitch)', dur=0.1)
        add(0.40, 'shimmer', -10, 'hook B: focus panel + "26" key rising', hp=5500, designed='hp 5500 under "26"')
        add(F(50), 'timeline_scrub', -8, 'hook B: D1 scrub v27 -> v3', align='start', hp=5000,
            params=dict(duration=0.667, speed=2.5), designed='hp 5000 under "client ne kaha"')
        add(2.0, 'ui_tick', -12, 'hook B: D1 playhead tick', params=dict(pitch=TICK_A7))
        add(F(70), 'ui_click', -6, 'hook B: D1 snap onto the marker (cut f70)', hp=4000, params=dict(pitch=CLICK_A6),
            designed='hp 4000 under "kaha..."')
        add(SPLICE, 'impact_soft', -4, 'hook B: splice f80, full frame on the body')
    # ---------------------------------------------------------------------------------------------- the spine (both hooks)
    add(F(96), 'swish_small', -10, 'pin 3: logo slides -72 px', lp=1100, pan=-0.1)
    add(F(128), 'flash_hit', -4, 'L3 push 0.5 on pin 4 (saturation spike)')
    add(F(130), 'pop', -6, 'GOLD NEW burst POPs in (f130)', params=dict(pitch=POP_D6), pan=0.25)
    add(F(192), 'downlifter', -10, 'cream fills the ad (f192-f204)', params=dict(dur=0.3), pan=-0.2)
    add(F(224), 'toggle_on', -10, 'steam gets its cartoon outline')
    add(F(256), 'impact_soft', -6, 'pin 7: beat shake starts, drums in')
    add(F(288), 'sparkle', -6, 'four sparkles appear on the glass', pan=0.05)
    add(F(320), 'bubble_pop', -6, 'garam -> parody font, wobble', params=dict(pitch=BUB_D6), pan=0.25)
    add(F(352), 'card_slide', -8, 'hard drop shadows on every ad graphic', pan=0.3)
    add(F(384), 'glitch_short', -6, 'D7 RGB shock (re-hook)', dur=0.1)
    add(F(384), 'whip', -8, 'D7 RGB shock (re-hook)', params=dict(direction=1))
    add(F(400), 'whoosh_slow', -12, 'cream eases back to dark', lp=1000, designed='lp 1000 under "Mummy"')
    add(F(416), 'shimmer', -12, 'glitter x2', hp=5500, pan=-0.2, designed='hp 5500 under "review"')
    add(F(432), 'pop', -12, 'logo x1.25', lp=1100, params=dict(pitch=POP_C6), designed='lp 1100 under "karengi"')
    add(F(448) - 0.022, 'braam', -4, 'pin 15 "Thora cinematic": letterbox, flares, slow-mo (hero). Cued at its START: its '
        'energy begins at its own t=0 (onset 14.913 = -20 ms), designed hit +18 ms, brass blat peak +110 ms of f448; the '
        'f448 cluster (pin_thock + flash_hit crack) reads +12 ms in qa_measure', align='start', params=dict(dur=2.0),
        ev_t=round(F(448), 4))
    add(F(448), 'flash_hit', -6, 'L3 push 0.6 on "Thora cinematic"')
    add(F(480), 'card_slide', -8, '50% OFF ribbon SLAMs in', lp=1100, pan=0.4, designed='lp 1100 under "cinematic"')
    add(F(496), 'whoosh_slow', -10, 'steam x3, rising', carve=True)
    add(F(512), 'air_zoom', -6, 'pin 18 "Sab kuch thora bara": everything x1.2')
    add(F(512), 'flash_hit', -8, 'L3 push 0.4 (the 50 % pattern break)')
    add(F(544), 'card_slide', -4, 'CALL NOW pill SLAMs in')
    add(F(576), 'pop', -8, 'second starburst POPs in', params=dict(pitch=POP_D6), pan=-0.25)
    add(F(584), 'clock_tick', -18, 'clock chip "3:47 AM" ticking (from the 2nd 8th: f576 already has 3 starts)',
        hp=4500, params=dict(n=7, bpm=225.0), designed='-18 hp 4500 under L9')
    add(F(592), 'whoosh_fast', -10, 'pin 21: logo x1.2')
    add(F(608), 'swish_small', -12, 'pin 22: shadows to alpha 0.42', pan=-0.3)
    add(F(624), 'swish_small', -12, 'pin 23: shadows back', pan=0.3)
    add(F(640), 'glitch_short', -6, 'D7 RGB shock (peak clutter)', dur=0.15)
    add(F(640), 'whip', -8, 'D7 RGB shock (peak clutter)', params=dict(direction=-1))
    add(F(642), 'card_slide', -8, 'version drawer slides in (rows v24, v25)', pan=0.35)
    add(F(704), 'shepard_riser', -10, 'into the hover; starts after "...aur ek." (21.683)', params=dict(duration=1.7),
        carve=True, designed='body in the VO gap 21.683-23.5; tail carved under "Phir"')
    add(F(656), 'card_slide', -14, 'drawer row v26', pan=0.35)
    add(F(672), 'card_slide', -14, 'drawer row v27', pan=0.35)
    add(F(704), 'ui_hover', -12, 'the last pin hovers, undecided', hp=5000, designed='hp 5000 at "Phir"')
    add(F(740), 'heartbeat_build', -8, 'hover: 3 accelerating beats from 23.467, last lub on f740; its dub decays to '
        '-15 dB by the drop-out gate', lp=1200, params=dict(duration=1.2, bpm0=100.0, bpm1=160.0),
        designed='lp 1200 dark under L10')
    add(T_DROP1, 'clock_tick', -14, 'held breath: one tick in the drop-out', params=dict(n=1, bpm=60.0))
    add(T_PAYOFF, 'pin_thock_big', 0, 'PAYOFF: "Pehle wala hi theek tha." slams on the glass', hero=True)
    add(T_PAYOFF, 'sub_drop', -4, 'PAYOFF sub', lp=120, params=dict(dur=1.6))
    add(T_PAYOFF, 'flash_hit', -3, 'PAYOFF L3 push 1.0')
    add(T_PRESS, 'typing', -6, 'Ctrl+Z press: "Ctrl+Z x26" chip POPs', params=dict(n=2, cps=8.0))
    add(T_RESTORE, 'pw_tape_rewind', -6, 'D9 rewind v27 -> v1 (ends on the cut)', params=dict(hook=hook))
    for t, f in rewind_ticks():
        k = VERSION_FRAMES.index(f) + 2
        add(t, 'ui_tick', -14, 'rewind: counter v%d -> v%d (the f%d step undone)' % (k, k - 1, f), hp=4000,
            params=dict(pitch=TICK_A7), pan=PAN_COUNTER)
    add(T_RESTORE, 'impact_soft', 0, 'RESTORE: v1 pristine, chip Approved', hero=True)
    add(T_RESTORE, 'glass_tap', -8, 'RESTORE tonal tail (D6)', params=dict(pitch=GT_D6), carve=True)
    add(F(835) + 0.15, 'swish_small', -12, 'payoff underline draws on (27.983)', align='start', hp=5000,
        designed='hp 5000 into "Har"')
    add(28.2, 'shimmer', -10, 'payoff lockup settles', hp=5500, designed='hp 5500 under "Har"')
    # end card (endcard.EndCard('US CLIENT KO', 'bhejo', monogram='JD', dur=4.2667).cues(29.8667, DUR)) + r2 overrides
    for e in _endcard_cues():
        c.append(e)
    add(F(979), 'ui_hover', -14, "the client's marker re-enters (loop)", hp=5000, pan=0.25,
        designed='hp 5000 under "...aur"')
    return sorted(c, key=lambda d: (d['t'], d['name']))


@functools.lru_cache(maxsize=1)
def _endcard_raw():
    try:
        import endcard as E
        card = E.EndCard('US CLIENT KO', 'bhejo', monogram='JD', dur=4.2667)
        return tuple(json.dumps(x, sort_keys=True) for x in card.cues(T_CARD, DUR))
    except Exception as ex:                     # fallback: the values BRIEF 7 row 48 lists (endcard.py r1)
        print('endcard import failed (%s): using the brief values' % ex)
        return tuple(json.dumps(x, sort_keys=True) for x in [
            dict(t=round(T_CARD + 0.1, 4), name='swish_small', gain_db=-12, align='start', params={}),
            dict(t=round(T_CARD + 0.75, 4), name='glass_tap', gain_db=-12, params={}),
            dict(t=30.437, name='shimmer', gain_db=-10, params={}),
            dict(t=round(DUR, 4), name='reverse_swell', gain_db=-8, params={'duration': 0.8})])


def _endcard_cues():
    out = []
    for s in _endcard_raw():
        e = json.loads(s)
        e['ev'] = 'end card (endcard.cues)'
        if e['name'] == 'swish_small':
            e['ev'] = 'end card: JD ring draws on'
            e['pan'] = 0.0
        elif e['name'] == 'glass_tap':                     # r2: -16, pitched to D7 (bar 14 = Bb: D is a chord tone)
            e.update(gain_db=-16.0, params=dict(pitch=GT_D7), designed='r2 -16 under "hi"', ev='end card: monogram tap')
        elif e['name'] == 'shimmer':
            e['ev'] = 'end card: CTA keyword "bhejo" rises'
        elif e['name'] == 'reverse_swell':                 # r2: lp 1000 under "client ne bola"; ends on DUR = frame 0
            e.update(lp=1000, designed='r2 lp 1000 under "client ne bola"', ev='card exit + loop swell into frame 0')
        out.append(e)
    return out


# ------------------------------------------------------------------------------------------------- VO fit + carve
CARVE_DB, CARVE_LP = -10.0, 600.0               # hero / swell tails under later speech (VO-first)
CARVE_LEAD, CARVE_TAIL, CARVE_BRIDGE = 0.015, 0.06, 1.0
CARVE_RAMP = 0.05


def _cue_span(c):
    x = A.sound(c['name'], **c['params'])
    rate = float(c.get('rate', 1.0))
    hit = x.hit / rate
    L = (c['dur'] if c.get('dur') else len(x) / SR / rate)
    start = float(c['t']) - (hit if c['align'] == 'hit' else 0.0)
    return start, start + hit, start + L


def _carve_windows(c, speech):
    """(t0, t1, depth_db, lp) windows for a cue: the measured speech it overlaps, widened by CARVE_LEAD / CARVE_TAIL and
    bridged across pauses < CARVE_BRIDGE. Heroes and spans (risers, swells: hit = end) keep their hit whole: their carve
    starts no earlier than hit + CARVE_RAMP (the ramp down begins ON the hit). Other carved cues (a swell's body) may be
    carved from their start."""
    start, hit, end = _cue_span(c)
    protect = bool(c.get('hero')) or A.resolve(c['name']) in SJ.HERO or A.resolve(c['name']) in SJ.SPAN
    lo = hit + CARVE_RAMP if protect else start
    w = []
    for a, b in speech:
        a2, b2 = max(a - CARVE_LEAD, lo), b + CARVE_TAIL
        if b2 <= a2 or a2 >= end:
            continue
        if w and a2 - w[-1][1] < CARVE_BRIDGE:
            w[-1] = (w[-1][0], max(w[-1][1], b2))
        else:
            w.append((a2, b2))
    return [(round(a, 4), round(b, 4), CARVE_DB, CARVE_LP) for a, b in w]


def cues(hook='A', report=False, _with_rewind=True):
    """The fitted cue sheet. Cues marked 'designed' keep the brief's VO-aware level/filter; every other cue goes through
    sfx_jawad.fit_under_vo (on-word cues -6 dB, air hp 5500, dark lp 1100, mid -8); hero cues and swells whose body
    meets later speech get carve windows (CARVE_DB with a low-pass crossfade) from the measured speech (words + VO
    audio activity)."""
    register()
    raw = raw_cues(hook)
    if not _with_rewind:
        raw = [c for c in raw if c['name'] != 'pw_tape_rewind']
    words = WORDS[hook]
    fit_idx = [i for i, c in enumerate(raw) if not c.get('designed')]
    fitted, frep = SJ.fit_under_vo([raw[i] for i in fit_idx], words, hero='warn', report=True)
    out = [A._norm_cue(c) for c in raw]
    for i, c in zip(fit_idx, fitted):
        out[i] = c
    speech, src = SJ.hero_windows(words, 0.0, 0.0, 'auto')
    carved = []
    for c in out:
        if c.get('hero') or A.resolve(c['name']) in SJ.HERO or c.get('carve'):
            w = _carve_windows(c, speech)
            if w:
                c['carve'] = w
                carved.append(dict(name=c['name'], t=c['t'], windows=w))
            elif c.get('carve') is True:
                c.pop('carve')
    out.sort(key=lambda d: (float(d['t']), d['name']))
    if report:
        frep = dict(frep)
        frep['carved'] = carved
        frep['speech_source'] = src
        return out, frep
    return out


BED_GAIN_DB = -32.0                             # BRIEF 11: edit_suite at -32; audio.mix fallback form below
BED = [dict(name='edit_suite', t0=0.0, t1=T_DROP0, gain_db=0.0, fade=GATE_EDGE),
       dict(name='edit_suite', t0=T_DROP1, t1=T_PAYOFF, gain_db=-8.0, fade=GATE_EDGE),
       dict(name='edit_suite', t0=T_PAYOFF, t1=DUR, gain_db=0.0, fade=0.05)]
BEDS_EXACT = [(0.0, T_DROP0, -32.0), (T_DROP0, T_DROP1, None), (T_DROP1, T_PAYOFF, -40.0), (T_PAYOFF, DUR, -32.0)]


# =============================================================================================== circular mixer
def _circ_pad(x, p):
    return np.concatenate([x[-p:], x, x[:p]], axis=0)


def _circ(fn, x, pad=1.0):
    p = _n(pad)
    return fn(_circ_pad(x, p))[p:p + len(x)]


def _fold(buf, pre, n):
    out = np.zeros((n,) + buf.shape[1:])
    np.add.at(out, (np.arange(len(buf)) - pre) % n, buf)
    return out


def _rc(x):
    return 0.5 - 0.5 * np.cos(np.pi * np.clip(x, 0, 1))


def _carve(y, start, windows):
    """Crossfade y into (lp(y) at depth) inside each window, raised-cosine ramps of CARVE_RAMP s."""
    t = start + np.arange(len(y)) / SR
    w = np.zeros(len(y))
    for a, b, d, f in windows:
        w = np.maximum(w, np.minimum(_rc((t - (a - CARVE_RAMP)) / CARVE_RAMP), _rc(((b + CARVE_RAMP) - t) / CARVE_RAMP)))
    if not w.any():
        return y
    d, f = windows[0][2], windows[0][3]
    return y * (1 - w)[:, None] + lp(y, f, 2) * (undb(d) * w)[:, None]


def _bed_bus(target_lufs=TARGET_LUFS):
    """edit_suite as an exact-level circular loop: seamless at the reel seam (0.5 s equal-power splice), gated to zero
    in the drop-out (4 ms edges ending ON 25.0667 and starting ON 25.3333), -40 held breath, back to -32 under the payoff.
    Level anchor as audio.mix: a segment at bed gain g sits at target + g + 8 LUFS."""
    loop = np.asarray(A.sound('edit_suite'), dtype=np.float64)
    X = _n(0.5)
    y = loop[np.arange(N + X) % len(loop)]
    a = np.sin(0.5 * np.pi * np.arange(X) / X)[:, None]
    y[:X] = y[:X] * a + y[N:N + X] * np.sqrt(1 - a ** 2)
    y = y[:N]
    y = y * undb(target_lufs + A.BED_ANCHOR_DB - A.loudness(y))      # gain 0 -> target + 8
    t = np.arange(N) / SR
    g = np.zeros(N)
    for t0, t1, lvl in BEDS_EXACT:
        if lvl is None:
            continue
        e = 0.05 if t0 == T_PAYOFF else GATE_EDGE
        up = _rc((t - t0) / e) if t0 > 0 else np.ones(N)
        dn = _rc((t1 - t) / GATE_EDGE) if t1 < DUR - 1e-9 else np.ones(N)
        g += undb(lvl) * np.minimum(up, dn) * ((t >= t0) & (t < t1 + (GATE_EDGE if t1 < DUR else 1)))
    return y * g[:, None], [dict(t0=round(a0, 4), t1=round(a1, 4), gain_db=l) for a0, a1, l in BEDS_EXACT]


def _drop_gate(n_long, pre):
    """1 before the drop-out, a 4 ms raised-cosine fall ENDING on 25.0667, 0 after (for buses of cues started before)."""
    t = (np.arange(n_long) - pre) / SR
    return _rc((T_DROP0 - t) / GATE_EDGE)


def _timing(y, start, hit_abs, hop=96):
    m = np.square(np.asarray(y, dtype=np.float64)).mean(1)
    nb = len(m) // hop
    p2 = m[:nb * hop].reshape(nb, hop).mean(1)
    e = 10 * np.log10(p2 + 1e-20)
    pk = float(e.max())
    on = int(np.argmax(e >= pk - 20.0))
    end = int(np.nonzero(e >= pk - 40.0)[0][-1]) + 1
    sm = np.convolve(p2, np.ones(15) / 15, 'same')
    k = int(np.clip(round((hit_abs - start) * SR / hop - 0.5), 0, len(sm) - 1))
    o_near, _ = _onset_near(y, hit_abs - start)
    return dict(onset_near_hit_abs=round(hit_abs + o_near, 4),onset_abs=round(start + on * hop / SR, 4), peak_abs=round(start + (int(np.argmax(sm)) + 0.5) * hop / SR, 4),
                end_abs=round(start + end * hop / SR, 4),
                at_hit_db=round(float(10 * np.log10(sm[k] + 1e-20) - 10 * np.log10(sm.max() + 1e-20)), 2))


def mix_loop(cue_list, out_stem=None, target_lufs=TARGET_LUFS, tp_ceiling=TP_CEILING, verbose=True):
    """audio.mix's chain on a loop (see module docstring); returns an audio.mix-style report (+ 'fx', 'bedbus')."""
    PRE, POST = _n(1.0), _n(9.0)
    L = PRE + N + POST
    cs = A.duck_under([A._norm_cue(c) for c in cue_list])
    buses = {k: np.zeros((L, 2)) for k in ('pre', 'post')}
    sends = {k: np.zeros((L, 2)) for k in ('pre', 'post')}
    placed, counts = [], {}
    for c in sorted(cs, key=lambda c: float(c['t'])):
        k = (c['name'], A._key(c['params']))
        counts[k] = counts.get(k, -1) + 1
        y, hit = A._render_cue(c, counts[k] % 4)
        start = float(c['t']) - (hit if c['align'] == 'hit' else 0.0)
        tm = _timing(y, start, start + hit)
        if c.get('carve'):
            y = _carve(y, start, c['carve'])
        i = PRE + _n(start)
        assert 0 <= i and i + len(y) <= L, (c['name'], start)
        grp = 'pre' if 0.0 <= start < T_DROP0 else 'post'
        buses[grp][i:i + len(y)] += y
        cat = A.SOUNDS[c['name']]['category']
        sdb = c.get('send_db', A.SOUNDS[c['name']]['send'] if A.SOUNDS[c['name']]['send'] is not None
                    else A._CAT_SEND[cat])
        if sdb is not None and sdb > -60:
            sends[grp][i:i + len(y)] += y * undb(sdb)
        warn = 'wraps to the loop end' if start < 0 else ('tail wraps to t=0' if start + len(y) / SR > DUR else '')
        if grp == 'pre' and start + len(y) / SR > T_DROP0:
            warn = (warn + '; ' if warn else '') + 'cut at the drop-out'
        placed.append(dict(t=float(c['t']), name=c['name'], start=round(start, 4), hit=round(start + hit, 4),
                           len=round(len(y) / SR, 3), gain_db=round(float(c['gain_db']), 2),
                           duck_db=c.get('duck_db', 0.0), align=c['align'], params=c['params'], lp=c.get('lp'),
                           hp=c.get('hp'), pan=c.get('pan', 0.0), dur=c.get('dur'), hero=bool(c.get('hero')),
                           vo=c.get('vo', ''), designed=c.get('designed', ''), ev=c.get('ev', ''), warn=warn,
                           carve=c.get('carve'), ev_t=c.get('ev_t'), **tm))
    gate = _drop_gate(L, PRE)
    fxb = np.zeros((L, 2))
    for grp in ('pre', 'post'):
        wet = A.reverb(sends[grp], 'studio', wet_db=0.0, dry=0.0)
        if len(wet) > L and np.max(np.abs(wet[L:])) > 1e-7:
            raise RuntimeError('room tail beyond the post-roll')
        b = buses[grp] + wet[:L]
        if grp == 'pre':
            b = b * gate[:, None]
        fxb += b
    fx = _fold(fxb, PRE, N)
    fx *= undb(target_lufs - A.loudness(fx))
    gr_comp = _circ(lambda z: A.compressor_gain(z, thresh_db=target_lufs + 8.0, ratio=2.0), fx)
    fx *= undb(gr_comp)[:, None]
    bed, bed_info = _bed_bus(target_lufs)
    p = _n(1.0)
    bed = A.sidechain(_circ_pad(bed, p), _circ_pad(fx, p), depth_db=5.0)[p:p + N]
    pk_fx = _circ(A.tp_envelope, fx)
    pk_bed = _circ(A.tp_envelope, bed)
    G, ceil, best = 0.0, tp_ceiling - 0.2, None
    for attempt in range(4):
        for it in range(40):
            gl = _circ(lambda z: A.limiter_gain(None, ceil, pk=z), pk_fx * undb(G) + pk_bed)
            y = (fx * undb(G) + bed) * gl[:, None]
            L1 = A.loudness(y)
            if best is None or abs(L1 - target_lufs) < abs(best[2] - target_lufs):
                best = (G, gl, L1, y)
            if abs(L1 - target_lufs) < 0.02:
                break
            G += float(np.clip(target_lufs - L1, -12, 12)) * 0.9
        G, gl, L1, y = best
        tp = A.true_peak(_circ_pad(y, _n(0.05)))
        if tp <= tp_ceiling - 0.05:
            break
        ceil -= tp - (tp_ceiling - 0.1)
        best = None
    fx_out = fx * (undb(G) * gl)[:, None]
    bed_out = bed * gl[:, None]
    master = fx_out + bed_out
    rep = dict(dur=DUR, cues=len(cs), integrated_lufs=round(A.loudness(master), 2),
               true_peak_dbtp=round(A.true_peak(_circ_pad(master, _n(0.05))), 2),
               sample_peak_dbfs=round(float(db(np.max(np.abs(master)))), 2), lra_lu=round(A.loudness_range(master), 2),
               max_momentary_lufs=round(A.momentary_max(master), 2),
               max_short_term_lufs=round(A.momentary_max(master, 3.0), 2),
               limiter_max_gr_db=round(max(0.0, float(-db(np.min(gl)))), 2),
               limiter_max_gr_at=round(float(np.argmin(gl)) / SR, 3),
               limiter_pct_over_1db=round(100.0 * float(np.mean(gl < undb(-1.0))), 2),
               comp_max_gr_db=round(float(-np.min(gr_comp)), 2), fx_gain_db=round(G, 2), bed=bed_info,
               bed_lufs=round(A.loudness(bed_out), 2), fx_lufs=round(A.loudness(fx_out), 2), placed=placed, files={})
    if out_stem:
        rep['files']['stem'] = A._write_wav(out_stem + '.wav', master, 24)
        rep['files']['stem_fx'] = A._write_wav(out_stem + '_fx.wav', fx_out, 24)
        rep['files']['stem_bed'] = A._write_wav(out_stem + '_bed.wav', bed_out, 24)
    rep['audio'] = master.astype(np.float32)
    rep['fx'] = fx_out.astype(np.float32)
    rep['bedbus'] = bed_out.astype(np.float32)
    if verbose:
        print('SFX loop mix %.3fs %d cues | I %.2f LUFS | TP %.2f dBTP | LRA %.1f | Mmax %.1f | limiter GR %.2f dB at %.3f'
              ' | glue GR %.2f dB | bed %.1f LUFS' % (DUR, rep['cues'], rep['integrated_lufs'], rep['true_peak_dbtp'],
                                                      rep['lra_lu'], rep['max_momentary_lufs'], rep['limiter_max_gr_db'],
                                                      rep['limiter_max_gr_at'], rep['comp_max_gr_db'], rep['bed_lufs']))
    return rep


# =============================================================================================== measurement
def ebur128(path):
    import re
    r = subprocess.run(['ffmpeg', '-hide_banner', '-nostats', '-i', path, '-af', 'ebur128=peak=true', '-f', 'null', '-'],
                       capture_output=True, text=True).stderr
    s = r[r.rfind('Summary'):]
    g = lambda k: float(re.search(k + r':\s+(-?[\d.]+)', s).group(1))
    return dict(I=g('I'), LRA=g('LRA'), TP=g('Peak'))


def _onset_near(x, t, win=0.06, hop=240):
    """qa_measure.py `cues` on an array: the 5 ms-energy rise nearest t within +-win -> (offset s, rise dB)."""
    m = np.asarray(x, dtype=np.float64)
    m = m.mean(1) if m.ndim == 2 else m
    e = np.sqrt(np.convolve(m * m, np.ones(hop) / hop, 'same')[::hop] + 1e-12)
    d = 20 * np.log10(e)
    on = np.maximum(np.diff(d, prepend=d[0]), 0)
    rate = SR / hop
    i0, i1 = max(0, int((t - win) * rate)), min(len(on) - 1, int((t + win) * rate))
    k = i0 + int(np.argmax(on[i0:i1]))
    return k / rate - t, float(on[k])


def _music_events():
    try:
        d = json.load(open(MUSIC_JSON))
    except Exception:
        return []
    return [(float(e['t']), e['inst']) for e in d.get('events', [])
            if e.get('inst') in ('kick', 'hat', 'ep', 'taiko', 'clap', 'trailer_hit', '808', 'str')]


def starts_per_instant(placed, music_events=(), tol=1.0 / FPS):
    """Bible 4.2: sounds STARTING on one instant (+-1 frame). A sound counts at its onset when its designed hit is < 50 ms
    after its start (transients) or at its start when cued align='start'; swells / whooshes / risers that peak or END on the
    instant do not count. The score is one bus: any score transients at the instant count as one. Also returns the stricter
    'transients landing' count (every hit-aligned SFX whose designed hit is on the instant, incl. slot_tick landings and
    whoosh passes)."""
    ev, land = [], []
    for p in placed:
        if p['align'] == 'start':
            ev.append((p['start'], p['name']))
        elif p['hit'] - p['start'] < 0.05:
            ev.append((p['hit'], p['name']))
        if p['align'] == 'hit' and p['name'] not in ('pw_tape_rewind', 'reverse_swell', 'shepard_riser', 'heartbeat_build'):
            land.append((p['hit'], p['name']))
    mus = sorted(float(t) for t, _ in music_events)

    def count(evl):
        worst, clusters = 0, []
        for t, n in evl:
            grp = sorted(e[1] for e in evl if abs(e[0] - t) <= tol)
            m = any(abs(tm - t) <= tol for tm in mus)
            k = len(grp) + (1 if m else 0)
            worst = max(worst, k)
            item = (round(t, 3), k, grp + (['music'] if m else []))
            if k >= 3 and item[2] not in [cc[2] for cc in clusters]:
                clusters.append(item)
        return worst, clusters
    return dict(starts=count(sorted(ev)), landings=count(sorted(land)))


def _rms_db(x):
    x = np.asarray(x, dtype=np.float64)
    return float(10 * np.log10(np.mean(np.square(x)) + 1e-30))


def _paths(hook):
    return os.path.join(AUD, '%s_sfx_%s' % (MODULE, hook))


def build(hook='A'):
    register()
    os.makedirs(AUD, exist_ok=True)
    base = _paths(hook)
    cl, frep = cues(hook, report=True)
    rep = mix_loop(cl, out_stem=base + '_stem')
    A.mix_overview(rep, base + '_overview.png', '%s SFX stem, hook %s (VO fit on the measured Vlad words)' % (MODULE, hook))
    x = np.asarray(rep['audio'], dtype=np.float64)
    fx = np.asarray(rep['fx'], dtype=np.float64)
    tt, lc = A.loudness_curve(x)
    timing = []
    for p in rep['placed']:
        ev = p.get('ev_t') or p['t']
        if p['name'] == 'heartbeat_build':                 # its END is the last lub's transient
            kind, at, ref, tol = 'last-lub', p['onset_near_hit_abs'], ev, 1.0 / FPS
        elif p['name'] in SJ.SPAN or p['name'] in ('reverse_swell', 'pw_tape_rewind'):
            kind, at, ref, tol = 'end', p['end_abs'], ev, 1.0 / FPS
        elif p['align'] == 'start':
            kind, at, ref, tol = 'start', p['onset_abs'], ev, 1.0 / FPS
        elif p['hit'] - p['start'] < 0.05:
            kind, at, ref, tol = 'onset', p['onset_abs'], ev, 1.0 / FPS
        else:
            kind, at, ref, tol = 'peak', p['peak_abs'], p['hit'], 0.06
        off = at - ref
        ok = abs(off) <= tol + 1e-6 or (kind in ('peak', 'end') and p['at_hit_db'] >= -1.5) or \
            (kind == 'start' and p['name'] in ('swish_small', 'timeline_scrub') and abs(p['onset_abs'] - p['start']) < 0.2)
        timing.append(dict(name=p['name'], t=p['t'], f=round(p['t'] * FPS, 2), kind=kind, ref=round(ref, 4), at=at,
                           off_ms=round(off * 1000, 1), off_frames=round(off * FPS, 2), at_hit_db=p['at_hit_db'],
                           flag='' if ok else 'CHECK'))
    onsets = []
    for p in rep['placed']:
        if p['hero'] or p['name'] in SJ.HERO:
            off, rise = _onset_near(fx, p['hit'])
            onsets.append(dict(name=p['name'], t=p['t'], qa_off_ms=round(off * 1000, 1), qa_rise_db=round(rise, 1)))
    a0, a1 = _n(T_DROP0), _n(T_DROP1 - 0.002)
    seam = dict(last50_rms_db=round(_rms_db(x[-_n(0.05):]), 2), first50_rms_db=round(_rms_db(x[:_n(0.05)]), 2),
                step=round(float(np.abs(x[0] - x[-1]).max()), 6),
                median_step_last50=round(float(np.median(np.abs(np.diff(x[-_n(0.05):], axis=0)).max(1))), 6))
    meas = dict(
        vo_fit=dict(ducked=frep['ducked'], spans=frep['spans'], heroes_ok=frep['heroes_ok'],
                    violations=frep['violations'], carved=frep['carved'], speech_source=frep['speech_source']),
        stem=dict((k, rep[k]) for k in ('integrated_lufs', 'true_peak_dbtp', 'sample_peak_dbfs', 'lra_lu',
                                        'max_momentary_lufs', 'max_short_term_lufs', 'limiter_max_gr_db', 'limiter_max_gr_at',
                                        'limiter_pct_over_1db', 'comp_max_gr_db', 'bed_lufs', 'fx_lufs', 'fx_gain_db')),
        ffmpeg=ebur128(base + '_stem.wav'),
        max_momentary_at=round(float(tt[np.argmax(lc)]), 3),
        dropout=dict(window=[round(T_DROP0, 4), round(T_DROP1, 4)], max_abs=float(np.abs(x[a0:a1]).max()),
                     zero_frames=int(sum(np.abs(x[_n(F(752 + k)):_n(F(753 + k))]).max() == 0.0 for k in range(8))),
                     held_breath_tick_rms_db=round(_rms_db(x[_n(T_DROP1):_n(T_PAYOFF)]), 1)),
        seam=seam, timing=timing, qa_onsets=onsets,
        starts_per_instant=starts_per_instant(rep['placed'], _music_events()),
        warnings=[(p['name'], p['t'], p['warn']) for p in rep['placed'] if p['warn']], bed=rep['bed'],
        files=rep['files'])
    cj = dict(module=MODULE, hook=hook, dur=DUR, bpm=BPM, fps=FPS, words=WORDS[hook],
              cues=[dict((k, v) for k, v in p.items()) for p in rep['placed']])
    json.dump(cj, open(base + '_cues.json', 'w'), indent=1, default=str)
    json.dump(meas, open(base + '_report.json', 'w'), indent=1, default=str)
    print(json.dumps(dict((k, meas[k]) for k in ('stem', 'ffmpeg', 'max_momentary_at', 'dropout', 'seam',
                                                 'starts_per_instant', 'warnings')), indent=1, default=str))
    for o in timing:
        if o['flag']:
            print('%5s %-16s t %7.3f (f%7.2f) %-5s ref %7.3f at %7.3f %+6.1f ms (%+.2f f) at_hit %.2f dB' % (
                o['flag'], o['name'], o['t'], o['f'], o['kind'], o['ref'], o['at'], o['off_ms'], o['off_frames'],
                o['at_hit_db']))
    print('timing CHECK lines: %d of %d' % (sum(1 for o in timing if o['flag']), len(timing)))
    for o in onsets:
        print('  qa-style onset %-14s t %7.3f  %+6.1f ms  rise %.1f dB' % (o['name'], o['t'], o['qa_off_ms'], o['qa_rise_db']))
    return rep, meas


# ------------------------------------------------------------------------------------------------- rough mix
LOOP_PAD = 3.0


def rough(hook='A'):
    """epic_mix.mix_reel(VO, SFX stem, music) on a loop-padded copy (LOOP_PAD s of the other end each side), cropped to
    DUR, one small gain back to -14.00 LUFS capped at TP <= -2.05. Writes <AUD>/pehle_wala_<hook>_rough_*.wav."""
    import epic_mix as M
    P = _n(LOOP_PAD)
    stem = _paths(hook) + '_stem.wav'
    rname = '%s_%s_rough' % (MODULE, hook)
    tmpd = os.path.join(AUD, '_tmp_' + rname)
    os.makedirs(tmpd, exist_ok=True)
    ins = {}
    try:
        for key, path in (('vo', VO[hook]), ('sfx', stem), ('music', MUSIC[hook])):
            x = _stereo_n(path, N)
            ins[key] = os.path.join(tmpd, key + '.wav')
            A._write_wav(ins[key], np.concatenate([x[-P:], x, x[:P]]), 24)
        rp = M.mix_reel(rname, DUR + 2 * LOOP_PAD, vo=ins['vo'], sfx=ins['sfx'], music=ins['music'], out_dir=tmpd,
                        vo_offset=0.0)
        cut = dict((k, np.asarray(A.read_wav(rp['files'][k])[0], dtype=np.float64)[P:P + N]) for k in
                   ('mix', 'vo_sfx', 'stem_vo', 'stem_sfx', 'stem_music'))
    finally:
        for fn in os.listdir(tmpd):
            os.remove(os.path.join(tmpd, fn))
        os.rmdir(tmpd)
    gains = {}
    for key, stems in (('mix', ('stem_vo', 'stem_sfx', 'stem_music')), ('vo_sfx', ())):
        g = TARGET_FINAL - A.loudness(cut[key])
        g = min(g, TP_CEILING - 0.05 - A.true_peak(_circ_pad(cut[key], _n(0.05))))
        gains[key] = round(g, 3)
        for k in (key,) + stems:
            cut[k] = cut[k] * undb(g)
    files = {}
    for k, x in cut.items():
        files[k] = os.path.join(AUD, rname + '_' + k + '.wav')
        A._write_wav(files[k], x, 24)
    yA, yB = cut['mix'], cut['vo_sfx']
    v, s, m = cut['stem_vo'], cut['stem_sfx'], cut['stem_music']
    # speech frames (epic_mix.speech_mask, hold 0.25 s) and loudness curves of the stems at mix gain
    sp = M.speech_mask(v)
    tt, lv = A.loudness_curve(v)
    _, lm = A.loudness_curve(m)
    _, ls = A.loudness_curve(s)
    _, la = A.loudness_curve(yA)
    idx = np.clip((tt * SR).astype(int), 0, N - 1)
    spk = sp[idx] & (lv > lv.max() - 15)
    # speech band (1-4 kHz) energy of SFX vs VO inside the measured words
    from audio import bp
    vb, sb = bp(v.mean(1), 1000, 4000, 2), bp(s.mean(1), 1000, 4000, 2)
    band = []
    for a, b, wd in _words(hook):
        i0, i1 = _n(a), _n(b)
        band.append((round(a, 3), wd, round(_rms_db(sb[i0:i1]) - _rms_db(vb[i0:i1]), 1)))
    band_sorted = sorted(band, key=lambda r: -r[2])
    a0, a1 = _n(T_DROP0), _n(T_DROP1 - 0.002)
    seamA = dict(last50_rms_db=round(_rms_db(yA[-_n(0.05):]), 2), first50_rms_db=round(_rms_db(yA[:_n(0.05)]), 2),
                 step=round(float(np.abs(yA[0] - yA[-1]).max()), 6),
                 median_step=round(float(np.median(np.abs(np.diff(yA[-_n(0.2):], axis=0)).max(1))), 6))
    rew = (_n(T_REW0 + 0.3), _n(T_RESTORE - 0.05))
    rep = dict(name=rname, hook=hook, dur=DUR, loop_pad_s=LOOP_PAD, crop_gain_db=gains,
               inputs=dict(vo=VO[hook], vo_sha256=hashlib.sha256(open(VO[hook], 'rb').read()).hexdigest()[:16],
                           sfx=stem, music=MUSIC[hook]),
               A_full=dict(lufs=round(A.loudness(yA), 2), tp_dbtp=round(A.true_peak(_circ_pad(yA, _n(0.05))), 2),
                           lra=round(A.loudness_range(yA), 1), max_momentary=round(A.momentary_max(yA), 2),
                           max_momentary_at=round(float(tt[np.argmax(la)]), 3)),
               B_vo_sfx=dict(lufs=round(A.loudness(yB), 2), tp_dbtp=round(A.true_peak(_circ_pad(yB, _n(0.05))), 2),
                             lra=round(A.loudness_range(yB), 1)),
               vo_over_music_lu_median=round(float(np.median((lv - lm)[spk])), 1),
               vo_over_music_lu_p10=round(float(np.percentile((lv - lm)[spk], 10)), 1),
               vo_over_sfx_lu_median=round(float(np.median((lv - ls)[spk])), 1),
               vo_over_sfx_lu_p10=round(float(np.percentile((lv - ls)[spk], 10)), 1),
               sfx_minus_vo_1to4k_db_worst5=band_sorted[:5],
               sfx_minus_vo_1to4k_db_median=round(float(np.median([r[2] for r in band])), 1),
               vo_lufs_in_mix=round(A.loudness(v), 2), music_lufs_in_mix=round(A.loudness(m), 2),
               sfx_lufs_in_mix=round(A.loudness(s), 2),
               dropout=dict(mix_max_abs=float(np.abs(yA[a0:a1]).max()), vo_sfx_max_abs=float(np.abs(yB[a0:a1]).max())),
               rewind_window_lufs=round(A.loudness(yA[rew[0]:rew[1]]), 1),
               pre_drop_music_bar11_lufs=round(A.loudness(yA[_n(23.6):_n(25.0)]), 1),
               seam=seamA, ffmpeg_mix=ebur128(files['mix']), ffmpeg_vo_sfx=ebur128(files['vo_sfx']), files=files)
    M._overview(yA, v, m, s, os.path.join(AUD, rname + '_mix.png'),
                '%s  A=%.2f LUFS %.2f dBTP | B=%.2f LUFS %.2f dBTP | VO over music %.1f LU' % (
                    rname, rep['A_full']['lufs'], rep['A_full']['tp_dbtp'], rep['B_vo_sfx']['lufs'],
                    rep['B_vo_sfx']['tp_dbtp'], rep['vo_over_music_lu_median']))
    json.dump(rep, open(os.path.join(AUD, rname + '.json'), 'w'), indent=1, default=str)
    print(json.dumps(rep, indent=1, default=str))
    return rep


# ------------------------------------------------------------------------------------------------- audition
def f0_of(name, **p):
    """bible 4.2: the dominant partial above 150 Hz of the rendered sound."""
    x = np.asarray(A.sound(name, **p), float).mean(1)
    X = np.abs(np.fft.rfft(x * np.hanning(len(x))))
    f = np.fft.rfftfreq(len(x), 1 / SR)
    return float(f[np.argmax(X * (f > 150))])


def cents_to_note(f):
    names = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
    m = 69 + 12 * math.log2(f / 440.0)
    k = int(round(m))
    return '%s%d' % (names[k % 12], k // 12 - 1), round(100 * (m - k), 1)


def audition():
    register()
    d = os.path.join(AUD, 'audition')
    os.makedirs(d, exist_ok=True)
    rows = []
    for nm in LOCAL:
        x = A.sound(nm)
        y = np.asarray(x, dtype=np.float64)
        st = A.stats(y, x.hit)
        q = A.qc(y, x.hit)
        A._write_wav(os.path.join(d, nm + '.wav'), y, 24)
        A.spectro_image(x, 1000, 420, x.hit, nm, 'hit %.3f s  Mmax %.1f LUFS  qc %s' % (
            x.hit, A.momentary_max(y), q or 'clean')).save(os.path.join(d, nm + '.png'))
        rows.append(dict(name=nm, dur=round(len(y) / SR, 3), hit=x.hit, mmax=round(A.momentary_max(y), 2),
                         peak_dbfs=round(float(db(np.abs(y).max())), 2), qc=q, stats={k: (round(v, 3) if isinstance(
                             v, float) else v) for k, v in st.items()}))
    tonal = [('pin_thock glass (glass_tap)', 'glass_tap', dict(pitch=GT_D7)),
             ('pin_thock_mummy glass', 'glass_tap', dict(pitch=GT_A6)),
             ('pin_thock_big / restore glass', 'glass_tap', dict(pitch=GT_D6)),
             ('pop (Dm/Bb bars)', 'pop', dict(pitch=POP_D6)), ('pop (F bar)', 'pop', dict(pitch=POP_C6)),
             ('ui_click (Dm bar)', 'ui_click', dict(pitch=CLICK_A6)), ('ui_tick (rewind)', 'ui_tick', dict(pitch=TICK_A7)),
             ('bubble_pop (Bb bar)', 'bubble_pop', dict(pitch=BUB_D6)), ('toggle_on (C bar)', 'toggle_on', {}),
             ('glass_tap brief 1.0926', 'glass_tap', dict(pitch=1.0926))]
    pitch = []
    for lab, nm, p in tonal:
        f = f0_of(nm, **p)
        pitch.append(dict(what=lab, sound=nm, params=p, f0=round(f, 1), note=cents_to_note(f)))
    # the composite's own dominant partial (pin_thock: the glass above 1 kHz)
    for nm in ('pin_thock', 'pin_thock_mummy', 'pin_thock_big'):
        x = np.asarray(A.sound(nm), float).mean(1)
        X = np.abs(np.fft.rfft(x * np.hanning(len(x))))
        f = np.fft.rfftfreq(len(x), 1 / SR)
        fm = float(f[np.argmax(X * (f > 1000))])
        pitch.append(dict(what=nm + ' (partial > 1 kHz)', sound=nm, params={}, f0=round(fm, 1), note=cents_to_note(fm)))
    ticks = rewind_ticks()
    out = dict(sounds=rows, pitch=pitch, rewind_ticks=[(round(t, 4), f) for t, f in ticks], n_ticks=len(ticks))
    json.dump(out, open(os.path.join(d, 'audition.json'), 'w'), indent=1, default=str)
    for r in rows:
        print('%-22s dur %.3f hit %.3f Mmax %6.2f peak %6.2f qc %s' % (r['name'], r['dur'], r['hit'], r['mmax'],
                                                                     r['peak_dbfs'], r['qc'] or 'clean'))
    for p in pitch:
        print('%-36s f0 %8.1f Hz  %s %+.1f c' % (p['what'], p['f0'], p['note'][0], p['note'][1]))
    print('rewind ticks: %d' % len(ticks))
    return out


def print_cues(hook='A'):
    cl, frep = cues(hook, report=True)
    for c in cl:
        print('%7.3f f%6.2f %-22s %6.1f %-5s %-28s %-24s %s' % (
            float(c['t']), float(c['t']) * FPS, c['name'], float(c['gain_db']), c['align'],
            ' '.join('%s=%s' % (k, c[k]) for k in ('lp', 'hp', 'dur', 'pan') if c.get(k) not in (None, 0, 0.0)),
            c.get('vo', '') or c.get('designed', ''), c.get('ev', '')))
    print('violations (hero pre-laps, carved):', json.dumps(frep['violations']))
    print('carved:', json.dumps(frep['carved']))
    print('speech source:', frep['speech_source'])


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument('cmd', choices=['cues', 'audition', 'build', 'rough'])
    ap.add_argument('--hook', default='A', choices=['A', 'B', 'AB'])
    a = ap.parse_args(argv)
    hooks = list(a.hook)
    if a.cmd == 'audition':
        audition()
        return
    for h in hooks:
        if a.cmd == 'cues':
            print_cues(h)
        elif a.cmd == 'build':
            build(h)
        elif a.cmd == 'rough':
            rough(h)


if __name__ == '__main__':
    main(sys.argv[1:])
