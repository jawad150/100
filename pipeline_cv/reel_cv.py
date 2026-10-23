"""IC London — "Three CV Mistakes That Could Cost You an Interview" (9:16, 30 s).

Look (deliberately unlike the dark route-map law reel): bright editorial "recruiter's desk". One 3D paper CV is
shot from cinematic angles, marked up live with a red marker (circles, strike-throughs, scribbles, handwritten notes),
then fixed mistake by mistake: 01 vague achievements -> 02 irrelevant information -> 03 poor formatting.
Advice from the National Careers Service and Prospects CV guides; the rewritten achievement is Prospects' own example.
Brand: IC London navy #00247D / red #CF142B, Inter + Cardo (site fonts), Caveat for handwriting.

Usage:
  python3 reel_cv.py still 1.0,5.0
  python3 reel_cv.py range 0 900
"""
import os, sys, math, functools
HERE = os.path.dirname(os.path.abspath(__file__))
os.environ['REEL_WORKDIR'] = os.path.abspath(os.path.join(HERE, '..', 'workspace_cv'))
sys.path.insert(0, os.path.join(HERE, '..', 'pipeline_ic'))
sys.path.insert(0, os.path.join(HERE, '..', 'pipeline_su'))
import numpy as np
import cv2
import reel_ic as RI
from reel_ic import (txt, icon, photo, check_spr_ic, NAVY, NAVY_D, RED, RED_L, INK, SLATE, ICE, GOLD,
                     IX, IB, IS, IM, IR, CB, CI)
from reel_su import paste, fitted, png, ripple, cursor
from reel_of import kinetic_line, word_spr, sweep, glow_add, whip, zoom_blur, shake, rrect_spr, glass
from engine import *  # noqa: F401,F403
import engine as E

S = E.S
FPS = 30
WHITE_ = (1.0, 1.0, 1.0, 1.0)
PAPER = hexc('#FFFFFF')
CV_RED = hexc('#E0182F')
HW = 'Caveat-700'

# ------------------------------------------------------------------ timeline (VO phrase onsets from vo_cv.py)
T = dict(hook=0.0, intro=2.6, m1=6.6, m2=13.0, m3=18.5, cta=24.6)
DUR = 30.0
NF = int(DUR * FPS)
VO = {'hook': 0.15, 'intro': 2.75, 'm1': 6.75, 'm2': 13.15, 'm3': 18.65, 'cta': 24.85}
M1_FIX = VO['m1'] + 3.8            # "show what you did, with real examples"
M2_TAILOR = VO['m2'] + 2.36        # "Tailor every line to the job..."
M3_FIX = VO['m3'] + 2.0            # "Use clear headings, bullet points..."
FADE = 1.3

SEQ = {}


def seq(name):
    if name not in SEQ:
        SEQ[name] = Seq(name, fps=24, loop=True)
    return SEQ[name]


# ------------------------------------------------------------------ background: bright desk
@functools.lru_cache(maxsize=1)
def desk():
    im = photo('p_14267')
    h, w = im.shape[:2]
    c = crop_resize(im, w / 2, h / 2, h * W / H, h, W, H).astype(np.float32)
    c = cv2.GaussianBlur(c, (0, 0), 18)
    paper = np.array([0.965, 0.955, 0.94], np.float32)
    return c * 0.28 + paper * 0.72


def bg(t):
    c = desk().copy()
    xs = np.linspace(0, 1, W, dtype=np.float32)[None, :, None]
    ys = np.linspace(0, 1, H, dtype=np.float32)[:, None, None]
    u = xs * 0.7 + ys * 0.4 - (0.2 + 0.1 * math.sin(t * 0.35))
    c += np.exp(-(u / 0.25) ** 2) * np.array([1.0, 0.95, 0.85], np.float32) * 0.08
    return c


# ------------------------------------------------------------------ the CV page (fictional candidate)
PW_, PH_ = 820, 1160


