# Device recipes (code)

Working patterns for the devices in SKILL.md, written against the reels toolkit API (TOOLKIT.md in the project's
toolkit folder). Each block is a starting point: copy it into a reel module (or `<module>_fx.py`), then replace the
copy, clip ids, colours and times with the brief's. Copy strings must come from the brief's verified-copy table.

Rules for all of them:
- `draw(t)` is pure. Static sprites are built once in `lru_cache`d functions that `prewarm()` calls.
- Times sit on the BPM grid (`B(n)`). Hard cuts switch half a frame early (`HALF`).
- Colour names like `'MAGENTA'` are the toolkit's colour roles (`K.C`). A project re-points them to its brand with
  `project.json` `"palette"` (if the toolkit has wsconf.py) or a brand kit profile from
  reels-studio:motion-toolkit-engineer. Don't hard-code another brand's hex values. The `side=` hex values in the
  extruded-type recipe are examples, so derive them from the brand's darkest tones.

## Shared header and finishing (exposure push instead of a flash)

```python
import functools, math, os
import numpy as np
import core as K, type3d as T, ui, footage as F, sprites3d as S3

DUR, LOOK, BPM = 26.0, 'neon', 120
HALF = 0.5 / K.FPS                        # cut switch: half a frame before the cut time
def B(n): return n * 60.0 / BPM           # beat n -> seconds
CUTS = [B(5), B(11)]                      # hard cuts from the shot list

def post(cv, t):
    # A cut "flash frame" is an exposure push (multiplicative: the blacks stay black) plus a bloom kick.
    # Never K.flash / K.fade / post(flash=, fade=): their uniform ivory term lifts the blacks into a grey veil.
    push = sum(K.impulse(t, c - 0.02, decay=16) for c in CUTS)      # peaks on the cut frame
    return K.post(cv, LOOK, t, exposure=1.4 * push, bloom=K.LOOKS[LOOK]['bloom'] * (1 + 0.9 * push))

def samples(t):
    fast = any(abs(t - c) < 0.15 for c in CUTS)                      # whips, fly-ins, zoom-throughs
    return 7 if fast else 3
```

## Particles kept off logos and copy

```python
@functools.lru_cache(maxsize=4)
def keep_mask(rects, soft=60.0):          # rects: ((x0, y0, x1, y1), ...) screen px of logo / copy areas
    yy = np.arange(K.H, dtype=np.float32)[:, None]
    xx = np.arange(K.W, dtype=np.float32)[None, :]
    m = np.ones((K.H, K.W), np.float32)
    for x0, y0, x1, y1 in rects:
        dx = np.maximum(np.maximum(x0 - xx, xx - x1), 0)
        dy = np.maximum(np.maximum(y0 - yy, yy - y1), 0)
        m = np.minimum(m, np.clip(np.sqrt(dx * dx + dy * dy) / soft, 0, 1))
    return m[..., None]

def particles_clear_of(cv, parts, cam, t, rects):
    layer = np.zeros_like(cv)
    parts.draw(layer, cam, t)
    cv[..., :3] += layer[..., :3] * keep_mask(tuple(rects))
```

## Iris montage hook

