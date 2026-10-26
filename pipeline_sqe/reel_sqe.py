"""IC London — "What Is the SQE?" (story version, 9:16). Real people footage + word-synced 3D pop-ups.

London goes to work (law, HR, finance) -> an aspiring solicitor is confused by the SQE -> it is simplified step by step
-> the story ends at the court, qualified -> IC London CTA. Every key word pops its object; cuts land on the words.

Usage: python3 reel_sqe.py still 1.0,5.0 | python3 reel_sqe.py range 0 1140
"""
import os, sys, math, json, glob, functools
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, '..', 'pipeline_sol'))
import numpy as np
import cv2
import frames_people as FP
import frames_story as FS
from frames_people import (prop, last, ice_bg, R, draw, blur_sprite, tint, rrect, ts, wspr, solid, paste_spr, _wmask,
                           load_png_sprite, NAVY, RED, RED_L, WHITE_, INK, GREY, LINE, F9, F8, F7, F6, hexc, SOL, SQ, W, H)
from engine import prog, clamp, lerp, e_out_back, e_out_cubic, e_in_cubic, e_inout_cubic, draw3d, post

FPS = 30
S = SQ
INFO = json.load(open(f'{S}/tts/lines/info.json'))
ORDER = ['l1', 'l2', 'l3', 'l4', 'l5', 'l6', 'l7', 'l8']
VO = {}
_t = 0.35
for _k in ORDER:
    VO[_k] = round(_t, 3)
    _t += INFO['dur'][_k] + 0.12
DUR = round(_t + 1.25, 2)
NF = int(DUR * FPS)
FADE = 1.0


def P(line, i):
    return VO[line] + INFO['phrases'][line][i][0]


def PD(line, i):
    return INFO['phrases'][line][i][1]


_Y, _X = R._Y, R._X


# ------------------------------------------------------------------ footage playback
class Clip:
    def __init__(self, cid):
        self.path = f'{S}/clips/{cid}.mp4'
        self.cap = cv2.VideoCapture(self.path)
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


def footage(cid, tl, start_frac=0.2, fx=0.5, fy=0.5, z0=1.0, z1=1.08, dur=3.0, drift=(0, 0)):
    """Cover-crop a playing clip to 9:16 with a slow push-in, graded."""
    if cid not in _clips:
        _clips[cid] = Clip(cid)
    c = _clips[cid]
    im = c.frame(start_frac * c.n / c.fps + tl)
    im = im[..., ::-1].astype(np.float32) / 255.0
    ih, iw = im.shape[:2]
    k = clamp(tl / dur)
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
    return FP.grade(out)


def shade(c, bottom=0.55, top=0.22):
    return FP.bottom_shade(FP.top_shade(c, top), bottom)


# ------------------------------------------------------------------ animated pieces
def pop_in(c, spr, x, y, sc, t, t0, rays=True, wobble=True, tilt=False, float_amp=10):
    """Object pops in on its word: overshoot scale, burst rays, then a gentle float (and 3D tilt for flat props)."""
    k = prog(t, t0, t0 + 0.38)
    if k <= 0:
        return
    e = e_out_back(k, 2.4)
    bob = float_amp * math.sin((t - t0) * 2.4)
    rot = (1 - k) * -18 + (3 * math.sin((t - t0) * 1.7) if wobble else 0)
    yy = y + bob + (1 - e_out_cubic(k)) * 60
    if rays:
        kr = prog(t, t0, t0 + 0.45)
        if 0 < kr < 1:
            lay = np.zeros((H, W), np.uint8)
            r0 = max(spr.shape[:2]) * sc * 0.45 + 30 * kr
            for j in range(10):
                a = j / 10 * 2 * math.pi + 0.3
                cv2.line(lay, (int((x + math.cos(a) * r0) * 4), int((yy + math.sin(a) * r0) * 4)),
                         (int((x + math.cos(a) * (r0 + 40 * (1 - kr))) * 4), int((yy + math.sin(a) * (r0 + 40 * (1 - kr))) * 4)),
                         255, 5 * 4, cv2.LINE_AA, shift=2)
            m = lay.astype(np.float32)[..., None] / 255 * (1 - kr)
            c[:] = c * (1 - m) + np.array(WHITE_[:3], np.float32) * m
    draw(c, blur_sprite(tint(spr, (0.0, 0.02, 0.1)), 22), x + 12, yy + 30, scale=sc * e, rot=rot, opacity=0.45 * min(1, k * 2))
    if tilt:
        ry = 22 * math.sin((t - t0) * 1.6) * min(1, k)
        draw3d(c, spr, x, yy, 0, spr.shape[1] * sc * e, None, ry=ry, rx=6 * math.sin((t - t0) * 1.2))
    else:
        draw(c, spr, x, yy, scale=sc * e, rot=rot, opacity=min(1, k * 2.5))


