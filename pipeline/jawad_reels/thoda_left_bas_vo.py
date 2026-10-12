#!/usr/bin/env python3
"""thoda_left_bas_vo.py - Bijli series #2 "Thoda Left... Bas Bas!" VO: the paid Vlad (Higgsfield elevenlabs_v4) takes ->
processed lines (vo_chain) -> the VO stem on the reel grid (hook A + hook B) + reel-time word timings + VO_TIMING.md.

Sources (binding): brand_reels/design/reels/thoda_left_bas/script.json ("vo" lines V1-V15: DEV / Roman, f_in / f_out;
vo.tokens = the 1:1 Roman <-> DEV token table with the keyword flags), SCRIPT.md section 4, SHOTS.md (picture events),
LEAD_DECISIONS 3 (the measured takes are final; picture beats move to the VO). vo_chain.py is imported read-only
(decode, voiced runs, pause edit, rubberband stretch, HPF 70 Hz / de-ess / 2.5:1 comp / loudnorm -16 LUFS -2 dBTP,
faster-whisper word timings + DP alignment + snap). Same conventions as pencil_se_rewind_vo.py / bijli_chali_gayi_vo.py.

Takes (never regenerated, never a paid call): brand_reels/assets/thoda_left_bas/vo_raw/V<NN>_t<N>.mp3. Where a _t2
exists (V06, V08, V09) the take with the lower mean CER (faster-whisper small + medium, no prompt, on the processed
line, against the DEV text; best of the two) wins; ties (< 0.02) -> the shorter span. faster-whisper always gets a
16 kHz float32 numpy array decoded by ffmpeg (its PyAV decoder is incompatible here).

Hook B (Trial Reel, client chat first) has no take of its own: stem B = stem A without V2 ("Bas bas! Ab theek hai!" is
the TV lock, which hook B does not show); V1 reads the client's "thoda left..." bubble. Identical from the f144 splice.

    cd pipeline/jawad_reels
    tools/heavy.sh python3 thoda_left_bas_vo.py process     # every take at every speed in SPEEDS (cached)
    tools/heavy.sh python3 thoda_left_bas_vo.py assemble    # pick, place (PLAN), stems, words, VO_TIMING.md, vo_final
    options: --force (re-run vo_chain), --no-final (skip the brand_reels/assets copies)

Outputs (<RW> = workspace/jawad_reels/thoda_left_bas/vo): proc/<take>_<speed>_c<cap>.wav (+ vo_chain .words.json /
.report.json), takes.json (CER per take), placement.json, vo_stem.wav (hook A) / vo_stem_B.wav (1,728,000 samples =
36.000 s, 48 kHz 24-bit mono, -16 LUFS integrated, TP <= -2 dBTP), words.json / words_B.json (reel time, snake_captions
format + line / i / dev / heard / ok / start_f / end_f), timeline.png; copies brand_reels/assets/thoda_left_bas/vo_final/
(FLAC + json); the table goes to brand_reels/design/reels/thoda_left_bas/VO_TIMING.md.
"""
import argparse
import glob
import json
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
SLUG = 'thoda_left_bas'
RW = os.path.join(REPO, 'workspace', 'jawad_reels', SLUG, 'vo')
RAW = os.path.join(REPO, 'brand_reels', 'assets', SLUG, 'vo_raw')
FINAL = os.path.join(REPO, 'brand_reels', 'assets', SLUG, 'vo_final')
DESIGN = os.path.join(REPO, 'brand_reels', 'design', 'reels', SLUG)
SCRIPT_JSON = os.path.join(DESIGN, 'script.json')
MD = os.path.join(DESIGN, 'VO_TIMING.md')
SR, FPS, NF = 48000, 30, 1080          # VO-led: 1008 -> 1080 f (one bar more in the hook, VO_TIMING.md section 3)
DUR = NF / FPS                         # 36.000 s
NSAMP = NF * SR // FPS                 # 1,728,000
LUFS, TP_MAX = -16.0, -2.0
GAP_MIN = 0.12                         # minimum silence between two lines (Bijli ladder F2)
SPEEDS = (1.06, 1.08, 1.10)            # vo_config: 1.06-1.10x for reels; the gentlest speed that fits wins
VOICE_DBFS = -55.0                     # absolute voiced threshold for mastered lines (Bijli convention)
ALL = ['V%d' % k for k in range(1, 16)]
DROP = ['V6', 'V9', 'V13']             # ladder F4 (Bijli / pencil precedent): see the PLAN notes
ORDER_A = [k for k in ALL if k not in DROP]
ORDER_B = [k for k in ORDER_A if k != 'V2']
FILE_ID = {'V%d' % k: 'V%02d' % k for k in range(1, 16)}
# pause caps (cap, keep_cap) per line: shouts are chained fast (the hook is 2.4 s); default vo_chain 0.45 / 0.9.
CAPS = {'V1': (0.12, 0.18), 'V2': (0.12, 0.18), 'V3': (0.30, 0.40), 'V5': (0.25, 0.30), 'V6': (0.45, 0.60),
        'V7': (0.30, 0.45), 'V9': (0.30, 0.30), 'V10': (0.20, 0.25), 'V12': (0.12, 0.18), 'V13': (0.30, 0.30)}
