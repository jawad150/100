"""Organic Fostering "The Question in the Notes App" (Reel 02 brief), 9:16, ~34 s.

0  Delete-key tap. Kinetic opening text "The question I kept deleting"; a 3D phone deletes "This might be a silly
   question…". "three times" -> LAYERCUT: three drafts peel apart; x3. "that week" -> RETRO tape rewind + calendar.
1  SPIRAL: the phone spins down beside the mug, "later that day", magenta circle wipe onto the caller dialling.
2  The caller (real footage): "Can I ask something?" in kinetic words; rain cloud on "struggling"; a home with its door
   open on "comes to live with me". Black circle wipe.
3  The answer on night plum: her portrait in a dotted ring (black-and-white warming to colour), the turning mug stops,
   3D badge on "supervising social worker"; EXPLAINER nodes along a dotted path; ECLIPSE + AURORA on "outside normal
   hours" with the night clock.
4  Back in the Notes app: the old question ticked, a new line typed; 3D cap on "training"; she smiles.
5  Plum end card: official logo, Start your enquiry, organicfostering.co.uk, no obligation.

Usage: python3 reel_notes.py still 1.0,5.0 | range a b | times
"""
import os, sys, json, math, re
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import numpy as np
import cv2
import frames_notes as G
from frames_notes import (W, H, S, ROOT, PLUM, MAG, ORANGE, GREEN, IVORY, INK, BLUSH, WHITE, GLOW, NIGHT, light_bg, dark_bg, blobs,
                          word, typed, subtitle, speaker, pop, circle_portrait, node, dotted_path, circle_wipe, spiral_warp,
                          colour_bar, logo, text_sprite, paste, rrect, cover, layercut, eclipse, aurora, retro, grain, load, Clip,
                          clamp, prog, e_out, e_inout, e_back, _grid, grade)

FPS = 30
INFO = json.load(open(f'{S}/tts/info.json'))
WORDS = INFO['words']
DUR = 34.0
NF = int(DUR * FPS)


def norm(w):
    return re.sub(r"[^a-z']", '', w.lower().replace('’', "'"))


def A(wd, k=0, end=False):
    n = 0
    for w in WORDS:
        if norm(w[0]) == norm(wd):
            if n == k:
                return w[2] if end else w[1]
            n += 1
    raise KeyError(wd)


T_QUESTION, T_THREE, T_TIMES, T_THAT, T_WEEK = A('question'), A('three'), A('times'), A('that'), A('week')
T_CAN, T_SOMETHING, T_WHAT, T_STRUG, T_CHILD, T_ME = A('can'), A('something'), A('what'), A('struggling'), A('child'), A('me', end=True)
T_YOULL, T_SUPER, T_SOCIAL, T_WORKER = A("you'll"), A('supervising'), A('social'), A('worker', end=True)
T_TALK, T_SUPPORT, T_CALL, T_OUTSIDE, T_HOURS = A('talk'), A('support'), A('call'), A('outside'), A('hours')
T_OKAY, T_CAN2, T_TRAIN, T_WELL = A('okay'), A('can', 2), A('training'), A('well', end=True)
T_START, T_ENQ, T_OBLIG = A('start'), A('enquiry'), A('obligation')

# sections
X_RETRO0, X_RETRO1 = T_THAT - 0.15, T_WEEK + 0.75
SP0, SP1 = X_RETRO1 - 0.1, X_RETRO1 + 0.9                     # spiral down beside the mug
CW0, CW1 = SP1 - 0.15, SP1 + 0.45                             # magenta circle wipe onto the call
C_WORRY = T_CAN - 0.25
BW0, BW1 = T_ME + 0.35, T_ME + 0.95                           # black circle wipe into night
EC0, EC1 = T_OUTSIDE - 0.45, T_HOURS + 0.9                    # eclipse + aurora beat
NW0, NW1 = EC1 - 0.1, EC1 + 0.45                              # back to the notes app
END0, END1 = T_START - 0.55, T_START - 0.05                   # plum end card

