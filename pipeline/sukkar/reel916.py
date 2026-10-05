"""Dr. Sukkar hero reel, 9:16 cut (1080x1920).

- cold open: the 12 flash cuts full screen in black and white
- on-camera lines: B-roll on top, the speaker below, joined by a soft gradient (two-camera interview:
  the frontal camera, and the side camera at every dialogue edit so no jump cut shows)
- voiceover lines (C8951, no synced picture): full-screen B-roll
Same dialogue timeline as the 4:3 cut, so the v3 audio (clean dialogue + SFX) lines up unchanged.

python3 reel916.py --plan | --still 1.0,5.0 | --video
"""
import math
import os
import subprocess
import sys
import time

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

_argv, sys.argv = sys.argv, [sys.argv[0]]
import reel_sukkar as R          # dialogue timeline (T, BITES), clip paths and LUTs
sys.argv = _argv
import engine916 as E

OUT = os.environ.get("REEL_OUT", "out")
os.makedirs(OUT, exist_ok=True)
T, BITES, H_MINUS_V = R.T, R.BITES, R.H_MINUS_V
OPEN_FRAMES, TOTAL, END_HOLD, FADE, CARD = R.OPEN_FRAMES, R.TOTAL, R.END_HOLD, R.FADE, R.CARD

BW = dict(mix=(0.34, 0.50, 0.16), contrast=1.2, pivot=0.40)


def B(clip, t, view, zoom=(1.0, 1.05), pan=((0, 0), (0, 0)), anchor=None, **kw):
    p = R.clip_path(clip)
    return dict(kind="broll", src=p, lut=R.lut(clip), t=t, view=view, zoom=zoom, pan=pan, anchor=anchor,
                rng=("tv" if p.endswith(".mov") else "pc"), label=f"{clip}@{t}", **kw)


FULL = (1080, 1920, 2160)      # whole vertical frame


# ------------------------------------------------------------------ main picture track
TL = []
open_specs = [
    B("C9010", 1.5, (1080, 2400, 1620), zoom=(1.0, 1.06)),                 # gloved hands + instruments
    B("C9015", 3.0, (1080, 1650, 1700), zoom=(1.05, 1.0)),                 # THE SUKE, loupes
    B("C8891", 9.0, (1080, 1500, 1500), zoom=(1.0, 1.06)),                 # instruments + implant sizer
    B("C8899", 1.0, FULL, zoom=(1.0, 1.05), flash_in=2),                    # OR ceiling light
    B("C8879", 4.0, (1080, 1550, 1700), zoom=(1.05, 1.0)),                 # IV drip
    B("C8911", 4.0, (1080, 1900, 1800), zoom=(1.0, 1.05)),                 # monitor
    B("C8875", 25.0, (1080, 2450, 1500), zoom=(1.0, 1.06)),                # tray
    B("C8902", 4.0, FULL, zoom=(1.0, 1.05), flash_in=2),                    # low angle under the OR lamp
    B("C9010", 3.3, (1080, 2400, 1620), zoom=(1.05, 1.0)),                 # hands
    B("C8905", 6.7, FULL, zoom=(1.0, 1.05)),                                # profile, loupes
    B("C8886", 3.9, (1080, 1650, 1800), zoom=(1.0, 1.05)),                 # monitor waveforms
    B("C8890", 27.3, FULL, zoom=(1.0, 1.06), flash_out=3),                  # drape movement
]
fr = 0
for n, spec in zip(OPEN_FRAMES, open_specs):
    fr += n
    spec["bw"] = BW
    TL.append((fr / E.FPS, spec, ("cut", 0)))
OPEN = fr / E.FPS

# speaker panel on/off (seconds): on-camera stretches of sections 1-3
PANEL = [(3.903, 4.40, 14.62, 14.86), (15.70, 16.05, 20.20, 20.45)]   # (in start, in end, out start, out end)

