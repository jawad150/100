"""grp2_coventry.py: Coventry Airport Taxis 247 client testimonial (Google Ranker Pro), 9:16, 24 fps, 33 s.

    cd pipeline/fostering && FOSTER_FPS=24 python3 render.py grp2_coventry --audio <mix.wav>

Source: workspace3/frames/coventry (Seedance clip hf_20261024_074103, 30.04 s): shot 1 she walks toward camera
across the taxi yard, 0-7.67 s; shot 2 the control room (she by the door, a dispatcher at the right), 7.67-16.0 s;
shot 3 a driver loads a suitcase into a boot, 16.0-23.08 s; shot 4 close-up of her by the car, 23.08-30.04 s.
End card from 30.0 s.

Real material only: Coventry Airport Taxis 247's live site (captured 22 Oct 2026: the QUOTE & BOOK form, 'We are
Available 24 Hours', 'Airport transfers', 'Meet & Greet Service', drivers who 'monitor flight statuses in
real-time', 'Professional drivers') and the site's logo; Google Search Console for coventryairporttaxis247.co.uk
('3 months' preset, about 19 Jul - 18 Oct 2026): 224 total clicks. The chart is noisy, so nothing claims growth,
and the spoken claims ('took over our SEO', 'had to add cars') stay in the captions only.
"""

import numpy as np

import core as K
import footage as F
import grp_base as GB
import grp_brand as B
import grp_kit as G

DUR = 33.0
LOOK = 'natural'
BPM = 90
N_SRC = 721
T_END_CARD = 30.0

# dusk / overcast yard: cool-neutral shadows and sky, mids (skin) a touch warm, soft highlight shoulder for the sky
F.GRADES['cov_yard'] = dict(wb=(1.012, 1.0, 0.985), exposure=0.03, contrast=1.08, pivot=0.42, black=0.016,
                            black_tint=(0.09, 0.10, 0.12), shadow_tint=(-0.006, 0.0, 0.010),
                            highlight_tint=(-0.004, 0.0, 0.006), sat=1.02, shoulder=0.90)

CLIP = GB.Clip('coventry', N_SRC, [
    (0, 183, dict(c0=(0.5, 0.5), c1=(0.5, 0.48), z0=1.0, z1=1.04)),
    (184, 383, dict(c0=(0.5, 0.5), c1=(0.49, 0.5), z0=1.01, z1=1.05)),
    (384, 553, dict(c0=(0.5, 0.5), c1=(0.5, 0.49), z0=1.0, z1=1.04)),
    (554, 720, dict(c0=(0.5, 0.48), c1=(0.5, 0.48), z0=1.02, z1=1.06)),
], 'cov_yard')

SITE = lambda *p: G.site('coventryairporttaxis247', *p)            # noqa: E731
LOGO = SITE('logo.png')                 # transparent PNG: blue mark + black wordmark (reads best on white)
URL = 'coventryairporttaxis247.co.uk'
CLIENT = 'Coventry Airport Taxis 247'

# ASR start times checked against the audio envelope: 'Morning' starts at 2.04, 'This is the control room' at 11.0
WORDS = G.load_words('coventry', fixes={8: '24/7', 9: None},
                     retime={8: (5.46, 6.34), 10: (6.58, 6.82), 58: (28.92, 29.16), 0: (2.04, 2.44), 15: (11.0, 11.12), 16: (11.16, 11.26), 17: (11.28, 11.42),
                             18: (11.44, 11.74), 19: (11.76, 12.16), 29: (18.56, 18.72), 30: (18.92, 19.22)})
CAP = B.captions(WORDS, max_chars=26, breaks=(3, 9, 22, 44, 53))


# ---------------------------------------------------------------------------------------------- pieces
def client_card(cv, t, t0=1.9, t1=5.05):
    """'Welcome to Coventry Airport Taxis': client lockup in the sky band above her head."""
    if not (t0 <= t < t1):
        return
    u, out, op = B.pop(t, t0, t1, fout=0.3)
    nm = 40
    w, h = int(232 + G.measure(CLIENT, nm, B.FB) + 50), 200
    cx, cy = 540, 340 - 24 * (1 - u) - 30 * out
    pnl, pad = B.card(w, h, 34)
    K.draw(cv, pnl, cx, cy, scale=0.88 + 0.12 * u, opacity=op)
    lg = G.image_logo(LOGO, 150)
    lu = K.spring(t - (t0 + 0.12), 2.6, 0.55) if t > t0 + 0.12 else 0.0
    K.draw(cv, lg, cx - w / 2 + 108, cy, scale=0.7 + 0.3 * lu, opacity=min(1, lu * 1.5) * (1 - out))
    tu = K.ramp(t, t0 + 0.25, t0 + 0.55, 'out_cubic') * (1 - out)
    x0 = cx - w / 2 + 214
    G.draw_text(cv, 'CLIENT STORY', x0 + 2, cy - 44, 21, B.FS, B.BODY, 'ls', opacity=tu, tracking=0.2)
    G.draw_text(cv, CLIENT, x0, cy + 10, nm, B.FB, B.INK, 'ls', opacity=tu)
    G.draw_text(cv, URL, x0 + 2, cy + 54, 27, B.FM, B.ACTION, 'ls', opacity=tu)