CL = f'{S}/clips'
CLIPS = {}


def clip(name, file):
    if name not in CLIPS:
        CLIPS[name] = Clip(f'{CL}/{file}.mp4')
    return CLIPS[name]


# ------------------------------------------------------------------ 0: the notes app, three drafts, that week
HOOK = 'This might be a silly question…'


def scene_hook(t):
    c = light_bg().copy()
    blobs(c, t, PLUM, clamp(t / 0.4))
    # opening text (kinetic, mixed weights)
    word(c, 'The question', 540, 300, 66, 700, PLUM, t - 0.05)
    word(c, 'I kept', 540, 400, 104, 900, INK, t - 0.25)
    word(c, 'deleting', 540, 525, 140, 900, MAG, t - 0.45)
    if t > 0.7:
        k = e_out(prog(t, 0.7, 1.0))
        cv2.line(c, (250, 532), (int(250 + 580 * k), int(532 - 17 * k)), MAG.tolist(), 10, cv2.LINE_AA)
    # the phone, its note being deleted from the end
    u = t - 0.1
    pop(c, 'phone_notes', 540, 1060, 700, u)
    if u > 0.3:
        n = len(HOOK) - int(len(HOOK) * prog(t, 0.35, 2.4))
        card = rrect(420, 170, 22, WHITE, 0.97)
        paste(c, card, 548, 990, clamp((u - 0.3) / 0.2))
        typed(c, 'This might be a', 352, 960, 36, n, 800, INK, caret=n <= 15, t=t)
        typed(c, 'silly question…', 352, 1012, 36, max(0, n - 16), 800, INK, caret=n > 15, t=t)
        # delete key glow pulse on every tap
        tap = (t * 14) % 1.0 if t < 2.4 else 1.0
        paste(c, rrect(120, 70, 16, MAG, 0.25 + 0.5 * (1 - tap)), 735, 1230, clamp((u - 0.3) / 0.2))
        paste(c, text_sprite('delete', 800, 26, WHITE), 735, 1231, clamp((u - 0.3) / 0.2))
    return c


def scene_drafts(t):
    c = light_bg().copy()
    blobs(c, t, PLUM, 1.0, 1)
    word(c, 'the same question', 540, 330, 64, 700, PLUM, t - T_QUESTION + 0.1)
    u = t - T_THREE + 0.1
    pop(c, 'drafts', 540, 920, 780, u)
    word(c, '×3', 840, 520, 230, 900, MAG, t - T_TIMES + 0.05, glow=GLOW)
    # LAYERCUT: the stack splits into slices that slide apart, then back
    if T_THREE < t < T_THAT:
        k = math.sin(math.pi * prog(t, T_THREE + 0.15, T_TIMES + 0.25))
        if k > 0:
            bg = light_bg().copy()
            c = layercut(c, bg, k * 0.28, n=5)
    return c


def scene_week(t):
    c = light_bg().copy()
    pop(c, 'calendar', 540, 900, 700, t - T_WEEK + 0.25)
    word(c, 'that week.', 540, 1330, 120, 900, PLUM, t - T_WEEK)
    amt = clamp((t - X_RETRO0) / 0.25) * (1 - prog(t, X_RETRO1 - 0.25, X_RETRO1))
    if amt > 0:
        c = retro(c, t, amt)
        ts = ['MON 23:41', 'WED 00:12', 'FRI 22:58'][min(2, int(prog(t, X_RETRO0, X_RETRO1) * 3))]
        word(c, ts, 230, 230, 50, 800, (1, 1, 1), 1.0, anchor='c')
        # rewind arrows drawn as shapes
        for k in range(2):
            x = 820 + k * 38
            pts = np.array([[x + 30, 205], [x + 30, 255], [x, 230]], np.int32)
            cv2.fillPoly(c, [pts], (1.0, 1.0, 1.0), cv2.LINE_AA)
        word(c, 'REW', 950, 230, 46, 800, (1, 1, 1), 1.0)
    return c


