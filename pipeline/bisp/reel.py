"""BISP "Interoperability" reel: frame renderer (1080x1920, 30 fps).

    python3 reel.py still 3.0,12.5,45          -> workspace_bisp/stills/still_<t>.jpg
    python3 reel.py sheet 24                   -> contact sheet of 24 evenly spaced frames
Rendering of the whole film is done by render.py (parallel chunks) which imports render_frame(t).
"""
import os, sys, json, math, re
from functools import lru_cache
import numpy as np
import cv2

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import kit as K
import edl

W, H, FPS = edl.W, edl.H, edl.FPS
WS = edl.WS
TL = edl.timeline()
WORDS = edl.out_words()
FACES = json.load(open(os.path.join(WS, 'faces.json')))
CLIP_DUR = {}

TOP_Y = 470       # centre of the upper graphics band (above her head)
LOW_Y = 1215      # centre of the lower graphics band (over her body)
CAP_Y = 1462      # caption line centre
CX = 540
CXL = 520         # lower band is nudged left of the like/comment/share column


# ---- word lookup ---------------------------------------------------------------------------------------------------
def _norm(w):
    return re.sub(r'[^a-z0-9\-]', '', w.lower())


def Wt(seg, word, k=0):
    """Output time of the k-th occurrence of `word` inside segment `seg`."""
    s = TL.seg(seg)
    hits = [w['ot'] for w in WORDS if s['t0'] - 0.05 <= w['ot'] < s['t1'] + 0.05 and _norm(w['word']) == _norm(word)]
    if len(hits) <= k:
        raise KeyError(f'{word}#{k} not in {seg}: {[w["word"] for w in WORDS if s["t0"] <= w["ot"] < s["t1"]]}')
    return hits[k]


def S(seg):
    return TL.seg(seg)


# ---- the plan: every timed event (also drives the SFX cue sheet) ---------------------------------------------------
def build_plan():
    P = {}
    P['hook_title1'] = 0.10
    P['hook_title2'] = Wt('hook', 'ka')
    P['hook_interop'] = Wt('hook', 'interoperability')
    P['hook_raqam'] = Wt('hook', 'raqam')
    P['hook_intikhab'] = Wt('hook', 'intikhab')
    P['hook_out'] = S('hook')['t1'] - 0.30
    P['logo_in'] = 0.35
    P['logo_pulse'] = Wt('wallets', 'benazir')
    P['crore_in'] = Wt('wallets', 'crore') - 0.4
    P['crore_out'] = S('wallets')['t1'] - 0.35
    P['any_pak'] = Wt('anytime', 'poore')
    P['any_waqt'] = Wt('anytime', 'waqt') - 0.2
    P['any_din'] = Wt('anytime', 'din') - 0.25
    P['any_sahulat'] = Wt('anytime', 'sahulat')
    P['any_out'] = S('anytime')['t1'] - 0.35
    P['plate1'] = Wt('vision_a', 'sadr-e-pakistan') - 0.1
    P['plate2'] = Wt('vision_a', 'wazir-e-azam') - 0.15
    P['plates_out'] = Wt('vision_b', 'khawateen') - 0.1
    P['maali_in'] = Wt('vision_b', 'maali') - 0.1
    P['maali_out'] = S('vision_b')['t1'] - 0.3
    P['whatis_in'] = S('whatis')['t0'] + 0.04
    P['whatis_out'] = S('whatis')['t1'] - 0.28
    P['pehle_tag'] = S('pehle')['t0'] + 0.15
    P['pain1'] = Wt('pehle', 'khaas') - 0.1
    P['pain2'] = Wt('pehle', 'lambi')
    P['pain3'] = Wt('pehle', 'intezar')
    P['pain4'] = Wt('pehle', 'najaiz')
    P['pehle_out'] = S('pehle')['t1'] - 0.35
    P['ab_tag'] = S('ab')['t0'] + 0.12
    P['net_in'] = Wt('ab', 'khawateen') - 0.2
    P['net_lines'] = Wt('ab', 'khawateen') - 0.05
    P['net_free'] = Wt('ab', 'paband') - 0.1
    P['net_auth'] = Wt('ab', 'authorized') - 0.15
    P['ab_out'] = S('ab')['t1'] - 0.35
    P['rush_a'] = Wt('rush', 'rush') - 0.15
    P['rush_taawun'] = Wt('rush', 'taawun') - 0.1
    P['rush_b'] = Wt('rush', 'doosre') - 0.1
    P['rush_pick'] = Wt('rush', 'intikhab')
    P['rush_out'] = S('rush')['t1'] - 0.3
    P['banks_head'] = Wt('banks', '6') - 0.1
    names = [('habib', 0), ('hbl', 0), ('easypaisa', 0), ('jazzcash', 0), ('punjab', 0), ('alfalah', 0)]
    P['bank_t'] = [Wt('banks', n, k) - (0.25 if n == 'punjab' else 0.05) for n, k in names]
    P['banks_out'] = S('banks')['t1'] - 0.35
    P['faide_head'] = Wt('faide', 'paanch') - 0.15
    P['faida_t'] = [Wt('faide', 'retailers'), Wt('faide', 'apni'), Wt('faide', 'lambi'), Wt('faide', 'najaiz'),
                    Wt('faide', 'aur', 1) if False else Wt('faide', 'digital')]
    P['faide_out'] = S('faide')['t1'] - 0.35
    P['steps_title'] = S('steps_a')['t0'] + 0.15
    P['step_t'] = [Wt('steps_a', 'sab'), Wt('steps_a', 'is'), Wt('steps_a', 'apni', 0), Wt('steps_a', 'is', 1)]
    P['steps_out'] = S('steps_b')['t1'] - 0.3
    P['hid_in'] = S('hidayat')['t0'] + 0.1
    P['hid_phone'] = Wt('hidayat', 'apna') - 0.1
    P['hid_wallet'] = Wt('hidayat', 'yeh') - 0.1
    P['hid_out'] = S('hidayat')['t1'] - 0.3
    P['cr_in'] = S('crore')['t0'] + 0.1
    P['cr_chip1'] = Wt('crore', 'wallets') - 0.2
    P['cr_chip2'] = Wt('crore', 'interoperable') - 0.1
    P['cr_globe'] = Wt('crore', 'pakistan') - 0.1
    P['cr_world'] = Wt('crore', 'duniya') - 0.15
    P['cr_out'] = S('crore')['t1'] - 0.3
    P['kh_chip1'] = Wt('khwab', 'paison') - 0.1
    P['kh_chip2'] = Wt('khwab', 'madad') - 0.15
    P['kh_chips_out'] = Wt('khwab', 'benazir') - 0.35
    P['kh_title'] = Wt('khwab', 'benazir') - 0.05
    P['kh_title2'] = Wt('khwab', 'benazir', 1) - 0.05
    P['kh_line2'] = Wt('khwab', 'har') - 0.05
    P['end_in'] = TL.speech_end - 0.15
    return P


PLAN = build_plan()

# caption suppression (graphics carry the words there)
CAP_OFF = [
    (0.0, S('hook')['t1']),
    (S('whatis')['t0'] - 0.05, S('whatis')['t1']),
    (PLAN['bank_t'][0] - 0.05, S('banks')['t1']),
    (PLAN['faida_t'][0] - 0.05, S('faide')['t1']),
    (PLAN['kh_title'] - 0.05, 1e9),
]

# transitions at clip changes: segment id -> type of the cut INTO it
TRANS = {'wallets': 'glass', 'anytime': 'whip', 'vision_a': 'glass', 'vision_b': 'punch', 'whatis': 'flash',
         'pehle': 'glass', 'ab': 'flash', 'rush': 'punch', 'banks': 'glass', 'faide': 'whip', 'steps_a': 'glass',
         'steps_b': 'punch', 'hidayat': 'whip', 'crore': 'glass', 'khwab': 'punch'}
GLASS_HALF = 0.24
WHIP_HALF = 0.15


