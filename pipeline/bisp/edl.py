"""Edit decision list, Roman Urdu captions and the output timeline for the BISP Interoperability reel.

Source = the presenter's 14 iPhone clips (workspace_bisp/src/IMG_*.MOV). Every cut below was chosen from the Whisper
transcripts (small / medium / large-v3) plus a 10 ms energy envelope, and the two splices were checked by
re-transcribing the joined audio:
  * IMG_1689: she says "Wazir-e-Azam Mian Muhammad Nawaz Sharif" (all three Whisper models agree and there is no "sh"
    burst where "Shehbaz" would start). The script says Shehbaz Sharif, so the name is cut (3.76 -> 4.93 s): the line
    becomes "... aur Wazir-e-Azam ke vision ke mutabiq ...", and the lower-third carries the script's correct name.
  * IMG_1731 has several takes. Used: the clean take 13.9-33.9 s ("Is ke") + the last take from "baad" (39.32 s).
  * IMG_1691: the first attempt (2.2-5.2 s) is dropped, the clean take starts at 7.2 s.
  * IMG_1704 is an alternate take of IMG_1705 (ends with an outtake), IMG_1738's second sentence is a flub that
    IMG_1740 repeats cleanly.

Caption tokens: one Roman Urdu word per Whisper token by default; 'word^k' consumes k Whisper tokens (k=0 = no token,
its time is interpolated). Whisper word starts are snapped to the nearest syllable onset in the energy envelope.
"""
import os, json, re
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
WS = os.path.abspath(os.environ.get('BISP_WS', os.path.join(HERE, '..', '..', 'workspace_bisp')))
FPS = 30
W, H = 1080, 1920

# transcripts used for word timings, per clip
TR_FILES = {
    'IMG_1731': 'transcript_large_1731_1691.json', 'IMG_1691': 'transcript_large_1731_1691.json',
    'IMG_1689': 'transcript_large_1689_1672.json', 'IMG_1672': 'transcript_large_1689_1672.json',
}
TR_DEFAULT = 'transcript_medium_ur.json'

# ---------------------------------------------------------------------------------------------------------------
# Segments in story order: (id, clip, src_in, src_out, zoom). zoom = base punch-in for the segment (jump cuts inside
# the same clip alternate it so the cut reads as a deliberate punch, not a glitch).
SEGMENTS = [
    ('hook',      'IMG_1672', 0.40, 6.62, 1.00),
    ('wallets',   'IMG_1677', 1.12, 9.98, 1.00),
    ('anytime',   'IMG_1681', 1.52, 8.18, 1.00),
    ('vision_a',  'IMG_1689', 0.45, 3.76, 1.00),
    ('vision_b',  'IMG_1689', 4.93, 9.02, 1.14),
    ('whatis',    'IMG_1689', 9.20, 11.00, 1.28),
    ('pehle',     'IMG_1691', 7.18, 16.22, 1.00),
    ('ab',        'IMG_1698', 0.55, 9.50, 1.00),
    ('rush',      'IMG_1699', 0.48, 6.05, 1.10),
    ('banks',     'IMG_1705', 0.50, 8.55, 1.00),
    ('faide',     'IMG_1725', 0.90, 15.30, 1.00),
    ('steps_a',   'IMG_1731', 13.86, 33.89, 1.00),
    ('steps_b',   'IMG_1731', 39.32, 44.25, 1.13),
    ('hidayat',   'IMG_1737', 1.55, 9.70, 1.00),
    ('crore',     'IMG_1738', 1.48, 9.55, 1.00),
    ('khwab',     'IMG_1740', 1.80, 11.50, 1.00),
]
END_CARD = 3.4          # seconds of end card after the last segment
SPEED = 1.0             # global playback speed (kept natural)
XFADE_AUDIO = 0.012     # audio crossfade at every cut (s)