def L(key, text, clean, messy):
    return dict(key=key, text=text, clean=clean, messy=messy)


# clean = (font, size, colour, x, y) ; messy = (font, size, colour, x, y)
BASE = [
    L('name', 'Alex Morgan', (CB, 60, INK, 60, 92), (IX, 52, INK, 120, 86)),
    L('role', 'Customer Service Advisor', (IM, 28, RED, 60, 150), (CI, 34, SLATE, 210, 146)),
    L('contact', 'alex.morgan@email.com  ·  London', (IR, 20, SLATE, 60, 190), (IR, 17, SLATE, 300, 186)),
    L('h_profile', 'PROFILE', (IX, 22, NAVY, 60, 268), (CI, 32, INK, 40, 262)),
    L('profile', 'Friendly advisor with three years in busy retail.', (IR, 22, INK, 60, 306),
      (IM, 19, INK, 100, 296)),
    L('h_exp', 'EXPERIENCE', (IX, 22, NAVY, 60, 378), (HW, 38, CV_RED, 150, 352)),
    L('job', 'Customer Advisor  ·  Northside Retail  ·  2022–now', (IB, 22, INK, 60, 418), (IR, 18, INK, 30, 392)),
    L('b1', 'Responsible for customer service', (IR, 22, INK, 84, 460), (IR, 21, INK, 60, 424)),
    L('b2', 'Helped with stock and the tills', (IR, 22, INK, 84, 496), (IM, 17, INK, 140, 452)),
    L('h_pers', 'PERSONAL DETAILS', (IX, 22, NAVY, 60, 576), (CB, 30, INK, 70, 506)),
    L('p1', 'Date of birth: 14/03/1999', (IR, 22, INK, 60, 614), (IR, 18, INK, 260, 540)),
    L('p2', 'Photo: attached', (IR, 22, INK, 60, 648), (IX, 22, INK, 40, 566)),
    L('p3', 'Interests: socialising, reading', (IR, 22, INK, 60, 682), (CI, 24, INK, 160, 594)),
    L('h_skills', 'SKILLS', (IX, 22, NAVY, 60, 760), (IX, 30, RED, 330, 640)),
    L('skills', 'Communication  ·  Problem solving', (IR, 22, INK, 60, 798), (IM, 18, INK, 50, 670)),
    L('h_edu', 'EDUCATION', (IX, 22, NAVY, 60, 876), (HW, 34, INK, 60, 712)),
    L('edu', 'BA (Hons) Business  ·  2021', (IR, 22, INK, 60, 914), (IR, 18, INK, 230, 740)),
]
FIX1 = ['Remained calm under pressure when answering', 'telephone queries from up to 100 customers a day']
SKILLS_NEW = 'Complaint handling  ·  CRM systems  ·  Teamwork'
REMOVE = ['h_pers', 'p1', 'p2', 'p3']


def tsp(text, fname, size, col):
    return word_spr(text, fname, size, col)


def paste_left(dst, spr, x, y, op=1.0):
    paste(dst, spr, x + spr.shape[1] / 2 - 3, y, op)


def marker_path(pts, k, jitter_seed=0):
    k = clamp(k)
    n = max(2, int(len(pts) * k))
    return np.array(pts[:n], np.int32)


def ellipse_pts(cx, cy, rx, ry, seed=0, turns=1.08):
    rng = np.random.default_rng(seed)
    pts = []
    n = 90
    for i in range(n):
        a = -2.4 + turns * 2 * math.pi * i / n
        wob = 1 + 0.05 * math.sin(i * 0.4 + seed) + rng.normal(0, 0.006)
        pts.append((cx + rx * wob * math.cos(a), cy + ry * wob * math.sin(a)))
    return pts


