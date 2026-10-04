"""Dr. Sukkar hero reel: timeline, picture render, audio mix, final encode.

python3 reel_sukkar.py [--preview] [--from SEC --to SEC] [--still SEC,SEC,...]
REEL_SCALE env var sets the render scale (0.5 for a quick preview).
"""
import json
import math
import os
import subprocess
import sys
import time

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

import audio as au
import engine as E
from bites_audio import assemble

OUT = os.environ.get("REEL_OUT", "out")
os.makedirs(OUT, exist_ok=True)
SRC = "src"
H_MINUS_V = 2.9645
BITES = json.load(open("tx/bites.json"))


def bdur(k):
    return sum(o - i for _, i, o in BITES[k])


def piece_offsets(k):
    acc, out = 0.0, []
    for _, i, o in BITES[k]:
        out.append(acc)
        acc += o - i
    return out


# ------------------------------------------------------------------ dialogue placement
OPEN_FRAMES = [5, 5, 4, 4, 5, 5, 4, 4, 4, 4, 4, 6]
OPEN = sum(OPEN_FRAMES) / E.FPS
SPACE = 1.0
T = {}
T["b1"] = OPEN + SPACE
T["b2a"] = T["b1"] + bdur("b1") + 0.70
T["b2b"] = T["b2a"] + bdur("b2a") + 0.62
T["b3"] = T["b2b"] + bdur("b2b") + 1.10
T["b4"] = T["b3"] + bdur("b3") + 1.55
T["b5"] = T["b4"] + bdur("b4") + 0.90
T["b6"] = T["b5"] + bdur("b5") + 0.30
END_HOLD = T["b6"] + bdur("b6") + 2.60
FADE = 0.80
CARD = 3.8
TOTAL = END_HOLD + FADE + CARD

p2a = piece_offsets("b2a")
T_P3 = T["b2a"] + p2a[2]                     # "plastic surgery, it's boundless" (on camera)
V_P3 = BITES["b2a"][2][1]
p3 = piece_offsets("b3")
V_B3 = BITES["b3"][0][1]                     # "We're always still learning" (on camera)
T_B3_P2 = T["b3"] + p3[1]


def lut(c):
    return f"luts/{c}.cube"


def B(clip, t, cy, cw=2160, cx=1080, zoom=(1.0, 1.05), pan=((0, 0), (0, 0)), **kw):
    return dict(kind="broll", src=f"{SRC}/{clip}.MP4", lut=lut(clip), t=t, crop=(cx, cy, cw),
                zoom=zoom, pan=pan, label=f"{clip}@{t}", **kw)


def TH(src_t, framing="medium", zoom=(1.0, 1.02), **kw):
    crop = (2000, 1080, 2880) if framing == "medium" else (2070, 1000, 1800)
    return dict(kind="th", src=f"{SRC}/C8948 (1).mov", lut=None, t=src_t, crop=crop, zoom=zoom,
                pan=((0, 0), (0, 0)), label=f"TH-{framing}@{src_t:.2f}", **kw)


# ------------------------------------------------------------------ picture timeline
# each entry: (end_time_seconds, shot_spec, transition_into (kind, frames))
TL = []
t = 0.0
open_specs = [
    B("C8999", 4.3, 1350, 1500, zoom=(1.0, 1.04)),                 # gloves
    B("C9017", 9.2, 1280, 1200, zoom=(1.04, 1.0)),                   # loupes / eyes
    B("C8894", 1.3, 2400, 1400, zoom=(1.0, 1.05)),                  # instruments + glove
    B("C9017", 0.5, 1350, 1300, cx=900, zoom=(1.0, 1.06), flash_in=2),        # headlight glare
    B("C9019", 3.4, 1600, 1400, zoom=(1.05, 1.0)),                  # hands + forceps
    B("C9028", 0.4, 1450, 1300, cx=600, zoom=(1.0, 1.04)),          # eye above mask
    B("C8894", 19.9, 2450, 1400, zoom=(1.0, 1.05)),                 # hand grabs instrument
    B("C8893", 15.9, 1350, 1300, zoom=(1.0, 1.05), flash_in=2),      # light glint
    B("C9019", 11.2, 2750, 1300, zoom=(1.05, 1.0)),                 # hemostat
    B("C8999", 43.8, 2200, 1500, zoom=(1.0, 1.05)),                 # instruments + pack
    B("C9017", 16.8, 1250, 1300, zoom=(1.0, 1.05)),                  # loupes
    B("C8893", 37.0, 1600, 1700, zoom=(1.0, 1.06), flash_out=3),     # movement
]
fr = 0
for n, spec in zip(OPEN_FRAMES, open_specs):
    fr += n
    TL.append((fr / E.FPS, spec, ("cut", 0)))

