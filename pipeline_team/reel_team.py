"""Organic Fostering Reel 02 "You Don't Have to Be the Whole Team" -- short film cut (9:16, 40 s).

Cold open: rain before dawn, "One day.", the alarm. The day in hard cuts that come faster and faster (school run,
homework, the call), then the frame splinters 1 -> 4 -> 16 -> 100 tiles, a heartbeat climbs, and a SMASH CUT to black.
23:05, silence. A door opens and warm light floods the film; a second pair of hands; Guidance / Learning / Support;
two hands meet in backlight. The film closes where it opened: 07:00 the next day, in sunlight. End card.
ElevenLabs voice (IDA, North West). Scope letterbox, film grain, halation, anamorphic flares, subtitle captions.

Usage: python3 reel_team.py still 1.0,5.0 | python3 reel_team.py range 0 100 | python3 reel_team.py times
"""
import os, sys, math, json, functools
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import numpy as np
import cv2
import frames_team as G
from frames_team import (R, W, H, draw, blur_sprite, tint, rrect, ts, solid, paste_spr, _wmask, cover, grade, halation, flare, BAR,
                         PLUM, MAG, ORANGE, GREEN, IVORY, WHITE, N8, N7, colour_bar, LOGO, token)
from engine import prog, clamp, lerp, e_out_back, e_out_cubic, e_in_cubic, e_inout_cubic, post

FPS = 30
S = G.S
DUR = 40.0
NF = int(DUR * FPS)
_X, _Y = R._X, R._Y
WORDS = [tuple(w) for w in json.load(open(f'{S}/tts/info.json'))['words']]


def WT(i):
    return WORDS[i][1]


SUBS = [  # (first word, last word, text, highlight words, colour)
    (0, 2, 'One school run.', ('school', 'run.'), ORANGE),
    (3, 5, 'One homework question.', ('homework',), ORANGE),
    (6, 10, "One appointment you didn't expect.", ('appointment',), MAG),
    (11, 19, 'And sometimes, one day | feels like a hundred things.', ('hundred',), MAG),
    (20, 30, 'But fostering was never meant to be | something you manage alone.', ('alone.',), MAG),
    (31, 39, 'At Organic Fostering, you have | guidance and ongoing support.', ('guidance', 'support.'), MAG),
    (40, 53, 'Because when you care for a child, | someone should be looking after you, too.', ('too.',), MAG),
]

SH = {}
SH['rain'] = (0.0, 2.3)
SH['alarm'] = (2.3, WT(0) - 0.15)
SH['drive'] = (SH['alarm'][1], WT(3) - 0.2)
SH['home'] = (SH['drive'][1], WT(6) - 0.2)
SH['phone'] = (SH['home'][1], WT(11) - 0.15)
SH['hundred'] = (SH['phone'][1], WT(19) + 0.75)
SH['silence'] = (SH['hundred'][1], WT(20) - 0.25)
SH['door'] = (SH['silence'][1], WT(28) - 0.1)
SH['hands'] = (SH['door'][1], WT(31) + 0.1)
SH['three'] = (SH['hands'][1], WT(40) - 0.15)
SH['clasp'] = (SH['three'][1], WT(53) + 0.75)
SH['next'] = (SH['clasp'][1], WT(54) - 0.25)
SH['end'] = (SH['next'][1], DUR + 1)
ORDER = ['rain', 'alarm', 'drive', 'home', 'phone', 'hundred', 'silence', 'door', 'hands', 'three', 'clasp', 'next', 'end']


# ------------------------------------------------------------------ footage
class Clip:
    def __init__(self, cid):
        self.cap = cv2.VideoCapture(f'{S}/clips/{cid}.mp4')
        self.fps = self.cap.get(cv2.CAP_PROP_FPS) or 25
        self.n = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
        self.pos = -1
        self.cache = {}

    def frame(self, t):
        t = t % max(0.5, self.n / self.fps - 0.1)
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


def raw(cid, ct):
    if cid not in _clips:
        _clips[cid] = Clip(cid)
    return _clips[cid].frame(ct).astype(np.float32)[..., ::-1] / 255


def foot(cid, ct, mood, fx=0.5, fy=0.5, z=1.0, w=W, h=H):
    return grade(cover(raw(cid, ct), fx, fy, z, w, h), mood)


