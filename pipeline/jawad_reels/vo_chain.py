"""vo_chain.py - Jawad's VO chain: a downloaded TTS take -> broadcast-ready VO stem + word timings for the captions.
Follows pipeline/jawad_reels/vo_config.json "post_processing". Standalone (numpy, scipy, ffmpeg, faster-whisper; no
toolkit imports), so it can run isolated on downloaded files:

    nice -n 10 python3 -I vo_chain.py process <take.mp3> --dev <dev.txt> --rom <rom.txt> [--speed auto|1.08]
                                              [--keep-after 12,30] [--out <WS>/vo/<name>.wav] [--realign]
    nice -n 10 python3 -I vo_chain.py align <final.wav> --dev <dev.txt> --rom <rom.txt> -o words.json
    nice -n 10 python3 -I vo_chain.py selftest        # the Vlad v4 DEV take + texts.py DEV / ROM

PROCESS (in this order; every step is measured into <out>.report.json)
    1. decode to 48 kHz mono float; find voiced runs (20 ms RMS, adaptive threshold: max(noise floor + 10 dB,
       peak - 45 dB), gaps < 80 ms closed).
    2. trim leading / trailing silence to 40 ms (the loop rule: the last word ends 40 ms before the cut).
    3. cap internal pauses at 0.45 s (the middle of the silence is removed, 10 ms crossfades), EXCEPT dramatic
       beats: pauses after tokens ending in '...', '\u2026' or a dash, or after the token indices in keep_after, are
       capped at 0.9 s instead. Finding them needs word times on the raw take: one faster-whisper pass.
    4. pitch-preserving time-stretch (ffmpeg rubberband, formant preserved; atempo fallback): speed='auto'
       lands ~160 wpm, clamped to 1.00-1.10x (vo_config: 1.06-1.10x for reels).
    5. high-pass 70 Hz, gentle de-ess, light compression (2.5:1 at -21 dB), two-pass loudnorm to -16 LUFS
       integrated with a -2 dBTP limiter; 48 kHz 24-bit mono WAV.
    6. word timings: faster-whisper (language 'hi', word_timestamps, the DEV text as initial prompt) -> aligned
       to the DEV tokens (Devanagari DP alignment with 1:2 / 2:1 merges) -> the ROM token of the same index
       (the hinglish-scriptwriter keeps DEV and ROM in the same order and count) -> <out>.words.json:
       [{"word": "Bhai,", "start": 0.04, "end": 0.33, "keyword": false, "dev": "\u092d\u093e\u0908,", "heard": "...",
         "ok": true}, ...] - exactly what snake_captions.load_words reads ('*word' in the ROM list = keyword).
       Default: the raw-take timings are mapped through the edit (trim, pause cuts, stretch: exact), then
       snapped to the final take's voiced onsets / offsets (whisper glues pauses to the next word; a start on
       a < 0.1 s voiced tail of the PREVIOUS word's run before a pause moves past the pause, while a word that
       starts on its own short first syllable stays: tail_fragment(); the first word after , . ? ! ...
       starts on its voiced onset: snap_to_voice); --realign transcribes the final take again (the vo_config
       wording), keeps the start nearer a voiced onset where the two passes differ by > 0.1 s (reconcile) and
       the report gives the mean AND max disagreement, the words over 0.1 s and which ones it took over, plus
       realign.independent: the final starts against the re-transcription BEFORE snapping (the snapped pass
       shares the snap rules, so only the raw one can expose a snap mistake).
Python API: process(path, dev_tokens, rom_tokens, out=None, speed='auto', keep_after=(), realign=False) -> report;
    align(path, dev_tokens, rom_tokens, snap=True) -> words; snap_to_voice(words, runs); tail_fragment(words, q, runs)
    -> run index or -1; tokens(text) -> list; load_texts(texts_py) -> TEXTS (ast, no exec).
"""
import ast
import difflib
import json
import math
import os
import re
import subprocess
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, '..', '..'))
SR = 48000
CFG = os.path.join(HERE, 'vo_config.json')
WHISPER = os.path.join(REPO, 'workspace', 'brand_reels', 'tts', 'models', 'whisper')
THREADS = int(os.environ.get('JAWAD_VO_THREADS', '2'))


def ws():
    """Workspace folder (project.json "workspace", default workspace/jawad_reels)."""
    try:
        w = json.load(open(os.path.join(HERE, 'project.json'))).get('workspace', 'workspace/jawad_reels')
    except (OSError, ValueError):
        w = 'workspace/jawad_reels'
    return os.path.join(REPO, w)


# =============================================================================================== audio io
def decode(path, sr=SR):
    """Any audio file -> mono float32 at sr (ffmpeg)."""
    p = subprocess.run(['ffmpeg', '-hide_banner', '-loglevel', 'error', '-i', path, '-ac', '1', '-ar', str(sr),
                        '-f', 'f32le', '-'], capture_output=True, check=True)
    return np.frombuffer(p.stdout, np.float32).copy()


def write_wav(path, x, sr=SR, fmt='pcm_s24le'):
    os.makedirs(os.path.dirname(os.path.abspath(path)) or '.', exist_ok=True)
    subprocess.run(['ffmpeg', '-hide_banner', '-loglevel', 'error', '-y', '-f', 'f32le', '-ar', str(sr), '-ac', '1',
                    '-i', '-', '-c:a', fmt, path], input=np.asarray(x, np.float32).tobytes(), check=True)
    return path


