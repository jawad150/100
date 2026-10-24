"""grp2_zentro.py: Zentro client testimonial (Google Ranker Pro), 9:16, 24 fps, 25.8 s.

    cd pipeline/fostering && FOSTER_FPS=24 python3 render.py grp2_zentro --audio <mix.wav>

Source: workspace3/frames/zentro (Seedance clip hf_20261024_074729, 25.04 s): shot 1 close-up of his hands with a
spudger on a laptop keyboard, face at the top, 0-5.33 s; shot 2 medium at the repair bench, 5.33-14.92 s; shot 3
wider, the shop and window behind, 14.92-25.04 s. End card from 22.8 s.

Real material only: Zentro's live site (captured 22 Oct 2026: the homepage hero 'Expert Laptop & Mobile Repair, You
Can Trust.' with its 'Book a Repair' button, and the homepage's 'Business IT Support' service card with 'Book IT
Enquiry') and the site's logo; Google Ranker Pro's own site promises ('No Long-Term Contracts', 'Transparent
Reporting') and CTA. No search data exists for Zentro, so nothing on screen shows a number, a ranking or a chart:
the spoken claims stay in the captions only.
"""
import functools

import numpy as np

import core as K
import footage as F
import grp_base as GB
import grp_brand as B
import grp_kit as G
import ui

DUR = 25.8
LOOK = 'natural'
BPM = 90
N_SRC = 601
T_END_CARD = 22.8

# warm neutral workshop: clean whites on the shelves, gently warm mids, neutral-cool shadows
F.GRADES['zen_shop'] = dict(wb=(1.015, 1.0, 0.975), exposure=0.02, contrast=1.08, pivot=0.42, black=0.016,
                            black_tint=(0.11, 0.10, 0.10), shadow_tint=(-0.002, 0.0, 0.006),
                            highlight_tint=(0.008, 0.003, -0.006), sat=1.02, shoulder=0.92)

CLIP = GB.Clip('zentro', N_SRC, [
    (0, 127, dict(c0=(0.5, 0.5), c1=(0.5, 0.5), z0=1.0, z1=1.04)),
    (128, 357, dict(c0=(0.5, 0.5), c1=(0.5, 0.49), z0=1.01, z1=1.05)),
    (358, 600, dict(c0=(0.5, 0.5), c1=(0.51, 0.5), z0=1.0, z1=1.04)),
], 'zen_shop')

SITE = lambda *p: G.site('zentro', *p)            # noqa: E731
LOGO = SITE('logo.png')                 # black 'ZN ZENTRO' mark on white
URL = 'zentro.co.uk'
CLIENT = 'Zentro'

# ASR is lower case without punctuation; start times checked against the audio envelope (the ASR stretches
# 'honestly', 'easy', 'more', 'if' and 'just' back into the pauses before them)
WORDS = G.load_words('zentro', fixes={0: 'How', 4: 'them?', 5: 'Honestly?', 6: 'Easy.', 7: 'No', 8: 'jargon,',
                                      11: 'contract.', 12: 'They', 18: 'fix,', 21: 'it.', 22: 'And', 36: 'us.',
                                      37: 'More', 39: 'bookings,', 43: 'enquiries.', 44: 'If', 48: 'fence,',
                                      53: 'Ranker', 54: None, 55: 'Pro.'},
                     retime={0: (3.16, 3.28), 5: (4.64, 5.06), 6: (6.20, 6.66), 7: (7.16, 7.32), 9: (7.92, 8.04),
                             10: (8.04, 8.30), 11: (8.34, 8.72), 12: (9.20, 9.32), 19: (10.88, 11.0),
                             31: (13.64, 13.74), 37: (15.80, 16.06), 38: (16.12, 16.44), 39: (16.48, 16.86),
                             40: (17.32, 17.46), 44: (19.58, 19.70), 49: (20.78, 20.92)})
CAP = B.captions(WORDS, max_chars=32, breaks=(28, 34))


# ---------------------------------------------------------------------------------------------- pieces
def _qcard_layout():
    mk = B.mark(96)
    tw = max(G.measure('How was working with', 46, B.FB), G.measure('Google Ranker Pro?', 52, B.FB))
    w = int(44 + mk.shape[1] + 30 + tw + 48)
    return mk, w, 196