# ------------------------------------------------------------------ film helpers
def letterbox(c):
    c[:BAR] = 0.0
    c[H - BAR:] = 0.0
    return c


def stamp(c, text, t, t0):
    k = prog(t, t0 + 0.15, t0 + 0.5)
    if k <= 0:
        return
    n = max(1, int(len(text) * k))
    G.stamp(c, text[:n] + (' ' * (len(text) - n)), col=(1, 1, 1, 0.9))


def prop(c, name, x, y, size, t, t0, rot=0, drift=1.0):
    """A real-looking object drifts into the shot on its word and floats, with depth-of-field softness."""
    k = prog(t, t0, t0 + 0.5)
    if k <= 0:
        return
    e = e_out_cubic(k)
    sp = token(name)
    sc = size / max(sp.shape[:2]) * (0.85 + 0.15 * e)
    yy = y + (1 - e) * 80 + 8 * math.sin((t - t0) * 1.6) * drift
    rr = rot + (1 - e) * 14 + 3 * math.sin((t - t0) * 1.1)
    draw(c, blur_sprite(tint(sp, (0, 0, 0)), 20), x + 12, yy + 30, scale=sc, rot=rr, opacity=0.45 * k)
    draw(c, sp, x, yy, scale=sc, rot=rr, opacity=min(1, k * 1.8))


def subtitles(c, t):
    for a, b, text, keys, hl in SUBS:
        t0 = WT(a) - 0.1
        nxt = [s for s in SUBS if s[0] > b]
        t1 = (WT(nxt[0][0]) - 0.25) if nxt else WT(b) + 1.2
        t1 = min(t1, WORDS[b][2] + 1.4)
        if a == 11:
            t1 = SH['hundred'][1]                                # the smash cut takes the words with it
        if not (t0 <= t < t1):
            continue
        k = prog(t, t0, t0 + 0.25) * (1 - prog(t, t1 - 0.25, t1))
        tmp = np.zeros_like(c)
        lines = [l.strip() for l in text.split('|')]
        size = 46 if len(lines) == 1 else 40
        G.subtitle(tmp, lines, keys=keys, hl=hl, y=H - BAR + (78 if len(lines) == 1 else 60), size=size)
        m = (tmp.max(2, keepdims=True) > 0).astype(np.float32)
        band = np.zeros((H, W, 1), np.float32)
        band[H - BAR:] = 1
        c[:] = c * (1 - band * m * k) + tmp * band * m * k


def push(c, z, cx=W / 2, cy=H / 2):
    if abs(z - 1) < 1e-3:
        return c
    return cv2.warpAffine(c, np.float32([[z, 0, (1 - z) * cx], [0, z, (1 - z) * cy]]), (W, H), borderMode=cv2.BORDER_REPLICATE)


# ------------------------------------------------------------------ shots
def sh_rain(t):
    c = foot('20311', 4.0 + t * 0.7, 'cold', z=1.05 + 0.02 * t) * 0.72
    stamp(c, '07:00', t, 0.0)
    k = prog(t, 0.5, 1.4) * (1 - prog(t, 2.0, 2.3))
    if k > 0:
        G.title_card(c, 'One day.', 960, 120, k=k)
    return c


def sh_alarm(t):
    t0 = SH['alarm'][0]
    c = foot('4758', 2.2 + (t - t0), 'cold', 0.7, 0.5, 1.0 + 0.03 * (t - t0))
    stamp(c, '07:00', t, t0)
    return c


def sh_drive(t):
    t0 = SH['drive'][0]
    c = foot('4521', 5.0 + (t - t0), 'cold', 0.4, 0.5, 1.1 + 0.03 * (t - t0))
    c = halation(c, 0.3)
    flare(c, 760 + 40 * math.sin(t * 3), 760, 0.35)
    prop(c, 'backpack', 830, 1180, 220, t, WT(1) - 0.05, rot=8)
    stamp(c, '08:12', t, t0)
    return c


def sh_home(t):
    t0 = SH['home'][0]
    c = foot('4533', 6.5 + (t - t0), 'cold', 0.5, 0.5, 1.1 + 0.03 * (t - t0))
    prop(c, 'question', 820, 760, 200, t, WT(5) - 0.05, rot=10)
    stamp(c, '16:40', t, t0)
    return c


