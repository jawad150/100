"""grp3_zentro.py: Video 8 'This keyword just hit position 3' for Zentro (Google Ranker Pro social), 9:16, 24 fps.

    cd pipeline/fostering && FOSTER_FPS=24 python3 render.py grp3_zentro --audio <mix.wav>

Source: workspace3/frames/zentro2 (Seedance clip hf_20261102_121819, 30.05 s): one handheld shot of a green monitor;
a hand traces a rising line the generator drew on the green; voiceover only. End card from 30.0 s.

The monitor (tracked by grp_prep3.py zentro2) shows the Google ranking chart he describes for 'laptop repair near
me' (grp3_rankchart.py): not in the top 20 three months ago, page two, top 10, position 3 this morning, the three
fixes he lists, and 'next stop: #1'. Its line uses the generated line's exact vertices, so his finger stays on it,
and it draws on behind his fingertip. No real ranking data exists for Zentro, so the chart is an ILLUSTRATION and is
labelled as one on the monitor, in the AI label and in the end-card fine print.
"""
import functools

import numpy as np

import core as K
import grp3_common as C
import grp3_rankchart as R
import grp_base as GB
import grp_brand as B
import grp_kit as G
import grp_prep3 as P3
import ui

DUR = 33.0
LOOK = 'natural'
BPM = 108
N_SRC = 721
T_END_CARD = 30.0
SW, SH = 1600, 970                          # monitor content canvas (screen ratio about 1.65)

CLIP = GB.Clip('zentro2', N_SRC, [
    (0, 720, dict(c0=(0.5, 0.5), c1=(0.5, 0.5), z0=1.0, z1=1.03)),
], LOOK, prep=None)

SITE = lambda *p: G.site('zentro', *p)            # noqa: E731
LOGO = SITE('logo.png')
URL = 'zentro.co.uk'
CLIENT = 'Zentro'
QUERY = 'laptop repair near me'

WORDS = G.load_words('zentro2', fixes={0: 'Okay,', 25: 'weren’t', 30: 'Watch.', 31: 'Page', 32: 'two,', 33: 'top',
                                       34: '10.', 40: 'That’s'},
                     retime={0: (1.72, 1.96), 31: (14.45, 14.72), 38: (18.08, 18.46), 57: (27.84, 28.10)})
CAP = B.captions(WORDS, max_chars=24, breaks=(4, 11, 16, 24, 27, 30, 35, 40, 43, 48, 52, 57), y=1600, max_w=700)


# ---------------------------------------------------------------------------------------------- monitor content
def content(t):
    """The monitor: the ranking chart he describes (an illustration), drawn on behind his fingertip."""
    return R.chart(t)


@functools.lru_cache(maxsize=1)
def _quads():
    return P3.load_quads('zentro2')


def _wide(q, s=1.07):
    """Widen the quad sideways only (a taller quad would reach the bezel and key the green-lit thumb)."""
    c = np.mean(np.array(q), 0)
    return [[c[0] + (p[0] - c[0]) * s, p[1]] for p in q]


_PAGE_WHITE = np.full((90, 160, 3), 247.0, np.float32)


def prep(fr, fi):
    q = _quads().get(fi)
    if q is None:
        return fr
    fr = C.key_with_hand(fr, q, content(fi / 24.0), shade=True, blur=0.8)
    # where the hand hid a screen edge from the tracker, any green left just past the edge becomes page white
    fr = C.ring_to_white(fr, q, _wide(q))
    fr = C.kill_bright_green(fr, q, g_min=120, excess=45)   # lime spill on the forearm where it crosses the bezel
    fr = C.kill_smooth_green(fr, q, excess=4, max_std=13.0)   # smooth (skin) spill outside the screen; plants stay
    return C.despill_skin(fr, max_excess=160, r_min=60)


CLIP.prep = prep


# ---------------------------------------------------------------------------------------------- overlays
def client_card(cv, t, t0=2.95, t1=7.4):
    """'This is Zentro, a laptop and phone repair shop': client lockup above the monitor."""
    if not (t0 <= t < t1):
        return
    u, out, op = B.pop(t, t0, t1, fout=0.28)
    w, h = 720, 210
    cx, cy = 540, 330 - 24 * (1 - u) - 30 * out
    pnl, pad = B.card(w, h, 34)
    K.draw(cv, pnl, cx, cy, scale=0.88 + 0.12 * u, opacity=op)
    lg = G.image_logo(LOGO, 132)
    lu = K.spring(t - (t0 + 0.12), 2.6, 0.55) if t > t0 + 0.12 else 0.0
    K.draw(cv, lg, cx - w / 2 + 112, cy, scale=0.7 + 0.3 * lu, opacity=min(1, lu * 1.5) * (1 - out))
    tu = K.ramp(t, t0 + 0.25, t0 + 0.55, 'out_cubic') * (1 - out)
    x0 = cx - w / 2 + 214
    G.draw_text(cv, 'CLIENT', x0 + 2, cy - 44, 21, B.FS, B.BODY, 'ls', opacity=tu, tracking=0.2)
    G.draw_text(cv, 'Laptop & mobile repair', x0, cy + 10, 40, B.FB, B.INK, 'ls', opacity=tu)
    G.draw_text(cv, URL, x0 + 2, cy + 56, 27, B.FM, B.ACTION, 'ls', opacity=tu)


