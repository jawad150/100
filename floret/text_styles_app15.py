"""Three text-style variations for the 15 s Floret promo.

Top headline "One Platform for Multiple Markets" and bottom CTA "Start trading today with Floret Capitals", inside the
Reels safe area (top 250 px, bottom 420 px and the right-hand button column kept clear), plus the end tagline under the
logo. The audio is copied unchanged from an already-finished cut.

    python3 floret/text_styles_app15.py <clean source.mp4> <audio from.mp4> <out_dir> [styles: 1,2,3,4]
      1  Fintech Clean    Plus Jakarta Sans; white + electric blue; left-aligned, masked slide-up reveals, accent bar
      2  Editorial        DM Serif Display (roman + italic) over tracked Montserrat caps; ivory + champagne; soft blur-in
      3  Bold Impact      Poppins Black caps, navy on a brand-gold highlight wipe; CTA in a frosted card that springs up
      4  Serif Accent     light Inter over tall Instrument Serif with an italic brand-gold accent word; words rise in one by one
    Every style sits on deep black gradients (top ~92 %, bottom ~94 %) so the text reads over any frame.
"""
import os, subprocess, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

SRC, AUDIO, OUTDIR = sys.argv[1:4]
STYLES = [int(s) for s in (sys.argv[4] if len(sys.argv) > 4 else '1,2,3,4').split(',')]
W, H, FPS, N = 1080, 1920, 30, 450
FONTS = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'fonts')
GOLD, NAVY, WHITE = (227, 157, 54), (12, 27, 58), (255, 255, 255)
# colour scheme per style
BLUE, ICE = (76, 141, 255), (214, 226, 245)               # 1: white + electric blue (the app's Buy buttons)
IVORY, CHAMPAGNE = (244, 238, 226), (216, 180, 106)        # 2: ivory + champagne gold

TOP_IN, BOT_IN, OUT, TAG_IN = 0.6, 4.9, 10.7, 13.1      # seconds; out before the phone fills the frame; logo done at 13.0 s
SAFE_TOP, SAFE_BOTTOM, SAFE_LEFT, SAFE_RIGHT = 250, H - 420, 72, W - 130


def F(name, size):
    return ImageFont.truetype(os.path.join(FONTS, name + '.ttf'), size)


def clamp(x, a=0.0, b=1.0):
    return min(b, max(a, x))


def ease_out(x, p=3):
    return 1 - (1 - clamp(x)) ** p


def ease_back(x, s=1.6):
    x = clamp(x)
    return 1 + (s + 1) * (x - 1) ** 3 + s * (x - 1) ** 2


# ---------------------------------------------------------------- text rendering
def text_img(text, font, fill, tracking=0, shadow=True, pad=24):
    """Tight RGBA image of one line (optional letter tracking, soft drop shadow)."""
    asc, desc = font.getmetrics()
    widths = [font.getlength(c) for c in text]
    w = int(sum(widths) + tracking * (len(text) - 1)) + 2 * pad
    h = asc + desc + 2 * pad
    img = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    sh = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    d, ds = ImageDraw.Draw(img), ImageDraw.Draw(sh)
    x = pad
    if tracking == 0:
        d.text((pad, pad), text, font=font, fill=(*fill, 255))
        ds.text((pad + 2, pad + 4), text, font=font, fill=(0, 0, 0, 150))
    else:
        for c, cw in zip(text, widths):
            d.text((x, pad), c, font=font, fill=(*fill, 255))
            ds.text((x + 2, pad + 4), c, font=font, fill=(0, 0, 0, 150))
            x += cw + tracking
    if shadow:
        img = Image.alpha_composite(sh.filter(ImageFilter.GaussianBlur(7)), img)
    return img, pad, asc


