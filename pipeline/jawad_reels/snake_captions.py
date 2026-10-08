"""snake_captions.py - Jawad's caption signature ("snake captions"), ported from his Yaadein / You-made-it reels
(festive-lovelace:pipeline/memories/captions.py + the face-avoiding paths of gold/snake.py) to this toolkit:
(H, W, 4) premultiplied linear-light canvases at 30 fps, brand type from jawad_kit.

    white Poppins SemiBold words + ONE glowing orange-red Instrument Serif Italic keyword (flame gradient
    #FFC34D -> #FF8A1F -> #F04A16, the 'jw_key' look) per chunk, laid glyph by glyph along a gentle bezier
    "snake" path, led by a thin glowing guide line (thin tail, hot comet head) that draws ahead of the voice
    under the words. No glass cards: only a soft feathered dark scrim for legibility.

    import jawad_kit
    import snake_captions as SC
    words = SC.load_words('<WS>/captions/reel3.words.json')     # [{word, start, end, keyword}, ...]
    cap = SC.Captions(words, band='lower', avoid=[(330, 420, 760, 980)])   # face rects (or fn(t) -> rects)
    def prewarm(): cap.prewarm()
    def draw(t): cv = scene(t); cap.draw(cv, t); return cv
    cap.report()  /  cap.check()  /  cap.save_srt(path)

WORD TIMING JSON (vo_chain.py writes it): a list (or {"words": [...]}) of
    {"word": "raat", "start": 1.20, "end": 1.46, "keyword": false}
    also accepted: w / s / e / key, and '*word' marks a keyword; 'token' (the script token with its punctuation)
    or 'brk' marks a sentence / clause end. Shown text follows the house SRT style: trailing , . and the danda
    are dropped, ? ! and ... stay. Times in seconds of the VO; pass offset= when the
    VO starts later in the reel. hide=[(t0, t1)] drops words that a designed headline already shows (the
    two-layer rule of hooks_retention_captions.md 4.1).

CHUNKING (chunk_words): 1-3 words per chunk; a pause > 0.45 s or end punctuation (. , ? ! ...) is a hard break;
    each phrase is then split by a small cost model: 2-word chunks preferred, no lone word unless it is the
    keyword, never start a chunk with a word that binds to the one before (ka ke ne sa hai ...) nor end on one
    that binds to the next (aur ek bas ...), break where the voice pauses, at most one keyword per chunk, and a
    chunk must fit the band at >= 85 % size.
TIMING: each word enters at its start - 0.05 s (glide along the path from behind with an out_expo ease, focus
    pull 10 px -> sharp, glow flare); white words pop and settle (POP spring, ~2 % overshoot), the keyword
    settles 1.06 -> 1 (out_cubic, no bounce: brand type). A chunk holds 0.35 s after its last word, then drifts on
    along the path and defocuses (in_cubic). Chunks never overlap: a chunk always finishes leaving (0.12 s when
    the next one follows, 0.3 s into silence) before the next one enters.
LAYOUT / SAFE ZONES (solved once per chunk, deterministic): key copy inside x 70-1010, y 230-1480; nothing at
    x > 930 for y 1050-1700; bottom 300 px clear. band='lower' (baseline ~1270, x 70-930), 'upper' (~700) or
    'auto' (lower, else upper). The chunk is moved (y, then x), then shrunk (1.0 -> 0.78) until its ink + guide
    line clears every avoid rect (+ margin 28 px) during its whole life. avoid: list of (x0, y0, x1, y1) or a
    callable t -> list (sampled at 10 Hz over the chunk's life).
COST: ~10-35 ms per frame with one visible chunk (glyph sprites are built once: call cap.prewarm()).
Self-test: python3 snake_captions.py selftest (or --selftest) -> <WS>/out/selftest/snake_captions_*.png; exits 1
on failure.
"""
import functools
import json
import math
import os
import re
import sys
import time

import cv2
import numpy as np

import jawad_kit
from jawad_kit import K, T, J

W, H = K.W, K.H
SAFE_X0, SAFE_X1, SAFE_Y0, SAFE_Y1 = 70, 1010, 230, 1480       # key copy
RIGHT_COL = (930, 1050, 1700)                                    # nothing at x > 930 for y 1050..1700
BOTTOM_CLEAR = 1620                                              # bottom 300 px clear
SHORT = {'ka', 'ki', 'ke', 'ko', 'hai', 'hain', 'toh', 'to', 'se', 'ne', 'na', 'aur', 'bhi', 'ho', 'tha', 'thi', 'the',
         'mein', 'me', 'ek', 'is', 'us', 'ye', 'wo', 'a', 'the', 'of', 'in', 'on', 'is'}
END_PUNCT = re.compile(r'[.,!?…:;—–-]+$')


# =============================================================================================== styles
@functools.lru_cache(maxsize=8)
def word_style(px):
    """White Poppins SemiBold caption word (warm white, tight warm halo, soft dark shadow for legibility)."""
    return T.style('jw_body', name='jw_snake_word', px=float(px), glow=0.32, glow_radii=(0.06, 0.2),
                   glow_weights=(0.5, 0.35), shadow=0.75, shadow_offset=(0.0, 0.05), shadow_blur=0.09)


