"""Rebuild the git-ignored workspace3/ data after a fresh clone (cloud containers are reset between sessions).

python3 setup_workspace.py              fonts + brand logo variants + website photos
python3 setup_workspace.py --footage    also download the client's Drive folder 'fostering' and extract frames

3D renders (workspace3/assets3d) are rebuilt with assets3d_icons.py / assets3d_hero.py / assets3d_everyday.py /
assets3d_household.py, and the SFX with the reel modules (render.py builds them on demand).
"""
import concurrent.futures as cf
import html
import json
import os
import re
import subprocess
import sys
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import wsconf  # noqa: E402
WS = wsconf.workspace()
SITE = 'https://organicfostering.co.uk'
DRIVE_FOLDER = '1HU1dWfJVcwtORMaNxGOOBIXbv6CJr4Z0'
UA = {'User-Agent': 'Mozilla/5.0'}


def get(url, path=None, headers=UA):
    req = urllib.request.Request(url, headers=headers)
    data = urllib.request.urlopen(req, timeout=300).read()
    if path:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'wb') as f:
            f.write(data)
    return data


def fonts():
    d = os.path.join(WS, 'fonts')
    names = {400: 'Regular', 500: 'Medium', 600: 'SemiBold', 700: 'Bold', 800: 'ExtraBold', 900: 'Black'}
    specs = {'Nunito': 'Nunito:ital,wght@0,400;0,600;0,700;0,800;0,900;1,800;1,900',
             'Poppins': 'Poppins:wght@400;500;600;700;800;900', 'Caveat': 'Caveat:wght@700'}
    for fam, spec in specs.items():
        css = get(f'https://fonts.googleapis.com/css2?family={spec}', headers={'User-Agent': 'Wget/1.0'}).decode()
        for block in re.findall(r'@font-face\s*{(.*?)}', css, re.S):
            italic = re.search(r'font-style:\s*(\w+)', block).group(1) == 'italic'
            w = int(re.search(r'font-weight:\s*(\d+)', block).group(1))
            url = re.search(r'url\((.*?)\)', block).group(1)
            get(url, os.path.join(d, f'{fam}-{names[w]}' + ('Italic' if italic else '') + '.ttf'))
    print('fonts ->', d, len(os.listdir(d)))


def brand():
    import cairosvg
    import numpy as np
    from PIL import Image
    d = os.path.join(WS, 'brand')
    os.makedirs(d, exist_ok=True)
    page = get(SITE + '/').decode('utf-8', 'ignore')
    logo = re.search(r'assets/organic-fostering-final-logo[^"?]*\.svg', page).group(0)
    get(f'{SITE}/{logo}', os.path.join(d, 'organic-fostering-final-logo-2026-09-25.svg'))
    get(f'{SITE}/assets/favicon.svg', os.path.join(d, 'favicon.svg'))
    svg = os.path.join(d, 'organic-fostering-final-logo-2026-09-25.svg')
    cairosvg.svg2png(url=svg, write_to=os.path.join(d, 'logo_4k.png'), output_width=4116)
    cairosvg.svg2png(url=os.path.join(d, 'favicon.svg'), write_to=os.path.join(d, 'favicon_1k.png'), output_width=1024)
    im = Image.open(os.path.join(d, 'logo_4k.png'))

    def trim(x):
        return x.crop(x.getbbox())
    trim(im).save(os.path.join(d, 'logo_full.png'))
    trim(im.crop((100, 0, 1910, 1180))).save(os.path.join(d, 'logo_mark.png'))
    trim(im.crop((2020, 0, im.width, 1180))).save(os.path.join(d, 'logo_wordmark.png'))
    trim(im.crop((0, 1240, im.width, im.height))).save(os.path.join(d, 'logo_tagline.png'))
    a = np.array(im).astype(np.float32)
    rgb = a[..., :3]
    mag = (rgb[..., 0] > 120) & (rgb[..., 1] < 60) & (rgb[..., 2] > 40)
    a[mag, 0:3] = [255, 236, 246]
    Image.fromarray(a.astype(np.uint8)).crop(im.getbbox()).save(os.path.join(d, 'logo_full_onDark.png'))
    print('brand ->', d, sorted(os.listdir(d)))


