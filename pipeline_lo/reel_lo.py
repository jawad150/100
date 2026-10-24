"""Organic Fostering — "Leave the Light On" (9:16, 30 s): emergency fostering on a rainy night.

Cinematic motion-graphics cut: Blender 3D rainy terraced street (drone push, porch light clicks on) -> 9:47pm call on a
3D phone in a warm kitchen -> "getting ready" montage (OF footage) with a ticking clock chip and a live checklist card ->
the arrival (the brand key visual in 2.5D parallax, neon heart glowing, captions) -> 3D clay payoff (tiny pink wellies
beside big slippers by the radiator) -> camera rises from the porch into the rain -> gradient end card.
Trending touches: word-by-word highlighted captions, rain on the lens, warm-vs-cold grade, beat-cut montage.

Usage:
  python3 reel_lo.py still 1.0,5.0
  python3 reel_lo.py range 0 900
"""
import os, sys, math, functools
HERE = os.path.dirname(os.path.abspath(__file__))
os.environ['REEL_WORKDIR'] = os.path.abspath(os.path.join(HERE, '..', 'workspace_lo'))
sys.path.insert(0, os.path.join(HERE, '..', 'pipeline_su'))
import numpy as np
import cv2
import reel_su as RS
from reel_su import paste, fitted, png, phone_body, screen_mask, draw_phone, PW, PH, SW, SH, PB, PX, PK, PS, PM, PL
from reel_of import (kinetic_line, word_spr, sweep, glow_add, whip, zoom_blur, shake, check_spr, rrect_spr, glass,
                     clip_frame, PLUM, MAGENTA, ORANGE_B, GREEN, PEACH, MUTEDC)
from engine import *  # noqa: F401,F403
import engine as E

S = E.S
FPS = 30
WHITE_ = (1.0, 1.0, 1.0, 1.0)
INK = hexc('#2B0B27')
WARM = hexc('#FFB45E')
GOLD = hexc('#FFD54A')
HL = hexc('#FFC24D')

# ------------------------------------------------------------------ timeline
T = dict(hook=0.0, call=3.3, ready=7.4, arrive=15.2, payoff=18.2, rise=22.9, end=26.0)
DUR = 30.0
NF = int(DUR * FPS)
VO = {'call': 3.45, 'ready': 8.25, 'never': 18.0, 'cta': 23.2}
PHRASES = {   # (line, phrase onset within line, text) for word-by-word captions
    'call': [(0.05, 'Sometimes a child needs somewhere safe…'), (3.54, 'tonight.')],
    'ready': [(0.03, 'Emergency foster carers'), (1.10, 'get ready at short notice…')],
    'never': [(0.04, 'and with advice outside normal hours,'), (3.14, "you're never on your own.")],
    'cta': [(0.04, 'Could you leave the light on?'), (2.32, 'Start the conversation with Organic Fostering.')],
}
LINE_DUR = {'call': 4.53, 'ready': 4.46, 'never': 5.01, 'cta': 5.58}
CLICK = 2.2                      # porch light clicks on (hook render is 3 s, stretched to 3.3 s)
ANSWER = T['call'] + 1.1
SHOTS = [(1, 1.4, 'Fresh sheets on the bed'), (6, 1.2, 'Nightlight on, teddy ready'),
         (5, 1.4, 'Something warm to eat'), (3, 1.0, 'Space by the door')]
SHOT_LEN = (T['arrive'] - T['ready']) / 4
FADE = 1.15

SEQ = {}


def seq(name, fps=24, loop=False):
    if name not in SEQ:
        SEQ[name] = Seq(name, fps=fps, loop=loop)
    return SEQ[name]


@functools.lru_cache(maxsize=8)
def img(name, flag=cv2.IMREAD_COLOR):
    im = cv2.imread(f'{S}/src/{name}', flag)
    if flag == cv2.IMREAD_COLOR:
        return im[..., ::-1].astype(np.float32) / 255.0
    return im.astype(np.float32) / 255.0


