"""Scene images for Hulk Marketing "Anything but ordinary" (9:16 video with people, word-synced 3D pop-ups).

Story: hundreds of people walk past Sam's café every day (grey, ordinary). Sam calls Hulk Marketing: a green "flex"
shockwave turns the world to colour, the real Hulk team lines up, and each service pops on its word (website, search,
social, Google & Meta ads, brand, AI that answers at midnight). The street stops walking past and walks in.

Look: near-black brand canvas with a faint green grid; Inter Tight Black captions with cue words knocked out of a green
"HULK box" (the logo device); numbered service chips (01 / Website) and a six-part service bar at the top; green energy
cracks and shockwaves; glossy green 3D tokens with burst lines.

Usage: python3 frames_hulk.py [n ...] -> workspace_hulk/frames/scene_XX.png + storyboard.jpg
"""
import os, sys, math, glob
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'pipeline_cf'))
import numpy as np
import cv2
import frames_cf as F
from frames_cf import R, W, H, draw, blur_sprite, tint, rrect, ts, solid, paste_spr, load_png_sprite, _wmask

ROOT = os.path.abspath(os.path.join(HERE, '..'))
S = f'{ROOT}/workspace_hulk'
OUT = f'{S}/frames'
_X, _Y = R._X, R._Y


def hexc(h, a=1.0):
    h = h.lstrip('#')
    return tuple(int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)) + (a,)


INK, GREEN, LIME, PAPER = hexc('#06070A'), hexc('#60D417'), hexc('#9DEF69'), hexc('#F3F5F0')
WHITE = (1.0, 1.0, 1.0, 1.0)
HB, HX = 'Headline-900', 'Headline-800'          # Inter Tight (site display face)
HK, HK5 = 'Hanken-700', 'Hanken-500'             # Hanken Grotesk (site body face)
SERVICES = ['Website', 'Search', 'Social', 'Ads', 'Brand', 'AI']


# ------------------------------------------------------------------ sources + grades
def frame_of(cid, t=0.45):
    cap = cv2.VideoCapture(f'{S}/clips/{cid}.mp4')
    cap.set(cv2.CAP_PROP_POS_FRAMES, int(cap.get(cv2.CAP_PROP_FRAME_COUNT) * t))
    ok, im = cap.read()
    return im[..., ::-1].astype(np.float32) / 255


def grey(im, amt=1.0):
    """'Ordinary': drained, cool, flat."""
    lum = (im * np.array([0.3, 0.59, 0.11], np.float32)).sum(2, keepdims=True)
    g = lum * np.array([0.96, 1.0, 1.04], np.float32)
    g = (g - 0.5) * 0.85 + 0.47
    return np.clip(im * (1 - amt) + g * amt, 0, 1).astype(np.float32)


def vivid(im):
    """'Hulk': punchy, rich colour, a green lift in the shadows."""
    lum = im.mean(2, keepdims=True)
    im = lum + (im - lum) * 1.22
    im = (im - 0.5) * 1.08 + 0.5
    sh = np.clip(1 - lum * 2.4, 0, 1)
    im = im + sh * np.array([-0.01, 0.035, -0.005], np.float32)
    return np.clip(im, 0, 1).astype(np.float32)


def clip(cid, t=0.45, fx=0.5, fy=0.5, z=1.0, w=W, h=H, mode='vivid'):
    im = F.cover(frame_of(cid, t), fx, fy, z, w, h)
    return grey(im) if mode == 'grey' else vivid(im)


def web(name, w, h, fx=0.5, fy=0.5):
    im = cv2.imread(f'{S}/web/{name}')[..., ::-1].astype(np.float32) / 255
    return F.cover(im, fx, fy, 1.0, w, h)


_SPR = {}


def spr(path):
    if path not in _SPR:
        _SPR[path] = load_png_sprite(path)
    return _SPR[path]


def trim(sp, pad=12):
    ys, xs = np.where(sp[..., 3] > 0.02)
    y0, y1, x0, x1 = max(0, ys.min() - pad), min(sp.shape[0], ys.max() + pad), max(0, xs.min() - pad), min(sp.shape[1], xs.max() + pad)
    return np.ascontiguousarray(sp[y0:y1, x0:x1])


_TOK = {}


def token(name):
    if name not in _TOK:
        _TOK[name] = trim(spr(f'{S}/tokens/{name}.png'))
    return _TOK[name]


