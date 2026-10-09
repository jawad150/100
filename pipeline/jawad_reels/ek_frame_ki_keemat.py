"""ek_frame_ki_keemat.py - Reel 3 · C08 "Ek Frame ki Keemat" (the exploded frame) for @jawad_mp4.

Owner: motion-timeline-builder. Spec: brand_reels/design/reels/ek_frame_ki_keemat/HANDOFF.md (r3, wins where it differs)
+ BRIEF.md r2 (§7 geometry and cameras, §8 strings, §10 samples, §17 contract), FACES.md §8. 33.6 s = 14 bars at 100 BPM
(beat 0.6 s = 18 f, bar 72 f), 1,008 frames. Look 'ember', finished only by G.tx_finish. Picture times are frame starts.

SHOT LIST (t s, frames [bar.beat]: picture · camera · transition / push · SFX event in ek_frame_ki_keemat_sfx)
 S1-01  0.0-0.9   f0-26   [0.0]  the frame PLAYING 1:1 (hook lockup settled, chip > 00:00:00:01); PAUSE f9 (layer clock
                                 frozen at tl 0.3 until f792, chip II); seam glint sweep 0.6-0.9 · locked · L3 0.6 (loop seam)
                                 · f0 impact, pause click, glass slide
 S2-01  0.9-2.4   f27-71  [0.1+] layers separate (gap 0 -> 120), pull-back D 4533 -> 8300, chip gone by f32 · P2 · card slide
 S2-02  2.4-5.9   f72-176 [1.0]  orbit to side-on (yaw 52, pitch 8) lands f157 (5.2333, VO "12"); counter 00 -> 12
                                 3.0-5.2333, seams light 01 -> 12; COVER f165 · P3 / P4 · L3 0.3 at f157 · slot ticks, glass truth
 S2-03  5.9-12.0  f177-359       counter exits 5.9-6.15; swoop 5.9-6.8 (gap 120 -> 300); fly-through: arrivals f204 f217 f230
                                 f259 f268 f278 f288 f300 f333 f343 (tags 01..11, <= 2 blocks) · P5 / P6, C6 racks (9 f) · ticks
 S2-04  12.0-16.8 f360-503 [5.0] RE-HOOK stop on pane 12 (tag 12 ON); swing frontal + fold to gap 30 by 13.2; flicks f396 OFF,
                                 f405 ON, f422 OFF, f446 ON (alive); push to the portal 14.6-16.0; rack to pane 03 15.0-15.8;
                                 camera static from 16.0 · P7 / P8 · L3 0.35 at 12.0; C3 * approach f480-503 · clicks, toggles
 S3-01  16.8-18.6 f504-557 [7.0] corridor: 29 flattened stacks + the live stack, light wave 16.9-18.6 · C-A glide · C3 cut
 S3-02  18.6-20.6 f558-617       surge, counter 012 -> 360 18.9-20.6, brake on f618 · C-B · L3 0.5 at 20.6 · whoosh-bys
 S3-03  20.6-24.0 f618-719       360 lockup exits 22.0-22.25; three audio lanes 22.2-24.6 + legend · C-C hold 1 %/s · bar grow
 S3-04  24.0-26.4 f720-791 [10.0] rush back into the live stack (to 25.5), drop-out 25.8, play click f782, slam gap 60 -> 0 ·
                                 C-D / C-E · C8 punch f788-791 · whoosh-bys, riser, silence, click, whip
 S4-01  26.4-29.4 f792-881 [11.0] PAYOFF: the frame PLAYING, EK FRAME KI / keemat, sub 27.7, hidden-JD glint f846-f847 ·
                                 locked (C8 settle 1.1 -> 1.0) · C8 + push 1.0 · reveal stack, dhol drop
 S4-02  29.4-33.6 f882-1007 [12.1] END CARD USKO YEH / bhejo over the dimmed playing frame; loop crossfade 33.0-33.6 brings
                                 the hook lockup + chip back · locked · loop push · card cues, reverse swell into f0

THE FRAME: FRAME[i](cv, tl, lock), i = 1..12 (BRIEF 7.2, true by construction: exactly 12 layer draws; HUD is annotation).
Assembled states draw them in order on one canvas; exploded states draw the 12 cached pane sprites (tl 0.3, hook lock)
as planes at z_i = (6.5 - i) * gap. Layer clock = FF.layer_clock(t); lock 'hook' (t < 26.4), 'pay' (26.4-29.45), None.

BUILD DEVIATIONS from HANDOFF r3 / BRIEF r2 (each seen on a still; reasons in SHARED_REQUESTS R8 where shared):
 - Tags: the brief's offsets put 03, 05/06, 07, 08, 09/10, 11 on top of the frame's own copy (or clamped them onto it) in
   the yawed fly-through views; tag_offset(k) picks, once per tag from its arrival camera, the candidate side with the
   least overlap (tag 12 keeps the brief's frontal box). Leaders end on the pill's nearest edge; two visible blocks are
   pushed apart vertically (fixed side per pair). Defocused foreground panes (CoC > 25 px, in front of focus) draw at
   down to 45 % opacity so blurred white type does not read as grey stains.
 - Corridor: billboards nearer than the live stack fade (to 20 %) where they cover it from 19.8 (the brake) to 24.6.
 - Lane legend at (90, 590 / 640 / 690) instead of y 1330-1440 (that crossed JD's face on the live stack); C3 avoids it.
 - Caption C2 also avoids JD's face on the live stack (live_face_rect): its last chunk sits at y 638-786.
 - End card: dur 4.0 with the type faded 32.94-33.27 (CARD_OUT) and the loop crossfade 33.15-33.6 (LOOP_D 0.45), so the
   card no longer overlaps the returning hook lockup; hold 1.69 s.
 - Lanes: <RW>/audio/ek_frame_ki_keemat_env.json is used when the mix stage writes it; until then VO = vo_stem.wav RMS,
   SFX / MUSIC = labelled PLACEHOLDER envelopes (envelopes()['placeholder']).

CLI: python3 ek_frame_ki_keemat.py --selftest   (geometry, timing, text blocks, safe zones, captions; no full renders)
     python3 ek_frame_ki_keemat.py --srt        (<RW>/captions/ek_frame_ki_keemat.srt, the three caption windows)
Render: run from pipeline/jawad_reels through tools/heavy.sh, render.py --workers 1 (HANDOFF §10).
"""
import functools
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import cv2                                          # noqa: E402
import numpy as np                                  # noqa: E402

import jawad_kit                                    # noqa: E402  FIRST: palette, looks, house type
from jawad_kit import K, T, J                       # noqa: E402
import jawad_tx as X                                # noqa: E402
import jawad_grade as G                             # noqa: E402
import endcard as E                                 # noqa: E402
import snake_captions as SC                         # noqa: E402
import ek_frame_ki_keemat_faces as FF               # noqa: E402

# ============================================================================================ contract
DUR, LOOK, BPM = 33.6, 'ember', 100
BEAT = 60.0 / BPM
FPS = K.FPS
HALF = 0.5 / FPS
BED = None                                          # the sfx / music modules build the mix (render with --audio)
GRID = X.Grid(100)
RW = os.path.join(K.WS, 'ek_frame_ki_keemat')
WORDS = os.path.join(RW, 'vo', 'words.json')
VO_WAV = os.path.join(RW, 'vo', 'vo_stem.wav')
ENV_JSON = os.path.join(RW, 'audio', 'ek_frame_ki_keemat_env.json')
SPRITES = os.path.join(RW, 'sprites')


def F(f):
    """Frame -> seconds, rounded as in the HANDOFF tables (SFX_EVENTS)."""
    return round(f / 30.0, 4)


def fr(f):
    """Frame -> exact seconds (picture times)."""
    return f / 30.0


def fi(t):
    """Frame index of a time (motion-blur sub-samples, +-0.25 f, map to their frame)."""
    return int(math.floor(t * FPS + 0.5))


T_PAUSE, T_PLAY, T_CARD = 0.3, 26.4, 29.4
T_LAND = fr(157)                                    # 5.2333: side-on lands, counter 12 settles ("12" spoken 5.230)
T_COVER = fr(165)                                   # 5.5 cover frame
T_C3, T_C8 = 16.8, 26.4
T_360 = fr(618)                                     # 20.6: 360 lands
CUTS = [(0.0, 0.6), (5.2333, 0.3), (12.0, 0.35), (20.6, 0.5), (26.4, 0.6)]
SFX_EVENTS = dict(
    land12=F(157),
    swoop=6.3,
    tags=(F(204), F(217), F(230), F(259), F(268), F(278), F(288), F(300), F(333), F(343)),
    flicks=(F(396), F(405), F(422), F(446)),
    alive=F(446),
    land360=F(618),
    lanes=F(666),
)
CTA = 'USKO YEH'                                    # HANDOFF R1: matches the VO stem ("usko"); fallback 'USSE YEH'

F85, F100, F35 = 4533.0, 5333.0, 1867.0             # lens set: f_px = mm / 36 x 1920
LIVE_Z = 10470.0                                    # the live stack in the corridor

# fly-through (BRIEF 7.3 LOOK_k + tag anchors, HANDOFF 3.2 arrivals)
LOOKS = {1: (760, 520), 2: (760, 600), 3: (640, 760), 4: (440, 1300), 5: (440, 1300), 6: (420, 1460), 7: (600, 1120),
         8: (540, 680), 9: (540, 640), 10: (540, 640), 11: (540, 791), 12: (540, 960)}
ARR = [(204, 1), (217, 2), (230, 3), (259, 4), (268, 5), (278, 6), (288, 7), (300, 8), (333, 9), (343, 11), (360, 12)]
ARR_T = [(fr(f), k) for f, k in ARR]
TAG_ANCHOR = {1: ((300, 500), (36, -36)), 2: ((760, 600), (36, -36)), 3: ((812, 1120), (36, -36)),
              4: ((600, 1180), (36, -36)), 5: ((590, 1010), (36, -36)), 6: ((640, 1560), (36, -60)),
              7: ((760, 1250), (36, -36)), 8: ((800, 471), (36, -40)), 9: ((830, 640), (30, -60)),
              11: ((870, 791), (30, -40)), 12: ((60, 60), (36, 30))}
# tag blocks (HANDOFF 3.2): (in frame, anchor pane, lines); block k fades out over the 0.2 s ending when block k+2 arrives
TAGS = [(204, 1, ('01 · andhera',)), (217, 2, ('02 · dhuaan',)), (230, 3, ('03 · roshni',)), (259, 4, ('04 · chehra',)),
        (268, 5, ('05 · rim light', '06 · saaya')), (288, 7, ('07 · chingaariyan',)), (300, 8, ('08 · lafz',)),
        (333, 9, ('09 · keyword', '10 · chamak')), (343, 11, ('11 · lakeer',)), (360, 12, None)]
FLICK_F = (396, 405, 422, 446)                      # OFF, ON, OFF, ON (resolved "with")

