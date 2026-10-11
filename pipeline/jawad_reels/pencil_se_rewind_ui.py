"""pencil_se_rewind_ui.py - UI / type layer of "Pencil Se Rewind" (Bijli series #1, @jawad_mp4), owner: UI/UX designer
(caption-designer + brand-kit-builder roles). Look 'ember', 1080x1920, 30 fps, DUR 1024 f, grid 112.5 BPM (16 f / beat).

Sources: brand_reels/design/reels/pencil_se_rewind/{SCRIPT.md, script.json, SHOTS.md (C), VO_TIMING.md}, BRAND.md.
VO-LED (LEAD_DECISIONS 3): the approved Vlad VO is final; every caption beat sits on its measured VO word.
Every draw is a pure function of reel time t (s) on the house canvas (premultiplied linear float32 RGBA, K.new_canvas);
static sprites are built once per process (lru_cache). Notes + deviations: brand_reels/design/reels/pencil_se_rewind/UI.md.

    import pencil_se_rewind_ui as UI
    UI.lockups(cv, t, hook='A')        every designed caption lockup (HA / HB, L5, L6, L7, L9, L12, L14 + L15)
    UI.captions(hook).draw(cv, t)      snake captions = the VO words of L2 L3 L4 L8 L10 L11 L13 (3 bands, avoid rects)
    UI.nle(cv, t, media=None)          S10-S13 glass NLE (f576-f909): pull-back into the viewer, timeline panel,
                                       scrubbing playhead, CUT marker, push into the payoff layout, line -> pencil
                                       morph, pencil snap + clip-edge glow.  media(src_t) -> R1 frame (1080x1920)
    UI.outro()                         PO.ProfileOutro('Aap ki pehli cassette kaunsi thi?', key='Pencil ya pen?')
                                       card.draw(cv, t, UI.T_END) / card.post_kw(t, UI.T_END, UI.DUR) / card.cues(...)
    UI.cover(cv)                       cover overlay: HA lockup settled (underline drawn); UI.grid_crop(img) = 3:4
    UI.state(t)                        the NLE state dict (playhead x, src time, timecode, scale, morph ...) for QA
    UI.prewarm()                       builds every sprite (call from the reel's prewarm())
    UI.TM / UI.retime(KEY=frame, ...)  the timing table (frames); UI.derive_vo_timing() recomputes it from the VO words
    UI.lockup_windows(hook)            {id: (f0, f1)} at the current timing (snake hide / QA 2-block rule)
    UI.ink_scan() / UI.vo_alignment() / UI.block_check()      QA helpers (the selftest prints all three)
    python3 pencil_se_rewind_ui.py selftest [lockups snake nle outro cover pencil]
                                       -> workspace/jawad_reels/pencil_se_rewind/ui_selftest/*.png (+ sheet_*.png)
    PSR_UI_TIMING=vo (default: derived from vo_final words) | static (TIMING_VO table) | script (text-led plan)

TIMING (TM, frames inclusive; defaults derived from the measured VO at import - see TIMING_VO for the values and why)
    HA   caps rise t0 -0.1 | 'Pencil.' SLAM HA_key = V1 'Pencil.' - 3 f (f43, with the SFX hit) | underline | exit
         HA_out f62-f69 (across the f64 cut, gone before L2 f70)        HB: 'khatam?' SLAM HB_key (f32)
    L5   'SIRF' rise L5_in (f240 'Sirf') / 'andaza.' glyph rise L5_key (f253)
    L6   'Play.' f320 / 'Galat!' f347 (+ strike through Play) / 'Phir se.' f376; instant swap out at L7_in
    L7   'Mil gaya!' SLAM f395        L9 'CASSETTE' f448 / 'phans gayi!' SLAM f464 + D7 (structure, never moves)
    L12  'Peeche.' / 'Aage.' / 'Peeche.' / 'Yahan.' on the scrub jumps f648 / f656 / f664 / f672 (V9 not in the VO)
    L14  caps f768 (payoff hit, structure) / 'Pencil.' key rise L14_key = V11 'Pencil.' (f832) = NLE pencil snap
    L15  'Scrubbing toh' f852 / 'cassette pe sikhi thi.' f878 (V12 onsets); L14 + L15 leave f884-f895 (razor f896)
LAYOUT (positions = text-box centres; SCRIPT.md 2 / SHOTS.md C)
    HA / HB caps (540, 400), key (540, 580), underline y 700 | L5 (540, 590) | L6 y 420 / 590 / 760 | L7 y 520 |
    L9 y 400 / 570 | L12 (540, 344) | L14 HouseTitle at (540, PAY_Y = 520), underline y 660, L15 y 728 / 800.
    Slam peaks are capped so a wide keyword stays inside x 70-1010 (ink scan, every frame).
SNAKE (snake_captions, VO words): upper band (baseline y 410) L2 L3 L8 L10, lower (y 1380) L4, top (y 330, margin 14)
    L11 L13. Each band clears for the lockup windows, the drop-out f752-f767, the other bands' lines and (upper) the
    f192 cut; splits instead of shrinks: 'Gaana' / 'dhoondna ho?', 'pencil se' / 'wapas'.
NLE (f576-f909; native layout, then the payoff layout after the S12 push)
    background NIGHT_1 -> NIGHT_0 + 40 px grid at 4 %; viewer glass 580 x 720 r 28 (540, 838), media 560 x 700 = R1 crop
    (x 0-1080, y 510-1860), header 'cassette_rewind.mov' jw_mono 24 ASH / timecode jw_mono 28 IVORY, title-safe
    corners, play icon + progress line; timeline glass x 70-1010 y 1260-1470: ruler 1270-1296 (ticks 1 s = 30 px,
    labels every 4 s jw_mono 28, in/out band), V2 1302-1338 (EMBER clips, keyframes), V1 1346-1396 (FLAME clips with
    filmstrip thumbnails), A1 1404-1458 (GOLD peak + RMS waveform, volume line); lane labels jw_mono 28 at x 103 +
    colour tabs; header column x 70-136 stays fixed when the content zooms (like a real NLE); scroll bar.
    time <-> x: x = X_ORIGIN + PXS * src_s (PXS 30 px / s, so the 1 px / f crawl is real time; f576 = x 520).
    Playhead: 4 px FLAME line + glow (3, 10, 28) and a 22 x 26 pentagon head with an AMBER core.
    f576-f597 pull-back (inout_sine 22 f): the frame shrinks into the viewer, the 9:16 mask tightens to 4:5;
    f584-f600 panel + viewer header slide in; 1 px / f crawl from x 520 until the first jump; scrub jumps (inout_expo
    6 f + SNAP landing) at TM['L12'] (f648 / f656 / f664 / f672) -> x 470 / 680 / 500 / 600 (= the cut: CUT chip POP +
    ruler flag + dashed AMBER line); viewer shows the source time under the playhead at 12 Hz; f704-f717 the viewer
    lifts 70 px and fades (it never crosses the top caption band); f704-f744 the
    content zooms 1.0 -> 1.9 about x 600 and the panel grows into the payoff layout (panel y 872-1444, ruler 884-936,
    V2 952-1036, V1 1050-1200, A1 1214-1430); the playhead steps back to screen x 520 f728-f748; f752-f767 the line
    narrows 4 -> 0 px while the pencil (R5 pencil_top, 620 px long, eraser + ferrule in the ruler, eraser top y 876)
    wipes in top -> bottom with a hot scan edge; NLE_snap (f832) SNAP 520 -> 600 with a 2 deg wobble; edit-point
    brackets and clip edges at x 600 glow FLAME for 16 f.
3D: final Blender renders (RWS/assets3d/<name>, meta.json) when present, else the Blender preview renders
    (RWS/out/preview3d, upscaled; layout / selftest only), else the procedural stand-ins.
"""
import functools
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import jawad_kit                                   # noqa: F401,E402  FIRST
from jawad_kit import K, T, J, ui, S3              # noqa: E402
import jawad_tx as X                               # noqa: E402
import profile_outro as PO                         # noqa: E402
import snake_captions as SC                        # noqa: E402

import cv2                                         # noqa: E402
import numpy as np                                 # noqa: E402

SLUG = 'pencil_se_rewind'
LOOK = 'ember'
FPS = K.FPS
HALF = 0.5 / FPS
DUR = 1024 / 30
REPO = os.path.abspath(os.path.join(HERE, '..', '..'))
SCRIPT_JSON = os.path.join(REPO, 'brand_reels', 'design', 'reels', SLUG, 'script.json')
RWS = os.path.join(K.WS, SLUG)
OUT_DIR = os.path.join(RWS, 'ui_selftest')

# outro (L16 / L16k)
OUTRO_Q = 'Aap ki pehli cassette kaunsi thi?'
OUTRO_KEY = 'Pencil ya pen?'
T_END = 896 / 30
OUTRO_DUR = 128 / 30


def F(f):
    return f / FPS


# =================================================================================================== timing (VO-led)
# Every caption / UI beat in reel frames (30 fps). Defaults = the measured Vlad VO (VO_TIMING.md section 3,
# LEAD_DECISIONS 3: picture beats move to the VO). The motion designer retimes with UI.retime(KEY=frame, ...)
# (or edits this table) and everything below - lockups, snake hide/clear windows, NLE scrub / snap - follows.
# Pairs are (first frame, last frame) inclusive; an element is gone from last + 1.
TIMING_SCRIPT = dict(                                    # the text-led plan (SCRIPT.md 2), kept for reference / A-B
    HA_key=16, HA_ul=(24, 44), HA_out=(56, 63),
    HB_key=32, HB_ul=(40, 58), HB_out=(56, 63),
    L5_in=262, L5_key=268, L5_out=(312, 319),
    L6_play=320, L6_galat=328, L6_phir=336, L6_out=(376, 383),
    L7_in=384, L7_out=(414, 419),
    L9_in=448, L9_key=464, L9_out=(504, 511),
    L12=(640, 648, 656, 664), L12_out=(696, 703),
    L14_in=768, L14_key=776, L14_ul=(784, 806), L14_out=(880, 895),
    L15_l1=816, L15_l2=820, L15_out=(880, 895),
    NLE_snap=800, NLE_chip_out=(700, 713),
)
TIMING_VO = dict(                                        # static fallback = VO assemble 2026-10-11 21:26 (stem A)
    HA_key=43,            # V1 'Pencil.' 46.2 - 3 f: the hit lands 0.1 s before the word (SFX f43, VO keeps 8 LU)
    HA_ul=(45, 57),
    HA_out=(62, 69),      # lockup leaves across the f64 cut, gone before L2 'Walkman' f70
    HB_key=32,            # V1B 'khatam?' 32.0
    HB_ul=(36, 52),
    HB_out=(58, 65),
    L5_in=240,            # V3 'Sirf' 240.3
    L5_key=253,           # V3 'andaza.' 253.1
    L5_out=(312, 319),
    L6_play=320,          # V4 'Play.' 320.0 (PLAY key)
    L6_galat=347,         # V4 'Galat!' 347.3 (STOP key)
    L6_phir=376,          # V4 'Phir' 376.1 (REW key + motor)
    L6_out=(391, 394),    # instant swap into 'Mil gaya!' (2nd PLAY + cut to S7 f392)
    L7_in=395,            # V5 'Mil' 395.0
    L7_out=(423, 428),    # 'gaya!' ends 422.3; L8 'Aur' 430.7
    L9_in=448,            # structure: the eat (stays)
    L9_key=464,           # structure: re-hook slam + D7 (stays; V6 'Cassette' 466.6 follows the slam)
    L9_out=(504, 511),
    L12=(648, 656, 664, 672),   # scrub jumps one 8th later (V8 'hain.' ends 642); V9 not in the VO (ladder F4)
    L12_out=(691, 697),   # gone before L13 'Bas' 698.3
    L14_in=768,           # structure: the payoff hit (V11 'Pehla' 777.7 follows it)
    L14_key=832,          # V11 'Pencil.' 832.6 = pencil snaps to the cut (SFX ui_tick f832)
    L14_ul=(835, 855),
    L14_out=(884, 895),
    L15_l1=852,           # V12 'Scrubbing' 852.7
    L15_l2=878,           # V12 'cassette' 878.4
    L15_out=(884, 895),   # leaves with L14 at the D2 razor: the outro badge pops f899 at the tag's height (V12 tail
                          # 'sikhi thi.' f896-f915 plays under the razor without text)
    NLE_snap=832,         # = L14_key
    NLE_chip_out=(704, 716),
)


def derive_vo_timing(words_a=None, words_b=None):
    """TIMING_VO recomputed from the measured VO words (reel time). Rule (VO_TIMING 3): a designed word lands on the
    floor of its VO onset frame (the visual leads by < 1 f); structural beats (f64 splice, f448 / f464 re-hook,
    f576 reveal, f752 drop-out, f768 payoff, f896 razor) never move. Keys whose word is missing keep the static
    value. Re-run after every VO assemble: UI.retime(**UI.derive_vo_timing())."""
    tm = dict(TIMING_VO)
    A = words_a if words_a is not None else (_vo_words('A') or [])
    B = words_b if words_b is not None else (_vo_words('B') or [])

    def w(ws, line, word, which='start'):
        for d in ws:
            if d.get('line') == line and d['word'] == word:
                return float(d[which]) * FPS
        return None

    def last_end(ws, line):
        e = [float(d['end']) * FPS for d in ws if d.get('line') == line]
        return max(e) if e else None
    fl = lambda v: int(math.floor(v + 1e-6))         # noqa: E731
    v = w(A, 'V1', 'Pencil.')
    if v is not None:
        k = fl(v) - 3
        tm.update(HA_key=k, HA_ul=(k + 2, k + 14), HA_out=(max(62, k + 18), max(69, k + 25)))
    v = w(B, 'V1B', 'khatam?')
    if v is not None:
        k = fl(v)
        tm.update(HB_key=k, HB_ul=(k + 4, k + 20), HB_out=(max(58, k + 26), max(65, k + 33)))
    for key, line, word in (('L5_in', 'V3', 'Sirf'), ('L5_key', 'V3', 'andaza.'), ('L6_play', 'V4', 'Play.'),
                            ('L6_galat', 'V4', 'Galat!'), ('L6_phir', 'V4', 'Phir'), ('L7_in', 'V5', 'Mil'),
                            ('L14_key', 'V11', 'Pencil.'), ('L15_l1', 'V12', 'Scrubbing'),
                            ('L15_l2', 'V12', 'cassette')):
        v = w(A, line, word)
        if v is not None:
            tm[key] = fl(v)
    tm['L6_out'] = (tm['L7_in'] - 4, tm['L7_in'] - 1)          # instant swap: Mil gaya! pops as Phir se. leaves
    aur, gend = w(A, 'V5', 'Aur'), w(A, 'V5', 'gaya!', 'end')
    if aur is not None and gend is not None:
        e1 = min(fl(aur) - 2, int(math.ceil(gend)) + 6)
        tm['L7_out'] = (e1 - 5, e1)
    bas = w(A, 'V10', 'Bas')
    if bas is not None:
        tm['L12_out'] = (fl(bas) - 7, fl(bas) - 1)
    k = tm['L14_key']
    tm.update(L14_ul=(k + 3, k + 23), NLE_snap=k)
    tm['L15_out'] = tm['L14_out']                               # the razor + outro badge (f899) end the tag
    return tm


TM = dict(TIMING_VO)                    # the live table; derive_vo_timing() refreshes it from the VO words at import
VO_WORDS = {h: os.path.join(REPO, 'brand_reels', 'assets', SLUG, 'vo_final', 'pencil_se_rewind_vo_%s.words.json' % h)
            for h in ('A', 'B')}


def retime(**kw):
    """Override timing keys (frames) - e.g. UI.retime(HA_key=44, L12=(648, 656, 664, 672)) - and drop the caches
    that depend on them. UI.retime(**UI.TIMING_SCRIPT) restores the text-led plan. Returns the table."""
    bad = [k for k in kw if k not in TIMING_VO]
    if bad:
        raise KeyError('unknown timing keys: %s' % bad)
    TM.update(kw)
    for fn in ('captions', '_snake_words'):
        g = globals().get(fn)
        if g is not None and hasattr(g, 'cache_clear'):
            g.cache_clear()
    return dict(TM)