def sh_phone(t):
    t0 = SH['phone'][0]
    c = foot('4513', 2.5 + (t - t0), 'cold', 0.5, 0.45, 1.22 + 0.04 * (t - t0))
    prop(c, 'calendar', 820, 1150, 220, t, WT(7) - 0.05, rot=-8)
    stamp(c, '17:25', t, t0)
    return c


TILE_SRC = [('4526', 7.0), ('4533', 5.0), ('4513', 3.5), ('4521', 6.0), ('4517', 4.0), ('38501', 6.0), ('4758', 3.0), ('39790', 5.0)]


@functools.lru_cache(maxsize=1)
def tile_bank():
    return [grade(cover(G.frame_of(cid, tt), 0.5, 0.5, 1.0, 216, 384), 'cold') for cid, tt in TILE_SRC]


def sh_hundred(t):
    """The day splinters: 1 -> 4 -> 16 -> 36 -> 100 tiles, each a different moment, faster and faster; objects
    tumble in; a heartbeat pulse shakes the frame."""
    t0, t1 = SH['hundred']
    base = foot('4526', 4.5 + (t - t0), 'cold', 0.5, 0.45, 1.2 + 0.05 * (t - t0))
    u = prog(t, t0 + 0.6, WT(19))
    n = [1, 2, 4, 6, 10][min(4, int(u * 5))]
    if n == 1:
        c = base
    else:
        c = np.zeros_like(base)
        bank = tile_bank()
        cw, ch = W / n, H / n
        rng = np.random.default_rng(int(t * 6))
        for r in range(n):
            for q in range(n):
                tile = cv2.resize(bank[rng.integers(0, len(bank))], (max(2, int(cw) - 3), max(2, int(ch) - 3)), interpolation=cv2.INTER_AREA)
                y0, x0 = int(r * ch) + 1, int(q * cw) + 1
                c[y0:y0 + tile.shape[0], x0:x0 + tile.shape[1]] = tile * rng.uniform(0.45, 1.0)
        m = np.clip(1 - np.hypot(_X - 540, _Y - 900) / (520 - 200 * u), 0, 1)[..., None] ** 0.7
        c = c * (1 - m) + base * m
    for j, (nm, x, y, r) in enumerate((('clock', 220, 560, -12), ('phone', 860, 600, 14), ('calendar', 230, 1250, 8),
                                        ('backpack', 860, 1260, -10), ('briefcase', 540, 430, 4), ('house', 540, 1420, -6))):
        prop(c, nm, x, y, 170, t, t0 + 0.5 + j * 0.35, rot=r + 20 * math.sin(t * 2 + j), drift=2.0)
    beat = (t - t0) * (1.4 + 1.6 * u)
    pulse = math.exp(-((beat % 1.0) / 0.08) ** 2)
    c = push(c, 1 + 0.025 * pulse * (0.4 + u))
    stamp(c, '21:30', t, t0)
    return c


def sh_silence(t):
    t0, t1 = SH['silence']
    if t < t0 + 0.45:                                          # smash cut to black
        return np.zeros((H, W, 3), np.float32)
    c = foot('4534', 4.0 + (t - t0) * 0.6, 'night', 0.5, 0.42, 1.12 + 0.03 * (t - t0))
    c = c * e_inout_cubic(prog(t, t0 + 0.45, t0 + 1.4))
    stamp(c, '23:05', t, t0 + 0.4)
    return c


def sh_door(t):
    t0 = SH['door'][0]
    c = foot('21813', 5.5 + (t - t0), 'warm', 0.55, 0.45, 1.1 + 0.02 * (t - t0))
    c = halation(c, 0.45)
    flare(c, 380, 700, 0.55 + 0.15 * math.sin(t * 2))
    return c


def sh_hands(t):
    t0 = SH['hands'][0]
    c = foot('4571', 3.0 + (t - t0) * 0.8, 'warm', 0.5, 0.62, 1.0 + 0.03 * (t - t0))
    return halation(c, 0.3)