TOP_ANCHOR = (540, 560)
# section 1 (the beat is full screen, the panel rises on the first on-camera words)
TL.append((T["b1"] + 3.00, B("C8893", 25.74, (1080, 1650, 1500), zoom=(1.0, 1.06), anchor=TOP_ANCHOR), ("dip", 6)))
TL.append((R.T_P3 + 0.06, B("C9016", 7.0, FULL, zoom=(1.0, 1.08), anchor=(540, 420)), ("dissolve", 12)))
# section 2
TL.append((T["b2a"] + R.bdur("b2a") + 0.38, B("C8907", 5.0, (1080, 2380, 2160), zoom=(1.0, 1.06), anchor=TOP_ANCHOR), ("zoomblur", 10)))
TL.append((T["b2b"] + 1.00, B("C9017", 12.9, (1080, 2230, 2160), zoom=(1.0, 1.06), anchor=TOP_ANCHOR), ("zoomblur", 10)))
TL.append((T["b2b"] + R.bdur("b2b") + 0.42, B("C9019", 6.0, (1080, 1950, 1500), zoom=(1.0, 1.05)), ("cut", 0)))
TL.append((T["b3"], B("C8894", 13.0, (1080, 1750, 1900), zoom=(1.0, 1.04)), ("cut", 0)))
# section 3
TL.append((R.T_B3_P2 + 0.02, B("C8912", 16.5, (1080, 2240, 1800), zoom=(1.0, 1.05), anchor=TOP_ANCHOR), ("zoomblur", 8)))
mont = [(0.55, B("C8894", 19.1, (1080, 2850, 2160), zoom=(1.0, 1.06), anchor=TOP_ANCHOR)),
        (0.50, B("C9017", 17.1, (1080, 2230, 2160), zoom=(1.06, 1.0), anchor=TOP_ANCHOR)),
        (0.50, B("C9019", 12.4, (1080, 2950, 1620), zoom=(1.0, 1.06), anchor=TOP_ANCHOR)),
        (0.55, B("C8893", 46.0, (1080, 1650, 1500), zoom=(1.0, 1.06), anchor=TOP_ANCHOR)),
        (0.40, B("C8999", 41.8, (1080, 2000, 1800), zoom=(1.06, 1.0))),
        (0.38, B("C9017", 19.6, FULL, zoom=(1.0, 1.06))),
        (0.35, B("C9019", 9.4, (1080, 1900, 1500), zoom=(1.0, 1.08)))]
tt = R.T_B3_P2 + 0.02
for i, (d, spec) in enumerate(mont):
    tt += d
    TL.append((tt, spec, ("whip", 6) if i == 0 else ("cut", 0)))
TL.append((T["b4"] - 0.20, B("C8894", 22.0, FULL, zoom=(1.0, 1.08)), ("cut", 0)))
# section 4 (voiceover): the facility, full screen
TL.append((T["b4"] + 3.25, B("C8956", 20.8, FULL, zoom=(1.0, 1.05)), ("flash", 14)))        # exterior + sign
TL.append((T["b4"] + 6.05, B("C8955", 2.6, FULL, zoom=(1.0, 1.04)), ("dissolve", 12)))       # atrium
TL.append((T["b4"] + 8.85, B("C9031", 0.6, FULL, zoom=(1.0, 1.04)), ("dissolve", 12)))       # staff, room
TL.append((T["b4"] + 10.60, B("C8894", 25.85, FULL, zoom=(1.0, 1.04)), ("dissolve", 10)))    # other doctors
TL.append((T["b5"], B("C8955", 6.9, FULL, zoom=(1.0, 1.04)), ("dissolve", 10)))             # lobby from above
# section 5: back into the OR, slower
TL.append((T["b5"] + 1.85, B("C8999", 3.9, FULL, zoom=(1.0, 1.05)), ("dip", 14)))           # gloving
TL.append((T["b6"], B("C9028", 4.8, FULL, zoom=(1.0, 1.05), reverse=True), ("dissolve", 12)))  # mask on
# section 6: hero, let it breathe
TL.append((END_HOLD + FADE, B("C9017", 6.2, FULL, zoom=(1.0, 1.10), anchor=(540, 700)), ("dissolve", 10)))
TL.append((TOTAL, dict(kind="card"), ("fadeblack", E.F(FADE) * 2)))


