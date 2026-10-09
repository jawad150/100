"""pehle_wala_vo.py - C26 "Pehle Wala Hi Theek Tha": Vlad line takes -> processed takes -> reel-timed VO stems,
word timings and the measured timing table (hinglish-scriptwriter, 2026-10-09).

Source of truth for the words, beats and hard ends: brand_reels/design/reels/pehle_wala/script.json (r2).
One Higgsfield take per beat line (Vlad, elevenlabs_v4, Devanagari prompt = script.json `dev`); L12 is generated
with its continuation ", बस एक छोटा सा चेंज।" so "bola" keeps a rising contour, and is cut after "बोला".

    tools/heavy.sh python3 -I pehle_wala_vo.py process [L1,L3,...] [--tag t1]   # vo_chain.process, speed 1.08
    tools/heavy.sh python3 -I pehle_wala_vo.py asr [L1_t1,...]                  # CER (whisper small/medium, hi)
    tools/heavy.sh python3 -I pehle_wala_vo.py assemble                        # stems A/B + words + timing
    tools/heavy.sh python3 -I pehle_wala_vo.py verify                          # whisper on the whole stem
    python3 -I pehle_wala_vo.py plot                                           # timeline PNG for a visual check

Paths: raw takes <VO>/raw/pw_<line>_<tag>.mp3, processed <VO>/proc/<line>_<tag>.{wav,words.json,report.json},
ASR <VO>/asr/<line>_<tag>.json, choice <VO>/takes_selected.json ({line: tag}); outputs <VO>/vo_stem.wav (hook A,
public), <VO>/vo_stem_B.wav (hook B, Trial), <VO>/words.json / words_B.json (reel seconds), the BRIEF names
pehle_wala_vo_{A,B}.wav / .words.json (same content), <VO>/timing.json, and VO_TIMING.md in the design folder.
CER (see cers()): whisper small and medium (language hi, beam 5, NO initial prompt, no VAD) on the processed take;
Levenshtein / reference length after NFC, lower case, nukta dropped, chandrabindu -> anusvara, punctuation and
spaces removed, vowel signs KEPT (norm_full), Latin words / numerals mapped to the script's Devanagari (map_latin);
the line's CER is the lower of the two models. The project metric of tts/scripts/evaluate.py (norm()) is also
stored ('skel'): it drops every Devanagari vowel sign, virama and anusvara (they are not \\w in Python's re).
"""
import json
import os
import re
import subprocess
import sys
import unicodedata

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import vo_chain as V  # noqa: E402  (read-only shared module)

REPO = os.path.abspath(os.path.join(HERE, '..', '..'))
DESIGN = os.path.join(REPO, 'brand_reels', 'design', 'reels', 'pehle_wala')
SCRIPT = os.path.join(DESIGN, 'script.json')
VO = os.path.join(REPO, 'workspace', 'jawad_reels', 'pehle_wala', 'vo')
RAW, PROC, ASRD = (os.path.join(VO, d) for d in ('raw', 'proc', 'asr'))
SEL = os.path.join(VO, 'takes_selected.json')
SR = V.SR
SPEED = 1.08
PAD = 0.04                    # cut pads at phrase edges (vo_chain / SCRIPT section 6)
CONT = {'L12': (['बस', 'एक', 'छोटा', 'सा', 'चेंज।'], ['Bas', 'ek', 'chhota', 'sa', 'change.'])}

S = json.load(open(SCRIPT))
DUR = S['frames'] / S['fps']                # 1024 / 30 = 34.1333... s exactly (dur_s is rounded)
NS = int(round(DUR * SR))
LINES = {l['id']: l for l in S['lines']}
ORDER = [l['id'] for l in S['lines']]

# phrase plan (SCRIPT section 4 placement rules): token spans per phrase and how each phrase is placed
#   ('at', t): voice onset of the phrase's first word on t
#   ('after', gap): onset = previous phrase's voice end + gap (placed internal pause)
#   ('frag', t): onset = max(t, previous phrase end + 0.03)  (L9 fragments)
#   ('end_at', t): last word END on t (L12)
PLAN = {
    'L1': [((0, 4), ('at', 0.100))],
    'L1B': [((0, 5), ('at', 0.100))],
    'L2': [((0, 1), ('at', 3.267))],
    'L3': [((0, 0), ('at', 4.400)), ((1, 4), ('after', 0.25))],
    'L4': [((0, 0), ('at', 6.733))],            # onset = max(6.733, L3 end + 0.15), enforced in assemble()
    'L5': [((0, 0), ('at', 8.600))],
    'L6': [((0, 0), ('at', 10.800))],
    'L7': [((0, 4), ('at', 12.867))],
    'L8': [((0, 1), ('at', 15.000))],
    'L9': [((0, 1), ('frag', 19.233)), ((2, 3), ('frag', 19.767)), ((4, 5), ('frag', 20.300))],
    'L10': [((0, 2), ('at', 23.500))],
    'L11': [((0, 3), ('at', 28.133)), ((4, 8), ('after', 0.15))],
    'L12': [((0, 4), ('end_at', 34.050))],
}
TRACKS = S['tracks']


# ============================================================================================ helpers
def dev_rom(lid):
    """(dev tokens, rom tokens) of the TAKE of a line (L12 includes its continuation)."""
    l = LINES[lid]
    dev, rom = list(l['dev_tokens']), list(l['tokens'])
    if lid in CONT:
        dev[-1] += ','
        rom[-1] += ','
        dev += CONT[lid][0]
        rom += CONT[lid][1]
    assert len(dev) == len(rom), lid
    return dev, rom


def norm(s):
    """evaluate.py norm (project CER metric)."""
    s = unicodedata.normalize('NFC', s.lower())
    s = s.replace('़', '').replace('ँ', 'ं')
    s = re.sub(r'[‌‍]', '', s)
    s = re.sub(r'[^\w\s]', ' ', s)
    s = unicodedata.normalize('NFC', s)
    # NFC re-composes nukta letters (e.g. U+095E); decompose them and drop the nukta again
    s = ''.join(V.NUKTA.get(ch, ch) if ch in 'क़ख़ग़ज़ड़ढ़फ़य़' else ch for ch in s)
    return re.sub(r'\s+', '', s)


def norm_full(s):
    """CER normalisation that KEEPS the vowel signs: evaluate.py's norm() (above) removes every character that is
    not \\w, and in Python's re the Devanagari vowel signs, virama and anusvara are not \\w, so the project metric
    compares consonant skeletons only (measured: re.sub(r'[^\\w\\s]', ' ', 'फिर आख़री मैसेज') -> 'फ र आख र  म स ज').
    Same equivalences (NFC, lower case, nukta dropped, chandrabindu -> anusvara, ZWJ/ZWNJ dropped), but only
    punctuation, symbols and spaces are removed."""
    s = unicodedata.normalize('NFC', s.lower()).replace('\u093c', '').replace('\u0901', '\u0902')
    s = re.sub(r'[\u200c\u200d]', '', s)
    s = ''.join(V.NUKTA.get(ch, ch) if ch in '\u0958\u0959\u095a\u095b\u095c\u095d\u095e\u095f' else ch for ch in s)
    return ''.join(ch for ch in s if unicodedata.category(ch)[0] in 'LMN')


def _latin_map():
    """Latin words / numerals that whisper may write for the script's loanwords -> the script's Devanagari."""
    m = {'26': 'छब्बीस', 'v1': 'वी-वन', 'v-1': 'वी-वन'}
    for t in S['token_table']:
        r = re.sub(r'[^a-z0-9]', '', t['roman'].lower())
        if r and r not in m:
            m[r] = t['dev']
    return m


