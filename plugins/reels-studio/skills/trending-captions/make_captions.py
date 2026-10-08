#!/usr/bin/env python3
"""make_captions.py: trending animated captions for 9:16 reels -> .ass (burn with ffmpeg/libass) + .srt.

USAGE
  python3 make_captions.py WORDS.json  --preset bold-pop --font /path/Brand-Black.ttf --highlight '#FFD21F' -o out/caps
  python3 make_captions.py talk.mp4    --preset karaoke  --fontsdir fonts/ --model large-v3 --language en
  python3 make_captions.py --sample words.json          # writes a 4 s demo word-timing file, then exits

INPUT (one positional argument)
  *.json      word timings. Accepted shapes:
                [{"word": "Hello", "start": 0.12, "end": 0.40}, ...]      ("text" works instead of "word")
                {"words": [...]}   or   {"segments": [{"words": [...]}, ...]}   (whisper-style)
              Optional per-word keys: "emph": true (force emphasis), "prob" (ASR confidence, shown in the report).
  media file  .mp4 .mov .mkv .wav .mp3 .m4a ...: transcribed with faster-whisper (word timestamps, VAD) if it
              is installed, written to <out>.words.json. Review and fix that JSON (brand names, numbers), then
              run again on the JSON. faster-whisper is optional: `uv pip install faster-whisper` (or pip).

OUTPUT
  <out>.ass             libass subtitles at the video resolution (PlayRes = --res), one preset
  <out>.srt             plain captions for the platform's caption upload / editing (sentence chunks, 2 x 42 chars)
  <out>.captions.json   phrases, times, line breaks, bounding boxes and the safe-zone report (for QA)
  and prints the ffmpeg burn command.

PRESETS
  bold-pop  big uppercase, heavy weight, thick outline; the phrase pops in, the active word turns the highlight
            colour and pops (scale), emphasis words stay highlighted and larger. Talking heads, hooks, energy.
  karaoke   progressive highlight: each word fills left to right (\\kf) as it is spoken. Tutorials, fast VO.
  boxed     each phrase sits in a rounded box (brand colour or dark glass), active word in the highlight
            colour. Busy or bright footage, brand-heavy pieces.
  minimal   sentence case, medium weight, soft shadow, gentle fades, no highlight; a clean lower third.
            Calm, premium, documentary, interviews.
  --pill    (bold-pop, boxed) draws a rounded highlight pill behind the active word instead of recolouring it.

SAFE ZONES (1080x1920; scaled for other resolutions): captions stay inside x 70-1010, y 230-1480, never at
x > 930 where y 1050-1700 (like/share column), nothing below y 1620. The default max line width is derived from
these rules and the block centre; violations are printed as SAFE-ZONE lines (exit 1 with --strict).
"""
import argparse
import json
import math
import os
import re
import shlex
import struct
import subprocess
import sys

# ------------------------------------------------------------------------------------------------ presets
PRESETS = {
    'bold-pop': dict(size=84, case='upper', max_words=3, lines=2, y=1240, mode='words',
                     weights=('black', 'extrabold', 'heavy', 'bold'), outline=0.085, shadow=0.035, shadow_alpha=0.45,
                     blur=0.6, line_h=1.14, word_gap=1.2, pop=1.12, entry_scale=0.72, emph_scale=1.12,
                     strip_punct=True, rise=0.20),
    'karaoke': dict(size=74, case='upper', max_words=4, lines=2, y=1250, mode='kara',
                    weights=('extrabold', 'black', 'heavy', 'bold'), outline=0.075, shadow=0.03, shadow_alpha=0.5,
                    blur=0.6, line_h=1.08, word_gap=1.0, pop=1.0, entry_scale=1.0, emph_scale=1.08,
                    strip_punct=True, rise=0.16),
    'boxed': dict(size=62, case='as-is', max_words=4, lines=2, y=1250, mode='words',
                  weights=('bold', 'extrabold', 'semibold', 'black'), outline=0.0, shadow=0.0, shadow_alpha=1.0,
                  blur=0.0, line_h=1.22, word_gap=1.0, pop=1.0, entry_scale=0.94, emph_scale=1.0,
                  strip_punct=False, rise=0.12, box=True, pad=(0.55, 0.44), radius=0.42),
    'minimal': dict(size=54, case='as-is', max_words=4, lines=2, y=1390, mode='lines',
                    weights=('semibold', 'medium', 'bold', 'regular'), outline=0.05, outline_alpha=0.62,
                    shadow=0.05, shadow_alpha=0.6, blur=2.5, line_h=1.26, word_gap=1.0, pop=1.0,
                    entry_scale=1.0, emph_scale=1.0, strip_punct=False, rise=0.0),
}
COLORS = dict(text='#FFFFFF', highlight='#FFD21F', outline='#000000', box='#101014')
REF_W, REF_H = 1080, 1920
SAFE = dict(x0=70, x1=1010, y0=230, y1=1480, col_x=930, col_y0=1050, col_y1=1700, floor=1620)
STOP = set('a an and are as at be but by for from has have i if in into is it its of on or so that the their them '
           'then there they this to was we were what when which who will with you your our us me my he she his her '
           'do does did not no yes just can could would should get got going gonna im youre dont its thats'.split())
MEDIA_EXT = ('.mp4', '.mov', '.mkv', '.webm', '.m4v', '.avi', '.wav', '.mp3', '.m4a', '.aac', '.flac', '.ogg')


def die(msg, code=2):
    print(msg, file=sys.stderr)
    sys.exit(code)


# ------------------------------------------------------------------------------------------------ fonts
def sfnt_metrics(path):
    """unitsPerEm, usWinAscent, usWinDescent, capHeight from the font file (no fontTools needed).
    libass sizes a font so that winAscent + winDescent == Fontsize, so em_px = Fontsize * upm / (wA + wD)."""
    with open(path, 'rb') as f:
        data = f.read()
    off = 0
    if data[:4] == b'ttcf':
        off = struct.unpack('>I', data[12:16])[0]
    n = struct.unpack('>H', data[off + 4:off + 6])[0]
    tables = {}
    for i in range(n):
        rec = off + 12 + 16 * i
        tag = data[rec:rec + 4].decode('latin-1')
        tables[tag] = struct.unpack('>I', data[rec + 8:rec + 12])[0]
    upm = struct.unpack('>H', data[tables['head'] + 18:tables['head'] + 20])[0]
    o = tables.get('OS/2')
    if o is None:
        return upm, int(upm * 0.95), int(upm * 0.25), int(upm * 0.7)
    ver = struct.unpack('>H', data[o:o + 2])[0]
    wa, wd = struct.unpack('>HH', data[o + 74:o + 78])
    cap = struct.unpack('>h', data[o + 88:o + 90])[0] if ver >= 2 else 0
    return upm, wa, wd, cap if cap > 0 else int(upm * 0.7)


