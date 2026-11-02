"""grp3_coventry.py: Video 9 reaction clip for Coventry Airport Taxis 247 (Google Ranker Pro social), 9:16, 24 fps.

    cd pipeline/fostering && FOSTER_FPS=24 python3 render.py grp3_coventry --audio <mix.wav>

Source: workspace3/frames/coventry2 (Seedance clip hf_20261102_123403, 15.05 s): shot 1 over her shoulder at a green
laptop, 0-4.54 s; shot 2 close-up reaction, 4.54-10.58 s; shot 3 wide at the desk, 10.58-15.05 s. End card 15.0 s.

The laptop (tracked by grp_prep3.py coventry2) shows the client's REAL Google Search Console capture for
coventryairporttaxis247.co.uk ('3 months' preset, about 19 Jul - 18 Oct 2026): 224 clicks, 15.9K impressions,
1.4% CTR, average position 18.4, the daily chart and the top three queries, under a Google Ranker Pro report header.

'Calls from Google doubled' is a spoken claim with NO data behind it (no call figures exist for this client, and the
Search Console period has no comparison). It stays in the captions only and must be verified, swapped for a real
figure in a regenerated line, or signed off by the client before publishing (README). The on-screen card shows only
the real Search Console totals.
"""
import functools

import numpy as np

import core as K
import grp3_common as C
import grp_base as GB
import grp_brand as B
import grp_kit as G
import grp_prep3 as P3

DUR = 18.0
LOOK = 'natural'
BPM = 100
N_SRC = 361
T_END_CARD = 15.0
SW, SH = 1600, 1063                          # laptop content canvas (screen ratio about 1.5)

SITE = lambda *p: G.site('coventryairporttaxis247', *p)            # noqa: E731
LOGO = SITE('logo.png')
URL = 'coventryairporttaxis247.co.uk'
CLIENT = 'Coventry Airport Taxis 247'
GSC = '/home/user/100/google_ranker_pro_videos/assets/gsc/'
REPORT = (GSC + 'coventryairporttaxis247_gsc_3m_chart.png',
          ((0, 121, 718, 110), (20, 265, 1260, 210), (GSC + 'coventryairporttaxis247_gsc_3m_full.png', 24, 847,
                                                       1318, 204)))

WORDS = G.load_words('coventry2', fixes={0: 'Oh,', 1: 'monthly', 2: 'report’s', 3: 'in,', 9: 'doubled!',
                                         10: 'Doubled!', 12: 'I’m'},
                     retime={6: (6.95, 7.24), 9: (8.55, 9.00)})
CAP = B.captions(WORDS, max_chars=24, breaks=(6, 10, 11, 15), y=1600, max_w=700)


@functools.lru_cache(maxsize=1)
def _quads():
    return P3.load_quads('coventry2')


def _report():
    return C.report_gsc(SW, SH, URL, REPORT[0], REPORT[1], 'Monthly report')


def prep(fr, fi):
    if fi <= 108:
        q = _quads().get(fi)
        if q is not None:
            fr = GB.green_replace(fr, q, _report(), k_lo=10.0, k_hi=45.0, black=10.0, white=236.0, shade=True)
        # her hair, the keyboard deck and the keys were lit / painted green by the generator; the screen is now a
        # white report: neutralise every strong green outside the screen in this shot (nothing else here is green)
        fr = C.despill_skin(fr, max_excess=150, r_min=30)
        return C.neutral_outside(fr, q) if q is not None else fr
    # glasses / face reflections of the old green screen (her green jumper is below these rows and keeps its colour)
    return C.neutralise_green(fr, 960 if fi <= 253 else 760)


CLIP = GB.Clip('coventry2', N_SRC, [
    (0, 108, dict(c0=(0.5, 0.5), c1=(0.52, 0.5), z0=1.0, z1=1.05)),
    (109, 253, dict(c0=(0.5, 0.45), c1=(0.5, 0.45), z0=1.0, z1=1.04)),
    (254, 360, dict(c0=(0.5, 0.5), c1=(0.5, 0.5), z0=1.02, z1=1.06)),
], LOOK, prep=prep)


# ---------------------------------------------------------------------------------------------- overlays
def client_card(cv, t, t0=0.9, t1=4.35):
    """Client lockup above the laptop (dark office wall)."""
    if not (t0 <= t < t1):
        return
    u, out, op = B.pop(t, t0, t1, fout=0.3)
    nm = 40
    w, h = int(232 + G.measure(CLIENT, nm, B.FB) + 50), 200
    cx, cy = 540, 330 - 24 * (1 - u) - 30 * out
    pnl, pad = B.card(w, h, 34)
    K.draw(cv, pnl, cx, cy, scale=0.88 + 0.12 * u, opacity=op)
    lg = G.image_logo(LOGO, 150)
    lu = K.spring(t - (t0 + 0.12), 2.6, 0.55) if t > t0 + 0.12 else 0.0
    K.draw(cv, lg, cx - w / 2 + 108, cy, scale=0.7 + 0.3 * lu, opacity=min(1, lu * 1.5) * (1 - out))
    tu = K.ramp(t, t0 + 0.25, t0 + 0.55, 'out_cubic') * (1 - out)
    x0 = cx - w / 2 + 214
    G.draw_text(cv, 'CLIENT', x0 + 2, cy - 44, 21, B.FS, B.BODY, 'ls', opacity=tu, tracking=0.2)
    G.draw_text(cv, CLIENT, x0, cy + 10, nm, B.FB, B.INK, 'ls', opacity=tu)
    G.draw_text(cv, URL, x0 + 2, cy + 54, 27, B.FM, B.ACTION, 'ls', opacity=tu)


