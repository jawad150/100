"""anim1.py: ANIM 1 "DAY IN THE LIFE" - what fostering really looks like. 1080x1920, 30 fps, 21.0 s, 100 BPM.

LOOK: EDITORIAL PAPER. Kinetic Nunito Black type printed (debossed) into a warm crumpled-paper sheet that is relit
every frame (anim1_paper.py: multi-scale crumple height field -> normals, moving key light, sky fill, sun pool):
morning light rakes in from the upper left, swings round to golden afternoon light from the top, and ends as a low
warm evening light from the right with a glowing lit window. Glossy 3D toy props (sprites3d, day variants) drop
onto the desk with contact + cast shadows that follow the light. Foreground: defocused drifting leaves and motes.
Type: PLUM #5B174F / MAGENTA #B7006E; accents ORANGE / LEAF; Caveat Bold handwritten lines with scribble underlines.
SFX only (no music) on the 100 BPM grid: beat = 0.6 s, B(n) = n * 0.6 (8th = 0.3, 16th = 0.15).

SHOT LIST (time s | beat | content | motion / transition | SFX)
 FRAME 1 - sheet A (morning, light from the upper left)
 0.00-1.80  b0-b3    HOOK: "WHAT DOES / FOSTERING / REALLY LOOK LIKE?" stamped word by word into the paper:
                     WHAT b0, DOES b0.5, FOSTERING b1 (biggest hit), REALLY b1.5, LOOK b1.75, LIKE? b2 (16ths);
                     each word drops 1.6x -> 1 with an overshoot, paper dust puff, 2-5 px camera shake on b0/b1.
                     b2.5 (1.5) "<  >" MAGENTA brackets snap in round FOSTERING (spring) | paper rustle, type
                     thumps, sub thump on b1, bracket clicks
 1.80-2.40  b3-b4    MAGENTA marker swipe wipes behind FOSTERING (word knocks out to paper white); the morning
                     LIGHT STREAK sweeps across the sheet and glints across the type (1.8-3.3) | marker swish, shimmer
 2.40-5.10  b4-b8.5  "It's often found in the everyday." (Caveat Bold 82 px, MAGENTA) writes on 2.4-3.6, ORANGE
                     scribble underline under "everyday." draws on 3.6-4.0; hold | pen write, scribble
 5.10-5.40  b8.5-b9  SLIDE: sheet B slides in from the right over sheet A (rotation 5 deg -> 0, edge shadow,
                     sheet A pushed left) | paper slide
 FRAME 2 - sheet B (late morning)
 5.40-7.20  b9-b12   "SCHOOL RUNS." slams (list item 1, MAGENTA); backpack drops (lands 5.7); ORANGE dashed path
                     draws across the paper 5.7-6.6 and the school bus (side view) drives along it 5.95-7.05 and
                     exits right | thump, backpack thud, bus pass + beep
 7.20-8.40  b12-b14  "HOMEWORK." slams (item 2; item 1 turns PLUM); open book + pencil drop (lands 7.35); the
                     pencil scribbles a graphite line beside the book 7.5-8.25 | thump, book thud, pencil scribble
 8.40-10.20 b14-b17  "BAKING." slams (item 3); mixing bowl lands 8.55 with a flour puff; cupcake lands 8.85;
                     oven-timer ding 9.6 (b16) | thump, bowl clink + whisk, flour puff, cupcake plop, ding
 FRAME 3 - sheet B (golden afternoon, light from the top)
 10.20-12.00 b17-b20 the list slides out into its slots; the props hop, tumble and morph (puff) into three 3D
                     building blocks that drop onto a tower: block 1 lands b18 with "SMALL MOMENTS" rising out
                     of its slot, block 2 b19 "CAN HELP BUILD", block 3 b20 "STABILITY." (MAGENTA slam; the tower
                     wobbles and settles) | swishes, poofs, block clacks, thumps
 12.60-15.45 b21-b25.75  "A consistent home." (house), "A familiar routine." (alarm clock), "Someone who is there."
                     (family figures) tick in on b21 / b22 / b23 with their small 3D icons; hold | ticks, pops,
                     clock tick-tock
 15.45-15.90 b25.75-b26.5 FLIP: sheet B flips up and away (hinged at the top edge, darkening) revealing sheet C
                     | paper flip
 FRAME 4 - sheet C (evening, low warm light from the right)
 15.60-17.40 b26-b29 "FOSTERING / HAPPENS IN THE / EVERYDAY." rise out of their slots on b26, b26.75, b27.5
                     (EVERYDAY. MAGENTA) | thumps
 17.10-18.60 b28.25-b31 the 3D house drops in below (lands 17.10); b30 the headline sinks away and the house glides
                     up; b31 its windows light up (warm glow spills onto the paper) | thud, swish, light-switch click
 18.60-19.35 b31-b32.25 "Could you make room?" (Caveat 116 px, MAGENTA) writes on, ORANGE scribble underline;
                     end card: logo_full.png rises in, CTA pill "Start your enquiry" pops, "0161 241 1332 ·
                     organicfostering.co.uk" | pen write, scribble, warm shimmer, pop
 19.35-21.00 b32.25- END CARD settled (1.65 s hold), only the light breathes | room tone tail
BED: room_tone at -32 dB (felt). SFX: anim1_sfx.py (custom paper / pencil / bus / bowl / ding / switch / block
sounds registered into the toolkit mixer) -> workspace3/audio/anim1_sfx.wav + anim1_sfx_stem.wav, -18 LUFS,
<= -2.0 dBTP.

CONTRACT (render.py): DUR, LOOK, BPM, draw(t) pure, post(cv, t), samples(t), cues(), prewarm().
"""
import functools
import math

import numpy as np

import core as K
import type3d as T
import ui
import anim1_paper as P
import anim1_fx as X
import anim1_sfx  # noqa: F401  (registers the custom SFX + routes the automatic mix to -2.0 dBTP)

DUR, LOOK, BPM = 21.0, 'airy', 100
BEAT = 60.0 / BPM               # 0.6 s
BED, BED_GAIN_DB = 'room_tone', -32.0
W, H = K.W, K.H
FPS = K.FPS


def B(n):
    return n * BEAT


PLUM, MAG, IVORY = '#5B174F', '#B7006E', '#FCF8F5'
C = K.C
T_SLIDE0, T_SLIDE1 = 5.06, 5.40          # sheet B slides in (lands on b9)
T_F3 = B(17)                             # 10.2 frame 3
T_FLIP0, T_FLIP1 = 15.10, 15.64          # sheet B flips up toward the viewer and away
T_F4 = B(26)                             # 15.6 frame 4

# ============================================================================================ layout constants
# frame 1 (centre x 540)
F1_BASE = (679, 832, 962)                # baselines: WHAT DOES / FOSTERING / REALLY LOOK LIKE?
F1_HAND_BASE = 1125
F1_BAND = (151, 929)                     # magenta swipe x range
F2_X, F2_BASE = 96, (432, 592, 752)      # list
F3_CAP = (300, 404, 518)                 # headline cap tops
F3_ROWS = (770, 875, 980)                # supporting rows (centre y)
TOWER = (540, 1600)                      # tower ground point
F4_CAP = (430, 580, 695)
HOUSE_DROP, HOUSE_END = (540, 1330), (540, 800)
F4_HAND_BASE = 944


# hook camera: starts pushed in on WHAT, whips word to word as they stamp in, settles on the whole question
HZ = 1.75                                # hi-res factor of the hook type sprites
T_HOOK_END = 1.5
S_ANCHOR = (540.0, 860.0)                # screen point the camera centre maps to


