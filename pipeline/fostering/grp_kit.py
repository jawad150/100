"""grp_kit.py: shared pieces for the Google Ranker Pro client testimonial edits (grp_leam.py, grp_of.py).

Both edits run at the footage's native 24 fps (FOSTER_FPS=24) on 1080x1920 Seedance clips registered in
workspace3/frames/manifest.json ('leam', 'of'). Everything follows core's convention (premultiplied linear RGBA
float32) except the footage pre-composite stage, which works on uint8 sRGB frames before the grade so that
screen replacements and clean-up patches are graded together with the shot.

FOOTAGE        frame_u8(cid, i) -> read-only RGB uint8;  fidx(t) -> nearest source frame (sub-samples of one
               output frame always land on the same source frame, so motion blur never ghosts the footage)
               shot_sprite(u8, look, center, zoom, sharpen) -> graded linear sprite, cover-cropped / punched in
               GRADES registered into footage.GRADES: 'leam_desk', 'leam_screen', 'leam_selfie', 'of_warm'
TEXT           T(txt, size, font, color, tracking) -> ui.Txt (cached);  shadowed(...) -> (sprite, ox, oy, adv)
SHAPES         panel(w, h, r, ...) -> sprite with soft shadow (body at pad, pad);  pill_text(...)
MASKS          masked(spr, mask) premultiplied multiply;  wipe(w, h, u, angle, soft);  iris(w, h, u, cx, cy)
               rrect_grow(w, h, u, r)
CARDS          browser_card(path, crop, width, url, ...) -> Card(spr, pad, content rect) (cached)
               image_crop(path, crop, width) -> sprite of a site capture region at a given width
CAPTIONS       Captions(asr_json, fixes, style).draw(cv, t)  word-timed pop-on captions, active word accent
LOGOS          leam_logo(h, strap_color) vector rebuild of the Leam Taxis pill logo; image_logo(path, width)
"""
import functools
import json
import math
import os

import cv2
import numpy as np

import core as K
import footage as F
import ui

REPO = K.REPO
PACK = os.path.join(REPO, 'google_ranker_pro_videos')
SITES = os.path.join(PACK, 'assets', 'sites')
GSC = os.path.join(PACK, 'assets', 'gsc')
ASR = os.path.join(PACK, 'edits', 'asr')
GRP = os.path.join(K.WS, 'grp')
W, H = K.W, K.H

# ---------------------------------------------------------------------------------------------- grades
F.GRADES.update({
    # overcast portakabin office: lift the grey-green cast, warmer skin, crisper contrast, cool window
    'leam_desk': dict(wb=(1.04, 0.985, 0.985), exposure=0.04, contrast=1.16, pivot=0.42, black=0.018,
                      black_tint=(0.10, 0.11, 0.13), shadow_tint=(-0.006, 0.0, 0.014),
                      highlight_tint=(0.010, 0.004, -0.010), sat=1.06, shoulder=0.92),
    'leam_screen': dict(wb=(1.02, 0.99, 1.0), exposure=0.0, contrast=1.12, pivot=0.40, black=0.015,
                        black_tint=(0.10, 0.11, 0.13), shadow_tint=(-0.004, 0.0, 0.012),
                        highlight_tint=(0.006, 0.004, -0.004), sat=1.04, shoulder=0.92),
    # selfie: the generated skin runs ruddy, so cool it a touch and pull saturation back
    'leam_selfie': dict(wb=(0.975, 1.0, 1.03), exposure=0.02, contrast=1.10, pivot=0.42, black=0.016,
                        black_tint=(0.10, 0.11, 0.13), shadow_tint=(-0.004, 0.0, 0.012),
                        highlight_tint=(0.006, 0.004, -0.006), sat=0.93, shoulder=0.92),
    # Organic Fostering office: warm, soft, plum-friendly shadows
    'of_warm': dict(wb=(1.025, 1.0, 0.975), exposure=0.03, contrast=1.10, pivot=0.42, black=0.02,
                    black_tint=(0.20, 0.12, 0.20), shadow_tint=(0.010, -0.004, 0.012),
                    highlight_tint=(0.012, 0.004, -0.010), sat=1.04, shoulder=0.92),
})