CAP_DEFAULT = (0.45, 0.60)
KEEP_AFTER = {}
LOAN = {'left': 'लेफ़्ट', 'right': 'राइट', 'scene': 'सीन', 'dialogue': 'डायलॉग', 'revision': 'रिविज़न',
        'antenna': 'एंटीना', 'ok': 'ओके'}

# ------------------------------------------------------------------------------------------------ placement plan
# t = reel time (s) of the line's FIRST voiced onset, or anchor=(token index, frame): that word's onset on the frame.
# lo / hi = hard limits for the line's voice (start >= lo, end <= hi). why = the picture reason.
# Picture beats move to the VO (LEAD_DECISIONS 3): the proposed frames are in VO_TIMING.md section 3.
PLAN = {
    'V1':  dict(t=2 / FPS, lo=0.05, hi=None, why='hook: "Thoda left... thoda right..." over the snowy CRT (H1 / H1b)'),
    'V2':  dict(anchor=(0, 90), lo=None, hi=154 / FPS, why='"Bas bas!" on the LOCK f90 (H2 slam + tv_lock); "hai!" may cross the f144 splice (L-cut)'),
    'V3':  dict(t=152 / FPS, lo=None, hi=None, why='S2 roof: "Aaya?" (R1) / far "Nahi! Thoda left..." (R2)'),
    'V4':  dict(anchor=(0, 234), lo=None, hi=None, why='"Kiska left?!" on the R4 slam + tape stop f234'),
    'V5':  dict(t=272 / FPS, lo=None, hi=372 / FPS, why='S3 CRT room: "Thoda aur..." (C5) / "nahi nahi, wapas!" (C6), tail over the clamp'),
    'V6':  dict(t=342 / FPS, lo=None, hi=None, why='S4 clamp "Haan... haan... bas!": DROPPED (F4)'),
    'V7':  dict(anchor=(0, 381), lo=380 / FPS, hi=None, why='"Ab theek hai!" 0.1 s after the f378 LOCK transient (C9), "Arre, phir se?!" on the slip (C10)'),
    'V8':  dict(t=470 / FPS, lo=None, hi=None, why='S6 roof wind: "Yeh scene kabhi khatam nahi hua." (C11), L-cut across M3 f504'),
    'V9':  dict(t=540 / FPS, lo=None, hi=None, why='S7 "Bees saal baad...": DROPPED (F4)'),
    'V10': dict(t=540 / FPS, lo=538 / FPS, hi=None, why='T1 toast f540 / phone bubbles: the client\'s words, read dry'),
    'V11': dict(t=668 / FPS, lo=None, hi=716 / FPS, why='"Dialogue wahi hai." (C13) over the TAB / AB split, ends before the f720 lock'),
    'V12': dict(anchor=(0, 720), lo=None, hi=None, why='client "Bas bas!" on the f720 lock (C14 / T2 = the rhyme with V2)'),
    'V13': dict(t=760 / FPS, lo=None, hi=809 / FPS, why='export "Sattaees revision baad...": DROPPED (F4)'),
    'V14': dict(t=832 / FPS, lo=831 / FPS, hi=935 / FPS, why='PAYOFF P1 (the f828 hit owns its first 0.1 s)'),
    'V15': dict(t=977 / FPS, lo=None, hi=1076 / FPS, why='outro question (profile outro from f954), ends <= f1076'),
}
# Ladder F4 (Bijli V9 / pencil V9 precedent), measured at 1.10x (the fastest allowed speed, tight pause caps):
#   hook  V1 2.80 s + V2 1.95 s: "Bas" can land no earlier than f90 -> the hook needs 2 bars (reel 1008 -> 1080 f).
#   V6 "Haan... haan... bas!" 2.31 s: S3+S4 (f270-f377 = 3.6 s) hold V5 (3.20 s) only; captions C7 / C8 + the clamp
#      ticks carry it.
#   V9 "Bees saal baad..." 1.03 s: V8 (2.15 s) runs from the V7 end (f465) across M3 to f535, and V10 (4.11 s) + V11
#      (1.14 s) must end before the f720 lock: no room; the `20 SAAL BAAD` caption carries it.
#   V13 "Sattaees revision baad..." 2.28 s: from the V12 end (f778) it would run into the drop-out (f810); C15 + the
#      export bar carry it.
#   The dropped takes stay processed in proc/ (takes.json has their CER).