# ---- footage ---------------------------------------------------------------------------------------------------------
def clip_frames(clip):
    if clip not in CLIP_DUR:
        d = os.path.join(WS, 'frames', clip)
        CLIP_DUR[clip] = len([f for f in os.listdir(d) if f.endswith('.jpg')])
    return CLIP_DUR[clip]


@lru_cache(48)
def load(clip, idx):
    n = clip_frames(clip)
    idx = int(min(max(idx, 0), n - 1))
    im = cv2.imread(os.path.join(WS, 'frames', clip, f'{idx:05d}.jpg'), cv2.IMREAD_COLOR)
    f = im[..., ::-1].astype(np.float32) * (1 / 255.0)
    f.setflags(write=False)
    return f


def src_frame(clip, src_t):
    return load(clip, int(round(src_t * FPS)))


def zoom_frame(img, z, clip, dx=0.0, dy=0.0):
    if abs(z - 1) < 1e-4 and dx == 0 and dy == 0:
        return img.copy()
    f = FACES[clip]
    px, py = f['cx'], f['cy'] - 0.15 * f['size']
    M = np.float32([[z, 0, px - z * px + dx], [0, z, py - z * py + dy]])
    return cv2.warpAffine(img, M, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)


def seg_zoom(s, t):
    q = (t - s['t0']) / max(1e-3, s['t1'] - s['t0'])
    return s['zoom'] * (1 + 0.045 * q)


def seg_image(s, t, extra_z=1.0, src_shift=0.0):
    """Footage of segment s at output time t (t may lie outside the segment: handles)."""
    src = s['a'] + (t - s['t0']) * edl.SPEED + src_shift
    src = min(max(src, 0.0), clip_frames(s['clip']) / FPS - 1 / FPS)
    img = src_frame(s['clip'], src)
    z = seg_zoom(s, min(max(t, s['t0']), s['t1'])) * extra_z
    out = zoom_frame(img, z, s['clip'])
    return look_adjust(out, s, t)


def look_adjust(img, s, t):
    # "Pehle" (the old way) is told in a muted, cooler memory grade; colour floods back at "Ab".
    if s['id'] == 'pehle':
        k = 0.62
        lum = img @ np.array([0.2126, 0.7152, 0.0722], np.float32)
        img = lum[..., None] + (img - lum[..., None]) * (1 - k)
        img = img * np.array([0.97, 1.0, 1.04], np.float32) * 0.94 + 0.015
    elif s['id'] == 'ab':
        q = K.ease_out_cubic(K.lin(t, s['t0'], s['t0'] + 0.5))
        if q < 1:
            k = 0.62 * (1 - q)
            lum = img @ np.array([0.2126, 0.7152, 0.0722], np.float32)
            img = lum[..., None] + (img - lum[..., None]) * (1 - k)
    return img


def base_frame(t):
    segs = TL.segs
    # end card: keep the last shot running a little, then hold
    if t >= TL.speech_end:
        s = segs[-1]
        return seg_image(s, t)
    s = TL.seg_at(t)
    i = segs.index(s)
    # transition into s (at s.t0) or out of s (into next at s.t1)
    for j, T in ((i, s['t0']), (i + 1, s['t1'])):
        if j <= 0 or j >= len(segs):
            continue
        typ = TRANS.get(segs[j]['id'], 'cut')
        a, b = segs[j - 1], segs[j]
        if typ == 'glass' and abs(t - T) < GLASS_HALF:
            return glass_wipe(a, b, t, T)
        if typ == 'whip' and abs(t - T) < WHIP_HALF:
            return whip(a, b, t, T)
    img = seg_image(s, t)
    typ = TRANS.get(s['id'], 'cut')
    if typ in ('punch', 'flash') and t - s['t0'] < 0.2:
        q = K.lin(t, s['t0'], s['t0'] + 0.2)
        img = zoom_frame_center(img, 1 + 0.045 * (1 - K.ease_out_cubic(q)))
        if typ == 'flash':
            img = img * (1 + 0.45 * (1 - q) ** 3)
    return img


def zoom_frame_center(img, z):
    M = np.float32([[z, 0, W / 2 - z * W / 2], [0, z, H / 2 - z * H / 2]])
    return cv2.warpAffine(img, M, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)


def glass_wipe(a, b, t, T):
    q = K.ease_io((t - (T - GLASS_HALF)) / (2 * GLASS_HALF))
    old = seg_image(a, t)
    new = seg_image(b, t)
    bw = 200
    xw = -bw + q * (W + 2 * bw)
    xs = np.arange(W, dtype=np.float32)
    m = np.clip((xw - xs) / 2 + 0.5, 0, 1)[None, :, None]     # left of the bar = new shot
    img = new * m + old * (1 - m)
    K.glass(img, xw, H / 2, bw, H + 400, bw / 2, refract=60, bevel=90, blur=24, tint=K.GREEN_L, tint_a=0.08,
            shadow=0.0, rim=1.0, sheen=0.0, chroma=0.8)
    return img


def whip(a, b, t, T):
    acc = np.zeros((H, W, 3), np.float32)
    n = 12
    for k in range(n):
        tt = t + (k - (n - 1) / 2) / n / FPS
        if tt < T:
            q = K.ease_in_expo(K.lin(tt, T - WHIP_HALF, T))
            acc += seg_image(a, tt, extra_z=1 + 0.55 * q)
        else:
            q = 1 - K.ease_out_expo(K.lin(tt, T, T + WHIP_HALF))
            acc += seg_image(b, tt, extra_z=1 + 0.45 * q)
    img = acc / n
    q = 1 - abs(t - T) / WHIP_HALF
    return img + 0.25 * q ** 2


# ---- UI building blocks ---------------------------------------------------------------------------------------------
STY = {
    'dark': dict(tint=K.GREEN_D, tint_a=0.34, dark=0.42, lift=0.0, vibrancy=1.15, rim=0.85, sheen=0.07),
    'deep': dict(tint=K.GREEN_D, tint_a=0.48, dark=0.55, lift=0.0, vibrancy=1.1, rim=0.9, sheen=0.06),
    'light': dict(tint=(1, 1, 1), tint_a=0.12, dark=0.0, lift=0.05, vibrancy=1.25, rim=0.9, sheen=0.10),
    'green': dict(tint=K.GREEN, tint_a=0.55, dark=0.25, lift=0.0, vibrancy=1.1, rim=0.95, sheen=0.10),
    'gold': dict(tint=K.GOLD_D, tint_a=0.45, dark=0.30, lift=0.0, vibrancy=1.1, rim=1.0, sheen=0.12),
    'red': dict(tint=(0.45, 0.06, 0.08), tint_a=0.45, dark=0.45, lift=0.0, vibrancy=1.0, rim=0.8, sheen=0.05),
    'amber': dict(tint=(0.55, 0.32, 0.02), tint_a=0.5, dark=0.42, lift=0.0, vibrancy=1.0, rim=1.0, sheen=0.08),
}


def anim(t, t_in, t_out, d_in=0.38, d_out=0.24):
    """-> (alpha, scale, in_progress, dy) for a pop-in / pop-out element; alpha 0 = hidden."""
    if t < t_in or t > t_out + d_out:
        return 0.0, 0.0, 0.0, 0.0
    pin = K.lin(t, t_in, t_in + d_in)
    pout = K.lin(t, t_out, t_out + d_out)
    a = min(K.ease_out_cubic(min(1, pin * 1.7)), 1 - K.ease_in_cubic(pout))
    s = (0.80 + 0.20 * K.ease_out_back(pin, 2.0)) * (1 - 0.10 * K.ease_in_cubic(pout))
    dy = (1 - K.ease_out_cubic(pin)) * 36 + K.ease_in_cubic(pout) * -20
    return a, s, pin, dy


