"""Scene images for Organic Fostering "You Are Here" — video version with people (after the static-post concept PDF).

Spine: one magenta-to-orange route line with eight stops (the stages from organicfostering.co.uk's journey page). The film
switches worlds the way the client's reference does: real people, a pastel dashboard, a paper-cut landscape, a bold type
slam, then the full route map with the glowing "You are here" pin. Captions are small word pills synced to the voice.

Usage: python3 frames_yah.py [n ...] -> workspace_yah/frames/scene_XX.png + storyboard.jpg
"""
import os, sys, math, glob
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'pipeline_cf'))
import numpy as np
import cv2
import frames_cf as F
import frames_cf2 as F2
from frames_cf import (R, W, H, draw, blur_sprite, tint, rrect, ts, solid, paste_spr, load_png_sprite, _wmask, PURPLE, ORANGE,
                       PLUM, IVORY, LAV, PEACH, LEAF, LAV_D, WHITE, N9, N8, N7)

S = os.path.abspath(os.path.join(HERE, '..', 'workspace_yah'))
OUT = f'{S}/frames'
WEB = F2.WEB
HAND = 'Caveat-700'
STOPS = ['Initial conversation', 'Initial home visit', 'Formal application', 'Checks and references', 'Fostering assessment',
         'Preparation training', 'Panel and decision', 'Induction and matching']
_X, _Y = R._X, R._Y


# ------------------------------------------------------------------ sources
def clip(cid, t=0.45, fx=0.5, fy=0.5, z=1.0, w=W, h=H, grade=True):
    cap = cv2.VideoCapture(f'{S}/clips/{cid}.mp4')
    cap.set(cv2.CAP_PROP_POS_FRAMES, int(cap.get(cv2.CAP_PROP_FRAME_COUNT) * t))
    ok, im = cap.read()
    out = F.cover(im[..., ::-1].astype(np.float32) / 255, fx, fy, z, w, h)
    return F.grade(out) if grade else out


def web(name, w, h, fx=0.5, fy=0.5):
    return F.grade(F2.web(name, w, h, fx, fy))


def prop(name):
    p = f'{S}/assets/{name}.png'
    if os.path.exists(p):
        return load_png_sprite(p)
    p = f'{F.S}/assets/{name}.png'
    if os.path.exists(p):
        return load_png_sprite(p)
    return F.lo2(name)


def rounded(img, r=34):
    h, w = img.shape[:2]
    m = cv2.resize(R.sdf_fill(R.rrect_alpha(w, h, r, 2)), (w, h))
    return np.concatenate([img * m[..., None], m[..., None]], 2).astype(np.float32)


# ------------------------------------------------------------------ route pieces
def grad_line(c, pts, width=18, k=1.0, glow=True):
    """Thick magenta→orange route line along a polyline (rounded), drawn to fraction k."""
    p = np.array(pts, np.float32)
    seg = np.cumsum(np.r_[0, np.hypot(*np.diff(p, axis=0).T)])
    L = seg[-1] * k
    keep = [q for q, s in zip(p, seg) if s <= L]
    i = len(keep)
    if i < len(p) and i > 0:
        u = (L - seg[i - 1]) / max(1e-6, seg[i] - seg[i - 1])
        keep.append(p[i - 1] + (p[i] - p[i - 1]) * u)
    if len(keep) < 2:
        return
    lay = np.zeros((H, W), np.uint8)
    cv2.polylines(lay, [(np.array(keep) * 4).astype(np.int32)], False, 255, int(width * 4), cv2.LINE_AA, shift=2)
    m = lay.astype(np.float32)[..., None] / 255
    # colour along the line's own length, projected roughly by x+y
    u = np.clip(((_X + _Y * 0.35) - (p[:, 0] + p[:, 1] * 0.35).min()) / max(1, np.ptp(p[:, 0] + p[:, 1] * 0.35)), 0, 1)[..., None]
    col = np.array(PURPLE[:3], np.float32) * (1 - u) + np.array(ORANGE[:3], np.float32) * u
    if glow:
        g = cv2.GaussianBlur(m[..., 0], (0, 0), width * 1.2)[..., None] * 0.55
        c[:] = c * (1 - g) + col * g
    c[:] = c * (1 - m) + col * m