def chip_in(c, text, x, y, t, t0, fill=RED, ink=WHITE_, size=40, rot=0, font=F9):
    k = prog(t, t0, t0 + 0.3)
    if k <= 0:
        return
    s = ts(text, font, size, ink, 0.04)
    p = rrect(s.shape[1] + 56, s.shape[0] + 34, (s.shape[0] + 34) / 2, fill).copy()
    paste_spr(p, s, p.shape[1] / 2, p.shape[0] / 2)
    e = e_out_back(k, 2.6)
    draw(c, blur_sprite(tint(p, (0, 0, 0.1)), 12), x + 6, y + 12, scale=e, rot=rot, opacity=0.5 * k)
    draw(c, p, x, y + 4 * math.sin((t - t0) * 2.2), scale=e, rot=rot * (0.4 + 0.6 * k), opacity=min(1, k * 3))


@functools.lru_cache(maxsize=8)
def pillar_card(label):
    m = np.zeros((220, 160), np.uint8)
    cv2.fillPoly(m, [np.array([[80, 6], [150, 70], [10, 70]], np.int32)], 255, cv2.LINE_AA)
    b = np.zeros((220, 160), np.uint8)
    cv2.rectangle(b, (10, 80), (150, 200), 255, -1)
    cv2.circle(b, (80, 140), 36, 0, -1, cv2.LINE_AA)
    em = R.over_spr(solid(m.astype(np.float32) / 255, NAVY), solid(b.astype(np.float32) / 255, RED))
    s = ts(label, F9, 54, NAVY, 0.04)
    w = int(140 + s.shape[1])
    card = rrect(w, 130, 30, (1, 1, 1, 0.96)).copy()
    paste_spr(card, cv2.resize(em, (64, 88), interpolation=cv2.INTER_AREA), 60, 65)
    paste_spr(card, s, 110 + s.shape[1] / 2, 65)
    return card


@functools.lru_cache(maxsize=1)
def qualified_card():
    s = ts('QUALIFIED SOLICITOR', F9, 46, WHITE_, 0.06)
    p = rrect(s.shape[1] + 130, 104, 52, RED).copy()
    paste_spr(p, R.check(70), 56, 52)
    paste_spr(p, s, 100 + s.shape[1] / 2, 52)
    return p


@functools.lru_cache(maxsize=1)
def chart_card():
    return FS.chart_spr()


def seq3d(name, tl, fps=24, loop=True):
    fs = sorted(glob.glob(f'{SOL}/assets/{name}/*.png'))
    i = int(tl * fps)
    i = i % len(fs) if loop else min(max(i, 0), len(fs) - 1)
    return _spr(fs[i])


@functools.lru_cache(maxsize=160)
def _spr(path):
    return load_png_sprite(path)


@functools.lru_cache(maxsize=16)
def P3(name):
    return prop(name)