# ============================================================================================ assets
@functools.lru_cache(maxsize=1)
def A():
    d = {}
    # frame 1
    d['l1'] = X.Txt('WHAT DOES', px=140, fill=PLUM)
    d['l2'] = X.Txt('FOSTERING', px=130, fill=PLUM)
    d['l2i'] = X.Txt('FOSTERING', px=130, fill=IVORY)
    d['l3'] = X.Txt('REALLY LOOK LIKE?', px=92, fill=PLUM)
    # hi-res copies for the hook camera (drawn minified while the camera is pushed in: razor sharp)
    d['l1h'] = X.Txt('WHAT DOES', px=140 * HZ, fill=PLUM)
    d['l2h'] = X.Txt('FOSTERING', px=130 * HZ, fill=PLUM)
    d['l3h'] = X.Txt('REALLY LOOK LIKE?', px=92 * HZ, fill=PLUM)
    d['hand1'] = X.Txt("It's often found in the everyday.", font='hand', px=82, fill=MAG)
    d['band'] = X.marker_band(F1_BAND[1] - F1_BAND[0], 150, seed=4)
    # frame 2
    d['list'] = [(X.Txt(s, px=116, fill=MAG), X.Txt(s, px=116, fill=PLUM))
                 for s in ('SCHOOL RUNS.', 'HOMEWORK.', 'BAKING.')]
    # frame 3
    d['h3'] = [X.Txt('SMALL MOMENTS', px=100, fill=PLUM), X.Txt('CAN HELP BUILD', px=105, fill=PLUM),
               X.Txt('STABILITY.', px=165, fill=MAG)]
    d['rows'] = [X.Txt(s, font='ui', px=50, fill=PLUM) for s in
                 ('A consistent home.', 'A familiar routine.', 'Someone who is there.')]
    # frame 4
    d['h4'] = [X.Txt('FOSTERING', px=155, fill=PLUM), X.Txt('HAPPENS IN THE', px=104, fill=PLUM),
               X.Txt('EVERYDAY.', px=158, fill=MAG)]
    d['hand2'] = X.Txt('Could you make room?', font='hand', px=116, fill=MAG)
    d['phone'] = X.Txt('0161 241 1332 · organicfostering.co.uk', font='ui', px=34, fill=PLUM)
    d['logo'] = K.load_image(K.BRAND + '/logo_full.png', size=680)
    d['button'] = ui.button('Start your enquiry', look='airy', h=92, size=40)
    # props
    d['backpack'] = X.Prop('backpack', 380)
    d['bus'] = X.Prop('school_bus', 185, mode='side')
    d['book'] = X.Prop('book_pencil', 330)
    d['bowl'] = X.Prop('mixing_bowl', 300)
    d['cupcake'] = X.Prop('cupcake', 300)
    d['i_house'] = X.Prop('house', 92)
    d['i_clock'] = X.Prop('alarm_clock', 92)
    d['i_family'] = X.Prop('family_figures', 92)
    d['house'] = X.Prop('house', 370)
    d['clock'] = X.Prop('alarm_clock', 330)
    d['blocks'] = block_sprites()
    d['bus_path'] = bus_path()
    return d


def prewarm():
    A()
    P.sheet(0)
    P.sheet(1)
    P.sheet(2)


def bus_path():
    ctrl = np.array([(-90, 1405), (160, 1338), (430, 1392), (700, 1318), (930, 1352), (1180, 1300)], np.float64)
    # Catmull-Rom through the control points
    pts = []
    for i in range(len(ctrl) - 1):
        p0 = ctrl[max(i - 1, 0)]; p1 = ctrl[i]; p2 = ctrl[i + 1]; p3 = ctrl[min(i + 2, len(ctrl) - 1)]
        for s in np.linspace(0, 1, 24, endpoint=False):
            s2, s3 = s * s, s * s * s
            pts.append(0.5 * ((2 * p1) + (-p0 + p2) * s + (2 * p0 - 5 * p1 + 4 * p2 - p3) * s2 +
                              (-p0 + 3 * p1 - 3 * p2 + p3) * s3))
    pts.append(ctrl[-1])
    return X.resample(np.array(pts), 3.0)


@functools.lru_cache(maxsize=1)
def block_sprites():
    """Three toy blocks (MAGENTA heart, ORANGE star, LEAF leaf) as separate sprites, ground-anchored.
    Placeholder (rounded glossy squares) until blocks/day exists."""
    out = []
    for col in ('MAGENTA', 'ORANGE', 'LEAF'):
        n = 200
        a = K.rrect_alpha(n - 20, n - 20, 30, 10)
        hh, ww = a.shape
        yy, xx = np.mgrid[0:hh, 0:ww].astype(np.float32)
        sh = np.clip(1.25 - 0.9 * ((xx / ww - 0.3) ** 2 + (yy / hh - 0.25) ** 2), 0.45, 1.3)
        rgb = C[col][None, None, :] * sh[..., None]
        spr = np.dstack([rgb * a[..., None], a]).astype(np.float32)
        spr.setflags(write=False)
        out.append((spr, (0.5, (hh - 10) / hh), 170.0 / (n - 20)))
    return out


# ============================================================================================ helpers
class BBox:
    def __init__(self):
        self.b = None

    def add(self, bb):
        if bb is None:
            return
        if self.b is None:
            self.b = list(bb)
        else:
            self.b = [min(self.b[0], bb[0]), min(self.b[1], bb[1]), max(self.b[2], bb[2]), max(self.b[3], bb[3])]

    @property
    def box(self):
        return tuple(self.b) if self.b else None


def ease(name):
    return K.EASE[name]


def in_quad(x):
    x = min(max(x, 0.0), 1.0)
    return x * x


def out_quad(x):
    x = min(max(x, 0.0), 1.0)
    return 1 - (1 - x) * (1 - x)


def stamp(t, t_hit, s0=1.6, lead=0.075):
    """Word stamped into the paper: scale s0 -> 1 hitting exactly at t_hit, then a pressed overshoot.
    Returns (scale, opacity, lift 0..1) or None before it starts."""
    dt = t - (t_hit - lead)
    if dt < 0:
        return None
    if dt < lead:
        u = dt / lead
        s = 1 + (s0 - 1) * (1 - u) ** 2
        return s, min(1.0, 0.25 + u * 1.5), (1 - u)
    d = t - t_hit
    s = 1 - 0.045 * math.exp(-d * 11) * math.cos(d * 30)
    return s, 1.0, 0.0


@functools.lru_cache(maxsize=1)
def hook_track():
    Ad = A()
    l1, l2, l3 = Ad['l1'], Ad['l2'], Ad['l3']

    def wc(txt, i, base):
        w = txt.words[i]
        return 540 - txt.w / 2 + (w[1] + w[2]) / 2, base - txt.ts.layout.cap / 2
    what, does = wc(l1, 0, F1_BASE[0]), wc(l1, 1, F1_BASE[0])
    fos = wc(l2, 0, F1_BASE[1])
    l3c = (540.0, F1_BASE[2] - l3.ts.layout.cap / 2)
    return K.Track([(-0.2, (what[0] - 30, what[1], 1.85)), (B(0), (what[0], what[1], 1.75), 'inout_cubic'),
                    (B(0.5), (does[0] - 40, does[1], 1.55), 'inout_cubic'),
                    (B(1), (fos[0], fos[1] - 10, 1.30), 'inout_cubic'),
                    (B(1.5), (l3c[0] - 20, l3c[1] - 40, 1.14), 'inout_cubic'),
                    (B(2), (l3c[0] + 10, l3c[1] - 80, 1.07), 'inout_cubic'),
                    (T_HOOK_END, (S_ANCHOR[0], S_ANCHOR[1], 1.0))], ease='inout_cubic')


def hook_cam(t):
    """(cx, cy, Z): world point at the screen anchor and zoom; None once settled."""
    if t >= T_HOOK_END:
        return None
    v = hook_track()(t)
    return float(v[0]), float(v[1]), float(v[2])


def w2s(cam, x, y):
    if cam is None:
        return x, y
    cx, cy, z = cam
    return S_ANCHOR[0] + (x - cx) * z, S_ANCHOR[1] + (y - cy) * z


def cam_matrix(cam):
    cx, cy, z = cam
    return np.float32([[z, 0, S_ANCHOR[0] - cx * z], [0, z, S_ANCHOR[1] - cy * z]])


