"""endcard.py - the @jawad_mp4 minimal end card (4.5-5 s) and the seamless-loop helpers that hand the reel's
last frame back to frame 0.

The card is a LAYER over the moving world (never a black slate, never a glass card): the world keeps moving
underneath, dimmed multiplicatively (blacks are never lifted), while the house lockup builds and holds:
    optional JD monogram (thin flame ring that draws on with a hot comet head + serif-italic 'JD' rising inside),
    white Poppins caps line + glowing Instrument Serif Italic keyword + glowing underline (J.HouseTitle),
    optional sub line (jw_body), '@jawad_mp4' signature (J.signature) at y ~1575.
No third-party logos, no 'watch full video' (refused). One verb-first CTA of <= 5 words that is TRUE, e.g.
caps='COMMENT MEIN', key='batao'. The type settles by ~1.7 s and holds >= 1.5 s, then exits in the last 0.36 s
into an exposure push that bridges the loop.

    import jawad_kit
    import endcard as E
    card = E.EndCard('COMMENT MEIN', 'batao', monogram='JD', dur=4.8)       # build once (lru_cache / prewarm)
    T_END = DUR - card.dur
    def draw(t):
        cv = E.loop_world(world, t, DUR, d=0.6)        # last 0.6 s crossfade into world(t - DUR) = frame 0's past
        card.draw(cv, t, T_END)
        return cv
    def post(cv, t): return X.finish(cv, t, LOOK, cuts=[(0.0, 0.6)], **card.post_kw(t, T_END, DUR))
    def cues(): return [...] + card.cues(T_END, DUR)

LOOP HELPERS (hooks_retention_captions.md 3.3: visual match + audio loop, never a fade to black or silence)
    loop_world(scene, t, dur, d=0.6, ease='inout_sine') -> canvas: over the last d s the world crossfades into
        scene(t - dur), so frame N-1 is one frame before frame 0 (scenes are pure, negative t is fine).
    loop_value(f, t, dur, d=1.0, ease='inout_sine') the same on parameters (camera tracks, positions: no ghosting).
    loop_push(t, dur, frames=3, gain=0.6) exposure push rising into the last frame (pair with cuts=[(0, gain)]).
    seam_report(render, dur) -> dict(seam, step, ok): mean |8-bit| difference last->first frame vs a normal
        frame step (render(t) -> uint8 RGB, e.g. lambda t: render.render_still(mod, t, 1)).
COST: ~15-60 ms per frame while building, ~8-20 ms settled (+ the world dim ~10 ms).
Self-test: python3 endcard.py selftest (or --selftest) -> <WS>/out/selftest/endcard_*.png; exits 1 on failure.
"""
import functools
import math
import os
import sys
import time

import cv2
import numpy as np

import jawad_kit
from jawad_kit import K, T, J

W, H = K.W, K.H
BANNED = ('watch full video', 'full video', 'watch the full', 'link in bio for the full')


# =============================================================================================== monogram
@functools.lru_cache(maxsize=4)
def _ring(r=112, width=4.0):
    """Thin flame ring (emissive core + glow) and its angle map (0 at 12 o'clock, clockwise, 0..1)."""
    core = K.ring(r, width, np.float32(K.C['AMBER']) * 0.6 + np.float32(K.C['FLAME']) * 1.4)
    spr = K.glow(core, K.C['FLAME'], sigmas=(4, 12, 30), strength=1.15, weights=(1.0, 0.6, 0.35))
    spr2 = K.glow(np.ascontiguousarray(core), K.C['RED'], sigmas=(46,), strength=0.35, include=False)
    d = (spr2.shape[0] - spr.shape[0]) // 2
    spr2[d:d + spr.shape[0], d:d + spr.shape[1], :3] += spr[..., :3]
    spr2[d:d + spr.shape[0], d:d + spr.shape[1], 3] = np.maximum(spr2[d:d + spr.shape[0], d:d + spr.shape[1], 3],
                                                                  spr[..., 3])
    n = spr2.shape[0]
    yy, xx = np.mgrid[0:n, 0:n].astype(np.float32) - (n - 1) / 2
    ang = (np.degrees(np.arctan2(xx, -yy)) % 360.0) / 360.0
    spr2.flags.writeable = False
    ang.flags.writeable = False
    return spr2, ang


