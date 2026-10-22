"""IC London — "No Law Degree? You May Still Have a Route into Law" (9:16, 30 s).

Concept: a career "route planner". Montage of IC London's own site photography -> "Law degree required?" flips to
"Not necessarily" -> "Recalculating route…" -> a tilted 3D route map the camera travels along, one waypoint per
SRA requirement (degree in any subject / equivalent L6, SQE1, SQE2, two years' QWE, character & suitability) ->
destination "Qualified solicitor" -> IC London SQE course card -> CTA.
Facts: sra.org.uk (SQE route, QWE page) and iclondon.co.uk (SQE course page). Brand: logo navy #00247D + red
#CF142B, site fonts Inter + Cardo.

Usage:
  python3 reel_ic.py still 1.0,5.0
  python3 reel_ic.py range 0 900
"""
import os, sys, math, functools
HERE = os.path.dirname(os.path.abspath(__file__))
os.environ['REEL_WORKDIR'] = os.path.abspath(os.path.join(HERE, '..', 'workspace_ic'))
sys.path.insert(0, os.path.join(HERE, '..', 'pipeline_su'))
import numpy as np
import cv2
import reel_su as RS
from reel_su import paste, fitted, png, ripple, sparks, cursor
from reel_of import kinetic_line, word_spr, sweep, glow_add, whip, zoom_blur, shake, rrect_spr, glass
from engine import *  # noqa: F401,F403
import engine as E

S = E.S
FPS = 30

# ------------------------------------------------------------------ brand
NAVY = hexc('#00247D')
NAVY_D = hexc('#06143F')
NAVY_M = hexc('#0B2C8F')
RED = hexc('#CF142B')
RED_L = hexc('#FF4D5E')
WHITE_ = (1.0, 1.0, 1.0, 1.0)
INK = hexc('#0A1A4A')
SLATE = hexc('#5A6A92')
ICE = hexc('#EEF2FB')
GOLD = hexc('#E3B24A')
IX, IB, IS, IM, IR = 'Inter-800', 'Inter-700', 'Inter-600', 'Inter-500', 'Inter-400'
CB, CI = 'Cardo-700', 'CardoItalic-400'

# ------------------------------------------------------------------ timeline
T = dict(hook=0.0, turn=3.6, route=8.6, ic=18.6, cta=24.3)
DUR = 30.0
NF = int(DUR * FPS)
VO = {'hook': 0.15, 'turn': 3.75, 'steps': 8.8, 'ic': 18.8, 'cta': 24.6}
NOT_NEC = VO['turn'] + 0.05                    # "Not necessarily."
ANY_SUBJ = VO['turn'] + 1.7                    # "With the SQE, your degree can be in any subject."
RECALC = 7.3
WAY_T = [8.6, 8.9, 10.0, VO['steps'] + 2.5, VO['steps'] + 5.55, 16.7]   # camera reaches each waypoint
CHIP_T = [VO['ic'] + 0.6, VO['ic'] + 2.8, VO['ic'] + 3.9, VO['ic'] + 4.6]
TAP_CTA = 26.4
FADE = 1.3

SEQ = {}


def seq(name):
    if name not in SEQ:
        SEQ[name] = Seq(name, fps=24, loop=True)
    return SEQ[name]


def txt(canvas, s, x, y, size, color, fname=IS, op=1.0, ax=0.5, shadow_op=0.0, scale=1.0):
    spr = word_spr(s, fname, size, color)
    if op <= 0:
        return spr
    if shadow_op > 0:
        sh = blur_sprite(tint(spr, (0.0, 0.02, 0.08)), 10)
        draw(canvas, sh, x, y + 6, scale=scale, opacity=shadow_op * op, ax=ax)
    draw(canvas, spr, x, y, scale=scale, opacity=op, ax=ax)
    return spr


def icon(canvas, name, t, x, y, size, t0=None, op=1.0, glow=None, shadow_on=True):
    s = 1.0
    if t0 is not None:
        if t < t0:
            return
        k = prog(t, t0, t0 + 0.45)
        s = e_out_back(k, 2.2)
        op *= min(1, k * 3)
    f = seq(name).frame(t)
    if f.shape[0] < 16:
        return
    sc = size / max(f.shape[:2]) * s
    if glow is not None:
        glow_add(canvas, f, x, y, glow, sigma=20, strength=0.5 * op, scale=sc)
    if shadow_on:
        sh = blur_sprite(tint(f, (0.0, 0.02, 0.1)), 12)
        draw(canvas, sh, x + 6, y + size * 0.08, scale=sc, opacity=0.45 * op)
    draw(canvas, f, x, y, scale=sc, opacity=op)


