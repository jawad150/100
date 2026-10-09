"""beta_tum_karte_kya_ho_ui.py - UI builders of Reel 4 / C02 "Beta, tum karte kya ho?" (motion-timeline-builder).

Geometry + strings: brand_reels/design/reels/beta_tum_karte_kya_ho/BRIEF.md r2 6.3-6.5 (HANDOFF r3 wins where they
differ). Every sprite is built once (lru_cache); every draw is a pure function of its arguments (screen px, linear
premultiplied float32 canvases). The layout proof (layout_proof_r2.py) was lost, so everything here is re-implemented
from the brief's numbers.

    hook_ui(cv, tau, sender, ...)        "Mummy"/"Nani" chip + typing pill (-> H1 bubble for Mummy) + POV label (S0/S11/S12)
    Card(...).draw(cv, t, ...)            the translate card (S1 S2 S4 S5): header, fields, small / big window
    killer(cv, t)                         "Achha. / Naukri kab lagegi?" bubble (S5 -> S6 overlay)
    payoff(cv, t)                         MERA BETA / cinema / BANATA HAI bubble (S9 -> S10 overlay)
    skip_scene(cv, t)                     S7 table + face-down phone + edge glow + chip / count pill
    chat(cv, t, thumb)                    S8 "Khandaan" panel, message stack, forwarded reel bubble, typing pill
    dot3_pose(t)                          M1's circle in S8 (x, y, r)
    make_thumb(cover_linear)              REEL_THUMB 300x533 from this reel's own cover canvas
"""
import functools
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import jawad_kit                                  # noqa: F401,E402  FIRST
from jawad_kit import K, T, J, ui                 # noqa: E402
import jawad_tx as X                              # noqa: E402

import cv2                                        # noqa: E402
import numpy as np                                # noqa: E402

LOOK = 'gold_hour'
FPS = K.FPS
HALF = 0.5 / FPS

# ---------------------------------------------------------------------------------------------- rects (BRIEF 6.4)
PILL = (147, 280, 467, 420)          # typing pill (frame 0 / Nani)
BUBBLE_H = (147, 280, 933, 740)      # hook bubble (H1)
CHIP_R = (147, 232, 320, 272)        # sender chip area
POV_R = (600, 235, 1000, 270)
CARD = (90, 296, 990, 1176)          # translate card / chat panel
CARD_C = (540.0, 736.0)
WIN_SMALL = (130, 836, 950, 1136)
WIN_BIG = (110, 590, 970, 1160)
INPUT_F = (130, 462, 950, 562)
OUTPUT_F = (130, 666, 950, 806)
KILLER_0 = (150, 640, 930, 880)
KILLER_1 = (150, 280, 930, 520)
PAYOFF_R = (147, 280, 933, 790)
CHIP_PILL = (310, 302, 770, 378)     # S7 chip / count pill
PHONE_BOX = (316, 586, 775, 1223)
SUN_BOX = (430, 1150, 650, 1370)


def C(name, k=1.0):
    return np.asarray(K.C[name], np.float32) * np.float32(k)


def hexl(h, k=1.0):
    return np.asarray(K.hexlin(h), np.float32)[:3] * np.float32(k)


def fidx(t):
    return int(math.floor(t * FPS + 0.5))


# ---------------------------------------------------------------------------------------------- primitives
@functools.lru_cache(maxsize=128)
def glass(w, h, r=44.0, rim=1.0, glow=1.0, shadow=1.0, tint=None, tint_a=None):
    kw = {}
    if tint is not None:
        kw['tint'] = tint
    if tint_a is not None:
        kw['tint_a'] = tint_a
    return ui.glass_card(int(round(w)), int(round(h)), r=float(r), look=LOOK, rim=rim, glow=glow, shadow=shadow, **kw)


def draw_glass(cv, rect, r=44.0, xf=None, opacity=1.0, frost=None, scale=1.0, **kw):
    """Glass card on screen rect (x0, y0, x1, y1); xf = Xf transform of the parent (card float / push)."""
    x0, y0, x1, y1 = rect
    p = glass(round(x1 - x0), round(y1 - y0), r, **kw)
    cx, cy = (x0 + x1) / 2.0, (y0 + y1) / 2.0
    s = scale
    if xf is not None:
        cx, cy = xf.p(cx, cy)
        s = s * xf.s
    p.draw(cv, cx, cy, scale=s, opacity=opacity, frost=frost)


@functools.lru_cache(maxsize=1024)
def tx(s, style, px, fill=None):
    if fill is None:
        return T.render(s, style, px=px)
    return T.render(s, style, px=px, fill=fill)


def text(cv, s, style, px, x, y, anchor=(0.0, 0.5), opacity=1.0, fill=None, xf=None, scale=1.0, **kw):
    if opacity <= 1e-4 or not s:
        return
    if xf is not None:
        x, y = xf.p(x, y)
        scale = scale * xf.s
    tx(s, style, px, fill).draw(cv, x, y, anchor=anchor, opacity=opacity, scale=scale, **kw)


def width(s, style, px):
    return T.measure(s, style, px=px)[0]


class Xf:
    """Screen transform of a card and its contents: p' = c + s (p - c) + (dx, dy)."""

    def __init__(self, s=1.0, dx=0.0, dy=0.0, c=CARD_C):
        self.s, self.dx, self.dy, self.c = float(s), float(dx), float(dy), c

    def p(self, x, y):
        return (self.c[0] + self.s * (x - self.c[0]) + self.dx, self.c[1] + self.s * (y - self.c[1]) + self.dy)

    def rect(self, R):
        x0, y0 = self.p(R[0], R[1])
        x1, y1 = self.p(R[2], R[3])
        return (x0, y0, x1, y1)