# ------------------------------------------------------------------------------------------------ script
def load_lines():
    """{id: dict(dev=[tokens], rom=[tokens, '*' on keywords], roman, dev_text, emotion, f_in, f_out, captions)}."""
    d = json.load(open(SCRIPT_JSON, encoding='utf8'))
    toks = d['vo']['tokens']
    out = {}
    for L in d['vo']['lines']:
        dev = V.tokens(L['dev'])
        tk = [t for t in toks if t['line'] == L['id']]
        if len(dev) != len(tk):
            raise ValueError('%s: DEV %d vs token table %d' % (L['id'], len(dev), len(tk)))
        rom = [('*' if t['keyword'] else '') + t['roman'] for t in tk]
        out[L['id']] = dict(dev=dev, rom=rom, roman=L['roman'].replace('*', ''), dev_text=L['dev'],
                            emotion=L.get('emotion', ''), f_in=L['f_in'], f_out=L['f_out'], captions=L['captions'])
    return out


# ------------------------------------------------------------------------------------------------ measures
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
    hyp = re.sub(r'[A-Za-z]+', lambda m: LOAN.get(m.group(0).lower(), m.group(0)), hyp)
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
def takes(lid):
    return sorted(glob.glob(os.path.join(RAW, '%s_t*.mp3' % FILE_ID[lid])))


def caps(lid):
    return CAPS.get(lid, CAP_DEFAULT)


def proc_path(lid, take, speed):
    c, k = caps(lid)
    return os.path.join(RW, 'proc', '%s_%.2f_c%02d%02d.wav' % (os.path.splitext(os.path.basename(take))[0], speed,
                                                               round(c * 100), round(k * 100)))


def run_chain(lines, lid, take, speed, force=False):
    out = proc_path(lid, take, speed)
    if force or not os.path.exists(os.path.splitext(out)[0] + '.report.json'):
        L = lines[lid]
        c, k = caps(lid)
        V.process(take, L['dev'], L['rom'], out=out, speed=speed, keep_after=KEEP_AFTER.get(lid, ()), cap=c,
                  keep_cap=k)
    rep = json.load(open(os.path.splitext(out)[0] + '.report.json', encoding='utf8'))
    words = json.load(open(os.path.splitext(out)[0] + '.words.json', encoding='utf8'))
    x = V.decode(out)
    return x, words, rep


def tab_key(lid, take, sp):
    c, k = caps(lid)
    return '%s@%.2f/c%.2f-%.2f' % (os.path.basename(take), sp, c, k)


def cmd_process(force=False):
    lines = load_lines()
    os.makedirs(os.path.join(RW, 'proc'), exist_ok=True)
    tp = os.path.join(RW, 'takes.json')
    tab = json.load(open(tp, encoding='utf8')) if os.path.exists(tp) and not force else {}
    for lid in ALL:
        for take in takes(lid):
            for sp in SPEEDS:
                key = tab_key(lid, take, sp)
                x, words, rep = run_chain(lines, lid, take, sp, force)
                r = runs_abs(x)
                if key not in tab:
                    heard = whisper_text(x)
                    hm = whisper_text(x, 'medium')
                    tab[key] = dict(line=lid, take=os.path.basename(take), speed=sp, caps=list(caps(lid)),
                                    heard=heard, cer_small=round(cer(heard, lines[lid]['dev_text']), 3),
                                    heard_medium=hm, cer_medium=round(cer(hm, lines[lid]['dev_text']), 3))
                tab[key]['cer'] = min(tab[key]['cer_small'], tab[key]['cer_medium'])      # CER best (Bijli)
                tab[key].update(span=round(r[-1][1] - r[0][0], 3) if r else None, dur=round(len(x) / SR, 3),
                                matched='%d/%d' % (rep['matched'], rep['tokens']), pauses=rep['pauses'],
                                lufs=rep['loudness']['lufs'], tp=rep['loudness']['tp'])
                print(key, tab[key]['span'], tab[key]['cer_small'], tab[key]['cer_medium'], tab[key]['heard'], '|',
                      tab[key]['heard_medium'], flush=True)
                json.dump(tab, open(tp, 'w', encoding='utf8'), ensure_ascii=False, indent=1)
    return tab


