"""grp_leam_screen.py: the replacement monitor screen for the Leam Taxis edit (shot 2, frames 192-407).

The generated clip shows a green screen with a made-up climbing line. We replace the whole display (frame rows
594-1342, full width) with a browser holding the REAL Google Business Profile Performance > Calls screenshot
(assets/gsc/leamingtonspa_gbp_calls_may-oct2026.png, May-Oct 2026, 114 calls, Sept = 25) at its true aspect
ratio. Only the line, its fill and its points are redrawn (from the screenshot's own point positions, measured to
0.1 px) so the line can draw on under the owner's finger; the tooltip is the screenshot's own pixels.
Nothing is stretched or re-scaled vertically.

    screen_u8(t, fx) -> (748, 1080, 3) uint8 sRGB screen at time t with the reveal front at screen x `fx`
    composite(frame_u8, i, scr_u8) -> frame with the screen under the owner's hand (workspace3/grp/leam_matte)
"""
import functools
import os

import cv2
import numpy as np
from PIL import Image, ImageDraw

import core as K
import grp_kit as G
import ui

GBP = os.path.join(G.GSC, 'leamingtonspa_gbp_calls_may-oct2026.png')
# point centres in screenshot px (May .. Oct 2026), measured from the ring pixels
PTS = [(26.71, 341.07), (201.84, 352.65), (371.68, 335.0), (547.13, 329.26), (723.39, 306.37), (892.11, 381.45)]
BASE_Y = 452.5
BLUE = (11, 87, 208)                  # #0B57D0, line + tooltip
FILL_A = 0.045
Y0, Y1 = 594, 1343                    # display rows in the frame (= the matte crop, 749 rows)
SW, SH = 1080, Y1 - Y0
PAGE_S, PAGE_X, PAGE_Y = 1.12, 8.0, 92.0
WHITE_OUT = np.float32([236, 240, 238]) / 255.0     # filmed monitor white / black (sRGB), from the plate
BLACK_OUT = np.float32([26, 30, 32]) / 255.0


def to_scr(x, y):
    return PAGE_X + PAGE_S * x, PAGE_Y + PAGE_S * y


def line_y(xp):
    """Line height (screenshot px) at screenshot x (piecewise linear between the real points)."""
    xs = [p[0] for p in PTS]
    ys = [p[1] for p in PTS]
    return float(np.interp(xp, xs, ys))


@functools.lru_cache(maxsize=1)
def _shot():
    im = cv2.cvtColor(cv2.imread(GBP), cv2.COLOR_BGR2RGB)
    return im


@functools.lru_cache(maxsize=1)
def empty_chart_u8():
    """The screenshot with the line, points, area fill and tooltip removed (gridlines and labels kept)."""
    im = _shot().astype(np.float32)
    x0, y0, x1, y1 = 18, 268, 905, 452
    reg = np.zeros(im.shape[:2], bool)
    reg[y0:y1, x0:x1] = True
    # tooltip box -> white (nothing else lives there)
    im[276:337, 729:842] = 255.0
    r, b = im[..., 0], im[..., 2]
    tint = reg & (b - r >= 3) & (b - r < 40) & (r > 180)
    C = np.float32(BLUE)
    un = (im - FILL_A * C) / (1 - FILL_A)
    im[tint] = np.clip(un[tint], 0, 255)
    strong = (reg & (b - im[..., 0] >= 40)).astype(np.uint8)
    # point discs (white centres inside rings)
    for (px, py) in PTS:
        cv2.circle(strong, (int(round(px)), int(round(py))), 8, 1, -1)
    strong = cv2.dilate(strong, np.ones((3, 3), np.uint8))
    out = cv2.inpaint(np.clip(im, 0, 255).astype(np.uint8), strong, 3, cv2.INPAINT_TELEA)
    return out


