"""grp_base.py: shared footage plumbing for the Google Ranker Pro testimonial set (grp2_*.py modules).

Clip(cid, shots, look, ...) wraps a registered 24 fps clip (workspace3/frames/<cid>):
    shots      [(f0, f1, dict(c0, c1, z0, z1, look, ease))]: per-shot slow punch-in / drift (center, zoom)
    remap      [(t_out, src_offset)]: timeline cuts (output t >= t_out shows source t + src_offset)
    prep       optional fn(u8, fi) -> u8 for screen replacement / clean-up before the grade
.fi(t)         source frame for output time t (never crosses a cut inside one output frame)
.footage(fi)   graded, punched-in linear sprite;  .person(fi) the speaker cut out of it (RVM matte)
.plate(t, tr)  footage with branded transitions at the cuts (tr: {cut index: 'band' | 'grow' | 'cut'})
.person_over(cv, t, skip)  composite the speaker over graphics drawn behind them
"""
import functools
import math

import numpy as np

import core as K
import grp_brand as B
import grp_kit as G

W, H = K.W, K.H
FPS = 24.0


class Clip:
    def __init__(self, cid, n_src, shots, look, remap=(), prep=None, sharpen=0.25, person_shots=None):
        self.cid, self.n, self.shots, self.look = cid, n_src, shots, look
        self.remap = sorted(remap)
        self.prep = prep
        self.sharpen = sharpen
        self.person_shots = person_shots                    # shot indices that have person mattes in use
        # output-time cut points: (t_out, first frame of the new shot)
        self.cuts = []
        for k, (f0, f1, _) in enumerate(shots[1:], 1):
            to = self.out_time(f0 / FPS)
            if abs(self.src_t(to) - f0 / FPS) < 1e-6:            # skip shot starts removed by a remap cut
                self.cuts.append((to, f0))
        for t_out, off in self.remap:
            f = int(round((t_out + off) * FPS))
            self.cuts.append((t_out, f))
        self.cuts.sort()
        self._fc, self._pc, self._gc = {}, {}, {}

    # ------------------------------------------------------------------ time
    def src_t(self, t):
        off = 0.0
        for t_out, o in self.remap:
            if t >= t_out:
                off = o
        return t + off

    def out_time(self, ts):
        """Output time of source time ts (inverse of src_t for times that are shown)."""
        t = ts
        for t_out, o in self.remap:
            if ts - o >= t_out:
                t = ts - o
        return t

    def fi(self, t):
        fi = G.fidx(self.src_t(t), self.n)
        for tc, f0 in self.cuts:
            if t < tc and f0 <= fi < f0 + 3:
                fi = f0 - 1
            elif t >= tc and f0 - 3 <= fi < f0:
                fi = f0
        return int(min(max(fi, 0), self.n - 1))

    def shot(self, fi):
        for k, (f0, f1, _) in enumerate(self.shots):
            if f0 <= fi <= f1:
                return k
        return len(self.shots) - 1

    def tf(self, fi):
        k = self.shot(fi)
        f0, f1, p = self.shots[k]
        u = K.clamp((fi - f0) / max(f1 - f0, 1))
        e = K.EASE[p.get('ease', 'inout_sine')](u)
        c0, c1 = p.get('c0', (0.5, 0.5)), p.get('c1', p.get('c0', (0.5, 0.5)))
        z0, z1 = p.get('z0', 1.0), p.get('z1', p.get('z0', 1.0))
        return (K.lerp(c0[0], c1[0], e), K.lerp(c0[1], c1[1], e)), K.lerp(z0, z1, e)

    # ------------------------------------------------------------------ pixels
    def frame(self, fi):
        if fi in self._gc:
            return self._gc[fi]
        fr = G.frame_u8(self.cid, fi)
        if self.prep is not None:
            fr = self.prep(fr, fi)
        if len(self._gc) > 3:
            self._gc.pop(next(iter(self._gc)))
        self._gc[fi] = fr
        return fr

    def footage(self, fi):
        if fi in self._fc:
            return self._fc[fi]
        c, z = self.tf(fi)
        look = self.shots[self.shot(fi)][2].get('look', self.look)
        spr = G.shot_sprite(self.frame(fi), look, c, z, sharpen=self.sharpen)
        spr.setflags(write=False)
        if len(self._fc) > 3:
            self._fc.pop(next(iter(self._fc)))
        self._fc[fi] = spr
        return spr

    def person(self, fi):
        if fi in self._pc:
            return self._pc[fi]
        c, z = self.tf(fi)
        p = G.person_sprite(self.footage(fi), self.cid, fi, c, z)
        if len(self._pc) > 2:
            self._pc.pop(next(iter(self._pc)))
        self._pc[fi] = p
        return p

    def near_cut(self, t, before=0.17, after=0.32):
        return any(tc - before <= t < tc + after for tc, _ in self.cuts)

    def person_over(self, cv, t, skip=()):
        """Speaker over the graphics behind them (skipped around transitions and in `skip` windows)."""
        if self.near_cut(t) or any(a <= t < b for a, b in skip):
            return
        fi = self.fi(t)
        if self.person_shots is not None and self.shot(fi) not in self.person_shots:
            return
        p = self.person(fi)
        if p is not None:
            K.over(cv, p)

    # ------------------------------------------------------------------ plate + transitions
    def plate(self, t, transitions=None, t_end=None, end_t0=None):
        transitions = transitions or {}
        fi = self.fi(t)
        cv = self.footage(fi).copy()
        tq = round(t * FPS) / FPS
        for k, (tc, f0) in enumerate(self.cuts):
            kind = transitions.get(k, 'band')
            if kind == 'band' and tc - 0.15 <= t < tc + 0.15:
                u = K.ramp(tq, tc - 0.15, tc + 0.15, 'inout_cubic')
                new_first = t < tc
                other = self.footage(f0 if new_first else self.fi(tc - 0.05))
                B.band_wipe(cv, other, u, new_first)
            elif kind == 'grow' and tc - 0.12 <= t < tc + 0.30:
                u = K.EASE['inout_cubic'](K.ramp(tq, tc - 0.12, tc + 0.30, 'linear'))
                m = G.rrect_grow(W, H, u, 40 * (1 - u) + 2, 0.5, K.lerp(0.40, 0.5, u), 240, 240)[..., None]
                if t < tc:
                    cv[:] = cv * (1 - m) + self.footage(f0) * m
                else:
                    cv[:] = self.footage(self.fi(tc - 0.05)) * (1 - m) + cv * m
        if end_t0 is not None and t >= end_t0:
            cv = B.end_backdrop(cv, t, end_t0)
        return cv


