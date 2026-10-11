"""thoda_left_bas_ui.py - type + glass UI of Bijli series #2 "Thoda Left... Bas Bas!" (UI/UX designer:
caption-designer + brand-kit-builder roles). Owner of every on-screen word and UI element of the reel; the motion
designer (thoda_left_bas.py / _world.py) calls these pure draw functions over the 3D worlds.

Sources: brand_reels/design/reels/thoda_left_bas/SCRIPT.md + script.json (words), SHOTS.md (frames, section c
UI/TYPE), BRIEF.md (signal grammar), pipeline/jawad_reels/BRAND.md (palette, type). Deviations: UI.md next to SHOTS.
Canvas convention: linear premultiplied float32 (H, W, 4), 1080 x 1920, t in seconds (f / 30). Every static sprite
is built once (lru_cache); every draw is a pure function of its arguments.

SIGNAL GRAMMAR (reference implementation of SHOTS 0; the world module may import it)
    yaw(t) -> antenna yaw deg       sig(t) -> 0 (locked) .. 1 (no signal)      gdir(t) -> +1 / -1 (ghost side)
    client(t) -> (title X, version, last move dir)                             sig_c(t) -> 0 / 1 (edit world)

CAPTIONS (SCRIPT 3; two voices: NEAR = big house lockup in the top band, FAR = small ASH caps rising from y 1480)
    captions(cv, t, sig=None, gdir=None, hook='A', m3_dx=None)    every caption active at t (sig / gdir default to
                                       the reference clocks); m3_dx(t) = C11's exit track (px, default slide left)
    near(cv, t, cid, sig=0, gdir=1)    one near / narrator lockup by SCRIPT id (H1 H1b H2 H3 HB1 R1 R4 C5 C6 C9 C10
                                       C11 C12 C13 C14 C15 P1)
    far(cv, t, cid)                    one far-voice line (R2 R3 C7 C8)
    CAPS                               the caption table (frames, parts, speed, exits) = script.json

CRT PICTURE (SHOTS c: 2D, warped by the world module through the A5 / A6 stmap)
    tv_card()                          1080 x 810 'SUNDAY KI FILM' card (static, linear RGB)
    tv_picture(t, sig, gdir=1, roll=None, shimmer=None, split=None) -> 810 x 1080 x 4 opaque linear picture with
                                       snow (15 fps), ghost, vertical roll, tearing, chroma drop, lock shimmer;
                                       split=0..1 = cover look (snow above the rolling tear, locked below)
    tv_picture_at(t)                   the same driven by the reference clocks (S1 / S3 / S5 / S13 + loop tail)

EDIT WORLD GLASS UI (S7 S9 S11; draw into a layer and tilt it with plane_warp for the 2.5D (4, -6, 0) plane)
    edit_ui(cv, t)                     viewer + timeline + toast + cursor + revision list + bubble + export by frame
    viewer(cv, t, X, ver, ...)  timeline(cv, t, dy=0)  toast(cv, t)  revisions(cv, t)  client_bubble(cv, t)
    export_dialog(cv, t)   cursor(cv, t)   plane_warp(layer, rx=4, ry=-6) -> tilted copy (perspective)
PHONE (S8)
    phone_screen(t) -> 1560 x 720 x 4 opaque chat screen for the A7 stmap    phone_mock(cv, t) 2D fallback phone
SMALL PIECES
    anachronism(cv, t, t0, t1, exit=None)  B0 (f63-71) / B1 (f990-1007) client bubble at (790, 300)
    hook_b(cv, t)                      S1B: viewer + bubble + nudge 540 -> 538 '-2 px' (+ snow_tear f62-f71)
    split_ui(cv, t)                    S10 TAB / AB: divider, chips, far words top, mini viewer + bubble bottom
OUTRO / COVER
    OUTRO, T_END, outro()              PO.ProfileOutro('Aap ke ghar antenna kaun ghumata tha?',
                                       key='Papa, bhai ya aap?', dur=4.2) at T_END = 882 / 30
    cover(cv)                          lockup + underline, BAS BAS!, bubble, signature over the cover CRT frame
    cover_picture()                    the half-snow / half-locked TV picture for the cover     GRID_CROP (y 240-1680)

    python3 thoda_left_bas_ui.py selftest   -> workspace/jawad_reels/thoda_left_bas/ui_selftest/*.png
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
import jawad_grade as G                           # noqa: E402,F401  registers 'gold_hour'
import jawad_tx as X                              # noqa: E402
import profile_outro as PO                        # noqa: E402

import cv2                                        # noqa: E402
import numpy as np                                # noqa: E402

LOOK = 'gold_hour'
FPS = K.FPS
HALF = 0.5 / FPS
W, H = K.W, K.H
DUR = 1008 / 30
REPO = os.path.abspath(os.path.join(HERE, '..', '..'))
RWS = os.path.join(K.WS, 'thoda_left_bas')
SELF_DIR = os.path.join(RWS, 'ui_selftest')
SCRIPT_JSON = os.path.join(REPO, 'brand_reels', 'design', 'reels', 'thoda_left_bas', 'script.json')
ASSETS3D = os.path.join(RWS, 'assets3d')


# ============================================================================================== helpers
def F(f):
    return f / FPS


def fi(t):
    return int(math.floor(t * FPS + 0.5))


def ease(name, u):
    return K.EASE[name](min(1.0, max(0.0, u)))


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


def over(dst, src):
    a = src[..., 3:4]
    dst *= (1.0 - a)
    dst += src
    return dst


@functools.lru_cache(maxsize=1024)
def tx(s, style, px, fill=None):
    if fill is None:
        return T.render(s, style, px=px)
    return T.render(s, style, px=px, fill=fill)


def text(cv, s, style, px, x, y, anchor=(0.5, 0.5), opacity=1.0, fill=None, **kw):
    if opacity <= 1e-4 or not s:
        return
    tx(s, style, px, fill).draw(cv, x, y, anchor=anchor, opacity=opacity, **kw)


@functools.lru_cache(maxsize=512)
def utext(s, size, fnt='ui', color='IVORY'):
    """Crisp UI text sprite (PIL, kerned) -> (sprite, ox, oy, adv) with (ox, oy) = baseline origin."""
    t = ui.text(s, size, fnt, color)
    return t


def uput(cv, s, size, x, y, fnt='ui', color='IVORY', anchor='ls', opacity=1.0, scale=1.0):
    """UI text at (x, y) with ui anchors ('ls', 'lm', 'mm', 'rm', 'rs' ...); sub-pixel when scale != 1."""
    if not s or opacity <= 1e-4:
        return
    t = utext(s, float(size), fnt, color)
    x0, y0 = t.topleft(0, 0, anchor)
    if abs(scale - 1.0) < 1e-6:
        ui.paste(cv, t.spr, round(x + x0), round(y + y0), opacity)
    else:
        K.draw(cv, t.spr, x + x0 * scale, y + y0 * scale, scale=scale, anchor=(0, 0), opacity=opacity)


def uwidth(s, size, fnt='ui'):
    return ui.measure(s, float(size), fnt)


@functools.lru_cache(maxsize=64)
def glass(w, h, r=32.0, rim=1.0, glow=1.0, shadow=1.0, tint=None, tint_a=None, rim_angle=-55.0):
    kw = {}
    if tint is not None:
        kw['tint'] = tint
    if tint_a is not None:
        kw['tint_a'] = tint_a
    return ui.glass_card(int(round(w)), int(round(h)), r=float(r), look=LOOK, rim=rim, glow=glow, shadow=shadow,
                         rim_angle=rim_angle, **kw)


def aa_line(cv, p0, p1, width, col, opacity=1.0):
    """Anti-aliased segment (premultiplied over)."""
    x0, y0 = p0
    x1, y1 = p1
    m = width + 2
    X0, Y0 = int(max(0, math.floor(min(x0, x1) - m))), int(max(0, math.floor(min(y0, y1) - m)))
    X1, Y1 = int(min(cv.shape[1], math.ceil(max(x0, x1) + m))), int(min(cv.shape[0], math.ceil(max(y0, y1) + m)))
    if X1 <= X0 or Y1 <= Y0:
        return
    yy, xx = np.mgrid[Y0:Y1, X0:X1].astype(np.float32) + 0.5
    dx, dy = x1 - x0, y1 - y0
    L2 = dx * dx + dy * dy
    if L2 < 1e-6:
        return
    u = np.clip(((xx - x0) * dx + (yy - y0) * dy) / L2, 0, 1)
    d = np.sqrt((xx - x0 - u * dx) ** 2 + (yy - y0 - u * dy) ** 2)
    a = np.clip(width / 2 + 0.5 - d, 0, 1) * np.float32(opacity)
    reg = cv[Y0:Y1, X0:X1]
    reg *= 1 - a[..., None]
    reg[..., :3] += a[..., None] * np.asarray(col, np.float32)
    reg[..., 3] += a


@functools.lru_cache(maxsize=32)
def soft_scrim(w, h, feather=80):
    """Elliptical-rounded SMOKE gradient (alpha <= 1) of body w x h with a feather: the type scrim of SHOTS c."""
    pad = feather
    a = K.rrect_alpha(int(w), int(h), min(w, h) / 2.0, pad)
    a = cv2.GaussianBlur(a, (0, 0), feather / 2.2)
    return ro(solid(a, hexl('#120806')))


def scrim(cv, cx, cy, w, h, amount=0.55, feather=80):
    if amount <= 1e-3:
        return
    K.draw(cv, soft_scrim(int(w), int(h), int(feather)), cx, cy, opacity=amount)


# ============================================================================================== signal grammar
YAW0 = -14.0
# (f_start, f_end, target yaw, ease): the value eases from the previous target to `target` over [f_start, f_end]
YAW_SEGS = [(6, 16, 9.0, 'inout_cubic'), (28, 36, 0.0, 'out_back'), (60, 66, -18.0, 'in_cubic'),
            (108, 113, -25.0, 'inout_cubic'), (118, 126, -32.0, 'inout_cubic'), (180, 197, -14.0, 'inout_cubic'),
            (198, 213, 6.0, 'inout_cubic'), (225, 240, -4.0, 'inout_cubic'), (252, 256, -3.0, 'out_cubic'),
            (261, 265, -2.0, 'out_cubic'), (270, 274, -1.0, 'out_cubic'), (279, 283, -0.5, 'out_cubic'),
            (288, 292, 0.0, 'out_cubic'), (346, 358, 11.0, 'in_cubic'), (414, 431, -40.0, 'in_expo'),
            (576, 582, -6.0, 'inout_cubic'), (594, 600, 4.0, 'inout_cubic'), (612, 618, -6.0, 'inout_cubic'),
            (630, 636, -1.0, 'inout_cubic'), (719, 720, 0.0, 'linear'), (828, 833, 2.0, 'out_cubic')]
WOBBLE = [(-1e9, 5.99, 1.5, 1.3), (66, 107, 1.0, 1.3), (342, 413, 3.0, 0.8)]       # (f0, f1, amp deg, hz)


def _yaw_f(f):
    if f >= 864 or f < 0:                                 # loop tail: frame 0's past (the pre-roll state)
        return YAW0 + 1.5 * math.sin(2 * math.pi * 1.3 * ((f - 1008 if f >= 864 else f) / FPS))
    v = YAW0
    for f0, f1, tgt, e in YAW_SEGS:
        if f < f0:
            break
        u = 1.0 if f1 <= f0 else (f - f0) / float(f1 - f0)
        v = v + (tgt - v) * ease(e, u) if u < 1 else tgt
    for f0, f1, a, hz in WOBBLE:
        if f0 <= f <= f1:
            v += a * math.sin(2 * math.pi * hz * f / FPS)
    return v


def yaw(t):
    return _yaw_f(t * FPS)


def _raw_sig(f):
    y = _yaw_f(f)
    return 0.0 if abs(y) < 0.75 else min(1.0, abs(y) / 12.0)


def sig(t):
    """0 = locked .. 1 = no signal; smoothed over 3 f on the way up, instant on a lock (SHOTS 0)."""
    f = t * FPS
    r = _raw_sig(f)
    if r == 0.0:
        return 0.0
    return (r + _raw_sig(f - 1) + _raw_sig(f - 2)) / 3.0


def gdir(t):
    return 1.0 if yaw(t) >= 0 else -1.0


# client clock (SHOTS 0): title X in the viewer and the version on screen
CLIENT = [(432, 540, 1), (477, 538, 2), (495, 540, 3), (509, 538, 4), (522, 541, 5), (531, 539, None),
          (540, 538, None), (549, 540, None), (558, 537, None), (567, 539, None), (576, 538, 23), (594, 541, 24),
          (612, 538, 25), (630, 539, 26), (648, 538, 27)]


def client(t):
    """(X float, version int, last move direction) at t."""
    f = t * FPS
    xv, ver, prev, dirn = 540.0, 1, 540.0, -1.0
    for k, (f0, xx, vv) in enumerate(CLIENT):
        if f < f0 - 0.5:
            break
        u = ease('out_cubic', (f - f0 + 0.5) / 3.0)
        prev_x = CLIENT[k - 1][1] if k else 540
        xv = prev_x + (xx - prev_x) * u
        if xx != prev_x:
            dirn = 1.0 if xx > prev_x else -1.0
        if vv is not None:
            ver = vv
    if 522 <= f < 576:
        ver = min(22, 5 + int((f - 522) // 3))
    return xv, ver, dirn


def sig_c(t):
    return 1.0 if F(468) - HALF <= t < F(648) - HALF else 0.0


# version names for the revision list (L1) and the export (E1)
def vname(v):
    if v == 27:
        return 'v27_final_FINAL.mp4'
    suf = ''
    if 10 <= v <= 13:
        suf = '_final'
    elif 14 <= v <= 16:
        suf = '_final2'
    elif 17 <= v <= 19:
        suf = '_FINAL'
    elif 20 <= v <= 22:
        suf = '_final_v2'
    elif v in (23, 24, 26):
        suf = '_final_final'
    elif v == 25:
        suf = '_FINAL_final'
    return 'trailer_v%d%s.mp4' % (v, suf)


def vx(v):
    """X readout stored with each version (v2 and v27 both 538: the easter egg)."""
    table = {1: 540, 2: 538, 3: 540, 4: 538, 23: 538, 24: 541, 25: 538, 26: 539, 27: 538}
    if v in table:
        return table[v]
    jit = [541, 539, 538, 540, 537, 539]
    return jit[(v - 5) % 6] if v != 22 else 539


# ============================================================================================== captions
SPEED = {   # caps rise (y_dur, op_dur, dist) | keyword (delay, glyph dur, stagger, dist em, blur)
    'std': dict(cy=0.60, co=0.42, cd=28.0, kt=0.22, kd=0.50, ks=0.030, kdist=0.30, kb=7.0),
    'fast': dict(cy=0.36, co=0.22, cd=22.0, kt=0.05, kd=0.32, ks=0.018, kdist=0.24, kb=6.0),
    'hook': dict(cy=0.24, co=0.13, cd=18.0, kt=0.00, kd=0.22, ks=0.012, kdist=0.20, kb=5.0),
}

# part = (kind, text, style, px, x, y, t0 offset s) ; kind caps | key | body | slam
CAPS = {
    'H1': dict(f=(0, 17), t0=F(0) - 0.25, speed='hook', ghost=True, out=None,
               parts=[('caps', 'THODA', 'jw_caps', 96, 540, 360, 0.0), ('key', 'left...', 'jw_key', 240, 540, 535, 0.0)]),
    'H2': dict(f=(36, 53), t0=F(36), speed='hook', out=(50, 54),
               parts=[('slam', 'BAS BAS!', 'jw_caps_bold', 170, 540, 470, 0.0)]),
    'H3': dict(f=(54, 71), t0=F(54), speed='hook', ghost=True, out=(63, 72), tear=True,
               parts=[('caps', 'AB', 'jw_caps', 96, 540, 330, 0.0), ('key', 'theek hai!', 'jw_key', 220, 540, 500, 0.0)]),
    'HB1': dict(f=(0, 71), t0=-0.45, speed='std', out=(62, 72), tear=True,
                parts=[('caps', 'YEH FEEDBACK', 'jw_caps', 96, 540, 330, 0.0),
                       ('key', 'suna suna', 'jw_key', 200, 540, 495, 0.0),
                       ('body', 'lagta hai?', 'jw_body', 72, 540, 650, 0.70)]),
    'R1': dict(f=(72, 98), t0=F(72), speed='fast', out=(94, 99),
               parts=[('key', 'Aaya?', 'jw_key', 230, 540, 470, 0.0)]),
    'R4': dict(f=(162, 197), t0=F(162), speed='fast', out=(193, 198),
               parts=[('slamkey', 'kiska', 'jw_key', 230, 450, 480, 0.0),
                      ('pop', 'left?!', 'jw_body', 72, 790, 520, F(6))]),
    'C5': dict(f=(198, 224), t0=F(198), speed='fast', ghost=True, out=(220, 225),
               parts=[('caps', 'THODA', 'jw_caps', 96, 540, 330, 0.0), ('key', 'aur...', 'jw_key', 230, 540, 500, 0.0)]),
    'C6': dict(f=(225, 251), t0=F(225), speed='fast', ghost=True, out=(247, 252), jolt=225,
               parts=[('caps', 'NAHI NAHI,', 'jw_caps', 96, 540, 330, 0.0),
                      ('key', 'wapas!', 'jw_key', 240, 540, 505, 0.0)]),
    'C9': dict(f=(306, 341), t0=F(306), speed='fast', out=(338, 342),
               parts=[('caps', 'AB', 'jw_caps', 96, 540, 330, 0.0), ('key', 'theek hai!', 'jw_key', 220, 540, 500, 0.0)]),
    'C10': dict(f=(351, 377), t0=F(351), speed='fast', ghost=True, out=(373, 378),
                parts=[('caps', 'ARRE,', 'jw_caps', 96, 540, 330, 0.0),
                       ('key', 'phir se?!', 'jw_key', 230, 540, 500, 0.0)]),
    'C11': dict(f=(378, 431), t0=F(378), speed='std', out=None, m3=True,
                parts=[('caps', 'YEH SCENE', 'jw_caps', 96, 540, 380, 0.0), ('key', 'khatam', 'jw_key', 240, 540, 550, 0.0),
                       ('body', 'nahi hua...', 'jw_body', 72, 540, 705, F(18))]),
    'C12': dict(f=(432, 467), t0=F(436), speed='std', out=(462, 468),
                parts=[('caps', '20 SAAL BAAD', 'jw_caps', 96, 540, 300, 0.0)]),
    'C13': dict(f=(540, 575), t0=F(540), speed='fast', out=(571, 576), scrim=(540, 420, 900, 330),
                parts=[('caps', 'DIALOGUE', 'jw_caps', 96, 540, 300, 0.0), ('key', 'wahi', 'jw_key', 250, 480, 470, 0.0),
                       ('pop', 'hai.', 'jw_body', 72, 790, 505, F(12))]),
    'C14': dict(f=(648, 683), t0=F(648), speed='hook', out=(679, 684), scrim=(540, 420, 960, 220),
                parts=[('slam', 'BAS BAS!', 'jw_caps_bold', 170, 540, 420, 0.0)]),
    'C15': dict(f=(684, 719), t0=F(684), speed='fast', out=(712, 720), scrim=(540, 450, 860, 420),
                parts=[('caps', '27', 'jw_caps', 96, 540, 300, 0.0), ('key', 'revision', 'jw_key', 220, 540, 460, 0.0),
                       ('body', 'baad...', 'jw_body', 72, 540, 600, F(12))]),
    'P1': dict(f=(756, 863), t0=F(756), speed='std', out=(846, 857), underline=True,
               parts=[('caps', 'HUM AAJ BHI', 'jw_caps', 96, 540, 380, 0.0), ('key', 'antenna', 'jw_key', 250, 540, 560, 0.0),
                      ('body', 'ghuma rahe hain.', 'jw_body', 72, 540, 770, F(24))]),
}
CAPS['C9']['crisp'] = True

# far voice lines: (text, style, px, y_end, fill, f_in, f_out, words?)
FAR = {
    'R2': dict(text='NAHI! THODA LEFT...', style='jw_caps', px=64, y=1420, fill='ASH', f=(99, 134)),
    'R3': dict(text='ULTA! DOOSRA LEFT!', style='jw_caps', px=64, y=1420, fill='ASH', f=(135, 161)),
    'C7': dict(text='HAAN... HAAN...', style='jw_caps', px=64, y=1420, fill='ASH', f=(252, 287),
               words=[('HAAN...', 252), ('HAAN...', 270)]),
    'C8': dict(text='BAS! BAS!', style='jw_caps_bold', px=110, y=1390, fill='IVORY', f=(288, 305), slam=True),
}


@functools.lru_cache(maxsize=64)
def glyphs(s, style, px):
    return T.Glyphs(s, style, px=px)


def _part_box(kind, s, style, px):
    st = 'jw_key_core' if kind in ('key', 'slamkey') else style
    w, h = T.measure(s, st, px=px)
    return w, h


def _rise(t, t0, sp):
    uy = ease('out_cubic', (t - t0) / sp['cy'])
    op = ease('inout_sine', (t - t0) / sp['co'])
    return uy, op


def _draw_part(L, t, part, t0, sp, oy, crisp):
    """One lockup part into layer L (band coords: y - oy). Returns nothing."""
    kind, s, style, px, x, y, dt = part
    ts = t0 + dt
    y = y - oy
    if t < ts - HALF:
        return
    if kind in ('caps', 'body'):
        uy, op = _rise(t, ts, sp)
        tx(s, style, px).draw(L, x, y + sp['cd'] * (1.0 - uy), opacity=op, blur=6.0 * (1.0 - uy), snap=uy >= 1)
    elif kind == 'pop':
        k = 0.82 + 0.18 * X.spring(max(0.0, t - ts), 'POP')
        op = ease('out_cubic', (t - ts + HALF) / F(3))
        tx(s, style, px).draw(L, x, y, opacity=op, scale=k, snap=False)
    elif kind == 'key':
        tk = ts + sp['kt']
        if t < tk - HALF:
            return
        hk = ease('inout_sine', (t - tk) / (sp['kd'] + 0.03 * len(s)))
        tx(s, 'jw_key_halo', px).draw(L, x, y, opacity=hk)
        settle = tk + sp['ks'] * len(s) + sp['kd'] + 0.05
        if crisp is False and t < settle:
            glyphs(s, 'jw_key_core', px).rise(L, t, x, y, t0=tk, stagger=sp['ks'], dur=sp['kd'], dist=sp['kdist'],
                                              blur=sp['kb'], scale0=0.94)
        else:
            tx(s, 'jw_key_core', px).draw(L, x, y)
    elif kind == 'slam':
        if t < ts + 0.5:
            glyphs(s, style, px).slam(L, t, x, y, t0=ts - HALF, fade=0, s0=1.14, dur=0.25, smear=False)
        else:
            tx(s, style, px).draw(L, x, y)
    elif kind == 'slamkey':
        tx(s, 'jw_key_halo', px).draw(L, x, y, opacity=ease('out_cubic', (t - ts) / 0.25))
        if t < ts + 0.5:
            glyphs(s, 'jw_key_core', px).slam(L, t, x, y, t0=ts - HALF, fade=0, s0=1.18, dur=0.4, smear=False)
        else:
            tx(s, 'jw_key_core', px).draw(L, x, y)


def _band(parts):
    """Vertical band (y0, y1) that holds every part with its glow (halo ~0.8 em)."""
    y0, y1 = 1e9, -1e9
    for kind, s, style, px, x, y, dt in parts:
        w, h = _part_box(kind, s, style, px)
        g = px * (0.95 if kind in ('key', 'slamkey') else 0.45) + 30
        y0, y1 = min(y0, y - h / 2 - g), max(y1, y + h / 2 + g)
    return int(max(0, math.floor(y0))), int(min(H, math.ceil(y1)))


def _rng(f, salt=0):
    return np.random.default_rng((int(f) * 7919 + salt * 104729) & 0x7FFFFFFF)


def _bands_shift(L, f, n, hgt, amp, salt=0, rows=None):
    """Shift n random horizontal bands (hgt px) of layer L by up to +-amp px (in place)."""
    if amp < 0.5:
        return
    rng = _rng(f, salt)
    r0, r1 = rows if rows is not None else (0, L.shape[0])
    for _ in range(n):
        h = int(hgt if np.isscalar(hgt) else rng.integers(hgt[0], hgt[1]))
        y = int(rng.integers(r0, max(r0 + 1, r1 - h)))
        dx = int(round(rng.uniform(-amp, amp)))
        if dx:
            L[y:y + h] = np.roll(L[y:y + h], dx, axis=1)
            if dx > 0:
                L[y:y + h, :dx] = 0
            else:
                L[y:y + h, dx:] = 0


@functools.lru_cache(maxsize=64)
def _auto_scrim(cid):
    """Soft SMOKE scrim rect (cx, cy, w, h) behind a lockup: the type stays >= 4.5:1 over a bright sky, the CRT
    glass or the UI (SHOTS c)."""
    x0, y0, x1, y1 = 1e9, 1e9, -1e9, -1e9
    for kind, s, style, px, x, y, dt in CAPS[cid]['parts']:
        w, h = _part_box(kind, s, style, px)
        x0, x1 = min(x0, x - w / 2), max(x1, x + w / 2)
        y0, y1 = min(y0, y - h / 2), max(y1, y + h / 2)
    return ((x0 + x1) / 2, (y0 + y1) / 2, min(1000, x1 - x0 + 120), y1 - y0 + 40)


def near(cv, t, cid, sig_v=0.0, gdir_v=1.0, dx=0.0, opacity=1.0, scrim_k=0.5):
    """Draw near / narrator lockup `cid` at t (nothing outside its frames)."""
    c = CAPS[cid]
    f = t * FPS
    f_in, f_out = c['f']
    out = c.get('out')
    f_end = out[1] if out else f_out + 1
    if f < f_in - 0.5 or f >= f_end - 0.5:
        return
    sp = SPEED[c['speed']]
    parts = c['parts']
    y0, y1 = _band(parts)
    L = np.zeros((y1 - y0, W, 4), np.float32)
    Lk = np.zeros_like(L) if c.get('ghost') else L
    crisp = bool(c.get('crisp'))
    for p in parts:
        _draw_part(Lk if p[0] in ('key', 'slamkey') else L, t, p, c['t0'], sp, y0, crisp)
    # underline (P1 + cover only): draws on after the keyword, from under its left end
    if c.get('underline'):
        kp = [p for p in parts if p[0] == 'key'][0]
        kw, kh = _part_box('key', kp[1], kp[2], kp[3])
        uln = int(min(980, kw * 1.08 + 40))
        ul = J.underline(uln, thick=max(4.0, kp[3] * 0.026))
        u = ease('inout_cubic', (t - (c['t0'] + 0.55)) / 0.7)
        if u > 0:
            ul.draw(L, kp[4] - uln / 2, kp[5] - y0 + kh / 2 + kp[3] * 0.13, u=u)
    # signal ghost-double on the keyword (SHOTS c): 0.35 sig opacity, 40 sig px toward the yaw side
    ex = 0.0
    if out:
        ex = ease('in_cubic', (f - out[0]) / max(1.0, out[1] - 1 - out[0]))
    s_eff = sig_v
    if c.get('tear') and ex > 0:
        s_eff = max(sig_v, ex)
    if Lk is not L:
        if s_eff > 0.5:
            kp = [p for p in parts if p[0] == 'key'][0]
            kw, kh = _part_box('key', kp[1], kp[2], kp[3])
            ky = int(kp[5] - y0)
            _bands_shift(Lk, f // 1, 3, 12, 9.0 * s_eff, salt=3, rows=(int(ky - kh / 2), int(ky + kh / 2)))
        if s_eff > 0.02:
            g = np.roll(Lk, int(round(40.0 * s_eff * gdir_v)), axis=1)
            over(L, g * np.float32(0.35 * s_eff))
        over(L, Lk)
    if c.get('tear') and ex > 0:                      # H3 / HB1: the lockup tears out with the signal
        _bands_shift(L, f // 1, 7, (10, 46), 40.0 * ex, salt=11)
    # jolt (C6 f225), M3 exit (C11), generic exit
    jx = 0.0
    if c.get('jolt') is not None and int(round(f)) == c['jolt']:
        jx = 12.0
    mdx = 0.0
    if c.get('m3'):
        mdx = -760.0 * ease('in_expo', (f - 414) / 17.0)
    oy = -8.0 * ex if not c.get('tear') else 0.0
    op = opacity * (1.0 - ex)
    if op <= 1e-3:
        return
    sc = c.get('scrim') or _auto_scrim(cid)
    if sc and scrim_k > 0:
        scrim(cv, sc[0] + dx + mdx, sc[1], sc[2], sc[3], (0.55 if c.get('scrim') else scrim_k) * op)
    blur = 6.0 * ex if not c.get('tear') else 0.0
    if c.get('m3') and mdx < -1:
        blur = min(14.0, abs(mdx) / 40.0)
    if blur > 0.3 or abs(dx + mdx + jx) > 1e-3 or abs(oy) > 1e-3 or op < 1:
        K.draw(cv, L, dx + mdx + jx, y0 + oy, anchor=(0, 0), opacity=op, blur=blur)
    else:
        ui.paste(cv, L, 0, y0)


def hook_chant(cv, t, sig_v, gdir_v):
    """H1 -> H1b (f0-f37): THODA stays; 'left...' slides out right, 'right...' enters from the left (SCRIPT anim)."""
    f = t * FPS
    if f >= 37.5:
        return
    c = CAPS['H1']
    sp = SPEED['hook']
    y0, y1 = _band(c['parts'] + [('key', 'right...', 'jw_key', 240, 540, 535, 0.0)])
    L = np.zeros((y1 - y0, W, 4), np.float32)
    Lk = np.zeros_like(L)
    ex = ease('in_cubic', (f - 33) / 4.0)              # out f33-f37
    _draw_part(L, t, c['parts'][0], c['t0'], sp, y0, False)
    # keyword A: 'left...' until f20 (slides 60 px right + fades f16-f20)
    if f < 20.5:
        u = ease('in_cubic', (f - 16) / 4.0)
        tmp = np.zeros_like(L)
        _draw_part(tmp, t, c['parts'][1], c['t0'], sp, y0, False)
        over(Lk, np.roll(tmp, int(round(60 * u)), axis=1) * np.float32(1.0 - u))
    if f >= 17.5:
        u = ease('out_cubic', (f - 18 + 0.5) / 6.0)
        tmp = np.zeros_like(L)
        tx('right...', 'jw_key_halo', 240).draw(tmp, 540 - 60 * (1 - u), 535 - y0, opacity=u)
        tx('right...', 'jw_key_core', 240).draw(tmp, 540 - 60 * (1 - u), 535 - y0, opacity=u, blur=5 * (1 - u))
        over(Lk, tmp)
    if sig_v > 0.5:
        kw, kh = _part_box('key', 'right...', 'jw_key', 240)
        _bands_shift(Lk, f // 1, 3, 12, 9.0 * sig_v, salt=3, rows=(int(535 - y0 - kh / 2), int(535 - y0 + kh / 2)))
    if sig_v > 0.02:
        over(L, np.roll(Lk, int(round(40.0 * sig_v * gdir_v)), axis=1) * np.float32(0.35 * sig_v))
    over(L, Lk)
    K.draw(cv, L, 0, y0 - 8 * ex, anchor=(0, 0), opacity=1.0 - ex, blur=6 * ex)


def _far_line(cv, t, spr, x, y_end, t0, f_out, slam=False, anchor=(0.5, 0.5), echo=True, fill_k=1.0):
    """A far-voice piece (+ two echoes: +10 f / +20 f, 14 px higher each, 0.35 / 0.15)."""
    ex = ease('in_cubic', (t * FPS - (f_out - 4)) / 5.0)
    if ex >= 1:
        return
    copies = [(0.0, 0.0, 1.0)]
    if echo:
        copies += [(F(10), -14.0, 0.35), (F(20), -28.0, 0.15)]
    for dl, dy, a in reversed(copies):
        tt = t - t0 - dl
        if tt < -HALF:
            continue
        if slam:
            y = 1480.0 + (y_end - 1480.0) * X.spring(max(0.0, tt), 'SLAM')
            op = ease('out_cubic', (tt + HALF) / F(3))
        else:
            u = ease('out_cubic', (tt + HALF) / F(10))
            y = 1480.0 + (y_end - 1480.0) * u
            op = ease('inout_sine', (tt + HALF) / F(5))
        o = op * a * (1.0 - ex) * fill_k
        if o > 1e-3:
            spr.draw(cv, x, y + dy - 6 * ex, anchor=anchor, opacity=o, blur=(1.5 if dl else 0.0) + 4 * ex, snap=False)


def far(cv, t, cid, scrim_k=0.5):
    d = FAR[cid]
    f = t * FPS
    f_in, f_out = d['f']
    if f < f_in - 0.5 or f >= f_out + 1.5:
        return
    spr = tx(d['text'], d['style'], d['px'], d['fill'])
    ex = ease('in_cubic', (f - (f_out - 4)) / 5.0)
    scrim(cv, 540, d['y'] - 10, spr.w + 140, spr.h + 70, scrim_k * (1 - ex) * ease('out_cubic', (f - f_in + 1) / 6))
    if d.get('words'):
        x0 = 540 - spr.w / 2
        sp_w = spr.w - T.measure(d['words'][-1][0], d['style'], px=d['px'])[0]
        for k, (w_, fw) in enumerate(d['words']):
            ws = tx(w_, d['style'], d['px'], d['fill'])
            _far_line(cv, t, ws, x0 + k * sp_w, d['y'], F(fw), f_out, anchor=(0.0, 0.5))
        return
    _far_line(cv, t, spr, 540, d['y'], F(f_in), f_out, slam=d.get('slam', False))


def captions(cv, t, sig_v=None, gdir_v=None, hook='A', scrim_k=0.5):
    """Every caption of the reel at t (house lockups + far voice). sig_v / gdir_v default to the reference clocks."""
    s = sig(t) if sig_v is None else sig_v
    g = gdir(t) if gdir_v is None else gdir_v
    f = t * FPS
    if f < 72:
        if hook == 'B':
            near(cv, t, 'HB1', scrim_k=scrim_k)
        else:
            if f < 37.5 and scrim_k > 0:
                scrim(cv, *_auto_scrim('H1'), amount=scrim_k * (1 - ease('in_cubic', (f - 33) / 4.0)))
            hook_chant(cv, t, s, g)
            near(cv, t, 'H2', scrim_k=scrim_k)
            near(cv, t, 'H3', s, g, scrim_k=scrim_k)
        return
    for cid in ('R1', 'R4', 'C5', 'C6', 'C9', 'C10', 'C11', 'C12', 'C13', 'C14', 'C15', 'P1'):
        a, b = CAPS[cid]['f']
        out = CAPS[cid].get('out')
        if a - 1 <= f <= (out[1] if out else b + 1):
            near(cv, t, cid, s if CAPS[cid].get('ghost') else 0.0, g, scrim_k=scrim_k)
    for cid in FAR:
        far(cv, t, cid)


# ============================================================================================== CRT picture
PIC_W, PIC_H = 1080, 810
SNOW = hexl('#F4DCC0')


@functools.lru_cache(maxsize=1)
def tv_card():
    """'SUNDAY KI FILM' card (SHOTS c): NIGHT_1 -> PLUM gradient, title, AMBER rule, 40 %-desaturated 7-bar strip,
    vignette, 1 px scanlines. Linear RGB (810, 1080, 3), emissive values (screen light)."""
    h, w = PIC_H, PIC_W
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    v = (yy / h)[..., None]
    top, bot = C('NIGHT_1') * 1.6 + hexl('#3A1A0E') * 0.4, C('PLUM') * 1.25
    img = top * (1 - v) + bot * v
    # soft centre bloom behind the title (studio card lighting)
    r2 = ((xx - w / 2) / (w * 0.42)) ** 2 + ((yy - h * 0.43) / (h * 0.30)) ** 2
    img += np.exp(-r2 * 1.6)[..., None] * (hexl('#7A2E12') * 0.55)
    # ornament: a thin double frame (old broadcast card)
    lay = np.zeros((h, w, 4), np.float32)
    S = ui.Surf(w, h, lay)
    S.stroke_rrect(70, 60, w - 140, h - 200, 22, 2.0, C('AMBER', 0.55), 0.85)
    S.stroke_rrect(82, 72, w - 164, h - 224, 16, 1.0, C('AMBER', 0.35), 0.7)
    img = img * (1 - lay[..., 3:4]) + lay[..., :3]
    t_ = T.render('SUNDAY KI FILM', 'jw_caps_bold', px=90, fill='IVORY')
    lay = np.zeros((h, w, 4), np.float32)
    t_.draw(lay, w / 2, h * 0.43)
    img = img * (1 - lay[..., 3:4]) + lay[..., :3]
    # AMBER rule + two small diamonds
    lay = np.zeros((h, w, 4), np.float32)
    S = ui.Surf(w, h, lay)
    ry = int(h * 0.43 + 78)
    S.rrect(w / 2 - 300, ry - 2, 600, 4, 2, C('AMBER', 1.1), 1.0)
    for dxd in (-330, 330):
        pts = np.array([[w / 2 + dxd, ry - 9], [w / 2 + dxd + 9, ry], [w / 2 + dxd, ry + 9], [w / 2 + dxd - 9, ry]],
                       np.float32)
        m = np.zeros((h, w), np.uint8)
        cv2.fillPoly(m, [np.round(pts * 16).astype(np.int32)], 255, cv2.LINE_AA, shift=4)
        a = m.astype(np.float32) / 255
        lay[..., :3] = lay[..., :3] * (1 - a[..., None]) + a[..., None] * C('AMBER', 1.1)
        lay[..., 3] = np.maximum(lay[..., 3], a)
    img = img * (1 - lay[..., 3:4]) + lay[..., :3]
    # 7-bar colour strip (desaturated 40 %), 60 px tall at the bottom
    bars = ['#C0C0C0', '#C0C000', '#00C0C0', '#00C000', '#C000C0', '#C00000', '#0000C0']
    bw = w / 7.0
    for i, b in enumerate(bars):
        c = hexl(b)
        lum = float(c @ np.float32([0.2126, 0.7152, 0.0722]))
        c = c * 0.6 + lum * 0.4
        x0, x1 = int(round(i * bw)), int(round((i + 1) * bw))
        img[h - 60:h, x0:x1] = c * 0.85
    # vignette + 1 px scanlines
    vig = np.clip(1.0 - 0.55 * (((xx - w / 2) / (w * 0.62)) ** 2 + ((yy - h / 2) / (h * 0.66)) ** 2), 0.25, 1.0)
    img *= vig[..., None]
    img[1::2] *= 0.86
    return ro(img)


@functools.lru_cache(maxsize=4)
def _snow_tile(k):
    """Pre-baked warm snow field k (810, 1080): horizontal-streaked grain at TV resolution."""
    rng = np.random.default_rng(900 + k)
    n = rng.random((PIC_H // 2, PIC_W // 3)).astype(np.float32)
    n = cv2.resize(n, (PIC_W, PIC_H), interpolation=cv2.INTER_NEAREST)
    fine = rng.random((PIC_H, PIC_W)).astype(np.float32)
    s = np.clip(0.55 * n + 0.45 * fine, 0, 1) ** 2.2
    streak = cv2.resize(rng.random((PIC_H // 3, 6)).astype(np.float32), (PIC_W, PIC_H), interpolation=cv2.INTER_LINEAR)
    s *= 0.65 + 0.7 * streak
    return ro(s)


def tv_picture(t, sig_v, gdir_v=1.0, roll=None, shimmer=None, split=None):
    """The TV picture at t: card + signal FX (SHOTS c). Returns (810, 1080, 4) linear, alpha 1."""
    f = int(math.floor(t * FPS + 0.5))
    base = tv_card()
    img = np.array(base, copy=True)
    rows_sig = None
    if split is not None:
        # vertical hold slipped: the card rolls down so its title sits in the locked half under the tear
        img = np.roll(img, int(round((split + 0.20 - 0.43) * PIC_H)), axis=0)
        yy = np.arange(PIC_H, dtype=np.float32)
        ys = split * PIC_H
        rows_sig = np.clip((ys - yy) / 30.0 + 0.5, 0, 1)            # 1 above the tear, 0 below
        s_eff = 1.0
    else:
        s_eff = float(sig_v)
    if s_eff > 1e-3:
        # chroma drop
        lum = img @ np.float32([0.2126, 0.7152, 0.0722])
        dk = s_eff if rows_sig is None else rows_sig[:, None]
        img = img + (lum[..., None] - img) * np.float32(0.85) * (dk[..., None] if rows_sig is not None else dk)
        # ghost (multipath) copy offset 60 sig px
        sh = int(round(60 * s_eff * gdir_v))
        if sh:
            gh = np.roll(img, sh, axis=1)
            ga = 0.4 * min(1.0, s_eff * 1.6)
            if rows_sig is not None:
                ga = ga * rows_sig[:, None, None]
            img = img * (1 - ga * 0.5) + gh * ga * 0.75
        # horizontal tearing (row offsets)
        rng = _rng(f // 2, 5)
        amp = 5.0 * s_eff
        offs = (np.sin(np.arange(PIC_H) * 0.05 + f * 0.9) * amp + rng.normal(0, amp * 0.4, PIC_H))
        if s_eff > 0.4:
            for _ in range(3):
                y = int(rng.integers(0, PIC_H - 40))
                offs[y:y + int(rng.integers(8, 40))] += rng.uniform(-40, 40) * s_eff
        if rows_sig is not None:
            offs = offs * rows_sig
        idx = (np.arange(PIC_W)[None, :] - np.round(offs).astype(np.int32)[:, None]) % PIC_W
        img = np.take_along_axis(img, idx[..., None].repeat(3, 2), axis=1)
        # vertical roll (phase 0..1) with the dark blanking bar at the seam
        ph = roll if roll is not None else (0.6 * s_eff * t) % 1.0
        if rows_sig is None and ph > 1e-3:
            shy = int(round(ph * PIC_H)) % PIC_H
            img = np.roll(img, shy, axis=0)
            bar = np.clip(np.abs(np.arange(PIC_H) - shy) / 22.0, 0, 1) ** 0.6
            img *= (0.15 + 0.85 * bar)[:, None, None]
    # snow (15 fps: 2-frame hold), warm ivory; 3 % when locked
    sn = _snow_tile((f // 2) % 4)
    if (f // 2) % 8 >= 4:
        sn = sn[::-1, ::-1]
    mix = 0.03 + 0.92 * (s_eff ** 0.8)
    if rows_sig is not None:
        mix = (0.03 + 0.92 * rows_sig)[:, None]
    m = sn * np.float32(1.15) * mix
    mk = mix if np.isscalar(mix) else mix[..., None]
    img = img * (1 - mk * 0.9) + m[..., None] * SNOW
    if split is not None:                              # the rolling tear: displaced band + hot line
        ys = int(split * PIC_H)
        band = slice(max(0, ys - 18), min(PIC_H, ys + 18))
        img[band] = np.roll(img[band], 46, axis=1)
        line = np.exp(-((np.arange(PIC_H) - ys) / 3.0) ** 2)[:, None, None]
        img = img + line * SNOW * 0.9
    if shimmer is not None and 0.0 < shimmer < 1.0:   # lock shimmer: soft AMBER diagonal sweep
        yy, xx = np.mgrid[0:PIC_H, 0:PIC_W].astype(np.float32)
        d = (xx + yy * 0.6) / (PIC_W + PIC_H * 0.6) - (shimmer * 1.4 - 0.2)
        img = img + np.exp(-(d / 0.05) ** 2)[..., None] * C('AMBER', 0.55)
    out = np.empty((PIC_H, PIC_W, 4), np.float32)
    out[..., :3] = np.maximum(img, 0)
    out[..., 3] = 1.0
    return out


def tv_picture_at(t):
    """Reference driver: picture state from the yaw clock (shimmer after the f36 / f306 / f648 locks)."""
    tt = t - DUR if t >= F(864) else t
    s = sig(tt)
    sh = None
    for fl in (36, 306):
        u = (tt - F(fl)) / 1.0
        if 0 < u < 1:
            sh = u
    return tv_picture(tt, s, gdir(tt), shimmer=sh)


# ---------------------------------------------------------------------------------------------- 2D CRT mock (preview)
SCREEN = (110, 640, 970, 1330)          # A5 screen box (SHOTS a)


@functools.lru_cache(maxsize=1)
def _crt_maps():
    x0, y0, x1, y1 = SCREEN
    w, h = x1 - x0, y1 - y0
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    u = (xx + 0.5) / w * 2 - 1
    v = (yy + 0.5) / h * 2 - 1
    k = 0.06
    r2 = u * u + v * v
    us, vs = u * (1 + k * r2), v * (1 + k * r2)
    mx = ((us + 1) / 2 * PIC_W).astype(np.float32)
    my = ((vs + 1) / 2 * PIC_H).astype(np.float32)
    a = K.rrect_alpha(w, h, 46.0, 0)
    inside = ((np.abs(us) <= 1) & (np.abs(vs) <= 1)).astype(np.float32)
    shade = np.clip(1.0 - 0.35 * r2 ** 1.5, 0.3, 1)
    return mx, my, a * inside, shade


@functools.lru_cache(maxsize=1)
def _crt_body():
    """Bezel + cabinet sprite around the screen (full frame, premultiplied), plus the glass reflection layer."""
    lay = np.zeros((H, W, 4), np.float32)
    S = ui.Surf(W, H, lay)
    # wood-vinyl cabinet
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    rng = np.random.default_rng(4)
    grain = cv2.resize(rng.standard_normal((40, 6)).astype(np.float32), (W, H), interpolation=cv2.INTER_CUBIC)
    rings = 0.5 + 0.5 * np.sin((yy + grain * 40) / 9.0)
    wood = hexl('#3A2416', 0.55) * (1 - rings[..., None]) + hexl('#5B3A22', 0.75) * rings[..., None]
    a, X0, Y0 = S.rrect_mask(-60, 470, W + 120, 1080, 70)
    S.fill(a, X0, Y0, wood[Y0:Y0 + a.shape[0], X0:X0 + a.shape[1]], 1.0)
    # bezel (dark textured plastic) with a soft top highlight
    bz, X0, Y0 = S.rrect_mask(40, 560, 1000, 860, 70)
    S.fill(bz, X0, Y0, hexl('#2B2927', 0.55), 1.0)
    S.sheen(40, 560, 1000, 860, 70, 0.05, 0.0, 0.25)
    x0, y0, x1, y1 = SCREEN
    S.rrect(x0 - 14, y0 - 14, x1 - x0 + 28, y1 - y0 + 28, 58, hexl('#0B0908'), 1.0)
    # knob row hint under the screen (right) + LED
    for kx in (820, 900):
        S.circle(kx, 1378, 20, hexl('#1A1817', 0.9))
        S.ring(kx, 1378, 20, 2.0, hexl('#C9C7C2', 0.35))
    S.circle(180, 1380, 5, hexl('#5A1008'))
    # glass reflection (window top-left) in its own layer (added over the picture)
    refl = np.zeros((H, W, 4), np.float32)
    w, h = x1 - x0, y1 - y0
    u = (xx[y0:y1, x0:x1] - x0) / w
    v = (yy[y0:y1, x0:x1] - y0) / h
    win = np.exp(-(((u - 0.24) / 0.22) ** 2 + ((v - 0.2) / 0.16) ** 4)) * 0.10
    edge = np.clip(1 - np.minimum(np.minimum(u, 1 - u), np.minimum(v, 1 - v)) / 0.06, 0, 1) ** 2 * 0.05
    refl[y0:y1, x0:x1, :3] = (win + edge)[..., None] * hexl('#FFE2B8')
    return ro(lay), ro(refl)


def crt_mock(cv, pic, glow=1.0):
    """Preview-only 2D CRT: cabinet + bezel + the picture barrel-warped into SCREEN + glass reflection + spill."""
    body, refl = _crt_body()
    over(cv, body.copy())
    mx, my, a, shade = _crt_maps()
    rgb = cv2.remap(np.ascontiguousarray(pic[..., :3]), mx, my, cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT)
    rgb *= shade[..., None]
    x0, y0, x1, y1 = SCREEN
    reg = cv[y0:y1, x0:x1]
    reg[..., :3] = reg[..., :3] * (1 - a[..., None]) + rgb * a[..., None]
    reg[..., 3] = np.maximum(reg[..., 3], a)
    # screen spill on the bezel (mean luma)
    mean = pic[..., :3].reshape(-1, 3).mean(0)
    sp = np.zeros((H, W, 4), np.float32)
    S = ui.Surf(W, H, sp)
    aa, X0, Y0 = S.rrect_mask(x0, y0, x1 - x0, y1 - y0, 46)
    S.glow(aa, X0, Y0, mean / max(1e-3, mean.max()), (18, 60), 0.6 * glow * float(mean.max()), knock=1.0)
    cv[..., :3] += sp[..., :3]
    cv[..., :3] += refl[..., :3]


# ============================================================================================== edit world glass UI
VIEW_C = (540.0, 780.0)
VIEW_W, VIEW_H = 960, 600
SLOT = (24, 60, 912, 513)               # media slot in card px
TL_C = (540.0, 1290.0)
TL_W, TL_H = 960, 360


def _roof_plate():
    """The trailer frame (blurred roof sunset): the A3 roof/sunset plate when rendered, else a procedural plate."""
    p = os.path.join(ASSETS3D, 'roof', 'sunset', '0000.png')
    if os.path.exists(p):
        im = cv2.imread(p, cv2.IMREAD_UNCHANGED)
        if im is not None:
            rgb = cv2.cvtColor(im[..., :3], cv2.COLOR_BGR2RGB)
            lin = (rgb.astype(np.float32) / 255.0) ** 2.2
            return lin
    return None


@functools.lru_cache(maxsize=1)
def trailer_plate():
    """912 x 513 linear RGB: sunset sky, low sun, rooftop skyline with tanks + antennas in silhouette (soft)."""
    w, h = SLOT[2], SLOT[3]
    src = _roof_plate()
    if src is not None:
        hh, ww = src.shape[:2]
        sc = max(w / ww, h / hh)
        r = cv2.resize(src, (int(ww * sc + 1), int(hh * sc + 1)), interpolation=cv2.INTER_AREA)
        y0 = max(0, int(r.shape[0] * 0.45 - h / 2))
        x0 = (r.shape[1] - w) // 2
        img = r[y0:y0 + h, x0:x0 + w]
        return ro(cv2.GaussianBlur(img, (0, 0), 3.0))
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    v = yy / h
    sky = (hexl('#2A0E06') * (1 - v[..., None]) + hexl('#E0782A', 0.9) * (v[..., None] ** 1.6))
    sun_x, sun_y = w * 0.62, h * 0.66
    d = np.sqrt((xx - sun_x) ** 2 + (yy - sun_y) ** 2)
    sky += np.exp(-(d / 34.0) ** 2)[..., None] * hexl('#FFE0A0', 2.2)
    sky += np.exp(-(d / 180.0) ** 2)[..., None] * hexl('#FF9A3C', 0.55)
    sil = np.zeros((h, w), np.uint8)
    rng = np.random.default_rng(12)
    x = 0
    while x < w:                                     # rooftops
        bw = int(rng.integers(60, 150))
        top = int(h * rng.uniform(0.70, 0.82))
        cv2.rectangle(sil, (x, top), (x + bw, h), 255, -1)
        if rng.random() < 0.5:                       # tank
            tw = int(rng.integers(18, 30))
            tx0 = x + int(rng.integers(5, max(6, bw - tw - 5)))
            cv2.rectangle(sil, (tx0, top - 22), (tx0 + tw, top), 255, -1)
        if rng.random() < 0.75:                      # small yagi antenna on a mast
            mx = x + int(rng.integers(10, max(11, bw - 10)))
            mt = top - int(rng.integers(40, 80))
            cv2.line(sil, (mx, top), (mx, mt), 255, 2, cv2.LINE_AA)
            for k in range(5):
                yk = mt + 3 * k
                cv2.line(sil, (mx - 16 + 2 * k, yk), (mx + 16 - 2 * k, yk), 255, 1, cv2.LINE_AA)
        x += bw
    # the hero antenna (left), bigger
    mx, top = int(w * 0.30), int(h * 0.74)
    cv2.line(sil, (mx, h), (mx, int(h * 0.36)), 255, 4, cv2.LINE_AA)
    by = int(h * 0.38)
    cv2.line(sil, (mx - 120, by), (mx + 120, by + 6), 255, 3, cv2.LINE_AA)
    for k in range(8):
        xk = mx - 105 + 30 * k
        L = 46 - 3 * k
        cv2.line(sil, (xk, by + int(k * 0.75) - L), (xk, by + int(k * 0.75) + L), 255, 2, cv2.LINE_AA)
    s = cv2.GaussianBlur(sil.astype(np.float32) / 255.0, (0, 0), 1.6)
    img = sky * (1 - s[..., None]) + hexl('#120604', 0.6) * s[..., None]
    img = cv2.GaussianBlur(img, (0, 0), 2.2)
    return ro(img * 0.85)


@functools.lru_cache(maxsize=1)
def viewer_base():
    """Viewer card: glass + media slot shadow + 'Program' label + scrub bar track (static face)."""
    p = glass(VIEW_W, VIEW_H, 32.0)
    f = p.face.copy()
    pd = p.pad
    S = ui.Surf(f.shape[1], f.shape[0], f)
    x, y, w, h = SLOT
    S.rrect(pd + x - 2, pd + y - 2, w + 4, h + 4, 20, hexl('#050302'), 0.9)
    uput(f, 'Program', 26, pd + 150, pd + 31, 'ui_medium', 'ASH', 'lm')
    uput(f, '00:00:12:04', 26, pd + 290, pd + 31, 'mono', 'ASH', 'lm', opacity=0.8)
    # scrub bar under the media
    S.rrect(pd + 24, pd + 584, 912, 4, 2, C('IVORY', 0.10), 1.0)
    S.rrect(pd + 24, pd + 584, 912 * 0.41, 4, 2, C('FLAME'), 1.0)
    S.circle(pd + 24 + 912 * 0.41, pd + 586, 7, C('IVORY'), 1.0)
    return ui.derive_panel(p, f)


@functools.lru_cache(maxsize=1)
def media_sprite():
    """Trailer plate in a rounded slot (premultiplied, alpha = slot)."""
    img = trailer_plate()
    w, h = SLOT[2], SLOT[3]
    a = K.rrect_alpha(w, h, 18.0, 0)
    out = np.zeros((h, w, 4), np.float32)
    out[..., :3] = img * a[..., None]
    out[..., 3] = a
    return ro(out)


@functools.lru_cache(maxsize=4)
def title_spr(px=58):
    return T.render('SUNDAY KI FILM', 'jw_caps_bold', px=px)


@functools.lru_cache(maxsize=4)
def handles_spr(w, h):
    """Selected-layer transform box (FLAME 1.5 px) with 8 handles and a centre crosshair."""
    pad = 12
    lay = np.zeros((h + 2 * pad, w + 2 * pad, 4), np.float32)
    S = ui.Surf(lay.shape[1], lay.shape[0], lay)
    S.stroke_rrect(pad, pad, w, h, 2, 1.6, C('FLAME', 1.2), 0.95)
    for hx in (0, 0.5, 1):
        for hy in (0, 0.5, 1):
            if hx == 0.5 and hy == 0.5:
                continue
            cx, cy = pad + hx * w, pad + hy * h
            S.rrect(cx - 6, cy - 6, 12, 12, 2, C('IVORY'), 1.0)
            S.stroke_rrect(cx - 6, cy - 6, 12, 12, 2, 1.4, C('FLAME', 1.2), 1.0)
    cx, cy = pad + w / 2, pad + h / 2
    S.rrect(cx - 10, cy - 0.75, 20, 1.5, 0.5, C('FLAME', 1.2), 0.9)
    S.rrect(cx - 0.75, cy - 10, 1.5, 20, 0.5, C('FLAME', 1.2), 0.9)
    return ro(lay)


@functools.lru_cache(maxsize=40)
def ver_chip(v, sel=1.0):
    return ui.chip('v%d' % v, sel=sel, look=LOOK, size=30, h=44, pad_x=20)


@functools.lru_cache(maxsize=1)
def readout_glass():
    return glass(170, 46, 23.0, rim=0.5, glow=0.3, shadow=0.4)


@functools.lru_cache(maxsize=64)
def readout_txt(xv):
    return T.render('X %d' % xv, 'jw_mono', px=30)


def viewer(cv, t, xv, ver, ghost=0.0, gdir_v=-1.0, dy=0.0, cx=None, cy=None, scale=1.0, delta=None,
           readout_flash=0.0, opacity=1.0, handles=True):
    """Glass viewer at (cx, cy) (default VIEW_C): trailer frame, title at X (ghost-double while ghost > 0),
    version chip, X readout chip (+ delta flash text), scrub bar."""
    cx = VIEW_C[0] if cx is None else cx
    cy = (VIEW_C[1] if cy is None else cy) + dy
    base = viewer_base()
    base.draw(cv, cx, cy, scale=scale, opacity=opacity)
    x0 = cx - VIEW_W / 2 * scale
    y0 = cy - VIEW_H / 2 * scale

    def P(px_, py_):
        return x0 + px_ * scale, y0 + py_ * scale
    mx, my = P(SLOT[0] + SLOT[2] / 2, SLOT[1] + SLOT[3] / 2)
    K.draw(cv, media_sprite(), mx, my, scale=scale, opacity=opacity)
    # the title in the trailer frame (X in 1080-px comp units -> slot px x 0.845)
    tsp = title_spr()
    off = (xv - 540.0) * 0.845 * scale
    ty = my - 6 * scale
    if ghost > 0:
        tsp.draw(cv, mx + off + 6 * gdir_v * scale, ty, scale=scale, opacity=0.25 * ghost * opacity, snap=False)
    tsp.draw(cv, mx + off, ty, scale=scale, opacity=opacity, snap=False)
    if handles:
        hs = handles_spr(int(tsp.w * 0.86) + 24, 64)
        K.draw(cv, hs, mx + off, ty, scale=scale, opacity=0.9 * opacity)
    # version chip (top-left) and readout (top-right)
    chx, chy = P(90, 31)
    if ver:
        K.draw(cv, ver_chip(ver), chx, chy, scale=scale, opacity=opacity)
    rx, ry = P(VIEW_W - 130, 31)
    readout_glass().draw(cv, rx, ry, scale=scale, opacity=opacity)
    if readout_flash > 0:
        g = J.underline(150)
        K.draw(cv, solid(K.rrect_alpha(170, 46, 23.0, 0), C('FLAME', 0.35)), rx, ry, scale=scale,
               opacity=readout_flash * opacity, mode='add')
    readout_txt(int(round(xv))).draw(cv, rx, ry, scale=scale, opacity=opacity, snap=False)
    if delta:
        s_, a = delta
        if a > 1e-3:
            tx(s_, 'jw_mono', 30, ('FLAME', 1.4)).draw(cv, rx - 100 * scale, ry, anchor=(1.0, 0.5), scale=scale,
                                                       opacity=a * opacity, snap=False)


@functools.lru_cache(maxsize=1)
def _clip_thumb():
    img = trailer_plate()
    th = cv2.resize(np.ascontiguousarray(img), (64, 36), interpolation=cv2.INTER_AREA)
    a = K.rrect_alpha(64, 36, 5.0, 0)
    out = np.zeros((36, 64, 4), np.float32)
    out[..., :3] = th * a[..., None]
    out[..., 3] = a
    return ro(out)


@functools.lru_cache(maxsize=1)
def timeline_panel():
    """Timeline card (static face): ruler, track headers, title clip, V1 clips with thumbs, A1 + A2 waveforms."""
    p = glass(TL_W, TL_H, 32.0)
    f = p.face.copy()
    pd = p.pad
    S = ui.Surf(f.shape[1], f.shape[0], f)
    X0 = pd + 130                                     # track area left (card px + pad)
    X1 = pd + TL_W - 24
    # header: timecode + ruler
    uput(f, '00:00:12:04', 26, pd + 26, pd + 34, 'mono', 'AMBER', 'lm')
    for k in range(0, 34):
        x = X0 + 24 * k
        if x > X1:
            break
        major = k % 6 == 0
        S.rrect(x, pd + (22 if major else 32), 1.5, 22 if major else 12, 0.5, C('ASH', 0.9 if major else 0.5), 1.0)
        if major and pd + 230 < x and x + 70 < pd + 840:
            uput(f, '00:%02d' % (12 + k // 6), 22, x + 6, pd + 30, 'mono', 'ASH', 'lm', opacity=0.85)
    S.rrect(pd + 16, pd + 56, TL_W - 32, 1.2, 0.5, C('IVORY', 0.12), 1.0)
    rows = [('V2', 70, 54), ('V1', 136, 66), ('A1', 214, 52), ('A2', 276, 52)]
    for name, ry, rh in rows:
        S.rrect(pd + 16, pd + ry, 100, rh, 10, C('IVORY', 0.05), 1.0)
        uput(f, name, 24, pd + 34, pd + ry + rh / 2, 'mono', 'ASH', 'lm')
        S.circle(pd + 96, pd + ry + rh / 2, 4, C('FLAME' if name[0] == 'V' else 'GOLD', 0.9), 1.0)
        S.rrect(X0, pd + ry + rh + 5, X1 - X0, 1, 0.5, C('IVORY', 0.06), 1.0)
    # V2: the title clip (FLAME) with keyframe diamonds
    cx0, cx1 = X0 + 150, X0 + 560
    a, ax, ay = S.rrect_grad(cx0, pd + 74, cx1 - cx0, 46, 10, C('AMBER'), C('FLAME'), -90, 1.0)
    S.sheen(cx0, pd + 74, cx1 - cx0, 46, 10, 0.10, 0.0, 0.5)
    uput(f, 'SUNDAY KI FILM', 22, cx0 + 16, pd + 97, 'mono_bold', 'INK', 'lm')
    for kx in (cx0 + 260, cx0 + 330, cx0 + 384):
        pts = np.array([[kx, pd + 89], [kx + 7, pd + 97], [kx, pd + 105], [kx - 7, pd + 97]], np.float32)
        m = np.zeros(f.shape[:2], np.uint8)
        cv2.fillPoly(m, [np.round(pts * 16).astype(np.int32)], 255, cv2.LINE_AA, shift=4)
        aa = m.astype(np.float32) / 255
        f[..., :3] = f[..., :3] * (1 - aa[..., None]) + aa[..., None] * C('INK')
        f[..., 3] = np.maximum(f[..., 3], aa)
    # V1: EMBER clips with tiny roof thumbs
    th = _clip_thumb()
    xs = [X0, X0 + 210, X0 + 380, X0 + 600]
    for i in range(len(xs)):
        x0c = xs[i] + 3
        x1c = (xs[i + 1] if i + 1 < len(xs) else X1) - 3
        S.rrect_grad(x0c, pd + 140, x1c - x0c, 58, 10, C('EMBER', 1.1), C('PLUM', 1.4), -90, 1.0)
        S.stroke_rrect(x0c, pd + 140, x1c - x0c, 58, 10, 1.2, C('FLAME', 0.7), 0.6)
        xx = x0c + 8
        while xx + 64 < x1c - 6:
            S.paste(th, xx, pd + 151)
            xx += 70
    # A1 / A2 waveforms
    rng = np.random.default_rng(31)
    for ry, colr, amp in ((214, C('ASH', 0.95), 1.0), (276, C('GOLD', 0.75), 0.7)):
        yc = pd + ry + 26
        n = int((X1 - X0) / 3)
        env = np.abs(np.convolve(rng.standard_normal(n), np.ones(5) / 5, 'same'))
        env = np.clip(env * 0.6 + 0.25 * np.abs(np.sin(np.arange(n) * 0.11)), 0.05, 1.0) * amp
        for k in range(n):
            hh_ = 2 + env[k] * 20
            S.rrect(X0 + 3 * k, yc - hh_, 2, 2 * hh_, 1, colr, 0.85)
    return ui.derive_panel(p, f), X0 - pd


def timeline(cv, t, dy=0.0, opacity=1.0, scale=1.0):
    panel, tx0 = timeline_panel()
    cx, cy = TL_C[0], TL_C[1] + dy
    panel.draw(cv, cx, cy, scale=scale, opacity=opacity)
    # playhead (IVORY 3 px + flame head), parked over the title clip
    x0 = cx - TL_W / 2
    ph = x0 + tx0 + 392
    y_top, y_bot = cy - TL_H / 2 + 14, cy + TL_H / 2 - 14
    aa_line(cv, (ph, y_top + 14), (ph, y_bot), 3.0, C('IVORY'), 0.95 * opacity)
    K.draw(cv, _playhead_head(), ph, y_top + 10, opacity=opacity)


@functools.lru_cache(maxsize=1)
def _playhead_head():
    lay = np.zeros((40, 40, 4), np.float32)
    S = ui.Surf(40, 40, lay)
    a, X0, Y0 = S.rrect(10, 6, 20, 16, 5, C('FLAME', 1.3), 1.0)
    pts = np.array([[10, 18], [30, 18], [20, 30]], np.float32)
    m = np.zeros((40, 40), np.uint8)
    cv2.fillPoly(m, [np.round(pts * 16).astype(np.int32)], 255, cv2.LINE_AA, shift=4)
    aa = m.astype(np.float32) / 255
    lay[..., :3] = lay[..., :3] * (1 - aa[..., None]) + aa[..., None] * C('FLAME', 1.3)
    lay[..., 3] = np.maximum(lay[..., 3], aa)
    return ro(K.glow(lay, C('FLAME'), sigmas=(3, 8), strength=0.5))


# ---------------------------------------------------------------------------------------------- notification toast T1
@functools.lru_cache(maxsize=1)
def toast_panel():
    w, h = 700, 132
    p = glass(w, h, 34.0, rim=0.7, glow=0.7)
    f = p.face.copy()
    pd = p.pad
    S = ui.Surf(f.shape[1], f.shape[0], f)
    # app icon: rounded square FLAME -> RED with a white chat glyph
    ix, iy = pd + 28, pd + 28
    a, X0, Y0 = S.rrect_grad(ix, iy, 76, 76, 20, C('AMBER'), C('RED'), -60, 1.0)
    S.sheen(ix, iy, 76, 76, 20, 0.14, 0.0, 0.5)
    S.paste(ui.icon('chat', 42, 'WHITE', stroke=2.6, fill_a=0.0), ix + 38, iy + 39, anchor=(0.5, 0.5))
    uput(f, 'Client', 34, pd + 128, pd + 56, 'ui_bold', 'IVORY', 'ls')
    uput(f, 'now', 26, pd + w - 30, pd + 54, 'body', 'ASH', 'rs')
    uput(f, 'thoda left...', 38, pd + 128, pd + 104, 'body', 'IVORY', 'ls')
    return ui.derive_panel(p, f)


def toast(cv, t, f0=468, f1=483, x=540.0):
    """T1: drops y 300 -> 420 with the POP spring on f0, leaves up (in_cubic 3 f) from f1."""
    f = t * FPS
    if f < f0 - 0.5 or f >= f1 + 3.5:
        return
    u = X.spring(max(0.0, t - F(f0) + HALF), 'POP')
    y = 300.0 + 120.0 * u
    op = ease('out_cubic', (f - f0 + 1) / 3.0)
    ex = ease('in_cubic', (f - f1) / 3.0)
    toast_panel().draw(cv, x, y - 40 * ex, scale=0.94 + 0.06 * min(1.0, u), opacity=op * (1 - ex))


# ---------------------------------------------------------------------------------------------- cursor (S7)
def cursor(cv, t):
    """Arrow cursor glides to the X readout and clicks it on f477 (then drifts off by f485)."""
    f = t * FPS
    if f < 466 or f >= 486:
        return
    rx, ry = VIEW_C[0] + VIEW_W / 2 - 130 - 52, VIEW_C[1] - VIEW_H / 2 + 40
    p0, p1, p2 = (760.0, 980.0), (rx, ry), (rx + 70, ry + 160)
    if f < 476:
        u = ease('inout_cubic', (f - 466) / 10.0)
        x, y = p0[0] + (p1[0] - p0[0]) * u, p0[1] + (p1[1] - p0[1]) * u - 30 * math.sin(math.pi * u)
    elif f < 480:
        x, y = p1
    else:
        u = ease('in_cubic', (f - 480) / 6.0)
        x, y = p1[0] + (p2[0] - p1[0]) * u, p1[1] + (p2[1] - p1[1]) * u
    press = K.impulse(t, F(477), 9)
    op = ease('out_cubic', (f - 466) / 3.0) * (1 - ease('in_cubic', (f - 482) / 4.0))
    ui.draw_cursor(cv, x, y, 'arrow', 64, press=press, click=(t - F(477)) if f >= 477 else None, opacity=op,
                   look=LOOK)


# ---------------------------------------------------------------------------------------------- revision list (L1)
ROW_W, ROW_H, ROW_PITCH, ROW_TOP = 780, 60, 70, 1140


@functools.lru_cache(maxsize=2)
def row_glass(hot=False):
    return glass(ROW_W, ROW_H, 18.0, rim=1.0 if hot else 0.35, glow=0.8 if hot else 0.15, shadow=0.45)


def _row(cv, cx, cy, v, op, hot=False, sweep=None, scale=1.0):
    p = row_glass(hot)
    face = p.face_at(sweep=sweep) if (hot and sweep is not None) else None
    p.draw(cv, cx, cy, scale=scale, opacity=op, face=face, frost=0)
    x0 = cx - ROW_W / 2 * scale
    K.draw(cv, _clip_thumb(), x0 + 24 * scale + 32 * scale, cy, scale=scale * 0.9, opacity=op)
    uput(cv, vname(v), 28, x0 + 104 * scale, cy, 'mono_bold' if hot else 'mono', 'IVORY', 'lm', opacity=op,
         scale=scale)
    uput(cv, 'X %d' % vx(v), 26, x0 + (ROW_W - 26) * scale, cy, 'mono', 'AMBER' if hot else 'ASH', 'rm',
         opacity=op, scale=scale)


def revisions(cv, t, alpha=1.0, light27=0.0):
    """S9 revision avalanche: a row every 3 f from f522 (v5 .. v22), newest on top with a flame rim and a comet,
    older rows dim to 0.6, max 5 visible. From f576 the list holds (v23-v26 arrive with the split) and v27 lands
    on f648 lit (light27)."""
    f = t * FPS
    if f < 521.5:
        return
    arrivals = [(522 + 3 * (v - 5), v) for v in range(5, 23)] + [(576, 23), (594, 24), (612, 25), (630, 26), (648, 27)]
    shown = [(fa, v) for fa, v in arrivals if f >= fa - 0.5]
    if not shown:
        return
    shown = shown[::-1]                              # newest first
    newest_f = shown[0][0]
    pu = ease('out_cubic', (f - newest_f + 1) / 3.0)
    for k, (fa, v) in enumerate(shown[:6]):
        slot = k - (1.0 - pu) if k > 0 else 0.0
        if k == 0:
            slot = 0.0
        y = ROW_TOP + ROW_H / 2 + ROW_PITCH * slot
        if k == 0:
            op = pu
            sc = 0.96 + 0.04 * pu
        else:
            op = 0.6 if k > 1 else 0.6 + 0.4 * (1 - pu)
            sc = 1.0
        if k >= 5:
            op *= (1 - pu)
        if k >= 1 and f >= 647.5:                    # T2 + v27: the older rows step back
            op *= 1.0 - 0.75 * ease('out_cubic', (f - 647.5) / 6.0)
        if k == 0 and v == 27:
            op = max(op, 0.0)
        hot = k == 0
        sweep = ((t * 0.9) % 1.0) if hot else None
        if op * alpha > 1e-3:
            _row(cv, 540.0, y, v, op * alpha, hot, sweep, sc)
    if light27 > 0 and shown[0][1] == 27:
        y = ROW_TOP + ROW_H / 2
        K.draw(cv, _row_glow(), 540.0, y, opacity=light27 * alpha, mode='add')


@functools.lru_cache(maxsize=1)
def _row_glow():
    a = K.rrect_alpha(ROW_W, ROW_H, 18.0, 40)
    g = np.array(K.glow(solid(a, C('GOLD', 0.0) + 1e-6), C('GOLD'), sigmas=(8, 24), strength=0.9, include=False))
    pd = (g.shape[0] - a.shape[0]) // 2
    inside = np.zeros(g.shape[:2], np.float32)
    inside[pd:pd + a.shape[0], pd:pd + a.shape[1]] = a
    g *= (1.0 - inside)[..., None]                   # outer halo only: the row text stays crisp
    return ro(g)


# ---------------------------------------------------------------------------------------------- chat bubble (T2 / split)
@functools.lru_cache(maxsize=16)
def chat_bubble(msg, w, h, body_px=38, name='Client', avatar=True):
    """Glass speech bubble with a left tail, SMOKE + FLAME hairline, avatar disc 'C', name + message."""
    pad = 50
    tail = 22
    lay = np.zeros((h + 2 * pad, w + 2 * pad + tail, 4), np.float32)
    S = ui.Surf(lay.shape[1], lay.shape[0], lay)
    x0, y0 = pad + tail, pad
    r = min(h / 2, 60)
    # shadow
    sh = np.zeros(lay.shape[:2], np.float32)
    a, X0, Y0 = S.rrect_mask(x0, y0 + 10, w, h, r)
    sh[Y0:Y0 + a.shape[0], X0:X0 + a.shape[1]] = a
    sh = cv2.GaussianBlur(sh, (0, 0), 16) * 0.55
    lay[..., 3] = sh
    # tail (curl at bottom-left)
    tm = np.zeros(lay.shape[:2], np.uint8)
    pts = np.array([[x0 + 24, y0 + h - 30], [x0 - tail + 2, y0 + h + 2], [x0 + 40, y0 + h - 4]], np.float32)
    cv2.fillPoly(tm, [np.round(pts * 16).astype(np.int32)], 255, cv2.LINE_AA, shift=4)
    ta = tm.astype(np.float32) / 255
    body = np.zeros(lay.shape[:2], np.float32)
    a, X0, Y0 = S.rrect_mask(x0, y0, w, h, r)
    body[Y0:Y0 + a.shape[0], X0:X0 + a.shape[1]] = a
    body = np.maximum(body, ta)
    yy = np.arange(lay.shape[0], dtype=np.float32)[:, None]
    g = np.clip((yy - y0) / h, 0, 1)
    colr = hexl('#3A241C') * (1 - g[..., None]) + hexl('#1E120D') * g[..., None]
    lay[..., :3] = lay[..., :3] * (1 - body[..., None]) + colr * body[..., None]
    lay[..., 3] = np.maximum(lay[..., 3] * (1 - body), body)
    lay[..., :3] *= 1.0
    # hairline (FLAME at the bottom-right, ivory at the top-left)
    e = np.clip(body - cv2.erode(body, np.ones((3, 3), np.uint8)), 0, 1)
    xx = np.arange(lay.shape[1], dtype=np.float32)[None, :]
    k = np.clip((xx - x0) / w * 0.6 + (yy - y0) / h * 0.6, 0, 1)
    lay[..., :3] += e[..., None] * (C('IVORY', 0.35) * (1 - k[..., None]) + C('FLAME', 1.2) * k[..., None])
    S.sheen(x0 + 2, y0 + 2, w - 4, h - 4, r - 2, 0.06, 0.0, 0.45)
    tx_ = x0 + 30
    if avatar:
        ar = min(30, h * 0.3)
        acx, acy = x0 + 26 + ar, y0 + h / 2
        a2, X0, Y0 = S.circle(acx, acy, ar, hexl('#4A2A1E'))
        gg = ui._lingrad(a2.shape[1], a2.shape[0], C('FLAME'), C('RED'), -60)
        S.fill(a2, X0, Y0, gg, 1.0)
        put = ui.text('C', ar * 1.05, 'ui_bold', 'WHITE')
        x_, y_ = put.topleft(acx, acy, 'mm')
        ui.paste(lay, put.spr, round(x_), round(y_))
        tx_ = acx + ar + 22
    if name:
        uput(lay, name, int(body_px * 0.74), tx_, y0 + h * 0.40, 'ui_bold', 'ASH', 'ls')
        uput(lay, msg, body_px, tx_, y0 + h * 0.40 + body_px * 1.12, 'body', 'IVORY', 'ls')
    else:
        uput(lay, msg, body_px, tx_, y0 + h / 2, 'body', 'IVORY', 'lm')
    # anchor: body centre
    return ro(lay), ((x0 + w / 2) / lay.shape[1], (y0 + h / 2) / lay.shape[0])


def bubble(cv, msg, w, h, cx, cy, t, t0, t1=None, body_px=38, name='Client', exit_f=4, scale=1.0, opacity=1.0):
    """Pop a chat bubble on t0 (POP spring from its tail corner), exit in_cubic over exit_f frames from t1."""
    if t < t0 - HALF:
        return
    spr, an = chat_bubble(msg, int(w), int(h), body_px, name)
    k = 0.6 + 0.4 * X.spring(max(0.0, t - t0 + HALF), 'POP')
    op = ease('out_cubic', (t - t0 + HALF) / F(3))
    ex = 0.0 if t1 is None else ease('in_cubic', (t - t1) / F(exit_f))
    o = op * (1 - ex) * opacity
    if o <= 1e-3:
        return
    K.draw(cv, spr, cx - (1 - k) * w * 0.35 * scale, cy + (1 - k) * h * 0.35 * scale - 10 * ex, scale=k * scale,
           anchor=an, opacity=o)


def client_bubble(cv, t):
    """T2 (f648-f683): 'BAS BAS! ab theek hai!' (centre y 1330: clear of the lit v27 row)."""
    f = t * FPS
    if 647.5 <= f < 684.5:
        bubble(cv, 'BAS BAS! ab theek hai!', 620, 124, 548, 1340, t, F(648), F(680))


# ---------------------------------------------------------------------------------------------- export dialog (E1)
EXP_C = (540.0, 1250.0)


@functools.lru_cache(maxsize=1)
def export_panel():
    w, h = 760, 260
    p = glass(w, h, 28.0, rim=0.9, glow=0.8)
    f = p.face.copy()
    pd = p.pad
    S = ui.Surf(f.shape[1], f.shape[0], f)
    S.paste(ui.icon('arrow_right', 34, 'AMBER', stroke=2.6), pd + 46, pd + 52, anchor=(0.5, 0.5))
    uput(f, 'Exporting', 34, pd + 76, pd + 52, 'body', 'ASH', 'lm')
    uput(f, 'v27_final_FINAL.mp4', 34, pd + 40, pd + 112, 'mono', 'IVORY', 'lm')
    uput(f, 'H.264  ·  1080 × 1920  ·  30 fps', 26, pd + 40, pd + 216, 'body', 'ASH', 'lm', opacity=0.85)
    S.rrect(pd + 40, pd + 152, 680, 14, 7, C('IVORY', 0.08), 1.0)
    return ui.derive_panel(p, f)


@functools.lru_cache(maxsize=1)
def _bar_full():
    w, h = 680, 14
    lay = np.zeros((h + 60, w + 60, 4), np.float32)
    S = ui.Surf(lay.shape[1], lay.shape[0], lay)
    a, X0, Y0 = S.rrect_grad(30, 30, w, h, 7, C('FLAME', 1.2), C('RED', 1.1), 0, 1.0)
    S.glow(a, X0, Y0, C('FLAME'), (4, 12), 0.6, knock=0.9)
    return ro(lay)


def export_dialog(cv, t, f0=684, f_done=716, f_out=None):
    f = t * FPS
    if f < f0 - 0.5 or (f_out is not None and f >= f_out + 4.5):
        return
    k = 0.9 + 0.1 * X.spring(max(0.0, t - F(f0) + HALF), 'POP')
    op = ease('out_cubic', (f - f0 + 1) / 3.0)
    if f_out is not None:
        op *= 1 - ease('in_cubic', (f - f_out) / 4.0)
    cx, cy = EXP_C
    export_panel().draw(cv, cx, cy, scale=k, opacity=op)
    p = ease('inout_sine', (f - (f0 + 3)) / float(f_done - f0 - 3))
    x0 = cx - 380 * k + 40 * k
    yb = cy - 130 * k + 159 * k
    if p > 0:
        bar = _bar_full()
        cut = int(30 + 680 * p)
        spr = np.array(bar[:, :cut + 30], copy=True)
        spr[:, cut:] *= np.linspace(1, 0, spr.shape[1] - cut, dtype=np.float32)[None, :, None] ** 3
        K.draw(cv, ro(spr), x0 - 30 * k, yb, anchor=(0, 0.5), scale=k, opacity=op)
        if p < 1:
            K.draw(cv, J.underline(40).head, x0 + 680 * p * k, yb, scale=0.7 * k, opacity=op, mode='add')
    pct = int(round(100 * p))
    txt = '%d %%' % pct
    text(cv, txt, 'jw_mono', 34, cx + 340 * k, cy - 130 * k + 52 * k, anchor=(1.0, 0.5), scale=k,
         opacity=op, snap=False, fill=('AMBER', 1.0) if pct >= 100 else None)
    if f >= f_done:
        u = X.spring(max(0.0, t - F(f_done)), 'POP')
        K.draw(cv, _done_tick(), cx + 340 * k - 150, cy - 130 * k + 52 * k, scale=k * (0.6 + 0.4 * u), opacity=op)


@functools.lru_cache(maxsize=1)
def _done_tick():
    return ro(ui.checkbox(1.0, size=44, look=LOOK))


# ---------------------------------------------------------------------------------------------- the S7 / S9 / S11 layer
def edit_ui(cv, t, title_in=None):
    """The edit-world glass UI by frame (S7 f432-485, S9 f522-575, S11 f648-719). title_in(t) = 0..1 progress of
    the title riding in on the M3 track (default: settled by f441). Draw into a layer + plane_warp for the tilt."""
    f = t * FPS
    xv, ver, dirn = client(t)
    gh = sig_c(t)
    if 431.5 <= f < 486 or 521.5 <= f < 576 or 647.5 <= f < 720:
        # timeline: in S7 and slides out (down) f522-f528
        if f < 529:
            dy = 0.0 if f < 522 else 420.0 * ease('in_cubic', (f - 522) / 6.0)
            op = 1.0 if f < 522 else 1.0 - ease('in_cubic', (f - 522) / 6.0)
            timeline(cv, t, dy=dy, opacity=op)
        delta = None
        flash = 0.0
        if 476.5 <= f < 483:
            delta = ('-2 px', 1.0 - ease('in_cubic', (f - 480) / 3.0))
            flash = 1.0 - ease('out_cubic', (f - 477) / 6.0)
        if f >= 647.5:
            flash = max(flash, 1.0 - ease('out_cubic', (f - 648) / 8.0))
        viewer(cv, t, xv, ver, ghost=gh, gdir_v=-dirn, delta=delta, readout_flash=flash)
        if f >= 521.5:
            a = 1.0
            if f >= 683.5:
                a = 1.0 - ease('in_cubic', (f - 684) / 5.0)
            revisions(cv, t, alpha=a, light27=(1.0 - ease('inout_sine', (f - 652) / 30.0)) if f >= 648 else 0.0)
        toast(cv, t)
        cursor(cv, t)
        client_bubble(cv, t)
        export_dialog(cv, t)


def plane_warp(layer, rx=4.0, ry=-6.0, rz=0.0, focal=2200.0, center=(540.0, 960.0)):
    """Perspective-tilt a full-frame layer about `center` (degrees; rx tips the top away, ry turns the right side
    away) - the 2.5D UI plane of S7 / S9 / S11. Returns a new premultiplied layer."""
    cx, cy = center
    pts = np.float32([[0, 0], [W, 0], [W, H], [0, H]])
    a, b, c = math.radians(rx), math.radians(ry), math.radians(rz)
    Rx = np.array([[1, 0, 0], [0, math.cos(a), -math.sin(a)], [0, math.sin(a), math.cos(a)]])
    Ry = np.array([[math.cos(b), 0, math.sin(b)], [0, 1, 0], [-math.sin(b), 0, math.cos(b)]])
    Rz = np.array([[math.cos(c), -math.sin(c), 0], [math.sin(c), math.cos(c), 0], [0, 0, 1]])
    R = Rz @ Ry @ Rx
    out = []
    for x, y in pts:
        p = R @ np.array([x - cx, y - cy, 0.0])
        z = focal + p[2]
        out.append([cx + p[0] * focal / z, cy + p[1] * focal / z])
    M = cv2.getPerspectiveTransform(pts, np.float32(out))
    return cv2.warpPerspective(layer, M, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT)


# ============================================================================================== phone screen (S8)
PH_W, PH_H = 720, 1560
# thread: (side, text, time, pop frame or None)
THREAD = [('in', 'thoda left...', '4:09', None), ('out', 'done', '4:10', None),
          ('in', 'thoda right...', '4:12', 490), ('in', 'nahi, pehle wala', '4:12', 504)]
TYPING_F = 510
BODY_PX = 50
BUB_H = 108


@functools.lru_cache(maxsize=1)
def _wallpaper():
    """Warm-dark chat wallpaper with a faint doodle pattern (no branding)."""
    h, w = PH_H, PH_W
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    v = (yy / h)[..., None]
    img = hexl('#140B08') * (1 - v) + hexl('#0C0605') * v
    lay = np.zeros((h, w, 4), np.float32)
    rng = np.random.default_rng(77)
    names = ('sparkle', 'clock', 'star', 'globe', 'mail', 'phone', 'chat', 'bell', 'pin', 'calendar')
    for gy in range(0, h + 120, 120):
        for gx in range(0, w + 120, 120):
            nm = names[int(rng.integers(0, len(names)))]
            ic = ui.icon(nm, int(rng.integers(30, 44)), 'IVORY', stroke=1.6)
            x = gx + (60 if (gy // 120) % 2 else 0) + rng.uniform(-14, 14)
            K.draw(lay, ic, x, gy + rng.uniform(-14, 14), rot=float(rng.uniform(-25, 25)), opacity=0.03)
    img = img * (1 - lay[..., 3:4]) + lay[..., :3]
    return ro(img)


def _status_bar(S, f, img):
    uput(img, '4:12', 30, 54, 50, 'ui_bold', 'IVORY', 'ls')
    # signal bars
    for k in range(4):
        hb = 8 + 5 * k
        S.rrect(538 + 9 * k, 50 - hb, 6, hb, 1.5, C('IVORY'), 1.0 if k < 3 else 0.35)
    # wifi (3 arcs) as rings clipped top
    cx, cy = 600, 50
    for r_, a_ in ((16, 1.0), (10, 1.0), (4, 1.0)):
        ring = np.zeros((60, 60), np.float32)
        yy, xx = np.mgrid[0:60, 0:60].astype(np.float32)
        d = np.sqrt((xx - 30) ** 2 + (yy - 44) ** 2)
        ring = np.clip(1.6 - np.abs(d - r_ - 2), 0, 1) * ((yy < 44 - 0.6 * np.abs(xx - 30)).astype(np.float32))
        if r_ == 4:
            ring = np.clip(r_ + 1.5 - d, 0, 1) * (yy < 46).astype(np.float32)
        S.fill(ring, cx - 30, cy - 44 + 0, C('IVORY'), a_)
    # battery
    S.stroke_rrect(626, 34, 44, 20, 6, 2.0, C('IVORY', 0.9), 1.0)
    S.rrect(630, 38, 28, 12, 3, C('IVORY'), 1.0)
    S.rrect(671, 40, 3, 8, 1.5, C('IVORY', 0.9), 1.0)


def _header(S, img):
    S.rrect(0, 0, PH_W, 210, 0, hexl('#1A0E0A'), 1.0)
    S.rrect(0, 209, PH_W, 1.5, 0, C('IVORY', 0.07), 1.0)
    # back chevron
    for (a0, a1) in (((44, 140), (28, 124)), ((28, 124), (44, 108))):
        pass
    m = np.zeros((PH_H, PH_W), np.float32)
    pts = np.array([[46, 112], [28, 140], [46, 168]], np.float32)
    mm = np.zeros((PH_H, PH_W), np.uint8)
    cv2.polylines(mm, [np.round(pts * 16).astype(np.int32)], False, 255, 4 * 16 // 16 + 3, cv2.LINE_AA, shift=4)
    m = mm.astype(np.float32) / 255
    S.fill(m[100:180, 10:70], 10, 100, C('IVORY'), 1.0)
    # avatar
    a, X0, Y0 = S.circle(112, 140, 38, C('FLAME'))
    g = ui._lingrad(a.shape[1], a.shape[0], C('AMBER'), C('RED'), -60)
    S.fill(a, X0, Y0, g, 1.0)
    S.sheen(74, 102, 76, 76, 38, 0.10, 0.0, 0.5)
    uput(img, 'C', 40, 112, 140, 'ui_bold', 'WHITE', 'mm')
    S.circle(140, 168, 9, hexl('#1A0E0A'))
    S.circle(140, 168, 6, C('GOLD', 1.1))
    uput(img, 'Client', 44, 172, 132, 'ui_bold', 'IVORY', 'ls')
    uput(img, 'online', 30, 172, 172, 'body', 'ASH', 'ls')
    S.paste(ui.icon('phone', 40, 'IVORY', stroke=2.2), 664, 140, anchor=(0.5, 0.5))
    # video camera glyph
    S.stroke_rrect(560, 124, 40, 32, 7, 2.4, C('IVORY'), 1.0)
    tri = np.zeros((40, 40), np.uint8)
    cv2.fillPoly(tri, [np.array([[2, 14], [16, 6], [16, 30], [2, 22]], np.int32) * 1], 255, cv2.LINE_AA)
    S.fill(tri.astype(np.float32) / 255, 600, 122, C('IVORY'), 1.0)


def _input_bar(S, img):
    S.rrect(0, PH_H - 150, PH_W, 150, 0, hexl('#140B08'), 0.96)
    S.rrect(24, PH_H - 132, 560, 84, 42, hexl('#2A1A15'), 1.0)
    S.stroke_rrect(24, PH_H - 132, 560, 84, 42, 1.2, C('IVORY', 0.10), 1.0)
    # emoji face
    S.ring(74, PH_H - 90, 15, 2.4, C('ASH'))
    S.circle(68, PH_H - 94, 2.2, C('ASH'))
    S.circle(80, PH_H - 94, 2.2, C('ASH'))
    arc = np.zeros((30, 30), np.float32)
    yy, xx = np.mgrid[0:30, 0:30].astype(np.float32)
    d = np.sqrt((xx - 15) ** 2 + (yy - 11) ** 2)
    arc = np.clip(1.4 - np.abs(d - 9), 0, 1) * (yy > 15).astype(np.float32)
    S.fill(arc, 59, PH_H - 98, C('ASH'), 1.0)
    uput(img, 'Message', 36, 110, PH_H - 90, 'body', 'ASH', 'lm', opacity=0.8)
    S.paste(ui.icon('pin', 36, 'ASH', stroke=2.2), 500, PH_H - 90, anchor=(0.5, 0.5))
    S.paste(ui.icon('plus', 36, 'ASH', stroke=2.2), 548, PH_H - 90, anchor=(0.5, 0.5))
    a, X0, Y0 = S.circle(648, PH_H - 90, 42, C('FLAME'))
    g = ui._lingrad(a.shape[1], a.shape[0], C('AMBER'), C('FLAME'), -70)
    S.fill(a, X0, Y0, g, 1.0)
    # mic glyph
    S.rrect(640, PH_H - 112, 16, 30, 8, C('INK'), 1.0)
    S.stroke_rrect(633, PH_H - 98, 30, 26, 12, 2.6, C('INK'), 1.0)
    S.rrect(646.5, PH_H - 74, 3, 10, 1, C('INK'), 1.0)
    S.rrect(PH_W / 2 - 70, PH_H - 18, 140, 6, 3, C('IVORY', 0.6), 1.0)


@functools.lru_cache(maxsize=1)
def _chrome():
    """Static screen layers: wallpaper, status bar, header, input bar, date chip -> (bg rgb, overlay rgba)."""
    bg = np.array(_wallpaper(), copy=True)
    ov = np.zeros((PH_H, PH_W, 4), np.float32)
    S = ui.Surf(PH_W, PH_H, ov)
    _header(S, ov)
    _status_bar(S, 0, ov)
    _input_bar(S, ov)
    return ro(bg), ro(ov)


@functools.lru_cache(maxsize=16)
def msg_bubble(side, msg, tm, tail=True):
    """One chat message bubble sprite: incoming SMOKE / outgoing PLUM, IVORY body 44, time 26 ASH, ticks."""
    tw = uwidth(msg, BODY_PX, 'body')
    meta_w = uwidth(tm, 26, 'body') + (44 if side == 'out' else 0)
    w = int(min(580, tw + meta_w + 76))
    h = BUB_H
    pad = 30
    lay = np.zeros((h + 2 * pad, w + 2 * pad + 20, 4), np.float32)
    S = ui.Surf(lay.shape[1], lay.shape[0], lay)
    x0 = pad + (20 if side == 'in' else 0)
    y0 = pad
    colr = hexl('#2C1C16') if side == 'in' else hexl('#5A1A0E')
    colr2 = hexl('#24160F') if side == 'in' else hexl('#46110A')
    sh = np.zeros(lay.shape[:2], np.float32)
    a, X0, Y0 = S.rrect_mask(x0, y0 + 4, w, h, 30)
    sh[Y0:Y0 + a.shape[0], X0:X0 + a.shape[1]] = a
    sh = cv2.GaussianBlur(sh, (0, 0), 6) * 0.45
    lay[..., 3] = sh
    a, X0, Y0 = S.rrect_mask(x0, y0, w, h, 30)
    body = np.zeros(lay.shape[:2], np.float32)
    body[Y0:Y0 + a.shape[0], X0:X0 + a.shape[1]] = a
    if tail:
        tm_ = np.zeros(lay.shape[:2], np.uint8)
        if side == 'in':
            pts = np.array([[x0 + 30, y0], [x0 - 18, y0], [x0 + 6, y0 + 26]], np.float32)
        else:
            pts = np.array([[x0 + w - 30, y0], [x0 + w + 18, y0], [x0 + w - 6, y0 + 26]], np.float32)
        cv2.fillPoly(tm_, [np.round(pts * 16).astype(np.int32)], 255, cv2.LINE_AA, shift=4)
        body = np.maximum(body, tm_.astype(np.float32) / 255)
    yy = np.arange(lay.shape[0], dtype=np.float32)[:, None]
    g = np.clip((yy - y0) / h, 0, 1)
    cc = colr * (1 - g[..., None]) + colr2 * g[..., None]
    lay[..., :3] = lay[..., :3] * (1 - body[..., None]) + cc * body[..., None]
    lay[..., 3] = np.maximum(lay[..., 3] * (1 - body), body)
    S.sheen(x0 + 1, y0 + 1, w - 2, h - 2, 29, 0.035, 0.0, 0.4)
    uput(lay, msg, BODY_PX, x0 + 30, y0 + 68, 'body', 'IVORY', 'ls')
    xr = x0 + w - 22
    if side == 'out':
        for dxk in (0, 12):                          # GOLD double tick
            pts = np.array([[xr - 34 + dxk, y0 + 78], [xr - 27 + dxk, y0 + 86], [xr - 13 + dxk, y0 + 68]], np.float32)
            mm = np.zeros(lay.shape[:2], np.uint8)
            cv2.polylines(mm, [np.round(pts * 16).astype(np.int32)], False, 255, 3, cv2.LINE_AA, shift=4)
            S.fill(mm.astype(np.float32) / 255, 0, 0, C('GOLD', 1.2), 1.0)
        xr -= 46
    uput(lay, tm, 26, xr, y0 + 88, 'body', 'ASH', 'rs')
    return ro(lay), w, h, x0, y0


def phone_screen(t):
    """S8 phone screen at t (720 x 1560, opaque linear RGBA): the client thread, bubbles pop f490 / f504, typing
    dots from f510, the list scrolls up as messages arrive. Screen brightness drives the A7 spill pass."""
    f = t * FPS
    bg, ov = _chrome()
    img = np.empty((PH_H, PH_W, 4), np.float32)
    img[..., :3] = bg
    img[..., 3] = 1.0
    bottom = PH_H - 176
    items = []
    for side, msg, tm, pf in THREAD:
        if pf is not None and f < pf - 0.5:
            continue
        items.append((side, msg, tm, pf))
    typing = f >= TYPING_F - 0.5
    gap = 14
    y = bottom
    rows = []
    if typing:
        u = ease('out_cubic', (f - TYPING_F + 1) / 5.0)
        rows.append(('typing', None, None, u, y))
        y -= (BUB_H + gap) * u
    for side, msg, tm, pf in reversed(items):
        u = 1.0 if pf is None else ease('out_cubic', (f - pf + 1) / 5.0)
        rows.append((side, msg, tm, u, y))
        y -= (BUB_H + gap) * u
    # date chip above the oldest message
    chip_y = y - 60
    if chip_y > 230:
        a = 0.95
        uput_chip = utext('Today', 26.0, 'ui_medium', 'ASH')
        S = ui.Surf(PH_W, PH_H, img)
        S.rrect(PH_W / 2 - 62, chip_y - 22, 124, 44, 22, hexl('#2A1A15'), a)
        uput(img, 'Today', 26, PH_W / 2, chip_y, 'ui_medium', 'ASH', 'mm')
    prev_side = None
    for side, msg, tm, u, yb in reversed(rows):
        if side == 'typing':
            spr, w, h, x0, y0 = typing_bubble()
            _draw_msg(img, spr, 'in', yb, u, w, h, x0, y0)
            for i in range(3):
                ph_ = (t * 1.4 - i * 0.18) % 1.0
                s_ = 0.7 + 0.3 * max(0.0, math.sin(math.pi * min(1.0, ph_ * 2)))
                o_ = 0.45 + 0.55 * max(0.0, math.sin(math.pi * min(1.0, ph_ * 2)))
                K.draw(img, _typing_dot(), 24 + 34 + 30 * i, yb - h / 2, scale=s_ * (0.86 + 0.14 * u), opacity=u * o_)
            prev_side = 'in'
            continue
        spr, w, h, x0, y0 = msg_bubble(side, msg, tm, prev_side != side)
        _draw_msg(img, spr, side, yb, u, w, h, x0, y0)
        prev_side = side
    over(img, np.array(ov))
    img[..., 3] = 1.0
    return img


@functools.lru_cache(maxsize=1)
def typing_bubble():
    """Incoming 'typing' pill (no tail: same sender as the message above), 128 x BUB_H."""
    w, h, pad = 128, BUB_H, 30
    lay = np.zeros((h + 2 * pad, w + 2 * pad + 20, 4), np.float32)
    S = ui.Surf(lay.shape[1], lay.shape[0], lay)
    x0, y0 = pad + 20, pad
    S.rrect(x0, y0 + 4, w, h, 30, hexl('#000000'), 0.0)
    a, X0, Y0 = S.rrect(x0, y0, w, h, 30, hexl('#2C1C16'), 1.0)
    S.sheen(x0 + 1, y0 + 1, w - 2, h - 2, 29, 0.035, 0.0, 0.4)
    return ro(lay), w, h, x0, y0


@functools.lru_cache(maxsize=1)
def _typing_dot():
    return ro(K.disc(8, C('ASH', 1.0)))


def _draw_msg(img, spr, side, y_bottom, u, w, h, x0, y0):
    if u <= 1e-3:
        return
    sc = 0.86 + 0.14 * ease('out_back', u)
    if side == 'in':
        ax, ay = x0 / spr.shape[1], (y0 + h) / spr.shape[0]
        K.draw(img, spr, 24, y_bottom, scale=sc, anchor=(ax, ay), opacity=min(1.0, u * 2))
    else:
        ax, ay = (x0 + w) / spr.shape[1], (y0 + h) / spr.shape[0]
        K.draw(img, spr, PH_W - 24, y_bottom, scale=sc, anchor=(ax, ay), opacity=min(1.0, u * 2))


@functools.lru_cache(maxsize=1)
def _phone_body():
    """2D phone (fallback for A7): bead-blasted frame, black glass bezel, dynamic island, buttons, edge light."""
    sw, sh = PH_W, PH_H
    bez = 22
    w, h = sw + 2 * bez, sh + 2 * bez
    pad = 60
    lay = np.zeros((h + 2 * pad, w + 2 * pad, 4), np.float32)
    S = ui.Surf(lay.shape[1], lay.shape[0], lay)
    # shadow
    a, X0, Y0 = S.rrect_mask(pad + 10, pad + 26, w, h, 112)
    sh_ = np.zeros(lay.shape[:2], np.float32)
    sh_[Y0:Y0 + a.shape[0], X0:X0 + a.shape[1]] = a
    lay[..., 3] = cv2.GaussianBlur(sh_, (0, 0), 26) * 0.7
    # side buttons
    S.rrect(pad - 5, pad + 300, 8, 90, 3, hexl('#3A3A3C', 0.8), 1.0)
    S.rrect(pad - 5, pad + 410, 8, 90, 3, hexl('#3A3A3C', 0.8), 1.0)
    S.rrect(pad + w - 3, pad + 360, 8, 140, 3, hexl('#3A3A3C', 0.8), 1.0)
    # frame (aluminium) + glass
    a, X0, Y0 = S.rrect_grad(pad, pad, w, h, 112, hexl('#5A5A5E', 0.9), hexl('#1E1E20', 0.9), -35, 1.0)
    S.rrect(pad + 5, pad + 5, w - 10, h - 10, 107, hexl('#050505'), 1.0)
    S.stroke_rrect(pad + 1, pad + 1, w - 2, h - 2, 111, 1.6, C('IVORY', 0.35), 1.0,
                   weight=lambda xs, ys: np.clip(1.2 - (xs - pad) / w - (ys - pad) / h * 0.6, 0.1, 1))
    S.stroke_rrect(pad + 1, pad + 1, w - 2, h - 2, 111, 2.0, C('FLAME', 0.8), 1.0,
                   weight=lambda xs, ys: np.clip((xs - pad) / w + (ys - pad) / h - 1.1, 0, 1))
    return ro(lay), pad + bez


@functools.lru_cache(maxsize=1)
def _screen_mask():
    return K.rrect_alpha(PH_W, PH_H, 92.0, 0)


def phone_mock(cv, t, cx=540.0, cy=980.0, scale=0.78, rot=-8.0, screen=None):
    """2D fallback for the A7 phone shot: the phone body with phone_screen(t) inside (+ island, glass glint)."""
    body, off = _phone_body()
    scr = phone_screen(t) if screen is None else screen
    full = np.array(body, copy=True)
    m = _screen_mask()
    s = np.empty_like(scr)
    s[..., :3] = scr[..., :3] * m[..., None]
    s[..., 3] = m
    reg = full[off:off + PH_H, off:off + PH_W]
    over(reg, s)
    S = ui.Surf(full.shape[1], full.shape[0], full)
    S.rrect(off + PH_W / 2 - 100, off + 26, 200, 56, 28, hexl('#000000'), 1.0)   # dynamic island
    S.circle(off + PH_W / 2 + 68, off + 54, 9, hexl('#0E1218'), 1.0)
    # glass glint
    hh, ww = full.shape[:2]
    yy, xx = np.mgrid[0:hh, 0:ww].astype(np.float32)
    d = (xx * 0.8 - yy * 0.6) / ww
    gl = np.exp(-((d + 0.05) / 0.10) ** 2) * 0.05
    msk = np.zeros((hh, ww), np.float32)
    msk[off:off + PH_H, off:off + PH_W] = m
    full[..., :3] += (gl * msk)[..., None] * C('IVORY')
    K.draw(cv, full, cx, cy, scale=scale, rot=rot)


# ============================================================================================== small pieces
B0_C = (790.0, 300.0)


@functools.lru_cache(maxsize=1)
def anach_spr():
    """B0 / B1: glass pill 380 x 96, avatar disc 'C', 'Client' / 'thoda left...'."""
    w, h = 380, 96
    p = glass(w, h, 48.0, rim=0.8, glow=0.8, shadow=0.7)
    f = p.face.copy()
    pd = p.pad
    S = ui.Surf(f.shape[1], f.shape[0], f)
    a, X0, Y0 = S.circle(pd + 50, pd + h / 2, 32, hexl('#3A241C'))
    S.ring(pd + 50, pd + h / 2, 32, 2.0, C('FLAME', 1.1))
    uput(f, 'C', 34, pd + 50, pd + h / 2, 'ui_bold', 'IVORY', 'mm')
    uput(f, 'Client', 26, pd + 98, pd + 40, 'ui_bold', 'ASH', 'ls')
    uput(f, 'thoda left...', 34, pd + 98, pd + 76, 'body', 'IVORY', 'ls')
    S.circle(pd + w - 30, pd + 30, 6, C('FLAME', 1.4))
    return ui.derive_panel(p, f)


def anachronism(cv, t, f0, f1=None, fade=None, cx=None, cy=None):
    """Pop the B0 / B1 bubble at f0 (POP spring from the right side), exit in_cubic 3 f from f1;
    fade = extra opacity factor (B1 rides the outro exit)."""
    f = t * FPS
    if f < f0 - 0.5:
        return
    cx = B0_C[0] if cx is None else cx
    cy = B0_C[1] if cy is None else cy
    k = 0.55 + 0.45 * X.spring(max(0.0, t - F(f0) + HALF), 'POP')
    op = ease('out_cubic', (f - f0 + 1) / 2.0)
    if f1 is not None:
        op *= 1 - ease('in_cubic', (f - f1) / 3.0)
    if fade is not None:
        op *= fade
    if op > 1e-3:
        anach_spr().draw(cv, cx + (1 - k) * 120, cy, scale=k, opacity=op)


def hook_b(cv, t):
    """S1B (hook B, f0-f71): viewer (centre y 1180) with the title nudging 540 -> 538 on f9 + '-2 px' flash, the
    client bubble B0b mid-pop at f0 (y 800). The snow tear (snow_tear) wipes it f62-f71."""
    f = t * FPS
    xv = 540.0 - 2.0 * ease('out_cubic', (f - 9 + 0.5) / 3.0)
    delta = ('-2 px', 1.0 - ease('in_cubic', (f - 15) / 4.0)) if 9 <= f < 19 else None
    viewer(cv, t, xv, 2 if f >= 9 else 1, ghost=1.0, gdir_v=1.0, cx=540, cy=1180, delta=delta,
           readout_flash=(1.0 - ease('out_cubic', (f - 9) / 6.0)) if f >= 9 else 0.0)
    bubble(cv, 'thoda left...', 470, 120, 520, 800, t, -0.10, None, body_px=40)


def snow_tear(cv, t, f0=62, f1=72):
    """2D snow tear wipe (hook B f62-f71): a widening band of warm snow + displaced rows sweeping top -> bottom."""
    f = t * FPS
    if f < f0 - 0.5 or f >= f1:
        return
    u = ease('in_cubic', (f - f0 + 0.5) / float(f1 - f0))
    edge = int(H * u)
    rng = _rng(f, 21)
    sn = cv2.resize(np.array(_snow_tile(int(f) % 4)), (W, H), interpolation=cv2.INTER_LINEAR)
    mix = np.clip((edge + 120 - np.arange(H)) / 240.0, 0, 1)[:, None] * 0.95
    for _ in range(9):
        y = int(rng.integers(0, H - 40))
        hgt = int(rng.integers(10, 60))
        cv[y:y + hgt] = np.roll(cv[y:y + hgt], int(rng.uniform(-80, 80) * u), axis=1)
    cv[..., :3] = cv[..., :3] * (1 - mix[..., None]) + (sn * 1.1)[..., None] * SNOW * mix[..., None]
    cv[..., 3] = np.maximum(cv[..., 3], mix)


SPLIT_WORDS = [(576, 'THODA LEFT...', 'thoda left...'), (594, 'THODA RIGHT...', 'thoda right...'),
               (612, 'NAHI, PEHLE WALA!', 'nahi, pehle wala!'), (630, 'THODA SA...', 'thoda sa...')]
SPLIT_Y = 960


@functools.lru_cache(maxsize=2)
def era_chip(label):
    return ui.chip(label, sel=1.0, look=LOOK, size=34, h=60, pad_x=26,
                   grad=('AMBER', 'FLAME') if label == 'TAB' else ('FLAME', 'RED'))


@functools.lru_cache(maxsize=1)
def divider_spr():
    lay = np.zeros((60, W, 4), np.float32)
    lay[29:31, :, :3] = C('FLAME', 1.6)
    lay[29:31, :, 3] = 1.0
    xx = np.arange(W, dtype=np.float32)
    fall = np.clip(1.0 - np.abs(xx - W / 2) / (W * 0.62), 0.2, 1.0)
    lay *= np.concatenate([np.ones((60, W, 3)), np.ones((60, W, 1))], 2) * 1.0
    lay[..., :3] *= fall[None, :, None]
    return ro(K.glow(lay, C('FLAME'), sigmas=(4, 14, 34), strength=0.9))


def split_ui(cv, t, xv=None):
    """S10 overlays (f576-f647): FLAME divider y 960, TAB / AB chips, far words in the top half (jw_caps 56 ASH
    at y 860 with an echo), the mini viewer (centre 540, 1330; title X from the client clock) and the client
    bubble (centre 590, 1040) saying the same words on the same frame."""
    f = t * FPS
    if f < 575.5 or f >= 648:
        return
    xv_, ver, dirn = client(t)
    xv = xv_ if xv is None else xv
    viewer(cv, t, xv, ver, ghost=1.0, gdir_v=-dirn, cx=540, cy=1330, scale=840 / VIEW_W, handles=True)
    K.draw(cv, divider_spr(), 540, SPLIT_Y)
    ui.place(cv, era_chip('TAB'), 150, 290)
    ui.place(cv, era_chip('AB'), 150, 1010)
    cur = [w for w in SPLIT_WORDS if f >= w[0] - 0.5]
    if not cur:
        return
    fw, caps, low = cur[-1]
    tt = t - F(fw)
    # top: the far voice from the roof's downstairs (rise 900 -> 860, echo)
    spr = tx(caps, 'jw_caps', 56, 'ASH')
    scrim(cv, 540, 858, spr.w + 120, spr.h + 60, 0.5)
    for dl, dy, a in ((F(6), -12.0, 0.3), (0.0, 0.0, 1.0)):
        u = ease('out_cubic', (tt - dl + HALF) / F(6))
        if u > 0:
            spr.draw(cv, 540, 900 - 40 * u + dy, opacity=a * ease('inout_sine', (tt - dl + HALF) / F(3)), snap=False)
    # bottom: the same words in the client's bubble
    bubble(cv, low, 520, 104, 590, 1040, t, F(fw), None, body_px=40)


# ============================================================================================== outro + cover
OUTRO = dict(question='Aap ke ghar antenna kaun ghumata tha?', key='Papa, bhai ya aap?', dur=4.2)
T_END = 882 / 30


@functools.lru_cache(maxsize=1)
def outro():
    return PO.ProfileOutro(OUTRO['question'], key=OUTRO['key'], dur=OUTRO['dur'])


def outro_layer(cv, t):
    """Outro card (f882-f1007) + B1 bubble (f990, exits with the card)."""
    card = outro()
    card.draw(cv, t, T_END)
    if t >= F(990) - HALF:
        t_last = T_END + card.dur - 1.0 / FPS
        exf = 1.0 - ease('in_cubic', (t - (T_END + card.dur - card.exit_dur)) / (t_last - (T_END + card.dur
                                                                                          - card.exit_dur)))
        anachronism(cv, t, 990, None, fade=exf)


GRID_CROP = (0, 240, 1080, 1680)         # 3:4 grid crop (x0, y0, x1, y1)
COVER_SPLIT = 0.54                       # picture fraction of the tear (screen y ~ 1010)


def cover_picture():
    return tv_picture(F(40), 1.0, 1.0, split=COVER_SPLIT)


@functools.lru_cache(maxsize=1)
def _cover_parts():
    return dict(caps=T.render('THODA', 'jw_caps', px=96), key=T.render('left...', 'jw_key_core', px=250),
                halo=T.render('left...', 'jw_key_halo', px=250), bas=T.render('BAS BAS!', 'jw_caps_bold', px=150))


def cover(cv):
    """Cover overlay (SHOTS 5 / c): THODA (caps 96, y 390) + left... (key 250, y 565) + underline, BAS BAS!
    (caps_bold 150, y 1500), the client bubble (790, 296), @jawad_mp4 at y 1590; SMOKE scrims where the type
    meets the CRT glass. Everything inside GRID_CROP."""
    P = _cover_parts()
    scrim(cv, 540, 470, 900, 360, 0.5)
    scrim(cv, 540, 1505, 900, 200, 0.6)
    P['caps'].draw(cv, 540, 390)
    P['halo'].draw(cv, 540, 565)
    P['key'].draw(cv, 540, 565)
    kw = P['key'].w
    uln = int(min(980, kw * 1.08 + 40))
    J.underline(uln, thick=6.5).draw(cv, 540 - uln / 2, 565 + P['key'].h / 2 + 250 * 0.13, u=1.0)
    P['bas'].draw(cv, 540, 1500)
    anach_spr().draw(cv, 790, 296, scale=0.96)
    J.signature(cv, 540, 1595)


def grid_crop(img):
    x0, y0, x1, y1 = GRID_CROP
    return img[y0:y1, x0:x1]


# ============================================================================================== selftest
def _bg(t, kind='void'):
    """Selftest backdrops only (the real worlds are the motion designer's)."""
    cv = K.background(LOOK, t, bokeh=0.5)
    if kind == 'roof':
        yy = np.arange(H, dtype=np.float32)[:, None, None]
        v = np.clip(yy / 1300, 0, 1)
        sky = hexl('#2A1408', 0.7) * (1 - v) + hexl('#D88232', 0.42) * v ** 1.4
        cv[..., :3] = cv[..., :3] * 0.4 + sky
        cv[1300:, :, :3] = hexl('#4A3A30', 0.35)                  # parapet
        cv[1290:1310, :, :3] = hexl('#8E8478', 0.4)
        aa_line(cv, (620, 1310), (650, 300), 9, hexl('#1A1210', 0.9))
        aa_line(cv, (300, 420), (980, 380), 6, hexl('#1A1210', 0.9))
        for k in range(9):
            x = 330 + 75 * k
            aa_line(cv, (x, 400 - (k * 2) - 110 + 6 * k), (x + 2, 400 - (k * 2) + 110 - 6 * k), 4, hexl('#1A1210', 0.9))
    if kind == 'dark':
        cv[..., :3] *= 0.55
    return cv


def _finish(cv, t, rays=0.0):
    G.finish(cv, LOOK, t, rays=rays)
    return K.to_srgb8(cv, t)


def _save(name, u8):
    os.makedirs(SELF_DIR, exist_ok=True)
    p = os.path.join(SELF_DIR, name + '.png')
    cv2.imwrite(p, cv2.cvtColor(u8, cv2.COLOR_RGB2BGR))
    return p


def _crt_frame(t, pic=None, dim=1.0):
    cv = _bg(t, 'dark')
    crt_mock(cv, tv_picture_at(t) if pic is None else pic)
    if dim < 1:
        cv[..., :3] *= dim
    return cv


def check_script():
    """Every caption / UI / outro string here must match script.json (words are the script writer's)."""
    d = json.load(open(SCRIPT_JSON))
    bad = []
    for c in d['captions']:
        cid = c['id']
        texts = [p[0] for p in c['parts']]
        if cid == 'H1b':
            if 'right...' not in texts:
                bad.append(cid)
            continue
        if cid in CAPS:
            mine = [p[1] for p in CAPS[cid]['parts']]
        elif cid in FAR:
            mine = [FAR[cid]['text']]
        else:
            bad.append('missing ' + cid)
            continue
        if mine != texts:
            bad.append('%s: %r != %r' % (cid, mine, texts))
        if tuple(c['f']) != tuple(CAPS[cid]['f'] if cid in CAPS else FAR[cid]['f']):
            bad.append('%s frames %r' % (cid, c['f']))
    o = d['outro']
    if o['question'] != OUTRO['question'] or o['key'] != OUTRO['key'] or abs(o['dur'] - OUTRO['dur']) > 1e-6:
        bad.append('outro')
    if o['t_end_frame'] != 882:
        bad.append('outro t_end')
    return bad


def selftest():
    import time
    os.makedirs(SELF_DIR, exist_ok=True)
    bad = check_script()
    print('script.json check:', 'OK' if not bad else bad)
    shots = []
    tm = {}

    def run(name, fn, f, rays=0.0):
        t = F(f)
        t0 = time.perf_counter()
        cv = fn(t)
        tm[name] = round((time.perf_counter() - t0) * 1e3)
        shots.append((name, _save(name, _finish(cv, t, rays))))

    def crt_caps(hook='A'):
        def fn(t):
            cv = _crt_frame(t)
            captions(cv, t, hook=hook)
            if 63 <= t * FPS < 72:
                anachronism(cv, t, 63)
            return cv
        return fn

    for f in (0, 8, 22, 40, 58, 66):
        run('s1_hookA_f%03d' % f, crt_caps(), f)

    def hb(t):
        cv = _bg(t, 'void')
        hook_b(cv, t)
        captions(cv, t, hook='B')
        snow_tear(cv, t)
        return cv
    for f in (0, 12, 66):
        run('s1B_hookB_f%03d' % f, hb, f)

    def roof(t):
        cv = _bg(t, 'roof')
        captions(cv, t)
        return cv
    for f in (85, 115, 150, 175):
        run('s2_roof_f%03d' % f, roof, f, rays=0.26)

    def crt_room(t):
        cv = _crt_frame(t)
        captions(cv, t)
        return cv
    for f in (210, 232):
        run('s3_crt_f%03d' % f, crt_room, f)

    def clamp(t):
        cv = _bg(t, 'dark')
        captions(cv, t)
        return cv
    for f in (275, 292):
        run('s4_clamp_f%03d' % f, clamp, f)
    for f in (320, 362):
        run('s5_lock_f%03d' % f, crt_room, f)
    run('s6_roofwind_f400', roof, 400, rays=0.26)
    run('s6_roofwind_f424', roof, 424, rays=0.26)

    def edit(t, tilt=True):
        cv = _bg(t, 'void')
        lay = np.zeros((H, W, 4), np.float32)
        edit_ui(lay, t)
        if tilt:
            lay = plane_warp(lay)
        over(cv, lay)
        captions(cv, t)
        return cv
    for f in (450, 472, 479, 560, 574, 660, 700, 717):
        run('s7_edit_f%03d' % f, edit, f)

    def phone(t):
        cv = _bg(t, 'dark')
        phone_mock(cv, t)
        return cv
    for f in (500, 515):
        run('s8_phone_f%03d' % f, phone, f)
    sc = phone_screen(F(515))
    shots.append(('s8_phone_screen_raw', _save('s8_phone_screen_raw', K.to_srgb8(sc.copy(), 0.0, dither=False))))

    def split(t):
        cv = _bg(t, 'void')
        top = _bg(t, 'roof')
        cv[:SPLIT_Y] = top[:SPLIT_Y]
        split_ui(cv, t)
        return cv
    for f in (580, 615):
        run('s10_split_f%03d' % f, split, f)

    def sunset(t):
        cv = _bg(t, 'roof')
        cv[..., :3] *= np.float32([1.0, 0.75, 0.55])
        captions(cv, t)
        return cv
    for f in (770, 800, 850):
        run('s12_payoff_f%03d' % f, sunset, f, rays=0.26)

    def loop(t):
        cv = _crt_frame(t)
        outro_layer(cv, t)
        return cv
    for f in (930, 995, 1004):
        run('s13_outro_f%04d' % f, loop, f)

    # TV picture states (raw 4:3)
    for s_ in (0.0, 0.5, 1.0):
        pic = tv_picture(F(100), s_, 1.0, shimmer=0.5 if s_ == 0 else None)
        shots.append(('tv_sig%.1f' % s_, _save('tv_sig%.1f' % s_, K.to_srgb8(pic.copy(), 0.0))))
    # cover + grid crop
    cv = _bg(0.0, 'dark')
    crt_mock(cv, cover_picture())
    cover(cv)
    u8 = _finish(cv, 0.0)
    shots.append(('cover', _save('cover', u8)))
    g = grid_crop(u8)
    shots.append(('cover_grid_3x4', _save('cover_grid_3x4', np.ascontiguousarray(g))))
    small = cv2.resize(g, (210, 280), interpolation=cv2.INTER_AREA)
    shots.append(('cover_grid_210px', _save('cover_grid_210px', small)))
    # phone-size contact sheet (360 px wide frames)
    frames = [p for n, p in shots if not n.startswith(('tv_', 'cover_grid', 's8_phone_screen'))]
    cols = 6
    tw_, th_ = 360, 640
    rows = int(math.ceil(len(frames) / cols))
    sheet = np.zeros((rows * (th_ + 30), cols * tw_, 3), np.uint8)
    for i, p in enumerate(frames):
        im = cv2.imread(p)
        im = cv2.resize(im, (tw_, th_), interpolation=cv2.INTER_AREA)
        r, c = divmod(i, cols)
        sheet[r * (th_ + 30) + 30:r * (th_ + 30) + 30 + th_, c * tw_:(c + 1) * tw_] = im
        cv2.putText(sheet, os.path.basename(p)[:-4], (c * tw_ + 6, r * (th_ + 30) + 21), cv2.FONT_HERSHEY_SIMPLEX,
                    0.5, (200, 200, 200), 1, cv2.LINE_AA)
    cv2.imwrite(os.path.join(SELF_DIR, '_contact_360px.png'), sheet)
    print('timings ms (draw only):', tm)
    print('->', SELF_DIR, len(shots), 'stills + _contact_360px.png')
    return bad


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] in ('selftest', '--selftest'):
        b = selftest()
        sys.exit(1 if b else 0)
    else:
        print(__doc__)