@functools.lru_cache(maxsize=1)
def tooltip_sprite():
    """The screenshot's own '25 · September 2026' tooltip (box + pointer) as a linear sprite at screen scale,
    with its anchor = the tip of the pointer (its left edge, level with the Sept point)."""
    im = _shot()
    x0, y0, x1, y1 = 729, 276, 840, 336
    sub = im[y0:y1, x0:x1].astype(np.int32)
    blue = ((sub[..., 2] - sub[..., 0] > 100) & (sub[..., 0] < 90)).astype(np.uint8)
    blue[:, :8] = 0                                   # keep the line / point out of the crop
    box = cv2.morphologyEx(blue, cv2.MORPH_CLOSE, np.ones((9, 9), np.uint8))
    # fill text holes inside the box rows
    ys, xs = np.nonzero(box)
    bx0, bx1, by0, by1 = xs.min(), xs.max(), ys.min(), ys.max()
    full = np.zeros_like(box)
    full[by0:by1 + 1, bx0 + 6:bx1 + 1] = 1
    alpha = np.maximum(box, full).astype(np.float32)
    alpha = cv2.GaussianBlur(alpha, (0, 0), 0.6)
    rgba = np.dstack([sub.astype(np.uint8), (alpha * 255).astype(np.uint8)])
    s = PAGE_S
    rgba = cv2.resize(rgba, (round(rgba.shape[1] * s), round(rgba.shape[0] * s)), interpolation=cv2.INTER_CUBIC)
    spr = K.sprite(rgba)
    spr.setflags(write=False)
    return spr, (x0, y0)


