"""BMHC "AI can recreate this building. But not what happens inside." 9:16, ~33 s, deep low-key film look.

0  AI hook: a prompt types itself; BMHC's façade draws in glowing lines while the camera spirals up (spiral);
   explainer call-outs + 3D window / bricks / pinnacle on "Every window. Every brick. Every detail."
1  "But it can't recreate what happens inside": push into the drawn door, eclipse, layercut onto real life.
2  Real BMHC moments, each line with its 3D object: friendships (tea glasses), knowledge (book), confidence (target),
   conversations (Salaam / Hello). Four-bar wipe.
3  Heritage: the tower stone as archive film (retro) + astrolabe under glass -> it comes alive: aurora + lantern.
4  The real building at night, its windows lighting up one by one: "A living community."
5  End card on ink: BMHC's own logo + four bars, "Come and experience it.", bmhc.org.uk.

Usage: python3 reel_ai.py still 1.0,5.0 | range a b | times
"""
import os, sys, json, math, re
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import numpy as np
import cv2
import frames_ai as G
from frames_ai import (W, H, S, ROOT, INK, WHITE, MAG, TEAL, ORANGE, LIME, HOLO, BARS, canvas, load, cover, deep, grain, pop, caption,
                       prompt_bar, callout, glow_lines, blueprint_bg, eclipse, layercut, four_bar_wipe, retro, aurora, logo, paste,
                       tag, text_sprite, rrect, prog, clamp, e_out, e_inout, e_back, Clip, window_lights)
import building as BL

FPS = 30
INFO = json.load(open(f'{S}/tts/info.json'))
OFF = 0.75
WORDS = [(w, a + OFF, b + OFF) for w, a, b in INFO['words']]


def norm(w):
    return re.sub(r"[^a-z']", '', w.lower().replace('’', "'"))


def A(word, k=0, end=False):
    """Start (or end) time of the k-th occurrence of `word` in the voice."""
    n = 0
    for w, a, b in WORDS:
        if norm(w) == norm(word):
            if n == k:
                return b if end else a
            n += 1
    raise KeyError(word)


T_SECONDS, T_WINDOW, T_BRICK, T_DETAIL = A('seconds'), A('window'), A('brick'), A('detail')
T_BUT, T_INSIDE = A('but'), A('inside')
T_LC0 = A('inside', end=True) + 0.05                      # layercut opens
T_LC1 = T_LC0 + 0.75
T_FRIEND, T_KNOW, T_YOUNG, T_CONF = A('friendships'), A('knowledge'), A('young'), A('confidence')
T_CONV, T_TOG = A('conversations'), A('together')
T_BEC, T_HER, T_PRES = A('because'), A('heritage'), A('preserve')
T_ITS, T_KEEP, T_ALIVE = A("it's"), A('keep'), A('alive')
T_BRIT, T_LIVING = A('british'), A('living')
T_COME, T_EXP = A('come'), A('experience')
T_LAST = WORDS[-1][2]
DUR = round(T_LAST + 2.4, 2)
NF = int(DUR * FPS)

# cut points
C_FRIEND = T_FRIEND - 0.42 if T_FRIEND - 0.42 > T_LC1 + 0.3 else T_LC1 + 0.3
C_KNOW = T_KNOW - 0.3
C_YOUNG = T_YOUNG - 0.25
C_CONV = T_CONV - 0.3
W_HER0 = T_BEC - 0.45                                       # four-bar wipe into heritage
C_HER = W_HER0 + 0.35
X_ALIVE0, X_ALIVE1 = T_ITS - 0.35, T_ITS + 0.45             # retro -> alive
C_BRIT = T_BRIT - 0.2
W_END0 = T_COME - 0.5                                       # four-bar wipe to the end card
C_END = W_END0 + 0.35

SEG = BL.segs()
DL = f'{S}/dl'
VID = f'{DL}/bmhc-new.mp4'
CLIPS = {}


def clip(name):
    if name not in CLIPS:
        CLIPS[name] = Clip(VID)
    return CLIPS[name]