@functools.lru_cache(maxsize=2)
def _head():
    d = K.disc(4.0, K.C['WHITE'] * 1.8)
    return K.glow(d, K.C['AMBER'] * 1.2, sigmas=(4, 12, 30), strength=1.3, weights=(1.0, 0.6, 0.35))


class Monogram:
    """'JD' monogram: thin flame ring (draws on clockwise from 12 o'clock with a comet head) + serif-italic JD."""

    def __init__(self, text='JD', r=112, px=126):
        self.text, self.r, self.px = text, r, px
        self.ring, self.ang = _ring(r)
        self.glyphs = T.Glyphs(text, 'jw_key_core', px=px)
        self.static = T.render(text, 'jw_key_core', px=px)
        self.halo = T.render(text, 'jw_key_halo', px=px)

    def draw(self, cv, t, x, y, t0=0.0, opacity=1.0, ring_dur=0.65):
        if t < t0 or opacity <= 0:
            return
        u = K.ramp(t, t0, t0 + ring_dur, 'inout_cubic')
        if u >= 1:
            K.draw(cv, self.ring, x, y, opacity=opacity)
        elif u > 0:
            m = np.clip((u - self.ang) * 40.0 + 0.5, 0, 1)                 # soft draw-on edge
            spr = self.ring * m[..., None]
            K.draw(cv, spr, x, y, opacity=opacity)
            a = math.radians(u * 360.0)
            K.draw(cv, _head(), x + self.r * math.sin(a), y - self.r * math.cos(a), opacity=opacity, mode='add')
        tk = t0 + 0.25
        if t >= tk:
            cy = y - self.static.h * 0.10                    # optical centre (the J descends)
            self.halo.draw(cv, x, cy, opacity=opacity * K.ramp(t, tk, tk + 0.6, 'inout_sine'))
            if t - tk < 1.0:
                self.glyphs.rise(cv, t, x, cy, t0=tk, stagger=0.06, dur=0.55, dist=0.25, blur=6, scale0=0.94,
                                 opacity=opacity)
            else:
                self.static.draw(cv, x, cy, opacity=opacity)


