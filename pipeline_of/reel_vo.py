"""Organic Fostering — 'Day in the life' reel, voiceover cut (1080x1920, 30 fps, ~29.4 s).

Same look and assets as reel_of.py, retimed so every graphic lands on its voiceover line.
Voiceover start times live in VO and are shared with audio_vo.py.

Usage:
  python3 reel_vo.py still 1.0,4.0
  python3 reel_vo.py range 0 882
"""
import os, sys, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import reel_of as R
from reel_of import *  # noqa: F401,F403

DUR = 29.4
NF = int(DUR * FPS)

# voiceover line start times (seconds) — lines are in workspace_of/tts/lines/<name>.wav
VO = {'hook': 0.15, 'money': 2.55, 'big': 7.0, 'day': 10.55, 'breakfast': 14.45, 'night': 16.95,
      'asking': 18.95, 'message': 21.55, 'end': 25.75}

# scene boundaries
T_HOOK, T_MONEY, T_BED, T_LIGHT, T_SHOES, T_BAG, T_KITCHEN, T_NIGHT, T_MSG, T_END = \
    0.0, 2.0, 6.65, 9.55, 10.45, 12.2, 14.05, 16.65, 21.25, 25.5

HOOK_SEQ = [(1, 1.2), (3, 2.0), (4, 1.4), (5, 0.8), (6, 1.6), (2, 2.2), (7, 1.0), (1, 2.6), (5, 2.4), (3, 3.2),
            (4, 2.6), (6, 2.8), (2, 3.4)]
CUT = 0.16

R.TIMES = [(T_BED, '7:00 am', 'sun'), (T_LIGHT, '7:10 am', 'sun'), (T_SHOES, '7:40 am', 'sun'),
           (T_BAG, '7:45 am', 'sun'), (T_KITCHEN, '7:50 am', 'sun'), (T_NIGHT, '7:30 pm', 'moon')]


def clock_pill_vo(canvas, t):
    if t < T_BED + 0.05 or t > T_MSG:
        return
    # reuse the original drawing with a remapped visibility window
    op_in = prog(t, T_BED + 0.05, T_BED + 0.35)
    op_out = 1 - prog(t, T_MSG - 0.3, T_MSG)
    if op_in * op_out <= 0.01:
        return
    cur = 0
    for i, (tt0, _, _) in enumerate(R.TIMES):
        if t >= tt0:
            cur = i
    tt0, label, icon = R.TIMES[cur]
    prev = R.TIMES[cur - 1][1] if cur > 0 else label
    k = e_out_expo(prog(t, tt0 + 0.05, tt0 + 0.45)) if cur > 0 else 1.0
    op = min(op_in, op_out)
    w, h = 300, 84
    cx, cy = W / 2, 214
    night = icon == 'moon'
    glass(canvas, cx, cy, w, h, r=42, tint_c=(0.2, 0.05, 0.17), tint_a=0.42, opacity=op, blur=22, shadow_a=0.25)
    dot_col = ORANGE_B if not night else hexc('#C9B8FF')
    draw(canvas, radial_sprite(60, dot_col, 2.0), cx - w / 2 + 44, cy, opacity=op, mode='add')
    draw(canvas, solid(sdf_fill(rrect_alpha(18, 18, 9, 2)), dot_col), cx - w / 2 + 44, cy, opacity=op)
    tx = cx + 22
    if k < 1:
        so = word_spr(prev, F_B, 42, WHITE_)
        draw(canvas, blur_sprite(so, 6 * k), tx, cy - 40 * k, opacity=op * (1 - k))
    sn = word_spr(label, F_B, 42, WHITE_)
    draw(canvas, blur_sprite(sn, 6 * (1 - k)), tx, cy + 40 * (1 - k), opacity=op * k)


