"""IC London — "Three CV Mistakes That Could Cost You an Interview", version 2 (9:16, 30 s).

Cinematic, footage-led edit (ideas taken from the client's sample, made our own): slow-push shots of IC London's
own photography with a cool filmic grade, heavy condensed captions lower-left with a spaced-caps line and a red accent,
a "MISTAKE 0X" label with a CV-strength meter whose bars fill as each mistake is fixed, small UI cards fixing each
mistake on top of the shot, blind-strip transitions, a red staircase line, a cream panel CTA, and a logo badge end card.
Brief: hook "Your CV might be holding you back." / vague achievements / irrelevant information / poor formatting /
CTA "Make your next application count."

Usage:
  python3 reel_cv2.py still 1.0,5.0
  python3 reel_cv2.py range 0 900
"""
import os, sys, math, functools
HERE = os.path.dirname(os.path.abspath(__file__))
os.environ['REEL_WORKDIR'] = os.path.abspath(os.path.join(HERE, '..', 'workspace_cv2'))
sys.path.insert(0, os.path.join(HERE, '..', 'pipeline_ic'))
sys.path.insert(0, os.path.join(HERE, '..', 'pipeline_su'))
import numpy as np
import cv2
from reel_ic import photo, check_spr_ic, NAVY, RED, RED_L, INK, SLATE, IX, IB, IS, IM, IR, CB
from reel_su import paste, fitted, png
from reel_of import kinetic_line, word_spr, sweep, glow_add, shake, rrect_spr
from engine import *  # noqa: F401,F403
import engine as E

S = E.S
FPS = 30
WHITE_ = (1.0, 1.0, 1.0, 1.0)
CREAM = hexc('#F6EFE4')
AN = 'Anton-400'

# ------------------------------------------------------------------ timeline (VO phrase onsets measured from the lines)
T = dict(hook=0.0, intro=2.6, m1=6.5, m2=12.9, m3=18.2, panel=24.4, brand=27.2)
DUR = 30.0
NF = int(DUR * FPS)
VO = {'hook': 0.15, 'intro': 2.75, 'm1': 6.7, 'm2': 13.05, 'm3': 18.4, 'cta': 25.0}
FIX_T = [VO['m1'] + 3.8, VO['m2'] + 2.36, VO['m3'] + 2.0]     # each fix lands with its spoken advice
FADE = 1.3

SHOTS = {  # name: (photo, zoom from, zoom to, pan x, pan y, focus y)
    'h1': ('p_13585', 1.30, 1.18, 0.05, 0.0, 0.45), 'h2': ('p_2149411549', 1.28, 1.16, -0.06, 0.0, 0.5),
    'h3': ('p_14828', 1.30, 1.16, 0.05, 0.0, 0.45), 'h4': ('p_12091', 1.26, 1.14, -0.05, 0.0, 0.5),
    'intro': ('p_14267', 1.35, 1.12, 0.04, 0.02, 0.5), 'm1': ('p_146452', 1.30, 1.10, -0.06, 0.0, 0.5),
    'm2': ('p_45573', 1.25, 1.08, 0.06, 0.0, 0.45), 'm3': ('p_2147898626', 1.28, 1.08, -0.04, 0.02, 0.5),
    'brand': ('p_810', 1.25, 1.12, 0.03, 0.0, 0.5),
}

SEQ = {}


def seq(name):
    if name not in SEQ:
        SEQ[name] = Seq(name, fps=24, loop=True)
    return SEQ[name]


# ------------------------------------------------------------------ cinematic footage from stills
def grade(c, dark=0.0):
    """Cool filmic grade: navy-lifted shadows, slightly warm highlights, lower saturation."""
    lum = c.mean(axis=2, keepdims=True)
    c = c * 0.82 + lum * 0.18
    shadow = np.array([0.02, 0.05, 0.14], np.float32)
    c = c * (0.92 - 0.25 * dark) + shadow * (1 - c) * 0.6
    c = c * np.array([1.03, 1.0, 0.96], np.float32)
    return np.clip(c, 0, 1)


def shot(name, lt, dur):
    ph, z0, z1, px, py, fy = SHOTS[name]
    im = photo(ph)
    h, w = im.shape[:2]
    k = e_inout_cubic(clamp(lt / max(dur, 1e-3)))
    z = lerp(z0, z1, k)
    ch = h / z
    cw = ch * W / H
    cx = w / 2 + px * w * (k - 0.5) * 2
    cy = h * fy + py * h * (k - 0.5) * 2
    return crop_resize(im, cx, cy, cw, ch, W, H).astype(np.float32)