def caption(c, t, rows, size=84, y=None, maxw=960):
    """Rows of (word, key, t_on), re-wrapped to fit. Words rise in as spoken; key words get a red marker underline."""
    words = [w for row in rows for w in row]
    if not words:
        return
    breaks = set()
    acc = 0
    for row in rows[:-1]:
        acc += len(row)
        breaks.add(acc)
    lay_rows, cur, x = [], [], 108                  # wrap: honour the given row breaks, add more if too wide
    for i, (w, key, ton) in enumerate(words):
        wd = wspr(w, F9, size, WHITE_).shape[1]
        if cur and (i in breaks or x + wd > maxw + 108):
            lay_rows.append(cur)
            cur, x = [], 108
        cur.append((w, key, ton, x))
        x += wd + size * 0.16
    lay_rows.append(cur)
    n = len(lay_rows)
    y0 = y if y is not None else 1780 - (n - 1) * size * 1.15 - size * 0.4
    y0 = min(y0, 1780 - (n - 1) * size * 1.15 - size * 0.4)
    kb = prog(t, words[0][2] - 0.1, words[0][2] + 0.15)
    if kb <= 0:
        return
    draw(c, rrect(12, (size * 1.15 * n + 10) * e_out_cubic(kb), 6, RED), 70, y0 + (n - 1) * size * 0.575)
    for li, row in enumerate(lay_rows):
        yy = y0 + li * size * 1.15
        for w, key, ton, x in row:
            s = wspr(w, F9, size, WHITE_)
            k = prog(t, ton, ton + 0.22)
            if k <= 0:
                continue
            if key:
                ku = prog(t, ton + 0.1, ton + 0.4)
                if ku > 0:
                    lay = np.zeros((H, W), np.uint8)
                    pts = [(x + 4 + (s.shape[1] - 8) * u, yy + size * 0.42 + 5 * math.sin(u * 6)) for u in np.linspace(0, ku, 24)]
                    cv2.polylines(lay, [(np.array(pts) * 4).astype(np.int32)], False, 255, int(size * 0.16) * 4, cv2.LINE_AA, shift=2)
                    m = lay.astype(np.float32)[..., None] / 255
                    c[:] = c * (1 - m) + np.array(RED[:3], np.float32) * m
            e = e_out_cubic(k)
            draw(c, blur_sprite(tint(s, (0, 0, 0)), 10), x + s.shape[1] / 2 + 3, yy + 6 + (1 - e) * 30, opacity=0.45 * k)
            draw(c, s, x + s.shape[1] / 2, yy + (1 - e) * 30, opacity=min(1, k * 2))


def cap_rows(spec):
    """spec: list of rows; each row a list of (line, phrase_idx, 'words', {keywords}). Word times spread over the phrase."""
    rows = []
    for row in spec:
        out = []
        for line, pi, words, keys in row:
            ws = words.split(' ')
            t0, d = P(line, pi), PD(line, pi)
            total = sum(len(w) + 1 for w in ws)
            acc = 0
            for w in ws:
                out.append((w, w.strip(',.!?:').lower() in keys, t0 + d * 0.75 * acc / total))
                acc += len(w) + 1
        rows.append(out)
    return rows


# ------------------------------------------------------------------ shots
def sh_london(t):          # "Every morning, London goes to work."
    c = shade(footage(4169, t, 0.15, 0.55, 0.45, 1.12, 1.0, P('l2', 0)))
    FP.logo_badge(c)
    k = prog(t, 0.25, 0.6)
    if k > 0:
        FS.doc_tag(c, 'LONDON  ·  08:00', x=80 - (1 - e_out_cubic(k)) * 300, y=290)
    caption(c, t, cap_rows([[('l1', 0, 'Every morning,', set())], [('l1', 1, 'London goes to work.', {'london'})]]))
    return c


def sh_law(t):             # "Into courtrooms,"
    t0 = P('l2', 0)
    c = shade(footage(12315, t - t0, 0.3, 0.45, 0.4, 1.0, 1.12, 1.4))
    FP.logo_badge(c)
    pop_in(c, pillar_card('LAW'), 760, 520, 1.0, t, t0 + 0.05, wobble=False)
    pop_in(c, seq3d('ic_scales', t - t0), 760, 900, 0.8, t, t0 + 0.2)
    caption(c, t, cap_rows([[('l2', 0, 'Into courtrooms,', {'courtrooms'})]]))
    return c


def sh_hr(t):              # "boardrooms,"
    t0 = P('l2', 1)
    c = shade(footage(5520, t - t0, 0.4, 0.3, 0.45, 1.05, 1.15, 1.2))
    FP.logo_badge(c)
    pop_in(c, pillar_card('HR'), 770, 1000, 1.0, t, t0 + 0.02, wobble=False)
    pop_in(c, seq3d('ic_briefcase', t - t0), 820, 1290, 0.62, t, t0 + 0.15)
    caption(c, t, cap_rows([[('l2', 1, 'boardrooms,', {'boardrooms'})]]))
    return c


