"""Organic Fostering "Asked the internet? Ask us instead." (9:16 video, ~34 s), after the client's projected-search
reference. Late at night, a search interface flickers on as light across a wooden table. The question is typed, deleted
and retyped ("...rent my home?" / "...I'm single?" / "...I work full time?"). Enter: a thousand answers flood the card
in a glitchy blur. Then one real result: Organic Fostering, and a 3D home rises out of the table. The camera pushes in
and flies through the lit window into a warm living room. End card. ElevenLabs voice (IDA).

Layers: Blender plates (table with projector off/on), Blender 3D house rise (transparent, shadow-caught), a live 2D UI
drawn every frame and projected onto the table with the camera's homography, then a 2D camera move over everything.

Usage: python3 reel_search.py still 1.0,5.0 | python3 reel_search.py range 0 100 | python3 reel_search.py times
"""
import os, sys, math, json, glob, functools
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'pipeline'))
import numpy as np
import cv2
from PIL import Image, ImageDraw, ImageFont
from engine import prog, clamp, lerp, e_out_back, e_out_cubic, e_in_cubic, e_inout_cubic, post

FPS = 30
ROOT = os.path.abspath(os.path.join(HERE, '..'))
S = f'{ROOT}/workspace_search'
RD = f'{S}/render'
FON = f'{ROOT}/workspace_sol/fonts'
W, H = 1080, 1350
DUR = 34.0
NF = int(DUR * FPS)
WORDS = [tuple(w) for w in json.load(open(f'{S}/tts/info.json'))['words']]


def WT(i):
    return WORDS[i][1]


PROJ = json.load(open(f'{RD}/proj.json'))
PW, PH = PROJ['res']
_PX, _PY = np.meshgrid(np.arange(PW, dtype=np.float32), np.arange(PH, dtype=np.float32))
_OX, _OY = np.meshgrid(np.arange(W, dtype=np.float32), np.arange(H, dtype=np.float32))
PLUM, MAG, ORANGE, GREEN, PEACH, IVORY = (91, 23, 79), (183, 0, 110), (255, 100, 17), (97, 168, 10), (255, 212, 186), (252, 248, 245)


@functools.lru_cache(maxsize=64)
def F(name, size):
    return ImageFont.truetype(f'{FON}/{name}.ttf', size)


def load(path):
    return cv2.imread(path, cv2.IMREAD_UNCHANGED)[..., ::-1].astype(np.float32) / 255 if path.endswith('.jpg') else None


@functools.lru_cache(maxsize=2)
def plate(which):
    im = cv2.imread(f'{RD}/plate_{which}.png')[..., ::-1].astype(np.float32) / 255
    return cv2.resize(im, (PW, PH)) if im.shape[:2] != (PH, PW) else im


@functools.lru_cache(maxsize=40)
def house_frame(i):
    p = f'{RD}/house/{i:03d}.png'
    im = cv2.imread(p, cv2.IMREAD_UNCHANGED).astype(np.float32) / 255
    rgb, a = im[..., 2::-1], im[..., 3:4]
    return np.ascontiguousarray(rgb), np.ascontiguousarray(a)


HBOX = json.load(open(f'{RD}/house_box.json'))['box'] if os.path.exists(f'{RD}/house_box.json') else None

# ------------------------------------------------------------------ the projected UI (drawn at 1200x1500, original layout x0.75)
US = 0.75
UW, UH = int(1600 * US), int(2000 * US)
LIGHT = (255, 246, 252, 255)
DIM = (255, 236, 248, 150)
PINK = (255, 120, 200, 255)


def u(v):
    return int(round(v * US))


KEYS = {}
_rows = ['QWERTYUIOP', 'ASDFGHJKL', 'ZXCVBNM']
for _r, _keys in enumerate(_rows):
    _kw, _gap = 118, 14
    _tw = len(_keys) * _kw + (len(_keys) - 1) * _gap
    _x0 = 800 - _tw / 2
    for _k, _ch in enumerate(_keys):
        _x = _x0 + _k * (_kw + _gap)
        _y = 1450 + _r * 132
        KEYS[_ch] = (_x, _y, _x + _kw, _y + 112)