# ------------------------------------------------------------------ AI section
def catmull(keys, t):
    """Catmull-Rom through (time, vector) keys, clamped at the ends, eased in time."""
    ts = [k[0] for k in keys]
    if t <= ts[0]:
        return np.array(keys[0][1], np.float32)
    if t >= ts[-1]:
        return np.array(keys[-1][1], np.float32)
    i = max(j for j in range(len(ts) - 1) if ts[j] <= t)
    u = (t - ts[i]) / (ts[i + 1] - ts[i])
    u = u * u * (3 - 2 * u) * 0.6 + u * 0.4
    P = [np.array(keys[max(0, min(len(keys) - 1, j))][1], np.float32) for j in (i - 1, i, i + 1, i + 2)]
    return 0.5 * ((2 * P[1]) + (-P[0] + P[2]) * u + (2 * P[0] - 5 * P[1] + 4 * P[2] - P[3]) * u * u +
                  (-P[0] + 3 * P[1] - 3 * P[2] + P[3]) * u ** 3)


CAM_KEYS = [  # time, (pos xyz, look xyz, fov)
    (0.0, (-58, -64, 1.5, 0, 0, 9, 38)),
    (1.7, (-34, -72, 6, 0, 0, 11, 38)),
    (T_SECONDS + 0.4, (10, -66, 15, 0, 0, 13, 38)),
    (T_WINDOW + 0.05, (27, -25, 8.5, 13, 0, 7.5, 40)),
    (T_BRICK + 0.05, (-30, -23, 4.5, -13, 0, 6, 42)),
    (T_DETAIL + 0.05, (-7, -24, 21, 0, -1, 32, 44)),
    (T_BUT + 0.1, (0, -26, 3.2, 0, 0, 5, 46)),
    (T_INSIDE + 0.15, (0, -11.0, 2.0, 0, -4.6, 2.3, 52)),
    (T_LC1, (0, -8.0, 1.9, 0, -4.6, 2.3, 56)),
]


def cam_at(t):
    v = catmull(CAM_KEYS, t)
    return BL.Cam(v[:3], v[3:6], fov=float(v[6]))


def proj(cam, p):
    q, z = cam.proj(np.array([p], np.float32))
    return float(q[0, 0]), float(q[0, 1])


def build_progress(t):
    return 1.04 * e_out(prog(t, 0.3, T_SECONDS + 0.5))


def bricks_overlay(c, cam, t):
    u = prog(t, T_BRICK - 0.1, T_BRICK + 0.9)
    if u <= 0 or t > T_DETAIL + 0.1:
        return c
    lay = np.zeros((H, W), np.uint8)
    for p0, p1 in BL.bricks(s=-1):
        q, z = cam.proj(np.array([p0, p1], np.float32))
        if (z > 0.3).all():
            cv2.line(lay, tuple((q[0] * 4).astype(int)), tuple((q[1] * 4).astype(int)), 255, 4, cv2.LINE_AA, shift=2)
    m = lay.astype(np.float32) / 255
    # scan band climbing the wall (in world height -> approximate with screen y of the wall)
    ytop, ybot = proj(cam, (-12, 0, 11.5))[1], proj(cam, (-12, 0, 0))[1]
    yy = G._grid()[0]
    ys = ybot + (ytop - ybot) * u
    band = np.clip(1 - np.abs(yy - ys) / 160, 0, 1) + np.clip((yy - ys) / 400, 0, 1) * 0.35 * (yy < ybot)
    fade = 1 - prog(t, T_DETAIL - 0.15, T_DETAIL + 0.1)
    m = (m * band * fade)[..., None]
    return c * (1 - m) + MAG * m * 1.2


