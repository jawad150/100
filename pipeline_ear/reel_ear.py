"""BMHC "Manchester, can you name this place by ear?" (Heart Work), 9:16, 34 s - rebuilt scene by scene from the
user's Pinterest reference, in BMHC's brand.

Timeline (brief): 0-4 hook + three sounds | 4-10 first clue (ball) | 10-16 second clue (book) | 16-22 last one (radio,
"Assalamu alaikum, Manchester.") | 22-27 "Got a guess?" + the sounds over BMHC's wide shots | 27-34 the reveal + end card.
Narrator lines sit in fixed slots (SLOTS); voice_ear.py drops each ElevenLabs line into its slot.

Usage: python3 reel_ear.py still 1.0,5.0 | range a b | times
"""
import os, sys, json, math, re
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import numpy as np
import cv2
import frames_ear as G
from frames_ear import (W, H, S, ROOT, INK, WHITE, MAG, TEAL, ORANGE, LIME, BARS, light_bg, dark_bg, pop, word, highlight, pill, clue_no,
                        card, orbit, confetti, caption, tag, paste, rrect, text_sprite, cover, load, logo, clamp, prog, e_out, e_inout,
                        e_back, _grid, grain, Clip)

FPS = 30
DUR = 34.0
NF = int(DUR * FPS)
BLACK = (0.04, 0.04, 0.04)
VID = f'{ROOT}/workspace_ai/dl/bmhc-new.mp4'
DL = f'{ROOT}/workspace_ai/dl'

# narrator / presenter slots (start, text, speaker) - the real takes are fitted into these
SLOTS = [
    (0.35, 'Manchester, can you name this place by ear?', 'nar'),
    (4.45, 'First clue.', 'nar'),
    (10.25, 'Second clue.', 'nar'),
    (16.2, 'Last one.', 'nar'),
    (18.75, 'Assalamu alaikum, Manchester.', 'pres'),
    (26.95, 'Three sounds. One address.', 'nar'),
    (29.6, 'The British Muslim Heritage Centre, Whalley Range.', 'nar'),
]
INFO_P = f'{S}/tts/info.json'
INFO = json.load(open(INFO_P)) if os.path.exists(INFO_P) else None

# sound moments (cut on the bounce, page turn and fader click)
SND = {
    'h_bounce': 3.0, 'h_rustle': 3.4, 'h_click': 3.8,
    'b1': 5.55, 'b2': 6.25, 'b3': 6.85, 'squeak': 6.95,
    'page': 11.45, 'pencil': 12.55,
    'fader': 17.35, 'phones': 17.95,
    'r_bounce': 23.85, 'r_rustle': 24.85, 'r_click': 25.85,
}
C1, C2, C3, C4, C5, C6, C7, C8 = 2.95, 4.2, 9.9, 15.9, 21.8, 23.7, 27.0, 32.4      # cuts

CLIPS = {}


def clip(name):
    if name not in CLIPS:
        CLIPS[name] = Clip(VID)
    return CLIPS[name]


def punch(c, t, t0, amt=0.06, dur=0.25):
    """A quick zoom punch on each cut (the reference's snappy cuts)."""
    u = (t - t0) / dur
    if 0 <= u < 1:
        z = 1 + amt * (1 - e_out(u))
        M = cv2.getRotationMatrix2D((W / 2, H / 2), 0, z)
        c = cv2.warpAffine(c, M, (W, H), borderMode=cv2.BORDER_REFLECT)
    return c


# ------------------------------------------------------------------ scenes
def s_hook(t):
    c = light_bg(0).copy()
    tag(c, 'HEART', 64, 150, MAG, a=1.0)
    word(c, 'Manchester,', 540, 470, 100, BLACK, t - 0.3)
    word(c, 'can you name', 540, 595, 86, BLACK, t - 1.0)
    word(c, 'this place', 540, 705, 86, BLACK, t - 1.45)
    highlight(c, 'by ear?', 540, 840, 100, t - 1.95)
    pop(c, 'mic', 760, 1170 + 10 * math.sin(t * 2), 520, t - 0.15, rot=4 * math.sin(t * 1.5))
    return c


def s_sounds(t):
    c = dark_bg(1).copy()
    for nm, key, (x, y, sz), (px, py), txt in (('ball', 'h_bounce', (300, 520, 300), (640, 430), '[ball bouncing]'),
                                               ('book', 'h_rustle', (780, 780, 380), (400, 940), '[page rustling]'),
                                               ('fader', 'h_click', (360, 1100, 400), (700, 1320), '[switch clicks]')):
        u = t - SND[key] + 0.02
        pop(c, nm, x, y, sz, u)
        pill(c, txt, px, py, u - 0.08)
    return c