```python
IRIS_C = (540.0, 860.0)
MONT = [('c01', 9.4, (0.50, 0.42)), ('c08', 1.0, (0.50, 0.40)), ('c12', 11.4, (0.62, 0.44))]  # footage-editor picks:
T_IRIS, DT = B(1), 60.0 / BPM / 3         # (clip, source s, face crop centre); one flash per triplet 8th

@functools.lru_cache(maxsize=1)
def iris_assets():
    return K.glow(K.ring(300, 4, K.C['HOT_PINK'] * 2.4), K.C['MAGENTA'], (8, 28, 80), 1.3)

def iris_r(t):                            # springs open with overshoot, then blows wide into the next shot
    t_end = T_IRIS + len(MONT) * DT
    return 820.0 * K.spring(t - T_IRIS, freq=2.2, damping=0.5) + 1300.0 * K.ramp(t, t_end - 0.15, t_end, 'in_cubic')

def iris_montage(cv, t):
    k = int(min(max((t + HALF - T_IRIS) // DT, 0), len(MONT) - 1))  # shot index switches half a frame early
    cid, src, ctr = MONT[k]
    u = K.clamp((t - T_IRIS - k * DT) / DT)
    foot = F.Clip(cid).get(src + u * DT, K.W, K.H, center=ctr, zoom=K.lerp(1.22, 1.0, K.EASE['out_cubic'](u)),
                           look=LOOK)
    r = iris_r(t)
    yy, xx = np.ogrid[0:K.H, 0:K.W]
    d = np.sqrt((xx - IRIS_C[0]) ** 2 + (yy - IRIS_C[1]) ** 2).astype(np.float32)
    m = np.clip((r - d) / 3.0 + 0.5, 0, 1)[..., None]                # 3 px anti-aliased edge
    cv[..., :3] = cv[..., :3] * (1 - m) + foot[..., :3] * m
    K.draw(cv, iris_assets(), *IRIS_C, scale=max(r, 1.0) / 300.0, mode='add')
    return cv
# SFX: seed_plip / heartbeat at the open, swish_small + ui_tick on each cut, reverse_swell ending on the close.
```

## Card tunnel

```python
TUN0, TUN1, V0 = B(1), B(3), 6600.0
TUN_STILLS = [('c12', 3.0, (0.60, 0.42)), ('c04', 1.4, (0.47, 0.38)), ('c09', 3.4, (0.45, 0.42))]

@functools.lru_cache(maxsize=1)
def tunnel_assets():
    card = ui.glass_card(480, 624, r=36, look='amber')
    faces = [ui.media_face(card, F.Clip(c).get(s, card.w, card.h, center=ctr, look='amber')) for c, s, ctr in TUN_STILLS]
    lay = []
    for k in range(18):                                              # golden-angle helix of cards
        th = math.radians(-58.0 + 137.5 * k)
        r = 620.0 + 200.0 * (k % 2)
        P = np.array([r * math.cos(th), 1.15 * r * math.sin(th), 900.0 + 560.0 * k])
        lay.append((k % len(faces), P, (-26.0 * math.sin(th), 26.0 * math.cos(th), ((k * 37) % 21 - 10) * 1.2)))
    return card, faces, lay

def tunnel_z(t):                          # surging rush, then an exponential brake (velocity stays continuous)
    L = TUN1 - TUN0
    a = K.clamp(t - TUN0, 0, L)
    z = -1500.0 + V0 * (a + 0.3 * L / math.pi * (1 - math.cos(math.pi * a / L)))
    return z + (V0 / 6.0 * (1 - math.exp(-6.0 * (t - TUN1))) if t > TUN1 else 0.0)

def tunnel(t):
    card, faces, lay = tunnel_assets()
    cam = K.Cam(pos=(0.0, 0.0, tunnel_z(t)), roll=34.0 * K.ramp(t, TUN0, TUN1 + 0.6, 'out_cubic'),
                aperture=26, focus_dist=2600.0)
    cv = K.background('amber', t, cam, rim=0, parallax=0.35)
    sc = K.Scene(cam)
    for fi, P, rot in lay:
        dep = cam.depth(P)
        if 40 < dep < 7800:
            op = K.smoothstep(7800.0, 5600.0, dep)                   # cards emerge from the fog
            sc.custom(P, lambda c, cm, P=P, rot=rot, f=faces[fi], op=op: card.plane(
                c, cm, P, 480.0, rot, opacity=op, face=f, frost=0.0, shadow=0.0, dof_scale=1.4))
    sc.render(cv)
    return cv
# samples(t) = 7 through the tunnel. SFX: whoosh_by on beats (pan alternating), slot_tick align='start',
# reverse_swell ending on the title slam.
```

## Video-in-type with zoom-through

