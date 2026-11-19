"""BMHC façade as a 3D line model (the "AI reconstruction") + a tiny perspective renderer.

Inspired by the building in BMHC's line-art logo: a tall central tower with octagonal corner turrets and pinnacles, a
porch with a pointed-arch door, two long crenellated wings (ground-floor arcade of pointed arches + two rows of
mullioned windows) and gabled end pavilions with pinnacles.

Every line carries:  kind  ('wall' | 'window' | 'arch' | 'detail' | 'brick' | 'door')
                     order (0..1, the order in which the AI 'draws' it: bottom-up, centre-out)
                     n     (the outward normal of the face it belongs to, for hidden-line culling; None = always drawn)
"""
import math
import numpy as np
import cv2

SEGS = []          # (p0, p1, kind, normal, order)
OCC = []           # solid boxes (x0, x1, y0, y1, z0, z1) used for hidden-line occlusion


def _add(p0, p1, kind, n=None):
    SEGS.append((np.array(p0, np.float32), np.array(p1, np.float32), kind, None if n is None else np.array(n, np.float32)))


def poly(pts, kind, n=None, closed=True):
    m = len(pts)
    for i in range(m if closed else m - 1):
        _add(pts[i], pts[(i + 1) % m], kind, n)


def boxl(x0, x1, y0, y1, z0, z1, kind='wall', faces='all'):
    """Box edges; each edge belongs to two faces, so it is drawn if either face is visible (stored twice with each normal)."""
    V = lambda x, y, z: (x, y, z)
    F = {
        'front': ([V(x0, y0, z0), V(x1, y0, z0), V(x1, y0, z1), V(x0, y0, z1)], (0, -1, 0)),
        'back': ([V(x0, y1, z0), V(x1, y1, z0), V(x1, y1, z1), V(x0, y1, z1)], (0, 1, 0)),
        'left': ([V(x0, y0, z0), V(x0, y1, z0), V(x0, y1, z1), V(x0, y0, z1)], (-1, 0, 0)),
        'right': ([V(x1, y0, z0), V(x1, y1, z0), V(x1, y1, z1), V(x1, y0, z1)], (1, 0, 0)),
        'top': ([V(x0, y0, z1), V(x1, y0, z1), V(x1, y1, z1), V(x0, y1, z1)], (0, 0, 1)),
    }
    for k, (pts, n) in F.items():
        if faces == 'all' or k in faces:
            poly(pts, kind, n)
    OCC.append((x0, x1, y0, y1, z0, z1))


def arch(cx, z0, w, spring, y, kind='arch', n=(0, -1, 0), seg=10, closed=True):
    r = w * 0.85
    cxl, cxr = -w / 2 + r, w / 2 - r
    a_end = math.acos(-cxl / r)
    pts = [(cx - w / 2, y, z0), (cx - w / 2, y, z0 + spring)]
    for i in range(1, seg + 1):
        a = math.pi - (math.pi - a_end) * i / seg
        pts.append((cx + cxl + r * math.cos(a), y, z0 + spring + r * math.sin(a)))
    for i in range(1, seg):
        a = (math.pi - a_end) - (math.pi - a_end) * i / seg
        pts.append((cx + cxr + r * math.cos(a), y, z0 + spring + r * math.sin(a)))
    pts += [(cx + w / 2, y, z0 + spring), (cx + w / 2, y, z0)]
    poly(pts, kind, n, closed=closed)
    return z0 + spring + r * math.sin(a_end)


def rect_win(cx, z0, w, h, y, kind='window', n=(0, -1, 0), mull=True):
    poly([(cx - w / 2, y, z0), (cx + w / 2, y, z0), (cx + w / 2, y, z0 + h), (cx - w / 2, y, z0 + h)], kind, n)
    if mull:
        _add((cx, y, z0), (cx, y, z0 + h), kind, n)
        _add((cx - w / 2, y, z0 + h * 0.62), (cx + w / 2, y, z0 + h * 0.62), kind, n)