def ball_y(t):
    """Height of the bouncing ball above the floor (0 at contact): bounces at b1, b2, b3 then rolls."""
    pts = [SND['b1'] - 0.75, SND['b1'], SND['b2'], SND['b3']]
    hs = [420, 290, 160]
    if t < pts[0]:
        return 420
    for i in range(3):
        a, b = pts[i], pts[i + 1]
        if t < b:
            u = (t - a) / (b - a)
            h = hs[i] if i else 600
            return h * (1 - (2 * u - 1) ** 2) if i else 420 * (1 - u ** 2)
    return 0.0


def s_ball(t):
    c = dark_bg(2, True).copy()
    clue_no(c, 1, 540, 400, t - C2 - 0.05)
    word(c, 'First clue.', 540, 640, 96, WHITE, t - SLOTS[1][0])
    floor = 1215
    u = prog(t, SND['b1'] - 0.75, SND['b3'] + 0.9)
    x = 900 - 560 * e_out(u)
    y = floor - 130 - ball_y(t)
    # shadow follows across the floor
    h = ball_y(t)
    sh = rrect(220 * (1 - h / 900), 40 * (1 - h / 900), 20, (0, 0, 0), 0.55 * (1 - h / 1200))
    paste(c, cv2.GaussianBlur(sh, (0, 0), 6), x, floor - 20)
    squash = 1.0
    for b in ('b1', 'b2', 'b3'):
        d = abs(t - SND[b])
        if d < 0.06:
            squash = 0.82
    spr = G.token('ball', 260, int(-200 * e_out(u)))
    spr = cv2.resize(spr, (int(spr.shape[1] / squash ** 0.5), int(spr.shape[0] * squash)))
    if t > SND['b1'] - 0.75:
        paste(c, spr, x, y + (1 - squash) * 80)
    pill(c, '[ball bouncing]', 540, 1420, t - SND['b1'])
    pill(c, '[trainer squeaks]', 540, 1520, t - SND['squeak'] - 0.05)
    if 0 < t - SND['squeak'] < 0.8:                               # squeak lines
        k = (t - SND['squeak']) / 0.8
        for i in range(3):
            ang = math.radians(-160 + i * 25)
            r0, r1 = 150 + 60 * k, 210 + 80 * k
            p0 = (int(x + r0 * math.cos(ang)), int(floor - 60 + r0 * math.sin(ang)))
            p1 = (int(x + r1 * math.cos(ang)), int(floor - 60 + r1 * math.sin(ang)))
            cv2.line(c, p0, p1, tuple(float(v) for v in MAG), 8, cv2.LINE_AA)
    return c


def s_book(t):
    c = dark_bg(3).copy()
    clue_no(c, 2, 540, 400, t - C3 - 0.05)
    word(c, 'Second clue.', 540, 640, 96, WHITE, t - SLOTS[2][0])
    # a page card: lines of text, a page that flips on the rustle, a magenta underline drawn by the pencil
    u0 = t - C3 - 0.4
    k = e_back(clamp(u0 / 0.4))
    if k > 0:
        pw, ph = 720 * k, 520 * k
        paste(c, rrect(pw, ph, 24, (0.985, 0.975, 0.95), 1.0), 540, 1060)
        if k > 0.8:
            for j in range(6):
                lw = (560, 600, 480, 590, 520, 400)[j]
                paste(c, rrect(lw, 16, 8, (0.78, 0.76, 0.74), 1.0), 540 - (600 - lw) / 2, 900 + j * 62)
            pu = prog(t, SND['pencil'], SND['pencil'] + 0.8)
            if pu > 0:
                paste(c, rrect(max(4, 300 * e_out(pu)), 12, 6, MAG, 1.0), 540 - 300 + 300 * e_out(pu) / 2 - 0, 1040)
                pop(c, 'book', 820 - 340 * pu, 1010, 0.0, 0)          # placeholder no-op
        fu = prog(t, SND['page'] - 0.05, SND['page'] + 0.45)
        if 0 < fu < 1:                                              # the page flips over (a quad rotating about the spine)
            sx = 540 - pw / 2
            wq = pw * math.cos(math.pi * fu)
            quad = np.float32([[sx, 1060 - ph / 2], [sx + wq, 1060 - ph / 2 - 40 * math.sin(math.pi * fu)],
                               [sx + wq, 1060 + ph / 2 + 40 * math.sin(math.pi * fu)], [sx, 1060 + ph / 2]])
            lay = np.zeros((H, W), np.uint8)
            cv2.fillPoly(lay, [quad.astype(np.int32)], 255, cv2.LINE_AA)
            m = lay.astype(np.float32)[..., None] / 255
            shade = 0.82 + 0.18 * abs(math.cos(math.pi * fu))
            c[:] = c * (1 - m) + np.array((0.97, 0.96, 0.93), np.float32) * shade * m
    pop(c, 'book', 800, 1420, 300, t - C3 - 0.2)
    pill(c, '[page rustling]', 400, 1440, t - SND['page'])
    pill(c, '[pencil scratching]', 540, 1560, t - SND['pencil'] - 0.1)
    return c