@functools.lru_cache(maxsize=8)
def key_style(px):
    """Keyword: the house 'jw_key' core (flame gradient, hot inner glow); the wide halo is drawn per word."""
    return T.style('jw_key_core', px=float(px))


@functools.lru_cache(maxsize=512)
def _glyphs(word, key, px):
    return T.Glyphs(word, key_style(px) if key else word_style(px))


@functools.lru_cache(maxsize=256)
def _halo(word, px):
    return T.render(word, 'jw_key_halo', px=float(px))


@functools.lru_cache(maxsize=4)
def _head_spr(r=3.2):
    d = K.disc(r, K.C['WHITE'] * 1.8)
    return K.glow(d, K.C['AMBER'] * 1.2, sigmas=(4, 11, 26), strength=1.2, weights=(1.0, 0.6, 0.35))


class _ByteLRU:
    """Tiny byte-budgeted LRU for settled-word sprites (env JAWAD_CAPTION_CACHE_MB, default 48 per process)."""

    def __init__(self, mb):
        import collections
        self.d, self.budget, self.size = collections.OrderedDict(), mb * 2 ** 20, 0

    def get(self, k):
        v = self.d.get(k)
        if v is not None:
            self.d.move_to_end(k)
        return v

    def put(self, k, v, nbytes):
        self.d[k] = (v, nbytes)
        self.size += nbytes
        while self.size > self.budget and len(self.d) > 1:
            _, (_, nb) = self.d.popitem(last=False)
            self.size -= nb


_SETTLED = _ByteLRU(float(os.environ.get('JAWAD_CAPTION_CACHE_MB', '48')))
_TOKENS = [0]


# =============================================================================================== words
def load_words(src, offset=0.0, hide=()):
    """Word timings from a JSON path, a JSON string or a list -> [dict(word, start, end, keyword)] sorted by
    start, shifted by offset, without words that start inside a hide window."""
    if isinstance(src, str):
        data = json.load(open(src, encoding='utf8')) if os.path.exists(src) else json.loads(src)
    else:
        data = src
    if isinstance(data, dict):
        data = data.get('words', data.get('segments', []))
    out = []
    for d in data:
        w = str(d.get('word', d.get('w', d.get('text', '')))).strip()
        key = bool(d.get('keyword', d.get('key', False)))
        if w.startswith('*'):
            w, key = w[1:], True
        if not w:
            continue
        s = float(d.get('start', d.get('s', 0.0))) + offset
        e = float(d.get('end', d.get('e', s + 0.25))) + offset
        if any(a <= s < b for a, b in hide):
            continue
        brk = bool(d.get('brk', END_PUNCT.search(str(d.get('token', w)))))
        disp = str(d.get('display', w))
        if not re.search(r'(\.\.\.|\u2026)$', disp):            # house style: keep ? ! ..., drop , . and the danda
            disp = re.sub(r'[,.\u0964]+$', '', disp) or disp
        out.append(dict(word=disp, start=s, end=max(e, s + 0.05), keyword=key, brk=brk))
    out.sort(key=lambda d: d['start'])
    return out


def _bare(w):
    return re.sub(r'[^\w]', '', w.lower())


def word_width(word, key, white_px, key_px):
    return T.measure(word, key_style(key_px) if key else word_style(white_px))[0]


def _space(prev_key, white_px):
    return white_px * (0.30 + (0.18 if prev_key else 0.0))


def chunk_width(ws, white_px, key_px):
    tot = 0.0
    for i, d in enumerate(ws):
        if i:
            tot += _space(ws[i - 1]['keyword'], white_px)
        tot += word_width(d['word'], d['keyword'], white_px, key_px)
    return tot


BIND_PREV = {'ka', 'ki', 'ke', 'ko', 'se', 'ne', 'sa', 'si', 'tak', 'mein', 'me', 'par', 'pe', 'wala', 'wali', 'wale',
             'hai', 'hain', 'tha', 'thi', 'the', 'hoon', 'hun', 'ho', 'gaya', 'gaye', 'gayi', 'raha', 'rahi', 'rahe',
             'diya', 'liya', 'bhi', 'hi', 'toh', 'na'}                 # attach to the word before them
KEEP_PAIRS = {('motion', 'graphics'), ('video', 'editor'), ('personal', 'brand'), ('sound', 'design'),
              ('color', 'grade'), ('colour', 'grade'), ('after', 'effects'), ('ai', 'video'), ('thumbnail', 'design'),
              ('reels', 'editing'), ('video', 'editing'), ('screen', 'time'), ('dead', 'line')}   # never split
BIND_NEXT = {'aur', 'ek', 'is', 'us', 'ye', 'yeh', 'wo', 'woh', 'jo', 'bas', 'lekin', 'magar', 'kyunki', 'agar',
             'the', 'a', 'an', 'my', 'your'}                           # attach to the word after them


def _chunk_cost(ws, gap_after, max_w, white_px, key_px, min_scale):
    n = len(ws)
    if sum(d['keyword'] for d in ws) > 1:
        return 1e9
    if n > 1 and chunk_width(ws, white_px, key_px) * min_scale > max_w:
        return 1e9
    c = {1: 2.0, 2: 0.0, 3: 0.3}.get(n, 1e9)
    if n == 1 and ws[0]['keyword']:
        c = 0.5                                       # a keyword alone is a dramatic beat, not a dangling word
    if _bare(ws[0]['word']) in BIND_PREV:
        c += 1.5
    if _bare(ws[-1]['word']) in BIND_NEXT and not (ws[-1].get('brk') or END_PUNCT.search(ws[-1]['word'])):
        c += 1.5
    return c - 2.0 * min(gap_after, 0.4)              # prefer breaking where the voice pauses