def font_names(path):
    """(family, style, full name) via PIL/FreeType."""
    from PIL import ImageFont
    fam, sty = ImageFont.truetype(path, 20).getname()
    full = fam if (sty or 'Regular').lower() in ('regular', 'normal', 'book', 'roman') else '%s %s' % (fam, sty)
    return fam, sty or 'Regular', full


def _norm(s):
    return re.sub(r'[^a-z0-9]', '', s.lower())


def resolve_font(font, fontsdir, weights):
    """Return dict(path, name, fontsdir). `font` may be a TTF/OTF path, a family/full name, or None (auto-pick
    the heaviest preferred weight in fontsdir). Fontname written to the ASS is the face's full name, which
    libass matches exactly (Bold=0 so it never synthesises bold on top)."""
    if font and os.path.isfile(font):
        path = os.path.abspath(font)
        return dict(path=path, name=font_names(path)[2], fontsdir=os.path.abspath(fontsdir or os.path.dirname(path)))
    cands = []
    if fontsdir and os.path.isdir(fontsdir):
        for fn in sorted(os.listdir(fontsdir)):
            if fn.lower().endswith(('.ttf', '.otf')):
                p = os.path.join(fontsdir, fn)
                try:
                    fam, sty, full = font_names(p)
                except Exception:
                    continue
                cands.append((p, fam, sty, full))
    if font:
        key = _norm(font)
        fam_c = [c for c in cands if _norm(c[1]).startswith(key) or _norm(c[3]).startswith(key)]
        for p, fam, sty, full in cands:
            if key in (_norm(full), _norm(fam + sty), _norm(os.path.splitext(os.path.basename(p))[0])):
                if full == fam and len(fam_c) > 1:     # a bare family name ("Poppins"): pick the preset weight
                    break
                return dict(path=p, name=full, fontsdir=os.path.abspath(fontsdir))
        if fam_c:
            cands = fam_c
        else:
            print('note: font "%s" not found in fontsdir; libass will use the system font of that name, layout '
                  'widths are estimated' % font)
            return dict(path=None, name=font, fontsdir=os.path.abspath(fontsdir) if fontsdir else None)
    if not cands:
        return dict(path=None, name=font or 'DejaVu Sans', fontsdir=None)
    upright = [c for c in cands if 'italic' not in c[2].lower() and 'oblique' not in c[2].lower()] or cands
    for w in weights:
        for c in upright:
            if w in _norm(c[3]) and (w != 'bold' or not re.search('semibold|extrabold|ultrabold|demibold', _norm(c[3]))):
                return dict(path=c[0], name=c[3], fontsdir=os.path.abspath(fontsdir))
    c = upright[0]
    return dict(path=c[0], name=c[3], fontsdir=os.path.abspath(fontsdir))


class Metrics:
    """Text advance widths (PIL + raqm/HarfBuzz when available, which matches libass shaping) at an em size."""

    def __init__(self, path, em):
        self.path, self.em = path, em
        if path:
            from PIL import ImageFont
            self.upm, self.wa, self.wd, cap = sfnt_metrics(path)
            self.font = ImageFont.truetype(path, em)
            self.cap = cap / self.upm * em
            self.ass_size = em * (self.wa + self.wd) / self.upm
            self.box_off = (cap / 2 - (self.wa - self.wd) / 2) / self.upm * em   # \an5 box centre below cap centre
        else:
            self.font = None
            self.cap = 0.70 * em
            self.ass_size = 1.2 * em
            self.box_off = 0.05 * em
        self._c = {}

    def adv(self, s):
        if s not in self._c:
            if self.font is not None:
                self._c[s] = float(self.font.getlength(s))
            else:
                self._c[s] = sum((0.5 if c == ' ' else 0.66 if c.isupper() else 0.56) for c in s) * self.em
        return self._c[s]


# ------------------------------------------------------------------------------------------------ words
def load_words(path):
    with open(path) as f:
        d = json.load(f)
    if isinstance(d, dict):
        if 'words' in d:
            d = d['words']
        elif 'segments' in d:
            d = [w for s in d['segments'] for w in (s.get('words') or [])]
    out = []
    for w in d:
        txt = str(w.get('word', w.get('text', ''))).strip()
        if not txt:
            continue
        s, e = float(w['start']), float(w['end'])
        if re.fullmatch(r'[^\w£$€¥%#@&]+', txt) and out:      # punctuation-only token -> glue to previous word
            out[-1]['word'] += txt
            out[-1]['end'] = max(out[-1]['end'], e)
            continue
        out.append(dict(word=txt, start=s, end=e, emph=bool(w.get('emph')), prob=w.get('prob', w.get('probability'))))
    out.sort(key=lambda w: w['start'])
    for i, w in enumerate(out):
        if w['end'] <= w['start']:
            w['end'] = w['start'] + 0.08
        if i and w['start'] < out[i - 1]['start']:
            w['start'] = out[i - 1]['start']
    return out


def transcribe(media, a, out_json):
    os.makedirs(os.path.dirname(os.path.abspath(out_json)) or '.', exist_ok=True)   # before the long transcription
    try:
        from faster_whisper import WhisperModel
    except ImportError:
        die('faster-whisper is not installed, so %s cannot be transcribed.\n'
            '  Install it in the project venv:  uv pip install faster-whisper   (or: pip install faster-whisper)\n'
            '  GPU (CUDA 12): also  uv pip install nvidia-cublas-cu12 "nvidia-cudnn-cu12==9.*"  or use --device cpu.\n'
            '  Or supply word timings yourself: a JSON list of {"word", "start", "end"} and run this script on it.'
            % media)
    print('transcribing %s with faster-whisper (%s, device %s) ...' % (media, a.model, a.device))
    model = WhisperModel(a.model, device=a.device, compute_type=a.compute_type)
    segs, info = model.transcribe(media, language=a.language, word_timestamps=True, vad_filter=True,
                                  initial_prompt=a.prompt or None, beam_size=5, condition_on_previous_text=False)
    words = []
    for s in segs:
        for w in (s.words or []):
            words.append(dict(word=w.word.strip(), start=round(w.start, 3), end=round(w.end, 3),
                              prob=round(float(w.probability), 3)))
    with open(out_json, 'w') as f:
        json.dump(dict(source=os.path.abspath(media), language=info.language, model=a.model, words=words), f, indent=1)
    print('words -> %s  (%d words, language %s). Check spellings, names and numbers against the script.'
          % (out_json, len(words), info.language))
    return out_json


