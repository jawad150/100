"""sirf_36_shots_ui.py - type + glass UI of Bijli series #3 "Sirf 36 Shots" (UI/UX designer: caption-designer +
brand-kit-builder roles; stage 2, BUILD_CONTRACT.md). The motion designer's `sirf_36_shots.py` imports this.

Source of truth: brand_reels/design/reels/sirf_36_shots/{SCRIPT.md, script.json, SHOTS.md (C) UI / TYPE}; every
lockup string, frame window and px size is read from script.json (no copy is retyped here). Deviations from SHOTS
are listed in brand_reels/design/reels/sirf_36_shots/UI.md. Look 'noir_ember', 1080x1920, 30 fps, 120 BPM.

Every sprite is built once per process (lru_cache); every draw is a pure function of (cv, t) in REEL time (s) on the
house canvas (premultiplied linear float32 RGBA, core.K convention). Nothing here touches post.

    import sirf_36_shots_ui as UI
    UI.captions(cv, t, hook='A')     every lockup of script.json with its in / out animation (hook 'B' = Trial Reel)
    UI.lockup('C13').draw(cv, t)     one lockup (Lockup / NumLockup / CountLockup objects, .f_in .f_out .box)
    UI.day_chip(cv, t)               S4 'DIN 1/2/3' glass chip, swaps f240 / f255 / f270, exits with C6
    UI.storage_hud(cv, t)            S7 glass card: STORAGE 0.00 -> 2.00 TB (f540-f565), flame bar
    UI.media_bin(cv, t)              S8-S9 glass media bin: dense clip grid (no faces: landscapes / abstract
                                     footage), accelerating scroll, hover-scrub, watched bars, TAKE 0,001 -> 3,000,
                                     storage bar -> RED + DISK FULL f735, 2-frame slice glitch, freeze f780, dim
    UI.toast(cv, t)                  S9 client message card: avatar (C3 portal centre (540, 1120)), typing dots
                                     f795-f809, f810 'Client · abhi' + "Ek achha shot nahi hai."
    UI.outro()                       PO.ProfileOutro (question / key from script.json), T_END = 32.0
    UI.cover(cv)                     cover overlay (SIRF / 36 shots + @jawad_mp4); UI.GRID_CROP = (240, 1680)
    UI.post_kw(t)                    {'rgb_split': ...} for the f735 DISK FULL glitch (merge into G.tx_finish kw)
    UI.write_srt(path)               one cue per lockup (sentence case, asterisks removed), t_in - t_out
    UI.prewarm()

    python3 sirf_36_shots_ui.py selftest   -> workspace/jawad_reels/sirf_36_shots/ui_selftest/*.png
(the selftest uses the Blender plates from RWS/assets3d/ when they exist, otherwise dark stand-in plates.)
"""
import functools
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import jawad_kit                                  # noqa: F401,E402  FIRST
from jawad_kit import K, T, J, ui                 # noqa: E402
import jawad_tx as X                              # noqa: E402
import jawad_grade as G                           # noqa: E402
import profile_outro as PO                        # noqa: E402

import cv2                                        # noqa: E402
import numpy as np                                # noqa: E402

SLUG = 'sirf_36_shots'
LOOK = 'noir_ember'
FPS = K.FPS
HALF = 0.5 / FPS
DUR = 36.0
T_END = 32.0                                      # outro start (bar 16, f960)
REPO = os.path.abspath(os.path.join(HERE, '..', '..'))
SCRIPT_JSON = os.path.join(REPO, 'brand_reels', 'design', 'reels', SLUG, 'script.json')
RWS = os.path.join(K.WS, SLUG)
SELFTEST_DIR = os.path.join(RWS, 'ui_selftest')
GRID_CROP = (240, 1680)                           # 3:4 grid crop rows of the cover (y0, y1)


def F(n):
    return n / float(FPS)


def fidx(t):
    return int(math.floor(t * FPS + 0.5))


def C(name, k=1.0):
    return np.asarray(K.C[name], np.float32)[:3] * np.float32(k)


def hexl(h, k=1.0):
    return np.asarray(K.hexlin(h), np.float32)[:3] * np.float32(k)


def ro(a):
    a = np.ascontiguousarray(a, np.float32)
    a.setflags(write=False)
    return a


def solid(mask, col):
    m = np.asarray(mask, np.float32)
    out = np.zeros(m.shape + (4,), np.float32)
    out[..., :3] = m[..., None] * np.asarray(col, np.float32)[:3]
    out[..., 3] = m
    return out


def emissive(mask, col):
    """Additive light sprite (alpha 0) from a coverage mask."""
    out = solid(mask, col)
    out[..., 3] = 0.0
    return out


@functools.lru_cache(maxsize=2048)
def txt(s, style, px, fill=None):
    return T.render(s, style, px=px) if fill is None else T.render(s, style, px=px, fill=fill)


def ease(name, u):
    return float(K.EASE[name](K.clamp(u)))


# ================================================================================================ script.json
@functools.lru_cache(maxsize=1)
def script():
    with open(SCRIPT_JSON, encoding='utf-8') as fh:
        return json.load(fh)


@functools.lru_cache(maxsize=64)
def line(lid):
    S = script()
    for d in S['lines']:
        if d['id'] == lid:
            return d
    for h in S['hooks']:
        for d in h.get('lines', []):
            if isinstance(d, dict) and d['id'] == lid:
                return d
    raise KeyError(lid)


# ================================================================================================ lockups
# SHOTS (C): 3-line lockup = caps y 318 / keyword y 520 / caps y 720 (bottom caps rises 4 f after the keyword);
# 2-line caps-over-key = J.HouseTitle geometry at keyword y 520 (underline on); key-over-caps number slams =
# keyword y 470 + jw_caps_bold 110 y 650; payoff keyword y 600. Exit = opacity in_cubic + 8 px up + blur 0 -> 6 over
# the last 5 f of the line's window (gone on f_out + 1).
Y3 = (318.0, 520.0, 720.0)
KEY_Y = 520.0
NUM_Y = (470.0, 650.0)
PAY_Y = 560.0                                     # SHOTS 600; 560 keeps the underline clear of the bin top (y 780)
CX = 540.0


def exit_u(t, f_out):
    return K.ramp(t, F(f_out - 5), F(f_out + 1), 'in_cubic')


def rise_static(cv, spr, t, x, y, t0, ex, op_dur=0.42, y_dur=0.6, dist=28.0):
    """House caps rise (opacity inout_sine, +28 px -> 0 out_cubic, blur 6 -> 0) with the common exit applied."""
    if t < t0 or ex >= 1.0:
        return
    uy = K.ramp(t, t0, t0 + y_dur, 'out_cubic')
    op = K.ramp(t, t0, t0 + op_dur, 'inout_sine') * (1.0 - ex)
    if op > 1e-3:
        spr.draw(cv, x, y + dist * (1.0 - uy) - 8.0 * ex, opacity=op, blur=6.0 * (1.0 - uy) + 6.0 * ex)


class Key:
    """House keyword (jw_key split into per-glyph core + one halo block, exactly like J.HouseTitle)."""

    def __init__(self, text, px):
        kw = T.measure(text, 'jw_key_core', px=px)[0]
        if kw > 940:
            px *= 940.0 / kw
        self.text, self.px = text, px
        self.g = T.Glyphs(text, 'jw_key_core', px=px)
        self.st = T.render(text, 'jw_key_core', px=px)
        self.halo = T.render(text, 'jw_key_halo', px=px)
        self.w, self.h = self.st.w, self.st.h

    def rise(self, cv, t, x, y, tk, ex, flare=0.0):
        if t < tk or ex >= 1.0:
            return
        op = 1.0 - ex
        yy = y - 8.0 * ex
        hk = K.ramp(t, tk, tk + 0.5 + 0.03 * len(self.text), 'inout_sine')
        self.halo.draw(cv, x, yy, opacity=op * hk, blur=6.0 * ex)
        if flare > 1e-3:
            self.halo.draw(cv, x, yy, opacity=min(1.0, flare) * op)
        if t - tk < 1.2:
            self.g.rise(cv, t, x, yy, t0=tk, stagger=0.03, dur=0.5, dist=0.3, blur=7, scale0=0.94, opacity=op,
                        block_blur=6.0 * ex)
        else:
            self.st.draw(cv, x, yy, opacity=op, blur=6.0 * ex)

    def slam(self, cv, t, x, y, tk, ex, s0=1.3):
        """SLAM spring 1.3 -> 1 with an exact motion smear; fully on from the hit frame (fade 0)."""
        if t < tk or ex >= 1.0:
            return
        op = 1.0 - ex
        yy = y - 8.0 * ex
        dt = t - tk
        fl = 0.9 * math.exp(-dt / 0.10)
        self.halo.draw(cv, x, yy, opacity=op, blur=6.0 * ex)
        if fl > 1e-3:
            self.halo.draw(cv, x, yy, opacity=fl * op)
        if dt < 0.7:
            self.g.slam(cv, t, x, yy, t0=tk, s0=s0, dur=0.42, fade=0, smear=True, opacity=op, block_blur=6.0 * ex)
        else:
            self.st.draw(cv, x, yy, opacity=op, blur=6.0 * ex)


def impact(cv, t, tk, x, y, w, k=1.0, ring=True):
    """Number-slam impact: a horizontal flame flare streak + an expanding thin shock ring (both additive, local,
    never full frame), decaying in ~0.3 s."""
    dt = t - tk
    if dt < 0 or dt > 0.45:
        return
    a = math.exp(-dt / 0.11) * k
    st = _flare_streak(int(w))
    K.draw(cv, st, x, y, scale=(1.0 + 0.5 * ease('out_cubic', dt / 0.3), 1.0), opacity=0.85 * a, mode='add')
    if ring:
        r = 120.0 + 260.0 * ease('out_cubic', dt / 0.3)
        K.draw(cv, _shock_ring(), x, y, scale=r / 300.0, opacity=0.4 * math.exp(-dt / 0.10) * k, mode='add')


@functools.lru_cache(maxsize=8)
def _flare_streak(w):
    h = 120
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    u = (xx + 0.5) / w * 2 - 1
    v = (yy + 0.5 - h / 2) / (h / 2)
    m = np.exp(-(v / 0.06) ** 2) * (1 - np.abs(u)) ** 1.6 + 0.35 * np.exp(-(v / 0.28) ** 2) * (1 - np.abs(u)) ** 3
    col = C('FLAME', 1.3) * 0.65 + C('AMBER', 1.0) * 0.35
    return ro(emissive(m, col))


@functools.lru_cache(maxsize=1)
def _shock_ring():
    return ro(emissive(K.ring(300, 3.0, (1, 1, 1))[..., 3], C('FLAME', 1.2)))


