"""anim4_props.py: 3D prop access for anim4.py (ANIM 4 "£447.60: BUT WHAT IS IT FOR?"), with stand-ins.

The Blender day renders arrive progressively in workspace3/assets3d/<name>/<folder>/ (complete when meta.json
exists). prop() returns the real sprites3d.Asset3D once its meta.json exists and a labelled stand-in until then,
so layout and timing can be built before the renders land. Stand-ins expose the same interface (at_yaw, at_time,
frame, blend, float_yaw, by_label, size, anchor, pivot, bbox, ground_y, n, mode) and carry .placeholder = True.

    import anim4_props as P
    house = P.prop('house')                         # day yaw sweep
    coin = P.prop('coin_gbp', mode='spin', scale=0.4)   # folder day_spin; stand-in = procedural gold coin
    basket = P.prop('basket', 'day_full')
    P.status() -> {name/folder: True|False}         # which renders are ready
    P.missing() -> list of missing folders

Pure: no side effects on import; everything cached per process (lru_cache).
"""
import functools
import math
import os

import numpy as np

import core as K

# every folder anim4 uses: (name, variant, mode)
NEEDED = [('coin_gbp', 'day', None), ('coin_gbp', 'day', 'spin'), ('question', 'day', 'spin'),
          ('question', 'day', None), ('house', 'day', None), ('bed', 'day', None), ('apple', 'day', None),
          ('sandwich', 'day', None), ('plate', 'day', None), ('basket', 'day', None), ('basket', 'day_full', None),
          ('tshirt', 'day', None), ('trainer', 'day', None), ('backpack', 'day', None), ('school_bus', 'day', None),
          ('school_bus', 'day_side', None), ('football', 'day', None), ('paint_palette', 'day', None),
          ('child_figure', 'day', None), ('book_pencil', 'day', None), ('heart', 'day', None), ('orbs', 'day', None)]

# stand-in colours (sRGB) per prop
_COL = dict(coin_gbp='#FFB15C', question='#B7006E', house='#FF6411', bed='#8E7BD8', apple='#E2342B',
            sandwich='#E8B25A', plate='#DDE3EA', basket='#C98A45', tshirt='#FF3D9A', trainer='#5B8DEF',
            backpack='#64A60B', school_bus='#FFC21A', football='#EDEDED', paint_palette='#D9A06A',
            child_figure='#FF6411', book_pencil='#4C7BD9', heart='#FF3D9A', orbs='#F6EAF3', check_tile='#64A60B')


def folder_of(variant='day', mode=None):
    return variant if not mode else '%s_%s' % (variant, mode)


def ready(name, variant='day', mode=None):
    return os.path.exists(os.path.join(K.ASSETS3D, name, folder_of(variant, mode), 'meta.json'))


def status():
    return {'%s/%s' % (n, folder_of(v, m)): ready(n, v, m) for n, v, m in NEEDED}


def missing():
    return [k for k, ok in status().items() if not ok]


def prop(name, variant='day', mode=None, scale=1.0):
    """Real Asset3D when its render is complete, else a stand-in with the same interface."""
    ok = ready(name, variant, mode)
    return _prop(name, variant, mode, float(scale), ok)


@functools.lru_cache(maxsize=96)
def _prop(name, variant, mode, scale, ok):
    if ok:
        import sprites3d as S3
        a = S3.get(name, variant, mode=mode, scale=scale)
        a.placeholder = False
        return a
    if name == 'coin_gbp':
        return CoinStandIn(scale, mode or 'yaw')
    return StandIn(name, folder_of(variant, mode), scale)


# ------------------------------------------------------------------------------------------- stand-ins
class _Base:
    placeholder = True
    fallback = True
    labels = []
    features = {}
    yaw_range = (-40.0, 40.0)
    loop = True
    fps = 30.0

    def frame(self, i):
        return self.at_yaw(0.0)

    def at_time(self, t, fps=None, loop=None, interp=None):
        return self.at_yaw(0.0)

    def float_yaw(self, t, amp=14.0, period=4.5, phase=0.0, interp=None):
        return self.at_yaw(amp * math.sin(2 * math.pi * (t / period + phase)))

    def blend(self, x, interp=None):
        return self.at_yaw(0.0)

    def by_label(self, label):
        return self.at_yaw(0.0)

    def feature(self, key, x=None):
        return self.anchor