def scene_spiral(t):
    c = light_bg().copy()
    u = prog(t, SP0, SP1)
    pop(c, 'mug', 650, 960, 520, t - SP0 + 0.1)
    rot = -70 * e_inout(u) - 15
    x = 470 - 190 * e_inout(u)
    y = 1100 + 40 * e_inout(u)
    pop(c, 'phone_notes', x, y, 520 - 220 * e_inout(u), 1.0, rot=rot)
    c = spiral_warp(c, 0.28 * math.sin(math.pi * u), 600, 950)
    word(c, 'later that day', 540, 330, 80, 800, PLUM, t - SP0 - 0.3)
    return c


# ------------------------------------------------------------------ 2: the call
def footage_dial(t):
    f = clip('dial', '39815').at(1.0 + (t - CW0) * 0.9)
    return grade(cover(f, fx=0.5, fy=0.5, z=1.0 + 0.05 * prog(t, CW0, C_WORRY)), warm=0.3, contrast=1.05, vig=0.4, exp=0.95)


def scene_call(t):
    if t < C_WORRY:
        c = footage_dial(t)
    else:
        f = clip('worry', '39790').at(2.0 + (t - C_WORRY) * 0.85)
        c = grade(cover(f, fx=0.3, fy=0.4, z=1.05 + 0.08 * prog(t, C_WORRY, BW1)), warm=0.2, contrast=1.06, vig=0.45,
                  exp=1.0 - 0.18 * prog(t, T_WHAT, T_STRUG + 0.4))
    if t < C_WORRY:
        word(c, 'later that day', 540, 330, 80, 800, WHITE, 1.0, glow=PLUM)
    fa = 1 - prog(t, T_WHAT - 0.25, T_WHAT + 0.1)
    word(c, 'Can I ask', 540, 340, 92, 700, WHITE, t - T_CAN, glow=PLUM, a=fa)
    word(c, 'something?', 540, 465, 134, 900, WHITE, t - T_SOMETHING, glow=MAG, a=fa)
    if t > T_WHAT - 0.2:                                       # the first words move up out of the way
        pass
    pop(c, 'cloud', 300, 420, 380, t - T_STRUG + 0.05)
    word(c, 'struggling', 330, 660, 92, 900, WHITE, t - T_STRUG, glow=MAG)
    pop(c, 'home_door', 760, 1050, 430, t - T_CHILD + 0.05, glow=np.array((1, 0.7, 0.4), np.float32))
    return c


# ------------------------------------------------------------------ 3: the answer
def portrait_img(t):
    f = clip('listen', '39791').at(0.5 + (t - BW0) * 0.75)
    return cover(f, fx=0.5, fy=0.33, z=1.0, w=520, h=520)


def mug_turn(c, t, x=250, y=1110, size=300):
    """The mug turns in her hands, then stops on 'supervising social worker'."""
    stop = prog(t, T_SUPER, T_WORKER)
    ang = 14 * math.sin(t * 5.0) * (1 - e_out(stop))
    pop(c, 'mug', x, y, size, t - BW0 - 0.2, rot=int(round(ang)))


def scene_answer(t):
    c = dark_bg().copy()
    bw = 1 - prog(t, T_SUPPORT, T_HOURS)                       # her portrait warms to colour as she listens
    circle_portrait(c, portrait_img(t), 540, 400, 230, bw=bw, ring_t=t, ring_col=GLOW, a=clamp((t - BW0) / 0.4))
    speaker(c, 'Organic Fostering', MAG, 700, clamp((t - T_YOULL + 0.2) / 0.3))
    if t < T_TALK - 0.2:
        word(c, 'supervising', 540, 840, 70, 700, WHITE, t - T_SUPER)
        word(c, 'social worker', 540, 935, 92, 900, GLOW, t - T_SOCIAL, glow=MAG)
        pop(c, 'badge', 820, 1150, 380, t - T_SOCIAL + 0.05)
        mug_turn(c, t)
        return c
    # EXPLAINER: nodes join up along a dotted path
    pts = [(190, 840), (430, 980), (250, 1160), (560, 1290), (860, 1180)]
    fr = prog(t, T_TALK - 0.2, T_CALL + 0.3)
    dotted_path(c, pts[:4], fr)
    node(c, *pts[0], t - T_TALK + 0.4, 'badge', 140, label='Your social worker')
    node(c, *pts[1], t - T_TALK, 'chat', 140, label='Talk it through')
    node(c, *pts[2], t - T_SUPPORT, 'calendar', 140, label='What support looks like')
    node(c, *pts[3], t - T_CALL, 'night_clock', 140, label='Out of hours', lab_side=1)
    mug_turn(c, t, 880, 1420, 220)
    return c


