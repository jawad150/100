"""grp_prep.py: one-off analysis for the Google Ranker Pro client edits (grp_leam, grp_of).

python3 grp_prep.py leam    hand mattes + finger track for the Leam Taxis screen shot (frames 192-407)
python3 grp_prep.py of      banner clean-up patches + laptop screen quad for the Organic Fostering clip

Outputs go to workspace3/grp/ (git-ignored). Sources are the registered clips workspace3/frames/{leam,of}.
"""
import json
import os
import sys

import cv2
import numpy as np

import core as K

FR = K.FRAMES
OUT = os.path.join(K.WS, 'grp')

# Leam Taxis screen shot geometry (measured on the 1080x1920 source)
LEAM_SHOT2 = (192, 407)          # inclusive frame range of the monitor shot
LEAM_DISPLAY = (594, 1342)       # display rows: top of tab bar .. bottom of taskbar (full width)
LEAM_GREEN_TOP = 684             # reference green top edge (per-frame drift is measured)


def _frame(cid, i, flags=cv2.IMREAD_COLOR):
    return cv2.imread(os.path.join(FR, cid, '%05d.jpg' % i), flags)


def leam():
    d = os.path.join(OUT, 'leam_matte')
    os.makedirs(d, exist_ok=True)
    y0, y1 = LEAM_DISPLAY
    track = {}
    k_open = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (13, 13))
    k_close = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (9, 9))
    for i in range(LEAM_SHOT2[0], LEAM_SHOT2[1] + 1):
        im = _frame('leam', i)
        hsv = cv2.cvtColor(im, cv2.COLOR_BGR2HSV)
        h, s, v = [hsv[..., c].astype(np.int32) for c in range(3)]
        b, g, r = [im[..., c].astype(np.float32) for c in range(3)]
        # drift: green top edge in a clean column band
        gmask = (h > 35) & (h < 85) & (s > 50) & (v > 90)
        prof = gmask[560:800, 120:420].mean(1)
        top = 560 + int(np.argmax(prof > 0.6))
        dy = top - LEAM_GREEN_TOP
        # hand = skin or dark sleeve, below the nav bar
        skin = (((h <= 25) | (h >= 165)) & (s > 35) & (s < 210) & (v > 60))
        dark = (v < 105)
        cand = (skin | dark)
        cand[:y0 + 92 + dy, :] = False          # nothing above the green (tab + nav bars)
        cand[y1 + 6:, :] = False
        m = cv2.morphologyEx(cand.astype(np.uint8), cv2.MORPH_OPEN, k_open)     # drops the thin drawn line
        m = cv2.morphologyEx(m, cv2.MORPH_CLOSE, k_close)
        n, lab, stats, _ = cv2.connectedComponentsWithStats(m, 8)
        keep = np.zeros_like(m)
        for c in range(1, n):
            if stats[c, cv2.CC_STAT_AREA] > 3000:
                keep[lab == c] = 1
        # soft edge: fade where the pixel is still mostly green (motion-blurred finger edges)
        green_score = np.clip((g - np.maximum(r, b) - 8.0) / 40.0, 0, 1)
        hard = cv2.dilate(keep, np.ones((5, 5), np.uint8)).astype(np.float32)
        alpha = hard * (1.0 - green_score)
        alpha = np.maximum(alpha, keep.astype(np.float32) * 0.0)
        alpha = cv2.GaussianBlur(alpha, (0, 0), 1.2)
        alpha[:y0 + dy, :] = 0
        crop = (np.clip(alpha[y0:y1 + 1, :], 0, 1) * 255).astype(np.uint8)
        cv2.imwrite(os.path.join(d, '%05d.png' % i), crop)
        # finger: the drawn line's tip (dark thin pixels on green, outside the hand)
        line = (v < 140) & ~cv2.dilate(keep, np.ones((15, 15), np.uint8)).astype(bool)
        line[:y0 + 100 + dy, :] = False
        line[1310 + dy:, :] = False
        ys, xs = np.where(line)
        tip_x = int(xs.max()) if len(xs) > 40 else -1
        tip_y = int(ys[xs.argmax()]) if len(xs) > 40 else -1
        # fingertip: the hand pixel furthest up-left along the pointing direction
        hy, hx = np.where(keep > 0)
        if len(hx):
            j = np.argmin(hy * 1.0 + hx * 0.15)
            fx, fy = int(hx[j]), int(hy[j])
        else:
            fx = fy = -1
        track[i] = dict(dy=int(dy), tip=[tip_x, tip_y], finger=[fx, fy], hand_px=int(keep.sum()))
    json.dump(track, open(os.path.join(OUT, 'leam_track.json'), 'w'), indent=0)
    print('leam mattes ->', d, len(track))