def draw_marker(dst, pts, k, width=7, col=CV_RED):
    p = marker_path(pts, k)
    if len(p) < 2:
        return
    a = np.zeros(dst.shape[:2], np.float32)
    cv2.polylines(a, [p], False, 1.0, width, cv2.LINE_AA)
    a = a[..., None] * 0.9
    dst[..., :3] = dst[..., :3] * (1 - a) + np.array(col[:3], np.float32) * a


def cv_page(t):
    """Render the CV for time t: cumulative fixes (m1 rewrite, m2 removals, m3 clean layout) + marker annotations."""
    spr = rrect_spr(PW_, PH_, 10, PAPER, border=(0.0, 0.08, 0.3, 0.12), bw=2)
    fm = prog(t, M3_FIX, M3_FIX + 0.8)                 # messy -> clean formatting
    k_rm = prog(t, VO['m2'] + 2.0, VO['m2'] + 2.6)     # irrelevant lines leave
    k_fix1 = prog(t, M1_FIX, M1_FIX + 1.4)             # vague bullet rewritten (typewriter)
    pos = {}
    after_b1 = False
    room = 36 * e_inout_cubic(prog(t, M1_FIX - 0.2, M1_FIX + 0.3))
    for i, el in enumerate(BASE):
        key = el['key']
        stag = clamp(fm * 1.6 - i * 0.035)
        e = e_inout_cubic(stag)
        cf, cs, cc, cx, cy = el['clean']
        mf, ms, mc, mx, my = el['messy']
        x = lerp(mx, cx, e)
        y = lerp(my, cy, e) + (room if after_b1 else 0.0)
        if key == 'b1':
            after_b1 = True
        if key in REMOVE:
            if k_rm >= 1:
                continue
            dy = -60 * e_in_cubic(k_rm)
            x += 500 * e_in_cubic(k_rm)
            op = 1 - k_rm
            y += dy
        else:
            op = 1.0
        # once the irrelevant block has gone, everything below it closes the gap
        if key in ('h_skills', 'skills', 'h_edu', 'edu') and k_rm > 0:
            y -= e_inout_cubic(k_rm) * lerp(125, 140, e)
        pos[key] = (x, y)
        if key == 'b1' and k_fix1 > 0:
            continue
        text = SKILLS_NEW if (key == 'skills' and t >= M2_TAILOR + 0.6) else el['text']
        if op <= 0.01:
            continue
        if e < 1:
            paste_left(spr, tsp(text, mf, ms, mc), x, y, op * (1 - e))
        if e > 0:
            paste_left(spr, tsp(text, cf, cs, cc), x, y, op * e)
        if key in ('b1', 'b2') and e > 0:
            paste(spr, rrect_spr(8, 8, 4, NAVY), x - 18, y + 1, op * e)
        if key.startswith('h_') and e > 0:
            paste_left(spr, rrect_spr(PW_ - 120, 2, 1, (0.0, 0.14, 0.49, 0.25)), 60, y + 22, op * e)
    # the rewritten achievement (Prospects' example), typed in with a navy highlight
    if k_fix1 > 0:
        x, y = pos['b1']
        n = int(k_fix1 * (len(FIX1[0]) + len(FIX1[1])))
        hl = rrect_spr(PW_ - 130, 74, 8, (0.0, 0.14, 0.49, 0.08))
        paste_left(spr, hl, x - 10, y + 16, min(1, k_fix1 * 3))
        for j, ln in enumerate(FIX1):
            m = clamp(n - (len(FIX1[0]) if j else 0), 0, len(ln))
            if m > 0:
                paste_left(spr, tsp(ln[:int(m)], IS, 21, NAVY), x, y + j * 32, 1.0)
        if k_fix1 >= 1:
            paste(spr, cv2.resize(check_spr_ic(40, NAVY), (34, 34)), PW_ - 50, y + 16)
    # ---- red marker annotations (drawn on the paper so they tilt with it)
    if 'b1' in pos and t < M1_FIX + 0.2:
        x, y = pos['b1']
        k = prog(t, VO['m1'] + 0.6, VO['m1'] + 1.3)
        if k > 0:
            draw_marker(spr, ellipse_pts(x + 190, y, 230, 30, seed=1), k)
            if k > 0.8:
                paste_left(spr, tsp('vague!', HW, 44, CV_RED), x + 440, y - 12, prog(t, VO['m1'] + 1.2, VO['m1'] + 1.5))
    for j, key in enumerate(['p1', 'p2', 'p3']):
        if key in pos and k_rm < 1:
            x, y = pos[key]
            k = prog(t, VO['m2'] + 0.5 + j * 0.35, VO['m2'] + 0.8 + j * 0.35)
            if k > 0:
                w_ = tsp(BASE[[b['key'] for b in BASE].index(key)]['text'], IR, 22, INK).shape[1]
                draw_marker(spr, [(x - 6, y + 2), (x + w_ + 6, y - 2)], k, width=6)
    if 'p3' in pos and k_rm < 1:
        x, y = pos['p3']
        kk = prog(t, VO['m2'] + 1.5, VO['m2'] + 1.8) * (1 - k_rm)
        if kk > 0:
            paste_left(spr, tsp('not needed', HW, 42, CV_RED), x + 420, y - 30, kk)
    km = prog(t, VO['m3'] + 0.5, VO['m3'] + 1.4) * (1 - prog(t, M3_FIX, M3_FIX + 0.3))
    if km > 0:
        zig = [(560 + 18 * (i % 2), 260 + i * 26) for i in range(18)]
        draw_marker(spr, zig, km, width=6)
        draw_marker(spr, ellipse_pts(330, 560, 300, 230, seed=4, turns=1.0), km)
        paste_left(spr, tsp('messy!', HW, 56, CV_RED), 520, 830, km)
    return spr