def site_images():
    d = os.path.join(WS, 'site_img')
    page = get(SITE + '/').decode('utf-8', 'ignore')
    paths = sorted(set(re.findall(r'assets/images/homepage/[A-Za-z0-9_.-]+\.(?:webp|jpg)', page)))
    paths = [p for p in paths if not re.search(r'-(480|768|1200)\.webp$', p)]
    with cf.ThreadPoolExecutor(6) as ex:
        list(ex.map(lambda p: get(f'{SITE}/{p}', os.path.join(d, os.path.basename(p))), paths))
    print('site_img ->', d, len(paths))


def footage():
    """Client footage (Drive folder 'fostering', shared as anyone-with-link) -> frames/cXX/%05d.jpg + manifest."""
    src, frames = os.path.join(WS, 'src'), os.path.join(WS, 'frames')
    os.makedirs(src, exist_ok=True)
    t = get(f'https://drive.google.com/embeddedfolderview?id={DRIVE_FOLDER}#list').decode('utf-8', 'ignore')
    ents = sorted(re.findall(r'<div class="flip-entry" id="entry-([^"]+)".*?<div class="flip-entry-title">(.*?)</div>', t, re.S),
                  key=lambda e: html.unescape(e[1]))

    def dl(e):
        out = os.path.join(src, html.unescape(e[1]))
        if not os.path.exists(out):
            subprocess.run(['curl', '-sSL', '--retry', '4', '-A', 'Mozilla/5.0', '-o', out,
                            f'https://drive.usercontent.google.com/download?id={e[0]}&export=download&confirm=t'], check=True)
        return out
    with cf.ThreadPoolExecutor(6) as ex:
        files = list(ex.map(dl, ents))
    short = ['tent_dad_daughter', 'two_moms_girl_hug', 'blocks_toddler', 'counselor_teddy_kids', 'counselor_family_sofa',
             'family_sofa_teddy_paperwork', 'two_dads_laptop_sofa', 'yard_meeting', 'piggyback_vertical', 'arrival_teddy_backpack',
             'dad_daughter_cuddle', 'mum_teddy_hug', 'mum_boy_laugh', 'two_dads_tablet', 'two_mums_baby_play',
             'two_mums_baby_blanket', 'dog_kennel', 'park_bench_teddy', 'document_explain']
    man = {}
    for k, f in enumerate(files):
        p = json.loads(subprocess.run(['ffprobe', '-v', 'error', '-select_streams', 'v:0', '-show_entries',
                                       'stream=width,height,r_frame_rate:format=duration', '-of', 'json', f],
                                      capture_output=True, text=True).stdout)
        s = p['streams'][0]
        num, den = map(int, s['r_frame_rate'].split('/'))
        cid = f'c{k:02d}'
        man[cid] = dict(name=short[k] if k < len(short) else cid, src=os.path.basename(f), w=s['width'], h=s['height'],
                        fps=num / den, dur=float(p['format']['duration']))
        d = os.path.join(frames, cid)
        os.makedirs(d, exist_ok=True)
        vf = ('scale=-2:1920:flags=lanczos,' if s['height'] > 1920 else '') + 'format=yuvj420p'
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', f, '-vf', vf, '-q:v', '2', '-start_number', '0',
                        os.path.join(d, '%05d.jpg')], check=True)
    json.dump(man, open(os.path.join(frames, 'manifest.json'), 'w'), indent=1)
    print('frames ->', frames, len(man))


if __name__ == '__main__':
    fonts()
    brand()
    site_images()
    if '--footage' in sys.argv:
        footage()
