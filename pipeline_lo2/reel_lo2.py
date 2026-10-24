"""Organic Fostering — "Leave the Light On", version 2 (9:16, 30 s): bright graphic-poster style with real 3D and real
website photography.

Look: the campaign key visual's language (cream paper, magenta / orange blobs, green brush stroke, dots, bold
black-magenta-orange Poppins type). New Blender 3D: a real light switch macro (opener), a cut-away dollhouse whose
rooms light up one by one (each room dives into a real organicfostering.co.uk photo), a 3D word "HOME" the camera
flies through into the arrival, and a glossy 3D heart on the end card. Transitions: light burst, blob wipes, heart
iris, split slides, 3D card flips, room dives and the HOME fly-through. Same story beats and calm male voiceover as v1.

Usage:
  python3 reel_lo2.py still 1.0,5.0
  python3 reel_lo2.py range 0 900
"""
import os, sys, math, json, glob, functools
HERE = os.path.dirname(os.path.abspath(__file__))
os.environ['REEL_WORKDIR'] = os.path.abspath(os.path.join(HERE, '..', 'workspace_lo2'))
sys.path.insert(0, os.path.join(HERE, '..', 'pipeline_lo'))
sys.path.insert(0, os.path.join(HERE, '..', 'pipeline_su'))
import numpy as np
import cv2
import reel_lo as V1
from reel_lo import call_screen, time_at, VO, PHRASES, LINE_DUR, FPS
from reel_su import paste, fitted, png, phone_body, screen_mask, draw_phone, PW, PH, PB, PX, PK, PS, PM
from reel_of import word_spr, shake, check_spr, rrect_spr
from engine import *  # noqa: F401,F403
import engine as E

S = os.path.abspath(os.path.join(HERE, '..', 'workspace_lo2'))     # v2 outputs + new assets (engine keeps v1's)
WHITE_ = (1.0, 1.0, 1.0, 1.0)
CREAM = hexc('#F7F0E5')
BLACK = hexc('#1C1A1B')
MAG = hexc('#C90663')
ORA = hexc('#FF6A0D')
GRN = hexc('#92C31F')
PINKN = hexc('#FF4F9A')
A3 = f'{S}/assets3d'
WEB = f'{S}/web/img'

# ------------------------------------------------------------------ timeline (same beats + VO as version 1)
T = dict(hook=0.0, call=3.3, ready=7.4, arrive=15.2, payoff=18.2, rise=22.9, end=26.0)
DUR = 30.0
NF = int(DUR * FPS)
SW_FLIP = 14 / 24                 # rocker flips on this frame of the switch render
SW_END = 1.25                     # switch macro hands over to the poster world
ANSWER = V1.ANSWER
SHOT_LEN = (T['arrive'] - T['ready']) / 4
TR = 0.45
HOME0, HOME1 = T['arrive'] - 0.55, T['arrive'] + 0.45      # 3D HOME fly-through window (24 frames)
FADE = 1.15
# dollhouse room -> website photo (focal point x, y), label, shape
ROOMS = [('balanced-home-reading-2026-09-23.webp', 0.5, 0.45, 'A STORY AT BEDTIME', 'circle'),
         ('07-siblings-growing-together.webp', 0.5, 0.4, 'ROOM FOR BROTHERS & SISTERS', 'arch'),
         ('home-belonging.webp', 0.55, 0.45, 'SOMETHING WARM TO EAT', 'heart'),
         ('hero-family.webp', 0.66, 0.5, 'READY AT THE DOOR', 'rect')]
ON_FRAMES = [8, 32, 56, 80]
ROOM_ON = 0.12                    # room light switches on this long into its shot
Z0, Z1 = 0.28, 0.72               # dive into the room
M0, M1 = 0.6, 0.98                # photo shape grows out of the room

_Y, _X = np.mgrid[0:H, 0:W].astype(np.float32)


# ------------------------------------------------------------------ loaders
@functools.lru_cache(maxsize=16)
def photo(name):
    return cv2.imread(f'{WEB}/{name}')[..., ::-1].astype(np.float32) / 255.0


def kb(name, w, h, z=1.0, fx=0.5, fy=0.5):
    """Cover-crop a website photo into w x h, zoomed by z around focal point (fx, fy)."""
    im = photo(name)
    ih, iw = im.shape[:2]
    sc = max(w / iw, h / ih) * z
    cw, ch = w / sc, h / sc
    x0 = clamp(fx * iw - cw / 2, 0, iw - cw)
    y0 = clamp(fy * ih - ch / 2, 0, ih - ch)
    M = np.float32([[sc, 0, -x0 * sc], [0, sc, -y0 * sc]])
    return cv2.warpAffine(im, M, (int(w), int(h)), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)


def fill_box(name, cx, cy, bw, bh, z=1.0, fx=0.5, fy=0.5):
    """Full-frame layer with the photo cover-cropped into the box centred at (cx, cy)."""
    out = np.zeros((H, W, 3), np.float32)
    bw, bh = int(max(4, bw)), int(max(4, bh))
    im = kb(name, bw, bh, z, fx, fy)
    x0, y0 = int(cx - bw / 2), int(cy - bh / 2)
    sx0, sy0 = max(0, -x0), max(0, -y0)
    dx0, dy0 = max(0, x0), max(0, y0)
    dx1, dy1 = min(W, x0 + bw), min(H, y0 + bh)
    if dx1 > dx0 and dy1 > dy0:
        out[dy0:dy1, dx0:dx1] = im[sy0:sy0 + dy1 - dy0, sx0:sx0 + dx1 - dx0]
    return out