def intro_reveal(cv, t, dur=0.78, cy0=0.42):
    """0..dur: the footage opens out of a rounded square on the brand plate."""
    if t >= dur:
        return
    u = K.EASE['inout_quart'](K.ramp(round(t * FPS) / FPS, 0.0, dur - 0.02, 'linear'))
    m = G.rrect_grow(W, H, u, 150 * (1 - u) + 1, 0.5, K.lerp(cy0, 0.5, u), 300, 300)
    cv[:] = B.backdrop() * (1 - m[..., None]) + cv * m[..., None]


def post(cv, t):
    cv = np.ascontiguousarray(cv, dtype=np.float32)
    K.vignette(cv, 0.12, 0.8, 1.8)
    K.grain(cv, t, 0.009, 1.2)
    cv[..., 3] = 1.0
    return cv


def white_card(w, h, r=30, accent=None):
    return B.card(w, h, r, accent=accent)


@functools.lru_cache(maxsize=32)
def site_card(path, crop, width, url, max_h=None):
    return G.browser_card(path, crop, width, url, r=26, bar=58, url_font='Inter-Medium', max_h=max_h)


def card_in(cv, crd, t, t0, t1, cx, cy, rise=40, wipe_angle=-90, scale0=0.9, fout=0.3, drift=(0, 0)):
    """Draw a Card with a spring-in + wipe reveal and an eased exit."""
    if not (t0 <= t < t1):
        return
    u = K.spring(t - t0, 2.3, 0.62)
    out = K.ramp(t, t1 - fout, t1, 'in_cubic')
    wu = K.ramp(t, t0, t0 + 0.45, 'out_cubic')
    m = G.wipe(crd.w, crd.h, wu, angle=wipe_angle, soft=0.1) if wu < 1 else None
    dx = drift[0] * K.clamp((t - t0) / max(t1 - t0, 1e-3))
    dy = drift[1] * K.clamp((t - t0) / max(t1 - t0, 1e-3))
    crd.draw(cv, cx + dx, cy + rise * (1 - u) - 30 * out + dy, scale=(scale0 + (1 - scale0) * u) * (1 - 0.06 * out),
             opacity=min(1, (t - t0) / 0.12) * (1 - out), mask=m)


