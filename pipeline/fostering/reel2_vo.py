"""reel2_vo.py: REEL 2 "Financial support" with voiceover (retime.py). Source times from reel2.py (128 BPM,
B(n) = n * 0.46875 s). The VO starts over the coin flip so "financial" lands on the title slam; each section
holds on its settled copy while its line is read (number, the 52-week total and fine print, the parked tag ring, the
end card); numbers are said just after they land; the calculator's continuous action plays at 1x; the coin, tunnel,
whips, wipes, zoom-throughs, the coin orbit and the beat pulse keep their speed.

    python3 retime.py plan reel2_vo ; python3 retime.py audio reel2_vo
    python3 render.py reel2_vo --workers 4 --audio ../../workspace3/audio/reel2_vo_mix.wav
"""
import retime
import reel2 as M

B = M.B

SLOTS = [
    # HOOK: "financial" lands on the title slam; the settled title holds for the read
    dict(lines=['financial_support'], at=0.0, delay=0.2, hold=(B(4) + 0.15, B(5) - 0.1), min_rate=0.08, tail=0.1),
    # SCENE B: "four" is said just after the counter lands on £447.60 (the coin orbit keeps its speed: ORBIT_CLOCK)
    dict(lines=['from_amount'], at=M.NUM_ROLL[1], delay=-0.22, hold=(B(9) + 0.3, B(11) - 0.15), min_rate=0.08,
         tail=0.6),
    # CALCULATOR: chip clicks, bar growth and the cursor are one continuous action from B12 to the drag: the line
    # plays over it at 1x (no hold)
    dict(lines=['rise_with_age'], at=B(12) + 0.2, delay=0.0, hold=None),
    # the 52-week total and the fine print: one hold once the cursor has left, one rate for both lines; "fifty-two"
    # is said just after 52 lands
    dict(lines=['fifty_two_weeks', 'rates_vary'], at=M.DRAG[1], delay=-0.25, gap=0.45,
         hold=(M.DRAG[1] + 1.0, B(27) - 0.25), tail=0.4),
    dict(lines=['support_household'], at=B(27.5), delay=0.0, hold=(B(32) + 0.3, B(34)), min_hold=2.0, tail=0.3),
    # the hold ends before the light-leak exit; >= 0.7 s of reading
    dict(lines=['recognition'], at=B(38), delay=0.0, hold=(B(40), M.T_END - 0.36), min_rate=0.5, tail=0.7),
    dict(lines=['discuss'], at=M.T_BTN, delay=0.0, hold=(22.4, M.DUR), tail=1.6),
]

retime.wrap(globals(), M, 'reel2', SLOTS)
# continuous motion keeps its speed through the holds: the coin orbit / spins run on output time from T_NUM, the
# background beat pulse on output time (the music grid)
M.ORBIT_CLOCK = lambda s, w=WARP: M.T_NUM + w.out(s) - w.out(M.T_NUM)
M.BEAT_CLOCK = WARP.out