def draw_page(c, t, cx, cy, w, rx=0.0, ry=0.0, rz=0.0, op=1.0):
    spr = cv_page(t)
    sh = blur_sprite(tint(rrect_spr(PW_, PH_, 10, WHITE_), (0.05, 0.06, 0.12)), 26)
    draw3d(c, sh, cx + 26, cy + 40, 0, w * 1.02, None, rx=rx, ry=ry, rz=rz, opacity=0.45 * op)
    draw3d(c, spr, cx, cy, 0, w, None, rx=rx, ry=ry, rz=rz, opacity=op)


# ------------------------------------------------------------------ typography helpers
_yy = np.linspace(0, 1, H, dtype=np.float32)[:, None, None]


def top_plate(c, h0=0.215, h1=0.30):
    """Opaque paper band behind the headline area, softening into the scene below (keeps titles clean)."""
    a = np.clip((h1 - _yy) / (h1 - h0), 0, 1) ** 1.3
    return c * (1 - a) + np.array([0.982, 0.977, 0.967], np.float32) * a

def big_number(c, n, t, t0, x=150, y=250):
    k = prog(t, t0, t0 + 0.5)
    if k <= 0:
        return
    s = word_spr(n, CB, 190, RED)
    draw(c, blur_sprite(tint(s, (0.4, 0.02, 0.05)), 14), x + 6, y + 10, opacity=0.25 * k)
    draw(c, s, x, y + 40 * (1 - e_out_cubic(k)), scale=0.85 + 0.15 * e_out_back(k, 1.8), opacity=min(1, k * 2))


def section_title(c, l1, l2, t, t0, x=300):
    for j, ln in enumerate((l1, l2)):
        k = prog(t, t0 + 0.12 + j * 0.12, t0 + 0.5 + j * 0.12)
        if k <= 0:
            continue
        s = word_spr(ln, IX, 62, NAVY if j == 0 else INK)
        draw(c, s, x + s.shape[1] / 2 + 40 * (1 - e_out_cubic(k)), 215 + j * 72, opacity=min(1, k * 2))


