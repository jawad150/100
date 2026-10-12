#!/usr/bin/env python3
"""sirf_36_shots_vo.py - Bijli series #3 "Sirf 36 Shots" VO: the paid Vlad (Higgsfield elevenlabs_v4) takes ->
processed lines (vo_chain) -> the VO stem on the reel grid (hook A + hook B) + reel-time word timings + VO_TIMING.md.

Sources (binding): brand_reels/design/reels/sirf_36_shots/script.json (lines[].vo: Roman / DEV per caption line,
hooks[B].lines[].vo, outro.vo), SCRIPT.md section 3 (VO windows), SHOTS.md (picture events), LEAD_DECISIONS 3 (the
measured takes are final; picture beats move to the VO). vo_chain.py is imported read-only (decode, voiced runs, pause
edit, rubberband stretch, HPF 70 Hz / de-ess / 2.5:1 comp / loudnorm -16 LUFS -2 dBTP, faster-whisper word timings +
DP alignment + snap). Same conventions as thoda_left_bas_vo.py / pencil_se_rewind_vo.py / bijli_chali_gayi_vo.py.

Takes (never regenerated, never a paid call): brand_reels/assets/sirf_36_shots/vo_raw/<FILE>_t<N>.mp3. A take is a
UNIT; combined takes hold several caption lines (C07C08 = C7 + C8, C11C13 = C11 + C12 + C13, C14C15 = C14 + C15,
HB = HB1 + HB2). Each unit is processed as one take, then cut in the middle of the silence between its lines into
PARTS (one per caption line), so every line lands on its own picture beat. Where a _t2 exists (C14C15) the take with
the lower mean CER (faster-whisper small + medium, no prompt, on the processed take, against the DEV text; best of the
two) wins; ties (< 0.02) -> the shorter span. faster-whisper always gets a 16 kHz float32 numpy array decoded by ffmpeg
(its PyAV decoder is incompatible here).

P (the client's line, payoff) gets a light voice-note colour (HP 220 Hz / LP 6.2 kHz, loudness-matched) as SCRIPT 4
asks ("a voice-note filter on the same voice"); "Bhai..." sits inside the drop-out, "ek" lands just after the f810 hit.
Hook B (Trial Reel): HB ("Hilna mat! Aankh mat jhapkana.") replaces C1 + C2; identical to A from C3 on.

    cd pipeline/jawad_reels
    tools/heavy.sh python3 sirf_36_shots_vo.py process     # every take at every speed in SPEEDS (cached)
    tools/heavy.sh python3 sirf_36_shots_vo.py assemble    # pick, place (PLAN), stems, words, VO_TIMING.md, vo_final
    options: --force (re-run vo_chain), --no-final (skip the brand_reels/assets copies)

Outputs (<RW> = workspace/jawad_reels/sirf_36_shots/vo): proc/<take>_<speed>_c<cap>.wav (+ vo_chain .words.json /
.report.json), takes.json (CER per take), placement.json, vo_stem.wav (hook A) / vo_stem_B.wav (1,728,000 samples =
36.000 s, 48 kHz 24-bit mono, -16 LUFS integrated, TP <= -2 dBTP), words.json / words_B.json (reel time, snake_captions
format + line / i / dev / heard / ok / start_f / end_f), timeline.png; copies brand_reels/assets/sirf_36_shots/vo_final/
(FLAC + json); the tables go to brand_reels/design/reels/sirf_36_shots/VO_TIMING.md.
"""
import argparse
import glob
import json
import math
import os
import re
import shutil
import subprocess
import sys
import unicodedata

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import vo_chain as V  # noqa: E402  (read-only shared module)

REPO = os.path.abspath(os.path.join(HERE, '..', '..'))
SLUG = 'sirf_36_shots'
RW = os.path.join(REPO, 'workspace', 'jawad_reels', SLUG, 'vo')
RAW = os.path.join(REPO, 'brand_reels', 'assets', SLUG, 'vo_raw')
FINAL = os.path.join(REPO, 'brand_reels', 'assets', SLUG, 'vo_final')
DESIGN = os.path.join(REPO, 'brand_reels', 'design', 'reels', SLUG)
SCRIPT_JSON = os.path.join(DESIGN, 'script.json')
MD = os.path.join(DESIGN, 'VO_TIMING.md')
SR, FPS, NF = 48000, 30, 1080          # 36.000 s = 18 bars at 120 BPM (the easter egg stays)
DUR = NF / FPS
NSAMP = NF * SR // FPS                 # 1,728,000
LUFS, TP_MAX = -16.0, -2.0
GAP_MIN = 0.12                         # minimum silence between two lines (Bijli ladder F2)
SPEEDS = (1.06, 1.08, 1.10)            # vo_config: 1.06-1.10x for reels; the gentlest speed that fits wins
VOICE_DBFS = -55.0                     # absolute voiced threshold for mastered lines (Bijli convention)

# unit (one take file) -> caption lines it holds, in order
UNITS = {'C1': ('C01', ['C1']), 'C2': ('C02', ['C2']), 'C3': ('C03', ['C3']), 'C4': ('C04', ['C4']),
         'C6': ('C06', ['C6']), 'C7C8': ('C07C08', ['C7', 'C8']), 'C9': ('C09', ['C9']), 'C10': ('C10', ['C10']),
         'C11C13': ('C11C13', ['C11', 'C12', 'C13']), 'C14C15': ('C14C15', ['C14', 'C15']), 'P': ('P', ['P']),
         'C16': ('C16', ['C16']), 'Q': ('Q', ['Q']), 'HB': ('HB', ['HB1', 'HB2'])}
UNIT_OF = {s: u for u, (_, subs) in UNITS.items() for s in subs}
# parts placed as ONE piece (HB: hook B is a single breath; it is a bonus version)
JOINED = {'HB': ['HB1', 'HB2']}
ORDER_A = ['C1', 'C2', 'C3', 'C4', 'C6', 'C7', 'C8', 'C9', 'C10', 'C11', 'C12', 'C13', 'C14', 'C15', 'P', 'C16', 'Q']
ORDER_B = ['HB'] + ORDER_A[2:]
# keyword token (Roman, lower, no punctuation) per line: the lockup's jw_key word as spoken
KEYWORD = {'C1': 'ek', 'C2': 'ready', 'C3': 'click', 'C4': 'studio', 'C6': 'intezaar', 'C7': 'aankhein', 'C8': 'thumb',
           'C9': 'sambhaali', 'C10': 'aaj', 'C11': 'tb', 'C12': 'chaar', 'C13': 'hazaar', 'C14': 'dekha', 'C15': 'full',
           'P': 'nahi', 'C16': 'chhattees', 'Q': 'camera', 'HB1': 'mat', 'HB2': 'jhapkana'}