class Box:
    """A glass panel whose children are placed in its local coordinates (scaled/faded with it)."""

    def __init__(self, f, t, cx, cy, w, h, t_in, t_out, r=44, style='dark', d_in=0.38, d_out=0.24, **gk):
        self.f = f
        self.a, self.s, self.p, dy = anim(t, t_in, t_out, d_in, d_out)
        self.cx, self.cy = cx, cy + dy
        self.ok = self.a > 0.003
        if self.ok:
            g = dict(STY[style]); g.update(gk)
            K.glass(f, self.cx, self.cy, w * self.s, h * self.s, r * self.s, alpha=self.a, **g)

    def pos(self, dx, dy):
        return self.cx + dx * self.s, self.cy + dy * self.s

    def put(self, L, dx, dy, alpha=1.0, scale=1.0, anchor='c'):
        if not self.ok or alpha <= 0: return
        x, y = self.pos(dx, dy)
        if anchor == 'l':
            K.blit(self.f, L, x, y, self.a * alpha, self.s * scale, 'l')
        elif anchor == 'r':
            K.blit(self.f, L, x, y, self.a * alpha, self.s * scale, 'r')
        else:
            K.blit(self.f, L, x, y, self.a * alpha, self.s * scale)


def T(s, size=40, w='xbold', color=(1, 1, 1), shadow=0.35, grad=None, tracking=0):
    return K.text_layer(s, w, size, color=tuple(color), shadow=shadow, shadow_blur=6, shadow_dy=3,
                        gradient=grad, tracking=tracking)


def Tfit(s, max_w, size, w='bold', **kw):
    """Text layer scaled down (by font size) until it fits max_w px."""
    while size > 18:
        L = T(s, size, w, **kw)
        if L.shape[1] - 12 <= max_w: return L
        size -= 1
    return T(s, size, w, **kw)


def chip_width(text, size, h):
    L = T(text, size, 'bold')
    return L.shape[1] - 12 + int(h * 0.74) + 64


def chip(f, t, cx, cy, text, icon, t_in, t_out, style='dark', badge=K.GREEN, size=42, h=96, w=None, icon_fg=K.WHITE,
         tsize=None, text_color=(1, 1, 1)):
    L = T(text, tsize or size, 'bold', color=text_color)
    bw = int(h * 0.74)
    w = w or (L.shape[1] - 12 + bw + 64)
    b = Box(f, t, cx, cy, w, h, t_in, t_out, r=h / 2, style=style)
    if not b.ok: return b
    p = K.ease_out_back(K.lin(t, t_in + 0.08, t_in + 0.45), 2.4)
    b.put(K.icon_badge(icon, bw, bg=badge, fg=icon_fg), -w / 2 + h / 2, 0, scale=max(0.01, p))
    b.put(L, -w / 2 + h / 2 + bw / 2 + 18, 0, anchor='l')
    return b


# ---- scenes ------------------------------------------------------------------------------------------------------------
def sc_logo(f, t):
    """Official BISP banner in a glass pill, top centre; it flies into the end card."""
    P = PLAN
    if t < P['logo_in']: return
    a = K.ease_out_cubic(K.lin(t, P['logo_in'], P['logo_in'] + 0.4))
    drop = (1 - K.ease_out_back(K.lin(t, P['logo_in'], P['logo_in'] + 0.55), 1.8)) * -60
    pulse = 1 + 0.10 * math.exp(-((t - P['logo_pulse'] - 0.25) / 0.22) ** 2)
    e = K.ease_io(K.lin(t, P['end_in'], P['end_in'] + 0.75))
    cx, cy = 540, 196 + drop
    wl = 280 * pulse
    # move into the end card
    cy = cy * (1 - e) + 690 * e
    wl = wl * (1 - e) + 880 * e
    hl = wl * 563 / 1600
    K.glass(f, cx, cy, wl + 34, hl + 30, 30 + 14 * e, alpha=a, **STY['light'])
    K.blit(f, K.logo_layer(880), cx, cy, a, wl / 880)


def sc_hook(f, t):
    P = PLAN
    t_out = P['hook_out']
    # line 1: BENAZIR KAFAALAT (gold, word pops)
    b = Box(f, t, CXL, LOW_Y - 40, 880, 300, P['hook_title1'], P['hook_interop'] - 0.18, r=56, style='deep')
    if b.ok:
        wa = T('BENAZIR', 72, 'black', grad=K.GOLD_GRAD, shadow=0.0).shape[1] - 12
        wb = T('KAFAALAT', 72, 'black', grad=K.GOLD_GRAD, shadow=0.0).shape[1] - 12
        tot = wa + wb + 52
        for i, (wd, dx) in enumerate((('BENAZIR', -tot / 2 + wa / 2), ('KAFAALAT', tot / 2 - wb / 2))):
            p = K.ease_out_back(K.lin(t, P['hook_title1'] + 0.12 + i * 0.22, P['hook_title1'] + 0.5 + i * 0.22), 1.3)
            if p > 0:
                b.put(T(wd, 72, 'black', grad=K.GOLD_GRAD, shadow=0.0), dx, -62, alpha=min(1, p * 1.5), scale=max(0.01, p))
        p2 = K.ease_out_cubic(K.lin(t, P['hook_title2'], P['hook_title2'] + 0.4))
        if p2 > 0:
            b.put(T('ka Naya', 44, 'semi'), 0, 22 + (1 - p2) * 20, alpha=p2)
            b.put(T('Digital Payment System', 54, 'xbold'), 0, 86 + (1 - p2) * 24, alpha=p2)
    # INTEROPERABILITY slab (slam)
    ti = P['hook_interop']
    b2 = Box(f, t, CXL, LOW_Y - 70, 900, 170, ti, t_out, r=50, style='deep', d_in=0.28)
    if b2.ok:
        slam = 1 + 0.35 * (1 - K.ease_out_expo(K.lin(t, ti, ti + 0.3)))
        b2.put(T('INTEROPERABILITY', 76, 'black', grad=K.GOLD_GRAD, shadow=0.0), 0, -4, scale=slam)
        # light sweep across the word
        sw = K.lin(t, ti + 0.3, ti + 1.1)
        if 0 < sw < 1:
            x0, y0 = b2.pos(-470 + 940 * sw, 0)
            K.blit(f, sweep_layer(), x0, y0, 0.55 * math.sin(math.pi * sw) * b2.a)
    # Raqam Aapki / Intikhab Bhi Aapka
    for k, (txt, ic, tt, sty, bg) in enumerate((('Raqam Aapki,', 'cash', P['hook_raqam'], 'green', K.GREEN_D),
                                               ('Intikhab Bhi Aapka!', 'check', P['hook_intikhab'], 'gold', K.GOLD_D))):
        chip(f, t, CXL, LOW_Y + 70 + k * 112, txt, ic, tt - 0.05, t_out, style=sty, badge=bg, size=46, h=100)


@lru_cache(1)
def sweep_layer():
    w, h = 160, 150
    xx = np.linspace(-1, 1, w, dtype=np.float32)[None, :]
    yy = np.linspace(-1, 1, h, dtype=np.float32)[:, None]
    a = np.exp(-(xx * 2.2) ** 2) * (1 - yy ** 2) * 0.9
    a = cv2.warpAffine(a, np.float32([[1, -0.35, 26], [0, 1, 0]]), (w, h))
    L = np.zeros((h, w, 4), np.float32)
    L[..., 3] = a
    L[..., :3] = a[..., None]
    return L


def counter_text(q):
    n = int(round(q * 10000000))
    s = f'{n:,}'
    # Pakistani grouping: 1,00,00,000
    s = str(n)
    if len(s) > 3:
        head, tail = s[:-3], s[-3:]
        parts = []
        while len(head) > 2:
            parts.insert(0, head[-2:]); head = head[:-2]
        if head: parts.insert(0, head)
        s = ','.join(parts + [tail])
    return s + '+'