def _partition(ph, max_words, max_w, white_px, key_px, min_scale, keep=KEEP_PAIRS):
    """Best split of one phrase (no hard break inside) into chunks of <= max_words (dynamic programming)."""
    n = len(ph)
    best = [0.0] + [1e18] * n
    prev = [0] * (n + 1)
    for j in range(1, n + 1):
        for i in range(max(0, j - max_words), j):
            gap = ph[j]['start'] - ph[j - 1]['end'] if j < n else 0.4
            c = best[i] + _chunk_cost(ph[i:j], gap, max_w, white_px, key_px, min_scale)
            if j < n and (_bare(ph[j - 1]['word']), _bare(ph[j]['word'])) in keep:
                c += 3.0                                  # 'motion | graphics' must not be split
            if c < best[j]:
                best[j], prev[j] = c, i
    out, j = [], n
    while j > 0:
        out.append(ph[prev[j]:j])
        j = prev[j]
    return out[::-1]


def chunk_words(words, max_words=3, max_gap=0.45, max_w=780.0, white_px=64, key_px=128, min_scale=0.85,
                keep=KEEP_PAIRS):
    """Group word timings into caption chunks (lists of word dicts): hard breaks at pauses > max_gap and end
    punctuation, then each phrase is split into 1-3 word chunks by a small cost model (2-word chunks best,
    no lone word unless it is the keyword, never start a chunk with a word that binds to the previous one -
    ka / ke / ne / sa / hai ... - nor end it on one that binds to the next - aur / ek / bas ..., break at
    pauses, one keyword per chunk, fit the band at >= min_scale, never split a KEEP_PAIRS pair such as
    'motion graphics'; pass keep= to add your own lower-case pairs)."""
    phrases, cur = [], []
    for d in words:
        if cur and (d['start'] - cur[-1]['end'] > max_gap or cur[-1].get('brk') or END_PUNCT.search(cur[-1]['word'])):
            phrases.append(cur)
            cur = []
        cur.append(d)
    if cur:
        phrases.append(cur)
    chunks = []
    for ph in phrases:
        chunks += _partition(ph, max_words, max_w, white_px, key_px, min_scale, keep)
    # merge lone short function words into a neighbour (never a dangling 'ka' / 'hai' on its own)
    i = 0
    while i < len(chunks):
        c = chunks[i]
        if len(c) == 1 and not c[0]['keyword'] and _bare(c[0]['word']) in SHORT:
            nxt = chunks[i + 1] if i + 1 < len(chunks) else None
            prv = chunks[i - 1] if i > 0 else None
            ends_sentence = END_PUNCT.search(c[0]['word'])
            if (prv and len(prv) < max_words and c[0]['start'] - prv[-1]['end'] <= max_gap
                    and not END_PUNCT.search(prv[-1]['word'])
                    and chunk_width(prv + c, white_px, key_px) * min_scale <= max_w):
                prv.extend(c)
                chunks.pop(i)
                continue
            if (nxt and not ends_sentence and len(nxt) < max_words and nxt[0]['start'] - c[0]['end'] <= max_gap
                    and not (nxt[0]['keyword'] and False)
                    and chunk_width(c + nxt, white_px, key_px) * min_scale <= max_w):
                chunks[i] = c + nxt
                chunks.pop(i + 1)
                continue
        i += 1
    return chunks


# =============================================================================================== path
class Path:
    """Dense polyline with arc-length lookup: at(s) -> (x, y, angle_deg) (extrapolates linearly past the ends)."""

    def __init__(self, pts):
        pts = np.asarray(pts, np.float64)
        d = np.r_[0, np.cumsum(np.hypot(*np.diff(pts, axis=0).T))]
        self.p, self.s, self.L = pts, d, float(d[-1])

    def at(self, s):
        s = np.asarray(s, np.float64)
        sc = np.clip(s, 0, self.L)
        x = np.interp(sc, self.s, self.p[:, 0])
        y = np.interp(sc, self.s, self.p[:, 1])
        e = 3.0
        sa, sb = np.clip(sc - e, 0, self.L), np.clip(sc + e, 0, self.L)
        dx = np.interp(sb, self.s, self.p[:, 0]) - np.interp(sa, self.s, self.p[:, 0])
        dy = np.interp(sb, self.s, self.p[:, 1]) - np.interp(sa, self.s, self.p[:, 1])
        n = np.maximum(np.hypot(dx, dy), 1e-6)
        over = (s - sc)
        return x + dx / n * over, y + dy / n * over, np.degrees(np.arctan2(dy, dx))