def logo(white_only=False):
    return spr(f'{S}/web/hulk-marketing-logo.png')


def cutout(name):
    return spr(f'{S}/web/{name}')


# ------------------------------------------------------------------ canvases
def canvas(glow=(760, 520), amt=0.22):
    """Near-black brand canvas, faint green grid, a green glow."""
    c = np.ones((H, W, 3), np.float32) * np.array(INK[:3], np.float32)
    grid = ((np.abs((_X % 90) - 45) > 44) | (np.abs((_Y % 90) - 45) > 44)).astype(np.float32)[..., None] * 0.05
    c = c + grid * np.array(GREEN[:3], np.float32)
    g = np.exp(-((_X - glow[0]) ** 2 + (_Y - glow[1]) ** 2) / (2 * 420 ** 2))[..., None] * amt
    c = c + g * np.array(GREEN[:3], np.float32)
    v = np.clip(1 - np.hypot((_X - W / 2) / W, (_Y - H / 2) / H) * 0.9, 0, 1)[..., None]
    return np.clip(c * (0.55 + 0.45 * v), 0, 1).astype(np.float32)


def shade(c, top=0.55, amt=0.85):
    g = np.clip((_Y / H - top) / (1 - top), 0, 1)[..., None] ** 1.3
    return c * (1 - amt * g) + np.array(INK[:3], np.float32) * amt * g


def top_shade(c, h=420, amt=0.6):
    g = np.clip(1 - _Y / h, 0, 1)[..., None] ** 1.5
    return c * (1 - amt * g) + np.array(INK[:3], np.float32) * amt * g


# ------------------------------------------------------------------ type
def caption(c, lines, cues=(), y=1560, size=70, x=70, upper=True):
    """Inter Tight Black, left aligned; cue words knocked out of a green HULK box."""
    cues = {q.lower() for q in cues}
    for li, ln in enumerate(lines):
        xx = x
        yy = y + li * size * 1.12
        for w_ in ln.split():
            word = w_.upper() if upper else w_
            m = _wmask(word, HB, size)
            key = w_.strip('.,?!’\'').lower() in cues
            if key:
                bx = rrect(m.shape[1] + size * 0.18, size * 1.08, 6, GREEN)
                draw(c, bx, xx + m.shape[1] / 2, yy + size * 0.04)
                draw(c, solid(m, INK), xx + m.shape[1] / 2, yy)
            else:
                draw(c, blur_sprite(solid(m, (0, 0, 0, 1)), 10), xx + m.shape[1] / 2 + 2, yy + 5, opacity=0.6)
                draw(c, solid(m, WHITE), xx + m.shape[1] / 2, yy)
            xx += m.shape[1] + size * 0.2


def eyebrow(c, text, x=70, y=150, col=GREEN):
    s = ts(text.upper(), 'Hanken-700', 26, col, 0.16)
    draw(c, solid(_wmask('✳', 'Hanken-700', 30), col) if False else rrect(12, 12, 6, col), x + 6, y)
    draw(c, s, x + 26 + s.shape[1] / 2, y)


def service_bar(c, k, y=96):
    """Six-part service bar at the top; segment k (1..6) lit, earlier ones done."""
    x0, x1, gap = 70, 1010, 10
    sw = (x1 - x0 - gap * 5) / 6
    for i in range(6):
        col = GREEN if i < k else (1, 1, 1, 0.18)
        draw(c, rrect(sw, 6, 3, col), x0 + i * (sw + gap) + sw / 2, y)


def chip(c, num, label, x=70, y=230, dark=True):
    n = ts(f'{num:02d}', 'Hanken-700', 28, GREEN, 0.05)
    s = ts(f'/  {label}', 'Hanken-700', 28, WHITE if dark else INK, 0.03)
    w = n.shape[1] + s.shape[1] + 70
    draw(c, rrect(w, 62, 31, (0.04, 0.05, 0.06, 0.78) if dark else (1, 1, 1, 0.9)), x + w / 2, y)
    draw(c, rrect(w - 2, 60, 30, (0.38, 0.83, 0.09, 0.0)), x + w / 2, y)
    draw(c, n, x + 30 + n.shape[1] / 2, y)
    draw(c, s, x + 30 + n.shape[1] + 12 + s.shape[1] / 2, y)


