"""BMHC "Tuned In" (Heritage Radio 90.6 FM), 9:16, ~32 s. ElevenLabs voice (Payyal Modi, a British community-radio presenter).

Hook: dawn footsteps towards the Centre while the golden tuning strip searches through static; the needle finds 90.6
and the voice comes in. The signal leaves the studio as golden rings, lights up a living map of Manchester, and is
followed through one day (kitchen radio, morning tea, rainy commute, a walk, the bus, the shop, a podcast) until the
rings flow back to the Centre at dusk. End card: 90.6 FM, DAB+, app. Every cue word pops a 3D object.

Usage: python3 reel_tuned.py still 1.0,5.0 | python3 reel_tuned.py range 0 100 | python3 reel_tuned.py times
"""
import os, sys, math, json, functools
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import numpy as np
import cv2
import frames_tuned as G
from frames_tuned import (FB, R, W, H, draw, blur_sprite, tint, rrect, ts, solid, paste_spr, _wmask, GREEN_D, IVORY, TEAL, GOLD, MAG,
                          ORANGE, GREEN, PB, PX, PS, PM, WHITE, LGOLD, RED, token, glow, chip, cover, grade, shade, top_shade, daylight)
from engine import prog, clamp, lerp, e_out_back, e_out_cubic, e_in_cubic, e_inout_cubic, post

FPS = 30
S = G.S
OFF = 2.0                                     # the voice starts when the needle finds 90.6
WORDS = [(w, a + OFF, b + OFF) for w, a, b in json.load(open(f'{S}/tts/info.json'))['words']]
DUR = 32.0
NF = int(DUR * FPS)
_X, _Y = R._X, R._Y


def WT(i):
    return WORDS[i][1]


T = dict(From=WT(0), room=WT(2), Whalley=WT(4), to=WT(6), Manchester=WT(10), Spiritual=WT(11), faith=WT(14), with_=WT(16),
         tea=WT(19), Community=WT(20), way=WT(24), work=WT(26), Health=WT(27), wellbeing=WT(28), youth=WT(29), family=WT(31),
         conversations=WT(32), wherever=WT(33), you=WT(34), are=WT(35), Missed=WT(36), podcast=WT(41), Heritage=WT(42),
         inform=WT(45), inspire=WT(46), elevate=WT(48), Tune=WT(49), ninety=WT(51), point=WT(52), FM=WT(53), DAB=WT(54),
         free=WT(58), app=WT(59), end=WORDS[-1][2])

# Captions = the PDF script word for word, each word timed to the voice; '*' marks the PDF's teal cue words.
CAPS = [
    ([['From', 0], ['one', 1], ['room', 2], ['in', 3], ['*Whalley', 4], ['*Range…', 5]],),
    ([['…to', 6], ['the', 7], ['whole', 8], ['of', 9], ['*Manchester.', 10]],),
    ([['Spiritual', 11], ['talks', 12], ['and', 13], ['*faith', 14], ['*reflections', 15]],
     [['with', 16], ['your', 17], ['morning', 18], ['tea.', 19]]),
    ([['*Community', 20], ['*news', 21], ['on', 22], ['the', 23], ['way', 24], ['to', 25], ['work.', 26]],),
    ([['Health,', 27], ['well-being,', 28], ['youth', 29], ['and', 30]],
     [['*family', 31], ['conversations,', 32], ['wherever', 33], ['you', 34], ['are.', 35]]),
    ([['Missed', 36], ['it?', 37], ["It's", 38], ['on', 39], ['the', 40], ['*podcast.', 41]],),
    ([['Heritage', 42], ['Radio.', 43], ['To', 44], ['inform,', 45], ['inspire', 46]], [['and', 47], ['*elevate.', 48]]),
    ([['Tune', 49], ['in:', 50], ['*ninety', 51], ['*point', 52], ['*six', 52.5], ['FM,', 53], ['DAB+', 54]],
     [['and', 56], ['the', 57], ['free', 58], ['app.', 59]]),
]


def word_time(i):
    if i == 52.5:
        return WT(52) + 0.2
    return WT(int(i))


def cap_window(k):
    lines = CAPS[k]
    t0 = word_time(lines[0][0][1]) - 0.12
    t1 = word_time(CAPS[k + 1][0][0][1]) - 0.2 if k + 1 < len(CAPS) else DUR
    return t0, t1


