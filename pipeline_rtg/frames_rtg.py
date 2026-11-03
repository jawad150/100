"""Scene images for Organic Fostering "Room to Grow" (video, people + 3D), after the AI-video concept PDF.

Story: real people out walking at first light (a couple, three generations) -> one of them measures up a spare room ->
the room becomes a 3D cutaway miniature that changes on the voice's cue words (boxes go, a bed, a lamp, empty spaces
left for the child) from morning to dusk -> the landing, door ajar, light on -> end card.

Look (new for this client): label-maker TAPE captions, a wooden HEIGHT-CHART ruler on the left that fills as the room
grows, arch "doorway" frames for footage, dashed PLACEHOLDER outlines on the spaces left for the child, handwritten notes,
and glossy 3D tokens that pop with ring pulses on each spoken object.

Usage: python3 frames_rtg.py [n ...] -> workspace_rtg/frames/scene_XX.png + storyboard.jpg
"""
import os, sys, math, glob
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'pipeline_cf'))
import numpy as np
import cv2
import frames_cf as F
from frames_cf import (R, W, H, draw, blur_sprite, tint, rrect, ts, solid, paste_spr, load_png_sprite, _wmask, PURPLE, ORANGE,
                       PLUM, IVORY, LAV, PEACH, LEAF, WHITE, N9, N8, N7)

ROOT = os.path.abspath(os.path.join(HERE, '..'))
S = f'{ROOT}/workspace_rtg'
OUT = f'{S}/frames'
HAND = 'Caveat-700'
_X, _Y = R._X, R._Y
INK = (0.36, 0.09, 0.31, 1.0)
CREAM = (1.0, 0.975, 0.95, 1.0)
GOLD = (1.0, 0.80, 0.45, 1.0)


def hexf(h):
    h = h.lstrip('#')
    return tuple(int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))


# ------------------------------------------------------------------ sources
def clip(cid, t=0.45, fx=0.5, fy=0.5, z=1.0, w=W, h=H, warm=1.0):
    cap = cv2.VideoCapture(f'{S}/clips/{cid}.mp4')
    cap.set(cv2.CAP_PROP_POS_FRAMES, int(cap.get(cv2.CAP_PROP_FRAME_COUNT) * t))
    ok, im = cap.read()
    out = F.cover(im[..., ::-1].astype(np.float32) / 255, fx, fy, z, w, h)
    return grade(out, warm)


def grade(im, warm=1.0):
    """Golden-morning grade: lifted plum shadows, honey highlights."""
    lum = im.mean(2, keepdims=True)
    sh = np.clip(1 - lum * 2.2, 0, 1)
    hi = np.clip((lum - 0.5) * 2.0, 0, 1)
    im = im * (1 - 0.16 * sh) + np.array([0.30, 0.10, 0.28], np.float32) * 0.16 * sh
    im = im + hi * np.array([0.05, 0.02, -0.03], np.float32) * warm
    im = np.clip((im - 0.5) * 1.04 + 0.52, 0, 1)
    return im.astype(np.float32)


_SPR = {}


def spr(path):
    if path not in _SPR:
        _SPR[path] = load_png_sprite(path)
    return _SPR[path]


def room(state):
    return spr(f'{S}/room/{state}.png')


def token(name):
    for p in (f'{S}/tokens/{name}.png', f'{ROOT}/workspace_yah/assets/{name}.png', f'{ROOT}/workspace_cf/assets/{name}.png',
              f'{ROOT}/workspace_lights/assets/{name}.png'):
        if os.path.exists(p):
            return spr(p)
    raise FileNotFoundError(name)


def still(name, w=W, h=H, fx=0.5, fy=0.5, z=1.0):
    im = cv2.imread(f'{S}/room/{name}.png')[..., ::-1].astype(np.float32) / 255
    return F.cover(im, fx, fy, z, w, h)


# ------------------------------------------------------------------ backdrops
TIMES = {
    'morning': ('#FFF7EF', '#F9DCCB', '#FFE2B8', 0.55),
    'day': ('#FFF4EA', '#F6D3C6', '#FFD0A0', 0.5),
    'warm': ('#FDEBDC', '#F1C2B4', '#FFB877', 0.55),
    'dusk': ('#241B47', '#5E2B5E', '#FF9A5A', 0.35),
}