def logo_small(c, x=905, y=150, w=230):
    lg = logo()
    draw(c, lg, x, y, scale=w / lg.shape[1])


def arrow_ne(size=40, col=INK, th=None):
    """North-east arrow (the site's ↗; the web fonts lack the glyph)."""
    n = int(size * 4)
    m = np.zeros((n, n), np.uint8)
    t = int((th or size * 0.14) * 4)
    p0, p1 = (int(n * 0.18), int(n * 0.82)), (int(n * 0.8), int(n * 0.2))
    cv2.line(m, p0, p1, 255, t, cv2.LINE_AA)
    cv2.line(m, p1, (int(n * 0.36), int(n * 0.2)), 255, t, cv2.LINE_AA)
    cv2.line(m, p1, (int(n * 0.8), int(n * 0.64)), 255, t, cv2.LINE_AA)
    return solid(cv2.resize(m, (int(size), int(size)), interpolation=cv2.INTER_AREA).astype(np.float32) / 255, col)


def text_ne(c, text, x, y, font, size, col):
    s = ts(text, font, size, col)
    a = arrow_ne(size * 0.8, col)
    tw = s.shape[1] + 14 + a.shape[1]
    draw(c, s, x - tw / 2 + s.shape[1] / 2, y)
    draw(c, a, x + tw / 2 - a.shape[1] / 2, y - size * 0.04)


# ------------------------------------------------------------------ effects
def burst(c, x, y, r0, r1, n=14, col=GREEN, th=6, seed=0):
    rng = np.random.default_rng(seed)
    lay = np.zeros((H, W), np.uint8)
    for j in range(n):
        a = j / n * 2 * math.pi + rng.uniform(-0.1, 0.1)
        ra, rb = r0 * rng.uniform(0.95, 1.1), r1 * rng.uniform(0.8, 1.15)
        cv2.line(lay, (int((x + math.cos(a) * ra) * 4), int((y + math.sin(a) * ra) * 4)),
                 (int((x + math.cos(a) * rb) * 4), int((y + math.sin(a) * rb) * 4)), 255, th * 4, cv2.LINE_AA, shift=2)
    m = lay.astype(np.float32)[..., None] / 255
    g = cv2.GaussianBlur(m[..., 0], (0, 0), 8)[..., None] * 0.7
    c[:] = np.clip(c + g * np.array(GREEN[:3], np.float32) * 0.8, 0, 1)
    c[:] = c * (1 - m) + np.array(col[:3], np.float32) * m


def ring(c, x, y, r, th=5, col=GREEN, glow=True):
    lay = np.zeros((H, W), np.uint8)
    cv2.circle(lay, (int(x * 4), int(y * 4)), int(r * 4), 255, th * 4, cv2.LINE_AA, shift=2)
    m = lay.astype(np.float32)[..., None] / 255
    if glow:
        g = cv2.GaussianBlur(m[..., 0], (0, 0), 12)[..., None] * 0.9
        c[:] = np.clip(c + g * np.array(GREEN[:3], np.float32) * 0.7, 0, 1)
    c[:] = c * (1 - m) + np.array(col[:3], np.float32) * m


def pop(c, sp, x, y, size=300, rot=0, bursts=True, halo=True, seed=0):
    sc = size / max(sp.shape[:2])
    if halo:
        g = np.exp(-((_X - x) ** 2 + (_Y - y) ** 2) / (2 * (size * 0.55) ** 2))[..., None] * 0.35
        c[:] = np.clip(c + g * np.array(GREEN[:3], np.float32), 0, 1)
    if bursts:
        burst(c, x, y, size * 0.62, size * 0.82, seed=seed)
    draw(c, blur_sprite(tint(sp, (0.0, 0.0, 0.0)), 22), x + 10, y + 30, scale=sc, rot=rot, opacity=0.5)
    draw(c, sp, x, y, scale=sc, rot=rot)


