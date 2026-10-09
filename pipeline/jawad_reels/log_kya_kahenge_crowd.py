"""log_kya_kahenge_crowd.py - the procedural cardboard stadium of reel 5, C15 "Log Kya Kahenge" (motion-timeline-builder).

No Blender, no 3D props (BRIEF section 13): every element is a numpy sprite on a core.py plane or billboard, built once
per worker (lru_cache, read-only) and drawn in one painter pass per frame (pure function of the camera and a state).

    import jawad_kit                                         # FIRST
    import log_kya_kahenge_crowd as CR
    cam = CR.cam_wide()                                      # 24 mm hook / judgement / end wide (BRIEF 7.1)
    lay = CR.render(cam, t, CR.State(head=CR.snap_a(t)))     # stadium layer (premultiplied, transparent sky)
    cv = CR.backdrop(cam, t, CR.FLOOD) ; CR.over(cv, lay)    # sky + lamp bank, then the stands
    CR.head_mask(cam, t, state) / CR.eye_mask(cam, t, state) # QA masks (BRIEF 7.4)
    CR.scroller_rect(t)                                      # caption avoid rect around the focus-pulled scroller

WORLD (BRIEF 7.1; mm, x right, y DOWN, z away from the hook camera; bowl centre F = (0, 0, 0))
    rows i = 0..9: radius R_i = 7000 + 800 i, seat height h_i = 500 + 560 i, arc theta -75..+60 deg (+ = screen right).
    CARDS: strips of 4 seated figures (2080 x 1100 mm, bottom at h_i - 150, head tops ~h_i + 950) yawed to face F;
        every figure is its own 520 mm plane (coplanar inside its strip) so each head can carry its own state:
        'turned' = dark hair mass (x0.75 of the print grey, x0.60 at the crown), 'front' = light face plate (+40 %)
        + two AMBER catch-light eyes drawn per instance (r = max(0.035 head px, 1.5 px) on rows 0-5).
        Cut-edge band 6 px (ASH x1.6) at 0.4 while a card faces the lens, rising to 1.0 at |dot| <= 0.60;
        edge-on (|dot| < 0.2) an emissive ASH line (the "lines of light"). Backs: corrugated board, packing tape,
        one easel strut per figure (a plank perpendicular to the card). 10 silhouette variants x 2 flips.
    PEOPLE: 350 mm behind every card row, ~70 % of seats, heads bowed over a phone (AMBER x1.8 core, the only
        practical besides the floodlight). Billboards: a front texture seen from the field, a profile texture seen
        from the side (cross-faded by view angle); phones are separate glows at their own 3D point (bokeh discs
        when far out of focus).
    TIERS: one bench/riser wall per row (dark, a floodlit nose line) at R_i - 400; barrier 800 mm at 6600; field.
    LAMP BANK: 6 lamps (3 x 2) on a roof truss at (5200, -13500, 15500) -> CAM_WIDE (973, 172).
CAMERAS: cam_wide() 24 mm locked; cam_rows(psi, focus) 135 mm orbit about the row-3 pivot; cam_jd() 85 mm plate.
LIGHT: the layer is drawn with albedo textures and multiplied by a screen light map (flood = gentle fall-off from the
    bank side; warm = low FLAME light from screen-left); emissive items are pre-divided by the map so they keep their
    level. State.light = 0 (flood) .. 1 (warm).
COST (shared 4-core box, 1 sample): wide ~0.35-0.5 s, rows ~0.2-0.4 s, the orbit end ~0.4 s, emptied wide ~0.3 s.
"""
import functools
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import jawad_kit                                  # noqa: F401,E402  FIRST
from jawad_kit import K, J                        # noqa: E402

import cv2                                        # noqa: E402
import numpy as np                                # noqa: E402

W, H = K.W, K.H
FPS = K.FPS
PXMM = 0.5                                        # card texture px per mm
FIG_W, FIG_H = 520.0, 1100.0                      # one seated figure (mm)
TW, TH = int(FIG_W * PXMM), int(FIG_H * PXMM)     # 260 x 550 px
NROWS = 10
R0, DR, H0, DH = 7000.0, 800.0, 500.0, 560.0
TH0, TH1 = -75.0, 36.0               # BRIEF 7.1 has +60; the right flank is trimmed to +36 so the 135 mm side view
                                   # at psi 70 shows the pivot section, not a frame-filling near flank (all
                                   # other cameras never see past +30)
STRIP = 4
PEOPLE_BACK = 350.0                               # people sit this far behind (outside) their card row
BANK = np.array([5200.0, -13500.0, 15500.0])
PIVOT = (3215.0, -2630.0, 8833.0)                 # row 3 at theta = +20 deg (BRIEF 7.1)
LINE_DOT = 0.2                                    # |dot(view, normal)| below which the edge-on line shows


def R_(i):
    return R0 + DR * i


def h_(i):
    return H0 + DH * i


def C(name, k=1.0):
    return np.asarray(K.C[name], np.float32) * np.float32(k)


# ============================================================================================== cameras
def cam_wide():
    """CAM_WIDE (S1-01, S2-01, S6): 24 mm, locked. Lamp bank -> (972.8, 171.5)."""
    return K.Cam(pos=(0.0, -1500.0, 2000.0), pitch=10.0, focal=1280.0, aperture=6.0, focus_dist=9000.0)


def cam_rows(psi=0.0, focus=16000.0):
    """CAM_ROWS (S1-01B, S3-02, S4): 135 mm orbit about the row-3 pivot; psi 0 -> 70 deg turns the pivot cards edge-on."""
    return K.Cam.orbit(PIVOT, 16000.0, yaw=psi, pitch=3.0, focal=7200.0, aperture=60.0, focus_dist=focus)


def cam_jd():
    """CAM_JD (S5-01 plate): 85 mm, the emptied stands as bokeh above JD's bust."""
    return K.Cam(pos=(1100.0, -1500.0, -500.0), yaw=-6.0, pitch=12.0, focal=4533.0, aperture=70.0,
                 focus_dist=2500.0)


# ============================================================================================== textures
SS = 3                                            # supersampling for the silhouettes (area-downsampled)


def _grid(w, h, ss=SS):
    xs = (np.arange(w * ss, dtype=np.float32) + 0.5) / ss
    ys = (np.arange(h * ss, dtype=np.float32) + 0.5) / ss
    return np.meshgrid(xs, ys)


def _down(m, w, h):
    return cv2.resize(m.astype(np.float32), (w, h), interpolation=cv2.INTER_AREA)


def _ro(a):
    a = np.ascontiguousarray(a, np.float32)
    a.flags.writeable = False
    return a


def _rgba(rgb, a):
    out = np.zeros(a.shape + (4,), np.float32)
    out[..., :3] = rgb * a[..., None]
    out[..., 3] = a
    return out


@functools.lru_cache(maxsize=1)
def variant_params():
    """10 seated-figure silhouettes (texture px, 0.5 px/mm). Hair: crop, side part, jaw-length, bun, curls."""
    rng = np.random.default_rng(1505)
    styles = ['crop', 'side', 'long', 'bun', 'curly', 'crop', 'side', 'long', 'curly', 'crop']
    out = []
    for k, st in enumerate(styles):
        hw = float(rng.uniform(53, 61))
        hh = float(rng.uniform(66, 75))
        top = float(rng.uniform(20, 34))
        hx = 130.0 + float(rng.uniform(-6, 6))
        hy = top + hh
        ys = hy + hh + float(rng.uniform(14, 24))
        out.append(dict(k=k, style=st, hw=hw, hh=hh, hx=hx, hy=hy, top=top, nw=float(rng.uniform(44, 54)),
                        ys=ys, S=float(rng.uniform(92, 110)), side=float(rng.choice([-1, 1])),
                        seed=int(rng.integers(1 << 30))))
    return out


def _shapes(v):
    """1x coverage maps of one figure: full alpha, head mass, face plate (front), body."""
    X, Y = _grid(TW, TH)
    hx, hy, hw, hh = v['hx'], v['hy'], v['hw'], v['hh']
    head = ((X - hx) / hw) ** 2 + ((Y - hy) / hh) ** 2 <= 1.0
    st = v['style']
    if st == 'side':
        head |= ((X - (hx + 0.45 * hw * v['side'])) / (0.62 * hw)) ** 2 + ((Y - (hy - 0.62 * hh)) / (0.36 * hh)) ** 2 <= 1
    elif st == 'long':
        head |= (np.abs(X - hx) <= hw * 1.07) & (Y >= hy - 0.2 * hh) & (Y <= hy + 0.95 * hh) & \
                (((X - hx) / (hw * 1.07)) ** 4 + ((Y - (hy + 0.2 * hh)) / (0.8 * hh)) ** 4 <= 1)
    elif st == 'bun':
        head |= ((X - (hx + 6 * v['side'])) ** 2 + (Y - (hy - hh * 1.02)) ** 2) <= 21.0 ** 2
    elif st == 'curly':
        ang = np.arctan2(Y - hy, X - hx)
        rr = np.sqrt(((X - hx) / hw) ** 2 + ((Y - hy) / hh) ** 2)
        head |= rr <= 1.09 + 0.05 * np.sin(ang * 9 + v['seed'] % 7)
    neck = (np.abs(X - hx) <= v['nw'] / 2) & (Y >= hy + 0.5 * hh) & (Y <= v['ys'] + 12)
    S, ys = v['S'], v['ys']
    cap = 46.0
    yb = ys + 58.0
    shoulder = (Y >= ys) & (((np.abs(X - hx) / S) ** 2.6 + (np.clip(ys + cap - Y, 0, None) / cap) ** 2.6) <= 1.0)
    board = Y >= yb
    body = neck | shoulder | board
    full = head | body
    plate = ((X - hx) / (0.72 * hw)) ** 2 + ((Y - (hy + 0.12 * hh)) / (0.80 * hh)) ** 2 <= 1.0
    plate &= ((X - hx) / hw) ** 2 + ((Y - hy) / hh) ** 2 <= 1.0
    return dict(full=_down(full, TW, TH), head=_down(head, TW, TH), plate=_down(plate, TW, TH),
                body=_down(body & ~head, TW, TH), yb=yb)