def backdrop(time='morning', sun=(780, 560), r=380):
    top, bot, glow_c, ga = TIMES[time]
    k = (_Y / H)[..., None]
    c = np.array(hexf(top), np.float32) * (1 - k) + np.array(hexf(bot), np.float32) * k
    g = np.exp(-((_X - sun[0]) ** 2 + (_Y - sun[1]) ** 2) / (2 * r * r))[..., None] * ga
    c = c * (1 - g) + np.array(hexf(glow_c), np.float32) * g
    # soft studio floor: a lighter ellipse where the miniature sits
    fl = np.exp(-(((_X - W / 2) / 620) ** 2 + ((_Y - 1330) / 210) ** 2))[..., None]
    c = c + fl * (0.05 if time != 'dusk' else 0.04)
    if time == 'dusk':
        rng = np.random.default_rng(5)
        for _ in range(90):
            x, y = rng.uniform(0, W), rng.uniform(0, 900)
            rr = rng.uniform(0.8, 2.2)
            m = np.exp(-((_X - x) ** 2 + (_Y - y) ** 2) / (2 * rr * rr))[..., None] * rng.uniform(0.3, 0.9)
            c = c + m * 0.8
    return np.clip(c, 0, 1).astype(np.float32)


def place_room(c, state, cx=W / 2, cy=1080, w=1180, shadow=0.35, opacity=1.0):
    """Draw the cutaway miniature; returns a mapping from room-image px to canvas px."""
    sp = room(state)
    sc = w / sp.shape[1]
    # contact shadow under the slab
    m = np.exp(-(((_X - (cx + 20 * sc)) / (420 * sc)) ** 2 + ((_Y - (cy + 330 * sc)) / (95 * sc)) ** 2))[..., None]
    c[:] = c * (1 - shadow * m * opacity) + np.array([0.25, 0.08, 0.2], np.float32) * shadow * m * opacity
    draw(c, sp, cx, cy, scale=sc, opacity=opacity)

    def at(px, py):
        return cx + (px - sp.shape[1] / 2) * sc, cy + (py - sp.shape[0] / 2) * sc
    return at


# room-image pixel anchors (projected from the Blender camera)
A = dict(frame=(650, 515), shelf=(512, 526), pin=(419, 608), card=(404, 598), lamp=(719, 645), bed=(553, 704),
         window=(833, 580), boxes=(655, 776), rug=(624, 894), door=(373, 677), top=(745, 395))


# ------------------------------------------------------------------ type: label-maker tape captions
def tape_mask(w, h, seed=0, teeth=7):
    m = np.zeros((h * 4, (w + 2 * teeth) * 4), np.uint8)
    rng = np.random.default_rng(seed)
    left = [(teeth * 4 + (rng.uniform(-1, 1) * teeth * 4 if i % 2 else 0), i * h * 4 / 8) for i in range(9)]
    right = [((w + teeth) * 4 + (rng.uniform(-1, 1) * teeth * 4 if i % 2 else 0), i * h * 4 / 8) for i in range(9)][::-1]
    cv2.fillPoly(m, [np.array(left + right, np.int32)], 255, cv2.LINE_AA)
    m = cv2.resize(m, (w + 2 * teeth, h), interpolation=cv2.INTER_AREA).astype(np.float32) / 255
    return m


def tape_line(c, words, cues, x, y, size=66, fill=CREAM, ink=INK, rot=0.0, seed=0, opacity=1.0, center=False):
    """One caption line on a strip of tape; cue words get a second, orange strip and white ink."""
    gap = size * 0.24
    sprs = [_wmask(w_, N9, size) for w_ in words]
    tw = sum(s.shape[1] for s in sprs) + gap * (len(words) - 1)
    padx, h = size * 0.42, int(size * 1.42)
    sw = int(tw + padx * 2)
    strip = np.zeros((h + 40, sw + 60, 4), np.float32)
    tm = tape_mask(sw, h, seed)
    paste_spr(strip, solid(tm, fill), strip.shape[1] / 2, strip.shape[0] / 2)
    xx = (strip.shape[1] - sw) / 2 + padx
    for w_, s in zip(words, sprs):
        key = w_.strip('.,?!’\'').lower() in cues
        cx_ = xx + s.shape[1] / 2
        if key:
            km = tape_mask(int(s.shape[1] + size * 0.3), int(size * 1.12), seed + 3, teeth=5)
            paste_spr(strip, solid(km, ORANGE), cx_, strip.shape[0] / 2 + 2)
        paste_spr(strip, solid(s, WHITE if key else ink), cx_, strip.shape[0] / 2 + size * 0.04)
        xx += s.shape[1] + gap
    px = x if center else x + strip.shape[1] / 2 - 30
    draw(c, blur_sprite(tint(strip, (0.25, 0.05, 0.2)), 12), px + 4, y + 12, rot=rot, opacity=0.35 * opacity)
    draw(c, strip, px, y, rot=rot, opacity=opacity)
    return strip.shape[1]