# ---------------------------------------------------------------------------------------------- footage
def fidx(t, n_frames=721, src_fps=24.0):
    """Nearest source frame for output time t (round, so +-0.25 frame sub-samples share a frame)."""
    return int(min(max(round(t * src_fps), 0), n_frames - 1))


def fidx_cut(t, cuts, n_frames=721, src_fps=24.0):
    """fidx() that never lets a motion-blur sub-sample cross a hard cut: cuts = [(t_cut, first_frame_of_new_shot)].
    (A sub-sample at t_cut - 1/144 s would otherwise round to the new shot's first frame.)"""
    fi = fidx(t, n_frames, src_fps)
    for tc, f0 in cuts:
        if t < tc and f0 <= fi < f0 + 3:
            fi = f0 - 1
        elif t >= tc and f0 - 3 <= fi < f0:
            fi = f0
    return fi


@functools.lru_cache(maxsize=40)
def frame_u8(cid, i):
    im = cv2.imread(os.path.join(K.FRAMES, cid, '%05d.jpg' % int(i)), cv2.IMREAD_COLOR)
    if im is None:
        raise FileNotFoundError((cid, i))
    im = cv2.cvtColor(im, cv2.COLOR_BGR2RGB)
    im.setflags(write=False)
    return im


def sharpen_u8(u8, amount=0.5, sigma=1.1):
    b = cv2.GaussianBlur(u8, (0, 0), sigma)
    return cv2.addWeighted(u8, 1.0 + amount, b, -amount, 0)


def shot_sprite(u8, look, center=(0.5, 0.5), zoom=1.0, sharpen=0.0, pan=(0.0, 0.0)):
    """Cover-crop (punch-in) an RGB uint8 frame to 1080x1920, optionally sharpen, grade -> linear sprite."""
    if zoom != 1.0 or tuple(center) != (0.5, 0.5) or pan != (0.0, 0.0):
        u8 = F.cover_crop(u8, W, H, center, zoom, 0.0, pan)
    if sharpen > 0:
        u8 = sharpen_u8(u8, sharpen)
    return F._to_sprite(np.ascontiguousarray(u8), look)


# ---------------------------------------------------------------------------------------------- text
def T(txt, size, font, color='#FFFFFF', tracking=0.0, weight=None):
    return ui.text(txt, size, font, color, tracking, 1.0, None, 0.0, weight)


@functools.lru_cache(maxsize=1024)
def shadowed(txt, size, font, color='#FFFFFF', tracking=0.0, shadow=0.55, blur=9.0, dy=4.0):
    """Text sprite with a soft drop shadow baked in. Returns (sprite, ox, oy, adv, cap): (ox, oy) = pen origin."""
    t = T(txt, size, font, color, tracking)
    p = int(blur * 3 + abs(dy) + 2)
    h, w = t.spr.shape[:2]
    out = np.zeros((h + 2 * p, w + 2 * p, 4), np.float32)
    a = np.zeros(out.shape[:2], np.float32)
    a[p + int(dy):p + int(dy) + h, p:p + w] = t.spr[..., 3]
    a = K.gblur(a, blur, border='constant') * np.float32(shadow)
    out[..., 3] = a
    ui.paste(out, t.spr, p, p)
    out.setflags(write=False)
    return out, t.ox + p, t.oy + p, t.adv, t.cap


def draw_text(cv, txt, x, y, size, font, color='#FFFFFF', anchor='ls', opacity=1.0, tracking=0.0,
              shadow=0.0, scale=1.0):
    """Draw a text run with its pen anchor ('ls', 'ms', 'rs', 'lm', 'mm', 'lt', ...) at (x, y)."""
    if shadow > 0:
        spr, ox, oy, adv, cap = shadowed(txt, size, font, color, tracking, shadow)
    else:
        t = T(txt, size, font, color, tracking)
        spr, ox, oy, adv, cap = t.spr, t.ox, t.oy, t.adv, t.cap
    hx = {'l': 0.0, 'm': 0.5, 'r': 1.0}[anchor[0]]
    base = {'s': 0.0, 'm': cap / 2, 't': cap}[anchor[1]]
    px = ox + hx * adv
    py = oy - base
    h, w = spr.shape[:2]
    if scale == 1.0:
        ui.paste(cv, spr, round(x - px), round(y - py), opacity)
    else:
        K.draw(cv, spr, x, y, scale=scale, opacity=opacity, anchor=(px / w, py / h))
    return adv