def _supersample_draw(fn, w, h, ss=4):
    im = Image.new('RGBA', (w * ss, h * ss), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    fn(d, ss)
    a = np.asarray(im, np.float32) / 255.0
    a = cv2.resize(a, (w, h), interpolation=cv2.INTER_AREA)
    return a                                          # straight sRGB RGBA float


@functools.lru_cache(maxsize=1)
def line_layer():
    """Premultiplied linear RGBA (SH, SW) with the area fill and the line (no points)."""
    pts = [to_scr(x, y) for x, y in PTS]
    base = to_scr(0, BASE_Y)[1]

    def fill(d, ss):
        poly = [(x * ss, y * ss) for x, y in pts] + [(pts[-1][0] * ss, base * ss), (pts[0][0] * ss, base * ss)]
        d.polygon(poly, fill=BLUE + (int(255 * FILL_A),))

    def line(d, ss):
        d.line([(x * ss, y * ss) for x, y in pts], fill=BLUE + (255,), width=int(round(3.0 * PAGE_S * ss)),
               joint='curve')
    f = _supersample_draw(fill, SW, SH)
    ln = _supersample_draw(line, SW, SH)
    out = np.zeros((SH, SW, 4), np.float32)
    for layer in (f, ln):
        a = layer[..., 3:4]
        rgb = K.to_lin(layer[..., :3]) * a
        out[..., :3] = out[..., :3] * (1 - a) + rgb
        out[..., 3:4] = out[..., 3:4] * (1 - a) + a
    out.setflags(write=False)
    return out


# ---------------------------------------------------------------------------------------------- chrome
@functools.lru_cache(maxsize=1)
def base_screen():
    """Linear premultiplied (SH, SW, 4): browser chrome + page (empty chart) + taskbar."""
    S = ui.Surf(SW, SH)
    S.rrect(-10, 0, SW + 20, SH, 0, ui.col('#FFFFFF'), 1.0)
    # tab strip
    S.rrect(-10, 0, SW + 20, 46, 0, ui.col('#DEE1E6'), 1.0)
    S.rrect(118, 6, 330, 44, 12, ui.col('#FFFFFF'), 1.0)
    S.rrect(456, 8, 300, 34, 10, ui.col('#E9EBEE'), 1.0)
    ic = ui.icon('chart', 22, color='#0B57D0', stroke=2.4)
    ui.paste(S.img, ic, 134, 16)
    S.text(166, 34, 'Business Profile · Performance', 19, 'OpenSans-SemiBold', '#3C4043')
    fav = G.image_crop('/home/user/100/workspace3/leam/cropped-Leam-taxis-icon-270x270.png', None, 22)
    ui.paste(S.img, fav, 470, 14)
    S.text(500, 33, 'Leam Taxis | Leamington Spa Taxis', 18, 'OpenSans-Regular', '#5F6368')
    S.text(778, 33, '+', 26, 'OpenSans-Regular', '#5F6368')
    # toolbar
    S.rrect(-10, 46, SW + 20, 46, 0, ui.col('#FFFFFF'), 1.0)
    for i, nm in enumerate(('arrow_right',)):
        pass
    S.text(22, 78, '←', 24, 'OpenSans-Regular', '#5F6368')
    S.text(58, 78, '→', 24, 'OpenSans-Regular', '#BDC1C6')
    S.circle(104, 69, 9, ui.col('#5F6368'), 1.0)
    S.circle(104, 69, 6.5, ui.col('#FFFFFF'), 1.0)
    S.rrect(140, 52, 820, 34, 17, ui.col('#F1F3F4'), 1.0)
    lock = ui.icon('shield', 18, color='#5F6368', stroke=2.2)
    ui.paste(S.img, lock, 156, 60)
    S.text(184, 75, 'business.google.com', 19, 'OpenSans-Regular', '#202124')
    S.circle(1010, 69, 14, ui.col('#FFC61A'), 1.0)
    S.text(1003, 76, 'L', 18, 'OpenSans-Bold', '#1F1F1F')
    S.rrect(-10, 91, SW + 20, 1, 0, ui.col('#DADCE0'), 1.0)
    # page
    page = K.sprite(empty_chart_u8())
    pw, ph = round(page.shape[1] * PAGE_S), round(page.shape[0] * PAGE_S)
    page = cv2.resize(page, (pw, ph), interpolation=cv2.INTER_CUBIC)
    ui.paste(S.img, np.clip(page, 0, None), round(PAGE_X), round(PAGE_Y))
    # (the monitor's own taskbar sits just below row 1343 and stays from the plate)
    S.img.setflags(write=False)
    return S.img


@functools.lru_cache(maxsize=4)
def _dot(r, color, ring=None, ring_w=0.0, glow=0.0):
    d = int(r * 2 + ring_w * 2 + glow * 3 + 6)
    S = ui.Surf(d, d)
    c = d / 2
    if glow > 0:
        a, X0, Y0 = S.circle(c, c, r, ui.col(color), 0.0)
        S.glow(a, X0, Y0, ui.col(color), sigmas=(glow * 0.4, glow), strength=0.9, knock=0.0)
    if ring is not None:
        S.circle(c, c, r + ring_w, ui.col(ring), 1.0)
    S.circle(c, c, r, ui.col(color), 1.0)
    S.img.setflags(write=False)
    return S.img


def screen_lin(t, fx, t_here, t_start=8.0):
    """Linear screen at time t. fx = reveal front in SCREEN px; t_here = when the Sept tooltip pops."""
    scr = base_screen().copy()
    xs = np.arange(SW, dtype=np.float32) + 0.5
    soft = 5.0
    m = np.clip((fx - xs) / soft + 0.5, 0, 1)[None, :]
    lay = line_layer()
    scr[:] = scr * (1 - lay[..., 3:4] * m[..., None]) + lay * m[..., None]
    # scrubber guide at the front (hover crosshair), only while it moves through the plot
    p0 = to_scr(PTS[0][0], 0)[0]
    p5 = to_scr(PTS[-1][0], 0)[0]
    if p0 < fx < p5 + 2:
        gy0 = to_scr(0, 268)[1]
        gy1 = to_scr(0, BASE_Y)[1]
        gx = int(round(fx))
        col = K.to_lin(np.float32(BLUE) / 255.0)
        seg = np.zeros((int(gy1 - gy0), 1), np.float32)
        seg[(np.arange(seg.shape[0]) // 6) % 2 == 0] = 0.55
        reg = scr[int(gy0):int(gy0) + seg.shape[0], gx:gx + 2]
        a = seg[:, :, None] * np.ones((1, 2, 1), np.float32)
        reg[..., :3] = reg[..., :3] * (1 - a) + col * a
    # points pop as the front passes them
    for k, (px, py) in enumerate(PTS):
        sx, sy = to_scr(px, py)
        if fx < sx - 1:
            continue
        sel = (k == 4 and t >= t_here)
        pop = K.spring(max(0.0, (fx - sx)) / 600.0 + 0.0, 2.6, 0.5) if not sel else 1.0
        if sel:
            dot = _dot(5.6 * PAGE_S, '#0B57D0', ring='#FFFFFF', ring_w=1.2)
            K.draw(scr, dot, sx, sy, scale=1.0 + 0.35 * K.impulse(t, t_here, 6))
        else:
            dot = _dot(4.2 * PAGE_S, '#FFFFFF', ring='#0B57D0', ring_w=2.0 * PAGE_S)
            K.draw(scr, dot, sx, sy, scale=0.4 + 0.6 * min(1.0, pop * 1.0))
    # travelling dot on the line at the front
    if p0 < fx < p5:
        xp = (fx - PAGE_X) / PAGE_S
        sy = to_scr(0, line_y(xp))[1]
        K.draw(scr, _dot(6.0, '#0B57D0', glow=9.0), fx, sy)
    # the tooltip (screenshot pixels) pops at "here"
    if t >= t_here:
        spr, (tx0, ty0) = tooltip_sprite()
        u = K.spring(t - t_here, 3.0, 0.55)
        sx, sy = to_scr(tx0, ty0)
        K.draw(scr, spr, sx, sy + spr.shape[0] * 0.5, scale=0.6 + 0.4 * u, opacity=min(1.0, (t - t_here) / 0.08),
               anchor=(0.0, 0.5))
    return scr


def look_u8(scr_lin, seed=0):
    """Make the clean screen look filmed: monitor white / black levels, slight defocus, falloff, noise."""
    s = K.to_srgb(np.clip(scr_lin[..., :3], 0, 1))
    s = cv2.GaussianBlur(s, (0, 0), 0.85)
    s = BLACK_OUT + (WHITE_OUT - BLACK_OUT) * s
    yy, xx = np.mgrid[0:SH, 0:SW].astype(np.float32)
    v = 1.0 - 0.07 * (((xx - SW * 0.55) / SW) ** 2 * 2.2 + ((yy - SH * 0.4) / SH) ** 2 * 1.6)
    s = s * v[..., None]
    rng = np.random.default_rng(seed)
    s = s * 255.0 + rng.normal(0, 1.6, (SH, SW, 1)).astype(np.float32)
    return np.clip(s + 0.5, 0, 255).astype(np.uint8)


@functools.lru_cache(maxsize=8)
def matte(i):
    p = os.path.join(G.GRP, 'leam_matte', '%05d.png' % i)
    m = cv2.imread(p, cv2.IMREAD_GRAYSCALE)
    return None if m is None else m.astype(np.float32) / 255.0


def composite(frame, i, scr_u8):
    """Put the screen into the frame (rows Y0..Y1) under the hand matte; despill the hand edges."""
    out = frame.copy()
    reg = out[Y0:Y1].astype(np.float32)
    a = matte(i)
    if a is None:
        a = np.zeros((SH, SW), np.float32)
    r, g, b = reg[..., 0], reg[..., 1], reg[..., 2]
    g2 = np.minimum(g, np.maximum(r, b) + 4)
    hand = np.dstack([r, g2, b])
    # feather the top / bottom edge of the display a touch
    ef = np.ones((SH, 1), np.float32)
    ef[0, 0] = 0.6
    ef[-1, 0] = 0.6
    a3 = a[..., None]
    comp = scr_u8.astype(np.float32) * (1 - a3) + hand * a3
    comp = comp * ef[..., None] + reg * (1 - ef[..., None])
    out[Y0:Y1] = np.clip(comp + 0.5, 0, 255).astype(np.uint8)
    return out


# ---------------------------------------------------------------------------------------------- finger -> front
@functools.lru_cache(maxsize=1)
def _front_table():
    """Fingertip x per frame: the hand-matte point farthest from where the arm enters (bottom right), median
    filtered, made monotonic (the line never un-draws) and lightly smoothed."""
    import json
    with open(os.path.join(G.GRP, 'leam_track.json')) as f:
        tr = json.load(f)
    fr = sorted(int(k) for k in tr)
    fx = np.array([tr[str(k)]['tip2'][0] if tr[str(k)].get('tip2') else np.nan for k in fr], np.float64)
    ok = ~np.isnan(fx)
    fx = np.interp(np.arange(len(fr)), np.nonzero(ok)[0], fx[ok])
    pad = np.pad(fx, 2, mode='edge')
    fx = np.array([np.median(pad[i:i + 5]) for i in range(len(fx))])
    fx = np.maximum.accumulate(fx)
    fx = np.convolve(np.pad(fx, 2, mode='edge'), np.ones(5) / 5, mode='valid')
    return np.array(fr, np.float64), fx


def finger_x(fi):
    fr, fx = _front_table()
    return float(np.interp(fi, fr, fx))


def front_x(t, fps=24.0):
    """Reveal front (screen px) = the fingertip's x plus a small lead (the chart spans the same x range)."""
    return finger_x(t * fps) + 10.0