def has_filter(name):
    out = subprocess.run(['ffmpeg', '-hide_banner', '-filters'], capture_output=True, text=True).stdout
    return any(line.split()[1:2] == [name] for line in out.splitlines() if len(line.split()) > 1)


def ebur128(path):
    """Integrated loudness (LUFS), loudness range (LU) and true peak (dBTP) of a file (ffmpeg ebur128)."""
    err = subprocess.run(['ffmpeg', '-hide_banner', '-nostats', '-i', path, '-af', 'ebur128=peak=true', '-f', 'null',
                          '-'], capture_output=True, text=True).stderr
    tail = err[err.rfind('Summary:'):]
    g = lambda pat: float(re.search(pat, tail, re.S).group(1))
    return dict(lufs=g(r'I:\s*(-?[\d.]+) LUFS'), lra=g(r'LRA:\s*(-?[\d.]+) LU'), tp=g(r'Peak:\s*(-?[\d.]+) dBFS'))


# =============================================================================================== silences
def voiced_runs(x, sr=SR, win=0.02, hop=0.01, close=0.08, min_run=0.03):
    """[(t0, t1)] voiced runs; adaptive threshold max(floor + 10 dB, peak - 45 dB)."""
    n, h = int(win * sr), int(hop * sr)
    if len(x) < n:
        return []
    frames = np.lib.stride_tricks.sliding_window_view(x, n)[::h]
    db = 10 * np.log10(np.mean(frames.astype(np.float64) ** 2, axis=1) + 1e-12)
    thr = max(float(np.percentile(db, 10)) + 10.0, float(db.max()) - 45.0)
    v = db > thr
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


def edit_pauses(x, runs, cap=0.45, keep_cap=0.9, keep=(), pad=0.04, sr=SR, xfade=0.01):
    """Trim lead / tail to `pad` and cap internal pauses (pauses overlapping a `keep` window get keep_cap).
    Returns (y, segments [(src0, src1, dst0)], pauses [dict(at, was, now, dramatic)])."""
    if not runs:
        return x.copy(), [(0.0, len(x) / sr, 0.0)], []
    start = max(0.0, runs[0][0] - pad)
    end = min(len(x) / sr, runs[-1][1] + pad)
    keeps = []                                     # source [start, end) to keep
    cur0 = start
    pauses = []
    for (a0, a1), (b0, b1) in zip(runs, runs[1:]):
        gap = b0 - a1
        dram = any(a1 - 0.25 <= k <= b0 + 0.25 for k in keep)
        lim = keep_cap if dram else cap
        if gap > lim:
            keeps.append((cur0, a1 + lim / 2))
            cur0 = b0 - lim / 2
            pauses.append(dict(at=round(a1, 3), was=round(gap, 3), now=round(lim, 3), dramatic=dram))
        elif dram:
            pauses.append(dict(at=round(a1, 3), was=round(gap, 3), now=round(gap, 3), dramatic=True))
    keeps.append((cur0, end))
    nx = int(xfade * sr)
    out, segs, dst = [], [], 0.0
    for i, (s0, s1) in enumerate(keeps):
        seg = x[int(round(s0 * sr)):int(round(s1 * sr))].astype(np.float32).copy()
        if i > 0 and nx > 0 and len(seg) > 2 * nx and len(out[-1]) > 2 * nx:
            r = 0.5 - 0.5 * np.cos(np.linspace(0, math.pi, nx, dtype=np.float32))
            prev = out[-1]
            prev[-nx:] = prev[-nx:] * (1 - r) + seg[:nx] * r
            seg = seg[nx:]
            segs.append((s0 + nx / sr, s1, dst))
        else:
            segs.append((s0, s1, dst))
        out.append(seg)
        dst += len(seg) / sr
    return np.concatenate(out), segs, pauses


def map_time(t, segs, speed=1.0):
    """Raw-take time -> final time through the edit (trim, pause cuts) and the stretch."""
    for s0, s1, d0 in segs:
        if t < s0:
            return d0 / speed                       # inside a removed silence: snap to the next kept piece
        if t <= s1:
            return (d0 + t - s0) / speed
    s0, s1, d0 = segs[-1]
    return (d0 + s1 - s0) / speed


# =============================================================================================== ffmpeg chain
def stretch_and_master(x, speed, lufs=-16.0, tp=-2.0, sr=SR):
    """Rubberband (pitch- and formant-preserving; atempo fallback) + HPF 70 Hz + de-ess + compression + two-pass
    loudnorm (+ limiter). Returns (y, info)."""
    rb = has_filter('rubberband')
    f = ['aresample=%d' % sr]
    if abs(speed - 1.0) > 1e-3:
        f.append('rubberband=tempo=%.4f:pitchq=quality:window=standard:formant=preserved' % speed if rb
                 else 'atempo=%.4f' % speed)
    f += ['highpass=f=70:poles=2', 'deesser=i=0.30:m=0.5:f=0.5:s=o',
          'acompressor=threshold=-21dB:ratio=2.5:attack=8:release=140:knee=4:makeup=1.5']
    pre = ','.join(f)
    raw = np.asarray(x, np.float32).tobytes()
    base = ['ffmpeg', '-hide_banner', '-nostats', '-f', 'f32le', '-ar', str(sr), '-ac', '1', '-i', '-']
    meas = subprocess.run(base + ['-af', pre + ',loudnorm=I=%s:TP=%s:LRA=11:print_format=json' % (lufs, tp),
                                  '-f', 'null', '-'], input=raw, capture_output=True).stderr.decode()
    j = json.loads(meas[meas.rindex('{'): meas.rindex('}') + 1])
    ln = ('loudnorm=I=%s:TP=%s:LRA=11:measured_I=%s:measured_TP=%s:measured_LRA=%s:measured_thresh=%s:offset=%s:'
          'linear=true,alimiter=limit=%.4f:attack=3:release=50:level=false,aresample=%d'
          % (lufs, tp, j['input_i'], j['input_tp'], j['input_lra'], j['input_thresh'], j['target_offset'],
             10 ** ((tp - 0.3) / 20), sr))
    p = subprocess.run(base + ['-af', pre + ',' + ln, '-f', 'f32le', '-ac', '1', '-'], input=raw, capture_output=True,
                       check=True)
    y = np.frombuffer(p.stdout, np.float32).copy()
    return y, dict(stretch='rubberband' if rb else 'atempo', speed=round(speed, 4), pre_lufs=float(j['input_i']),
                   chain=pre)


