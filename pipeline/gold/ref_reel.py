"""Reference-style cut of the gold reel (refs 1-3), rendered over the untouched color-graded video.

- captions in Inter Tight ExtraBold (the refs' tight grotesque): one word at a time at her chest, or a
  3D block that builds word by word beside her head; both motion-tracked to her head (RVM-matte track)
  and living in the same 3D space as the virtual camera, so they move with the shot like AE 3D layers
- spotlight cutaways with the gold 3D elements and the current word (ref 2), light-leak flashes
- hand-drawn gold tracking box around the face, "!!!" pops, ref-1 hook and chapter cards
- no regrade: the plate is the color-corrected render as delivered

  python3 ref_reel.py still 1.0,9.5            -> $GOLD_WORKDIR/stills/r_*.jpg
  python3 ref_reel.py range <f0> <f1> <out.mp4>
"""
import os, sys, math, json, functools, subprocess
import numpy as np
import cv2

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import gold_reel as G
import timeline as TL
import ref_timeline as RT
from gold_reel import (en, K, OW, OH, W, H, CX, CY, FPS, clamp, lerp, prog, e_out_expo, e_in_cubic, e_out_cubic,
                       e_out_back, e_inout_cubic, draw3d, draw, blur_sprite, solid, over_spr, pad, text_mask, rotm,
                       GOLD, GOLD3, WHITE)

# ---------------------------------------------------------------- configure the shared engine
G.COVER_ALL = True
G.TITLE_FONT, G.TITLE_TRACK = 'Anton-400', 0.0
G.PILL_FONT, G.NEON_FONT, G.BLOCK_FONT, G.BIG_STYLE = 'InterTight-800', 'Anton-400', 'InterTight-900', 'flat'
G.TL.BIG_TYPE[:] = RT.BIG_TYPE
G.TL.HOOK['flank'] = RT.HOOK_FLANK
G.TL.HOOK['block'] = (-9, -8, 'X', 0, 0, 0)          # no title block
G.TL.PILLS[:] = []
G.TL.METERS[:] = []
G.TL.INGOT_RAIN[:] = []
G.TL.ELEMENTS[:] = [e for e in G.TL.ELEMENTS if (e['name'], e['t0']) in RT.KEEP_ELEMENTS]
S = G.S
CAP_FONT = 'InterTight-800'
TRACK = np.array(json.load(open(S + '/work/head_track.json')), np.float32)
FACE = json.load(open(S + '/work/face_track.json'))     # OpenCV face boxes, smoothed (None where not found)
SMALL = {'ke', 'ki', 'ko', 'ne', 'se', 'me', 'ya', 'yeh', 'ye', 'ka', 'par', 'aur', 'hai', 'hain', 'tak', 'jo',
         'the', 'aa', 'ho', 'iss', 'jab', 'ek'}

# ---------------------------------------------------------------- plate (untouched color grade)


class Plate:
    def __init__(self):
        self.cache = {}

    def get(self, i):
        if i not in self.cache:
            f = cv2.imread(f'{S}/{G.FRAMES_DIR}/{i:05d}.jpg')[..., ::-1].astype(np.float32) / 255.0
            Hs, Ws = f.shape[:2]
            m = cv2.resize(cv2.imread(f'{S}/matte/{i:05d}.png', 0), (Ws, Hs), interpolation=cv2.INTER_LINEAR)
            m = m.astype(np.float32)[..., None] / 255.0
            one = np.ones((Hs, Ws, 1), np.float32)
            if len(self.cache) > 1:
                self.cache.pop(next(iter(self.cache)))
            self.cache[i] = dict(rgba=np.concatenate([f, one], 2), person=np.concatenate([f * m, m], 2))
        return self.cache[i]


PLATE = Plate()


def draw_plate(cv, i, cam, plates):
    for sh, xoff in plates:
        draw3d(cv, PLATE.get(G.hold_frame(i, sh))['rgba'], CX + xoff, CY, 0, w=W, h=H, cam=cam)


def draw_person(cv, i, cam, plates):
    for sh, xoff in plates:
        draw3d(cv, PLATE.get(G.hold_frame(i, sh))['person'], CX + xoff, CY, 0, w=W, h=H, cam=cam)

