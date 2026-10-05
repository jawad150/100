"""Reference-style edit (refs 1-3): which caption phrases become motion-tracked 3D word blocks,
the spotlight cutaways, the face-tracking box, the "!!!" pops and the light-leak cuts.

Phrase indices refer to timeline.CAPTIONS (one phrase per line, 0-based).
"""

# phrases shown as a 3D block that builds word by word beside her head (tracked to it);
# every other phrase is shown one word at a time at her chest (also tracked).
BLOCKS = {0, 1, 2, 8, 11, 15, 18, 24, 28, 29, 32, 37, 40, 41, 47, 51}

# spotlight cutaways (ref 2): (t_in, t_out, element, kind) - the current word sits centred over it
INSERTS = [
    (7.70, 8.55, 'candles3d', 'seq'),       # "Gold ne sharp retracement"
    (10.56, 11.42, 'arrow_crash', 'seq'),   # "sharply neeche"
    (21.10, 21.98, 'bond', 'seq'),          # "US government bonds"
    (27.62, 28.42, 'dollar3d', 'seq'),      # "Jab Dollar strong"
    (33.05, 33.86, 'cal_oct', 'seq'),       # "October me 25"
    (41.86, 42.72, 'cal_28sep', 'seq'),     # "28 September"
    (46.56, 47.16, 'ingot', 'seq'),         # "tak aa gaya" (per ounce)
    (54.00, 54.92, 'cal_30sep', 'seq'),     # "30 September"
    (57.60, 58.52, 'arrow_up', 'seq'),      # "aur Gold wapas"
    (67.86, 68.42, 'barrel', 'seq'),        # "oil risk"
    (74.26, 75.02, 'shield', 'seq'),        # "risk manage"
]

# hand-drawn gold tracking box around her face (ref 2): (t_in, t_out)
BOXES = [(47.18, 49.02), (69.38, 70.60)]

# "!!!" popping above her head (ref 2 opening): (t_in, t_out)
BANGS = [(1.96, 3.42), (49.40, 51.10)]

# in-scene elements kept from the 3D set (others now live in the cutaways)
KEEP_ELEMENTS = {('target', 4.30), ('fed', 31.55)}

# big condensed type behind her head (ref 1 "BETTER THAN" look): (t_in, t_out, text, sy, height, dz)
BIG_TYPE = [
    (49.10, 51.10, 'CRASH NAHI', 300, 150, 1200),
    (63.30, 64.60, 'CORRECTION', 245, 150, 300),
]

# hook: ref-1 halo + condensed words split behind the head + light trails (no title block)
HOOK_FLANK = [('SONA', 0.06, 0.94, 380, 330, 8), ('MEHNGA?', 0.94, 1.98, 380, 250, -8)]