def ai_frame(t):
    c = blueprint_bg(t, 1.0)
    cam = cam_at(t)
    hi = {}
    if T_WINDOW - 0.1 < t < T_BRICK + 0.2:
        hi['window'] = (MAG, 0.9 * clamp((t - T_WINDOW + 0.1) / 0.15) * (1 - prog(t, T_BRICK - 0.05, T_BRICK + 0.2)))
    if T_DETAIL - 0.1 < t < T_BUT + 0.2:
        hi['detail'] = (TEAL, 0.9 * clamp((t - T_DETAIL + 0.1) / 0.15) * (1 - prog(t, T_BUT - 0.1, T_BUT + 0.2)))
    if t > T_BUT - 0.1:
        hi['door'] = ((1.0, 0.8, 0.5), clamp((t - T_BUT + 0.1) / 0.4))
    dim = 1 - 0.55 * prog(t, T_BUT, T_INSIDE)                  # everything but the door falls away
    rgb, a = BL.render_lines(cam, SEG, build_progress(t), hi=hi, colour=HOLO * dim, width=2.0 if t < T_BUT else 2.6)
    rgb, a = glow_lines(rgb, a, 0.8)
    c = np.clip(c * (1 - a[..., None]) + rgb, 0, 1)
    c = bricks_overlay(c, cam, t)
    # door light, then the eclipse
    if t > T_BUT - 0.1:
        dx, dy = proj(cam, (0, -4.6, 1.7))
        k = prog(t, T_BUT, T_INSIDE)
        r = 120 + 260 * e_inout(k)
        if t > T_INSIDE - 0.35:
            c = eclipse(c, dx, dy, r, prog(t, T_INSIDE - 0.35, T_INSIDE + 0.3))
        else:
            yy, xx = G._grid()
            g = np.exp(-((xx - dx) ** 2 + (yy - dy) ** 2) / (2 * (r * 0.8) ** 2)) * 0.35 * k
            c = np.clip(c + g[..., None] * np.array((1.0, 0.75, 0.42), np.float32), 0, 1)
    # explainer call-outs
    if T_WINDOW - 0.1 < t < T_BRICK + 0.1:
        callout(c, proj(cam, (12.6, 0, 9.4)), '79 WINDOWS', t - T_WINDOW, side=-1, dy=-300)
    if T_BRICK - 0.1 < t < T_DETAIL + 0.1:
        n = int(212480 * e_out(prog(t, T_BRICK, T_BRICK + 0.7)))
        callout(c, proj(cam, (-9, 0, 9.5)), f'{n:,} BRICKS', t - T_BRICK, side=1, dy=-330)
    if T_DETAIL - 0.1 < t < T_BUT + 0.1:
        callout(c, proj(cam, (-4.2, -2.6, 35.5)), 'EVERY DETAIL', t - T_DETAIL, side=1, dy=140, col=TEAL)
    # 3D pops (each leaves as the next arrives)
    for name, t0, t1, x, y, size, glow in (('window', T_WINDOW, T_BRICK - 0.05, 300, 760, 400, (1, 0.7, 0.4)),
                                          ('brick', T_BRICK, T_DETAIL - 0.05, 760, 1130, 430, None),
                                          ('pinnacle', T_DETAIL, T_BUT, 300, 1060, 470, None)):
        if t0 - 0.05 < t < t1 + 0.3:
            out = 1 - prog(t, t1, t1 + 0.25)
            if out > 0:
                cc = c.copy()
                pop(cc, name, x, y, size * (0.6 + 0.4 * out), t - t0, glow=None if glow is None else np.array(glow, np.float32))
                c = c * (1 - out) + cc * out
    # the prompt + status
    if t < T_WINDOW + 0.2:
        a = 1 - prog(t, T_WINDOW - 0.35, T_WINDOW + 0.1)
        dy = -80 * e_inout(prog(t, T_WINDOW - 0.35, T_WINDOW + 0.1))
        q = 'Recreate this historic Manchester building.'
        n = int(len(q) * prog(t, 0.08, 1.05))
        p = build_progress(t)
        st = 'GENERATING  ·  ' + (f'{min(100, int(p * 100))}%' if p < 1 else 'DONE IN 2.6 s')
        prompt_bar(c, q[:n], y=300 + dy, t=t, status=st if t > 0.6 else None, a=a)
    if t < 1.0:
        tag(c, 'STORIES', 64, 150, WHITE, INK, a=1 - prog(t, 0.8, 1.0))
    if 1.15 < t < T_WINDOW:
        u = t - 1.15
        a = 1 - prog(t, T_WINDOW - 0.4, T_WINDOW - 0.1)
        s1 = text_sprite('AI CAN', 800, 88, WHITE, track=0.02)
        s2 = text_sprite('RECREATE THIS.', 800, 88, MAG, track=0.02)
        k = e_out(clamp(u / 0.4))
        sh = np.zeros((H, W), np.float32)                     # an ink shadow so the headline reads over the lines
        cv2.rectangle(sh, (90, 450), (W - 90, 680), 1.0, -1)
        sh = cv2.GaussianBlur(sh, (0, 0), 40)[..., None] * 0.85 * a * k
        c[:] = c * (1 - sh) + INK * sh
        paste(c, s1, W / 2, 520 + 30 * (1 - k), a * k)
        paste(c, s2, W / 2, 615 + 30 * (1 - k), a * clamp((u - 0.15) / 0.3))
    return c