# ---------------------------------------------------------------- text sprites (ref look)


def _mask(text, size, font=CAP_FONT, track=-0.045):
    return text_mask(text, font, int(size * K), track)


@functools.lru_cache(maxsize=64)
def word_sprite(text, kind, size):
    """Caption word at output res: a stacked 3D depth shadow, a soft drop shadow, a tight dark edge for
    contrast on any background, then glow + face. kind: 'gold' (keyword) or 'white'."""
    a = np.pad(_mask(text, size), int(48 * K))
    dk = (0.0, 0.0, 0.0, 1.0)
    out = np.zeros(a.shape + (4,), np.float32)
    soft = cv2.GaussianBlur(G._shift(a, 3 * K, 9 * K), (0, 0), 9 * K)          # soft cast shadow
    out = over_spr(out, solid(soft * 0.85, dk))
    n = max(2, int(round(4 * K)))                                               # short extruded depth
    for j in range(n, 0, -1):
        out = over_spr(out, solid(G._shift(a, j * 0.45, j * 0.9) * 0.9, (0.04, 0.03, 0.02, 1)))
    edge = cv2.GaussianBlur(cv2.dilate(a, np.ones((3, 3), np.uint8), iterations=max(1, int(K))), (0, 0), 1.5 * K)
    out = over_spr(out, solid(edge * 0.75, dk))                                 # tight dark edge
    if kind == 'gold':
        g = cv2.GaussianBlur(a, (0, 0), 5 * K) * 0.65 + cv2.GaussianBlur(a, (0, 0), 18 * K) * 0.55
        out = over_spr(out, solid(np.clip(g, 0, 1), GOLD))
        top = np.linspace(1.04, 0.86, a.shape[0], dtype=np.float32)[:, None, None]
        face = np.concatenate([np.clip(GOLD3 * top, 0, 1) * a[..., None], a[..., None]], 2)
        return over_spr(out, face)
    g = cv2.GaussianBlur(a, (0, 0), 6 * K) * 0.22 + cv2.GaussianBlur(a, (0, 0), 20 * K) * 0.20
    out = over_spr(out, solid(np.clip(g, 0, 1), (1.0, 0.96, 0.88, 1)))
    return over_spr(out, solid(a, WHITE))


def glyph_box(text, size):
    """Design-px (width, cap height) of the bare glyphs."""
    m = _mask(text, size)
    return m.shape[1] / K, m.shape[0] / K

# ---------------------------------------------------------------- tracking helpers


def head_at(i):
    """Tracked head centre and size (design px): face detector where it found her, matte track otherwise."""
    i = int(clamp(i, 0, len(TRACK) - 1))
    f = FACE[i]
    if f is not None:
        return f[0], f[1] - f[3] * 0.1, f[3] * 1.55
    cx, cy, s = TRACK[i]
    return float(cx), float(cy), float(min(s, 330))


def face_box(i):
    f = FACE[int(clamp(i, 0, len(FACE) - 1))]
    if f is None:
        hx, hy, hs = head_at(i)
        return hx, hy, hs * 0.6, hs * 0.72
    return f[0], f[1], f[2] * 1.35, f[3] * 1.5


def plate_xoff(plates, shot):
    d = dict(plates)
    if shot in d:
        return d[shot]
    return d.get(max(d), 0.0) if len(d) == 1 else None   # phrase straddles a cut: ride the live shot


def word_kind(w):
    return 'gold' if w['gold'] else 'white'


def word_size(w, mode):
    if mode == 'word':
        return 112 if w['gold'] else 92
    if w['gold']:
        return 128
    return 64 if w['text'].lower().strip('?!.,') in SMALL else 86

# ---------------------------------------------------------------- 3D word blocks


@functools.lru_cache(maxsize=None)
def vmetrics(text, size):
    """(ink top, ink bottom) relative to the baseline and the font cap height, design px."""
    f = en.font(CAP_FONT, int(size * K))
    x0, y0, x1, y1 = f.getbbox(text, anchor='ls')
    cap = -f.getbbox('H', anchor='ls')[1]
    return y0 / K, y1 / K, cap / K