@functools.lru_cache(maxsize=512)
def wmask(w, size):
    return _wmask(w, PX, size)


@functools.lru_cache(maxsize=64)
def cap_size(k, size=64, maxw=W - 150):
    while size > 36:
        wmax = max(sum(wmask(w.lstrip('*'), size).shape[1] for w, _ in line) + size * 0.22 * (len(line) - 1) for line in CAPS[k])
        if wmax <= maxw:
            return size
        size -= 2
    return size


def captions(c, t, y=1440, size=64):
    for k, lines in enumerate(CAPS):
        t0, t1 = cap_window(k)
        if not (t0 - 0.05 <= t < t1 + 0.25):
            continue
        size = cap_size(k)
        out = prog(t, t1 - 0.05, t1 + 0.2)
        yy0 = y if k < len(CAPS) - 1 else 1470
        for li, line in enumerate(lines):
            ms = [wmask(w.lstrip('*'), size) for w, _ in line]
            tw = sum(m.shape[1] for m in ms) + size * 0.22 * (len(ms) - 1)
            x = W / 2 - tw / 2
            yy = yy0 + li * size * 1.24
            for (w, i), m in zip(line, ms):
                ti = word_time(i)
                k_in = prog(t, ti - 0.1, ti + 0.18)
                if k_in > 0:
                    op = min(1, k_in * 1.7) * (1 - out)
                    dy = (1 - e_out_cubic(k_in)) * 18 - out * 16
                    cx = x + m.shape[1] / 2
                    if w.startswith('*'):
                        kh = e_out_back(prog(t, ti, ti + 0.3), 1.6)
                        if kh > 0:
                            hl = rrect(m.shape[1] + 18, size * 1.12, 16, TEAL)
                            draw(c, hl, cx, yy + 3 + dy, scale=max(0.01, kh), opacity=op)
                    else:
                        draw(c, blur_sprite(solid(m, (0, 0.04, 0.03, 1)), 9), cx + 3, yy + 7 + dy, opacity=0.55 * op)
                    draw(c, solid(m, WHITE), cx, yy + dy, opacity=op)
                x += m.shape[1] + size * 0.22


# ------------------------------------------------------------------ footage
class Clip:
    def __init__(self, cid):
        self.cap = cv2.VideoCapture(f'{S}/clips/{cid}.mp4')
        self.fps = self.cap.get(cv2.CAP_PROP_FPS) or 25
        self.n = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
        self.pos = -1
        self.cache = {}

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


def footage(cid, ct, fx=0.5, fy=0.5, z=1.0, w=W, h=H, day='midday'):
    if cid not in _clips:
        _clips[cid] = Clip(cid)
    im = _clips[cid].frame(ct).astype(np.float32)[..., ::-1] / 255
    return daylight(grade(cover(im, fx, fy, z, w, h, sharpen=False)), day)


# ------------------------------------------------------------------ animated pieces
def pop(c, name, x, y, size, t, t0, rot=0, rays=True, col=None, bob=8, t1=None):
    k = prog(t, t0, t0 + 0.42)
    if k <= 0:
        return
    ko = prog(t, t1, t1 + 0.25) if t1 else 0
    if ko >= 1:
        return
    sp = token(name)
    e = e_out_back(k, 2.2) * (1 - 0.3 * ko)
    sc = size / max(sp.shape[:2]) * e
    yy = y + bob * math.sin((t - t0) * 2.1) + (1 - e_out_cubic(k)) * 70
    rr = rot + (1 - k) * -16 + 2.5 * math.sin((t - t0) * 1.6)
    op = min(1, k * 2.5) * (1 - ko)
    if rays and k < 1:
        kr = e_out_cubic(prog(t, t0, t0 + 0.5))
        lay = np.zeros((H, W), np.uint8)
        r0 = size * 0.48 + kr * 30
        for j in range(12):
            a = j / 12 * 2 * math.pi + 0.15
            ln = (28 if j % 2 else 46) * (1 - kr * 0.5)
            cv2.line(lay, (int((x + math.cos(a) * r0) * 4), int((yy + math.sin(a) * r0) * 4)),
                     (int((x + math.cos(a) * (r0 + ln)) * 4), int((yy + math.sin(a) * (r0 + ln)) * 4)), 255, 5 * 4, cv2.LINE_AA, shift=2)
        m = lay.astype(np.float32)[..., None] / 255 * 0.9 * (1 - kr * 0.7)
        c[:] = c * (1 - m) + np.array((col or LGOLD)[:3], np.float32) * m
    draw(c, blur_sprite(tint(sp, (0.0, 0.05, 0.04)), 20), x + 8, yy + 24, scale=sc, rot=rr, opacity=0.5 * op)
    draw(c, sp, x, yy, scale=sc, rot=rr, opacity=op)