# Organic Fostering clip geometry
OF_SHOTS = {1: (0, 236), 2: (237, 419), 3: (420, 720)}
OF_BANNER = {1: (840, 480, 1080, 1000), 3: (900, 440, 1080, 1000)}    # x0, y0, x1, y1 search rect per shot

OF_BANNER_TOP = {1: 540, 3: 505}     # approximate top edge of the dark banner per shot (frame px)


def _banner_fill(sub, v, s, top_hint):
    """Replace the generated lettering / glyph / icons on the defocused dark banner with a smooth slate plate.
    Her hair and scarf (v < 42) are much darker than the banner (v ~ 64) and are kept."""
    hh, ww = v.shape
    f = sub.astype(np.float32)
    person = (v < 42).astype(np.uint8)
    skin = ((f[..., 2] - f[..., 0] > 28) & (v > 70)).astype(np.uint8)       # warm skin (BGR: R - B)
    person = cv2.dilate(person | skin, np.ones((3, 3), np.uint8))
    top = top_hint                     # locked-off shots: the banner edge does not move
    rows = np.arange(hh)[:, None]
    inside = (rows > top + 14)
    cyan = ((f[..., 0] - f[..., 2]) > 18) & (s > 60)                        # coloured icon dots
    # plate: quadratic fit to clean banner pixels
    bright = (v > 82) | cyan
    text = (bright & inside & ~person.astype(bool)).astype(np.uint8)
    text_d = cv2.dilate(text, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (17, 17)))
    clean = inside & (text_d == 0) & (person == 0) & (v >= 42) & (v < 100)
    ys, xs = np.nonzero(clean)
    if len(ys) < 200:
        return sub
    X = np.stack([np.ones_like(xs), xs, ys, xs * xs, xs * ys, ys * ys], 1).astype(np.float64) / \
        np.array([1, ww, hh, ww * ww, ww * hh, hh * hh])
    yy, xx = np.mgrid[0:hh, 0:ww]
    XA = np.stack([np.ones_like(xx), xx, yy, xx * xx, xx * yy, yy * yy], -1).reshape(-1, 6).astype(np.float64) / \
        np.array([1, ww, hh, ww * ww, ww * hh, hh * hh])
    plate = np.zeros_like(f)
    for c in range(3):
        coef, *_ = np.linalg.lstsq(X, f[ys, xs, c].astype(np.float64), rcond=None)
        plate[..., c] = (XA @ coef).reshape(hh, ww)
    # local tone correction: smooth residual of the clean pixels (normalised convolution) so the plate
    # matches the banner's own shading at the fill edges
    cm = clean.astype(np.float32)
    den = cv2.GaussianBlur(cm, (0, 0), 14) + 1e-4
    for c in range(3):
        res = (f[..., c] - plate[..., c]) * cm
        plate[..., c] += np.clip(cv2.GaussianBlur(res, (0, 0), 14) / den, -12, 12)
    rng = np.random.default_rng(int(f.sum()) % 100000)
    plate += rng.normal(0, 1.3, plate.shape[:2])[..., None].astype(np.float32)
    fill = cv2.GaussianBlur(text_d.astype(np.float32), (0, 0), 5.0)
    keep = cv2.GaussianBlur(person.astype(np.float32), (0, 0), 1.2)
    fill = np.clip(fill * 1.6, 0, 1) * (1 - keep) * inside
    out = f * (1 - fill[..., None]) + plate * fill[..., None]
    return np.clip(out + 0.5, 0, 255).astype(np.uint8)


