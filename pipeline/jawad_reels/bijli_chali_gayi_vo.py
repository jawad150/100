"""bijli_chali_gayi_vo.py - C11 "Bijli Chali Gayi" VO: Vlad (Higgsfield elevenlabs_v4) takes -> processed lines
(vo_chain) -> the VO stems on the BRIEF r2 section 6.7 beat table (hook A and hook B) + reel-time word timings +
VO_TIMING.md.

Sources (binding): brand_reels/design/reels/bijli_chali_gayi/script.json (DEV / ROM tokens per line, v2 copy),
BRIEF.md r2 section 6.3 / 6.4 / 6.7 (windows, bold targets, +-0.25 s rule, overrun ladder), SCRIPT.md v2 sections 4,
6, 7, 9 (speeds, fit ladders, pronunciation risks), vo_config.json (recipe, post-processing). Only this reel's files
are written; vo_chain is imported read-only.

    cd pipeline/jawad_reels
    python3 -I bijli_chali_gayi_vo.py requests [--plan lines|grouped]   # -> <RW>/vo/requests.json (payloads)
    python3 -I bijli_chali_gayi_vo.py ledger --balance 7180.2           # record a balance check (guard 7015)
    python3 -I bijli_chali_gayi_vo.py ledger --id V8 --cost 0.6 [--job ID] [--preflight]   # credits.json
    tools/heavy.sh python3 -I bijli_chali_gayi_vo.py pron       # carriers P1-P4 -> pron_check.json, spelling.json
    tools/heavy.sh python3 -I bijli_chali_gayi_vo.py cands      # every candidate take (CANDS) -> cands.json
    tools/heavy.sh python3 -I bijli_chali_gayi_vo.py assemble   # placement, stems A/B, words, VO_TIMING.md, checks
    tools/heavy.sh python3 -I bijli_chali_gayi_vo.py process    # the chosen takes at the placed speeds -> CER, keywords
    (final run 2026-10-09: assemble -> process -> assemble; the second assemble writes the report with the CERs)
    options: --raw DIR (takes, default <RW>/vo/raw) --work DIR (outputs, default <RW>/vo) --md PATH
             --label TEXT --lines V1,V2 (process only these) --force (re-run vo_chain)

Run 2026-10-09: the takes are <raw>/<ID>_r<N>.mp3 (lines), <G>_r<N>.mp3 (grouped takes; T2m = T2 with the
SCRIPT 9 spelling मुहल्ला, T4p = T4 with "दबाती है,", T5f3 = T5 without हमें), V1Bc = V1B with a comma, V3bm = V3b
with मुहल्ला, V10c = V10 with a comma, pron/P0-P8 = carriers. requests.json "submitted" records each file's job id,
cost and exact text (the DEV a take is aligned against); select.json picks the take per line ({"take", "group"} = cut
out of a grouped take) and the ladder variants in force ("_variants": ["F4"] drops V9); decisions.json adds the lead
items to the report. Original naming scheme (still supported):
Takes: <raw>/bcg_<ID>_t<N>.mp3 (ID = V1, V2, V1B, V3a, V3b, V4 ... V12; P1 ... P4 = pronunciation carriers; TA, TB,
T2 ... T6 = the grouped takes of SCRIPT section 7, used only with --plan grouped). The highest N wins unless
<work>/select.json maps an ID to a file name. A line with no take of its own is cut out of its grouped take.
The DEV text of a take is the text recorded for its file name in requests.json (so a re-spelled retake is aligned
against what was actually sent), else script.json + spelling.json.

Outputs in <work>: proc/<take>_<speed>.wav (+ .words.json / .report.json from vo_chain), lines.json (every measure and
decision), placement.json, vo_stem.wav (= hook A) and vo_stem_B.wav (34.667 s = 1,664,000 samples, 48 kHz 24-bit mono,
-16 LUFS integrated, TP <= -2 dBTP; copies bijli_chali_gayi_vo_A.wav / _B.wav), words.json (= A) and words_B.json
(reel time, snake_captions format + line / i / dev / heard / ok / hide; copies bijli_chali_gayi_vo_A.words.json /
_B.words.json as BRIEF 6.14 names them), check.json, timeline.png; the timing table goes to --md (default the reel's
VO_TIMING.md).
"""
import glob
import json
import os
import re
import shutil
import subprocess
import sys
import time
import unicodedata

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import vo_chain as V  # noqa: E402  (read-only shared module)

REPO = os.path.abspath(os.path.join(HERE, '..', '..'))
RW = os.path.join(REPO, 'workspace', 'jawad_reels', 'bijli_chali_gayi')
DESIGN = os.path.join(REPO, 'brand_reels', 'design', 'reels', 'bijli_chali_gayi')
SCRIPT_JSON = os.path.join(DESIGN, 'script.json')
SR = 48000
FPS = 30
DUR = 1040 / FPS                      # 34.667 s
NSAMP = 1040 * SR // FPS              # 1,664,000 samples exactly
LUFS, TP_MAX = -16.0, -2.0
CER_MAX = 0.15
GAP_MIN = 0.12                        # BRIEF 6.7 ladder F2: inter-line gaps down to 0.12 s
VOICE_ID = 'e5666b9c-99a2-4fac-8b4e-abee078b186d'
BUDGET, GUARD = 25.0, 6800.0          # task rule (run 2): stop generating below 6800 credits
PREFIX = 'bcg'

ORDER_A = ['V1', 'V2', 'V3a', 'V3b', 'V4', 'V5', 'V6', 'V7', 'V8', 'V9', 'V10', 'V11', 'V12']
ORDER_B = ['V1B', 'V3a', 'V3b', 'V4', 'V5', 'V6', 'V7', 'V8', 'V9', 'V10', 'V11', 'V12']
LINES = ['V1', 'V2', 'V1B', 'V3a', 'V3b', 'V4', 'V5', 'V6', 'V7', 'V8', 'V9', 'V10', 'V11', 'V12']
BODY = ORDER_A[2:]
# requests: the lines plan (one take per beat line, the task's plan) in batches of <= 12; the grouped plan is
# SCRIPT section 7 (7 takes) for the case where the per-request price makes 18 requests exceed the 25-credit budget.
BATCHES = [['V1', 'V2', 'V1B', 'V3a', 'V3b', 'V4', 'V5'], ['V6', 'V7', 'V8', 'V9', 'V10', 'V11', 'V12']]
GROUPS = {'T5': ['V10', 'V11'], 'T4': ['V7', 'V8', 'V9'], 'TB': ['V1B'], 'TA': ['V1', 'V2'],
          'T2': ['V3a', 'V3b', 'V4'], 'T3': ['V5', 'V6'], 'T6': ['V12']}

# ------------------------------------------------------------------------------------------------ the plan
# BRIEF r2 6.7 windows (bold = may not move), +-0.25 s on the rest (bible 5.5). Per line:
#   speeds  vo_chain speeds to try in order, gentlest first (SCRIPT 7; never above 1.10, never pitch); a line that
#           cannot fit its window moves to the next speed (ladder F1), then its chain neighbours do
#   anchor  (token index, target s, lo, hi): the anchor word's voiced onset must land in [lo, hi]; alts = other
#           targets tried in order inside [lo, hi] (V9 "tees" on an 8th press: f700, f690, f680)
#   win     the brief window (t0, t1) for the report; start_min / end_max = hard limits on the voiced start / end
#   soft_end  end limit dropped only if nothing else fits (reported as a miss)
PLAN = {
    'V1': dict(speeds=[1.08, 1.10], anchor=(0, 0.100, 0.085, 0.130), win=(0.100, 1.300), bold='start',
               end_max=1.300, why='VO onset <= 0.13 (QA); ends before the backup beep at 1.333 (f40)'),
    'V2': dict(speeds=[1.10], anchor=(0, 2.200, 2.170, 2.240), win=(2.200, 2.600), bold='end', end_max=2.633,
               fallback=dict(anchor=(0, 1.550, 1.545, 1.600), end_max=2.000, win=(1.550, 2.000)),
               why='"Yaad" f66 after beep pulse 2; <= 0.43 s keeps 2.200 (ends <= 2.633, the f79 splice); else the '
                   'GATE fix-5 fallback 1.550-2.000 between the beep pairs (lead OK); never trim the rising "hai?"'),
    'V1B': dict(speeds=[1.08, 1.10], anchor=(0, 0.300, 0.285, 0.330), win=(0.300, 1.950), bold='start',
                end_max=1.950, soft_end=True, split=1,
                part2=dict(anchor=(2, 1.667, 1.567, 1.700), why='"yaad" on the 8th f50; the "..." pause holds the '
                           'beep pair f40/f44 (1.333-1.537): "awaaz" ends <= 1.333, "yaad" starts >= 1.567'),
                beep=(1.333, 1.537), why='hook B: VO 0.300 (QA <= 0.33)'),
    'V3a': dict(speeds=[1.08, 1.10], anchor=(0, 3.000, 2.850, 3.100), win=(3.000, 4.000), end_max=4.000,
                soft_end=True, why='"Light" on the 8th f90 after the match strike f80; the start may move to 2.850'),
    'V3b': dict(speeds=[1.08, 1.10], anchor=(3, 5.400, 5.350, 5.450), win=(4.200, 6.450), start_min=3.950,
                end_max=6.700, why='BOLD "chhat" onset 5.350-5.450 (f162, never before f160)'),
    'V4': dict(speeds=[1.08, 1.10], anchor=(0, 6.600, 6.350, 6.850), win=(6.600, 7.850), bold='end',
               end_max=7.850, why='ends <= 7.85 (>= 0.15 s before the f240 slam AA GAYI!)'),
    'V5': dict(speeds=[1.08, 1.10], anchor=(2, 11.333, 11.100, 11.600), win=(11.000, 12.650), start_min=10.750,
               end_max=12.650, why='"bachche" on beat 17 (f340); ends before the beep at 12.667'),
    'V6': dict(speeds=[1.08, 1.10], anchor=(1, 13.367, 13.330, 13.400), win=(13.150, 14.600), bold='anchor',
               start_min=12.900, end_max=14.850, soft_end=True,
               why='BOLD "editor" onset 13.367 (QA 13.33-13.40) = the on-word cut f400; no VO 14.6-16.4'),
    'V7': dict(speeds=[1.08, 1.10], anchor=(0, 16.400, 16.400, 16.450), win=(16.400, 18.830), bold='start',
               end_max=19.080, soft_end=True, why='BOLD start after 0.4 s of designed silence (power dies f480)'),
    'V8': dict(speeds=[1.08, 1.10], anchor=(6, 21.333, 20.667, 21.700), win=(18.950, 22.390), start_min=18.700,
               bold_anchor=(20.667, 21.333),
               end_max=22.640, soft_end=True,
               why='"Ctrl+S" onset inside f620-f640 (20.667-21.333), f640 if the take allows'),
    'V9': dict(speeds=[1.08, 1.10], anchor=(1, 23.333, 22.633, 23.367), alts=[(23.000,), (22.667,)],
               win=(22.510, 23.320), start_min=22.260, end_max=23.570, soft_end=True,
               why='"tees" on an 8th press: f700 (23.333) preferred, f690 (23.000), then f680'),
    'V10': dict(speeds=[1.10], anchor=(0, 24.000, 23.670, 24.050), win=(23.680, 26.300), bold='end',
                end_max=26.300, why='"Bijli" on the f720 cut when the take allows, else a J-cut pre-lap <= 0.33 s; '
                                    'BOLD end 26.300 before the drop-out f790'),
    'V11': dict(speeds=[1.06, 1.10], anchor=(0, 27.333, 27.300, 27.370), win=(27.300, 28.200), bold='anchor',
                end_max=28.450, soft_end=True, why='BOLD "sabr" onset f820 (QA 27.30-27.37), the harmonium peak'),
    'V12': dict(speeds=[1.06, 1.10], anchor=(0, 31.667, 31.350, 31.900), win=(31.650, 34.100), bold='end',
                end_max=34.100, why='start on the 8th f950 or later (as early as 31.35 if the take is slow); BOLD end '
                                    '<= 34.10 (QA <= 34.17); V1 answers it on the loop'),
}
NO_VO = [(8.000, 10.667, 'slam + cheer (no VO)'), (16.000, 16.400, 'designed VO silence after f480'),
         (28.450, 31.350, 'power return, the loudest moment')]