# =============================================================================================== text + alignment
PUNCT = re.compile(r'[\s,.!?;:\u0964\u0965\u2026"\'()\[\]\u2014\u2013-]+')
NUKTA = {'\u0958': '\u0915', '\u0959': '\u0916', '\u095a': '\u0917', '\u095b': '\u091c', '\u095c': '\u0921',
         '\u095d': '\u0922', '\u095e': '\u092b', '\u095f': '\u092f', '\u093c': '', '\u0901': '\u0902'}
DEV2LAT = {'\u0905': 'a', '\u0906': 'aa', '\u0907': 'i', '\u0908': 'i', '\u0909': 'u', '\u090a': 'u', '\u090f': 'e',
           '\u0910': 'ai', '\u0913': 'o', '\u0914': 'au', '\u0915': 'k', '\u0916': 'kh', '\u0917': 'g', '\u0918': 'gh',
           '\u091a': 'ch', '\u091b': 'chh', '\u091c': 'j', '\u091d': 'jh', '\u091f': 't', '\u0920': 'th', '\u0921': 'd',
           '\u0922': 'dh', '\u0923': 'n', '\u0924': 't', '\u0925': 'th', '\u0926': 'd', '\u0927': 'dh', '\u0928': 'n',
           '\u092a': 'p', '\u092b': 'f', '\u092c': 'b', '\u092d': 'bh', '\u092e': 'm', '\u092f': 'y', '\u0930': 'r',
           '\u0932': 'l', '\u0935': 'w', '\u0936': 'sh', '\u0937': 'sh', '\u0938': 's', '\u0939': 'h', '\u093e': 'a',
           '\u093f': 'i', '\u0940': 'i', '\u0941': 'u', '\u0942': 'u', '\u0947': 'e', '\u0948': 'ai', '\u094b': 'o',
           '\u094c': 'au', '\u0902': 'n', '\u094d': '', '\u0911': 'o', '\u0949': 'o', '\u0943': 'ri'}


def tokens(text):
    """Script text -> whitespace tokens (punctuation kept on the token, empty tokens dropped)."""
    if isinstance(text, (list, tuple)):
        text = ' '.join(text)
    return [w for w in text.split() if PUNCT.sub('', w)]


def norm_dev(w):
    w = PUNCT.sub('', w)
    return ''.join(NUKTA.get(ch, ch) for ch in w)


def skel(w):
    lat = ''.join(DEV2LAT.get(ch, ch) for ch in norm_dev(w)).lower()
    lat = re.sub(r'(.)\1+', r'\1', lat)
    return re.sub(r'[aeiouyh]', '', lat) or lat[:2]


def sim(a, b):
    """Similarity of two Devanagari words in about [-1, 3] (3 = identical after normalising)."""
    na, nb = norm_dev(a), norm_dev(b)
    if not na or not nb:
        return -1.0
    if na == nb:
        return 3.0
    r1 = difflib.SequenceMatcher(None, na, nb).ratio()
    r2 = difflib.SequenceMatcher(None, skel(a), skel(b)).ratio()
    return 2.2 * max(r1, r2) - 1.0


def _whisper_words(path_or_x, prompt=None, model='small'):
    from faster_whisper import WhisperModel
    mpath = os.path.join(WHISPER, 'faster-whisper-%s' % model)
    m = WhisperModel(mpath if os.path.isdir(mpath) else model, device='cpu', compute_type='int8', cpu_threads=THREADS)
    x = decode(path_or_x, 16000) if isinstance(path_or_x, str) else path_or_x
    segs, info = m.transcribe(x, language='hi', word_timestamps=True, beam_size=5, initial_prompt=prompt,
                              condition_on_previous_text=False, vad_filter=False)
    out = []
    for s in segs:
        for w in s.words or []:
            if norm_dev(w.word):
                out.append(dict(w=w.word.strip(), s=float(w.start), e=float(w.end), p=float(w.probability)))
    return out