@functools.lru_cache(maxsize=None)
def block_layout(pi, k):
    """First k words of phrase pi laid out on true baselines with the refs' tight leading:
    [(word, x, top, w, h, line_width)] in design px, plus block width/height."""
    ph = G.phrases()[pi]
    lines, n = [], 0
    for row in ph['rows']:
        cur = []
        for w in row:
            if n >= k:
                break
            cur.append(w)
            n += 1
        if cur:
            lines.append(cur)
    items, widths, base, maxw, bottom = [], [], 0.0, 0.0, 0.0
    for li, row in enumerate(lines):
        cap = max(vmetrics(w['text'], word_size(w, 'block'))[2] for w in row)
        base += cap if li == 0 else cap * 1.20
        x = 0.0
        for j, w in enumerate(row):
            sz = word_size(w, 'block')
            gw, gh = glyph_box(w['text'], sz)
            top, bot, _ = vmetrics(w['text'], sz)
            items.append((w, x, base + top - 4 / K, gw, gh, li))
            bottom = max(bottom, base + bot)
            x += gw + sz * 0.16
        widths.append(x - word_size(row[-1], 'block') * 0.16)
        maxw = max(maxw, widths[-1])
    return [(w, x, yy, gw, gh, widths[li]) for (w, x, yy, gw, gh, li) in items], maxw, bottom


@functools.lru_cache(maxsize=None)
def block_plan(pi):
    """Where the block lives for this phrase, decided from the frame it appears in: beside the head on
    the roomier side (aligned toward her), or centred under her face when there's no room beside it."""
    ph = G.phrases()[pi]
    ta = ph['t_on'] + 0.3
    fi = int(round(ta * FPS))
    cam, _, v = G.camera(ta)
    hx, hy, hs = head_at(fi)
    zoom = cam.focal / (cam.focal - cam.z)
    scr = en.project_pts(np.array([[hx, hy, 0.0]]), cam)[0][0]
    side = -1 if scr[0] > 540 else 1
    gap = hs * 0.42 + 26
    avail = 1e9
    for tq in (ta, max(ta, ph['t_off'] - 0.1)):     # the camera may keep pushing in: fit at both ends
        cq, _, _ = G.camera(tq)
        hq = head_at(int(round(tq * FPS)))
        zq = cq.focal / (cq.focal - cq.z)
        sq = en.project_pts(np.array([[hq[0], hq[1], 0.0]]), cq)[0][0]
        eq = sq[0] + side * gap * zq
        avail = min(avail, ((1030 - eq) if side > 0 else (eq - 50)) / zq)
        zoom = max(zoom, zq)
    if avail >= 300 and hs <= 330:
        top = scr[1] - hs * 0.34 * zoom
        return dict(side=side, align='L' if side > 0 else 'R', dx=side * gap, dy=-hs * 0.34,
                    maxw=min(avail, 470), maxh=min((1660 - top) / zoom, 480))
    # under the face, centred on her
    top = scr[1] + hs * 0.55 * zoom
    return dict(side=1 if scr[0] < 540 else -1, align='C', dx=0.0, dy=hs * 0.55,
                maxw=min(980 / zoom, 600), maxh=min((1680 - top) / zoom, 420))


