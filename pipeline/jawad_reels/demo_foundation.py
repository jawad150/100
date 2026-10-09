"""demo_foundation.py - 6 s demo of the shared motion foundations on Jawad's look 'ember' (not one of the five
reels): three transitions from jawad_tx (C3 portal push-in through the hook's own flame ring (rim=False), O6
ember disintegration, L1 ember leak burn into the card), a snake-caption line with a serif keyword
(snake_captions; clear=PLAN keeps it off screen while the L1 leak washes the frame), and the @jawad_mp4 end card
with the seamless loop back to frame 0 (endcard). 120 BPM grid (a beat = 15 frames): cuts at 0.5, 1.0, 1.5 s.

    python3 demo_foundation.py --stills                 # full-quality stills -> <WS>/foundation/stills/
    python3 demo_foundation.py --sheet 12               # contact sheet -> <WS>/foundation/sheet.jpg
    python3 demo_foundation.py selftest                 # contract + loop seam + stills + sheet (exit 1 on failure)
    python3 render.py demo_foundation --range 0 6 --workers 1    # it is a normal render.py module too
"""
import functools
import math
import os
import sys
import time

import cv2
import numpy as np

import jawad_kit
from jawad_kit import K, T, ui, J
import jawad_tx as X
import snake_captions as SC
import endcard as E

DUR, LOOK, BPM = 6.0, 'ember', 120
G = X.Grid(BPM)
C1, C2, C3 = G.at(0, 1), G.at(0, 2), G.at(0, 3)                  # 0.5, 1.0, 1.5 s (on whole frames)
PLAN = X.Plan([('C3', C1, dict(pre=12, post=3, center=(540.0, 760.0), r0=192.0, rim=False)),   # A draws the ring
               ('O6', C2, dict(pre=10, post=5, direction='ltr', n=3000)),
               ('L1', C3, dict(pre=6, post=6, seed=4))])
CARD_T0 = DUR - 4.5
WORDS = [dict(word='Bas', start=0.08, end=0.30), dict(word='ek', start=0.33, end=0.46),
         dict(word='*change...', start=0.52, end=0.98)]
OUT = os.path.join(K.WS, 'foundation')


@functools.lru_cache(maxsize=1)
def assets():
    ring = K.glow(K.ring(200, 9, np.float32(K.C['AMBER']) * 1.5), K.C['FLAME'], sigmas=(5, 16, 44), strength=1.2)
    s = ui.Surf(940, 300)
    xs = 20.0
    for i, wdt in enumerate((150, 210, 120, 260, 140)):            # a strip of clips on a timeline lane
        col = K.C['FLAME'] if i % 2 == 0 else K.C['RED']
        s.rrect(xs, 90, wdt - 12, 120, 18, np.float32(col) * 0.55)
        s.stroke_rrect(xs, 90, wdt - 12, 120, 18, 2.0, np.float32(col) * 1.6)
        xs += wdt
    clips = K.glow(s.img, K.C['FLAME'], sigmas=(6, 18), strength=0.6)
    return dict(ring=ring, clips=clips, sparks=J.embers(110, seed=11), sparks2=J.embers(90, seed=12),
                rec=T.render('● REC   00:00:00:12', 'jw_mono', px=36),
                cap=SC.Captions(WORDS, band='lower', clear=PLAN),      # off screen during the L1 leak
                card=E.EndCard('COMMENT MEIN', 'batao', monogram='JD', dur=4.5))


def prewarm():
    A = assets()
    A['cap'].prewarm()


def scene_hook(t):
    """A: the hook world - warm void, embers, a flame ring (the portal object), REC readout."""
    A = assets()
    cam = K.Cam.orbit((0, 0, 0), 1500, yaw=2.0 * math.sin(t * 0.8), pitch=0.8, aperture=28)
    cv = K.background(LOOK, t, cam)
    K.draw(cv, A['ring'], 540, 760, scale=1.0 + 0.03 * math.sin(t * 2.0))
    A['sparks'].draw(cv, cam, t)
    A['rec'].draw(cv, 90, 300, anchor=(0, 0.5), opacity=0.9)
    return cv


def scene_edit(t):
    """B: inside the edit - a lane of flame clips drifting in a warmer, closer world."""
    A = assets()
    cam = K.Cam.orbit((0, 0, 0), 1400, yaw=-3.0 + 2.0 * t, pitch=-1.0, aperture=34)
    cv = K.background(LOOK, t + 3.0, cam, center=(0.3, 0.35), boost=0.35)
    K.draw(cv, A['clips'], 540 - 40 * t, 820, scale=1.0)
    A['sparks2'].draw(cv, cam, t)
    return cv


def scene_ash(t):
    """C: after the burn - the darker world the card sits on (noir backdrop under the ember finish)."""
    A = assets()
    cam = K.Cam.orbit((0, 0, 0), 1500, yaw=1.5 * math.sin(t * 0.5), pitch=0.5, aperture=30)
    cv = K.background('noir_ember', t, cam)
    A['sparks'].draw(cv, cam, t + 7.0)
    return cv


def scene_ash_card(t):
    return scene_ash(t)


def world(t):
    return PLAN.draw(t, [scene_hook, scene_edit, scene_ash, scene_ash_card][:len(PLAN.steps) + 1])


