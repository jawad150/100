"""grp3_rankchart.py: the ranking chart on Zentro's monitor (video 8), as he describes it.

ILLUSTRATION, not live data: no Search Console / rank-tracker export exists for Zentro, so this chart draws the story
he tells ("three months ago ... not even on page two", "page two, top 10", "this morning, position three", "next
stop, position one") and is labelled 'Illustration' on screen and in the end-card fine print.

Geometry: the chart's line uses the exact vertices of the line the generator drew on the green monitor (measured in
the flattened screen, 1600 x 970), so his finger, which traces that line, stays on it. The line draws on behind his
fingertip (tracked: workspace3/grp/zentro2_tips.json).
"""
import functools

import numpy as np
from PIL import Image, ImageDraw

import grp3_common as C

SW, SH = 1600, 970
SS = 2
# vertices of the generated line in screen pixels (start .. arrow tip)
V = [(125, 875), (223, 796), (332, 717), (456, 726), (570, 646), (687, 558), (808, 582), (922, 495), (1037, 418),
     (1153, 390), (1257, 290), (1355, 128)]
K_POS = 29.0 / (875 - 128)                   # position per pixel: start = 32, arrow tip = 3


def y_of(pos):
    return 128 + (pos - 3) / K_POS


def pos_of(y):
    return 3 + (y - 128) * K_POS


# fingertip x over time (from the tracked tip; outliers dropped, made monotonic) -> how far the line is drawn
TIP_X = [(0.0, 125), (1.45, 125), (2.0, 228), (5.0, 245), (7.5, 300), (9.0, 450), (11.0, 741), (12.5, 912),
         (14.0, 1025), (15.5, 1122), (16.6, 1280), (18.05, 1355)]

INK, BODY, ACTION, BLUE, ORANGE, SURF, BORDER = C.INK, C.BODY, C.ACTION, C.BLUE, C.ORANGE, C.SURF, C.BORDER
GREEN_OK = (22, 163, 74)
MONTHS = [(125, 'Aug'), (535, 'Sep'), (945, 'Oct'), (1355, 'Nov')]


def drawn_x(t):
    ts = [a for a, _ in TIP_X]
    xs = [b for _, b in TIP_X]
    return float(np.interp(t, ts, xs))


def _f(name, size):
    return C.font(name, size * SS)


@functools.lru_cache(maxsize=1)
def _base():
    """Static chart: white page, header, page bands, rank axis, month axis."""
    im = Image.new('RGB', (SW * SS, SH * SS), (255, 255, 255))
    d = ImageDraw.Draw(im)
    s = SS
    # page bands
    d.rectangle([90 * s, y_of(1) * s, 1500 * s, y_of(10.5) * s], fill=(236, 246, 253))
    d.rectangle([90 * s, y_of(10.5) * s, 1500 * s, y_of(20.5) * s], fill=(246, 249, 252))
    d.text((1490 * s, (y_of(1) + 16) * s), 'PAGE 1', font=_f('Inter-Bold', 30), fill=ACTION, anchor='ra')
    d.text((1490 * s, (y_of(10.5) + 16) * s), 'PAGE 2', font=_f('Inter-Bold', 30), fill=(120, 140, 160), anchor='ra')
    # rank axis
    for p in (1, 10, 20, 30):
        y = y_of(p) * s
        d.line([90 * s, y, 1500 * s, y], fill=(225, 232, 240), width=s)
        d.text((78 * s, y), '#%d' % p, font=_f('Inter-SemiBold', 30), fill=BODY, anchor='rm')
    # month axis
    for x, m in MONTHS:
        d.text((x * s, 930 * s), m, font=_f('Inter-SemiBold', 32), fill=BODY, anchor='mm')
    # header: bottom right, the empty space under the line's final climb
    hx0, hy0 = 1010, 640
    d.rounded_rectangle([hx0 * s, hy0 * s, 1480 * s, 860 * s], radius=22 * s, fill=(255, 255, 255),
                        outline=BORDER, width=2 * s)
    d.text(((hx0 + 28) * s, (hy0 + 46) * s), 'Google position', font=_f('Inter-Bold', 40), fill=INK, anchor='lm')
    d.text(((hx0 + 28) * s, (hy0 + 96) * s), '“laptop repair near me”', font=_f('Inter-SemiBold', 28), fill=ACTION,
           anchor='lm')
    d.text(((hx0 + 28) * s, (hy0 + 136) * s), 'zentro.co.uk', font=_f('Inter-Medium', 26), fill=BODY, anchor='lm')
    tw = d.textlength('ILLUSTRATION', font=_f('Inter-Bold', 20))
    d.rounded_rectangle([(hx0 + 28) * s, (hy0 + 164) * s, (hx0 + 28) * s + tw + 28 * s, (hy0 + 198) * s],
                        radius=17 * s, fill=(255, 241, 224))
    d.text(((hx0 + 42) * s, (hy0 + 181) * s), 'ILLUSTRATION', font=_f('Inter-Bold', 20), fill=(180, 95, 0),
           anchor='lm')
    return im