def measure(txt, size, font, tracking=0.0):
    return ui.measure(txt, size, font, tracking)


# ---------------------------------------------------------------------------------------------- shapes / masks
def lin(c):
    return ui.col(c)


@functools.lru_cache(maxsize=256)
def panel(w, h, r, fill='#141414', fill_a=0.86, border='#FFFFFF', border_a=0.10, border_w=2.0,
          shadow=0.45, shadow_blur=26.0, shadow_dy=14.0, accent=None, accent_w=8.0, grad=None, grad_angle=-90.0):
    """Rounded card sprite with a soft shadow. Body occupies (pad, pad, w, h). Returns (sprite, pad)."""
    pad = int(shadow_blur * 2.6 + abs(shadow_dy)) if shadow > 0 else 4
    S = ui.Surf(w + 2 * pad, h + 2 * pad)
    if shadow > 0:
        sh = ui.Surf(w + 2 * pad, h + 2 * pad)
        sh.rrect(pad, pad + shadow_dy, w, h, r, (0, 0, 0), 1.0)
        a = K.gblur(sh.img[..., 3], shadow_blur, border='constant') * np.float32(shadow)
        S.img[..., 3] = a
    if grad is not None:
        S.rrect_grad(pad, pad, w, h, r, grad[0], grad[1], angle=grad_angle, opacity=fill_a)
    else:
        S.rrect(pad, pad, w, h, r, lin(fill), fill_a)
    if accent is not None:
        a, X0, Y0 = S.rrect_mask(pad, pad, w, h, r)
        bar = np.zeros_like(a)
        xs = np.arange(a.shape[1]) + X0 + 0.5 - pad
        bar[:, :] = np.clip(accent_w - xs, 0, 1)[None, :]
        S.fill(a * bar, X0, Y0, lin(accent), 1.0)
    if border_a > 0:
        S.stroke_rrect(pad, pad, w, h, r, border_w, lin(border), border_a)
    S.img.setflags(write=False)
    return S.img, pad


def masked(spr, m):
    """Premultiplied sprite times a coverage mask (same h, w)."""
    return spr * m[..., None].astype(np.float32)


def wipe(w, h, u, angle=0.0, soft=0.06):
    """Linear wipe coverage: u=0 nothing, u=1 everything, travelling along `angle` (deg CCW from +x)."""
    a = math.radians(angle)
    dx, dy = math.cos(a), -math.sin(a)
    xs = (np.arange(w, dtype=np.float32) + 0.5) / w - 0.5
    ys = (np.arange(h, dtype=np.float32) + 0.5) / h - 0.5
    proj = xs[None, :] * dx + ys[:, None] * dy                     # -0.5..0.5 along the travel
    span = 0.5 * (abs(dx) + abs(dy))
    front = -span + u * (2 * span + soft)
    if soft <= 0:
        return (proj < front).astype(np.float32)
    return np.clip((front - proj) / soft, 0, 1).astype(np.float32)


def iris(w, h, u, cx=0.5, cy=0.5, soft=10.0):
    """Circle reveal from (cx, cy) (fractions); u=1 covers the far corner."""
    X = (np.arange(w, dtype=np.float32) + 0.5) - cx * w
    Y = (np.arange(h, dtype=np.float32) + 0.5) - cy * h
    d = np.sqrt(X[None, :] ** 2 + Y[:, None] ** 2)
    rmax = math.hypot(max(cx, 1 - cx) * w, max(cy, 1 - cy) * h) + soft
    return np.clip((u * rmax - d) / soft + 0.5, 0, 1).astype(np.float32)