def write_sample(path):
    seq = [('Stop', .15, .45), ('scrolling.', .45, 1.0), ('This', 1.12, 1.28), ('is', 1.28, 1.38), ('how', 1.38, 1.55),
           ('your', 1.55, 1.70), ('captions', 1.70, 2.15), ('pop', 2.15, 2.50), ('on', 2.58, 2.68),
           ('every', 2.68, 2.92), ('word,', 2.92, 3.20), ('100%', 3.30, 3.72), ('in', 3.72, 3.80), ('sync.', 3.80, 3.98)]
    with open(path, 'w') as f:
        json.dump(dict(words=[dict(word=w, start=s, end=e) for w, s, e in seq]), f, indent=1)
    print('sample words ->', path)


# ------------------------------------------------------------------------------------------------ helpers
def hex_bgr(h):
    h = h.strip().lstrip('#')
    if len(h) == 3:
        h = ''.join(c * 2 for c in h)
    if not re.fullmatch(r'[0-9a-fA-F]{6}', h):
        die('bad colour %r (use #RRGGBB)' % h)
    return h[4:6].upper() + h[2:4].upper() + h[0:2].upper()


def alpha_hex(opacity):
    return '%02X' % int(round((1 - max(0.0, min(1.0, opacity))) * 255))


def ass_time(frame, fps):
    cs = int(math.floor(frame * 100.0 / fps + 1e-6))          # floor: frame k shows events starting at frame k
    h, cs = divmod(cs, 360000)
    m, cs = divmod(cs, 6000)
    s, cs = divmod(cs, 100)
    return '%d:%02d:%02d.%02d' % (h, m, s, cs)


def srt_time(t):
    ms = int(round(max(0.0, t) * 1000))
    h, ms = divmod(ms, 3600000)
    m, ms = divmod(ms, 60000)
    s, ms = divmod(ms, 1000)
    return '%02d:%02d:%02d,%03d' % (h, m, s, ms)


def esc(s):
    return s.replace('\\', '/').replace('{', '(').replace('}', ')')


def display(word, P, case):
    s = word
    if P['strip_punct']:
        s = re.sub(r'(?<=\w)[.,;:]+$', '', s) if not re.fullmatch(r'[\d.,]+', s) else s.rstrip('.,;:')
    if case == 'upper':
        s = s.upper()
    elif case == 'lower':
        s = s.lower()
    return s


def rrect(w, h, r):
    """ASS drawing path of a rounded rectangle (0,0)-(w,h), cubic corners (k = 0.5523)."""
    r = max(0.0, min(r, w / 2, h / 2))
    k = 0.5523 * r
    f = lambda v: ('%.1f' % v).rstrip('0').rstrip('.')
    pts = ['m %s 0' % f(r), 'l %s 0' % f(w - r), 'b %s 0 %s %s %s %s' % (f(w - r + k), f(w), f(r - k), f(w), f(r)),
           'l %s %s' % (f(w), f(h - r)), 'b %s %s %s %s %s %s' % (f(w), f(h - r + k), f(w - r + k), f(h), f(w - r), f(h)),
           'l %s %s' % (f(r), f(h)), 'b %s %s 0 %s 0 %s' % (f(r - k), f(h), f(h - r + k), f(h - r)),
           'l 0 %s' % f(r), 'b 0 %s %s 0 %s 0' % (f(r - k), f(r - k), f(r))]
    return ' '.join(pts)


# ------------------------------------------------------------------------------------------------ layout
def layout(disp, emph, P, M, max_w, max_lines):
    """Split a phrase into <= max_lines balanced lines. Returns (lines [[idx..]], widths, gap, shrink).
    Lines are fitted at their PEAK width: any one word at the active-word pop scale (plus its pill), centred on
    the line centre, must stay inside max_w, so a single wide word that pops cannot reach the like/share column."""
    widths = [M.adv(d) * (P['emph_scale'] if e else 1.0) for d, e in zip(disp, emph)]
    gap = M.adv(' ') * P['word_gap'] + 2 * P.get('out_px', 0.0) + P.get('extra_gap', 0.0)   # outline-independent
    lw = lambda seq: sum(widths[i] for i in seq) + gap * (len(seq) - 1)
    pop, pad, opx = P['pop'], P.get('pill_pad', 0.0), P.get('out_px', 0.0)

    def span(seq):                                 # peak width around the line centre (outer outline excluded)
        L = lw(seq)
        x, m = -L / 2, L / 2
        for i in seq:
            m = max(m, abs(x + widths[i] / 2) + 0.5 * (widths[i] + pad) * pop + opx * (pop - 1))
            x += widths[i] + gap
        return 2 * m
    n = len(disp)
    lines = [list(range(n))]
    if span(lines[0]) > max_w and max_lines >= 2 and n >= 2:
        best = None
        for k in range(1, n):
            a, b = list(range(k)), list(range(k, n))
            weak = re.sub(r'[^\w]', '', disp[k - 1].lower()) in WEAK_END
            score = (max(span(a), span(b)) * (1.2 if weak else 1.0), lw(a) > lw(b))   # balanced, no weak line end
            if best is None or score < best[0]:
                best = (score, [a, b])
        lines = best[1]
    widest = max(span(l) for l in lines)
    shrink = min(1.0, max_w / widest) if widest > 0 else 1.0
    return lines, widths, gap, shrink


WEAK_END = set('a an the to of in on at for with and or but nor your my our their his her its is are was were be '
               'been that this these those from by as into than so if very really just i we you they it'.split())


def chunk(words, P, fits, max_words, gap_s):
    """Split into clauses (sentence ends, commas, pauses > gap_s), then cut each clause into phrases of
    1..max_words with a small DP: fewest phrases, balanced sizes, no phrase ending on a weak word
    ("the", "your", "to" ...), no lonely single words, every phrase fits the safe width."""
    clauses, cur = [], []
    for w in words:
        if cur and (w['start'] - cur[-1]['end'] > gap_s or cur[-1]['word'][-1] in '.?!,;:'):
            clauses.append(cur)
            cur = []
        cur.append(w)
    if cur:
        clauses.append(cur)
    out = []
    for c in clauses:
        n = len(c)
        k = max(1, math.ceil(n / max_words))
        target = n / k
        best = [0.0] + [math.inf] * n
        prev = [0] * (n + 1)
        for j in range(1, n + 1):
            for size in range(1, min(max_words, j) + 1):
                i = j - size
                seg = c[i:j]
                if best[i] == math.inf or (size > 1 and not fits(seg)):
                    continue
                last = re.sub(r'[^\w]', '', seg[-1]['word'].lower())
                cost = 10.0 + 0.8 * (size - target) ** 2
                if j < n and last in WEAK_END:
                    cost += 4.0
                if size == 1 and n > 1 and not seg[0]['emph']:
                    cost += 3.0
                if seg[-1]['end'] - seg[0]['start'] > 2.6:
                    cost += 5.0
                if best[i] + cost < best[j]:
                    best[j], prev[j] = best[i] + cost, i
        cuts, j = [], n
        while j > 0:
            cuts.append((prev[j], j))
            j = prev[j]
        out += [c[i:j] for i, j in reversed(cuts)]
    return out