# ---------------------------------------------------------------------------------------------- screens
def warp_into(content, quad, size=(W, H), pre_w=None, flags=None):
    """Warp an sRGB float image (h, w, 3) into a frame-space quad [[tl], [tr], [br], [bl]].
    Returns (warped (bh, bw, 3), mask (bh, bw), (x0, y0)) cropped to the quad's bounding box."""
    import cv2
    q = np.float32(quad)
    x0 = int(max(0, np.floor(q[:, 0].min()) - 3))
    y0 = int(max(0, np.floor(q[:, 1].min()) - 3))
    x1 = int(min(size[0], np.ceil(q[:, 0].max()) + 4))
    y1 = int(min(size[1], np.ceil(q[:, 1].max()) + 4))
    if x1 <= x0 or y1 <= y0:
        return None, None, (0, 0)
    h, w = content.shape[:2]
    tw = pre_w or int(max(np.linalg.norm(q[1] - q[0]), np.linalg.norm(q[2] - q[3])))
    if tw < w:
        th = max(2, int(round(h * tw / w)))
        content = cv2.resize(content, (tw, th), interpolation=cv2.INTER_AREA)
        h, w = th, tw
    src = np.float32([[0, 0], [w, 0], [w, h], [0, h]])
    Hm = cv2.getPerspectiveTransform(src, q - np.float32([x0, y0]))
    warped = cv2.warpPerspective(content, Hm, (x1 - x0, y1 - y0), flags=flags or cv2.INTER_LINEAR,
                                 borderMode=cv2.BORDER_REPLICATE)
    mask = cv2.warpPerspective(np.ones((h, w), np.float32), Hm, (x1 - x0, y1 - y0), flags=cv2.INTER_LINEAR)
    return warped, mask, (x0, y0)


def green_replace(fr, quad, content, k_lo=12.0, k_hi=58.0, black=14.0, white=238.0, blur=0.9, shade=True,
                  region=None, defocus=0.0, extra_alpha=None):
    """Chroma-key a green screen inside `quad` of RGB uint8 frame `fr` and put `content` (sRGB float, any size)
    there, keeping anything in front (hair, hands) and despilling its edges. region: optional (H, W) bool limit.
    extra_alpha: optional (bh, bw) float, 1 = force screen (e.g. drawn lines / fake text to drop)."""
    import cv2
    warped, qm, (x0, y0) = warp_into(content, quad)
    if warped is None:
        return fr
    bh, bw = qm.shape
    out = fr.astype(np.float32)
    sub = out[y0:y0 + bh, x0:x0 + bw]
    r, g, b = sub[..., 0], sub[..., 1], sub[..., 2]
    gs = np.clip((g - np.maximum(r, b) - k_lo) / (k_hi - k_lo), 0, 1)
    if extra_alpha is not None:
        gs = np.maximum(gs, extra_alpha)
    k = gs * qm
    if region is not None:
        k = k * region[y0:y0 + bh, x0:x0 + bw]
    if blur > 0:
        warped = cv2.GaussianBlur(warped, (0, 0), blur)
    if defocus > 0:
        warped = cv2.GaussianBlur(warped, (0, 0), defocus)
    warped = black + warped * (white - black) / 255.0
    if shade:
        wsum = cv2.GaussianBlur(gs, (0, 0), 25) + 1e-3
        gl = cv2.GaussianBlur(g * gs, (0, 0), 25) / wsum
        ref = np.median(g[gs > 0.9]) if (gs > 0.9).sum() > 200 else max(gl.max(), 1)
        s = np.clip(gl / max(ref, 1), 0.82, 1.08)
        warped = warped * s[..., None]
    fg = sub.copy()
    fg[..., 1] = np.minimum(g, np.maximum(r, b) + 3)                       # despill
    km = k[..., None]
    out[y0:y0 + bh, x0:x0 + bw] = fg * (1 - km) + warped * km
    return np.clip(out + 0.5, 0, 255).astype(np.uint8)


def paste_quad(fr, quad, content, feather=1.0, gain=1.0, blur=0.6, opacity=1.0):
    """Put content (sRGB float) into a quad (opaque display, e.g. a phone screen) with a feathered edge."""
    import cv2
    warped, qm, (x0, y0) = warp_into(content, quad)
    if warped is None:
        return fr
    if blur > 0:
        warped = cv2.GaussianBlur(warped, (0, 0), blur)
    if feather > 0:
        qm = cv2.GaussianBlur(qm, (0, 0), feather)
    bh, bw = qm.shape
    out = fr.astype(np.float32)
    km = (qm * opacity)[..., None]
    out[y0:y0 + bh, x0:x0 + bw] = out[y0:y0 + bh, x0:x0 + bw] * (1 - km) + warped * gain * km
    return np.clip(out + 0.5, 0, 255).astype(np.uint8)
