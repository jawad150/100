"""Hook HUD (0 - 3.4 s): a Spider-sense lock-on reticle tracking the mask (positions exported from the
Blender camera), a REC/timecode frame, and a 'DELETING MEMORIES' progress panel that fails with
'ERROR - CAN'T DELETE' on 'aasaan NAHI'. Everything is drawn into an overlay and given an After
Effects-style deep glow before it is added to the frame.
"""
import functools
import json
import math
import os

import cv2
import numpy as np

import anim as A
import comp as C
import hud as U

RED = np.float32([1.0, 0.10, 0.06])
WHITE = np.float32([1.0, 0.97, 0.95])
TRACK = C.ROOT + '/plates3/h1_hook_head.json'
T_ERR = 2.78


@functools.lru_cache(maxsize=1)
def track():
    if os.path.exists(TRACK):
        d = json.load(open(TRACK))
        return {int(k): v for k, v in d.items()}
    return {}


def head_at(u):
    tr = track()
    if not tr:
        return 540.0, 820.0
    f = min(max(1, int(round(u * 60)) + 1), max(tr))
    x, y, z = tr[f]
    return x, y


def _line(ov, p0, p1, col, w=2, a=1.0):
    m = np.zeros(ov.shape[:2], np.float32)
    cv2.line(m, (int(p0[0] * 8), int(p0[1] * 8)), (int(p1[0] * 8), int(p1[1] * 8)), 1.0, w, cv2.LINE_AA, shift=3)
    ov += m[..., None] * col * a