# pause caps (cap, keep_cap) per unit; default vo_chain-ish 0.45 / 0.60. Splits re-space the lines anyway.
CAPS = {'C1': (0.25, 0.30), 'C2': (0.20, 0.25), 'C9': (0.30, 0.35), 'P': (0.45, 0.55), 'HB': (0.30, 0.35)}
CAP_DEFAULT = (0.45, 0.60)
KEEP_AFTER = {}
LOAN = {'ready': 'रेडी', 'click': 'क्लिक', 'roll': 'रोल', 'studio': 'स्टूडियो', 'photo': 'फ़ोटो', 'thumb': 'थंब',
        'tb': 'टीबी', 'footage': 'फ़ुटेज', 'camera': 'कैमरा', 'takes': 'टेक्स', 'take': 'टेक', 'disk': 'डिस्क',
        'full': 'फ़ुल', 'shot': 'शॉट'}
VOICE_NOTE = {'P': dict(hp=220.0, lp=6200.0)}  # the client's voice note (loudness-matched)

# ------------------------------------------------------------------------------------------------ picture frames
# The VO-led grid (frames, 1080-f reel). Hook: C1 (1.99 s even at 1.10x) + C2 (1.12 s) need 3.25 s, so the FLASH POP
# moves from f60 to f100 (the shot fires right after "jao!"; the music answers with a stinger, kit on bar 2 f120);
# S2 is f100-f165, the C1 whip moves f150 -> f166 (after C3 "tha.").
# The rest stays on the SHOTS grid: the measured lines fit their shots (VO_TIMING.md section 3 lists every move).
FLASH_F = 100
WHIP_F = 167

# ------------------------------------------------------------------------------------------------ placement plan
# per PART: t = reel time (s) of the part's FIRST voiced onset, or anchor=(token index, frame): that word's onset on the
# frame; t=None = as early as possible after the previous part (+ GAP_MIN). lo / hi = hard limits for the voice
# (start >= lo, end <= hi). why = the picture reason.
PLAN = {
    'C1':  dict(t=1 / FPS, lo=0.03, hi=61.5 / FPS, why='hook: "Sirf ek photo bachi hai." over the ticking counter (C1 mid-rise f0)'),
    'C2':  dict(t=None, lo=None, hi=(FLASH_F - 1) / FPS, why='"Sab ready ho jao!" (C2), ends before the FLASH POP f%d' % FLASH_F),
    'C3':  dict(t=(FLASH_F + 4) / FPS, lo=(FLASH_F + 4) / FPS, hi=(WHIP_F - 2) / FPS,
                why='S2 flash: "Har click ginti mein hota tha." after the pop (C3), ends before the C1 whip f%d' % WHIP_F),
    'C4':  dict(t=(WHIP_F + 3) / FPS, lo=(WHIP_F + 3) / FPS, hi=227 / FPS, why='S3 canister: "Phir roll studio jaata tha..." (C4) after the whip, ends by the fall (f225 -> f228)'),
    'C6':  dict(t=245 / FPS, lo=241 / FPS, hi=298 / FPS, why='S4 counter: "Teen din ka intezaar." (C6) over DIN 1/2/3, ends before the C6 rack f300'),
    'C7':  dict(t=301 / FPS, lo=299 / FPS, hi=None, why='S5 prints: "Aadhi mein aankhein band," (C7) from the C6 rack f300, "aankhein" on the P2 eyes-shut print; leaves C8 room to put "thumb" on f375'),
    'C8':  dict(anchor=(2, 375), lo=None, hi=None, why='"aadhi mein thumb." with "thumb" on the thumb-print SLAP f375 (music stop)'),
    'C9':  dict(t=405 / FPS, lo=(375 + 21) / FPS, hi=478 / FPS, why='S6 album: "Phir bhi har photo sambhaali." (C9) on the album cut (f420 -> f405, a beat after "thumb."), ends before the re-hook f480'),
    'C10': dict(t=486 / FPS, lo=482 / FPS, hi=536 / FPS, why='RE-HOOK: "Aur aaj?" (C10) after the f480 snap'),
    'C11': dict(anchor=(0, 541), lo=None, hi=None, why='"Do TB footage," on the 2 TB slam (C11)'),
    'C12': dict(t=None, lo=None, hi=None, why='"chaar camera," on the 4 CAMERAS slam (C12; slam frame = the onset)'),
    'C13': dict(t=None, lo=None, hi=668 / FPS, why='"teen hazaar takes." on the 3,000 TAKES slam (C13; slam = the onset)'),
    'C14': dict(t=676 / FPS, lo=None, hi=None, why='S8 bin: "Har take dekha..." (C14)'),
    'C15': dict(t=736 / FPS, lo=None, hi=774 / FPS, why='"disk full." on the DISK FULL error f735 (C15), ends before the freeze'),
    'P':   dict(anchor=(1, 818), lo=782 / FPS, hi=895 / FPS,
                why='PAYOFF (client voice note): the drawn-out "Bhaaai..." fills the drop-out, "ek" 8 f after the f810 hit (the hit owns 0.27 s)'),
    'C16': dict(t=907 / FPS, lo=902 / FPS, hi=960 / FPS, why='S10 closer: "Tab chhattees kaafi the." after the C3 portal (C16), ends by the outro f960'),
    'Q':   dict(t=1000 / FPS, lo=None, hi=1074 / FPS, why='outro question (profile outro from f960, question lands f999), ends <= f1074'),
    'HB':  dict(t=1 / FPS, lo=0.03, hi=(FLASH_F - 1) / FPS, why='hook B: "Hilna mat! Aankh mat jhapkana." before the flash'),
}


# ------------------------------------------------------------------------------------------------ script
def _clean(s):
    return re.sub(r'[^\w]', '', s.lower())