class Lockup:
    """A designed lockup from script.json. kind: 'house3' | 'house2' | 'payoff'. key='rise' | 'slam'."""

    def __init__(self, lid, kind, key='rise', t0=None, caps_lead=0.0, key_t=0.22, ul=None, key_y=None):
        d = line(lid)
        self.id, self.d, self.kind, self.key_mode = lid, d, kind, key
        self.f_in, self.f_out = int(d['f_in']), int(d['f_out'])
        self.t0 = F(self.f_in) - HALF if t0 is None else float(t0)
        self.caps_lead, self.key_t = float(caps_lead), float(key_t)
        L = d['lockup']
        ki = [i for i, q in enumerate(L) if q['style'].startswith('jw_key')][0]
        self.key = Key(L[ki]['text'], float(L[ki]['px']))
        self.top = txt(L[ki - 1]['text'], L[ki - 1]['style'], float(L[ki - 1]['px'])) if ki > 0 else None
        self.bot = txt(L[ki + 1]['text'], L[ki + 1]['style'], float(L[ki + 1]['px'])) if ki + 1 < len(L) else None
        if kind == 'house3':
            self.y_top, self.y_key, self.y_bot = Y3
            self.ul = False if ul is None else ul
        else:
            self.y_key = (PAY_Y if kind == 'payoff' else KEY_Y) if key_y is None else key_y
            gap = 0.30 * self.key.px
            self.y_top = self.y_key - self.key.h / 2 - gap - (self.top.h / 2 if self.top else 0)
            self.y_bot = None
            self.ul = True if ul is None else ul
        self.ul_len = int(min(860, self.key.w * 1.08 + 40))
        self.ul_y = self.y_key + self.key.h / 2 + self.key.px * 0.36
        self.under = J.underline(self.ul_len, thick=max(4.0, self.key.px * 0.026)) if self.ul else None

    @property
    def t_in(self):
        return self.t0

    def active(self, t):
        return self.t0 - self.caps_lead - HALF <= t < F(self.f_out + 1)

    def box(self):
        """(x0, y0, x1, y1) of the settled ink box incl. the underline (layout checks)."""
        ys = [self.y_key - self.key.h / 2]
        y1 = self.y_key + self.key.h / 2 + self.key.px * 0.22
        w = self.key.w
        if self.top is not None:
            ys.append(self.y_top - self.top.h / 2)
            w = max(w, self.top.w)
        if self.bot is not None:
            y1 = max(y1, self.y_bot + self.bot.h / 2)
            w = max(w, self.bot.w)
        if self.under is not None:
            y1 = max(y1, self.ul_y + 10)
            w = max(w, self.ul_len)
        return (CX - w / 2, min(ys), CX + w / 2, y1)

    def draw(self, cv, t, opacity=1.0):
        if not self.active(t):
            return
        ex = exit_u(t, self.f_out)
        ex = 1.0 - (1.0 - ex) * opacity
        t0 = self.t0
        tk = t0 + self.key_t
        if self.top is not None:
            rise_static(cv, self.top, t, CX, self.y_top, t0 - self.caps_lead, ex)
        if self.key_mode == 'slam':
            self.key.slam(cv, t, CX, self.y_key, tk, ex)
        else:
            self.key.rise(cv, t, CX, self.y_key, tk, ex)
        if self.bot is not None:
            rise_static(cv, self.bot, t, CX, self.y_bot, tk + F(4), ex)
        if self.under is not None:
            ut = t0 + (0.30 if self.key_mode == 'slam' else 0.55)

            def uu(tt):
                return K.ramp(tt, ut, ut + 0.7, 'inout_cubic')
            u = uu(t)
            if u > 0 and ex < 1.0:
                speed = (uu(t + 0.004) - uu(t - 0.004)) / 0.008 * self.ul_len
                self.under.draw(cv, CX - self.ul_len / 2, self.ul_y - 8.0 * ex, u=u, opacity=1.0 - ex,
                                smear=speed * 0.25 / FPS)


class NumLockup:
    """C11 / C12 / C13: the big counting number (serif keyword as an odometer) slams on the beat (SLAM spring
    1.45 -> 1, flare streak + shock ring), the jw_caps_bold line slams 2 f later. mode:
        'slot'  every digit reel spins and lands (2 TB),
        'step'  counts 1 -> 2 -> 3 -> 4 on f570 / f574 / f578 / f582 with the CAM A-D label light-ups (4),
        'roll'  odometer 0 -> 3,000 out_expo over 0.6 s with per-digit motion blur (3,000)."""

    def __init__(self, lid, mode, s0=1.45):
        d = line(lid)
        self.id, self.d, self.mode, self.s0 = lid, d, mode, float(s0)
        self.f_in, self.f_out = int(d['f_in']), int(d['f_out'])
        self.t0 = F(self.f_in) - HALF
        L = d['lockup']
        kt, kp = L[0]['text'], float(L[0]['px'])
        num = ''.join(ch for ch in kt if ch.isdigit())
        self.target = float(num)
        self.suffix = kt[kt.rfind(num[-1]) + 1:] if num else ''
        self.ndig = len(num)
        self.cnt = T.Counter('jw_key_core', prefix='', suffix=self.suffix, decimals=0, sep=',', px=kp,
                             blur_cap=0.12)
        self.lead = 0.1
        self.final = self.cnt.sprite(self.target, 0.0)
        self.halo = T.render(kt, 'jw_key_halo', px=kp)
        self.kw = self.final.w
        self.capg = T.Glyphs(L[1]['text'], L[1]['style'], px=float(L[1]['px']))
        self.caps = T.render(L[1]['text'], L[1]['style'], px=float(L[1]['px']))
        self.y_key, self.y_caps = NUM_Y

    def active(self, t):
        return self.t0 - HALF <= t < F(self.f_out + 1)

    def box(self):
        w = max(self.kw * self.s0 * 0 + self.kw, self.caps.w)
        return (CX - w / 2, self.y_key - self.final.h / 2, CX + w / 2, self.y_caps + self.caps.h / 2)

    def value(self, t):
        """-> (sprite, settled?)"""
        dt = t - self.t0
        if self.mode == 'slot':
            if dt > 0.75:
                return self.final, True
            return self.cnt.slot_sprite(t, self.target, t0=self.t0 - 0.04, dur=0.20, stagger=0.0, spins=1,
                                        ease='out_cubic'), False
        if self.mode == 'step':
            v, vel = 1.0, 0.0
            for k in range(1, int(self.target)):
                a = F(self.f_in + 4 * k) - HALF
                u = K.ramp(t, a, a + F(1.5), 'out_cubic')
                v += u
                if 0 < u < 1:
                    vel = 1.0 / F(1.5)
            if v >= self.target - 1e-4 and dt > 0.6:
                return self.final, True
            return self.cnt.sprite(v, vel, ndig=self.ndig), False
        # roll
        if dt > 0.75:
            return self.final, True
        u = K.clamp((dt + self.lead) / 0.6)          # starts 0.1 s before the hit: the hit frame reads '2,0..'
        v = self.target * ease('out_expo', u)
        vel = self.target * (ease('out_expo', min(1.0, u + 0.01)) - ease('out_expo', u)) / (0.01 * 0.6) if u < 1 else 0
        return self.cnt.sprite(v, vel), False

    def step_pulse(self, t):
        if self.mode != 'step':
            return 0.0
        p = 0.0
        for k in range(1, int(self.target)):
            a = F(self.f_in + 4 * k) - HALF
            if t >= a:
                p = max(p, math.exp(-(t - a) / 0.07))
        return p

    def draw(self, cv, t, opacity=1.0):
        if not self.active(t):
            return
        ex = exit_u(t, self.f_out)
        op = (1.0 - ex) * opacity
        if op <= 1e-3:
            return
        dt = t - self.t0
        sh = math.exp(-max(0.0, dt) / 0.09)
        jx, jy, _ = K.shake(t, 7.0 * sh, 26.0, seed=self.f_in)
        s = self.s0 + (1.0 - self.s0) * X.spring(max(0.0, dt), 'SLAM')
        s *= 1.0 + 0.07 * self.step_pulse(t)
        y = self.y_key - 8.0 * ex + jy
        x = CX + jx
        impact(cv, t, self.t0, CX, self.y_key + 10, 1000, k=op)
        for k in range(1, int(self.target) if self.mode == 'step' else 1):
            impact(cv, t, F(self.f_in + 4 * k) - HALF, CX, self.y_key + 10, 640, k=0.45 * op, ring=False)
        hk = 0.55 + 0.45 * K.ramp(t, self.t0, self.t0 + 0.35, 'inout_sine')
        self.halo.draw(cv, x, y, scale=s, opacity=op * hk, blur=6.0 * ex)
        fl = math.exp(-max(0.0, dt) / 0.12)
        if fl > 1e-3:
            self.halo.draw(cv, x, y, scale=s, opacity=0.9 * fl * op)
        spr, settled = self.value(t)
        spr.draw(cv, x, y, scale=s, opacity=op, blur=6.0 * ex)
        tc = self.t0 + F(2)
        if t >= tc:
            yc = self.y_caps - 8.0 * ex + jy * 0.6
            if t - tc < 0.7:
                self.capg.slam(cv, t, CX + jx * 0.6, yc, t0=tc, s0=1.28, dur=0.36, fade=0, smear=True, opacity=op,
                               block_blur=6.0 * ex)
            else:
                self.caps.draw(cv, CX, yc, opacity=op, blur=6.0 * ex)


class CountLockup(Lockup):
    """C16 'TAB / 36 / KAAFI THE.': the 3-line lockup of C1's positions; the keyword is an odometer that rolls
    DOWN from 3,000 (the editor's takes) to 36 (the roll) as it rises: one count per world."""

    def __init__(self, lid, start=3000.0, roll=0.40, hold=0.17):
        super().__init__(lid, 'house3')
        L = self.d['lockup']
        kt, kp = L[1]['text'], float(L[1]['px'])
        self.target = float(kt)
        self.start, self.roll, self.hold = float(start), float(roll), float(hold)
        self.cnt = T.Counter('jw_key_core', prefix='', suffix='', decimals=0, sep=',', px=kp, blur_cap=0.07)
        self.final = self.cnt.sprite(self.target, 0.0)

    def draw(self, cv, t, opacity=1.0):
        if not self.active(t):
            return
        ex = exit_u(t, self.f_out)
        ex = 1.0 - (1.0 - ex) * opacity
        if ex >= 1.0:
            return
        t0 = self.t0
        tk = t0 + self.key_t
        if self.top is not None:
            rise_static(cv, self.top, t, CX, self.y_top, t0, ex)
        if t >= tk:
            u = K.clamp((t - tk - self.hold) / self.roll)   # 3,000 reads sharp for 5 f, then rolls down to 36
            e = ease('out_cubic', u)
            v = self.start + (self.target - self.start) * e
            vel = (self.start - self.target) * (ease('out_cubic', min(1.0, u + 0.01)) - e) / (0.01 * self.roll)
            spr = self.final if u >= 1 else self.cnt.sprite(v, vel if 0 < u < 1 else 0.0)
            p = K.ramp(t, tk, tk + 0.3, 'out_expo')
            op = K.ramp(t, tk, tk + 0.22, 'out_cubic') * (1.0 - ex)
            y = self.y_key + (1 - p) * 0.3 * self.key.px - 8.0 * ex
            hk = K.ramp(t, tk + self.hold, tk + self.hold + self.roll + 0.15, 'inout_sine')
            self.key.halo.draw(cv, CX, y, opacity=hk * (1.0 - ex), blur=6.0 * ex)
            spr.draw(cv, CX, y, scale=0.94 + 0.06 * p, opacity=op, blur=5.0 * (1 - p) + 6.0 * ex)
        if self.bot is not None:
            rise_static(cv, self.bot, t, CX, self.y_bot, tk + F(4), ex)


