"""pehle_wala_faces_proof.py - STAND-IN world for proofing the C26 face tile (face-compositor QA only, NOT the reel).

pehle_wala.py (motion-timeline-builder) is the reel; until it exists, this module puts pehle_wala_faces.draw_tile on a
stand-in of the BRIEF section 5 layout (inferno backdrop + bokeh, the real review player window, a simplified ad with
the real Blender chai glass, pins, counter / status chips, the payoff lockup, real snake captions from the measured
VO words) and the real finish (G.tx_finish with the L3 / D9 exposure pushes on the tile's frames), so the stills
show the tile in its true light, scale and neighbourhood. Render contract of render.py (DUR, LOOK, BPM, draw, post,
samples, prewarm). Outputs: <WS>/out/pehle_wala_faces_proof -> symlink to <WS>/pehle_wala/qa/faces/render.

    tools/heavy.sh python3 render.py pehle_wala_faces_proof --stills 14.9333,16.0,17.0333 --workers 1 --no-audio
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
from jawad_kit import K, T, ui, J                 # noqa: E402
import jawad_grade as G                           # noqa: E402
import pehle_wala_faces as PF                     # noqa: E402

import cv2                                        # noqa: E402
import numpy as np                                # noqa: E402

DUR = 1024 / 30.0
LOOK = 'inferno'
BPM = 112.5
WIN = (80, 236, 920, 1032)                        # x, y, w, h
AD = (120, 468, 840, 760)
C = K.C
GLASS = os.path.join(K.WS, 'pehle_wala', 'props', 'pw_chai_glass', 'inferno_yaw', '0006.png')
WORDS = os.path.join(K.WS, 'pehle_wala', 'vo', 'pehle_wala_vo_A.words.json')
CUTS = [(14.9333, 0.6), (17.0667, 0.4), (27.7333, 0.6)]     # L3 v16, L3 v19, D9 restore (BRIEF 7)


@functools.lru_cache(maxsize=1)
def win():
    return ui.app_window(w=WIN[2], h=WIN[3], look=LOOK, title='ubaal_chai_ad.mp4', header='Review · POV',
                         sidebar=False, header_size=52)


@functools.lru_cache(maxsize=1)
def glass():
    g = K.load_image(GLASS)
    m = json.load(open(os.path.join(os.path.dirname(GLASS), 'meta.json')))
    return g, m


@functools.lru_cache(maxsize=4)
def ad_canvas(state):
    """Simplified ad (840 x 760, ad-local px). state 'v1' (pristine) or 'v16' (letterbox, flares, burst, big logo,
    parody garam): enough of the BRIEF 5.2 / 6.2 look to judge the tile's light and neighbours."""
    w, h = AD[2], AD[3]
    ad = np.zeros((h, w, 4), np.float32)
    yy = np.linspace(0, 1, h, dtype=np.float32)[:, None, None]
    ad[..., :3] = np.float32(C['NIGHT_1']) * (1 - yy) + np.float32(C['NIGHT_0']) * yy
    ad[..., 3] = 1
    K.draw(ad, K.radial(900, np.float32(C['EMBER']) * 0.9), 395, 512, mode='add')
    K.draw(ad, K.radial(420, np.float32(C['FLAME']) * 0.6), 395, 512, mode='add')
    sh = np.zeros((80, 340, 4), np.float32)
    sh[..., 3] = K.rrect_alpha(300, 40, 20, 20)[:80, :340] * 0.6
    K.draw(ad, cv2.GaussianBlur(sh, (0, 0), 8), 395, 744)
    g, m = glass()
    s = 440.0 / (m['features']['base'][1] - m['features']['rim'][1])
    K.draw(ad, g, 395, 742, scale=s, anchor=(m['anchor'][0] / g.shape[1], m['anchor'][1] / g.shape[0]))
    stm = np.zeros((h, w), np.float32)
    for i, dx in enumerate((-40, 0, 40)):
        ys = np.linspace(318, 90, 40)
        xs = 395 + dx + 24 * np.sin(np.linspace(0, 5, 40) + i)
        cv2.polylines(stm, [np.stack([xs, ys], 1).astype(np.int32)], False, 1.0, 12, cv2.LINE_AA)
    stm = cv2.GaussianBlur(stm, (0, 0), 9) * 0.28
    ad[..., :3] += stm[..., None] * np.float32(C['IVORY'])
    if state == 'v16':
        lg = 3.75
        t = T.render('UBAAL CHAI', 'jw_caps_bold', px=38 * lg)
        t.draw(ad, 34 + 66 * lg + t.w / 2, 62 * lg / 1.6)
        n, R0, R1 = 16, 70, 110
        pts = [[690 + (R1 if k % 2 == 0 else R0) * math.cos(math.pi * k / n),
                332 + (R1 if k % 2 == 0 else R0) * math.sin(math.pi * k / n)] for k in range(2 * n)]
        mk = np.zeros((h, w), np.float32)
        cv2.fillPoly(mk, [np.array(pts, np.int32)], 1.0, cv2.LINE_AA)
        ad[..., :3] = ad[..., :3] * (1 - mk[..., None]) + mk[..., None] * np.float32(C['GOLD']) * 1.1
        T.render('NEW', 'jw_caps_bold', px=60).draw(ad, 690, 332, rot=-12)
        T.render('garam', 'jw_key', px=130).draw(ad, 780 - 140, 682, rot=-4)
        bh = 64
        ad[:bh, :, :3] = 0.0
        ad[h - bh:, :, :3] = 0.0
        fl = K.streak(1400, 70, np.float32(C['FLAME']) * 2.4, np.float32(C['AMBER']) * 2.8)
        K.draw(ad, fl, 395, 790 - AD[1], mode='add')
        K.draw(ad, fl, 395, 1140 - AD[1], mode='add', opacity=0.8)
    else:
        ring = K.ring(26, 5, np.float32(C['FLAME']) * 1.6)
        K.draw(ad, ring, 60, 62)
        t = T.render('UBAAL CHAI', 'jw_caps_bold', px=38)
        t.draw(ad, 98 + t.w / 2, 62)
        gk = T.render('garam', 'jw_key', px=120)
        gk.draw(ad, 780 - gk.w / 2, 682, opacity=0.35)
    ad[..., 3] = 1
    mask = K.rrect_alpha(w, h, 18, 0)
    return PF._ro(ad * mask[..., None])


