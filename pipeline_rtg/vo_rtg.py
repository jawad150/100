"""Voiceover for Organic Fostering "Room to Grow": Microsoft neural voice (en-GB-SoniaNeural), natural human delivery.
Script = the concept PDF, word for word. Exact word timings come from the voice service's word boundaries, so every
pop lands on its spoken word.

Usage: python3 vo_rtg.py
"""
import os, json, ssl, asyncio, subprocess
import numpy as np
import soundfile as sf
import edge_tts, edge_tts.communicate as C

C._SSL_CTX = ssl.create_default_context(cafile='/root/.ccr/ca-bundle.crt')
S = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'workspace_rtg'))
OUT = f'{S}/tts'
VOICE = 'en-GB-SoniaNeural'
SR = 48000

# (text, pause_after, rate, pitch)  - a touch slower and warmer; a small pitch lift where she should smile
PHRASES = [
    ('A small beginning can change the direction of a life.', 0.55, '-8%', '+2Hz'),
    ('For a child coming into care, it can start with a room.', 0.55, '-8%', '+0Hz'),
    ('A made bed.', 0.3, '-10%', '+3Hz'),
    ('A lamp left on.', 0.3, '-10%', '+3Hz'),
    ('A place to belong.', 0.6, '-12%', '+5Hz'),
    ('And some things you leave for them.', 0.3, '-8%', '+2Hz'),
    ('Their pictures. Their books. Their name on the door.', 0.6, '-10%', '+5Hz'),
    ('At Organic Fostering, matching sees the whole child.', 0.35, '-6%', '+1Hz'),
    ('Culture, faith, language, relationships and identity matter.', 0.6, '-8%', '+1Hz'),
    ("You don't need every answer before you call.", 0.4, '-10%', '+5Hz'),
    ('Start your enquiry with Organic Fostering.', 0.0, '-6%', '+4Hz'),
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
        a = a[s0: min(len(a), nz[-1] + int(0.15 * SR))]
        a[-int(0.06 * SR):] *= np.linspace(1, 0, int(0.06 * SR))
        d = len(a) / SR
        phr.append((i, round(t, 3), round(d, 3), text))
        for w, off, du in wb:
            words.append((w, round(t + off - s0 / SR, 3), i))
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