def pill(c, text, x, y, t, t0, t1=None):
    k = prog(t, t0, t0 + 0.4)
    if k <= 0:
        return
    ko = prog(t, t1, t1 + 0.25) if t1 else 0
    if ko >= 1:
        return
    e = e_out_back(k, 1.7)
    s = ts(text, PS, 34, GREEN_D, 0.02)
    p = rrect(s.shape[1] + 120, s.shape[0] + 36, (s.shape[0] + 36) / 2, IVORY).copy()
    paste_spr(p, rrect(22, 22, 11, TEAL), 40, p.shape[0] / 2)
    paste_spr(p, s, 90 + s.shape[1] / 2, p.shape[0] / 2)
    op = min(1, k * 2) * (1 - ko)
    xx = x - (1 - e_out_cubic(k)) * 60
    draw(c, blur_sprite(tint(p, (0, 0.04, 0.03)), 12), xx + 6, y + 12, scale=e, opacity=0.45 * op)
    draw(c, p, xx, y, scale=e, opacity=op)


def rings(c, x, y, phase, n=4, rmax=900, amt=1.0, inward=False, w=4):
    if amt <= 0:
        return
    lay = np.zeros((H, W), np.float32)
    for j in range(n):
        p = (phase + j / n) % 1.0
        if inward:
            p = 1 - p
        r = 30 + p * rmax
        tmp = np.zeros((H, W), np.uint8)
        cv2.circle(tmp, (int(x * 4), int(y * 4)), int(r * 4), 255, max(4, int(w * 4 * (1.4 - p))), cv2.LINE_AA, shift=2)
        lay = np.maximum(lay, tmp.astype(np.float32) / 255 * (1 - p) ** 1.2 * min(1, p * 8))
    small = cv2.resize(lay, (W // 4, H // 4), interpolation=cv2.INTER_AREA)
    bl = cv2.resize(cv2.GaussianBlur(small, (0, 0), 2.5), (W, H))
    m = np.clip(lay + bl * 0.9, 0, 1)[..., None] * amt
    c[:] = c * (1 - m) + np.array(LGOLD[:3], np.float32) * m


def tag(c, t, t0, text='WHALLEY RANGE · MANCHESTER', x=70, y=420):
    k = prog(t, t0, t0 + 0.45)
    if k <= 0:
        return
    tmp = c.copy()
    FB.tag(tmp, text, x, y, icon='pin')
    e = e_out_cubic(k)
    # wipe the tag on from the left
    ramp = np.clip((_X - 40 - e * 900) / -40, 0, 1)[..., None] * (np.abs(_Y - y - 10) < 70)[..., None]
    c[:] = c * (1 - ramp) + tmp * ramp


def light_leak(c, t, x=900, y=300, amt=0.25, col=(1.0, 0.7, 0.4)):
    g = np.exp(-(((_X - x - 80 * math.sin(t * 0.7)) / 520) ** 2 + ((_Y - y) / 700) ** 2))[..., None] * amt
    c[:] = np.clip(c + g * np.array(col, np.float32), 0, 1)


# ------------------------------------------------------------------ shots
def sh_walk(t):
    c = footage(4893, 0.6 + t, fy=0.62, z=1.08 + 0.02 * t, day='dawn')
    light_leak(c, t, 860, 260, 0.22)
    c = top_shade(c, 0.25, 0.55)
    c = shade(c, 0.64, 0.75)
    fi = prog(t, 0, 0.5)
    c = c * fi
    tag(c, t, 0.4)
    return c


def sh_studio(t):
    t0 = SH['studio'][0]
    c = footage(24621, 1.0 + (t - t0), fx=0.45, z=1.08 + 0.03 * (t - t0), day='studio')
    kl = prog(t, T['room'] - 0.05, T['room'] + 0.25)
    if kl > 0:
        glow(c, 540, 560, 420, RED, 0.28 * kl * (0.92 + 0.08 * math.sin(t * 20)))
    c = shade(c, 0.66, 0.75)
    pop(c, 'onair', 540, 560, 440, t, T['room'] - 0.1, rot=-3, col=RED)
    pop(c, 'pin', 850, 960, 220, t, T['Whalley'] - 0.05)
    tag(c, t, T['Whalley'] - 0.05, y=1180)
    G.logo_small(c)
    return c


@functools.lru_cache(maxsize=1)
def MAP():
    return G.map_bg()


@functools.lru_cache(maxsize=1)
def BLD_CARD():
    return FB.sprite_of(G.photo('Generated-Image-September-14-2025-9_38PM.png', 0.5, 0.5, 1.0, 300, 190), 20)


def sh_map(t):
    t0 = SH['map'][0]
    c = MAP().copy()
    kz = e_inout_cubic(prog(t, t0, t0 + 1.2))
    kr = prog(t, T['to'], T['Manchester'] + 1.4)
    radius = 140 + kr * 900
    rings(c, *G.WR, (t - T['to']) * 0.55, n=5, rmax=1100, amt=min(1, prog(t, T['to'] - 0.1, T['to'] + 0.3) * 1.2))
    G.map_labels(c, radius)
    card = BLD_CARD()
    draw(c, rrect(316, 206, 26, LGOLD), *G.WR)
    draw(c, card, *G.WR)
    pop(c, 'mast', 850, 1190, 250, t, T['Manchester'] - 0.05)
    z = lerp(2.4, 1.0, kz)                       # rise up from the building to the whole city
    if z > 1.001:
        cx, cy = G.WR
        c = cv2.warpAffine(c, np.float32([[z, 0, (1 - z) * cx], [0, z, (1 - z) * cy]]), (W, H), borderMode=cv2.BORDER_REPLICATE)
    return c


def sh_radio(t):
    t0 = SH['radio'][0]
    c = footage(43370, 2.5 + (t - t0), fx=0.42, z=1.04 + 0.02 * (t - t0), day='morning')
    # hide the radio's brand badge under a patch of its own grille fabric (no brand names on screen)
    u = clamp((t - 6.6) / 3.0, 0, 1.3)
    bx, by, bw, bh = int(lerp(555, 475, u)), 830, 150, 235
    src = c[by:by + bh, bx + 180:bx + 180 + bw].copy()
    fm = np.zeros((bh, bw), np.float32)
    fm[14:-14, 14:-14] = 1
    fm = cv2.GaussianBlur(fm, (0, 0), 6)[..., None]
    c[by:by + bh, bx:bx + bw] = c[by:by + bh, bx:bx + bw] * (1 - fm) + src * fm
    light_leak(c, t, 900, 380, 0.18)
    c = shade(c, 0.64, 0.8)
    rings(c, 350, 820, (t - t0) * 0.45, n=3, rmax=420, amt=0.8)
    pop(c, 'radio', 760, 640, 370, t, T['faith'] - 0.05)
    pill(c, 'Spiritual talks · faith reflections', 540, 1240, t, T['faith'] + 0.15)
    return c


def sh_tea(t):
    t0 = SH['tea'][0]
    c = footage(45086, 5.0 + (t - t0), fx=0.6, z=1.06 + 0.02 * (t - t0), day='morning')
    light_leak(c, t, 760, 420, 0.2)
    c = shade(c, 0.64, 0.75)
    pop(c, 'tea', 790, 620, 320, t, T['tea'] - 0.05)
    return c


def lcd(c, t, x, y, a=1.0):
    k = prog(t, T['way'] - 0.2, T['work'] + 0.2)
    f = lerp(87.5, 90.6, e_out_cubic(k))
    txt = f'{f:.1f}'
    G.lcd(c, x, y, txt, a=a)


def sh_car(t):
    t0 = SH['car'][0]
    c = footage(2846, 4.0 + (t - t0), fx=0.55, z=1.05 + 0.03 * (t - t0), day='rain')
    c = shade(c, 0.62, 0.8)
    ka = prog(t, t0 + 0.2, t0 + 0.6)
    if ka > 0:
        lcd(c, t, 540, 980, a=ka)
    pop(c, 'news', 790, 600, 330, t, T['Community'] - 0.05, rot=4)
    pill(c, 'Community news', 300, 760, t, T['Community'] + 0.2)
    return c


def sh_walk2(t):
    t0 = SH['walk2'][0]
    c = footage(4855, 3.0 + (t - t0), fx=0.58, z=1.04, day='midday')
    c = shade(c, 0.62, 0.8)
    pop(c, 'heart', 300, 640, 260, t, T['wellbeing'] - 0.05)
    pill(c, 'Health · well-being', 300, 840, t, T['wellbeing'] + 0.15)
    return c


def sh_bus(t):
    t0 = SH['bus'][0]
    c = footage(46702, 6.0 + (t - t0), fx=0.45, z=1.04 + 0.02 * (t - t0), day='midday')
    c = shade(c, 0.62, 0.8)
    pop(c, 'family', 300, 820, 250, t, T['family'] - 0.05, rays=False)
    pop(c, 'bubbles', 760, 560, 320, t, T['conversations'] - 0.05)
    pill(c, 'Youth · family conversations', 540, 1160, t, T['conversations'] + 0.15)
    return c


def sh_trip(t):
    t0 = SH['trip'][0]
    c = np.ones((H, W, 3), np.float32) * np.array(GREEN_D[:3], np.float32)
    hh = (H - 60) // 3
    for i, (cid, ct, fx) in enumerate(((15914, 3.0, 0.45), (4855, 7.0, 0.55), (47203, 4.0, 0.5))):
        k = e_out_cubic(prog(t, t0 + i * 0.22, t0 + i * 0.22 + 0.4))
        if k <= 0:
            continue
        sub = footage(cid, ct + (t - t0), fx=fx, w=W - 40, h=hh, day='midday')
        y0 = 20 + i * (hh + 10)
        dx = int((1 - k) * (W if i % 2 == 0 else -W))
        x0 = 20 + dx
        xa, xb = max(0, x0), min(W, x0 + W - 40)
        if xb > xa:
            c[y0:y0 + hh, xa:xb] = sub[:, xa - x0:xb - x0]
    c = shade(c, 0.7, 0.8)
    pop(c, 'speaker', 860, 470, 230, t, T['you'] - 0.05)
    pop(c, 'earbuds', 220, 1060, 230, t, T['are'] - 0.05)
    return c


def sh_pod(t):
    t0 = SH['pod'][0]
    c = footage(51134, 3.5 + (t - t0), fx=0.5, z=1.04 + 0.02 * (t - t0), day='evening')
    light_leak(c, t, 300, 500, 0.15, (1, 0.6, 0.4))
    c = shade(c, 0.62, 0.8)
    pop(c, 'headphones', 760, 600, 340, t, T['podcast'] - 0.05)
    pop(c, 'play', 330, 900, 210, t, T['podcast'] + 0.25, rays=False)
    pill(c, 'YouTube · Spotify · Apple Podcasts', 540, 1240, t, T['podcast'] + 0.35)
    return c


@functools.lru_cache(maxsize=1)
def DUSK():
    return G.dusk_centre(0.42, 1.12)


def sh_dusk(t):
    t0 = SH['dusk'][0]
    base = DUSK()
    z = 1.0 + 0.05 * e_inout_cubic(prog(t, t0, SH['dusk'][1]))
    c = cv2.warpAffine(base, np.float32([[z, 0, (1 - z) * 540], [0, z, (1 - z) * 760]]), (W, H), borderMode=cv2.BORDER_REPLICATE)
    rings(c, 540, 760, (t - t0) * 0.5, n=4, rmax=900, inward=True, amt=0.9)
    c = shade(c, 0.62, 0.85)
    for i, (nm, lab, x, key) in enumerate((('bulb', 'inform', 220, 'inform'), ('star', 'inspire', 540, 'inspire'),
                                            ('arrow', 'elevate', 860, 'elevate'))):
        pop(c, nm, x, 1040 - i * 40, 190, t, T[key] - 0.05, rays=(i == 2))
        k = prog(t, T[key] + 0.05, T[key] + 0.4)
        if k > 0:
            s = ts(lab, PB, 34, GREEN_D)
            p = rrect(s.shape[1] + 50, s.shape[0] + 30, (s.shape[0] + 30) / 2, (1, 1, 1, 0.95)).copy()
            paste_spr(p, s, p.shape[1] / 2, p.shape[0] / 2)
            draw(c, p, x, 1185 - i * 40, scale=e_out_back(k, 1.8), opacity=min(1, k * 2))
    return c


def sh_dial(t):
    t0 = SH['dial'][0]
    c = footage(48533, 2.0 + (t - t0) * 1.4, fx=0.5, z=1.15 + 0.06 * (t - t0), day='evening')
    glow(c, 540, 900, 500, LGOLD, 0.15)
    c = shade(c, 0.66, 0.8)
    return c


def sh_end(t):
    t0 = SH['end'][0]
    c = FB.sacred_bg()
    rings(c, 540, 560, (t - t0) * 0.35, n=4, rmax=620, amt=0.45)
    k = prog(t, T['ninety'] - 0.1, T['ninety'] + 0.4)
    if k > 0:
        big = ts('90.6 FM', PB, 170, WHITE)
        e = e_out_back(k, 1.8)
        draw(c, blur_sprite(tint(big, LGOLD[:3]), 24), 540, 560, scale=e, opacity=0.5 * min(1, k * 2))
        draw(c, big, 540, 560, scale=e, opacity=min(1, k * 2))
    kd = prog(t, T['DAB'] - 0.1, T['DAB'] + 0.3)
    if kd > 0:
        draw(c, ts('DAB+ Manchester  ·  Online  ·  Free app', PM, 38, (1, 1, 1, 0.92)), 540, 690 + (1 - kd) * 20, opacity=kd)
    kb = prog(t, T['free'], T['free'] + 0.4)
    if kb > 0:
        pulse = 1 + 0.03 * math.sin((t - T['free']) * 4) * prog(t, T['free'] + 0.6, T['free'] + 1.0)
        e = e_out_back(kb, 2.0) * pulse
        b = rrect(560, 112, 56, MAG)
        draw(c, blur_sprite(b, 20), 540, 836, scale=e, opacity=0.5 * min(1, kb * 2))
        draw(c, b, 540, 820, scale=e)
        tmp = np.zeros((130, 600, 4), np.float32)
        s = ts('Listen live', PB, 48, WHITE)
        paste_spr(tmp, s, 300 - 20, 65)
        tri = np.zeros((40, 34), np.uint8)
        cv2.fillPoly(tri, [np.array([[4, 4], [4, 36], [32, 20]])], 255, cv2.LINE_AA)
        paste_spr(tmp, solid(tri.astype(np.float32) / 255, WHITE), 300 + s.shape[1] / 2 + 10, 65)
        draw(c, tmp, 540, 820, scale=e)
        sw = prog(t, T['free'] + 0.7, T['free'] + 1.4)
        if 0 < sw < 1:
            band = np.exp(-((_X - lerp(240, 840, sw) - (_Y - 820) * 0.4) / 36) ** 2) * (np.abs(_Y - 820) < 54)
            c = np.clip(c + band[..., None] * 0.35, 0, 1)
    kt = prog(t, T['app'] + 0.3, T['app'] + 0.8)
    if kt > 0:
        draw(c, ts('Heritage Radio · inform, inspire, elevate', PS, 32, LGOLD), 540, 950, opacity=kt)
    pop(c, 'phone', 850, 1120, 250, t, T['app'] - 0.1, rays=False)
    pop(c, 'radio', 240, 1130, 240, t, T['DAB'] - 0.05, rays=False)
    kl = prog(t, t0 + 0.2, t0 + 0.7)
    lg = FB.logo()
    draw(c, lg, 540, 1330, scale=420 / lg.shape[1] * (0.92 + 0.08 * e_out_cubic(kl)), opacity=kl)
    return c


def build_shots():
    s = {}
    s['walk'] = (0.0, T['room'] - 0.12)
    s['studio'] = (s['walk'][1], T['to'] - 0.1)
    s['map'] = (s['studio'][1], T['Spiritual'] - 0.3)
    s['radio'] = (s['map'][1], T['with_'] + 0.25)
    s['tea'] = (s['radio'][1], T['Community'] - 0.28)
    s['car'] = (s['tea'][1], T['Health'] - 0.25)
    s['walk2'] = (s['car'][1], T['youth'] - 0.05)
    s['bus'] = (s['walk2'][1], T['wherever'] - 0.15)
    s['trip'] = (s['bus'][1], T['Missed'] - 0.2)
    s['pod'] = (s['trip'][1], T['Heritage'] - 0.25)
    s['dusk'] = (s['pod'][1], T['Tune'] - 0.2)
    s['dial'] = (s['dusk'][1], T['ninety'] - 0.15)
    s['end'] = (s['dial'][1], DUR + 1)
    return s


SH = build_shots()
ORDER = ['walk', 'studio', 'map', 'radio', 'tea', 'car', 'walk2', 'bus', 'trip', 'pod', 'dusk', 'dial', 'end']
FN = dict(walk=sh_walk, studio=sh_studio, map=sh_map, radio=sh_radio, tea=sh_tea, car=sh_car, walk2=sh_walk2, bus=sh_bus,
          trip=sh_trip, pod=sh_pod, dusk=sh_dusk, dial=sh_dial, end=sh_end)


# ------------------------------------------------------------------ transitions
def tr_static(a, b, p):
    """Radio static: torn scanlines, colour split, noise, then the next picture."""
    src = (a if p < 0.5 else b).copy()
    k = 1 - abs(p - 0.5) * 2
    rng = np.random.default_rng(int(p * 1000))
    out = src.copy()
    for _ in range(int(14 * k) + 2):
        y0 = rng.integers(0, H - 40)
        hh = rng.integers(6, 60)
        out[y0:y0 + hh] = np.roll(src[y0:y0 + hh], int(rng.integers(-120, 120) * k), axis=1)
    sh = int(18 * k)
    if sh:
        out[..., 0] = np.roll(out[..., 0], sh, 1)
        out[..., 2] = np.roll(out[..., 2], -sh, 1)
    noise = rng.random((H // 4, W // 4)).astype(np.float32)
    noise = cv2.resize(noise, (W, H), interpolation=cv2.INTER_NEAREST)[..., None]
    return np.clip(out * (1 - 0.45 * k) + noise * 0.45 * k, 0, 1)


def tr_ring(a, b, p, cx=540, cy=560):
    """Signal-ring wipe: a golden ring expands and the next shot is inside it."""
    e = e_inout_cubic(p)
    r = e * 1500
    d = np.hypot(_X - cx, _Y - cy)
    m = np.clip((r - d) / 6, 0, 1)[..., None]
    rim = np.clip(1 - np.abs(d - r) / 12, 0, 1)[..., None] * (1 - abs(p - 0.5) * 1.2)
    out = b * m + a * (1 - m)
    return np.clip(out * (1 - rim) + np.array(LGOLD[:3], np.float32) * rim, 0, 1)


def tr_ring_in(a, b, p):
    """Rings flowing back home: the old shot closes in a shrinking gold ring onto the next."""
    e = e_inout_cubic(p)
    r = (1 - e) * 1500
    d = np.hypot(_X - 540, _Y - 760)
    m = np.clip((r - d) / 6, 0, 1)[..., None]
    rim = np.clip(1 - np.abs(d - r) / 12, 0, 1)[..., None] * (1 - abs(p - 0.5) * 1.2)
    out = a * m + b * (1 - m)
    return np.clip(out * (1 - rim) + np.array(LGOLD[:3], np.float32) * rim, 0, 1)


def tr_needle(a, b, p):
    """A red tuning needle sweeps across; behind it is the next shot."""
    e = e_inout_cubic(p)
    x = lerp(-60, W + 60, e)
    m = (_X < x).astype(np.float32)[..., None]
    out = b * m + a * (1 - m)
    g = np.exp(-((_X - x) / 40) ** 2)[..., None]
    line = (np.abs(_X - x) < 4).astype(np.float32)[..., None]
    out = np.clip(out + g * 0.35 * np.array(LGOLD[:3], np.float32), 0, 1)
    return out * (1 - line) + np.array(RED[:3], np.float32) * line


def tr_whip(a, b, p):
    return R.whip(a, b, p, 1)


def tr_whipv(a, b, p):
    return R.whip(a, b, p, 0)


def tr_flash(a, b, p):
    src = a if p < 0.5 else b
    k = 1 - abs(p - 0.5) * 2
    return np.clip(src + k ** 2 * 0.45, 0, 1)


def tr_leak(a, b, p):
    e = e_inout_cubic(p)
    out = a * (1 - e) + b * e
    k = math.sin(math.pi * p)
    g = np.exp(-(((_X - lerp(0, W, p)) / 500) ** 2))[..., None] * k * 0.5
    return np.clip(out + g * np.array([1.0, 0.75, 0.45], np.float32), 0, 1)


def tr_zoom(a, b, p):
    e = e_inout_cubic(p)
    za = 1 + e * 0.6
    A = cv2.warpAffine(a, np.float32([[za, 0, (1 - za) * W / 2], [0, za, (1 - za) * H / 2]]), (W, H), borderMode=cv2.BORDER_REPLICATE)
    zb = 1.4 - e * 0.4
    B = cv2.warpAffine(b, np.float32([[zb, 0, (1 - zb) * W / 2], [0, zb, (1 - zb) * H / 2]]), (W, H), borderMode=cv2.BORDER_REPLICATE)
    out = A * (1 - e) + B * e
    k = math.sin(math.pi * p)
    return cv2.GaussianBlur(out, (0, 0), 0.1 + 6 * k) if k > 0.1 else out


def tr_slide(a, b, p):
    e = e_inout_cubic(p)
    off = int(e * H)
    out = a.copy()
    out[:H - off] = a[off:] * (1 - 0.3 * e)
    out[H - off:] = b[:off] if off else out[H - off:]
    return out


TRANS = {'studio': (tr_static, 0.32), 'map': (tr_ring, 0.55), 'radio': (tr_zoom, 0.45), 'tea': (tr_leak, 0.5),
         'car': (tr_whip, 0.34), 'walk2': (tr_needle, 0.45), 'bus': (tr_whipv, 0.34), 'trip': (tr_flash, 0.3),
         'pod': (tr_slide, 0.42), 'dusk': (tr_ring_in, 0.6), 'dial': (tr_static, 0.32), 'end': (tr_ring, 0.55)}


# ------------------------------------------------------------------ global overlays
def freq_at(t):
    """Needle: searches the band through static in the opening, finds 90.6 as the voice comes in."""
    if t < OFF:
        u = t / OFF
        return 90.6 + (1 - e_out_cubic(u)) * 14 * math.cos(u * 9) * (1 - u) + 4 * (1 - u) * math.sin(u * 23)
    return 90.6 + 0.05 * math.sin(t * 1.3)


def overlays(c, t):
    if t < SH['end'][0] - 0.1:
        a = prog(t, 0.15, 0.6)
        G.tuner(c, freq_at(t), 0.0, y=290, a=a)
    else:
        lock = prog(t, T['ninety'] - 0.1, T['ninety'] + 0.4)
        G.tuner(c, 90.6, lock, y=330)
    if t >= SH['studio'][0] and t < SH['end'][0]:
        G.logo_small(c) if False else None
    captions(c, t)


def cue_hits():
    return [(T['room'], 0.6), (T['Whalley'], 0.3), (T['Manchester'], 0.6), (T['faith'], 0.5), (T['tea'], 0.5), (T['Community'], 0.6),
            (T['wellbeing'], 0.5), (T['conversations'], 0.5), (T['podcast'], 0.6), (T['elevate'], 0.5), (T['ninety'], 0.8),
            (T['free'], 0.5)]


HITS = cue_hits()


def energy(t):
    z = 1.0
    for th, pn in HITS:
        d = t - th
        if 0 <= d < 0.3:
            z += 0.02 * pn * (1 - d / 0.3) ** 2
    return z


def shot_at(name, t):
    return FN[name](t)


def render_raw(t):
    c = None
    for j in range(1, len(ORDER)):
        nm = ORDER[j]
        a = SH[nm][0]
        kind, td = TRANS[nm]
        d = t - (a - td / 2)
        if 0 <= d < td:
            c = kind(shot_at(ORDER[j - 1], min(t, a - 0.01)), shot_at(nm, max(t, a)), d / td)
            break
    if c is None:
        for nm in ORDER:
            a, b = SH[nm]
            if a <= t < b:
                c = shot_at(nm, t)
                break
        if c is None:
            c = shot_at('end', t)
    z = energy(t)
    if z > 1.001:
        c = cv2.warpAffine(c, np.float32([[z, 0, (1 - z) * W / 2], [0, z, (1 - z) * H / 2]]), (W, H), borderMode=cv2.BORDER_REPLICATE)
    c = np.ascontiguousarray(c, dtype=np.float32)
    overlays(c, t)
    fo = prog(t, DUR - 1.5, DUR)
    if fo > 0:
        c = c * (1 - 0.85 * e_inout_cubic(fo))
    return c


def render(fi):
    t = fi / FPS
    return post(render_raw(t), fi, bloom=0.1, grain=0.012, vig=0.18)


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
        print('DUR', DUR, 'NF', NF)
        print({k: round(v, 2) for k, v in T.items()})
        print({k: (round(a, 2), round(b, 2)) for k, (a, b) in SH.items()})
