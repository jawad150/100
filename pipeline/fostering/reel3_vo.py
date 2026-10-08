"""reel3_vo.py: REEL 3 "Nurture · Develop · Grow" with voiceover (retime.py). Source times from reel3.py (92 BPM,
B(n) = n * 0.652 s). Each chapter word is spoken as it lands and its sub-line holds for the read (footage inside
the letters / full frame never slower than 0.3-0.4x); the chips pop as "culture" is said; the kinds-of-care dial
turns slower so every tag can be read; each trust pill gets its line; the CTA is clicked on "Start your enquiry".

    python3 retime.py plan reel3_vo ; python3 retime.py audio reel3_vo
    python3 render.py reel3_vo --workers 4 --audio ../../workspace3/audio/reel3_vo_mix.wav
"""
import retime
import reel3 as M

B = M.B
TT = M.TRUST_T          # 20.543 / 20.870 / 21.196

SLOTS = [
    # HOOK + GROWTH: "A small beginning..." from frame 0; "...can change the direction of a life." on b4
    dict(lines=['small_beginning'], at=0.0, delay=0.1, hold=(B(2.3), B(3) - 0.05), min_rate=1.0, tail=0.0),
    dict(lines=['change_direction'], at=B(4), delay=0.0, hold=(B(6), B(8) - 0.1), tail=0.35),
    # NURTURE: the word, then its sub-line; the settled letters slow evenly (footage inside them >= 0.3x) and the
    # line finishes over the zoom through the U
    dict(lines=['nurture', 'safe_home'], at=M.T_NUR, delay=0.1, gap=0.25, hold=(M.T_NUR + 0.1, B(10)), min_rate=0.3,
         tail=-0.6),
    # DEVELOP: the whole chapter slows evenly (~0.45x) so the chips pop near "culture" and the line ends before the
    # push-through into GROW
    dict(lines=['develop', 'matching'], at=M.T_DEV + 0.05, delay=0.0, gap=0.3, hold=(M.T_DEV + 0.1, B(17.8)),
         min_rate=0.35, tail=0.2),
    # GROW: the word + its sub-line over the settled letters; it may run on over the zoom through the O
    dict(lines=['grow', 'steady_care'], at=M.T_GRO + 0.05, delay=0.0, gap=0.25, hold=(M.T_GRO + 0.1, B(20)),
         min_rate=0.35, tail=-0.4),
    # KINDS OF CARE: the headline, then the dial turns at ~0.6x so each tag reads
    dict(lines=['kinds_of_care'], at=B(23.5), delay=0.0, hold=(B(27), B(30.8)), min_hold=4.2, tail=0.4),
    # TRUST: one line per pill
    dict(lines=['independent'], at=TT[0], delay=0.0, hold=(TT[0] + 0.08, TT[1] - 0.03), min_rate=0.06, tail=0.05),
    dict(lines=['cultural'], at=TT[1], delay=0.0, hold=(TT[1] + 0.08, TT[2] - 0.03), min_rate=0.06, tail=0.05),
    dict(lines=['ofsted'], at=TT[2], delay=0.0, hold=(TT[2] + 0.15, M.TRUST_OUT), min_rate=0.08, tail=0.35),
    # END: the tagline as it types on (the CTA waits), then "Start your enquiry..." as the CTA pops and is clicked
    dict(lines=['tagline'], at=B(35.5), delay=0.05, hold=(B(35.6), B(36) - 0.02), min_rate=0.05, tail=0.1),
    dict(lines=['start_enquiry'], at=B(36), delay=0.0, hold=(24.4, M.DUR), tail=1.6),
]

retime.wrap(globals(), M, 'reel3', SLOTS)
