"""core.py: rendering engine for the Organic Fostering reels (1080x1920, 30 fps).

PIXEL CONVENTION: every canvas and sprite is a premultiplied, LINEAR-light float32 RGBA array (H, W, 4).
Convert brand hex colours with hexlin() / C[...] and convert back to sRGB only at encode time (to_srgb8).
Values above 1.0 are fine (emissive light); to_srgb8 rolls them off with a soft shoulder.
Importing this module has no side effects beyond process tuning: cv2.setNumThreads (env FOSTER_CV_THREADS,
default 2), limit_blas_threads() (numpy's OpenBLAS pool -> FOSTER_BLAS_THREADS, default 1; its idle threads
spin) and tune_malloc() (glibc mmap threshold, so 33 MB frame buffers are recycled; FOSTER_NO_MALLOPT=1).

PATHS
    REPO, WS (= REPO/workspace3, env FOSTER_WS), FONTS, BRAND, FRAMES, SITE_IMG, ASSETS3D, AUDIO, OUT, SELFTEST
    W, H, FPS = 1080, 1920, 30;  CX, CY = 540.0, 960.0;   font_path('Nunito-Black') -> .ttf path

COLOUR
    hexlin('#B7006E') -> np.float32[3] linear RGB;  C['MAGENTA'], C['HOT_PINK'], C['ORANGE'], C['AMBER'],
        C['LEAF'], C['LEAF_HI'], C['PLUM'], C['INK'], C['NIGHT_0'], C['NIGHT_1'], C['IVORY'], C['PEACH'],
        C['LAVENDER'], C['LOGO_MAGENTA'], C['LOGO_ORANGE'], C['WHITE'], C['BLACK'] (all linear)
    to_lin(srgb), to_srgb(lin) exact, any shape;  lum(rgb) Rec.709 luminance
    mix(c0, c1, t, space='oklab'|'linear'|'srgb') -> colour (t may be an array)
    gradient(w, h, stops, angle=35) -> (h, w, 3) linear; stops [c0, c1, ...] or [(pos, c), ...], OKLab ramp;
        angle in degrees counter-clockwise from +x (0 = left->right, 90 = bottom->top, -90 = top->bottom)
    brand_gradient(w, h, angle=35, c0=C['MAGENTA'], c1=C['ORANGE'], alpha=None) -> sprite (signature
        gradient, magenta bottom-left -> orange top-right); alpha = optional (h, w) coverage
    to_srgb8(canvas, t=0, dither=True, shoulder=True) -> uint8 (H, W, 3) RGB: highlight shoulder (knee 0.82),
        sRGB, and temporally varying blue-noise dither of +-0.5 LSB (no banding in dark glows). Alpha ignored.

ANIMATION (all eases take x in 0..1 and clamp)
    clamp, lerp (tuples ok), smoothstep(e0, e1, x), remap(x, a0, a1, b0=0, b1=1, ease=None, clip=True)
    ramp(t, t0, t1, ease='out_expo') -> eased 0..1 progress of t within [t0, t1]
    eases: linear, in_/out_/inout_ + expo | quint | quart | cubic | sine | circ | back | elastic, smooth
        EASE['out_expo'](0.3);  get_ease(spec): callable | EASE name | 'hold' | (out_pct, in_pct) | (x1, y1, x2, y2)
    bezier(x1, y1, x2, y2) -> CSS cubic-bezier ease;  influence(80, 80) -> AE keyframe 'easy ease' (camera moves)
        EASE['easy'] = influence(33, 33), EASE['easy_ease'] = influence(80, 80), EASE['glide'] = influence(90, 90)
    Track(keys, ease='inout_cubic'): keys [(t, v), (t, v, ease_to_next), ...], scalar or vector values; a key's
        ease applies from that key to the next ('hold' = step). Clamps outside the key range.
        pos = Track([(0, (0, 0)), (0.6, (300, 40), 'out_expo'), (1.2, (300, 40), 'hold'), (1.5, (0, 0))])
        pos(0.3) -> np.array([x, y]); Track([(0, 0), (1, 1)])(0.5) -> 0.5; pos.vel(t); pos.start, pos.end
    spring(t, freq=2.0, damping=0.4) -> 0..1 with overshoot, t = seconds since release (0 before)
    wiggle(t, freq=1, amp=1, seed=0, octaves=2) -> smooth non-periodic noise in about [-amp, amp]
    shake(t, amp=12, freq=14, seed=0) -> (dx, dy, rot_deg);  scale it by impulse() for hits
    impulse(t, t0, decay=7.0, attack=0.02) -> 0 before t0, 1 at t0+attack, then exp(-decay * dt)
    beat(n, bpm, offset=0) -> seconds;  beat_index(t, bpm, offset=0) -> float beat;  beat_pulse(t, bpm,
        offset=0, decay=6) -> 1 on each beat decaying to the next

CANVAS / COMPOSITING (in place, return the canvas)
    new_canvas(rgb=None, w=W, h=H) -> transparent (rgb None) or opaque solid canvas
    over(dst, src, opacity=1), add(...), screen(...), multiply(...)   same-shape full arrays
    sprite(img) -> sprite from PIL.Image, uint8/uint16 RGB/RGBA/L (sRGB, straight alpha), or float RGBA
        (assumed already premultiplied linear);  load_image(path, size=None, scale=None) -> cached read-only
        sprite (size=(w, h) or a width int keeping aspect);  pad(spr, p) (centre preserved), tint(spr, rgb,
        amount=1), with_opacity(spr, k), alpha_bbox(spr), crop_to_alpha(spr, margin=4)
    draw(canvas, spr, cx, cy, scale=1, rot=0, opacity=1, mode='over', anchor=(0.5, 0.5), blur=0, frost=0)
        -> bbox (x0, y0, x1, y1) or None. Anchor point lands at (cx, cy) with sub-pixel accuracy; scale float
        or (sx, sy); rot degrees clockwise; trilinear mip-mapped minification (no aliasing when shrinking);
        works only on the affected bbox. mode: 'over' | 'add' | 'screen' | 'multiply' | 'erase'.
        blur: gaussian sigma in screen px (cached per sprite). frost: sigma of a frosted-glass blur applied to
        the canvas under the sprite's alpha before compositing (glass cards).
    draw_quad(canvas, spr, quad, opacity=1, mode='over', blur=0, frost=0) -> homography warp of the sprite
        corners onto quad = [TL, TR, BR, BL] canvas px (premultiplied bilinear + mips)
    Sprites are treated as immutable for caching (mips / blur levels, keyed by identity + a 64-pixel
    fingerprint, LRU budget env FOSTER_SPRITE_CACHE_MB, default 256). Call invalidate(spr) after editing
    a sprite in place to be safe.
    shapes: disc(r, color, soft=1), ring(r, width, color, glow=0), radial(size, color, power=2),
        rrect_sdf(w, h, r, pad_px=0) (signed distance, <0 inside), rrect_alpha(w, h, r, pad_px=0),
        streak(w, h, color, core) (emissive light streak)

BLUR
    gblur(img, sigma, border='reflect'|'constant') -> any (h, w[, c]) float image; pyramid for sigma > 6
    disc_blur(img, radius) -> flat-disc bokeh blur (reduced resolution for radius > 7)

3D  (world units = canvas px at z=0 for the default camera; x right, y DOWN, z away from the viewer)
    cam = Cam(pos=(0, 0, -1500), yaw=0, pitch=0, roll=0, focal=1500 | fov=<vertical deg>, focus_dist=None
              (-> distance to the origin), aperture=0, max_coc=90, near=8)
        yaw>0 looks right, pitch>0 looks up, roll>0 rotates the camera clockwise (scene turns CCW).
        aperture = pupil diameter in world units: 0 = no DOF, 20 subtle, 40 soft, 80 dreamy.
        Cam.orbit(target=(0, 0, 0), dist=1500, yaw=0, pitch=0, roll=0, **kw) -> camera on a sphere looking at
            target (yaw>0 = camera moves right, pitch>0 = camera moves up and looks down; focus on target)
        cam.project(P) -> (N, 2) screen px, (N,) depth (nan behind);  cam.depth(p);  cam.to_cam(P)
        cam.coc(depth) -> depth-of-field blur RADIUS px;  cam.px_per_unit(depth);  cam.forward;  cam.K()
    plane_corners(center, width, height, rot=(rx, ry, rz), anchor=(.5, .5)) -> (4, 3) world TL, TR, BR, BL
        rot degrees: rx>0 tips the top edge toward the camera, ry>0 swings the right edge toward the camera,
        rz>0 spins clockwise on screen.  plane_point(center, width, height, rot, uv) -> world point(s) at
        normalised uv (u right, v down) - project it with cam.project to place cursors on tilted UI.
    draw_plane(canvas, spr, cam, center, width, rot=(0, 0, 0), opacity=1, mode='over', dof=True, height=None,
               blur=0, frost=0, anchor=(.5, .5), dof_scale=1) -> {'quad', 'poly', 'bbox', 'depth', 'coc'} | None
        Perspective-correct homography, near-plane clipping (cards may fly through the lens; quad is None
        then), mip-mapping, and depth of field that varies per pixel across tilted planes (rack focus
        along a dolly) by blending cached blur levels. Height keeps the sprite aspect unless given.
    draw_billboard(canvas, spr, cam, pos, width, rot=0, opacity=1, mode='over', dof=True, blur=0) -> camera-
        facing sprite at a world point (glows, chips, bokeh cards)
    Scene(cam): sc.plane(spr, center, width, **kw); sc.billboard(spr, pos, width, **kw);
        sc.custom(pos_or_depth, fn(canvas, cam)); sc.particles(parts, t, opacity=1); sc.render(canvas)
        -> draws back to front; particle sets are interleaved by depth between the items.

EFFECTS (in place on a canvas unless noted)
    glow(spr, color=None, sigmas=(4, 12, 32), strength=1, weights=None, include=True, source='alpha')
        -> NEW padded sprite (centre preserved): multi-radius 'deep glow' that is emissive (alpha 0, so plain
        'over' adds light), with the original on top when include=True. color None = sprite's own colours.
    bloom(canvas, threshold=0.8, strength=0.5, radii=(10, 30, 80), tint=None, knee=0.3)  (1/4 res)
    halation(canvas, strength=0.15, threshold=0.6, tint=(1, .32, .12), radius=10)
    anamorphic(canvas, threshold=1.0, strength=0.3, color=C['HOT_PINK'], length=0.6) horizontal streaks
    light_leak(canvas, t, colors=None, strength=0.6, seed=0, speed=1, sweep=None, angle=35, mode='screen')
        animated organic leak drifting in from the edges; sweep=0..1 instead makes a light band sweep
        across along `angle` (transitions).
    god_rays(canvas, center, strength=0.4, threshold=0.5, length=0.4, n=10, tint=None) volumetric shafts
    Particles(n=160, seed=0, box=((-1600, -2600, 300), (1600, 2600, 6500)), vel=(0, -18, 0),
              size=(1.2, 3.6), colors=None, twinkle=0.6, follow=True, bright=1.0, wander=30, min_energy=0.12)
        .draw(canvas, cam, t, opacity=1, zmin=None, zmax=None)  -> dust specks in focus, soft bokeh discs
        when defocused (DOF from cam), twinkling; follow=True wraps the box around the camera (endless).
        .positions(t, cam) -> (n, 3)
    vignette(canvas, amount=0.35, roundness=0.75, softness=1.6)
    chroma(canvas, amount=1.5, power=2.0) radial chromatic aberration: amount px at the corners, ~0 centre
    grain(canvas, t, amount=0.018, size=1.3) monochrome film grain (display-referred)
    flash(canvas, amount, color=IVORY) exposure x(1 + 3*amount) + 0.3*amount*color (3 = white-out)
    fade(canvas, amount, color=black)
    whip_blur(canvas, amount, angle=0) directional smear of `amount` px;  zoom_blur(canvas, amount,
        center=None) radial zoom-through blur, amount = scale spread (0.08 = 8 %), centre stays sharp
    shake(t, ...) see ANIMATION;  dot_grid(w, h, spacing=34, radius=1.6) -> alpha (cached, tileable);
    grid_floor(canvas, cam, y=600, spacing=200, extent=6000, color=HOT_PINK, opacity=0.35, width=1.2)
        anti-aliased perspective grid on the plane y = const, fading with distance

BACKGROUNDS / FINISHING
    background(look, t, cam=None, center=None, boost=0, dots=1, rim=1, seed=0, parallax=1, intensity=1)
        -> new opaque canvas. look 'neon' (NIGHT void, magenta aurora glows, orange planet-rim light, lit dot
        grid), 'amber' (warm orange/gold aurora, magenta accent), 'airy' (ivory paper with soft peach /
        lavender / pink / orange blooms). All drift slowly. With cam the backdrop pans / rolls / zooms like a
        distant plate (parallax 0..1). center=(x, y) normalised moves the main glow; boost (0..1) pumps the
        glow (beat pulses); dots / rim / intensity scale those parts (rim=0 hides the horizon).  ~40-130 ms.
    post(canvas, look, t, **overrides) -> finished canvas (alpha set to 1), in place: exposure, bloom +
        halation, optional anamorphic / leak / flash / fade, vignette, black tint, edge chroma, grain. ~90 ms.
        LOOKS[look] keys you can override: exposure, bloom, bloom_threshold, bloom_knee, bloom_radii,
        bloom_tint, halation, anamorphic, anamorphic_color, vignette, chroma, grain, black_tint, plus extras
        flash, flash_color, fade, fade_color, leak, leak_seed, leak_colors.
        e.g. post(cv, 'neon', t, flash=0.6 * impulse(t, 2.45), chroma=1.8 + 10 * whip)
        footage=0..1 for frames dominated by bright full-bleed footage (keeps whites clean, no milky bloom haze).

RENDER LOOP / ENCODE
    render_frame(draw_fn, t, samples=3, shutter=0.5) -> average of draw_fn(t_i) over sub-frame times
        across the shutter (0.5 = 180 degrees) centred on t: real motion blur. Use 5-7 samples on whips.
    with FFWriter(path, fps=30, crf=14, preset='slow') as fw: fw.write(to_srgb8(post(cv, LOOK, t), t))
        libx264 High, yuv420p, bt709 matrix + tags, +faststart; pix_fmt='yuv444p' for intermediates;
        audio='x.wav' muxes AAC 320k / 48 kHz; out_size=(w, h) rescales.
    save_png(path, canvas_or_u8, t=0) -> path (PNG or JPG);  sprite_preview(spr, bg) -> canvas for previews

PERFORMANCE (1 core, 1 sample): background 40-130 ms, post ~90 ms, to_srgb8 ~45 ms, a full-frame footage
plane ~60-110 ms; a typical frame (backdrop + footage plane + 6 sprites + particles + post) ~0.5 s.

EXAMPLE
    import core as K, footage as F
    clip = F.Clip('c12')
    def draw(t):
        cam = K.Cam(pos=(0, 0, -1500 + 80 * t), yaw=K.lerp(8, -4, K.EASE['easy_ease'](t / 3)), aperture=40)
        cv = K.background('neon', t, cam)
        card = clip.get(6.0 + t, 720, 1000, zoom=1.05, look='neon')
        K.draw_plane(cv, card, cam, (0, 0, 600 * (1 - K.ramp(t, 0, 1))), 760, rot=(4, -12, 0))
        return cv
    u8 = K.to_srgb8(K.post(K.render_frame(draw, 0.5, samples=5), 'neon', 0.5), 0.5)
"""
import collections
import functools
import math
import os
import subprocess
import weakref

for _v in ('OPENBLAS_NUM_THREADS', 'OMP_NUM_THREADS', 'MKL_NUM_THREADS'):
    os.environ.setdefault(_v, os.environ.get('FOSTER_BLAS_THREADS', '1'))   # only effective before numpy loads

import cv2  # noqa: E402
import numpy as np  # noqa: E402

cv2.setNumThreads(int(os.environ.get('FOSTER_CV_THREADS', '2')))


def tune_malloc():
    """Raise glibc's mmap threshold to its 32 MiB maximum so full-frame float buffers (33.2 MB) are
    recycled from the heap instead of being mmapped and page-faulted on every allocation (~30 % faster
    frames, far less system time). Called once at import; disable with env FOSTER_NO_MALLOPT=1."""
    if os.environ.get('FOSTER_NO_MALLOPT'):
        return False
    try:
        import ctypes
        libc = ctypes.CDLL('libc.so.6')
        ok = libc.mallopt(-3, 32 * 1024 * 1024) == 1          # M_MMAP_THRESHOLD
        libc.mallopt(-1, 1024 * 1024 * 1024)                    # M_TRIM_THRESHOLD
        return ok
    except (OSError, AttributeError):
        return False


tune_malloc()


def limit_blas_threads(n=1):
    """Limit numpy's OpenBLAS thread pool at runtime (its idle threads spin in sched_yield and steal CPU
    from the 4-core render pool). Called once at import with FOSTER_BLAS_THREADS (default 1)."""
    import ctypes
    done = False
    try:
        with open('/proc/self/maps') as f:
            libs = {l.split()[-1] for l in f if 'openblas' in l.lower() and l.strip().endswith('.so')}
    except OSError:
        libs = set()
    for path in libs:
        try:
            lib = ctypes.CDLL(path)
        except OSError:
            continue
        for fn in ('scipy_openblas_set_num_threads64_', 'openblas_set_num_threads64_', 'openblas_set_num_threads',
                   'scipy_openblas_set_num_threads'):
            f = getattr(lib, fn, None)
            if f is not None:
                f(int(n))
                done = True
                break
    return done


limit_blas_threads(int(os.environ.get('FOSTER_BLAS_THREADS', '1')))


# =============================================================================================== paths
REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))
WS = os.path.abspath(os.environ.get('FOSTER_WS', os.path.join(REPO, 'workspace3')))
FONTS = os.path.join(WS, 'fonts')
BRAND = os.path.join(WS, 'brand')
FRAMES = os.path.join(WS, 'frames')
SITE_IMG = os.path.join(WS, 'site_img')
ASSETS3D = os.path.join(WS, 'assets3d')
AUDIO = os.path.join(WS, 'audio')
OUT = os.path.join(WS, 'out')
SELFTEST = os.path.join(OUT, 'selftest')

W, H = 1080, 1920
FPS = 30
CX, CY = W / 2.0, H / 2.0


def font_path(name):
    """'Nunito-Black' -> absolute .ttf path in FONTS."""
    return os.path.join(FONTS, name if name.endswith('.ttf') else name + '.ttf')


# =============================================================================================== colour
def to_lin(x):
    """sRGB-encoded values (any shape) -> linear float32."""
    x = np.asarray(x, np.float32)
    return np.where(x <= 0.04045, x / 12.92, ((np.maximum(x, 0.04045) + 0.055) / 1.055) ** 2.4).astype(np.float32)


def to_srgb(x):
    """linear values (any shape) -> sRGB-encoded float32 (clipped to 0..1)."""
    x = np.clip(np.asarray(x, np.float32), 0.0, 1.0)
    return np.where(x <= 0.0031308, x * 12.92, 1.055 * np.power(np.maximum(x, 0.0031308), 1 / 2.4) - 0.055
                    ).astype(np.float32)