# copy rects (frame px) that layer 03's bokeh avoids (BRIEF 7.2)
COPY_RECTS = [(220, 420, 860, 935), (190, 420, 890, 915), (575, 1226, 945, 1338), (242, 1120, 564, 1564)]
DISC_XY, DISC_R = (812.0, 1120.0), 58.0             # pane 03 portal disc (the C3 aperture)
HJD_XY = (836.0, 330.0)                             # hidden JD glyph in layer 03
CHIP_XY = (760.0, 1282.0)


def lin(name, gain=1.0):
    return np.asarray(K.C[name], np.float32) * np.float32(gain)


def ease(name, x):
    return float(K.get_ease(name)(min(1.0, max(0.0, x))))


def ramp(t, a, b, e):
    return K.ramp(t, a, b, e)


def _ro(a):
    a = np.ascontiguousarray(a, np.float32)
    a.setflags(write=False)
    return a


def lock_of(t):
    if t < T_PLAY:
        return 'hook'
    if t < 29.45:
        return 'pay'
    return None


def layer_clock(t):
    return FF.layer_clock(t)


def glint_gain(tl):
    """BRIEF 7.2 r2: hidden-JD emission 0.35, x1.20 on f846, x0.70 on f847 (keyed on the rounded frame)."""
    return {-162: 1.20, -161: 0.70}.get(int(round(tl * 30)), 0.35)


# ============================================================================================ static sprites
@functools.lru_cache(maxsize=1)
def _haze():
    """Layer 02 (dhuaan): warm fbm haze + 5 god-ray shafts from (1060, 60), FLAME x0.10 emissive (BRIEF 7.2)."""
    n = X.up(X.fbm(11, 5.0))
    ys = np.arange(K.H, dtype=np.float32)[:, None] / K.H
    a = np.clip(n * 0.20 * (0.35 + 0.65 * (1 - ys)), 0, 1)
    out = np.zeros((K.H, K.W, 4), np.float32)
    out[..., :3] = lin('SMOKE', 1.8) * a[..., None]
    out[..., 3] = a
    yy, xx = np.mgrid[0:K.H, 0:K.W].astype(np.float32)
    ang = np.degrees(np.arctan2(yy - 60, xx - 1060)) % 360
    r = np.hypot(xx - 1060, yy - 60)
    rays = np.zeros((K.H, K.W), np.float32)
    for c, wdt in ((112, 2.0), (118, 1.2), (124, 2.4), (131, 1.5), (138, 1.0)):
        rays += np.exp(-0.5 * ((ang - c) / wdt) ** 2)
    rays = cv2.GaussianBlur(rays, (0, 0), 32) * np.clip(1 - r / 2200, 0, 1)
    out[..., :3] += lin('FLAME', 0.10) * rays[..., None]
    return _ro(out)


@functools.lru_cache(maxsize=1)
def _copy_mask():
    """(H, W, 1) multiplier for layer 03's bokeh: 0.15 inside the copy rects, 40 px feather."""
    m = np.zeros((K.H, K.W), np.float32)
    for x0, y0, x1, y1 in COPY_RECTS:
        m[y0:y1, x0:x1] = 1.0
    m = cv2.GaussianBlur(m, (0, 0), 40 / 2.5)
    return _ro((1.0 - 0.85 * np.clip(m, 0, 1))[..., None])


@functools.lru_cache(maxsize=1)
def _hidden_jd():
    """Hidden JD glyph: jw_key_core 80 px at (836, 330), blurred sigma 2.5, emissive (alpha 0). -> (x0, y0, rgb)."""
    cv = np.zeros((K.H, K.W, 4), np.float32)
    T.render('JD', 'jw_key_core', px=80).draw(cv, HJD_XY[0], HJD_XY[1])
    ys, xs = np.nonzero(cv[..., 3] > 0.002)
    x0, x1 = max(0, xs.min() - 12), min(K.W, xs.max() + 13)
    y0, y1 = max(0, ys.min() - 12), min(K.H, ys.max() + 13)
    rgb = cv2.GaussianBlur(np.ascontiguousarray(cv[y0:y1, x0:x1, :3]), (0, 0), 2.5)
    return int(x0), int(y0), _ro(rgb)


@functools.lru_cache(maxsize=1)
def assets():
    A = dict(haze=_haze(), mask03=_copy_mask(), hjd=_hidden_jd(), disc=jawad_kit._bokeh_disc(int(DISC_R), 'FLAME'),
             embers=J.embers(150, seed=7), cam_emb=K.Cam(aperture=24),
             ht_hook=J.HouseTitle('AAP NE ISE', '0.03 sec', caps_px=86, key_px=210),
             ht_pay=J.HouseTitle('EK FRAME KI', 'keemat', caps_px=86, key_px=210),
             dekha=T.render('DEKHA', 'jw_caps', px=86), sub=T.render('banane wala jaanta hai', 'jw_body', px=56))
    return A


# ============================================================================================ the 12 frame layers
def _L01(cv, tl, lock):                             # background void (andhera), opaque base
    cv[...] = K.background('ember', tl, bokeh=0.0)


def _L02(cv, tl, lock):                             # haze + god rays (dhuaan)
    h = assets()['haze']
    cv *= (1.0 - h[..., 3:4])
    cv += h


def _L03(cv, tl, lock):                             # bokeh (roshni) + portal disc + hidden JD
    A = assets()
    lay = np.zeros((K.H, K.W, 4), np.float32)
    jawad_kit._draw_bokeh(lay, 'ember', tl, None, 1.8, 3, 1.0)
    cv[..., :3] += lay[..., :3] * A['mask03']
    K.draw(cv, A['disc'], DISC_XY[0], DISC_XY[1], opacity=0.45)
    x0, y0, rgb = A['hjd']
    cv[y0:y0 + rgb.shape[0], x0:x0 + rgb.shape[1], :3] += rgb * np.float32(glint_gain(tl))


def _L04(cv, tl, lock):                             # JD cut-out (chehra), light wrap from layers 01-03 in cv
    FF.draw_layer(cv, 4, tl)


def _L05(cv, tl, lock):                             # rim light (emissive)
    FF.draw_layer(cv, 5, tl)


def _L06(cv, tl, lock):                             # contact shadow + halo (saaya)
    FF.draw_layer(cv, 6, tl)


def _L07(cv, tl, lock):                             # embers (chingaariyan)
    A = assets()
    A['embers'].draw(cv, A['cam_emb'], tl)


def _title(lock):
    return assets()['ht_hook' if lock == 'hook' else 'ht_pay']


def _title_t(tl, lock):
    """Reel time used by the payoff lockup animation (t0 26.4); the hook lockup is settled (frame content)."""
    return tl + DUR if lock == 'pay' else 99.0


def _L08(cv, tl, lock):                             # caps words (lafz)
    if lock is None:
        return
    A = assets()
    ht = _title(lock)
    x, y = 540.0, 640.0
    cy = y - ht.kh / 2 - ht.gap - ht.caps.h / 2
    if lock == 'hook':
        ht.caps.draw(cv, x, cy)
        A['dekha'].draw(cv, 540.0, 884.5)
        return
    t = _title_t(tl, lock)
    out = 1.0 - ramp(t, 29.1, 29.45, 'in_cubic')
    uc = ramp(t, T_PLAY, T_PLAY + 0.6, 'out_cubic')
    op = out * ramp(t, T_PLAY, T_PLAY + 0.42, 'inout_sine')
    if op > 0:
        ht.caps.draw(cv, x, cy + 28 * (1 - uc), opacity=op, blur=6 * (1 - uc))
    us = ramp(t, 27.7, 28.1, 'out_cubic')
    so = out * ramp(t, 27.7, 28.1, 'inout_sine')
    if so > 0:
        A['sub'].draw(cv, 540.0, 874.0 + 16 * (1 - us), opacity=so)


def _L09(cv, tl, lock):                             # keyword core (keyword)
    if lock is None:
        return
    ht = _title(lock)
    if lock == 'hook':
        ht.key_static.draw(cv, 540.0, 640.0)
        return
    t = _title_t(tl, lock)
    op = 1.0 - ramp(t, 29.1, 29.45, 'in_cubic')
    tk = T_PLAY + 0.22
    if t < tk or op <= 0:
        return
    if t - tk < 1.2 or op < 1:
        ht.key.rise(cv, t, 540.0, 640.0, t0=tk, stagger=0.03, dur=0.5, dist=0.3, blur=7, scale0=0.94, opacity=op)
    else:
        ht.key_static.draw(cv, 540.0, 640.0, opacity=op)


def _L10(cv, tl, lock):                             # keyword halo (chamak)
    if lock is None:
        return
    ht = _title(lock)
    if lock == 'hook':
        ht.halo.draw(cv, 540.0, 640.0)
        return
    t = _title_t(tl, lock)
    op = 1.0 - ramp(t, 29.1, 29.45, 'in_cubic')
    tk = T_PLAY + 0.22
    if t < tk or op <= 0:
        return
    hk = ramp(t, tk, tk + 0.5 + 0.03 * len(ht.key_txt), 'inout_sine')
    ht.halo.draw(cv, 540.0, 640.0, opacity=op * hk)


def _L11(cv, tl, lock):                             # underline (lakeer)
    if lock is None:
        return
    ht = _title(lock)
    x0, yl = 540.0 - ht.ul_len / 2, 640.0 + ht.kh / 2 + ht.key_px * 0.36
    if lock == 'hook':
        ht.ul.draw(cv, x0, yl, u=1.0)
        return
    t = _title_t(tl, lock)
    op = 1.0 - ramp(t, 29.1, 29.45, 'in_cubic')

    def uu(tt):
        return ramp(tt, T_PLAY + 0.55, T_PLAY + 1.25, 'inout_cubic')
    u = uu(t)
    if u > 0 and op > 0:
        speed = (uu(t + 0.004) - uu(t - 0.004)) / 0.008 * ht.ul_len
        ht.ul.draw(cv, x0, yl, u=u, opacity=op, smear=speed * 0.25 / FPS)


def _L12(cv, tl, lock):                             # finish (vignette, halation, grain): one static sprite
    fin = panes()['finish']
    cv *= (1.0 - fin[..., 3:4])
    cv += fin


FRAME = [_L01, _L02, _L03, _L04, _L05, _L06, _L07, _L08, _L09, _L10, _L11, _L12]
LAYER_NAMES = ['andhera', 'dhuaan', 'roshni', 'chehra', 'rim light', 'saaya', 'chingaariyan', 'lafz', 'keyword', 'chamak',
               'lakeer', 'finish']


def draw_frame(tl, lock, upto=12):
    """Assembled frame (playing / paused) at layer time tl: the 12 layers in order on one canvas."""
    cv = np.zeros((K.H, K.W, 4), np.float32)
    for i in range(upto):
        FRAME[i](cv, tl, lock)
    return cv