def scene_eclipse(t):
    c = dark_bg().copy()
    u = prog(t, EC0, EC0 + 1.0)
    c = aurora(c, t, 0.75 * prog(t, EC0, T_HOURS + 0.2), 0.06, 0.28)
    # the warm sun slides into night: eclipse, then a soft moon glow
    c = eclipse(c, 540, 560, 170, u, warm=(1.0, 0.75, 0.5))
    word(c, 'outside', 540, 820, 70, 700, WHITE, t - T_OUTSIDE)
    pop(c, 'night_clock', 540, 1060, 500, t - T_OUTSIDE - 0.1, glow=np.array((0.9, 0.4, 0.8), np.float32))
    word(c, 'normal hours', 540, 1340, 100, 900, GLOW, t - T_HOURS + 0.1, glow=MAG)
    return c


# ------------------------------------------------------------------ 4: back to the notes app
NEW = 'Can I ask about training as well?'


def scene_notes(t):
    c = light_bg().copy()
    blobs(c, t, PLUM, 1.0, 2)
    paste(c, rrect(920, 640, 46, WHITE, 0.97), 540, 760)
    paste(c, text_sprite('Questions', 900, 64, INK), 330, 520)
    # the old question, ticked
    k = clamp((t - NW1) / 0.35)
    typed(c, 'What happens if I’m struggling?', 170, 640, 38, 99, 700, (0.55, 0.5, 0.55), caret=False)
    if k > 0:
        cv2.polylines(c, [np.array([[118, 640], [132, 656], [158, 622]], np.int32)], False, GREEN.tolist(), 7, cv2.LINE_AA)
    # the new line, typed as she says it
    n = len(NEW) * prog(t, T_CAN2 - 0.1, T_WELL - 0.05)
    typed(c, NEW, 120, 740, 44, n, 800, INK, caret=True, t=t)
    word(c, 'Okay.', 540, 330, 120, 900, GREEN, t - T_OKAY, glow=None)
    pop(c, 'cap', 770, 1180, 420, t - T_TRAIN + 0.05)
    f = clip('smile', '39791').at(6.0 + (t - NW0) * 0.8)
    circle_portrait(c, cover(f, fx=0.5, fy=0.33, z=1.0, w=300, h=300), 270, 1190, 140, bw=0.0, ring_t=t, ring_col=MAG,
                    a=clamp((t - NW0) / 0.4))
    return c


# ------------------------------------------------------------------ 5: end card
def end_card(t):
    c = np.empty((H, W, 3), np.float32)
    c[:] = PLUM
    blobs(c, t, np.array((0.42, 0.06, 0.36), np.float32), 1.0, 3)
    u = t - END1
    lg = logo(640)
    k = e_back(clamp(u / 0.5), 1.2)
    a = clamp(u / 0.3)
    paste(c, rrect(760 * (0.9 + 0.1 * k), lg.shape[0] + 110, 40, IVORY), 540, 560, a)
    paste(c, lg, 540, 560 + 20 * (1 - k), a)
    word(c, 'Start your enquiry', 540, 860, 76, 900, WHITE, t - T_START)
    if t > T_ENQ:
        kk = e_back(clamp((t - T_ENQ) / 0.4))
        paste(c, rrect(560 * kk + 2, 104, 52, MAG), 540, 1010)
        word(c, 'organicfostering.co.uk', 540, 1010, 44, 800, WHITE, t - T_ENQ - 0.15)
    word(c, 'We’ll talk through your questions,', 540, 1170, 42, 700, (0.95, 0.85, 0.93), t - T_START - 2.9)
    word(c, 'with no obligation.', 540, 1232, 46, 800, WHITE, t - T_OBLIG + 0.3)
    colour_bar(c)
    return c


