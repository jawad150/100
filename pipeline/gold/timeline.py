"""Edit decision list for the gold-market reel: shots, camera, transitions, chapter cards,
3D elements, big type, captions and SFX cues. All times are seconds on the source clock
(29.97 fps), so frame i of the output is frame i of the color-corrected video (lip sync is exact).
"""

FPS = 30000 / 1001
NFRAMES = 2380

# first frame of every shot (hard cuts in the color-corrected render)
CUTS = [0, 157, 408, 752, 912, 1204, 1541, 1936]
CUT_T = [c / FPS for c in CUTS]

# transition at the start of shot k (k >= 1): kind, direction
TRANSITIONS = {
    1: ('zoom', 0),
    2: ('whip', 1),
    3: ('whip', 1),
    4: ('whip', -1),
    5: ('spin', 1),
    6: ('whip', -1),
    7: ('zoom', 0),
}

# ------------------------------------------------------------------ camera
# keys: (t, zoom, x, y, roll, rx, ry, cut)   x/y = camera offset in canvas px (+x looks right)
# cut=True jumps to the key (a new camera angle) instead of easing into it.
CAM = [
    # shot 0 - hook close-up
    (0.00, 1.45, 20, -130, -5, 0, 4, True),
    (0.95, 1.10, 10, -40, 0, 0, 0, False),
    (2.60, 1.15, 20, -40, 1.5, 0, 1, False),
    (3.55, 1.10, -40, 0, -1.5, 0, -3, False),
    (5.24, 1.20, -20, -40, 0, 0, -2, False),
    # shot 1 - full body (she stands right of centre)
    (5.24, 1.10, 60, 0, 0, 0, -4, True),
    (8.00, 1.18, 40, -40, 0, 0, 3, False),
    (10.5, 1.15, 40, -60, -1, 0, 2, False),
    (13.61, 1.24, 40, -120, -2, 0, 0, False),
    # shot 2 - medium, chapter 01
    (13.61, 1.10, 0, 0, 0, 0, 0, True),
    (15.70, 1.06, 0, -160, 0, 0, 0, False),
    (19.70, 1.14, -30, -200, 1.5, 0, 4, False),
    (19.78, 1.12, 80, -20, -2, 0, -5, True),
    (23.15, 1.20, 40, -60, -1, 0, -3, False),
    (23.22, 1.42, 0, -240, 0, 0, 2, True),
    (25.09, 1.55, 0, -290, 0.5, 0, 3, False),
    # shot 3 - she walks in from the right, chapter 02
    (25.09, 1.10, 40, 0, 0, 0, 0, True),
    (27.40, 1.14, 60, -50, 0, 0, -4, False),
    (30.43, 1.32, 110, -150, 2, 0, 0, False),
    # shot 4 - she walks in from the left, chapter 03
    (30.43, 1.10, -40, 0, 0, 0, 0, True),
    (33.05, 1.12, -20, -40, 0, 0, 4, False),
    (36.05, 1.20, 0, -80, 0, 0, 2, False),
    (36.10, 1.40, -150, -250, -2, 0, 0, True),
    (38.05, 1.45, -150, -260, -2, 0, 1, False),
    (38.10, 1.12, 30, -30, 1.5, 0, -5, True),
    (40.17, 1.18, 40, -50, 1, 0, -3, False),
    # shot 5 - medium, the drop
    (40.17, 1.10, 0, -60, 0, 0, 0, True),
    (41.60, 1.04, 0, -170, 0, 0, 2, False),
    (43.90, 1.08, -20, -180, 0, 0, 3, False),
    (44.40, 1.05, 20, -170, -1.5, 0, -2, True),
    (47.15, 1.10, 20, -180, 0, 0, 0, False),
    (50.30, 1.60, -30, -330, 0, 0, 0, False),
    (51.20, 1.14, 0, -40, 0, 0, 0, False),
    (51.42, 1.12, 0, -20, 0, 0, 0, False),
    # shot 6 - wide stage, she walks in and sits
    (51.42, 1.10, -70, 0, 0, 0, 8, True),
    (53.80, 1.10, 0, -60, 0, 0, -4, False),
    (57.55, 1.12, -20, -90, 0, 0, -2, False),
    (57.62, 1.06, 0, -120, 2, 0, 3, True),
    (60.65, 1.10, 10, -130, 1, 0, 2, False),
    (60.72, 1.10, 40, -170, -1.5, 0, 0, True),
    (64.60, 1.18, 40, -190, -1, 0, 0, False),
    # shot 7 - seated, the outlook
    (64.60, 1.10, 20, -60, 0, 0, 0, True),
    (69.25, 1.14, 30, -110, 0, 0, -4, False),
    (69.32, 1.22, 120, -120, 2, 0, -3, True),
    (72.65, 1.28, 130, -140, 1, 0, -2, False),
    (72.72, 1.06, 0, -60, 0, 0, 4, True),
    (76.90, 1.12, 10, -80, 0, 0, 2, False),
    (79.41, 1.08, 0, 0, 0, 0, 0, False),
]