def sh_three(t):
    t0, t1 = SH['three']
    c = np.zeros((H, W, 3), np.float32)
    band = (H - 2 * BAR) // 3
    for i, (cid, ct, lab, col, wi) in enumerate((('4571', 11.0, 'Guidance', MAG, 36), ('4547', 7.0, 'Learning', ORANGE, 38),
                                                ('4573', 8.0, 'Support', GREEN, 39))):
        ts0 = t0 + i * 0.55
        k = e_out_cubic(prog(t, ts0, ts0 + 0.5))
        if k <= 0:
            continue
        im = grade(cover(raw(cid, ct + (t - t0) * 0.8), 0.5, 0.45, 1.0, W, band - 6), 'warm')
        y0 = BAR + i * band + 3
        dx = int((1 - k) * (W if i % 2 == 0 else -W))
        xa, xb = max(0, dx), min(W, W + dx)
        if xb > xa:
            c[y0:y0 + im.shape[0], xa:xb] = im[:, xa - dx:xb - dx]
        kl = prog(t, WT(wi) - 0.05, WT(wi) + 0.3) if i != 1 else prog(t, WT(37), WT(37) + 0.35)
        if kl > 0:
            s = ts(lab, N8, 64, WHITE)
            p = rrect(s.shape[1] + 70, 92, 46, col).copy()
            paste_spr(p, s, p.shape[1] / 2, 46)
            e = e_out_back(kl, 1.8)
            draw(c, blur_sprite(tint(p, (0, 0, 0)), 14), 80 + p.shape[1] / 2 + 6, y0 + band - 60, scale=e, opacity=0.5 * min(1, kl * 2))
            draw(c, p, 80 + p.shape[1] / 2, y0 + band - 70, scale=e, opacity=min(1, kl * 2))
    return halation(c, 0.2)


def sh_clasp(t):
    t0, t1 = SH['clasp']
    c = foot('4505', 2.5 + (t - t0) * 0.55, 'warm', 0.5, 0.5, 1.12 + 0.04 * (t - t0))    # slow motion
    c = halation(c, 0.6)
    flare(c, 540 + 30 * math.sin(t * 0.8), 820, 0.6 + 0.2 * prog(t, WT(46), WT(53)))
    return c


def sh_next(t):
    t0 = SH['next'][0]
    c = foot('4758', 4.5 + (t - t0) * 0.6, 'warm', 0.7, 0.5, 1.0 + 0.02 * (t - t0))
    g = np.exp(-(((_X - 900) / 520) ** 2 + ((_Y - 520) / 700) ** 2))[..., None]
    c = np.clip(c + g * np.array([0.35, 0.2, 0.05], np.float32), 0, 1)
    c = halation(c, 0.6)
    flare(c, 880, 560, 0.7)
    stamp(c, '07:00', t, t0)
    k = prog(t, t0 + 0.4, t0 + 1.1)
    if k > 0:
        sh = np.clip((_Y - 1050) / 400, 0, 1)[..., None] * 0.55 * k
        c = c * (1 - sh)
        G.title_card(c, 'The next day.', 1330, 100, k=k)
    return c


def sh_end(t):
    t0 = SH['end'][0]
    c = np.ones((H, W, 3), np.float32) * np.array(IVORY[:3], np.float32)
    lg = LOGO()
    kl = prog(t, t0 + 0.2, t0 + 0.9)
    draw(c, lg, 540, 600, scale=760 / lg.shape[1] * (0.95 + 0.05 * e_out_cubic(kl)), opacity=kl)
    for j, (line, col) in enumerate((('You do not have to', PLUM), ('manage it alone.', MAG))):
        k = prog(t, t0 + 0.5 + j * 0.15, t0 + 0.9 + j * 0.15)
        if k > 0:
            draw(c, ts(line, N8, 66, col), 540, 900 + j * 85 + (1 - e_out_cubic(k)) * 20, opacity=k)
    kb = prog(t, WT(54) - 0.05, WT(54) + 0.35)
    if kb > 0:
        pulse = 1 + 0.025 * math.sin((t - WT(54)) * 4) * prog(t, WT(54) + 0.6, WT(54) + 1.0)
        e = e_out_back(kb, 1.8) * pulse
        draw(c, rrect(620, 120, 60, MAG), 540, 1160, scale=e)
        draw(c, ts('Start your enquiry', N8, 48, WHITE), 540, 1160, scale=e)
    kp = prog(t, WT(57) - 0.05, WT(57) + 0.35)
    if kp > 0:
        draw(c, ts('No pressure, no obligation.', N7, 40, PLUM), 540, 1270 + (1 - kp) * 16, opacity=kp)
        draw(c, ts('0161 241 1332  ·  organicfostering.co.uk', N7, 34, R.hexc('#655563')), 540, 1350, opacity=kp)
    colour_bar(c, H - BAR - 14, 14)
    return c


