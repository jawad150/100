"""grp3_grace.py: Video 10 'Meet the team' (Google Ranker Pro service pages), 9:16, 24 fps.

    cd pipeline/fostering && FOSTER_FPS=24 python3 render.py grp3_grace --audio <mix.wav>

Source: workspace3/frames/grace (Seedance clip hf_20261102_130620, 30.04 s): shot 1 to camera, 0-8.0 s; shot 2 wide at
the desk with a green laptop, 8.0-17.88 s; shot 3 close-up to camera, 17.88-30.04 s. End card from 28.8 s.

Google Ranker Pro's own brand, no client. The presenter is AI-generated (labelled on screen and in the fine print);
no name or job title is added in the graphics (only her own spoken line carries them).
The laptop (grp_prep3.py grace) shows a Google Ranker Pro monthly-review page built from the site's own copy
(googlerankerpro.com/seo-services: 'A useful report answers better questions. 01 Are the right people finding you?
02 What happens after the click? 03 What should change next?'), so no client data appears. The chips use other
lines from the site: 'Straight-talking. No jargon.', 'Clear progress updates', 'Know the monthly investment.'
"""
import functools

import numpy as np

import core as K
import grp3_common as C
import grp_base as GB
import grp_brand as B
import grp_kit as G
import grp_prep3 as P3

DUR = 31.8
LOOK = 'natural'
BPM = 96
N_SRC = 721
T_END_CARD = 28.8
SW, SH = 1600, 1000

WORDS = G.load_words('grace', fixes={0: 'Hi,', 1: 'I’m', 10: 'I’m', 43: 'disappearing', 44: None, 45: 'act.',
                                     49: 'working,', 50: 'I’ll', 54: 'we’ll', 57: 'You’ll', 61: 'you’re',
                                     37: 'we’re'})
CAP = B.captions(WORDS, max_chars=28, breaks=(10, 17, 25, 30, 35, 40, 42, 46, 53, 57))


@functools.lru_cache(maxsize=1)
def _quads():
    q = P3.load_quads('grace')
    # the generated call-control pills sit at the bottom of the green: push the bottom edge down to cover them
    out = {}
    for f, v in q.items():
        tl, tr, br, bl = [np.array(p, np.float64) for p in v]
        out[f] = [tl.tolist(), tr.tolist(), (tr + (br - tr) * 1.15).tolist(), (tl + (bl - tl) * 1.15).tolist()]
    return out


@functools.lru_cache(maxsize=1)
def _quads_wide():
    """A slightly larger quad for the clean-up key (any green the paste missed turns page-white)."""
    out = {}
    for f, v in _quads().items():
        c = np.mean(np.array(v), 0)
        out[f] = [(c + (np.array(p) - c) * 1.06).tolist() for p in v]
    return out


_WHITE = np.full((100, 160, 3), 246.0, np.float32)


def screen(t):
    if t < 9.7:
        return C.report_questions(SW, SH, 0, -1)
    if t < 13.3:
        return C.report_questions(SW, SH, 3, -1)
    if t < 16.4:
        return C.report_questions(SW, SH, 3, 0)
    return C.report_questions(SW, SH, 3, 2)


def prep(fr, fi):
    if 192 <= fi <= 428:
        q = _quads().get(fi)
        if q is not None:
            fr = GB.paste_quad(fr, q, screen(fi / 24.0), feather=1.2, gain=0.97, blur=0.7)
            fr = GB.green_replace(fr, _quads_wide()[fi], _WHITE, shade=False, black=10.0, white=236.0)
    return fr


CLIP = GB.Clip('grace', N_SRC, [
    (0, 191, dict(c0=(0.5, 0.5), c1=(0.5, 0.48), z0=1.0, z1=1.05)),
    (192, 428, dict(c0=(0.45, 0.6), c1=(0.42, 0.6), z0=1.08, z1=1.12)),
    (429, 720, dict(c0=(0.5, 0.45), c1=(0.5, 0.45), z0=1.0, z1=1.04)),
], LOOK, prep=prep)