def tip(c, text, t, t0, y=1700, src=None):
    k = prog(t, t0, t0 + 0.4)
    if k <= 0:
        return
    p = pill(text, IX, 32, pad_x=34, pad_y=18, fill=NAVY, border=None, text_color=WHITE_)
    draw(c, blur_sprite(tint(p, (0, 0.05, 0.2)), 14), W / 2 + 6, y + 14, opacity=0.4 * k)
    draw(c, p, W / 2, y, scale=0.85 + 0.15 * e_out_back(k, 2.0), opacity=min(1, k * 3))
    if src:
        txt(c, src, W / 2, y + 74, 22, SLATE, IM, k)


def chip(c, text, x, y, t, t0):
    k = prog(t, t0, t0 + 0.35)
    if k <= 0:
        return
    p = pill(text, IB, 28, pad_x=26, pad_y=14, fill=(1, 1, 1, 0.96), border=(0.0, 0.14, 0.49, 0.25),
             text_color=INK, dot=RED)
    draw(c, blur_sprite(tint(p, (0, 0.05, 0.2)), 10), x + 4, y + 10, opacity=0.25 * k)
    draw(c, p, x, y, scale=0.85 + 0.15 * e_out_back(k, 2.4), opacity=min(1, k * 3))


# ------------------------------------------------------------------ scenes
HOOK_SHOTS = [  # (cx, cy, w, rx, ry, rz) — extreme cinematic angles on the paper
    (620, 1250, 1500, 52, -28, -8),
    (420, 900, 1700, 8, 24, 14),
    (560, 1150, 1250, 36, 30, -4),
]


def sc_hook(t):
    c = bg(t)
    i = min(int(t / 0.55), 3)
    lt = t - i * 0.55
    if i < 3:
        cx, cy, w, rx, ry, rz = HOOK_SHOTS[i]
        k = lt / 0.55
        draw_page(c, t, cx - 30 * k, cy - 20 * k, w * (1 + 0.06 * k), rx, ry, rz + 3 * k)
        if lt < 0.04:
            c = c * 0.85 + 0.15
    else:
        k = e_out_cubic(prog(t, 1.65, 2.4))
        draw_page(c, t, W / 2, lerp(1300, 1180, k), lerp(980, 760, k), lerp(30, 14, k), lerp(-26, -12, k), lerp(-6, -3, k))
        icon(c, 'marker', t, 860, 1500, 260, 1.8)
    # title over a soft paper plate
    c = top_plate(c, 0.2, 0.27)
    kinetic_line(c, 'Your CV might be', W / 2, 190, 74, t, 0.1, color=INK, fname=IX, shadow_op=0.0)
    kinetic_line(c, 'holding you back.', W / 2, 310, 112, t, 0.45, color=RED, fname=CB, shadow_op=0.0, sweep_t=1.3)
    ku = prog(t, 1.2, 1.7)
    if ku > 0:
        pts = [(W / 2 - 330 + 660 * u, 382 + 6 * math.sin(u * 9)) for u in np.linspace(0, 1, 60)]
        line = np.zeros((H, W), np.float32)
        cv2.polylines(line, [marker_path(pts, ku)], False, 1.0, 9, cv2.LINE_AA)
        c = c * (1 - line[..., None] * 0.9) + np.array(CV_RED[:3], np.float32) * line[..., None] * 0.9
    return c