LATIN = None


def map_latin(hyp):
    """Replace Latin-script words and numerals in a Devanagari transcript by the script's spelling of that word
    (whisper-medium writes English loanwords and numbers in Latin: "Pop!", "editor", "V1", "26")."""
    global LATIN
    LATIN = LATIN or _latin_map()
    out = []
    for w in hyp.split():
        k = re.sub(r'[^a-z0-9]', '', w.lower())
        out.append(LATIN.get(k, w) if re.search(r'[a-z0-9]', k) else w)
    return ' '.join(out)


def cers(hyp, ref):
    """dict(skel=project metric, full=with vowel signs, fullmap=with vowel signs after map_latin)."""
    r_s, r_f = norm(ref), norm_full(ref)
    return dict(skel=round(lev(norm(hyp), r_s) / max(1, len(r_s)), 3),
                full=round(lev(norm_full(hyp), r_f) / max(1, len(r_f)), 3),
                fullmap=round(lev(norm_full(map_latin(hyp)), r_f) / max(1, len(r_f)), 3))


def lev(a, b):
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        cur = [i]
        for j, cb in enumerate(b, 1):
            cur.append(min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + (ca != cb)))
        prev = cur
    return prev[-1]


def cer(hyp, ref):
    r = norm(ref)
    return lev(norm(hyp), r) / max(1, len(r))


def runs_abs(x, thr=-45.0, win=0.02, hop=0.01, close=0.08, min_run=0.03):
    """Voiced runs with an absolute RMS threshold (dBFS). The processed takes sit at about -16 LUFS on ElevenLabs'
    digital-silence floor (about -90 dBFS), so -45 dBFS separates voice from silence without the percentile floor
    that fails on takes with little silence."""
    n, h = int(win * SR), int(hop * SR)
    fr = np.lib.stride_tricks.sliding_window_view(x, n)[::h]
    v = 10 * np.log10(np.mean(fr.astype(np.float64) ** 2, axis=1) + 1e-12) > thr
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
    return [(a, b) for a, b in merged if b - a >= min_run]


def selected():
    return json.load(open(SEL)) if os.path.exists(SEL) else {lid: 't1' for lid in ORDER}


# ============================================================================================ process
def process(ids, tag):
    os.makedirs(PROC, exist_ok=True)
    out = {}
    for lid in ids:
        raw = os.path.join(RAW, 'pw_%s_%s.mp3' % (lid, tag))
        dev, rom = dev_rom(lid)
        dst = os.path.join(PROC, '%s_%s.wav' % (lid, tag))
        # vo_chain.voiced_runs takes its noise floor from the 10th percentile of 20 ms frames: on a take with less
        # than ~10 % silence (L7_t1: floor at -39 dB re peak) the threshold lands inside speech and the trim cuts the
        # last word's decay. Local workaround (SHARED_REQUESTS #8): pad the take with 0.5 s of digital silence at
        # both ends before processing; the trim to 40 ms removes the pads again.
        padded = os.path.join(PROC, '_pad_%s_%s.wav' % (lid, tag))
        z = np.zeros(int(0.5 * SR), np.float32)
        V.write_wav(padded, np.concatenate([z, V.decode(raw), z]), fmt='pcm_f32le')
        try:
            rep = V.process(padded, dev, rom, out=dst, speed=SPEED)
        finally:
            os.remove(padded)
        rep['input'] = os.path.relpath(raw, REPO) + ' (+0.5 s digital silence each end)'
        json.dump(rep, open(os.path.splitext(dst)[0] + '.report.json', 'w'), ensure_ascii=False, indent=1)
        stem = os.path.splitext(dst)[0]
        if rep['unmatched']:                       # SHARED_REQUESTS #6 workaround: second pass without the prompt
            w1 = json.load(open(stem + '.words.json'))
            w2, _ = V.align(dst, dev, rom, prompt=' ')
            took = []
            for i, (a, b) in enumerate(zip(w1, w2)):
                if not a['ok'] and b['ok']:
                    w1[i] = dict(b, filled_from='no-prompt pass')
                    took.append(a['word'])
            json.dump(w1, open(stem + '.words.json', 'w'), ensure_ascii=False, indent=1)
            rep['second_pass'] = dict(took=took, still_unmatched=[(w['word'], w['heard']) for w in w1 if not w['ok']])
            json.dump(rep, open(stem + '.report.json', 'w'), ensure_ascii=False, indent=1)
        out[lid] = dict(final_dur=rep['final_dur'], raw_dur=rep['raw_dur'], lufs=rep['loudness']['lufs'],
                        tp=rep['loudness']['tp'], matched='%d/%d' % (rep['matched'], rep['tokens']),
                        unmatched=rep['unmatched'], second_pass=rep.get('second_pass'),
                        pauses=[(p['at'], p['was'], p['now']) for p in rep['pauses']], stretch=rep['chain']['stretch'])
        print(lid, json.dumps(out[lid], ensure_ascii=False))
    return out


# ============================================================================================ ASR / CER
EN_KEYS = {'L1': ['change'], 'L1B': ['26|twenty', 'revision', 'client'], 'L3': ['pop'], 'L4': ['clean'],
           'L5': ['energetic'], 'L6': ['fun'], 'L7': ['mumm|momm|mom', 'review'], 'L8': ['cinematic'],
           'L10': ['message'], 'L11': ['editor', 'final'], 'L12': ['client', 'change']}


def asr(names):
    from faster_whisper import WhisperModel
    os.makedirs(ASRD, exist_ok=True)
    models = {m: WhisperModel(os.path.join(V.WHISPER, 'faster-whisper-%s' % m), device='cpu', compute_type='int8',
                              cpu_threads=V.THREADS) for m in ('small', 'medium')}

    def tr(m, x, lang):
        segs, _ = models[m].transcribe(x, language=lang, beam_size=5, vad_filter=False,
                                       condition_on_previous_text=False)
        return ' '.join(s.text.strip() for s in segs).strip()

    res = {}
    for name in names:
        lid, tag = name.rsplit('_', 1)
        path = os.path.join(PROC, '%s_%s.wav' % (lid, tag))
        x = V.decode(path, 16000)                         # ffmpeg -> 16 kHz mono numpy (PyAV path bug)
        ref = ' '.join(dev_rom(lid)[0])
        r = dict(ref=ref)
        for m in ('small', 'medium'):
            r['hi_' + m] = tr(m, x, 'hi')
            r['en_' + m] = tr(m, x, 'en')
        keys = EN_KEYS.get(lid, [])
        en = (r['en_small'] + ' ' + r['en_medium']).lower()
        r['en_keys'] = {k: bool(re.search(k, en)) for k in keys}
        score(r)
        json.dump(r, open(os.path.join(ASRD, '%s_%s.json' % (lid, tag)), 'w'), ensure_ascii=False, indent=1)
        res[name] = r
        print(name, 'CER', r['cer_small'], r['cer_medium'], '| hi-s:', r['hi_small'], '| hi-m:', r['hi_medium'],
              '| en-s:', r['en_small'], '| en-m:', r['en_medium'], '|', r['en_keys'])
    return res


def score(r):
    """CERs of one ASR record (in place): per model the project skeleton metric, the full metric and the full
    metric after map_latin; `cer` = the line's CER = the lower full+map value of the two models."""
    for m in ('small', 'medium'):
        r['cer_' + m] = cers(r['hi_' + m], r['ref'])
    r['cer'] = min(r['cer_small']['fullmap'], r['cer_medium']['fullmap'])
    r['cer_model'] = 'small' if r['cer_small']['fullmap'] <= r['cer_medium']['fullmap'] else 'medium'
    return r