def rrect_grow(w, h, u, r, cx=0.5, cy=0.5, w0=0.0, h0=0.0):
    """Rounded-rect coverage that grows from a (w0 x h0) box centred at (cx, cy) to the full sprite at u=1."""
    bw = w0 + (w - w0) * u
    bh = h0 + (h - h0) * u
    if bw < 1 or bh < 1:
        return np.zeros((h, w), np.float32)
    S = ui.Surf(w, h)
    a, X0, Y0 = S.rrect_mask(cx * w - bw / 2, cy * h - bh / 2, bw, bh, min(r, bw / 2, bh / 2))
    m = np.zeros((h, w), np.float32)
    if a is not None:
        m[Y0:Y0 + a.shape[0], X0:X0 + a.shape[1]] = a
    return m


def canvas_rrect_mask(x, y, w, h, r):
    """Full-canvas (H, W) coverage of a rounded rect (for masking footage into windows)."""
    m = np.zeros((H, W), np.float32)
    S = ui.Surf(W, H, img=None)
    a, X0, Y0 = S.rrect_mask(x, y, w, h, min(r, w / 2, h / 2))
    if a is not None:
        m[Y0:Y0 + a.shape[0], X0:X0 + a.shape[1]] = a
    return m


# ---------------------------------------------------------------------------------------------- images / cards
@functools.lru_cache(maxsize=64)
def _rgb(path):
    im = cv2.imread(path, cv2.IMREAD_UNCHANGED)
    if im is None:
        raise FileNotFoundError(path)
    if im.ndim == 2:
        im = cv2.cvtColor(im, cv2.COLOR_GRAY2BGR)
    if im.shape[2] == 4:
        im = cv2.cvtColor(im, cv2.COLOR_BGRA2RGBA)
    else:
        im = cv2.cvtColor(im, cv2.COLOR_BGR2RGB)
    im.setflags(write=False)
    return im


def site(*parts):
    return os.path.join(SITES, *parts)


@functools.lru_cache(maxsize=128)
def image_crop(path, crop=None, width=None, height=None):
    """Sprite of a crop (x, y, w, h) of an image, resized (area) to `width` (or height)."""
    im = _rgb(path)
    if crop is not None:
        x, y, w, h = crop
        im = im[y:y + h, x:x + w]
    if width is not None or height is not None:
        h0, w0 = im.shape[:2]
        if width is None:
            width = round(w0 * height / h0)
        nh = round(h0 * width / w0) if height is None else height
        interp = cv2.INTER_AREA if width < w0 else cv2.INTER_LANCZOS4
        im = cv2.resize(np.ascontiguousarray(im), (int(width), int(nh)), interpolation=interp)
    spr = K.sprite(np.ascontiguousarray(im))
    spr.setflags(write=False)
    return spr


class Card:
    __slots__ = ('spr', 'pad', 'w', 'h', 'content')

    def __init__(self, spr, pad, w, h, content):
        self.spr, self.pad, self.w, self.h, self.content = spr, pad, w, h, content

    def draw(self, cv, cx, cy, scale=1.0, opacity=1.0, mask=None, rot=0.0, blur=0.0):
        """Draw with the BODY centred at (cx, cy). mask: (h, w) coverage over the body (applied to the
        whole padded sprite, shadow included)."""
        spr = self.spr
        if mask is not None:
            m = np.zeros(spr.shape[:2], np.float32)
            m[self.pad:self.pad + self.h, self.pad:self.pad + self.w] = mask
            # let the shadow follow the revealed body
            m = np.maximum(m, K.gblur(m, 18, border='constant') * 0.999)
            spr = masked(spr, m)
        return K.draw(cv, spr, cx, cy, scale=scale, opacity=opacity, rot=rot, blur=blur)