ID = Xf()


def solid(mask, col):
    """Premultiplied RGBA sprite from a coverage mask and a linear colour."""
    m = np.asarray(mask, np.float32)
    out = np.zeros(m.shape + (4,), np.float32)
    out[..., :3] = m[..., None] * np.asarray(col, np.float32)[:3]
    out[..., 3] = m
    return out


def over(dst, src):
    """dst = src over dst (premultiplied, same shape), in place."""
    a = src[..., 3:4]
    dst *= (1.0 - a)
    dst += src
    return dst


def ro(a):
    a = np.ascontiguousarray(a, np.float32)
    a.setflags(write=False)
    return a


@functools.lru_cache(maxsize=16)
def rr_sprite(w, h, r, col, a=1.0):
    """Flat rounded rect (colour tuple, alpha a)."""
    m = K.rrect_alpha(int(w), int(h), float(r), 2) * np.float32(a)
    return ro(solid(m, np.asarray(col, np.float32)))


@functools.lru_cache(maxsize=8)
def dot_sprite(r=14):
    return ro(K.glow(K.disc(r, C('AMBER', 2.0)), C('FLAME'), sigmas=(max(2, r * 0.3), r * 0.75), strength=0.8))


def dot_scale(tau, i):
    """BRIEF 6.3: s_i(tau) = 0.85 + 0.15 cos(2 pi (tau - 0.1 i) / 0.6)."""
    return 0.85 + 0.15 * math.cos(2.0 * math.pi * (tau - 0.1 * i) / 0.6)


def dots(cv, tau, x0, cy, pitch, r=14, opacity=1.0, scale=1.0, freeze=None, xf=None):
    spr = dot_sprite(r)
    for i in range(3):
        s = dot_scale(tau if freeze is None else freeze, i)
        x, y = x0 + pitch * i, cy
        if xf is not None:
            x, y = xf.p(x, y)
        K.draw(cv, spr, x, y, scale=s * scale * (xf.s if xf is not None else 1.0), opacity=opacity, mode='over')


# ---------------------------------------------------------------------------------------------- house type
@functools.lru_cache(maxsize=4)
def house(caps, key, underline=False):
    return J.HouseTitle(caps, key, caps_px=86, key_px=210, underline=underline)


def pov(cv, opacity=1.0):
    text(cv, 'POV · har desi ghar', 'jw_mono', 34, 1000, 252, anchor=(1.0, 0.5), opacity=0.85 * opacity,
         fill='ASH')


# ---------------------------------------------------------------------------------------------- S0 / S11 / S12 hook UI
def _lerp_rect(a, b, u):
    return tuple(a[i] + (b[i] - a[i]) * u for i in range(4))


def hook_ui(cv, tau, sender='Mummy', pop=None, pov_op=1.0):
    """Sender chip + typing pill (tau < f8) -> bubble with H1 (Mummy only, tau >= f8) + POV label.
    tau = local hook time (t in S0, t - 36.4 for Nani). pop = (t, t0): UI POP of the Nani chip + pill at t0."""
    sc, op = 1.0, 1.0
    if pop is not None:
        tt, t0 = pop
        if tt < t0 - HALF:
            return
        sc = 0.6 + 0.4 * K.spring(max(0.0, tt - t0), 2.6, 0.55)
        op = K.ramp(tt, t0 - HALF, t0 + 5.0 / FPS, 'out_cubic')
    pov(cv, pov_op)
    # chip (left x 160, cy 252)
    text(cv, sender, 'jw_body', 36, 160, 252, fill='AMBER', opacity=op)
    k = fidx(tau)
    if sender != 'Mummy' or k < 8:
        cx, cy = (PILL[0] + PILL[2]) / 2.0, (PILL[1] + PILL[3]) / 2.0
        # the pill pops about its own centre
        x0, y0, x1, y1 = PILL
        p = glass(x1 - x0, y1 - y0, 40.0)
        p.draw(cv, cx, cy, scale=sc, opacity=op)
        dx0 = 263 - cx
        for i in range(3):
            s = dot_scale(tau, i)
            K.draw(cv, dot_sprite(14), cx + (dx0 + 44 * i) * sc, cy + (350 - cy) * sc, scale=s * sc, opacity=op)
        return
    # f8-f12: pill -> bubble (out_cubic, one glass size per frame)
    u = K.EASE['out_cubic'](K.clamp((k - 8) / 4.0))
    R = _lerp_rect(PILL, BUBBLE_H, u)
    rr = 40 + 4 * u
    draw_glass(cv, tuple(round(v) for v in R), r=round(rr))
    if k <= 9:                                         # dots fade f8-f9 inside the growing pill
        fo = 1.0 - K.clamp((tau - 8 / FPS) / (2 / FPS))
        for i in range(3):
            K.draw(cv, dot_sprite(14), 263 + 44 * i, 350, scale=dot_scale(tau, i), opacity=fo)
    h1(cv, tau)