# ------------------------------------------------------------------ scenes
def sc_hook(t):
    """0.0-2.0 flash montage of the day + the question."""
    i = min(int(t / CUT), len(HOOK_SEQ) - 1)
    ci, off = HOOK_SEQ[i]
    lt = t - i * CUT
    z = 1.28 - 0.18 * e_out_expo(lt / CUT)
    c = grade(clip_frame(ci, off + lt, zoom=z, rot=(-1) ** i * 1.2 * (1 - lt / CUT)), warm=0.5)
    c = c * 0.8
    c += max(0.0, 1 - lt / 0.07) * 0.35
    scrim(c, top=0.0, bottom=0.0)
    k = prog(t, 0.04, 0.4)
    pl = pill('A day in the life', F_B, 44, pad_x=40, pad_y=24, fill=(1, 1, 1, 0.92), border=None, text_color=PLUM,
              dot=MAGENTA)
    draw(c, pl, W / 2, 700, scale=e_out_back(k, 2.0), opacity=min(1, k * 3))
    # question headline synced to the hook voiceover
    kinetic_line(c, 'Where does a fostering', W / 2, 880, 82, t, VO['hook'] + 0.05, color=WHITE_, glow=MAGENTA,
                 glow_str=0.45, shadow_op=0.8, stagger=0.09)
    kinetic_line(c, 'allowance really go?', W / 2, 990, 92, t, VO['hook'] + 1.05, color=WHITE_, fname=F_X,
                 grad=(hexc('#FFE3CF'), hexc('#FF8A3D')), glow=ORANGE_B, glow_str=0.7, shadow_op=0.85, stagger=0.1,
                 sweep_t=VO['hook'] + 1.6)
    return c


def sc_money(t):
    """2.0-6.65 SaaS light stage: 3D coin + 3D £447.60."""
    c = bg_ivory(t)
    t0 = T_MONEY
    lt = t - t0
    leaf(c, 'leaf_green', t, 150, 520 + 20 * math.sin(t * 2), 230, blur=5, op=0.9)
    leaf(c, 'leaf_orange', t, 950, 420 + 20 * math.cos(t * 2.2), 200, blur=6, op=0.85, phase=0.7)
    leaf(c, 'leaf_plum', t, 960, 1560, 260, blur=4, op=0.9, phase=0.3)
    leaf(c, 'leaf_magenta', t, 120, 1450, 210, blur=7, op=0.85, phase=1.1)
    k = prog(lt, 0.0, 0.45)
    e = e_out_expo(k)
    exit_k = prog(t, T_BED - 0.43, T_BED)
    ex = e_in_expo(exit_k)
    cs = (0.15 + 0.85 * e) * (1 + 7 * ex)
    cy = 640 - 220 * (1 - e) + 12 * math.sin(lt * 1.6) * e
    if exit_k < 1:
        seq_draw(c, 'coin', t * 1.2, W / 2, cy, 450 * cs, op=min(1, k * 4) * (1 - ex ** 3),
                 blur=(1 - e) * 6 + ex * 10)
        draw(c, radial_sprite(700, MAGENTA, 2.0), W / 2, cy + 40, scale=cs, opacity=0.25 * min(1, k * 3), mode='add')
    # "From" label on the voice's first word
    kf = prog(t, VO['money'] - 0.05, VO['money'] + 0.35)
    if kf > 0 and exit_k < 1:
        fs = word_spr('From', F_B, 52, hexc('#7A2A6C'))
        draw(c, blur_sprite(fs, 8 * (1 - e_out_expo(kf))), W / 2, 1010 + 20 * (1 - e_out_expo(kf)),
             opacity=min(1, kf * 2) * (1 - ex))
    ts0 = T_MONEY + 0.25
    if t >= ts0 and exit_k < 1:
        idx = min(33, int((t - ts0) * 24))
        f = seq('text_money').frame(idx / 24.0)
        sc = 860 / f.shape[1]
        ff = colorized('text_money', idx, hexc('#2A0826'), hexc('#A3005F'), 1.8)
        sh = blur_sprite(tint(f, (0.25, 0.04, 0.2)), 16)
        draw(c, sh, W / 2, 1167, scale=sc, opacity=0.45 * (1 - ex))
        # sweep timed to "...pounds sixty a week"
        pp = (t - (VO['money'] + 1.9)) / 0.6 * 1.6 - 0.3
        if -0.3 < pp < 1.3:
            ff = sweep(ff, pp, width=0.1, strength=0.8)
        draw(c, ff, W / 2, 1145, scale=sc * (1 + 0.6 * ex) * (1 + 0.012 * math.sin(lt * 2.2)), opacity=(1 - ex))
    tp = VO['money'] + 1.1
    if t >= tp:
        kp = prog(t, tp, tp + 0.4)
        pl = pill('Weekly fostering allowance', F_B, 38, pad_x=36, pad_y=20, fill=PLUM + (), border=None,
                  text_color=IVORY, dot=GREEN)
        draw(c, pl, W / 2, 1330 + 30 * (1 - e_out_expo(kp)), scale=0.9 + 0.1 * e_out_back(kp),
             opacity=min(1, kp * 3) * (1 - ex))
    if exit_k <= 0.0:
        type_line(c, 'for each child', W / 2, 1470, 64, t, VO['money'] + 3.0, cps=22, color=MAGENTA)
    tb = T_BED - 0.47
    if t > tb:
        for j, (col, ang) in enumerate([(ORANGE_B, -2.3), (MAGENTA, -0.6), (GREEN, 0.9), (PEACH, 2.5)]):
            kk = e_in_cubic(prog(t, tb, T_BED))
            r = 40 + 900 * kk
            x = W / 2 + math.cos(ang) * r
            y = 640 + math.sin(ang) * r * 1.2
            draw(c, radial_sprite(220, col[:3], 2.0), x, y, opacity=0.9, mode='add')
            draw(c, radial_sprite(80, (1, 1, 1), 2.5, core=0.6), x, y, opacity=0.9, mode='add')
    if exit_k > 0.6:
        c += (exit_k - 0.6) / 0.4 * 0.9
    return c


