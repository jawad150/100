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
CAP_Y = 1455      # caption line centre (inside the Reels safe area, below the protected zone in every shot)
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
    P['plate2'] = Wt('vision_a2', 'wazir-e-azam') - 0.15
    P['plates_out'] = Wt('vision_b', 'maali') - 0.55
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
    (S('hidayat')['t0'], S('hidayat')['t1']),
    (PLAN['kh_title'] - 0.05, 1e9),
]

# transitions at clip changes: segment id -> type of the cut INTO it
TRANS = {'wallets': 'glass', 'anytime': 'whip', 'vision_a': 'glass', 'vision_a2': 'ramp', 'vision_b': 'ramp', 'whatis': 'flash',
         'pehle': 'glass', 'ab': 'flash', 'rush': 'punch', 'banks': 'glass', 'faide': 'whip', 'steps_a': 'glass',
         'steps_b': 'punch', 'hidayat': 'whip', 'crore': 'glass', 'khwab': 'punch'}
GLASS_HALF = 0.24
WHIP_HALF = 0.15
MORPH_HALF = 0.10
RAMP_HALF = 0.15


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
    return TL.zoom_at(s, t)


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
        if typ == 'morph' and abs(t - T) < MORPH_HALF:
            return morph(a, b, t, T)
        if typ == 'ramp' and abs(t - T) < RAMP_HALF:
            return ramp(a, b, t, T)
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


_dis = None