def rescore():
    """Recompute every stored ASR record's CERs (no whisper run)."""
    for f in sorted(os.listdir(ASRD)):
        if re.match(r'L\w+_t\d\.json$', f):
            p = os.path.join(ASRD, f)
            r = score(json.load(open(p)))
            json.dump(r, open(p, 'w'), ensure_ascii=False, indent=1)
            print('%-8s line CER %.3f (%s) | small skel %.3f full %.3f map %.3f | medium skel %.3f full %.3f map %.3f | en %s' % (
                f[:-5], r['cer'], r['cer_model'], r['cer_small']['skel'], r['cer_small']['full'],
                r['cer_small']['fullmap'], r['cer_medium']['skel'], r['cer_medium']['full'],
                r['cer_medium']['fullmap'], r['en_keys']))


# ============================================================================================ assemble
def phrase_cut(lid, tag):
    """Per phrase of the line: (audio segment, voice onset in the segment, voice end in the segment, words with
    times relative to the segment start)."""
    stem = os.path.join(PROC, '%s_%s' % (lid, tag))
    x = V.decode(stem + '.wav')
    words = json.load(open(stem + '.words.json'))
    runs = runs_abs(x)
    n_line = len(LINES[lid]['tokens'])
    out = []
    plan = PLAN[lid]
    for k, ((i0, i1), rule) in enumerate(plan):
        ws = words[i0:i1 + 1]
        on = ws[0]['start']
        # acoustic end: the end of the voiced run that holds (or precedes) the last word's end
        we = ws[-1]['end']
        offs = [b for a, b in runs if a < we + 0.02]
        ve = max(we, offs[-1]) if offs else we
        nxt = words[i1 + 1]['start'] if i1 + 1 < len(words) else len(x) / SR + PAD
        if i1 + 1 < len(words):                # never cut into the next word: stop at the next voiced onset
            nxt_on = [a for a, b in runs if a > ve - 0.005]
            nxt = min(nxt, nxt_on[0]) if nxt_on else nxt
            ve = min(ve, nxt - 0.02)
        prv = words[i0 - 1]['end'] if i0 > 0 else 0.0
        a = max(prv + 0.0, on - PAD, 0.0) if i0 > 0 else max(0.0, on - PAD)
        b = min(ve + PAD, nxt - 0.01, len(x) / SR)
        seg = x[int(round(a * SR)):int(round(b * SR))].copy()
        fi, fo = int(0.005 * SR), int(0.012 * SR)
        seg[:fi] *= np.linspace(0, 1, fi)
        seg[-fo:] *= np.linspace(1, 0, fo)
        wrel = [dict(w, start=round(w['start'] - a, 4), end=round(w['end'] - a, 4)) for w in ws]
        if ve > we and ve - we <= 0.40:          # the final word's audible end (whisper ends early on drawls)
            wrel[-1]['end'] = round(ve - a, 4)
            wrel[-1]['end_from'] = 'voiced offset'
        for w in wrel:
            w['line'] = lid
        if lid in CONT:                         # the continuation is not part of the line: drop the comma marks
            assert i1 < n_line, (lid, i1)
            wrel[-1]['word'] = wrel[-1]['word'].rstrip(',')
            wrel[-1]['dev'] = wrel[-1]['dev'].rstrip(',')
        p = dict(seg=seg, on=on - a, ve=ve - a, words=wrel, rule=rule, src=(round(a, 3), round(b, 3)), closed=[])
        if lid in CLOSE_GAPS:
            close_gaps(p, CLOSE_GAPS[lid])
        out.append(p)
    return out


# SCRIPT section 4 fallback (L1B step 2; L10 "trim the drawl" is not needed when this lands it): silent gaps
# BETWEEN words longer than 0.10 s shortened to `keep` s (silence only, never inside a word; 5 ms crossfade).
CLOSE_GAPS = {'L1B': 0.06, 'L10': 0.06}      # lines whose measured end crossed the hard end without it


def close_gaps(p, keep=0.06, min_gap=0.10):
    seg, ws = p['seg'], p['words']
    runs = runs_abs(seg)
    cuts = []
    for (a0, a1), (b0, b1) in zip(runs, runs[1:]):
        gap = b0 - a1
        between = any(a1 - 0.05 <= w['start'] <= b0 + 0.05 for w in ws[1:])
        if gap > min_gap and between:
            cuts.append((a1 + keep / 2, b0 - keep / 2))
    xf = int(0.005 * SR)
    for c0, c1 in reversed(cuts):
        i0, i1 = int(round(c0 * SR)), int(round(c1 * SR))
        head, tail = seg[:i0 + xf].copy(), seg[i1:].copy()
        r = np.linspace(1, 0, xf)
        head[-xf:] = head[-xf:] * r + tail[:xf] * (1 - r)
        seg = np.concatenate([head, tail[xf:]])
        d = (i1 - i0) / SR
        for w in ws:
            for k in ('start', 'end'):
                if w[k] >= c1 - 0.03:
                    w[k] = round(w[k] - d, 4)
        if p['ve'] >= c1:
            p['ve'] -= d
        p['closed'].append((round(c0, 3), round(c1, 3), round(d, 3)))
    p['seg'] = seg.astype(np.float32)
    return p


def build(track, sel):
    """Place every line of a track on the beat table -> (signal, words in reel s, per-line timing rows)."""
    y = np.zeros(NS + SR, np.float32)
    words, rows = [], []
    prev_end = None
    for lid in TRACKS[track]:
        tag = sel[lid]
        L = LINES[lid]
        phrases = phrase_cut(lid, tag)
        # level match: every line to the same integrated loudness (vo_chain's -2 dBTP limit leaves peaky short
        # takes up to 2 dB under -16 LUFS); the master limiter below catches the raised peaks
        lufs = measure(np.concatenate([p['seg'] for p in phrases]))['lufs']
        g = float(np.clip(LINE_LUFS - lufs, -3.0, 3.0))
        for p in phrases:
            p['seg'] = (p['seg'] * 10 ** (g / 20)).astype(np.float32)
        pl = []
        for k, p in enumerate(phrases):
            kind, val = p['rule']
            if kind == 'at':
                t_on = val
                if lid == 'L4':
                    t_on = max(val, prev_end + 0.15)
            elif kind == 'after':
                t_on = pl[-1]['t_ve'] + val
            elif kind == 'frag':
                t_on = val if not pl else max(val, pl[-1]['t_ve'] + 0.03)
            else:                                   # end_at: last word END on val
                t_on = val - (max(p['words'][-1]['end'], p['ve']) - p['on'])
            off = t_on - p['on']                    # reel time of the segment's first sample
            i0 = int(round(off * SR))
            seg = p['seg']
            if i0 < 0:
                seg, i0 = seg[-i0:], 0
            y[i0:i0 + len(seg)] += seg
            pl.append(dict(t_on=t_on, t_ve=off + p['ve'], t_a=off, t_b=off + len(p['seg']) / SR, closed=p['closed'],
                           words=[dict(w, start=round(w['start'] + off, 3), end=round(w['end'] + off, 3))
                                  for w in p['words']]))
        lw = [w for p in pl for w in p['words']]
        words += lw
        t0, t1w, t1v = lw[0]['start'], lw[-1]['end'], max(p['t_ve'] for p in pl)
        kw = [w for w in lw if w.get('keyword')]
        nw = len(L['tokens']) + (1 if lid == 'L11' else 0)        # v1 = two spoken words
        speech = sum(p['t_ve'] - p['t_on'] for p in pl)
        rows.append(dict(line=lid, tag=tag, line_lufs_in=lufs, line_gain_db=round(g, 2), beat=L['beat'], frame=L['frame'], target_start=L['start_target'],
                         target_end=L['end_target'], hard_end=L['hard_end'], t0=round(t0, 3), t1=round(t1w, 3),
                         t1_voice=round(t1v, 3), d_start=round(t0 - L['start_target'], 3),
                         d_end=round(max(t1w, t1v) - L['end_target'], 3), over_hard=round(max(t1w, t1v) - L['hard_end'], 3),
                         words=nw, speech_s=round(speech, 3), wps=round(nw / max(1e-6, t1w - t0), 2),
                         keyword=(kw[0]['word'].strip('*?,.') if kw else None), keyword_at=(kw[0]['start'] if kw else None),
                         phrases=[(round(p['t_on'], 3), round(p['t_ve'], 3)) for p in pl],
                         gaps_closed=[c for p in pl for c in p['closed']],
                         seg_edges=[(round(p['t_a'], 3), round(p['t_b'], 3)) for p in pl]))
        prev_end = max(t1w, t1v)
    return y[:NS], words, rows


