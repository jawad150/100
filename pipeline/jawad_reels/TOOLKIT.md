# jawad_reels project notes (read first)

This is the project copy of the Reels Studio toolkit for **Jawad (@jawad_mp4)**. The rest of this file is the
toolkit's generic cheat-sheet, written for an earlier client: its examples (copy, footage `c01`..., props such as
heart / house / coin_gbp, looks `neon` / `amber` / `airy`) are API illustrations only. Never use them in Jawad's reels.

* Brand: `BRAND.md` (palette, fonts, logo, contrast, safe zones, restore block). Palette + fonts live in
  `project.json`; `K.C['MAGENTA']` is Jawad's FLAME orange here, `K.C['ORANGE']` his RED.
* Profile: start every module with `import jawad_kit` then `from jawad_kit import K, T, ui, F, S3, SFX, J`.
  Looks: `LOOK = 'ember'` (deep warm-black void, flame / ember glows, warm bokeh, red-orange bloom, crushed
  blacks) or `'noir_ember'` (monochrome warm black, one red-orange light). `J.register_look()` adds more.
* House type: `T.render('younger self', 'jw_key', px=210)` (Instrument Serif Italic flame keyword),
  `'jw_caps'` / `'jw_caps_bold'` (white Poppins uppercase), `'jw_body'`, `'jw_mono'` (JetBrains Mono), `'jw_handle'`,
  `'jw_key3d'`, `'jw_neon'`; aliases `font='serif' | 'grotesk' | 'mono'` (`'hand'` = the serif italic).
  `J.HouseTitle('MEETING MY', 'younger self').draw(cv, t, 540, 700, t0=...)` = the covers' lockup (caps line,
  keyword rise, underline draw-on); `J.underline(760).draw(cv, x0, y, u)`; `J.signature(cv, 540, 1585)`;
  `J.embers(140)` rising sparks.
* `brand_smoke.py` is the 2 s reference module (`python3 render.py brand_smoke --sheet 4 --samples 1 --workers 1`).
  Measured on the shared 4-core box, 1 worker: 0.5-0.6 s/frame at 1 sample, 1.0-1.1 s/frame at 3 samples (worker
  peak 0.8-1.0 GB).
* Project-copy fixes: `Glyphs.rise/slam/track(blur=...)` now sets the animator's blur-in (it used to blur the
  settled block for good; use `block_blur=` for a whole-block blur); type3d / ui self-tests skip their footage
  tiles when the workspace has no `frames/manifest.json`; setup_workspace.py: `font_copies`, `"site_images": false`,
  `--footage` refuses without a `drive_folder`.

---------------------------------------------------------------------------------------------------------------
# Organic Fostering toolkit: cheat-sheet for the timeline agents

Read `BRIEF.md` first (copy, palette, safe zones, per-reel looks). This page tells you how to *build* a reel with the
toolkit. Every module's docstring has the full API; `demo_looks.py` is a worked reference that uses almost all of
it (three hero frames plus a 4 s clip with whip, flash and an SFX mix). Steal its patterns.

**Audio is SFX only. No music, no melodic loops or beats.** The client adds music later at each reel's BPM.