def draw_word_stamp(ink, bb, txt, i, line_left, base, t, t_hit, s0=1.6, light=None, cam=None, hi=None):
    st = stamp(t, t_hit, s0)
    if st is None:
        return
    s, op, lift = st
    w, x0, x1 = txt.words[i]
    ts = txt.word_ts(i)
    cx = line_left + (x0 + x1) / 2
    cy = base - txt.ts.layout.cap / 2
    if cam is not None:
        cx, cy = w2s(cam, cx, cy)
        s = s * cam[2] / HZ
        ts = hi.word_ts(i)
    if lift > 0.02 and light is not None:
        # soft shadow on the paper below the airborne word (drawn into the ink layer under the word)
        (dx, dy), ln = light.shadow_dir()
        off = 60 * lift * min(ln, 2.5)
        spr = ts.sprite
        anc = ts.sprite_anchor((0.5, 0.5))
        sil = _sil(spr)
        bb.add(K.draw(ink, sil, cx + dx * off, cy + dy * off, scale=s * 0.98, anchor=anc,
                      opacity=0.22 * (1 - lift * 0.6), blur=4 + 14 * lift))
    bb.add(ts.draw(ink, cx, cy, anchor=(0.5, 0.5), scale=s, opacity=op))


_SIL = {}


def _sil(spr):
    k = id(spr)
    h = _SIL.get(k)
    if h is not None and h[0] is spr:
        return h[1]
    out = np.zeros_like(spr)
    out[..., 3] = spr[..., 3]
    out[..., :3] = spr[..., 3:4] * np.float32(X.SHADOW_RGB)
    out.setflags(write=False)
    if len(_SIL) > 64:
        _SIL.clear()
    _SIL[k] = (spr, out)
    return out


def slot_rise(ink, bb, txt, cx, cap_top, t, t0, dur=0.42, out_t0=None, out_dur=0.3, anchor_x=0.5, overshoot=True):
    """Masked line reveal: the line rises out of a slot at its final position (clip rect = its own text box
    + descender room). out_t0: sinks back down into the slot."""
    if t < t0:
        return
    cap = txt.ts.layout.cap
    u = K.ramp(t, t0, t0 + dur, 'out_back' if overshoot else 'out_expo')
    dy = (1 - u) * cap * 1.35
    if out_t0 is not None and t >= out_t0:
        v = K.ramp(t, out_t0, out_t0 + out_dur, 'in_cubic')
        dy += v * cap * 1.4
        if v >= 1:
            return
    spr = txt.spr
    anc = txt.anc((anchor_x, 0.0))
    pad = 0.30 * txt.px
    rect = (0, cap_top - pad * 0.6, W, cap_top + cap + pad)
    bb.add(X.draw_clip(ink, spr, cx, cap_top + dy, anc, rect))


def write_on(ink, bb, txt, cx, base, t, t0, dur, anchor_x=0.5):
    """Handwritten write-on: a soft left-to-right reveal at pen speed."""
    if t < t0:
        return
    u = K.ramp(t, t0, t0 + dur, 'inout_sine')
    spr = txt.spr
    anc = txt.anc((anchor_x, 1.0))
    left = cx - anchor_x * txt.w
    mx1 = left - 30 + u * (txt.w + 60)
    if u >= 1:
        bb.add(K.draw(ink, spr, cx, base, anchor=anc))
        return
    bb.add(X.draw_hmask(ink, spr, cx, base, anc, -1e4, mx1, soft=26.0))


def paint_shaded(ink, alpha, shade, x0, y0, rgb):
    """Paint a colour through alpha with a per-pixel brightness (dry-brush streaks) - integer placement."""
    h, w = alpha.shape
    X0, Y0 = max(0, x0), max(0, y0)
    X1, Y1 = min(W, x0 + w), min(H, y0 + h)
    if X1 <= X0 or Y1 <= Y0:
        return None
    a = alpha[Y0 - y0:Y1 - y0, X0 - x0:X1 - x0]
    sh = shade[Y0 - y0:Y1 - y0, X0 - x0:X1 - x0]
    d = ink[Y0:Y1, X0:X1]
    d *= (1.0 - a)[..., None]
    d[..., :3] += (a * sh)[..., None] * np.float32(rgb)
    d[..., 3] += a
    return X0, Y0, X1, Y1


def draw_stroke(ink, bb, pts, width, rgb, u0, u1, dash=None, opacity=1.0):
    if u1 <= u0:
        return
    a, x0, y0 = X.stroke_alpha(pts, width, u0, u1, dash=dash)
    bb.add(X.paint(ink, a, x0, y0, K.hexlin(rgb) if isinstance(rgb, str) else rgb, opacity))


def light_for(t):
    """Scene light at time t: time-of-day + morning streak + the lit window glow."""
    L = P.light_at(t)
    su = K.ramp(t, 1.75, 3.3, 'inout_sine')
    if 0 < su < 1:
        L.streak = (su, -32.0, 0.13, 0.30, (1.0, 0.90, 0.74))
    g = K.ramp(t, B(31) - 0.02, B(31) + 0.25, 'out_cubic')
    if g > 0:
        hx, hy = house_pos(t)[:2]
        flick = 1.0 + 0.04 * K.wiggle(t, 7, 1, seed=3)
        L.glow = (hx, hy - 170, 520.0, 0.65 * g * flick, (1.0, 0.62, 0.30))
    return L


def tint_for(light):
    """Prop tint relative to the morning light (keeps saturated toys, warms them in the evening)."""
    ref = P.light_at(0.0).mean_rgb()
    m = light.mean_rgb() / ref
    m = m / max(m[1], 1e-3)
    return 1.0 + 0.75 * (m - 1.0)


# ============================================================================================ frame 1
def f1_ink(ink, bb, t, light, cam=None):
    Ad = A()
    l1, l2, l2i, l3 = Ad['l1'], Ad['l2'], Ad['l2i'], Ad['l3']
    # line lefts (centred lines)
    x1 = 540 - l1.w / 2
    x2 = 540 - l2.w / 2
    x3 = 540 - l3.w / 2
    # swipe band (under FOSTERING), wiping on 1.8 -> 2.12
    wu = K.ramp(t, B(3), B(3) + 0.32, 'inout_cubic')
    bx0, bx1 = F1_BAND
    wipe_x = bx0 - 40 + wu * (bx1 - bx0 + 80)
    if wu > 0:
        band, bshade = Ad['band']
        hh, ww = band.shape
        xs = bx0 + np.arange(ww, dtype=np.float32) + 0.5
        m = np.clip((wipe_x - xs) / 30.0 + 0.5, 0, 1)
        y0 = int(F1_BASE[1] - l2.ts.layout.cap / 2 - hh / 2 + 4)
        bb.add(paint_shaded(ink, band * m[None, :], bshade, bx0, y0, K.hexlin(MAG)))
    # words (stamped)
    hits1 = (B(0), B(0.5))
    for i, th in enumerate(hits1):
        draw_word_stamp(ink, bb, l1, i, x1, F1_BASE[0], t, th, 1.7, light, cam, Ad['l1h'])
    if wu <= 0:
        draw_word_stamp(ink, bb, l2, 0, x2, F1_BASE[1], t, B(1), 1.9, light, cam, Ad['l2h'])
    else:
        cy = F1_BASE[1] - l2.ts.layout.cap / 2
        anc = l2.anc((0.5, 0.5))
        bb.add(X.draw_hmask(ink, l2.spr, 540, cy, anc, -1e4, wipe_x, soft=14.0, invert=True))
        bb.add(X.draw_hmask(ink, l2i.spr, 540, cy, l2i.anc((0.5, 0.5)), -1e4, wipe_x, soft=14.0))
    hits3 = (B(1.5), B(1.75), B(2))
    for i, th in enumerate(hits3):
        draw_word_stamp(ink, bb, l3, i, x3, F1_BASE[2], t, th, 1.6, light, cam, Ad['l3h'])
    # brackets snap in round FOSTERING
    if t >= B(2.5) - 0.06:
        sp = K.spring(t - (B(2.5) - 0.06), freq=3.0, damping=0.42)
        cy = F1_BASE[1] - l2.ts.layout.cap / 2
        for d, cx in ((-1, 104), (1, 976)):
            spr, ax, ay = X.chevron_sprite(100, 15, d, tuple(K.hexlin(MAG)))
            off = (1 - sp) * 150 * d
            sc = 1 + (1 - sp) * 0.5
            bb.add(K.draw(ink, spr, cx + off, cy, anchor=(ax, ay), scale=max(sc, 0.2),
                          opacity=min(1.0, (t - B(2.5) + 0.06) / 0.05)))
    # handwritten line + scribble underline under "everyday."
    hand = Ad['hand1']
    write_on(ink, bb, hand, 540, F1_HAND_BASE, t, B(4), 1.15)
    uu = K.ramp(t, 3.62, 4.02, 'inout_sine')
    if uu > 0:
        w_ev = hand.words[-1]
        left = 540 - hand.w / 2
        pts = X.scribble_path(left + w_ev[1] - 6, left + w_ev[2] + 4, F1_HAND_BASE + 26, seed=11, amp=12,
                              loops=1, slope=-6)
        draw_stroke(ink, bb, pts, 7.0, C['ORANGE'], 0.0, uu)


