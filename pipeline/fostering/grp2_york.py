"""grp2_york.py: York Cars client testimonial (Google Ranker Pro), 9:16, 24 fps, 22 s.

    cd pipeline/fostering && FOSTER_FPS=24 python3 render.py grp2_york --audio <mix.wav>

Source: workspace3/frames/york (Seedance clip hf_20261024_063833, 20.04 s): shot 1 wide on a cobbled York street
with the Minster behind, 0-9.04 s; shot 2 medium, 9.04-20.04 s. End card from 19.0 s.

Real material only: York Cars' live site (captured 22 Oct 2026: hero 'York Taxis - Reliable 24/7 Taxi Service in
York', nav 'Airport Transfers', 'Book your ride today using our mobile app, online booking system, or phone
booking service') and the site's logo. No search data was available for York Cars, so nothing on screen shows a
ranking, a results page or a '#1' badge: the spoken claims stay in the captions only.
"""
import os

import numpy as np

import core as K
import footage as F
import grp_base as GB
import grp_brand as B
import grp_kit as G

DUR = 22.0
LOOK = 'natural'
BPM = 90
N_SRC = 481
T_END_CARD = 19.0

F.GRADES['york_street'] = dict(wb=(1.02, 1.0, 0.975), exposure=0.02, contrast=1.10, pivot=0.42, black=0.018,
                               black_tint=(0.10, 0.10, 0.12), shadow_tint=(-0.004, 0.0, 0.010),
                               highlight_tint=(0.010, 0.004, -0.008), sat=1.03, shoulder=0.92)

CLIP = GB.Clip('york', N_SRC, [
    (0, 216, dict(c0=(0.5, 0.5), c1=(0.5, 0.48), z0=1.0, z1=1.05)),
    (217, 480, dict(c0=(0.5, 0.47), c1=(0.5, 0.46), z0=1.03, z1=1.07)),
], 'york_street')

SITE = lambda *p: G.site('yorkcars', *p)            # noqa: E731
LOGO = SITE('logo.png')
URL = 'yorkcars.co.uk'

WORDS = G.load_words('york', fixes={6: '“taxi', 7: 'York”'})
CAP = B.captions(WORDS, max_chars=26, breaks=(8,))


# ---------------------------------------------------------------------------------------------- pieces
def client_card(cv, t, t0=0.35, t1=2.6):
    """Client lockup in the sky above him: logo + name + URL."""
    if not (t0 <= t < t1):
        return
    u, out, op = B.pop(t, t0, t1, fout=0.3)
    w, h = 600, 210
    cx, cy = 540, 236 - 24 * (1 - u) - 30 * out
    pnl, pad = B.card(w, h, 34)
    K.draw(cv, pnl, cx, cy, scale=0.88 + 0.12 * u, opacity=op)
    lg = G.image_logo(LOGO, 150)
    lu = K.spring(t - (t0 + 0.12), 2.6, 0.55) if t > t0 + 0.12 else 0.0
    K.draw(cv, lg, cx - w / 2 + 104, cy, scale=0.7 + 0.3 * lu, opacity=min(1, lu * 1.5) * (1 - out))
    tu = K.ramp(t, t0 + 0.25, t0 + 0.55, 'out_cubic') * (1 - out)
    G.draw_text(cv, 'CLIENT STORY', cx - w / 2 + 206, cy - 44, 21, B.FS, B.BODY, 'ls', opacity=tu, tracking=0.2)
    G.draw_text(cv, 'York Cars', cx - w / 2 + 204, cy + 14, 50, B.FB, B.INK, 'ls', opacity=tu)
    G.draw_text(cv, URL, cx - w / 2 + 206, cy + 58, 27, B.FM, B.ACTION, 'ls', opacity=tu)


def phone(cv, t, t0=6.15, t1=8.95):
    """'...and there we were': York Cars' real mobile homepage slides in on the left, clear of him."""
    if not (t0 <= t < t1):
        return
    crd = B.phone_card(SITE('now_mobile.png'), (0, 0, 780, 1330), 330)
    u = K.spring(t - t0, 2.2, 0.66)
    out = K.ramp(t, t1 - 0.3, t1, 'in_cubic')
    x = 196 - 300 * (1 - u) - 200 * out
    y = 640 - 10 * K.clamp((t - t0) / (t1 - t0))
    crd.draw(cv, x, y, rot=4 * (1 - u) - 3, opacity=min(1, (t - t0) / 0.1) * (1 - out))