| module | what | self-test |
|---|---|---|
| `core.py` | colour, easing, compositing, 3D camera / planes / DOF, effects, backgrounds, post, render loop | `python3 core.py selftest` |
| `footage.py` | graded, time-remapped client footage | `python3 footage.py selftest` |
| `type3d.py` | extruded / glow / neon / glass-pill type, light sweeps, kinetic glyphs, orbit text, counters, video-in-type | `python3 type3d.py selftest` |
| `ui.py` | glass cards, app window, widgets, cursors, bar chart, dock, orbit ring of tags | `python3 ui.py selftest` |
| `sprites3d.py` | loader for the Blender sprite sequences | `python3 sprites3d.py selftest` |
| `assets3d_icons.py`, `assets3d_hero.py` | the Blender renderers (the brief's `assets3d.py`); finals are already rendered | `... selftest` |
| `audio.py` | procedural SFX library, cue mixer, loudness, stems | `python3 audio.py selftest` |
| `render.py` | stills / sheets / previews / parallel master + SFX mux | `python3 render.py selftest` |
| `demo_looks.py` | worked example: one hero frame per look + a 4 s clip with SFX | `python3 demo_looks.py selftest` |

---------------------------------------------------------------------------------------------------------------
## 1. Skeleton of a reel module (`pipeline/fostering/reelN.py`)

```python
import functools, math
import numpy as np
import core as K, footage as F, type3d as T, ui, sprites3d as S3

DUR, LOOK, BPM = 26.0, 'neon', 120          # render.py contract
BED, BED_GAIN_DB = 'room_tone', -30         # optional SFX bed (audio.build_reel reads these)

@functools.lru_cache(maxsize=1)             # build heavy sprites ONCE per process
def assets():
    return dict(you=T.render('YOU', 'extrude3d', px=250), win=ui.app_window(look=LOOK),
                q=S3.get('question', 'night', mode='spin'), clip=F.Clip('c01'), dust=K.Particles(180, seed=7))

def prewarm():                              # called once per render worker
    assets()

def draw(t):                                # PURE function of t -> linear premultiplied canvas (H, W, 4)
    A = assets()
    cam = K.Cam.orbit((0, 0, 0), 1650, yaw=K.lerp(8, -4, K.EASE['easy_ease'](t / DUR)), aperture=30)
    cv = K.background(LOOK, t, cam)
    sc = K.Scene(cam)                       # depth-sorted: planes, billboards, custom draws, particles
    sc.billboard(A['q'].at_yaw(t * 90), (0, -300, 200), 600)
    sc.custom((0, 100, 0), lambda c, cm: A['you'].draw_plane(c, cm, (0, 100, 0), sweep=K.ramp(t, 1, 2)))
    sc.particles(A['dust'], t)
    return sc.render(cv)

def post(cv, t):                            # finishing; default would be K.post(cv, LOOK, t)
    return K.post(cv, LOOK, t, flash=0.3 * K.impulse(t, 2.45))

def samples(t):                             # motion-blur sub-samples: 3 normal, 5-7 on whips / fly-ins
    return 7 if 2.3 < t < 2.6 else 3

def cues():                                 # SFX cue sheet (catalog names, see section 8)
    return [dict(t=2.45, name='impact_big'), dict(t=2.45, name='riser', params=dict(duration=1.6))]
```

`python3 render.py reelN --sheet 16 --samples 1` gives a quick contact sheet; `python3 render.py reelN` gives the
master with SFX muxed in (see section 9).

---------------------------------------------------------------------------------------------------------------
## 2. Conventions (the ones people get wrong)

| thing | convention |
|---|---|
| pixels | `float32 (H, W, 4)` **premultiplied, LINEAR light**. sRGB only at encode (`K.to_srgb8`). Values > 1 are emissive light (rolled off by a soft shoulder). |
| colours | `K.C['MAGENTA']` / `K.hexlin('#B7006E')` are linear RGB. In type3d / ui you may also pass `'MAGENTA'`, `'#B7006E'`, `('ORANGE', 1.8)` (x gain). |
| canvas | `K.W, K.H = 1080, 1920`, `K.FPS = 30`, centre `K.CX, K.CY = 540, 960`. |
| 2D angles | `rot` = degrees **clockwise** on screen. Gradient / sweep `angle` = degrees **CCW from +x** (35 = brand sunset diagonal, -90 = top to bottom). |
| world | x right, **y DOWN**, z AWAY from the viewer. Default `K.Cam()` sits at (0, 0, -1500) with focal 1500, so at z=0 1 world unit = 1 px and (0, 0, 0) is the canvas centre. |
| camera | `yaw>0` looks right, `pitch>0` looks up, `roll>0` turns the scene CCW. `Cam.orbit(target, dist, yaw, pitch)`: yaw>0 moves the camera right (sees the target's right side). |
| planes | `rot=(rx, ry, rz)`: rx>0 tips the top edge toward the camera, ry>0 brings the right edge toward the camera, rz>0 clockwise. `width` in world units. |
| anchors | `K.draw(..., anchor=(ax, ay))` = fraction of the sprite. type3d anchors are fractions of the **text box** (cap-top to baseline), so (.5, .5) centres capitals optically. ui `Panel` anchors are fractions of the card **body** (padding for glows is excluded). |
| time | every animation is a pure function of t (frames render out of order in 4 processes). No state, no `global` counters. |
| depth of field | `Cam(aperture=0..80)`: 0 off, 20 subtle, 34 the demo look, 80 dreamy; `focus_dist` defaults to the distance to the origin (orbit: to the target). |

Place things by layout with `demo_looks.unproject(cam, sx, sy, depth)` (world point seen at screen px at a camera
depth) and read back with `cam.project(P) -> (xy, depth)`.

---------------------------------------------------------------------------------------------------------------
## 3. core (`import core as K`)

```python
K.ramp(t, t0, t1, 'out_expo')                 # eased 0..1 progress   (eases: in_/out_/inout_ + expo quint quart cubic
                                              #  sine circ back elastic, 'easy_ease' = AE 80/80 for cameras, 'glide')
K.Track([(0, (0, 0)), (0.6, (300, 40), 'out_expo'), (1.2, (300, 40), 'hold'), (1.5, (0, 0))])(t)   # .vel(t)
K.spring(t - t0, freq=2.4, damping=0.42)      # 0..1 with overshoot (slams, pops)
K.impulse(t, t0, decay=7) ; K.shake(t, amp, freq, seed) -> dx, dy, rot ; K.wiggle(t, freq, amp, seed)
K.beat(n, BPM) ; K.beat_pulse(t, BPM)         # exact beat times / a 1-at-the-beat pulse
cv = K.background('neon'|'amber'|'airy', t, cam, boost=0..1, center=(x, y), rim=0)   # rim=0 hides the planet rim
K.draw(cv, spr, cx, cy, scale=1, rot=0, opacity=1, mode='over'|'add'|'screen'|'multiply', anchor=(.5, .5), blur=0)
K.draw_plane(cv, spr, cam, center, width, rot=(rx, ry, rz), dof=True, mode='over', blur=0, dof_scale=1)
K.draw_billboard(cv, spr, cam, pos, width, rot=0)                       # camera-facing (coins, glows, 3D sprites)
sc = K.Scene(cam); sc.plane(...); sc.billboard(...); sc.custom(pos, fn(cv, cam)); sc.particles(p, t); sc.render(cv)
K.glow(spr, K.C['MAGENTA'], (8, 28, 80), 1.2)  # padded emissive deep glow (build once)
K.ring(300, 4, K.C['HOT_PINK'] * 2.4) ; K.disc(r, col) ; K.radial(size, col) ; K.rrect_alpha(w, h, r, pad)
K.Particles(180, seed=7, bright=0.9, colors=[...]).draw(cv, cam, t)     # dust / bokeh with DOF
K.light_leak(cv, t, strength=0.6, sweep=0..1) ; K.god_rays(cv, (x, y)) ; K.whip_blur(cv, px, angle) ; K.zoom_blur(cv, 0.08)
K.post(cv, LOOK, t, flash=, chroma=, leak=, fade=, exposure=, footage=0..1)  # finishing; ALWAYS last
u8 = K.to_srgb8(cv, t) ; K.save_png(path, cv_or_u8)
```

`K.post(..., footage=1)` (new): use on frames dominated by **bright full-bleed footage** (hook montage, payoff
shots). The void-tuned bloom (threshold 0.42) otherwise blooms white walls into a milky pink haze.

---------------------------------------------------------------------------------------------------------------
## 4. footage (`import footage as F`)

```python
clip = F.Clip('c12')                                   # .fps .dur .w .h ; times clamp to the clip
spr = clip.get(t_src, 1080, 1920, center=(x, y), zoom=1.1, rot=0, look='neon'|'amber'|'airy'|'natural', pan=(0, 0))
ramp = F.SpeedRamp([(0, 1.0), (0.8, 1.0), (1.3, 0.4, 'inout_sine'), (3.0, 0.4)], src0=2.0); clip.get(ramp(t), ...)
F.still('03-short-term-everyday-connection.webp', 140, 140, look='airy')   # site photos for tags / thumbs
F.contact_sheet('c11', n=8, look='airy')               # find moments + face positions before you frame a shot
```
* `zoom` >= 1 punches in; with `zoom` > 1 you can also move the crop vertically (`center=(x, y)`): at zoom 1 a 16:9
  source covering 9:16 has no vertical slack. 1080p sources (most clips) go soft above ~1.3x zoom full-bleed.
* `c13` has a dark occluder on its left 35 % (FOCUS already crops right). `c11` is all beige: inside letters on an
  ivory page grade it `'natural'` for contrast (demo airy hero).
* A sprite from `clip.get` is writable: dim a far plate with `spr[..., :3] *= 0.7` (demo neon far card).
* The `'neon'` grade was pushed a step (contrast 1.26, plum blacks, stronger magenta/orange split); skin was checked
  on c01, c08, c10 and c12. Grades are display-referred LUTs in `F.GRADES` if a shot needs a local tweak.

---------------------------------------------------------------------------------------------------------------
## 5. type3d (`import type3d as T`)

```python
ts = T.render('YOU', 'extrude3d', px=250, fill=('MAGENTA', 'HOT_PINK', 'ORANGE'), fill_angle=35)   # cached sprite
ts.draw(cv, 540, 900, scale=1, sweep=K.ramp(t, 1.0, 1.9, 'inout_sine'))       # 2D (scale 1 + rot 0 = pixel sharp)
ts.draw_plane(cv, cam, (0, 30, -60), rot=(0, 0, 0), scale=1, opacity=1, blur=0, sweep=u)  # 3D, DOF, parallax
T.Glyphs('A SAFE HOME.', 'deep_glow', px=130, scrim=0.8).slam(cv, t, 540, 900, t0=0.45)   # per-glyph kinetic (2D)
#   animators: rise slam typewriter wipe track flip scramble; exit with out_t0=; 3D tilt=(rx, ry, rz)
T.Counter('gold', px=150).draw(cv, trk(t), 540, 400, vel=trk.vel(t))         # odometer + per-digit motion blur
T.Counter('gold', px=150).sprite(v, vel).draw_plane(cv, cam, P)              # counter in 3D (demo amber)
vt = T.VideoType('NURTURE', px=190, look='light'); vt.draw(cv, clip.get(ts_, 1080, 1920, look='natural'), 540, 640)
z = vt.zoom(u, vt.zoom_point('U'), 540, 640); vt.draw(cv, foot, **z); K.zoom_blur(cv, 0.08 * u)   # zoom-through
ot = T.OrbitText('NURTURE • DEVELOP • GROW • ', 'flat', px=56, fill='IVORY'); ot.draw(cv, cam, c, t=t, part='back') ...
T.measure('NURTURE', 'flat', px=200)   # -> (w, h): check widths against the 940 px safe width BEFORE you design
```
Presets: `flat ui ui_ink extrude3d chrome gold deep_glow neon gradient ink_soft glass_pill glass_pill_light`.

* Saturated extruded word on a dark look (demo "YOU"): `extrude3d` with `env=0, ambient=0.74, spec=0.65,
  depth=0.24, angle=-70, persp=0.08, side=(('#9A1066', 1), ('#22041C', 1)), rim_color=('HOT_PINK', 1.4)`. A warm
  `rim_color` (AMBER / ORANGE) also feeds the side rim and turns plum sides tan.
* `deep_glow` over footage needs `scrim=0.75-0.85`. `ui_ink` (not `flat` INK) for dark text under 32 px.
* `T.Counter(..., blur_cap=0.12)` (new default): spinning digits stay legible gold streaks. The old fixed 0.26
  averaged fast wheels into flat beige bars ("barcode"). Land a roll with `K.Track([(t0, 0, 'out_expo'), (t1, v)])`
  and pass `vel=trk.vel(t)`; cue `slot_tick` (align='start', dur=t1-t0) and `cash_kaching` at t1.
* Width limits at 1080: `NURTURE` Nunito Black ~ 4.8 px per px of size (190 px = 916 px wide), `Foster Carer?` at
  122 px ~ 750 px. Key copy must stay inside x 70..1010.
* Glyphs animators are **2D only** (screen space, optional tilt). For text that must parallax with a 3D camera
  use `ts.draw_plane` and animate the whole word (position, scale, opacity, blur), as the demo does.

---------------------------------------------------------------------------------------------------------------
## 6. ui (`import ui`)

```python
win = ui.app_window(w=820, h=1010, look='amber', header='Allowance calculator', sub='Weekly allowance per child',
                    icons=('home', 'pound', 'chart', 'calendar', 'settings'), active=1)
x, y, sw, sh = win.meta['slot']                        # content area in card px
f = win.face_at(sweep=(t * 0.3) % 1)                   # writable face + neon comet round the edge
win.put(f, ui.chip('0–4', sel, look='amber'), x - 24, y - 24)       # widgets carry 24-32 px glow padding
win.put(f, ui.bar_chart(vals, labels, grow=[...], active=0, w=sw, h=310, look='amber', depth=12), x - 32, y + 64)
win.put(f, ui.check_row('A spare bedroom', w=sw, t=t - tick, look='neon'), x - ui.ROW_PAD, y + i * 120 - ui.ROW_PAD)
win.plane(cv, cam, (30, 255, 150), 790, rot=(9, 13, -1.5), face=f)       # 3D with perspective frost + shadow
xy = win.screen(cam, (30, 255, 150), 790, (9, 13, -1.5), cx_card, cy_card, z=-40)   # cursor on tilted UI
ui.draw_cursor(cv, *xy, 'hand', 84, press=K.impulse(t, tc, 9), click=t - tc, look='amber')
card = ui.glass_card(600, 820, r=48, look='neon'); face = ui.media_face(card, clip.get(t, card.w, card.h, look='neon'))
card.plane(cv, cam, P, 820, rot=(4, -26, 6), face=face, dof_scale=2.2)   # footage in a glass card, extra bokeh
ui.place(cv, ui.button('Start your enquiry', hover=1, press=p, ripple=t - tc), 540, 1450)
ui.orbit_ring(cv, cam, ['Short-term', ('Siblings', thumb, 'siblings')], phase=t * .05, mid=draw_hero, look='airy')
ui.toast(...).plane(...) ; ui.dock_tile(...) + ui.dock_face(...) + ui.carousel(...) ; ui.progress_ring(p) ; ui.slider(v)
ui.badge('Rated Good by Ofsted', 'Inspected May 2025', look='airy').draw(cv, 540, 1290)
```
Window content must fit `win.meta['slot']` (things placed below it land outside the glass body). Budget the slot
height: chips 72, bar chart h + 64, slider ~250 incl. bubble and ticks, fine print 40. Counter digits are in
type3d (`T.Counter`), not ui.

---------------------------------------------------------------------------------------------------------------
## 7. 3D assets (`import sprites3d as S3`; Blender renders in workspace3/assets3d/)

```python
a = S3.get('heart', 'night')                 # cached; .frame(i) .at_yaw(deg) .float_yaw(t, amp, period) .at_time(t)
q = S3.get('question', 'night', mode='spin') # mode picks folder <variant>_<mode>; spin: at_yaw(any deg), wraps
s = S3.get('sprout', 'day', mode='sway')     # .pivot (soil point), .anchor (visual centre), .ground_y, .feature(k)
K.draw(cv, s.at_time(t), x, y, scale=0.6, anchor=(s.pivot[0] / s.size[0], s.pivot[1] / s.size[1]))
sc.billboard(q.at_yaw(ang), (x, y, z), 640)  # world-size billboard: DOF + depth sorting for free
```

| asset | variants (mode, frames, px) | notes |
|---|---|---|
| heart | night, day (yaw 49, 720) | yaw = -40..40 deg |
| house | night, day (yaw 49, 720) | R2 orbit centre |
| shield_check | night, day (yaw 49, 720) | R3 trust |
| check_tile | night, day (yaw 49, 720) | green 3D check (R1 rows) |
| coin_gbp | night (yaw 49, 720), night_spin (spin 72, 1000) | `mode='spin'` for flips / orbiting coins |
| orbs | night, day (static 6, 720) | `.by_label(name)`: sphere_magenta, sphere_orange, sphere_peach, sphere_leaf, torus_glass, capsule_magenta_orange |
| grad_cap, chat_bubble, key_heart, pin_phone | night (yaw 49, 560) | dock / support icons |
| star_badge | night, day (yaw 49, 560) | Ofsted badge icon |
| logo_mark3d | night, day (yaw 49, 1200x1000); night_anim, day_anim (anim 60, swing-in, last frame == yaw 0) | features: heart, girl, boy, leaf_l, leaf_r, leaf_top |
| question | night (yaw 49), night_spin (spin 72) (1000) | R1 "?" |
| pound_glyph | night (yaw 49, 1000) | gold £ |
| sprout | day (anim 120 grow, no loop), day_sway (anim 48 loop) (900x1200) | sway frame 0 == grow frame 119; features base, tip, leaf_low_l/r, leaf_top_l/r |
| leaf | day, night (spin 48 two-axis tumble, 600) | broad frames ~0-4, 16-26, 40-47; edge-on near 9 and 33 |
| seed | day (static 1), day_glow (anim 24 loop) (600) | the sprout already contains its own seed |
| puzzle_pair | day (yaw 49), day_anim (anim 48, click at frame 25) (1000x800) | R3 DEVELOP |
| blocks | day (yaw 49, 800) | lots of empty side space: scale up |

Missing variant -> the loader silently falls back to another one (`a.fallback` is True). Day variants show pale
rims on dark backgrounds; use night on the dark looks. For slow, large hero rotations pass `interp='flow'`.

---------------------------------------------------------------------------------------------------------------
## 8. SFX (`import audio as A`), SFX only

Cue: `dict(t=2.45, name='impact_big', gain_db=0, pan=0, align='hit'|'start', params={...})`. Levels are
pre-balanced: start at gain_db 0, nudge +-3. **`align='hit'` (default) puts the sound's designed hit on t**:

| hit = | sounds |
|---|---|
| the transient (onset) | heartbeat (n, bpm), impact_big (tail), impact_soft, sub_drop (dur), flash_hit (0.1 s suck first), logo_sting (0.42 s swell first), downlifter, glitch_short, ui_click, ui_tick, typing (n, cps), pop, bubble_pop, check_ding, toggle_on, toast_chime, glass_tap, puzzle_click, camera_shutter, coin_flip, coin_ring, coins_burst, cash_kaching ("ching"), shimmer, sparkle, ripple, seed_plip, leaf_rustle (0.3 x dur) |
| the loudest pass | whip (direction +-1), whoosh_fast, whoosh_slow, whoosh_by (doppler: dur, speed, dist, direction), swish_small, air_zoom, card_slide (the "thup") |
| the END (lands on t) | riser (duration), reverse_swell (duration) |
| end of the motion: cue with `align='start'` at the motion start | slot_tick (n, dur), slider_drag (duration, detents), bar_grow (duration, pitch), grow_swell (duration) |

Beds (seamless loops, set `BED` / `BED_GAIN_DB` in the reel module): `room_tone` (R1/R2), `night_air`,
`outdoor_birds` (R3); a list of `{'name', 't0', 't1', 'gain_db', 'fade'}` dicts switches beds per section.
`-30` = felt not heard, `-24` = present. Grid helper: `A.on_beats('whip', BPM * 2, range(1, 9), offset=0.2)`.

`python3 audio.py reel reelN` writes `workspace3/audio/reelN_sfx.wav` + `reelN_sfx_stem.wav` (48 kHz 24-bit,
-18 LUFS, <= -1.5 dBTP). `render.py` now does this for you (next section). Ignore 'tail cut at end' warnings for
cues near DUR; fix 'hit before 0 s'.

---------------------------------------------------------------------------------------------------------------
## 9. Rendering

```bash
cd pipeline/fostering
python3 render.py reel1 --sheet 16 --samples 1          # contact sheet, ~1 min: check layout / timing
python3 render.py reel1 --stills 2.6,5.9,12.0           # full-quality stills (PNG) for critique
python3 render.py reel1 --preview                        # 15 fps, 1 sample, quick motion check
python3 render.py reel1 --range 5.3 11.6                 # one section
FOSTER_NICE=10 python3 render.py reel1                   # master: reel1.mp4 (crf 14) + reel1_share.mp4
python3 demo_looks.py heroes | clip | selftest           # the reference demo
```
* The SFX mix is (re)built automatically from `cues()` when `audio/<reel>_sfx.wav` is missing or older than the reel
  module; `--sfx` forces a rebuild, `--no-sfx-build` disables it, `--audio x.wav` uses a given file.
* The master is H.264 High yuv420p bt709, 30 fps, AAC 320k 48 kHz, cut to exactly DUR. `demo_looks.verify_master(path, dur=26.0)`
  checks streams, frame count, duration and loudness (ffmpeg ebur128) of any master.
* Outputs: `workspace3/out/<reel>/` (stills/, sheet.jpg, cues.json, render_stats.json).

---------------------------------------------------------------------------------------------------------------
## 10. Performance (4 cores shared, 1 sample, warm caches)

| piece | cost |
|---|---|
| background | 40-130 ms (with a moving cam ~120 ms) |
| post + to_srgb8 | ~90 + 45 ms |
| full-bleed footage get | 60-110 ms; a 700x1000 card ~25 ms |
| glass window plane + face_at | 60-180 ms |
| extruded hero word draw / sweep | ~20 ms (build 0.3-1.2 s once) |
| demo hero frames (whole scene, 3 samples) | 3-10 s |
| demo clip on 4 workers | ~2.5-6 s per frame per worker (3-7 samples) |

* Build every static sprite (type, windows, glows, glass cards, Particles) in an `lru_cache`d function called from
  `prewarm()`. Never rebuild per frame. Per-frame: only `face_at`, widgets with changing values, footage.
* `samples(t)`: 3 normal, 5-7 only where things move > ~1500 px/s. Cost scales linearly.
* `Glyphs.slam` adds its own sub-frame smear (up to 24 renders of the word per sample). Fine for a 0.4 s slam,
  expensive if you leave it on for long stretches (`smear=False` once settled, or use `ts.draw` when settled).
* Memory: every worker holds its own caches. Budgets (env, MB per process): `FOSTER_S3_CACHE_MB` sprites3d frames
  (768; render.py workers 448), `FOSTER_SPRITE_CACHE_MB` core mips/blur levels (256), `FOSTER_TYPE_CACHE_MB`
  type3d (400; 256 with 3+ workers), `FOSTER_CLIP_CACHE_MB` footage frames (160). The demo clip peaks at ~2.2 GB
  per worker; the shell's memory limit is ~14 GB for everything you run, so 4 workers is the ceiling.
* render.py survives a worker being OOM-killed: it prints `!! a render worker died` and retries the unfinished
  chunks with one worker fewer (it used to hang forever). `render_stats.json` records `worker_max_rss_mb`.
* Never keep per-frame arrays in module-level lists/dicts, and avoid reference cycles that capture big arrays
  (closures that capture an object which stores the closure). `K.Scene` itself had such a cycle (fixed): it
  held every frame's sprites until a rare GC pass, 4.5 GB per worker on the demo.

---------------------------------------------------------------------------------------------------------------
## 11. Pitfalls

1. `draw(t)` must be pure: frames render out of order across 4 processes.
2. Don't modify arrays returned by caches (`S3 ... .frame()`, `T.render().layers`, `ui.glass_card().face`): copy,
   or use `face_at()` (writable). If you edit any sprite in place call `K.invalidate(spr)`.
3. Bright full-bleed footage: `K.post(..., footage=1)`; `deep_glow` text over it needs `scrim=0.8`.
4. `K.background('neon'|'amber')` always has the planet rim at the bottom: `rim=0` when it competes with content.
5. Billboards and plane corners behind the camera's near plane are culled (planes are clipped and may fly
   through the lens; billboards just vanish).
6. Sprites scaled from 0 (pop-ins) are now safe (sub-pixel footprints are skipped).
7. `T.style(...)`/`T.render(...)` now accept `spec=` (specular). `OrbitText(fill='IVORY')` now sets the colour
   (`fill=True/False` keeps meaning "repeat the text round the ring"; or pass `repeat=`).
8. Text sizes: hero 130-240 px, H2 80-120, UI 34-46, fine print >= 28 *after* perspective (a tilted window shrinks
   its text by ~10 %: give fine print 30 px on tilted UI).
9. Safe zones: key copy x 70..1010, y 230..1480; nothing textual below y 1620; avoid x > 930 for y 1050..1700.
10. Use catalog SFX names (`A.names()`); unknown names fall back fuzzily with a printed warning.
11. `mode='add'` adds colour but combines alpha like 'over'. That suits light added onto an opaque canvas (glows,
    bokeh, leaks), but summing N weighted copies of a sprite into an empty layer (a motion smear) leaves the result
    semi-transparent and pale (alpha 1-(1-a/N)^N). Accumulate smears with plain array sums, as
    `anim4_fx.accumulate` does, and composite the summed layer once with 'over'.
12. `ui.glass_card(shadow=0)` raises a TypeError: pass a small value (0.5) and draw only the face. `ui.button`'s
    glow is clipped at the sprite bounds: feather it or pad the sprite.
13. `to_srgb8` rolls linear white off to about 247/255. For a pure-white page, use a page value around linear 1.16
    and a bloom threshold of about 1.3 (anim4).
14. `render.py` rebuilds a stale SFX mix with `audio.build_reel` at -1.5 dBTP and without custom sounds. A module
    with its own `<module>_sfx.py` builds the mix itself (`python3 <module>_sfx.py build`) and renders with
    `--no-sfx-build`.
15. `K.shake` peaks at about 2 px at frame times even at high amplitude. For a visible hit judder, use a damped
    sub-pixel offset as `anim1.py` does (`SHAKES`).
16. `K.ramp(t, a, b)` defaults to `'out_expo'`, which makes about 60 % of the change happen in the first ~12 % of
    the ramp. Used as a fade, it gives one-frame exits, ghost frames and pops (anim4 QA). Always pass the ease:
    'inout_sine' or 'linear' for fades, 'in_cubic' for exits, 'out_cubic' for arrivals.