def sc_wallets(f, t):
    P = PLAN
    t_in, t_out = P['crore_in'], P['crore_out']
    b = Box(f, t, CX, TOP_Y + 10, 900, 300, t_in, t_out, r=52, style='dark')
    if not b.ok: return
    b.put(K.icon_badge('wallet', 150, bg=K.GREEN), -330, 0, scale=max(0.01, K.ease_out_back(K.lin(t, t_in + 0.1, t_in + 0.5), 2.2)))
    q = K.ease_out_expo(K.lin(t, t_in + 0.15, t_in + 1.5))
    b.put(T(counter_text(q), 78, 'black', grad=K.GOLD_GRAD, shadow=0.0), -225, -42, anchor='l')
    p = K.ease_out_cubic(K.lin(t, t_in + 0.6, t_in + 1.0))
    b.put(T('Mustahiq khawateen ke', 38, 'semi'), -225, 34, alpha=p, anchor='l')
    b.put(T('Digital Wallets qaim', 44, 'xbold', color=K.GOLD_L), -225, 88, alpha=p, anchor='l')


def sc_anytime(f, t):
    P = PLAN
    items = (('Poore Pakistan mein', 'pin', P['any_pak']), ('Kisi bhi waqt', 'clock', P['any_waqt']),
             ('Kisi bhi din', 'calendar', P['any_din']), ('Apni sahulat ke mutabiq', 'heart', P['any_sahulat']))
    for k, (txt, ic, tt) in enumerate(items):
        chip(f, t, CX, 330 + k * 110, txt, ic, tt, P['any_out'] + k * 0.05, style='dark', size=44, h=96)


def sc_vision(f, t):
    P = PLAN
    for k, (role, name, tt) in enumerate((('SADR-E-PAKISTAN', 'Asif Ali Zardari', P['plate1']),
                                          ('WAZIR-E-AZAM', 'Muhammad Shehbaz Sharif', P['plate2']))):
        Ln = T(name, 44, 'xbold')
        pw = Ln.shape[1] + 150
        px = 70 + pw / 2
        b = Box(f, t, px, LOW_Y - 70 + k * 150, pw, 128, tt, P['plates_out'] + k * 0.06, r=34, style='dark')
        if b.ok:
            b.put(K.icon_badge('person', 84, bg=K.GREEN), -pw / 2 + 64, 0)
            b.put(T(role, 26, 'ui_b', color=K.GOLD, tracking=3, shadow=0.0), -pw / 2 + 120, -26, anchor='l')
            b.put(Ln, -pw / 2 + 120, 18, anchor='l')
    b = Box(f, t, CX, TOP_Y, 860, 230, P['maali_in'], P['maali_out'], r=48, style='dark')
    if b.ok:
        b.put(K.icon_badge('rise', 132, bg=K.GOLD_D), -310, 0)
        b.put(T('Khawateen ki', 38, 'semi'), -220, -52, anchor='l')
        b.put(T('Maali Khudmukhtari', 54, 'black', grad=K.GOLD_GRAD, shadow=0.0), -220, 6, anchor='l')
        b.put(T('ki taraf ek aham qadam', 34, 'semi', color=(0.9, 0.95, 0.92)), -220, 62, anchor='l')


def sc_whatis(f, t):
    P = PLAN
    t_in, t_out = P['whatis_in'], P['whatis_out']
    b = Box(f, t, CXL, LOW_Y - 20, 880, 300, t_in, t_out, r=60, style='deep', d_in=0.26)
    if not b.ok: return
    slam = 1 + 0.4 * (1 - K.ease_out_expo(K.lin(t, t_in, t_in + 0.32)))
    b.put(T('INTEROPERABILITY', 78, 'black', grad=K.GOLD_GRAD, shadow=0.0), 0, -52, scale=slam)
    p = K.ease_out_back(K.lin(t, t_in + 0.35, t_in + 0.75), 2.2)
    if p > 0:
        b.put(T('kya hai?', 70, 'black'), -40, 58, scale=max(0.01, p))
        b.put(K.icon_badge('question', 92, bg=K.GOLD_D), 175, 58, scale=max(0.01, p), alpha=1)


def sc_pehle(f, t):
    P = PLAN
    s = S('pehle')
    b = Box(f, t, 205, 196, 250, 82, P['pehle_tag'], P['pehle_out'], r=41, style='red')
    if b.ok:
        b.put(K.icon('cross', 34, (1, 0.8, 0.8)), -78, 0)
        b.put(T('PEHLE', 38, 'black', tracking=4), 22, 0)
    items = (('Sirf ek khaas bank ka retailer', 'store', P['pain1']), ('Lambi qataarein', 'users', P['pain2']),
             ('Intezar', 'clock', P['pain3']), ('Najaiz katautiyan', 'cash', P['pain4']))
    for k, (txt, ic, tt) in enumerate(items):
        chip(f, t, CX, 330 + k * 104, txt, ic, tt, P['pehle_out'] + k * 0.04, style='red', badge=(0.62, 0.1, 0.12),
             size=40, h=90)


NET_NODES = [(-330, 0), (-230, 130), (0, 170), (230, 130), (330, 0), (0, -112)]


def sc_ab(f, t):
    P = PLAN
    b = Box(f, t, 205, 196, 190, 82, P['ab_tag'], P['ab_out'], r=41, style='green')
    if b.ok:
        b.put(K.icon('check', 36), -50, 0)
        b.put(T('AB', 40, 'black', tracking=4), 22, 0)
    # network: one woman, many retailers
    bx = Box(f, t, CX, 490, 900, 400, P['net_in'], P['ab_out'], r=56, style='dark')
    if not bx.ok: return
    cxy = (0, -10)
    for k, (dx, dy) in enumerate(NET_NODES):
        tk = P['net_lines'] + k * 0.12
        q = K.ease_out_cubic(K.lin(t, tk, tk + 0.35))
        if q <= 0: continue
        x0, y0 = bx.pos(*cxy)
        x1, y1 = bx.pos(cxy[0] + dx * q, cxy[1] + dy * q * 0.8)
        lit = K.lin(t, P['net_free'], P['net_free'] + 0.3)
        col = np.array(K.GOLD) * lit + np.array((0.85, 0.95, 0.9)) * (1 - lit)
        line(f, x0, y0, x1, y1, col, 4 * bx.s, bx.a * 0.9)
        p = K.ease_out_back(K.lin(t, tk + 0.2, tk + 0.55), 2.2)
        if p > 0:
            bx.put(K.icon_badge('store', 78, bg=K.GREEN), dx, dy * 0.8, scale=max(0.01, p))
            ka = K.ease_out_back(K.lin(t, P['net_auth'] + k * 0.08, P['net_auth'] + 0.35 + k * 0.08), 2.5)
            if ka > 0:
                bx.put(K.icon_badge('check', 34, bg=K.GOLD_D), dx + 28, dy * 0.8 - 28, scale=max(0.01, ka))
    bx.put(K.icon_badge('woman', 120, bg=K.GOLD_D), *cxy)
    p = K.ease_out_cubic(K.lin(t, P['net_free'], P['net_free'] + 0.35))
    p2 = K.ease_out_cubic(K.lin(t, P['net_auth'], P['net_auth'] + 0.35))
    if p > 0:
        txt = 'Kisi ek bank ki paband nahi' if p2 < 0.5 else 'Kisi bhi Authorized Retailer se'
        a = p * (1 - 2 * min(p2, 0.5)) if p2 < 0.5 else (p2 - 0.5) * 2
        bx.put(T(txt, 32, 'bold', color=K.GOLD_L), 0, -160, alpha=a)


def line(f, x0, y0, x1, y1, col, wpx, a):
    """Anti-aliased line drawn into the frame."""
    pad = int(wpx * 2 + 4)
    xa, ya = int(min(x0, x1)) - pad, int(min(y0, y1)) - pad
    xb, yb = int(max(x0, x1)) + pad, int(max(y0, y1)) + pad
    xa, ya, xb, yb = max(xa, 0), max(ya, 0), min(xb, W), min(yb, H)
    if xb <= xa or yb <= ya: return
    yy, xx = np.mgrid[ya:yb, xa:xb].astype(np.float32)
    dx, dy = x1 - x0, y1 - y0
    L2 = dx * dx + dy * dy + 1e-6
    u = np.clip(((xx - x0) * dx + (yy - y0) * dy) / L2, 0, 1)
    d = np.hypot(xx - (x0 + u * dx), yy - (y0 + u * dy))
    m = np.clip(wpx / 2 + 0.5 - d, 0, 1)[..., None] * a
    f[ya:yb, xa:xb] = f[ya:yb, xa:xb] * (1 - m) + np.array(col, np.float32) * m


