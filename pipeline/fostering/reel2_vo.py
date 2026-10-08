"""reel2_vo.py: REEL 2 "Financial support" with voiceover (retime.py). Source times from reel2.py (128 BPM,
B(n) = n * 0.46875 s). The VO starts over the coin flip so "financial" lands on the title slam; each section
holds on its settled copy while its line is read (number, calculator chips, the 52-week total, the fine print,
the parked tag ring, the end card); the coin, tunnel, whips, wipes and zoom-throughs keep their speed.

    python3 retime.py plan reel2_vo ; python3 retime.py audio reel2_vo
    python3 render.py reel2_vo --workers 4 --audio ../../workspace3/audio/reel2_vo_mix.wav
"""
import retime
import reel2 as M

B = M.B

SLOTS = [
    dict(lines=['financial_support'], at=0.0, delay=0.2, hold=(B(4) + 0.15, B(5) - 0.1), min_rate=0.08, tail=0.1),
    dict(lines=['from_amount'], at=M.T_NUM, delay=0.05, hold=(B(9) + 0.3, B(11) - 0.15), min_rate=0.1, tail=0.15),
    dict(lines=['rise_with_age'], at=B(12) + 0.2, delay=0.0, hold=(B(15) + 0.1, B(16)), tail=0.15),
    dict(lines=['fifty_two_weeks'], at=B(17.5), delay=0.0, hold=(B(20) + 0.25, B(23)), tail=0.25),
    dict(lines=['rates_vary'], at=B(23), delay=0.05, hold=(B(23) + 0.05, B(27) - 0.25), tail=0.4),
    dict(lines=['support_household'], at=B(27.5), delay=0.0, hold=(B(32) + 0.3, B(34)), min_hold=2.0, tail=0.3),
    dict(lines=['recognition'], at=B(38), delay=0.0, hold=(B(40), B(42.5)), min_rate=0.6, tail=0.3),
    dict(lines=['discuss'], at=M.T_BTN, delay=0.0, hold=(22.4, M.DUR), tail=1.6),
]

retime.wrap(globals(), M, 'reel2', SLOTS)
