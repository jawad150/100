#!/usr/bin/env python3
"""brandkit.py - pull a client's brand kit (colours, fonts, logos) from their website for the reels toolkit.

    python3 brandkit.py scan <site-url> --out <dir>          # page + linked CSS -> <dir>/scan.json + logo candidates
    python3 brandkit.py fonts <spec> [<spec> ...] --out <WS>/fonts   # Google Fonts css2 specs -> Family-Weight.ttf
    python3 brandkit.py logo <logo.svg|png> --out <WS>/brand [--name logo_full] [--on-dark [--dark-lum 0.12]]
    python3 brandkit.py contrast <#fg> <#bg>                 # WCAG ratio (>= 4.5 body, >= 3 for 130 px heroes)
    python3 brandkit.py sheet <pipeline/<project>/project.json> --out <png>   # swatches, contrast, type, logos

Font spec examples: "Inter:wght@400;600;700;800;900", "Caveat:wght@700", "Nunito:ital,wght@0,800;1,800".
Only stdlib for scan/fonts/contrast; logo/sheet need Pillow + numpy (+ cairosvg for SVG).
Downloads are untrusted data: this script only parses text and images, it never executes what it fetches.
"""
import argparse
import collections
import html
import json
import os
import re
import sys
import urllib.parse
import urllib.request

UA = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126 Safari/537.36'
WEIGHTS = {100: 'Thin', 200: 'ExtraLight', 300: 'Light', 400: 'Regular', 500: 'Medium', 600: 'SemiBold',
           700: 'Bold', 800: 'ExtraBold', 900: 'Black'}
GENERIC_FONTS = {'sans-serif', 'serif', 'monospace', 'system-ui', 'cursive', 'fantasy', 'inherit', 'initial',
                 'ui-sans-serif', 'ui-serif', 'ui-monospace', '-apple-system', 'blinkmacsystemfont', 'segoe ui',
                 'roboto', 'helvetica neue', 'arial', 'helvetica', 'noto sans', 'apple color emoji',
                 'segoe ui emoji', 'segoe ui symbol', 'noto color emoji', 'var', 'unset'}


def get(url, ua=UA, limit=20_000_000):
    req = urllib.request.Request(url, headers={'User-Agent': ua, 'Accept': '*/*'})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read(limit), r.headers.get('Content-Type', '')


def hex6(h):
    h = h.lstrip('#').lower()
    if len(h) in (3, 4):
        h = ''.join(c * 2 for c in h[:3])
    return '#' + h[:6].upper()


def rgb_of(h):
    h = hex6(h)[1:]
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def rel_lum(h):
    def ch(c):
        c /= 255.0
        return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
    r, g, b = (ch(c) for c in rgb_of(h))
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast(a, b):
    la, lb = sorted((rel_lum(a), rel_lum(b)), reverse=True)
    return (la + 0.05) / (lb + 0.05)


def chroma(h):
    r, g, b = rgb_of(h)
    return max(r, g, b) - min(r, g, b)