def warm(c, k=0.15):
    return np.clip(c * np.array([1 + k * 0.6, 1 + k * 0.15, 1 - k * 0.4], np.float32), 0, 1.2)


_files = {}


def files(name):
    if not _files.get(name):
        _files[name] = sorted(glob.glob(f'{A3}/{name}/*.png'))
    return _files[name]


@functools.lru_cache(maxsize=48)
def sprite3d(name, i):
    return load_png_sprite(files(name)[i])


def sprite_at(name, f):
    """Frame-blended 3D sprite at fractional frame f (premultiplied, so a plain mix is correct)."""
    fs = files(name)
    if not fs:
        return np.zeros((8, 8, 4), np.float32)
    f = clamp(f, 0, len(fs) - 1)
    i0 = int(f)
    i1 = min(i0 + 1, len(fs) - 1)
    a = f - i0
    s0 = sprite3d(name, i0)
    return s0 if a < 0.05 or i1 == i0 else s0 * (1 - a) + sprite3d(name, i1) * a


def full3d(name, f):
    """Opaque full-frame 3D render, covering 9:16."""
    fs = files(name)
    if not fs:
        return np.zeros((H, W, 3), np.float32)
    i = int(clamp(round(f), 0, len(fs) - 1))
    im = cv2.imread(fs[i])[..., ::-1].astype(np.float32) / 255.0
    return cv2.resize(im, (W, H), interpolation=cv2.INTER_CUBIC)


@functools.lru_cache(maxsize=1)
def room_track():
    p = f'{A3}/house_rooms.json'
    return json.load(open(p)) if os.path.exists(p) else [[(400, 400)] * 4] * 132


# ------------------------------------------------------------------ shape masks
def m_circle(cx, cy, r, soft=1.5):
    d = np.sqrt((_X - cx) ** 2 + (_Y - cy) ** 2)
    return np.clip((r - d) / soft + 0.5, 0, 1)


def m_rrect(cx, cy, w, h, r):
    r = min(r, w / 2, h / 2)
    qx = np.abs(_X - cx) - (w / 2 - r)
    qy = np.abs(_Y - cy) - (h / 2 - r)
    d = np.sqrt(np.maximum(qx, 0) ** 2 + np.maximum(qy, 0) ** 2) + np.minimum(np.maximum(qx, qy), 0) - r
    return np.clip(-d / 1.5 + 0.5, 0, 1)


def m_arch(cx, cy, w, h):
    top = cy - h / 2 + w / 2
    body = m_rrect(cx, (top + cy + h / 2) / 2, w, (cy + h / 2) - top, 24)
    return np.maximum(body, m_circle(cx, top, w / 2))


@functools.lru_cache(maxsize=1)
def heart_poly():
    pts = []
    for i in range(240):
        a = i / 240 * 2 * math.pi
        x = 16 * math.sin(a) ** 3
        y = -(13 * math.cos(a) - 5 * math.cos(2 * a) - 2 * math.cos(3 * a) - math.cos(4 * a))
        pts.append((x / 17.0, (y + 2.5) / 17.0))
    return np.array(pts, np.float32)


def m_heart(cx, cy, s):
    m = np.zeros((H, W), np.uint8)
    p = heart_poly() * s + np.array([cx, cy], np.float32)
    p = np.clip(p, -4000, 6000)
    cv2.fillPoly(m, [(p * 4).astype(np.int32)], 255, cv2.LINE_AA, shift=2)
    return m.astype(np.float32) / 255.0


def shape_mask(kind, cx, cy, size):
    if kind == 'circle':
        return m_circle(cx, cy, size / 2)
    if kind == 'arch':
        return m_arch(cx, cy, size * 0.84, size * 1.12)
    if kind == 'heart':
        return m_heart(cx, cy, size * 0.6)
    return m_rrect(cx, cy, size * 0.9, size * 1.1, 60)


def framed(c, fill, mask, border=12, shadow=True, border_col=WHITE_):
    """Composite a layer inside a shape with a white sticker border and a soft drop shadow."""
    if border:
        k = np.ones((border * 2 + 1, border * 2 + 1), np.uint8)
        ring = cv2.dilate(mask, k)
    else:
        ring = mask
    if shadow:
        sh = cv2.GaussianBlur(ring, (0, 0), 18)
        sh = np.roll(np.roll(sh, 20, 0), 10, 1)[..., None] * 0.32
        c = c * (1 - sh) + np.array([0.3, 0.12, 0.06], np.float32) * sh
    if border:
        c = c * (1 - ring[..., None]) + np.array(border_col[:3], np.float32) * ring[..., None]
    m = mask[..., None]
    return c * (1 - m) + fill * m


# ------------------------------------------------------------------ poster background + decorations
@functools.lru_cache(maxsize=1)
def paper():
    c = np.ones((H, W, 3), np.float32) * np.array(CREAM[:3], np.float32)
    rng = np.random.default_rng(2)
    n = rng.normal(0, 1, (H // 2, W // 2)).astype(np.float32)
    n = cv2.resize(cv2.GaussianBlur(n, (0, 0), 1.2), (W, H))[..., None]
    return c + n * 0.012


def blob(c, cx, cy, r, col, t, seed=0, op=1.0):
    """Wobbly organic blob (the key visual's orange / magenta shapes)."""
    if r < 2 or op <= 0:
        return c
    pts = []
    for i in range(90):
        a = i / 90 * 2 * math.pi
        rr = r * (1 + 0.06 * math.sin(3 * a + t * 1.3 + seed) + 0.04 * math.sin(5 * a - t * 0.9 + seed * 2))
        pts.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))
    m = np.zeros((H, W), np.uint8)
    p = np.clip(np.array(pts), -4000, 6000)
    cv2.fillPoly(m, [(p * 4).astype(np.int32)], 255, cv2.LINE_AA, shift=2)
    m = (m.astype(np.float32) / 255.0)[..., None] * op
    return c * (1 - m) + np.array(col[:3], np.float32) * m