HIDE = [(0.0, 80 / FPS), (800 / FPS, 880 / FPS), (920 / FPS, DUR)]       # BRIEF 6.14 caption hide windows

# ------------------------------------------------------------------------------------------------ pronunciation
# SCRIPT section 9 risk words in short carrier phrases (primary spelling, and the fallback where one exists).
PRON = [
    dict(id='P1', text='सब्र सिखाया। सबर सिखाया।', words=['सब्र', 'सबर'],
         why='risk 1: sabr as one stressed beat (<= 0.35 s) vs the fallback सबर'),
    dict(id='P2', text='उंगली ख़ुद कंट्रोल-एस दबाती है। उंगली खुद कंट्रोल एस दबाती है।',
         words=['ख़ुद', 'कंट्रोल-एस', 'खुद', 'कंट्रोल', 'एस'],
         why='risks 2 + 4: the hyphenated Ctrl+S (gap / "dash") vs P-ctrl, the nukta kh vs खुद'),
    dict(id='P3', text='ये आवाज़... याद है? हमें एडिटिंग नहीं सिखाई।', words=['आवाज़', 'याद', 'एडिटिंग', 'हमें'],
         why='risks 3, 5, 6: nukta z, "editing" (not "edi-tang"), the "..." pause and the rising "hai?"'),
    dict(id='P4', text='पूरा मोहल्ला छत पे होता था। हर तीस सेकंड। सब से बड़ी दुश्मन।',
         words=['मोहल्ला', 'छत', 'सेकंड', 'बड़ी', 'दुश्मन'],
         why='risks 8, 9, 10: the double l, the final d of "second", the retroflex flap'),
]
# spelling decisions: primary DEV token -> fallback (applied to the line texts only when the carrier check fails)
FALLBACK = {'सब्र': 'सबर', 'कंट्रोल-एस': 'कंट्रोल एस', 'ख़ुद': 'खुद', 'एडिटिंग': 'एडीटिंग', 'मोहल्ला': 'मुहल्ला',
            'सेकंड': 'सेकेंड'}
TOKEN_SPLITS = {'कंट्रोल एस': (['कंट्रोल', 'एस'], ['Ctrl', 'S'])}    # P-ctrl: one token becomes two (DEV and ROM)
LOAN = {'editor': 'एडिटर', 'editors': 'एडिटर', 'editing': 'एडिटिंग', 'light': 'लाइट', 'second': 'सेकंड',
        'seconds': 'सेकंड', 'sec': 'सेकंड', 'ctrl': 'कंट्रोल', 'control': 'कंट्रोल', 's': 'एस', 'desi': 'देसी',
        'ctrls': 'कंट्रोलएस', 'mohalla': 'मोहल्ला', '30': 'तीस', '३०': 'तीस'}
KW_OK = 1.15        # vo_chain.sim >= 1.15: the heard word carries the keyword's consonant skeleton


# ------------------------------------------------------------------------------------------------ script
def load_script():
    d = json.load(open(SCRIPT_JSON, encoding='utf8'))
    lines = {l['id']: l for l in d['lines']}
    for k in LINES:
        l = lines[k]
        dev, rom = V.tokens(l['dev']), V.tokens(l['tokens'])
        if dev != l['dev_tokens'] or len(dev) != len(rom):
            raise ValueError('%s: DEV/ROM token mismatch (%d vs %d)' % (k, len(dev), len(rom)))
        if re.search(r'[A-Za-z0-9\[\]()]', l['dev']):
            raise ValueError('%s: DEV text has Latin, digits or brackets' % k)
    return d, lines


# BRIEF 6.7 overrun ladder variants that change a line's tokens (a re-take with the shorter text). Activated by
# select.json "_variants": ["F3"]; DEV and ROM stay 1:1.
VARIANTS = {
    'F3': {'V10': (['बिजली', 'ने', 'एडिटिंग', 'नहीं', 'सिखाई...'], ['Bijli', 'ne', '*editing', 'nahi', 'sikhai...'])},
    'F4': {},
}
DROPS = {'F4': ['V9']}     # F4: V9 leaves the VO; U3F `Saved · har 30 sec` shows as the last chip (f712-f719)


def dropped(work):
    sel = os.path.join(work, 'select.json')
    if not os.path.exists(sel):
        return []
    return [l for v in json.load(open(sel, encoding='utf8')).get('_variants', []) for l in DROPS.get(v, [])]


def with_variant(lines, variant):
    out = dict(lines)
    for lid, (dv, rm) in VARIANTS[variant].items():
        l = dict(lines[lid])
        l.update(dev_tokens=list(dv), tokens=list(rm), dev=' '.join(dv), roman=' '.join(r.lstrip('*') for r in rm),
                 variant=variant)
        out[lid] = l
    return out


def load_lines(work):
    """script.json lines with the select.json "_variants" applied."""
    d, lines = load_script()
    sel = os.path.join(work, 'select.json')
    if os.path.exists(sel):
        for v in json.load(open(sel, encoding='utf8')).get('_variants', []):
            lines = with_variant(lines, v)
    return d, lines


def load_spelling(work):
    p = os.path.join(work, 'spelling.json')
    return json.load(open(p, encoding='utf8')).get('use', {}) if os.path.exists(p) else {}


def apply_spelling(dev_tokens, rom_tokens, use):
    """Swap DEV tokens for the chosen spellings (punctuation kept); a P-ctrl swap splits one token into two on both
    tracks (the keyword mark goes to the first part, trailing punctuation to the last)."""
    dev, rom = [], []
    for d, r in zip(dev_tokens, rom_tokens):
        core, punct = re.match(r'^(.*?)([,.?!\u0964\u2026]*)$', d).groups()
        new = use.get(core, core)
        if new in TOKEN_SPLITS:
            dd, rr = TOKEN_SPLITS[new]
            star, _, rpunct = re.match(r'^(\*?)(.*?)([,.?!\u0964\u2026]*)$', r).groups()
            dev += dd[:-1] + [dd[-1] + punct]
            rr = list(rr)
            rr[0], rr[-1] = star + rr[0], rr[-1] + rpunct
            rom += rr
        else:
            dev.append(new + punct)
            rom.append(r)
    return dev, rom


def line_tokens(lines, lid, use):
    l = lines[lid]
    return apply_spelling(l['dev_tokens'], l['tokens'], use)


def anchor_index(lines, lid, use):
    """The plan's anchor token index after any token split (a split before the anchor shifts it)."""
    i = PLAN[lid]['anchor'][0] if lid in PLAN else 0
    dev0 = lines[lid]['dev_tokens']
    shift = 0
    for k in range(i):
        core = re.sub(r'[,.?!।…]+$', '', dev0[k])
        new = use.get(core, core)
        if new in TOKEN_SPLITS:
            shift += len(TOKEN_SPLITS[new][0]) - 1
    return i + shift


# ------------------------------------------------------------------------------------------------ text metrics
def norm_cer(s):
    s = unicodedata.normalize('NFD', s.lower())
    s = ''.join(V.NUKTA.get(ch, ch) for ch in s)
    s = unicodedata.normalize('NFC', s).replace('़', '').replace('ँ', 'ं')
    s = re.sub(r'[‌‍]', '', s)
    s = re.sub(r'[^\w\s]', ' ', s)
    return re.sub(r'\s+', '', s)


def lev(a, b):
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        cur = [i]
        for j, cb in enumerate(b, 1):
            cur.append(min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + (ca != cb)))
        prev = cur
    return prev[-1]


def cer(hyp, ref):
    r = norm_cer(ref)
    return lev(norm_cer(hyp), r) / max(1, len(r))


def loan_map(hyp):
    """Latin / digit words whisper wrote for loan words -> the script's Devanagari ('editing' was said एडिटिंग)."""
    return re.sub(r'[A-Za-z0-9०-९]+', lambda m: LOAN.get(m.group(0).lower(), m.group(0)), hyp)


_WM = {}


def whisper(x16, prompt=None, model='small'):
    """faster-whisper int8 (language hi, word stamps) on a 16 kHz numpy array (never a path: the PyAV path bug)."""
    from faster_whisper import WhisperModel
    if model not in _WM:
        mp = os.path.join(V.WHISPER, 'faster-whisper-%s' % model)
        _WM[model] = WhisperModel(mp if os.path.isdir(mp) else model, device='cpu', compute_type='int8',
                                  cpu_threads=V.THREADS)
    segs, _ = _WM[model].transcribe(np.asarray(x16, np.float32), language='hi', word_timestamps=True, beam_size=5,
                                    initial_prompt=prompt, condition_on_previous_text=False, vad_filter=False)
    words, text = [], []
    for s in segs:
        text.append(s.text.strip())
        for w in s.words or []:
            words.append(dict(w=w.word.strip(), s=round(float(w.start), 3), e=round(float(w.end), 3),
                              p=round(float(w.probability), 3)))
    return ' '.join(text).strip(), words