# ------------------------------------------------------------------ real life
def scene_iftar(t):
    if t < C_FRIEND:                                            # the welcome: a smiling volunteer
        f = clip('scout').at(11.05 + (t - T_LC0) * 0.8)
        c = cover(f, fx=0.64, fy=0.42, z=1.05 + 0.04 * prog(t, T_LC0, C_FRIEND))
        return deep(c, exp=0.66, haze=1.0, t=t, seed=11, pool=(0.55, 0.36, 0.5))
    f = clip('iftar').at(16.85 + (t - C_FRIEND) * 0.9)
    c = cover(f, fx=0.6, fy=0.45, z=1.15 + 0.05 * prog(t, C_FRIEND, C_KNOW))
    c = deep(c, exp=0.68, haze=1.0, t=t, seed=12, pool=(0.42, 0.32, 0.55))
    pop(c, 'chai', 770, 1080, 360, t - T_FRIEND - 0.1)
    return c


def scene_know(t):
    u = prog(t, C_KNOW, C_YOUNG)
    c = cover(load(f'{DL}/487090267_1088144326686714_8941517225088640181_n.jpg'), fx=0.42 + 0.03 * u, fy=0.58, z=1.08 + 0.1 * u)
    c = deep(c, exp=0.62, haze=1.0, t=t, seed=13, pool=(0.55, 0.62, 0.5))
    pop(c, 'book', 330, 1080, 420, t - T_KNOW)
    return c


def scene_young(t):
    f = clip('hall').at(12.25 + (t - C_YOUNG) * 0.6)
    c = cover(f, fx=0.45, fy=0.38, z=1.05 + 0.06 * prog(t, C_YOUNG, C_CONV))
    c = deep(c, exp=0.64, haze=1.4, t=t, seed=14, pool=(0.62, 0.3, 0.55))
    hit = t - (T_CONF + 0.12)
    sh = 10 * math.exp(-max(0, hit) * 9) * math.sin(hit * 60) if hit > 0 else 0
    pop(c, 'target', 760 + sh, 1060, 380 + (30 * math.exp(-hit * 6) if hit > 0 else 0), t - T_YOUNG - 0.15)
    if 0 < hit < 0.35:                                          # the 'thunk' flash
        yy, xx = G._grid()
        g = np.exp(-((xx - 760) ** 2 + (yy - 1060) ** 2) / (2 * 140 ** 2)) * (1 - hit / 0.35) * 0.6
        c = np.clip(c + g[..., None] * np.array((1.0, 0.9, 0.7), np.float32), 0, 1)
    return c


def scene_conv(t):
    f = clip('expo').at(27.15 + (t - C_CONV) * 0.8)
    c = cover(f, fx=0.36, fy=0.42, z=1.06 + 0.05 * prog(t, C_CONV, W_HER0))
    c = deep(c, exp=0.66, haze=1.0, t=t, seed=15, pool=(0.66, 0.3, 0.5))
    bump = math.exp(-max(0, t - T_TOG) * 7) * (t > T_TOG)
    pop(c, 'bubbles', 540, 1060, 500 * (1 + 0.12 * bump), t - T_CONV - 0.05)
    return c


def scene_heritage(t):
    f = clip('tower').at(14.6 + (t - C_HER) * 0.6)
    c = cover(f, fx=0.56, fy=0.5, z=1.12 + 0.05 * prog(t, C_HER, X_ALIVE1))
    c = deep(c, exp=0.58, hal=0.25, t=t, seed=16, pool=(0.55, 0.45, 0.65))
    amt = 1 - prog(t, X_ALIVE0, X_ALIVE1)
    c = retro(c, t, amt=amt) if amt > 0 else c
    # astrolabe under glass: in on 'heritage', dome lifts (token leaves upward) as it comes alive
    up = e_inout(prog(t, X_ALIVE0, X_ALIVE1))
    if up < 1:
        cc = c.copy()
        pop(cc, 'astrolabe', 540, 1020 - 260 * up, 480, t - T_HER)
        c = c * up + cc * (1 - up)
    return c


