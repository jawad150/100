"""assets3d_bijli_chali_gayi.py - Blender props for reel 2 · C11 "Bijli Chali Gayi" (@jawad_mp4).

Builds the 8 asset folders of BRIEF §6.12 (brand_reels/design/reels/bijli_chali_gayi/BRIEF.md) with bpy 5.2 /
Cycles CPU (threads 2, adaptive sampling 0.02 + OpenImageDenoise with albedo/normal guides, fixed seed, view
transform Standard, look None, gamma 1) as RGBA 8-bit straight-alpha sRGB PNGs in the shared 3D asset spec, mode
'static', one folder 'passes' per asset, frames in the order of meta 'labels'.

    RWS = workspace/jawad_reels/bijli_chali_gayi          (RWS/props is a symlink to RWS/assets3d)
    RWS/assets3d/<name>/passes/0000.png ... + meta.json   (meta.json is written LAST)
    load: S3.Asset3D(name, 'passes', root=RWS + '/assets3d').by_label('key_l')

Assets (labels in frame order)
------------------------------
    desk_plate   CAM_ROOM 1080x1920 opaque   lit, practicals                       tube_xy, crt_slot, box_slot
    crt_room     CAM_ROOM, cropped           room, key_l, key_r, screen_mask, emit frame_xy, screen_tl/tr/br/bl,
                                                                                    power_led (+ meta screen_quad)
    tower_room   CAM_ROOM, cropped           room, key_l, key_r, emit              frame_xy, hdd_led
    box_room     CAM_ROOM, cropped           room, key_l, key_r, emit              frame_xy, led_xy
    pankhi       85 mm, yaw 20, 900x1100     key_l, key_r                          pivot (handle end)
    candle       100 mm, 8 deg up, 600x1400  self, key_l, key_r                    wick_tip, base, flame_light
    keycap_ctrl  100 mm, 35 deg up, yaw 15   key_l, key_r, emit                    legend_centre, contact
    keycap_s     (same camera)  900x900      key_l, key_r, emit                    legend_centre, contact

    CAM_ROOM: 28 mm, 36 mm sensor fitted vertically, camera level at 0.913 m (15 cm above the table top) looking
    at the back wall, lens shift puts the horizon on row 1212. The room is solved from the brief's screen targets
    (ceiling/wall line y 230, floor/wall line y 1700, table front edge y 1380, CRT / box / tower / copy / tube /
    window / switchboard rectangles): `python3 assets3d_bijli_chali_gayi.py targets` projects every component
    and prints its bbox against the target (tolerance +-20 px).
    Room props: the prop is rendered inside the full room. 'room' = the plate's lit rig (emissive tube light,
    faint CRT spill, faint window spill, dim front room-bounce fill) with the receiving surface (table top; floor
    for the tower) as a shadow catcher and every other room surface a holdout (the prop's contact shadow comes
    with it; the plate has no prop shadows). The shadow alpha is cleaned after rendering (split against the
    prop's coverage, kept only where the catcher is visible, blurred 1.6 px, sub-2 % noise floor removed).
    'key_l' / 'key_r' = the torch only (one spot 35 deg above, cone 25 deg, soft r 0.05 m, IVORY x0.85 + AMBER
    x0.15, from screen-left / screen-right) plus a soft warm back rim; for the CRT also a soft torch-side card
    seen only in the convex glass, so the reflection slides across it as key_l cross-fades to key_r. Room
    surfaces are holdouts there (they still bounce light). 'emit' / 'screen_mask' = emission only (every other surface a
    holdout), 16 spp without denoise (1 spp aliases the edges). Each prop folder is cropped to the union alpha
    bbox of its passes + 24 px; meta 'frame_xy' (also a feature) = the crop's top-left in the 1080x1920 frame,
    features are in sprite px (add frame_xy for frame px).

CLI
---
    python3 assets3d_bijli_chali_gayi.py <name> [<name> ...] [--preview] [--samples N]
    python3 assets3d_bijli_chali_gayi.py all [--preview]
    python3 assets3d_bijli_chali_gayi.py targets        # CAM_ROOM layout vs the brief's screen targets (no render)
    python3 assets3d_bijli_chali_gayi.py sheet          # finals: contact sheets over black and over FLAME, plus
                                                        # the lit and torch room composites with target boxes
    python3 assets3d_bijli_chali_gayi.py previewsheet   # the same for the --preview renders
    python3 assets3d_bijli_chali_gayi.py selftest       # palette, layout and render-border alignment checks

    --preview   16 spp, half resolution, written to RWS/out/preview3d/<name>/passes/ (finals untouched)
    env BCG_THREADS (default 2), BCG_OUT (default RWS/assets3d). Run every render through tools/heavy.sh.
    Samples: room-scale lit passes 96, macro passes 128 (adaptive threshold 0.02, OIDN), emission passes 16.

Palette (project.json tokens, sRGB hex -> linear for Blender): NIGHT_0 #070404, NIGHT_1 #170A07, FLAME #FF6A1A,
RED #F2312B, EMBER #B3120E, GOLD #FF9F1C, AMBER #FFB547, SMOKE #2A1A15, PLUM #4A0E08, IVORY #FFF3E6, ASH #A8978C;
the dusk shadow #171431 is used only as the night-sky card and the faint window spill. No text, logo or mark on
any prop (the only glyphs are the keycap legends "Ctrl" and "S", Poppins SemiBold). Nothing from the toolkit's
earlier-client prop sets is used; the hero/icon builders are imported for engine helpers only (reset, mesher,
camera framing, projection, meta writer).
"""
import os
import sys
import json
import math
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import assets3d_hero as H  # noqa: E402  (engine helpers only: reset, mesh_field, frame_camera, project_px, write_meta)

bpy = None
Vector = None

REEL = 'bijli_chali_gayi'
RWS = os.path.join(H.WS, REEL)
OUT = os.environ.get('BCG_OUT', os.path.join(RWS, 'assets3d'))
PREVIEW = os.path.join(RWS, 'out', 'preview3d')
SHEETS = os.path.join(RWS, 'out', 'sheets3d')
TEX = os.path.join(RWS, 'out', 'tex3d')
THREADS = int(os.environ.get('BCG_THREADS', '2'))
FONT_SEMI = os.path.join(H.FONTS, 'Poppins-SemiBold.ttf')
S_ROOM, S_MACRO, S_FLAT, S_PREVIEW = 96, 128, 16, 16
CROP_PAD = 24

# ============================================================================= palette

TOK = dict(NIGHT_0='#070404', NIGHT_1='#170A07', FLAME='#FF6A1A', RED='#F2312B', EMBER='#B3120E', GOLD='#FF9F1C',
           AMBER='#FFB547', SMOKE='#2A1A15', PLUM='#4A0E08', IVORY='#FFF3E6', ASH='#A8978C', DUSK='#171431',
           HOUSING='#3B2A22', GLASS='#0C0807', BOXMETAL='#120C0A', PBT='#0E0908')


def lin(c):
    """Token / '#RRGGBB' / tuple -> linear RGB tuple."""
    if isinstance(c, str):
        h = TOK.get(c, c).lstrip('#')
        return tuple(H._s2l(int(h[i:i + 2], 16) / 255.0) for i in (0, 2, 4))
    return tuple(float(x) for x in c[:3])


def mixl(a, b, t):
    a, b = lin(a), lin(b)
    return tuple(x * (1 - t) + y * t for x, y in zip(a, b))


def mul(c, k):
    return tuple(x * k for x in lin(c))


def hue(c):
    """Colour normalised to max 1 (for light colours: energy carries the intensity)."""
    c = lin(c)
    m = max(c)
    return tuple(x / m for x in c)


TORCH = mixl('IVORY', 'AMBER', 0.15)             # IVORY x0.85 + AMBER x0.15 (brief §6.12)
RIM = hue(mixl('AMBER', 'FLAME', 0.5))           # warm back rim (brand red-orange rim)

# ============================================================================= CAM_ROOM (solved from the brief's screen targets)

W_PX, H_PX = 1080, 1920
F_PX = 28.0 / 36.0 * H_PX            # 1493.33 px: 28 mm lens, 36 mm sensor fitted vertically
CAM_Z = 0.9131                       # camera height: 15 cm above the table top, level
HOR_Y = 1212.0                       # horizon row (vertical lens shift)


def X_at(x, Y):
    return (x - W_PX / 2) * Y / F_PX


def Z_at(y, Y):
    return CAM_Z + (HOR_Y - y) * Y / F_PX


WALL_Y = F_PX * CAM_Z / (1700.0 - HOR_Y)               # back wall plane: floor/wall line on row 1700  (2.794 m)
CEIL_Z = Z_at(230.0, WALL_Y)                           # ceiling height: ceiling/wall line on row 230   (2.750 m)
TABLE_Z = 0.76
TABLE_Y0 = F_PX * (CAM_Z - TABLE_Z) / (1380.0 - HOR_Y)  # table front edge on row 1380                  (1.361 m)
TABLE_Y1 = TABLE_Y0 + 0.80
TABLE_X = (-0.70, 0.74)
APRON_Y = TABLE_Y0 + 0.012
APRON_Z0 = Z_at(1500.0, APRON_Y)                       # apron bottom on row 1500

CRT_Y = 1.425                                          # bezel front plane
CRT_YG = CRT_Y + 0.016                                 # back edge of the lip = visible glass outline
CRT_X0, CRT_X1 = X_at(250, CRT_Y + 0.010), X_at(690, CRT_Y + 0.010)
CRT_ZT = Z_at(1010, CRT_Y + 0.010)
CRT_ZB = 0.800                                         # bezel bottom (the swivel stand below it)
CRT_GX0, CRT_GX1 = X_at(300, CRT_YG), X_at(640, CRT_YG)
CRT_GZ1, CRT_GZ0 = Z_at(1050, CRT_YG), Z_at(1290, CRT_YG)

BOX_Y = 1.400
BOX_X0, BOX_X1 = X_at(760, BOX_Y + 0.004), X_at(960, BOX_Y + 0.004)
BOX_Z0 = TABLE_Z + 0.006                               # rubber feet
BOX_ZT = 0.896
BOX_D = 0.25
BOX_YAW = -6.0                                         # deg, about the vertical through the LED
LED_X, LED_Z = X_at(800, BOX_Y - 0.004), Z_at(1265, BOX_Y - 0.004)

TW_W, TW_H, TW_D = 0.200, 0.430, 0.400
TW_Z0 = 0.014                                          # feet
TW_Y = F_PX * (CAM_Z - TW_Z0) / (1900.0 - HOR_Y)       # front-bottom edge on row 1900
TW_X1 = X_at(955, TW_Y)
TW_X0 = TW_X1 - TW_W

TUBE_Y = WALL_Y - 0.045                                 # tube axis (in front of the batten)
TUBE_X0, TUBE_X1 = X_at(96, TUBE_Y), X_at(374, TUBE_Y)
TUBE_Z = Z_at(268, TUBE_Y)
WIN_X0, WIN_X1 = X_at(720, WALL_Y), X_at(1010, WALL_Y)
WIN_Z0, WIN_Z1 = Z_at(900, WALL_Y), Z_at(300, WALL_Y)
SB_Y = WALL_Y - 0.012
SB_X0, SB_X1 = X_at(122, SB_Y), X_at(248, SB_Y)
SB_Z0, SB_Z1 = Z_at(898, SB_Y), Z_at(762, SB_Y)
FAN_Y = 2.22

TARGETS = {   # brief §6.12 screen targets (x0, y0, x1, y1), tolerance +-20 px
    'ceiling_line': (0, 230, 1080, 230), 'tube': (90, 250, 380, 275), 'window': (720, 300, 1010, 900),
    'switchboard': (120, 760, 250, 900), 'crt_body': (250, 1010, 690, 1380), 'crt_glass': (300, 1050, 640, 1290),
    'box': (760, 1230, 960, 1380), 'led': (800, 1265, 800, 1265), 'tower': (740, 1520, 960, 1900),
    'copy': (70, 1310, 240, 1380), 'table_edge': (0, 1380, 1080, 1380), 'apron_bottom': (0, 1500, 1080, 1500),
    'floor_line': (0, 1700, 1080, 1700), 'fan_mount': (540, 0, 540, 40)}


# ============================================================================= numpy SDF toolkit (Blender coords, metres)

def sd_box(P, c, h, r=0.0):
    q = np.abs(P - np.asarray(c, float)) - (np.asarray(h, float) - r)
    return np.sqrt((np.maximum(q, 0.0) ** 2).sum(-1)) + np.minimum(q.max(-1), 0.0) - r


def sd_rect(x, y, hx, hy, r):
    qx = np.abs(x) - (hx - r)
    qy = np.abs(y) - (hy - r)
    return np.hypot(np.maximum(qx, 0), np.maximum(qy, 0)) + np.minimum(np.maximum(qx, qy), 0) - r


def extrude(d2, w):
    """2D sdf d2 combined with a 1D slab distance w (both arrays)."""
    return np.minimum(np.maximum(d2, w), 0) + np.hypot(np.maximum(d2, 0), np.maximum(w, 0))


def smin(a, b, k):
    h = np.clip(0.5 + 0.5 * (b - a) / k, 0.0, 1.0)
    return b * (1 - h) + a * h - k * h * (1 - h)


def smax(a, b, k):
    return -smin(-a, -b, k)


def sd_capsule(P, a, b, ra, rb=None):
    rb = ra if rb is None else rb
    a = np.asarray(a, float)
    b = np.asarray(b, float)
    pa = P - a
    ba = b - a
    t = np.clip((pa @ ba) / (ba @ ba), 0.0, 1.0)
    d = np.linalg.norm(pa - t[..., None] * ba, axis=-1)
    return d - (ra + (rb - ra) * t)


def sd_ellipsoid(P, c, radii):
    return H.sd3_ellipsoid(P - np.asarray(c, float), radii)


def slots(u, v, u0, pitch, n, hu, hv, r):
    """2D sdf of n rounded slots repeated along u (centres u0 + k*pitch), half sizes hu x hv."""
    k = np.clip(np.round((u - u0) / pitch), 0, n - 1)
    return sd_rect(u - (u0 + k * pitch), v, hu, hv, r)


def field_mesh(name, fn, lo, hi, step, mat, role='prop'):
    f = H.FieldFn(fn, lo, hi)
    V, Q, N = H.mesh_field(f, step, verbose=True)
    o = H.add_mesh(name, V, Q, N, mat, icon_frame=False)
    o['role'] = role
    return o


# ============================================================================= bpy helpers

def _bpy():
    global bpy, Vector
    if bpy is None:
        H._bpy()
        import bpy as _b
        from mathutils import Vector as _V
        bpy, Vector = _b, _V
    return bpy


def reset(res, samples, transparent=True):
    sc = H.reset(res, samples, 'night')
    sc.render.threads_mode = 'FIXED'
    sc.render.threads = THREADS
    sc.cycles.adaptive_threshold = 0.02
    sc.cycles.adaptive_min_samples = 0
    sc.cycles.seed = 21
    sc.cycles.use_animated_seed = False
    sc.cycles.diffuse_bounces = 3
    sc.cycles.glossy_bounces = 3
    sc.cycles.transmission_bounces = 4
    sc.cycles.max_bounces = 8
    sc.render.film_transparent = transparent
    sc.render.use_persistent_data = False
    sc.view_settings.exposure = 0.0
    w = bpy.data.worlds.new('W_black')
    sc.world = w
    bg = w.node_tree.nodes.get('Background')
    bg.inputs['Color'].default_value = (0, 0, 0, 1)
    bg.inputs['Strength'].default_value = 0.0
    return sc


def world_dark(strength=1.0):
    """Very dark warm world for object-centred props (faint glossy context, never a light source)."""
    w = bpy.context.scene.world
    bg = w.node_tree.nodes['Background']
    bg.inputs['Color'].default_value = tuple(mul('NIGHT_1', 1.0)) + (1,)
    bg.inputs['Strength'].default_value = strength


def link(o):
    bpy.context.scene.collection.objects.link(o)
    return o


def set_vis(o, camera=True, diffuse=True, glossy=True, transmission=True, shadow=True, scatter=True):
    o.visible_camera = camera
    o.visible_diffuse = diffuse
    o.visible_glossy = glossy
    o.visible_transmission = transmission
    o.visible_shadow = shadow
    o.visible_volume_scatter = scatter


def _aim(o, target):
    d = Vector(target) - o.location
    o.rotation_euler = d.to_track_quat('-Z', 'Y').to_euler()


