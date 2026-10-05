"""Frame-accurate edit engine: ffmpeg decodes (and grades through a 3D LUT),
numpy/OpenCV reframes, transitions and finishes each output frame.

Output size defaults to 1440x1080 (4:3); REEL_SCALE=0.5 renders a quick preview.
"""
import math
import os
import subprocess

import cv2
import numpy as np

FPS_NUM, FPS_DEN = 24000, 1001
FPS = FPS_NUM / FPS_DEN
SCALE = float(os.environ.get("REEL_SCALE", "1"))
W, H = int(round(1440 * SCALE / 2) * 2), int(round(1080 * SCALE / 2) * 2)


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


class Shot:
    """A piece of picture.

    kind 'broll': vertical 2160x3840 S-Log3 clip graded by `lut`.
    kind 'th':    horizontal 3840x2160 graded interview (tv range).
    crop = (cx, cy, cw): centre and width (source px) of the 4:3 window at zoom 1.
    zoom = (z0, z1) push across the shot; pan in output px at zoom 1.
    """

    def __init__(self, src, t, dur, crop, kind="broll", lut=None, zoom=(1.0, 1.0),
                 pan=((0, 0), (0, 0)), ease=ease_io, speed=1.0, label="", gain=1.0,
                 flash_in=0, flash_out=0, sat=1.0):
        self.src, self.t, self.dur = src, t, dur
        self.crop, self.kind, self.lut = crop, kind, lut
        self.zoom, self.pan, self.ease = zoom, pan, ease
        self.speed, self.label, self.gain = speed, label, gain
        self.flash_in, self.flash_out, self.sat = flash_in, flash_out, sat
        self.n = F(dur)
        self.start = 0
        self.pre = 0
        self.post = 0
        self.reader = None
        self.src_size = (2160, 3840) if kind == "broll" else (3840, 2160)

    def open(self, skip=0):
        cx, cy, cw = self.crop
        sw, sh = self.src_size
        cw = min(cw, sw, sh * 4 / 3)
        ch = cw * 3 / 4
        cw_i, ch_i = int(round(cw / 2) * 2), int(round(ch / 2) * 2)
        x = int(round(min(max(cx - cw_i / 2, 0), sw - cw_i)))
        y = int(round(min(max(cy - ch_i / 2, 0), sh - ch_i)))
        # decode a little larger than output when the shot moves, to keep pushes sharp
        moving = max(self.zoom) > 1.001 or any(abs(v) > 0 for p in self.pan for v in p)
        k = min(1.35, max(self.zoom) * 1.04) if moving else 1.0
        k = max(1.0, min(k, cw_i / W))   # never decode above the source window size
        ow, oh = int(round(W * k / 2) * 2), int(round(H * k / 2) * 2)
        self.k, self.ow, self.oh = ow / W, ow, oh
        if self.kind == "broll":
            vf = (f"crop={cw_i}:{ch_i}:{x}:{y},"
                  f"scale={ow}:{oh}:flags=lanczos:in_color_matrix=bt709:in_range={getattr(self, 'rng', 'pc')}:out_range=pc,"
                  f"format=rgb48le,lut3d=file={self.lut}:interp=tetrahedral")
        else:
            vf = (f"crop={cw_i}:{ch_i}:{x}:{y},"
                  f"scale={ow}:{oh}:flags=lanczos:in_color_matrix=bt709:in_range=tv:out_range=pc,format=rgb48le")
        if self.speed != 1.0:
            vf = f"setpts=PTS/{self.speed},fps={FPS_NUM}/{FPS_DEN}," + vf
        self.vf = vf
        total = self.pre + self.n + self.post - skip
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
        s = z / self.k
        M = np.array([[s, 0, W / 2 - s * (self.ow / 2 + px * self.k)],
                      [0, s, H / 2 - s * (self.oh / 2 + py * self.k)]], np.float32)
        if abs(s - 1) < 1e-4 and abs(M[0, 2]) < 1e-3 and abs(M[1, 2]) < 1e-3 and img.shape[1] == W:
            out = img.copy()
        else:
            out = cv2.warpAffine(img, M, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
        if self.gain != 1.0:
            out *= self.gain
        if self.sat != 1.0:
            y = out.mean(axis=2, keepdims=True)
            out = y + (out - y) * self.sat
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


def flash(img, amount):
    """Overexposed, blooming flash frame (amount 0..1)."""
    g = 1 + 1.6 * amount
    out = img * g
    out = bloom(out, strength=0.7 * amount, sigma=22, thresh=0.55)
    return out + 0.06 * amount


def radial_blur(img, amount, n=7):
    if amount <= 2e-3:
        return img
    h, w = img.shape[:2]
    cx, cy = w / 2, h / 2
    acc = np.zeros_like(img)
    for j in range(n):
        s = 1 + amount * j / (n - 1)
        M = np.array([[s, 0, cx - s * cx], [0, s, cy - s * cy]], np.float32)
        acc += cv2.warpAffine(img, M, (w, h), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
    return acc / n


def dir_blur(img, length):
    length = int(length)
    if length < 2:
        return img
    return cv2.blur(img, (length, 1), borderType=cv2.BORDER_REFLECT)


_leak = {}


def light_leak(t, seed=3, warm=(1.0, 0.58, 0.28)):
    """Soft drifting amber light leak (BGR, 0..1)."""
    if seed not in _leak:
        rng = np.random.default_rng(seed)
        _leak[seed] = [(rng.uniform(-0.1, 1.1), rng.uniform(-0.1, 1.1), rng.uniform(0.22, 0.5),
                        rng.uniform(-0.6, 0.6), rng.uniform(-0.3, 0.3)) for _ in range(4)]
    sw, sh = 96, 72
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


_vig = None


def vignette(img, strength=0.28):
    global _vig
    if _vig is None:
        yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
        d = np.sqrt(((xx - W / 2) / (W / 2)) ** 2 + ((yy - H / 2) / (H / 2)) ** 2) / math.sqrt(2)
        _vig = (1 - strength * np.clip(d, 0, 1) ** 2.4)[..., None].astype(np.float32)
    return img * _vig


_grng = np.random.default_rng(11)


def grain(img, amount=0.014):
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
        dx = W * 0.22
        a = dir_blur(a_img_fn(1.0, (dx * ease_in(u), 0)), 140 * SCALE * math.sin(math.pi * min(1, u * 1.4)))
        b = dir_blur(b_img_fn(1.0, (-dx * (1 - ease_out(u)), 0)), 140 * SCALE * math.sin(math.pi * max(0, u * 1.4 - 0.4)))
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