def to16(x48):
    from scipy.signal import resample_poly
    return resample_poly(np.asarray(x48, np.float64), 1, 3).astype(np.float32)


GEM0 = re.compile('^([\u0915\u0917\u091a\u091c\u091f\u0921\u0924\u0926\u092a\u092c])\u094d'
                  '(?=[\u0916\u0918\u091b\u091d\u0920\u0922\u0925\u0927\u092b\u092d])')


def ungeminate(w):
    """Whisper writes a strongly aspirated word-initial stop as a geminate (च्छत for छत); Hindi has no word-initial
    geminate, so the first consonant + virama is dropped before comparing."""
    return GEM0.sub('', w)


def best_match(word, heard):
    if not heard:
        return None, -1.0, None
    cands = [(h['w'], h['s'], h['e']) for h in heard]
    cands += [(a['w'] + b['w'], a['s'], b['e']) for a, b in zip(heard, heard[1:])]
    cands = [(loan_map(c), s, e) for c, s, e in cands]
    sc = [V.sim(word, ungeminate(c[0])) for c in cands]
    k = int(np.argmax(sc))
    return cands[k][0], round(float(sc[k]), 2), (cands[k][1], cands[k][2])


# ------------------------------------------------------------------------------------------------ takes
def takes_for(raw, ident):
    fs = [f for ext in ('mp3', 'wav') for f in glob.glob(os.path.join(raw, '%s_%s_t*.%s' % (PREFIX, ident, ext)))]
    fs = [f for f in fs if re.search(r'_%s_t(\d+)\.(mp3|wav)$' % re.escape(ident), f)]
    return sorted(fs, key=lambda f: int(re.search(r'_t(\d+)\.(mp3|wav)$', f).group(1)))


def selection(work, ident):
    """select.json entry for an id: "file.mp3" (a take of this line alone) or {"take": "file.mp3", "group": "T4"}
    (the line is cut out of that grouped take). -> (file name, group id or None) or None."""
    sel = os.path.join(work, 'select.json')
    if not os.path.exists(sel):
        return None
    v = json.load(open(sel, encoding='utf8')).get(ident)
    if not v:
        return None
    return (v, None) if isinstance(v, str) else (v['take'], v.get('group'))


def pick_take(raw, work, ident):
    s = selection(work, ident)
    if s:
        p = os.path.join(raw, s[0])
        if not os.path.exists(p):
            raise FileNotFoundError(p)
        return p
    fs = takes_for(raw, ident)
    return fs[-1] if fs else None


def sent_text(work, take):
    """The DEV text recorded in requests.json for this take's file name (None if unknown)."""
    p = os.path.join(work, 'requests.json')
    if not os.path.exists(p):
        return None
    name = os.path.splitext(os.path.basename(take))[0]
    req = json.load(open(p, encoding='utf8'))
    for key, val in req.items():
        if isinstance(val, list):
            for r in val:
                if isinstance(r, dict) and os.path.splitext(r.get('save_as', ''))[0] == name:
                    return r['params']['prompt']
    return None


def source_for(raw, work, lid):
    """-> ('line', take) | ('group', take, group id, [lines]) | None."""
    s = selection(work, lid)
    if s and s[1]:
        p = os.path.join(raw, s[0])
        if not os.path.exists(p):
            raise FileNotFoundError(p)
        return ('group', p, s[1], GROUPS[s[1]])
    t = pick_take(raw, work, lid)
    if t:
        return ('line', t)
    for g, ls in GROUPS.items():
        if lid in ls:
            t = pick_take(raw, work, g)
            if t:
                return ('group', t, g, ls)
    return None


def tokens_for_take(work, take, lines, ids, use):
    """DEV / ROM token lists for the line ids a take covers (from the text actually sent when recorded)."""
    dev, rom, ranges = [], [], {}
    for lid in ids:
        d, r = line_tokens(lines, lid, use)
        ranges[lid] = (len(dev), len(dev) + len(d) - 1)
        dev += d
        rom += r
    sent = sent_text(work, take)
    if sent is not None and V.tokens(sent) != dev:
        sd = V.tokens(sent)
        if len(sd) != len(dev):
            raise ValueError('%s: sent text has %d tokens, the script %d: %s' % (take, len(sd), len(dev), sent))
        dev = sd                                         # same count: align against what was sent
    return dev, rom, ranges


# ------------------------------------------------------------------------------------------------ requests
def req_params(text, stability=None):
    p = dict(model='elevenlabs_v4', prompt=text, dialogue=[dict(text=text, voice_id=VOICE_ID, voice_type='preset')])
    if stability is not None:
        p['stability'] = stability
    return p


def cmd_requests(work, plan='lines', retake=None, stability=None):
    if os.path.exists(os.path.join(work, 'requests.json')) and 'submitted' in json.load(
            open(os.path.join(work, 'requests.json'), encoding='utf8')):
        raise SystemExit('requests.json holds the record of submitted requests (run 2026-10-09): not overwritten')
    d, lines = load_script()
    use = load_spelling(work)
    p = os.path.join(work, 'requests.json')
    old = json.load(open(p, encoding='utf8')) if os.path.exists(p) else {}

    def entry(ident, text, n=1, **kw):
        return dict(id=ident, save_as='%s_%s_t%d.mp3' % (PREFIX, ident, n), chars=len(text), params=req_params(
            text, kw.pop('stability', None)), **kw)

    def line_text(lid):
        return ' '.join(line_tokens(lines, lid, use)[0])
    if retake:                                          # append retakes to the existing file
        raw = os.path.join(work, 'raw')
        out = old
        out.setdefault('retakes', [])
        for lid in retake:
            ids = GROUPS.get(lid, [lid])
            n = max([int(re.search(r'_t(\d+)\.', f).group(1)) for f in takes_for(raw, lid)] +
                    [int(re.search(r'_t(\d+)\.', r['save_as']).group(1)) for r in out['retakes'] if r['id'] == lid]
                    + [0]) + 1
            out['retakes'].append(entry(lid, ' '.join(line_text(k) for k in ids), n, stability=stability,
                                        why='retake (CER / keyword / timing); spelling.json applied'))
    else:
        out = dict(
            reel='bijli_chali_gayi', voice='Vlad (preset) on elevenlabs_v4', voice_id=VOICE_ID, plan=plan,
            rules=['call balance first and before each batch; stop generating if the balance is below %d' % GUARD,
                   'preflight every request with get_cost: true; record it with `ledger --preflight` before submitting;'
                   ' reel budget %.0f credits (credits.json keeps the running sum)' % BUDGET,
                   'leave use_unlim unset (answer an unlim_choice with false); omit folder_id; stability only on a '
                   'retake (0.35 flat / 0.55 unstable)',
                   'poll job ids with jobs_wait; never resubmit blindly',
                   'curl each result_url into vo/raw/ under save_as (the next _t<N> for a retake)',
                   'batch_1 first; run `pron`; then `requests` again (spelling.json fallbacks go into the line texts) '
                   'and submit the line batches',
                   'use the grouped plan (7 takes) instead of the 14 line takes if the preflight price of 18 requests '
                   'exceeds the budget'],
            batch_1_pronunciation=[entry(x['id'], x['text'], why=x['why']) for x in PRON],
            spelling=use)
        if plan == 'lines':
            for b, ids in enumerate(BATCHES, 2):
                out['batch_%d_lines' % b] = [entry(lid, line_text(lid), lines=[lid]) for lid in ids]
        else:
            out['batch_2_grouped'] = [entry(g, ' '.join(line_text(k) for k in ids), lines=ids)
                                      for g, ids in GROUPS.items()]
        out['retakes'] = old.get('retakes', [])
    os.makedirs(work, exist_ok=True)
    json.dump(out, open(p, 'w', encoding='utf8'), ensure_ascii=False, indent=1)
    print('->', p)
    for k, v in out.items():
        if isinstance(v, list) and v and isinstance(v[0], dict) and 'chars' in v[0]:
            print('%-24s %2d requests, %3d chars' % (k, len(v), sum(r['chars'] for r in v)))
    return out


# ------------------------------------------------------------------------------------------------ ledger
def cmd_ledger(work, ident=None, cost=None, job=None, balance=None, preflight=False, note=''):
    p = os.path.join(work, 'credits.json')
    L = json.load(open(p)) if os.path.exists(p) else dict(reel='bijli_chali_gayi', budget_credits=BUDGET,
                                                          global_guard_min_balance=GUARD, spent_credits=0.0,
                                                          requests=[], balance_checks=[], log=[])
    now = time.strftime('%Y-%m-%dT%H:%M', time.gmtime())
    rc = 0
    if balance is not None:
        L['balance_checks'].append(dict(at=now, balance=balance, ok=balance >= GUARD))
        print('balance %.2f: %s' % (balance, 'OK' if balance >= GUARD else 'BELOW %d: STOP' % GUARD))
        rc = 0 if balance >= GUARD else 3
    if ident and cost is not None:
        after = L['spent_credits'] + cost
        if after > BUDGET + 1e-9:
            print('REFUSED: %s costs %.3f, spent %.3f, would be %.3f > %.0f' % (ident, cost, L['spent_credits'], after,
                                                                               BUDGET))
            rc = 2
        elif preflight:
            print('preflight %s %.3f: OK (spent %.3f -> %.3f of %.0f)' % (ident, cost, L['spent_credits'], after,
                                                                          BUDGET))
        else:
            L['requests'].append(dict(at=now, id=ident, cost=cost, job=job, note=note))
            L['spent_credits'] = round(after, 4)
            print('recorded %s %.3f: spent %.3f of %.0f' % (ident, cost, after, BUDGET))
    if note and not ident:
        L['log'].append(dict(at=now, event='note', detail=note))
    json.dump(L, open(p, 'w'), ensure_ascii=False, indent=1)
    return rc


# ------------------------------------------------------------------------------------------------ pron
def inner_gap(x, t0, t1):
    """Longest silence between voiced runs inside [t0, t1] (s) of a 48 kHz take."""
    runs = [r for r in V.voiced_runs(x) if r[1] > t0 and r[0] < t1]
    gaps = [b[0] - a[1] for a, b in zip(runs, runs[1:])]
    return round(max(gaps), 3) if gaps else 0.0