# ---------------------------------------------------------------------------------------------------------------
# Captions: (clip, t0, t1, roman). The words of the clip's transcript with start in [t0, t1) are consumed in order.
SENTENCES = [
    ('IMG_1672', 0.0, 3.9, 'Benazir^2 Kafaalat ka naya Digital Payment System Interoperability'),
    ('IMG_1672', 3.9, 7.0, 'Raqam Aapki^2 aur Intikhab bhi Aapka!^2'),
    ('IMG_1677', 1.0, 5.7, 'Benazir Income Support Programme ne apne payment system mein ek bari tabdeeli introduce ki hai'),
    ('IMG_1677', 5.7, 10.0, 'Ek crore se zyada mustahiq khawateen ke digital wallets qaim kiye ja chuke hain'),
    ('IMG_1681', 1.0, 8.5, 'Ab khawateen poore Pakistan mein kisi bhi waqt aur kisi bhi din apni sahulat ke hisaab se wazaaif ki raqam hasil kar sakengi^2'),
    ('IMG_1689', 0.0, 3.7, 'Yeh iqdaam Sadr-e-Pakistan^2 Asif Ali Zardari aur Wazir-e-Azam^2'),
    ('IMG_1689', 3.7, 4.85, '-^4'),   # cut: "Mian Muhammad Nawaz Sharif"
    ('IMG_1689', 4.85, 8.8, 'ke vision ke mutabiq khawateen ki maali khud-mukhtari^2 ki taraf ek aham qadam hai'),
    ('IMG_1689', 8.8, 11.0, 'Ab@9.31 Interoperability^2 hai kya?'),
    ('IMG_1691', 6.5, 16.5, 'Pehle khawateen apni raqam hasil karne ke liye ek khaas bank ke retailer ki paband hoti thin, jis ki wajah se lambi qataron, intezar aur najaiz katautiyon ka saamna karna parta tha'),
    ('IMG_1698', 0.0, 5.1, 'Ab^0 Interoperability^3 ke zariye khawateen kisi bhi bank ya retailer ki paband nahi hain'),
    ('IMG_1698', 5.1, 9.6, 'Woh kisi bhi banking partner ke authorized retailer se apni raqam hasil kar sakti hain'),
    ('IMG_1699', 0.0, 6.2, 'Agar kisi retailer ke paas rush ho ya woh taawun na kare, toh woh kisi doosre retailer ka intikhab bhi kar sakti hain'),
    ('IMG_1705', 0.0, 8.6, 'In ke 6 banking partners hain: Habib Bank Limited, HBL Microfinance Bank, Easypaisa, JazzCash, Bank of Punjab, Bank Alfalah'),
    ('IMG_1725', 0.0, 2.7, 'Is naye system ke paanch faide hain'),
    ('IMG_1725', 2.7, 4.7, 'Retailers ki monopoly ka khatma'),
    ('IMG_1725', 4.7, 6.9, 'Apni marzi se retailer chunne ki azadi'),
    ('IMG_1725', 6.9, 9.1, 'Lambi qataron aur intezar mein kami'),
    ('IMG_1725', 9.1, 11.1, 'Najaiz katautiyon ki hosla shikni'),
    ('IMG_1725', 11.1, 12.45, 'Aur digital wallet ke through'),
    ('IMG_1725', 12.45, 15.5, 'mehfooz payments aur financial facilities tak rasai'),
    ('IMG_1731', 13.5, 16.8, 'Ab main aap ko batati hoon ke aap ne raqam kaise hasil karni hai'),
    ('IMG_1731', 16.8, 21.9, 'Sab se pehle aap ko bank ka SMS receive hoga, jis ke andar aap ke account mein jama raqam batayi jaye gi'),
    ('IMG_1731', 21.9, 28.45, 'Is ke baad aap ne apna CNIC aur registered mobile number le kar kisi bhi partner bank ke authorized retailer ke paas jana hai'),
    ('IMG_1731', 28.45, 32.9, 'Apni biometric^2 verification karwani hai aur apni raqam le kar gin leni hai'),
    ('IMG_1731', 32.9, 33.7, 'Is ke'),
    ('IMG_1731', 33.7, 36.65, '-^12'),       # rest of take A (replaced by take C)
    ('IMG_1731', 36.65, 39.5, '-^2'),
    ('IMG_1731', 39.5, 44.3, 'baad aap ko ek aur SMS receive hoga jis ko aap ne apne payment record ke liye mehfooz rakhna hai'),
    ('IMG_1737', 1.0, 9.7, 'Ek zaroori hidayat: apna mobile phone aur SIM kisi ghair mutaliqa shakhs ko na dein. Yeh aapka^2 digital wallet hai, iski^2 hifazat aap ko khud hi karni hai'),
    ('IMG_1738', 1.0, 9.6, 'Ek crore se zyada khawateen ko digital wallets aur interoperable^3 payment system se jorna Pakistan hi nahi balke poori duniya ke^0 liye ek bohat bari kamyabi hai'),
    ('IMG_1740', 1.0, 7.33, 'Is se khawateen ko paison se juri sahuliyaton aur digital madad tak pohanchne ka behtar mauqa milta hai'),
    ('IMG_1740', 7.33, 11.6, 'Benazir ka Benazir Khwab, Har Aurat Khud Mukhtar, Ba^1 Ikhtiyar!'),
]

