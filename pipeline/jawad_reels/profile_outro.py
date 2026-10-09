"""profile_outro.py - the @jawad_mp4 profile outro (Jawad's request 2026-10-09: "use the outro like the Genjutsu
reel and add the question there"), a drop-in replacement for endcard.EndCard.

The Genjutsu v2/v3 profile ending (pipeline/reel.py profile_ending) rebuilt in the house ember style, as a LAYER over
the dimmed moving world (the reels keep their seamless loop):
    1. the profile photo pops in as a circle with a flame ring and pulse rings (u 0.10-0.60),
    2. the circle travels left and the profile pill grows out of it: '@jawad_mp4' + sub line (u 0.75-1.30),
    3. the reel's question rises in under the pill (white grotesk, 1-3 lines, u 1.30+),
    4. an amber 'FOLLOW +' button pops (u 1.55) and keeps a soft pulse + sheen through the hold,
    5. everything fades in the last exit_dur s into the loop push (same as EndCard).

    import profile_outro as PO
    card = PO.ProfileOutro('Aap ke ghar light jaane pe kya hota tha?', dur=4.0)
    card.draw(cv, t, T_END)  /  card.post_kw(t, T_END, DUR)  /  card.cues(T_END, DUR)   (EndCard's interface)

Photo: brand_reels/assets/charsheet/jawad_profile_v.jpg (Jawad's upload V.png, 2026-10-09).
Self-test: python3 profile_outro.py selftest -> <WS>/out/selftest/profile_outro_*.png
"""
import functools
import math
import os
import sys

import cv2
import numpy as np

import jawad_kit
from jawad_kit import K, T, J
import endcard as E

W, H = K.W, K.H
REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))
PHOTO = os.path.join(REPO, 'brand_reels', 'assets', 'charsheet', 'jawad_profile_v.jpg')
CROP = (20, 90, 1120, 1190)                 # square around the head in the 1223 x 1407 upload
R_BIG, R_PILL = 190.0, 96.0
PILL_W, PILL_H = 860, 228
PILL_Y = 700.0
SUB = 'Video editor · Motion designer'


def _lin(c):
    return np.asarray(K.C[c], np.float32)[:3]


@functools.lru_cache(maxsize=1)
def _avatar():
    """Circular photo sprite, radius R_BIG (premultiplied linear)."""
    from PIL import Image
    im = Image.open(PHOTO).convert('RGB').crop(CROP)
    d = int(2 * R_BIG)
    a = np.asarray(im.resize((d, d), Image.LANCZOS))
    yy, xx = np.mgrid[0:d, 0:d].astype(np.float32)
    dist = np.sqrt((xx - d / 2 + 0.5) ** 2 + (yy - d / 2 + 0.5) ** 2)
    al = (np.clip(R_BIG - dist, 0, 1) * 255).astype(np.uint8)
    spr = K.sprite(np.dstack([a, al]))
    spr = np.ascontiguousarray(np.pad(spr, ((2, 2), (2, 2), (0, 0))))
    spr.flags.writeable = False
    return spr


@functools.lru_cache(maxsize=1)
def _ring():
    core = K.ring(R_BIG + 3, 5.0, _lin('AMBER') * 0.6 + _lin('FLAME') * 1.4)
    return K.glow(core, K.C['FLAME'], sigmas=(4, 12, 30), strength=1.1, weights=(1.0, 0.6, 0.35))


@functools.lru_cache(maxsize=1)
def _pulse():
    return K.ring(R_BIG, 3.0, _lin('FLAME') * 1.2, glow=4.0)


@functools.lru_cache(maxsize=64)
def _pill(w):
    """Pill body (dark glass + flame hairline) of width w and its soft glow, both (PILL_H + 2p, w + 2p)."""
    p = 60
    a = K.rrect_alpha(w, PILL_H, PILL_H / 2, p)
    inner = K.rrect_alpha(max(w - 5, 2), PILL_H - 5, (PILL_H - 5) / 2, p + 2)
    inner = cv2.resize(inner, (a.shape[1], a.shape[0])) if inner.shape != a.shape else inner
    stroke = np.clip(a - inner, 0, 1)
    body_a = a * 0.9
    rgb = body_a[..., None] * np.float32([0.030, 0.024, 0.021]) + stroke[..., None] * _lin('FLAME') * 0.85
    body = np.dstack([rgb, np.maximum(body_a, stroke)]).astype(np.float32)
    g = K.gblur(a, 22) * 0.45
    glow = np.dstack([g[..., None] * _lin('FLAME'), np.zeros_like(g)]).astype(np.float32)
    return body, glow