def question(cv, t, t0=0.45, t1=3.3):
    """Opening question over the hands / keyboard, clear of his face (before he answers)."""
    if not (t0 <= t < t1):
        return
    mk, w, h = _qcard_layout()
    cx, cy = 540, 1240
    u, out, op = B.pop(t, t0, t1, fout=0.3, freq=2.3, damping=0.62)
    yy = cy + 34 * (1 - u) - 30 * out
    pnl, pad = B.card(w, h, 34)
    K.draw(cv, pnl, cx, yy, scale=(0.9 + 0.1 * u) * (1 - 0.05 * out), opacity=op)
    x0 = cx - w / 2 + 44
    mu = K.spring(t - (t0 + 0.12), 2.6, 0.55) if t > t0 + 0.12 else 0.0
    K.draw(cv, mk, x0 + mk.shape[1] / 2, yy, scale=0.7 + 0.3 * mu, opacity=min(1, mu * 1.5) * (1 - out))
    tx = x0 + mk.shape[1] + 30
    a1 = K.ramp(t, t0 + 0.22, t0 + 0.52, 'out_cubic') * (1 - out)
    a2 = K.ramp(t, t0 + 0.38, t0 + 0.68, 'out_cubic') * (1 - out)
    G.draw_text(cv, 'How was working with', tx, yy - 14 + 14 * (1 - a1), 46, B.FB, B.INK, 'ls', opacity=a1)
    G.draw_text(cv, 'Google Ranker Pro?', tx, yy + 50 + 14 * (1 - a2), 52, B.FB, B.ACTION, 'ls', opacity=a2)


def client_card(cv, t, t0=3.42, t1=5.15):
    """Client lockup in the same clear space over the hands: logo + name + URL."""
    if not (t0 <= t < t1):
        return
    u, out, op = B.pop(t, t0, t1, fout=0.28)
    w, h = 560, 210
    cx, cy = 540, 1240 - 24 * (1 - u) - 30 * out
    pnl, pad = B.card(w, h, 34)
    K.draw(cv, pnl, cx, cy, scale=0.88 + 0.12 * u, opacity=op)
    lg = G.image_logo(LOGO, 132)
    lu = K.spring(t - (t0 + 0.12), 2.6, 0.55) if t > t0 + 0.12 else 0.0
    K.draw(cv, lg, cx - w / 2 + 112, cy, scale=0.7 + 0.3 * lu, opacity=min(1, lu * 1.5) * (1 - out))
    tu = K.ramp(t, t0 + 0.25, t0 + 0.55, 'out_cubic') * (1 - out)
    x0 = cx - w / 2 + 214
    G.draw_text(cv, 'CLIENT STORY', x0 + 2, cy - 44, 21, B.FS, B.BODY, 'ls', opacity=tu, tracking=0.2)
    G.draw_text(cv, CLIENT, x0, cy + 14, 50, B.FB, B.INK, 'ls', opacity=tu)
    G.draw_text(cv, URL, x0 + 2, cy + 58, 27, B.FM, B.ACTION, 'ls', opacity=tu)


CHIPS = [('No jargon', 'chat', 7.12), ('No long-term contracts', 'check', 7.88)]


def chips(cv, t, t1=9.7):
    """'No jargon, no long contract': GRP's promise, in the band above his head."""
    pos = [(540 - 8, 196, 'r'), (540 + 8, 196, 'l')]
    for k, (txt, ic, t0) in enumerate(CHIPS):
        x, y, a = pos[k]
        B.draw_chip(cv, t, txt, x, y, t0, t1, icon=ic, size=32, anchor=a)


@functools.lru_cache(maxsize=1)
def _report_card():
    """'Transparent reporting' card: calendar + chart icons, the promise, the GRP logo. Icons only, no numbers."""
    w, h = 324, 316
    pnl, pad = B.card(w, h, 30, accent=B.BLUE)
    spr = pnl.copy()
    S = ui.Surf(spr.shape[1], spr.shape[0], img=spr)
    for k, ic in enumerate(('calendar', 'chart')):
        bx = pad + 38 + k * 86
        S.rrect(bx, pad + 34, 70, 70, 18, G.lin(B.SURF), 1.0)
        icn = ui.icon(ic, 40, color=B.ACTION, stroke=2.6)
        ui.paste(spr, icn, round(bx + 35 - icn.shape[1] / 2), round(pad + 69 - icn.shape[0] / 2))
    S.text(pad + 38, pad + 160, 'Transparent', 42, B.FB, B.INK)
    S.text(pad + 38, pad + 210, 'reporting', 42, B.FB, B.INK)
    lg = B.logo(46)
    ui.paste(spr, lg, round(pad + 34), round(pad + h - 36 - lg.shape[0]))
    spr.setflags(write=False)
    return G.Card(spr, pad, w, h, (0, 0, w, h))


def reporting(cv, t, t0=11.75, t1=14.72):
    """'Every month I can see where we rank and how many people found us': the promise, top left (shelves)."""
    GB.card_in(cv, _report_card(), t, t0, t1, 208, 440, rise=36, wipe_angle=0)


HERO_CROP = (90, 140, 620, 480)             # now_desktop.png: hero headline, ticks, 'Book a Repair' button
BIT_CROP = (945, 935, 395, 248)             # now_desktop_full.png: 'Business IT Support' card, 'Book IT Enquiry'