def cmd_pron(raw, work):
    res, use, notes = [], {}, []
    for p in PRON:
        f = pick_take(raw, work, p['id'])
        if not f:
            res.append(dict(id=p['id'], missing=True))
            continue
        x = V.decode(f)
        x16 = to16(x)
        r = dict(id=p['id'], take=os.path.basename(f), text=p['text'], why=p['why'], dur=round(len(x) / SR, 3),
                 asr=[], words=[])
        heards = {}
        for model in ('small', 'medium'):
            txt, heard = whisper(x16, model=model)
            heards[model] = heard
            r['asr'].append(dict(model=model, heard=txt, cer=round(cer(loan_map(txt), p['text']), 3)))
        for w in p['words']:
            ms = []
            for model in ('small', 'medium'):
                m, sc, span = best_match(w, heards[model])
                ms.append(dict(model=model, heard=m, sim=sc, span=span))
            best = max(ms, key=lambda m: m['sim'])
            item = dict(word=w, heard=[(m['model'], m['heard'], m['sim']) for m in ms], best=best['sim'],
                        verdict='ok' if best['sim'] >= KW_OK else 'fail',
                        listen='़' in unicodedata.normalize('NFD', w))
            if best['span']:
                item['dur'] = round(best['span'][1] - best['span'][0], 3)
                if w in ('कंट्रोल-एस', 'कंट्रोल'):
                    item['inner_gap'] = inner_gap(x, *best['span'])
            r['words'].append(item)
        res.append(r)
        print(json.dumps(r, ensure_ascii=False), flush=True)
    W = {w['word']: w for r in res for w in r.get('words', [])}
    # decisions (SCRIPT 9 accept-if rules); nukta sounds (z, kh) cannot be judged by ASR: a listener confirms them
    if 'सब्र' in W:
        s = W['सब्र']
        if s['verdict'] != 'ok' or s.get('dur', 0) > 0.35:
            if W.get('सबर', {}).get('verdict') == 'ok':
                use['सब्र'] = 'सबर'
            notes.append('sabr: %s, %.3f s heard as %s' % (s['verdict'], s.get('dur', -1), s['heard']))
    if 'कंट्रोल-एस' in W:
        c = W['कंट्रोल-एस']
        if c['verdict'] != 'ok' or c.get('inner_gap', 0) > 0.12:
            use['कंट्रोल-एस'] = 'कंट्रोल एस'
            notes.append('Ctrl+S: %s, inner gap %.3f s: P-ctrl (two tokens, ROM "Ctrl S")' % (c['verdict'],
                                                                                              c.get('inner_gap', -1)))
    if W.get('ख़ुद', {}).get('verdict') == 'fail' and W.get('खुद', {}).get('verdict') == 'ok':
        use['ख़ुद'] = 'खुद'
    for prim in ('एडिटिंग', 'मोहल्ला', 'सेकंड'):
        if W.get(prim, {}).get('verdict') == 'fail':
            use[prim] = FALLBACK[prim]
            notes.append('%s failed the carrier check: line text uses %s (untested fallback)' % (prim, FALLBACK[prim]))
    out = dict(use=use, notes=notes, listen=[w for w, v in W.items() if v['listen']],
               rule='SCRIPT 9 accept-if; ASR folds nuktas, so z / kh need a listener')
    json.dump(res, open(os.path.join(work, 'pron_check.json'), 'w', encoding='utf8'), ensure_ascii=False, indent=1)
    json.dump(out, open(os.path.join(work, 'spelling.json'), 'w', encoding='utf8'), ensure_ascii=False, indent=1)
    print('spelling.json:', json.dumps(out, ensure_ascii=False))
    return res


# ------------------------------------------------------------------------------------------------ process
def proc_path(work, take, speed):
    return os.path.join(work, 'proc', '%s_%.2f.wav' % (os.path.splitext(os.path.basename(take))[0], speed))


def run_chain(work, take, dev, rom, speed, force=False):
    out = proc_path(work, take, speed)
    rep_p = os.path.splitext(out)[0] + '.report.json'
    if not force and os.path.exists(rep_p) and os.path.getmtime(rep_p) > os.path.getmtime(take):
        return json.load(open(rep_p))
    os.makedirs(os.path.dirname(out), exist_ok=True)
    return V.process(take, dev, rom, out=out, speed=speed)


SPLIT_DBFS = -45.0     # level that separates two lines cut out of one take (Clip.gap_after)
VOICE_DBFS = -55.0     # absolute voiced threshold (20 ms RMS, dBFS) for clips and stems: every line is mastered to
                       # -16 LUFS, so one level measures them all alike (vo_chain.voiced_runs adapts to each file's
                       # 10th percentile, which sits inside the speech on a tightly cut line and shortens its span)


def runs_abs(x, thr_db=VOICE_DBFS, win=0.02, hop=0.01, close=0.08, min_run=0.03):
    """[(t0, t1)] voiced runs above an absolute RMS level (same windows and gap closing as vo_chain.voiced_runs)."""
    n, h = int(win * SR), int(hop * SR)
    x = np.asarray(x, np.float32)
    if len(x) < n:
        return []
    fr = np.lib.stride_tricks.sliding_window_view(x, n)[::h]
    v = 10 * np.log10(np.mean(fr.astype(np.float64) ** 2, axis=1) + 1e-12) > thr_db
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


class Clip:
    """A processed line: 48 kHz float audio + its word list (clip time)."""

    def __init__(self, x, words):
        self.x = np.asarray(x, np.float32).copy()
        self.words = [dict(w) for w in words]

    @property
    def runs(self):
        return runs_abs(self.x)

    @property
    def dur(self):
        return len(self.x) / SR

    def span(self):
        r = self.runs
        return (r[0][0], r[-1][1]) if r else (0.0, self.dur)

    def gap_after(self, i, thr_db=SPLIT_DBFS):
        """The silence between token i and i+1: the longest gap between runs above `thr_db` inside
        [start_i, end_i+1]. A stricter level than VOICE_DBFS, so a breath / release tail that joins two sentences
        (-45 to -60 dBFS) is cut away instead of travelling with the next line."""
        a, b = self.words[i]['start'], self.words[i + 1]['end']
        best = None
        runs = runs_abs(self.x, thr_db)
        for (p0, p1), (q0, q1) in zip(runs, runs[1:]):
            if p1 >= a and q0 <= b and q0 > p1 and (best is None or q0 - p1 > best[1] - best[0]):
                best = (p1, q0)
        return best

    def split_after(self, i, pad=0.04, fade=0.01):
        """Split in the pause after token i -> (clip1, clip2); each keeps <= `pad` s of silence at the cut."""
        g = self.gap_after(i)
        if not g:
            mid = 0.5 * (self.words[i]['end'] + self.words[i + 1]['start'])
            g = (mid, mid)
        a1, b0 = g
        c1 = int(round(min(a1 + pad, (a1 + b0) / 2) * SR))
        c2 = int(round(max(b0 - pad, (a1 + b0) / 2) * SR))
        nf = int(fade * SR)
        x1, x2 = self.x[:c1].copy(), self.x[c2:].copy()
        if len(x1) > nf:
            x1[-nf:] *= np.linspace(1, 0, nf, dtype=np.float32)
        if len(x2) > nf:
            x2[:nf] *= np.linspace(0, 1, nf, dtype=np.float32)
        w1 = [dict(w) for w in self.words[:i + 1]]
        w2 = [dict(w, start=round(w['start'] - c2 / SR, 3), end=round(w['end'] - c2 / SR, 3))
              for w in self.words[i + 1:]]
        for w in w1:
            w['end'] = min(w['end'], round(c1 / SR, 3))
        for w in w2:
            w['start'] = max(w['start'], 0.0)
        return Clip(x1, w1), Clip(x2, w2)

    def snap_first(self, look=0.10):
        """A word that starts in the silence just before the clip's first voiced onset (vo_chain snaps to the
        voiced runs of the whole take; a cut-out line is measured on its own) starts on that onset. In place."""
        s0 = self.span()[0]
        for w in self.words:
            if w['start'] < s0 and s0 - w['start'] <= look:
                w['start'] = round(s0, 3)
                w['end'] = max(w['end'], round(s0 + 0.05, 3))
        return self

    def sub(self, i0, i1):
        """Tokens i0..i1 (a line out of a grouped take)."""
        c = self
        if i1 < len(c.words) - 1:
            c = c.split_after(i1)[0]
        if i0 > 0:
            c = c.split_after(i0 - 1)[1]
        return c


def line_clip(raw, work, lines, lid, speed, use, force=False):
    """Processed clip of one line at `speed` (cut out of its grouped take if it has no take of its own)."""
    src = source_for(raw, work, lid)
    if not src:
        raise FileNotFoundError('no take for %s in %s' % (lid, raw))
    take = src[1]
    ids = [lid] if src[0] == 'line' else src[3]
    dev, rom, ranges = tokens_for_take(work, take, lines, ids, use)
    rep = run_chain(work, take, dev, rom, speed, force)
    p = proc_path(work, take, speed)
    words = json.load(open(os.path.splitext(p)[0] + '.words.json', encoding='utf8'))
    c = Clip(V.decode(p), words)
    if src[0] == 'group':
        c = c.sub(*ranges[lid])
    c.snap_first()
    for i, w in enumerate(c.words):
        w['i'] = i
    return c, rep, take, dev[ranges[lid][0]:ranges[lid][1] + 1]


def score_clip(c, dev_text, kw_idx, model='small'):
    """CER (no initial prompt: unbiased) + the keyword heard in the free transcript."""
    txt, heard = whisper(to16(c.x), model=model)
    m, sc, _ = best_match(V.tokens(dev_text)[kw_idx], heard) if kw_idx is not None else (None, None, None)
    return dict(model=model, heard=txt, cer_raw=round(cer(txt, dev_text), 3), cer=round(cer(loan_map(txt), dev_text), 3),
                kw_heard=m, kw_sim=sc)


