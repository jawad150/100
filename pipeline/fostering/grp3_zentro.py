"""grp3_zentro.py: Video 8 'This keyword just hit position 3' for Zentro (Google Ranker Pro social), 9:16, 24 fps.

    cd pipeline/fostering && FOSTER_FPS=24 python3 render.py grp3_zentro --audio <mix.wav>

Source: workspace3/frames/zentro2 (Seedance clip hf_20261102_121819, 30.05 s): one handheld shot of a green monitor,
a hand points along a line the generator drew on the green; voiceover only (the SEO specialist). End card from 30.0 s.

The monitor (tracked by grp_prep3.py zentro2) shows ONLY real Zentro material: the live homepage, a plain search box
with the query he names ('laptop repair near me'), the real Laptop Repair page and the real repair-brand menu
(captured 22 Oct 2026). The generated chart line and its fake axis labels are keyed out with the green.

No ranking data exists for Zentro (no Search Console export; Semrush had no API units), so nothing on screen shows a
position. 'Not even on page two', 'position three' and 'next stop, position one' stay spoken claims only and are
listed for verification in the README. Zentro's unsourced review badges ('5,000+ customers, 4.8/5', 'Trusted by
thousands') are painted out of the captures.
"""
import functools

import numpy as np

import core as K
import grp3_common as C
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

WORDS = G.load_words('zentro2', fixes={0: 'Okay,', 30: 'Watch.', 31: 'Page', 32: 'two,', 33: 'top', 34: '10.'})
CAP = B.captions(WORDS, max_chars=30, breaks=(4, 16, 24, 30, 35, 40, 43, 48, 52, 57))


# ---------------------------------------------------------------------------------------------- monitor content
def content(t):
    def at(tt):
        if tt < 7.7:
            return C.zen_page('now_desktop.png', SW, SH, 0)
        if tt < 13.0:
            k = int(np.clip((tt - 9.25) / (10.6 - 9.25), 0, 1) * len(QUERY))
            return C.search_screen(SW, SH, QUERY, k, caret=(int(tt * 2.2) % 2 == 0) or 9.2 < tt < 10.7)
        if tt < 21.0:
            sc = K.EASE['inout_sine'](K.clamp((tt - 14.0) / 6.5)) * 260
            return C.zen_page('laptop-repair_desktop_full.png', SW, SH, sc)
        if tt < 25.6:
            return C.zen_page('nav_repair_menu_laptop_desktop.png', SW, SH, 0)
        return C.zen_page('mobile-repair_desktop.png', SW, SH, 0)
    for tc in (7.7, 13.0, 21.0, 25.6):
        if tc - 0.12 <= t < tc + 0.12:
            return C.xfade(at(tc - 0.13), at(tc + 0.13), (t - (tc - 0.12)) / 0.24)
    return at(t)


@functools.lru_cache(maxsize=1)
def _quads():
    return P3.load_quads('zentro2')


def prep(fr, fi):
    q = _quads().get(fi)
    if q is None:
        return fr
    return C.despill_skin(C.key_with_hand(fr, q, content(fi / 24.0), shade=True, blur=0.8), max_excess=160, r_min=60)


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


# ---------------------------------------------------------------------------------------------- contract
def draw(t):
    cv = CLIP.plate(t, {}, end_t0=T_END_CARD - 0.15)
    GB.intro_reveal(cv, t)
    if t < T_END_CARD:
        client_card(cv, t)
        query_chip(cv, t)
        live_chip(cv, t)
        work_chips(cv, t)
        G.bottom_shade(cv, 0.42, 1330, opacity=1 - K.ramp(t, T_END_CARD - 0.4, T_END_CARD, 'inout_sine'))
        CAP.draw(cv, t, opacity=1 - K.ramp(t, T_END_CARD - 0.3, T_END_CARD - 0.05, 'inout_sine'))
        B.logo_bug(cv, t, 1.2, T_END_CARD)
    B.ai_label(cv, t, solid=t >= T_END_CARD, text='AI-generated scene · real client website')
    B.end_card(cv, t, T_END_CARD, CLIENT, URL,
               fine=['AI-generated scene and voice.', 'Client website as captured Oct 2026.',
                     'Results vary by business.'])
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
        dict(t=7.70, name='swish_small', gain_db=-9),
        dict(t=8.77, name='pop', gain_db=-7, params=dict(pitch=1.1)),
        dict(t=9.30, name='typing', gain_db=-13, params=dict(n=14, cps=11.0)),
        dict(t=12.95, name='ui_click', gain_db=-9),
        dict(t=13.32, name='swish_small', gain_db=-9),
        dict(t=21.0, name='ui_click', gain_db=-10),
        dict(t=22.62, name='check_ding', gain_db=-12, pan=-0.2),
        dict(t=24.87, name='check_ding', gain_db=-13, pan=0.2, params=dict(pitch=1.06)),
        dict(t=25.6, name='ui_click', gain_db=-11),
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
    B.chip('zentro.co.uk/laptop-repair', 'globe', 34, color=B.ACTION)