def sh_fin(t):             # "and trading floors."
    t0 = P('l2', 2)
    c = shade(footage(9607, t - t0, 0.3, 0.5, 0.5, 1.15, 1.0, 1.6, drift=(0.05, 0)))
    FP.logo_badge(c)
    pop_in(c, pillar_card('FINANCE'), 640, 500, 1.0, t, t0 + 0.02, wobble=False)
    pop_in(c, chart_card(), 600, 900, 0.95, t, t0 + 0.25, tilt=True)
    caption(c, t, cap_rows([[('l2', 2, 'and trading floors.', {'trading', 'floors'})]]))
    return c


def sh_think(t):           # "Thinking of law?"
    t0 = P('l3', 0)
    c = shade(footage(15923, t - t0, 0.2, 0.5, 0.4, 1.0, 1.1, 1.6))
    FP.logo_badge(c)
    pop_in(c, seq3d('qmark', t - t0 - 0.15, loop=False), 820, 520, 0.62, t, t0 + 0.15)
    pop_in(c, pillar_card('LAW'), 300, 560, 0.9, t, t0 + 0.55, wobble=False)
    caption(c, t, cap_rows([[('l3', 0, 'Thinking of law?', {'law'})]]))
    return c


CHIPS = [('SQE1', 200, 520, -10, RED), ('FLK', 860, 470, 8, NAVY), ('QWE', 900, 820, -6, RED), ('SRA', 170, 860, 7, NAVY),
         ('MCQ', 760, 1080, 5, NAVY), ('SQE2', 260, 1160, -6, RED)]


def sh_confused(t):        # "Confused about the SQE? Let's simplify it!"
    t0, t1 = P('l4', 0), P('l4', 1)
    c = shade(footage(28321, t - t0, 0.3, 0.42, 0.5, 1.0, 1.1, 3.4), 0.5)
    FP.logo_badge(c)
    ks = e_inout_cubic(prog(t, t1 + 0.1, t1 + 0.7))       # chips line up on one clean line
    if ks > 0:
        lay = np.zeros((H, W), np.uint8)
        cv2.line(lay, (90, 1250), (int(90 + 900 * ks), 1250), 255, 10, cv2.LINE_AA)
        m = lay.astype(np.float32) / 255
        c = c + cv2.GaussianBlur(m, (0, 0), 14)[..., None] * np.array(LINE[:3], np.float32) * 0.9
        c = c * (1 - m[..., None]) + np.array(WHITE_[:3], np.float32) * m[..., None]
    for j, (txt, x, y, rot, col) in enumerate(CHIPS):
        tj = t0 + 0.08 + j * 0.12
        if t < tj:
            continue
        jx = 6 * math.sin(t * 23 + j) * (1 - ks)
        tx, ty = lerp(x, 190 + (j % 4) * 235 if j < 4 else 540 + (j - 4.5) * 240, ks), lerp(y, 1250 if j < 4 else 1360, ks)
        chip_in(c, txt, tx + jx, ty, t, tj, fill=col, rot=rot * (1 - ks))
    kc = prog(t, t1 + 0.6, t1 + 0.9)
    if kc > 0:
        pop_in(c, R.check(150), 900, 1080, 1.0, t, t1 + 0.6)
    caption(c, t, cap_rows([[('l4', 0, 'Confused about the SQE?', {'sqe'})], [('l4', 1, "Let's simplify it!", {'simplify'})]]),
            size=78, y=1580)
    return c


def sh_sqe1(t):            # "SQE one tests your legal knowledge,"
    t0 = P('l5', 0)
    c = shade(footage(9011, t - t0, 0.3, 0.38, 0.45, 1.0, 1.1, 2.6), 0.5)
    FP.logo_badge(c)
    chip_in(c, 'SQE1', 840, 330, t, t0, fill=RED, size=76)
    pop_in(c, seq3d('bulb', t - P('l5', 1)), 230, 620, 0.5, t, P('l5', 1) - 0.05)
    chip_in(c, 'LEGAL KNOWLEDGE', 330, 880, t, P('l5', 1) + 0.25, fill=(1, 1, 1, 1), ink=INK, size=34)
    caption(c, t, cap_rows([[('l5', 0, 'SQE1', {'sqe1'}), ('l5', 1, 'tests your', set())], [('l5', 1, 'legal knowledge,', {'legal', 'knowledge'})]]))
    return c