# space + section 1 (tight, intimate)
TL.append((T["b1"] + 0.66, B("C8893", 2.0, 760, 2160, zoom=(1.02, 1.10)), ("dip", 6)))          # IV drip, surgeon soft
TL.append((T["b1"] + 2.15, B("C9028", 0.15, 1450, 1500, cx=650, zoom=(1.0, 1.06)), ("dissolve", 10)))  # eye above mask
TL.append((T["b1"] + 3.80, B("C9019", 3.0, 1650, 1600, zoom=(1.0, 1.05)), ("dissolve", 10)))  # hands
TL.append((T["b1"] + bdur("b1") + 0.15, B("C8999", 10.4, 1500, 2000, zoom=(1.0, 1.05)), ("dissolve", 8)))  # implant prep
TL.append((T["b2a"] + p2a[1] + 0.25, B("C9017", 9.0, 1250, 1450, zoom=(1.0, 1.08)), ("dissolve", 8)))   # loupes tight
TL.append((T_P3 + 0.06, B("C8894", 15.4, 1450, 2160, zoom=(1.0, 1.05)), ("cut", 0)))              # him + observers
# section 2: interview reveal (lip sync), then him operating
th1_start = T_P3 + 0.06
TL.append((T["b2a"] + bdur("b2a") + 0.38, TH(V_P3 + H_MINUS_V + 0.06, "medium", zoom=(1.0, 1.03)), ("zoomblur", 10)))
TL.append((T["b2b"] + 1.00, B("C9017", 12.9, 1750, 2160, zoom=(1.0, 1.06)), ("zoomblur", 10)))     # operating
TL.append((T["b2b"] + bdur("b2b") + 0.42, B("C9019", 6.0, 2250, 1700, zoom=(1.0, 1.05)), ("cut", 0)))  # hands precision
TL.append((T["b3"], B("C8894", 13.0, 1450, 2160, zoom=(1.0, 1.04)), ("cut", 0)))                   # team
# section 3: close-up (lip sync), then the build
TL.append((T_B3_P2 + 0.02, TH(V_B3 + H_MINUS_V, "close", zoom=(1.0, 1.04)), ("zoomblur", 8)))
mont = [(0.55, B("C8894", 19.1, 2400, 1500, zoom=(1.0, 1.06))),
        (0.50, B("C9017", 17.1, 1250, 1300, zoom=(1.06, 1.0))),
        (0.50, B("C9019", 12.4, 2600, 1500, zoom=(1.0, 1.06))),
        (0.55, B("C8893", 46.0, 1650, 1800, zoom=(1.0, 1.06))),
        (0.40, B("C8999", 41.8, 2000, 1500, zoom=(1.06, 1.0))),
        (0.38, B("C9017", 19.6, 1200, 1700, zoom=(1.0, 1.06))),
        (0.35, B("C9019", 9.4, 2300, 1500, zoom=(1.0, 1.08)))]
tt = T_B3_P2 + 0.02
for i, (d, spec) in enumerate(mont):
    tt += d
    TL.append((tt, spec, ("whip", 6) if i == 0 else ("cut", 0)))
