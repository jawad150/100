"""log_kya_kahenge_vo.py - C15 "Log Kya Kahenge" VO: Vlad (Higgsfield elevenlabs_v4) takes -> processed lines
(vo_chain) -> the VO stems on the beat table (hook A and hook B) + reel-time word timings + VO_TIMING.md.

Sources (binding): brand_reels/design/reels/log_kya_kahenge/script.json (DEV / ROM tokens, windows, speeds) and
BRIEF.md r2 section 9 (windows, overrun rules). Only this reel's files are written; shared modules are imported read-only.

    cd pipeline/jawad_reels
    python3 -I log_kya_kahenge_vo.py requests                 # -> <RW>/vo/requests.json (Higgsfield payloads)
    tools/heavy.sh python3 -I log_kya_kahenge_vo.py pron      # whisper check of the carrier takes <RW>/vo/raw/lkk_P*_t*.mp3
    tools/heavy.sh python3 -I log_kya_kahenge_vo.py process   # each line take -> vo_chain passes at the line's speeds + CER
    tools/heavy.sh python3 -I log_kya_kahenge_vo.py assemble  # rules, placement, stems, words, VO_TIMING.md, checks
    options: --raw DIR (takes, default <RW>/vo/raw) --work DIR (outputs, default <RW>/vo) --md PATH --label TEXT
             --lines V1,V2 (process only these)

Takes are named lkk_<ID>_t<N>.mp3 (ID = V1, V1B, V2 ... V7; P1 ... P4 for the pronunciation carriers); the highest N
wins unless <work>/select.json maps an ID to a file name.

Outputs in <work>: proc/<ID>_t<N>_<speed>.wav (+ .words.json, .report.json from vo_chain), lines.json (every
measurement and decision), vo_stem.wav (= hook A), lkk_vo_A.wav, lkk_vo_B.wav (35.200 s, 48 kHz 24-bit mono, -16 LUFS
integrated, TP <= -2 dBTP), words.json (= A), lkk_vo_A.words.json, lkk_vo_B.words.json (reel time; snake_captions format
plus line / i / dev / heard / ok / hide), check.json; the timing table goes to --md (default VO_TIMING.md of the reel).
"""
import glob
import json
import os
import re
import subprocess
import sys
import time
import unicodedata

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import vo_chain as V  # noqa: E402  (read-only shared module)

REPO = os.path.abspath(os.path.join(HERE, '..', '..'))
RW = os.path.join(REPO, 'workspace', 'jawad_reels', 'log_kya_kahenge')
DESIGN = os.path.join(REPO, 'brand_reels', 'design', 'reels', 'log_kya_kahenge')
SCRIPT_JSON = os.path.join(DESIGN, 'script.json')
SR = 48000
DUR = 35.2
NSAMP = int(round(DUR * SR))
LUFS, TP_MAX = -16.0, -2.0
CER_MAX = 0.15
VOICE_ID = 'e5666b9c-99a2-4fac-8b4e-abee078b186d'

# ------------------------------------------------------------------------------------------------ the plan
# Windows and rules from BRIEF r2 section 9 + SCRIPT v2 section 2 (only these moves; never above 1.10x, never pitch).
# pauses: {token index: cap (s)} applied to the silence after that token ('always'), or only on overrun ('overrun').
PLAN = {
    'V1': dict(speeds=[1.10], onset=0.100, end=2.700, hard=2.850, over_pause=(3, 0.10), over_dur=2.60),
    'V1B': dict(speeds=[1.10], onset=0.100, end=2.700, hard=2.700, over_pause=(1, 0.30), over_dur=2.60),
    'V2': dict(speeds=[1.10], onset=8.800, end=14.833, hard=14.833, pauses={8: 0.30}),
    'V3': dict(speeds=[1.10], split=4, onset=16.367, onset2=18.200, onset2_range=(18.0, 18.3), end=19.133,
               hard=19.133, part1_max=1.45, part2_max=1.10),
    'V4': dict(speeds=[1.06, 1.10], onset=19.333, end=22.233, hard=22.233, pauses={4: 0.20}),
    'V5': dict(speeds=[1.08, 1.10], split=3, onset=22.400, onset2=23.667, end=25.400, hard=25.480,
               part1_end=23.467, part2_max={1.08: 1.733, 1.10: 1.78}, contains=23.600),
    'V6': dict(speeds=[1.05, 1.10], onset=26.000, onset_alt=25.933, end=29.100, hard=29.100, pauses={4: 0.20}),
    'V7': dict(speeds=[1.00, 1.03, 1.06, 1.10], onset=31.600, end=35.100, hard=35.100),
}
ORDER_A = ['V1', 'V2', 'V3', 'V4', 'V5', 'V6', 'V7']
ORDER_B = ['V1B', 'V2', 'V3', 'V4', 'V5', 'V6', 'V7']
NO_VO = [(15.85, 16.30, 'drop-out to the reveal'), (25.48, 25.90, 'floodlight clunk guard')]
HIDE_TOK = {'V1': {4, 5, 6}, 'V1B': {0, 1, 2, 3, 4, 5}, 'V7': set(range(10))}   # BRIEF section 15 (captions hidden)