def draw_block(cv, t, i, ph, cam, plates):
    pi = ph['i']
    shot = G.shot_of(ph['t_on'] + 0.05)
    xoff = plate_xoff(plates, shot)
    if xoff is None:
        return
    words = [w for r in ph['rows'] for w in r]
    k = sum(1 for w in words if w['t'] - 0.03 <= t)
    if k == 0:
        return
    plan = block_plan(pi)
    side, align = plan['side'], plan['align']
    hx, hy, hs = head_at(i)
    lay, bw, bh = block_layout(pi, k)
    lay0, bw0, bh0 = block_layout(pi, max(k - 1, 1))
    t_new = words[k - 1]['t'] - 0.03
    blend = e_out_expo(clamp((t - t_new) / 0.18))
    maxw, maxh = plan['maxw'], plan['maxh']
    sc_new = min(1.0, maxw / max(bw, 1), maxh / max(bh, 1))
    sc_old = min(1.0, maxw / max(bw0, 1), maxh / max(bh0, 1)) if k > 1 else sc_new
    sc = lerp(sc_old, sc_new, blend)
    ax, ay = hx + plan['dx'], hy + plan['dy']          # tracked: rides on her head every frame
    out = clamp((t - (ph['t_off'] - 0.12)) / 0.12)
    ry, rx, rz = (-side * 27.0, 8.0, -side * 3.0) if align != 'C' else (-side * 14.0, 12.0, 0.0)
    R = rotm(rx, ry, rz)
    base = np.array([ax + xoff, ay, -60.0])
    shift = {'L': 0.0, 'R': 1.0, 'C': 0.5}[align]
    for n, (w, lx, ly, gw, gh, lw) in enumerate(lay):
        lx -= lw * shift                                  # align each line toward her (or centre it)
        if n < len(lay0) and k > 1:
            _, lx0, ly0, _, _, lw0 = lay0[n]
            lx, ly = lerp(lx0 - lw0 * shift, lx, blend), lerp(ly0, ly, blend)
        u = t - (w['t'] - 0.03)
        p = e_out_expo(clamp(u / 0.2))
        slam = 1 + 1.5 * (1 - p)
        local = np.array([(lx + gw / 2) * sc, (ly + gh / 2) * sc, 0.0])
        pos = base + R @ local
        pos[2] -= 420 * (1 - p)                           # flies in from near the lens
        spr = word_sprite(w['text'], word_kind(w), word_size(w, 'block'))
        bl = (1 - p) * 9 + out * 10
        s_ = blur_sprite(spr, bl * K) if bl > 0.6 else spr
        gm = _mask(w['text'], word_size(w, 'block')).shape[0]
        hdraw = s_.shape[0] / gm * gh * sc * slam * (1 + 0.2 * out)
        op = clamp(u / 0.05) * (1 - out)
        draw3d(cv, s_, pos[0], pos[1], pos[2], h=hdraw, rx=rx, ry=ry, rz=rz, cam=cam, opacity=op)

# ---------------------------------------------------------------- single words (tracked to the chest)


def current_word(ph, t):
    ws = [w for r in ph['rows'] for w in r]
    cur = None
    for w in ws:
        if w['t'] - 0.03 <= t:
            cur = w
    return cur


def draw_word(cv, t, i, ph, cam, plates, fixed=None):
    w = current_word(ph, t)
    if w is None:
        return
    u = t - (w['t'] - 0.03)
    out = clamp((t - (ph['t_off'] - 0.06)) / 0.06)
    spr = word_sprite(w['text'], word_kind(w), word_size(w, 'word'))
    gm = _mask(w['text'], word_size(w, 'word')).shape[0]
    gh = glyph_box(w['text'], word_size(w, 'word'))[1]
    p = e_out_back(clamp(u / 0.12), 2.2)
    sc = lerp(1.25, 1.0, clamp(u / 0.12)) if u < 0.12 else 1.0
    op = 1.0 - out
    if fixed is not None:                      # cutaways / chapter cards: centred, screen-fixed
        draw3d(cv, spr, fixed[0], fixed[1], 0, h=spr.shape[0] / gm * gh * sc, cam=en.Cam(), opacity=op)
        return
    shot = G.shot_of(ph['t_on'] + 0.05)
    xoff = plate_xoff(plates, shot)
    if xoff is None:
        return
    hx, hy, hs = head_at(i)
    y = hy + hs * (1.2 if hs < 330 else 0.95)
    x = clamp(hx, 300, 780)
    draw3d(cv, spr, x + xoff, y, -40, h=spr.shape[0] / gm * gh * sc, ry=-4, cam=cam, opacity=op)


def draw_captions(cv, t, i, cam, plates, card_k=0.0, insert=False, tc=None):
    tc = t if tc is None else tc
    for ph in G.phrases():
        if not (ph['t_on'] <= tc < ph['t_off']):
            continue
        if insert:
            draw_word(cv, tc, i, ph, cam, plates, fixed=(540, 1530))
        elif card_k > 0.5:
            draw_word(cv, tc, i, ph, cam, plates, fixed=(540, 1560))
        elif ph['i'] in RT.BLOCKS:
            draw_block(cv, t, i, ph, cam, plates)
        else:
            draw_word(cv, tc, i, ph, cam, plates)

# ---------------------------------------------------------------- tracking box, "!!!", light leaks


