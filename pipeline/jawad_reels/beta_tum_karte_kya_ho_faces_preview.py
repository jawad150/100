"""beta_tum_karte_kya_ho_faces_preview.py - render.py harness for the C02 face shots (face-compositor QA only).

NOT the reel: the world here is the gold_hour plate (+ bokeh 0.6, + the S10 sun) moved by FF.world_cam, JD from
beta_tum_karte_kya_ho_faces, J.embers in front, and labelled STAND-INS of the brief's bubbles / lockups (lifted from
brief_proof/layout_proof.py geometry) so composition and spacing can be judged. Outside the face shots it draws the
plain plate. The finish is the reel's: G.tx_finish(..., cuts=GLUE, rays=0.0).

    cd pipeline/jawad_reels
    tools/heavy.sh python3 render.py beta_tum_karte_kya_ho_faces_preview --stills 0,1.0,2.767 --workers 1 --jpg
    (outputs: <WS>/out/beta_tum_karte_kya_ho_faces_preview -> workspace/jawad_reels/beta_tum_karte_kya_ho/out/faces_preview)
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
import jawad_grade as G                           # noqa: E402
import beta_tum_karte_kya_ho_faces as FF          # noqa: E402

DUR = 36.4
LOOK = 'gold_hour'
BPM = 600 / 7
UI = os.environ.get('BTK_FACES_UI', '1') != '0'   # BTK_FACES_UI=0 -> JD + world only
GLUE = [(2.8, 0.5), (7.7, 0.7), (8.4, 0.4), (14.0, 0.6), (16.8, 0.4), (28.7, 0.7), (32.2, 0.3), (35.7, 0.3)]

BUBBLE_A = (147, 280, 933, 740)
PILL = (147, 280, 467, 420)
PAYOFF = (147, 280, 933, 790)
KILLER_UP = (150, 280, 930, 520)


@functools.lru_cache(maxsize=None)
def _card(w, h, r=44):
    return ui.glass_card(int(w), int(h), r=r, look=LOOK)


def _rect(cv, R, r=44, opacity=1.0):
    x0, y0, x1, y1 = R
    _card(x1 - x0, y1 - y0, r).draw(cv, (x0 + x1) / 2, (y0 + y1) / 2, opacity=opacity)


def _txt(cv, s, style, px, x, y, anchor=(0, 0.5), opacity=1.0, **kw):
    T.render(s, style, px=px, **kw).draw(cv, x, y, anchor=anchor, opacity=opacity)


@functools.lru_cache(maxsize=None)
def _house(caps, key, underline):
    return J.HouseTitle(caps, key, caps_px=86, key_px=210, underline=underline)


def _lockup3(cv, caps, key, third, yk, underline=False):
    h = _house(caps, key, underline)
    h.draw(cv, 30.0, 540, yk, t0=0.0)
    dy = (h.kh / 2 + h.key_px * 0.36 + 62) if underline else (h.kh / 2 + h.gap + 30.14)
    T.render(third, 'jw_caps', px=86).draw(cv, 540, yk + dy)


def _dots(cv, tau):
    for i in range(3):
        s = 0.85 + 0.15 * math.cos(2 * math.pi * (tau - 0.1 * i) / 0.6)
        K.draw(cv, K.glow(K.disc(14, K.C['AMBER'] * 2.0), K.C['FLAME'], sigmas=(4, 10), strength=0.8),
               263 + 44 * i, 350, scale=s, mode='add')


@functools.lru_cache(maxsize=2)
def _embers():
    return J.embers(60, seed=21, bright=0.4)


@functools.lru_cache(maxsize=1)
def _sun():
    return K.glow(K.disc(110, K.C['AMBER'] * 1.3), K.C['FLAME'], sigmas=(12, 36, 90), strength=0.9)


def draw(t):
    key = FF.shot_at(t)
    wc = FF.world_cam(t, key) if key else None
    g = FF.window_gain(t)
    cv = K.background(LOOK, t, wc, bokeh=0.6, intensity=g)
    if key is None:
        return cv
    if key == 'S10':
        u = K.ramp(t, 30.8, 31.3, 'out_cubic')
        K.draw(cv, _sun(), 540, 1260, mode='add', opacity=1.0 + 0.3 * u)
    FF.draw_face(cv, key, t)
    if wc is not None:
        sc = K.Scene(wc)
        sc.particles(_embers(), t)
        sc.render(cv)
    if UI:
        if key in ('S0', 'S12'):
            tau = t if key == 'S0' else t - 36.4
            _txt(cv, 'Mummy' if key == 'S0' else 'Nani', 'jw_body', 36, 160, 252, fill='AMBER')
            _txt(cv, 'POV · har desi ghar', 'jw_mono', 34, 1000, 252, anchor=(1, 0.5), opacity=0.85)
            if tau < 0.3:
                _rect(cv, PILL, r=40)
                _dots(cv, tau)
            else:
                _rect(cv, BUBBLE_A)
                _lockup3(cv, 'BETA, TUM', 'karte kya', 'HO?', 518.7)
        elif key == 'S6' and t < 15.0:
            _txt(cv, 'Mummy', 'jw_body', 36, 160, 252, fill='AMBER')
            _rect(cv, KILLER_UP)
            _txt(cv, 'Achha.', 'jw_body', 60, 190, 352)
            _txt(cv, 'Naukri kab lagegi?', 'jw_body', 60, 190, 442)
        elif key == 'S10' and t < 31.83:
            _txt(cv, 'Mummy', 'jw_body', 36, 160, 252, fill='AMBER')
            _rect(cv, PAYOFF)
            _lockup3(cv, 'MERA BETA', 'cinema', 'BANATA HAI', 518.7, underline=True)
    return cv


def post(cv, t):
    return G.tx_finish(cv, t, LOOK, cuts=[(0.0, 0.6)] + GLUE, rays=0.0)


def samples(t):
    return 3


def prewarm():
    FF.prewarm()