def sc_rush(f, t):
    P = PLAN
    # retailer A: rush / no co-operation
    b = Box(f, t, 285, TOP_Y + 20, 420, 360, P['rush_a'], P['rush_out'], r=48, style='red')
    if b.ok:
        fade = 1 - 0.45 * K.lin(t, P['rush_b'], P['rush_b'] + 0.4)
        b.put(K.icon_badge('store', 110, bg=(0.5, 0.1, 0.12)), 0, -92, alpha=fade)
        b.put(T('Retailer 1', 40, 'xbold'), 0, 8, alpha=fade)
        p = K.ease_out_back(K.lin(t, P['rush_a'] + 0.15, P['rush_a'] + 0.5), 2)
        b.put(T('Rush', 36, 'semi', color=(1, 0.8, 0.8)), -60, 72, alpha=p * fade)
        b.put(K.icon('users', 46, (1, 0.8, 0.8)), 40, 70, alpha=p * fade)
        p2 = K.ease_out_back(K.lin(t, P['rush_taawun'], P['rush_taawun'] + 0.4), 2)
        b.put(T('Taawun nahi', 34, 'semi', color=(1, 0.8, 0.8)), 0, 124, alpha=p2 * fade)
        x = K.ease_out_back(K.lin(t, P['rush_b'] - 0.1, P['rush_b'] + 0.3), 2.5)
        if x > 0:
            b.put(K.icon_badge('cross', 70, bg=K.RED), 150, -130, scale=max(0.01, x))
    # arrow
    q = K.ease_out_cubic(K.lin(t, P['rush_b'], P['rush_b'] + 0.35))
    a_out = 1 - K.lin(t, P['rush_out'], P['rush_out'] + 0.24)
    if q > 0 and a_out > 0:
        K.blit(f, K.icon_badge('arrow', 76, bg=K.GOLD_D), 540, TOP_Y + 20, q * a_out, 0.6 + 0.4 * q)
    b = Box(f, t, 795, TOP_Y + 20, 420, 360, P['rush_b'], P['rush_out'], r=48, style='green')
    if b.ok:
        b.put(K.icon_badge('store', 110, bg=K.GREEN_D), 0, -92)
        b.put(T('Doosra Retailer', 38, 'xbold'), 0, 8)
        p = K.ease_out_back(K.lin(t, P['rush_pick'] - 0.1, P['rush_pick'] + 0.3), 2.2)
        b.put(T('Aapka intikhab', 36, 'bold', color=K.GOLD_L), 0, 72, alpha=p)
        if p > 0:
            b.put(K.icon_badge('check', 70, bg=K.GOLD_D), 150, -130, scale=max(0.01, p))


BANKS = ['Habib Bank Limited', 'HBL Microfinance Bank', 'Easypaisa', 'JazzCash', 'Bank of Punjab', 'Bank Alfalah']


@lru_cache(1)
def bank_size():
    """One font size for all six tiles: the largest at which every name fits the tile."""
    size = 34
    while size > 20 and max(T(n, size, 'bold').shape[1] - 12 for n in BANKS) > 340:
        size -= 1
    return size


def sc_banks(f, t):
    P = PLAN
    b = Box(f, t, CX, 362, 640, 150, P['banks_head'], P['banks_out'], r=75, style='dark')
    if b.ok:
        p = K.ease_out_back(K.lin(t, P['banks_head'] + 0.05, P['banks_head'] + 0.45), 2.3)
        b.put(T('6', 112, 'black', grad=K.GOLD_GRAD, shadow=0.0), -210, 4, scale=max(0.01, p))
        b.put(T('Banking', 44, 'xbold'), -140, -26, anchor='l')
        b.put(T('Partners', 44, 'xbold', color=K.GOLD_L), -140, 26, anchor='l')
        b.put(K.icon_badge('bank', 86, bg=K.GREEN), 230, 0)
    # single-column list (names at full size), growing as she names each bank
    t_in = P['bank_t'][0] - 0.12
    grow = sum(K.ease_out_cubic(K.lin(t, tk - 0.2, tk + 0.12)) for tk in P['bank_t'][1:])
    rh = 68
    hh = 56 + rh * (1 + grow)
    top = LOW_Y - 215
    bx = Box(f, t, CXL, top + hh / 2, 860, hh, t_in, P['banks_out'], r=40, style='dark')
    if not bx.ok: return
    for k, name in enumerate(BANKS):
        tk = P['bank_t'][k]
        p = K.ease_out_back(K.lin(t, tk - 0.08, tk + 0.3), 2.0)
        if p <= 0: continue
        y = -hh / 2 + 28 + rh / 2 + k * rh
        bx.put(K.disc(50, K.GOLD_D, ring=K.GOLD_L, ring_w=2), -372, y, scale=max(0.01, p))
        bx.put(T(str(k + 1), 27, 'black', shadow=0.0), -372, y + 1, alpha=min(1, p))
        a2 = K.ease_out_cubic(K.lin(t, tk - 0.05, tk + 0.25))
        bx.put(T(name, 34, 'bold'), -332 + (1 - a2) * 24, y, alpha=a2, anchor='l')
        if k < 5 and t >= P['bank_t'][k + 1] - 0.2:
            x0, y0 = bx.pos(-340, y + rh / 2)
            x1, _ = bx.pos(380, y + rh / 2)
            line(f, x0, y0, x1, y0, (1, 1, 1), 1.2 * bx.s, bx.a * 0.18 * K.lin(t, P['bank_t'][k + 1] - 0.2, P['bank_t'][k + 1]))


FAIDE = ['Retailers ki monopoly ka khatma', 'Apni marzi se retailer chunne ki azadi', 'Lambi qataron aur intezar mein kami',
         'Najaiz katautiyon ki hosla shikni', 'Digital wallets: mehfooz payments']
FAIDE2 = {4: 'aur financial facilities tak rasai'}


def sc_faide(f, t):
    P = PLAN
    b = Box(f, t, CX, 362, 640, 150, P['faide_head'], P['faide_out'], r=75, style='dark')
    if b.ok:
        n = sum(1 for tt in P['faida_t'] if t >= tt)
        p = K.ease_out_back(K.lin(t, P['faide_head'] + 0.05, P['faide_head'] + 0.45), 2.3)
        b.put(T('5', 112, 'black', grad=K.GOLD_GRAD, shadow=0.0), -210, 4, scale=max(0.01, p))
        b.put(T('Naye System', 40, 'xbold'), -140, -26, anchor='l')
        b.put(T('ke Faide', 44, 'xbold', color=K.GOLD_L), -140, 26, anchor='l')
        # progress ring dots
        for k in range(5):
            on = k < n
            b.put(K.disc(20, K.GOLD if on else (0.5, 0.55, 0.52)), 150 + k * 30, 0)
    t_in = P['faida_t'][0] - 0.15
    grow = sum(K.ease_out_cubic(K.lin(t, tk - 0.2, tk + 0.15)) for tk in P['faida_t'][1:])
    hh = 100 + 82 * (1 + grow) + 10 * K.lin(t, P['faida_t'][4] - 0.2, P['faida_t'][4] + 0.15)
    top = LOW_Y - 195
    bx = Box(f, t, CXL, top + hh / 2, 860, hh, t_in, P['faide_out'], r=46, style='dark')
    if not bx.ok: return
    for k, txt in enumerate(FAIDE):
        tk = P['faida_t'][k]
        p = K.ease_out_back(K.lin(t, tk - 0.05, tk + 0.35), 2.0)
        if p <= 0: continue
        y = -hh / 2 + 62 + k * 82 + (8 if k == 4 else 0)
        bx.put(K.icon_badge('check', 54, bg=K.GREEN_L if k < 4 else K.GOLD_D), -372, y, scale=max(0.01, p))
        a = K.ease_out_cubic(K.lin(t, tk, tk + 0.3))
        bx.put(T(txt, 33, 'bold'), -332 + (1 - a) * 24, y - (12 if k in FAIDE2 else 0), alpha=a, anchor='l')
        if k in FAIDE2:
            bx.put(T(FAIDE2[k], 28, 'semi', color=K.GOLD_L), -332 + (1 - a) * 24, y + 28, alpha=a, anchor='l')