class StandIn(_Base):
    """Labelled soft disc (720 px at scale 1, object radius ~300 px): placeholder for a 3D prop."""
    mode = 'yaw'
    n = 33

    def __init__(self, name, folder, scale):
        self.name, self.folder, self.scale = name, folder, scale
        s = int(round(720 * scale))
        self.size = (s, s)
        self.anchor = (s / 2, s / 2)
        self.pivot = self.anchor
        r = 300 * scale
        self.bbox = (s / 2 - r, s / 2 - r, s / 2 + r, s / 2 + r)
        self.ground_y = s / 2 + r
        self._spr = _standin_sprite(name, folder, s)

    def at_yaw(self, deg, interp=None):
        return self._spr


@functools.lru_cache(maxsize=48)
def _standin_sprite(name, folder, s):
    from PIL import Image, ImageDraw, ImageFont
    S = 2 * s
    im = Image.new('RGBA', (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    col = _COL.get(name, '#999999')
    rgb = tuple(int(col[i:i + 2], 16) for i in (1, 3, 5))
    r = int(300 / 720 * S)
    c = S // 2
    for k in range(r, 0, -2):                       # soft radial shading, light top-left
        f = k / r
        sh = tuple(int(min(255, v * (0.78 + 0.35 * (1 - f)) + 40 * (1 - f))) for v in rgb)
        o = int((1 - f) * r * 0.18)
        d.ellipse([c - k - o, c - k - o, c + k - o, c + k - o], fill=sh + (255,))
    d.ellipse([c - r, c - r, c + r, c + r], outline=(255, 255, 255, 230), width=max(2, S // 160))
    try:
        fnt = ImageFont.truetype(K.font_path('Poppins-SemiBold'), max(10, S // 14))
    except Exception:
        fnt = ImageFont.load_default()
    lab = name.replace('_', ' ')
    dark = sum(rgb) > 520
    d.text((c, c), lab, font=fnt, anchor='mm', fill=(50, 31, 53, 255) if dark else (255, 255, 255, 255))
    d.text((c, c + S // 11), folder, font=fnt, anchor='mm', fill=(50, 31, 53, 160) if dark else (255, 255, 255, 170))
    im = im.resize((s, s), Image.LANCZOS)
    spr = K.sprite(im)
    spr.setflags(write=False)
    return spr


class CoinStandIn(_Base):
    """Procedural gold GBP coin (spin about the vertical axis): face squashed by |cos(yaw)| plus a darker rim
    band for the edge thickness. 512 px at scale 1, coin radius 230 px."""

    def __init__(self, scale, mode):
        self.scale = scale
        self.mode = 'spin' if mode == 'spin' else 'yaw'
        self.n = 48 if self.mode == 'spin' else 33
        s = int(round(512 * scale))
        self.size = (s, s)
        self.anchor = (s / 2, s / 2)
        self.pivot = self.anchor
        r = 230 * scale
        self.bbox = (s / 2 - r, s / 2 - r, s / 2 + r, s / 2 + r)
        self.ground_y = s / 2 + r

    def at_yaw(self, deg, interp=None):
        q = int(round((deg % 360.0) / 5.0)) % 72
        return _coin_frame(self.size[0], q * 5)

    def at_time(self, t, fps=None, loop=None, interp=None):
        return self.at_yaw(t * 360.0 / 1.6)


@functools.lru_cache(maxsize=4)
def _coin_face(s):
    from PIL import Image, ImageDraw, ImageFont
    S = 2 * s
    yy, xx = np.mgrid[0:S, 0:S].astype(np.float32)
    c = S / 2
    r = 230 / 512 * S
    d = np.hypot(xx - c, yy - c) / r
    # gold: bright top-left, deep orange bottom-right, raised rim
    lit = np.clip(0.55 + 0.45 * (-(xx - c) * 0.6 - (yy - c) * 0.8) / r, 0, 1)
    base = np.array([255, 196, 106], np.float32) / 255.0
    hi = np.array([255, 241, 210], np.float32) / 255.0
    lo = np.array([214, 112, 22], np.float32) / 255.0
    col = lo[None, None] + (base - lo)[None, None] * lit[..., None]
    col = col + (hi - col) * (np.clip(lit - 0.75, 0, 1) * 3.0)[..., None]
    rim = ((d > 0.84) & (d <= 1.0)).astype(np.float32)
    col = col * (1 - 0.18 * rim[..., None]) + 0.10 * rim[..., None] * hi
    a = np.clip((1.0 - d) * r + 0.5, 0, 1)
    img = np.dstack([np.clip(col, 0, 1) * 255, a * 255]).astype(np.uint8)
    im = Image.fromarray(img, 'RGBA')
    dr = ImageDraw.Draw(im)
    fnt = ImageFont.truetype(K.font_path('Nunito-Black'), int(S * 0.42))
    dr.text((c + S * 0.006, c + S * 0.012), '£', font=fnt, anchor='mm', fill=(150, 62, 8, 255))
    dr.text((c, c), '£', font=fnt, anchor='mm', fill=(255, 226, 160, 255))
    dr.ellipse([c - r * 0.80, c - r * 0.80, c + r * 0.80, c + r * 0.80], outline=(196, 102, 20, 255),
               width=max(2, S // 110))
    im = im.resize((s, s), Image.LANCZOS)
    spr = K.sprite(im)
    spr.setflags(write=False)
    return spr


@functools.lru_cache(maxsize=80)
def _coin_frame(s, deg):
    import cv2
    face = _coin_face(s)
    a = math.radians(deg)
    cx = abs(math.cos(a))
    th = 0.075 * s * abs(math.sin(a))               # edge thickness on screen
    out = np.zeros_like(face)
    w = max(2, int(round(s * max(cx, 0.02))))
    sq = cv2.resize(face, (w, s), interpolation=cv2.INTER_AREA)
    x0 = (s - w) // 2
    edge = sq.copy()
    edge[..., :3] *= np.array([0.62, 0.40, 0.16], np.float32)
    n = max(1, int(th))
    side = 1 if math.sin(a) >= 0 else -1
    for k in range(n, 0, -1):
        dx = int(round(side * k * 0.5))
        xs = x0 + dx
        lo, hi = max(0, xs), min(s, xs + w)
        if hi > lo:
            seg = edge[:, lo - xs:hi - xs]
            dst = out[:, lo:hi]
            dst *= 1 - seg[..., 3:4]
            dst += seg
    xs = x0 - side * int(round(n * 0.5))
    lo, hi = max(0, xs), min(s, xs + w)
    seg = sq[:, lo - xs:hi - xs] * (0.55 + 0.45 * cx)
    seg[..., 3] = sq[:, lo - xs:hi - xs, 3]
    dst = out[:, lo:hi]
    dst *= 1 - seg[..., 3:4]
    dst += seg
    out.setflags(write=False)
    return out


if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == 'status':
        for k, v in status().items():
            print('%-26s %s' % (k, 'ready' if v else '-'))
    elif len(sys.argv) > 1 and sys.argv[1] == 'sheet':
        # every ready folder at yaw -20 / 0 / +20 on the anim4 white page -> out/anim4/dev/props_sheet.png
        import anim4_fx as X
        ready_ = [(n, v, m) for n, v, m in NEEDED if ready(n, v, m)]
        cols = 3
        tile = 360
        H_ = tile * len(ready_)
        cv = np.ones((max(tile, H_), tile * cols, 4), np.float32)
        cv[..., :3] = X.lin('#FFFFFF') * 1.1
        for r, (n, v, m) in enumerate(ready_):
            a = prop(n, v, m, scale=0.45)
            for k, yaw in enumerate((-20.0, 0.0, 20.0)):
                spr = a.frame(0) if getattr(a, 'mode', 'yaw') == 'static' else a.at_yaw(yaw)
                K.draw(cv, spr, tile * k + tile / 2, tile * r + tile / 2, scale=0.9 * tile / spr.shape[1])
        d = os.path.join(K.OUT, 'anim4', 'dev')
        os.makedirs(d, exist_ok=True)
        K.save_png(os.path.join(d, 'props_sheet.png'), K.to_srgb8(cv))
        print('->', os.path.join(d, 'props_sheet.png'), [n + '/' + folder_of(v, m) for n, v, m in ready_])
    else:
        os.makedirs(K.SELFTEST, exist_ok=True)
        cv = K.new_canvas(K.C['IVORY'])
        for i, (n, v, m) in enumerate(NEEDED[:12]):
            p = prop(n, v, m, scale=0.4)
            K.draw(cv, p.at_yaw(30.0 * i), 140 + 260 * (i % 4), 200 + 300 * (i // 4))
        K.save_png(os.path.join(K.SELFTEST, 'anim4_props.png'), K.post(cv, 'airy', 0.0))
        print('->', os.path.join(K.SELFTEST, 'anim4_props.png'))