# ============================================================================================ frame 2 / 3
def list_item_alpha(i, t):
    return 1.0


def f2_list_ink(ink, bb, t, light):
    Ad = A()
    hits = (B(9), B(12), B(14))
    for i, (mag, plum) in enumerate(Ad['list']):
        th = hits[i]
        if t < th - 0.1:
            continue
        nxt = hits[i + 1] if i + 1 < 3 else 99
        active = t < nxt
        txt = mag if active else plum
        base = F2_BASE[i]
        cap = txt.ts.layout.cap
        # exit into slots at 10.2 (staggered)
        if t >= T_F3:
            slot_rise(ink, bb, txt, F2_X, base - cap, t, -10, 0.1, out_t0=T_F3 + 0.05 * i, out_dur=0.28,
                      anchor_x=0.0, overshoot=False)
            continue
        st = stamp(t, th, 1.45)
        if st is None:
            continue
        s, op, lift = st
        anc = txt.anc((0.0, 1.0))
        if lift > 0.02:
            (dx, dy), ln = light.shadow_dir()
            off = 50 * lift * min(ln, 2.5)
            bb.add(K.draw(ink, _sil(txt.spr), F2_X + dx * off, base + dy * off, anchor=anc, scale=s,
                          opacity=0.2, blur=4 + 12 * lift))
        # colour change MAG -> PLUM crossfade when the next item lands
        if not active and t < nxt + 0.25:
            k = K.ramp(t, nxt, nxt + 0.25, 'out_cubic')
            bb.add(K.draw(ink, mag.spr, F2_X, base, anchor=mag.anc((0.0, 1.0)), scale=s, opacity=1 - k))
            bb.add(K.draw(ink, plum.spr, F2_X, base, anchor=anc, scale=s, opacity=k))
        else:
            bb.add(K.draw(ink, txt.spr, F2_X, base, anchor=anc, scale=s, opacity=op))


def f2_ding_ink(ink, bb, t):
    """Oven-timer 'ding': three short hand-drawn ORANGE strokes burst from the cupcake's top (b16)."""
    t0 = B(16)
    if t < t0 - 0.02 or t > t0 + 0.75:
        return
    (cx, cy), _, _ = PROPS2['cupcake']
    top = cy - 300 - 18
    for k, ang in enumerate((-58.0, -90.0, -122.0)):
        a = math.radians(ang)
        r0, r1 = 40.0, 92.0 - 10 * abs(k - 1)
        u_in = K.ramp(t, t0 + 0.02 * k, t0 + 0.12 + 0.02 * k, 'out_cubic')
        u_out = K.ramp(t, t0 + 0.45, t0 + 0.7, 'in_cubic')
        p0 = (cx + math.cos(a) * r0, top + math.sin(a) * r0 + 20)
        p1 = (cx + math.cos(a) * r1, top + math.sin(a) * r1 + 20)
        pts = X.resample(np.array([p0, p1]), 2.0)
        draw_stroke(ink, bb, pts, 8.0, C['ORANGE'], u_out, u_in)


def f2_path_ink(ink, bb, t):
    """ORANGE dashed bus route drawn across the paper (fades as frame 3 starts)."""
    u = K.ramp(t, 5.7, 6.6, 'inout_sine')
    if u <= 0:
        return
    fade = 1 - K.ramp(t, T_F3, T_F3 + 0.5, 'inout_sine')
    if fade <= 0:
        return
    draw_stroke(ink, bb, A()['bus_path'], 7.0, C['ORANGE'], 0.0, u, dash=(22, 15), opacity=0.92 * fade)


# pencil scribble (frame 2, HOMEWORK)
def scribble_pts():
    """A quick cursive pencil line (looped 'handwriting' made of a prolate cycloid with natural variation)."""
    rng = np.random.default_rng(21)
    th = np.linspace(0, 13 * math.pi, 900)
    amp = 1.0 + 0.25 * np.sin(th * 0.37 + 1.0) + 0.12 * np.sin(th * 1.3)
    x = 8.6 * th - 13.0 * np.sin(th) * amp
    y = -15.0 * np.cos(th) * amp - 0.9 * th
    pts = np.stack([590 + x, 1258 + y], 1)
    return X.resample(pts, 2.0)


_SCRIB = None


def f2_scribble_ink(ink, bb, t):
    global _SCRIB
    if _SCRIB is None:
        _SCRIB = scribble_pts()
    u = K.ramp(t, 7.5, 8.25, 'inout_sine')
    if u <= 0:
        return None
    fade = 1 - K.ramp(t, T_F3 + 0.6, T_F3 + 1.1, 'inout_sine')
    if fade <= 0:
        return None
    draw_stroke(ink, bb, _SCRIB, 3.4, (0.05, 0.045, 0.055), 0.0, u, opacity=0.82 * fade)
    return X.path_point(_SCRIB, u)


def f3_ink(ink, bb, t, light):
    Ad = A()
    t_lines = (B(18), B(19), B(20))
    for i, txt in enumerate(Ad['h3']):
        if i < 2:
            slot_rise(ink, bb, txt, 540, F3_CAP[i], t, t_lines[i] - 0.05, 0.42)
        else:
            st = stamp(t, t_lines[i], 1.55)
            if st is None:
                continue
            s, op, lift = st
            cy = F3_CAP[i] + txt.ts.layout.cap / 2
            if lift > 0.02:
                (dx, dy), ln = light.shadow_dir()
                off = 70 * lift * min(ln, 2.5)
                bb.add(K.draw(ink, _sil(txt.spr), 540 + dx * off, cy + dy * off, anchor=txt.anc((0.5, 0.5)),
                              scale=s, opacity=0.22, blur=4 + 14 * lift))
            bb.add(txt.draw(ink, 540, cy, scale=s, opacity=op))
    # supporting rows: text rises out of a slot right after its icon pops
    for i, txt in enumerate(Ad['rows']):
        t0 = B(21 + i)
        cap = txt.ts.layout.cap
        slot_rise(ink, bb, txt, 238, F3_ROWS[i] - cap / 2, t, t0 + 0.05, 0.38, anchor_x=0.0)


# ============================================================================================ frame 4
def house_pos(t):
    """(x, ground_y, scale) of the evening house."""
    u = K.ramp(t, B(30) + 0.05, B(30) + 0.6, 'inout_cubic')
    x = HOUSE_DROP[0]
    y = HOUSE_DROP[1] + (HOUSE_END[1] - HOUSE_DROP[1]) * u
    return x, y, 1.0