def stop_dot(c, x, y, n=None, filled=False, dest=False, r=26, label=None, lx=0, ly=60, lsize=34, ink=PLUM):
    if filled:
        for rr, a in ((r * 2.6, 0.12), (r * 1.9, 0.2)):
            draw(c, rrect(rr * 2, rr * 2, rr, (*ORANGE[:3], a)), x, y)
        draw(c, F.grad_spr(r * 2.3, r * 2.3, r * 1.15), x, y)
    else:
        ring = LEAF if dest else PLUM
        draw(c, blur_sprite(rrect(r * 2 + 10, r * 2 + 10, r + 5, (0.36, 0.09, 0.31, 0.35)), 8), x, y + 6)
        draw(c, rrect(r * 2 + 12, r * 2 + 12, r + 6, ring), x, y)
        draw(c, rrect(r * 2 - 2, r * 2 - 2, r - 1, WHITE), x, y)
    if n is not None and not filled:
        s = ts('%02d' % n, 'Poppins-SemiBold', int(r * 0.85), PLUM)
        draw(c, s, x, y)
    if label:
        s = ts(label, N8, lsize, ink)
        draw(c, s, x + lx, y + ly)


def here_pill(c, x, y, size=34):
    s = ts('You are here', N9, size, WHITE)
    p = F.grad_spr(s.shape[1] + 56, s.shape[0] + 30, (s.shape[0] + 30) / 2)
    draw(c, blur_sprite(p, 18), x, y + 8, opacity=0.6)
    draw(c, p, x, y)
    draw(c, s, x, y)


def word_pill(c, text, y=1700, size=50, dark=False):
    """Reference-style caption: a small white pill with the spoken words."""
    s = ts(text, N8, size, PLUM if not dark else WHITE)
    w, h = s.shape[1] + 48, s.shape[0] + 26
    fill = (1, 1, 1, 0.96) if not dark else (0.2, 0.05, 0.17, 0.85)
    draw(c, blur_sprite(rrect(w, h, 14, (0, 0, 0, 0.4)), 14), W / 2 + 3, y + 10, opacity=0.5)
    draw(c, rrect(w, h, 14, fill), W / 2, y)
    draw(c, s, W / 2, y)


def route_strip(c, cur, y=150, x0=110, x1=970, light=True):
    """Progress strip: the eight stops in a row, current one glowing (the line runs up to it)."""
    xs = np.linspace(x0, x1, 8)
    lay = np.zeros((H, W), np.uint8)
    cv2.line(lay, (int(x0 * 4), int(y * 4)), (int(x1 * 4), int(y * 4)), 255, 6 * 4, cv2.LINE_AA, shift=2)
    m = lay.astype(np.float32)[..., None] / 255 * (0.35 if light else 0.5)
    base = np.array((1, 1, 1) if light else PLUM[:3], np.float32)
    c[:] = c * (1 - m) + base * m
    grad_line(c, [(x0, y), (xs[cur], y)], width=8, glow=False)
    for j, x in enumerate(xs):
        if j == cur:
            stop_dot(c, x, y, filled=True, r=14)
        else:
            col = (1, 1, 1, 0.95) if j > cur else (1.0, 0.85, 0.75, 1)
            draw(c, rrect(20, 20, 10, col), x, y)
    s = ts('STOP %02d / 08' % (cur + 1), 'Poppins-SemiBold', 24, WHITE if light else PLUM, 0.12)
    draw(c, s, x0 + s.shape[1] / 2 - 4, y + 44)


def people_card(c, img, x, y, rot=0.0, sc=1.0):
    sp = rounded(img, 40)
    draw(c, blur_sprite(tint(sp, PLUM[:3]), 30), x + 10, y + 34, scale=sc, rot=rot, opacity=0.45)
    border = rrect(sp.shape[1] + 20, sp.shape[0] + 20, 48, WHITE).copy()
    paste_spr(border, sp, border.shape[1] / 2, border.shape[0] / 2)
    draw(c, border, x, y, scale=sc, rot=rot)


def cta(c, x, y, text='Start your enquiry'):
    btn = F.grad_spr(760, 130, 65)
    draw(c, blur_sprite(btn, 24), x, y + 20, opacity=0.55)
    draw(c, btn, x, y)
    F.text_arrow(c, text, x, y)