TL.append((T["b4"] - 0.20, B("C8894", 22.0, 2350, 1500, zoom=(1.0, 1.08)), ("cut", 0)))
# section 4: open up -- the facility
TL.append((T["b4"] + 3.25, B("C8956", 20.8, 1450, 2160, zoom=(1.0, 1.05)), ("flash", 14)))      # exterior + sign
TL.append((T["b4"] + 6.05, B("C8955", 2.6, 2150, 2160, zoom=(1.0, 1.04)), ("dissolve", 12)))     # atrium
TL.append((T["b4"] + 8.85, B("C9031", 0.6, 2350, 2160, zoom=(1.0, 1.04)), ("dissolve", 12)))     # staff, room
TL.append((T["b4"] + 10.60, B("C8894", 25.85, 1300, 2160, zoom=(1.0, 1.04)), ("dissolve", 10)))  # other doctors
TL.append((T["b5"], B("C8955", 6.9, 2000, 2160, zoom=(1.0, 1.04)), ("dissolve", 10)))           # lobby from above
# section 5: back into the OR, slower
TL.append((T["b5"] + 1.85, B("C8999", 3.9, 1300, 1900, zoom=(1.0, 1.05)), ("dip", 14)))         # gloving
TL.append((T["b6"], B("C9028", 4.8, 2000, 2160, cx=1080, zoom=(1.0, 1.05), reverse=True), ("dissolve", 12)))  # mask on
# section 6: hero, let it breathe
TL.append((END_HOLD + FADE, B("C9017", 6.2, 1500, 2160, zoom=(1.0, 1.10)), ("dissolve", 10)))
TL.append((TOTAL, dict(kind="card"), ("fadeblack", E.F(FADE) * 2)))


def make_shot(spec, start_s, end_s):
    if spec["kind"] == "card":
        return None
    kw = {k: v for k, v in spec.items() if k in ("flash_in", "flash_out", "gain", "sat")}
    s = E.Shot(spec["src"], spec["t"], end_s - start_s, spec["crop"], kind=spec["kind"], lut=spec["lut"],
               zoom=spec["zoom"], pan=spec["pan"], label=spec["label"], **kw)
    s.reverse = spec.get("reverse", False)
    return s


# ------------------------------------------------------------------ end card
FONT_DIR = "fonts"


def tracked(draw, xy, text, font, fill, tracking):
    x, y = xy
    for ch in text:
        draw.text((x, y), ch, font=font, fill=fill)
        x += font.getlength(ch) + tracking


def tracked_width(text, font, tracking):
    return sum(font.getlength(c) for c in text) + tracking * (len(text) - 1)


def card_layers():
    Wc, Hc = E.W, E.H
    title = ImageFont.truetype(f"{FONT_DIR}/Montserrat-600.ttf", int(0.078 * Hc))
    sub = ImageFont.truetype(f"{FONT_DIR}/Montserrat-500.ttf", int(0.031 * Hc))
    t_track, s_track = 0.20 * title.size, 0.55 * sub.size
    L1 = Image.new("L", (Wc, Hc), 0)
    L2 = Image.new("L", (Wc, Hc), 0)
    t_text, s_text = "DR. SUKKAR", "BEHIND THE MASK"
    tw = tracked_width(t_text, title, t_track)
    sw = tracked_width(s_text, sub, s_track)
    asc, desc = title.getmetrics()
    cy = Hc * 0.47
    tracked(ImageDraw.Draw(L1), ((Wc - tw) / 2, cy - asc), t_text, title, 255, t_track)
    tracked(ImageDraw.Draw(L2), ((Wc - sw) / 2, cy + 0.050 * Hc), s_text, sub, 236, s_track)
    return np.asarray(L1, np.float32) / 255, np.asarray(L2, np.float32) / 255


_card = None


def card_frame(tc):
    """tc: seconds since the card started."""
    global _card
    if _card is None:
        _card = card_layers()
    L1, L2 = _card
    a1 = E.ease_io((tc - 0.15) / 0.9)
    a2 = E.ease_io((tc - 0.75) / 0.9)
    out = np.zeros((E.H, E.W, 3), np.float32)
    for L, a, lift, blur0 in ((L1, a1, 0.012, 10), (L2, a2, 0.008, 6)):
        if a <= 0:
            continue
        # soft focus-in and a small upward settle
        m = L
        bl = blur0 * (1 - a) * E.SCALE
        if bl > 0.3:
            m = cv2.GaussianBlur(m, (0, 0), bl)
        dy = lift * E.H * (1 - a)
        M = np.array([[1, 0, 0], [0, 1, dy]], np.float32)
        m = cv2.warpAffine(m, M, (E.W, E.H))
        out += (m * a)[..., None] * np.array([0.97, 0.98, 1.0], np.float32)
    # gentle fade at the very end so the loop restarts from black
    out *= 1 - E.ease_io((tc - (CARD - 0.35)) / 0.35)
    return out


