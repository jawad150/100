"""IC London — "Why do you want to be a solicitor?" (9:16, 36 s). Concept: build your answer like a landmark.

The IC London emblem is a tower of three pieces. Here they are the three parts of a strong answer, drawn as a blueprint
and built in 3D: the red block whose white circle is a target (motivation), the navy foundation laid course by course
(experience) and the navy spire pointing up a rising career path (long-term goals). They snap into the emblem for the
CTA. Hook: an interview chat where "I love law." is copied by everyone, stamped TOO GENERIC and falls away.
Transitions are built from the emblem's own shapes: circle iris, navy-base wipe, spire-triangle wipe, red-square zoom.

Usage: python3 reel_sol.py still 1.0,5.0   |   python3 reel_sol.py range 0 1080
"""
import os, sys, math, json, glob, functools
HERE = os.path.dirname(os.path.abspath(__file__))
os.environ['REEL_WORKDIR'] = os.path.abspath(os.path.join(HERE, '..', 'workspace_sol'))
sys.path.insert(0, os.path.join(HERE, '..', 'pipeline'))
import numpy as np
import cv2
from engine import *  # noqa: F401,F403
import engine as E

S = E.S
FPS = 30
DUR = 36.0
NF = int(DUR * FPS)
FADE = 1.1

NAVY = hexc('#00247D')
NAVY_D = hexc('#041640')
NAVY_M = hexc('#0B2C8F')
RED = hexc('#CF142B')
RED_L = hexc('#FF4D5E')                  # brighter red for text on photos
WHITE_ = (1.0, 1.0, 1.0, 1.0)
ICE = hexc('#EEF2FB')
INK = hexc('#0A1A4A')
LINE = (0.78, 0.86, 1.0, 1.0)            # blueprint line colour
GREY = hexc('#9AA6C8')
F9, F8, F7, F6, F5 = 'Inter-900', 'Inter-800', 'Inter-700', 'Inter-600', 'Inter-500'

# ------------------------------------------------------------------ voiceover timing (from the generated lines)
INFO = json.load(open(f'{S}/tts/lines/info.json'))
ORDER = ['hook', 'generic', 'three', 'motiv', 'exp', 'goals', 'cta']
VO = {}
_t = 0.2
for _k in ORDER:
    VO[_k] = round(_t, 3)
    _t += INFO['dur'][_k] + 0.08
PH = {k: [(VO[k] + o, txt) for o, txt in INFO['phrases'][k]] for k in ORDER}


def ph(k, i):
    return PH[k][i][0]


T = dict(hook=0.0, generic=4.75, three=8.15, motiv=11.2, exp=16.1, goals=23.9, cta=31.0)
_Y, _X = np.mgrid[0:H, 0:W].astype(np.float32)


# ------------------------------------------------------------------ small helpers
def ts(text, font, size, col=WHITE_, trk=0.0):
    return text_sprite(text, font, size, col, trk)


@functools.lru_cache(maxsize=512)
def _wmask(text, font_, size):
    from PIL import Image, ImageDraw
    f = E.font(font_, size)
    asc, desc = f.getmetrics()
    w = int(math.ceil(f.getlength(text))) + 12
    im = Image.new('L', (w, asc + desc + 12), 0)
    ImageDraw.Draw(im).text((6, 6), text, font=f, fill=255)
    return np.asarray(im, np.float32) / 255.0


def wspr(text, font_, size, col=WHITE_):
    """Word sprite on a fixed ascent+descent box, so words in a line share one baseline."""
    return solid(_wmask(text, font_, size), col)


def rrect(w, h, r, fill):
    return solid(sdf_fill(rrect_alpha(int(w), int(h), r, 2)), fill)


def shadow(c, spr, x, y, op=0.35, sig=18, dy=14, col=(0.0, 0.03, 0.12)):
    draw(c, blur_sprite(tint(spr, col), sig), x, y + dy, opacity=op)


def kin(c, words, x, y, size, t, t0, font=F9, stagger=0.07, dur=0.42, align='left', lh=1.12):
    """Kinetic headline: words rise into place one by one. words = list of lines, each a list of (word, colour)."""
    for li, line in enumerate(words):
        sprs = [wspr(w, font, size, col) for w, col in line]
        sp = size * 0.13
        total = sum(s.shape[1] for s in sprs) + sp * (len(sprs) - 1)
        xx = x if align == 'left' else x - total / 2
        yy = y + li * size * lh
        for wi, s in enumerate(sprs):
            k = prog(t, t0 + (li * len(line) + wi) * stagger, t0 + (li * len(line) + wi) * stagger + dur)
            if k > 0:
                e = e_out_cubic(k)
                draw(c, s, xx + s.shape[1] / 2, yy + (1 - e) * size * 0.55, opacity=min(1, k * 1.8))
            xx += s.shape[1] + sp


def chip(c, text, x, y, t, t0, fill=RED, ink=WHITE_, size=28, dot=False):
    k = prog(t, t0, t0 + 0.3)
    if k <= 0:
        return
    s = ts(text, F8, size, ink, 0.12)
    w, h = s.shape[1] + 48 + (26 if dot else 0), s.shape[0] + 22
    p = rrect(w, h, h / 2, fill)
    sc = e_out_back(k, 2.2)
    draw(c, p, x + w / 2, y, scale=sc, opacity=min(1, k * 3))
    if dot:
        draw(c, rrect(14, 14, 7, WHITE_), x + 30, y, scale=sc, opacity=min(1, k * 3) * (0.6 + 0.4 * math.sin(t * 6)))
    draw(c, s, x + w / 2 + (13 if dot else 0), y, scale=sc, opacity=min(1, k * 3))


def section_head(c, t, num, title, sub_t, title_t, accent=RED):
    """'01' outline numeral + chip + big title."""
    k = prog(t, sub_t, sub_t + 0.35)
    if k > 0:
        n = ts(num, F9, 220, (1, 1, 1, 0.0))
        m = text_mask(num, F9, 220)
        edge = cv2.morphologyEx((m > 0.5).astype(np.uint8), cv2.MORPH_GRADIENT, np.ones((5, 5), np.uint8)).astype(np.float32)
        ring = solid(edge, accent)
        draw(c, pad(ring, 3), 80 + ring.shape[1] / 2, 330 + (1 - e_out_cubic(k)) * 60, opacity=k)
    kin(c, [[(title, WHITE_)]], 80, 520, 84, t, title_t, stagger=0.0, dur=0.45)
    title_sweep(c, title, 80, 520, 84, t, title_t + 0.45)


def title_sweep(c, title, x, y, size, t, t0, font_=F9, dur=0.55):
    """A glossy light band runs across a headline once it has landed."""
    k = prog(t, t0, t0 + dur)
    if k <= 0 or k >= 1:
        return
    m = _wmask(title, font_, size)
    h, w = m.shape
    xs = np.arange(w, dtype=np.float32)[None, :] + np.arange(h, dtype=np.float32)[:, None] * 0.35
    band = np.exp(-((xs - lerp(-0.2 * w, 1.2 * w, k)) / (0.07 * w + 20)) ** 2)
    draw(c, solid(m * band, WHITE_), x + w / 2, y, opacity=0.9, mode='add')


@functools.lru_cache(maxsize=1)
def grid_layer():
    g = np.zeros((H + 200, W + 200), np.float32)
    for x in range(0, W + 200, 40):
        g[:, x] = 0.05 if x % 200 else 0.12
    for y in range(0, H + 200, 40):
        g[y, :] = np.maximum(g[y, :], 0.05 if y % 200 else 0.12)
    return g


@functools.lru_cache(maxsize=1)
def bg_base():
    top = np.array(hexc('#0A2468')[:3], np.float32)
    bot = np.array(hexc('#020A26')[:3], np.float32)
    k = (_Y / H)[..., None]
    c = top * (1 - k) + bot * k
    v = np.clip(((_X / W - 0.5) ** 2 + (_Y / H - 0.45) ** 2) * 1.6, 0, 1)[..., None]
    return c * (1 - 0.5 * v)


@functools.lru_cache(maxsize=1)
def dust_layer():
    rng = np.random.default_rng(11)
    d = np.zeros((H + 600, W), np.float32)
    for _ in range(70):
        x, y, r = rng.uniform(0, W), rng.uniform(0, H + 600), rng.uniform(1.5, 5.5)
        cv2.circle(d, (int(x), int(y)), int(r), rng.uniform(0.25, 0.9), -1, cv2.LINE_AA)
    return cv2.GaussianBlur(d, (0, 0), 2.2)


def dust(t, amt=0.35):
    o = int((t * 45) % 600)
    return dust_layer()[600 - o:600 - o + H][..., None] * amt * np.array(LINE[:3], np.float32)


def bg(t, grid=1.0):
    c = bg_base().copy() + dust(t)
    if grid > 0:
        o = int(t * 10) % 200
        g = grid_layer()[o:o + H, o:o + W][..., None] * grid
        c = c + g * np.array(LINE[:3], np.float32) * 0.9
    return c


