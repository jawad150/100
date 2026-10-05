"""Frame-accurate 9:16 edit engine: ffmpeg decodes (and grades through a 3D LUT),
numpy/OpenCV reframes, transitions and finishes each output frame.

Output 1080x1920 (9:16); REEL_SCALE=0.5 renders a quick preview.
A shot's view = (cx, cy, cw): centre and width (source px) of the 9:16 window at zoom 1.
The window may run past the source edge; that part renders black (use only where it is hidden).
"""
import math
import os
import subprocess

import cv2
import numpy as np

FPS_NUM, FPS_DEN = 24000, 1001
FPS = FPS_NUM / FPS_DEN
SCALE = float(os.environ.get("REEL_SCALE", "1"))
W, H = int(round(1080 * SCALE / 2) * 2), int(round(1920 * SCALE / 2) * 2)


def F(sec):
    """seconds -> frame count"""
    return int(round(sec * FPS))


def ease_io(x):
    x = min(max(x, 0.0), 1.0)
    return x * x * (3 - 2 * x)


def ease_out(x):
    x = min(max(x, 0.0), 1.0)
    return 1 - (1 - x) ** 3


def ease_in(x):
    x = min(max(x, 0.0), 1.0)
    return x ** 3


def linear(x):
    return min(max(x, 0.0), 1.0)


# ------------------------------------------------------------------ decoding

class Reader:
    def __init__(self, path, t0, n, vf, size, dur=None):
        self.size, self.n, self.got = size, n, 0
        ow, oh = size
        lim = ["-t", f"{dur:.4f}"] if dur else []
        cmd = ["ffmpeg", "-v", "error", "-ss", f"{max(0.0, t0):.4f}", *lim, "-i", path, "-an", "-sn",
               "-vf", vf, "-frames:v", str(n), "-f", "rawvideo", "-pix_fmt", "bgr48le", "-"]
        self.p = subprocess.Popen(cmd, stdout=subprocess.PIPE, bufsize=ow * oh * 6 * 2)
        self.last = None

    def read(self):
        ow, oh = self.size
        nb = ow * oh * 6
        if self.got < self.n:
            buf = self.p.stdout.read(nb)
            if len(buf) == nb:
                self.last = np.frombuffer(buf, np.uint16).reshape(oh, ow, 3).astype(np.float32) * (1 / 65535)
                self.got += 1
        if self.last is None:
            self.last = np.zeros((oh, ow, 3), np.float32)
        return self.last

    def close(self):
        try:
            self.p.stdout.close()
            self.p.kill()
            self.p.wait()
        except Exception:
            pass


def mono(img, mix=(0.30, 0.52, 0.18), contrast=1.25, pivot=0.42, tone=(1.0, 1.0, 1.0)):
    """Cinematic black and white: R/G/B channel mix, then an S-curve around the pivot."""
    b, g, r = img[..., 0], img[..., 1], img[..., 2]
    y = mix[0] * r + mix[1] * g + mix[2] * b
    y = np.clip(y, 0, 1.5)
    # log-ish S-curve: deeper blacks, rolled highlights
    x = np.clip(y, 1e-4, None)
    s = 1 / (1 + (pivot / x) ** (2.2 * contrast))
    s0 = 1 / (1 + (pivot / 1e-4) ** (2.2 * contrast))
    s1 = 1 / (1 + (pivot / 1.0) ** (2.2 * contrast))
    y = (s - s0) / (s1 - s0)
    return np.dstack([y * tone[2], y * tone[1], y * tone[0]])