def align_tokens(dev, heard, gap=-0.6):
    """DP alignment of script tokens (Devanagari) to heard words with 1:1, 1:2 and 2:1 moves -> per-token
    (start, end, heard text, score) or None."""
    n, m = len(dev), len(heard)
    NEG = -1e9
    dp = np.full((n + 1, m + 1), NEG)
    bt = np.zeros((n + 1, m + 1), np.int8)
    dp[0, :] = np.arange(m + 1) * gap
    dp[:, 0] = np.arange(n + 1) * gap
    bt[0, 1:], bt[1:, 0] = 2, 1
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            c = [dp[i - 1, j - 1] + sim(dev[i - 1], heard[j - 1]['w']), dp[i - 1, j] + gap, dp[i, j - 1] + gap, NEG, NEG]
            if j >= 2:
                c[3] = dp[i - 1, j - 2] + sim(dev[i - 1], heard[j - 2]['w'] + heard[j - 1]['w']) - 0.3
            if i >= 2:
                c[4] = dp[i - 2, j - 1] + sim(dev[i - 2] + dev[i - 1], heard[j - 1]['w']) - 0.3
            k = int(np.argmax(c))
            dp[i, j], bt[i, j] = c[k], k
    res = [None] * n
    i, j = n, m
    while i > 0 or j > 0:
        k = bt[i, j] if i > 0 and j > 0 else (1 if j == 0 else 2)
        if k == 0:
            h = heard[j - 1]
            res[i - 1] = (h['s'], h['e'], h['w'], sim(dev[i - 1], h['w']))
            i, j = i - 1, j - 1
        elif k == 1:
            i -= 1
        elif k == 2:
            j -= 1
        elif k == 3:
            a, b = heard[j - 2], heard[j - 1]
            res[i - 1] = (a['s'], b['e'], a['w'] + b['w'], sim(dev[i - 1], a['w'] + b['w']))
            i, j = i - 1, j - 2
        else:
            h = heard[j - 1]
            la, lb = len(norm_dev(dev[i - 2])), len(norm_dev(dev[i - 1]))
            mid = h['s'] + (h['e'] - h['s']) * la / max(1, la + lb)
            sc = sim(dev[i - 2] + dev[i - 1], h['w'])
            res[i - 2] = (h['s'], mid, h['w'], sc)
            res[i - 1] = (mid, h['e'], h['w'], sc)
            i, j = i - 2, j - 1
    return res


def words_json(dev, rom, res, keyword_marks=True):
    """Aligned results -> the caption word list (ROM text, keyword flags from '*'), gaps interpolated, monotone."""
    if len(dev) != len(rom):
        raise ValueError('DEV has %d tokens but ROM has %d: the scriptwriter keeps them 1:1' % (len(dev), len(rom)))
    words = []
    for d, r, x in zip(dev, rom, res):
        key = keyword_marks and r.startswith('*')
        r = r[1:] if key else r
        if x is None:
            words.append(dict(word=r, start=None, end=None, keyword=key, dev=d, heard='', ok=False, score=None))
        else:
            words.append(dict(word=r, start=round(x[0], 3), end=round(x[1], 3), keyword=key, dev=d, heard=x[2],
                              ok=x[3] > 0.3, score=round(float(x[3]), 2)))
    k = 0
    while k < len(words):
        if words[k]['start'] is None:
            a = k
            while k < len(words) and words[k]['start'] is None:
                k += 1
            t0 = words[a - 1]['end'] if a > 0 else 0.0
            t1 = words[k]['start'] if k < len(words) else t0 + 0.3 * (k - a)
            step = (t1 - t0) / (k - a)
            for q in range(a, k):
                words[q]['start'] = round(t0 + step * (q - a), 3)
                words[q]['end'] = round(t0 + step * (q - a + 1), 3)
        else:
            k += 1
    for q in range(1, len(words)):
        words[q]['start'] = max(words[q]['start'], words[q - 1]['start'] + 0.04)
        words[q]['end'] = max(words[q]['end'], words[q]['start'] + 0.05)
    return words


CLAUSE_END = re.compile(r'([,.?!\u0964\u2026;:]|\.\.\.)$')


def _onsets(runs):
    return np.array([r[0] for r in runs]) if runs else np.zeros(0)


def onset_dist(t, runs):
    """Distance (s) from t to the nearest voiced-run onset."""
    on = _onsets(runs)
    return float(np.min(np.abs(on - t))) if len(on) else 9.0


def tail_fragment(words, q, runs, frag=0.10, gap=0.06, inside=0.03):
    """Index of the voiced run whose short tail word q starts on (rule 2 of snap_to_voice), or -1. The start must
    sit INSIDE a run that began >= `inside` s before it and that the previous word overlaps (so it is that
    word's tail), with < `frag` s of voice left, then a pause >= `gap` s, and the next onset before the word's
    end. A word whose own first syllable is a short run (start on its onset) is NOT a tail fragment.
    e.g. tail_fragment([{'start': 15.11, 'end': 15.618}, {'start': 15.618, 'end': 16.05}], 1,
                       [(15.11, 15.69), (15.85, 16.48)]) -> 0"""
    if q <= 0 or not runs:
        return -1
    on = [r[0] for r in runs]
    s, e = words[q]['start'], words[q]['end']
    prev = words[q - 1]
    i = int(np.searchsorted(on, s, side='right')) - 1
    if not 0 <= i < len(runs) - 1:
        return -1
    a, b = runs[i]
    if s <= b and s - a >= inside and b - s < frag and runs[i + 1][0] - b >= gap and runs[i + 1][0] < e - 0.04 \
            and prev['end'] > a + 0.02 and prev['start'] < b:
        return i
    return -1