def _jit(seed, amp):
    r = np.random.default_rng(seed)
    return r.uniform(-amp, amp, 2)


def draw_box(cv, t, i, cam, plates):
    for t_in, t_out in RT.BOXES:
        if not (t_in <= t < t_out):
            continue
        shot = G.shot_of(t)
        xoff = plate_xoff(plates, shot) or 0.0
        hx, hy, bw, bh = face_box(i)
        x0, y0, x1, y1 = hx - bw / 2 + xoff, hy - bh / 2, hx + bw / 2 + xoff, hy + bh / 2
        boil = int(t * 12)
        ov = 0.16
        segs = [((x0 - bw * ov, y0), (x1 + bw * ov * 0.6, y0)), ((x1, y0 - bh * ov), (x1, y1 + bh * ov * 0.7)),
                ((x1 + bw * ov, y1), (x0 - bw * ov * 0.5, y1)), ((x0, y1 + bh * ov), (x0, y0 - bh * ov * 0.8))]
        u = t - t_in
        out = clamp((t - (t_out - 0.15)) / 0.15)
        pts = []
        for j, (a, b) in enumerate(segs):
            p = e_out_cubic(clamp((u - j * 0.05) / 0.16))
            if p <= 0:
                continue
            ja, jb = _jit(boil * 7 + j, 5), _jit(boil * 7 + j + 50, 5)
            a2 = np.array(a) + ja
            b2 = np.array(a) + (np.array(b) - np.array(a)) * p + jb
            pts.append((a2, b2))
        if not pts:
            continue
        world = np.array([[x, y, -50.0] for seg in pts for x, y in seg])
        scr, ok = en.project_pts(world, cam)
        if not ok:
            continue
        scr = scr * K
        m = int(40 * K)
        bx0, by0 = int(scr[:, 0].min()) - m, int(scr[:, 1].min()) - m
        bx1, by1 = int(scr[:, 0].max()) + m, int(scr[:, 1].max()) + m
        mask = np.zeros((by1 - by0, bx1 - bx0), np.float32)
        for j in range(0, len(scr), 2):
            p0 = tuple(np.round((scr[j] - [bx0, by0]) * 4).astype(int))
            p1 = tuple(np.round((scr[j + 1] - [bx0, by0]) * 4).astype(int))
            cv2.line(mask, p0, p1, 1.0, int(6 * K), cv2.LINE_AA, shift=2)
        glow = cv2.GaussianBlur(mask, (0, 0), 8 * K)
        a = np.clip(mask + glow * 0.6, 0, 1) * (1 - out)
        rgb = (mask[..., None] * GOLD3 + glow[..., None] * GOLD3 * 0.8) * (1 - out)
        en.composite(cv, np.concatenate([rgb, a[..., None]], 2).astype(np.float32), bx0, by0, 1.0, 'over')


@functools.lru_cache(maxsize=None)
def bang_sprite():
    return word_sprite('!', 'gold', 170)


def draw_bangs(cv, t, i, cam, plates):
    for t_in, t_out in RT.BANGS:
        if not (t_in <= t < t_out):
            continue
        xoff = plate_xoff(plates, G.shot_of(t)) or 0.0
        hx, hy, hs = head_at(i)
        out = clamp((t - (t_out - 0.12)) / 0.12)
        spr = bang_sprite()
        gm = _mask('!', 170).shape[0]
        bx, by = (hx + xoff, hy - hs * 0.78) if hs <= 330 else (hx + xoff + hs * 0.62, hy - hs * 0.28)
        for j, (dx, dy, rot, s_) in enumerate([(-0.42, -0.02, -16, 0.8), (0.0, -0.12, 0, 1.0), (0.42, -0.02, 16, 0.8)]):
            u = t - t_in - j * 0.07
            if u < 0:
                continue
            p = clamp(u / 0.22)
            sc = e_out_back(p, 3.0) * s_
            wig = 6 * math.sin(u * 18) * math.exp(-u * 4)
            hgt = spr.shape[0] / gm * min(hs, 300) * 0.42 * sc
            draw3d(cv, spr, bx + dx * min(hs, 300), by + dy * hs, -60, h=hgt, rz=rot + wig, cam=cam,
                   opacity=(1 - out) * clamp(u / 0.04))