class Shot:
    """A piece of picture.

    kind 'broll': vertical 2160x3840 S-Log3 clip graded by `lut`.
    kind 'spk':   vertical 2160x3840 graded interview export (tv range, Rec.709).
    view = (cx, cy, cw) window at zoom 1; zoom = (z0, z1) push; pan in output px at zoom 1;
    anchor = output point the zoom is centred on (default frame centre).
    """

    def __init__(self, src, t, dur, view, kind="broll", lut=None, zoom=(1.0, 1.0),
                 pan=((0, 0), (0, 0)), ease=ease_io, speed=1.0, label="", gain=1.0,
                 flash_in=0, flash_out=0, sat=1.0, rng="pc", bw=None, anchor=None,
                 src_size=(2160, 3840), visible=(0.0, 1.0)):
        self.src, self.t, self.dur = src, t, dur
        self.view, self.kind, self.lut = view, kind, lut
        self.zoom, self.pan, self.ease = zoom, pan, ease
        self.speed, self.label, self.gain = speed, label, gain
        self.flash_in, self.flash_out, self.sat = flash_in, flash_out, sat
        self.rng, self.bw, self.anchor = rng, bw, anchor
        self.src_size = src_size
        self.visible = visible          # output rows (fraction of H) that can ever be seen
        self.n = F(dur)
        self.start = 0
        self.pre = 0
        self.post = 0
        self.reader = None
        self.reverse = False

    def open(self, skip=0):
        cx, cy, cw = self.view
        sw, sh = self.src_size
        ch = cw * H / W
        # source rows/cols that can reach the visible part of the output (with zoom <= 1 margin)
        v0, v1 = self.visible
        y_lo = cy - ch / 2 + v0 * ch
        y_hi = cy - ch / 2 + v1 * ch
        x0 = max(0.0, cx - cw / 2)
        x1 = min(float(sw), cx + cw / 2)
        y0 = max(0.0, y_lo)
        y1 = min(float(sh), y_hi)
        x0, y0 = int(math.floor(x0 / 2) * 2), int(math.floor(y0 / 2) * 2)
        x1, y1 = int(math.ceil(x1 / 2) * 2), int(math.ceil(y1 / 2) * 2)
        x1, y1 = min(x1, sw), min(y1, sh)
        self.win = (x0, y0, x1 - x0, y1 - y0)
        # decode a little larger than output when the shot moves, to keep pushes sharp
        moving = max(self.zoom) > 1.001 or any(abs(v) > 0 for p in self.pan for v in p)
        k = min(1.35, max(self.zoom) * 1.04) if moving else 1.0
        s_dec = (W / cw) * k
        s_dec = min(s_dec, 1.0)                 # never decode above source resolution
        self.s_dec = s_dec
        ow = int(round((x1 - x0) * s_dec / 2) * 2)
        oh = int(round((y1 - y0) * s_dec / 2) * 2)
        self.ow, self.oh = ow, oh
        self.s_dec_x, self.s_dec_y = ow / (x1 - x0), oh / (y1 - y0)
        rng = self.rng if self.kind == "broll" else "tv"
        vf = (f"crop={x1 - x0}:{y1 - y0}:{x0}:{y0},"
              f"scale={ow}:{oh}:flags=lanczos:in_color_matrix=bt709:in_range={rng}:out_range=pc,format=rgb48le")
        if self.kind == "broll":
            vf += f",lut3d=file={self.lut}:interp=tetrahedral"
        if self.speed != 1.0:
            vf = f"setpts=PTS/{self.speed},fps={FPS_NUM}/{FPS_DEN}," + vf
        self.vf = vf
        total = self.pre + self.n + self.post - skip
        if self.reverse:
            t_end = self.t - (skip - self.pre) / FPS
            self.reader = Reader(self.src, t_end - total / FPS, total, vf + ",reverse", (ow, oh),
                                 dur=total / FPS + 0.5 / FPS)
        else:
            t0 = self.t - (self.pre - skip) / FPS * self.speed
            self.reader = Reader(self.src, t0, total, vf, (ow, oh))

    def frame(self, i, extra_zoom=1.0, extra_pan=(0.0, 0.0)):
        """i = frame index relative to the shot's first frame (negative in pre-roll)."""
        if self.reader is None:
            self.open()
        img = self.reader.read()
        u = i / max(1, self.n - 1)
        e = self.ease(u)
        z = (self.zoom[0] + (self.zoom[1] - self.zoom[0]) * e) * extra_zoom
        (px0, py0), (px1, py1) = self.pan
        px = (px0 + (px1 - px0) * e) * SCALE + extra_pan[0]
        py = (py0 + (py1 - py0) * e) * SCALE + extra_pan[1]
        cx, cy, cw = self.view
        ax, ay = (W / 2, H / 2) if self.anchor is None else (self.anchor[0] * SCALE, self.anchor[1] * SCALE)
        base = W / cw                              # output px per source px at zoom 1
        x0, y0, _, _ = self.win
        # source -> output at zoom 1: X = W/2 + base*(sx - cx);  zoom about the anchor point
        # decoded pixel u -> source sx = x0 + u / s_dec
        ax_s = cx + (ax - W / 2) / base
        ay_s = cy + (ay - H / 2) / base
        a_x = z * base / self.s_dec_x
        a_y = z * base / self.s_dec_y
        bx = ax + z * base * (x0 - ax_s) + px
        by = ay + z * base * (y0 - ay_s) + py
        M = np.array([[a_x, 0, bx], [0, a_y, by]], np.float32)
        out = cv2.warpAffine(img, M, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
        if self.gain != 1.0:
            out *= self.gain
        if self.sat != 1.0:
            y = out.mean(axis=2, keepdims=True)
            out = y + (out - y) * self.sat
        if self.bw:
            out = mono(out, **(self.bw if isinstance(self.bw, dict) else {}))
        # flash frames (overexposed bloom) at shot head/tail
        fl = 0.0
        if self.flash_in and 0 <= i < self.flash_in:
            fl = 1 - i / self.flash_in
        if self.flash_out and self.n - self.flash_out <= i < self.n:
            fl = max(fl, (i - (self.n - self.flash_out) + 1) / self.flash_out)
        if fl > 0:
            out = flash(out, fl)
        return out

    def close(self):
        if self.reader:
            self.reader.close()
            self.reader = None


# ------------------------------------------------------------------ effects

def _small(img, f=4):
    return cv2.resize(img, (img.shape[1] // f, img.shape[0] // f), interpolation=cv2.INTER_AREA)


def bloom(img, strength=0.12, sigma=14, thresh=0.70):
    sm = _small(img)
    hi = np.clip((sm - thresh) / (1 - thresh), 0, 1)
    b = cv2.GaussianBlur(hi, (0, 0), sigma * SCALE / 4 + 0.5)
    return img + strength * cv2.resize(b, (img.shape[1], img.shape[0]), interpolation=cv2.INTER_LINEAR)


def halation(img, strength=0.06, sigma=10, thresh=0.62):
    """Film halation: a warm red glow bleeding around bright edges."""
    sm = _small(img)
    lum = sm.max(axis=2)
    hi = np.clip((lum - thresh) / (1 - thresh), 0, 1)
    b = cv2.GaussianBlur(hi, (0, 0), sigma * SCALE / 4 + 0.5)
    b = cv2.resize(b, (img.shape[1], img.shape[0]), interpolation=cv2.INTER_LINEAR)
    return img + strength * b[..., None] * np.array([0.10, 0.35, 1.0], np.float32)


def flash(img, amount):
    """Overexposed, blooming flash frame (amount 0..1)."""
    g = 1 + 1.6 * amount
    out = img * g
    out = bloom(out, strength=0.7 * amount, sigma=22, thresh=0.55)
    return out + 0.06 * amount


def radial_blur(img, amount, n=7, center=None):
    if amount <= 2e-3:
        return img
    h, w = img.shape[:2]
    cx, cy = (w / 2, h / 2) if center is None else center
    acc = np.zeros_like(img)
    for j in range(n):
        s = 1 + amount * j / (n - 1)
        M = np.array([[s, 0, cx - s * cx], [0, s, cy - s * cy]], np.float32)
        acc += cv2.warpAffine(img, M, (w, h), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
    return acc / n


def dir_blur(img, length, vertical=False):
    length = int(length)
    if length < 2:
        return img
    k = (1, length) if vertical else (length, 1)
    return cv2.blur(img, k, borderType=cv2.BORDER_REFLECT)


_leak = {}


def light_leak(t, seed=3, warm=(1.0, 0.58, 0.28)):
    """Soft drifting amber light leak (BGR, 0..1)."""
    if seed not in _leak:
        rng = np.random.default_rng(seed)
        _leak[seed] = [(rng.uniform(-0.1, 1.1), rng.uniform(-0.1, 1.1), rng.uniform(0.22, 0.5),
                        rng.uniform(-0.6, 0.6), rng.uniform(-0.3, 0.3)) for _ in range(4)]
    sw, sh = 54, 96
    yy, xx = np.mgrid[0:sh, 0:sw].astype(np.float32)
    xx /= sw
    yy /= sh
    acc = np.zeros((sh, sw), np.float32)
    for bx, by, r, vx, vy in _leak[seed]:
        acc += np.exp(-((xx - (bx + vx * t)) ** 2 + (yy - (by + vy * t)) ** 2) / (2 * r * r))
    acc = acc / (acc.max() + 1e-6)
    acc = cv2.resize(acc, (W, H), interpolation=cv2.INTER_CUBIC)
    return np.dstack([acc * warm[2], acc * warm[1], acc * warm[0]])


def screen(a, b):
    return 1 - (1 - np.clip(a, 0, 1)) * (1 - np.clip(b, 0, 1))


_vig = {}


def vignette(img, strength=0.28):
    if strength not in _vig:
        yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
        d = np.sqrt(((xx - W / 2) / (W / 2)) ** 2 + ((yy - H / 2) / (H / 2)) ** 2) / math.sqrt(2)
        _vig[strength] = (1 - strength * np.clip(d, 0, 1) ** 2.4)[..., None].astype(np.float32)
    return img * _vig[strength]


_grng = np.random.default_rng(11)


def grain(img, amount=0.014, mono_grain=False):
    g = _grng.standard_normal((H // 2, W // 2)).astype(np.float32)
    g = cv2.resize(g, (W, H), interpolation=cv2.INTER_LINEAR)
    lum = img.mean(axis=2, keepdims=True)
    wgt = np.clip(4 * lum * (1 - lum), 0, 1)
    return img + amount * g[..., None] * (0.35 + 0.65 * wgt)


# ------------------------------------------------------------------ transitions

def transition(kind, a_img_fn, b_img_fn, u, t):
    """u in (0,1) across the transition. a_img_fn(extra_zoom, extra_pan) -> frame."""
    if kind == "dissolve":
        m = ease_io(u)
        return a_img_fn() * (1 - m) + b_img_fn() * m
    if kind == "dip":
        a, b = a_img_fn(), b_img_fn()
        if u < 0.5:
            return a * (1 - 0.85 * ease_io(u * 2))
        return b * (0.15 + 0.85 * ease_io((u - 0.5) * 2))
    if kind == "fadeblack":
        a, b = a_img_fn(), b_img_fn()
        return a * (1 - ease_io(min(1, u * 2))) + b * ease_io(max(0, u * 2 - 1))
    if kind == "zoomblur":
        za = 1 + 0.10 * ease_in(u)
        zb = 1 + 0.10 * (1 - ease_out(u))
        blur = 0.07 * math.sin(math.pi * u) ** 1.5
        a = radial_blur(a_img_fn(za), blur)
        b = radial_blur(b_img_fn(zb), blur)
        m = ease_io((u - 0.3) / 0.4)
        out = a * (1 - m) + b * m
        return out * (1 + 0.25 * math.sin(math.pi * u) ** 2)
    if kind == "whip":
        dx = W * 0.30
        a = dir_blur(a_img_fn(1.0, (dx * ease_in(u), 0)), 160 * SCALE * math.sin(math.pi * min(1, u * 1.4)))
        b = dir_blur(b_img_fn(1.0, (-dx * (1 - ease_out(u)), 0)), 160 * SCALE * math.sin(math.pi * max(0, u * 1.4 - 0.4)))
        m = ease_io((u - 0.35) / 0.3)
        return a * (1 - m) + b * m
    if kind == "whipv":
        dy = H * 0.18
        a = dir_blur(a_img_fn(1.0, (0, -dy * ease_in(u))), 200 * SCALE * math.sin(math.pi * min(1, u * 1.4)), vertical=True)
        b = dir_blur(b_img_fn(1.0, (0, dy * (1 - ease_out(u)))), 200 * SCALE * math.sin(math.pi * max(0, u * 1.4 - 0.4)), vertical=True)
        m = ease_io((u - 0.35) / 0.3)
        return a * (1 - m) + b * m
    if kind == "flash":
        a, b = a_img_fn(), b_img_fn()
        m = ease_io((u - 0.38) / 0.24)
        base = a * (1 - m) + b * m
        k = math.sin(math.pi * u) ** 1.2
        out = flash(base, 0.5 * k)
        return screen(out, light_leak(t, warm=(1.0, 0.48, 0.22)) * (0.6 * k))
    raise ValueError(kind)