# words shown in gold (brand keywords); compared lower-case without punctuation
KEYWORDS = {'benazir', 'kafaalat', 'interoperability', 'interoperable', 'raqam', 'intikhab', 'aapki', 'aapka', 'crore',
            'digital', 'wallets', 'wallet', 'bisp', 'pakistan', 'khawateen', 'khud-mukhtari', 'maali', 'mukhtar',
            'ikhtiyar', 'khwab', 'sms', 'cnic', 'biometric', 'mehfooz', 'hifazat', 'faide', 'azadi', '6', 'paanch',
            'partners', 'retailer', 'retailers', 'aurat', 'kamyabi', 'zaroori', 'hidayat', 'programme'}


# ---------------------------------------------------------------------------------------------------------------
def _load_words(clip):
    f = TR_FILES.get(clip, TR_DEFAULT)
    d = json.load(open(os.path.join(WS, f)))[clip]
    ws = []
    for s in d:
        for a, b, t in s['w']:
            ws.append([float(a), float(b), t.strip()])
    return ws


_env_cache = {}


def _envelope(clip):
    """10 ms RMS envelope (dB) of the clip's 16 kHz mono audio."""
    if clip not in _env_cache:
        import soundfile as sf
        a, sr = sf.read(os.path.join(WS, 'audio', clip + '.wav'), dtype='float32')
        hop = sr // 100
        n = len(a) // hop
        e = np.sqrt(np.mean(a[:n * hop].reshape(n, hop) ** 2, 1))
        _env_cache[clip] = 20 * np.log10(e + 1e-9)
    return _env_cache[clip]


def snap_onset(clip, t, lo=-0.22, hi=0.12):
    """Snap a Whisper word start to the nearest syllable onset (energy rising through a threshold after a dip)."""
    db = _envelope(clip)
    floor, peak = np.percentile(db, 10), np.percentile(db, 95)
    thr = floor + 0.5 * (peak - floor)
    i0, i1 = max(1, int((t + lo) * 100)), min(len(db) - 1, int((t + hi) * 100))
    cands = [i for i in range(i0, i1) if db[i] >= thr and db[i - 1] < thr]
    if not cands:
        return t
    best = min(cands, key=lambda i: abs(i / 100 - t))
    return best / 100 - 0.02


def caption_words():
    """-> list of dict(clip, t (source s), word, key) in story order (source time)."""
    out = []
    used = {}
    for si, (clip, t0, t1, roman) in enumerate(SENTENCES):
        ws = [w for w in _load_words(clip) if t0 <= w[0] < t1]
        toks = roman.split()
        plan = []
        for tok in toks:
            force = None
            if '@' in tok:
                tok, force = tok.split('@'); force = float(force)
            m = re.match(r'^(.*?)\^(\d+)$', tok)
            word, k = (m.group(1), int(m.group(2))) if m else (tok, 1)
            plan.append((word, k, force))
        need = sum(k for _, k, _f in plan)
        if need != len(ws):
            raise ValueError(f'{clip} [{t0},{t1}) roman needs {need} tokens, transcript has {len(ws)}: '
                             f'{[w[2] for w in ws]}')
        i = 0
        pending = []
        for word, k, force in plan:
            if k == 0:
                pending.append(word)
                continue
            ts = ws[i][0]
            te = ws[i + k - 1][1]
            i += k
            if word == '-':
                pending = []
                continue
            raw = ts if force is None else force
            ts = snap_onset(clip, raw) if force is None else force
            prev = out[-1]['t'] if out and out[-1]['clip'] == clip else -1.0
            nxt = ws[i][0] if i < len(ws) else raw + 1.0
            if ts < prev + 0.12 or ts >= nxt - 0.05:   # snapping collided with a neighbour: keep Whisper's time
                ts = max(raw, prev + 0.12)
            for j, pw in enumerate(pending):     # interpolate zero-token words just before this one
                out.append(dict(clip=clip, t=ts - 0.22 * (len(pending) - j), word=pw, sent=si))
            pending = []
            out.append(dict(clip=clip, t=ts, te=te, word=word, sent=si))
        for j, pw in enumerate(pending):
            out.append(dict(clip=clip, t=(out[-1]['te'] if out else t0) + 0.15 * (j + 1), word=pw, sent=si))
    for w in out:
        k = re.sub(r'[^a-z0-9\-]', '', w['word'].lower())
        w['key'] = k in KEYWORDS
    return out


