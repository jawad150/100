"""reel1_vo.py: REEL 1 "Could you?" with voiceover (retime.py). Source times from reel1.py (beat 0.5 s).
Each hook word is spoken on its slam (slams, settles and whips at 1x, the footage between them slows); the question,
each checklist tick, each support tile and the payoff lines hold for their read (no hold starts inside a spring,
glide or settle; >= 0.7 s of reading after each line); hard cuts are cut-aware, so a ramp never blends two shots.

    python3 retime.py plan reel1_vo ; python3 retime.py audio reel1_vo
    python3 render.py reel1_vo --workers 4 --audio ../../workspace3/audio/reel1_vo_mix.wav
"""
import retime
import reel1 as M

T = M.TICKS            # 6.5 / 7.25 / 8.0 / 8.75 / 9.5

SLOTS = [
    # HOOK MONTAGE: each word is spoken on its slam; the slams, their settles and the whips run at 1x and only the
    # footage between them slows (each hold starts after the word's settle); "to belong" waits for its slam
    dict(lines=['safe_home'], at=0.5, delay=0.08, hold=(0.81, 0.98), min_rate=0.17, tail=0.02, quant=0.25,
         duck_lead=-0.02),
    dict(lines=['everyday_care'], at=1.0, delay=0.08, hold=(1.31, 1.48), min_rate=0.17, tail=0.02, quant=0.25,
         duck_lead=-0.02),
    dict(lines=['place_belong'], at=1.5, delay=0.08, hold=(2.31, 2.42), min_rate=0.11, tail=0.4, quant=0.25,
         duck_lead=-0.02),
    # THE QUESTION: words land 3.25-4.0; hold for the read before the whip down (5.25)
    dict(lines=['could_you'], at=3.25, delay=0.0, hold=(4.3, 5.2), min_hold=1.2, tail=0.35),
    # CHECKLIST: header (hold after the cursor's glide and the row highlight), then one line per tick; each hold
    # starts once the cursor has arrived and the check tile has settled (its spring runs at 1x); the toast
    dict(lines=['eligible'], at=5.9, delay=0.0, hold=(6.30, 6.45), min_rate=0.08, tail=0.1),
    dict(lines=['bedroom'], at=T[0], delay=0.05, hold=(T[0] + 0.63, T[1] - 0.05), min_rate=0.04, tail=0.1,
         duck_lead=-0.02),
    dict(lines=['time_flex'], at=T[1], delay=0.05, hold=(T[1] + 0.63, T[2] - 0.05), min_rate=0.04, tail=0.1,
         duck_lead=-0.02),
    dict(lines=['single'], at=T[2], delay=0.05, hold=(T[2] + 0.63, T[3] - 0.05), min_rate=0.04, tail=0.1,
         duck_lead=-0.02, trim={'single': 1.97}),          # a mouth click after "relationship" held the duck on tick 4
    dict(lines=['rent_own'], at=T[3], delay=0.05, hold=(T[3] + 0.63, T[4] - 0.05), min_rate=0.04, tail=0.1,
         duck_lead=-0.02),
    dict(lines=['no_experience'], at=T[4], delay=0.05, hold=(9.90, 9.94), min_rate=0.02, tail=0.15,
         duck_lead=-0.02),
    dict(lines=['great_fit'], at=M.TOAST_T, delay=0.05, hold=(M.TOAST_T + 0.35, M.T_DOCK - 0.25), tail=0.5,
         duck_lead=-0.02),
    # SUPPORT DOCK: headline, then each focused tile (12.5 / 14.5 / 16.5); tile 3 plays footage (>= 0.2x)
    dict(lines=['support_role'], at=11.8, delay=0.0, hold=(12.0, 12.45), tail=0.1),
    dict(lines=['training'], at=12.5, delay=0.05, hold=(13.0, 14.45), tail=0.1, duck_lead=-0.02),
    dict(lines=['ongoing'], at=14.5, delay=0.05, hold=(15.0, 16.45), tail=0.1, duck_lead=-0.02),
    dict(lines=['allowance'], at=16.5, delay=0.05, hold=(16.9, 18.2), min_rate=0.2, tail=0.65, duck_lead=-0.02),
    # PAYOFF (c08 already 0.6x slow-mo: keep >= 0.4)
    dict(lines=['open_home'], at=M.PAY_L1, delay=0.0, hold=(M.PAY_L1 + 0.25, M.PAY_L2), min_rate=0.5, tail=0.1),
    dict(lines=['change_life'], at=M.PAY_L2, delay=0.08, hold=(M.PAY_L2 + 0.3, 20.65), min_rate=0.40, tail=0.7,
         duck_lead=-0.02),
    # END CARD: wordmark -> "Organic Fostering, rated Good by Ofsted." (cursor waits before the click), then the CTA
    dict(lines=['ofsted'], at=21.75, delay=0.0, hold=(23.40, 23.47), min_rate=0.03, tail=0.1),
    dict(lines=['start_enquiry'], at=23.5, delay=0.07, hold=(24.35, M.DUR), tail=1.52, duck_lead=-0.02),
]

# hard cuts (source switch instants: the module cuts half a frame early): hook flash / zoom cuts and section cuts
CUTS = ([M._cut_t(k) - M.HALF for k in (2, 4, 5, 6)] +
        [t - M.HALF for t in (M.T_HOOK, M.T_Q, M.T_LIST, M.T_DOCK, M.T_PAY, M.T_END)])


def cue_gain(cue, src_t, rate):
    """Hits that land on words: hook whips/shimmers, the question swishes, the CTA pop."""
    if cue['name'] in ('whip', 'shimmer') and src_t < 2.5:
        return -5.0
    if cue['name'] == 'swish_small' and abs(src_t - 3.25) < 0.05:          # under "Could"
        return -8.0
    if cue['name'] == 'swish_small' and abs(src_t - 4.0) < 0.05:
        return -5.0
    if cue['name'] == 'pop' and abs(src_t - 22.75) < 0.05:
        return -4.0
    if cue['name'] == 'impact_soft' and abs(src_t - 1.5) < 0.05:        # slam 3's tail on the "A" of "A place"
        return -6.0
    if cue['name'] == 'impact_soft' and any(abs(src_t - x) < 0.05 for x in (0.5, 19.5)):        # on "A" / "Ch-"
        return -3.0
    if cue['name'] == 'heartbeat' and abs(src_t - 18.75) < 0.05:         # the reprise's 2nd beat on "home"
        return -4.0
    if cue['name'] == 'riser' and abs(src_t - 2.5) < 0.1:                                     # under "-long"
        return -3.0
    return 0.0


retime.wrap(globals(), M, 'reel1', SLOTS, cue_gain=cue_gain, cuts=CUTS)