def h1(cv, tau, opacity=1.0, rise=True):
    """H1 lockup BETA, TUM / karte kya / HO? (static sprites): fade + 14 px rise f9-f12, halo flare f42."""
    h = house('BETA, TUM', 'karte kya')
    if rise:
        u = K.ramp(tau, 9 / FPS - HALF, 12 / FPS, 'out_cubic')
    else:
        u = 1.0
    if u <= 0:
        return
    op = u * opacity
    dy = 14.0 * (1 - u)
    h.caps.draw(cv, 540, 350.0 + dy, opacity=op)
    flare = K.ramp(tau, 1.25, 1.40, 'inout_sine') * (1 - K.ramp(tau, 1.40, 1.55, 'inout_sine'))
    if h.halo is not None:
        h.halo.draw(cv, 540, 518.7 + dy, opacity=op * (1.0 + 0.3 * flare))
    h.key_static.draw(cv, 540, 518.7 + dy, opacity=op)
    tx('HO?', 'jw_caps', 86).draw(cv, 540, 687.4 + dy, opacity=op)


# ---------------------------------------------------------------------------------------------- translate card
@functools.lru_cache(maxsize=1)
def card_glass():
    return glass(900, 880, 48.0)


@functools.lru_cache(maxsize=4)
def field_glass(w, h, r=24.0):
    return glass(w, h, r, rim=0.35, glow=0.2, shadow=0.5)


@functools.lru_cache(maxsize=40)
def window_glass(w, h):
    return glass(w, h, 24.0, rim=0.55, glow=0.3, shadow=0.5, tint=tuple(float(v) for v in C('NIGHT_1')), tint_a=0.92)


@functools.lru_cache(maxsize=4)
def icons():
    return dict(globe=ui.icon('globe', 44, 'AMBER', stroke=2.4),
                arrow=ui.icon('arrow_right', 44, 'FLAME', stroke=2.6),
                fwd=ui.icon('arrow_right', 28, 'ASH', stroke=2.2))


@functools.lru_cache(maxsize=4)
def caret_sprite():
    return ro(solid(np.ones((46, 3), np.float32), C('FLAME', 1.4)))


def typed(s, t, t0, t1):
    """Characters of s shown at t when typing runs t0 -> t1 (first char on t0)."""
    if t < t0 - HALF:
        return 0
    n = len(s)
    k = int(math.floor((t - t0 + HALF) / max(1e-6, (t1 - t0)) * (n - 1) + 1e-6)) + 1
    return max(0, min(n, k))


def card_body(cv, xf, opacity=1.0):
    """Glass + header + 'Aap ne kaha' + input field (the parts every card state shares)."""
    x, y = xf.p(*CARD_C)
    card_glass().draw(cv, x, y, scale=xf.s, opacity=opacity)
    ic = icons()
    gx, gy = xf.p(152, 352)
    K.draw(cv, ic['globe'], gx, gy, scale=xf.s, opacity=opacity)
    text(cv, 'Mummy translate', 'jw_body', 50, 186, 352, xf=xf, opacity=opacity)
    text(cv, 'Aap ne kaha', 'jw_mono', 34, 130, 436, fill='ASH', xf=xf, opacity=opacity)
    fx, fy = xf.p((INPUT_F[0] + INPUT_F[2]) / 2, (INPUT_F[1] + INPUT_F[3]) / 2)
    field_glass(820, 100).draw(cv, fx, fy, scale=xf.s, opacity=opacity, frost=0)


def card_input(cv, xf, s, n=None, dim=1.0, caret=False, t=0.0, opacity=1.0):
    n = len(s) if n is None else n
    shown = s[:n]
    if shown:
        text(cv, shown, 'jw_body', 46, 162, 512, xf=xf, opacity=opacity * dim)
    if caret and (int(math.floor(t * 4.0)) % 2 == 0):
        cx = 162 + (width(shown, 'jw_body', 46) if shown else 0) + 4
        x, y = xf.p(cx, 512)
        K.draw(cv, caret_sprite(), x, y, scale=xf.s, opacity=opacity)


def card_labels(cv, xf, op):
    """Arrow + 'Mummy ne suna' + output field (S1 only; fade out f135-f141)."""
    if op <= 1e-4:
        return
    ax, ay = xf.p(540, 600)
    K.draw(cv, icons()['arrow'], ax, ay, rot=90.0, scale=xf.s, opacity=op)
    text(cv, 'Mummy ne suna', 'jw_mono', 34, 130, 640, fill='ASH', xf=xf, opacity=op)
    fx, fy = xf.p((OUTPUT_F[0] + OUTPUT_F[2]) / 2, (OUTPUT_F[1] + OUTPUT_F[3]) / 2)
    field_glass(820, 140).draw(cv, fx, fy, scale=xf.s, opacity=op, frost=0)


def window_at(u):
    """Parody window rect: small (u = 0) -> big (u = 1), integer px."""
    return tuple(int(round(v)) for v in _lerp_rect(WIN_SMALL, WIN_BIG, u))


def card_window(cv, xf, R, opacity=1.0):
    x0, y0, x1, y1 = R
    cx, cy = xf.p((x0 + x1) / 2, (y0 + y1) / 2)
    window_glass(x1 - x0, y1 - y0).draw(cv, cx, cy, scale=xf.s, opacity=opacity, frost=0)


@functools.lru_cache(maxsize=4)
def scrim_sprite(w, h, r):
    return ro(solid(K.rrect_alpha(int(w), int(h), float(r), 2), C('NIGHT_0')))


def scrim(cv, R, r, a, xf=ID):
    if a <= 1e-4:
        return
    x0, y0, x1, y1 = R
    cx, cy = xf.p((x0 + x1) / 2, (y0 + y1) / 2)
    K.draw(cv, scrim_sprite(x1 - x0, y1 - y0, r), cx, cy, scale=xf.s, opacity=a)


def loading_dots(cv, t, xf, opacity=1.0):
    spr = dot_sprite(10)
    for i in range(3):
        s = dot_scale(t * 1.5, i)
        x, y = xf.p(540 - 34 + 34 * i, 875)
        K.draw(cv, spr, x, y, scale=s * xf.s, opacity=opacity)