# pronunciation carriers (step 1): every SCRIPT section 6 risk word, primary spelling and the fallback where one exists
PRON = [
    dict(id='P1', text='ये क्राउड फ़्लैट है। ये कार्डबोर्ड है।', words=['क्राउड', 'फ़्लैट', 'कार्डबोर्ड'],
         why='V3 risks 1, 2, 5 in their script spelling'),
    dict(id='P2', text='ये कार्ड-बोर्ड है। ये फ्लैट है।', words=['कार्ड-बोर्ड', 'फ्लैट'],
         why='V3 fallbacks (risk 1 hyphen, risk 2 no nukta)'),
    dict(id='P3', text='लोग बिज़ी हैं। उसकी नज़र में। अपनी ज़िंदगी। अपना फ़ोन।', words=['बिज़ी', 'नज़र', 'ज़िंदगी', 'फ़ोन'],
         why='z / f nukta words (risks 3, 4, 7, 8); ASR normalises nuktas, so a listener must confirm z and f'),
    dict(id='P4', text="हम भी 'लोग' हैं। हम भी लोग हैं।", words=["'लोग'", 'लोग'],
         why="risk 6: does the quoted 'log' hiccup or lose stress against the plain one"),
]
LOAN = {'crowd': 'क्राउड', 'flat': 'फ्लैट', 'cardboard': 'कार्डबोर्ड', 'card': 'कार्ड', 'board': 'बोर्ड',
        'busy': 'बिजी', 'edit': 'एडिट', 'video': 'वीडियो', 'phone': 'फोन'}


def load_script():
    d = json.load(open(SCRIPT_JSON, encoding='utf8'))
    lines = {l['id']: l for l in d['lines']}
    for k, l in lines.items():
        dev, rom = V.tokens(l['tts']), V.tokens(l['rom_tokens_marked'])
        if len(dev) != len(rom) or dev != l['dev_tokens']:
            raise ValueError('%s: DEV/ROM token mismatch (%d vs %d)' % (k, len(dev), len(rom)))
    return d, lines


# ------------------------------------------------------------------------------------------------ text metrics
def norm_cer(s):
    s = unicodedata.normalize('NFC', s.lower())
    s = s.replace('़', '').replace('ँ', 'ं')
    s = unicodedata.normalize('NFC', ''.join(V.NUKTA.get(ch, ch) for ch in unicodedata.normalize('NFD', s)))
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
    """Latin loanwords that whisper wrote in English -> the Devanagari spelling (a word heard as 'cardboard' was said)."""
    return re.sub(r'[A-Za-z]+', lambda m: LOAN.get(m.group(0).lower(), m.group(0)), hyp)


_WM = {}
KW_OK = 1.15     # vo_chain.sim >= 1.2: the heard word has the keyword's consonant skeleton (or spelling) exactly


def transcribe(path, prompt=None, model='small'):
    """faster-whisper (small, or medium for the cross-check) int8, language hi, word stamps; the audio is decoded by
    ffmpeg to a 16 kHz numpy array (the PyAV path is avoided). -> (text, words)."""
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


def best_match(word, heard):
    if not heard:
        return None, -1.0
    cands = [h['w'] for h in heard] + [a['w'] + b['w'] for a, b in zip(heard, heard[1:])]
    cands = [loan_map(c) for c in cands]
    sc = [V.sim(word, c) for c in cands]
    k = int(np.argmax(sc))
    return cands[k], round(float(sc[k]), 2)


# ------------------------------------------------------------------------------------------------ takes
def takes_for(raw, ident):
    fs = glob.glob(os.path.join(raw, 'lkk_%s_t*.mp3' % ident)) + glob.glob(os.path.join(raw, 'lkk_%s_t*.wav' % ident))
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
def cmd_requests(work):
    d, lines = load_script()

    def req(text):
        return dict(model='elevenlabs_v4', prompt=text,
                    dialogue=[dict(text=text, voice_id=VOICE_ID, voice_type='preset')])
    out = dict(
        reel='log_kya_kahenge', voice='Vlad (preset) on elevenlabs_v4', voice_id=VOICE_ID,
        rules=['balance first and before each batch; stop if the balance is below 7015',
               'preflight every request with get_cost: true; keep the running sum in vo/credits.json; reel budget 25',
               'leave use_unlim unset (answer an unlim_choice with false); omit folder_id; no stability override',
               'poll job ids with jobs_wait; never resubmit blindly',
               'download result_url with curl into vo/raw/ as lkk_<id>_t<n>.mp3 (n = 1 for the first take)'],
        batch_1_pronunciation=[dict(id=p['id'], save_as='lkk_%s_t1.mp3' % p['id'], why=p['why'], chars=len(p['text']),
                                    params=req(p['text'])) for p in PRON],
        batch_2_lines=[dict(id=k, save_as='lkk_%s_t1.mp3' % k, chars=len(lines[k]['tts']), params=req(lines[k]['tts']))
                       for k in ['V1', 'V1B', 'V2', 'V3', 'V4', 'V5', 'V6', 'V7']])
    os.makedirs(work, exist_ok=True)
    p = os.path.join(work, 'requests.json')
    json.dump(out, open(p, 'w', encoding='utf8'), ensure_ascii=False, indent=1)
    print('->', p)
    for b in ('batch_1_pronunciation', 'batch_2_lines'):
        print(b, sum(r['chars'] for r in out[b]), 'chars in', len(out[b]), 'requests')
    return out