def pin(cv, mx, my, text, card_xy):
    K.draw(cv, K.disc(20, np.float32(C['NIGHT_1'])), mx, my)
    K.draw(cv, K.ring(22, 4, np.float32(C['FLAME']) * 1.8), mx, my)
    T.render('C', 'jw_caps_bold', px=26).draw(cv, mx, my)
    ts = T.render(text, 'jw_body', px=44)
    nm = T.render('Client', 'jw_mono', px=34)
    w = max(ts.w, nm.w) + 56
    hh = 118
    cx, cy = card_xy
    ui.glass_card(int(w), hh, r=24, look=LOOK, shadow=0.5).draw(cv, cx, cy)
    nm.draw(cv, cx - w / 2 + 28 + nm.w / 2, cy - hh / 2 + 22 + nm.h / 2, opacity=0.8)
    ts.draw(cv, cx - w / 2 + 28 + ts.w / 2, cy + hh / 2 - 26 - ts.h / 2)


def status(cv, txt):
    if txt == 'Approved':
        sz = ui.chip_size(txt, 34, h=64, icon_name='check', pad_x=26)
        spr = ui.chip(txt, sel=1.0, look=LOOK, size=34, h=64, icon_name='check', pad_x=26, grad=('EMBER', 'PLUM'))
    else:
        sz = ui.chip_size(txt, 34, h=64, pad_x=26)
        spr = ui.chip(txt, sel=0.0, look=LOOK, size=34, h=64, pad_x=26)
    ui.place(cv, spr, 960 - sz[0] / 2, 404)


def counter(cv, v):
    ui.glass_card(140, 60, r=18, look=LOOK, shadow=0.4).draw(cv, 908, 280)
    T.render('v%d' % v, 'jw_mono', px=56).draw(cv, 908, 280)


@functools.lru_cache(maxsize=1)
def captions():
    import snake_captions as SC
    words = json.load(open(WORDS))
    words = [w for w in words if 14.5 < w['start'] < 17.5 or 27.5 < w['start'] < 31.5]
    return SC.Captions(words, band='lower', y=1400,
                       avoid=lambda t: [(WIN[0], WIN[1], WIN[0] + WIN[2], WIN[1] + WIN[3])] +
                       ([PF.avoid_rect(t)] if PF.avoid_rect(t) else []))


def lockup(cv):
    """Payoff lockup, settled (BRIEF 6.1 PO1 / PO2): key centre (540, 670), caps (540, 891)."""
    m = np.zeros((K.H, K.W), np.float32)
    cv2.ellipse(m, (540, 740), (500, 230), 0, 0, 360, 1.0, -1)
    m = cv2.GaussianBlur(m, (0, 0), 60)
    cv[..., :3] *= (1 - 0.55 * m)[..., None]
    k = T.render('pehle wala', 'jw_key', px=210)
    k.draw(cv, 540, 670)
    ul = J.underline(918)
    ul.draw(cv, 540 - 459, 821, 1.0)
    T.render('HI THEEK THA', 'jw_caps', px=86).draw(cv, 540, 891)


def draw(t):
    cv = K.background(LOOK, t, bokeh=1.0)
    win().draw(cv, WIN[0], WIN[1], anchor=(0, 0))
    v16 = t < 20.0
    ad = ad_canvas('v16' if v16 else 'v1')
    reg = cv[AD[1]:AD[1] + AD[3], AD[0]:AD[0] + AD[2]]
    reg[...] = ad + reg * (1 - ad[..., 3:4])
    if v16:
        v = 16 if t < 16.0 else (17 if t < 16.5333 else 18)
        counter(cv, v)
        status(cv, 'Changes requested')
        if t < 16.0:
            pin(cv, 515, 790 - 34, 'Thora cinematic', (640, 640))
        elif t < 16.5333:
            pin(cv, 840, 720 - 34, 'Price bhi daal do', (640, 560))
        else:
            pin(cv, 515, 690 - 34, 'Bhaap aur zyada', (680, 900))
    else:
        counter(cv, 1)
        status(cv, 'Approved')
        if t < 29.8667:
            lockup(cv)
    PF.draw_tile(cv, t, mode=os.environ.get('PWF_MODE', 'full'))
    if not os.environ.get('PW_CAPTIONS') == '0':
        captions().draw(cv, t)
    return cv


def post(cv, t):
    return G.tx_finish(cv, t, LOOK, cuts=CUTS)


def samples(t):
    return 3


def prewarm():
    PF.prewarm()
    win()
    ad_canvas('v1')
    ad_canvas('v16')
