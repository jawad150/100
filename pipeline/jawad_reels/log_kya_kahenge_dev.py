"""log_kya_kahenge_dev.py - QA and gate measurements for reel 5, C15 (motion-timeline-builder; dev only, never imported
by a render).

    python3 log_kya_kahenge_dev.py snap A|B          # BRIEF 7.4 head-snap: head-pixel luma 0.10 -> 0.70 s (B 0.0 -> 0.6)
                                                     # on the LKK_NOTEXT gate stills, full size and 360 px; eye radii
    python3 log_kya_kahenge_dev.py lines <png>       # bright near-vertical lines <= 12 px wide in the centre third
    python3 log_kya_kahenge_dev.py camera            # projected-subject steps per frame for every camera move (snaps)
    python3 log_kya_kahenge_dev.py text [A|B]        # ink boxes of every text element every 1/15 s vs the safe zones
    python3 log_kya_kahenge_dev.py o6                # share of ember spawn points inside the card layer's alpha
    python3 log_kya_kahenge_dev.py captions [A|B]    # cap.check(), cap.report(), SRT to <RW>/captions/
    python3 log_kya_kahenge_dev.py all               # everything above (gate stills must exist)
Results are printed as JSON and written to <RW>/qa/<name>.json.
"""
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import jawad_kit                                   # noqa: F401,E402
from jawad_kit import K                            # noqa: E402
import cv2                                         # noqa: E402
import numpy as np                                 # noqa: E402
import log_kya_kahenge as M                        # noqa: E402
import log_kya_kahenge_crowd as CR                 # noqa: E402
import log_kya_kahenge_faces as LF                 # noqa: E402

RW = M.RW
QA = os.path.join(RW, 'qa')
GATE = os.path.join(RW, 'gate')


def _save(name, d):
    os.makedirs(QA, exist_ok=True)
    with open(os.path.join(QA, name + '.json'), 'w') as fh:
        json.dump(d, fh, indent=1, default=float)
    print(json.dumps(d, indent=1, default=float))
    return d


def _luma(u8):
    f = u8.astype(np.float32)
    return f[..., 0] * 0.2126 + f[..., 1] * 0.7152 + f[..., 2] * 0.0722


def _imread_rgb(p):
    return cv2.cvtColor(cv2.imread(p), cv2.COLOR_BGR2RGB)


# ============================================================================================== head-snap
def snap(hook='A'):
    """BRIEF 7.4: mean head-pixel luma (BT.709 Y of the 8-bit frame, eyes masked + 1 px) turned -> front, at full size
    and on the 360 x 640 area downscale (mask area-downscaled, > 0.5). Needs the LKK_NOTEXT stills in <RW>/gate."""
    if hook == 'A':
        cam, ts, which, t0, sp = CR.cam_wide(), (0.1, 0.7), 'wide', 0.2, 0.4
        files = [os.path.join(GATE, 'notext_A_%06.2f.png' % t) for t in ts]
    else:
        cam, ts, which, t0, sp = CR.cam_rows(0.0), (0.0, 0.6), 'rows', 0.1, 0.3
        files = [os.path.join(GATE, 'notext_B_%06.2f.png' % t) for t in ts]
    out = dict(hook=hook, times=ts, files=files)
    ims, hm, em = [], [], []
    for t, f in zip(ts, files):
        ims.append(_imread_rgb(f))
        w, j = CR.snap_state(t, which, t0, sp)
        st = CR.State(head=w, jolt=j, walls=0.0 if hook == 'B' else 1.0)
        hm.append(CR.head_mask(cam, t, st))
        em.append(CR.eye_mask(cam, t, st))
    m = (hm[0] > 0.5) & (hm[1] > 0.5)
    eyes = cv2.dilate((np.maximum(em[0], em[1]) > 0.02).astype(np.uint8), np.ones((3, 3), np.uint8)) > 0
    m &= ~eyes
    l0, l1 = float(_luma(ims[0])[m].mean()), float(_luma(ims[1])[m].mean())
    out['full'] = dict(px=int(m.sum()), luma=(round(l0, 2), round(l1, 2)), change_pct=round(100 * (l1 - l0) / l0, 1))
    sm = [cv2.resize(i, (360, 640), interpolation=cv2.INTER_AREA) for i in ims]
    ms = cv2.resize(m.astype(np.float32), (360, 640), interpolation=cv2.INTER_AREA) > 0.5
    s0, s1 = float(_luma(sm[0])[ms].mean()), float(_luma(sm[1])[ms].mean())
    out['360'] = dict(px=int(ms.sum()), luma=(round(s0, 2), round(s1, 2)), change_pct=round(100 * (s1 - s0) / s0, 1))
    out['pass'] = out['full']['change_pct'] >= 15 and out['360']['change_pct'] >= 15
    cv2.imwrite(os.path.join(GATE, 'snap360_%s.png' % hook), cv2.cvtColor(np.hstack(sm), cv2.COLOR_RGB2BGR))
    # eye radii per visible row (front state) and the eye core level
    if hook == 'A':
        out['eyes'] = eye_radii(cam)
    y = _luma(ims[0])
    yl = 16 + y * 219 / 255
    out['frame0_like'] = dict(YAVG_lim=round(float(yl.mean()), 1), frac_Y200_lim=round(float((yl >= 200).mean()), 4))
    return _save('snap_%s' % hook, out)