def snap_to_voice(words, runs, look=0.35, frag=0.10, gap=0.06, clause=0.30, inside=0.03):
    """Whisper puts word edges inside pauses (often a pause is glued to the next word). In place; returns words.
    1. a start that sits in silence moves to the next voiced onset (within `look` s, before the word's end), an
       end in silence back to the previous voiced offset;
    2. tail fragment (tail_fragment()): a start that sits >= `inside` s into a voiced run the previous word
       overlaps, with < `frag` s of voice left and then a pause of >= `gap` s inside the word, belongs to the
       previous word's tail ('Lekin sach': 'sach' started 0.23 s early inside the end of 'Lekin'): it moves to
       the onset after the pause, and the previous word ends at the pause. A word that starts ON its own short
       first syllable ('Accha' = 'A' + closure + 'ccha') is left alone (fix round 2: it used to be moved past
       its own closure and the previous word stretched across the pause);
    3. clause start: after a token ending in , . ? ! ... or the danda the speaker paused, so a start up to
       `clause` s after a voiced onset moves back to that onset."""
    if not runs:
        return words
    on = np.array([r[0] for r in runs])
    off = np.array([r[1] for r in runs])

    def voiced(t):
        i = np.searchsorted(on, t, side='right') - 1
        return i >= 0 and t <= off[i] + 0.02

    for w in words:
        s, e = w['start'], w['end']
        if not voiced(s):
            i = np.searchsorted(on, s)
            if i < len(on) and on[i] - s <= look and on[i] < e - 0.04:
                w['start'] = round(float(on[i]), 3)
        if not voiced(e):
            i = np.searchsorted(off, e) - 1
            if i >= 0 and e - off[i] <= look and off[i] > w['start'] + 0.05:
                w['end'] = round(float(off[i]), 3)
    for q, w in enumerate(words):
        s, e = w['start'], w['end']
        i = tail_fragment(words, q, runs, frag, gap, inside)          # the run whose tail the start sits on
        if i >= 0:
            w['start'] = round(float(on[i + 1]), 3)
            w['snap'] = 'tail fragment'
            if q > 0 and words[q - 1]['start'] < off[i] - 0.05:          # the fragment is the previous word's
                words[q - 1]['end'] = round(float(off[i]), 3)
            continue
        prev = words[q - 1] if q > 0 else None
        if prev is not None and (CLAUSE_END.search(str(prev.get('dev', ''))) or CLAUSE_END.search(str(prev.get('word', '')))):
            j = np.searchsorted(on, s, side='right') - 1
            if j >= 0 and 0 < s - on[j] <= clause and on[j] >= prev['end'] - 0.02:
                w['start'] = round(float(on[j]), 3)
                w['snap'] = 'clause start'
    for q in range(1, len(words)):
        words[q]['start'] = max(words[q]['start'], words[q - 1]['start'] + 0.04)
        words[q]['end'] = max(words[q]['end'], words[q]['start'] + 0.05)
        words[q - 1]['end'] = min(words[q - 1]['end'], max(words[q]['start'], words[q - 1]['start'] + 0.05))
    return words


def reconcile(words, realigned, runs, thr=0.10, margin=0.03):
    """Where the mapped and the re-transcribed start differ by > thr s, keep the one nearer a voiced onset
    (the re-transcribed one only when it is nearer by > margin s). In place; returns the changed indices."""
    changed = []
    for i, (a, b) in enumerate(zip(words, realigned)):
        if abs(a['start'] - b['start']) > thr and onset_dist(b['start'], runs) + margin < onset_dist(a['start'], runs):
            a['start'] = b['start']
            a['snap'] = 'realigned'
            changed.append(i)
    for q in range(1, len(words)):
        words[q]['start'] = max(words[q]['start'], words[q - 1]['start'] + 0.04)
        words[q]['end'] = max(words[q]['end'], words[q]['start'] + 0.05)
        words[q - 1]['end'] = min(words[q - 1]['end'], max(words[q]['start'], words[q - 1]['start'] + 0.05))
    return changed


def align(path_or_x, dev_tokens, rom_tokens, prompt=None, snap=True):
    """Word timings of an audio file (or 16 kHz array) for DEV / ROM token lists -> caption words (snapped to the
    voiced onsets with snap_to_voice when snap and a path is given; snap=False = whisper's own times)."""
    dev, rom = tokens(dev_tokens), tokens(rom_tokens)
    heard = _whisper_words(path_or_x, prompt=prompt or ' '.join(dev))
    words = words_json(dev, rom, align_tokens(dev, heard))
    if snap and isinstance(path_or_x, str):
        snap_to_voice(words, voiced_runs(decode(path_or_x)))
    return words, heard


# =============================================================================================== process
def _dramatic_idx(dev, rom, keep_after=()):
    marks = set(int(i) for i in keep_after)
    for i, (d, r) in enumerate(zip(dev, rom)):
        if re.search(r'(\.\.\.|\u2026|[\u2014\u2013-])$', d) or re.search(r'(\.\.\.|\u2026|[\u2014\u2013-])$', r):
            marks.add(i)
    return sorted(i for i in marks if i < len(dev) - 1)