class El:
    """A layer placed at (x, y) whose look over time comes from anim(t) -> dict(a, dx, dy, s, blur, wipe, reveal)."""
    def __init__(self, img, x, y, anim):
        self.img, self.x, self.y, self.anim = img, x, y, anim

    def draw(self, canvas, t):
        p = self.anim(t)
        a = p.get('a', 1.0)
        if a <= 0.003:
            return
        im = self.img
        s = p.get('s', 1.0)
        if abs(s - 1) > 0.002:
            im = im.resize((max(1, round(im.width * s)), max(1, round(im.height * s))), Image.BICUBIC)
        if p.get('blur', 0) > 0.3:
            im = im.filter(ImageFilter.GaussianBlur(p['blur']))
        if p.get('wipe', 1.0) < 0.999:                          # left-to-right wipe
            m = Image.new('L', im.size, 0)
            m.paste(255, (0, 0, round(im.width * clamp(p['wipe'])), im.height))
            im = im.copy(); im.putalpha(Image.composite(im.getchannel('A'), m, m))
        if p.get('reveal', 1.0) < 0.999:                        # masked slide-up: only show above the line's baseline box
            m = Image.new('L', im.size, 0)
            m.paste(255, (0, 0, im.width, round(im.height * clamp(p['reveal']))))
            im = im.copy(); im.putalpha(Image.composite(im.getchannel('A'), m, m))
        if a < 0.999:
            im = im.copy(); im.putalpha(im.getchannel('A').point(lambda v: int(v * a)))
        cx = self.x + self.img.width / 2 + p.get('dx', 0)
        cy = self.y + self.img.height / 2 + p.get('dy', 0)
        canvas.alpha_composite(im, (round(cx - im.width / 2), round(cy - im.height / 2)))


def window(t, t_in, dur, t_out=OUT - 0.15, out_dur=0.3):
    # text is gone by OUT + 0.15 s, while its gradient fades until OUT + 0.4 s (no ghosting over the bright phone)
    return ease_out((t - t_in) / dur), clamp((t_out + out_dur - t) / out_dur)


# ---------------------------------------------------------------- gradients (alpha maps), faded with their text
yy = np.arange(H, dtype=np.float32)[:, None]
TOP_GRAD = (np.clip(1 - (yy - 470) / (700 - 470), 0, 1) ** 1.4) * 0.92            # solid ~92 % black to y 470, fading out by 700
BOT_GRAD = (np.clip((yy - 1000) / (1290 - 1000), 0, 1) ** 1.2) * 0.94            # fading in from y 1000, ~94 % black from 1290