@functools.lru_cache(maxsize=32)
def browser_card(path, crop, width, url, r=26, bar=58, theme='light', accent='#FFC61A', url_font='OpenSans-SemiBold',
                 shadow=0.5, max_h=None):
    """A clean browser window holding a site capture crop. Returns Card (body w x h, content rect)."""
    img = image_crop(path, crop, width)
    if max_h is not None and img.shape[0] > max_h:
        img = img[:max_h]
    ch = img.shape[0]
    w, h = width, bar + ch
    body, pad = panel(w, h, r, fill='#FFFFFF' if theme == 'light' else '#1B1B1B', fill_a=1.0,
                      border='#000000' if theme == 'light' else '#FFFFFF', border_a=0.10, border_w=1.5,
                      shadow=shadow, shadow_blur=30, shadow_dy=18)
    spr = body.copy()
    S = ui.Surf(spr.shape[1], spr.shape[0], img=spr)
    barc = '#F1F1F3' if theme == 'light' else '#262626'
    # title bar (top corners rounded via the body mask)
    a, X0, Y0 = S.rrect_mask(pad, pad, w, h, r)
    top = np.zeros_like(a)
    ys = np.arange(a.shape[0]) + Y0 + 0.5 - pad
    top[:] = (ys < bar)[:, None]
    S.fill(a * top, X0, Y0, lin(barc), 1.0)
    S.fill(a * ((ys >= bar - 1) & (ys < bar))[:, None].astype(np.float32), X0, Y0, lin('#000000'), 0.08)
    for i, c in enumerate(('#FF5F57', '#FEBC2E', '#28C840')):
        S.circle(pad + 30 + i * 24, pad + bar / 2, 7, lin(c), 1.0)
    pw = min(w - 220, 560)
    px = pad + (w - pw) / 2
    S.rrect(px, pad + 12, pw, bar - 24, (bar - 24) / 2, lin('#FFFFFF' if theme == 'light' else '#333333'), 1.0)
    lock = ui.icon('shield', 20, color='#5F6368' if theme == 'light' else '#BBBBBB', stroke=2.2)
    tw = measure(url, 22, url_font)
    tx = px + pw / 2 - (tw + 26) / 2
    ui.paste(spr, lock, round(tx - 2), round(pad + bar / 2 - lock.shape[0] / 2))
    S.text(round(tx + 26), round(pad + bar / 2 + 8), url, 22, url_font, '#3C4043' if theme == 'light' else '#DDDDDD')
    # content, clipped to the body's rounded bottom
    cm = np.zeros(spr.shape[:2], np.float32)
    cm[Y0:Y0 + a.shape[0], X0:X0 + a.shape[1]] = a
    sub = cm[pad + bar:pad + bar + ch, pad:pad + w]
    reg = spr[pad + bar:pad + bar + ch, pad:pad + w]
    m = sub[..., None]
    reg[...] = reg * (1 - m) + img[:, :w] * m
    spr.setflags(write=False)
    return Card(spr, pad, w, h, (0, bar, w, ch))


@functools.lru_cache(maxsize=16)
def browser_frame(width, view_h, url, r=26, bar=58, shadow=0.5, url_font='OpenSans-SemiBold'):
    """Empty browser window (white viewport) -> Card; .content = viewport rect (x, y, w, h) in body px.
    Use browser_view(card, content_sprite, scroll) to fill it per frame (scrolling pages)."""
    blank = np.full((view_h, width, 3), 255, np.uint8)
    path = os.path.join(K.WS, 'grp', '_blank_%dx%d.png' % (width, view_h))
    if not os.path.exists(path):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        cv2.imwrite(path, blank)
    return browser_card(path, None, width, url, r=r, bar=bar, shadow=shadow, url_font=url_font)


@functools.lru_cache(maxsize=16)
def _view_mask(card):
    x, y, w, h = card.content
    S = ui.Surf(card.spr.shape[1], card.spr.shape[0])
    a, X0, Y0 = S.rrect_mask(card.pad, card.pad, card.w, card.h, 26)
    m = np.zeros(card.spr.shape[:2], np.float32)
    m[Y0:Y0 + a.shape[0], X0:X0 + a.shape[1]] = a
    return m[card.pad + y:card.pad + y + h, card.pad + x:card.pad + x + w].copy()