# ------------------------------------------------------------------------------------------------ pron
def cmd_pron(raw, work):
    res = []
    for p in PRON:
        f = pick_take(raw, work, p['id'])
        if not f:
            res.append(dict(id=p['id'], missing=True))
            continue
        r = dict(id=p['id'], take=os.path.basename(f), text=p['text'], why=p['why'], dur=round(len(V.decode(f)) / SR, 3),
                 asr=[], words=[])
        heards = {}
        for model in ('small', 'medium'):
            txt, heard = transcribe(f, model=model)
            heards[model] = heard
            r['asr'].append(dict(model=model, heard=txt, cer=round(cer(txt, p['text']), 3),
                                 cer_loan=round(cer(loan_map(txt), p['text']), 3)))
        for w in p['words']:
            ms = [(model,) + best_match(w, heards[model]) for model in ('small', 'medium')]
            best = max(m[2] for m in ms)
            r['words'].append(dict(word=w, heard=ms, verdict='ok' if best >= KW_OK else 'fail',
                                   ear='\u093c' in unicodedata.normalize('NFD', w)))
        res.append(r)
        print(json.dumps(r, ensure_ascii=False))
    json.dump(res, open(os.path.join(work, 'pron_check.json'), 'w', encoding='utf8'), ensure_ascii=False, indent=1)
    return res


# ------------------------------------------------------------------------------------------------ process
def proc_path(work, take, speed):
    base = os.path.splitext(os.path.basename(take))[0]
    return os.path.join(work, 'proc', '%s_%.2f.wav' % (base, speed))


def process_line(lid, take, work, speed, lines, force=False):
    l = lines[lid]
    out = proc_path(work, take, speed)
    rep_p = os.path.splitext(out)[0] + '.report.json'
    if not force and os.path.exists(rep_p) and os.path.getmtime(rep_p) > os.path.getmtime(take):
        return json.load(open(rep_p))
    os.makedirs(os.path.dirname(out), exist_ok=True)
    return V.process(take, l['dev_tokens'], l['rom_tokens_marked'], out=out, speed=speed)


def cmd_process(raw, work, only=None):
    d, lines = load_script()
    state_p = os.path.join(work, 'lines.json')
    state = json.load(open(state_p)) if os.path.exists(state_p) else {}
    for lid in ['V1', 'V1B', 'V2', 'V3', 'V4', 'V5', 'V6', 'V7']:
        if only and lid not in only:
            continue
        take = pick_take(raw, work, lid)
        if not take:
            print(lid, 'no take in', raw)
            continue
        l = lines[lid]
        t0 = time.time()
        reps = {}
        for sp in PLAN[lid]['speeds']:
            reps['%.2f' % sp] = process_line(lid, take, work, sp, lines)
        plan_sp = PLAN[lid]['speeds'][0]
        fin = proc_path(work, take, plan_sp)
        kw = [i for i, r in enumerate(l['rom_tokens_marked']) if r.startswith('*')]
        words = json.load(open(os.path.splitext(fin)[0] + '.words.json'))

        def score(model):
            # CER: no initial prompt (the prompt would bias whisper toward the script)
            txt, heard = transcribe(fin, model=model)
            ks = []
            for i in kw:
                m, sc = best_match(l['dev_tokens'][i], heard)
                ks.append(dict(i=i, word=words[i]['word'], dev=l['dev_tokens'][i], heard=m, sim=sc))
            return dict(model=model, heard=txt, cer=round(cer(txt, l['tts']), 3),
                        cer_loan=round(cer(loan_map(txt), l['tts']), 3), keywords=ks)
        asr = [score('small')]
        weak = asr[0]['cer_loan'] > CER_MAX or any(k['sim'] < KW_OK for k in asr[0]['keywords'])
        if weak:                                   # independent second ear before calling a retake
            asr.append(score('medium'))
        best_cer = min(a['cer_loan'] for a in asr)
        kw_chk = []
        for j, i in enumerate(kw):
            sims = [a['keywords'][j]['sim'] for a in asr]
            best = max(sims)
            kw_chk.append(dict(i=i, word=words[i]['word'], dev=l['dev_tokens'][i], aligned_ok=words[i]['ok'],
                               aligned_heard=words[i]['heard'],
                               free=[(a['model'], a['keywords'][j]['heard'], a['keywords'][j]['sim']) for a in asr],
                               nukta='\u093c' in unicodedata.normalize('NFD', l['dev_tokens'][i]),
                               verdict='ok' if words[i]['ok'] and best >= KW_OK else 'retake'))
        state[lid] = dict(take=os.path.relpath(take, REPO), take_dur=round(len(V.decode(take)) / SR, 3),
                          heard=asr[0]['heard'], cer=asr[0]['cer'], cer_loan=asr[0]['cer_loan'], asr=asr,
                          cer_best=best_cer, keywords=kw_chk,
                          matched='%d/%d' % (sum(w['ok'] for w in words), len(words)),
                          unmatched=[(w['word'], w['heard']) for w in words if not w['ok']],
                          passes={k: dict(final_dur=r['final_dur'], speed=r['speed'], lufs=r['loudness']['lufs'],
                                          tp=r['loudness']['tp'], pauses=r['pauses'], wpm_after=r['wpm_after'],
                                          out=r['output']) for k, r in reps.items()},
                          retake=bool(best_cer > CER_MAX or any(k['verdict'] == 'retake' for k in kw_chk)),
                          listen=[k['word'] for k in kw_chk if k['nukta']],
                          seconds=round(time.time() - t0, 1))
        print(lid, json.dumps({k: state[lid][k] for k in ('cer', 'cer_loan', 'cer_best', 'matched', 'retake', 'listen',
                                                          'heard')}, ensure_ascii=False), flush=True)
        json.dump(state, open(state_p, 'w', encoding='utf8'), ensure_ascii=False, indent=1)
    return state