# (t, zoom kick, shake amplitude)
PUNCH = [(2.72, 0.10, 14), (12.20, 0.10, 12), (29.60, 0.06, 12), (32.26, 0.05, 6), (35.04, 0.06, 8),
         (38.12, 0.06, 8), (43.98, 0.12, 18), (44.54, 0.06, 8), (49.62, 0.08, 10), (56.64, 0.05, 6),
         (58.60, 0.07, 9), (62.36, 0.06, 10), (63.84, 0.05, 6)]

# background brightness (spotlight moments) and depth-of-field blur (px at 1080 scale)
BG_DIM = [(0, 1.0), (47.2, 1.0), (48.4, 0.5), (50.6, 0.5), (51.42, 1.0)]
DOF = [(0, 2.5), (47.2, 2.5), (49.0, 7.0), (51.0, 3.0)]

# golden god-rays behind the presenter's head: (t_in, t_out, strength)
RAYS = [(0.0, 1.9, 0.55), (47.9, 51.0, 0.85), (51.6, 53.8, 0.6), (77.0, 79.4, 0.5)]

# ------------------------------------------------------------------ chapter cards (reference-1 style)
SECTIONS = [
    dict(t_in=13.72, t_out=15.62, num='01', title='TREASURY YIELDS', neon='YIELDS',
         tags=['10-YEAR', '2007 HIGH', 'BONDS']),
    dict(t_in=25.45, t_out=27.30, num='02', title='US DOLLAR', neon='DOLLAR',
         tags=['USD', 'STRONG', 'SELL-OFF']),
    dict(t_in=31.20, t_out=33.00, num='03', title='FED RATE HIKE', neon='FED',
         tags=['OCTOBER', '25 BP', 'RATE HIKE']),
]

# ------------------------------------------------------------------ elements
# kind: 'seq' (Blender PNG sequence in assets3d/) or 'png' (still from the AE project, assets2d/)
# sx, sy: on-screen position when it lands; size: on-screen height in px
# dz: depth relative to the presenter (+ behind / - in front), layer: 'back' (behind her) or 'front'
# enter: pop | fly | drop | slam | rise    play: loop | once
def E(name, t0, t1, sx, sy, size, layer='back', dz=150, kind='seq', enter='pop', play='loop', fps=20,
      tilt=0.0, sway=8.0, glow=0.35, spin=0.0):
    return dict(name=name, t0=t0, t1=t1, sx=sx, sy=sy, size=size, layer=layer, dz=dz, kind=kind, enter=enter,
                play=play, fps=fps, tilt=tilt, sway=sway, glow=glow, spin=spin)


