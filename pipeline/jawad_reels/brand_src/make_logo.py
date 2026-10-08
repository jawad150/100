"""make_logo.py - builds Jawad's wordmark SVGs (text outlined from the brand fonts) + committed PNG crops.

    cd pipeline/jawad_reels && python3 brand_src/make_logo.py      # needs <WS>/fonts (setup_workspace.py)

Writes brand_src/logo_full.svg (stacked lockup: serif-italic 'Jawad' in the flame gradient, glowing underline
stroke, '@jawad_mp4' grotesk signature), logo_mark.svg ('J' monogram in a thin flame ring), logo_wordmark.svg
(one line: 'JAWAD' grotesk + 'mp4' serif italic) and the 2048 px PNGs logo_mark.png, logo_wordmark.png,
logo_wordmark_onDark.png. Jawad has no official logo yet: this is a derived, house-style wordmark (fonts:
Instrument Serif Italic + Poppins, the faces measured from his covers). Replace it if he sends one.
"""
import os
import sys

from fontTools.pens.boundsPen import BoundsPen
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTFont
from PIL import Image, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import wsconf  # noqa: E402

FONTS = os.path.join(wsconf.workspace(), 'fonts')
SERIF = os.path.join(FONTS, 'InstrumentSerif-RegularItalic.ttf')
GROT = os.path.join(FONTS, 'Poppins-SemiBold.ttf')
GROT_M = os.path.join(FONTS, 'Poppins-Medium.ttf')
PAL = wsconf.project()['palette']
GOLD, FLAME, RED, AMBER, INK, IVORY = (PAL[k] for k in ('GOLD', 'FLAME', 'RED', 'AMBER', 'INK', 'IVORY'))


def text_path(font_file, text, px, x, y, tracking=0.0):
    """Outlined text: (svg path d, (x0, y0, x1, y1) bounds, advance width). Kerning from raqm (PIL)."""
    tt = TTFont(font_file)
    gs = tt.getGlyphSet()
    cmap = tt.getBestCmap()
    upm = tt['head'].unitsPerEm
    s = px / upm
    pf = ImageFont.truetype(font_file, upm, layout_engine=ImageFont.Layout.RAQM)
    pen, bp = SVGPathPen(gs), BoundsPen(gs)
    for i, ch in enumerate(text):
        xi = pf.getlength(text[:i + 1]) - pf.getlength(ch) + i * tracking * upm
        m = (s, 0, 0, -s, x + xi * s, y)
        gs[cmap[ord(ch)]].draw(TransformPen(pen, m))
        gs[cmap[ord(ch)]].draw(TransformPen(bp, m))
    adv = (pf.getlength(text) + (len(text) - 1) * tracking * upm) * s
    return pen.getCommands(), bp.bounds, adv


def svg(w, h, body, defs=''):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w:.1f} {h:.1f}" width="{w:.0f}" height="{h:.0f}">'
            f'<defs>{defs}</defs>{body}</svg>\n')


def flame_grad(gid, x0, y0, x1, y1):
    return (f'<linearGradient id="{gid}" gradientUnits="userSpaceOnUse" x1="{x0:.1f}" y1="{y0:.1f}" x2="{x1:.1f}" '
            f'y2="{y1:.1f}"><stop offset="0" stop-color="{GOLD}"/><stop offset="0.45" stop-color="{FLAME}"/>'
            f'<stop offset="1" stop-color="{RED}"/></linearGradient>')


def underline(x0, x1, y, thick, gid):
    """Tapered light stroke with a hot head on the right (the covers' glowing underline)."""
    xm = x0 + (x1 - x0) * 0.62
    d = (f'M{x0:.1f},{y:.1f} Q{xm:.1f},{y - thick * 1.6:.1f} {x1:.1f},{y - thick * 0.9:.1f} '
         f'Q{xm:.1f},{y + thick * 0.2:.1f} {x0:.1f},{y:.1f}Z')
    g = (f'<linearGradient id="{gid}" gradientUnits="userSpaceOnUse" x1="{x0:.1f}" y1="0" x2="{x1:.1f}" y2="0">'
         f'<stop offset="0" stop-color="{RED}" stop-opacity="0"/><stop offset="0.35" stop-color="{RED}"/>'
         f'<stop offset="0.8" stop-color="{FLAME}"/><stop offset="1" stop-color="{AMBER}"/></linearGradient>')
    head = f'<circle cx="{x1:.1f}" cy="{y - thick * 0.9:.1f}" r="{thick * 0.95:.1f}" fill="{AMBER}"/>'
    return f'<path d="{d}" fill="url(#{gid})"/>' + head, g