def cmd_process(raw, work, only=None, force=False):
    d, lines = load_lines(work)
    use = load_spelling(work)
    state_p = os.path.join(work, 'lines.json')
    state = json.load(open(state_p, encoding='utf8')) if os.path.exists(state_p) else {}
    for lid in LINES:
        if only and lid not in only:
            continue
        if not source_for(raw, work, lid):
            print(lid, 'no take in', raw)
            continue
        t0 = time.time()
        sp = PLAN[lid]['speeds'][0]
        pl = os.path.join(work, 'placement.json')
        if os.path.exists(pl):                     # measure the take at the speed the placement chose
            P = json.load(open(pl, encoding='utf8'))['placement']
            key = next((k for k in P if k.split('.')[0] == lid), None)
            if key:
                sp = P[key]['speed']
        c, rep, take, dev = line_clip(raw, work, lines, lid, sp, use, force)
        dev_text = ' '.join(dev)
        rom = line_tokens(lines, lid, use)[1]
        kw = next((i for i, r in enumerate(rom) if r.startswith('*')), None)
        asr = [score_clip(c, dev_text, kw), score_clip(c, dev_text, kw, 'medium')]   # two independent ears
        best = min(a['cer'] for a in asr)
        kw_ok = kw is None or (c.words[kw]['ok'] and max(a['kw_sim'] or -1 for a in asr) >= KW_OK)
        s0, s1 = c.span()
        nw = len(dev)
        state[lid] = dict(take=os.path.relpath(take, REPO), source=source_for(raw, work, lid)[0],
                          take_dur=round(len(V.decode(take)) / SR, 3), speed=sp, dev=dev_text,
                          heard=asr[0]['heard'], cer_raw=asr[0]['cer_raw'], cer=asr[0]['cer'], cer_best=best,
                          asr=asr, keyword=dict(i=kw, word=c.words[kw]['word'] if kw is not None else None,
                                                aligned_ok=c.words[kw]['ok'] if kw is not None else None,
                                                heard=[(a['model'], a['kw_heard'], a['kw_sim']) for a in asr],
                                                ok=kw_ok),
                          matched='%d/%d' % (sum(w['ok'] for w in c.words), len(c.words)),
                          unmatched=[(w['word'], w['heard']) for w in c.words if not w['ok']],
                          speech_s=round(s1 - s0, 3), words=nw, wps=round(nw / max(1e-3, s1 - s0), 2),
                          chain=dict(speed=rep['speed'], raw_dur=rep['raw_dur'], final_dur=rep['final_dur'],
                                     lufs=rep['loudness']['lufs'], tp=rep['loudness']['tp'], pauses=rep['pauses'],
                                     stretch=rep['chain']['stretch']),
                          listen=[t for t in dev if '़' in unicodedata.normalize('NFD', t)],
                          retake=bool(best > CER_MAX or not kw_ok), seconds=round(time.time() - t0, 1))
        print(lid, json.dumps({k: state[lid][k] for k in ('cer', 'cer_best', 'matched', 'speech_s', 'wps', 'retake',
                                                          'heard')}, ensure_ascii=False), flush=True)
        json.dump(state, open(state_p, 'w', encoding='utf8'), ensure_ascii=False, indent=1)
    return state


# ------------------------------------------------------------------------------------------------ candidates
# Every take recorded for a line (its own takes and the grouped takes it can be cut from), measured at one speed so
# the best fitting take with a clean CER can be chosen into select.json. Group takes: T2m = T2 with the SCRIPT 9
# fallback spelling मुहल्ला; T4p = T4 with "दबाती है," (DEV punctuation only).
CANDS = {
    'V1': [('TA_r1.mp3', 'TA'), ('TA_r2.mp3', 'TA'), ('TA_r3.mp3', 'TA'), ('TA_r4.mp3', 'TA'), ('TA_r5.mp3', 'TA'),
           ('V1_r1.mp3', None), ('V1_r2.mp3', None)],
    'V2': [('TA_r1.mp3', 'TA'), ('TA_r2.mp3', 'TA'), ('TA_r3.mp3', 'TA'), ('TA_r4.mp3', 'TA'), ('TA_r5.mp3', 'TA'),
           ('V2_r1.mp3', None), ('V2_r2.mp3', None), ('V2_r3.mp3', None)],
    'V1B': [('V1B_r1.mp3', None), ('V1B_r2.mp3', None), ('V1Bc_r1.mp3', None), ('V1Bc_r2.mp3', None)],
    'V3a': [('T2m_r1.mp3', 'T2'), ('T2m_r2.mp3', 'T2'), ('T2m_r3.mp3', 'T2'), ('V3a_r1.mp3', None), ('V3a_r2.mp3', None)],
    'V3b': [('T2m_r1.mp3', 'T2'), ('T2m_r2.mp3', 'T2'), ('T2m_r3.mp3', 'T2'), ('V3bm_r1.mp3', None), ('V3b_r1.mp3', None),
            ('V3b_r2.mp3', None)],
    'V4': [('T2m_r1.mp3', 'T2'), ('T2m_r2.mp3', 'T2'), ('T2m_r3.mp3', 'T2'), ('T2_r1.mp3', 'T2'), ('V4_r1.mp3', None)],
    'V5': [('T3_r1.mp3', 'T3'), ('V5_r1.mp3', None)],
    'V6': [('T3_r1.mp3', 'T3'), ('V6_r1.mp3', None)],
    'V7': [('V7_r1.mp3', None), ('V7_r2.mp3', None), ('T4_r1.mp3', 'T4'), ('T4_r2.mp3', 'T4'), ('T4_r3.mp3', 'T4'),
           ('T4p_r1.mp3', 'T4'), ('T4p_r2.mp3', 'T4')],
    'V8': [('T4_r1.mp3', 'T4'), ('T4_r2.mp3', 'T4'), ('T4_r3.mp3', 'T4'), ('T4p_r1.mp3', 'T4'), ('T4p_r2.mp3', 'T4'),
           ('V8_r1.mp3', None), ('V8_r2.mp3', None)],
    'V9': [('T4_r1.mp3', 'T4'), ('T4_r2.mp3', 'T4'), ('T4_r3.mp3', 'T4'), ('T4p_r1.mp3', 'T4'), ('T4p_r2.mp3', 'T4'),
           ('V9_r1.mp3', None), ('V9_r2.mp3', None), ('V9_r3.mp3', None)],
    'V10': [('T5_r1.mp3', 'T5'), ('T5_r2.mp3', 'T5'), ('V10_r1.mp3', None), ('V10c_r1.mp3', None),
            ('V10c_r2.mp3', None), ('T5f3_r1.mp3', 'T5', 'F3'), ('T5f3_r2.mp3', 'T5', 'F3')],
    'V11': [('T5_r1.mp3', 'T5'), ('T5_r2.mp3', 'T5'), ('V11_r1.mp3', None), ('T5f3_r1.mp3', 'T5', 'F3'),
            ('T5f3_r2.mp3', 'T5', 'F3')],
    'V12': [('V12_r1.mp3', None), ('V12_r2.mp3', None)],
}


def cand_clip(raw, work, lines, lid, fname, group, speed, use, force=False):
    take = os.path.join(raw, fname)
    ids = GROUPS[group] if group else [lid]
    dev, rom, ranges = tokens_for_take(work, take, lines, ids, use)
    rep = run_chain(work, take, dev, rom, speed, force)
    pth = proc_path(work, take, speed)
    c = Clip(V.decode(pth), json.load(open(os.path.splitext(pth)[0] + '.words.json', encoding='utf8')))
    if group:
        c = c.sub(*ranges[lid])
    return c, rep, dev[ranges[lid][0]:ranges[lid][1] + 1]


def cmd_cands(raw, work, only=None, speed=1.10, models=('small', 'medium')):
    """-> <work>/cands.json: per line and candidate take: speech span at `speed` (and scaled to 1.08 / 1.06), the
    anchor word's offset from the span start, CER per whisper model (no prompt), keyword heard."""
    d, lines = load_script()
    use = load_spelling(work)
    out_p = os.path.join(work, 'cands.json')
    res = json.load(open(out_p, encoding='utf8')) if os.path.exists(out_p) else {}
    for lid, cl in CANDS.items():
        if only and lid not in only:
            continue
        ai = PLAN[lid]['anchor'][0]
        res[lid] = []
        for cand in cl:
            fname, group = cand[:2]
            var = cand[2] if len(cand) > 2 else None
            lns = with_variant(lines, var) if var else lines
            rom = lns[lid]['tokens']
            kw = next((i for i, r in enumerate(rom) if r.startswith('*')), None)
            c, rep, dev = cand_clip(raw, work, lns, lid, fname, group, speed, use)
            s0, s1 = c.span()
            r = dict(take=fname, group=group, variant=var, speed=speed, dev=' '.join(dev), span=round(s1 - s0, 3),
                     span_108=round((s1 - s0) * speed / 1.08, 3), span_106=round((s1 - s0) * speed / 1.06, 3),
                     anchor_off=round(c.words[ai]['start'] - s0, 3), tail_after_anchor=round(s1 - c.words[ai]['start'], 3))
            if lid == 'V1B':
                b1, b2 = c.split_after(PLAN['V1B']['split'])
                r['part1'] = round(b1.span()[1] - b1.span()[0], 3)
                r['part2'] = round(b2.span()[1] - b2.span()[0], 3)
            for m in models:
                a = score_clip(c, ' '.join(dev), kw, m)
                r['cer_' + m] = a['cer']
                r['heard_' + m] = a['heard']
                r['kw_' + m] = (a['kw_heard'], a['kw_sim'])
            res[lid].append(r)
            print(lid, json.dumps(r, ensure_ascii=False), flush=True)
        json.dump(res, open(out_p, 'w', encoding='utf8'), ensure_ascii=False, indent=1)
    return res


# ------------------------------------------------------------------------------------------------ placement
def solve(items):
    """items: [dict(id, s, e, lo, hi, start_min, end_max, target)] in time order, offsets s <= 0 <= e relative to the
    anchor onset. Chain rule: start_i >= end_{i-1} + GAP_MIN. -> (anchors, feasible)."""
    n = len(items)
    L = [max(it['lo'], it.get('start_min', -1e9) - it['s']) for it in items]
    U = [min(it['hi'], it.get('end_max', 1e9) - it['e']) for it in items]
    lb, ub = L[:], U[:]
    for i in range(1, n):
        lb[i] = max(lb[i], lb[i - 1] + items[i - 1]['e'] + GAP_MIN - items[i]['s'])
    for i in range(n - 2, -1, -1):
        ub[i] = min(ub[i], ub[i + 1] + items[i + 1]['s'] - GAP_MIN - items[i]['e'])
    ok = all(a <= b + 1e-9 for a, b in zip(lb, ub))
    out = []
    for i, it in enumerate(items):
        lo = lb[i] if i == 0 else max(lb[i], out[-1] + items[i - 1]['e'] + GAP_MIN - it['s'])
        targets = [it['target']] + [a[0] for a in it.get('alts', [])]
        a = None
        for t in targets:                             # the first target that fits wins (V9: the presses in order)
            if lo - 1e-9 <= t <= ub[i] + 1e-9:
                a = t
                break
        if a is None:
            a = min(max(it['target'], lo), ub[i]) if lo <= ub[i] + 1e-9 else lo
        out.append(round(a, 3))
    return out, ok