# ------------------------------------------------------------------------------------------------ main build
def build(a):
    P = dict(PRESETS[a.preset])
    rw, rh = [int(v) for v in a.res.lower().split('x')]
    sx, sy = rw / REF_W, rh / REF_H
    fps = a.fps
    case = a.case or P['case']
    max_words = max(1, a.max_words or P['max_words'])
    max_lines = max(1, a.lines or P['lines'])
    em = (a.size or P['size']) * sy
    font = resolve_font(a.font, a.fontsdir, P['weights'])
    M = Metrics(font['path'], em)
    if font['path'] is None:
        print('note: no font file found (pass --font PATH.ttf or --fontsdir DIR); widths are estimated.')
    col = dict(text=a.text_color, hl=a.highlight, emph=a.emph_color or a.highlight, outline=a.outline_color,
               box=a.box_color, pill=a.pill_color or a.highlight, pill_text=a.pill_text or a.text_color)
    B = {k: hex_bgr(v) for k, v in col.items()}
    pill = a.pill and P['mode'] == 'words'
    if pill:
        P['extra_gap'] = 0.30 * em               # room for the pill padding between words
        if not P.get('box'):                     # boxed: the phrase box already covers the pill padding
            P['pill_pad'] = 0.56 * em
    if a.pill and not pill:
        print('note: --pill applies to bold-pop and boxed only; ignored.')

    out_px = P['outline'] * em
    P['out_px'] = out_px
    shad_px = P['shadow'] * em
    cx = (a.x if a.x is not None else 540) * sx

    def y_for(t):
        for t0, t1, yy in a.y_at:
            if t0 <= t < t1:
                return yy * sy
        return (a.y if a.y is not None else P['y']) * sy

    padx, pady = [v * em for v in P.get('pad', (0, 0))]
    if a.max_width:
        max_w = a.max_width * sx
    else:                                           # safe width around cx; the caption band overlaps the column zone
        half = min(cx - SAFE['x0'] * sx, SAFE['col_x'] * sx - cx)
        max_w = 2 * half - 2 * out_px - 2 * padx - 2 * (shad_px + P['blur'])   # shadow and blur are ink too
        # layout() fits each line at its peak pop / pill width inside max_w
    max_w = max(200.0, max_w)

    words = load_words(a.input_json)
    if not words:
        die('no words in %s' % a.input_json)
    for w in words:
        w['start'] += a.offset
        w['end'] += a.offset
    emph_set = {_norm(e) for e in (a.emphasis.split(',') if a.emphasis else []) if e.strip()}
    for w in words:
        nw = _norm(w['word'])
        w['emph'] = bool(w['emph'] or (nw and nw in emph_set) or
                         (not a.no_number_emphasis and re.search(r'[\d£$€¥%]', w['word'])))
        w['disp'] = display(w['word'], P, case)

    def fits(ws):
        _, _, _, shrink = layout([w['disp'] for w in ws], [w['emph'] for w in ws], P, M, max_w, max_lines)
        return shrink >= 0.999

    phrases = chunk(words, P, fits, max_words, a.gap)

    # ---- phrase timing (frames)
    F = lambda t: int(round(t * fps))
    starts = [max(0.0, p[0]['start'] - a.lead) for p in phrases]
    ph = []
    for i, p in enumerate(phrases):
        s = starts[i]
        nxt = starts[i + 1] if i + 1 < len(phrases) else None
        e = p[-1]['end'] + a.hold
        e = max(e, s + a.min_dur)
        if nxt is not None:
            if nxt - e < 0.25:                      # tiny gaps flicker: hold until the next phrase
                e = nxt
            e = min(e, nxt)
        f0, f1 = F(s), F(e)
        if f1 <= f0:
            f1 = f0 + 1
        ph.append(dict(words=p, f0=f0, f1=f1))
    for i in range(len(ph) - 1):                  # rounding can overlap by a frame
        ph[i]['f1'] = min(ph[i]['f1'], ph[i + 1]['f0'])
        if ph[i]['f1'] <= ph[i]['f0']:
            ph[i]['f1'] = ph[i]['f0'] + 1

    # ---- ASS
    name = font['name']
    fs = M.ass_size
    head = ['[Script Info]', '; generated by make_captions.py (reels-studio trending-captions), preset ' + a.preset,
            'ScriptType: v4.00+', 'PlayResX: %d' % rw, 'PlayResY: %d' % rh, 'WrapStyle: 2',
            'ScaledBorderAndShadow: yes', '', '[V4+ Styles]',
            'Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, '
            'Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, '
            'MarginL, MarginR, MarginV, Encoding']
    o_alpha = alpha_hex(1 - P.get('outline_alpha', 0.0)) if P.get('outline_alpha') else '00'
    s_alpha = alpha_hex(1 - P['shadow_alpha'])
    if P['mode'] == 'kara':                        # \kf: Secondary (unsung) -> Primary (sung)
        prim, sec = B['hl'], B['text']
    else:
        prim, sec = B['text'], B['hl']
    head.append('Style: Cap,%s,%.2f,&H00%s,&H00%s,&H%s%s,&H%s000000,0,0,0,0,100,100,0,0,1,%.2f,%.2f,5,0,0,0,1' % (
        name, fs, prim, sec, o_alpha, B['outline'], s_alpha, out_px, shad_px))
    head.append('Style: Box,%s,%.2f,&H00%s,&H00%s,&H00000000,&H00000000,0,0,0,0,100,100,0,0,1,0,0,5,0,0,0,1' % (
        name, fs, B['box'], B['box']))
    head += ['', '[Events]', 'Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text']
    ev = []

    def D(layer, f0, f1, style, text):
        if f1 > f0:
            ev.append('Dialogue: %d,%s,%s,%s,,0,0,0,,%s' % (layer, ass_time(f0, fps), ass_time(f1, fps), style, text))

    ms = lambda frames: int(round(frames * 1000.0 / fps))
    blur = '\\blur%.1f' % P['blur'] if P['blur'] else ''
    report = []
    warns = []
    box_alpha = alpha_hex(a.box_opacity)

    for pi, p in enumerate(ph):
        ws = p['words']
        disp = [w['disp'] for w in ws]
        emph = [w['emph'] for w in ws]
        lines, widths, gap, shrink = layout(disp, emph, P, M, max_w, max_lines)
        if shrink < 0.85:
            warns.append('SIZE phrase %d "%s" shrunk to %d%% to fit %.0f px: shorten it, split it or lower --size'
                         % (pi, ' '.join(disp), shrink * 100, max_w))
        elif shrink < 0.999:
            warns.append('phrase %d "%s" shrunk to %d%% to fit %.0f px' % (pi, ' '.join(disp), shrink * 100, max_w))
        f0, f1 = p['f0'], p['f1']
        Y = y_for(f0 / fps)
        lh = em * P['line_h'] * shrink
        nl = len(lines)
        exit_fade = (pi + 1 == len(ph)) or (ph[pi + 1]['f0'] - f1 >= 2)
        fo = min(110, ms(f1 - f0) // 2) if exit_fade else 0
        pos = {}                                   # word idx -> (x centre, cap-centre y, width)
        line_w = []
        for li, idx in enumerate(lines):
            W = (sum(widths[i] for i in idx) + gap * (len(idx) - 1)) * shrink
            line_w.append(W)
            x = cx - W / 2
            yc = Y + (li - (nl - 1) / 2) * lh
            for i in idx:
                wpx = widths[i] * shrink
                pos[i] = (x + wpx / 2, yc, wpx)
                x += wpx + gap * shrink
        W = max(line_w)
        cap = M.cap * shrink
        desc = 0.0 if case == 'upper' else 0.22 * em * shrink
        top_y, bot_y = Y - (nl - 1) / 2 * lh, Y + (nl - 1) / 2 * lh
        bx0, bx1 = cx - W / 2 - out_px, cx + W / 2 + out_px
        by0 = top_y - cap / 2 - out_px - 0.04 * em
        by1 = bot_y + cap / 2 + desc + out_px
        if P['mode'] == 'words' and (P['pop'] > 1 or pill):   # QA bbox at the active word's PEAK scale (+ pill)
            pk = P['pop']
            ppad = 0.56 * em * shrink if pill else 0.0
            for j in range(len(ws)):
                x, _, wpx = pos[j]
                hx = max(0.5 * wpx + out_px, 0.5 * (wpx + ppad)) * pk
                bx0, bx1 = min(bx0, x - hx), max(bx1, x + hx)
            hy = max(cap / 2 + out_px, 0.5 * (cap + ppad)) * pk
            by0 = min(by0, top_y - hy - 0.04 * em)
            by1 = max(by1, bot_y + hy + desc * pk + P['rise'] * em / 3)   # entry rise is ~1/3 left at the peak
        elif P['mode'] == 'kara':                  # emphasis words are scaled up; lines rise into place from below
            ek = P['emph_scale'] if any(emph) else 1.0
            by0 = min(by0, top_y - cap / 2 * ek - out_px - 0.04 * em)
            by1 = max(by1, bot_y + cap / 2 * ek + desc + out_px + P['rise'] * em)
        if P.get('box'):
            bw, bh = W + 2 * padx, (nl - 1) * lh + cap + 2 * pady
            byc = Y + 0.05 * em * shrink if case != 'upper' else Y     # room for descenders
            bx0, bx1, by0, by1 = cx - bw / 2, cx + bw / 2, byc - bh / 2, byc + bh / 2
            path = rrect(bw, bh, min(P['radius'] * em, bh / 2))
            fo_box = '\\fad(90,%d)' % fo
            D(0, f0, f1, 'Box', '{\\an5\\pos(%.1f,%.1f)\\bord0\\shad0\\1c&H%s&\\1a&H%s&%s\\fscx%d\\fscy%d'
              '\\t(0,140,0.6,\\fscx100\\fscy100)\\p1}%s{\\p0}' % (cx, byc, B['box'], box_alpha, fo_box,
                                                                  int(P['entry_scale'] * 100 - 2),
                                                                  int(P['entry_scale'] * 100 - 2), path))
        if P['mode'] == 'words':
            rise = P['rise'] * em
            for j, w in enumerate(ws):
                x, yc, wpx = pos[j]
                py = yc + M.box_off * shrink
                b = 100.0 * shrink * (P['emph_scale'] if w['emph'] else 1.0)
                pk, st = b * P['pop'], b * (1 + (P['pop'] - 1) * 0.35)
                a_f = max(f0, min(f1 - 1, F(w['start'] - a.lead)))
                b_f = max(a_f + 1, min(f1, F(ws[j + 1]['start'] - a.lead))) if j + 1 < len(ws) else f1
                base_c = B['emph'] if w['emph'] else B['text']
                act_c = B['pill_text'] if pill else B['hl']
                segs = [('pre', f0, a_f), ('act', a_f, b_f), ('post', b_f, f1)]
                segs = [s for s in segs if s[2] > s[1]]
                for si, (kind, s0, s1) in enumerate(segs):
                    entry = s0 == f0
                    last = si == len(segs) - 1
                    tags = ['\\an5']
                    fi = 80 if entry else 0
                    fout = fo if last else 0
                    if fi or fout:
                        tags.append('\\fad(%d,%d)' % (fi, min(fout, max(0, ms(s1 - s0) - fi))))
                    if entry and rise:
                        tags.append('\\move(%.1f,%.1f,%.1f,%.1f,0,150)' % (x, py + rise, x, py))
                    else:
                        tags.append('\\pos(%.1f,%.1f)' % (x, py))
                    c = act_c if kind == 'act' else base_c
                    tags.append('\\1c&H%s&' % c)
                    if pill and kind == 'act':
                        tags.append('\\bord0\\shad0')           # clean type on the pill
                    sc = []
                    if kind == 'act' and entry:
                        e0 = b * P['entry_scale']
                        sc = [e0, '\\t(0,100,0.7,\\fscx%.1f\\fscy%.1f)' % (pk, pk), '\\t(100,190,\\fscx%.1f\\fscy%.1f)' % (st, st)]
                    elif kind == 'act':
                        sc = [b, '\\t(0,70,0.7,\\fscx%.1f\\fscy%.1f)' % (pk, pk), '\\t(70,160,\\fscx%.1f\\fscy%.1f)' % (st, st)] \
                            if P['pop'] > 1 else [b]
                    elif entry:
                        e0 = b * P['entry_scale']
                        sc = [e0, '\\t(0,90,0.7,\\fscx%.1f\\fscy%.1f)' % (b * 1.05, b * 1.05) if P['pop'] > 1 else
                              '\\t(0,140,0.6,\\fscx%.1f\\fscy%.1f)' % (b, b),
                              '\\t(90,170,\\fscx%.1f\\fscy%.1f)' % (b, b) if P['pop'] > 1 else '']
                    else:                          # post: settle back from the active scale
                        sc = [st, '\\t(0,100,\\fscx%.1f\\fscy%.1f)' % (b, b)] if P['pop'] > 1 else [b]
                    tags.append('\\fscx%.1f\\fscy%.1f' % (sc[0], sc[0]))
                    tags += [t for t in sc[1:] if t]
                    if fout:
                        tags.append('\\t(%d,%d,\\fscx%.1f\\fscy%.1f)' % (max(0, ms(s1 - s0) - fout), ms(s1 - s0),
                                                                     b * 0.94, b * 0.94))
                    D(2, s0, s1, 'Cap', '{%s%s}%s' % (''.join(tags), blur, esc(w['disp'])))
                    if pill and kind == 'act':
                        pw, phh = wpx + 0.56 * em * shrink, cap + 0.56 * em * shrink
                        ratio = pk / b
                        ptags = '\\an5\\pos(%.1f,%.1f)\\bord0\\shad0\\1c&H%s&' % (x, yc, B['pill'])
                        if entry:
                            ptags += '\\fad(80,%d)' % (fout if last else 0)
                        elif fout and last:
                            ptags += '\\fad(0,%d)' % fout
                        s0p = P['entry_scale'] * 100 if entry else 100
                        ptags += '\\fscx%.1f\\fscy%.1f\\t(0,80,0.7,\\fscx%.1f\\fscy%.1f)\\t(80,170,\\fscx%.1f\\fscy%.1f)' % (
                            s0p, s0p, 100 * ratio, 100 * ratio, 100 * (st / b), 100 * (st / b))
                        D(1, s0, s1, 'Box', '{%s\\p1}%s{\\p0}' % (ptags, rrect(pw, phh, phh * 0.32)))
        elif P['mode'] == 'kara':
            rise = P['rise'] * em
            for li, idx in enumerate(lines):
                yc = Y + (li - (nl - 1) / 2) * lh
                py = yc + M.box_off * shrink
                b = 100.0 * shrink
                parts = ['{\\an5\\move(%.1f,%.1f,%.1f,%.1f,0,140)\\fad(80,%d)\\fscx%.1f\\fscy%.1f%s}' % (
                    cx, py + rise, cx, py, fo, b, b, blur)]
                t0 = f0 / fps
                cur = 0                            # cs from event start, kept absolute to avoid drift
                for k, i in enumerate(idx):
                    w = ws[i]
                    ws_cs = max(cur, int(round((w['start'] - a.lead - t0) * 100)))
                    we_cs = max(ws_cs + 1, int(round((w['end'] - a.lead - t0) * 100)))
                    if k == 0 and ws_cs > cur:            # line 2 waits for line 1 (empty syllable)
                        parts.append('{\\k%d}' % (ws_cs - cur))
                    sty = ''
                    if w['emph']:
                        es = b * P['emph_scale']
                        sty = '\\fscx%.1f\\fscy%.1f\\1c&H%s&' % (es, es, B['emph'])
                    parts.append('{\\kf%d%s}%s' % (we_cs - ws_cs, sty, esc(w['disp'])))
                    if w['emph']:
                        parts.append('{\\fscx%.1f\\fscy%.1f\\1c&H%s&}' % (b, b, B['hl']))
                    cur = we_cs
                    if k + 1 < len(idx):
                        nxt = ws[idx[k + 1]]
                        ns = max(cur, int(round((nxt['start'] - a.lead - t0) * 100)))
                        sp = 100.0 * gap / max(1e-6, M.adv(' '))      # widen the space like the layout
                        parts.append('{\\k%d\\fscx%.1f} {\\fscx%.1f}' % (ns - cur, b * sp / 100.0, b))
                        cur = ns
                D(2, f0, f1, 'Cap', ''.join(parts))
        else:                                       # minimal: one event per line, gentle fades
            for li, idx in enumerate(lines):
                yc = Y + (li - (nl - 1) / 2) * lh
                py = yc + M.box_off * shrink
                b = 100.0 * shrink
                txt = ' '.join(esc(ws[i]['disp']) for i in idx)
                fo_m = min(140, ms(f1 - f0) // 3) if exit_fade else 0
                D(2, f0, f1, 'Cap', '{\\an5\\pos(%.1f,%.1f)\\fad(%d,%d)\\fscx%.1f\\fscy%.1f%s}%s' % (
                    cx, py, min(120, ms(f1 - f0) // 3), fo_m, b, b, blur, txt))

        # ---- safe-zone check (reference px); the drop shadow (down-right) and blur spread are ink as well
        if not P.get('box'):
            bx0, by0 = bx0 - P['blur'], by0 - P['blur']
            bx1, by1 = bx1 + shad_px + P['blur'], by1 + shad_px + P['blur']
        r = dict(x0=bx0 / sx, x1=bx1 / sx, y0=by0 / sy, y1=by1 / sy)
        tol = 0.5                                  # px tolerance: a line fitted exactly to the limit is not a hit
        prob = []
        if r['x0'] < SAFE['x0'] - tol or r['x1'] > SAFE['x1'] + tol:
            prob.append('outside x %d-%d' % (SAFE['x0'], SAFE['x1']))
        if r['y0'] < SAFE['y0'] - tol:
            prob.append('above y %d' % SAFE['y0'])
        if r['y1'] > SAFE['floor'] + tol:
            prob.append('below y %d (bottom UI)' % SAFE['floor'])
        elif r['y1'] > SAFE['y1'] + tol:
            prob.append('below y %d (key-copy limit)' % SAFE['y1'])
        if r['y1'] > SAFE['col_y0'] and r['y0'] < SAFE['col_y1'] and r['x1'] > SAFE['col_x'] + tol:
            prob.append('enters the like/share column (x > %d at y %d-%d)' % (SAFE['col_x'], SAFE['col_y0'], SAFE['col_y1']))
        for q in prob:
            warns.append('SAFE-ZONE phrase %d at %.2fs "%s": %s (bbox x %.0f-%.0f, y %.0f-%.0f)' % (
                pi, f0 / fps, ' '.join(disp), q, r['x0'], r['x1'], r['y0'], r['y1']))
        report.append(dict(i=pi, start=round(f0 / fps, 3), end=round(f1 / fps, 3),
                           lines=[' '.join(disp[i] for i in idx) for idx in lines],
                           emph=[disp[i] for i in range(len(ws)) if emph[i]], shrink=round(shrink, 3),
                           bbox=[round(v) for v in (r['x0'], r['y0'], r['x1'], r['y1'])], safe=not prob))

    if a.guides:                                   # QA only: safe-zone lines; never deliver with these
        T = max(p['f1'] for p in ph) + 1
        g = '{\\an7\\pos(0,0)\\bord0\\shad0\\1c&H00FFFF&\\1a&H60&\\p1}%s{\\p0}'
        rect = lambda x0, y0, x1, y1: 'm %d %d l %d %d l %d %d l %d %d' % (x0, y0, x1, y0, x1, y1, x0, y1)
        lines_g = [rect(SAFE['x0'] * sx, 0, SAFE['x0'] * sx + 2, rh), rect(SAFE['x1'] * sx - 2, 0, SAFE['x1'] * sx, rh),
                   rect(0, SAFE['y0'] * sy, rw, SAFE['y0'] * sy + 2), rect(0, SAFE['y1'] * sy, rw, SAFE['y1'] * sy + 2),
                   rect(0, SAFE['floor'] * sy, rw, SAFE['floor'] * sy + 2),
                   rect(SAFE['col_x'] * sx, SAFE['col_y0'] * sy, rw, SAFE['col_y1'] * sy)]
        for gl in lines_g:
            D(9, 0, T, 'Box', g % gl)

    base = a.out
    os.makedirs(os.path.dirname(os.path.abspath(base)) or '.', exist_ok=True)
    with open(base + '.ass', 'w', encoding='utf-8') as f:
        f.write('\n'.join(head + ev) + '\n')
    write_srt(words, base + '.srt', a, ph if a.srt_mode == 'phrases' else None, fps)
    rep = dict(preset=a.preset, font=font, em_px=round(em, 1), ass_fontsize=round(fs, 2), max_line_width=round(max_w),
               centre=[round(cx), round(y_for(0))], phrases=report, warnings=warns)
    with open(base + '.captions.json', 'w') as f:
        json.dump(rep, f, indent=1)

    # ---- console report
    print('captions: %d words -> %d phrases | preset %s | font "%s" (%s) %.0f px em -> ASS Fontsize %.1f' % (
        len(words), len(ph), a.preset, name, font['path'] or 'system', em, fs))
    print('  wrote %s.ass, %s.srt, %s.captions.json' % (base, base, base))
    wide = max(report, key=lambda r: r['bbox'][2] - r['bbox'][0])
    print('  widest phrase "%s" bbox x %d-%d at %.2fs; block y %d-%d; max line width %d px' % (
        ' / '.join(wide['lines']), wide['bbox'][0], wide['bbox'][2], wide['start'],
        min(r['bbox'][1] for r in report), max(r['bbox'][3] for r in report), max_w))
    for w in warns:
        print('  ' + w)
    if not any(w.startswith('SAFE-ZONE') for w in warns):
        print('  safe zones: OK')
    low = [w for w in words if w.get('prob') is not None and w['prob'] < 0.6]
    if low:
        print('  low-confidence words (check against the script): ' +
              ', '.join('%s@%.2f' % (w['word'], w['start']) for w in low[:30]))
    if not emph_set:
        cand = {}
        for w in words:
            k = re.sub(r'[^\w]', '', w['word'].lower())
            if len(k) >= 5 and k not in STOP:
                cand[k] = cand.get(k, 0) + 1
        top = sorted(cand, key=lambda k: (-cand[k], -len(k)))[:8]
        if top:
            print('  emphasis candidates (pass the 1-3 that carry the message with --emphasis): ' + ', '.join(top))
    video = a.video or (a.input if a.input.lower().endswith(MEDIA_EXT[:6]) else 'IN.mp4')
    print_burn(video, base, font['fontsdir'])
    return 1 if (a.strict and any(w.startswith(('SAFE-ZONE', 'SIZE')) for w in warns)) else 0


def write_srt(words, path, a, ph, fps):
    """Sentence chunks (<= 2 lines x 42 chars, <= 6 s) for platform caption files; or the burned phrases."""
    blocks = []
    if ph is not None:
        for p in ph:
            blocks.append((p['f0'] / fps, p['f1'] / fps, ' '.join(w['word'] for w in p['words'])))
    else:
        cur = []
        for w in words:
            if cur:
                txt = ' '.join(x['word'] for x in cur + [w])
                if (len(txt) > 84 or w['start'] - cur[-1]['end'] > 0.8 or cur[-1]['word'][-1] in '.?!'
                        or w['end'] - cur[0]['start'] > 6.0):
                    blocks.append((cur[0]['start'], cur[-1]['end'], ' '.join(x['word'] for x in cur)))
                    cur = []
            cur.append(w)
        if cur:
            blocks.append((cur[0]['start'], cur[-1]['end'], ' '.join(x['word'] for x in cur)))
        fixed = []
        for i, (s, e, t) in enumerate(blocks):
            e2 = max(e + 0.25, s + 1.0)
            if i + 1 < len(blocks):
                e2 = min(e2, blocks[i + 1][0] - 0.001)
            fixed.append((s, max(e2, e), t))
        blocks = fixed
    with open(path, 'w', encoding='utf-8') as f:
        for i, (s, e, t) in enumerate(blocks, 1):
            f.write('%d\n%s --> %s\n%s\n\n' % (i, srt_time(s), srt_time(e), wrap2(t)))


def wrap2(t, limit=42):
    if len(t) <= limit:
        return t
    ws = t.split(' ')
    best = None
    for k in range(1, len(ws)):
        a, b = ' '.join(ws[:k]), ' '.join(ws[k:])
        sc = max(len(a), len(b)) + (8 if re.sub(r'[^\w]', '', ws[k - 1].lower()) in WEAK_END else 0)
        if max(len(a), len(b)) > limit:
            sc += 100
        if best is None or sc < best[0]:
            best = (sc, a + '\n' + b)
    return best[1]


def ff_escape(p):
    return p.replace('\\', '\\\\').replace(':', '\\:').replace("'", "\\'").replace(',', '\\,')


def print_burn(video, base, fontsdir):
    vf = 'ass=' + ff_escape(os.path.abspath(base + '.ass'))
    if fontsdir:
        vf += ':fontsdir=' + ff_escape(fontsdir)
    out = base + '_captioned.mp4'
    cmd = ['ffmpeg', '-y', '-i', video, '-vf', vf, '-c:v', 'libx264', '-preset', 'slow', '-crf', '14',
           '-profile:v', 'high', '-pix_fmt', 'yuv420p', '-color_primaries', 'bt709', '-color_trc', 'bt709',
           '-colorspace', 'bt709', '-c:a', 'copy', '-movflags', '+faststart', out]
    print('burn (CRF 14 master; then encode the deliverables from it):')
    print('  ' + ' '.join(shlex.quote(c) for c in cmd))


def probe(video):
    """(width, height, fps) of a video via ffprobe, or None."""
    try:
        r = subprocess.run(['ffprobe', '-v', 'error', '-select_streams', 'v:0', '-show_entries',
                            'stream=width,height,r_frame_rate', '-of', 'json', video],
                           capture_output=True, text=True, timeout=60)
        st = json.loads(r.stdout)['streams'][0]
        num, den = st['r_frame_rate'].split('/')
        return int(st['width']), int(st['height']), float(num) / float(den)
    except Exception:
        return None


def parse_y_at(s):
    out = []
    for part in (s or '').split(','):
        part = part.strip()
        if not part:
            continue
        m = re.fullmatch(r'([\d.]+)-([\d.]+):([\d.]+)', part)
        if not m:
            die('bad --y-at entry %r (use t0-t1:y, e.g. 0-3.5:1300,3.5-9:620)' % part)
        out.append((float(m.group(1)), float(m.group(2)), float(m.group(3))))
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('input', nargs='?', help='words JSON or a video/audio file to transcribe')
    ap.add_argument('-o', '--out', help='output base path (default: next to the input, same stem)')
    ap.add_argument('--preset', choices=sorted(PRESETS), default='bold-pop')
    ap.add_argument('--font', help='TTF/OTF path, or a font name found in --fontsdir (default: heaviest preferred '
                                   'weight in --fontsdir)')
    ap.add_argument('--fontsdir', help='folder of brand TTF/OTF files (also passed to the ffmpeg ass filter)')
    ap.add_argument('--size', type=float, help='font size in px (em, like CSS) at 1080x1920; preset default')
    ap.add_argument('--text-color', default=COLORS['text'])
    ap.add_argument('--highlight', default=COLORS['highlight'], help='active word / karaoke fill colour')
    ap.add_argument('--emph-color', help='emphasis word colour (default: --highlight)')
    ap.add_argument('--outline-color', default=COLORS['outline'])
    ap.add_argument('--box-color', default=COLORS['box'], help='boxed preset: phrase box colour')
    ap.add_argument('--box-opacity', type=float, default=0.82)
    ap.add_argument('--pill', action='store_true', help='bold-pop/boxed: rounded pill behind the active word')
    ap.add_argument('--pill-color', help='pill colour (default: --highlight)')
    ap.add_argument('--pill-text', help='active word colour on the pill (default: --text-color)')
    ap.add_argument('--case', choices=('upper', 'lower', 'as-is'))
    ap.add_argument('--max-words', type=int, help='words per phrase (1-4 recommended)')
    ap.add_argument('--lines', type=int, help='max lines per phrase (default 2)')
    ap.add_argument('--emphasis', help='comma list of keywords to emphasise (numbers are emphasised by default)')
    ap.add_argument('--no-number-emphasis', action='store_true')
    ap.add_argument('--x', type=float, help='block centre x at 1080 wide (default 540)')
    ap.add_argument('--y', type=float, help='block centre y at 1920 tall (preset default, lower-middle band)')
    ap.add_argument('--y-at', type=parse_y_at, default=[], help='per-time y, e.g. "0-3.5:1300,3.5-9:620"')
    ap.add_argument('--max-width', type=float, help='max line width px (default: from the safe zones)')
    ap.add_argument('--res', help='WxH (default: from --video, else 1080x1920)')
    ap.add_argument('--fps', type=float, help='frame rate (default: from --video, else 30)')
    ap.add_argument('--offset', type=float, default=0.0, help='shift all word times (s)')
    ap.add_argument('--lead', type=float, default=0.05, help='show words this much before they are spoken (s)')
    ap.add_argument('--hold', type=float, default=0.35, help='keep a phrase after its last word (s)')
    ap.add_argument('--min-dur', type=float, default=0.4)
    ap.add_argument('--gap', type=float, default=0.45, help='pause (s) that forces a new phrase')
    ap.add_argument('--srt-mode', choices=('sentences', 'phrases'), default='sentences')
    ap.add_argument('--guides', action='store_true', help='QA only: draw safe-zone lines into the ASS')
    ap.add_argument('--strict', action='store_true', help='exit 1 on a safe-zone violation or a phrase shrunk below 85%%')
    ap.add_argument('--video', help='video path for the printed burn command')
    ap.add_argument('--model', default='small', help='faster-whisper model (small, medium, large-v3, ...)')
    ap.add_argument('--device', default='auto', help='faster-whisper device: auto, cuda, cpu')
    ap.add_argument('--compute-type', default='auto', help='faster-whisper compute type (auto, int8, float16)')
    ap.add_argument('--language', help='spoken language code (e.g. en); default: detect')
    ap.add_argument('--prompt', help='transcription hint: brand names, product terms, spellings')
    ap.add_argument('--sample', metavar='JSON', help='write a demo word-timing JSON and exit')
    a = ap.parse_args()
    if a.sample:
        write_sample(a.sample)
        return 0
    if not a.input:
        ap.error('input (words JSON or media file) is required')
    if not os.path.exists(a.input):
        die('no such file: %s' % a.input)
    stem = os.path.splitext(a.input)[0]
    a.out = os.path.splitext(a.out)[0] if a.out else stem
    if a.input.lower().endswith('.json'):
        a.input_json = a.input
    elif a.input.lower().endswith(MEDIA_EXT):
        a.input_json = transcribe(a.input, a, a.out + '.words.json')
        if a.video is None and a.input.lower().endswith(MEDIA_EXT[:6]):
            a.video = a.input
    else:
        die('input must be a .json word list or a media file (%s)' % ' '.join(MEDIA_EXT))
    info = probe(a.video) if (a.video and os.path.exists(a.video)) else None
    if info:
        if a.res is None:
            a.res = '%dx%d' % info[:2]
        if a.fps is None:
            a.fps = round(info[2], 3)
        if abs(info[0] / info[1] - 9 / 16) > 0.01:
            print('note: %s is %dx%d, not 9:16; safe zones are scaled from 1080x1920' % ((a.video,) + info[:2]))
    a.res = a.res or '1080x1920'
    a.fps = a.fps or 30.0
    return build(a)


if __name__ == '__main__':
    sys.exit(main())
