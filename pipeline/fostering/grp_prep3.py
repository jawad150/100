"""grp_prep3.py: green-screen quads for the Nov 2026 Google Ranker Pro clips (videos 8-10).

python3 grp_prep3.py zentro2     monitor (handheld, hand in front)  -> workspace3/grp/zentro2_quads.json
python3 grp_prep3.py coventry2   laptop, shot 1 (over the shoulder)  -> workspace3/grp/coventry2_quads.json
python3 grp_prep3.py grace       laptop, shot 2 (wide desk shot)     -> workspace3/grp/grace_quads.json

Per frame: robust line fits to the green screen's top / bottom edges (column scans) and its left / right edges
(row scans). A side that is off frame, or hidden by a hand, is rebuilt from the screen's width / height ratio
measured on the frames where both sides are clean (interpolated over time). Then light temporal smoothing.
"""
import json
import os
import sys

import cv2
import numpy as np

import core as K
from grp_prep2 import _frame, _line_fit

OUT = os.path.join(K.WS, 'grp')
W, H = 1080, 1920


def gmask(im, s_min, v_min, h_lo=35, h_hi=90):
    hsv = cv2.cvtColor(im, cv2.COLOR_BGR2HSV)
    h, s, v = [hsv[..., c].astype(np.int32) for c in range(3)]
    m = ((h > h_lo) & (h < h_hi) & (s > s_min) & (v > v_min)).astype(np.uint8)
    return cv2.morphologyEx(m, cv2.MORPH_OPEN, np.ones((5, 5), np.uint8)) > 0


def env_fit(pts, side, tol=3.0, iters=600, viol=0.05, rng=np.random.default_rng(7)):
    """Line through the outer envelope of points. pts (u, v): v = a u + b. side=+1: all points have v <= line
    (line is a lower bound in v, e.g. the bottom edge); side=-1: all points have v >= line (top edge).
    Picks the line with most points within tol among lines that at most `viol` of the points cross."""
    P = np.asarray(pts, np.float64)
    if len(P) < 6:
        return None, 0
    u, v = P[:, 0], P[:, 1]
    best, bn = None, -1
    n = len(P)
    for _ in range(iters):
        i, j = rng.choice(n, 2, replace=False)
        if abs(u[i] - u[j]) < 20:
            continue
        a = (v[j] - v[i]) / (u[j] - u[i])
        b = v[i] - a * u[i]
        r = side * (a * u + b - v)          # >= 0 when the point is on the inner side
        if (r < -tol).mean() > viol:
            continue
        k = (np.abs(r) <= tol).sum()
        if k > bn:
            best, bn = (a, b), k
    if best is None:
        return None, 0
    a, b = best
    r = np.abs(a * u + b - v)
    keep = r <= tol
    if keep.sum() >= 4:
        a, b = np.polyfit(u[keep], v[keep], 1)
    return (float(a), float(b)), int(keep.sum()) / n


def _longest_run(b):
    """(start, end) of the longest run of True in a 1-D bool array."""
    d = np.diff(np.concatenate([[0], b.astype(np.int8), [0]]))
    s, e = np.where(d == 1)[0], np.where(d == -1)[0]
    if not len(s):
        return None
    k = int(np.argmax(e - s))
    return int(s[k]), int(e[k] - 1)


def fit_frame(m, box, step=6, border=4):
    x_lo, x_hi, y_lo, y_hi = box
    top, bot = [], []
    for x in range(x_lo, x_hi, step):
        col = m[y_lo:y_hi, x]
        run = _longest_run(col)
        if run is None or run[1] - run[0] < 40:
            continue
        top.append((x, run[0] + y_lo))
        bot.append((x, run[1] + y_lo))
    if len(top) < 12:
        return None
    lt, ft = env_fit(top, -1)
    lb, fb = env_fit(bot, +1)
    if lt is None or lb is None:
        return None
    xm = 0.5 * (top[0][0] + top[-1][0])
    y0, y1 = lt[0] * xm + lt[1], lb[0] * xm + lb[1]
    left, right = [], []
    for y in np.linspace(y0 + 0.04 * (y1 - y0), y1 - 0.04 * (y1 - y0), 60).astype(int):
        if y < 0 or y >= H:
            continue
        run = _longest_run(m[y])
        if run is not None and run[1] - run[0] > 30:
            left.append((y, run[0]))
            right.append((y, run[1]))
    rec = dict(top=list(lt), bot=list(lb))
    if len(left) > 12:
        ll, fl = env_fit(left, -1)      # x = c y + d, all green has x >= line
        lr, fr = env_fit(right, +1)
        lxs = np.array([p[1] for p in left]); rxs = np.array([p[1] for p in right])
        rec['l_off'] = bool(np.median(lxs) <= border)
        rec['r_off'] = bool(np.median(rxs) >= W - 1 - border)
        if ll is not None and fl > 0.3 and np.median(lxs) > border and ll[0] * 0.5 * (y0 + y1) + ll[1] > border:
            rec['left'] = list(ll)
            rec['lx'] = float(ll[0] * 0.5 * (y0 + y1) + ll[1])
        if lr is not None and fr > 0.3 and np.median(rxs) < W - 1 - border and lr[0] * 0.5 * (y0 + y1) + lr[1] < W - 1 - border:
            rec['right'] = list(lr)
            rec['rx'] = float(lr[0] * 0.5 * (y0 + y1) + lr[1])
    return rec