def build_style(n):
    els, top_dark, bot_dark = [], 1.0, 1.0
    if n == 1:      # ---------------------------------------- Fintech Clean (Plus Jakarta Sans)
        f_top, f_cta, f_cta2, f_tag = (F('plus-jakarta-sans-800-normal', 82), F('plus-jakarta-sans-700-normal', 52),
                                        F('plus-jakarta-sans-500-normal', 52), F('plus-jakarta-sans-700-normal', 46))
        bar = Image.new('RGBA', (78, 8), (*BLUE, 255))
        els.append(El(bar, SAFE_LEFT + 6, SAFE_TOP + 28,
                      lambda t: (lambda i, o: {'a': o, 'wipe': i})(*window(t, TOP_IN, 0.45))))
        y = SAFE_TOP + 44
        for k, (txt, col) in enumerate((('One Platform for', WHITE), ('Multiple Markets', BLUE))):
            img, pad, asc = text_img(txt, f_top, col)
            els.append(El(img, SAFE_LEFT - pad, y - pad,
                          lambda t, k=k: (lambda i, o: {'a': o * clamp(i * 3), 'dy': 46 * (1 - i), 'reveal': 0.35 + 0.65 * i})(
                              *window(t, TOP_IN + 0.15 + 0.13 * k, 0.6))))
            y += 96
        y = SAFE_BOTTOM - 150
        for k, (txt, f, col) in enumerate((('Start trading today', f_cta, WHITE), ('with Floret Capitals', f_cta2, ICE))):
            img, pad, asc = text_img(txt, f, col)
            els.append(El(img, SAFE_LEFT - pad, y - pad,
                          lambda t, k=k: (lambda i, o: {'a': o * clamp(i * 3), 'dy': 40 * (1 - i), 'reveal': 0.35 + 0.65 * i})(
                              *window(t, BOT_IN + 0.13 * k, 0.6))))
            y += 66
        arrow = Image.new('RGBA', (56, 40), (0, 0, 0, 0))            # drawn, so it never depends on a font glyph
        da = ImageDraw.Draw(arrow)
        da.rounded_rectangle((0, 16, 40, 24), 4, fill=(*BLUE, 255))
        da.polygon([(30, 4), (54, 20), (30, 36)], fill=(*BLUE, 255))
        cta2_w = text_img('with Floret Capitals', f_cta2, WHITE)[0].width - 48
        els.append(El(arrow, SAFE_LEFT + cta2_w + 18, SAFE_BOTTOM - 84 + 18,
                      lambda t: (lambda i, o: {'a': o * i, 'dx': -24 * (1 - i)})(*window(t, BOT_IN + 0.45, 0.5))))
        tag_lines = [('Simplifying investments', f_tag, WHITE, 0), ('for millions of Pakistanis', f_tag, ICE, 0)]
    elif n == 2:    # ---------------------------------------- Editorial (DM Serif Display + Montserrat)
        f_a, f_b = F('dm-serif-display-400-normal', 78), F('dm-serif-display-400-italic', 96)
        f_c1, f_c2, f_tag = F('montserrat-600-normal', 38), F('montserrat-800-normal', 38), F('dm-serif-display-400-italic', 54)
        y = SAFE_TOP + 20
        for k, (txt, f, col) in enumerate((('One Platform for', f_a, IVORY), ('Multiple Markets', f_b, CHAMPAGNE))):
            img, pad, asc = text_img(txt, f, col)
            els.append(El(img, (W - img.width) // 2 - 20, y - pad,
                          lambda t, k=k: (lambda i, o: {'a': o * i, 's': 1.06 - 0.06 * i, 'blur': 10 * (1 - i)})(
                              *window(t, TOP_IN + 0.25 * k, 0.9))))
            y += 92 if k == 0 else 0
        # thin gold rules flanking a small diamond under the headline
        rule = Image.new('RGBA', (200, 3), (*CHAMPAGNE, 220))
        for side in (-1, 1):
            els.append(El(rule, W // 2 - 20 - 100 + side * 125, SAFE_TOP + 250,
                          lambda t: (lambda i, o: {'a': o * i, 'wipe': i})(*window(t, TOP_IN + 0.6, 0.6))))
        dia = Image.new('RGBA', (16, 16), (0, 0, 0, 0)); ImageDraw.Draw(dia).polygon([(8, 0), (16, 8), (8, 16), (0, 8)], fill=(*CHAMPAGNE, 255))
        els.append(El(dia, W // 2 - 20 - 8, SAFE_TOP + 243, lambda t: (lambda i, o: {'a': o * i})(*window(t, TOP_IN + 0.8, 0.4))))
        y = SAFE_BOTTOM - 136
        for k, (txt, f, col) in enumerate((('START TRADING TODAY', f_c1, IVORY), ('WITH FLORET CAPITALS', f_c2, CHAMPAGNE))):
            img, pad, asc = text_img(txt, f, col, tracking=7)
            els.append(El(img, (W - img.width) // 2 - 20, y - pad,
                          lambda t, k=k: (lambda i, o: {'a': o * i, 's': 0.94 + 0.06 * i, 'blur': 6 * (1 - i)})(
                              *window(t, BOT_IN + 0.2 * k, 0.8))))
            y += 62
        line = Image.new('RGBA', (120, 2), (*CHAMPAGNE, 200))
        els.append(El(line, (W - 120) // 2 - 20, SAFE_BOTTOM - 162, lambda t: (lambda i, o: {'a': o * i, 'wipe': i})(*window(t, BOT_IN, 0.6))))
        tag_lines = [('Simplifying investments', f_tag, IVORY, 0), ('for millions of Pakistanis', f_tag, CHAMPAGNE, 0)]
    elif n == 4:    # ---------------------------------------- Serif Accent (Inter + Instrument Serif)
        sans = lambda size: ImageFont.truetype('/usr/share/fonts/opentype/inter/Inter-Regular.otf', size)
        roman = lambda size: F('instrument-serif-400-normal', size)
        ital = lambda size: F('instrument-serif-400-italic', size)

        def words(runs, x, base_y, t_in, max_w=SAFE_RIGHT - SAFE_LEFT):
            # one line of mixed runs on a shared baseline; each word rises in through a mask, staggered
            size = runs[0][1]
            while True:
                fonts = [(txt, (roman if kind == 'r' else ital if kind == 'i' else sans)(size), col) for txt, _, col, kind in
                         [(r[0], r[1], r[2], r[3]) for r in runs]]
                total = sum(f.getlength(txt) for txt, f, _ in fonts)
                if total <= max_w or size < 40:
                    break
                size -= 4
                runs = [(r[0], size, r[2], r[3]) for r in runs]
            k = 0
            for txt, f, col in fonts:
                for wi, w in enumerate(txt.split(' ')):
                    if not w:
                        continue
                    img, pad, asc = text_img(w, f, col)
                    els.append(El(img, x - pad, base_y - asc - pad,
                                  lambda t, k=k: (lambda i, o: {'a': o * clamp(i * 2.5), 'dy': 34 * (1 - i), 'reveal': 0.45 + 0.55 * i})(
                                      *window(t, t_in + 0.09 * k, 0.6))))
                    x += f.getlength(w + ' ')
                    k += 1
            return size

        words([('One Platform for', 54, WHITE, 's')], SAFE_LEFT, SAFE_TOP + 70, TOP_IN)
        words([('Multiple', 132, WHITE, 'r'), ('Markets', 132, GOLD, 'i')], SAFE_LEFT, SAFE_TOP + 196, TOP_IN + 0.25)
        words([('Start trading today', 48, WHITE, 's')], SAFE_LEFT, SAFE_BOTTOM - 136, BOT_IN)
        words([('with Floret', 104, WHITE, 'r'), ('Capitals', 104, GOLD, 'i')], SAFE_LEFT, SAFE_BOTTOM - 38, BOT_IN + 0.2)
        tag_lines = [('Simplifying investments', roman(64), WHITE, 0), ('for millions of Pakistanis', ital(64), GOLD, 0)]
    else:           # ---------------------------------------- Bold Impact (Poppins)
        f_1, f_2 = F('poppins-800-normal', 60), F('poppins-900-normal', 74)
        f_c1, f_c2, f_tag = F('poppins-600-normal', 48), F('poppins-800-normal', 48), F('poppins-600-normal', 44)
        img1, pad1, _ = text_img('ONE PLATFORM FOR', f_1, WHITE, tracking=2)
        els.append(El(img1, (W - img1.width) // 2 - 20, SAFE_TOP + 20 - pad1,
                      lambda t: (lambda i, o: {'a': o * clamp(i * 2), 's': 0.7 + 0.3 * ease_back((t - TOP_IN) / 0.55)})(
                          *window(t, TOP_IN, 0.55))))
        img2, pad2, asc2 = text_img('MULTIPLE MARKETS', f_2, NAVY, tracking=1, shadow=False)
        box = Image.new('RGBA', (img2.width - 2 * pad2 + 44, asc2 + 34), (0, 0, 0, 0))
        ImageDraw.Draw(box).rounded_rectangle((0, 0, box.width - 1, box.height - 1), 14, fill=(*GOLD, 255))
        bx, by = (W - box.width) // 2 - 20, SAFE_TOP + 112
        els.append(El(box, bx, by, lambda t: (lambda i, o: {'a': o, 'wipe': i})(*window(t, TOP_IN + 0.35, 0.45))))
        els.append(El(img2, bx + 22 - pad2, by + 8 - pad2 + 6,
                      lambda t: (lambda i, o: {'a': o * i, 'dy': 18 * (1 - i)})(*window(t, TOP_IN + 0.6, 0.4))))
        # frosted card for the CTA
        c1, p1, a1 = text_img('Start trading today', f_c1, WHITE)
        c2, p2, a2 = text_img('with Floret Capitals', f_c2, GOLD)
        cw, ch = max(c1.width, c2.width) - 2 * p1 + 96, 196
        card = Image.new('RGBA', (cw, ch), (0, 0, 0, 0))
        dc = ImageDraw.Draw(card)
        dc.rounded_rectangle((0, 0, cw - 1, ch - 1), 34, fill=(14, 26, 54, 205), outline=(*GOLD, 200), width=3)
        card.alpha_composite(c1, (48 - p1, 30 - p1))
        card.alpha_composite(c2, (48 - p2, 30 + 70 - p2))
        cx, cy = (W - cw) // 2 - 20, SAFE_BOTTOM - ch - 4
        els.append(El(card, cx, cy, lambda t: (lambda i, o: {'a': o * clamp(i * 2.5), 'dy': 70 * (1 - ease_back((t - BOT_IN) / 0.7))})(
            *window(t, BOT_IN, 0.7))))
        els.append(('blur_card', (cx, cy, cw, ch)))
        tag_lines = [('SIMPLIFYING INVESTMENTS', f_tag, WHITE, 2), ('FOR MILLIONS OF PAKISTANIS', f_tag, GOLD, 2)]
        bot_dark = 0.85                                         # the frosted card adds contrast on top
    # end tagline under the logo (logo spans y 436-945)
    y = 1010
    for k, (txt, f, col, tr) in enumerate(tag_lines):
        img, pad, asc = text_img(txt, f, col, tracking=tr)
        els.append(El(img, (W - img.width) // 2, y - pad,
                      lambda t, k=k: {'a': ease_out((t - TAG_IN - 0.15 * k) / 0.7), 'dy': 28 * (1 - ease_out((t - TAG_IN - 0.15 * k) / 0.7))}))
        y += 70
    return els, top_dark, bot_dark


def render(n):
    els, top_dark, bot_dark = build_style(n)
    blur_cards = [e[1] for e in els if isinstance(e, tuple)]
    els = [e for e in els if not isinstance(e, tuple)]
    out = os.path.join(OUTDIR, f'floret_app_15s_style{n}.mp4')
    dec = subprocess.Popen(['ffmpeg', '-v', 'error', '-i', SRC, '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'], stdout=subprocess.PIPE)
    enc = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                            '-i', AUDIO, '-map', '0:v', '-map', '1:a', '-c:v', 'libx264', '-preset', 'slow', '-crf', '15',
                            '-pix_fmt', 'yuv420p', '-c:a', 'copy', '-movflags', '+faststart', out], stdin=subprocess.PIPE)
    for i in range(N):
        buf = dec.stdout.read(W * H * 3)
        if len(buf) < W * H * 3:
            break
        t = i / FPS
        f = np.frombuffer(buf, np.uint8).reshape(H, W, 3).astype(np.float32)
        top_v = clamp((t - TOP_IN + 0.3) / 0.6) * clamp((OUT + 0.4 - t) / 0.4)
        bot_v = clamp((t - BOT_IN + 0.3) / 0.6) * clamp((OUT + 0.4 - t) / 0.4)
        f *= (1 - TOP_GRAD * top_dark * top_v - BOT_GRAD * bot_dark * bot_v)[..., None]
        canvas = Image.fromarray(np.clip(f + 0.5, 0, 255).astype(np.uint8)).convert('RGBA')
        for (x, y, w, h) in blur_cards:                         # frosted glass: blur what is behind the card
            if bot_v > 0.01:
                region = canvas.crop((x, y, x + w, y + h)).filter(ImageFilter.GaussianBlur(18))
                m = Image.new('L', (w, h), 0)
                ImageDraw.Draw(m).rounded_rectangle((0, 0, w - 1, h - 1), 34, fill=int(255 * bot_v))
                canvas.paste(region, (x, y), m)
        for e in els:
            e.draw(canvas, t)
        enc.stdin.write(canvas.convert('RGB').tobytes())
    enc.stdin.close(); enc.wait(); dec.wait()
    print(out, flush=True)


if __name__ == '__main__':
    if os.environ.get('STILLS'):
        # quick preview: STILLS=2.0,6.5,14 -> PNG frames per style
        ts = [float(x) for x in os.environ['STILLS'].split(',')]
        for n in STYLES:
            els, top_dark, bot_dark = build_style(n)
            blur_cards = [e[1] for e in els if isinstance(e, tuple)]
            els = [e for e in els if not isinstance(e, tuple)]
            for t in ts:
                raw = subprocess.run(['ffmpeg', '-v', 'error', '-ss', str(t), '-i', SRC, '-frames:v', '1', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'],
                                     capture_output=True).stdout
                f = np.frombuffer(raw, np.uint8).reshape(H, W, 3).astype(np.float32)
                top_v = clamp((t - TOP_IN + 0.3) / 0.6) * clamp((OUT + 0.4 - t) / 0.4)
                bot_v = clamp((t - BOT_IN + 0.3) / 0.6) * clamp((OUT + 0.4 - t) / 0.4)
                f *= (1 - TOP_GRAD * top_dark * top_v - BOT_GRAD * bot_dark * bot_v)[..., None]
                canvas = Image.fromarray(np.clip(f + 0.5, 0, 255).astype(np.uint8)).convert('RGBA')
                for (x, y, w, h) in blur_cards:
                    if bot_v > 0.01:
                        region = canvas.crop((x, y, x + w, y + h)).filter(ImageFilter.GaussianBlur(18))
                        m = Image.new('L', (w, h), 0)
                        ImageDraw.Draw(m).rounded_rectangle((0, 0, w - 1, h - 1), 34, fill=int(255 * bot_v))
                        canvas.paste(region, (x, y), m)
                for e in els:
                    e.draw(canvas, t)
                canvas.convert('RGB').save(os.path.join(OUTDIR, f'style{n}_{t:05.2f}.png'))
    else:
        for n in STYLES:
            render(n)
