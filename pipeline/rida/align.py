"""Aligns the Roman-Urdu script (Script.txt) to Whisper word timestamps, giving per-word
caption timings. Also reports script lines that are missing / repeated in the audio."""
import json, re, sys, difflib

DEV = {'अ':'a','आ':'aa','इ':'i','ई':'i','उ':'u','ऊ':'u','ए':'e','ऐ':'ai','ओ':'o','औ':'au','क':'k','ख':'kh','ग':'g','घ':'gh',
       'च':'ch','छ':'chh','ज':'j','झ':'jh','ट':'t','ठ':'th','ड':'d','ढ':'dh','ण':'n','त':'t','थ':'th','द':'d','ध':'dh','न':'n',
       'प':'p','फ':'f','ब':'b','भ':'bh','म':'m','य':'y','र':'r','ल':'l','व':'w','श':'sh','ष':'sh','स':'s','ह':'h','़':'',
       'ा':'a','ि':'i','ी':'i','ु':'u','ू':'u','े':'e','ै':'ai','ो':'o','ौ':'au','ं':'n','ँ':'n','्':'','ड़':'r','ढ़':'rh','ज़':'z','फ़':'f','क़':'q','ख़':'kh','ग़':'gh'}


def translit(w):
    return ''.join(DEV.get(ch, ch) for ch in w)


def norm(w):
    w = w.lower()
    w = re.sub(r'[^a-z0-9%.]', '', w)
    return w.strip('.')


def skel(w):
    w = norm(w)
    w = re.sub(r'(.)\1+', r'\1', w)
    return re.sub(r'[aeiouyh]', '', w) or w[:2]


def sim(a, b):
    if norm(a) == norm(b):
        return 3.0
    r = difflib.SequenceMatcher(None, skel(a), skel(b)).ratio()
    r2 = difflib.SequenceMatcher(None, norm(a), norm(b)).ratio()
    return 2.2 * max(r, r2) - 1.0


def tokens(script):
    out = []
    for li, line in enumerate([l for l in script.split('\n') if l.strip()]):
        for w in line.split():
            out.append((w, li))
    return out


def main(script_path, roman_json, dev_json, out_json, roman_start, roman_end):
    script = open(script_path, encoding='utf8').read()
    script = script.split('\n\n\n')[0]  # drop editor notes after the script
    S = tokens(script)
    R = json.load(open(roman_json))
    D = json.load(open(dev_json))
    # Devanagari pass before roman_start (the Roman pass mis-timed the opening), Roman pass after
    H = [dict(w=translit(d['w']), s=d['s'], e=d['e']) for d in D if d['s'] < roman_start]
    H += [r for r in R if r['s'] >= roman_start and r['s'] <= roman_end]
    H += [dict(w=translit(d['w']), s=d['s'], e=d['e']) for d in D if d['s'] > roman_end]
    n, m = len(S), len(H)
    G = -0.6
    dp = [[0.0] * (m + 1) for _ in range(n + 1)]
    bt = [[0] * (m + 1) for _ in range(n + 1)]
    for i in range(1, n + 1):
        dp[i][0] = i * G; bt[i][0] = 1
    for j in range(1, m + 1):
        dp[0][j] = j * G; bt[0][j] = 2
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            c = [dp[i-1][j-1] + sim(S[i-1][0], H[j-1]['w']), dp[i-1][j] + G, dp[i][j-1] + G]
            k = max(range(3), key=lambda q: c[q]); dp[i][j] = c[k]; bt[i][j] = k
    i, j, pairs = n, m, {}
    while i > 0 or j > 0:
        k = bt[i][j] if i > 0 and j > 0 else (1 if j == 0 else 2)
        if k == 0:
            pairs[i-1] = j-1; i -= 1; j -= 1
        elif k == 1:
            i -= 1
        else:
            j -= 1
    words = []
    for i, (w, li) in enumerate(S):
        if i in pairs:
            h = H[pairs[i]]; words.append(dict(w=w, line=li, s=h['s'], e=h['e'], ok=sim(w, h['w']) > 0.3, heard=h['w']))
        else:
            words.append(dict(w=w, line=li, s=None, e=None, ok=False, heard=''))
    # interpolate gaps
    k = 0
    while k < len(words):
        if words[k]['s'] is None:
            a = k
            while k < len(words) and words[k]['s'] is None:
                k += 1
            t0 = words[a-1]['e'] if a > 0 else 0.0
            t1 = words[k]['s'] if k < len(words) else t0 + 0.3 * (k - a)
            step = (t1 - t0) / (k - a)
            for q in range(a, k):
                words[q]['s'] = t0 + step * (q - a); words[q]['e'] = t0 + step * (q - a + 1)
        else:
            k += 1
    for q in range(1, len(words)):  # monotone
        words[q]['s'] = max(words[q]['s'], words[q-1]['s'] + 0.04)
    json.dump(words, open(out_json, 'w'), indent=1, ensure_ascii=False)
    used = sorted(set(pairs.values()))
    extra = [H[j]['w'] for j in range(m) if j not in used]
    print('script words', n, 'heard words', m, 'matched', sum(w['ok'] for w in words))
    print('heard but not in script:', ' '.join(extra))
    for w in words:
        if not w['ok']:
            print(f"  ? {w['w']:<14} heard={w['heard']:<14} {w['s']:.2f}")


if __name__ == '__main__':
    main(*sys.argv[1:5], float(sys.argv[5]), float(sys.argv[6]))