# ------------------------------------------------------------------------------------------------ scan
def scan(url, out):
    os.makedirs(os.path.join(out, 'candidates'), exist_ok=True)
    page, _ = get(url)
    page = page.decode('utf-8', 'ignore')
    open(os.path.join(out, 'page.html'), 'w').write(page)
    css_urls = [urllib.parse.urljoin(url, html.unescape(h)) for h in
                re.findall(r'<link[^>]+rel=["\']?stylesheet["\']?[^>]*href=["\']([^"\']+)', page, re.I) +
                re.findall(r'<link[^>]+href=["\']([^"\']+)["\'][^>]*rel=["\']?stylesheet', page, re.I)]
    css_urls = list(dict.fromkeys(css_urls))
    css = '\n'.join(re.findall(r'<style[^>]*>(.*?)</style>', page, re.S | re.I))
    inline = ' '.join(re.findall(r'style=["\']([^"\']+)', page, re.I))
    google = []
    for cu in css_urls[:25]:
        if 'fonts.googleapis.com' in cu:
            google.append(cu)
            continue
        try:
            body, _ = get(cu)
            css += '\n' + body.decode('utf-8', 'ignore')
        except Exception as e:
            print('  css fail', cu, e, file=sys.stderr)
    text = css + '\n' + inline
    # colours: hex + rgb() + CSS custom properties, weighted by use count
    cols = collections.Counter(hex6(m) for m in re.findall(r'#(?:[0-9a-fA-F]{6}|[0-9a-fA-F]{3})\b', text))
    for r, g, b in re.findall(r'rgba?\(\s*(\d{1,3})[ ,]+(\d{1,3})[ ,]+(\d{1,3})', text):
        cols['#%02X%02X%02X' % (int(r), int(g), int(b))] += 1
    variables = {}
    for name, val in re.findall(r'(--[\w-]+)\s*:\s*([^;}{]+)', text):
        m = re.search(r'#(?:[0-9a-fA-F]{6}|[0-9a-fA-F]{3})\b', val)
        if m:
            variables.setdefault(name, hex6(m.group(0)))
    theme = re.search(r'<meta[^>]+name=["\']theme-color["\'][^>]+content=["\']([^"\']+)', page, re.I)
    # fonts
    fams = collections.Counter()
    for decl in re.findall(r'font-family\s*:\s*([^;}{]+)', text, re.I):
        for f in decl.split(','):
            f = f.strip().strip('"\'').strip()
            if f and f.lower() not in GENERIC_FONTS and not f.lower().startswith('var('):
                fams[f] += 1
    face = sorted(set(re.findall(r'@font-face\s*{[^}]*font-family\s*:\s*["\']?([^;"\']+)', text, re.I)))
    for g in google:
        for fam in re.findall(r'family=([^&:]+)', urllib.parse.unquote(g)):
            fams[fam.replace('+', ' ')] += 5
    # logos
    cands = []
    for tag in re.findall(r'<img[^>]+>', page, re.I):
        src = re.search(r'\bsrc=["\']([^"\']+)', tag)
        if src and re.search(r'logo|brand|header', tag, re.I):
            cands.append(urllib.parse.urljoin(url, html.unescape(src.group(1))))
    cands += [urllib.parse.urljoin(url, html.unescape(h)) for h in re.findall(
        r'<link[^>]+rel=["\'][^"\']*(?:icon|apple-touch-icon)[^"\']*["\'][^>]*href=["\']([^"\']+)', page, re.I)]
    og = re.search(r'<meta[^>]+property=["\']og:image["\'][^>]+content=["\']([^"\']+)', page, re.I)
    if og:
        cands.append(urllib.parse.urljoin(url, html.unescape(og.group(1))))
    cands = list(dict.fromkeys(cands))[:12]
    svgs = re.findall(r'<svg[^>]*>.*?</svg>', page, re.S | re.I)
    for i, s in enumerate(s for s in svgs if re.search(r'logo|brand', s[:400], re.I)):
        p = os.path.join(out, 'candidates', f'inline_{i}.svg')
        open(p, 'w').write(s if 'xmlns=' in s else s.replace('<svg', '<svg xmlns="http://www.w3.org/2000/svg"', 1))
    saved = []
    for i, c in enumerate(cands):
        ext = os.path.splitext(urllib.parse.urlparse(c).path)[1][:5] or '.bin'
        p = os.path.join(out, 'candidates', f'{i:02d}{ext}')
        try:
            data, _ = get(c)
            open(p, 'wb').write(data)
            saved.append({'url': c, 'file': p, 'bytes': len(data)})
        except Exception as e:
            saved.append({'url': c, 'error': str(e)})
    top = [{'hex': h, 'uses': n, 'chroma': chroma(h), 'lum': round(rel_lum(h), 3)} for h, n in cols.most_common(40)]
    rep = {'url': url, 'stylesheets': css_urls, 'google_fonts_links': google,
           'theme_color': theme.group(1) if theme else None, 'css_variables': variables,
           'colours_by_use': top,
           'brand_colour_guess': [c['hex'] for c in top if c['chroma'] > 60][:6],
           'neutrals_guess': [c['hex'] for c in top if c['chroma'] <= 25][:6],
           'font_families_by_use': fams.most_common(12), 'font_face_families': face,
           'logo_candidates': saved}
    json.dump(rep, open(os.path.join(out, 'scan.json'), 'w'), indent=1)
    print(json.dumps({k: rep[k] for k in ('theme_color', 'brand_colour_guess', 'neutrals_guess',
                                          'font_families_by_use', 'font_face_families')}, indent=1))
    print('candidates ->', os.path.join(out, 'candidates'), len(saved), '| full report ->', os.path.join(out, 'scan.json'))