def brush(c, x0, y0, length, k, col=GRN, thick=26, tilt=-0.06):
    """Green brush stroke that paints itself on (tapered ends)."""
    if k <= 0:
        return c
    n = 80
    m = np.zeros((H, W), np.uint8)
    for i in range(int(n * clamp(k))):
        u = i / n
        x = x0 + length * u
        y = y0 + length * tilt * u + 6 * math.sin(u * 7)
        w_ = thick * (0.35 + 0.65 * math.sin(math.pi * min(1, u * 1.1)))
        cv2.circle(m, (int(x * 4), int(y * 4)), max(8, int(w_ * 2)), 255, -1, cv2.LINE_AA, shift=2)
    m = (m.astype(np.float32) / 255.0)[..., None]
    return c * (1 - m) + np.array(col[:3], np.float32) * m


def dot(c, cx, cy, r, col, k=1.0):
    if k <= 0:
        return c
    m = m_circle(cx, cy, max(0.5, r * e_out_back(clamp(k), 2.5)))[..., None]
    return c * (1 - m) + np.array(col[:3], np.float32) * m


def stamp_text(c, text, x, y, size, col, t, t0, fname=PK, rot=0.0, glow=None):
    """Bold word that slams in with overshoot (poster headline animation). x is the left edge."""
    k = prog(t, t0, t0 + 0.4)
    if k <= 0:
        return c
    s = word_spr(text, fname, size, col)
    sc = 1.6 - 0.6 * e_out_back(k, 2.2)
    cx = x + s.shape[1] / 2
    if glow is not None:
        draw(c, blur_sprite(tint(s, glow[:3]), 18), cx, y, scale=sc, rot=rot, opacity=0.8 * min(1, k * 2), mode='add')
    else:
        draw(c, blur_sprite(tint(s, (0.3, 0.12, 0.05)), 10), cx + 6, y + 10, scale=sc, rot=rot, opacity=0.25 * min(1, k * 2))
    draw(c, s, cx, y, scale=sc, rot=rot, opacity=min(1, k * 2.5))
    return c


def sticker(c, text, x, y, t, t0, fill=MAG, ink=WHITE_, rot=-6, size=34):
    k = prog(t, t0, t0 + 0.35)
    if k <= 0:
        return
    p = pill(text, PK, size, pad_x=30, pad_y=16, fill=fill, border=None, text_color=ink, tracking=0.04)
    draw(c, blur_sprite(tint(p, (0.3, 0.1, 0.05)), 10), x + 8, y + 12, rot=rot, opacity=0.3 * k)
    draw(c, p, x, y, scale=e_out_back(k, 2.6), rot=rot, opacity=min(1, k * 3))


def stamp_check(c, x, y, t, t0, size=110):
    k = prog(t, t0, t0 + 0.3)
    if k <= 0:
        return
    sc = 1.8 - 0.8 * e_out_back(k, 2.0)
    draw(c, rrect_spr(size + 40, size + 40, (size + 40) / 2, (1, 1, 1, 1)), x, y, scale=sc, opacity=min(1, k * 3))
    draw(c, check_spr(size, GRN), x, y, scale=sc, rot=-12 * (1 - k), opacity=min(1, k * 3))
    if k < 1:
        draw(c, ring_sprite(int(size * 3), size * 0.6 + 80 * k, 5, GRN, glow=8), x, y, opacity=1 - k)


def polaroid(c, name, fx, fy, cx, cy, w, h, label, t, t0, rot=5, from_x=1500):
    """A real website photo on a white instant-print card that slides in and settles."""
    k = prog(t, t0, t0 + 0.55)
    if k <= 0:
        return c
    e = e_out_back(k, 1.4)
    card = np.ones((h + 120, w + 40, 4), np.float32)
    card[20:20 + h, 20:20 + w, :3] = kb(name, w, h, 1.05 + 0.04 * prog(t, t0, t0 + 4), fx, fy)
    s = word_spr(label, PX, 36, BLACK)
    paste(card, s, card.shape[1] / 2, h + 20 + 50)
    x = lerp(from_x, cx, e)
    r = lerp(rot + 18 * np.sign(from_x - cx), rot, e)
    draw(c, blur_sprite(tint(card, (0.3, 0.12, 0.06)), 16), x + 14, cy + 22, rot=r, opacity=0.35 * min(1, k * 2))
    draw(c, card, x, cy, rot=r)
    return c