def browser_view(card, content, scroll=0.0):
    """Copy of a browser_frame card with `content` (sprite, same width) scrolled by `scroll` px."""
    spr = card.spr.copy()
    x, y, w, h = card.content
    s = int(round(min(max(scroll, 0), max(0, content.shape[0] - h))))
    sub = content[s:s + h, :w]
    m = _view_mask(card)[:sub.shape[0], :sub.shape[1], None]
    reg = spr[card.pad + y:card.pad + y + sub.shape[0], card.pad + x:card.pad + x + sub.shape[1]]
    reg[...] = reg * (1 - m) + sub * m
    return Card(spr, card.pad, card.w, card.h, card.content)


@functools.lru_cache(maxsize=32)
def image_logo(path, width):
    return image_crop(path, None, width)


# ---------------------------------------------------------------------------------------------- Leam logo
LEAM_Y = '#FFC61A'
LEAM_K = '#1F1F1F'


@functools.lru_cache(maxsize=16)
def leam_logo(h=80, strap=True, strap_color='#FFFFFF', outline=False):
    """Vector rebuild of the Leam Taxis logo: yellow pill 'LEAM' (black, Montserrat SemiBold) + black pill
    'TAXIS' (yellow, Montserrat Light), optional 'On time. Every time.' strap. h = pill height (px)."""
    size = h * 0.62
    lw = measure('LEAM', size, 'Montserrat-Bold', 0.0)
    tw = measure('TAXIS', size, 'Montserrat-Light', 0.02)
    padx = h * 0.36
    w1 = lw + padx * 2 - h * 0.08
    w2 = tw + padx * 2 - h * 0.12
    W0 = w1 + w2
    sh = h * 0.40 if strap else 0
    S = ui.Surf(int(W0 + 8), int(h + sh + 8))
    ox, oy = 4, 4
    r = h / 2
    S.rrect(ox, oy, W0, h, r, lin(LEAM_K), 1.0)
    if outline:
        S.stroke_rrect(ox, oy, W0, h, r, 2.0, lin(LEAM_Y), 0.9)
    # yellow left half: rounded on the left only
    a, X0, Y0 = S.rrect_mask(ox, oy, w1 + r, h, r)
    xs = np.arange(a.shape[1]) + X0 + 0.5
    a = a * np.clip(ox + w1 - xs + 0.5, 0, 1)[None, :]
    S.fill(a, X0, Y0, lin(LEAM_Y), 1.0)
    cap = size * 0.70
    S.text(round(ox + padx), round(oy + h / 2 + cap / 2), 'LEAM', size, 'Montserrat-Bold', LEAM_K)
    S.text(round(ox + w1 + padx * 0.82), round(oy + h / 2 + cap / 2), 'TAXIS', size, 'Montserrat-Light', LEAM_Y,
           tracking=0.02)
    if strap:
        ss = h * 0.205
        txt = 'On time. Every time.'
        sw = measure(txt, ss, 'Montserrat-Regular', 0.32)
        S.text(round(ox + W0 / 2 - sw / 2), round(oy + h + sh * 0.80), txt, ss, 'Montserrat-Regular', strap_color,
               tracking=0.32)
    S.img.setflags(write=False)
    return S.img


# ---------------------------------------------------------------------------------------------- captions
def load_words(name, fixes=None, retime=None):
    """Words from edits/asr/<name>.json -> [(text, start, end)], with text fixes {index: 'text'} and
    retimes {index: (start, end)}."""
    with open(os.path.join(ASR, name + '.json')) as f:
        segs = json.load(f)
    words = []
    for s in segs:
        for w in s['words']:
            words.append([w['w'].strip(), float(w['s']), float(w['e'])])
    for i, txt in (fixes or {}).items():
        if txt is None:
            words[i][0] = None
        else:
            words[i][0] = txt
    for i, (s, e) in (retime or {}).items():
        words[i][1], words[i][2] = s, e
    return [tuple(w) for w in words if w[0]]