# ------------------------------------------------------------------------------------------------ editing
class Clip:
    """A processed line: 48 kHz float audio + word list (clip time)."""

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

    def gap_after(self, i):
        """The silence between token i and token i+1: the longest voiced-run gap inside [start_i, end_i+1]."""
        a, b = self.words[i]['start'], self.words[i + 1]['end']
        r = self.runs
        best = None
        for (p0, p1), (q0, q1) in zip(r, r[1:]):
            if p1 >= a and q0 <= b and q0 > p1:
                if best is None or q0 - p1 > best[1] - best[0]:
                    best = (p1, q0)
        return best

    def cap_gap(self, i, cap, xfade=0.005):
        """Shorten the pause after token i to `cap` s (never lengthens). -> (was, now)."""
        g = self.gap_after(i)
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
        shift = (ia - nx - ib) / SR                 # time shift of everything after the cut
        cut_t = (ib + nx) / SR
        for w in self.words:
            for k in ('start', 'end'):
                if w[k] >= cut_t - 1e-6:
                    w[k] = round(w[k] + shift, 3)
                elif w[k] > ia / SR:
                    w[k] = round(ia / SR, 3)
        return (round(b0 - a1, 3), round(cap, 3))

    def split_after(self, i, pad=0.04, fade=0.01):
        """Split in the pause after token i -> (clip1, clip2); each keeps `pad` s of silence at the cut."""
        g = self.gap_after(i)
        if not g:
            raise ValueError('no pause after token %d' % i)
        a1, b0 = g
        c1 = int(round(min(a1 + pad, (a1 + b0) / 2) * SR))
        c2 = int(round(max(b0 - pad, (a1 + b0) / 2) * SR))
        nf = int(fade * SR)
        x1, x2 = self.x[:c1].copy(), self.x[c2:].copy()
        x1[-nf:] *= np.linspace(1, 0, nf, dtype=np.float32)
        x2[:nf] *= np.linspace(0, 1, nf, dtype=np.float32)
        w1 = [dict(w) for w in self.words[:i + 1]]
        w2 = [dict(w, start=round(w['start'] - c2 / SR, 3), end=round(w['end'] - c2 / SR, 3))
              for w in self.words[i + 1:]]
        for w in w1:
            w['end'] = min(w['end'], round(c1 / SR, 3))
        for w in w2:
            w['start'] = max(w['start'], 0.0)
        return Clip(x1, w1), Clip(x2, w2)


def load_clip(work, take, speed):
    p = proc_path(work, take, speed)
    if not os.path.exists(p):
        raise FileNotFoundError(p)
    words = json.load(open(os.path.splitext(p)[0] + '.words.json'))
    for i, w in enumerate(words):
        w['i'] = i
    return Clip(V.decode(p), words)