def captions(c, t, key, y=1740, size=46):
    """Sticker-box captions: the phrase's box pops in, words reveal one by one, newest word in orange."""
    if key not in VO:
        return
    lt = t - VO[key]
    if lt < 0 or lt > LINE_DUR[key] + 0.35:
        return
    phrases = PHRASES[key]
    idx = 0
    for i, (p0, _) in enumerate(phrases):
        if lt >= p0:
            idx = i
    p0, text = phrases[idx]
    p1 = phrases[idx + 1][0] if idx + 1 < len(phrases) else LINE_DUR[key]
    words = text.split(' ')
    n = max(1, int(math.ceil(clamp((lt - p0) / max(0.3, p1 - p0 - 0.25)) * len(words))))
    op = 1 - prog(lt, LINE_DUR[key] + 0.05, LINE_DUR[key] + 0.35)
    kpop = e_out_back(prog(lt, p0, p0 + 0.25), 2.0)
    full = word_spr(text, PX, size, WHITE_)
    lines = [words] if full.shape[1] < 900 else [words[:(len(words) + 1) // 2], words[(len(words) + 1) // 2:]]
    count = 0
    for li, ws in enumerate(lines):
        if count >= n:
            break
        yy = y + (li - (len(lines) - 1) / 2) * size * 1.55
        fullw = word_spr(' '.join(ws), PX, size, WHITE_).shape[1]
        draw(c, rrect_spr(int(fullw + 54), int(size * 1.45), 22, (0.11, 0.1, 0.1, 0.88)), W / 2, yy,
             scale=0.85 + 0.15 * kpop, opacity=op)
        k = min(len(ws), n - count)
        spr = word_spr(' '.join(ws[:k]), PX, size, WHITE_).copy()      # one sprite per line keeps a true baseline
        if count + k == n:                                             # newest word in orange
            cut = word_spr(' '.join(ws[:k - 1]), PX, size, WHITE_).shape[1] + int(size * 0.12) if k > 1 else 0
            spr[:, cut:, :3] = spr[:, cut:, 3:4] * np.array(ORA[:3], np.float32)
        draw(c, spr, W / 2 - fullw / 2 + spr.shape[1] / 2, yy, opacity=op)
        count += len(ws)


# ------------------------------------------------------------------ 3D dollhouse helpers
HX, HY, HS = 540, 1010, 1.28


def house_frame(t):
    """Dollhouse frame for time t: each room lights as its shot begins; afterwards the house keeps turning."""
    knots = [(T['ready'] - 0.33, 0)] + [(T['ready'] + j * SHOT_LEN + ROOM_ON, ON_FRAMES[j]) for j in range(4)] + \
            [(T['arrive'], 100), (T['payoff'], 100), (T['rise'], 131)]
    if t < knots[0][0]:
        return 0
    for (a, fa), (b, fb) in zip(knots, knots[1:]):
        if t < b:
            return lerp(fa, fb, clamp((t - a) / max(1e-3, b - a)))
    return 131


def room_screen(f, j, cx=HX, cy=HY, sc=HS):
    tr = room_track()
    rx, ry = tr[int(clamp(round(f), 0, len(tr) - 1))][j]
    return cx + (rx - 400) * sc, cy + (ry - 400) * sc


def house_view(t, j, lt):
    """Poster paper + 3D dollhouse; diving into room j."""
    c = paper().copy()
    c = blob(c, 900, 420, 260, ORA, t, 5 + j)
    c = blob(c, 150, 1600, 240, MAG, t, 9 + j)
    f = house_frame(t)
    ez = e_in_cubic(prog(lt, Z0, Z1))
    z = 1 + 2.4 * ez
    rx, ry = room_screen(f, j)
    tx, ty = lerp(rx, W / 2, ez), lerp(ry, 930, ez)
    sc = HS * z
    cx = tx - (rx - HX) / HS * sc
    cy = ty - (ry - HY) / HS * sc
    draw(c, sprite_at('house', f), cx, cy, scale=sc)
    kk = prog(lt, ROOM_ON, ROOM_ON + 0.4)            # little "lights on" ring at the room
    if 0 < kk < 1:
        draw(c, ring_sprite(260, 30 + 90 * kk, 6, ORA, glow=10), rx, ry, opacity=1 - kk)
    return c, (tx, ty)


def ready_shot(t, j, lt):
    name, fx, fy, label, kind = ROOMS[j]
    c, (rx, ry) = house_view(t, j, lt)
    km = prog(lt, M0, M1)
    if km > 0:
        e = e_out_cubic(km)
        size = lerp(60, 830, e)
        cx, cy = lerp(rx, W / 2, e), lerp(ry, 1010, e)
        fill = warm(fill_box(name, cx, cy, size * 1.25, size * 1.4, 1.12 - 0.08 * prog(lt, M0, SHOT_LEN), fx, fy), 0.08)
        bg = paper().copy()
        bg = blob(bg, [880, 160, 900, 150][j], [1520, 400, 380, 1540][j], 300, [ORA, MAG, ORA, MAG][j], t, 5 + j)
        c = c * (1 - e) + bg * e
        c = framed(c, fill, shape_mask(kind, cx, cy, size), border=int(4 + 8 * e))
    sticker(c, label, W / 2, 400, t, T['ready'] + j * SHOT_LEN + M0 + 0.15, fill=[MAG, ORA, MAG, ORA][j],
            rot=[-5, 4, -4, 5][j], size=32 if len(label) > 22 else 36)
    stamp_check(c, 880, 1420, t, T['ready'] + j * SHOT_LEN + 1.25)
    s = word_spr(time_at(t), PK, 50, BLACK)                 # running clock + 4-step progress
    bw = s.shape[1] + 50
    draw(c, rrect_spr(bw, 86, 43, (1, 1, 1, 1)), 70 + bw / 2, 180)
    draw(c, s, 70 + bw / 2, 182)
    for q in range(4):
        on = t >= T['ready'] + SHOT_LEN * q + 1.25
        draw(c, rrect_spr(28, 28, 14, GRN if on else (0.82, 0.78, 0.74, 1)), 830 + q * 50, 180)
    return c


# ------------------------------------------------------------------ scenes
def sc_hook(t):
    if t < SW_END:
        c = full3d('switch', t * 24)
        k = prog(t, 0.05, 0.4) * (1 - prog(t, SW_FLIP, SW_FLIP + 0.2))
        if k > 0:
            draw(c, word_spr('9:47 PM', PK, 64, (1, 1, 1, 1)), W / 2, 330, opacity=0.9 * k)
        return c
    c = paper().copy()
    c = blob(c, 870, 330, 270 * e_out_back(prog(t, SW_END, SW_END + 0.5), 1.6), ORA, t, 1)
    c = blob(c, 170, 1600, 230 * e_out_back(prog(t, SW_END + 0.15, SW_END + 0.65), 1.6), MAG, t, 2)
    kk = e_out_back(prog(t, SW_END + 0.15, SW_END + 0.65), 1.5)
    if kk > 0.01:
        z = 1.12 - 0.08 * prog(t, SW_END, T['call'])
        fill = warm(fill_box('hero-family.webp', 600, 1270, 900, 900, z, 0.66, 0.5), 0.12)
        g = m_circle(640, 1090, 200, soft=220)[..., None] * 0.3 * prog(t, SW_END + 0.5, SW_END + 1.2)
        fill = fill + g * np.array([1.0, 0.7, 0.35], np.float32)       # the porch glow warms the photo
        c = framed(c, fill, m_circle(600, 1270, 410 * kk))
    c = stamp_text(c, 'Could you', 70, 300, 120, BLACK, t, SW_END + 0.05)
    c = stamp_text(c, 'leave the', 70, 440, 120, MAG, t, SW_END + 0.25)
    c = stamp_text(c, 'light on?', 70, 580, 132, ORA, t, SW_END + 0.45)
    c = brush(c, 80, 700, 520, prog(t, SW_END + 0.7, SW_END + 1.2))
    c = dot(c, 120, 960, 22, ORA, prog(t, SW_END + 0.9, SW_END + 1.2))
    c = dot(c, 200, 1030, 44, GRN, prog(t, SW_END + 1.0, SW_END + 1.35))
    c = dot(c, 960, 860, 30, MAG, prog(t, SW_END + 1.1, SW_END + 1.4))
    return c


def light_burst(prev, nxt, p):
    """The switch's warm light blooms out into the poster world."""
    r = e_in_cubic(clamp(p)) * 1500 + 1
    m = m_circle(W / 2, 980, r, soft=60)[..., None]
    glow = m_circle(W / 2, 980, r * 0.9 + 80, soft=260)[..., None] * (1 - p)
    return prev * (1 - m) + nxt * m + glow * np.array([1.0, 0.75, 0.45], np.float32) * 0.8


def sc_call(t):
    t0 = T['call']
    c = paper().copy()
    c = blob(c, 920, 1560, 320, MAG, t, 3)
    c = blob(c, 110, 420, 170, ORA, t, 4)
    k = prog(t, t0 + 0.05, t0 + 0.55)                       # 3D flip-card clock 9:47
    if k > 0:
        s = word_spr('9:47', PK, 170, BLACK)
        spr = rrect_spr(s.shape[1] + 80, 230, 30, (1, 1, 1, 1)).copy()
        paste(spr, s, spr.shape[1] / 2, 122)
        ang = (1 - e_out_back(k, 1.6)) * 90
        draw(c, blur_sprite(tint(spr, (0.3, 0.12, 0.05)), 14), 70 + spr.shape[1] / 2 + 10, 348, opacity=0.3 * k)
        draw3d(c, spr, 70 + spr.shape[1] / 2, 330, 0, spr.shape[1], None, rx=ang)
    c = stamp_text(c, 'PM', 500, 330, 80, MAG, t, t0 + 0.4)
    c = stamp_text(c, 'A child needs', 70, 560, 66, BLACK, t, t0 + 0.6, fname=PX)
    c = stamp_text(c, 'somewhere safe', 70, 648, 66, BLACK, t, t0 + 0.8, fname=PX)
    c = stamp_text(c, 'tonight.', 70, 750, 96, ORA, t, VO['call'] + 3.5)
    kp = e_out_cubic(prog(t, t0 + 0.2, t0 + 0.8))
    rz = 3 * math.sin(t * 40) * (1 - prog(t, ANSWER - 0.2, ANSWER)) if t < ANSWER else 0
    body = phone_body().copy()
    paste(body, call_screen(t) * screen_mask(), PW / 2, PH / 2)
    paste(body, rrect_spr(150, 40, 20, (0, 0, 0, 1)), PW / 2, 62)
    draw_phone(c, body, lerp(1300, 760, kp), 1290, 470, 8, -22 + 10 * kp, 8 + rz)
    sticker(c, 'EMERGENCY FOSTERING', 300, 1010, t, t0 + 1.2, fill=GRN, ink=BLACK, rot=-5)
    captions(c, t, 'call')
    return c


def sc_ready(t):
    t0 = T['ready']
    j = min(int((t - t0) / SHOT_LEN), 3)
    lt = t - t0 - j * SHOT_LEN
    c = ready_shot(t, j, lt)
    if j > 0 and lt < TR:
        prev = ready_shot(t, j - 1, SHOT_LEN - 0.01)
        c = [None, split_slide, card_flip, lambda a, b, q: blob_wipe(a, b, q, MAG)][j](prev, c, lt / TR)
    captions(c, t, 'ready')
    return c


def sc_arrive(t):
    t0 = T['arrive']
    k = e_inout_cubic(prog(t, t0 - 0.5, T['payoff']))
    c = warm(kb('05-emergency-a-calm-welcome.webp', W, H, 1.14 - 0.08 * k, 0.5 - 0.04 * k, 0.48), 0.18)
    c = c + m_circle(250, 500, 300, soft=400)[..., None] * np.array([1.0, 0.65, 0.3], np.float32) * 0.18
    vig = np.clip(((_X / W - 0.5) ** 2 * 1.2 + (_Y / H - 0.5) ** 2 * 1.6), 0, 1)[..., None]
    c = c * (1 - vig * 0.9)
    kh = prog(t, t0 + 0.35, t0 + 1.7)                     # neon heart draws itself round the welcome
    if kh > 0:
        p = heart_poly() * 470 + np.array([560, 960], np.float32)
        n = int(len(p) * kh)
        line = np.zeros((H, W), np.float32)
        cv2.polylines(line, [p[:max(2, n)].astype(np.int32)], False, 1.0, 8, cv2.LINE_AA)
        g = cv2.GaussianBlur(line, (0, 0), 12) * 1.8 + line
        c = c + g[..., None] * np.array([1.0, 0.3, 0.6], np.float32) * 0.7
    for j, (line_, ts, x, y, fill, ink) in enumerate([("You're safe here.", t0 + 0.6, 600, 1480, (1, 1, 1, 0.97), BLACK),
                                                      ('Fancy some toast?', t0 + 1.5, 520, 1610, ORA, WHITE_)]):
        kk = prog(t, ts, ts + 0.35)
        if kk > 0:
            p_ = pill(line_, PX, 46, pad_x=34, pad_y=20, fill=fill, border=None, text_color=ink)
            draw(c, blur_sprite(tint(p_, (0, 0, 0)), 10), x + 6, y + 10, opacity=0.35 * kk)
            draw(c, p_, x, y, scale=e_out_back(kk, 2.4), rot=-3 + 6 * j, opacity=min(1, kk * 3))
    return c


def sc_payoff(t):
    t0 = T['payoff']
    c = paper().copy()
    c = blob(c, 1010, 1060, 230, ORA, t, 9)
    c = blob(c, 140, 1700, 260, MAG, t, 10)
    ks = e_inout_cubic(prog(t, VO['never'] + 2.7, VO['never'] + 3.4))     # house slides aside for the 2nd photo
    k = e_out_back(prog(t, t0, t0 + 0.6), 1.4)
    draw(c, sprite_at('house', house_frame(t)), lerp(540, 300, ks), lerp(1150, 1230, ks),
         scale=lerp(1.2, 0.8, ks) * (0.7 + 0.3 * k), opacity=min(1, k * 2))
    c = stamp_text(c, 'Ready when', 70, 250, 104, BLACK, t, t0 + 0.2)
    c = stamp_text(c, 'it matters.', 70, 375, 112, ORA, t, t0 + 0.45)
    c = brush(c, 80, 470, 460, prog(t, t0 + 0.7, t0 + 1.2))
    c = polaroid(c, 'adviser-conversation.webp', 0.45, 0.5, 800, 740, 360, 280, 'Advice, day or night', t,
                 VO['never'] + 0.7, rot=6)
    sticker(c, 'ADVICE OUTSIDE NORMAL HOURS', 540, 560, t, VO['never'] + 1.0, fill=MAG, rot=-4, size=30)
    c = polaroid(c, 'balanced-home-outdoors-2026-09-23.webp', 0.45, 0.5, 760, 1330, 420, 320, 'Never on your own', t,
                 VO['never'] + 3.0, rot=-5)
    captions(c, t, 'never', y=1820, size=42)
    return c


def sc_rise(t):
    t0 = T['rise']
    k = prog(t, t0, T['end'] + 0.3)
    c = warm(kb('hero-children-sunset-2026-09-21.jpg', W, H, 1.3 - 0.22 * e_out_cubic(k), 0.52, 0.55), 0.05)
    top = np.clip(1 - _Y / 1050, 0, 1)[..., None] ** 1.2
    c = c * (1 - 0.72 * top)
    c = stamp_text(c, 'Could you', 80, 330, 112, WHITE_, t, VO['cta'] + 0.05, glow=ORA)
    c = stamp_text(c, 'leave the', 80, 460, 112, WHITE_, t, VO['cta'] + 0.35, glow=MAG)
    c = stamp_text(c, 'light on?', 80, 600, 124, WHITE_, t, VO['cta'] + 0.65, glow=ORA)
    sw = prog(t, t0 + 1.2, t0 + 2.4)                     # one warm light sweep across the sky
    if 0 < sw < 1:
        band = np.exp(-((_X - lerp(-300, W + 300, sw) + (_Y - 500) * 0.4) / 120) ** 2)[..., None]
        c = c + band * top * np.array([1.0, 0.8, 0.5], np.float32) * 0.25
    captions(c, t, 'cta', y=1720, size=44)
    return c


def sc_end(t):
    t0 = T['end']
    c = paper().copy()
    c = blob(c, 1010, 640, 210, ORA, t, 11)
    c = blob(c, 110, 1720, 250, MAG, t, 12)
    lg = fitted('logo', png('logo_full'), width=600)
    kl = prog(t, t0, t0 + 0.45)
    draw(c, lg, 360, 220, scale=0.88 + 0.12 * e_out_back(kl, 1.8), opacity=min(1, kl * 2))
    c = stamp_text(c, 'Could you', 70, 470, 100, BLACK, t, t0 + 0.1)
    c = stamp_text(c, 'leave the', 70, 585, 100, MAG, t, t0 + 0.22)
    c = stamp_text(c, 'light on?', 70, 705, 112, ORA, t, t0 + 0.34)
    c = brush(c, 80, 800, 440, prog(t, t0 + 0.5, t0 + 0.95))
    ka = e_out_back(prog(t, t0 + 0.25, t0 + 0.75), 1.4)     # real photo in an arch card...
    if ka > 0.01:
        aw, ah = 430 * ka, 600 * ka
        fill = warm(fill_box('01-hero-cultural-belonging.webp', 790, 1210, aw * 1.3, ah, 1.05, 0.42, 0.5), 0.08)
        c = framed(c, fill, m_arch(790, 1210, aw, ah), border=12)
    kh = e_out_back(prog(t, t0 + 0.6, t0 + 1.1), 1.8)      # ...with the glossy 3D heart over its corner
    if kh > 0.01:
        draw(c, sprite_at('heart', ((t - t0) * 16) % max(1, len(files('heart')) - 1)), 610, 1480, scale=0.95 * kh)
    kb_ = prog(t, t0 + 0.8, t0 + 1.2)
    if kb_ > 0:
        p = pill('Start the conversation', PK, 38, pad_x=38, pad_y=20, fill=MAG, border=None, text_color=WHITE_)
        draw(c, blur_sprite(tint(p, (0.3, 0, 0.1)), 12), 70 + p.shape[1] / 2 + 6, 972, opacity=0.4 * kb_)
        draw(c, p, 70 + p.shape[1] / 2, 960, scale=e_out_back(kb_, 2.2), opacity=min(1, kb_ * 3))
    ki = prog(t, t0 + 1.0, t0 + 1.4)
    if ki > 0:
        for j, (line_, sz, col, fn) in enumerate([('0161 241 1332', 54, BLACK, PK), ('organicfostering.co.uk', 34, MAG, PB)]):
            s = word_spr(line_, fn, sz, col)
            draw(c, s, 80 + s.shape[1] / 2, 1100 + j * 70, opacity=ki)
    ko = prog(t, t0 + 1.2, t0 + 1.6)
    if ko > 0:
        p = pill('Rated Good by Ofsted', PB, 26, pad_x=24, pad_y=12, fill=GRN, border=None, text_color=BLACK)
        draw(c, p, 80 + p.shape[1] / 2, 1250, scale=e_out_back(ko, 2.2), opacity=min(1, ko * 3))
    ks = prog(t, t0 + 1.3, t0 + 1.7)
    if ks > 0:
        s = word_spr('Illustrative story. Photography: organicfostering.co.uk', PM, 22, (0.4, 0.35, 0.35, 1))
        draw(c, s, W / 2, 1855, opacity=ks)
    return c


# ------------------------------------------------------------------ transitions
def blob_wipe(prev, nxt, p, col=ORA):
    """Organic colour blob floods the frame, then the next scene grows out of it."""
    r1 = e_inout_cubic(clamp(p * 1.5)) * 1700
    r2 = e_inout_cubic(clamp(p * 1.5 - 0.45)) * 1700
    out = blob(prev, 180, 1720, r1, col, p * 3, 21)
    if r2 > 2:
        m = np.zeros((H, W), np.uint8)
        pts = [(180 + r2 * (1 + 0.05 * math.sin(4 * a)) * math.cos(a), 1720 + r2 * (1 + 0.05 * math.sin(4 * a)) * math.sin(a))
               for a in np.linspace(0, 2 * math.pi, 90)]
        cv2.fillPoly(m, [(np.clip(np.array(pts), -4000, 6000) * 4).astype(np.int32)], 255, cv2.LINE_AA, shift=2)
        m = (m.astype(np.float32) / 255.0)[..., None]
        out = out * (1 - m) + nxt * m
    return out


def heart_iris(prev, nxt, p):
    s = e_in_cubic(clamp(p)) * 3400 + 1
    m = m_heart(W / 2, H / 2, s)
    ring = np.clip(cv2.dilate(m, np.ones((17, 17), np.uint8)) - m, 0, 1)
    ring = cv2.GaussianBlur(ring, (0, 0), 3)[..., None] * (1 - clamp(p))
    m = m[..., None]
    return prev * (1 - m) + nxt * m + ring * np.array(PINKN[:3], np.float32)


def split_slide(prev, nxt, p):
    e = e_inout_cubic(clamp(p))
    out = nxt.copy()
    off = int(W * e)
    if off < W:
        out[:H // 2, :W - off] = prev[:H // 2, off:]
        out[H // 2:, off:] = prev[H // 2:, :W - off]
    if 0 < e < 1:
        out[H // 2 - 5:H // 2 + 5] = np.array(ORA[:3], np.float32)
    return out


def card_flip(prev, nxt, p):
    e = e_inout_cubic(clamp(p))
    out = (paper() * 0.8).copy()
    a = 180 * e
    spr = np.concatenate([prev if a < 90 else nxt, np.ones((H, W, 1), np.float32)], 2)
    ry = a if a < 90 else a - 180
    draw3d(out, spr, W / 2, H / 2, 420 * math.sin(math.radians(a)), W, H, ry=ry)
    return out


@functools.lru_cache(maxsize=30)
def home_layers(i):
    """3D HOME frame i: premultiplied colour, alpha, and the O's counter (transparent, not touching the frame edge)."""
    fs = files('home_text')
    if not fs:
        return None
    im = cv2.imread(fs[min(i, len(fs) - 1)], cv2.IMREAD_UNCHANGED)
    im = cv2.resize(im, (W, H), interpolation=cv2.INTER_CUBIC)
    a = im[..., 3].astype(np.float32) / 255.0
    rgb = im[..., :3][..., ::-1].astype(np.float32) / 255.0
    clear = (a < 0.5).astype(np.uint8)
    n, lab = cv2.connectedComponents(clear)
    edge = set(np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]])).tolist())
    hole = np.isin(lab, [q for q in range(1, n) if q not in edge]).astype(np.float32)
    if i >= len(fs) - 2:
        hole = 1 - a
    hole = np.minimum(cv2.GaussianBlur(hole, (0, 0), 1.5), 1 - a)
    return rgb * a[..., None], a, hole


def home_fly(t):
    """Outside the letters: the last ready shot; letters: 3D HOME; through the O: the arrival."""
    i = int(clamp((t - HOME0) * 24, 0, 23))
    L = home_layers(i)
    nxt = sc_arrive(t)
    if L is None:
        return nxt
    rgb, a, hole = L
    ys, xs = np.where(hole > 0.5)
    if len(xs) > 50 and hole.mean() < 0.9:          # portal: the whole arrival picture sits inside the O and grows
        hx, hy = (xs.min() + xs.max()) / 2, (ys.min() + ys.max()) / 2
        f = clamp(max((xs.max() - xs.min()) / W, (ys.max() - ys.min()) / H) * 1.25, 0.05, 1.0)
        M = np.float32([[f, 0, hx - f * W / 2], [0, f, hy - f * H / 2]])
        nxt = cv2.warpAffine(nxt, M, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
    prev = sc_ready(min(t, T['arrive'] - 0.01))
    k = prog(t, HOME0, HOME0 + 0.15)
    outside = np.clip(1 - a - hole, 0, 1)[..., None]
    out = prev * outside + rgb + nxt * hole[..., None]
    return prev * (1 - k) + out * k


SCENES = [(T['hook'], T['call'], sc_hook), (T['call'], T['ready'], sc_call), (T['ready'], T['arrive'], sc_ready),
          (T['arrive'], T['payoff'], sc_arrive), (T['payoff'], T['rise'], sc_payoff), (T['rise'], T['end'], sc_rise),
          (T['end'], 99, sc_end)]
TRANS = {SW_END: (light_burst, 0.4), T['call']: (lambda a, b, p: blob_wipe(a, b, p, ORA), TR),
         T['ready']: (heart_iris, 0.5), T['payoff']: (split_slide, TR), T['rise']: (card_flip, 0.55),
         T['end']: (lambda a, b, p: blob_wipe(a, b, p, MAG), TR)}


def scene_at(t):
    for a, b, f in SCENES:
        if a <= t < b:
            return f
    return SCENES[-1][2]


def render_raw(t):
    if HOME0 <= t < HOME1:
        c = home_fly(t)
    else:
        c = scene_at(t)(t)
        for tc, (fn, dur) in TRANS.items():
            d = t - tc
            if 0 <= d < dur:
                c = fn(scene_at(tc - 0.01)(tc - 0.01), c, d / dur)
    dx = dy = 0.0
    for tc in [SW_FLIP, ANSWER]:
        sx, sy = shake(t, tc, amp=8, dur=0.3)
        dx += sx
        dy += sy
    if abs(dx) + abs(dy) > 0.5:
        c = cv2.warpAffine(c, np.float32([[1, 0, dx], [0, 1, dy]]), (W, H), borderMode=cv2.BORDER_REFLECT)
    if t > DUR - FADE:
        c = c * (1 - 0.88 * e_inout_cubic(prog(t, DUR - FADE, DUR)))
    return c


def is_fast(t):
    if any(0 <= t - tc < dur for tc, (_, dur) in TRANS.items()) or HOME0 + 0.3 <= t < HOME1:
        return True
    if T['ready'] <= t < T['arrive']:
        lt = (t - T['ready']) % SHOT_LEN
        return lt < TR or Z0 + 0.15 < lt < M0 + 0.2
    return False


def render(fi):
    t = fi / FPS
    if is_fast(t):
        acc = None
        for k in range(3):
            r = render_raw(max(0.0, t + (k / 3 - 0.33) * 0.5 / FPS))
            acc = r if acc is None else acc + r
        c = acc / 3
    else:
        c = render_raw(t)
    dark = t < SW_END
    return post(c, fi, bloom=0.3 if dark else 0.08, grain=0.016, vig=1.0 if dark else 0.25)


def to_u8(im):
    return (np.clip(im, 0, 1) * 255 + 0.5).astype(np.uint8)[..., ::-1]


if __name__ == '__main__':
    mode = sys.argv[1]
    if mode == 'still':
        os.makedirs(f'{S}/stills', exist_ok=True)
        for ts in sys.argv[2].split(','):
            t = float(ts)
            cv2.imwrite(f'{S}/stills/s_{t:05.2f}.jpg', to_u8(render(int(round(t * FPS)))), [cv2.IMWRITE_JPEG_QUALITY, 90])
            print('still', t, flush=True)
    elif mode == 'range':
        a, b = int(sys.argv[2]), int(sys.argv[3])
        os.makedirs(f'{S}/frames_out', exist_ok=True)
        for fi in range(a, b):
            if os.environ.get('RESUME') and os.path.exists(f'{S}/frames_out/{fi:04d}.png'):
                continue
            cv2.imwrite(f'{S}/frames_out/{fi:04d}.png', to_u8(render(fi)), [cv2.IMWRITE_PNG_COMPRESSION, 1])
            print('frame', fi, flush=True)