def scanline(c, y, strength=0.6):
    band = np.exp(-((_Y - y) / 6) ** 2)[..., None]
    glow = np.exp(-((_Y - y) / 60) ** 2)[..., None]
    return c + (band * 0.8 + glow * 0.25) * np.array(LINE[:3], np.float32) * strength


# ------------------------------------------------------------------ the client's reference photos
@functools.lru_cache(maxsize=8)
def photo(name):
    return cv2.imread(f'{S}/src/{name}.png')[..., ::-1].astype(np.float32) / 255.0


def kb(name, w, h, z=1.0, fx=0.5, fy=0.5):
    """Cover-crop a photo into w x h, zoomed by z around the focal point (fx, fy)."""
    im = photo(name)
    ih, iw = im.shape[:2]
    sc = max(w / iw, h / ih) * z
    cw, ch = w / sc, h / sc
    x0 = clamp(fx * iw - cw / 2, 0, iw - cw)
    y0 = clamp(fy * ih - ch / 2, 0, ih - ch)
    M = np.float32([[sc, 0, -x0 * sc], [0, sc, -y0 * sc]])
    return cv2.warpAffine(im, M, (int(w), int(h)), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)


def photo_bg(name, t, t0, dur, fx=0.5, fy=0.5, z0=1.12, z1=1.0, keep=0.55, top=0.0, bot=0.0):
    """Full-bleed photo with a slow push, graded into the brand navy (keep = how much photo shows through)."""
    k = clamp((t - t0) / dur)
    im = kb(name, W, H, lerp(z0, z1, e_inout_cubic(k)), fx, fy)
    navy = np.array(hexc('#041640')[:3], np.float32)
    lum = im.mean(2, keepdims=True)
    im = im * 0.85 + lum * 0.15
    im = im * keep + navy * (1 - keep)
    if top:
        g = np.clip(1 - _Y / (H * top), 0, 1)[..., None] ** 1.3
        im = im * (1 - 0.85 * g) + navy * 0.85 * g
    if bot:
        g = np.clip((_Y - H * (1 - bot)) / (H * bot), 0, 1)[..., None] ** 1.3
        im = im * (1 - 0.85 * g) + navy * 0.85 * g
    return im


# ------------------------------------------------------------------ 3D sequences (Blender, 24 fps, RGBA)
_files = {}


def files(name):
    if not _files.get(name):
        _files[name] = sorted(glob.glob(f'{S}/assets/{name}/*.png'))
    return _files[name]


@functools.lru_cache(maxsize=64)
def spr3(name, i):
    fs = files(name)
    return load_png_sprite(fs[max(0, min(i, len(fs) - 1))]) if fs else np.zeros((8, 8, 4), np.float32)


def seq_at(name, tl, loop=False, fps=24):
    n = max(1, len(files(name)))
    f = tl * fps
    return spr3(name, int(f) % n if loop else int(clamp(f, 0, n - 1)))


TOWER_DY = {'pieces_float': 170, 'emblem_build': 150}
TOWER_DX = {'emblem_build': -230, 'pieces_float': -90}


def shift_down(im, dy):
    if not dy:
        return im
    out = np.zeros_like(im)
    out[dy:] = im[:-dy]
    return out


@functools.lru_cache(maxsize=4)
def full_rgba(name, i):
    """A 720x1280 render scaled to the full 1080x1920 frame: (premultiplied rgb, alpha)."""
    fs = files(name)
    if not fs:
        return np.zeros((H, W, 3), np.float32), np.zeros((H, W), np.float32)
    im = cv2.imread(fs[max(0, min(i, len(fs) - 1))], cv2.IMREAD_UNCHANGED)
    im = cv2.resize(im, (W, H), interpolation=cv2.INTER_CUBIC).astype(np.float32) / 255.0
    im = shift_down(im, TOWER_DY.get(name, 0))
    dx = TOWER_DX.get(name, 0)
    if dx:
        im = np.roll(im, dx, 1)
        im[:, dx:] = 0
    a = im[..., 3]
    return im[..., :3][..., ::-1] * a[..., None], a


def over_full(c, name, tl, op=1.0, fps=24):
    n = max(1, len(files(name)))
    rgb, a = full_rgba(name, int(clamp(tl * fps, 0, n - 1)))
    return c * (1 - a[..., None] * op) + rgb * op


@functools.lru_cache(maxsize=1)
def tower_geo():
    """Blueprint line art + piece boxes + circle centre, from the last pieces_float frame."""
    fs = files('pieces_float')
    if not fs:
        return None
    im = cv2.imread(fs[-1], cv2.IMREAD_UNCHANGED)
    im = shift_down(cv2.resize(im, (W, H), interpolation=cv2.INTER_CUBIC), TOWER_DY['pieces_float'])
    im = np.roll(im, TOWER_DX['pieces_float'], 1)
    im[:, TOWER_DX['pieces_float']:] = 0
    a = im[..., 3]
    b, g, r = [im[..., i].astype(int) for i in range(3)]
    solidm = a > 140
    edges = cv2.Canny((solidm * 255).astype(np.uint8), 50, 150)
    inner = cv2.Canny(cv2.GaussianBlur(cv2.cvtColor(im[..., :3], cv2.COLOR_BGR2GRAY), (5, 5), 0), 40, 110) * solidm
    art = np.clip(edges.astype(np.float32) / 255 + inner.astype(np.float32) / 255 * 0.6, 0, 1)
    art = cv2.dilate(art, np.ones((2, 2), np.uint8))
    red = solidm & (r > g + 70) & (r > b + 40)
    white = solidm & (r > 170) & (g > 170) & (b > 170)
    ys, xs = np.where(red)
    rb = (xs.min(), ys.min(), xs.max(), ys.max())
    navy = solidm & ~red & ~white
    ys2, xs2 = np.where(navy & (_Y < rb[1] - 10))
    sb = (xs2.min(), ys2.min(), xs2.max(), ys2.max())
    ys3, xs3 = np.where(navy & (_Y > rb[3] + 10))
    bb = (xs3.min(), ys3.min(), xs3.max(), ys3.max())
    wy, wx = np.where(white)
    return dict(art=art, block=rb, spire=sb, base=bb, circle=(wx.mean(), wy.mean(), (wx.max() - wx.min()) / 2))


def blueprint(c, t, t0, t1, op=1.0):
    g = tower_geo()
    if g is None:
        return c
    k = prog(t, t0, t1)
    if k <= 0:
        return c
    yb = lerp(g['spire'][1] - 40, g['base'][3] + 40, e_inout_cubic(k))
    m = (_Y < yb).astype(np.float32) if k < 1 else 1.0
    art = g['art'] * m
    glow = cv2.GaussianBlur(art, (0, 0), 5) * 0.8
    c = c + (art + glow)[..., None] * np.array(LINE[:3], np.float32) * 0.75 * op
    if k < 1:
        c = scanline(c, yb, 0.5 * op)
    return c


def dim_line(c, x0, y0, x1, y1, k, col=LINE, label=None, lpos=None, t=0, lt0=0, size=25):
    if k <= 0:
        return c
    lay = np.zeros((H, W), np.uint8)
    xe, ye = lerp(x0, x1, k), lerp(y0, y1, k)
    cv2.line(lay, (int(x0 * 4), int(y0 * 4)), (int(xe * 4), int(ye * 4)), 255, 2 * 4, cv2.LINE_AA, shift=2)
    for (px, py) in [(x0, y0)] + ([(x1, y1)] if k >= 1 else []):
        cv2.circle(lay, (int(px * 4), int(py * 4)), 6 * 4, 255, -1, cv2.LINE_AA, shift=2)
    m = lay.astype(np.float32)[..., None] / 255
    c = c * (1 - m) + np.array(col[:3], np.float32) * m
    if label and k >= 1:
        kk = prog(t, lt0, lt0 + 0.3)
        if kk > 0:
            s = ts(label, F8, size, WHITE_, 0.14)
            draw(c, s, lpos[0] + s.shape[1] / 2, lpos[1] + (1 - e_out_cubic(kk)) * 16, opacity=kk)
    return c


def target_rings(c, cx, cy, r0, t, t0, col=WHITE_):
    if t < t0:
        return
    for j in range(3):
        ph_ = ((t - t0) * 0.7 + j / 3) % 1.0
        draw(c, ring_sprite(int(r0 * 6), r0 * (1 + 1.8 * ph_), 4, col, glow=6), cx, cy, opacity=0.55 * (1 - ph_))


def crosshair(c, cx, cy, r, k, col=LINE):
    if k <= 0:
        return c
    lay = np.zeros((H, W), np.uint8)
    L = r * 1.5 * e_out_cubic(k)
    for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
        cv2.line(lay, (int((cx + dx * r * 1.15) * 4), int((cy + dy * r * 1.15) * 4)),
                 (int((cx + dx * (r * 1.15 + L)) * 4), int((cy + dy * (r * 1.15 + L)) * 4)), 255, 8, cv2.LINE_AA, shift=2)
    m = lay.astype(np.float32)[..., None] / 255 * 0.8
    return c * (1 - m) + np.array(col[:3], np.float32) * m