```python
VT0, VZ0, VZ1 = B(8), B(10), B(11)        # entrance, zoom start, zoom end (= the cut to full footage)
VT_CLIP = ('c01', 2.0, (0.50, 0.40))      # high-contrast faces that sit in the letter band

@functools.lru_cache(maxsize=1)
def vit_assets():
    vt = T.VideoType('NURTURE', px=191, tracking=-0.01, look='light')   # very heavy letters; T.measure: <= 940 px
    return vt, vt.zoom_point('U', index=4)                           # character index 4 = the second U

def vit(t):
    vt, zp = vit_assets()
    cv = K.background('airy', t)
    foot = F.Clip(VT_CLIP[0]).get(VT_CLIP[1] + (t - VT0), K.W, K.H, center=VT_CLIP[2], look='natural')
    if t + HALF < VZ0:
        sw = K.ramp(t, VT0 + 0.4, VT0 + 1.2, 'inout_sine')
        vt.draw(cv, foot, 540, 900, scale=K.lerp(1.12, 1.0, K.ramp(t, VT0, VT0 + 0.6, 'out_expo')),
                sweep=sw if 0 < sw < 1 else None)
    else:
        u = K.ramp(t, VZ0, VZ1, 'linear')                            # vt.zoom applies its own in_expo
        vt.draw(cv, foot, **vt.zoom(u, zp, 540, 900, s0=1.0, s1=46.0, ease='in_expo'))
        K.zoom_blur(cv, 0.12 * K.EASE['in_cubic'](u) * (1 - K.ramp(u, 0.92, 1.0)))
    return cv
# The footage is screen-locked, so the zoom lands exactly on the full-frame shot that follows at VZ1.
# samples 7 during VZ0..VZ1. SFX: reverse_swell + air_zoom ending on VZ1.
```

## App-window checklist with cursor, progress ring and toast

```python
ROWS = ['A spare bedroom', 'Time & flexibility', 'Rent or own your home']   # verified copy only
TICK = [B(13), B(14.5), B(16)]
WIN_C, WIN_W, WIN_ROT = (0.0, -60.0, 0.0), 860.0, (7.0, -14.0, 1.5)

@functools.lru_cache(maxsize=1)
def win_assets():
    win = ui.app_window(w=860, h=1100, look='neon', title='example.com', header='Am I eligible?', active=1)
    return win, ui.toast('You could be a great fit', look='neon')

def checklist(t):
    win, toast = win_assets()
    cam = K.Cam.orbit((0, 0, 0), 1650, yaw=K.lerp(-6, 4, K.EASE['easy_ease'](K.ramp(t, B(12), B(18), 'linear'))),
                      pitch=3, aperture=34)
    cv = K.background('neon', t, cam, rim=0)
    f = win.face_at(sweep=(t * 0.35) % 1)                            # neon comet round the edge
    x, y, sw, sh = win.meta['slot']                                  # everything must fit this slot
    for i, lab in enumerate(ROWS):
        win.put(f, ui.check_row(lab, w=sw, t=t - TICK[i], look='neon'), x - ui.ROW_PAD, y + i * 120 - ui.ROW_PAD)
    p = sum(K.ramp(t, tk, tk + 0.3) for tk in TICK) / len(TICK)
    win.put(f, ui.progress_ring(p, size=260, look='neon'), x + sw / 2, y + 3 * 120 + 10, anchor=(0.5, 0))
    win.plane(cv, cam, WIN_C, WIN_W, rot=WIN_ROT, face=f)
    a = K.ramp(t, B(17), B(17.5), 'out_cubic')
    if a > 0:
        toast.plane(cv, cam, (0.0, 520.0 - 60.0 * a, -120.0), 620, rot=WIN_ROT, opacity=a)
    path = K.Track([(TICK[0] - 0.6, (x + 300, y + 420))] +
                   [(tk - 0.08, (x + 58, y + 48 + 120 * i)) for i, tk in enumerate(TICK)] +
                   [(TICK[-1] + 0.6, (x + 420, y + 520))], ease='inout_cubic')
    tc = max([tk for tk in TICK if tk <= t], default=-9.0)
    xy = win.screen(cam, WIN_C, WIN_W, WIN_ROT, *path(t), z=-60)
    ui.draw_cursor(cv, xy[0], xy[1], 'arrow', 76, press=K.impulse(t, tc, 9), click=t - tc, look='neon',
                   opacity=K.ramp(t, TICK[0] - 0.6, TICK[0] - 0.4) * (1 - K.ramp(t, TICK[-1] + 0.4, TICK[-1] + 0.6)))
    return cv
# SFX per tick: ui_click + check_ding (pitch rising), swish_small on cursor moves, toast_chime on the toast.
# UI text >= 34 px on screen after perspective; fine print 30 px on tilted UI.
```