def of():
    d = os.path.join(OUT, 'of_banner')
    os.makedirs(d, exist_ok=True)
    info = {'banner': {}, 'scarf_max_x': {}}
    for shot in (1,):                 # shot 3 is punched in past the banner instead (see grp_of.py)
        x0, y0, x1, y1 = OF_BANNER[shot]
        a, b = OF_SHOTS[shot]
        smax = 0
        for i in range(a, b + 1):
            im = _frame('of', i)
            sub = im[y0:y1, x0:x1].copy()
            hsv = cv2.cvtColor(sub, cv2.COLOR_BGR2HSV)
            h, s, v = [hsv[..., c].astype(np.int32) for c in range(3)]
            out = _banner_fill(sub, v, s, top_hint=OF_BANNER_TOP[shot] - y0)
            cv2.imwrite(os.path.join(d, '%05d.jpg' % i), out, [cv2.IMWRITE_JPEG_QUALITY, 95])
            # scarf / hijab extent (plum: hue 120-175, some saturation, darkish)
            plum = ((h > 120) & (h < 178) & (s > 40) & (v < 140)).astype(np.uint8)
            plum = cv2.morphologyEx(plum, cv2.MORPH_OPEN, np.ones((5, 5), np.uint8))
            cols = np.where(plum[:min(420, y1 - y0)].sum(0) > 25)[0]
            if len(cols):
                smax = max(smax, int(cols.max()) + x0)
        info['banner'][shot] = [x0, y0, x1, y1]
        info['scarf_max_x'][shot] = smax
    # laptop screen quad (shot 2, static camera)
    im = _frame('of', 300)
    hsv = cv2.cvtColor(im, cv2.COLOR_BGR2HSV)
    m = ((hsv[..., 2] > 200) & (hsv[..., 1] < 30)).astype(np.uint8)
    m[:700] = 0; m[1200:] = 0; m[:, 700:] = 0
    n, lab, st, _ = cv2.connectedComponentsWithStats(m, 8)
    c = 1 + int(np.argmax(st[1:, cv2.CC_STAT_AREA]))
    blob = (lab == c)
    xs_top, ys_top, xs_bot, ys_bot = [], [], [], []
    for x in range(5, 240, 5):
        col = np.where(blob[:, x])[0]
        if len(col):
            xs_top.append(x); ys_top.append(col.min())
    for x in range(70, 330, 5):
        col = np.where(blob[:, x])[0]
        if len(col):
            xs_bot.append(x); ys_bot.append(col.max())
    rows = range(940, 1170, 5)
    xs_r, ys_r = [], []
    for y in rows:
        r = np.where(blob[y, :])[0]
        if len(r):
            xs_r.append(r.max()); ys_r.append(y)
    top = np.polyfit(xs_top, ys_top, 1)          # y = a x + b
    bot = np.polyfit(xs_bot, ys_bot, 1)
    right = np.polyfit(ys_r, xs_r, 1)             # x = c y + d

    def inter_tr(line_y, line_x):                 # y = a x + b and x = c y + d
        a, b = line_y; cc, dd = line_x
        y = (a * dd + b) / (1 - a * cc)
        return [float(cc * y + dd), float(y)]
    TR = inter_tr(top, right)
    BR = inter_tr(bot, right)
    XL = -70.0                                    # left edge is off frame: extend the page past x = 0
    TL = [XL, float(top[0] * XL + top[1])]
    BL = [XL, float(bot[0] * XL + bot[1])]
    info['laptop_quad'] = [TL, TR, BR, BL]
    info['mug_ellipse'] = [240, 1186, 104, 24]
    json.dump(info, open(os.path.join(OUT, 'of_info.json'), 'w'), indent=1)
    print('of ->', json.dumps(info))


if __name__ == '__main__':
    {'leam': leam, 'of': of}[sys.argv[1]]()