def search(cv, t):
    B.search_bar(cv, t, 'taxi York', 2.7, 8.95, cx=540, cy=236, w=720, h=104, type_dur=0.75)


def grp(cv, t, t0=12.1, t1=14.95):
    """'...and Google Ranker Pro got us right to the top': the GRP card in the band above his head."""
    GB.card_in(cv, B.grp_card(440, 180), t, t0, t1, 540, 214, rise=36)


CHIPS = [('Reliable 24/7 taxis', 'clock'), ('Airport transfers', 'pin'), ('Book by app or online', 'phone')]


def chips(cv, t, t0=15.35, t1=18.75):
    """Facts from the York Cars homepage, in the band above his head."""
    if not (t0 <= t < t1):
        return
    pos = [(540 - 8, 196, 'r'), (540 + 8, 196, 'l'), (540, 280, 'm')]
    for k, (txt, ic) in enumerate(CHIPS):
        x, y, a = pos[k]
        B.draw_chip(cv, t, txt, x, y, t0 + 0.12 + 0.28 * k, t1, icon=ic, size=28, anchor=a)


# ---------------------------------------------------------------------------------------------- contract
def draw(t):
    cv = CLIP.plate(t, {0: 'band'}, end_t0=T_END_CARD - 0.15)
    GB.intro_reveal(cv, t)
    if t < T_END_CARD:
        # behind him
        client_card(cv, t)
        search(cv, t)
        phone(cv, t)
        grp(cv, t)
        chips(cv, t)
        CLIP.person_over(cv, t, skip=[(0, 0.8)])
        G.bottom_shade(cv, 0.42, 1330, opacity=1 - K.ramp(t, T_END_CARD - 0.4, T_END_CARD))
        CAP.draw(cv, t)
        B.logo_bug(cv, t, 2.6, T_END_CARD)
    B.ai_label(cv, t, solid=t >= T_END_CARD)
    B.end_card(cv, t, T_END_CARD, 'York Cars', URL)
    return np.ascontiguousarray(cv, dtype=np.float32)


post = GB.post
FAST = [(0.0, 0.8), (8.85, 9.2), (T_END_CARD - 0.2, T_END_CARD + 1.8)]


def samples(t):
    return 7 if any(a <= t < b for a, b in FAST) else 1


def cues():
    return [
        dict(t=0.06, name='whoosh_fast', gain_db=-5),
        dict(t=0.76, name='impact_soft', gain_db=-8),
        dict(t=0.42, name='pop', gain_db=-6, params=dict(pitch=1.05)),
        dict(t=2.72, name='swish_small', gain_db=-6),
        dict(t=3.05, name='typing', gain_db=-10, align='start', params=dict(n=9, cps=12)),
        dict(t=6.18, name='card_slide', gain_db=-6, pan=0.4),
        dict(t=6.50, name='shimmer', gain_db=-16, pan=0.4),
        dict(t=CLIP.cuts[0][0], name='whip', gain_db=-6),
        dict(t=12.12, name='pop', gain_db=-6, params=dict(pitch=1.1), pan=-0.4),
        dict(t=15.47, name='check_ding', gain_db=-12, pan=-0.4),
        dict(t=15.75, name='check_ding', gain_db=-13, pan=-0.4, params=dict(pitch=1.06)),
        dict(t=16.03, name='check_ding', gain_db=-13, pan=-0.4, params=dict(pitch=1.12)),
        dict(t=T_END_CARD, name='logo_sting', gain_db=-4),
        dict(t=T_END_CARD + 0.95, name='pop', gain_db=-7, params=dict(pitch=1.2)),
    ]


def prewarm():
    B.prewarm()
    G.image_logo(LOGO, 150)
    B.phone_card(SITE('now_mobile.png'), (0, 0, 780, 1330), 330)
    B.grp_card(440, 180)
