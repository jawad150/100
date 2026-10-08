"""vo_tools.py - voiceover takes -> checked, sentence-level line clips for retime.py.

    python3 vo_tools.py split [piece ...]     # needs faster-whisper (pip install faster-whisper soundfile)

Reads vo/script.json and the TTS takes vo/<piece>/<p>.mp3 (one take per paragraph, natural prosody; a paragraph with
"pad" was voiced with that throwaway word after it, because the TTS clips the last word of a take, and the pad clip
is dropped). Each take is
transcribed with word timestamps; it is cut between sentences at the silence gaps that follow sentence-final
punctuation (the largest such gaps, as many as the paragraph has lines), trimmed to 30 ms before the first and
120 ms after the last word, faded (10 / 60 ms) and written as 48 kHz mono float WAVs:
    <WS>/vo/<piece>/<line>.wav  +  <WS>/vo/<piece>/lines.json  {line: {text, dur, file, lufs, heard}}
`heard` is Whisper's re-transcription of the cut clip: read it against `text` (numbers come back as digits).
"""
import json
import os
import re
import subprocess
import sys
import tempfile

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import wsconf  # noqa: E402

WS = wsconf.workspace()
SR = 48000
PRE, POST = 0.03, 0.12            # s kept before the first / after the last word of a line
_MODEL = {}


def _model():
    if 'm' not in _MODEL:
        from faster_whisper import WhisperModel
        _MODEL['m'] = WhisperModel('small.en', device='cpu', compute_type='int8', cpu_threads=2)
    return _MODEL['m']


def load(path, sr=SR):
    """Any audio file -> float32 mono at sr (ffmpeg)."""
    with tempfile.TemporaryDirectory() as td:
        w = os.path.join(td, 'a.wav')
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', path, '-ac', '1', '-ar', str(sr), '-c:a', 'pcm_f32le', w],
                       check=True)
        import soundfile as sf
        x, _ = sf.read(w, dtype='float32')
    return x