def _band(alpha, width=6):
    """Cut-edge band along the TOP silhouette (sides and bottom are padded: strips join without a seam)."""
    p = 12
    a = cv2.copyMakeBorder(alpha, p, p, p, p, cv2.BORDER_REPLICATE)
    a[:p] = 0.0                                                   # the open sky above the heads
    k = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * width + 1, 2 * width + 1))
    inner = cv2.erode(a, k)
    b = np.clip(a - inner, 0, 1)[p:-p, p:-p]
    return cv2.GaussianBlur(b, (0, 0), 0.6) * alpha


def _flood_grad(h=TH):
    y = np.arange(h, dtype=np.float32)[:, None]
    return 0.80 + 0.20 * np.exp(-y / 200.0)


@functools.lru_cache(maxsize=1)
def figure_textures():
    """Per variant v (0..9) and flip (0/1): dict of read-only sprites
    front, turned (combined), body, head_front, head_turned (cropped to head_box), back, band (extra band layer),
    mask (rgb = (head, 0, 0), alpha = full) + geometry (head ellipse, eyes, neck point, head crop box)."""
    grey = np.asarray(K.mix(K.C['SMOKE'], K.C['ASH'], 0.35), np.float32)
    ash = C('ASH')
    back_base = np.asarray(K.mix(K.mix(K.C['SMOKE'], K.C['ASH'], 0.30), K.C['GOLD'], 0.14), np.float32) * 0.95
    brown = np.asarray(K.mix(K.C['SMOKE'], K.C['GOLD'], 0.55), np.float32)
    grad = _flood_grad()
    out = {}
    for v in variant_params():
        sh = _shapes(v)
        rng = np.random.default_rng(v['seed'])
        full, head, plate, body = sh['full'], sh['head'], sh['plate'], sh['body']
        X, Y = np.meshgrid(np.arange(TW, dtype=np.float32) + 0.5, np.arange(TH, dtype=np.float32) + 0.5)
        hx, hy, hw, hh = v['hx'], v['hy'], v['hw'], v['hh']
        # printed grey with the top floodlight: a top-down gradient, lit shoulder tops, a short shadow under the head
        noise = cv2.GaussianBlur(rng.standard_normal((TH, TW)).astype(np.float32), (0, 0), 1.2) * 0.025
        shade = grad * (1.0 + noise)
        shade = shade * (1.0 - 0.32 * np.exp(-((Y - (hy + hh + 10)) / 16.0) ** 2) * (np.abs(X - hx) < hw * 0.95))
        shade = shade * (1.0 + 0.16 * np.exp(-((Y - (v['ys'] + 4)) / 10.0) ** 2) * (np.abs(X - hx) < v['S']))
        body_rgb = grey[None, None, :] * shade[..., None]
        # front head: hair at x1.0, face plate +40 % (soft 1 px edge), clamped to ASH
        pl = cv2.GaussianBlur(plate, (0, 0), 0.6)
        front_head = grey[None, None, :] * (shade * (1.0 + 0.40 * pl))[..., None]
        front_head = np.minimum(front_head, ash)
        # turned head: dark hair mass x0.75, ramp to x0.60 at the crown (15 % .. 45 % of the head height)
        vfrac = (Y - (hy - hh)) / (2 * hh)
        ramp = np.interp(vfrac, [0.15, 0.45], [0.60, 0.75]).astype(np.float32)
        turned_head = grey[None, None, :] * (shade * ramp)[..., None]
        band = _band(full)
        bandc = ash * 1.6

        def comp(rgb_head, alpha_head):
            rgb = body_rgb * (1.0 - alpha_head[..., None]) + rgb_head * alpha_head[..., None]
            rgb = rgb * (1.0 - 0.4 * band[..., None]) + 0.4 * band[..., None] * bandc
            return _rgba(rgb, full)
        front = comp(front_head, head)
        turned = comp(turned_head, head)
        body_only_a = np.clip(full - head, 0, 1)
        brgb = body_rgb * (1.0 - 0.4 * band[..., None]) + 0.4 * band[..., None] * bandc
        body_spr = _rgba(brgb, body_only_a)
        # head crop box (+ band) for the separately drawn head (snap / tilt)
        ys_, xs_ = np.nonzero(head > 0.002)
        x0, y0 = max(0, xs_.min() - 3), max(0, ys_.min() - 3)
        x1, y1 = min(TW, xs_.max() + 4), min(TH, int(hy + hh) + 14)
        hb = band[y0:y1, x0:x1, None]

        def headspr(rgb):
            r = rgb[y0:y1, x0:x1] * (1.0 - 0.4 * hb) + 0.4 * hb * bandc
            a = head[y0:y1, x0:x1].copy()
            a[-10:] *= np.linspace(1.0, 0.0, 10, dtype=np.float32)[:, None]   # soft neck seam (body covers it)
            return _rgba(r, a)
        hf, ht = headspr(front_head), headspr(turned_head)
        # back: corrugated board (flutes every 8 mm), 2-3 strips of packing tape, warm band
        fl = 1.0 + 0.06 * np.sin(2 * math.pi * X / 4.0)
        bk = back_base[None, None, :] * (fl * grad)[..., None]
        tape = np.zeros((TH, TW), np.float32)
        ntape = 2 + int(rng.integers(0, 2))
        for kk in range(ntape):
            if kk == 0:                                               # across the strut fixing (60 % height)
                yc = TH - 0.6 * TH + rng.uniform(-14, 14)
                tape = np.maximum(tape, (np.abs(Y - yc) < 12).astype(np.float32))
            else:
                ang = math.radians(rng.uniform(-35, 35))
                xc, yc = rng.uniform(40, TW - 40), rng.uniform(sh['yb'] + 20, TH - 40)
                d = np.abs((X - xc) * math.sin(ang) - (Y - yc) * math.cos(ang))
                along = np.abs((X - xc) * math.cos(ang) + (Y - yc) * math.sin(ang))
                tape = np.maximum(tape, ((d < 12) & (along < rng.uniform(50, 90))).astype(np.float32))
        tape = cv2.GaussianBlur(tape, (0, 0), 0.7)
        tape_rgb = (bk * 1.25) * 0.7 + C('AMBER', 0.3)[None, None, :] * np.mean(bk * 1.25, axis=2, keepdims=True) * 0.3 / 0.46
        bk = bk * (1.0 - tape[..., None]) + tape_rgb * tape[..., None]
        bk = bk * (1.0 - 0.4 * band[..., None]) + 0.4 * band[..., None] * (brown * 1.4)
        back = _rgba(bk, full)
        bandspr = _rgba(np.broadcast_to(bandc, (TH, TW, 3)) * 1.0, band)          # extra band (obliquity)
        bandback = _rgba(np.broadcast_to(brown * 1.4, (TH, TW, 3)) * 1.0, band)
        mask = np.zeros((TH, TW, 4), np.float32)
        mask[..., 0] = head * full
        mask[..., 3] = full
        geo = dict(hx=hx, hy=hy, hw=hw, hh=hh, eyes=((hx - 0.18 * 2 * hw, hy - 0.02 * 2 * hh),
                                                     (hx + 0.18 * 2 * hw, hy - 0.02 * 2 * hh)),
                   neck=(hx, hy + hh * 0.92), box=(x0, y0, x1, y1), top=v['top'])
        for flip in (0, 1):
            def F_(a):
                return _ro(a[:, ::-1] if flip else a)
            g = dict(geo)
            if flip:
                g = dict(hx=TW - hx, hy=hy, hw=hw, hh=hh, eyes=tuple((TW - ex, ey) for ex, ey in geo['eyes'][::-1]),
                         neck=(TW - geo['neck'][0], geo['neck'][1]), box=(TW - x1, y0, TW - x0, y1), top=v['top'])
            out[(v['k'], flip)] = dict(front=F_(front), turned=F_(turned), body=F_(body_spr), head_front=F_(hf),
                                       head_turned=F_(ht), back=F_(back), band=F_(bandspr), bandback=F_(bandback),
                                       mask=F_(mask), geo=g)
    return out


