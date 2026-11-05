"""Voiceover for Hulk Marketing "Same Business?" (the concept PDF's 64 words, word for word): Microsoft neural voice
en-GB-RyanNeural, natural and upbeat. Word timings from the voice's own word boundaries.

Usage: python3 vo_sb.py [voice]
"""
import os, sys, json, ssl, asyncio, subprocess
import numpy as np
import soundfile as sf
import edge_tts, edge_tts.communicate as C

C._SSL_CTX = ssl.create_default_context(cafile='/root/.ccr/ca-bundle.crt')
S = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'workspace_hulk'))
OUT = f'{S}/tts'
VOICE = sys.argv[1] if len(sys.argv) > 1 else 'en-GB-RyanNeural'
SR = 48000

# (text, pause_after, rate, pitch)
PHRASES = [
    ('Quick one.', 0.15, '+0%', '+4Hz'),
    ('Are these the same business?', 0.35, '+0%', '+3Hz'),
    ('The van.', 0.14, '+6%', '+3Hz'),
    ('The sign.', 0.14, '+6%', '+2Hz'),
    ('The card.', 0.14, '+6%', '+3Hz'),
    ('The website.', 0.14, '+6%', '+2Hz'),
    ('The Instagram.', 0.14, '+6%', '+3Hz'),
    ('The invoice.', 0.45, '+6%', '+1Hz'),
    ('They are.', 0.25, '-6%', '+0Hz'),
    ("And your customers can't tell either.", 0.45, '+0%', '+1Hz'),
    ('Disjointed brand, diluted trust.', 0.5, '-6%', '-1Hz'),
    ('So we build one system: one logo, one palette, one typeface.', 0.35, '+0%', '+3Hz'),
    ('Then roll it out across every touchpoint.', 0.45, '+0%', '+3Hz'),
    ('A premium brand is a system, not a logo file.', 0.4, '-4%', '+2Hz'),
    ('Build your brand identity with Hulk.', 0.0, '-2%', '+5Hz'),
]


async def synth(text, rate, pitch, path):
    com = edge_tts.Communicate(text, VOICE, rate=rate, pitch=pitch, boundary='WordBoundary', proxy=os.environ.get('HTTPS_PROXY'))
    words = []
    with open(path, 'wb') as f:
        async for ch in com.stream():
            if ch['type'] == 'audio':
                f.write(ch['data'])
            elif ch['type'] == 'WordBoundary':
                words.append((ch['text'], ch['offset'] / 1e7, ch['duration'] / 1e7))
    return words


def load(path):
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', path, '-f', 'f32le', '-ac', '1', '-ar', str(SR), '-'], capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.float32).copy()


if __name__ == '__main__':
    os.makedirs(f'{OUT}/parts', exist_ok=True)
    parts, t, words, phr = [], 0.0, [], []
    for i, (text, pause, rate, pitch) in enumerate(PHRASES):
        p = f'{OUT}/parts/p{i:02d}.mp3'
        wb = asyncio.run(synth(text, rate, pitch, p))
        a = load(p)
        env = np.abs(a)
        nz = np.where(env > 0.01 * env.max())[0]
        s0 = max(0, nz[0] - int(0.03 * SR))
        a = a[s0: min(len(a), nz[-1] + int(0.12 * SR))]
        a[-int(0.05 * SR):] *= np.linspace(1, 0, int(0.05 * SR))
        d = len(a) / SR
        phr.append((i, round(t, 3), round(d, 3), text))
        for w, off, du in wb:
            words.append((w, round(max(0, t + off - s0 / SR), 3), i))
        parts.append(a)
        t += d
        parts.append(np.zeros(int(pause * SR), np.float32))
        t += pause
        print(f'{i:2d} {t:6.2f}  {text}')
    vo = np.concatenate(parts)
    vo = vo / max(1e-6, np.abs(vo).max()) * 0.9
    sf.write(f'{OUT}/vo.wav', vo, SR)
    json.dump({'voice': VOICE, 'dur': round(len(vo) / SR, 3), 'phrases': phr, 'words': words}, open(f'{OUT}/info.json', 'w'), indent=1)
    print('total', round(len(vo) / SR, 2), 'words', len(words))