def sc_bedroom(t):
    lt = t - T_BED
    c = grade(clip_frame(1, 0.4 + lt * 0.78, zoom=1.04 + 0.07 * (lt / 2.9)), warm=0.6)
    scrim(c, top=0.66, top_h=0.5, bottom=0.25)
    c += max(0.0, 1 - lt / 0.25) * 0.9
    seq_draw(c, 'sun', t, 950, 335 + 10 * math.sin(t * 2), 140, op=min(1, prog(t, T_BED + 0.5, T_BED + 0.9)))
    v = VO['big']
    out = T_LIGHT - 0.35
    kinetic_line(c, 'Sometimes,', W / 2, 470, 104, t, v - 0.05, color=WHITE_, glow=MAGENTA, glow_str=0.35,
                 out_t=out, out_dur=0.25)
    kinetic_line(c, "it's not the", W / 2, 600, 104, t, v + 0.65, color=WHITE_, glow=MAGENTA, glow_str=0.35,
                 out_t=out + 0.03, out_dur=0.25)
    kinetic_line(c, 'big things.', W / 2, 735, 118, t, v + 1.4, color=WHITE_, fname=F_X,
                 grad=(hexc('#FFE3CF'), hexc('#FF8A3D')), glow=ORANGE_B, glow_str=0.75, sweep_t=v + 1.9,
                 shadow_op=0.85, out_t=out + 0.06, out_dur=0.25)
    return c


def sc_light(t):
    lt = t - T_LIGHT
    c = grade(clip_frame(2, 1.2 + lt, zoom=1.06 + 0.05 * lt), warm=0.4)
    scrim(c, top=0.3, bottom=0.2)
    orb(c, t, T_LIGHT + 0.12, T_LIGHT + 0.72, (-120, 300), (300, 520), (560, 1080), ORANGE_B)
    return c


def sc_shoes(t):
    lt = t - T_SHOES
    c = grade(clip_frame(3, 0.5 + lt * 0.9, zoom=1.05 + 0.04 * lt), warm=0.4)
    scrim(c, top=0.3, bottom=0.2)
    orb(c, t, T_SHOES + 0.02, T_SHOES + 0.42, (1200, 500), (900, 760), (560, 1190), MAGENTA)
    tag(c, t, T_SHOES + 0.42, W / 2, 960, 'School shoes')
    return c


def sc_bag(t):
    lt = t - T_BAG
    c = grade(clip_frame(4, 0.3 + lt * 0.9, zoom=1.04 + 0.05 * lt, cx=W / 2 - 40), warm=0.4)
    scrim(c, top=0.3, bottom=0.25)
    orb(c, t, T_BAG + 0.02, T_BAG + 0.37, (-150, 1500), (200, 900), (470, 640), GREEN)
    tag(c, t, T_BAG + 0.37, W / 2, 1240, 'Books & packed lunch')
    return c


