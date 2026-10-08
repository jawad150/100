"""anim4_vo.py: ANIM 4 "£447.60: where does it go?" with voiceover (retime.py). Source times from anim4.py
(B(n) = n * 0.5 s; ARRIVE / LEAVE per station). The hook and the final number get a near-freeze on the settled
type (the spinning coins float like bullet time) while the amount is read; each station's whole dwell slows
evenly (>= 0.35x, so pops stay lively) to fit its line; camera moves between stations stay 1:1.

    python3 retime.py plan anim4_vo ; python3 retime.py audio anim4_vo
    python3 render.py anim4_vo --workers 4 --audio ../../workspace3/audio/anim4_vo_mix.wav
"""
import retime
import anim4 as M

A, L = M.ARRIVE, M.LEAVE

SLOTS = [
    # HOOK: "£447.60 a week." over the slam + "per week" (float), "But where does it go?" with the "?" and chips
    dict(lines=['amount'], at=0.0, delay=0.05, hold=(0.6, 1.0), min_rate=0.1, tail=0.1),
    dict(lines=['where'], at=M.T_Q, delay=0.08, hold=(1.9, 2.25), min_hold=1.6, tail=0.4),
    # the coins break into the ribbon; the message writes in line by line
    dict(lines=['payments_help'], at=M.T_MSG, delay=0.05, hold=(M.T_MSG + 0.8, L['s0']), tail=0.45),
    # STATIONS: headline lands at ARRIVE + 0.25; the whole dwell slows evenly
    dict(lines=['home'], at=A['home'] + 0.25, delay=0.0, hold=(A['home'], L['home']), min_rate=0.35, tail=0.3),
    dict(lines=['food'], at=A['food'] + 0.25, delay=0.0, hold=(A['food'], L['food']), min_rate=0.35, tail=0.3),
    dict(lines=['clothes'], at=A['cloth'] + 0.25, delay=0.0, hold=(A['cloth'], L['cloth']), min_rate=0.35, tail=0.3),
    dict(lines=['travel'], at=A['travel'] + 0.25, delay=0.0, hold=(A['travel'], L['travel']), min_rate=0.35,
         tail=0.3),
    # the child gathers everything
    dict(lines=['everyday_life'], at=A['child'] + 0.25, delay=0.05, hold=(A['child'], M.T_FADE[0]), min_rate=0.35,
         tail=0.35),
    # FINAL: "£447.60 a week, per child aged nought to four" over a near-freeze on the settled number + statement
    dict(lines=['final_amount'], at=M.T_NUM2, delay=0.05, hold=(M.T_STMT + 0.1, M.T_LOGO), min_rate=0.06,
         tail=0.15),
    # END CARD: the question as it lands, then "Start the conversation..." as the CTA pops and is clicked
    dict(lines=['want_understand'], at=M.T_ASK, delay=0.05, hold=(M.T_ASK + 0.05, M.T_BTN), min_rate=0.065,
         tail=0.1),
    dict(lines=['start_conversation'], at=M.T_BTN, delay=0.0, hold=(M.T_CLICK + 0.56, M.DUR), tail=1.6),
]

retime.wrap(globals(), M, 'anim4', SLOTS)