def crenel(x0, x1, y, z, step=0.55, hgt=0.5, kind='detail', n=(0, -1, 0)):
    pts = []
    x = x0
    up = True
    while x < x1 - 1e-6:
        nx = min(x1, x + step)
        zz = z + (hgt if up else 0)
        pts += [(x, y, zz), (nx, y, zz)]
        up = not up
        x = nx
    pts2 = [pts[0]]
    for a, b in zip(pts[:-1], pts[1:]):
        if abs(a[2] - b[2]) > 1e-6:
            pts2.append(a)
        pts2.append(b)
    poly(pts2, kind, n, closed=False)


def prism(cx, cy, r, z0, z1, k=8, kind='detail'):
    OCC.append((cx - r * 0.9, cx + r * 0.9, cy - r * 0.9, cy + r * 0.9, z0, z1))
    for i in range(k):
        a0, a1 = 2 * math.pi * i / k, 2 * math.pi * (i + 1) / k
        n = (math.cos((a0 + a1) / 2), math.sin((a0 + a1) / 2), 0)
        p = lambda a, z: (cx + r * math.cos(a), cy + r * math.sin(a), z)
        poly([p(a0, z0), p(a1, z0), p(a1, z1), p(a0, z1)], kind, n)


def spire(cx, cy, r, z0, h, k=8, kind='detail'):
    apex = (cx, cy, z0 + h)
    for i in range(k):
        a0, a1 = 2 * math.pi * i / k, 2 * math.pi * (i + 1) / k
        n = (math.cos((a0 + a1) / 2), math.sin((a0 + a1) / 2), 0.3)
        p = lambda a: (cx + r * math.cos(a), cy + r * math.sin(a), z0)
        poly([p(a0), p(a1), apex], kind, n)
    _add(apex, (cx, cy, z0 + h + 0.8), kind)


def build():
    SEGS.clear()
    OCC.clear()
    # ---- wings (both sides), front face at y=0
    for s in (-1, 1):
        xa, xb = 4.2 * s, 21.0 * s
        x0, x1 = min(xa, xb), max(xa, xb)
        boxl(x0, x1, 0, 9, 0, 11.5)
        crenel(x0, x1, 0, 11.5)
        _add((x0, 0, 4.0), (x1, 0, 4.0), 'detail', (0, -1, 0))          # string courses
        _add((x0, 0, 7.6), (x1, 0, 7.6), 'detail', (0, -1, 0))
        bays = 11
        for i in range(bays):
            cx = x0 + (x1 - x0) * (i + 0.5) / bays
            arch(cx, 0.3, 1.05, 1.9, 0)                                 # ground arcade
            rect_win(cx, 4.6, 0.95, 2.3, 0)                             # first floor
            rect_win(cx, 8.25, 0.95, 2.3, 0)                            # second floor
        for i in range(0, bays + 1, 2):                                  # small pinnacles along the parapet
            cx = x0 + (x1 - x0) * i / bays
            spire(cx, 0.15, 0.22, 11.5, 1.6, k=4)
        # ---- end pavilions
        pa, pb = 21.0 * s, 26.5 * s
        p0, p1 = min(pa, pb), max(pa, pb)
        boxl(p0, p1, -1.6, 9.5, 0, 13.5)
        pc = (p0 + p1) / 2
        poly([(p0, -1.6, 13.5), (pc, -1.6, 17.0), (p1, -1.6, 13.5)], 'detail', (0, -1, 0))
        _add((pc, -1.6, 17.0), (pc, 9.5, 17.0), 'detail', (0, 0, 1))
        _add((p0, -1.6, 13.5), (p0, 9.5, 13.5), 'detail', (-1, 0, 0))
        for xx in (p0, p1):
            prism(xx, -1.6, 0.35, 0, 15.5, k=6)
            spire(xx, -1.6, 0.35, 15.5, 2.2, k=6)
        arch(pc, 1.0, 2.0, 3.0, -1.6, 'window')
        rect_win(pc, 6.0, 2.4, 3.0, -1.6)
        rect_win(pc, 10.0, 1.6, 2.4, -1.6)
    # ---- central tower
    tx0, tx1, ty0, ty1, TZ = -4.2, 4.2, -2.6, 6.0, 31.0
    boxl(tx0, tx1, ty0, ty1, 0, TZ)
    crenel(tx0, tx1, ty0, TZ, step=0.6)
    for z in (11.5, 19.0, 25.0):
        _add((tx0, ty0, z), (tx1, ty0, z), 'detail', (0, -1, 0))
    for cx in (-1.6, 0.0, 1.6):                                         # lancet windows, tiers
        arch(cx, 12.2, 1.0, 4.0, ty0, 'window')
        arch(cx, 19.8, 1.0, 3.2, ty0, 'window')
    arch(0, 25.8, 3.6, 2.4, ty0, 'window')                              # great belfry window
    _add((-0.6, ty0, 25.8), (-0.6, ty0, 29.3), 'window', (0, -1, 0))
    _add((0.6, ty0, 25.8), (0.6, ty0, 29.3), 'window', (0, -1, 0))
    for cx in (tx0, tx1):                                                # corner turrets + pinnacles
        for cy in (ty0, ty1):
            prism(cx, cy, 0.75, 0, TZ + 2.0)
            crenel(cx - 0.75, cx + 0.75, cy - 0.75, TZ + 2.0, step=0.38, hgt=0.35)
            spire(cx, cy, 0.75, TZ + 2.35, 3.8)
    for cx in (-2.1, 2.1):
        spire(cx, ty0, 0.3, TZ + 0.5, 2.2, k=4)
    # ---- porch + door
    boxl(-3.0, 3.0, -4.6, -2.6, 0, 7.5)
    crenel(-3.0, 3.0, -4.6, 7.5, step=0.5)
    arch(0, 0.0, 2.6, 2.6, -4.6, 'door')
    arch(0, 0.0, 2.1, 2.3, -4.6, 'door')
    for xx in (-3.0, 3.0):
        spire(xx, -4.6, 0.3, 7.5, 2.0, k=4)
    # ---- the AI's draw order: bottom-up, then centre-out, with a little noise
    rng = np.random.default_rng(5)
    out = []
    for p0, p1, kind, n in SEGS:
        mid = (p0 + p1) / 2
        o = 0.62 * (mid[2] / 38.0) + 0.38 * (abs(mid[0]) / 27.0) + rng.uniform(0, 0.05)
        out.append((p0, p1, kind, n, o))
    os_ = np.array([o for *_, o in out])
    os_ = (os_ - os_.min()) / (os_.max() - os_.min())
    return [(a, b, k, n, float(o)) for (a, b, k, n, _), o in zip(out, os_)]