# ---------------------------------------------------------------------------------------------- killer + payoff bubbles
def killer(cv, t):
    """S5 f378 -> S6 f458: chip + bubble + two lines; POP f378, glide f410-f419, exit f450-f458."""
    t0 = 378 / FPS
    if t < t0 - HALF or t >= 459 / FPS - HALF:
        return
    pop = 0.85 + 0.15 * X.spring(max(0.0, t - t0), 'POP')
    op = K.ramp(t, t0 - HALF, t0 + 3 / FPS, 'out_cubic')
    g = K.ramp(t, 410 / FPS, 419 / FPS, 'easy_ease')
    ex = K.ramp(t, 450 / FPS, 458 / FPS, 'in_cubic')
    op *= 1.0 - ex
    if op <= 1e-4:
        return
    dy = -360.0 * g - 20.0 * ex
    R = KILLER_0
    cx, cy = (R[0] + R[2]) / 2.0, (R[1] + R[3]) / 2.0 + dy
    xf = Xf(pop, 0.0, dy, c=((R[0] + R[2]) / 2.0, (R[1] + R[3]) / 2.0))
    glass(R[2] - R[0], R[3] - R[1], 44.0).draw(cv, cx, cy, scale=pop, opacity=op)
    text(cv, 'Mummy', 'jw_body', 36, 186, 612, fill='AMBER', xf=xf, opacity=op)
    text(cv, 'Achha.', 'jw_body', 60, 190, 712, xf=xf, opacity=op)
    text(cv, 'Naukri kab lagegi?', 'jw_body', 60, 190, 802, xf=xf, opacity=op)


def killer_rect(t):
    g = K.ramp(t, 410 / FPS, 419 / FPS, 'easy_ease')
    return (150, 640 - 360 * g, 930, 880 - 360 * g)


P_T0 = 28.0
P_OUT = 955 / FPS          # 31.8333


def payoff(cv, t):
    """f840 -> f965: Mummy chip + bubble (POP) + MERA BETA / cinema / BANATA HAI (HouseTitle + third caps line)."""
    if t < P_T0 - HALF or t >= 966 / FPS - HALF:
        return
    ex = K.ramp(t, P_OUT, 965 / FPS, 'in_cubic')
    op = K.ramp(t, P_T0 - HALF, P_T0 + 4 / FPS, 'out_cubic') * (1.0 - ex)
    if op <= 1e-4:
        return
    pop = 0.86 + 0.14 * X.spring(max(0.0, t - P_T0), 'POP')
    R = PAYOFF_R
    cx, cy = (R[0] + R[2]) / 2.0, (R[1] + R[3]) / 2.0
    glass(R[2] - R[0], R[3] - R[1], 44.0).draw(cv, cx, cy, scale=pop, opacity=op)
    text(cv, 'Mummy', 'jw_body', 36, 160, 252, fill='AMBER', opacity=op)
    house('MERA BETA', 'cinema', True).draw(cv, t, 540, 518.7, t0=P_T0, out_t0=P_OUT)
    t3 = 28.45
    if t >= t3:
        out = 1.0 - K.ramp(t, P_OUT, P_OUT + 0.35, 'in_cubic')
        uc = K.ramp(t, t3, t3 + 0.6, 'out_cubic')
        tx('BANATA HAI', 'jw_caps', 86).draw(cv, 540, 731.9 + 28 * (1 - uc),
                                              opacity=out * K.ramp(t, t3, t3 + 0.42, 'inout_sine'), blur=6 * (1 - uc))