def heart_spr(size, col):
    s = size * 3
    im = np.zeros((s, s), np.uint8)
    pts = []
    for i in range(80):
        a = i / 80 * 2 * math.pi
        x = 16 * math.sin(a) ** 3
        y = -(13 * math.cos(a) - 5 * math.cos(2 * a) - 2 * math.cos(3 * a) - math.cos(4 * a))
        pts.append((s / 2 + x / 17 * s * 0.46, s / 2 + (y + 2) / 17 * s * 0.46))
    cv2.fillPoly(im, [np.array(pts, np.int32)], 255, cv2.LINE_AA)
    a = cv2.resize(im, (size, size), interpolation=cv2.INTER_AREA).astype(np.float32) / 255
    return solid(a, col)


def check(size, fill=RED):
    s = size * 3
    d = np.zeros((s, s), np.uint8)
    cv2.circle(d, (s // 2, s // 2), s // 2 - 2, 255, -1, cv2.LINE_AA)
    tk = np.zeros((s, s), np.uint8)
    cv2.polylines(tk, [np.array([[s * 0.28, s * 0.52], [s * 0.44, s * 0.68], [s * 0.74, s * 0.36]], np.int32)], False, 255,
                  int(s * 0.11), cv2.LINE_AA)
    spr = over_spr(solid(d.astype(np.float32) / 255, fill), solid(tk.astype(np.float32) / 255, WHITE_))
    return cv2.resize(spr, (size, size), interpolation=cv2.INTER_AREA)


@functools.lru_cache(maxsize=4)
def icon(kind, size=64):
    """Small line icons in a red badge: target (motivation), document (experience), growth chart (goals)."""
    S4 = size * 4
    m = np.zeros((S4, S4), np.uint8)
    w = int(S4 * 0.06)
    if kind == 'target':
        for r in (0.36, 0.24, 0.1):
            cv2.circle(m, (S4 // 2, S4 // 2), int(S4 * r), 255, w if r > 0.1 else -1, cv2.LINE_AA)
    elif kind == 'doc':
        cv2.rectangle(m, (int(S4 * 0.28), int(S4 * 0.18)), (int(S4 * 0.72), int(S4 * 0.82)), 255, w, cv2.LINE_AA)
        for j in range(3):
            y = int(S4 * (0.36 + j * 0.14))
            cv2.line(m, (int(S4 * 0.37), y), (int(S4 * 0.63), y), 255, w, cv2.LINE_AA)
    else:
        for j, hgt in enumerate((0.18, 0.3, 0.44)):
            x = int(S4 * (0.26 + j * 0.18))
            cv2.rectangle(m, (x, int(S4 * (0.78 - hgt))), (x + int(S4 * 0.11), int(S4 * 0.78)), 255, -1)
        cv2.line(m, (int(S4 * 0.22), int(S4 * 0.52)), (int(S4 * 0.74), int(S4 * 0.22)), 255, w, cv2.LINE_AA)
    disc = np.zeros((S4, S4), np.uint8)
    cv2.circle(disc, (S4 // 2, S4 // 2), S4 // 2 - 4, 255, -1, cv2.LINE_AA)
    spr = over_spr(solid(disc.astype(np.float32) / 255, RED), solid(m.astype(np.float32) / 255, WHITE_))
    return cv2.resize(spr, (size, size), interpolation=cv2.INTER_AREA)


# ------------------------------------------------------------------ hook: the interview chat
CARD_X, CARD_Y, CARD_W, CARD_H = 540, 1490, 920, 600


def bubble(text, fill, ink, size=44, tail='left', heart=False):
    s = ts(text, F7, size, ink)
    w = s.shape[1] + 64 + (56 if heart else 0)
    h = s.shape[0] + 40
    b = rrect(w, h, 30, fill).copy()
    paste_spr(b, s, 32 + s.shape[1] / 2, h / 2)
    if heart:
        paste_spr(b, heart_spr(40, RED), w - 52, h / 2)
    return b


def paste_spr(dst, spr, cx, cy):
    h, w = spr.shape[:2]
    x0, y0 = int(cx - w / 2), int(cy - h / 2)
    x1, y1 = min(dst.shape[1], x0 + w), min(dst.shape[0], y0 + h)
    sx, sy = max(0, -x0), max(0, -y0)
    x0, y0 = max(0, x0), max(0, y0)
    a = spr[sy:sy + y1 - y0, sx:sx + x1 - x0, 3:4]
    dst[y0:y1, x0:x1] = dst[y0:y1, x0:x1] * (1 - a) + spr[sy:sy + y1 - y0, sx:sx + x1 - x0]


def typing(c, x, y, t, fill=(0.85, 0.89, 0.97, 1), dotc=GREY):
    draw(c, rrect(130, 70, 35, fill), x, y)
    for j in range(3):
        a = 0.4 + 0.6 * max(0, math.sin(t * 9 - j * 0.9))
        draw(c, rrect(16, 16, 8, dotc), x - 30 + j * 30, y - 6 * max(0, math.sin(t * 9 - j * 0.9)), opacity=a)


ANS = None


def answer_bubble():
    global ANS
    if ANS is None:
        ANS = bubble('I love law.', NAVY, WHITE_, 46, heart=True)
    return ANS


def chat_card(c, t):
    k = e_out_cubic(prog(t, 0.25, 0.85))
    if k <= 0:
        return
    y = lerp(H + 400, CARD_Y, k)
    card = rrect(CARD_W, CARD_H, 44, (1, 1, 1, 1))
    shadow(c, card, CARD_X, y, 0.45, 30, 30)
    draw(c, card, CARD_X, y)
    top = y - CARD_H / 2
    draw(c, rrect(CARD_W - 2, 2, 1, (0.9, 0.92, 0.97, 1)), CARD_X, top + 110)
    draw(c, rrect(64, 64, 32, NAVY), CARD_X - CARD_W / 2 + 70, top + 56)
    draw(c, ts('IP', F8, 26, WHITE_), CARD_X - CARD_W / 2 + 70, top + 56)
    draw(c, ts('Interview panel', F8, 32, INK), CARD_X - CARD_W / 2 + 120 + ts('Interview panel', F8, 32, INK).shape[1] / 2, top + 44)
    draw(c, ts('Training contract  ·  Round 2', F5, 24, GREY), CARD_X - CARD_W / 2 + 120 + ts('Training contract  ·  Round 2', F5, 24, GREY).shape[1] / 2, top + 76)
    draw(c, rrect(14, 14, 7, hexc('#22B35E')), CARD_X + CARD_W / 2 - 110, top + 56)
    draw(c, ts('LIVE', F8, 22, hexc('#22B35E'), 0.12), CARD_X + CARD_W / 2 - 70, top + 56)
    q = bubble('Why do you want to be a solicitor?', ICE, INK, 38)
    qx, qy = CARD_X - CARD_W / 2 + 40 + q.shape[1] / 2, top + 200
    if 0.75 <= t < 1.05:
        typing(c, CARD_X - CARD_W / 2 + 105, qy, t)
    kq = prog(t, 1.05, 1.3)
    if kq > 0:
        draw(c, q, qx, qy + (1 - e_out_back(kq, 2)) * 20, scale=0.9 + 0.1 * e_out_back(kq, 2), opacity=min(1, kq * 3))
    ax_, ay_ = CARD_X + CARD_W / 2 - 40 - answer_bubble().shape[1] / 2, top + 340
    fy = top + CARD_H - 70                                     # answer field with a blinking cursor
    draw(c, rrect(CARD_W - 80, 84, 42, (0.95, 0.96, 0.99, 1)), CARD_X, fy)
    ph_txt = 'I love law.' if 1.2 <= t < 2.25 else 'Type your answer...'
    n = int(clamp((t - 1.3) / 0.6) * len(ph_txt)) if ph_txt == 'I love law.' else len(ph_txt)
    if n > 0:
        st = ts(ph_txt[:n], F6, 32, INK if ph_txt == 'I love law.' else GREY)
        draw(c, st, CARD_X - CARD_W / 2 + 80 + st.shape[1] / 2, fy)
        if (t * 2) % 1 < 0.6:
            draw(c, rrect(3, 40, 1, NAVY), CARD_X - CARD_W / 2 + 84 + st.shape[1], fy)
    draw(c, rrect(64, 64, 32, NAVY if t < 2.25 else RED), CARD_X + CARD_W / 2 - 84, fy)
    draw(c, ts('>', F9, 30, WHITE_), CARD_X + CARD_W / 2 - 82, fy)
    if 1.7 <= t < 2.25:
        typing(c, CARD_X + CARD_W / 2 - 105, ay_, t, fill=NAVY_M, dotc=(0.8, 0.85, 1, 1))
    return ax_, ay_, top


def sc_hook(t):
    c = photo_bg('ref_library', t, 0, T['generic'], fx=0.5, fy=0.475, z0=1.12, z1=1.02, keep=0.85, top=0.36, bot=0.3)
    c = c + bg(t, 0.5) * 0 + (grid_layer()[:H, :W][..., None] * 0.35) * np.array(LINE[:3], np.float32)
    float_props(c, t, 'hook')
    chip(c, 'INTERVIEW QUESTION', 80, 300, t, 0.1, dot=True)
    kq = prog(t, 0.35, 0.6)
    if kq > 0 and t < ph('hook', 1) + 0.2:
        q = seq_at('qmark', t - 0.35)
        draw(c, q, 880, 560 + 10 * math.sin(t * 2.4), scale=0.62, opacity=1 - prog(t, ph('hook', 1) - 0.2, ph('hook', 1) + 0.2))
    out = prog(t, ph('hook', 1) - 0.3, ph('hook', 1))
    if out < 1:
        y0 = 430 - e_in_cubic(out) * 120
        layer = np.zeros_like(c)
        kin(layer, [[('Why', WHITE_), ('do', WHITE_), ('you', WHITE_), ('want', WHITE_)],
                    [('to', WHITE_), ('be', WHITE_), ('a', WHITE_), ('solicitor?', RED)]],
            80, y0, 96, t, ph('hook', 0) - 0.05, stagger=0.09)
        c = c + layer * (1 - out)
    kin(c, [[("Don't", WHITE_), ('just', WHITE_), ('say', WHITE_)], [('"I love law."', RED)]], 80, 430, 104, t,
        ph('hook', 1) - 0.05, stagger=0.1)
    r = chat_card(c, t)
    if r:
        ax_, ay_, top = r
        ka = prog(t, 2.25, 2.5)
        if ka > 0:
            dx = 10 * math.sin(t * 60) * (1 - prog(t, ph('hook', 1) + 0.5, ph('hook', 1) + 0.9)) if t > ph('hook', 1) + 0.3 else 0
            a = answer_bubble()
            if t > ph('hook', 1) + 0.3:
                pulse = 0.5 + 0.5 * math.sin(t * 10)
                draw(c, blur_sprite(tint(a, RED[:3]), 14), ax_ + dx, ay_, scale=1.06, opacity=0.8 * pulse, mode='add')
            draw(c, a, ax_ + dx, ay_ + (1 - e_out_back(ka, 2)) * 20, scale=0.9 + 0.1 * e_out_back(ka, 2), opacity=min(1, ka * 3))
            draw(c, ts('You', F6, 22, GREY), ax_ + a.shape[1] / 2 - 30, ay_ + 62, opacity=min(1, ka * 3))
    return c


# ------------------------------------------------------------------ generic: everyone says the same thing
_rng = np.random.default_rng(7)
COPIES = []
for _r in range(9):
    for _cidx in range(3):
        COPIES.append((150 + _cidx * 390 + _rng.uniform(-40, 40) + (_r % 2) * 90, 330 + _r * 175 + _rng.uniform(-20, 20),
                       _rng.uniform(-7, 7), _rng.uniform(0, 1.0), _rng.uniform(-1, 1), _rng.uniform(0.8, 1.2)))


@functools.lru_cache(maxsize=1)
def seminar_blur():
    return cv2.GaussianBlur(kb('ref_seminar', W, H, 1.1, 0.55, 0.45), (0, 0), 14)


def sc_generic(t):
    t0 = T['generic']
    c = bg(t) * 0.75 + seminar_blur() * 0.25
    a = answer_bubble()
    fall0 = FALL0
    grey = prog(t, ph('generic', 1), ph('generic', 1) + 0.6)
    for i, (x, y, rot, d, sp, sc) in enumerate(COPIES):
        k = prog(t, t0 + 0.05 + d * 1.1, t0 + 0.05 + d * 1.1 + 0.25)
        if k <= 0:
            continue
        fk = max(0.0, t - fall0 - d * 0.25)
        yy = y + 2600 * fk * fk
        rr = rot + sp * 260 * fk
        op = min(1, k * 3)
        draw(c, a, x + sp * 120 * fk, yy, scale=0.78 * sc * e_out_back(k, 2), rot=rr, opacity=op * (1 - 0.55 * grey))
    band = np.clip(1 - np.abs(_Y - 560) / 320, 0, 1)[..., None] ** 0.7 * 0.75
    c = c * (1 - band) + np.array(NAVY_D[:3], np.float32) * band
    kin(c, [[("It's", WHITE_), ('too', WHITE_), ('generic.', RED)]], 540, 500, 110, t, ph('generic', 0) - 0.05,
        align='center')
    kin(c, [[('It', GREY), ("won't", GREY), ('stand', GREY), ('out.', GREY)]], 540, 640, 64, t, ph('generic', 1),
        align='center', font=F8)
    ks = prog(t, ph('generic', 0) + 0.55, ph('generic', 0) + 0.8)
    if ks > 0 and t < fall0 + 0.3:
        st = stamp_spr()
        draw(c, st, 540, 1180, scale=2.4 - 1.4 * e_out_cubic(ks), rot=-9, opacity=min(1, ks * 2.5) * (1 - prog(t, fall0, fall0 + 0.3)))
    paper_toss(c, t)
    return c


FALL0 = 6.15                 # the copies fall away
X0 = 6.3                     # the red X is drawn over the featured answer
CR0, CR1 = 6.72, 6.95        # it crumples into a paper ball...
BIN0 = 6.95                  # ...which the 3D shot throws into the bin (lands at frame 24 = BIN0 + 1.0 s)
BIN_X, BIN_Y, BIN_S = 560, 1290, 1.3


@functools.lru_cache(maxsize=1)
def check_x():
    S4 = 200
    d = np.zeros((S4, S4), np.uint8)
    cv2.circle(d, (100, 100), 96, 255, -1, cv2.LINE_AA)
    m = np.zeros((S4, S4), np.uint8)
    cv2.line(m, (64, 64), (136, 136), 255, 20, cv2.LINE_AA)
    cv2.line(m, (136, 64), (64, 136), 255, 20, cv2.LINE_AA)
    spr = over_spr(solid(d.astype(np.float32) / 255, RED), solid(m.astype(np.float32) / 255, WHITE_))
    return cv2.resize(spr, (50, 50), interpolation=cv2.INTER_AREA)


def paper_toss(c, t):
    if t < FALL0:
        return
    a = answer_bubble()
    if t < CR1:
        kin_ = e_out_back(prog(t, FALL0, FALL0 + 0.3), 1.6)
        kc = e_in_cubic(prog(t, CR0, CR1))
        x = lerp(540, BIN_X + (60 - 360) * BIN_S, kc)
        y = lerp(1120, BIN_Y + (470 - 480) * BIN_S, kc)
        sc = 2.3 * kin_ * (1 - 0.88 * kc)
        b = a.copy()
        kx = prog(t, X0, X0 + 0.35)                         # red X scribbled across it
        if kx > 0:
            hh, ww = b.shape[:2]
            lay = np.zeros((hh, ww), np.uint8)
            for j, (p0, p1) in enumerate([((0.2, 0.12), (0.8, 0.88)), ((0.8, 0.12), (0.2, 0.88))]):
                kk = clamp(kx * 2 - j)
                if kk > 0:
                    xa, ya = p0[0] * ww, p0[1] * hh
                    xb, yb = lerp(xa, p1[0] * ww, kk), lerp(ya, p1[1] * hh, kk)
                    cv2.line(lay, (int(xa * 4), int(ya * 4)), (int(xb * 4), int(yb * 4)), 255, 6 * 4, cv2.LINE_AA, shift=2)
            m = lay.astype(np.float32)[..., None] / 255
            b[..., :3] = b[..., :3] * (1 - m) + np.array(RED[:3], np.float32) * m
            b[..., 3:] = np.maximum(b[..., 3:], m)
        if kc > 0:                                         # crumple: crush + turn into paper
            hh, ww = b.shape[:2]
            yy, xx = np.mgrid[0:hh, 0:ww].astype(np.float32)
            n = 18 * kc
            mx = xx + n * np.sin(yy / 7 + t * 9) + kc * (ww / 2 - xx) * 0.5
            my = yy + n * np.cos(xx / 9 + t * 7) + kc * (hh / 2 - yy) * 0.5
            b = cv2.remap(b, mx, my, cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT)
            paper = np.array([0.96, 0.95, 0.92], np.float32)
            b[..., :3] = b[..., :3] * (1 - kc) + paper * b[..., 3:] * kc
        if kc < 0.05:
            draw(c, blur_sprite(tint(b, (0, 0.02, 0.1)), 20), x, y + 20, scale=sc, opacity=0.5 * kin_)
        draw(c, b, x, y, scale=sc, rot=-4 + 220 * kc)
        kp = prog(t, X0 + 0.3, X0 + 0.5) * (1 - prog(t, CR0, CR0 + 0.1))
        if kp > 0:                                         # "Too generic" pill under it
            s_ = ts('Too generic', F7, 40, INK)
            p_ = rrect(s_.shape[1] + 120, 84, 42, (1, 1, 1, 1)).copy()
            paste_spr(p_, check_x(), 46, 42)
            paste_spr(p_, s_, 86 + s_.shape[1] / 2, 42)
            draw(c, p_, 540, 1300, scale=e_out_back(kp, 2.4), opacity=min(1, kp * 3))
    if t >= BIN0 - 0.05:
        k = prog(t, BIN0 - 0.25, BIN0)
        draw(c, seq_at('paper_bin', t - BIN0), BIN_X, BIN_Y, scale=BIN_S, opacity=min(1, k * 2) if t < BIN0 else 1.0)
    elif t >= BIN0 - 0.4:
        k = prog(t, BIN0 - 0.4, BIN0)
        draw(c, seq_at('paper_bin', 0), BIN_X, BIN_Y + (1 - e_out_cubic(k)) * 500, scale=BIN_S, opacity=k)


@functools.lru_cache(maxsize=1)
def stamp_spr():
    s = ts('TOO GENERIC', F9, 120, RED, 0.06)
    w, h = s.shape[1] + 90, s.shape[0] + 60
    a = rrect_alpha(w, h, 26, 2)
    ring = sdf_stroke(a, 10)
    st = over_spr(solid(ring, RED), pad(s, (w - s.shape[1]) // 2)[:ring.shape[0], :ring.shape[1]] if False else solid(ring, RED))
    out = st.copy()
    paste_spr(out, s, out.shape[1] / 2, out.shape[0] / 2)
    rng = np.random.default_rng(3)
    grit = (rng.random(out.shape[:2]) > 0.12).astype(np.float32)[..., None]
    return out * grit


# ------------------------------------------------------------------ three: the blueprint
def sc_three(t):
    c = bg(t)
    kin(c, [[('Instead,', WHITE_), ('build', WHITE_), ('your', WHITE_)], [('answer', WHITE_), ('on', WHITE_)],
            [('3', RED), ('key', RED), ('things.', RED)]], 80, 230, 80, t, ph('three', 0) - 0.05, stagger=0.07)
    c = blueprint(c, t, T['three'] + 0.15, T['three'] + 1.2, op=1.0 - 0.6 * prog(t, 9.6, 10.3))
    g = tower_geo()
    if g:
        labels = [('spire', '03  GOALS', 'right'), ('block', '01  MOTIVATION', 'left'), ('base', '02  EXPERIENCE', 'right')]
        for j, (key, lab, side) in enumerate(labels):
            x0, y0, x1, y1 = g[key]
            cy = (y0 + y1) / 2
            k = prog(t, T['three'] + 0.9 + j * 0.2, T['three'] + 1.3 + j * 0.2)
            c = dim_line(c, x1 + 20, cy, x1 + 80, cy, k, label=lab, lpos=(x1 + 150, cy), t=t, lt0=T['three'] + 1.2 + j * 0.2, size=27)
            ki = prog(t, T['three'] + 1.2 + j * 0.2, T['three'] + 1.45 + j * 0.2)
            if ki > 0:
                draw(c, icon(['chart', 'target', 'doc'][j]), x1 + 114, cy, scale=e_out_back(ki, 2.4), opacity=min(1, ki * 3))
    c = over_full(c, 'pieces_float', t - (T['three'] + 0.85))
    return c


# ------------------------------------------------------------------ 01 motivation
MOT_X, MOT_Y, MOT_S = 540, 1040, 1.55


def sc_motiv(t):
    t0 = T['motiv']
    c = bg(t)
    section_head(c, t, '01', 'Your motivation', ph('motiv', 0), ph('motiv', 1))
    float_props(c, t, 'motiv')
    k = e_out_back(prog(t, t0 + 0.05, t0 + 0.6), 1.5)
    spr = seq_at('motiv_hero', t - t0, loop=True)
    # circle centre in the hero render (block centred in a 640 frame) + gentle float
    cx, cy = MOT_X, MOT_Y + 8 * math.sin(t * 2)
    r = 118 * MOT_S * k
    target_rings(c, cx, cy, r, t, t0 + 0.6)
    c = crosshair(c, cx, cy, r, prog(t, t0 + 0.5, t0 + 0.9))
    draw(c, target_photo(spr, t), MOT_X, MOT_Y + 8 * math.sin(t * 2), scale=MOT_S * (0.6 + 0.4 * k), opacity=min(1, k * 2))
    kb_ = prog(t, ph('motiv', 2) + 0.1, ph('motiv', 2) + 0.4)
    if kb_ > 0:
        draw(c, seq_at('bulb', t - ph('motiv', 2) - 0.1), 900, 690 + 8 * math.sin(t * 2.2), scale=0.5)
    kin(c, [[('Explain', WHITE_), ('what', WHITE_), ('really', WHITE_)], [('drives', RED), ('you.', RED)]],
        80, 640, 60, t, ph('motiv', 2) - 0.05, font=F8)
    sticky(c, t, ph('motiv', 2) + 0.6)
    return c


NOTE = ['e.g. A desire to make', 'a positive impact', 'on people\'s lives.']
NOTE_X, NOTE_Y = 560, 1560


def sticky(c, t, t0):
    """A yellow sticky note slaps on, then the example writes itself in pen."""
    k = prog(t, t0, t0 + 0.3)
    if k <= 0:
        return
    w, h = 720, 330
    note = rrect(w, h, 10, hexc('#FFE27A')).copy()
    note[:, :, :3] *= np.linspace(1.0, 0.9, note.shape[0], dtype=np.float32)[:, None, None]
    paste_spr(note, rrect(150, 40, 4, (1, 1, 1, 0.55)), w / 2, 6)
    n_all = sum(len(l) for l in NOTE)
    n = int(clamp((t - t0 - 0.3) / 1.4) * n_all)
    for li, line in enumerate(NOTE):
        take = max(0, min(len(line), n))
        n -= len(line)
        if take:
            sp = solid(_wmask(line[:take], 'Caveat-700', 66), INK)
            paste_spr(note, sp, 44 + sp.shape[1] / 2, 86 + li * 84)
    shadow(c, note, NOTE_X, NOTE_Y, 0.45, 18, 16)
    draw(c, note, NOTE_X, NOTE_Y, scale=1.25 - 0.25 * e_out_back(k, 2.0), rot=-4, opacity=min(1, k * 3))


def target_photo(spr, t):
    """Put the person inside the block's white circle: the disc keeps its 3D shading, the photo replaces its colour."""
    a = spr[..., 3]
    rgb = spr[..., :3] / np.maximum(a[..., None], 1e-4)
    disc = ((rgb.min(2) > 0.7) & (a > 0.9)).astype(np.uint8)
    n, lab, st, _ = cv2.connectedComponentsWithStats(disc)
    if n < 2:
        return spr
    j = 1 + int(np.argmax(st[1:, cv2.CC_STAT_AREA]))
    x, y, w, h = st[j, :4]
    m = (lab == j).astype(np.float32)
    m = cv2.GaussianBlur(cv2.erode(m, np.ones((3, 3), np.uint8)), (0, 0), 1.0)
    ph_ = kb('ref_entrance', w, h, 1.6 + 0.04 * math.sin(t), 0.5, 0.36)
    shade = np.clip(rgb[y:y + h, x:x + w].mean(2, keepdims=True) / 0.92, 0.6, 1.15)
    out = spr.copy()
    mm = m[y:y + h, x:x + w, None]
    out[y:y + h, x:x + w, :3] = out[y:y + h, x:x + w, :3] * (1 - mm) + ph_ * shade * a[y:y + h, x:x + w, None] * mm
    return out


# ------------------------------------------------------------------ 02 experience
EXP_X, EXP_Y, EXP_S = 560, 1180, 1.15
BOOK_Y = [608, 536, 464, 392]       # spine centres in the 900x900 books render
BOOK_L, BOOK_R = 162, 711
EXP_SEQ0 = None
COURSE_LABELS = ['Work experience', 'Volunteering', 'Academic projects', 'Transferable skills']


def exp_seq0():
    return ph('exp', 1) - 0.25


def course_screen_y(k):
    return EXP_Y + (BOOK_Y[k] - 450) * EXP_S


def sc_exp(t):
    t0 = T['exp']
    c = photo_bg('ref_notes', t, t0, T['goals'] - t0, fx=0.5, fy=0.55, z0=1.1, z1=1.0, keep=0.32, top=0.4)
    c = c + grid_layer()[:H, :W][..., None] * 0.6 * np.array(LINE[:3], np.float32)
    section_head(c, t, '02', 'Relevant experience', ph('exp', 0), ph('exp', 1))
    float_props(c, t, 'exp')
    kin(c, [[('Link', WHITE_), ('your', WHITE_), ('skills,', WHITE_), ('studies', WHITE_)],
            [('or', WHITE_), ('work', WHITE_), ('experience', WHITE_), ('to', WHITE_)],
            [('what', RED_L), ("you've", RED_L), ('learned.', RED_L)]], 80, 640, 50, t, ph('exp', 2) - 0.05, font=F8, stagger=0.05)
    tl = t - exp_seq0()
    spr = seq_at('books', tl)
    draw(c, spr, EXP_X, EXP_Y + 6 * math.sin(t * 1.8), scale=EXP_S)
    learned = prog(t, ph('exp', 3) - 0.1, ph('exp', 3) + 0.5)
    for k, lab in enumerate(COURSE_LABELS):            # a tick lands beside each book
        land = exp_seq0() + (8 + 18 * k + 9) / 24
        kk = prog(t, land + 0.05, land + 0.35)
        if kk <= 0:
            continue
        y = course_screen_y(k) + 6 * math.sin(t * 1.8)
        x = EXP_X + (BOOK_R - 450) * EXP_S + 70
        draw(c, check(66), x, y, scale=e_out_back(kk, 2.6), opacity=min(1, kk * 3))
    if learned > 0:                                  # a red bracket links the whole foundation to what you learned
        y_top, y_bot = course_screen_y(3) - 50, course_screen_y(0) + 50
        bx = EXP_X + (BOOK_L - 450) * EXP_S - 50
        s_ = ts("WHAT YOU'VE LEARNED", F9, 40, WHITE_, 0.1)
        pw = s_.shape[1] + 90
        path = [(bx + 40, y_top), (bx, y_top), (bx, y_bot), (bx, 1700), (540 - pw / 2, 1700)]
        seg = [math.hypot(path[i + 1][0] - path[i][0], path[i + 1][1] - path[i][1]) for i in range(len(path) - 1)]
        L = sum(seg) * e_inout_cubic(learned)
        pts = [path[0]]
        for i, d in enumerate(seg):
            if L <= 0:
                break
            u = min(1.0, L / d)
            pts.append((lerp(path[i][0], path[i + 1][0], u), lerp(path[i][1], path[i + 1][1], u)))
            L -= d
        lay = np.zeros((H, W), np.uint8)
        cv2.polylines(lay, [(np.array(pts) * 4).astype(np.int32)], False, 255, 6 * 4, cv2.LINE_AA, shift=2)
        cv2.line(lay, (int((bx) * 4), int(y_bot * 4)), (int((bx + 40) * 4), int(y_bot * 4)), 255 if learned > 0.3 else 0, 6 * 4, cv2.LINE_AA, shift=2)
        mm = lay.astype(np.float32)
        glow = cv2.GaussianBlur(mm, (0, 0), 8) / 255 * 0.6
        c = c + glow[..., None] * np.array(RED[:3], np.float32)
        mm = mm[..., None] / 255
        c = c * (1 - mm) + np.array(RED_L[:3], np.float32) * mm
    if learned > 0.95:
        kk = prog(t, ph('exp', 3) + 0.4, ph('exp', 3) + 0.7)
        s = ts("WHAT YOU'VE LEARNED", F9, 40, WHITE_, 0.1)
        p = rrect(s.shape[1] + 90, 96, 48, RED)
        draw(c, blur_sprite(tint(p, RED[:3]), 24), 540, 1700, opacity=0.6 * kk, mode='add')
        draw(c, p, 540, 1700, scale=e_out_back(kk, 2.2))
        draw(c, s, 540, 1700, scale=e_out_back(kk, 2.2))
    return c


# ------------------------------------------------------------------ 03 long-term goals
GOAL_X, GOAL_Y, GOAL_S = 300, 1380, 1.25
MILES = [('Trainee solicitor', 520, 1320), ('Specialise', 720, 1080), ('Make an impact', 900, 840)]


SIGN_X, SIGN_Y, SIGN_S = 470, 1250, 1.25
SIGN_T0 = None


def sign_t0():
    return ph('goals', 2) - 0.75                 # signs pop at sequence frames 8 / 26 / 44


def sc_goals(t):
    t0 = T['goals']
    c = photo_bg('ref_city', t, t0, T['cta'] - t0, fx=0.5, fy=0.42, z0=1.0, z1=1.12, keep=0.6, top=0.45, bot=0.3)
    section_head(c, t, '03', 'Long-term goals', ph('goals', 0), ph('goals', 1))
    float_props(c, t, 'goals')
    kin(c, [[('Show', WHITE_), ('how', WHITE_), ('becoming', WHITE_), ('a', WHITE_)],
            [('solicitor', WHITE_), ('fits', WHITE_), ('into', WHITE_)], [('your', RED_L), ('future.', RED_L)]],
        80, 640, 50, t, ph('goals', 2) - 0.05, font=F8, stagger=0.05)
    # rising red growth arrow behind the signpost
    ka = e_inout_cubic(prog(t, ph('goals', 3) - 0.6, ph('goals', 3) + 0.4))
    if ka > 0:
        path = [(110, 1700), (330, 1520), (450, 1580), (700, 1280), (820, 1340), (1000, 1020)]
        seg = [math.hypot(path[i + 1][0] - path[i][0], path[i + 1][1] - path[i][1]) for i in range(len(path) - 1)]
        L = sum(seg) * ka
        pts = [path[0]]
        for i, d in enumerate(seg):
            if L <= 0:
                break
            u = min(1.0, L / d)
            pts.append((lerp(path[i][0], path[i + 1][0], u), lerp(path[i][1], path[i + 1][1], u)))
            L -= d
        lay = np.zeros((H, W), np.uint8)
        cv2.polylines(lay, [(np.array(pts) * 4).astype(np.int32)], False, 255, 14 * 4, cv2.LINE_AA, shift=2)
        (xa, ya), (xb, yb) = pts[-2], pts[-1]
        ang = math.atan2(yb - ya, xb - xa)
        head = [(xb + 40 * math.cos(ang), yb + 40 * math.sin(ang)), (xb + 34 * math.cos(ang + 2.3), yb + 34 * math.sin(ang + 2.3)),
                (xb + 34 * math.cos(ang - 2.3), yb + 34 * math.sin(ang - 2.3))]
        cv2.fillPoly(lay, [(np.array(head) * 4).astype(np.int32)], 255, cv2.LINE_AA, shift=2)
        m = lay.astype(np.float32) / 255
        c = c + cv2.GaussianBlur(m, (0, 0), 14)[..., None] * np.array(RED[:3], np.float32) * 0.7
        c = c * (1 - m[..., None]) + np.array(RED[:3], np.float32) * m[..., None]
    k = prog(t, t0 + 0.1, t0 + 0.6)
    if k > 0:
        draw(c, seq_at('signpost', t - sign_t0()), SIGN_X, SIGN_Y + (1 - e_out_back(k, 1.4)) * 300, scale=SIGN_S,
             opacity=min(1, k * 2))
    kf = prog(t, ph('goals', 3) + 0.35, ph('goals', 3) + 0.7)
    if kf > 0:
        s_ = ts('YOUR FUTURE', F9, 34, WHITE_, 0.12)
        p_ = rrect(s_.shape[1] + 60, 70, 35, RED)
        draw(c, p_, 870, 950, scale=e_out_back(kf, 2.4))
        draw(c, s_, 870, 950, scale=e_out_back(kf, 2.4))
    return c


# ------------------------------------------------------------------ CTA: the emblem snaps together -> logo card
@functools.lru_cache(maxsize=1)
def logo():
    return load_png_sprite(f'{S}/src/logo_full.png')


CHECKS = [('base', 'Relevant experience', 'that shaped you'), ('block', 'Genuine motivation', 'personal and specific'),
          ('spire', 'Clear long-term goals', "where you're heading")]
SNAPS = [T['cta'] + (6 + 9 * j + 12) / 24 for j in range(3)]


@functools.lru_cache(maxsize=1)
def emblem_geo():
    """Piece boxes of the assembled emblem (last emblem_build frame, as placed on screen)."""
    fs = files('emblem_build')
    if not fs:
        return None
    rgb, a = full_rgba('emblem_build', len(fs) - 1)
    col = rgb / np.maximum(a[..., None], 1e-4)
    solidm = a > 0.6
    red = solidm & (col[..., 0] > col[..., 1] + 0.25) & (col[..., 0] > col[..., 2] + 0.15)
    ys, xs = np.where(red)
    if len(xs) == 0:
        return None
    rb = (xs.min(), ys.min(), xs.max(), ys.max())
    navy = solidm & ~red & (col.min(2) < 0.6)
    ys2, xs2 = np.where(navy & (_Y < rb[1] - 5))
    ys3, xs3 = np.where(navy & (_Y > rb[3] + 5))
    return dict(block=rb, spire=(xs2.min(), ys2.min(), xs2.max(), ys2.max()), base=(xs3.min(), ys3.min(), xs3.max(), ys3.max()))


def sc_cta(t):
    t0 = T['cta']
    card_k = e_inout_cubic(prog(t, ph('cta', 1) + 0.2, ph('cta', 1) + 0.75))
    c = bg(t)
    kin(c, [[('Connect', WHITE_), ('all', WHITE_), ('three.', RED)]], 540, 320, 96, t, ph('cta', 0) - 0.05, align='center')
    c = over_full(c, 'emblem_build', t - t0)
    chip(c, 'STRONG ANSWER', 540 - 130, 190, t, ph('cta', 0) - 0.1)
    g = emblem_geo()
    if g:
        for j, (key, l1, l2) in enumerate(CHECKS):
            kk = prog(t, SNAPS[j], SNAPS[j] + 0.3)
            if kk <= 0:
                continue
            x0, y0, x1, y1 = g[key]
            y = (y0 + y1) / 2
            x = x1 + 36
            draw(c, check(56), x + 28, y - 18, scale=e_out_back(kk, 2.4))
            s1 = wspr(l1, F8, 36, WHITE_)
            s2 = wspr(l2, F6, 28, GREY)
            draw(c, s1, x + 70 + s1.shape[1] / 2, y - 22 + (1 - e_out_cubic(kk)) * 16, opacity=kk)
            draw(c, s2, x + 70 + s2.shape[1] / 2, y + 24 + (1 - e_out_cubic(kk)) * 16, opacity=kk)
        sw = prog(t, SNAPS[2] + 0.3, SNAPS[2] + 1.0)
        if 0 < sw < 1:
            rgb, a_ = full_rgba('emblem_build', 59)
            band = np.exp(-((_X - lerp(-200, W + 200, sw) + (_Y - 1100) * 0.35) / 70) ** 2)
            c = c + (band * a_)[..., None] * 0.55
    if card_k > 0:
        c = end_card(c, t, card_k)
    return c


@functools.lru_cache(maxsize=1)
def card_base():
    card = np.ones((H, W, 3), np.float32) * np.array(ICE[:3], np.float32)
    return card - grid_layer()[:H, :W][..., None] * 0.12


@functools.lru_cache(maxsize=1)
def arrow_spr():
    m = np.zeros((160, 160), np.uint8)
    cv2.line(m, (40, 80), (116, 80), 255, 16, cv2.LINE_AA)
    cv2.polylines(m, [np.array([[86, 48], [120, 80], [86, 112]], np.int32)], False, 255, 16, cv2.LINE_AA)
    return cv2.resize(solid(m.astype(np.float32) / 255, WHITE_), (40, 40), interpolation=cv2.INTER_AREA)


def end_card(c, t, card_k):
    """Ice panel rises: the St Paul's steps photo up top, logo + 3D cap, 'Prepare with purpose.'"""
    t1 = ph('cta', 1)
    card = card_base().copy()
    ph_ = kb('ref_stpauls', W, 900, 1.08 - 0.06 * prog(t, t1, DUR), 0.5, 0.42)
    fade = np.clip((_Y[:900] - 560) / 340, 0, 1)[..., None] ** 1.2
    card[:900] = ph_ * (1 - fade) + card[:900] * fade
    m = np.clip((card_k * (H + 400) - (H - _Y)) / 3, 0, 1)[..., None]     # panel rises from the bottom
    c = c * (1 - m) + card * m
    kl = prog(t, t1 + 0.55, t1 + 1.0)
    if kl > 0:
        lg = logo()
        draw(c, blur_sprite(tint(lg, (0.0, 0.05, 0.2)), 16), 540, 1035, scale=1.05, opacity=0.18 * kl)
        draw(c, lg, 540, 1020, scale=1.0 * (0.9 + 0.1 * e_out_back(kl, 1.8)), opacity=min(1, kl * 2))
    kc = prog(t, t1 + 0.8, t1 + 1.2)
    if kc > 0:
        draw(c, seq_at('cap', t - t1, loop=True), 870, 830 + 10 * math.sin(t * 2), scale=0.5 * e_out_back(kc, 1.8))
    kin(c, [[('Prepare', INK), ('with', INK)], [('purpose.', RED)]], 540, 1330, 104, t, t1 + 0.75, align='center',
        stagger=0.1)
    pw_ = _wmask('purpose.', F9, 104).shape[1]
    title_sweep(c, 'purpose.', 540 - pw_ / 2, 1330 + 104 * 1.12, 104, t, t1 + 1.35)
    ku = prog(t, t1 + 1.3, t1 + 1.8)
    if ku > 0:
        lay = np.zeros((H, W), np.uint8)
        pts = [(340 + 400 * u, 1515 + 12 * math.sin(u * 3.2)) for u in np.linspace(0, e_out_cubic(ku), 40)]
        cv2.polylines(lay, [(np.array(pts) * 4).astype(np.int32)], False, 255, 9 * 4, cv2.LINE_AA, shift=2)
        mm = lay.astype(np.float32)[..., None] / 255
        c = c * (1 - mm) + np.array(RED[:3], np.float32) * mm
    kw = prog(t, t1 + 1.6, t1 + 2.0)
    if kw > 0:
        s_ = ts('iclondon.co.uk', F7, 44, NAVY)
        draw(c, s_, 510, 1640, opacity=kw)
        bx_ = 510 + s_.shape[1] / 2 + 60
        kb2 = prog(t, t1 + 1.8, t1 + 2.1)
        if kb2 > 0:
            draw(c, blur_sprite(tint(rrect(76, 76, 38, RED), RED[:3]), 14), bx_, 1640, opacity=0.5 * kb2, mode='add')
            draw(c, rrect(76, 76, 38, RED), bx_, 1640, scale=e_out_back(kb2, 2.6))
            draw(c, arrow_spr(), bx_ + 4 * math.sin(t * 6), 1640, scale=e_out_back(kb2, 2.6))
        s2 = ts('SQE PREPARATION  ·  LONDON', F7, 26, GREY, 0.16)
        draw(c, s2, 540, 1705, opacity=kw)
    return c


# ------------------------------------------------------------------ transitions (brand shapes)
def circle_iris(prev, nxt, p):
    """The white circle of the red block grows until it fills the frame, then dissolves into the next scene."""
    g = tower_geo()
    cx, cy, r0 = g['circle'] if g else (W / 2, H / 2, 60)
    if p < 0.55:
        r = r0 + e_in_cubic(p / 0.55) * 2300
        m = np.clip((r - np.sqrt((_X - cx) ** 2 + (_Y - cy) ** 2)) / 2, 0, 1)[..., None]
        return prev * (1 - m) + m * 1.0
    k = (p - 0.55) / 0.45
    return nxt * e_out_cubic(k) + (1 - e_out_cubic(k)) * 1.0


def base_wipe(prev, nxt, p):
    """A navy slab (the emblem base) slides up over the frame, then off the top revealing the next scene."""
    e = e_inout_cubic(p)
    y_top = lerp(H, -H * 0.15, e)
    y_bot = lerp(H * 1.9, H * 0.0, e) if False else y_top + H * 1.15 * (1 - e) + 10
    out = np.where(_Y[..., None] < y_top, prev, nxt)
    slab = (_Y >= y_top) & (_Y < y_top + H * 0.55 * math.sin(math.pi * e))
    out = np.where(slab[..., None], np.array(NAVY[:3], np.float32), out)
    edge = np.exp(-((_Y - y_top) / 4) ** 2)[..., None] * 0.8 * math.sin(math.pi * e)
    return out + edge * np.array(LINE[:3], np.float32)


def tri_wipe(prev, nxt, p):
    """The emblem spire (a triangle) rises from the bottom and opens onto the next scene."""
    e = e_in_cubic(p)
    apex_y = lerp(H + 50, -2600, e)
    half = (_Y - apex_y) * 0.62
    inside = (np.abs(_X - W / 2) < half) & (_Y > apex_y)
    edge = np.exp(-((np.abs(_X - W / 2) - half) / 5) ** 2) * (_Y > apex_y)
    out = np.where(inside[..., None], nxt, prev)
    return out + edge[..., None] * np.array(RED[:3], np.float32) * 0.9 * (1 - e)


def square_zoom(prev, nxt, p):
    """The red emblem block zooms through the camera."""
    e = e_in_cubic(p)
    s = 20 + e * 2400
    inside = (np.abs(_X - W / 2) < s / 2) & (np.abs(_Y - H / 2) < s / 2)
    hole = (np.sqrt((_X - W / 2) ** 2 + (_Y - H / 2) ** 2) < s * 0.33) & inside
    out = np.where(inside[..., None], np.array(RED[:3], np.float32), prev)
    out = np.where(hole[..., None], nxt, out)
    return out


# ------------------------------------------------------------------ energy layer
PROPS = {   # scene -> (prop, x, y, scale, appear time, depth blur, phase)
    'hook': [('gavel', 150, 880, 0.6, 0.5, 2.5, 0.0), ('scales', 935, 930, 0.6, 0.7, 2.5, 1.3)],
    'motiv': [('pin', 160, 830, 0.55, T['motiv'] + 0.5, 1.5, 0.4)],
    'exp': [('briefcase', 930, 360, 0.5, T['exp'] + 0.5, 0.0, 0.2), ('exam', 960, 1560, 0.45, T['exp'] + 3.6, 1.5, 1.1)],
    'goals': [('shield', 935, 340, 0.5, T['goals'] + 0.6, 0.0, 0.7), ('scales', 880, 1660, 0.45, T['goals'] + 2.0, 1.5, 2.0)],
}


def float_props(c, t, key):
    for name, x, y, sc, t0, blur, phs in PROPS.get(key, []):
        k = prog(t, t0, t0 + 0.55)
        if k <= 0:
            continue
        spr = seq_at('ic_' + name, (t - t0), loop=True, fps=14)
        if blur:
            spr = blur_sprite(spr, blur)
        e = e_out_back(k, 1.8)
        draw(c, blur_sprite(tint(spr, (0.0, 0.02, 0.1)), 14), x + 12, y + 30, scale=sc * e, opacity=0.35 * k)
        draw(c, spr, x + 10 * math.sin(t * 0.9 + phs), y + 16 * math.sin(t * 1.4 + phs) + (1 - e) * 120,
             scale=sc * e, rot=6 * math.sin(t * 0.8 + phs), opacity=min(1, k * 2))


@functools.lru_cache(maxsize=1)
def shapes():
    out = []
    for col in (RED, WHITE_, LINE, RED_L):
        for kind in range(3):
            s_ = 48
            m = np.zeros((s_, s_), np.uint8)
            if kind == 0:
                cv2.rectangle(m, (10, 10), (38, 38), 255, -1)
            elif kind == 1:
                cv2.circle(m, (24, 24), 14, 255, -1, cv2.LINE_AA)
            else:
                cv2.fillPoly(m, [np.array([[24, 8], [40, 38], [8, 38]], np.int32)], 255, cv2.LINE_AA)
            out.append(solid(m.astype(np.float32) / 255, col))
    return out


def burst(c, x, y, t, t0, seed=0, n=22, speed=900, size=1.0):
    """Brand-shape confetti (squares, circles, triangles from the emblem) bursting out on a hit."""
    dt = t - t0
    if dt < 0 or dt > 1.1:
        return
    rng = np.random.default_rng(seed)
    sh = shapes()
    for i in range(n):
        a = rng.uniform(0, 2 * math.pi)
        v = speed * rng.uniform(0.45, 1.0)
        drag = math.exp(-dt * 2.2)
        px = x + math.cos(a) * v * (1 - drag) / 2.2
        py = y + math.sin(a) * v * (1 - drag) / 2.2 + 520 * dt * dt
        op = clamp(1 - dt / 1.1) ** 1.2
        draw(c, sh[rng.integers(len(sh))], px, py, scale=size * rng.uniform(0.35, 0.8), rot=rng.uniform(0, 360) + dt * rng.uniform(-500, 500),
             opacity=op)


def bursts_at(c, t):
    B = [(ph('generic', 0) + 0.65, 540, 1180, 1, 34, 1300, 1.2)]
    B.append((ph('motiv', 2) + 0.65, NOTE_X, NOTE_Y, 10, 16, 800, 0.8))
    for k in range(4):
        B.append((exp_seq0() + (8 + 18 * k + 9) / 24, EXP_X + (BOOK_R - 450) * EXP_S + 70, course_screen_y(k), 20 + k, 14, 700, 0.8))
    B.append((ph('exp', 3) + 0.45, 540, 1700, 30, 26, 1000, 1.0))
    for j in range(3):
        B.append((sign_t0() + (8 + 18 * j + 8) / 24, SIGN_X + (1 if j != 1 else -1) * 220, SIGN_Y - 380 + j * 190, 40 + j, 14, 700, 0.8))
    B.append((ph('goals', 3) + 0.4, 1000, 1020, 44, 24, 1000, 1.0))
    g = emblem_geo()
    if g:
        for j, (key, _, _) in enumerate(CHECKS):
            x0, y0, x1, y1 = g[key]
            B.append((SNAPS[j], (x0 + x1) / 2, (y0 + y1) / 2, 50 + j, 16, 900, 0.9))
    B.append((ph('cta', 1) + 0.6, 540, 1020, 60, 40, 1500, 1.2))
    for (t0, x, y, seed, n, sp, sz) in B:
        burst(c, x, y, t, t0, seed, n, sp, sz)


def hits():
    """(time, punch strength, shake amplitude, flash)"""
    hs = [(ph('hook', 0), 0.5, 0, 0), (ph('hook', 1), 0.9, 6, 0), (ph('generic', 0), 0.8, 0, 0),
          (ph('generic', 0) + 0.65, 1.2, 18, 0.25), (ph('three', 0), 0.6, 0, 0),
          (ph('motiv', 1), 0.9, 4, 0), (ph('exp', 1), 0.9, 4, 0), (ph('goals', 1), 0.9, 4, 0),
          (ph('cta', 0), 0.7, 0, 0), (ph('cta', 1) + 0.6, 1.0, 10, 0.35)]
    for tc in TRANS:
        hs.append((tc, 0.7, 0, 0.3))
    for k in range(4):
        hs.append((exp_seq0() + (8 + 18 * k + 9) / 24, 0.4, 9, 0))
    for j in range(3):
        hs.append((T['cta'] + (6 + 9 * j + 12) / 24, 0.5, 10, 0))
        hs.append((T['three'] + 0.85 + (4 + 7 * j + 16) / 24, 0.3, 6, 0))
    return hs


HITS = None


def energy(t):
    """Zoom punch, shake offset, chromatic split and flash for time t."""
    global HITS
    if HITS is None:
        HITS = hits()
    z, sx, sy, ca, fl = 1.0, 0.0, 0.0, 0.0, 0.0
    for (th, pn, sh, f) in HITS:
        d = t - th
        if 0 <= d < 0.35:
            e = (1 - d / 0.35) ** 2
            z += 0.045 * pn * e
            ca = max(ca, 7 * pn * e)
            if sh:
                sx += sh * e * math.sin(t * 97 + th)
                sy += sh * e * math.cos(t * 83 + th)
        if f and 0 <= d < 0.18:
            fl = max(fl, f * (1 - d / 0.18))
    return z, sx, sy, ca, fl


def whip(prev, nxt, p, axis=1):
    """Whip-pan: both frames slide with heavy motion blur."""
    e = e_inout_cubic(p)
    off = int(e * (W if axis == 1 else H))
    if axis == 1:
        both = np.concatenate([prev, nxt], 1)[:, off:off + W]
    else:
        both = np.concatenate([prev, nxt], 0)[off:off + H]
    L = int(1 + 160 * math.sin(math.pi * p))
    k = np.ones((1, L) if axis == 1 else (L, 1), np.float32) / L
    return cv2.filter2D(both, -1, k, borderType=cv2.BORDER_REFLECT)


SCENES = [(T['hook'], T['generic'], sc_hook), (T['generic'], T['three'], sc_generic), (T['three'], T['motiv'], sc_three),
          (T['motiv'], T['exp'], sc_motiv), (T['exp'], T['goals'], sc_exp), (T['goals'], T['cta'], sc_goals),
          (T['cta'], 99, sc_cta)]
TRANS = {T['generic']: (lambda a, b, p: whip(a, b, p, 1), 0.4), T['three']: (lambda a, b, p: whip(a, b, p, 0), 0.4),
         T['motiv']: (circle_iris, 0.5), T['exp']: (base_wipe, 0.55), T['goals']: (tri_wipe, 0.5),
         T['cta']: (square_zoom, 0.5)}


def scene_at(t):
    for a, b, f in SCENES:
        if a <= t < b:
            return f
    return SCENES[-1][2]


def render_raw(t):
    c = None
    for tc, (fn, dur) in TRANS.items():
        d = t - (tc - dur / 2)
        if 0 <= d < dur:
            prev = scene_at(tc - 0.01)(min(t, tc - 0.01))
            nxt = scene_at(tc)(max(t, tc))
            c = fn(prev, nxt, d / dur)
    if c is None:
        c = scene_at(t)(t)
    bursts_at(c, t)
    z, sx, sy, _, _ = energy(t)
    if z > 1.001 or abs(sx) + abs(sy) > 0.5:
        M = np.float32([[z, 0, (1 - z) * W / 2 + sx], [0, z, (1 - z) * H / 2 + sy]])
        c = cv2.warpAffine(c, M, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
    if t > DUR - 0.5:
        c = c * (1 - 0.15 * prog(t, DUR - 0.5, DUR))
    return c


def is_fast(t):
    return any(abs(t - tc) < dur / 2 + 0.02 for tc, (_, dur) in TRANS.items()) or energy(t)[0] > 1.02


def render(fi):
    t = fi / FPS
    if is_fast(t):
        acc = sum(render_raw(t + (k / 3 - 0.33) * 0.5 / FPS) for k in range(3))
        c = acc / 3
    else:
        c = render_raw(t)
    end = t >= ph('cta', 1) + 0.6
    _, _, _, ca, fl = energy(t)
    return post(c, fi, bloom=0.06 if end else 0.22, grain=0.012, vig=0.0 if end else 0.6, ca=ca, flash=fl,
                flash_color=(1.0, 1.0, 1.0))


def to_u8(im):
    return (np.clip(im, 0, 1) * 255 + 0.5).astype(np.uint8)[..., ::-1]


if __name__ == '__main__':
    mode = sys.argv[1]
    if mode == 'still':
        os.makedirs(f'{S}/stills', exist_ok=True)
        for tt_ in sys.argv[2].split(','):
            t = float(tt_)
            cv2.imwrite(f'{S}/stills/s_{t:05.2f}.jpg', to_u8(render(int(round(t * FPS)))), [cv2.IMWRITE_JPEG_QUALITY, 90])
            print('still', t, flush=True)
    elif mode == 'range':
        a, b = int(sys.argv[2]), int(sys.argv[3])
        os.makedirs(f'{S}/frames_out', exist_ok=True)
        for fi in range(a, b):
            p = f'{S}/frames_out/{fi:04d}.png'
            if os.environ.get('RESUME') and os.path.exists(p):
                continue
            cv2.imwrite(p, to_u8(render(fi)), [cv2.IMWRITE_PNG_COMPRESSION, 1])
            print('frame', fi, flush=True)
    elif mode == 'times':
        print(json.dumps({'VO': VO, 'PH': PH}, indent=1))