def sh_exams(t):           # "across two multiple-choice exams."
    t0 = P('l5', 2)
    c = shade(footage(50126, t - t0, 0.35, 0.42, 0.5, 1.05, 1.15, 2.2), 0.5)
    FP.logo_badge(c)
    pop_in(c, P3('papers'), 260, 500, 0.5, t, t0 + 0.05, tilt=True)
    for j, l in enumerate('ABCDE'):
        tj = t0 + 0.5 + j * 0.07
        k = prog(t, tj, tj + 0.25)
        if k <= 0:
            continue
        x = 230 + j * 155
        on = l == 'C' and t > t0 + 1.0
        draw(c, rrect(96, 96, 48, RED if on else (1, 1, 1, 1)), x, 1320, scale=e_out_back(k, 2.6))
        draw(c, ts(l, F9, 44, WHITE_ if on else NAVY), x, 1320, scale=e_out_back(k, 2.6))
    caption(c, t, cap_rows([[('l5', 2, 'across two multiple-choice exams.', {'two', 'multiple-choice'})]]), size=74)
    return c


SKILLS = [(15858, 290, 560, 'speech', 'Client interviews', 0.4), (22961, 790, 560, 'lectern', 'Advocacy', 0.45),
          (50722, 290, 1150, 'magnifier', 'Research', 0.3), (17049, 790, 1150, 'pen', 'Drafting', 0.55)]


def sh_sqe2(t):            # "SQE two tests practical skills: client interviews, advocacy, research, and drafting."
    t0 = P('l6', 0)
    c = np.ones((H, W, 3), np.float32) * np.array(hexc('#071233')[:3], np.float32)
    c = c + R.grid_layer()[:H, :W][..., None] * 0.35 * np.array(LINE[:3], np.float32) + R.dust(t, 0.3)
    FP.logo_badge(c)
    chip_in(c, 'SQE2', 880, 105, t, t0, fill=RED, size=60)
    pw, ph_ = 470, 540
    for j, (cid, x, y, icon_, lab, fx) in enumerate(SKILLS):
        tj = P('l6', 2 + j) - 0.05
        k = prog(t, tj, tj + 0.35)
        if k <= 0:
            continue
        im = footage(cid, t - tj, 0.35, fx, 0.5, 1.0, 1.08, 3.0)
        im = cv2.resize(im, (pw, int(pw * H / W)))[int((pw * H / W - ph_) / 2):][:ph_]
        spr = np.concatenate([im, np.ones((ph_, pw, 1), np.float32)], 2)
        m = R.sdf_fill(R.rrect_alpha(pw, ph_, 26, 2))
        m = cv2.resize(m, (pw, ph_))[..., None]
        spr = spr * m
        e = e_out_back(k, 1.8)
        draw(c, blur_sprite(tint(spr, (0, 0, 0.1)), 16), x + 8, y + 18, scale=e, opacity=0.45 * k)
        draw(c, spr, x, y, scale=e, rot=(1 - k) * (8 if j % 2 else -8))
        if k >= 1:
            bx_, by_ = x + pw / 2 - 70, y - ph_ / 2 + 70
            pop_in(c, rrect(124, 124, 62, WHITE_), bx_, by_, 1.0, t, tj + 0.25, rays=True, wobble=False, float_amp=0)
            kk = prog(t, tj + 0.25, tj + 0.6)
            if kk > 0:
                draw(c, P3(icon_), bx_, by_, scale=0.2 * e_out_back(kk, 2.4))
            s = ts(lab, F8, 34, INK)
            draw(c, rrect(s.shape[1] + 44, 64, 32, (1, 1, 1, 1)), x - pw / 2 + 30 + (s.shape[1] + 44) / 2, y + ph_ / 2 - 54)
            draw(c, s, x - pw / 2 + 30 + (s.shape[1] + 44) / 2, y + ph_ / 2 - 54)
    caption(c, t, cap_rows([[('l6', 0, 'SQE2', {'sqe2'}), ('l6', 1, 'tests practical', {'practical'})], [('l6', 1, 'skills.', {'skills'})]]),
            size=80, y=1600)
    return c