LINE_LUFS = -16.0


def measure(x):
    """ebur128 (integrated LUFS, LRA, true peak) of a float signal (temp 24-bit wav)."""
    tmp = os.path.join(VO, '_tmp_meas_%d.wav' % os.getpid())
    V.write_wav(tmp, x)
    try:
        return V.ebur128(tmp)
    finally:
        os.remove(tmp)


def master(y, target=-16.0, tp_max=-2.0):
    """Gain + look-ahead limiter (ffmpeg alimiter, latency compensated, ceiling 1 dB under the TP limit),
    iterated so the integrated loudness lands on the target. Returns (y, loudness, gain_db, limiter_db)."""
    lim = 10 ** ((tp_max - 1.0) / 20)            # sample-peak ceiling 1 dB under the TP limit (inter-sample overs)
    g = target - measure(y)['lufs']
    for _ in range(4):
        z = (y * 10 ** (g / 20)).astype(np.float32)
        p = subprocess.run(['ffmpeg', '-hide_banner', '-loglevel', 'error', '-f', 'f32le', '-ar', str(SR), '-ac', '1',
                            '-i', '-', '-af', 'alimiter=limit=%.5f:attack=2:release=40:level=false:latency=true' % lim,
                            '-f', 'f32le', '-ac', '1', '-'], input=z.tobytes(), capture_output=True, check=True)
        out = np.frombuffer(p.stdout, np.float32).copy()[:len(y)]
        if len(out) < len(y):
            out = np.concatenate([out, np.zeros(len(y) - len(out), np.float32)])
        L = measure(out)
        if abs(L['lufs'] - target) <= 0.05:
            break
        g += target - L['lufs']
    red = 20 * np.log10(max(1e-9, float(np.max(np.abs(z)))) / max(1e-9, float(np.max(np.abs(out)))))
    if L['tp'] > tp_max - 0.1:                   # ebur128 prints one decimal: keep a 0.1 dB margin
        raise RuntimeError('true peak %.2f dBTP (max %.1f)' % (L['tp'], tp_max))
    return out, L, round(g, 2), round(red, 2)


def assemble():
    sel = selected()
    res = {}
    for track in ('A', 'B'):
        y, words, rows = build(track, sel)
        y, L, g, red = master(y)
        name = 'vo_stem.wav' if track == 'A' else 'vo_stem_B.wav'
        wname = 'words.json' if track == 'A' else 'words_B.json'
        V.write_wav(os.path.join(VO, name), y)
        V.write_wav(os.path.join(VO, 'pehle_wala_vo_%s.wav' % track), y)
        clean = [dict(word=w['word'], start=w['start'], end=w['end'], keyword=bool(w.get('keyword')), line=w['line'],
                      dev=w['dev'], heard=w.get('heard', ''), ok=w.get('ok', False)) for w in words]
        for p in (os.path.join(VO, wname), os.path.join(VO, 'pehle_wala_vo_%s.words.json' % track)):
            json.dump(clean, open(p, 'w'), ensure_ascii=False, indent=1)
        runs = V.voiced_runs(y)
        gaps = []
        for a_, b_ in zip(rows, rows[1:]):
            gaps.append((a_['line'], b_['line'], round(b_['t0'] - max(a_['t1'], a_['t1_voice']), 3)))
        seam = round(DUR - max(rows[-1]['t1'], rows[-1]['t1_voice']) + rows[0]['t0'], 3)
        res[track] = dict(file=os.path.join(VO, name), loudness=L, gain_db=g, limiter_peak_reduction_db=red,
                          samples=len(y), dur=len(y) / SR,
                          rows=rows, gaps=gaps, loop_seam_gap=seam, speech_s=round(sum(b - a for a, b in runs), 3),
                          first_voice=round(runs[0][0], 3), last_voice=round(runs[-1][1], 3))
        print(track, json.dumps({k: v for k, v in res[track].items() if k != 'rows'}, ensure_ascii=False))
        for r in rows:
            print('  ', json.dumps(r, ensure_ascii=False))
    res['selected'] = sel
    json.dump(res, open(os.path.join(VO, 'timing.json'), 'w'), ensure_ascii=False, indent=1)
    return res


