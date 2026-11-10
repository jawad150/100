"""Scene images for Organic Fostering "Three of Me" v2: THREE DIFFERENT REAL PEOPLE, each one voice of the debate,
seen in their own working day (no talking to camera; the voices are their thoughts).

  THE WORRIER  - an office worker, 5:30 pm, still writing tomorrow's schedule      (Mixkit 4806, 4807)
  THE OPTIMIST - a delivery driver on his round, parcel under his arm, waving      (Mixkit 31139, 31136)
  THE REALIST  - a care nurse with her residents, clipboard in hand                 (Mixkit 5820, 5798, 5568)

Opening: commuters stream home at 5:30 pm. Each factor slaps on as a 3D sticker on its word. "You ask." = all three
side by side. End card. The nurse footage is 720p, so she sits in a big tilted photo frame over a soft blurred copy of
her scene (keeps her sharp); the other two are full-bleed.

Usage: python3 frames_three2.py [n ...] -> workspace_three2/frames/scene_XX.png + storyboard.jpg
"""
import os, sys, math, glob
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import numpy as np
import cv2
import frames_three as F
from frames_three import (R, W, H, draw, blur_sprite, tint, rrect, ts, solid, paste_spr, _wmask, PURPLE, ORANGE, PLUM, IVORY, LAV,
                          LEAF, SLATE, WHITE, N9, N8, N7, grade, cover, slap, word_sticker, caption, shade, top_shade)

ROOT = os.path.abspath(os.path.join(HERE, '..'))
S = f'{ROOT}/workspace_three2'
OUT = f'{S}/frames'
F.S = f'{ROOT}/workspace_three'          # stickers + logo live with v1
_X, _Y = R._X, R._Y
TEAL = R.hexc('#0E8C8C')
CHAR = {'worrier': ('THE WORRIER', SLATE, 'mug', 'office worker'),
        'optimist': ('THE OPTIMIST', ORANGE, 'sun', 'delivery driver'),
        'realist': ('THE REALIST', PURPLE, 'clipboard', 'care nurse')}


def frame_of(cid, t):
    cap = cv2.VideoCapture(f'{S}/clips/{cid}.mp4')
    cap.set(cv2.CAP_PROP_POS_MSEC, t * 1000)
    ok, im = cap.read()
    return im[..., ::-1].astype(np.float32) / 255


def full(kind, cid, t, fx=0.5, fy=0.5, z=1.0, w=W, h=H):
    return grade(cover(frame_of(cid, t), fx, fy, z, w, h), kind)


def photo_card(kind, img, fx=0.5, fy=0.5, z=1.0, cw=960, ch=1080, x=W / 2, y=840, rot=-2.5, bg_tint=PURPLE):
    """Footage in a big white-bordered photo frame, tilted, over a soft blurred copy of the same scene."""
    bg = cv2.GaussianBlur(cover(img, fx, fy, 1.0), (0, 0), 28)
    bg = grade(bg, kind) * 0.75 + np.array(bg_tint[:3], np.float32) * 0.25
    pic = grade(cover(img, fx, fy, z, cw, ch), kind)
    m = cv2.resize(R.sdf_fill(R.rrect_alpha(cw, ch, 22, 2)), (cw, ch))
    card = np.concatenate([pic * m[..., None], m[..., None]], 2).astype(np.float32)
    frame = rrect(cw + 36, ch + 36, 32, WHITE)
    draw(bg, blur_sprite(tint(frame, (0.15, 0.05, 0.12)), 26), x + 12, y + 26, rot=rot, opacity=0.5)
    draw(bg, frame, x, y, rot=rot)
    draw(bg, card, x, y, rot=rot)
    return bg


def name_tag(c, kind, x=70, y=330):
    label, col, _, job = CHAR[kind]
    s = ts(label, N9, 40, WHITE, 0.08)
    j = ts(job, N7, 30, (1, 1, 1, 0.95))
    p = rrect(s.shape[1] + 60, 74, 37, col).copy()
    paste_spr(p, s, p.shape[1] / 2, 37)
    draw(c, blur_sprite(tint(p, (0.1, 0.03, 0.08)), 12), x + p.shape[1] / 2 + 6, y + 10, opacity=0.4)
    draw(c, p, x + p.shape[1] / 2, y)
    q = rrect(j.shape[1] + 36, 50, 25, (0.1, 0.05, 0.1, 0.65)).copy()
    paste_spr(q, j, q.shape[1] / 2, 25)
    draw(c, q, x + q.shape[1] / 2 + 10, y + 66)