def cracks(c, x, y, n=9, length=700, seed=3, amt=1.0):
    """Green energy veins spreading from a point (the 'flex')."""
    rng = np.random.default_rng(seed)
    lay = np.zeros((H, W), np.uint8)

    def branch(px, py, a, L, w, depth):
        steps = int(L / 18)
        for _ in range(steps):
            a += rng.normal(0, 0.28)
            nx, ny = px + math.cos(a) * 18, py + math.sin(a) * 18
            cv2.line(lay, (int(px * 4), int(py * 4)), (int(nx * 4), int(ny * 4)), 255, max(1, int(w * 4)), cv2.LINE_AA, shift=2)
            px, py = nx, ny
            w *= 0.985
            if depth < 2 and rng.random() < 0.06:
                branch(px, py, a + rng.choice([-1, 1]) * rng.uniform(0.5, 1.0), L * 0.4, w * 0.7, depth + 1)
    for j in range(n):
        branch(x, y, j / n * 2 * math.pi + rng.uniform(-0.2, 0.2), length * rng.uniform(0.6, 1.1), 5, 0)
    m = lay.astype(np.float32)[..., None] / 255 * amt
    g = cv2.GaussianBlur(m[..., 0], (0, 0), 10)[..., None]
    c[:] = np.clip(c + g * np.array(GREEN[:3], np.float32) * 1.1, 0, 1)
    c[:] = np.clip(c * (1 - m) + np.array(LIME[:3], np.float32) * m + m * 0.25, 0, 1)


def card(img, w, h, r=36, border=0, arrow=True):
    m = cv2.resize(R.sdf_fill(R.rrect_alpha(w, h, r, 2)), (w, h))
    pic = F.cover(img, 0.5, 0.5, 1.0, w, h) if img.shape[:2] != (h, w) else img
    out = np.concatenate([pic * m[..., None], m[..., None]], 2).astype(np.float32)
    if arrow:
        a = rrect(64, 64, 32, GREEN)
        paste_spr(out, a, w - 52, 52)
        paste_spr(out, arrow_ne(34, INK), w - 52, 52)
    return out


def put_card(c, img, x, y, w, h, rot=0, arrow=True):
    k = card(img, w, h, arrow=arrow)
    draw(c, blur_sprite(tint(k, (0, 0, 0)), 30), x + 10, y + 30, rot=rot, opacity=0.6)
    draw(c, k, x, y, rot=rot)
    ln = np.zeros((h + 8, w + 8), np.uint8)
    cv2.rectangle(ln, (0, 0), (w + 7, h + 7), 0, -1)


def brackets(c, x, y, w, h, col=GREEN, L=46, th=6):
    lay = np.zeros((H, W), np.uint8)
    for sx in (-1, 1):
        for sy in (-1, 1):
            cx_, cy_ = x + sx * w / 2, y + sy * h / 2
            cv2.line(lay, (int(cx_ * 4), int(cy_ * 4)), (int((cx_ - sx * L) * 4), int(cy_ * 4)), 255, th * 4, cv2.LINE_AA, shift=2)
            cv2.line(lay, (int(cx_ * 4), int(cy_ * 4)), (int(cx_ * 4), int((cy_ - sy * L) * 4)), 255, th * 4, cv2.LINE_AA, shift=2)
    m = lay.astype(np.float32)[..., None] / 255
    c[:] = c * (1 - m) + np.array(col[:3], np.float32) * m


def stamp(c, text, x, y, rot=-8, col=(0.75, 0.77, 0.8, 1)):
    s = solid(_wmask(text, HB, 110), col)
    w, h = s.shape[1] + 60, s.shape[0] + 30
    box = np.zeros((h, w, 4), np.float32)
    m = np.zeros((h, w), np.uint8)
    cv2.rectangle(m, (6, 6), (w - 7, h - 7), 255, 8)
    paste_spr(box, solid(m.astype(np.float32) / 255, col), w / 2, h / 2)
    paste_spr(box, s, w / 2, h / 2)
    rng = np.random.default_rng(2)
    rough = (cv2.GaussianBlur(rng.random((h, w)).astype(np.float32), (0, 0), 1.2) > 0.42).astype(np.float32)
    box *= rough[..., None]
    draw(c, box, x, y, rot=rot, opacity=0.92)