def hexlin(h):
    """'#B7006E' -> linear RGB np.float32[3]."""
    h = h.lstrip('#')
    return to_lin(np.array([int(h[i:i + 2], 16) for i in (0, 2, 4)], np.float32) / 255.0)


PALETTE_HEX = {
    'MAGENTA': '#B7006E', 'LOGO_MAGENTA': '#A6055E', 'HOT_PINK': '#FF3D9A',
    'ORANGE': '#FF6411', 'LOGO_ORANGE': '#F46308', 'AMBER': '#FFB15C',
    'LEAF': '#64A60B', 'LEAF_HI': '#A8E04A', 'PLUM': '#5B174F', 'INK': '#321F35',
    'NIGHT_0': '#0B0310', 'NIGHT_1': '#1C0822', 'IVORY': '#FCF8F5', 'PEACH': '#FFD4BA',
    'LAVENDER': '#F6EAF3', 'WHITE': '#FFFFFF', 'BLACK': '#000000',
}
C = {k: hexlin(v) for k, v in PALETTE_HEX.items()}

_LUMA = np.array([0.2126, 0.7152, 0.0722], np.float32)


def lum(rgb):
    """Rec.709 luminance of (..., 3) or (..., 4) array -> (...)."""
    rgb = np.asarray(rgb, np.float32)
    return rgb[..., :3] @ _LUMA


def _oklab(lin):
    lin = np.asarray(lin, np.float64)
    M1 = np.array([[0.4122214708, 0.5363325363, 0.0514459929], [0.2119034982, 0.6806995451, 0.1073969566],
                   [0.0883024619, 0.2817188376, 0.6299787005]])
    M2 = np.array([[0.2104542553, 0.7936177850, -0.0040720468], [1.9779984951, -2.4285922050, 0.4505937099],
                   [0.0259040371, 0.7827717662, -0.8086757660]])
    lms = np.cbrt(lin @ M1.T)
    return lms @ M2.T


def _oklab_inv(lab):
    lab = np.asarray(lab, np.float64)
    M2i = np.array([[1.0, 0.3963377774, 0.2158037573], [1.0, -0.1055613458, -0.0638541728],
                    [1.0, -0.0894841775, -1.2914855480]])
    M1i = np.array([[4.0767416621, -3.3077115913, 0.2309699292], [-1.2684380046, 2.6097574011, -0.3413193965],
                    [-0.0041960863, -0.7034186147, 1.7076147010]])
    lms = (lab @ M2i.T) ** 3
    return np.maximum(lms @ M1i.T, 0.0)


def mix(c0, c1, t, space='oklab'):
    """Mix two linear colours (t may be an array -> (..., 3)). space: 'oklab' | 'linear' | 'srgb'."""
    c0 = np.asarray(c0, np.float32)[:3]
    c1 = np.asarray(c1, np.float32)[:3]
    t = np.asarray(t, np.float32)[..., None]
    if space == 'linear':
        return (c0 * (1 - t) + c1 * t).astype(np.float32)
    if space == 'srgb':
        return to_lin(to_srgb(c0) * (1 - t) + to_srgb(c1) * t)
    a, b = _oklab(c0), _oklab(c1)
    return _oklab_inv(a * (1 - t) + b * t).astype(np.float32)


def _ramp_lut(stops, n=512):
    """Colour ramp LUT (n, 3) from stops [c, c, ...] or [(pos, c), ...] interpolated in OKLab."""
    if not isinstance(stops[0], (tuple, list)) or len(stops[0]) != 2 or np.ndim(stops[0][1]) == 0:
        k = len(stops)
        stops = [(i / max(1, k - 1), c) for i, c in enumerate(stops)]
    pos = np.array([s[0] for s in stops], np.float64)
    labs = np.array([_oklab(np.asarray(s[1], np.float64)[:3]) for s in stops])
    x = np.linspace(0, 1, n)
    lab = np.stack([np.interp(x, pos, labs[:, i]) for i in range(3)], 1)
    return _oklab_inv(lab).astype(np.float32)


def gradient(w, h, stops, angle=35.0, span=None):
    """Linear gradient image (h, w, 3) linear RGB. angle: degrees counter-clockwise from +x
    (0 = left->right, 90 = bottom->top). span=(p0, p1) optionally narrows where the ramp happens."""
    lut = _ramp_lut(stops)
    a = math.radians(angle)
    dx, dy = math.cos(a), -math.sin(a)
    ys, xs = np.mgrid[0:h, 0:w].astype(np.float32)
    proj = (xs + 0.5 - w / 2) * dx + (ys + 0.5 - h / 2) * dy
    ext = abs(w / 2 * dx) + abs(h / 2 * dy)
    u = (proj / max(ext, 1e-6) + 1) * 0.5
    if span is not None:
        u = (u - span[0]) / max(1e-6, span[1] - span[0])
    idx = np.clip(u * (len(lut) - 1), 0, len(lut) - 1).astype(np.int32)
    return lut[idx]


def brand_gradient(w, h, angle=35.0, c0=None, c1=None, alpha=None):
    """Signature MAGENTA -> ORANGE gradient sprite (h, w, 4). alpha: optional (h, w) coverage mask."""
    c0 = C['MAGENTA'] if c0 is None else c0
    c1 = C['ORANGE'] if c1 is None else c1
    rgb = gradient(w, h, [c0, c1], angle)
    a = np.ones((h, w), np.float32) if alpha is None else np.asarray(alpha, np.float32)
    return np.dstack([rgb * a[..., None], a]).astype(np.float32)


# ---- final conversion: tone shoulder + sRGB + blue-noise dither, all through one integer LUT
_SRGB_N = 16384        # LUT steps per unit of linear light
_SRGB_MAX = 4.0        # linear values above this clip


def _shoulder_curve(x, knee=0.82):
    """Soft highlight roll-off: identity below knee, asymptotic to 1.0 (reaches ~0.999 at 4)."""
    x = np.asarray(x, np.float64)
    k = knee
    over = np.maximum(x - k, 0.0)
    rng = 1.0 - k
    return np.where(x <= k, x, k + rng * (1 - np.exp(-over / rng * 1.0)) / (1 - math.exp(-(_SRGB_MAX - k) / rng)))


@functools.lru_cache(maxsize=4)
def _srgb16_lut(shoulder):
    """uint16 LUT: linear * _SRGB_N -> sRGB * 255 * 256 (8.8 fixed point, max 65280)."""
    x = np.arange(65536, dtype=np.float64) / _SRGB_N
    if shoulder:
        x = _shoulder_curve(x)
    x = np.clip(x, 0, 1)
    s = np.where(x <= 0.0031308, x * 12.92, 1.055 * np.power(np.maximum(x, 0.0031308), 1 / 2.4) - 0.055)
    return np.clip(np.round(s * 255.0 * 256.0), 0, 65280).astype(np.uint16)


@functools.lru_cache(maxsize=1)
def _blue_noise(n=64, seed=11):
    """Approximate blue-noise tile (high-pass filtered + rank equalised white noise), values in [0, 1)."""
    rng = np.random.default_rng(seed)
    a = rng.random((n, n)).astype(np.float32)
    for _ in range(8):
        lo = cv2.GaussianBlur(np.tile(a, (3, 3)), (0, 0), 1.3)[n:2 * n, n:2 * n]
        a = a - lo
        r = a.ravel().argsort().argsort().reshape(n, n)
        a = (r.astype(np.float32) + 0.5) / (n * n)
    return a


