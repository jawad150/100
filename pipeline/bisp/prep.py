"""Rebuild workspace_bisp/ (git-ignored) from scratch: footage, brand, fonts, transcripts, grade, frames, faces.

    pip install numpy scipy "opencv-python-headless==4.10.0.84" pillow soundfile faster-whisper
    python3 prep.py all            # or one step: download | brand | fonts | audio | transcribe | probe | grade | frames | faces

Footage: the client's Drive folder (shared anyone-with-link). Logo: the official banner from bisp.gov.pk.
Transcripts: Whisper medium for every clip, large-v3 for IMG_1731 / IMG_1691 / IMG_1689 / IMG_1672 (edl.TR_FILES).
"""
import os, sys, re, json, glob, html, subprocess, urllib.request
import concurrent.futures as cf

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
WS = os.path.abspath(os.environ.get('BISP_WS', os.path.join(HERE, '..', '..', 'workspace_bisp')))
DRIVE_FOLDER = '1SgVDv53IFY4xL5JajLbTD5B_lms_dkF5'
UA = 'Mozilla/5.0'
PROMPT = ('Benazir Income Support Programme BISP, Interoperability, digital wallets, khawateen, mustahiq, wazaaif, raqam, '
          'retailer, Habib Bank Limited, HBL Microfinance Bank, Easypaisa, JazzCash, Bank Alfalah, Bank of Punjab, '
          'CNIC, SMS, registered mobile number, partner bank, authorized retailer, biometric verification')


def get(url, out=None):
    req = urllib.request.Request(url, headers={'User-Agent': UA})
    data = urllib.request.urlopen(req, timeout=60).read()
    if out:
        open(out, 'wb').write(data)
    return data


def download():
    src = os.path.join(WS, 'src'); os.makedirs(src, exist_ok=True)
    t = get(f'https://drive.google.com/embeddedfolderview?id={DRIVE_FOLDER}#list').decode('utf-8', 'ignore')
    ents = re.findall(r'<div class="flip-entry" id="entry-([^"]+)".*?<div class="flip-entry-title">(.*?)</div>', t, re.S)

    def dl(e):
        out = os.path.join(src, html.unescape(e[1]))
        if not os.path.exists(out):
            subprocess.run(['curl', '-sSL', '--retry', '4', '-A', UA, '-o', out,
                            f'https://drive.usercontent.google.com/download?id={e[0]}&export=download&confirm=t'], check=True)
    with cf.ThreadPoolExecutor(6) as ex:
        list(ex.map(dl, ents))
    print('clips', len(ents))


def brand():
    d = os.path.join(WS, 'brand', 'dl'); os.makedirs(d, exist_ok=True)
    get('https://bisp.gov.pk/Siteimage/Setting/bisplogonew.png', os.path.join(d, 'bisplogonew.png'))
    print('logo ok')


def fonts():
    d = os.path.join(WS, 'fonts'); os.makedirs(d, exist_ok=True)
    ua = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_6_8) AppleWebKit/534.59.10 (KHTML, like Gecko) Version/5.1.9 Safari/534.59.10'
    for fam, ws in (('Poppins', (500, 600, 700, 800, 900)), ('Inter', (500, 600, 700, 800))):
        for w in ws:
            css = urllib.request.urlopen(urllib.request.Request(
                f'https://fonts.googleapis.com/css2?family={fam}:wght@{w}', headers={'User-Agent': ua})).read().decode()
            url = re.search(r'url\(([^)]+)\)', css).group(1)
            get(url, os.path.join(d, f'{fam}-{w}.ttf'))
    print('fonts ok')


def audio():
    d = os.path.join(WS, 'audio'); os.makedirs(d, exist_ok=True)
    for f in sorted(glob.glob(os.path.join(WS, 'src', '*.MOV'))):
        b = os.path.basename(f)[:-4]
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', f, '-vn', '-ac', '1', '-ar', '16000', os.path.join(d, b + '.wav')], check=True)