def site_repair(cv, t, t0=15.62, t1=17.32):
    """'More repair bookings': Zentro's real homepage hero with its 'Book a Repair' button, top left."""
    crd = GB.site_card(SITE('now_desktop.png'), HERO_CROP, 560, URL)
    GB.card_in(cv, crd, t, t0, t1, 322, 450, rise=40, drift=(0, -10))


def site_business(cv, t, t0=17.2, t1=19.1):
    """'More business IT enquiries': the homepage's real 'Business IT Support' card, top left."""
    crd = GB.site_card(SITE('now_desktop_full.png'), BIT_CROP, 540, URL)
    GB.card_in(cv, crd, t, t0, t1, 322, 420, rise=40, drift=(0, -10))


def grp(cv, t, t0=20.72, t1=22.62):
    """'Just talk to Google Ranker Pro': the GRP card, top left."""
    GB.card_in(cv, B.grp_card(440, 180), t, t0, t1, 292, 330, rise=36)


def cta(cv, t, t0=21.3, t1=22.62):
    """The GRP site's call to action, as an orange pill under the GRP card."""
    if not (t0 <= t < t1):
        return
    u, out, op = B.pop(t, t0, t1, fout=0.3)
    txt = 'Get your free SEO audit'
    tw = G.measure(txt, 32, B.FS)
    bw, bh = int(tw + 120), 86
    btn, pad = G.panel(bw, bh, 22, fill=B.ORANGE, fill_a=1.0, border_a=0.0, shadow=0.35, shadow_blur=16,
                       shadow_dy=8)
    x, y = 292, 520 + 22 * (1 - u) - 20 * out
    K.draw(cv, btn, x, y, scale=0.88 + 0.12 * u, opacity=op)
    G.draw_text(cv, txt, x - 20, y + 11, 32, B.FS, B.INK, 'ms', opacity=op)
    K.draw(cv, ui.icon('arrow_right', 30, color=B.INK, stroke=3.0), x + tw / 2 + 10, y, opacity=op)


# ---------------------------------------------------------------------------------------------- contract
def draw(t):
    cv = CLIP.plate(t, {0: 'band', 1: 'band'}, end_t0=T_END_CARD - 0.15)
    GB.intro_reveal(cv, t)
    if t < T_END_CARD:
        # behind him
        chips(cv, t)
        reporting(cv, t)
        site_repair(cv, t)
        site_business(cv, t)
        grp(cv, t)
        cta(cv, t)
        CLIP.person_over(cv, t, skip=[(0, 0.8)])
        # shot 1: over his hands and the keyboard (the matte includes the hands), well below his face
        question(cv, t)
        client_card(cv, t)
        G.bottom_shade(cv, 0.42, 1330, opacity=1 - K.ramp(t, T_END_CARD - 0.4, T_END_CARD, 'inout_sine'))
        CAP.draw(cv, t, opacity=1 - K.ramp(t, T_END_CARD - 0.3, T_END_CARD - 0.05, 'inout_sine'))
        B.logo_bug(cv, t, 2.6, T_END_CARD)
    B.ai_label(cv, t, solid=t >= T_END_CARD)
    B.end_card(cv, t, T_END_CARD, CLIENT, URL)
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
        dict(t=0.76, name='impact_soft', gain_db=-8),
        dict(t=3.44, name='pop', gain_db=-6, params=dict(pitch=1.05)),
        dict(t=c0, name='whip', gain_db=-6),
        dict(t=7.14, name='check_ding', gain_db=-12, pan=-0.3),
        dict(t=7.90, name='check_ding', gain_db=-13, pan=0.3, params=dict(pitch=1.06)),
        dict(t=11.77, name='card_slide', gain_db=-6, pan=-0.4),
        dict(t=12.05, name='shimmer', gain_db=-16, pan=-0.4),
        dict(t=c1, name='whip', gain_db=-6),
        dict(t=15.64, name='card_slide', gain_db=-6, pan=-0.4),
        dict(t=17.22, name='swish_small', gain_db=-7, pan=-0.4),
        dict(t=20.74, name='pop', gain_db=-6, params=dict(pitch=1.1), pan=-0.4),
        dict(t=21.32, name='ui_click', gain_db=-9, pan=-0.4),
        dict(t=T_END_CARD, name='logo_sting', gain_db=-4),
        dict(t=T_END_CARD + 0.95, name='pop', gain_db=-7, params=dict(pitch=1.2)),
    ]


def prewarm():
    B.prewarm()
    _qcard_layout()
    G.image_logo(LOGO, 132)
    GB.site_card(SITE('now_desktop.png'), HERO_CROP, 560, URL)
    GB.site_card(SITE('now_desktop_full.png'), BIT_CROP, 540, URL)
    B.grp_card(440, 180)
    _report_card()
    for txt, ic, _ in CHIPS:
        B.chip(txt, ic, 32)