KEYS[' '] = (340, 1846, 1100, 1958)
KEYS['\n'] = (1130, 1846, 1460, 1958)
KEYS['\b'] = KEYS['P']


@functools.lru_cache(maxsize=1)
def ui_base():
    im = Image.new('RGBA', (UW, UH), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([u(60), u(40), u(1540), u(1960)], u(70), fill=(255, 220, 240, 10), outline=(255, 220, 240, 70), width=3)
    d.rounded_rectangle([u(140), u(150), u(1460), u(300)], u(75), fill=(255, 240, 248, 50), outline=LIGHT, width=4)
    d.ellipse([u(200), u(192), u(262), u(254)], outline=LIGHT, width=6)
    d.line([(u(254), u(246)), (u(284), u(276))], fill=LIGHT, width=7)
    for ch, (x0, y0, x1, y1) in KEYS.items():
        if ch in ('\b',):
            continue
        if ch == '\n':
            d.rounded_rectangle([u(x0), u(y0), u(x1), u(y1)], u(22), outline=PINK, width=4, fill=(255, 120, 200, 70))
            d.text(((u(x0) + u(x1)) / 2, (u(y0) + u(y1)) / 2), 'search', font=F('Nunito-800', u(44)), fill=LIGHT, anchor='mm')
        else:
            d.rounded_rectangle([u(x0), u(y0), u(x1), u(y1)], u(20), outline=(255, 236, 248, 150), width=3, fill=(255, 230, 245, 8))
            if ch != ' ':
                d.text(((u(x0) + u(x1)) / 2, (u(y0) + u(y1)) / 2), ch, font=F('Nunito-700', u(44)), fill=(255, 236, 248, 200), anchor='mm')
    return im


# typing timeline: (time, action, payload)
Q1 = 'Can I foster if I rent my home?'
SCHED = []


def _type(text, t0, t1):
    for i, ch in enumerate(text):
        SCHED.append((t0 + (t1 - t0) * i / max(1, len(text) - 1), 'add', ch))


def _back(n, t0, t1):
    for i in range(n):
        SCHED.append((t0 + (t1 - t0) * i / max(1, n - 1), 'del', None))


_type(Q1, 5.55, 7.6)
_back(len('rent my home?'), 7.95, 8.35)
_type("'m single?", 8.6, 9.25)
_back(len("'m single?"), 9.65, 9.95)
_type(' work full time?', 10.15, 11.25)
ENTER = 11.85
SCHED.sort()


def typed_at(t):
    s, last_t, last_ch = '', -9, None
    for tt, act, ch in SCHED:
        if tt > t:
            break
        if act == 'add':
            s += ch
            last_ch = ch.upper() if ch.isalpha() else (' ' if ch == ' ' else None)
        else:
            s = s[:-1]
            last_ch = '\b'
        last_t = tt
    return s, last_t, last_ch


CHAOS = ["Can renters foster? (forum, 847 replies)", "Fostering rules explained (2014)", "Do you have to own your home?",
         "I read somewhere that you can't...", "Top 10 fostering myths", "Is it even worth asking?", "Single carers: yes or no?",
         "My friend's cousin said...", "Fostering FAQ (page 14 of 31)", "Comments (2,113)", "Requirements: it depends",
         "Full-time work and fostering?", "Don't bother if you rent?", "Opinions wanted"]
REAL = 16.45
RISE = WT(33) - 0.05                                    # "real"
CARD_LINES = [("Renting doesn't automatically", 37), ('rule you out. Neither does', 43), ('being single. Ask us.', 45)]


def ui_frame(t):
    im = ui_base().copy()
    d = ImageDraw.Draw(im)
    text, last_t, last_ch = typed_at(t)
    if t < 5.5 and t > 2.0:
        text = ''
    shown = text if text else ''
    if shown:
        d.text((u(320), u(225)), shown, font=F('Nunito-700', u(58)), fill=LIGHT, anchor='lm')
    tw = d.textlength(shown, font=F('Nunito-700', u(58))) if shown else 0
    if (t * 2) % 1 < 0.6 or t - last_t < 0.5:
        d.rectangle([u(322) + tw + 4, u(195), u(322) + tw + 8, u(255)], fill=PINK)
    # key glow + ripple
    kp = []
    for tt, act, ch in SCHED:
        if tt <= t < tt + 0.35:
            key = '\b' if act == 'del' else (ch.upper() if ch.isalpha() else (' ' if ch == ' ' else None))
            if key in KEYS:
                kp.append((key, (t - tt) / 0.35))
    if ENTER <= t < ENTER + 0.6:
        kp.append(('\n', (t - ENTER) / 0.6))
    for key, k in kp:
        x0, y0, x1, y1 = KEYS[key]
        a = int(220 * (1 - k))
        d.rounded_rectangle([u(x0), u(y0), u(x1), u(y1)], u(20), fill=(255, 140, 210, a // 2), outline=(255, 255, 255, a), width=4)
        r = u(40 + 90 * k)
        cx, cy = u((x0 + x1) / 2), u((y0 + y1) / 2)
        d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=(255, 200, 235, int(160 * (1 - k))), width=3)
    # suggestions while typing
    if 5.6 <= t < ENTER + 0.2:
        for i, sug in enumerate(("can I foster if I'm single", 'can I foster if I work full time', 'fostering support Manchester')):
            y = u(380 + i * 92)
            d.ellipse([u(200), y - u(18), u(236), y + u(18)], outline=DIM, width=4)
            d.text((u(270), y), sug, font=F('Nunito-700', u(46)), fill=DIM, anchor='lm')
    cx0, cy0, cx1, cy1 = u(140), u(680), u(1460), u(1330)
    # a thousand answers: glitchy stream of results
    if ENTER + 0.1 <= t < REAL:
        k = prog(t, ENTER + 0.1, ENTER + 0.5) * (1 - prog(t, REAL - 0.35, REAL))
        rng = np.random.default_rng(int(t * 14))
        for j in range(9):
            y = cy0 - u(260) + j * u(150) + int((t * 900) % u(150))
            if y < u(330) or y > u(1360):
                continue
            jx = int(rng.normal(0, 10))
            alpha = int(rng.uniform(80, 230) * k)
            d.rounded_rectangle([cx0 + jx, y, cx1 + jx, y + u(126)], u(26), outline=(255, 220, 240, alpha), width=3, fill=(255, 210, 235, alpha // 6))
            d.text((cx0 + jx + u(40), y + u(40)), CHAOS[rng.integers(0, len(CHAOS))], font=F('Nunito-800', u(46)), fill=(255, 240, 248, alpha), anchor='lm')
            d.rectangle([cx0 + jx + u(40), y + u(80), cx0 + jx + u(40) + int(rng.uniform(200, 700) * US), y + u(92)], fill=(255, 220, 240, alpha // 2))
    # the one real result
    if t >= REAL:
        k = e_out_cubic(prog(t, REAL, REAL + 0.5))
        a = int(255 * k)
        d.rounded_rectangle([cx0, cy0, cx1, cy1], u(46), fill=(255, 235, 246, int(30 * k)), outline=(255, 246, 252, a), width=4)
        d.rounded_rectangle([cx0 + u(40), cy0 + u(40), cx0 + u(520), cy1 - u(40)], u(34), fill=(255, 225, 240, int(20 * k)), outline=(255, 230, 245, int(140 * k)), width=3)
        tx = cx0 + u(580)
        d.text((tx, cy0 + u(70)), 'organicfostering.co.uk', font=F('Nunito-700', u(40)), fill=(255, 236, 248, int(150 * k)))
        d.text((tx, cy0 + u(130)), 'Organic Fostering', font=F('Nunito-900', u(74)), fill=(255, 246, 252, a))
        d.text((tx, cy0 + u(225)), 'Manchester · Rated Good by Ofsted', font=F('Nunito-700', u(40)), fill=(255, 120, 200, a))
        for j, (line, wi) in enumerate(CARD_LINES):
            kl = prog(t, WT(wi) - 0.1, WT(wi) + 0.4)
            col = (255, 246, 252, int(a * (0.55 + 0.45 * kl)))
            y = cy0 + u(300 + j * 58)
            if kl > 0:
                tw = d.textlength(line, font=F('Nunito-700', u(44)))
                d.rounded_rectangle([tx - u(8), y - u(4), tx + int(tw * min(1, kl * 1.5)) + u(8), y + u(54)], u(10), fill=(255, 120, 200, int(70 * kl)))
            d.text((tx, y), line, font=F('Nunito-700', u(44)), fill=col)
        for j, lab in enumerate(('Enquire', 'Call', 'FAQs')):
            x = tx + j * u(230)
            pulse = 1 if j else (0.6 + 0.4 * math.sin(t * 4)) * prog(t, WT(53), WT(53) + 0.3)
            d.rounded_rectangle([x, cy1 - u(120), x + u(200), cy1 - u(50)], u(35), outline=(255, 246, 252, a), width=3,
                                fill=(255, 120, 200, int(70 * k + 120 * (pulse if j == 0 else 0))) if j == 0 else None)
            d.text((x + u(100), cy1 - u(85)), lab, font=F('Nunito-800', u(36)), fill=(255, 246, 252, a), anchor='mm')
        sw = prog(t, REAL, REAL + 0.7)
        if 0 < sw < 1:
            y = int(lerp(cy0, cy1, sw))
            d.rectangle([cx0, y - 3, cx1, y + 3], fill=(255, 255, 255, int(200 * (1 - sw))))
    a = np.asarray(im).astype(np.float32) / 255
    return a[..., :3] * a[..., 3:4], a[..., 3:4]


@functools.lru_cache(maxsize=1)
def HOMO():
    src = np.float32([[0, 0], [UW, 0], [UW, UH], [0, UH]])
    return cv2.getPerspectiveTransform(src, np.float32(PROJ['ui']))


def project_ui(c, t, power):
    rgb, a = ui_frame(t)
    M = HOMO()
    wr = cv2.warpPerspective(rgb, M, (PW, PH), flags=cv2.INTER_LINEAR)
    wa = cv2.warpPerspective(a[..., 0], M, (PW, PH), flags=cv2.INTER_LINEAR)[..., None]
    small = cv2.resize(wr, (PW // 4, PH // 4), interpolation=cv2.INTER_AREA)
    glow = cv2.resize(cv2.GaussianBlur(small, (0, 0), 5), (PW, PH))
    tint = np.array([1.0, 0.86, 0.95], np.float32)
    c[:] = np.clip(c * (1 - 0.12 * wa * power) + (wr * 1.1 + glow * 0.8) * tint * power, 0, 1)


def paste_house(c, t):
    if t < RISE or HBOX is None:
        return
    i = min(24, int((t - RISE) * 30))
    rgb, a = house_frame(i)
    x0, y0, x1, y1 = [int(round(v)) for v in HBOX]
    h, w = rgb.shape[:2]
    x1, y1 = x0 + w, y0 + h
    reg = c[y0:y1, x0:x1]
    reg[:] = reg * (1 - a) + rgb
    if t < RISE + 1.0:                                   # light burst as it rises
        bx, by = PROJ['house_base']
        k = math.sin(math.pi * prog(t, RISE, RISE + 1.0))
        g = np.exp(-(((_PX - bx) / 420) ** 2 + ((_PY - by) / 420) ** 2))[..., None]
        c[:] = np.clip(c + g * np.array([1.0, 0.7, 0.85], np.float32) * 0.35 * k, 0, 1)


# ------------------------------------------------------------------ footage
class Clip:
    def __init__(self, cid):
        self.cap = cv2.VideoCapture(f'{S}/clips/{cid}.mp4')
        self.fps = self.cap.get(cv2.CAP_PROP_FPS) or 25
        self.n = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
        self.pos, self.cache = -1, {}

    def frame(self, t):
        i = int(clamp(t * self.fps, 0, self.n - 1))
        if i in self.cache:
            return self.cache[i]
        if i != self.pos + 1:
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, i)
        ok, im = self.cap.read()
        if not ok:
            return self.cache[max(self.cache)] if self.cache else np.zeros((720, 1280, 3), np.uint8)
        self.pos = i
        if len(self.cache) > 20:
            self.cache.clear()
        self.cache[i] = im
        return im


_clips = {}


def footage(cid, ct, z=1.0, fx=0.5, fy=0.5):
    if cid not in _clips:
        _clips[cid] = Clip(cid)
    im = _clips[cid].frame(ct).astype(np.float32)[..., ::-1] / 255
    ih, iw = im.shape[:2]
    sc = max(W / iw, H / ih) * z
    cw, ch = W / sc, H / sc
    x0 = min(max(fx * iw - cw / 2, 0), iw - cw)
    y0 = min(max(fy * ih - ch / 2, 0), ih - ch)
    M = np.float32([[sc, 0, -x0 * sc], [0, sc, -y0 * sc]])
    out = cv2.warpAffine(im, M, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
    lum = out.mean(2, keepdims=True)
    hi = np.clip((lum - 0.4) * 2, 0, 1)
    return np.clip((out - 0.5) * 1.05 + 0.52 + hi * np.array([0.07, 0.03, -0.03], np.float32), 0, 1)


# ------------------------------------------------------------------ camera
FLY0, FLY1 = WT(47) - 0.15, WT(50) - 0.1                  # "Ask the internet?" -> fly through the window


def ui_pt(x, y):
    v = HOMO() @ np.array([x * US, y * US, 1.0])
    return v[0] / v[2], v[1] / v[2]


def camera(t):
    """(zoom, centre x, centre y) in plate coordinates."""
    hx, hy = PROJ['house_base']
    wx, wy = PROJ['window']
    bx, by = ui_pt(800, 330)                          # the search bar + first suggestion
    mx, my = ui_pt(800, 1000)                         # middle of the projection
    if t < REAL:
        kin = e_inout_cubic(prog(t, 1.4, 5.3))        # push in on the search bar
        kout = e_inout_cubic(prog(t, ENTER, ENTER + 0.9))   # pull back on Enter
        z = lerp(lerp(1.06, 1.95, kin), 1.12, kout)
        cx = lerp(lerp(PW / 2, bx, kin), mx, kout)
        cy = lerp(lerp(PH / 2, by + 60, kin), my, kout)
        return z, cx, cy
    k = e_inout_cubic(prog(t, REAL + 0.8, FLY0))
    z = lerp(1.12, 1.5, k)
    cx, cy = lerp(mx, (mx + hx) / 2, k), lerp(my, (my + hy) / 2, k)
    if t >= FLY0:
        f = e_in_cubic(prog(t, FLY0, FLY1))
        z = z * (1 + 9 * f)
        q = e_out_cubic(prog(t, FLY0, FLY0 + 0.6))
        cx, cy = lerp(cx, wx, q), lerp(cy, wy, q)
    return z, cx, cy


def view(c, z, cx, cy):
    s = (W / PW) * z
    M = np.float32([[s, 0, W / 2 - cx * s], [0, s, H / 2 - cy * s]])
    return cv2.warpAffine(c, M, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)


# ------------------------------------------------------------------ captions
def draw_text(img, text, y, size, col=(255, 253, 251), font='Nunito-800', shadow=True):
    pil = Image.fromarray((np.clip(img, 0, 1) * 255).astype(np.uint8))
    d = ImageDraw.Draw(pil, 'RGBA')
    for li, line in enumerate(text.split('|')):
        yy = y + li * size * 1.25
        if shadow:
            for dx, dy, a in ((3, 5, 160), (0, 2, 120)):
                d.text((W / 2 + dx, yy + dy), line.strip(), font=F(font, size), fill=(10, 0, 8, a), anchor='mm')
        d.text((W / 2, yy), line.strip(), font=F(font, size), fill=col, anchor='mm')
    return np.asarray(pil).astype(np.float32) / 255


SUBS = [(0, 1, "It's late."), (2, 7, 'And you type the question again.'), (24, 29, 'The internet has a thousand answers.'),
        (30, 36, 'We have a real one, for you.'), (37, 42, "Renting doesn't automatically rule you out."), (43, 46, 'Neither does being single.')]


def subtitles(c, t):
    for a, b, text in SUBS:
        t0, t1 = WT(a) - 0.1, WORDS[b][2] + 0.6
        if t0 <= t < t1:
            k = prog(t, t0, t0 + 0.25) * (1 - prog(t, t1 - 0.25, t1))
            out = draw_text(c, text, 1268, 44)
            c[:] = c * (1 - k) + out * k
            return c
    return c


# ------------------------------------------------------------------ the end
END0 = WT(53) - 0.35


@functools.lru_cache(maxsize=1)
def LOGO():
    lg = Image.open(f'{ROOT}/workspace_three/web/logo.png').convert('RGBA')
    return lg.crop(lg.getbbox())


def end_card(t):
    pil = Image.new('RGB', (W, H), IVORY)
    d = ImageDraw.Draw(pil, 'RGBA')
    k = e_out_cubic(prog(t, END0, END0 + 0.6))
    lg = LOGO()
    lw = int(700 * (0.94 + 0.06 * k))
    l2 = lg.resize((lw, int(lg.height * lw / lg.width)), Image.LANCZOS)
    if k > 0:
        l2.putalpha(l2.split()[3].point(lambda v: int(v * k)))
        pil.paste(l2, (int(W / 2 - lw / 2), 300 - l2.height // 2), l2)
    for j, (line, col) in enumerate((('Asked the internet?', PLUM), ('Ask us instead.', MAG))):
        kj = prog(t, END0 + 0.3 + j * 0.15, END0 + 0.7 + j * 0.15)
        if kj > 0:
            d.text((W / 2, 610 + j * 100 + (1 - e_out_cubic(kj)) * 20), line, font=F('Nunito-900', 84), fill=col + (int(255 * kj),), anchor='mm')
    kb = prog(t, WT(53) - 0.05, WT(53) + 0.35)
    if kb > 0:
        e = e_out_back(kb, 1.8) * (1 + 0.025 * math.sin((t - WT(53)) * 4) * prog(t, WT(53) + 0.6, WT(53) + 1.0))
        bw, bh = int(560 * e), int(118 * e)
        d.rounded_rectangle([W / 2 - bw / 2, 900 - bh / 2, W / 2 + bw / 2, 900 + bh / 2], bh // 2, fill=MAG)
        d.text((W / 2, 900), 'Start your enquiry', font=F('Nunito-800', int(48 * e)), fill=(255, 255, 255), anchor='mm')
    kp = prog(t, WT(59) - 0.05, WT(59) + 0.35)
    if kp > 0:
        d.text((W / 2, 1010), 'No pressure, no obligation.', font=F('Nunito-700', 40), fill=PLUM + (int(255 * kp),), anchor='mm')
        d.text((W / 2, 1080), '0161 241 1332  ·  organicfostering.co.uk', font=F('Nunito-700', 34), fill=(101, 85, 99, int(255 * kp)), anchor='mm')
    for i, col in enumerate((MAG, ORANGE, GREEN)):
        d.rectangle([i * W // 3, H - 14, (i + 1) * W // 3, H], fill=col)
    return np.asarray(pil).astype(np.float32) / 255


# ------------------------------------------------------------------ frame
def table_frame(t):
    on = prog(t, 0.6, 1.6)
    flick = 1.0 if on >= 1 else (on * (0.5 + 0.5 * (math.sin(t * 90) > -0.2)) if on > 0 else 0.0)
    c = plate('off') * (1 - flick) + plate('on') * flick
    c = np.ascontiguousarray(c)
    if flick > 0:
        project_ui(c, t, flick)
    paste_house(c, t)
    z, cx, cy = camera(t)
    out = view(c, z, cx, cy)
    if t >= FLY0:                                       # flying in: zoom blur + warm window light swallowing the frame
        f = prog(t, FLY0, FLY1)
        if f > 0.05:
            acc = out.copy()
            for j in range(1, 5):
                zz = 1 + 0.05 * j * f
                acc += cv2.warpAffine(out, np.float32([[zz, 0, (1 - zz) * W / 2], [0, zz, (1 - zz) * H / 2]]), (W, H), borderMode=cv2.BORDER_REPLICATE)
            out = acc / 5
        g = e_in_cubic(f)
        out = out * (1 - g) + np.array([1.0, 0.82, 0.55], np.float32) * g
    return out


def render_raw(t):
    if t < FLY1:
        c = table_frame(t)
        c = subtitles(c, t)
    elif t < END0:
        ft = t - FLY1
        c = footage('4858', 1.5 + ft * 0.9, z=1.25 - 0.15 * e_out_cubic(prog(t, FLY1, END0)), fx=0.5, fy=0.45)
        g = 1 - e_out_cubic(prog(t, FLY1, FLY1 + 0.6))
        c = c * (1 - g) + np.array([1.0, 0.82, 0.55], np.float32) * g
        k = prog(t, WT(50) - 0.1, WT(50) + 0.3)
        sh = np.clip((_OY - 900) / 450, 0, 1)[..., None] * 0.6
        c = c * (1 - sh * k)
        if k > 0:
            out = draw_text(c, 'Ask us instead.', 1180, 92, font='Nunito-900', col=(255, 253, 251))
            c = c * (1 - k) + out * k
    else:
        c = end_card(t)
        kx = 1 - prog(t, END0, END0 + 0.5)
        if kx > 0:
            prev = footage('4858', 1.5 + (END0 - FLY1) * 0.9, z=1.1)
            c = c * (1 - kx) + prev * kx
    fo = prog(t, DUR - 1.2, DUR)
    if fo > 0:
        c = c * (1 - 0.4 * e_inout_cubic(fo)) + np.array(IVORY, np.float32) / 255 * 0.4 * e_inout_cubic(fo)
    return np.clip(c, 0, 1).astype(np.float32)


def finish(c, fi, bloom=0.1, grain=0.01, vig=0.12):
    small = cv2.resize(c, (W // 4, H // 4), interpolation=cv2.INTER_AREA)
    hi = np.clip(small - 0.6, 0, 1)
    c = c + cv2.resize(cv2.GaussianBlur(hi, (0, 0), 6), (W, H)) * bloom * 3
    rng = np.random.default_rng(fi)
    c = c + cv2.resize(rng.normal(0, grain, (H // 2, W // 2)).astype(np.float32), (W, H))[..., None]
    if vig:
        v = np.clip(1 - (((_OX - W / 2) / (W * 0.75)) ** 2 + ((_OY - H / 2) / (H * 0.75)) ** 2), 0, 1)[..., None]
        c = c * (1 - vig + vig * v)
    return np.clip(c, 0, 1)


def render(fi):
    t = fi / FPS
    return finish(render_raw(t), fi, vig=0.12 if t < FLY1 else 0.0)


def to_u8(im):
    return (np.clip(im, 0, 1) * 255 + 0.5).astype(np.uint8)[..., ::-1]


if __name__ == '__main__':
    mode = sys.argv[1]
    if mode == 'still':
        os.makedirs(f'{S}/stills', exist_ok=True)
        for tt_ in sys.argv[2].split(','):
            t = float(tt_)
            cv2.imwrite(f'{S}/stills/s_{t:05.2f}.jpg', to_u8(render(int(round(t * FPS)))), [cv2.IMWRITE_JPEG_QUALITY, 88])
            print('still', t, flush=True)
    elif mode == 'range':
        a, b = int(sys.argv[2]), int(sys.argv[3])
        os.makedirs(f'{S}/frames_out', exist_ok=True)
        for fi in range(a, b):
            p = f'{S}/frames_out/{fi:04d}.jpg'
            if os.environ.get('RESUME') and os.path.exists(p):
                continue
            cv2.imwrite(p, to_u8(render(fi)), [cv2.IMWRITE_JPEG_QUALITY, 95])
            print('frame', fi, flush=True)
    elif mode == 'times':
        print('DUR', DUR, 'REAL', REAL, 'RISE', round(RISE, 2), 'FLY', round(FLY0, 2), round(FLY1, 2), 'END', round(END0, 2))