ELEMENTS = [
    # --- hook: "Sona achanak itna mehnga kaise ho gaya? Kya yeh market crash hai... ya opportunity zone?"
    E('arrow_crash', 2.56, 3.55, 850, 380, 280, layer='front', dz=-120, enter='fly', play='once', fps=30),
    E('target', 4.30, 5.24, 200, 400, 240, layer='front', dz=-100, kind='png', enter='pop', sway=14),
    # --- shot 1: "Gold traders ne notice kiya hoga... sharp retracement ... sharply neeche ... 3 bari wajahain"
    E('candles3d', 5.55, 9.70, 255, 640, 380, layer='back', dz=120, enter='rise', play='once', fps=24),
    E('candlestick', 7.74, 9.70, 255, 1000, 190, layer='back', dz=80, kind='png', enter='pop', sway=10, glow=0.2),
    E('arrow_crash', 10.55, 11.95, 270, 760, 460, layer='back', dz=100, enter='fly', play='once', fps=30),
    E('num_3', 12.15, 13.61, 215, 640, 440, layer='back', dz=150, enter='slam', play='once', fps=30),
    # --- chapter 01: Treasury yields
    E('bond', 15.80, 19.70, 290, 330, 250, layer='back', dz=160, enter='fly'),
    E('num_2007', 17.20, 19.70, 800, 290, 170, layer='back', dz=200, enter='slam', play='once', fps=30),
    E('money_bag', 20.20, 23.15, 190, 840, 300, layer='front', dz=-90, kind='png', enter='drop', sway=10),
    E('arrow_up', 22.35, 23.15, 860, 760, 300, layer='front', dz=-80, enter='fly', play='once', fps=30),
    E('coin_au', 23.45, 25.09, 850, 860, 300, layer='front', dz=-100, enter='pop'),
    # --- chapter 02: dollar
    E('dollar3d', 27.62, 30.43, 250, 700, 520, layer='back', dz=120, enter='slam'),
    E('dollar_coin', 27.90, 30.43, 200, 1060, 200, layer='front', dz=-80, kind='png', enter='pop', spin=1.0),
    E('arrow_crash', 29.30, 30.43, 330, 400, 300, layer='back', dz=80, enter='fly', play='once', fps=30),
    # --- chapter 03: Fed
    E('fed', 31.55, 33.00, 840, 640, 380, layer='back', dz=150, enter='rise'),
    E('cal_oct', 33.05, 37.00, 850, 760, 330, layer='back', dz=120, enter='drop'),
    E('num_025', 35.00, 37.00, 560, 330, 230, layer='back', dz=200, enter='slam', play='once', fps=30),
    E('num_6070', 38.10, 40.17, 650, 300, 200, layer='back', dz=200, enter='slam', play='once', fps=30),
    # --- the drop: 28 Sept, -4%, $4,145
    E('cal_28sep', 41.80, 43.36, 540, 240, 230, layer='back', dz=150, enter='drop'),
    E('num_4pct', 43.38, 44.45, 540, 225, 190, layer='back', dz=200, enter='slam', play='once', fps=30),
    E('arrow_crash', 43.95, 47.15, 185, 640, 300, layer='front', dz=-100, enter='fly', play='once', fps=30),
    E('num_4145', 44.50, 47.15, 540, 230, 175, layer='back', dz=200, enter='slam', play='once', fps=30),
    E('ingot', 46.25, 47.15, 890, 860, 210, layer='front', dz=-100, enter='drop'),
    E('guarantee_gold', 49.95, 51.00, 860, 900, 260, layer='front', dz=-120, kind='png', enter='slam', sway=10),
    # --- empty stage: rebound teaser, then 30 Sept / 40% / $4,200
    E('arrow_up', 51.75, 53.75, 540, 760, 560, layer='back', dz=200, enter='rise', play='once', fps=24),
    E('cal_30sep', 54.00, 57.55, 210, 330, 250, layer='back', dz=120, enter='drop'),
    E('num_40', 56.60, 57.55, 860, 290, 190, layer='back', dz=150, enter='slam', play='once', fps=30),
    E('arrow_up', 58.10, 60.60, 190, 700, 330, layer='back', dz=100, enter='fly', play='once', fps=30),
    E('num_4200', 58.55, 60.60, 560, 215, 165, layer='back', dz=200, enter='slam', play='once', fps=30),
    E('refund', 58.90, 60.60, 925, 400, 200, layer='back', dz=100, kind='png', enter='pop', spin=0.6),
    # --- outlook: Fed next move, PCE data, Middle East oil risk
    E('fed', 65.10, 69.25, 200, 530, 230, layer='back', dz=120, enter='rise'),
    E('candles3d', 66.30, 69.25, 870, 540, 190, layer='back', dz=120, enter='rise', play='once', fps=24),
    E('barrel', 67.85, 69.25, 200, 950, 230, layer='back', dz=80, enter='drop'),
    # --- selective buying opportunity, risk management, news flow
    E('target', 70.40, 72.65, 905, 640, 290, layer='back', dz=100, kind='png', enter='pop', sway=12),
    E('shield', 74.25, 77.30, 160, 680, 280, layer='back', dz=100, enter='pop'),
    E('gold_fire_bubble', 75.62, 77.30, 925, 620, 240, layer='back', dz=100, kind='png', enter='pop', sway=12),
]