def morph(a, b, t, T):
    """Morph cut (like Premiere's): dense optical flow from the outgoing to the incoming frame; both are warped
    towards the in-between position and cross-blended, so a jump cut inside one take reads as continuous motion."""
    global _dis
    q = K.ease_io((t - (T - MORPH_HALF)) / (2 * MORPH_HALF))
    A = seg_image(a, t)
    B = seg_image(b, t)
    if _dis is None:
        _dis = cv2.DISOpticalFlow_create(cv2.DISOPTICAL_FLOW_PRESET_MEDIUM)
    ga = cv2.cvtColor((cv2.resize(A, (W // 2, H // 2)) * 255).astype(np.uint8), cv2.COLOR_RGB2GRAY)
    gb = cv2.cvtColor((cv2.resize(B, (W // 2, H // 2)) * 255).astype(np.uint8), cv2.COLOR_RGB2GRAY)
    fl = _dis.calc(ga, gb, None)
    fl = cv2.GaussianBlur(fl, (0, 0), 6)
    fl = cv2.resize(fl, (W, H), interpolation=cv2.INTER_LINEAR) * 2.0
    gx, gy = np.meshgrid(np.arange(W, dtype=np.float32), np.arange(H, dtype=np.float32))
    Aw = cv2.remap(A, gx - q * fl[..., 0], gy - q * fl[..., 1], cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
    Bw = cv2.remap(B, gx + (1 - q) * fl[..., 0], gy + (1 - q) * fl[..., 1], cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
    return Aw * (1 - q) + Bw * q


def ramp_src(a, b, t, T):
    """Source time through a speed ramp: normal speed at both edges of the window, a smooth (Hermite) acceleration
    through the skipped moment in between, so the take's own camera move simply runs on, fast."""
    h = RAMP_HALF
    u = min(max((t - (T - h)) / (2 * h), 0.0), 1.0)
    s0 = a['b'] - h * edl.SPEED
    s1 = b['a'] + h * edl.SPEED
    m = 2 * h * edl.SPEED
    h00, h10, h01, h11 = 2 * u**3 - 3 * u**2 + 1, u**3 - 2 * u**2 + u, -2 * u**3 + 3 * u**2, u**3 - u**2
    return h00 * s0 + h10 * m + h01 * s1 + h11 * m


def ramp(a, b, t, T):
    """Speed-ramp cut inside one take (used where she walks and the camera moves, so a morph cannot work): the skipped
    seconds of video fly past in ~0.3 s with real motion blur; the audio cut stays clean."""
    n = 10
    acc = np.zeros((H, W, 3), np.float32)
    s_lo = ramp_src(a, b, t - 0.5 / FPS, T)
    s_hi = ramp_src(a, b, t + 0.5 / FPS, T)
    for k in range(n):
        src = s_lo + (s_hi - s_lo) * (k + 0.5) / n
        img = src_frame(a['clip'], src)
        acc += zoom_frame(img, seg_zoom(a, t), a['clip'])
    return look_adjust(acc / n, a, t)


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

# ---- layout: Instagram safe area + a protected zone around the presenter ---------------------------------------------
# Safe area (1080x1920 Reels): clear of the top bar (y < 222), the caption/username/audio strip (y > 1538) and the
# like/comment/share column (x > 960). The protected ZONE (facetrack.py) covers her hair, face and neck for the whole
# segment, zoom included. Graphics live only in the band above the zone (under the logo pill) or the band below it
# (above the captions), and sit at the far edge of that band, away from her.
SAFE = dict(top=222, bot=1538, l=60, r=960)
LOGO_Y = 278
TOP0 = 346
CAP_TOP = 1410
FSEG = json.load(open(os.path.join(WS, 'faces_seg.json')))
RECTS = []          # panels drawn in the current frame (for the layout audit)


def band(seg, where, caps=True, m=12):
    z = FSEG[seg]['zone']
    if where == 'top':
        return TOP0, z[1] - m
    return z[3] + m, (CAP_TOP - 10) if caps else SAFE['bot'] - 20     # 20 px for the slide-in


def stack(seg, where, heights, gap=10, caps=True, align=None):
    """Lay blocks of design heights out in a band. -> (centre ys, scale). Top band: from the logo down;
    lower band: from the captions up (as far from her as possible)."""
    a, b = band(seg, where, caps)
    tot = sum(heights) + gap * (len(heights) - 1)
    k = max(0.3, min(1.0, (b - a) / tot))
    align = align or ('start' if where == 'top' else 'end')
    y = a if align == 'start' else b - tot * k
    out = []
    for h in heights:
        out.append(y + h * k / 2)
        y += (h + gap) * k
    return out, k


def anim(t, t_in, t_out, d_in=0.34, d_out=0.22):
    """-> (alpha, scale, in_progress, slide) for a pop-in / pop-out element; alpha 0 = hidden."""
    if t < t_in or t > t_out + d_out:
        return 0.0, 0.0, 0.0, 0.0
    pin = K.lin(t, t_in, t_in + d_in)
    pout = K.lin(t, t_out, t_out + d_out)
    a = min(K.ease_out_cubic(min(1, pin * 1.7)), 1 - K.ease_in_cubic(pout))
    s = (0.9 + 0.1 * K.ease_out_back(pin, 1.2)) * (1 - 0.06 * K.ease_in_cubic(pout))
    sl = (1 - K.ease_out_cubic(pin)) * 16 + K.ease_in_cubic(pout) * 10
    return a, min(s, 1.0), pin, sl


class Box:
    """A glass panel whose children are placed in its local coordinates (scaled/faded with it). k = layout scale;
    side = +1 slides in from below (lower band), -1 from above (upper band): never towards her."""

    def __init__(self, f, t, cx, cy, w, h, t_in, t_out, r=44, style='dark', d_in=0.34, d_out=0.22, k=1.0, side=None,
                 tag='panel', **gk):
        self.f = f
        self.a, s, self.p, sl = anim(t, t_in, t_out, d_in, d_out)
        self.s = s * k
        side = side if side is not None else (1 if cy > 900 else -1)
        self.cx, self.cy = cx, cy + side * sl
        self.ok = self.a > 0.003
        if self.ok:
            g = dict(STY[style]); g.update(gk)
            K.glass(f, self.cx, self.cy, w * self.s, h * self.s, r * self.s, alpha=self.a, **g)
            RECTS.append((tag, self.cx - w * self.s / 2, self.cy - h * self.s / 2, self.cx + w * self.s / 2,
                          self.cy + h * self.s / 2))

    def pos(self, dx, dy):
        return self.cx + dx * self.s, self.cy + dy * self.s

    def put(self, L, dx, dy, alpha=1.0, scale=1.0, anchor='c'):
        if not self.ok or alpha <= 0: return
        x, y = self.pos(dx, dy)
        K.blit(self.f, L, x, y, self.a * alpha, self.s * scale, anchor)


def T(s, size=40, w='xbold', color=(1, 1, 1), shadow=0.35, grad=None, tracking=0):
    return K.text_layer(s, w, int(size), color=tuple(color), shadow=shadow, shadow_blur=6, shadow_dy=3,
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
    return L.shape[1] - 12 + int(h * 0.74) + 50


def chip(f, t, cx, cy, text, icon, t_in, t_out, style='dark', badge=K.GREEN, size=26, h=56, w=None, icon_fg=K.WHITE,
         text_color=(1, 1, 1), k=1.0, side=None, tag='chip'):
    L = T(text, size, 'bold', color=text_color)
    bw = int(h * 0.74)
    w = w or chip_width(text, size, h)
    b = Box(f, t, cx, cy, w, h, t_in, t_out, r=h / 2, style=style, k=k, side=side, tag=tag)
    if not b.ok: return b
    p = K.ease_out_back(K.lin(t, t_in + 0.08, t_in + 0.4), 1.3)
    b.put(K.icon_badge(icon, bw, bg=badge, fg=icon_fg), -w / 2 + h / 2, 0, scale=max(0.01, p))
    b.put(L, -w / 2 + h / 2 + bw / 2 + 14, 0, anchor='l')
    return b


def chip_rows(f, t, seg, where, rows, t_out, h=56, gap=10, size=26, style='dark', badge=K.GREEN, caps=True, cx0=None):
    """Rows of chips (each row a list of (text, icon, t_in[, style])) fitted into a band, each row centred."""
    ys, k = stack(seg, where, [h] * len(rows), gap, caps)
    cx0 = cx0 or (CX if where == 'top' else CXL)
    n = 0
    for row, cy in zip(rows, ys):
        ws = [chip_width(it[0], size, h) for it in row]
        tot = (sum(ws) + 14 * (len(row) - 1)) * k
        x = cx0 - tot / 2
        for it, wch in zip(row, ws):
            sty = it[3] if len(it) > 3 else style
            chip(f, t, x + wch * k / 2, cy, it[0], it[1], it[2], t_out + n * 0.04, style=sty, badge=badge, size=size,
                 h=h, w=wch, k=k, side=(-1 if where == 'top' else 1))
            x += (wch + 14) * k
            n += 1


def tag_pill(f, t, text, icon, t_in, t_out, style):
    """Small section tag left of the logo pill (PEHLE / AB)."""
    b = Box(f, t, 160, LOGO_Y, 172, 60, t_in, t_out, r=30, style=style, side=-1, tag='tag')
    if b.ok:
        b.put(K.icon(icon, 26, (1, 1, 1)), -48, 0)
        b.put(T(text, 28, 'black', tracking=3), 16, 0)


# ---- scenes ------------------------------------------------------------------------------------------------------------
def sc_logo(f, t):
    """Official BISP banner in a glass pill, top centre inside the safe area; it flies into the end card."""
    P = PLAN
    if t < P['logo_in']: return
    a = K.ease_out_cubic(K.lin(t, P['logo_in'], P['logo_in'] + 0.4))
    pop = 0.88 + 0.12 * K.ease_out_cubic(K.lin(t, P['logo_in'], P['logo_in'] + 0.5))
    pulse = 1 + 0.06 * math.exp(-((t - P['logo_pulse'] - 0.25) / 0.22) ** 2)
    e = K.ease_io(K.lin(t, P['end_in'], P['end_in'] + 0.75))
    cx, cy = 540, LOGO_Y
    wl = 228 * pulse * pop
    cy = cy * (1 - e) + 700 * e
    wl = wl * (1 - e) + 740 * e
    hl = wl * 563 / 1600
    K.glass(f, cx, cy, wl + 28, hl + 26, 26 + 12 * e, alpha=a, **STY['light'])
    K.blit(f, K.logo_layer(880), cx, cy, a, wl / 880)
    RECTS.append(('logo', cx - (wl + 28) / 2, cy - (hl + 26) / 2, cx + (wl + 28) / 2, cy + (hl + 26) / 2))


def sc_hook(f, t):
    P = PLAN
    t_out = P['hook_out']
    # title card (before "Interoperability"): BENAZIR KAFAALAT / ka naya Digital Payment System
    (cy1,), k1 = stack('hook', 'low', [160], caps=False)
    b = Box(f, t, CXL, cy1, 720, 160, P['hook_title1'], P['hook_interop'] - 0.18, r=40, style='deep', k=k1)
    if b.ok:
        wa = T('BENAZIR', 48, 'black', grad=K.GOLD_GRAD, shadow=0.0).shape[1] - 12
        wb = T('KAFAALAT', 48, 'black', grad=K.GOLD_GRAD, shadow=0.0).shape[1] - 12
        tot = wa + wb + 36
        for i, (wd, dx) in enumerate((('BENAZIR', -tot / 2 + wa / 2), ('KAFAALAT', tot / 2 - wb / 2))):
            p = K.ease_out_back(K.lin(t, P['hook_title1'] + 0.12 + i * 0.22, P['hook_title1'] + 0.5 + i * 0.22), 1.2)
            if p > 0:
                b.put(T(wd, 48, 'black', grad=K.GOLD_GRAD, shadow=0.0), dx, -36, alpha=min(1, p * 1.5), scale=max(0.01, p))
        p2 = K.ease_out_cubic(K.lin(t, P['hook_title2'], P['hook_title2'] + 0.4))
        if p2 > 0:
            b.put(T('ka Naya Digital Payment System', 34, 'xbold'), 0, 34 + (1 - p2) * 14, alpha=p2)
    # INTEROPERABILITY slab + the two promise pills, one row
    ti = P['hook_interop']
    (cy2, cy3), k2 = stack('hook', 'low', [104, 60], gap=12, caps=False)
    b2 = Box(f, t, CXL, cy2, 720, 104, ti, t_out, r=36, style='deep', d_in=0.28, k=k2)
    if b2.ok:
        slam = 1 + 0.15 * (1 - K.ease_out_expo(K.lin(t, ti, ti + 0.3)))
        b2.put(T('INTEROPERABILITY', 54, 'black', grad=K.GOLD_GRAD, shadow=0.0), 0, -2, scale=slam)
        sw = K.lin(t, ti + 0.3, ti + 1.1)
        if 0 < sw < 1:
            x0, y0 = b2.pos(-360 + 720 * sw, 0)
            K.blit(f, sweep_layer(), x0, y0, 0.5 * math.sin(math.pi * sw) * b2.a, 0.7 * k2)
    items = (('Raqam Aapki,', 'cash', P['hook_raqam'], 'green', K.GREEN_D),
             ('Intikhab Bhi Aapka!', 'check', P['hook_intikhab'], 'gold', K.GOLD_D))
    ws = [chip_width(it[0], 28, 60) for it in items]
    x = CXL - (sum(ws) + 14) * k2 / 2
    for (txt, ic, tt, sty, bg), wch in zip(items, ws):
        chip(f, t, x + wch * k2 / 2, cy3, txt, ic, tt - 0.05, t_out, style=sty, badge=bg, size=28, h=60, w=wch, k=k2, side=1)
        x += (wch + 14) * k2


@lru_cache(1)
def sweep_layer():
    w, h = 150, 130
    xx = np.linspace(-1, 1, w, dtype=np.float32)[None, :]
    yy = np.linspace(-1, 1, h, dtype=np.float32)[:, None]
    a = np.exp(-(xx * 2.2) ** 2) * (1 - yy ** 2) * 0.9
    a = cv2.warpAffine(a, np.float32([[1, -0.35, 24], [0, 1, 0]]), (w, h))
    L = np.zeros((h, w, 4), np.float32)
    L[..., 3] = a
    L[..., :3] = a[..., None]
    return L


def counter_text(q):
    n = int(round(q * 10000000))
    s = str(n)
    if len(s) > 3:   # Pakistani grouping: 1,00,00,000
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
    (cy,), k = stack('wallets', 'top', [140])
    b = Box(f, t, CX, cy, 660, 140, t_in, t_out, r=38, style='dark', k=k)
    if not b.ok: return
    b.put(K.icon_badge('wallet', 88, bg=K.GREEN), -258, 0, scale=max(0.01, K.ease_out_back(K.lin(t, t_in + 0.1, t_in + 0.5), 1.3)))
    q = K.ease_out_expo(K.lin(t, t_in + 0.15, t_in + 1.5))
    b.put(T(counter_text(q), 48, 'black', grad=K.GOLD_GRAD, shadow=0.0), -196, -26, anchor='l')
    p = K.ease_out_cubic(K.lin(t, t_in + 0.6, t_in + 1.0))
    b.put(T('Mustahiq khawateen ke Digital Wallets', 25, 'bold', color=K.GOLD_L), -196, 30, alpha=p, anchor='l')


def sc_anytime(f, t):
    P = PLAN
    chip_rows(f, t, 'anytime', 'top', [[('Poore Pakistan mein', 'pin', P['any_pak']), ('Kisi bhi waqt', 'clock', P['any_waqt'])],
                                       [('Kisi bhi din', 'calendar', P['any_din']),
                                        ('Apni sahulat ke mutabiq', 'heart', P['any_sahulat'])]], P['any_out'])


def sc_vision(f, t):
    P = PLAN
    # Wazir-e-Azam name plate (the President's name is cut from this line), below her neck, left-aligned, in a band
    # that is safe for both segments it spans
    a1, b1 = band('vision_a2', 'low'); a2, b2 = band('vision_b', 'low')
    lo, hi = max(a1, a2), min(b1, b2)
    hh = 76
    k = min(1.0, (hi - lo) / hh)
    role, name, tt = 'WAZIR-E-AZAM', 'Muhammad Shehbaz Sharif', P['plate2']
    Ln = T(name, 30, 'xbold')
    pw = Ln.shape[1] + 112
    b = Box(f, t, SAFE['l'] + 6 + pw * k / 2, hi - hh * k / 2, pw, hh, tt, P['plates_out'], r=24,
            style='dark', side=1, tag='plate', k=k)
    if b.ok:
        b.put(K.emblem_disc(56), -pw / 2 + 42, 0)
        b.put(T(role, 17, 'ui_b', color=K.GOLD, tracking=3, shadow=0.0), -pw / 2 + 80, -17, anchor='l')
        b.put(Ln, -pw / 2 + 80, 11, anchor='l')
    # "Maali Khudmukhtari" (after the plates have gone), same lower band
    (cy,), k = stack('vision_b', 'low', [104])
    b = Box(f, t, CXL, cy, 620, 104, P['maali_in'], P['maali_out'], r=32, style='dark', k=k)
    if b.ok:
        b.put(K.icon_badge('rise', 68, bg=K.GOLD_D), -248, 0)
        b.put(T('Maali Khudmukhtari', 38, 'black', grad=K.GOLD_GRAD, shadow=0.0), -198, -14, anchor='l')
        b.put(T('ki taraf ek aham qadam', 24, 'semi', color=(0.92, 0.96, 0.93)), -198, 26, anchor='l')


def sc_whatis(f, t):
    P = PLAN
    t_in, t_out = P['whatis_in'], P['whatis_out']
    (cy,), k = stack('whatis', 'low', [150], caps=False)
    b = Box(f, t, CXL, cy, 680, 150, t_in, t_out, r=40, style='deep', d_in=0.26, k=k)
    if not b.ok: return
    slam = 1 + 0.15 * (1 - K.ease_out_expo(K.lin(t, t_in, t_in + 0.32)))
    b.put(T('INTEROPERABILITY', 52, 'black', grad=K.GOLD_GRAD, shadow=0.0), 0, -28, scale=slam)
    p = K.ease_out_back(K.lin(t, t_in + 0.35, t_in + 0.75), 1.3)
    if p > 0:
        b.put(T('kya hai?', 42, 'black'), -28, 38, scale=max(0.01, p))
        b.put(K.icon_badge('question', 54, bg=K.GOLD_D), 106, 38, scale=max(0.01, p))


def sc_pehle(f, t):
    P = PLAN
    tag_pill(f, t, 'PEHLE', 'cross', P['pehle_tag'], P['pehle_out'], 'red')
    rows = [[('Ek khaas bank ka retailer', 'store', P['pain1']), ('Lambi qataarein', 'users', P['pain2'])],
            [('Intezar', 'clock', P['pain3']), ('Najaiz katautiyan', 'cash', P['pain4'])]]
    chip_rows(f, t, 'pehle', 'top', rows, P['pehle_out'], style='red', badge=(0.62, 0.1, 0.12))


BANK_KEYS = ['hbl', 'hblmfb', 'easypaisa', 'jazzcash', 'bop', 'alfalah']
BANKS = ['Habib Bank Limited', 'HBL Microfinance Bank', 'Easypaisa', 'JazzCash', 'Bank of Punjab', 'Bank Alfalah']


def sc_ab(f, t):
    P = PLAN
    tag_pill(f, t, 'AB', 'check', P['ab_tag'], P['ab_out'], 'green')
    # hub: one woman -> any partner's authorized retailer (the six official logos), below her neck
    h = 176
    (cy,), k = stack('ab', 'low', [h])
    bx = Box(f, t, CXL, cy, 820, h, P['net_in'], P['ab_out'], r=40, style='dark', k=k)
    if not bx.ok: return
    hub = (-330, 18)
    lw, lh = 150, 50
    for i in range(6):
        col, row = i % 3, i // 3
        dx, dy = -150 + col * 172, -16 + row * 62
        tk = P['net_lines'] + i * 0.12
        q = K.ease_out_cubic(K.lin(t, tk, tk + 0.35))
        if q <= 0: continue
        x0, y0 = bx.pos(hub[0] + 40, hub[1])
        tx, ty = dx - lw / 2, dy
        x1, y1 = bx.pos(hub[0] + 40 + (tx - hub[0] - 40) * q, hub[1] + (ty - hub[1]) * q)
        lit = K.lin(t, P['net_free'], P['net_free'] + 0.3)
        col_ = np.array(K.GOLD) * lit + np.array((0.85, 0.95, 0.9)) * (1 - lit)
        line(f, x0, y0, x1, y1, col_, 2.5 * bx.s, bx.a * 0.85)
        p = K.ease_out_back(K.lin(t, tk + 0.15, tk + 0.5), 1.3)
        if p > 0:
            bx.put(K.logo_plate(BANK_KEYS[i], lw, lh), dx, dy, scale=max(0.01, p))
            ka = K.ease_out_back(K.lin(t, P['net_auth'] + i * 0.08, P['net_auth'] + 0.35 + i * 0.08), 1.5)
            if ka > 0:
                bx.put(K.icon_badge('check', 24, bg=K.GOLD_D), dx + lw / 2 - 4, dy - lh / 2 + 4, scale=max(0.01, ka))
    bx.put(K.icon_badge('woman', 76, bg=K.GOLD_D), *hub)
    p = K.ease_out_cubic(K.lin(t, P['net_free'], P['net_free'] + 0.35))
    p2 = K.ease_out_cubic(K.lin(t, P['net_auth'], P['net_auth'] + 0.35))
    if p > 0:
        txt = 'Kisi ek bank ki paband nahi' if p2 < 0.5 else 'Kisi bhi Authorized Retailer se'
        a = p * (1 - 2 * min(p2, 0.5)) if p2 < 0.5 else (p2 - 0.5) * 2
        bx.put(T(txt, 24, 'bold', color=K.GOLD_L), 22, -68, alpha=a)


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
    h = 190
    (cy,), k = stack('rush', 'top', [h])
    b = Box(f, t, 320, cy, 340, h, P['rush_a'], P['rush_out'], r=36, style='red', k=k)
    if b.ok:
        fade = 1 - 0.45 * K.lin(t, P['rush_b'], P['rush_b'] + 0.4)
        b.put(K.icon_badge('store', 64, bg=(0.5, 0.1, 0.12)), -112, -42, alpha=fade)
        b.put(T('Retailer 1', 30, 'xbold'), -66, -42, alpha=fade, anchor='l')
        p = K.ease_out_back(K.lin(t, P['rush_a'] + 0.15, P['rush_a'] + 0.5), 1.3)
        b.put(K.icon('users', 30, (1, 0.8, 0.8)), -112, 18, alpha=p * fade)
        b.put(T('Rush', 26, 'semi', color=(1, 0.8, 0.8)), -84, 18, alpha=p * fade, anchor='l')
        p2 = K.ease_out_back(K.lin(t, P['rush_taawun'], P['rush_taawun'] + 0.4), 1.3)
        b.put(K.icon('cross', 26, (1, 0.8, 0.8)), -112, 58, alpha=p2 * fade)
        b.put(T('Taawun nahi', 26, 'semi', color=(1, 0.8, 0.8)), -84, 58, alpha=p2 * fade, anchor='l')
        x = K.ease_out_back(K.lin(t, P['rush_b'] - 0.1, P['rush_b'] + 0.3), 1.5)
        if x > 0:
            b.put(K.icon_badge('cross', 44, bg=K.RED), 146, -72, scale=max(0.01, x))
    q = K.ease_out_cubic(K.lin(t, P['rush_b'], P['rush_b'] + 0.35))
    a_out = 1 - K.lin(t, P['rush_out'], P['rush_out'] + 0.24)
    if q > 0 and a_out > 0:
        K.blit(f, K.icon_badge('arrow', 52, bg=K.GOLD_D), 540, cy, q * a_out, (0.6 + 0.4 * q) * k)
    b = Box(f, t, 760, cy, 340, h, P['rush_b'], P['rush_out'], r=36, style='green', k=k)
    if b.ok:
        b.put(K.icon_badge('store', 64, bg=K.GREEN_D), -112, -42)
        b.put(T('Doosra Retailer', 24, 'xbold'), -66, -42, anchor='l')
        p = K.ease_out_back(K.lin(t, P['rush_pick'] - 0.1, P['rush_pick'] + 0.3), 1.3)
        b.put(K.icon('check', 28, K.GOLD_L), -112, 36, alpha=p)
        b.put(T('Aapka intikhab', 28, 'bold', color=K.GOLD_L), -84, 36, alpha=p, anchor='l')
        if p > 0:
            b.put(K.icon_badge('check', 44, bg=K.GOLD_D), 146, -72, scale=max(0.01, p))


def sc_banks(f, t):
    """'6 Banking Partners' + a 3x2 grid of the partners' official logos, landing as she names them; all of it in the
    band below her neck (no room above her head in this close-up), stacked up from the bottom of the safe area."""
    P = PLAN
    tw, th, gx, gy = 236, 84, 18, 12
    (cyh, cyr1, cyr2), k = stack('banks', 'low', [60, th, th], gap=gy, caps=False)
    Lt = T('Banking Partners', 30, 'xbold')
    tw0 = Lt.shape[1] - 12
    hw = 40 + 34 + 12 + tw0 + 14 + 44 + 22
    b = Box(f, t, CXL, cyh, hw, 60, P['banks_head'], P['banks_out'], r=30, style='dark', side=1, k=k)
    if b.ok:
        p = K.ease_out_back(K.lin(t, P['banks_head'] + 0.05, P['banks_head'] + 0.45), 1.3)
        x0 = -hw / 2 + 22
        b.put(T('6', 46, 'black', grad=K.GOLD_GRAD, shadow=0.0), x0 + 16, 2, scale=max(0.01, p))
        b.put(Lt, x0 + 44, 0, anchor='l')
        b.put(K.icon_badge('bank', 44, bg=K.GREEN), x0 + 44 + tw0 + 14 + 22, 0)
    for i, key in enumerate(BANK_KEYS):
        tk = P['bank_t'][i]
        col, row = i % 3, i // 3
        cx = CXL + (col - 1) * (tw + gx) * k
        cy = (cyr1, cyr2)[row]
        bb = Box(f, t, cx, cy, tw, th, tk - 0.08, P['banks_out'] + i * 0.03, r=22, style='light', side=1, tag='bank',
                 shadow=0.22, k=k)
        if bb.ok:
            bb.put(K.logo_plate(key, tw - 14, th - 14, r=17), 0, 0)
            bb.put(K.disc(28, K.GOLD_D, ring=K.GOLD_L, ring_w=2), -tw / 2 + 10, -th / 2 + 10)
            bb.put(T(str(i + 1), 16, 'black', shadow=0.0), -tw / 2 + 10, -th / 2 + 11)


FAIDE = ['Retailers ki monopoly ka khatma', 'Apni marzi se retailer chunne ki azadi', 'Lambi qataron aur intezar mein kami',
         'Najaiz katautiyon ki hosla shikni', 'Digital wallets se mehfooz payments aur financial facilities tak rasai']


def sc_faide(f, t):
    P = PLAN
    # header pill above her hair
    (cy,), k = stack('faide', 'top', [56])
    hw = 400
    b = Box(f, t, CX, cy, hw, 56, P['faide_head'], P['faide_out'], r=28, style='dark', k=k)
    if b.ok:
        n = sum(1 for tt in P['faida_t'] if t >= tt)
        p = K.ease_out_back(K.lin(t, P['faide_head'] + 0.05, P['faide_head'] + 0.45), 1.3)
        b.put(T('5', 44, 'black', grad=K.GOLD_GRAD, shadow=0.0), -hw / 2 + 34, 2, scale=max(0.01, p))
        b.put(T('Naye System ke Faide', 26, 'xbold'), -hw / 2 + 60, 0, anchor='l')
        for i in range(5):
            b.put(K.disc(12, K.GOLD if i < n else (0.5, 0.55, 0.52)), hw / 2 - 86 + i * 16, 0)
    # the list, below her neck, growing upwards from the bottom of the safe area
    t_in = P['faida_t'][0] - 0.15
    rh = 44
    grow = sum(K.ease_out_cubic(K.lin(t, tk - 0.2, tk + 0.15)) for tk in P['faida_t'][1:])
    full = 26 + rh * 5
    (cyf,), k = stack('faide', 'low', [full], caps=False)
    bottom = cyf + full * k / 2
    hh = 26 + rh * (1 + grow)
    bx = Box(f, t, CXL, bottom - hh * k / 2, 820, hh, t_in, P['faide_out'], r=30, style='dark', side=1, k=k)
    if not bx.ok: return
    for i, txt in enumerate(FAIDE):
        tk = P['faida_t'][i]
        p = K.ease_out_back(K.lin(t, tk - 0.05, tk + 0.35), 1.3)
        if p <= 0: continue
        y = -hh / 2 + 13 + rh / 2 + i * rh
        bx.put(K.icon_badge('check', 32, bg=K.GREEN_L if i < 4 else K.GOLD_D), -380, y, scale=max(0.01, p))
        a = K.ease_out_cubic(K.lin(t, tk, tk + 0.3))
        bx.put(Tfit(txt, 740, 25, 'bold'), -354 + (1 - a) * 16, y, alpha=a, anchor='l')


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
    b = Box(f, t, CX, TOP0 + 32, 520, 64, t0, st[0] - 0.25, r=32, style='gold')
    if b.ok:
        b.put(T('Raqam kaise hasil karein?', 30, 'black'), 0, 0)
    h = 170
    a1, b1 = band('steps_a', 'top'); a2, b2 = band('steps_b', 'top')
    k = min(1.0, (min(b1, b2) - TOP0) / h)
    bx = Box(f, t, CX, TOP0 + h * k / 2, 720, h, st[0] - 0.12, t_out, r=40, style='dark', k=k)
    if not bx.ok: return
    for i in range(4):
        x = -150 + i * 100
        done = t >= st[i] - 0.1
        fill = K.ease_out_back(K.lin(t, st[i] - 0.1, st[i] + 0.25), 1.3)
        if i < 3:
            q = K.lin(t, st[i + 1] - 0.4, st[i + 1] - 0.1)
            x0, y0 = bx.pos(x + 18, -56)
            x1, y1 = bx.pos(x + 18 + 64 * q, -56)
            line(f, x0, y0, bx.pos(x + 82, -56)[0], y0, (0.6, 0.66, 0.62), 3 * bx.s, bx.a * 0.6)
            if q > 0:
                line(f, x0, y0, x1, y1, K.GOLD, 3.5 * bx.s, bx.a)
        bx.put(K.disc(34, (0.35, 0.42, 0.38)), x, -56)
        if done:
            bx.put(K.disc(34, K.GOLD_D, ring=K.GOLD_L, ring_w=2), x, -56, scale=max(0.01, fill))
        bx.put(T(str(i + 1), 18, 'black', shadow=0.0), x, -55)
    bx.put(T('STEP', 16, 'ui_b', color=K.GOLD, tracking=4, shadow=0.0), 260, -56)
    for i in range(4):
        tin = st[i] - 0.12
        tnext = st[i + 1] - 0.12 if i < 3 else 1e9
        if t < tin or t > tnext: continue
        pin = K.ease_out_cubic(K.lin(t, tin, tin + 0.35))
        pout = K.ease_in_cubic(K.lin(t, tnext - 0.2, tnext - 0.02))
        dx = (1 - pin) * 40 - pout * 40
        a = min(pin, 1 - pout)
        ic, l1, l2 = STEPS[i]
        pop = K.ease_out_back(K.lin(t, tin + 0.05, tin + 0.45), 1.3)
        bx.put(K.icon_badge(ic, 84, bg=K.GREEN), -282 + dx, 24, alpha=a, scale=max(0.01, pop))
        bx.put(Tfit(l1, 500, 30, 'xbold'), -222 + dx, 6, alpha=a, anchor='l')
        bx.put(Tfit(l2, 500, 23, 'semi', color=K.GOLD_L), -222 + dx, 44, alpha=a, anchor='l')
        if i in (0, 3):
            ping = K.lin(t, tin + 0.3, tin + 1.0)
            if 0 < ping < 1:
                bx.put(K.disc(20, K.RED, ring=(1, 1, 1), ring_w=2), -252 + dx, -6, alpha=a,
                       scale=1 + 0.2 * math.sin(ping * math.pi))
                bx.put(T('1', 13, 'black', shadow=0.0), -252 + dx, -5, alpha=a)


def sc_hidayat(f, t):
    P = PLAN
    h = 190
    (cy,), k = stack('hidayat', 'low', [h], caps=False)
    b = Box(f, t, CXL, cy, 720, h, P['hid_in'], P['hid_out'], r=38, style='amber', side=1, k=k)
    if not b.ok: return
    p = K.ease_out_back(K.lin(t, P['hid_in'] + 0.05, P['hid_in'] + 0.45), 1.3)
    b.put(K.icon_badge('warning', 52, bg=(0.85, 0.5, 0.02)), -310, -56, scale=max(0.01, p))
    b.put(T('ZAROORI HIDAYAT', 30, 'black', color=K.GOLD_L, tracking=2), -272, -56, anchor='l')
    sw = K.ease_out_cubic(K.lin(t, P['hid_wallet'] - 0.05, P['hid_wallet'] + 0.35))
    a1 = K.ease_out_cubic(K.lin(t, P['hid_phone'], P['hid_phone'] + 0.35)) * (1 - sw)
    if a1 > 0:
        b.put(K.icon_badge('sim', 68, bg=(0.5, 0.1, 0.12)), -296, 30, alpha=a1)
        b.put(K.icon_badge('cross', 28, bg=K.RED), -268, 4, alpha=a1)
        b.put(T('Mobile phone aur SIM', 30, 'xbold'), -244, 14, alpha=a1, anchor='l')
        b.put(T('kisi ghair mutaliqa shakhs ko na dein', 23, 'semi', color=(1, 0.92, 0.8)), -244, 52, alpha=a1, anchor='l')
    if sw > 0:
        b.put(K.icon_badge('shield', 68, bg=K.GREEN), -296, 30, alpha=sw, scale=0.8 + 0.2 * K.ease_out_back(sw, 1.3))
        b.put(T('Yeh aapka Digital Wallet hai', 30, 'xbold'), -244 + (1 - sw) * 18, 14, alpha=sw, anchor='l')
        b.put(T('iski hifazat karein!', 25, 'bold', color=K.GOLD_L), -244 + (1 - sw) * 18, 52, alpha=sw, anchor='l')


def sc_crore(f, t):
    P = PLAN
    (cyc, cyr), k = stack('crore', 'low', [100, 52], gap=12)
    b = Box(f, t, CXL, cyc, 620, 100, P['cr_in'], P['cr_out'], r=32, style='dark', k=k)
    if b.ok:
        sw = K.ease_out_cubic(K.lin(t, P['cr_globe'], P['cr_globe'] + 0.4))
        b.put(K.icon_badge('woman', 68, bg=K.GOLD_D), -250, 0, alpha=1 - sw)
        b.put(K.icon_badge('globe', 68, bg=K.GREEN), -250, 0, alpha=sw, scale=0.8 + 0.2 * K.ease_out_back(sw, 1.3))
        if sw < 1:
            b.put(T('1 Crore+', 42, 'black', grad=K.GOLD_GRAD, shadow=0.0), -200, -14, alpha=1 - sw, anchor='l')
            b.put(T('khawateen jor di gayin', 24, 'semi'), -200, 26, alpha=1 - sw, anchor='l')
        if sw > 0:
            b.put(T('Ghair mamooli peshraft', 32, 'black', grad=K.GOLD_GRAD, shadow=0.0), -200, -14, alpha=sw, anchor='l')
            b.put(T('Pakistan aur aalami satah par', 24, 'semi'), -200, 24, alpha=sw, anchor='l')
    chips = (('Digital Wallets', 'wallet', P['cr_chip1']), ('Interoperable Payments', 'phone', P['cr_chip2']))
    chips2 = (('Financial Inclusion', 'rise', P['cr_world']), ('Digital Social Protection', 'shield', P['cr_world'] + 0.3))
    for grp, t_out, sty in ((chips, P['cr_world'] - 0.35, 'dark'), (chips2, P['cr_out'], 'gold')):
        ws = [chip_width(txt, 23, 52) for txt, _, _ in grp]
        x = CXL - (sum(ws) + 14) * k / 2
        for (txt, ic, tt), wch in zip(grp, ws):
            chip(f, t, x + wch * k / 2, cyr, txt, ic, tt, t_out, style=sty, badge=K.GREEN, size=23, h=52, w=wch, k=k, side=1)
            x += (wch + 14) * k


def sc_khwab(f, t):
    P = PLAN
    chip_rows(f, t, 'khwab', 'top', [[('Paison se juri sahuliyaat', 'hand_coin', P['kh_chip1']),
                                      ('Digital madad tak rasai', 'phone', P['kh_chip2'])]], P['kh_chips_out'], size=24, h=52)
    tt = P['kh_title']
    g2 = K.ease_out_cubic(K.lin(t, P['kh_title2'] - 0.15, P['kh_title2'] + 0.2))
    g3 = K.ease_out_cubic(K.lin(t, P['kh_line2'] - 0.15, P['kh_line2'] + 0.2))
    full = 70 + 64 + 86
    (cyf,), k = stack('khwab', 'low', [full], caps=False)
    bottom = cyf + full * k / 2
    hh = 70 + 64 * g2 + 86 * g3
    b = Box(f, t, CXL, bottom - hh * k / 2, 700, hh, tt, P['end_in'] - 0.1, r=40, style='deep', side=1, k=k)
    if not b.ok: return
    oy = -hh / 2
    p1 = K.ease_out_back(K.lin(t, tt + 0.02, tt + 0.4), 1.3)
    b.put(T('Benazir ka', 34, 'xbold'), 0, oy + 36, scale=max(0.01, p1), alpha=min(1, p1 * 1.4))
    p2 = K.ease_out_back(K.lin(t, P['kh_title2'], P['kh_title2'] + 0.45), 1.3)
    if p2 > 0:
        b.put(T('Benazir Khwab!', 54, 'black', grad=K.GOLD_GRAD, shadow=0.0), 0, oy + 98, scale=max(0.01, p2))
    p3 = K.ease_out_cubic(K.lin(t, P['kh_line2'], P['kh_line2'] + 0.45))
    if p3 > 0:
        b.put(T('Har Aurat Khud Mukhtar, Ba Ikhtiyar!', 32, 'xbold', color=K.GOLD_L), 0, oy + 166 + (1 - p3) * 12, alpha=p3)
    for i in range(6):
        if t < P['kh_title2']: break
        q = ((t - tt) * 0.9 + i * 0.37) % 1.0
        side = -1 if i % 2 else 1
        x, y = b.pos(side * (318 + (i * 13) % 20), -hh / 2 + 22 + (i * 47) % max(1, int(hh - 44)))
        K.blit(f, K.icon('sparkle', 20, K.GOLD_L), x, y - q * 18, b.a * math.sin(math.pi * q) * 0.85, (0.6 + 0.5 * q) * k)


def sc_end(f, t):
    P = PLAN
    t0 = P['end_in']
    if t < t0: return
    e = K.ease_io(K.lin(t, t0, t0 + 0.7))
    small = cv2.resize(f, (W // 8, H // 8), interpolation=cv2.INTER_AREA)
    small = cv2.GaussianBlur(small, (0, 0), 6)
    bl = cv2.resize(small, (W, H), interpolation=cv2.INTER_LINEAR)
    bl = bl * 0.45 + np.array(K.GREEN_D, np.float32) * 0.35
    f[:] = f * (1 - e) + bl * e
    b = Box(f, t, 540, 900, 840, 720, t0 + 0.15, 1e9, r=64, style='dark', d_in=0.5, side=0, tag='endcard')
    if not b.ok: return
    p = K.ease_out_cubic(K.lin(t, t0 + 0.7, t0 + 1.1))
    b.put(T('Benazir ka Benazir Khwab!', 54, 'black', grad=K.GOLD_GRAD, shadow=0.0), 0, 60, alpha=p)
    p2 = K.ease_out_cubic(K.lin(t, t0 + 0.95, t0 + 1.35))
    b.put(T('Har Aurat Khud Mukhtar, Ba Ikhtiyar!', 36, 'bold'), 0, 128, alpha=p2)
    p3 = K.ease_out_back(K.lin(t, t0 + 1.25, t0 + 1.7), 1.3)
    if p3 > 0:
        x, y = b.pos(0, 246)
        K.glass(f, x, y, 740 * b.s * p3, 112 * b.s, 56, alpha=b.a * min(1, p3), **STY['green'])
        b.put(T('INTEROPERABILITY', 27, 'ui_x', color=K.GOLD_L, tracking=4, shadow=0.0), 0, 224, alpha=min(1, p3))
        b.put(T('Raqam Aapki, Intikhab Bhi Aapka!', 35, 'xbold'), 0, 266, alpha=min(1, p3))


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
CAP_SIZE = 56
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
    scale = min(1.0, 840 / total)
    x = CXL - total * scale / 2
    RECTS.append(('captions', x, CAP_Y - 44 * scale, x + total * scale, CAP_Y + 44 * scale))
    # active word = last word whose time has come (until the next one)
    act = max([i for i, w in enumerate(words) if t >= w['ot'] - 0.03] or [-1])
    for i, (w, L) in enumerate(zip(words, Ls)):
        cx = x + widths[i] * scale / 2
        x += (widths[i] + GAP) * scale
        tp = pg['t0'] + i * 0.035
        p = K.ease_out_back(K.lin(t, tp, tp + 0.16), 1.6)
        if p <= 0: continue
        dim = 1.0 if t >= w['ot'] - 0.05 else 0.78
        if i == act:
            bp = K.ease_out_back(K.lin(t, w['ot'] - 0.04, w['ot'] + 0.1), 1.5)
            K.fill_rrect(f, cx, CAP_Y + 3, (widths[i] + 24) * scale * (0.85 + 0.15 * bp), 82 * scale, 20, None,
                         alpha=fade * min(1, bp * 1.5), grad=(K.GREEN_L, K.GREEN))
        K.blit(f, L, cx, CAP_Y, fade * min(1, p * 1.6) * dim, scale * (0.8 + 0.2 * p))


# ---- frame ---------------------------------------------------------------------------------------------------------------
SCENES = [sc_hook, sc_wallets, sc_anytime, sc_vision, sc_whatis, sc_pehle, sc_ab, sc_rush, sc_banks, sc_faide, sc_steps,
          sc_hidayat, sc_crore, sc_khwab]


def render_frame(t):
    RECTS.clear()
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
        if typ == 'morph': continue
        if typ == 'glass': add(s['t0'], 'whoosh_slow', -9)
        elif typ == 'whip': add(s['t0'], 'whip', -7)
        elif typ == 'flash': add(s['t0'], 'flash_hit', -9)
        elif typ == 'punch': add(s['t0'], 'swish_small', -12)
    add(P['logo_pulse'] + 0.2, 'glass_tap', -10)
    add(P['crore_in'], 'card_slide', -9); add(P['crore_in'] + 0.2, 'slot_tick', -12, align='start'); add(P['crore_in'] + 1.45, 'coin_ring', -10)
    for k in ('any_pak', 'any_waqt', 'any_din', 'any_sahulat'): add(P[k], 'bubble_pop', -9)
    add(P['plate2'], 'card_slide', -10)
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