# ------------------------------------------------------------------ speaker track (two cameras)
FRONT = {"b1": ("v916/srcF/C8948 (1).mov", 0.0), "b2a": ("src/TH_384.mov", 384.0),
         "b2b": ("src/TH_384.mov", 384.0), "b3": ("src/TH_440.mov", 440.0)}
SIDE = "v916/srcV/C8950 V2 (1).mp4"
FACE = (560, 1215)          # output point of his face in the panel (zoom anchor)


def spk(angle, k, p, tl_start, close=False):
    off = R.piece_offsets(k)[p]
    v = BITES[k][p][1] + (tl_start - T[k] - off)          # vertical-camera time at tl_start
    if angle == "front":
        path, base = FRONT[k]
        t, view, size = v + H_MINUS_V - base, (2080, 160, 2160), (3840, 2160)
    else:
        path, t, view, size = SIDE, v, (1080, 952, 2160), (2160, 3840)
    zoom = (1.20, 1.24) if close else (1.0, 1.035)
    return dict(kind="spk", src=path, t=t, view=view, zoom=zoom, anchor=FACE, src_size=size,
                label=f"{angle}-{k}.{p}{'-close' if close else ''}", pan=((0, 0), (0, 0)))


P1, P2 = PANEL
TS = [
    (P1[0], None, ("cut", 0)),
    (T["b1"] + R.piece_offsets("b1")[2], spk("front", "b1", 1, P1[0]), ("cut", 0)),
    (8.62, spk("side", "b1", 2, T["b1"] + R.piece_offsets("b1")[2]), ("cut", 0)),
    (T["b2a"] + R.piece_offsets("b2a")[1], spk("front", "b2a", 0, 8.62), ("cut", 0)),
    (T["b2a"] + R.piece_offsets("b2a")[2], spk("side", "b2a", 1, T["b2a"] + R.piece_offsets("b2a")[1]), ("cut", 0)),
    (13.08, spk("front", "b2a", 2, T["b2a"] + R.piece_offsets("b2a")[2]), ("cut", 0)),
    (P1[3], spk("side", "b2b", 0, 13.08), ("cut", 0)),
    (P2[0], None, ("cut", 0)),
    (T["b3"] + R.piece_offsets("b3")[1], spk("front", "b3", 0, P2[0], close=True), ("cut", 0)),
    (T["b3"] + R.piece_offsets("b3")[2], spk("front", "b3", 1, T["b3"] + R.piece_offsets("b3")[1], close=True), ("cut", 0)),
    (P2[3], spk("side", "b3", 2, T["b3"] + R.piece_offsets("b3")[2]), ("cut", 0)),
]


def panel_alpha(t):
    for a0, a1, b0, b1 in PANEL:
        if a0 <= t < a1:
            return E.ease_out((t - a0) / (a1 - a0))
        if a1 <= t < b0:
            return 1.0
        if b0 <= t < b1:
            return 1 - E.ease_io((t - b0) / (b1 - b0))
    return 0.0


G0, G1 = 0.45, 0.61         # gradient: B-roll opaque above G0*H, gone below G1*H
_grad = None


def gradient():
    global _grad
    if _grad is None:
        y = (np.arange(E.H, dtype=np.float32) + 0.5) / E.H
        u = np.clip((y - G0) / (G1 - G0), 0, 1)
        g = 1 - (u * u * (3 - 2 * u))
        _grad = g[:, None, None].astype(np.float32)
    return _grad