def make_path(kind, xc, yb, length, scale=1.0, phase=0.0):
    """'wave' (gentle S), 'arc' (soft arch) or 'flat' baseline path centred on (xc, yb), `length` px long."""
    xs = np.linspace(xc - length / 2, xc + length / 2, 200)
    v = (xs - xc) / (length / 2)
    k = min(1.0, length / 700.0)                     # short chunks get a flatter curve (no tilted single words)
    if kind == 'wave':
        ys = yb + 15.0 * scale * k * np.sin(v * math.pi * 0.95 + phase)
    elif kind == 'arc':
        ys = yb - 22.0 * scale * k * (1 - v * v) + 11.0 * scale * k
    else:
        ys = np.full_like(xs, yb)
    return Path(np.c_[xs, ys])


# =============================================================================================== chunk
class Chunk:
    """One caption chunk: words, timing, solved layout (path, scale, glyph placements, bbox)."""

    def __init__(self, ws, idx):
        self.words, self.idx = ws, idx
        self.text = ' '.join(d['word'] for d in ws)
        self.t_in = ws[0]['start'] - 0.05
        self.t_exit0 = self.t_exit1 = None
        self.ok, self.issues = True, []
        self.scrim = None


def _rects_over(avoid, t0, t1, step=0.1):
    if avoid is None:
        return []
    if not callable(avoid):
        return [tuple(map(float, r)) for r in avoid]
    out = []
    for tt in np.arange(t0, t1 + 1e-6, step):
        out += [tuple(map(float, r)) for r in (avoid(float(tt)) or [])]
    return out


def _hit(b, rects, m):
    x0, y0, x1, y1 = b
    for r in rects:
        if x0 < r[2] + m and x1 > r[0] - m and y0 < r[3] + m and y1 > r[1] - m:
            return True
    return False


def safe_violations(b):
    """Safe-zone issues of an ink bbox (x0, y0, x1, y1) -> list of strings (empty = fine)."""
    x0, y0, x1, y1 = b
    out = []
    if x0 < SAFE_X0 or x1 > SAFE_X1:
        out.append('x outside 70-1010')
    if y0 < SAFE_Y0 or y1 > SAFE_Y1:
        out.append('y outside 230-1480')
    if x1 > RIGHT_COL[0] and y1 > RIGHT_COL[1] and y0 < RIGHT_COL[2]:
        out.append('x > 930 in y 1050-1700')
    if y1 > BOTTOM_CLEAR:
        out.append('inside the bottom 300 px')
    return out