# ---------------------------------------------------------------------------------------------- S7 time skip
@functools.lru_cache(maxsize=1)
def table_albedo():
    """Dark wood planks in table space (1400 x 2400) warped to the screen (30 deg look-down) + vignette."""
    TW, TH = 1400, 2400
    rng = np.random.default_rng(17)
    y, x = np.mgrid[0:TH, 0:TW].astype(np.float32)
    PW = 232.0
    pl = (x // PW).astype(np.int32)
    npl = int(TW // PW) + 2
    poff = rng.uniform(0, 26, npl).astype(np.float32)[pl]
    ptint = rng.uniform(-0.10, 0.10, npl).astype(np.float32)[pl]
    wn = cv2.resize(rng.standard_normal((12, 60)).astype(np.float32), (TW, TH), interpolation=cv2.INTER_CUBIC)
    wn = (wn - wn.mean()) / (wn.std() + 1e-6) * 0.45
    ring = (0.5 + 0.5 * np.sin(2 * np.pi * ((x + poff) / 26.0 + 1.6 * wn))) ** 2.2
    fib = cv2.resize(rng.standard_normal((TH // 24, TW // 2)).astype(np.float32), (TW, TH),
                     interpolation=cv2.INTER_LINEAR) * 0.10
    v = np.clip(0.30 + 0.55 * ring + fib + ptint, 0, 1)
    c0, c1 = hexl('#1A0F0A'), hexl('#3A2416')
    alb = c0[None, None, :] * (1 - v[..., None]) + c1[None, None, :] * v[..., None]
    seam = (np.mod(x, PW) < 3.0).astype(np.float32)
    alb *= (1.0 - 0.8 * seam)[..., None]
    # one short pale scratch lower-left (the uncomposed element)
    sc = np.zeros((TH, TW), np.uint8)
    pts = np.array([[250 + 6 * i + 3 * math.sin(i * 0.4), 1900 - 9 * i] for i in range(38)], np.int32)
    cv2.polylines(sc, [pts], False, 255, 3, cv2.LINE_AA)
    sc = cv2.GaussianBlur(sc.astype(np.float32) / 255.0, (0, 0), 1.0)
    alb += sc[..., None] * C('ASH', 0.10)[None, None, :]
    src = np.float32([[0, 0], [TW, 0], [TW, TH], [0, TH]])
    dst = np.float32([[70, -90], [1010, -90], [1330, 2010], [-250, 2010]])
    M = cv2.getPerspectiveTransform(src, dst)
    scr = cv2.warpPerspective(alb, M, (K.W, K.H), flags=cv2.INTER_AREA, borderMode=cv2.BORDER_REFLECT)
    scr = cv2.GaussianBlur(scr, (0, 0), 0.6)
    yy, xx = np.mgrid[0:K.H, 0:K.W].astype(np.float32)
    r2 = ((xx - 540) / 620.0) ** 2 + ((yy - 960) / 1050.0) ** 2
    vig = np.maximum(0.25, 1.0 - 0.55 * r2)
    return ro(scr * vig[..., None])


@functools.lru_cache(maxsize=1)
def _band_grid():
    h, w = K.H // 4, K.W // 4
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    return xx * 4 + 2, yy * 4 + 2


def band_mask(t):
    """Window-light band (340 px at 28 deg, 60 px soft edges, one 9 px mullion shadow 40 px inside), centre line
    sweeping x 340 -> 740 over f504-f587 (linear); full-res float32."""
    xs, ys = _band_grid()
    u = K.clamp((t - 504 / FPS) / ((587 - 504) / FPS))
    xc = 340.0 + 400.0 * u
    a = math.radians(28.0)
    d = (xs - xc) * math.cos(a) + (ys - 960.0) * math.sin(a)
    half = 170.0
    m = np.clip((half - np.abs(d)) / 60.0 + 0.5, 0, 1)
    m = m * m * (3 - 2 * m)
    mull = np.clip(1.0 - np.abs(d - (-half + 40.0)) / 4.5, 0, 1)
    m = m * (1.0 - 0.85 * mull)
    return cv2.resize(m.astype(np.float32), (K.W, K.H), interpolation=cv2.INTER_LINEAR)


GOLDN = C('GOLD') / float(np.max(C('GOLD')))


def table(t):
    """The S7 world: light = albedo x (1.35 + 9 band GOLD/max(GOLD)); alpha 1."""
    alb = table_albedo()
    b = band_mask(t)
    cv = np.empty((K.H, K.W, 4), np.float32)
    cv[..., :3] = alb * (1.35 + 9.0 * b[..., None] * GOLDN[None, None, :])
    cv[..., 3] = 1.0
    return cv


@functools.lru_cache(maxsize=1)
def phone_sprites():
    """PHONE_FACE_DOWN 300x620 r 52 + 6 px pad: glossy back, bevel, camera bump with 3 lenses + flash.
    -> (phone, glow, shadow) sprites sharing one centre."""
    pw, ph, pr, pad = 300, 620, 52.0, 6
    a = K.rrect_alpha(pw, ph, pr, pad)
    Hh, Ww = a.shape
    yy, xx = np.mgrid[0:Hh, 0:Ww].astype(np.float32)
    v = np.clip((yy - pad) / ph, 0, 1)
    rgb = hexl('#2C1B15')[None, None, :] * (1 - v[..., None]) + hexl('#100705')[None, None, :] * v[..., None]
    ang = math.radians(62.0)
    d = (xx - Ww * 0.42) * math.cos(ang) - (yy - Hh * 0.40) * math.sin(ang)
    rgb += np.exp(-0.5 * (d / 46.0) ** 2)[..., None] * C('IVORY', 0.10)
    rgb += np.exp(-0.5 * ((d - 120.0) / 2.5) ** 2)[..., None] * C('IVORY', 0.05)
    sdf = K.rrect_sdf(pw, ph, pr, pad)
    inner = np.clip(-sdf, 0, None)
    bev = np.clip(1.0 - inner / 6.0, 0, 1) * (inner > 0)
    lit = np.clip(1.1 - (xx / Ww + yy / Hh), 0, 1)
    rgb += (bev * lit)[..., None] * (C('ASH', 0.55) + C('FLAME', 0.10))
    # camera bump (top-left island 146 x 156 r 40)
    bx, by, bw, bh = pad + 20, pad + 20, 146, 156
    isl = np.zeros((Hh, Ww), np.float32)
    ia = K.rrect_alpha(bw, bh, 40.0, 0)
    isl[by:by + bh, bx:bx + bw] = ia
    isl_edge = np.zeros_like(isl)
    ie = np.clip(1.0 - np.clip(-K.rrect_sdf(bw, bh, 40.0, 0), 0, None) / 3.0, 0, 1) * ia
    isl_edge[by:by + bh, bx:bx + bw] = ie
    rgb = rgb * (1 - isl[..., None]) + isl[..., None] * hexl('#24160F')[None, None, :]
    rgb += isl_edge[..., None] * C('ASH', 0.45)

    def disc_m(cx, cy, r):
        return np.clip(r - np.hypot(xx - cx, yy - cy) + 0.5, 0, 1)

    for (lx, ly, lr) in ((bx + 42, by + 42, 28), (bx + 42, by + 114, 28), (bx + 108, by + 78, 21)):
        m0 = disc_m(lx, ly, lr)
        ring_m = np.clip(m0 - disc_m(lx, ly, lr - 4), 0, 1)
        rgb = rgb * (1 - m0[..., None]) + m0[..., None] * C('NIGHT_0')[None, None, :]
        mi = disc_m(lx, ly, lr * 0.62)
        rgb = rgb * (1 - mi[..., None]) + mi[..., None] * hexl('#1B0E14')[None, None, :]
        rgb += ring_m[..., None] * C('ASH', 0.75)
        cl = disc_m(lx - lr * 0.32, ly - lr * 0.32, max(2.0, lr * 0.16))
        rgb += cl[..., None] * C('IVORY', 0.9)
    fl = disc_m(bx + 108, by + 128, 8)
    rgb = rgb * (1 - fl[..., None]) + fl[..., None] * C('AMBER', 0.55)[None, None, :]
    phone = np.zeros((Hh, Ww, 4), np.float32)
    phone[..., :3] = rgb * a[..., None]
    phone[..., 3] = a
    am = solid(a, (1.0, 1.0, 1.0))
    glow = K.glow(am, C('FLAME'), sigmas=(6, 18, 48), strength=1.0, include=False)
    shp = 60
    sa = np.pad(a, shp)
    sa = cv2.GaussianBlur(sa, (0, 0), 22.0) * 0.75
    shadow = solid(sa, C('NIGHT_0'))
    return ro(phone), ro(glow), ro(shadow)


BUZZ = (16.8, 17.0, 18.2, 18.4)          # haptic pulses: shake + 6 px creep + 0.4 deg each
PINGS = (18.9, 19.267, 19.433)          # 2 px jolt + 5 px creep + 0.25 deg each
GLOW_PULSES = (17.2, 18.6, 18.9, 19.267, 19.433)
CREEP_DIR = (math.cos(math.radians(20.0)), math.sin(math.radians(20.0)))


def creep(t):
    """(dx, dy, drot) of the phone at t (BRIEF 6.4 S7): 12 px per buzz, 5 px per ping, 39 px / +2.35 deg in all."""
    d, r, jx, jy = 0.0, 0.0, 0.0, 0.0
    for p in BUZZ:
        u = K.ramp(t, p, p + 0.13, 'out_cubic')
        d += 6.0 * u
        r += 0.4 * u
        if p <= t < p + 0.13:
            env = math.sin(math.pi * (t - p) / 0.13)
            sx, sy, _ = K.shake(t, 5.0, 30.0, seed=int(p * 10))
            jx += sx * env
            jy += sy * env
    for p in PINGS:
        u = K.ramp(t, p, p + 0.10, 'out_cubic')
        d += 5.0 * u
        r += 0.25 * u
        if p <= t < p + 0.10:
            env = math.sin(math.pi * (t - p) / 0.10)
            jx += 2.0 * env * CREEP_DIR[1]
            jy -= 2.0 * env * CREEP_DIR[0]
    return d * CREEP_DIR[0] + jx, d * CREEP_DIR[1] + jy, r


def edge_glow(t):
    g = 0.18 * K.ramp(t, 16.8, 17.0, 'out_cubic') + 0.22 * K.ramp(t, 17.2, 18.9, 'inout_sine') \
        + 0.60 * K.ramp(t, 18.9, 19.6, 'in_cubic')
    for p in GLOW_PULSES:
        if t >= p - 2 / FPS:
            a = K.clamp((t - (p - 2 / FPS)) / (2 / FPS))
            g += 0.5 * a * math.exp(-max(0.0, t - p) / 0.22)
    return min(1.0, g)


PHONE_C = (522.0, 896.0)


def phone_pose(t):
    dx, dy, dr = creep(t)
    return PHONE_C[0] + dx, PHONE_C[1] + dy, 12.0 + dr


@functools.lru_cache(maxsize=1)
def counter():
    return T.Counter('jw_mono', px=40, fill='AMBER', prefix='', suffix='', decimals=0, sep='')


COUNT = K.Track([(18.9, 12.0, 'out_cubic'), (19.1, 47.0), (19.267, 47.0, 'out_cubic'), (19.4, 99.0)])


def count_pill(cv, t):
    """Chip 'Kuch mahine baad' (POP f504-f512, out f540-f545) -> 'Khandaan . 12 -> 47 -> 99+' (from f546)."""
    k = fidx(t)
    t0 = 504 / FPS
    pop = 0.7 + 0.3 * X.spring(max(0.0, t - t0), 'POP')
    op = K.ramp(t, t0 - HALF, t0 + 4 / FPS, 'out_cubic')
    R = CHIP_PILL
    cx, cy = (R[0] + R[2]) / 2.0, (R[1] + R[3]) / 2.0
    glass(R[2] - R[0], R[3] - R[1], 38.0).draw(cv, cx, cy, scale=pop, opacity=op)
    if k < 546:
        ex = K.ramp(t, 540 / FPS - HALF, 545 / FPS, 'in_cubic')
        o = op * (1.0 - ex)
        if o > 1e-4:
            tx('Kuch mahine baad', 'jw_mono', 40).draw(cv, cx + 0 * pop, 340 - 12 * ex, opacity=o, scale=pop)
        return
    u = K.ramp(t, 546 / FPS - HALF, 552 / FPS, 'out_cubic')
    dy = 12.0 * (1 - u)
    text(cv, 'Khandaan · ', 'jw_mono', 40, 366.8, 340 + dy, opacity=u)
    v = COUNT(t)
    counter().draw(cv, v, 639.0, 340 + dy, anchor=(0.0, 0.5), vel=COUNT.vel(t), opacity=u, ndig=2)
    pl = K.ramp(t, 583 / FPS - HALF, 587 / FPS, 'inout_sine')
    if pl > 0:
        text(cv, '+', 'jw_mono', 40, 688.5, 340 + dy, fill='AMBER', opacity=pl * u)


@functools.lru_cache(maxsize=1)
def skip_motes():
    return J.embers(40, seed=17, bright=0.5, vel=(4, -10, 0))


def skip_scene(t):
    """S7 world (f504-f587): table + light band + phone (edge glow under it) + motes + chip / count pill."""
    cv = table(t)
    ph, gl, sh = phone_sprites()
    x, y, r = phone_pose(t)
    K.draw(cv, sh, x + 10, y + 18, scale=(1.0, 0.92), rot=r, opacity=1.0)
    g = edge_glow(t)
    if g > 1e-4:
        K.draw(cv, gl, x, y, scale=(1.0, 0.92), rot=r, opacity=1.6 * g, mode='add')
    K.draw(cv, ph, x, y, scale=(1.0, 0.92), rot=r)
    sc = K.Scene(K.Cam())
    sc.particles(skip_motes(), t)
    sc.render(cv)
    count_pill(cv, t)
    return cv


# ---------------------------------------------------------------------------------------------- S8 family chat
@functools.lru_cache(maxsize=1)
def avatar():
    r = 30
    m = K.disc(r, (1, 1, 1))[..., 3]
    hh, ww = m.shape
    yy, xx = np.mgrid[0:hh, 0:ww].astype(np.float32)
    u = np.clip((xx + yy) / (hh + ww), 0, 1)[..., None]
    col = C('FLAME') * (1 - u) + C('RED') * u
    out = np.zeros((hh, ww, 4), np.float32)
    out[..., :3] = col * m[..., None]
    out[..., 3] = m
    return ro(out)


# message stack: (kind, w, h, t_arrive) oldest -> newest; flood placeholders scroll in f588-f609
FLOOD = [(300, 96), (520, 130), (410, 96), (260, 96), (480, 160), (350, 96), (560, 130), (300, 96), (440, 130),
         (380, 96), (500, 96), (330, 130), (460, 96), (290, 96)]
ITEMS = ([('ph', w, h, None) for (w, h) in FLOOD]
         + [('reel', 356, 660, 651 / FPS), ('kamaal', 340, 120, 672 / FPS), ('wah', 270, 120, 693 / FPS),
            ('typing', 470, 70, 756 / FPS)])
STACK_BOTTOM = 1150.0
CLIP_TOP = 400.0
FLOOD_D = 1500.0


def _arrived(t, ta):
    return ta is None or t >= ta - HALF


def stack_layout(t):
    """[(kind, x0, y0, w, h, pop_u)] at t (screen px, before the panel float)."""
    flood = FLOOD_D * (1.0 - K.ramp(t, 19.6 - HALF, 609 / FPS, 'out_expo'))
    out = []
    y_bottom = STACK_BOTTOM
    # newest first: each arrived newer item pushes the older ones up (eased 0.25 s out_cubic)
    for kind, w, h, ta in reversed(ITEMS):
        if not _arrived(t, ta):
            continue
        pu = 1.0 if ta is None else K.ramp(t, ta - HALF, ta + 0.25, 'out_cubic')
        y1 = y_bottom
        out.append((kind, 130.0, y1 - h, w, h, pu))
        y_bottom = y1 - (h + 20.0) * (pu if ta is not None else 1.0)
    res = []
    for kind, x0, y0, w, h, pu in out:
        if kind == 'ph':
            y0 += flood
        res.append((kind, x0, y0, w, h, pu))
    return res


def dot3_pose(t):
    """M1 'a': the drawn pose of the typing pill's dot 3 (x, y, r) incl. the panel float."""
    dx, dy = chat_float(t)
    return (562.0 + dx, 1115.0 + dy, 9.0)


def chat_float(t):
    return K.wiggle(t, 0.3, 4.0, 11), K.wiggle(t, 0.25, 3.0, 12)


def chat_dot_freeze(t):
    k = fidx(t)
    if 777 <= k < 798:
        return 0.42, 0.6           # frozen phase, dim
    if k >= 825:
        return 0.0, 1.0            # held at scale 1.0 for the M1 push
    return None, 1.0


def _bubble(layer, kind, x0, y0, w, h, pu, t, thumb):
    """One message into the (unclipped) column layer."""
    op = K.clamp(pu * 4.0) if pu < 1 else 1.0
    if op <= 1e-4:
        return
    s = 0.88 + 0.12 * K.EASE['out_back'](pu) if pu < 1 else 1.0
    xf = Xf(s, 0.0, 0.0, c=(x0, y0 + h))           # pops from its bottom-left corner
    R = (x0, y0, x0 + w, y0 + h)
    if kind == 'ph':
        glass(w, h, 30.0, rim=0.35, glow=0.0, shadow=0.4).draw(layer, x0 + w / 2, y0 + h / 2, frost=0)
        bar = rr_sprite(int(w * 0.62), 14, 7, tuple(float(v) for v in C('ASH', 0.20)))
        K.draw(layer, bar, x0 + 28, y0 + h / 2 - (12 if h > 100 else 0), anchor=(0, 0.5))
        if h > 100:
            bar2 = rr_sprite(int(w * 0.38), 14, 7, tuple(float(v) for v in C('ASH', 0.16)))
            K.draw(layer, bar2, x0 + 28, y0 + h / 2 + 22, anchor=(0, 0.5))
        return
    cx, cy = xf.p(x0 + w / 2, y0 + h / 2)
    r = 36.0 if kind == 'reel' else (35.0 if kind == 'typing' else 34.0)
    glass(w, h, r, rim=0.6, glow=0.4, shadow=0.5).draw(layer, cx, cy, scale=s, opacity=op, frost=0)
    if kind == 'reel':
        text(layer, 'Chachi', 'jw_body', 36, 158, y0 + 40, fill='AMBER', xf=xf, opacity=op)
        fx, fy = xf.p(172, y0 + 80)
        K.draw(layer, icons()['fwd'], fx, fy, scale=s, opacity=op)
        text(layer, 'Forwarded', 'jw_mono', 34, 194, y0 + 80, fill='ASH', xf=xf, opacity=op)
        if thumb is not None:
            tx_, ty_ = xf.p(158, y0 + 104)
            K.draw(layer, thumb, tx_, ty_, anchor=(0, 0), scale=s, opacity=op)
    elif kind in ('kamaal', 'wah'):
        who, msg = ('Mamu', 'Kamaal!') if kind == 'kamaal' else ('Chachu', 'Wah!')
        text(layer, who, 'jw_body', 36, x0 + 28, y0 + 34, fill='AMBER', xf=xf, opacity=op)
        text(layer, msg, 'jw_body', 50, x0 + 28, y0 + 82, xf=xf, opacity=op)
    elif kind == 'typing':
        text(layer, 'Mummy is typing', 'jw_body', 36, 160, y0 + 35, fill='ASH', xf=xf, opacity=op)
        ph_, dim = chat_dot_freeze(t)
        k = fidx(t)
        tau = t
        if 819 <= k < 825:
            tau = 819 / FPS + (t - 819 / FPS) * 0.35          # slow pulse
        spr = dot_sprite(9)
        for i in range(3):
            sc_ = 1.0 if (ph_ is not None and k >= 825) else dot_scale(tau if ph_ is None else ph_, i)
            dx_, dy_ = xf.p(510 + 26 * i, y0 + 35)
            K.draw(layer, spr, dx_, dy_, scale=sc_ * s, opacity=op * dim)


@functools.lru_cache(maxsize=1)
def column_mask():
    """Row mask of the message column: clip y 400-1150 with 12 px feathers."""
    ys = np.arange(K.H, dtype=np.float32) + 0.5
    m = np.clip((ys - (CLIP_TOP - 6)) / 12.0, 0, 1) * np.clip(((STACK_BOTTOM + 6) - ys) / 12.0, 0, 1)
    return ro(m)


def chat(cv, t, thumb=None):
    """S8 panel (f588-f839) onto cv: glass panel, header, clipped message column."""
    dx, dy = chat_float(t)
    xf = Xf(1.0, dx, dy)
    x, y = xf.p(*CARD_C)
    card_glass().draw(cv, x, y)
    ax, ay = xf.p(156, 352)
    K.draw(cv, avatar(), ax, ay)
    text(cv, 'K', 'jw_body', 34, 156, 352, anchor=(0.5, 0.5), xf=xf)
    text(cv, 'Khandaan', 'jw_body', 48, 202, 352, xf=xf)
    y0c, y1c = int(CLIP_TOP - 8), int(STACK_BOTTOM + 8)
    layer = np.zeros((K.H, K.W, 4), np.float32)
    for kind, x0, yy0, w, h, pu in stack_layout(t):
        if yy0 > y1c or yy0 + h < y0c:
            continue
        _bubble(layer, kind, x0, yy0, w, h, pu, t, thumb)
    # clip + composite (screen-space float applied as an integer-free shift via K.draw of the band)
    m = column_mask()
    band = layer[y0c:y1c] * m[y0c:y1c, None, None]
    K.draw(cv, ro(band), 0 + dx, y0c + dy, anchor=(0, 0))
    return cv


# ---------------------------------------------------------------------------------------------- REEL_THUMB
@functools.lru_cache(maxsize=2)
def play_triangle():
    w, h, p = 36, 40, 12
    m = np.zeros((h + 2 * p, w + 2 * p), np.uint8)
    pts = np.array([[p, p], [p + w, p + h // 2], [p, p + h]], np.int32) * 4
    big = np.zeros(((h + 2 * p) * 4, (w + 2 * p) * 4), np.uint8)
    cv2.fillPoly(big, [pts], 255, cv2.LINE_AA)
    m = cv2.resize(big, (w + 2 * p, h + 2 * p), interpolation=cv2.INTER_AREA).astype(np.float32) / 255.0
    sh = cv2.GaussianBlur(m, (0, 0), 4.0)
    spr = solid(sh * 0.7, C('NIGHT_0'))
    over(spr, solid(m * 0.9, C('IVORY')))
    return ro(spr)


def make_thumb(cover_lin):
    """REEL_THUMB 300x533 r 20 from the linear cover canvas (f30 layers, no captions, before post)."""
    rgb = np.ascontiguousarray(cover_lin[..., :3])
    sm = cv2.resize(rgb, (300, 533), interpolation=cv2.INTER_AREA) * np.float32(0.92)
    m = K.rrect_alpha(300, 533, 20.0, 0)
    spr = np.zeros((533, 300, 4), np.float32)
    spr[..., :3] = sm * m[..., None]
    spr[..., 3] = m
    tri = play_triangle()
    th, tw = tri.shape[:2]
    p = 12
    x0, y1 = 20 - p, 533 - 20 + p
    y0 = y1 - th
    sub = spr[y0:y1, x0:x0 + tw]
    over(sub, tri * m[y0:y1, x0:x0 + tw, None])
    return ro(spr)