# ------------------------------------------------------------------------------------------------ rules
def decide(lid, take, work, lines):
    """Apply the line's rules on the measured take. -> dict(segments=[(clip, onset, label)], speed, notes, fail)."""
    P = PLAN[lid]
    notes, fail = [], []

    def clip_at(sp):
        if not os.path.exists(proc_path(work, take, sp)):
            process_line(lid, take, work, sp, lines)
            notes.append('processed the %.2fx pass on demand' % sp)
        c = load_clip(work, take, sp)
        for i, cap in P.get('pauses', {}).items():
            was, now = c.cap_gap(i, cap)
            notes.append('pause after "%s" %.3f -> %.3f s' % (c.words[i]['word'], was, now))
        return c

    if lid in ('V1', 'V1B'):
        sp = P['speeds'][0]
        c = clip_at(sp)
        s0, s1 = c.span()
        if s1 - s0 > P['over_dur']:
            i, cap = P['over_pause']
            was, now = c.cap_gap(i, cap)
            notes.append('%.3f s > %.2f s: pause after "%s" %.3f -> %.3f s (overrun rule)'
                         % (s1 - s0, P['over_dur'], c.words[i]['word'], was, now))
        s0, s1 = c.span()
        if P['onset'] + (s1 - s0) > P['hard'] + 1e-6:
            fail.append('ends %.3f > hard %.3f: retake' % (P['onset'] + s1 - s0, P['hard']))
        return dict(segments=[(c, P['onset'], lid)], speed=sp, notes=notes, fail=fail)

    if lid == 'V2':
        sp = P['speeds'][0]
        c = clip_at(sp)
        s0, s1 = c.span()
        if P['onset'] + s1 - s0 > P['hard'] + 1e-6:
            fail.append('ends %.3f > %.3f with the 0.30 s pause: retake with the 14-word fallback'
                        % (P['onset'] + s1 - s0, P['hard']))
        return dict(segments=[(c, P['onset'], lid)], speed=sp, notes=notes, fail=fail)

    if lid == 'V3':
        sp = P['speeds'][0]
        c = clip_at(sp)
        c1, c2 = c.split_after(P['split'] - 1)
        d1 = c1.span()[1] - c1.span()[0]
        d2 = c2.span()[1] - c2.span()[0]
        on2 = P['onset2']
        if on2 + d2 > P['hard']:
            on2 = max(P['onset2_range'][0], P['hard'] - d2)
            notes.append('"Cardboard." moved to %.3f s to end by %.3f' % (on2, P['hard']))
        if d1 > P['part1_max']:
            fail.append('part 1 %.3f s > %.2f s' % (d1, P['part1_max']))
        if d2 > P['part2_max']:
            fail.append('"Cardboard." %.3f s > %.2f s: retake with the fallback spelling' % (d2, P['part2_max']))
        if P['onset'] + d1 > on2 - 0.15:
            fail.append('part 1 ends %.3f, < 0.15 s before "Cardboard." at %.3f' % (P['onset'] + d1, on2))
        if on2 + d2 > P['hard'] + 1e-6:
            fail.append('"Cardboard." ends %.3f > %.3f' % (on2 + d2, P['hard']))
        return dict(segments=[(c1, P['onset'], 'V3a'), (c2, on2, 'V3b')], speed=sp, notes=notes, fail=fail)

    if lid == 'V4':
        for sp in P['speeds']:
            c = clip_at(sp)
            s0, s1 = c.span()
            if P['onset'] + s1 - s0 <= P['hard'] + 1e-6:
                break
            notes.append('%.2fx ends %.3f > %.3f: next pass' % (sp, P['onset'] + s1 - s0, P['hard']))
        else:
            fail.append('ends %.3f > %.3f at 1.10x: retake V4' % (P['onset'] + s1 - s0, P['hard']))
        return dict(segments=[(c, P['onset'], lid)], speed=sp, notes=notes, fail=fail)

    if lid == 'V5':
        for sp in P['speeds']:
            c = clip_at(sp)
            c1, c2 = c.split_after(P['split'] - 1)
            d1 = c1.span()[1] - c1.span()[0]
            d2 = c2.span()[1] - c2.span()[0]
            ok1 = P['onset'] + d1 <= P['part1_end'] + 1e-6
            ok2 = d2 <= P['part2_max'][sp] + 1e-6
            if ok1 and ok2:
                break
            notes.append('%.2fx: part 1 %.3f s (ends %.3f, max %.3f), part 2 %.3f s (max %.3f): next pass'
                         % (sp, d1, P['onset'] + d1, P['part1_end'], d2, P['part2_max'][sp]))
        else:
            fail.append('part 2 %.3f s > 1.78 s at 1.10x (or part 1 late): retake with "हैं," and part 2 at 23.650' % d2)
        on2 = P['onset2']
        if on2 + d2 > P['hard']:
            fail.append('part 2 ends %.3f > 25.480 (clunk guard)' % (on2 + d2))
        return dict(segments=[(c1, P['onset'], 'V5a'), (c2, on2, 'V5b')], speed=sp, notes=notes, fail=fail)

    if lid == 'V6':
        onset = P['onset']
        for sp in P['speeds']:
            c = clip_at(sp)
            s0, s1 = c.span()
            if onset + s1 - s0 <= P['hard'] + 1e-6:
                break
            notes.append('%.2fx ends %.3f > %.3f: next pass' % (sp, onset + s1 - s0, P['hard']))
        else:
            onset = P['onset_alt']
            notes.append('onset moved to %.3f (f778)' % onset)
            if onset + s1 - s0 > P['hard'] + 1e-6:
                fail.append('ends %.3f > %.3f even at 1.10x from 25.933' % (onset + s1 - s0, P['hard']))
        return dict(segments=[(c, onset, lid)], speed=sp, notes=notes, fail=fail)

    if lid == 'V7':
        for sp in P['speeds']:
            c = clip_at(sp)
            s0, s1 = c.span()
            if P['onset'] + s1 - s0 <= P['hard'] + 1e-6:
                break
            notes.append('%.2fx ends %.3f > %.3f: next pass' % (sp, P['onset'] + s1 - s0, P['hard']))
        else:
            fail.append('ends %.3f > %.3f at 1.10x: retake V7' % (P['onset'] + s1 - s0, P['hard']))
        if sp > 1.06:
            notes.append('1.10x is outside the gate band 1.00-1.06x: tell the lead')
        return dict(segments=[(c, P['onset'], lid)], speed=sp, notes=notes, fail=fail)
    raise KeyError(lid)


# ------------------------------------------------------------------------------------------------ assemble
def place(segments):
    """[(clip, onset, label)] -> (stem, placed): the first voiced onset of each clip lands on its onset time."""
    y = np.zeros(NSAMP, np.float32)
    placed = []
    for c, onset, label in segments:
        s0, s1 = c.span()
        off = onset - s0
        i0 = int(round(off * SR))
        if i0 < 0:
            raise ValueError('%s would start before 0 s' % label)
        seg = c.x[: max(0, min(len(c.x), NSAMP - i0))]
        y[i0:i0 + len(seg)] += seg
        words = []
        for w in c.words:
            words.append(dict(w, start=round(w['start'] + off, 3), end=round(w['end'] + off, 3)))
        placed.append(dict(label=label, onset=round(onset, 3), voice_on=round(s0 + off, 3), voice_off=round(s1 + off, 3),
                           file_on=round(off, 3), file_off=round(off + c.dur, 3), words=words))
    return y, placed


def lufs_tp(x):
    """Integrated loudness and true peak with 2 decimals (ffmpeg loudnorm analysis pass)."""
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


def master(y, path):
    """Static gain to -16.0 LUFS integrated (+-0.05); a lookahead limiter only if the true peak passes -2.2 dBTP
    (then gain and limiter are iterated). 48 kHz 24-bit mono."""
    l0, tp0 = lufs_tp(y)
    z, lim, it = y.copy(), False, []
    g_tot = 0.0
    for k in range(4):
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
    V.write_wav(path, z)
    L3 = V.ebur128(path)
    li, tp = lufs_tp(V.decode(path))
    return dict(pre_lufs=round(l0, 2), pre_tp=round(tp0, 2), gain_db=round(g_tot, 2), limiter=lim, iterations=it,
                lufs_precise=round(li, 2), tp_precise=round(tp, 2), **L3)


def probe(path):
    out = subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'stream=sample_rate,channels,sample_fmt,bits_per_raw_sample,codec_name',
                          '-show_entries', 'format=duration', '-of', 'json', path], capture_output=True, text=True).stdout
    return json.loads(out)