def light(name, kind, loc, energy, color, target=None, size=None, soft=None, spot=None, blend=0.15, glossy=True,
          group=None):
    ld = bpy.data.lights.new(name, kind)
    ld.energy = energy
    ld.color = hue(color)
    if kind == 'AREA':
        ld.shape = 'RECTANGLE'
        ld.size, ld.size_y = size
    if soft is not None:
        ld.shadow_soft_size = soft
    if kind == 'SPOT':
        ld.spot_size = math.radians(spot)
        ld.spot_blend = blend
    o = link(bpy.data.objects.new(name, ld))
    o.location = loc
    if target is not None:
        _aim(o, target)
    set_vis(o, camera=False, glossy=glossy)
    o['group'] = group or name
    return o


def mesh_from(name, V, F, mat=None, uv=None, smooth=True, role='prop'):
    """Mesh object from numpy verts (N, 3) and faces (list or (M, k) array); uv: per-vertex (N, 2)."""
    me = bpy.data.meshes.new(name)
    me.from_pydata([tuple(map(float, v)) for v in np.asarray(V)], [], [tuple(int(i) for i in f) for f in F])
    me.update()
    if uv is not None:
        lay = me.uv_layers.new(name='UVMap')
        idx = np.empty(len(me.loops), np.int64)
        me.loops.foreach_get('vertex_index', idx)
        lay.data.foreach_set('uv', np.asarray(uv, np.float32)[idx].ravel())
    me.polygons.foreach_set('use_smooth', np.full(len(me.polygons), smooth, bool))
    if mat is not None:
        me.materials.append(mat)
    o = link(bpy.data.objects.new(name, me))
    o['role'] = role
    return o


def bm_obj(name, bm, mat, role='prop', smooth=False, bevel=0.0, seg=2):
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    me.polygons.foreach_set('use_smooth', np.full(len(me.polygons), smooth, bool))
    if mat is not None:
        me.materials.append(mat)
    o = link(bpy.data.objects.new(name, me))
    o['role'] = role
    if bevel > 0:
        m = o.modifiers.new('bevel', 'BEVEL')
        m.width = bevel
        m.segments = seg
        m.limit_method = 'ANGLE'
        m.angle_limit = math.radians(40)
    return o


def cube(name, c0, c1, mat, role='prop', bevel=0.0, seg=2):
    """Axis-aligned box from corner c0 to corner c1 (world coords; object origin at the world origin)."""
    import bmesh
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    c0, c1 = np.asarray(c0, float), np.asarray(c1, float)
    bmesh.ops.scale(bm, vec=tuple(np.abs(c1 - c0)), verts=bm.verts)
    bmesh.ops.translate(bm, vec=tuple((c0 + c1) / 2), verts=bm.verts)
    return bm_obj(name, bm, mat, role, bevel=bevel, seg=seg)


def cyl(name, c, r, h, mat, axis='Z', role='prop', seg=48, r2=None, smooth=True, bevel=0.0):
    import bmesh
    from mathutils import Matrix
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=seg, radius1=r, radius2=r if r2 is None else r2,
                          depth=h)
    if axis == 'Y':
        bmesh.ops.rotate(bm, verts=bm.verts, cent=(0, 0, 0), matrix=Matrix.Rotation(math.radians(90), 3, 'X'))
    elif axis == 'X':
        bmesh.ops.rotate(bm, verts=bm.verts, cent=(0, 0, 0), matrix=Matrix.Rotation(math.radians(90), 3, 'Y'))
    bmesh.ops.translate(bm, vec=tuple(c), verts=bm.verts)
    o = bm_obj(name, bm, mat, role, smooth=smooth, bevel=bevel, seg=2)
    if smooth:   # caps flat, sides smooth
        me = o.data
        for p in me.polygons:
            n = np.array(p.normal)
            ax = {'Z': 2, 'Y': 1, 'X': 0}[axis]
            p.use_smooth = bool(abs(n[ax]) < 0.9)
    return o


def torus_mesh(R, r, nu=96, nv=24):
    u = np.linspace(0, 2 * np.pi, nu, endpoint=False)
    v = np.linspace(0, 2 * np.pi, nv, endpoint=False)
    U, Vv = np.meshgrid(u, v, indexing='ij')
    X = (R + r * np.cos(Vv)) * np.cos(U)
    Y = (R + r * np.cos(Vv)) * np.sin(U)
    Z = r * np.sin(Vv)
    V = np.stack([X, Y, Z], -1).reshape(-1, 3)
    F = []
    for i in range(nu):
        for j in range(nv):
            a = i * nv + j
            b = ((i + 1) % nu) * nv + j
            c = ((i + 1) % nu) * nv + (j + 1) % nv
            d = i * nv + (j + 1) % nv
            F.append((a, b, c, d))
    return V, F


def torus(name, c, R, r, mat, axis='Z', role='prop', nu=96, nv=24):
    V, F = torus_mesh(R, r, nu, nv)
    if axis == 'Y':
        V = V[:, [0, 2, 1]] * np.array([1, -1, 1])
    elif axis == 'X':
        V = V[:, [2, 1, 0]]
    return mesh_from(name, V + np.asarray(c), F, mat, role=role)


def lathe(name, prof, c, mat, seg=96, role='prop', axis='Z'):
    """Surface of revolution: prof = [(r, z), ...] (a closed or open polyline, r >= 0) around Z through c."""
    prof = np.asarray(prof, float)
    a = np.linspace(0, 2 * np.pi, seg, endpoint=False)
    V = np.stack([np.outer(np.cos(a), prof[:, 0]), np.outer(np.sin(a), prof[:, 0]),
                  np.tile(prof[:, 1], (seg, 1))], -1).reshape(-1, 3)
    n = len(prof)
    F = []
    for i in range(seg):
        for j in range(n - 1):
            a0 = i * n + j
            b0 = ((i + 1) % seg) * n + j
            F.append((a0, b0, b0 + 1, a0 + 1))
    if axis == 'Y':
        V = V[:, [0, 2, 1]] * np.array([1, -1, 1])
    o = mesh_from(name, V + np.asarray(c), F, mat, role=role)
    m = o.modifiers.new('weld', 'WELD')
    m.merge_threshold = 1e-6
    return o


# ----------------------------------------------------------------------------- shader graph helper

class G:
    def __init__(self, nt):
        self.nt = nt

    def n(self, kind, **kw):
        node = self.nt.nodes.new(kind)
        for k, v in kw.items():
            setattr(node, k, v)
        return node

    def put(self, sock, v):
        if isinstance(v, bpy.types.NodeSocket):
            self.nt.links.new(v, sock)
        else:
            if sock.type == 'RGBA' and len(v) == 3:
                v = tuple(v) + (1.0,)
            sock.default_value = v

    def m(self, op, a, b=0.0, c=None, clamp=False):
        node = self.n('ShaderNodeMath', operation=op, use_clamp=clamp)
        self.put(node.inputs[0], a)
        self.put(node.inputs[1], b)
        if c is not None:
            self.put(node.inputs[2], c)
        return node.outputs[0]

    def mix(self, fac, a, b):
        node = self.n('ShaderNodeMix', data_type='RGBA', clamp_factor=True)
        ins = {s.identifier: s for s in node.inputs}
        self.put(ins['Factor_Float'], fac)
        self.put(ins['A_Color'], a)
        self.put(ins['B_Color'], b)
        return [s for s in node.outputs if s.identifier == 'Result_Color'][0]

    def co(self, kind='Object'):
        return self.n('ShaderNodeTexCoord').outputs[kind]

    def uv(self):
        return self.n('ShaderNodeUVMap').outputs[0]

    def xyz(self, v):
        s = self.n('ShaderNodeSeparateXYZ')
        self.put(s.inputs[0], v)
        return s.outputs[0], s.outputs[1], s.outputs[2]

    def comb(self, x, y, z):
        c = self.n('ShaderNodeCombineXYZ')
        for i, v in enumerate((x, y, z)):
            self.put(c.inputs[i], v)
        return c.outputs[0]

    def vscale(self, v, s):
        node = self.n('ShaderNodeVectorMath', operation='MULTIPLY')
        self.put(node.inputs[0], v)
        self.put(node.inputs[1], s)
        return node.outputs[0]

    def noise(self, vec, scale, detail=2.0, rough=0.5, dist=0.0, color=False):
        nn = self.n('ShaderNodeTexNoise')
        if vec is not None:
            self.put(nn.inputs['Vector'], vec)
        nn.inputs['Scale'].default_value = scale
        nn.inputs['Detail'].default_value = detail
        nn.inputs['Roughness'].default_value = rough
        nn.inputs['Distortion'].default_value = dist
        return nn.outputs[1] if color else nn.outputs[0]

    def wave(self, vec, scale, dist=4.0, detail=3.0, bands='X', profile='SIN'):
        w = self.n('ShaderNodeTexWave', wave_type='BANDS', bands_direction=bands, wave_profile=profile)
        if vec is not None:
            self.put(w.inputs['Vector'], vec)
        w.inputs['Scale'].default_value = scale
        w.inputs['Distortion'].default_value = dist
        w.inputs['Detail'].default_value = detail
        return w.outputs[1]

    def mr(self, v, a, b, c=0.0, d=1.0, smooth=False):
        node = self.n('ShaderNodeMapRange', interpolation_type='SMOOTHSTEP' if smooth else 'LINEAR', clamp=True)
        self.put(node.inputs['Value'], v)
        node.inputs['From Min'].default_value = a
        node.inputs['From Max'].default_value = b
        self.put(node.inputs['To Min'], c)
        self.put(node.inputs['To Max'], d)
        return node.outputs[0]

    def bump(self, h, strength, distance, normal=None):
        b = self.n('ShaderNodeBump')
        b.inputs['Strength'].default_value = strength
        b.inputs['Distance'].default_value = distance
        self.put(b.inputs['Height'], h)
        if normal is not None:
            self.put(b.inputs['Normal'], normal)
        return b.outputs[0]


def principled(name, base, rough=0.5, metal=0.0, spec=0.5, coat=0.0, coat_rough=0.06, sss=0.0,
               sss_radius=(1.0, 0.5, 0.3), sss_scale=0.01, sheen=0.0, ior=1.45, aniso=0.0):
    m = bpy.data.materials.new(name)
    nt = m.node_tree
    b = nt.nodes['Principled BSDF']
    b.inputs['Base Color'].default_value = tuple(lin(base)) + (1.0,)
    b.inputs['Roughness'].default_value = rough
    b.inputs['Metallic'].default_value = metal
    b.inputs['Specular IOR Level'].default_value = spec
    b.inputs['IOR'].default_value = ior
    if coat:
        b.inputs['Coat Weight'].default_value = coat
        b.inputs['Coat Roughness'].default_value = coat_rough
    if sss:
        b.subsurface_method = 'RANDOM_WALK'
        b.inputs['Subsurface Weight'].default_value = sss
        b.inputs['Subsurface Radius'].default_value = sss_radius
        b.inputs['Subsurface Scale'].default_value = sss_scale
    if sheen:
        b.inputs['Sheen Weight'].default_value = sheen
    if aniso:
        b.inputs['Anisotropic'].default_value = aniso
    return m, b, G(nt)


def aged(m, b, g, base, cvar=0.10, cscale=30.0, rvar=0.10, rbase=None, bscale=1200.0, bstr=0.10, bdist=0.0003,
         grime=0.0, gscale=6.0, coord='Object'):
    """Colour / roughness variation + fine micro-bump (+ optional low-frequency grime) on a principled material."""
    co = g.co(coord)
    nv = g.noise(co, cscale, 3.0, 0.55)
    k = g.m('MULTIPLY_ADD', g.m('SUBTRACT', nv, 0.5), 2.0 * cvar, 1.0)
    if grime:
        gn = g.noise(co, gscale, 4.0, 0.6)
        k = g.m('MULTIPLY', k, g.mr(gn, 0.45, 0.75, 1.0, 1.0 - grime, smooth=True))
    rgb = g.n('ShaderNodeRGB')
    rgb.outputs[0].default_value = tuple(lin(base)) + (1.0,)
    g.put(b.inputs['Base Color'], g.vscale(rgb.outputs[0], k))
    rb = rbase if rbase is not None else b.inputs['Roughness'].default_value
    rn = g.noise(co, cscale * 1.7, 2.0, 0.5)
    g.put(b.inputs['Roughness'], g.m('MULTIPLY_ADD', g.m('SUBTRACT', rn, 0.5), 2.0 * rvar, rb))
    if bstr:
        bn = g.noise(co, bscale, 2.0, 0.6)
        g.put(b.inputs['Normal'], g.bump(bn, bstr, bdist))
    return m


def m_holdout():
    m = bpy.data.materials.new('holdout')
    nt = m.node_tree
    for nn in list(nt.nodes):
        nt.nodes.remove(nn)
    h = nt.nodes.new('ShaderNodeHoldout')
    out = nt.nodes.new('ShaderNodeOutputMaterial')
    nt.links.new(h.outputs[0], out.inputs[0])
    return m


def m_emit(name, color, strength=1.0, light=False):
    m = bpy.data.materials.new(name)
    nt = m.node_tree
    for nn in list(nt.nodes):
        nt.nodes.remove(nn)
    e = nt.nodes.new('ShaderNodeEmission')
    e.inputs['Color'].default_value = tuple(lin(color)) + (1.0,)
    e.inputs['Strength'].default_value = strength
    out = nt.nodes.new('ShaderNodeOutputMaterial')
    nt.links.new(e.outputs[0], out.inputs[0])
    m.cycles.emission_sampling = 'AUTO' if light else 'NONE'
    return m


def m_emit_masked(name, color, mask_fn, strength=1.0):
    """Emission where mask_fn(g) -> 1, holdout elsewhere (legend shine-through pass)."""
    m = bpy.data.materials.new(name)
    nt = m.node_tree
    for nn in list(nt.nodes):
        nt.nodes.remove(nn)
    g = G(nt)
    e = g.n('ShaderNodeEmission')
    e.inputs['Color'].default_value = tuple(lin(color)) + (1.0,)
    e.inputs['Strength'].default_value = strength
    h = g.n('ShaderNodeHoldout')
    mx = g.n('ShaderNodeMixShader')
    g.put(mx.inputs[0], mask_fn(g))
    g.nt.links.new(h.outputs[0], mx.inputs[1])
    g.nt.links.new(e.outputs[0], mx.inputs[2])
    out = g.n('ShaderNodeOutputMaterial')
    g.nt.links.new(mx.outputs[0], out.inputs[0])
    m.cycles.emission_sampling = 'NONE'
    return m


# ============================================================================= the room (desk_plate + context for room props)

def mat_wall():
    base = mixl('SMOKE', 'ASH', 0.35)
    m, b, g = principled('wall_limewash', base, rough=0.92, spec=0.3)
    co = g.co('Object')
    x, y, z = g.xyz(co)
    big = g.noise(co, 1.6, 4.0, 0.6)                        # blotchy lime-wash
    k = g.m('MULTIPLY_ADD', g.m('SUBTRACT', big, 0.5), 0.34, 1.0)
    fine = g.noise(co, 60.0, 3.0, 0.6)
    k = g.m('MULTIPLY', k, g.m('MULTIPLY_ADD', fine, 0.12, 0.94))
    # seepage stains: vertical streaks hanging from the ceiling line and a damp band near the floor
    st = g.noise(g.comb(g.m('MULTIPLY', x, 9.0), g.m('MULTIPLY', z, 0.9), y), 1.0, 3.0, 0.55)
    top = g.mr(z, CEIL_Z - 0.75, CEIL_Z - 0.05, 0.0, 1.0, smooth=True)
    stain = g.m('MULTIPLY', g.mr(st, 0.48, 0.70, 0.0, 1.0, smooth=True), top)
    damp = g.mr(z, 0.45, 0.05, 0.0, 0.6, smooth=True)
    stain = g.m('MAXIMUM', stain, g.m('MULTIPLY', damp, g.mr(g.noise(co, 3.0, 3.0, 0.6), 0.4, 0.7, 0.3, 1.0)))
    # hand grime around the switchboard
    dx = g.m('SUBTRACT', x, (SB_X0 + SB_X1) / 2)
    dz = g.m('SUBTRACT', z, (SB_Z0 + SB_Z1) / 2 - 0.05)
    rr = g.m('SQRT', g.m('ADD', g.m('MULTIPLY', dx, dx), g.m('MULTIPLY', g.m('MULTIPLY', dz, 0.75), g.m('MULTIPLY', dz, 0.75))))
    grime = g.m('MULTIPLY', g.mr(rr, 0.26, 0.10, 0.0, 0.45, smooth=True), g.mr(g.noise(co, 14.0, 3.0, 0.6), 0.3, 0.7, 0.5, 1.0))
    stain = g.m('MAXIMUM', stain, grime)
    k = g.m('MULTIPLY', k, g.m('MULTIPLY_ADD', stain, -0.42, 1.0))
    rgb = g.n('ShaderNodeRGB')
    rgb.outputs[0].default_value = tuple(base) + (1.0,)
    g.put(b.inputs['Base Color'], g.vscale(rgb.outputs[0], k))
    g.put(b.inputs['Normal'], g.bump(g.noise(co, 220.0, 3.0, 0.6), 0.25, 0.002))
    return m