def process(path, dev_tokens, rom_tokens, out=None, speed='auto', keep_after=(), realign=False, cap=0.45,
            keep_cap=0.9, target_wpm=160.0, lufs=-16.0, tp=-2.0):
    """The whole chain (see module docstring). Returns the report dict; writes <out>.wav, .words.json,
    .report.json."""
    t_start = time.time()
    cfg = json.load(open(CFG)) if os.path.exists(CFG) else {}
    dev, rom = tokens(dev_tokens), tokens(rom_tokens)
    if len(dev) != len(rom):
        raise ValueError('DEV %d tokens vs ROM %d tokens' % (len(dev), len(rom)))
    if out is None:
        out = os.path.join(ws(), 'vo', os.path.splitext(os.path.basename(path))[0] + '_final.wav')
    stem = os.path.splitext(out)[0]
    x = decode(path)
    runs = voiced_runs(x)
    raw_dur = len(x) / SR
    # pass 1: word times on the raw take (finds the dramatic pauses; mapped through the edit afterwards)
    x16 = decode(path, 16000)
    heard1 = _whisper_words(x16, prompt=' '.join(dev))
    res1 = align_tokens(dev, heard1)
    w_raw = words_json(dev, rom, res1)
    keep_times = [w_raw[i]['end'] for i in _dramatic_idx(dev, rom, keep_after)]
    y, segs, pauses = edit_pauses(x, runs, cap=cap, keep_cap=keep_cap, keep=keep_times)
    ed_dur = len(y) / SR
    wpm_before = len(dev) / (ed_dur / 60.0)
    if speed == 'auto':
        speed = float(np.clip(target_wpm / wpm_before, 1.0, 1.10))
    speed = float(speed)
    z, info = stretch_and_master(y, speed, lufs, tp)
    write_wav(out, z)
    loud = ebur128(out)
    fin_dur = len(z) / SR
    # timings: mapped through the edit (exact), optionally re-transcribed on the final take
    words = []
    for w in w_raw:
        d = dict(w)
        d['start'] = round(map_time(w['start'], segs, speed), 3)
        d['end'] = round(max(map_time(w['end'], segs, speed), d['start'] + 0.05), 3)
        words.append(d)
    final_runs = voiced_runs(z)
    snap_to_voice(words, final_runs)
    cmp_ = None
    if realign:
        w2raw, heard2 = align(out, dev, rom, snap=False)
        w2 = [dict(d) for d in w2raw]
        snap_to_voice(w2, final_runs)
        # independent: the re-transcription BEFORE snap_to_voice (the snapped pass shares the snap rules, so it
        # cannot catch a snap mistake by itself)
        raw_d = [abs(a['start'] - b['start']) for a, b in zip(words, w2raw)]
        diffs = [abs(a['start'] - b['start']) for a, b in zip(words, w2)]
        big = [(words[i]['word'], words[i]['start'], w2[i]['start']) for i, d_ in enumerate(diffs) if d_ > 0.1]
        changed = reconcile(words, w2, final_runs)
        diffs2 = [abs(a['start'] - b['start']) for a, b in zip(words, w2)]
        cmp_ = dict(mean_abs_start_diff=round(float(np.mean(diffs)), 3), max=round(float(np.max(diffs)), 3),
                    over_0_1=big, took_realigned=[words[i]['word'] for i in changed],
                    max_after=round(float(np.max(diffs2)), 3), matched_final=sum(w['ok'] for w in w2),
                    independent=dict(mean=round(float(np.mean(raw_d)), 3), median=round(float(np.median(raw_d)), 3),
                                     max=round(float(np.max(raw_d)), 3),
                                     over_0_15=[(words[i]['word'], words[i]['start'], w2raw[i]['start'])
                                                for i, d_ in enumerate(raw_d) if d_ > 0.15],
                                     note='final starts vs the re-transcription before snap_to_voice'))
        json.dump(w2, open(stem + '.words_realigned.json', 'w'), ensure_ascii=False, indent=1)
    json.dump(words, open(stem + '.words.json', 'w'), ensure_ascii=False, indent=1)
    rep = dict(input=os.path.relpath(path, REPO), output=os.path.relpath(out, REPO), sr=SR, format='pcm_s24le mono',
               raw_dur=round(raw_dur, 3), edited_dur=round(ed_dur, 3), final_dur=round(fin_dur, 3),
               lead_trim=round(max(0.0, runs[0][0] - 0.04), 3) if runs else 0.0,
               tail_trim=round(max(0.0, raw_dur - runs[-1][1] - 0.04), 3) if runs else 0.0,
               starts_on_voice=round(float(np.mean([any(a - 0.02 <= w['start'] <= b for a, b in final_runs)
                                                     for w in words])), 3),
               snaps={k: [w['word'] for w in words if w.get('snap') == k]
                      for k in ('tail fragment', 'clause start', 'realigned')},
               pauses=pauses, max_pause_after=round(max([p['now'] for p in pauses] + [0.0]), 3),
               wpm_before=round(wpm_before, 1), wpm_after=round(len(dev) / (fin_dur / 60.0), 1), speed=speed,
               chain=info, loudness=loud, tokens=len(dev), matched=sum(w['ok'] for w in words),
               unmatched=[(w['word'], w['heard']) for w in words if not w['ok']], realign=cmp_,
               config_rules=cfg.get('post_processing', []), seconds=round(time.time() - t_start, 1))
    json.dump(rep, open(stem + '.report.json', 'w'), ensure_ascii=False, indent=1)
    return rep


# =============================================================================================== CLI / selftest
def load_texts(path):
    """TEXTS dict of a texts.py WITHOUT executing it (ast.literal_eval of the assignment)."""
    tree = ast.parse(open(path, encoding='utf8').read())
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(getattr(t, 'id', '') == 'TEXTS' for t in node.targets):
            return ast.literal_eval(node.value)
    raise KeyError('TEXTS not found in %s' % path)


def _read_text(arg):
    return open(arg, encoding='utf8').read() if arg and os.path.exists(arg) else (arg or '')