def chain_items(clips, ids, plan_over=None):
    items = []
    for lid in ids:
        P = dict(PLAN[lid.split('.')[0]])
        if plan_over and lid in plan_over:
            P.update(plan_over[lid])
        c, ai = clips[lid]
        s0, s1 = c.span()
        a0 = c.words[ai]['start']
        _, tgt, lo, hi = P['anchor']
        items.append(dict(id=lid, s=round(s0 - a0, 3), e=round(s1 - a0, 3), lo=lo, hi=hi, target=tgt,
                          start_min=P.get('start_min', -1e9), end_max=P.get('end_max', 1e9),
                          alts=P.get('alts', [])))
    return items


def place_chain(clips, ids, plan_over=None):
    """Anchors for a chain; when infeasible, the soft ends (soft_end) are dropped one by one from the end of the
    chain (reported). -> (anchors, items, relaxed ids, feasible)."""
    items = chain_items(clips, ids, plan_over)
    an, ok = solve(items)
    relaxed = []
    if not ok:
        for it in reversed(items):
            if PLAN[it['id'].split('.')[0]].get('soft_end'):
                it['end_max'] = 1e9
                relaxed.append(it['id'])
                an, ok = solve(items)
                if ok:
                    break
    return an, items, relaxed, ok


def lufs_tp(x):
    p = os.path.join(os.environ.get('TMPDIR', '/tmp'), 'bcg_vo_meas_%d.wav' % os.getpid())
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
    m = lufs_tp(y)
    g = LUFS - m['lufs']
    z = y * np.float32(10 ** (g / 20))
    info = dict(pre=m, gain_db=round(g, 2), limiter=False)
    if m['tp'] + g > TP_MAX - 0.2:
        z = limit(z, TP_MAX - 0.4)
        info['limiter'] = True
        m2 = lufs_tp(z)
        z = z * np.float32(10 ** ((LUFS - m2['lufs']) / 20))
        if lufs_tp(z)['tp'] > TP_MAX:
            z = limit(z, TP_MAX - 0.5)
    V.write_wav(path, z)
    info['post'] = V.ebur128(path)
    return z, info


def cmd_assemble(raw, work, md, label):
    d, lines = load_lines(work)
    use = load_spelling(work)
    sp_ = os.path.join(work, 'lines.json')
    state = json.load(open(sp_, encoding='utf8')) if os.path.exists(sp_) else {}
    notes, speeds, clips, devs, reps = [], {}, {}, {}, {}

    def load(lid, sp):
        c, rep, take, dev = line_clip(raw, work, lines, lid, sp, use)
        speeds[lid], devs[lid], reps[lid] = sp, dev, rep
        return c

    # --- hook A: V1 then V2 (V2's measured length picks the SLATE placement or the fix-5 fallback)
    for lid in LINES:
        clips[lid] = load(lid, PLAN[lid]['speeds'][0])
    v2 = clips['V2']
    a0 = v2.words[0]['start']
    d2 = round(v2.span()[1] + 0.02 - a0, 3)
    v2_over = None
    if d2 > 0.43:
        v2_over = {'V2': dict(PLAN['V2']['fallback'])}
        notes.append('V2 measures %.3f s (> 0.43): placed at the GATE fix-5 fallback 1.550 between the beep pairs '
                     '(needs the lead OK, a SLATE 3.2 deviation)%s' % (d2, '; > 0.45 s: retake or accept (lead)' if
                                                                         d2 > 0.45 else ''))
    hook_a = {k: (clips[k], anchor_index(lines, k, use)) for k in ('V1', 'V2')}
    anA, itA, relA, okA = place_chain(hook_a, ['V1', 'V2'], v2_over)
    # V1 overrun ladder (F1): the next speed in the list while V1 runs past its end limit (the beep at 1.333)
    for sp in PLAN['V1']['speeds'][PLAN['V1']['speeds'].index(speeds['V1']) + 1:]:
        if anA[0] + itA[0]['e'] <= PLAN['V1']['end_max'] + 1e-6:
            break
        clips['V1'] = load('V1', sp)
        hook_a['V1'] = (clips['V1'], anchor_index(lines, 'V1', use))
        notes.append('V1 re-processed at %.2fx (ladder F1)' % sp)
        anA, itA, relA, okA = place_chain(hook_a, ['V1', 'V2'], v2_over)
    # --- hook B: V1B split at the "..." pause; "yaad" placed on its own (the beep pair sits in the pause)
    p2 = PLAN['V1B']['part2']
    overB = {'V1B.1': dict(end_max=PLAN['V1B']['beep'][0]),
             'V1B.2': dict(anchor=(0, p2['anchor'][1], p2['anchor'][2], p2['anchor'][3]),
                           start_min=PLAN['V1B']['beep'][1] + 0.03, end_max=PLAN['V1B']['end_max'])}

    def hook_b_place():
        b1, b2 = clips['V1B'].split_after(PLAN['V1B']['split'])
        b1.snap_first()
        b2.snap_first()
        for i, w in enumerate(b2.words):
            w['i'] = i + PLAN['V1B']['split'] + 1
        hb = {'V1B.1': (b1, 0), 'V1B.2': (b2, 0)}
        return (hb,) + place_chain(hb, ['V1B.1', 'V1B.2'], overB)

    hook_b, anB, itB, relB, okB = hook_b_place()
    # V1B ladder (F1): next speed while "ye awaaz" runs into the beep pair or the chain does not fit
    for sp in PLAN['V1B']['speeds'][PLAN['V1B']['speeds'].index(speeds['V1B']) + 1:]:
        if okB and anB[0] + itB[0]['e'] <= PLAN['V1B']['beep'][0] + 1e-6:
            break
        clips['V1B'] = load('V1B', sp)
        notes.append('V1B re-processed at %.2fx (ladder F1)' % sp)
        hook_b, anB, itB, relB, okB = hook_b_place()
    # --- body: one chain V3a .. V12; a line that cannot fit tries its next speed (SCRIPT 6 ladder F1)
    drop = dropped(work)
    BODY_ = [k for k in BODY if k not in drop]
    if drop:
        notes.append('ladder F4: %s dropped from the VO (BRIEF 6.7; U3F `Saved · har 30 sec` carries it on screen)'
                     % ', '.join(drop))
    body = {k: (clips[k], anchor_index(lines, k, use)) for k in BODY_}
    anC, itC, relC, okC = place_chain(body, BODY_)
    tried = set()
    while True:
        bad = [it['id'] for it, a in zip(itC, anC) if a + it['e'] > it['end_max'] + 1e-6 or
               a + it['s'] < it['start_min'] - 1e-6 or not it['lo'] - 1e-6 <= a <= it['hi'] + 1e-6]
        bad += [itC[i + 1]['id'] for i in range(len(itC) - 1)
                if anC[i + 1] + itC[i + 1]['s'] < anC[i] + itC[i]['e'] + GAP_MIN - 1e-6]
        nxt = None
        for lid in list(dict.fromkeys(bad)) + (relC if relC else []):
            sps = PLAN[lid]['speeds']
            k = sps.index(speeds[lid]) if speeds[lid] in sps else 0
            if k + 1 < len(sps) and (lid, sps[k + 1]) not in tried:
                nxt = (lid, sps[k + 1])
                break
        if not nxt:
            break
        tried.add(nxt)
        clips[nxt[0]] = load(*nxt)
        body[nxt[0]] = (clips[nxt[0]], anchor_index(lines, nxt[0], use))
        notes.append('%s re-processed at %.2fx (ladder F1)' % nxt)
        anC, itC, relC, okC = place_chain(body, BODY_)
    if relC:
        notes.append('soft window ends dropped to fit: %s' % ', '.join(relC))
    if not okC:
        notes.append('body chain infeasible even after the ladder: misses reported below')

    # --- stems + words
    def put(y, c, anchor_t, ai):
        off = anchor_t - c.words[ai]['start']
        i0 = int(round(off * SR))
        if i0 < 0:
            raise ValueError('clip starts before 0')
        seg = c.x[:max(0, min(len(c.x), NSAMP - i0))]
        y[i0:i0 + len(seg)] += seg
        return off

    placed = {}
    for ids, an, its in ((['V1', 'V2'], anA, itA), (['V1B.1', 'V1B.2'], anB, itB), (BODY_, anC, itC)):
        for lid, a, it in zip(ids, an, its):
            c, ai = (hook_a.get(lid) or hook_b.get(lid) or body.get(lid))
            placed[lid] = dict(clip=c, ai=ai, anchor=a, it=it, start=round(a + it['s'], 3), end=round(a + it['e'], 3))
    stems = {}
    for ver, order in (('A', ['V1', 'V2'] + BODY_), ('B', ['V1B.1', 'V1B.2'] + BODY_)):
        y = np.zeros(NSAMP, np.float32)
        words = []
        for lid in order:
            P = placed[lid]
            off = put(y, P['clip'], P['anchor'], P['ai'])
            base = lid.split('.')[0]
            for w in P['clip'].words:
                ww = dict(word=('*' if w.get('keyword') else '') + w['word'] if False else w['word'],
                          start=round(w['start'] + off, 3), end=round(w['end'] + off, 3), keyword=bool(w['keyword']),
                          line=base, i=w['i'], dev=w.get('dev'), heard=w.get('heard'), ok=w.get('ok'))
                ww['hide'] = any(a <= ww['start'] < b for a, b in HIDE)
                words.append(ww)
        words.sort(key=lambda w: w['start'])
        path = os.path.join(work, 'vo_stem.wav' if ver == 'A' else 'vo_stem_B.wav')
        z, info = master(y, path)
        stems[ver] = dict(path=path, words=words, master=info, order=order)
        wp = os.path.join(work, 'words.json' if ver == 'A' else 'words_B.json')
        json.dump(words, open(wp, 'w', encoding='utf8'), ensure_ascii=False, indent=1)
        shutil.copyfile(path, os.path.join(work, 'bijli_chali_gayi_vo_%s.wav' % ver))
        shutil.copyfile(wp, os.path.join(work, 'bijli_chali_gayi_vo_%s.words.json' % ver))
    plc = {k: dict(start=v['start'], end=v['end'], anchor=v['anchor'], anchor_word=v['clip'].words[v['ai']]['word'],
                   speed=speeds[k.split('.')[0]], item=v['it']) for k, v in placed.items()}
    json.dump(dict(placement=plc, notes=notes, d2=d2, relaxed=dict(A=relA, B=relB, body=relC),
                   feasible=dict(A=okA, B=okB, body=okC)), open(os.path.join(work, 'placement.json'), 'w',
                                                                  encoding='utf8'), ensure_ascii=False, indent=1)
    chk = checks(stems, placed, state, speeds)
    json.dump(chk, open(os.path.join(work, 'check.json'), 'w', encoding='utf8'), ensure_ascii=False, indent=1)
    plot_timeline(stems, placed, os.path.join(work, 'timeline.png'))
    write_md(md, label, stems, placed, state, lines, chk, notes, speeds, d2, raw, work)
    print(json.dumps(chk['summary'], ensure_ascii=False, indent=1))
    return chk


