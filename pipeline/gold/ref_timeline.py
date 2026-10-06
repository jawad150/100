"""Reference-style edit (refs 1-3): which caption phrases become motion-tracked 3D word blocks,
the spotlight cutaways, the face-tracking box, the "!!!" pops and the light-leak cuts.

Phrase indices refer to timeline.CAPTIONS (one phrase per line, 0-based).
"""

# every phrase is a motion-tracked 3D block (white sans + gold Gwyner keywords, like the hook caption)
BLOCKS = set(range(200))

# cutaways: spotlight 3D elements ('seq') and photoreal Blender b-roll ('broll', optional 5th = mirrored).
# b-roll runs as fast montages cut on sound hits; they also hide the walk-ins and the camera cuts.
INSERTS = [
    (0.00, 0.50, 'br_bars', 'broll'),           # cold open: "Sona ..."
    (2.68, 3.10, 'br_crash', 'broll'),          # "market crash"
    (4.30, 4.62, 'br_coins', 'broll'),          # "opportunity zone?"
    (7.70, 8.55, 'candles3d', 'seq'),           # "Gold ne sharp retracement"
    (10.56, 11.42, 'arrow_crash', 'seq'),       # "sharply neeche"
    (13.02, 13.34, 'br_barfall', 'broll'),      # "3 bari wajahain hain" -> chapter 01
    (13.34, 13.62, 'br_coins', 'broll', 1),
    (21.10, 21.98, 'bond', 'seq'),              # "US government bonds"
    (24.96, 25.30, 'br_bars', 'broll'),      # walk-in -> chapter 02 (dollar)
    (25.30, 25.64, 'br_dollar', 'broll'),
    (27.62, 28.42, 'dollar3d', 'seq'),          # "Jab Dollar strong"
    (30.34, 30.66, 'br_barfall', 'broll'),     # "selling pressure" -> chapter 03 (Fed)
    (30.66, 30.96, 'br_fed', 'broll'),
    (33.05, 33.86, 'cal_oct', 'seq'),           # "October me 25"
    (40.05, 40.40, 'br_coins', 'broll', 1),       # walk-in -> "Isi pressure mein"
    (40.40, 40.74, 'br_bars', 'broll'),
    (41.86, 42.72, 'cal_28sep', 'seq'),         # "28 September"
    (46.56, 47.16, 'ingot', 'seq'),             # "tak aa gaya" (per ounce)
    (54.00, 54.92, 'cal_30sep', 'seq'),         # "30 September"
    (57.60, 58.52, 'arrow_up', 'seq'),          # "aur Gold wapas"
    (64.30, 64.60, 'br_crash', 'broll'),   # "correction hai" -> "Abhi market Fed ..."
    (64.60, 64.92, 'br_fed', 'broll'),
    (67.86, 68.42, 'br_barrels', 'broll'),      # "Middle East oil risk"
    (74.26, 75.02, 'shield', 'seq'),            # "risk manage"
]

# hand-drawn gold tracking box around her face (ref 2): (t_in, t_out)
BOXES = [(47.18, 49.02), (69.38, 70.60)]

# "!!!" popping above her head (ref 2 opening): (t_in, t_out)
BANGS = [(1.96, 2.66)]

# in-scene elements kept from the 3D set (others now live in the cutaways)
KEEP_ELEMENTS = {('fed', 31.55)}

# big condensed type behind her head (ref 1 "BETTER THAN" look): (t_in, t_out, text, sy, height, dz)
BIG_TYPE = [
    (49.10, 51.10, 'CRASH NAHI', 345, 108, 1200),
    (63.30, 64.60, 'CORRECTION', 330, 104, 300),
]

# hook: ref-1 halo + condensed words split behind the head + light trails (no title block)
HOOK_FLANK = [('SONA', 0.50, 1.02, 380, 260, 8), ('MEHNGA?', 1.02, 1.98, 380, 165, -8)]

# chapter card 02 starts once she is in frame (the walk-in is covered by a cutaway)
CARD2_IN = 25.66

# last chapter: she walks out of frame, the stool stays, she walks back in from the other side and sits
EXIT = (50.30, 51.418)        # her exit in clip 5 is composited over clip 6's empty-stool plate
STOOL_FRAME = 1548            # clean plate of the stool (clip 6, before she walks in)
CONTINUITY = (50.30, 53.85)   # one locked wide shot across the cut