# ------------------------------------------------------------------ render picture
def build_shots():
    shots, starts = [], []
    prev_end = 0.0
    for end_s, spec, trans in TL:
        sh = make_shot(spec, prev_end, end_s)
        starts.append(prev_end)
        if sh is not None:
            sh.start = E.F(prev_end)
            sh.n = E.F(end_s) - sh.start
        shots.append((sh, trans, E.F(prev_end), E.F(end_s), spec))
        prev_end = end_s
    # transition handles
    for i in range(1, len(shots)):
        sh_b, (kind, L), b0, _, _ = shots[i]
        sh_a = shots[i - 1][0]
        if L and sh_a is not None:
            sh_a.post = L - L // 2
        if L and sh_b is not None:
            sh_b.pre = L // 2
    return shots


def open_reader(sh, skip=0):
    if getattr(sh, "reverse", False):
        # play the source stretch backwards; frame k of the window = source t - k/FPS
        sh.open(skip=0)
        sh.reader.close()
        total = sh.pre + sh.n + sh.post - skip
        t_end = sh.t - (skip - sh.pre) / E.FPS
        sh.reader = E.Reader(sh.src, t_end - total / E.FPS, total, sh.vf + ",reverse", (sh.ow, sh.oh),
                             dur=total / E.FPS + 0.5 / E.FPS)
    else:
        sh.open(skip=skip)


def finish(img):
    img = E.bloom(img, strength=0.10, sigma=16, thresh=0.72)
    img = E.vignette(img, 0.26)
    img = E.grain(img, 0.011)
    return np.clip(img, 0, 1)


def render_frames(f0, f1, sink, shots=None):
    shots = shots or build_shots()
    f1 = min(f1, E.F(TOTAL))
    card_start = shots[-1][2]
    opened, active = set(), {}
    t_start = time.time()
    for f in range(f0, f1):
        for idx, (sh, trans, s0, s1, spec) in enumerate(shots):
            if sh is None or idx in opened:
                continue
            a0, a1 = sh.start - sh.pre, sh.start + sh.n + sh.post
            if a0 <= f < a1:
                open_reader(sh, skip=f - a0)
                opened.add(idx)
                active[idx] = sh
        cur = next(i for i, (sh, tr, s0, s1, sp) in enumerate(shots) if s0 <= f < s1)
        used = set()

        def get(i, ez=1.0, ep=(0.0, 0.0)):
            sh = shots[i][0]
            if sh is None:
                return card_frame((f - card_start) / E.FPS)
            used.add(i)
            return sh.frame(f - sh.start, ez, ep)

        img = None
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
                break
        if img is None:
            img = get(cur)
        for idx, sh in active.items():
            if idx not in used:
                sh.reader.read()
        out = np.clip(img, 0, 1) if shots[cur][0] is None else finish(img)
        sink(f, out)
        for idx in [i for i, sh in active.items() if f >= sh.start + sh.n + sh.post - 1]:
            active.pop(idx).close()
        if f % 96 == 0 and f1 - f0 > 1:
            print(f"  frame {f}/{f1}  {time.time() - t_start:.0f}s", flush=True)
    for sh in active.values():
        sh.close()


# ------------------------------------------------------------------ audio
def dialogue_bus():
    bus = au.Bus(TOTAL)
    for k in ["b1", "b2a", "b2b", "b3", "b4", "b5", "b6"]:
        a = assemble([tuple(p) for p in BITES[k]], fout=0.05)
        bus.add(a, T[k])
    return bus