def bricks(face='wing', s=1):
    """Brick courses for the 'every brick' sweep (front face of one wing)."""
    out = []
    x0, x1 = sorted((4.2 * s, 21.0 * s))
    z = 0.0
    row = 0
    while z < 11.4:
        out.append(((x0, -0.01, z), (x1, -0.01, z)))
        off = 0.0 if row % 2 == 0 else 0.45
        x = x0 + off
        while x < x1:
            out.append(((x, -0.01, z), (x, -0.01, min(11.5, z + 0.3))))
            x += 0.9
        z += 0.3
        row += 1
    return out


class Cam:
    def __init__(self, pos, look, fov=40.0, W=1080, H=1920, roll=0.0):
        self.pos = np.array(pos, np.float32)
        f = np.array(look, np.float32) - self.pos
        f /= np.linalg.norm(f)
        up = np.array((0, 0, 1), np.float32)
        r = np.cross(f, up)
        r /= np.linalg.norm(r)
        u = np.cross(r, f)
        if roll:
            c, s_ = math.cos(roll), math.sin(roll)
            r, u = r * c + u * s_, -r * s_ + u * c
        self.f, self.r, self.u = f, r, u
        self.W, self.H = W, H
        self.foc = (H / 2) / math.tan(math.radians(fov) / 2)

    def proj(self, P):
        P = np.asarray(P, np.float32)
        d = P - self.pos
        z = d @ self.f
        x = d @ self.r
        y = d @ self.u
        z = np.maximum(z, 0.05)
        return np.stack([self.W / 2 + self.foc * x / z, self.H / 2 - self.foc * y / z], -1), z