# ---------------------------------------------------------------------------------------------- overlays
def grp(cv, t, t0=3.9, t1=7.7):
    """'... at Google Ranker Pro': the GRP card on her jumper, above the captions (where the shot 3 chips sit)."""
    GB.card_in(cv, B.grp_card(440, 170), t, t0, t1, 540, 1420, rise=36)


CHIPS2 = [('Where you rank', 'chart', 13.32, 0), ('How many people found you', 'users', 14.4, 1),
          ('What we’re doing next', 'arrow_right', 16.42, 2)]


def report_chips(cv, t, t1=17.75):
    """'Where they rank, how many people found them and what we're doing next', over the brick wall."""
    for txt, ic, t0, k in CHIPS2:
        B.draw_chip(cv, t, txt, 540, 250 + 100 * k, t0, t1, icon=ic, size=36)


CHIPS3 = [('Straight-talking. No jargon.', 'chat', 18.8, 21.7), ('Clear progress updates', 'check', 21.95, 26.3),
          ('Know the monthly investment', 'pound', 26.5, 28.55)]


def promise_chips(cv, t):
    """Shot 3: one site promise at a time, on her jumper under her chin, above the captions."""
    for txt, ic, t0, t1 in CHIPS3:
        B.draw_chip(cv, t, txt, 540, 1450, t0, t1, icon=ic, size=40)


# ---------------------------------------------------------------------------------------------- contract
def draw(t):
    cv = CLIP.plate(t, {0: 'band', 1: 'band'}, end_t0=T_END_CARD - 0.15)
    GB.intro_reveal(cv, t)
    if t < T_END_CARD:
        grp(cv, t)
        report_chips(cv, t)
        promise_chips(cv, t)
        G.bottom_shade(cv, 0.42, 1330, opacity=1 - K.ramp(t, T_END_CARD - 0.4, T_END_CARD, 'inout_sine'))
        CAP.draw(cv, t, opacity=1 - K.ramp(t, T_END_CARD - 0.3, T_END_CARD - 0.05, 'inout_sine'))
        B.logo_bug(cv, t, 0.6, T_END_CARD)
    B.ai_label(cv, t, solid=t >= T_END_CARD, text='AI-generated presenter')
    B.end_card(cv, t, T_END_CARD, None, None,
               fine=['AI-generated presenter and voice.', 'Report screen: Google Ranker Pro’s own site copy.'])
    return np.ascontiguousarray(cv, dtype=np.float32)


post = GB.post
FAST = [(0.0, 0.8)] + [(tc - 0.2, tc + 0.2) for tc, _ in CLIP.cuts] + [(T_END_CARD - 0.2, T_END_CARD + 1.8)]


def samples(t):
    return 7 if any(a <= t < b for a, b in FAST) else 1


def cues():
    c0, c1 = (tc for tc, _ in CLIP.cuts)
    return [
        dict(t=0.06, name='whoosh_fast', gain_db=-5),
        dict(t=3.92, name='card_slide', gain_db=-7, pan=0.4),
        dict(t=c0, name='whip', gain_db=-6),
        dict(t=9.7, name='ui_click', gain_db=-11, pan=-0.3),
        dict(t=13.34, name='pop', gain_db=-8),
        dict(t=14.42, name='pop', gain_db=-8, params=dict(pitch=1.06)),
        dict(t=16.44, name='pop', gain_db=-8, params=dict(pitch=1.12)),
        dict(t=c1, name='whip', gain_db=-6),
        dict(t=18.82, name='check_ding', gain_db=-12),
        dict(t=21.97, name='check_ding', gain_db=-12, params=dict(pitch=1.06)),
        dict(t=26.52, name='check_ding', gain_db=-12, params=dict(pitch=1.12)),
        dict(t=T_END_CARD, name='logo_sting', gain_db=-4),
        dict(t=T_END_CARD + 0.95, name='pop', gain_db=-7, params=dict(pitch=1.2)),
    ]


def prewarm():
    B.prewarm()
    _quads()
    B.grp_card(440, 170)
    for txt, ic, *_ in CHIPS2:
        B.chip(txt, ic, 36)
    for txt, ic, *_ in CHIPS3:
        B.chip(txt, ic, 40)
