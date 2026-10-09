"""pehle_wala_faces_proof.py - STAND-IN world for proofing the C26 face tile (face-compositor QA only, NOT the reel).

pehle_wala.py (motion-timeline-builder) is the reel; until it exists, this module puts pehle_wala_faces.draw_tile on a
stand-in of the BRIEF section 5 layout (inferno backdrop + bokeh, the real review player window, a simplified ad with
the real Blender chai glass, pins, counter / status chips, the payoff lockup, real snake captions from the measured
VO words) and the real finish (G.tx_finish with the L3 / D9 exposure pushes on the tile's frames), so the stills
show the tile in its true light, scale and neighbourhood. Render contract of render.py (DUR, LOOK, BPM, draw, post,
samples, prewarm). Outputs: <WS>/out/pehle_wala_faces_proof -> symlink to <WS>/pehle_wala/qa/faces/render.

    tools/heavy.sh python3 render.py pehle_wala_faces_proof --stills 14.9333,16.0,17.0333 --workers 1 --no-audio
    tools/heavy.sh python3 pehle_wala_faces_proof.py measure 15.6 16.0 28.5    # post-finish QA numbers (JSON)
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


# ============================================================================================ QA measurements
QA_OUT = '/home/user/100/workspace/jawad_reels/pehle_wala/qa/faces'
SKIN_PATCH = {'street_smirk': {'cheekL': (246, 433, 302, 489), 'cheekR': (395, 400, 465, 445), 'forehead': (300, 250, 380, 300)},
         'street_sunglasses': {'cheekL': (252, 394, 300, 442), 'cheekR': (395, 395, 460, 440), 'forehead': (300, 230, 380, 290)}}


def _still(t, mode, finish=True):
    import render
    M = sys.modules[__name__]
    os.environ['PWF_MODE'] = mode
    if finish:
        u8 = render.render_still(M, t, samples=1)
    else:
        u8 = K.to_srgb8(M.draw(t), t, dither=False)
    os.environ['PWF_MODE'] = 'full'
    return u8


def _luma(u8):
    return u8.astype(np.float32) @ np.float32([0.2126, 0.7152, 0.0722])


def _screen_of(t, sh, p):
    L = PF.layers(sh['pose'])
    m = PF.meta(sh['pose'])
    uv = (L['eye'][0] + (p[0] - m['eye_mid'][0]) * PF.SCALE, L['eye'][1] + (p[1] - m['eye_mid'][1]) * PF.SCALE)
    return PF._screen(t, sh, PF.feed_point(t, uv, sh))


def _hsv(rgb8):
    hsv = cv2.cvtColor(rgb8[None].astype(np.uint8), cv2.COLOR_RGB2HSV)[0].astype(np.float32)
    return dict(hue_deg=round(float(np.median(hsv[:, 0])) * 2, 1), sat=round(float(np.median(hsv[:, 1])) / 255, 3),
                val=round(float(np.median(hsv[:, 2])), 1))



def measure(ts):
    """Post-finish QA numbers per time: halo ring, blacks (with / without the finish's bloom), key, skin."""
    import render
    M = sys.modules[__name__]
    res = {}
    PF.prewarm()
    M.prewarm()
    for t in ts:
        sh = PF.shot_at(t)
        r = {}
        full, plate, matte = _still(t, 'full'), _still(t, 'plate'), _still(t, 'matte')
        jd = PF.jd_alpha(t)
        tile = PF.tile_alpha(t) > 0.999
        hard = (jd > 0.05).astype(np.uint8)
        ring = (cv2.dilate(hard, np.ones((7, 7), np.uint8)) - hard).astype(bool) & tile
        lf, lp, lm = _luma(full), _luma(plate), _luma(matte)
        r['halo_ring_post_finish'] = dict(full_minus_plate=round(float((lf - lp)[ring].mean()), 2),
                                          matte_minus_plate=round(float((lm - lp)[ring].mean()), 2), ring_px=int(ring.sum()))
        pf, pp = _still(t, 'full', False), _still(t, 'plate', False)
        r['halo_ring_pre_finish'] = round(float((_luma(pf) - _luma(pp))[ring].mean()), 2)
        body = (jd > 0.95) & tile
        away = tile & ~cv2.dilate(hard, np.ones((31, 31), np.uint8)).astype(bool)
        r['black'] = dict(subject_p2=round(float(np.percentile(lf[body], 2)), 1),
                          tile_plate_p2=round(float(np.percentile(lf[away], 2)), 1),
                          frame_p2=round(float(np.percentile(lf, 2)), 1),
                          frame_p0_5=round(float(np.percentile(lf, 0.5)), 1),
                          plate_render_same_px_p2=round(float(np.percentile(lp[body], 2)), 1))
        import jawad_grade as G
        os.environ['PWF_MODE'] = 'full'; c1 = M.draw(t); G.finish(c1, 'inferno', t, grain=0, bloom=0.0)
        os.environ['PWF_MODE'] = 'plate'; c2 = M.draw(t); G.finish(c2, 'inferno', t, grain=0, bloom=0.0)
        os.environ['PWF_MODE'] = 'full'
        b1, b2 = _luma(K.to_srgb8(c1, t, dither=False)), _luma(K.to_srgb8(c2, t, dither=False))
        r['black_bloom_off'] = dict(subject_p2=round(float(np.percentile(b1[body], 2)), 2),
                                    tile_plate_p2=round(float(np.percentile(b1[away], 2)), 2),
                                    frame_p2=round(float(np.percentile(b1, 2)), 2),
                                    plate_render_same_px_p2=round(float(np.percentile(b2[body], 2)), 2))
        ad = np.zeros(lf.shape, bool); ad[468:1228, 430:960] = True
        r['key'] = dict(subject_p99=round(float(np.percentile(lf[body], 99)), 1),
                        subject_p99_9=round(float(np.percentile(lf[body], 99.9)), 1),
                        ad_p99=round(float(np.percentile(lf[ad], 99)), 1), frame_p99_5=round(float(np.percentile(lf, 99.5)), 1))
        # skin: final frame vs the native source patch
        src = cv2.cvtColor(cv2.imread('/home/user/100/workspace/brand_reels/charsheet/crops/%s_2x.png' % sh['pose']), cv2.COLOR_BGR2RGB)
        sk = {}
        for nm, (x0, y0, x1, y1) in SKIN_PATCH[sh['pose']].items():
            a = _screen_of(t, sh, (x0, y0)); b = _screen_of(t, sh, (x1, y1))
            X0, Y0, X1, Y1 = int(round(a[0])) + 1, int(round(a[1])) + 1, int(round(b[0])) - 1, int(round(b[1])) - 1
            sk[nm] = dict(final=_hsv(full[Y0:Y1, X0:X1].reshape(-1, 3)), source=_hsv(src[y0:y1, x0:x1].reshape(-1, 3)),
                          screen_box=(X0, Y0, X1, Y1))
        r['skin'] = sk
        fr = PF.face_rect(t)
        x0, y0, x1, y1 = [int(round(v)) for v in fr]
        crop = full[max(0, y0 - 40):y1 + 20, max(0, x0 - 40):x1 + 40]
        p = os.path.join(QA_OUT, 'skin_%s_t%.2f_x3.png' % (sh['pose'], t))
        cv2.imwrite(p, cv2.cvtColor(cv2.resize(crop, None, fx=3, fy=3, interpolation=cv2.INTER_NEAREST), cv2.COLOR_RGB2BGR))
        r['face_crop_x3'] = p
        res['%.4f' % t] = r
    return res


if __name__ == '__main__':
    if len(sys.argv) > 2 and sys.argv[1] == 'measure':
        print(json.dumps(measure([float(x) for x in sys.argv[2:]]), indent=1))