def load_lines():
    """{line id: dict(dev=[tokens], rom=[tokens, '*' on the keyword], roman, dev_text, f_in, f_out, vo_f)}."""
    d = json.load(open(SCRIPT_JSON, encoding='utf8'))
    src = [(L['id'], L['vo']['roman'], L['vo']['dev'], L['f_in'], L['f_out'], (L['vo']['f_in'], L['vo']['f_out']))
           for L in d['lines']]
    for L in d['hooks'][1]['lines']:
        src.append((L['id'], L['vo']['roman'], L['vo']['dev'], L['f_in'], L['f_out'], (L['f_in'], L['f_out'])))
    o = d['outro']
    src.append(('Q', o['vo']['roman'], o['vo']['dev'], 999, 1065, (o['vo']['f_in'], o['vo']['f_out'])))
    out = {}
    for lid, roman, dev_text, fi, fo, vf in src:
        roman = re.sub(r'^\([^)]*\)\s*', '', roman)      # P: "(client, a second voice) Bhai..."
        dev, rom = V.tokens(dev_text), V.tokens(roman)
        if len(dev) != len(rom):
            raise ValueError('%s: DEV %d vs ROM %d tokens' % (lid, len(dev), len(rom)))
        kw = KEYWORD[lid]
        hits = [i for i, r in enumerate(rom) if _clean(r) == kw]
        if not hits:
            raise ValueError('%s: keyword %r not in %r' % (lid, kw, rom))
        rom = [('*' + r) if i == hits[0] else r for i, r in enumerate(rom)]
        out[lid] = dict(dev=dev, rom=rom, roman=roman, dev_text=dev_text, f_in=fi, f_out=fo, vo_f=vf)
    return out


def unit_text(lines, uid):
    subs = UNITS[uid][1]
    dev = sum((lines[s]['dev'] for s in subs), [])
    rom = sum((lines[s]['rom'] for s in subs), [])
    return dev, rom, ' '.join(lines[s]['dev_text'] for s in subs)


# ------------------------------------------------------------------------------------------------ measures
def norm_cer(s):
    s = unicodedata.normalize('NFD', s.lower())
    s = ''.join(V.NUKTA.get(ch, ch) for ch in s)
    s = unicodedata.normalize('NFC', s).replace('़', '').replace('ँ', 'ं')
    s = re.sub(r'[‌‍]', '', s)
    # keep the vowel signs (Mn / Mc): Python's \w drops them, which would compare consonant skeletons only
    return ''.join(ch for ch in s if unicodedata.category(ch)[0] in 'LMN')


def lev(a, b):
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        cur = [i]
        for j, cb in enumerate(b, 1):
            cur.append(min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + (ca != cb)))
        prev = cur
    return prev[-1]


def cer(hyp, ref):
    hyp = re.sub(r'[A-Za-z]+', lambda m: LOAN.get(m.group(0).lower(), m.group(0)), hyp)
    hyp = re.sub(r'\b36\b', 'छत्तीस', hyp)
    ref = ref.replace('टी-बी', 'टीबी')
    r = norm_cer(ref)
    return lev(norm_cer(hyp), r) / max(1, len(r))


_WM = {}


def whisper_text(x48, model='small'):
    """Free transcript (no prompt) of a 48 kHz float array: faster-whisper int8 on a 16 kHz numpy array."""
    from faster_whisper import WhisperModel
    from scipy.signal import resample_poly
    if model not in _WM:
        mp = os.path.join(V.WHISPER, 'faster-whisper-%s' % model)
        _WM[model] = WhisperModel(mp if os.path.isdir(mp) else model, device='cpu', compute_type='int8',
                                  cpu_threads=V.THREADS)
    x16 = resample_poly(np.asarray(x48, np.float64), 1, 3).astype(np.float32)
    segs, _ = _WM[model].transcribe(x16, language='hi', beam_size=5, condition_on_previous_text=False,
                                    vad_filter=False)
    return ' '.join(s.text.strip() for s in segs).strip()


def runs_abs(x, thr_db=VOICE_DBFS, win=0.02, hop=0.01, close=0.08, min_run=0.03):
    """[(t0, t1)] runs above an absolute 20 ms RMS level (same windows / gap closing as vo_chain.voiced_runs)."""
    n, h = int(win * SR), int(hop * SR)
    x = np.asarray(x, np.float32)
    if len(x) < n:
        return []
    fr_ = np.lib.stride_tricks.sliding_window_view(x, n)[::h]
    v = 10 * np.log10(np.mean(fr_.astype(np.float64) ** 2, axis=1) + 1e-12) > thr_db
    runs, i = [], 0
    while i < len(v):
        if v[i]:
            j = i
            while j < len(v) and v[j]:
                j += 1
            runs.append([i * hop, (j - 1) * hop + win])
            i = j
        else:
            i += 1
    merged = []
    for r in runs:
        if merged and r[0] - merged[-1][1] < close:
            merged[-1][1] = r[1]
        else:
            merged.append(r)
    return [(round(a, 3), round(b, 3)) for a, b in merged if b - a >= min_run]


# ------------------------------------------------------------------------------------------------ process
def takes(uid):
    return sorted(glob.glob(os.path.join(RAW, '%s_t*.mp3' % UNITS[uid][0])))


def caps(uid):
    return CAPS.get(uid, CAP_DEFAULT)


def proc_path(uid, take, speed):
    c, k = caps(uid)
    return os.path.join(RW, 'proc', '%s_%.2f_c%02d%02d.wav' % (os.path.splitext(os.path.basename(take))[0], speed,
                                                               round(c * 100), round(k * 100)))


def run_chain(lines, uid, take, speed, force=False):
    out = proc_path(uid, take, speed)
    if force or not os.path.exists(os.path.splitext(out)[0] + '.report.json'):
        dev, rom, _ = unit_text(lines, uid)
        c, k = caps(uid)
        V.process(take, dev, rom, out=out, speed=speed, keep_after=KEEP_AFTER.get(uid, ()), cap=c, keep_cap=k)
    rep = json.load(open(os.path.splitext(out)[0] + '.report.json', encoding='utf8'))
    words = json.load(open(os.path.splitext(out)[0] + '.words.json', encoding='utf8'))
    x = V.decode(out)
    return x, words, rep


def tab_key(uid, take, sp):
    c, k = caps(uid)
    return '%s@%.2f/c%.2f-%.2f' % (os.path.basename(take), sp, c, k)