def eye_radii(cam):
    """Per row: the eye radius actually drawn in this camera (min / median px) for figures with a visible head."""
    F, _ = CR.seats()
    T = CR.figure_textures()
    x = CR.head_screen_x('wide')
    res = {}
    for i in range(CR.NROWS):
        ks = np.flatnonzero((F['row'] == i) & (x > 0) & (x < K.W))
        rs = []
        for k in ks:
            tex = T[(int(F['var'][k]), int(F['flip'][k]))]
            g = tex['geo']
            hc, hw_, hh_, an, hrot = CR._head_plane(cam, tex, F['B'][k], CR.FIG_W, CR.FIG_H, (0.0, float(F['yaw'][k]), 0.0),
                                                    0.0, 0.0, 1.0, 1.0)
            x0, y0, x1, y1 = g['box']
            hl = K.plane_point(hc, hw_, hh_, rot=hrot, uv=np.array([[(g['hx'] - g['hw'] - x0) / (x1 - x0), 0.5],
                                                                    [(g['hx'] + g['hw'] - x0) / (x1 - x0), 0.5]]), anchor=an)
            hxy, _ = cam.project(hl)
            hpx = float(np.hypot(*(hxy[1] - hxy[0])))
            r = 0.035 * hpx
            if i <= 5:
                r = max(r, 1.5)
            rs.append((hpx, r))
        if rs:
            a = np.array(rs)
            res['row%d' % i] = dict(n=len(rs), head_px=(round(a[:, 0].min(), 1), round(float(np.median(a[:, 0])), 1)),
                                    eye_r=(round(a[:, 1].min(), 2), round(float(np.median(a[:, 1])), 2)))
    res['eye_core_linear_x_amber'] = 1.3
    return res


# ============================================================================================== edge-on lines
def lines(png):
    """Bright near-vertical lines <= 12 px wide in the centre third (x 360-720): column profile of a vertical
    top-hat (line minus its 9 px horizontal median) over runs >= 80 px tall."""
    u8 = _imread_rgb(png)
    y = _luma(u8)
    bg = cv2.blur(y, (31, 1))
    th = y - bg
    mask = (th > 18) & (y > 70)
    col = mask[:, 360:720]
    # vertical runs per column
    runs = []
    for c in range(col.shape[1]):
        v = col[:, c].astype(np.int8)
        d = np.diff(np.r_[0, v, 0])
        st, en = np.flatnonzero(d == 1), np.flatnonzero(d == -1)
        L = (en - st).max() if len(st) else 0
        runs.append(L)
    runs = np.array(runs)
    good = runs >= 80
    # group adjacent columns into lines; a line <= 12 px wide
    groups, cur = [], []
    for c in range(len(good)):
        if good[c]:
            cur.append(c)
        elif cur:
            groups.append(cur)
            cur = []
    if cur:
        groups.append(cur)
    lines_ = [(360 + g[0], 360 + g[-1], int(runs[g].max())) for g in groups if len(g) <= 12]
    return _save('lines_' + os.path.basename(png)[:-4], dict(png=png, lines=lines_, n=len(lines_), pass_=len(lines_) >= 3))


# ============================================================================================== camera snaps
def camera():
    """For every moving camera: per-frame screen step of tracked world points; flag a step > 3x both neighbours."""
    out = {}

    def track(name, f0, f1, camf, pts):
        xy = []
        for f in range(f0, f1 + 1):
            p, _ = camf(f / K.FPS).project(np.asarray(pts, np.float64))
            xy.append(p)
        xy = np.array(xy)
        d = np.linalg.norm(np.diff(xy, axis=0), axis=2).max(axis=1)
        snaps = [f0 + i + 1 for i in range(1, len(d) - 1) if d[i] > 3 * max(d[i - 1], d[i + 1], 2.0)]
        acc = np.abs(np.diff(d))
        out[name] = dict(frames=(f0, f1), max_px_per_frame=round(float(d.max()), 2),
                         first_steps=[round(float(v), 2) for v in d[:4]], max_step_change=round(float(acc.max()), 2),
                         snaps=snaps)
    F, _ = CR.seats()
    s3_pts = [LF.S3_FEET, (0.0, -2180.0, 9400.0), tuple(CR.BANK)]
    track('S3-01 cam_s3', 288, 383, LF.cam_s3, s3_pts)
    piv = [CR.PIVOT, (CR.R_(5) * math.sin(math.radians(10)), -CR.h_(5), CR.R_(5) * math.cos(math.radians(10))),
           (CR.R_(2) * math.sin(math.radians(30)), -CR.h_(2), CR.R_(2) * math.cos(math.radians(30)))]
    track('S4-01 orbit', 479, 576, lambda t: CR.cam_rows(M.psi_at(t), M.focus_at(t)), piv)
    return _save('camera', out)