def captions(c, lines, cues=(), y=1560, size=66, x=70, center=False, dark=False):
    cues = {q.lower() for q in cues}
    for i, ln in enumerate(lines):
        rot = (-1.6, 1.2, -0.8, 1.4)[i % 4]
        fill = (0.16, 0.1, 0.24, 0.92) if dark else CREAM
        ink = (1, 0.96, 0.92, 1) if dark else INK
        tape_line(c, ln.split(), cues, (W / 2 if center else x + i * 18), y + i * size * 1.5, size, fill, ink, rot, seed=i + len(ln),
                  center=center)


def hand(c, s, x, y, size=64, col=PURPLE, rot=0, anchor='c'):
    sp = solid(_wmask(s, HAND, size), col)
    draw(c, sp, x + (sp.shape[1] / 2 if anchor == 'l' else 0), y, rot=rot)
    return sp.shape[1]


def eyebrow(c, text='ROOM TO GROW', x=70, y=150, dark=False):
    s = ts(text, 'Poppins-SemiBold', 26, WHITE if dark else PLUM, 0.18)
    dot = rrect(14, 14, 7, ORANGE)
    draw(c, dot, x + 7, y)
    draw(c, s, x + 30 + s.shape[1] / 2, y)


# ------------------------------------------------------------------ motifs
def ruler(c, k, dark=False):
    """Wooden height chart on the left edge; the magenta-to-orange fill grows with the story (k 0..1)."""
    x0, y0, y1, wdt = 22, 330, 1610, 40
    wood = np.array(hexf('#E9C9A0') if not dark else hexf('#8E6A55'), np.float32)
    lay = np.zeros((H, W), np.float32)
    lay[y0:y1, x0:x0 + wdt] = 1
    lay = cv2.GaussianBlur(lay, (0, 0), 0.8)[..., None] * 0.92
    c[:] = c * (1 - lay) + wood * lay
    fy = int(y1 - (y1 - y0) * k)
    if k > 0:
        u = np.clip((_Y - y0) / (y1 - y0), 0, 1)[..., None]
        col = np.array(PURPLE[:3], np.float32) * (1 - u) + np.array(ORANGE[:3], np.float32) * u
        m = np.zeros((H, W), np.float32)
        m[fy:y1, x0 + 26:x0 + wdt] = 1
        m = m[..., None]
        c[:] = c * (1 - m) + col * m
    tick = np.zeros((H, W), np.uint8)
    for i, yy in enumerate(range(y1, y0, -32)):
        L = 20 if i % 5 == 0 else 11
        cv2.line(tick, (x0, yy), (x0 + L, yy), 255, 2, cv2.LINE_AA)
    t = tick.astype(np.float32)[..., None] / 255 * 0.75
    c[:] = c * (1 - t) + np.array(PLUM[:3], np.float32) * t
    if k > 0:
        draw(c, rrect(54, 8, 4, PLUM if not dark else WHITE), x0 + wdt / 2 + 4, fy)