# ------------------------------------------------------------------ composition
def base(t):
    if t < T_QUESTION - 0.15:
        return scene_hook(t)
    if t < X_RETRO0:
        return scene_drafts(t)
    if t < SP0:
        return scene_week(t)
    if t < CW0:
        return scene_spiral(t)
    if t < CW1:
        return circle_wipe(scene_spiral(t), footage_dial(t), prog(t, CW0, CW1), 650, 900, col=MAG)
    if t < BW0:
        return scene_call(t)
    if t < BW1:
        return circle_wipe(scene_call(t), scene_answer(t), prog(t, BW0, BW1), 540, 960, col=NIGHT)
    if t < EC0:
        return scene_answer(t)
    if t < EC0 + 0.35:
        k = prog(t, EC0, EC0 + 0.35)
        return scene_answer(t) * (1 - k) + scene_eclipse(t) * k
    if t < NW0:
        return scene_eclipse(t)
    if t < NW1:
        return circle_wipe(scene_eclipse(t), scene_notes(t), prog(t, NW0, NW1), 540, 1060, col=GLOW)
    if t < END0:
        return scene_notes(t)
    if t < END1:
        return circle_wipe(scene_notes(t), end_card(t), prog(t, END0, END1), 540, 960, col=MAG)
    return end_card(t)


def chunks():
    """Subtitle chunks: split each spoken segment at sentence ends / ~7 words."""
    out, cur = [], []
    for i, w in enumerate(WORDS):
        cur.append(w)
        nxt = WORDS[i + 1] if i + 1 < len(WORDS) else None
        brk = (nxt is None or nxt[1] - w[2] > 0.5 or nxt[3] != w[3] or w[0].endswith(('.', '?')) or norm(w[0]) in ('struggling', 'like')
               or len(cur) >= 10)
        if brk:
            out.append(cur)
            cur = []
    return out


CH = chunks()


def subtitles(c, t):
    for i, ch in enumerate(CH):
        t0, t1 = ch[0][1] - 0.08, ch[-1][2] + 0.35
        if i + 1 < len(CH):
            t1 = min(t1, CH[i + 1][0][1] - 0.08)
        if t0 <= t < t1:
            subtitle(c, ' '.join(w[0] for w in ch), 1560, clamp((t - t0) / 0.12) * clamp((t1 - t) / 0.12))
            if CW1 < t < NW0 and t < END0:
                who = 'Caller' if ch[0][3] == 'caller' else 'Organic Fostering'
                if who == 'Caller':
                    speaker(c, who, MAG, 1470, clamp((t - t0) / 0.12))
    return c


def finish(c, t):
    c = np.clip(c, 0, 1)
    c = grain(c, 0.012, int(t * FPS))
    return np.clip(c * prog(t, 0.0, 0.12), 0, 1)


def frame(t):
    c = base(t)
    c = subtitles(c, t)
    return finish(c, t)


def write(i, c, d):
    cv2.imwrite(f'{d}/{i:05d}.png', (np.clip(c, 0, 1)[..., ::-1] * 255 + 0.5).astype(np.uint8))


if __name__ == '__main__':
    mode = sys.argv[1]
    if mode == 'times':
        for k, v in sorted(((k, v) for k, v in globals().items() if re.match(r'^(T|C|X|SP|CW|BW|EC|NW|END)\w*$', k) and isinstance(v, float)), key=lambda kv: kv[1]):
            print(f'{k:10s} {v:6.2f}')
        print('DUR', DUR, 'NF', NF)
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