def rows_of(tab, lid):
    out = {}
    for take in takes(lid):
        for sp in SPEEDS:
            k = tab_key(lid, take, sp)
            if k in tab:
                out.setdefault(os.path.basename(take), []).append(tab[k])
    return out


def pick(tab, lid):
    """The take of a line: lowest mean CER over the processed speeds; tie (< 0.02) -> the shorter span at 1.08x."""
    rows = rows_of(tab, lid)
    score = {t: (float(np.mean([r['cer'] for r in rs])), [r['span'] for r in rs if abs(r['speed'] - 1.08) < 1e-6][0])
             for t, rs in rows.items()}
    best = min(s[0] for s in score.values())
    cands = [t for t, s in score.items() if s[0] <= best + 0.02]
    return min(cands, key=lambda t: score[t][1]), score


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


def r1(f):
    """script.json (r1, 1008-f grid) frame -> the 1080-f grid: + 72 after the hook (one bar inserted at f72)."""
    return f + 72 if f >= 72 else f


def fr(t):
    return round(t * FPS, 1)


def cmd_assemble(final=True):
    lines = load_lines()
    tab = json.load(open(os.path.join(RW, 'takes.json'), encoding='utf8'))
    chosen, scores, notes = {}, {}, []
    for lid in ALL:
        take, sc = pick(tab, lid)
        chosen[lid], scores[lid] = take, sc
    placed = {}

    def desired(lid, words, s0):
        P = PLAN[lid]
        if 'anchor' in P:
            i, f = P['anchor']
            return f / FPS - (words[i]['start'] - s0)
        return P['t']

    prev_end = 0.0
    for idx, lid in enumerate(ORDER_A):
        P = PLAN[lid]
        take = os.path.join(RAW, chosen[lid])
        nxt = ORDER_A[idx + 1] if idx + 1 < len(ORDER_A) else None
        nxt_t = (PLAN[nxt].get('t') or PLAN[nxt]['anchor'][1] / FPS) if nxt else None
        limit_end = min(P['hi'] or 1e9, (nxt_t - GAP_MIN) if nxt_t else DUR - 0.04)
        best = None
        for sp in SPEEDS:                                    # the gentlest speed that fits its slot
            x, words, rep = run_chain(lines, lid, take, sp)
            r = runs_abs(x)
            s0, s1 = r[0][0], r[-1][1]
            t0 = max(desired(lid, words, s0), prev_end + GAP_MIN if prev_end else 0.0, P['lo'] or 0.0)
            best = dict(speed=sp, x=x, words=words, rep=rep, s0=s0, s1=s1, t0=t0, t1=t0 + s1 - s0)
            if best['t1'] <= limit_end + 1e-6:
                break
        if best['t1'] > (P['hi'] or 1e9) + 1e-6:             # hard end: pull the start earlier (never < prev+gap)
            need = best['t1'] - P['hi']
            room = best['t0'] - max(prev_end + GAP_MIN if prev_end else 0.04, P['lo'] or 0.0)
            sh = min(need, max(0.0, room))
            best['t0'] -= sh
            best['t1'] -= sh
            notes.append('%s: start pulled %.3f s earlier to end by its hard limit %.3f s (f%.1f)'
                         % (lid, sh, P['hi'], fr(P['hi'])))
            if best['t1'] > P['hi'] + 1e-6:
                notes.append('WARNING %s: ends %.3f s after its hard limit' % (lid, best['t1'] - P['hi']))
        elif nxt_t and best['t1'] > nxt_t - GAP_MIN + 1e-6:
            notes.append('%s: runs %.3f s into the next line\'s planned start; %s moves later'
                         % (lid, best['t1'] + GAP_MIN - nxt_t, nxt))
        prev_end = best['t1']
        placed[lid] = best
    for lid in DROP:
        notes.append('ladder F4: %s dropped from the VO; best take `%s` processed and kept in proc/' % (lid, chosen[lid]))
    stems = {}
    for ver, order in (('A', ORDER_A), ('B', ORDER_B)):
        y = np.zeros(NSAMP, np.float32)
        words = []
        for lid in order:
            b = placed[lid]
            off = b['t0'] - b['s0']
            i0 = int(round(off * SR))
            seg = b['x'][max(0, -i0):][:NSAMP - max(i0, 0)]
            y[max(i0, 0):max(i0, 0) + len(seg)] += seg
            for i, w in enumerate(b['words']):
                words.append(dict(word=w['word'], start=round(w['start'] + off, 3), end=round(w['end'] + off, 3),
                                  keyword=bool(w['keyword']), line=lid, i=i, dev=w.get('dev'), heard=w.get('heard'),
                                  ok=w.get('ok'), start_f=fr(w['start'] + off), end_f=fr(w['end'] + off)))
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
    for lid, b in placed.items():
        k = tab_key(lid, os.path.join(RAW, chosen[lid]), b['speed'])
        plc[lid] = dict(take=chosen[lid], speed=b['speed'], caps=list(caps(lid)), start=round(b['t0'], 3),
                        end=round(b['t1'], 3), start_f=fr(b['t0']), end_f=fr(b['t1']), planned_f=r1(lines[lid]['f_in']),
                        planned_out_f=r1(lines[lid]['f_out']), cer=tab[k]['cer'], heard=tab[k]['heard'],
                        heard_medium=tab[k].get('heard_medium'),
                        matched='%d/%d' % (b['rep']['matched'], b['rep']['tokens']), pauses=b['rep']['pauses'],
                        why=PLAN[lid]['why'])
    gaps = [round(plc[b]['start'] - plc[a]['end'], 3) for a, b in zip(ORDER_A, ORDER_A[1:])]
    doc = dict(placement=plc, notes=notes,
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
    for lid in ORDER_A:
        p = plc[lid]
        print('%-4s %-11s %.2f f%6.1f-f%6.1f (plan f%d-f%d) cer %.3f %s' % (lid, p['take'], p['speed'], p['start_f'],
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
    for k in range(0, NF + 1, 18):
        xx = int(k / NF * W)
        d.line([(xx, 270 if k % 72 else 250), (xx, 300)], fill=(120, 110, 130))
    for lid, p in plc.items():
        a, b = int(p['start'] / DUR * W), int(p['end'] / DUR * W)
        d.rectangle([a, 20, b, 34], outline=(80, 230, 255))
        d.text((a + 2, 4), '%s f%d' % (lid, round(p['start_f'])), fill=(255, 243, 230))
    for w in st['words']:
        xx = int(w['start'] / DUR * W)
        d.line([(xx, 40), (xx, 60)], fill=(242, 49, 43) if w['keyword'] else (200, 200, 200))
    im.save(path)


# ------------------------------------------------------------------------------------------------ report
PICTURE = {   # picture events tied to a VO word: (line, token index, frame in the 1080-f grid (r1 + 72 after the
              # hook), event[, 'stay'])
    'V1': [(0, 0, 'H1 `THODA *left...*` (mid-rise on f0)', 'stay'), (3, 18, 'H1b keyword flip `*right...*` + yaw +9 (r1 f18)')],
    'V2': [(0, 90, 'H2 `BAS BAS!` SLAM + picture LOCK + tv_lock (r1 f36; bar 1 beat 1)', 'stay'),
           (2, 54, 'H3 `AB *theek hai!*` (r1 f54)')],
    'V3': [(0, 144, 'R1 `*Aaya?*` (S2 cut f144 = r1 f72)'), (1, 171, 'R2 far `NAHI! THODA LEFT...` (r1 f99)')],
    'V4': [(0, 234, 'R4 `*kiska* left?!` SLAM + tape_stop (r1 f162)', 'stay')],
    'V5': [(0, 270, 'C5 `thoda *aur...*` (S3 cut f270 = r1 f198)'), (2, 297, 'C6 `NAHI NAHI, *wapas!*` (r1 f225)')],
    'V7': [(0, 378, 'C9 `AB *theek hai!*` LOCK + TV sting (r1 f306)', 'stay'),
           (3, 423, 'C10 `ARRE, *phir se?!*` (r1 f351; gust f414, slip f418-f430)')],
    'V8': [(0, 450, 'C11 `YEH SCENE / *khatam* / nahi hua...` (S6 cut f450 = r1 f378)')],
    'V10': [(0, 540, 'T1 toast `thoda left...` (r1 f468)'), (1, 549, 'X 540 -> 538 click + `-2 px` (r1 f477)'),
            (2, 562, 'P1b phone bubble `thoda right...` (r1 f490)'), (4, 576, 'P1c phone bubble `nahi, pehle wala` (r1 f504)')],
    'V11': [(0, 612, 'C13 `DIALOGUE / *wahi* hai.` (r1 f540)')],
    'V12': [(0, 720, 'C14 `BAS BAS!` + T2 + tv_lock + impact_big (r1 f648)', 'stay')],
    'V14': [(0, 828, 'P1 PAYOFF lockup (hit f828 = r1 f756)', 'stay')],
    'V15': [(0, 977, 'outro question on the card (PO from f954 = r1 f882)', 'stay')],
}


def write_md(lines, plc, stems, notes, scores, tab, doc):
    A_, B_ = stems['A'], stems['B']
    W = lambda ws, lid: [w for w in ws if w['line'] == lid]  # noqa: E731
    o = ['# VO_TIMING · Thoda Left... Bas Bas! (@jawad_mp4)', '',
         '2026-10-11, sound-designer + music-supervisor, `pipeline/jawad_reels/thoda_left_bas_vo.py assemble` '
         '(measured). Voice: Higgsfield preset Vlad, `elevenlabs_v4`, the paid takes in '
         '`brand_reels/assets/thoda_left_bas/vo_raw/` (none regenerated, no paid call). Chain `vo_chain.py` per '
         'vo_config: trim to 40 ms, internal pauses capped per line (shouts 0.12-0.30 s, speech 0.45 s; table in '
         'section 4), rubberband 1.06-1.10x (formant preserved; the gentlest speed that fits its slot), HPF 70 Hz, '
         'de-ess, 2.5:1 compression, loudnorm -16 LUFS / -2 dBTP; word timings faster-whisper small (DEV prompt, '
         'numpy input) aligned to the DEV tokens, snapped to the voiced onsets. LEAD_DECISIONS 3: picture beats move '
         'to the VO (section 3).', '']
    for ver, s in (('A', A_), ('B', B_)):
        m = s['master']['post']
        o.append('- **Stem %s** `%s`: %d samples (%.3f s) at 48000 Hz, %.2f LUFS integrated, %.2f dBTP, LRA %.1f LU, '
                 'VO %.3f-%.3f s, %.2f s voiced, %d words (%d keywords), %d %% of word starts on voice; gain %+.2f dB, '
                 'limiter %s; lines %s.' % (ver, os.path.relpath(s['path'], REPO), NSAMP, DUR, m['lufs'], m['tp'],
                                            m['lra'], s['voice'][0], s['voice'][1], s['voiced_s'], len(s['words']),
                                            sum(w['keyword'] for w in s['words']), round(100 * s['on_voice']),
                                            s['master']['gain_db'], 'on' if s['master']['limiter'] else 'off',
                                            '+'.join(s['order']) if ver == 'B' else 'V1-V15'))
    o += ['- Hook B (Trial Reel) has no take of its own: stem B = stem A without V2 (the TV-lock line); V1 reads the '
          'client bubble. Identical to A from the f144 splice (r1 f72).',
          '- Words: `workspace/jawad_reels/thoda_left_bas/vo/words.json` (A) / `words_B.json` (B), reel time, '
          'snake_captions format (+ line, i, dev, heard, ok, start_f, end_f). Copies (FLAC 24-bit + json): '
          '`brand_reels/assets/thoda_left_bas/vo_final/thoda_left_bas_vo_{A,B}.flac` / `.words.json`, '
          '`placement.json`, `takes.json`.',
          '- Lines not in the VO (ladder F4): ' + ', '.join(DROP) + ' (their captions carry them; takes processed and kept).',
          '- Minimum gap between lines: %.3f s (rule >= %.2f s).' % (doc['min_gap'], GAP_MIN), '',
          '## 1. Line timing (hook A)', '',
          '| line | take | speed | start → end (s) | frames | script f (r1 +72 after the hook) | Δ start f | words (reel s) | CER | aligned |',
          '|---|---|---|---|---|---|---|---|---|---|']
    for lid in ORDER_A:
        p = plc[lid]
        ws = W(A_['words'], lid)
        wtxt = ' '.join('%s%s %.2f' % ('**' if w['keyword'] else '', w['word'] + ('**' if w['keyword'] else ''),
                                       w['start']) for w in ws)
        o.append('| %s | `%s` | %.2f | %.3f → %.3f | f%.1f-f%.1f | f%d-f%d | %+.1f | %s | %.3f | %s |'
                 % (lid, p['take'], p['speed'], p['start'], p['end'], p['start_f'], p['end_f'], p['planned_f'],
                    p['planned_out_f'], p['start_f'] - p['planned_f'], wtxt, p['cer'], p['matched']))
    o += ['', '## 2. Word frames (stem A; f = reel frame at 30 fps)', '',
          '| line | word | start s | end s | start f | end f | keyword | heard |', '|---|---|---|---|---|---|---|---|']
    for lid in ORDER_A:
        for w in W(A_['words'], lid):
            o.append('| %s | %s | %.3f | %.3f | %.1f | %.1f | %s | %s |' % (lid, w['word'], w['start'], w['end'],
                                                                         w['start_f'], w['end_f'],
                                                                         'yes' if w['keyword'] else '', w['heard']))
    o += ['', '## 3. Picture beats that move to the VO (proposed frames for the motion designer)', '',
          'LEAD_DECISIONS 3: the picture follows the measured VO. Proposed frame = the onset frame of the VO word '
          '(rounded down, so the visual leads the word by at most 1 frame). |Δ| <= 2 f, or a structural frame '
          '(cut / lock / slam marked "stays"): keep the planned frame.', '',
          '| line | word | event (SHOTS / SCRIPT) | planned f | VO onset f | proposed f | Δ f |',
          '|---|---|---|---|---|---|---|']
    moves = []
    for lid in ORDER_A:
        ws = W(A_['words'], lid)
        for row in PICTURE.get(lid, []):
            i, f_plan, ev = row[:3]
            if i >= len(ws):
                continue
            on = ws[i]['start_f']
            stay = len(row) > 3
            prop = f_plan if (stay or abs(on - f_plan) <= 2) else int(np.floor(on))
            if prop != f_plan:
                moves.append('%s f%d -> f%d' % (ev.split(' ')[0], f_plan, prop))
            o.append('| %s | %s | %s | f%d | %.1f | **f%d**%s | %+d |' % (lid, ws[i]['word'], ev, f_plan, on, prop,
                                                                       ' (stays)' if stay else '', prop - f_plan))
    o += ['', 'Frames above are on the NEW 1080-f grid. Caption lockups whose word moved: ' +
          ('; '.join(moves) if moves else 'none') + '. The music (thoda_left_bas_music.py) and the SFX cue table '
          '(thoda_left_bas_sfx.py) already follow these frames; the full new shot grid is in SOUND.md section 2.']
    o += ['', '## 4. Takes (CER = faster-whisper small and medium, no prompt, on the processed line vs the DEV text; '
          'best of the two; nukta / candrabindu folded, Latin loan words mapped)', '',
          '| line | pause caps (s) | take | mean CER (1.06/1.08/1.10) | span @1.08 s | heard @ placed speed (small / medium) | chosen |',
          '|---|---|---|---|---|---|---|']
    for lid in ALL:
        for t, s in sorted(scores[lid].items()):
            sp = plc[lid]['speed'] if lid in plc else 1.10
            k = tab_key(lid, os.path.join(RAW, t), sp)
            o.append('| %s | %.2f / %.2f | `%s` | %.3f | %.3f | %s / %s | %s |' % (
                lid, caps(lid)[0], caps(lid)[1], t, s[0], s[1], tab[k]['heard'], tab[k].get('heard_medium', ''),
                ('yes' if t == plc[lid]['take'] else '') if lid in plc else 'dropped (F4)'))
    o += ['', '## 5. Notes', ''] + ['- ' + n for n in notes] + [
        '- Rebuild: `cd pipeline/jawad_reels && tools/heavy.sh python3 thoda_left_bas_vo.py process && '
        'tools/heavy.sh python3 thoda_left_bas_vo.py assemble` (deterministic; PLAN / CAPS at the top of the module '
        'hold the slots), then `tools/heavy.sh python3 thoda_left_bas_sfx.py build` (music, SFX, mixes).', '']
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
