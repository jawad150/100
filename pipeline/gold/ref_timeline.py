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
    (12.15, 13.62, 'saas_reasons', 'saas'),     # "3 bari wajahain": app panel lists the 3 reasons -> chapter 01
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
    # last chapter: she walks out past the stool, a fast b-roll montage on hits, then she's seated and talking
    (51.250, 51.636, 'br_crash', 'broll'),
    (51.636, 52.021, 'br_barfall', 'broll'),
    (52.021, 52.407, 'br_dollar', 'broll'),
    (52.407, 52.793, 'br_fed', 'broll'),
    (52.793, 53.179, 'br_barrels', 'broll'),
    (53.179, 53.564, 'br_coins', 'broll'),
    (53.564, 53.950, 'br_bars', 'broll'),
    (57.60, 58.52, 'arrow_up', 'seq'),          # "aur Gold wapas"
    (64.30, 65.50, 'saas_carousel', 'saas'),    # "Abhi market Fed ke next move": glass carousel Fed / PCE / Oil
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
CONTINUITY = (50.30, 51.30)   # locked wide while she walks out (the montage covers the empty stage)
MONTAGE_END = 53.95           # back on her, seated, as the next line starts

# SaaS glass widgets beside her (ref 4); the camera eases out a little to give them room
SAAS_CARDS = [
    (37.05, 39.25, 'gauge', dict(v0=0.0, v1=0.65, label='60\u201370%', sub='October \u00b7 25 bp')),
    (44.30, 46.50, 'ticker', dict(p0=4320, p1=4145, delta='4.0%', up=False, series='down')),
    (55.35, 57.55, 'gauge', dict(v0=0.65, v1=0.40, label='40%', sub='30 September')),
    (58.60, 60.65, 'ticker', dict(p0=4145, p1=4200, delta='1.3%', up=True, series='up')),
    (70.55, 71.75, 'button', dict(text='Selective Buying')),
]