def logo_full():
    d1, b1, a1 = text_path(SERIF, 'Jawad', 420, 0, 0, tracking=-0.01)
    pad = 40
    ox, oy = pad - b1[0], pad - b1[1]
    d1, b1, a1 = text_path(SERIF, 'Jawad', 420, ox, oy, tracking=-0.01)
    uy = b1[3] + 46
    ul, ulg = underline(b1[0] + 10, b1[2] - 6, uy, 11, "ul")
    d2, b2, a2 = text_path(GROT_M, '@jawad_mp4', 92, 0, 0, tracking=0.04)
    hx = (b1[0] + b1[2]) / 2 - (b2[2] - b2[0]) / 2 - b2[0]
    hy = uy + 52 - b2[1]
    d2, b2, a2 = text_path(GROT_M, '@jawad_mp4', 92, hx, hy, tracking=0.04)
    w = max(b1[2], b2[2]) + pad
    h = b2[3] + pad
    defs = flame_grad('fl', b1[0], b1[1], b1[2], b1[3]) + ulg
    body = f'<path d="{d1}" fill="url(#fl)"/>' + ul + f'<path d="{d2}" fill="{INK}"/>'
    return svg(w, h, body, defs)


def logo_mark():
    R, sw = 460, 26
    c = R + sw + 20
    d, b, a = text_path(SERIF, 'J', 760, 0, 0)
    jx = c - (b[0] + b[2]) / 2
    jy = c - (b[1] + b[3]) / 2 + 10
    d, b, a = text_path(SERIF, 'J', 760, jx, jy)
    defs = flame_grad('fl', c - R, c - R, c + R, c + R) + flame_grad('rg', c + R, c - R, c - R, c + R)
    body = (f'<circle cx="{c}" cy="{c}" r="{R}" fill="none" stroke="url(#rg)" stroke-width="{sw}"/>'
            f'<path d="{d}" fill="url(#fl)"/>')
    return svg(2 * c, 2 * c, body, defs)


def logo_wordmark(grot_color):
    d1, b1, a1 = text_path(GROT, 'JAWAD', 300, 0, 0, tracking=0.10)
    pad = 30
    d1, b1, a1 = text_path(GROT, 'JAWAD', 300, pad - b1[0], pad + 260, tracking=0.10)
    d2, b2, a2 = text_path(SERIF, 'mp4', 330, 0, 0, tracking=-0.01)
    d2, b2, a2 = text_path(SERIF, 'mp4', 330, b1[2] + 70 - b2[0], b1[3], tracking=-0.01)
    w = b2[2] + pad
    h = max(b1[3], b2[3]) + pad
    defs = flame_grad('fl', b2[0], b2[1], b2[2], b2[3])
    body = f'<path d="{d1}" fill="{grot_color}"/><path d="{d2}" fill="url(#fl)"/>'
    return svg(w, h, body, defs)


def png(svg_path, out, width=2048):
    import cairosvg
    cairosvg.svg2png(url=svg_path, write_to=out, output_width=width)
    im = Image.open(out).convert('RGBA')
    im.crop(im.getbbox()).save(out)
    print('->', out, Image.open(out).size)


if __name__ == '__main__':
    for name, s in (('logo_full', logo_full()), ('logo_mark', logo_mark()), ('logo_wordmark', logo_wordmark(INK)),
                    ('logo_wordmark_onDark', logo_wordmark(IVORY))):
        p = os.path.join(HERE, name + '.svg')
        open(p, 'w').write(s)
        print('->', p)
    for name in ('logo_mark', 'logo_wordmark', 'logo_wordmark_onDark'):
        png(os.path.join(HERE, name + '.svg'), os.path.join(HERE, name + '.png'))