def draw(t):
    A = assets()
    cv = E.loop_world(world, t, DUR, d=0.5)           # the last 0.5 s fades into frame 0's own past (loop)
    A['cap'].draw(cv, t)
    A['card'].draw(cv, t, CARD_T0)
    return cv


def post(cv, t):
    kw = PLAN.post_kw(t)
    ck = assets()['card'].post_kw(t, CARD_T0, DUR)
    kw['push'] = kw.get('push', 0.0) + ck.get('push', 0.0)
    return X.finish(cv, t, LOOK, cuts=[(0.0, 0.6)], **kw)


def samples(t):
    return PLAN.samples(t)


def cues():
    A = assets()
    return sorted([dict(t=0.0, name='impact_soft', gain_db=-6, params={})] + PLAN.cues()
                  + A['card'].cues(CARD_T0, DUR), key=lambda c: c['t'])


# =============================================================================================== CLI
STILLS = (0.0, 0.25, 0.45, 0.7, 0.9, 1.1, 1.5, 2.3, 4.0, DUR - 1 / K.FPS)


def _render(t, samples_=None):
    import render
    return render.render_still(sys.modules[__name__], t, samples_)


def do_stills(times=STILLS, samples_=None):
    os.makedirs(os.path.join(OUT, 'stills'), exist_ok=True)
    paths = []
    for t in times:
        t0 = time.perf_counter()
        u8 = _render(t, samples_)
        p = os.path.join(OUT, 'stills', 'demo_foundation_%05.2f.png' % t)
        cv2.imwrite(p, u8[..., ::-1])
        paths.append(p)
        print('%.2f s -> %s  (%.1f s)' % (t, p, time.perf_counter() - t0))
    return paths


def do_sheet(n=12, samples_=1):
    times = [round(i * DUR / n * K.FPS) / K.FPS for i in range(n)]
    ims = []
    for t in times:
        u8 = _render(t, samples_)
        im = cv2.resize(u8, (270, 480), interpolation=cv2.INTER_AREA)
        cv2.putText(im, '%.2f' % t, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (120, 220, 255), 2)
        ims.append(im)
    cols = 6
    rows = [np.hstack(ims[i:i + cols] + [np.zeros_like(ims[0])] * (cols - len(ims[i:i + cols])))
            for i in range(0, len(ims), cols)]
    sheet = np.vstack(rows)
    os.makedirs(OUT, exist_ok=True)
    p = os.path.join(OUT, 'sheet.jpg')
    cv2.imwrite(p, sheet[..., ::-1], [cv2.IMWRITE_JPEG_QUALITY, 92])
    print('->', p)
    return p


def selftest():
    fails = []
    prewarm()
    rep = assets()['cap'].check()
    if rep:
        fails += rep
    if X.check_cues(cues()):
        fails.append('unknown sfx %s' % X.check_cues(cues()))
    a, b = draw(1.234), draw(1.234)
    if not np.array_equal(a, b):
        fails.append('draw is not pure')
    # window-edge continuity in the demo itself (1 sample): the first / last frame of each transition window
    # against its plain neighbour, within 1.5x the step between the two plain frames before / after it
    for (a, b, tid) in PLAN.windows():
        k0, k1 = int(round(a * K.FPS)), int(round(b * K.FPS))
        f = {k: _render(k / K.FPS, 1) for k in (k0 - 2, k0 - 1, k0, k1 - 1, k1, k1 + 1)}
        ent, ext = X.frame_step(f[k0 - 1], f[k0]), X.frame_step(f[k1 - 1], f[k1])
        b_in, b_out = X.frame_step(f[k0 - 2], f[k0 - 1]), X.frame_step(f[k1], f[k1 + 1])
        print('%s window frames %d-%d: entry %.2f / %.2f %%  (plain %.2f / %.2f %%)   exit %.2f / %.2f %%  (plain %.2f / %.2f %%)'
              % (tid, k0, k1 - 1, ent[0], 100 * ent[1], b_in[0], 100 * b_in[1], ext[0], 100 * ext[1], b_out[0],
                 100 * b_out[1]))
        if not X._edge_ok(ent, b_in, floor=0.005) or not X._edge_ok(ext, b_out, floor=0.005):
            fails.append('%s window edge pop in the demo' % tid)
    sr = E.seam_report(lambda t: _render(t, 1), DUR)
    if not sr['ok']:
        fails.append('loop seam %s' % sr)
    if assets()['card'].hold < 1.5:
        fails.append('card hold < 1.5 s')
    t0 = time.perf_counter()
    _render(2.3, 1)
    print('one 1-sample frame under the card: %.2f s' % (time.perf_counter() - t0))
    print('loop seam:', sr)
    print('cuts:', PLAN.cuts, 'windows:', [(round(a, 3), round(b, 3), i) for a, b, i in PLAN.windows()])
    do_stills()
    do_sheet()
    if fails:
        print('FAIL:', *fails, sep='\n  ')
        return False
    print('demo_foundation selftest OK')
    return True


if __name__ == '__main__':
    args = sys.argv[1:]
    if args and args[0] in ('selftest', '--selftest'):
        sys.exit(0 if selftest() else 1)
    if args and args[0] == '--stills':
        times = [float(v) for v in args[1].split(',')] if len(args) > 1 and not args[1].startswith('-') else STILLS
        do_stills(times)
    elif args and args[0] == '--sheet':
        do_sheet(int(args[1]) if len(args) > 1 else 12)
    else:
        print(__doc__)