# ============================================================================================ verify / plot
def verify():
    """Independent checks of the assembled stems.
    1. per line: whisper-small (hi, word timestamps, no prompt) on the stem cut to the line's window +-0.3 s,
       aligned to the line's tokens (vo_chain.align_tokens): tokens matched and |placed start - whisper start|.
       (A whole-stem pass is not usable: with 19 s of silence in 34 s and no VAD, whisper pulls the first word
       after every long pause up to 1.1 s early and hallucinates on hook B.)
    2. acoustic: every line's first word start must sit on a voiced onset of the stem (-45 dBFS runs) within
       20 ms, and no voice outside the placed phrases.
    3. hook B = hook A after the hook (from 3.0 s): max abs sample difference."""
    from faster_whisper import WhisperModel
    m = WhisperModel(os.path.join(V.WHISPER, 'faster-whisper-small'), device='cpu', compute_type='int8',
                     cpu_threads=V.THREADS)
    T = json.load(open(os.path.join(VO, 'timing.json')))
    out = {}
    for track, wname, sname in (('A', 'words.json', 'vo_stem.wav'), ('B', 'words_B.json', 'vo_stem_B.wav')):
        placed = json.load(open(os.path.join(VO, wname)))
        y = V.decode(os.path.join(VO, sname))
        y16 = V.decode(os.path.join(VO, sname), 16000)
        runs = runs_abs(y)
        onsets = np.array([a for a, b in runs])
        lines = []
        for r in T[track]['rows']:
            lw = [w for w in placed if w['line'] == r['line']]
            a = max(0.0, r['t0'] - 0.3)
            b = min(DUR, max(r['t1'], r['t1_voice']) + 0.3)
            x = y16[int(a * 16000):int(b * 16000)]
            segs, _ = m.transcribe(x, language='hi', word_timestamps=True, beam_size=5, vad_filter=False,
                                   condition_on_previous_text=False)
            heard = [dict(w=w.word.strip(), s=float(w.start) + a, e=float(w.end) + a) for g in segs for w in (g.words or [])
                     if V.norm_dev(w.word)]
            res = V.align_tokens([w['dev'] for w in lw], heard)
            # whisper stamps the first word of a clip that starts in silence at the clip start (0.3 s early here),
            # so the first word is checked acoustically (first_word_to_onset) and the whisper diff uses the rest
            ok = [(w, q) for w, q in zip(lw, res) if q is not None and q[3] > 0.3]
            d = [abs(w['start'] - q[0]) for w, q in ok[1:]] if len(ok) > 1 else []
            on_d = float(np.min(np.abs(onsets - lw[0]['start']))) if len(onsets) else 9.0
            lines.append(dict(line=r['line'], matched='%d/%d' % (len(ok), len(lw)),
                              mean_start_diff=round(float(np.mean(d)), 3) if d else None,
                              max_start_diff=round(float(np.max(d)), 3) if d else None,
                              first_word_to_onset=round(on_d, 3), heard=' '.join(h['w'] for h in heard)))
        ph = [tuple(p) for r in T[track]['rows'] for p in r['seg_edges']]
        cover = np.zeros(len(y), bool)
        for p0, p1 in ph:
            cover[max(0, int(p0 * SR)):int(p1 * SR)] = True
        stray = [(round(a, 3), round(b, 3)) for a, b in runs if cover[int(a * SR):int(b * SR)].mean() < 0.98]
        allm = [l for l in lines if l['max_start_diff'] is not None]
        out[track + '_note'] = 'whisper diffs over the non-first words of each line (%d lines have >1 word)' % len(allm)
        out[track] = dict(lines=lines, stray_voice=stray,
                          tokens_matched='%d/%d' % (sum(int(l['matched'].split('/')[0]) for l in lines),
                                                    sum(int(l['matched'].split('/')[1]) for l in lines)),
                          max_start_diff=max(l['max_start_diff'] for l in allm),
                          mean_start_diff=round(float(np.mean([l['mean_start_diff'] for l in allm])), 3),
                          max_first_word_to_onset=max(l['first_word_to_onset'] for l in lines))
        print(track, json.dumps({k: v for k, v in out[track].items() if k != 'lines'}, ensure_ascii=False))
        for l in lines:
            print('  ', json.dumps(l, ensure_ascii=False))
    ya, yb = V.decode(os.path.join(VO, 'vo_stem.wav')), V.decode(os.path.join(VO, 'vo_stem_B.wav'))
    k = int(3.0 * SR)
    out['B_equals_A_after_3s_max_abs_diff'] = float(np.max(np.abs(ya[k:] - yb[k:])))
    out['B_equals_A_after_3s_max_abs_diff_dB'] = round(20 * np.log10(max(1e-12, out['B_equals_A_after_3s_max_abs_diff'])), 1)
    print('B vs A after 3.0 s: max abs diff %.2e (%.1f dBFS)' % (out['B_equals_A_after_3s_max_abs_diff'],
                                                             out['B_equals_A_after_3s_max_abs_diff_dB']))
    json.dump(out, open(os.path.join(VO, 'verify.json'), 'w'), ensure_ascii=False, indent=1)
    return out