def f4_ink(ink, bb, t, light):
    Ad = A()
    t_lines = (B(26), B(26.75), B(27.5))
    for i, txt in enumerate(Ad['h4']):
        slot_rise(ink, bb, txt, 540, F4_CAP[i], t, t_lines[i] - 0.05, 0.42, out_t0=B(29.75) + 0.06 * (2 - i),
                  out_dur=0.26)
    hand = Ad['hand2']
    write_on(ink, bb, hand, 540, F4_HAND_BASE, t, B(31) + 0.02, 0.55)
    uu = K.ramp(t, 19.08, 19.36, 'inout_sine')
    if uu > 0:
        w_room = hand.words[-1]
        left = 540 - hand.w / 2
        pts = X.scribble_path(left + w_room[1] - 4, left + w_room[2] + 2, F4_HAND_BASE + 26, seed=5, amp=12,
                              loops=1, slope=-7)
        draw_stroke(ink, bb, pts, 8.0, C['ORANGE'], 0.0, uu)
    # phone / url line (printed): rises in on the end card
    ph = Ad['phone']
    slot_rise(ink, bb, ph, 540, 1418, t, 19.02, 0.33, overshoot=False)


# ============================================================================================ props (after light)
def props_frame1(cv, layer, lb, t, light):
    """Morning: the alarm clock sits on the desk below the question (revealed as the hook camera pulls back)
    and rattles once at b4 as the handwritten line starts."""
    pr = A()['clock']
    cam = hook_cam(t)
    x, y = w2s(cam, 540, 1530)
    z = cam[2] if cam is not None else 1.0
    if y - pr.height * z > H + 40:
        return
    tr = B(4) + 0.15
    rot, hop = 0.0, 0.0
    if t > tr:
        d = t - tr
        e = math.exp(-d * 3.2)
        rot = 4.0 * math.sin(d * 62) * e
        hop = 7.0 * abs(math.sin(d * 31)) * e
    yaw = -14 + 5 * math.sin(t * 0.8)
    pr.shadow(cv, x, y, light, lift=hop, yaw=yaw, scale=z)
    lb.add(pr.draw(layer, x, y - hop, yaw=yaw, scale=z, rot=rot))


# frame-2 props: ground point, landing time, base yaw
PROPS2 = {'backpack': ((250, 1232), 5.70, -12.0), 'book': ((785, 1196), 7.38, 0.0),
          'bowl': ((305, 1562), 8.55, -10.0), 'cupcake': ((785, 1566), 8.85, 12.0)}
GROUPS = [('backpack',), ('book',), ('bowl', 'cupcake')]
# HOMEWORK: cursive lines written on the book's right page (sprite coords normalised by the sprite width,
# measured on the yaw-0 render: the page's ruled lines rise ~10 deg to the right)
WRITE_T = (7.52, 8.18)
REST_TIP = None


@functools.lru_cache(maxsize=1)
def write_paths():
    def cursive(x0, y0, length, seed, loops):
        rng = np.random.default_rng(seed)
        th = np.linspace(0, loops * 2 * math.pi, 60 * loops)
        amp = 1.0 + 0.22 * np.sin(th * 0.41 + rng.uniform(0, 6)) + 0.1 * np.sin(th * 1.7)
        a, b = length / (loops * 2 * math.pi), 0.0105
        x = a * th - b * np.sin(th) * amp
        y = -b * 0.95 * np.cos(th) * amp
        ang = math.radians(-10.0)
        xr = x * math.cos(ang) - y * math.sin(ang)
        yr = x * math.sin(ang) + y * math.cos(ang)
        return np.stack([x0 + xr, y0 + yr], 1)
    return [cursive(0.548, 0.488, 0.165, 3, 8), cursive(0.548, 0.536, 0.115, 7, 6)]


def book_to_screen(pr, x, y, scale, pts_norm):
    """Sprite-normalised points -> screen px for the book drawn with its ground point at (x, y)."""
    sw = pr.a.size[0]
    gx, gy = pr.ground()
    P = np.asarray(pts_norm) * sw
    return np.stack([x + (P[:, 0] - gx) * pr.k * scale, y + (P[:, 1] - gy) * pr.k * scale], 1)


def draw_book_writing(cv, layer, lb, t, light, x, y):
    """The book (pencil removed) + graphite lines + the book's own pencil lifting off, writing, settling back."""
    pr = A()['book']
    sp = X.split_book(X.register_prop(pr), 0.0) if pr.real else None
    if sp is None:
        return False
    book, pen, tip, _ = sp
    sw = pr.a.size[0]
    anc = pr.anchor_frac()
    k = pr.k
    lb.add(K.draw(layer, book, x, y, scale=k, anchor=anc))
    paths = [book_to_screen(pr, x, y, 1.0, p) for p in write_paths()]
    lens = [X._arclen(p)[-1] for p in paths]
    tot = sum(lens) + 40.0                               # +40 px of pen travel between the lines
    w0, w1 = WRITE_T
    u = K.ramp(t, w0, w1, 'linear')
    dist = u * tot
    # graphite written so far
    acc = 0.0
    for i, p in enumerate(paths):
        d = min(max(dist - acc, 0.0), lens[i])
        if d > 0:
            al, ax0, ay0 = X.stroke_alpha(p, 2.1 * k / 0.75, 0.0, d / lens[i])
            lb.add(X.paint(layer, al, ax0, ay0, (0.035, 0.032, 0.04), 0.9))
        acc += lens[i] + (40.0 if i == 0 else 0.0)
    # pencil tip position
    rest = np.array([x + (tip[0] - sw * anc[0]) * k, y + (tip[1] - pr.a.size[1] * anc[1]) * k])
    start = paths[0][0]
    if t < w0:
        f = K.ramp(t, w0 - 0.14, w0, 'inout_sine')
        pos = rest + (start - rest) * f
        lift = 14.0 * math.sin(math.pi * f)
        rot = -6.0 * math.sin(math.pi * f)
    elif t <= w1:
        acc = 0.0
        pos = paths[-1][-1]
        lift = 0.0
        for i, p in enumerate(paths):
            if dist <= acc + lens[i]:
                px, py, _ = X.path_point(p, (dist - acc) / lens[i])
                pos = np.array([px, py])
                break
            acc += lens[i]
            if i == 0 and dist <= acc + 40.0:          # hop to the next line
                f = (dist - acc) / 40.0
                pos = paths[0][-1] + (paths[1][0] - paths[0][-1]) * f
                lift = 12.0 * math.sin(math.pi * f)
                break
            acc += 40.0
        rot = 4.0 * math.sin(t * 31.0) + 2.0 * math.sin(t * 13.0)
    else:
        f = K.ramp(t, w1, w1 + 0.16, 'inout_sine')
        pos = paths[-1][-1] + (rest - paths[-1][-1]) * f
        lift = 14.0 * math.sin(math.pi * f)
        rot = -6.0 * math.sin(math.pi * f)
    tip_anchor = (tip[0] / pen.shape[1], tip[1] / pen.shape[0])
    sil = _sil(pen)
    K.draw(layer, sil, pos[0] + 5 + lift * 0.5, pos[1] + 6 + lift * 0.6, scale=k, rot=rot, anchor=tip_anchor,
           opacity=0.28, blur=2.5 + lift * 0.3)
    lb.add(K.draw(layer, pen, pos[0], pos[1] - lift, scale=k, rot=rot, anchor=tip_anchor))
    return True


