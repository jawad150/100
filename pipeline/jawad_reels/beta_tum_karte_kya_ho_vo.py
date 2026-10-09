"""beta_tum_karte_kya_ho_vo.py - C02 "Beta, tum karte kya ho?" VO: Vlad (Higgsfield elevenlabs_v4) line takes ->
vo_chain -> the reel-time VO stems (version A and B, 36.4 s) + word timings + VO_TIMING.md.

Sources (binding): brand_reels/design/reels/beta_tum_karte_kya_ho/script.json (lines, DEV / ROM tokens, slots, per-line
vo_chain cap / keep_cap, fallbacks) = SCRIPT.md sections 6-7 and BRIEF.md section 6.7. Only this reel's files are
written; vo_chain is imported read-only.

    cd /home/user/100/pipeline/jawad_reels
    python3 -I beta_tum_karte_kya_ho_vo.py requests                 # -> <RW>/vo/requests.json (Higgsfield payloads)
    tools/heavy.sh python3 -I beta_tum_karte_kya_ho_vo.py pron [--model small|medium]   # carriers <raw>/btk_P*_t*.mp3
    tools/heavy.sh python3 -I beta_tum_karte_kya_ho_vo.py process   # every candidate take -> vo_chain ladder + 2x ASR
    tools/heavy.sh python3 -I beta_tum_karte_kya_ho_vo.py assemble  # selection, placement, stems, words, VO_TIMING.md
    options: --only L2,L7 (process only these lines)

Takes: <raw>/btk_<ID>_t<N>.mp3. ID = a line (L1 L1B L2 ... L11: the script.json text) or a line variant 'L3-N'
(VARIANTS below: a prosody / spelling variant or the script's own fallback wording, same slot); P0-P11 = pronunciation
carriers. Every take of a line is a candidate; select() picks one (rules in its docstring) unless <work>/select.json maps
the line to '<take>@<step>'. <work>/spelling.json maps a DEV word to the spelling the pronunciation check chose: applied
to the requests AND to the alignment text (1:1, so the token counts never change).

Ladder per candidate (SCRIPT 3 / 7, vo_config: 1.06-1.10x, never above 1.10, never pitch): '1.08' (the script's caps),
'1.10', '1.10t' (1.10x with the pauses capped tighter: cap <= 0.25 s, dramatic keep_cap <= 0.30 s); L11 also '1.06'.
L11 onset ladder (SCRIPT 7): 34.90, earlier down to 34.70 if the voice would end after 36.35.

Outputs in <work> (= workspace/jawad_reels/beta_tum_karte_kya_ho/vo): proc/<take>_<step>.wav (+ .words.json /
.report.json from vo_chain), lines.json (per take: ASR small + medium, CER, voice times per step), selection.json,
vo_stem.wav (= beta_tum_karte_kya_ho_vo_A.wav, version A, 36.400 s, 48 kHz 24-bit mono, -16.0 LUFS integrated,
TP <= -2 dBTP), beta_tum_karte_kya_ho_vo_B.wav (hook B + the same body at the same gain), words.json (=
beta_tum_karte_kya_ho.words.json, version A, reel time, snake_captions.load_words format + line / i / dev / heard / ok /
hide), words_B.json, check.json, vo_timeline.png, vo_lines.png.
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
import vo_chain as V  # noqa: E402  (shared, read-only)

REPO = os.path.abspath(os.path.join(HERE, '..', '..'))
REEL = 'beta_tum_karte_kya_ho'
RW = os.path.join(REPO, 'workspace', 'jawad_reels', REEL)
WORK = os.path.join(RW, 'vo')
RAW = os.path.join(WORK, 'raw')
DESIGN = os.path.join(REPO, 'brand_reels', 'design', 'reels', REEL)
SCRIPT_JSON = os.path.join(DESIGN, 'script.json')
MD = os.path.join(DESIGN, 'VO_TIMING.md')
SR = 48000
FPS = 30
DUR = 36.4
NSAMP = int(round(DUR * SR))
BEAT = 0.7                     # 85.714 BPM = 600/7 -> 0.7 s = 21 frames
LUFS, TP_MAX = -16.0, -2.0
CER_MAX = 0.15
VOICE_ID = 'e5666b9c-99a2-4fac-8b4e-abee078b186d'
PREFIX = 'btk'
ORDER_A = ['L1', 'L2', 'L3', 'L4', 'L5', 'L6', 'L7', 'L8', 'L9', 'L10', 'L11']
ORDER_B = ['L1B'] + ORDER_A[1:]
ALL_LINES = ['L1', 'L1B'] + ORDER_A[1:]
TOL = 0.15                     # BRIEF 6.7: a line may end <= end_target + 0.15 s
HARD_END = {'L1': 2.69, 'L1B': 2.45, 'L11': 36.35}     # SCRIPT 7 hard limits (L1 QA 2.75; L11 gate 36.36)
MIN_GAP = 0.15                 # voice-to-voice gap between lines (and across the loop seam)
L11_ONSET_MIN = 34.70          # SCRIPT 7 / script.json L11 fallback ladder: never before 34.70, never after 34.95
STEPS = {k: ['1.08', '1.10', '1.10t'] for k in ALL_LINES}
STEPS['L11'] = ['1.06', '1.08', '1.10', '1.10t']
HIDE = {'L1B', 'L6', 'L10', 'L11'}          # captions hidden (script.json caption_notes)
KIND_RANK = {'script': 0, 'prosody': 1, 'fallback': 2}

# ------------------------------------------------------------------------------------------------ line variants
# Same slot, same ROM caption track (1:1 tokens). 'prosody' = punctuation / spelling only (same words); 'fallback' =
# the wording script.json / SLATE already list as the line's fallback (fewer words). Added after the first takes
# measured long (VO_TIMING.md): isolated Vlad lines run ~25-40 % slower than the script's rate model.
VARIANTS = {
    'L1-F': dict(line='L1', kind='fallback', dev='ये सवाल क्लायंट नहीं पूछता।', rom='Yeh sawaal client nahi poochta.',
                 why='SLATE 3.4 fallback; the locked line measured 3.28 s of voice (limit 2.59 s from 0.10)'),
    'L2-C': dict(line='L2', kind='prosody', dev='जवाब का ट्रांसलेशन,', rom='Jawab ka *translation...',
                 why='"..." stretched "translation" (0.74 s); a comma keeps the open, continuing tone'),
    'L3-N': dict(line='L3', kind='prosody', dev='जितना समझाओ उतना उल्टा।', rom='Jitna samjhao, utna *ulta.',
                 why='no comma: one breath, no beat (the take ran 0.7 s over and into the 7.0 pop)'),
    'L5-C': dict(line='L5', kind='prosody', dev='फिर, हार मान ली।', rom='Phir... *haar maan li.',
                 why='"Phir..." was drawn out to 1.0 s; a comma beat is shorter'),
    'L6-C': dict(line='L6', kind='prosody', dev='कुछ महीने बाद,', rom='Kuch mahine baad...',
                 why='"baad..." stretched; a comma ending'),
    'L6-F': dict(line='L6', kind='fallback', dev='महीने बाद...', rom='Mahine baad...',
                 why='script.json L6 fallback (2 words)'),
    'L7-C': dict(line='L7', kind='prosody', dev='फिर एक दिन फ़ैमिली ग्रुप में, एक रील फ़ॉर्वर्ड होती है।',
                 rom='Phir ek din family group mein... ek *reel forward hoti hai.',
                 why='comma beat instead of "..." (shorter) + the SCRIPT 6 rank 7 fallback spelling फ़ॉर्वर्ड (r kept)'),
    'L11-F': dict(line='L11', kind='fallback', dev='अब नानी।', rom='Ab Nani.',
                  why='script.json L11 fallback (the loop line must end <= 36.35 s)'),
    # round 2 (after the round-1 measurements): L3 cannot fit 1.85 s with 4 words at Vlad's isolated-line rate (best
    # 2.52 s), so a 3-word cut (BRIEF 6.7: overrun > 0.15 s -> cut words; L3 is not SLATE-locked; lead's OK flagged)
    'L3-S': dict(line='L3', kind='fallback', dev='समझाओ तो उल्टा।', rom='Samjhao toh *ulta.',
                 why='word cut: 4 words cannot fit 1.85 s (best 2.52 s); same joke, keyword *ulta* kept'),
    'L3-J': dict(line='L3', kind='fallback', dev='जितना समझाओ, उल्टा।', rom='Jitna samjhao, *ulta.',
                 why='word cut (alternative to L3-S): drops "utna"'),
    'L1B-R': dict(line='L1B', kind='prosody', dev='मम्मी के लिए, कारटून।', rom='Mummy ke liye, cartoon.',
                  why='both ASR models heard कार्टून as काटून (r dropped) in both takes; full र spelling'),
    'L7-O': dict(line='L7', kind='prosody', dev='फिर एक दिन फ़ैमिली ग्रुप में, एक रील फ़ोरवर्ड होती है।',
                 rom='Phir ek din family group mein... ek *reel forward hoti hai.',
                 why='both ASR models heard फ़ॉरवर्ड / फ़ॉर्वर्ड as फोवर्ड (first r dropped) in 3 takes; ो + full र '
                     '(the कारटून fix brought the r back in L1B) + the L7-C comma beat that fits the slot'),
}

# ------------------------------------------------------------------------------------------------ pronunciation carriers
# SCRIPT.md section 6 ranks 1-13 in short carrier phrases (one request each, one batch); the fallback spellings of the
# rank 1, 2, 4, 5 words run in the same batch so a spelling decision needs no second round. 'check' = the words judged.
PRON = [
    dict(id='P0', text='ये सवाल क्लाइंट नहीं पूछता।', check=['क्लाइंट', 'पूछता'], why='rank 1 client (L1), rank 10 poochta'),
    dict(id='P1', text='ये सवाल क्लायंट नहीं पूछता।', check=['क्लायंट', 'पूछता'], why='rank 1 fallback spelling'),
    dict(id='P2', text='मम्मी बोलीं, कार्टून।', check=['मम्मी', 'कार्टून'], why='rank 2 Mummy (L1B, L8), rank 6 cartoon'),
    dict(id='P3', text='ममी बोलीं, कार्टून।', check=['ममी', 'कार्टून'], why='rank 2 fallback spelling'),
    dict(id='P4', text='पहले इसका ट्रांसलेशन करो।', check=['ट्रांसलेशन'], why='rank 4 translation (L2 keyword)'),
    dict(id='P5', text='पहले इसका ट्रैन्सलेशन करो।', check=['ट्रैन्सलेशन'], why='rank 4 fallback spelling'),
    dict(id='P6', text='फ़ैमिली ग्रुप में भेजो।', check=['फ़ैमिली', 'ग्रुप', 'भेजो'], why='rank 5 family group, rank 3 bhejo'),
    dict(id='P7', text='फ़ेमिली ग्रुप में भेजो।', check=['फ़ेमिली', 'ग्रुप', 'भेजो'], why='rank 5 fallback spelling'),
    dict(id='P8', text='एक रील फ़ॉरवर्ड हुई।', check=['रील', 'फ़ॉरवर्ड'], why='rank 7 forward (L7)'),
    dict(id='P9', text='सब उल्टा है, सब सीधा है।', check=['उल्टा', 'सीधा'], why='rank 8 ulta (L3 keyword), rank 9 seedha'),
    dict(id='P10', text='सब की नज़र उन पे, वो ख़ुद हमसे बेहतर हैं।', check=['नज़र', 'ख़ुद', 'हमसे', 'बेहतर'],
         why='rank 11 khud / nazar, rank 12 behtar'),
    dict(id='P11', text='अब नानी की बारी आई।', check=['नानी', 'बारी'], why='rank 13 Nani / baari (L11)'),
]
ASPIRATED = {'भेजो': 'भ', 'सीधा': 'ध', 'पूछता': 'छ', 'ख़ुद': 'ख', 'बेहतर': 'ह', 'समझाती': 'झ'}

# whisper sometimes writes an English loan in Latin or a spoken form in its book spelling: mapped back before the CER
# (each is the same spoken word; listed so the CER never hides a different word)
LOAN = {'client': 'क्लाइंट', 'translation': 'ट्रांसलेशन', 'family': 'फ़ैमिली', 'group': 'ग्रुप', 'reel': 'रील',
        'reels': 'रील', 'forward': 'फ़ॉरवर्ड', 'cartoon': 'कार्टून', 'mummy': 'मम्मी', 'mommy': 'मम्मी'}
VARIANT = {'वह': 'वो', 'लिये': 'लिए', 'पर': 'पे'}      # SCRIPT 4: book form -> the spoken form the script uses
PUNCT_END = re.compile(r'[,.!?;:।…]+$')


def nfc(s):
    return unicodedata.normalize('NFC', s)


# ------------------------------------------------------------------------------------------------ script
def load_fixes(work=WORK):
    p = os.path.join(work, 'spelling.json')
    return {nfc(k): nfc(v) for k, v in json.load(open(p, encoding='utf8')).items()} if os.path.exists(p) else {}


def fix_token(tok, fixes):
    tok = nfc(tok)
    core = PUNCT_END.sub('', tok)
    return tok.replace(core, fixes[core], 1) if core in fixes else tok


def fix_text(text, fixes):
    return ' '.join(fix_token(t, fixes) for t in nfc(text).split())


def load_script(work=WORK):
    d = json.load(open(SCRIPT_JSON, encoding='utf8'))
    fixes = load_fixes(work)
    lines = {}
    for l in d['lines']:
        if l['id'] not in ALL_LINES:
            continue
        l = dict(l)
        l['req'] = fix_text(l['dev'], fixes)
        dev, rom = V.tokens(l['req']), V.tokens(l['rom_chain'])
        if len(dev) != len(rom):
            raise ValueError('%s: DEV %d tokens vs ROM %d' % (l['id'], len(dev), len(rom)))
        l['dev_tokens'], l['rom_tokens'] = dev, rom
        risk = [fix_token(w, fixes) for r in d.get('pron_risk', []) if l['id'] in r.get('lines', [])
                for w in r['word'].split()]
        l['risk'] = [w for w in risk if re.search('[\u0900-\u097f]', w)]
        lines[l['id']] = l
    return d, lines


def ident_text(ident, lines, fixes=None):
    """A take ID ('L3' or 'L3-N') -> dict(line, kind, req, dev_tokens, rom_tokens, keywords to check)."""
    fixes = load_fixes() if fixes is None else fixes
    if ident in VARIANTS:
        v = VARIANTS[ident]
        l = lines[v['line']]
        req = fix_text(v['dev'], fixes)
        dev, rom = V.tokens(req), V.tokens(v['rom'])
        if len(dev) != len(rom):
            raise ValueError('%s: DEV %d tokens vs ROM %d' % (ident, len(dev), len(rom)))
        kind, why = v['kind'], v['why']
    else:
        l = lines[ident]
        req, dev, rom, kind, why = l['req'], l['dev_tokens'], l['rom_tokens'], 'script', 'script.json text'
    cores = [PUNCT_END.sub('', t) for t in dev]
    key = [PUNCT_END.sub('', d) for d, r in zip(dev, rom) if r.startswith('*')]
    risk = [w for w in l['risk'] if w in cores]
    # the risk words of the original text that the variant respells (फ़ॉरवर्ड -> फ़ॉर्वर्ड) are checked in their new form
    for w in l['risk']:
        if w not in cores:
            near = [c for c in cores if V.skel(c) == V.skel(w)]
            risk += near
    return dict(line=l['id'], ident=ident, kind=kind, why=why, req=req, dev_tokens=dev, rom_tokens=rom,
                check=list(dict.fromkeys(key + risk)), vo_chain=l.get('vo_chain') or {})


def req(text):
    return dict(model='elevenlabs_v4', prompt=text, dialogue=[dict(text=text, voice_id=VOICE_ID, voice_type='preset')])


def check_tts_text(lid, text):
    bad = re.findall(r'[0-9A-Za-z\[\]()<>#@*:]', text)
    if bad:
        raise ValueError('%s: TTS text has %s' % (lid, bad))
    if nfc(text) != text:
        raise ValueError('%s: not NFC' % lid)


def cmd_requests(work=WORK):
    d, lines = load_script(work)
    for p in PRON:
        check_tts_text(p['id'], p['text'])
    for k in ALL_LINES:
        check_tts_text(k, lines[k]['req'])
    var = {k: ident_text(k, lines) for k in VARIANTS}
    for k, v in var.items():
        check_tts_text(k, v['req'])
    out = dict(
        reel=REEL, voice='Vlad (preset) on elevenlabs_v4', voice_id=VOICE_ID,
        rules=['balance first and before each batch; STOP if the balance is below 6800',
               'preflight every request with get_cost: true; keep the running sum in vo/credits.json; reel budget 25',
               'leave use_unlim unset (answer an unlim_choice with false); omit folder_id; provider default stability',
               'poll job ids with jobs_wait; never resubmit blindly',
               'download result_url with curl into vo/raw/ as %s_<id>_t<n>.mp3' % PREFIX],
        spelling_fixes=load_fixes(work),
        batch_1_pronunciation=[dict(id=p['id'], save_as='%s_%s_t1.mp3' % (PREFIX, p['id']), why=p['why'],
                                    chars=len(p['text']), params=req(p['text'])) for p in PRON],
        batch_2_lines=[dict(id=k, save_as='%s_%s_t1.mp3' % (PREFIX, k), chars=len(lines[k]['req']),
                            slot='%.2f-%.2f' % (lines[k]['start_target'], lines[k]['end_target']),
                            params=req(lines[k]['req'])) for k in ALL_LINES],
        variants=[dict(id=k, line=v['line'], kind=v['kind'], why=v['why'], chars=len(v['req']), rom=' '.join(
            v['rom_tokens']), params=req(v['req'])) for k, v in var.items()])
    os.makedirs(work, exist_ok=True)
    p = os.path.join(work, 'requests.json')
    json.dump(out, open(p, 'w', encoding='utf8'), ensure_ascii=False, indent=1)
    print('->', p)
    for b in ('batch_1_pronunciation', 'batch_2_lines', 'variants'):
        print(b, sum(r['chars'] for r in out[b]), 'chars in', len(out[b]), 'requests')
    return out


# ------------------------------------------------------------------------------------------------ text metrics
def devify(text, fixes=None):
    fixes = load_fixes() if fixes is None else fixes
    return re.sub(r'[A-Za-z]+', lambda m: fixes.get(LOAN.get(m.group(0).lower(), ''), LOAN.get(m.group(0).lower(),
                                                                                                m.group(0))), text)


def norm_cer(s, variants=True):
    """Text -> the character string the CER compares: Latin loans mapped to the script's Devanagari, nukta and
    chandrabindu folded (whisper drops them), punctuation and spaces removed. variants=True also folds the spoken-form
    pairs of VARIANT and two orthographic equivalents (a half nasal before a consonant = the anusvara; the virama of a
    cluster): same sounds, different spellings. variants=False = the strict CER."""
    s = devify(nfc(s))
    if variants:
        s = ' '.join(VARIANT.get(V.PUNCT.sub('', w), w) for w in s.split())
    s = unicodedata.normalize('NFD', s.lower())
    s = ''.join(V.NUKTA.get(ch, ch) for ch in s)
    s = unicodedata.normalize('NFC', s).replace('ँ', 'ं')
    s = s.replace('‌', '').replace('‍', '')
    # keep letters, marks (the matras and the virama are category M: a plain [^\w] strips every vowel sign) and digits
    s = ''.join(ch for ch in s if unicodedata.category(ch)[0] in 'LMN')
    if variants:
        s = re.sub('[ङञणनम]्', 'ं', s).replace('्', '')
    return s


def lev(a, b):
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        cur = [i]
        for j, cb in enumerate(b, 1):
            cur.append(min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + (ca != cb)))
        prev = cur
    return prev[-1]


def cer(hyp, ref, variants=True):
    r = norm_cer(ref, variants)
    return lev(norm_cer(hyp, variants), r) / max(1, len(r))


_WM = {}


def transcribe(path, prompt=None, model='small'):
    """faster-whisper int8, language hi, word stamps; audio decoded by ffmpeg to a 16 kHz mono float array (never the
    PyAV path). No initial prompt by default, so the script text cannot bias the check."""
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


def heard_tokens(text):
    return [t for t in devify(nfc(text)).split() if V.norm_dev(t)]


def word_verdict(word, toks):
    """-> dict(heard, score, verdict): 'exact' = the heard word is the word after nukta / chandrabindu normalising;
    'skeleton' = same consonant skeleton (vo_chain.skel: vowel length and aspiration ignored, so listen); 'fail'."""
    if not toks:
        return dict(heard=None, score=-1.0, verdict='fail')
    cands = toks + [a + b for a, b in zip(toks, toks[1:])]
    sc = [V.sim(word, c) for c in cands]
    k = int(np.argmax(sc))
    h = cands[k]
    nw, nh = V.norm_dev(word), V.norm_dev(h)
    verdict = 'exact' if nw == nh else ('skeleton' if V.skel(word) == V.skel(h) else 'fail')
    out = dict(heard=h, score=round(float(sc[k]), 2), verdict=verdict)
    asp = ASPIRATED.get(word)
    if asp:
        out['aspirate_heard'] = asp in h
    return out


def asr_check(path, t, model):
    text, _ = transcribe(path, model=model)
    toks = heard_tokens(text)
    return dict(heard=text, cer=round(cer(text, t['req']), 3), cer_strict=round(cer(text, t['req'], False), 3),
                words={w: word_verdict(w, toks) for w in t['check']})


# ------------------------------------------------------------------------------------------------ takes
def take_ident(path):
    m = re.match(r'%s_(.+)_t(\d+)\.mp3$' % PREFIX, os.path.basename(path))
    return (m.group(1), int(m.group(2))) if m else (None, None)


def candidates(raw, lid):
    """Every take of a line: btk_<lid>_t<n>.mp3 and btk_<lid>-<variant>_t<n>.mp3 (variants registered in VARIANTS)."""
    out = []
    for f in sorted(glob.glob(os.path.join(raw, '%s_*_t*.mp3' % PREFIX))):
        ident, n = take_ident(f)
        if ident == lid or (ident in VARIANTS and VARIANTS[ident]['line'] == lid):
            out.append(f)
    return out


def takes_for(raw, ident):
    fs = glob.glob(os.path.join(raw, '%s_%s_t*.mp3' % (PREFIX, ident)))
    return sorted(fs, key=lambda f: take_ident(f)[1])


# ------------------------------------------------------------------------------------------------ pron
def cmd_pron(raw=RAW, work=WORK, model='small'):
    res = []
    for p in PRON:
        for f in takes_for(raw, p['id']):
            text, words = transcribe(f, model=model)
            toks = heard_tokens(text)
            r = dict(id=p['id'], take=os.path.basename(f), model=model, text=p['text'], why=p['why'],
                     dur=round(len(V.decode(f)) / SR, 3), heard=text, cer=round(cer(text, p['text']), 3),
                     cer_strict=round(cer(text, p['text'], False), 3),
                     words={w: word_verdict(w, toks) for w in p['check']})
            res.append(r)
            print(json.dumps(r, ensure_ascii=False), flush=True)
    json.dump(res, open(os.path.join(work, 'pron_check_%s.json' % model), 'w', encoding='utf8'), ensure_ascii=False,
              indent=1)
    return res


# ------------------------------------------------------------------------------------------------ process
def proc_path(work, take, step):
    """step '1.08' (script caps) / '1.10t' (tight caps) -> proc/<take>_<1.08|1.10t>.wav"""
    return os.path.join(work, 'proc', '%s_%s.wav' % (os.path.splitext(os.path.basename(take))[0], step))


def step_kw(t, step):
    vc = t['vo_chain']
    cap = float(vc.get('cap') or 0.45)
    keep = float(vc['keep_cap']) if vc.get('keep_cap') is not None else 0.9
    if step.endswith('t'):
        cap, keep = min(cap, 0.25), min(keep, 0.30)
    return float(step.rstrip('t')), dict(cap=cap, keep_cap=keep)


def process_take(t, take, work, step, force=False):
    out = proc_path(work, take, step)
    rp = os.path.splitext(out)[0] + '.report.json'
    if os.path.exists(rp) and os.path.exists(out) and not force:
        return json.load(open(rp))
    speed, kw = step_kw(t, step)
    return V.process(take, t['dev_tokens'], t['rom_tokens'], out=out, speed=speed, realign=True, **kw)


def voice_runs(x, pad=0.5):
    """vo_chain.voiced_runs on the clip padded with 0.5 s of digital silence each side, so the adaptive threshold is
    always vo_chain's 'peak - 45 dB' (a trimmed clip has almost no silence of its own, which would raise the noise
    floor estimate into the speech and clip quiet onsets)."""
    n = int(pad * SR)
    xp = np.concatenate([np.zeros(n, np.float32), np.asarray(x, np.float32), np.zeros(n, np.float32)])
    return [(round(a - pad, 4), round(b - pad, 4)) for a, b in V.voiced_runs(xp)]


def line_limit(lines, lid):
    """The latest the voice may end: min(end_target + 0.15, the hard limit, next line's onset - 0.15)."""
    l = lines[lid]
    lim = min(float(l['end_target']) + TOL, HARD_END.get(lid, 99.0))
    order = ORDER_B if lid == 'L1B' else ORDER_A
    i = order.index(lid)
    if i + 1 < len(order):
        nxt = order[i + 1]
        on = L11_ONSET_MIN if nxt == 'L11' else float(lines[nxt]['start_target'])
        lim = min(lim, on - MIN_GAP)
    return round(lim, 4)


def onset_for(lid, lines, voice):
    on = float(lines[lid]['start_target'])
    if lid == 'L11':
        on = max(L11_ONSET_MIN, min(on, HARD_END['L11'] - voice))
    return round(on, 4)


def cmd_process(raw=RAW, work=WORK, only=None):
    d, lines = load_script(work)
    fixes = load_fixes(work)
    state_p = os.path.join(work, 'lines.json')
    state = json.load(open(state_p, encoding='utf8')) if os.path.exists(state_p) else {}
    for lid in ALL_LINES:
        if only and lid not in only:
            continue
        lim = line_limit(lines, lid)
        for take in candidates(raw, lid):
            key = os.path.splitext(os.path.basename(take))[0]
            ident, n = take_ident(take)
            t = ident_text(ident, lines, fixes)
            st = state.get(key, {})
            if st.get('req') != t['req']:
                st = {}
            t0 = time.time()
            st.update(line=lid, ident=ident, kind=t['kind'], why=t['why'], req=t['req'], rom=' '.join(t['rom_tokens']),
                      check=t['check'], take=os.path.relpath(take, REPO), take_dur=round(len(V.decode(take)) / SR, 3))
            if 'raw_small' not in st:
                st['raw_small'] = asr_check(take, t, 'small')
            steps = st.setdefault('steps', {})
            for step in STEPS[lid]:
                if step in steps and os.path.exists(proc_path(work, take, step)):
                    continue
                if step.endswith('t') and any(s.get('fits') for s in steps.values()):
                    continue                       # the tight-cap step only when no plain step fits
                r = process_take(t, take, work, step)
                p = proc_path(work, take, step)
                runs = voice_runs(V.decode(p))
                voice = runs[-1][1] - runs[0][0]
                on = onset_for(lid, lines, voice)
                end = on + voice
                steps[step] = dict(speed=r['speed'], caps=step_kw(t, step)[1], final_dur=r['final_dur'],
                                   voice=round(voice, 3), onset=on, end=round(end, 3), limit=lim,
                                   fits=bool(end <= lim + 1e-6), pauses=r['pauses'], lufs=r['loudness']['lufs'],
                                   tp=r['loudness']['tp'], matched='%d/%d' % (r['matched'], r['tokens']),
                                   unmatched=r['unmatched'], tail_trim=r['tail_trim'],
                                   realign=(r.get('realign') or {}).get('independent'),
                                   asr={m: asr_check(p, t, m) for m in ('small', 'medium')})
            state[key] = st
            print(key, json.dumps({s: (v['voice'], v['end'], v['fits'], v['asr']['small']['cer'],
                                       v['asr']['medium']['cer']) for s, v in steps.items()}),
                  '%.0fs' % (time.time() - t0), flush=True)
            json.dump(state, open(state_p, 'w', encoding='utf8'), ensure_ascii=False, indent=1)
    return state


# ------------------------------------------------------------------------------------------------ selection
def judge(st, step):
    """ASR verdict of one processed version. A CER or a word counts as wrong only when BOTH independent whisper models
    (small, medium) agree: each model alone mis-hears short clips (small: 'सीद हजबाब' for a clean 'सीधा जवाब' that
    medium heard exactly). Returns dict(cer_small, cer_medium, cer_ok, bad_words, ok)."""
    a = st['steps'][step]['asr']
    cs, cm = a['small']['cer'], a['medium']['cer']
    bad = [w for w in st['check'] if a['small']['words'][w]['verdict'] == 'fail'
           and a['medium']['words'][w]['verdict'] == 'fail']
    cer_ok = not (cs > CER_MAX and cm > CER_MAX)
    inexact = sum(a[m]['words'][w]['verdict'] != 'exact' for m in ('small', 'medium') for w in st['check'])
    return dict(cer_small=cs, cer_medium=cm, cer_ok=cer_ok, bad_words=bad, inexact=inexact,
                ok=bool(cer_ok and not bad))


def select(state, lines, work=WORK):
    """Per line, over every candidate take x ladder step:
    1. ASR ok and fits its limit: the first by (text kind script < prosody < fallback, ladder step, check words not
       heard exactly (both models summed), |end - end_target|, CER small + medium);
    2. else, if some fit: the fitting one with the fewest words both models mis-hear, then CER ok, kind, step,
       inexact words, |end - end_target|, CER (flagged: a human listen decides);
    3. else (nothing fits): the ASR-ok one (else any) with the smallest overrun, then kind, step, CER (flagged).
    <work>/select.json {"L3": "btk_L3-N_t1@1.10t"} overrides."""
    man = {}
    sp = os.path.join(work, 'select.json')
    if os.path.exists(sp):
        man = json.load(open(sp))
    sel = {}
    for lid in ALL_LINES:
        tgt = float(lines[lid]['end_target'])
        rows = []
        for key, st in state.items():
            if st.get('line') != lid or not os.path.exists(os.path.join(REPO, st['take'])):
                continue
            for step, s in st['steps'].items():
                j = judge(st, step)
                rows.append(dict(key=key, step=step, kind=st['kind'], fits=s['fits'], over=round(s['end'] - s['limit'], 3),
                                 end=s['end'], onset=s['onset'], voice=s['voice'], **j))
        si = lambda r: STEPS[lid].index(r['step'])
        cs = lambda r: r['cer_small'] + r['cer_medium']
        if lid in man:
            k, s = man[lid].split('@')
            pick = [r for r in rows if r['key'] == k and r['step'] == s][0]
            why = 'select.json'
        else:
            good = [r for r in rows if r['ok'] and r['fits']]
            fit = [r for r in rows if r['fits']]
            okr = [r for r in rows if r['ok']]
            if good:
                pick = min(good, key=lambda r: (KIND_RANK[r['kind']], si(r), r['inexact'], abs(r['end'] - tgt), cs(r)))
                why = 'ASR ok + fits'
            elif fit:
                pick = min(fit, key=lambda r: (len(r['bad_words']), not r['cer_ok'], KIND_RANK[r['kind']], si(r),
                                               r['inexact'], abs(r['end'] - tgt), cs(r)))
                why = 'fits, but no fitting take passes ASR (both models mis-hear %s): human listen' % (
                    ', '.join(pick['bad_words']) or 'the line (CER)')
            else:
                pool = okr or rows
                pick = min(pool, key=lambda r: (r['over'], KIND_RANK[r['kind']], si(r), cs(r)))
                why = 'NO candidate fits: the %s with the smallest overrun' % ('ASR-ok one' if okr else 'take')
        sel[lid] = dict(pick=pick, why=why, candidates=sorted(rows, key=lambda r: (r['key'], si(r))))
    return sel


# ------------------------------------------------------------------------------------------------ assemble
def load_clip(work, take, step):
    p = proc_path(work, take, step)
    x = V.decode(p)
    words = json.load(open(os.path.splitext(p)[0] + '.words.json', encoding='utf8'))
    runs = voice_runs(x)
    # vo_chain normalises each take to -16 LUFS but its -2 dBTP limiter caps peaky short takes below that (L1B-R came
    # out at -18.9): level-match every line to -16 LUFS here; the master limiter takes the peaks
    lufs = V.ebur128(p)['lufs']
    g = 10 ** ((LUFS - lufs) / 20)
    return dict(path=p, x=(x * g).astype(np.float32), words=words, runs=runs, on=runs[0][0], off=runs[-1][1],
                dur=len(x) / SR, step=step, lufs_in=lufs, gain_db=round(LUFS - lufs, 2))


def lufs_tp(x):
    err = subprocess.run(['ffmpeg', '-hide_banner', '-nostats', '-f', 'f32le', '-ar', str(SR), '-ac', '1', '-i', '-',
                          '-af', 'loudnorm=I=-16:TP=-2:LRA=11:print_format=json', '-f', 'null', '-'],
                         input=np.asarray(x, np.float32).tobytes(), capture_output=True).stderr.decode()
    j = json.loads(err[err.rindex('{'): err.rindex('}') + 1])
    return float(j['input_i']), float(j['input_tp'])


def beat_pos(t):
    """Reel time -> 'bar.beat+Nf' (bar 2.8 s, beat 0.7 s = 21 f) and the distance to the nearest 8th (0.35 s)."""
    f = int(round(t * FPS))
    bar, r = divmod(f, 84)
    beat, fr = divmod(r, 21)
    e8 = round(t / (BEAT / 2)) * (BEAT / 2)
    return '%d.%d+%df' % (bar, beat, fr), round(t - e8, 3)


def place(order, clips, n=NSAMP):
    y = np.zeros(n, np.float32)
    placed = []
    for lid in order:
        c, onset = clips[lid]['clip'], clips[lid]['onset']
        i0 = int(round((onset - c['on']) * SR))     # file start: the first voiced onset lands on the slot
        off = i0 / SR
        if i0 < 0:
            raise ValueError('%s would start before 0 s' % lid)
        xs = c['x'][:max(0, min(len(c['x']), n - i0))]
        y[i0:i0 + len(xs)] += xs
        words = []
        for k, w in enumerate(c['words']):
            words.append(dict(word=w['word'], start=round(w['start'] + off, 3), end=round(w['end'] + off, 3),
                              keyword=bool(w.get('keyword')), line=lid, i=k, dev=w.get('dev'), heard=w.get('heard'),
                              ok=w.get('ok'), hide=lid in HIDE))
        placed.append(dict(line=lid, take=clips[lid]['key'], step=c['step'], file_on=round(off, 4),
                           file_off=round(off + c['dur'], 4), voice_on=round(off + c['on'], 4),
                           voice_off=round(off + c['off'], 4), cut=len(c['x']) > len(xs), lufs_in=c['lufs_in'],
                           line_gain_db=c['gain_db'],
                           proc=os.path.relpath(c['path'], REPO), words=words))
    return y, placed


def limit(x, ceiling_db):
    """ffmpeg alimiter (lookahead, latency compensated, no auto level) at ceiling_db sample peak."""
    p = subprocess.run(['ffmpeg', '-hide_banner', '-loglevel', 'error', '-f', 'f32le', '-ar', str(SR), '-ac', '1', '-i',
                        '-', '-af', 'alimiter=limit=%.5f:attack=3:release=50:level=false:latency=true'
                        % (10 ** (ceiling_db / 20)), '-f', 'f32le', '-ac', '1', '-'],
                       input=np.asarray(x, np.float32).tobytes(), capture_output=True, check=True)
    z = np.frombuffer(p.stdout, np.float32)[:len(x)]
    return np.pad(z, (0, len(x) - len(z))).astype(np.float32)


def master(yA, yB):
    """Static gain to -16.0 LUFS integrated on version A; a lookahead limiter only while the true peak is above
    -2.1 dBTP; version B gets exactly the same chain (its body stays sample-identical). -> (zA, zB, info)."""
    l0, tp0 = lufs_tp(yA)
    zA, zB = yA.copy(), yB.copy()
    steps = []
    for _ in range(5):
        li, tp = lufs_tp(zA)
        steps.append(dict(lufs=round(li, 2), tp=round(tp, 2)))
        if abs(li - LUFS) <= 0.05 and tp <= TP_MAX - 0.1:
            break
        if abs(li - LUFS) > 0.05:
            g = 10 ** ((LUFS - li) / 20)
            zA, zB = (zA * g).astype(np.float32), (zB * g).astype(np.float32)
            steps[-1]['gain_db'] = round(LUFS - li, 3)
            li, tp = lufs_tp(zA)
        if tp > TP_MAX - 0.1:
            zA, zB = limit(zA, TP_MAX - 0.6), limit(zB, TP_MAX - 0.6)
            steps[-1]['limiter_db'] = TP_MAX - 0.6
    return zA, zB, dict(pre_lufs=round(l0, 2), pre_tp=round(tp0, 2), steps=steps)


def write_wav_checked(path, z):
    V.write_wav(path, z)
    L = V.ebur128(path)
    li, tp = lufs_tp(V.decode(path))
    pr = json.loads(subprocess.run(['ffprobe', '-v', 'error', '-show_entries',
                                    'stream=sample_rate,channels,codec_name,bits_per_sample', '-show_entries',
                                    'format=duration', '-of', 'json', path], capture_output=True, text=True).stdout)
    return dict(L, lufs_precise=round(li, 2), tp_precise=round(tp, 2), probe=pr)


def cmd_assemble(raw=RAW, work=WORK, md=MD):
    d, lines = load_script(work)
    state = json.load(open(os.path.join(work, 'lines.json'), encoding='utf8'))
    sel = select(state, lines, work)
    clips = {}
    for lid in ALL_LINES:
        pk = sel[lid]['pick']
        st = state[pk['key']]
        c = load_clip(work, os.path.join(REPO, st['take']), pk['step'])
        clips[lid] = dict(clip=c, onset=st['steps'][pk['step']]['onset'], limit=line_limit(lines, lid), key=pk['key'])
    yA, pA = place(ORDER_A, clips)
    yB, pB = place(ORDER_B, clips)
    # one chain for both versions: the body (from 2.8 s) is sample-identical in A and B
    zA, zB, minfo = master(yA, yB)
    out = {}
    stem = os.path.join(work, 'vo_stem.wav')
    out['A'] = write_wav_checked(stem, zA)
    subprocess.run(['cp', '-f', stem, os.path.join(work, '%s_vo_A.wav' % REEL)], check=True)
    out['B'] = write_wav_checked(os.path.join(work, '%s_vo_B.wav' % REEL), zB)
    zA2, zB2 = V.decode(stem), V.decode(os.path.join(work, '%s_vo_B.wav' % REEL))
    body_same = float(np.max(np.abs(zA2[int(2.8 * SR):] - zB2[int(2.8 * SR):])))
    wA = [w for p in pA for w in p['words']]
    wB = [w for p in pB for w in p['words']]
    for name, w in (('words.json', wA), ('%s.words.json' % REEL, wA), ('words_B.json', wB)):
        json.dump(w, open(os.path.join(work, name), 'w', encoding='utf8'), ensure_ascii=False, indent=1)
    chk = checks(pA, pB, clips, lines, out, wA, body_same)
    chk['master'] = minfo
    # placement check on the written file: every line's first voiced onset in the stem (its own window) vs placement
    on_err = []
    for p in pA:
        a0, a1 = int((p['file_on'] - 0.02) * SR), int((p['file_off'] + 0.02) * SR)
        seg = zA2[max(0, a0):a1]
        r = voice_runs(seg)
        if r:
            on_err.append((p['line'], round(max(0, a0) / SR + r[0][0] - p['voice_on'], 4)))
    chk['onset_error_in_stem'] = on_err
    if any(abs(e) > 0.005 for _, e in on_err):
        chk['fails'].append('onsets in the written stem moved: %s' % [x for x in on_err if abs(x[1]) > 0.005])
    # per-line loudness inside the stem (each line was normalised alone by vo_chain)
    ll = []
    for p in pA + [x for x in pB if x['line'] == 'L1B']:
        z = zA2 if p['line'] != 'L1B' else zB2
        seg = z[int(p['voice_on'] * SR):int(p['voice_off'] * SR)]
        ll.append((p['line'], round(lufs_tp(np.pad(seg, (0, max(0, int(0.5 * SR) - len(seg)))))[0], 2)))
    med = float(np.median([v for _, v in ll]))
    chk['line_lufs'] = ll
    chk['line_lufs_spread'] = [(k, round(v - med, 2)) for k, v in ll if abs(v - med) > 1.5]
    json.dump(dict(placed_A=[{k: v for k, v in p.items() if k != 'words'} for p in pA],
                   placed_B=[{k: v for k, v in p.items() if k != 'words'} for p in pB], checks=chk),
              open(os.path.join(work, 'check.json'), 'w', encoding='utf8'), ensure_ascii=False, indent=1)
    json.dump(sel, open(os.path.join(work, 'selection.json'), 'w', encoding='utf8'), ensure_ascii=False, indent=1)
    plot_timeline(zA, pA, lines, os.path.join(work, 'vo_timeline.png'))
    allp = pA[:1] + [x for x in pB if x['line'] == 'L1B'] + pA[1:]
    plot_lines(allp, os.path.join(work, 'vo_lines.png'))
    write_md(md, pA, pB, clips, lines, state, sel, chk)
    print(json.dumps({k: v for k, v in chk.items()}, ensure_ascii=False, indent=1))
    return chk


def checks(pA, pB, clips, lines, out, wA, body_same):
    c = dict(fails=[], warns=[])
    for ver, pl in (('A', pA), ('B', pB)):
        for a, b in zip(pl, pl[1:]):
            gap = b['voice_on'] - a['voice_off']
            if gap < MIN_GAP - 1e-6:
                c['fails'].append('%s: gap %s -> %s %.3f s < %.2f' % (ver, a['line'], b['line'], gap, MIN_GAP))
            if b['file_on'] < a['file_off'] - 1e-6:
                c['warns'].append('%s: the 40 ms file pads of %s / %s overlap by %.3f s (silence only)'
                                  % (ver, a['line'], b['line'], a['file_off'] - b['file_on']))
        seam = (DUR - pl[-1]['voice_off']) + pl[0]['voice_on']
        c['seam_%s' % ver] = round(seam, 3)
        if seam < MIN_GAP - 1e-6:
            c['fails'].append('%s: loop seam gap %.3f s < %.2f' % (ver, seam, MIN_GAP))
        if pl[-1]['file_off'] > DUR + 1e-6 or pl[-1]['cut']:
            c['fails'].append('%s: the last line crosses %.1f s' % (ver, DUR))
    for p in pA + [x for x in pB if x['line'] == 'L1B']:
        l = lines[p['line']]
        lim = clips[p['line']]['limit']
        want = clips[p['line']]['onset']
        if abs(p['voice_on'] - want) > 0.5 / SR * 4:
            c['fails'].append('%s onset %.4f vs placement %.4f' % (p['line'], p['voice_on'], want))
        if abs(p['voice_on'] - l['start_target']) > 1.0 / FPS + 1e-6:
            c['warns'].append('%s onset %.3f moved from the slot start %.2f (ladder)' % (p['line'], p['voice_on'],
                                                                                         l['start_target']))
        if p['voice_off'] > lim + 1e-6:
            c.setdefault('over_limit', []).append('%s ends %.3f > limit %.3f' % (p['line'], p['voice_off'], lim))
    for v in ('A', 'B'):
        L = out[v]
        if abs(L['lufs_precise'] - LUFS) > 0.3:
            c['fails'].append('%s loudness %.2f LUFS' % (v, L['lufs_precise']))
        if L['tp_precise'] > TP_MAX + 1e-6:
            c['fails'].append('%s true peak %.2f dBTP' % (v, L['tp_precise']))
        st = L['probe']['streams'][0]
        if int(st['sample_rate']) != SR or int(st['channels']) != 1 or int(st.get('bits_per_sample', 0)) != 24:
            c['fails'].append('%s format %s' % (v, st))
        if abs(float(L['probe']['format']['duration']) - DUR) > 0.002:
            c['fails'].append('%s duration %s' % (v, L['probe']['format']['duration']))
    if body_same > 1e-4:
        c['fails'].append('A and B bodies differ after 2.8 s (max %.2e)' % body_same)
    if any(b['start'] < a['start'] for a, b in zip(wA, wA[1:])):
        c['fails'].append('word starts not monotone')
    c['words'] = len(wA)
    c['words_ok'] = sum(1 for w in wA if w['ok'])
    c['A'] = {k: out['A'][k] for k in ('lufs', 'lufs_precise', 'lra', 'tp', 'tp_precise')}
    c['B'] = {k: out['B'][k] for k in ('lufs', 'lufs_precise', 'lra', 'tp', 'tp_precise')}
    c['body_identical_after_2_8'] = body_same <= 1e-4
    c['body_max_diff'] = body_same
    return c


def plot_timeline(z, placed, lines, path):
    import cv2
    W, H = 2400, 900
    img = np.full((H, W, 3), 18, np.uint8)
    px = lambda t: int(40 + (W - 80) * t / DUR)
    for k in range(0, int(round(DUR / BEAT)) + 1):
        t = k * BEAT
        cv2.line(img, (px(t), 60), (px(t), H - 60), (60, 60, 60) if k % 4 else (110, 110, 110), 1)
        if k % 4 == 0:
            cv2.putText(img, '%d' % (k // 4), (px(t) + 3, 55), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (160, 160, 160), 1)
    hop = SR // 100
    env = np.sqrt(np.mean(z[:len(z) // hop * hop].reshape(-1, hop) ** 2, axis=1))
    env = env / (env.max() + 1e-9)
    mid = 330
    for i, e in enumerate(env):
        x = px(i / 100.0)
        cv2.line(img, (x, int(mid - e * 200)), (x, int(mid + e * 200)), (60, 150, 255), 1)
    for p in placed:
        l = lines[p['line']]
        x0, x1 = px(l['start_target']), px(l['end_target'])
        cv2.rectangle(img, (x0, 580), (x1, 640), (70, 200, 70), 2)
        cv2.rectangle(img, (px(p['voice_on']), 660), (px(p['voice_off']), 720), (40, 110, 255), -1)
        cv2.putText(img, p['line'], (x0, 575), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (230, 230, 230), 2)
        for w in p['words']:
            cv2.line(img, (px(w['start']), 740), (px(w['start']), 770), (0, 200, 255) if w['keyword'] else
                     (200, 200, 200), 2)
    cv2.putText(img, 'green = slot (start_target-end_target), orange = measured voice, ticks = word starts (yellow = '
                     'caption keyword); grid = beats, bars numbered', (40, H - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.7,
                (200, 200, 200), 1)
    cv2.imwrite(path, img)


def plot_lines(placed, path):
    """One row per placed line: spectrogram (0-8 kHz) + RMS envelope (dB, -60..0) of the clip in reel time, word starts
    (cyan, keyword yellow) with the ROM words, voice on / off (green / red): a visual check of onsets, pause caps and
    tails (L11: nothing after 'baari')."""
    import cv2
    rows = []
    for p in placed:
        x = V.decode(os.path.join(REPO, p['proc']))
        t0 = p['file_on']
        dur = len(x) / SR
        W, H = 1800, 260
        img = np.full((H, W, 3), 14, np.uint8)
        n, hop = 1024, 240
        if len(x) > n:
            fr = np.lib.stride_tricks.sliding_window_view(x, n)[::hop] * np.hanning(n)
            S = 20 * np.log10(np.abs(np.fft.rfft(fr, axis=1))[:, :171] + 1e-6)     # 0-8 kHz
            S = np.clip((S - S.max() + 70) / 70, 0, 1)
            spec = (S.T[::-1] * 255).astype(np.uint8)
            spec = cv2.resize(spec, (W - 100, 150), interpolation=cv2.INTER_AREA)
            img[20:170, 80:W - 20] = cv2.applyColorMap(spec, cv2.COLORMAP_INFERNO)
        px = lambda t: int(80 + (W - 100) * (t - t0) / dur)
        h2 = SR // 100
        env = 20 * np.log10(np.sqrt(np.mean(x[:len(x) // h2 * h2].reshape(-1, h2) ** 2, axis=1)) + 1e-6)
        for i in range(1, len(env)):
            y0 = int(240 - np.clip(env[i - 1] + 60, 0, 60))
            y1 = int(240 - np.clip(env[i] + 60, 0, 60))
            cv2.line(img, (px(t0 + (i - 1) / 100), y0), (px(t0 + i / 100), y1), (220, 220, 220), 1)
        cv2.line(img, (px(p['voice_on']), 15), (px(p['voice_on']), 245), (60, 220, 60), 2)
        cv2.line(img, (px(p['voice_off']), 15), (px(p['voice_off']), 245), (60, 60, 240), 2)
        for k, w in enumerate(p['words']):
            col = (0, 220, 255) if w['keyword'] else (255, 220, 0)
            cv2.line(img, (px(w['start']), 20), (px(w['start']), 175), col, 1)
            cv2.putText(img, w['word'], (px(w['start']) + 2, 188 + 14 * (k % 2)), cv2.FONT_HERSHEY_SIMPLEX, 0.45, col, 1)
        cv2.putText(img, '%s %s %s  on %.3f  off %.3f' % (p['line'], p['take'], p['step'], p['voice_on'],
                                                          p['voice_off']),
                    (4, 14), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (230, 230, 230), 1)
        rows.append(img)
    cv2.imwrite(path, np.concatenate(rows, axis=0))


PRON_VERDICT = {
    'P0': 'FAIL: both models hear a p-onset (प्लैंट / प्लाइंट) -> spelling क्लायंट',
    'P1': 'use: medium hears क्लाइंट exactly (small ख्लान्त, its usual k-aspiration habit)',
    'P2': 'keep मम्मी (medium exact for both spellings)', 'P3': 'ममी not needed',
    'P4': 'keep ट्रांसलेशन (medium exact)', 'P6': 'keep फ़ैमिली (heard फामली / फामिली for both spellings); भेजो exact '
    '(medium)', 'P7': 'फ़ेमिली no better', 'P8': 'forward heard r-less (पववड / फोवड): see the human-listen flags',
    'P9': 'keep उल्टा, सीधा (medium exact)', 'P10': 'keep नज़र, ख़ुद, हमसे; बेहतर heard बहतर (colloquial spelling)',
    'P11': 'keep नानी, बारी (both exact; not भारी)'}


def pron_rows():
    rows = []
    try:
        sm = {r['id']: r for r in json.load(open(os.path.join(WORK, 'pron_check_small.json'), encoding='utf8'))}
        md = {r['id']: r for r in json.load(open(os.path.join(WORK, 'pron_check_medium.json'), encoding='utf8'))}
    except OSError:
        return ['| - | (no pron check files) | | | |']
    for k in sm:
        rows.append('| %s | %s | %s | %s | %s |' % (k, sm[k]['text'], sm[k]['heard'], md.get(k, {}).get('heard', '-'),
                                                PRON_VERDICT.get(k, '')))
    rows.append('| P5 | पहले इसका ट्रैन्सलेशन करो। | - | - | not generated (429 rate limit, no job, not charged); '
                'not needed: P4 passed |')
    return rows


def listen_rows(sel, state):
    out = []
    for lid in ALL_LINES:
        pk = sel[lid]['pick']
        if pk['bad_words']:
            st = state[pk['key']]
            a = st['steps'][pk['step']]['asr']
            out.append('- %s: both models hear %s (small "%s", medium "%s"); every take and spelling tried gave the '
                       'same (L7: 4 takes, 3 spellings) -> the voice says it non-rhotic ("fo-ward"): listen; if it '
                       'reads wrong, the only further lever is Latin "forward" in the TTS text (untested).' % (
                           lid, ', '.join(pk['bad_words']),
                           ' / '.join(a['small']['words'][w]['heard'] or '-' for w in pk['bad_words']),
                           ' / '.join(a['medium']['words'][w]['heard'] or '-' for w in pk['bad_words'])))
    out += ['- L1 क्लायंट ("client"): medium hears क्लाइंट, small ख्लांट (gate note 9 asks one human listen before '
            'publishing).',
            '- L1B / L8 मम्मी: stress must fall on the first syllable (MUM-mee); ASR cannot tell. L8 heard ममी (same '
            'word).',
            '- L10 भेजो ("bhejo", the CTA): small exact, medium भहझो (aspiration present, odd vowel): listen.',
            '- L9 समझाती: both models write संजाती (m -> n before jh, the common spoken assimilation); listen.']
    return out


def write_md(md, pA, pB, clips, lines, state, sel, chk):
    cr = json.load(open(os.path.join(WORK, 'credits.json'), encoding='utf8')) \
        if os.path.exists(os.path.join(WORK, 'credits.json')) else {}
    allp = pA[:1] + [x for x in pB if x['line'] == 'L1B'] + pA[1:]
    rows, misses = [], []
    for p in allp:
        lid = p['line']
        l, pk = lines[lid], sel[lid]['pick']
        st = state[pk['key']]
        dur = p['voice_off'] - p['voice_on']
        nwords = len(p['words'])
        kw = [w for w in p['words'] if w['keyword']]
        kws = ', '.join('*%s* @ %.2f (%s, %+.2f to 8th)' % ((w['word'], w['start']) + beat_pos(w['start']))
                        for w in kw) or '-'
        ver = pB if lid == 'L1B' else pA
        i = [x['line'] for x in ver].index(lid)
        gap = (ver[i + 1]['voice_on'] - p['voice_off']) if i + 1 < len(ver) else (DUR - p['voice_off'] +
                                                                                  ver[0]['voice_on'])
        d_on = p['voice_on'] - l['start_target']
        d_end = p['voice_off'] - l['end_target']
        flag = []
        if abs(d_end) > 0.3 + 1e-9:
            flag.append('MISS end %+.2f s (%s)' % (d_end, 'late' if d_end > 0 else 'early'))
            misses.append((lid, d_end))
        elif abs(d_end) > 0.3 - 0.005:
            flag.append('end %+.2f s: on the 0.3 s line' % d_end)
            misses.append((lid, d_end))
        if p['voice_off'] > clips[lid]['limit'] + 1e-6:
            flag.append('OVER limit %.2f' % clips[lid]['limit'])
        if not pk['ok']:
            flag.append('ASR')
        if pk['kind'] != 'script':
            flag.append(pk['kind'])
        rows.append('| %s | %s | %s | %.2f-%.2f | %.3f (%+.3f) | %.3f | %+.3f | %.2f | %s | %d | %.2f | %s | %.3f / %.3f |'
                    ' %.2f%s | %s |'
                    % (lid, st['rom'].replace('*', ''), '`%s` %s' % (pk['key'], pk['step']), l['start_target'],
                       l['end_target'], p['voice_on'], d_on, p['voice_off'], d_end, dur, beat_pos(p['voice_on'])[0],
                       nwords, nwords / dur, kws, pk['cer_small'], pk['cer_medium'], gap,
                       ' (loop seam)' if i + 1 == len(ver) else '', '; '.join(flag) or 'ok'))
    cand = []
    for lid in ALL_LINES:
        for r in sel[lid]['candidates']:
            st = state[r['key']]
            a = st['steps'][r['step']]['asr']
            cand.append('| %s | `%s` | %s | %s | %.3f | %.3f | %s | %.3f / %.3f | %s | %s | %s | %s |' % (
                lid, r['key'], r['kind'], r['step'], r['voice'], r['end'], 'yes' if r['fits'] else 'no (%+.2f)' % r['over'],
                r['cer_small'], r['cer_medium'], ', '.join(r['bad_words']) or '-', a['small']['heard'],
                a['medium']['heard'],
                '**picked** (%s)' % sel[lid]['why'] if (r['key'], r['step']) == (sel[lid]['pick']['key'],
                                                                                  sel[lid]['pick']['step']) else ''))
    total_A = sum(p['voice_off'] - p['voice_on'] for p in pA)
    L = chk
    used_var = sorted({sel[k]['pick']['key'] for k in ALL_LINES if sel[k]['pick']['kind'] != 'script'})
    var_lines = []
    for key in used_var:
        st = state[key]
        var_lines.append('- %s (`%s`, %s): DEV `%s` · ROM "%s" · why: %s' % (st['line'], key, st['kind'], st['req'],
                                                                         st['rom'], st['why']))
    txt = ['# VO_TIMING · Reel 4 · C02 · "Beta, tum karte kya ho?"', '',
           'Measured %s on the final processed Vlad takes (Higgsfield `elevenlabs_v4`, preset Vlad, provider defaults) '
           'after `vo_chain` (trim to 40 ms, pause caps, rubberband, HPF / de-ess / comp, loudnorm). Written by '
           '`pipeline/jawad_reels/beta_tum_karte_kya_ho_vo.py assemble`; replaces the ESTIMATED table of `SCRIPT.md` '
           'section 3.' % time.strftime('%Y-%m-%d %H:%M UTC', time.gmtime()), '',
           'Grid 85.714 BPM (beat 0.7 s = 21 f, bar 2.8 s = 84 f), DUR 36.4 s. Placement: each line\'s first voiced onset '
           '(vo_chain voiced runs, peak - 45 dB) on its `start_target`, sample-exact (L11: the SCRIPT 7 onset ladder, '
           '34.90 down to 34.70). Limit = min(end_target + 0.15, hard limit (L1 2.69, L1B 2.45, L11 36.35), next onset '
           '- 0.15). CER = faster-whisper small / medium (language hi, no prompt) on the placed processed take vs the '
           'DEV text actually sent (Latin loans mapped back; nukta, chandrabindu, half nasal = anusvara, cluster virama '
           'and the spoken forms वह/वो, पर/पे, लिये/लिए folded); a line fails ASR only when BOTH models give CER > 0.15 '
           'or both mis-hear a keyword / SCRIPT 6 risk word.', '',
           '## Per line (placed)', '',
           '| line | words (ROM) | take · ladder step | slot (s) | voice on (vs slot) | voice off | end vs target (s) | '
           'speech (s) | onset bar.beat | words | w/s | caption keyword @ t | CER small / medium | gap to next (s) | '
           'flags |',
           '|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|'] + rows + [
        '',
        '**End vs target beyond 0.3 s:** %s (early = the line ends before its slot end: no conflict).' % (
            ', '.join('%s %+.2f s' % m for m in misses) or 'none'),
        '',
        '## Pronunciation check (step 1: 11 carriers, `vo/pron_check_*.json`)', '',
        '| carrier | text | small heard | medium heard | verdict |', '|---|---|---|---|---|'] + pron_rows() + [
        '',
        '## Human-listen flags (ASR cannot judge stress / accent)', ''] + listen_rows(sel, state) + [
        '',
        '## Text changes against script.json (measured necessity)', ''] + (var_lines or ['- none']) + [
        '- Spelling: क्लाइंट -> क्लायंट (pronunciation carriers P0 / P1: whisper small and medium both heard P0 as '
        'प्लैंट / प्लाइंट, i.e. a p-onset; P1 was heard क्लाइंट by medium). All other SCRIPT 6 spellings kept '
        '(मम्मी, ट्रांसलेशन, फ़ैमिली, कार्टून, उल्टा, सीधा, पूछता, ख़ुद, नज़र, बेहतर, नानी, बारी: see '
        '`vo/pron_check_small.json`, `vo/pron_check_medium.json`).',
        '',
        '## Stems and words', '',
        '- Workspace `workspace/jawad_reels/%s/vo/`: `vo_stem.wav` = `%s_vo_A.wav` (L1 + L2-L11), `%s_vo_B.wav` (L1B + '
        'L2-L11, same static gain; body identical after 2.8 s: %s, max diff %.1e). 48 kHz 24-bit mono, %.3f s.' % (
            REEL, REEL, REEL, L['body_identical_after_2_8'], L['body_max_diff'], DUR),
        '- A: %.2f LUFS integrated (ebur128 %.1f), TP %.2f dBTP, LRA %.1f LU. B: %.2f LUFS, TP %.2f dBTP. Master '
        'chain on the placed takes (each -16 LUFS from vo_chain): %s. Per-line loudness in the stem (LUFS): %s; lines '
        'more than 1.5 LU from the median: %s. Onset error of every line in the written stem: max %.4f s.' % (
            L['A']['lufs_precise'], L['A']['lufs'], L['A']['tp_precise'], L['A']['lra'], L['B']['lufs_precise'],
            L['B']['tp_precise'], json.dumps(L['master']['steps']), ', '.join('%s %.1f' % x for x in L['line_lufs']),
            L['line_lufs_spread'] or 'none', max(abs(e) for _, e in L['onset_error_in_stem'])),
        '- Speech A: %.2f s of voice, first onset %.3f s, last offset %.3f s; %d words. Loop seam (L11 end -> 36.4 -> '
        'L1 onset): A %.3f s, B %.3f s.' % (total_A, pA[0]['voice_on'], pA[-1]['voice_off'], L['words'], L['seam_A'],
                                            L['seam_B']),
        '- `words.json` = `%s.words.json` (version A, reel seconds; `snake_captions.load_words` format plus line / i / '
        'dev / heard / ok / hide), `words_B.json` (version B). %d words, %d aligned ok by vo_chain.' % (
            REEL, L['words'], L['words_ok']),
        '- Checks: %s. Over the line limit (no take fits; reported, not fixed): %s. Notes: %s.' % (
            '; '.join(L['fails']) or 'all pass', '; '.join(L.get('over_limit', [])) or 'none',
            '; '.join(L['warns']) or 'none'),
        '- Credits (this reel, sum of its own get_cost preflights for submitted requests): %s of 25.' % (
            cr.get('spent_credits', 'see vo/credits.json')),
        '- Visual checks: `vo/vo_timeline.png` (slots vs measured voice on the beat grid), `vo/vo_lines.png` (per line '
        'spectrogram, envelope, word starts).',
        '',
        '## All candidates (take x ladder step)', '',
        '| line | take | kind | step | voice (s) | end (s) | fits | CER small / medium | misheard by both | heard (small) | '
        'heard (medium) | pick |',
        '|---|---|---|---|---|---|---|---|---|---|---|---|'] + cand + ['']
    os.makedirs(os.path.dirname(md), exist_ok=True)
    open(md, 'w', encoding='utf8').write('\n'.join(txt))
    print('->', md)


def main(argv=None):
    import argparse
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('cmd', choices=['requests', 'pron', 'process', 'assemble'])
    ap.add_argument('--only', default='')
    ap.add_argument('--model', default='small', help='whisper model for pron (small / medium)')
    a = ap.parse_args(argv)
    os.makedirs(os.path.join(WORK, 'proc'), exist_ok=True)
    if a.cmd == 'requests':
        cmd_requests()
    elif a.cmd == 'pron':
        cmd_pron(model=a.model)
    elif a.cmd == 'process':
        cmd_process(only=[x for x in a.only.split(',') if x] or None)
    else:
        cmd_assemble()


if __name__ == '__main__':
    main()