def mat_teak(name='teak'):
    base = mixl('NIGHT_1', 'EMBER', 0.15)
    m, b, g = principled(name, base, rough=0.30, coat=0.45, coat_rough=0.18, spec=0.5)
    co = g.co('Object')
    x, y, z = g.xyz(co)
    grain = g.wave(g.comb(g.m('MULTIPLY', x, 0.12), y, g.m('MULTIPLY', z, 1.0)), 9.0, 7.0, 3.0, bands='Y')
    fine = g.noise(g.comb(g.m('MULTIPLY', x, 0.08), g.m('MULTIPLY', y, 3.0), z), 120.0, 2.0, 0.6)
    k = g.m('MULTIPLY', g.mr(grain, 0.0, 1.0, 0.72, 1.18), g.m('MULTIPLY_ADD', fine, 0.25, 0.88))
    # water rings (glass marks) on the top
    ring_k = None
    for (rx, ry, R) in ((0.50, 1.43, 0.034), (-0.12, 1.395, 0.031), (0.62, 1.52, 0.036)):
        ddx = g.m('SUBTRACT', x, rx)
        ddy = g.m('SUBTRACT', y, ry)
        d = g.m('SQRT', g.m('ADD', g.m('MULTIPLY', ddx, ddx), g.m('MULTIPLY', ddy, ddy)))
        e = g.m('ABSOLUTE', g.m('SUBTRACT', d, R))
        ring = g.mr(e, 0.0035, 0.0006, 0.0, 1.0, smooth=True)
        ring_k = ring if ring_k is None else g.m('MAXIMUM', ring_k, ring)
    k = g.m('MULTIPLY', k, g.m('MULTIPLY_ADD', ring_k, 0.6, 1.0))
    rgb = g.n('ShaderNodeRGB')
    rgb.outputs[0].default_value = tuple(base) + (1.0,)
    g.put(b.inputs['Base Color'], g.vscale(rgb.outputs[0], k))
    g.put(b.inputs['Coat Roughness'], g.m('MULTIPLY_ADD', ring_k, 0.35, 0.16))
    g.put(b.inputs['Normal'], g.bump(fine, 0.08, 0.0005))
    return m


def mat_paper(name='paper', lines=True):
    base = mixl('IVORY', 'ASH', 0.30)
    m, b, g = principled(name, base, rough=0.75, spec=0.35, sss=0.15, sss_radius=(1.0, 0.9, 0.8), sss_scale=0.002)
    b.inputs['Sheen Weight'].default_value = 0.2
    if lines:
        uv = g.uv()
        u, v, _ = g.xyz(uv)
        # ruled lines every 7 mm across the page (u = metres along the spine), a header line, a red margin
        ph = g.m('FRACT', g.m('DIVIDE', g.m('SUBTRACT', u, 0.012), 0.007))
        ln = g.mr(g.m('ABSOLUTE', g.m('SUBTRACT', ph, 0.5)), 0.5, 0.42, 0.0, 1.0, smooth=True)
        ln = g.m('MULTIPLY', ln, g.mr(u, 0.008, 0.012, 0.0, 1.0))
        mg = g.mr(g.m('ABSOLUTE', g.m('SUBTRACT', v, 0.080)), 0.0009, 0.0002, 0.0, 1.0, smooth=True)
        rgb = g.n('ShaderNodeRGB')
        rgb.outputs[0].default_value = tuple(base) + (1.0,)
        c1 = g.mix(g.m('MULTIPLY', ln, 0.42), rgb.outputs[0], tuple(mul('SMOKE', 1.3)))
        c2 = g.mix(g.m('MULTIPLY', mg, 0.50), c1, tuple(mul('EMBER', 0.9)))
        g.put(b.inputs['Base Color'], c2)
    g.put(b.inputs['Normal'], g.bump(g.noise(g.co('Object'), 900.0, 2.0, 0.6), 0.06, 0.0002))
    return m


def build_room(want_copy=True):
    """Room shell, table, window + grille + night sky, tube fixture, switchboard, fan canopy, homework copy and
    the lit / practicals light rigs. Every object gets role 'room' (or 'emitvis' / 'sky' for camera-only
    emissive cards). Returns {'lights': {group: [objs]}, 'feat': {...}}."""
    wall = mat_wall()
    ceil_m, b, g = principled('ceiling', 'NIGHT_1', rough=0.9)
    aged(ceil_m, b, g, 'NIGHT_1', cvar=0.25, cscale=3.0, rvar=0.05, bstr=0.1, bscale=150.0)
    floor_m, b, g = principled('floor_redoxide', mixl('NIGHT_1', 'EMBER', 0.22), rough=0.32, coat=0.3, coat_rough=0.2)
    aged(floor_m, b, g, mixl('NIGHT_1', 'EMBER', 0.22), cvar=0.18, cscale=4.0, rvar=0.12, bstr=0.05, bscale=300.0)
    teak = mat_teak()
    paint, b, g = principled('grille_paint', 'NIGHT_0', rough=0.38, spec=0.5, coat=0.3, coat_rough=0.25)
    aged(paint, b, g, 'NIGHT_0', cvar=0.3, cscale=40.0, rvar=0.15, bstr=0.15, bscale=600.0)
    sbm, b, g = principled('switchboard', mixl('ASH', 'IVORY', 0.3), rough=0.42, spec=0.5, coat=0.2, coat_rough=0.2)
    aged(sbm, b, g, mixl('ASH', 'IVORY', 0.3), cvar=0.12, cscale=60.0, rvar=0.12, grime=0.35, gscale=18.0,
         bstr=0.08, bscale=900.0)
    batten, b, g = principled('batten', mixl('ASH', 'IVORY', 0.45), rough=0.4, spec=0.5)
    aged(batten, b, g, mixl('ASH', 'IVORY', 0.45), cvar=0.12, cscale=40.0, grime=0.3, gscale=12.0, bstr=0.05)
    holder, b, g = principled('tube_holder', mixl('ASH', 'NIGHT_1', 0.55), rough=0.5)
    canopy_m, b, g = principled('canopy', 'SMOKE', rough=0.35, metal=0.6)
    aged(canopy_m, b, g, 'SMOKE', cvar=0.2, cscale=50.0, bstr=0.1)
    tube_dead, b, g = principled('tube_glass', mixl('IVORY', 'ASH', 0.35), rough=0.25, spec=0.6)
    objs = []
    R = lambda o: (o.__setitem__('role', 'room'), objs.append(o), o)[2]  # noqa: E731
    X0, X1 = -1.45, 1.65
    Yf, T = -1.7, 0.24
    # back wall (with the window opening) + other walls, floor, ceiling slab
    R(cube('wall_back_l', (X0, WALL_Y, 0), (WIN_X0, WALL_Y + T, CEIL_Z), wall, role='room'))
    R(cube('wall_back_r', (WIN_X1, WALL_Y, 0), (X1, WALL_Y + T, CEIL_Z), wall, role='room'))
    R(cube('wall_back_b', (WIN_X0, WALL_Y, 0), (WIN_X1, WALL_Y + T, WIN_Z0), wall, role='room'))
    R(cube('wall_back_t', (WIN_X0, WALL_Y, WIN_Z1), (WIN_X1, WALL_Y + T, CEIL_Z), wall, role='room'))
    R(cube('wall_left', (X0 - 0.2, Yf, 0), (X0, WALL_Y, CEIL_Z), wall, role='room'))
    R(cube('wall_right', (X1, Yf, 0), (X1 + 0.2, WALL_Y, CEIL_Z), wall, role='room'))
    R(cube('wall_front', (X0, Yf - 0.2, 0), (X1, Yf, CEIL_Z), wall, role='room'))
    R(cube('floor', (X0 - 0.2, Yf - 0.2, -0.1), (X1 + 0.2, WALL_Y + T, 0.0), floor_m, role='room'))
    R(cube('ceiling', (X0 - 0.2, Yf - 0.2, CEIL_Z), (X1 + 0.2, WALL_Y + T, CEIL_Z + 0.15), ceil_m, role='room'))
    # table: top slab, front + side aprons, legs (dark teak, water rings)
    R(cube('table_top', (TABLE_X[0], TABLE_Y0, TABLE_Z - 0.026), (TABLE_X[1], TABLE_Y1, TABLE_Z), teak, role='room',
           bevel=0.004))
    R(cube('apron_front', (TABLE_X[0] + 0.04, APRON_Y, APRON_Z0), (TABLE_X[1] - 0.04, APRON_Y + 0.02, TABLE_Z - 0.026),
           teak, role='room', bevel=0.002))
    R(cube('apron_back', (TABLE_X[0] + 0.04, TABLE_Y1 - 0.06, APRON_Z0), (TABLE_X[1] - 0.04, TABLE_Y1 - 0.04,
                                                                          TABLE_Z - 0.026), teak, role='room'))
    for i, xx in enumerate((TABLE_X[0] + 0.02, TABLE_X[1] - 0.07)):
        R(cube(f'apron_side{i}', (xx, APRON_Y, APRON_Z0), (xx + 0.05, TABLE_Y1 - 0.04, TABLE_Z - 0.026), teak, role='room'))
        for j, yy in enumerate((APRON_Y, TABLE_Y1 - 0.09)):
            R(cube(f'leg{i}{j}', (xx, yy, 0.0), (xx + 0.05, yy + 0.05, TABLE_Z - 0.026), teak, role='room', bevel=0.003))
    # window: reveal comes from the wall pieces; steel frame + iron grille + sky card
    fr = 0.035
    ym = WALL_Y + 0.16
    for nm, a, c in (('win_fr_l', (WIN_X0, ym, WIN_Z0), (WIN_X0 + fr, ym + 0.04, WIN_Z1)),
                     ('win_fr_r', (WIN_X1 - fr, ym, WIN_Z0), (WIN_X1, ym + 0.04, WIN_Z1)),
                     ('win_fr_b', (WIN_X0, ym, WIN_Z0), (WIN_X1, ym + 0.04, WIN_Z0 + fr)),
                     ('win_fr_t', (WIN_X0, ym, WIN_Z1 - fr), (WIN_X1, ym + 0.04, WIN_Z1)),
                     ('win_fr_m', ((WIN_X0 + WIN_X1) / 2 - 0.018, ym, WIN_Z0), ((WIN_X0 + WIN_X1) / 2 + 0.018, ym + 0.04, WIN_Z1))):
        R(cube(nm, a, c, paint, role='room', bevel=0.003))
    yg = WALL_Y + 0.045
    nbar = 6
    for i in range(nbar):
        xx = WIN_X0 + (WIN_X1 - WIN_X0) * (i + 0.5) / nbar
        R(cyl(f'grille_v{i}', (xx, yg, (WIN_Z0 + WIN_Z1) / 2), 0.0075, WIN_Z1 - WIN_Z0, paint, role='room', seg=20))
    for j, zz in enumerate((WIN_Z0 + (WIN_Z1 - WIN_Z0) * 0.30, WIN_Z0 + (WIN_Z1 - WIN_Z0) * 0.68)):
        R(cube(f'grille_h{j}', (WIN_X0, yg - 0.004, zz - 0.016), (WIN_X1, yg + 0.004, zz + 0.016), paint, role='room',
               bevel=0.002))
    sky = m_emit('sky_dusk', mixl('DUSK', 'NIGHT_0', 0.15), 0.85)
    skyo = cube('sky_card', (WIN_X0 - 0.8, WALL_Y + 0.9, WIN_Z0 - 0.9), (WIN_X1 + 0.8, WALL_Y + 0.92, WIN_Z1 + 0.9), sky,
                role='sky')
    set_vis(skyo, camera=True, diffuse=False, glossy=True, transmission=False, shadow=False, scatter=False)
    # switchboard (blank: no labels) with four rocker switches and two screws
    R(cube('switchboard', (SB_X0, SB_Y, SB_Z0), (SB_X1, WALL_Y + 0.002, SB_Z1), sbm, role='room', bevel=0.004))
    sw_w, sw_h = 0.017, 0.030
    for i in range(4):
        cx = SB_X0 + (SB_X1 - SB_X0) * (i + 0.5) / 4
        cz = SB_Z1 - 0.07
        R(cube(f'switch{i}', (cx - sw_w / 2, SB_Y - 0.008 - 0.002 * (i % 2), cz - sw_h / 2), (cx + sw_w / 2, SB_Y, cz + sw_h / 2),
               sbm, role='room', bevel=0.0025))
    sock = cyl('socket_plate', ((SB_X0 + SB_X1) / 2, SB_Y - 0.003, SB_Z0 + 0.075), 0.026, 0.006, sbm, axis='Y',
               role='room', seg=40)
    R(sock)
    hole_m, b, g = principled('socket_hole', 'NIGHT_0', rough=0.8)
    for k, (dx, dz) in enumerate(((0.0, 0.011), (-0.009, -0.007), (0.009, -0.007))):
        R(cyl(f'socket_hole{k}', ((SB_X0 + SB_X1) / 2 + dx, SB_Y - 0.0062, SB_Z0 + 0.075 + dz), 0.0028 if k else 0.0036,
              0.001, hole_m, axis='Y', role='room', seg=16))
    for k, xx in enumerate((SB_X0 + 0.012, SB_X1 - 0.012)):
        R(cyl(f'screw{k}', (xx, SB_Y - 0.0005, (SB_Z0 + SB_Z1) / 2), 0.0035, 0.002, canopy_m, axis='Y', role='room', seg=16))
    # tube-light fixture: batten channel on the wall + two end holders + the tube
    tz = TUBE_Z
    R(cube('batten', (TUBE_X0 - 0.025, WALL_Y - 0.028, tz - 0.004), (TUBE_X1 + 0.025, WALL_Y, tz + 0.034), batten,
           role='room', bevel=0.004))
    for k, xx in enumerate((TUBE_X0 - 0.018, TUBE_X1 + 0.006)):
        R(cube(f'holder{k}', (xx, TUBE_Y - 0.016, tz - 0.016), (xx + 0.012, WALL_Y - 0.026, tz + 0.012), holder,
               role='room', bevel=0.002))
    tlen = TUBE_X1 - TUBE_X0
    tube_vis_m = m_emit('tube_core', 'IVORY', 0.93)
    tube_vis = cyl('tube_vis', ((TUBE_X0 + TUBE_X1) / 2, TUBE_Y, tz), 0.0131, tlen, tube_vis_m, axis='X', role='emitvis',
                   seg=32)
    set_vis(tube_vis, camera=True, diffuse=False, glossy=False, transmission=False, shadow=False, scatter=False)
    tube_dead_o = cyl('tube_dead', ((TUBE_X0 + TUBE_X1) / 2, TUBE_Y, tz), 0.0130, tlen, tube_dead, axis='X',
                      role='room', seg=32)
    R(tube_dead_o)
    tube_light_m = m_emit('tube_emitter', 'IVORY', 135.0, light=True)
    tube_light = cyl('tube_light', ((TUBE_X0 + TUBE_X1) / 2, TUBE_Y, tz), 0.0129, tlen - 0.004, tube_light_m, axis='X',
                     role='light', seg=24)
    set_vis(tube_light, camera=False, diffuse=True, glossy=True, transmission=True, shadow=False, scatter=True)
    # fan canopy + down-rod stub (the fan itself is a 2D sprite)
    R(cyl('canopy', (0.0, FAN_Y, CEIL_Z - 0.032), 0.032, 0.064, canopy_m, role='room', seg=40, r2=0.045))
    # lights
    L = {'lit': [tube_light], 'practicals': []}
    L['lit'].append(light('crt_spill', 'AREA', ((CRT_GX0 + CRT_GX1) / 2, CRT_Y - 0.004, (CRT_GZ0 + CRT_GZ1) / 2), 1.6,
                          'AMBER', target=((CRT_GX0 + CRT_GX1) / 2, CRT_Y - 2.0, (CRT_GZ0 + CRT_GZ1) / 2),
                          size=(CRT_GX1 - CRT_GX0, CRT_GZ1 - CRT_GZ0), glossy=False, group='lit'))
    L['lit'].append(light('window_spill', 'AREA', ((WIN_X0 + WIN_X1) / 2, WALL_Y - 0.010, (WIN_Z0 + WIN_Z1) / 2), 2.2,
                          'DUSK', target=((WIN_X0 + WIN_X1) / 2, WALL_Y - 2.0, (WIN_Z0 + WIN_Z1) / 2), size=(WIN_X1 - WIN_X0, WIN_Z1 - WIN_Z0),
                          glossy=False, group='lit'))
    L['lit'].append(light('room_bounce', 'AREA', (0.25, -0.95, 1.75), 8.0, mixl('IVORY', 'AMBER', 0.2),
                          target=(0.0, 2.0, 0.9), size=(2.0, 1.2), glossy=True, group='lit'))
    L['practicals'].append(light('led_point', 'POINT', (LED_X, BOX_Y - 0.012, LED_Z), 0.5, 'FLAME', soft=0.003,
                                 glossy=True, group='practicals'))
    if want_copy:
        objs += build_copy()
    return dict(objs=objs, lights=L, tube_vis=tube_vis, tube_dead=tube_dead_o, sky=skyo,
                feat={'tube_xy': ((TUBE_X0 + TUBE_X1) / 2, TUBE_Y, tz),
                      'crt_slot': ((CRT_X0 + CRT_X1) / 2, CRT_Y, TABLE_Z),
                      'box_slot': ((BOX_X0 + BOX_X1) / 2, BOX_Y, TABLE_Z)})