def props_frame2(cv, layer, lb, t, light, morph=True):
    Ad = A()
    groups = {'backpack': 0, 'book': 1, 'bowl': 2, 'cupcake': 2}
    for name, ((x, y), tl, yaw0) in PROPS2.items():
        pr = Ad[name]
        dr = X.drop(t, tl - 0.30, 0.30)
        if dr is None:
            continue
        g = groups[name]
        if morph and t >= T_F3 + 0.6 * g:
            continue       # handled by the tumble / morph
        yaw = yaw0 + (0.0 if name == 'book' else 4.0 * math.sin(t * 0.9 + g))
        pr.shadow(cv, x, y, light, lift=dr['lift'], yaw=yaw, scale=dr['scale'], opacity=dr['opacity'])
        if name == 'book' and WRITE_T[0] - 0.16 <= t <= WRITE_T[1] + 0.17 and dr['land'] >= 1:
            if draw_book_writing(cv, layer, lb, t, light, x, y - dr['lift'] * 0.35):
                continue
        lb.add(pr.draw(layer, x, y - dr['lift'] * 0.35, yaw=yaw, scale=dr['scale'], squash=dr['squash'],
                       opacity=dr['opacity']))
        if name == 'book' and t > WRITE_T[1] + 0.17:
            draw_book_lines(layer, lb, x, y, t)
    # flour puff out of the bowl on landing (and a smaller second puff from the whisk)
    if 8.5 <= t <= 10.1 and not (morph and t >= T_F3 + 1.2):
        (bx, by), tl, _ = PROPS2['bowl']
        pr = Ad['bowl']
        fx, fy = pr.feature('batter', -10.0)
        X.puff(layer, t, tl - 0.01, bx + fx, by + fy - 10, n=46, spread=190, seed=12, rgb=(1.0, 0.985, 0.95),
               size=(6, 20), up=-1.8, dur=1.25, opacity=0.95, ang=(-170, -10))
        X.puff(layer, t, tl + 0.35, bx + fx + 30, by + fy - 30, n=18, spread=90, seed=13, rgb=(1.0, 0.985, 0.95),
               size=(4, 12), up=-1.2, dur=0.9, opacity=0.8, ang=(-150, -30))
    # bus drives along the dashed path
    if 5.95 <= t <= 7.1:
        u = (t - 5.95) / 1.1
        u = u * u * (3 - 2 * u) * 0.35 + u * 0.65
        px, py, ang = X.path_point(Ad['bus_path'], u)
        bus = Ad['bus']
        bob = 2.0 * math.sin(t * 46) + 1.2 * math.sin(t * 29)
        bus.shadow(cv, px, py, light, lift=0, scale=1.0)
        lb.add(bus.draw(layer, px, py - 10 + bob, rot=ang * 0.7, scale=1.0))


def draw_book_lines(layer, lb, x, y, t):
    """The finished pencil lines stay on the page after writing (until the book tumbles)."""
    pr = A()['book']
    if not pr.real:
        return
    for p in write_paths():
        P = book_to_screen(pr, x, y, 1.0, p)
        al, ax0, ay0 = X.stroke_alpha(P, 2.1 * pr.k / 0.75)
        lb.add(X.paint(layer, al, ax0, ay0, (0.035, 0.032, 0.04), 0.9))


def props_frame3(cv, layer, lb, t, light):
    """Tumble + morph of the frame-2 props into blocks; tower; supporting-row icons."""
    Ad = A()
    groups = [[(nm, PROPS2[nm][0]) for nm in grp] for grp in GROUPS]
    blocks = Ad['blocks']
    tower_h = 0.0
    for g, members in enumerate(groups):
        t0 = T_F3 + 0.6 * g                 # hop starts
        t_m = t0 + 0.24                      # morph moment (top of the hop, mid-spin)
        t_land = t0 + 0.6                    # block lands on the tower (b18 / b19 / b20)
        spr, anc, ks = blocks[g]
        bh = 170.0
        gx, gy = TOWER[0], TOWER[1] - bh * g
        if t < t0:
            continue
        if t < t_m + 0.05:
            # props hop up, spin and shrink toward the morph point
            u = K.ramp(t, t0, t_m + 0.05, out_quad)
            for name, (x, y) in members:
                pr = Ad[name]
                mx, my = (x * 0.4 + gx * 0.6), (y * 0.55 + (gy - 420) * 0.45)
                px = x + (mx - x) * u
                py = y + (my - y) * u - 160 * math.sin(math.pi * min(u, 1.0)) * 0.6
                rot = 300 * u * (1 if x < 540 else -1)
                sc = 1.0 - 0.35 * u
                op = 1.0 - K.ramp(t, t_m - 0.03, t_m + 0.05, 'linear')
                pr.shadow(cv, px, py, light, lift=(y - py) + 40, scale=sc, opacity=op * 0.7)
                lb.add(pr.draw(layer, px, py, rot=rot, scale=sc, opacity=op))
        if t >= t_m - 0.04 and t < t_land + 2.0:
            X.puff(layer, t, t_m - 0.02, gx * 0.6 + members[0][1][0] * 0.4, (gy - 420) * 0.45 +
                   members[0][1][1] * 0.55 - 60, n=26, spread=120, seed=40 + g, size=(5, 16), dur=0.7,
                   ang=(-180, 180), opacity=0.9)
        if t >= t_m - 0.04:
            # block appears at the morph point (spinning), then drops onto the tower
            mx = (members[0][1][0] * 0.4 + gx * 0.6)
            my = (members[0][1][1] * 0.55 + (gy - 420) * 0.45)
            u = K.ramp(t, t_m, t_land, in_quad)
            px = mx + (gx - mx) * K.ramp(t, t_m, t_land, 'out_sine')
            py = my + (gy - my) * u
            rot = (1 - K.ramp(t, t_m - 0.04, t_land, 'out_cubic')) * 220 * (1 if mx < 540 else -1)
            pop = K.ramp(t, t_m - 0.04, t_m + 0.08, 'out_back')
            sq = (1.0, 1.0)
            wob = 0.0
            if t >= t_land:
                d = t - t_land
                imp = math.exp(-d * 10) * math.cos(d * 32)
                sq = (1 + 0.07 * imp, 1 - 0.09 * imp)
            # tower wobble: STABILITY. slam (b20) rocks the stack once, then it settles
            ws = t - B(20)
            if ws > 0:
                wob = 2.6 * math.exp(-ws * 3.2) * math.sin(ws * 13) * (g + 1) / 3
            lift = max(0.0, gy - py)
            if g == 0 or t >= t_land:
                X_ = gx + wob * (bh * g) * 0.017
            else:
                X_ = px
            if t < t_land:
                X_ = px
            sh_op = min(1.0, pop)
            _block_shadow(cv, X_ if t >= t_land else gx, gy, light, lift, ks, spr, anc, sh_op, g, t >= t_land)
            K_ = ks * pop
            lb.add(K.draw(layer, spr, X_, py if t < t_land else gy, scale=(K_ * sq[0], K_ * sq[1]),
                          rot=rot + wob, anchor=anc))
        tower_h = max(tower_h, g)
    # supporting-row icons
    icons = (Ad['i_house'], Ad['i_clock'], Ad['i_family'])
    for i, pr in enumerate(icons):
        tl = B(21 + i)
        dr = X.drop(t, tl - 0.22, 0.22, h0=160, s0=0.5)
        if dr is None:
            continue
        x, y = 165, F3_ROWS[i] + 44
        yaw = 10 * math.sin(t * 1.3 + i)
        if i == 1 and t > tl:
            yaw = 0
        pr.shadow(cv, x, y, light, lift=dr['lift'], yaw=yaw, scale=dr['scale'], opacity=dr['opacity'] * 0.8)
        rot = 0.0
        if i == 1 and t > tl:      # alarm clock: rings (shakes) briefly
            rot = 4.0 * math.sin((t - tl) * 70) * math.exp(-(t - tl) * 4)
        lb.add(pr.draw(layer, x, y - dr['lift'] * 0.3, yaw=yaw, scale=dr['scale'], squash=dr['squash'],
                       opacity=dr['opacity'], rot=rot))


def _block_shadow(cv, x, y, light, lift, ks, spr, anc, op, g, landed):
    """Tower block shadows on the paper: a cast silhouette away from the light once landed (the tower's
    shadow), a contact shadow under the base block, and a soft growing shadow where a falling block will land."""
    (dx, dy), ln = light.shadow_dir()
    base_y = TOWER[1]
    if landed:
        off = 26 * min(ln, 3.0) + 18 * g
        sil = _sil(spr)
        K.draw(cv, sil, x + dx * off, y + dy * off * 0.5 + 6, scale=ks, anchor=anc, opacity=0.24 * op, blur=10)
        if g == 0:
            c = X._contact()
            K.draw(cv, c, x + 3, base_y + 2, scale=(230 / c.shape[1], 34 / c.shape[0]), opacity=0.6 * op)
    else:
        f = float(np.clip(1.0 - lift / 700.0, 0, 1)) ** 1.5
        c = X._contact()
        w = 150 + 120 * (1 - f)
        K.draw(cv, c, x + dx * 20, y + 4, scale=(w / c.shape[1], w * 0.2 / c.shape[0]), opacity=0.45 * f * op)


