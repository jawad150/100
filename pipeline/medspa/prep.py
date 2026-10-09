"""Prepare sources for the P.S. Med Spa reel.

- downloads the caption fonts (free stand-ins for the brand fonts, see README)
- extracts every frame of the source edit at 1440x2560 (headroom for push-ins)
- transcribes the voice with word timings (faster-whisper large-v3) unless
  words.json already exists

Usage: python3 pipeline/medspa/prep.py [fonts|frames|words|all]
"""
import json, os, subprocess, sys, urllib.request, re

HERE = os.path.dirname(os.path.abspath(__file__))
WS = os.environ.get('MEDSPA_WORKDIR', os.path.abspath(os.path.join(HERE, '..', '..', 'workspace', 'medspa')))
SRC = f'{WS}/src/PS-Med-Spa.mov'
FW, FH = 1440, 2560

# Founders Grotesk -> Hanken Grotesk, Freight Display Pro -> Fraunces (opsz 144, no soft/wonk)
FONTS = {
    'Hanken-LightItalic': 'Hanken+Grotesk:ital,wght@1,300',
    'Hanken-Light': 'Hanken+Grotesk:wght@300',
    'Hanken-Regular': 'Hanken+Grotesk:wght@400',
    'Hanken-Medium': 'Hanken+Grotesk:wght@500',
    'Hanken-MediumItalic': 'Hanken+Grotesk:ital,wght@1,500',
    'Fraunces-SemiBold': 'Fraunces:opsz,wght,SOFT,WONK@144,600,0,0',
    'Fraunces-SemiBoldItalic': 'Fraunces:ital,opsz,wght,SOFT,WONK@1,144,600,0,0',
}


def fonts():
    os.makedirs(f'{WS}/fonts', exist_ok=True)
    for name, q in FONTS.items():
        out = f'{WS}/fonts/{name}.ttf'
        if os.path.exists(out):
            continue
        req = urllib.request.Request(f'https://fonts.googleapis.com/css2?family={q}', headers={'User-Agent': 'Wget/1.21'})
        css = urllib.request.urlopen(req).read().decode()
        url = re.findall(r'url\((https://fonts\.gstatic\.com/[^)]+)\)', css)[0]
        urllib.request.urlretrieve(url, out)
        print('font', name)


def frames():
    out = f'{WS}/frames'
    os.makedirs(out, exist_ok=True)
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', SRC, '-vf',
                    f'scale={FW}:{FH}:flags=lanczos', '-start_number', '0',
                    '-compression_level', '1', f'{out}/%04d.png'], check=True)
    print('frames', len(os.listdir(out)))


def words():
    out = os.path.join(HERE, 'words.json')
    if os.path.exists(out):
        return
    import numpy as np, wave
    from faster_whisper import WhisperModel
    wav = f'{WS}/audio16k.wav'
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', SRC, '-vn', '-ac', '1', '-ar', '16000', wav], check=True)
    wf = wave.open(wav)
    a = np.frombuffer(wf.readframes(wf.getnframes()), np.int16).astype(np.float32) / 32768
    m = WhisperModel('large-v3', device='cpu', compute_type='int8')
    segs, _ = m.transcribe(a, language='en', word_timestamps=True, beam_size=5)
    ws = [dict(w=w.word.strip(), s=round(w.start, 3), e=round(w.end, 3)) for s in segs for w in s.words]
    json.dump(ws, open(out, 'w'), indent=1)


if __name__ == '__main__':
    what = sys.argv[1] if len(sys.argv) > 1 else 'all'
    if what in ('fonts', 'all'):
        fonts()
    if what in ('words', 'all'):
        words()
    if what in ('frames', 'all'):
        frames()
