"""BMHC — "The First Word" (people + heritage version, 9:16). Real people + BMHC photos + word-synced 3D pop-ups.

People walk through BMHC's gates -> a question pops up -> "Iqra. Read." -> the verse (quiet sacred mode) -> a gold pen line
runs through Baghdad, Fez and Manchester 1843 -> BMHC today -> "what will you read next?" -> CTA.
Every key word pops its object on screen; cuts land on the words.

Usage: python3 reel_bmhc.py still 1.0,5.0 | python3 reel_bmhc.py range 0 100 | python3 reel_bmhc.py times
"""
import os, sys, math, json, functools
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, '..', 'pipeline_sol'))
import numpy as np
import cv2
import frames_bmhc as F
from frames_bmhc import (R, W, H, draw, blur_sprite, tint, rrect, ts, solid, paste_spr, _wmask, GREEN_D, IVORY, TEAL, GOLD,
                         MAG, ORANGE, GREEN, WHITE, BARS, PB, PX, PS, PM, PR, AR)
from engine import prog, clamp, lerp, e_out_back, e_out_cubic, e_in_cubic, e_inout_cubic, draw3d, post

FPS = 30
S = F.S
INFO = json.load(open(f'{S}/tts/lines/info.json'))
ORDER = ['l1', 'l2', 'l3', 'l4', 'l5', 'l6', 'l7', 'l8', 'l9', 'l10', 'l11', 'l12', 'l13']
GAP = {'l6': 0.7, 'l7': 0.35, 'l8': 0.7, 'l13': 0.2}          # breathing room around the verse
VO = {}
_t = 0.45
for _k in ORDER:
    _t += GAP.get(_k, 0.12) if _k != 'l1' else 0
    VO[_k] = round(_t, 3)
    _t += INFO['dur'][_k]
DUR = round(_t + 1.4, 2)
NF = int(DUR * FPS)
FADE = 1.1


def P(line, i):
    return VO[line] + INFO['phrases'][line][i][0]


def PD(line, i):
    return INFO['phrases'][line][i][1]


def END(line):
    return VO[line] + INFO['dur'][line]


SACRED = (P('l6', 0) - 0.5, END('l7') + 0.35)                 # no SFX, no hits, no light leaks
_Y, _X = R._Y, R._X


# ------------------------------------------------------------------ sources
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
            return self.cache.get(max(self.cache) if self.cache else 0)
        self.pos = i
        if len(self.cache) > 90:
            self.cache.clear()
        self.cache[i] = im
        return im


_clips = {}


