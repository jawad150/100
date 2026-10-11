#!/usr/bin/env python3
"""pencil_se_rewind_vo.py - Bijli series #1 "Pencil Se Rewind" VO: the paid Vlad (Higgsfield elevenlabs_v4) takes ->
processed lines (vo_chain) -> the VO stem on the reel grid (hook A + hook B) + reel-time word timings + VO_TIMING.md.

Sources (binding): brand_reels/design/reels/pencil_se_rewind/script.json ("vo" lines: DEV / Roman per line, start_f),
SCRIPT.md section 3 (delivery, windows), SHOTS.md (picture events), LEAD_DECISIONS 3 (the measured takes are final;
picture beats move to the VO). vo_chain.py is imported read-only (decode, voiced runs, edit, rubberband stretch,
HPF 70 Hz / de-ess / 2.5:1 comp / loudnorm -16 LUFS -2 dBTP, faster-whisper word timings + DP alignment + snap).

Takes (never regenerated, never a paid call): brand_reels/assets/pencil_se_rewind/vo_raw/<ID>_t<N>.mp3, ID = V01 ...
V13, V01B (hook B). Where a _t2 exists the take with the lower CER (faster-whisper small, no prompt, on the processed
line, against the DEV text) wins; ties -> the shorter one.

    cd pipeline/jawad_reels
    tools/heavy.sh python3 pencil_se_rewind_vo.py process     # every take at every speed in SPEEDS (cached)
    tools/heavy.sh python3 pencil_se_rewind_vo.py assemble    # pick, place (PLAN), stems, words, VO_TIMING.md, vo_final
    options: --force (re-run vo_chain), --no-final (skip the brand_reels/assets copies)

Outputs (<RW> = workspace/jawad_reels/pencil_se_rewind/vo): proc/<take>_<speed>.wav (+ vo_chain .words.json /
.report.json), takes.json (CER per take), placement.json, vo_stem.wav (hook A) / vo_stem_B.wav (1,638,400 samples =
34.133 s, 48 kHz 24-bit mono, -16 LUFS integrated, TP <= -2 dBTP), words.json / words_B.json (reel time, snake_captions
format + line / i / dev / heard / ok / frame), timeline.png; copies brand_reels/assets/pencil_se_rewind/vo_final/
(FLAC + json); the table goes to brand_reels/design/reels/pencil_se_rewind/VO_TIMING.md.
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
SLUG = 'pencil_se_rewind'
RW = os.path.join(REPO, 'workspace', 'jawad_reels', SLUG, 'vo')
RAW = os.path.join(REPO, 'brand_reels', 'assets', SLUG, 'vo_raw')
FINAL = os.path.join(REPO, 'brand_reels', 'assets', SLUG, 'vo_final')
DESIGN = os.path.join(REPO, 'brand_reels', 'design', 'reels', SLUG)
SCRIPT_JSON = os.path.join(DESIGN, 'script.json')
MD = os.path.join(DESIGN, 'VO_TIMING.md')
SR, FPS, NF = 48000, 30, 1024
DUR = NF / FPS                         # 34.1333 s
NSAMP = NF * SR // FPS                 # 1,638,400
LUFS, TP_MAX = -16.0, -2.0
GAP_MIN = 0.12                         # minimum silence between two lines (Bijli ladder F2)
SPEEDS = (1.06, 1.08, 1.10)            # vo_config: 1.06-1.10x for reels; the gentlest speed that fits wins
VOICE_DBFS = -55.0                     # absolute voiced threshold for mastered lines (Bijli convention)
ALL = ['V1', 'V2', 'V3', 'V4', 'V5', 'V6', 'V7', 'V8', 'V9', 'V10', 'V11', 'V12', 'V13']
ORDER_A = [k for k in ALL if k not in ('V9',)]   # DROP (below)
ORDER_B = ['V1B'] + ORDER_A[1:]
FILE_ID = {'V1B': 'V01B', **{'V%d' % k: 'V%02d' % k for k in range(1, 14)}}
KEEP_AFTER = {'V1': (1,), 'V11': (2,)}  # dramatic beats (SCRIPT 3): "Rewind button? | Pencil.", "Pehla editing tool? | Pencil."
LOAN = {'editing': 'एडिटिंग', 'tool': 'टूल', 'play': 'प्ले', 'pencil': 'पेंसिल', 'battery': 'बैटरी',
        'cassette': 'कैसेट', 'walkman': 'वॉकमैन', 'rewind': 'रिवाइंड', 'button': 'बटन', 'scrubbing': 'स्क्रबिंग', 'skrubbing': 'स्क्रबिंग'}

# ------------------------------------------------------------------------------------------------ placement plan
# t   = reel time (s) of the line's FIRST voiced onset (the frame in brackets); speed = the speed used.
# lo / hi = hard limits for the line's voice (start >= lo, end <= hi). why = the picture reason.
# Picture beats move to the VO (LEAD_DECISIONS 3): the proposed new frames are in VO_TIMING.md section 3.
PLAN = {
    'V1':  dict(t=3 / FPS, lo=0.05, hi=62 / FPS, why='hook A, ends before the f64 splice'),
    'V1B': dict(anchor=(1, 32), lo=0.05, hi=62 / FPS, why='hook B: "khatam?" on the planned f32 slam'),
    'V2':  dict(t=70 / FPS, lo=66 / FPS, hi=None, why='S2/S3 walkman + pencil (L2+L3)'),
    'V3':  dict(t=198 / FPS, lo=None, hi=None, why='S4 label + S5 fast rewind (L4+L5)'),
    'V4':  dict(t=320 / FPS, lo=320 / FPS, hi=None, why='S6 keys: "Play." on the PLAY key f320 (L6)'),
    'V5':  dict(t=395 / FPS, lo=393 / FPS, hi=None, why='S7 "Mil gaya!" right after the 2nd PLAY key (L7+L8)'),
    'V6':  dict(t=466 / FPS, lo=465 / FPS, hi=None, why='S8 re-hook, after the f464 slam transient (L9)'),
    'V7':  dict(t=509 / FPS, lo=None, hi=None, why='S9 rescue, whispered (L10); runs into the f576 pull-back'),
    'V8':  dict(t=594 / FPS, lo=None, hi=None, why='S10 reveal, NLE panels landed (L11)'),
    'V9':  dict(t=648 / FPS, lo=None, hi=None, why='S11 scrub (L12): DROPPED, ladder F4 (captions + scrub SFX carry it)'),
    'V10': dict(t=698 / FPS, lo=None, hi=750 / FPS, why='S12, ends before the f752 drop-out (L13)'),
    'V11': dict(t=778 / FPS, lo=778 / FPS, hi=None, why='S13 payoff: 10 f (0.33 s) after the f768 hit, so the hit owns '
                                                          'its 400 ms (the payoff is the loudest moment) (L14)'),
    'V12': dict(t=852 / FPS, lo=None, hi=None, why='S13 tag (L15); its tail crosses the f896 D2 razor (L-cut)'),
    'V13': dict(t=930 / FPS, lo=None, hi=1005 / FPS, why='S14 outro question, ends <= f1005'),
}
# Ladder F4 (Bijli precedent): V9 "Peeche. Aage. Yahan." leaves the VO. Measured need from the f464 slam to the f750
# limit with V9: V6..V10 = 10.05 s of voice at 1.10x + 4 x 0.12 s gaps = 10.53 s against 9.53 s; even with V7 / V9
# pauses cut to 0.2 s the slam would have to move >= 0.6 s (2 beats) earlier. Without V9 the picture keeps its
# structure (scrub = captions + timeline_scrub SFX + music stutters). V9's processed take stays in proc/.
DROP = ['V9']


# ------------------------------------------------------------------------------------------------ script
def load_lines():
    """{id: dict(dev=[tokens], rom=[tokens with '*' on keywords], roman, delivery, start_f, captions)}."""
    d = json.load(open(SCRIPT_JSON, encoding='utf8'))
    toks = d['tokens']
    out = {}
    for L in d['vo']['lines']:
        dev, rom = V.tokens(L['dev']), V.tokens(L['roman'])
        if len(dev) != len(rom):
            raise ValueError('%s: DEV %d vs ROM %d tokens' % (L['id'], len(dev), len(rom)))
        caps = [t for c in L['captions'].split('+') for t in toks if t['line'] == c]
        k, marked = 0, []
        for r in rom:
            key = False
            for j in range(k, len(caps)):
                if re.sub(r'\W', '', caps[j]['roman']).lower() == re.sub(r'\W', '', r).lower():
                    key, k = bool(caps[j]['keyword']), j + 1
                    break
            marked.append(('*' if key else '') + r)
        out[L['id']] = dict(dev=dev, rom=marked, roman=L['roman'], dev_text=L['dev'], delivery=L['delivery'],
                            start_f=L['start_f'], captions=L['captions'])
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
    """Free transcript (no prompt) of a 48 kHz float array: faster-whisper int8 on a 16 kHz numpy array (never a path:
    its PyAV decoder is incompatible here)."""
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


# ------------------------------------------------------------------------------------------------ process
def takes(lid):
    return sorted(glob.glob(os.path.join(RAW, '%s_t*.mp3' % FILE_ID[lid])))


def proc_path(take, speed):
    return os.path.join(RW, 'proc', '%s_%.2f.wav' % (os.path.splitext(os.path.basename(take))[0], speed))


def run_chain(lines, lid, take, speed, force=False):
    out = proc_path(take, speed)
    if force or not os.path.exists(os.path.splitext(out)[0] + '.report.json'):
        L = lines[lid]
        V.process(take, L['dev'], L['rom'], out=out, speed=speed, keep_after=KEEP_AFTER.get(lid, ()))
    rep = json.load(open(os.path.splitext(out)[0] + '.report.json', encoding='utf8'))
    words = json.load(open(os.path.splitext(out)[0] + '.words.json', encoding='utf8'))
    x = V.decode(out)
    return x, words, rep


def cmd_process(force=False):
    lines = load_lines()
    os.makedirs(os.path.join(RW, 'proc'), exist_ok=True)
    tp = os.path.join(RW, 'takes.json')
    tab = json.load(open(tp, encoding='utf8')) if os.path.exists(tp) and not force else {}
    for lid in ORDER_B[:1] + ALL:
        for take in takes(lid):
            for sp in SPEEDS:
                key = '%s@%.2f' % (os.path.basename(take), sp)
                x, words, rep = run_chain(lines, lid, take, sp, force)
                r = runs_abs(x)
                if key not in tab:
                    heard = whisper_text(x)
                    tab[key] = dict(line=lid, take=os.path.basename(take), speed=sp, heard=heard,
                                    cer_small=round(cer(heard, lines[lid]['dev_text']), 3))
                if 'heard_medium' not in tab[key]:
                    hm = whisper_text(x, 'medium')
                    tab[key].update(heard_medium=hm, cer_medium=round(cer(hm, lines[lid]['dev_text']), 3))
                tab[key]['cer_small'] = tab[key].pop('cer', tab[key].get('cer_small'))
                tab[key]['cer'] = min(tab[key]['cer_small'], tab[key]['cer_medium'])      # CER best (Bijli)
                tab[key].update(span=round(r[-1][1] - r[0][0], 3) if r else None, dur=round(len(x) / SR, 3),
                                matched='%d/%d' % (rep['matched'], rep['tokens']), pauses=rep['pauses'],
                                lufs=rep['loudness']['lufs'], tp=rep['loudness']['tp'])
                print(key, tab[key]['span'], tab[key]['cer_small'], tab[key]['cer_medium'], tab[key]['heard'], '|', tab[key]['heard_medium'], flush=True)
                json.dump(tab, open(tp, 'w', encoding='utf8'), ensure_ascii=False, indent=1)
    return tab


def pick(tab, lid):
    """The take of a line: lowest mean CER over the processed speeds; tie (< 0.02) -> the shorter span at 1.08x."""
    rows = {}
    for k, v in tab.items():
        if v['line'] == lid:
            rows.setdefault(v['take'], []).append(v)
    score = {t: (np.mean([r['cer'] for r in rs]), [r['span'] for r in rs if abs(r['speed'] - 1.08) < 1e-6][0])
             for t, rs in rows.items()}
    best = min(score.values(), key=lambda s: s[0])[0]
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
        for k in range(4):                                       # true peak after the gain
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


def cmd_assemble(final=True):
    lines = load_lines()
    tab = json.load(open(os.path.join(RW, 'takes.json'), encoding='utf8'))
    chosen, scores, clips, notes = {}, {}, {}, []
    for lid in ORDER_B[:1] + ALL:
        take, sc = pick(tab, lid)
        chosen[lid], scores[lid] = take, sc
    placed = {}

    def desired(lid, words, s0):
        P = PLAN[lid]
        if 'anchor' in P:                                       # the anchor word's onset on its frame
            i, f = P['anchor']
            return f / FPS - (words[i]['start'] - s0)
        return P['t']

    for ver, order in (('A', ORDER_A), ('B', ORDER_B)):
        prev_end = 0.0
        for lid in order:
            if lid in placed:
                prev_end = placed[lid]['t1']
                continue
            P = PLAN[lid]
            take = os.path.join(RAW, chosen[lid])
            nxt = order[order.index(lid) + 1] if lid != order[-1] else None
            nxt_t = PLAN[nxt].get('t') if nxt else None
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
        notes.append('ladder F4: %s dropped from the VO (%s); best take `%s` processed and kept in proc/'
                     % (lid, PLAN[lid]['why'], chosen[lid]))
    # stems + words
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
    plc = {lid: dict(take=chosen[lid], speed=b['speed'], start=round(b['t0'], 3), end=round(b['t1'], 3),
                     start_f=fr(b['t0']), end_f=fr(b['t1']), planned_f=lines[lid]['start_f'],
                     cer=tab['%s@%.2f' % (chosen[lid], b['speed'])]['cer'],
                     heard=tab['%s@%.2f' % (chosen[lid], b['speed'])]['heard'],
                     matched='%d/%d' % (b['rep']['matched'], b['rep']['tokens']), pauses=b['rep']['pauses'],
                     why=PLAN[lid]['why'])
           for lid, b in placed.items()}
    gaps = []
    for ver in ('A', 'B'):
        o = stems[ver]['order']
        for a, b in zip(o, o[1:]):
            gaps.append(round(plc[b]['start'] - plc[a]['end'], 3))
    doc = dict(placement=plc, notes=notes, scores={k: {t: [round(float(s[0]), 3), s[1]] for t, s in v.items()}
                                                   for k, v in scores.items()},
               stems={v: {k: s[k] for k in ('path', 'words_path', 'master', 'voice', 'voiced_s', 'on_voice')}
                      for v, s in stems.items()}, min_gap=min(gaps))
    json.dump(doc, open(os.path.join(RW, 'placement.json'), 'w', encoding='utf8'), ensure_ascii=False, indent=1)
    plot_timeline(stems['A'], plc, os.path.join(RW, 'timeline.png'))
    if final:
        save_final(stems)
    write_md(lines, plc, stems, notes, scores, tab, doc)
    print(json.dumps(dict(notes=notes, min_gap=doc['min_gap'],
                          A=doc['stems']['A'], B=doc['stems']['B']), ensure_ascii=False, indent=1, default=str))
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
    x, _ = V.decode(st['path']), None
    W, H = 2048, 300
    im = Image.new('RGB', (W, H), (14, 10, 8))
    d = ImageDraw.Draw(im)
    spp = len(x) / W
    for i in range(W):
        seg = x[int(i * spp):int((i + 1) * spp)]
        a = float(np.abs(seg).max()) if len(seg) else 0.0
        d.line([(i, 150 - a * 120), (i, 150 + a * 120)], fill=(255, 181, 71))
    for k in range(0, NF + 1, 16):
        xx = int(k / NF * W)
        d.line([(xx, 270 if k % 64 else 250), (xx, 300)], fill=(120, 110, 130))
    for lid, p in plc.items():
        if lid == 'V1B':
            continue
        a, b = int(p['start'] / DUR * W), int(p['end'] / DUR * W)
        d.rectangle([a, 20, b, 34], outline=(80, 230, 255))
        d.text((a + 2, 4), '%s f%d' % (lid, round(p['start_f'])), fill=(255, 243, 230))
    for w in st['words']:
        xx = int(w['start'] / DUR * W)
        d.line([(xx, 40), (xx, 60)], fill=(242, 49, 43) if w['keyword'] else (200, 200, 200))
    im.save(path)


# ------------------------------------------------------------------------------------------------ report
PICTURE = {   # SHOTS / SCRIPT picture events tied to a VO word: (line, token index, planned frame, event)
    'V1': [(2, 16, '`Pencil.` slam (HA key)')],
    'V1B': [(1, 32, '`khatam?` slam (HB key)')],
    'V2': [(0, 70, 'L2 snake in'), (5, 134, 'L3 snake in ("toh")')],
    'V3': [(0, 198, 'L4 snake in'), (3, 262, 'L5 `SIRF` in'), (4, 268, '`andaza.` glyph rise')],
    'V4': [(0, 320, 'PLAY key + `Play.` slam'), (1, 328, '`Galat!` slam + STOP key (STOP was f336)'),
           (2, 336, '`Phir se.` slam + REW key + motor (REW was f340)')],
    'V5': [(0, 384, '2nd PLAY key + cut to S7 + `Mil gaya!` slam'), (2, 420, 'L8 `Aur phir...` in')],
    'V6': [(0, 448, '`CASSETTE` rise', 'stay'), (1, 464, '`phans gayi!` SLAM + D7 (re-hook)', 'stay')],
    'V7': [(0, 514, 'L10 snake in')],
    'V8': [(0, 588, 'L11 snake in')],
    'V9': [(0, 640, 'playhead back + `Peeche.`'), (1, 648, 'playhead fwd + `Aage.`'),
           (2, 664, 'playhead onto CUT + `Yahan.`')],
    'V10': [(0, 706, 'L13 snake in')],
    'V11': [(0, 768, 'L14 caps (payoff hit f768)', 'stay'), (3, 800, 'pencil snaps to the cut + `Pencil.` key rise')],
    'V12': [(0, 816, 'L15 tag in'), (2, 816, '`cassette` inline key')],
    'V13': [(0, 935, 'outro question text lands (card f896 + t_q 1.3 s)', 'stay')],
}


def write_md(lines, plc, stems, notes, scores, tab, doc):
    A_, B_ = stems['A'], stems['B']
    W = lambda ws, lid: [w for w in ws if w['line'] == lid]  # noqa: E731
    o = ['# VO_TIMING · Pencil Se Rewind (@jawad_mp4)', '',
         '2026-10-11, sound-designer + music-supervisor, `pipeline/jawad_reels/pencil_se_rewind_vo.py assemble` '
         '(measured). Voice: Higgsfield preset Vlad, `elevenlabs_v4`, the paid takes in '
         '`brand_reels/assets/pencil_se_rewind/vo_raw/` (none regenerated). Chain `vo_chain.py` per vo_config: trim to '
         '40 ms, pauses capped 0.45 s (0.9 s after the dramatic beats V1 "button?" and V11 "tool?"), rubberband '
         '1.06-1.10x (formant preserved; the gentlest speed that fits its slot), HPF 70 Hz, de-ess, 2.5:1 compression, '
         'loudnorm -16 LUFS / -2 dBTP; word timings faster-whisper small (DEV prompt) aligned to the DEV tokens, '
         'snapped to the voiced onsets. LEAD_DECISIONS 3: picture beats move to the VO (section 3).', '']
    for ver, s in (('A', A_), ('B', B_)):
        m = s['master']['post']
        o.append('- **Stem %s** `%s`: %d samples (%.3f s) at 48000 Hz, %.2f LUFS integrated, %.2f dBTP, LRA %.1f LU, '
                 'VO %.3f-%.3f s, %.2f s voiced, %d words (%d keywords), %d %% of word starts on voice; gain %+.2f dB, '
                 'limiter %s.' % (ver, os.path.relpath(s['path'], REPO), NSAMP, DUR, m['lufs'], m['tp'], m['lra'],
                                  s['voice'][0], s['voice'][1], s['voiced_s'], len(s['words']),
                                  sum(w['keyword'] for w in s['words']), round(100 * s['on_voice']),
                                  s['master']['gain_db'], 'on' if s['master']['limiter'] else 'off'))
    o += ['- Words: `workspace/jawad_reels/pencil_se_rewind/vo/words.json` (A) / `words_B.json` (B), reel time, '
          'snake_captions format (+ line, i, dev, heard, ok, start_f, end_f). Copies (FLAC 24-bit + json): '
          '`brand_reels/assets/pencil_se_rewind/vo_final/pencil_se_rewind_vo_{A,B}.flac` / `.words.json`.',
          '- Minimum gap between lines: %.3f s (rule >= %.2f s).' % (doc['min_gap'], GAP_MIN), '',
          '## 1. Line timing (hook A order; V1B = hook B only)', '',
          '| line | take | speed | start → end (s) | frames | planned f | Δ f | words (reel s) | CER | aligned |',
          '|---|---|---|---|---|---|---|---|---|---|']
    for lid in ['V1', 'V1B'] + ORDER_A[1:]:
        p = plc[lid]
        ws = W(B_['words'] if lid == 'V1B' else A_['words'], lid)
        wtxt = ' '.join('%s%s %.2f' % ('**' if w['keyword'] else '', w['word'] + ('**' if w['keyword'] else ''),
                                       w['start']) for w in ws)
        o.append('| %s | `%s` | %.2f | %.3f → %.3f | f%.1f-f%.1f | f%d | %+.1f | %s | %.3f | %s |'
                 % (lid, p['take'], p['speed'], p['start'], p['end'], p['start_f'], p['end_f'], p['planned_f'],
                    p['start_f'] - p['planned_f'], wtxt, p['cer'], p['matched']))
    o += ['', '## 2. Word frames (stem A; f = reel frame of the word onset, 30 fps)', '',
          '| line | word | start s | end s | start f | end f | keyword | heard |', '|---|---|---|---|---|---|---|---|']
    for lid in ['V1', 'V1B'] + ORDER_A[1:]:
        for w in W(B_['words'] if lid == 'V1B' else A_['words'], lid):
            o.append('| %s | %s | %.3f | %.3f | %.1f | %.1f | %s | %s |' % (lid, w['word'], w['start'], w['end'],
                                                                         w['start_f'], w['end_f'],
                                                                         'yes' if w['keyword'] else '', w['heard']))
    o += ['', '## 3. Picture beats that move to the VO (proposed frames for the motion designer)', '',
          'LEAD_DECISIONS 3: the picture follows the measured VO. Proposed frame = the onset frame of the VO word '
          '(rounded down, so the visual leads the word by at most 1 frame). |Δ| <= 2 f: keep the planned frame.', '',
          '| line | word | event (SHOTS / SCRIPT) | planned f | VO onset f | proposed f | Δ f |', '|---|---|---|---|---|---|---|']
    for lid in ['V1', 'V1B'] + ORDER_A[1:]:
        ws = W(B_['words'] if lid == 'V1B' else A_['words'], lid)
        for row in PICTURE.get(lid, []):
            i, f_plan, ev = row[:3]
            if i >= len(ws):
                continue
            on = ws[i]['start_f']
            stay = len(row) > 3
            prop = f_plan if (stay or abs(on - f_plan) <= 2) else int(np.floor(on))
            o.append('| %s | %s | %s | f%d | %.1f | **f%d**%s | %+d |' % (lid, ws[i]['word'], ev, f_plan, on, prop,
                                                                       ' (stays)' if stay else '', prop - f_plan))
    o += ['', 'Structure that does NOT move: f64 splice, f256 D8, f320 PLAY key, f448 eat, f464 re-hook slam, f576 '
          'reveal, f752-f767 drop-out, f768 payoff, f896 D2 razor + profile outro (128 f). Moves inside shots (all on '
          'the measured VO; the sound files already follow them): HA `Pencil.` slam f16 -> f43/f46; S6 STOP key f336 -> '
          'f347 (on "Galat!", music wrong-spot snippet f322-f346), REW key + motor f340 -> f376 (on "Phir se."), '
          '2nd PLAY key + cut to S7 f384 -> f392, `Mil gaya!` slam f395; L8 f420 -> f430; S11 scrub jumps one 8th '
          'later f648 / f656 / f664 / f672 (CUT marker f672; V8 "hain." ends f648; music stutters follow); S13 pencil '
          'snap + `Pencil.` key f800 -> the V11 "Pencil." onset; L15 tag f816 -> the V12 onset, held to the V12 end '
          '(across the razor; the outro question lands f935 and V13 reads it from f930); `Pencil.` slam f43 (0.1 s '
          'before the word, so the word keeps 8 LU over the hit). V9 is not in '
          'the VO (ladder F4): L12 `Peeche. Aage. Peeche. Yahan.` stays text-led on the scrub jumps.']
    o += ['', '## 4. Takes (CER = faster-whisper small, no prompt, on the processed line vs the DEV text; nukta / '
          'candrabindu folded, Latin loan words mapped)', '', '| line | take | mean CER (1.06/1.08/1.10) | span @1.08 s | heard @ placed speed | chosen |',
          '|---|---|---|---|---|---|']
    for lid in ['V1', 'V1B'] + ALL[1:]:
        for t, s in sorted(scores[lid].items()):
            sp = plc[lid]['speed'] if lid in plc else 1.10
            k = '%s@%.2f' % (t, sp)
            o.append('| %s | `%s` | %.3f | %.3f | %s / %s | %s |' % (lid, t, s[0], s[1], tab[k]['heard'],
                                                                      tab[k].get('heard_medium', ''),
                                                                      ('yes' if t == plc[lid]['take'] else '')
                                                                      if lid in plc else 'dropped (F4)'))
    o += ['', '## 5. Notes', ''] + ['- ' + n for n in notes] + [
        '- Rebuild: `cd pipeline/jawad_reels && tools/heavy.sh python3 pencil_se_rewind_vo.py process && '
        'tools/heavy.sh python3 pencil_se_rewind_vo.py assemble` (deterministic; the PLAN table at the top of the '
        'module holds the slots).', '']
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