STEPS = [
    ('sms', 'Bank ka SMS aayega', 'Account mein jama (Credit) raqam'),
    ('idcard', 'Asal CNIC + Registered Mobile', 'Partner bank ke Authorized Retailer'),
    ('fingerprint', 'Biometric Verification', 'Raqam lein aur poori gin lein'),
    ('shield', 'Doosra SMS mehfooz rakhein', 'Apne payment record ke liye'),
]


def sc_steps(f, t):
    P = PLAN
    t0, t_out = P['steps_title'], P['steps_out']
    st = P['step_t']
    # title chip, then the stepper card
    b = Box(f, t, CX, 340, 720, 104, t0, st[0] - 0.25, r=52, style='gold')
    if b.ok:
        b.put(T('Raqam kaise hasil karein?', 46, 'black'), 0, 0)
    bx = Box(f, t, CX, TOP_Y + 10, 920, 380, st[0] - 0.12, t_out, r=56, style='dark')
    if not bx.ok: return
    cur = max([k for k in range(4) if t >= st[k] - 0.12] or [0])
    # stepper header
    for k in range(4):
        x = -210 + k * 140
        done = t >= st[k] - 0.1
        fill = K.ease_out_back(K.lin(t, st[k] - 0.1, st[k] + 0.25), 2.0)
        if k < 3:
            q = K.lin(t, st[k + 1] - 0.4, st[k + 1] - 0.1)
            x0, y0 = bx.pos(x + 30, -140)
            x1, y1 = bx.pos(x + 30 + 80 * q, -140)
            line(f, x0, y0, bx.pos(x + 110, -140)[0], y0, (0.6, 0.66, 0.62), 4 * bx.s, bx.a * 0.6)
            if q > 0:
                line(f, x0, y0, x1, y1, K.GOLD, 5 * bx.s, bx.a)
        bx.put(K.disc(54, (0.35, 0.42, 0.38)), x, -140)
        if done:
            bx.put(K.disc(54, K.GOLD_D, ring=K.GOLD_L, ring_w=2), x, -140, scale=max(0.01, fill))
        bx.put(T(str(k + 1), 28, 'black', shadow=0.0), x, -139)
    bx.put(T('STEP', 22, 'ui_b', color=K.GOLD, tracking=4, shadow=0.0), 330, -140)
    # content: outgoing slides left, incoming slides in from the right
    for k in range(4):
        tin = st[k] - 0.12
        tnext = st[k + 1] - 0.12 if k < 3 else 1e9
        if t < tin or t > tnext: continue
        pin = K.ease_out_cubic(K.lin(t, tin, tin + 0.35))
        pout = K.ease_in_cubic(K.lin(t, tnext - 0.2, tnext - 0.02))
        dx = (1 - pin) * 60 - pout * 60
        a = min(pin, 1 - pout)
        ic, l1, l2 = STEPS[k]
        pop = K.ease_out_back(K.lin(t, tin + 0.05, tin + 0.45), 2.2)
        bx.put(K.icon_badge(ic, 156, bg=K.GREEN), -320 + dx, 40, alpha=a, scale=max(0.01, pop))
        bx.put(Tfit(l1, 600, 44, 'xbold'), -210 + dx, 8, alpha=a, anchor='l')
        bx.put(Tfit(l2, 600, 32, 'semi', color=K.GOLD_L), -210 + dx, 68, alpha=a, anchor='l')
        if k in (0, 3):
            ping = K.lin(t, tin + 0.3, tin + 1.0)
            if 0 < ping < 1:
                bx.put(K.disc(30, K.RED, ring=(1, 1, 1), ring_w=3), -262 + dx, -22, alpha=a * (1 - ping * 0.2),
                       scale=1 + 0.25 * math.sin(ping * math.pi))
                bx.put(T('1', 18, 'black', shadow=0.0), -262 + dx, -21, alpha=a)


def sc_hidayat(f, t):
    P = PLAN
    b = Box(f, t, CXL, LOW_Y - 40, 860, 330, P['hid_in'], P['hid_out'], r=52, style='amber')
    if not b.ok: return
    p = K.ease_out_back(K.lin(t, P['hid_in'] + 0.05, P['hid_in'] + 0.45), 2.2)
    b.put(K.icon_badge('warning', 84, bg=(0.85, 0.5, 0.02)), -330, -102, scale=max(0.01, p))
    b.put(T('ZAROORI HIDAYAT', 46, 'black', color=K.GOLD_L, tracking=2), -270, -102, anchor='l')
    sw = K.ease_out_cubic(K.lin(t, P['hid_wallet'] - 0.05, P['hid_wallet'] + 0.35))
    a1 = K.ease_out_cubic(K.lin(t, P['hid_phone'], P['hid_phone'] + 0.35)) * (1 - sw)
    if a1 > 0:
        b.put(K.icon_badge('sim', 104, bg=(0.5, 0.1, 0.12)), -312, 40, alpha=a1)
        b.put(K.icon_badge('cross', 44, bg=K.RED), -272, 2, alpha=a1)
        b.put(T('Mobile phone aur SIM', 40, 'xbold'), -235, 14, alpha=a1, anchor='l')
        b.put(T('kisi ghair mutaliqa shakhs ko na dein', 30, 'semi', color=(1, 0.92, 0.8)), -235, 64, alpha=a1, anchor='l')
    if sw > 0:
        b.put(K.icon_badge('shield', 104, bg=K.GREEN), -312, 40, alpha=sw, scale=0.7 + 0.3 * K.ease_out_back(sw, 2))
        b.put(T('Yeh aapka Digital Wallet hai', 40, 'xbold'), -235 + (1 - sw) * 30, 14, alpha=sw, anchor='l')
        b.put(T('iski hifazat karein!', 34, 'bold', color=K.GOLD_L), -235 + (1 - sw) * 30, 64, alpha=sw, anchor='l')


def sc_crore(f, t):
    P = PLAN
    b = Box(f, t, CX, 400, 900, 230, P['cr_in'], P['cr_out'], r=52, style='dark')
    if b.ok:
        sw = K.ease_out_cubic(K.lin(t, P['cr_globe'], P['cr_globe'] + 0.4))
        b.put(K.icon_badge('woman', 140, bg=K.GOLD_D), -320, -10, alpha=1 - sw)
        b.put(K.icon_badge('globe', 140, bg=K.GREEN), -320, -10, alpha=sw, scale=0.7 + 0.3 * K.ease_out_back(sw, 2))
        if sw < 1:
            b.put(T('1 Crore+', 80, 'black', grad=K.GOLD_GRAD, shadow=0.0), -215, -38, alpha=1 - sw, anchor='l')
            b.put(T('khawateen jor di gayin', 38, 'semi'), -215, 40, alpha=1 - sw, anchor='l')
        if sw > 0:
            b.put(T('Ghair mamooli peshraft', 44, 'black', grad=K.GOLD_GRAD, shadow=0.0), -215, -36, alpha=sw, anchor='l')
            b.put(T('Pakistan aur aalami satah par', 34, 'semi'), -215, 28, alpha=sw, anchor='l')
    chips = (('Digital Wallets', 'wallet', P['cr_chip1']), ('Interoperable Payments', 'phone', P['cr_chip2']))
    chips2 = (('Financial Inclusion', 'rise', P['cr_world']), ('Digital Social Protection', 'shield', P['cr_world'] + 0.3))
    for grp, t_out, sty in ((chips, P['cr_world'] - 0.35, 'dark'), (chips2, P['cr_out'], 'gold')):
        ws = [chip_width(txt, 28, 78) for txt, _, _ in grp]
        gap = 24
        x = CX - (sum(ws) + gap) / 2
        for (txt, ic, tt), wch in zip(grp, ws):
            chip(f, t, x + wch / 2, 590, txt, ic, tt, t_out, style=sty, badge=K.GREEN, size=28, h=78, w=wch)
            x += wch + gap