# ------------------------------------------------------------------ shots
def make_shot(spec, start_s, end_s, visible=(0.0, 1.0)):
    if spec is None or spec["kind"] == "card":
        return None
    kw = {k: v for k, v in spec.items() if k in ("flash_in", "flash_out", "gain", "sat", "bw", "anchor")}
    s = E.Shot(spec["src"], spec["t"], end_s - start_s, spec["view"], kind=spec["kind"], lut=spec.get("lut"),
               zoom=spec["zoom"], pan=spec.get("pan", ((0, 0), (0, 0))), label=spec["label"],
               rng=spec.get("rng", "pc"), src_size=spec.get("src_size", (2160, 3840)), visible=visible, **kw)
    s.reverse = spec.get("reverse", False)
    return s


def build(track, top=False):
    shots = []
    prev = 0.0
    for end_s, spec, trans in track:
        f0, f1 = E.F(prev), E.F(end_s)
        vis = (0.38, 1.0) if spec is not None and spec.get("kind") == "spk" else (0.0, 1.0)
        sh = make_shot(spec, prev, end_s, vis)
        if sh is not None:
            sh.start, sh.n = f0, f1 - f0
        shots.append((sh, trans, f0, f1, spec))
        prev = end_s
    for i in range(1, len(shots)):
        kind, L = shots[i][1]
        if L and shots[i - 1][0] is not None:
            shots[i - 1][0].post = L - L // 2
        if L and shots[i][0] is not None:
            shots[i][0].pre = L // 2
    if top:
        # rows the viewer can see: only the top part while the panel is fully up for the whole shot
        for sh, trans, f0, f1, spec in shots:
            if sh is not None and sh.kind == "broll":
                hidden = all(panel_alpha((f + 0.5) / E.FPS) >= 0.999 for f in range(f0 - sh.pre, f1 + sh.post))
                sh.visible = (0.0, G1 + 0.02) if hidden else (0.0, 1.0)
    return shots


def check_views(shots):
    """Warn if a shot that can be seen full screen has its window run past the source edge."""
    for sh, trans, f0, f1, spec in shots:
        if sh is None or sh.visible[1] < 0.99:
            continue
        cx, cy, cw = sh.view
        sw, shh = sh.src_size
        ch = cw * 16 / 9
        if cx - cw / 2 < -1 or cx + cw / 2 > sw + 1 or cy - ch / 2 < -1 or cy + ch / 2 > shh + 1:
            print(f"  ! {sh.label}: full-screen window outside the source "
                  f"(x {cx - cw / 2:.0f}..{cx + cw / 2:.0f}, y {cy - ch / 2:.0f}..{cy + ch / 2:.0f})")


# ------------------------------------------------------------------ end card
def tracked(draw, xy, text, font, fill, tracking):
    x, y = xy
    for ch in text:
        draw.text((x, y), ch, font=font, fill=fill)
        x += font.getlength(ch) + tracking


def tracked_width(text, font, tracking):
    return sum(font.getlength(c) for c in text) + tracking * (len(text) - 1)


_card = None


def card_layers():
    Wc, Hc = E.W, E.H
    title = ImageFont.truetype("fonts/Montserrat-600.ttf", int(0.082 * Wc))
    sub = ImageFont.truetype("fonts/Montserrat-500.ttf", int(0.036 * Wc))
    t_track, s_track = 0.20 * title.size, 0.55 * sub.size
    L1, L2 = Image.new("L", (Wc, Hc), 0), Image.new("L", (Wc, Hc), 0)
    t_text, s_text = "DR. SUKKAR", "BEHIND THE MASK"
    tw, sw = tracked_width(t_text, title, t_track), tracked_width(s_text, sub, s_track)
    asc, _ = title.getmetrics()
    cy = Hc * 0.48
    tracked(ImageDraw.Draw(L1), ((Wc - tw) / 2, cy - asc), t_text, title, 255, t_track)
    tracked(ImageDraw.Draw(L2), ((Wc - sw) / 2, cy + 0.030 * Hc), s_text, sub, 236, s_track)
    return np.asarray(L1, np.float32) / 255, np.asarray(L2, np.float32) / 255