class Captions:
    """Snake captions for a word-timing list (see module docstring)."""

    def __init__(self, words, band='lower', avoid=None, white_px=64, key_px=128, max_words=3, max_gap=0.45,
                 path='snake', offset=0.0, hide=(), lead=0.05, hold=0.35, enter=0.55, travel=70.0, scrim=0.45,
                 line=True, margin=28.0, y=None, x=None, keep_pairs=()):
        self.words = load_words(words, offset, hide)
        self.band, self.avoid, self.wpx, self.kpx = band, avoid, float(white_px), float(key_px)
        self.lead, self.hold, self.enter, self.travel = lead, hold, enter, travel
        self.scrim_k, self.line, self.margin, self.path_kind = scrim, line, margin, path
        self.y_pref, self.x_pref = y, x
        _TOKENS[0] += 1
        self._token = _TOKENS[0]
        max_w = 930 - 70 - 40 if band != 'upper' else 1010 - 70 - 40
        self.chunks = [Chunk(ws, i) for i, ws in enumerate(
            chunk_words(self.words, max_words, max_gap, max_w, self.wpx, self.kpx,
                        keep=KEEP_PAIRS | {tuple(p_) for p_ in keep_pairs}))]
        for i, ch in enumerate(self.chunks):
            ch.t_in = ch.words[0]['start'] - lead
        for i, ch in enumerate(self.chunks):
            last = ch.words[-1]
            nxt = self.chunks[i + 1].t_in if i + 1 < len(self.chunks) else None
            gap_next = (nxt - (last['end'] + hold)) if nxt is not None else 9.0
            dur = 0.12 if gap_next < 0.25 else 0.30
            t1 = last['end'] + hold + dur
            if nxt is not None:
                t1 = min(t1, nxt)
            t0 = max(t1 - dur, last['start'] - lead + 0.15)
            t1 = max(t1, t0 + 0.04)
            if nxt is not None and t1 > nxt:
                t1 = nxt
                t0 = min(t0, t1 - 0.04)
            ch.t_exit0, ch.t_exit1 = t0, t1
            self._layout(ch)

    # ------------------------------------------------------------------------------------- layout
    def _place(self, ch, s, kind, xc, yb):
        """Glyph placements + ink bbox for a chunk at scale s on a path centred at (xc, yb)."""
        ws = ch.words
        wid = [word_width(d['word'], d['keyword'], self.wpx, self.kpx) for d in ws]
        L = sum(wid) + sum(_space(ws[i - 1]['keyword'], self.wpx) for i in range(1, len(ws)))
        Lp = L * s + 160.0 * s
        p = make_path(kind, xc, yb, Lp, s, phase=0.6 * (ch.idx % 2))
        s0 = (p.L - L * s) / 2
        items, pen = [], s0
        for i, (d, ww) in enumerate(zip(ws, wid)):
            if i:
                pen += _space(ws[i - 1]['keyword'], self.wpx) * s
            g = _glyphs(d['word'], d['keyword'], self.kpx if d['keyword'] else self.wpx)
            items.append(dict(d=d, g=g, s0=pen, w=ww * s, boxes=g.boxes(), cap=g.layout.cap, key=d['keyword']))
            pen += ww * s
        off = 0.52 * self.kpx * s
        # ink bbox: each glyph's cap-top .. descender band along the path, plus the guide line
        pts = []
        for it in items:
            px_ = (self.kpx if it['key'] else self.wpx) * s
            for (x0, y0, x1, y1) in it['boxes']:
                for sx in (it['s0'] + x0 * s, it['s0'] + x1 * s):
                    x, y, a = p.at(sx)
                    ar = math.radians(float(a))
                    nu = (math.sin(ar), -math.cos(ar))
                    pts.append((x + nu[0] * it['cap'] * s * 1.04, y + nu[1] * it['cap'] * s * 1.04))
                    pts.append((x - nu[0] * px_ * 0.27, y - nu[1] * px_ * 0.27))
        if self.line:
            for sx in np.linspace(s0 - 40, s0 + L * s + 60, 12):
                x, y, a = p.at(sx)
                ar = math.radians(float(a))
                pts.append((x - math.sin(ar) * (off + 5), y + math.cos(ar) * (off + 5)))
        P = np.array(pts)
        bbox = (float(P[:, 0].min()), float(P[:, 1].min()), float(P[:, 0].max()), float(P[:, 1].max()))
        return dict(path=p, items=items, s0=s0, L=L * s, off=off, bbox=bbox, scale=s, kind=kind, xc=xc, yb=yb)

    def _layout(self, ch):
        kinds = {'snake': ('wave', 'arc')[ch.idx % 2], 'wave': 'wave', 'arc': 'arc', 'flat': 'flat'}
        kind = kinds.get(self.path_kind, 'wave')
        rects = _rects_over(self.avoid, ch.t_in - 0.1, ch.t_exit1)
        order = {'lower': ['lower', 'upper'], 'upper': ['upper', 'lower'], 'auto': ['lower', 'upper']}
        names = order.get(self.band, ['lower', 'upper'])
        bands = [(n, {'lower': 1270.0, 'upper': 700.0}[n]) for n in names]
        if self.y_pref is not None:
            bands[0] = (bands[0][0], float(self.y_pref))
        first = None
        for bname, y0 in bands:                         # the requested band first; the other one only if a face
            lo, hi = (1090.0, 1405.0) if bname == 'lower' else (330.0, 1000.0)     # leaves no room in it
            ys = [y0] + [y0 + sgn * k * 40.0 for k in range(1, 20) for sgn in (-1, 1)]
            ys = [y for y in ys if lo <= y <= hi or y == y0]
            for s in (1.0, 0.92, 0.85, 0.78):
                for yb in ys:
                    xmax = 930.0 if yb > 1000 else 1010.0
                    xcs = [self.x_pref if self.x_pref is not None else (70.0 + xmax) / 2]
                    lay0 = self._place(ch, s, kind, xcs[0], yb)
                    wbox = lay0['bbox'][2] - lay0['bbox'][0]
                    xcs += [70.0 + wbox / 2 + 2, xmax - wbox / 2 - 2]
                    for xc in xcs:
                        lay = lay0 if xc == xcs[0] else self._place(ch, s, kind, xc, yb)
                        if first is None:
                            first = lay
                        if safe_violations(lay['bbox']) or _hit(lay['bbox'], rects, self.margin):
                            continue
                        ch.lay = lay
                        return
        ch.lay = first
        ch.ok = False
        ch.issues = safe_violations(first['bbox']) + (['over an avoid rect'] if _hit(first['bbox'], rects, 0) else [])

    def prewarm(self):
        """Build every glyph sprite (call from the reel's prewarm())."""
        for ch in self.chunks:
            for it in ch.lay['items']:
                g = it['g']
                for k in range(g.n):
                    g.glyph(k)
                if it['key']:
                    _halo(it['d']['word'], self.kpx)
            self._scrim(ch)
        _head_spr()

    # ------------------------------------------------------------------------------------- drawing
    def _scrim(self, ch):
        """Static soft dark backing along the phrase (bbox-local, full res), cached on the chunk."""
        if ch.scrim is None:
            lay = ch.lay
            x0, y0, x1, y1 = lay['bbox']
            pad = 90
            X0, Y0 = int(max(0, x0 - pad)), int(max(0, y0 - pad))
            X1, Y1 = int(min(W, x1 + pad)), int(min(H, y1 + pad))
            m = np.zeros(((Y1 - Y0) // 4 + 2, (X1 - X0) // 4 + 2), np.float32)
            p = lay['path']
            r = 0.62 * self.kpx * lay['scale'] / 4
            for sx in np.linspace(lay['s0'] - 30, lay['s0'] + lay['L'] + 30, 40):
                x, y, a = p.at(sx)
                cv2.circle(m, (int((x - X0) / 4), int((y - self.kpx * 0.2 * lay['scale'] - Y0) / 4)), int(r), 1.0, -1)
            m = cv2.GaussianBlur(m, (0, 0), 9)
            m = cv2.resize(m, (m.shape[1] * 4, m.shape[0] * 4), interpolation=cv2.INTER_LINEAR)[:Y1 - Y0, :X1 - X0]
            m = np.clip(m * 1.15, 0, 1).astype(np.float32)
            m.flags.writeable = False
            ch.scrim = (X0, Y0, m)
        return ch.scrim

    def visible(self, t):
        """Chunks on screen at t (at most one: chunks never overlap)."""
        return [ch for ch in self.chunks if ch.t_in <= t < ch.t_exit1]

    def draw(self, cv, t, opacity=1.0):
        """Draw the caption state at time t into cv (pure function of t). Returns the drawn chunk or None."""
        out = None
        for ch in self.visible(t):
            self._draw_chunk(cv, ch, t, opacity)
            out = ch
        return out

    def _draw_chunk(self, cv, ch, t, opacity):
        lay = ch.lay
        p, s = lay['path'], lay['scale']
        q = K.ramp(t, ch.t_exit0, ch.t_exit1, 'in_cubic')                  # exit 0..1
        drift = q * 120.0 * s
        vis = K.ramp(t, ch.t_in, ch.t_in + 0.25, 'inout_sine') * (1.0 - q) * opacity
        if vis <= 0.002:
            return
        if self.scrim_k > 0:
            X0, Y0, m = self._scrim(ch)
            reg = cv[Y0:Y0 + m.shape[0], X0:X0 + m.shape[1], :3]
            reg *= (1.0 - m * np.float32(self.scrim_k * vis))[..., None]
        if self.line:
            self._guide(cv, ch, t, q, drift, vis)
        for ii, it in enumerate(lay['items']):
            d = it['d']
            u = t - (d['start'] - self.lead)
            if u < 0:
                continue
            if u >= 0.9 and q <= 0.0:                     # settled: one cached bbox sprite, pixel aligned
                X0, Y0, spr = self._settled(ch, ii)
                K.draw(cv, spr, X0, Y0, anchor=(0, 0), opacity=opacity)
                continue
            self._draw_word(cv, ch, it, t, u, q, drift, opacity)

    def _word_state(self, it, u, q, drift, s):
        pe = K.EASE['out_expo'](K.clamp(u / self.enter))
        if it['key']:
            sc = s * (1.06 - 0.06 * K.EASE['out_cubic'](K.clamp(u / self.enter)))
        else:
            sc = s * (0.90 + 0.10 * K.spring(u, 2.6, 0.5))
        fb = (1.0 - K.ramp(u, 0, self.enter * 0.8, 'out_quart')) * 10.0 + q * 12.0
        fb = 0.0 if fb < 1.0 else float(round(fb))
        return pe, sc, fb, it['s0'] - (1.0 - pe) * self.travel * s + drift

    def _draw_word(self, cv, ch, it, t, u, q, drift, opacity, settled=False):
        lay = ch.lay
        p, s = lay['path'], lay['scale']
        d = it['d']
        if settled:
            pe, sc, fb, pen0 = 1.0, s, 0.0, it['s0']
            op = 1.0
        else:
            pe, sc, fb, pen0 = self._word_state(it, u, q, drift, s)
            op = K.ramp(u, 0, self.enter * 0.45, 'inout_sine') * (1.0 - q) * opacity
        if op <= 0.003:
            return
        g = it['g']
        for k, (x0, y0, x1, y1) in enumerate(it['boxes']):
            x, y, a = p.at(pen0 + (x0 + x1) / 2 * s)
            ar = math.radians(float(a))
            lift = it['cap'] / 2 * sc
            g.glyph(k).draw(cv, float(x) + math.sin(ar) * lift, float(y) - math.cos(ar) * lift, anchor=(0.5, 0.5),
                            scale=sc, rot=float(a), opacity=op, blur=fb)
        if it['key']:
            x, y, a = p.at(pen0 + it['w'] / 2)
            ar = math.radians(float(a))
            lift = it['cap'] / 2 * sc
            hk = op * (0.85 + 0.9 * (1.0 - pe))                          # the glow flares while it enters
            _halo(d['word'], self.kpx).draw(cv, float(x) + math.sin(ar) * lift, float(y) - math.cos(ar) * lift,
                                            scale=sc, rot=float(a), opacity=min(1.6, hk))

    def _settled(self, ch, ii):
        """Settled word as one bbox sprite (built once, byte-budget LRU): (x0, y0, sprite)."""
        key = (self._token, ch.idx, ii)
        v = _SETTLED.get(key)
        if v is not None:
            return v[0]
        it = ch.lay['items'][ii]
        tmp = np.zeros((H, W, 4), np.float32)
        self._draw_word(tmp, ch, it, 0.0, 9.0, 0.0, 0.0, 1.0, settled=True)
        nz = np.abs(tmp).max(2) > 1e-5
        rows, cols = np.nonzero(nz.any(1))[0], np.nonzero(nz.any(0))[0]
        if len(rows) == 0:
            out = (0, 0, np.zeros((1, 1, 4), np.float32))
        else:
            y0, y1, x0, x1 = rows[0], rows[-1] + 1, cols[0], cols[-1] + 1
            spr = np.ascontiguousarray(tmp[y0:y1, x0:x1])
            spr.flags.writeable = False
            out = (int(x0), int(y0), spr)
        _SETTLED.put(key, out, out[2].nbytes)
        return out

    def _guide(self, cv, ch, t, q, drift, vis):
        """Thin glowing guide line under the words: tail fades, head is hot; it draws ahead of the voice."""
        lay = ch.lay
        p, s = lay['path'], lay['scale']
        spoken = [it for it in lay['items'] if t >= it['d']['start'] - self.lead]
        if not spoken:
            return
        it = spoken[-1]
        pl = K.EASE['out_expo'](K.clamp((t - (it['d']['start'] - self.lead)) / 0.45))
        head = it['s0'] - 30 * s + (it['w'] + 60 * s) * pl + drift * 1.4
        tail = lay['s0'] - 40 * s + q * (lay['L'] + 140 * s)
        head = min(head, lay['s0'] + lay['L'] + 70 * s + drift * 1.4)
        if head - tail < 6:
            return
        ss = np.linspace(tail, head, max(10, int((head - tail) / 5)))
        x, y, a = p.at(ss)
        ar = np.radians(a)
        off = lay['off']
        px_, py_ = x - np.sin(ar) * off, y + np.cos(ar) * off
        pad = 40
        bx0, by0 = int(max(0, px_.min() - pad)), int(max(0, py_.min() - pad))
        bx1, by1 = int(min(W, px_.max() + pad)), int(min(H, py_.max() + pad))
        if bx1 <= bx0 or by1 <= by0:
            return
        m = np.zeros((by1 - by0, bx1 - bx0), np.float32)
        n = len(ss)
        prog = np.arange(n) / max(n - 1, 1)
        fade = np.clip(prog / 0.45, 0, 1) ** 1.4                         # tail fades in, head is hot
        width = 1 + (prog > 0.6)                                         # thin tail, thicker towards the head
        P = np.int32(np.c_[(px_ - bx0) * 16, (py_ - by0) * 16])
        for j in range(n - 1):
            cv2.line(m, tuple(P[j]), tuple(P[j + 1]), float(fade[j]), int(width[j] + 1), cv2.LINE_AA, shift=4)
        glow = cv2.GaussianBlur(m, (0, 0), 3.0) * 0.9 + cv2.GaussianBlur(m, (0, 0), 9.0) * 0.6
        k = np.float32(0.9 * vis)
        reg = cv[by0:by1, bx0:bx1, :3]
        reg += glow[..., None] * (np.float32(K.C['FLAME']) * 1.3 * k)
        reg += m[..., None] * ((np.float32(K.C['AMBER']) * 0.6 + np.float32(K.C['WHITE']) * 0.5) * k)
        if q < 1:
            K.draw(cv, _head_spr(), float(px_[-1]), float(py_[-1]), opacity=float(vis * (1 - q)), mode='add')

    # ------------------------------------------------------------------------------------- QA / export
    def report(self):
        """One dict per chunk: text, t_in, t_exit0, t_exit1, scale, baseline y, bbox, ok, issues."""
        return [dict(i=ch.idx, text=ch.text, t_in=round(ch.t_in, 3), t_exit0=round(ch.t_exit0, 3),
                     t_exit1=round(ch.t_exit1, 3), scale=ch.lay['scale'], y=ch.lay['yb'], x=ch.lay['xc'],
                     bbox=tuple(round(v, 1) for v in ch.lay['bbox']), keyword=[d['word'] for d in ch.words
                                                                              if d['keyword']],
                     ok=ch.ok, issues=list(ch.issues)) for ch in self.chunks]

    def check(self, step=0.1):
        """QA every `step` s: overlapping chunks, safe zones, avoid rects, chunk sizes. -> list of issues."""
        out = []
        for a, b in zip(self.chunks, self.chunks[1:]):
            if b.t_in < a.t_exit1 - 1e-6:
                out.append('chunks %d/%d overlap in time' % (a.idx, b.idx))
        for ch in self.chunks:
            if not 1 <= len(ch.words) <= 3:
                out.append('chunk %d has %d words' % (ch.idx, len(ch.words)))
            if sum(d['keyword'] for d in ch.words) > 1:
                out.append('chunk %d has 2 keywords' % ch.idx)
            out += ['chunk %d: %s' % (ch.idx, v) for v in safe_violations(ch.lay['bbox'])]
            if self.avoid is not None:
                for tt in np.arange(ch.t_in, ch.t_exit1, step):
                    if _hit(ch.lay['bbox'], _rects_over(self.avoid, tt, tt), 0.0):
                        out.append('chunk %d over an avoid rect at %.2f s' % (ch.idx, tt))
                        break
        return out

    def save_srt(self, path):
        """Plain SRT of the chunks (upload captions; no styling)."""
        def ts(x):
            ms = int(round(max(0.0, x) * 1000))
            return '%02d:%02d:%02d,%03d' % (ms // 3600000, ms // 60000 % 60, ms // 1000 % 60, ms % 1000)
        with open(path, 'w', encoding='utf8') as f:
            for i, ch in enumerate(self.chunks, 1):
                f.write('%d\n%s --> %s\n%s\n\n' % (i, ts(ch.t_in), ts(ch.t_exit1), ch.text))
        return path


# =============================================================================================== selftest
SAMPLE = [  # Roman Urdu demo line (timings synthetic); '*' = keyword
    ('Bhai,', 0.30, 0.52), ('client', 0.56, 0.88), ('ne', 0.90, 1.00), ('bola', 1.02, 1.30), ('bas', 1.36, 1.52),
    ('thoda', 1.55, 1.82), ('sa', 1.84, 1.95), ('*change...', 1.98, 2.55), ('aur', 3.10, 3.25), ('phir', 3.28, 3.50),
    ('raat', 3.55, 3.80), ('ke', 3.82, 3.92), ('*teen', 3.95, 4.30), ('baj', 4.34, 4.52), ('gaye.', 4.55, 4.95)]


def selftest():
    """Builds captions for a demo line twice (no faces / a face rect in the lower band), checks the rules,
    renders frames and writes <WS>/out/selftest/snake_captions_*.png."""
    os.makedirs(K.SELFTEST, exist_ok=True)
    words = [dict(word=w, start=s, end=e) for w, s, e in SAMPLE]
    fails = []
    face = (300, 1080, 760, 1420)                                    # a face sitting in the lower band
    tm = []
    sheets = []
    for name, avoid in (('free', None), ('face', [face])):
        cap = Captions(words, band='lower', avoid=avoid)
        cap.prewarm()
        issues = cap.check()
        if issues:
            fails += ['%s: %s' % (name, i) for i in issues]
        rep = cap.report()
        if any(not r['ok'] for r in rep):
            fails.append('%s: unplaced chunk %s' % (name, [r for r in rep if not r['ok']]))
        kws = [r['keyword'] for r in rep]
        if sum(len(k) for k in kws) != 2:
            fails.append('%s: keywords lost %s' % (name, kws))
        print(name, 'chunks:', [(r['text'], r['scale'], r['y'], r['bbox']) for r in rep])
        times = [0.45, 1.2, 2.3, 2.9, 4.05, 4.9]
        frames = []
        for tt in times:
            cv = K.background('ember', tt, bokeh=0.5)
            if avoid:
                x0, y0, x1, y1 = face
                cv[y0:y1, x0:x1, :3] = cv[y0:y1, x0:x1, :3] * 0.4 + np.float32(K.C['ASH']) * 0.15
            cap.draw(cv, tt)
            c2 = cv.copy()
            K.background('ember', tt, bokeh=0.5)
            t0 = time.perf_counter()
            cv3 = K.background('ember', tt, bokeh=0.5)
            tb = time.perf_counter() - t0
            t0 = time.perf_counter()
            cap.draw(cv3, tt)
            tm.append((time.perf_counter() - t0) * 1e3)
            cv4 = K.background('ember', tt, bokeh=0.5)
            cap.draw(cv4, tt)
            if not np.array_equal(cv3, cv4):
                fails.append('impure draw at %.2f' % tt)
            if not np.isfinite(c2).all():
                fails.append('nan at %.2f' % tt)
            K.post(c2, 'ember', tt)
            u8 = K.to_srgb8(c2, tt)
            if avoid:
                x0, y0, x1, y1 = face
                cv2.rectangle(u8, (x0, y0), (x1, y1), (90, 160, 255), 3)
            cv2.rectangle(u8, (70, 230), (1010, 1480), (60, 90, 60), 2)
            cv2.line(u8, (930, 1050), (930, 1700), (60, 90, 60), 2)
            cv2.putText(u8, '%s t=%.2f' % (name, tt), (90, 290), cv2.FONT_HERSHEY_SIMPLEX, 1.4, (120, 220, 255), 3)
            frames.append(cv2.resize(u8, (360, 640), interpolation=cv2.INTER_AREA))
        sheet = np.hstack(frames)
        p = os.path.join(K.SELFTEST, 'snake_captions_%s.png' % name)
        cv2.imwrite(p, sheet[..., ::-1])
        sheets.append(p)
        # full-res crop of the keyword frame for close inspection
        cv = K.background('ember', 4.3, bokeh=0.5)
        cap.draw(cv, 4.3)
        K.post(cv, 'ember', 4.3)
        u8 = K.to_srgb8(cv, 4.3)
        b = [ch for ch in cap.chunks if ch.t_in <= 4.3 < ch.t_exit1][0].lay['bbox']
        crop = u8[int(max(0, b[1] - 80)):int(min(H, b[3] + 80)), int(max(0, b[0] - 60)):int(min(W, b[2] + 60))]
        p = os.path.join(K.SELFTEST, 'snake_captions_%s_crop.png' % name)
        cv2.imwrite(p, crop[..., ::-1])
        sheets.append(p)
        if avoid:
            # the face chunk must have moved off the face
            for ch in cap.chunks:
                if _hit(ch.lay['bbox'], [face], 0):
                    fails.append('chunk %d over the face' % ch.idx)
    # chunking rules on their own
    ch = chunk_words(load_words(words))
    if any(len(c) > 3 for c in ch):
        fails.append('chunk > 3 words')
    if any(len(c) == 1 and _bare(c[0]['word']) in SHORT for c in ch):
        fails.append('lone short word chunk')
    print('chunks:', [' '.join(d['word'] for d in c) for c in ch])
    print('draw cost ms (one chunk visible): median %.1f, max %.1f' % (np.median(tm), max(tm)))
    for p in sheets:
        print('->', p)
    if fails:
        print('FAIL:', *fails, sep='\n  ')
        return False
    print('snake_captions selftest OK')
    return True


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] in ('selftest', '--selftest'):
        sys.exit(0 if selftest() else 1)
    print(__doc__)