@functools.lru_cache(maxsize=1)
def strut_texture():
    """Easel strut: 40 x 800 mm plank (20 x 400 px), warm wood with grain lines."""
    rng = np.random.default_rng(77)
    w, h = 20, 400
    base = np.asarray(K.mix(K.C['SMOKE'], K.C['GOLD'], 0.45), np.float32)
    X, Y = np.meshgrid(np.arange(w, dtype=np.float32), np.arange(h, dtype=np.float32))
    grain = 1.0 + 0.10 * np.sin(X * 1.7 + np.sin(Y / 23.0) * 2.0) + 0.05 * rng.standard_normal((h, w)).astype(np.float32)
    rgb = base[None, None, :] * grain[..., None] * _flood_grad(h)[..., None] * 0.6
    a = np.ones((h, w), np.float32)
    a[:, 0] = a[:, -1] = 0.6
    return _ro(_rgba(rgb, a))


@functools.lru_cache(maxsize=1)
def line_sprite():
    """Edge-on card: a 4 px emissive ASH x1.4 line with a 2 px glow (unit height 200 px, scaled to the card)."""
    w, h = 24, 200
    x = np.arange(w, dtype=np.float32) - (w - 1) / 2
    core = np.clip(2.2 - np.abs(x), 0, 1) * 1.6
    glow = np.exp(-(x / 3.2) ** 2) * 0.55 + np.exp(-(x / 7.0) ** 2) * 0.12
    prof = np.maximum(core, glow)
    yy = np.arange(h, dtype=np.float32)
    vert = np.clip(np.minimum(yy, h - 1 - yy) / 3.0, 0, 1)
    m = prof[None, :] * vert[:, None]
    spr = np.zeros((h, w, 4), np.float32)
    spr[..., :3] = m[..., None] * C('ASH', 1.4)
    spr[..., 3] = np.clip(core[None, :] * vert[:, None], 0, 1)
    spr[..., :3] *= 1.3
    return _ro(spr)


# ---------------------------------------------------------------------------------------------- people
PPX = 0.4                                          # people texture px per mm
PW, PH = 240, 508                                  # 600 x 1270 mm; anchor = seat point
P_ANCHOR = (0.5, 328.0 / PH)                       # seat at y 328 (feet 450 mm below, head top 820 above)


def _poly(mask_ss, pts, ss=SS):
    cv2.fillPoly(mask_ss, [np.int32(np.round(np.asarray(pts) * ss))], 1.0)


def _ell(mask_ss, c, ax, ang=0.0, ss=SS):
    cv2.ellipse(mask_ss, (int(round(c[0] * ss)), int(round(c[1] * ss))), (int(round(ax[0] * ss)), int(round(ax[1] * ss))),
                ang, 0, 360, 1.0, -1)


def _line(mask_ss, p0, p1, wdt, ss=SS):
    cv2.line(mask_ss, (int(round(p0[0] * ss)), int(round(p0[1] * ss))), (int(round(p1[0] * ss)), int(round(p1[1] * ss))),
             1.0, int(round(wdt * ss)))


def _person(kind, k):
    """One person silhouette at 0.4 px/mm: kind 'front' (seen from the field), 'profile' (facing screen-left, toward
    the field), 'lookup' (profile, head raised). Dark SMOKE / NIGHT_1, lit only by the phone (amber underlight)."""
    rng = np.random.default_rng(900 + 31 * k + {'front': 0, 'profile': 7, 'lookup': 13}[kind])
    m = np.zeros((PH * SS, PW * SS), np.float32)
    s = rng.uniform(0.94, 1.06)
    sx = 120.0
    seat = 328.0
    if kind == 'front':
        hr = (rng.uniform(42, 48) * s, rng.uniform(44, 50) * s)
        hc = (sx + rng.uniform(-4, 4), seat - 262 * s)
        _ell(m, hc, hr)
        sh = rng.uniform(78, 92) * s
        _poly(m, [(sx - sh, seat - 175 * s), (sx - sh * 0.8, seat - 205 * s), (sx - 30, seat - 222 * s),
                  (sx + 30, seat - 222 * s), (sx + sh * 0.8, seat - 205 * s), (sx + sh, seat - 175 * s),
                  (sx + sh * 0.86, seat + 6), (sx - sh * 0.86, seat + 6)])
        for sg in (-1, 1):                                           # forearms to the phone at the chest
            _line(m, (sx + sg * sh * 0.85, seat - 150 * s), (sx + sg * 14, seat - 152 * s), 26 * s)
            _poly(m, [(sx + sg * 18, seat), (sx + sg * 62, seat), (sx + sg * 58, seat + 175), (sx + sg * 20, seat + 175)])
        phone = (sx, seat - 152 * s)
        if rng.random() < 0.4:                                       # longer hair
            _ell(m, (hc[0], hc[1] + 18), (hr[0] * 1.05, hr[1] * 0.9))
    else:
        up = kind == 'lookup'
        hc = (sx - 36 * s, seat - (282 if up else 236) * s)
        hr = (rng.uniform(40, 46) * s, rng.uniform(46, 52) * s)
        _ell(m, hc, hr, ang=(-10 if up else 32))
        _poly(m, [(sx + 46 * s, seat + 4), (sx + 52 * s, seat - 120 * s), (sx + 20 * s, seat - 210 * s),
                  (sx - 18 * s, seat - 220 * s), (sx - 40 * s, seat - 190 * s), (sx - 30 * s, seat - 60 * s),
                  (sx - 30 * s, seat + 4)])
        _line(m, (sx + 30 * s, seat - 18), (sx - 112 * s, seat - 8), 64 * s)           # thigh
        _line(m, (sx - 108 * s, seat - 4), (sx - 100 * s, seat + 168), 46 * s)          # shin
        _line(m, (sx - 120 * s, seat + 170), (sx - 72 * s, seat + 172), 22 * s)         # foot
        _line(m, (sx - 4 * s, seat - 186 * s), (sx - 18 * s, seat - 108 * s), 30 * s)   # upper arm
        _line(m, (sx - 18 * s, seat - 108 * s), (sx - 82 * s, seat - 138 * s), 26 * s)  # forearm
        phone = (sx - 88 * s, seat - 142 * s)
    a = _down(np.clip(m, 0, 1), PW, PH)
    a = cv2.GaussianBlur(a, (0, 0), 0.5)
    X, Y = np.meshgrid(np.arange(PW, dtype=np.float32), np.arange(PH, dtype=np.float32))
    base = np.asarray(K.mix(K.C['NIGHT_1'], K.C['SMOKE'], 0.6), np.float32) * 0.9
    d2 = ((X - phone[0]) ** 2 + ((Y - phone[1]) * 1.15) ** 2)
    under = np.exp(-d2 / (2 * 46.0 ** 2)) + 0.35 * np.exp(-d2 / (2 * 110.0 ** 2))
    if kind != 'front':
        under *= np.clip(1.0 - (X - phone[0]) / 140.0, 0.15, 1.0)    # the face side toward the screen
        fc = (hc[0] - 0.55 * hr[0], hc[1] + 0.35 * hr[1])            # the bowed face, lit from the screen below
        under = under + 0.9 * np.exp(-((X - fc[0]) ** 2 + (Y - fc[1]) ** 2) / (2 * 22.0 ** 2))
    else:
        under = under + 0.5 * np.exp(-((X - hc[0]) ** 2 + ((Y - (hc[1] + 0.7 * hr[1])) * 1.6) ** 2) / (2 * 24.0 ** 2))
    rgb = base[None, None, :] + under[..., None] * C('AMBER', 0.34)
    # the floodlight from above: a thin rim on the crown and shoulders (silhouettes separate from the dark)
    inner = cv2.erode(a, np.ones((5, 5), np.uint8))
    top = np.clip(a - np.roll(a, 4, axis=0), 0, 1) * (1.0 - inner * 0.5)
    rgb = rgb + top[..., None] * C('ASH', 0.20) * np.clip(1.2 - Y / 300.0, 0, 1)[..., None]
    return _ro(_rgba(rgb, a)), (phone[0] / PW, phone[1] / PH)


@functools.lru_cache(maxsize=1)
def people_textures():
    """{'front': [(spr, phone_uv)] x4, 'profile': [...] x4 (facing left), 'profile_r': mirrored, 'lookup': [...]}."""
    out = {'front': [_person('front', k) for k in range(4)], 'profile': [_person('profile', k) for k in range(4)],
           'lookup': [_person('lookup', 0)]}
    out['profile_r'] = [(_ro(s[:, ::-1]), (1.0 - uv[0], uv[1])) for s, uv in out['profile']]
    out['lookup_r'] = [(_ro(s[:, ::-1]), (1.0 - uv[0], uv[1])) for s, uv in out['lookup']]
    return out


@functools.lru_cache(maxsize=1)
def phone_sprite():
    """Phone glow (billboard, 360 mm wide sprite): a 70 x 140 mm AMBER x1.8 core + a soft halo. 0.4 px/mm."""
    n = 144
    X, Y = np.meshgrid(np.arange(n, dtype=np.float32) - (n - 1) / 2, np.arange(n, dtype=np.float32) - (n - 1) / 2)
    core = np.clip(6.5 - np.abs(X), 0, 1) * np.clip(11.5 - np.abs(Y), 0, 1)
    core = cv2.GaussianBlur(core.astype(np.float32), (0, 0), 2.2) * 0.85
    halo = np.exp(-(X ** 2 + Y ** 2) / (2 * 13.0 ** 2)) * 0.30 + np.exp(-(X ** 2 + Y ** 2) / (2 * 36.0 ** 2)) * 0.06
    spr = np.zeros((n, n, 4), np.float32)
    spr[..., :3] = core[..., None] * C('AMBER', 1.8) + halo[..., None] * C('AMBER', 1.0)
    spr[..., 3] = 0.0                                                  # emissive (added light)
    return _ro(spr)