def tf(key, i=None):
    """A timing value in seconds (i picks an element of a tuple)."""
    v = TM[key]
    return F(v if i is None else v[i])


def ease(name, u):
    return K.EASE[name](min(1.0, max(0.0, u)))


def C(name, k=1.0):
    return np.asarray(K.C[name], np.float32)[:3] * np.float32(k)


def hexl(h, k=1.0):
    return np.asarray(K.hexlin(h), np.float32)[:3] * np.float32(k)


def ro(a):
    a = np.ascontiguousarray(a, np.float32)
    a.setflags(write=False)
    return a


def solid(mask, col):
    m = np.asarray(mask, np.float32)
    c = np.asarray(col, np.float32)
    c = c[:3] if c.ndim == 1 else c[..., :3]               # one colour, or a per-pixel (h, w, 3) colour
    out = np.zeros(m.shape + (4,), np.float32)
    out[..., :3] = m[..., None] * c
    out[..., 3] = m
    return out


def over(dst, src):
    a = src[..., 3:4]
    dst *= (1.0 - a)
    dst += src
    return dst


@functools.lru_cache(maxsize=512)
def tx(s, style, px, fill=None):
    return T.render(s, style, px=px) if fill is None else T.render(s, style, px=px, fill=fill)


def exit_u(t, f0, f1):
    """Exit progress over frames f0..f1 (in_cubic; the element is gone from frame f1 + 1)."""
    return ease('in_cubic', (t - F(f0)) / F(f1 - f0 + 1))


def live(t, f0, f1):
    return F(f0) - HALF <= t < F(f1 + 1) - HALF


# =================================================================================================== type helpers
@functools.lru_cache(maxsize=32)
def key_parts(text, px):
    """Serif keyword split like J.HouseTitle: per-glyph core (Glyphs), static core, wide halo."""
    return T.Glyphs(text, 'jw_key_core', px=px), T.render(text, 'jw_key_core', px=px), T.render(text, 'jw_key_halo', px=px)


@functools.lru_cache(maxsize=32)
def caps_glyphs(text, style, px):
    return T.Glyphs(text, style, px=px), T.render(text, style, px=px)


def slam_scale(tt, s0, dur):
    if tt <= 0:
        return s0
    return s0 + (1.0 - s0) * K.spring(tt / max(dur, 1e-3) * 0.45, 3.2, 0.45)


def key_slam(cv, text, px, t, x, y, t0, op=1.0, s0=1.24, dur=0.30, blur=0.0, flare=0.55):
    """'jw_key' block slam at t0 (word fully on from its hit frame), halo follows the scale, additive hit flare."""
    tt = t - t0
    if tt < -HALF or op <= 1e-4:
        return
    g, st, halo = key_parts(text, px)
    s0 = min(s0, max(1.04, 860.0 / max(1.0, st.w)))      # peak of a wide word stays inside x 70-1010 (ink scan)
    s = slam_scale(max(tt, 0.0), s0, dur)
    halo.draw(cv, x, y, scale=s, opacity=op * min(1.0, 0.55 + tt / 0.35), blur=blur)
    if tt < 0.55:
        g.slam(cv, max(t, t0 + 1e-4), x, y, t0=t0, s0=s0, dur=dur, fade=0, opacity=op)
    else:
        st.draw(cv, x, y, opacity=op, blur=blur)
    if flare > 0 and tt < 0.5:
        halo.draw(cv, x, y, scale=s * 1.04, opacity=op * flare * math.exp(-max(tt, 0) / 0.12), mode='add')


def caps_slam(cv, text, style, px, t, x, y, t0, op=1.0, s0=1.16, dur=0.26, blur=0.0):
    tt = t - t0
    if tt < -HALF or op <= 1e-4:
        return
    g, st = caps_glyphs(text, style, px)
    if tt < 0.5:
        g.slam(cv, max(t, t0 + 1e-4), x, y, t0=t0, s0=s0, dur=dur, fade=0, opacity=op)
    else:
        st.draw(cv, x, y, opacity=op, blur=blur)


def caps_rise(cv, spr, t, x, y, t0, ex=0.0, dur=0.6):
    """House caps rise: opacity inout_sine over 0.7 dur, y +28 -> 0 out_cubic, blur 6 -> 0; exit factor ex."""
    if t < t0 or ex >= 1.0:
        return
    uy = ease('out_cubic', (t - t0) / dur)
    op = ease('inout_sine', (t - t0) / (dur * 0.7)) * (1.0 - ex)
    spr.draw(cv, x, y + 28.0 * (1.0 - uy) - 8.0 * ex, opacity=op, blur=6.0 * (1.0 - uy) + 6.0 * ex)


def underline(cv, length, cx, y, u, op, thick=None):
    if u <= 0 or op <= 1e-4:
        return
    ul = J.underline(int(length), thick=thick or 6.0)
    ul.draw(cv, cx - length / 2.0, y, u=u, opacity=op)


def ul_progress(t, f0, f1):
    return K.ramp(t, F(f0), F(f1), 'inout_cubic')


# =================================================================================================== lockups
def hook_a(cv, t, settled=False):
    """HA f0 -> HA_out: REWIND BUTTON? / Pencil. (slam HA_key; settled=True: the cover state)."""
    o0, o1 = TM['HA_out']
    if not settled and not live(t, 0, o1):
        return
    ex = 0.0 if settled else exit_u(t, o0, o1)
    tt = 3.0 if settled else t
    caps_rise(cv, tx('REWIND BUTTON?', 'jw_caps', 86), tt, 540.0, 400.0, -0.1, ex)
    op = 1.0 - ex
    dy = -8.0 * ex
    if settled:
        g, st, halo = key_parts('Pencil.', 250)
        halo.draw(cv, 540.0, 580.0)
        st.draw(cv, 540.0, 580.0)
    else:
        key_slam(cv, 'Pencil.', 250, t, 540.0, 580.0 + dy, tf('HA_key'), op=op, blur=6.0 * ex)
    underline(cv, 640, 540.0, 700.0 + dy, 1.0 if settled else ul_progress(t, *TM['HA_ul']), op)


def hook_b(cv, t):
    """HB (trial reel): BATTERY / khatam? (slam HB_key)."""
    o0, o1 = TM['HB_out']
    if not live(t, 0, o1):
        return
    ex = exit_u(t, o0, o1)
    caps_rise(cv, tx('BATTERY', 'jw_caps', 96), t, 540.0, 400.0, -0.1, ex)
    dy = -8.0 * ex
    key_slam(cv, 'khatam?', 240, t, 540.0, 580.0 + dy, tf('HB_key'), op=1.0 - ex, blur=6.0 * ex)
    underline(cv, 800, 540.0, 690.0 + dy, ul_progress(t, *TM['HB_ul']), 1.0 - ex)


@functools.lru_cache(maxsize=4)
def house(caps, key, caps_px, key_px):
    return J.HouseTitle(caps, key, caps_px=caps_px, key_px=key_px, underline=False)


def sirf_andaza(cv, t):
    """L5: SIRF (caps rise L5_in) / andaza. (per-glyph rise L5_key)."""
    o0, o1 = TM['L5_out']
    if not live(t, TM['L5_in'], o1):
        return
    ex = exit_u(t, o0, o1)
    house('SIRF', 'andaza.', 96, 220).draw(cv, t, 540.0, 590.0 - 8.0 * ex, t0=tf('L5_in'),
                                           key_t=tf('L5_key') - tf('L5_in'), opacity=1.0 - ex)


def galat_stack(cv, t):
    """L6: Play. / Galat! / Phir se. on the VO; Galat! shakes 'no' and strikes through Play."""
    f_play, f_gal, f_phir = TM['L6_play'], TM['L6_galat'], TM['L6_phir']
    o0, o1 = TM['L6_out']
    if not live(t, f_play, o1):
        return
    ex = exit_u(t, o0, o1)
    op = 1.0 - ex
    dy = -8.0 * ex
    bl = 6.0 * ex
    strike = K.ramp(t, F(f_gal + 1), F(f_gal + 5), 'out_cubic')
    caps_slam(cv, 'Play.', 'jw_caps_bold', 150, t, 540.0, 420.0 + dy, F(f_play), op=op * (1.0 - 0.45 * strike), blur=bl)
    if strike > 0:
        w = T.measure('Play.', 'jw_caps_bold', px=150)[0]
        underline(cv, w + 50, 540.0, 420.0 + dy + 4.0, strike, op, thick=7.0)
    if t >= F(f_gal) - HALF:
        tt = t - F(f_gal)
        shake = 14.0 * math.sin(2 * math.pi * 7.0 * max(tt, 0)) * math.exp(-max(tt, 0) * 9.0) if tt > 0.06 else 0.0
        key_slam(cv, 'Galat!', 200, t, 540.0 + shake, 590.0 + dy, F(f_gal), op=op, blur=bl)
    if t >= F(f_phir) - HALF:
        caps_slam(cv, 'Phir se.', 'jw_caps_bold', 150, t, 540.0, 760.0 + dy, F(f_phir), op=op, blur=bl)


def mil_gaya(cv, t):
    """L7: Mil gaya! SLAM L7_in."""
    o0, o1 = TM['L7_out']
    if not live(t, TM['L7_in'], o1):
        return
    ex = exit_u(t, o0, o1)
    key_slam(cv, 'Mil gaya!', 220, t, 540.0, 520.0 - 8.0 * ex, tf('L7_in'), op=1.0 - ex, blur=6.0 * ex, flare=0.7)


def shock(t, t0=None, amp=6.0, decay=10.0):
    """D7 frame shock at the re-hook (SHOTS S8: 6 px, decay 10) -> (dx, dy)."""
    t0 = tf('L9_key') if t0 is None else t0
    if t < t0:
        return 0.0, 0.0
    sx, sy, _ = K.shake(t, amp, 18.0, seed=464)
    k = math.exp(-(t - t0) * decay)
    return sx * k, sy * k


@functools.lru_cache(maxsize=1)
def _phans_box():
    g, st, halo = key_parts('phans gayi!', 190)
    pad = 150
    w, h = int(st.w + 2 * pad), int(st.h + 2 * pad)
    return w, h, pad


def phans_gayi(cv, t):
    """L9: CASSETTE rises L9_in / phans gayi! SLAM L9_key + D7 shock + tape warble."""
    o0, o1 = TM['L9_out']
    if not live(t, TM['L9_in'], o1):
        return
    ex = exit_u(t, o0, o1)
    sx, sy = shock(t)
    caps_rise(cv, tx('CASSETTE', 'jw_caps', 96), t, 540.0 + sx, 400.0 + sy, tf('L9_in'), ex)
    t_key = tf('L9_key')
    if t < t_key - HALF:
        return
    tt = t - t_key
    amp = 10.0 * math.exp(-max(tt, 0) / 0.22) if tt < 0.62 else 0.0
    op = 1.0 - ex
    x, y = 540.0 + sx, 570.0 + sy - 8.0 * ex
    if amp < 0.4:
        key_slam(cv, 'phans gayi!', 190, t, x, y, t_key, op=op, blur=6.0 * ex, flare=0.7)
        return
    # draw into a local layer, then sway the rows like a stretched tape (warble)
    w, h, pad = _phans_box()
    lay = np.zeros((h, w, 4), np.float32)
    key_slam(lay, 'phans gayi!', 190, t, w / 2.0, h / 2.0, t_key, op=1.0, flare=0.7)
    ys = np.arange(h, dtype=np.float32)
    dx = amp * np.sin(ys / 23.0 + tt * 38.0) * (0.6 + 0.4 * np.sin(ys / 61.0 - tt * 17.0))
    mx = np.tile(np.arange(w, dtype=np.float32)[None, :], (h, 1)) - dx[:, None]
    my = np.tile(ys[:, None], (1, w))
    lay = cv2.remap(lay, mx, my, cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT, borderValue=0)
    K.draw(cv, lay, x, y, opacity=op)


L12_TEXT = (('Peeche.', -1), ('Aage.', +1), ('Peeche.', -1), ('Yahan.', 0))


def yahan(cv, t):
    """L12: Peeche. / Aage. / Peeche. / Yahan. replace each other on the scrub jumps at (540, 330)."""
    fr = TM['L12']
    o0, o1 = TM['L12_out']
    if not live(t, fr[0], o1):
        return
    x0, y0 = 540.0, 344.0                            # 330 + 14: the Yahan. slam peak keeps y >= 230
    for i, ((word, d), f0) in enumerate(zip(L12_TEXT, fr)):
        t0 = F(f0)
        nxt = F(fr[i + 1]) if i + 1 < len(fr) else None
        if t < t0 - HALF:
            continue
        if nxt is not None and t >= nxt - HALF:      # instant swap: the next word's slam is the transition
            continue
        if d == 0:                                   # Yahan.
            ex = exit_u(t, o0, o1)
            key_slam(cv, word, 220, t, x0, y0 - 8.0 * ex, t0, op=1.0 - ex, blur=6.0 * ex, flare=0.7)
            continue
        # travel: comes in moving the playhead's way (Peeche = leftwards, d=-1), leaves further along it
        uin = ease('out_expo', (t - t0) / F(4))
        dx = -d * 70.0 * (1.0 - uin)
        op = 1.0
        bl = 5.0 * (1.0 - uin)
        g, st = caps_glyphs(word, 'jw_caps_bold', 140)
        s = slam_scale(max(t - t0, 0.0), 1.12, 0.22)
        st.draw(cv, x0 + dx, y0, scale=s, opacity=op, blur=bl)


PAY_Y = 520.0          # L14 key centre (SHOTS: 560); caps at PAY_Y - 200, underline PAY_Y + 140, tag PAY_Y + 208 / + 280


def payoff(cv, t):
    """L14 (HouseTitle: caps L14_in, key rise L14_key, underline L14_ul at y 700) and the L15 tag."""
    o0, o1 = TM['L14_out']
    q0, q1 = TM['L15_out']
    if not live(t, TM['L14_in'], max(o1, q1)):
        return
    if live(t, TM['L14_in'], o1):
        ex = exit_u(t, o0, o1)
        op = 1.0 - ex
        dy = -8.0 * ex
        ht = house('PEHLA EDITING TOOL?', 'Pencil.', 74, 260)
        ht.draw(cv, t, 540.0, PAY_Y + dy, t0=tf('L14_in'), key_t=tf('L14_key') - tf('L14_in'), opacity=op)
        underline(cv, 720, 540.0, PAY_Y + 140.0 + dy, ul_progress(t, *TM['L14_ul']), op, thick=7.0)
    if live(t, TM['L15_l1'], q1):
        ex = exit_u(t, q0, q1)
        tag(cv, t, 1.0 - ex, -8.0 * ex)


@functools.lru_cache(maxsize=1)
def _tag_line2():
    k = tx('cassette', 'jw_key_core', 96)
    kh = tx('cassette', 'jw_key_halo', 96)
    b = tx(' pe sikhi thi.', 'jw_body', 56)
    return k, kh, b


def tag(cv, t, op=1.0, dy=0.0):
    """L15: 'Scrubbing toh' (L15_l1) / 'cassette pe sikhi thi.' (L15_l2; keyword inline, shared baseline)."""
    l1 = tx('Scrubbing toh', 'jw_body', 56)
    for i, (t0, y) in enumerate(((tf('L15_l1'), PAY_Y + 208.0), (tf('L15_l2'), PAY_Y + 280.0))):
        if t < t0:
            continue
        a = ease('inout_sine', (t - t0) / 0.45) * op
        yy = y + 22.0 * (1.0 - ease('out_cubic', (t - t0) / 0.5)) + dy
        bl = 6.0 * (1.0 - ease('out_cubic', (t - t0) / 0.5))
        if i == 0:
            l1.draw(cv, 540.0, yy, opacity=a, blur=bl)
            continue
        k, kh, b = _tag_line2()
        gap = 0.30 * 56                             # a word space between the serif keyword and ' pe'
        wtot = k.w + gap + b.w
        x0 = 540.0 - wtot / 2.0
        base = yy + b.h / 2.0                       # shared baseline (text boxes are cap-height boxes)
        kh.draw(cv, x0, base, anchor=(0.0, 1.0), opacity=a * 0.9, blur=bl)
        k.draw(cv, x0, base, anchor=(0.0, 1.0), opacity=a, blur=bl)
        b.draw(cv, x0 + k.w + gap, base, anchor=(0.0, 1.0), opacity=a, blur=bl)


