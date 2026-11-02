"""grp3_hamza.py: Video 7 'What I learned from SEO' selfie (Google Ranker Pro social), 9:16, 24 fps.

    cd pipeline/fostering && FOSTER_FPS=24 python3 render.py grp3_hamza --audio <mix.wav>

Source: workspace3/frames/hamza (Seedance clip hf_20261102_120846, 20.05 s): a phone selfie in three shots,
0-7.25 s, 7.25-13.5 s, 13.5-20.05 s. The first nine frames are a lens wobble (held on frame 9 under the intro) and
the last frame is a thumb over the lens (the end card starts before it). End card from 19.6 s.

Google Ranker Pro's own brand, no client and no figures. The presenter is AI-generated (labelled on screen); no name
or job title is added in the graphics. The three tips are his spoken lines; the phone shows googlerankerpro.com's
real mobile page (captured Oct 2026).
"""
import numpy as np

import core as K
import grp_base as GB
import grp_brand as B
import grp_kit as G
import ui

DUR = 22.6
LOOK = 'natural'
BPM = 104
N_SRC = 481
T_END_CARD = 19.6


def prep(fr, fi):
    if fi < 9:
        return G.frame_u8('hamza', 9)
    return fr


CLIP = GB.Clip('hamza', N_SRC, [
    (0, 173, dict(c0=(0.5, 0.5), c1=(0.5, 0.5), z0=1.0, z1=1.04)),
    (174, 323, dict(c0=(0.5, 0.5), c1=(0.5, 0.49), z0=1.0, z1=1.04)),
    (324, 480, dict(c0=(0.5, 0.5), c1=(0.5, 0.5), z0=1.02, z1=1.05)),
], LOOK, prep=prep)

WORDS = G.load_words('hamza', fixes={3: 'SEO’s', 28: 'site’s', 30: 'they’re', 33: 'it’s', 36: 'it’s',
                                     38: 'That’s'},
                     retime={0: (0.60, 0.92), 30: (12.64, 12.88), 32: (14.28, 14.54)})
CAP = B.captions(WORDS, max_chars=24, breaks=(6, 14, 17, 25, 32, 36, 38), y=1600, max_w=700)
# googlerankerpro.com's mobile page with its two trust badges ('UK's Trusted Search Growth Experts',
# '500+ Businesses Grow With Us') painted out: no figures or claims beyond the tips themselves
GRP_MOBILE = G.site('googlerankerpro', 'now_mobile_nobadge.png')

TIPS = [  # (number, line 1, line 2, t0, t1)
    ('1', 'Your Google profile', 'is your shop window.', 3.42, 7.2),
    ('2', 'Most people find you', 'on their phone.', 7.76, 13.3),
    ('3', 'It’s not magic.', 'It’s consistency.', 14.1, 17.05),
]
SUBS = [('Keep it updated', 'check', 6.28, 7.2), ('Slow site? They’re gone.', 'clock', 10.4, 13.3)]


def hook(cv, t, t0=0.45, t1=3.25):
    """'Okay, three things SEO's taught me': title card above his head."""
    if not (t0 <= t < t1):
        return
    u, out, op = B.pop(t, t0, t1, fout=0.28, freq=2.3, damping=0.62)
    w, h = 760, 150
    cx, cy = 540, 236 - 24 * (1 - u) - 26 * out
    pnl, pad = B.card(w, h, 34)
    K.draw(cv, pnl, cx, cy, scale=0.9 + 0.1 * u, opacity=op)
    bu = K.spring(t - (t0 + 0.1), 2.6, 0.55) if t > t0 + 0.1 else 0.0
    bx = cx - w / 2 + 92
    circ, _ = G.panel(104, 104, 52, fill=B.ACTION, fill_a=1.0, border_a=0.0, shadow=0.0)
    K.draw(cv, circ, bx, cy, scale=0.6 + 0.4 * bu, opacity=min(1, bu * 1.5) * (1 - out))
    G.draw_text(cv, '3', bx, cy + 22, 64, B.FB, '#FFFFFF', 'ms', opacity=min(1, bu * 1.5) * (1 - out))
    tu = K.ramp(t, t0 + 0.2, t0 + 0.5, 'out_cubic') * (1 - out)
    G.draw_text(cv, 'things SEO taught me', bx + 84, cy + 16, 50, B.FB, B.INK, 'ls', opacity=tu)