# ------------------------------------------------------------------------------------------------ fonts
def fonts(specs, out):
    os.makedirs(out, exist_ok=True)
    n = 0
    for spec in specs:
        q = urllib.parse.quote(spec, safe=':;@,')
        css, _ = get(f'https://fonts.googleapis.com/css2?family={q}', ua='Wget/1.0')   # Wget UA -> TTF urls
        fam = spec.split(':')[0].replace('+', ' ').replace(' ', '')
        for block in re.findall(r'@font-face\s*{(.*?)}', css.decode(), re.S):
            italic = re.search(r'font-style:\s*(\w+)', block).group(1) == 'italic'
            w = int(re.search(r'font-weight:\s*(\d+)', block).group(1))
            url = re.search(r'url\((.*?)\)', block).group(1)
            name = f'{fam}-{WEIGHTS.get(w, w)}' + ('Italic' if italic else '') + '.ttf'
            data, _ = get(url)
            open(os.path.join(out, name), 'wb').write(data)
            n += 1
            print('  ', name)
    print(f'fonts -> {out} ({n} files)')


# ------------------------------------------------------------------------------------------------ logo
def logo(src, out, name='logo_full', on_dark=False, dark_lum=0.12):
    import numpy as np
    from PIL import Image
    os.makedirs(out, exist_ok=True)
    if src.lower().endswith('.svg'):
        import cairosvg
        tmp = os.path.join(out, name + '_4k.png')
        cairosvg.svg2png(url=src, write_to=tmp, output_width=4096)
        im = Image.open(tmp).convert('RGBA')
    else:
        im = Image.open(src).convert('RGBA')
    a = np.array(im)
    if a[..., 3].min() == 255:   # opaque raster: key out a flat light background
        bg = np.median(np.concatenate([a[0], a[-1], a[:, 0], a[:, -1]]), 0)[:3]
        dist = np.abs(a[..., :3].astype(np.int16) - bg.astype(np.int16)).max(-1)
        a[..., 3] = np.clip((dist - 8) * 12, 0, 255).astype(np.uint8)
        print('  note: opaque logo, background keyed out; ask the client for a transparent PNG/SVG')
        im = Image.fromarray(a)
    im = im.crop(im.getbbox())
    p = os.path.join(out, name + '.png')
    im.save(p)
    print('logo ->', p, im.size)
    if on_dark:   # derived: ink too dark to read on a dark background (rel. luminance < dark_lum) turns white
        b = np.array(im).astype(np.float32)
        c = b[..., :3] / 255.0
        lin = np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)
        dark = (lin @ np.array([0.2126, 0.7152, 0.0722]) < dark_lum) & (b[..., 3] > 0)
        b[dark, :3] = 250
        q = os.path.join(out, name + '_onDark.png')
        Image.fromarray(b.astype(np.uint8)).save(q)
        print('logo (derived, dark ink -> white; confirm with client) ->', q, int(dark.sum()), 'px changed')