def headline(c, text, cy, size, t, t0, color=WHITE_, fname=IX, glow=None, sweep_t=None, shadow_op=0.6, stagger=0.05):
    kinetic_line(c, text, W / 2, cy, size, t, t0, color=color, fname=fname, glow=glow, glow_str=0.45,
                 shadow_op=shadow_op, stagger=stagger, sweep_t=sweep_t)


# ------------------------------------------------------------------ backgrounds
_bY, _bX = np.mgrid[0:H // 4, 0:W // 4].astype(np.float32)


def _blob(cx, cy, r):
    d = np.sqrt((_bX - cx / 4) ** 2 + (_bY - cy / 4) ** 2) / (r / 4)
    return np.exp(-d * d)[..., None]


def bg(t, red=0.18):
    base = vgrad(H // 4, W // 4, hexc('#0A2470'), NAVY_D)
    for (cx, cy, r, col, a, ph) in [(200, 380, 620, NAVY_M, 0.7, 0.0), (900, 1450, 600, RED, red, 1.9),
                                    (980, 500, 420, hexc('#1F49C2'), 0.35, 3.0)]:
        x = cx + 80 * math.sin(t * 0.45 + ph)
        y = cy + 60 * math.cos(t * 0.4 + ph)
        b = _blob(x, y, r) * a
        base = base * (1 - b) + np.array(col[:3], np.float32) * b
    c = cv2.resize(base, (W, H), interpolation=cv2.INTER_CUBIC)
    c += grid_overlay() * 0.035
    return c


@functools.lru_cache(maxsize=1)
def grid_overlay():
    g = np.zeros((H, W), np.float32)
    for x in range(0, W, 90):
        cv2.line(g, (x, 0), (x, H), 1.0, 1)
    for y in range(0, H, 90):
        cv2.line(g, (0, y), (W, y), 1.0, 1)
    return g[..., None]


@functools.lru_cache(maxsize=16)
def photo(name):
    im = cv2.imread(f'{S}/src/{name}.jpg')[..., ::-1].astype(np.float32) / 255.0
    return im


def photo_frame(name, lt, dur, zoom0=1.18, zoom1=1.06, pan=(0.0, 0.0)):
    """Fill 9:16 from a landscape site photo with a slow push (Ken Burns)."""
    im = photo(name)
    h, w = im.shape[:2]
    k = e_inout_cubic(clamp(lt / max(dur, 1e-3)))
    z = lerp(zoom0, zoom1, k)
    ch = h / z
    cw = ch * W / H
    cx = w / 2 + pan[0] * w * (k - 0.5)
    cy = h / 2 + pan[1] * h * (k - 0.5)
    return crop_resize(im, cx, cy, cw, ch, W, H).astype(np.float32)


def navy_grade(c, amt=0.55):
    lum = c.mean(axis=2, keepdims=True)
    tinted = lum * np.array([0.55, 0.68, 1.15], np.float32) + np.array([0.0, 0.02, 0.08], np.float32)
    return c * (1 - amt) + tinted * amt


# ------------------------------------------------------------------ scenes
HOOK = ['p_2147898626', 'p_14828', 'p_45573', 'p_810', 'p_13585', 'p_124799', 'p_2147898626', 'p_14267']


def sc_hook(t):
    i = min(int(t / 0.45), len(HOOK) - 1)
    lt = t - i * 0.45
    c = photo_frame(HOOK[i], lt, 0.45, zoom0=1.22, zoom1=1.08, pan=(0.08 * (-1) ** i, 0))
    c = navy_grade(c, 0.5) * 0.78
    scrim_navy(c, 0.75, 0.85)
    if lt < 0.05:
        c = c + 0.22 * (1 - lt / 0.05)
    # logo pill
    kp = prog(t, 0.1, 0.4)
    if kp > 0:
        card = rrect_spr(400, 150, 40, (1, 1, 1, 0.96))
        c2 = card.copy()
        paste(c2, fitted('logo_h', png('logo_full'), height=124), 200, 75)
        draw(c, c2, W / 2, 230, opacity=min(1, kp * 2))
    headline(c, 'Think you need a', 760, 76, t, 0.15, fname=IX, shadow_op=0.75)
    kinetic_line(c, 'law degree', W / 2, 905, 156, t, 0.45, color=WHITE_, fname=CB, glow=RED, glow_str=0.5,
                 shadow_op=0.75, sweep_t=1.1)
    kr = e_out_cubic(prog(t, 0.95, 1.35))
    if kr > 0:
        draw(c, rrect_spr(max(8, 620 * kr), 10, 5, RED), W / 2 - 310 + 310 * kr, 1000)
    headline(c, 'to become a solicitor?', 1095, 66, t, VO['hook'] + 1.6, fname=IX, shadow_op=0.75, sweep_t=2.6)
    return c


_yy = np.linspace(0, 1, H, dtype=np.float32)[:, None, None]


def scrim_navy(c, top, bot):
    col = np.array(NAVY_D[:3], np.float32)
    a = np.clip(1 - _yy / 0.35, 0, 1) ** 1.6 * top + np.clip((_yy - 0.55) / 0.45, 0, 1) ** 1.4 * bot
    a = np.clip(a + 0.25, 0, 1)
    c *= (1 - a)
    c += col * a


def ui_card(c, cx, cy, w, h, op=1.0, r=34, dark=False):
    glass(c, cx, cy, w, h, r=r, tint_c=(1, 1, 1) if not dark else (0.1, 0.18, 0.45), tint_a=0.95 if not dark else 0.5,
          opacity=op, blur=22, shadow_a=0.45, border_a=0.7)


@functools.lru_cache(maxsize=4)
def toggle_spr(on):
    w, h = 150, 80
    spr = rrect_spr(w, h, 40, RED if on else hexc('#C9D2EA'))
    knob = rrect_spr(64, 64, 32, (1, 1, 1, 1))
    paste(spr, knob, w - 42 if on else 42, h / 2)
    return spr


@functools.lru_cache(maxsize=4)
def check_spr_ic(size=48, col=RED):
    s = size * 3
    im = np.zeros((s, s), np.float32)
    cv2.circle(im, (s // 2, s // 2), s // 2 - 2, 1.0, -1, cv2.LINE_AA)
    tk = np.zeros((s, s), np.float32)
    pts = np.array([[s * 0.28, s * 0.52], [s * 0.44, s * 0.68], [s * 0.74, s * 0.36]], np.int32)
    cv2.polylines(tk, [pts], False, 1.0, int(s * 0.11), cv2.LINE_AA)
    spr = over_spr(solid(im, col), solid(tk, WHITE_))
    return cv2.resize(spr, (size, size), interpolation=cv2.INTER_AREA)


def sc_turn(t):
    t0 = T['turn']
    c = bg(t)
    # app header
    kh = prog(t, t0, t0 + 0.35)
    if kh > 0:
        ui_card(c, W / 2, 200, 940, 120, op=min(1, kh * 2), dark=True)
        txt(c, 'Career Route Planner', 110, 200, 38, WHITE_, IX, kh, ax=0.0)
        p = pill('IC London', IB, 24, pad_x=22, pad_y=10, fill=RED, border=None, text_color=WHITE_)
        draw(c, p, 920, 200, opacity=kh)
    # destination search field
    kd = prog(t, t0 + 0.1, t0 + 0.45)
    if kd > 0:
        y = 420 + 40 * (1 - e_out_cubic(kd))
        ui_card(c, W / 2, y, 940, 150, op=min(1, kd * 2))
        icon(c, 'pin', t, 150, y, 96, t0 + 0.15, shadow_on=False)
        txt(c, 'DESTINATION', 225, y - 30, 24, SLATE, IB, kd, ax=0.0)
        dest = 'Solicitor (England & Wales)'
        n = int(max(0, t - (t0 + 0.35)) * 34)
        if n > 0:
            txt(c, dest[:n], 225, y + 18, 40, INK, IX, kd, ax=0.0)
        if n < len(dest) and int(t * 3) % 2 == 0:
            ts = word_spr(dest[:max(n, 0)] or ' ', IX, 40, INK)
            draw(c, rrect_spr(4, 44, 2, RED), 225 + (ts.shape[1] if n > 0 else 0) + 4, y + 18)
    # "Law degree required?" -> "Not necessarily"
    kq = prog(t, t0 + 0.25, t0 + 0.6)
    if kq > 0:
        y = 680 + 40 * (1 - e_out_cubic(kq))
        flip = prog(t, NOT_NEC, NOT_NEC + 0.3)
        ui_card(c, W / 2, y, 940, 190, op=min(1, kq * 2))
        txt(c, 'Law degree required?', 110, y - 32, 42, INK, IX, kq, ax=0.0)
        if flip < 0.5:
            txt(c, 'Checking requirements…', 110, y + 30, 30, SLATE, IM, kq, ax=0.0)
        else:
            txt(c, 'Not necessarily', 110, y + 30, 34, RED, IX, kq, ax=0.0)
        draw(c, toggle_spr(flip < 0.5), 920, y, opacity=kq)
        if 0 < flip < 1:
            draw(c, ring_sprite(260, 50 + 80 * flip, 4, RED, glow=8), 920, y, opacity=1 - flip)
    # degree in any subject / equivalent L6
    for j, (l1, l2) in enumerate([('A degree in any subject', 'SRA: the degree can be in any subject'),
                                  ('or an equivalent qualification', 'e.g. a level 6 qualification')]):
        kk = prog(t, ANY_SUBJ + 0.5 + j * 0.45, ANY_SUBJ + 0.9 + j * 0.45)
        if kk <= 0:
            continue
        y = 960 + j * 190
        x = W / 2 + 120 * (1 - e_out_expo(kk))
        ui_card(c, x, y, 940, 160, op=min(1, kk * 2))
        draw(c, check_spr_ic(58), x - 400, y, scale=e_out_back(kk, 2.5))
        txt(c, l1, x - 340, y - 22, 38, INK, IX, kk, ax=0.0)
        txt(c, l2, x - 340, y + 28, 28, SLATE, IM, kk, ax=0.0)
    icon(c, 'cap', t, 850, 860, 190, ANY_SUBJ + 0.4, glow=RED)
    # recalculating
    kr = prog(t, RECALC, RECALC + 0.3)
    if kr > 0:
        y = 1420
        ui_card(c, W / 2, y, 760, 130, op=min(1, kr * 2), dark=True)
        s = 70
        im = np.zeros((s * 2, s * 2), np.float32)
        cv2.ellipse(im, (s, s), (s - 8, s - 8), (t * 540) % 360, 0, 250, 1.0, 9, cv2.LINE_AA)
        draw(c, cv2.resize(solid(im, RED_L), (s, s)), W / 2 - 250, y, opacity=kr)
        txt(c, 'Recalculating route…', W / 2 + 40, y, 38, WHITE_, IB, kr)
    return c


# ------------------------------------------------------------------ route map (tilted 3D plane)
RW, RH = 1080, 4000
WAYS = [  # (title, subtitle lines, icon, tag)
    ('A degree in any subject', ['or an equivalent level 6', 'qualification'], 'cap', 'STEP 1'),
    ('Pass SQE1', ['Functioning legal knowledge', '(FLK1 and FLK2)'], 'exam', 'STEP 2'),
    ('Pass SQE2', ['Practical legal skills', 'assessment'], 'gavel', 'STEP 3'),
    ("2 years' qualifying work", ['experience (QWE) · full-time or equiv.', 'up to 4 organisations · paid or volunteer'],
     'briefcase', 'STEP 4'),
    ('Character & suitability', ["Meet the SRA's requirements"], 'shield', 'STEP 5'),
    ('Qualified solicitor', ['England & Wales'], 'scales', 'DESTINATION'),
]
WAY_Y = [RH - 320 - j * 560 for j in range(6)]


def route_x(y):
    return 170 + 46 * math.sin(y / 330.0)


@functools.lru_cache(maxsize=1)
def map_base():
    """Static map: navy streets grid, a river, faint district blocks, dashed route and all waypoint cards."""
    rgb = np.ones((RH, RW, 3), np.float32) * np.array(hexc('#0A1E5C')[:3], np.float32)
    rng = np.random.default_rng(3)
    for _ in range(70):
        x, y = rng.uniform(0, RW), rng.uniform(0, RH)
        w, h = rng.uniform(90, 260), rng.uniform(90, 260)
        cv2.rectangle(rgb, (int(x), int(y)), (int(x + w), int(y + h)), tuple(float(v) for v in hexc('#0E2670')[:3]), -1)
    for x in range(-200, RW + 200, 150):
        cv2.line(rgb, (x, 0), (x + 120, RH), tuple(float(v) for v in hexc('#18348A')[:3]), 6, cv2.LINE_AA)
    for y in range(0, RH, 170):
        cv2.line(rgb, (0, y), (RW, y + 60), tuple(float(v) for v in hexc('#18348A')[:3]), 6, cv2.LINE_AA)
    pts = np.array([[RW * 0.95 + 120 * math.sin(y / 500), y] for y in range(0, RH, 40)], np.int32)
    cv2.polylines(rgb, [pts], False, tuple(float(v) for v in hexc('#1B47B5')[:3]), 60, cv2.LINE_AA)
    spr = np.concatenate([rgb, np.ones((RH, RW, 1), np.float32)], 2)
    # dashed route
    ys = np.arange(WAY_Y[-1], WAY_Y[0] + 1, 4)
    for y0 in range(int(WAY_Y[-1]), int(WAY_Y[0]), 36):
        y1 = y0 + 20
        cv2.line(spr, (int(route_x(y0)), y0), (int(route_x(y1)), y1), (1, 1, 1, 1), 6, cv2.LINE_AA)
    return spr


@functools.lru_cache(maxsize=8)
def way_card(j):
    t1, subs, ic, tag = WAYS[j]
    w = 790
    h = 140 + 44 * len(subs)
    spr = rrect_spr(w, h, 34, (1, 1, 1, 0.97) if j < 5 else (1, 0.97, 0.9, 1), border=RED if j == 5 else None, bw=4)
    p = pill(tag, IX, 22, pad_x=18, pad_y=8, fill=RED if j < 5 else GOLD, border=None, text_color=WHITE_)
    paste(spr, p, 200 + p.shape[1] / 2 - 30, 44)
    ts = text_sprite(t1, IX, 40, INK)
    paste(spr, ts, 190 + ts.shape[1] / 2, 100)
    for k, s_ in enumerate(subs):
        ss = text_sprite(s_, IM, 28, SLATE)
        paste(spr, ss, 190 + ss.shape[1] / 2, 148 + k * 40)
    return spr


def route_layer(t):
    spr = map_base().copy()
    prog_y = route_progress_y(t)
    # glowing travelled route
    pts = [(int(route_x(y)), int(y)) for y in np.arange(WAY_Y[0], prog_y - 1, -8)]
    if len(pts) > 1:
        line = np.zeros((RH, RW), np.float32)
        cv2.polylines(line, [np.array(pts, np.int32)], False, 1.0, 14, cv2.LINE_AA)
        y0, y1 = int(max(0, prog_y - 60)), int(WAY_Y[0] + 60)
        g = cv2.GaussianBlur(line[y0:y1], (0, 0), 14)
        col = np.array(RED[:3], np.float32)
        spr[y0:y1, :, :3] += g[..., None] * col * 0.9
        a = line[y0:y1, :, None]
        spr[y0:y1, :, :3] = spr[y0:y1, :, :3] * (1 - a) + np.array(RED_L[:3], np.float32) * a
    for j, y in enumerate(WAY_Y):
        x = route_x(y)
        reached = t >= WAY_T[j]
        k = prog(t, WAY_T[j] - 0.15, WAY_T[j] + 0.35)
        node = rrect_spr(64, 64, 32, RED if reached else (1, 1, 1, 1), border=(1, 1, 1, 1), bw=5)
        paste(spr, node, x, y)
        if k > 0:
            card = way_card(j)
            cx = x + 70 + card.shape[1] / 2
            s = 0.9 + 0.1 * e_out_back(k, 1.8)
            if s != 1.0:
                card = cv2.resize(card, (int(card.shape[1] * s), int(card.shape[0] * s)), interpolation=cv2.INTER_LINEAR)
            sh = np.zeros_like(card)
            sh[..., 3] = card[..., 3] * 0.45
            paste(spr, cv2.GaussianBlur(sh, (0, 0), 12), cx + 8, y + 18, op=min(1, k * 2))
            paste(spr, card, cx, y, op=min(1, k * 2.5))
            f = seq(WAYS[j][2]).frame(t + j * 0.3)
            if f.shape[0] > 16:
                isz = 150 if j < 5 else 170
                fi = cv2.resize(f, (int(f.shape[1] * isz / max(f.shape[:2])), int(f.shape[0] * isz / max(f.shape[:2]))),
                                interpolation=cv2.INTER_AREA)
                paste(spr, fi, cx - card.shape[1] / 2 + 95, y + 8, op=min(1, k * 2.5) * e_out_back(k, 2.0))
    return spr


def route_progress_y(t):
    """Map-space y of the travelling marker, easing between waypoints on their beats."""
    if t < WAY_T[0]:
        return WAY_Y[0]
    for j in range(5):
        a, b = WAY_T[j], WAY_T[j + 1]
        if t < b:   # travel in the last 0.9 s before the next waypoint's beat, arriving exactly on it
            k = e_inout_cubic(prog(t, b - min(0.9, b - a), b))
            return lerp(WAY_Y[j], WAY_Y[j + 1], k)
    return WAY_Y[-1]


RX = -20.0
KS = 1.08                                   # plane is drawn 8% wider than the frame
TARGET_Y = 1120                             # where the camera holds the current waypoint on screen


def map_to_screen(mx, my, cyc):
    """Project a map-space point through the same plane geometry draw3d uses."""
    w, h = RW * KS, RH * KS
    loc = np.array([(mx / RW - 0.5) * w, (my / RH - 0.5) * h, 0.0])
    P = loc @ rotm(RX, 0, 0).T + np.array([W / 2, cyc, 0.0])
    q, _ = project_pts(P[None])
    return q[0]


def solve_cyc(fy):
    a, b = -6000.0, 8000.0
    for _ in range(40):                       # bisection: projected y grows with the plane centre
        m = (a + b) / 2
        if map_to_screen(route_x(fy), fy, m)[1] < TARGET_Y:
            a = m
        else:
            b = m
    return (a + b) / 2


def sc_route(t):
    c = bg(t, 0.12)
    spr = route_layer(t)
    fy = route_progress_y(t)
    cyc = solve_cyc(fy)
    draw3d(c, spr, W / 2, cyc, 0, RW * KS, None, rx=RX)
    # top fog so the far route fades into the night
    a = np.clip(1 - _yy / 0.42, 0, 1) ** 1.3 * 0.95
    c *= (1 - a)
    c += np.array(NAVY_D[:3], np.float32) * a
    # travelling marker (red pin billboard) at the focus point
    px, py = map_to_screen(route_x(fy), fy, cyc)
    icon(c, 'pin', t, px, py - 62, 120, shadow_on=True, glow=RED)
    # HUD
    ui_card(c, W / 2, 190, 940, 150, dark=True)
    txt(c, 'Your route to: Solicitor', 100, 165, 38, WHITE_, IX, 1.0, ax=0.0)
    step = sum(1 for wt in WAY_T[1:] if t >= wt)
    txt(c, 'SQE route · SRA requirements', 100, 220, 26, (1, 1, 1, 0.75), IM, 1.0, ax=0.0)
    p = pill(f'{min(step + 1, 5)} / 5' if step < 5 else 'Arrived', IX, 26, pad_x=22, pad_y=10,
             fill=RED if step < 5 else GOLD, border=None, text_color=WHITE_)
    draw(c, p, 930, 190)
    # QWE timing note + source
    kq = prog(t, WAY_T[3] + 0.8, WAY_T[3] + 1.2) * (1 - prog(t, WAY_T[4] - 0.2, WAY_T[4] + 0.2))
    if kq > 0:
        p = pill('QWE can be gained before, during or after the SQE', IB, 26, pad_x=24, pad_y=12, fill=(1, 1, 1, 0.14),
                 border=(1, 1, 1, 0.5), text_color=WHITE_)
        draw(c, p, W / 2, 1620, opacity=kq)
    txt(c, 'Source: Solicitors Regulation Authority · sra.org.uk', W / 2, 1840, 24, (1, 1, 1, 0.7), IM, 1.0)
    ka = prog(t, WAY_T[5] + 0.2, WAY_T[5] + 0.6)
    if ka > 0:
        rays = np.zeros((H, W), np.float32)
        cv2.circle(rays, (W // 2, TARGET_Y), int(500 * e_out_cubic(ka)), 1.0, 8, cv2.LINE_AA)
        c += cv2.GaussianBlur(rays, (0, 0), 10)[..., None] * np.array(GOLD[:3], np.float32) * (1 - ka) * 0.9
    return c


# ------------------------------------------------------------------ IC London course card
CHIPS = ['Complete SQE1 & SQE2 coverage', 'Mock exams and practice tests', 'Career guidance and QWE support',
         'Expert solicitor-tutors']


def sc_ic(t):
    t0 = T['ic']
    c = bg(t, 0.25)
    headline(c, 'Prepare with', 230, 58, t, t0 + 0.05, fname=IB, shadow_op=0.5)
    kinetic_line(c, 'IC London', W / 2, 330, 104, t, t0 + 0.25, color=WHITE_, fname=CB, glow=RED, glow_str=0.45,
                 shadow_op=0.6, sweep_t=t0 + 1.0)
    k = prog(t, t0 + 0.2, t0 + 0.8)
    if k <= 0:
        return c
    cw, ch = 940, 1160
    cy = 1100 + 500 * (1 - e_out_cubic(k))
    rot = 18 * (1 - e_out_cubic(k))
    card = rrect_spr(cw, ch, 44, (1, 1, 1, 1))
    src = photo('p_13585')
    sh_, sw_ = src.shape[:2]
    zz = 1.0 + 0.06 * e_inout_cubic(prog(t, t0, T['cta']))       # slow push inside the card
    pw_ = sw_ / zz
    ph = crop_resize(src, sw_ / 2, sh_ * 0.40, pw_, pw_ * 430 / (cw - 40), cw - 40, 430).astype(np.float32)
    pa = sdf_fill(rrect_alpha(cw - 40, 430, 30, 0))
    pa = cv2.resize(pa, (cw - 40, 430))[..., None]
    paste(card, np.concatenate([ph * pa, pa], 2).astype(np.float32), cw / 2 + 2, 20 + 215 + 2)
    tag = pill('LAW · SQE', IX, 24, pad_x=20, pad_y=10, fill=RED, border=None, text_color=WHITE_)
    paste(card, tag, 60 + tag.shape[1] / 2 - 20, 500)
    for j, ln in enumerate(['Solicitors Qualifying', 'Examination (SQE) Course']):
        ts = text_sprite(ln, IX, 50, INK)
        paste(card, ts, 40 + ts.shape[1] / 2, 580 + j * 62)
    draw(c, blur_sprite(tint(card, (0.0, 0.02, 0.1)), 30), W / 2 + 10, cy + 30, opacity=0.55 * k)
    draw3d(c, card, W / 2, cy, 0, card.shape[1], None, rx=rot, opacity=min(1, k * 2))
    top = cy - ch / 2
    for j, chip in enumerate(CHIPS):
        kk = prog(t, CHIP_T[j], CHIP_T[j] + 0.35)
        if kk <= 0:
            continue
        y = top + 820 + j * 92
        x = W / 2 + 60 * (1 - e_out_expo(kk))
        draw(c, check_spr_ic(52), 145, y, scale=e_out_back(kk, 2.6))
        txt(c, chip, 195, y + 1, 36, INK, IB, min(1, kk * 2), ax=0.0)
    icon(c, 'exam', t, 870, top + 470, 170, t0 + 1.0, shadow_on=True)
    return c


# ------------------------------------------------------------------ CTA (white brand card)
@functools.lru_cache(maxsize=1)
def cta_base():
    c = np.ones((H, W, 3), np.float32) * np.array([0.975, 0.98, 1.0], np.float32)
    band = np.zeros((H, W), np.float32)
    cv2.fillPoly(band, [np.array([[0, 1560], [W, 1380], [W, H], [0, H]], np.int32)], 1.0, cv2.LINE_AA)
    c = c * (1 - band[..., None]) + np.array(NAVY[:3], np.float32) * band[..., None]
    stripe = np.zeros((H, W), np.float32)
    cv2.line(stripe, (0, 1552), (W, 1372), 1.0, 14, cv2.LINE_AA)
    c = c * (1 - stripe[..., None]) + np.array(RED[:3], np.float32) * stripe[..., None]
    return c


def sc_cta(t):
    t0 = T['cta']
    c = cta_base().copy()
    kl = prog(t, t0 + 0.05, t0 + 0.55)
    lg = fitted('logo', png('logo_full'), width=560)
    if kl > 0:
        draw(c, lg, W / 2, 470, scale=0.88 + 0.12 * e_out_back(kl, 1.8), opacity=min(1, kl * 2))
        if t0 + 0.6 < t < t0 + 1.5:
            p = (t - t0 - 0.6) / 0.8 * 1.6 - 0.3
            draw(c, sweep(lg, p, strength=0.45), W / 2, 470, opacity=0.5)
    kinetic_line(c, 'Explore your legal', W / 2, 860, 84, t, VO['cta'] + 0.05, color=INK, fname=CB, shadow_op=0.0)
    kinetic_line(c, 'career options', W / 2, 960, 84, t, VO['cta'] + 0.45, color=RED, fname=CB, shadow_op=0.0,
                 sweep_t=VO['cta'] + 1.2)
    kb = prog(t, t0 + 1.0, t0 + 1.4)
    if kb > 0:
        press = math.sin(math.pi * prog(t, TAP_CTA - 0.06, TAP_CTA + 0.2))
        b = rrect_spr(640, 130, 65, RED)
        g = blur_sprite(tint(rrect_spr(640, 130, 65, WHITE_), RED[:3]), 24)
        draw(c, g, W / 2, 1150 + 10, opacity=0.5 * kb)
        s = (0.85 + 0.15 * e_out_back(kb, 2.0)) * (1 - 0.05 * press)
        draw(c, b, W / 2, 1150, scale=s, opacity=min(1, kb * 3))
        draw(c, word_spr('Visit iclondon.co.uk', IX, 44, WHITE_), W / 2, 1152, scale=s, opacity=min(1, kb * 3))
        ripple(c, W / 2 + 140, 1160, t, TAP_CTA, RED, n=2, rmax=260)
    cursor(c, t, (960, 1700), (W / 2 + 140, 1160), t0 + 1.2, TAP_CTA - 0.05, TAP_CTA,
           op=1 - prog(t, TAP_CTA + 0.3, TAP_CTA + 0.6))
    ks = prog(t, t0 + 1.6, t0 + 2.0)
    if ks > 0:
        for j, ln in enumerate(['Online, at your own pace', 'SQE · Law · HR · Finance']):
            txt(c, ln, W / 2, 1640 + j * 56, 34 if j == 0 else 30, WHITE_, IB if j == 0 else IM, ks)
        txt(c, 'SQE route requirements summarised from the Solicitors Regulation Authority (sra.org.uk).',
            W / 2, 1840, 22, (1, 1, 1, 0.8), IM, ks)
    return c


# ------------------------------------------------------------------ assembly
SCENES = [(T['hook'], T['turn'], sc_hook), (T['turn'], T['route'], sc_turn), (T['route'], T['ic'], sc_route),
          (T['ic'], T['cta'], sc_ic), (T['cta'], 99, sc_cta)]
TRANS = [(T['turn'], 'flash'), (T['route'], 'zoom'), (T['ic'], 'whip'), (T['cta'], 'flashw')]


def scene_at(t):
    for a, b, f in SCENES:
        if a <= t < b:
            return f
    return SCENES[-1][2]


def render_raw(t):
    c = scene_at(t)(t)
    for tc, kind in TRANS:
        d = t - tc
        if kind == 'whip' and -0.15 < d < 0.15:
            c = whip(c, 1 - abs(d) / 0.15, -1)
        elif kind == 'zoom' and -0.15 < d < 0.15:
            c = zoom_blur(c, (1 - abs(d) / 0.15) * 4)
        elif kind == 'flash' and -0.04 < d < 0.3:
            c = c + np.array((0.9, 0.3, 0.35), np.float32) * 0.7 * math.exp(-max(0, d) * 12)
        elif kind == 'flashw' and -0.1 < d < 0.35:
            c = c + 0.85 * math.exp(-abs(d) * 9)
    dx = dy = 0.0
    for tc in [NOT_NEC, TAP_CTA, WAY_T[5]]:
        sx, sy = shake(t, tc, amp=8, dur=0.3)
        dx += sx
        dy += sy
    if abs(dx) + abs(dy) > 0.5:
        c = cv2.warpAffine(c, np.float32([[1, 0, dx], [0, 1, dy]]), (W, H), borderMode=cv2.BORDER_REFLECT)
    if t > DUR - FADE:
        c *= 1 - 0.85 * e_inout_cubic(prog(t, DUR - FADE, DUR))
    return c


def is_fast(t):
    return t < T['turn'] or any(abs(t - tc) < 0.2 for tc, _ in TRANS)


def render(fi):
    t = fi / FPS
    if is_fast(t):
        acc = None
        for k in range(3):
            r = render_raw(max(0.0, t + (k / 3 - 0.5) * 0.5 / FPS))
            acc = r if acc is None else acc + r
        c = acc / 3
    else:
        c = render_raw(t)
    light = t >= T['cta']
    return post(c, fi, bloom=0.15 if light else 0.4, grain=0.014, ca=1.2 if t < T['turn'] else 0.0,
                vig=0.3 if light else 1.0)


def to_u8(im):
    return (np.clip(im, 0, 1) * 255 + 0.5).astype(np.uint8)[..., ::-1]


if __name__ == '__main__':
    mode = sys.argv[1]
    if mode == 'still':
        os.makedirs(f'{S}/stills', exist_ok=True)
        for ts in sys.argv[2].split(','):
            t = float(ts)
            cv2.imwrite(f'{S}/stills/s_{t:05.2f}.jpg', to_u8(render(int(round(t * FPS)))), [cv2.IMWRITE_JPEG_QUALITY, 90])
            print('still', t, flush=True)
    elif mode == 'range':
        a, b = int(sys.argv[2]), int(sys.argv[3])
        os.makedirs(f'{S}/frames_out', exist_ok=True)
        for fi in range(a, b):
            cv2.imwrite(f'{S}/frames_out/{fi:04d}.png', to_u8(render(fi)), [cv2.IMWRITE_PNG_COMPRESSION, 1])
            print('frame', fi, flush=True)
