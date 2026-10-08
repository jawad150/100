"""reel3_vo.py: REEL 3 "Nurture · Develop · Grow" with voiceover (retime.py). Source times from reel3.py (92 BPM,
B(n) = n * 0.652 s). Each chapter word is spoken as it lands and its sub-line holds for the read (footage inside
the letters / full frame never slower than 0.3-0.4x); no hold starts inside a gust, glide, spring or pop; the
kinds-of-care dial turns slower so every tag can be read; each trust pill gets its line; the end-card lines play over
the settled card.

    python3 retime.py plan reel3_vo ; python3 retime.py audio reel3_vo
    python3 render.py reel3_vo --workers 4 --audio ../../workspace3/audio/reel3_vo_mix.wav
"""
import retime
import reel3 as M

B = M.B
TT = M.TRUST_T          # 20.543 / 20.870 / 21.196

SLOTS = [
    # HOOK + GROWTH: "A small beginning..." from frame 0; "...can change the direction of a life." on b4, read until
    # just before the NURTURE leaf gust (no slow-down inside the gust)
    dict(lines=['small_beginning'], at=0.0, delay=0.1, hold=(B(2.3), B(3) - 0.05), min_rate=1.0, tail=0.0),
    dict(lines=['change_direction'], at=B(4), delay=0.0, hold=(B(6), M.T_NUR - 0.33), tail=0.6),
    # NURTURE: the word as it lands, then its sub-line; the hold starts after the gust, the house and pill pops
    # (T_NUR + 0.6); the settled letters slow evenly (footage inside them >= 0.3x); the hit lands before the duck
    dict(lines=['nurture', 'safe_home'], at=M.T_NUR, delay=0.1, gap=0.25, hold=(M.T_NUR + 0.6, B(10)), min_rate=0.3,
         tail=-0.6, duck_lead=-0.05),
    # DEVELOP: the word over the settled letters; the 380 px glide-up and the chip springs run 1:1; the sub-line is
    # read once it has landed (D_UP + 0.45) while the chips and puzzle pieces settle
    dict(lines=['develop'], at=M.T_DEV + 0.05, delay=0.0, hold=(M.T_DEV + 0.1, M.D_UP - 0.26), min_rate=0.35,
         tail=0.1, duck_lead=-0.05),
    dict(lines=['matching'], at=M.D_UP + 0.45, delay=0.05, hold=(M.D_UP + 0.52, B(17.8)), min_rate=0.3, tail=0.2),
    # GROW: the sprout pop, "03 / 03" pill and word settle run 1:1; then the word + sub-line over the settled letters
    dict(lines=['grow', 'steady_care'], at=M.T_GRO + 0.05, delay=0.0, gap=0.25, hold=(M.T_GRO + 0.45, B(20)),
         min_rate=0.3, tail=-0.4, duck_lead=-0.05),
    # KINDS OF CARE: the headline (spoken once it reads), then the dial turns at ~0.6x so each tag reads
    dict(lines=['kinds_of_care'], at=B(23.5), delay=0.15, hold=(B(27), B(30.8)), min_hold=4.2, tail=0.4),
    # TRUST: one line per pill; contiguous holds, so no pill sags at a hand-off
    dict(lines=['independent'], at=TT[0], delay=0.0, hold=(TT[0] + 0.08, TT[1] + 0.08), min_rate=0.06, tail=0.05),
    dict(lines=['cultural'], at=TT[1], delay=0.0, hold=(TT[1] + 0.08, TT[2] + 0.15), min_rate=0.06, tail=0.05),
    dict(lines=['ofsted'], at=TT[2], delay=0.0, hold=(TT[2] + 0.15, M.TRUST_OUT), min_rate=0.08, tail=0.35),
    # END: the leaves' flight, tagline typing, CTA pop, click and logo light sweep all run 1:1 (they overlap within
    # 0.6 s, so nothing there can slow); "Nurture. Develop. Grow." and "Start your enquiry..." over the settled card
    dict(lines=['tagline', 'start_enquiry'], at=M.E_CLICK + 0.05, delay=0.1, gap=0.35, hold=(24.96, M.DUR),
         min_rate=0.1, tail=1.6),
]

retime.wrap(globals(), M, 'reel3', SLOTS)