@functools.lru_cache(maxsize=2)
def _dither_base(w, h):
    """(h+64, w+64, 3) uint16 blue-noise thresholds in [0, 255], decorrelated per channel."""
    bn = _blue_noise()
    n = bn.shape[0]
    chans = [np.roll(np.roll(bn, 21 * c, 1), 43 * c, 0) for c in range(3)]
    chans[1] = chans[1].T
    tile3 = np.stack(chans, 2)
    full = np.tile(tile3, ((h + n) // n + 1, (w + n) // n + 1, 1))[:h + n, :w + n]
    return np.ascontiguousarray(np.floor(full * 256.0).clip(0, 255).astype(np.uint16))


def _dither_frame(w, h, phase):
    base = _dither_base(w, h)
    ox, oy = (phase * 37) % 64, (phase * 23) % 64
    return base[oy:oy + h, ox:ox + w]


def to_srgb8(canvas, t=0.0, dither=True, shoulder=True):
    """Final conversion of a linear canvas (h, w, 3|4) to uint8 sRGB (h, w, 3) RGB with a soft highlight
    shoulder and temporally varying blue-noise dither (+-0.5 LSB). Alpha is ignored (as if over black)."""
    c = canvas.shape[2]
    x = np.multiply(canvas, np.float32(_SRGB_N))
    x += np.float32(0.5)
    np.clip(x, 0, 65535.0, out=x)
    idx = x.astype(np.uint16)
    if c == 4:
        idx = cv2.cvtColor(idx, cv2.COLOR_RGBA2RGB)
    v = _srgb16_lut(bool(shoulder))[idx]
    if dither:
        ph = int(round(t * FPS * 7.0)) % 4096
        v = cv2.add(v, _dither_frame(v.shape[1], v.shape[0], ph))
        return cv2.convertScaleAbs(v, alpha=1 / 256.0, beta=-0.5)
    return cv2.convertScaleAbs(v, alpha=1 / 256.0)


# =============================================================================================== animation
def clamp(x, a=0.0, b=1.0):
    return a if x < a else b if x > b else x


def lerp(a, b, t):
    if isinstance(a, (tuple, list)):
        a = np.asarray(a, np.float64)
    if isinstance(b, (tuple, list)):
        b = np.asarray(b, np.float64)
    return a + (b - a) * t


def smoothstep(e0, e1, x):
    if e1 == e0:
        return 1.0 if x >= e1 else 0.0
    x = clamp((x - e0) / (e1 - e0))
    return x * x * (3 - 2 * x)


def linear(x):
    return clamp(x)


def in_expo(x):
    x = clamp(x)
    return 0.0 if x <= 0 else 2 ** (10 * x - 10)


def out_expo(x):
    x = clamp(x)
    return 1.0 if x >= 1 else 1 - 2 ** (-10 * x)


def inout_expo(x):
    x = clamp(x)
    if x <= 0:
        return 0.0
    if x >= 1:
        return 1.0
    return 2 ** (20 * x - 10) / 2 if x < 0.5 else (2 - 2 ** (-20 * x + 10)) / 2


def in_quint(x):
    return clamp(x) ** 5


def out_quint(x):
    return 1 - (1 - clamp(x)) ** 5


def inout_quint(x):
    x = clamp(x)
    return 16 * x ** 5 if x < 0.5 else 1 - (-2 * x + 2) ** 5 / 2


def in_quart(x):
    return clamp(x) ** 4


def out_quart(x):
    return 1 - (1 - clamp(x)) ** 4


def inout_quart(x):
    x = clamp(x)
    return 8 * x ** 4 if x < 0.5 else 1 - (-2 * x + 2) ** 4 / 2


def in_cubic(x):
    return clamp(x) ** 3


def out_cubic(x):
    return 1 - (1 - clamp(x)) ** 3


def inout_cubic(x):
    x = clamp(x)
    return 4 * x ** 3 if x < 0.5 else 1 - (-2 * x + 2) ** 3 / 2


def in_sine(x):
    return 1 - math.cos(clamp(x) * math.pi / 2)


def out_sine(x):
    return math.sin(clamp(x) * math.pi / 2)


def inout_sine(x):
    return -(math.cos(math.pi * clamp(x)) - 1) / 2


def in_circ(x):
    x = clamp(x)
    return 1 - math.sqrt(1 - x * x)


def out_circ(x):
    x = clamp(x)
    return math.sqrt(1 - (x - 1) ** 2)


def inout_circ(x):
    x = clamp(x)
    return (1 - math.sqrt(1 - (2 * x) ** 2)) / 2 if x < 0.5 else (math.sqrt(1 - (-2 * x + 2) ** 2) + 1) / 2


def in_back(x, s=1.70158):
    x = clamp(x)
    return (s + 1) * x ** 3 - s * x ** 2


def out_back(x, s=1.70158):
    x = clamp(x)
    return 1 + (s + 1) * (x - 1) ** 3 + s * (x - 1) ** 2


def inout_back(x, s=1.70158):
    x = clamp(x)
    c = s * 1.525
    return ((2 * x) ** 2 * ((c + 1) * 2 * x - c)) / 2 if x < 0.5 else \
        ((2 * x - 2) ** 2 * ((c + 1) * (x * 2 - 2) + c) + 2) / 2


def out_elastic(x, period=0.3, amp=1.0):
    x = clamp(x)
    if x <= 0 or x >= 1:
        return x
    return amp * 2 ** (-10 * x) * math.sin((x - period / 4) * (2 * math.pi) / period) + 1


def in_elastic(x, period=0.3, amp=1.0):
    return 1 - out_elastic(1 - clamp(x), period, amp)


def inout_elastic(x, period=0.45, amp=1.0):
    x = clamp(x)
    return in_elastic(2 * x, period, amp) / 2 if x < 0.5 else 0.5 + out_elastic(2 * x - 1, period, amp) / 2


class _Bezier:
    def __init__(self, x1, y1, x2, y2):
        self.c = (float(x1), float(y1), float(x2), float(y2))

    def __call__(self, x):
        x1, y1, x2, y2 = self.c
        x = clamp(float(x))
        if x <= 0 or x >= 1:
            return x

        def bx(u):
            return 3 * x1 * (1 - u) ** 2 * u + 3 * x2 * (1 - u) * u * u + u ** 3

        u = x
        for _ in range(8):
            d = 3 * x1 * (1 - u) ** 2 + 6 * (x2 - x1) * (1 - u) * u + 3 * (1 - x2) * u * u
            if abs(d) < 1e-7:
                break
            u2 = u - (bx(u) - x) / d
            if not 0 <= u2 <= 1:
                break
            u = u2
        if abs(bx(u) - x) > 1e-6:                      # robust bisection fallback
            lo, hi = 0.0, 1.0
            for _ in range(40):
                u = (lo + hi) / 2
                if bx(u) < x:
                    lo = u
                else:
                    hi = u
        return 3 * y1 * (1 - u) ** 2 * u + 3 * y2 * (1 - u) * u * u + u ** 3

    def __repr__(self):
        return 'bezier%r' % (self.c,)


@functools.lru_cache(maxsize=256)
def bezier(x1, y1, x2, y2):
    """CSS cubic-bezier timing function through (0,0), (x1,y1), (x2,y2), (1,1)."""
    return _Bezier(x1, y1, x2, y2)


def influence(out_pct=33.0, in_pct=33.0):
    """After Effects keyframe velocity: speed 0 at both keys, outgoing/incoming influence in percent.
    influence(80, 80) is the brief's camera 'easy ease'."""
    return bezier(out_pct / 100.0, 0.0, 1.0 - in_pct / 100.0, 1.0)


EASE = {
    'linear': linear, 'in_expo': in_expo, 'out_expo': out_expo, 'inout_expo': inout_expo,
    'in_quint': in_quint, 'out_quint': out_quint, 'inout_quint': inout_quint,
    'in_quart': in_quart, 'out_quart': out_quart, 'inout_quart': inout_quart,
    'in_cubic': in_cubic, 'out_cubic': out_cubic, 'inout_cubic': inout_cubic,
    'in_sine': in_sine, 'out_sine': out_sine, 'inout_sine': inout_sine,
    'in_circ': in_circ, 'out_circ': out_circ, 'inout_circ': inout_circ,
    'in_back': in_back, 'out_back': out_back, 'inout_back': inout_back,
    'out_elastic': out_elastic, 'in_elastic': in_elastic, 'inout_elastic': inout_elastic,
    'smooth': lambda x: smoothstep(0, 1, x),
    'easy': influence(33, 33), 'easy_ease': influence(80, 80), 'glide': influence(90, 90),
}
HOLD = 'hold'


def get_ease(spec):
    """Resolve an ease spec: callable | name | 'hold' | (out_pct, in_pct) | (x1, y1, x2, y2) | None."""
    if spec is None:
        return linear
    if callable(spec):
        return spec
    if isinstance(spec, str):
        if spec == HOLD:
            return HOLD
        return EASE[spec]
    spec = tuple(spec)
    if len(spec) == 2:
        return influence(*spec)
    if len(spec) == 4:
        return bezier(*spec)
    raise ValueError('bad ease spec %r' % (spec,))


def ramp(t, t0, t1, ease='out_expo'):
    """Eased 0..1 progress of t within [t0, t1] (0 before, 1 after)."""
    if t1 <= t0:
        return 1.0 if t >= t1 else 0.0
    e = get_ease(ease)
    return float(e(clamp((t - t0) / (t1 - t0))))


def remap(x, a0, a1, b0=0.0, b1=1.0, ease=None, clip=True):
    """Map x from [a0, a1] to [b0, b1] (optionally eased and clipped)."""
    u = (x - a0) / (a1 - a0) if a1 != a0 else (1.0 if x >= a1 else 0.0)
    if clip:
        u = clamp(u)
    if ease is not None:
        u = get_ease(ease)(u)
    return b0 + (b1 - b0) * u


class Track:
    """Keyframe track. keys: [(t, value), (t, value, ease_to_next), ...]; values scalar or vector.
    ease_to_next: any get_ease() spec, or 'hold' (value jumps at the next key). Returns float for scalar
    tracks and np.ndarray (float64) for vector tracks; clamps outside the key range."""

    def __init__(self, keys, ease='inout_cubic'):
        if not keys:
            raise ValueError('Track needs at least one key')
        self.scalar = np.ndim(keys[0][1]) == 0
        ks = []
        for k in keys:
            e = get_ease(k[2]) if len(k) > 2 else get_ease(ease)
            ks.append((float(k[0]), np.atleast_1d(np.asarray(k[1], np.float64)), e))
        ks.sort(key=lambda q: q[0])
        self.k = ks
        self.times = [q[0] for q in ks]

    def __call__(self, t):
        k = self.k
        if t <= k[0][0]:
            v = k[0][1]
        elif t >= k[-1][0]:
            v = k[-1][1]
        else:
            import bisect
            i = bisect.bisect_right(self.times, t) - 1
            t0, v0, e = k[i]
            t1, v1, _ = k[i + 1]
            if e == HOLD:
                v = v0
            else:
                v = v0 + (v1 - v0) * e((t - t0) / (t1 - t0))
        return float(v[0]) if self.scalar else np.array(v, np.float64)

    def vel(self, t, dt=1e-3):
        """Numerical derivative (units per second)."""
        return (np.asarray(self(t + dt)) - np.asarray(self(t - dt))) / (2 * dt)

    @property
    def start(self):
        return self.k[0][0]

    @property
    def end(self):
        return self.k[-1][0]


def spring(t, freq=2.0, damping=0.4):
    """Unit step response of a damped spring, t seconds after release: 0 -> 1 with overshoot.
    freq in Hz (higher = snappier), damping 0..1 (lower = more bounce)."""
    if t <= 0:
        return 0.0
    w = 2 * math.pi * freq
    z = damping
    if z < 1:
        wd = w * math.sqrt(1 - z * z)
        return 1 - math.exp(-z * w * t) * (math.cos(wd * t) + z * w / wd * math.sin(wd * t))
    return 1 - math.exp(-w * t) * (1 + w * t)


def _hash1(i, seed):
    v = math.sin(i * 127.1 + seed * 311.7 + 0.123) * 43758.5453123
    return (v - math.floor(v)) * 2.0 - 1.0


def _gnoise1(x, seed):
    i = math.floor(x)
    f = x - i
    g0, g1 = _hash1(i, seed), _hash1(i + 1, seed)
    u = f * f * f * (f * (f * 6 - 15) + 10)
    return (g0 * f) * (1 - u) + (g1 * (f - 1)) * u


def wiggle(t, freq=1.0, amp=1.0, seed=0, octaves=2):
    """Smooth, non-periodic 1D gradient noise (AE wiggle-like) in roughly [-amp, amp]."""
    v, a, f, norm = 0.0, 1.0, freq, 0.0
    for o in range(octaves):
        v += a * _gnoise1(t * f + o * 17.31, seed * 7 + o)
        norm += a
        a *= 0.5
        f *= 2.07
    return amp * 2.0 * v / norm


def shake(t, amp=12.0, freq=14.0, seed=0):
    """Camera shake offsets (dx, dy, rot_deg). Scale by impulse() to make hits decay."""
    return (wiggle(t, freq, amp, seed, 2), wiggle(t, freq, amp, seed + 101, 2),
            wiggle(t, freq * 0.8, amp * 0.06, seed + 202, 2))


def impulse(t, t0, decay=7.0, attack=0.02):
    """Envelope: 0 before t0, rises over `attack` s to 1, then exp(-decay * dt)."""
    u = t - t0
    if u < 0:
        return 0.0
    if u < attack:
        return out_sine(u / attack)
    return math.exp(-decay * (u - attack))


def beat(n, bpm, offset=0.0):
    """Time (s) of beat n."""
    return offset + n * 60.0 / bpm


def beat_index(t, bpm, offset=0.0):
    return (t - offset) * bpm / 60.0


def beat_pulse(t, bpm, offset=0.0, decay=6.0):
    """1 at each beat, decaying exponentially until the next beat (0 before offset)."""
    if t < offset:
        return 0.0
    ph = (t - offset) % (60.0 / bpm)
    return math.exp(-decay * ph)


# =============================================================================================== canvas
def new_canvas(rgb=None, w=W, h=H):
    """Transparent canvas (rgb None) or an opaque solid colour canvas, (h, w, 4) float32."""
    cv = np.zeros((h, w, 4), np.float32)
    if rgb is not None:
        cv[..., :3] = np.asarray(rgb, np.float32)[:3]
        cv[..., 3] = 1.0
    return cv


def _blend(dst, src, opacity=1.0, mode='over'):
    """Composite premultiplied src onto dst (same shape views, 4 channels), in place."""
    if opacity <= 0:
        return dst
    if opacity != 1.0:
        src = src * np.float32(opacity)
    if mode == 'over':
        a = src[..., 3:4]
        dst *= 1.0 - a
        dst += src
    elif mode == 'add':
        dst[..., :3] += src[..., :3]
        da = dst[..., 3]
        da += src[..., 3] * (1.0 - da)
    elif mode == 'screen':
        d = dst[..., :3]
        d += src[..., :3] * (1.0 - np.clip(d, 0.0, 1.0))
        da = dst[..., 3]
        da += src[..., 3] * (1.0 - da)
    elif mode == 'multiply':
        sa = src[..., 3:4]
        da = dst[..., 3:4].copy()
        dst[..., :3] = src[..., :3] * dst[..., :3] + src[..., :3] * (1 - da) + dst[..., :3] * (1 - sa)
        dst[..., 3:4] = sa + da * (1 - sa)
    elif mode == 'erase':
        dst *= 1.0 - src[..., 3:4]
    else:
        raise ValueError('unknown blend mode %r' % mode)
    return dst


def over(dst, src, opacity=1.0):
    return _blend(dst, src, opacity, 'over')


def add(dst, src, opacity=1.0):
    return _blend(dst, src, opacity, 'add')


def screen(dst, src, opacity=1.0):
    return _blend(dst, src, opacity, 'screen')


def multiply(dst, src, opacity=1.0):
    return _blend(dst, src, opacity, 'multiply')


@functools.lru_cache(maxsize=1)
def _lin_lut8():
    return to_lin(np.arange(256, dtype=np.float32) / 255.0)


def sprite(img, srgb=True):
    """Convert to a premultiplied linear float32 RGBA sprite.
    Accepts PIL.Image, uint8/uint16 arrays (h,w), (h,w,3) RGB or (h,w,4) RGBA (straight alpha, sRGB),
    or float arrays (h,w,4) which are assumed to be premultiplied linear already (returned as float32)."""
    if hasattr(img, 'convert') and hasattr(img, 'size'):
        img = np.asarray(img.convert('RGBA'))
    a = np.asarray(img)
    if a.dtype in (np.float32, np.float64) and a.ndim == 3 and a.shape[2] == 4:
        return np.ascontiguousarray(a, np.float32)
    if a.dtype == np.uint16:
        f = a.astype(np.float32) / 65535.0
        if a.ndim == 2:
            f = np.dstack([f, f, f])
        rgb = to_lin(f[..., :3]) if srgb else f[..., :3]
        al = f[..., 3] if f.shape[2] == 4 else np.ones(f.shape[:2], np.float32)
    else:
        if a.dtype != np.uint8:
            a = np.clip(a, 0, 255).astype(np.uint8)
        if a.ndim == 2:
            a = np.dstack([a, a, a])
        rgb = cv2.LUT(np.ascontiguousarray(a[..., :3]), _lin_lut8()) if srgb else a[..., :3].astype(np.float32) / 255
        al = a[..., 3].astype(np.float32) / 255.0 if a.shape[2] == 4 else np.ones(a.shape[:2], np.float32)
    out = np.empty(rgb.shape[:2] + (4,), np.float32)
    out[..., :3] = rgb * al[..., None]
    out[..., 3] = al
    return out


@functools.lru_cache(maxsize=64)
def _load_image_cached(path, size, scale):
    im = cv2.imread(path, cv2.IMREAD_UNCHANGED)
    if im is None:
        from PIL import Image
        im = np.asarray(Image.open(path).convert('RGBA'))[..., [2, 1, 0, 3]]
    if im.dtype == np.uint16 and im.ndim == 3:
        pass
    if im.ndim == 2:
        im = cv2.cvtColor(im, cv2.COLOR_GRAY2BGR)
    if im.shape[2] == 3:
        im = cv2.cvtColor(im, cv2.COLOR_BGR2RGB)
    else:
        im = cv2.cvtColor(im, cv2.COLOR_BGRA2RGBA)
    h0, w0 = im.shape[:2]
    if size is not None:
        if isinstance(size, int):
            size = (size, max(1, int(round(h0 * size / w0))))
        tw, th = size
    elif scale is not None:
        tw, th = max(1, int(round(w0 * scale))), max(1, int(round(h0 * scale)))
    else:
        tw, th = w0, h0
    spr = sprite(im)
    if (tw, th) != (w0, h0):
        spr = cv2.resize(spr, (tw, th), interpolation=cv2.INTER_AREA if tw < w0 else cv2.INTER_CUBIC)
        spr[..., 3] = np.clip(spr[..., 3], 0, 1)
    spr.setflags(write=False)
    return spr


def load_image(path, size=None, scale=None):
    """Load PNG/JPG/WEBP as a (read-only, cached) sprite. size=(w, h) or width (keeps aspect)."""
    if isinstance(size, list):
        size = tuple(size)
    return _load_image_cached(os.path.abspath(path), size, scale)


def pad(spr, p):
    """Transparent padding of p px on every side (centre is preserved)."""
    p = int(p)
    return cv2.copyMakeBorder(spr, p, p, p, p, cv2.BORDER_CONSTANT, value=(0, 0, 0, 0)) if p > 0 else spr


def tint(spr, rgb, amount=1.0):
    """Recolour a sprite towards rgb (keeps alpha)."""
    out = spr.copy()
    col = np.asarray(rgb, np.float32)[:3]
    out[..., :3] = spr[..., :3] * (1 - amount) + spr[..., 3:4] * col * amount
    return out


def with_opacity(spr, k):
    return spr * np.float32(k)


def alpha_bbox(spr, thresh=1e-3):
    """(x0, y0, x1, y1) of alpha > thresh, or None."""
    a = spr[..., 3] > thresh
    ys = np.flatnonzero(a.any(1))
    xs = np.flatnonzero(a.any(0))
    if len(xs) == 0:
        return None
    return int(xs[0]), int(ys[0]), int(xs[-1]) + 1, int(ys[-1]) + 1


def crop_to_alpha(spr, margin=4):
    bb = alpha_bbox(spr)
    if bb is None:
        return spr[:1, :1]
    x0, y0, x1, y1 = bb
    h, w = spr.shape[:2]
    return spr[max(0, y0 - margin):min(h, y1 + margin), max(0, x0 - margin):min(w, x1 + margin)]


# ---- sprite-derived caches (mip levels, blur levels), keyed by object identity with weakrefs
class _SpriteCache:
    def __init__(self, budget_mb=320):
        self.d = collections.OrderedDict()
        self.bytes = 0
        self.budget = budget_mb * 1024 * 1024
        self.refs = {}
        self.fps = {}

    def _drop_owner(self, oid):
        for k in [k for k in self.d if k[0] == oid]:
            self.bytes -= self.d.pop(k).nbytes
        self.refs.pop(oid, None)
        self.fps.pop(oid, None)

    def invalidate(self, spr):
        self._drop_owner(id(spr))

    @staticmethod
    def _fingerprint(spr):
        h, w = spr.shape[:2]
        sub = spr[::max(1, h // 7), ::max(1, w // 7)]
        return (h, w, hash(np.ascontiguousarray(sub).tobytes()))

    def get(self, spr, key, fn):
        oid = id(spr)
        ref = self.refs.get(oid)
        fp = self._fingerprint(spr)
        if ref is None or ref() is not spr or self.fps.get(oid) != fp:
            if ref is not None:
                self._drop_owner(oid)
            try:
                self.refs[oid] = weakref.ref(spr, lambda _r, o=oid: self._drop_owner(o))
            except TypeError:
                return fn()
            self.fps[oid] = fp
        k = (oid,) + key
        v = self.d.get(k)
        if v is not None:
            self.d.move_to_end(k)
            return v
        v = fn()
        self.d[k] = v
        self.bytes += v.nbytes
        while self.bytes > self.budget and len(self.d) > 1:
            _, old = self.d.popitem(last=False)
            self.bytes -= old.nbytes
        return v


_CACHE = _SpriteCache(int(os.environ.get('FOSTER_SPRITE_CACHE_MB', '256')))


def invalidate(spr):
    """Forget cached mip / blur levels of a sprite you mutated in place (a cheap 64-pixel fingerprint also
    catches most in-place edits automatically)."""
    _CACHE.invalidate(spr)


def _mip_level(spr, k):
    """Sprite downscaled by 2**k (k >= 0), cached."""
    if k <= 0:
        return spr

    def make():
        prev = _mip_level(spr, k - 1)
        h, w = prev.shape[:2]
        return cv2.resize(prev, (max(1, (w + 1) // 2), max(1, (h + 1) // 2)), interpolation=cv2.INTER_AREA)
    return _CACHE.get(spr, ('mip', k), make)


_SIG_STEP = 2 ** (1 / 9.0)        # blur buckets: 8 % steps
_SIG_MIN = 0.35


def _sigma_bucket(s):
    if s < _SIG_MIN:
        return 0
    return int(round(math.log(s / _SIG_MIN) / math.log(_SIG_STEP))) + 1


def _bucket_sigma(b):
    return 0.0 if b <= 0 else _SIG_MIN * _SIG_STEP ** (b - 1)


def _level(spr, k, b):
    """Mip level k blurred by sigma bucket b, padded. Returns (array, pad_px, fx, fy) where fx/fy are
    level px per sprite px."""
    base = _mip_level(spr, k)
    sh, sw = spr.shape[:2]
    lh, lw = base.shape[:2]
    if b <= 0:
        return base, 0, lw / sw, lh / sh
    # a sigma beyond the level's own size only flattens it further; clamping keeps the cache key and the
    # padding bounded when a sprite is drawn near-zero-sized (blur / scale -> huge, e.g. a scale-0 pop-in)
    b = min(b, _sigma_bucket(max(lw, lh) + 8.0))
    sig = _bucket_sigma(b)
    p = int(math.ceil(sig * 3.0)) + 1

    def make():
        return gblur(pad(base, p), sig, border='constant')
    return _CACHE.get(spr, ('blur', k, b), make), p, lw / sw, lh / sh


def _choose_level(scale, blur_px):
    """mip level k and fractional trilinear weight for a minification `scale` (screen px per sprite px),
    plus an extra downscale when a big blur makes resolution pointless."""
    k_blur = 0
    if blur_px > 2.5:
        k_blur = int(math.floor(math.log2(blur_px / 2.5)))
    if scale >= 1.0:
        kf = 0.0
    else:
        kf = math.log2(1.0 / max(scale, 1e-6))
    kf = max(kf, float(k_blur))
    kf = min(kf, 10.0)
    return kf


def _comp_region(canvas, out, x0, y0, opacity, mode, frost=0.0, frost_gain=6.0):
    reg = canvas[y0:y0 + out.shape[0], x0:x0 + out.shape[1]]
    if frost and frost > 0.3:
        _frost_region(canvas, out[..., 3], x0, y0, frost, frost_gain * min(1.0, opacity * 1.5))
    _blend(reg, out, opacity, mode)


def _frost_region(canvas, alpha, x0, y0, sigma, gain):
    h, w = alpha.shape
    m = int(math.ceil(sigma * 2))
    X0, Y0 = max(0, x0 - m), max(0, y0 - m)
    X1, Y1 = min(canvas.shape[1], x0 + w + m), min(canvas.shape[0], y0 + h + m)
    big = canvas[Y0:Y1, X0:X1, :3]
    bl = gblur(big, sigma)
    bl = bl[y0 - Y0:y0 - Y0 + h, x0 - X0:x0 - X0 + w]
    k = np.clip(alpha * gain, 0, 1)[..., None]
    reg = canvas[y0:y0 + h, x0:x0 + w, :3]
    reg += (bl - reg) * k


def _warp_affine_levels(spr, A, bw, bh, kf, blur_px, scale):
    """Warp sprite (continuous affine A: sprite coords -> local dst coords) with trilinear mips."""
    k0 = int(math.floor(kf))
    wfrac = kf - k0
    outs = []
    for k, wgt in ((k0, 1 - wfrac), (k0 + 1, wfrac)):
        if wgt < 0.04:
            continue
        lvl_scale = scale * (2 ** k)                     # screen px per level px
        sig_l = blur_px / lvl_scale if blur_px > 0 else 0.0
        arr, p, fx, fy = _level(spr, k, _sigma_bucket(sig_l))
        S = np.array([[1 / fx, 0, (0.5 - p) / fx], [0, 1 / fy, (0.5 - p) / fy], [0, 0, 1]], np.float64)
        M = (A @ S)
        M[0, 2] -= 0.5
        M[1, 2] -= 0.5
        o = cv2.warpAffine(arr, M[:2], (bw, bh), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT,
                           borderValue=(0, 0, 0, 0))
        outs.append((o, wgt))
    if len(outs) == 1:
        return outs[0][0]
    (a, wa), (b, wb) = outs
    return a * np.float32(wa / (wa + wb)) + b * np.float32(wb / (wa + wb))


def draw(canvas, spr, cx, cy, scale=1.0, rot=0.0, opacity=1.0, mode='over', anchor=(0.5, 0.5), blur=0.0,
         frost=0.0):
    """Draw a sprite with its anchor at canvas position (cx, cy). Sub-pixel accurate, mip-mapped.
    scale: float or (sx, sy); rot: degrees clockwise; blur: gaussian sigma in screen px;
    frost: sigma (px) of a frosted-glass blur applied to the canvas under the sprite's alpha.
    Returns the touched bbox (x0, y0, x1, y1) or None."""
    if opacity <= 1e-4 or spr is None:
        return None
    sh, sw = spr.shape[:2]
    if isinstance(scale, (tuple, list, np.ndarray)):
        sx, sy = float(scale[0]), float(scale[1])
    else:
        sx = sy = float(scale)
    if abs(sx) < 1e-5 or abs(sy) < 1e-5:
        return None
    ax, ay = anchor[0] * sw, anchor[1] * sh
    r = math.radians(rot)
    c, s = math.cos(r), math.sin(r)
    # continuous mapping: X = R S (U - a) + center
    A = np.array([[c * sx, -s * sy, 0.0], [s * sx, c * sy, 0.0], [0, 0, 1.0]])
    A[0, 2] = cx - (A[0, 0] * ax + A[0, 1] * ay)
    A[1, 2] = cy - (A[1, 0] * ax + A[1, 1] * ay)
    corners = np.array([[0, 0, 1], [sw, 0, 1], [sw, sh, 1], [0, sh, 1]], np.float64) @ A.T
    m = 2 + int(math.ceil(blur * 3.0))
    x0 = int(math.floor(corners[:, 0].min())) - m
    y0 = int(math.floor(corners[:, 1].min())) - m
    x1 = int(math.ceil(corners[:, 0].max())) + m
    y1 = int(math.ceil(corners[:, 1].max())) + m
    X0, Y0 = max(0, x0), max(0, y0)
    X1, Y1 = min(canvas.shape[1], x1), min(canvas.shape[0], y1)
    if X1 <= X0 or Y1 <= Y0:
        return None
    # integer fast path
    if (sx == 1.0 and sy == 1.0 and rot == 0.0 and blur <= 0.0):
        fx, fy = cx - ax, cy - ay
        if abs(fx - round(fx)) < 1e-3 and abs(fy - round(fy)) < 1e-3:
            ix, iy = int(round(fx)), int(round(fy))
            u0, v0 = max(0, -ix), max(0, -iy)
            u1, v1 = min(sw, canvas.shape[1] - ix), min(sh, canvas.shape[0] - iy)
            if u1 <= u0 or v1 <= v0:
                return None
            _comp_region(canvas, spr[v0:v1, u0:u1], ix + u0, iy + v0, opacity, mode, frost)
            return ix + u0, iy + v0, ix + u1, iy + v1
    scl = math.sqrt(abs(sx * sy))
    kf = _choose_level(scl, blur)
    Al = A.copy()
    Al[0, 2] -= X0
    Al[1, 2] -= Y0
    out = _warp_affine_levels(spr, Al, X1 - X0, Y1 - Y0, kf, blur, scl)
    _comp_region(canvas, out, X0, Y0, opacity, mode, frost)
    return X0, Y0, X1, Y1


def _homography_from_quad(sw, sh, quad):
    src = np.float32([[0, 0], [sw, 0], [sw, sh], [0, sh]])
    return cv2.getPerspectiveTransform(src, np.float32(quad)).astype(np.float64)


def _warp_homography(canvas, spr, Hc, poly, opacity=1.0, mode='over', blur_px=0.0, frost=0.0,
                     blur_map=None, blur_levels=None, clip_poly=False):
    """Core perspective warp. Hc: 3x3 sprite continuous coords -> canvas continuous coords.
    poly: (N, 2) screen polygon of the visible part (used for bbox, and as a mask when clip_poly).
    blur_map: optional (x0, y0, map) per-pixel blur sigma (screen px) with blur_levels (list of sigmas)."""
    sh, sw = spr.shape[:2]
    if not np.isfinite(poly).all():
        return None
    px_, py_ = poly[:, 0], poly[:, 1]
    if 0.5 * abs(float(np.dot(px_, np.roll(py_, -1)) - np.dot(py_, np.roll(px_, -1)))) < 0.02:
        return None                                   # degenerate / sub-pixel footprint: nothing visible
    pad_px = 2 + int(math.ceil(3 * max(blur_px, max(blur_levels) if blur_levels else 0.0)))
    x0 = int(math.floor(poly[:, 0].min())) - pad_px
    y0 = int(math.floor(poly[:, 1].min())) - pad_px
    x1 = int(math.ceil(poly[:, 0].max())) + pad_px
    y1 = int(math.ceil(poly[:, 1].max())) + pad_px
    X0, Y0 = max(0, x0), max(0, y0)
    X1, Y1 = min(canvas.shape[1], x1), min(canvas.shape[0], y1)
    if X1 <= X0 or Y1 <= Y0:
        return None
    bw, bh = X1 - X0, Y1 - Y0
    # minification estimate: linear scale at the visible centroid via |det H| / w^3
    detH = abs(np.linalg.det(Hc))
    try:
        Hi = np.linalg.inv(Hc)
    except np.linalg.LinAlgError:
        return None
    pts = np.c_[poly, np.ones(len(poly))]
    uvw = pts @ Hi.T
    uv = uvw[:, :2] / uvw[:, 2:3]
    ws = []
    for u, v in uv:
        wv = Hc[2, 0] * u + Hc[2, 1] * v + Hc[2, 2]
        ws.append(math.sqrt(detH / max(abs(wv) ** 3, 1e-12)))
    ws = np.array(ws)
    scale = float(math.sqrt(ws.min() * ws.max()))
    T = np.array([[1, 0, -X0 - 0.5], [0, 1, -Y0 - 0.5], [0, 0, 1]], np.float64)

    def warp_one(sig_screen):
        kf = _choose_level(scale, sig_screen)
        k0 = int(math.floor(kf))
        wfrac = kf - k0
        acc = None
        tot = 0.0
        for k, wgt in ((k0, 1 - wfrac), (k0 + 1, wfrac)):
            if wgt < 0.04:
                continue
            lvl_scale = scale * (2 ** k)
            sig_l = sig_screen / lvl_scale if sig_screen > 0 else 0.0
            arr, p, fx, fy = _level(spr, k, _sigma_bucket(sig_l))
            S = np.array([[1 / fx, 0, (0.5 - p) / fx], [0, 1 / fy, (0.5 - p) / fy], [0, 0, 1]], np.float64)
            M = T @ Hc @ S
            o = cv2.warpPerspective(arr, M, (bw, bh), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT,
                                    borderValue=(0, 0, 0, 0))
            if acc is None:
                acc = o * np.float32(wgt) if wgt != 1 else o
            else:
                acc += o * np.float32(wgt)
            tot += wgt
        if tot != 1.0:
            acc *= np.float32(1.0 / tot)
        return acc

    if blur_map is not None and blur_levels:
        levels = list(blur_levels)
        bx, by, bmap = blur_map
        bm = bmap[Y0 - by:Y1 - by, X0 - bx:X1 - bx]
        outs = [warp_one(s) for s in levels]
        out = np.zeros_like(outs[0])
        # piecewise-linear weights over the sorted levels
        for i, s in enumerate(levels):
            if len(levels) == 1:
                wgt = np.ones_like(bm)
            else:
                lo = levels[i - 1] if i > 0 else None
                hi = levels[i + 1] if i < len(levels) - 1 else None
                wgt = np.ones_like(bm)
                if lo is not None:
                    wgt = np.where(bm < s, np.clip((bm - lo) / max(s - lo, 1e-6), 0, 1), wgt)
                if hi is not None:
                    wgt = np.where(bm >= s, np.clip((hi - bm) / max(hi - s, 1e-6), 0, 1), wgt)
            out += outs[i] * wgt[..., None].astype(np.float32)
    else:
        out = warp_one(blur_px)
    if clip_poly:
        mask = np.zeros((bh, bw), np.uint8)
        P = np.round((poly - [X0 + 0.5, Y0 + 0.5]) * 16).astype(np.int32)
        cv2.fillPoly(mask, [P], 255, cv2.LINE_AA, shift=4)
        out *= (mask.astype(np.float32) / 255.0)[..., None]
    _comp_region(canvas, out, X0, Y0, opacity, mode, frost)
    return X0, Y0, X1, Y1


def draw_quad(canvas, spr, quad, opacity=1.0, mode='over', blur=0.0, frost=0.0):
    """Warp sprite so its corners land on quad (4x2: TL, TR, BR, BL, canvas px). Premultiplied
    bilinear filtering with mip-mapping. Returns bbox or None."""
    if opacity <= 1e-4:
        return None
    q = np.asarray(quad, np.float64).reshape(4, 2)
    sh, sw = spr.shape[:2]
    Hc = _homography_from_quad(sw, sh, q)
    return _warp_homography(canvas, spr, Hc, q, opacity, mode, blur, frost)


# ---- shapes
def disc(r, color=(1, 1, 1), soft=1.0, opacity=1.0):
    """Anti-aliased filled disc sprite of radius r (px)."""
    n = int(math.ceil(r + soft + 2))
    yy, xx = np.mgrid[-n:n + 1, -n:n + 1].astype(np.float32)
    d = np.sqrt(xx * xx + yy * yy)
    a = np.clip((r - d) / max(soft, 1e-3) + 0.5, 0, 1) * opacity
    col = np.asarray(color, np.float32)[:3]
    return np.dstack([a[..., None] * col, a]).astype(np.float32)


def ring(r, width, color=(1, 1, 1), glow=0.0, opacity=1.0):
    """Anti-aliased ring sprite; glow>0 adds an emissive falloff (px)."""
    n = int(math.ceil(r + width + 3 * glow + 3))
    yy, xx = np.mgrid[-n:n + 1, -n:n + 1].astype(np.float32)
    d = np.abs(np.sqrt(xx * xx + yy * yy) - r) - width / 2
    a = np.clip(0.5 - d, 0, 1) * opacity
    col = np.asarray(color, np.float32)[:3]
    spr = np.dstack([a[..., None] * col, a]).astype(np.float32)
    if glow > 0:
        g = np.exp(-np.maximum(d, 0) / glow) * 0.6 * opacity
        spr[..., :3] += g[..., None] * col
    return spr


def radial(size, color=(1, 1, 1), power=2.0, opacity=1.0):
    """Soft radial falloff sprite (size x size), alpha = (1 - r)^power."""
    yy, xx = np.mgrid[0:size, 0:size].astype(np.float32)
    rr = np.sqrt((xx - size / 2 + 0.5) ** 2 + (yy - size / 2 + 0.5) ** 2) / (size / 2)
    a = np.clip(1 - rr, 0, 1) ** power * opacity
    col = np.asarray(color, np.float32)[:3]
    return np.dstack([a[..., None] * col, a]).astype(np.float32)


def rrect_sdf(w, h, r, pad_px=0, ss=1.0):
    """Signed distance (px, negative inside) of a w x h rounded rectangle, on a (h+2p, w+2p) grid."""
    ys, xs = np.mgrid[0:h + 2 * pad_px, 0:w + 2 * pad_px].astype(np.float32)
    xs = xs + 0.5 - pad_px - w / 2
    ys = ys + 0.5 - pad_px - h / 2
    qx = np.abs(xs) - (w / 2 - r)
    qy = np.abs(ys) - (h / 2 - r)
    return np.sqrt(np.maximum(qx, 0) ** 2 + np.maximum(qy, 0) ** 2) + np.minimum(np.maximum(qx, qy), 0) - r


def rrect_alpha(w, h, r, pad_px=0):
    """Anti-aliased rounded-rect coverage (h+2p, w+2p) float32."""
    return np.clip(0.5 - rrect_sdf(w, h, r, pad_px), 0, 1).astype(np.float32)


def streak(w, h, color=(1, 1, 1), core=(1, 1, 1)):
    """Horizontal light streak sprite (emissive, alpha 0)."""
    ys, xs = np.mgrid[0:h, 0:w].astype(np.float32)
    x = (xs - w / 2) / (w / 2)
    y = (ys - h / 2) / (h / 2)
    fall = np.clip(1 - np.abs(x), 0, 1) ** 1.6
    a = np.exp(-(y * 4) ** 2) * fall
    cc = np.exp(-(y * 16) ** 2) * np.clip(1 - np.abs(x) * 1.5, 0, 1) ** 2
    rgb = a[..., None] * np.asarray(color, np.float32)[:3] + cc[..., None] * np.asarray(core, np.float32)[:3]
    return np.dstack([rgb, np.zeros((h, w), np.float32)]).astype(np.float32)


# =============================================================================================== blur
def gblur(img, sigma, border='reflect'):
    """Gaussian blur (sigma px) of an (h, w[, c]) float32 image. Large sigmas use a downscale pyramid.
    border: 'reflect' (default) or 'constant' (zeros, for sprites)."""
    if sigma < 0.3:
        return img.copy()
    bmode = cv2.BORDER_CONSTANT if border == 'constant' else cv2.BORDER_REFLECT101
    h, w = img.shape[:2]
    if sigma <= 6.0 or min(h, w) < 16:
        return cv2.GaussianBlur(img, (0, 0), sigma, borderType=bmode)
    f = 2 ** int(math.floor(math.log2(sigma / 3.0)))
    f = max(1, min(f, max(1, min(h, w) // 4)))
    if f <= 1:
        return cv2.GaussianBlur(img, (0, 0), sigma, borderType=bmode)
    sw, sh = max(1, int(math.ceil(w / f))), max(1, int(math.ceil(h / f)))
    if border == 'constant':
        # pad to a multiple so edges stay transparent
        small = cv2.resize(img, (sw, sh), interpolation=cv2.INTER_AREA)
    else:
        small = cv2.resize(img, (sw, sh), interpolation=cv2.INTER_AREA)
    s2 = math.sqrt(max(sigma ** 2 - (0.5 * f) ** 2, 0.25)) / f
    small = cv2.GaussianBlur(small, (0, 0), s2, borderType=bmode)
    return cv2.resize(small, (w, h), interpolation=cv2.INTER_LINEAR)


@functools.lru_cache(maxsize=64)
def _disc_kernel(r):
    n = int(math.ceil(r)) * 2 + 1
    yy, xx = np.mgrid[:n, :n] - n // 2
    k = np.clip(r + 0.5 - np.hypot(xx, yy), 0, 1).astype(np.float32)
    return k / k.sum()


def disc_blur(img, radius):
    """Bokeh-style lens blur with a flat disc kernel of `radius` px. Large radii run at reduced res."""
    if radius < 0.6:
        return img.copy()
    h, w = img.shape[:2]
    if radius > 7:
        f = 6.0 / radius
        sw, sh = max(1, int(round(w * f))), max(1, int(round(h * f)))
        small = cv2.resize(img, (sw, sh), interpolation=cv2.INTER_AREA)
        small = cv2.filter2D(small, -1, _disc_kernel(6.0), borderType=cv2.BORDER_REFLECT101)
        return cv2.resize(small, (w, h), interpolation=cv2.INTER_LINEAR)
    return cv2.filter2D(img, -1, _disc_kernel(round(radius * 2) / 2), borderType=cv2.BORDER_REFLECT101)


# =============================================================================================== 3D
def _rot(rx, ry, rz):
    """R = Ry(ry) @ Rx(rx) @ Rz(rz), degrees, for y-down / z-forward coordinates."""
    rx, ry, rz = (math.radians(a) for a in (rx, ry, rz))
    cx_, sx_ = math.cos(rx), math.sin(rx)
    cy_, sy_ = math.cos(ry), math.sin(ry)
    cz_, sz_ = math.cos(rz), math.sin(rz)
    Rx = np.array([[1, 0, 0], [0, cx_, -sx_], [0, sx_, cx_]])
    Ry = np.array([[cy_, 0, sy_], [0, 1, 0], [-sy_, 0, cy_]])
    Rz = np.array([[cz_, -sz_, 0], [sz_, cz_, 0], [0, 0, 1]])
    return Ry @ Rx @ Rz


class Cam:
    """Pinhole camera with thin-lens depth of field.
    World: x right, y down, z away from the viewer; the default camera sits at (0, 0, -focal) so a plane
    at z=0 maps 1 world unit to 1 px (After Effects convention, origin at the canvas centre).
    yaw>0 looks right, pitch>0 looks up, roll>0 rotates the camera clockwise (scene turns CCW).
    fov: vertical field of view in degrees (overrides focal). aperture: pupil diameter in world units
    (0 = no DOF; 20 subtle, 40 soft, 80 dreamy). focus_dist: in front of the camera (default: to origin)."""

    def __init__(self, pos=None, yaw=0.0, pitch=0.0, roll=0.0, fov=None, focal=1500.0, focus_dist=None,
                 aperture=0.0, max_coc=90.0, near=8.0):
        self.focal = (H / 2) / math.tan(math.radians(fov) / 2) if fov else float(focal)
        self.pos = np.array(pos if pos is not None else (0.0, 0.0, -self.focal), np.float64)
        self.yaw, self.pitch, self.roll = float(yaw), float(pitch), float(roll)
        self.aperture = float(aperture)
        self.max_coc = float(max_coc)
        self.near = float(near)
        self.R = _rot(self.pitch, self.yaw, self.roll)           # camera -> world
        self.focus_dist = float(focus_dist) if focus_dist else float(max(self.depth((0, 0, 0)), 1.0))

    @classmethod
    def orbit(cls, target=(0, 0, 0), dist=1500.0, yaw=0.0, pitch=0.0, roll=0.0, **kw):
        """Camera on a sphere around target, looking at it. yaw>0 moves the camera to the right
        (seeing the target's right side), pitch>0 moves it up (looking down)."""
        R = _rot(-pitch, -yaw, 0.0)                # the camera's own (pitch, yaw) = (-pitch, -yaw)
        fwd = R @ np.array([0, 0, 1.0])
        pos = np.asarray(target, np.float64) - fwd * dist
        kw.setdefault('focus_dist', dist)
        return cls(pos=pos, yaw=-yaw, pitch=-pitch, roll=roll, **kw)

    @property
    def forward(self):
        return self.R @ np.array([0, 0, 1.0])

    def to_cam(self, P):
        P = np.atleast_2d(np.asarray(P, np.float64))
        return (P - self.pos) @ self.R          # == R^T (P - pos)

    def depth(self, p):
        return float(self.to_cam(p)[0, 2])

    def project(self, P):
        """World points (N, 3) -> screen px (N, 2), camera depth (N,). Points behind return nan."""
        Pc = self.to_cam(P)
        z = Pc[:, 2]
        with np.errstate(divide='ignore', invalid='ignore'):
            x = np.where(z > 1e-6, self.focal * Pc[:, 0] / z + CX, np.nan)
            y = np.where(z > 1e-6, self.focal * Pc[:, 1] / z + CY, np.nan)
        return np.c_[x, y], z

    def coc(self, depth):
        """Depth-of-field blur radius (px) for a point at camera depth `depth` (scalar or array)."""
        if self.aperture <= 0:
            return 0.0 if np.ndim(depth) == 0 else np.zeros_like(np.asarray(depth, np.float64))
        d = np.maximum(np.asarray(depth, np.float64), 1e-3)
        r = 0.5 * self.aperture * self.focal * np.abs(1.0 / self.focus_dist - 1.0 / d)
        r = np.minimum(r, self.max_coc)
        return float(r) if np.ndim(depth) == 0 else r

    def px_per_unit(self, depth):
        """Screen px per world unit at camera depth."""
        return self.focal / max(depth, 1e-6)

    def K(self):
        return np.array([[self.focal, 0, CX], [0, self.focal, CY], [0, 0, 1.0]])

    def __repr__(self):
        return 'Cam(pos=%s, yaw=%.2f, pitch=%.2f, roll=%.2f, focal=%.0f, focus=%.0f, ap=%.1f)' % (
            np.round(self.pos, 1).tolist(), self.yaw, self.pitch, self.roll, self.focal, self.focus_dist,
            self.aperture)


def plane_corners(center, width, height, rot=(0.0, 0.0, 0.0), anchor=(0.5, 0.5)):
    """World corners (TL, TR, BR, BL) of a width x height plane. rot=(rx, ry, rz) degrees."""
    R = _rot(*rot)
    ax, ay = anchor
    loc = np.array([[-ax * width, -ay * height, 0], [(1 - ax) * width, -ay * height, 0],
                    [(1 - ax) * width, (1 - ay) * height, 0], [-ax * width, (1 - ay) * height, 0]], np.float64)
    return loc @ R.T + np.asarray(center, np.float64)


def plane_point(center, width, height, rot=(0.0, 0.0, 0.0), uv=(0.5, 0.5), anchor=(0.5, 0.5)):
    """World position of normalised (u, v) on a plane (u right, v down, 0..1). uv may be (N, 2)."""
    R = _rot(*rot)
    uv = np.atleast_2d(np.asarray(uv, np.float64))
    loc = np.c_[(uv[:, 0] - anchor[0]) * width, (uv[:, 1] - anchor[1]) * height, np.zeros(len(uv))]
    P = loc @ R.T + np.asarray(center, np.float64)
    return P[0] if P.shape[0] == 1 else P


def _clip_near(Pc, uv, near):
    """Sutherland-Hodgman clip of a camera-space polygon (and its uv) against z >= near."""
    outP, outU = [], []
    n = len(Pc)
    for i in range(n):
        a, b = Pc[i], Pc[(i + 1) % n]
        ua, ub = uv[i], uv[(i + 1) % n]
        ina, inb = a[2] >= near, b[2] >= near
        if ina:
            outP.append(a)
            outU.append(ua)
        if ina != inb:
            t = (near - a[2]) / (b[2] - a[2])
            outP.append(a + (b - a) * t)
            outU.append(ua + (ub - ua) * t)
    return np.array(outP), np.array(outU)


def draw_plane(canvas, spr, cam, center, width, rot=(0.0, 0.0, 0.0), opacity=1.0, mode='over', dof=True,
               height=None, blur=0.0, frost=0.0, anchor=(0.5, 0.5), dof_scale=1.0):
    """Project a sprite as a 3D plane (width world units; height keeps the sprite aspect unless given).
    dof: True = depth of field from cam (per-pixel across tilted planes), False = sharp.
    blur: extra gaussian sigma (screen px). frost: frosted-glass sigma under the plane's alpha.
    Returns {'quad': (4,2) screen corners or None if clipped, 'bbox', 'depth', 'coc'} or None."""
    if opacity <= 1e-4 or spr is None:
        return None
    sh, sw = spr.shape[:2]
    if height is None:
        height = width * sh / sw
    Pw = plane_corners(center, width, height, rot, anchor)
    Pc = cam.to_cam(Pw)
    z = Pc[:, 2]
    if (z < cam.near).all():
        return None
    # plane -> screen homography (sprite continuous coords -> canvas continuous coords)
    e_u = (Pc[1] - Pc[0]) / sw
    e_v = (Pc[3] - Pc[0]) / sh
    Hc = cam.K() @ np.c_[e_u, e_v, Pc[0]]
    clipped = (z < cam.near).any()
    uv = np.array([[0, 0], [sw, 0], [sw, sh], [0, sh]], np.float64)
    if clipped:
        Pcc, uvc = _clip_near(Pc, uv, cam.near)
        if len(Pcc) < 3:
            return None
    else:
        Pcc = Pc
    proj = (cam.K() @ Pcc.T).T
    poly = proj[:, :2] / proj[:, 2:3]
    # quick reject
    if poly[:, 0].max() < -50 or poly[:, 1].max() < -50 or poly[:, 0].min() > canvas.shape[1] + 50 \
            or poly[:, 1].min() > canvas.shape[0] + 50:
        return None
    zc = float(np.mean(Pcc[:, 2]))
    blur_map = None
    levels = None
    coc_c = 0.0
    if dof and cam.aperture > 0:
        cocs = np.asarray(cam.coc(Pcc[:, 2])) * dof_scale
        coc_c = float(cam.coc(max(zc, cam.near))) * dof_scale
        cmin, cmax = float(cocs.min()), float(cocs.max())
        # gaussian sigma ~ half the CoC radius gives a disc-like visual radius
        if cmax - cmin > max(1.5, 0.3 * cmax) and len(Pcc) >= 3:
            # per-pixel: 1/z is affine in screen space; fit through 3 visible vertices
            A3 = np.c_[poly[:3], np.ones(3)]
            iz = 1.0 / Pcc[:3, 2]
            try:
                coef = np.linalg.solve(A3, iz)
            except np.linalg.LinAlgError:
                coef = None
            if coef is not None:
                nlev = 3 if cmax - cmin > 6 else 2
                levels = [float(v) * 0.5 + blur for v in np.linspace(cmin, cmax, nlev)]
                pad_px = 2 + int(math.ceil(3 * max(levels)))
                bx0 = max(0, int(math.floor(poly[:, 0].min())) - pad_px)
                by0 = max(0, int(math.floor(poly[:, 1].min())) - pad_px)
                bx1 = min(canvas.shape[1], int(math.ceil(poly[:, 0].max())) + pad_px)
                by1 = min(canvas.shape[0], int(math.ceil(poly[:, 1].max())) + pad_px)
                if bx1 > bx0 and by1 > by0:
                    xs = np.arange(bx0, bx1, dtype=np.float32) + 0.5
                    ys = np.arange(by0, by1, dtype=np.float32) + 0.5
                    izm = (coef[0] * xs[None, :] + coef[1] * ys[:, None] + coef[2]).astype(np.float32)
                    izm = np.maximum(izm, 1e-6)
                    cm = 0.5 * cam.aperture * cam.focal * np.abs(1.0 / cam.focus_dist - izm) * dof_scale
                    cm = np.clip(np.minimum(cm, cam.max_coc), cmin, cmax)
                    blur_map = (bx0, by0, (cm * 0.5 + blur).astype(np.float32))
                else:
                    levels = None
        sig = coc_c * 0.5 + blur
    else:
        sig = blur
    if blur_map is not None:
        bb = _warp_homography(canvas, spr, Hc, poly, opacity, mode, 0.0, frost, blur_map=blur_map,
                              blur_levels=levels, clip_poly=clipped)
    else:
        bb = _warp_homography(canvas, spr, Hc, poly, opacity, mode, sig, frost, clip_poly=clipped)
    if bb is None:
        return None
    quad = None if clipped else poly
    return {'quad': quad, 'bbox': bb, 'depth': zc, 'coc': coc_c, 'poly': poly}


def draw_billboard(canvas, spr, cam, pos, width, rot=0.0, opacity=1.0, mode='over', dof=True, blur=0.0,
                   height=None, frost=0.0):
    """Camera-facing sprite at world position pos (width in world units, rot = screen roll degrees)."""
    # orientation that faces the camera: use the camera rotation (Euler from its own angles)
    sh, sw = spr.shape[:2]
    if height is None:
        height = width * sh / sw
    Rp = cam.R @ _rot(0, 0, rot)
    loc = np.array([[-width / 2, -height / 2, 0], [width / 2, -height / 2, 0], [width / 2, height / 2, 0],
                    [-width / 2, height / 2, 0]])
    Pw = loc @ Rp.T + np.asarray(pos, np.float64)
    Pc = cam.to_cam(Pw)
    if (Pc[:, 2] < cam.near).any():
        return None
    proj = (cam.K() @ Pc.T).T
    poly = proj[:, :2] / proj[:, 2:3]
    zc = float(Pc[:, 2].mean())
    sig = blur + (cam.coc(zc) * 0.5 if (dof and cam.aperture > 0) else 0.0)
    Hc = cam.K() @ np.c_[(Pc[1] - Pc[0]) / sw, (Pc[3] - Pc[0]) / sh, Pc[0]]
    bb = _warp_homography(canvas, spr, Hc, poly, opacity, mode, sig, frost)
    if bb is None:
        return None
    return {'quad': poly, 'bbox': bb, 'depth': zc, 'coc': sig * 2}


class Scene:
    """Collect 3D drawables and render them back to front.
        sc = Scene(cam)
        sc.plane(card, (0, 0, 300), 700, rot=(0, 15, 0))
        sc.billboard(glow_spr, (200, -300, 900), 400, mode='add')
        sc.custom((0, 0, 50), lambda cv, cam: ...)        # any callable at a world point (or depth)
        sc.particles(dust, t)                               # interleaved between items by depth
        sc.render(canvas)
    """

    def __init__(self, cam):
        self.cam = cam
        self.items = []
        self.parts = []

    def _depth(self, p):
        if np.ndim(p) == 0:
            return float(p)
        return self.cam.depth(p)

    # NOTE: the stored closures capture the camera, never `self`: a Scene -> items -> lambda -> Scene cycle kept
    # every frame's sprites (blended 3D frames, faces, footage) alive until a rare cyclic GC pass (GBs per worker)
    def plane(self, spr, center, width, **kw):
        cam = self.cam
        self.items.append((self._depth(center), lambda cv: draw_plane(cv, spr, cam, center, width, **kw)))
        return self

    def billboard(self, spr, pos, width, **kw):
        cam = self.cam
        self.items.append((self._depth(pos), lambda cv: draw_billboard(cv, spr, cam, pos, width, **kw)))
        return self

    def custom(self, pos_or_depth, fn):
        cam = self.cam
        self.items.append((self._depth(pos_or_depth), lambda cv: fn(cv, cam)))
        return self

    def particles(self, parts, t, opacity=1.0):
        self.parts.append((parts, t, opacity))
        return self

    def render(self, canvas):
        items = sorted(self.items, key=lambda it: -it[0])
        depths = [d for d, _ in items]
        bounds = [float('inf')] + depths + [-float('inf')]
        for i in range(len(bounds) - 1):
            zmax, zmin = bounds[i], bounds[i + 1]
            for p, t, op in self.parts:
                p.draw(canvas, self.cam, t, opacity=op, zmin=zmin, zmax=zmax)
            if i < len(items):
                items[i][1](canvas)
        return canvas


# =============================================================================================== effects
def glow(spr, color=None, sigmas=(4, 12, 32), strength=1.0, weights=None, include=True, pad_px=None,
         source='alpha'):
    """Multi-radius 'deep glow'. Returns a padded sprite (centre preserved) = emissive glow (alpha 0, so
    it adds light under 'over') with the original sprite on top (include=True).
    color: glow colour (default: the sprite's own colours). source: 'alpha' or 'rgb' (glow from luminance)."""
    sigmas = tuple(sigmas)
    if weights is None:
        weights = [1.0 / (1 + 0.35 * i) for i in range(len(sigmas))]
    p = int(math.ceil(max(sigmas) * 2.6)) if pad_px is None else int(pad_px)
    s = pad(spr, p)
    if color is not None:
        base = np.asarray(color, np.float32)[:3]
        src = s[..., 3:4] * base if source == 'alpha' else s[..., :3].mean(2, keepdims=True) * base
    else:
        src = s[..., :3]
    h, w = s.shape[:2]
    acc = np.zeros((h, w, 3), np.float32)
    for sg, wt in zip(sigmas, weights):
        acc += gblur(np.ascontiguousarray(src), sg, border='constant') * np.float32(wt)
    acc *= np.float32(strength)
    out = np.zeros((h, w, 4), np.float32)
    out[..., :3] = acc
    if include:
        _blend(out, s, 1.0, 'over')
    return out


def _bright_pass(small, threshold, knee):
    mx = small[..., :3].max(2)
    k = max(knee, 1e-4)
    soft = np.clip(mx - threshold + k, 0, 2 * k)
    soft = soft * soft / (4 * k)
    contrib = np.maximum(soft, mx - threshold) / np.maximum(mx, 1e-5)
    return small[..., :3] * contrib[..., None]


def _quarter(canvas):
    h, w = canvas.shape[:2]
    return cv2.resize(np.ascontiguousarray(canvas), (w // 4, h // 4), interpolation=cv2.INTER_AREA)


def _add_lowres(canvas, rgb_small):
    """canvas[..., :3] += upscale(rgb_small) using 4-channel OpenCV ops."""
    h, w = canvas.shape[:2]
    sh, sw = rgb_small.shape[:2]
    s4 = np.zeros((sh, sw, canvas.shape[2]), np.float32)
    s4[..., :3] = rgb_small
    up = cv2.resize(s4, (w, h), interpolation=cv2.INTER_LINEAR)
    cv2.add(canvas, up, dst=canvas)
    return canvas


def _bloom_small(small, threshold, strength, radii, tint, knee=0.3):
    bp = _bright_pass(small, threshold, knee)
    acc = np.zeros_like(bp)
    for r in radii:
        acc += gblur(bp, r / 4.0)
    acc *= np.float32(strength / len(radii))
    if tint is not None:
        acc *= np.asarray(tint, np.float32)[:3]
    return acc


def _halation_small(small, strength, threshold, tint, radius):
    hi = np.clip(small[..., :3].max(2) - threshold, 0, None)
    g = gblur(hi, radius / 4.0)
    return g[..., None] * (np.asarray(tint, np.float32)[:3] * strength)


def bloom(canvas, threshold=0.8, strength=0.5, radii=(10, 30, 80), tint=None, knee=0.3):
    """Additive multi-radius bloom of highlights (soft-knee threshold, computed at 1/4 res), in place."""
    if strength <= 0:
        return canvas
    return _add_lowres(canvas, _bloom_small(_quarter(canvas)[..., :3], threshold, strength, radii, tint, knee))


def halation(canvas, strength=0.15, threshold=0.6, tint=(1.0, 0.32, 0.12), radius=10):
    """Film halation: warm red fringe bleeding from bright edges, in place."""
    if strength <= 0:
        return canvas
    return _add_lowres(canvas, _halation_small(_quarter(canvas)[..., :3], strength, threshold, tint, radius))


def anamorphic(canvas, threshold=1.0, strength=0.3, color=None, length=0.6):
    """Horizontal anamorphic streaks from the brightest highlights, in place."""
    if strength <= 0:
        return canvas
    h, w = canvas.shape[:2]
    small = cv2.resize(np.ascontiguousarray(canvas), (w // 8, h // 8), interpolation=cv2.INTER_AREA)[..., :3]
    hi = np.clip(small.max(2) - threshold, 0, None)
    k = max(3, int(w // 8 * length)) | 1
    st = cv2.blur(hi, (k, 1))
    st = cv2.blur(st, (k // 2 | 1, 1))
    st = cv2.GaussianBlur(st, (0, 0), 0.6)
    col = np.asarray(color if color is not None else C['HOT_PINK'], np.float32)[:3]
    return _add_lowres(canvas, st[..., None] * col * np.float32(strength * 4))


@functools.lru_cache(maxsize=8)
def _noise_tile(seed=0, n=256, beta=2.6):
    """Tileable fBm noise (n x n) in [0, 1] via spectral synthesis."""
    rng = np.random.default_rng(seed)
    wn = rng.standard_normal((n, n))
    fy = np.fft.fftfreq(n)[:, None]
    fx = np.fft.fftfreq(n)[None, :]
    f = np.sqrt(fx * fx + fy * fy)
    f[0, 0] = 1.0
    spec = np.fft.fft2(wn) / f ** (beta / 2)
    spec[0, 0] = 0
    out = np.real(np.fft.ifft2(spec))
    out = (out - out.min()) / (out.max() - out.min())
    return out.astype(np.float32)


@functools.lru_cache(maxsize=4)
def _lowres_grid(lw, lh):
    ys, xs = np.mgrid[0:lh, 0:lw].astype(np.float32)
    return (xs + 0.5) * (W / lw), (ys + 0.5) * (H / lh)


def _sample_noise(seed, X, Y, scale, ox, oy, warp=0.0, wt=0.0):
    """Sample the tileable noise at world px coords (X, Y) / scale + offset, optional domain warp."""
    tile = _noise_tile(seed)
    n = tile.shape[0]
    u = X / scale + ox
    v = Y / scale + oy
    if warp > 0:
        t2 = _noise_tile(seed + 1)
        mu = (u * 0.7 + wt) % n
        mv = (v * 0.7 - wt * 0.6) % n
        du = cv2.remap(t2, mu.astype(np.float32), mv.astype(np.float32), cv2.INTER_LINEAR,
                       borderMode=cv2.BORDER_WRAP) - 0.5
        u = u + du * warp
        v = v + du * warp * 0.8
    return cv2.remap(tile, (u % n).astype(np.float32), (v % n).astype(np.float32), cv2.INTER_LINEAR,
                     borderMode=cv2.BORDER_WRAP)


def light_leak(canvas, t, colors=None, strength=0.6, seed=0, speed=1.0, sweep=None, angle=35.0, mode='screen'):
    """Animated organic light leak (screen blend by default), in place.
    sweep: None for a drifting edge leak, or 0..1 progress of a leak band sweeping across the frame along
    `angle` (degrees, counter-clockwise from +x) for transitions."""
    if strength <= 0:
        return canvas
    cols = [np.asarray(c, np.float32)[:3] for c in (colors or (C['ORANGE'], C['AMBER'], C['HOT_PINK']))]
    lw, lh = W // 8, H // 8
    X, Y = _lowres_grid(lw, lh)
    rng = np.random.default_rng(seed)
    acc = np.zeros((lh, lw, 3), np.float32)
    nz = _sample_noise(seed + 3, X, Y, 9.0, t * 6 * speed, t * 2.5 * speed, warp=12.0, wt=t * 3 * speed)
    if sweep is None:
        for i, col in enumerate(cols):
            ph = rng.uniform(0, 2 * math.pi, 4)
            edge = rng.integers(0, 4)
            s = t * 0.35 * speed
            a = 0.5 + 0.45 * math.sin(s + ph[0])
            if edge == 0:
                cx, cy = -0.1 * W, a * H
            elif edge == 1:
                cx, cy = 1.1 * W, a * H
            elif edge == 2:
                cx, cy = a * W, -0.08 * H
            else:
                cx, cy = a * W, 1.08 * H
            rx = W * (0.45 + 0.15 * math.sin(s * 1.3 + ph[1]))
            ry = rx * (1.6 + 0.4 * math.sin(s * 0.7 + ph[2]))
            th = ph[3] + s * 0.4
            dx, dy = X - cx, Y - cy
            c_, s_ = math.cos(th), math.sin(th)
            u = (dx * c_ + dy * s_) / rx
            v = (-dx * s_ + dy * c_) / ry
            g = np.exp(-(u * u + v * v) * 1.4)
            acc += g[..., None] * col * (0.6 + 0.8 * i / max(1, len(cols) - 1) * 0 + 0.4)
        acc *= (0.55 + 0.9 * nz)[..., None]
    else:
        a = math.radians(angle)
        dx, dy = math.cos(a), -math.sin(a)
        proj = (X - CX) * dx + (Y - CY) * dy
        ext = abs(CX * dx) + abs(CY * dy)
        pos = (sweep * 2.6 - 1.3) * ext
        width = ext * 0.42
        d = (proj - pos) / width
        band = np.exp(-d * d * 2.0) * (0.5 + 0.9 * nz)
        core = np.exp(-d * d * 14.0)
        for i, col in enumerate(cols):
            off = (i - (len(cols) - 1) / 2) * 0.35
            g = np.exp(-(d - off) ** 2 * 2.5)
            acc += g[..., None] * col * 0.7
        acc *= band[..., None] * 1.4
        acc += core[..., None] * np.float32([1.0, 0.9, 0.8]) * 0.45
        env = math.sin(math.pi * clamp(sweep))
        acc *= env
    up = cv2.resize(acc * np.float32(strength), (canvas.shape[1], canvas.shape[0]), interpolation=cv2.INTER_CUBIC)
    np.maximum(up, 0, out=up)
    if mode == 'add':
        canvas[..., :3] += up
    else:
        d = canvas[..., :3]
        d += up * (1.0 - np.clip(d, 0, 1))
    return canvas


def _radial_smear(q, cx, cy, length, n, decay=True):
    h, w = q.shape[:2]
    acc = np.zeros_like(q)
    tot = 0.0
    for i in range(n):
        s = 1 + length * i / n
        wgt = (1 - i / n) if decay else 1.0
        M = np.float32([[s, 0, (1 - s) * cx], [0, s, (1 - s) * cy]])
        acc += cv2.warpAffine(q, M, (w, h), flags=cv2.INTER_LINEAR) * np.float32(wgt)
        tot += wgt
    return acc / np.float32(tot)


def god_rays(canvas, center, strength=0.4, threshold=0.5, length=0.4, n=10, tint=None):
    """Volumetric light shafts: bright areas smeared radially away from `center` (two-pass radial blur at
    1/4 res, so ~n*n effective samples without banding), in place."""
    if strength <= 0:
        return canvas
    h, w = canvas.shape[:2]
    q = _quarter(canvas)[..., :3]
    q = _bright_pass(q, threshold, 0.2)
    cx, cy = center[0] / 4, center[1] / 4
    # scaled-up copies about the light centre: bright areas stream away from the light
    acc = _radial_smear(q, cx, cy, length, n, True)
    acc = _radial_smear(acc, cx, cy, length / n, n, False)
    acc = cv2.GaussianBlur(acc, (0, 0), 0.8)
    if tint is not None:
        acc *= np.asarray(tint, np.float32)[:3]
    return _add_lowres(canvas, acc * np.float32(strength * 3))


# ---- particles
@functools.lru_cache(maxsize=256)
def _bokeh_sprite(rq):
    """Bokeh disc of radius rq/4 px (quantised), with a faint bright rim; float32 (n, n) intensity."""
    r = rq / 4.0
    n = int(math.ceil(r + 2.5))
    yy, xx = np.mgrid[-n:n + 1, -n:n + 1].astype(np.float32)
    d = np.sqrt(xx * xx + yy * yy)
    soft = max(0.8, r * 0.07)
    a = np.clip((r - d) / soft + 0.5, 0, 1)
    rim = np.clip((d - r * 0.62) / (r * 0.38), 0, 1) ** 2
    a = a * (0.80 + 0.25 * rim)             # peak-normalised: interior 0.8, faint bright rim
    return a.astype(np.float32)


class Particles:
    """Dust / bokeh drifting through 3D. Deterministic for a seed; draw() is cheap (~5 ms / 200 particles).
    box: ((x0, y0, z0), (x1, y1, z1)) world volume; with follow=True it is relative to the camera
    position and wraps around it (infinite dust field that parallaxes as the camera moves).
    size: world radius range; colors: list of linear RGB (default ivory/peach/hot pink);
    twinkle: 0..1 brightness flicker; bright: overall intensity."""

    def __init__(self, n=160, seed=0, box=((-1600, -2600, 300), (1600, 2600, 6500)), vel=(0, -18, 0),
                 size=(1.2, 3.6), colors=None, twinkle=0.6, follow=True, bright=1.0, wander=30.0,
                 min_energy=0.12):
        rng = np.random.default_rng(seed)
        self.n = n
        self.lo = np.array(box[0], np.float64)
        self.hi = np.array(box[1], np.float64)
        self.P0 = rng.uniform(self.lo, self.hi, (n, 3))
        self.V = np.asarray(vel, np.float64) * rng.uniform(0.6, 1.4, (n, 1))
        self.size = rng.uniform(size[0], size[1], n) ** 1.0
        cols = colors or [C['IVORY'], C['PEACH'], C['HOT_PINK'] * 0.8 + 0.2]
        cols = [np.asarray(c, np.float32)[:3] for c in cols]
        self.col = np.array([cols[i] for i in rng.integers(0, len(cols), n)], np.float32)
        self.bright = bright * rng.uniform(0.35, 1.0, n) ** 1.5
        self.tw_f = rng.uniform(0.4, 2.2, n)
        self.tw_p = rng.uniform(0, 2 * math.pi, n)
        self.tw_a = twinkle * rng.uniform(0.3, 1.0, n)
        self.wph = rng.uniform(0, 2 * math.pi, (n, 3))
        self.wander = wander
        self.follow = follow
        self.min_energy = min_energy

    def positions(self, t, cam=None):
        P = self.P0 + self.V * t + self.wander * np.sin(t * 0.35 + self.wph) * np.array([1, 1, 0.5])
        span = self.hi - self.lo
        if self.follow and cam is not None:
            rel = P - cam.pos
            rel = self.lo + np.mod(rel - self.lo, span)
            return rel + cam.pos
        return self.lo + np.mod(P - self.lo, span)

    def draw(self, canvas, cam, t, opacity=1.0, zmin=None, zmax=None, mode='add'):
        if opacity <= 0:
            return canvas
        P = self.positions(t, cam)
        scr, z = cam.project(P)
        ok = z > cam.near * 4
        if zmin is not None:
            ok &= z >= zmin
        if zmax is not None:
            ok &= z < zmax
        idx = np.flatnonzero(ok)
        if len(idx) == 0:
            return canvas
        f = cam.focal
        r_px = self.size[idx] * f / z[idx]
        coc = np.asarray(cam.coc(z[idx])) if cam.aperture > 0 else np.zeros(len(idx))
        R = np.sqrt(r_px ** 2 + coc ** 2)
        tw = 1.0 + self.tw_a[idx] * np.sin(t * 2 * math.pi * self.tw_f[idx] + self.tw_p[idx])
        # fade in from the far end of the box and out very near the lens
        span_z = self.hi[2] - self.lo[2]
        zrel = z[idx] - (cam.pos[2] if self.follow else 0)
        far_fade = np.clip((self.hi[2] - zrel) / (0.25 * span_z), 0, 1)
        near_fade = np.clip((z[idx] - cam.near * 4) / 120.0, 0, 1)
        # display-friendly bokeh model: in-focus specks keep their energy, defocused discs keep a visible
        # peak brightness (falls ~linearly with blur, floored by min_energy)
        peak = self.bright[idx] * np.maximum(r_px / np.maximum(R, 1e-6), self.min_energy)
        inten = peak * np.maximum(tw, 0) * far_fade * near_fade * opacity
        hh, ww = canvas.shape[:2]
        for j, i in enumerate(idx):
            x, y = scr[i]
            Rj = float(R[j])
            if not (-Rj - 4 < x < ww + Rj + 4 and -Rj - 4 < y < hh + Rj + 4):
                continue
            a = float(inten[j])
            if a < 0.003:
                continue
            col = self.col[i] * a
            if Rj < 1.8:
                # sub-pixel gaussian splat; total energy ~ physical disc area
                sig = max(0.6, Rj * 0.65)
                n = int(math.ceil(sig * 3))
                ix, iy = int(math.floor(x)), int(math.floor(y))
                x0, y0 = ix - n, iy - n
                xs = np.arange(x0, ix + n + 2, dtype=np.float32) + 0.5 - x
                ys = np.arange(y0, iy + n + 2, dtype=np.float32) + 0.5 - y
                g = np.exp(-(ys[:, None] ** 2 + xs[None, :] ** 2) / (2 * sig * sig))
                g *= math.pi * max(float(r_px[j]), 0.7) ** 2 / max(float(g.sum()), 1e-6)
                kern = g
            else:
                kern = _bokeh_sprite(int(round(Rj * 4)))
                n = kern.shape[0] // 2
                x0, y0 = int(round(x)) - n, int(round(y)) - n
            kh, kw = kern.shape
            X0, Y0 = max(0, x0), max(0, y0)
            X1, Y1 = min(ww, x0 + kw), min(hh, y0 + kh)
            if X1 <= X0 or Y1 <= Y0:
                continue
            k = kern[Y0 - y0:Y1 - y0, X0 - x0:X1 - x0]
            canvas[Y0:Y1, X0:X1, :3] += k[..., None] * col
        return canvas


# ---- finishing pieces
@functools.lru_cache(maxsize=3)
def _vignette_map(w, h, amount, roundness, softness, ch=4):
    """(h, w, ch) multiplicative vignette map (alpha channel = 1)."""
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    nx = (xx + 0.5 - w / 2) / (w / 2)
    ny = (yy + 0.5 - h / 2) / (h / 2)
    asp = (h / w) ** roundness          # roundness 1 = circular on screen, 0 = follows the frame aspect
    r = np.sqrt(nx ** 2 + (ny / asp) ** 2) / math.sqrt(1 + 1 / asp ** 2) * math.sqrt(2)
    v = 1.0 - amount * np.clip(r - 0.35, 0, None) ** softness / (math.sqrt(2) - 0.35) ** softness
    v = np.clip(v, 0, 1).astype(np.float32)
    m = np.repeat(v[..., None], ch, 2)
    if ch == 4:
        m[..., 3] = 1.0
    m.setflags(write=False)
    return m


def vignette(canvas, amount=0.35, roundness=0.75, softness=1.6):
    """Darken towards the corners (multiplicative), in place."""
    if amount <= 0:
        return canvas
    h, w, c = canvas.shape
    cv2.multiply(canvas, _vignette_map(w, h, round(float(amount), 3), roundness, softness, c), dst=canvas)
    return canvas


@functools.lru_cache(maxsize=2)
def _chroma_unit(w, h, power):
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    dx = xx + 0.5 - w / 2
    dy = yy + 0.5 - h / 2
    rmax = math.hypot(w / 2, h / 2)
    r = np.sqrt(dx * dx + dy * dy) / rmax
    k = r ** (power - 1) / rmax          # displacement = amount * r^power along the radial unit vector
    return xx, yy, (dx * k).astype(np.float32), (dy * k).astype(np.float32)


@functools.lru_cache(maxsize=4)
def _chroma_maps(w, h, power, amount, sign):
    xx, yy, ux, uy = _chroma_unit(w, h, power)
    a = np.float32(amount * sign)
    return cv2.convertMaps(xx + ux * a, yy + uy * a, cv2.CV_16SC2)


def chroma(canvas, amount=1.5, power=2.0):
    """Radial lateral chromatic aberration: red pushed out, blue pulled in by up to `amount` px at the
    corners, falling off as r^power so the centre stays clean. In place."""
    if amount < 0.15:
        return canvas
    h, w = canvas.shape[:2]
    a = round(float(amount) * 10) / 10.0
    for ch, sign in ((0, -1.0), (2, 1.0)):
        m1, m2 = _chroma_maps(w, h, float(power), a, sign)
        src = np.ascontiguousarray(canvas[..., ch])
        canvas[..., ch] = cv2.remap(src, m1, m2, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT101)
    return canvas


@functools.lru_cache(maxsize=2)
def _grain_tiles(w, h, size, n=4, seed=5):
    rng = np.random.default_rng(seed)
    gw, gh = int(w / size) + 102, int(h / size) + 102
    tiles = []
    for _ in range(n):
        g = rng.standard_normal((gh, gw)).astype(np.float32)
        g = cv2.GaussianBlur(g, (0, 0), 0.45)
        g /= g.std() + 1e-6
        tiles.append(g)
    return tiles


@functools.lru_cache(maxsize=2)
def _zeros(h, w):
    z = np.zeros((h, w), np.float32)
    z.setflags(write=False)
    return z


def _grain_noise(canvas, t, size):
    h, w = canvas.shape[:2]
    tiles = _grain_tiles(w, h, float(size))
    fi = int(round(t * FPS * 3.0))
    g = tiles[fi % len(tiles)]
    ox, oy = (fi * 7919) % 97, (fi * 104729) % 89
    g = g[oy:oy + int(h / size) + 2, ox:ox + int(w / size) + 2]
    if (fi // len(tiles)) % 2:
        g = g[::-1]
    return cv2.resize(g, (w, h), interpolation=cv2.INTER_LINEAR)


def grain(canvas, t, amount=0.018, size=1.3):
    """Monochrome film grain, in place. amount ~ std in display (sRGB) units at mid-grey. The grain is
    mostly multiplicative in linear light (so saturated colours do not get chroma noise in their dark
    channels) plus a small additive floor for the blacks."""
    if amount <= 0:
        return canvas
    g = _grain_noise(canvas, t, size)
    h, w, c = canvas.shape
    g4 = cv2.merge([g, g, g] + ([_zeros(h, w)] if c == 4 else []))
    tmp = cv2.multiply(canvas, g4, scale=5.2 * amount)
    cv2.add(canvas, tmp, dst=canvas)
    cv2.scaleAdd(g4, 0.04 * amount, canvas, dst=canvas)
    return canvas


def flash(canvas, amount, color=None):
    """Exposure flash: multiplies exposure by (1 + 3 * amount) and adds 0.3 * amount of `color` (default
    ivory), so highlights blow out before the blacks lift. amount 1 = strong flash frame, 3 = white-out."""
    if amount <= 0:
        return canvas
    col = np.asarray(color if color is not None else C['IVORY'], np.float32)[:3]
    k = np.float32(1 + amount * 3.0)
    canvas *= np.float32([k, k, k, 1.0])[:canvas.shape[2]]
    canvas += np.append(col * np.float32(amount * 0.3), np.float32(0))[:canvas.shape[2]]
    return canvas


def fade(canvas, amount, color=None):
    """Fade towards a colour (default black), in place."""
    if amount <= 0:
        return canvas
    col = np.asarray(color if color is not None else (0, 0, 0), np.float32)[:3]
    k = np.float32(1 - amount)
    canvas *= np.float32([k, k, k, 1.0])[:canvas.shape[2]]
    canvas += np.append(col * np.float32(amount), np.float32(0))[:canvas.shape[2]]
    return canvas


def whip_blur(canvas, amount, angle=0.0):
    """Directional (whip-pan) smear of `amount` px along `angle` degrees (0 = horizontal), in place."""
    if amount < 1.0:
        return canvas
    h, w = canvas.shape[:2]
    f = 1 if amount < 40 else 2 if amount < 140 else 4
    img = canvas if f == 1 else cv2.resize(canvas, (w // f, h // f), interpolation=cv2.INTER_AREA)
    k = max(1, int(round(amount / f))) | 1
    a = angle % 180
    if a < 2 or a > 178:
        out = cv2.blur(img, (k, 1), borderType=cv2.BORDER_REFLECT101)
    elif abs(a - 90) < 2:
        out = cv2.blur(img, (1, k), borderType=cv2.BORDER_REFLECT101)
    else:
        ih, iw = img.shape[:2]
        diag = int(math.ceil(math.hypot(iw, ih))) + 2
        M = cv2.getRotationMatrix2D((iw / 2, ih / 2), a, 1.0)
        M[0, 2] += (diag - iw) / 2
        M[1, 2] += (diag - ih) / 2
        rot = cv2.warpAffine(img, M, (diag, diag), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT101)
        rot = cv2.blur(rot, (k, 1), borderType=cv2.BORDER_REFLECT101)
        Mi = cv2.invertAffineTransform(M)
        out = cv2.warpAffine(rot, Mi, (iw, ih), flags=cv2.INTER_LINEAR)
    if f > 1:
        out = cv2.resize(out, (w, h), interpolation=cv2.INTER_LINEAR)
    canvas[...] = out
    return canvas


def zoom_blur(canvas, amount, center=None, samples=10):
    """Radial zoom-through blur; amount = scale spread (0.08 = 8 %). The centre stays sharp. In place."""
    if amount < 0.003:
        return canvas
    h, w = canvas.shape[:2]
    cx, cy = center if center is not None else (w / 2, h / 2)
    f = 2
    sm = cv2.resize(canvas, (w // f, h // f), interpolation=cv2.INTER_AREA)
    acc = np.zeros_like(sm)
    for i in range(samples):
        s = 1 + amount * i / (samples - 1)
        M = np.float32([[1 / s, 0, (1 - 1 / s) * cx / f], [0, 1 / s, (1 - 1 / s) * cy / f]])
        acc += cv2.warpAffine(sm, M, (w // f, h // f), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT101)
    acc /= samples
    up = cv2.resize(acc, (w, h), interpolation=cv2.INTER_LINEAR)
    yy, xx = _lowres_grid(w // 8, h // 8)
    r = np.sqrt((xx - cx) ** 2 + (yy - cy) ** 2) * amount
    wgt = cv2.resize(np.clip(r / 3.0, 0, 1).astype(np.float32), (w, h), interpolation=cv2.INTER_LINEAR)
    canvas += (up - canvas) * wgt[..., None]
    return canvas


@functools.lru_cache(maxsize=8)
def dot_grid(w=W, h=H, spacing=34, radius=1.6, offset=(0.0, 0.0)):
    """Anti-aliased dot grid alpha (h, w) float32 (read-only, cached). Tileable with period `spacing`."""
    ys, xs = np.mgrid[0:h, 0:w].astype(np.float32)
    dx = (xs + 0.5 - offset[0]) % spacing - spacing / 2
    dy = (ys + 0.5 - offset[1]) % spacing - spacing / 2
    d = np.sqrt(dx * dx + dy * dy)
    a = np.clip(radius - d + 0.5, 0, 1).astype(np.float32)
    a.setflags(write=False)
    return a


def grid_floor(canvas, cam, y=600.0, spacing=200.0, extent=6000.0, color=None, opacity=0.35, width=1.2,
               z0=-1000.0, fade_dist=6000.0, mode='add'):
    """Perspective grid on the horizontal plane at world height y (lines every `spacing`), fading with
    distance. Drawn as anti-aliased lines (no texture aliasing), in place."""
    col = np.asarray(color if color is not None else C['HOT_PINK'], np.float32)[:3]
    h, w = canvas.shape[:2]
    layer = np.zeros((h, w), np.float32)
    zs_far = cam.pos[2] + extent
    n = int(extent / spacing)
    x_c = round(cam.pos[0] / spacing) * spacing
    z_c = math.floor(cam.pos[2] / spacing) * spacing

    def seg(p0, p1):
        Pc = cam.to_cam(np.array([p0, p1]))
        for _ in range(1):
            if Pc[0, 2] < cam.near and Pc[1, 2] < cam.near:
                return
            if Pc[0, 2] < cam.near:
                tt = (cam.near - Pc[0, 2]) / (Pc[1, 2] - Pc[0, 2])
                Pc[0] = Pc[0] + (Pc[1] - Pc[0]) * tt
            if Pc[1, 2] < cam.near:
                tt = (cam.near - Pc[1, 2]) / (Pc[0, 2] - Pc[1, 2])
                Pc[1] = Pc[1] + (Pc[0] - Pc[1]) * tt
        # subdivide so the distance fade can vary along the line
        k = 24
        ts = np.linspace(0, 1, k + 1)[:, None]
        Q = Pc[0] + (Pc[1] - Pc[0]) * ts
        sx = cam.focal * Q[:, 0] / Q[:, 2] + CX
        sy = cam.focal * Q[:, 1] / Q[:, 2] + CY
        fadev = np.clip(1 - Q[:, 2] / fade_dist, 0, 1) ** 1.5
        for i in range(k):
            v = float((fadev[i] + fadev[i + 1]) / 2)
            if v < 0.01:
                continue
            a = (int(sx[i] * 16), int(sy[i] * 16))
            b = (int(sx[i + 1] * 16), int(sy[i + 1] * 16))
            if max(abs(a[0]), abs(a[1]), abs(b[0]), abs(b[1])) > 2 ** 26:
                continue
            cv2.line(layer, a, b, v, max(1, int(round(width))), cv2.LINE_AA, shift=4)

    for i in range(-n, n + 1):
        x = x_c + i * spacing
        seg((x, y, max(z0, cam.pos[2])), (x, y, zs_far))
    for j in range(0, n + 1):
        z = z_c + j * spacing
        if z < cam.pos[2]:
            continue
        seg((x_c - extent, y, z), (x_c + extent, y, z))
    layer = cv2.GaussianBlur(layer, (0, 0), 0.6)
    if mode == 'add':
        canvas[..., :3] += layer[..., None] * col * opacity
    else:
        a = layer * opacity
        canvas[..., :3] = canvas[..., :3] * (1 - a[..., None]) + a[..., None] * col
    return canvas


# =============================================================================================== backgrounds
# blob: (cx, cy, rx, ry, angle, colour, intensity, drift_x, drift_y, period[, aurora])  (normalised to W / H)
_BG_LOOKS = {
    'neon': dict(
        top='NIGHT_0', bottom='NIGHT_1', lift=0.45,
        blobs=[
            (0.78, 0.22, 0.56, 0.30, -28, 'MAGENTA', 0.80, 0.06, 0.04, 23.0, 1.0),
            (0.70, 0.26, 0.17, 0.10, -28, 'HOT_PINK', 0.34, 0.05, 0.035, 17.0, 0.5),
            (0.06, 0.66, 0.50, 0.42, 32, 'PLUM', 0.55, 0.05, 0.05, 29.0, 0.4),
            (0.10, 0.60, 0.26, 0.20, 32, 'MAGENTA', 0.30, 0.05, 0.05, 19.0, 0.8),
            (0.96, 0.80, 0.34, 0.24, 15, 'ORANGE', 0.10, 0.03, 0.03, 31.0, 0.0),
        ],
        rim=('ORANGE', 'AMBER', 1.0), rim_geom=(0.42, 1.52, 0.66), dots=0.016, dots_lit=0.9, noise=0.55),
    'amber': dict(
        top='NIGHT_0', bottom='NIGHT_1', lift=0.4, base_tint=(1.35, 0.8, 0.4),
        blobs=[
            (0.24, 0.24, 0.56, 0.32, 24, 'ORANGE', 0.42, 0.06, 0.04, 25.0, 1.0),
            (0.30, 0.27, 0.18, 0.11, 24, 'AMBER', 0.30, 0.05, 0.035, 18.0, 0.5),
            (0.95, 0.70, 0.46, 0.40, -30, 'LOGO_ORANGE', 0.17, 0.05, 0.05, 27.0, 0.5),
            (1.00, 0.14, 0.26, 0.20, -12, 'MAGENTA', 0.22, 0.04, 0.03, 21.0, 0.3),
            (0.05, 0.90, 0.40, 0.30, 15, 'PLUM', 0.30, 0.05, 0.04, 33.0, 0.0),
        ],
        rim=('AMBER', 'ORANGE', 0.9), rim_geom=(0.62, 1.55, 0.68), dots=0.014, dots_lit=0.8, noise=0.5),
    'airy': dict(
        top='IVORY', bottom='IVORY', lift=0.0,
        blobs=[  # light looks: intensity = how far the paper is tinted towards the colour
            (0.86, 0.12, 0.72, 0.50, -30, 'PEACH', 1.0, 0.05, 0.04, 26.0),
            (0.80, 0.16, 0.38, 0.26, -30, 'AMBER', 0.24, 0.04, 0.03, 19.0),
            (0.08, 0.38, 0.62, 0.50, 25, 'LAVENDER', 1.0, 0.05, 0.05, 22.0),
            (0.12, 0.40, 0.42, 0.30, 25, 'HOT_PINK', 0.30, 0.05, 0.05, 30.0),
            (0.88, 0.84, 0.66, 0.46, -20, 'PEACH', 1.0, 0.05, 0.04, 24.0),
            (0.92, 0.88, 0.36, 0.25, -20, 'ORANGE', 0.26, 0.04, 0.04, 21.0),
            (0.35, 0.99, 0.80, 0.34, 10, 'LAVENDER', 0.8, 0.04, 0.03, 34.0),
            (0.14, 0.86, 0.34, 0.24, 0, 'HOT_PINK', 0.14, 0.04, 0.04, 27.0),
        ],
        rim=None, dots=0.0, dots_lit=0.0, noise=0.12, paper=0.016),
}


@functools.lru_cache(maxsize=4)
def _bg_base(look, w, h):
    """(h, w, 3) base gradient with a gentle off-centre lift (never a flat fill)."""
    cfg = _BG_LOOKS[look]
    g = gradient(w, h, [(0.0, C[cfg['top']]), (1.0, C[cfg['bottom']])], angle=-90)
    if 'base_tint' in cfg:
        g = g * np.asarray(cfg['base_tint'], np.float32)
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    r = np.sqrt(((xx - w * 0.55) / w) ** 2 + ((yy - h * 0.40) / h) ** 2)
    if look == 'airy':
        g = g * (1.0 - 0.03 * np.clip(r * 1.6, 0, 1))[..., None]
    else:
        g = g * (1.0 + cfg.get('lift', 0.4) * np.exp(-r * r * 6))[..., None]
    return g.astype(np.float32)


@functools.lru_cache(maxsize=2)
def _paper(w, h, seed=3):
    """Soft paper texture (zero-mean, unit std): fine tooth, short fibres and large mottling."""
    rng = np.random.default_rng(seed)
    fine = cv2.GaussianBlur(rng.standard_normal((h, w)).astype(np.float32), (0, 0), 0.8)
    fib = rng.standard_normal((h // 2, w // 2)).astype(np.float32)
    fib = cv2.GaussianBlur(fib, (0, 0), sigmaX=3.0, sigmaY=1.2)
    fib = cv2.resize(fib, (w, h), interpolation=cv2.INTER_LINEAR)
    blot = cv2.resize(_noise_tile(seed + 9, 256, 3.0), (w, h), interpolation=cv2.INTER_CUBIC) - 0.5
    p = fine / (fine.std() + 1e-6) * 0.45 + fib / (fib.std() + 1e-6) * 0.25 + blot / (blot.std() + 1e-6) * 0.6
    return (p / (p.std() + 1e-6)).astype(np.float32)


@functools.lru_cache(maxsize=3)
def _bg_maps(look, w, h):
    """Cached full-res maps so that canvas = A + upscaled_field * B (+ dots handled inside A / B).
    Returns (A, B, Dc, Dl): A, B (h, w, 4); Dc / Dl dot-only terms for when the dots must move."""
    cfg = _BG_LOOKS[look]
    base = _bg_base(look, w, h)
    A = np.zeros((h, w, 4), np.float32)
    B = np.ones((h, w, 4), np.float32)
    A[..., :3] = base
    A[..., 3] = 1.0
    B[..., 3] = 0.0
    Dc = Dl = None
    if cfg.get('paper'):
        pm = 1.0 + _paper(w, h) * np.float32(cfg['paper'])
        A[..., :3] *= pm[..., None]
        B[..., :3] = pm[..., None]
    if cfg['dots'] > 0:
        da = dot_grid(w, h, 34, 1.5)
        Dc = np.zeros((h, w, 4), np.float32)
        Dc[..., :3] = da[..., None] * (np.float32(cfg['dots']) * C['IVORY'])
        Dl = np.zeros((h, w, 4), np.float32)
        Dl[..., :3] = da[..., None] * np.float32(cfg['dots_lit'])
        A += Dc
        B += Dl
    for m in (A, B, Dc, Dl):
        if m is not None:
            m.setflags(write=False)
    return A, B, Dc, Dl


@functools.lru_cache(maxsize=2)
def _bg_maps_nodots(look, w, h):
    A, B, Dc, Dl = _bg_maps(look, w, h)
    if Dc is None:
        return A, B
    Am, Bm = cv2.subtract(A, Dc), cv2.subtract(B, Dl)
    Am.setflags(write=False)
    Bm.setflags(write=False)
    return Am, Bm


def _bg_transform(cam, parallax):
    """Similarity (scale, rot, tx, ty) mapping background coords -> screen for a distant backdrop."""
    if cam is None or parallax == 0:
        return 1.0, 0.0, 0.0, 0.0
    D = 9000.0
    p, _ = cam.project(np.array([[0, 0, D], [400, 0, D]]))
    if not np.isfinite(p).all():
        return 1.0, 0.0, 0.0, 0.0
    q, _ = Cam().project(np.array([[0, 0, D], [400, 0, D]]))
    v = p[1] - p[0]
    v0 = q[1] - q[0]
    s = math.hypot(*v) / math.hypot(*v0)
    rot = math.atan2(v[1], v[0]) - math.atan2(v0[1], v0[0])
    tx, ty = float(p[0, 0] - q[0, 0]) * parallax, float(p[0, 1] - q[0, 1]) * parallax
    s = 1.0 + (s - 1.0) * parallax
    return s, rot * parallax, tx, ty


def _rim_line(cv, ccx, ccy, R, width, ang_mid, ang_w, col_core, col_hot, k):
    """Full-res thin rim line along the upper arc of a circle, evaluated only in a narrow strip around
    the arc in every column (anti-aliased, white-hot core)."""
    hh, ww = cv.shape[:2]
    xs = np.arange(ww, dtype=np.float32) + 0.5
    dxv = xs - np.float32(ccx)
    ok = np.abs(dxv) < R * 0.999
    yc = np.full(ww, -1e6, np.float32)
    yc[ok] = ccy - np.sqrt(R * R - dxv[ok] ** 2)
    angc = np.arctan2(yc - ccy, dxv)
    dang = (angc - ang_mid + math.pi) % (2 * math.pi) - math.pi
    arcw = np.exp(-(dang / ang_w) ** 2).astype(np.float32)
    m = int(width * 7 + 8)
    cols = np.flatnonzero(ok & (arcw > 0.004) & (yc > -m) & (yc < hh + m))
    if len(cols) == 0:
        return
    offs = np.arange(-m, m + 1, dtype=np.int32)
    Yi = np.floor(yc[cols]).astype(np.int32)[None, :] + offs[:, None]
    Xi = np.broadcast_to(cols[None, :], Yi.shape)
    valid = (Yi >= 0) & (Yi < hh)
    Yv, Xv = Yi[valid], Xi[valid]
    dx = Xv.astype(np.float32) + 0.5 - np.float32(ccx)
    dy = Yv.astype(np.float32) + 0.5 - np.float32(ccy)
    e = (np.sqrt(dx * dx + dy * dy) - np.float32(R)) / np.float32(width)
    aw = np.broadcast_to(arcw[cols][None, :], Yi.shape)[valid]
    core = np.exp(-e * e) * aw
    glowv = np.exp(-np.abs(e) * 0.25) * aw * 0.35
    hot = np.clip(core * aw - 0.55, 0, None) * 1.4
    add_ = (core * k)[:, None] * np.asarray(col_core, np.float32) + (glowv * k * 0.6)[:, None] * \
        np.asarray(col_core, np.float32) + (hot * k)[:, None] * np.asarray(col_hot, np.float32)
    cv[Yv, Xv, :3] += add_


def background(look='neon', t=0.0, cam=None, center=None, boost=0.0, dots=1.0, rim=1.0, seed=0, parallax=1.0,
               intensity=1.0):
    """Animated premium backdrop -> opaque canvas (H, W, 4). look: 'neon' | 'amber' | 'airy'.
    cam: optional Cam; the backdrop then pans/rotates/zooms like a distant plate (parallax scales it).
    center: (x, y) normalised override for the main glow centre; boost: extra glow (beat pulses, 0..1);
    dots: dot-grid multiplier; rim: rim-light multiplier (0 hides it); intensity: all glows."""
    cfg = _BG_LOOKS[look]
    light = look == 'airy'
    lw, lh = W // 8, H // 8
    X, Y = _lowres_grid(lw, lh)
    s, rot, tx, ty = _bg_transform(cam, parallax)
    c_, s_ = math.cos(-rot), math.sin(-rot)
    Xs, Ys = X - CX - tx, Y - CY - ty
    Xb = (Xs * c_ - Ys * s_) / s + CX
    Yb = (Xs * s_ + Ys * c_) / s + CY
    field = np.zeros((lh, lw, 4), np.float32)
    f3 = field[..., :3]
    nz = _sample_noise(seed + 21, Xb, Yb, 5.5, t * 1.6, t * 0.9, warp=18.0, wt=t * 0.8)
    nz2 = _sample_noise(seed + 33, Xb, Yb, 2.6, -t * 2.4, t * 1.3)
    vol = (1 - cfg['noise']) + cfg['noise'] * (nz * 1.25 + nz2 * 0.35)
    for i, bl in enumerate(cfg['blobs']):
        bx, by, rx, ry, ang, col, inten, ax_, ay_, per = bl[:10]
        aur = bl[10] if len(bl) > 10 else 0.0
        ph = i * 1.7 + seed
        w_ = 2 * math.pi * t / per
        cx = (bx + ax_ * math.sin(w_ + ph)) * W
        cy = (by + ay_ * math.sin(w_ * 0.8 + ph * 1.3)) * H
        if center is not None and i in (0, 1):
            cx, cy = center[0] * W + (cx - bx * W), center[1] * H + (cy - by * H)
        th = math.radians(ang + 6 * math.sin(w_ * 0.6 + ph))
        dx, dy = Xb - cx, Yb - cy
        cth, sth = math.cos(th), math.sin(th)
        u = (dx * cth + dy * sth) / (rx * W)
        v = (-dx * sth + dy * cth) / (ry * W)
        d2 = u * u + v * v
        g = np.exp(-d2 * 1.5) * 0.7 + np.exp(-d2 * 6.0) * 0.5
        if aur > 0:
            # aurora curtains: ridged noise stretched along the blob's long axis, drifting slowly
            ua = (dx * cth + dy * sth) / 260.0 + t * 0.05 + i * 3.1
            va = (-dx * sth + dy * cth) / 70.0 + 0.6 * np.sin(ua * 1.3 + t * 0.21) + t * 0.11
            n = _noise_tile(seed + 50 + i)
            nn = cv2.remap(n, ((ua * 6.0) % 256).astype(np.float32), ((va * 6.0) % 256).astype(np.float32),
                           cv2.INTER_LINEAR, borderMode=cv2.BORDER_WRAP)
            ridge = (1.0 - np.abs(nn * 2.0 - 1.0)) ** 4
            g = g * ((1 - 0.7 * aur) + aur * 2.1 * ridge)
        k = inten * intensity * (1 + boost * (1.0 if i < 2 else 0.35))
        if light:
            f3 += (g * k * (0.75 + 0.25 * vol))[..., None] * (C[col] - C['IVORY'])
        else:
            f3 += (g * k * (0.5 + 0.5 * vol))[..., None] * C[col]
    rim_args = None
    if cfg.get('rim') and rim > 0:
        c0, c1, ri = cfg['rim']
        rcx, rcy, rr = cfg['rim_geom']
        drift = 0.025 * math.sin(2 * math.pi * t / 21.0)
        ccx, ccy, R = (rcx + drift) * W, rcy * H, rr * H
        d = np.sqrt((Xb - ccx) ** 2 + (Yb - ccy) ** 2) - R
        ang = np.arctan2(Yb - ccy, Xb - ccx)
        mid = -math.pi / 2 + 0.22 + 0.12 * math.sin(2 * math.pi * t / 17.0)
        aw = 0.34
        arcw = np.exp(-(((ang - mid + math.pi) % (2 * math.pi) - math.pi) / aw) ** 2)
        k = ri * rim * intensity
        # the glow stops just inside the planet; the cut is a ramp ~3 low-res px wide (a hard step on the 1/8
        # grid upsampled to 8 px stair-steps that crawled under camera moves); the full-res rim line below
        # gives the crisp edge
        inside = np.clip((d + 0.004 * H) / (0.0125 * H) + 0.5, 0, 1)
        atmo = np.exp(-np.maximum(d, 0) / (0.035 * H)) * (inside * inside * (3 - 2 * inside)) * 0.55
        halo = (atmo * arcw * (0.7 + 0.5 * nz2))[..., None] * C[c0] * k
        f3 += halo
        body = np.clip(-d / (0.06 * H), 0, 1)[..., None]
        f3 *= 1 - body * 0.75
        # rim line in screen space (circle maps to circle under the similarity)
        sc_cx = (ccx - CX) * s
        sc_cy = (ccy - CY) * s
        rc, rs = math.cos(rot), math.sin(rot)
        rim_args = (CX + tx + sc_cx * rc - sc_cy * rs, CY + ty + sc_cx * rs + sc_cy * rc, R * s,
                    0.0035 * H * s, mid + rot, aw, C[c0] * 1.4, C[c1] * 2.0, k)
    up = cv2.resize(field, (W, H), interpolation=cv2.INTER_CUBIC)
    A, B, Dc, Dl = _bg_maps(look, W, H)
    moved = cam is not None and (abs(tx) > 0.02 or abs(ty) > 0.02 or abs(s - 1) > 1e-4 or abs(rot) > 1e-5)
    if Dc is not None and dots > 0 and (moved or dots != 1.0):
        # dots move with the backdrop: rebuild their terms
        M = cv2.getRotationMatrix2D((CX, CY), -math.degrees(rot), s)
        M[0, 2] += tx
        M[1, 2] += ty
        Am, Bm = _bg_maps_nodots(look, W, H)
        Dlw = cv2.warpAffine(Dl, M, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_WRAP)
        cfgd = cfg['dots'] * dots / max(cfg['dots_lit'], 1e-6)
        Dcw = Dlw * np.append(C['IVORY'] * np.float32(cfgd), np.float32(0.0))
        if dots != 1.0:
            Dlw *= np.float32(dots)
        cv2.add(Dlw, Bm, dst=Dlw)
        cv = cv2.multiply(up, Dlw)
        cv2.add(cv, Am, dst=cv)
        cv2.add(cv, Dcw, dst=cv)
    elif Dc is not None and dots <= 0:
        Am, Bm = _bg_maps_nodots(look, W, H)
        cv = cv2.multiply(up, Bm)
        cv2.add(cv, Am, dst=cv)
    else:
        cv = cv2.multiply(up, B)
        cv2.add(cv, A, dst=cv)
    if rim_args is not None:
        _rim_line(cv, *rim_args)
    if not light:
        np.maximum(cv, 0, out=cv)
    return cv


# =============================================================================================== post
LOOKS = {
    'neon': dict(exposure=0.0, bloom=0.6, bloom_threshold=0.42, bloom_radii=(8, 26, 70, 170),
                 bloom_tint=(1.0, 0.62, 0.86), halation=0.10, anamorphic=0.0, vignette=0.42, chroma=1.8,
                 grain=0.018, black_tint=(0.0016, 0.0003, 0.0018)),
    'amber': dict(exposure=0.0, bloom=0.6, bloom_threshold=0.42, bloom_radii=(8, 26, 70, 170),
                  bloom_tint=(1.0, 0.72, 0.42), halation=0.14, anamorphic=0.0, vignette=0.45, chroma=1.6,
                  grain=0.018, black_tint=(0.0020, 0.0008, 0.0002)),
    'airy': dict(exposure=0.0, bloom=0.30, bloom_threshold=1.0, bloom_knee=0.15, bloom_radii=(10, 30, 90),
                 bloom_tint=(1.0, 0.85, 0.80), halation=0.04, anamorphic=0.0, vignette=0.14, chroma=0.9,
                 grain=0.011, black_tint=None),
    'natural': dict(exposure=0.0, bloom=0.3, bloom_threshold=0.8, bloom_radii=(10, 30, 80),
                    bloom_tint=(1.0, 0.9, 0.85), halation=0.06, anamorphic=0.0, vignette=0.3, chroma=1.0,
                    grain=0.016, black_tint=None),
}


def post(canvas, look='neon', t=0.0, **ov):
    """Per-look finishing stack, in place: exposure, bloom + halation (one shared 1/4-res pass), optional
    anamorphic streaks / light leak / flash / fade, vignette, black tint, edge chroma, grain. Returns the
    canvas (alpha set to 1). Override any LOOKS[look] key: post(cv, 'neon', t, chroma=6, flash=0.4, leak=0.5).
    Extra keys: flash_color, fade_color, leak_seed, leak_colors, anamorphic_color, bloom_knee.
    footage=0..1: frame dominated by bright footage (full-bleed montage, payoff shots): raises the bloom threshold
    to 0.85 and eases bloom / halation so whites stay clean instead of a milky haze (blend it over transitions)."""
    cfg = dict(LOOKS[look])
    cfg.update(ov)
    fk = float(cfg.pop('footage', 0.0) or 0.0)
    if fk > 0:
        # bright full-bleed footage: the void-tuned bloom (threshold ~0.42) blooms white walls into a milky haze
        fk = min(fk, 1.0)
        cfg['bloom_threshold'] = lerp(cfg.get('bloom_threshold', 0.8), max(cfg.get('bloom_threshold', 0.8), 0.85), fk)
        cfg['bloom'] = lerp(cfg.get('bloom', 0.0), min(cfg.get('bloom', 0.0), 0.35), fk)
        cfg['halation'] = cfg.get('halation', 0.0) * (1 - 0.6 * fk)
    h, w = canvas.shape[:2]
    if cfg.get('exposure'):
        k = float(2 ** cfg['exposure'])
        canvas *= np.float32([k, k, k, 1.0])[:canvas.shape[2]]
    acc = None
    if cfg.get('bloom', 0) > 0 or cfg.get('halation', 0) > 0:
        small = _quarter(canvas)[..., :3]
        if cfg.get('bloom', 0) > 0:
            acc = _bloom_small(small, cfg['bloom_threshold'], cfg['bloom'], cfg['bloom_radii'],
                               cfg.get('bloom_tint'), cfg.get('bloom_knee', 0.3))
        if cfg.get('halation', 0) > 0:
            hal = _halation_small(small, cfg['halation'], 0.55, (1.0, 0.32, 0.12), 10)
            acc = hal if acc is None else acc + hal
    if acc is not None:
        _add_lowres(canvas, acc)
    if cfg.get('anamorphic', 0) > 0:
        anamorphic(canvas, 0.9, cfg['anamorphic'], cfg.get('anamorphic_color'))
    if cfg.get('leak', 0) > 0:
        light_leak(canvas, t, cfg.get('leak_colors'), cfg['leak'], cfg.get('leak_seed', 0))
    if cfg.get('flash', 0) > 0:
        flash(canvas, cfg['flash'], cfg.get('flash_color'))
    if cfg.get('fade', 0) > 0:
        fade(canvas, cfg['fade'], cfg.get('fade_color'))
    if cfg.get('vignette', 0) > 0:
        vignette(canvas, cfg['vignette'])
    if cfg.get('black_tint') is not None:
        bt = cfg['black_tint']
        canvas += np.float32([bt[0], bt[1], bt[2], 0.0])[:canvas.shape[2]]
    if cfg.get('chroma', 0) > 0:
        chroma(canvas, cfg['chroma'])
    if cfg.get('grain', 0) > 0:
        grain(canvas, t, cfg['grain'])
    canvas[..., 3] = 1.0
    return canvas


# =============================================================================================== render loop
def render_frame(draw_fn, t, samples=3, shutter=0.5, fps=FPS):
    """True motion blur: average draw_fn(t_i) over `samples` sub-frame times spread across the shutter
    (shutter = fraction of a frame, 0.5 = 180 degrees), centred on t. samples=1 -> draw_fn(t)."""
    samples = max(1, int(samples))
    if samples == 1:
        return draw_fn(t)
    span = shutter / fps
    acc = None
    for i in range(samples):
        ti = t - span / 2 + (i + 0.5) / samples * span
        f = draw_fn(ti)
        if acc is None:
            acc = f.astype(np.float32, copy=True)
        else:
            acc += f
    acc *= np.float32(1.0 / samples)
    return acc


class FFWriter:
    """Pipe RGB24 frames to ffmpeg/libx264 (High, yuv420p, bt709 matrix + tags).
        with FFWriter(path, fps=30, crf=14, preset='slow') as fw:
            fw.write(frame_u8)                   # (H, W, 3) uint8 RGB
    pix_fmt='yuv444p' gives a high-444 intermediate; audio='x.wav' muxes AAC 320k 48 kHz;
    out_size=(w, h) rescales on encode (lanczos)."""

    def __init__(self, path, fps=FPS, crf=14, preset='slow', size=(W, H), pix_fmt='yuv420p', audio=None,
                 out_size=None, faststart=True, tune=None, extra=()):
        self.path = path
        self.size = tuple(size)
        os.makedirs(os.path.dirname(os.path.abspath(path)) or '.', exist_ok=True)
        vf = 'scale=%sout_color_matrix=bt709:out_range=tv:flags=lanczos+accurate_rnd+full_chroma_int' % (
            '%d:%d:' % tuple(out_size) if out_size else '')
        cmd = ['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24',
               '-s', '%dx%d' % self.size, '-r', str(fps), '-i', '-']
        if audio:
            cmd += ['-i', audio]
        cmd += ['-vf', vf + ',format=%s' % pix_fmt, '-c:v', 'libx264',
                '-profile:v', 'high444' if pix_fmt == 'yuv444p' else 'high',
                '-preset', preset, '-crf', str(crf), '-pix_fmt', pix_fmt,
                '-colorspace', 'bt709', '-color_primaries', 'bt709', '-color_trc', 'bt709', '-color_range', 'tv']
        if tune:
            cmd += ['-tune', tune]
        if audio:
            cmd += ['-map', '0:v', '-map', '1:a', '-c:a', 'aac', '-b:a', '320k', '-ar', '48000', '-shortest']
        if faststart and path.endswith('.mp4'):
            cmd += ['-movflags', '+faststart']
        cmd += list(extra) + [path]
        self.cmd = cmd
        self.p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
        self.n = 0

    def write(self, frame):
        f = np.ascontiguousarray(frame)
        if f.dtype != np.uint8:
            f = to_srgb8(f, self.n / FPS)
        if f.shape[1] != self.size[0] or f.shape[0] != self.size[1]:
            raise ValueError('frame %s does not match writer size %s' % (f.shape, self.size))
        self.p.stdin.write(f[..., :3].tobytes())
        self.n += 1

    def close(self):
        if self.p is not None:
            self.p.stdin.close()
            rc = self.p.wait()
            self.p = None
            if rc != 0:
                raise RuntimeError('ffmpeg failed (%d): %s' % (rc, ' '.join(self.cmd)))

    def __enter__(self):
        return self

    def __exit__(self, *a):
        self.close()


def save_png(path, canvas_or_u8, t=0.0):
    """Write a canvas (linear float) or uint8 RGB frame to PNG/JPG."""
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    img = canvas_or_u8 if canvas_or_u8.dtype == np.uint8 else to_srgb8(canvas_or_u8, t)
    cv2.imwrite(path, cv2.cvtColor(np.ascontiguousarray(img[..., :3]), cv2.COLOR_RGB2BGR),
                [cv2.IMWRITE_JPEG_QUALITY, 93] if path.lower().endswith('.jpg') else [])
    return path


def sprite_preview(spr, bg=(0.02, 0.02, 0.03)):
    """Composite a sprite over a solid colour for previews -> canvas-sized (h, w, 4)."""
    out = new_canvas(bg, spr.shape[1], spr.shape[0])
    return over(out, spr)


# =============================================================================================== self-test
def _label(u8, text, x=24, y=54, scale=1.3):
    cv2.putText(u8, text, (x, y), cv2.FONT_HERSHEY_DUPLEX, scale, (0, 0, 0), 5, cv2.LINE_AA)
    cv2.putText(u8, text, (x, y), cv2.FONT_HERSHEY_DUPLEX, scale, (255, 255, 255), 2, cv2.LINE_AA)
    return u8


def _hstack_u8(imgs, h=960):
    out = []
    for im in imgs:
        s = h / im.shape[0]
        out.append(cv2.resize(im, (int(im.shape[1] * s), h), interpolation=cv2.INTER_AREA))
    return np.concatenate(out, 1)


def _write_u8(path, u8):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    params = [cv2.IMWRITE_JPEG_QUALITY, 92] if path.lower().endswith('.jpg') else [cv2.IMWRITE_PNG_COMPRESSION, 3]
    cv2.imwrite(path, cv2.cvtColor(u8, cv2.COLOR_RGB2BGR), params)
    print('wrote', path)


def _demo_card(w=600, h=400):
    """Test sprite: rounded card with gradient, text and a grid."""
    from PIL import Image, ImageDraw, ImageFont
    a = rrect_alpha(w, h, 36)
    g = gradient(w, h, [C['MAGENTA'], C['ORANGE']], 35)
    spr = np.dstack([g * a[..., None], a]).astype(np.float32)
    im = Image.new('L', (w, h), 0)
    d = ImageDraw.Draw(im)
    try:
        f = ImageFont.truetype(font_path('Nunito-Black'), 92)
        f2 = ImageFont.truetype(font_path('Poppins-SemiBold'), 34)
    except OSError:
        f = f2 = ImageFont.load_default()
    d.text((w / 2, h * 0.42), 'Organic', font=f, fill=255, anchor='mm')
    d.text((w / 2, h * 0.70), 'Nurture  Develop  Grow', font=f2, fill=255, anchor='mm')
    for x in range(40, w - 30, 40):
        d.line([(x, h - 40), (x, h - 22)], fill=180, width=2)
    m = np.asarray(im, np.float32)[..., None] / 255 * a[..., None]
    spr[..., :3] = spr[..., :3] * (1 - m) + C['IVORY'] * m
    return spr


def selftest():
    import time
    os.makedirs(SELFTEST, exist_ok=True)
    out = []
    # 1. backgrounds
    imgs = []
    for look in ('neon', 'amber', 'airy'):
        background(look, 2.9)
        t0 = time.time()
        cv = background(look, 3.0)
        tb = time.time() - t0
        post(cv, look, 3.0)
        u8 = to_srgb8(cv, 3.0)
        imgs.append(_label(u8, '%s  bg %.0f ms' % (look, tb * 1000)))
    p = os.path.join(SELFTEST, 'core_backgrounds.png')
    _write_u8(p, _hstack_u8(imgs))
    out.append(p)
    # 2. 3D planes with DOF + particles + scene
    card = _demo_card()
    cam = Cam(pos=(0, 0, -1500), yaw=4, pitch=-2, aperture=46, focus_dist=1500)
    cv = background('neon', 1.0, cam)
    dust = Particles(220, seed=2)
    sc = Scene(cam)
    for i, (x, y, z, ry) in enumerate([(-330, -560, 2600, 28), (260, -120, 1200, -24), (-200, 330, 0, 18),
                                        (250, 760, -700, -30)]):
        sc.plane(card, (x, y, z), 600, rot=(6, ry, -4 + 3 * i))
    sc.particles(dust, 1.0)
    sc.render(cv)
    # tilted floor-like plane with a varying DOF
    big = _demo_card(900, 600)
    draw_plane(cv, big, cam, (0, 1150, 900), 1400, rot=(-62, 0, 0))
    grid_floor(cv, cam, y=1300, spacing=160, opacity=0.25)
    post(cv, 'neon', 1.0)
    p = os.path.join(SELFTEST, 'core_planes_dof.png')
    _write_u8(p, _label(to_srgb8(cv, 1.0), 'planes: DOF far/focus/near + tilted plane'))
    out.append(p)
    # 3. glow / bloom / light leak / god rays
    imgs = []
    cv = background('neon', 2.0)
    g = glow(card, C['HOT_PINK'], (6, 18, 48, 110), 1.1)
    draw(cv, g, CX, 500, 1.0)
    rr = ring(150, 6, C['ORANGE'] * 3.0, glow=10)
    draw(cv, glow(rr, None, (4, 14, 40), 1.4), CX, 1200, 1.0)
    draw(cv, disc(30, C['IVORY'] * 6), CX, 1200, 1.0)
    post(cv, 'neon', 2.0)
    imgs.append(_label(to_srgb8(cv, 2.0), 'glow + bloom'))
    cv = background('amber', 2.0)
    draw(cv, card, CX, 900, 1.2)
    light_leak(cv, 2.0, strength=0.8, seed=3)
    post(cv, 'amber', 2.0)
    imgs.append(_label(to_srgb8(cv, 2.0), 'light leak (drift)'))
    cv = background('neon', 2.0)
    draw(cv, card, CX, 900, 1.2)
    light_leak(cv, 2.0, strength=1.0, seed=1, sweep=0.5)
    post(cv, 'neon', 2.0)
    imgs.append(_label(to_srgb8(cv, 2.0), 'light leak (sweep)'))
    cv = background('neon', 2.0)
    draw(cv, disc(60, C['IVORY'] * 4), CX, 520, 1.0)
    draw(cv, card, CX, 1000, 1.1)
    god_rays(cv, (CX, 520), 0.8, 0.5, 0.6)
    post(cv, 'neon', 2.0)
    imgs.append(_label(to_srgb8(cv, 2.0), 'god rays'))
    p = os.path.join(SELFTEST, 'core_glow_leak.png')
    _write_u8(p, _hstack_u8(imgs))
    out.append(p)
    # 4. particles
    imgs = []
    for look, ap in (('neon', 60), ('airy', 40)):
        cam = Cam(aperture=ap, focus_dist=2200)
        cv = background(look, 0.0, cam)
        pt = Particles(260, seed=5, colors=None if look == 'neon' else [C['WHITE'], C['PEACH'], C['AMBER']],
                       bright=1.0 if look == 'neon' else 0.7)
        pt.draw(cv, cam, 4.0)
        post(cv, look, 4.0)
        imgs.append(_label(to_srgb8(cv, 4.0), 'particles %s' % look))
    p = os.path.join(SELFTEST, 'core_particles.png')
    _write_u8(p, _hstack_u8(imgs))
    out.append(p)
    # 5. motion blur test: fast moving + spinning card, 1 vs 7 samples; whip / zoom blur
    def mdraw(tt):
        cvv = background('neon', tt)
        # 2D card: 2400 px/s horizontal + 540 deg/s spin
        draw(cvv, card, -300 + 2400 * tt, 560, 0.75, rot=tt * 540)
        # 3D card flying at the camera on a curve
        cam2 = Cam(aperture=0)
        z = 2600 - 5200 * tt
        draw_plane(cvv, card, cam2, (-120 + 300 * tt, 520, z), 600, rot=(10, 35 - tt * 80, -8))
        return cvv
    imgs = []
    for n in (1, 3, 7):
        cv = render_frame(mdraw, 0.45, samples=n, shutter=0.5)
        post(cv, 'neon', 0.45)
        imgs.append(_label(to_srgb8(cv, 0.45), 'motion blur %d sample%s' % (n, 's' if n > 1 else '')))
    cv = background('neon', 1.0)
    draw(cv, card, CX, 900, 1.3)
    whip_blur(cv, 160, 20)
    post(cv, 'neon', 1.0, chroma=8)
    imgs.append(_label(to_srgb8(cv, 1.0), 'whip blur 160px'))
    cv = background('neon', 1.0)
    draw(cv, card, CX, 900, 1.3)
    zoom_blur(cv, 0.12)
    post(cv, 'neon', 1.0)
    imgs.append(_label(to_srgb8(cv, 1.0), 'zoom blur'))
    p = os.path.join(SELFTEST, 'core_motionblur.png')
    _write_u8(p, _hstack_u8(imgs))
    out.append(p)
    # 6. sprite draw accuracy / mips: a card scaled down a lot, rotated, all modes
    cv = new_canvas(C['NIGHT_1'])
    for i, s in enumerate([1.0, 0.7, 0.45, 0.3, 0.17, 0.09]):
        draw(cv, card, 160 + i * 170, 300, s, rot=0)
    for i, m in enumerate(('over', 'add', 'screen', 'multiply')):
        draw(cv, card, 170 + i * 250, 700, 0.4, rot=-10, mode=m)
    # gradient + sRGB banding check
    bg = brand_gradient(1000, 300)
    draw(cv, bg, CX, 1100)
    rad = radial(900, C['MAGENTA'], 1.5)
    draw(cv, rad, CX, 1600, 1.0, mode='add')
    p = os.path.join(SELFTEST, 'core_draw_modes.png')
    _write_u8(p, _label(to_srgb8(cv), 'mips / blend modes / gradient'))
    out.append(p)
    # 7. rack focus along a tilted plane (per-pixel DOF) + frosted glass
    from PIL import Image, ImageDraw, ImageFont
    rows = Image.new('RGBA', (900, 1300), (0, 0, 0, 0))
    d = ImageDraw.Draw(rows)
    try:
        fnt = ImageFont.truetype(font_path('Poppins-SemiBold'), 54)
    except OSError:
        fnt = ImageFont.load_default()
    d.rounded_rectangle((0, 0, 899, 1299), 48, fill=(255, 255, 255, 34), outline=(255, 120, 200, 255), width=4)
    for i in range(9):
        y = 60 + i * 136
        d.rounded_rectangle((50, y, 850, y + 104), 26, fill=(255, 255, 255, 30))
        d.ellipse((76, y + 22, 136, y + 82), fill=(100, 166, 11, 255))
        d.text((170, y + 52), 'Row %d  A spare bedroom' % (i + 1), font=fnt, fill=(252, 248, 245, 255), anchor='lm')
    rows_spr = sprite(rows)
    imgs = []
    for label, fd in (('focus near', 1150.0), ('focus mid', 1500.0), ('focus far', 2100.0)):
        cam = Cam(aperture=70, focus_dist=fd)
        cv = background('neon', 1.0, cam)
        draw_plane(cv, rows_spr, cam, (0, 0, 0), 900, rot=(0, -58, 0), frost=18)
        post(cv, 'neon', 1.0)
        imgs.append(_label(to_srgb8(cv, 1.0), 'rack %s (%d)' % (label, fd)))
    cv = background('neon', 1.0)
    glass = np.zeros((700, 820, 4), np.float32)
    ga = rrect_alpha(780, 660, 60, 20)
    glass[..., :3] = (ga * 0.06)[..., None]
    glass[..., 3] = ga * 0.25
    glass += pad(sprite(rows.crop((40, 40, 860, 740)).resize((780, 660))), 20) * 0.0
    edge = np.clip(1.6 - np.abs(rrect_sdf(780, 660, 60, 20) + 1), 0, 1)
    glass[..., :3] += edge[..., None] * C['HOT_PINK'] * 1.4
    glass[..., 3] = np.maximum(glass[..., 3], edge)
    draw(cv, glass, CX, 520, frost=22)
    draw(cv, glow(glass, C['MAGENTA'], (10, 30), 0.5, include=False), CX, 520, mode='add')
    cam = Cam(aperture=0)
    draw_plane(cv, glass, cam, (0, 420, 300), 820, rot=(28, -22, 4), frost=22)
    post(cv, 'neon', 1.0)
    imgs.append(_label(to_srgb8(cv, 1.0), 'frosted glass (2D + 3D)'))
    p = os.path.join(SELFTEST, 'core_rackfocus_glass.png')
    _write_u8(p, _hstack_u8(imgs))
    out.append(p)
    # 8. timing of a typical frame
    cam = Cam(aperture=40)
    dust = Particles(160, seed=1)
    spr6 = [glow(_demo_card(300, 160), C['HOT_PINK'], (6, 18), 0.6) for _ in range(6)]
    foot = np.ascontiguousarray(np.dstack([gradient(700, 1000, [C['PEACH'], C['PLUM']], 60),
                                           np.ones((1000, 700), np.float32)]))

    def typical(tt):
        cvv = background('neon', tt, cam)
        draw_plane(cvv, foot, cam, (0, 0, 300), 800, rot=(4, 14, -3))
        for i, s in enumerate(spr6):
            draw(cvv, s, 200 + 130 * i, 400 + 160 * i, 0.9 + 0.02 * i, rot=i * 3)
        dust.draw(cvv, cam, tt)
        return cvv
    typical(0.0)
    t0 = time.time()
    for k in range(3):
        cv = typical(0.1 * k)
        post(cv, 'neon', 0.1 * k)
        to_srgb8(cv)
    dt = (time.time() - t0) / 3
    print('typical frame (no footage decode), 1 sample: %.3f s' % dt)
    return out


if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == 'selftest':
        selftest()
    else:
        print(__doc__)