def words(x, sr=SR):
    """Whisper word timings [(start, end, word)] for a mono clip."""
    import scipy.signal as ss  # noqa: E402
    x16 = ss.resample_poly(x, 1, sr // 16000).astype(np.float32)
    segs, _ = _model().transcribe(x16, language='en', word_timestamps=True, beam_size=5)
    return [(w.start, w.end, w.word.strip()) for s in segs for w in s.words]


def lufs(x, sr=SR):
    try:
        import pyloudnorm as pyln
        return float(pyln.Meter(sr).integrated_loudness(x.astype(np.float64)))
    except Exception:
        return float(10 * np.log10(np.mean(x.astype(np.float64) ** 2) + 1e-12) - 0.691)


def _fade(y, a=0.010, b=0.060, sr=SR):
    y = y.copy()
    na, nb = int(a * sr), int(b * sr)
    y[:na] *= np.linspace(0, 1, na, dtype=np.float32)
    y[-nb:] *= np.linspace(1, 0, nb, dtype=np.float32)
    return y


_NUM = {'0': 'nought', '4': 'four', '15': 'fifteen', '52': 'fifty'}


def _tok(w):
    w = re.sub(r'[^a-z0-9]', '', w.lower())
    return _NUM.get(w, w)


def _env_db(x, sr=SR, hop=0.01):
    n = int(hop * sr)
    m = len(x) // n
    rms = np.sqrt(np.mean(x[:m * n].reshape(m, n).astype(np.float64) ** 2, 1) + 1e-12)
    return 20 * np.log10(rms), hop


def split_take(x, texts, sr=SR):
    """Cut a paragraph take into one clip per expected sentence (texts). Whisper finds the last word of each
    sentence; the cut goes in the longest real silence (RMS envelope) between that word's start and the end of the
    next word, because Whisper's word times smear pauses into neighbouring words and squash spoken numbers."""
    ws = words(x, sr)
    if not ws:
        raise ValueError('no speech found')
    env, hop = _env_db(x, sr)
    thr = max(env.max() - 38.0, -55.0)
    loud = np.where(env > thr)[0]
    t_on, t_off = loud[0] * hop, (loud[-1] + 1) * hop
    toks = [_tok(w) for _, _, w in ws]
    cuts, i0 = [], 0
    for text in texts[:-1]:
        end = _tok(text.split()[-1])
        idx = next((i for i in range(i0, len(ws) - 1) if toks[i] == end or
                    (len(end) > 4 and toks[i].startswith(end[:-1]))), None)
        if idx is None:      # proportional fallback by word count
            frac = sum(len(t.split()) for t in texts[:len(cuts) + 1]) / sum(len(t.split()) for t in texts)
            idx = min(len(ws) - 2, max(i0, int(round(frac * len(ws))) - 1))
        a, b = int(ws[idx][0] / hop), int(min(ws[idx + 1][1], len(x) / sr) / hop)
        quiet = env[a:b] <= thr + 6.0
        best, run, start = (0, a), 0, a
        for k, q in enumerate(quiet):
            if q:
                if run == 0:
                    start = a + k
                run += 1
                if run > best[0]:
                    best = (run, start)
            else:
                run = 0
        r0 = best[1] * hop
        r1 = r0 + best[0] * hop
        cuts.append((r0, r1))
        i0 = idx + 1
    clips = []
    starts = [max(0.0, t_on - PRE)] + [max(r0, r1 - PRE) for r0, r1 in cuts]
    ends = [min(r1, r0 + 0.08) for r0, r1 in cuts] + [min(len(x) / sr, t_off + POST)]
    for k, (t0, t1) in enumerate(zip(starts, ends)):
        seg = x[int(t0 * sr):int(t1 * sr)]
        # end 0.15 s after the last frame within 24 dB of the line's loudest 20 ms (drops room tone / breaths that
        # sit around -30 dB after the last word, which would otherwise hold the line open and the SFX ducked)
        e20, h20 = _env_db(seg, sr, 0.02)
        speech = np.where(e20 > e20.max() - 24.0)[0]
        n_end = min(len(seg), int(((speech[-1] + 1) * h20 + 0.15) * sr)) if len(speech) else len(seg)
        # and start 0.06 s before the first such frame (no dead air / breath before the first word)
        n_beg = max(0, int((speech[0] * h20 - 0.06) * sr)) if len(speech) else 0
        y = _fade(seg[n_beg:n_end], 0.010, 0.04)
        clips.append((y, ''))
    return clips


def split(pieces=None):
    import soundfile as sf
    script = json.load(open(os.path.join(HERE, 'vo', 'script.json')))
    for piece, paras in script['pieces'].items():
        if pieces and piece not in pieces:
            continue
        out = os.path.join(WS, 'vo', piece)
        os.makedirs(out, exist_ok=True)
        meta = {}
        for para in paras:
            x = load(os.path.join(HERE, 'vo', piece, para['p'] + '.mp3'))
            texts = para.get('texts') or [s.strip() for s in re.split(r'(?<=[.?!])\s+', para['say'].replace('... ', '.... '))
                                          if s.strip()]
            texts = [t.replace('....', '...') for t in texts]
            if len(texts) != len(para['lines']):
                raise ValueError('%s %s: %d sentences for %d lines' % (piece, para['p'], len(texts), len(para['lines'])))
            n20 = int(0.02 * SR)
            end_db = 20 * np.log10(np.sqrt(np.mean(x[-n20:] ** 2)) / (np.abs(x).max() + 1e-9) + 1e-9)
            if end_db > -35 and not para.get('pad'):     # the take stops mid-sound: its last word is clipped
                print('   !! %s %s: take ends %.0f dB below peak (clipped last word): re-voice with "pad"'
                      % (piece, para['p'], end_db))
            clips = split_take(x, texts + ([para['pad']] if para.get('pad') else []), SR)[:len(texts)]
            for k, (line, (y, _)) in enumerate(zip(para['lines'], clips)):
                p = os.path.join(out, line + '.wav')
                sf.write(p, y, SR, subtype='FLOAT')
                heard = ' '.join(w for _, _, w in words(y))
                meta[line] = dict(text=texts[k], para=para['p'],
                                  dur=round(len(y) / SR, 3), file=p, lufs=round(lufs(y), 2), heard=heard)
                print('%-6s %-18s %5.2fs %6.1f LUFS | %s' % (piece, line, len(y) / SR, meta[line]['lufs'], heard),
                      flush=True)
        json.dump(meta, open(os.path.join(out, 'lines.json'), 'w'), indent=1)
        print('->', os.path.join(out, 'lines.json'))


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'split':
        split(sys.argv[2:] or None)
    else:
        print(__doc__)
