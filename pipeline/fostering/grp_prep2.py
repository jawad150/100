"""grp_prep2.py: screen geometry for the Google Ranker Pro set (Oct 2026 clips).

python3 grp_prep2.py golden   per-frame laptop display quad for Golden Line shot 1 (frames 0-216) from the green
                              screen's unoccluded edges -> workspace3/grp/golden_quads.json
python3 grp_prep2.py leam2    per-frame monitor quad (homography track) + hand matte + fingertip for the
                              Leam monitor shot (frames 187-720) -> workspace3/grp/leam2_track.json
"""
import json
import os
import sys

import cv2
import numpy as np

import core as K

FR = K.FRAMES
OUT = os.path.join(K.WS, 'grp')


def _frame(cid, i):
    return cv2.imread(os.path.join(FR, cid, '%05d.jpg' % i), cv2.IMREAD_COLOR)


def green_mask(im, s_min=80, v_min=60):
    hsv = cv2.cvtColor(im, cv2.COLOR_BGR2HSV)
    h, s, v = [hsv[..., c].astype(np.int32) for c in range(3)]
    return ((h > 35) & (h < 90) & (s > s_min) & (v > v_min))


def _line_fit(xs, ys):
    """Robust y = a x + b (or x = a y + b) via iterated least squares with outlier rejection."""
    xs, ys = np.asarray(xs, np.float64), np.asarray(ys, np.float64)
    keep = np.ones(len(xs), bool)
    for _ in range(4):
        a, b = np.polyfit(xs[keep], ys[keep], 1)
        r = np.abs(ys - (a * xs + b))
        thr = max(1.5, np.percentile(r[keep], 80) * 1.5)
        keep = r < thr
    return a, b


def _isect(l1, l2):
    """l = (a, b, kind) with kind 'y' (y = a x + b) or 'x' (x = a y + b)."""
    (a1, b1, k1), (a2, b2, k2) = l1, l2
    if k1 == 'y' and k2 == 'x':
        y = (a1 * b2 + b1) / (1 - a1 * a2)
        return [a2 * y + b2, y]
    if k1 == 'x' and k2 == 'y':
        return _isect(l2, l1)
    raise ValueError


def golden():
    quads = {}
    for i in range(0, 217):
        m = green_mask(_frame('golden', i))
        cols = np.arange(40, 420, 6)
        top = [(x, int(np.argmax(m[700:1450, x])) + 700) for x in cols if m[700:1450, x].any()]
        bot = [(x, 1450 - int(np.argmax(m[700:1450, x][::-1]))) for x in np.arange(40, 560, 6) if m[700:1450, x].any()]
        rows = np.arange(1150, 1250, 4)
        right = [(int(np.where(m[y, :900])[0].max()) + 1, y) for y in rows if m[y, :900].any()]
        lt = _line_fit([p[0] for p in top], [p[1] for p in top])
        lb = _line_fit([p[0] for p in bot], [p[1] for p in bot])
        lr = _line_fit([p[1] for p in right], [p[0] for p in right])
        L = ('y', lt), ('y', lb)
        tl_x, bl_x = -170.0, -170.0                       # display continues past the frame's left edge
        tr = _isect((lt[0], lt[1], 'y'), (lr[0], lr[1], 'x'))
        br = _isect((lb[0], lb[1], 'y'), (lr[0], lr[1], 'x'))
        q = [[tl_x, lt[0] * tl_x + lt[1]], tr, br, [bl_x, lb[0] * bl_x + lb[1]]]
        quads[i] = q
    # temporal smoothing (the camera drifts slowly; edge fits jitter by a pixel or two)
    arr = np.array([quads[i] for i in range(217)], np.float64)
    sm = arr.copy()
    for k in range(217):
        a, b = max(0, k - 6), min(217, k + 7)
        sm[k] = np.median(arr[a:b], axis=0)
    out = {str(i): sm[i].round(2).tolist() for i in range(217)}
    json.dump(out, open(os.path.join(OUT, 'golden_quads.json'), 'w'))
    print('golden quads', out['0'], out['216'])


if __name__ == '__main__':
    if sys.argv[1] == 'golden':
        golden()


# ---------------------------------------------------------------------------------------------- leam2 monitor
LEAM2_X_R = 1500.0           # virtual right edge of the display (off frame) for the screen quad


def _edges(m, x_cols, y_lo=420, y_hi=1460):
    top, bot = [], []
    for x in x_cols:
        col = m[y_lo:y_hi, x]
        if col.sum() < 30:
            continue
        ys = np.where(col)[0]
        top.append((x, ys[0] + y_lo))
        bot.append((x, ys[-1] + y_lo))
    return top, bot