def reticle(ov, x, y, u, lock):
    """Segmented ring that spins and closes in on the target, ticks + crosshair, label."""
    r = 190 - 95 * A.EXPO_OUT(lock)
    rot = u * 140 * (1 - lock) + 45 * lock
    m = np.zeros(ov.shape[:2], np.float32)
    for k in range(4):
        a0 = rot + k * 90 + 12
        cv2.ellipse(m, (int(x * 8), int(y * 8)), (int(r * 8), int(r * 8)), 0, a0, a0 + 60, 1.0, 3, cv2.LINE_AA, shift=3)
    cv2.circle(m, (int(x * 8), int(y * 8)), int((r + 18) * 8), 0.35, 1, cv2.LINE_AA, shift=3)
    for k in range(4):
        ang = math.radians(k * 90 + 45 * lock)
        p0 = (x + math.cos(ang) * (r - 16), y + math.sin(ang) * (r - 16))
        p1 = (x + math.cos(ang) * (r + 30), y + math.sin(ang) * (r + 30))
        cv2.line(m, (int(p0[0] * 8), int(p0[1] * 8)), (int(p1[0] * 8), int(p1[1] * 8)), 1.0, 3, cv2.LINE_AA, shift=3)
    col = RED * (1 - lock) + WHITE * 0.0 + RED * lock
    ov += m[..., None] * col * 1.6
    if lock > 0.6:
        spr, b = U.text_mask('TARGET LOCKED', 'SpaceGrotesk-700', 22, 0.25)
        spr = cv2.resize(spr, (spr.shape[1] // U.SS, spr.shape[0] // U.SS), interpolation=cv2.INTER_AREA)
        X, Y = int(x - spr.shape[1] / 2), int(y + r + 40)
        h, w = spr.shape
        if 0 <= X and X + w <= C.W and 0 <= Y and Y + h <= C.H:
            ov[Y:Y + h, X:X + w] += spr[..., None] * RED * 1.4 * A.clamp((lock - 0.6) / 0.4)


def frame_hud(ov, u):
    """Thin corner brackets on the safe area + REC timecode."""
    k = A.ramp(u, 0.05, 0.4, A.EXPO_OUT)
    if k <= 0:
        return
    x0, y0, x1, y1 = 90, 270, 990, 1450
    L = 70 * k
    for (cx, cy, sx, sy) in ((x0, y0, 1, 1), (x1, y0, -1, 1), (x0, y1, 1, -1), (x1, y1, -1, -1)):
        _line(ov, (cx, cy), (cx + sx * L, cy), WHITE, 2, 0.55)
        _line(ov, (cx, cy), (cx, cy + sy * L), WHITE, 2, 0.55)
    tc = f'REC  00:00:{int(u):02d}:{int((u % 1) * 60):02d}'
    m, b = U.text_mask(tc, 'SpaceGrotesk-700', 22, 0.12)
    m = cv2.resize(m, (m.shape[1] // U.SS, m.shape[0] // U.SS), interpolation=cv2.INTER_AREA)
    h, w = m.shape
    ov[300:300 + h, 120:120 + w] += m[..., None] * WHITE * 0.8 * k
    if int(u * 2.5) % 2 == 0:
        cv2.circle(ov, (112, 300 + h // 2), 6, tuple(float(c) for c in RED * 1.4), -1, cv2.LINE_AA)
    m2, _ = U.text_mask('MEMORY.SYS  //  YAADEIN', 'SpaceGrotesk-700', 22, 0.12)
    m2 = cv2.resize(m2, (m2.shape[1] // U.SS, m2.shape[0] // U.SS), interpolation=cv2.INTER_AREA)
    h2, w2 = m2.shape
    ov[300:300 + h2, 960 - w2:960] += m2[..., None] * WHITE * 0.6 * k


@functools.lru_cache(maxsize=256)
def delete_panel(prog_q, err_q):
    prog, err = prog_q / 100, err_q / 16
    w, h = 640, 150
    p = U.Paint(w, h)
    U.glass_panel(p, 0, 0, w, h, 26)
    if err < 0.5:
        p.text('DELETING MEMORIES…', 32, 52, 'SpaceGrotesk-700', 26, U.WHITE, 1.0, track=0.12)
        p.text(f'{int(prog * 100):d}%', w - 32, 52, 'SpaceGrotesk-700', 26, U.WHITE, 1.0, anchor='r')
        p.rrect(32, 84, w - 64, 12, 6, U.WHITE, 0.12)
        if prog > 0.01:
            m = p.rrect(32, 84, (w - 64) * prog, 12, 6, U.RED, 1.0)
            p.glow(m, U.RED, 7, 1.0)
        p.text('memory_0427.jpg  •  khushi', 32, 128, 'SpaceGrotesk-500', 20, U.MUTED, 1.0)
    else:
        p.text('ERROR', 32, 66, 'InterTight-900', 46, U.RED, 1.0, track=0.18)
        p.text("CAN'T DELETE THIS MEMORY", 32, 118, 'SpaceGrotesk-700', 26, U.WHITE, 1.0, track=0.1)
        p.rrect(w - 112, 36, 80, 80, 40, U.RED, 0.18)
        p.line([(w - 92, 56), (w - 52, 96)], 4, U.RED, 1.0)
        p.line([(w - 52, 56), (w - 92, 96)], 4, U.RED, 1.0)
    return p.result()


def draw(cv, t):
    """Overlay for the hook (t global seconds). Returns cv."""
    if t > 3.45:
        return cv
    ov = np.zeros_like(cv)
    frame_hud(ov, t)
    if t < 2.2:
        x, y = head_at(t)
        lock = A.ramp(t, 0.9, 1.7, A.SMOOTH)
        reticle(ov, x, y, t, lock)
    # delete progress panel (1.25 -> error at 2.78)
    if 1.2 < t < 3.45:
        u = t - 1.2
        prog = 0.73 * A.ramp(t, 1.3, 2.7, A.EASY)
        err = A.ramp(t, T_ERR, T_ERR + 0.05)
        img = delete_panel(int(prog * 100), round(err * 16))
        s = A.spring(u, 1.9, 0.6)
        out = A.ramp(t, 3.25, 3.45, A.EXPO_IN)
        shake = 14 * math.exp(-max(0, t - T_ERR) * 9) * math.sin(t * 90) if t > T_ERR else 0.0
        C.draw_img3d(cv, img, C.Cam(0, 0, 0), (shake / 686.0, 0.40, 3.0), (1.0, 1.0 * img.shape[0] / img.shape[1]),
                     ((1 - s) * -60, 0, 0), opacity=min(1.0, u * 4) * (1 - out), glass=(C.frosted(cv), 1.0))
        if t > T_ERR:
            e = math.exp(-(t - T_ERR) * 6)
            cv[...] = U.glitch(cv, 1.4 * e, t, seed=7)
            ov += RED * 0.25 * e
    # deep glow on the HUD lines
    cv += ov + _glow(ov)
    return cv


def _glow(ov):
    q = cv2.resize(ov, (C.W // 4, C.H // 4), interpolation=cv2.INTER_AREA)
    g = cv2.GaussianBlur(q, (0, 0), 2.5) * 0.9 + cv2.GaussianBlur(q, (0, 0), 8) * 0.7 + cv2.GaussianBlur(q, (0, 0), 20) * 0.5
    return cv2.resize(g, (C.W, C.H), interpolation=cv2.INTER_LINEAR)