def sc_kitchen(t):
    lt = t - T_KITCHEN
    c = grade(clip_frame(5, 0.1 + lt * 0.9, zoom=1.03 + 0.04 * lt), warm=0.5)
    scrim(c, top=0.78, top_h=0.5, bottom=0.2)
    orb(c, t, T_KITCHEN + 0.05, T_KITCHEN + 0.4, (1250, 1700), (900, 1300), (420, 1090), PEACH)
    v = VO['breakfast']
    out = T_NIGHT - 0.3
    kinetic_line(c, "It's breakfast", W / 2, 470, 104, t, v - 0.05, color=WHITE_, glow=ORANGE_B, glow_str=0.35,
                 out_t=out, out_dur=0.3)
    kinetic_line(c, 'at the table.', W / 2, 600, 104, t, v + 0.65, color=WHITE_, fname=F_X,
                 grad=(hexc('#FFE3CF'), hexc('#FF8A3D')), glow=ORANGE_B, glow_str=0.6, sweep_t=v + 1.1,
                 shadow_op=0.9, out_t=out + 0.03, out_dur=0.3)
    kh = prog(t, v + 1.2, v + 1.6)
    if kh > 0:
        seq_draw(c, 'heart', t, 905, 790 + 10 * math.sin(t * 3), 120 * e_out_back(kh, 2.6),
                 op=min(1, kh * 3) * (1 - prog(t, out - 0.05, out + 0.2)))
    tag(c, t, T_KITCHEN + 0.4, W / 2, 1360, 'Breakfast')
    return c


def sc_night(t):
    lt = t - T_NIGHT
    c = grade(clip_frame(6, 0.05 + lt * 0.85, zoom=1.04 + 0.03 * lt), night=0.6)
    scrim(c, top=0.5, bottom=0.25)
    seq_draw(c, 'moon', t, 890, 400 + 10 * math.sin(t * 1.6), 170, op=min(1, prog(t, T_NIGHT + 0.3, T_NIGHT + 0.7)))
    v, a = VO['night'], VO['asking']
    kinetic_line(c, 'A goodnight', W / 2, 470, 104, t, v - 0.05, color=WHITE_, glow=hexc('#C9B8FF'), glow_str=0.4,
                 out_t=a - 0.35, out_dur=0.3)
    kinetic_line(c, 'at bedtime.', W / 2, 600, 104, t, v + 0.7, color=WHITE_, fname=F_X,
                 grad=(hexc('#FFF1E3'), hexc('#FFB36B')), glow=ORANGE_B, glow_str=0.5, sweep_t=v + 1.1,
                 out_t=a - 0.32, out_dur=0.3)
    kinetic_line(c, 'Someone asking,', W / 2, 520, 84, t, a - 0.05, color=WHITE_, fname=F_B, glow=MAGENTA,
                 glow_str=0.3, out_t=T_MSG - 0.3, out_dur=0.25)
    chat_bubble(c, t, a + 0.35, W / 2, 700, '“How was your day?”', typing_until=a + 0.85)
    return c


