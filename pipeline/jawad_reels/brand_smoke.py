"""brand_smoke.py - 2 s brand smoke test of Jawad's kit on the 'ember' look (no client footage or 3D assets):
house title lockup (white grotesk line + glowing serif-italic keyword + underline stroke), a glass UI window
rising in 3D with ticking check rows, rising embers, the @jawad_mp4 signature.

    python3 render.py brand_smoke --sheet 4 --samples 1 --workers 1      # contact sheet
    python3 render.py brand_smoke --stills 0.6,1.9 --workers 1            # full-quality stills
    python3 render.py brand_smoke --range 0 2 --samples 1 --workers 1     # render_stats.json (s/frame)
"""
import functools

import jawad_kit as J
from jawad_kit import K, ui

DUR, LOOK, BPM = 2.0, 'ember', 100


@functools.lru_cache(maxsize=1)
def assets():
    win = ui.app_window(w=760, h=600, look=LOOK, title='edit_room.prproj', header='Render queue',
                        sub='reel_01 · 1080 × 1920 · 30 fps', sidebar=False)
    return dict(title=J.HouseTitle('HAR FRAME', 'ek kahani', caps_px=84, key_px=230), win=win,
                sparks=J.embers(110, seed=4))


def prewarm():
    assets()


ROWS = (('Color grade', 0.85), ('Sound design', 1.05), ('Roman Urdu captions', 1.25))


def draw(t):
    A = assets()
    push = K.EASE['inout_sine'](t / DUR)
    cam = K.Cam.orbit((0, 0, 0), 1500 - 70 * push, yaw=K.lerp(2.0, -1.5, push), pitch=K.lerp(-1.0, 0.6, push),
                      aperture=28)
    cv = K.background(LOOK, t, cam)
    A['title'].draw(cv, t, K.CX, 640, t0=0.08)
    win = A['win']
    u = K.ramp(t, 0.30, 1.20, 'out_cubic')
    if u > 0:
        f = win.face_at(sweep=(0.1 + t * 0.4) % 1)
        x, y, sw, sh = win.meta['slot']
        for i, (label, tick) in enumerate(ROWS):
            win.put(f, ui.check_row(label, w=sw, t=t - tick, look=LOOK), x - ui.ROW_PAD, y + i * 104 - ui.ROW_PAD)
        win.plane(cv, cam, (0, 190 + 260 * (1 - u), -30), 740, rot=(6 + 14 * (1 - u), -7, 0.8), face=f,
                  opacity=K.ramp(t, 0.30, 0.65, 'inout_sine'))
    A['sparks'].draw(cv, cam, t)
    J.signature(cv, K.CX, 1585, opacity=K.ramp(t, 1.1, 1.6, 'inout_sine'))
    return cv


def post(cv, t):
    return K.post(cv, LOOK, t)


def samples(t):
    return 3