_yy = np.linspace(0, 1, H, dtype=np.float32)[:, None, None]


def lower_scrim(c, a=0.85):
    s = np.clip((_yy - 0.38) / 0.62, 0, 1) ** 1.25 * a
    col = np.array([0.02, 0.04, 0.11], np.float32)
    return c * (1 - s) + col * s


# ------------------------------------------------------------------ typography (sample-inspired, our own layout)
def caps(c, text, x, y, size, t, t0, color=WHITE_, track=0.22, op=1.0):
    k = prog(t, t0, t0 + 0.35)
    if k <= 0:
        return 0
    s = text_sprite(text, IB, size, color, track)
    draw(c, s, x + s.shape[1] / 2 + 30 * (1 - e_out_cubic(k)), y, opacity=min(1, k * 2) * op)
    return s.shape[1]


def heavy(c, text, x, y, size, t, t0, color=WHITE_, op=1.0):
    """Condensed headline, revealed upwards from a mask line (clipped rise)."""
    k = prog(t, t0, t0 + 0.42)
    if k <= 0:
        return 0
    s = word_spr(text, AN, size, color)
    e = e_out_cubic(k)
    h = s.shape[0]
    vis = int(h * e)
    if vis < 2:
        return s.shape[1]
    part = s[h - vis:] if e < 1 else s
    sh = blur_sprite(tint(s, (0.0, 0.02, 0.08)), 10)
    draw(c, sh, x + s.shape[1] / 2, y + 6, opacity=0.6 * e * op)
    draw(c, part, x + s.shape[1] / 2, y + (h - vis) / 2 * 0 + (h - part.shape[0]) / 2, opacity=op)
    return s.shape[1]


def meter(c, x, y, level, t, label=None, op=1.0):
    """CV-strength meter: five rising bars (our take on the sample's signal bars)."""
    for i in range(5):
        hgt = 12 + i * 7
        on = level > i
        k = clamp(level - i) if on else 0.0
        col = RED if level < 2.5 else (hexc('#F2A33A') if level < 4.5 else hexc('#3CC36B'))
        base = rrect_spr(10, hgt, 3, (1, 1, 1, 0.3))
        draw(c, base, x + i * 15, y - hgt / 2, opacity=op)
        if k > 0:
            fill = rrect_spr(10, max(2, hgt * k), 3, col)
            draw(c, fill, x + i * 15, y - max(2, hgt * k) / 2, opacity=op)
    if label:
        s = text_sprite(label, IB, 22, WHITE_, 0.22)
        draw(c, s, x + 90 + s.shape[1] / 2, y - 16, opacity=op)


def strength(t):
    lv = 1.0
    for ft in FIX_T:
        lv += e_out_cubic(prog(t, ft + 0.3, ft + 0.8))
    lv += e_out_cubic(prog(t, T['panel'] + 0.8, T['panel'] + 1.3))
    return lv


def staircase(c, x0, y0, k, steps=5, sw=90, sh=60, col=RED, width=6):
    if k <= 0:
        return
    pts = [(x0, y0)]
    for i in range(steps):
        x, y = pts[-1]
        pts += [(x + sw, y), (x + sw, y - sh)]
    seg = []
    total = len(pts) - 1
    n = k * total
    for i in range(int(n)):
        seg.append(pts[i])
    i = int(n)
    if i < total:
        f = n - i
        seg += [pts[i], (pts[i][0] + (pts[i + 1][0] - pts[i][0]) * f, pts[i][1] + (pts[i + 1][1] - pts[i][1]) * f)]
    else:
        seg.append(pts[-1])
    m = np.zeros((H, W), np.float32)
    cv2.polylines(m, [np.array(seg, np.int32)], False, 1.0, width, cv2.LINE_AA)
    c[:] = c * (1 - m[..., None]) + np.array(col[:3], np.float32) * m[..., None]


# ------------------------------------------------------------------ UI cards on top of the footage
def card(c, cx, cy, w, h, op, r=22):
    sh = blur_sprite(tint(rrect_spr(w, h, r, WHITE_), (0, 0.02, 0.08)), 22)
    draw(c, sh, cx + 8, cy + 18, opacity=0.5 * op)
    draw(c, rrect_spr(w, h, r, (1, 1, 1, 0.97)), cx, cy, opacity=op)