def sc_khwab(f, t):
    P = PLAN
    for k, (txt, ic, tt) in enumerate((('Paison se juri sahuliyaat', 'hand_coin', P['kh_chip1']),
                                       ('Digital madad tak rasai', 'phone', P['kh_chip2']))):
        chip(f, t, CX, 330 + k * 112, txt, ic, tt, P['kh_chips_out'] + k * 0.05, style='dark', size=42, h=98)
    tt = P['kh_title']
    g2 = K.ease_out_cubic(K.lin(t, P['kh_title2'] - 0.15, P['kh_title2'] + 0.2))
    g3 = K.ease_out_cubic(K.lin(t, P['kh_line2'] - 0.15, P['kh_line2'] + 0.2))
    hh = 120 + 100 * g2 + 140 * g3
    top = LOW_Y + 20 - 180
    b = Box(f, t, CXL, top + hh / 2, 900, hh, tt, P['end_in'] - 0.1, r=60, style='deep')
    oy = (top + 180) - (top + hh / 2)   # keep children at fixed screen positions while the card grows
    if not b.ok: return
    p1 = K.ease_out_back(K.lin(t, tt + 0.02, tt + 0.4), 2.0)
    b.put(T('Benazir ka', 52, 'xbold'), 0, -112 + oy, scale=max(0.01, p1), alpha=min(1, p1 * 1.4))
    p2 = K.ease_out_back(K.lin(t, P['kh_title2'], P['kh_title2'] + 0.45), 2.0)
    if p2 > 0:
        b.put(T('Benazir Khwab!', 84, 'black', grad=K.GOLD_GRAD, shadow=0.0), 0, -30 + oy, scale=max(0.01, p2))
    p3 = K.ease_out_cubic(K.lin(t, P['kh_line2'], P['kh_line2'] + 0.45))
    if p3 > 0:
        b.put(T('Har Aurat Khud Mukhtar,', 46, 'xbold'), 0, 64 + oy + (1 - p3) * 20, alpha=p3)
        b.put(T('Ba Ikhtiyar!', 50, 'black', color=K.GOLD_L), 0, 124 + oy + (1 - p3) * 20, alpha=p3)
    # sparkles
    for k in range(7):
        ph = (t - tt) * 0.9 + k * 0.37
        q = ph % 1.0
        if t < P['kh_title2']: break
        side = -1 if k % 2 else 1
        x, y = b.pos(side * (400 + (k * 17) % 40), -hh / 2 + 30 + (k * 53) % max(1, int(hh - 60)))
        K.blit(f, K.icon('sparkle', 30, K.GOLD_L), x, y - q * 30, b.a * math.sin(math.pi * q) * 0.9, 0.6 + 0.6 * q)