def sc_message(t):
    c = bg_plum(t)
    lt = t - T_MSG
    k = prog(t, T_MSG + 0.05, T_MSG + 0.75)
    e = e_out_expo(k)
    cw, ch = 700, 900
    img = grade(clip_frame(7, 0.3 + lt * 0.9, zoom=1.08), warm=0.4)
    small = cv2.resize(img, (cw, int(cw * H / W)), interpolation=cv2.INTER_AREA)
    y0 = (small.shape[0] - ch) // 2
    card = small[y0:y0 + ch]
    a = sdf_fill(rrect_alpha(cw, ch, 40, 0))
    spr = rgb_to_sprite(card, a)
    sh = blur_sprite(solid(a, (0.05, 0.0, 0.04, 1)), 30)
    ry = 8 * math.sin(lt * 1.0)
    cy_ = 1330 + 300 * (1 - e)
    draw3d(c, sh, W / 2, cy_ + 30, 40, w=cw * 1.04, rx=6, ry=ry, opacity=0.6 * e)
    draw3d(c, spr, W / 2, cy_, 0, w=cw, rx=6 * (1 - e) + 3, ry=ry, opacity=e)
    leaf(c, 'leaf_green', t, 150, 1050 + 20 * math.sin(t * 2), 220, blur=3, op=e)
    leaf(c, 'leaf_magenta', t, 950, 1700, 240, blur=2, op=e, phase=0.6)
    leaf(c, 'leaf_orange', t, 940, 980, 160, blur=6, op=e * 0.8, phase=1.3)
    v = VO['message']
    kinetic_line(c, 'Sometimes, ordinary moments', W / 2, 300, 64, t, v - 0.05, color=WHITE_, fname=F_B,
                 stagger=0.12, glow=MAGENTA, glow_str=0.4, shadow_op=0.3)
    kinetic_line(c, 'help create', W / 2, 395, 64, t, v + 1.4, color=WHITE_, fname=F_B, glow=MAGENTA,
                 glow_str=0.4, shadow_op=0.3)
    tx = v + 1.98
    kx = prog(t, tx, tx + 0.45)
    if kx > 0:
        fi_ = int(t * 24) % 24
        f = seq('text_extra').frame(fi_ / 24.0)
        sc = 960 / f.shape[1] * (0.85 + 0.15 * e_out_back(kx, 1.8))
        glow_add(c, f, W / 2, 545, MAGENTA, sigma=40, strength=0.28 * kx, scale=sc)
        f = colorized('text_extra', fi_, hexc('#3A0C33'), hexc('#FFE6F0'), 2.2)
        p = (t - (tx + 0.5)) / 0.8 * 1.6 - 0.3
        ff = sweep(f, p, width=0.07, strength=0.5) if -0.3 < p < 1.3 else f
        draw(c, blur_sprite(ff, (1 - kx) * 10), W / 2, 545 + 40 * (1 - e_out_expo(kx)), scale=sc, opacity=min(1, kx * 2))
    kinetic_line(c, 'change.', W / 2, 700, 118, t, v + 3.05, color=WHITE_, fname=F_X,
                 grad=(hexc('#FFD4BA'), hexc('#FF6411')), glow=ORANGE_B, glow_str=0.9, sweep_t=v + 3.5, shadow_op=0.3)
    return c


def sc_end(t):
    c = bg_ivory(t)
    lt = t - T_END
    leaf(c, 'leaf_green', t, 160 - 60 * (1 - e_out_expo(prog(lt, 0, 0.8))), 500, 200, blur=3)
    leaf(c, 'leaf_orange', t, 930 + 60 * (1 - e_out_expo(prog(lt, 0.1, 0.9))), 430, 170, blur=5, phase=0.5)
    leaf(c, 'leaf_magenta', t, 940, 1660, 230, blur=2, phase=1.0)
    leaf(c, 'leaf_plum', t, 140, 1600, 190, blur=4, phase=0.2)
    k = prog(t, T_END + 0.1, T_END + 0.75)
    e = e_out_expo(k)
    lg = logo_full()
    sc = 860 / lg.shape[1] * (0.94 + 0.06 * e)
    draw(c, lg, W / 2, 820 + 40 * (1 - e), scale=sc, opacity=min(1, k * 1.6))
    colour_bar(c, W / 2, 1100, 520, 12, prog(t, T_END + 0.6, T_END + 1.15))
    v = VO['end']
    kinetic_line(c, 'Room to grow, roots to keep.', W / 2, 1200, 58, t, v + 1.3, color=PLUM, fname=F_B,
                 stagger=0.1, shadow_op=0.0, rise=24)
    kp = prog(t, v + 2.3, v + 2.7)
    if kp > 0:
        pl = pill('organicfostering.co.uk', F_B, 40, pad_x=40, pad_y=22, fill=PLUM + (), border=None,
                  text_color=IVORY)
        draw(c, pl, W / 2, 1330 + 20 * (1 - e_out_expo(kp)), scale=0.9 + 0.1 * e_out_back(kp), opacity=min(1, kp * 3))
    kf = prog(t, v + 2.6, v + 3.0)
    if kf > 0:
        fp = word_spr('Allowance shown is the weekly rate for one child aged 0 to 4.', F_M, 26, MUTEDC)
        fp2 = word_spr('Rates vary by age and region.', F_M, 26, MUTEDC)
        draw(c, fp, W / 2, 1500, opacity=kf)
        draw(c, fp2, W / 2, 1540, opacity=kf)
    return c


SCENES = [(T_HOOK, T_MONEY, sc_hook), (T_MONEY, T_BED, sc_money), (T_BED, T_LIGHT, sc_bedroom),
          (T_LIGHT, T_SHOES, sc_light), (T_SHOES, T_BAG, sc_shoes), (T_BAG, T_KITCHEN, sc_bag),
          (T_KITCHEN, T_NIGHT, sc_kitchen), (T_NIGHT, T_MSG, sc_night), (T_MSG, T_END, sc_message),
          (T_END, DUR + 1, sc_end)]