def _sheet(name, mat, curve, u0, u1, nu=28, nv=40, thick=0.0):
    """Paper sheet: curve(s) -> (y, z) for s in [0, 1] (cross-section from the spine), extruded along X in [u0, u1].
    UV: u = metres along the spine, v = metres from the outer edge."""
    s = np.linspace(0, 1, nv)
    yz = np.array([curve(t) for t in s])
    seg = np.r_[0, np.cumsum(np.linalg.norm(np.diff(yz, axis=0), axis=1))]
    xs = np.linspace(u0, u1, nu)
    V, UV = [], []
    for x in xs:
        for (yy, zz), sl in zip(yz, seg):
            V.append((x, yy, zz))
            UV.append((x - u0, seg[-1] - sl))
    F = []
    for i in range(nu - 1):
        for j in range(nv - 1):
            a = i * nv + j
            F.append((a, a + nv, a + nv + 1, a + 1))
    o = mesh_from(name, np.array(V), F, mat, uv=np.array(UV), role='room')
    if thick:
        m = o.modifiers.new('solid', 'SOLIDIFY')
        m.thickness = thick
    return o


def build_copy():
    """Homework copy: brown-paper (kraft) cover, open, ruled pages, a few pages fanned up by the breeze."""
    kraft, b, g = principled('kraft_cover', mul('AMBER', 0.4), rough=0.7, spec=0.3)
    aged(kraft, b, g, mul('AMBER', 0.4), cvar=0.12, cscale=80.0, rvar=0.1, grime=0.2, gscale=30.0, bstr=0.15,
         bscale=700.0)
    paper = mat_paper()
    edge, b, g = principled('page_edges', mixl('IVORY', 'ASH', 0.45), rough=0.8)
    objs = []
    ux0, ux1 = -0.440, -0.305                           # spine runs along X (page height 135 mm)
    pd = 0.100                                          # page width (spine -> outer edge)
    ys = TABLE_Y0 + 0.011 + pd + 0.004                  # spine (gutter) line
    z0 = TABLE_Z
    for k, sgn in enumerate((-1, 1)):                   # cover halves (near / far)
        a = (ux0 - 0.004, ys if sgn > 0 else ys - pd - 0.004, z0)
        c = (ux1 + 0.004, ys + pd + 0.004 if sgn > 0 else ys, z0 + 0.0012)
        o = cube(f'copy_cover{k}', a, c, kraft, role='room', bevel=0.0004)
        objs.append(o)
        # page block
        a = (ux0, ys if sgn > 0 else ys - pd, z0 + 0.0012)
        c = (ux1, ys + pd if sgn > 0 else ys, z0 + 0.0042)
        objs.append(cube(f'copy_block{k}', a, c, edge, role='room'))
        # top page lying (gentle gull-wing towards the gutter)
        def flat(t, sgn=sgn):
            yy = ys + sgn * t * pd
            zz = z0 + 0.0043 + 0.0035 * math.exp(-t / 0.10) * (1 - math.exp(-t / 0.015))
            return yy, zz
        objs.append(_sheet(f'copy_page{k}', paper, flat, ux0, ux1))
    # three pages of the far half lifted by the breeze (arching up from the gutter and curling back)
    for k, (a0, curl, ln) in enumerate(((1.55, 2.0, 0.100), (1.15, 2.2, 0.100), (0.75, 1.8, 0.100))):
        def lift(t, a0=a0, curl=curl, ln=ln, k=k):
            n = 24
            yy, zz = ys + 0.0005, z0 + 0.0046 + 0.0004 * k
            th = a0
            ds = ln * t / n
            for _ in range(n):
                yy += math.cos(th) * ds
                zz += math.sin(th) * ds
                th -= curl * ds / ln * 1.0
            return yy, zz
        objs.append(_sheet(f'copy_lift{k}', paper, lift, ux0 + 0.001 * k, ux1 - 0.001 * k, nv=48))
    return objs


# ============================================================================= room props

def mat_housing(name='crt_housing', base='HOUSING', rough=0.55):
    m, b, g = principled(name, base, rough=rough, spec=0.45, coat=0.08, coat_rough=0.3)
    return aged(m, b, g, base, cvar=0.10, cscale=25.0, rvar=0.08, bstr=0.12, bscale=1500.0, bdist=0.00025,
                grime=0.12, gscale=10.0)


def mat_led_lens(name, color):
    m, b, g = principled(name, mul(color, 0.22), rough=0.12, spec=0.6, coat=1.0, coat_rough=0.03)
    return m


def build_crt(q=1.0):
    """CRT monitor: SMOKE bezel with a chamfered lip, convex dark glass, tapered #3B2A22 back housing,
    bottom-bezel vent slots, four small buttons, power button + power LED, swivel stand. No text or logo."""
    step = 0.001 / q
    cx = (CRT_X0 + CRT_X1) / 2
    bw, bh, bd = (CRT_X1 - CRT_X0), (CRT_ZT - CRT_ZB), 0.075
    bz = (CRT_ZT + CRT_ZB) / 2
    gx, gz = (CRT_GX0 + CRT_GX1) / 2, (CRT_GZ0 + CRT_GZ1) / 2
    ghx, ghz = (CRT_GX1 - CRT_GX0) / 2, (CRT_GZ1 - CRT_GZ0) / 2
    vz = CRT_ZB + 0.020
    vx0 = CRT_X0 + 0.045

    def bezel(P):
        x, y, z = P[..., 0], P[..., 1], P[..., 2]
        outer = sd_box(P, (cx, CRT_Y + bd / 2, bz), (bw / 2, bd / 2, bh / 2), 0.013)
        s = np.clip((CRT_YG - y) * 0.75, 0.0, None)
        op = sd_rect(x - gx, z - gz, ghx + s, ghz + s, 0.016 + 0.6 * s)
        d = smax(outer, -op, 0.0025)
        vs = slots(x, z - vz, vx0, 0.0085, 9, 0.0016, 0.0085, 0.0014)
        cut = np.maximum(vs, y - (CRT_Y + 0.005))
        return smax(d, -cut, 0.0008)
    lo = (CRT_X0 - 0.01, CRT_Y - 0.01, CRT_ZB - 0.01)
    hi = (CRT_X1 + 0.01, CRT_Y + bd + 0.01, CRT_ZT + 0.01)
    bez_m = mat_housing('crt_bezel', 'SMOKE', 0.5)
    objs = [field_mesh('crt_bezel', bezel, lo, hi, step, bez_m)]
    # back housing (tapered, rounded), hidden mostly behind the bezel
    hm = mat_housing()
    y0b, y1b = CRT_Y + bd - 0.01, CRT_Y + 0.40

    def back(P):
        x, y, z = P[..., 0], P[..., 1], P[..., 2]
        t = np.clip((y - y0b) / (y1b - y0b), 0, 1)
        hx = bw / 2 - 0.012 - 0.085 * t
        hz = bh / 2 - 0.012 - 0.060 * t
        d2 = sd_rect(x - cx, z - (bz - 0.01 * t), hx, hz, 0.03)
        return smax(d2 * 0.95, np.abs(y - (y0b + y1b) / 2) - (y1b - y0b) / 2, 0.02)
    objs.append(field_mesh('crt_back', back, (CRT_X0, y0b - 0.01, CRT_ZB - 0.01), (CRT_X1, y1b + 0.01, CRT_ZT),
                           0.004 / q, hm))
    # swivel stand: elliptical foot + neck
    fy, fz = CRT_Y + 0.155, TABLE_Z

    def stand(P):
        x, y, z = P[..., 0], P[..., 1], P[..., 2]
        d2 = (np.hypot((x - cx) / 1.0, (y - fy) / 0.82) - 0.130) * 0.82
        foot = extrude(d2 + 0.006, np.abs(z - (fz + 0.009)) - 0.009 + 0.006) - 0.006
        neck = sd_box(P, (cx, fy - 0.02, fz + 0.026), (0.075, 0.055, 0.016), 0.008)
        return smin(foot, neck, 0.008)
    objs.append(field_mesh('crt_stand', stand, (cx - 0.14, fy - 0.13, fz - 0.002), (cx + 0.14, fy + 0.13, CRT_ZB + 0.004),
                           0.0015 / q, bez_m))
    # convex glass (6 mm bulge), edges hidden inside the bezel tunnel
    gm, b, g = principled('crt_glass', 'GLASS', rough=0.04, spec=0.6, coat=1.0, coat_rough=0.02)
    nu, nv = 64, 48
    us = np.linspace(-1, 1, nu)
    vs_ = np.linspace(-1, 1, nv)
    V, UV = [], []
    for u in us:
        for v in vs_:
            xx = gx + u * (ghx + 0.006)
            zz = gz + v * (ghz + 0.006)
            yy = CRT_YG + 0.004 - 0.006 * (1.0 - 0.5 * (u * u + v * v))
            V.append((xx, yy, zz))
    F = [(i * nv + j, i * nv + j + 1, (i + 1) * nv + j + 1, (i + 1) * nv + j) for i in range(nu - 1) for j in range(nv - 1)]
    glass = mesh_from('crt_glass', np.array(V), F, gm, role='glass')
    objs.append(glass)
    # bottom-bezel controls: 4 small buttons, power button, power LED
    btn_m, b, g = principled('crt_buttons', mixl('SMOKE', 'NIGHT_0', 0.4), rough=0.45, coat=0.2)
    zb = CRT_ZB + 0.020
    for k in range(4):
        xx = cx + 0.020 + k * 0.016
        objs.append(cube(f'crt_btn{k}', (xx - 0.0055, CRT_Y - 0.0025, zb - 0.0035), (xx + 0.0055, CRT_Y + 0.004, zb + 0.0035),
                         btn_m, bevel=0.0012))
    px = CRT_X1 - 0.040
    objs.append(cyl('crt_power', (px, CRT_Y - 0.0005, zb), 0.0068, 0.008, btn_m, axis='Y', seg=40, bevel=0.0012))
    led = cyl('crt_led', (px - 0.022, CRT_Y - 0.0002, zb), 0.0024, 0.004, mat_led_lens('crt_led_lens', 'FLAME'),
              axis='Y', seg=24)
    led['role'] = 'emitter'
    objs.append(led)
    feats = {'power_led': (px - 0.022, CRT_Y - 0.0025, zb)}
    quad = [(gx - ghx, CRT_YG, gz + ghz), (gx + ghx, CRT_YG, gz + ghz), (gx + ghx, CRT_YG, gz - ghz),
            (gx - ghx, CRT_YG, gz - ghz)]
    for nm, p in zip(('screen_tl', 'screen_tr', 'screen_br', 'screen_bl'), quad):
        feats[nm] = p
    return dict(objs=objs, emitters={'emit': (led, 'FLAME'), 'screen_mask': (glass, 'IVORY_WHITE')},
                feats=feats, centre=(cx, CRT_Y + 0.15, bz), quad=quad)


def build_tower(q=1.0):
    """Desktop tower on the floor under the table: SMOKE body, NIGHT_1 bezel with two 5.25" bays (#3B2A22 drive
    tray + blank cover), a 3.5" floppy slot, power button with a satin ring, reset button, HDD LED, lower vents."""
    step = 0.0015 / q
    cx = (TW_X0 + TW_X1) / 2
    zc = TW_Z0 + TW_H / 2
    zt = TW_Z0 + TW_H
    body_m = mat_housing('tower_body', 'SMOKE', 0.45)
    bez_m = mat_housing('tower_bezel', 'NIGHT_1', 0.42)
    tray_m = mat_housing('tower_tray', 'HOUSING', 0.38)
    bays = [(zt - 0.050, 0.0735, 0.0205), (zt - 0.098, 0.0735, 0.0205), (zt - 0.150, 0.051, 0.0125)]
    vz = TW_Z0 + 0.040

    def body(P):
        return sd_box(P, (cx, TW_Y + 0.022 + (TW_D - 0.022) / 2, zc), (TW_W / 2, (TW_D - 0.022) / 2, TW_H / 2), 0.006)

    def bezel(P):
        x, y, z = P[..., 0], P[..., 1], P[..., 2]
        d = sd_box(P, (cx, TW_Y + 0.015, zc), (TW_W / 2 + 0.001, 0.015, TW_H / 2 + 0.001), 0.009)
        for (bzc, hx, hz) in bays:
            cut = np.maximum(sd_rect(x - cx, z - bzc, hx, hz, 0.0015), y - (TW_Y + 0.008))
            d = smax(d, -cut, 0.0008)
        vs = slots(z, x - cx, vz - 0.02, 0.008, 6, 0.0018, 0.060, 0.0015)
        d = smax(d, -np.maximum(vs, y - (TW_Y + 0.005)), 0.0008)
        return d
    objs = [field_mesh('tower_body', body, (TW_X0 - 0.01, TW_Y + 0.01, TW_Z0 - 0.01),
                       (TW_X1 + 0.01, TW_Y + TW_D + 0.01, zt + 0.01), 0.004 / q, body_m),
            field_mesh('tower_bezel', bezel, (TW_X0 - 0.01, TW_Y - 0.01, TW_Z0 - 0.01), (TW_X1 + 0.01, TW_Y + 0.04, zt + 0.01),
                       step, bez_m)]
    # drive fronts inside the bays
    (z1, hx1, hz1), (z2, hx2, hz2), (z3, hx3, hz3) = bays
    yb = TW_Y + 0.0035
    objs.append(cube('tray_front', (cx - hx1 + 0.0015, yb, z1 - hz1 + 0.0015), (cx + hx1 - 0.0015, yb + 0.01, z1 + hz1 - 0.0015),
                     tray_m, bevel=0.0012))
    objs.append(cube('tray_line', (cx - hx1 + 0.008, yb - 0.0004, z1 - 0.004), (cx + hx1 - 0.008, yb + 0.002, z1 - 0.003),
                     bez_m))
    objs.append(cube('tray_eject', (cx + hx1 - 0.024, yb - 0.003, z1 - hz1 + 0.006), (cx + hx1 - 0.008, yb + 0.004, z1 - hz1 + 0.011),
                     bez_m, bevel=0.001))
    objs.append(cube('bay2_cover', (cx - hx2 + 0.0015, yb, z2 - hz2 + 0.0015), (cx + hx2 - 0.0015, yb + 0.01, z2 + hz2 - 0.0015),
                     bez_m, bevel=0.0012))
    fl = cube('floppy_front', (cx - hx3 + 0.0012, yb, z3 - hz3 + 0.0012), (cx + hx3 - 0.0012, yb + 0.01, z3 + hz3 - 0.0012),
              tray_m, bevel=0.001)
    objs.append(fl)
    slot_m, b, g = principled('slot_black', 'NIGHT_0', rough=0.6)
    objs.append(cube('floppy_slot', (cx - 0.044, yb - 0.0006, z3 + 0.001), (cx + 0.036, yb + 0.003, z3 + 0.0052), slot_m))
    objs.append(cube('floppy_eject', (cx + 0.026, yb - 0.0025, z3 - 0.0085), (cx + 0.040, yb + 0.003, z3 - 0.0035), bez_m,
                     bevel=0.0008))
    # power button with a satin ring, reset, HDD LED
    pz = TW_Z0 + 0.135
    ring_m, b, g = principled('power_ring', 'ASH', rough=0.32, metal=1.0)
    objs.append(cyl('tw_power', (cx, TW_Y - 0.0015, pz), 0.0095, 0.008, bez_m, axis='Y', seg=48, bevel=0.0015))
    objs.append(torus('tw_power_ring', (cx, TW_Y - 0.0008, pz), 0.0118, 0.0016, ring_m, axis='Y'))
    objs.append(cyl('tw_reset', (cx, TW_Y - 0.001, pz - 0.034), 0.0035, 0.006, bez_m, axis='Y', seg=24, bevel=0.0008))
    hdd = cube('tw_hdd_led', (cx + 0.026, TW_Y - 0.0018, pz - 0.0015), (cx + 0.034, TW_Y + 0.003, pz + 0.0015),
               mat_led_lens('tw_hdd_lens', 'RED'), bevel=0.0006)
    hdd['role'] = 'emitter'
    objs.append(hdd)
    pled = cube('tw_pwr_led', (cx - 0.034, TW_Y - 0.0018, pz - 0.0015), (cx - 0.026, TW_Y + 0.003, pz + 0.0015),
                mat_led_lens('tw_pwr_lens', 'AMBER'), bevel=0.0006)
    objs.append(pled)
    feet_m, b, g = principled('rubber', 'NIGHT_0', rough=0.85)
    for i, xx in enumerate((TW_X0 + 0.02, TW_X1 - 0.02)):
        for j, yy in enumerate((TW_Y + 0.03, TW_Y + TW_D - 0.03)):
            objs.append(cyl(f'tw_foot{i}{j}', (xx, yy, TW_Z0 / 2), 0.009, TW_Z0, feet_m, seg=24))
    return dict(objs=objs, emitters={'emit': (hdd, 'RED')}, feats={'hdd_led': (cx + 0.030, TW_Y - 0.002, pz)},
                centre=(cx, TW_Y + TW_D / 2, zc))