def s_radio(t):
    c = dark_bg(4).copy()
    clue_no(c, 3, 540, 400, t - C4 - 0.05)
    word(c, 'Last one.', 540, 620, 96, WHITE, t - SLOTS[3][0])
    orbit(c, 540, 1060, 330, t, [(MAG, 90), (TEAL, 70), (ORANGE, 60), (LIME, 70), (MAG, 60)], t - C4 - 0.3)
    pop(c, 'fader', 540, 1070, 440, t - C4 - 0.3)
    fu = t - SND['fader']
    if 0 < fu < 1.2:                                                # ON AIR pulse when the fader goes up
        yy, xx = _grid()
        g = np.exp(-((xx - 560) ** 2 + (yy - 930) ** 2) / (2 * 110 ** 2)) * 0.5 * (1 - fu / 1.2)
        c[:] = np.clip(c + g[..., None] * np.array((1, 0.2, 0.2), np.float32), 0, 1)
    hu = t - SND['phones']
    if hu > 0:
        y = 700 + 130 * e_out(clamp(hu / 0.5))
        pop(c, 'headphones', 820, y, 300, hu + 0.3)
    pill(c, '[switch clicks]', 540, 1440, fu)
    if t > SLOTS[4][0] - 0.3:
        s = text_sprite('HERITAGE RADIO', 800, 28, WHITE, track=0.12)
        paste(c, rrect(s.shape[1] + 44, 56, 28, MAG), 540, 1520, clamp((t - SLOTS[4][0] + 0.3) / 0.2))
        paste(c, s, 540, 1521, clamp((t - SLOTS[4][0] + 0.3) / 0.2))
    return c


def s_guess(t):
    c = light_bg(2).copy()
    word(c, 'Got a', 540, 700, 130, BLACK, t - C5 - 0.05)
    highlight(c, 'guess?', 540, 860, 140, t - C5 - 0.3)
    for i, (x, y, s) in enumerate(((290, 420, '[ball bouncing]'), (830, 1080, '[page rustling]'), (330, 1200, '[switch clicks]'))):
        pill(c, s, x, y + 12 * math.sin(t * 2 + i), t - C5 - 0.5 - i * 0.15, dark=False)
    confetti(c, t, prog(t, C5 + 0.2, C5 + 2.4))
    return c


def s_cards(t):
    c = dark_bg(5).copy()
    word(c, 'Got a guess?', 540, 200, 60, (0.8, 0.8, 0.8), 1.0)
    f1 = clip('sports').at(3.0 + (t - C6) * 0.8)
    card(c, cover(f1, 0.5, 0.5, 1.0, 560, 380), 360, 480, 560, 380, t - SND['r_bounce'] + 0.05, 0.06, '[ball bouncing]')
    if t > SND['r_rustle'] - 0.1:
        f2 = clip('hall').at(12.2 + (t - SND['r_rustle']) * 0.6)
        card(c, cover(f2, 0.5, 0.5, 1.0, 560, 380), 720, 900, 560, 380, t - SND['r_rustle'] + 0.05, -0.06, '[page rustling]')
    card(c, cover(load(f'{DL}/18953234_1692708564077281_8688673643638198134_o.jpg'), 0.5, 0.45, 1.0, 560, 380), 360, 1330, 560, 380,
         t - SND['r_click'] + 0.05, 0.06, '[switch clicks]')
    return c


def s_reveal(t):
    c = dark_bg(6).copy()
    f = clip('drone').at(33.4 + (t - C7) * 0.8)
    card(c, cover(f, 0.45, 0.6, 1.0, 860, 760), 540, 960, 860, 760, t - C7, 0.0)
    word(c, 'Three sounds.', 540, 360, 90, WHITE, t - SLOTS[5][0])
    word(c, 'One address.', 540, 470, 90, MAG, t - SLOTS[5][0] - 0.9)
    word(c, 'Whalley Range, Manchester', 540, 1420, 44, (0.85, 0.85, 0.85), t - SLOTS[6][0] - 1.6, w=600)
    return c