def search_bar(c, text, y=760, x=W / 2, w=920, results=None, hi=0):
    bar = rrect(w, 118, 59, (1, 1, 1, 1))
    draw(c, blur_sprite(tint(bar, (0, 0, 0)), 24), x, y + 16, opacity=0.5)
    draw(c, bar, x, y)
    draw(c, solid(_wmask('G', HB, 54), GREEN), x - w / 2 + 62, y)
    s = ts(text, 'Hanken-500', 44, INK)
    draw(c, s, x - w / 2 + 110 + s.shape[1] / 2, y)
    draw(c, rrect(4, 52, 2, GREEN), x - w / 2 + 120 + s.shape[1], y)
    if results:
        top = y + 110
        panel = rrect(w, 140 * len(results) + 30, 34, (1, 1, 1, 0.97))
        draw(c, panel, x, top + (140 * len(results) + 30) / 2)
        for i, (title, sub) in enumerate(results):
            yy = top + 30 + i * 140 + 55
            if i == hi:
                draw(c, rrect(w - 30, 124, 24, (0.38, 0.83, 0.09, 0.16)), x, yy)
                draw(c, rrect(78, 46, 23, GREEN), x + w / 2 - 80, yy - 22)
                draw(c, ts('#1', HB, 30, INK), x + w / 2 - 80, yy - 22)
            draw(c, ts(title, HB, 40, INK if i == hi else (0.35, 0.37, 0.4, 1)), x - w / 2 + 40 + ts(title, HB, 40, INK).shape[1] / 2, yy - 20)
            draw(c, ts(sub, 'Hanken-500', 28, (0.4, 0.42, 0.45, 1)), x - w / 2 + 40 + ts(sub, 'Hanken-500', 28, INK).shape[1] / 2, yy + 26)


def bubble(c, text, x, y, mine=False, w=None, size=36):
    lines = text.split('\n')
    sps = [ts(l, 'Hanken-700', size, INK if mine else WHITE) for l in lines]
    bw = (w or max(s.shape[1] for s in sps) + 70)
    bh = len(lines) * size * 1.35 + 44
    col = GREEN if mine else (0.16, 0.17, 0.19, 0.96)
    draw(c, blur_sprite(tint(rrect(bw, bh, 34, col), (0, 0, 0)), 16), x + 6, y + 14, opacity=0.5)
    draw(c, rrect(bw, bh, 34, col), x, y)
    for i, s in enumerate(sps):
        draw(c, s, x - bw / 2 + 35 + s.shape[1] / 2, y - bh / 2 + 22 + size * 0.7 + i * size * 1.35)


def site_mock(w=880, h=600):
    """A simple café homepage (generic, made up) shown inside the 3D browser beat."""
    c = np.ones((h, w, 3), np.float32) * np.array([0.97, 0.97, 0.95], np.float32)
    img = vivid(F.cover(frame_of(205, 0.3), 0.5, 0.5, 1.0, w, int(h * 0.58)))
    c[:int(h * 0.58)] = img
    g = np.clip(1 - np.arange(int(h * 0.58))[:, None] / (h * 0.58), 0, 1)[..., None] * 0.0
    out = np.concatenate([c, np.ones((h, w, 1), np.float32)], 2)
    paste_spr(out, rrect(w, 70, 0, (0.03, 0.03, 0.04, 0.8)), w / 2, 35)
    paste_spr(out, ts("SAM'S CAFÉ", HB, 32, WHITE, 0.08), 130, 36)
    for i, t in enumerate(('Menu', 'Order', 'Visit')):
        paste_spr(out, ts(t, 'Hanken-500', 24, WHITE), w - 300 + i * 100, 36)
    paste_spr(out, ts('Freshly roasted,', HB, 56, WHITE), 260, int(h * 0.58) - 140)
    paste_spr(out, ts('five minutes away.', HB, 56, WHITE), 285, int(h * 0.58) - 80)
    paste_spr(out, rrect(240, 64, 32, GREEN), 170, int(h * 0.58) + 70)
    paste_spr(out, ts('Order ahead', HB, 28, INK), 170, int(h * 0.58) + 70)
    for i in range(3):
        paste_spr(out, rrect(250, 120, 18, (0.9, 0.91, 0.88, 1)), 160 + i * 280, h - 80)
    return out


# ------------------------------------------------------------------ scenes (one per voice beat)
def s01():   # "Every day, hundreds of people walk past Sam's café."
    c = clip(15997, 0.35, fy=0.6, mode='grey')
    c = shade(top_shade(c, 380, 0.5), 0.55, 0.85)
    eyebrow(c, 'High street · 8:02 am')
    logo_small(c)
    pop(c, token('cup'), 800, 980, 300)
    draw(c, rrect(260, 64, 32, (1, 1, 1, 0.92)), 800, 1180)
    draw(c, ts("Sam's café", HB, 32, INK), 800, 1180)
    caption(c, ['Every day, hundreds of', 'people walk past', 'Sam’s café.'], cues=('café',), y=1440, size=66)
    return c