@functools.lru_cache(maxsize=32)
def bokeh_disc(r):
    """Out-of-focus phone: a flat AMBER disc with a brighter rim (unit energy scale), radius r px."""
    r = max(2, int(r))
    n = r + 3
    X, Y = np.meshgrid(np.arange(-n, n + 1, dtype=np.float32), np.arange(-n, n + 1, dtype=np.float32))
    d = np.sqrt(X * X + Y * Y)
    body = np.clip((r - d) / 1.2 + 0.5, 0, 1)
    rim = np.clip((d / r - 0.62) / 0.36, 0, 1) ** 2
    prof = body * (0.62 + 0.55 * rim)
    spr = np.zeros(d.shape + (4,), np.float32)
    spr[..., :3] = prof[..., None] * C('AMBER')
    return _ro(spr)


# ---------------------------------------------------------------------------------------------- tiers, bank, floor
@functools.lru_cache(maxsize=1)
def wall_texture():
    """Bench / riser wall: dark, a floodlit nose line on the top edge (unit 400 x 120 px)."""
    w, h = 400, 120
    rng = np.random.default_rng(5)
    Y = np.arange(h, dtype=np.float32)[:, None]
    base = np.asarray(K.mix(K.C['NIGHT_1'], K.C['SMOKE'], 0.55), np.float32)
    shade = (0.75 + 0.25 * np.exp(-Y / 30.0)) * (1.0 + 0.04 * rng.standard_normal((h, w)).astype(np.float32))
    rgb = base[None, None, :] * shade[..., None]
    nose = np.exp(-((Y - 2.0) / 1.8) ** 2)
    rgb = rgb + nose[..., None] * C('ASH', 0.55)
    return _ro(_rgba(rgb, np.ones((h, w), np.float32)))


@functools.lru_cache(maxsize=1)
def floor_texture():
    n = 256
    yy, xx = np.mgrid[0:n, 0:n].astype(np.float32) / n
    # field floor (texture v = 0 near the camera, z -2500 .. +10500): NIGHT_1, the floodlight's spill brightest at the
    # barrier foot (z ~6600, v ~0.70) and toward the bank side; never a pool at centre field (no spotlight)
    spill = np.exp(-((yy - 0.70) / 0.16) ** 2) * (0.75 + 0.5 * xx)
    rgb = C('NIGHT_1')[None, None, :] * (0.9 + 3.2 * spill)[..., None]
    return _ro(_rgba(rgb, np.ones((n, n), np.float32)))


@functools.lru_cache(maxsize=1)
def bank_sprite():
    """Floodlight bank: 6 lamps (3 x 2, 600 x 700 mm, 140 mm gaps) in a dark housing, cores AMBER x2.6 with a hot
    centre, FLAME glow. Returns (sprite, width in mm)."""
    s = 0.2                                                            # px per mm
    W_MM, H_MM = 3000.0, 2400.0
    w, h = int(W_MM * s), int(H_MM * s)
    spr = np.zeros((h, w, 4), np.float32)
    gw, gh = 3 * 690 + 2 * 120, 2 * 790 + 120
    x0, y0 = int((W_MM - gw) / 2 * s), int((H_MM - gh) / 2 * s)
    hous = np.zeros((h, w), np.float32)
    hous[y0 - 6:y0 + int(gh * s) + 6, x0 - 6:x0 + int(gw * s) + 6] = 1.0
    spr[..., :3] = hous[..., None] * C('SMOKE', 0.6)
    spr[..., 3] = hous
    for r in range(2):
        for c in range(3):
            lx, ly = x0 + int(c * 810 * s), y0 + int(r * 910 * s)
            lw, lh = int(690 * s), int(790 * s)
            yy, xx = np.mgrid[0:lh, 0:lw].astype(np.float32)
            hot = np.exp(-(((xx - lw / 2) / (lw * 0.5)) ** 2 + ((yy - lh / 2) / (lh * 0.5)) ** 2) * 1.2)
            edge = np.clip(np.minimum(np.minimum(xx, lw - 1 - xx), np.minimum(yy, lh - 1 - yy)) / 3.0, 0, 1)
            spr[ly:ly + lh, lx:lx + lw, :3] = (C('AMBER', 2.6) * (0.8 + 0.2 * hot[..., None]) +
                                               C('WHITE', 0.9) * hot[..., None] ** 2) * edge[..., None]
            spr[ly:ly + lh, lx:lx + lw, 3] = 1.0
    g = K.glow(spr, K.C['FLAME'], sigmas=(6, 18, 46), strength=1.25, source='rgb')
    return _ro(g), W_MM * g.shape[1] / w


@functools.lru_cache(maxsize=1)
def truss_sprite():
    """A dark roof-edge truss the bank hangs on (8000 x 300 mm), faintly lit underside."""
    w, h = 800, 30
    spr = np.zeros((h, w, 4), np.float32)
    spr[..., :3] = C('SMOKE', 0.5)
    spr[-3:, :, :3] = C('ASH', 0.18)
    spr[..., 3] = 1.0
    return _ro(spr)