def _cover(im, k, fx, fy, z0, z1, drift):
    ih, iw = im.shape[:2]
    z = lerp(z0, z1, e_inout_cubic(k))
    sc = max(W / iw, H / ih) * z
    cw, ch = W / sc, H / sc
    cx = fx * iw + drift[0] * k * iw
    cy = fy * ih + drift[1] * k * ih
    x0 = min(max(cx - cw / 2, 0), iw - cw)
    y0 = min(max(cy - ch / 2, 0), ih - ch)
    M = np.float32([[sc, 0, -x0 * sc], [0, sc, -y0 * sc]])
    out = cv2.warpAffine(im, M, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
    if sc > 1.6:
        bl = cv2.GaussianBlur(out, (0, 0), 1.5)
        out = np.clip(out * 1.45 - bl * 0.45, 0, 1)
    return out


def footage(cid, tl, start=0.2, fx=0.5, fy=0.5, z0=1.0, z1=1.08, dur=3.0, drift=(0, 0)):
    if cid not in _clips:
        _clips[cid] = Clip(cid)
    c = _clips[cid]
    im = c.frame(start * c.n / c.fps + max(0, tl)).astype(np.float32)[..., ::-1] / 255.0
    return F.grade(_cover(im, clamp(tl / dur), fx, fy, z0, z1, drift))


@functools.lru_cache(maxsize=6)
def _photo(name, mono=False):
    im = cv2.imread(f'{F.IMG}/{name}', cv2.IMREAD_COLOR)
    if max(im.shape[:2]) > 2600:
        s = 2600 / max(im.shape[:2])
        im = cv2.resize(im, None, fx=s, fy=s, interpolation=cv2.INTER_AREA)
    im = im[..., ::-1].astype(np.float32) / 255
    if mono:
        im = im.mean(2, keepdims=True) * np.array([1.0, 0.93, 0.8], np.float32)
    return np.ascontiguousarray(im)


def still(name, tl, fx=0.5, fy=0.5, z0=1.0, z1=1.1, dur=3.0, drift=(0, 0), mono=False, grade=True):
    out = _cover(_photo(name, mono), clamp(tl / dur), fx, fy, z0, z1, drift)
    return F.grade(out) if grade else out


@functools.lru_cache(maxsize=12)
def P3(name):
    return F.prop(name)


@functools.lru_cache(maxsize=1)
def SACRED_BG():
    return F.sacred_bg()


@functools.lru_cache(maxsize=1)
def LOGO():
    return F.logo()


def shade(c, top=0.52, amt=0.85):
    return F.shade(F.top_shade(c), top, amt)


# ------------------------------------------------------------------ animated pieces
def rays(c, x, y, r0, kr, col=GOLD, n=12):
    if not 0 < kr < 1:
        return
    lay = np.zeros((H, W), np.uint8)
    r = r0 + 34 * kr
    for j in range(n):
        a = j / n * 2 * math.pi + 0.15
        ln = (30 if j % 2 else 48) * (1 - kr)
        cv2.line(lay, (int((x + math.cos(a) * r) * 4), int((y + math.sin(a) * r) * 4)),
                 (int((x + math.cos(a) * (r + ln)) * 4), int((y + math.sin(a) * (r + ln)) * 4)), 255, 5 * 4, cv2.LINE_AA, shift=2)
    m = lay.astype(np.float32)[..., None] / 255 * (1 - kr)
    c[:] = c * (1 - m) + np.array(col[:3], np.float32) * m


def pop_in(c, spr, x, y, sc, t, t0, ray=True, wobble=True, tilt=False, float_amp=10, gentle=False, opacity=1.0):
    """Object pops in on its word: overshoot scale, gold burst rays, then a gentle float (3D tilt for flat cards)."""
    k = prog(t, t0, t0 + (0.9 if gentle else 0.38))
    if k <= 0:
        return
    e = e_out_cubic(k) if gentle else e_out_back(k, 2.4)
    bob = float_amp * math.sin((t - t0) * 2.2)
    rot = (0 if gentle else (1 - k) * -16) + (3 * math.sin((t - t0) * 1.7) if wobble else 0)
    yy = y + bob + (1 - e_out_cubic(k)) * (40 if gentle else 60)
    if ray and not gentle:
        rays(c, x, yy, max(spr.shape[:2]) * sc * 0.45, prog(t, t0, t0 + 0.45))
    a = min(1, k * (1.2 if gentle else 2.5)) * opacity
    draw(c, blur_sprite(tint(spr, (0.0, 0.05, 0.04)), 20), x + 10, yy + 26, scale=sc * e, rot=rot, opacity=0.42 * a)
    if tilt:
        ry = 20 * math.sin((t - t0) * 1.5) * min(1, k)
        draw3d(c, spr, x, yy, 0, spr.shape[1] * sc * e, None, ry=ry, rx=6 * math.sin((t - t0) * 1.1))
    else:
        draw(c, spr, x, yy, scale=sc * e, rot=rot, opacity=a)


@functools.lru_cache(maxsize=64)
def chip_spr(text, fill, ink, size, font=PX, dot=None):
    s = ts(text, font, size, ink, 0.02)
    pad = 56 if dot else 0
    p = rrect(s.shape[1] + 60 + pad, s.shape[0] + 36, (s.shape[0] + 36) / 2, fill).copy()
    if dot:
        paste_spr(p, rrect(22, 22, 11, dot), 40, p.shape[0] / 2)
    paste_spr(p, s, 30 + pad + s.shape[1] / 2, p.shape[0] / 2)
    return p


def chip_in(c, text, x, y, t, t0, fill=TEAL, ink=WHITE, size=40, rot=0, font=PX, opacity=1.0, scale=1.0, dot=None):
    k = prog(t, t0, t0 + 0.3)
    if k <= 0:
        return
    p = chip_spr(text, fill, ink, size, font, dot)
    e = e_out_back(k, 2.6) * scale
    yy = y + 4 * math.sin((t - t0) * 2.2)
    draw(c, blur_sprite(tint(p, (0, 0.04, 0.03)), 12), x + 6, yy + 12, scale=e, rot=rot, opacity=0.45 * k * opacity)
    draw(c, p, x, yy, scale=e, rot=rot * (0.4 + 0.6 * k), opacity=min(1, k * 3) * opacity)


def tag_in(c, text, t, t0, y=190):
    k = prog(t, t0, t0 + 0.45)
    if k > 0:
        F.tag(c, text, 70 - (1 - e_out_cubic(k)) * 700, y, icon='pin')


def source_in(c, text, t, t0):
    k = prog(t, t0, t0 + 0.4)
    if k > 0:
        F.source(c, text, y=1840 + (1 - e_out_cubic(k)) * 120)


def progress_bar(c, t):
    """Thin story progress bar along the top in the logo's four colours."""
    k = clamp(t / (P('l13', 0)))
    w = W - 120
    draw(c, rrect(w, 7, 3.5, (1, 1, 1, 0.25)), W / 2, 64)
    fw = w * k
    seg = w / 4
    for j, col in enumerate(BARS):
        a, b = j * seg, min(fw, (j + 1) * seg)
        if b > a + 4:
            draw(c, rrect(b - a, 7, 3.5, col), 60 + (a + b) / 2, 64)


@functools.lru_cache(maxsize=256)
def word_spr(w, size, style):
    if style == 'ar':
        return solid(_wmask(w, AR, size), GOLD)
    return solid(_wmask(w, PX, size), GOLD if style == 'gold' else WHITE)


def caption(c, t, rows, size=80, y=None, maxw=920, x0=80):
    """Rows of (word, style, t_on). Words rise in as spoken; gold key words, teal highlight pills, Arabic glyphs."""
    words = [w for row in rows for w in row]
    if not words:
        return
    breaks, acc = set(), 0
    for row in rows[:-1]:
        acc += len(row)
        breaks.add(acc)
    lay_rows, cur, x = [], [], x0
    for i, (w, st, ton) in enumerate(words):
        wd = word_spr(w, size, st).shape[1]
        if cur and (i in breaks or x + wd > maxw + x0):
            lay_rows.append(cur)
            cur, x = [], x0
        cur.append((w, st, ton, x))
        x += wd + size * 0.18
    lay_rows.append(cur)
    n = len(lay_rows)
    y0 = y if y is not None else 1760 - (n - 1) * size * 1.22
    for li, row in enumerate(lay_rows):
        yy = y0 + li * size * 1.22
        for w, st, ton, x in row:
            k = prog(t, ton, ton + 0.22)
            if k <= 0:
                continue
            s = word_spr(w, size, st)
            e = e_out_cubic(k)
            if st == 'hl':
                kh = prog(t, ton + 0.05, ton + 0.3)
                hw = (s.shape[1] + 10) * e_out_cubic(kh)
                if hw > 4:
                    draw(c, rrect(hw, size * 1.08, 16, TEAL), x - 5 + hw / 2, yy + 2)
            else:
                draw(c, blur_sprite(tint(s, (0, 0.03, 0.02)), 10), x + s.shape[1] / 2 + 3, yy + 6 + (1 - e) * 30, opacity=0.5 * k)
            draw(c, s, x + s.shape[1] / 2, yy + (1 - e) * 30, opacity=min(1, k * 2))


def cap_rows(spec):
    """spec rows: list of (line, phrase_idx, 'words', {gold}, {hl}). Word times spread across the phrase."""
    rows = []
    for row in spec:
        out = []
        for item in row:
            line, pi, words, gold = item[:4]
            hl = item[4] if len(item) > 4 else set()
            ws = words.split(' ')
            t0, d = P(line, pi), PD(line, pi)
            total = sum(len(w) + 1 for w in ws)
            acc = 0
            for w in ws:
                key = w.strip(',.!?:…').lower()
                st = 'ar' if w == 'ﷺ' else ('hl' if key in hl else ('gold' if key in gold else None))
                out.append((w, st, t0 + d * 0.78 * acc / total))
                acc += len(w) + 1
        rows.append(out)
    return rows


def search_bar(c, full, t, t0, t1, y, size=44, w=940, sub=None, scale_in=True):
    """Glass search bar pops in at t0, then the question types out between t0 and t1."""
    k = prog(t, t0 - 0.25, t0 + 0.1)
    if k <= 0:
        return
    n = sum(len(l) for l in full)
    typed = int(n * clamp((t - t0) / max(0.1, t1 - t0)))
    lines, rem = [], typed
    for l in full:
        lines.append(l[:max(0, rem)])
        rem -= len(l)
    hgt = 70 + len(full) * size * 1.3
    e = e_out_back(k, 1.8) if scale_in else 1
    bar = rrect(w, hgt, 44, (1, 1, 1, 0.97))
    draw(c, blur_sprite(tint(bar, (0, 0.05, 0.04)), 26), W / 2 + 8, y + 22, scale=e, opacity=0.5 * k)
    draw(c, bar, W / 2, y, scale=e, opacity=min(1, k * 2))
    if k < 1:
        return
    m = np.zeros((60, 60), np.uint8)
    cv2.circle(m, (24, 24), 16, 255, 5, cv2.LINE_AA)
    cv2.line(m, (36, 36), (52, 52), 255, 7, cv2.LINE_AA)
    draw(c, solid(m.astype(np.float32) / 255, TEAL), W / 2 - w / 2 + 62, y - hgt / 2 + 35 + size * 0.65)
    x0 = W / 2 - w / 2 + 112
    caret_line = 0
    for li, ln in enumerate(lines):
        yy = y - hgt / 2 + 35 + size * 0.65 + li * size * 1.3
        if ln:
            s = ts(ln, PS, size, GREEN_D, 0.0)
            draw(c, s, x0 + s.shape[1] / 2, yy)
            caret_line = li
    ln = lines[caret_line]
    cx = x0 + (ts(ln, PS, size, GREEN_D).shape[1] + 12 if ln else 0)
    if (t * 2.2) % 1 < 0.6:
        draw(c, rrect(5, size * 1.1, 2, TEAL), cx, y - hgt / 2 + 35 + size * 0.65 + caret_line * size * 1.3)
    if sub and typed >= n:
        ks = prog(t, t1 + 0.1, t1 + 0.4)
        s = ts(sub, PM, 26, (1, 1, 1, 0.9), 0.1)
        draw(c, s, W / 2, y + hgt / 2 + 44 + (1 - ks) * 20, opacity=ks)


def glass_in(c, x, y, w, h, t, t0, r=40):
    k = prog(t, t0, t0 + 0.35)
    if k <= 0:
        return 0
    e = e_out_back(k, 1.6)
    F.glass(c, x, y, max(20, w * e), max(20, h * e), r, a=0.18)
    return k


# ------------------------------------------------------------------ shots
def sh_walk(t):            # "Every day,"
    c = shade(footage(15998, t, 0.1, 0.5, 0.55, 1.15, 1.0, P('l1', 1) + 0.3), 0.55)
    caption(c, t, cap_rows([[('l1', 0, 'Every day,', {'day'})]]), size=96)
    return c


def sh_gates(t):           # "people walk through these gates, in Whalley Range."
    t0 = P('l1', 1)
    c = shade(still('W6A9208-1-scaled.jpg', t - t0, 0.5, 0.5, 1.0, 1.12, 4.0, drift=(0.02, 0)), 0.5)
    tag_in(c, 'WHALLEY RANGE · MANCHESTER', t, P('l1', 2))
    caption(c, t, cap_rows([[('l1', 1, 'people walk through these gates,', {'people'}, {'gates'})],
                            [('l1', 2, 'in Whalley Range.', {'whalley', 'range'})]]), size=84)
    return c


def sh_building(t):        # "Into a place of learning, that's stood since 1843."
    t0 = P('l2', 0)
    c = shade(still('bhmc-f.png', t - t0, 0.5, 0.55, 1.12, 1.0, 4.0), 0.52)
    tk = P('l2', 1) + PD('l2', 1) * 0.55
    k = prog(t, tk - 0.1, tk + 0.4)
    if k > 0:
        old = _old_card()
        pop_in(c, old, 720, 560, 1.0, t, tk - 0.1, tilt=True)
        chip_in(c, 'Since 1843', 820, 790, t, tk + 0.15, fill=GOLD, ink=GREEN_D, size=46, rot=-4)
    caption(c, t, cap_rows([[('l2', 0, 'Into a place of learning,', {'learning'})],
                            [('l2', 1, "that's stood since 1843.", set(), {'1843'})]]), size=84)
    return c


@functools.lru_cache(maxsize=1)
def _old_card():
    old = F.photo('BMHC-Year-1866.jpg', fx=0.55, fy=0.5, w=540, h=370, g=False)
    old = old.mean(2, keepdims=True) * np.array([1.0, 0.94, 0.82], np.float32)
    card = rrect(568, 398, 28, IVORY).copy()
    paste_spr(card, F.sprite_of(old, 20), 284, 199)
    return card


QUESTION = ['What was the very first word', "of the Qur'an to be revealed?"]


def sh_question(t):        # "But here's a question. What was the very first word of the Qur'an, to be revealed?"
    t0 = P('l3', 0)
    c = shade(footage(8800, t - t0, 0.3, 0.55, 0.5, 1.0, 1.1, 5.0), 0.45, 0.9)
    chip_in(c, "Here's a question", 330, 960, t, t0 + 0.1, fill=MAG, size=40, rot=-3)
    search_bar(c, QUESTION, t, P('l3', 1), END('l3') - 0.2, 1180, sub='ASK YOURSELF FIRST')
    return c


GUESS = [('Pray?', MAG, 250, 1120, -4), ('Fast?', ORANGE, 800, 1060, 3), ('Read?', TEAL, 290, 1290, 2), ('Give?', GREEN, 800, 1260, -3)]


def sh_guess(t):           # "Pray? Fast? Read? Give? Take a guess!" (+ 3-2-1)
    t0 = P('l4', 0)
    c = shade(footage(49306, t - t0, 0.2, 0.5, 0.4, 1.05, 1.0, 6.0), 0.5, 0.88)
    for j, (txt, col, x, y, r) in enumerate(GUESS):
        chip_in(c, txt, x, y, t, P('l4', j) - 0.03, fill=col, size=60, rot=r)
    tg = P('l4', 4)
    k = prog(t, tg, tg + 0.3)
    if k > 0:
        d = t - (tg + PD('l4', 4))
        n = 3 - int(clamp(d / 0.4, 0, 2.99)) if d > 0 else 3
        frac = clamp(d / 1.2) if d > 0 else 0
        F.counter_ring(c, W / 2, 1530, 90 * e_out_back(k, 2), 1 - frac, str(n))
        s = ts('TAKE A GUESS', PX, 40, WHITE, 0.2)
        draw(c, s, W / 2, 1690, opacity=k)
    return c


def sh_iqra(t):            # "It was Iqra. Read. Revealed to the Prophet Muhammad, peace be upon him."
    t0 = P('l5', 0)
    c = shade(footage(34275, t - t0, 0.25, 0.45, 0.55, 1.0, 1.1, 6.0), 0.4, 0.9)
    kf = prog(t, t0, t0 + 0.6)                          # the other answers simply fade (no crosses)
    for (txt, col, x, y, r) in GUESS:
        if txt == 'Read?':
            continue
        chip_in(c, txt, x, lerp(y, y - 480, e_out_cubic(kf)), t, -1, fill=col, size=60, rot=r, opacity=1 - 0.75 * kf,
                scale=1 - 0.25 * kf)
    tr = P('l5', 1)
    kr = prog(t, t0, t0 + 0.5)
    rx, ry = lerp(290, W / 2, e_out_cubic(kr)), lerp(1290, 700, e_out_cubic(kr))
    if t > tr - 0.1:
        F.glow(c, rx, ry, 240, TEAL, 0.35 * prog(t, tr - 0.1, tr + 0.3))
    chip_in(c, 'Read.' if t > tr - 0.1 else 'Read?', rx, ry, t, -1, fill=TEAL, size=60 + 16 * prog(t, tr - 0.1, tr + 0.2))
    rays(c, rx, ry, 120, prog(t, tr - 0.1, tr + 0.4))
    ki = prog(t, t0 + 0.35, t0 + 0.8)
    if ki > 0:
        s = ts('IQRA', PB, 210, GOLD, 0.06)
        e = e_out_back(ki, 2.0)
        draw(c, blur_sprite(tint(s, (0, 0.05, 0.04)), 18), W / 2 + 8, 1080 + 22, scale=e, opacity=0.45 * ki)
        draw(c, s, W / 2, 1080, scale=e, opacity=min(1, ki * 2))
        s2 = ts('the first word', PM, 44, (1, 1, 1, 0.92), 0.1)
        draw(c, s2, W / 2, 1220 + (1 - ki) * 20, opacity=ki)
    caption(c, t, cap_rows([[('l5', 2, 'Revealed to the', set())], [('l5', 2, 'Prophet Muhammad ﷺ', {'muhammad'})]]), size=70,
            y=1520)
    source_in(c, 'Sahih al-Bukhari 3', t, P('l5', 2))
    return c


def verse_lines(c, t, lines, t_ons, y0, size=76, x=None, step=100):
    for ln, ton, j in zip(lines, t_ons, range(len(lines))):
        k = prog(t, ton - 0.1, ton + 0.7)
        if k <= 0:
            continue
        s = ts(ln, 'Poppins-SemiBold', size, IVORY)
        xx = W / 2 if x is None else x + s.shape[1] / 2
        draw(c, s, xx, y0 + j * step + (1 - e_out_cubic(k)) * 24, opacity=e_out_cubic(k))


def sh_verse(t):           # SACRED: "Read! In the name of your Lord, who created." — quiet, no pops, no people
    t0 = P('l6', 0)
    c = SACRED_BG().copy()
    kb = prog(t, t0 - 0.4, t0 + 1.2)
    F.glow(c, W / 2, 1180, 380, GOLD, 0.25 * kb)
    pop_in(c, P3('book'), W / 2, 1260, 1.05, t, t0 - 0.4, gentle=True, wobble=False, float_amp=6)
    verse_lines(c, t, ['“Read! In the name', 'of your Lord', 'who created.”'], [P('l6', 0), P('l6', 1) + 0.4, P('l6', 2)], 560)
    k = prog(t, P('l6', 2) + 0.3, P('l6', 2) + 1.0)
    if k > 0:
        draw(c, ts("AL-'ALAQ 96:1", PX, 32, GOLD, 0.25), W / 2, 900, opacity=k)
        draw(c, ts('trans. M.A.S. Abdel Haleem', PR, 26, (1, 1, 1, 0.65), 0.04), W / 2, 1620, opacity=k)
    return c


def sh_pen(t):             # SACRED: "Who taught, by means of the pen."
    t0 = P('l7', 0)
    c = footage(50700, t - t0, 0.45, 0.48, 0.5, 1.0, 1.06, 4.0)
    c = c * 0.5 + np.array(GREEN_D[:3], np.float32) * 0.5
    kd = e_inout_cubic(prog(t, P('l7', 1), END('l7') + 0.6))
    if kd > 0:
        pts = [(120, 1500), (300, 1300), (520, 1380), (700, 1150), (900, 1050), (1000, 820)]
        curve = F.pen_line(c, pts, w=7, amt=1.0) if kd >= 1 else _partial_line(c, pts, kd)
    F.glow(c, 820, 860, 260, GOLD, 0.2 * prog(t, t0, t0 + 1))
    pop_in(c, P3('quill'), 820, 860, 1.25, t, t0 - 0.2, gentle=True, wobble=True, float_amp=12)
    verse_lines(c, t, ['“who taught', 'by [means of]', 'the pen”'], [P('l7', 0), P('l7', 1), P('l7', 1) + 0.6], 330, size=74,
                x=80, step=96)
    k = prog(t, P('l7', 1) + 0.8, P('l7', 1) + 1.3)
    if k > 0:
        chip_in(c, "AL-'ALAQ 96:4", 210, 638, t, P('l7', 1) + 0.8, fill=GOLD, ink=GREEN_D, size=30)
    return c


def _partial_line(c, pts, k):
    p = np.array(pts, np.float32)
    seg = np.cumsum(np.r_[0, np.hypot(*np.diff(p, axis=0).T)])
    L = seg[-1] * k
    keep = [tuple(q) for q, s in zip(p, seg) if s <= L]
    i = len(keep)
    if i < len(p):
        u = (L - seg[i - 1]) / (seg[i] - seg[i - 1])
        keep.append(tuple(p[i - 1] + (p[i] - p[i - 1]) * u))
    if len(keep) >= 2:
        curve = F.pen_line(c, keep, w=7)
        F.sparkle(c, curve[-1][0], curve[-1][1], 30)


def sh_baghdad(t):         # "And that pen drew a line, through Baghdad's House of Wisdom, where al-Khwarizmi gave us algebra, and the algorithm!"
    t0 = P('l8', 0)
    c = shade(footage(24632, t - t0, 0.2, 0.5, 0.5, 1.12, 1.0, 7.0, drift=(0.03, 0)), 0.5, 0.85)
    kl = e_inout_cubic(prog(t, t0, t0 + 1.4))
    if kl > 0:
        _partial_line(c, [(-20, 380), (300, 330), (600, 420), (1100, 300)], kl)
    tag_in(c, 'BAGHDAD · 9TH CENTURY', t, P('l8', 1))
    pop_in(c, P3('astrolabe'), 800, 650, 0.85, t, P('l8', 1) + 0.35)
    tw = P('l8', 1) + 0.35
    if glass_in(c, W / 2, 1100, 900, 300, t, tw) >= 1:
        k = prog(t, tw + 0.1, tw + 0.4)
        draw(c, ts('House of Wisdom', PX, 64, WHITE), W / 2, 1010 + (1 - k) * 20, opacity=k)
        ta = P('l8', 2) + PD('l8', 2) * 0.62                 # "algebra"
        ka = prog(t, ta - 0.25, ta + 0.1)
        if ka > 0:
            draw(c, solid(_wmask('الجبر', AR, 96), GOLD), 300, 1150, scale=e_out_back(ka, 2), opacity=ka)
        kb = prog(t, ta, ta + 0.35)
        if kb > 0:
            m = np.zeros((40, 120), np.uint8)
            cv2.line(m, (6, 20), (int(6 + 94 * kb), 20), 255, 6, cv2.LINE_AA)
            if kb > 0.8:
                cv2.fillPoly(m, [np.array([[96, 6], [116, 20], [96, 34]])], 255, cv2.LINE_AA)
            draw(c, solid(m.astype(np.float32) / 255, WHITE), 500, 1160)
            s = ts('algebra', PX, 76, TEAL)
            draw(c, s, 720, 1150, scale=e_out_back(prog(t, ta + 0.2, ta + 0.5), 2), opacity=prog(t, ta + 0.2, ta + 0.4))
    chip_in(c, 'al-Khwārizmī', 300, 1340, t, P('l8', 2) + 0.2, fill=GOLD, ink=GREEN_D, size=44, rot=-3)
    chip_in(c, 'Algoritmi', 640, 1440, t, P('l8', 3), fill=(1, 1, 1, 0.92), ink=GREEN_D, size=38, rot=2)
    chip_in(c, 'algorithm', 870, 1520, t, P('l8', 3) + 0.35, fill=TEAL, size=38, rot=-2)
    caption(c, t, cap_rows([[('l8', 1, "through Baghdad's House of Wisdom,", {'house', 'of', 'wisdom'})]]), size=66, y=1700)
    return c


def sh_fez(t):             # "To Fez, where Fatima al-Fihri founded al-Qarawiyyin, in 859. And it's still teaching today!"
    t0 = P('l9', 0)
    c = shade(footage(45772, t - t0, 0.25, 0.5, 0.5, 1.0, 1.1, 7.0), 0.42, 0.9)
    tag_in(c, 'FEZ · 859 CE', t, P('l9', 2))
    F.glow(c, W / 2, 760, 330, GOLD, 0.3 * prog(t, t0, t0 + 0.4))
    pop_in(c, P3('arch'), W / 2, 760, 0.95, t, t0 + 0.05, tilt=True)
    d1 = P('l9', 1)
    chip_in(c, 'Fatima al-Fihri', 300, 1120, t, d1 + PD('l9', 1) * 0.12, fill=MAG, size=46, rot=-3)
    chip_in(c, 'al-Qarawiyyin', 780, 1200, t, d1 + PD('l9', 1) * 0.6, fill=TEAL, size=46, rot=2)
    ts_ = P('l9', 3)
    if glass_in(c, W / 2, 1400, 760, 120, t, ts_, r=60) >= 1:
        blink = 0.6 + 0.4 * math.sin(t * 6)
        draw(c, rrect(22, 22, 11, GREEN), W / 2 - 300, 1400, opacity=blink)
        yrs = int(1167 * e_out_cubic(prog(t, ts_ + 0.1, ts_ + 1.0)))
        draw(c, ts('Still teaching · %s years' % format(yrs, ','), PX, 46, WHITE), W / 2 + 20, 1400)
        source_in(c, 'Guinness World Records', t, ts_ + 0.4)
    caption(c, t, cap_rows([[('l9', 3, "And it's still teaching today!", {'today'}, {'teaching'})]]), size=66, y=1640)
    return c


def sh_manc(t):            # "And to Manchester, 1843, where this building opened as Lancashire Independent College."
    t0 = P('l10', 0)
    tl = t - t0
    old = still('BMHC-Year-1855-before-photography.jpg', tl, 0.5, 0.4, 1.0, 1.08, 6.0, mono=True, grade=False)
    new = still('Dut-kbsW4AIRs6T.jpg', tl, 0.5, 0.4, 1.0, 1.08, 6.0)
    kw = e_inout_cubic(prog(t, P('l10', 1) + 0.2, P('l10', 2) + 0.4))           # THEN -> NOW wipe along a gold line
    edge = lerp(-500, W + 500, kw)
    lx = edge + (_Y - H / 2) * 0.25
    k = np.clip((_X - lx) / 6 + 0.5, 0, 1)[..., None]
    c = old * k + new * (1 - k)
    if 0 < kw < 1:
        lay = np.zeros((H, W), np.uint8)
        cv2.line(lay, (int((edge - H / 2 * 0.25) * 4), 0), (int((edge + H / 2 * 0.25) * 4), H * 4), 255, 8 * 4, cv2.LINE_AA, shift=2)
        m = lay.astype(np.float32)[..., None] / 255
        c = c + cv2.GaussianBlur(m[..., 0], (0, 0), 18)[..., None] * np.array(GOLD[:3], np.float32) * 0.8
        c = c * (1 - m) + np.array(GOLD[:3], np.float32) * m
    c = shade(c, 0.55, 0.85)
    tag_in(c, 'MANCHESTER · 1843', t, P('l10', 1))
    chip_in(c, 'THEN', 260, 1180, t, t0 + 0.3, fill=IVORY, ink=GREEN_D, size=40, rot=-3, opacity=1 - 0.6 * kw)
    chip_in(c, 'NOW', 840, 1180, t, P('l10', 2) + 0.3, fill=TEAL, size=40, rot=3)
    caption(c, t, cap_rows([[('l10', 2, 'where this building opened as', set())],
                            [('l10', 2, 'Lancashire Independent College.', {'college'}, {'lancashire'})]]), size=66, y=1560)
    return c


def sh_bmhc(t):            # "Today, it's the British Muslim Heritage Centre."
    t0 = P('l11', 0)
    c = shade(still('476280551_1049256607242153_4186426492440189340_n.jpg', t - t0, 0.5, 0.5, 1.15, 1.0, 3.2), 0.4, 0.88)
    kl = prog(t, t0 + 0.6, t0 + 1.0)
    if kl > 0:
        F.glow(c, W / 2, 900, 380, GREEN_D, 0.5 * kl)
        pop_in(c, LOGO(), W / 2, 900, 0.85, t, t0 + 0.6, ray=False, wobble=False, float_amp=4)
    chip_in(c, 'TODAY', W / 2, 600, t, t0, fill=GOLD, ink=GREEN_D, size=44)
    caption(c, t, cap_rows([[('l11', 0, "Today, it's the British Muslim", set())], [('l11', 0, 'Heritage Centre.', {'heritage', 'centre'})]]),
            size=70)
    return c


PANELS = (('Screenshot-2025-10-26-033526.png', 300, 520, -3, "Qur'an classes", TEAL, 0.5, 0.5),
          ('MAS09785-scaled.jpg', 780, 600, 3, 'Study circles', GREEN, 0.5, 0.45),
          ('487090267_1088144326686714_8941517225088640181_n.jpg', 300, 1050, 2, 'Exhibitions', ORANGE, 0.45, 0.6),
          ('scouts.jpg', 780, 1130, -3, 'Youth clubs', MAG, 0.5, 0.4))


@functools.lru_cache(maxsize=4)
def panel_spr(j):
    name, x, y, rot, label, col, fx, fy = PANELS[j]
    im = F.photo(name, fx=fx, fy=fy, w=440, h=420)
    card = rrect(464, 444, 34, WHITE).copy()
    paste_spr(card, F.sprite_of(im, 26), 232, 222)
    return card


@functools.lru_cache(maxsize=1)
def IVORY_BG():
    c = np.ones((H, W, 3), np.float32) * np.array(IVORY[:3], np.float32)
    return c - R.grid_layer()[:H, :W][..., None] * 0.05


def sh_programmes(t):      # "Qur'an classes, study circles, exhibitions, and youth clubs. Welcoming over 130,000 visitors a year!"
    c = IVORY_BG().copy() + R.dust(t, 0.15) * 0.0
    draw(c, ts('TODAY · BRITISH MUSLIM HERITAGE CENTRE', PS, 28, GREEN_D, 0.14), W / 2, 170)
    for j, (name, x, y, rot, label, col, fx, fy) in enumerate(PANELS):
        tj = P('l11', 1 + j) - 0.05
        pop_in(c, panel_spr(j), x, y, 1.0, t, tj, ray=True, wobble=False, float_amp=5)
        chip_in(c, label, x, y + 230, t, tj + 0.18, fill=col, size=36, rot=rot)
    tv = P('l11', 5)
    k = prog(t, tv, tv + 0.3)
    if k > 0:
        v = int(130 * e_out_cubic(prog(t, tv, tv + PD('l11', 5) * 0.8)))
        s = ts('%dK+' % v, PB, 150, GREEN_D, 0.0)
        draw(c, s, W / 2, 1540, scale=e_out_back(k, 2))
        draw(c, ts('VISITORS EVERY YEAR', PX, 36, TEAL, 0.25), W / 2, 1650, opacity=k)
        F.bars(c, W / 2 - 200, 1730, 400 * e_out_cubic(k), 10, 8)
    return c


def sh_oneword(t):         # "It all began with one word. So, what will you read next?"
    t0 = P('l12', 0)
    c = shade(footage(6049, t - t0, 0.3, 0.5, 0.55, 1.0, 1.1, 5.0), 0.35, 0.92)
    tw = P('l12', 0) + PD('l12', 0) * 0.7
    F.glow(c, 860, 300, 220, TEAL, 0.3 * prog(t, tw, tw + 0.4))
    pop_in(c, P3('star'), 860, 300, 0.5, t, tw, wobble=True)
    caption(c, t, cap_rows([[('l12', 0, 'It all began with', set())], [('l12', 0, 'one word.', {'one'}, {'word'})]]), size=84,
            y=1060)
    search_bar(c, ['So, what will you read next?'], t, P('l12', 1), END('l12') - 0.1, 1450, sub='TELL US IN THE COMMENTS')
    return c


def sh_cta(t):             # "Find a class at bmhc.org.uk"
    t0 = P('l13', 0)
    c = SACRED_BG().copy()
    F.glow(c, W / 2, 700, 420, TEAL, 0.18)
    pop_in(c, LOGO(), W / 2, 640, 0.95, t, t0 - 0.2, ray=False, wobble=False, float_amp=4)
    k = prog(t, t0 + 0.2, t0 + 0.5)
    if k > 0:
        draw(c, ts('Find a class at', PM, 52, (1, 1, 1, 0.9)), W / 2, 1020 + (1 - k) * 20, opacity=k)
    tu = P('l13', 1)
    ku = prog(t, tu, tu + 0.35)
    if ku > 0:
        e = e_out_back(ku, 2.2) * (1 + 0.03 * math.sin((t - tu) * 5))
        btn = rrect(720, 120, 60, GOLD).copy()
        paste_spr(btn, ts('bmhc.org.uk', PB, 64, GREEN_D), 360, 60)
        draw(c, blur_sprite(tint(btn, (0, 0.05, 0.04)), 20), W / 2 + 8, 1162, scale=e, opacity=0.4)
        draw(c, btn, W / 2, 1140, scale=e)
        rays(c, W / 2, 1140, 380, prog(t, tu, tu + 0.5))
    for j, ln in enumerate(('College Road, Whalley Range', 'Manchester M16 8BP')):
        kk = prog(t, tu + 0.4 + j * 0.12, tu + 0.8 + j * 0.12)
        if kk > 0:
            draw(c, ts(ln, PM, 36, (1, 1, 1, 0.75), 0.04), W / 2, 1330 + j * 56, opacity=kk)
    for j, (txt, col) in enumerate((('Learn', TEAL), ('Meet', MAG), ('Belong', GREEN))):
        chip_in(c, txt, W / 2 - 290 + j * 290, 1560, t, tu + 0.7 + j * 0.15, fill=col, size=38)
    R.burst(c, W / 2, 1140, t, tu + 0.1, seed=11, n=26, speed=1000, size=0.9)
    return c


def shots():
    return [(0.0, P('l1', 1), sh_walk), (P('l1', 1), P('l2', 0), sh_gates), (P('l2', 0), P('l3', 0), sh_building),
            (P('l3', 0), P('l4', 0), sh_question), (P('l4', 0), P('l5', 0), sh_guess), (P('l5', 0), SACRED[0], sh_iqra),
            (SACRED[0], P('l7', 0) - 0.3, sh_verse), (P('l7', 0) - 0.3, SACRED[1], sh_pen), (SACRED[1], P('l9', 0), sh_baghdad),
            (P('l9', 0), P('l10', 0), sh_fez), (P('l10', 0), P('l11', 0), sh_manc), (P('l11', 0), P('l11', 1), sh_bmhc),
            (P('l11', 1), P('l12', 0), sh_programmes), (P('l12', 0), P('l13', 0) - 0.15, sh_oneword), (P('l13', 0) - 0.15, 999, sh_cta)]


SHOTS = None


# ------------------------------------------------------------------ transitions
def tr_whip(a, b, p, axis=1):
    return R.whip(a, b, p, axis)


def tr_zoom(a, b, p):
    e = e_in_cubic(min(1, p * 1.6))
    za = 1 + 0.6 * e
    A = cv2.warpAffine(a, np.float32([[za, 0, (1 - za) * W / 2], [0, za, (1 - za) * H / 2]]), (W, H), borderMode=cv2.BORDER_REFLECT)
    zb = 1.25 - 0.25 * e_out_cubic(clamp(p * 1.4 - 0.3))
    B = cv2.warpAffine(b, np.float32([[zb, 0, (1 - zb) * W / 2], [0, zb, (1 - zb) * H / 2]]), (W, H), borderMode=cv2.BORDER_REFLECT)
    k = clamp((p - 0.35) / 0.3)
    out = A * (1 - k) + B * k
    blur = int(1 + 30 * math.sin(math.pi * p))
    if blur > 2:
        out = cv2.addWeighted(out, 0.6, cv2.blur(out, (blur, blur)), 0.4, 0)
    return out


def tr_bars(a, b, p):
    """The logo's four colour bars sweep up the screen and reveal the next shot."""
    out = a.copy()
    seg = W / 4
    for j, col in enumerate(BARS):
        pj = clamp((p - j * 0.08) / 0.68)
        top = lerp(H, -H * 0.3, e_inout_cubic(pj))
        x0, x1 = int(j * seg), int((j + 1) * seg)
        yb, yt = int(clamp(top + H * 0.3, 0, H)), int(clamp(top, 0, H))
        out[yb:, x0:x1] = b[yb:, x0:x1]
        out[yt:yb, x0:x1] = np.array(col[:3], np.float32)
    return out


def tr_circle(a, b, p):
    """A gold ring opens onto the next shot."""
    r = e_in_cubic(p) * 1300
    d = np.sqrt((_X - W / 2) ** 2 + (_Y - H / 2) ** 2)
    hole = np.clip((r - 70 - d) / 2, 0, 1)[..., None]
    disk = np.clip((r - d) / 2, 0, 1)[..., None]
    return a * (1 - disk) + np.array(GOLD[:3], np.float32) * (disk - hole) + b * hole


def tr_flash(a, b, p):
    k = 1 - abs(p - 0.5) * 2
    return (a if p < 0.5 else b) * (1 - k) + k * np.array([1.0, 0.96, 0.88], np.float32)


def tr_dissolve(a, b, p):
    e = e_inout_cubic(p)
    return a * (1 - e) + b * e


def tr_ink(a, b, p):
    """Soft radial ink-bleed reveal from the bottom (used out of the sacred section)."""
    d = np.sqrt((_X - W / 2) ** 2 + (_Y - H * 1.05) ** 2)
    r = e_inout_cubic(p) * 2300
    k = np.clip((r - d) / 160, 0, 1)[..., None]
    return a * (1 - k) + b * k


# per cut: (kind, duration)
TRANS = [(lambda a, b, p: tr_whip(a, b, p, 1), 0.32), (tr_zoom, 0.36), (tr_bars, 0.5), (tr_flash, 0.26), (tr_circle, 0.4),
         (tr_dissolve, 1.0), (tr_dissolve, 0.8), (tr_ink, 0.9), (lambda a, b, p: tr_whip(a, b, p, 1), 0.32), (tr_zoom, 0.36),
         (tr_bars, 0.5), (tr_flash, 0.26), (tr_zoom, 0.36), (tr_circle, 0.45)]


def shot_at(t):
    for a, b, f in SHOTS:
        if a <= t < b:
            return f
    return SHOTS[-1][2]


def hits():
    hs = [(P('l1', 1), 0.7, 0), (P('l2', 0), 0.6, 0), (P('l2', 1) + PD('l2', 1) * 0.55, 0.6, 0), (P('l3', 0), 0.6, 0),
          (P('l4', 4), 0.5, 0), (P('l5', 0) + 0.4, 1.0, 10), (P('l5', 1), 0.8, 0), (P('l8', 1) + 0.35, 0.7, 0),
          (P('l9', 0) + 0.05, 0.8, 0), (P('l9', 3), 0.6, 0), (P('l10', 2) + 0.3, 0.6, 0), (P('l11', 0) + 0.6, 0.8, 0),
          (P('l11', 5), 0.9, 8), (P('l12', 0) + PD('l12', 0) * 0.7, 0.7, 0), (P('l13', 1), 1.0, 6)]
    hs += [(P('l4', j), 0.45, 4) for j in range(4)]
    hs += [(P('l11', 1 + j) - 0.05, 0.5, 4) for j in range(4)]
    return hs


HITS = None


def energy(t):
    z, sx, sy, ca = 1.0, 0.0, 0.0, 0.0
    for th, pn, sh in HITS:
        d = t - th
        if 0 <= d < 0.32:
            e = (1 - d / 0.32) ** 2
            z += 0.045 * pn * e
            ca = max(ca, 5 * pn * e)
            if sh:
                sx += sh * e * math.sin(t * 97 + th)
                sy += sh * e * math.cos(t * 83 + th)
    return z, sx, sy, ca


def light_leak(c, t):
    for tc in [P('l1', 1), P('l3', 0), P('l5', 0), P('l9', 0), P('l11', 0), P('l13', 0)]:
        d = t - tc + 0.25
        if 0 <= d < 0.9:
            k = d / 0.9
            x = lerp(-300, W + 300, k)
            g = np.exp(-(((_X - x) / 380) ** 2 + ((_Y - H * 0.35) / 900) ** 2))[..., None] * math.sin(math.pi * k)
            c = c + g * np.array([1.0, 0.7, 0.3], np.float32) * 0.4
    return c


def render_raw(t):
    global SHOTS, HITS
    if SHOTS is None:
        SHOTS = shots()
        HITS = hits()
    c = None
    for j, (a, b, f) in enumerate(SHOTS[1:]):
        kind, td = TRANS[j]
        d = t - (a - td / 2)
        if 0 <= d < td:
            prev = SHOTS[j][2](min(t, a - 0.01))
            nxt = f(max(t, a))
            c = kind(prev, nxt, d / td)
    if c is None:
        c = shot_at(t)(t)
    sacred = SACRED[0] - 0.4 < t < SACRED[1] + 0.3
    if not sacred and t < P('l13', 0) - 0.4:
        progress_bar(c, t)
    c = light_leak(c, t)
    z, sx, sy, _ = energy(t)
    if z > 1.001 or abs(sx) + abs(sy) > 0.5:
        M = np.float32([[z, 0, (1 - z) * W / 2 + sx], [0, z, (1 - z) * H / 2 + sy]])
        c = cv2.warpAffine(c, M, (W, H), borderMode=cv2.BORDER_REFLECT)
    if t > DUR - FADE:
        c = c * (1 - 0.6 * e_inout_cubic(prog(t, DUR - FADE, DUR)))
    return c


def render(fi):
    t = fi / FPS
    c = render_raw(t)
    _, _, _, ca = energy(t)
    return post(c, fi, bloom=0.12, grain=0.013, vig=0.3, ca=ca)


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
            cv2.imwrite(p, to_u8(render(fi)), [cv2.IMWRITE_JPEG_QUALITY, 96])
            print('frame', fi, flush=True)
    elif mode == 'times':
        print('DUR', DUR, 'NF', NF, 'SACRED', SACRED)
        for k in ORDER:
            print(k, [round(P(k, i), 2) for i in range(len(INFO['phrases'][k]))])