def build_box(q=1.0):
    """Unlabelled power-backup box: matte powder-coated metal #120C0A, side vents, one round LED with a chrome
    bezel, rocker switch in a frame, rubber feet. No text, no logo, no UPS / inverter marks."""
    step = 0.001 / q
    cx = (BOX_X0 + BOX_X1) / 2
    zc = (BOX_Z0 + BOX_ZT) / 2
    hz = (BOX_ZT - BOX_Z0) / 2
    rx, rz = BOX_X1 - 0.040, BOX_Z0 + 0.052

    def body(P):
        x, y, z = P[..., 0], P[..., 1], P[..., 2]
        d = sd_box(P, (cx, BOX_Y + BOX_D / 2, zc), ((BOX_X1 - BOX_X0) / 2, BOX_D / 2, hz), 0.006)
        # side vents on both sides: 2 columns x 6 rows of horizontal slots
        for xs in (BOX_X0, BOX_X1):
            for ycol in (BOX_Y + 0.060, BOX_Y + 0.150):
                vs = slots(z, y - ycol, BOX_Z0 + 0.030, 0.012, 6, 0.0018, 0.032, 0.0016)
                cut = np.maximum(vs, 0.006 - np.abs(x - xs))
                d = smax(d, -cut, 0.0008)
        # front: LED recess and rocker frame recess
        led = np.maximum(np.hypot(x - LED_X, z - LED_Z) - 0.0062, y - (BOX_Y + 0.0015))
        d = smax(d, -led, 0.0006)
        rk = np.maximum(sd_rect(x - rx, z - rz, 0.0135, 0.0095, 0.0015), y - (BOX_Y + 0.002))
        return smax(d, -rk, 0.0006)
    pm, b, g = principled('powdercoat', 'BOXMETAL', rough=0.6, metal=0.15, spec=0.5)
    aged(pm, b, g, 'BOXMETAL', cvar=0.15, cscale=35.0, rvar=0.08, bstr=0.35, bscale=2600.0, bdist=0.0002,
         grime=0.15, gscale=12.0)
    objs = [field_mesh('box_body', body, (BOX_X0 - 0.01, BOX_Y - 0.01, BOX_Z0 - 0.01),
                       (BOX_X1 + 0.01, BOX_Y + BOX_D + 0.01, BOX_ZT + 0.01), step, pm)]
    chrome, b, g = principled('chrome', 'ASH', rough=0.16, metal=1.0)
    objs.append(torus('led_bezel', (LED_X, BOX_Y - 0.0004, LED_Z), 0.0050, 0.0011, chrome, axis='Y', nu=64, nv=16))
    prof = [(0.0, -0.0028), (0.0036, -0.0028), (0.0040, -0.0022), (0.0040, 0.0010), (0.0036, 0.0022), (0.0026, 0.0029),
            (0.0012, 0.0033), (0.0, 0.0034)]
    lens = lathe('led_lens', [(r, z) for r, z in prof], (LED_X, BOX_Y + 0.0006, LED_Z), mat_led_lens('box_led_lens', 'FLAME'),
                 seg=48, axis='Y')
    lens['role'] = 'emitter'
    objs.append(lens)
    fr_m, b, g = principled('rocker_frame', 'NIGHT_0', rough=0.25, coat=0.5, coat_rough=0.1)
    objs.append(cube('rocker_frame', (rx - 0.0125, BOX_Y - 0.0025, rz - 0.0085), (rx + 0.0125, BOX_Y + 0.003, rz + 0.0085),
                     fr_m, bevel=0.0012))
    rk_m, b, g = principled('rocker', 'NIGHT_0', rough=0.35, coat=0.3, coat_rough=0.15)
    rk = cube('rocker', (rx - 0.0095, BOX_Y - 0.0045, rz - 0.0062), (rx + 0.0095, BOX_Y + 0.0, rz + 0.0062), rk_m,
              bevel=0.0012)
    objs.append(rk)
    feet_m, b, g = principled('box_rubber', 'NIGHT_0', rough=0.85)
    for i, xx in enumerate((BOX_X0 + 0.018, BOX_X1 - 0.018)):
        for j, yy in enumerate((BOX_Y + 0.025, BOX_Y + BOX_D - 0.025)):
            objs.append(cyl(f'box_foot{i}{j}', (xx, yy, TABLE_Z + 0.003), 0.007, 0.006, feet_m, seg=24))
    from mathutils import Matrix
    piv = Vector((LED_X, BOX_Y, LED_Z))
    M = Matrix.Translation(piv) @ Matrix.Rotation(math.radians(BOX_YAW), 4, 'Z') @ Matrix.Translation(-piv)
    for o in objs:
        o.matrix_world = M @ o.matrix_world
    rot = lambda p: tuple(M @ Vector(p))  # noqa: E731
    return dict(objs=objs, emitters={'emit': (lens, 'FLAME')}, feats={'led_xy': rot((LED_X, BOX_Y - 0.0028, LED_Z))},
                centre=rot((cx, BOX_Y + BOX_D / 2, zc)))


# ============================================================================= object-centred props

def build_pankhi(q=1.0):
    """Woven straw hand fan (Ø 300 mm): two-tone weave in concentric bands (AMBER x0.55 / EMBER), RED fabric
    piping, bamboo stick (handle 250 mm) running up behind the blade to its centre. Pivot = handle end (origin).
    Local: blade in the XZ plane facing -Y, handle along -Z from the blade."""
    Rb = 0.150
    zc = 0.250 + Rb                                    # blade centre above the handle end
    # blade: polar grid with gentle waviness, solidified 2.4 mm
    nr, na = int(44 * q) + 8, int(160 * q) + 32
    rs = np.linspace(0.0, Rb, nr)
    an = np.linspace(0, 2 * np.pi, na, endpoint=False)
    V = [(0.0, 0.0, zc)]
    for r in rs[1:]:
        for a in an:
            x, z = r * math.cos(a), r * math.sin(a)
            y = (0.004 * math.sin(3 * a + 0.5) * (r / Rb) ** 1.5 + 0.004 * (r / Rb) ** 2
                 - 0.003 * math.cos(a) * (r / Rb))
            V.append((x, y, zc + z))
    F = []
    for j in range(na):
        F.append((0, 1 + j, 1 + (j + 1) % na))
    for i in range(nr - 2):
        for j in range(na):
            a = 1 + i * na + j
            b_ = 1 + i * na + (j + 1) % na
            F.append((a, a + na, b_ + na, b_))
    weave = mat_weave(zc)
    blade = mesh_from('pankhi_blade', np.array(V), F, weave)
    sm = blade.modifiers.new('solid', 'SOLIDIFY')
    sm.thickness = 0.0024
    sm.offset = 0.0
    objs = [blade]
    # piping: torus along the rim, following the rim waviness approximately (rim y ~ +0.010)
    pip, b, g = principled('piping_fabric', 'RED', rough=0.78, spec=0.3, sheen=0.6)
    co = g.co('Object')
    th = g.wave(co, 260.0, 2.0, 1.0, bands='Z')
    g.put(b.inputs['Normal'], g.bump(th, 0.5, 0.0006))
    nu, nv = int(220 * q) + 40, 18
    Vp, Fp = [], []
    for i in range(nu):
        a = 2 * np.pi * i / nu
        x0, z0 = Rb * math.cos(a), Rb * math.sin(a)
        y0 = 0.004 * math.sin(3 * a + 0.5) + 0.004 - 0.003 * math.cos(a)
        rad = np.array([math.cos(a), 0.0, math.sin(a)])
        for j in range(nv):
            v = 2 * np.pi * j / nv
            off = 0.0065 * (math.cos(v) * rad + math.sin(v) * np.array([0, 1.0, 0]))
            Vp.append((x0 + off[0], y0 + off[1], zc + z0 + off[2]))
    for i in range(nu):
        for j in range(nv):
            a_ = i * nv + j
            b_ = ((i + 1) % nu) * nv + j
            Fp.append((a_, b_, ((i + 1) % nu) * nv + (j + 1) % nv, i * nv + (j + 1) % nv))
    objs.append(mesh_from('pankhi_piping', np.array(Vp), Fp, pip))
    # bamboo stick: handle (z 0 -> 0.25) and the spine across the blade (front, proud by ~4 mm)
    bam = mat_bamboo()
    stick = cyl('pankhi_stick', (0.0, 0.0145, (zc + 0.06) / 2), 0.0062, zc + 0.06, bam, seg=32)   # behind the blade
    objs.append(stick)
    for k, zz in enumerate((0.085, 0.205)):
        objs.append(torus(f'bamboo_node{k}', (0.0, 0.0145, zz), 0.0063, 0.0011, bam, nu=48, nv=12))
    cap = cyl('stick_cap', (0.0, 0.0145, 0.0015), 0.0058, 0.003, bam, seg=32)
    objs.append(cap)
    # binding wraps where the stick enters the blade
    for k, zz in enumerate((zc - Rb - 0.004, zc - Rb + 0.012)):
        objs.append(torus(f'pankhi_bind{k}', (0.0, 0.0145, zz), 0.0068, 0.0013, pip, nu=48, nv=12))
    return dict(objs=objs, feats={'pivot': (0.0, 0.0145, 0.0), 'blade_centre': (0.0, 0.0, zc)})


def mat_weave(zc):
    """Basket weave of 6 mm straw strips at +-45 deg (over/under), two-tone concentric bands."""
    m, b, g = principled('weave', mul('AMBER', 0.55), rough=0.55, spec=0.45, coat=0.15, coat_rough=0.3, sheen=0.2)
    co = g.co('Object')
    x, y, z = g.xyz(co)
    zr = g.m('SUBTRACT', z, zc)
    w = 0.006
    s1 = g.m('DIVIDE', g.m('ADD', x, zr), w * 1.4142)
    s2 = g.m('DIVIDE', g.m('SUBTRACT', x, zr), w * 1.4142)
    f1 = g.m('FRACT', s1)
    f2 = g.m('FRACT', s2)
    i1 = g.m('FLOOR', s1)
    i2 = g.m('FLOOR', s2)
    par = g.m('FLOORED_MODULO', g.m('ADD', i1, i2), 2.0)            # which strip is on top
    p1 = g.m('SINE', g.m('MULTIPLY', f1, math.pi))
    p2 = g.m('SINE', g.m('MULTIPLY', f2, math.pi))
    # along-strip undulation so strips dive under each other
    u1 = g.m('SINE', g.m('MULTIPLY', f2, math.pi))
    u2 = g.m('SINE', g.m('MULTIPLY', f1, math.pi))
    top = g.m('MULTIPLY_ADD', par, g.m('SUBTRACT', g.m('MULTIPLY', p1, u1), g.m('MULTIPLY', p2, u2)), g.m('MULTIPLY', p2, u2))
    hgt = g.m('POWER', g.m('MAXIMUM', top, 0.0), 0.6)
    # strip-wise colour jitter
    j1 = g.noise(g.comb(i1, i2, 0.0), 0.37, 0.0, 0.5)
    rr = g.m('SQRT', g.m('ADD', g.m('MULTIPLY', x, x), g.m('MULTIPLY', zr, zr)))
    red1 = g.m('LESS_THAN', g.m('FLOORED_MODULO', i1, 6.0), 2.0)          # EMBER strips: 2 of every 6 (+45 deg)
    red2 = g.m('LESS_THAN', g.m('FLOORED_MODULO', g.m('ADD', i2, 3.0), 6.0), 2.0)   # and (-45 deg), offset
    on1 = g.m('SUBTRACT', 1.0, par)                                        # strip family on top here
    band = g.m('ADD', g.m('MULTIPLY', on1, red1), g.m('MULTIPLY', par, red2))
    border = g.mr(rr, 0.121, 0.124, 0.0, 1.0)                              # plain EMBER border band at the rim
    band = g.m('MAXIMUM', band, border)
    straw = g.n('ShaderNodeRGB')
    straw.outputs[0].default_value = tuple(mul('AMBER', 0.55)) + (1.0,)
    red = g.n('ShaderNodeRGB')
    red.outputs[0].default_value = tuple(lin('EMBER')) + (1.0,)
    col = g.mix(band, straw.outputs[0], red.outputs[0])
    shade = g.m('MULTIPLY', g.m('MULTIPLY_ADD', hgt, 0.45, 0.55), g.m('MULTIPLY_ADD', j1, 0.30, 0.85))
    fib = g.noise(g.comb(g.m('MULTIPLY', g.m('ADD', x, zr), 6.0), g.m('MULTIPLY', g.m('SUBTRACT', x, zr), 260.0), y),
                  1.0, 2.0, 0.5)
    shade = g.m('MULTIPLY', shade, g.m('MULTIPLY_ADD', fib, 0.2, 0.9))
    g.put(b.inputs['Base Color'], g.vscale(col, shade))
    g.put(b.inputs['Normal'], g.bump(g.m('MULTIPLY_ADD', fib, 0.15, hgt), 0.9, 0.0012))
    return m


def mat_bamboo():
    base = mixl('NIGHT_1', 'AMBER', 0.25)
    m, b, g = principled('bamboo', base, rough=0.34, spec=0.5, coat=0.35, coat_rough=0.15)
    co = g.co('Object')
    x, y, z = g.xyz(co)
    fib = g.noise(g.comb(g.m('MULTIPLY', x, 300.0), g.m('MULTIPLY', y, 300.0), g.m('MULTIPLY', z, 6.0)), 1.0, 3.0, 0.6)
    rgb = g.n('ShaderNodeRGB')
    rgb.outputs[0].default_value = tuple(base) + (1.0,)
    g.put(b.inputs['Base Color'], g.vscale(rgb.outputs[0], g.m('MULTIPLY_ADD', fib, 0.55, 0.72)))
    g.put(b.inputs['Normal'], g.bump(fib, 0.2, 0.0004))
    return m