def sc_intro(t):
    t0 = T['intro']
    c = bg(t)
    draw_page(c, t, W / 2, 1180, 760, 14 + 2 * math.sin(t), -12 + 3 * math.sin(t * 0.7), -3)
    # three red tabs on the page edge
    for j in range(3):
        k = prog(t, t0 + 0.4 + j * 0.25, t0 + 0.7 + j * 0.25)
        if k > 0:
            y = 880 + j * 210
            tab = rrect_spr(120, 90, 18, CV_RED)
            paste(tab, word_spr(str(j + 1), IX, 44, WHITE_), 72, 46)
            draw(c, blur_sprite(tint(tab, (0.3, 0, 0.02)), 10), 930 + 6, y + 10, opacity=0.35 * k)
            draw(c, tab, 930 - 40 * (1 - e_out_back(k, 2.0)), y, opacity=min(1, k * 3))
    # magnifier scans the page
    km = prog(t, t0 + 0.6, T['m1'] - 0.3)
    if km > 0:
        x = lerp(300, 700, 0.5 + 0.5 * math.sin(km * math.pi * 1.5))
        y = lerp(780, 1550, e_inout_cubic(km))
        icon(c, 'magnifier', t, x, y, 300, t0 + 0.6, glow=(0.6, 0.75, 1.0))
    c = top_plate(c, 0.21, 0.28)
    k3 = prog(t, VO['intro'] + 0.6, VO['intro'] + 1.1)
    if k3 > 0:
        s = word_spr('3', CB, 230, RED)
        draw(c, s, 230, 260, scale=0.8 + 0.2 * e_out_back(k3, 2.2), opacity=min(1, k3 * 2))
    kinetic_line(c, 'common mistakes', 640, 210, 60, t, VO['intro'] + 0.8, color=NAVY, fname=IX, shadow_op=0.0)
    kinetic_line(c, 'that could cost you', 640, 290, 46, t, VO['intro'] + 2.0, color=INK, fname=IM, shadow_op=0.0)
    kinetic_line(c, 'an interview', 640, 352, 46, t, VO['intro'] + 2.4, color=RED, fname=IB, shadow_op=0.0)
    return c


def sc_m1(t):
    t0 = T['m1']
    c = bg(t)
    k = e_inout_cubic(prog(t, t0, t0 + 0.9))
    # camera pushes in on the experience bullets
    w = lerp(760, 1100, k)
    fx, fy = 410, 470                      # focus point on the page
    cx = W / 2 - (fx - PW_ / 2) * w / PW_ * k
    cy = lerp(1180, 1050 - (fy - PH_ / 2) * w / PW_, k)
    draw_page(c, t, cx, cy, w, lerp(14, 8, k) + 1.5 * math.sin(t), lerp(-12, 4, k), lerp(-3, -1, k))
    c = top_plate(c)
    big_number(c, '01', t, t0 + 0.05)
    section_title(c, 'Vague', 'achievements', t, t0 + 0.1)
    tip(c, "Don't list duties — show evidence", t, VO['m1'] + 2.0, y=1640)
    kk = prog(t, M1_FIX + 1.4, M1_FIX + 1.7)
    if kk > 0:
        txt(c, 'Example from Prospects’ CV guide', W / 2, 1730, 24, SLATE, IM, kk)
    icon(c, 'marker', t, 900, 1450, 230, t0 + 0.4)
    return c


@functools.lru_cache(maxsize=1)
def advert_spr():
    w, h = 470, 520
    spr = rrect_spr(w, h, 26, (1, 1, 1, 1), border=(0.0, 0.14, 0.49, 0.2), bw=2)
    paste(spr, rrect_spr(w, 90, 26, NAVY), w / 2, 45)
    paste(spr, rrect_spr(w, 40, 0, NAVY), w / 2, 70)
    paste(spr, text_sprite('JOB ADVERT', IX, 26, WHITE_, 0.1), w / 2, 48)
    t1 = text_sprite('Customer Service Advisor', IB, 26, INK)
    paste(spr, t1, 30 + t1.shape[1] / 2, 132)
    y = 190
    for ln, hl in [('You will handle', False), ('complaint handling', True), ('using our CRM systems', True),
                   ('as part of a friendly', False), ('teamwork-first team.', True)]:
        ts = text_sprite(ln, IM if not hl else IB, 24, INK if not hl else NAVY)
        if hl:
            paste(spr, rrect_spr(ts.shape[1] + 16, 38, 8, (1.0, 0.85, 0.3, 0.55)), 30 + ts.shape[1] / 2, y)
        paste(spr, ts, 30 + ts.shape[1] / 2, y)
        y += 58
    return spr