def strike(c, x0, x1, y, k, col=RED, width=6):
    if k <= 0:
        return
    m = np.zeros((H, W), np.float32)
    cv2.line(m, (int(x0), int(y)), (int(x0 + (x1 - x0) * clamp(k)), int(y - 4 * k)), 1.0, width, cv2.LINE_AA)
    c[:] = c * (1 - m[..., None]) + np.array(col[:3], np.float32) * m[..., None]


def ui_m1(c, t):
    t0 = T['m1']
    k = prog(t, t0 + 0.5, t0 + 0.9)
    if k <= 0:
        return
    op = min(1, k * 2)
    y = 560 + 40 * (1 - e_out_cubic(k))
    card(c, W / 2, y, 900, 250, op)
    caps(c, 'EXPERIENCE', 110, y - 82, 20, t, t0 + 0.55, SLATE)
    fx = FIX_T[0]
    kf = prog(t, fx, fx + 0.35)
    if kf < 1:
        s = word_spr('Responsible for customer service', IS, 34, INK)
        draw(c, s, 110 + s.shape[1] / 2, y - 20, opacity=op * (1 - kf))
        strike(c, 106, 114 + s.shape[1], y - 20, prog(t, VO['m1'] + 2.0, VO['m1'] + 2.5))
        kv = prog(t, VO['m1'] + 2.3, VO['m1'] + 2.6) * (1 - kf)
        if kv > 0:
            tag = pill('TOO VAGUE', IX, 20, pad_x=16, pad_y=8, fill=RED, border=None, text_color=WHITE_)
            draw(c, tag, 110 + tag.shape[1] / 2, y + 50, scale=e_out_back(kv, 2.4), opacity=kv)
    if kf > 0:
        for j, ln in enumerate(['Resolved 60+ customer queries a day', 'and cut average wait times by 20%']):
            n = int(prog(t, fx + 0.1 + j * 0.5, fx + 0.6 + j * 0.5) * len(ln))
            if n > 0:
                s = word_spr(ln[:n], IB, 34, NAVY)
                draw(c, s, 110 + s.shape[1] / 2, y - 30 + j * 50)
        kc = prog(t, fx + 1.1, fx + 1.4)
        if kc > 0:
            draw(c, check_spr_ic(52, hexc('#3CC36B')), 880, y - 6, scale=e_out_back(kc, 2.6))


def ui_m2(c, t):
    t0 = T['m2']
    items = ['Date of birth', 'Photo', 'Hobbies: socialising']
    sweep_k = prog(t, VO['m2'] + 1.9, VO['m2'] + 2.4)
    for j, it in enumerate(items):
        k = prog(t, t0 + 0.4 + j * 0.18, t0 + 0.75 + j * 0.18)
        if k <= 0:
            continue
        x = 330 + j * 0 + 700 * e_in_cubic(sweep_k)
        y = 470 + j * 120
        p = pill(it, IB, 32, pad_x=28, pad_y=16, fill=(1, 1, 1, 0.97), border=None, text_color=INK)
        op = min(1, k * 2) * (1 - sweep_k)
        if op <= 0.01:
            continue
        draw(c, blur_sprite(tint(p, (0, 0.02, 0.08)), 14), x + 6, y + 12, opacity=0.4 * op)
        draw(c, p, x, y, scale=0.9 + 0.1 * e_out_back(k, 2.0), opacity=op)
        strike(c, x - p.shape[1] / 2 + 30, x + p.shape[1] / 2 - 30, y + 2,
               prog(t, VO['m2'] + 0.6 + j * 0.3, VO['m2'] + 0.9 + j * 0.3) * (1 - sweep_k))
    kt = prog(t, FIX_T[1], FIX_T[1] + 0.4)
    if kt > 0:
        y = 560
        card(c, W / 2, y, 860, 210, min(1, kt * 2))
        caps(c, 'TAILORED TO THE JOB ADVERT', 130, y - 55, 20, t, FIX_T[1] + 0.05, SLATE)
        for j, kw in enumerate(['Customer service', 'CRM systems', 'Teamwork']):
            kk = prog(t, FIX_T[1] + 0.3 + j * 0.2, FIX_T[1] + 0.6 + j * 0.2)
            if kk > 0:
                p = pill(kw, IB, 26, pad_x=20, pad_y=12, fill=NAVY, border=None, text_color=WHITE_)
                draw(c, p, 240 + j * 270, y + 30, scale=e_out_back(kk, 2.4), opacity=min(1, kk * 3))


