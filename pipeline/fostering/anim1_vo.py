"""anim1_vo.py: ANIM 1 "Day in the Life" with voiceover (retime.py). Holds slow down to fit each VO line plus
reading time; stamps, drops, the slide, tumbles and the flip keep their speed. Times below are anim1 SOURCE times
(anim1.py shot list); every hold extension is a whole number of beats (100 BPM grid kept).

    python3 retime.py plan anim1_vo ; python3 retime.py audio anim1_vo
    python3 render.py anim1_vo --workers 4 --audio ../../workspace3/audio/anim1_vo_mix.wav
"""
import retime
import anim1 as M

SLOTS = [
    # FRAME 1: the hook question is spoken over the stamps (type lands ahead of the voice); the handwriting writes
    # while "It's often found in the everyday." is read, then the sheet holds with the clock ticking.
    dict(lines=['what_does'], at=0.0, delay=0.05, hold=(1.8, 2.4), tail=0.0),
    dict(lines=['often_found'], at=2.4, delay=0.1, hold=(4.02, 4.98), tail=0.7),
    # FRAME 2: one list item per stamp; the bus run is not slowed (min_rate 1), BAKING holds for reading
    dict(lines=['school_runs'], at=5.4, delay=0.08, hold=(6.9, 7.2), min_rate=1.0, tail=0.0),
    dict(lines=['homework'], at=7.2, delay=0.08, hold=(8.1, 8.4), min_rate=1.0, tail=0.0),
    dict(lines=['baking'], at=8.4, delay=0.08, hold=(9.75, 10.2), tail=0.9),
    # FRAME 3: "Small moments can help build stability." over the block tower, then one checklist row per line
    dict(lines=['small_moments'], at=10.8, delay=0.0, hold=(12.3, 12.6), tail=0.35),
    dict(lines=['consistent_home'], at=12.6, delay=0.1, hold=(12.95, 13.2), tail=0.25),
    dict(lines=['familiar_routine'], at=13.2, delay=0.1, hold=(13.55, 13.8), tail=0.25),
    dict(lines=['someone_there'], at=13.8, delay=0.1, hold=(14.2, 15.1), tail=1.0),
    # FRAME 4: the headline, the house lands, a read before the headline sinks
    dict(lines=['happens_everyday'], at=15.6, delay=0.1, hold=(17.25, 17.85), tail=0.6),
    # END CARD: "Could you make room?" as it writes on, then the CTA over the settled card
    dict(lines=['make_room', 'start_enquiry'], at=18.6, delay=0.15, gap=0.35, hold=(19.35, 21.0), tail=1.6),
]

retime.wrap(globals(), M, 'anim1', SLOTS)