# ============================================================================================== seats
@functools.lru_cache(maxsize=1)
def seats():
    """Every figure (cards) and every person (people) as numpy arrays (read-only, built once)."""
    rng = np.random.default_rng(15)
    fig = dict(row=[], strip=[], j=[], th=[], yaw=[], B=[], var=[], flip=[], ph=[], fq=[])
    sid = 0
    for i in range(NROWS):
        R, h = R_(i), h_(i)
        dth = math.degrees(STRIP * FIG_W / R)
        n = int(math.floor((TH1 - TH0) / dth))
        start = TH0 + ((TH1 - TH0) - n * dth) / 2
        for s in range(n):
            ths = start + (s + 0.5) * dth
            r = math.radians(ths)
            Cc = np.array([R * math.sin(r), -(h - 150.0), R * math.cos(r)])
            tang = np.array([math.cos(r), 0.0, -math.sin(r)])
            ph, fq = rng.uniform(0, 2 * math.pi), rng.uniform(0.32, 0.55)
            for j in range(STRIP):
                fig['row'].append(i)
                fig['strip'].append(sid)
                fig['j'].append(j)
                fig['th'].append(ths)
                fig['yaw'].append(ths)
                fig['B'].append(Cc + tang * (j - 1.5) * FIG_W)
                fig['var'].append(int(rng.integers(0, 10)))
                fig['flip'].append(int(rng.integers(0, 2)))
                fig['ph'].append(ph)
                fig['fq'].append(fq)
            sid += 1
    F = {k: np.asarray(v) for k, v in fig.items()}
    # the "last card": row 9 near theta +11 deg survives the burn and tips over at 29.2 s (one figure)
    r9 = np.flatnonzero(F['row'] == 9)
    F['last'] = int(r9[np.argmin(np.abs(np.degrees(np.arctan2(F['B'][r9, 0], F['B'][r9, 2])) - 11.0))])
    # uncomposed: one narrower card in row 6 leaning 3 deg off true; one card sways later than its row
    r6 = np.flatnonzero(F['row'] == 6)
    F['lean_odd'] = int(r6[np.argmin(np.abs(np.degrees(np.arctan2(F['B'][r6, 0], F['B'][r6, 2])) + 6.0))])
    r4 = np.flatnonzero(F['row'] == 4)
    F['late_sway'] = int(r4[np.argmin(np.abs(np.degrees(np.arctan2(F['B'][r4, 0], F['B'][r4, 2])) - 4.0))])
    F['late_tilt'] = int(np.flatnonzero((F['row'] == 3))[len(np.flatnonzero(F['row'] == 3)) // 2 + 3])
    # people: one seat per figure position, 350 mm further out, ~70 % occupied
    P = dict(row=[], B=[], inward=[], var=[], occ=[], fig=[])
    for k in range(len(F['row'])):
        i = F['row'][k]
        b = F['B'][k]
        r = math.atan2(b[0], b[2])
        out_ = np.array([math.sin(r), 0.0, math.cos(r)])
        seat = b + out_ * PEOPLE_BACK + np.array([0.0, 30.0, 0.0])          # seat ~120 mm below the card's h
        P['row'].append(i)
        P['B'].append(seat)
        P['inward'].append(-out_)
        P['var'].append(int(rng.integers(0, 4)))
        P['occ'].append(rng.random() < 0.70)
        P['fig'].append(k)
    Pp = {k: np.asarray(v) for k, v in P.items()}
    F = {k: _ro(v) if isinstance(v, np.ndarray) and v.dtype != object else v for k, v in F.items()}
    return F, Pp


# ---------------------------------------------------------------------------------------------- special people
def _view_people(psi=70.0):
    F, P = seats()
    cam = cam_rows(psi)
    xy, z = cam.project(P['B'] + np.array([0.0, -380.0, 0.0]) + P['inward'] * 220.0)
    return xy, z


@functools.lru_cache(maxsize=1)
def specials():
    """Indices of the scroller (focus-pull target), the look-up person (two seats to his left), the empty seats."""
    F, P = seats()
    xy, z = _view_people(70.0)
    occ = P['occ']
    # scroller: an occupied seat whose phone lands near the brief's target (600, 1080) at psi = 70, nearer than the
    # pivot lines (16.0 m) so the focus pull from the card lines to him reads (14-15.3 m)
    cost = np.hypot(xy[:, 0] - 600.0, xy[:, 1] - 1060.0) + 0.05 * np.abs(z - 14400.0)
    cost[~occ | ~np.isfinite(cost) | (z < 13600) | (z > 15300)] = 1e9
    sc = int(np.argmin(cost))
    row = P['row'][sc]
    same = np.flatnonzero((P['row'] == row) & occ)
    xs = xy[same, 0]
    left = same[(xs < xy[sc, 0] - 20)]
    lk = int(left[np.argsort(xy[left, 0])[::-1][1]]) if len(left) > 1 else int(same[0])
    # an empty seat in row 1 and a seat in row 2 with only a phone glow (S6 wide): near frame centre in CAM_WIDE
    cw = cam_wide()
    xw, _ = cam_wide().project(P['B'])
    r1 = np.flatnonzero(P['row'] == 1)
    e1 = int(r1[np.argmin(np.abs(xw[r1, 0] - 380.0))])
    r2 = np.flatnonzero(P['row'] == 2)
    g2 = int(r2[np.argmin(np.abs(xw[r2, 0] - 700.0))])
    del cw
    return dict(scroller=sc, lookup=lk, empty=e1, ghost=g2)


# ============================================================================================== state + timing
class State:
    """What the stadium shows at one instant (a plain value object; build one per frame).
    head: None (all turned) | float 0..1 (all) | callable(xs) -> per-figure 0..1 (0 = turned, 1 = front)
    jolt: callable(xs) -> per-figure px of head jolt (snap) or None
    tilt: head tilt deg (in sync) | tilt_late (the one late head)
    lean: card scale about the seat line; flap: None | per-row angle array (deg, 0 upright, -90 flat back)
    cards: 0/1 draw the cards; people: 0..1; phones: 0..1; light: 0 flood .. 1 warm; part: 'all' | 'cards' | 'nocards'
    last_tip: the last card's tip angle (deg, 0 upright .. -90 flat); eyes: 1/0; lines: edge-on lines on/off
    tap: scroller phone brightness multiplier; lookup: 0..1 (the one person looking up); key: warm key gain"""

    def __init__(self, **kw):
        self.head = kw.get('head', 1.0)
        self.jolt = kw.get('jolt')
        self.tilt = kw.get('tilt', 0.0)
        self.tilt_late = kw.get('tilt_late', self.tilt)
        self.lean = kw.get('lean', 1.0)
        self.flap = kw.get('flap')
        self.cards = kw.get('cards', 1.0)
        self.people = kw.get('people', 0.0)
        self.phones = kw.get('phones', self.people)
        self.light = kw.get('light', 0.0)
        self.part = kw.get('part', 'all')
        self.last_tip = kw.get('last_tip', 0.0)
        self.last = kw.get('last', True)               # draw the last card (burned with the rest when False)
        self.eyes = kw.get('eyes', 1.0)
        self.lines = kw.get('lines', True)
        self.tap = kw.get('tap', 1.0)
        self.lookup = kw.get('lookup', 0.0)
        self.near_cull = kw.get('near_cull', 0.0)      # fade items nearer than this camera depth (orbit flank)
        self.t = kw.get('t', 0.0)
        self.mask = kw.get('mask', None)               # None | 'head' | 'eye' (QA render)
        self.walls = kw.get('walls', 1.0)
        self.empty = kw.get('empty', False)            # S6: the empty row-1 seat and the phone-only seat
        self.fog = kw.get('fog', 0.0)                  # 0..1 depth darkening beyond fog_d0 (the orbit's far side)
        self.fog_d0 = kw.get('fog_d0', 16800.0)


def sway(F, t):
    """Card micro-sway (deg, about each card's seat line): +-0.3 deg, per strip phase; one card lags its row."""
    a = 0.3 * np.sin(2 * math.pi * F['fq'] * t + F['ph'])
    k = F['late_sway']
    a = np.array(a)
    a[k] = 0.3 * math.sin(2 * math.pi * F['fq'][k] * (t - 0.35) + F['ph'][k])
    return a


@functools.lru_cache(maxsize=4)
def head_screen_x(which):
    """Screen x of every figure's head centre in the snap camera ('wide' = CAM_WIDE, 'rows' = CAM_ROWS psi 0)."""
    F, _ = seats()
    T = figure_textures()
    cam = cam_wide() if which == 'wide' else cam_rows(0.0)
    pts = []
    for k in range(len(F['row'])):
        g = T[(int(F['var'][k]), int(F['flip'][k]))]['geo']
        uv = (g['hx'] / TW, g['hy'] / TH)
        pts.append(K.plane_point(F['B'][k], FIG_W, FIG_H, rot=(0.0, float(F['yaw'][k]), 0.0), uv=uv, anchor=(0.5, 1.0)))
    xy, _ = cam.project(np.array(pts))
    x = np.nan_to_num(xy[:, 0], nan=-4000.0)
    x.flags.writeable = False
    return x


def snap_state(t, which='wide', t0=0.2, spread=0.4):
    """Head-snap wave (BRIEF 6.1 / 6.2): each head flips turned -> front over 3 frames from
    t_s(x) = t0 + spread |x - 540| / 540 (x = its screen x in the snap camera). Returns (w, jolt) callables' arrays."""
    x = head_screen_x(which)
    ts = t0 + spread * np.abs(x - 540.0) / 540.0
    u = np.clip((t - ts) / (3.0 / FPS), 0, 1)
    w = u * u * (3 - 2 * u)
    # SNAP: a 2 px jolt (up) that springs back: sin-shaped, starts at 0 on the flip start, gone in ~6 frames
    d = t - ts
    jolt = np.where(d > 0, 2.0 * np.exp(-d * 18.0) * np.sin(np.clip(d, 0, None) * 2 * math.pi * 3.0), 0.0)
    return w, jolt


# ============================================================================================== light maps
@functools.lru_cache(maxsize=4)
def _light_map_lo(kind):
    lw, lh = W // 8, H // 8
    X, Y = np.meshgrid((np.arange(lw, dtype=np.float32) + 0.5) / lw, (np.arange(lh, dtype=np.float32) + 0.5) / lh)
    if kind == 'flood':
        # one hard top floodlight from the bank (top right): a gentle diagonal fall-off, warm-neutral
        d = np.sqrt(((X - 0.95) / 1.25) ** 2 + ((Y - 0.05) / 1.1) ** 2)
        g = 1.30 - 0.45 * np.clip(d, 0, 1) ** 1.3
        m = g[..., None] * np.float32([1.0, 0.97, 0.93])
    elif kind == 'rows':
        g = 1.0 - 0.18 * np.clip(Y - 0.2, 0, 1)
        m = g[..., None] * np.float32([1.0, 0.97, 0.93])
    else:
        # warm: one low FLAME light at the field's edge, screen left; the right side falls off, a little ambient
        fl = np.asarray(K.C['FLAME'], np.float32) * 0.55 + np.asarray(K.C['AMBER'], np.float32) * 0.45
        g = np.exp(-(X / 0.62) ** 1.6) * (0.85 + 0.25 * np.clip(Y - 0.25, 0, 1))
        m = 0.10 * np.float32([1.0, 0.85, 0.75])[None, None, :] + (2.4 * g)[..., None] * fl[None, None, :]
    return m.astype(np.float32)


def light_map(light, kind_flood='flood'):
    """Full-res (H, W, 3) light map for State.light (0 flood .. 1 warm)."""
    a = _light_map_lo(kind_flood)
    if light >= 1.0:
        lo = _light_map_lo('warm')
    elif light <= 0.0:
        lo = a
    else:
        lo = a * np.float32(1 - light) + _light_map_lo('warm') * np.float32(light)
    return cv2.resize(lo, (W, H), interpolation=cv2.INTER_LINEAR)


def light_at(light, kind_flood, xy):
    """Light map value at screen points (N, 2) -> (N, 3) (for emissive pre-compensation)."""
    lo = _light_map_lo(kind_flood) * np.float32(1 - light) + _light_map_lo('warm') * np.float32(light) \
        if 0 < light < 1 else (_light_map_lo('warm') if light >= 1 else _light_map_lo(kind_flood))
    lw, lh = lo.shape[1], lo.shape[0]
    ix = np.clip((np.asarray(xy)[:, 0] / W * lw).astype(int), 0, lw - 1)
    iy = np.clip((np.asarray(xy)[:, 1] / H * lh).astype(int), 0, lh - 1)
    return lo[iy, ix]


# ============================================================================================== the painter
def _vis_fig(cam, F, idx, margin=260):
    """Figures whose card quad can touch the frame (cheap pre-cull, vectorised)."""
    B = F['B'][idx]
    top = B + np.array([0.0, -FIG_H, 0.0])
    xy0, z0 = cam.project(B)
    xy1, z1 = cam.project(top)
    ok = (z0 > cam.near) | (z1 > cam.near)
    x = np.nan_to_num(np.c_[xy0[:, 0], xy1[:, 0]], nan=1e6)
    y = np.nan_to_num(np.c_[xy0[:, 1], xy1[:, 1]], nan=1e6)
    span = np.maximum(np.abs(xy0[:, 1] - xy1[:, 1]), 50)
    span = np.nan_to_num(span, nan=4000.0)
    m = margin + span * 0.6
    ok &= (x.max(1) > -m) & (x.min(1) < W + m) & (y.max(1) > -m) & (y.min(1) < H + m)
    return idx[ok], np.minimum(z0, z1)[ok]


def _dofblur(cam, z):
    return float(cam.coc(max(z, 1.0))) * 0.5 if cam.aperture > 0 else 0.0


def render(cam, t, st, light_kind='flood'):
    """The stadium layer for camera `cam` at time t in state `st` (premultiplied linear, transparent where there is
    sky), already multiplied by the light map. Painter order by camera depth (far -> near)."""
    F, P = seats()
    T = figure_textures()
    cv = np.zeros((H, W, 4), np.float32)
    items = []
    mask = st.mask
    sp = specials()
    camR = cam.R
    cpos = cam.pos
    # -------- walls (barrier + bench / riser walls), floor
    if st.walls > 0 and mask is None:
        wt = wall_texture()
        for i in range(-1, NROWS):
            if i < 0:
                R, ybot, ytop = 6600.0, 0.0, 800.0
            else:
                R = R_(i) - 400.0
                ybot = 0.0 if i == 0 else h_(i - 1) - 550.0
                ytop = h_(i) - 150.0
                if i == 0:
                    continue                                               # the barrier is row 0's front
            seg = 7.5
            for th in np.arange(TH0, TH1, seg):
                thc = th + seg / 2
                r = math.radians(thc)
                c = np.array([R * math.sin(r), -ybot, R * math.cos(r)])
                wdt = 2 * R * math.sin(math.radians(seg / 2)) + 30
                z = cam.depth(c + np.array([0.0, -(ytop - ybot) / 2, 0.0]))
                if z < cam.near * 4:
                    continue
                items.append((z + 60.0, 0, ('wall', c, wdt, ytop - ybot, thc)))
    # -------- cards
    show_cards = st.cards > 0 and st.part in ('all', 'cards')
    fig_idx = np.arange(len(F['row']))
    if show_cards or (st.part == 'nocards' and st.last):
        if show_cards:
            sel = fig_idx
            if not st.last:
                sel = sel[sel != F['last']]
        else:
            sel = np.array([F['last']])
        vis, zs = _vis_fig(cam, F, sel)
        sw = sway(F, t)
        hx_state = None
        if callable(st.head):
            hx_state = st.head
        for k, z in zip(vis, zs):
            if st.part == 'cards' and k == F['last'] and not st.last:
                continue
            items.append((float(cam.depth(F['B'][k] + np.array([0.0, -500.0, 0.0]))), 2, ('fig', int(k), float(sw[k]))))
            del hx_state
            hx_state = None
    # -------- people + phones
    if st.people > 0 and st.part in ('all', 'nocards') and mask is None:
        occ = np.flatnonzero(P['occ'])
        xy, z = cam.project(P['B'])
        ok = np.isfinite(xy[:, 0]) & (z > cam.near * 4) & (xy[:, 0] > -400) & (xy[:, 0] < W + 400) & \
            (xy[:, 1] > -400) & (xy[:, 1] < H + 900)
        for k in occ:
            if not ok[k]:
                continue
            if st.empty and k in (sp['empty'], sp['ghost']):
                if k == sp['ghost']:
                    items.append((float(z[k]) - 1.0, 4, ('phone', int(k))))
                continue
            zp = float(cam.depth(P['B'][k] + np.array([0.0, -380.0, 0.0]) + P['inward'][k] * 220.0))
            items.append((float(z[k]), 3, ('person', int(k))))
            items.append((min(float(z[k]) - 1.0, zp), 4, ('phone', int(k))))
    items.sort(key=lambda it: (-it[0], it[1]))
    # depth cue: everything drawn before an item nearer than a fog step is darkened (exponential-ish fog to black)
    fog_steps = []
    if st.fog > 0 and mask is None:
        fog_steps = [(d, 1.0 - (1.0 - 0.72) * st.fog) for d in np.arange(st.fog_d0 + 6 * 900.0, st.fog_d0 - 1, -900.0)]
    fi = 0
    for z, kind, it in items:
        while fi < len(fog_steps) and z < fog_steps[fi][0]:
            cv[..., :3] *= np.float32(fog_steps[fi][1])
            fi += 1
        if it[0] == 'wall':
            _draw_wall(cv, cam, it, st)
        elif it[0] == 'fig':
            _draw_fig(cv, cam, t, st, F, T, it[1], it[2], sp)
        elif it[0] == 'person':
            _draw_person(cv, cam, t, st, P, it[1], sp)
        elif it[0] == 'phone':
            _draw_phone(cv, cam, t, st, P, it[1], sp, light_kind)
    if mask is None:
        lm = light_map(st.light, light_kind)
        cv[..., :3] *= lm
    del camR, cpos
    return cv


def _near_fade(st, z):
    if st.near_cull <= 0:
        return 1.0
    return float(np.clip((z - st.near_cull) / 1500.0, 0, 1))


def _draw_wall(cv, cam, it, st):
    _, c, wdt, hgt, thc = it
    K.draw_plane(cv, wall_texture(), cam, tuple(c), wdt, height=hgt, rot=(0.0, thc, 0.0), anchor=(0.5, 1.0),
                 opacity=st.walls)


def _fig_rot(st, F, k, sw):
    rz = sw
    rx = 0.0
    if k == F['lean_odd']:
        rz += 3.0
    if st.flap is not None:
        rx = float(st.flap[int(F['row'][k])])
    if k == F['last']:
        rx = min(rx, 0.0) + float(st.last_tip) if st.flap is None else rx
    return rx, rz


def _draw_fig(cv, cam, t, st, F, T, k, sw, sp):
    tex = T[(int(F['var'][k]), int(F['flip'][k]))]
    g = tex['geo']
    B = F['B'][k]
    yaw = float(F['yaw'][k])
    rx, rz = _fig_rot(st, F, k, sw)
    if rx <= -89.0:
        return
    lean = st.lean
    wmul = 0.86 if k == F['lean_odd'] else 1.0
    fw, fh = FIG_W * lean * wmul, FIG_H * lean
    rot = (rx, yaw, rz)
    # facing: n points to F; the camera sees the back when dot(n, card - cam) > 0
    r = math.radians(yaw)
    n = np.array([-math.sin(r), 0.0, -math.cos(r)])
    mid = K.plane_point(B, fw, fh, rot=rot, uv=(0.5, 0.5), anchor=(0.5, 1.0))
    v = mid - cam.pos
    dist = float(np.linalg.norm(v))
    zc = cam.depth(mid)
    if zc < cam.near * 6:
        return
    op = _near_fade(st, zc)
    if op <= 0:
        return
    dot = float(np.dot(n, v / max(dist, 1e-6)))
    back = dot > 0
    ad = abs(dot)
    if st.mask is not None:
        spr = tex['mask']
        if st.mask == 'eye':
            spr = _black_like(spr)
        K.draw_plane(cv, spr, cam, tuple(B), fw, height=fh, rot=rot, anchor=(0.5, 1.0), dof=False)
        if st.mask == 'eye' and not back:
            _draw_eyes(cv, cam, st, F, k, tex, B, fw, fh, rot, 1.0, mask=True, head_w=_head_w(st, F, k))
        return
    if back:
        K.draw_plane(cv, tex['back'], cam, tuple(B), fw, height=fh, rot=rot, anchor=(0.5, 1.0), opacity=op)
        if ad < 0.95:
            K.draw_plane(cv, tex['bandback'], cam, tuple(B), fw, height=fh, rot=rot, anchor=(0.5, 1.0),
                         opacity=op * float(np.clip((0.95 - ad) / 0.35, 0, 1)) * 0.35, mode='add')
        _draw_strut(cv, cam, F, k, B, fw, fh, rot, op)
    else:
        w = _head_w(st, F, k)
        jolt = _jolt(st, F, k)
        tilt = st.tilt_late if k == F['late_tilt'] else st.tilt
        if (0.0 < w < 1.0) or abs(tilt) > 0.01 or abs(jolt) > 0.01:
            # body + a separately drawn head (blend turned -> front, jolt, tilt about the neck)
            K.draw_plane(cv, tex['body'], cam, tuple(B), fw, height=fh, rot=rot, anchor=(0.5, 1.0), opacity=op)
            hc, hw_, hh_, an, hrot = _head_plane(cam, tex, B, fw, fh, rot, tilt, jolt, lean * wmul, lean)
            if w < 1.0:
                K.draw_plane(cv, tex['head_turned'], cam, tuple(hc), hw_, height=hh_, rot=hrot, anchor=an, opacity=op)
            if w > 0.0:
                K.draw_plane(cv, tex['head_front'], cam, tuple(hc), hw_, height=hh_, rot=hrot, anchor=an, opacity=op * w)
        else:
            K.draw_plane(cv, tex['front'] if w >= 1.0 else tex['turned'], cam, tuple(B), fw, height=fh, rot=rot,
                         anchor=(0.5, 1.0), opacity=op)
        if ad < 0.95:
            K.draw_plane(cv, tex['band'], cam, tuple(B), fw, height=fh, rot=rot, anchor=(0.5, 1.0),
                         opacity=op * float(np.clip((0.95 - ad) / 0.35, 0, 1)) * 0.6, mode='add')
        if w > 0 and st.eyes > 0:
            _draw_eyes(cv, cam, st, F, k, tex, B, fw, fh, rot, w * st.eyes * op, tilt=tilt, jolt=jolt,
                       head_w=w)
    if st.lines and ad < LINE_DOT and F['j'][k] == 1:
        _draw_line(cv, cam, F, k, B, fw, fh, rot, (1.0 - ad / LINE_DOT) * op)


@functools.lru_cache(maxsize=2)
def _black_like_cached(key):
    return None


def _black_like(spr):
    out = spr.copy()
    out[..., :3] = 0.0
    return out


def _head_w(st, F, k):
    h = st.head
    if h is None:
        return 0.0
    if isinstance(h, (int, float)):
        return float(h)
    return float(h[k])


def _jolt(st, F, k):
    j = st.jolt
    if j is None:
        return 0.0
    return float(j[k])


def _head_plane(cam, tex, B, fw, fh, rot, tilt, jolt_px, sx, sy):
    """World centre / size / anchor / rotation of the cropped head sprite, pivoting about the neck."""
    g = tex['geo']
    x0, y0, x1, y1 = g['box']
    nx, ny = g['neck']
    neck_w = K.plane_point(B, fw, fh, rot=rot, uv=(nx / TW, ny / TH), anchor=(0.5, 1.0))
    if abs(jolt_px) > 0:
        z = max(cam.depth(neck_w), 1.0)
        neck_w = neck_w + np.array([0.0, -jolt_px * z / cam.focal, 0.0])
    hw_ = (x1 - x0) / PXMM * sx
    hh_ = (y1 - y0) / PXMM * sy
    an = ((nx - x0) / (x1 - x0), (ny - y0) / (y1 - y0))
    return neck_w, hw_, hh_, an, (rot[0], rot[1], rot[2] + tilt)


def _draw_eyes(cv, cam, st, F, k, tex, B, fw, fh, rot, op, tilt=0.0, jolt=0.0, mask=False, head_w=1.0):
    g = tex['geo']
    hc, hw_, hh_, an, hrot = _head_plane(cam, tex, B, fw, fh, rot, tilt, jolt, fw / FIG_W, fh / FIG_H)
    x0, y0, x1, y1 = g['box']
    uv = np.array([((ex - x0) / (x1 - x0), (ey - y0) / (y1 - y0)) for ex, ey in g['eyes']])
    Pw = K.plane_point(hc, hw_, hh_, rot=hrot, uv=uv, anchor=an)
    xy, z = cam.project(Pw)
    if not np.isfinite(xy).all():
        return
    # head width in px (0.035 x head width, floored at 1.5 px on rows 0-5)
    hl = K.plane_point(hc, hw_, hh_, rot=hrot, uv=np.array([[(g['hx'] - g['hw'] - x0) / (x1 - x0), 0.5],
                                                            [(g['hx'] + g['hw'] - x0) / (x1 - x0), 0.5]]), anchor=an)
    hxy, _ = cam.project(hl)
    hpx = float(np.hypot(*(hxy[1] - hxy[0])))
    r = 0.035 * hpx
    if int(F['row'][k]) <= 5:
        r = max(r, 1.5)
    r = max(r, 0.6)
    if k == specials_eye_low():
        xy = xy + np.array([0.0, 2.0])
    blur = _dofblur(cam, float(z.mean()))
    spr = _eye_disc(round(r * 4) / 4, mask)
    for p in xy:
        K.draw(cv, spr, float(p[0]), float(p[1]), opacity=op, blur=blur)


@functools.lru_cache(maxsize=1)
def specials_eye_low():
    """Hook B's 'one card's eyes 2 px lower than its neighbours': a pivot-row figure near frame centre."""
    F, _ = seats()
    x = head_screen_x('rows')
    r3 = np.flatnonzero(F['row'] == 3)
    return int(r3[np.argmin(np.abs(x[r3] - 640.0))])


@functools.lru_cache(maxsize=64)
def _eye_disc(r, mask=False):
    col = np.float32([0.0, 1.0, 0.0]) if mask else C('AMBER', 1.3)
    d = K.disc(r, col, soft=0.8)
    d.flags.writeable = False
    return d


def _draw_strut(cv, cam, F, k, B, fw, fh, rot, op):
    """Easel strut: from 60 % card height on the back down to the seat 450 mm behind (a plank perpendicular to it)."""
    if st_strut_skip(F, k):
        return
    yaw = rot[1]
    r = math.radians(yaw)
    out_ = np.array([math.sin(r), 0.0, math.cos(r)])
    A = np.asarray(B) + np.array([0.0, -0.55 * fh, 0.0]) + out_ * 15.0
    Fp = np.asarray(B) + out_ * 230.0 + np.array([0.0, 60.0, 0.0])
    mid = (A + Fp) / 2
    L = float(np.linalg.norm(A - Fp))
    ang = math.degrees(math.atan2(215.0, 0.55 * fh + 60.0))
    # plane perpendicular to the card: yaw + 90 (its normal along the card's tangent); tilt the long axis toward out_
    K.draw_plane(cv, strut_texture(), cam, tuple(mid), 40.0, height=L, rot=(0.0, yaw + 90.0, -ang), opacity=op)


def st_strut_skip(F, k):
    return F['j'][k] in (0, 3) and (int(F['strip'][k]) % 2 == 1)


def _draw_line(cv, cam, F, k, B, fw, fh, rot, op):
    """Edge-on card: an emissive ASH line on the strip's projected seam axis (j=1|2 boundary), card height."""
    g = 1.0
    bot = K.plane_point(B, fw, fh, rot=rot, uv=(1.0, 1.0), anchor=(0.5, 1.0))
    top = K.plane_point(B, fw, fh, rot=rot, uv=(1.0, 0.16), anchor=(0.5, 1.0))
    xy, z = cam.project(np.array([bot, top]))
    if not np.isfinite(xy).all():
        return
    dx, dy = xy[1] - xy[0]
    L = math.hypot(dx, dy)
    if L < 3:
        return
    spr = line_sprite()
    ang = math.degrees(math.atan2(dx, -dy))
    blur = _dofblur(cam, float(z.mean()))
    K.draw(cv, spr, float(xy[0][0]), float(xy[0][1]), scale=(1.0, L / spr.shape[0]), rot=ang, anchor=(0.5, 1.0),
           opacity=op * g, mode='add', blur=blur * 0.6)


def _person_tex(cam, P, k, st, sp):
    """Choose front / profile by the angle between his facing (toward the field) and the camera."""
    T = people_textures()
    seat = P['B'][k]
    to_cam = cam.pos - seat
    to_cam[1] = 0.0
    to_cam /= max(np.linalg.norm(to_cam), 1e-6)
    inward = P['inward'][k]
    c = float(np.dot(to_cam, inward))                 # 1 = he faces the camera
    ang = math.degrees(math.acos(np.clip(c, -1, 1)))
    # which way he faces on screen (profile direction)
    xy, _ = cam.project(np.array([seat, seat + inward * 600.0]))
    left = (xy[1][0] - xy[0][0]) < 0 if np.isfinite(xy).all() else True
    v = int(P['var'][k])
    kind_p = 'profile' if left else 'profile_r'
    if k == sp['lookup'] and st.lookup > 0:
        kind_p = 'lookup' if left else 'lookup_r'
        v = 0
    wf = float(np.clip((55.0 - ang) / 20.0, 0, 1))
    return T['front'][v], T[kind_p][v % len(T[kind_p])], wf


def _draw_person(cv, cam, t, st, P, k, sp):
    seat = P['B'][k]
    z = cam.depth(seat)
    op = st.people * _near_fade(st, z)
    if op <= 0:
        return
    (fs, _), (ps, _), wf = _person_tex(cam, P, k, st, sp)
    width = PW / PPX
    hgt = PH / PPX
    # billboard anchored at the seat point
    up = np.array([0.0, -(P_ANCHOR[1] - 0.5) * hgt, 0.0])
    pos = seat + _cam_up(cam) * 0.0 + up
    blur = 0.0
    if wf > 0:
        K.draw_billboard(cv, fs, cam, tuple(pos), width, opacity=op * (1.0 if wf >= 1 else 1.0))
    if wf < 1:
        K.draw_billboard(cv, ps, cam, tuple(pos), width, opacity=op * (1.0 - wf) if wf > 0 else op)
    del blur


def _cam_up(cam):
    return cam.R @ np.array([0.0, -1.0, 0.0])


def _draw_phone(cv, cam, t, st, P, k, sp, light_kind):
    if st.phones <= 0:
        return
    seat = P['B'][k]
    pos = seat + np.array([0.0, -380.0, 0.0]) + P['inward'][k] * 220.0
    xy, z = cam.project(pos[None])
    if not np.isfinite(xy).all() or z[0] < cam.near * 4:
        return
    z = float(z[0])
    op = st.phones * _near_fade(st, z)
    if op <= 0:
        return
    rng = np.random.default_rng(int(k) * 7 + 1)
    base = 0.55 + 0.45 * rng.random()                       # screens differ in brightness
    fl = 1.0 + 0.04 * math.sin(2 * math.pi * (0.3 + rng.random()) * t + rng.random() * 6)
    if k == sp['scroller']:
        base = 1.0
        fl = (1.0 + 0.15 * math.sin(2 * math.pi * 2.5 * t)) * st.tap
    gain = op * base * fl
    lm = light_at(st.light, light_kind, xy)[0] if st.mask is None else np.ones(3, np.float32)
    comp = 1.0 / np.maximum(lm, 0.08)
    coc = float(cam.coc(z)) if cam.aperture > 0 else 0.0
    if coc > 4.0:
        # bokeh: a disc of radius coc with the core's energy (floored so a far phone still reads as a dot)
        core_px = 70.0 * cam.focal / z
        e = (core_px * core_px * 2.0) / (math.pi * coc * coc)
        a = gain * max(e * 1.8, 0.10)
        spr = bokeh_disc(int(round(coc)))
        tmp = spr
        K.draw(cv, tmp, float(xy[0, 0]), float(xy[0, 1]), opacity=1.0, mode='add') if False else None
        _add_tinted(cv, spr, xy[0], a * comp)
    else:
        spr = phone_sprite()
        width = spr.shape[1] / PPX
        _add_billboard(cv, cam, spr, pos, width, gain, comp, blur=coc * 0.5)


def _add_tinted(cv, spr, xy, gain_rgb):
    """Add an emissive sprite (alpha 0) scaled per channel at an integer-rounded centre."""
    h, w = spr.shape[:2]
    x0, y0 = int(round(xy[0])) - w // 2, int(round(xy[1])) - h // 2
    X0, Y0, X1, Y1 = max(0, x0), max(0, y0), min(W, x0 + w), min(H, y0 + h)
    if X1 <= X0 or Y1 <= Y0:
        return
    cv[Y0:Y1, X0:X1, :3] += spr[Y0 - y0:Y1 - y0, X0 - x0:X1 - x0, :3] * np.asarray(gain_rgb, np.float32)


def _add_billboard(cv, cam, spr, pos, width, gain, comp, blur=0.0):
    tmp_op = float(gain)
    if tmp_op <= 1e-4:
        return
    # per-channel compensation: draw into the canvas with 'add' (alpha 0 sprite), then nothing else
    if np.allclose(comp, comp[0], rtol=0.02):
        K.draw_billboard(cv, spr, cam, tuple(pos), width, opacity=tmp_op * float(comp[0]), mode='add', blur=blur)
    else:
        sc = _comp_sprite(tuple(float(x) for x in np.round(np.asarray(comp) / max(float(np.max(comp)), 1e-6), 2)))
        K.draw_billboard(cv, sc, cam, tuple(pos), width, opacity=tmp_op * float(np.max(comp)), mode='add', blur=blur)


@functools.lru_cache(maxsize=64)
def _comp_sprite(rel):
    s = phone_sprite().copy()
    s[..., :3] *= np.asarray(rel, np.float32)
    s.flags.writeable = False
    return s


# ============================================================================================== backdrop
def bank_xy(cam):
    xy, z = cam.project(BANK[None])
    return (float(xy[0, 0]), float(xy[0, 1])) if np.isfinite(xy).all() and z[0] > 0 else None


def backdrop(cam, t, bank=1.0, light=0.0, warm_key=0.0, bokeh=0.4):
    """Sky / haze (K.background, the look's key glow on the bank) + the roof truss + the lamp bank.
    bank 0..1 = the floodlight's brightness (0 after the clunk); light = warm state (key moves screen-left)."""
    b = bank_xy(cam)
    if light < 1.0:
        c = (b[0] / W, b[1] / H) if b is not None else (0.98, -0.06)
        c = (float(np.clip(c[0], -0.3, 1.3)), float(np.clip(c[1], -0.4, 1.2)))
    else:
        c = (0.06, 0.50)
    if 0 < light < 1:
        c0 = (b[0] / W, b[1] / H) if b is not None else (0.98, -0.06)
        c = (K.lerp(c0[0], 0.06, light), K.lerp(c0[1], 0.50, light))
    inten = 0.35 + 0.65 * max(bank, light)
    cv = K.background('noir_ember', t, None, center=c, boost=0.3 * warm_key, bokeh=bokeh * max(bank, 0.3),
                      intensity=inten)
    if bank > 0 and b is not None:
        tr = truss_sprite()
        K.draw_plane(cv, tr, cam, tuple(BANK + np.array([-1200.0, -900.0, 400.0])), 9000.0, opacity=1.0)
        spr, wmm = bank_sprite()
        lit = spr
        K.draw_billboard(cv, lit, cam, tuple(BANK), wmm, opacity=1.0, mode='over') if bank >= 1 else \
            _bank_dim(cv, cam, spr, wmm, bank)
    return cv


def _bank_dim(cv, cam, spr, wmm, bank):
    """The bank partly lit (light hand-back): housing at full alpha, the lamps' light scaled."""
    K.draw_billboard(cv, _bank_off(), cam, tuple(BANK), wmm, opacity=1.0)
    K.draw_billboard(cv, _bank_light(), cam, tuple(BANK), wmm, opacity=float(bank), mode='add')


@functools.lru_cache(maxsize=1)
def _bank_off():
    spr, _ = bank_sprite()
    o = spr.copy()
    o[..., :3] = o[..., 3:4] * C('SMOKE', 0.5)
    o.flags.writeable = False
    return o


@functools.lru_cache(maxsize=1)
def _bank_light():
    spr, _ = bank_sprite()
    o = spr.copy()
    o[..., 3] = 0.0
    o.flags.writeable = False
    return o


def over(cv, lay):
    """Premultiplied 'over' of the stadium layer onto the backdrop (in place)."""
    a = lay[..., 3:4]
    cv *= (1.0 - a)
    cv += lay
    cv[..., 3] = 1.0
    return cv


def floor(cv, cam, light=0.0):
    """The field floor (y = 0), drawn into the backdrop before the stands."""
    K.draw_plane(cv, floor_texture(), cam, (0.0, 0.0, 4000.0), 15000.0, height=13000.0, rot=(90.0, 0.0, 0.0),
                 dof=False)
    return cv


# ============================================================================================== QA helpers
def head_mask(cam, t, st=None):
    """(H, W) float32 union of the visible (occlusion-aware) head masses of rows 0-9 (BRIEF 7.4 / 17.5)."""
    s = st or State()
    s2 = State(**{k: getattr(s, k) for k in vars(s)})
    s2.mask = 'head'
    s2.people = 0.0
    s2.lines = False
    lay = render(cam, t, s2)
    return np.clip(lay[..., 0], 0, 1)


def eye_mask(cam, t, st=None):
    """(H, W) float32 coverage of the visible catch-light eye discs."""
    s = st or State()
    s2 = State(**{k: getattr(s, k) for k in vars(s)})
    s2.mask = 'eye'
    s2.people = 0.0
    s2.lines = False
    lay = render(cam, t, s2)
    return np.clip(lay[..., 1], 0, 1)


def scroller_xy(t, psi=70.0, focus=16000.0):
    """Screen px of the scroller's phone and head at CAM_ROWS(psi)."""
    F, P = seats()
    k = specials()['scroller']
    seat = P['B'][k]
    pts = np.array([seat + np.array([0.0, -380.0, 0.0]) + P['inward'][k] * 220.0,
                    seat + np.array([0.0, -640.0, 0.0]) + P['inward'][k] * 90.0])
    xy, z = cam_rows(psi, focus).project(pts)
    return xy, z


def scroller_rect(t, margin=28):
    """Caption avoid rect (x0, y0, x1, y1): the scroller's projected head + phone bbox + margin (S4-02)."""
    xy, z = scroller_xy(t)
    hpx = 260.0 * 7200.0 / float(z[1])                       # head + shoulders extent in px
    x0, x1 = xy[:, 0].min() - hpx * 0.6, xy[:, 0].max() + hpx * 0.6
    y0, y1 = xy[:, 1].min() - hpx * 0.6, xy[:, 1].max() + hpx * 0.5
    return (int(x0 - margin), int(y0 - margin), int(x1 + margin), int(y1 + margin))


def prewarm():
    figure_textures()
    people_textures()
    strut_texture()
    line_sprite()
    phone_sprite()
    wall_texture()
    floor_texture()
    bank_sprite()
    _bank_off()
    _bank_light()
    truss_sprite()
    seats()
    specials()
    head_screen_x('wide')
    head_screen_x('rows')
    specials_eye_low()
    for kind in ('flood', 'rows', 'warm'):
        _light_map_lo(kind)