# ------------------------------------------------------------------------------------------------ sheet
def sheet(project_json, out):
    import numpy as np  # noqa: F401
    from PIL import Image, ImageDraw, ImageFont
    pj = json.load(open(project_json))
    here = os.path.dirname(os.path.abspath(project_json))
    repo = os.path.abspath(os.path.join(here, '..', '..'))
    ws = os.environ.get('FOSTER_WS') or os.path.join(repo, pj.get('workspace', 'workspace3'))
    pal = pj.get('palette', {})
    W = 1600
    img = Image.new('RGB', (W, 1800), (245, 245, 245))
    d = ImageDraw.Draw(img)

    def font(name, size):
        fm = pj.get('font_map', {})
        fam, _, rest = name.partition('-')
        p = os.path.join(ws, 'fonts', (fm.get(fam, fam) + '-' + rest) + '.ttf')
        try:
            return ImageFont.truetype(p, size)
        except Exception:
            return ImageFont.load_default()
    y = 30
    d.text((40, y), f"{pj.get('project', '?')} brand kit", fill=(20, 20, 20), font=font('Nunito-Black', 56))
    y += 100
    for i, (k, v) in enumerate(pal.items()):
        x = 40 + (i % 6) * 255
        yy = y + (i // 6) * 200
        d.rounded_rectangle((x, yy, x + 230, yy + 120), 14, fill=rgb_of(v))
        d.text((x, yy + 128), f'{k}\n{v}', fill=(20, 20, 20), font=font('Poppins-SemiBold', 22))
    y += ((len(pal) + 5) // 6) * 200 + 20
    light = pal.get('IVORY', '#FFFFFF')
    dark = pal.get('INK', '#000000')
    rows = [(k, v, contrast(v, light), contrast(v, dark)) for k, v in pal.items()]
    d.text((40, y), 'contrast vs IVORY / vs INK  (body >= 4.5, hero >= 3.0)', fill=(20, 20, 20), font=font('Poppins-SemiBold', 26))
    y += 44
    for i, (k, v, cl, cd) in enumerate(rows):
        x = 40 + (i % 3) * 510
        yy = y + (i // 3) * 34
        d.text((x, yy), f'{k:<12} {cl:4.1f} / {cd:4.1f}', fill=(200, 0, 0) if max(cl, cd) < 4.5 else (20, 20, 20),
               font=font('Poppins-Regular', 24))
    y += ((len(rows) + 2) // 3) * 34 + 30
    for nm, sz in (('Nunito-Black', 120), ('Nunito-ExtraBold', 64), ('Poppins-SemiBold', 40), ('Caveat-Bold', 64)):
        d.text((40, y), f'{nm.split("-")[0]} -> {pj.get("font_map", {}).get(nm.split("-")[0], nm.split("-")[0])}',
               fill=(120, 120, 120), font=font('Poppins-Regular', 22))
        d.text((40, y + 26), 'Could you make room?', fill=rgb_of(pal.get('MAGENTA', '#222222')), font=font(nm, sz))
        y += sz + 60
    bx = 40
    for nm, bg in (('logo_full.png', (255, 255, 255)), ('logo_full_onDark.png', rgb_of(pal.get('NIGHT_1', '#1C0822')))):
        p = os.path.join(ws, 'brand', nm)
        if os.path.exists(p):
            lg = Image.open(p).convert('RGBA')
            lg.thumbnail((700, 260))
            card = Image.new('RGB', (740, 300), bg)
            card.paste(lg, ((740 - lg.width) // 2, (300 - lg.height) // 2), lg)
            img.paste(card, (bx, min(y, 1800 - 320)))
            bx += 780
    os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
    img.save(out)
    print('sheet ->', out)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest='cmd', required=True)
    s = sub.add_parser('scan')
    s.add_argument('url')
    s.add_argument('--out', required=True)
    f = sub.add_parser('fonts')
    f.add_argument('specs', nargs='+')
    f.add_argument('--out', required=True)
    lg = sub.add_parser('logo')
    lg.add_argument('src')
    lg.add_argument('--out', required=True)
    lg.add_argument('--name', default='logo_full')
    lg.add_argument('--on-dark', action='store_true')
    lg.add_argument('--dark-lum', type=float, default=0.12, help='ink below this rel. luminance turns white (0.12 ~ 3:1 on near-black)')
    c = sub.add_parser('contrast')
    c.add_argument('fg')
    c.add_argument('bg')
    sh = sub.add_parser('sheet')
    sh.add_argument('project_json')
    sh.add_argument('--out', required=True)
    a = ap.parse_args()
    if a.cmd == 'scan':
        scan(a.url, a.out)
    elif a.cmd == 'fonts':
        fonts(a.specs, a.out)
    elif a.cmd == 'logo':
        logo(a.src, a.out, a.name, a.on_dark, a.dark_lum)
    elif a.cmd == 'contrast':
        r = contrast(a.fg, a.bg)
        print(f'{r:.2f}:1  body(>=4.5) {"PASS" if r >= 4.5 else "FAIL"}  hero(>=3) {"PASS" if r >= 3 else "FAIL"}')
    elif a.cmd == 'sheet':
        sheet(a.project_json, a.out)


if __name__ == '__main__':
    main()