def sh_degree(t):          # "Add a degree,"
    t0 = P('l7', 0)
    c = shade(footage(12820, t - t0, 0.3, 0.5, 0.4, 1.0, 1.1, 1.6))
    FP.logo_badge(c)
    pop_in(c, seq3d('cap', t - t0), 780, 560, 0.62, t, t0 + 0.1)
    chip_in(c, 'DEGREE  ·  ANY SUBJECT', 740, 830, t, t0 + 0.4, fill=(1, 1, 1, 1), ink=INK, size=32)
    caption(c, t, cap_rows([[('l7', 0, 'Add a degree,', {'degree'})]]))
    return c


def sh_qwe(t):             # "two years' qualifying work experience,"
    t0 = P('l7', 1)
    c = shade(footage(8873, t - t0, 0.3, 0.66, 0.45, 1.05, 1.15, 2.4))
    FP.logo_badge(c)
    pop_in(c, P3('calendar'), 300, 690, 0.72, t, t0 + 0.05, tilt=True)
    chip_in(c, 'QWE', 300, 990, t, t0 + 0.35, fill=NAVY, size=44)
    caption(c, t, cap_rows([[('l7', 1, "two years' qualifying", {'two', "years'"})], [('l7', 1, 'work experience,', set())]]), size=80)
    return c


def sh_qualify(t):         # "and the SRA's character checks, and you can qualify!"
    t0, t1 = P('l7', 2), P('l7', 3)
    c = shade(footage(16107, t - t0, 0.3, 0.62, 0.45, 1.0, 1.12, 3.4), 0.5)
    FP.logo_badge(c)
    pop_in(c, seq3d('ic_shield', t - t0), 300, 600, 0.75, t, t0 + 0.15)
    chip_in(c, 'CHARACTER & SUITABILITY', 470, 860, t, t0 + 0.45, fill=(1, 1, 1, 1), ink=INK, size=30)
    pop_in(c, qualified_card(), 540, 1200, 1.0, t, t1 + 0.35, wobble=False)
    R.burst(c, 540, 1200, t, t1 + 0.4, seed=9, n=34, speed=1300, size=1.2)
    caption(c, t, cap_rows([[('l7', 2, "and the SRA's character checks,", {'character'})], [('l7', 3, 'and you can qualify!', {'qualify'})]]),
            size=72, y=1600)
    return c


def sh_cta(t):             # "Find out more about SQE preparation, at IC London."
    t0, t1 = P('l8', 0), P('l8', 1)
    c = footage(4457, t - t0, 0.45, 0.42, 0.45, 1.12, 1.0, 4.0)
    c = FP.top_shade(c, 0.3)
    kp = e_inout_cubic(prog(t, t0 + 0.1, t0 + 0.7))
    if kp > 0:
        top = lerp(H + 50, H * 0.42, kp)
        g = np.clip((_Y - top) / 140, 0, 1)[..., None]
        c = c * (1 - g) + ice_bg() * g
    kl = prog(t, t0 + 0.6, t0 + 1.0)
    if kl > 0:
        lg = load_png_sprite(f'{S}/src/logo_full.png')
        pop_in(c, lg, 540, 1000, 1.0, t, t0 + 0.6, rays=False, wobble=False, float_amp=0)
    for j, lab in enumerate(['LAW', 'HR', 'FINANCE']):
        chip_in(c, lab, [300, 540, 790][j], 1270, t, t0 + 0.9 + j * 0.12, fill=RED if j == 0 else NAVY, size=32)
    k1 = prog(t, t0 + 1.1, t0 + 1.4)
    if k1 > 0:
        for li, (words, size, col) in enumerate([(['Find', 'out', 'more', 'about'], 62, INK), (['SQE', 'preparation'], 86, RED)]):
            sprs = [wspr(w, F9, size, col) for w in words]
            total = sum(s.shape[1] for s in sprs) + size * 0.13 * (len(sprs) - 1)
            x = 540 - total / 2
            y = 1420 + li * 100
            for s in sprs:
                draw(c, s, x + s.shape[1] / 2, y + (1 - e_out_cubic(k1)) * 30, opacity=k1)
                x += s.shape[1] + size * 0.13
        FS_title = 'preparation'
    ku = prog(t, t1, t1 + 0.4)
    if ku > 0:
        s = ts('iclondon.co.uk', F7, 46, NAVY)
        draw(c, s, 510, 1660, opacity=ku)
        bx = 510 + s.shape[1] / 2 + 64
        draw(c, rrect(80, 80, 40, RED), bx, 1660, scale=e_out_back(ku, 2.6))
        draw(c, R.arrow_spr(), bx + 4 * math.sin(t * 6), 1660, scale=e_out_back(ku, 2.6))
    pop_in(c, seq3d('cap', t - t0), 880, 720, 0.45, t, t0 + 0.9, rays=False)
    R.burst(c, 540, 1000, t, t0 + 0.65, seed=12, n=30, speed=1100, size=1.0)
    return c