def _polyline_upto(xmax):
    pts = [V[0]]
    for a, b in zip(V[:-1], V[1:]):
        if b[0] <= xmax:
            pts.append(b)
        else:
            if a[0] < xmax:
                u = (xmax - a[0]) / (b[0] - a[0])
                pts.append((xmax, a[1] + (b[1] - a[1]) * u))
            break
    return pts


def _badge(d, x, y, big, small, fill, anchor='l'):
    s = SS
    fb, fs = _f('Inter-Bold', 72), _f('Inter-SemiBold', 34)
    w = max(d.textlength(big, font=fb), d.textlength(small, font=fs)) + 44 * s
    h = 150 * s
    x0 = x * s if anchor == 'l' else x * s - w
    d.rounded_rectangle([x0 + 4 * s, y * s + 6 * s, x0 + w + 4 * s, y * s + h + 6 * s], radius=22 * s,
                        fill=(220, 228, 236))
    d.rounded_rectangle([x0, y * s, x0 + w, y * s + h], radius=22 * s, fill=fill)
    d.text((x0 + 26 * s, y * s + 50 * s), big, font=fb, fill=(255, 255, 255), anchor='lm')
    d.text((x0 + 26 * s, y * s + 112 * s), small, font=fs, fill=(255, 255, 255), anchor='lm')


def _pill(d, x, y, text, fill=(255, 255, 255), color=INK, border=BORDER, size=24, icon_dot=None):
    s = SS
    f = _f('Inter-SemiBold', size)
    w = d.textlength(text, font=f) + (52 if icon_dot else 32) * s
    h = (size + 22) * s
    d.rounded_rectangle([x * s - w / 2, y * s - h / 2, x * s + w / 2, y * s + h / 2], radius=h / 2, fill=fill,
                        outline=border, width=2 * s)
    tx = x * s - w / 2 + (40 if icon_dot else 16) * s
    if icon_dot:
        d.ellipse([tx - 26 * s, y * s - 7 * s, tx - 12 * s, y * s + 7 * s], fill=icon_dot)
    d.text((tx, y * s), text, font=f, fill=color, anchor='lm')


MILESTONES = [(456, 726, 'Service pages fixed', 23.1), (808, 582, 'Google profile sorted', 24.85),
              (1153, 390, 'Real reviews coming in', 26.3)]


def chart(t):
    """Chart frame (sRGB float, SW x SH) at output time t."""
    return _chart(round(t * 24) / 24.0)


@functools.lru_cache(maxsize=8)
def _chart(t):
    im = _base().copy()
    d = ImageDraw.Draw(im)
    s = SS
    xm = drawn_x(t)
    pts = _polyline_upto(xm)
    if len(pts) > 1:
        d.line([(x * s, y * s) for x, y in pts], fill=ACTION, width=9 * s, joint='curve')
    # vertices reached
    for (x, y) in V[:-1]:
        if x <= xm + 0.5:
            d.ellipse([(x - 11) * s, (y - 11) * s, (x + 11) * s, (y + 11) * s], fill=(255, 255, 255),
                      outline=ACTION, width=5 * s)
    # head of the line: a dot that is the live position
    hx, hy = pts[-1]
    pos = pos_of(hy)
    if t >= 1.45:
        r = 17
        d.ellipse([(hx - r) * s, (hy - r) * s, (hx + r) * s, (hy + r) * s], fill=ORANGE, outline=(255, 255, 255),
                  width=5 * s)
    # 'three months ago': start point
    if 7.9 <= t < 12.6:
        _pill(d, 520, 860, '3 months ago: not in the top 20', fill=(255, 255, 255), color=INK, icon_dot=(225, 29, 72), size=36)
    # page two / top 10 callouts as the line enters each band (spoken at 13.5 / 15.7)
    if 13.45 <= t < 15.7:
        _pill(d, 720, 450, 'Page 2', fill=(255, 255, 255), color=INK, icon_dot=(120, 140, 160), size=40)
    if 15.7 <= t < 18.05:
        _pill(d, 980, 250, 'Top 10', fill=(255, 255, 255), color=ACTION, icon_dot=ACTION, size=40)
    # position three (spoken at 18.1)
    if t >= 18.05:
        _badge(d, 1300, 150, '#3', 'Position 3 · this morning', ACTION, anchor='r')
    # the work he lists (22.2-27.5): markers on the line
    for (x, y, txt, t0) in MILESTONES:
        if t >= t0:
            d.ellipse([(x - 15) * s, (y - 15) * s, (x + 15) * s, (y + 15) * s], fill=GREEN_OK,
                      outline=(255, 255, 255), width=4 * s)
            _pill(d, x + 10, y + 72, txt, fill=(240, 253, 244), color=(21, 128, 61), border=(187, 247, 208), size=32)
    # next stop, position one (27.6)
    if t >= 27.6:
        y1 = y_of(1)
        for x in range(160, 1480, 28):
            d.line([x * s, y1 * s, (x + 14) * s, y1 * s], fill=GREEN_OK, width=4 * s)
        _pill(d, 640, y1 + 44, 'Next stop: #1', fill=GREEN_OK, color=(255, 255, 255), border=GREEN_OK, size=40)
    out = np.asarray(im.resize((SW, SH), Image.LANCZOS), np.float32)
    out.setflags(write=False)
    return out