def card_frame(tc):
    global _card
    if _card is None:
        _card = card_layers()
    L1, L2 = _card
    a1 = E.ease_io((tc - 0.15) / 0.9)
    a2 = E.ease_io((tc - 0.75) / 0.9)
    out = np.zeros((E.H, E.W, 3), np.float32)
    for L, a, lift, blur0 in ((L1, a1, 0.007, 10), (L2, a2, 0.005, 6)):
        if a <= 0:
            continue
        m = L
        bl = blur0 * (1 - a) * E.SCALE
        if bl > 0.3:
            m = cv2.GaussianBlur(m, (0, 0), bl)
        M = np.array([[1, 0, 0], [0, 1, lift * E.H * (1 - a)]], np.float32)
        m = cv2.warpAffine(m, M, (E.W, E.H))
        out += (m * a)[..., None] * np.array([0.97, 0.98, 1.0], np.float32)
    out *= 1 - E.ease_io((tc - (CARD - 0.35)) / 0.35)
    return out


# ------------------------------------------------------------------ render
def finish(img, f):
    t = f / E.FPS
    if t < OPEN:
        # black and white cold open: a touch of gate flicker, heavier grain, deeper vignette
        flick = 1 + 0.018 * math.sin(f * 2.1) * math.sin(f * 0.77 + 1.3)
        img = E.bloom(img * flick, strength=0.12, sigma=18, thresh=0.70)
        img = E.vignette(img, 0.42)
        img = E.grain(img, 0.024)
        y = img.mean(axis=2, keepdims=True)          # keep the grain monochrome
        return np.clip(np.repeat(y, 3, axis=2), 0, 1)
    img = E.halation(img, strength=0.05)
    img = E.bloom(img, strength=0.09, sigma=16, thresh=0.74)
    img = E.vignette(img, 0.30)
    img = E.grain(img, 0.012)
    return np.clip(img, 0, 1)


class Track:
    def __init__(self, shots):
        self.shots = shots
        self.opened, self.active = set(), {}

    def step_open(self, f):
        for idx, (sh, trans, s0, s1, spec) in enumerate(self.shots):
            if sh is None or idx in self.opened:
                continue
            a0, a1 = sh.start - sh.pre, sh.start + sh.n + sh.post
            if a0 <= f < a1:
                sh.open(skip=f - a0)
                self.opened.add(idx)
                self.active[idx] = sh

    def render(self, f, card_start=None):
        shots = self.shots
        cur = next((i for i, (sh, tr, s0, s1, sp) in enumerate(shots) if s0 <= f < s1), None)
        used = set()
        if cur is None:
            return None, used

        def get(i, ez=1.0, ep=(0.0, 0.0)):
            sh = shots[i][0]
            if sh is None:
                if shots[i][4] is not None and shots[i][4].get("kind") == "card":
                    return card_frame((f - card_start) / E.FPS)
                return np.zeros((E.H, E.W, 3), np.float32)
            used.add(i)
            return sh.frame(f - sh.start, ez, ep)

        for b in (cur, cur + 1):
            if b <= 0 or b >= len(shots):
                continue
            kind, L = shots[b][1]
            if not L:
                continue
            b0 = shots[b][2]
            w0, w1 = b0 - L // 2, b0 + (L - L // 2)
            if w0 <= f < w1:
                u = (f - w0 + 0.5) / L
                img = E.transition(kind, lambda ez=1.0, ep=(0.0, 0.0): get(b - 1, ez, ep),
                                   lambda ez=1.0, ep=(0.0, 0.0): get(b, ez, ep), u, f / E.FPS)
                return img, used
        if shots[cur][0] is None and shots[cur][4] is None:
            return None, used
        return get(cur), used

    def advance_unused(self, used):
        for idx, sh in self.active.items():
            if idx not in used:
                sh.reader.read()

    def close_done(self, f):
        for idx in [i for i, sh in self.active.items() if f >= sh.start + sh.n + sh.post - 1]:
            self.active.pop(idx).close()

    def close_all(self):
        for sh in self.active.values():
            sh.close()