# ============================================================================================== text safe zones
def _ink(cv, thr=0.25):
    a = cv[..., 3] > thr
    if not a.any():
        return None
    ys, xs = np.nonzero(a)
    return (int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1)


def _violations(b, key=True, cta=False):
    v = []
    x0, y0, x1, y1 = b
    ymax = 1600 if cta else 1480
    if key and (x0 < 70 or x1 > 1010 or y0 < 230 or y1 > ymax):
        v.append('outside key zone')
    if x1 > 930 and y1 > 1050 and y0 < 1700:
        v.append('in the like/share column')
    if y1 > 1620:
        v.append('below y 1620')
    return v


def text(hook='A', step=1.0 / 15):
    """Ink boxes (alpha > 0.25) of each text element every 1/15 s, drawn alone on an empty canvas."""
    A = M.assets()
    cap = M.captions(hook)
    res = {}
    worst = {}
    t = 0.0
    while t < M.DUR:
        els = {}
        cv = np.zeros((K.H, K.W, 4), np.float32)
        M.draw_overlays(cv, t, hook)
        els['lockups'] = _ink(cv)
        cv = np.zeros((K.H, K.W, 4), np.float32)
        if t >= 3.0 and t < 9.6 + 1.2:
            M.draw_judgements(cv, t)
        els['judgement'] = _ink(cv)
        cv = np.zeros((K.H, K.W, 4), np.float32)
        A['card'].draw(cv, t, M.T_CARD)
        els['endcard'] = _ink(cv)
        cv = np.zeros((K.H, K.W, 4), np.float32)
        cap.draw(cv, t)
        els['caption'] = _ink(cv)
        for k, b in els.items():
            if b is None:
                continue
            v = _violations(b, cta=(k == 'endcard'))
            r = res.setdefault(k, dict(n=0, union=list(b), violations=[]))
            r['n'] += 1
            r['union'] = [min(r['union'][0], b[0]), min(r['union'][1], b[1]), max(r['union'][2], b[2]),
                          max(r['union'][3], b[3])]
            if v:
                r['violations'].append((round(t, 3), b, v))
            m = min(b[0] - 70, 1010 - b[2], b[1] - 230, (1600 if k == 'endcard' else 1480) - b[3])
            if k not in worst or m < worst[k][0]:
                worst[k] = (m, round(t, 3), b)
        t += step
    for k in res:
        res[k]['violations'] = res[k]['violations'][:12]
        res[k]['worst_margin_px'] = worst[k]
    return _save('text_%s' % hook, res)


# ============================================================================================== O6 / captions
def o6():
    pts, rnd, nrm, lumv = M.o6_seed()
    lay = np.asarray(M.X._frozen(M.S_C_cards, M.fr(708 - M.O6_PRE)))
    a = lay[..., 3]
    xi = np.clip(pts[:, 0].astype(int), 0, K.W - 1)
    yi = np.clip(pts[:, 1].astype(int), 0, K.H - 1)
    inside = a[yi, xi] > 0.5
    return _save('o6', dict(n=len(pts), inside_share=round(float(inside.mean()), 4), pass_=bool(inside.mean() >= 0.98)))


def captions(hook='A'):
    cap = M.captions(hook)
    os.makedirs(os.path.join(RW, 'captions'), exist_ok=True)
    srt = cap.save_srt(os.path.join(RW, 'captions', 'log_kya_kahenge_%s.srt' % hook))
    return _save('captions_%s' % hook, dict(check=cap.check(), report=cap.report(), srt=srt,
                                            skipped=[c.text for c in cap.skipped]))


if __name__ == '__main__':
    cmd = sys.argv[1] if len(sys.argv) > 1 else 'all'
    arg = sys.argv[2] if len(sys.argv) > 2 else None
    if cmd == 'snap':
        snap(arg or 'A')
    elif cmd == 'lines':
        lines(arg)
    elif cmd == 'camera':
        camera()
    elif cmd == 'text':
        text(arg or 'A')
    elif cmd == 'o6':
        o6()
    elif cmd == 'captions':
        captions(arg or 'A')
    elif cmd == 'all':
        snap('A')
        snap('B')
        lines(os.path.join(GATE, 'log_kya_kahenge_019.60.png'))
        camera()
        text('A')
        text('B')
        o6()
        captions('A')
        captions('B')