def rewind(c, x, y, s=40, col=WHITE):
    m = np.zeros((s * 2, s * 4), np.uint8)
    for k in range(2):
        ox = k * s * 1.6
        cv2.fillPoly(m, [np.array([[ox + s * 1.6, 0], [ox + s * 1.6, s * 2], [ox, s]], np.int32)], 255, cv2.LINE_AA)
    draw(c, solid(m.astype(np.float32) / 255, col), x, y)


def stage_title(c, n, name, x=90, y=1300, light=False):
    ink = WHITE if light else PLUM
    s = ts('%02d' % n, N9, 150, (1, 1, 1, 0.22) if light else (0.36, 0.09, 0.31, 0.18))
    draw(c, s, x + s.shape[1] / 2, y)
    t = ts(name, N9, 74, ink)
    draw(c, blur_sprite(tint(t, (0, 0, 0)), 10), x + t.shape[1] / 2 + 3, y + 96, opacity=0.35 if light else 0)
    draw(c, t, x + t.shape[1] / 2, y + 90)


def paper_texture(c, amt=0.025, seed=3):
    rng = np.random.default_rng(seed)
    n = cv2.GaussianBlur(rng.normal(0, 1, (H // 2, W // 2)).astype(np.float32), (0, 0), 1.2)
    n = cv2.resize(n, (W, H))[..., None]
    return np.clip(c + n * amt, 0, 1)


def paper_layer(c, poly, col, shadow=0.35, off=(0, 14), blur=16):
    m = np.zeros((H, W), np.uint8)
    cv2.fillPoly(m, [np.array(poly, np.int32)], 255, cv2.LINE_AA)
    mf = m.astype(np.float32) / 255
    sh = cv2.GaussianBlur(np.roll(np.roll(mf, off[1], 0), off[0], 1), (0, 0), blur)[..., None] * shadow
    c[:] = c * (1 - sh)
    c[:] = c * (1 - mf[..., None]) + np.array(col[:3], np.float32) * mf[..., None]


def hill(y0, amp, freq, phase, ystep=6):
    xs = np.arange(-20, W + 40, 12)
    top = y0 + amp * np.sin(xs / W * math.pi * freq + phase) + amp * 0.35 * np.sin(xs / W * math.pi * freq * 2.3 + phase * 1.7)
    return [(x, t) for x, t in zip(xs, top)] + [(W + 40, H + 20), (-20, H + 20)]


def terrace(c, x, y, n=5, w=70, h=110, col=(0.72, 0.33, 0.27, 1)):
    """A little Manchester terrace: brick houses, pitched roofs, glowing windows."""
    for j in range(n):
        hx = x + j * w
        paper_layer(c, [(hx, y), (hx + w, y), (hx + w, y - h), (hx + w / 2, y - h - 46), (hx, y - h)], col, 0.25, (4, 8), 6)
        draw(c, rrect(w * 0.32, h * 0.26, 4, (1.0, 0.85, 0.5, 1)), hx + w * 0.3, y - h * 0.62)
        draw(c, rrect(w * 0.22, h * 0.36, 3, PLUM), hx + w * 0.72, y - h * 0.2)


# ------------------------------------------------------------------ scenes
def s01():   # "Fostering can feel like one huge leap…"
    c = clip(33379, 0.5, fx=0.58, fy=0.5)
    c = F.shade(c, 0.5, 0.75)
    for j, (txt, sz) in enumerate((('one huge', 130), ('leap?', 170))):
        g = F2.grad_text(txt, N9, sz)
        draw(c, blur_sprite(tint(g, (0, 0, 0)), 16), W / 2 + 6, 1250 + j * 150 + 10, opacity=0.4)
        draw(c, g, W / 2, 1250 + j * 150)
    F.pop(c, prop('qmark'), 860, 520, 0.5)
    word_pill(c, 'Fostering can feel like…')
    return c


def s02():   # "…into the unknown." — VHS rewind glitch over the street
    c = clip(46494, 0.4, fx=0.5, fy=0.5)
    c = c * 0.75 + 0.25 * cv2.GaussianBlur(c, (0, 0), 12)
    lines = ((np.sin(_Y * 0.9) > 0.6).astype(np.float32) * 0.12)[..., None]
    c = np.clip(c * (1 - lines) + lines, 0, 1)
    sh = 14
    c = np.stack([np.roll(c[..., 0], sh, 1), c[..., 1], np.roll(c[..., 2], -sh, 1)], 2)
    rng = np.random.default_rng(4)
    for _ in range(6):
        y0 = int(rng.uniform(200, H - 300)); hh = int(rng.uniform(20, 90))
        c[y0:y0 + hh] = np.roll(c[y0:y0 + hh], int(rng.uniform(-80, 80)), 1)
    rewind(c, 930, 170)
    word_pill(c, 'into the unknown.')
    return c


def s03():   # "But it isn't a leap. It's a route."
    c = F.canvas()
    chip = F2.chip_spr if hasattr(F2, 'chip_spr') else None
    s = ts('YOUR FOSTERING JOURNEY', 'Poppins-SemiBold', 28, PURPLE, 0.14)
    draw(c, rrect(s.shape[1] + 50, 62, 31, LAV), W / 2, 330)
    draw(c, s, W / 2, 330)
    draw(c, ts('Your route into', N9, 110, PLUM), W / 2, 470)
    draw(c, F2.grad_text('fostering.', N9, 130), W / 2, 600)
    pts = [(90, 960), (360, 960), (430, 1030), (430, 1150), (500, 1220), (700, 1220), (770, 1290), (770, 1420), (990, 1420)]
    grad_line(c, pts, 20, 1.0)
    for j, (x, y) in enumerate([(90, 960), (360, 960), (430, 1150), (700, 1220), (770, 1420), (990, 1420)]):
        stop_dot(c, x, y, filled=(j == 0), r=24)
    F.pop(c, prop('pin'), 120, 820, 0.42, rays=False)
    word_pill(c, "It's a route.")
    return c


def s04():   # "Eight stops. One at a time." — pastel dashboard
    c = F.canvas()
    glow = np.exp(-((_X - 900) ** 2 + (_Y - 300) ** 2) / (2 * 420 ** 2))[..., None] * 0.25
    c = c * (1 - glow) + np.array(LEAF[:3], np.float32) * glow * 0.6 + np.array((1, 1, 0.8), np.float32) * glow * 0.4
    card = rrect(900, 1040, 44, (1, 1, 1, 0.92))
    draw(c, blur_sprite(tint(card, PLUM[:3]), 30), W / 2, 900, opacity=0.25)
    draw(c, card, W / 2, 870)
    draw(c, ts('Organic Fostering', N8, 30, PLUM), 300, 420)
    draw(c, rrect(150, 44, 22, LAV), 860, 420)
    draw(c, ts('LIVE', 'Poppins-SemiBold', 22, PURPLE, 0.1), 860, 420)
    draw(c, ts('YOUR JOURNEY · STOPS', 'Poppins-Medium', 22, (0.36, 0.09, 0.31, 0.6), 0.14), 330, 500)
    s = ts('8', N9, 260, PLUM)
    draw(c, s, 230, 660)
    draw(c, ts('stops', N8, 70, PURPLE), 410, 700)
    for j in range(8):
        h = 60 + j * 22
        col = ORANGE if j == 0 else (0.94, 0.88, 0.92, 1)
        draw(c, rrect(70, h, 10, col), 200 + j * 92, 1000 - h / 2)
    for j, (k, v) in enumerate((('AT A TIME', '1'), ('FIRST STEP', 'Chat'), ('PRESSURE', 'None'))):
        x = 250 + j * 290
        draw(c, rrect(260, 170, 24, (0.98, 0.95, 0.97, 1)), x, 1150)
        draw(c, ts(k, 'Poppins-Medium', 20, (0.36, 0.09, 0.31, 0.6), 0.12), x, 1100)
        draw(c, ts(v, N9, 62, PLUM), x, 1170)
    cta(c, W / 2, 1300)
    word_pill(c, 'One at a time.')
    return c


def stage_scene(n, img, propname, extra=None, rot=-3, fy=760):
    c = F.canvas()
    c = c * 0.94 + np.array(LAV[:3], np.float32) * 0.06
    route_strip(c, n - 1, light=False)
    people_card(c, img, W / 2, fy, rot=rot)
    F.pop(c, prop(propname), 880, fy - img.shape[0] / 2 + 10, 0.5)
    stage_title(c, n, STOPS[n - 1], y=1290)
    if extra:
        extra(c)
    return c


def s05():   # Stop 1: "an initial conversation. Ask your questions…"
    c = stage_scene(1, clip(39791, 0.5, fx=0.5, fy=0.45, w=760, h=860), 'phone')
    here_pill(c, 300, 340)
    word_pill(c, 'Ask your questions.')
    return c


def s06():   # Stop 2: "a home visit. We meet you, and the people you live with."
    c = stage_scene(2, clip(4725, 0.55, fx=0.5, fy=0.4, w=820, h=820), 'house', rot=3)
    word_pill(c, 'the people you live with.')
    return c


def s07():   # Stop 3: "a formal application, only if moving forward feels right."
    c = stage_scene(3, clip(46533, 0.5, fx=0.5, fy=0.4, w=820, h=820), 'clipboard')
    word_pill(c, 'only if it feels right.')
    return c


def s08():   # Stop 4: "checks and references, including an enhanced DBS check."
    def ex(c):
        F.chip(c, 'Enhanced DBS check', 300, 1580, fill=LEAF, size=36, rot=-2)
    c = stage_scene(4, clip(22857, 0.5, fx=0.5, fy=0.6, w=820, h=820), 'shield', ex, rot=2)
    word_pill(c, 'checks and references.', y=1730)
    return c


def s09():   # Stop 5: "your fostering assessment. Honest conversations. Nobody expects a perfect life!"
    def ex(c):
        s = solid(_wmask('Nobody expects a perfect life.', HAND, 76), PURPLE)
        draw(c, s, W / 2, 1590, rot=-3)
    c = stage_scene(5, web('adviser-conversation.webp', 820, 820, 0.5, 0.5), 'speech', ex)
    word_pill(c, 'Honest conversations.', y=1740)
    return c


def s10():   # Stop 6: "preparation training, which can overlap with your assessment."
    def ex(c):
        lay = np.zeros((H, W), np.uint8)
        for a in np.linspace(math.pi * 1.05, math.pi * 1.95, 14):
            p0 = (W / 2 + 330 * math.cos(a), 300 + 140 * math.sin(a) + 40)
            p1 = (W / 2 + 330 * math.cos(a + 0.035), 300 + 140 * math.sin(a + 0.035) + 40)
            cv2.line(lay, (int(p0[0] * 4), int(p0[1] * 4)), (int(p1[0] * 4), int(p1[1] * 4)), 255, 5 * 4, cv2.LINE_AA, shift=2)
        m = lay.astype(np.float32)[..., None] / 255
        c[:] = c * (1 - m) + np.array(ORANGE[:3], np.float32) * m
        s = solid(_wmask('these two can overlap', HAND, 56), ORANGE)
        draw(c, s, W / 2 + 120, 270, rot=-2)
    c = stage_scene(6, clip(48712, 0.5, fx=0.45, fy=0.5, w=820, h=820), 'books', ex, rot=3)
    word_pill(c, 'can overlap with your assessment.')
    return c


def s11():   # Stops 7 + 8 in a paper-cut Manchester: "Seven: panel and decision. Eight: induction and matching."
    sky = np.zeros((H, W, 3), np.float32)
    k = (_Y / H)[..., None]
    sky[:] = np.array((1.0, 0.92, 0.88), np.float32) * (1 - k) + np.array((0.98, 0.84, 0.88), np.float32) * k
    c = sky
    sun = (840, 380)
    draw(c, rrect(220, 220, 110, (1.0, 0.75, 0.3, 1)), *sun)
    draw(c, blur_sprite(rrect(260, 260, 130, (1.0, 0.7, 0.3, 0.6)), 30), *sun)
    for cx, cy, sc in ((230, 300, 1.0), (620, 220, 0.7)):
        for dx, r in ((-60, 50), (0, 70), (70, 52)):
            draw(c, rrect(r * 2 * sc, r * 1.6 * sc, r * sc, (1, 1, 1, 0.95)), cx + dx * sc, cy)
    paper_layer(c, hill(820, 60, 1.6, 0.4), (0.84, 0.66, 0.8, 1))
    terrace(c, 120, 900, 5, 64, 100, (0.75, 0.42, 0.55, 1))
    paper_layer(c, hill(1000, 70, 1.2, 1.9), (0.72, 0.5, 0.7, 1))
    terrace(c, 600, 1060, 5, 72, 110, (0.78, 0.36, 0.3, 1))
    paper_layer(c, hill(1240, 80, 1.0, 3.0), (0.36, 0.09, 0.31, 1), 0.4)
    # the route as a road, ending at home
    road = [(-20, 1700), (220, 1640), (380, 1520), (300, 1420), (420, 1330), (650, 1300), (820, 1240)]
    grad_line(c, road, 30, 1.0)
    stop_dot(c, 380, 1520, n=7, r=30)
    stop_dot(c, 820, 1240, n=8, r=34, dest=True)
    paper_layer(c, [(720, 1210), (930, 1210), (930, 1060), (825, 960), (720, 1060)], (1.0, 0.98, 0.95, 1), 0.4)
    paper_layer(c, [(700, 1068), (825, 945), (950, 1068), (950, 1040), (825, 915), (700, 1040)], PURPLE, 0.3)
    draw(c, rrect(54, 84, 6, ORANGE), 790, 1168)
    draw(c, rrect(54, 46, 6, (1.0, 0.85, 0.5, 1)), 870, 1110)
    plane = prop('plane')
    lay = np.zeros((H, W), np.uint8)
    for t in np.linspace(0, 1, 26):
        x = 200 + 500 * t; y = 640 - 180 * math.sin(t * math.pi) + 40 * t
        cv2.circle(lay, (int(x), int(y)), 4, 255, -1, cv2.LINE_AA)
    m = lay.astype(np.float32)[..., None] / 255
    c = c * (1 - m) + np.array(PURPLE[:3], np.float32) * m
    draw(c, plane, 730, 640, scale=0.32, rot=12)
    c = paper_texture(c)
    F.pop(c, prop('badge'), 210, 1380, 0.36)
    F.pop(c, prop('key'), 930, 1420, 0.36)
    draw(c, ts('Panel and decision', N8, 40, WHITE), 300, 1600)
    draw(c, ts('Induction and matching', N8, 40, WHITE), 760, 1340)
    word_pill(c, 'Eight: induction and matching.', y=1780)
    return c


def s12():   # "The whole route can take up to eight months." — bold type slam
    c = np.zeros((H, W, 3), np.float32) + np.array(PURPLE[:3], np.float32)
    ang = np.arctan2(_Y - 1500, _X - W / 2)
    rays = ((np.sin(ang * 36) > 0.3) & (np.hypot(_X - W / 2, _Y - 1500) > 380)).astype(np.float32)[..., None]
    c = c * (1 - rays * 0.25) + np.array(ORANGE[:3], np.float32) * rays * 0.25
    draw(c, rrect(820, 820, 410, ORANGE), W / 2, 1560)
    for txt, y, col, sz in (('UP TO', 420, WHITE, 170), ('EIGHT', 600, (1.0, 0.85, 0.35, 1), 250), ('MONTHS.', 790, WHITE, 210)):
        s = ts(txt, N9, sz, col, -0.01)
        draw(c, blur_sprite(tint(s, (0, 0, 0)), 14), W / 2 + 6, y + 10, opacity=0.35)
        draw(c, s, W / 2, y)
    F.pop(c, prop('calendar'), W / 2, 1420, 0.62, rays=False)
    F.chip(c, 'Source: GOV.UK', W / 2, 1000, fill=WHITE, ink=PLUM, size=32)
    word_pill(c, 'up to eight months.', y=1780, dark=True)
    return c


ROUTE = [(130, 760), (540, 760), (950, 760), (950, 1040), (540, 1040), (130, 1040), (130, 1320), (540, 1320), (950, 1320)]


def route_map(c, here_glow=1.0):
    pts = [(130, 760), (950, 760), (950, 1040), (130, 1040), (130, 1320), (950, 1320)]
    grad_line(c, pts, 20, 1.0)
    pos = [(130, 760), (540, 760), (950, 760), (950, 1040), (540, 1040), (130, 1040), (300, 1320), (780, 1320)]
    labels = ['Initial\nconversation', 'Initial\nhome visit', 'Formal\napplication', 'Checks and\nreferences', 'Fostering\nassessment',
              'Preparation\ntraining', 'Panel and\ndecision', 'Induction and\nmatching']
    for j, ((x, y), lab) in enumerate(zip(pos, labels)):
        stop_dot(c, x, y, n=j + 1, filled=(j == 0), dest=(j == 7), r=26)
        dx, dy = {2: (-170, 46), 5: (150, 46)}.get(j, (0, 64))
        for li, ln in enumerate(lab.split('\n')):
            s = ts(ln, N8, 30, PLUM)
            draw(c, s, x + dx, y + dy + li * 36)


def s13():   # "But today? You only need stop one. Your first enquiry is only a conversation."
    c = F.canvas()
    s = ts('YOUR FOSTERING JOURNEY', 'Poppins-SemiBold', 26, PURPLE, 0.14)
    draw(c, rrect(s.shape[1] + 50, 58, 29, LAV), 90 + (s.shape[1] + 50) / 2, 300)
    draw(c, s, 90 + (s.shape[1] + 50) / 2, 300)
    draw(c, ts('Your route into', N9, 88, PLUM), 90 + ts('Your route into', N9, 88, PLUM).shape[1] / 2, 410)
    g = F2.grad_text('fostering.', N9, 100)
    draw(c, g, 90 + g.shape[1] / 2, 515)
    route_map(c)
    here_pill(c, 300, 680, 32)
    draw(c, ts('The whole route can take up to eight months (GOV.UK).', 'Poppins-Medium', 24, (0.36, 0.09, 0.31, 0.7)), W / 2, 1480)
    word_pill(c, 'Your first enquiry is only a conversation.', y=1700, size=40)
    return c


def s14():   # "Start your enquiry. No pressure, no obligation. Organic Fostering." — split end card
    c = F.canvas()
    bot = clip(18258, 0.5, fx=0.5, fy=0.5, w=W, h=H // 2)
    bot = bot * 0.55 + np.array(PLUM[:3], np.float32) * 0.45
    c[H // 2:] = bot
    lg = F.logo()
    draw(c, lg, W / 2, 300, scale=640 / lg.shape[1])
    cta(c, W / 2, 610)
    draw(c, ts('0161 241 1332', N9, 64, PURPLE), W / 2, 770)
    s = ts('Rated Good by Ofsted · Inspected May 2025', N7, 30, PLUM)
    draw(c, F.star(ORANGE, 30), W / 2 - s.shape[1] / 2 - 22, 860)
    draw(c, s, W / 2 + 10, 860)
    for j, (txt, col) in enumerate((('No pressure.', WHITE), ('No obligation.', (1.0, 0.8, 0.55, 1)))):
        t = ts(txt, N9, 120, col)
        draw(c, blur_sprite(tint(t, (0, 0, 0)), 14), W / 2 + 5, 1250 + j * 150 + 8, opacity=0.4)
        draw(c, t, W / 2, 1250 + j * 150)
    here_pill(c, W / 2, 1060, 36)
    return c


SCENES = [s01, s02, s03, s04, s05, s06, s07, s08, s09, s10, s11, s12, s13, s14]


if __name__ == '__main__':
    os.makedirs(OUT, exist_ok=True)
    only = [int(a) for a in sys.argv[1:]]
    for j, fn in enumerate(SCENES, start=1):
        if only and j not in only:
            continue
        im = F.to_u8(R.post(fn(), j, bloom=0.1, grain=0.01, vig=0.2 if j in (1, 2) else 0.0))
        cv2.imwrite(f'{OUT}/scene_{j:02d}.png', im)
        print('scene', j, flush=True)
    fs = sorted(glob.glob(f'{OUT}/scene_*.png'))
    th = [cv2.resize(cv2.imread(f), (324, 576)) for f in fs]
    while len(th) % 7:
        th.append(np.zeros_like(th[0]))
    cv2.imwrite(f'{OUT}/storyboard.jpg', np.vstack([np.hstack(th[i:i + 7]) for i in range(0, len(th), 7)]), [cv2.IMWRITE_JPEG_QUALITY, 90])