def scene_alive(t):
    u = prog(t, X_ALIVE0, C_BRIT)
    c = cover(load(f'{DL}/476280551_1049256607242153_4186426492440189340_n.jpg'), fx=0.5, fy=0.55, z=1.1 + 0.08 * u)
    c = deep(c, exp=0.72, night=0.55, t=t, seed=17, pool=(0.5, 0.6, 0.55))
    c = aurora(c, t, 0.32 * prog(t, X_ALIVE0, T_ALIVE + 0.2), 0.04, 0.17)
    pop(c, 'lantern', 540, 1040, 430, t - T_KEEP + 0.1, glow=np.array((1, 0.45, 0.7), np.float32) * (0.6 + 0.4 * prog(t, T_ALIVE - 0.1, T_ALIVE + 0.3)))
    return c


def scene_living(t):
    u = prog(t, C_BRIT, C_END)
    f = clip('drone').at(33.6 + (t - C_BRIT) * 0.75)
    src = cover(f, fx=0.42, fy=0.6, z=1.0 + 0.06 * u)
    c = deep(src, exp=0.85, night=0.85, hal=0.8, t=t, seed=18, pool=(0.45, 0.62, 0.6))
    lt = (t - (T_LIVING - 1.2)) * 1.2
    if lt > 0:
        c = window_lights(c, src, t=lt, seed=7)
    return c


def end_card(t):
    c = canvas(INK)
    u = t - (T_COME - 0.1)
    lg = logo(860)
    a = clamp(u / 0.5)
    paste(c, lg, W / 2, 780 + 20 * (1 - e_out(clamp(u / 0.6))), a)
    if t > T_EXP - 0.15:
        k = clamp((t - T_EXP + 0.15) / 0.35)
        s = text_sprite('COME AND EXPERIENCE IT.', 800, 66, WHITE, track=0.02)
        paste(c, s, W / 2, 1090 + 20 * (1 - e_out(k)), k)
        s2 = text_sprite('bmhc.org.uk', 600, 44, (0.75, 0.75, 0.75))
        paste(c, s2, W / 2, 1180, clamp((t - T_EXP - 0.1) / 0.4))
    pop(c, 'door', 540, 1400, 260, t - T_EXP - 0.2, glow=np.array((1, 0.7, 0.4), np.float32))
    for i, col in enumerate(BARS):                              # the four bars, fixed order
        k = clamp((u - 0.15 * i) / 0.4)
        c[H - 22:, int(W * i / 4):int(W * i / 4 + W / 4 * e_out(k))] = col
    return c


def base(t):
    if t < T_LC0:
        return ai_frame(t)
    if t < T_LC1:
        a = ai_frame(min(t, T_LC1))
        b = scene_iftar(t)
        return layercut(a, b, prog(t, T_LC0, T_LC1), n=6)
    if t < C_KNOW:
        return scene_iftar(t)
    if t < C_YOUNG:
        return scene_know(t)
    if t < C_CONV:
        return scene_young(t)
    if t < C_HER:
        c = scene_conv(t)
        if t > W_HER0:
            u = prog(t, W_HER0, W_HER0 + 0.7)
            c = scene_heritage(t) if u > 0.5 else c
            c = four_bar_wipe(c, u)
        return c
    if t < X_ALIVE0:
        return scene_heritage(t)
    if t < X_ALIVE1:
        k = e_inout(prog(t, X_ALIVE0, X_ALIVE1))
        return scene_heritage(t) * (1 - k) + scene_alive(t) * k
    if t < C_BRIT:
        return scene_alive(t)
    if t < C_END:
        c = scene_living(t)
        if t > W_END0:
            u = prog(t, W_END0, W_END0 + 0.7)
            c = end_card(t) if u > 0.5 else c
            c = four_bar_wipe(c, u)
        return c
    c = end_card(t)
    if t > W_END0 and t < W_END0 + 0.7:
        c = four_bar_wipe(c, prog(t, W_END0, W_END0 + 0.7))
    return c