@functools.lru_cache(maxsize=None)
def leak_sprite(c):
    n = int(900 * K)
    ys, xs = np.mgrid[0:n, 0:n].astype(np.float32)
    r = np.sqrt((xs - n / 2) ** 2 + (ys - n / 2) ** 2) / (n / 2)
    a = np.clip(1 - r, 0, 1) ** 1.8
    col = np.array(c, np.float32)
    return np.concatenate([a[..., None] * col, a[..., None]], 2)


def leak_events():
    ev = [TL.CUT_T[k] for k in range(1, len(TL.CUT_T))]
    for t_in, t_out, *_ in RT.INSERTS:
        ev += [t_in, t_out]
    return ev


def draw_leaks(cv, t):
    for k, tc in enumerate(leak_events()):
        x = t - tc
        if -0.12 <= x < 0.30:
            a = math.exp(-abs(x) * (16 if x < 0 else 9))
            d = 1 if k % 2 else -1
            sweep = (x + 0.12) / 0.42
            draw(cv, leak_sprite((1.0, 0.50, 0.12)), CX + d * (-700 + 1400 * sweep), CY - 300, 2.4, 0, 0.9 * a, 'add')
            draw(cv, leak_sprite((1.0, 0.78, 0.40)), CX - d * (-500 + 1000 * sweep), CY + 420, 1.8, 0, 0.7 * a, 'add')
            draw(cv, leak_sprite((1.0, 0.95, 0.85)), CX, CY, 3.0, 0, 0.35 * a * a, 'add')

# ---------------------------------------------------------------- spotlight cutaways


@functools.lru_cache(maxsize=None)
def spot_sprite():
    n = int(1300 * K)
    ys, xs = np.mgrid[0:n, 0:n].astype(np.float32)
    r = np.sqrt((xs - n / 2) ** 2 + (ys - n / 2) ** 2) / (n / 2)
    disc = np.clip((1 - r) / 0.10, 0, 1)
    core = 0.55 + 0.45 * np.clip(1 - r, 0, 1) ** 0.8
    a = disc * core
    col = np.array([1.0, 0.86, 0.62], np.float32)
    return np.concatenate([a[..., None] * col, a[..., None]], 2)


def insert_at(t):
    for ins in RT.INSERTS:
        if ins[0] <= t < ins[1]:
            return ins
    return None


def render_insert(fi, t, ins, n):
    t_in, t_out, name, kind = ins
    acc = np.zeros((OH, OW, 3), np.float32)
    for j in range(n):
        ts = t + ((j + 0.5) / n - 0.5) * 0.5 / FPS if n > 1 else t
        u = ts - t_in
        cv = np.zeros((OH, OW, 3), np.float32)
        cam = en.Cam(z=G.FOCAL * (1 - 1 / (1.0 + 0.05 * u)), rz=1.2 * math.sin(u * 2))
        # dark room + spotlight disc behind the object (ref 2 cutaways)
        draw3d(cv, spot_sprite(), CX, 820, 200, h=1180, cam=cam, opacity=0.95)
        draw3d(cv, G.glow_spr(), CX, 820, 210, h=2200, cam=cam, opacity=0.35, mode='add')
        s3 = G.seq(name) if kind == 'seq' else None
        if s3 is not None and s3.n():
            if name in ('arrow_crash', 'arrow_up', 'candles3d'):
                fi3 = min(int(u * 30) + (14 if name == 'candles3d' else 10), s3.n() - 1)
            else:
                fi3 = int(u * 24) % s3.n()
            fr = s3.frame(fi3)
            sh = solid(cv2.GaussianBlur(fr[..., 3], (0, 0), 18 * K) * 0.6, (0, 0, 0, 1))
            p = e_out_expo(clamp(u / 0.3))
            hgt = (560 if name in ('arrow_crash', 'arrow_up', 'candles3d') else 780) * lerp(1.25, 1.0, p)
            draw3d(cv, sh, CX + 24, 860, 20, h=hgt * 1.05, cam=cam)
            draw3d(cv, fr, CX, 820, 0, h=hgt, ry=8 * math.sin(u * 1.5), cam=cam)
        draw_captions(cv, ts, fi, cam, [], insert=True, tc=t)
        acc += cv
    return acc / n

# ---------------------------------------------------------------- frame