# gold bars raining in the hook: (t0, sx, size, dz, seq offset, rotation)
INGOT_RAIN = [(0.00, 180, 230, -150, 0, -18), (0.10, 860, 260, -200, 9, 22), (0.25, 420, 170, 250, 17, 8),
              (0.35, 700, 150, 300, 25, -12), (0.50, 110, 150, 260, 4, 30), (0.62, 960, 190, 120, 13, -25),
              (0.80, 330, 280, -260, 21, 14), (0.95, 760, 170, 220, 30, -6), (1.10, 560, 140, 320, 6, 20)]

# big gold type behind the presenter: (t_in, t_out, text, sy, height, dz)
BIG_TYPE = [
    (0.05, 1.95, 'SONA', 360, 330, 300),
    (2.60, 3.50, 'CRASH?', 330, 270, 300),
    (48.10, 51.10, 'CRASH NAHI', 330, 140, 300),
    (63.30, 64.60, 'CORRECTION', 245, 135, 300),
]

# tag pills in the scene: (t_in, t_out, text, sx, sy, layer)
PILLS = [
    (24.15, 25.09, 'INTEREST  0%', 850, 1060, 'front'),
    (62.00, 63.25, 'STRUCTURAL CRASH', 540, 255, 'back'),
    (66.34, 69.25, 'PCE DATA', 870, 700, 'back'),
    (67.90, 69.25, 'OIL RISK', 200, 1120, 'back'),
    (65.40, 69.25, 'FED NEXT MOVE', 210, 720, 'back'),
]

# probability meter: (t_in, t_out, from, to, sx, sy, label)
METERS = [
    (38.10, 40.17, 0.0, 0.70, 650, 450, 'RATE HIKE ODDS'),
    (56.60, 57.55, 0.70, 0.40, 860, 440, 'RATE HIKE ODDS'),
]

# ------------------------------------------------------------------ captions
# One phrase per line of this block. Lines inside a phrase are split by ' / '.
# word:idx  -> timing from Whisper word idx;  word@t -> explicit start time;  *word -> gold keyword
CAPTION_Y = {0: 1330, 1: 1290, 2: 1300, 3: 1310, 4: 1290, 5: 1300, 6: 1300, 7: 1280}
CAPTIONS = """
*Sona:0 / achanak:1 itna:2 / *mehnga:3 / kaise:4 ho:5 gaya?:6
Kya:7 yeh:8 / market:9 / *crash:10 hai...:11
ya:12 traders:13 / ke:14 liye:15 ek:16 naya:17 / *opportunity:18 / *zone?:19
*Gold:20 traders:21 ne:22 / notice:23 kiya:24 hoga:25
ke:26 recent:27 / days:28 mein:29
*Gold:30 ne:31 / *sharp:32 / *retracement:33 / dikhai:34
yaani:35 *Gold:36 / recent:37 *rally:38 / ke:39 baad:40
*sharply:41 / *neeche:42 / aaya:43 hai:44
Iski:45 / *3:46 bari:47 / *wajahain:48 hain:49
Pehli@13.72 / US@14.02 *Treasury:51 / *Yields:52 / barh:53 gayi:54 hain:55
*10:56 saala:57 / Treasury:58 Yields:59
June:60 *2007:61 / ke:62 baad:63 / *highest:64 *level:65
par:66 pohanch:67 / gayi:68
Yaani:69 *investors:70 ko:71 / US:72 government:73 / *bonds:74 se:75
behtar:76 *return:77 / mil:78 raha:79 tha:80
jabke:81 *Gold:82 / koi:83 *interest:84 / nahi:85 deta:86
Doosri@25.68 / US@26.08 *Dollar:88 / *strong:89 hua:90
Jab:91 *Dollar:92 / strong:93 hota:94 hai:95
iss:96 se:97 *Gold:98 par:99 / *selling:100 / *pressure:101 / aata:102 hai@30.12
Teesri@31.20 / *Fed@31.56 ke:104 / *rate:105 *hike:106
ki:107 / *umeedain:108
*October:109 me:110 / *25:111 / *basis-point:112
yaani:114 / *0.25%:115
rate:118 barhne:119 / ke:120 *chances:121
ek:122 point:123 par:124 / around:125 / *60-70%:126
tak:129 chale:130 / gaye:131 the:132
Isi:133 *pressure:134 / mein:135
*28:136 *September:137 / ko:138 *Gold:139 / almost:140
*4%:141 / *gira:143
aur:144 / *$4,145:145 / per:147 *ounce:148
tak:149 aa:150 / gaya:151
*Lekin:152 yahan:153 / ek:154 *important:155 / *point:156 hai@48.82
har@49.10 *drop:158 / *crash:159 / nahi:160 hota!:161
*30:162 *September:163 / tak:164
rate:165 hike:166 / ki:167 *probability:168
around:169 / *40%:170 hui:172
aur:173 *Gold:174 / *wapas:175
*$4,200:176 / ke:178 aas:179 paas:180
aa:181 gaya:182 / hai:183
*Gold:184 ka:185 / ye:186 *drop:187
koi:188 *structural:189 / *crash:190 nahi:191
balki:192 / *macro-driven:193 / *correction:195 hai:196
Abhi:197 *market:198 / *Fed:199 ke:200 / next:201 *move:202
*PCE:203 *data:204 / aur:205
*Middle:206 *East:207 / *oil:208 *risk:209
ko:210 price:211 / kar:212 raha:213 hai:214
Traders:215 ke:216 liye:217 / ye:218 *zone:219
*selective:220 / *buying:221 ka:222 / *opportunity:223
ho:224 sakta:225 / hai:226
Lekin:227 sirf:228 / unke:229 liye:230 jo:231
*risk:232 *manage:233 / kar:234 sakte:235 hain:236
aur:237 *news:238 *flow:239 / par:240 *nazar:241
rakhte:242 hain:243
"""