# ------------------------------------------------------------------------------------------------ checks + report
def targets(lid):
    P = PLAN[lid]
    return P['win'], P['anchor'][1]


def checks(stems, placed, state, speeds):
    fails, warn = [], []
    rows = {}
    for lid in LINES:
        parts = [k for k in placed if k.split('.')[0] == lid]
        if not parts:
            continue
        st = min(placed[k]['start'] for k in parts)
        en = max(placed[k]['end'] for k in parts)
        main = placed[parts[0]]
        P = PLAN[lid]
        win = P['win']
        if lid == 'V2' and main['anchor'] < 2.0:
            win = P['fallback']['win']
        _, tgt, lo, hi = P['anchor']
        if lid == 'V2' and main['anchor'] < 2.0:
            _, tgt, lo, hi = P['fallback']['anchor']
        a = main['anchor']
        r = dict(start=st, end=en, anchor=a, anchor_target=tgt, d_anchor=round(a - tgt, 3),
                 d_start=round(st - win[0], 3), d_end=round(en - win[1], 3), win=win)
        miss = []
        if not lo - 1e-6 <= a <= hi + 1e-6:
            miss.append('anchor %.3f outside %.3f-%.3f' % (a, lo, hi))
        if abs(r['d_anchor']) > 0.3:
            miss.append('anchor %.3f s from target' % r['d_anchor'])
        if r['d_end'] > 0.3:
            miss.append('ends %.3f s after the window' % r['d_end'])
        if r['d_start'] < -0.3:
            miss.append('starts %.3f s before the window' % -r['d_start'])
        if P.get('bold_anchor') and not P['bold_anchor'][0] - 1e-6 <= a <= P['bold_anchor'][1] + 1e-6:
            ba = P['bold_anchor']
            miss.append('BOLD anchor %.3f outside %.3f-%.3f (%+.3f s)' % (a, ba[0], ba[1], a - ba[1] if a > ba[1]
                                                                          else a - ba[0]))
        if P.get('bold') == 'start' and abs(r['d_start']) > 0.03:
            miss.append('BOLD start off by %.3f s' % r['d_start'])
        if P.get('bold') == 'end' and en > win[1] + 0.02:
            miss.append('BOLD end passed by %.3f s' % (en - win[1]))
        r['miss'] = miss
        rows[lid] = r
        if miss:
            warn.append('%s: %s' % (lid, '; '.join(miss)))
    if rows.get('V1') and rows['V1']['start'] > 0.13:
        fails.append('V1 onset %.3f > 0.13' % rows['V1']['start'])
    if rows.get('V1B') and rows['V1B']['start'] > 0.33:
        fails.append('V1B onset %.3f > 0.33' % rows['V1B']['start'])
    if rows.get('V1') and rows['V1']['end'] > 1.333:
        fails.append('V1 runs into the beep at 1.333 (ends %.3f)' % rows['V1']['end'])
    if rows.get('V4') and rows['V4']['end'] > 7.85:
        fails.append('V4 ends %.3f > 7.85 (slam)' % rows['V4']['end'])
    if rows.get('V10') and rows['V10']['end'] > 26.30 + 0.02:
        fails.append('V10 ends %.3f > 26.30 (drop-out)' % rows['V10']['end'])
    if rows.get('V12') and rows['V12']['end'] > 34.17:
        fails.append('V12 ends %.3f > 34.17' % rows['V12']['end'])
    b1, b2 = placed.get('V1B.1'), placed.get('V1B.2')
    if b1 and b2 and not (b1['end'] <= 1.333 + 0.01 and b2['start'] >= 1.537):
        warn.append('hook B: the beep pair 1.333-1.537 is not inside the "..." pause (%.3f-%.3f)' % (b1['end'],
                                                                                                b2['start']))
    out = dict(rows=rows, stems={})
    for ver, s in stems.items():
        x = V.decode(s['path'])
        L = s['master']['post']
        info = subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'stream=sample_rate,channels,bits_per_raw_sample,'
                               'duration_ts', '-of', 'json', s['path']], capture_output=True, text=True).stdout
        pi = json.loads(info)['streams'][0]
        f = []
        if int(pi['sample_rate']) != SR or int(pi['channels']) != 1:
            f.append('format %s' % pi)
        if len(x) != NSAMP:
            f.append('length %d samples != %d' % (len(x), NSAMP))
        if abs(L['lufs'] - LUFS) > 0.5:
            f.append('loudness %.2f LUFS' % L['lufs'])
        if L['tp'] > TP_MAX:
            f.append('true peak %.2f dBTP' % L['tp'])
        runs = runs_abs(x)
        for a, b, why in NO_VO:
            hit = [(round(r0, 3), round(r1, 3)) for r0, r1 in runs if r1 > a + 0.01 and r0 < b - 0.01]
            if hit:
                (f if why.startswith('designed') else warn).append('%s: voice in %.3f-%.3f (%s): %s' % (ver, a, b, why,
                                                                                                       hit))
        W = s['words']
        if any(b['start'] < a['start'] for a, b in zip(W, W[1:])):
            f.append('word starts not monotone')
        on = np.mean([any(r0 - 0.03 <= w['start'] <= r1 for r0, r1 in runs) for w in W])
        if on < 0.9:
            f.append('only %.0f %% of word starts on voice' % (100 * on))
        order = s['order']
        for p, q in zip(order, order[1:]):
            g = placed[q]['start'] - placed[p]['end']
            if g < GAP_MIN - 0.005:
                f.append('%s -> %s gap %.3f < %.2f' % (p, q, g, GAP_MIN))
        kws = sum(w['keyword'] for w in W)
        out['stems'][ver] = dict(path=os.path.relpath(s['path'], REPO), lufs=L['lufs'], tp=L['tp'], lra=L['lra'],
                                 samples=len(x), sr=int(pi['sample_rate']), bits=pi.get('bits_per_raw_sample'),
                                 words=len(W), keywords=kws, starts_on_voice=round(float(on), 3),
                                 vo_first=round(runs[0][0], 3) if runs else None,
                                 vo_last=round(runs[-1][1], 3) if runs else None,
                                 speech_s=round(sum(b - a for a, b in runs), 3), gain_db=s['master']['gain_db'],
                                 limiter=s['master']['limiter'], fails=f)
        fails += ['%s: %s' % (ver, e) for e in f]
    used = set(k.split('.')[0] for k in placed)
    cer_bad = [(k, v['cer_best']) for k, v in state.items() if k in used and v['cer_best'] > CER_MAX]
    kw_bad = [(k, v['keyword']['word']) for k, v in state.items() if k in used and not v['keyword']['ok']]
    if cer_bad:
        warn.append('CER > %.2f: %s' % (CER_MAX, cer_bad))
    if kw_bad:
        warn.append('keyword not heard: %s' % kw_bad)
    out['summary'] = dict(fails=fails, warnings=warn, retake=[k for k, v in state.items() if k in used and v['retake']],
                          speeds={k: v for k, v in speeds.items()})
    return out