def leam2():
    """Monitor quad per frame (187-400: edge fits; later: the green sliver's bbox), hand blob + fingertip."""
    track = {}
    k_open = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (17, 17))
    prev_left = None
    for i in range(187, 721):
        im = _frame('leam2', i)
        g = green_mask(im, s_min=70, v_min=50)
        rec = {}
        if i <= 398:
            # top edge: columns right of his head; bottom edge: columns clear of the arm are picked by the fit
            top, bot = _edges(g, range(560, 1076, 8))
            ta, tb = _line_fit([p[0] for p in top], [p[1] for p in top])
            ba, bb = _line_fit([p[0] for p in bot], [p[1] for p in bot])
            # left edge from rows in the middle; reject when his head covers it
            rows = range(700, 1150, 6)
            left = []
            for y in rows:
                xs = np.where(g[y, :700])[0]
                if len(xs):
                    left.append((y, xs[0]))
            la, lb = _line_fit([p[0] for p in left], [p[1] for p in left]) if len(left) > 10 else (None, None)
            rec.update(top=[ta, tb], bot=[ba, bb], left=[la, lb] if la is not None else None, n_left=len(left))
            # hand: non-green inside the display, opened (drops drawn lines / labels), largest blob touching
            # the lower part, right of the head
            ytop = lambda x: ta * x + tb          # noqa: E731
            ybot = lambda x: ba * x + bb          # noqa: E731
            yy, xx = np.mgrid[0:1920, 0:1080]
            inside = (yy > ytop(xx) + 4) & (yy < ybot(xx) - 4) & (xx > 150)
            fg = (~g) & inside
            fgo = cv2.morphologyEx(fg.astype(np.uint8), cv2.MORPH_OPEN, k_open)
            n, lab, st, _ = cv2.connectedComponentsWithStats(fgo, 8)
            best, score = 0, 0
            for c in range(1, n):
                x, y, w, h, a = st[c]
                if a < 2500 or x + w < 380:
                    continue
                s = a * (1 + (y + h > ybot(x + w / 2) - 40))
                if s > score:
                    best, score = c, s
            if best:
                hy, hx = np.where(lab == best)
                j = int(np.argmin(hy + 0.25 * hx))
                rec['tip'] = [int(hx[j]), int(hy[j])]
                rec['hand_px'] = int(len(hx))
        else:
            ys, xs = np.where(g)
            if len(xs) > 200:
                rec['bbox'] = [int(xs.min()), int(ys.min()), int(xs.max()), int(ys.max())]
        track[i] = rec
    json.dump(track, open(os.path.join(OUT, 'leam2_track.json'), 'w'))
    for i in (187, 230, 260, 300, 340, 380, 398, 420, 600):
        print(i, track[i])


if __name__ == '__main__' and sys.argv[1] == 'leam2':
    leam2()


# ---------------------------------------------------------------------------------------------- leam2 fit
LEAM2_REF = 230
LEAM2_QREF = None
CW, CH = 1600, 900                    # replacement screen canvas (16:9)
CUM = [19, 36, 56, 77, 102, 114]       # Leam Taxis Business Profile calls, running total May..Oct 2026


def _isect_lines(top, left):
    """top: y = a x + b;  left: x = c y + d."""
    a, b = top
    c, d = left
    y = (a * d + b) / (1 - a * c)
    return [c * y + d, y]