CHIPS1 = [('Available 24 hours', 'clock', 5.2), ('Airport transfers', 'pin', 6.3)]


def chips_24(cv, t, t1=7.45):
    """'We run 24/7 every day of the year': facts from the site's hero, in the sky band."""
    pos = [(540 - 8, 360, 'r'), (540 + 8, 360, 'l')]
    for k, (txt, ic, t0) in enumerate(CHIPS1):
        x, y, a = pos[k]
        B.draw_chip(cv, t, txt, x, y, t0, t1, icon=ic, size=32, anchor=a)


def control_chip(cv, t, t0=8.3, t1=12.62):
    """'This is the control room': a label on the free wall, top right."""
    B.draw_chip(cv, t, 'Control room', 770, 330, t0, t1, icon='pin', size=32)


BOOK_CROP = (205, 118, 465, 512)            # now_desktop.png: 'BOOK YOUR RIDE NOW', QUOTE & BOOK form, Google badge


def booking(cv, t, t0=12.55, t1=15.85):
    """'Every airport run comes through here, day or night': the site's real QUOTE & BOOK form, top right."""
    crd = GB.site_card(SITE('now_desktop.png'), BOOK_CROP, 540, URL)
    GB.card_in(cv, crd, t, t0, t1, 768, 405, rise=40, drift=(0, -10))


CHIPS3 = [('Professional drivers', 'users', 18.5, 300), ('Flight monitoring', 'globe', 20.42, 392),
          ('Meet & greet', 'user', 21.42, 484)]


def chips_drivers(cv, t, t1=22.85):
    """'These are our drivers... flight tracking, meet and greet': service facts from the site, over the boot lid."""
    for txt, ic, t0, y in CHIPS3:
        B.draw_chip(cv, t, txt, 600, y, t0, t1, icon=ic, size=30)


def grp(cv, t, t0=23.95, t1=26.45):
    """'Since Google Ranker Pro took over our SEO': the GRP card in the sky band above her head."""
    GB.card_in(cv, B.grp_card(440, 180), t, t0, t1, 540, 210, rise=36)


def _data_layout():
    num = G.measure('224', 100, B.FB)
    l1 = G.measure('clicks from Google search', 35, B.FB)
    l2 = G.measure('Last 3 months · Jul–Oct 2026', 27, B.FM)
    w = int(40 + num + 32 + max(l1, l2) + 38)
    return w, 214, num


def data_card(cv, t, t0=26.5, t1=29.82):
    """'We've had to add cars just to keep up': the real Search Console total for the site, source and period
    labelled (no trend claim: the daily chart is noisy). Right-aligned in the sky band, clear of the logo bug."""
    if not (t0 <= t < t1):
        return
    w, h, numw = _data_layout()
    cx, cy = 1036 - w / 2, 236
    u, out, op = B.pop(t, t0, t1, fout=0.32, freq=2.3, damping=0.62)
    yy = cy + 36 * (1 - u) - 30 * out
    pnl, pad = B.card(w, h, 32, accent=B.BLUE)
    wu = K.ramp(t, t0, t0 + 0.45, 'out_cubic')
    if wu < 1:
        m = np.zeros(pnl.shape[:2], np.float32)
        m[pad:pad + h, pad:pad + w] = G.wipe(w, h, wu, angle=0, soft=0.1)
        m = np.maximum(m, K.gblur(m, 18, border='constant') * 0.999)
        pnl = G.masked(pnl, m)
    K.draw(cv, pnl, cx, yy, scale=(0.92 + 0.08 * u) * (1 - 0.05 * out), opacity=op)
    x0 = cx - w / 2 + 40
    # count-up (starts once the wipe has passed it)
    cu = K.ramp(t, t0 + 0.2, t0 + 1.25, 'out_cubic')
    n = int(round(224 * cu))
    nu = K.ramp(t, t0 + 0.12, t0 + 0.32, 'inout_sine') * (1 - out)
    G.draw_text(cv, str(n), x0 + numw, yy + 38, 100, B.FB, B.ACTION, 'rs', opacity=nu)
    tx = x0 + numw + 32
    tu = K.ramp(t, t0 + 0.3, t0 + 0.6, 'out_cubic') * (1 - out)
    G.draw_text(cv, 'clicks from Google search', tx, yy - 12 + 14 * (1 - tu), 35, B.FB, B.INK, 'ls', opacity=tu)
    su = K.ramp(t, t0 + 0.45, t0 + 0.75, 'out_cubic') * (1 - out)
    G.draw_text(cv, 'Google Search Console', tx, yy + 30 + 10 * (1 - su), 27, B.FM, B.BODY, 'ls', opacity=su)
    G.draw_text(cv, 'Last 3 months · Jul–Oct 2026', tx, yy + 66 + 10 * (1 - su), 27, B.FM, B.BODY, 'ls',
                opacity=su)