def merge_words(placed, lines, order):
    out = []
    for p in placed:
        lid = re.sub(r'[ab]$', '', p['label'])
        lid = 'V1B' if p['label'] == 'V1B' else lid
        for w in p['words']:
            i = w.get('i')
            out.append(dict(word=w['word'], start=w['start'], end=w['end'], keyword=w['keyword'], line=lid, i=i,
                            dev=w['dev'], heard=w.get('heard', ''), ok=w.get('ok', False),
                            hide=i in HIDE_TOK.get(lid, set())))
    out.sort(key=lambda w: w['start'])
    return out


def kw_time(words, lid):
    return [(w['word'], w['start']) for w in words if w['line'] == lid and w['keyword']]


def syllables(dev):
    """Rough Devanagari syllable count: independent vowels + consonants not followed by a virama, per word."""
    n = 0
    for w in dev.split():
        w = re.sub(r'[^ऀ-ॿ]', '', w)
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
        # a final inherent 'a' is silent in Hindustani (schwa deletion): "log" is one syllable, not two
        if c > 1 and re.search(r'[क-हक़-य़]़?$', w):
            c -= 1
        n += max(1, c)
    return n


def cmd_assemble(raw, work, md, label):
    d, lines = load_script()
    state_p = os.path.join(work, 'lines.json')
    state = json.load(open(state_p)) if os.path.exists(state_p) else {}
    dec = {}
    for lid in ['V1', 'V1B', 'V2', 'V3', 'V4', 'V5', 'V6', 'V7']:
        take = pick_take(raw, work, lid)
        if not take:
            raise FileNotFoundError('no take for %s in %s' % (lid, raw))
        dec[lid] = decide(lid, take, work, lines)
        print(lid, 'speed %.2f' % dec[lid]['speed'], dec[lid]['notes'], dec[lid]['fail'] or 'OK', flush=True)
    stems = {}
    for name, order in (('A', ORDER_A), ('B', ORDER_B)):
        segs = [s for lid in order for s in dec[lid]['segments']]
        y, placed = place(segs)
        path = os.path.join(work, 'lkk_vo_%s.wav' % name)
        loud = master(y, path)
        words = merge_words(placed, lines, order)
        json.dump(words, open(os.path.splitext(path)[0] + '.words.json', 'w', encoding='utf8'), ensure_ascii=False,
                  indent=1)
        stems[name] = dict(path=path, loud=loud, placed=placed, words=words, probe=probe(path))
    # vo_stem.wav / words.json = hook A (the public version)
    import shutil
    shutil.copyfile(stems['A']['path'], os.path.join(work, 'vo_stem.wav'))
    shutil.copyfile(os.path.splitext(stems['A']['path'])[0] + '.words.json', os.path.join(work, 'words.json'))
    chk = checks(stems, dec, state)
    json.dump(dict(label=label, checks=chk, decisions={k: dict(speed=v['speed'], notes=v['notes'], fail=v['fail'])
                                                       for k, v in dec.items()},
                   stems={k: dict(loud=v['loud'], probe=v['probe'],
                                  placed=[{kk: vv for kk, vv in p.items() if kk != 'words'} for p in v['placed']])
                          for k, v in stems.items()}),
              open(os.path.join(work, 'check.json'), 'w', encoding='utf8'), ensure_ascii=False, indent=1)
    plot_timeline(stems, os.path.join(work, 'vo_timeline.png'))
    write_md(md, label, stems, dec, state, lines, chk, work, raw)
    print(json.dumps(chk, ensure_ascii=False, indent=1))
    return stems, dec, chk


def checks(stems, dec, state):
    out = {}
    for name, s in stems.items():
        y = V.decode(s['path'])
        runs = V.voiced_runs(y)
        st = s['probe']['streams'][0]
        c = dict(duration=float(s['probe']['format']['duration']), sr=int(st['sample_rate']), channels=st['channels'],
                 fmt=st.get('sample_fmt'), bits=st.get('bits_per_raw_sample'), lufs=s['loud']['lufs'], tp=s['loud']['tp'],
                 lufs_precise=s['loud']['lufs_precise'], tp_precise=s['loud']['tp_precise'], lra=s['loud']['lra'], fails=[])
        if abs(c['duration'] - DUR) > 0.002:
            c['fails'].append('duration %.4f' % c['duration'])
        if c['sr'] != SR or c['channels'] != 1:
            c['fails'].append('format %s Hz %s ch' % (c['sr'], c['channels']))
        if abs(c['lufs_precise'] - LUFS) > 0.1:
            c['fails'].append('loudness %.2f LUFS' % c['lufs_precise'])
        if max(c['tp'], c['tp_precise']) > TP_MAX:
            c['fails'].append('true peak %.2f dBTP' % max(c['tp'], c['tp_precise']))
        if str(c['bits']) != '24':
            c['fails'].append('bit depth %s' % c['bits'])
        for a, b, why in NO_VO:
            hit = [(round(r0, 3), round(r1, 3)) for r0, r1 in runs if r0 < b and r1 > a]
            if hit:
                c['fails'].append('voice inside %.2f-%.2f (%s): %s' % (a, b, why, hit))
        pl = s['placed']
        gaps = []
        for p, q in zip(pl, pl[1:]):
            g = q['voice_on'] - p['voice_off']
            gaps.append((p['label'], q['label'], round(g, 3)))
            if g < 0.15:
                c['fails'].append('gap %s -> %s %.3f s < 0.15 s' % (p['label'], q['label'], g))
            if q['file_on'] < p['file_off'] - 1e-3:
                c['fails'].append('files overlap %s / %s' % (p['label'], q['label']))
        c['gaps'] = gaps
        c['loop_seam_s'] = round(DUR - pl[-1]['voice_off'] + pl[0]['voice_on'], 3)
        c['first_voice_s'] = round(runs[0][0], 3) if runs else None
        c['last_voice_s'] = round(runs[-1][1], 3) if runs else None
        if c['first_voice_s'] is None or c['first_voice_s'] > 0.3:
            c['fails'].append('VO onset %s > 0.3 s' % c['first_voice_s'])
        w = s['words']
        if any(b['start'] < a['start'] for a, b in zip(w, w[1:])):
            c['fails'].append('word starts not monotone')
        c['words'] = len(w)
        c['words_ok'] = sum(x['ok'] for x in w)
        out[name] = c
    out['retakes'] = {k: v.get('retake') for k, v in state.items()}
    out['rule_fails'] = {k: v['fail'] for k, v in dec.items() if v['fail']}
    return out