@functools.lru_cache(maxsize=1)
def _button():
    bw, bh = 340, 104
    p = 4
    a = K.rrect_alpha(bw, bh, bh / 2, p)
    yy = np.linspace(0, 1, a.shape[0], dtype=np.float32)[:, None, None]
    col = _lin('AMBER') * (1 - yy) * 1.15 + _lin('FLAME') * yy * 1.1
    spr = np.dstack([a[..., None] * col, a]).astype(np.float32)
    txt = T.render('FOLLOW  +', 'jw_caps_bold', px=40)
    tmp = spr.copy()
    txt.draw(tmp, tmp.shape[1] / 2, tmp.shape[0] / 2 + 1)
    glow = K.glow(np.dstack([a[..., None] * _lin('FLAME'), a]).astype(np.float32), K.C['FLAME'],
                  sigmas=(8, 22), strength=0.9, include=False)
    return tmp, glow, a


def _sheen(btn_a, ph):
    """Diagonal light sweep across the button (emissive, alpha 0), ph 0..1."""
    h, w = btn_a.shape
    xx = np.arange(w, dtype=np.float32)[None, :] + np.arange(h, dtype=np.float32)[:, None] * 0.5
    c = -0.2 * w + ph * 1.4 * w
    band = np.exp(-((xx - c) / 26.0) ** 2) * btn_a * 0.55
    return np.dstack([band[..., None] * np.float32([1.0, 0.9, 0.75]), np.zeros_like(band)]).astype(np.float32)


def _wrap(text, px, max_w, style='jw_body'):
    words, lines, cur = text.split(), [], ''
    for w_ in words:
        nxt = (cur + ' ' + w_).strip()
        if cur and T.measure(nxt, style, px=px)[0] > max_w:
            lines.append(cur)
            cur = w_
        else:
            cur = nxt
    if cur:
        lines.append(cur)
    return lines


@functools.lru_cache(maxsize=4)
def _scrim_mask(y0, y1):
    """Soft vertical band (1 inside y0..y1, gaussian shoulders) x a wide horizontal falloff, (H, W)."""
    yy = np.arange(H, dtype=np.float32)[:, None]
    xx = np.arange(W, dtype=np.float32)[None, :]
    band = np.clip(np.minimum((yy - y0) / 160.0 + 1, (y1 - yy) / 160.0 + 1), 0, 1)
    band = band * band * (3 - 2 * band)
    m = band * (0.55 + 0.45 * np.exp(-((xx - W / 2) / 520.0) ** 2))
    m = m.astype(np.float32)
    m.flags.writeable = False
    return m


@functools.lru_cache(maxsize=8)
def _scrim_factor(k, y0, y1):
    f = np.ones((H, W, 4), np.float32)
    f[..., :3] = (1.0 - _scrim_mask(y0, y1) * np.float32(k))[..., None]
    f.flags.writeable = False
    return f