class Captions:
    """Word-timed captions: chunks of up to `max_chars`, split at sentence ends and pauses; each word pops on at
    its start (rise + fade), the active word takes the accent. style keys: font, size, color, accent, mode
    ('color' | 'pill'), pill_color, y (baseline of the last line), max_w, line_h, shadow, upper."""

    def __init__(self, words, style, max_chars=24, pause=0.42, breaks=()):
        self.style = dict(font='FiraSansCondensed-ExtraBold', size=68, color='#FFFFFF', accent='#FFC61A',
                          mode='color', pill_color='#B7006E', y=1560, max_w=900, line_h=1.12, shadow=0.6,
                          upper=False, hold=0.5, x=540)
        self.style.update(style)
        st = self.style
        self.words = [(w.upper() if st['upper'] else w, s, e) for w, s, e in words]
        # phrases: split at pauses, sentence ends and commas; then split long phrases into balanced pieces
        phrases, cur = [], []
        for i, (w, s, e) in enumerate(self.words):
            if cur:
                prev = cur[-1]
                n_cur = sum(len(x[0]) + 1 for x in cur)
                if s - prev[2] > pause or prev[0][-1] in '.?!' or (prev[0][-1] in ',;:' and n_cur > 10) \
                        or (w.lower().strip(',.') in ('and', 'but') and n_cur >= 12) or i in breaks:
                    phrases.append(cur)
                    cur = []
            cur.append((w, s, e))
        if cur:
            phrases.append(cur)
        chunks = []
        for ph in phrases:
            n_chars = sum(len(x[0]) + 1 for x in ph) - 1
            n = max(1, int(math.ceil(n_chars / float(max_chars))))
            if n == 1:
                chunks.append(ph)
                continue
            # balanced split points: cumulative character targets k * n_chars / n, nearest word boundary
            cum = np.cumsum([len(x[0]) + 1 for x in ph])
            cuts = []
            for k in range(1, n):
                j = int(np.argmin(np.abs(cum - k * n_chars / n)))
                # prefer the nearby boundary with the longest pause (a page should not flip right after a word
                # has popped on), as long as neither side grows past max_chars by much
                best, best_gap = j, -1.0
                for jj in (j - 1, j, j + 1):
                    if not (0 <= jj < len(ph) - 1):
                        continue
                    left = cum[jj] - (cum[cuts[-1] - 1] if cuts else 0)
                    if left > max_chars * 1.25:
                        continue
                    gap = ph[jj + 1][1] - ph[jj][1]
                    if gap > best_gap + 0.06:
                        best, best_gap = jj, gap
                j = best
                if j + 1 < len(ph) and (not cuts or j + 1 > cuts[-1]):
                    cuts.append(j + 1)
            prev_j = 0
            for j in cuts + [len(ph)]:
                chunks.append(ph[prev_j:j])
                prev_j = j
        self.chunks = []
        for k, c in enumerate(chunks):
            t0 = c[0][1] - 0.08
            nxt = chunks[k + 1][0][1] - 0.08 if k + 1 < len(chunks) else 1e9
            t1 = min(c[-1][2] + st['hold'], nxt)
            self.chunks.append(dict(words=c, t0=t0, t1=t1, lines=self._layout(c)))

    def _layout(self, c):
        st = self.style
        sp = measure(' ', st['size'], st['font'])
        lines, cur, cw = [], [], 0.0
        for w, s, e in c:
            ww = measure(w, st['size'], st['font'])
            if cur and cw + sp + ww > st['max_w']:
                lines.append((cur, cw))
                cur, cw = [], 0.0
            cur.append((w, s, e, ww))
            cw = ww if len(cur) == 1 else cw + sp + ww
        if cur:
            lines.append((cur, cw))
        out = []
        n = len(lines)
        for li, (ws, lw) in enumerate(lines):
            y = st['y'] - (n - 1 - li) * st['size'] * st['line_h']
            x = st['x'] - lw / 2
            row = []
            for w, s, e, ww in ws:
                row.append((w, s, e, x, ww))
                x += ww + sp
            out.append((y, row))
        return out

    def active_chunk(self, t):
        for c in self.chunks:
            if c['t0'] <= t < c['t1']:
                return c
        return None

    def draw(self, cv, t, opacity=1.0, dy=0.0, color=None, shadow=None):
        st = dict(self.style)
        if color is not None:
            st['color'] = color
        if shadow is not None:
            st['shadow'] = shadow
        c = self.active_chunk(t)
        if c is None:
            return
        fade = K.clamp((c['t1'] - t) / 0.12) * opacity
        cur = None                                         # the one active word: last started, not long over
        for w, s, e in c['words']:
            if s - 0.03 <= t:
                cur = (w, s, e)
        if cur is not None and t > cur[2] + 0.30:
            cur = None
        for y, row in c['lines']:
            for w, s, e, x, ww in row:
                if t < s - 0.07:
                    continue
                u = K.ramp(t, s - 0.07, s + 0.10, 'out_cubic')
                active = cur is not None and cur[1] == s and cur[0] == w
                col = st['accent'] if active else st['color']      # pill mode: accent = text colour on the pill
                yy = y + dy + (1 - u) * 18
                if active and st['mode'] == 'pill':
                    pu = K.ramp(t, s - 0.05, s + 0.06, 'out_cubic')
                    pw, ph = ww + 26, st['size'] * 1.02
                    pill, pp = panel(int(pw), int(ph), int(ph * 0.28), fill=st['pill_color'], fill_a=1.0,
                                     border_a=0.0, shadow=0.35, shadow_blur=10, shadow_dy=5)
                    K.draw(cv, pill, x + ww / 2, yy - st['size'] * 0.34, scale=0.9 + 0.1 * pu,
                           opacity=fade * pu)
                draw_text(cv, w, x + ww / 2, yy, st['size'], st['font'], col, 'ms', opacity=fade * u,
                          shadow=st['shadow'] if not (active and st['mode'] == 'pill') else 0.25,
                          scale=0.94 + 0.06 * u)