# ---------------------------------------------------------------------------------------------------------------
class Timeline:
    """Maps output time <-> (segment, source time)."""

    def __init__(self):
        self.segs = []
        t = 0.0
        for sid, clip, a, b, z in SEGMENTS:
            d = (b - a) / SPEED
            self.segs.append(dict(id=sid, clip=clip, a=a, b=b, zoom=z, t0=t, t1=t + d))
            t += d
        self.speech_end = t
        self.dur = t + END_CARD
        self.nframes = int(round(self.dur * FPS))

    def seg_at(self, t):
        for s in self.segs:
            if t < s['t1']:
                return s
        return self.segs[-1]

    def src(self, t):
        s = self.seg_at(t)
        return s, s['a'] + (min(t, s['t1']) - s['t0']) * SPEED

    def out_time(self, clip, src_t):
        """Output time for a source time (None if that moment was cut)."""
        for s in self.segs:
            if s['clip'] == clip and s['a'] - 1e-6 <= src_t < s['b'] + 1e-6:
                return s['t0'] + (src_t - s['a']) / SPEED
        return None

    def seg(self, sid):
        return next(s for s in self.segs if s['id'] == sid)

    def at(self, clip, src_t):
        """Output time of a source moment; raises if it was cut."""
        t = self.out_time(clip, src_t)
        if t is None:
            raise ValueError(f'{clip}@{src_t} is not in the edit')
        return t


_TL = None


def timeline():
    global _TL
    if _TL is None:
        _TL = Timeline()
    return _TL


def out_words():
    """Caption words placed on the output timeline (cut words dropped)."""
    tl = timeline()
    res = []
    for w in caption_words():
        t = tl.out_time(w['clip'], w['t'])
        if t is None:
            # words timed into a cut by Whisper drift: clamp to the nearest kept moment of the same clip
            cands = [s for s in tl.segs if s['clip'] == w['clip']]
            best = min(cands, key=lambda s: min(abs(w['t'] - s['a']), abs(w['t'] - s['b'])))
            src = min(max(w['t'], best['a']), best['b'] - 0.05)
            lead = best['a'] - w['t']           # Whisper often puts a clip's first word at 0.00 s (before speech)
            if not (0 <= lead <= 1.4) and min(abs(w['t'] - best['a']), abs(w['t'] - best['b'])) > 0.6:
                continue
            if 0 <= lead <= 1.4:
                src = best['a'] + 0.06
            t = tl.out_time(w['clip'], src)
        if res and t < res[-1]['ot'] + 0.08 and t > res[-1]['ot'] - 1.0:
            t = res[-1]['ot'] + 0.08
        res.append(dict(w, ot=t))
    return res


if __name__ == '__main__':
    tl = timeline()
    for s in tl.segs:
        print(f"{s['id']:10s} {s['clip']} src {s['a']:6.2f}-{s['b']:6.2f}  out {s['t0']:7.2f}-{s['t1']:7.2f}  zoom {s['zoom']}")
    print('speech end %.2f  total %.2f  frames %d' % (tl.speech_end, tl.dur, tl.nframes))
    ws = out_words()
    line = []
    for w in ws:
        line.append(f"{w['word']}@{w['ot']:.2f}")
    print(' '.join(line))