def _transcribe(model, clips, out):
    import soundfile as sf
    from faster_whisper import WhisperModel
    m = WhisperModel(model, device='cpu', compute_type='int8', cpu_threads=os.cpu_count())
    res = {}
    for c in clips:
        a, _ = sf.read(os.path.join(WS, 'audio', c + '.wav'), dtype='float32')
        segs, _ = m.transcribe(a, language='ur', word_timestamps=True, beam_size=5, initial_prompt=PROMPT,
                               condition_on_previous_text=(model != 'large-v3'))
        res[c] = [dict(s=s.start, e=s.end, t=s.text, w=[(w.start, w.end, w.word) for w in s.words]) for s in segs]
        print(model, c, ' '.join(s['t'] for s in res[c]), flush=True)
    json.dump(res, open(os.path.join(WS, out), 'w'), ensure_ascii=False, indent=1)


def transcribe():
    clips = sorted(os.path.basename(f)[:-4] for f in glob.glob(os.path.join(WS, 'audio', '*.wav')))
    _transcribe('medium', clips, 'transcript_medium_ur.json')
    _transcribe('large-v3', ['IMG_1731', 'IMG_1691'], 'transcript_large_1731_1691.json')
    _transcribe('large-v3', ['IMG_1689', 'IMG_1672'], 'transcript_large_1689_1672.json')


def probe():
    import grade
    d = os.path.join(WS, 'probe'); os.makedirs(d, exist_ok=True)
    for f in sorted(glob.glob(os.path.join(WS, 'src', '*.MOV'))):
        b = os.path.basename(f)[:-4]
        dur = float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', f],
                                   capture_output=True, text=True).stdout)
        for k in range(1, 6):
            subprocess.run(['ffmpeg', '-v', 'error', '-y', '-ss', str(dur * k / 6), '-i', f, '-frames:v', '1', '-vf',
                            grade.CST + ',scale=270:480,format=rgb48le', os.path.join(d, f'{b}_{k}.png')], check=True)


def grade_step():
    import grade
    grade.measure(); grade.luts()


def frames():
    def one(f):
        c = os.path.basename(f)[:-4]
        d = os.path.join(WS, 'frames', c); os.makedirs(d, exist_ok=True)
        import grade
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', f, '-vf',
                        f"{grade.CST},lut3d=file={os.path.join(WS, 'grade', c + '.cube')}:interp=tetrahedral,format=rgb24",
                        '-q:v', '2', '-start_number', '0', os.path.join(d, '%05d.jpg')], check=True)
        return c
    with cf.ThreadPoolExecutor(3) as ex:
        for c in ex.map(one, sorted(glob.glob(os.path.join(WS, 'src', '*.MOV')))):
            print('frames', c)


def faces():
    import cv2, numpy as np
    fc = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    out = {}
    for d in sorted(glob.glob(os.path.join(WS, 'frames', 'IMG_*'))):
        fs = sorted(glob.glob(d + '/*.jpg'))
        res = []
        for p in fs[::max(1, len(fs) // 24)]:
            g = cv2.cvtColor(cv2.resize(cv2.imread(p), (540, 960)), cv2.COLOR_BGR2GRAY)
            f = fc.detectMultiScale(g, 1.1, 5, minSize=(40, 40))
            if len(f):
                x, y, w, h = max(f, key=lambda r: r[2] * r[3])
                res.append(((x + w / 2) * 2, (y + h / 2) * 2, w * 2))
        r = np.array(res)
        out[os.path.basename(d)] = dict(cx=float(np.median(r[:, 0])), cy=float(np.median(r[:, 1])), size=float(np.median(r[:, 2])))
    json.dump(out, open(os.path.join(WS, 'faces.json'), 'w'), indent=1)
    print('faces', len(out))


STEPS = dict(download=download, brand=brand, fonts=fonts, audio=audio, transcribe=transcribe, probe=probe,
             grade=grade_step, frames=frames, faces=faces)

if __name__ == '__main__':
    arg = sys.argv[1] if len(sys.argv) > 1 else 'all'
    for k, fn in STEPS.items():
        if arg in ('all', k):
            fn()