class ProfileOutro:
    """Drop-in for endcard.EndCard: draw(cv, t, t0, opacity), post_kw, cues, boxes, settle, hold, dur."""

    def __init__(self, question, key=None, dur=4.0, sub=SUB, dim=0.74, exit_dur=0.36, y_q=None, q_px=66, key_px=124,
                 scrim=0.62, **_ignored):
        for txt in (question, key, sub):
            if txt and any(b in txt.lower() for b in E.BANNED):
                raise ValueError('outro copy may not say "watch full video": %r' % txt)
        self.question, self.dur, self.dim, self.exit_dur = question, float(dur), float(dim), float(exit_dur)
        px = float(q_px)
        lines = _wrap(question, px, 860)
        while len(lines) > 3 and px > 44:
            px -= 4
            lines = _wrap(question, px, 860)
        self.q_px, self.q_lines = px, [T.render(s, 'jw_body', px=px) for s in lines]
        self.lh = px * 1.28
        self.y_q = float(y_q) if y_q is not None else PILL_Y + PILL_H / 2 + 90 + self.lh * (len(lines) - 1) / 2 + 20
        y_end = self.y_q + self.lh * len(lines) / 2
        self.key = None
        if key:
            kp = float(key_px)
            while T.measure(key, 'jw_key_core', px=kp)[0] > 800 and kp > 70:
                kp -= 6
            self.key = T.render(key, 'jw_key_core', px=kp)
            self.key_halo = T.render(key, 'jw_key_halo', px=kp)
            self.y_key = y_end + 26 + self.key.h / 2
            y_end = self.y_key + self.key.h / 2
        self.y_btn = y_end + 135
        self.scrim = float(scrim)
        self.name = T.render(J.HANDLE, 'jw_caps_bold', px=54)
        self.sub_txt = T.render(sub, 'jw_handle', px=31) if sub else None
        self.sub = None                       # EndCard attribute some reels poke at (ignored)
        self.t_pop, self.t_move, self.t_q, self.t_btn = 0.10, 0.75, 1.30, 1.60
        self.settle = 2.0
        self.hold = (self.dur - self.exit_dur) - self.settle
        if self.hold < 1.5:
            raise ValueError('settled hold %.2f s < 1.5 s: make dur longer' % self.hold)

    # EndCard compatibility (prewarm hook)
    def _settled_layer(self):
        _avatar(), _ring(), _pulse(), _button()
        return None

    def boxes(self):
        out = {'pill': (K.CX - PILL_W / 2, PILL_Y - PILL_H / 2, K.CX + PILL_W / 2, PILL_Y + PILL_H / 2)}
        qw = max(s.w for s in self.q_lines)
        qh = self.lh * len(self.q_lines)
        out['question'] = (K.CX - qw / 2, self.y_q - qh / 2, K.CX + qw / 2, self.y_q + qh / 2)
        if self.key is not None:
            out['key'] = (K.CX - self.key.w / 2, self.y_key - self.key.h / 2, K.CX + self.key.w / 2, self.y_key + self.key.h / 2)
        out['button'] = (K.CX - 170, self.y_btn - 52, K.CX + 170, self.y_btn + 52)
        return out

    def draw(self, cv, t, t0, opacity=1.0):
        u = t - t0
        if u < 0:
            return cv
        t_last = t0 + self.dur - 1.0 / K.FPS
        ex = K.ramp(t, t0 + self.dur - self.exit_dur, t_last, 'in_cubic')
        k = K.ramp(u, 0.0, 0.5, 'inout_sine') * (1.0 - ex)
        if k > 0:
            cv *= E._dim_factor(round(float(self.dim * k) * 64) / 64)
            if self.scrim > 0:
                cv *= _scrim_factor(round(float(self.scrim * k) * 32) / 32, int(PILL_Y - 200), int(self.y_btn + 120))
        op = opacity * (1.0 - ex)
        if op <= 1e-3:
            return cv
        lift = 14.0 * ex
        # circle: pop, then travel to the pill's left end
        pp = K.ramp(u, self.t_pop, self.t_pop + 0.5, 'out_back') if u < self.t_pop + 0.5 else 1.0
        mv = K.ramp(u, self.t_move, self.t_move + 0.55, 'inout_cubic')
        r = K.lerp(R_BIG, R_PILL, mv) * pp
        bx = K.CX - PILL_W / 2 + 18 + R_PILL
        cx, cy = K.lerp(K.CX, bx, mv), PILL_Y - lift
        if mv > 0:
            left = cx - r - 18
            pw = int(round(K.lerp(2 * r + 36, PILL_W, mv) / 4) * 4)
            body, glow = _pill(max(pw, 8))
            K.draw(cv, glow, left - 60, cy - PILL_H / 2 - 60, anchor=(0, 0), opacity=0.9 * op * mv, mode='add')
            K.draw(cv, body, left - 60, cy - PILL_H / 2 - 60, anchor=(0, 0), opacity=op)
            tx = bx + R_PILL + 40
            tn = K.ramp(u, self.t_move + 0.30, self.t_move + 0.75, 'out_expo')
            if tn > 0:
                self.name.draw(cv, tx + (1 - tn) * 40, cy - 30, anchor=(0, 0.5), opacity=op * tn)
            if self.sub_txt is not None:
                ts = K.ramp(u, self.t_move + 0.45, self.t_move + 0.90, 'out_expo')
                if ts > 0:
                    self.sub_txt.draw(cv, tx + (1 - ts) * 40, cy + 38, anchor=(0, 0.5), opacity=op * ts)
        if r > 1:
            sc = r / R_BIG
            ra = K.ramp(u, self.t_pop + 0.1, self.t_pop + 0.6, 'inout_sine')
            if ra > 0:
                K.draw(cv, _ring(), cx, cy, scale=sc, opacity=op * ra, mode='add')
            if u > self.t_pop + 0.5:
                ph = ((u - self.t_pop - 0.5) * 0.7) % 1.0
                K.draw(cv, _pulse(), cx, cy, scale=sc * (1 + ph * 0.6), opacity=op * (1 - ph) * 0.6, mode='add')
            K.draw(cv, _avatar(), cx, cy, scale=sc, opacity=op)
        # question
        n = len(self.q_lines)
        for i, s in enumerate(self.q_lines):
            tq = self.t_q + 0.10 * i
            a = K.ramp(u, tq, tq + 0.45, 'inout_sine')
            if a <= 0:
                continue
            dy = 22 * (1 - K.ramp(u, tq, tq + 0.5, 'out_cubic'))
            y = self.y_q + (i - (n - 1) / 2) * self.lh + dy - lift
            s.draw(cv, K.CX, y, opacity=op * a)
        if self.key is not None:
            tk = self.t_q + 0.10 * n + 0.05
            a = K.ramp(u, tk, tk + 0.5, 'inout_sine')
            if a > 0:
                dy = 22 * (1 - K.ramp(u, tk, tk + 0.55, 'out_cubic'))
                self.key_halo.draw(cv, K.CX, self.y_key + dy - lift, opacity=op * a)
                self.key.draw(cv, K.CX, self.y_key + dy - lift, opacity=op * a)
        # follow button
        if u >= self.t_btn:
            fp = K.ramp(u, self.t_btn, self.t_btn + 0.4, 'out_back')
            btn, bglow, ba = _button()
            puls = 1.0 + 0.025 * math.sin((u - self.t_btn) * 5.0)
            y = self.y_btn - lift
            K.draw(cv, bglow, K.CX, y + 6, scale=fp, opacity=op * (0.55 + 0.2 * math.sin(u * 5.0)), mode='add')
            K.draw(cv, btn, K.CX, y, scale=fp * puls, opacity=op)
            ph = ((u - self.t_btn - 0.5) % 1.6) / 1.1
            if 0 < ph < 1 and u > self.t_btn + 0.5:
                K.draw(cv, _sheen(ba, ph), K.CX, y, scale=fp * puls, opacity=op, mode='add')
        return cv

    def post_kw(self, t, t0, dur_reel, gain=0.6):
        return {'push': E.loop_push(t, dur_reel, gain=gain)} if t >= t0 else {}

    def cues(self, t0, dur_reel):
        return [dict(t=round(t0 + self.t_pop, 4), name='swish_small', gain_db=-12, align='start', params={}),
                dict(t=round(t0 + self.t_move + 0.5, 4), name='glass_tap', gain_db=-12, params={}),
                dict(t=round(t0 + self.t_q + 0.2, 4), name='shimmer', gain_db=-10, params={}),
                dict(t=round(dur_reel, 4), name='reverse_swell', gain_db=-8, params={'duration': 0.8})]


def selftest():
    out = os.path.join(jawad_kit.WS if hasattr(jawad_kit, 'WS') else '/tmp', 'out', 'selftest')
    os.makedirs(out, exist_ok=True)
    c = ProfileOutro('Aap ke ghar light jaane pe kya hota tha? Chhat ya candle?')
    for u in (0.4, 1.0, 1.6, 2.6, 3.9):
        cv = K.background('ember', u) if hasattr(K, 'background') else np.zeros((H, W, 4), np.float32)
        c.draw(cv, u, 0.0)
        cv = K.post(cv, 'ember', u)
        img = K.to_srgb8(cv) if hasattr(K, 'to_srgb8') else (np.clip(cv[..., :3], 0, 1) ** (1 / 2.2) * 255).astype(np.uint8)
        cv2.imwrite(os.path.join(out, 'profile_outro_%.1f.png' % u), img[..., ::-1])
    print('ok', out, c.boxes())


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] in ('selftest', '--selftest'):
        selftest()