def _finish_sprite(p5, p9):
    """Layer 12: vignette (black alpha 0.62 x smoothstep(0.50, 1.15, r)), halation (FLAME x0.22 x blur 22 of the
    luminance > 0.9 of layers 05 + 09), grain (sigma 0.8 px, +-0.02: + emissive, - as black alpha x0.6)."""
    yy, xx = np.mgrid[0:K.H, 0:K.W].astype(np.float32)
    r = np.hypot((xx - 540) / 540, (yy - 960) / 960)
    av = 0.62 * np.clip((r - 0.50) / 0.65, 0, 1) ** 2 * (3 - 2 * np.clip((r - 0.50) / 0.65, 0, 1))
    lum = (p5[..., :3] + p9[..., :3]) @ np.array([0.2126, 0.7152, 0.0722], np.float32)
    hal = cv2.GaussianBlur(np.clip(lum - 0.9, 0, None).astype(np.float32), (0, 0), 22)
    rng = np.random.default_rng(1208)
    g = cv2.GaussianBlur(rng.standard_normal((K.H, K.W)).astype(np.float32), (0, 0), 0.8)
    g *= np.float32(0.02 / max(1e-6, float(g.std())))
    out = np.zeros((K.H, K.W, 4), np.float32)
    out[..., :3] = lin('FLAME', 0.22) * hal[..., None] + np.clip(g, 0, None)[..., None] * lin('IVORY')
    an = 0.6 * np.clip(-g, 0, None)
    out[..., 3] = 1.0 - (1.0 - av) * (1.0 - an)
    return _ro(out)


@functools.lru_cache(maxsize=1)
def panes():
    """The 12 pane sprites at the pause (tl 0.3, hook lock), their flat composite, the finish sprite and the seam-glint
    edge sprites of panes 04, 08, 09, 11. Built once per process (~3-5 s)."""
    tl, lock = T_PAUSE, 'hook'
    P = {}
    cv = np.zeros((K.H, K.W, 4), np.float32)
    _L01(cv, tl, lock)
    P[1] = _ro(cv)
    for i, fn in ((2, _L02), (3, _L03), (7, _L07), (8, _L08), (9, _L09), (10, _L10), (11, _L11)):
        c = np.zeros((K.H, K.W, 4), np.float32)
        fn(c, tl, lock)
        P[i] = _ro(c)
    bg = np.array(P[1], copy=True)
    for i in (2, 3):
        bg = P[i] + bg * (1.0 - P[i][..., 3:4])
    P[4] = FF.pane(4, bg)
    P[5] = FF.pane(5)
    P[6] = FF.pane(6)
    fin = _finish_sprite(P[5], P[9])
    P[12] = fin
    flat = np.array(P[1], copy=True)
    for i in range(2, 13):
        flat = P[i] + flat * (1.0 - P[i][..., 3:4])
    edges = {}
    for i in (4, 8, 9, 11):
        a = np.ascontiguousarray(P[i][..., 3])
        gx = cv2.Sobel(a, cv2.CV_32F, 1, 0, ksize=3)
        gy = cv2.Sobel(a, cv2.CV_32F, 0, 1, ksize=3)
        m = np.clip(np.hypot(gx, gy) * 0.5, 0, 1)
        m = cv2.GaussianBlur(m, (0, 0), 1.2)
        ys, xs = np.nonzero(m > 0.01)
        x0, x1 = max(0, xs.min() - 4), min(K.W, xs.max() + 5)
        y0, y1 = max(0, ys.min() - 4), min(K.H, ys.max() + 5)
        e = np.zeros((y1 - y0, x1 - x0, 4), np.float32)
        e[..., :3] = lin('FLAME', 1.6) * m[y0:y1, x0:x1, None]
        edges[i] = (_ro(e), (x0 + x1) / 2.0 - 540.0, (y0 + y1) / 2.0 - 960.0, float(x1 - x0))
    return dict(P=P, flat=_ro(flat), finish=fin, edges=edges)