# ------------------------------------------------------------------ captions (the voice, 2-3 words at a time)
KEY = {'recreate', 'seconds', 'window', 'brick', 'detail', 'but', 'inside', 'friendships', 'knowledge', 'confidence', 'together',
       'preserve', 'alive', 'heritage', 'living', 'community', 'experience', 'building'}


def chunks():
    out = []
    line = []
    for i, (w, a, b) in enumerate(WORDS):
        line.append((w, a, b))
        end_line = w.endswith(('.', ',')) or i == len(WORDS) - 1
        if len(line) == 3 or end_line:
            if len(line) == 3 and not end_line and i + 1 < len(WORDS) and WORDS[i + 1][0].endswith('.') and False:
                pass
            out.append(list(line))
            line = []
    # avoid single trailing words: merge a 1-word chunk into the previous one when it is in the same line
    res = []
    for ch in out:
        if len(ch) == 1 and res and not res[-1][-1][0].endswith('.') and len(res[-1]) < 4:
            res[-1] += ch
        else:
            res.append(ch)
    return res


CH = chunks()


def captions(c, t):
    if t > W_END0 + 0.2:
        return c
    for i, ch in enumerate(CH):
        t0 = ch[0][1] - 0.06
        t1 = CH[i + 1][0][1] - 0.06 if i + 1 < len(CH) else ch[-1][2] + 0.5
        t1 = min(t1, ch[-1][2] + 0.6)
        if t0 <= t < t1:
            parts = [(w.strip('.,'), MAG if norm(w) in KEY else WHITE) for w, a, b in ch]
            if ch[-1][0].endswith('.'):
                parts[-1] = (parts[-1][0] + '.', parts[-1][1])
            caption(c, parts, 1385, u=t - t0, size=74)
    return c


def headlines(c, t):
    if T_LC0 + 0.2 < t < C_FRIEND + 0.05:                     # "BUT NOT THIS."
        u = t - T_LC0 - 0.2
        a = 1 - prog(t, C_FRIEND - 0.15, C_FRIEND + 0.05)
        s1 = text_sprite('BUT', 800, 120, WHITE, track=0.02)
        s2 = text_sprite('NOT THIS.', 800, 120, MAG, track=0.02)
        k = e_back(clamp(u / 0.35), 1.2)
        paste(c, s1, W / 2, 1060 + 20 * (1 - k), a * clamp(u / 0.15))
        paste(c, s2, W / 2, 1190 + 20 * (1 - k), a * clamp((u - 0.12) / 0.15))
    return c


def finish(c, t):
    c = np.clip(c, 0, 1)
    fi = prog(t, 0.0, 0.25)
    fo = 1 - 0.0 * prog(t, DUR - 0.6, DUR)
    return np.clip(c * fi * fo, 0, 1)


def frame(t):
    c = base(t)
    c = headlines(c, t)
    c = captions(c, t)
    return finish(c, t)


def write(i, c, d):
    cv2.imwrite(f'{d}/{i:05d}.png', (np.clip(c, 0, 1)[..., ::-1] * 255 + 0.5).astype(np.uint8))


if __name__ == '__main__':
    mode = sys.argv[1]
    if mode == 'times':
        for k, v in sorted(((k, v) for k, v in globals().items() if re.match(r'^(T|C|W|X)_', k)), key=lambda kv: kv[1]):
            print(f'{k:10s} {v:6.2f}')
        print('DUR', DUR, 'NF', NF, 'placeholder' if INFO.get('placeholder') else 'real voice')
        print([' '.join(w for w, a, b in ch) for ch in CH])
    elif mode == 'still':
        d = f'{S}/stills_out'
        os.makedirs(d, exist_ok=True)
        for ts in sys.argv[2].split(','):
            t = float(ts)
            write(int(t * 100), frame(t), d)
            print('still', t, flush=True)
    elif mode == 'range':
        a, b = int(sys.argv[2]), int(sys.argv[3])
        d = f'{S}/frames'
        os.makedirs(d, exist_ok=True)
        for i in range(a, min(b, NF)):
            if os.environ.get('RESUME') and os.path.exists(f'{d}/{i:05d}.png'):
                continue
            write(i, frame(i / FPS), d)
            if i % 30 == 0:
                print('frame', i, flush=True)