def shots():
    return [(0.0, P('l2', 0), sh_london), (P('l2', 0), P('l2', 1), sh_law), (P('l2', 1), P('l2', 2), sh_hr),
            (P('l2', 2), P('l3', 0), sh_fin), (P('l3', 0), P('l4', 0), sh_think), (P('l4', 0), P('l5', 0), sh_confused),
            (P('l5', 0), P('l5', 2), sh_sqe1), (P('l5', 2), P('l6', 0), sh_exams), (P('l6', 0), P('l7', 0), sh_sqe2),
            (P('l7', 0), P('l7', 1), sh_degree), (P('l7', 1), P('l7', 2), sh_qwe), (P('l7', 2), P('l8', 0), sh_qualify),
            (P('l8', 0), 999, sh_cta)]


SHOTS = None


# ------------------------------------------------------------------ transitions
def tr_whip(a, b, p, axis=1):
    return R.whip(a, b, p, axis)


def tr_zoom(a, b, p):
    """Zoom-through: the outgoing shot rushes into camera, the new one settles in."""
    e = e_in_cubic(min(1, p * 1.6))
    za = 1 + 0.6 * e
    Ma = np.float32([[za, 0, (1 - za) * W / 2], [0, za, (1 - za) * H / 2]])
    A = cv2.warpAffine(a, Ma, (W, H), borderMode=cv2.BORDER_REFLECT)
    zb = 1.25 - 0.25 * e_out_cubic(clamp(p * 1.4 - 0.3))
    Mb = np.float32([[zb, 0, (1 - zb) * W / 2], [0, zb, (1 - zb) * H / 2]])
    B = cv2.warpAffine(b, Mb, (W, H), borderMode=cv2.BORDER_REFLECT)
    k = clamp((p - 0.35) / 0.3)
    out = A * (1 - k) + B * k
    blur = int(1 + 30 * math.sin(math.pi * p))
    if blur > 2:
        out = cv2.addWeighted(out, 0.6, cv2.blur(out, (blur, blur)), 0.4, 0)
    return out


def tr_glitch(a, b, p):
    """Slice glitch with an RGB split."""
    rng = np.random.default_rng(int(p * 20))
    out = (b if p > 0.5 else a).copy()
    for _ in range(9):
        y0 = int(rng.uniform(0, H - 60))
        hh = int(rng.uniform(20, 140))
        dx = int(rng.uniform(-120, 120) * math.sin(math.pi * p))
        out[y0:y0 + hh] = np.roll(out[y0:y0 + hh], dx, 1)
    s = int(14 * math.sin(math.pi * p))
    if s:
        out = np.stack([np.roll(out[..., 0], s, 1), out[..., 1], np.roll(out[..., 2], -s, 1)], 2)
    return out


def tr_circle(a, b, p):
    """A red circle (the emblem's) bursts open onto the next shot."""
    r = e_in_cubic(p) * 1300
    d = np.sqrt((_X - W / 2) ** 2 + (_Y - H / 2) ** 2)
    hole = np.clip((r - 90 - d) / 2, 0, 1)[..., None]
    ring = np.clip((r - d) / 2, 0, 1)[..., None] - hole
    out = a * (1 - np.clip((r - d) / 2, 0, 1)[..., None]) + np.array(RED[:3], np.float32) * ring + b * hole
    return out


def tr_flash(a, b, p):
    k = 1 - abs(p - 0.5) * 2
    return (a if p < 0.5 else b) * (1 - k) + k * np.array([1.0, 0.97, 0.92], np.float32)