# ------------------------------------------------------------------ SFX cues (audio.py renders these)
# (t, kind, gain)
SFX = []


def _cues():
    out = []
    for k, (kind, d) in TRANSITIONS.items():
        t = CUT_T[k]
        out.append((t - 0.28, 'whoosh_big' if kind != 'zoom' else 'whoosh_zoom', 0.9))
        out.append((t, 'hit_soft', 0.5))
    for s in SECTIONS:
        out.append((s['t_in'] - 0.5, 'riser', 0.35))
        out.append((s['t_in'] + 0.35, 'impact', 0.8))
        out.append((s['t_in'] + 0.55, 'shimmer', 0.35))
        out.append((s['t_out'] - 0.2, 'whoosh', 0.55))
    for e in ELEMENTS:
        if e['enter'] == 'slam':
            out.append((e['t0'] + 0.05, 'impact', 0.75))
        elif e['enter'] in ('fly', 'rise'):
            out.append((e['t0'] - 0.05, 'whoosh', 0.45))
        else:
            out.append((e['t0'], 'pop', 0.45))
        if e['name'] in ('ingot', 'coin_au', 'dollar_coin', 'num_4145', 'num_4200'):
            out.append((e['t0'] + 0.12, 'ching', 0.35))
    for t, z, a in PUNCH:
        if a >= 12:
            out.append((t, 'boom', 0.65))
    for k in range(len(CAM)):
        if CAM[k][7] and k > 0 and abs(CAM[k][0] - CAM[k - 1][0]) < 0.2:
            out.append((CAM[k][0] - 0.06, 'swish', 0.35))
    for t0, sx, size, dz, off, rot in INGOT_RAIN:
        out.append((t0 + 0.55, 'ching', 0.18))
    for t in BIG_TYPE:
        out.append((t[0], 'impact', 0.55))
    for p in PILLS:
        out.append((p[0], 'click', 0.35))
    for m in METERS:
        out.append((m[0], 'tick_run', 0.3))
    out.append((0.0, 'boom', 0.8))
    out.append((0.0, 'shimmer', 0.4))
    out.append((47.9, 'riser_long', 0.35))
    out.append((51.42, 'boom', 0.6))
    out.append((77.0, 'shimmer', 0.35))
    out.sort()
    return out


SFX = _cues()