def _isect(top, side):
    a, b = top
    c, d = side
    y = (a * d + b) / (1 - a * c)
    return [c * y + d, y]


def build(cid, frames, box, s_min=80, v_min=60, border=4, ratio_tol=0.05, smooth=2, left_virtual=None):
    recs = {}
    for i in frames:
        recs[i] = fit_frame(gmask(_frame(cid, i), s_min, v_min), box)
    # width / height ratio at mid height from frames with both sides clean
    ratio = {}
    for i, r in recs.items():
        if r is None or 'lx' not in r or 'rx' not in r:
            continue
        if True:
            xm = 0.5 * (r['lx'] + r['rx'])
            h = (r['bot'][0] * xm + r['bot'][1]) - (r['top'][0] * xm + r['top'][1])
            ratio[i] = (r['rx'] - r['lx']) / h
    if ratio:
        med = np.median(list(ratio.values()))
        good = {i: v for i, v in ratio.items() if abs(v / med - 1) < ratio_tol}
    else:
        good = {}
    gi = np.array(sorted(good))
    gv = np.array([good[i] for i in gi]) if len(gi) else None
    quads = {}
    for i in frames:
        r = recs[i]
        if r is None:
            continue
        rr = float(np.interp(i, gi, gv)) if gv is not None else None
        top, bot = r['top'], r['bot']
        lv = 'lx' in r and left_virtual is None
        rv = 'rx' in r
        if lv and rv and i not in good and rr is not None:
            # one side is hidden: keep the side whose implied ratio is closer
            xm = 0.5 * (r['lx'] + r['rx'])
            h = (bot[0] * xm + bot[1]) - (top[0] * xm + top[1])
            if abs((r['rx'] - r['lx']) / h / rr - 1) > 0.05:
                # one side is wrong (a hand or hair against it): keep the one closer to the previous quad
                lv, rv = (True, False) if r['rx'] < W * 0.92 else (False, True)
        if lv and rv:
            tl, bl = _isect(top, r['left']), _isect(bot, r['left'])
            tr, br = _isect(top, r['right']), _isect(bot, r['right'])
        elif rv:
            tr, br = _isect(top, r['right']), _isect(bot, r['right'])
            h = br[1] - tr[1]
            w = (rr or 1.6) * h if left_virtual is None else (tr[0] - left_virtual)
            xl = tr[0] - w
            if r.get('l_off'):
                xl = min(xl, -15.0)                 # the hidden side is off frame: keep it past the edge
            sl = r['right'][0]
            tl = [xl, top[0] * xl + top[1]]
            bl = [xl + sl * (h * 1.0), bot[0] * (xl + sl * h) + bot[1]]
        elif lv:
            tl, bl = _isect(top, r['left']), _isect(bot, r['left'])
            h = bl[1] - tl[1]
            xr = tl[0] + (rr or 1.6) * h
            if r.get('r_off'):
                xr = max(xr, W + 15.0)
            sr = r['left'][0]
            tr = [xr, top[0] * xr + top[1]]
            br = [xr + sr * h, bot[0] * (xr + sr * h) + bot[1]]
        else:
            continue
        quads[i] = [tl, tr, br, bl]
    ks = sorted(quads)
    arr = np.array([quads[k] for k in ks], np.float64)
    sm = arr.copy()
    for j in range(len(ks)):
        a, b = max(0, j - smooth), min(len(ks), j + smooth + 1)
        sm[j] = np.median(arr[a:b], axis=0)
    sm2 = sm.copy()
    for j in range(len(ks)):
        a, b = max(0, j - 1), min(len(ks), j + 2)
        sm2[j] = sm[a:b].mean(axis=0)
    out = {str(k): sm2[j].round(2).tolist() for j, k in enumerate(ks)}
    json.dump(out, open(os.path.join(OUT, '%s_quads.json' % cid), 'w'))
    print(cid, len(out), 'frames; clean-ratio frames', len(good), 'median ratio', round(float(np.median(gv)), 3) if gv is not None else None)
    return out


if __name__ == '__main__':
    os.makedirs(OUT, exist_ok=True)
    which = sys.argv[1]
    if which == 'zentro2':
        build('zentro2', range(0, 721), (40, 1040, 450, 1650), s_min=150, v_min=150)
    elif which == 'coventry2':
        build('coventry2', range(0, 112), (300, 1060, 450, 1350), s_min=80, v_min=180)
    elif which == 'grace':
        build('grace', range(186, 432), (10, 290, 1000, 1500), s_min=80, v_min=60)


def load_quads(cid):
    """Per-frame quads with missing frames linearly interpolated (int frame -> 4x2 list)."""
    q = json.load(open(os.path.join(OUT, '%s_quads.json' % cid)))
    ks = sorted(int(k) for k in q)
    arr = np.array([q[str(k)] for k in ks], np.float64)
    out = {}
    for f in range(ks[0], ks[-1] + 1):
        out[f] = np.array([[np.interp(f, ks, arr[:, c, d]) for d in range(2)] for c in range(4)]).tolist()
    return out