def txt(canvas, s, x, y, size, color, fname=PS, op=1.0, ax=0.5, shadow_op=0.0):
    spr = word_spr(s, fname, size, color)
    if op <= 0:
        return spr
    if shadow_op > 0:
        sh = blur_sprite(tint(spr, (0.03, 0.0, 0.03)), 10)
        draw(canvas, sh, x, y + 6, opacity=shadow_op * op, ax=ax)
    draw(canvas, spr, x, y, opacity=op, ax=ax)
    return spr


# ------------------------------------------------------------------ atmosphere: rain + lens drops + grade
_rng = np.random.default_rng(12)
RAIN = [(_rng.uniform(0, W), _rng.uniform(0, H), _rng.uniform(900, 1700), _rng.uniform(30, 80), _rng.uniform(0.15, 0.5))
        for _ in range(260)]
DROPS = [(_rng.uniform(0, W), _rng.uniform(0, H), _rng.uniform(6, 22), _rng.uniform(0, 30)) for _ in range(40)]


def rain(c, t, amt=1.0, col=(0.75, 0.82, 1.0)):
    if amt <= 0:
        return c
    m = np.zeros((H // 2, W // 2), np.float32)
    for x, y, sp, ln, a in RAIN:
        yy = (y + t * sp) % (H + 200) - 100
        xx = (x + t * sp * 0.12) % W
        cv2.line(m, (int(xx / 2), int(yy / 2)), (int((xx + ln * 0.12) / 2), int((yy + ln) / 2)), a, 1, cv2.LINE_AA)
    m = cv2.resize(m, (W, H))[..., None] * amt
    return c + m * np.array(col, np.float32) * 0.5


def lens_drops(c, t, amt=1.0):
    if amt <= 0:
        return c
    out = c
    for x, y, r, t0 in DROPS:
        age = (t + t0) % 8.0
        if age > 6:
            continue
        yy = y + max(0, age - 4) * 60
        x0, y0 = int(x - r * 2), int(yy - r * 2)
        x1, y1 = int(x + r * 2), int(yy + r * 2)
        if x0 < 0 or y0 < 0 or x1 >= W or y1 >= H:
            continue
        patch = out[y0:y1, x0:x1]
        flipped = cv2.GaussianBlur(patch[::-1, ::-1], (0, 0), 1.2)
        mm = np.zeros(patch.shape[:2], np.float32)
        cv2.circle(mm, (patch.shape[1] // 2, patch.shape[0] // 2), int(r), 1.0, -1, cv2.LINE_AA)
        mm = cv2.GaussianBlur(mm, (0, 0), 1.0)[..., None] * 0.85 * amt
        out[y0:y1, x0:x1] = patch * (1 - mm) + (flipped * 1.08 + 0.03) * mm
    return out


def night(c, warm=0.0):
    """Cold blue night grade, with optional warm (tungsten) push."""
    lum = c.mean(axis=2, keepdims=True)
    cold = c * 0.6 + lum * np.array([0.25, 0.32, 0.5], np.float32)
    w_ = c * np.array([1.08, 0.94, 0.78], np.float32)
    return np.clip(cold * (1 - warm) + w_ * warm, 0, 1)


_yy = np.linspace(0, 1, H, dtype=np.float32)[:, None, None]


def title_band(c, y0, y1, a=0.8):
    """Soft dark band behind a headline block (keeps warm text readable over lit windows / bright walls)."""
    ys = np.linspace(0, H, H, dtype=np.float32)[:, None, None]
    mid, half = (y0 + y1) / 2, (y1 - y0) / 2
    m = np.clip(1 - np.abs(ys - mid) / (half + 140), 0, 1) ** 0.8 * a
    return c * (1 - m) + np.array([0.03, 0.01, 0.03], np.float32) * m


def scrim(c, top=0.5, bot=0.75):
    col = np.array([0.02, 0.01, 0.03], np.float32)
    a = np.clip(1 - _yy / 0.32, 0, 1) ** 1.5 * top + np.clip((_yy - 0.58) / 0.42, 0, 1) ** 1.3 * bot
    return c * (1 - a) + col * a


_ff = {}


def full_files(name):
    import glob
    if name not in _ff or len(_ff[name]) == 0:
        _ff[name] = sorted(glob.glob(f'{S}/assets/{name}/*.png'))
    return _ff[name]


def seq_full(name, t_local, dur_target):
    """Full-frame 3D render (opaque PNG) scaled to cover 9:16."""
    files = full_files(name)
    if not files:
        return np.zeros((H, W, 3), np.float32)
    k = clamp(t_local / dur_target)
    i = min(len(files) - 1, int(k * (len(files) - 1) + 0.5))
    im = cv2.imread(files[i])[..., ::-1].astype(np.float32) / 255.0
    h, w = im.shape[:2]
    sc = max(W / w, H / h)
    im = cv2.resize(im, (int(w * sc + 0.5), int(h * sc + 0.5)), interpolation=cv2.INTER_CUBIC)
    y0 = (im.shape[0] - H) // 2
    x0 = (im.shape[1] - W) // 2
    return im[y0:y0 + H, x0:x0 + W].copy()


# ------------------------------------------------------------------ UI pieces
def clock_chip(c, t, hhmm, op=1.0, y=150):
    if op <= 0.01:
        return
    glass(c, 210, y, 330, 96, r=48, tint_c=(0.1, 0.06, 0.12), tint_a=0.55, opacity=op, blur=18, shadow_a=0.3,
          border_a=0.5)
    s = 46
    moon = np.zeros((s * 2, s * 2), np.float32)
    cv2.circle(moon, (s, s), s - 6, 1.0, -1, cv2.LINE_AA)
    cv2.circle(moon, (s + 22, s - 14), s - 10, 0.0, -1, cv2.LINE_AA)
    draw(c, cv2.resize(solid(moon, GOLD), (s, s)), 92, y, opacity=op)
    txt(c, hhmm, 140, y, 44, WHITE_, PX, op, ax=0.0)
    # ticking second hand dot
    a = (t * 2 * math.pi) % (2 * math.pi)
    draw(c, rrect_spr(10, 10, 5, ORANGE_B), 342 + 8 * math.cos(a), y + 8 * math.sin(a), opacity=op)


def time_at(t):
    """Story clock: 9:47pm at the call, ticking quickly through the getting-ready montage."""
    if t < T['ready']:
        m = 47
    else:
        m = 47 + int(prog(t, T['ready'], T['arrive']) * 44)
    h = 9 + m // 60
    return f'{h if h <= 12 else h - 12}:{m % 60:02d} PM'


def checklist(c, t, op=1.0):
    if op <= 0.01:
        return
    x, y, w, h = 770, 470, 560, 360
    glass(c, x, y, w * 0.8, h, r=32, tint_c=(1, 1, 1), tint_a=0.9, opacity=op, blur=22, shadow_a=0.4)
    txt(c, "TONIGHT'S CHECKLIST", x - 200, y - 135, 22, MAGENTA, PB, op, ax=0.0)
    for j, (_, _, label) in enumerate(SHOTS):
        yy = y - 80 + j * 66
        done = t >= T['ready'] + SHOT_LEN * (j + 0.55)
        kd = prog(t, T['ready'] + SHOT_LEN * (j + 0.55), T['ready'] + SHOT_LEN * (j + 0.55) + 0.3)
        box = rrect_spr(34, 34, 9, (0.85, 0.8, 0.86, 1)) if not done else check_spr(34, GREEN)
        draw(c, box, x - 190, yy, scale=e_out_back(kd, 3.0) if done else 1.0, opacity=op)
        col = INK if done else (0.45, 0.38, 0.45, 1)
        txt(c, label, x - 160, yy, 24, col, PS if done else PM, op, ax=0.0)


def captions(c, t, key, y=1560, size=50):
    """Word-by-word highlighted captions (trending style) for the voiceover line `key`."""
    if key not in VO:
        return
    t0 = VO[key]
    lt = t - t0
    if lt < 0 or lt > LINE_DUR[key] + 0.4:
        return
    phrases = PHRASES[key]
    idx = max(i for i in range(len(phrases)) if phrases[i][0] <= max(lt, 0.0)) if lt >= phrases[0][0] else 0
    p0, text = phrases[idx]
    p1 = phrases[idx + 1][0] if idx + 1 < len(phrases) else LINE_DUR[key]
    words = text.split(' ')
    k = clamp((lt - p0) / max(0.3, (p1 - p0) - 0.25))
    active = min(len(words) - 1, int(k * len(words)))
    sprs = [word_spr(wd, PX, size, HL if i == active else WHITE_) for i, wd in enumerate(words)]
    sw = font(PX, size).getlength(' ')
    # wrap to two lines max
    lines, cur, cw = [], [], 0
    for i, s in enumerate(sprs):
        if cur and cw + s.shape[1] > 900:
            lines.append(cur)
            cur, cw = [], 0
        cur.append(i)
        cw += s.shape[1] + sw
    lines.append(cur)
    op = min(1, prog(lt, p0 - 0.05, p0 + 0.12) * 1.5) * (1 - prog(lt, LINE_DUR[key] + 0.1, LINE_DUR[key] + 0.4))
    for li, ids in enumerate(lines):
        tw = sum(sprs[i].shape[1] for i in ids) + sw * (len(ids) - 1)
        x = W / 2 - tw / 2
        yy = y + (li - (len(lines) - 1) / 2) * size * 1.25
        for i in ids:
            s = sprs[i]
            sc = 1.08 if i == active else 1.0
            sh = blur_sprite(tint(s, (0, 0, 0)), 8)
            draw(c, sh, x + s.shape[1] / 2, yy + 5, opacity=0.85 * op, scale=sc)
            draw(c, s, x + s.shape[1] / 2, yy, opacity=op, scale=sc)
            x += s.shape[1] + sw


def headline(c, text, y, size, t, t0, color=WHITE_, fname=PK, glow=None, sweep_t=None):
    kinetic_line(c, text, W / 2, y, size, t, t0, color=color, fname=fname, glow=glow, glow_str=0.5, shadow_op=0.7,
                 sweep_t=sweep_t)


# ------------------------------------------------------------------ scenes
def sc_hook(t):
    c = seq_full('street_hook', t, T['call'])
    c = rain(c, t, 1.0)
    # light bloom burst when the porch light clicks on
    if t >= CLICK:
        k = prog(t, CLICK, CLICK + 0.25)
        c = c + np.array([1.0, 0.6, 0.25], np.float32) * 0.18 * math.exp(-(t - CLICK) * 4) * k
    c = scrim(c, 0.65, 0.4)
    c = title_band(c, 250, 560, 0.78)
    headline(c, 'When this light', 300, 82, t, 0.35, fname=PK)
    headline(c, 'comes on,', 400, 82, t, 0.7, fname=PK)
    headline(c, "someone's ready.", 520, 92, t, CLICK + 0.1, color=WARM, glow=ORANGE_B, sweep_t=CLICK + 0.6)
    c = lens_drops(c, t, 0.8)
    return c


def call_screen(t):
    scr = np.zeros((SH, SW, 4), np.float32)
    ys = np.linspace(0, 1, SH, dtype=np.float32)[:, None, None]
    scr[..., :3] = np.array([0.10, 0.04, 0.10], np.float32) * (1 - ys) + np.array([0.28, 0.06, 0.2], np.float32) * ys
    scr[..., 3] = 1
    paste(scr, text_sprite('9:47', PS, 24, WHITE_), 70, 40)
    answered = t >= ANSWER
    av = rrect_spr(190, 190, 95, (1, 1, 1, 0.12))
    pulse = 1 + (0.08 * math.sin(t * 8) if not answered else 0)
    for r_ in (1.35, 1.7):
        if not answered:
            ring = ring_sprite(int(190 * r_ + 40), 95 * r_ * (1 + 0.05 * math.sin(t * 6)), 2, (1, 1, 1, 0.3), glow=4)
            paste(scr, ring, SW / 2, 330)
    paste(scr, av, SW / 2, 330)
    paste(scr, text_sprite('SW', PX, 70, WHITE_), SW / 2, 330)
    paste(scr, text_sprite('Social worker', PX, 44, WHITE_), SW / 2, 500)
    sub = 'Emergency placement' if not answered else f'00:{int((t - ANSWER) + 1):02d}'
    paste(scr, text_sprite(sub, PM, 30, (1, 1, 1, 0.8)), SW / 2, 556)
    if not answered:
        for (x, col, lab) in ((140, hexc('#E5484D'), 'Decline'), (SW - 140, hexc('#34C759'), 'Accept')):
            b = rrect_spr(120, 120, 60, col)
            paste(scr, b, x, 1020 + (0 if lab == 'Decline' else -6 * abs(math.sin(t * 6))))
            paste(scr, text_sprite(lab, PM, 24, WHITE_), x, 1110)
    else:
        b = rrect_spr(120, 120, 60, hexc('#E5484D'))
        paste(scr, b, SW / 2, 1020)
        paste(scr, text_sprite('A child needs', PB, 34, WHITE_), SW / 2, 720)
        paste(scr, text_sprite('somewhere safe tonight', PB, 34, WHITE_), SW / 2, 768)
    return scr


def sc_call(t):
    t0 = T['call']
    lt = t - t0
    bg = night(clip_frame(5, 0.5 + lt * 0.6, zoom=1.15), warm=0.75) * 0.55
    bg = cv2.GaussianBlur(bg, (0, 0), 10)
    c = bg
    k = e_out_cubic(prog(t, t0, t0 + 0.6))
    rz = 2.5 * math.sin(t * 40) * (1 - prog(t, ANSWER - 0.2, ANSWER)) if t < ANSWER else 0
    body = phone_body().copy()
    scr = call_screen(t) * screen_mask()
    paste(body, scr, PW / 2, PH / 2)
    paste(body, rrect_spr(150, 40, 20, (0, 0, 0, 1)), PW / 2, 62)
    draw_phone(c, body, W / 2, lerp(1300, 1080, k), lerp(560, 640, k), lerp(20, 6, k), lerp(-18, -6, k), rz - 2 * (1 - k))
    c = scrim(c, 0.6, 0.6)
    clock_chip(c, t, time_at(t), op=min(1, prog(t, t0 + 0.2, t0 + 0.5) * 2))
    captions(c, t, 'call', y=1660)
    c = rain(c, t, 0.25, col=(1.0, 0.85, 0.7))
    return c


def sc_ready(t):
    t0 = T['ready']
    i = min(int((t - t0) / SHOT_LEN), 3)
    lt = t - t0 - i * SHOT_LEN
    ci, off, label = SHOTS[i]
    z = 1.16 - 0.08 * e_out_cubic(lt / SHOT_LEN)
    c = night(clip_frame(ci, off + lt * 1.1, zoom=z, rot=(1.2 if i % 2 else -1.2) * (1 - lt / SHOT_LEN)),
              warm=0.85 if i != 1 else 0.4)
    if lt < 0.05:
        c = c + 0.2 * (1 - lt / 0.05)
    # headlights sweep across the hallway window on the last shot
    if i == 3:
        kh = prog(t, T['arrive'] - 0.8, T['arrive'] - 0.05)
        if kh > 0:
            xs = np.linspace(0, 1, W, dtype=np.float32)[None, :, None]
            band = np.exp(-((xs - (kh * 1.6 - 0.3)) / 0.12) ** 2)
            c = c + band * np.array([1.0, 0.95, 0.85], np.float32) * 0.6 * math.sin(math.pi * kh)
    c = scrim(c, 0.55, 0.7)
    clock_chip(c, t, time_at(t))
    checklist(c, t, op=min(1, prog(t, t0 + 0.2, t0 + 0.6) * 2))
    captions(c, t, 'ready', y=1640)
    return c


@functools.lru_cache(maxsize=1)
def arrival_layers():
    bg = img('arrival_bg.png')
    base = img('arrival_base.png')
    a = img('arrival_child_a.png', cv2.IMREAD_GRAYSCALE)
    heart = img('arrival_heart.png', cv2.IMREAD_GRAYSCALE)
    child = np.concatenate([base * a[..., None], a[..., None]], 2).astype(np.float32)
    return bg, child, heart


def cover(im, z, dx, dy):
    """Scale a 654x1254 layer to cover 9:16 with zoom z and offset (dx, dy) in output px."""
    h, w = im.shape[:2]
    sc = max(W / w, H / h) * z
    M = np.float32([[sc, 0, W / 2 - sc * w / 2 + dx], [0, sc, H / 2 - sc * h / 2 + dy]])
    return cv2.warpAffine(im, M, (W, H), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REFLECT)


def sc_arrive(t):
    t0 = T['arrive']
    lt = t - t0
    k = e_inout_cubic(prog(t, t0, T['payoff']))
    bg, child, heart = arrival_layers()
    c = cover(bg, 1.04 + 0.04 * k, -20 * k, 10 * k)
    ch = cover(child, 1.08 + 0.07 * k, 26 * k - 10, 18 * k)
    a = ch[..., 3:4]
    c = c * (1 - a) + ch[..., :3]
    # neon heart: a bright pulse travels along the poster's heart line
    hm = cover(heart[..., None].repeat(3, 2), 1.04 + 0.04 * k, -20 * k, 10 * k)[..., 0]
    ys, xs = np.nonzero(hm > 0.3)
    if len(xs):
        cy_, cx_ = ys.mean(), xs.mean()
        ang = (np.arctan2(ys - cy_, xs - cx_) + math.pi) / (2 * math.pi)
        head = (lt * 0.55) % 1.0
        d = np.minimum(np.abs(ang - head), 1 - np.abs(ang - head))
        boost = np.zeros((H, W), np.float32)
        boost[ys, xs] = np.exp(-(d / 0.06) ** 2)
        g = cv2.GaussianBlur(boost, (0, 0), 8) * 2.5 + cv2.GaussianBlur(hm, (0, 0), 6) * (0.4 + 0.2 * math.sin(t * 5))
        c = c + g[..., None] * np.array([1.0, 0.25, 0.6], np.float32) * 0.5
    # hide the poster's graphic corner + warm the porch light
    vig = np.clip(1 - (((np.linspace(0, 1, W)[None, :] - 0.0) ** 2 * 3 + (np.linspace(0, 1, H)[:, None]) ** 2 * 8)), 0, 1)
    c = c * (1 - vig[..., None] * 0.85) + np.array([0.04, 0.02, 0.03], np.float32) * vig[..., None] * 0.85
    c = rain(c, t, 0.7)
    c = scrim(c, 0.35, 0.75)
    # spoken subtitles from the carer (story captions)
    for j, (line, ts) in enumerate([('“Hiya. You must be cold.', t0 + 0.4), ('Fancy some toast?”', t0 + 1.5)]):
        kk = prog(t, ts, ts + 0.3)
        if kk > 0:
            s = word_spr(line, PX, 54, WHITE_)
            box = rrect_spr(s.shape[1] + 50, 86, 20, (0.05, 0.02, 0.05, 0.6))
            yy = 1520 + j * 104
            draw(c, box, W / 2, yy, opacity=kk)
            draw(c, s, W / 2, yy, opacity=kk)
    c = lens_drops(c, t, 0.6)
    return c


def sc_payoff(t):
    t0 = T['payoff']
    c = seq_full('wellies', t - t0, T['rise'] - t0)
    c = c * 0.9 + np.array([0.03, 0.01, 0.0], np.float32)
    c = scrim(c, 0.7, 0.75)
    c = title_band(c, 230, 580, 0.86)
    headline(c, 'Ready when', 280, 92, t, t0 + 0.3, color=WHITE_)
    headline(c, 'it matters.', 390, 92, t, t0 + 0.55, color=WARM, glow=ORANGE_B, sweep_t=t0 + 1.2)
    kc = prog(t, VO['never'] + 0.9, VO['never'] + 1.3)
    if kc > 0:
        p = pill('Advice outside normal hours', PB, 32, pad_x=34, pad_y=16, fill=(1, 1, 1, 0.95), border=None,
                 text_color=INK, dot=MAGENTA)
        draw(c, blur_sprite(tint(p, (0, 0, 0)), 12), W / 2 + 6, 545 + 12, opacity=0.4 * kc)
        draw(c, p, W / 2, 545, scale=e_out_back(kc, 2.2), opacity=min(1, kc * 3))
        f = seq('clock', loop=True).frame(t)
        if f.shape[0] > 16:
            draw(c, f, W / 2 - p.shape[1] / 2 - 30, 545, scale=110 / max(f.shape[:2]) * e_out_back(kc, 2.2), opacity=kc)
    headline(c, 'Never on your own.', 1340, 82, t, VO['never'] + 3.1, color=WHITE_, glow=MAGENTA, sweep_t=VO['never'] + 3.8)
    captions(c, t, 'never', y=1640)
    return c


@functools.lru_cache(maxsize=1)
def grad_bg():
    ys, xs = np.mgrid[0:H, 0:W].astype(np.float32)
    u = np.clip((xs / W * 0.45 + ys / H * 0.8) / 1.25, 0, 1)[..., None]
    a = np.array(hexc('#8E0F5E')[:3], np.float32)
    m = np.array(MAGENTA[:3], np.float32)
    o = np.array(ORANGE_B[:3], np.float32)
    return np.where(u < 0.5, a * (1 - u * 2) + m * u * 2, m * (1 - (u - 0.5) * 2) + o * (u - 0.5) * 2).astype(np.float32)


def sc_rise(t):
    t0 = T['rise']
    c = seq_full('street_rise', t - t0, T['end'] - t0 + 0.2)
    c = rain(c, t, 1.0)
    c = scrim(c, 0.55, 0.5)
    c = title_band(c, 1180, 1420, 0.7)
    headline(c, 'Could you leave', 1230, 90, t, VO['cta'] + 0.05, fname=PK)
    headline(c, 'the light on?', 1345, 104, t, VO['cta'] + 0.5, color=WARM, glow=ORANGE_B, sweep_t=VO['cta'] + 1.2)
    kf = prog(t, T['end'] - 0.35, T['end'])
    if kf > 0:
        c = c * (1 - kf) + grad_bg() * kf
    c = lens_drops(c, t, 0.5)
    return c


def sc_end(t):
    t0 = T['end']
    c = grad_bg().copy()
    c = rain(c, t, 0.35, col=(1, 0.9, 0.95))
    kl = prog(t, t0, t0 + 0.5)
    glass(c, W / 2, 470, 860, 330, r=48, tint_c=(1, 1, 1), tint_a=0.96, opacity=min(1, kl * 2.5), blur=24,
          shadow_a=0.45, border_a=0.9)
    lg = fitted('logo', png('logo_full'), width=740)
    draw(c, lg, W / 2, 470, scale=0.9 + 0.1 * e_out_back(kl, 2.0), opacity=min(1, kl * 2))
    headline(c, 'Could you leave', 800, 84, t, t0 + 0.1, fname=PK)
    headline(c, 'the light on?', 905, 96, t, t0 + 0.3, color=hexc('#FFE3B0'), glow=ORANGE_B, sweep_t=t0 + 0.9)
    kb = prog(t, t0 + 0.5, t0 + 0.9)
    if kb > 0:
        p = pill('Start the conversation', PK, 46, pad_x=50, pad_y=24, fill=(1, 1, 1, 1), border=None, text_color=PLUM)
        draw(c, blur_sprite(tint(p, (0.3, 0, 0.15)), 14), W / 2 + 6, 1080 + 14, opacity=0.5 * kb)
        draw(c, p, W / 2, 1080, scale=e_out_back(kb, 2.2), opacity=min(1, kb * 3))
    ki = prog(t, t0 + 0.8, t0 + 1.2)
    if ki > 0:
        txt(c, '0161 241 1332', W / 2, 1250, 58, WHITE_, PK, ki, shadow_op=0.5)
        txt(c, 'organicfostering.co.uk', W / 2, 1325, 40, WHITE_, PS, ki, shadow_op=0.5)
    ko = prog(t, t0 + 1.0, t0 + 1.4)
    if ko > 0:
        p = pill('Rated Good by Ofsted', PB, 30, pad_x=30, pad_y=14, fill=(1, 1, 1, 0.18), border=(1, 1, 1, 0.7),
                 text_color=WHITE_, dot=hexc('#8BC34A'))
        draw(c, p, W / 2, 1440, scale=e_out_back(ko, 2.2), opacity=min(1, ko * 3))
    ks = prog(t, t0 + 1.2, t0 + 1.6)
    if ks > 0:
        txt(c, 'AI-generated imagery. Not a real child. Story and time are illustrative.', W / 2, 1800, 24,
            (1, 1, 1, 0.85), PM, ks, shadow_op=0.4)
    captions(c, t, 'cta', y=1620, size=44)
    return c


SCENES = [(T['hook'], T['call'], sc_hook), (T['call'], T['ready'], sc_call), (T['ready'], T['arrive'], sc_ready),
          (T['arrive'], T['payoff'], sc_arrive), (T['payoff'], T['rise'], sc_payoff), (T['rise'], T['end'], sc_rise),
          (T['end'], 99, sc_end)]
TRANS = [(T['call'], 'flash'), (T['ready'], 'whip'), (T['arrive'], 'flash'), (T['payoff'], 'whip'), (T['rise'], 'zoom')]


def scene_at(t):
    for a, b, f in SCENES:
        if a <= t < b:
            return f
    return SCENES[-1][2]


def render_raw(t):
    c = scene_at(t)(t)
    for tc, kind in TRANS:
        d = t - tc
        if kind == 'whip' and -0.15 < d < 0.15:
            c = whip(c, 1 - abs(d) / 0.15, -1)
        elif kind == 'zoom' and -0.12 < d < 0.15:
            c = zoom_blur(c, (1 - abs(d) / 0.15) * 3)
        elif kind == 'flash' and -0.04 < d < 0.3:
            c = c + np.array((1.0, 0.75, 0.55), np.float32) * 0.6 * math.exp(-max(0, d) * 12)
    dx = dy = 0.0
    for tc in [CLICK, ANSWER]:
        sx, sy = shake(t, tc, amp=7, dur=0.3)
        dx += sx
        dy += sy
    if abs(dx) + abs(dy) > 0.5:
        c = cv2.warpAffine(c, np.float32([[1, 0, dx], [0, 1, dy]]), (W, H), borderMode=cv2.BORDER_REFLECT)
    if t > DUR - FADE:
        c *= 1 - 0.88 * e_inout_cubic(prog(t, DUR - FADE, DUR))
    return c


def is_fast(t):
    return any(abs(t - tc) < 0.2 for tc, _ in TRANS) or (T['ready'] <= t < T['arrive'] and
                                                            ((t - T['ready']) % SHOT_LEN) < 0.15)


def render(fi):
    t = fi / FPS
    if is_fast(t):
        acc = None
        for k in range(3):
            r = render_raw(max(0.0, t + (k / 3 - 0.5) * 0.5 / FPS))
            acc = r if acc is None else acc + r
        c = acc / 3
    else:
        c = render_raw(t)
    return post(c, fi, bloom=0.45, grain=0.02, vig=1.0)


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
            cv2.imwrite(f'{S}/frames_out/{fi:04d}.png', to_u8(render(fi)), [cv2.IMWRITE_PNG_COMPRESSION, 1])
            print('frame', fi, flush=True)