def plot_timeline(stems, placed, path):
    try:
        import cv2
    except ImportError:
        return
    W, H = 1800, 420
    img = np.full((H, W, 3), (14, 10, 8), np.uint8)
    sx = lambda t: int(40 + (W - 80) * t / DUR)
    for k in range(0, 53):                          # beats (90 BPM: 0.667 s)
        t = k * 20 / FPS
        cv2.line(img, (sx(t), 30), (sx(t), H - 30), (60, 50, 45) if k % 4 else (110, 90, 80), 1)
    for a, b, _ in NO_VO:
        cv2.rectangle(img, (sx(a), 30), (sx(b), H - 30), (30, 30, 70), -1)
    for row, (ver, s) in enumerate(stems.items()):
        x = V.decode(s['path'])
        y0 = 90 + row * 160
        env = np.abs(x[:len(x) // 480 * 480]).reshape(-1, 480).max(axis=1)
        for i, v in enumerate(env):
            t = i * 0.01
            h = int(55 * min(1.0, v / 0.5))
            cv2.line(img, (sx(t), y0 - h), (sx(t), y0 + h), (40, 120, 255), 1)
        for lid in s['order']:
            P = placed[lid]
            cv2.putText(img, lid, (sx(P['start']), y0 - 62), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (230, 240, 255), 1)
            base = lid.split('.')[0]
            if base in PLAN:
                at = P['anchor']
                cv2.line(img, (sx(at), y0 + 58), (sx(at), y0 + 70), (80, 220, 255), 2)
        cv2.putText(img, 'hook %s' % ver, (5, y0 + 5), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (200, 200, 200), 1)
    cv2.imwrite(path, img)


def syl(dev):
    """Rough Devanagari syllable count (vowel signs + independent vowels + consonants without virama/vowel sign)."""
    n = 0
    t = re.sub(r'[^ऀ-ॿ]', '', unicodedata.normalize('NFC', dev).replace('़', ''))
    for i, ch in enumerate(t):
        if 'अ' <= ch <= 'औ':
            n += 1
        elif 'क' <= ch <= 'ह' or 'क़' <= ch <= 'य़':
            nxt = t[i + 1] if i + 1 < len(t) else ''
            if nxt != '्' and not ('ा' <= nxt <= 'ौ'):
                n += 1
        elif 'ा' <= ch <= 'ौ':
            n += 1
    return n


def write_md(md, label, stems, placed, state, lines, chk, notes, speeds, d2, raw, work):
    R = chk['rows']
    L = []
    L.append('# VO_TIMING · Reel 2 · C11 · Bijli Chali Gayi (@jawad_mp4)')
    L.append('')
    L.append('%s, hinglish-scriptwriter, `pipeline/jawad_reels/bijli_chali_gayi_vo.py assemble` (measured; replaces '
             'the estimates of SCRIPT section 4). Voice: Higgsfield preset Vlad, `elevenlabs_v4`, Devanagari text; '
             'chain `vo_chain.py` per vo_config. Targets: BRIEF r2 section 6.7 (bold = may not move, the rest +-0.25 s).'
             % label)
    L.append('')
    for ver, s in chk['stems'].items():
        L.append('- **Stem %s** `%s`: %d samples (%.3f s) at %d Hz, %.2f LUFS integrated, %.2f dBTP, LRA %.1f LU, '
                 'VO %.3f-%.3f s, %.2f s of voiced speech, %d words (%d keywords), %.0f %% of word starts on voice; '
                 'gain %+.2f dB%s.' % (ver, s['path'], s['samples'], s['samples'] / SR, s['sr'], s['lufs'], s['tp'],
                                       s['lra'], s['vo_first'], s['vo_last'], s['speech_s'], s['words'], s['keywords'],
                                       100 * s['starts_on_voice'], s['gain_db'],
                                       ', limiter on' if s['limiter'] else ''))
    L.append('- Words: `%s/words.json` (A), `words_B.json` (B), and the BRIEF 6.14 names `bijli_chali_gayi_vo_A.words.json`'
             ' / `_B.words.json`; reel time, offset 0.' % os.path.relpath(work, REPO))
    L.append('- V2 "Yaad hai?" measured %.3f s (onset of याद to the end of है? + 20 ms): %s.' % (
        d2, 'SLATE placement 2.200 kept' if d2 <= 0.43 else 'GATE fix-5 fallback 1.550 (lead OK needed)'))
    L.append('')
    L.append('## Per-beat timing vs BRIEF r2 6.7')
    L.append('')
    L.append('| line | brief window (s) | placed t0 → t1 (s) | anchor word @ placed (target, Δ) | beat @ anchor | words · syl |'
             ' speech s | w/s | speed | CER (best) | misses > 0.3 s / bold |')
    L.append('|---|---|---|---|---|---|---|---|---|---|---|')
    for lid in LINES:
        if lid not in R:
            continue
        r = R[lid]
        st = state.get(lid, {})
        parts = [k for k in placed if k.split('.')[0] == lid]
        main = placed[parts[0]]
        aw = main['clip'].words[main['ai']]['word']
        beat = r['anchor'] * 90 / 60
        dev = ' '.join(lines[lid]['dev_tokens'])
        nw = len(lines[lid]['dev_tokens'])
        sp_s = sum(placed[k]['end'] - placed[k]['start'] for k in parts)
        L.append('| %s | %.3f-%.3f | %.3f → %.3f | %s @ %.3f (%.3f, %+.3f) | %.2f (f%.1f) | %d · %d | %.2f | %.2f | %.2f |'
                 ' %.3f%s | %s |' % (lid, r['win'][0], r['win'][1], r['start'], r['end'], aw, r['anchor'],
                                     r['anchor_target'], r['d_anchor'], beat, r['anchor'] * FPS, nw,
                                     lines[lid].get('syl') or syl(dev), sp_s,
                                     nw / max(1e-3, sp_s), speeds[lid], st.get('cer_best', -1),
                                     ' ⚑' if st.get('retake') else '', '; '.join(r['miss']) or 'none'))
    for lid in dropped(work):
        P = PLAN[lid]
        L.append('| %s | %.3f-%.3f | dropped (ladder F4) | - | - | %d · %s | - | - | - | %.3f (measured on `%s`) | not in '
                 'the VO |' % (lid, P['win'][0], P['win'][1], len(lines[lid]['dev_tokens']), lines[lid].get('syl', '-'),
                               state.get(lid, {}).get('cer_best', -1), os.path.basename(state.get(lid, {}).get('take', '-'))))
    L.append('')
    L.append('Flags: lines above 3.2 words/s: %s.' % (', '.join(
        lid for lid in LINES if lid in R and len(lines[lid]['dev_tokens']) / max(1e-3, R[lid]['end'] - R[lid]['start'])
        > 3.2) or 'none'))
    L.append('')
    L.append('## Takes, CER and keywords')
    L.append('')
    L.append('CER = character error rate of the free transcript (no initial prompt, so the ASR is not told the text) '
             'against the DEV text sent, after folding nuktas / candrabindu and spaces and mapping Latin loan words '
             '(whisper writes "editing" for एडिटिंग). Retake rule: best CER > %.2f or the keyword not heard.' % CER_MAX)
    L.append('')
    L.append('| line | take (source) | DEV sent | heard (whisper medium, no prompt) | CER small / medium / best | '
             'keyword heard | aligned | retake |')
    L.append('|---|---|---|---|---|---|---|---|')
    for lid in LINES:
        st = state.get(lid)
        if not st:
            continue
        kw = st['keyword']
        am = {a['model']: a for a in st['asr']}
        L.append('| %s | `%s` (%s) | %s | %s | %.3f / %.3f / %.3f | %s | %s | %s |' % (
            lid, os.path.basename(st['take']), st['source'], st['dev'], am.get('medium', am['small'])['heard'],
            am['small']['cer'], am.get('medium', am['small'])['cer'], st['cer_best'],
            ', '.join('%s: %s (%.2f)' % (m, h, s if s is not None else -1) for m, h, s in kw['heard']),
            st['matched'], 'YES' if st['retake'] else 'no'))
    L.append('')
    pc = os.path.join(work, 'pron_check.json')
    if os.path.exists(pc):
        P = json.load(open(pc, encoding='utf8'))
        L.append('## Pronunciation batch (SCRIPT 9 risk words in carrier phrases)')
        L.append('')
        L.append('| take | text sent | risk word | heard (medium) · CER | heard (small) · CER | verdict |')
        L.append('|---|---|---|---|---|---|')
        for r in P['rows']:
            L.append('| `%s` | %s | %s (%s) | %s · %.3f | %s · %.3f | %s |' % (
                os.path.basename(r['file']), r['text'], r['word'], r['caption'], r['heard_medium'], r['cer_medium'],
                r['heard_small'], r['cer_small'], r['verdict']))
        L.append('')
    cj = os.path.join(work, 'credits.json')
    if os.path.exists(cj):
        C = json.load(open(cj, encoding='utf8'))
        reqs = C.get('requests', [])
        bal = C.get('balance_checks', [])
        L.append('## Credits (Higgsfield, voice generation only)')
        L.append('')
        L.append('- %d requests submitted, **%.2f credits** of the reel budget %.0f (each preflighted with get_cost: 0.23 '
                 'credits up to 50 characters, 0.46 for 51-100); %d balance checks, lowest %.2f (guard %.0f). Ledger: '
                 '`%s`; every request with its job id and exact text: `%s`.' % (
                     len(reqs), sum(r['cost'] for r in reqs), C.get('budget_credits', BUDGET), len(bal),
                     min([b.get('credits', b.get('balance', 1e9)) for b in bal] or [0]), C.get('global_guard_min_balance', GUARD),
                     os.path.relpath(cj, REPO), os.path.relpath(os.path.join(work, 'requests.json'), REPO)))
        L.append('')
    dj = os.path.join(work, 'decisions.json')
    if os.path.exists(dj):
        D = json.load(open(dj, encoding='utf8'))
        for sec, items in D.items():
            L.append('## %s' % sec)
            L.append('')
            for it in items:
                L.append('- %s' % it)
            L.append('')
    L.append('## Notes and checks')
    L.append('')
    for n in notes:
        L.append('- %s' % n)
    for e in chk['summary']['fails']:
        L.append('- FAIL: %s' % e)
    for e in chk['summary']['warnings']:
        L.append('- warning: %s' % e)
    if not chk['summary']['fails']:
        L.append('- Stem checks pass (format, length, loudness, true peak, gaps >= %.2f s, monotone words, starts on '
                 'voice, designed silence 16.000-16.400).' % GAP_MIN)
    L.append('- Nukta sounds (आवाज़, ख़ुद) cannot be judged by ASR (whisper folds the nukta): a listener confirms them.')
    L.append('')
    os.makedirs(os.path.dirname(os.path.abspath(md)), exist_ok=True)
    open(md, 'w', encoding='utf8').write('\n'.join(L) + '\n')
    print('->', md)


# ------------------------------------------------------------------------------------------------ CLI
def main(argv=None):
    import argparse
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('cmd', choices=['requests', 'ledger', 'pron', 'process', 'assemble', 'cands'])
    ap.add_argument('--raw', default=os.path.join(RW, 'vo', 'raw'))
    ap.add_argument('--work', default=os.path.join(RW, 'vo'))
    ap.add_argument('--md', default=os.path.join(DESIGN, 'VO_TIMING.md'))
    ap.add_argument('--label', default=time.strftime('%Y-%m-%d', time.gmtime()))
    ap.add_argument('--lines', default='')
    ap.add_argument('--force', action='store_true')
    ap.add_argument('--plan', default='lines', choices=['lines', 'grouped'])
    ap.add_argument('--retake', default='', help='comma list of ids: append retake requests')
    ap.add_argument('--stability', type=float, default=None)
    ap.add_argument('--id')
    ap.add_argument('--cost', type=float)
    ap.add_argument('--job')
    ap.add_argument('--balance', type=float)
    ap.add_argument('--preflight', action='store_true')
    ap.add_argument('--note', default='')
    a = ap.parse_args(argv)
    only = [s for s in a.lines.split(',') if s]
    if a.cmd == 'requests':
        cmd_requests(a.work, a.plan, [s for s in a.retake.split(',') if s] or None, a.stability)
    elif a.cmd == 'ledger':
        return cmd_ledger(a.work, a.id, a.cost, a.job, a.balance, a.preflight, a.note)
    elif a.cmd == 'pron':
        cmd_pron(a.raw, a.work)
    elif a.cmd == 'process':
        cmd_process(a.raw, a.work, only or None, a.force)
    elif a.cmd == 'cands':
        cmd_cands(a.raw, a.work, only or None)
    else:
        cmd_assemble(a.raw, a.work, a.md, a.label)
    return 0


if __name__ == '__main__':
    sys.exit(main())