def nat_bus():
    """Natural OR sound from speech-free stretches only."""
    bus = au.Bus(TOTAL)

    def cue(clip, src_t, at, dur, gain_db, fin=0.08, fout=0.25):
        a = au.read(f"{SRC}/{clip}.MP4", src_t, dur)
        bus.add(au.fade(a, fin, fout), at, gain_db)

    # cold open: instrument clinks + OR room, a little forward (music will sit on top)
    cue("C8894", 0.2, 0.0, OPEN + 0.3, -8, fin=0.02, fout=0.3)
    cue("C9019", 2.0, 0.0, OPEN + 0.3, -6, fin=0.02, fout=0.3)
    # OR room bed under sections 1-3 (C9017 has no speech)
    bed_t = OPEN - 0.1
    src_t = 1.0
    while bed_t < T["b4"] - 0.2:
        d = min(9.0, T["b4"] - 0.2 - bed_t + 0.4)
        cue("C9017", src_t, bed_t, d, -3, fin=0.4, fout=0.4)
        bed_t += d - 0.4
        src_t = 1.0 if src_t > 10 else src_t + 9.0
    # the build after "chasing perfection": clinks come up
    cue("C8894", 0.6, T_B3_P2 + 0.3, T["b4"] - T_B3_P2, 0, fin=0.3, fout=0.15)
    cue("C9019", 6.0, T_B3_P2 + 0.8, T["b4"] - T_B3_P2 - 0.5, -1, fin=0.3, fout=0.15)
    # facility: exterior air, atrium, rooms
    cue("C8956", 20.8, T["b4"] - 0.2, 3.6, 1, fin=0.2, fout=0.6)
    cue("C8955", 2.2, T["b4"] + 3.0, 6.2, 0, fin=0.6, fout=0.8)
    cue("C9017", 12.0, T["b4"] + 8.6, T["b5"] - T["b4"] - 8.4, -4, fin=0.8, fout=0.6)
    # back in the OR: room bed through section 5, then the hero shot's own sound
    cue("C9017", 2.0, T["b5"] - 0.3, T["b6"] - T["b5"] + 0.6, -3, fin=0.5, fout=0.4)
    cue("C9017", 6.2 - 0.4, T["b6"] - 0.4, END_HOLD + FADE - T["b6"] + 0.4, -1, fin=0.4, fout=FADE + 0.2)
    return bus


def mix():
    dlg = dialogue_bus()
    # dialogue clean-up: high-pass, gentle denoise, light compression
    raw = dlg.buf.astype(np.float32).tobytes()
    p = subprocess.run(["ffmpeg", "-v", "error", "-f", "f32le", "-ar", "48000", "-ac", "2", "-i", "-",
                        "-af", "highpass=f=85,afftdn=nr=8:nf=-42:tn=1,acompressor=threshold=-22dB:ratio=2.2:attack=8:release=120:makeup=1",
                        "-f", "f32le", "-"], input=raw, capture_output=True, check=True)
    d = np.frombuffer(p.stdout, np.float32).reshape(-1, 2)
    # compensate the denoiser's processing latency so lip sync stays exact
    from scipy.signal import fftconvolve
    ref = dlg.buf[:, 0][: 48000 * 12]
    got = d[:, 0][: 48000 * 12]
    c = fftconvolve(got, ref[::-1][: 48000 * 12], mode="full")
    lag = int(np.argmax(c[len(ref) - 1: len(ref) - 1 + 4800]))
    print(f"dialogue chain latency: {lag} samples ({lag / 48:.1f} ms) -> compensated")
    d = d[lag:]
    n = min(len(d), len(dlg.buf))
    dlg.buf[:] = 0
    dlg.buf[:n] = d[:n]
    nat = nat_bus()
    # duck nat under dialogue
    pres = au.presence(dlg, attack=0.08, release=0.30, thresh_db=-40)
    duck = au.db(-14 * pres)
    nat.buf *= duck[:, None]
    # overall nat level and a gentle slope into the end card
    nat.buf *= au.db(-6)
    mixbuf = dlg.buf * au.db(-4) + nat.buf
    au.SR
    return mixbuf, dlg, nat