def _count(t, t0, v, dur=0.8):
    u = K.EASE['out_cubic'](K.clamp((t - t0) / dur))
    return v * u


def data_card(cv, t, t0=6.45, t1=10.45):
    """The real report totals (Search Console, 3 months), top left, clear of her face."""
    if not (t0 <= t < t1):
        return
    u, out, op = B.pop(t, t0, t1, fout=0.3)
    w, h = 360, 290
    cx, cy = 222, 430 - 24 * (1 - u) - 30 * out
    pnl, pad = B.card(w, h, 32, accent=B.BLUE)
    K.draw(cv, pnl, cx, cy, scale=0.9 + 0.1 * u, opacity=op)
    x0, y0 = cx - w / 2 + 34, cy - h / 2
    tu = K.ramp(t, t0 + 0.15, t0 + 0.45, 'out_cubic') * (1 - out)
    G.draw_text(cv, 'SEARCH CONSOLE', x0, y0 + 56, 20, B.FS, B.BODY, 'ls', opacity=tu, tracking=0.16)
    G.draw_text(cv, 'Last 3 months', x0, y0 + 92, 26, B.FM, B.BODY, 'ls', opacity=tu)
    # the real total only (no rolling counter: in-between numbers were never in the report)
    G.draw_text(cv, '224', x0, y0 + 182, 74, B.FB, B.ACTION, 'ls', opacity=tu)
    G.draw_text(cv, 'clicks', x0 + G.measure('224', 74, B.FB) + 14, y0 + 182, 30, B.FS, B.INK, 'ls', opacity=tu)
    u2 = K.ramp(t, t0 + 0.55, t0 + 0.85, 'out_cubic') * (1 - out)
    G.draw_text(cv, '15.9K impressions', x0, y0 + 244, 30, B.FB, B.INK, 'ls', opacity=u2)


def service_chip(cv, t, t0=12.5, t1=14.85):
    """'I'm going to need more drivers': what the client's site offers (real), above her in the wide shot."""
    B.draw_chip(cv, t, 'Airport transfers · 24 hours', 540, 300, t0, t1, icon='clock', size=36)


# ---------------------------------------------------------------------------------------------- contract
def draw(t):
    cv = CLIP.plate(t, {0: 'band', 1: 'band'}, end_t0=T_END_CARD - 0.15)
    GB.intro_reveal(cv, t)
    if t < T_END_CARD:
        data_card(cv, t)
        client_card(cv, t)
        service_chip(cv, t)
        G.bottom_shade(cv, 0.42, 1330, opacity=1 - K.ramp(t, T_END_CARD - 0.4, T_END_CARD, 'inout_sine'))
        CAP.draw(cv, t, opacity=1 - K.ramp(t, T_END_CARD - 0.3, T_END_CARD - 0.05, 'inout_sine'))
        B.logo_bug(cv, t, 0.6, T_END_CARD)
    B.ai_label(cv, t, solid=t >= T_END_CARD, text='AI re-creation · real Search Console data', y=1712)
    B.end_card(cv, t, T_END_CARD, CLIENT, URL,
               fine=['AI re-creation. Search Console: coventryairporttaxis247.co.uk,',
                     '3 months to 18 Oct 2026. Results vary by business.'])
    return np.ascontiguousarray(cv, dtype=np.float32)


post = GB.post
FAST = [(0.0, 0.8)] + [(tc - 0.2, tc + 0.2) for tc, _ in CLIP.cuts] + [(T_END_CARD - 0.2, T_END_CARD + 1.8)]


def samples(t):
    return 7 if any(a <= t < b for a, b in FAST) else 1


def cues():
    c0, c1 = (tc for tc, _ in CLIP.cuts)
    return [
        dict(t=0.06, name='whoosh_fast', gain_db=-5),
        dict(t=0.92, name='card_slide', gain_db=-7),
        dict(t=1.30, name='toast_chime', gain_db=-9),
        dict(t=c0, name='whip', gain_db=-6),
        dict(t=6.47, name='card_slide', gain_db=-6, pan=-0.4),
        dict(t=6.80, name='coin', gain_db=-12, pan=-0.4),
        dict(t=c1, name='whip', gain_db=-6),
        dict(t=12.52, name='pop', gain_db=-7, params=dict(pitch=1.08)),
        dict(t=T_END_CARD, name='logo_sting', gain_db=-4),
        dict(t=T_END_CARD + 0.95, name='pop', gain_db=-7, params=dict(pitch=1.2)),
    ]


def prewarm():
    B.prewarm()
    _quads()
    _report()
    G.image_logo(LOGO, 150)
    B.chip('Airport transfers · 24 hours', 'clock', 36)