@functools.lru_cache(maxsize=1)
def lockups():
    """id -> lockup object. Hook A = C1..C16 + P; hook B swaps C1/C2 for HB1/HB2 (from f60 B = A)."""
    L = {}
    L['C1'] = Lockup('C1', 'house3', t0=-0.1, caps_lead=0.15, key_t=0.0)   # enters mid-rise: f0 shows SIRF / ek
    L['C2'] = Lockup('C2', 'house3')
    L['C3'] = Lockup('C3', 'house3')
    L['C4'] = Lockup('C4', 'house3')
    L['C6'] = Lockup('C6', 'house2')
    L['C7'] = Lockup('C7', 'house3')
    L['C8'] = Lockup('C8', 'house2', key='slam', key_t=0.0)                # keyword slams with the thumb print f375
    L['C9'] = Lockup('C9', 'house2')
    L['C10'] = Lockup('C10', 'house2', key='slam', key_t=F(3))             # re-hook: caps on the snap, key on +3 f
    L['C11'] = NumLockup('C11', 'slot')
    L['C12'] = NumLockup('C12', 'step')
    L['C13'] = NumLockup('C13', 'roll')
    L['C14'] = Lockup('C14', 'house2')
    L['C15'] = Lockup('C15', 'house2', key='slam', key_t=F(2))             # the error hit f735
    L['P'] = Lockup('P', 'payoff')                                         # = J.HouseTitle timings (t0 27.0)
    L['C16'] = CountLockup('C16')
    L['HB1'] = Lockup('HB1', 'house2', t0=-0.1, caps_lead=0.15, key_t=0.0)
    L['HB2'] = Lockup('HB2', 'house2')
    return L


def lockup(lid):
    return lockups()[lid]


ORDER_A = ('C1', 'C2', 'C3', 'C4', 'C6', 'C7', 'C8', 'C9', 'C10', 'C11', 'C12', 'C13', 'C14', 'C15', 'P', 'C16')
ORDER_B = ('HB1', 'HB2') + ORDER_A[2:]


def captions(cv, t, hook='A', opacity=1.0):
    """Every lockup active at t (max two overlap: C2 -> C3 hand-off f75-f89)."""
    for lid in (ORDER_A if hook == 'A' else ORDER_B):
        if hook == 'B' and lid == 'C3' and t < F(71):
            continue
        L = lockup(lid)
        if L.active(t):
            L.draw(cv, t, opacity)
    return cv


# ================================================================================================ glass primitives
@functools.lru_cache(maxsize=64)
def glass(w, h, r=36.0, rim=1.0, glow=1.0, shadow=1.0):
    return ui.glass_card(int(w), int(h), r=float(r), look=LOOK, rim=rim, glow=glow, shadow=shadow)


@functools.lru_cache(maxsize=64)
def rrect(w, h, r, col, a=1.0):
    return ro(solid(K.rrect_alpha(int(w), int(h), float(r), 1) * np.float32(a), np.asarray(col, np.float32)))


@functools.lru_cache(maxsize=16)
def grad_bar(w, h, c0='FLAME', c1='RED', gain=1.25):
    """Rounded bar w x h, horizontal gradient c0 -> c1, a hot top sheen; + 1 px pad."""
    a = K.rrect_alpha(int(w), int(h), h / 2.0, 1)
    hh, ww = a.shape
    u = np.clip((np.arange(ww, dtype=np.float32) - 1) / max(1, w - 1), 0, 1)[None, :, None]
    col = C(c0, gain) * (1 - u) + C(c1, gain) * u
    v = np.clip((np.arange(hh, dtype=np.float32) - 1) / max(1, h - 1), 0, 1)[:, None, None]
    col = col * (1.0 + 0.45 * np.exp(-((v - 0.25) / 0.18) ** 2))
    out = np.zeros((hh, ww, 4), np.float32)
    out[..., :3] = col * a[..., None]
    out[..., 3] = a
    return ro(out)


def bar_fill(cv, x0, y, w_full, h, frac, c0='FLAME', c1='RED', opacity=1.0, head=True):
    """Gradient fill cropped to frac (sub-pixel AA end) with a glowing head on the tip."""
    if frac <= 1e-4 or opacity <= 1e-4:
        return
    spr = grad_bar(int(w_full), int(h), c0, c1)
    wf = frac * w_full
    n = int(math.ceil(wf)) + 2
    s = np.array(spr[:, :min(n, spr.shape[1])], copy=True)
    xs = np.arange(s.shape[1], dtype=np.float32) - 1
    s *= np.clip(wf - xs, 0, 1)[None, :, None]
    K.draw(cv, s, x0 - 1, y - h / 2.0 - 1, anchor=(0, 0), opacity=opacity)
    if head and frac < 0.999:
        K.draw(cv, _head(h), x0 + wf - h * 0.3, y, opacity=opacity, mode='add')


@functools.lru_cache(maxsize=4)
def _head(h):
    d = K.disc(h * 0.42, C('WHITE', 1.6))
    return ro(K.glow(d, C('AMBER', 1.3), sigmas=(3, 8, 20), strength=1.2, weights=(1.0, 0.6, 0.35)))


@functools.lru_cache(maxsize=8)
def dot_spr(r, cname='ASH', k=1.0):
    return ro(K.disc(r, C(cname, k)))


@functools.lru_cache(maxsize=32)
def icon(name, size, cname='ASH', stroke=2.2):
    return ui.icon(name, size, cname, stroke=stroke)


@functools.lru_cache(maxsize=1)
def drive_icon():
    """Tiny portable-drive glyph (34 x 22 rounded body, activity LED) for the storage HUD."""
    w, h, p = 34, 22, 6
    body = K.rrect_alpha(w, h, 5.0, p)
    inner = np.zeros_like(body)
    inner[p + 2:p + h - 2, p + 2:p + w - 2] = K.rrect_alpha(w - 4, h - 4, 3.0, 0)
    ring = np.clip(body - inner, 0, 1)
    spr = solid(ring, C('ASH', 0.9))
    led = np.zeros_like(body)
    led[p + h - 7:p + h - 4, p + w - 11:p + w - 5] = 1.0
    spr = spr + emissive(led, C('FLAME', 2.0))
    return ro(K.glow(spr, None, sigmas=(2,), strength=0.0))


# ================================================================================================ S4 day chip
DAY_C = (540.0, 820.0)
DAYS = ((240, 'DIN 1'), (255, 'DIN 2'), (270, 'DIN 3'))
DAY_OUT = 290                                     # exits with C6 (f286-f290)


@functools.lru_cache(maxsize=8)
def day_spr(name, sel):
    return ui.chip(name, sel=1.0 if sel else 0.0, look=LOOK, size=44, h=92, icon_name='calendar', pad_x=34,
                   grad=('RED', 'EMBER') if sel else None)


def day_chip(cv, t, opacity=1.0):
    """'DIN 1' f240 -> 'DIN 2' f255 -> 'DIN 3' f270 (selected, ember gradient: night + safelight); each swap: the
    old chip lifts 14 px and fades over 3 f while the new one pops (POP spring 0.82 -> 1)."""
    if t < F(240) - HALF or t >= F(DAY_OUT + 1):
        return
    ex = exit_u(t, DAY_OUT)
    for i, (f0, name) in enumerate(DAYS):
        a = F(f0) - HALF
        nxt = F(DAYS[i + 1][0]) - HALF if i + 1 < len(DAYS) else None
        if t < a:
            continue
        o = (1.0 - ex) * opacity
        dy = -8.0 * ex
        if nxt is not None and t >= nxt:
            q = K.ramp(t, nxt - HALF, nxt + F(1.5), 'in_cubic')
            o *= 1.0 - q
            dy -= 20.0 * q
        if o <= 1e-3:
            continue
        k = 0.82 + 0.18 * X.spring(t - a, 'POP')
        op = o * K.ramp(t, a + F(0.5), a + F(2.5), 'out_cubic')
        ui.place(cv, day_spr(name, i == 2), DAY_C[0], DAY_C[1] + dy, scale=k, opacity=op)
        if i == 2:                                 # the safelight comes on: one warm pulse in the chip
            pl = math.exp(-max(0.0, t - a) / 0.25)
            if pl > 0.02:
                K.draw(cv, _chip_glow(), DAY_C[0], DAY_C[1] + dy, opacity=0.6 * pl * o, mode='add')


@functools.lru_cache(maxsize=1)
def _chip_glow():
    w, h = ui.chip_size('DIN 3', 44, 92, 'calendar', 34)
    m = K.rrect_alpha(w, h, h / 2.0, 40)
    return ro(K.glow(emissive(m, C('RED')), C('RED', 1.0), sigmas=(10, 26), strength=0.7, include=False))


# ================================================================================================ S7 storage HUD
HUD_C = (540.0, 860.0)
HUD_W, HUD_H = 640, 140
HUD_T0 = F(540) - HALF
HUD_FILL = (F(540), F(565))
HUD_OUT = 599                                     # hard cut f600 (the bin takes over)
BAR_X0, BAR_X1, BAR_Y, BAR_H = 260.0, 820.0, 896.0, 14


@functools.lru_cache(maxsize=1)
def hud_counter():
    return T.Counter('jw_mono', prefix='', suffix=' TB', decimals=2, px=46, font=J.MONO_BOLD, fill=('IVORY', 0.95))


@functools.lru_cache(maxsize=1)
def hud_panel():
    """Glass card with the static parts baked in: drive glyph, STORAGE label, bar track + quarter ticks."""
    base = glass(HUD_W, HUD_H, 32.0)
    f = base.copy() if hasattr(base, 'copy') else base.face.copy()
    f = np.array(base.face, copy=True)
    p = base.pad
    x0, y0 = HUD_C[0] - HUD_W / 2, HUD_C[1] - HUD_H / 2
    K.draw(f, drive_icon(), p + 262 - x0, p + 838 - y0)
    txt('STORAGE', 'jw_mono', 34, ('ASH', 1.0)).draw(f, p + 290 - x0, p + 838 - y0, anchor=(0, 0.5))
    tw = int(BAR_X1 - BAR_X0)
    K.draw(f, rrect(tw, BAR_H, BAR_H / 2, tuple(C('NIGHT_0')), 0.85), p + BAR_X0 - x0, p + BAR_Y - y0, anchor=(0, 0.5))
    K.draw(f, rrect(tw, BAR_H, BAR_H / 2, tuple(C('SMOKE', 1.4)), 0.55), p + BAR_X0 - x0, p + BAR_Y - y0,
           anchor=(0, 0.5))
    for q in (0.25, 0.5, 0.75):
        K.draw(f, rrect(2, 6, 1, tuple(C('ASH')), 0.5), p + BAR_X0 + q * tw - x0, p + BAR_Y + 15 - y0)
    return ui.derive_panel(base, f)