@functools.lru_cache(maxsize=1)
def stack_flat():
    """ONE pre-flattened stack sprite for the corridor billboards (gap 120, hook lock, tl 0.3) seen from
    Cam.orbit((0, 0, 0), 9000, yaw=30, pitch=4, focal=4533), alpha-cropped; cached in <RW>/sprites/."""
    path = os.path.join(SPRITES, 'stack_flat_v1.npz')
    if os.path.exists(path):
        try:
            return _ro(np.load(path)['spr'].astype(np.float32))
        except (OSError, ValueError, KeyError):
            pass
    P = panes()['P']
    cam = K.Cam.orbit((0, 0, 0), 9000, yaw=30, pitch=4, focal=F85)
    cv = np.zeros((K.H, K.W, 4), np.float32)
    for i in range(1, 13):
        K.draw_plane(cv, P[i], cam, (0.0, 0.0, (6.5 - i) * 120.0), 1080.0, dof=False)
    ys, xs = np.nonzero(cv[..., 3] > 0.003)
    spr = cv[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    os.makedirs(SPRITES, exist_ok=True)
    tmp = path + '.tmp.npz'
    np.savez_compressed(tmp, spr=spr.astype(np.float16))
    os.replace(tmp, path)
    return _ro(spr.astype(np.float16).astype(np.float32))


# ============================================================================================ cameras
def zk(k, gap):
    return (6.5 - k) * gap


def _blend(a, b, u):
    return tuple(x + (y - x) * u for x, y in zip(a, b))


def _fly(k, gap):
    lx, ly = LOOKS[k]
    return (lx - 540.0, ly - 960.0, zk(k, gap), 4920.0, 32.0, 3.0, F85, 420.0)


FRONT = (0.0, -306.4, 0.0, 8600.0, 0.0, 0.0, F100, 0.0)


def _S(x):
    """Integral of an inout_sine rate ramp over 0.3 s (BRIEF 7.3 P8)."""
    if x <= 0:
        return 0.0
    if x < 0.3:
        return x / 2 - (0.15 / math.pi) * math.sin(math.pi * x / 0.3)
    return x - 0.15


def push_p(t):
    return 0.01 * (t - 13.2) + 0.035 * _S(t - 14.6)


def _hold_pose(t):
    return (0.0, -265.0, 0.0, 9400.0 * (1 - 0.01 * (t - T_LAND)), 52.0, 8.0, F85, 0.0)


def stack_pose(t):
    """(pose, gap, focus) of the stack camera (S1 / S2; held static from 16.0). pose = (tx, ty, tz, D, yaw, pitch,
    focal, aperture); focus = None | ('pane', k0, k1, w) (blend of pane-centre depths) | ('z', z)."""
    t = min(t, 16.0)
    if t < 0.9:
        return (0.0, 0.0, 0.0, 4533.0, 0.0, 0.0, F85, 0.0), 0.0, None
    if t < 2.4:
        v = (t - 0.9) / 1.5
        u = ease('easy_ease', v)
        return (0.0, -347.9 * u, 0.0, 4533.0 + (8300.0 - 4533.0) * u, 0.0, 0.0, F85, 0.0), 120.0 * ease('inout_cubic', v), None
    if t < T_LAND:
        u = ease('easy_ease', (t - 2.4) / (T_LAND - 2.4))
        return (0.0, -347.9 + (347.9 - 265.0) * u, 0.0, 8300.0 + 1100.0 * u, 52.0 * u, 8.0 * u, F85, 0.0), 120.0, None
    if t < 5.9:
        return _hold_pose(t), 120.0, None
    if t < 6.8:
        v = (t - 5.9) / 0.9
        gap = 120.0 + 180.0 * ease('inout_cubic', v)
        return _blend(_hold_pose(t), _fly(1, gap), ease('easy_ease', v)), gap, ('pane', 1, 1, 0.0)
    if t < 12.0:
        j = max(i for i in range(len(ARR_T) - 1) if ARR_T[i][0] <= t)
        (a0, k0), (a1, k1) = ARR_T[j], ARR_T[j + 1]
        u = ease('inout_sine', (t - a0) / (a1 - a0))
        w = ease('inout_cubic', (t - (a1 - 9.0 / FPS)) / (9.0 / FPS))
        return _blend(_fly(k0, 300.0), _fly(k1, 300.0), u), 300.0, ('pane', k0, k1, w)
    if t < 13.2:
        u = ease('easy_ease', (t - 12.0) / 1.2)
        gap = 300.0 - 270.0 * u
        return _blend(_fly(12, gap), FRONT, u), gap, ('pane', 12, 12, 0.0)
    ap = 900.0 * ease('inout_cubic', (t - 15.0) / 0.8) if t >= 15.0 else 0.0
    return (0.0, -306.4, 0.0, 8600.0 * (1 - push_p(t)), 0.0, 0.0, F100, ap), 30.0, ('z', zk(3, 30.0))


def make_cam(pose, gap=0.0, focus=None):
    tx, ty, tz, D, yaw, pitch, f, ap = pose
    cam = K.Cam.orbit((tx, ty, tz), D, yaw=yaw, pitch=pitch, focal=f, aperture=ap)
    if focus is not None and ap > 0:
        if focus[0] == 'pane':
            _, k0, k1, w = focus
            d0 = cam.depth((0.0, 0.0, zk(k0, gap)))
            d1 = cam.depth((0.0, 0.0, zk(k1, gap)))
            cam.focus_dist = max(1.0, d0 + (d1 - d0) * w)
        else:
            cam.focus_dist = max(1.0, cam.depth((0.0, 0.0, focus[1])))
    return cam


def stack_cam(t):
    pose, gap, focus = stack_pose(t)
    return make_cam(pose, gap, focus), gap


def stack_corners(gap, z0=0.0, only=None):
    P = []
    for i in range(1, 13) if only is None else only:
        z = z0 + zk(i, gap)
        P += [(-540.0, -960.0, z), (540.0, -960.0, z), (540.0, 960.0, z), (-540.0, 960.0, z)]
    return np.array(P, np.float64)


def _bbox(cam, P):
    xy, z = cam.project(P)
    return float(np.nanmin(xy[:, 0])), float(np.nanmin(xy[:, 1])), float(np.nanmax(xy[:, 0])), float(np.nanmax(xy[:, 1]))


# --- C3 portal geometry (re-derived from the 16.0 camera; HANDOFF §5)
def _c3_geometry():
    cam, gap = stack_cam(16.0)
    c = np.array([[DISC_XY[0] - 540.0, DISC_XY[1] - 960.0, zk(3, gap)],
                  [DISC_XY[0] - 540.0 + DISC_R, DISC_XY[1] - 960.0, zk(3, gap)]])
    xy, _ = cam.project(c)
    return (float(xy[0, 0]), float(xy[0, 1])), float(np.hypot(*(xy[1] - xy[0])))


_C3_PROJ, _C3_R = _c3_geometry()
if abs(_C3_PROJ[0] - 719.4) <= 0.5 and abs(_C3_PROJ[1] - 1267.5) <= 0.5 and abs(_C3_R - 38.2) <= 0.5:
    C3_CENTER, C3_R0 = (719.4, 1267.5), 41.0                      # the brief's numbers (projection agrees)
else:                                                           # pragma: no cover (geometry changed)
    C3_CENTER, C3_R0 = (round(_C3_PROJ[0], 1), round(_C3_PROJ[1], 1)), round(_C3_R + 2.8, 1)
C8_CENTER = (465.0, 1282.0)
PLAN = X.Plan([('C3', T_C3, dict(center=C3_CENTER, r0=C3_R0, rim=False)),
               ('C8', T_C8, dict(center=C8_CENTER, s1=1.25, b0=1.1))])
_C3_WIN = X.TX['C3'].win(T_C3)


def c3_affine(t):
    """The C3 A-side zoom (scale s about C3_CENTER, gliding to the frame centre) at t: (s, cx, cy, px, py)."""
    u = _C3_WIN.ua(t)
    e = K.EASE['in_expo'](u)
    far = max(math.hypot(K.CX - x, K.CY - y) for x in (0, K.W) for y in (0, K.H))     # X._portal_scale(centre)
    sfull = far * 1.06 / C3_R0 * 1.02
    s = sfull ** e
    em = (s - 1.0) / max(1e-6, sfull - 1.0)
    return s, C3_CENTER[0], C3_CENTER[1], K.lerp(C3_CENTER[0], K.CX, em), K.lerp(C3_CENTER[1], K.CY, em)


def stack_rect(t):
    """Screen bbox of the 48 projected pane corners at the scene camera of t (caption C1's avoid rect); for
    t >= 16.0 mapped through the C3 A-side affine."""
    cam, gap = stack_cam(t)
    x0, y0, x1, y1 = _bbox(cam, stack_corners(gap))
    if t >= 16.0:
        s, cx, cy, px, py = c3_affine(t)
        x0, x1 = s * (x0 - cx) + px, s * (x1 - cx) + px
        y0, y1 = s * (y0 - cy) + py, s * (y1 - cy) + py
    return (x0, y0, x1, y1)


# --- corridor camera (C-A .. C-E; r3: surge to 20.6)
def _corr_pose(t):
    """(camera z, camera y, look-at y) of the corridor camera (looking at (0, look_y, LIVE_Z))."""
    if t < 18.6:
        u = ease('easy_ease', (t - 16.8) / 1.8)
        return -700.0 + 1000.0 * u, -40.0, -40.0
    if t < T_360:
        u = ease('inout_sine', (t - 18.6) / (T_360 - 18.6))
        return 300.0 + 6770.0 * u, -40.0, -40.0 - 306.0 * u
    zc = LIVE_Z - (LIVE_Z - 7070.0) * (1 - 0.01 * (t - T_360))     # C-C hold, 1 %/s push
    if t < 24.0:
        return zc, -40.0, -346.0
    if t < 25.8:                                                  # C-D push in (in_cubic) to 8545, centred
        u = ease('in_cubic', (t - 24.0) / 1.8)
        z_end = LIVE_Z - (LIVE_Z - 7070.0) * (1 - 0.01 * (25.8 - T_360))
        return zc + (8545.0 - z_end) * u, -40.0 * (1 - u), -346.0 * (1 - u)
    return LIVE_Z - (LIVE_Z - 8545.0) * (1 - 0.01 * (t - 25.8)), 0.0, 0.0     # C-E near-freeze


def corr_cam(t):
    z, cy, ly = _corr_pose(t)
    pitch = math.degrees(math.atan2(cy - ly, LIVE_Z - z))
    return K.Cam(pos=(0.0, cy, z), pitch=pitch, focal=F35)


def corr_gap(t):
    if t < 24.0:
        return 120.0
    if t < 26.0667:
        return 120.0 - 60.0 * ease('inout_sine', (t - 24.0) / 1.5)
    return 60.0 * (1.0 - ease('in_expo', (t - fr(782)) / (26.4 - fr(782))))


# ============================================================================================ HUD sprites
@functools.lru_cache(maxsize=1)
def chip():
    """HUD chip (BRIEF 7.4): pill 330x72 r 18, SMOKE x0.9 fill, 2 px FLAME x1.4 stroke + glow; icon at pill x 20-50;
    00:00:00:01 jw_mono 38 from pill x 54. Returns sprites (all centred on the pill centre, same size)."""
    w, h, M = 330, 72, 40
    a = K.rrect_alpha(w, h, 18, M)
    inner = np.clip(0.5 - (K.rrect_sdf(w, h, 18, M) + 2.0), 0, 1)
    ring = np.clip(a - inner, 0, 1)
    base = np.zeros(a.shape + (4,), np.float32)
    base[..., :3] = lin('SMOKE', 0.9) * inner[..., None]
    base[..., 3] = inner
    T.render('00:00:00:01', 'jw_mono', px=38, fill=('IVORY', 0.92)).draw(base, M + 54, M + h / 2, anchor=(0, 0.5))
    stroke = np.zeros_like(base)
    stroke[..., :3] = lin('FLAME', 1.4) * ring[..., None]
    stroke[..., 3] = ring
    stroke = K.glow(stroke, K.C['FLAME'], sigmas=(6, 16), strength=0.35, include=True, pad_px=0)
    ss = 4
    def icon(polys):
        m = np.zeros(((h + 2 * M) * ss, (w + 2 * M) * ss), np.uint8)
        for p in polys:
            cv2.fillPoly(m, [np.round((np.array(p, np.float64) + M) * ss).astype(np.int32)], 255, cv2.LINE_AA)
        m = cv2.resize(m.astype(np.float32) / 255.0, (w + 2 * M, h + 2 * M), interpolation=cv2.INTER_AREA)
        s = np.zeros((h + 2 * M, w + 2 * M, 4), np.float32)
        s[..., :3] = lin('IVORY', 0.92) * m[..., None]
        s[..., 3] = m
        return _ro(s)
    play = icon([[(22, 19), (22, 53), (50, 36)]])
    pause = icon([[(20, 19), (28, 19), (28, 53), (20, 53)], [(42, 19), (50, 19), (50, 53), (42, 53)]])
    if stroke.shape != base.shape:                      # K.glow may pad: centre-crop to the base size
        dy, dx = (stroke.shape[0] - base.shape[0]) // 2, (stroke.shape[1] - base.shape[1]) // 2
        stroke = stroke[dy:dy + base.shape[0], dx:dx + base.shape[1]]
    return dict(base=_ro(base), stroke=_ro(stroke), play=play, pause=pause)


def draw_chip(cv, t):
    """Chip f0-f31 (fade f24-f32, in_cubic) and t < 0 (the loop); icon > until f8, II from f9; stroke flare at f9."""
    if t >= fr(32):
        return
    op = 1.0 - ramp(t, fr(24), fr(32), 'in_cubic') if t >= 0 else 1.0
    if op <= 0:
        return
    C = chip()
    x, y = CHIP_XY
    K.draw(cv, C['base'], x, y, opacity=op)
    paused = 0 <= t and fi(t) >= 9
    K.draw(cv, C['pause' if paused else 'play'], x, y, opacity=op)
    K.draw(cv, C['stroke'], x, y, opacity=op)
    if paused:                                          # FLAME stroke flares x2.2 -> x1.4 over 6 f (local glow)
        fl = (2.2 / 1.4 - 1.0) * (1.0 - ramp(t, T_PAUSE, T_PAUSE + fr(6), 'out_cubic'))
        if fl > 0.003:
            K.draw(cv, C['stroke'], x, y, opacity=min(1.0, op * fl), mode='add')


@functools.lru_cache(maxsize=16)
def tag_sprite(lines, state=None):
    """Tag block: jw_mono 44 IVORY lines on a SMOKE scrim pill (alpha 0.55, r 10, pad 14). state 'ON' / 'OFF' gives
    tag 12 with its tinted suffix. -> (sprite, (ax, ay) = text left-middle in sprite px, text w, text h)."""
    pad, M, pitch = 14, 24, 52.0
    if state is not None:
        lines = ('12 · finish  %s' % state,)
    sts = [T.render(s, 'jw_mono', px=44, fill=('IVORY', 0.92)) for s in lines]
    tw = max(T.measure(s, 'jw_mono', px=44)[0] for s in lines)
    th = 32.12 + pitch * (len(lines) - 1)
    pw, ph = int(math.ceil(tw + 2 * pad)), int(math.ceil(th + 2 * pad))
    a = K.rrect_alpha(pw, ph, 10, M) * 0.55
    spr = np.zeros(a.shape + (4,), np.float32)
    spr[..., :3] = lin('SMOKE') * a[..., None]
    spr[..., 3] = a
    x0, ymid = M + pad, M + ph / 2.0
    for i, s in enumerate(lines):
        y = ymid + (i - (len(lines) - 1) / 2.0) * pitch
        if state is None:
            sts[i].draw(spr, x0, y, anchor=(0, 0.5))
        else:
            pre = '12 · finish  '
            wall = T.measure(pre + state, 'jw_mono', px=44)[0]
            wst = T.measure(state, 'jw_mono', px=44)[0]
            T.render(pre.rstrip(), 'jw_mono', px=44, fill=('IVORY', 0.92)).draw(spr, x0, y, anchor=(0, 0.5))
            col = ('FLAME', 1.25) if state == 'ON' else ('ASH', 1.0)
            T.render(state, 'jw_mono', px=44, fill=col).draw(spr, x0 + wall - wst, y, anchor=(0, 0.5))
    return _ro(spr), (float(x0), float(ymid)), float(tw), float(th)


@functools.lru_cache(maxsize=1)
def reticle():
    r = K.ring(7.0, 2.0, lin('FLAME', 1.8))
    return _ro(K.glow(r, K.C['FLAME'], sigmas=(3, 8), strength=0.6))


def add_line(cv, p0, p1, col, thick=1.5, opacity=1.0):
    """Anti-aliased emissive line (screen space)."""
    if opacity <= 0:
        return
    x0 = int(max(0, math.floor(min(p0[0], p1[0])) - 4))
    y0 = int(max(0, math.floor(min(p0[1], p1[1])) - 4))
    x1 = int(min(K.W, math.ceil(max(p0[0], p1[0])) + 5))
    y1 = int(min(K.H, math.ceil(max(p0[1], p1[1])) + 5))
    if x1 <= x0 or y1 <= y0:
        return
    m = np.zeros((y1 - y0, x1 - x0), np.uint8)
    s = 16.0
    a = (int(round((p0[0] - x0) * s)), int(round((p0[1] - y0) * s)))
    b = (int(round((p1[0] - x0) * s)), int(round((p1[1] - y0) * s)))
    cv2.line(m, a, b, 255, max(1, int(round(thick))), cv2.LINE_AA, 4)      # AA needs an 8-bit target
    k = float(thick) / max(1, int(round(thick))) / 255.0
    cv[y0:y1, x0:x1, :3] += m.astype(np.float32)[..., None] * (np.asarray(col, np.float32) * np.float32(k * opacity))


def tag_block_times():
    """[(t_in, t_out_end, pane, lines)] per HANDOFF 3.2 (tag 12: 12.0 -> 15.9)."""
    out = []
    for n, (f, k, lines) in enumerate(TAGS):
        t_in = fr(f)
        if k == 12:
            t_out = 15.9
        elif n + 2 < len(TAGS):
            t_out = fr(TAGS[n + 2][0])
        else:
            t_out = 12.2
        out.append((t_in, t_out, k, lines))
    return out


TAG_BLOCKS = tag_block_times()


def tag12_state(t):
    f = fi(t)
    if f < 396:
        return 'ON'
    if f < 405 or 422 <= f < 446:
        return 'OFF'
    return 'ON'


def pane12_hidden(t):
    f = fi(t)
    return 396 <= f < 405 or 422 <= f < 446


# frame-px keep-out boxes of the frame's own content (pane: boxes): tags avoid covering them
KEEP_OUT = {3: [(754, 1062, 870, 1178), (796, 296, 876, 364)], 4: [(172, 925, 634, 1600)],
            8: [(293, 441, 787, 501), (386, 854, 694, 915)], 9: [(262, 564, 819, 716)], 11: [(220, 780, 860, 802)]}


def _tag_offset_cands(k, tw, th):
    (ax, ay), (ox, oy) = TAG_ANCHOR[k]
    return [(ox, oy), (ox, -oy if oy < 0 else oy + 60), (-abs(ox) - tw, oy), (-tw / 2, -abs(oy) - 40 - th / 2),
            (-tw / 2, abs(oy) + 40 + th / 2), (ox, oy - 70), (ox, oy + 70)]


@functools.lru_cache(maxsize=32)
def tag_offset(k):
    """Screen offset (reticle -> text left-middle) of tag k, chosen ONCE from the arrival-frame camera: the brief's
    offset unless the tag would cover the frame's own copy / JD there (or need a large clamp); then the candidate
    with the least overlap (right, mirrored, left, above, below)."""
    if k == 12:                                         # tag 12 lives in the frontal re-hook view: BRIEF 8 box
        return TAG_ANCHOR[12][1]
    t_in = [b[0] for b in TAG_BLOCKS if b[2] == k][0]
    lines = [b[3] for b in TAG_BLOCKS if b[2] == k][0]
    cam, gap = stack_cam(t_in)
    tw, th = tag_sprite(lines, 'ON' if k == 12 else None)[2:4]
    (ax, ay), _ = TAG_ANCHOR[k]
    xy, _ = cam.project(np.array([[ax - 540.0, ay - 960.0, zk(k, gap)]]))
    rx, ry = float(xy[0, 0]), float(xy[0, 1])
    boxes = []
    for pk, bl in KEEP_OUT.items():
        for (x0, y0, x1, y1) in bl:
            P = np.array([[x - 540.0, y - 960.0, zk(pk, gap)] for x in (x0, x1) for y in (y0, y1)])
            q, _ = cam.project(P)
            if np.isfinite(q).all():
                boxes.append((q[:, 0].min(), q[:, 1].min(), q[:, 0].max(), q[:, 1].max()))
    best = None
    for n, (ox, oy) in enumerate(_tag_offset_cands(k, tw, th)):
        x, y = _clamp_tag(rx + ox, ry + oy, tw, th)
        bx0, by0, bx1, by1 = x - TAG_PAD, y - th / 2 - TAG_PAD, x + tw + TAG_PAD, y + th / 2 + TAG_PAD
        ov = sum(max(0.0, min(bx1, b[2]) - max(bx0, b[0])) * max(0.0, min(by1, b[3]) - max(by0, b[1])) for b in boxes)
        score = ov + 40.0 * math.hypot(x - rx - ox, y - ry - oy) + (0 if n == 0 else 500.0)
        if best is None or score < best[0]:
            best = (score, (ox, oy))
    return best[1]


def tag_pos(cam, gap, k):
    """Projected reticle and the (unclamped) text left-middle of tag k at the camera."""
    (ax, ay), _ = TAG_ANCHOR[k]
    ox, oy = tag_offset(k)
    xy, z = cam.project(np.array([[ax - 540.0, ay - 960.0, zk(k, gap)]]))
    rx, ry = float(xy[0, 0]), float(xy[0, 1])
    return rx, ry, rx + ox, ry + oy


def _clamp_tag(x, y, w, h):
    y = min(1440.0 - h / 2, max(250.0 + h / 2, y))
    xmax = (1010.0 if y + h / 2 < 1050 else 930.0) - w
    return min(xmax, max(80.0, x)), y


TAG_PAD, TAG_GAP = 14.0, 10.0


def _tag_natural(t, k, lines):
    """Clamped natural position of tag block k at t: (rx, ry, x, y, tw, th) (x, y = the text's left-middle)."""
    cam, gap = stack_cam(t)
    tw, th = tag_sprite(lines, 'ON' if k == 12 else None)[2:4]
    rx, ry, x, y = tag_pos(cam, gap, k)
    x, y = _clamp_tag(x, y, tw, th)
    return rx, ry, x, y, tw, th


@functools.lru_cache(maxsize=64)
def _pair_dir(ka, kb):
    """Side (+1 below / -1 above) on which the newer tag block kb keeps clear of the older ka: fixed per pair, from
    their natural positions on kb's arrival frame (no flip while both are on screen)."""
    ta = [b for b in TAG_BLOCKS if b[2] == kb][0]
    la = [b for b in TAG_BLOCKS if b[2] == ka][0]
    ya = _tag_natural(ta[0], ka, la[3])[3]
    yb = _tag_natural(ta[0], kb, ta[3])[3]
    return 1.0 if yb >= ya else -1.0


def tag_layout(t, cam, gap):
    """Visible tag blocks at t with their positions; a newer block is pushed vertically clear of an older one it
    overlaps (smoothly weighted by the horizontal overlap, so nothing jumps). -> [(k, lines, op, rx, ry, x, y, tw, th)]"""
    vis = []
    for (t_in, t_out, k, lines) in TAG_BLOCKS:
        if t < t_in - fr(1) or t >= t_out:
            continue
        fade = fr(4) if k == 12 else 0.2
        op = ramp(t, t_in - fr(1), t_in + fr(3), 'inout_sine') * (1.0 - ramp(t, t_out - fade, t_out, 'in_cubic'))
        tw, th = tag_sprite(lines, 'ON' if k == 12 else None)[2:4]
        rx, ry, x, y = tag_pos(cam, gap, k)
        x, y = _clamp_tag(x, y, tw, th)
        for (ka, _, _, _, _, xa, ya, twa, tha) in vis:
            hov = min(x + tw, xa + twa) - max(x, xa) + 2 * TAG_PAD + TAG_GAP
            w = K.smoothstep(-20.0, 20.0, hov)
            if w <= 0:
                continue
            d = _pair_dir(ka, k)
            need = (tha + th) / 2 + 2 * TAG_PAD + TAG_GAP
            ys = max(y, ya + need) if d > 0 else min(y, ya - need)
            y = y + (ys - y) * w
            y = min(1440.0 - th / 2, max(250.0 + th / 2, y))
        vis.append((k, lines, op, rx, ry, x, y, tw, th))
    return vis


def draw_tags(cv, t, cam, gap):
    for (k, lines, op, rx, ry, x, y, tw, th) in tag_layout(t, cam, gap):
        if op <= 0.002:
            continue
        t_in = [b[0] for b in TAG_BLOCKS if b[2] == k][0]
        spr, (ax, ay), tw, th = tag_sprite(lines, tag12_state(t) if k == 12 else None)
        if -20 < rx < K.W + 20 and -20 < ry < K.H + 20:
            bx0, by0 = x - TAG_PAD - 2, y - th / 2 - TAG_PAD - 2           # leader ends on the pill's nearest edge
            bx1, by1 = x + tw + TAG_PAD + 2, y + th / 2 + TAG_PAD + 2
            ex, ey = min(bx1, max(bx0, rx)), min(by1, max(by0, ry))
            if math.hypot(ex - rx, ey - ry) > 6:
                u = ramp(t, t_in - fr(1), t_in + fr(5), 'out_cubic')
                add_line(cv, (rx, ry), (rx + (ex - rx) * u, ry + (ey - ry) * u), lin('FLAME', 1.4), 1.5, op)
            K.draw(cv, reticle(), rx, ry, opacity=op)
        K.draw(cv, spr, x, y, anchor=(ax / spr.shape[1], ay / spr.shape[0]), opacity=op)
        if k == 5 and t >= fr(278):                     # the camera passes pane 06 (its tick): line 2 flares
            fl = 1.0 - ramp(t, fr(278), fr(278) + 0.35, 'out_cubic')
            if fl > 0.01:
                K.draw(cv, spr, x, y, anchor=(ax / spr.shape[1], ay / spr.shape[0]), opacity=op * 0.35 * fl, mode='add')
        if k == 12 and fi(t) >= 446:                    # resolved "with": the ON suffix sparkles once
            fl = 1.0 - ramp(t, fr(446), fr(446) + 0.5, 'out_cubic')
            if fl > 0.01:
                K.draw(cv, spr, x, y, anchor=(ax / spr.shape[1], ay / spr.shape[0]), opacity=op * 0.5 * fl, mode='add')


# --- counters
@functools.lru_cache(maxsize=1)
def counters():
    return dict(c12=T.Counter('jw_key', prefix='', decimals=0, sep='', min_int=2, px=230),
                layers=T.render('LAYERS', 'jw_caps', px=86),
                c360=T.Counter('jw_key', prefix='', decimals=0, sep='', min_int=3, px=240),
                l360=T.render('LAYERS · 1 SECOND', 'jw_caps', px=86),
                scrim=_scrim())


TR12 = K.Track([(3.0, 0, 'out_cubic'), (T_LAND, 12)])
TR360 = K.Track([(18.9, 12, 'inout_sine'), (T_360, 360)])


def _counter_reach(k):
    """Time the 00 -> 12 counter reaches k (out_cubic): seams of pane k light then."""
    x = 1.0 - (1.0 - k / 12.0) ** (1.0 / 3.0)
    return 3.0 + x * (T_LAND - 3.0)


T_LIT = {k: _counter_reach(k) for k in range(1, 13)}


def _scrim():
    """Soft NIGHT_0 elliptical scrim (alpha 0.5) for the 360 lockup, at half res (drawn x2)."""
    w, h = 560, 240
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    d = ((xx - w / 2 + 0.5) / (w / 2)) ** 2 + ((yy - h / 2 + 0.5) / (h / 2)) ** 2
    a = 0.5 * np.clip(1 - d, 0, 1) ** 1.6
    s = np.zeros((h, w, 4), np.float32)
    s[..., :3] = lin('NIGHT_0') * a[..., None]
    s[..., 3] = a
    return _ro(s)


def draw_counter12(cv, t):
    if t < 3.0 or t >= 6.15:
        return
    C = counters()
    uin = ramp(t, 3.0, fr(94), 'out_cubic')
    op = ramp(t, 3.0, fr(94), 'inout_sine') * (1.0 - ramp(t, 5.9, 6.15, 'in_cubic'))
    dy = 24.0 * (1 - uin) - 12.0 * ramp(t, 5.9, 6.15, 'in_cubic')
    if op <= 0:
        return
    C['c12'].draw(cv, TR12(t), 540.0, 380.0 + dy, vel=TR12.vel(t), opacity=op)
    C['layers'].draw(cv, 540.0, 518.0 + dy, opacity=op)


def draw_counter360(cv, t):
    if t < 18.9 or t >= fr(667):                        # HANDOFF: exit f660-f667, gone ON f667
        return
    C = counters()
    op = ramp(t, 18.9, fr(571), 'inout_sine') * (1.0 - ramp(t, 22.0, fr(667), 'in_cubic'))
    if op <= 0:
        return
    K.draw(cv, C['scrim'], 540.0, 430.0, scale=2.0, opacity=op)
    C['c360'].draw(cv, TR360(t), 540.0, 380.0, vel=TR360.vel(t), opacity=op)
    C['l360'].draw(cv, 540.0, 520.0, opacity=op)


# --- seams, spill, seam glint (annotation)
@functools.lru_cache(maxsize=1)
def spill():
    return _ro(K.radial(256, lin('FLAME', 0.06), power=1.6))


def seam_lit(k, t):
    tk = T_LIT[k]
    if t < tk:
        return 0.0
    return 0.4 + 1.4 * (1.0 - ramp(t, tk, tk + 0.3, 'out_cubic'))


def draw_seams(cv, cam, gap, t, hide12=False):
    """Each pane's outline projected per frame, 2 px at half res, ASH x0.22 + FLAME x0.12 (+ the counter's lit
    flare), blurred by the pane's CoC; opacity smoothstep(40, 100, gap)."""
    op = K.smoothstep(40.0, 100.0, gap)
    if op <= 0.002:
        return
    base = lin('ASH', 0.22) + lin('FLAME', 0.12)
    bins = {}
    for i in range(1, 13):
        if i == 12 and hide12:
            continue
        P = stack_corners(gap, only=(i,))
        xy, z = cam.project(P)
        if not np.isfinite(xy).all():
            continue
        coc = cam.coc(max(1.0, cam.depth((0.0, 0.0, zk(i, gap))))) if cam.aperture > 0 else 0.0
        sig = min(16.0, 0.25 * coc)
        b = 0 if sig < 0.75 else (1 if sig < 2.5 else (2 if sig < 6 else 3))
        col = (base + lin('FLAME') * seam_lit(i, t)) * op
        bins.setdefault(b, []).append((xy * 0.5, col))
    if not bins:
        return
    h2, w2 = K.H // 2, K.W // 2
    acc = np.zeros((h2, w2, 3), np.float32)
    for b, items in bins.items():
        lay = np.zeros_like(acc)
        for xy2, col in items:
            x0 = int(max(0, math.floor(xy2[:, 0].min()) - 3))
            y0 = int(max(0, math.floor(xy2[:, 1].min()) - 3))
            x1 = int(min(w2, math.ceil(xy2[:, 0].max()) + 4))
            y1 = int(min(h2, math.ceil(xy2[:, 1].max()) + 4))
            if x1 <= x0 or y1 <= y0:
                continue
            m = np.zeros((y1 - y0, x1 - x0), np.uint8)
            pts = np.round((xy2 - (x0, y0)) * 16).astype(np.int32).reshape(-1, 1, 2)
            cv2.polylines(m, [pts], True, 255, 1, cv2.LINE_AA, 4)              # AA needs an 8-bit target
            lay[y0:y1, x0:x1] += m.astype(np.float32)[..., None] * (col / np.float32(255.0))
        if b:
            lay = cv2.GaussianBlur(lay, (0, 0), (0, 1.2, 3.0, 7.0)[b])
        acc += lay
    cv[..., :3] += cv2.resize(acc, (K.W, K.H), interpolation=cv2.INTER_LINEAR)


def draw_spill(cv, cam, gap, k, z0=0.0):
    """One K.radial FLAME x0.06 behind the stack, centred on its projected bbox, 1.4 x its height."""
    x0, y0, x1, y1 = _bbox(cam, stack_corners(gap, z0))
    h = max(1.0, y1 - y0)
    if k > 0.003:
        s = spill()
        K.draw(cv, s, (x0 + x1) / 2, (y0 + y1) / 2, scale=1.4 * h / s.shape[0], opacity=k, mode='add')


def glint_k(t):
    """Seam glint intensity: x1.6 under the sweep 0.6-0.9, decaying to x0.35 by 1.2, then out by 2.4."""
    if t < 0.6:
        return 0.0
    if t < 0.9:
        return 1.6
    return (1.6 + (0.35 - 1.6) * ramp(t, 0.9, 1.2, 'out_cubic')) * (1.0 - ramp(t, 1.2, 2.4, 'inout_sine'))


def draw_glint_flat(cv, t):
    k = glint_k(t)
    if k <= 0:
        return
    m = X.sweep_mask(ease('out_cubic', (t - 0.6) / 0.3), angle=35.0) if t < 0.9 else None
    for i, (e, cx, cy, w) in panes()['edges'].items():
        h = e.shape[0]
        x0, y0 = int(round(cx + 540 - w / 2)), int(round(cy + 960 - h / 2))
        sub = e[..., :3] * np.float32(k / 1.6)
        if m is not None:
            sub = sub * m[y0:y0 + h, x0:x0 + int(w), None]
        cv[y0:y0 + h, x0:x0 + int(w), :3] += sub


def draw_glint_planes(cv, cam, gap, t):
    k = glint_k(t)
    if k <= 0.003:
        return
    for i, (e, cx, cy, w) in panes()['edges'].items():
        K.draw_plane(cv, e, cam, (cx, cy, zk(i, gap)), w, dof=False, opacity=min(1.0, k / 1.6), mode='add')


# ============================================================================================ scenes
def void():
    cv = np.empty((K.H, K.W, 4), np.float32)
    cv[..., :3] = lin('NIGHT_0', 0.6)
    cv[..., 3] = 1.0
    return cv


def draw_stack(cv, cam, gap, z0=0.0, hide12=False, dof=True):
    """The 12 frame planes (exactly 12 frame draws; 11 while pane 12 is flicked OFF), back to front."""
    P = panes()['P']
    n = 0
    for i in range(1, 13):
        if i == 12 and hide12:
            continue
        c = (0.0, 0.0, z0 + zk(i, gap))
        d = max(1.0, cam.depth(c))
        coc = cam.coc(d) if cam.aperture > 0 else 0.0
        use = dof and coc > 2.5
        op = 1.0 - 0.55 * K.smoothstep(25.0, 70.0, coc) if (use and d < cam.focus_dist) else 1.0
        K.draw_plane(cv, P[i], cam, c, 1080.0, dof=use, opacity=op)
        n += 1
    return n


def S_STACK(t):
    """S1 + S2 (0-16.8; t < 0 = the loop's playing frame): playing / paused-flat / exploded stack + HUD."""
    if t + HALF < T_PAUSE:                              # playing, assembled (hook lock), chip > (frames 0-8)
        cv = draw_frame(min(t, T_PAUSE), 'hook')
        draw_chip(cv, t)
        return cv
    if t < 0.9:                                         # paused, gap 0, 1:1: the flat composite
        cv = np.array(panes()['flat'], copy=True)
        draw_glint_flat(cv, t)
        draw_chip(cv, t)
        return cv
    cam, gap = stack_cam(t)
    cv = void()
    draw_spill(cv, cam, gap, ramp(t, 0.9, 1.6, 'inout_sine'))
    hide = pane12_hidden(t)
    draw_stack(cv, cam, gap, hide12=hide)
    draw_glint_planes(cv, cam, gap, t)
    draw_seams(cv, cam, gap, t, hide12=hide)
    draw_chip(cv, t)
    draw_counter12(cv, t)
    if 6.6 <= t < 15.95:
        draw_tags(cv, t, cam, gap)
    return cv


# --- corridor
BB = [((-600.0 if j % 2 == 0 else 600.0), 0.0, 900.0 + 330.0 * j) for j in range(29)]


def _bb_state(j, t):
    """(pos, opacity, flare) of billboard j at t (light wave 16.9 + j x 0.0607; rush in_expo to 25.5)."""
    p0 = BB[j]
    tj = 16.9 + j * 0.0607
    flare = 0.6 * ramp(t, tj - fr(2), tj, 'inout_sine') * (1.0 - ramp(t, tj, tj + 0.4, 'out_cubic'))
    if t < 24.0:
        return p0, 1.0, flare
    t0 = 24.0 + 0.02 * (28 - j)
    u = ease('in_expo', (t - t0) / (25.5 - t0)) if t > t0 else 0.0
    pos = (p0[0] * (1 - u), p0[1] * (1 - u), p0[2] + (LIVE_Z - p0[2]) * u)
    op = 1.0 - ramp(t, 25.5 - fr(4), 25.5, 'linear')
    return pos, op, 0.0


@functools.lru_cache(maxsize=1)
def envelopes():
    """RMS dBFS per reel frame for the three lanes: <RW>/audio/ek_frame_ki_keemat_env.json when the mix stage has
    written it; else the VO from vo_stem.wav and PLACEHOLDER sfx / music envelopes (warned)."""
    n = int(round(DUR * FPS)) + 240
    if os.path.exists(ENV_JSON):
        try:
            d = json.load(open(ENV_JSON))
            out = {}
            for k in ('vo', 'sfx', 'music'):
                v = np.asarray(d[k], np.float32)
                out[k] = np.pad(v, (0, max(0, n - len(v))), constant_values=-90.0)[:n]
            out['placeholder'] = False
            return out
        except (OSError, ValueError, KeyError):
            pass
    out = {'placeholder': True}
    try:
        import scipy.io.wavfile as wf
        sr, x = wf.read(VO_WAV)
        x = x.astype(np.float64) / (float(2 ** 31) if np.issubdtype(x.dtype, np.integer) else 1.0)
        if x.ndim > 1:
            x = x.mean(1)
        hop = sr // FPS
        m = len(x) // hop
        rms = np.sqrt(np.mean(x[:m * hop].reshape(m, hop) ** 2, axis=1) + 1e-12)
        vo = 20 * np.log10(rms)
    except Exception:                                   # noqa: BLE001
        vo = np.full(n, -90.0)
    out['vo'] = np.pad(vo, (0, max(0, n - len(vo))), constant_values=-90.0)[:n].astype(np.float32)
    tt = np.arange(n) / FPS
    rng = np.random.default_rng(7)
    b8 = (tt % (BEAT / 2)) / (BEAT / 2)
    bt = (tt % BEAT) / BEAT
    out['music'] = (-30.0 + 9.0 * np.exp(-bt * 5.0) + 4.0 * np.exp(-b8 * 7.0) + 3.0 * rng.standard_normal(n)
                    ).astype(np.float32)
    sfx = np.full(n, -60.0) + 2.0 * rng.standard_normal(n)
    hits = [v for v in SFX_EVENTS.values() for v in (v if isinstance(v, (tuple, list)) else (v,))]
    hits += [22.2 + 0.3 * i for i in range(8)] + [19.2, 19.8, 24.3, 24.75, 25.2]
    for tv in hits:
        sfx = np.maximum(sfx, -10.0 - 36.0 * np.clip((tt - tv) / 0.45, 0, 1) - 200.0 * (tt < tv))
    out['sfx'] = sfx.astype(np.float32)
    return out


LANE_X = (-260.0, 0.0, 260.0)
LANE_KEYS = ('vo', 'sfx', 'music')
LANE_COLS = ('FLAME', 'AMBER', 'RED')
LANE_LABELS = ('VO · AI voice', 'SFX', 'MUSIC')


def _lane_now_z(cam, y, z_near):
    """Lane depth whose centre projects to screen y 1850 (the playhead, the visible near end)."""
    lo, hi = z_near, 9770.0
    for _ in range(24):
        mid = (lo + hi) / 2
        xy, _ = cam.project(np.array([[0.0, y, mid]]))
        if not np.isfinite(xy[0, 1]) or xy[0, 1] > 1850.0:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


def _lane_tex(env, t, z0, z1, znow, col, rows=512, cols=96):
    d = (np.arange(rows, dtype=np.float32) + 0.5) / rows * (z1 - z0) + z0
    tf = t * FPS + (d - znow) / 30.0                   # 30 world units per audio frame, the near end = now
    idx = np.clip(np.round(tf).astype(int), 0, len(env) - 1)
    amp = np.clip((env[idx] + 54.0) / 48.0, 0, 1) * (tf >= 0)
    hw = amp * (cols / 2 - 6)
    dc = np.abs(np.arange(cols, dtype=np.float32) + 0.5 - cols / 2)
    m = np.clip(hw[:, None] - dc[None, :] + 0.5, 0, 1)
    past = np.where(d < znow, 0.45, 1.0).astype(np.float32)[:, None]
    tex = np.zeros((rows, cols, 4), np.float32)
    tex[..., :3] = lin('SMOKE', 0.6 * 0.7)
    tex[..., 3] = 0.7
    tex[..., :3] += (m * past)[..., None] * lin(col, 1.6)
    return tex


def draw_lanes(cv, cam, t, zcam):
    lift = ramp(t, fr(666), 22.5, 'out_cubic') * (1.0 - ramp(t, fr(729), 24.6, 'in_cubic'))
    if lift <= 0.002:
        return
    y = 900.0 - 280.0 * lift
    z0, z1 = zcam + 400.0, 9770.0
    if z1 - z0 < 200:
        return
    znow = _lane_now_z(cam, y, z0)
    env = envelopes()
    for i, key in enumerate(LANE_KEYS):
        tex = _lane_tex(env[key], t, z0, z1, znow, LANE_COLS[i])
        K.draw_plane(cv, tex, cam, (LANE_X[i], y, (z0 + z1) / 2), 180.0, rot=(90.0, 0.0, 0.0), height=z1 - z0,
                     dof=False, opacity=min(1.0, lift * 1.2))
    a, _ = cam.project(np.array([[LANE_X[0] - 90.0, y, znow], [LANE_X[2] + 90.0, y, znow]]))
    if np.isfinite(a).all():
        add_line(cv, tuple(a[0]), tuple(a[1]), lin('RED', 1.6), 3.0, lift)


@functools.lru_cache(maxsize=1)
def legend():
    out = []
    for lab, col in zip(LANE_LABELS, LANE_COLS):
        sw = np.zeros((22, 22, 4), np.float32)
        a = K.rrect_alpha(22, 22, 4)
        sw[..., :3] = lin(col, 1.2) * a[..., None]
        sw[..., 3] = a
        out.append((_ro(sw), T.render(lab, 'jw_mono', px=40, fill=('IVORY', 0.92))))
    return out


LEGEND_Y = (590.0, 640.0, 690.0)       # r3 deviation: BRIEF's y 1330-1440 crossed JD's face on the live stack (x 376-553)
LEGEND_BOX = (80, 570, 480, 710)


def draw_legend(cv, t):
    op = ramp(t, fr(666), 22.4, 'inout_sine') * (1.0 - ramp(t, fr(729), 24.6, 'in_cubic'))
    if op <= 0.002:
        return
    for (sw, lab), y in zip(legend(), LEGEND_Y):
        K.draw(cv, sw, 90.0, y, anchor=(0, 0.5), opacity=op)
        lab.draw(cv, 122.0, y, anchor=(0, 0.5), opacity=op)


def S_CORR(t):
    """S3 (16.8-26.4; also rendered inside the C3 iris from 16.0): the 30-frame corridor."""
    cam = corr_cam(max(t, 16.8))
    gap = corr_gap(t)
    cv = void()
    spr = stack_flat()
    draw_spill(cv, cam, gap, 1.0, z0=LIVE_Z)
    items = []
    if t < 25.5:
        for j in range(29):
            pos, op, flare = _bb_state(j, t)
            if op <= 0.002:
                continue
            d = cam.depth(pos)
            if d < 60:
                continue
            op *= min(1.0, max(0.15, (9500.0 - d) / 4000.0))
            kr = ramp(t, 24.0, 24.4, 'inout_sine')         # rush: a stack flying through the lens would fill the
            if kr > 0:                                      # screen (black / busy frames): fade it near the camera
                op *= 1.0 - kr * (1.0 - K.smoothstep(250.0, 1200.0, d))
            items.append((d, 'bb', (pos, op, flare)))
    live_d = cam.depth((0.0, 0.0, LIVE_Z))
    lb = _bbox(cam, stack_corners(gap, LIVE_Z))
    kf = ramp(t, 19.8, 20.6, 'inout_sine') * (1.0 - ramp(t, 24.0, 24.6, 'inout_sine'))
    if kf > 0:
        for n, (d, kind, data) in enumerate(items):
            pos, op, flare = data
            if d >= live_d:
                continue
            q, _ = cam.project(np.array([[pos[0] - 410.0, pos[1], pos[2]], [pos[0] + 410.0, pos[1], pos[2]]]))
            if not np.isfinite(q).all():
                continue
            ov = (min(q[:, 0].max(), lb[2]) - max(q[:, 0].min(), lb[0])) / max(1.0, lb[2] - lb[0])
            items[n] = (d, kind, (pos, op * (1.0 - 0.8 * kf * K.smoothstep(0.0, 0.25, ov)), flare))
    items.append((live_d, 'live', None))
    items.sort(key=lambda r: -r[0])
    for d, kind, data in items:
        if kind == 'bb':
            pos, op, flare = data
            K.draw_billboard(cv, spr, cam, pos, 820.0, opacity=op, dof=False)
            if flare > 0.003:
                K.draw_billboard(cv, spr, cam, pos, 820.0, opacity=min(1.0, op * flare), mode='add', dof=False)
        else:
            draw_stack(cv, cam, gap, z0=LIVE_Z, dof=False)
    zc = _corr_pose(max(t, 16.8))[0]
    draw_lanes(cv, cam, t, zc)
    draw_counter360(cv, t)
    draw_legend(cv, t)
    return cv


def S_PLAY(t):
    """S4 (26.4-33.6): the frame PLAYING again (pay lock to 29.45, then the plain playing frame under the card)."""
    return draw_frame(t - DUR, 'pay' if t < 29.45 else None)       # tl = t - 33.6 on every sub-sample (C8 HALF)


def world(t):
    return PLAN.draw(t, [S_STACK, S_CORR, S_PLAY])


# ============================================================================================ captions + card
def _words(t0, t1):
    ws = SC.load_words(WORDS)
    return [w for w in ws if t0 <= w['start'] < t1]


def live_face_rect(t, m=10.0):
    """Screen box of JD's face on the corridor's live stack (pane 04, frame px 242-564 x 1120-1564) at t."""
    cam, gap = corr_cam(max(t, 16.8)), corr_gap(t)
    P = np.array([[x - 540.0, y - 960.0, LIVE_Z + zk(4, gap)] for x in (242.0, 564.0) for y in (1120.0, 1564.0)])
    xy, _ = cam.project(P)
    return (float(xy[:, 0].min() - m), float(xy[:, 1].min() - m), float(xy[:, 0].max() + m), float(xy[:, 1].max() + m))


@functools.lru_cache(maxsize=1)
def captions():
    c1 = SC.Captions(_words(12.0, 16.25), band='upper', y=420, hold=0.15, max_words=3, clear=[(16.25, 16.9)],
                     avoid=lambda t: [stack_rect(max(t, 13.2)), (245, 565, 715, 635)])
    c2 = SC.Captions(_words(16.9, 20.5), band='lower', hold=0.15, max_words=3, clear=[(20.6, 22.3)],
                     avoid=lambda t: ([(100, 280, 980, 560)] if t >= 18.9 else []) + [live_face_rect(t)])
    c3 = SC.Captions(_words(22.1, 24.7), band='upper', y=420, hold=0.15, max_words=3, avoid=[LEGEND_BOX])
    return (c1, c2, c3)


CARD_DUR = 4.0          # r3 deviation (HANDOFF: 4.2, exit 33.24-33.6): the card's type now fades 32.94-33.27 (CARD_OUT,
CARD_OUT = (32.94, fr(998))   # through EndCard.draw's opacity) and the loop crossfade is 33.15-33.6, so the card no
LOOP_D = 0.45           # longer sits on top of the returning hook lockup; hold 31.25-32.94 = 1.69 s (>= 1.5)


@functools.lru_cache(maxsize=1)
def card():
    return E.EndCard(CTA, 'bhejo', sub='jo kehta hai "editing mein kya hai?"', handle=False, monogram='JD',
                     dur=CARD_DUR, y_mono=365.0, y_key=715.0, y_sub=922.0)


def draw(t):
    cv = E.loop_world(world, t, DUR, d=LOOP_D)
    if 11.9 <= t < 24.9:
        for cap in captions():
            cap.draw(cv, t)
    if t >= T_CARD:
        out = 1.0 - ramp(t, CARD_OUT[0], CARD_OUT[1], 'inout_sine')
        card().draw(cv, t, T_CARD, opacity=out)
        op = ramp(t, 30.4, 30.85, 'inout_sine') * out
        if op > 0:
            J.signature(cv, 760.0, 1575.0, opacity=op)
    return cv


def post(cv, t):
    kw = dict(PLAN.post_kw(t))
    for k, v in card().post_kw(t, T_CARD, DUR).items():
        if k == 'push':
            kw['push'] = kw.get('push', 0.0) + v
        elif k == 'bloom_scale':
            kw[k] = kw.get(k, 1.0) * v
        else:
            kw[k] = v
    return G.tx_finish(cv, t, LOOK, cuts=CUTS, **kw)


def _base_samples(t):
    if t < 0.9:
        return 2
    if t < 5.9:
        return 5 if 3.3 <= t < 4.6 else 3
    if t < 6.8:
        return 7
    if t < 13.2:
        return 5
    if t < 16.8:
        return 2
    if t < 18.6:
        return 3
    if t < T_360:
        return 7
    if t < 24.0:
        return 2
    if t < 25.6:
        return 7
    return 2


def samples(t):
    return PLAN.samples(t, default=_base_samples(t))


def cues():
    return []                                       # the sfx module builds the stems from SFX_EVENTS


def prewarm():
    assets()
    FF.prewarm()
    panes()
    stack_flat()
    chip()
    counters()
    reticle()
    legend()
    spill()
    envelopes()
    for _, _, k, lines in TAG_BLOCKS:
        if k == 12:
            tag_sprite(None, 'ON')
            tag_sprite(None, 'OFF')
        else:
            tag_sprite(lines)
    for cap in captions():
        cap.prewarm()
    card()


# ============================================================================================ dev: text blocks + selftest
def text_blocks(t):
    """Designed text blocks being read at t (analytic registry for the <= 2 blocks rule; a block that has started
    its exit no longer counts, BRIEF 17.5): [(name, box)]."""
    out = []
    if t < 0.9:
        out.append(('hook lockup', (262, 441, 819, 915)))
    if 0 <= t < fr(24):
        out.append(('chip', (595, 1246, 925, 1318)))
    if 3.0 <= t < 5.9:
        out.append(('counter 12', (373, 297, 708, 548)))
    for (t_in, t_out, k, lines) in TAG_BLOCKS:
        if t_in <= t < t_out - (fr(4) if k == 12 else 0.2):
            out.append(('tag %02d' % k, None))
    for i, cap in enumerate(captions()):
        for ch in cap.chunks:
            if getattr(ch, 'cleared', None) == 'skipped':
                continue
            if ch.t_in <= t < ch.t_exit0:
                out.append(('caption C%d' % (i + 1), None))
    if 18.9 <= t < 22.0:
        out.append(('360 lockup', (108, 294, 972, 550)))
    if fr(666) <= t < fr(729):
        out.append(('lane legend', LEGEND_BOX))
    if T_PLAY <= t < 29.1:
        out.append(('payoff lockup', (200, 441, 880, 915)))
    if T_CARD <= t < CARD_OUT[0]:
        out.append(('end card', None))
    return out


def selftest():
    import time
    ok = True
    log = []

    def check(name, cond, info=''):
        nonlocal ok
        ok &= bool(cond)
        log.append('%s %s %s' % ('PASS' if cond else 'FAIL', name, info))

    t0 = time.time()
    check('len(FRAME) == 12', len(FRAME) == 12)
    check('grid 14 bars = DUR', abs(GRID.at(14) - DUR) < 1e-9 and GRID.fpb == 18)
    # camera numbers (BRIEF 7.3, re-measured)
    def bb(t):
        cam, gap = stack_cam(t)
        return _bbox(cam, stack_corners(gap))
    b = bb(2.4 - 1e-9)
    check('P2 end bbox ~ (220, 597, 860, 1736)', abs(b[0] - 219.6) < 3 and abs(b[1] - 596.8) < 3 and abs(b[3] - 1736) < 3,
          str(np.round(b, 1)))
    b = bb(T_LAND)
    check('P3 end bbox ~ (125, 600, 956, 1649)', abs(b[0] - 125.4) < 2 and abs(b[3] - 1648.7) < 2, str(np.round(b, 1)))
    b = bb(13.2)
    check('P7 end bbox ~ (199, 547, 881, 1761)', abs(b[0] - 198.6) < 1 and abs(b[1] - 546.8) < 1, str(np.round(b, 1)))
    b = bb(16.0)
    check('P8 16.0 bbox x 172-908, y 514-1824 (+-2)', abs(b[0] - 172) <= 2 and abs(b[2] - 908) <= 2 and abs(b[1] - 514) <= 2
          and abs(b[3] - 1824) <= 2, str(np.round(b, 1)))
    check('C3 disc centre within 0.5 px of (719.4, 1267.5), r 38.2', abs(_C3_PROJ[0] - 719.4) <= 0.5 and
          abs(_C3_PROJ[1] - 1267.5) <= 0.5 and abs(_C3_R - 38.2) <= 0.5,
          'proj (%.2f, %.2f) r %.2f -> center %s r0 %s' % (_C3_PROJ[0], _C3_PROJ[1], _C3_R, C3_CENTER, C3_R0))
    # counter clear of the stack 3.0-5.9
    ymin = min(bb(3.0 + k / 30.0)[1] for k in range(0, int(2.9 * 30)))
    check('counter (y <= 548) clear of the stack 3.0-5.9', ymin > 560, 'stack top min y %.1f' % ymin)
    # push continuity 13.2-16.0
    sc = [1.0 / (1 - push_p(13.2 + k / 30.0)) for k in range(0, 85)]
    steps = [abs(sc[i + 1] / sc[i] - 1) for i in range(len(sc) - 1)]
    check('P8 push: no per-frame scale step > 0.2 %', max(steps) < 0.002, 'max %.3f %%' % (100 * max(steps)))
    aps = [stack_pose(t)[0][7] for t in (14.9, 14.99, 15.8, 15.9, 16.0)]
    check('rack aperture 0 before 15.0, 900 from 15.8', aps[0] == 0 and aps[1] == 0 and abs(aps[2] - 900) < 1e-6
          and abs(aps[4] - 900) < 1e-6, str(aps))
    # hidden-JD gain incl. sub-samples
    bad = []
    for f in range(0, 1008):
        for s in (-0.25, 0.0, 0.25):
            t = (f + s) / 30.0
            g = glint_gain(layer_clock(t))
            want = 1.20 if f == 846 else (0.70 if f == 847 else 0.35)
            if abs(g - want) > 1e-9:
                bad.append((f, s, g))
    check('hidden-JD gain 0.35 except f846 1.20 / f847 0.70', not bad, str(bad[:4]))
    # fly-through arrivals: the camera reaches each pane at its frame
    worst = 0.0
    for f, k in ARR:
        pose = stack_pose(fr(f))[0]
        tgt = _fly(k, 300.0)
        worst = max(worst, max(abs(a - c) for a, c in zip(pose[:3], tgt[:3])))
    check('fly-through arrivals land on their panes', worst < 1e-6, 'max err %.2g' % worst)
    # camera snaps (stack + corridor): projected frame centre per frame
    def snaps(fn, f0, f1, P=(0.0, 0.0, 0.0)):
        xy = []
        for f in range(f0, f1):
            cam = fn(f / 30.0)
            xy.append(cam.project(np.array([P]))[0][0])
        xy = np.array(xy)
        d = np.linalg.norm(np.diff(xy, axis=0), axis=1)
        return [f0 + i for i in range(1, len(d) - 1) if d[i] > 3 * max(d[i - 1], d[i + 1], 2.0)]
    s1 = snaps(lambda t: stack_cam(t)[0], 27, 480)
    s2 = snaps(corr_cam, 504, 792, (0.0, 0.0, LIVE_Z))
    check('no camera snaps (stack f27-479, corridor f504-791)', not s1 and not s2, 'stack %s corridor %s' % (s1, s2))
    # end card
    c = card()
    hold = CARD_OUT[0] - (T_CARD + c.settle)
    check('end card hold >= 1.5 s', hold >= 1.5 and c.hold >= 1.5, 'hold %.2f s (%.2f-%.2f)' % (hold, T_CARD + c.settle,
                                                                                            CARD_OUT[0]))
    # text blocks <= 2 per frame (the loop's 33.0-33.6 lockup + chip are frame 0 coming back: not counted)
    over = [f for f in range(0, 990) if len(text_blocks(f / 30.0)) > 2]
    check('<= 2 text blocks per frame (f0-f989)', not over, str(over[:10]))
    # safe zones of the fixed boxes
    boxes = [('counter', (373, 297, 708, 548)), ('360', (108, 294, 972, 550)), ('legend', LEGEND_BOX),
             ('signature', (631, 1563, 889, 1587))]
    bad = [n for n, (x0, y0, x1, y1) in boxes if x0 < 70 or x1 > 1010 or y0 < 230 or y1 > 1620 or (x1 > 930 and y1 > 1050
                                                                                                     and y0 < 1700)]
    check('fixed text boxes inside the safe zones', not bad, str(bad))
    # tags: clamped boxes inside the safe zone every frame
    worst = 1e9
    overlaps = []
    for f in range(198, 478):
        t = f / 30.0
        cam, gap = stack_cam(t)
        lay = tag_layout(t, cam, gap)
        for (k, lines, op, rx, ry, x, y, tw, th) in lay:
            x0, y0, x1, y1 = x, y - th / 2, x + tw, y + th / 2
            lim = 930 if y1 >= 1050 else 1010
            worst = min(worst, x0 - 70, lim - x1, y0 - 230, 1480 - y1)
        for i in range(len(lay)):
            for j in range(i + 1, len(lay)):
                a, b = lay[i], lay[j]
                if min(a[2], b[2]) < 0.05:
                    continue
                ox = min(a[5] + a[7], b[5] + b[7]) - max(a[5], b[5]) + 2 * TAG_PAD
                oy = min(a[6] + a[8] / 2, b[6] + b[8] / 2) - max(a[6] - a[8] / 2, b[6] - b[8] / 2) + 2 * TAG_PAD
                if ox > 0 and oy > 0:
                    overlaps.append((f, a[0], b[0], round(min(ox, oy), 1)))
    check('tag text boxes inside the safe zones (worst margin >= 0)', worst >= 0, 'worst margin %.1f px' % worst)
    check('tag pills never overlap (both > 5 % opaque)', not overlaps, str(overlaps[:6]))
    # captions
    for i, cap in enumerate(captions()):
        r = cap.check()
        check('caption C%d check() == []' % (i + 1), r == [], str(r)[:300])
    rep = [(i + 1, [(round(ch.t_in, 2), round(ch.t_exit1, 2), ' '.join(w['word'] for w in ch.words)) for ch in cap.chunks])
           for i, cap in enumerate(captions())]
    log.append('captions: %s' % rep)
    check('C1 gone by 16.25, C2 by 20.6, C3 by 24.81', max(ch.t_exit1 for ch in captions()[0].chunks) <= 16.25 + 1e-6
          and max(ch.t_exit1 for ch in captions()[1].chunks) <= 20.6 + 1e-6
          and max(ch.t_exit1 for ch in captions()[2].chunks) <= 24.81 + 1e-6)
    # exploded scenes draw exactly 12 frame planes (11 while pane 12 is flicked OFF)
    counts = {}
    for t in (1.5, 5.5, 8.6333, 13.2, 13.3, 16.0):
        counts[t] = 12 - int(pane12_hidden(t))
    check('12 frame planes per exploded scene', all(v == 12 for t, v in counts.items() if not pane12_hidden(t)),
          str(counts))
    check('envelopes', True, 'placeholder sfx/music' if envelopes()['placeholder'] else 'real env.json')
    log.append('selftest %.1f s' % (time.time() - t0))
    print('\n'.join(log))
    print('SELFTEST', 'OK' if ok else 'FAILED')
    return ok


def save_srt(path=os.path.join(RW, 'captions', 'ek_frame_ki_keemat.srt')):
    """Upload SRT: the union of the three caption instances (only the caption windows, house spelling)."""
    def ts(x):
        ms = int(round(max(0.0, x) * 1000))
        return '%02d:%02d:%02d,%03d' % (ms // 3600000, ms // 60000 % 60, ms // 1000 % 60, ms % 1000)
    chunks = sorted((ch for cap in captions() for ch in cap.chunks if getattr(ch, 'cleared', None) != 'skipped'),
                    key=lambda ch: ch.t_in)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf8') as f:
        for i, ch in enumerate(chunks, 1):
            f.write('%d\n%s --> %s\n%s\n\n' % (i, ts(ch.t_in), ts(ch.t_exit1), ch.text))
    return path


if __name__ == '__main__':
    if '--selftest' in sys.argv or 'selftest' in sys.argv:
        sys.exit(0 if selftest() else 1)
    if '--srt' in sys.argv:
        print(save_srt())
        sys.exit(0)
    print(__doc__)