# ------------------------------------------------------------------------------------------------ report
def seg_target(lab):
    lid = 'V1B' if lab == 'V1B' else re.sub(r'[ab]$', '', lab)
    P = PLAN[lid]
    if lab.endswith('a') and lid in ('V3', 'V5'):
        return lid, P['onset'], (P.get('part1_end') or P['onset2'] - 0.15)
    if lab.endswith('b') and lid in ('V3', 'V5'):
        return lid, P['onset2'], P['end']
    return lid, P['onset'], P['end']


def plot_timeline(stems, path):
    """QA image: the A stem's envelope on the 75 BPM grid, the target windows (grey), the placed voice (orange), keyword
    onsets (red ticks) and the no-VO guards (dark red). Hook B's V1B is drawn under the A row."""
    from PIL import Image, ImageDraw, ImageFont
    W, H, X0 = 2400, 520, 60
    sx = (W - 2 * X0) / DUR
    img = Image.new('RGB', (W, H), (12, 8, 7))
    d = ImageDraw.Draw(img)
    try:
        f = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 18)
    except OSError:
        f = ImageFont.load_default()
    X = lambda t: X0 + t * sx
    for k in range(int(DUR / 0.8) + 1):
        t = k * 0.8
        d.line([(X(t), 40), (X(t), H - 40)], fill=(70, 50, 45) if k % 4 else (140, 100, 90), width=1 if k % 4 else 2)
        if k % 4 == 0:
            d.text((X(t) + 3, 8), 'bar %d  %.1f s' % (k // 4, t), fill=(200, 180, 170), font=f)
    for a, b, why in NO_VO:
        d.rectangle([X(a), 40, X(b), H - 40], fill=(70, 10, 8))
    rows = [('A', stems['A'], 140), ('B', stems['B'], 360)]
    for name, s, yc in rows:
        y = V.decode(s['path'])
        hop = int(SR / sx) or 1
        env = np.sqrt(np.convolve(y.astype(np.float64) ** 2, np.ones(hop) / hop, 'same'))[::hop]
        env = env / (env.max() + 1e-9)
        for i, e in enumerate(env):
            d.line([(X0 + i, yc - e * 70), (X0 + i, yc + e * 70)], fill=(255, 106, 26))
        for p in s['placed']:
            lid, on, end = seg_target(p['label'])
            d.rectangle([X(on), yc + 80, X(end), yc + 96], outline=(180, 180, 180), width=2)
            d.rectangle([X(p['voice_on']), yc + 100, X(p['voice_off']), yc + 112], fill=(255, 159, 28))
            d.text((X(p['voice_on']), yc + 116), p['label'], fill=(255, 243, 230), font=f)
            for w in p['words']:
                if w['keyword']:
                    d.line([(X(w['start']), yc - 85), (X(w['start']), yc + 75)], fill=(242, 49, 43), width=3)
                    d.text((X(w['start']) + 4, yc - 95), w['word'].strip(',.?!\u0964'), fill=(255, 181, 71), font=f)
        d.text((8, yc - 10), name, fill=(255, 243, 230), font=f)
    img.save(path)
    return path


def write_md(md, label, stems, dec, state, lines, chk, work, raw):
    A = stems['A']
    wordsA = A['words']
    rows, misses = [], []
    segs = A['placed'] + [x for x in stems['B']['placed'] if x['label'] == 'V1B']
    line_dur = {}
    for p in segs:
        lid = seg_target(p['label'])[0]
        line_dur[lid] = line_dur.get(lid, 0.0) + p['voice_off'] - p['voice_on']
    for p in segs:
        lab = p['label']
        lid, tgt_on, tgt_end = seg_target(lab)
        l = lines[lid]
        ws = p['words']
        n = len(ws)
        dur = p['voice_off'] - p['voice_on']
        lw = len(l['dev_tokens']) / line_dur[lid]
        ls = syllables(l['tts']) / line_dur[lid]
        kws = ', '.join('*%s* @ %.3f' % (re.sub(r'[,.\u0964?!]+$', '', w['word']), w['start']) for w in ws if w['keyword'])
        d_on = p['voice_on'] - tgt_on
        d_end = p['voice_off'] - tgt_end
        flag = []
        if abs(d_on) > 0.3:
            flag.append('onset off by %+.3f s' % d_on)
        if d_end > 0.0:
            flag.append('ends %+.3f s after the window%s' % (d_end, ' (MISS > 0.3 s)' if d_end > 0.3 else ''))
        if lw > 3.2 and not lab.endswith('b'):
            flag.append('line %.2f w/s > 3.2 (syll/s %.2f)' % (lw, ls))
        if any(f_ for f_ in flag if 'MISS' in f_ or 'onset' in f_):
            misses.append('%s: %s' % (lab, '; '.join(flag)))
        rows.append('| %s | %s | %.3f | %.3f | %+.3f | %.3f | %.3f | %+.3f | %.2fx | %.3f | %d | %.2f | %.2f | %s | %s |'
                    % (lab, l['beat'], tgt_on, p['voice_on'], d_on, tgt_end, p['voice_off'], -d_end, dec[lid]['speed'],
                       dur, n, lw, ls, kws or '-', '; '.join(flag) or 'ok'))
    cer_rows = []
    for lid in ['V1', 'V1B', 'V2', 'V3', 'V4', 'V5', 'V6', 'V7']:
        s = state.get(lid, {})
        asr = s.get('asr', [])
        heard = ' / '.join('%s: %s' % (a['model'], a['heard']) for a in asr) or '-'
        cers = ' / '.join('%.3f (%.3f)' % (a['cer'], a['cer_loan']) for a in asr) or '-'
        kw = '; '.join('*%s* aligned "%s", free %s -> %s' % (re.sub(r'[,.\u0964?!]+$', '', k['word']), k['aligned_heard'],
                                                            ', '.join('%s "%s" %.2f' % (m, h, sc) for m, h, sc in k['free']),
                                                            k['verdict']) for k in s.get('keywords', []))
        cer_rows.append('| %s | %s | %s | %.3f | %s | %s | %s | %s |'
                        % (lid, os.path.basename(s.get('take', '-')), cers, s.get('cer_best', -1), s.get('matched', '-'),
                           heard, kw or '-', 'RETAKE' if s.get('retake') else ('ok; z/f by ear: ' + ', '.join(s['listen'])
                                                                              if s.get('listen') else 'ok')))
    notes = []
    for lid, v in dec.items():
        for n_ in v['notes']:
            notes.append('- %s: %s' % (lid, n_))
        for f_ in v['fail']:
            notes.append('- **%s FAIL**: %s' % (lid, f_))
    cA, cB = chk['A'], chk['B']
    speech = sum(p['voice_off'] - p['voice_on'] for p in A['placed'])
    txt = """# VO_TIMING: Reel 5 · C15 · Log Kya Kahenge (Vlad · elevenlabs_v4)

Status: **%s** · generated %s by `pipeline/jawad_reels/log_kya_kahenge_vo.py assemble` · takes: `%s`

Stems (35.200 s, 48 kHz 24-bit mono): `%s` (= hook A; also `lkk_vo_A.wav`), `lkk_vo_B.wav` (hook B). Words: `words.json`
(= A), `lkk_vo_A.words.json`, `lkk_vo_B.words.json` (reel time, `keyword`, `line`, `i`, `hide` per BRIEF section 15). QA image:
`vo_timeline.png` (same folder).

| stem | LUFS (target -16) | TP dBTP (<= -2) | LRA | first voice | last voice | loop seam (V7 end -> V1 start) | words ok | checks |
|---|---|---|---|---|---|---|---|---|
| A | %.2f | %.2f | %.1f | %.3f | %.3f | %.3f s | %d/%d | %s |
| B | %.2f | %.2f | %.1f | %.3f | %.3f | %.3f s | %d/%d | %s |

## Per-beat timing (measured voiced onset / offset in reel time vs the BRIEF r2 section 9 windows)

Onsets are placed on the grid onsets (first voiced sample of each segment). "target end" = the window end (V3a: 0.15 s before
*Cardboard*; V5a: 23.467). w/s and syll/s are per LINE (all its segments' voiced time; syllables approximate).

| seg | beat | target on | on | d on | target end | end | slack | speed | dur | words | line w/s | line syll/s | keyword @ t | flags |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
%s

Speech in A: %.2f s (%d words). Gaps (voice to voice, A): %s.
Beats that miss their targets by > 0.3 s: %s

## CER per line (faster-whisper int8, language hi, NO prompt; CER after nukta / punctuation normalisation, in brackets with English
words whisper wrote in Latin mapped back to the DEV spelling; whisper medium is run as a second ear only when small flags the line)

| line | take | CER small / medium | best | aligned (vo_chain) | heard | keywords | verdict |
|---|---|---|---|---|---|---|---|
%s

## Rules applied (BRIEF r2 section 9 / SCRIPT v2 section 2)

%s
""" % (label, time.strftime('%Y-%m-%d %H:%M'), os.path.relpath(raw, REPO), os.path.relpath(os.path.join(work, 'vo_stem.wav'), REPO),
       cA['lufs_precise'], cA['tp_precise'], cA['lra'], cA['first_voice_s'], cA['last_voice_s'], cA['loop_seam_s'], cA['words_ok'],
       cA['words'], 'PASS' if not cA['fails'] else '; '.join(cA['fails']),
       cB['lufs_precise'], cB['tp_precise'], cB['lra'], cB['first_voice_s'], cB['last_voice_s'], cB['loop_seam_s'], cB['words_ok'],
       cB['words'], 'PASS' if not cB['fails'] else '; '.join(cB['fails']),
       '\n'.join(rows), speech, len(wordsA), ', '.join('%s->%s %.3f' % g for g in cA['gaps']), '; '.join(misses) or 'none',
       '\n'.join(cer_rows), '\n'.join(notes) or '- none')
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
    a = ap.parse_args(argv)
    only = [s for s in a.lines.split(',') if s]
    if a.cmd == 'requests':
        cmd_requests(a.work)
    if a.cmd == 'pron':
        cmd_pron(a.raw, a.work)
    if a.cmd in ('process', 'all'):
        cmd_process(a.raw, a.work, only)
    if a.cmd in ('assemble', 'all'):
        cmd_assemble(a.raw, a.work, a.md, a.label)
    return 0


if __name__ == '__main__':
    sys.exit(main())