def ui_m3(c, t):
    t0 = T['m3']
    k = prog(t, t0 + 0.4, t0 + 0.8)
    if k <= 0:
        return
    op = min(1, k * 2)
    cx, cy, w, h = W / 2, 600, 620, 640
    card(c, cx, cy, w, h, op, r=16)
    kf = e_inout_cubic(prog(t, FIX_T[2], FIX_T[2] + 0.8))
    rng = np.random.default_rng(9)
    # messy blocks (random fonts/sizes/offsets) -> clean aligned headings + bullet lines
    rows = 9
    for i in range(rows):
        heading = i in (0, 3, 6)
        mx = cx - w / 2 + 40 + rng.uniform(0, 180)
        my = cy - h / 2 + 60 + i * 62 + rng.uniform(-20, 20)
        mw = rng.uniform(200, 460)
        mh = rng.uniform(10, 26)
        mr = rng.uniform(-6, 6)
        clx = cx - w / 2 + (50 if heading else 80)
        cly = cy - h / 2 + 70 + i * 62
        clw = 300 if heading else 440
        clh = 22 if heading else 12
        x = lerp(mx, clx, kf)
        y = lerp(my, cly, kf)
        bw = lerp(mw, clw, kf)
        bh = lerp(mh, clh, kf)
        rot = lerp(mr, 0, kf)
        col = NAVY if heading else (0.75, 0.78, 0.86, 1)
        if not heading and kf < 1:
            col = (lerp(0.4, 0.75, kf), lerp(0.42, 0.78, kf), lerp(0.5, 0.86, kf), 1)
        draw(c, rrect_spr(bw, bh, bh / 2, col), x + bw / 2, y, rot=rot, opacity=op)
        if not heading and kf > 0:
            draw(c, rrect_spr(10, 10, 5, RED), clx - 22, cly, opacity=op * kf)
    ks = prog(t, VO['m3'] + 0.5, VO['m3'] + 1.0) * (1 - kf)
    if ks > 0:
        tag = pill('HARD TO SKIM', IX, 20, pad_x=16, pad_y=8, fill=RED, border=None, text_color=WHITE_)
        draw(c, tag, cx + w / 2 - 120, cy - h / 2 + 26, scale=e_out_back(ks, 2.4), opacity=ks)
    if kf > 0.95:
        kc = prog(t, FIX_T[2] + 0.8, FIX_T[2] + 1.1)
        draw(c, check_spr_ic(56, hexc('#3CC36B')), cx + w / 2 - 50, cy - h / 2 + 40, scale=e_out_back(kc, 2.6))


# ------------------------------------------------------------------ scenes
def caption_block(c, t, label, l1, l2, accent, t0, lvl=None):
    """Lower-left caption: meter + spaced label, then a two-line heavy headline with a red accent line."""
    y0 = 1330
    if lvl is not None:
        meter(c, 64, y0, lvl, t, op=min(1, prog(t, t0, t0 + 0.3) * 2))
        caps(c, label, 150, y0 - 16, 22, t, t0, RED_L)
    else:
        caps(c, label, 64, y0 - 16, 22, t, t0, RED_L)
    heavy(c, l1, 60, y0 + 90, 104, t, t0 + 0.1)
    heavy(c, l2, 60, y0 + 210, 104, t, t0 + 0.22, color=accent)


def sc_hook(t):
    cut = [0.0, 0.65, 1.3, 1.95, 99]
    names = ['h1', 'h2', 'h3', 'h4']
    i = max(j for j in range(4) if cut[j] <= t)
    lt = t - cut[i]
    c = grade(shot(names[i], lt, 0.65 if i < 3 else 0.7), dark=0.15)
    if lt < 0.04 and i:
        c = c + 0.15
    c = lower_scrim(c, 0.9)
    caps(c, 'A QUICK CV CHECK', 64, 1150, 26, t, 0.1, RED_L)
    heavy(c, 'Your CV', 60, 1250, 118, t, 0.15)
    heavy(c, 'might be holding', 60, 1380, 104, t, 0.45)
    heavy(c, 'you back.', 60, 1500, 104, t, 0.75, color=RED_L)
    staircase(c, 60, 1760, prog(t, 0.6, 2.4), steps=6, sw=80, sh=46)
    return c