def cmd_process(force=False):
    lines = load_lines()
    os.makedirs(os.path.join(RW, 'proc'), exist_ok=True)
    tp = os.path.join(RW, 'takes.json')
    tab = json.load(open(tp, encoding='utf8')) if os.path.exists(tp) and not force else {}
    for uid in UNITS:
        ref = unit_text(lines, uid)[2]
        for take in takes(uid):
            for sp in SPEEDS:
                key = tab_key(uid, take, sp)
                x, words, rep = run_chain(lines, uid, take, sp, force)
                r = runs_abs(x)
                if key not in tab:
                    heard = whisper_text(x)
                    hm = whisper_text(x, 'medium')
                    tab[key] = dict(unit=uid, take=os.path.basename(take), speed=sp, caps=list(caps(uid)),
                                    heard=heard, cer_small=round(cer(heard, ref), 3),
                                    heard_medium=hm, cer_medium=round(cer(hm, ref), 3))
                tab[key]['cer'] = min(tab[key]['cer_small'], tab[key]['cer_medium'])      # CER best (Bijli)
                tab[key].update(span=round(r[-1][1] - r[0][0], 3) if r else None, dur=round(len(x) / SR, 3),
                                matched='%d/%d' % (rep['matched'], rep['tokens']), pauses=rep['pauses'],
                                lufs=rep['loudness']['lufs'], tp=rep['loudness']['tp'])
                print(key, tab[key]['span'], tab[key]['cer_small'], tab[key]['cer_medium'], tab[key]['heard'], '|',
                      tab[key]['heard_medium'], flush=True)
                json.dump(tab, open(tp, 'w', encoding='utf8'), ensure_ascii=False, indent=1)
    return tab


def rescore(tab, lines):
    """Recompute the CERs from the cached transcripts (the scorer may change; whisper is not re-run)."""
    for k, r in tab.items():
        ref = unit_text(lines, r['unit'])[2]
        r['cer_small'] = round(cer(r['heard'], ref), 3)
        r['cer_medium'] = round(cer(r['heard_medium'], ref), 3)
        r['cer'] = min(r['cer_small'], r['cer_medium'])
    return tab


def rows_of(tab, uid):
    out = {}
    for take in takes(uid):
        for sp in SPEEDS:
            k = tab_key(uid, take, sp)
            if k in tab:
                out.setdefault(os.path.basename(take), []).append(tab[k])
    return out


def pick(tab, uid):
    """The take of a unit: lowest mean CER over the processed speeds; tie (< 0.02) -> the shorter span at 1.08x."""
    rows = rows_of(tab, uid)
    score = {t: (float(np.mean([r['cer'] for r in rs])), [r['span'] for r in rs if abs(r['speed'] - 1.08) < 1e-6][0])
             for t, rs in rows.items()}
    best = min(s[0] for s in score.values())
    cands = [t for t, s in score.items() if s[0] <= best + 0.02]
    return min(cands, key=lambda t: score[t][1]), score


# ------------------------------------------------------------------------------------------------ parts
def split_parts(lines, uid, x, words):
    """Processed unit -> {part id: dict(x, words (part-local), s0, s1)}. Cuts sit in the middle of the silence between
    two lines (voiced runs at the absolute threshold); 8 ms raised-cosine edges (the cut is in silence)."""
    subs = UNITS[uid][1]
    groups = [[s] for s in subs] if uid not in JOINED else [JOINED[uid]]
    r = runs_abs(x)
    n_tok = [sum(len(lines[s]['dev']) for s in g) for g in groups]
    bounds = [0]
    k = 0
    for gi in range(1, len(groups)):
        k += n_tok[gi - 1]
        ws = words[k]['start']
        j = int(np.argmin([abs(a - ws) for a, _ in r]))
        cut = 0.5 * (r[j - 1][1] + r[j][0]) if j > 0 else ws - 0.06
        bounds.append(int(round(cut * SR)))
    bounds.append(len(x))
    out = {}
    k = 0
    fade = int(0.008 * SR)
    for gi, g in enumerate(groups):
        a, b = bounds[gi], bounds[gi + 1]
        seg = np.array(x[a:b], dtype=np.float32)
        if gi > 0:
            seg[:fade] *= (0.5 - 0.5 * np.cos(np.pi * np.arange(fade) / fade)).astype(np.float32)
        if gi < len(groups) - 1:
            seg[-fade:] *= (0.5 + 0.5 * np.cos(np.pi * np.arange(fade) / fade)).astype(np.float32)
        pid = 'HB' if uid in JOINED else g[0]
        ws = []
        for s in g:
            for i in range(len(lines[s]['dev'])):
                w = dict(words[k])
                w['start'] = round(w['start'] - a / SR, 3)
                w['end'] = round(w['end'] - a / SR, 3)
                w['line'], w['i'] = s, i
                ws.append(w)
                k += 1
        rr = runs_abs(seg)
        r45 = runs_abs(seg, -45.0)
        for q in range(1, len(ws)):                  # clause start: the word after , . ? ! ... starts on the next voiced
            w, pw = ws[q], ws[q - 1]                 # onset inside its span (vo_chain snaps only within 0.35 s)
            if not re.search(r'([,.?!\u0964\u2026;:]|\.\.\.)$', pw['word']):
                continue
            ons = [r_ for r_ in r45 if w['start'] + 0.02 < r_[0] < w['end'] - 0.08]
            if ons:
                prev_end = max([r_[1] for r_ in r45 if r_[1] <= ons[0][0]] or [pw['end']])
                w['start'], w['snap'] = round(ons[0][0], 3), 'clause onset (long)'
                pw['end'] = round(min(pw['end'], prev_end) if prev_end > pw['start'] else pw['end'], 3)
        for w in ws:                                 # a word ends with its voiced run (a dramatic pause is not the word)
            inside = [r_ for r_ in rr if r_[0] < w['end'] - 0.02 and r_[1] > w['start']]
            if inside and inside[-1][1] < w['end']:
                w['end'] = round(max(inside[-1][1], w['start'] + 0.05), 3)
        out[pid] = dict(x=seg, words=ws, s0=rr[0][0], s1=rr[-1][1])
    return out


LINE_LEVEL = -16.3       # speech loudness (K-weighted over the voiced span) every line is ridden to (median of the takes)
LINE_RIDE_MAX = 6.0      # dB cap of that ride


def speech_lufs(seg, s0, s1):
    from scipy import signal
    x = np.asarray(seg[int(s0 * SR):int(s1 * SR)], np.float64)
    sh = signal.lfilter(*_kw_shelf(), x)
    k = signal.lfilter(*_kw_hp(), sh)
    return float(-0.691 + 10 * np.log10(np.mean(k ** 2) + 1e-20))


def _kw_shelf():
    import math as m
    f0, G, Q = 1681.974450955533, 3.999843853973347, 0.7071752369554196
    K = m.tan(m.pi * f0 / SR); Vh = 10 ** (G / 20); Vb = Vh ** 0.4996667741545416
    a0 = 1 + K / Q + K * K
    return ([(Vh + Vb * K / Q + K * K) / a0, 2 * (K * K - Vh) / a0, (Vh - Vb * K / Q + K * K) / a0],
            [1.0, 2 * (K * K - 1) / a0, (1 - K / Q + K * K) / a0])