# =============================================================================================== end card
class EndCard:
    """The @jawad_mp4 end card (see module docstring). Static parts are built in __init__ (cache the card)."""

    def __init__(self, caps='COMMENT MEIN', key='batao', sub=None, handle=True, monogram='JD', dur=4.8,
                 y_key=930.0, y_mono=560.0, y_sub=1165.0, y_sig=1575.0, dim=0.58, caps_px=86, key_px=200,
                 exit_dur=0.36):
        for txt in (caps, key, sub):
            if txt and any(b in txt.lower() for b in BANNED):
                raise ValueError('end card copy may not say "watch full video" (Jawad removed it): %r' % txt)
        if not (4.0 <= dur <= 6.0):
            raise ValueError('end card should run 4.5-5 s (got %.2f)' % dur)
        self.dur, self.dim, self.exit_dur = float(dur), float(dim), float(exit_dur)
        self.y_key, self.y_mono, self.y_sub, self.y_sig = y_key, y_mono, y_sub, y_sig
        self.title = J.HouseTitle(caps, key, caps_px=caps_px, key_px=key_px)
        self.mono = Monogram(monogram) if monogram else None
        if sub:
            spx = 56.0
            sw = T.measure(sub, 'jw_body', px=spx)[0]
            if sw > 760:                                        # lower band: <= 780 px, right edge <= x 930
                spx *= 760.0 / sw
            self.sub = T.render(sub, 'jw_body', px=spx)
        else:
            self.sub = None
        self.handle = handle
        self.t_title = 0.35 if self.mono else 0.15
        self.settle = self.t_title + 1.5                       # keyword rise + underline done (HouseTitle)
        if self.mono:
            self.settle = max(self.settle, 0.25 + 1.0)
        self.hold = (self.dur - self.exit_dur) - self.settle
        if self.hold < 1.5:
            raise ValueError('settled hold %.2f s < 1.5 s: make dur longer' % self.hold)

    def boxes(self):
        """Approximate ink boxes of every element (for safe-zone QA)."""
        ht = self.title
        out = {'keyword': (K.CX - ht.kw / 2, self.y_key - ht.kh / 2, K.CX + ht.kw / 2, self.y_key + ht.kh / 2 + ht.key_px * 0.4)}
        if ht.caps is not None:
            cy = self.y_key - ht.kh / 2 - ht.gap - ht.caps.h / 2
            out['caps'] = (K.CX - ht.caps.w / 2, cy - ht.caps.h / 2, K.CX + ht.caps.w / 2, cy + ht.caps.h / 2)
        if self.mono:
            r = self.mono.r + 8
            out['monogram'] = (K.CX - r, self.y_mono - r, K.CX + r, self.y_mono + r)
        if self.sub:
            out['sub'] = (K.CX - self.sub.w / 2, self.y_sub - self.sub.h / 2, K.CX + self.sub.w / 2, self.y_sub + self.sub.h / 2)
        if self.handle:
            sw, sh = T.measure(J.HANDLE, 'jw_handle', px=34)
            out['signature'] = (K.CX - sw / 2, self.y_sig - sh / 2, K.CX + sw / 2, self.y_sig + sh / 2)
        return out

    def _dim(self, cv, k):
        """Multiplicative dim of the world under the type (stronger behind the lockup), never lifts blacks."""
        if k <= 0:
            return
        cv *= _dim_factor(round(float(self.dim * k) * 64) / 64)

    def _settled_layer(self):
        """The whole settled type layer as one bbox sprite (built once): (x0, y0, sprite)."""
        if getattr(self, '_settled', None) is None:
            tmp = np.zeros((H, W, 4), np.float32)
            self._draw_type(tmp, self.settle + 0.2, 0.0, 1.0, settled=False)
            nz = np.abs(tmp).max(2) > 1e-5
            rows, cols = np.nonzero(nz.any(1))[0], np.nonzero(nz.any(0))[0]
            y0, y1, x0, x1 = rows[0], rows[-1] + 1, cols[0], cols[-1] + 1
            spr = np.ascontiguousarray(tmp[y0:y1, x0:x1])
            spr.flags.writeable = False
            self._settled = (int(x0), int(y0), spr)
        return self._settled

    def draw(self, cv, t, t0, opacity=1.0):
        """Draw the card at reel time t; the card starts at t0 (= DUR - dur). Pure function of t."""
        u = t - t0
        if u < 0:
            return cv
        t_last = t0 + self.dur - 1.0 / K.FPS                    # the reel's last frame: type fully gone
        out_t0 = t_last - 0.35                                  # HouseTitle's exit runs 0.35 s
        ex = K.ramp(t, t0 + self.dur - self.exit_dur, t_last, 'in_cubic')
        self._dim(cv, K.ramp(u, 0.0, 0.5, 'inout_sine') * (1.0 - ex))
        if self.settle <= u < self.dur - self.exit_dur and opacity >= 1.0:
            x0, y0, spr = self._settled_layer()                  # static during the hold: one cached sprite
            K.draw(cv, spr, x0, y0, anchor=(0, 0))
            return cv
        self._draw_type(cv, t, t0, opacity, ex=ex, out_t0=out_t0)
        return cv

    def _draw_type(self, cv, t, t0, opacity, settled=False, ex=0.0, out_t0=None):
        op = opacity * (1.0 - ex)
        if self.mono:
            self.mono.draw(cv, t, K.CX, self.y_mono - 18 * ex, t0=t0 + 0.1, opacity=op)
        self.title.draw(cv, t, K.CX, self.y_key, t0=t0 + self.t_title, out_t0=out_t0, opacity=opacity)
        if self.sub:
            ts = t0 + self.t_title + 0.8
            self.sub.draw(cv, K.CX, self.y_sub + 16 * (1 - K.ramp(t, ts, ts + 0.5, 'out_cubic')),
                          opacity=op * K.ramp(t, ts, ts + 0.45, 'inout_sine'))
        if self.handle:
            J.signature(cv, K.CX, self.y_sig, opacity=op * K.ramp(t, t0 + 1.0, t0 + 1.45, 'inout_sine'))

    def post_kw(self, t, t0, dur_reel, gain=0.6):
        """finish() overrides: the exposure push rising into the last frame (frame 0 carries cuts=[(0, gain)])."""
        return {'push': loop_push(t, dur_reel, gain=gain)} if t >= t0 else {}

    def cues(self, t0, dur_reel):
        """Quiet SFX for the card (audio.py names) + the loop swell ending exactly on DUR (= frame 0's hit;
        put dict(t=0.0, name='impact_soft', gain_db=-6) at the head of the reel's cue sheet)."""
        out = []
        if self.mono:
            out += [dict(t=round(t0 + 0.1, 4), name='swish_small', gain_db=-12, align='start', params={}),
                    dict(t=round(t0 + 0.75, 4), name='glass_tap', gain_db=-12, params={})]
        out += [dict(t=round(t0 + self.t_title + 0.22, 4), name='shimmer', gain_db=-10, params={}),
                dict(t=round(dur_reel, 4), name='reverse_swell', gain_db=-8, params={'duration': 0.8})]
        return out