def hud_value(t):
    return 2.0 * K.ramp(t, HUD_FILL[0], HUD_FILL[1], 'out_cubic')


def storage_hud(cv, t, opacity=1.0):
    """S7 f540-f599: POP in, value 0.00 -> 2.00 TB rolling (f540-f565, out_cubic) with the flame fill."""
    if t < HUD_T0 or t >= F(HUD_OUT + 1):
        return
    k = 0.92 + 0.08 * X.spring(t - HUD_T0, 'POP')
    op = K.ramp(t, HUD_T0, HUD_T0 + F(4), 'out_cubic') * opacity
    pan = hud_panel()
    sweep = ((t - HUD_T0) * 0.6) % 1.0
    face = pan.face_at(sweep=sweep, sweep_gain=0.9)
    pan.draw(cv, HUD_C[0], HUD_C[1], scale=k, opacity=op, face=face)

    def P(x, y):
        return HUD_C[0] + (x - HUD_C[0]) * k, HUD_C[1] + (y - HUD_C[1]) * k
    v = hud_value(t)
    vel = (hud_value(t + 0.01) - hud_value(t - 0.01)) / 0.02
    vx, vy = P(840, 838)
    hud_counter().draw(cv, v, vx, vy, anchor=(1.0, 0.5), scale=k, vel=vel, opacity=op)
    bx, by = P(BAR_X0, BAR_Y)
    if k > 0.999:
        bar_fill(cv, bx, by, BAR_X1 - BAR_X0, BAR_H, v / 2.0, opacity=op)
    else:
        lay = np.zeros((40, int(BAR_X1 - BAR_X0) + 60, 4), np.float32)
        bar_fill(lay, 20, 20, BAR_X1 - BAR_X0, BAR_H, v / 2.0, opacity=1.0)
        K.draw(cv, lay, bx - 20 * k, by - 20 * k, scale=k, anchor=(0, 0), opacity=op)


# ================================================================================================ clip thumbnails
TW0, TH0 = 72, 128                               # tile at zoom 1 (10 columns); f660 snap zoom x1.5 -> 108 x 192
NCOL, GAP = 10, 10
PITCH_X, PITCH_Y = TW0 + GAP, TH0 + GAP
NPOOL = 28