def draw_back(cv, t, cam, plates):
    G._hook(cv, t, cam, 'back')
    G._big_types(cv, t, cam)
    for el in G.elements():
        if el.e['layer'] == 'back' and el.active(t):
            xo = plate_xoff(plates, el.shot)
            if xo is not None:
                el.draw(cv, t, cam, xo)


def back_active(t):
    if t < 3.6:
        return True
    if any(b[0] <= t < b[1] for b in RT.BIG_TYPE):
        return True
    return any(e['layer'] == 'back' and e['t0'] <= t < e['t1'] for e in G.TL.ELEMENTS)


def draw_front(cv, t, cam, plates):
    for el in G.elements():
        if el.e['layer'] == 'front' and el.active(t):
            xo = plate_xoff(plates, el.shot)
            if xo is not None:
                el.draw(cv, t, cam, xo)
    G._hook(cv, t, cam, 'front')


def draw_overlay(cv, t, i, cam, plates, card_k, tc=None):
    draw_box(cv, t, i, cam, plates)
    draw_bangs(cv, t, i, cam, plates)
    draw_captions(cv, t, i, cam, plates, card_k=card_k, tc=tc)


def nsub_at(t):
    n = G.nsub_at(t)
    for ph in G.phrases():
        if ph['t_on'] <= t < ph['t_off'] + 0.05:
            for w in (w for r in ph['rows'] for w in r):
                if -0.05 <= t - w['t'] < 0.22 and ph['i'] in RT.BLOCKS:
                    return max(n, 5)
    return n


def render_frame(fi):
    t = fi / FPS
    en._mips.clear()
    ins = insert_at(t)
    if ins:
        cv = render_insert(fi, t, ins, 3)
    else:
        n = nsub_at(t)
        shutter = 0.55 / FPS
        if n > 1 and not G.camera_fast(t):
            cv = _layered(fi, t, n, shutter)
        else:
            cv = _full(fi, t, n, shutter)
    return _finish(cv, fi, t)


def _layered(fi, t, n, shutter):
    cam, plates, v = G.camera(t)
    cv = np.zeros((OH, OW, 3), np.float32)
    draw_plate(cv, fi, cam, plates)
    back, front, over = G.layer('back'), G.layer('front'), G.layer('over')
    s_, k, u = G.section_k(t)
    for j in range(n):
        ts = t + ((j + 0.5) / n - 0.5) * shutter
        cj, pj, vj = G.camera(ts)
        if back_active(t):
            back.sample(lambda c: draw_back(c, ts, cj, pj))
        front.sample(lambda c: draw_front(c, ts, cj, pj))
        over.sample(lambda c: draw_overlay(c, ts, fi, cj, pj, k, tc=t))
    if back_active(t):
        back.over(cv, n)
        draw_person(cv, fi, cam, plates)
    front.over(cv, n)
    if s_ is not None and k > 0.001:
        cv = G.render_section(cv, t, s_, k, u)
    over.over(cv, n)
    return cv


def _full(fi, t, n, shutter):
    acc = np.zeros((OH, OW, 3), np.float32)
    for j in range(n):
        ts = t + ((j + 0.5) / n - 0.5) * shutter if n > 1 else t
        if G.shot_of(ts) != G.shot_of(t) and not G.transition_state(t):
            ts = t
        cam, plates, v = G.camera(ts)
        cv = np.zeros((OH, OW, 3), np.float32)
        draw_plate(cv, fi, cam, plates)
        if back_active(t):
            draw_back(cv, ts, cam, plates)
            draw_person(cv, fi, cam, plates)
        draw_front(cv, ts, cam, plates)
        s_, k, u = G.section_k(ts)
        if s_ is not None and k > 0.001:
            cv = G.render_section(cv, ts, s_, k, u)
        draw_overlay(cv, ts, fi, cam, plates, k, tc=t)
        acc += cv
    return acc / n