def write_wav(path, buf):
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "f32le", "-ar", "48000", "-ac", "2", "-i", "-",
                    "-c:a", "pcm_s24le", path], input=np.clip(buf, -1, 1).astype(np.float32).tobytes(), check=True)


def measure_i(path):
    out = subprocess.run(["ffmpeg", "-hide_banner", "-i", path, "-af", "ebur128=peak=true", "-f", "null", "-"],
                         capture_output=True, text=True).stderr
    tail = out[out.rindex("Summary:"):]
    i = float(tail.split("I:")[1].split("LUFS")[0])
    tp = float(tail.split("Peak:")[1].split("dBFS")[0])
    return i, tp


def loudnorm(src, dst, target=-16.0, tp=-1.5):
    """Linear gain to the integrated target, then a true-peak safety limiter (no AGC)."""
    i, _ = measure_i(src)
    g = target - i
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", src, "-af",
                    f"volume={g:.2f}dB,alimiter=limit={10 ** (tp / 20):.4f}:attack=5:release=60:level=disabled",
                    "-ar", "48000", "-c:a", "pcm_s24le", dst], check=True)
    print(f"loudness {i:.1f} LUFS -> gain {g:+.1f} dB")


# ------------------------------------------------------------------ main
def main():
    args = sys.argv[1:]
    print(f"timeline: total {TOTAL:.2f}s  bites at " + ", ".join(f"{k}={v:.2f}" for k, v in T.items()))
    if "--plan" in args:
        prev = 0.0
        for end_s, spec, trans in TL:
            print(f"  {prev:6.2f}-{end_s:6.2f}  {spec.get('label', spec['kind']):22s} {trans}")
            prev = end_s
        return
    if "--still" in args:
        times = [float(x) for x in args[args.index("--still") + 1].split(",")]
        for x in times:
            f = E.F(x)
            got = {}
            render_frames(f, f + 1, lambda fi, img: got.setdefault(fi, img))
            cv2.imwrite(f"{OUT}/still_{x:06.2f}.jpg", (got[f] * 255 + 0.5).astype(np.uint8), [cv2.IMWRITE_JPEG_QUALITY, 92])
        print("stills written")
        return
    if "--audio" in args or "--all" in args:
        mixbuf, dlg, nat = mix()
        write_wav(f"{OUT}/mix_raw.wav", mixbuf)
        write_wav(f"{OUT}/stem_dialogue.wav", dlg.buf * au.db(-4))
        write_wav(f"{OUT}/stem_nat.wav", nat.buf)
        loudnorm(f"{OUT}/mix_raw.wav", f"{OUT}/mix.wav")
        print("audio written")
        if "--audio" in args:
            return
    tag = os.environ.get("REEL_TAG", "sukkar_reel")
    vid = f"{OUT}/{tag}_video.mp4"
    enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "bgr24",
                            "-s", f"{E.W}x{E.H}", "-r", f"{E.FPS_NUM}/{E.FPS_DEN}", "-i", "-",
                            "-vf", "scale=out_color_matrix=bt709:out_range=tv,format=yuv420p",
                            "-c:v", "libx264", "-preset", os.environ.get("X264_PRESET", "slow"),
                            "-crf", os.environ.get("CRF", "16"), "-tune", "grain" if E.SCALE == 1 else "film",
                            "-color_primaries", "bt709", "-color_trc", "bt709", "-colorspace", "bt709",
                            "-movflags", "+faststart", vid], stdin=subprocess.PIPE)

    def sink(f, img):
        enc.stdin.write((img * 255 + 0.5).astype(np.uint8).tobytes())

    render_frames(0, E.F(TOTAL), sink)
    enc.stdin.close()
    enc.wait()
    final = f"{OUT}/{tag}.mp4"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", vid, "-i", f"{OUT}/mix.wav", "-map", "0:v", "-map", "1:a",
                    "-c:v", "copy", "-c:a", "aac", "-b:a", "320k", "-shortest", "-movflags", "+faststart", final], check=True)
    print("wrote", final)


if __name__ == "__main__":
    main()