def sc_m2(t):
    t0 = T['m2']
    c = bg(t)
    k = e_inout_cubic(prog(t, t0, t0 + 0.8))
    w = lerp(1100, 1000, k)
    fx, fy = 410, 640
    ka = e_out_cubic(prog(t, M2_TAILOR - 0.1, M2_TAILOR + 0.5))
    cx = W / 2 - (fx - PW_ / 2) * w / PW_ - 170 * ka
    cy = 1080 - (fy - PH_ / 2) * w / PW_
    draw_page(c, t, cx, cy, w, 8 + 1.5 * math.sin(t), 4 - 8 * ka, -1)
    if ka > 0:
        adv = advert_spr()
        x = lerp(1400, 830, ka)
        draw3d(c, blur_sprite(tint(adv, (0.05, 0.06, 0.12)), 18), x + 18, 1140, 0, adv.shape[1], None, ry=-14,
               opacity=0.4 * ka)
        draw3d(c, adv, x, 1110, 0, adv.shape[1], None, ry=-14, rz=3, opacity=min(1, ka * 2))
        kc = prog(t, M2_TAILOR + 0.5, M2_TAILOR + 1.1)
        if kc > 0:
            for j in range(3):
                y = 1090 + j * 62
                dots = np.zeros((H, W), np.float32)
                x0, x1 = 520, int(lerp(520, 640, kc))
                for xx in range(x0, x1, 18):
                    cv2.circle(dots, (xx, int(lerp(1300, y, (xx - x0) / 120.0))), 4, 1.0, -1, cv2.LINE_AA)
                c = c * (1 - dots[..., None]) + np.array(RED[:3], np.float32) * dots[..., None]
    c = top_plate(c)
    big_number(c, '02', t, t0 + 0.05)
    section_title(c, 'Irrelevant', 'information', t, t0 + 0.1)
    tip(c, 'Tailor your CV to the job advert', t, M2_TAILOR + 0.2, y=1680, src='National Careers Service')
    return c