TRANS_KINDS = [lambda a, b, p: tr_whip(a, b, p, 1), tr_flash, tr_zoom, lambda a, b, p: tr_whip(a, b, p, 1), tr_glitch, tr_circle,
               tr_zoom, tr_circle, lambda a, b, p: tr_whip(a, b, p, 0), tr_flash, tr_zoom, tr_circle]
TR_DUR = 0.32


def shot_at(t):
    for a, b, f in SHOTS:
        if a <= t < b:
            return f
    return SHOTS[-1][2]


def hits():
    hs = [(P('l2', 0), 0.8, 0), (P('l2', 1), 0.8, 0), (P('l2', 2), 0.8, 0), (P('l3', 0) + 0.15, 0.7, 0),
          (P('l4', 0) + 0.1, 0.6, 8), (P('l4', 1) + 0.6, 0.9, 6), (P('l5', 0), 0.8, 0), (P('l5', 2) + 0.05, 0.7, 0),
          (P('l6', 0), 0.8, 0), (P('l7', 0) + 0.1, 0.6, 0), (P('l7', 1) + 0.05, 0.6, 0), (P('l7', 3) + 0.35, 1.2, 14),
          (P('l8', 0) + 0.6, 0.8, 0)]
    hs += [(P('l6', 2 + j) - 0.05, 0.5, 4) for j in range(4)]
    return hs


HITS = None


def energy(t):
    z, sx, sy, ca = 1.0, 0.0, 0.0, 0.0
    for th, pn, sh in HITS:
        d = t - th
        if 0 <= d < 0.32:
            e = (1 - d / 0.32) ** 2
            z += 0.05 * pn * e
            ca = max(ca, 6 * pn * e)
            if sh:
                sx += sh * e * math.sin(t * 97 + th)
                sy += sh * e * math.cos(t * 83 + th)
    return z, sx, sy, ca


def light_leak(c, t):
    """Warm light leaks drifting across on the bigger cuts."""
    for tc in [P('l3', 0), P('l5', 0), P('l7', 0), P('l8', 0)]:
        d = t - tc + 0.25
        if 0 <= d < 0.9:
            k = d / 0.9
            x = lerp(-300, W + 300, k)
            g = np.exp(-(((_X - x) / 380) ** 2 + ((_Y - H * 0.35) / 900) ** 2))[..., None] * math.sin(math.pi * k)
            c = c + g * np.array([1.0, 0.55, 0.25], np.float32) * 0.45
    return c


def render_raw(t):
    global SHOTS, HITS
    if SHOTS is None:
        SHOTS = shots()
        HITS = hits()
    c = None
    for j, (a, b, f) in enumerate(SHOTS[1:]):
        d = t - (a - TR_DUR / 2)
        if 0 <= d < TR_DUR:
            prev = SHOTS[j][2](min(t, a - 0.01))
            nxt = f(max(t, a))
            c = TRANS_KINDS[j % len(TRANS_KINDS)](prev, nxt, d / TR_DUR)
    if c is None:
        c = shot_at(t)(t)
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
    return post(c, fi, bloom=0.1, grain=0.014, vig=0.3, ca=ca)


def to_u8(im):
    return (np.clip(im, 0, 1) * 255 + 0.5).astype(np.uint8)[..., ::-1]


if __name__ == '__main__':
    mode = sys.argv[1]
    if mode == 'still':
        os.makedirs(f'{S}/stills', exist_ok=True)
        for tt_ in sys.argv[2].split(','):
            t = float(tt_)
            cv2.imwrite(f'{S}/stills/s_{t:05.2f}.jpg', to_u8(render(int(round(t * FPS)))), [cv2.IMWRITE_JPEG_QUALITY, 90])
            print('still', t, flush=True)
    elif mode == 'range':
        a, b = int(sys.argv[2]), int(sys.argv[3])
        os.makedirs(f'{S}/frames_out', exist_ok=True)
        for fi in range(a, b):
            p = f'{S}/frames_out/{fi:04d}.png'
            if os.environ.get('RESUME') and os.path.exists(p):
                continue
            cv2.imwrite(p, to_u8(render(fi)), [cv2.IMWRITE_PNG_COMPRESSION, 1])
            print('frame', fi, flush=True)
    elif mode == 'times':
        print('DUR', DUR, 'NF', NF)
        for k in ORDER:
            print(k, [round(P(k, i), 2) for i in range(len(INFO['phrases'][k]))])
