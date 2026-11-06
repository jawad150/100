"""Voiceover for BMHC "Shine" (the PDF's script word for word): Microsoft neural en-GB-LibbyNeural — young, warm, gentle
and conversational. Calm, flowing pace with natural pauses (half a second or more between the lantern words), a soft
lift where she smiles, and a clean, un-clipped last word with a gentle fade-out tail.

Usage: python3 vo_shine.py [voice]
"""
import os, sys, json, ssl, asyncio, subprocess
import numpy as np
import soundfile as sf
import edge_tts, edge_tts.communicate as C

C._SSL_CTX = ssl.create_default_context(cafile='/root/.ccr/ca-bundle.crt')
S = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'workspace_shine'))
OUT = f'{S}/tts'
VOICE = sys.argv[1] if len(sys.argv) > 1 else 'en-GB-LibbyNeural'
SR = 48000

# (text, pause_after, rate, pitch)
PHRASES = [
    ('Every girl has a spark.', 0.8, '-12%', '+2Hz'),
    ('At Shine, it grows through faith and character,', 0.55, '-10%', '+1Hz'),
    ('creativity,', 0.55, '-10%', '+2Hz'),
    ('life skills and well-being,', 0.55, '-10%', '+1Hz'),
    ('sport,', 0.55, '-8%', '+2Hz'),
    ('and friendship.', 0.85, '-10%', '+4Hz'),
    ('Give your daughter a place where she can shine, grow, and feel confident.', 0.8, '-12%', '+3Hz'),
    ('Shine Youth Club, for girls fourteen to eighteen.', 0.45, '-10%', '+2Hz'),
    ('Join today.', 0.0, '-12%', '+4Hz'),
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
        env = np.convolve(np.abs(a), np.ones(240) / 240, mode='same')
        nz = np.where(env > 0.006 * env.max())[0]
        s0 = max(0, nz[0] - int(0.04 * SR))
        last = i == len(PHRASES) - 1
        tail = int((0.45 if last else 0.22) * SR)          # never clip the end of a word
        a = a[s0: min(len(a), nz[-1] + tail)]
        fo = int((0.3 if last else 0.08) * SR)
        a[-fo:] *= np.cos(np.linspace(0, np.pi / 2, fo)) ** 2
        a[:int(0.01 * SR)] *= np.linspace(0, 1, int(0.01 * SR))
        d = len(a) / SR
        phr.append((i, round(t, 3), round(d, 3), text))
        for w, off, du in wb:
            words.append((w, round(max(0, t + off - s0 / SR), 3), i))
        parts.append(a)
        t += d
        parts.append(np.zeros(int(pause * SR), np.float32))
        t += pause
        print(f'{i:2d} {t:6.2f}  {text}')
    vo = np.concatenate(parts + [np.zeros(int(0.6 * SR), np.float32)])
    vo = vo / max(1e-6, np.abs(vo).max()) * 0.9
    sf.write(f'{OUT}/vo.wav', vo, SR)
    json.dump({'voice': VOICE, 'dur': round(len(vo) / SR, 3), 'phrases': phr, 'words': words}, open(f'{OUT}/info.json', 'w'), indent=1)
    print('total', round(len(vo) / SR, 2), 'words', len(words))