def tips(cv, t):
    for num, l1, l2, t0, t1 in TIPS:
        if not (t0 <= t < t1):
            continue
        u, out, op = B.pop(t, t0, t1, fout=0.25, freq=2.4, damping=0.6)
        w, h = int(96 + 90 + max(G.measure(l1, 46, B.FB), G.measure(l2, 46, B.FB)) + 70), 190
        cx, cy = 540, 250 - 24 * (1 - u) - 26 * out
        pnl, pad = B.card(w, h, 34, accent=B.BLUE)
        K.draw(cv, pnl, cx, cy, scale=0.9 + 0.1 * u, opacity=op)
        bx = cx - w / 2 + 96
        bu = K.spring(t - (t0 + 0.08), 2.6, 0.55) if t > t0 + 0.08 else 0.0
        circ, _ = G.panel(108, 108, 54, fill=B.ORANGE, fill_a=1.0, border_a=0.0, shadow=0.0)
        K.draw(cv, circ, bx, cy, scale=0.6 + 0.4 * bu, opacity=min(1, bu * 1.5) * (1 - out))
        G.draw_text(cv, num, bx, cy + 23, 66, B.FB, B.INK, 'ms', opacity=min(1, bu * 1.5) * (1 - out))
        a1 = K.ramp(t, t0 + 0.18, t0 + 0.45, 'out_cubic') * (1 - out)
        a2 = K.ramp(t, t0 + 0.30, t0 + 0.57, 'out_cubic') * (1 - out)
        x = bx + 90
        G.draw_text(cv, l1, x, cy - 10 + 12 * (1 - a1), 46, B.FB, B.INK, 'ls', opacity=a1)
        G.draw_text(cv, l2, x, cy + 52 + 12 * (1 - a2), 46, B.FB, B.ACTION, 'ls', opacity=a2)
    for txt, ic, t0, t1 in SUBS:
        B.draw_chip(cv, t, txt, 540, 412, t0, t1, icon=ic, size=36)


def phone(cv, t, t0=8.45, t1=13.3):
    """'Most people find you on their phone': googlerankerpro.com's real mobile page, right of his face."""
    crd = B.phone_card(GRP_MOBILE, (0, 0, 390, 760), 206)
    GB.card_in(cv, crd, t, t0, t1, 900, 660, rise=50, wipe_angle=0, drift=(0, -12))


def grp(cv, t, t0=17.25, t1=19.5):
    """'That's literally our job at Google Ranker Pro': the GRP card above his head."""
    GB.card_in(cv, B.grp_card(520, 190), t, t0, t1, 540, 250, rise=36)


# ---------------------------------------------------------------------------------------------- contract
def draw(t):
    cv = CLIP.plate(t, {0: 'band', 1: 'band'}, end_t0=T_END_CARD - 0.15)
    GB.intro_reveal(cv, t)
    if t < T_END_CARD:
        hook(cv, t)
        phone(cv, t)
        tips(cv, t)
        grp(cv, t)
        G.bottom_shade(cv, 0.42, 1330, opacity=1 - K.ramp(t, T_END_CARD - 0.4, T_END_CARD, 'inout_sine'))
        CAP.draw(cv, t, opacity=1 - K.ramp(t, T_END_CARD - 0.3, T_END_CARD - 0.05, 'inout_sine'))
        B.logo_bug(cv, t, 0.6, T_END_CARD)
    B.ai_label(cv, t, solid=t >= T_END_CARD, text='AI-generated presenter', y=1712)
    B.end_card(cv, t, T_END_CARD, None, None, fine=['AI-generated presenter and voice.'])
    return np.ascontiguousarray(cv, dtype=np.float32)


post = GB.post
FAST = [(0.0, 0.8)] + [(tc - 0.2, tc + 0.2) for tc, _ in CLIP.cuts] + [(T_END_CARD - 0.2, T_END_CARD + 1.8)]


def samples(t):
    return 7 if any(a <= t < b for a, b in FAST) else 1


def cues():
    c0, c1 = (tc for tc, _ in CLIP.cuts)
    return [
        dict(t=0.06, name='whoosh_fast', gain_db=-5),
        dict(t=0.47, name='card_slide', gain_db=-7),
        dict(t=0.60, name='pop', gain_db=-7),
        dict(t=3.44, name='swish_small', gain_db=-7),
        dict(t=3.52, name='pop', gain_db=-7, params=dict(pitch=1.0)),
        dict(t=6.30, name='check_ding', gain_db=-12),
        dict(t=c0, name='whip', gain_db=-6),
        dict(t=7.78, name='pop', gain_db=-7, params=dict(pitch=1.06)),
        dict(t=8.47, name='card_slide', gain_db=-7, pan=0.4),
        dict(t=10.42, name='ui_tick', gain_db=-10),
        dict(t=c1, name='whip', gain_db=-6),
        dict(t=14.12, name='pop', gain_db=-7, params=dict(pitch=1.12)),
        dict(t=17.27, name='card_slide', gain_db=-7),
        dict(t=T_END_CARD, name='logo_sting', gain_db=-4),
        dict(t=T_END_CARD + 0.95, name='pop', gain_db=-7, params=dict(pitch=1.2)),
    ]


def prewarm():
    B.prewarm()
    B.phone_card(GRP_MOBILE, (0, 0, 390, 760), 206)
    B.grp_card(520, 190)
    for txt, ic, *_ in SUBS:
        B.chip(txt, ic, 36)
