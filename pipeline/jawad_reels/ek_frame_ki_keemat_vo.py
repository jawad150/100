"""ek_frame_ki_keemat_vo.py - C08 "Ek Frame ki Keemat" VO: Vlad (Higgsfield elevenlabs_v4) line takes -> vo_chain ->
the reel-time VO stems (hook A 33.6 s, hook B 0-3.0 s) + word timings + VO_TIMING.md.

Sources (binding): brand_reels/design/reels/ek_frame_ki_keemat/script.json (lines, DEV / ROM tokens, windows, anchors,
fit ladder = SCRIPT.md section 7) and BRIEF.md section 9. Only this reel's files are written; vo_chain is imported read-only.

    cd /home/user/100/pipeline/jawad_reels
    python3 -I ek_frame_ki_keemat_vo.py requests                  # -> <RW>/vo/requests.json (Higgsfield payloads)
    tools/heavy.sh python3 -I ek_frame_ki_keemat_vo.py pron       # whisper check of the carriers <raw>/efk_P*_t*.mp3
    tools/heavy.sh python3 -I ek_frame_ki_keemat_vo.py process    # each line take -> vo_chain (1.08x, 1.10x) + CER
    tools/heavy.sh python3 -I ek_frame_ki_keemat_vo.py assemble   # fit ladder, placement, stems, words, VO_TIMING.md
    options: --raw DIR (takes, default <RW>/vo/raw) --work DIR (outputs, default <RW>/vo) --md PATH (default the reel's
             VO_TIMING.md) --label TEXT --lines V2,V7 (process only these) --v10 usko|usey (C7; default usko)

Takes: <raw>/efk_<ID>_t<N>.mp3 (ID = V1A V1B V2 ... V10, V10K = the 'usey' fallback, P1-P4 = pronunciation carriers);
the highest N wins unless <work>/select.json maps an ID to a file name. <work>/spelling.json (optional) maps a DEV word to
the spelling the pronunciation check chose ({"फ़्रेम": "फ्रेम"}): applied to the requests AND to the alignment text.

Outputs in <work>: proc/<take>_<speed>.wav (+ .words.json / .report.json from vo_chain), lines.json (CER, keywords),
vo_stem.wav = ek_frame_ki_keemat_vo.wav (hook A, 33.600 s, 48 kHz 24-bit mono, -16.0 LUFS integrated, TP <= -2 dBTP),
words.json = ek_frame_ki_keemat_vo.words.json (reel time; snake_captions.load_words format + line / i / dev / heard / ok /
hide), ek_frame_ki_keemat_hookb_vo.wav (+ .words.json; 3.000 s, V1B at the A stem's gain), check.json, vo_timeline.png.
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
import vo_chain as V  # noqa: E402  (shared, read-only)

REPO = os.path.abspath(os.path.join(HERE, '..', '..'))
REEL = 'ek_frame_ki_keemat'
RW = os.path.join(REPO, 'workspace', 'jawad_reels', REEL)
DESIGN = os.path.join(REPO, 'brand_reels', 'design', 'reels', REEL)
SCRIPT_JSON = os.path.join(DESIGN, 'script.json')
SR = 48000
DUR = 33.6
NSAMP = int(round(DUR * SR))
HOOK_B_DUR = 3.0
BPM = 100.0
BEAT = 60.0 / BPM
LUFS, TP_MAX = -16.0, -2.0
CER_MAX = 0.15
VOICE_ID = 'e5666b9c-99a2-4fac-8b4e-abee078b186d'
PREFIX = 'efk'
SPLICE = 3.03            # no body VO before this (hook splice at 3.000 + 5 ms crossfade)
GAP_LINES = 0.15         # voice-to-voice gap between lines
GAP_WORDS = 0.05         # inside a split line (V3 words, V4 phrases)
MIN_HOLD = 0.25          # the "..." hold when a line is split at it (V2, V7, V9)
ORDER_A = ['V1A', 'V2', 'V3', 'V4', 'V5', 'V6', 'V7', 'V8', 'V9', 'V10']
ALL_LINES = ['V1A', 'V1B', 'V2', 'V3', 'V4', 'V5', 'V6', 'V7', 'V8', 'V9', 'V10']

# ------------------------------------------------------------------------------------------------ the plan
# SCRIPT.md section 7 (placement + fit ladder) on the script.json windows. limit = the end that triggers the next ladder
# step (min(hard end, next line - 0.15) where the script asks for it); hard = the failure line. Speeds: 1.08 baseline,
# 1.10 the ladder step (vo_config 1.06-1.10x; never above 1.10, never pitch).
PLAN = {
    'V1A': dict(mode='whole', onset=0.10, limit=2.70, hard=2.70),
    'V1B': dict(mode='whole', onset=0.10, limit=2.70, hard=2.70),
    'V2': dict(mode='anchor', onset=3.07, anchor=5, at=4.80, tol=0.10, split=4, part1_max=1.45, limit=5.85, hard=5.95),
    'V3': dict(mode='words', onsets=[6.00, 6.75, 7.30, 7.90], limit=8.45, hard=8.45, drop=1),
    'V4': dict(mode='phrases', onsets=[10.03, 10.95], onset2_alt=10.90, split=1, limit=11.70, hard=11.70),
    'V5': dict(mode='whole', onset=12.05, onset_alt=12.00, limit=15.85, hard=15.85, hold_cap=(2, 0.45),
               checks=[(4, 13.80, 0.15, 'bina ~ flick OFF f414'), (6, 14.45, 0.20, 'zinda ~ flick ON f432')]),
    'V6': dict(mode='whole', onset=16.95, limit=18.75, hard=18.85),
    'V7': dict(mode='anchor', onset=18.90, anchor=3, at=20.45, tol=0.10, split=2, limit=21.99, hard=21.99),
    'V8': dict(mode='whole', onset=22.15, limit=24.15, hard=24.15),
    'V9': dict(mode='anchor', onset=26.75, anchor=1, at=27.70, tol=0.10, split=0, limit=29.85, hard=29.85,
               hold_cap=(0, 0.45)),
    'V10': dict(mode='whole', onset=29.60, onset_max=29.85, limit=33.24, hard=33.35),
}
NEXT_ONSET = {'V1A': SPLICE, 'V1B': HOOK_B_DUR - 0.005}

# pronunciation carriers (step 1): every SCRIPT section 8 risk word in its script spelling (P1-P3) and the fallback
# spellings (P4, optional), each in a short natural phrase.
PRON = [
    dict(id='P1', text='तीन सौ साठ लेयर्स। एक फ़्रेम, तीस फ़्रेम्स।',
         words=['साठ', 'लेयर्स', 'फ़्रेम,', 'फ़्रेम्स।'], why='risks 1 (saath, never saat), 2 (frame / frames), 6 (layers)'),
    dict(id='P2', text='पलक झपकते। फ़्रेम ज़िंदा है। हर लफ़्ज़। धुआँ।',
         words=['झपकते।', 'ज़िंदा', 'लफ़्ज़।', 'धुआँ।'], why='risks 3 (jhapakte), 4 (zinda), 7 (lafz), 10 (dhuaan)'),
    dict(id='P3', text='इसकी क़ीमत। आवाज़ के तीन ट्रैक्स। एडिटिंग में क्या है? उसको भेजो।',
         words=['क़ीमत।', 'आवाज़', 'ट्रैक्स।', 'एडिटिंग', 'उसको'], why='risks 5 (keemat), 8 (tracks), 9 (editing), awaaz, C7 usko'),
    dict(id='P4', text='एक फ्रेम। फ्रेम ज़िन्दा है। कीमत। हर लफ़ज़। तीन ट्रैक।', optional=True,
         words=['फ्रेम।', 'ज़िन्दा', 'कीमत।', 'लफ़ज़।', 'ट्रैक।'],
         why='the SCRIPT section 8 fallback spellings (frame no nukta, zinda, keemat no nukta, lafaz, track); drop if the '
             'preflight says > 1 credit'),
]
# which DEV word a carrier word stands for (to suggest spelling.json entries)
FALLBACK_OF = {'फ्रेम': 'फ़्रेम', 'ज़िन्दा': 'ज़िंदा', 'कीमत': 'क़ीमत', 'लफ़ज़': 'लफ़्ज़', 'ट्रैक': 'ट्रैक्स'}
_N = lambda s: unicodedata.normalize('NFC', s)  # noqa: E731  (combining nukta, as in script.json)
PRON = [dict(p, text=_N(p['text']), words=[_N(w) for w in p['words']]) for p in PRON]
FALLBACK_OF = {_N(k): _N(v) for k, v in FALLBACK_OF.items()}
# words whose consonant ASR cannot judge (nukta z / f / q): flagged for a listen, never auto-failed
EAR = ('ज़', 'फ़', 'क़', '़')
# per line: token indices that must be heard right (keywords + the risk words + the numbers)
CRITICAL = {'V1A': [3, 4], 'V1B': [2, 3, 4, 5], 'V2': [3, 5, 6], 'V3': [3], 'V4': [1, 3], 'V5': [2, 5, 6],
            'V6': [1, 3, 4], 'V7': [3, 4, 5, 6], 'V8': [1, 3, 4], 'V9': [0, 1], 'V10': [3, 7, 8]}
# the spoken-number lock (SLATE section 4): these lines must contain exactly these number words
NUMBERS = {'V1B': 'तीन सौ साठ', 'V2': 'बारह', 'V6': 'तीस', 'V7': 'तीन सौ साठ', 'V8': 'तीन'}
LOAN = {'frame': 'फ़्रेम', 'frames': 'फ़्रेम्स', 'layer': 'लेयर', 'layers': 'लेयर्स', 'second': 'सेकंड',
        'seconds': 'सेकंड्स', 'editing': 'एडिटिंग', 'track': 'ट्रैक', 'tracks': 'ट्रैक्स', 'sec': 'सेकंड'}
DIGITS = {'360': 'तीन सौ साठ', '60': 'साठ', '12': 'बारह', '30': 'तीस', '3': 'तीन', '1': 'एक', '307': 'तीन सौ सात',
          '7': 'सात', '300': 'तीन सौ'}


def load_script(v10='usko', work=None):
    d = json.load(open(SCRIPT_JSON, encoding='utf8'))
    lines = {l['id']: dict(l) for l in d['lines']}
    if v10 == 'usey':                                    # C7 fallback: takes[T3].alt (V10 part only)
        t3 = next(t for t in d['takes'] if t['id'] == 'T3')['alt']
        dev_t, rom_t = V.tokens(t3['dev']), V.tokens(t3['rom'])
        n9 = len(lines['V9']['dev_tokens'])
        l = lines['V10']
        l.update(tts=' '.join(dev_t[n9:]), dev=' '.join(dev_t[n9:]), roman_marked=' '.join(rom_t[n9:]),
                 dev_tokens=dev_t[n9:], take_id='V10K')
    fixes = load_fixes(work)
    for k, l in lines.items():
        l.setdefault('take_id', k)
        dev = [fix_token(t, fixes) for t in V.tokens(l['tts'])]
        rom = V.tokens(l['roman_marked'])
        if len(dev) != len(rom) or len(dev) != len(l['dev_tokens']):
            raise ValueError('%s: DEV/ROM token mismatch (%d vs %d)' % (k, len(dev), len(rom)))
        l['req_tokens'], l['rom_tokens'] = dev, rom
        l['req'] = ' '.join(dev)
    return d, lines


# ------------------------------------------------------------------------------------------------ spelling fixes
def load_fixes(work=None):
    p = os.path.join(work or os.path.join(RW, 'vo'), 'spelling.json')
    if not os.path.exists(p):
        return {}
    return {nfc(k): nfc(v) for k, v in json.load(open(p, encoding='utf8')).items()}


def nfc(s):
    return unicodedata.normalize('NFC', s)


def fix_token(tok, fixes):
    tok = nfc(tok)
    core =re.sub(r'^["\']+|[,.!?;:।…"\']+$', '', tok)
    if core in fixes:
        return tok.replace(core, fixes[core], 1)
    return tok


# ------------------------------------------------------------------------------------------------ text metrics
def norm_cer(s):
    s = unicodedata.normalize('NFD', s.lower())
    s = ''.join(V.NUKTA.get(ch, ch) for ch in s)
    s = unicodedata.normalize('NFC', s).replace('ँ', 'ं')
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


def devify(hyp):
    """Whisper's Latin loanwords and digits -> the DEV spelling ('360' is said 'teen sau saath'; '307' is a wrong number
    and stays visible as 'teen sau saat')."""
    hyp = re.sub(r'\d+', lambda m: DIGITS.get(m.group(0), m.group(0)), hyp)
    return re.sub(r'[A-Za-z]+', lambda m: LOAN.get(m.group(0).lower(), m.group(0)), hyp)


def nd(w):
    return V.norm_dev(unicodedata.normalize('NFC', w))


_WM = {}
KW_OK = 1.15     # vo_chain.sim >= 1.15: the heard word has the word's consonant skeleton (or spelling) exactly


def transcribe(path, prompt=None, model='small'):
    """faster-whisper int8, language hi, word stamps, decoded by ffmpeg to a 16 kHz numpy array (not the PyAV path)."""
    from faster_whisper import WhisperModel
    if model not in _WM:
        mp = os.path.join(V.WHISPER, 'faster-whisper-%s' % model)
        _WM[model] = WhisperModel(mp if os.path.isdir(mp) else model, device='cpu', compute_type='int8',
                                  cpu_threads=V.THREADS)
    x = V.decode(path, 16000)
    segs, _ = _WM[model].transcribe(x, language='hi', word_timestamps=True, beam_size=5, initial_prompt=prompt,
                                    condition_on_previous_text=False, vad_filter=False)
    words, text = [], []
    for s in segs:
        text.append(s.text.strip())
        for w in s.words or []:
            words.append(dict(w=w.word.strip(), s=round(float(w.start), 3), e=round(float(w.end), 3),
                              p=round(float(w.probability), 3)))
    return ' '.join(text).strip(), words


def heard_tokens(heard):
    """Heard words with digits / Latin mapped to DEV words (a '360' becomes three tokens)."""
    out = []
    for h in heard:
        for t in devify(h['w']).split():
            if V.norm_dev(t):
                out.append(t)
    return out


def best_match(word, toks):
    """-> (heard candidate, score): best vo_chain.sim over single heard tokens and adjacent pairs."""
    if not toks:
        return None, -1.0
    cands = toks + [a + b for a, b in zip(toks, toks[1:])]
    sc = [V.sim(word, c) for c in cands]
    k = int(np.argmax(sc))
    return cands[k], round(float(sc[k]), 2)


def word_verdict(word, toks):
    """'ok' / 'fail' for a risk word against the heard tokens. साठ needs the exact word (vo_chain.skel maps साठ and सात to
    the same skeleton, so the similarity score cannot tell 60 from 7)."""
    m, sc = best_match(word, toks)
    core = nd(word)
    if core == nd('साठ'):
        ok = any(nd(t) == core for t in toks)
        return m, sc, 'ok' if ok else 'fail'
    return m, sc, 'ok' if sc >= KW_OK else 'fail'


def number_check(text, want):
    """The spoken-number lock: the heard text (digits mapped to words; spaces ignored, since whisper glues words such
    as 'बारहलेयर्स') must contain the line's number words in order. साठ must be exact (सात = 7, साथ = 'with');
    सौ may be written सो, तीन as तीं, बारह as बारा."""
    alt = {nd('सौ'): '(?:%s|%s)' % (nd('सौ'), nd('सो')), nd('तीन'): '(?:%s|%s)' % (nd('तीन'), nd('तीं')),
           nd('बारह'): '(?:%s|%s)' % (nd('बारह'), nd('बारा'))}
    t = ''.join(nd(x) for x in devify(text).split())
    pat = ''.join(alt.get(nd(w), re.escape(nd(w))) for w in want.split())
    return re.search(pat, t) is not None


# ------------------------------------------------------------------------------------------------ takes
def takes_for(raw, ident):
    fs = glob.glob(os.path.join(raw, '%s_%s_t*.mp3' % (PREFIX, ident))) + \
        glob.glob(os.path.join(raw, '%s_%s_t*.wav' % (PREFIX, ident)))
    fs = [f for f in fs if re.search(r'_t(\d+)\.(mp3|wav)$', f)]
    return sorted(fs, key=lambda f: int(re.search(r'_t(\d+)\.', f).group(1)))


def pick_take(raw, work, ident):
    sel = os.path.join(work, 'select.json')
    if os.path.exists(sel):
        name = json.load(open(sel)).get(ident)
        if name:
            p = os.path.join(raw, name)
            if not os.path.exists(p):
                raise FileNotFoundError(p)
            return p
    fs = takes_for(raw, ident)
    return fs[-1] if fs else None


# ------------------------------------------------------------------------------------------------ requests
def req(text):
    return dict(model='elevenlabs_v4', prompt=text, dialogue=[dict(text=text, voice_id=VOICE_ID, voice_type='preset')])


def cmd_requests(work):
    d, lines = load_script(work=work)
    _, lines_k = load_script('usey', work)
    for l in list(lines.values()) + [lines_k['V10']]:
        bad = re.findall(r'[0-9A-Za-z\[\]()<>#@]', l['req'])
        if bad:
            raise ValueError('%s: TTS text has %s' % (l['id'], bad))
        if unicodedata.normalize('NFC', l['req']) != l['req']:
            raise ValueError('%s: not NFC' % l['id'])
    out = dict(
        reel=REEL, voice='Vlad (preset) on elevenlabs_v4', voice_id=VOICE_ID,
        rules=['balance first and before each batch; STOP if the balance is below 7015',
               'preflight every request with get_cost: true; keep the running sum in vo/credits.json; reel budget 25',
               'leave use_unlim unset (answer an unlim_choice with false); omit folder_id; no stability override on the '
               'first takes (0.55 only on a retake that drags or wobbles)',
               'poll job ids with jobs_wait; never resubmit blindly',
               'download result_url with curl into vo/raw/ as %s_<id>_t<n>.mp3 (n = 1 for the first take)' % PREFIX],
        spelling_fixes=load_fixes(work),
        batch_1_pronunciation=[dict(id=p['id'], save_as='%s_%s_t1.mp3' % (PREFIX, p['id']), why=p['why'],
                                    optional=bool(p.get('optional')), chars=len(p['text']), params=req(p['text']))
                               for p in PRON],
        batch_2_lines=[dict(id=k, save_as='%s_%s_t1.mp3' % (PREFIX, k), chars=len(lines[k]['req']),
                            window='%.2f-%.2f (hard %.2f)' % (lines[k]['start_target'], lines[k]['end_target'],
                                                             lines[k]['hard_end']),
                            params=req(lines[k]['req'])) for k in ALL_LINES],
        batch_alt_only_if_lead_keeps_USSE=[dict(id='V10K', save_as='%s_V10K_t1.mp3' % PREFIX,
                                                chars=len(lines_k['V10']['req']), params=req(lines_k['V10']['req']),
                                                when='C7 refused: card USSE YEH; then assemble with --v10 usey')])
    os.makedirs(work, exist_ok=True)
    p = os.path.join(work, 'requests.json')
    json.dump(out, open(p, 'w', encoding='utf8'), ensure_ascii=False, indent=1)
    print('->', p)
    for b in ('batch_1_pronunciation', 'batch_2_lines', 'batch_alt_only_if_lead_keeps_USSE'):
        print(b, sum(r['chars'] for r in out[b]), 'chars in', len(out[b]), 'requests')
    return out


# ------------------------------------------------------------------------------------------------ pron
def cmd_pron(raw, work):
    res, fixes = [], {}
    for p in PRON:
        f = pick_take(raw, work, p['id'])
        if not f:
            res.append(dict(id=p['id'], missing=True))
            continue
        r = dict(id=p['id'], take=os.path.basename(f), text=p['text'], why=p['why'],
                 dur=round(len(V.decode(f)) / SR, 3), asr=[], words=[])
        toks = {}
        for model in ('small', 'medium'):
            txt, heard = transcribe(f, model=model)
            toks[model] = heard_tokens(heard)
            r['asr'].append(dict(model=model, heard=txt, cer=round(cer(devify(txt), p['text']), 3)))
        for w in p['words']:
            ms = [(model,) + word_verdict(w, toks[model]) for model in ('small', 'medium')]
            ok = any(m[3] == 'ok' for m in ms)
            r['words'].append(dict(word=w, heard=ms, verdict='ok' if ok else 'fail',
                                   listen=any(c in unicodedata.normalize('NFD', w) for c in EAR)))
        res.append(r)
        print(json.dumps(r, ensure_ascii=False), flush=True)
    # spelling suggestions: a script spelling that failed both ears while its fallback passed
    verd = {re.sub(r'[,.।?]+$', '', w['word']): w['verdict'] for r in res if not r.get('missing') for w in r['words']}
    for fb, prim in FALLBACK_OF.items():
        if verd.get(prim) == 'fail' and verd.get(fb) == 'ok':
            fixes[prim] = fb
    out = dict(carriers=res, suggested_spelling_json=fixes,
               note='write suggested_spelling_json to <work>/spelling.json, re-run requests, then generate the lines')
    json.dump(out, open(os.path.join(work, 'pron_check.json'), 'w', encoding='utf8'), ensure_ascii=False, indent=1)
    print('suggested spelling.json:', json.dumps(fixes, ensure_ascii=False))
    return out


# ------------------------------------------------------------------------------------------------ process
def proc_path(work, take, speed):
    base = os.path.splitext(os.path.basename(take))[0]
    return os.path.join(work, 'proc', '%s_%.2f.wav' % (base, speed))


def process_line(l, take, work, speed, force=False):
    out = proc_path(work, take, speed)
    rep_p = os.path.splitext(out)[0] + '.report.json'
    if not force and os.path.exists(rep_p) and os.path.getmtime(rep_p) > os.path.getmtime(take):
        return json.load(open(rep_p))
    os.makedirs(os.path.dirname(out), exist_ok=True)
    return V.process(take, l['req_tokens'], l['rom_tokens'], out=out, speed=speed, realign=True)


def score_line(l, path, words):
    """CER (no prompt) + the critical words + the number lock on one processed take; whisper medium only as a second
    ear when small flags the line."""
    crit = CRITICAL.get(l['id'], [])

    def run(model):
        txt, heard = transcribe(path, model=model)
        toks = heard_tokens(heard)
        ks = []
        for i in crit:
            m, sc, v = word_verdict(l['req_tokens'][i], toks)
            ks.append(dict(i=i, word=l['rom_tokens'][i].lstrip('*'), dev=l['req_tokens'][i], heard=m, sim=sc,
                           verdict=v))
        num = number_check(txt, NUMBERS[l['id']]) if l['id'] in NUMBERS else None
        return dict(model=model, heard=txt, cer=round(cer(devify(txt), l['req']), 3), words=ks, number_ok=num)
    asr = [run('small')]
    a = asr[0]
    if a['cer'] > CER_MAX or any(k['verdict'] != 'ok' for k in a['words']) or a['number_ok'] is False:
        asr.append(run('medium'))
    best_cer = min(x['cer'] for x in asr)
    kw = []
    for j, i in enumerate(crit):
        vs = [x['words'][j] for x in asr]
        ok = any(v['verdict'] == 'ok' for v in vs)
        kw.append(dict(i=i, word=vs[0]['word'], dev=vs[0]['dev'], aligned_ok=words[i]['ok'],
                       aligned_heard=words[i]['heard'], free=[(x['model'], v['heard'], v['sim']) for x, v in zip(asr, vs)],
                       listen=any(c in unicodedata.normalize('NFD', vs[0]['dev']) for c in EAR),
                       verdict='ok' if ok else 'retake'))
    num_ok = None if l['id'] not in NUMBERS else any(x['number_ok'] for x in asr)
    return dict(asr=asr, cer=a['cer'], cer_best=best_cer, keywords=kw, number_ok=num_ok,
                retake=bool(best_cer > CER_MAX or any(k['verdict'] == 'retake' for k in kw) or num_ok is False))


def cmd_process(raw, work, only=None, v10='usko'):
    d, lines = load_script(v10, work)
    state_p = os.path.join(work, 'lines.json')
    state = json.load(open(state_p)) if os.path.exists(state_p) else {}
    for lid in ALL_LINES:
        if only and lid not in only:
            continue
        l = lines[lid]
        take = pick_take(raw, work, l['take_id'])
        if not take:
            print(lid, 'no take', l['take_id'], 'in', raw)
            continue
        t0 = time.time()
        reps = {'1.08': process_line(l, take, work, 1.08)}        # 1.10 runs on demand in decide()
        fin = proc_path(work, take, 1.08)
        words = json.load(open(os.path.splitext(fin)[0] + '.words.json'))
        sc = score_line(l, fin, words)
        state[lid] = dict(take=os.path.relpath(take, REPO), take_dur=round(len(V.decode(take)) / SR, 3), req=l['req'],
                          heard=sc['asr'][0]['heard'], matched='%d/%d' % (sum(w['ok'] for w in words), len(words)),
                          unmatched=[(w['word'], w['heard']) for w in words if not w['ok']],
                          passes={k: dict(final_dur=r['final_dur'], speed=r['speed'], lufs=r['loudness']['lufs'],
                                          tp=r['loudness']['tp'], pauses=r['pauses'], wpm_after=r['wpm_after'],
                                          realign=(r.get('realign') or {}).get('independent'), out=r['output'])
                                  for k, r in reps.items()},
                          listen=[k['word'] for k in sc['keywords'] if k['listen']],
                          seconds=round(time.time() - t0, 1), **sc)
        print(lid, json.dumps({k: state[lid][k] for k in ('cer', 'cer_best', 'matched', 'number_ok', 'retake', 'listen',
                                                          'heard')}, ensure_ascii=False), flush=True)
        json.dump(state, open(state_p, 'w', encoding='utf8'), ensure_ascii=False, indent=1)
    return state


# ------------------------------------------------------------------------------------------------ editing
class Clip:
    """A processed line: 48 kHz float audio + word list (clip time; 'i' = token index in the line)."""

    def __init__(self, x, words):
        self.x = np.asarray(x, np.float32).copy()
        self.words = [dict(w) for w in words]

    @property
    def runs(self):
        return V.voiced_runs(self.x)

    @property
    def dur(self):
        return len(self.x) / SR

    def span(self):
        r = self.runs
        return (r[0][0], r[-1][1]) if r else (0.0, self.dur)

    def voice_off(self):
        return self.span()[1]

    def gap_after(self, k):
        """The silence between list word k and k+1: the longest voiced-run gap inside [start_k, end_k+1]."""
        a, b = self.words[k]['start'], self.words[k + 1]['end']
        best = None
        r = self.runs
        for (p0, p1), (q0, q1) in zip(r, r[1:]):
            if p1 >= a and q0 <= b and q0 > p1:
                if best is None or q0 - p1 > best[1] - best[0]:
                    best = (p1, q0)
        return best

    def cap_gap(self, k, cap, xfade=0.005):
        """Shorten the pause after list word k to `cap` s (never lengthens). -> (was, now)."""
        g = self.gap_after(k)
        if not g:
            return (0.0, 0.0)
        a1, b0 = g
        if b0 - a1 <= cap + 0.005:
            return (round(b0 - a1, 3), round(b0 - a1, 3))
        nx = int(xfade * SR)
        ia = int(round((a1 + cap / 2) * SR))
        ib = int(round((b0 - cap / 2) * SR)) - nx
        r = 0.5 - 0.5 * np.cos(np.linspace(0, np.pi, nx, dtype=np.float32))
        A, B = self.x[:ia], self.x[ib:]
        mid = A[-nx:] * (1 - r) + B[:nx] * r
        self.x = np.concatenate([A[:-nx], mid, B[nx:]])
        shift = (ia - nx - ib) / SR
        cut_t = (ib + nx) / SR
        for w in self.words:
            for key in ('start', 'end'):
                if w[key] >= cut_t - 1e-6:
                    w[key] = round(w[key] + shift, 3)
                elif w[key] > ia / SR:
                    w[key] = round(ia / SR, 3)
        return (round(b0 - a1, 3), round(cap, 3))

    def split_after(self, k, pad=0.04, fade=0.01):
        """Split in the pause after list word k -> (clip1, clip2); each keeps `pad` s of silence at the cut."""
        g = self.gap_after(k)
        if not g:                                   # no silence: cut at the quietest 10 ms around the word boundary
            bnd = 0.5 * (self.words[k]['end'] + self.words[k + 1]['start'])
            h = int(0.005 * SR)
            ts = np.arange(max(0.02, bnd - 0.06), min(self.dur - 0.02, bnd + 0.06), 0.002)
            rms = [float(np.sqrt(np.mean(self.x[int(t * SR) - h:int(t * SR) + h].astype(np.float64) ** 2)))
                   for t in ts]
            t = float(ts[int(np.argmin(rms))]) if len(ts) else bnd
            self.last_cut = dict(at=round(t, 3), word=self.words[k]['word'], inside_voice=True)
            g = (t, t)
        else:
            self.last_cut = dict(at=round(0.5 * (g[0] + g[1]), 3), word=self.words[k]['word'], inside_voice=False,
                                 pause=round(g[1] - g[0], 3))
        a1, b0 = g
        c1 = int(round(min(a1 + pad, (a1 + b0) / 2) * SR))
        c2 = int(round(max(b0 - pad, (a1 + b0) / 2) * SR))
        nf = int(fade * SR)
        x1, x2 = self.x[:c1].copy(), self.x[c2:].copy()
        x1[-nf:] *= np.linspace(1, 0, nf, dtype=np.float32)
        x2[:nf] *= np.linspace(0, 1, nf, dtype=np.float32)
        w1 = [dict(w) for w in self.words[:k + 1]]
        w2 = [dict(w, start=round(w['start'] - c2 / SR, 3), end=round(w['end'] - c2 / SR, 3)) for w in self.words[k + 1:]]
        for w in w1:
            w['end'] = min(w['end'], round(c1 / SR, 3))
        for w in w2:
            w['start'] = max(w['start'], 0.0)
        return Clip(x1, w1), Clip(x2, w2)

    def word_onset(self, k, back=0.30, look=0.35):
        """The voiced onset of list word k: the onset of the voiced run its start sits in (when that onset is at most
        `back` s earlier: whisper sometimes starts a take's first word late inside it), else the next onset within
        `look` s when the start sits in silence, else the start itself."""
        s = self.words[k]['start']
        for r0, r1 in self.runs:
            if r0 - 1e-6 <= s <= r1 + 0.02:
                return r0 if s - r0 <= back else s
            if r0 > s:
                return r0 if r0 - s <= look and r0 < self.words[k]['end'] else s
        return s

    def trim_head(self, pre=0.04, fade=0.008):
        """Drop anything (breath, click) more than `pre` s before the first word's voiced onset; word times follow.
        Never cuts into the run the first word starts in."""
        on = self.word_onset(0)
        self.words[0]['start'] = round(on, 3)
        t = max(0.0, on - pre)
        n = int(round(t * SR))
        if n <= 0:
            return 0.0
        self.x = self.x[n:].copy()
        nf = int(fade * SR)
        self.x[:nf] *= np.linspace(0, 1, nf, dtype=np.float32)
        for w in self.words:
            w['start'] = round(max(0.0, w['start'] - t), 3)
            w['end'] = round(max(0.0, w['end'] - t), 3)
        return round(t, 3)


def load_clip(work, take, speed):
    p = proc_path(work, take, speed)
    if not os.path.exists(p):
        raise FileNotFoundError(p)
    words = json.load(open(os.path.splitext(p)[0] + '.words.json'))
    for i, w in enumerate(words):
        w['i'] = i
    return Clip(V.decode(p), words)


# ------------------------------------------------------------------------------------------------ the fit ladder
def seg(c, onset, label, k=0):
    """A placement: the voiced onset of list word k of clip c lands on reel time `onset`."""
    o = c.word_onset(k)
    if abs(o - c.words[k]['start']) > 1e-3:
        c.words[k]['start'] = round(o, 3)
        if k > 0:
            c.words[k - 1]['end'] = min(c.words[k - 1]['end'], round(o, 3))
    off = onset - o
    return dict(clip=c, onset=onset, label=label, off=off, end=off + c.voice_off(), on=off + c.span()[0])


def decide(lid, take, work, lines, v9_end=None, p2=False):
    """The SCRIPT section 7 ladder on the measured take -> dict(segments, speed, notes, fail, flags). p2 = the last
    V9 + V10 step (SCRIPT 7: 'Keemat...' cut, 'banane wala jaanta hai.' from 26.75, V10 from 29.50): a copy change,
    so it runs only with --p2 (the lead's OK)."""
    P, l = PLAN[lid], lines[lid]
    notes, fail, flags = [], [], []

    def clip_at(sp):
        if not os.path.exists(proc_path(work, take, sp)):
            process_line(l, take, work, sp)
            notes.append('processed the %.2fx pass on demand' % sp)
        c = load_clip(work, take, sp)
        t = c.trim_head()
        if t > 0.02:
            notes.append('%.2fx: %.3f s before the first word removed (breath / click)' % (sp, t))
        return c

    def split(c, k):
        a, b = c.split_after(k)
        if c.last_cut['inside_voice']:
            flags.append('no pause after "%s": cut inside the voice at %.3f s (quietest 10 ms; listen)'
                         % (c.last_cut['word'], c.last_cut['at']))
        return a, b

    mode = P['mode']
    if lid == 'V9' and p2:
        c = clip_at(1.08)
        c1, c2 = split(c, 0)
        s = seg(c2, P['onset'], lid + 'b')
        notes.append('P2 (--p2, lead OK): "%s" dropped; "%s" from %.2f' % (c.words[0]['word'], c2.words[0]['word'],
                                                                         P['onset']))
        flags.append('P2 copy change: the VO no longer says "Keemat" (the lockup still shows it)')
        if s['end'] > P['limit'] + 1e-6:
            fail.append('P2 ends %.3f > %.2f' % (s['end'], P['limit']))
        return dict(segments=[s], speed=1.08, notes=notes, fail=fail, flags=flags)
    if mode == 'whole':
        onsets = [P['onset']]
        if lid == 'V10' and v9_end is not None:
            o = max(29.50 if p2 else P['onset'], round(v9_end + GAP_LINES, 3))
            if o > P['onset_max'] + 1e-6:
                fail.append('V9 ends %.3f: V10 would start %.3f > %.2f' % (v9_end, o, P['onset_max']))
            onsets = [o]
        tries = [(sp, onsets[0], False) for sp in (1.08, 1.10)]
        if 'hold_cap' in P:
            tries.append((1.10, P['onset'], True))
        if 'onset_alt' in P:
            tries.append((1.10, P['onset_alt'], True))
        for sp, on, cap in tries:
            c = clip_at(sp)
            if cap:
                k, cp = P['hold_cap']
                was, now = c.cap_gap(k, cp)
                notes.append('%.2fx: pause after "%s" %.3f -> %.3f s' % (sp, c.words[k]['word'], was, now))
            s = seg(c, on, lid)
            if s['end'] <= P['limit'] + 1e-6:
                break
            notes.append('%.2fx%s from %.2f ends %.3f > %.2f: next ladder step'
                         % (sp, ' + hold cap' if cap else '', on, s['end'], P['limit']))
        if s['end'] > P['hard'] + 1e-6:
            fail.append('ends %.3f > hard %.2f after the zero-credit ladder: retake' % (s['end'], P['hard']))
        elif s['end'] > P['limit'] + 1e-6:
            flags.append('ends %.3f > %.2f (inside hard %.2f)' % (s['end'], P['limit'], P['hard']))
        for k, t, tol, why in P.get('checks', []):
            got = s['off'] + s['clip'].words[k]['start']
            if abs(got - t) > tol:
                flags.append('"%s" at %.3f, target %.2f +-%.2f (%s)' % (s['clip'].words[k]['word'], got, t, tol, why))
        return dict(segments=[s], speed=sp, notes=notes, fail=fail, flags=flags)

    if mode == 'anchor':
        for sp in (1.08, 1.10):
            c = clip_at(sp)
            s = seg(c, P['onset'], lid)
            nat = s['off'] + c.words[P['anchor']]['start']
            if abs(nat - P['at']) <= P['tol'] and s['end'] <= P['limit'] + 1e-6:
                notes.append('%.2fx: "%s" lands %.3f (target %.2f +-%.2f): whole line'
                             % (sp, c.words[P['anchor']]['word'], nat, P['at'], P['tol']))
                return dict(segments=[s], speed=sp, notes=notes, fail=fail, flags=flags)
            c1, c2 = split(c, P['split'])
            s1 = seg(c1, P['onset'], lid + 'a')
            d1 = s1['end'] - P['onset']
            k2 = P['anchor'] - (P['split'] + 1)
            on2 = max(P['at'], s1['end'] + MIN_HOLD + (c2.words[k2]['start'] - c2.span()[0]))
            s2 = seg(c2, on2, lid + 'b', k2)
            why = '%.2fx: "%s" would land %.3f (target %.2f +-%.2f); split at the hold' % (
                sp, c.words[P['anchor']]['word'], nat, P['at'], P['tol'])
            bad = []
            if P.get('part1_max') and d1 > P['part1_max'] + 1e-6:
                bad.append('part 1 %.3f s > %.2f s' % (d1, P['part1_max']))
            if on2 > P['at'] + P['tol'] + 1e-6:
                bad.append('anchor %.3f > %.2f (hold >= %.2f s after part 1 at %.3f)' % (on2, P['at'] + P['tol'],
                                                                                       MIN_HOLD, s1['end']))
            if s2['end'] > P['limit'] + 1e-6:
                bad.append('ends %.3f > %.2f' % (s2['end'], P['limit']))
            if not bad:
                notes.append(why + ': part 2 at %.3f, hold %.3f s' % (on2, s2['on'] - s1['end']))
                return dict(segments=[s1, s2], speed=sp, notes=notes, fail=fail, flags=flags)
            notes.append(why + ' -> ' + '; '.join(bad) + ': next ladder step')
            last = [s1, s2]
        if 'hold_cap' in P:                       # V9: hold capped, whole line (the anchor may move)
            c = clip_at(1.10)
            k, cp = P['hold_cap']
            was, now = c.cap_gap(k, cp)
            s = seg(c, P['onset'], lid)
            nat = s['off'] + c.words[P['anchor']]['start']
            notes.append('1.10x: pause after "%s" %.3f -> %.3f s; "%s" at %.3f' % (c.words[k]['word'], was, now,
                                                                                   c.words[P['anchor']]['word'], nat))
            if s['end'] <= P['limit'] + 1e-6:
                flags.append('anchor "%s" at %.3f (target %.2f)' % (c.words[P['anchor']]['word'], nat, P['at']))
                return dict(segments=[s], speed=1.10, notes=notes, fail=fail, flags=flags)
        fail.append('no zero-credit ladder step fits: ' + notes[-1])
        return dict(segments=last, speed=1.10, notes=notes, fail=fail, flags=flags)

    if mode == 'words':                            # V3: each word at its tag arrival
        for sp, drop in ((1.08, False), (1.10, False), (1.10, True)):
            c = clip_at(sp)
            parts, rest = [], c
            for k in range(len(P['onsets']) - 1):
                a, rest = split(rest, 0)
                parts.append(a)
            parts.append(rest)
            names = [p.words[0]['word'] for p in parts]
            segs_ = [seg(p, on, '%s.%d' % (lid, j)) for j, (p, on) in enumerate(zip(parts, P['onsets']))]
            if drop:
                segs_.pop(P['drop'])
                notes.append('1.10x: "%s" dropped (tag 02 carries it; zero credits)' % names[P['drop']])
            bad = ['"%s" ends %.3f, next word at %.3f' % (a['clip'].words[0]['word'], a['end'], b['on'])
                   for a, b in zip(segs_, segs_[1:]) if a['end'] > b['on'] - GAP_WORDS + 1e-6]
            if segs_[-1]['end'] > P['limit'] + 1e-6:
                bad.append('ends %.3f > %.2f' % (segs_[-1]['end'], P['limit']))
            if not bad:
                return dict(segments=segs_, speed=sp, notes=notes, fail=fail, flags=flags)
            notes.append('%.2fx%s: %s: next ladder step' % (sp, ' (drop)' if drop else '', '; '.join(bad)))
        fail.append('V3 does not fit: ' + notes[-1])
        return dict(segments=segs_, speed=1.10, notes=notes, fail=fail, flags=flags)

    if mode == 'phrases':                          # V4: "Har lafz." / "Har chamak."
        for sp, on2 in ((1.08, P['onsets'][1]), (1.08, P['onset2_alt']), (1.10, P['onsets'][1]),
                        (1.10, P['onset2_alt'])):
            c = clip_at(sp)
            c1, c2 = split(c, P['split'])
            s1 = seg(c1, P['onsets'][0], lid + 'a')
            s2 = seg(c2, on2, lid + 'b')
            bad = []
            if s1['end'] > s2['on'] - GAP_WORDS + 1e-6:
                bad.append('"Har lafz." ends %.3f, "Har chamak." at %.3f' % (s1['end'], s2['on']))
            if s2['end'] > P['limit'] + 1e-6:
                bad.append('ends %.3f > %.2f' % (s2['end'], P['limit']))
            if not bad:
                if on2 != P['onsets'][1]:
                    notes.append('"Har chamak." moved to %.2f' % on2)
                return dict(segments=[s1, s2], speed=sp, notes=notes, fail=fail, flags=flags)
            notes.append('%.2fx, part 2 at %.2f: %s: next ladder step' % (sp, on2, '; '.join(bad)))
        fail.append('V4 does not fit: ' + notes[-1])
        return dict(segments=[s1, s2], speed=1.10, notes=notes, fail=fail, flags=flags)
    raise KeyError(lid)


# ------------------------------------------------------------------------------------------------ assemble
def place(segments, n=NSAMP):
    """-> (stem, placed): each segment's clip added at its offset; word times in reel time."""
    y = np.zeros(n, np.float32)
    placed = []
    for s in segments:
        c = s['clip']
        i0 = int(round(s['off'] * SR))
        if i0 < 0:
            raise ValueError('%s would start before 0 s' % s['label'])
        xs = c.x[: max(0, min(len(c.x), n - i0))]
        y[i0:i0 + len(xs)] += xs
        words = [dict(w, start=round(w['start'] + s['off'], 3), end=round(w['end'] + s['off'], 3)) for w in c.words]
        placed.append(dict(label=s['label'], onset=round(s['onset'], 3), voice_on=round(s['on'], 3),
                           voice_off=round(s['end'], 3), file_on=round(s['off'], 3),
                           file_off=round(s['off'] + c.dur, 3), cut=len(c.x) > len(xs), words=words))
    return y, placed


def lufs_tp(x):
    err = subprocess.run(['ffmpeg', '-hide_banner', '-nostats', '-f', 'f32le', '-ar', str(SR), '-ac', '1', '-i', '-', '-af',
                          'loudnorm=I=-16:TP=-2:LRA=11:print_format=json', '-f', 'null', '-'],
                         input=np.asarray(x, np.float32).tobytes(), capture_output=True).stderr.decode()
    j = json.loads(err[err.rindex('{'): err.rindex('}') + 1])
    return float(j['input_i']), float(j['input_tp'])


def limit(x, ceiling_db):
    p = subprocess.run(['ffmpeg', '-hide_banner', '-loglevel', 'error', '-f', 'f32le', '-ar', str(SR), '-ac', '1', '-i', '-',
                        '-af', 'alimiter=limit=%.5f:attack=3:release=50:level=false:latency=true' % (10 ** (ceiling_db / 20)),
                        '-f', 'f32le', '-ac', '1', '-'], input=np.asarray(x, np.float32).tobytes(), capture_output=True,
                       check=True)
    z = np.frombuffer(p.stdout, np.float32)[:len(x)]
    return np.pad(z, (0, len(x) - len(z))).astype(np.float32)


def master(y):
    """Static gain to -16.0 LUFS integrated (+-0.05); a lookahead limiter only if the true peak passes -2.2 dBTP.
    -> (z, info) with the total gain so another stem can get the same gain."""
    l0, tp0 = lufs_tp(y)
    z, lim, it, g_tot = y.copy(), False, [], 0.0
    for _ in range(4):
        li, tp = lufs_tp(z)
        it.append((round(li, 2), round(tp, 2)))
        if abs(li - LUFS) <= 0.05 and tp <= TP_MAX - 0.1:
            break
        g = LUFS - li
        g_tot += g
        z = (z * 10 ** (g / 20)).astype(np.float32)
        if lufs_tp(z)[1] > TP_MAX - 0.2:
            z = limit(z, TP_MAX - 0.5)
            lim = True
    return z, dict(pre_lufs=round(l0, 2), pre_tp=round(tp0, 2), gain_db=round(g_tot, 3), limiter=lim, iterations=it)


def write_checked(path, z):
    V.write_wav(path, z)
    L = V.ebur128(path)
    li, tp = lufs_tp(V.decode(path))
    return dict(L, lufs_precise=round(li, 2), tp_precise=round(tp, 2))


def probe(path):
    out = subprocess.run(['ffprobe', '-v', 'error', '-show_entries',
                          'stream=sample_rate,channels,sample_fmt,bits_per_raw_sample,codec_name',
                          '-show_entries', 'format=duration', '-of', 'json', path], capture_output=True, text=True).stdout
    return json.loads(out)


def merge_words(placed, lines, tokens_vis):
    out = []
    for p in placed:
        lid = re.sub(r'(a|b|\.\d)$', '', p['label'])
        for w in p['words']:
            i = w['i']
            out.append(dict(word=w['word'], start=w['start'], end=w['end'], keyword=w['keyword'], line=lid, i=i,
                            dev=w['dev'], heard=w.get('heard', ''), ok=w.get('ok', False),
                            hide=not tokens_vis.get((lid, i), False)))
    out.sort(key=lambda w: w['start'])
    return out


def syllables(dev):
    """Rough Devanagari syllable count (vowels + consonants not followed by a virama; final schwa deleted)."""
    n = 0
    for w in dev.split():
        w = re.sub(r'[^ऀ-ॿ]', '', unicodedata.normalize('NFC', w))
        c = 0
        for k, ch in enumerate(w):
            if 'अ' <= ch <= 'औ':
                c += 1
            elif 'क' <= ch <= 'ह' or 'क़' <= ch <= 'य़':
                nxt = w[k + 1] if k + 1 < len(w) else ''
                nxt2 = w[k + 2] if k + 2 < len(w) else ''
                if nxt == '्' or (nxt == '़' and nxt2 == '्'):
                    continue
                c += 1
        if c > 1 and re.search(r'[क-हक़-य़]़?$', w):
            c -= 1
        n += max(1, c)
    return n


def beat_of(t):
    """'[bar.beat] +n f' on the 100 BPM grid (frame 0 = bar 0 beat 0; 18 f per beat)."""
    f = int(round(t * 30))
    b, r = divmod(f, 18)
    return '[%d.%d]%s' % (b // 4, b % 4, (' +%d f' % r) if r else '')


def cmd_assemble(raw, work, md, label, v10='usko', p2=False):
    d, lines = load_script(v10, work)
    vis = {(t['line'], t['i']): bool(t.get('caption_visible')) for t in d['tokens']}
    state_p = os.path.join(work, 'lines.json')
    state = json.load(open(state_p)) if os.path.exists(state_p) else {}
    dec = {}
    for lid in ALL_LINES:
        take = pick_take(raw, work, lines[lid]['take_id'])
        if not take:
            raise FileNotFoundError('no take for %s (%s) in %s' % (lid, lines[lid]['take_id'], raw))
        v9e = dec['V9']['segments'][-1]['end'] if lid == 'V10' else None
        dec[lid] = decide(lid, take, work, lines, v9_end=v9e, p2=p2)
        if lid == 'V10' and dec[lid]['fail'] and not p2:
            dec[lid]['fail'].append('zero-credit P2 exists (--p2: VO drops "Keemat...", needs the lead\'s OK) or retake')
        print(lid, 'speed %.2f' % dec[lid]['speed'], dec[lid]['notes'], dec[lid]['flags'], dec[lid]['fail'] or 'OK',
              flush=True)
    # line levels: vo_chain normalises each take to -16 LUFS but its -2 dBTP ceiling holds peaky short takes lower
    # (up to several dB), so every line is re-levelled to -16 LUFS here; the stem limiter then catches the peaks
    for lid, v in dec.items():
        xs = np.concatenate([s_['clip'].x for s_ in v['segments']])
        li = lufs_tp(xs)[0]
        g = LUFS - li
        for s_ in v['segments']:
            s_['clip'].x = (s_['clip'].x * 10 ** (g / 20)).astype(np.float32)
        v['level'] = dict(lufs_in=round(li, 2), gain_db=round(g, 2))
    # stem A (hook A + body), static gain to -16 LUFS
    segsA = [s for lid in ORDER_A for s in dec[lid]['segments']]
    yA, placedA = place(segsA)
    zA, gain = master(yA)
    pA = os.path.join(work, '%s_vo.wav' % REEL)
    loudA = write_checked(pA, zA)
    loudA.update(gain)
    wordsA = merge_words(placedA, lines, vis)
    # hook B stem (0-3.0 s): V1B at the A stem's gain (the level matches across the splice at 3.000)
    yB, placedB = place(dec['V1B']['segments'], n=int(round(HOOK_B_DUR * SR)))
    zB = (yB * 10 ** (gain['gain_db'] / 20)).astype(np.float32)
    limB = False
    if lufs_tp(zB)[1] > TP_MAX - 0.2:
        zB, limB = limit(zB, TP_MAX - 0.5), True
    pB = os.path.join(work, '%s_hookb_vo.wav' % REEL)
    loudB = write_checked(pB, zB)
    loudB.update(gain_db=gain['gain_db'], limiter=limB)
    wordsB = merge_words(placedB, lines, vis)
    for p, w in ((pA, wordsA), (pB, wordsB)):
        json.dump(w, open(os.path.splitext(p)[0] + '.words.json', 'w', encoding='utf8'), ensure_ascii=False, indent=1)
    shutil.copyfile(pA, os.path.join(work, 'vo_stem.wav'))
    shutil.copyfile(os.path.splitext(pA)[0] + '.words.json', os.path.join(work, 'vo_stem.words.json'))
    shutil.copyfile(os.path.splitext(pA)[0] + '.words.json', os.path.join(work, 'words.json'))
    stems = dict(A=dict(path=pA, loud=loudA, placed=placedA, words=wordsA, probe=probe(pA), dur=DUR),
                 B=dict(path=pB, loud=loudB, placed=placedB, words=wordsB, probe=probe(pB), dur=HOOK_B_DUR))
    chk = checks(stems, dec, state, lines)
    credits = json.load(open(os.path.join(work, 'credits.json'))) if os.path.exists(os.path.join(work, 'credits.json')) \
        else {}
    json.dump(dict(label=label, v10=v10, checks=chk, credits_spent=credits.get('spent_credits'),
                   decisions={k: dict(speed=v['speed'], level=v['level'], notes=v['notes'], flags=v['flags'],
                                      fail=v['fail'])
                              for k, v in dec.items()},
                   stems={k: dict(loud=v['loud'], probe=v['probe'],
                                  placed=[{kk: vv for kk, vv in p.items() if kk != 'words'} for p in v['placed']])
                          for k, v in stems.items()}),
              open(os.path.join(work, 'check.json'), 'w', encoding='utf8'), ensure_ascii=False, indent=1)
    plot_timeline(stems, lines, os.path.join(work, 'vo_timeline.png'))
    write_md(md, label, stems, dec, state, lines, chk, work, raw, credits, v10)
    print(json.dumps(chk, ensure_ascii=False, indent=1))
    return stems, dec, chk


def checks(stems, dec, state, lines):
    out = {}
    for name, s in stems.items():
        y = V.decode(s['path'])
        runs = V.voiced_runs(y)
        st = s['probe']['streams'][0]
        c = dict(duration=float(s['probe']['format']['duration']), sr=int(st['sample_rate']), channels=st['channels'],
                 bits=st.get('bits_per_raw_sample'), lufs=s['loud']['lufs'], tp=s['loud']['tp'],
                 lufs_precise=s['loud']['lufs_precise'], tp_precise=s['loud']['tp_precise'], lra=s['loud']['lra'],
                 fails=[], flags=[])
        if abs(c['duration'] - s['dur']) > 0.002:
            c['fails'].append('duration %.4f' % c['duration'])
        if c['sr'] != SR or c['channels'] != 1 or str(c['bits']) != '24':
            c['fails'].append('format %s Hz %s ch %s bit' % (c['sr'], c['channels'], c['bits']))
        if name == 'A' and abs(c['lufs_precise'] - LUFS) > 0.1:
            c['fails'].append('loudness %.2f LUFS' % c['lufs_precise'])
        if max(c['tp'], c['tp_precise']) > TP_MAX:
            c['fails'].append('true peak %.2f dBTP' % max(c['tp'], c['tp_precise']))
        pl = s['placed']
        gaps = []
        for p, q in zip(pl, pl[1:]):
            g = q['voice_on'] - p['voice_off']
            same = re.sub(r'(a|b|\.\d)$', '', p['label']) == re.sub(r'(a|b|\.\d)$', '', q['label'])
            gaps.append((p['label'], q['label'], round(g, 3)))
            if g < (GAP_WORDS if same else GAP_LINES) - 1e-6:
                c['fails'].append('gap %s -> %s %.3f s' % (p['label'], q['label'], g))
            if q['file_on'] < p['file_off'] - 1e-3:
                c['flags'].append('files overlap %s / %s by %.3f s (silence pads summed)' % (p['label'], q['label'],
                                                                                         p['file_off'] - q['file_on']))
        c['gaps'] = gaps
        c['first_voice_s'] = round(runs[0][0], 3) if runs else None
        c['last_voice_s'] = round(runs[-1][1], 3) if runs else None
        if c['first_voice_s'] is None or c['first_voice_s'] > 0.15:
            c['fails'].append('VO onset %s > 0.15 s' % c['first_voice_s'])
        if name == 'A':
            body = [p for p in pl if p['label'] not in ('V1A', 'V1B')]
            if body and body[0]['voice_on'] < SPLICE - 1e-3:
                c['fails'].append('body voice at %.3f < splice %.2f' % (body[0]['voice_on'], SPLICE))
            hook = [p for p in pl if p['label'] in ('V1A', 'V1B')]
            if hook and hook[-1]['file_off'] > HOOK_B_DUR - 0.005:
                c['fails'].append('hook A file runs to %.3f (splice 3.000)' % hook[-1]['file_off'])
            quiet = [(round(a, 3), round(b, 3)) for a, b in runs if a < HOOK_B_DUR and b > PLAN['V1A']['hard'] + 0.02]
            if quiet:
                c['fails'].append('voice inside %.2f-3.00: %s' % (PLAN['V1A']['hard'], quiet))
            c['loop_seam_s'] = round(DUR - c['last_voice_s'] + c['first_voice_s'], 3)
            if c['last_voice_s'] > PLAN['V10']['hard']:
                c['fails'].append('last voice %.3f > %.2f' % (c['last_voice_s'], PLAN['V10']['hard']))
        else:
            if c['last_voice_s'] > HOOK_B_DUR - 0.03:
                c['fails'].append('hook B voice runs to %.3f (splice 3.000)' % c['last_voice_s'])
        w = s['words']
        if any(b['start'] < a['start'] for a, b in zip(w, w[1:])):
            c['fails'].append('word starts not monotone')
        c['words'] = len(w)
        c['words_ok'] = sum(x['ok'] for x in w)
        out[name] = c
    out['retakes'] = {k: v.get('retake') for k, v in state.items()}
    out['rule_fails'] = {k: v['fail'] for k, v in dec.items() if v['fail']}
    want = sum(len(lines[k]['req_tokens']) for k in ORDER_A)
    dropped = sum(1 for v in dec.values() for n_ in v['notes'] if 'dropped' in n_)
    if out['A']['words'] != want - dropped:
        out['A']['fails'].append('%d words in A, want %d' % (out['A']['words'], want - dropped))
    return out


# ------------------------------------------------------------------------------------------------ report
def seg_target(lab):
    lid = re.sub(r'(a|b|\.\d)$', '', lab)
    P = PLAN[lid]
    m = re.search(r'\.(\d)$', lab)
    if m:
        j = int(m.group(1))
        on = P['onsets'][j]
        end = P['onsets'][j + 1] - GAP_WORDS if j + 1 < len(P['onsets']) else P['limit']
        return lid, on, end
    if P['mode'] == 'phrases':
        return (lid, P['onsets'][0], P['onsets'][1] - GAP_WORDS) if lab.endswith('a') else (lid, P['onsets'][1],
                                                                                              P['limit'])
    if P['mode'] == 'anchor' and lab.endswith('a'):
        return lid, P['onset'], P['at'] - MIN_HOLD
    if P['mode'] == 'anchor' and lab.endswith('b'):
        return lid, P['at'], P['limit']
    return lid, P['onset'], P['limit']


def plot_timeline(stems, lines, path):
    """QA image: the A stem envelope on the 100 BPM grid, target windows (grey), placed voice (orange), keyword onsets
    (red), hook B's V1B on its own row."""
    from PIL import Image, ImageDraw, ImageFont
    W, H, X0 = 2400, 560, 60
    sx = (W - 2 * X0) / DUR
    img = Image.new('RGB', (W, H), (12, 8, 7))
    dr = ImageDraw.Draw(img)
    try:
        f = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 17)
    except OSError:
        f = ImageFont.load_default()
    X = lambda t: X0 + t * sx  # noqa: E731
    for k in range(int(DUR / BEAT) + 1):
        t = k * BEAT
        dr.line([(X(t), 40), (X(t), H - 40)], fill=(70, 50, 45) if k % 4 else (140, 100, 90), width=1 if k % 4 else 2)
        if k % 4 == 0:
            dr.text((X(t) + 3, 8), 'bar %d  %.1f s' % (k // 4, t), fill=(200, 180, 170), font=f)
    for name, yc in (('A', 150), ('B', 400)):
        s = stems[name]
        y = V.decode(s['path'])
        hop = max(1, int(SR / sx))
        env = np.sqrt(np.convolve(y.astype(np.float64) ** 2, np.ones(hop) / hop, 'same'))[::hop]
        env = env / (env.max() + 1e-9)
        for i, e in enumerate(env):
            dr.line([(X0 + i, yc - e * 70), (X0 + i, yc + e * 70)], fill=(255, 106, 26))
        for p in s['placed']:
            lid, on, end = seg_target(p['label'])
            dr.rectangle([X(on), yc + 80, X(end), yc + 94], outline=(180, 180, 180), width=2)
            dr.rectangle([X(p['voice_on']), yc + 98, X(p['voice_off']), yc + 110],
                         fill=(255, 159, 28) if p['voice_off'] <= end + 1e-6 else (242, 49, 43))
            dr.text((X(p['voice_on']), yc + 114), p['label'], fill=(255, 243, 230), font=f)
            for w in p['words']:
                if w['keyword']:
                    dr.line([(X(w['start']), yc - 85), (X(w['start']), yc + 75)], fill=(242, 49, 43), width=3)
                    dr.text((X(w['start']) + 4, yc - 100), w['word'].strip(',.?!।"'), fill=(255, 181, 71), font=f)
        dr.text((8, yc - 10), name, fill=(255, 243, 230), font=f)
    img.save(path)
    return path


def write_md(md, label, stems, dec, state, lines, chk, work, raw, credits, v10):
    A = stems['A']
    segs = A['placed'] + stems['B']['placed']
    line_dur = {}
    for p in segs:
        lid = seg_target(p['label'])[0]
        line_dur[lid] = line_dur.get(lid, 0.0) + p['voice_off'] - p['voice_on']
    rows, misses, fast = [], [], []
    for p in segs:
        lab = p['label']
        lid, tgt_on, tgt_end = seg_target(lab)
        l = lines[lid]
        ws = p['words']
        dur = p['voice_off'] - p['voice_on']
        lw = len(l['req_tokens']) / line_dur[lid]
        ls = l.get('syllables', syllables(l['req'])) / line_dur[lid]
        kws = ', '.join('*%s* @ %.3f' % (re.sub(r'[,.।?!"]+$', '', w['word']), w['start']) for w in ws
                        if w['keyword'])
        anchor = ws[0]['start']
        d_on = anchor - tgt_on
        d_end = p['voice_off'] - tgt_end
        d_brief = p['voice_off'] - l['end_target'] if not re.search(r'(a|\.\d)$', lab) or lab.endswith('.3') else None
        flag = []
        if abs(d_on) > 0.3:
            flag.append('first word %+.3f s off target' % d_on)
        if d_end > 0.0:
            flag.append('ends %+.3f s after %.2f' % (d_end, tgt_end))
        if d_brief is not None and d_brief > 0.0:
            flag.append('%+.3f s vs the script end %.2f' % (d_brief, l['end_target']))
        if max(abs(d_on), max(0.0, d_end), max(0.0, d_brief or 0.0)) > 0.3:
            misses.append('%s (%s)' % (lab, '; '.join(flag)))
        if lw > 3.2 and lab in (lid, lid + 'b', lid + '.3'):
            fast.append('%s %.2f w/s (%.2f syl/s)' % (lid, lw, ls))
        rows.append('| %s | %s | %.3f | %.3f | %+.3f | %.2f | %.3f | %+.3f | %.2fx | %.3f | %d | %.2f | %.2f | %s | %s |'
                    % (lab, beat_of(anchor), tgt_on, anchor, d_on, tgt_end, p['voice_off'], tgt_end - p['voice_off'],
                       dec[lid]['speed'], dur, len(ws), lw, ls, kws or '-', '; '.join(flag) or 'ok'))
    cer_rows = []
    for lid in ALL_LINES:
        s = state.get(lid, {})
        asr = s.get('asr', [])
        heard = ' / '.join('%s: %s' % (a['model'], a['heard']) for a in asr) or '-'
        cers = ' / '.join('%.3f' % a['cer'] for a in asr) or '-'
        kw = '; '.join('%s "%s" -> %s%s' % (k['word'], ', '.join('%s %s %.2f' % (m, h, sc) for m, h, sc in k['free']),
                                            k['verdict'], ' (listen)' if k['listen'] else '')
                       for k in s.get('keywords', []))
        num = {None: '-', True: 'ok', False: 'FAIL'}[s.get('number_ok')]
        cer_rows.append('| %s | %s | %s | %.3f | %s | %s | %s | %s | %s |'
                        % (lid, os.path.basename(s.get('take', '-')), cers, s.get('cer_best', -1), s.get('matched', '-'),
                           num, heard, kw or '-', 'RETAKE' if s.get('retake') else 'ok'))
    notes = ['- line re-level to -16 LUFS before the stem gain (take LUFS -> dB): ' +
             ', '.join('%s %.1f -> %+.1f' % (k, v['level']['lufs_in'], v['level']['gain_db']) for k, v in dec.items()),
             '- stem gain %+.2f dB%s' % (A['loud']['gain_db'], ', limiter engaged' if A['loud']['limiter'] else
                                         ', no limiter')]
    for lid, v in dec.items():
        for n_ in v['notes']:
            notes.append('- %s: %s' % (lid, n_))
        for f_ in v['flags']:
            notes.append('- %s flag: %s' % (lid, f_))
        for f_ in v['fail']:
            notes.append('- **%s FAIL**: %s' % (lid, f_))
    cA, cB = chk['A'], chk['B']
    speech = sum(p['voice_off'] - p['voice_on'] for p in A['placed'])
    nwords = len(A['words'])
    txt = """# VO_TIMING: Reel 3 · C08 · Ek Frame ki Keemat (Vlad · elevenlabs_v4)

Status: **%s** · %s · `pipeline/jawad_reels/ek_frame_ki_keemat_vo.py assemble` · takes `%s` · V10 = `%s` · credits spent
for this reel: %s

Stems (48 kHz 24-bit mono): `%s` (hook A, 33.600 s; copy `vo_stem.wav`), `%s_hookb_vo.wav` (hook B, 0-3.000 s, V1B at
the A gain). Words (reel time; `keyword`, `line`, `i`, `hide`): `%s_vo.words.json` (= `words.json`), `%s_hookb_vo.words.json`.
QA image: `vo_timeline.png` (same folder).

| stem | LUFS | TP dBTP (<= -2) | LRA | first voice | last voice | loop seam | words ok | checks |
|---|---|---|---|---|---|---|---|---|
| A | %.2f | %.2f | %.1f | %.3f | %.3f | %s s | %d/%d | %s |
| B (3.0 s) | %.2f | %.2f | %.1f | %.3f | %.3f | - | %d/%d | %s |

## Per-beat timing (measured, reel time, vs the script.json targets)

"first word" = the anchor word's onset (snapped to voice by vo_chain); "end" = the last voiced sample of the segment;
"target end" = the line's ladder limit (split parts: the next part's onset minus the hold / gap). w/s and syl/s are per LINE.

| seg | beat | target on | first word | d on | target end | end | slack | speed | dur | words | w/s | syl/s | keyword @ t | flags |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
%s

Speech in A: %.2f s, %d words. Gaps (voice to voice): %s.
**Beats that miss their targets by > 0.3 s:** %s
Lines above 3.2 words/s: %s

## CER per line (faster-whisper int8, language hi, NO prompt; nukta / punctuation normalised; Latin loanwords and digits
mapped to the DEV spelling; whisper medium runs as a second ear only when small flags the line)

| line | take | CER small / medium | best | aligned | numbers | heard | critical words | verdict |
|---|---|---|---|---|---|---|---|---|
%s

z / f / q (nukta) consonants cannot be judged by ASR: the words marked (listen) need one listen before the master.

## Ladder steps applied (SCRIPT.md section 7)

%s
""" % (label, time.strftime('%Y-%m-%d %H:%M'), os.path.relpath(raw, REPO), v10, credits.get('spent_credits', 'n/a'),
       os.path.relpath(A['path'], REPO), REEL, REEL, REEL,
       cA['lufs_precise'], cA['tp_precise'], cA['lra'], cA['first_voice_s'], cA['last_voice_s'], cA.get('loop_seam_s'),
       cA['words_ok'], cA['words'], 'PASS' if not cA['fails'] else '; '.join(cA['fails']),
       cB['lufs_precise'], cB['tp_precise'], cB['lra'], cB['first_voice_s'], cB['last_voice_s'], cB['words_ok'],
       cB['words'], 'PASS' if not cB['fails'] else '; '.join(cB['fails']),
       '\n'.join(rows), speech, nwords, ', '.join('%s->%s %.3f' % g for g in cA['gaps']),
       '; '.join(misses) or 'none', '; '.join(fast) or 'none', '\n'.join(cer_rows), '\n'.join(notes) or '- none')
    os.makedirs(os.path.dirname(md), exist_ok=True)
    open(md, 'w', encoding='utf8').write(txt)
    print('->', md)


# ------------------------------------------------------------------------------------------------ CLI
def main(argv=None):
    import argparse
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('cmd', choices=['requests', 'pron', 'process', 'assemble', 'all'])
    ap.add_argument('--raw', default=os.path.join(RW, 'vo', 'raw'))
    ap.add_argument('--work', default=os.path.join(RW, 'vo'))
    ap.add_argument('--md', default=os.path.join(DESIGN, 'VO_TIMING.md'))
    ap.add_argument('--label', default='MEASURED (Vlad takes)')
    ap.add_argument('--lines', default='')
    ap.add_argument('--v10', default='usko', choices=['usko', 'usey'])
    ap.add_argument('--p2', action='store_true', help='SCRIPT 7 P2 for V9 + V10 (copy change: the lead OK first)')
    a = ap.parse_args(argv)
    only = [s for s in a.lines.split(',') if s]
    if a.cmd == 'requests':
        cmd_requests(a.work)
    if a.cmd == 'pron':
        cmd_pron(a.raw, a.work)
    if a.cmd in ('process', 'all'):
        cmd_process(a.raw, a.work, only, a.v10)
    if a.cmd in ('assemble', 'all'):
        cmd_assemble(a.raw, a.work, a.md, a.label, a.v10, a.p2)
    return 0


if __name__ == '__main__':
    sys.exit(main())