FN = dict(rain=sh_rain, alarm=sh_alarm, drive=sh_drive, home=sh_home, phone=sh_phone, hundred=sh_hundred, silence=sh_silence,
          door=sh_door, hands=sh_hands, three=sh_three, clasp=sh_clasp, next=sh_next, end=sh_end)


# ------------------------------------------------------------------ film transitions
def tr_dissolve(a, b, p):
    e = e_inout_cubic(p)
    return a * (1 - e) + b * e


def tr_flashcut(a, b, p):
    """Hard cut with a two-frame exposure flash, like a camera roll-out."""
    src = a if p < 0.5 else b
    k = max(0.0, 1 - abs(p - 0.5) * 4)
    return np.clip(src + k * 0.55, 0, 1)


def tr_cut(a, b, p):
    return a if p < 0.5 else b


def tr_lightbloom(a, b, p):
    """From the dark: the door's light blooms and becomes the next shot."""
    e = e_inout_cubic(p)
    glow = np.exp(-(((_X - 380) / (200 + 1400 * e)) ** 2 + ((_Y - 700) / (300 + 1600 * e)) ** 2))[..., None]
    out = a * (1 - e) + b * e
    return np.clip(out + glow * np.array([1.0, 0.75, 0.45], np.float32) * math.sin(math.pi * p) * 0.9, 0, 1)


def tr_leak(a, b, p):
    e = e_inout_cubic(p)
    out = a * (1 - e) + b * e
    k = math.sin(math.pi * p)
    g = np.exp(-(((_X - lerp(-200, W + 200, p)) / 420) ** 2))[..., None] * k
    return np.clip(out + g * np.array([1.0, 0.6, 0.3], np.float32) * 0.7, 0, 1)


def tr_golden(a, b, p):
    """Fade through golden light (the night turns into the next morning)."""
    k = math.sin(math.pi * p)
    src = a if p < 0.5 else b
    return np.clip(src * (1 - 0.7 * k) + np.array([1.0, 0.85, 0.6], np.float32) * 0.7 * k, 0, 1)


def tr_black(a, b, p):
    k = math.sin(math.pi * p)
    src = a if p < 0.5 else b
    return src * (1 - k)


TRANS = {'alarm': (tr_dissolve, 0.6), 'drive': (tr_flashcut, 0.14), 'home': (tr_cut, 0.04), 'phone': (tr_flashcut, 0.14),
         'hundred': (tr_cut, 0.04), 'silence': (tr_cut, 0.04), 'door': (tr_lightbloom, 1.0), 'hands': (tr_dissolve, 0.5),
         'three': (tr_leak, 0.6), 'clasp': (tr_leak, 0.7), 'next': (tr_golden, 1.0), 'end': (tr_black, 0.8)}


def render_raw(t):
    c = None
    for j in range(1, len(ORDER)):
        nm = ORDER[j]
        a = SH[nm][0]
        kind, td = TRANS[nm]
        d = t - (a - td / 2)
        if 0 <= d < td:
            c = kind(FN[ORDER[j - 1]](min(t, a - 0.01)), FN[nm](max(t, a)), d / td)
            break
    if c is None:
        for nm in ORDER:
            s0, s1 = SH[nm]
            if s0 <= t < s1:
                c = FN[nm](t)
                break
        if c is None:
            c = FN['end'](t)
    c = np.ascontiguousarray(c, dtype=np.float32)
    rng = np.random.default_rng(int(t * FPS))
    g = rng.normal(0, 0.03, (H // 2, W // 2)).astype(np.float32)
    c = np.clip(c + cv2.resize(g, (W, H))[..., None], 0, 1)
    v = np.clip(1 - (((_X - W / 2) / (W * 0.72)) ** 2 + ((_Y - H / 2) / (H * 0.62)) ** 2), 0, 1)[..., None]
    if t < SH['end'][0]:
        c = c * (0.6 + 0.4 * v)
    c = letterbox(c)
    subtitles(c, t)
    fo = prog(t, DUR - 1.4, DUR)
    if fo > 0:
        c = c * (1 - e_inout_cubic(fo))
    return c


def render(fi):
    t = fi / FPS
    return post(render_raw(t), fi, bloom=0.12, grain=0.006, vig=0.0)


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
        print({k: (round(a, 2), round(b, 2)) for k, (a, b) in SH.items()})