def leam2fit():
    from scipy.optimize import least_squares
    tr = json.load(open(os.path.join(OUT, 'leam2_track.json')))
    r = tr[str(LEAM2_REF)]
    top, bot, left = r['top'], r['bot'], r['left']
    tl = _isect_lines(top, left)
    bl = _isect_lines(bot, left)
    tr_ = [LEAM2_X_R, top[0] * LEAM2_X_R + top[1]]
    br = [LEAM2_X_R, bot[0] * LEAM2_X_R + bot[1]]
    qref = np.float32([tl, tr_, br, bl])
    ref800 = top[0] * 800 + top[1]
    dys = {}
    for i in range(187, 399):
        t = tr[str(i)]['top']
        dys[i] = t[0] * 800 + t[1] - ref800
    # smooth dy (median of 5 then mean of 5)
    ks = sorted(dys)
    arr = np.array([dys[k] for k in ks])
    med = np.array([np.median(arr[max(0, j - 2):j + 3]) for j in range(len(arr))])
    sm = np.array([med[max(0, j - 2):j + 3].mean() for j in range(len(arr))])
    quads = {k: (qref + np.float32([0, sm[j]])).round(2).tolist() for j, k in enumerate(ks)}
    # fingertips -> screen canvas coords
    src = np.float32([[0, 0], [CW, 0], [CW, CH], [0, CH]])
    tips = []
    for k in ks:
        rec = tr[str(k)]
        if 'tip' not in rec or rec.get('hand_px', 0) < 8000 or k < 226 or k > 386:
            continue
        Hm = cv2.getPerspectiveTransform(src, np.float32(quads[k]))
        p = cv2.perspectiveTransform(np.float32([[rec['tip']]]), np.linalg.inv(Hm))[0, 0]
        tips.append((k, float(p[0]), float(p[1])))
    tips = np.array(tips)
    # reject outliers (knuckle picks): distance from a running median path
    keep = np.ones(len(tips), bool)
    for j in range(len(tips)):
        a, b = max(0, j - 4), min(len(tips), j + 5)
        mx, my = np.median(tips[a:b, 1]), np.median(tips[a:b, 2])
        if abs(tips[j, 1] - mx) > 40 or abs(tips[j, 2] - my) > 40:
            keep[j] = False
    tips = tips[keep]
    pad = 10.0                                         # the line runs just under the fingertip

    def line_y(x, p):
        x0, dx, yb, ppc = p
        xs = x0 + dx * np.arange(6)
        ys = yb - ppc * np.array(CUM)
        return np.interp(x, xs, ys)

    def res(p):
        return line_y(tips[:, 1], p) - (tips[:, 2] + pad)
    p0 = [150.0, 170.0, 830.0, 5.0]
    bounds = ([120.0, 150.0, 600.0, 2.0], [260.0, 186.0, 1100.0, 9.0])     # May on screen, Oct x <= ~1050
    for _ in range(3):                                   # refit without stray knuckle picks
        sol = least_squares(res, p0, bounds=bounds)
        rms = float(np.sqrt(np.mean(sol.fun ** 2)))
        good = np.abs(sol.fun) < max(2.5 * rms, 25.0)
        if good.all():
            break
        tips = tips[good]
        p0 = list(sol.x)
    sol = least_squares(res, p0, bounds=bounds)
    rms = float(np.sqrt(np.mean(sol.fun ** 2)))
    out = dict(quads=quads, qref=qref.tolist(), cw=CW, ch=CH, tips=tips.tolist(), fit=list(map(float, sol.x)),
               rms=rms, pad=pad)
    json.dump(out, open(os.path.join(OUT, 'leam2_screen.json'), 'w'))
    print('qref', qref.tolist())
    print('fit X0 %.1f DX %.1f YB %.1f PPC %.3f  rms %.1f  n=%d' % (*sol.x, rms, len(tips)))
    print('tips first/last', tips[0].round(1).tolist(), tips[-1].round(1).tolist())


if __name__ == '__main__' and sys.argv[1] == 'leam2fit':
    leam2fit()


def leam2swing():
    """Rough monitor quads for the camera move to his face (frames 399-720): the green is defocused / partly
    hidden, so top / bottom lines are fitted to the visible green and the page is laid along them."""
    d = json.load(open(os.path.join(OUT, 'leam2_screen.json')))
    aspect = 1.88
    swing = {}
    for i in range(399, 721):
        g = green_mask(_frame('leam2', i), s_min=70, v_min=50)
        g = cv2.morphologyEx(g.astype(np.uint8), cv2.MORPH_OPEN, np.ones((9, 9), np.uint8)).astype(bool)
        n, lab, st, _ = cv2.connectedComponentsWithStats(g.astype(np.uint8), 8)
        if n < 2:
            continue
        k = 1 + int(np.argmax(st[1:, 4]))
        if st[k, 4] < 1500:
            continue
        comp = lab == k
        cols = [x for x in range(0, 1080, 4) if comp[:, x].any()]
        top = [(x, np.where(comp[:, x])[0][0]) for x in cols]
        bot = [(x, np.where(comp[:, x])[0][-1]) for x in cols]
        if len(cols) < 6:
            continue
        ta, tb = _line_fit([p[0] for p in top], [p[1] for p in top])
        ba, bb = _line_fit([p[0] for p in bot], [p[1] for p in bot])
        xl = float(min(cols))
        h = (ba * xl + bb) - (ta * xl + tb)
        xr = xl + aspect * h
        q = [[xl, ta * xl + tb], [xr, ta * xr + tb], [xr, ba * xr + bb], [xl, ba * xl + bb]]
        swing[i] = dict(q=[[round(a, 2), round(b, 2)] for a, b in q], area=int(st[k, 4]))
    d['swing'] = swing
    json.dump(d, open(os.path.join(OUT, 'leam2_screen.json'), 'w'))
    for i in (400, 404, 410, 416, 430, 500, 700):
        print(i, swing.get(i))


if __name__ == '__main__' and sys.argv[1] == 'leam2swing':
    leam2swing()