def _timing_unit_checks():
    """Synthetic checks of snap_to_voice / reconcile (no audio): the QA case 'Lekin sach' (voiced runs
    15.11-15.69 and 15.85-16.48; whisper put 'sach' at 15.618 inside the tail of 'Lekin'), a clause start after
    'hai,', the word-initial short syllable ('Accha': its own 0.08 s first run + closure is NOT a tail
    fragment) and the realign tie-break. -> list of failures."""
    fails = []
    runs = [(14.40, 14.73), (15.11, 15.69), (15.85, 16.48)]
    w = [dict(word='hue!', dev='\u0939\u0941\u090f!', start=14.40, end=14.73),
         dict(word='Lekin', dev='\u0932\u0947\u0915\u093f\u0928', start=15.11, end=15.618),
         dict(word='sach', dev='\u0938\u091a', start=15.618, end=16.055),
         dict(word='bataun?', dev='?', start=16.055, end=16.364)]
    snap_to_voice(w, runs)
    if abs(w[2]['start'] - 15.85) > 1e-6 or abs(w[1]['end'] - 15.69) > 1e-6:
        fails.append('tail fragment rule: sach %.3f (want 15.85), Lekin end %.3f (want 15.69)'
                     % (w[2]['start'], w[1]['end']))
    w2 = [dict(word='hai,', dev='\u0939\u0948,', start=11.936, end=12.064),
          dict(word='aur', dev='\u0914\u0930', start=12.464, end=12.591)]
    snap_to_voice(w2, [(10.13, 12.15), (12.44, 14.73)])
    if abs(w2[1]['start'] - 12.44) > 1e-6:
        fails.append('clause start rule: aur %.3f (want 12.44)' % w2[1]['start'])
    # word-initial short syllable (fix round 2): 'Accha' = run 11.00-11.08 + closure + 11.20-11.50; whisper puts
    # it at 11.00 ON its own onset: not a tail fragment, 'hai,' keeps its end (it used to be stretched to 11.08)
    runs3 = [(9.9, 10.5), (11.00, 11.08), (11.20, 11.50)]
    w3 = [dict(word='hai,', dev='\u0939\u0948,', start=9.9, end=10.5),
          dict(word='Accha', dev='\u0905\u091a\u094d\u091b\u093e', start=11.00, end=11.5)]
    snap_to_voice(w3, runs3)
    if abs(w3[1]['start'] - 11.00) > 1e-6 or abs(w3[0]['end'] - 10.5) > 1e-6 or w3[1].get('snap') == 'tail fragment':
        fails.append('word-initial syllable: Accha %.3f (want 11.00), hai, end %.3f (want 10.50)'
                     % (w3[1]['start'], w3[0]['end']))
    # whisper 20 ms late inside its own first syllable: still not a tail (< `inside` s into the run)
    w4 = [dict(word='hai,', dev='\u0939\u0948,', start=9.9, end=10.5),
          dict(word='Accha', dev='\u0905\u091a\u094d\u091b\u093e', start=11.02, end=11.5)]
    snap_to_voice(w4, runs3)
    if w4[1]['start'] > 11.08 or abs(w4[0]['end'] - 10.5) > 1e-6:
        fails.append('word-initial syllable (late start): Accha %.3f, hai, end %.3f' % (w4[1]['start'], w4[0]['end']))
    # a short run the previous word does NOT overlap is the word's own: rule 2 must not fire, the clause rule
    # puts the start back on that run's onset
    w5 = [dict(word='hai,', dev='\u0939\u0948,', start=9.9, end=10.5),
          dict(word='Accha', dev='\u0905\u091a\u094d\u091b\u093e', start=11.00, end=11.5)]
    snap_to_voice(w5, [(9.9, 10.5), (10.95, 11.08), (11.20, 11.50)])
    if abs(w5[1]['start'] - 10.95) > 1e-6 or abs(w5[0]['end'] - 10.5) > 1e-6:
        fails.append('own first syllable: Accha %.3f (want 10.95), hai, end %.3f' % (w5[1]['start'], w5[0]['end']))
    mapped = [dict(word='Lekin', start=15.11, end=15.6), dict(word='sach', start=15.618, end=16.0)]
    re_ = [dict(word='Lekin', start=14.64, end=15.7), dict(word='sach', start=15.88, end=16.08)]
    ch = reconcile(mapped, re_, runs)
    if ch != [1] or abs(mapped[0]['start'] - 15.11) > 1e-6 or abs(mapped[1]['start'] - 15.88) > 1e-6:
        fails.append('reconcile: took %s, starts %s' % (ch, [m['start'] for m in mapped]))
    return fails