# ---------------------------------------------------------------------------------------------- contract
def draw(t):
    cv = CLIP.plate(t, {0: 'band', 1: 'band', 2: 'band'}, end_t0=T_END_CARD - 0.15)
    GB.intro_reveal(cv, t)
    if t < T_END_CARD:
        # behind her
        client_card(cv, t)
        chips_24(cv, t)
        control_chip(cv, t)
        booking(cv, t)
        chips_drivers(cv, t)
        grp(cv, t)
        data_card(cv, t)
        CLIP.person_over(cv, t, skip=[(-1.0, 0.8)])
        G.bottom_shade(cv, 0.42, 1330, opacity=1 - K.ramp(t, T_END_CARD - 0.4, T_END_CARD, 'inout_sine'))
        CAP.draw(cv, t, opacity=1 - K.ramp(t, T_END_CARD - 0.3, T_END_CARD - 0.05, 'inout_sine'))
        B.logo_bug(cv, t, 2.6, T_END_CARD)
    B.ai_label(cv, t, solid=t >= T_END_CARD)
    B.end_card(cv, t, T_END_CARD, CLIENT, URL,
               extra_fine=('Search data: Google Search Console (%s),' % URL,
                           'last 3 months, Jul–Oct 2026.'))
    return np.ascontiguousarray(cv, dtype=np.float32)


post = GB.post
FAST = [(0.0, 0.8)] + [(tc - 0.2, tc + 0.2) for tc, _ in CLIP.cuts] + [(T_END_CARD - 0.2, T_END_CARD + 1.8)]


def samples(t):
    return 7 if any(a <= t < b for a, b in FAST) else 1


def cues():
    c0, c1, c2 = (tc for tc, _ in CLIP.cuts)
    return [
        dict(t=0.06, name='whoosh_fast', gain_db=-5),
        dict(t=0.76, name='impact_soft', gain_db=-8),
        dict(t=1.92, name='pop', gain_db=-6, params=dict(pitch=1.05)),
        dict(t=5.22, name='check_ding', gain_db=-12, pan=-0.3),
        dict(t=6.32, name='check_ding', gain_db=-13, pan=0.3, params=dict(pitch=1.06)),
        dict(t=c0, name='whip', gain_db=-6),
        dict(t=8.32, name='ui_click', gain_db=-9, pan=0.4),
        dict(t=12.57, name='card_slide', gain_db=-6, pan=0.4),
        dict(t=12.9, name='shimmer', gain_db=-16, pan=0.4),
        dict(t=c1, name='whip', gain_db=-6),
        dict(t=18.52, name='pop', gain_db=-7, params=dict(pitch=1.0)),
        dict(t=20.44, name='pop', gain_db=-7, params=dict(pitch=1.08)),
        dict(t=21.44, name='pop', gain_db=-7, params=dict(pitch=1.16)),
        dict(t=c2, name='whip', gain_db=-6),
        dict(t=23.97, name='swish_small', gain_db=-6),
        dict(t=26.52, name='card_slide', gain_db=-6),
        dict(t=26.75, name='glass_tap', gain_db=-12),
        dict(t=T_END_CARD, name='logo_sting', gain_db=-4),
        dict(t=T_END_CARD + 0.95, name='pop', gain_db=-7, params=dict(pitch=1.2)),
    ]


def prewarm():
    B.prewarm()
    G.image_logo(LOGO, 150)
    GB.site_card(SITE('now_desktop.png'), BOOK_CROP, 540, URL)
    B.grp_card(440, 180)
    w, h, _ = _data_layout()
    B.card(w, h, 32, accent=B.BLUE)
    for txt, ic, *_ in CHIPS1 + CHIPS3:
        B.chip(txt, ic, 32 if (txt, ic) in [c[:2] for c in CHIPS1] else 30)