def _vnoise(h, w, cells, rng):
    g = rng.standard_normal((cells[0] + 3, cells[1] + 3)).astype(np.float32)
    n = cv2.resize(g, (w + 2 * (w // cells[1]), h + 2 * (h // cells[0])), interpolation=cv2.INTER_CUBIC)
    oy, ox = h // cells[0], w // cells[1]
    return n[oy:oy + h, ox:ox + w]


def _fbm(h, w, rng, base=(3, 2), octaves=4):
    acc = np.zeros((h, w), np.float32)
    a, tot = 1.0, 0.0
    for o in range(octaves):
        cy, cx = base[0] * 2 ** o, base[1] * 2 ** o
        acc += a * _vnoise(h, w, (cy, cx), rng)
        tot += a
        a *= 0.5
    return acc / tot


def _ridge(w, rng, base, amp, octaves=4, rough=0.5):
    x = np.zeros(w, np.float32)
    a = amp
    for o in range(octaves):
        n = 3 * 2 ** o
        pts = rng.standard_normal(n + 3).astype(np.float32)
        x += a * cv2.resize(pts[None, :], (w, 1), interpolation=cv2.INTER_CUBIC)[0]
        a *= rough
    return base + x


def _sky(h, w, top, mid, hor, horizon=0.6):
    y = (np.arange(h, dtype=np.float32) / h)[:, None, None]
    a = np.clip(y / horizon, 0, 1)
    c = np.where(a < 0.6, top + (mid - top) * (a / 0.6), mid + (hor - mid) * ((a - 0.6) / 0.4))
    return np.broadcast_to(c, (h, w, 3)).astype(np.float32).copy()


def _sun(img, cx, cy, r, col, glow=3.0, k=1.0):
    h, w = img.shape[:2]
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    d = np.sqrt((xx - cx) ** 2 + (yy - cy) ** 2)
    img += (np.clip(r - d + 1, 0, 1) * 1.2 + np.exp(-d / (r * glow)) * 0.55)[..., None] * col * k


def _layer(img, ys, col, soft=1.2):
    h, w = img.shape[:2]
    yy = np.arange(h, dtype=np.float32)[:, None]
    m = np.clip((yy - ys[None, :]) / soft + 0.5, 0, 1)
    img[:] = img * (1 - m[..., None]) + m[..., None] * col


def _bokeh(img, rng, n, cols, rr=(3, 10), k=0.8, region=(0, 1)):
    h, w = img.shape[:2]
    for _ in range(n):
        r = rng.uniform(*rr)
        cx, cy = rng.uniform(0, w), rng.uniform(region[0] * h, region[1] * h)
        c = np.asarray(cols[rng.integers(len(cols))], np.float32)
        x0, x1 = int(max(0, cx - r - 2)), int(min(w, cx + r + 3))
        y0, y1 = int(max(0, cy - r - 2)), int(min(h, cy + r + 3))
        if x1 <= x0 or y1 <= y0:
            continue
        yy, xx = np.mgrid[y0:y1, x0:x1].astype(np.float32)
        d = np.sqrt((xx - cx) ** 2 + (yy - cy) ** 2)
        m = np.clip(r - d + 0.5, 0, 1) * (0.7 + 0.3 * np.clip(d / r, 0, 1) ** 3)
        img[y0:y1, x0:x1] += m[..., None] * c * k * rng.uniform(0.4, 1.0)


def _thumb_scene(kind, seed, h=256, w=144):
    """A faceless 'footage frame' in display sRGB (h, w, 3) 0..1: landscapes, nature, night city, abstract light.
    No people, no faces, no text (BIJLI_SERIES hard rule)."""
    rng = np.random.default_rng(seed)
    X_ = lambda *v: np.asarray(v, np.float32)     # noqa: E731
    if kind == 'sunset_hills':
        img = _sky(h, w, X_(0.10, 0.10, 0.22), X_(0.75, 0.38, 0.22), X_(1.0, 0.72, 0.42), 0.62)
        _sun(img, rng.uniform(0.3, 0.7) * w, 0.56 * h, 9, X_(1.0, 0.8, 0.5))
        for i, (b, c) in enumerate(((0.58, X_(0.42, 0.24, 0.24)), (0.68, X_(0.22, 0.13, 0.14)), (0.80, X_(0.08, 0.05, 0.06)))):
            _layer(img, _ridge(w, rng, b * h, (10 - 2 * i) * 1.0), c, 1.5 + i)
    elif kind == 'sea':
        img = _sky(h, w, X_(0.18, 0.28, 0.45), X_(0.65, 0.62, 0.65), X_(0.98, 0.78, 0.55), 0.5)
        hy = 0.5 * h
        sx = rng.uniform(0.35, 0.65) * w
        _sun(img, sx, hy - 14, 8, X_(1.0, 0.85, 0.6))
        yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
        sea = (yy > hy)[..., None]
        wav = _fbm(h, w, rng, (24, 3), 3)
        depth = np.clip((yy - hy) / (h - hy), 0, 1)
        sc = X_(0.10, 0.20, 0.30) * (1 - depth[..., None]) * 1.4 + X_(0.03, 0.06, 0.09) * depth[..., None]
        streak = np.exp(-((xx - sx) / (6 + 30 * depth)) ** 2) * (0.5 + 0.5 * np.clip(wav * 2, 0, 1))
        sc = sc + streak[..., None] * X_(1.0, 0.75, 0.45) * 0.9 * (1 - depth[..., None] * 0.5)
        img = np.where(sea, sc, img)
    elif kind == 'city_night':
        img = _sky(h, w, X_(0.02, 0.03, 0.07), X_(0.08, 0.07, 0.12), X_(0.30, 0.15, 0.10), 0.75)
        x = 0
        base = 0.62 * h
        while x < w:
            bw = int(rng.uniform(10, 26))
            bh = rng.uniform(0.15, 0.45) * h
            y0 = int(base + 0.25 * h - bh)
            img[y0:, x:x + bw] = X_(0.03, 0.03, 0.05)
            for wy in range(y0 + 4, h - 4, 6):
                for wx in range(x + 2, min(w, x + bw) - 2, 4):
                    if rng.random() < 0.35:
                        img[wy:wy + 2, wx:wx + 2] = X_(1.0, 0.75, 0.40) * rng.uniform(0.4, 1.0)
            x += bw + int(rng.uniform(0, 4))
        _bokeh(img, rng, 26, [X_(1.0, 0.6, 0.3), X_(1.0, 0.3, 0.2), X_(0.9, 0.85, 0.7)], (3, 9), 0.6, (0.8, 1.0))
    elif kind == 'road_trails':
        img = _sky(h, w, X_(0.02, 0.02, 0.04), X_(0.06, 0.05, 0.08), X_(0.20, 0.10, 0.08), 0.5)
        yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
        vx, vy = w * rng.uniform(0.4, 0.6), 0.42 * h
        for j, (off, col) in enumerate(((-0.9, X_(1.0, 0.25, 0.12)), (-0.55, X_(1.0, 0.3, 0.15)),
                                        (0.5, X_(1.0, 0.9, 0.75)), (0.85, X_(1.0, 0.85, 0.6)))):
            tt = np.clip((yy - vy) / (h - vy), 0, 1)
            lx = vx + off * tt * w * 0.9
            d = np.abs(xx - lx)
            m = np.exp(-(d / (0.6 + 2.2 * tt)) ** 2) * (yy > vy) * (0.5 + tt)
            img += m[..., None] * col * 0.9
        img[int(vy):] += X_(0.03, 0.025, 0.02)
    elif kind == 'forest_mist':
        img = _sky(h, w, X_(0.55, 0.58, 0.55), X_(0.70, 0.70, 0.62), X_(0.80, 0.76, 0.66), 0.7)
        for i in range(4):
            col = X_(0.42, 0.45, 0.40) * (1 - i * 0.24)
            base = (0.42 + i * 0.13) * h
            ys = np.full(w, base, np.float32)
            for _ in range(int(w / 9) + 3):
                cx = rng.uniform(0, w)
                th = rng.uniform(18, 40) * (1 + i * 0.3)
                xs = np.arange(w, dtype=np.float32)
                tri = base - th + np.abs(xs - cx) * (th / rng.uniform(5, 9))
                ys = np.minimum(ys, tri)
            _layer(img, ys, col, 1.0 + (3 - i) * 0.8)
    elif kind == 'dunes':
        img = _sky(h, w, X_(0.35, 0.45, 0.62), X_(0.85, 0.75, 0.62), X_(0.98, 0.85, 0.66), 0.45)
        for i in range(4):
            ys = _ridge(w, rng, (0.45 + 0.13 * i) * h, 8 + 3 * i, 3, 0.35)
            c = X_(0.85, 0.52, 0.30) * (1.0 - 0.18 * i)
            _layer(img, ys, c, 1.0)
            yy = np.arange(h, dtype=np.float32)[:, None]
            m = np.clip((yy - ys[None, :]) / 22.0, 0, 1) * (yy > ys[None, :])
            img *= (1 - 0.25 * m * (1 - m))[..., None]
    elif kind == 'lamp_room':
        img = np.zeros((h, w, 3), np.float32) + X_(0.05, 0.035, 0.03)
        yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
        lx, ly = rng.uniform(0.25, 0.75) * w, rng.uniform(0.3, 0.5) * h
        d = np.sqrt((xx - lx) ** 2 + ((yy - ly) * 0.8) ** 2)
        img += np.exp(-d / 40.0)[..., None] * X_(1.0, 0.55, 0.25) * 0.9
        img[int(0.72 * h):] *= 0.55
        _bokeh(img, rng, 10, [X_(1.0, 0.6, 0.3), X_(1.0, 0.45, 0.2)], (6, 16), 0.35, (0.1, 0.7))
        win = (xx > w * 0.70) & (yy < h * 0.5) & (yy > h * 0.1)
        img[win] += X_(0.10, 0.14, 0.20)
    elif kind == 'snow_peaks':
        img = _sky(h, w, X_(0.20, 0.35, 0.60), X_(0.55, 0.68, 0.82), X_(0.85, 0.88, 0.90), 0.55)
        ys = _ridge(w, rng, 0.42 * h, 34, 5, 0.55)
        yy = np.arange(h, dtype=np.float32)[:, None]
        m = np.clip((yy - ys[None, :]) + 0.5, 0, 1)
        snow = np.clip(1 - (yy - ys[None, :]) / 26.0, 0, 1) * m
        rock = X_(0.22, 0.22, 0.25)
        img = img * (1 - m[..., None]) + m[..., None] * (rock * (1 - snow[..., None]) + X_(0.95, 0.95, 0.97) * snow[..., None])
        _layer(img, _ridge(w, rng, 0.72 * h, 10), X_(0.10, 0.12, 0.12), 1.5)
    elif kind == 'clouds':
        img = _sky(h, w, X_(0.25, 0.42, 0.70), X_(0.50, 0.62, 0.80), X_(0.78, 0.80, 0.82), 1.0)
        n = _fbm(h, w, rng, (4, 2), 5)
        n = cv2.GaussianBlur(n, (0, 0), 3.0)
        c = np.clip(n * 2.0, 0, 1) ** 1.5
        yy = np.arange(h, dtype=np.float32)[:, None]
        lit = np.clip(1.0 - yy / h, 0.3, 1.0)
        img = img * (1 - c[..., None] * 0.75) + (c * lit)[..., None] * X_(0.98, 0.90, 0.80) * 0.85
        _layer(img, _ridge(w, rng, 0.82 * h, 6), X_(0.06, 0.06, 0.07), 1.2)
    elif kind == 'rain_bokeh':
        img = np.zeros((h, w, 3), np.float32) + X_(0.03, 0.03, 0.04)
        _bokeh(img, rng, 40, [X_(1.0, 0.55, 0.25), X_(0.9, 0.2, 0.15), X_(0.95, 0.85, 0.6), X_(0.4, 0.5, 0.7)],
               (5, 18), 0.45)
        img = cv2.GaussianBlur(img, (0, 0), 1.2)
    elif kind == 'stage_beams':
        img = np.zeros((h, w, 3), np.float32) + X_(0.02, 0.015, 0.02)
        yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
        for _ in range(3):
            sx = rng.uniform(0, w)
            ang = rng.uniform(-0.5, 0.5)
            d = np.abs((xx - sx) - (yy) * ang)
            m = np.exp(-(d / (2 + yy * 0.12)) ** 2) * (1 - yy / h * 0.6)
            img += m[..., None] * X_(1.0, 0.55, 0.30) * 0.5
        img += (_fbm(h, w, rng, (6, 3), 3)[..., None] * 0.02)
    elif kind == 'river_valley':
        img = _sky(h, w, X_(0.40, 0.50, 0.62), X_(0.80, 0.72, 0.60), X_(0.95, 0.80, 0.60), 0.4)
        _layer(img, _ridge(w, rng, 0.36 * h, 14), X_(0.38, 0.40, 0.38), 1.5)
        _layer(img, _ridge(w, rng, 0.48 * h, 12), X_(0.22, 0.26, 0.20), 1.2)
        yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
        cx = w * 0.5 + 18 * np.sin(yy / 30.0 + rng.uniform(0, 6))
        rv = np.exp(-((xx - cx) / (2 + (yy - 0.5 * h).clip(0) * 0.25)) ** 2) * (yy > 0.52 * h)
        img = img * (1 - rv[..., None]) + rv[..., None] * X_(0.85, 0.80, 0.70)
    else:                                          # 'tint' abstract footage: soft gradient + light leak
        img = np.zeros((h, w, 3), np.float32)
        a = np.asarray([rng.uniform(0.05, 0.4) for _ in range(3)], np.float32)
        b = np.asarray([rng.uniform(0.3, 1.0), rng.uniform(0.15, 0.6), rng.uniform(0.05, 0.4)], np.float32)
        y = (np.arange(h, dtype=np.float32) / h)[:, None, None]
        img += a * (1 - y) + b * y * 0.6
        n = cv2.GaussianBlur(_fbm(h, w, rng, (3, 2), 3), (0, 0), 6.0)
        img += np.clip(n * 1.5, 0, 1)[..., None] * X_(1.0, 0.5, 0.2) * 0.4
    # lens + sensor: vignette, mild contrast, grain (it is footage, not a flat illustration)
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    r2 = ((xx - w / 2) / (w * 0.62)) ** 2 + ((yy - h / 2) / (h * 0.62)) ** 2
    img = img * np.clip(1.05 - 0.45 * r2, 0.35, 1.05)[..., None]
    img = img + rng.standard_normal(img.shape).astype(np.float32) * 0.012
    return np.clip(img, 0, 1)


THUMB_KINDS = ('sunset_hills', 'sea', 'city_night', 'road_trails', 'forest_mist', 'dunes', 'lamp_room', 'snow_peaks',
               'clouds', 'rain_bokeh', 'stage_beams', 'river_valley', 'tint')


@functools.lru_cache(maxsize=1)
def thumb_pool():
    """NPOOL faceless footage thumbnails at 2x the zoomed tile (216 x 384 -> stored 108 x 192), each with a random
    exposure / white-balance offset (+-10 %), linear premultiplied, rounded r 10 at zoomed size."""
    out = []
    rng = np.random.default_rng(36)
    for i in range(NPOOL):
        kind = THUMB_KINDS[i % len(THUMB_KINDS)]
        img = _thumb_scene(kind, 1000 + i, 384, 216)
        img = cv2.resize(img, (108, 192), interpolation=cv2.INTER_AREA)
        lin = K.to_lin(np.clip(img, 0, 1)).astype(np.float32)
        lin *= np.float32(0.78 * rng.uniform(0.9, 1.1))       # tiles sit under the lockups: keep them below the type
        lin *= np.asarray([rng.uniform(0.95, 1.05), 1.0, rng.uniform(0.92, 1.05)], np.float32)
        a = K.rrect_alpha(108, 192, 10.0, 0)
        spr = np.zeros((192, 108, 4), np.float32)
        spr[..., :3] = lin * a[..., None]
        spr[..., 3] = a
        # 1 px inner hairline (the tile sits behind glass) + soft inner shade at the edge
        sdf = K.rrect_sdf(108, 192, 10.0, 0)
        hl = np.clip(1.0 - np.abs(sdf + 1.0), 0, 1) * a
        spr[..., :3] = spr[..., :3] * (1 - 0.30 * np.exp(sdf / 6.0) * a)[..., None] + hl[..., None] * C('IVORY', 0.10)
        out.append(ro(spr))
    return tuple(out)


def _h(i, s=0):
    """Deterministic hash -> [0, 1)."""
    x = (i * 2654435761 + s * 40503 + 12345) & 0xFFFFFFFF
    x ^= x >> 13
    x = (x * 1274126177) & 0xFFFFFFFF
    x ^= x >> 16
    return (x & 0xFFFFFF) / float(0x1000000)


@functools.lru_cache(maxsize=1)
def tile_ring():
    """Selected / playing tile ring (3 px FLAME, glow) at zoomed size 108 x 192."""
    sdf = K.rrect_sdf(108, 192, 11.0, 14)
    m = np.clip(1.6 - np.abs(sdf + 0.5), 0, 1)
    spr = solid(m, C('FLAME', 1.5))
    return ro(K.glow(spr, C('FLAME'), sigmas=(3, 8), strength=0.5))


@functools.lru_cache(maxsize=1)
def tile_bar():
    """Watched bar (FLAME 5 px, full tile width minus 8 px inset), zoomed size."""
    return grad_bar(92, 5, 'FLAME', 'RED', 1.4)


# ================================================================================================ S8 media bin
BIN_C = (540.0, 1160.0)
BIN_W, BIN_H = 900, 760
BIN_X0, BIN_Y0 = BIN_C[0] - BIN_W / 2, BIN_C[1] - BIN_H / 2     # 90, 780
HDR_Y = 828.0
STO_Y = 886.0
STO_X0, STO_X1 = 130.0, 596.0
GRID_Y0, GRID_Y1 = 916.0, 1514.0
GRID_X0 = BIN_C[0] - (NCOL * TW0 + (NCOL - 1) * GAP) / 2.0       # 125
GRID_W = NCOL * TW0 + (NCOL - 1) * GAP                           # 810
BIN_T0 = F(600) - HALF
FREEZE = F(780)
ZOOM_T = (F(660) - HALF, F(666))                                 # out_expo 6 f
DISK_T = F(735) - HALF
WATCH_T = F(675) - HALF
TAKES = 3000


def bin_time(t):
    return min(t, FREEZE)


def scroll_px(t):
    """Grid scroll (px at zoom 1): speed 120 -> 620 px/s, in_quad over f600-f779 (0.6 -> 3 rows/s of SHOTS'
    204 px rows), integrated; frozen from f780."""
    s = max(0.0, bin_time(t) - F(600))
    D = F(780) - F(600)
    u = min(1.0, s / D)
    return 120.0 * s + 500.0 * D * (u ** 3) / 3.0 + 40.0


def grid_zoom(t):
    return 1.0 + 0.5 * K.ramp(bin_time(t), ZOOM_T[0], ZOOM_T[1], 'out_expo')


def take_value(t):
    return 1.0 + (TAKES - 1.0) * K.ramp(bin_time(t), F(600), F(650), 'in_cubic')


def bin_dim(t):
    """0 -> 0.62 darkening of the frozen bin f780-f795 (SHOTS: bin x0.45; a touch deeper so toast + payoff lead)."""
    return 0.62 * K.ramp(t, FREEZE - HALF, F(795), 'inout_sine')


def bin_glitch(t):
    """2-frame DISK FULL glitch on f735-f736 -> 0..1."""
    k = fidx(t)
    return {735: 1.0, 736: 0.6}.get(k, 0.0)


def post_kw(t):
    g = bin_glitch(t)
    return {'rgb_split': 0.6 * g} if g > 0 else {}


@functools.lru_cache(maxsize=1)
def take_counter():
    return T.Counter('jw_mono', prefix='', suffix='', decimals=0, sep=',', px=46, font=J.MONO_BOLD,
                     fill=('IVORY', 0.95))


@functools.lru_cache(maxsize=1)
def take_width():
    return take_counter().sprite(3000.0, 0.0, ndig=4).w


@functools.lru_cache(maxsize=1)
def bin_panel():
    """The bin glass with its static header baked in: grid icon + MEDIA BIN, TAKE label, storage track."""
    base = glass(BIN_W, BIN_H, 40.0)
    f = np.array(base.face, copy=True)
    p = base.pad

    def P(x, y):
        return p + x - BIN_X0, p + y - BIN_Y0
    K.draw(f, icon('grid', 34, 'ASH', 2.2), *P(146, HDR_Y))
    txt('MEDIA BIN', 'jw_mono', 34, ('ASH', 1.0)).draw(f, *P(176, HDR_Y), anchor=(0, 0.5))
    tw = int(STO_X1 - STO_X0)
    K.draw(f, rrect(tw, 12, 6, tuple(C('NIGHT_0')), 0.85), *P(STO_X0, STO_Y), anchor=(0, 0.5))
    # hairline under the header rows (grid well)
    K.draw(f, rrect(BIN_W - 80, 1, 0.5, tuple(C('ASH')), 0.18), *P(BIN_X0 + 40, GRID_Y0 - 6), anchor=(0, 0.5))
    return ui.derive_panel(base, f)


@functools.lru_cache(maxsize=1)
def grid_mask():
    """Vertical feather of the grid well (rows GRID_Y0..GRID_Y1, 16 px soft edges), (h, 1)."""
    h = int(GRID_Y1 - GRID_Y0)
    ys = np.arange(h, dtype=np.float32) + 0.5
    m = np.clip(ys / 16.0, 0, 1) * np.clip((h - ys) / 16.0, 0, 1)
    return ro(m[:, None, None])


def _tile_watch(idx, t, sx, sy):
    """Watched fraction of a tile: before f675 a few tiles are part-watched; f675-f690 a wave fills every bar
    (top-left -> bottom-right in screen space); afterwards every take is watched."""
    base = 0.0
    r = _h(idx, 7)
    if r < 0.32:
        base = 0.25 + 0.75 * _h(idx, 8)
    if t < WATCH_T:
        return base
    d = ((sx - GRID_X0) / GRID_W) * 0.5 + ((sy - GRID_Y0) / (GRID_Y1 - GRID_Y0)) * 0.5
    u = K.ramp(t, WATCH_T + 0.30 * d, WATCH_T + 0.30 * d + 0.16, 'out_cubic')
    return base + (1.0 - base) * u


def _grid_layer(t):
    """The clip grid inside the well at bin time t -> (layer (h, w, 4), x0, y0)."""
    tb = bin_time(t)
    z = grid_zoom(t)
    pool = thumb_pool()
    ring = tile_ring()
    bar = tile_bar()
    lw, lh = int(BIN_W - 40), int(GRID_Y1 - GRID_Y0)
    lx0, ly0 = BIN_X0 + 20, GRID_Y0
    lay = np.zeros((lh, lw, 4), np.float32)
    s = scroll_px(t)
    zc = (BIN_C[0], (GRID_Y0 + GRID_Y1) / 2.0)                    # zoom about the well's centre
    # playing tile: 2nd visible row (screen y ~ 1150 at zoom 1), column steps every 5 f
    play_col = int(tb * FPS / 5.0) % NCOL
    play_u = (tb * FPS / 5.0) % 1.0
    tsz = z * TW0 / 108.0                                          # sprite scale (sprites are zoomed size)
    first_row = int(math.floor((s + (GRID_Y0 - zc[1]) / z + zc[1] - GRID_Y0 - 20) / PITCH_Y)) - 1
    rows = int(lh / (PITCH_Y * z)) + 4
    play_row = None
    best = 1e9
    for r in range(first_row, first_row + rows):
        cy0 = GRID_Y0 + 6 + r * PITCH_Y - s + TH0 / 2.0             # grid-space centre y at zoom 1
        sy = zc[1] + (cy0 - zc[1]) * z
        if abs(sy - 1130.0) < best:
            best, play_row = abs(sy - 1130.0), r
    for r in range(first_row, first_row + rows):
        if r < 0:
            continue
        cy0 = GRID_Y0 + 6 + r * PITCH_Y - s + TH0 / 2.0
        sy = zc[1] + (cy0 - zc[1]) * z
        if sy < GRID_Y0 - TH0 * z or sy > GRID_Y1 + TH0 * z:
            continue
        for c in range(NCOL):
            idx = r * NCOL + c
            cx0 = GRID_X0 + c * PITCH_X + TW0 / 2.0
            sx = zc[0] + (cx0 - zc[0]) * z
            if sx < lx0 - TW0 * z or sx > lx0 + lw + TW0 * z:
                continue
            spr = pool[int(_h(idx, 1) * NPOOL) % NPOOL]
            lx, ly = sx - lx0, sy - ly0
            K.draw(lay, spr, lx, ly, scale=tsz)
            w = _tile_watch(idx, t, sx, sy)
            if w > 1e-3:
                K.draw(lay, rrect(92, 5, 2.5, tuple(C('NIGHT_0')), 0.7), lx - 46 * tsz, ly + 84 * tsz,
                       scale=tsz, anchor=(0, 0.5))
                bar_fill(lay, lx - 46 * tsz, ly + 84 * tsz, 92 * tsz, max(2.0, 5 * tsz), w, head=False)
            playing = (r == play_row and c == play_col and t < FREEZE + 1.0)
            if playing:
                K.draw(lay, ring, lx, ly, scale=tsz)
                px_ = lx + (-54 + 108 * play_u) * tsz                # scrub playhead across the tile
                K.draw(lay, _playhead(), px_, ly, scale=tsz)
            elif _h(idx, 3) < 0.07:
                K.draw(lay, ring, lx, ly, scale=tsz, opacity=0.55)
    lay *= grid_mask()
    return lay, lx0, ly0


@functools.lru_cache(maxsize=1)
def _playhead():
    m = np.zeros((200, 12), np.float32)
    m[4:196, 4:8] = 1.0
    return ro(K.glow(solid(m, C('AMBER', 1.6)), C('FLAME'), sigmas=(3, 8), strength=0.8))


@functools.lru_cache(maxsize=1)
def _scroll_track():
    return rrect(4, int(GRID_Y1 - GRID_Y0 - 24), 2, tuple(C('ASH')), 0.16)


def disk_chip_spr():
    return ui.chip('DISK FULL', sel=1.0, look=LOOK, size=34, h=60, pad_x=26, grad=('RED', 'EMBER'))


def media_bin(cv, t, opacity=1.0):
    """S8 + S9 (f600-f899): glass bin, header (MEDIA BIN · TAKE count), storage bar (full; RED + DISK FULL chip
    from f735), the clip grid (scroll accelerates, f660 snap zoom x1.5, watched-bar wave from f675, hover-scrub
    tile), scrollbar; freezes on f780 (t clamps), darkens x0.45 f780-f795; slice glitch f735-f736."""
    if t < BIN_T0:
        return
    tb = bin_time(t)
    k = 0.96 + 0.04 * X.spring(t - BIN_T0, 'POP')
    k *= 1.0 + 0.012 * math.exp(-max(0.0, t - ZOOM_T[0]) / 0.08) * (t >= ZOOM_T[0])
    op = K.ramp(t, BIN_T0, BIN_T0 + F(3), 'out_cubic') * opacity
    pan = bin_panel()
    face = pan.face_at(sweep=(tb * 0.35) % 1.0, sweep_gain=0.9)
    lay = np.zeros((BIN_H + 2 * 60, BIN_W + 2 * 60, 4), np.float32)    # bin-local layer (card + content)
    ox, oy = BIN_X0 - 60, BIN_Y0 - 60

    def L(x, y):
        return x - ox, y - oy
    # grid
    g, gx, gy = _grid_layer(t)
    K.draw(lay, g, *L(gx, gy), anchor=(0, 0))
    # scrollbar (thumb = 4.3 visible rows of 300)
    track_y0 = GRID_Y0 + 12
    th = int(GRID_Y1 - GRID_Y0 - 24)
    K.draw(lay, _scroll_track(), *L(BIN_X0 + BIN_W - 26, track_y0), anchor=(0.5, 0))
    rows_total = TAKES / NCOL
    pos = (scroll_px(t) / PITCH_Y) / rows_total
    K.draw(lay, rrect(4, 22, 2, tuple(C('FLAME', 1.2)), 0.9), *L(BIN_X0 + BIN_W - 26, track_y0 + pos * (th - 22)),
           anchor=(0.5, 0))
    # header: TAKE  0,001 -> 3,000 (rolls f600-f650 in_cubic, holds)
    v = take_value(t)
    vel = (take_value(t + 0.01) - take_value(t - 0.01)) / 0.02
    tc = take_counter()
    tc.draw(lay, v, *L(930, HDR_Y), anchor=(1.0, 0.5), vel=vel, ndig=4)
    txt('TAKE', 'jw_mono', 34, ('ASH', 1.0)).draw(lay, *L(930 - take_width() - 18, HDR_Y), anchor=(1.0, 0.5))
    # storage row: full bar (FLAME -> RED); f735 -> solid RED pulsing + 'DISK FULL' chip replaces the readout
    sw = STO_X1 - STO_X0
    full = tb >= DISK_T
    if not full:
        bar_fill(lay, *L(STO_X0, STO_Y), sw, 12, 1.0, head=False)
        txt('2.00 / 2.00 TB', 'jw_mono', 34, ('IVORY', 0.86)).draw(lay, *L(930, STO_Y), anchor=(1.0, 0.5))
    else:
        pul = 0.75 + 0.25 * math.cos((tb - DISK_T) * 2 * math.pi * 2.0)
        bar_fill(lay, *L(STO_X0, STO_Y), sw, 12, 1.0, 'RED', 'RED', opacity=1.0, head=False)
        K.draw(lay, _red_glow(int(sw)), *L(STO_X0 + sw / 2, STO_Y), opacity=0.7 * pul, mode='add')
        kc = 0.7 + 0.3 * X.spring(t - DISK_T, 'POP')
        cw = ui.chip_size('DISK FULL', 34, 60, None, 26)[0]
        ui.place(lay, disk_chip_spr(), *L(930 - cw / 2, STO_Y), scale=kc,
                 opacity=K.ramp(t, DISK_T, DISK_T + F(2), 'out_cubic'))
    # card glass first (with frost from the plate), then the content layer
    pan.draw(cv, BIN_C[0], BIN_C[1], scale=k, opacity=op, face=face)
    gl = bin_glitch(t)
    if gl > 0:
        lay = _slice_glitch(lay, fidx(t), gl)
    K.draw(cv, lay, BIN_C[0], BIN_C[1], scale=k, opacity=op, anchor=((BIN_C[0] - ox) / lay.shape[1],
                                                                     (BIN_C[1] - oy) / lay.shape[0]))
    dm = bin_dim(t)
    if dm > 1e-3:
        K.draw(cv, rrect(BIN_W + 4, BIN_H + 4, 42, tuple(C('NIGHT_0')), 1.0), BIN_C[0], BIN_C[1], scale=k,
               opacity=dm * op)


@functools.lru_cache(maxsize=2)
def _red_glow(w):
    m = K.rrect_alpha(w, 12, 6.0, 30)
    return ro(K.glow(emissive(m, C('RED')), C('RED'), sigmas=(5, 14), strength=0.8, include=False))


def _slice_glitch(lay, k, g):
    rng = np.random.default_rng(735 + k)
    out = lay.copy()
    h = lay.shape[0]
    for _ in range(9):
        y0 = int(rng.uniform(0, h - 20))
        hh = int(rng.uniform(6, 40))
        dx = int(rng.uniform(-26, 26) * g)
        out[y0:y0 + hh] = np.roll(lay[y0:y0 + hh], dx, axis=1)
    return out


# ================================================================================================ S9 client toast
AV_C = (540.0, 1120.0)                            # = the C3 portal centre (r0 56)
AV_R = 56.0
TOAST_C = (540.0, 1250.0)
TOAST_W, TOAST_H = 760, 176
TOAST_T0 = F(795) - HALF
MSG_T = F(810) - HALF
TOAST_OUT = 899
MSG = 'Ek achha shot nahi hai.'


@functools.lru_cache(maxsize=1)
def avatar_spr():
    """SMOKE disc r 56, 4 px flame ring with glow, IVORY 'C' (Poppins SemiBold 54)."""
    r = AV_R
    disc = K.disc(r, C('SMOKE', 1.6))
    n = disc.shape[0]
    yy, xx = np.mgrid[0:n, 0:n].astype(np.float32)
    c = n / 2.0 - 0.5
    d = np.sqrt((xx - c) ** 2 + (yy - c) ** 2)
    shade = np.clip(1.15 - (yy - c + r) / (2 * r) * 0.5, 0.6, 1.2)
    disc[..., :3] *= shade[..., None]
    ringm = np.clip(2.0 + 0.5 - np.abs(d - (r - 2.0)), 0, 1)
    disc = disc * (1 - ringm[..., None]) + solid(ringm, C('FLAME', 1.5))
    spr = K.glow(disc, C('FLAME'), sigmas=(4, 12, 28), strength=0.55)
    pad = (spr.shape[0] - n) // 2
    spr = np.array(spr, copy=True)
    txt('C', 'jw_body', 54).draw(spr, pad + c + 0.5, pad + c + 1.5)
    return ro(spr)


@functools.lru_cache(maxsize=1)
def badge_spr():
    d = K.disc(11.0, C('RED', 1.3))
    return ro(K.glow(d, C('RED'), sigmas=(3, 9), strength=0.8))


@functools.lru_cache(maxsize=1)
def toast_panel():
    return glass(TOAST_W, TOAST_H, 40.0)


def _typing_dots(cv, t, cx, cy, s, op):
    spr = dot_spr(9, 'ASH', 1.0)
    for i in range(3):
        ph = ((t - 0.1 * i) / 0.4) % 1.0
        b = max(0.0, math.sin(2 * math.pi * ph))
        K.draw(cv, spr, cx + (i - 1) * 30 * s, cy - 9 * b * s, scale=s, opacity=op * (0.55 + 0.45 * b))


def toast(cv, t, opacity=1.0):
    """f795 the glass card POPs up (y +60 -> 0) with the avatar; 'Client' + typing dots until f809; f810 the dots
    collapse, '· abhi' appears and the message lands ("Ek achha shot nahi hai."), a red unread dot pops on the
    avatar and the card bumps once. Holds to f899 (the C3 portal opens through the avatar)."""
    if t < TOAST_T0 or t >= F(TOAST_OUT + 1):
        return
    dt = t - TOAST_T0
    sp = X.spring(dt, 'POP')
    k = 0.9 + 0.1 * sp
    k *= 1.0 + 0.035 * math.exp(-max(0.0, t - MSG_T) / 0.09) * (t >= MSG_T)
    dy = 60.0 * (1.0 - ease('out_cubic', dt / 0.3))
    op = K.ramp(t, TOAST_T0, TOAST_T0 + F(3), 'out_cubic') * opacity
    cx, cy = TOAST_C[0], TOAST_C[1] + dy

    def P(x, y):
        return cx + (x - TOAST_C[0]) * k, cy + (y - TOAST_C[1]) * k
    pan = toast_panel()
    face = pan.face_at(sweep=(dt * 0.5) % 1.0, sweep_gain=1.0 if t >= MSG_T else 0.6,
                       rim_gain=1.0 + 0.8 * math.exp(-max(0.0, t - MSG_T) / 0.2) * (t >= MSG_T))
    pan.draw(cv, cx, cy, scale=k, opacity=op, face=face)
    # header row: 'Client' (+ ' · abhi' from f810), centred as the final group
    nm = txt('Client', 'jw_body', 40)
    dot = txt('·', 'jw_body', 34, ('ASH', 1.0))
    ab = txt('abhi', 'jw_body', 34, ('ASH', 1.0))
    g1, g2 = 14.0, 12.0
    gw = nm.w + g1 + dot.w + g2 + ab.w
    hx, hy = P(TOAST_C[0] - gw / 2, TOAST_C[1] - 34)
    nm.draw(cv, hx, hy, anchor=(0, 0.5), scale=k, opacity=op)
    if t >= MSG_T:
        a = K.ramp(t, MSG_T, MSG_T + F(5), 'out_cubic')
        dot.draw(cv, hx + (nm.w + g1) * k, hy, anchor=(0, 0.5), scale=k, opacity=op * a)
        ab.draw(cv, hx + (nm.w + g1 + dot.w + g2) * k, hy, anchor=(0, 0.5), scale=k, opacity=op * a)
    # second row: typing dots -> message
    rx, ry = P(TOAST_C[0], TOAST_C[1] + 36)
    if t < MSG_T + F(3):
        a = 1.0 - K.ramp(t, MSG_T, MSG_T + F(3), 'in_cubic')
        _typing_dots(cv, t, rx, ry, k * (0.6 + 0.4 * a), op * a)
    if t >= MSG_T:
        u = K.ramp(t, MSG_T, MSG_T + 0.35, 'out_cubic')
        a = K.ramp(t, MSG_T, MSG_T + 0.2, 'out_cubic')
        txt(MSG, 'jw_body', 44).draw(cv, rx, ry + 14 * (1 - u) * k, scale=k * (0.96 + 0.04 * u), opacity=op * a,
                                     blur=4.0 * (1 - u))
    # avatar (portal centre) + unread dot
    ay = AV_C[1] + dy
    K.draw(cv, avatar_spr(), AV_C[0], ay, scale=0.85 + 0.15 * sp, opacity=op)
    if t >= MSG_T:
        kb = X.spring(t - MSG_T, 'POP')
        K.draw(cv, badge_spr(), AV_C[0] + 42, ay - 40, scale=max(0.0, kb), opacity=op)


# ================================================================================================ outro + cover
@functools.lru_cache(maxsize=1)
def outro():
    o = script()['outro']
    return PO.ProfileOutro(o['question'], key=o['key'], dur=4.0, scrim=OUTRO_SCRIM)


OUTRO_SCRIM = 0.75                               # PO default 0.62: the counter window sits behind the key line
OUTRO = dict(question=script()['outro']['question'], key=script()['outro']['key'], dur=4.0, t_end=T_END,
             dim=0.74, scrim=OUTRO_SCRIM)


@functools.lru_cache(maxsize=1)
def cover_title():
    return J.HouseTitle('SIRF', '36 shots', caps_px=110, key_px=250)


COVER_KEY_Y = 590.0


def cover(cv):
    """Cover overlay over the counter-at-36 still: SIRF / 36 shots lockup (caps ~y 386, keyword y 590, underline
    ~y 770) and @jawad_mp4 at y 1580; everything inside the 3:4 grid crop y 240-1680."""
    cover_title().draw(cv, 9.0, CX, COVER_KEY_Y, t0=0.0)
    J.signature(cv, CX, 1580, opacity=0.9)
    return cv


def cover_guides(cv):
    """Selftest only: the 3:4 grid crop rows and the counter window ring."""
    y0, y1 = GRID_CROP
    for y in (y0, y1):
        cv[int(y) - 1:int(y) + 2, :, :3] = C('AMBER', 0.9)
        cv[int(y) - 1:int(y) + 2, :, 3] = 1.0
    return cv


def grid_crop(u8):
    return u8[GRID_CROP[0]:GRID_CROP[1]]


# ================================================================================================ SRT
def _ts(s):
    ms = int(round(s * 1000))
    h, ms = divmod(ms, 3600000)
    m, ms = divmod(ms, 60000)
    sec, ms = divmod(ms, 1000)
    return '%02d:%02d:%02d,%03d' % (h, m, sec, ms)


def srt_text(hook='A'):
    S = script()
    lines = list(S['lines'])
    if hook == 'B':
        hb = [d for d in S['hooks'][1]['lines']]
        lines = [dict(id=d['id'], t_in=d['f_in'] / FPS, t_out=(d['f_out'] + 1) / FPS, roman=d['roman']) for d in hb] \
            + [d for d in lines if d['id'] not in ('C1', 'C2')]
    out = []
    for i, d in enumerate(lines):
        s = d['roman'].replace('*', '').strip()
        s = s[0].upper() + s[1:]
        out.append('%d\n%s --> %s\n%s\n' % (i + 1, _ts(d['t_in']), _ts(d['t_out']), s))
    o = S['outro']
    out.append('%d\n%s --> %s\n%s\n%s\n' % (len(lines) + 1, _ts(o['f_in'] / FPS + 1.3), _ts(DUR - 0.36),
                                           o['question'], o['key']))
    return '\n'.join(out)


def write_srt(path, hook='A'):
    with open(path, 'w', encoding='utf-8') as fh:
        fh.write(srt_text(hook))
    return path


# ================================================================================================ prewarm
def prewarm():
    for L in lockups().values():
        if isinstance(L, NumLockup):
            L.final
    for name in ('DIN 1', 'DIN 2', 'DIN 3'):
        day_spr(name, name == 'DIN 3')
    _chip_glow()
    hud_panel()
    hud_counter()
    take_counter()
    bin_panel()
    thumb_pool()
    tile_ring()
    tile_bar()
    _playhead()
    disk_chip_spr()
    toast_panel()
    avatar_spr()
    badge_spr()
    txt(MSG, 'jw_body', 44)
    outro()._settled_layer()
    cover_title()


# ================================================================================================ selftest
def _plate(name, pas, t):
    """A Blender plate from RWS/assets3d/<name>/<pass>/0000.png if the artist has rendered it, else a dark
    stand-in with the plate's practical so composition and contrast can still be judged."""
    p = os.path.join(RWS, 'assets3d', name, pas, '0000.png')
    if os.path.exists(p):
        spr = K.load_image(p)
        cv = np.zeros((K.H, K.W, 4), np.float32)
        cv[..., 3] = 1.0
        K.draw(cv, spr, K.CX, K.CY, scale=K.W / spr.shape[1])
        return cv
    cv = K.background(LOOK, t, bokeh=0.6)
    if name == 'counter_macro':                      # stand-in: the counter window
        K.draw(cv, ro(K.glow(K.ring(150, 6, C('ASH', 0.5)), C('FLAME', 0.4), sigmas=(10, 30), strength=0.4)),
               540, 1120)
        txt('36' if pas == 'tick15' else '35', 'jw_mono', 120, ('IVORY', 0.8)).draw(cv, 540, 1120)
        K.draw(cv, ro(K.glow(K.disc(10, C('FLAME', 2.0)), C('FLAME'), sigmas=(6, 18), strength=1.0)), 250, 1380)
    elif name == 'drives':                           # stand-in: dark desk, drive LEDs, monitor glow
        rng = np.random.default_rng(4)
        for i in range(4):
            y = 1050 + i * 120
            K.draw(cv, rrect(520, 96, 14, tuple(C('SMOKE', 1.2)), 1.0), 540 + rng.uniform(-12, 12), y)
            K.draw(cv, ro(K.glow(K.disc(4, C('FLAME', 2.0)), C('FLAME'), sigmas=(5, 14), strength=1.0)), 760, y)
    elif name == 'studio_counter':
        K.draw(cv, rrect(900, 1300, 20, tuple(hexl('#3A2416', 0.6)), 1.0), 540, 1100)
    return cv


def _grade(cv, t):
    return K.to_srgb8(G.finish(cv, LOOK, t), t)


def _sheet(imgs, cols, w=360, labels=None):
    h = int(round(w * imgs[0].shape[0] / imgs[0].shape[1]))
    rows = (len(imgs) + cols - 1) // cols
    out = np.zeros((rows * h, cols * w, 3), np.uint8)
    for i, im in enumerate(imgs):
        sm = cv2.resize(im, (w, h), interpolation=cv2.INTER_AREA)
        if labels:
            cv2.putText(sm, labels[i], (8, 22), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (120, 200, 255), 1, cv2.LINE_AA)
        r, c = divmod(i, cols)
        out[r * h:(r + 1) * h, c * w:(c + 1) * w] = sm
    return out


def _save(name, u8):
    os.makedirs(SELFTEST_DIR, exist_ok=True)
    p = os.path.join(SELFTEST_DIR, name)
    cv2.imwrite(p, u8[..., ::-1] if u8.shape[-1] == 3 else u8)
    return p


def _frame(t, world, *draws, samples=1, dim=None):
    """Average `samples` sub-frames over a half shutter (the renderer's motion blur) of world + draws."""
    acc = None
    for i in range(samples):
        tt = t + (i - (samples - 1) / 2.0) / max(1, samples) * (0.5 / FPS) if samples > 1 else t
        cv = world(tt).copy()
        for d in draws:
            d(cv, tt)
        acc = cv if acc is None else acc + cv
    acc /= samples
    acc[..., 3] = 1.0
    return np.ascontiguousarray(acc)


def selftest():
    import time
    out = []
    t_start = time.time()
    prewarm()
    print('prewarm %.1f s' % (time.time() - t_start))
    W_home = lambda tt: _plate('counter_macro', 'plate', tt)                     # noqa: E731
    W_desk = lambda tt: _plate('drives', 'plate', tt)                            # noqa: E731
    W_ctr = lambda tt: _plate('studio_counter', 'night', tt)                     # noqa: E731

    def W_bin(tt):
        cv = W_desk(tt)
        cv[..., :3] = cv2.GaussianBlur(cv[..., :3], (0, 0), 18) * 0.45
        return cv

    def at_settle(L):
        return F(L.f_out) - 0.35 if not isinstance(L, NumLockup) else F(L.f_out) - 0.1

    # 1. every lockup settled, on its world (sheets at phone-ish size)
    world_of = {'C11': W_desk, 'C12': W_desk, 'C13': W_bin, 'C14': W_bin, 'C15': W_bin, 'C10': W_desk, 'P': W_bin,
                'C6': W_ctr}
    imgs, labs = [], []
    for lid in ORDER_A + ('HB1', 'HB2'):
        L = lockup(lid)
        t = at_settle(L)
        cv = _frame(t, world_of.get(lid, W_home), lambda c, tt, L=L: L.draw(c, tt))
        imgs.append(_grade(cv, t))
        labs.append('%s f%d' % (lid, fidx(t)))
    for i in range(0, len(imgs), 6):
        out.append(_save('s36_lockups_%d.png' % (i // 6 + 1), _sheet(imgs[i:i + 6], 3, 360, labs[i:i + 6])))
    # full-res keyword checks (largest lockups)
    out.append(_save('s36_lockup_P_full.png', imgs[ORDER_A.index('P')]))
    out.append(_save('s36_lockup_C1_full.png', imgs[0]))
    # 2. kinetic strips: hook entry at f0, numbers, countdown, slam keys
    strips = {'C1': (0, 1, 3, 6, 10, 20), 'C11': (540, 541, 543, 546, 550, 560), 'C12': (570, 572, 575, 579, 583, 592),
              'C13': (600, 601, 603, 605, 608, 615), 'C16': (910, 914, 917, 920, 924, 935),
              'C8': (375, 376, 378, 381, 386, 400)}
    for lid, fr in strips.items():
        L = lockup(lid)
        ims = []
        for f in fr:
            t = F(f)
            cv = _frame(t, world_of.get(lid, W_home), lambda c, tt, L=L: L.draw(c, tt), samples=3)
            ims.append(_grade(cv, t))
        out.append(_save('s36_kinetic_%s.png' % lid, _sheet(ims, 6, 300, ['f%d' % f for f in fr])))
    # 3. S4 day chip with C6
    ims = []
    for f in (242, 257, 262, 275, 284):
        t = F(f)
        cv = _frame(t, W_ctr, lambda c, tt: lockup('C6').draw(c, tt), day_chip)
        ims.append(_grade(cv, t))
    out.append(_save('s36_day_chip.png', _sheet(ims, 5, 300, ['f242', 'f257', 'f262', 'f275', 'f284'])))
    # 4. S7 storage HUD with C11 / C12
    for f in (548, 590):
        t = F(f)
        cv = _frame(t, W_desk, lambda c, tt: captions(c, tt), storage_hud, samples=3)
        out.append(_save('s36_storage_hud_f%d.png' % f, _grade(cv, t)))
    # 5. S8 media bin
    for f in (612, 640, 700, 742, 790):
        t = F(f)
        cv = _frame(t, W_bin, media_bin, lambda c, tt: captions(c, tt), toast, samples=3)
        out.append(_save('s36_media_bin_f%d.png' % f, _grade(cv, t)))
    # 6. S9 payoff: frozen bin + toast + P
    for f in (803, 845):
        t = F(f)
        cv = _frame(t, W_bin, media_bin, toast, lambda c, tt: captions(c, tt))
        out.append(_save('s36_toast_f%d.png' % f, _grade(cv, t)))
    # 7. outro (profile badge allowed) over the dimmed counter world at 35
    o = outro()
    t = T_END + 2.6
    cv = _frame(t, W_home, lambda c, tt: o.draw(c, tt, T_END))
    out.append(_save('s36_outro.png', _grade(cv, t)))
    print('outro boxes', {k: tuple(int(v) for v in b) for k, b in o.boxes().items()}, 'q lines', len(o.q_lines))
    # 8. cover + 3:4 crop + 210 px check
    cv = _plate('counter_macro', 'tick15', 0.5)
    cover(cv)
    u8 = _grade(cv, 0.5)
    out.append(_save('s36_cover.png', u8))
    crop = grid_crop(u8)
    out.append(_save('s36_cover_grid_3x4.png', crop))
    sm = cv2.resize(crop, (210, 280), interpolation=cv2.INTER_AREA)
    out.append(_save('s36_cover_210.png', sm))
    # 9. thumbnail pool (no faces)
    pool = thumb_pool()
    sheet = np.zeros((192 * 4 + 50, 108 * 7 + 60, 4), np.float32)
    sheet[..., 3] = 1
    for i, s_ in enumerate(pool):
        r, c = divmod(i, 7)
        K.draw(sheet, s_, 10 + c * 116 + 54, 10 + r * 202 + 96)
    out.append(_save('s36_thumbs.png', K.to_srgb8(sheet)))
    # 10. phone-size read check: one frame per section at 360 px wide
    picks = [(0, W_home), (100, W_home), (300, W_ctr), (520, W_desk), (585, W_desk), (630, W_bin), (760, W_bin),
             (840, W_bin), (930, W_home)]
    ims = []
    for f, wfn in picks:
        t = F(f)
        dr = [lambda c, tt: captions(c, tt)]
        if 240 <= f < 300:
            dr.append(day_chip)
        if 540 <= f < 600:
            dr.append(storage_hud)
        if 600 <= f < 900:
            dr = [media_bin, toast] + dr
        cv = _frame(t, wfn, *dr)
        ims.append(_grade(cv, t))
    out.append(_save('s36_phone.png', _sheet(ims, 9, 240, ['f%d' % f for f, _ in picks])))
    # layout report
    for lid in ORDER_A + ('HB1', 'HB2'):
        b = lockup(lid).box()
        flag = '' if (b[0] >= 70 and b[2] <= 1010 and b[1] >= 230 and b[3] <= 1480) else '  <-- OUT OF SAFE ZONE'
        print('%-4s box x %4d-%4d y %4d-%4d%s' % (lid, b[0], b[2], b[1], b[3], flag))
    write_srt(os.path.join(SELFTEST_DIR, 'sirf_36_shots_A.srt'))
    for p in out:
        print('->', p)
    print('selftest %.1f s' % (time.time() - t_start))
    return out


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'selftest':
        selftest()
    elif len(sys.argv) > 1 and sys.argv[1] == 'srt':
        print(srt_text(sys.argv[2] if len(sys.argv) > 2 else 'A'))
    else:
        print(__doc__)