def query_chip(cv, t, t0=8.75, t1=12.6):
    """'For laptop repair near me': the search term he names, above the monitor."""
    B.draw_chip(cv, t, QUERY, 540, 330, t0, t1, icon='search', size=40)


def live_chip(cv, t, t0=13.3, t1=20.6):
    """The page on screen is Zentro's real Laptop Repair page."""
    B.draw_chip(cv, t, 'zentro.co.uk/laptop-repair', 540, 330, t0, t1, icon='globe', size=34, color=B.ACTION)


CHIPS = [('Service pages fixed', 'check', 22.6, 0), ('Google profile sorted', 'pin', 24.85, 1)]


def work_chips(cv, t, t1=27.7):
    """'We fixed their service pages, sorted the Google profile': the work, stacked above the monitor."""
    for txt, ic, t0, k in CHIPS:
        B.draw_chip(cv, t, txt, 540, 268 + 104 * k, t0, t1, icon=ic, size=36)


BEATS = [  # (text, icon, t0, t1, y): what he says, readable above the monitor
    ('Page 2', 'chart', 13.45, 15.68, 330),
    ('Top 10', 'chart', 15.7, 18.02, 330),
    ('Position 3 · this morning', 'star', 18.05, 21.9, 330),
    ('Service pages fixed', 'check', 22.6, 27.5, 230),
    ('Google profile sorted', 'pin', 24.85, 27.5, 330),
    ('Real reviews coming in', 'star', 26.3, 27.5, 430),
    ('Next stop: #1', 'arrow_right', 27.6, 29.9, 330),
]


def beats(cv, t):
    for txt, ic, t0, t1, y in BEATS:
        B.draw_chip(cv, t, txt, 540, y, t0, t1, icon=ic, size=44)


# ---------------------------------------------------------------------------------------------- contract
def draw(t):
    cv = CLIP.plate(t, {}, end_t0=T_END_CARD - 0.15)
    GB.intro_reveal(cv, t)
    if t < T_END_CARD:
        client_card(cv, t)
        query_chip(cv, t)
        beats(cv, t)
        G.bottom_shade(cv, 0.42, 1330, opacity=1 - K.ramp(t, T_END_CARD - 0.4, T_END_CARD, 'inout_sine'))
        CAP.draw(cv, t, opacity=1 - K.ramp(t, T_END_CARD - 0.3, T_END_CARD - 0.05, 'inout_sine'))
        B.logo_bug(cv, t, 1.2, T_END_CARD)
    B.ai_label(cv, t, solid=t >= T_END_CARD, text='AI-generated scene · ranking chart is an illustration', y=1712)
    B.end_card(cv, t, T_END_CARD, CLIENT, URL,
               fine=['AI-generated scene and voice.', 'The ranking chart illustrates the story told;',
                     'it is not Zentro’s live ranking data. Results vary by business.'])
    return np.ascontiguousarray(cv, dtype=np.float32)


post = GB.post
FAST = [(0.0, 0.8), (T_END_CARD - 0.2, T_END_CARD + 1.8)]


def samples(t):
    return 7 if any(a <= t < b for a, b in FAST) else 1


def cues():
    return [
        dict(t=0.06, name='whoosh_fast', gain_db=-5),
        dict(t=2.97, name='card_slide', gain_db=-7),
        dict(t=3.30, name='pop', gain_db=-8, params=dict(pitch=1.05)),
        dict(t=8.77, name='pop', gain_db=-7, params=dict(pitch=1.1)),
        dict(t=13.47, name='ui_tick', gain_db=-9),
        dict(t=15.72, name='ui_tick', gain_db=-9, params=dict(pitch=1.08)),
        dict(t=18.07, name='check_ding', gain_db=-9),
        dict(t=18.10, name='shimmer', gain_db=-15),
        dict(t=22.62, name='check_ding', gain_db=-12, pan=-0.2),
        dict(t=24.87, name='check_ding', gain_db=-13, pan=0.2, params=dict(pitch=1.06)),
        dict(t=26.32, name='check_ding', gain_db=-13, params=dict(pitch=1.12)),
        dict(t=27.62, name='swish_small', gain_db=-8),
        dict(t=T_END_CARD, name='logo_sting', gain_db=-4),
        dict(t=T_END_CARD + 0.95, name='pop', gain_db=-7, params=dict(pitch=1.2)),
    ]


def prewarm():
    B.prewarm()
    _quads()
    G.image_logo(LOGO, 132)
    for txt, ic, _, _ in CHIPS:
        B.chip(txt, ic, 36)
    B.chip(QUERY, 'search', 40)
    for txt, ic, *_ in BEATS:
        B.chip(txt, ic, 44)
