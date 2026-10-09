"""log_kya_kahenge_hookb.py - hook B (Trial Reel) of reel 5, C15: frames 0-89 only differ from version A.

S1-01B: the 135 mm compressed rows (CAM_ROWS psi 0), heads turned on f0, a head-snap wave f3-f15
(t_s = 0.1 + 0.3 |x - 540| / 540), lockup YEH / log / HAIN KAUN? (t0 -0.1, out_t0 1.733, gone f63), every V1B word
hidden from the captions, then an O2 smoke wipe (c f72, pre 15, post 12) to the S1-01 wide (post-snap). From f90 on the
picture is identical to log_kya_kahenge (A).

    tools/heavy.sh python3 render.py log_kya_kahenge_hookb --range 0 3.0 --workers 1 --no-sfx-build --no-audio
    (render.py writes to <WS>/out/log_kya_kahenge_hookb -> <RW>/out_hookb; splice frames 0-89 onto A's 90-1055)
"""
from log_kya_kahenge import build, DUR, LOOK, BPM   # noqa: F401

draw, post, samples, cues, prewarm = build('B')