def s_end(t):
    c = np.empty((H, W, 3), np.float32)
    c[:] = INK
    u = t - C8
    lg = logo(820)
    k = e_out(clamp(u / 0.5))
    paste(c, lg, 540, 760 + 20 * (1 - k), clamp(u / 0.3))
    word(c, 'Which clue gave it away?', 540, 1080, 62, WHITE, u - 0.25)
    word(c, '@thebmhc  ·  bmhc.org.uk', 540, 1180, 40, (0.75, 0.75, 0.75), u - 0.45, w=600)
    for i, col in enumerate(BARS):
        kk = clamp((u - 0.1 * i) / 0.35)
        c[H - 22:, int(W * i / 4):int(W * i / 4 + W / 4 * e_out(kk))] = col
    return c


SCENES = [(0, s_hook), (C1, s_sounds), (C2, s_ball), (C3, s_book), (C4, s_radio), (C5, s_guess), (C6, s_cards), (C7, s_reveal), (C8, s_end)]


def base(t):
    i = max(j for j, (t0, _) in enumerate(SCENES) if t >= t0)
    t0, fn = SCENES[i]
    c = fn(t)
    return punch(c, t, t0) if i else c


# ------------------------------------------------------------------ subtitles: white Inter ExtraBold on ink, 2-3 words
def chunks():
    out = []
    if INFO:
        words = INFO['words']
    else:                                                        # placeholder timing until the voice exists
        words = []
        for st, text, spk in SLOTS:
            t = st
            for w_ in text.split():
                d = 0.14 + 0.065 * len(re.sub(r'[^a-z]', '', w_.lower()))
                words.append([w_, t, t + d, spk])
                t += d + 0.04
    cur = []
    for i, w_ in enumerate(words):
        cur.append(w_)
        nxt = words[i + 1] if i + 1 < len(words) else None
        if nxt is None or len(cur) == 3 or w_[0].endswith(('.', ',', '?')) or nxt[1] - w_[2] > 0.5:
            out.append(cur)
            cur = []
    merged = []
    for ch in out:                                               # no single-word orphans
        if len(ch) == 1 and merged and len(merged[-1]) <= 3 and not merged[-1][-1][0].endswith(('.', '?')) and ch[0][1] - merged[-1][-1][2] < 0.4:
            merged[-1] = merged[-1] + ch
        else:
            merged.append(ch)
    return merged


CH = chunks()
KEY = {'manchester', 'ear', 'clue', 'one', 'address', 'heritage', 'range'}


def subtitles(c, t):
    for i, ch in enumerate(CH):
        t0 = ch[0][1] - 0.05
        t1 = min(ch[-1][2] + 0.45, CH[i + 1][0][1] - 0.05) if i + 1 < len(CH) else ch[-1][2] + 0.6
        if t0 <= t < t1 and t < C8:
            parts = [(w_[0], MAG if re.sub(r'[^a-z]', '', w_[0].lower()) in KEY else WHITE) for w_ in ch]
            caption(c, parts, 1660, t - t0, 60)
    return c


def frame(t):
    c = base(t)
    c = subtitles(c, t)
    c = grain(np.clip(c, 0, 1), 0.01, int(t * FPS))
    return np.clip(c * prog(t, 0, 0.12), 0, 1)


def write(i, c, d):
    cv2.imwrite(f'{d}/{i:05d}.png', (np.clip(c, 0, 1)[..., ::-1] * 255 + 0.5).astype(np.uint8))


if __name__ == '__main__':
    mode = sys.argv[1]
    if mode == 'times':
        print('voice:', 'real' if INFO else 'placeholder')
        print([' '.join(w[0] for w in ch) for ch in CH])
    elif mode == 'still':
        d = f'{S}/stills_out'
        os.makedirs(d, exist_ok=True)
        for ts in sys.argv[2].split(','):
            write(int(float(ts) * 100), frame(float(ts)), d)
            print('still', ts, flush=True)
    elif mode == 'range':
        a, b = int(sys.argv[2]), int(sys.argv[3])
        d = f'{S}/frames'
        os.makedirs(d, exist_ok=True)
        for i in range(a, min(b, NF)):
            write(i, frame(i / FPS), d)
            if i % 30 == 0:
                print('frame', i, flush=True)