def clock_tag(c, x=70, y=330):
    s = ts('5:30 PM', N9, 44, WHITE, 0.06)
    p = rrect(s.shape[1] + 60, 80, 40, (0.1, 0.05, 0.1, 0.72)).copy()
    paste_spr(p, s, p.shape[1] / 2, 40)
    draw(c, p, x + p.shape[1] / 2, y)


# ------------------------------------------------------------------ scenes
def s01():   # WORRIER (opening): "I work full time." — commuters stream home at 5:30 pm
    c = grade(cover(frame_of(25890, 3.0), 0.5, 0.6), 'worrier')
    c = top_shade(c)
    clock_tag(c)
    slap(c, 'briefcase', 300, 1050, 300, rot=-8)
    slap(c, 'clock', 780, 760, 300, rot=8)
    c = shade(c)
    caption(c, 'I work full time.', keys=('full', 'time'), hl=SLATE)
    return c


def s02():   # WORRIER: "So I can't foster, right?" — still at her desk, writing tomorrow's list
    c = full('worrier', 4806, 6.0, fx=0.68, fy=0.45, z=1.0)
    c = top_shade(c)
    name_tag(c, 'worrier')
    slap(c, 'mug', 250, 1080, 220, rot=-6)
    slap(c, 'house', 300, 720, 240, rot=-8)
    slap(c, 'question', 470, 560, 140, rot=10)
    c = shade(c)
    caption(c, ["I work full time.", "So I can't foster, right?"], keys=('foster',), hl=SLATE)
    return c


def s03():   # OPTIMIST: "Wait. Nobody said that's an automatic no." — the delivery driver waves, parcel on his shoulder
    c = full('optimist', 31139, 6.5, fx=0.25, fy=0.42, z=1.0)
    c = top_shade(c)
    name_tag(c, 'optimist')
    slap(c, 'sun', 840, 760, 220, rot=8)
    slap(c, 'nostamp', 330, 1080, 320, rot=-10)
    lay = np.zeros((H, W), np.uint8)
    cv2.line(lay, (150 * 4, 1180 * 4), (520 * 4, 980 * 4), 255, 22 * 4, cv2.LINE_AA, shift=2)
    m = lay.astype(np.float32)[..., None] / 255
    c = c * (1 - m) + np.array(LEAF[:3], np.float32) * m
    c = shade(c)
    caption(c, ["Wait. Nobody said that's", "an automatic no."], keys=('automatic', 'no'), hl=ORANGE)
    return c


def s04():   # REALIST: "The honest answer is: possibly." — the care nurse with a resident
    c = photo_card('realist', frame_of(5820, 4.0), fx=0.42, fy=0.5, cw=940, ch=1000, y=800)
    c = top_shade(c)
    name_tag(c, 'realist')
    slap(c, 'possibly', 820, 470, 230, rot=6)
    word_sticker(c, 'POSSIBLY.', 560, 1220, fill=PURPLE, size=96, rot=-5)
    c = shade(c, 0.66)
    caption(c, 'The honest answer is: possibly.', keys=('possibly',), hl=PURPLE)
    return c


def s05():   # REALIST: "It depends on your hours, your flexibility, your support network and the child's needs."
    c = photo_card('realist', frame_of(5798, 4.0), fx=0.45, fy=0.4, cw=940, ch=1000, y=800, rot=2)
    c = top_shade(c)
    name_tag(c, 'realist')
    for name, x, y, r, lab in (('clock', 200, 560, -8, 'hours'), ('calendar', 880, 560, 7, 'flexibility'),
                               ('network', 200, 1110, 6, 'support network'), ('heart', 880, 1110, -6, "child's needs")):
        slap(c, name, x, y, 210, rot=r)
        s = ts(lab, N9, 32, WHITE)
        p = rrect(s.shape[1] + 40, 56, 28, PURPLE).copy()
        paste_spr(p, s, p.shape[1] / 2, 28)
        draw(c, p, x, y + 140, rot=r * 0.5)
    c = shade(c, 0.66)
    caption(c, ["It depends on your hours, your flexibility,", "your support network and the child's needs."],
            keys=('hours', 'flexibility', 'support', 'network', 'needs'), hl=PURPLE, size=58)
    return c