def selftest():
    """The Vlad v4 DEV take + texts.py DEV / ROM (keywords marked on 3 ROM tokens): checks every rule."""
    unit = _timing_unit_checks()
    print('timing unit checks (tail fragment, clause start, reconcile):', 'OK' if not unit else unit)
    take = os.path.join(REPO, 'workspace', 'brand_reels', 'tts', 'hf_dl', 'vlad', 'vlad_v4_r1_DEV.mp3')
    texts = load_texts(os.path.join(REPO, 'workspace', 'brand_reels', 'tts', 'scripts', 'texts.py'))
    dev = tokens(' '.join(texts['DEV']))
    rom = tokens(' '.join(texts['ROM']))
    keys = {'change': True, 'deadline': True, 'raaton': True}
    rom = ['*' + r if PUNCT.sub('', r).lower() in keys else r for r in rom]
    out = os.path.join(ws(), 'vo', 'selftest', 'vlad_v4_r1_DEV_final.wav')
    rep = process(take, dev, rom, out=out, realign=True)
    words = json.load(open(os.path.splitext(out)[0] + '.words.json'))
    fails = list(unit)
    L = rep['loudness']
    if abs(L['lufs'] + 16.0) > 0.6:
        fails.append('loudness %.2f LUFS (want -16)' % L['lufs'])
    if L['tp'] > -1.0:
        fails.append('true peak %.2f dBTP' % L['tp'])
    runs = voiced_runs(decode(out))
    lead, tail = runs[0][0], rep['final_dur'] - runs[-1][1]
    if lead > 0.12 or tail > 0.15:
        fails.append('silence not trimmed (lead %.3f, tail %.3f)' % (lead, tail))
    gaps = [b[0] - a[1] for a, b in zip(runs, runs[1:])]
    long_ = [g for g in gaps if g > 0.45 / rep['speed'] + 0.06]
    dram = [p for p in rep['pauses'] if p['dramatic']]
    if len(long_) > len(dram):
        fails.append('pauses over the cap: %s (dramatic kept: %d)' % ([round(g, 2) for g in long_], len(dram)))
    if not 1.0 <= rep['speed'] <= 1.10:
        fails.append('speed %.3f outside 1.00-1.10' % rep['speed'])
    if rep['matched'] < 0.85 * rep['tokens']:
        fails.append('only %d / %d tokens matched' % (rep['matched'], rep['tokens']))
    if any(b['start'] < a['start'] for a, b in zip(words, words[1:])):
        fails.append('word starts not monotone')
    if rep['starts_on_voice'] < 0.9:
        fails.append('only %.0f %% of word starts sit on voice' % (100 * rep['starts_on_voice']))
    if words[-1]['end'] > rep['final_dur'] + 0.05:
        fails.append('last word ends after the take')
    if rep['realign'] and rep['realign']['mean_abs_start_diff'] > 0.08:
        fails.append('mapped vs re-transcribed timings differ by %.3f s' % rep['realign']['mean_abs_start_diff'])
    # where the two passes disagree, the start we keep must sit on a voiced onset (<= 0.05 s): an independent
    # check of the 'sach' case (it started 0.23 s early, inside the voiced tail of 'Lekin')
    if rep['realign']:
        off_onset = [(wd, round(onset_dist(next(x['start'] for x in words if x['word'] == wd), runs), 3))
                     for wd, _, _ in rep['realign']['over_0_1']]
        bad = [(wd, d_) for wd, d_ in off_onset if d_ > 0.05]
        print('disagreements > 0.1 s (word, mapped, realigned):', rep['realign']['over_0_1'])
        print('kept start -> nearest voiced onset (s):', off_onset)
        if bad:
            fails.append('kept starts off a voiced onset where the passes disagree: %s' % bad)
    tails = [x['word'] for x in words if x.get('snap') == 'tail fragment']
    for q, x in enumerate(words[1:], 1):                         # no start left on a short tail fragment
        if tail_fragment(words, q, runs) >= 0:
            fails.append('%r still starts on the tail of the previous word (%.3f s)' % (x['word'], x['start']))
        if x.get('snap') == 'tail fragment':                     # a moved start: the run it left began before
            st0 = x['start']                                     # it and the previous word now ends at a pause
            if not any(abs(r[0] - st0) < 1e-3 for r in runs) or words[q - 1]['end'] > st0:
                fails.append('%r tail-fragment move not onto an onset after the pause' % x['word'])
    if rep['realign']:
        print('independent (final vs re-transcription before snapping):', rep['realign']['independent'])
    print('snapped:', rep['snaps'], ' tail fragments moved:', tails)
    if sum(w['keyword'] for w in words) != 3:
        fails.append('keyword flags lost')
    print(json.dumps({k: rep[k] for k in ('raw_dur', 'edited_dur', 'final_dur', 'lead_trim', 'tail_trim', 'pauses',
                                          'starts_on_voice', 'snaps',
                                          'wpm_before', 'wpm_after', 'speed', 'loudness', 'matched', 'tokens',
                                          'unmatched', 'realign', 'seconds')}, ensure_ascii=False, indent=1))
    print('stretch:', rep['chain']['stretch'])
    print('->', out)
    print('->', os.path.splitext(out)[0] + '.words.json')
    if fails:
        print('FAIL:', *fails, sep='\n  ')
        return False
    print('vo_chain selftest OK')
    return True


def main(argv=None):
    import argparse
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    sub = ap.add_subparsers(dest='cmd')
    p = sub.add_parser('process')
    p.add_argument('take')
    p.add_argument('--dev', required=True, help='DEV text or a .txt path')
    p.add_argument('--rom', required=True, help='ROM text or a .txt path (*word = keyword)')
    p.add_argument('--out')
    p.add_argument('--speed', default='auto')
    p.add_argument('--keep-after', default='', help='token indices whose following pause is dramatic')
    p.add_argument('--realign', action='store_true')
    a2 = sub.add_parser('align')
    a2.add_argument('audio')
    a2.add_argument('--dev', required=True)
    a2.add_argument('--rom', required=True)
    a2.add_argument('-o', '--out', required=True)
    sub.add_parser('selftest')
    if argv is None:
        argv = sys.argv[1:]
    if argv and argv[0] == '--selftest':
        argv = ['selftest']
    a = ap.parse_args(argv)
    if a.cmd == 'process':
        keep = [int(v) for v in a.keep_after.split(',') if v.strip()]
        rep = process(a.take, _read_text(a.dev), _read_text(a.rom), a.out,
                      a.speed if a.speed == 'auto' else float(a.speed), keep, a.realign)
        print(json.dumps(rep, ensure_ascii=False, indent=1))
        return 0
    if a.cmd == 'align':
        words, _ = align(a.audio, _read_text(a.dev), _read_text(a.rom))
        json.dump(words, open(a.out, 'w'), ensure_ascii=False, indent=1)
        print('->', a.out)
        return 0
    if a.cmd == 'selftest':
        return 0 if selftest() else 1
    ap.print_help()
    return 0


if __name__ == '__main__':
    sys.exit(main())