def render_frames(f0, f1, sink):
    A = Track(build(TL, top=True))
    S = Track(build(TS))
    check_views(A.shots)
    card_start = A.shots[-1][2]
    f1 = min(f1, E.F(TOTAL))
    grad = gradient()
    t_start = time.time()
    for f in range(f0, f1):
        A.step_open(f)
        S.step_open(f)
        img, used_a = A.render(f, card_start)
        pa = panel_alpha((f + 0.5) / E.FPS)
        used_s = set()
        if pa > 0.001:
            spk_img, used_s = S.render(f)
            if spk_img is not None:
                dy = (1 - pa) * 90 * E.SCALE                    # the panel rises into place
                if dy > 0.5:
                    M = np.array([[1, 0, 0], [0, 1, dy]], np.float32)
                    spk_img = cv2.warpAffine(spk_img, M, (E.W, E.H), borderMode=cv2.BORDER_REPLICATE)
                m = 1 - pa * (1 - grad)
                img = img * m + spk_img * (1 - m)
        A.advance_unused(used_a)
        S.advance_unused(used_s)
        is_card = A.shots[next(i for i, s in enumerate(A.shots) if s[2] <= f < s[3])][4].get("kind") == "card"
        out = np.clip(img, 0, 1) if is_card else finish(img, f)
        sink(f, out)
        A.close_done(f)
        S.close_done(f)
        if f % 96 == 0 and f1 - f0 > 1:
            print(f"  frame {f}/{f1}  {time.time() - t_start:.0f}s", flush=True)
    A.close_all()
    S.close_all()


def main():
    args = sys.argv[1:]
    if "--plan" in args:
        for name, track in (("picture", TL), ("speaker", TS)):
            print(name)
            prev = 0.0
            for end_s, spec, trans in track:
                lab = "-" if spec is None else spec.get("label", spec["kind"])
                extra = f" src t={spec['t']:.3f}" if spec is not None and "t" in spec else ""
                print(f"  {prev:6.2f}-{end_s:6.2f}  {lab:24s} {trans}{extra}")
                prev = end_s
        check_views(build(TL, top=True))
        return
    if "--still" in args:
        times = [float(x) for x in args[args.index("--still") + 1].split(",")]
        for x in times:
            f = E.F(x)
            got = {}
            render_frames(f, f + 1, lambda fi, img: got.setdefault(fi, img))
            cv2.imwrite(f"{OUT}/s916_{x:06.2f}.jpg", (got[f] * 255 + 0.5).astype(np.uint8), [cv2.IMWRITE_JPEG_QUALITY, 92])
        print("stills written")
        return
    tag = os.environ.get("REEL_TAG", "sukkar_916")
    vid = f"{OUT}/{tag}_video.mp4"
    enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "bgr24",
                            "-s", f"{E.W}x{E.H}", "-r", f"{E.FPS_NUM}/{E.FPS_DEN}", "-i", "-",
                            "-vf", "scale=out_color_matrix=bt709:out_range=tv,format=yuv420p",
                            "-c:v", "libx264", "-preset", os.environ.get("X264_PRESET", "slow"),
                            "-crf", os.environ.get("CRF", "15"), "-tune", "grain",
                            "-color_primaries", "bt709", "-color_trc", "bt709", "-colorspace", "bt709",
                            "-movflags", "+faststart", vid], stdin=subprocess.PIPE)
    f0 = E.F(float(os.environ.get("FROM", "0")))
    f1 = E.F(float(os.environ.get("TO", str(TOTAL))))

    def sink(f, img):
        enc.stdin.write((img * 255 + 0.5).astype(np.uint8).tobytes())

    render_frames(f0, f1, sink)
    enc.stdin.close()
    enc.wait()
    print("wrote", vid)


if __name__ == "__main__":
    main()