def sc_m3(t):
    t0 = T['m3']
    c = bg(t)
    k = e_inout_cubic(prog(t, t0, t0 + 0.8))
    kf = e_inout_cubic(prog(t, M3_FIX, M3_FIX + 0.9))
    w = lerp(1000, 760, k)
    draw_page(c, t, lerp(540, W / 2, k), lerp(1000, 1110, k), w, lerp(8, 10, k) + 1.5 * math.sin(t),
              lerp(-4, -14, k) + 14 * kf, lerp(-1, -4, k) + 4 * kf)
    c = top_plate(c)
    big_number(c, '03', t, t0 + 0.05)
    section_title(c, 'Poor', 'formatting', t, t0 + 0.1)
    for j, (label, tt) in enumerate([('Clear font, size 11+', M3_FIX + 0.2), ('Headings & bullet points', M3_FIX + 0.7),
                                     ('One consistent style', VO['m3'] + 4.2), ('Up to two A4 pages', VO['m3'] + 4.8)]):
        chip(c, label, 300 if j % 2 == 0 else 780, 1700 + (j // 2) * 92, t, tt)
    ks = prog(t, VO['m3'] + 4.8, VO['m3'] + 5.1)
    if ks > 0:
        txt(c, 'National Careers Service · Prospects', W / 2, 1880, 22, SLATE, IM, ks)
    if kf > 0:
        icon(c, 'paperclip', t, 220, 600, 220, M3_FIX + 0.3)
    return c


def sc_cta(t):
    t0 = T['cta']
    c = bg(t)
    k = e_inout_cubic(prog(t, t0, t0 + 0.9))
    draw_page(c, t, lerp(W / 2, 760, k), lerp(1110, 1260, k), lerp(760, 520, k), lerp(10, 18, k),
              lerp(0, -22, k), lerp(0, 6, k))
    # "ready" stamp on the fixed CV
    ks = prog(t, t0 + 0.6, t0 + 0.9)
    if ks > 0:
        st = pill('READY TO SEND', IX, 30, pad_x=26, pad_y=14, fill=(1, 1, 1, 0.9), border=NAVY, text_color=NAVY)
        draw(c, st, 770, 1300, scale=1.6 - 0.6 * e_out_back(ks, 2.0), rot=-10, opacity=min(1, ks * 3))
    a = np.clip(1 - np.linspace(0, 1, H, dtype=np.float32)[:, None, None] / 0.5, 0, 1) ** 1.1 * 0.95
    c = c * (1 - a) + np.array([0.985, 0.98, 0.97], np.float32) * a
    kl = prog(t, t0 + 0.1, t0 + 0.6)
    lg = fitted('logo', png('logo_full'), width=360)
    if kl > 0:
        draw(c, lg, 290, 340, scale=0.88 + 0.12 * e_out_back(kl, 1.8), opacity=min(1, kl * 2))
    kinetic_line(c, 'Make your next', W / 2, 650, 82, t, VO['cta'] + 0.05, color=INK, fname=CB, shadow_op=0.0)
    kinetic_line(c, 'application count.', W / 2, 750, 82, t, VO['cta'] + 0.45, color=RED, fname=CB, shadow_op=0.0,
                 sweep_t=VO['cta'] + 1.3)
    kb = prog(t, t0 + 1.2, t0 + 1.6)
    if kb > 0:
        b = rrect_spr(480, 110, 55, NAVY)
        draw(c, b, 300, 930, scale=0.85 + 0.15 * e_out_back(kb, 2.0), opacity=min(1, kb * 3))
        draw(c, word_spr('iclondon.co.uk', IX, 38, WHITE_), 300, 932, opacity=min(1, kb * 3))
    kf = prog(t, t0 + 1.8, t0 + 2.2)
    if kf > 0:
        txt(c, 'CV tips: National Careers Service · Prospects', W / 2, 1860, 22, SLATE, IM, kf)
    return c


SCENES = [(T['hook'], T['intro'], sc_hook), (T['intro'], T['m1'], sc_intro), (T['m1'], T['m2'], sc_m1),
          (T['m2'], T['m3'], sc_m2), (T['m3'], T['cta'], sc_m3), (T['cta'], 99, sc_cta)]
TRANS = [(T['intro'], 'paper'), (T['m1'], 'paper'), (T['m2'], 'paper'), (T['m3'], 'paper'), (T['cta'], 'paper')]


def scene_at(t):
    for a, b, f in SCENES:
        if a <= t < b:
            return f
    return SCENES[-1][2]


def render_raw(t):
    c = scene_at(t)(t)
    for tc, kind in TRANS:
        d = t - tc
        if -0.12 < d < 0.18:   # paper slide: a quick directional blur + light bump
            k = 1 - abs(d) / (0.12 if d < 0 else 0.18)
            c = whip(c, k * 0.7, -1)
            c = c + 0.12 * k
    dx = dy = 0.0
    for tc in [VO['m1'] + 1.3, VO['m2'] + 2.0, M3_FIX]:
        sx, sy = shake(t, tc, amp=6, dur=0.3)
        dx += sx
        dy += sy
    if abs(dx) + abs(dy) > 0.5:
        c = cv2.warpAffine(c, np.float32([[1, 0, dx], [0, 1, dy]]), (W, H), borderMode=cv2.BORDER_REFLECT)
    if t > DUR - FADE:
        c *= 1 - 0.85 * e_inout_cubic(prog(t, DUR - FADE, DUR))
    return c


def is_fast(t):
    return t < 1.7 or any(abs(t - tc) < 0.2 for tc, _ in TRANS)


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
    return post(c, fi, bloom=0.08, grain=0.012, vig=0.35)


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