def props_frame4(cv, layer, lb, t, light):
    Ad = A()
    pr = Ad['house']
    dr = X.drop(t, B(28.25) + 0.15 - 0.30, 0.30, h0=380)
    if dr is None:
        return
    x, y, sc = house_pos(t)
    yaw = -8 + 6 * math.sin(t * 0.7)
    pr.shadow(cv, x, y, light, lift=dr['lift'], yaw=yaw, scale=dr['scale'], opacity=dr['opacity'])
    lb.add(pr.draw(layer, x, y - dr['lift'] * 0.35, yaw=yaw, scale=dr['scale'] * sc, squash=dr['squash'],
                   opacity=dr['opacity']))


def endcard(cv, t):
    """logo + CTA pill (drawn after lighting: true brand colours)."""
    Ad = A()
    u = K.ramp(t, B(31.5), B(31.5) + 0.42, 'out_back')
    if u > 0:
        lg = Ad['logo']
        op = K.ramp(t, B(31.5), B(31.5) + 0.15, 'linear')
        K.draw(cv, lg, 540, 1135 + (1 - u) * 60, scale=0.94 + 0.06 * u, opacity=op)
    v = K.ramp(t, 19.05, 19.33, 'out_back')
    if v > 0:
        bt = Ad['button']
        op = K.ramp(t, 19.05, 19.15, 'linear')
        K.draw(cv, bt, 540, 1335, scale=0.7 + 0.3 * v, opacity=op)


# ============================================================================================ sheets
@functools.lru_cache(maxsize=2)
def _zoomed_sheet(fi):
    """Sheet A through the hook camera at frame fi (shared by the frame's motion-blur samples)."""
    return P.zoomed(P.sheet(0), cam_matrix(hook_cam(fi / FPS)))


def compose(sheet_id, t, fi):
    """One sheet with its content at time t: lit paper + ink, then shadows + props. fi = frame index (cache)."""
    tq = fi / FPS
    light = light_for(tq)
    ink = np.zeros((H, W, 4), np.float32)
    bb = BBox()
    sweep = None
    sh = P.sheet((0, 1, 2)[sheet_id])
    if sheet_id == 0:
        cam = hook_cam(tq)
        f1_ink(ink, bb, t, light, hook_cam(t))
        if cam is not None:
            sh = _zoomed_sheet(fi)
        su = K.ramp(t, 1.75, 3.3, 'inout_sine')
        if 0 < su < 1:
            sweep = (su, -32.0, 0.035, 0.16, (1.0, 0.90, 0.78))
    elif sheet_id == 1:
        su = K.ramp(t, B(20) + 0.15, B(20) + 0.95, 'inout_sine')
        if 0 < su < 1:
            sweep = (su, -32.0, 0.04, 0.24, (1.0, 0.90, 0.76))
        f2_path_ink(ink, bb, t)
        f2_ding_ink(ink, bb, t)
        f2_list_ink(ink, bb, t, light)
        if t >= T_F3 - 0.2:
            f3_ink(ink, bb, t, light)
    else:
        su = max(K.ramp(t, B(27.5) + 0.2, B(27.5) + 1.0, 'inout_sine'), 0.0)
        if 0 < su < 1:
            sweep = (su, -32.0, 0.04, 0.24, (1.0, 0.88, 0.72))
        su2 = K.ramp(t, 19.5, 20.5, 'inout_sine')
        if 0 < su2 < 1:
            sweep = (su2, -32.0, 0.05, 0.22, (1.0, 0.88, 0.72))
        f4_ink(ink, bb, t, light)
    cv = P.shade(sh, light, ink, bb.box, sweep=sweep, key=(sheet_id, fi))
    layer = np.zeros((H, W, 4), np.float32)
    lb = BBox()
    if sheet_id == 0:
        props_frame1(cv, layer, lb, t, light)
    if sheet_id == 1:
        props_frame2(cv, layer, lb, t, light)
        if t >= T_F3:
            props_frame3(cv, layer, lb, t, light)
    elif sheet_id == 2:
        props_frame4(cv, layer, lb, t, light)
    if lb.box is not None:
        x0, y0, x1, y1 = [int(v) for v in lb.box]
        x0, y0 = max(0, x0), max(0, y0)
        x1, y1 = min(W, x1), min(H, y1)
        if x1 > x0 and y1 > y0:
            reg = layer[y0:y1, x0:x1]
            reg[..., :3] *= tint_for(light).astype(np.float32)
            d = cv[y0:y1, x0:x1]
            d *= (1.0 - reg[..., 3:4])
            d += reg
    if sheet_id == 2:
        endcard(cv, t)
    cv[..., 3] = 1.0
    return cv