## Glass dock carousel

```python
DOCK = [('Full Training', 'Preparation & learning', 'graduation', ('c03', 2.4)),
        ('Ongoing Support', 'Your social worker', 'chat', ('c04', 1.0)),
        ('Weekly Allowance', 'Verified figure here', 'pound', ('c10', 17.4))]
D0 = B(23)

@functools.lru_cache(maxsize=1)
def dock_assets():
    return [ui.dock_tile(ti, su, ic, look='neon') for ti, su, ic, _ in DOCK]

def dock(t):
    tiles = dock_assets()
    focus = K.Track([(D0 + 1.0, 0.0), (D0 + 3.0, 0.0), (D0 + 3.5, 1.0), (D0 + 5.5, 1.0), (D0 + 6.0, 2.0)],
                    ease='inout_cubic')(t)
    cam = K.Cam(pos=(K.lerp(-60, 60, K.ramp(t, D0, D0 + 7, 'inout_sine')), 0, -1500), aperture=30, focus_dist=1500)
    cv = K.background('neon', t, cam, rim=0)
    sc = K.Scene(cam)
    for i, (dx, s, w) in enumerate(ui.carousel(len(tiles), focus, spacing=330, grow=0.16)):
        sx, sy, sw_, sh_, sr = tiles[i].meta['slot']
        cid, src = DOCK[i][3]
        media = F.Clip(cid).get(src + (t - D0) * 0.5, int(sw_), int(sh_), look='neon') if w > 0.05 else None
        face = ui.dock_face(tiles[i], focus=w, media=media, media_mix=w, sweep=((t - D0) * 0.3 + i * 0.33) % 1.0)
        P = (dx - 48.0, 40.0, 0.0)                                   # row centred left of x 540: text stays <= x 915
        sc.custom(P, lambda c, cm, i=i, P=P, s=s, face=face: tiles[i].plane(c, cm, P, 300.0 * s, rot=(0, -8, 0),
                                                                           face=face))
    sc.render(cv)
    return cv
# A tile's 3D icon may lift above its tile, never over the footage faces. SFX: card_slide on the entrances,
# ui_hover + ui_click + glass_tap per focus change.
```

## Orbit text and orbit tags