def sc_end(f, t):
    P = PLAN
    t0 = P['end_in']
    if t < t0: return
    e = K.ease_io(K.lin(t, t0, t0 + 0.7))
    # blur + green wash behind
    small = cv2.resize(f, (W // 8, H // 8), interpolation=cv2.INTER_AREA)
    small = cv2.GaussianBlur(small, (0, 0), 6)
    bl = cv2.resize(small, (W, H), interpolation=cv2.INTER_LINEAR)
    bl = bl * 0.45 + np.array(K.GREEN_D, np.float32) * 0.35
    f[:] = f * (1 - e) + bl * e
    b = Box(f, t, 540, 905, 960, 780, t0 + 0.15, 1e9, r=70, style='dark', d_in=0.5)
    if not b.ok: return
    p = K.ease_out_cubic(K.lin(t, t0 + 0.7, t0 + 1.1))
    b.put(T('Benazir ka Benazir Khwab!', 60, 'black', grad=K.GOLD_GRAD, shadow=0.0), 0, 70, alpha=p)
    p2 = K.ease_out_cubic(K.lin(t, t0 + 0.95, t0 + 1.35))
    b.put(T('Har Aurat Khud Mukhtar, Ba Ikhtiyar!', 40, 'bold'), 0, 146, alpha=p2)
    p3 = K.ease_out_back(K.lin(t, t0 + 1.25, t0 + 1.7), 2.0)
    if p3 > 0:
        x, y = b.pos(0, 272)
        K.glass(f, x, y, 820 * b.s * p3, 120 * b.s, 60, alpha=b.a * min(1, p3), **STY['green'])
        b.put(T('INTEROPERABILITY', 30, 'ui_x', color=K.GOLD_L, tracking=4, shadow=0.0), 0, 248, alpha=min(1, p3))
        b.put(T('Raqam Aapki, Intikhab Bhi Aapka!', 38, 'xbold'), 0, 292, alpha=min(1, p3))


# ---- captions ----------------------------------------------------------------------------------------------------------
NOBREAK = {('asif', 'ali'), ('ali', 'zardari'), ('habib', 'bank'), ('bank', 'limited')}
BREAK_BEFORE = {'asif'}


def build_pages():
    pages, cur = [], []
    segs = TL.segs

    def seg_id(tt):
        return TL.seg_at(tt)['id']
    for w in WORDS:
        if any(a <= w['ot'] < b for a, b in CAP_OFF):
            if cur: pages.append(cur); cur = []
            continue
        if cur:
            gap = w['ot'] - cur[-1]['ot']
            chars = sum(len(x['word']) + 1 for x in cur) + len(w['word'])
            brk = cur[-1]['word'][-1] in ',.:!?' or w['sent'] != cur[-1]['sent']
            pair = (_norm(cur[-1]['word']), _norm(w['word']))
            if pair in NOBREAK and w['sent'] == cur[-1]['sent'] and len(cur) < 4:
                cur.append(w); continue
            if _norm(w['word']) in BREAK_BEFORE and cur:
                pages.append(cur); cur = []
            elif len(cur) >= 3 or chars > 21 or gap > 0.7 or brk or TL.seg_at(w['ot'])['clip'] != TL.seg_at(cur[-1]['ot'])['clip']:
                pages.append(cur); cur = []
        cur.append(w)
    if cur: pages.append(cur)
    out = []
    for i, pg in enumerate(pages):
        start = pg[0]['ot'] - 0.06
        end = pg[-1]['ot'] + 0.75
        if i + 1 < len(pages):
            end = min(end, pages[i + 1][0]['ot'] - 0.07)
        # never across a caption-off window
        for a, b in CAP_OFF:
            if start < a < end: end = a
        out.append(dict(words=pg, t0=start, t1=end))
    # a page shorter than 0.25 s would only flash: fold it into the previous page of the same sentence
    merged = []
    for p in out:
        if merged and p['t1'] - p['t0'] < 0.25 and p['words'][0]['sent'] == merged[-1]['words'][-1]['sent'] \
                and p['t0'] - merged[-1]['t1'] < 0.2:
            merged[-1]['words'] = merged[-1]['words'] + p['words']
            merged[-1]['t1'] = p['t1']
        else:
            merged.append(p)
    return merged


PAGES = build_pages()
CAP_SIZE = 66
GAP = 20


def sc_captions(f, t):
    pg = next((p for p in PAGES if p['t0'] <= t < p['t1'] + 0.06), None)
    if pg is None: return
    fade = 1 - K.lin(t, pg['t1'], pg['t1'] + 0.06)
    words = pg['words']
    Ls = []
    for i, w in enumerate(words):
        col = K.GOLD if w['key'] else (1, 1, 1)
        Ls.append(K.text_layer(w['word'], 'xbold', CAP_SIZE, color=col, stroke=3, stroke_color=(0.02, 0.08, 0.04, 0.7 if w['key'] else 0.55),
                               shadow=0.6, shadow_blur=7, shadow_dy=4))
    pad = Ls[0].shape[1] - K.text_size(words[0]['word'], 'xbold', CAP_SIZE)[0]
    widths = [L.shape[1] - pad for L in Ls]
    total = sum(widths) + GAP * (len(Ls) - 1)
    scale = min(1.0, 860 / total)
    x = CXL - total * scale / 2
    # active word = last word whose time has come (until the next one)
    act = max([i for i, w in enumerate(words) if t >= w['ot'] - 0.03] or [-1])
    for i, (w, L) in enumerate(zip(words, Ls)):
        cx = x + widths[i] * scale / 2
        x += (widths[i] + GAP) * scale
        tp = pg['t0'] + i * 0.035
        p = K.ease_out_back(K.lin(t, tp, tp + 0.16), 2.4)
        if p <= 0: continue
        dim = 1.0 if t >= w['ot'] - 0.05 else 0.78
        if i == act:
            bp = K.ease_out_back(K.lin(t, w['ot'] - 0.04, w['ot'] + 0.1), 2.0)
            K.fill_rrect(f, cx, CAP_Y + 3, (widths[i] + 26) * scale * (0.85 + 0.15 * bp), 90 * scale, 22, None,
                         alpha=fade * min(1, bp * 1.5), grad=(K.GREEN_L, K.GREEN))
        K.blit(f, L, cx, CAP_Y, fade * min(1, p * 1.6) * dim, scale * (0.8 + 0.2 * p))


# ---- frame ---------------------------------------------------------------------------------------------------------------
SCENES = [sc_hook, sc_wallets, sc_anytime, sc_vision, sc_whatis, sc_pehle, sc_ab, sc_rush, sc_banks, sc_faide, sc_steps,
          sc_hidayat, sc_crore, sc_khwab]


def render_frame(t):
    f = base_frame(t)
    f = np.ascontiguousarray(f, np.float32)
    f *= K.vignette_map(W, H)
    for sc in SCENES:
        sc(f, t)
    sc_end(f, t)
    sc_captions(f, t)
    sc_logo(f, t)
    K.grain(f, t, 0.018)
    # fade from black at the head, to black at the very end
    f *= min(1.0, 0.25 + 0.75 * K.ease_out_cubic(K.lin(t, 0, 0.25)), 1 - K.lin(t, TL.dur - 0.35, TL.dur))
    return (np.clip(f, 0, 1) * 255 + 0.5).astype(np.uint8)


# ---- SFX cue sheet (synced to the same plan) -------------------------------------------------------------------------
def sfx_cues():
    P = PLAN
    c = []
    def add(t, name, g=0.0, **kw):
        c.append(dict(t=float(t), name=name, gain_db=g, **kw))
    add(0.02, 'impact_soft', -4)
    add(P['logo_in'] + 0.2, 'shimmer', -8)
    add(P['hook_title1'] + 0.15, 'pop', -6); add(P['hook_title1'] + 0.37, 'pop', -6)
    add(P['hook_interop'], 'impact_big', -5); add(P['hook_interop'] - 0.02, 'whoosh_fast', -8)
    add(P['hook_interop'] + 0.35, 'shimmer', -10)
    add(P['hook_raqam'] + 0.5, 'cash_kaching', -15); add(P['hook_intikhab'], 'check_ding', -8)
    for s in TL.segs[1:]:
        typ = TRANS.get(s['id'], 'cut')
        if typ == 'glass': add(s['t0'], 'whoosh_slow', -9)
        elif typ == 'whip': add(s['t0'], 'whip', -7)
        elif typ == 'flash': add(s['t0'], 'flash_hit', -9)
        elif typ == 'punch': add(s['t0'], 'swish_small', -12)
    add(P['logo_pulse'] + 0.2, 'glass_tap', -10)
    add(P['crore_in'], 'card_slide', -9); add(P['crore_in'] + 0.2, 'slot_tick', -12, align='start'); add(P['crore_in'] + 1.45, 'coin_ring', -10)
    for k in ('any_pak', 'any_waqt', 'any_din', 'any_sahulat'): add(P[k], 'bubble_pop', -9)
    add(P['plate1'], 'card_slide', -10); add(P['plate2'], 'card_slide', -10)
    add(P['maali_in'], 'toast_chime', -10)
    add(P['whatis_in'], 'impact_big', -6)
    add(P['pehle_tag'], 'glitch_short', -12)
    for k in ('pain1', 'pain2', 'pain3', 'pain4'): add(P[k], 'ui_tick', -8)
    add(P['ab_tag'], 'toggle_on', -8)
    add(P['net_in'], 'card_slide', -10)
    for k in range(6): add(P['net_lines'] + k * 0.12 + 0.2, 'pop', -13)
    add(P['net_free'], 'shimmer', -11); add(P['net_auth'], 'check_ding', -10)
    add(P['rush_a'], 'card_slide', -10); add(P['rush_b'] - 0.05, 'whoosh_by', -16); add(P['rush_b'] + 0.1, 'card_slide', -10)
    add(P['rush_pick'], 'check_ding', -8)
    add(P['banks_head'], 'impact_soft', -9)
    for tk in P['bank_t']: add(tk, 'glass_tap', -8)
    add(P['faide_head'], 'impact_soft', -9)
    for tk in P['faida_t']: add(tk, 'check_ding', -14)
    add(P['steps_title'], 'card_slide', -9)
    for k, tk in enumerate(P['step_t']):
        add(tk - 0.12, 'card_slide', -11)
        if k in (0, 3): add(tk + 0.35, 'toast_chime', -9)
        if k == 2: add(tk + 0.2, 'ui_click', -8)
    add(P['hid_in'], 'glitch_short', -12); add(P['hid_wallet'], 'toggle_on', -9)
    add(P['cr_in'], 'card_slide', -10); add(P['cr_chip1'], 'bubble_pop', -10); add(P['cr_chip2'], 'bubble_pop', -10)
    add(P['cr_globe'], 'shimmer', -10); add(P['cr_world'], 'bubble_pop', -10)
    add(P['kh_chip1'], 'bubble_pop', -10); add(P['kh_chip2'], 'bubble_pop', -10)
    add(P['kh_title'], 'impact_soft', -8); add(P['kh_title2'], 'shimmer', -6); add(P['kh_line2'], 'sparkle', -9)
    add(P['end_in'] + 0.1, 'whoosh_slow', -9); add(P['end_in'] + 0.75, 'logo_sting', -6)
    return c


# ---- CLI ----------------------------------------------------------------------------------------------------------------
if __name__ == '__main__':
    od = os.path.join(WS, 'stills')
    os.makedirs(od, exist_ok=True)
    if sys.argv[1] == 'still':
        for s in sys.argv[2].split(','):
            t = float(s)
            img = render_frame(t)
            p = os.path.join(od, f'still_{t:07.2f}.jpg')
            cv2.imwrite(p, img[..., ::-1], [cv2.IMWRITE_JPEG_QUALITY, 90])
            print(p)
    elif sys.argv[1] == 'sheet':
        n = int(sys.argv[2])
        ts = sys.argv[3].split(',') if len(sys.argv) > 3 else None
        ts = [float(x) for x in ts] if ts else [TL.dur * (i + 0.5) / n for i in range(n)]
        tiles = []
        for t in ts:
            img = cv2.resize(render_frame(t), (270, 480), interpolation=cv2.INTER_AREA)
            cv2.putText(img, f'{t:.2f}', (6, 22), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)
            tiles.append(img)
        cols = 6
        while len(tiles) % cols: tiles.append(np.zeros_like(tiles[0]))
        rows = [np.concatenate(tiles[i:i + cols], 1) for i in range(0, len(tiles), cols)]
        sheet = np.concatenate(rows, 0)
        p = os.path.join(od, sys.argv[4] if len(sys.argv) > 4 else 'sheet.jpg')
        cv2.imwrite(p, sheet[..., ::-1], [cv2.IMWRITE_JPEG_QUALITY, 85])
        print(p)
    elif sys.argv[1] == 'plan':
        for k, v in PLAN.items():
            print(k, v)
        for p in PAGES[:400]:
            print('%.2f-%.2f' % (p['t0'], p['t1']), ' '.join(w['word'] for w in p['words']))