def s02():   # "Great coffee. Ordinary marketing."
    c = clip(41856, 0.6, fx=0.55)
    left = c[:, :W // 2].copy()
    c[:, W // 2:] = grey(c[:, W // 2:])
    c = shade(c, 0.6, 0.85)
    lay = np.zeros((H, W), np.float32)
    lay[:, W // 2 - 3:W // 2 + 3] = 1
    c[:] = c * (1 - lay[..., None]) + np.array(GREEN[:3], np.float32) * lay[..., None]
    stamp(c, 'ORDINARY', 760, 900, rot=-9)
    eyebrow(c, 'Great coffee')
    caption(c, ['Great coffee.', 'Ordinary marketing.'], cues=('coffee',), y=1520, size=72)
    return c


def s03():   # "Most of them never even notice it."
    c = clip(4401, 0.45, mode='grey')
    c = shade(top_shade(c, 380, 0.4), 0.58, 0.85)
    for x, y, s in ((300, 840, 120), (620, 900, 110), (840, 760, 100)):
        brackets(c, x, y, s, s * 1.6, col=(0.6, 0.62, 0.65, 1), L=26, th=3)
    pop(c, token('eye'), 760, 520, 280, bursts=False, halo=False)
    draw(c, ts('0 noticed', HB, 40, (0.8, 0.82, 0.85, 1)), 760, 700)
    caption(c, ['Most of them never', 'even notice it.'], cues=('notice',), y=1520, size=72)
    return c


def s04():   # "So Sam called Hulk Marketing."
    c = clip(41174, 0.5, fy=0.42)
    c = shade(c, 0.55, 0.8)
    cracks(c, 820, 560, n=7, length=520, seed=4, amt=0.55)
    ring(c, 820, 560, 230, 6)
    ring(c, 820, 560, 300, 2)
    pop(c, token('phone'), 820, 560, 260, rot=-10, bursts=False)
    draw(c, rrect(980, 200, 30, (0.02, 0.03, 0.03, 0.82)), W / 2, 1260)
    lg = logo()
    draw(c, blur_sprite(tint(lg, GREEN[:3]), 18), W / 2, 1260, scale=880 / lg.shape[1], opacity=0.8)
    draw(c, lg, W / 2, 1260, scale=880 / lg.shape[1])
    caption(c, ['So Sam called', 'Hulk Marketing.'], cues=('hulk', 'marketing'), y=1520, size=72)
    return c


def s05():   # "Strategy, creative, digital and AI, all pulling in the same direction." (the real team)
    c = canvas((W / 2, 820), 0.3)
    names = (('CUT-01-muhammad-abubakar.webp', 'Muhammad', 'Development'), ('CUT-05-ayesha-jahangir.webp', 'Ayesha', 'Generative AI'),
             ('CUT-07-oliver-james-whitmore.webp', 'Oliver', 'Social strategy'), ('CUT-10-ihtisham-adalat.webp', 'Ihtisham', 'Media & production'))
    xs = (190, 430, 660, 890)
    for i, (f, n, role) in enumerate(names):
        sp = cutout(f)
        sc = 760 / sp.shape[0]
        y = 820 + (40 if i % 2 else 0)
        rim = blur_sprite(tint(sp, GREEN[:3]), 10)
        draw(c, rim, xs[i], y, scale=sc * 1.01, opacity=0.6)
        draw(c, sp, xs[i], y, scale=sc)
    for i, (f, n, role) in enumerate(names):
        draw(c, rrect(200, 52, 26, (0.04, 0.05, 0.06, 0.92)), xs[i], 1150)
        draw(c, ts(n, HB, 28, GREEN), xs[i], 1150)
    fade = np.clip((_Y - 1110) / 160, 0, 1)[..., None]
    c[:] = c * (1 - fade * 0.85) + np.array(INK[:3], np.float32) * fade * 0.85
    eyebrow(c, 'Meet the team')
    logo_small(c)
    for i, w_ in enumerate(('Strategy.', 'Creative.', 'Digital.', 'AI.')):
        draw(c, ts(w_, HB, 40, GREEN if w_ == 'AI.' else WHITE), 140 + i * 230, 1300)
    caption(c, ['All pulling in the', 'same direction.'], cues=('same', 'direction'), y=1490, size=72)
    return c


def s06():   # "A website that works harder."
    c = canvas((W / 2, 760), 0.28)
    mock = site_mock()
    put_card(c, mock[..., :3], W / 2, 760, 880, 600, rot=-2, arrow=False)
    pop(c, token('browser'), 800, 360, 320, seed=1)
    service_bar(c, 1)
    chip(c, 1, 'Website')
    draw(c, rrect(360, 70, 35, GREEN), 330, 1160)
    draw(c, ts('+ Order ahead online', HK, 30, INK), 330, 1160)
    caption(c, ['A website that', 'works harder.'], cues=('harder',), y=1500, size=76)
    return c


def s07():   # "Search that puts the café first."
    c = canvas((W / 2, 900), 0.25)
    search_bar(c, 'coffee near me', y=620, results=[("Sam's Café", 'Open now · 0.2 miles'), ('Another café', '0.6 miles'), ('Chain coffee', '1.1 miles')], hi=0)
    pop(c, token('magnifier'), 860, 400, 280, seed=2)
    service_bar(c, 2)
    chip(c, 2, 'Search')
    caption(c, ['Search that puts', 'the café first.'], cues=('first',), y=1500, size=76)
    return c


def s08():   # "Social people actually share."
    c = clip(4919, 0.5, fx=0.45)
    c = shade(top_shade(c, 380, 0.5), 0.58, 0.85)
    pop(c, token('heart'), 790, 620, 300, seed=3)
    for i, (x, y, t) in enumerate(((300, 520, '+128'), (220, 800, 'Shared'), (880, 920, '+46'))):
        draw(c, rrect(ts(t, HB, 34, INK).shape[1] + 50, 62, 31, GREEN if i != 1 else WHITE), x, y)
        draw(c, ts(t, HB, 34, INK), x, y)
    service_bar(c, 3)
    chip(c, 3, 'Social')
    caption(c, ['Social people', 'actually share.'], cues=('share',), y=1500, size=76)
    return c


def s09():   # "Google and Meta ads, aimed at the right people."
    c = clip(6302, 0.4, fy=0.45)
    c = shade(top_shade(c, 380, 0.45), 0.58, 0.85)
    brackets(c, 360, 640, 380, 640)
    brackets(c, 760, 640, 380, 640)
    for x, y, t in ((360, 300, 'Local · 2 miles'), (760, 320, 'Coffee lovers')):
        draw(c, rrect(ts(t, HK, 28, INK).shape[1] + 44, 54, 27, GREEN), x, y)
        draw(c, ts(t, HK, 28, INK), x, y)
    pop(c, token('target'), 840, 1120, 280, seed=4)
    for i, t in enumerate(('Google Ads', 'Meta Ads')):
        draw(c, rrect(220, 58, 29, (1, 1, 1, 0.94)), 180 + i * 240, 1230)
        draw(c, ts(t, HK, 28, INK), 180 + i * 240, 1230)
    service_bar(c, 4)
    chip(c, 4, 'Google & Meta ads')
    caption(c, ['Google and Meta ads,', 'aimed at the right people.'], cues=('right', 'people'), y=1480, size=62)
    return c


def s10():   # "A brand they remember."
    c = clip(205, 0.25, fx=0.4)
    c = shade(top_shade(c, 380, 0.45), 0.58, 0.85)
    pop(c, token('badge'), 760, 640, 320, seed=5)
    pop(c, token('cup'), 330, 860, 260, bursts=False)
    for i, sw in enumerate((GREEN, INK, PAPER, LIME)):
        draw(c, rrect(84, 84, 42, sw), 160 + i * 104, 1220)
        draw(c, rrect(84, 84, 42, (1, 1, 1, 0.0)), 160 + i * 104, 1220)
    draw(c, ts('Aa', HB, 64, WHITE), 620, 1220)
    service_bar(c, 5)
    chip(c, 5, 'Brand')
    caption(c, ['A brand they', 'remember.'], cues=('remember',), y=1500, size=80)
    return c


def s11():   # "And AI that answers, even at midnight."
    c = clip(39782, 0.5, fx=0.42)
    c = shade(top_shade(c, 380, 0.5), 0.5, 0.85)
    bubble(c, 'Are you open tomorrow?', 600, 520, mine=False)
    bubble(c, 'Yes! 7am to 6pm.\nWant to order ahead?', 520, 720, mine=True)
    draw(c, rrect(190, 58, 29, (0.04, 0.05, 0.06, 0.85)), 880, 380)
    draw(c, ts('00:12', HB, 32, GREEN), 880, 380)
    pop(c, token('chatbot'), 850, 1000, 280, seed=6)
    service_bar(c, 6)
    chip(c, 6, 'AI automation')
    caption(c, ['And AI that answers,', 'even at midnight.'], cues=('midnight',), y=1490, size=68)
    return c


def s12():   # "Now the street doesn't walk past. It walks in."
    c = clip(41222, 0.5)
    c = shade(top_shade(c, 380, 0.4), 0.58, 0.85)
    inset = clip(15997, 0.6, w=380, h=520, mode='vivid')
    put_card(c, inset, 270, 560, 380, 520, rot=-3, arrow=False)
    pop(c, token('bell'), 820, 520, 260, rot=12, seed=7)
    draw(c, ts('Ding!', HB, 54, GREEN), 820, 740)
    service_bar(c, 6)
    caption(c, ['Now the street doesn’t', 'walk past.', 'It walks in.'], cues=('walks', 'in'), y=1430, size=66)
    return c


def s13():   # "Anything but ordinary."
    c = canvas((W / 2, 900), 0.45)
    cracks(c, W / 2, 1060, n=10, length=900, seed=9, amt=0.3)
    pop(c, token('asterisk'), W / 2, 520, 300, seed=8)
    for i, (w_, col) in enumerate((('ANYTHING', WHITE), ('BUT', INK), ('ORDINARY.', WHITE))):
        m = _wmask(w_, HB, 168)
        if w_ == 'BUT':
            draw(c, rrect(m.shape[1] + 40, 186, 10, GREEN), W / 2, 880 + i * 175 + 6)
        else:
            draw(c, blur_sprite(solid(m, (0, 0, 0, 1)), 14), W / 2 + 4, 890 + i * 175, opacity=0.8)
        draw(c, solid(m, col), W / 2, 880 + i * 175)
    draw(c, ts('Marketing with muscle.', HK, 40, LIME), W / 2, 1450)
    return c


def s14():   # "Book your free business audit with Hulk Marketing."
    c = canvas((W / 2, 700), 0.3)
    lg = logo()
    draw(c, lg, W / 2, 560, scale=860 / lg.shape[1])
    draw(c, ts('UK digital marketing & creative agency', HK5, 32, (1, 1, 1, 0.75)), W / 2, 680)
    btn = rrect(760, 140, 70, GREEN)
    draw(c, blur_sprite(btn, 30), W / 2, 960, opacity=0.6)
    draw(c, btn, W / 2, 960)
    text_ne(c, 'Free business audit', W / 2, 960, HB, 50, INK)
    draw(c, rrect(760, 110, 55, (1, 1, 1, 0.0)), W / 2, 1110)
    text_ne(c, 'Book a growth consultation', W / 2, 1110, HK, 36, WHITE)
    draw(c, rrect(940, 2, 1, (1, 1, 1, 0.2)), W / 2, 1250)
    draw(c, ts('hulkmarketing.co.uk', HB, 44, GREEN), W / 2, 1330)
    pop(c, token('asterisk'), 900, 1500, 140, bursts=False)
    return c


SCENES = [s01, s02, s03, s04, s05, s06, s07, s08, s09, s10, s11, s12, s13, s14]


if __name__ == '__main__':
    os.makedirs(OUT, exist_ok=True)
    only = [int(a) for a in sys.argv[1:]]
    for j, fn in enumerate(SCENES, start=1):
        if only and j not in only:
            continue
        im = F.to_u8(R.post(fn(), j, bloom=0.16, grain=0.012, vig=0.25))
        cv2.imwrite(f'{OUT}/scene_{j:02d}.png', im)
        print('scene', j, flush=True)
    fs = sorted(glob.glob(f'{OUT}/scene_*.png'))
    th = [cv2.resize(cv2.imread(f), (324, 576)) for f in fs]
    while len(th) % 7:
        th.append(np.zeros_like(th[0]))
    cv2.imwrite(f'{OUT}/storyboard.jpg', np.vstack([np.hstack(th[i:i + 7]) for i in range(0, len(th), 7)]),
                [cv2.IMWRITE_JPEG_QUALITY, 90])