def build_candle(q=1.0):
    """Paraffin candle (IVORY wax, random-walk SSS) on a small steel saucer with a wax pool, drips, charred 2 mm
    wick. Local: saucer bottom at the origin, Z up."""
    zf = 0.0042                    # saucer floor (top surface)
    rc = 0.0112                    # candle radius
    ztop = zf + 0.150
    drips = [  # (angle deg, length, radius)
        (-28.0, 0.060, 0.0017), (-62.0, 0.024, 0.0014), (22.0, 0.105, 0.0016), (75.0, 0.034, 0.0013),
        (150.0, 0.050, 0.0016), (205.0, 0.020, 0.0012)]

    def wax(P):
        x, y, z = P[..., 0], P[..., 1], P[..., 2]
        r = np.hypot(x, y)
        ang = np.arctan2(y, x)
        lip = ztop + 0.0012 * np.sin(3 * ang + 0.7) + 0.0006 * np.sin(7 * ang)
        body = extrude(r - rc + 0.0009, np.abs(z - (zf + lip) / 2) - (lip - zf) / 2 + 0.0009) - 0.0009
        dish = sd_ellipsoid(P, (0.0, 0.0, ztop + 0.0018), (rc - 0.0020, rc - 0.0020, 0.0042))
        d = smax(body, -dish, 0.0012)
        for (a_deg, ln, rad) in drips:
            a = math.radians(a_deg)
            cs, sn = math.cos(a), math.sin(a)
            p0 = np.array([cs * (rc - 0.0002), sn * (rc - 0.0002), ztop - 0.001])
            p1 = np.array([cs * (rc + 0.0004), sn * (rc + 0.0004), ztop - ln])
            dr = sd_capsule(P, p0, p1, rad * 0.75, rad)
            bead = np.linalg.norm(P - (p1 + np.array([cs, sn, 0]) * 0.0004), axis=-1) - rad * 1.25
            d = smin(d, smin(dr, bead, 0.0015), 0.0016)
        pool = sd_ellipsoid(P, (0.0006, -0.0008, zf), (0.0190, 0.0175, 0.0026))
        return smin(d, pool, 0.0035)
    step = 0.00028 / q
    wm, b, g = principled('paraffin', 'IVORY', rough=0.38, spec=0.45, sss=0.6, sss_radius=(1.0, 0.45, 0.25),
                          sss_scale=0.004)
    co = g.co('Object')
    g.put(b.inputs['Normal'], g.bump(g.noise(co, 900.0, 3.0, 0.6), 0.10, 0.00015))
    rgb = g.n('ShaderNodeRGB')
    rgb.outputs[0].default_value = tuple(lin('IVORY')) + (1.0,)
    g.put(b.inputs['Base Color'], g.vscale(rgb.outputs[0], g.m('MULTIPLY_ADD', g.noise(co, 140.0, 2.0, 0.5), 0.10, 0.95)))
    objs = [field_mesh('candle_wax', wax, (-0.024, -0.024, zf - 0.003), (0.024, 0.024, ztop + 0.003), step, wm)]
    # steel saucer (lathe profile, closed shell)
    st, b, g = principled('steel', 'ASH', rough=0.35, metal=1.0, spec=0.5)
    aged(st, b, g, 'ASH', cvar=0.06, cscale=90.0, rvar=0.12, bstr=0.05, bscale=1500.0, grime=0.15, gscale=40.0)
    R = 0.0375
    prof = [(0.0, 0.0), (0.020, 0.0), (0.021, 0.0006), (0.0215, 0.0016), (0.029, 0.0026), (0.034, 0.0050), (0.0368, 0.0082),
            (R, 0.0094), (R - 0.0006, 0.0100), (R - 0.0016, 0.0098), (0.0355, 0.0086), (0.0335, 0.0062), (0.029, 0.0042),
            (0.0215, zf), (0.0, zf)]
    objs.append(lathe('saucer', prof, (0, 0, 0), st, seg=int(96 * q) + 32))
    # wick: charred, slightly bent, 2 mm diameter section
    import bmesh  # noqa: F401
    cu = bpy.data.curves.new('wick_cu', 'CURVE')
    cu.dimensions = '3D'
    cu.bevel_depth = 0.00085
    cu.bevel_resolution = 4
    cu.use_fill_caps = True
    sp = cu.splines.new('BEZIER')
    pts = [(0.0, 0.0, ztop - 0.002), (0.0004, 0.0002, ztop + 0.0035), (0.0018, 0.0006, ztop + 0.0068)]
    sp.bezier_points.add(len(pts) - 1)
    for bp, p in zip(sp.bezier_points, pts):
        bp.co = p
        bp.handle_left_type = bp.handle_right_type = 'AUTO'
    char, b, g = principled('wick_char', 'NIGHT_0', rough=0.85)
    cu.materials.append(char)
    wick = link(bpy.data.objects.new('wick', cu))
    wick['role'] = 'prop'
    objs.append(wick)
    tip = (0.0018, 0.0006, ztop + 0.0068)
    return dict(objs=objs, feats={'wick_tip': tip, 'base': (0.0, 0.0, 0.0), 'candle_base': (0.0, 0.0, zf),
                                  'flame_light': (tip[0], tip[1], tip[2] + 0.012)}, tip=tip, ztop=ztop)


# ----------------------------------------------------------------------------- keycaps