def sc_intro(t):
    t0 = T['intro']
    c = grade(shot('intro', t - t0, T['m1'] - t0), dark=0.1)
    c = lower_scrim(c, 0.9)
    meter(c, 64, 1330, strength(t), t, op=min(1, prog(t, t0 + 0.2, t0 + 0.5) * 2))
    caps(c, 'CV STRENGTH: WEAK', 150, 1314, 22, t, t0 + 0.2, RED_L)
    k3 = prog(t, VO['intro'] + 0.6, VO['intro'] + 1.0)
    if k3 > 0:
        s = word_spr('3', AN, 300, RED_L)
        draw(c, blur_sprite(tint(s, (0, 0.02, 0.08)), 14), 150, 1560, opacity=0.5 * k3)
        draw(c, s, 140, 1550, scale=0.8 + 0.2 * e_out_back(k3, 2.0), opacity=min(1, k3 * 2))
    heavy(c, 'mistakes that', 270, 1480, 92, t, VO['intro'] + 0.8)
    heavy(c, 'could cost you', 270, 1585, 92, t, VO['intro'] + 2.0)
    caps(c, 'AN INTERVIEW', 276, 1680, 30, t, VO['intro'] + 2.4, RED_L, track=0.3)
    return c


def sc_m(i):
    key = ['m1', 'm2', 'm3'][i]
    labels = [('Vague', 'achievements.'), ('Irrelevant', 'information.'), ('Poor', 'formatting.')]
    ui = [ui_m1, ui_m2, ui_m3][i]

    def f(t):
        t0 = T[key]
        nxt = [T['m2'], T['m3'], T['panel']][i]
        c = grade(shot(key, t - t0, nxt - t0), dark=0.12)
        c = lower_scrim(c, 0.92)
        ui(c, t)
        caption_block(c, t, f'MISTAKE 0{i + 1}', labels[i][0], labels[i][1], RED_L, t0 + 0.05, lvl=strength(t))
        # vertical side label (sample-inspired)
        s = text_sprite(['ACHIEVEMENTS', 'RELEVANCE', 'LAYOUT'][i], IB, 20, (1, 1, 1, 0.7), 0.3)
        s = np.ascontiguousarray(np.rot90(s, 1))
        draw(c, s, W - 50, 1100, opacity=min(1, prog(t, t0 + 0.3, t0 + 0.7)))
        return c
    return f


@functools.lru_cache(maxsize=1)
def cream_base():
    return np.ones((H, W, 3), np.float32) * np.array(CREAM[:3], np.float32)


def sc_panel(t):
    t0 = T['panel']
    # the m3 shot keeps playing behind; the cream panel wipes in from the right (sample idea, our layout)
    under = grade(shot('m3', t - T['m3'], T['panel'] - T['m3'] + 1.0), dark=0.12)
    under = lower_scrim(under, 0.92)
    k = e_inout_cubic(prog(t, t0, t0 + 0.55))
    xw = int(W * (1 - k))
    c = under.copy()
    c[:, xw:] = cream_base()[:, xw:]
    if 0 < k < 1:
        c[:, max(0, xw - 8):xw] = np.array(RED[:3], np.float32)
    caps(c, 'MAKE YOUR NEXT', 104, 700, 36, t, VO['cta'] - 0.05, INK, track=0.3)
    heavy(c, 'APPLICATION', 96, 850, 196, t, VO['cta'] + 0.3, color=NAVY)
    heavy(c, 'COUNT.', 96, 1060, 196, t, VO['cta'] + 0.75, color=RED)
    kl = prog(t, VO['cta'] + 1.0, VO['cta'] + 1.4)
    if kl > 0:
        draw(c, rrect_spr(max(4, 520 * e_out_cubic(kl)), 8, 4, INK), 104 + 260 * e_out_cubic(kl), 1200)
    staircase(c, 120, 1600, prog(t, t0 + 0.6, t0 + 2.4), steps=6, sw=130, sh=70, width=7)
    meter(c, 120, 1330, strength(t), t, op=min(1, prog(t, t0 + 0.6, t0 + 1.0) * 2))
    caps(c, 'CV STRENGTH: STRONG', 210, 1314, 22, t, t0 + 1.0, NAVY)
    return c