def lockup_windows(hook='A'):
    """Lockup windows (first, last frame) at the current timing - hidden from the snake track, QA's 2-block rule."""
    hk = 'HB' if str(hook).upper() == 'B' else 'HA'
    return {hk: (0, TM[hk + '_out'][1]), 'L5': (TM['L5_in'], TM['L5_out'][1]),
            'L6': (TM['L6_play'], TM['L6_out'][1]), 'L7': (TM['L7_in'], TM['L7_out'][1]),
            'L9': (TM['L9_in'], TM['L9_out'][1]), 'L12': (TM['L12'][0], TM['L12_out'][1]),
            'L14': (TM['L14_in'], TM['L14_out'][1]), 'L15': (TM['L15_l1'], TM['L15_out'][1])}


def lockups(cv, t, hook='A'):
    """Every designed caption lockup active at t (pure in t)."""
    if str(hook).upper() == 'B':
        hook_b(cv, t)
    else:
        hook_a(cv, t)
    sirf_andaza(cv, t)
    galat_stack(cv, t)
    mil_gaya(cv, t)
    phans_gayi(cv, t)
    yahan(cv, t)
    payoff(cv, t)
    return cv


# =================================================================================================== snake captions
# VO-led: the snake words ARE the measured VO words (vo_final/pencil_se_rewind_vo_<hook>.words.json, reel time), so
# every word lands on its voiced onset. Lines the lockups / the outro already show (V1, V1B, 'Sirf andaza.', V4,
# 'Mil gaya!', V6, V11, V12, V13) are never snake text (two-layer rule). (snake id, VO line, word slice, band)
SNAKE_LINES = (('L2', 'V2', 0, 5, 'upper'), ('L3', 'V2', 5, 10, 'upper'), ('L4', 'V3', 0, 3, 'lower'),
               ('L8', 'V5', 2, 4, 'upper'), ('L10', 'V7', 0, 6, 'upper'), ('L11', 'V8', 0, 5, 'top'),
               ('L13', 'V10', 0, 4, 'top'))
BANDS = {'upper': ('upper', 410.0, 28.0), 'lower': ('lower', 1380.0, 28.0), 'top': ('upper', 330.0, 14.0)}
SNAKE_KEY = {'L2': 'battery', 'L3': 'ghumate', 'L4': 'Gaana', 'L8': None, 'L10': 'pencil', 'L11': 'wahi',
             'L13': 'badal'}                                       # SCRIPT.md keywords (one per line)
SNAKE_PX = (64, 128)
SNAKE_BREAK_AFTER = {('L4', 'Gaana'), ('L10', 'se')}                            # split instead of shrinking (lower band is 820 px)
DROPOUT = (752, 767)
BAND_CUTS = {'upper': (192,)}                                      # upper text leaves by the S3 -> S4 cut (L4 is low)
LEAD, HOLD = 0.05, 0.35


def avoid_at(t):
    """SHOTS C avoid rects per shot (x0, y0, x1, y1)."""
    f = t * FPS
    if 64 <= f < 128:
        return [(190, 900, 900, 1560)]                              # S2 walkman
    if 128 <= f < 192 or 512 <= f < 576:
        return [(300, 700, 860, 1500)]                              # S3 / S9 hub + pencil
    if 192 <= f < 256:
        return [(100, 520, 980, 1260)]                              # S4 label
    if 576 <= f < 768:
        return [(250, 470, 830, 1205), (70, 1260, 1010, 1470)]      # S10-S12 viewer + timeline
    return []


@functools.lru_cache(maxsize=1)
def script():
    with open(SCRIPT_JSON, encoding='utf8') as fh:
        return json.load(fh)


def _vo_words(hook):
    p = VO_WORDS['B' if str(hook).upper() == 'B' else 'A']
    alt = os.path.join(RWS, 'vo', 'words%s.json' % ('_B' if str(hook).upper() == 'B' else ''))
    for q in (alt, p):                                              # workspace stem (latest assemble) first
        if os.path.exists(q):
            with open(q, encoding='utf8') as fh:
                d = json.load(fh)
            return d['words'] if isinstance(d, dict) else d
    return None


def line_words(line_id, wpx=SNAKE_PX[0], kpx=SNAKE_PX[1]):
    """Fallback (no VO words on disk): script.json tokens, re-paced inside the text-led line window."""
    d = script()
    L = [l for l in d['lines'] if l['id'] == line_id][0]
    toks = [tk for tk in d['tokens'] if tk['line'] == line_id]
    f_in, f_out = L['in_f'], L['out_f']
    base = [dict(word=tk['roman'], start=tk['onset_f'] / FPS, end=(tk['end_f'] + 1) / FPS, keyword=tk['keyword'],
                 token=tk['roman']) for tk in toks]
    chunks = SC.chunk_words(SC.load_words(base), 3, 0.45, 1010 - 70 - 40, float(wpx), float(kpx))
    sizes = [len(c) for c in chunks]
    n, span, k, starts = sum(sizes), f_out + 1 - f_in, 0, []
    for sz in sizes:
        starts.append(f_in + int(round(span * k / n)))
        k += sz
    out, tok_i = [], 0
    for j, sz in enumerate(sizes):
        nxt = starts[j + 1] if j + 1 < len(sizes) else None
        for q in range(sz):
            tk = toks[tok_i]
            tok_i += 1
            st = (starts[j] + 4 * q) / FPS
            en = st + 4 / FPS if q < sz - 1 else (nxt / FPS if nxt is not None
                                                  else max(st + 0.1, (f_out + 1) / FPS - 0.65))
            out.append(dict(word=tk['roman'], start=st, end=en, keyword=tk['keyword'], token=tk['roman']))
    return out


@functools.lru_cache(maxsize=2)
def _snake_words(hook='A'):
    """{snake id: [word dicts]} in reel time (VO words, keywords per SCRIPT.md; fallback: script.json)."""
    vo = _vo_words(hook)
    out = {}
    for lid, vline, a, b, band in SNAKE_LINES:
        if vo is None:
            out[lid] = line_words(lid)
            continue
        ws = [w for w in vo if w.get('line') == vline]
        ws = sorted(ws, key=lambda w: w.get('i', 0))[a:b]
        out[lid] = [dict(word=w['word'], start=float(w['start']), end=float(w['end']),
                         token=w['word'] + (',' if (lid, w['word']) in SNAKE_BREAK_AFTER else ''),
                         keyword=bool(SNAKE_KEY[lid]) and w['word'].strip('.,?!').lower() == SNAKE_KEY[lid].lower())
                    for w in ws]
    return out


def _span(ws):
    """Time a line blocks the OTHER bands: from its first word's lead-in to just after its last word (the next line
    wins over this line's hold, so a new VO line is never delayed by the previous caption)."""
    return ws[0]['start'] - LEAD, ws[-1]['end'] + 0.10