def _kw_hp():
    import math as m
    f0, Q = 38.13547087602444, 0.5003270373238773
    K = m.tan(m.pi * f0 / SR)
    a0 = 1 + K / Q + K * K
    return ([1.0, -2.0, 1.0], [1.0, 2 * (K * K - 1) / a0, (1 - K / Q + K * K) / a0])


def level_line(seg, s0, s1):
    """Ride a line to LINE_LEVEL (speech loudness), capped at +-LINE_RIDE_MAX dB. -> (seg, gain dB)."""
    g = float(np.clip(LINE_LEVEL - speech_lufs(seg, s0, s1), -LINE_RIDE_MAX, LINE_RIDE_MAX))
    return (np.asarray(seg, np.float32) * np.float32(10 ** (g / 20))), round(g, 2)


def voice_note(seg, lid):
    """P: the client's voice-note colour, loudness-matched to the dry part (K-weighted)."""
    from scipy import signal
    p = VOICE_NOTE[lid]
    y = signal.sosfiltfilt(signal.butter(2, p['hp'], 'highpass', fs=SR, output='sos'), seg.astype(np.float64))
    y = signal.sosfiltfilt(signal.butter(2, p['lp'], 'lowpass', fs=SR, output='sos'), y)
    a, b = lufs_tp(seg)['lufs'], lufs_tp(y.astype(np.float32))['lufs']
    return (y * 10 ** ((a - b) / 20)).astype(np.float32)


# ------------------------------------------------------------------------------------------------ stems
def lufs_tp(x):
    p = os.path.join(RW, '_meas_%d.wav' % os.getpid())
    V.write_wav(p, x)
    try:
        return V.ebur128(p)
    finally:
        os.remove(p)


def limit(x, ceiling_db):
    p = subprocess.run(['ffmpeg', '-hide_banner', '-loglevel', 'error', '-f', 'f32le', '-ar', str(SR), '-ac', '1',
                        '-i', '-', '-af', 'alimiter=limit=%.5f:attack=3:release=50:level=false:latency=true'
                        % (10 ** (ceiling_db / 20)), '-f', 'f32le', '-ac', '1', '-'],
                       input=np.asarray(x, np.float32).tobytes(), capture_output=True, check=True)
    y = np.frombuffer(p.stdout, np.float32).copy()
    return np.pad(y, (0, max(0, len(x) - len(y))))[:len(x)]


def master(y, path):
    """Linear gain to -16 LUFS integrated; a limiter only if the true peak would pass -2 dBTP. 48 kHz 24-bit."""
    pk = float(np.max(np.abs(y))) + 1e-12
    if pk > 0.5:                                         # the measurement wav is 24-bit: keep it from clipping
        y = y * np.float32(0.5 / pk)
    m = lufs_tp(y)
    g = LUFS - m['lufs']
    z = y * np.float32(10 ** (g / 20))
    info = dict(pre=m, gain_db=round(g, 2), limiter=False)
    if m['tp'] + g > TP_MAX - 0.2:
        z = limit(z, TP_MAX - 0.4)
        info['limiter'] = True
        z = z * np.float32(10 ** ((LUFS - lufs_tp(z)['lufs']) / 20))
        for k in range(4):
            m2 = lufs_tp(z)
            if m2['tp'] <= TP_MAX - 0.1:
                break
            z = limit(z, TP_MAX - 0.6 - 0.2 * k)
            z = z * np.float32(10 ** ((LUFS - lufs_tp(z)['lufs']) / 20))
    V.write_wav(path, z)
    info['post'] = V.ebur128(path)
    return z, info


def fr(t):
    return round(t * FPS, 1)


def _plan_t(pid):
    P = PLAN[pid]
    if P.get('t') is not None:
        return P['t']
    if 'anchor' in P:
        return P['anchor'][1] / FPS
    return P.get('lo')