def dashed_rect(c, x, y, w, h, col=PURPLE, dash=18, gap=12, th=4, r=14, glow=True):
    lay = np.zeros((H, W), np.uint8)
    per = []
    for (ax, ay, bx, by) in ((x - w / 2 + r, y - h / 2, x + w / 2 - r, y - h / 2), (x + w / 2, y - h / 2 + r, x + w / 2, y + h / 2 - r),
                             (x + w / 2 - r, y + h / 2, x - w / 2 + r, y + h / 2), (x - w / 2, y + h / 2 - r, x - w / 2, y - h / 2 + r)):
        L = math.hypot(bx - ax, by - ay)
        n = int(L // (dash + gap)) + 1
        for i in range(n):
            s0 = i * (dash + gap) / L
            s1 = min(1, (i * (dash + gap) + dash) / L)
            if s0 >= 1:
                break
            per.append(((ax + (bx - ax) * s0, ay + (by - ay) * s0), (ax + (bx - ax) * s1, ay + (by - ay) * s1)))
    for p, q in per:
        cv2.line(lay, (int(p[0] * 4), int(p[1] * 4)), (int(q[0] * 4), int(q[1] * 4)), 255, th * 4, cv2.LINE_AA, shift=2)
    for cx_, cy_, a0 in ((x - w / 2 + r, y - h / 2 + r, 180), (x + w / 2 - r, y - h / 2 + r, 270), (x + w / 2 - r, y + h / 2 - r, 0), (x - w / 2 + r, y + h / 2 - r, 90)):
        cv2.ellipse(lay, (int(cx_ * 4), int(cy_ * 4)), (int(r * 4), int(r * 4)), 0, a0, a0 + 90, 255, th * 4, cv2.LINE_AA, shift=2)
    m = lay.astype(np.float32)[..., None] / 255
    if glow:
        g = cv2.GaussianBlur(m[..., 0], (0, 0), 7)[..., None] * 0.6
        c[:] = c * (1 - g) + np.array(WHITE[:3], np.float32) * g
    c[:] = c * (1 - m) + np.array(col[:3], np.float32) * m


def leader(c, p, q, col=PLUM, th=3, dot=True):
    lay = np.zeros((H, W), np.uint8)
    mid = ((p[0] + q[0]) / 2, min(p[1], q[1]) - 40)
    pts = [((1 - t) ** 2 * p[0] + 2 * (1 - t) * t * mid[0] + t * t * q[0], (1 - t) ** 2 * p[1] + 2 * (1 - t) * t * mid[1] + t * t * q[1])
           for t in np.linspace(0, 1, 40)]
    cv2.polylines(lay, [(np.array(pts) * 4).astype(np.int32)], False, 255, th * 4, cv2.LINE_AA, shift=2)
    if dot:
        cv2.circle(lay, (int(p[0] * 4), int(p[1] * 4)), 9 * 4, 255, -1, cv2.LINE_AA, shift=2)
    m = lay.astype(np.float32)[..., None] / 255
    c[:] = c * (1 - m) + np.array(col[:3], np.float32) * m
    if dot:
        draw(c, rrect(9, 9, 4.5, WHITE), p[0], p[1])


def sparkle(c, x, y, s=26, col=GOLD):
    m = np.zeros((int(s * 8), int(s * 8)), np.uint8)
    cc = s * 4
    pts = []
    for i in range(8):
        a = i * math.pi / 4
        rr = cc * (1 if i % 2 == 0 else 0.22)
        pts.append((cc + math.cos(a) * rr, cc + math.sin(a) * rr))
    cv2.fillPoly(m, [np.array(pts, np.int32)], 255, cv2.LINE_AA)
    sp = solid(cv2.resize(m, (int(s * 2), int(s * 2)), interpolation=cv2.INTER_AREA).astype(np.float32) / 255, col)
    draw(c, blur_sprite(sp, 6), x, y, opacity=0.8)
    draw(c, sp, x, y)


def pop(c, sp, x, y, size=300, rings=True, rot=0, sparks=True, col=ORANGE):
    """3D token with ring pulses (two thin rings) and sparkles."""
    sc = size / max(sp.shape[:2])
    if rings:
        lay = np.zeros((H, W), np.uint8)
        r0 = size * 0.62
        cv2.circle(lay, (int(x * 4), int(y * 4)), int(r0 * 4), 255, 5 * 4, cv2.LINE_AA, shift=2)
        cv2.circle(lay, (int(x * 4), int(y * 4)), int(r0 * 1.22 * 4), 255, 2 * 4, cv2.LINE_AA, shift=2)
        m = lay.astype(np.float32)[..., None] / 255
        m[..., 0] *= 0.85
        cc = np.array(col[:3], np.float32)
        c[:] = c * (1 - m) + cc * m
    draw(c, blur_sprite(tint(sp, (0.3, 0.06, 0.22)), 22), x + 10, y + 30, scale=sc, rot=rot, opacity=0.38)
    draw(c, sp, x, y, scale=sc, rot=rot)
    if sparks:
        for dx, dy, s in ((0.58, -0.5, 22), (-0.62, -0.28, 15), (0.48, 0.55, 13)):
            sparkle(c, x + dx * size, y + dy * size, s)


def arch(img, w, h, border=16):
    """Footage in an arched doorway frame (premultiplied sprite with an ivory border)."""
    m = np.zeros((h * 2, w * 2), np.uint8)
    rr = w
    cv2.rectangle(m, (0, rr), (w * 2, h * 2), 255, -1)
    cv2.circle(m, (w, rr), rr, 255, -1, cv2.LINE_AA)
    m = cv2.resize(m, (w, h), interpolation=cv2.INTER_AREA).astype(np.float32) / 255
    inner = cv2.erode(m, np.ones((border * 2 + 1, border * 2 + 1), np.uint8))
    inner = cv2.GaussianBlur(inner, (0, 0), 0.8)
    pic = F.cover(img, 0.5, 0.5, 1.0, w, h)
    rgb = pic * inner[..., None] + np.array(CREAM[:3], np.float32) * (m - inner)[..., None]
    return np.concatenate([rgb * 1.0, m[..., None]], 2).astype(np.float32)


def put_arch(c, img, x, y, w, h, rot=0):
    a = arch(img, w, h)
    draw(c, blur_sprite(tint(a, (0.25, 0.05, 0.18)), 26), x + 8, y + 26, rot=rot, opacity=0.45)
    draw(c, a, x, y, rot=rot)


def logo_small(c, x=930, y=150, w=200, white=False):
    lg = F.logo()
    if white:
        a = lg[..., 3:4]
        lg = np.concatenate([np.ones_like(lg[..., :3]) * a, a], 2)
    draw(c, lg, x, y, scale=w / lg.shape[1])


def top_veil(c, h=420, amt=0.55, col=(1, 0.97, 0.94)):
    g = np.clip(1 - _Y / h, 0, 1)[..., None] ** 1.6
    c[:] = c * (1 - amt * g) + np.array(col, np.float32) * amt * g


def bottom_veil(c, top=0.62, amt=0.75, col=PLUM):
    c[:] = F.shade(c, top, amt, col)


def blur_room_ghost(c, state, at_fn, k=0.5):
    pass


def raw_clip(cid, t):
    cap = cv2.VideoCapture(f'{S}/clips/{cid}.mp4')
    cap.set(cv2.CAP_PROP_POS_FRAMES, int(cap.get(cv2.CAP_PROP_FRAME_COUNT) * t))
    ok, im = cap.read()
    return grade(im[..., ::-1].astype(np.float32) / 255)


# ------------------------------------------------------------------ scenes (one per voice beat)
def s01():   # "A small beginning…"
    c = clip(939, 0.35, fx=0.5, fy=0.55)
    top_veil(c, 380, 0.35, (1.0, 0.85, 0.7))
    bottom_veil(c, 0.58, 0.8)
    eyebrow(c, dark=True)
    pop(c, token('seedling'), 790, 1080, 300)
    hand(c, 'it starts small', 790, 1350, 58, GOLD, rot=-5)
    captions(c, ['A small beginning'], cues=('small', 'beginning'), y=1560)
    ruler(c, 0.04)
    return c


def s02():   # "…can change the direction of a life."
    c = clip(6472, 0.55, fx=0.5, fy=0.6)
    top_veil(c, 380, 0.3, (1.0, 0.8, 0.6))
    bottom_veil(c, 0.55, 0.8)
    eyebrow(c, dark=True)
    # dashed path curving off to a new direction
    lay = np.zeros((H, W), np.uint8)
    pts = [(120 + t * 760, 1260 - math.sin(t * math.pi * 0.9) * 340) for t in np.linspace(0, 1, 60)]
    for i in range(0, 58, 3):
        cv2.line(lay, (int(pts[i][0] * 4), int(pts[i][1] * 4)), (int(pts[i + 1][0] * 4), int(pts[i + 1][1] * 4)), 255, 8 * 4, cv2.LINE_AA, shift=2)
    m = lay.astype(np.float32)[..., None] / 255
    c[:] = c * (1 - m) + np.array(GOLD[:3], np.float32) * m
    pop(c, token('compass'), 840, 880, 270)
    captions(c, ['can change the', 'direction of a life.'], cues=('direction', 'life'), y=1500)
    ruler(c, 0.1)
    return c


def s03():   # "For a child coming into care,"
    c = backdrop('morning', (760, 520))
    put_arch(c, raw_clip(23392, 0.25), W / 2 + 30, 820, 760, 1000, rot=1.2)
    # measuring annotation
    lay = np.zeros((H, W), np.uint8)
    cv2.line(lay, (170 * 4, 1390 * 4), (930 * 4, 1390 * 4), 255, 4 * 4, cv2.LINE_AA, shift=2)
    for xx in (170, 930):
        cv2.line(lay, (xx * 4, 1365 * 4), (xx * 4, 1415 * 4), 255, 4 * 4, cv2.LINE_AA, shift=2)
    m = lay.astype(np.float32)[..., None] / 255
    c[:] = c * (1 - m) + np.array(PURPLE[:3], np.float32) * m
    hand(c, 'measuring up the spare room', W / 2 + 20, 1350, 52, PURPLE, rot=-1.5)
    eyebrow(c)
    logo_small(c)
    captions(c, ['For a child', 'coming into care,'], cues=('child',), y=1530)
    ruler(c, 0.16)
    return c


def s04():   # "it can start with a…"
    c = backdrop('morning')
    at = place_room(c, 's1', cy=1000)
    # blueprint dimension callouts
    hand(c, 'the boxroom', 300, 520, 70, PURPLE, rot=-6)
    leader(c, at(*A['boxes']), (330, 580))
    eyebrow(c)
    logo_small(c)
    captions(c, ['it can start', 'with a room.'], cues=('room',), y=1560)
    ruler(c, 0.24)
    return c


def s05():   # "…room." the time-lapse clear (people packing, boxes fly out)
    c = backdrop('morning', (700, 480))
    at = place_room(c, 's2', cy=1060)
    # ghost boxes lifting out of the room, motion trails
    rs = room('s1')
    diff = np.abs(room('s1')[..., :3] - room('s2')[..., :3]).sum(2)
    m = (cv2.GaussianBlur((diff > 0.18).astype(np.float32), (0, 0), 3) > 0.3).astype(np.float32)
    ys, xs = np.where(m[520:1000, 450:900] > 0)
    ghost = rs * m[..., None]
    gs = 1180 / rs.shape[1]
    for k, (dy, op) in enumerate(((-160, 0.18), (-320, 0.12), (-470, 0.07))):
        draw(c, blur_sprite(ghost, 2 + k * 3), W / 2 + k * 40, 1060 + dy, scale=gs, opacity=op)
    put_arch(c, raw_clip(31218, 0.6), 290, 470, 400, 540, rot=-3)
    put_arch(c, raw_clip(2296, 0.5), 790, 420, 360, 480, rot=3)
    hand(c, 'cleared', 300, 790, 60, PURPLE, rot=-4)
    hand(c, 'freshened', 800, 720, 60, PURPLE, rot=4)
    captions(c, ['…with a room.'], cues=('room',), y=1600)
    ruler(c, 0.32)
    return c


def s06():   # "A made bed."
    c = backdrop('day')
    at = place_room(c, 's3', cy=1000, w=1250)
    bx, by = at(*A['bed'])
    for dx, dy, s in ((-150, -130, 30), (120, -170, 22), (190, -40, 16), (-210, 30, 14)):
        sparkle(c, bx + dx, by + dy, s)
    hand(c, 'fresh sheets', bx - 230, by - 260, 60, PURPLE, rot=-6)
    leader(c, (bx - 40, by - 20), (bx - 210, by - 220))
    eyebrow(c)
    logo_small(c)
    captions(c, ['A made bed.'], cues=('bed',), y=1600)
    ruler(c, 0.4)
    return c


def s07():   # "A lamp left on."
    c = backdrop('warm', (760, 900), 420)
    at = place_room(c, 's4', cy=1060, w=1250)
    lx, ly = at(*A['lamp'])
    g = np.exp(-((_X - lx) ** 2 + (_Y - ly) ** 2) / (2 * 120 ** 2))[..., None] * 0.35
    c[:] = c * (1 - g) + np.array([1.0, 0.8, 0.5], np.float32) * g
    put_arch(c, raw_clip(46393, 0.75), 300, 460, 400, 540, rot=-2.5)
    hand(c, 'click.', 600, 400, 84, ORANGE, rot=-8)
    leader(c, (lx, ly - 30), (560, 470), col=ORANGE)
    eyebrow(c)
    captions(c, ['A lamp left on.'], cues=('lamp',), y=1600)
    ruler(c, 0.48)
    return c


def s08():   # "A place to belong."
    c = backdrop('warm', (W / 2, 900), 520)
    at = place_room(c, 's4', cy=980, w=1060)
    # soft heart drawn around the room
    lay = np.zeros((H, W), np.uint8)
    t = np.linspace(0, 2 * math.pi, 300)
    hx = 16 * np.sin(t) ** 3
    hy = -(13 * np.cos(t) - 5 * np.cos(2 * t) - 2 * np.cos(3 * t) - np.cos(4 * t))
    pts = np.stack([W / 2 + hx * 31, 960 + hy * 31], 1)
    cv2.polylines(lay, [(pts * 4).astype(np.int32)], True, 255, 6 * 4, cv2.LINE_AA, shift=2)
    m = lay.astype(np.float32)[..., None] / 255
    g = cv2.GaussianBlur(m[..., 0], (0, 0), 10)[..., None] * 0.5
    c[:] = c * (1 - g) + np.array(WHITE[:3], np.float32) * g
    u = np.clip(_X / W, 0, 1)[..., None]
    col = np.array(PURPLE[:3], np.float32) * (1 - u) + np.array(ORANGE[:3], np.float32) * u
    c[:] = c * (1 - m) + col * m
    pop(c, token('house'), 880, 470, 220, rings=False)
    eyebrow(c)
    captions(c, ['A place to belong.'], cues=('belong',), y=1600)
    ruler(c, 0.56)
    return c


def s09():   # "And some things you leave for them."
    c = still('frame')
    c = grade(c, 0.6)
    top_veil(c, 300, 0.25)
    bottom_veil(c, 0.66, 0.7)
    dashed_rect(c, 452, 672, 560, 460, PURPLE, r=10)
    hand(c, 'left for them', 470, 960, 80, PURPLE, rot=-3)
    eyebrow(c)
    captions(c, ['And some things', 'you leave for them.'], cues=('them',), y=1490)
    ruler(c, 0.64)
    return c


def s10():   # "Their pictures. Their books. Their name on the door."
    c = backdrop('warm', (W / 2, 760), 460)
    at = place_room(c, 's5', cy=1080, w=1250)
    for key, w_, h_ in (('frame', 92, 74), ('shelf', 120, 40), ('card', 46, 44)):
        x, y = at(*A[key])
        dashed_rect(c, x, y, w_, h_, PURPLE, dash=9, gap=6, th=3, r=6)
    spots = (('frame', 'frame', 'Their pictures.', 820, 430), ('shelf', 'books', 'Their books.', 420, 440), ('card', 'doortag', 'Their name.', 190, 820))
    for key, tok, label, tx, ty in spots:
        x, y = at(*A[key])
        leader(c, (x, y), (tx, ty + 90), col=PLUM)
        pop(c, token(tok), tx, ty, 240, rings=False, sparks=True)
    eyebrow(c)
    captions(c, ['Their pictures. Their books.', 'Their name on the door.'], cues=('pictures', 'books', 'name'), y=1560, size=58)
    ruler(c, 0.72)
    return c


def s11():   # "At Organic Fostering, matching sees the whole child."
    c = backdrop('dusk', (760, 620), 380)
    at = place_room(c, 's6', cy=1060, w=1180, shadow=0.5)
    pop(c, token('puzzle'), W / 2 + 10, 440, 340, col=GOLD)
    hand(c, 'the whole child', W / 2, 640, 70, GOLD, rot=-3)
    eyebrow(c, dark=True)
    logo_small(c, white=True)
    captions(c, ['At Organic Fostering,', 'matching sees the whole child.'], cues=('matching', 'whole', 'child'), y=1530, size=56, dark=True)
    ruler(c, 0.8, dark=True)
    return c


def s12():   # "Culture, faith, language, relationships and identity matter."
    c = backdrop('dusk', (W / 2, 900), 460)
    at = place_room(c, 's6', cy=1000, w=820, shadow=0.5)
    items = (('globe', 'Culture'), ('lantern', 'Faith'), ('speech', 'Language'), ('rings', 'Relationships'), ('fingerprint', 'Identity'))
    cx, cy, rx, ry = W / 2, 930, 410, 520
    for i, (tok, lab) in enumerate(items):
        a = math.radians(-90 + i * 72 - 36 + 36)
        a = math.radians(-160 + i * 70)
        x, y = cx + math.cos(a) * rx, cy + math.sin(a) * ry * 0.78 - 60
        pop(c, token(tok), x, y, 170, rings=True, sparks=False, col=GOLD)
        s = ts(lab, N9, 36, WHITE)
        draw(c, rrect(s.shape[1] + 34, 54, 27, (0.72, 0.0, 0.43, 0.92)), x, y + 118)
        draw(c, s, x, y + 118)
    eyebrow(c, dark=True)
    captions(c, ['Culture, faith, language,', 'relationships and identity', 'matter.'], cues=('matter',), y=1430, size=56, dark=True)
    ruler(c, 0.88, dark=True)
    return c


def s13():   # "You don't need every answer before you call."
    c = still('landing')
    c = grade(c, 1.0)
    g = np.exp(-((_X - 640) ** 2 + (_Y - 1250) ** 2) / (2 * 330 ** 2))[..., None] * 0.22
    c[:] = c * (1 - g) + np.array([1.0, 0.75, 0.45], np.float32) * g
    put_arch(c, raw_clip(39803, 0.3), 300, 520, 380, 520, rot=-2)
    pop(c, token('phone'), 800, 470, 230, col=GOLD)
    eyebrow(c, dark=True)
    captions(c, ['You don’t need every answer', 'before you call.'], cues=('call',), y=1500, size=56, dark=True)
    ruler(c, 0.95, dark=True)
    return c


def s14():   # "Start your enquiry with Organic Fostering." end card over the landing
    c = still('landing')
    c = grade(c, 1.0)
    c = cv2.GaussianBlur(c, (0, 0), 6)
    cw, ch = 940, 1080
    card = rrect(cw, ch, 48, CREAM)
    draw(c, blur_sprite(tint(card, (0.1, 0.02, 0.08)), 40), W / 2, 960 + 30, opacity=0.6)
    draw(c, card, W / 2, 960)
    lg = F.logo()
    draw(c, lg, W / 2, 610, scale=620 / lg.shape[1])
    hand(c, 'there’s room to grow', W / 2, 800, 74, ORANGE, rot=-3)
    draw(c, ts('You don’t need every answer', N9, 46, PLUM), W / 2, 905)
    draw(c, ts('before you call.', N9, 46, PLUM), W / 2, 965)
    btn = F.grad_spr(700, 124, 62)
    draw(c, blur_sprite(btn, 22), W / 2, 1110 + 18, opacity=0.5)
    draw(c, btn, W / 2, 1110)
    F.text_arrow(c, 'Start your enquiry', W / 2, 1110, size=50)
    draw(c, rrect(cw - 140, 2, 1, (0.36, 0.09, 0.31, 0.25)), W / 2, 1250)
    s1 = ts('organicfostering.co.uk', N8, 34, PLUM)
    s2 = ts('0161 241 1332', N9, 38, PURPLE)
    draw(c, s1, W / 2 - cw / 2 + 70 + s1.shape[1] / 2, 1320)
    draw(c, s2, W / 2 + cw / 2 - 70 - s2.shape[1] / 2, 1320)
    pop(c, token('doortag'), 860, 1520, 170, rings=False, sparks=False, rot=8)
    return c


SCENES = [s01, s02, s03, s04, s05, s06, s07, s08, s09, s10, s11, s12, s13, s14]


if __name__ == '__main__':
    os.makedirs(OUT, exist_ok=True)
    only = [int(a) for a in sys.argv[1:]]
    for j, fn in enumerate(SCENES, start=1):
        if only and j not in only:
            continue
        im = F.to_u8(R.post(fn(), j, bloom=0.12, grain=0.012, vig=0.22))
        cv2.imwrite(f'{OUT}/scene_{j:02d}.png', im)
        print('scene', j, flush=True)
    fs = sorted(glob.glob(f'{OUT}/scene_*.png'))
    th = [cv2.resize(cv2.imread(f), (324, 576)) for f in fs]
    while len(th) % 7:
        th.append(np.zeros_like(th[0]))
    cv2.imwrite(f'{OUT}/storyboard.jpg', np.vstack([np.hstack(th[i:i + 7]) for i in range(0, len(th), 7)]),
                [cv2.IMWRITE_JPEG_QUALITY, 90])