@functools.lru_cache(maxsize=1)
def pencil_sprite():
    """Procedural glossy toy pencil (horizontal, tip at the left), 4x supersampled."""
    ss = 4
    L, Wd = 250, 30
    w, h = (L + 20) * ss, (Wd + 20) * ss
    img = np.zeros((h, w, 4), np.float32)
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32) / ss
    cy = (Wd + 20) / 2
    v = (yy - cy) / (Wd / 2)                 # -1..1 across
    x = xx - 10
    body = (x > 48) & (x < 205) & (np.abs(v) <= 1)
    ferr = (x >= 205) & (x < 226) & (np.abs(v) <= 1.02)
    eras = (x >= 226) & (x < 248) & (np.abs(v) <= 0.98 - np.clip((x - 240) / 8, 0, 1) ** 2 * 0.4)
    cone_w = np.clip((x - 4) / 44, 0, 1)
    cone = (x >= 4) & (x <= 48) & (np.abs(v) <= cone_w)
    lead = cone & (x < 16)
    # facet shading across the hexagonal body
    fac = np.where(v < -0.33, 1.15, np.where(v < 0.33, 0.95, 0.68))
    col = np.zeros((h, w, 3), np.float32)
    col[body] = (K.hexlin('#FFB400') * fac[body][:, None])
    col[ferr] = (np.float32([0.62, 0.62, 0.66]) * (1.1 - 0.5 * np.abs(v[ferr]))[:, None] *
                 (0.85 + 0.15 * np.cos(x[ferr] * 1.6))[:, None])
    col[eras] = K.hexlin('#F48FB1') * (1.05 - 0.35 * np.clip(v[eras], 0, 1))[:, None]
    col[cone] = K.hexlin('#E8C49A') * (1.05 - 0.35 * np.clip(v[cone], 0, 1))[:, None]
    col[lead] = np.float32([0.05, 0.05, 0.06])
    a = (body | ferr | eras | cone).astype(np.float32)
    # gloss streak
    gl = body & (np.abs(v + 0.55) < 0.12)
    col[gl] = col[gl] * 0.5 + 0.5
    img[..., :3] = col * a[..., None]
    img[..., 3] = a
    import cv2
    small = cv2.resize(img, (w // ss, h // ss), interpolation=cv2.INTER_AREA)
    small.setflags(write=False)
    tip = (10 + 4) / small.shape[1], cy / small.shape[0]
    return small, tip


def draw_pencil(cv, layer, lb, t, light):
    """The pencil scribbling beside the book (HOMEWORK)."""
    global _SCRIB
    if _SCRIB is None:
        _SCRIB = scribble_pts()
    u = K.ramp(t, 7.5, 8.25, 'inout_sine')
    op = K.ramp(t, 7.45, 7.52, 'linear') * (1 - K.ramp(t, 8.27, 8.35, 'linear'))
    px, py, _ = X.path_point(_SCRIB, u)
    lift = 0 if 7.5 < t < 8.25 else 30
    spr, tip = pencil_sprite()
    rot = 205 + 6 * math.sin(t * 22)
    sil = _sil(spr)
    (dx, dy), ln = light.shadow_dir()
    K.draw(cv, sil, px + dx * 18 + 10, py + dy * 18 + 12, anchor=tip, rot=rot, opacity=0.25 * op, blur=5)
    lb.add(K.draw(layer, spr, px, py - lift, anchor=tip, rot=rot, opacity=op))


# ============================================================================================ transitions
@functools.lru_cache(maxsize=1)
def _sheet_shadow():
    q = 4
    pad = 40
    a = np.zeros((H // q + 2 * pad, W // q + 2 * pad), np.float32)
    a[pad:pad + H // q, pad:pad + W // q] = 1.0
    a = K.gblur(a, 7.0, border='constant')
    spr = np.zeros(a.shape + (4,), np.float32)
    spr[..., 3] = a
    spr[..., :3] = a[..., None] * np.float32(X.SHADOW_RGB) * 0.5
    spr.setflags(write=False)
    return spr


_FLIP_CAM = K.Cam(pos=(0, 0, -4200), focal=4200)


@functools.lru_cache(maxsize=1)
def _shadow_band():
    a = np.linspace(1.0, 0.0, 64, dtype=np.float32) ** 1.8
    a = np.repeat(a[:, None], 64, 1)
    xs = np.linspace(-1, 1, 64, dtype=np.float32)
    a *= np.clip((1 - np.abs(xs)) * 4, 0, 1)[None, :]
    spr = np.zeros((64, 64, 4), np.float32)
    spr[..., 3] = a
    spr[..., :3] = a[..., None] * np.float32(X.SHADOW_RGB) * 0.7
    spr.setflags(write=False)
    return spr


@functools.lru_cache(maxsize=2)
def frozen(sheet_id, t_freeze):
    """A sheet frozen at t_freeze (outgoing sheets during transitions): built once, read-only."""
    cv = compose(sheet_id, t_freeze, frame_index(t_freeze))
    cv.setflags(write=False)
    return cv


def frame_index(t):
    return int(round(t * FPS))


def draw(t):
    fi = frame_index(t)
    if t < T_SLIDE0:
        cv = compose(0, t, fi)
    elif t < T_SLIDE1:
        u = K.ramp(t, T_SLIDE0, T_SLIDE1, 'out_quart')
        base = frozen(0, T_SLIDE0)
        cv = np.empty_like(base)
        cv[...] = base
        push = int(round(-170 * u))
        if push:
            cv[:, :W + push] = base[:, -push:]
            cv[:, W + push:] = base[:, W - 1:W]
        cv[..., :3] *= np.float32(1.0 - 0.12 * u)
        new = compose(1, t, fi)
        x = 540 + (1 - u) * 1180
        y = 960 + (1 - u) * 140
        rot = (1 - u) * 6.0
        sh = _sheet_shadow()
        K.draw(cv, sh, x - 26, y + 22, scale=4.0, rot=rot, opacity=0.55)
        K.draw(cv, new, x, y, rot=rot)
    elif t < T_FLIP0:
        cv = compose(1, t, fi)
    elif t < T_FLIP1:
        u = K.ramp(t, T_FLIP0, T_FLIP1, in_quad)
        cv = compose(2, t, fi)
        page = frozen(1, T_FLIP0).copy()
        rx = -90.0 * u
        th = math.radians(-rx)
        # the lifting page turns away from the key light: darker overall and toward its (nearer) bottom edge
        k = math.sin(th)
        if k > 0:
            ramp = np.linspace(1.0, 1.0 - 0.30 * k, H, dtype=np.float32)[:, None, None]
            page[..., :3] *= ramp * np.float32(1.0 - 0.18 * k)
        # projected bottom edge of the page
        depth = 4200.0 - 1920.0 * math.sin(th)
        ye = 960.0 + (-960.0 + 1920.0 * math.cos(th)) * 4200.0 / depth
        hw = 540.0 * 4200.0 / depth
        # soft shadow cast on the sheet below, just under the lifting edge
        sb = _shadow_band()
        hgt = 40 + 420 * k
        K.draw(cv, sb, 540, ye - 6, scale=((2 * hw + 120) / sb.shape[1], hgt / sb.shape[0]), anchor=(0.5, 0.0),
               opacity=min(1.0, 0.55 * k * 3) * (1 - 0.5 * u))
        K.draw_plane(cv, page, _FLIP_CAM, (0, -960, 0), W, rot=(rx, 0, 0), anchor=(0.5, 0.0), dof=False)
        # thin lit paper edge
        if 0 < ye < H:
            y0 = int(round(ye)) - 1
            x0, x1 = max(0, int(540 - hw)), min(W, int(540 + hw))
            cv[max(0, y0):y0 + 2, x0:x1, :3] = cv[max(0, y0):y0 + 2, x0:x1, :3] * 0.4 + 0.6 * np.float32(
                [0.95, 0.88, 0.76])
    else:
        cv = compose(2, t, fi)
    foreground(cv, t, light_for(frame_index(t) / FPS))
    shake_hits = ((B(0), 5.0), (B(1), 7.0), (B(20), 4.0))
    sx = sy = 0.0
    for th, amp in shake_hits:
        k = K.impulse(t, th, decay=14.0)
        if k > 0.01:
            dx, dy, _ = K.shake(t, amp * k, 22, seed=int(th * 10))
            sx += dx
            sy += dy
    ix, iy = int(round(sx)), int(round(sy))
    if ix or iy:
        cv = np.roll(cv, (iy, ix), axis=(0, 1))
    return cv


# ============================================================================================ foreground
# near-lens leaves (a houseplant beside the desk): heavily defocused, swaying, casting soft shadows on the paper.
FG_LEAVES = [  # x, y (stem base), size px, rot deg, blur, sway phase, shadow offset scale
    (-70, 110, 330, 100.0, 20.0, 0.0, 1.0),
    (1135, 1835, 390, -52.0, 22.0, 0.9, 1.1),
    (-50, 1915, 300, 38.0, 18.0, 2.6, 0.9),
]


def foreground(cv, t, light):
    spr = X.leaf_sprite()
    sh = X.leaf_shadow_sprite()
    (dx, dy), ln = light.shadow_dir()
    for x, y, size, rot, bl, ph, so in FG_LEAVES:
        sway = 3.2 * math.sin(t * 0.9 + ph) + 1.2 * math.sin(t * 2.3 + ph * 2)
        px = x + 6 * math.sin(t * 0.6 + ph)
        py = y + 4 * math.sin(t * 0.8 + ph * 1.3)
        sc = size / spr.shape[0]
        off = 120 * so * min(ln, 2.5)
        K.draw(cv, sh, px + dx * off, py + dy * off, scale=sc * 1.05, rot=rot + sway * 1.2, anchor=(0.5, 0.97),
               opacity=0.30, blur=bl * 1.8 + 8)
    for x, y, size, rot, bl, ph, so in FG_LEAVES:
        sway = 3.2 * math.sin(t * 0.9 + ph) + 1.2 * math.sin(t * 2.3 + ph * 2)
        px = x + 6 * math.sin(t * 0.6 + ph)
        py = y + 4 * math.sin(t * 0.8 + ph * 1.3)
        sc = size / spr.shape[0]
        lt = np.float32(np.clip(light.mean_rgb() / P.light_at(0.0).mean_rgb(), 0.5, 1.4)) * 0.62
        K.draw(cv, _lit_leaf(tuple(np.round(lt, 2))), px, py, scale=sc, rot=rot + sway, anchor=(0.5, 0.97),
               blur=bl)


@functools.lru_cache(maxsize=8)
def _lit_leaf(tint):
    spr = X.leaf_sprite().copy()
    spr[..., :3] *= np.float32(tint)
    spr.setflags(write=False)
    return spr


def post(cv, t):
    return K.post(cv, LOOK, t, vignette=0.10, grain=0.012, chroma=0.6)


def samples(t):
    if t < 1.45:
        return 5
    if T_SLIDE0 - 0.02 < t < T_SLIDE1 + 0.05:
        return 7
    if T_F3 - 0.02 < t < B(20) + 0.2:
        return 5
    if T_FLIP0 + 0.25 < t < T_FLIP1 + 0.02:
        return 11
    if T_FLIP0 - 0.02 < t < T_FLIP1 + 0.02:
        return 5
    return 3


def cues():
    return anim1_sfx.cues()