```python
@functools.lru_cache(maxsize=1)
def orbit_assets():
    ot = T.OrbitText('NURTURE • DEVELOP • GROW • ', 'flat', px=56, radius=380, tilt=14, roll=-8,
                     fill='IVORY')
    return ot, S3.get('house', 'night')

def orbit_text(t):
    ot, hero = orbit_assets()
    cam = K.Cam.orbit((0, 0, 0), 1600, yaw=K.wiggle(t, 0.2, 4, seed=1), pitch=6, aperture=30)
    cv = K.background('neon', t, cam, rim=0)
    ot.draw(cv, cam, (0, 0, 0), t=t, spin=20, part='back')          # back half: mirrored, dim, blurred
    K.draw_billboard(cv, hero.float_yaw(t, amp=14, period=4.5), cam, (0, 0, 0), 520)
    ot.draw(cv, cam, (0, 0, 0), t=t, spin=20, part='front')
    return cv

TAGS = ['Short-term', 'Long-term', 'Emergency', 'Respite', 'Siblings', 'Teenagers']   # or (text, thumb, key)
def orbit_tags(t, t0=B(24)):
    rz, tilt = 300.0, 20.0
    cam = K.Cam.orbit((0, 60, 0), 1500, yaw=K.lerp(-6, 4.5, K.EASE['easy_ease'](K.ramp(t, t0, t0 + 5, 'linear'))),
                      pitch=7, aperture=18, focus_dist=1500 - rz * math.cos(math.radians(tilt)))
    cv = K.background('airy', t, cam)
    hero = S3.get('heart', 'day')
    enter = [K.ramp(t, t0 + 0.25 * i, t0 + 0.25 * i + 0.35, 'out_cubic') for i in range(len(TAGS))]
    ui.orbit_ring(cv, cam, TAGS, phase=(t - t0) * 0.05, center=(0, 60, 0), radius=(430, rz), tilt=tilt, roll=6,
                  look='airy', enter=enter,
                  mid=lambda c: K.draw_billboard(c, hero.float_yaw(t, 12, 4.0), cam, (0, 60, 0), 420))
    return cv
# Thumbnails: ('Siblings', F.still('<site photo>', 140, 140, look='airy'), 'siblings'). Check every frame that each
# tag stays inside x 70-1010 and out of the like/share column. Parked tags must all be readable (give explicit slots
# if the ring hides some). In a set, tilt and roll each ring differently. SFX: pop per tag, whoosh_by on turns.
```

## Counter and slot digits

```python
C0, C1, VALUE = B(5), B(8), 447.60        # VALUE comes from the verified-copy table, never invented

@functools.lru_cache(maxsize=1)
def counter_assets():
    return T.Counter('gold', px=150, prefix='£', decimals=2), K.Track([(C0, 0.0, 'out_expo'), (C1, VALUE)])

def counter(cv, t):
    cnt, trk = counter_assets()
    cnt.draw(cv, trk(t), 540, 760, vel=trk.vel(t))                    # per-digit motion blur from the velocity
    # slot-machine variant: cnt.slot(cv, t, VALUE, 540, 760, t0=C0, dur=1.4, spins=2)
    # in 3D: cnt.sprite(trk(t), trk.vel(t)).draw_plane(cv, cam, (0, -200, 0))

def counter_cues():
    return [dict(t=C0, name='slot_tick', align='start', params=dict(dur=C1 - C0)),
            dict(t=C1, name='cash_kaching'), dict(t=C1, name='coin_ring', gain_db=-3)]
# Set prefix / decimals / sep for the brand's currency. Keep blur_cap at 0.12 (the default): legible gold streaks.
```

## Extruded 3D slam, light sweep and deep glow

```python
@functools.lru_cache(maxsize=1)
def type_assets():
    hero = T.render('YOU', 'extrude3d', px=250, fill=('MAGENTA', 'HOT_PINK', 'ORANGE'), fill_angle=35, env=0,
                    ambient=0.74, spec=0.65, depth=0.24, angle=-70, persp=0.08,
                    side=(('#9A1066', 1), ('#22041C', 1)), rim_color=('HOT_PINK', 1.4))
    sub = T.Glyphs('Foster Carer?', 'deep_glow', px=132, glow_color=('ORANGE', 2.4), scrim=0.8)
    return hero, sub

def type_slam(cv, t, t0=B(7)):
    hero, sub = type_assets()
    s = K.lerp(1.6, 1.0, K.spring(t - t0, freq=3.2, damping=0.45))  # 1.6 -> 1 with overshoot
    sw = K.ramp(t, t0 + 0.55, t0 + 1.45, 'inout_sine')
    hero.draw(cv, 540, 860, scale=s, opacity=K.ramp(t, t0 - 0.03, t0 + 0.05), sweep=sw if 0 < sw < 1 else None)
    sub.rise(cv, t, 540, 1080, t0=t0 + 0.5)
# In 3D with parallax: hero.draw_plane(cv, cam, (0, 30, -60), rot=(0, 0, 0), sweep=sw).
# Gold variant: T.render('£447.60', 'gold', px=210). Warm sweep on light looks: sweep_kw=dict(color='AMBER').
# Camera shake on the slam: dx, dy, rot = K.shake(t, 9 * K.impulse(t, t0, 8), 15). SFX: impact_big (+ sub_drop) on
# t0, riser ending on t0, shimmer at the sweep.
# Hand-off: when a Glyphs animation settles into a static sprite, the glow and scrim fade on their own ramps so
# the last animated and first static frames match.
```

