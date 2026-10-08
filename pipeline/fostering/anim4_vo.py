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
    # (the hold ends 0.12 s before the "?" slam so the ramp back to 1x is done when it lands; "But where..." starts
    # after the slam's transient, ducked from its first word)
    dict(lines=['amount'], at=0.0, delay=0.35, hold=(0.6, 0.88), min_rate=0.085, tail=0.0),
    dict(lines=['where'], at=M.T_Q, delay=0.14, hold=(1.9, 2.25), min_hold=1.2, tail=0.4, duck_lead=0.0),
    # the coins break into the ribbon; the message writes in line by line
    # (tails: >= 0.7 s of reading after the speech ends, before each headline fades)
    dict(lines=['payments_help'], at=M.T_MSG, delay=0.05, hold=(M.T_MSG + 0.8, L['s0']), tail=0.69),
    # STATIONS: headline lands at ARRIVE + 0.25; the whole dwell slows evenly
    dict(lines=['home'], at=A['home'] + 0.25, delay=0.0, hold=(A['home'], L['home']), min_rate=0.35, tail=0.66),
    dict(lines=['food'], at=A['food'] + 0.25, delay=0.06, hold=(A['food'], L['food']), min_rate=0.35, tail=0.68),
    dict(lines=['clothes'], at=A['cloth'] + 0.25, delay=0.0, hold=(A['cloth'], L['cloth']), min_rate=0.35, tail=0.64),
    dict(lines=['travel'], at=A['travel'] + 0.25, delay=0.0, hold=(A['travel'], L['travel']), min_rate=0.35,
         tail=0.70),
    # the child gathers everything
    dict(lines=['everyday_life'], at=A['child'] + 0.25, delay=0.05, hold=(A['child'], M.T_FADE[0]), min_rate=0.35,
         tail=0.67),
    # FINAL: "£447.60 a week, per child aged nought to four" over a near-freeze on the settled number + statement
    dict(lines=['final_amount'], at=M.T_NUM2, delay=0.35, hold=(M.T_STMT + 0.1, M.T_LOGO), min_rate=0.06,
         tail=0.15),
    # END CARD: the child's flight into the logo, the question, the CTA pop and the click all run 1:1 (no settled
    # span between them: a hold there leaves the child hanging); the question is read as it lands and the CTA line
    # over the settled card
    dict(lines=['want_understand', 'start_conversation'], at=M.T_ASK, delay=0.05, gap=0.3,
         hold=(M.T_CLICK + 0.56, M.DUR), tail=1.6),
]

DUCK_DB = -14.0          # dense pops / drops under every station line


def cue_gain(cue, src_t, rate):
    """Hits that land on words: the basket drops, the first ball bounce, the gather whoosh, the chip / clothes pops."""
    if cue['name'] == 'basket_drop' or (cue['name'] == 'ball_bounce' and src_t < M.BOUNCES[0] + 0.05):
        return -5.0
    if cue['name'] == 'whoosh_slow' and abs(src_t - (M.T_GATHER + 0.25)) < 0.3:
        return -5.0
    if cue['name'] in ('pop', 'glass_tap') and M.T_CHIPS < src_t < M.T_CHIPS + 0.4:     # chips under "does it"
        return -3.0
    if cue['name'] == 'pop' and abs(src_t - 12.5) < 0.03:                                # clothes pop on "school"
        return -4.0
    return 0.0


retime.wrap(globals(), M, 'anim4', SLOTS, cue_gain=cue_gain)