def scene_at(t):
    for a, b, f in SCENES:
        if a <= t < b:
            return f
    return SCENES[-1][2]


def win(t, c0, half):
    return max(0.0, 1 - abs((t - c0) / half))


def render_raw(t):
    c = scene_at(t)(t)
    if T_LIGHT - 0.15 <= t < T_LIGHT:
        c = whip(c, prog(t, T_LIGHT - 0.15, T_LIGHT), -1)
    elif T_LIGHT <= t < T_LIGHT + 0.15:
        c = whip(c, 1 - prog(t, T_LIGHT, T_LIGHT + 0.15), -1)
    if abs(t - T_SHOES) < 0.1:
        c = whip(c, win(t, T_SHOES, 0.1), 1)
    if abs(t - T_BAG) < 0.1:
        c = zoom_blur(c, win(t, T_BAG, 0.1) * 3)
    if T_KITCHEN - 0.15 <= t < T_KITCHEN + 0.15:
        light_leak(c, prog(t, T_KITCHEN - 0.15, T_KITCHEN + 0.15), (1.0, 0.62, 0.35), 1)
    if abs(t - T_NIGHT) < 0.15:
        c *= 1 - 0.85 * win(t, T_NIGHT, 0.15)
    if abs(t - T_MSG) < 0.2:
        k = win(t, T_MSG, 0.2)
        c = zoom_blur(c, k * 4)
        c += k ** 2 * np.array([0.9, 0.4, 0.7], np.float32)
    if abs(t - T_END) < 0.15:
        c += win(t, T_END, 0.15) ** 1.5 * 0.95
    clock_pill_vo(c, t)
    dx = dy = 0.0
    for st in (T_MONEY, T_BED, T_SHOES + 0.42, T_BAG + 0.37, VO['message'] + 1.98):
        a, b = shake(t, st, amp=10)
        dx += a
        dy += b
    if abs(dx) + abs(dy) > 0.5:
        c = cv2.warpAffine(c, np.float32([[1, 0, dx], [0, 1, dy]]), (W, H), borderMode=cv2.BORDER_REFLECT)
    if t > DUR - 0.45:
        c *= 1 - 0.9 * prog(t, DUR - 0.45, DUR)
    return c


FAST = [(0.0, 2.05), (T_BED - 0.5, T_BED + 0.1), (T_LIGHT - 0.2, T_LIGHT + 0.85), (T_SHOES - 0.1, T_SHOES + 0.5),
        (T_BAG - 0.1, T_BAG + 0.45), (T_KITCHEN, T_KITCHEN + 0.45), (T_MSG - 0.25, T_MSG + 0.25)]


def render(fi):
    t = fi / FPS
    sub = 3 if any(a <= t < b for a, b in FAST) else 1
    if sub == 1:
        c = render_raw(t)
    else:
        acc = None
        for k in range(sub):
            r = render_raw(max(0.0, t + (k / sub - 0.5) * 0.5 / FPS))
            acc = r if acc is None else acc + r
        c = acc / sub
    ca = 2.5 if t < T_MONEY else 0.0
    night = T_NIGHT <= t < T_MSG
    return post(c, fi, bloom=0.45 if not night else 0.6, grain=0.018, ca=ca)


if __name__ == '__main__':
    mode = sys.argv[1]
    if mode == 'still':
        os.makedirs(f'{S}/stills_vo', exist_ok=True)
        for ts in sys.argv[2].split(','):
            t = float(ts)
            cv2.imwrite(f'{S}/stills_vo/s_{t:05.2f}.jpg', to_u8(render(int(round(t * FPS)))), [cv2.IMWRITE_JPEG_QUALITY, 92])
            print('still', t, flush=True)
    elif mode == 'range':
        a, b = int(sys.argv[2]), int(sys.argv[3])
        os.makedirs(f'{S}/frames_vo', exist_ok=True)
        for fi in range(a, b):
            cv2.imwrite(f'{S}/frames_vo/{fi:04d}.png', to_u8(render(fi)), [cv2.IMWRITE_PNG_COMPRESSION, 1])
            print('frame', fi, flush=True)