def s06():   # OPTIMIST: "There's training, meetings, school events…" — on his round
    c = full('optimist', 31136, 5.0, fx=0.5, fy=0.5, z=1.15)
    c = top_shade(c)
    name_tag(c, 'optimist')
    slap(c, 'gradcap', 260, 640, 220, rot=-8)
    slap(c, 'calendar', 830, 600, 200, rot=6)
    slap(c, 'backpack', 830, 1060, 220, rot=8)
    c = shade(c)
    caption(c, ["There's training,", "meetings, school events…"], keys=('training', 'meetings', 'school', 'events'), hl=ORANGE)
    return c


def s07():   # REALIST: "…some in working hours. Plan for that." — the nurse with her notes
    c = photo_card('realist', frame_of(5568, 6.0), fx=0.45, fy=0.4, cw=940, ch=1000, y=800, rot=-2)
    c = top_shade(c)
    name_tag(c, 'realist')
    slap(c, 'briefcase', 830, 520, 220, rot=-6)
    slap(c, 'clipboard', 230, 1060, 220, rot=6)
    word_sticker(c, 'PLAN FOR THAT.', 600, 1230, fill=PURPLE, size=70, rot=-3)
    c = shade(c, 0.66)
    caption(c, ["…some in working hours.", "Plan for that."], keys=('working', 'hours', 'plan'), hl=PURPLE)
    return c


def s08():   # WORRIER: "So how do I know if it works for me?" — on her work call, looking up
    c = full('worrier', 4807, 8.0, fx=0.5, fy=0.42, z=1.35)
    c = top_shade(c)
    name_tag(c, 'worrier')
    slap(c, 'magnifier', 800, 760, 260, rot=10)
    c = shade(c)
    caption(c, ["So how do I know", "if it works for me?"], keys=('works',), hl=SLATE)
    return c


def s09():   # ALL THREE: "You ask." — side by side
    c = np.ones((H, W, 3), np.float32) * np.array(PLUM[:3], np.float32)
    pw = (W - 16) // 3
    for i, (kind, cid, t, fx) in enumerate((('worrier', 4807, 8.0, 0.5), ('optimist', 31139, 6.5, 0.25), ('realist', 5820, 5.0, 0.38))):
        sub = full(kind, cid, t, fx, 0.42, 1.0 if cid != 4807 else 1.6, pw, 1240)
        c[200:1440, i * (pw + 8):i * (pw + 8) + pw] = sub
        label, col, prop, job = CHAR[kind]
        s = ts(label.replace('THE ', ''), N9, 30, WHITE, 0.06)
        p = rrect(s.shape[1] + 34, 54, 27, col).copy()
        paste_spr(p, s, p.shape[1] / 2, 27)
        draw(c, p, i * (pw + 8) + pw / 2, 1390)
        slap(c, prop, i * (pw + 8) + pw / 2, 300, 150, rot=(-8, 6, -4)[i])
    word_sticker(c, 'YOU ASK.', 540, 1560, fill=ORANGE, size=110, rot=-3)
    slap(c, 'phone', 900, 1560, 200, rot=10)
    return c


def s10():   # end card
    return F.s09()


SCENES = [s01, s02, s03, s04, s05, s06, s07, s08, s09, s10]


if __name__ == '__main__':
    os.makedirs(OUT, exist_ok=True)
    which = [int(a) for a in sys.argv[1:]] or range(1, len(SCENES) + 1)
    for j in which:
        cv2.imwrite(f'{OUT}/scene_{j:02d}.png', F.to_u8(SCENES[j - 1]()))
        print('scene', j, flush=True)
    fs = sorted(glob.glob(f'{OUT}/scene_*.png'))
    th = [cv2.resize(cv2.imread(f), (270, 480), interpolation=cv2.INTER_AREA) for f in fs]
    while len(th) % 5:
        th.append(np.zeros_like(th[0]))
    cv2.imwrite(f'{OUT}/storyboard.jpg', np.vstack([np.hstack(th[i:i + 5]) for i in range(0, len(th), 5)]), [cv2.IMWRITE_JPEG_QUALITY, 90])