@functools.lru_cache(maxsize=2)
def _dim_factor(k):
    """(H, W, 4) multiplier 1 - k * mask on rgb, 1 on alpha (read-only, cached per quantised k)."""
    f = np.ones((H, W, 4), np.float32)
    f[..., :3] = (1.0 - _dim_mask() * np.float32(k))[..., None]
    f.flags.writeable = False
    return f


@functools.lru_cache(maxsize=1)
def _dim_mask():
    """Full-res dim weight: 0.75 at the edges, 1.0 in a soft band behind the lockup (read-only)."""
    yy, xx = np.mgrid[0:H // 8, 0:W // 8].astype(np.float32) * 8
    band = np.exp(-((yy - 900.0) / 520.0) ** 2)
    m = 0.75 + 0.25 * band
    m = cv2.resize(m, (W, H), interpolation=cv2.INTER_CUBIC).astype(np.float32)
    m.flags.writeable = False
    return m


# =============================================================================================== loop helpers
def loop_world(scene, t, dur, d=0.6, ease='inout_sine'):
    """Seamless loop of a pure scene: over the last d s, crossfade scene(t) into scene(t - dur), so the last
    frame is one frame before frame 0.  cv = E.loop_world(world, t, DUR)"""
    t_a = dur - d
    if t < t_a:
        return scene(t)
    w = float(K.get_ease(ease)(K.clamp((t - t_a) / d)))
    a = scene(t)
    if w <= 0:
        return a
    b = scene(t - dur)
    a += (b - a) * np.float32(w)
    return a


def loop_value(f, t, dur, d=1.0, ease='inout_sine'):
    """loop_world for parameters: f(t) blended into f(t - dur) over the last d s (camera poses, positions)."""
    t_a = dur - d
    v = f(t)
    if t < t_a:
        return v
    w = float(K.get_ease(ease)(K.clamp((t - t_a) / d)))
    vb = f(t - dur)
    return K.lerp(v, vb, w) if np.ndim(v) == 0 else np.asarray(v) * (1 - w) + np.asarray(vb) * w


def loop_push(t, dur, frames=3, gain=0.6):
    """Exposure push rising (in_cubic) over the last `frames` frames into the wrap."""
    return gain * K.ramp(t, dur - frames / K.FPS, dur - 1.0 / K.FPS, 'in_cubic')


def seam_report(render, dur, fps=K.FPS):
    """Seam QA: mean |difference| (8-bit) last frame -> frame 0 vs frame 0 -> frame 1 (a normal step).
    ok when the seam is within 1.5 x the normal step + 2 levels."""
    last = render(dur - 1.0 / fps).astype(np.int16)
    f0 = render(0.0).astype(np.int16)
    f1 = render(1.0 / fps).astype(np.int16)
    seam = float(np.abs(last - f0).mean())
    step = float(np.abs(f1 - f0).mean())
    return dict(seam=round(seam, 3), step=round(step, 3), ok=seam <= 1.5 * step + 2.0)


# =============================================================================================== selftest
def selftest():
    """Renders the card over a moving ember world with a seamless loop, checks hold / exit / safe zones /
    banned copy / purity / the seam, writes <WS>/out/selftest/endcard_*.png."""
    os.makedirs(K.SELFTEST, exist_ok=True)
    fails = []
    DUR = 6.0
    card = EndCard('COMMENT MEIN', 'batao', sub='kaunsa edit sabse mushkil tha?', monogram='JD', dur=4.8)
    t0c = DUR - card.dur
    sparks = J.embers(90, seed=7)

    def world(t):
        cam = K.Cam.orbit((0, 0, 0), 1500, yaw=3.0 * math.sin(t * 0.7), pitch=1.0, aperture=30)
        cv = K.background('ember', t, cam)
        sparks.draw(cv, cam, t)
        return cv

    def draw(t):
        cv = loop_world(world, t, DUR, 0.6)
        card.draw(cv, t, t0c)
        return cv

    def render(t):
        cv = draw(t)
        pk = card.post_kw(t, t0c, DUR)
        p = pk.get('push', 0.0) + 0.6 * K.impulse(t, -0.02, 16.0)
        b = K.LOOKS['ember']['bloom']
        K.post(cv, 'ember', t, exposure=1.4 * p, bloom=b * (1 + 0.9 * p))
        return K.to_srgb8(cv, t)

    # banned copy
    try:
        EndCard('WATCH FULL VIDEO', 'link')
        fails.append('banned copy accepted')
    except ValueError:
        pass
    # safe zones
    for name, (x0, y0, x1, y1) in card.boxes().items():
        if x0 < 70 or x1 > 1010 or y0 < 230 or y1 > 1620 or (x1 > 930 and y1 > 1050 and y0 < 1700 and name != 'signature'):
            fails.append('%s outside the safe zone %s' % (name, (x0, y0, x1, y1)))
        if name != 'signature' and y1 > 1480:
            fails.append('%s below y 1480' % name)
    # settled hold: the type layer is identical over the hold
    blank = lambda: np.zeros((H, W, 4), np.float32)
    a, b = blank(), blank()
    card.draw(a, t0c + card.settle + 0.05, t0c)
    card.draw(b, t0c + card.dur - card.exit_dur - 0.02, t0c)
    if float(np.abs(a - b).max()) > 1e-4:
        fails.append('type moves during the hold (%.4f)' % float(np.abs(a - b).max()))
    if card.hold < 1.5:
        fails.append('hold %.2f < 1.5 s' % card.hold)
    # exit: nothing of the type left on the last frame except the dim
    c = blank()
    card.draw(c, DUR - 1 / K.FPS, t0c)
    if float(c[..., 3].max()) > 0.35:
        fails.append('type still on the last frame (alpha %.2f)' % float(c[..., 3].max()))
    # purity
    d1, d2 = draw(t0c + 1.0), draw(t0c + 1.0)
    if not np.array_equal(d1, d2):
        fails.append('impure draw')
    # cost
    world(t0c + 0.6)
    tms = []
    for u in (0.3, 0.6, 1.0, 2.5):
        cv = world(t0c + u)
        t1 = time.perf_counter()
        card.draw(cv, t0c + u, t0c)
        tms.append((time.perf_counter() - t1) * 1e3)
    # seam
    sr = seam_report(render, DUR)
    if not sr['ok']:
        fails.append('loop seam %s' % sr)
    # sheet
    times = [t0c + x for x in (0.15, 0.45, 0.8, 1.3, 2.4, card.dur - 0.15, card.dur - 1 / K.FPS)] + [0.0]
    ims = []
    for tt in times:
        u8 = render(tt)
        cv2.putText(u8, 't=%.2f%s' % (tt, ' (frame 0)' if tt == 0 else ''), (40, 120), cv2.FONT_HERSHEY_SIMPLEX, 1.6,
                    (120, 220, 255), 3)
        for (x0, y0, x1, y1) in [(70, 230, 1010, 1480)]:
            cv2.rectangle(u8, (x0, y0), (x1, y1), (60, 90, 60), 2)
        ims.append(cv2.resize(u8, (360, 640), interpolation=cv2.INTER_AREA))
    p = os.path.join(K.SELFTEST, 'endcard_sheet.png')
    cv2.imwrite(p, np.hstack(ims)[..., ::-1])
    p2 = os.path.join(K.SELFTEST, 'endcard_hold.png')
    cv2.imwrite(p2, render(t0c + 2.4)[..., ::-1])
    print('card: dur %.2f s, settled at +%.2f s, hold %.2f s, exit %.2f s' % (card.dur, card.settle, card.hold,
                                                                         card.exit_dur))
    print('draw cost ms (+0.3 / +0.6 / +1.0 / +2.5 s):', [round(x, 1) for x in tms])
    print('loop seam:', sr)
    print('->', p)
    print('->', p2)
    if fails:
        print('FAIL:', *fails, sep='\n  ')
        return False
    print('endcard selftest OK')
    return True


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] in ('selftest', '--selftest'):
        sys.exit(0 if selftest() else 1)
    print(__doc__)