class Snake:
    """The reel's snake-caption track: one SC.Captions per band. Each band clears for the lockups, the drop-out,
    the other bands' lines and its cuts, so there is never more than one caption block from this track and never a
    snake line under a lockup."""

    def __init__(self, hook='A'):
        words = _snake_words(hook)
        lock = [(F(a) - 0.02, F(b + 1)) for a, b in lockup_windows(hook).values()]
        self.parts = []
        for band in ('upper', 'lower', 'top'):
            lids = [l[0] for l in SNAKE_LINES if l[4] == band]
            ws = [w for lid in lids for w in words[lid]]
            if not ws:
                continue
            other = [_span(words[l[0]]) for l in SNAKE_LINES if l[4] != band and words[l[0]]]
            clear = lock + other + [(F(DROPOUT[0]), F(DROPOUT[1] + 1))] + \
                [(F(c), F(c) + 0.02) for c in BAND_CUTS.get(band, ())]
            sc_band, y, margin = BANDS[band]
            self.parts.append(SC.Captions(ws, band=sc_band, y=y, avoid=avoid_at, white_px=SNAKE_PX[0],
                                          key_px=SNAKE_PX[1], margin=margin, clear=sorted(clear), lead=LEAD,
                                          hold=HOLD))

    @property
    def chunks(self):
        return sorted([c for p in self.parts for c in p.chunks], key=lambda c: c.t_in)

    def draw(self, cv, t, opacity=1.0):
        for p in self.parts:
            p.draw(cv, t, opacity)
        return cv

    def prewarm(self):
        for p in self.parts:
            p.prewarm()

    def report(self):
        return sorted([r for p in self.parts for r in p.report()], key=lambda r: r['t_in'])

    def check(self):
        return [i for p in self.parts for i in p.check()]

    def save_srt(self, path):
        def ts(x):
            ms = int(round(max(0.0, x) * 1000))
            return '%02d:%02d:%02d,%03d' % (ms // 3600000, ms // 60000 % 60, ms // 1000 % 60, ms % 1000)
        with open(path, 'w', encoding='utf8') as f:
            for i, ch in enumerate(self.chunks, 1):
                f.write('%d\n%s --> %s\n%s\n\n' % (i, ts(ch.t_in), ts(ch.t_exit1), ch.text))
        return path


@functools.lru_cache(maxsize=2)
def captions(hook='A'):
    return Snake(hook)


# =================================================================================================== outro + cover
@functools.lru_cache(maxsize=1)
def outro():
    return PO.ProfileOutro(OUTRO_Q, key=OUTRO_KEY, dur=OUTRO_DUR)


GRID_Y = (240, 1680)                                # 3:4 grid crop (1080 x 1440)


def cover(cv):
    """Cover overlay: the HA lockup at full opacity with the underline settled (over the hub_cover still)."""
    hook_a(cv, 0.0, settled=True)
    return cv


def grid_crop(img):
    return img[GRID_Y[0]:GRID_Y[1]]


# =================================================================================================== 3D assets / stand-ins
PREVIEW_ROOT = os.path.join(RWS, 'out', 'preview3d')
# final render size (ASSETS.md) and the preview frames that match the final framing (hub_loop 0001 is an older camera)
PREVIEW_SPEC = dict(hub_loop=((1080, 1920), (0,)), hub_cover=((1080, 1920), (0,)), hub_rescue=((810, 1440), None),
                    label=((1080, 1920), None), walkman_loop=((1080, 1920), None), walkman_eat=((810, 1440), None),
                    pencil_top=((600, 1700), None))
PREVIEW_FEATURES = dict(pencil_top={'eraser_top': (300.0, 100.0), 'tip': (300.0, 1600.0)})


class _Preview:
    """Blender preview renders (assets3d ... --preview, low spp / res) upscaled to the final asset size: the fallback
    while the GPU finals are not on this machine (selftest / layout only, never a delivery). Same API subset as
    S3.Asset3D: n, frame(i), by_label(lab), features, preview=True."""
    preview = True

    def __init__(self, name):
        size, keep = PREVIEW_SPEC[name]
        src = 'hub_loop' if name == 'hub_cover' else name
        d = os.path.join(PREVIEW_ROOT, src, 'passes')
        fs = sorted(f for f in os.listdir(d) if f.endswith('.png') and f[:-4].isdigit())
        if keep is not None:
            fs = [f for f in fs if int(f[:-4]) in keep]
        if not fs:
            raise FileNotFoundError(d)
        self.idx = [int(f[:-4]) for f in fs]
        self.paths = [os.path.join(d, f) for f in fs]
        self.size = size
        self.n = max(self.idx) + 1
        self.features = dict(PREVIEW_FEATURES.get(name, {}))
        self._c = {}

    def frame(self, i):
        j = int(np.argmin(np.abs(np.asarray(self.idx) - int(i) % max(1, self.n))))
        if j not in self._c:
            im = S3.decode_png(self.paths[j])
            self._c[j] = ro(cv2.resize(np.ascontiguousarray(im), self.size, interpolation=cv2.INTER_CUBIC))
        return self._c[j]

    def by_label(self, lab):
        return self.frame({'key': 0, 'shadow': 1}.get(lab, 0))


@functools.lru_cache(maxsize=16)
def _asset(name):
    """Final Blender render (RWS/assets3d/<name>, meta.json present), else its preview render, else None."""
    if os.path.exists(os.path.join(RWS, 'assets3d', name, 'passes', 'meta.json')):
        try:
            return S3.Asset3D(name, 'passes', root=os.path.join(RWS, 'assets3d'))
        except Exception:
            pass
    try:
        return _Preview(name)
    except Exception:
        return None


@functools.lru_cache(maxsize=1)
def hub_asset():
    return _asset('hub_loop')


def media_r1(src_t):
    """Default viewer media: R1 hub_loop frame for source time src_t (idx = floor(30 src_t) mod 16); stand-in
    when the Blender render is not there yet."""
    idx = int(math.floor(src_t * FPS + 1e-6)) % 16
    a = hub_asset()
    if a is not None:
        return a.frame(idx)
    return standin_hub(idx)


@functools.lru_cache(maxsize=1)
def _desk():
    """Stand-in desk + wall (only when the Blender plates are missing): warm wood, lamp pool, falloff."""
    h, w = K.H, K.W
    rng = np.random.default_rng(11)
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    hor = 760.0
    v = np.clip((yy - hor) / (h - hor), 0, 1)
    z = 1.0 / (0.12 + v)                                       # depth for the grain perspective
    gx = (xx - 540.0) / (0.4 + v * 2.2)
    wn = cv2.resize(rng.standard_normal((40, 24)).astype(np.float32), (w, h), interpolation=cv2.INTER_CUBIC)
    grain = 0.5 + 0.5 * np.sin(z * 9.0 + 0.004 * gx + 1.8 * wn)
    fib = cv2.resize(rng.standard_normal((h // 6, w // 30)).astype(np.float32), (w, h), interpolation=cv2.INTER_LINEAR)
    wood = hexl('#4A2A18')[None, None, :] * (0.62 + 0.38 * grain[..., None] + 0.06 * fib[..., None])
    wall = hexl('#2A1C14', 0.45)[None, None, :] * np.ones((h, w, 1), np.float32)
    m = np.clip((yy - hor + 30) / 60.0, 0, 1)[..., None]
    rgb = wall * (1 - m) + wood * m
    pool = np.exp(-(((xx - 520) / 560.0) ** 2 + ((yy - 1230) / 470.0) ** 2))
    lamp = hexl('#FFB46B')
    rgb = rgb * (0.10 + 1.25 * pool[..., None] * lamp[None, None, :] / lamp.max())
    rim = np.exp(-(((xx - 1000) / 260.0) ** 2 + ((yy - 900) / 360.0) ** 2)) * 0.10
    rgb += rim[..., None] * C('FLAME')
    return ro(rgb)


@functools.lru_cache(maxsize=1)
def _cassette_tex():
    """Cassette face texture (1004 x 638 px = 10 px / mm) without the hubs: shell, label, window, screws."""
    Wt, Ht = 1004, 638
    S = ui.Surf(Wt, Ht)
    shell = hexl('#3A2618', 1.1)
    S.rrect(0, 0, Wt, Ht, 36, shell)
    S.stroke_rrect(0, 0, Wt, Ht, 36, 3, hexl('#6B4A33'))
    S.rrect(60, 46, 884, 400, 18, hexl('#EDE3CF', 0.82))                     # label
    for i in range(6):                                                        # ruled lines
        S.rrect(90, 92 + i * 30, 824, 2, 1, hexl('#E7A27A', 0.55))
    S.rrect(232, 236, 540, 138, 20, hexl('#0E0806'))                          # window
    S.stroke_rrect(232, 236, 540, 138, 20, 2, hexl('#7A5A40'))
    for cx in (290, 714):
        S.circle(cx, 305, 66, hexl('#120A06'))
    S.rrect(200, 470, 604, 150, 22, hexl('#2A1A10'))                          # head area
    for (sx, sy) in ((40, 40), (964, 40), (40, 598), (964, 598), (502, 560)):
        S.circle(sx, sy, 13, hexl('#8A857E'))
        S.rrect(sx - 9, sy - 1.5, 18, 3, 1, hexl('#2A2622'))
    img = np.array(S.img, copy=True)
    # handwriting: Mix '98 . Side A + scribbled track lines (blue ballpoint)
    ink = np.zeros((Ht, Wt), np.uint8)
    cv2.putText(ink, "Mix '98", (110, 160), cv2.FONT_HERSHEY_SCRIPT_SIMPLEX, 2.3, 255, 4, cv2.LINE_AA)
    cv2.putText(ink, 'Side A', (640, 160), cv2.FONT_HERSHEY_SCRIPT_SIMPLEX, 1.6, 255, 3, cv2.LINE_AA)
    rng = np.random.default_rng(3)
    for i in range(3):
        y = 212 + i * 30
        if y > 226:
            continue
        x = 110.0
        pts = []
        while x < 860:
            pts.append([x, y + rng.uniform(-6, 6)])
            x += rng.uniform(10, 22)
        cv2.polylines(ink, [np.int32(pts)], False, 200, 2, cv2.LINE_AA)
    a = ink.astype(np.float32) / 255.0
    img[..., :3] = img[..., :3] * (1 - a[..., None] * 0.9) + a[..., None] * hexl('#26306E')
    return ro(img)


QUAD = np.float32([[270, 1010], [1290, 900], [1400, 1430], [210, 1640]])


def _hub_tex(idx, r_out=46.0, r_in=22.0):
    """White POM hub with 6 drive teeth, rotated by idx * 22.5 deg (clockwise)."""
    n = 140
    yy, xx = np.mgrid[0:n, 0:n].astype(np.float32) - n / 2 + 0.5
    rr = np.sqrt(xx * xx + yy * yy)
    th = np.arctan2(yy, xx) - math.radians(22.5 * idx)
    ring = np.clip(r_out - rr + 0.5, 0, 1) * np.clip(rr - r_in + 0.5, 0, 1)
    teeth = (np.cos(6 * th) > 0.55).astype(np.float32) * np.clip(r_in + 9 - rr, 0, 1) * np.clip(rr - r_in + 9, 0, 1)
    m = np.clip(ring + teeth * (rr < r_in + 1), 0, 1)
    shade = 0.75 + 0.25 * np.clip(-(xx + yy) / (r_out * 1.4), -1, 1)
    out = np.zeros((n, n, 4), np.float32)
    out[..., :3] = (m * shade)[..., None] * hexl('#E9E4DA', 0.9)
    out[..., 3] = m
    # tape pack (oxide) around the hub
    pack = np.clip(66 - rr, 0, 1) * np.clip(rr - r_out + 1, 0, 1)
    band = 0.85 + 0.15 * np.sin(rr * 1.7)
    pk = solid(pack, hexl('#2B1A10') * band[..., None])
    return over(pk, out)


@functools.lru_cache(maxsize=16)
def standin_hub(idx):
    """Stand-in for R1 hub_loop (selftest / fallback only): desk, cassette in perspective, hubs turning, pencil
    upright in the left hub. The reel uses the Blender render (assets3d hub_loop) whenever it exists."""
    idx = int(idx) % 16
    cv = np.zeros((K.H, K.W, 4), np.float32)
    cv[..., :3] = _desk()
    cv[..., 3] = 1.0
    tex = np.array(_cassette_tex(), copy=True)
    for k, cx in enumerate((290, 714)):
        h = _hub_tex(idx)
        x0, y0 = cx - 70, 305 - 70
        reg = tex[y0:y0 + 140, x0:x0 + 140]
        over(reg, h)
    Mp = cv2.getPerspectiveTransform(np.float32([[0, 0], [1004, 0], [1004, 638], [0, 638]]), QUAD)
    warped = cv2.warpPerspective(tex, Mp, (K.W, K.H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT)
    # shadow of the shell
    sh = cv2.GaussianBlur(warped[..., 3], (0, 0), 18.0)
    sh = np.roll(np.roll(sh, 22, axis=0), 16, axis=1) * 0.7
    cv[..., :3] *= (1 - sh[..., None])
    lit = np.exp(-(((np.arange(K.W)[None, :] - 520) / 700.0) ** 2 + ((np.arange(K.H)[:, None] - 1220) / 520.0) ** 2))
    warped[..., :3] *= (0.35 + 1.1 * lit)[..., None]
    over(cv, warped)
    # pencil upright in the left hub
    hub = Mp @ np.float32([290, 305, 1])
    hx, hy = float(hub[0] / hub[2]), float(hub[1] / hub[2])
    key, shadow, top, tip = pencil_sprites()
    s = 0.55
    vis = (hy - 600.0) / s                                       # sprite rows from the eraser top to the hub
    y_top = top[1]
    crop = np.array(key[: int(y_top + vis)], copy=True)
    shc = np.array(shadow[: int(y_top + vis)], copy=True)
    K.draw(cv, ro(shc), hx + 40, hy + 10, scale=(s, s * 0.55), rot=-62, anchor=(0.5, 1.0), opacity=0.45)
    K.draw(cv, ro(crop), hx, hy + 6, scale=s, anchor=(top[0] / key.shape[1], 1.0))
    # depth of field: soften away from the hub / pencil plane
    yy, xx = np.mgrid[0:K.H, 0:K.W].astype(np.float32)
    d = np.clip((np.abs(xx - hx) - 220) / 380.0, 0, 1) * 0.8 + np.clip((yy - 1500) / 300.0, 0, 1) * 0.6
    d = np.clip(d + np.clip((900 - yy) / 400.0, 0, 1) * 0.5 * (np.abs(xx - hx) > 60), 0, 1)
    bl = cv2.GaussianBlur(cv, (0, 0), 9.0)
    cv = cv * (1 - d[..., None]) + bl * d[..., None]
    cv[..., 3] = 1.0
    return ro(cv)


# --------------------------------------------------------------------------------------------------- pencil
PEN_W, PEN_L, PEN_PAD = 84, 1500, 10
PEN_Y = dict(eraser=60, ferrule=168, body=1344, wood=1464, tip=1500)


@functools.lru_cache(maxsize=1)
def pencil_procedural():
    """Top-down hex pencil, eraser up (R5 'pencil_top' stand-in): chrome-yellow lacquer with chipped arrises, cedar
    cone with blade facets and grain, blunted graphite, brushed-aluminium ferrule with crimp grooves, pink eraser
    worn at an angle with a graphite smudge, 4 tooth dents, rubbed gold 'HB'. 84 x 1500 px body (12 px / mm).
    Returns (sprite, shadow, eraser_top_xy, tip_xy) in sprite px."""
    P = PEN_PAD
    Wd, Hd = PEN_W + 2 * P + 8, PEN_L + 2 * P
    rng = np.random.default_rng(42)
    yy, xx = np.mgrid[0:Hd, 0:Wd].astype(np.float32) + 0.5
    cx = Wd / 2.0
    y = yy - P
    u = (xx - (cx - PEN_W / 2.0)) / PEN_W                     # 0..1 across the body
    ye, yf, yb, yw, yt = (PEN_Y[k] for k in ('eraser', 'ferrule', 'body', 'wood', 'tip'))
    # half width profile
    hw = np.full_like(y, PEN_W / 2.0)
    hw = np.where((y >= ye) & (y < yf), PEN_W / 2.0 + 2.0, hw)
    cone = (y >= yb)
    uc = np.clip((y - yb) / (yt - yb), 0, 1)
    hw_c = PEN_W / 2.0 * (1 - uc) ** 0.92 + 1.2
    hw = np.where(cone, hw_c, hw)
    tipr = np.clip((y - (yt - 6)) / 6.0, 0, 1)
    hw = np.where(cone, hw * (1 - 0.6 * tipr ** 2), hw)
    top_y = 4.0 + 14.0 * np.clip(u, 0, 1)                      # eraser worn at an angle
    a = np.clip(hw - np.abs(xx - cx) + 0.5, 0, 1) * np.clip(y - top_y + 0.5, 0, 1) * np.clip(yt - y + 0.5, 0, 1)
    rgb = np.zeros((Hd, Wd, 3), np.float32)
    uu = np.clip((xx - (cx - hw)) / np.maximum(2 * hw, 1e-3), 0, 1)   # across the local width
    # ---------------- lacquer body (hex: faces 0-.25 / .25-.75 / .75-1)
    face = np.where(uu < 0.25, 0, np.where(uu < 0.75, 1, 2))
    fk = np.choose(face, [0.74, 1.0, 0.40]).astype(np.float32)
    fk = fk * (1.0 + 0.10 * (0.5 - np.abs(((uu % 0.5) / 0.5) - 0.5)))
    peel = cv2.resize(rng.standard_normal((Hd // 18, Wd // 6)).astype(np.float32), (Wd, Hd), interpolation=cv2.INTER_CUBIC)
    lac = hexl('#E3A21A')[None, None, :] * (fk * (1 + 0.025 * peel))[..., None]
    spec = np.exp(-((uu - 0.36) / 0.022) ** 2) * 0.85 + np.exp(-((uu - 0.46) / 0.11) ** 2) * 0.16 \
        + np.exp(-((uu - 0.11) / 0.05) ** 2) * 0.10
    lac = lac + spec[..., None] * hexl('#FFF1D8')[None, None, :]
    rim = np.exp(-((uu - 0.975) / 0.022) ** 2) * 0.75
    lac = lac + rim[..., None] * C('FLAME')
    ar = np.exp(-((uu - 0.25) / 0.012) ** 2) + np.exp(-((uu - 0.75) / 0.012) ** 2)
    lac = lac * (1 - 0.35 * ar[..., None]) + (np.exp(-((uu - 0.237) / 0.008) ** 2) * 0.35)[..., None] * hexl('#FFF1D8')
    # chips on the arrises (cedar shows) + dents near the ferrule
    chips = np.zeros((Hd, Wd), np.float32)
    for k in range(34):
        cy_ = rng.uniform(yf + 30, yb - 20) + P
        cxu = rng.choice([0.25, 0.75]) + rng.uniform(-0.01, 0.01)
        rx, ry = rng.uniform(1.6, 3.4), rng.uniform(2.5, 11.0)
        cx_ = cx - PEN_W / 2 + cxu * PEN_W
        chips = np.maximum(chips, np.clip(1.0 - (((xx - cx_) / rx) ** 2 + ((yy - cy_) / ry) ** 2), 0, 1) ** 0.4)
    lac = lac * (1 - chips[..., None]) + chips[..., None] * hexl('#C4915E', 0.8)
    for (du, dy_) in ((0.42, 214), (0.58, 226), (0.33, 241), (0.52, 252)):
        cx_ = cx - PEN_W / 2 + du * PEN_W
        cy_ = dy_ + P
        d = ((xx - cx_) / 7.0) ** 2 + ((yy - cy_) / 3.2) ** 2
        dent = np.clip(1 - d, 0, 1)
        lac *= (1 - 0.28 * dent[..., None] * (yy < cy_)[..., None])
        lac += (0.22 * dent * (yy >= cy_))[..., None] * hexl('#FFF1D8')
    # gold foil 'HB' (rubbed)
    hb = ui.text('HB', 34, 'ui_bold', color=(1, 1, 1))
    m = np.rot90(hb.spr[..., 3], 1)
    mh, mw = m.shape
    ox, oy = int(cx - mw / 2), int(P + 330)
    rub = (cv2.resize(rng.random((mh // 3 + 1, mw // 3 + 1)).astype(np.float32), (mw, mh)) > 0.42).astype(np.float32)
    foil = np.zeros((Hd, Wd), np.float32)
    foil[oy:oy + mh, ox:ox + mw] = m * rub
    lac = lac * (1 - foil[..., None]) + foil[..., None] * hexl('#D9A441', 1.25) * fk[..., None]
    body_m = ((y >= yf) & (y < yb)).astype(np.float32)
    # paint / wood boundary: one arc per face reaching toward the tip at the face centre
    fc = np.choose(face, [0.125, 0.5, 0.875]).astype(np.float32)
    fw = np.choose(face, [0.125, 0.25, 0.125]).astype(np.float32)
    y_paint = yb + 30.0 * (1.0 - ((uu - fc) / fw) ** 2)
    paint_c = cone & (y < y_paint)
    body_m = np.maximum(body_m, paint_c.astype(np.float32))
    rgb += lac * body_m[..., None]
    # ---------------- cedar cone (5 blade facets, grain converging to the tip)
    wood_m = (cone & ~paint_c & (y < yw)).astype(np.float32)
    fac = np.floor(uu * 3.0).clip(0, 2)
    wk = np.choose(fac.astype(np.int64), [0.78, 1.0, 0.55]).astype(np.float32)
    gr = 0.5 + 0.5 * np.sin(uu * 70.0 + 4.0 * np.sin(y * 0.05))
    wood = hexl('#C4915E')[None, None, :] * (wk * (0.85 + 0.15 * gr))[..., None]
    wood += (np.exp(-((uu - 0.4) / 0.06) ** 2) * 0.10)[..., None] * hexl('#FFE2C0')
    wood += (np.exp(-((uu - 0.96) / 0.04) ** 2) * 0.35)[..., None] * C('FLAME')
    rgb += wood * wood_m[..., None]
    # ---------------- graphite
    gm = (cone & (y >= yw)).astype(np.float32)
    gph = hexl('#3A393C')[None, None, :] * (0.7 + 0.5 * np.exp(-((uu - 0.38) / 0.12) ** 2))[..., None]
    gph += (np.exp(-((uu - 0.33) / 0.05) ** 2) * 0.25)[..., None] * hexl('#D8D4CC')
    rgb += gph * gm[..., None]
    # ---------------- ferrule (brushed aluminium, crimp grooves, knurl rows)
    fm = ((y >= ye) & (y < yf)).astype(np.float32)
    cyl = 0.30 + 0.70 * np.clip(np.cos((uu - 0.36) * math.pi * 0.95), 0, 1) ** 1.3
    brush = cv2.resize(rng.standard_normal((Hd, 3)).astype(np.float32), (Wd, Hd), interpolation=cv2.INTER_LINEAR) * 0.06
    yl = y - ye
    groove = np.zeros_like(y)
    for g0 in (24.0, 84.0):
        groove += np.exp(-((yl - g0) / 2.4) ** 2) * -0.55 + np.exp(-((yl - g0 - 4.0) / 1.6) ** 2) * 0.35
    knurl = ((yl > 36) & (yl < 72)).astype(np.float32) * 0.12 * np.sin(yl * 1.25)
    al = hexl('#B9B4AC')[None, None, :] * np.clip(cyl + brush + groove + knurl, 0.05, 1.6)[..., None]
    al += (np.exp(-((uu - 0.33) / 0.04) ** 2) * 0.55)[..., None] * hexl('#FFF6EA')
    al += (np.exp(-((uu - 0.975) / 0.03) ** 2) * 0.6)[..., None] * C('FLAME')
    rgb += al * fm[..., None]
    # ---------------- eraser (pink, matte, worn top, graphite smudge)
    em = (y < ye).astype(np.float32)
    ecyl = 0.38 + 0.62 * np.clip(np.cos((uu - 0.4) * math.pi * 0.9), 0, 1)
    crumb = cv2.resize(rng.standard_normal((Hd // 3, Wd // 3)).astype(np.float32), (Wd, Hd)) * 0.05
    er = hexl('#D7837C')[None, None, :] * (ecyl + crumb)[..., None]
    smudge = np.exp(-(((xx - (cx + 18)) / 14.0) ** 2 + ((y - 20) / 10.0) ** 2)) * 0.55
    er = er * (1 - smudge[..., None]) + smudge[..., None] * hexl('#3A3436')
    topband = np.clip(1 - (y - top_y) / 7.0, 0, 1)
    er = er * (1 - 0.25 * topband[..., None]) + (topband * 0.12)[..., None] * hexl('#FFE6E0')
    rgb += er * em[..., None]
    # contact AO where parts meet
    for yj in (ye, yf):
        rgb *= (1 - 0.45 * np.exp(-((y - yj) / 2.0) ** 2))[..., None]
    spr = np.zeros((Hd, Wd, 4), np.float32)
    spr[..., :3] = rgb * a[..., None]
    spr[..., 3] = a
    sha = cv2.GaussianBlur(a, (0, 0), 5.0)
    shadow = solid(sha * 0.9, C('NIGHT_0'))
    return ro(spr), ro(shadow), (cx, P + 4.0), (cx, P + float(yt))


@functools.lru_cache(maxsize=1)
def pencil_sprites():
    """(sprite, shadow, eraser_top_xy, tip_xy): R5 'pencil_top' passes 'key' / 'shadow' when rendered, else the
    procedural stand-in."""
    a = _asset('pencil_top')
    if a is not None:
        try:
            key = np.array(a.by_label('key'), np.float32)
            try:
                shadow = np.array(a.by_label('shadow'), np.float32)
            except Exception:
                shadow = solid(cv2.GaussianBlur(key[..., 3], (0, 0), 5.0) * 0.9, C('NIGHT_0'))
            fe = a.features
            if 'eraser_top' in fe and 'tip' in fe:
                top, tip = fe['eraser_top'], fe['tip']
            else:
                rows = np.nonzero(key[..., 3].max(1) > 0.5)[0]
                cols = np.nonzero(key[..., 3].max(0) > 0.5)[0]
                cxx = (cols[0] + cols[-1]) / 2.0
                top, tip = (cxx, float(rows[0])), (cxx, float(rows[-1]))
            return ro(key), ro(shadow), tuple(top), tuple(tip)
        except Exception:
            pass
    return pencil_procedural()


# =================================================================================================== NLE layout
VIEW_C = (540.0, 838.0)          # SHOTS: (540, 830) 660 x 820; smaller so the L12 slams (y 250-440) and the CUT chip
VIEW_CARD = (580, 720)           # (y 1201-1257) both clear the card: top 478, bottom 1198
VIEW_MEDIA = (560, 700)
MEDIA_R = 20.0
R1_CROP = (0.0, 510.0, 1080.0, 1860.0)
S_VIEW = VIEW_MEDIA[0] / (R1_CROP[2] - R1_CROP[0])         # 0.5926
CROP_C = ((R1_CROP[0] + R1_CROP[2]) / 2.0, (R1_CROP[1] + R1_CROP[3]) / 2.0)

PXS = 30.0                                               # px per timeline second (1 px / frame)
X_ORIGIN = 520.0 - PXS * 576 / 30                        # x of timeline time 0 (f576 -> x 520)
CUT_X = 600.0
PIVOT_X = 600.0
SCALE_P = 1.9
HEAD_X0, HEAD_X1 = 70.0, 136.0                           # fixed track-header column
TRACK_X0, TRACK_X1 = 138.0, 1002.0
STRIP_X0, STRIP_X1 = 130.0, 1012.0                       # native x range kept in the lane strips

PANEL_N = (70.0, 1260.0, 1010.0, 1470.0)
PANEL_P = (70.0, 872.0, 1010.0, 1444.0)
LANES_N = dict(ruler=(1270.0, 1296.0), V2=(1302.0, 1338.0), V1=(1346.0, 1396.0), A1=(1404.0, 1458.0))
LANES_P = dict(ruler=(884.0, 936.0), V2=(952.0, 1036.0), V1=(1050.0, 1200.0), A1=(1214.0, 1430.0))
LANE_COL = dict(V2='EMBER', V1='FLAME', A1='GOLD')

V1_EDGES = (60, 214, 322, 431, 600, 712, 836, 940, 1100)
V1_NAMES = ('walkman_keys.mov', 'mix98_label.mov', 'tape_spill.mov', 'cassette_rewind.mov', 'pencil_cut.mov',
            'hub_macro.mov', 'rescue_take2.mov', 'walkman_lid.mov')
V2_CLIPS = ((150, 296, 'title_01'), (380, 548, 'lower_third'), (618, 770, 'flare_fx'), (858, 1060, 'grain_35mm'))
A1_CLIPS = ((60, 600, 'ratchet_loop.wav'), (602, 1100, 'tape_hiss.wav'))
IN_OUT = (431.0, 712.0)
ACTIVE_CLIP = 3                                          # cassette_rewind.mov (under the scrub)

PEN_LEN = 620.0                                          # visible pencil length on screen (SHOTS C)
PEN_TOP_Y = 876.0                                        # eraser top in the payoff layout (head in the ruler)
PEN_X0 = 520.0                                           # screen x before the snap


def x_of(src_t):
    return X_ORIGIN + PXS * src_t


def src_of(x):
    return (x - X_ORIGIN) / PXS


def timecode(src_t):
    fr = int(math.floor(src_t * FPS + 1e-6))
    return '00:00:%02d:%02d' % ((fr // FPS) % 60, fr % FPS)


def _lerp(a, b, u):
    return a + (b - a) * u


# --------------------------------------------------------------------------------------------------- state
SCRUB_X = (470.0, 680.0, 500.0, CUT_X)                  # back / forward / back / forward onto the cut (native px)


def scrub():
    """((frame, x), ...) of the four scrub jumps = the L12 word frames."""
    return tuple(zip(TM['L12'], SCRUB_X))


def _playhead_native(t):
    """Playhead x in native timeline px (before the zoom)."""
    f = t * FPS
    sc = scrub()
    f_s = sc[0][0]
    if f < f_s - 0.5:                                       # 1 px / f crawl from x 520 at f576
        return 520.0 + (min(f, f_s - 0.01) - 576.0) * 1.0
    x = 520.0 + (f_s - 0.01 - 576.0)
    for f0, xb in sc:
        if f < f0 - 0.5:
            break
        u = (f - f0) / 6.0
        xa = x
        if u <= 1:
            x = xa + (xb - xa) * ease('inout_expo', u)
        else:                                               # SNAP landing: a small decaying overshoot
            tl = (f - f0 - 6.0) / FPS
            x = xb + (xb - xa) * 0.05 * math.sin(2 * math.pi * 5.0 * tl) * math.exp(-tl * 16.0)
    if f >= 728 - 0.5:                                      # step back to just before the cut (screen x 520)
        xn = PIVOT_X + (PEN_X0 - PIVOT_X) / SCALE_P
        x = _lerp(CUT_X, xn, ease('inout_cubic', (f - 728) / 20.0))
    return x


def state(t):
    """Everything the NLE draw needs at t (screen px unless noted)."""
    f = t * FPS
    f_cut, f_snap = TM['L12'][-1], TM['NLE_snap']
    c0, c1 = TM['NLE_chip_out']
    st = {}
    st['pull'] = ease('inout_sine', (f - 576) / 21.0)                       # 0 at f576, 1 at f597
    st['panel_in'] = ease('out_cubic', (f - 584) / 16.0)
    st['head_in'] = ease('inout_sine', (f - 584) / 16.0)
    ve = ease('in_cubic', (f - 704) / 14.0)
    st['view_dy'] = -70.0 * ve                                               # lifts + fades (gone f718); it never
    st['view_op'] = 1.0 - ease('inout_sine', (f - 704) / 14.0)              # crosses the top caption band
    u12 = ease('inout_cubic', (f - 704) / 40.0)
    st['u12'] = u12
    st['S'] = _lerp(1.0, SCALE_P, u12)
    xn = _playhead_native(t)
    st['x_native'] = xn
    st['x'] = PIVOT_X + (xn - PIVOT_X) * st['S']
    # source time shown in the viewer: real time while playing, the playhead's time (12 Hz) while scrubbing
    if f < TM['L12'][0] - 0.5:
        src = t
    else:
        tq = math.floor(t * 12.0 + 1e-6) / 12.0
        src = src_of(_playhead_native(max(tq, F(TM['L12'][0]))))
    st['src'] = src
    st['tc'] = timecode(src)
    st['cut'] = f >= f_cut - 0.5
    st['cut_pop'] = 0.7 + 0.3 * X.spring(max(0.0, t - F(f_cut)), 'POP') if st['cut'] else 0.0
    st['chip_op'] = (K.ramp(t, F(f_cut) - HALF, F(f_cut + 3), 'out_cubic') *
                     (1.0 - ease('in_cubic', (f - c0) / float(c1 - c0 + 1))) if st['cut'] else 0.0)
    st['morph'] = ease('out_cubic', (f - DROPOUT[0]) / 16.0)               # line -> pencil
    st['pencil'] = f >= DROPOUT[0] - 0.5
    sn = X.spring(max(0.0, t - F(f_snap)), 'SNAP') if f >= f_snap - 0.5 else 0.0
    st['pen_x'] = _lerp(PEN_X0, CUT_X, sn)
    tt = t - F(f_snap)
    st['pen_rot'] = 2.0 * math.sin(2 * math.pi * 3.2 * tt) * math.exp(-tt * 6.0) if tt > 0 else 0.0
    st['contact'] = (K.ramp(t, F(f_snap) - HALF, F(f_snap + 2), 'out_cubic') *
                     (1.0 - ease('inout_sine', (f - f_snap - 6) / 10.0)) if f >= f_snap - 0.5 else 0.0)
    return st


def lane_rect(name, u12):
    a, b = LANES_N[name], LANES_P[name]
    return _lerp(a[0], b[0], u12), _lerp(a[1], b[1], u12)


def panel_rect(u12, dy=0.0):
    return tuple(_lerp(a, b, u12) + (dy if i in (1, 3) else 0.0) for i, (a, b) in enumerate(zip(PANEL_N, PANEL_P)))


# --------------------------------------------------------------------------------------------------- background
@functools.lru_cache(maxsize=1)
def nle_bg():
    """NIGHT_1 -> NIGHT_0 gradient, 40 px grid at 4 %, soft vignette (read-only)."""
    g = K.gradient(K.W, K.H, [K.C['NIGHT_1'], K.C['NIGHT_0']], angle=-90)
    cv = np.zeros((K.H, K.W, 4), np.float32)
    cv[..., :3] = g[..., :3]
    cv[..., 3] = 1.0
    yy, xx = np.mgrid[0:K.H, 0:K.W].astype(np.float32)
    grid = ((np.mod(xx, 40.0) < 1.0) | (np.mod(yy, 40.0) < 1.0)).astype(np.float32) * 0.04
    cv[..., :3] += grid[..., None] * C('IVORY', 0.55)
    glow = np.exp(-(((xx - 820) / 700.0) ** 2 + ((yy - 300) / 700.0) ** 2)) * 0.05
    cv[..., :3] += glow[..., None] * C('FLAME')
    vig = np.clip(1.0 - 0.45 * (((xx - 540) / 760.0) ** 2 + ((yy - 960) / 1150.0) ** 2), 0.3, 1.0)
    cv[..., :3] *= vig[..., None]
    return ro(cv)


# --------------------------------------------------------------------------------------------------- viewer
@functools.lru_cache(maxsize=1)
def viewer_card():
    return ui.glass_card(VIEW_CARD[0], VIEW_CARD[1], r=28, look=LOOK, rim=0.8)


def _rr_mask(h, w, x0, y0, x1, y1, r):
    """Anti-aliased rounded-rect coverage on an (h, w) grid (float rect, radius r)."""
    X0, Y0 = int(max(0, math.floor(x0))), int(max(0, math.floor(y0)))
    X1, Y1 = int(min(w, math.ceil(x1))), int(min(h, math.ceil(y1)))
    m = np.zeros((h, w), np.float32)
    if X1 <= X0 or Y1 <= Y0:
        return m, (X0, Y0, X0, Y0)
    ys, xs = np.mgrid[Y0:Y1, X0:X1].astype(np.float32) + 0.5
    cx, cy = (x0 + x1) / 2.0, (y0 + y1) / 2.0
    hw, hh = (x1 - x0) / 2.0, (y1 - y0) / 2.0
    r = min(r, hw, hh)
    qx = np.abs(xs - cx) - (hw - r)
    qy = np.abs(ys - cy) - (hh - r)
    d = np.sqrt(np.maximum(qx, 0) ** 2 + np.maximum(qy, 0) ** 2) + np.minimum(np.maximum(qx, qy), 0) - r
    m[Y0:Y1, X0:X1] = np.clip(0.5 - d, 0, 1)
    return m, (X0, Y0, X1, Y1)


@functools.lru_cache(maxsize=1)
def _view_overlays():
    """Static viewer chrome in media px (640 x 800): top + bottom scrims, title-safe corners, play icon, FIT."""
    w, h = VIEW_MEDIA
    lay = np.zeros((h, w, 4), np.float32)
    ys = np.arange(h, dtype=np.float32)[:, None]
    top = np.clip(1.0 - ys / 96.0, 0, 1) ** 1.6 * 0.78
    bot = np.clip((ys - (h - 110)) / 110.0, 0, 1) ** 1.6 * 0.80
    a = np.broadcast_to(np.maximum(top, bot), (h, w)).astype(np.float32)
    lay[..., :3] = a[..., None] * C('NIGHT_0')
    lay[..., 3] = a
    S = ui.Surf(w, h, lay)
    ins_x, ins_y, L = 32, 112, 34                      # title-safe corners
    col = C('IVORY', 0.55)
    for (x, y, sx, sy) in ((ins_x, ins_y, 1, 1), (w - ins_x, ins_y, -1, 1), (ins_x, h - ins_y, 1, -1),
                           (w - ins_x, h - ins_y, -1, -1)):
        S.rrect(min(x, x + sx * L), y - 1, L, 2, 1, col, opacity=0.45)
        S.rrect(x - 1, min(y, y + sy * L), 2, L, 1, col, opacity=0.45)
    S.rrect(w / 2 - 12, h / 2 - 1, 24, 2, 1, col, opacity=0.35)         # centre cross
    S.rrect(w / 2 - 1, h / 2 - 12, 2, 24, 1, col, opacity=0.35)
    img = S.img
    # play triangle (bottom-left) + FIT (bottom-right)
    tri = np.zeros((h * 1, w), np.uint8)
    pts = np.int32([[28 * 4, (h - 48) * 4], [50 * 4, (h - 36) * 4], [28 * 4, (h - 24) * 4]])
    big = np.zeros((h * 4, w * 4), np.uint8)
    cv2.fillPoly(big, [pts], 255, cv2.LINE_AA, shift=0)
    tri = cv2.resize(big, (w, h), interpolation=cv2.INTER_AREA).astype(np.float32) / 255.0
    over(img, solid(tri, C('AMBER', 1.1)))
    tx('FIT', 'jw_mono', 28, fill='ASH').draw(img, w - 28, h - 36, anchor=(1.0, 0.5))
    return ro(img)


@functools.lru_cache(maxsize=1)
def _media_shade():
    """Inner edge shade + hairline highlight for the media slot (multiplicative / additive, media px)."""
    w, h = VIEW_MEDIA
    ys, xs = np.mgrid[0:h, 0:w].astype(np.float32) + 0.5
    hw, hh, r = w / 2.0, h / 2.0, MEDIA_R
    qx = np.abs(xs - hw) - (hw - r)
    qy = np.abs(ys - hh) - (hh - r)
    d = np.sqrt(np.maximum(qx, 0) ** 2 + np.maximum(qy, 0) ** 2) + np.minimum(np.maximum(qx, qy), 0) - r
    shade = (1 - 0.35 * np.exp(d / 14.0)).astype(np.float32)
    hl = np.clip(0.5 - np.abs(d + 0.8) + 0.8, 0, 1) * np.clip(1.2 - ys / h * 2.0, 0, 1) * 0.30
    return ro(shade), ro(hl.astype(np.float32))


def _viewer_xf(st):
    """(s, cx, cy, crop rect in world px, radius) of the viewer media at this state."""
    p = st['pull']
    s = _lerp(1.0, S_VIEW, p)
    cy_scr = _lerp(CROP_C[1], VIEW_C[1], p) + st['view_dy']
    crop = (0.0, _lerp(0.0, R1_CROP[1], p), 1080.0, _lerp(1920.0, R1_CROP[3], p))
    return s, 540.0, cy_scr, crop, _lerp(0.0, MEDIA_R, p)


def viewer(cv, t, st, media):
    """The glass viewer: card, media (pull-back from full frame), header row, overlays, progress line."""
    op = st['view_op']
    if op <= 1e-3:
        return
    s, cx, cy, crop, rad = _viewer_xf(st)
    p = st['pull']
    k = s / S_VIEW                                     # scale relative to the settled viewer
    yc = cy                                            # screen y of the crop centre
    card_op = ease('inout_sine', (p - 0.45) / 0.55) * op
    if card_op > 1e-3:
        viewer_card().draw(cv, cx, yc, scale=k, opacity=card_op)
    src = media(st['src'])
    # media: world px -> screen, crop centre CROP_C -> (cx, yc)
    M = np.float32([[s, 0, cx - s * CROP_C[0]], [0, s, yc - s * CROP_C[1]]])
    x0, y0 = cx + s * (crop[0] - CROP_C[0]), yc + s * (crop[1] - CROP_C[1])
    x1, y1 = cx + s * (crop[2] - CROP_C[0]), yc + s * (crop[3] - CROP_C[1])
    mask, (X0, Y0, X1, Y1) = _rr_mask(K.H, K.W, x0, y0, x1, y1, rad)
    if X1 <= X0 or Y1 <= Y0:
        return
    Ms = M.copy()
    Ms[0, 2] -= X0
    Ms[1, 2] -= Y0
    reg = cv2.warpAffine(np.ascontiguousarray(src), Ms, (X1 - X0, Y1 - Y0),
                         flags=cv2.INTER_AREA if s < 0.75 else cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)
    m = mask[Y0:Y1, X0:X1, None] * np.float32(op)
    if p >= 0.999:                                     # settled: the media sits inside the glass
        sh, hl = _media_shade()
        hh_, ww_ = reg.shape[:2]
        if (hh_, ww_) == sh.shape:
            reg[..., :3] *= sh[..., None]
            reg[..., :3] += hl[..., None]
    dst = cv[Y0:Y1, X0:X1]
    dst *= (1.0 - m)
    dst += reg * m
    # chrome on the media (title-safe, scrims, play, FIT) + header row
    ho = st['head_in'] * op
    if ho > 1e-3:
        K.draw(cv, _view_overlays(), cx, yc, scale=k, opacity=ho)
        top = yc - VIEW_MEDIA[1] / 2.0 * k
        left, right = cx - VIEW_MEDIA[0] / 2.0 * k, cx + VIEW_MEDIA[0] / 2.0 * k
        hy = top + 34.0 * k + 6.0 * (1.0 - st['head_in'])
        tx('cassette_rewind.mov', 'jw_mono', 24, fill='ASH').draw(cv, left + 22 * k, hy, anchor=(0.0, 0.5),
                                                                  scale=k, opacity=ho)
        tx(st['tc'], 'jw_mono', 28).draw(cv, right - 22 * k, hy, anchor=(1.0, 0.5), scale=k, opacity=ho, snap=False)
        # progress line (timeline position under the playhead)
        bot = yc + VIEW_MEDIA[1] / 2.0 * k
        by = bot - 36.0 * k
        bx0, bx1 = left + 72 * k, right - 96 * k
        prog = min(1.0, max(0.0, (st['x_native'] - TRACK_X0) / (TRACK_X1 - TRACK_X0)))
        _hbar(cv, bx0, bx1, by, 3.0 * k, C('IVORY', 0.22), 0.9 * ho)
        _hbar(cv, bx0, _lerp(bx0, bx1, prog), by, 3.0 * k, C('FLAME', 1.2), ho)
        K.draw(cv, _dot_spr(), _lerp(bx0, bx1, prog), by, scale=k, opacity=ho)


@functools.lru_cache(maxsize=1)
def _dot_spr():
    return ro(K.glow(K.disc(6.0, C('AMBER', 1.6)), C('FLAME'), sigmas=(3, 8), strength=0.6))


def _hbar(cv, x0, x1, y, th, col, op):
    """AA horizontal bar (sub-pixel in x and y)."""
    if x1 - x0 <= 0.2 or op <= 1e-4:
        return
    X0, X1 = int(max(0, math.floor(x0))), int(min(K.W, math.ceil(x1)))
    Y0, Y1 = int(max(0, math.floor(y - th / 2 - 1))), int(min(K.H, math.ceil(y + th / 2 + 1)))
    if X1 <= X0 or Y1 <= Y0:
        return
    xs = np.arange(X0, X1, dtype=np.float32) + 0.5
    ys = np.arange(Y0, Y1, dtype=np.float32) + 0.5
    ax = np.clip(np.minimum(xs - x0, x1 - xs) + 0.5, 0, 1)
    ay = np.clip(th / 2 - np.abs(ys - y) + 0.5, 0, 1)
    a = (ay[:, None] * ax[None, :] * np.float32(op))[..., None]
    reg = cv[Y0:Y1, X0:X1]
    reg *= 1 - a
    reg[..., :3] += a * col
    reg[..., 3:4] += a


def _vbar(cv, x, y0, y1, th, col, op, add=False):
    if y1 - y0 <= 0.2 or op <= 1e-4:
        return
    X0, X1 = int(max(0, math.floor(x - th / 2 - 1))), int(min(K.W, math.ceil(x + th / 2 + 1)))
    Y0, Y1 = int(max(0, math.floor(y0))), int(min(K.H, math.ceil(y1)))
    if X1 <= X0 or Y1 <= Y0:
        return
    xs = np.arange(X0, X1, dtype=np.float32) + 0.5
    ys = np.arange(Y0, Y1, dtype=np.float32) + 0.5
    ay = np.clip(np.minimum(ys - y0, y1 - ys) + 0.5, 0, 1)
    ax = np.clip(th / 2 - np.abs(xs - x) + 0.5, 0, 1)
    a = (ay[:, None] * ax[None, :] * np.float32(op))[..., None]
    reg = cv[Y0:Y1, X0:X1]
    if not add:
        reg *= 1 - a
        reg[..., 3:4] += a
    reg[..., :3] += a * col


# --------------------------------------------------------------------------------------------------- timeline panel
@functools.lru_cache(maxsize=1)
def _panel_base():
    """Glass sized for the payoff layout; drawn 3-sliced at any height (the middle rows stretch)."""
    w = int(PANEL_P[2] - PANEL_P[0])
    h = int(PANEL_P[3] - PANEL_P[1])
    return ui.glass_card(w, h, r=22, look=LOOK, rim=0.9)


def _rr_poly(x0, y0, x1, y1, r, n=8):
    pts = []
    for cx, cy, a0 in ((x1 - r, y0 + r, -90), (x1 - r, y1 - r, 0), (x0 + r, y1 - r, 90), (x0 + r, y0 + r, 180)):
        for i in range(n + 1):
            a = math.radians(a0 + 90.0 * i / n)
            pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    return np.array(pts, np.float64)


def panel(cv, rect, op):
    """Glass panel at screen rect: shadow, frost, 3-sliced face."""
    if op <= 1e-3:
        return
    base = _panel_base()
    x0, y0, x1, y1 = rect
    h = y1 - y0
    p = base.pad
    face = base.face
    cap = p + 40
    Hf = face.shape[0]
    # shadow (soft: scaled non-uniformly)
    sh = base.shadow
    spx, spy = base.spad
    K.draw(cv, sh, (x0 + x1) / 2.0, (y0 + y1) / 2.0, scale=((base.w + 2 * spx) / sh.shape[1],
                                                            (h + 2 * spy) / sh.shape[0]), opacity=op)
    ui.frost_poly(cv, _rr_poly(x0, y0, x1, y1, 22.0), base.frost, min(1.0, op * 1.5))
    top, mid, bot = face[:cap], face[cap:Hf - cap], face[Hf - cap:]
    mh = max(1.0, h - 80.0)
    K.draw(cv, top, x0 - p, y0 - p, anchor=(0, 0), opacity=op)
    K.draw(cv, mid, x0 - p, y0 + 40.0, anchor=(0, 0), scale=(1.0, mh / mid.shape[0]), opacity=op)
    K.draw(cv, bot, x0 - p, y0 + 40.0 + mh, anchor=(0, 0), opacity=op)


# --------------------------------------------------------------------------------------------------- lane strips
@functools.lru_cache(maxsize=1)
def thumb_sources():
    """4:5 frames for the V1 filmstrips: real renders when present (hub_loop, label, walkman_loop, hub_rescue),
    else the stand-in hub frames."""
    srcs = []
    for name in ('hub_loop', 'label', 'walkman_loop', 'hub_rescue', 'walkman_eat'):
        a = _asset(name)
        if a is None:
            continue
        for i in range(0, max(1, a.n), max(1, a.n // 4)):
            fr = a.frame(i)
            srcs.append(fr)
    if not srcs:
        srcs = [standin_hub(i) for i in (0, 3, 6, 9, 12)]
    out = []
    for fr in srcs:
        h, w = fr.shape[:2]
        ch = int(w * 5 / 4)
        y0 = int(min(max(0, h * 0.62 - ch / 2), h - ch))
        out.append(np.ascontiguousarray(fr[y0:y0 + ch]))
    return out


@functools.lru_cache(maxsize=64)
def _thumb(i, tw, th):
    src = thumb_sources()[i % len(thumb_sources())]
    t = cv2.resize(src, (tw, th), interpolation=cv2.INTER_AREA)
    t[..., :3] *= 0.86
    t[..., 3] = 1.0
    return ro(t)


def _amp(xn, seed=0, kind='ratchet'):
    """Deterministic waveform amplitude (0..1) at native x positions (array)."""
    rng = np.random.default_rng(seed)
    base_x = np.arange(-50, 1200, 1.0)
    n1 = rng.random(len(base_x))
    n2 = np.convolve(rng.random(len(base_x)), np.ones(9) / 9.0, mode='same')
    a1 = np.interp(xn, base_x, n1)
    a2 = np.interp(xn, base_x, n2)
    if kind == 'ratchet':
        beat = PXS * 16 / 30.0                                 # 16 px per beat
        ph = np.mod(xn - X_ORIGIN, beat)
        tick = np.exp(-ph / 3.2) * 0.75
        sub = np.mod(xn - X_ORIGIN, beat / 6.0)
        click = np.exp(-sub / 0.9) * 0.25
        a = 0.18 + 0.22 * a2 + tick + click * (0.6 + 0.4 * a1)
    else:
        a = 0.14 + 0.12 * a2 + 0.10 * a1
    return np.clip(a, 0, 1)


@functools.lru_cache(maxsize=16)
def lane_strip(name, k, h):
    """One lane's content (clips, thumbnails, waveform, ticks) for native x in [STRIP_X0, STRIP_X1] at horizontal
    scale k and height h (px). Premultiplied sprite (h, w)."""
    w = int(round((STRIP_X1 - STRIP_X0) * k))
    h = int(round(h))
    S = ui.Surf(w, h)

    def X(xn):
        return (xn - STRIP_X0) * k
    big = k > 1.4
    if name == 'ruler':
        S.rrect(0, 0, w, h, 6, C('NIGHT_0'), opacity=0.55)
        a, b = X(IN_OUT[0]), X(IN_OUT[1])
        S.rrect(a, 0, b - a, h, 3, C('FLAME', 0.35), opacity=0.35)
        S.rrect(a, 0, b - a, 2.0 * (1 + big), 1, C('FLAME', 1.0), opacity=0.8)
        for xx_ in (a, b):
            S.rrect(xx_ - 1, 0, 2, h * 0.55, 1, C('FLAME', 1.1), opacity=0.9)
        step = 0.25 if big else 0.5
        t0 = math.floor(src_of(STRIP_X0))
        tt = t0
        while x_of(tt) <= STRIP_X1:
            xs = X(x_of(tt))
            whole = abs(tt - round(tt)) < 1e-6
            four = whole and int(round(tt)) % 4 == 0
            th = h * (0.62 if four else (0.34 if whole else 0.18))
            S.rrect(xs - 0.6 * (1 + big * 0.4), h - th, 1.2 * (1 + big * 0.4), th, 0.5, C('IVORY'),
                    opacity=0.55 if whole else 0.32)
            tt += step
        S.rrect(0, h - 1.2, w, 1.2, 0.5, C('IVORY'), opacity=0.18)
        return ro(S.img)
    col = C(LANE_COL[name])
    r = 7.0 if big else 4.5
    if name == 'V1':
        for i in range(len(V1_EDGES) - 1):
            xa, xb = X(V1_EDGES[i]) + 1.5, X(V1_EDGES[i + 1]) - 1.5
            if xb < 0 or xa > w:
                continue
            S.rrect(xa, 1, xb - xa, h - 2, r, col * 0.10 + C('SMOKE') * 0.8)
            label_h = 30 if big else 0
            th_ = int(h - 6 - label_h)
            tw_ = int(round(th_ * 0.8))
            # filmstrip thumbnails (clip clipped to its rounded body)
            strip = np.zeros((h, int(math.ceil(xb - xa)) + 2, 4), np.float32)
            xx_ = 0.0
            j = 0
            while xx_ < strip.shape[1]:
                th_spr = _thumb(i * 3 + j, tw_, th_)
                ww = min(tw_, strip.shape[1] - int(xx_))
                strip[3 + label_h:3 + label_h + th_, int(xx_):int(xx_) + ww] = th_spr[:, :ww]
                strip[3 + label_h:3 + label_h + th_, int(xx_) + ww - 1:int(xx_) + ww, :3] *= 0.35
                xx_ += tw_
                j += 1
            m = K.rrect_alpha(strip.shape[1] - 2, h - 2, r, 0)
            mm = np.zeros(strip.shape[:2], np.float32)
            mm[1:1 + m.shape[0], 0:m.shape[1]] = m
            strip *= mm[..., None]
            tint = solid(mm * 0.10, col)
            over(strip, tint)
            S.paste(ro(strip), int(xa), 0)
            if big:
                S.rrect(xa, 1, xb - xa, label_h + 3, r, col * 0.30, opacity=0.95)
                S.text(xa + 14, 1 + label_h * 0.5 + 2, V1_NAMES[i], 26, 'mono', color=C('IVORY'), anchor='lm',
                       opacity=0.88)
            act = i == ACTIVE_CLIP
            S.stroke_rrect(xa, 1, xb - xa, h - 2, r, 2.0 if act else 1.3, col * (1.5 if act else 0.9))
        return ro(S.img)
    if name == 'V2':
        for (a_, b_, nm) in V2_CLIPS:
            xa, xb = X(a_) + 1.5, X(b_) - 1.5
            if xb < 0 or xa > w:
                continue
            S.rrect_grad(xa, 1, xb - xa, h - 2, r, col * 0.75, col * 0.42, angle=-90)
            S.sheen(xa, 1, xb - xa, h - 2, r, amount=0.10)
            S.stroke_rrect(xa, 1, xb - xa, h - 2, r, 1.3, col * 1.6)
            cy = h * (0.66 if big else 0.5)
            S.rrect(xa + 6, cy - 0.75, xb - xa - 12, 1.5, 0.7, C('AMBER'), opacity=0.35)
            for q in (0.18, 0.5, 0.82):
                kx = xa + (xb - xa) * q
                dk = 6.0 if big else 3.0
                pts = [(kx, cy - dk), (kx + dk, cy), (kx, cy + dk), (kx - dk, cy)]
                m = ui.fill_mask([(np.array(pts), True)], w, h)
                S.fill(m, 0, 0, C('AMBER', 1.3))
            if big:
                S.text(xa + 14, h * 0.30, nm, 26, 'mono', color=C('IVORY'), anchor='lm', opacity=0.85)
        return ro(S.img)
    if name == 'A1':
        for ci, (a_, b_, nm) in enumerate(A1_CLIPS):
            xa, xb = X(a_) + 1.5, X(b_) - 1.5
            if xb < 0 or xa > w:
                continue
            S.rrect(xa, 1, xb - xa, h - 2, r, col * 0.10 + C('SMOKE') * 0.7)
            top_pad = 30 if big else 3
            cy = top_pad + (h - top_pad) / 2.0
            amp_h = (h - top_pad) / 2.0 - 3
            xs = np.arange(max(0, int(xa) + 2), min(w, int(xb) - 2), 1.0)
            xn = STRIP_X0 + xs / k
            a = _amp(xn, seed=7 + ci, kind='ratchet' if ci == 0 else 'hiss')
            pk = np.clip(a * 1.25, 0, 1)
            img = S.img
            ys = np.arange(h, dtype=np.float32)[:, None] + 0.5
            for amp_arr, kcol, al in ((pk, col * 0.42, 0.40), (a * 0.62, col * 0.80, 0.85)):
                hh = amp_arr[None, :] * amp_h
                cov = np.clip(hh - np.abs(ys - cy) + 0.5, 0, 1) * al
                X0 = int(xs[0]) if len(xs) else 0
                reg = img[:, X0:X0 + len(xs)]
                reg *= (1 - cov[..., None])
                reg[..., :3] += cov[..., None] * kcol
                reg[..., 3] += cov
            S.rrect(xa + 4, cy - 0.5, xb - xa - 8, 1.0, 0.5, col, opacity=0.35)
            vy = top_pad + (h - top_pad) * 0.24
            S.rrect(xa + 4, vy - 0.9, xb - xa - 8, 1.8, 0.9, C('IVORY'), opacity=0.45)
            for q in (0.08, 0.92):
                kx = xa + (xb - xa) * q
                S.circle(kx, vy, 5.0 if big else 2.6, C('IVORY'), opacity=0.9)
            fl = 18 * k
            pts = [(xa, 1), (xa + fl, 1), (xa, 1 + (h - 2) * 0.5)]
            S.fill(ui.fill_mask([(np.array(pts), True)], w, h), 0, 0, C('IVORY', 0.6))
            S.stroke_rrect(xa, 1, xb - xa, h - 2, r, 1.3, col * 0.9)
            if big:
                S.text(xa + 14, top_pad * 0.55, nm, 26, 'mono', color=C('IVORY'), anchor='lm', opacity=0.85)
        return ro(S.img)
    raise KeyError(name)


def _strip_draw(cv, spr, k, S, y0, y1, op):
    """Draw a lane strip (built at scale k) at the current zoom S into screen rows y0..y1, clipped to the track."""
    sx0 = PIVOT_X + (STRIP_X0 - PIVOT_X) * S             # screen x of the strip's left edge
    f = S / k                                            # screen px per strip px
    c0 = max(0, int(math.floor((TRACK_X0 - sx0) / f)))
    c1 = min(spr.shape[1], int(math.ceil((TRACK_X1 - sx0) / f)))
    if c1 <= c0:
        return
    sub = spr[:, c0:c1]
    # feather the two clip edges (1 px) so nothing pops at the header column
    K.draw(cv, sub, sx0 + c0 * f, y0, scale=(f, (y1 - y0) / spr.shape[0]), anchor=(0, 0), opacity=op)


def lanes(cv, st, rect, op):
    u12, S = st['u12'], st['S']
    big_w = ease('inout_sine', (u12 - 0.30) / 0.30)      # crossfade native -> payoff strips mid-zoom
    for name in ('ruler', 'V2', 'V1', 'A1'):
        y0, y1 = lane_rect(name, u12)
        dy = rect[1] - _lerp(PANEL_N[1], PANEL_P[1], u12)
        y0, y1 = y0 + dy, y1 + dy
        hn = LANES_N[name][1] - LANES_N[name][0]
        hp = LANES_P[name][1] - LANES_P[name][0]
        if big_w < 1.0:
            _strip_draw(cv, lane_strip(name, 1.0, hn), 1.0, S, y0, y1, op * (1.0 - big_w) if big_w > 0 else op)
        if big_w > 0.0:
            _strip_draw(cv, lane_strip(name, SCALE_P, hp), SCALE_P, S, y0, y1, op * big_w)
        if name != 'ruler':
            px = _lerp(28.0, 34.0, u12)
            tx(name, 'jw_mono', 34, fill='ASH').draw(cv, 103.0, (y0 + y1) / 2.0, scale=px / 34.0, opacity=op * 0.95)
            _vbar(cv, 131.0, y0 + 3, y1 - 3, 3.0, C(LANE_COL[name], 1.2), op)
            _hbar(cv, TRACK_X0, TRACK_X1, y1 + 3.0, 1.0, C('IVORY'), op * 0.06)
    # ruler labels (every 4 s)
    y0, y1 = lane_rect('ruler', u12)
    dy = rect[1] - _lerp(PANEL_N[1], PANEL_P[1], u12)
    ly = y0 + dy + (y1 - y0) * 0.36
    px = _lerp(28.0, 34.0, u12)
    s0 = math.floor(src_of(PIVOT_X + (TRACK_X0 - PIVOT_X) / S) / 4.0) * 4
    sec = s0
    while True:
        xs = PIVOT_X + (x_of(sec) - PIVOT_X) * S
        if xs > TRACK_X1 + 60:
            break
        if TRACK_X0 + 6 < xs + 6 and xs + 6 + 80 < TRACK_X1 + 40:
            fade = min(1.0, max(0.0, (xs - TRACK_X0) / 30.0), max(0.0, (TRACK_X1 - xs - 70) / 30.0))
            if fade > 0:
                tx('00:%02d' % int(sec), 'jw_mono', 34, fill='ASH').draw(cv, xs + 6, ly, anchor=(0.0, 0.5),
                                                                       scale=px / 34.0, opacity=op * fade, snap=False)
        sec += 4
    _vbar(cv, HEAD_X1, rect[1] + 10, rect[3] - 10, 1.0, C('IVORY'), op * 0.08)
    # scroll bar (thumb shrinks as the content zooms)
    sy = rect[3] - 7.0
    span = (TRACK_X1 - TRACK_X0) / S
    cxs = _lerp(560.0, PIVOT_X, u12)
    _hbar(cv, cxs - span * 0.5, cxs + span * 0.5, sy, 3.0, C('IVORY'), op * 0.18)


# --------------------------------------------------------------------------------------------------- playhead + marker
@functools.lru_cache(maxsize=1)
def _ph_line():
    """Playhead line (4 px FLAME core) + glow, built 600 px tall; drawn scaled in y."""
    h = 600
    line = np.zeros((h, 4, 4), np.float32)
    line[..., :3] = C('FLAME', 1.25) * 0.75 + C('AMBER', 0.5) * 0.25
    line[..., 3] = 1.0
    g = K.glow(line, C('FLAME'), sigmas=(3, 10, 28), strength=0.9)
    return ro(g), (g.shape[1] - 4) // 2, (g.shape[0] - h) // 2


@functools.lru_cache(maxsize=1)
def _ph_head():
    """22 x 26 down-pointing pentagon: AMBER core, FLAME rim, glow."""
    s = 4
    w, h, p = 22, 26, 12
    big = np.zeros(((h + 2 * p) * s, (w + 2 * p) * s), np.uint8)
    pts = np.int32([[p, p], [p + w, p], [p + w, p + h * 0.58], [p + w / 2, p + h], [p, p + h * 0.58]]) * s
    cv2.fillPoly(big, [pts], 255, cv2.LINE_AA)
    m = cv2.resize(big, (w + 2 * p, h + 2 * p), interpolation=cv2.INTER_AREA).astype(np.float32) / 255.0
    inner = cv2.erode(m, np.ones((3, 3), np.uint8), iterations=2)
    spr = solid(m, C('FLAME', 1.3))
    over(spr, solid(inner, C('AMBER', 1.25)))
    g = K.glow(spr, C('FLAME'), sigmas=(3, 9), strength=0.6)
    pad = (g.shape[0] - m.shape[0]) // 2
    tip = ((p + w / 2 + pad) / g.shape[1], (p + h + pad) / g.shape[0])
    return ro(g), tip


def playhead(cv, x, y_top, y_bot, op, width=4.0, head_y=None, head_op=1.0):
    if op <= 1e-3:
        return
    spr, px, py = _ph_line()
    h = 600.0
    if width > 0.05:
        K.draw(cv, spr, x, (y_top + y_bot) / 2.0, scale=(width / 4.0, (y_bot - y_top) / h), opacity=op)
    if head_y is not None and head_op > 1e-3:
        hs, tip = _ph_head()
        K.draw(cv, hs, x, head_y, anchor=tip, opacity=op * head_op)


@functools.lru_cache(maxsize=1)
def _cut_chip():
    base = ui.glass_card(150, 56, r=28, look=LOOK, rim=1.0, shadow=0.6)
    f = base.face_at()
    p = base.pad
    d = 7.0
    pts = np.array([(p + 28, p + 28 - d), (p + 28 + d, p + 28), (p + 28, p + 28 + d), (p + 28 - d, p + 28)])
    m = ui.fill_mask([(pts, True)], f.shape[1], f.shape[0])
    over(f, solid(m, C('AMBER', 1.3)))
    tx('CUT', 'jw_mono', 30).draw(f, p + 92, p + 28)
    return ui.derive_panel(base, f)


@functools.lru_cache(maxsize=1)
def _flag():
    """Ruler marker flag (AMBER pentagon, 16 x 18)."""
    s = 4
    w, h, p = 16, 18, 8
    big = np.zeros(((h + 2 * p) * s, (w + 2 * p) * s), np.uint8)
    pts = np.int32([[p, p], [p + w, p], [p + w, p + h * 0.6], [p + w / 2, p + h], [p, p + h * 0.6]]) * s
    cv2.fillPoly(big, [pts], 255, cv2.LINE_AA)
    m = cv2.resize(big, (w + 2 * p, h + 2 * p), interpolation=cv2.INTER_AREA).astype(np.float32) / 255.0
    return ro(K.glow(solid(m, C('AMBER', 1.2)), C('GOLD'), sigmas=(3, 8), strength=0.5))


def dashed(cv, x, y0, y1, op, dash=8.0, gap=6.0, th=2.0, col=None, u=1.0):
    col = C('AMBER', 1.15) if col is None else col
    yy = y0
    yend = y0 + (y1 - y0) * u
    while yy < yend:
        _vbar(cv, x, yy, min(yy + dash, yend), th, col, op)
        yy += dash + gap


@functools.lru_cache(maxsize=4)
def _edge_glow(h):
    line = np.zeros((int(h), 3, 4), np.float32)
    line[..., :3] = C('AMBER', 1.4)
    line[..., 3] = 1.0
    return ro(K.glow(line, C('FLAME'), sigmas=(3, 9, 24), strength=1.2, include=False))


def contact(cv, st, rect, op):
    """f800-f816: the clip edges at the cut glow FLAME, edit-point brackets ] [ on V1."""
    k = st['contact'] * op
    if k <= 1e-3:
        return
    for name in ('V2', 'V1', 'A1'):
        y0, y1 = lane_rect(name, st['u12'])
        dy = rect[1] - _lerp(PANEL_N[1], PANEL_P[1], st['u12'])
        y0, y1 = y0 + dy, y1 + dy
        g = _edge_glow(round(y1 - y0))
        K.draw(cv, g, CUT_X, (y0 + y1) / 2.0, opacity=k, mode='add')
        if name == 'V1':
            bw, th = 14.0, 4.0
            for sgn in (-1, 1):
                xe = CUT_X + sgn * 5.0
                _vbar(cv, xe, y0 + 2, y1 - 2, th, C('FLAME', 1.4), k)
                _hbar(cv, min(xe, xe - sgn * bw), max(xe, xe - sgn * bw), y0 + 2 + th / 2, th, C('FLAME', 1.4), k)
                _hbar(cv, min(xe, xe - sgn * bw), max(xe, xe - sgn * bw), y1 - 2 - th / 2, th, C('FLAME', 1.4), k)


# --------------------------------------------------------------------------------------------------- pencil-playhead
def pencil_playhead(cv, st, morph):
    key, shadow, top, tip = pencil_sprites()
    s = PEN_LEN / max(1.0, tip[1] - top[1])
    x, rot = st['pen_x'], st['pen_rot']
    an = (top[0] / key.shape[1], top[1] / key.shape[0])
    y_top = PEN_TOP_Y
    if morph < 1.0:                                       # wipe in top -> bottom (feathered, hot scan edge)
        y_w = _lerp(y_top - 8.0, y_top + PEN_LEN + 12.0, morph)
        rows = int(max(0, min(key.shape[0], top[1] + (y_w - y_top) / s)))
        if rows <= 2:
            return
        fe = int(24 / s)
        kc = np.array(key[:rows], copy=True)
        sc = np.array(shadow[:rows], copy=True)
        r0 = max(0, rows - fe)
        ramp = np.linspace(1.0, 0.0, rows - r0, dtype=np.float32)[:, None, None]
        kc[r0:] *= ramp
        sc[r0:] *= ramp
        K.draw(cv, ro(sc), x + 10, y_top + 14, scale=s, anchor=an, opacity=0.35)
        K.draw(cv, ro(kc), x, y_top, scale=s, anchor=an)
        scan = _scan_spr()
        K.draw(cv, scan, x, y_w, opacity=0.9 * (1.0 - morph) ** 0.5, mode='add')
        return
    K.draw(cv, shadow, x + 10, y_top + 14, scale=s, rot=rot, anchor=an, opacity=0.35)
    K.draw(cv, key, x, y_top, scale=s, rot=rot, anchor=an)


@functools.lru_cache(maxsize=1)
def _scan_spr():
    line = np.zeros((3, 60, 4), np.float32)
    xs = np.linspace(-1, 1, 60, dtype=np.float32)
    a = np.clip(1 - xs ** 2, 0, 1)
    line[..., :3] = (C('AMBER', 1.6) * a[:, None])[None]
    line[..., 3] = a[None]
    return ro(K.glow(line, C('FLAME'), sigmas=(4, 12), strength=1.0, include=True))


# --------------------------------------------------------------------------------------------------- NLE draw
def nle(cv, t, media=None):
    """S10-S13 glass NLE onto cv for f576-f909 (valid into the D2 window). media(src_t) -> R1 frame (1080x1920
    linear RGBA); default media_r1 (Blender hub_loop, stand-in until it is rendered). Returns cv."""
    if t < F(576) - HALF:
        return cv
    media = media or media_r1
    st = state(t)
    # background (always under the shrinking frame)
    cv[...] = nle_bg()
    # timeline panel group
    pin = st['panel_in']
    slide = 150.0 * (1.0 - pin)
    rect = panel_rect(st['u12'], slide)
    op = ease('inout_sine', (t * FPS - 584) / 12.0)
    if op > 1e-3:
        panel(cv, rect, op)
        lanes(cv, st, rect, op)
        # cut line + ruler flag
        if st['cut']:
            ry0, ry1 = lane_rect('ruler', st['u12'])
            dy = rect[1] - _lerp(PANEL_N[1], PANEL_P[1], st['u12'])
            u = ease('out_cubic', (t - F(664)) / F(4))
            dashed(cv, CUT_X, ry1 + dy + 2, rect[3] - 12, op * 0.9, u=u, th=2.0 if st['u12'] < 0.5 else 3.0)
            fs = _lerp(1.0, 1.5, st['u12'])
            K.draw(cv, _flag(), CUT_X, ry0 + dy + 3, scale=fs * st['cut_pop'], anchor=(0.5, 0.18), opacity=op)
        contact(cv, st, rect, op)
        # playhead line / pencil
        ry0, ry1 = lane_rect('ruler', st['u12'])
        dy = rect[1] - _lerp(PANEL_N[1], PANEL_P[1], st['u12'])
        morph = st['morph']
        if not st['pencil'] or morph < 1.0:
            wline = 4.0 * (1.0 - morph) if st['pencil'] else 4.0
            playhead(cv, st['x'], rect[1] + 2.0, rect[3] - 2.0, op, width=wline, head_y=ry1 + dy - 1.0,
                     head_op=1.0 - morph if st['pencil'] else 1.0)
        if st['pencil']:
            pencil_playhead(cv, st, morph)
    # viewer (on top of the panel while it slides up and out)
    viewer(cv, t, st, media)
    # CUT chip above the ruler
    if st['chip_op'] > 1e-3:
        _cut_chip().draw(cv, CUT_X, 1229.0 + (rect[1] - PANEL_N[1]), scale=st['cut_pop'], opacity=st['chip_op'])
    return cv


# =================================================================================================== prewarm + selftest
def prewarm():
    for txt, px in (('Pencil.', 250), ('khatam?', 240), ('Galat!', 200), ('Mil gaya!', 220), ('phans gayi!', 190),
                    ('Yahan.', 220)):
        key_parts(txt, px)
    for txt, stl, px in (('Play.', 'jw_caps_bold', 150), ('Phir se.', 'jw_caps_bold', 150),
                         ('Peeche.', 'jw_caps_bold', 140), ('Aage.', 'jw_caps_bold', 140)):
        caps_glyphs(txt, stl, px)
    for s, stl, px in (('REWIND BUTTON?', 'jw_caps', 86), ('BATTERY', 'jw_caps', 96), ('CASSETTE', 'jw_caps', 96),
                       ('Scrubbing toh', 'jw_body', 56)):
        tx(s, stl, px)
    house('SIRF', 'andaza.', 96, 220)
    house('PEHLA EDITING TOOL?', 'Pencil.', 74, 260)
    _tag_line2()
    captions().prewarm()
    outro()._settled_layer()
    nle_bg()
    viewer_card()
    _view_overlays()
    _media_shade()
    _panel_base()
    for name in ('ruler', 'V2', 'V1', 'A1'):
        lane_strip(name, 1.0, LANES_N[name][1] - LANES_N[name][0])
        lane_strip(name, SCALE_P, LANES_P[name][1] - LANES_P[name][0])
    _ph_line()
    _ph_head()
    _cut_chip()
    _flag()
    pencil_sprites()


def _zoom(img, s, cx, cy):
    M = np.float32([[s, 0, cx - s * cx], [0, s, cy - s * cy]])
    return cv2.warpAffine(np.ascontiguousarray(img), M, (K.W, K.H), flags=cv2.INTER_LINEAR,
                          borderMode=cv2.BORDER_REPLICATE)


def _full(fr):
    if fr.shape[:2] != (K.H, K.W):
        fr = cv2.resize(np.ascontiguousarray(fr), (K.W, K.H), interpolation=cv2.INTER_CUBIC)
    return np.array(fr, copy=True)


def _canvas_plate(t, hook='A'):
    """Selftest backdrop = the shot's Blender plate (final, else preview, else stand-in) with the SHOTS.md framing,
    so every caption is judged over the picture it will sit on."""
    f = int(math.floor(t * FPS + 1e-6))
    hub = hub_asset()
    if f < 64 and str(hook).upper() == 'B':
        name, idx, z = 'walkman_loop', 0, (1.0, 540, 1180)
    elif f < 64 or 256 <= f < 320 or f >= 896:
        name, idx, z = 'hub_loop', f % 16, (1.0, 540, 960)
    elif f < 128 or 320 <= f < 384:
        name, idx, z = 'walkman_loop', f % 8, (1.0, 540, 960)
    elif f < 192:
        name, idx, z = 'hub_loop', f % 16, (1.43, 560, 1240)        # S3 crop on the pencil-hub contact
    elif f < 256:
        name, idx, z = 'label', 0, (1.05, 540, 900)
    elif f < 448:
        name, idx, z = 'walkman_loop', f % 8, (1.38, 495, 1110)     # S7 into the lid window
    elif f < 512:
        g = f - 448
        idx = 0 if g < 4 else (g - 4 if g < 10 else min(31, g - 4))
        name, z = 'walkman_eat', (1.0, 540, 960)
    else:
        name, idx, z = 'hub_rescue', (f - 512) // 2, (1.03, 540, 960)
    a = _asset(name)
    if a is None:
        fr = standin_hub(f % 16) if hub is None else hub.frame(f % 16)
    else:
        fr = a.frame(idx)
    img = _full(fr)
    if z[0] != 1.0:
        img = _zoom(img, *z)
    img[..., 3] = 1.0
    return img


def _finish(cv, t):
    try:
        import jawad_grade as G
        G.finish(cv, LOOK, t)
    except Exception:
        K.post(cv, LOOK, t)
    return cv


def _save(cv, t, name, guides=False):
    os.makedirs(OUT_DIR, exist_ok=True)
    cv = np.ascontiguousarray(cv)
    _finish(cv, t)
    img = K.to_srgb8(cv, t)
    if guides:
        img = np.array(img, copy=True)
        _guides(img)
    p = os.path.join(OUT_DIR, name + '.png')
    K.save_png(p, img)
    return p, img


def _guides(img):
    """Safe zones (x 70-1010, y 230-1480; x > 930 for y 1050-1700) and the 3:4 grid crop, drawn on an sRGB image."""
    c1 = (90, 200, 255)
    cv2.rectangle(img, (70, 230), (1010, 1480), c1, 1)
    cv2.rectangle(img, (930, 1050), (1079, 1700), (255, 90, 90), 1)
    cv2.line(img, (0, GRID_Y[0]), (1079, GRID_Y[0]), (120, 255, 120), 1)
    cv2.line(img, (0, GRID_Y[1]), (1079, GRID_Y[1]), (120, 255, 120), 1)


def _sheet(paths_imgs, name, cols=4, w=360):
    """Contact sheet at phone size (each frame w px wide) with frame labels."""
    ims = []
    for lab, img in paths_imgs:
        h = int(img.shape[0] * w / img.shape[1])
        sm = cv2.resize(img, (w, h), interpolation=cv2.INTER_AREA)
        sm = np.array(sm, copy=True)
        cv2.putText(sm, lab, (8, 22), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2, cv2.LINE_AA)
        ims.append(sm)
    rows = []
    for i in range(0, len(ims), cols):
        r = ims[i:i + cols]
        while len(r) < cols:
            r.append(np.zeros_like(ims[0]))
        rows.append(np.concatenate(r, axis=1))
    sheet = np.concatenate(rows, axis=0)
    p = os.path.join(OUT_DIR, name + '.png')
    K.save_png(p, sheet)
    return p


SAFE = (70, 230, 1010, 1480)


def ink_scan(step=1, thr=0.10):
    """Every-frame ink bbox of the lockups alone (hook A over f0-f1023 + hook B over its window) on an empty canvas:
    dict(bbox, max_x_in_1050_1700, violations=[frames]). Ink = premultiplied alpha > thr (halo cores included)."""
    X0 = Y0 = 10 ** 6
    X1 = Y1 = colx = -1
    bad = []
    jobs = [('A', f) for f in range(0, 1024, step)] + [('B', f) for f in range(0, TM['HB_out'][1] + 1, step)]
    for hook, f in jobs:
        cv = K.new_canvas()
        lockups(cv, F(f), hook)
        ys, xs = np.nonzero(cv[..., 3] > thr)
        if not len(xs):
            continue
        x0, x1, y0, y1 = xs.min(), xs.max(), ys.min(), ys.max()
        X0, X1, Y0, Y1 = min(X0, x0), max(X1, x1), min(Y0, y0), max(Y1, y1)
        band = xs[(ys >= 1050) & (ys <= 1700)]
        cx = band.max() if len(band) else -1
        colx = max(colx, cx)
        if x0 < SAFE[0] or x1 > SAFE[2] or y0 < SAFE[1] or y1 > SAFE[3] or cx > 930:
            bad.append('%s f%d (%d-%d, %d-%d)' % (hook, f, x0, x1, y0, y1))
    return dict(bbox=(int(X0), int(Y0), int(X1), int(Y1)), max_x_in_1050_1700=int(colx), violations=bad)


VO_MAP = (('HA', 'Pencil.', 'V1', 'HA_key', False), ('HB', 'khatam?', 'V1B', 'HB_key', False),
          ('L5', 'Sirf', 'V3', 'L5_in', False), ('L5', 'andaza.', 'V3', 'L5_key', False),
          ('L6', 'Play.', 'V4', 'L6_play', False), ('L6', 'Galat!', 'V4', 'L6_galat', False),
          ('L6', 'Phir', 'V4', 'L6_phir', False), ('L7', 'Mil', 'V5', 'L7_in', False),
          ('L9', 'Cassette', 'V6', 'L9_in', True), ('L9', 'phans', 'V6', 'L9_key', True),
          ('L14', 'Pehla', 'V11', 'L14_in', True), ('L14', 'Pencil.', 'V11', 'L14_key', False),
          ('L15', 'Scrubbing', 'V12', 'L15_l1', False), ('L15', 'cassette', 'V12', 'L15_l2', False))


def vo_alignment(hook=None):
    """Rows (lockup, word, ui frame, VO onset frame, delta, verdict): a designed word must land 0-2 f before its VO
    onset (or 1 f after), unless it is a structural beat that stays (the re-hook)."""
    rows = []
    for h in ((hook,) if hook else ('A', 'B')):
        vo = _vo_words(h) or []
        for lid, word, vline, key, structural in VO_MAP:
            if (lid == 'HA' and h == 'B') or (lid == 'HB' and h == 'A'):
                continue
            ws = [w for w in vo if w.get('line') == vline and w['word'] == word]
            if not ws:
                continue
            vf = ws[0]['start'] * FPS
            d = TM[key] - vf
            lead = -3.0 if lid == 'HA' else 0.0                # HA: the hit leads the word by 0.1 s (SOUND)
            ok = 'structural (stays)' if structural else ('OK' if -2.5 <= d - lead <= 1.0 else 'CHECK')
            rows.append((lid + h if lid in ('HA', 'HB') else lid, word, TM[key], vf, d, ok))
    return rows


def block_check(hook='A'):
    """Snake chunks overlapping a lockup window or the drop-out (> 1 frame) -> list of strings (empty = OK)."""
    issues = []
    wins = dict(lockup_windows(hook))
    wins['dropout'] = DROPOUT
    for ch in captions(hook).chunks:
        for k, (a, b) in wins.items():
            ov = min(ch.t_exit1, F(b + 1)) - max(ch.t_in, F(a))
            if ov > 1.0 / FPS + 1e-6:
                issues.append('%r f%.0f-%.0f overlaps %s by %.0f f' % (ch.text, ch.t_in * FPS, ch.t_exit1 * FPS, k,
                                                                    ov * FPS))
    return issues


def selftest(which=None):
    import time
    os.makedirs(OUT_DIR, exist_ok=True)
    out = []
    t0 = time.perf_counter()
    prewarm()
    print('prewarm %.1f s' % (time.perf_counter() - t0))
    want = set(which or ['lockups', 'snake', 'nle', 'outro', 'cover', 'pencil'])

    if 'lockups' in want:
        T_ = TM
        frames = [('HA', 'A', (2, T_['HA_key'] + 1, T_['HA_key'] + 6, T_['HA_ul'][1] + 2, T_['HA_out'][0] + 3)),
                  ('HB', 'B', (T_['HB_key'] + 1, T_['HB_ul'][1])),
                  ('L5', 'A', (T_['L5_key'] - 4, T_['L5_key'] + 30)),
                  ('L6', 'A', (T_['L6_play'] + 2, T_['L6_galat'] + 3, T_['L6_phir'] + 4, T_['L6_out'][0] + 1)),
                  ('L7', 'A', (T_['L7_in'] + 2, T_['L7_in'] + 18)),
                  ('L9', 'A', (T_['L9_in'] + 8, T_['L9_key'] + 1, T_['L9_key'] + 6, T_['L9_key'] + 26)),
                  ('L12', 'A', tuple(f + 1 for f in T_['L12']) + (T_['L12'][-1] + 16,)),
                  ('L14', 'A', (T_['L14_in'] + 8, T_['L14_key'] + 2, T_['L15_l2'] + 14, T_['L15_out'][0] - 2,
                                T_['L15_out'][0] + 3))]
        sheet = []
        for lab, hook, fs in frames:
            for f in fs:
                t = F(f)
                cv = _canvas_plate(t, hook) if f < 576 or f >= 896 else np.array(nle_bg(), copy=True)
                if 576 <= f < 896:
                    nle(cv, t)
                if f >= 896:
                    outro().draw(cv, t, T_END)
                lockups(cv, t, hook)
                p, img = _save(cv, t, 'lockup_%s_f%03d' % (lab, f), guides=False)
                sheet.append(('%s f%d' % (lab, f), img))
                out.append(p)
        out.append(_sheet(sheet, 'sheet_lockups', cols=5))
        print('ink scan (lockups, every frame):', ink_scan())
        print('VO alignment:')
        for row in vo_alignment():
            print('  %-8s %-10s ui f%-4d vo f%6.1f  d %+5.1f f  %s' % row)

    if 'snake' in want:
        cap = captions()
        issues = cap.check()
        print('snake check:', issues or 'OK')
        print('blocks check (snake vs lockups / outro text):', block_check() or 'OK')
        sheet = []
        for r in cap.report():
            t = r['t_in'] + 0.45 + 0.25 * max(0.0, r['t_exit0'] - r['t_in'] - 0.45)
            f = int(round(t * FPS))
            cv = _canvas_plate(t) if f < 576 else np.array(nle_bg(), copy=True)
            if f >= 576:
                nle(cv, t)
            cap.draw(cv, t)
            p, img = _save(cv, t, 'snake_f%03d' % f, guides=True)
            sheet.append(('f%d %s' % (f, r['text']), img))
            print('  f%4d-%4d  %-28s scale %.2f y %.0f bbox %s %s' % (round(r['t_in'] * 30), round(r['t_exit1'] * 30),
                                                                      r['text'], r['scale'], r['y'], r['bbox'],
                                                                      r['issues'] or ''))
        out.append(_sheet(sheet, 'sheet_snake', cols=4))
        cap.save_srt(os.path.join(OUT_DIR, 'snake_captions.srt'))

    if 'nle' in want:
        sheet = []
        L12, sn = TM['L12'], TM['NLE_snap']
        for f in (580, 588, 600, 625, L12[0] + 3, L12[1] + 3, L12[3] + 2, 690, 712, 724, 740, 756, 762, 785,
                  sn + 2, sn + 10, 860, 890):
            t = F(f)
            tm = time.perf_counter()
            cv = np.array(nle_bg(), copy=True)
            nle(cv, t)
            dt = (time.perf_counter() - tm) * 1e3
            if f >= 588:
                captions().draw(cv, t)
                lockups(cv, t)
            p, img = _save(cv, t, 'nle_f%03d' % f)
            sheet.append(('f%d %.0fms' % (f, dt), img))
            out.append(p)
        out.append(_sheet(sheet, 'sheet_nle', cols=6))

    if 'outro' in want:
        card = outro()
        sheet = []
        for f in (900, 940, 980, 1015):
            t = F(f)
            cv = _canvas_plate(t)
            card.draw(cv, t, T_END)
            p, img = _save(cv, t, 'outro_f%04d' % f, guides=True)
            sheet.append(('f%d' % f, img))
            out.append(p)
        out.append(_sheet(sheet, 'sheet_outro', cols=4))
        print('outro boxes:', {k: tuple(round(v) for v in b) for k, b in card.boxes().items()})

    if 'cover' in want:
        a = _asset('hub_cover')
        cv = np.array(a.frame(0), copy=True) if a is not None else _canvas_plate(0.0)
        cover(cv)
        p, img = _save(cv, 0.0, 'cover')
        out.append(p)
        g = grid_crop(img)
        pg = os.path.join(OUT_DIR, 'cover_grid_3x4.png')
        K.save_png(pg, np.ascontiguousarray(g))
        out.append(pg)
        img2 = np.array(img, copy=True)
        _guides(img2)
        pg2 = os.path.join(OUT_DIR, 'cover_guides.png')
        K.save_png(pg2, img2)
        out.append(pg2)

    if 'pencil' in want:
        key, shadow, top, tip = pencil_sprites()
        cv = np.array(nle_bg(), copy=True)
        K.draw(cv, shadow, 330 + 10, 120 + 14, anchor=(top[0] / key.shape[1], top[1] / key.shape[0]), opacity=0.35)
        K.draw(cv, key, 330, 120, anchor=(top[0] / key.shape[1], top[1] / key.shape[0]))
        # macro crops at 3x: eraser + ferrule, dents + HB, cone
        for i, (y0, label) in enumerate(((0, 'eraser / ferrule'), (180, 'dents / HB'), (1280, 'cone'))):
            crop = key[max(0, int(top[1] + y0 - 10)):int(top[1] + y0 + 230)]
            K.draw(cv, crop, 760, 190 + i * 590, scale=2.0, anchor=(0.5, 0.0))
            tx(label, 'jw_mono', 28, fill='ASH').draw(cv, 760, 160 + i * 590)
        p, img = _save(cv, 0.0, 'pencil')
        out.append(p)

    for p in out:
        print('->', p)
    return out


# VO-led defaults: follow the latest measured VO (env PSR_UI_TIMING=script keeps the text-led plan, =static the table)
_MODE = os.environ.get('PSR_UI_TIMING', 'vo')
if _MODE == 'script':
    TM.update(TIMING_SCRIPT)
elif _MODE == 'vo':
    try:
        TM.update(derive_vo_timing())
    except Exception as _e:                              # never break a render over the VO words: keep the table
        print('pencil_se_rewind_ui: VO timing not derived (%s); static TIMING_VO' % _e, file=sys.stderr)


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] in ('selftest', '--selftest'):
        selftest(sys.argv[2:] or None)
    else:
        print(__doc__)