def cmd_assemble(final=True):
    lines = load_lines()
    tab = rescore(json.load(open(os.path.join(RW, 'takes.json'), encoding='utf8')), lines)
    json.dump(tab, open(os.path.join(RW, 'takes.json'), 'w', encoding='utf8'), ensure_ascii=False, indent=1)
    chosen, scores, notes = {}, {}, []
    for uid in UNITS:
        chosen[uid], scores[uid] = pick(tab, uid)
    placed = {}

    def desired(pid, part, prev_end):
        P = PLAN[pid]
        if 'anchor' in P:
            i, f = P['anchor']
            return f / FPS - (part['words'][i]['start'] - part['s0'])
        if P.get('t') is not None:
            return P['t']
        return prev_end + GAP_MIN

    def place_unit(uid, prev_end, order):
        pids = [p for p in order if UNIT_OF.get(p, p) == uid or (uid in JOINED and p == uid)]
        best = None
        for sp in SPEEDS:                                    # the gentlest speed that fits every part's slot
            x, words, rep = run_chain(lines, uid, os.path.join(RAW, chosen[uid]), sp)
            parts = split_parts(lines, uid, x, words)
            pe, res, fits = prev_end, {}, True
            for pid in pids:
                P, pt = PLAN[pid], parts[pid]
                if pid in VOICE_NOTE:
                    pt['x'] = voice_note(pt['x'], pid)
                pt['x'], pt['level_db'] = level_line(pt['x'], pt['s0'], pt['s1'])
                idx = order.index(pid)
                nxt = order[idx + 1] if idx + 1 < len(order) else None
                nxt_t = _plan_t(nxt) if nxt else None
                if nxt and 'anchor' in PLAN[nxt]:
                    nxt_t = None                             # anchored next part: its own lo / gap rule decides
                limit_end = min(P['hi'] or 1e9, (nxt_t - GAP_MIN) if nxt_t else DUR - 0.04)
                t0 = max(desired(pid, pt, pe), pe + GAP_MIN if pe else 0.0, P['lo'] or 0.0)
                b = dict(speed=sp, rep=rep, unit=uid, t0=t0, t1=t0 + pt['s1'] - pt['s0'], limit_end=limit_end, **pt)
                if b['t1'] > limit_end + 1e-6:
                    fits = False
                res[pid] = b
                pe = b['t1']
            best = res
            if fits:
                break
        return best

    def place(order, fixed):
        out, prev_end, done = dict(fixed), 0.0, set()
        for pid in order:
            uid = pid if pid in JOINED else UNIT_OF[pid]
            if pid in out:
                prev_end = out[pid]['t1']
                continue
            if uid in done:
                continue
            res = place_unit(uid, prev_end, order)
            for k, b in res.items():
                P = PLAN[k]
                if P['hi'] and b['t1'] > P['hi'] + 1e-6:        # hard end: pull the start earlier (never < prev+gap)
                    need = b['t1'] - P['hi']
                    pe = prev_end if k == min(res, key=lambda q: order.index(q)) else out[order[order.index(k) - 1]]['t1']
                    room = b['t0'] - max(pe + GAP_MIN if pe else 0.04, P['lo'] or 0.0)
                    sh = min(need, max(0.0, room))
                    b['t0'] -= sh
                    b['t1'] -= sh
                    notes.append('%s: start pulled %.3f s earlier to end by its hard limit %.3f s (f%.1f)'
                                 % (k, sh, P['hi'], fr(P['hi'])))
                    if b['t1'] > P['hi'] + 1e-6:
                        notes.append('WARNING %s: ends %.3f s after its hard limit' % (k, b['t1'] - P['hi']))
                elif b['t1'] > b['limit_end'] + 1e-6:
                    notes.append('%s: runs %.3f s past its slot (next planned start - gap)' % (k, b['t1'] - b['limit_end']))
                out[k] = b
                prev_end = b['t1']
            done.add(uid)
        return out

    placed = place(ORDER_A, {})
    placed_b = place(ORDER_B, {k: v for k, v in placed.items() if k in ORDER_B[1:]})
    placed['HB'] = placed_b['HB']
    stems = {}
    for ver, order in (('A', ORDER_A), ('B', ORDER_B)):
        y = np.zeros(NSAMP, np.float32)
        words = []
        for pid in order:
            b = placed[pid]
            off = b['t0'] - b['s0']
            i0 = int(round(off * SR))
            seg = b['x'][max(0, -i0):][:NSAMP - max(i0, 0)]
            y[max(i0, 0):max(i0, 0) + len(seg)] += seg
            for w in b['words']:
                words.append(dict(word=w['word'], start=round(w['start'] + off, 3), end=round(w['end'] + off, 3),
                                  keyword=bool(w['keyword']), line=w['line'], i=w['i'], dev=w.get('dev'),
                                  heard=w.get('heard'), ok=w.get('ok'), start_f=fr(w['start'] + off),
                                  end_f=fr(w['end'] + off)))
        words.sort(key=lambda w: w['start'])
        os.makedirs(RW, exist_ok=True)
        path = os.path.join(RW, 'vo_stem.wav' if ver == 'A' else 'vo_stem_B.wav')
        z, info = master(y, path)
        wp = os.path.join(RW, 'words.json' if ver == 'A' else 'words_B.json')
        json.dump(words, open(wp, 'w', encoding='utf8'), ensure_ascii=False, indent=1)
        r = runs_abs(z)
        stems[ver] = dict(path=path, words_path=wp, words=words, master=info, order=order,
                          voice=(r[0][0], r[-1][1]) if r else None, voiced_s=round(sum(b - a for a, b in r), 2),
                          on_voice=round(float(np.mean([any(a - 0.02 <= w['start'] <= b for a, b in r)
                                                        for w in words])), 3))
    plc = {}
    for pid, b in placed.items():
        uid = b['unit']
        k = tab_key(uid, os.path.join(RAW, chosen[uid]), b['speed'])
        lf = lines[pid] if pid in lines else dict(f_in=0, f_out=70, vo_f=(0, 70))
        plc[pid] = dict(unit=uid, take=chosen[uid], speed=b['speed'], caps=list(caps(uid)), start=round(b['t0'], 3),
                        end=round(b['t1'], 3), start_f=fr(b['t0']), end_f=fr(b['t1']), planned_f=lf['vo_f'][0],
                        planned_out_f=lf['vo_f'][1], caption_f=(lf['f_in'], lf['f_out']), cer=tab[k]['cer'],
                        heard=tab[k]['heard'], heard_medium=tab[k].get('heard_medium'),
                        matched='%d/%d' % (b['rep']['matched'], b['rep']['tokens']), pauses=b['rep']['pauses'],
                        why=PLAN[pid]['why'], voice_note=pid in VOICE_NOTE, level_ride_db=b.get('level_db'))
    gaps = [round(plc[b]['start'] - plc[a]['end'], 3) for a, b in zip(ORDER_A, ORDER_A[1:])]
    doc = dict(placement=plc, notes=notes, flash_f=FLASH_F, whip_f=WHIP_F,
               scores={k: {t: [round(float(s[0]), 3), s[1]] for t, s in v.items()} for k, v in scores.items()},
               stems={v: {k: s[k] for k in ('path', 'words_path', 'master', 'voice', 'voiced_s', 'on_voice', 'order')}
                      for v, s in stems.items()}, min_gap=min(gaps))
    json.dump(doc, open(os.path.join(RW, 'placement.json'), 'w'), ensure_ascii=False, indent=1, default=str)
    plot_timeline(stems['A'], plc, os.path.join(RW, 'timeline.png'))
    if final:
        save_final(stems)
    write_md(lines, plc, stems, notes, scores, tab, doc)
    print(json.dumps(dict(notes=notes, min_gap=doc['min_gap'], A=doc['stems']['A'], B=doc['stems']['B']),
                     ensure_ascii=False, indent=1, default=str))
    for pid in ORDER_A + ['HB']:
        p = plc[pid]
        print('%-4s %-14s %.2f f%6.1f-f%6.1f (plan f%d-f%d) cer %.3f %s' % (pid, p['take'], p['speed'], p['start_f'],
                                                                          p['end_f'], p['planned_f'], p['planned_out_f'],
                                                                          p['cer'], p['matched']))
    return doc


def save_final(stems):
    os.makedirs(FINAL, exist_ok=True)
    for ver, s in stems.items():
        nm = '%s_vo_%s' % (SLUG, ver)
        subprocess.run(['ffmpeg', '-hide_banner', '-loglevel', 'error', '-y', '-i', s['path'], '-c:a', 'flac',
                        '-compression_level', '8', '-sample_fmt', 's32', os.path.join(FINAL, nm + '.flac')], check=True)
        shutil.copyfile(s['words_path'], os.path.join(FINAL, nm + '.words.json'))
    shutil.copyfile(os.path.join(RW, 'placement.json'), os.path.join(FINAL, 'placement.json'))
    shutil.copyfile(os.path.join(RW, 'takes.json'), os.path.join(FINAL, 'takes.json'))