## Logo end card with CTA

```python
E0, TC = B(42), B(47)                      # card starts, cursor click; settled hold >= 1.5 s after the cursor leaves
CTA, LINE = 'Start your enquiry', 'example.com'           # verified copy only
LOGO_FILE = 'logo_full_onDark.png'        # the brand's light-on-dark logo file in <WS>/brand/ (light looks: the normal one)

@functools.lru_cache(maxsize=1)
def end_assets():
    logo = K.load_image(os.path.join(K.BRAND, LOGO_FILE), size=760)  # width 760 px, aspect kept; never stretched
    pool = K.radial(1300, K.C['PLUM'] * 0.6)          # a dark pool behind the logo, NOT a glow in the logo's colour
    line = T.render(LINE, 'ui', px=34)
    dust = K.Particles(120, seed=5, bright=0.7)
    return logo, pool, line, dust

def end_card(t):
    logo, pool, line, dust = end_assets()
    cam = K.Cam(pos=(0, 0, K.lerp(-1700, -1500, K.ramp(t, E0, E0 + 1.2, 'out_cubic'))), aperture=20)
    cv = K.background(LOOK, t, cam, rim=0, intensity=0.6)
    particles_clear_of(cv, dust, cam, t, ((150, 560, 930, 960), (200, 1320, 880, 1560)))   # logo + CTA rects
    K.draw(cv, pool, 540, 760, opacity=0.8)
    a = K.ramp(t, E0, E0 + 0.6, 'out_cubic')
    K.draw(cv, logo, 540, 760, scale=K.lerp(0.92, 1.0, a), opacity=a)
    b = K.spring(t - (E0 + 1.0), freq=2.6, damping=0.5)
    btn = ui.button(CTA, hover=K.ramp(t, TC - 0.5, TC - 0.2), press=K.impulse(t, TC, 9),
                    ripple=(t - TC) if t >= TC else None, look=LOOK)
    ui.place(cv, btn, 540, 1400, scale=K.lerp(0.6, 1.0, b), opacity=K.clamp(1.5 * b))
    line.draw(cv, 540, 1530, opacity=K.ramp(t, E0 + 1.25, E0 + 1.6))
    cur = K.Track([(TC - 0.7, (760.0, 1700.0)), (TC - 0.05, (560.0, 1410.0)), (TC + 0.35, (560.0, 1410.0)),
                   (TC + 0.85, (820.0, 1760.0))], ease='inout_cubic')
    op = K.ramp(t, TC - 0.7, TC - 0.5) * (1 - K.ramp(t, TC + 0.6, TC + 0.85))
    if op > 0:
        ui.draw_cursor(cv, *cur(t), 'hand', 84, press=K.impulse(t, TC, 9), click=t - TC, look=LOOK, opacity=op)
    return cv
# CTA button body inside x 70-1010 with its bottom <= y 1600, the URL line right edge <= x 930 (it sits in the
# like/share band), nothing textual below y 1620. 3D mark instead of the flat logo:
# S3.get('<brand>_mark3d', 'night_anim').at_time(t - E0) (swing-in, last frame == yaw 0), then .float_yaw(t, 6, 5).
# SFX: logo_sting on E0 (+ impact_soft), pop on the CTA, ui_click + toggle_on on TC.
```