def sc_brand(t):
    t0 = T['brand']
    c = grade(shot('brand', t - t0, DUR - t0), dark=0.45)
    c = c * 0.6 + np.array([0.02, 0.04, 0.12], np.float32) * 0.4
    k = prog(t, t0 + 0.1, t0 + 0.6)
    if k > 0:
        ring = ring_sprite(380, 160 + 6 * math.sin(t * 3), 3, RED, glow=10)
        draw(c, ring, W / 2, 780, opacity=k)
        disc = rrect_spr(290, 290, 145, (1, 1, 1, 1))
        d2 = disc.copy()
        paste(d2, fitted('logo_b', png('logo_full'), width=230), 145, 150)
        draw(c, d2, W / 2, 780, scale=0.85 + 0.15 * e_out_back(k, 2.0), opacity=min(1, k * 2))
    kinetic_line(c, 'IC London', W / 2, 1030, 92, t, t0 + 0.35, color=WHITE_, fname=CB, shadow_op=0.5,
                 sweep_t=t0 + 0.9)
    ln = text_sprite('SQE  ·  LAW  ·  HR  ·  FINANCE', IB, 24, RED_L, 0.25)
    caps(c, 'SQE  ·  LAW  ·  HR  ·  FINANCE', W / 2 - ln.shape[1] / 2 - 15, 1110, 24, t, t0 + 0.6, RED_L, track=0.25)
    kw = prog(t, t0 + 0.8, t0 + 1.1)
    if kw > 0:
        s = word_spr('iclondon.co.uk', IB, 34, WHITE_)
        draw(c, s, W / 2, 1180, opacity=kw)
    return c


SCENES = [(T['hook'], T['intro'], sc_hook), (T['intro'], T['m1'], sc_intro), (T['m1'], T['m2'], sc_m(0)),
          (T['m2'], T['m3'], sc_m(1)), (T['m3'], T['panel'], sc_m(2)), (T['panel'], T['brand'], sc_panel),
          (T['brand'], 99, sc_brand)]
BLINDS = [T['intro'], T['m1'], T['m2'], T['m3'], T['brand']]
BL = 0.45


def scene_at(t):
    for a, b, f in SCENES:
        if a <= t < b:
            return f
    return SCENES[-1][2]


def blinds(prev, nxt, p, n=6):
    """Blind-strip transition: vertical strips of the next shot slide in with a stagger."""
    out = prev.copy()
    sw = W // n
    for i in range(n):
        k = e_inout_cubic(clamp(p * 1.5 - i * 0.1))
        if k <= 0:
            continue
        x0, x1 = i * sw, (i + 1) * sw if i < n - 1 else W
        off = int((1 - k) * H * (1 if i % 2 == 0 else -1))
        strip = np.roll(nxt[:, x0:x1], off, axis=0)
        if off > 0:
            strip[:off] = prev[:off, x0:x1]
        elif off < 0:
            strip[off:] = prev[off:, x0:x1]
        out[:, x0:x1] = strip
        if 0 < k < 1:
            edge = max(0, min(H - 4, (off if off > 0 else H + off)))
            out[edge:edge + 4, x0:x1] = np.array(RED[:3], np.float32)
    return out


def render_raw(t):
    c = scene_at(t)(t)
    for tb in BLINDS:
        d = t - tb
        if 0 <= d < BL:
            prev = scene_at(tb - 0.01)(tb - 0.01 + d * 0.3)
            c = blinds(prev, c, d / BL)
    dx = dy = 0.0
    for tc in FIX_T + [T['panel']]:
        sx, sy = shake(t, tc, amp=6, dur=0.3)
        dx += sx
        dy += sy
    if abs(dx) + abs(dy) > 0.5:
        c = cv2.warpAffine(c, np.float32([[1, 0, dx], [0, 1, dy]]), (W, H), borderMode=cv2.BORDER_REFLECT)
    if t > DUR - FADE:
        c *= 1 - 0.88 * e_inout_cubic(prog(t, DUR - FADE, DUR))
    return c


def is_fast(t):
    return t < T['intro'] or any(0 <= t - tb < BL for tb in BLINDS)


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
    cream = T['panel'] + 0.5 <= t < T['brand']
    return post(c, fi, bloom=0.12 if cream else 0.3, grain=0.022, vig=0.3 if cream else 1.0)


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