def plot_timeline(st, plc, path):
    from PIL import Image, ImageDraw
    x = V.decode(st['path'])
    W, H = 2048, 300
    im = Image.new('RGB', (W, H), (14, 10, 8))
    d = ImageDraw.Draw(im)
    spp = len(x) / W
    for i in range(W):
        seg = x[int(i * spp):int((i + 1) * spp)]
        a = float(np.abs(seg).max()) if len(seg) else 0.0
        d.line([(i, 150 - a * 120), (i, 150 + a * 120)], fill=(255, 181, 71))
    for k in range(0, NF + 1, 15):
        xx = int(k / NF * W)
        d.line([(xx, 270 if k % 60 else 250), (xx, 300)], fill=(120, 110, 130))
    for lid, p in plc.items():
        if lid == 'HB':
            continue
        a, b = int(p['start'] / DUR * W), int(p['end'] / DUR * W)
        d.rectangle([a, 20, b, 34], outline=(80, 230, 255))
        d.text((a + 2, 4), '%s f%d' % (lid, round(p['start_f'])), fill=(255, 243, 230))
    for w in st['words']:
        xx = int(w['start'] / DUR * W)
        d.line([(xx, 40), (xx, 60)], fill=(242, 49, 43) if w['keyword'] else (200, 200, 200))
    im.save(path)


# ------------------------------------------------------------------------------------------------ report
PICTURE = {   # picture events tied to a VO word: (token index, planned frame (SHOTS), event[, 'stay' | 'after'])
              # 'after' = the event follows the END of that word (+ 2 f), e.g. the flash fires after "jao!"
    'C1': [(0, 0, 'C1 `SIRF / *ek* / PHOTO BACHI.` (mid-rise on f0)', 'stay')],
    'C2': [(0, 45, 'C2 `SAB / *ready* / HO JAO!`'), (3, 60, 'FLASH POP + hard cut + L3 push (S2); the kit enters', 'after')],
    'C3': [(0, 75, 'C3 `HAR / *click* / GINTI MEIN THA.`'), (5, 150, 'C1 whip up into the canister (S3)', 'after')],
    'C4': [(0, 165, 'C4 `PHIR ROLL / *studio* / JAATA THA...`')],
    'C6': [(0, 243, 'C6 `3 DIN KA / *intezaar.*` (S4 cut f240 stays)')],
    'C7': [(0, 315, 'C7 `AADHI MEIN / *aankhein* / BAND,` + P1 lands')],
    'C8': [(2, 375, 'P4 THUMB print SLAP + C8 `*thumb.*` slam (music stop f375-f389)', 'stay')],
    'C9': [(0, 420, 'hard cut f420 album page + C9 `PHIR BHI HAR PHOTO / *sambhaali.*`')],
    'C10': [(0, 486, 'C10 `AUR / *aaj?*` (C8 snap f480 stays)')],
    'C11': [(0, 540, '2 TB slam + storage HUD (C11)', 'stay')],
    'C12': [(0, 570, '4 CAMERAS slam (C12) + CAM A-D labels (every 4 f after)')],
    'C13': [(0, 600, '3,000 TAKES slam + hard cut to the bin (C13) + take counter roll')],
    'C14': [(0, 675, 'C14 `HAR TAKE / *dekha.*`')],
    'C15': [(0, 735, 'DISK FULL: bar red + chip + glitch (C15)')],
    'P': [(0, 795, 'toast slides up + typing dots (drop-out)'), (1, 810, 'PAYOFF stack + lockup (f810)', 'stay')],
    'C16': [(0, 909, 'C16 `TAB / *36* / KAAFI THE.`')],
    'Q': [(0, 999, 'outro question on the card (PO from f960)', 'stay')],
}


def proposals(words):
    """[(line, word, event, planned f, VO f, proposed f, kind)] from PICTURE and the placed words."""
    rows = []
    for lid in ORDER_A:
        ws = [w for w in words if w['line'] == lid]
        for row in PICTURE.get(lid, []):
            i, f_plan, ev = row[:3]
            kind = row[3] if len(row) > 3 else ''
            if i >= len(ws):
                continue
            if kind == 'after':
                on = ws[i]['end_f']
                prop = max(f_plan, int(math.ceil(on)) + 2)
            else:
                on = ws[i]['start_f']
                prop = f_plan if (kind == 'stay' or abs(on - f_plan) <= 2) else int(np.floor(on))
            rows.append((lid, ws[i]['word'], ev, f_plan, on, prop, kind))
    return rows