def legend_texture(text, path, ink_h_px=600):
    """Poppins SemiBold legend mask (white on black), tightly framed: returns (path, ink_w/ink_h)."""
    from PIL import Image, ImageDraw, ImageFont
    font = ImageFont.truetype(FONT_SEMI, 1000)
    img = Image.new('L', (4000, 2000), 0)
    d = ImageDraw.Draw(img)
    d.text((200, 200), text, font=font, fill=255)
    a = np.array(img)
    ys, xs = np.nonzero(a > 127)
    crop = a[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    k = ink_h_px / crop.shape[0]
    im = Image.fromarray(crop).resize((max(1, int(round(crop.shape[1] * k))), ink_h_px), Image.LANCZOS)
    pad = 40
    canvas = Image.new('L', (im.width + 2 * pad, im.height + 2 * pad), 0)
    canvas.paste(im, (pad, pad))
    os.makedirs(os.path.dirname(path), exist_ok=True)
    canvas.save(path)
    return path, im.width / im.height, pad


KEY_U = 0.01905
KEYS = {'ctrl': dict(text='Ctrl', units=1.25, ink_h=0.0062), 's': dict(text='S', units=1.0, ink_h=0.0066)}


def keycap_dims(units):
    wb = units * KEY_U - 0.00095
    db = KEY_U - 0.00095
    return dict(wb=wb, db=db, wt=wb - 0.0058, dt=db - 0.0062, h=0.0098, yoff=0.0006, dish=0.0006)


def build_keycap(which, q=1.0):
    """OEM-profile keycap (1u / 1.25u), PBT #0E0908 with fine texture, cylindrical dish, engraved legend
    (#2A1A15) mapped from a Poppins SemiBold mask (also the FLAME shine-through emission of the 'emit' pass).
    Local: base centre at the origin, Z up, front towards -Y."""
    k = KEYS[which]
    dm = keycap_dims(k['units'])
    wb, db, wt, dt, hh, yo, dish = dm['wb'], dm['db'], dm['wt'], dm['dt'], dm['h'], dm['yoff'], dm['dish']
    Rd = ((wt / 2) ** 2 + dish ** 2) / (2 * dish)

    def cap(P):
        x, y, z = P[..., 0], P[..., 1], P[..., 2]
        t = np.clip(z / hh, 0, 1)
        hx = wb / 2 + (wt / 2 - wb / 2) * t
        hy = db / 2 + (dt / 2 - db / 2) * t
        cy = yo * t
        rr = 0.0010 + 0.0016 * t
        d2 = sd_rect(x, y - cy, hx, hy, rr) * 0.955
        topz = hh - dish + (Rd - np.sqrt(np.maximum(Rd * Rd - x * x, 0.0)))
        dz = np.maximum(-z, z - topz)
        dz = np.maximum(dz, z - hh)
        return smax(d2, dz, 0.0011)
    tex, aspect, pad = legend_texture(k['text'], os.path.join(TEX, f'legend_{which}.png'))
    ink_h = k['ink_h']
    ink_w = ink_h * aspect
    full_w = ink_w * (1 + 2 * pad / (600 * aspect))
    full_h = ink_h * (1 + 2 * pad / 600)
    lc = (0.0, yo, hh - dish)

    def mask(g):
        co = g.co('Object')
        x, y, z = g.xyz(co)
        u = g.m('ADD', g.m('DIVIDE', x, full_w), 0.5)
        v = g.m('ADD', g.m('DIVIDE', g.m('SUBTRACT', y, yo), full_h), 0.5)
        img = g.n('ShaderNodeTexImage', interpolation='Cubic', extension='CLIP')
        img.image = bpy.data.images.load(tex, check_existing=True)
        img.image.colorspace_settings.name = 'Non-Color'
        g.put(img.inputs['Vector'], g.comb(u, v, 0.0))
        top = g.mr(z, hh - 0.0016, hh - 0.0010, 0.0, 1.0)                # only on the top surface
        return g.m('MULTIPLY', img.outputs[0], top)
    pm, b, g = principled(f'pbt_{which}', 'PBT', rough=0.45, spec=0.5)
    co = g.co('Object')
    msk = mask(g)
    rgb = g.n('ShaderNodeRGB')
    rgb.outputs[0].default_value = tuple(lin('PBT')) + (1.0,)
    eng = g.n('ShaderNodeRGB')
    eng.outputs[0].default_value = tuple(lin('SMOKE')) + (1.0,)
    nz = g.noise(co, 2400.0, 2.0, 0.6)
    base = g.vscale(rgb.outputs[0], g.m('MULTIPLY_ADD', nz, 0.25, 0.88))
    g.put(b.inputs['Base Color'], g.mix(msk, base, eng.outputs[0]))
    g.put(b.inputs['Roughness'], g.m('MULTIPLY_ADD', msk, 0.15, g.m('MULTIPLY_ADD', nz, 0.10, 0.40)))
    hgt = g.m('SUBTRACT', g.m('MULTIPLY', nz, 0.6), g.m('MULTIPLY', msk, 2.0))
    g.put(b.inputs['Normal'], g.bump(hgt, 0.12, 0.00006))
    step = 0.00011 / q
    o = field_mesh(f'keycap_{which}', cap, (-wb / 2 - 0.001, -db / 2 - 0.001, -0.0005), (wb / 2 + 0.001, db / 2 + 0.001, hh + 0.001),
                   step, pm)
    o['role'] = 'emitter'
    emit_m = m_emit_masked(f'legend_emit_{which}', 'FLAME', mask, 1.0)
    return dict(objs=[o], emit_mat=emit_m, key=o, feats={'legend_centre': lc, 'contact': (0.0, 0.0, 0.0)}, dims=dm,
                ink=(ink_w, ink_h))


# ============================================================================= cameras

def cam_room(res):
    sc = bpy.context.scene
    cd = bpy.data.cameras.new('CAM_ROOM')
    cd.lens = 28.0
    cd.sensor_fit = 'VERTICAL'
    cd.sensor_height = 36.0
    cd.sensor_width = 36.0
    cd.shift_x = 0.0
    cd.shift_y = (HOR_Y - H_PX / 2) / H_PX
    cd.clip_start = 0.05
    cd.clip_end = 50.0
    cam = link(bpy.data.objects.new('CAM_ROOM', cd))
    cam.location = (0.0, 0.0, CAM_Z)
    cam.rotation_euler = (math.radians(90), 0.0, 0.0)
    sc.camera = cam
    return cam


def mesh_points(objs, max_per=6000):
    dg = bpy.context.evaluated_depsgraph_get()
    pts = []
    rng = np.random.default_rng(0)
    for o in objs:
        if o.type not in ('MESH', 'CURVE'):
            continue
        ev = o.evaluated_get(dg)
        me = ev.to_mesh()
        co = np.empty(len(me.vertices) * 3, np.float32)
        me.vertices.foreach_get('co', co)
        co = co.reshape(-1, 3)
        ev.to_mesh_clear()
        if len(co) > max_per:
            co = co[rng.choice(len(co), max_per, replace=False)]
        M = np.array(o.matrix_world)
        pts.append(co @ M[:3, :3].T + M[:3, 3])
    return np.concatenate(pts) if pts else np.zeros((0, 3))


def proj(pts):
    """World points (N, 3) -> pixel coords (N, 2) through the scene camera at the scene resolution."""
    from bpy_extras.object_utils import world_to_camera_view
    sc = bpy.context.scene
    out = []
    for p in pts:
        c = world_to_camera_view(sc, sc.camera, Vector(tuple(float(v) for v in p)))
        out.append((c.x * sc.render.resolution_x, (1 - c.y) * sc.render.resolution_y))
    return np.array(out)


def bbox_px(objs):
    p = proj(mesh_points(objs, 3000))
    return [float(p[:, 0].min()), float(p[:, 1].min()), float(p[:, 0].max()), float(p[:, 1].max())]


# ============================================================================= pass machinery

class Rig:
    """Holds the scene state for one asset and switches it between passes."""

    def __init__(self):
        self.lights = {}          # group -> [light objects]
        self.room = []            # room surfaces (catchers / holdouts in prop passes)
        self.prop = []            # prop objects
        self.emitters = {}        # pass label -> (object, colour) or (object, material)
        self.extra_hide = []      # camera-only room cards hidden in prop passes
        self.orig = {}
        self.hold = None

    def all_lights(self):
        return [o for v in self.lights.values() for o in v]

    def set_lights(self, groups):
        on = set(id(o) for gname in groups for o in self.lights.get(gname, []))
        for o in self.all_lights():
            o.hide_render = id(o) not in on

    def restore_materials(self):
        for o, mats in self.orig.items():
            for i, m in enumerate(mats):
                o.material_slots[i].material = m
        self.orig = {}

    def override_materials(self, objs, mat):
        for o in objs:
            if o.type not in ('MESH', 'CURVE') or not o.material_slots:
                continue
            if o not in self.orig:
                self.orig[o] = [s.material for s in o.material_slots]
            for s in o.material_slots:
                s.material = mat


def settings(sc, kind, samples):
    if kind == 'flat':
        sc.cycles.samples = S_FLAT
        sc.cycles.use_denoising = False
        sc.cycles.use_adaptive_sampling = False
        sc.cycles.max_bounces = 0
    else:
        sc.cycles.samples = samples
        sc.cycles.use_denoising = True
        sc.cycles.use_adaptive_sampling = True
        sc.cycles.max_bounces = 8


def render_to(sc, path):
    sc.render.filepath = path
    bpy.ops.render.render(write_still=True)


def set_border(sc, rect, res):
    """rect = (x0, y0, x1, y1) integer px in the full frame (top-left origin); [x0, x1) x [y0, y1)."""
    W, Hh = res
    x0, y0, x1, y1 = rect
    sc.render.use_border = True
    sc.render.use_crop_to_border = True
    sc.render.border_min_x = (x0 + 0.25) / W
    sc.render.border_max_x = (x1 + 0.25) / W
    sc.render.border_min_y = (Hh - y1 + 0.25) / Hh
    sc.render.border_max_y = (Hh - y0 + 0.25) / Hh


# ============================================================================= asset builds

ASSETS = {}


def asset(name, kind, size, labels, notes):
    def deco(fn):
        ASSETS[name] = dict(name=name, kind=kind, size=size, labels=labels, notes=notes, build=fn)
        return fn
    return deco


def _room_context(rig, plate_only=False):
    R = build_room(want_copy=True)
    rig.room = R['objs']
    rig.lights.update(R['lights'])
    rig.extra_hide = [R['tube_vis'], R['sky']]
    return R


def _torch(rig, centre, side, dist=1.25, elev=35.0, az=42.0, energy=50.0, cone=25.0):
    """Spot from screen-left (side -1) / screen-right (+1), `elev` deg above the prop, aimed at it."""
    c = np.asarray(centre, float)
    a = math.radians(az) * side
    e = math.radians(elev)
    pos = c + dist * np.array([math.sin(a) * math.cos(e), -math.cos(a) * math.cos(e), math.sin(e)])
    return light(f'torch_{"l" if side < 0 else "r"}', 'SPOT', tuple(pos), energy, TORCH, target=tuple(c), soft=0.05,
                 spot=cone, blend=0.25, glossy=True, group='torch')


def _rim(rig, centre, side, dist=0.9, size=(0.25, 0.5), energy=6.0, up=0.25, name='rim'):
    """Soft warm back rim (behind the prop, opposite the key)."""
    c = np.asarray(centre, float)
    pos = c + np.array([-side * 0.55 * dist, 0.85 * dist, up])
    return light(f'{name}_{"l" if side < 0 else "r"}', 'AREA', tuple(pos), energy, RIM, target=tuple(c), size=size,
                 glossy=True)


@asset('desk_plate', 'plate', (1080, 1920), ['lit', 'practicals'],
       'CAM_ROOM plate (opaque): lime-wash wall, NIGHT_1 ceiling, iron-grille window on a dusk sky card, blank '
       'switchboard, 2 ft tube-light batten, fan canopy, dark-teak table with water rings, homework copy (kraft '
       'cover, ruled pages fanned by the breeze), red-oxide floor. lit = tube light (IVORY) + faint CRT spill '
       '(AMBER) + faint window spill; practicals = only the 0.5 W FLAME LED point (near-black). No props in it.')
def build_desk_plate(rig, q, preview):
    R = _room_context(rig)
    tube_vis = R['tube_vis']

    def setup(label):
        rig.set_lights(['lit'] if label == 'lit' else ['practicals'])
        tube_vis.hide_render = label != 'lit'
        R['tube_dead'].hide_render = label == 'lit'
        return 'lit', S_PREVIEW if preview else S_ROOM
    return dict(setup=setup, feats=R['feat'], transparent=False, camera='room')


def _prop_asset(rig, q, preview, builder, catchers):
    R = _room_context(rig)
    P = builder(q)
    rig.prop = P['objs']
    hold = m_holdout()
    centre = P['centre']
    rig.lights['key_l'] = [_torch(rig, centre, -1), _rim(rig, centre, -1, energy=7.0, up=0.04)]
    rig.lights['key_r'] = [_torch(rig, centre, +1), _rim(rig, centre, +1, energy=7.0, up=0.04)]
    if builder is build_crt:   # torch-side spill behind the camera, seen only in the convex glass: the reflection
        for side, lab in ((-1, 'key_l'), (1, 'key_r')):          # slides across it as key_l -> key_r cross-fade
            cd = H.card(f'glass_refl_{lab}', (side * 0.38, -0.55, 1.20), (0.55, 0.32), TORCH, 0.6,
                        target=(centre[0], CRT_YG, (CRT_GZ0 + CRT_GZ1) / 2), shape='oval', soft=0.4)
            rig.lights[lab].append(cd)

    def setup(label):
        rig.restore_materials()
        for o in rig.extra_hide:
            o.hide_render = True
        R['tube_dead'].hide_render = False
        for o in rig.room:
            catch = label == 'room' and o.name in catchers
            o.is_shadow_catcher = catch
            o.is_holdout = not catch
            o.visible_shadow = label == 'room'      # the torch is never blocked by the room (bounce only)
        if label == 'room':
            rig.set_lights(['lit'])
            return 'lit', S_PREVIEW if preview else S_ROOM
        if label in ('key_l', 'key_r'):
            rig.set_lights([label])
            return 'lit', S_PREVIEW if preview else S_ROOM
        rig.set_lights([])
        if label == '_catchmask':      # internal: where the catcher surfaces are visible (white), else holdout
            rig.override_materials(rig.prop, hold)
            white = m_emit('catch_white', (1.0, 1.0, 1.0), 1.0)
            cs = [o for o in rig.room if o.name in catchers]
            for o in cs:
                o.is_holdout = False
            rig.override_materials(cs, white)
            return 'flat', S_FLAT
        # emission-only passes
        obj, col = P['emitters'][label]
        rig.override_materials([o for o in rig.prop if o is not obj], hold)
        em = m_emit(f'{label}_emission', (1.0, 1.0, 1.0) if col == 'IVORY_WHITE' else col, 1.0)
        rig.override_materials([obj], em)
        return 'flat', S_FLAT
    feats = dict(P['feats'])
    extra = {}
    if 'quad' in P:
        extra['quad'] = P['quad']
    return dict(setup=setup, feats=feats, transparent=True, camera='room', crop=True, extra=extra, clean_shadow=True)


@asset('crt_room', 'room_prop', (1080, 1920), ['room', 'key_l', 'key_r', 'screen_mask', 'emit'],
       'CRT monitor (no text/logo): SMOKE bezel with a chamfered lip, convex #0C0807 glass (6 mm bulge, roughness '
       '0.04, coat 1), tapered #3B2A22 back housing, bottom vents, 4 buttons, power button + power LED, swivel '
       'stand. screen_mask = visible glass (white emission), emit = power LED (FLAME).')
def build_crt_room(rig, q, preview):
    return _prop_asset(rig, q, preview, build_crt, ('table_top',))


@asset('tower_room', 'room_prop', (1080, 1920), ['room', 'key_l', 'key_r', 'emit'],
       'Desktop tower under the table (no logos): SMOKE body, NIGHT_1 bezel, #3B2A22 5.25-inch drive tray, blank '
       'bay, 3.5-inch floppy slot, power button with a satin ring, reset, HDD LED (emit, RED), lower vents.')
def build_tower_room(rig, q, preview):
    return _prop_asset(rig, q, preview, build_tower, ('floor',))


@asset('box_room', 'room_prop', (1080, 1920), ['room', 'key_l', 'key_r', 'emit'],
       'Unlabelled power-backup box: matte powder-coated #120C0A metal (roughness 0.6), side vents, rocker switch, '
       'one round LED with a chrome bezel (emit, FLAME), rubber feet. No text, no logo, no UPS/inverter marks.')
def build_box_room(rig, q, preview):
    return _prop_asset(rig, q, preview, build_box, ('table_top',))


@asset('pankhi', 'object', (900, 1100), ['key_l', 'key_r'],
       'Woven straw hand fan (pankhi), Ø 300 mm: two-tone basket weave (AMBER x0.55 / EMBER concentric bands), '
       'RED fabric piping, bamboo handle 250 mm. 85 mm, front 3/4 (yaw 20). key_l / key_r = candle light from '
       'screen-left / screen-right + soft warm back rim. pivot = handle end.')
def build_pankhi_asset(rig, q, preview):
    world_dark(0.6)
    P = build_pankhi(q)
    rig.prop = P['objs']
    root = link(bpy.data.objects.new('pankhi_root', None))
    for o in rig.prop:
        o.parent = root
    root.rotation_euler = (0.0, 0.0, math.radians(20.0))
    bpy.context.view_layer.update()
    feats = {k: tuple(root.matrix_world @ Vector(v)) for k, v in P['feats'].items()}   # local -> world
    c = (0.0, 0.0, 0.33)
    for side, lab in ((-1, 'key_l'), (1, 'key_r')):
        cand = light(f'candle_{lab}', 'POINT', (side * 0.42, -0.38, 0.12), 17.0, mixl('AMBER', 'IVORY', 0.35), soft=0.012,
                     group=lab)
        fill = light(f'fill_{lab}', 'AREA', (-side * 0.6, -0.9, 0.5), 1.2, mixl('IVORY', 'AMBER', 0.4), target=c,
                     size=(0.8, 0.8), glossy=False, group=lab)
        rim = _rim(rig, c, side, dist=0.8, size=(0.3, 0.7), energy=14.0, up=0.2, name=f'rim_{lab}')
        strip = H.card(f'strip_{lab}', (side * 0.15, -0.55, 0.85), (0.6, 0.12), mixl('IVORY', 'AMBER', 0.3), 1.5,
                       target=c, soft=0.3)
        strip['group'] = lab
        rig.lights[lab] = [cand, fill, rim]
        rig.cards = getattr(rig, 'cards', {})
        rig.cards.setdefault(lab, []).append(strip)

    def setup(label):
        rig.set_lights([label])
        for lab, cards in rig.cards.items():
            for o in cards:
                o.hide_render = lab != label
        return 'lit', S_PREVIEW if preview else S_MACRO
    return dict(setup=setup, feats=feats, transparent=True, camera=dict(lens=85.0, elev=6.0, fill=0.80),
                frame_objs=rig.prop)


@asset('candle', 'object', (600, 1400), ['self', 'key_l', 'key_r'],
       'Paraffin candle (IVORY, SSS 0.6 radius (1, 0.45, 0.25) scale 0.004) with drips and a charred 2 mm wick, '
       'standing in its wax pool on a small steel saucer (ASH metallic, roughness 0.35). 100 mm macro, 8 deg '
       'above. self = point light at the wick tip + 12 mm (AMBER, r 4 mm) only; key_l / key_r = soft warm side '
       'key + back rim. The flame is a 2D element anchored on wick_tip.')
def build_candle_asset(rig, q, preview):
    world_dark(0.4)
    P = build_candle(q)
    rig.prop = P['objs']
    tip = P['tip']
    c = (0.0, 0.0, 0.08)
    rig.lights['self'] = [light('flame', 'POINT', (tip[0], tip[1], tip[2] + 0.012), 0.06, 'AMBER', soft=0.004,
                                group='self')]
    for side, lab in ((-1, 'key_l'), (1, 'key_r')):
        key = light(f'key_{lab}', 'AREA', (side * 0.30, -0.32, 0.20), 0.55, mixl('IVORY', 'AMBER', 0.5), target=c,
                    size=(0.18, 0.28), glossy=True, group=lab)
        rim = _rim(rig, c, side, dist=0.35, size=(0.08, 0.30), energy=3.0, up=0.06, name=f'rim_{lab}')
        rig.lights[lab] = [key, rim]

    def setup(label):
        rig.set_lights([label])
        return 'lit', S_PREVIEW if preview else S_MACRO
    return dict(setup=setup, feats=P['feats'], transparent=True, camera=dict(lens=100.0, elev=8.0, fill=0.80),
                frame_objs=rig.prop)


def _keycap_asset(rig, q, preview, which):
    world_dark(0.35)
    P = build_keycap(which, q)
    rig.prop = P['objs']
    key = P['key']
    root = link(bpy.data.objects.new('key_root', None))
    key.parent = root
    root.rotation_euler = (0.0, 0.0, math.radians(15.0))
    bpy.context.view_layer.update()
    feats = {k: tuple(root.matrix_world @ Vector(v)) for k, v in P['feats'].items()}   # local -> world
    # frame on the Ctrl keycap (both keycaps share this camera): its outline points
    dm = keycap_dims(KEYS['ctrl']['units'])
    fr = []
    for zz, hx, hy in ((0.0, dm['wb'] / 2, dm['db'] / 2), (dm['h'], dm['wt'] / 2, dm['dt'] / 2)):
        for sx in (-1, 1):
            for sy in (-1, 1):
                fr.append((sx * hx, sy * hy, zz))
    rz = np.array([[math.cos(math.radians(15)), -math.sin(math.radians(15)), 0],
                   [math.sin(math.radians(15)), math.cos(math.radians(15)), 0], [0, 0, 1]])
    fr = np.array(fr) @ rz.T
    c = (0.0, 0.0, 0.004)
    for side, lab in ((-1, 'key_l'), (1, 'key_r')):
        top = light(f'monitor_{lab}', 'AREA', (side * 0.06, -0.035, 0.15), 1.2, mixl('IVORY', 'AMBER', 0.35), target=c,
                    size=(0.16, 0.10), glossy=True, group=lab)
        rim = _rim(rig, c, side, dist=0.16, size=(0.05, 0.10), energy=0.9, up=0.03, name=f'rim_{lab}')
        rig.lights[lab] = [top, rim]
    hold = m_holdout()

    def setup(label):
        rig.restore_materials()
        if label == 'emit':
            rig.set_lights([])
            rig.override_materials([key], P['emit_mat'])
            return 'flat', S_FLAT
        rig.set_lights([label])
        return 'lit', S_PREVIEW if preview else S_MACRO
    return dict(setup=setup, feats=feats, transparent=True, camera=dict(lens=100.0, elev=35.0, fill=0.80),
                frame_points=fr, extra=dict(ink_mm=[round(P['ink'][0] * 1000, 2), round(P['ink'][1] * 1000, 2)]))


@asset('keycap_ctrl', 'object', (900, 900), ['key_l', 'key_r', 'emit'],
       'OEM-profile 1.25u keycap, PBT #0E0908 (roughness 0.45, fine texture), legend "Ctrl" (Poppins SemiBold) '
       'engraved #2A1A15; 100 mm macro, 35 deg above, yaw 15. key_l / key_r = soft warm top light (monitor glow) '
       'from left / right + back rim; emit = legend shine-through (FLAME). Same camera as keycap_s.')
def build_keycap_ctrl(rig, q, preview):
    return _keycap_asset(rig, q, preview, 'ctrl')


@asset('keycap_s', 'object', (900, 900), ['key_l', 'key_r', 'emit'],
       'OEM-profile 1u keycap, same material and camera as keycap_ctrl, legend "S".')
def build_keycap_s(rig, q, preview):
    return _keycap_asset(rig, q, preview, 's')


# ============================================================================= render driver

def _alpha_bbox(paths, thr=2):
    import cv2
    bb = None
    for p in paths:
        im = cv2.imread(p, cv2.IMREAD_UNCHANGED)
        a = im[:, :, 3] if im.shape[2] == 4 else np.full(im.shape[:2], 255, np.uint8)
        ys, xs = np.nonzero(a > thr)
        if len(xs) == 0:
            continue
        b = [int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1]
        bb = b if bb is None else [min(bb[0], b[0]), min(bb[1], b[1]), max(bb[2], b[2]), max(bb[3], b[3])]
    return bb


def render_asset(name, preview=False, samples=None):
    import cv2
    _bpy()
    spec = ASSETS[name]
    W, Hh = spec['size']
    res = (W // 2, Hh // 2) if preview else (W, Hh)
    q = 0.55 if preview else 1.0
    t0 = time.time()
    sc = reset(res, samples or S_ROOM, transparent=True)
    rig = Rig()
    S = spec['build'](rig, q, preview)
    sc.render.film_transparent = S.get('transparent', True)
    if S['camera'] == 'room':
        cam_room(res)
    else:
        cp = S['camera']
        pts = S.get('frame_points')
        if pts is None:
            bpy.context.view_layer.update()
            pts = mesh_points(S['frame_objs'])
        H.frame_camera(np.asarray(pts, float), res, fill=cp['fill'], lens=cp['lens'], elev=cp['elev'])
    bpy.context.view_layer.update()
    outdir = os.path.join(PREVIEW if preview else OUT, name, 'passes')
    os.makedirs(outdir, exist_ok=True)
    for f in os.listdir(outdir):
        if f.endswith('.png') or f == 'meta.json':
            os.remove(os.path.join(outdir, f))
    border = None
    if S.get('crop'):
        bb = bbox_px(rig.prop)
        mg = 170 * res[0] / 1080.0
        border = [max(0, int(bb[0] - 1.9 * mg)), max(0, int(bb[1] - mg)), min(res[0], int(math.ceil(bb[2] + 1.9 * mg))),
                  min(res[1], int(math.ceil(bb[3] + mg * 1.6)))]
        set_border(sc, border, res)
    print(f'[{name}] scene built in {time.time() - t0:.1f}s; {res[0]}x{res[1]}; border {border}', flush=True)
    raws = []
    times = {}
    for i, label in enumerate(spec['labels']):
        kind, spp = S['setup'](label)
        settings(sc, kind, samples if (samples and kind != 'flat') else spp)
        p = os.path.join(outdir, f'_raw_{i:02d}_{label}.png')
        t1 = time.time()
        render_to(sc, p)
        times[label] = round(time.time() - t1, 1)
        print(f'  {name}/{label}: {times[label]}s ({kind}, {sc.cycles.samples} spp)', flush=True)
        raws.append(p)
    feats_w = S['feats']
    fpx = {k: [float(v) for v in proj([p])[0]] for k, p in feats_w.items()}
    meta_extra = dict(S.get('extra', {}))
    frame_xy = None
    if S.get('clean_shadow'):
        kind, spp = S['setup']('_catchmask')
        settings(sc, kind, spp)
        mp = os.path.join(outdir, '_raw_catchmask.png')
        render_to(sc, mp)
        clean_shadow(raws[spec['labels'].index('room')], raws[spec['labels'].index('key_l')], mp, res[0] / 1080.0)
        os.remove(mp)
    if border is not None:
        ims = [cv2.imread(p, cv2.IMREAD_UNCHANGED) for p in raws]
        bh, bw = ims[0].shape[:2]
        assert (bw, bh) == (border[2] - border[0], border[3] - border[1]), ((bw, bh), border)
        bb = _alpha_bbox(raws, thr=2)
        pad = int(round(CROP_PAD * res[0] / 1080.0))
        cx0, cy0 = max(0, bb[0] - pad), max(0, bb[1] - pad)
        cx1, cy1 = min(bw, bb[2] + pad), min(bh, bb[3] + pad)
        edge = []
        for p, im in zip(raws, ims):
            a = im[:, :, 3]
            for side, sl in (('left', a[:, 0]), ('top', a[0, :]), ('right', a[:, -1]), ('bottom', a[-1, :])):
                at_frame = ((side == 'left' and border[0] == 0) or (side == 'top' and border[1] == 0) or
                            (side == 'right' and border[2] == res[0]) or (side == 'bottom' and border[3] == res[1]))
                if sl.max() > 2 and not at_frame:
                    edge.append((os.path.basename(p), side, int(sl.max())))
        if edge:
            print(f'  WARNING {name}: alpha touches the render border (enlarge the margin): {edge}', flush=True)
        frame_xy = [border[0] + cx0, border[1] + cy0]
        for i, (p, im) in enumerate(zip(raws, ims)):
            cv2.imwrite(os.path.join(outdir, f'{i:04d}.png'), im[cy0:cy1, cx0:cx1], [cv2.IMWRITE_PNG_COMPRESSION, 6])
        for p in raws:
            os.remove(p)
        fpx = {k: [round(v[0] - frame_xy[0], 1), round(v[1] - frame_xy[1], 1)] for k, v in fpx.items()}
        fpx['frame_xy'] = [float(frame_xy[0]), float(frame_xy[1])]
        meta_extra['frame_xy'] = frame_xy
        meta_extra['crop_rect_frame'] = [frame_xy[0], frame_xy[1], border[0] + cx1, border[1] + cy1]
        if 'quad' in meta_extra:
            qp = proj(meta_extra.pop('quad'))
            meta_extra['screen_quad'] = [[round(x - frame_xy[0], 1), round(y - frame_xy[1], 1)] for x, y in qp]
            meta_extra['screen_quad_frame'] = [[round(x, 1), round(y, 1)] for x, y in qp]
    else:
        for i, p in enumerate(raws):
            os.replace(p, os.path.join(outdir, f'{i:04d}.png'))
        fpx = {k: [round(v[0], 1), round(v[1], 1)] for k, v in fpx.items()}
    size = list(cv2.imread(os.path.join(outdir, '0000.png'), cv2.IMREAD_UNCHANGED).shape[1::-1])
    meta = dict(name=name, variant='passes', mode='static', frames=len(spec['labels']), fps_hint=30, size=size,
                loop=False, labels=list(spec['labels']), notes=spec['notes'], features=fpx,
                samples={lab: (S_FLAT if lab in ('emit', 'screen_mask') else (samples or (S_PREVIEW if preview else
                                                                                      (S_ROOM if spec['kind'] != 'object'
                                                                                       else S_MACRO))))
                         for lab in spec['labels']},
                preview=bool(preview), render_seconds=times, device='CPU', threads=THREADS,
                camera=_cam_meta(), builder='pipeline/jawad_reels/assets3d_bijli_chali_gayi.py')
    if 'pivot' in fpx:
        meta['pivot'] = fpx['pivot']
    meta.update(meta_extra)
    out = H.write_meta(outdir, **meta)
    print(f'  -> {outdir}  size {size}  total {time.time() - t0:.0f}s', flush=True)
    return out


def clean_shadow(room_p, cover_p, mask_p, k=1.0):
    """The 'room' pass = prop over shadow-catcher shadows (black, alpha = shadow). Split it against the prop's
    coverage (alpha of a key pass: same camera and geometry), keep the shadow only where the catcher surface is
    visible (internal mask pass), blur it (sigma 1.6 px), drop the sub-2 % noise floor and recombine
    (A = c + s (1 - c)) keeping the premultiplied prop colour."""
    import cv2
    im = cv2.imread(room_p, cv2.IMREAD_UNCHANGED).astype(np.float32) / 255.0
    cov = cv2.imread(cover_p, cv2.IMREAD_UNCHANGED)[:, :, 3].astype(np.float32) / 255.0
    a = im[:, :, 3]
    rgb = im[:, :, :3]
    lin_ = np.where(rgb <= 0.04045, rgb / 12.92, ((rgb + 0.055) / 1.055) ** 2.4)
    prem = lin_ * a[..., None]
    catch = cv2.imread(mask_p, cv2.IMREAD_UNCHANGED)[:, :, 3].astype(np.float32) / 255.0
    sh = np.clip((a - cov) / np.maximum(1.0 - cov, 1e-3), 0.0, 1.0) * catch
    sh = cv2.GaussianBlur(sh, (0, 0), 1.6 * k) * catch
    sh = sh * np.clip((sh - 0.02) / 0.04, 0.0, 1.0)
    af = np.clip(cov + sh * (1.0 - cov), 0.0, 1.0)
    st = np.where(af[..., None] > 1e-4, prem / np.maximum(af[..., None], 1e-4), 0.0)
    st = np.clip(st, 0, 1)
    srgb = np.where(st <= 0.0031308, st * 12.92, 1.055 * np.power(st, 1 / 2.4) - 0.055)
    out = np.dstack([srgb, af])
    cv2.imwrite(room_p, np.clip(out * 255 + 0.5, 0, 255).astype(np.uint8))


def _cam_meta():
    c = bpy.context.scene.camera
    return dict(lens=round(c.data.lens, 2), sensor_fit=c.data.sensor_fit, location=[round(v, 4) for v in c.location],
                rotation_deg=[round(math.degrees(v), 3) for v in c.rotation_euler], shift=[round(c.data.shift_x, 5),
                                                                                            round(c.data.shift_y, 5)])


# ============================================================================= targets check (no render)

def targets_report(write=True):
    _bpy()
    sc = reset((W_PX, H_PX), 16)
    rig = Rig()
    R = _room_context(rig)
    cam_room((W_PX, H_PX))
    crt = build_crt(0.5)
    tower = build_tower(0.5)
    box = build_box(0.5)
    bpy.context.view_layer.update()
    byname = {o.name: o for o in bpy.context.scene.objects}
    rows = {}
    rows['crt_body'] = bbox_px([o for o in crt['objs'] if o.name in ('crt_bezel', 'crt_stand')])
    rows['crt_glass'] = [*proj([crt['quad'][0]])[0], *proj([crt['quad'][2]])[0]]
    rows['box'] = bbox_px(box['objs'])
    rows['led'] = [*proj([box['feats']['led_xy']])[0]] * 2
    tb = bbox_px(tower['objs'])
    apron_bottom = proj([(0.0, APRON_Y, APRON_Z0)])[0][1]
    rows['tower'] = [tb[0], max(tb[1], apron_bottom), tb[2], min(tb[3], 1920.0)]
    rows['copy'] = bbox_px([o for o in R['objs'] if o.name.startswith('copy')])
    rows['tube'] = bbox_px([byname['tube_dead'], byname['batten']])
    rows['switchboard'] = bbox_px([byname['switchboard']])
    rows['window'] = [*proj([(WIN_X0, WALL_Y, WIN_Z1)])[0], *proj([(WIN_X1, WALL_Y, WIN_Z0)])[0]]
    rows['ceiling_line'] = [0, proj([(0, WALL_Y, CEIL_Z)])[0][1], 1080, proj([(0, WALL_Y, CEIL_Z)])[0][1]]
    rows['floor_line'] = [0, proj([(0, WALL_Y, 0)])[0][1], 1080, proj([(0, WALL_Y, 0)])[0][1]]
    rows['table_edge'] = [0, proj([(0, TABLE_Y0, TABLE_Z)])[0][1], 1080, proj([(0, TABLE_Y0, TABLE_Z)])[0][1]]
    rows['apron_bottom'] = [0, apron_bottom, 1080, apron_bottom]
    fm = bbox_px([byname['canopy']])
    rows['fan_mount'] = [(fm[0] + fm[2]) / 2, max(fm[1], 0.0), (fm[0] + fm[2]) / 2, fm[3]]
    rep = {}
    ok_all = True
    print(f'{"component":14s} {"target (x0 y0 x1 y1)":>26s}   {"measured":>30s}   max|d|')
    for k, tgt in TARGETS.items():
        m = rows.get(k)
        if m is None:
            continue
        d = max(abs(a - b) for a, b in zip(m, tgt))
        ok = bool(d <= 20.0)
        ok_all &= ok
        rep[k] = dict(target=list(tgt), measured=[round(float(v), 1) for v in m], max_dev=round(float(d), 1), ok=ok)
        print(f'{k:14s} {str(tgt):>26s}   {str([round(v) for v in m]):>30s}   {d:5.1f} {"ok" if ok else "FAIL"}')
    rep['ok'] = ok_all
    rep['layout'] = dict(cam_z=CAM_Z, horizon_row=HOR_Y, wall_y=round(WALL_Y, 4), ceiling_z=round(CEIL_Z, 4),
                         table_front_y=round(TABLE_Y0, 4), tower_front_y=round(TW_Y, 4))
    if write:
        os.makedirs(SHEETS, exist_ok=True)
        with open(os.path.join(SHEETS, 'cam_room_targets.json'), 'w') as fh:
            json.dump(rep, fh, indent=1)
    return rep


# ============================================================================= sheets (over black and over FLAME) + room composites

def _read_lin(p):
    import cv2
    im = cv2.imread(p, cv2.IMREAD_UNCHANGED)
    if im.shape[2] == 3:
        im = np.dstack([im, np.full(im.shape[:2], 255, np.uint8)])
    rgb = im[:, :, 2::-1].astype(np.float32) / 255.0
    a = im[:, :, 3:4].astype(np.float32) / 255.0
    return np.concatenate([np.where(rgb <= 0.04045, rgb / 12.92, ((rgb + 0.055) / 1.055) ** 2.4) * a, a], 2)


def _to8(x):
    x = np.clip(x, 0, 1)
    s_ = np.where(x <= 0.0031308, x * 12.92, 1.055 * np.power(x, 1 / 2.4) - 0.055)
    return np.clip(s_ * 255 + 0.5, 0, 255).astype(np.uint8)[:, :, ::-1].copy()


def contact_sheets(root=None, tag='finals', cell=300):
    """Per asset one row: every pass over black, then every pass over FLAME. Returns the sheet paths."""
    import cv2
    root = root or OUT
    rows = []
    for nm in ASSETS:
        d = os.path.join(root, nm, 'passes')
        if not os.path.isfile(os.path.join(d, 'meta.json')):
            continue
        meta = json.load(open(os.path.join(d, 'meta.json')))
        tiles = []
        for bgname, bg in (('black', (0.0, 0.0, 0.0)), ('FLAME', lin('FLAME'))):
            for i, lab in enumerate(meta['labels']):
                im = _read_lin(os.path.join(d, f'{i:04d}.png'))
                h = cell
                w = max(1, int(round(im.shape[1] * h / im.shape[0])))
                im = cv2.resize(im, (w, h), interpolation=cv2.INTER_AREA)
                comp = im[:, :, :3] + np.array(bg, np.float32) * (1 - im[:, :, 3:4])
                t = _to8(comp)
                cv2.putText(t, f'{lab}/{bgname}', (5, 16), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (255, 255, 255), 1, cv2.LINE_AA)
                tiles.append(np.pad(t, ((0, 0), (0, 4), (0, 0)), constant_values=40))
        row = np.concatenate(tiles, 1)
        lab = f"{nm}  {meta['size'][0]}x{meta['size'][1]}  {len(meta['labels'])} passes  frame_xy {meta.get('frame_xy', '-')}"
        hdr = np.full((24, row.shape[1], 3), 30, np.uint8)
        cv2.putText(hdr, lab, (6, 17), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (230, 230, 230), 1, cv2.LINE_AA)
        rows.append(np.concatenate([hdr, row], 0))
    if not rows:
        return []
    os.makedirs(SHEETS, exist_ok=True)
    outs = []
    per = 4
    for k in range(0, len(rows), per):
        chunk = rows[k:k + per]
        wmax = max(r.shape[1] for r in chunk)
        chunk = [np.pad(r, ((0, 6), (0, wmax - r.shape[1]), (0, 0)), constant_values=255) for r in chunk]
        p = os.path.join(SHEETS, f'bcg_{tag}_contact_{k // per}.png')
        cv2.imwrite(p, np.concatenate(chunk, 0))
        outs.append(p)
    return outs


def room_composites(root=None, tag='finals'):
    """Lit room (plate lit + every prop's room pass at frame_xy) and torch room (plate practicals + key_r passes),
    with the brief's target boxes drawn on a copy. Returns the paths."""
    import cv2
    root = root or OUT

    def load(nm):
        d = os.path.join(root, nm, 'passes')
        if not os.path.isfile(os.path.join(d, 'meta.json')):
            return None, None
        return d, json.load(open(os.path.join(d, 'meta.json')))
    dp, mp = load('desk_plate')
    if dp is None:
        return []
    k = mp['size'][0] / 1080.0
    outs = []
    for mode, plate_lab, prop_lab in (('lit', 'lit', 'room'), ('torch', 'practicals', 'key_r')):
        cv = _read_lin(os.path.join(dp, f"{mp['labels'].index(plate_lab):04d}.png"))[:, :, :3].copy()
        if mode == 'torch':
            lit = _read_lin(os.path.join(dp, f"{mp['labels'].index('lit'):04d}.png"))[:, :, :3]
            yy, xx = np.mgrid[0:cv.shape[0], 0:cv.shape[1]]
            hx, hy = 830 * k, 1300 * k
            mask = np.exp(-(((xx - hx) / (300 * k)) ** 2 + ((yy - hy) / (300 * k)) ** 2))[..., None]
            cv = cv + mask * lit * 0.55
        for nm in ('tower_room', 'crt_room', 'box_room'):
            d, m = load(nm)
            if d is None:
                continue
            im = _read_lin(os.path.join(d, f"{m['labels'].index(prop_lab):04d}.png"))
            x0, y0 = m['frame_xy']
            h, w = im.shape[:2]
            reg = cv[y0:y0 + h, x0:x0 + w]
            reg[:] = im[:, :, :3] + reg * (1 - im[:, :, 3:4])
            if mode == 'lit':
                for lab in ('emit', 'screen_mask'):
                    if lab in m['labels']:
                        e = _read_lin(os.path.join(d, f"{m['labels'].index(lab):04d}.png"))
                        gain = 0.30 if lab == 'emit' else 0.0
                        if lab == 'screen_mask':
                            scr = np.array(lin('AMBER'), np.float32) * 0.35
                            reg[:] = reg * (1 - e[:, :, 3:4]) + e[:, :, 3:4] * scr
                        else:
                            reg[:] = reg + e[:, :, :3] * gain
            else:
                if 'emit' in m['labels']:
                    e = _read_lin(os.path.join(d, f"{m['labels'].index('emit'):04d}.png"))
                    reg[:] = reg + e[:, :, :3] * 0.6
        img = _to8(cv)
        os.makedirs(SHEETS, exist_ok=True)
        p = os.path.join(SHEETS, f'bcg_{tag}_room_{mode}.png')
        cv2.imwrite(p, img)
        outs.append(p)
        tz = img.copy()
        for nm_, (x0, y0, x1, y1) in TARGETS.items():
            x0, y0, x1, y1 = [int(round(v * k)) for v in (x0, y0, x1, y1)]
            cv2.rectangle(tz, (x0 - 1, y0 - 1), (x1 + 1, y1 + 1), (60, 255, 60), 1)
            cv2.putText(tz, nm_, (x0 + 2, max(10, y0 - 3)), cv2.FONT_HERSHEY_SIMPLEX, 0.4 * max(k, 0.6), (60, 255, 60), 1,
                        cv2.LINE_AA)
        p2 = os.path.join(SHEETS, f'bcg_{tag}_room_{mode}_targets.png')
        cv2.imwrite(p2, tz)
        outs.append(p2)
    return outs


# ============================================================================= selftest

def selftest():
    assert abs(WALL_Y - 2.7942) < 1e-3 and abs(CEIL_Z - 2.7505) < 1e-3, (WALL_Y, CEIL_Z)
    for t, hx in (('FLAME', (1.0, 0.1441, 0.0103)), ('SMOKE', (0.0232, 0.0103, 0.0075)), ('AMBER', (1.0, 0.4621, 0.063)),
                  ('IVORY', (1.0, 0.8963, 0.7913)), ('ASH', (0.3916, 0.3095, 0.2623))):
        assert max(abs(a - b) for a, b in zip(lin(t), hx)) < 2e-3, (t, lin(t))
    # render-border alignment: a border render must equal the same window of a full render
    import cv2
    _bpy()
    sc = reset((216, 384), 4)
    cam_room((216, 384))
    m, b, g = principled('t', 'IVORY', rough=0.5)
    cube('t_box', (-0.3, 1.5, 0.6), (0.3, 1.8, 1.2), m)
    light('t_sun', 'SUN', (0, 0, 5), 3.0, 'IVORY')
    os.makedirs(SHEETS, exist_ok=True)
    full = os.path.join(SHEETS, '_st_full.png')
    part = os.path.join(SHEETS, '_st_part.png')
    settings(sc, 'flat', 4)
    sc.cycles.max_bounces = 4
    render_to(sc, full)
    set_border(sc, (37, 101, 151, 263), (216, 384))
    render_to(sc, part)
    A = cv2.imread(full, cv2.IMREAD_UNCHANGED)[101:263, 37:151].astype(int)
    B = cv2.imread(part, cv2.IMREAD_UNCHANGED).astype(int)
    assert A.shape == B.shape, (A.shape, B.shape)
    diff = np.abs(A - B)[:, :, 3].max()
    os.remove(full)
    os.remove(part)
    print(f'selftest ok: palette, layout, border alignment (alpha max diff {diff})')
    assert diff <= 8, diff


# ============================================================================= CLI

def _ensure_props_link():
    try:
        link_p = os.path.join(RWS, 'props')
        if OUT == os.path.join(RWS, 'assets3d') and not os.path.lexists(link_p):
            os.symlink('assets3d', link_p)
    except Exception as e:
        print('props symlink:', e)


def main(argv):
    if not argv:
        print(__doc__)
        return
    preview = '--preview' in argv
    samples = None
    if '--samples' in argv:
        samples = int(argv[argv.index('--samples') + 1])
    names = [a for a in argv if not a.startswith('--') and not a.isdigit()]
    if names == ['targets']:
        rep = targets_report()
        print('targets ok' if rep['ok'] else 'targets FAIL')
        return
    if names == ['selftest']:
        selftest()
        return
    if names in (['sheet'], ['previewsheet']):
        root = PREVIEW if names == ['previewsheet'] else OUT
        tag = 'preview' if names == ['previewsheet'] else 'finals'
        for p in contact_sheets(root, tag) + room_composites(root, tag):
            print(p)
        return
    if names == ['all']:
        names = list(ASSETS)
    for nm in names:
        if nm not in ASSETS:
            raise SystemExit(f'unknown asset {nm!r}; have {list(ASSETS)}')
    _ensure_props_link()
    for nm in names:
        render_asset(nm, preview=preview, samples=samples)


if __name__ == '__main__':
    main(sys.argv[1:])