def visibility(cam, segs):
    """Fraction of each segment that is not hidden behind a solid box (3 samples per segment)."""
    P0 = np.array([s[0] for s in segs], np.float32)
    P1 = np.array([s[1] for s in segs], np.float32)
    B = np.array(OCC, np.float32)                                   # (nb, 6)
    lo = B[:, [0, 2, 4]]
    hi = B[:, [1, 3, 5]]
    vis = np.zeros(len(segs), np.float32)
    for u in (0.15, 0.5, 0.85):
        P = P0 + (P1 - P0) * u
        D = P - cam.pos                                             # ray from the camera, t in (0, 1) reaches P
        inv = 1.0 / np.where(np.abs(D) < 1e-6, 1e-6, D)
        t1 = (lo[None] - cam.pos[None, None]) * inv[:, None]
        t2 = (hi[None] - cam.pos[None, None]) * inv[:, None]
        tn = np.minimum(t1, t2).max(-1)
        tf = np.maximum(t1, t2).min(-1)
        hit = (tn <= tf) & (tn > 0) & (tn < 0.985)
        vis += (~hit.any(-1)).astype(np.float32) / 3
    return vis


def render_lines(cam, segs, t, W=1080, H=1920, ss=2, colour=(1, 1, 1), hi=None, hidden=0.12, width=2.2, trail=0.06):
    """Return (rgb, alpha) float32 images of the line model drawn up to progress `t` (0..1+).
    hi = {kind: (rgb, amount)} recolours/brightens some kinds (the voice's word highlights)."""
    ss = int(ss)
    lay = {}
    base = np.zeros((H * ss, W * ss), np.uint8)
    pts0 = np.array([s[0] for s in segs])
    pts1 = np.array([s[1] for s in segs])
    q0, z0 = cam.proj(pts0)
    q1, z1 = cam.proj(pts1)
    groups = {}
    VIS = visibility(cam, segs)
    for i, (p0, p1, kind, n, o) in enumerate(segs):
        if o > t:
            continue
        a = hidden + (1 - hidden) * (VIS[i] ** 2)
        if n is not None:
            mid = (p0 + p1) / 2
            if float(np.dot(n, cam.pos - mid)) <= 0:
                a = hidden
        if z0[i] < 0.2 or z1[i] < 0.2:
            continue
        frac = 1.0 if t - o > trail else max(0.0, (t - o) / trail)
        e = q0[i] + (q1[i] - q0[i]) * frac
        hot = t - o < trail * 1.5
        key = (kind, round(a, 2), hot)
        groups.setdefault(key, []).append(np.stack([q0[i], e]))
    rgb = np.zeros((H, W, 3), np.float32)
    alpha = np.zeros((H, W), np.float32)
    for (kind, a, hot), lines in groups.items():
        m = np.zeros((H * ss, W * ss), np.uint8)
        arr = (np.array(lines) * ss * 4).astype(np.int32)
        cv2.polylines(m, list(arr), False, 255, max(1, int(width * ss * (1.6 if hot else 1.0))), cv2.LINE_AA, shift=2)
        m = cv2.resize(m, (W, H), interpolation=cv2.INTER_AREA).astype(np.float32) / 255 * a
        col = np.array(colour, np.float32)
        if hi and kind in hi:
            hc, amt = hi[kind]
            col = col * (1 - amt) + np.array(hc, np.float32) * amt
        if hot:
            col = np.array((0.75, 1.0, 0.95), np.float32)
        rgb = rgb * (1 - m[..., None]) + col * m[..., None]
        alpha = np.maximum(alpha, m)
    return rgb, alpha


SEG_CACHE = None


def segs():
    global SEG_CACHE
    if SEG_CACHE is None:
        SEG_CACHE = build()
    return SEG_CACHE


if __name__ == '__main__':
    S = segs()
    print(len(S), 'lines')
    cam = Cam((-14, -58, 12), (0, 0, 15), fov=38)
    rgb, a = render_lines(cam, S, 1.2)
    g = cv2.GaussianBlur(rgb, (0, 0), 6) * 0.9
    img = np.clip(rgb + g, 0, 1)
    cv2.imwrite('/tmp/claude-0/-home-user-100/12e29207-ca18-56fe-8c40-721069807f57/scratchpad/bld.jpg', (img[..., ::-1] * 255).astype(np.uint8))