def write_md(lines, plc, stems, notes, scores, tab, doc):
    A_, B_ = stems['A'], stems['B']
    W = lambda ws, lid: [w for w in ws if w['line'] == lid]  # noqa: E731
    o = ['# VO_TIMING · Sirf 36 Shots (@jawad_mp4)', '',
         '2026-10-12, sound-designer + music-supervisor, `pipeline/jawad_reels/sirf_36_shots_vo.py assemble` '
         '(measured). Voice: Higgsfield preset Vlad, `elevenlabs_v4`, the paid takes in '
         '`brand_reels/assets/sirf_36_shots/vo_raw/` (none regenerated, no paid call). Chain `vo_chain.py` per '
         'vo_config: trim to 40 ms, internal pauses capped per take (table in section 4), rubberband 1.06-1.10x '
         '(formant preserved; the gentlest speed that fits every line of the take), HPF 70 Hz, de-ess, 2.5:1 '
         'compression, loudnorm -16 LUFS / -2 dBTP; word timings faster-whisper small (DEV prompt, numpy input) '
         'aligned to the DEV tokens, snapped to the voiced onsets. Combined takes (C07C08, C11C13, C14C15) are cut in '
         'the middle of the silence between their lines so each line sits on its own beat. P (the client) carries a '
         'light voice-note colour (HP 220 Hz / LP 6.2 kHz, loudness-matched). Every line is ridden to the same speech '
         'loudness (-16.3 LUFS K-weighted over its voiced span = the median line, before the stem gain; column `ride dB`): the C14C15 '
         't2 take came out 4.5 dB under the rest. LEAD_DECISIONS 3: picture beats move '
         'to the VO (section 3).', '']
    for ver, s in (('A', A_), ('B', B_)):
        m = s['master']['post']
        o.append('- **Stem %s** `%s`: %d samples (%.3f s) at 48000 Hz, %.2f LUFS integrated, %.2f dBTP, LRA %.1f LU, '
                 'VO %.3f-%.3f s, %.2f s voiced, %d words (%d keywords), %d %% of word starts on voice; gain %+.2f dB, '
                 'limiter %s; lines %s.' % (ver, os.path.relpath(s['path'], REPO), NSAMP, DUR, m['lufs'], m['tp'],
                                            m['lra'], s['voice'][0], s['voice'][1], s['voiced_s'], len(s['words']),
                                            sum(w['keyword'] for w in s['words']), round(100 * s['on_voice']),
                                            s['master']['gain_db'], 'on' if s['master']['limiter'] else 'off',
                                            ' '.join(s['order'])))
    o += ['- Hook B (Trial Reel): `HB_t1.mp3` ("Hilna mat! Aankh mat jhapkana.") replaces C1 + C2; identical to A '
          'from C3 on (the flash pops after the hook in both).',
          '- Words: `workspace/jawad_reels/sirf_36_shots/vo/words.json` (A) / `words_B.json` (B), reel time, '
          'snake_captions format (+ line, i, dev, heard, ok, start_f, end_f). Copies (FLAC 24-bit + json): '
          '`brand_reels/assets/sirf_36_shots/vo_final/sirf_36_shots_vo_{A,B}.flac` / `.words.json`, '
          '`placement.json`, `takes.json`.',
          '- Every SCRIPT line is in the VO (no line dropped). Minimum gap between lines: %.3f s (rule >= %.2f s).'
          % (doc['min_gap'], GAP_MIN), '',
          '## 1. Line timing (hook A)', '',
          '| line | take | speed | ride dB | start → end (s) | frames | SCRIPT VO window f | Δ start f | words (reel s) | CER (take) | aligned (take) |',
          '|---|---|---|---|---|---|---|---|---|---|---|']
    for lid in ORDER_A + ['HB']:
        p = plc[lid]
        ws = W((A_ if lid != 'HB' else B_)['words'], lid) if lid != 'HB' else [w for w in B_['words'] if w['line'] in ('HB1', 'HB2')]
        wtxt = ' '.join('%s%s %.2f' % ('**' if w['keyword'] else '', w['word'] + ('**' if w['keyword'] else ''),
                                       w['start']) for w in ws)
        o.append('| %s | `%s` | %.2f | %+.1f | %.3f → %.3f | f%.1f-f%.1f | f%d-f%d | %+.1f | %s | %.3f | %s |'
                 % (lid + (' (B)' if lid == 'HB' else ''), p['take'], p['speed'], p['level_ride_db'], p['start'], p['end'], p['start_f'],
                    p['end_f'], p['planned_f'], p['planned_out_f'], p['start_f'] - p['planned_f'], wtxt, p['cer'],
                    p['matched']))
    o += ['', '## 2. Word frames (stem A; f = reel frame at 30 fps)', '',
          '| line | word | start s | end s | start f | end f | keyword | heard |', '|---|---|---|---|---|---|---|---|']
    for lid in ORDER_A:
        for w in W(A_['words'], lid):
            o.append('| %s | %s | %.3f | %.3f | %.1f | %.1f | %s | %s |' % (lid, w['word'], w['start'], w['end'],
                                                                         w['start_f'], w['end_f'],
                                                                         'yes' if w['keyword'] else '', w['heard']))
    o += ['', '## 3. Picture beats that move to the VO (proposed frames for the motion designer)', '',
          'LEAD_DECISIONS 3: the picture follows the measured VO. Proposed frame = the onset frame of the VO word '
          '(rounded down, so the visual leads the word by at most 1 frame); "after" events follow the END of the word '
          '(+2 f). |Δ| <= 2 f, or a structural frame marked "stays": keep the planned frame.', '',
          '| line | word | event (SHOTS / SCRIPT) | planned f | VO f | proposed f | Δ f |', '|---|---|---|---|---|---|---|']
    moves = []
    for lid, word, ev, f_plan, on, prop, kind in proposals(A_['words']):
        if prop != f_plan:
            moves.append('%s f%d -> f%d' % (ev.split(' ')[0].strip('`'), f_plan, prop))
        o.append('| %s | %s | %s | f%d | %.1f%s | **f%d**%s | %+d |' % (lid, word, ev, f_plan, on,
                                                                     ' (end)' if kind == 'after' else '', prop,
                                                                     ' (stays)' if kind == 'stay' else '',
                                                                     prop - f_plan))
    o += ['', 'Moves: ' + ('; '.join(moves) if moves else 'none') + '. Fixed by sound (the music and SFX already follow): '
          'FLASH POP f%d (was f60), C1 whip f%d (was f150). Caption lockups enter on their word onset (rows above); '
          'exits stay as SHOTS unless the next lockup now enters earlier. The music (sirf_36_shots_music.py) and the '
          'SFX cue table (sirf_36_shots_sfx.py) follow these frames; SOUND.md section 2 has the full grid.'
          % (FLASH_F, WHIP_F)]
    o += ['', '## 4. Takes (CER = faster-whisper small and medium, no prompt, on the processed take vs the DEV text; '
          'best of the two; nukta / candrabindu folded, Latin loan words mapped)', '',
          '| unit (lines) | pause caps (s) | take | mean CER (1.06/1.08/1.10) | span @1.08 s | heard @ placed speed (small / medium) | chosen |',
          '|---|---|---|---|---|---|---|']
    for uid in UNITS:
        sp = next((p['speed'] for p in plc.values() if p['unit'] == uid), 1.10)
        for t, s in sorted(scores[uid].items()):
            k = tab_key(uid, os.path.join(RAW, t), sp)
            ch = next((p['take'] for p in plc.values() if p['unit'] == uid), None)
            o.append('| %s (%s) | %.2f / %.2f | `%s` | %.3f | %.3f | %s / %s | %s |' % (
                uid, '+'.join(UNITS[uid][1]), caps(uid)[0], caps(uid)[1], t, s[0], s[1], tab[k]['heard'],
                tab[k].get('heard_medium', ''), 'yes' if t == ch else ''))
    o += ['', '## 5. Notes', ''] + ['- ' + n for n in notes] + [
        '- Rebuild: `cd pipeline/jawad_reels && tools/heavy.sh python3 sirf_36_shots_vo.py process && '
        'tools/heavy.sh python3 sirf_36_shots_vo.py assemble` (deterministic; PLAN / CAPS / FLASH_F / WHIP_F at the '
        'top of the module hold the slots), then `tools/heavy.sh python3 sirf_36_shots_sfx.py build` (music, SFX, '
        'mixes).', '']
    open(MD, 'w', encoding='utf8').write('\n'.join(o))


def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('cmd', choices=('process', 'assemble'))
    ap.add_argument('--force', action='store_true')
    ap.add_argument('--no-final', action='store_true')
    a = ap.parse_args()
    if a.cmd == 'process':
        cmd_process(a.force)
    else:
        cmd_assemble(not a.no_final)


if __name__ == '__main__':
    main()
