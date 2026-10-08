"""reel1_vo.py: REEL 1 "Could you?" with voiceover (retime.py). Source times from reel1.py (beat 0.5 s).
Each hook word is spoken on its slam (the montage slows per slam, extensions on eighth notes); the question, each
checklist tick, each support tile and the payoff lines hold for their read; the end card holds the cursor just
before the click so "Start your enquiry today" lands on it.

    python3 retime.py plan reel1_vo ; python3 retime.py audio reel1_vo
    python3 render.py reel1_vo --workers 4 --audio ../../workspace3/audio/reel1_vo_mix.wav
"""
import retime
import reel1 as M

T = M.TICKS            # 6.5 / 7.25 / 8.0 / 8.75 / 9.5

SLOTS = [
    # HOOK MONTAGE: one line per slammed word (0.5 / 1.0 / 1.5 + 2.0)
    dict(lines=['safe_home'], at=0.5, delay=0.0, hold=(0.5, 1.0), min_rate=0.4, tail=0.02, quant=0.25),
    dict(lines=['everyday_care'], at=1.0, delay=0.0, hold=(1.0, 1.5), min_rate=0.4, tail=0.02, quant=0.25),
    dict(lines=['place_belong'], at=1.5, delay=0.0, hold=(1.5, 2.5), min_rate=0.4, tail=0.05, quant=0.25),
    # THE QUESTION: words land 3.25-4.0; hold for the read before the whip down (5.25)
    dict(lines=['could_you'], at=3.25, delay=0.0, hold=(4.3, 5.2), min_hold=1.2, tail=0.35),
    # CHECKLIST: header, then one line per tick, the toast
    dict(lines=['eligible'], at=5.9, delay=0.0, hold=(6.0, 6.45), tail=0.1),
    dict(lines=['bedroom'], at=T[0], delay=0.05, hold=(T[0] + 0.35, T[1] - 0.05), tail=0.1),
    dict(lines=['time_flex'], at=T[1], delay=0.05, hold=(T[1] + 0.35, T[2] - 0.05), tail=0.1),
    dict(lines=['single'], at=T[2], delay=0.05, hold=(T[2] + 0.35, T[3] - 0.05), tail=0.1),
    dict(lines=['rent_own'], at=T[3], delay=0.05, hold=(T[3] + 0.35, T[4] - 0.05), tail=0.1),
    dict(lines=['no_experience'], at=T[4], delay=0.05, hold=(T[4] + 0.25, M.RING_POP), min_rate=0.1, tail=0.15),
    dict(lines=['great_fit'], at=M.TOAST_T, delay=0.05, hold=(M.TOAST_T + 0.35, M.T_DOCK - 0.25), tail=0.5),
    # SUPPORT DOCK: headline, then each focused tile (12.5 / 14.5 / 16.5); tile 3 plays footage (>= 0.25x)
    dict(lines=['support_role'], at=11.8, delay=0.0, hold=(12.0, 12.45), tail=0.1),
    dict(lines=['training'], at=12.5, delay=0.05, hold=(13.0, 14.45), tail=0.1),
    dict(lines=['ongoing'], at=14.5, delay=0.05, hold=(15.0, 16.45), tail=0.1),
    dict(lines=['allowance'], at=16.5, delay=0.05, hold=(16.9, 18.2), min_rate=0.25, tail=0.3),
    # PAYOFF (c08 already 0.6x slow-mo: keep >= 0.5)
    dict(lines=['open_home'], at=M.PAY_L1, delay=0.0, hold=(M.PAY_L1 + 0.25, M.PAY_L2), min_rate=0.5, tail=0.1),
    dict(lines=['change_life'], at=M.PAY_L2, delay=0.0, hold=(M.PAY_L2 + 0.3, 20.65), min_rate=0.5, tail=0.3),
    # END CARD: wordmark -> "Organic Fostering, rated Good by Ofsted." (cursor waits before the click), then the CTA
    dict(lines=['ofsted'], at=21.75, delay=0.0, hold=(23.3, 23.45), min_rate=0.05, tail=0.1),
    dict(lines=['start_enquiry'], at=23.5, delay=0.0, hold=(24.35, M.DUR), tail=1.6),
]

retime.wrap(globals(), M, 'reel1', SLOTS)