# ---------------------------------------------------------------------------------------------- misc
def ease(u, kind='out_cubic'):
    return K.get_ease(kind)(K.clamp(u))


def spring_in(t, t0, freq=2.4, damping=0.55):
    """0 before t0, springs to 1 with a small overshoot."""
    return K.spring(t - t0, freq, damping) if t >= t0 else 0.0


def window(t, t0, t1, fin=0.25, fout=0.25):
    """1 inside [t0, t1] with eased in / out ramps."""
    return min(K.ramp(t, t0, t0 + fin, 'out_cubic'), 1 - K.ramp(t, t1 - fout, t1, 'in_cubic'))


# ---------------------------------------------------------------------------------------------- depth layering
@functools.lru_cache(maxsize=6)
def person_alpha_u8(cid, i):
    """Person matte (Robust Video Matting, grp_prep.py mattes) for source frame i, uint8 (H, W) or None."""
    m = cv2.imread(os.path.join(GRP, 'person_%s' % cid, '%05d.png' % int(i)), cv2.IMREAD_GRAYSCALE)
    if m is not None:
        m.setflags(write=False)
    return m


def person_sprite(spr, cid, i, center=(0.5, 0.5), zoom=1.0, choke=0.0):
    """The footage sprite (already cropped with center / zoom) times the person matte cropped the same way:
    composite it over graphics to put them BEHIND the speaker."""
    m = person_alpha_u8(cid, i)
    if m is None:
        return None
    if zoom != 1.0 or tuple(center) != (0.5, 0.5):
        m = F.cover_crop(np.dstack([m, m, m]), W, H, center, zoom)[..., 0]
    a = m.astype(np.float32) * np.float32(1 / 255.0)
    if choke > 0:
        a = np.clip((a - choke) / (1 - choke), 0, 1)
    return spr * a[..., None]


@functools.lru_cache(maxsize=4)
def _shade_ramp(y0, strength):
    y = np.arange(H, dtype=np.float32)
    r = np.clip((y - y0) / max(H - y0, 1), 0, 1) ** 1.6 * strength
    return (1 - r)[:, None, None].astype(np.float32)


def bottom_shade(cv, strength=0.42, y0=1350, opacity=1.0):
    """Soft dark gradient at the bottom of frame (caption legibility over bright footage)."""
    if opacity <= 0:
        return
    k = _shade_ramp(int(y0), round(float(strength * opacity), 3))
    cv[..., :3] *= k