def plot():
    import cv2
    T = json.load(open(os.path.join(VO, 'timing.json')))
    W, Hh = 2400, 900
    img = np.full((Hh, W, 3), 18, np.uint8)
    px = lambda t: int(40 + (W - 80) * t / DUR)
    for track, y0, sname, wname in (('A', 60, 'vo_stem.wav', 'words.json'), ('B', 480, 'vo_stem_B.wav', 'words_B.json')):
        y = V.decode(os.path.join(VO, sname))
        hop = int(SR * DUR / (W - 80))
        env = np.abs(y[:hop * (W - 80)]).reshape(-1, hop).max(1)
        mid = y0 + 170
        for b in range(int(DUR / S['beat_s']) + 1):
            t = b * S['beat_s']
            cv2.line(img, (px(t), y0), (px(t), y0 + 340), (60, 60, 60) if b % 4 else (110, 110, 110), 1)
        for i, e in enumerate(env):
            h = int(150 * min(1.0, e / 0.8))
            cv2.line(img, (40 + i, mid - h), (40 + i, mid + h), (60, 140, 255), 1)
        for r in T[track]['rows']:
            ts, te, he = r['target_start'], r['target_end'], r['hard_end']
            cv2.rectangle(img, (px(ts), y0 + 5), (px(te), y0 + 22), (90, 200, 90), 1)
            cv2.line(img, (px(he), y0), (px(he), y0 + 340), (0, 0, 255), 1)
            for p0, p1 in r['phrases']:
                cv2.rectangle(img, (px(p0), y0 + 26), (px(p1), y0 + 40), (0, 210, 255), -1)
            cv2.putText(img, r['line'], (px(r['t0']), y0 + 60), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
        for w in json.load(open(os.path.join(VO, wname))):
            cv2.line(img, (px(w['start']), mid + 155), (px(w['start']), mid + 168), (255, 255, 255), 1)
        cv2.putText(img, 'hook %s  %s  LUFS %.2f TP %.2f' % (track, sname, T[track]['loudness']['lufs'],
                                                           T[track]['loudness']['tp']), (40, y0 - 15),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (230, 230, 230), 1)
    for t in range(0, int(DUR) + 1, 2):
        cv2.putText(img, '%d' % t, (px(t) - 6, Hh - 12), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)
    for a_, b_ in ((25.067, 28.133),):
        cv2.rectangle(img, (px(a_), 40), (px(b_), Hh - 40), (40, 40, 120), 1)
    out = os.path.join(VO, 'vo_timeline.png')
    cv2.imwrite(out, img)
    print('->', out)
    return out


KAHA = 'छब्बीस रिविज़न बाद क्लाइंट ने कहा। (SCRIPT fallback 3: no drawl)'
MSG = 'फिर आख़री मैसेज। (no drawl)'
PROMPT_VARIANT = {('L1B', 't3'): KAHA, ('L1B', 't4'): KAHA, ('L1B', 't5'): KAHA, ('L1B', 't6'): KAHA,
                  ('L1B', 't7'): KAHA,
                  ('L9', 't2'): 'और एक और एक और एक। (run-on: no commas)',
                  ('L9', 't3'): 'और एक और एक और एक। (run-on: no commas)',
                  ('L9', 't4'): 'और एक! और एक! और एक! (exclamations)',
                  ('L9', 't6'): 'औरएक, औरएक, औरएक। (fused)',
                  ('L10', 't3'): MSG, ('L10', 't4'): MSG, ('L10', 't5'): MSG,
                  ('L12', 't1'): 'और फिर क्लाइंट ने बोला, बस एक छोटा सा चेंज। (cut after बोला)'}
# cues from SCRIPT section 8 / BRIEF section 11 whose variant depends on whether a VO word sounds at that instant
CUES = [(0.267, 'A', 'pin 1 "Logo thora bara?" pin_thock_dark'), (1.067, 'A', 'logo swell v2'),
        (2.133, 'A', 'pin 2 "Aur bara." + whoosh'), (1.667, 'B', 'hook B timeline_scrub -8 (0.667 s)'), (2.333, 'B', 'hook B ui_click 0'),
        (3.200, 'AB', 'pin 3 "Thora left." pin_thock 0'), (6.400, 'AB', 'pin 5 cream fill'),
        (7.467, 'AB', 'pin 6 thock'), (9.600, 'AB', 'pin 8 thock'), (13.333, 'AB', 'Mummy thread pin'),
        (13.867, 'AB', 'Mummy thread pin'), (14.400, 'AB', 'Mummy thread pin'), (14.933, 'AB', 'braam (hero hit)'),
        (16.000, 'AB', 'pin v17'), (16.533, 'AB', 'pin 17 thock'), (19.733, 'AB', 'pin 21'), (20.267, 'AB', 'pin 22'),
        (20.800, 'AB', 'pin 23'), (21.333, 'AB', 'D7 transition'), (25.600, 'AB', 'payoff pin (hero hit)'),
        (27.733, 'AB', 'v1 restore (hero hit)'), (30.617, 'AB', 'end card glass_tap -12'),
        (32.633, 'AB', 'client marker ui_hover -14'), (33.333, 'AB', 'end card reverse_swell -8 (to 34.133)')]


def _f(v, fmt='%.3f'):
    return '-' if v is None else fmt % v


def report():
    """VO_TIMING.md from timing.json, asr/*.json, credits.json, pron_check.json and verify.json."""
    T = json.load(open(os.path.join(VO, 'timing.json')))
    C = json.load(open(os.path.join(VO, 'credits.json')))
    PR = json.load(open(os.path.join(ASRD, 'pron_check.json')))
    VF = json.load(open(os.path.join(VO, 'verify.json'))) if os.path.exists(os.path.join(VO, 'verify.json')) else {}
    sel = T['selected']
    asrs = {}
    for f in sorted(os.listdir(ASRD)):
        if re.match(r'L\w+_t\d\.json$', f):
            asrs[f[:-5]] = json.load(open(os.path.join(ASRD, f)))
    o = []
    A, B = T['A'], T['B']
    rowsA = {r['line']: r for r in A['rows']}
    rowsB = {r['line']: r for r in B['rows']}
    allrows = A['rows'] + [rowsB['L1B']]
    o.append('# VO_TIMING · Reel 1 · C26 · Pehle Wala Hi Theek Tha · `pehle_wala`\n')
    o.append('Author: hinglish-scriptwriter · 2026-10-09 · **MEASURED** on the final Vlad takes (replaces the ESTIMATED '
             'timings of `SCRIPT.md` §4 / `script.json`). Generated by `pipeline/jawad_reels/pehle_wala_vo.py report` '
             'from `<WS>/pehle_wala/vo/timing.json`; every number below is a measurement.\n')
    o.append('## 0. Deliverables\n')
    o.append('| file | what |\n|---|---|')
    o.append('| `workspace/jawad_reels/pehle_wala/vo/vo_stem.wav` (= `pehle_wala_vo_A.wav`) | hook A (public) VO stem, '
             '48 kHz 24-bit mono, %d samples = %.4f s = DUR, %.2f LUFS integrated, TP %.1f dBTP, LRA %.1f LU |'
             % (A['samples'], A['dur'], A['loudness']['lufs'], A['loudness']['tp'], A['loudness']['lra']))
    o.append('| `.../vo/vo_stem_B.wav` (= `pehle_wala_vo_B.wav`) | hook B (Trial): L1B + L2-L12, same format, %.2f LUFS, TP %.1f dBTP |'
             % (B['loudness']['lufs'], B['loudness']['tp']))
    o.append('| `.../vo/words.json` (= `pehle_wala_vo_A.words.json`), `words_B.json` | word timings in reel seconds on '
             'the Roman caption tokens (`word`, `start`, `end`, `keyword`, `line`, `dev`, `heard`, `ok`): '
             '`snake_captions.load_words` reads them as they are |')
    o.append('| `.../vo/timing.json`, `verify.json`, `credits.json`, `asr/*.json`, `proc/*` | measurements, independent '
             'whisper check, credit ledger, per-take ASR, processed takes (vo_chain reports) |')
    o.append('| `.../vo/vo_timeline.png` | waveform + targets + hard ends + word onsets (visual check) |\n')
    o.append('## 1. Voice, processing, credits\n')
    o.append('- Voice: Higgsfield `elevenlabs_v4`, preset Vlad `e5666b9c-99a2-4fac-8b4e-abee078b186d`, Devanagari '
             'prompt = `script.json` `dev` per line, stability omitted, no tags, one take per beat line (L12 with its '
             'continuation ", बस एक छोटा सा चेंज।" and cut after "बोला" so it keeps the rising, unfinished contour).')
    o.append('- **Prompt changes in the chosen takes (punctuation only, same words, same Roman caption tokens):** L1B '
             '"...ने कहा।" instead of "कहा..." (SCRIPT §4 fallback 3, needed for the 2.70 gate); L9 "और एक! और एक! और '
             'एक!" (the shortest count Vlad gave; see §5); L10 "...मैसेज।" instead of "मैसेज..." (both "..." takes, t1 and '
             't2, ran 0.21-0.28 s past the 24.95 hard end). `words*.json` keep the script\'s tokens and punctuation, so '
             'the captions still show "Phir aakhri message..." and "Aur ek, aur ek, aur ek".')
    o.append('- Chain: `vo_chain.process` (trim 40 ms, pause cap 0.45 s, rubberband 1.08x for every take, HPF 70 Hz, '
             'de-ess, 2.5:1 compression, -16 LUFS / -2 dBTP) on each take padded with 0.5 s of digital silence '
             '(SHARED_REQUESTS #8); phrases cut at measured word boundaries (absolute -45 dBFS voiced runs, 40 ms '
             'pads, 5/12 ms fades); each line level-matched to -16 LUFS; master = gain + look-ahead limiter '
             '(ffmpeg `alimiter`, latency compensated) to -16.0 LUFS, TP <= -2.1 dBTP. Limiter peak reduction: '
             'max %.2f dB (A); it acts on a few syllable peaks only.' % A['limiter_peak_reduction_db'])
    o.append('- Credits (own `get_cost` preflights, ledger `vo/credits.json`): **%.2f of 25** for %d jobs (%d '
             'pronunciation carriers, %d line takes incl. re-takes). One 7-job batch was refused by the backend (429 '
             'rate limit, 0 submitted, nothing billed) and re-sent in groups of 2-4. Account balance checks (global '
             'guard 6800): %s.' % (C['spent_credits'], len(C['requests']),
                                  sum(1 for r in C['requests'] if r['id'].startswith('P')),
                                  sum(1 for r in C['requests'] if not r['id'].startswith('P')),
                                  ', '.join('%.2f (%s)' % (b['balance'], b['when']) for b in C['balance_checks'])))
    o.append('')
    o.append('## 2. Pronunciation test (SCRIPT §7 risk words in carrier phrases)\n')
    o.append('ASR: %s.\n' % PR['asr'])
    o.append('| id | carrier (sent to Vlad) | tests | whisper-small hi | whisper-medium hi | whisper-small en | whisper-medium en | verdict |')
    o.append('|---|---|---|---|---|---|---|---|')
    for p in PR['items']:
        o.append('| %s | %s | %s | %s | %s | %s | %s | %s |' % (p['id'], p['text'], p['words'], p['hi_small'], p['hi_medium'],
                                                          p['en_small'] or '-', p['en_medium'] or '(not run)', p['verdict']))
    o.append('\n**Spelling decision:** %s.\n' % PR['decision'])
    o.append('## 3. Takes and CER\n')
    o.append('**CER used for the rule** (`cers()` in `pehle_wala_vo.py`): faster-whisper `small` and `medium`, language '
             '`hi`, beam 5, **no** prompt, no VAD, on the processed take; Levenshtein / reference length after NFC, lower '
             'case, nukta dropped, chandrabindu -> anusvara, punctuation and spaces removed, **vowel signs kept**; Latin '
             'words and numerals that whisper-medium writes for the script\'s loanwords ("26", "V1", "editor", "Pop!") '
             'are mapped to the script\'s Devanagari first (`map_latin`, from the token table). The line CER is the '
             'lower of the two models; the English passes (`en`) must hear every loanword keyword.\n')
    o.append('**Finding on the project metric:** `tts/scripts/evaluate.py` `norm()` (and so `vo_config.json` '
             '`cer_whisper_small_hi` = 0.079) removes every character that is not `\\w`; in Python\'s `re` the Devanagari '
             'vowel signs, virama and anusvara are not `\\w`, so it compares consonant skeletons only (measured: '
             '`फिर आख़री मैसेज` -> `फरआखरमसज`). Its values are kept in the table as "skel" for continuity; the rule uses '
             'the full metric. Rule: a line whose CER is over 0.15 or whose keyword fails is re-taken (within budget).\n')
    o.append('| line | take | prompt | proc dur (s) | CER small skel / full / map | CER medium skel / full / map | line CER | English keywords heard | whisper-small hi | whisper-medium hi | chosen |')
    o.append('|---|---|---|---|---|---|---|---|---|---|---|')
    for lid in ORDER:
        for name in sorted(k for k in asrs if k.rsplit('_', 1)[0] == lid):
            tag = name.rsplit('_', 1)[1]
            a = asrs[name]
            rep = json.load(open(os.path.join(PROC, '%s.report.json' % name)))
            ek = ', '.join('%s %s' % (k.split('|')[0], 'yes' if v else 'NO') for k, v in a['en_keys'].items()) or '-'
            cs, cm = a['cer_small'], a['cer_medium']
            o.append('| %s | %s | %s | %.3f | %.3f / %.3f / %.3f | %.3f / %.3f / %.3f | **%.3f** | %s | %s | %s | %s |' % (
                lid, tag, PROMPT_VARIANT.get((lid, tag), 'script text'), rep['final_dur'], cs['skel'], cs['full'],
                cs['fullmap'], cm['skel'], cm['full'], cm['fullmap'], a['cer'], ek, a['hi_small'], a['hi_medium'],
                '**yes**' if sel.get(lid) == tag else ''))
        if lid == 'L9':
            o.append('| L9 | t5 | carrier "वो लिखता गया, और एक, और एक, और एक, पूरी रात।" | raw only | - | - | - | - | not '
                     'processed: its three fragments measure 0.88 / 0.85 / 0.84 s raw (0.81 / 0.79 / 0.78 s at 1.08x), '
                     'no shorter than t4 | - | |')
    o.append('')
    o.append('Notes on the CER over 0.15 that remain: ' + TAKE_NOTES + '\n')
    o.append('## 4. Timing table, hook A (public) - measured, reel seconds\n')
    o.append('t0 = first word onset; t1 = audible end of the last word (the later of the aligned word end and the '
             'voiced offset); w/s = spoken words / (t1 - t0) ("v1" = 2 spoken words). Δ = measured - SCRIPT target. '
             'Flags: **MISS** = |Δ| > 0.3 s against the target; **OVER** = past the hard end.\n')
    o.append('| line | beat (frame) | target t0 -> t1 | hard end | measured t0 -> t1 | Δ t0 | Δ t1 | words | w/s | keyword @ t | phrases placed (on -> off) | flags |')
    o.append('|---|---|---|---|---|---|---|---|---|---|---|---|')
    misses = []
    for r in allrows:
        t1 = max(r['t1'], r['t1_voice'])
        fl = []
        if abs(r['d_start']) > 0.3:
            fl.append('MISS t0')
        if abs(r['d_end']) > 0.3:
            fl.append('MISS t1 %+.2f' % r['d_end'])
        if r['over_hard'] > 0:
            fl.append('OVER %+.3f' % r['over_hard'])
        if fl:
            misses.append((r, fl))
        o.append('| %s%s | %s (f%d) | %.3f -> %.3f | %.3f | %.3f -> %.3f | %+.3f | %+.3f | %d | %.2f | %s | %s | %s |' % (
            r['line'], ' (hook B)' if r['line'] == 'L1B' else '', r['beat'], r['frame'], r['target_start'],
            r['target_end'], r['hard_end'], r['t0'], t1, r['d_start'], r['d_end'], r['words'], r['wps'],
            ('%s @ %.3f' % (r['keyword'], r['keyword_at'])) if r['keyword'] else '- (all-white)',
            ' · '.join('%.3f-%.3f' % tuple(p) for p in r['phrases']), ', '.join(fl) or 'ok'))
    o.append('')
    o.append('Gaps between lines (hook A, voice end -> next onset, s): ' +
             ', '.join('%s->%s %.3f' % tuple(g) for g in A['gaps']) + '. Hook B: L1B->L2 %.3f.' % B['gaps'][0][2])
    o.append('Loop seam (L12 end -> DUR -> L1 onset at frame 0): **%.3f s** (A), %.3f s (B).' % (A['loop_seam_gap'], B['loop_seam_gap']))
    sp = sum(r['speech_s'] for r in A['rows'])
    o.append('Total VO (hook A): first onset %.3f s, last word end %.3f s (span %.3f s of the %.4f s reel); voiced '
             'speech %.2f s by the phrase spans (%.2f s by -45 dBFS voiced runs) = %.0f %% of the reel. Hook B: '
             'phrase speech %.2f s.' % (
                 A['rows'][0]['t0'], max(A['rows'][-1]['t1'], A['rows'][-1]['t1_voice']),
                 max(A['rows'][-1]['t1'], A['rows'][-1]['t1_voice']) - A['rows'][0]['t0'], DUR, sp, A['speech_s'],
                 100 * sp / DUR, sum(r['speech_s'] for r in B['rows'])))
    o.append('')
    o.append('## 5. Beats that miss their target by more than 0.3 s\n')
    if not misses:
        o.append('None.\n')
    for r, fl in misses:
        o.append('- **%s** (%s): target %.3f -> %.3f, measured %.3f -> %.3f, hard end %.3f: %s.' % (
            r['line'], ', '.join(fl), r['target_start'], r['target_end'], r['t0'], max(r['t1'], r['t1_voice']),
            r['hard_end'], NOTES.get(r['line'], '')))
    o.append('')
    o.append('## 6. Sound-design cues against the measured words (BRIEF §11 rule: pins inside VO words use the dark variants)\n')
    o.append('| t (s) | hook | cue | VO word sounding at t (A / B) |')
    o.append('|---|---|---|---|')
    WA = json.load(open(os.path.join(VO, 'words.json')))
    WB = json.load(open(os.path.join(VO, 'words_B.json')))

    def at(ws, t):
        h = [w for w in ws if w['start'] - 0.02 <= t <= w['end'] + 0.02]
        return ('%s "%s" %.3f-%.3f' % (h[0]['line'], h[0]['word'], h[0]['start'], h[0]['end'])) if h else 'none'
    for t, hk, cue in CUES:
        o.append('| %.3f | %s | %s | %s / %s |' % (t, hk, cue, at(WA, t) if 'A' in hk else '-', at(WB, t)))
    o.append('')
    if VF:
        o.append('## 7. Independent checks of the assembled stems (`verify.json`)\n')
        o.append('1. whisper-small (hi, no prompt) per line on the stem cut to the line window +-0.3 s, aligned to the '
                 'line tokens. A whole-stem pass was tried first and is not usable: with 19 s of silence in 34 s and no '
                 'VAD, whisper pulled the first word after each long pause up to 1.15 s early and hallucinated on hook B. '
                 'Whisper also stamps a clip\'s first word at the clip start, so first words are checked acoustically '
                 '(2.) and the whisper differences cover the other words.')
        o.append('2. acoustic: every line\'s first word start vs the nearest voiced onset of the stem (-45 dBFS runs); '
                 'voice outside the placed phrase segments ("stray").')
        o.append('3. hook B against hook A from 3.0 s on.\n')
        o.append('| hook | tokens heard | word start vs whisper (non-first words): mean / max | first word -> voiced onset (max) | stray voice |')
        o.append('|---|---|---|---|---|')
        for tr in ('A', 'B'):
            v = VF[tr]
            o.append('| %s | %s | %.3f / %.3f s | %.3f s | %s |' % (tr, v['tokens_matched'], v['mean_start_diff'],
                                                                v['max_start_diff'], v['max_first_word_to_onset'],
                                                                v['stray_voice'] or 'none'))
        o.append('')
        o.append('| line | heard (whisper-small, hook A; L1B from hook B) | tokens | max start diff (s) | first word -> onset (s) |')
        o.append('|---|---|---|---|---|')
        for l in VF['A']['lines'][:1] + [x for x in VF['B']['lines'] if x['line'] == 'L1B'] + VF['A']['lines'][1:]:
            o.append('| %s | %s | %s | %s | %.3f |' % (l['line'], l['heard'], l['matched'], _f(l['max_start_diff']),
                                                     l['first_word_to_onset']))
        o.append('')
        o.append('The largest whisper difference (L3 "Kisi", 0.37 s) is whisper gluing the placed 0.25 s "?" pause to '
                 'the next word; the placed start sits 0.010 s from the voiced onset. Hook B equals hook A from 3.0 s '
                 'on: max abs sample difference %.1e (%s dBFS).\n' % (VF['B_equals_A_after_3s_max_abs_diff'],
                                                                     VF['B_equals_A_after_3s_max_abs_diff_dB']))
    o.append('## 8. Visual check\n')
    o.append('`workspace/jawad_reels/pehle_wala/vo/vo_timeline.png`: per hook, the stem waveform on the 112.5 BPM '
             'grid (bars brighter), green boxes = SCRIPT target windows, red lines = hard ends, yellow bars = placed '
             'phrases, white ticks = word onsets, dark-red box = the no-VO window 25.067-28.133, orange = waveform.\n')
    open(os.path.join(DESIGN, 'VO_TIMING.md'), 'w').write('\n'.join(o) + '\n')
    print('->', os.path.join(DESIGN, 'VO_TIMING.md'))


TAKE_NOTES = ('**L10** (all five takes, line CER 0.167): whisper-medium writes the same "फिर आख्री मेसेज" for every take; '
              'the only two differences from the script are आख्री (the spoken "aakh-ri" written with a virama) and '
              'मेसेज (the other common Hindi spelling of "message"); against those two spellings the CER is 0.000, and '
              'both English passes hear "then the last message". It is spelling, not pronunciation, so the 4 re-takes '
              'stopped there. Rejected on CER: L9 t3 (0.250, "aar ek"), L9 t6 (0.250, fused "orek"), L1B t3 and t7 '
              '(0.185). Rejected on "client": L1B t3 (heard "plaint" by 3 of 4 passes). **Listen check for the chosen L1B t5:** its "client" is heard as "client" by 5 of 8 passes (full line: small-hi ख्लाएंट, small-en and medium-en "client"; the "client ne kaha" part alone: medium-hi and medium-en "client") but with a /p/ by 3 (medium-hi on the full line प्लाइंट; small-hi and small-en on the part alone प्लाएंट / "Plank"). t5 is the only valid take that meets the 2.70 gate with margin (2.580). Alternate if it sounds wrong: t1 (clean "client" in 7 of 7 readable passes, script text) ends 2.760 with the same gap closing, 2 frames past the gate. Spelling note for L1B: every '
              'take is written रेविशन / रविजन by whisper because Vlad says the English /ʒ/ of "revision" (both English '
              'passes: "26 revisions").')
NOTES = {
    'L1': 'Vlad reads it with two short breaths ("Bas · ek · chhota sa change", 0.09 s and 0.14 s at 1.08x); t3 is the '
          'shortest of three takes (t1 2.32 s, t2 2.25 s, t3 2.17 s of speech) and has CER 0.000. It lands inside the '
          'lockup exit (2.60) and the 2.70 hook rule; the BRIEF wish of <= 1.90 is missed by 0.37 s. Hook A is now '
          'voice-free 2.270-3.267 (1.00 s); pin 2 "Aur bara." (2.133) lands under the end of "change" (section 6)',
    'L1B': '',
    'L3': 'early, not late: "Kisi ko nahi pata" is 0.43 s faster than the estimate. No action; the 6.400 cue (pin 5) '
          'now falls 0.28 s after the voice, so it can stay full (section 6)',
    'L4': 'both "Clean." takes measure 0.80 s; SCRIPT fallback applies: the 7.467 thock uses pin_thock_dark',
    'L5': '0.02 s past; SCRIPT fallback applies: the 9.600 thock uses pin_thock_dark (it lands 0.03 s after the voice '
          'end, on the decay)',
    'L9': 'Vlad does not say "aur ek" in less than about 0.70 s per fragment at 1.08x: 6 takes, 4 prompt forms (commas '
          't1: 0.91-0.92 s each; run-on t2/t3: unusable boundaries; exclamations t4: 0.98 / 0.70 / 0.71 s; fused t6: '
          '0.73-0.76 s but CER 0.25; carrier t5: 0.78-0.81 s). Three fragments cannot fit 19.233-21.100 (1.87 s) '
          'without overlapping. Chosen t4 (shortest valid): fragments at 19.233 / 20.243 / 20.973 (pins 19.200 / '
          '19.733 / 20.267: +0.03 / +0.51 / +0.71 s), keyword "ek" at 21.270, end 21.683, so the D7 at 21.333 lands '
          'inside the last "ek!". Decision for the creative director: (a) keep it, the D7 hits the last "ek" (sync '
          'accent); (b) move the D7 to >= 21.733; (c) cut L9 to two fragments "Aur ek, aur ek." (ends 20.943, the '
          'rule of three is lost). Alternate: t1 (the scripted tired comma read) ends 22.033. Note: t4 was prompted '
          'with "!" so it may read punchier than the scripted "tired count": listen before the mix',
    'L11': 'the read is 0.63 s slower than the estimate (two clauses, comma beat placed at 0.15 s); it ends 0.36 s '
           'before its hard end and 0.61 s before L12. No action; caption chunks 14-17 re-solve on words.json',
}


def main(argv):
    cmd = argv[0] if argv else ''
    if cmd == 'process':
        ids = argv[1].split(',') if len(argv) > 1 and not argv[1].startswith('--') else ORDER
        tag = argv[argv.index('--tag') + 1] if '--tag' in argv else 't1'
        process(ids, tag)
    elif cmd == 'asr':
        sel = selected()
        names = argv[1].split(',') if len(argv) > 1 else ['%s_%s' % (l, sel[l]) for l in ORDER]
        asr(names)
    elif cmd == 'assemble':
        assemble()
    elif cmd == 'verify':
        verify()
    elif cmd == 'plot':
        plot()
    elif cmd == 'rescore':
        rescore()
    elif cmd == 'report':
        report()
    else:
        print(__doc__)


if __name__ == '__main__':
    main(sys.argv[1:])