def _finish(cv, fi, t):
    flash, ca = 0.0, 0.0
    tr = G.transition_state(t)
    if tr:
        kind, d, k, tc, pre, post_ = tr
        x = abs(t - tc)
        flash = 0.22 * math.exp(-x * 14)
        ca = 5 * math.exp(-x * 10)
    s_, k, u = G.section_k(t)
    if s_ is not None and 0.0 < u < 0.25:
        flash = max(flash, 0.18 * (1 - u / 0.25))
    draw_leaks(cv, t)
    if flash > 0:
        cv += np.array([1.0, 0.8, 0.5], np.float32) * flash
    if ca > 0.05:
        kk = int(round(ca * K))
        cv = np.stack([np.roll(cv[..., 0], kk, axis=1), cv[..., 1], np.roll(cv[..., 2], -kk, axis=1)], 2)
    fade = clamp((t - 78.9) / 0.5)
    if fade > 0:
        cv *= 1 - fade
    return (np.clip(cv, 0, 1) * 255 + 0.5).astype(np.uint8)


def sfx_cues():
    out = []
    for k, (kind, d) in TL.TRANSITIONS.items():
        tc = TL.CUT_T[k]
        out += [(tc - 0.28, 'whoosh_big' if kind != 'zoom' else 'whoosh_zoom', 0.9), (tc, 'hit_soft', 0.5)]
    for sc in TL.SECTIONS:
        out += [(sc['t_in'] - 0.5, 'riser', 0.35), (sc['t_in'] + 0.35, 'impact', 0.8),
                (sc['t_in'] + 0.55, 'shimmer', 0.35), (sc['t_out'] - 0.2, 'whoosh', 0.55)]
    for t_in, t_out, *_ in RT.INSERTS:
        out += [(t_in - 0.06, 'swish', 0.55), (t_in, 'hit_soft', 0.45), (t_out - 0.06, 'swish', 0.45)]
    for t_in, t_out in RT.BANGS:
        out += [(t_in + j * 0.07, 'pop', 0.5) for j in range(3)]
    for t_in, t_out in RT.BOXES:
        out += [(t_in, 'click', 0.4), (t_in + 0.02, 'tick_run', 0.22)]
    for ph in G.phrases():
        if ph['i'] in RT.BLOCKS:
            for w in (w for r in ph['rows'] for w in r):
                if w['gold']:
                    out.append((w['t'] - 0.06, 'swish', 0.28))
    for b in RT.BIG_TYPE:
        out.append((b[0], 'impact', 0.6))
    for fl in RT.HOOK_FLANK:
        out.append((fl[1] - 0.08, 'whoosh', 0.55))
    for tp, kick, amp in TL.PUNCH:
        if amp >= 12:
            out.append((tp, 'boom', 0.55))
    for k in range(1, len(TL.CAM)):
        if TL.CAM[k][7] and abs(TL.CAM[k][0] - TL.CAM[k - 1][0]) < 0.2:
            out.append((TL.CAM[k][0] - 0.06, 'swish', 0.3))
    out += [(0.0, 'boom', 0.8), (0.0, 'shimmer', 0.4), (47.9, 'riser_long', 0.35), (51.42, 'boom', 0.6),
            (77.0, 'shimmer', 0.35)]
    return sorted(out)


def main():
    cmd = sys.argv[1]
    if cmd == 'sfx':
        json.dump(sfx_cues(), open(S + '/work/ref_sfx.json', 'w'))
        print('cues', len(sfx_cues()))
        return
    if cmd == 'still':
        os.makedirs(S + '/stills', exist_ok=True)
        for ts in sys.argv[2].split(','):
            fi = int(round(float(ts) * FPS))
            cv2.imwrite(f'{S}/stills/r_{float(ts):06.2f}.jpg', render_frame(fi)[..., ::-1], [cv2.IMWRITE_JPEG_QUALITY, 92])
            print('still', ts, flush=True)
    elif cmd == 'range':
        f0, f1, out = int(sys.argv[2]), int(sys.argv[3]), sys.argv[4]
        p = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24',
                              '-s', f'{OW}x{OH}', '-r', '30000/1001', '-i', '-', '-c:v', 'libx264', '-preset', 'faster',
                              '-crf', '11', '-pix_fmt', 'yuv420p', out], stdin=subprocess.PIPE)
        for fi in range(f0, f1):
            p.stdin.write(render_frame(fi).tobytes())
            if fi % 20 == 0:
                print('frame', fi, flush=True)
        p.stdin.close()
        p.wait()


if __name__ == '__main__':
    main()
