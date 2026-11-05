"""Finish floret_app_15s.mp4: voiceover, bottom-left "One platform / Multiple markets" over a black gradient,
and the tagline under the end logo.

    MUSIC=bed.wav python3 floret/finish_app15.py <in.mp4> <voiceover.(wav|mp3)> <out.mp4>
    (VO_START=seconds to move the voice, SFX=1 to keep the video's own sound effects)
"""
import os, subprocess, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

SRC, VO, OUT = sys.argv[1:4]
W, H, FPS, SR = 1080, 1920, 30, 48000
DUR = 15.0
N = int(DUR * FPS)

VO_START = float(os.environ.get('VO_START', 0.5))    # from the opening, under "One platform / Multiple markets"
KEEP_SFX = os.environ.get('SFX') == '1'               # the video's own sound effects (off: music + voice only)
TEXT_IN, TEXT_OUT = 1.0, 9.6                           # bottom-left lines, gone before the phone fills that corner (~9.9 s)
TAG_IN = 13.1                                          # logo is fully drawn at ~13.0 s
GOLD = (227, 157, 54)                                  # the logo's gold
FONT_DIR = '/usr/share/fonts/opentype/inter'


def font(name, size):
    return ImageFont.truetype(os.path.join(FONT_DIR, name), size)


def clamp(x, a=0.0, b=1.0):
    return min(b, max(a, x))


def ease_out(x):
    return 1 - (1 - clamp(x)) ** 3


def text_layer(lines, anchor_xy, align, line_gap):
    """RGBA layer with text lines (text, font, colour) and a soft drop shadow; returns (layer, per-line boxes)."""
    layer = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    shadow = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    d, ds = ImageDraw.Draw(layer), ImageDraw.Draw(shadow)
    x0, y = anchor_xy
    boxes = []
    for text, f, col in lines:
        l, t, r, b = d.textbbox((0, 0), text, font=f)
        x = x0 if align == 'left' else (W - (r - l)) // 2 - l
        ds.text((x + 2, y + 4), text, font=f, fill=(0, 0, 0, 170))
        d.text((x, y), text, font=f, fill=(*col, 255))
        boxes.append((y + t, y + b))
        y += (b - t) + line_gap
    shadow = shadow.filter(ImageFilter.GaussianBlur(8))
    return Image.alpha_composite(shadow, layer), boxes


# bottom-left headline, two lines
L1, b1 = text_layer([('One platform', font('InterDisplay-Bold.otf', 84), (255, 255, 255))], (80, 1468), 'left', 0)
L2, b2 = text_layer([('Multiple markets', font('InterDisplay-Bold.otf', 84), GOLD)], (80, 1574), 'left', 0)
# tagline under the end logo (logo spans y 436-945), two centred lines
TAG, _ = text_layer([('Simplifying investments', font('Inter-SemiBold.otf', 50), (255, 255, 255)),
                     ('for millions of Pakistanis', font('Inter-SemiBold.otf', 50), (255, 255, 255))], (0, 1010), 'center', 18)
L1, L2, TAG = (np.asarray(x, np.float32) for x in (L1, L2, TAG))

# black gradient behind the bottom-left lines: clear above y=1080, ~75 % black at the first line, 92 % at the bottom
yy = np.arange(H, dtype=np.float32)[:, None, None]
grad = (np.clip((yy - 1080) / (1560 - 1080), 0, 1) ** 0.8) * 0.80 + np.clip((yy - 1560) / 360, 0, 1) * 0.12
xx = np.arange(W, dtype=np.float32)[None, :, None]
grad = grad * (1 - 0.30 * np.clip((xx - 700) / 380, 0, 1))  # a touch lighter at the far right


def over(frame, layer, alpha, dy=0):
    if alpha <= 0.001:
        return frame
    lay = np.roll(layer, int(round(dy)), axis=0) if dy else layer
    a = lay[..., 3:4] / 255 * alpha
    return frame * (1 - a) + lay[..., :3] * a


# ---------------------------------------------------------------- audio: the video's own sound effects + music bed + voiceover
music = np.frombuffer(subprocess.run(['ffmpeg', '-v', 'error', '-i', SRC, '-vn', '-ac', '2', '-ar', str(SR), '-f', 'f32le', '-'],
                                     capture_output=True, check=True).stdout, np.float32).reshape(-1, 2).copy()
music = np.pad(music, ((0, max(0, int(DUR * SR) - len(music))), (0, 0)))[:int(DUR * SR)]
vo = np.frombuffer(subprocess.run(['ffmpeg', '-v', 'error', '-i', VO, '-af',
                                   'silenceremove=start_periods=1:start_threshold=-50dB,areverse,'
                                   'silenceremove=start_periods=1:start_threshold=-50dB,afade=t=in:d=0.04,areverse,'
                                   'highpass=f=70,acompressor=threshold=-24dB:ratio=1.8:attack=10:release=150:makeup=1.5',
                                   '-ac', '1', '-ar', str(SR), '-f', 'f32le', '-'], capture_output=True, check=True).stdout, np.float32)
vo = vo / (np.abs(vo).max() + 1e-9) * 0.85
track = np.zeros(len(music), np.float32)
i0 = int(VO_START * SR)
track[i0:i0 + len(vo)] = vo[:len(track) - i0]
# music bed (floret/music_app15.py), if given: under the video's own sound effects, ducked ~7 dB under the voice
bed = np.zeros_like(music)
if os.environ.get('MUSIC'):
    bed = np.frombuffer(subprocess.run(['ffmpeg', '-v', 'error', '-i', os.environ['MUSIC'], '-ac', '2', '-ar', str(SR), '-f', 'f32le', '-'],
                                       capture_output=True, check=True).stdout, np.float32).reshape(-1, 2)
    bed = np.pad(bed, ((0, max(0, len(music) - len(bed))), (0, 0)))[:len(music)] * float(os.environ.get('MUSIC_GAIN', 0.58))
env = np.zeros(len(track), np.float32)
env[i0:i0 + len(vo)] = 1
k = int(0.25 * SR)
env = np.convolve(env, np.ones(k) / k, mode='same')
duck = (1 - 0.55 * env)[:, None]
mix = (music * (1 - 0.3 * env)[:, None] if KEEP_SFX else 0) + bed * duck + track[:, None]
# loudness to -14 LUFS (measured with ffmpeg's EBU R128 meter), then a soft limiter keeps peaks under -1 dBFS
wav = OUT + '.wav'
probe = subprocess.run(['ffmpeg', '-hide_banner', '-f', 'f32le', '-ar', str(SR), '-ac', '2', '-i', '-', '-af', 'ebur128', '-f', 'null', '-'],
                       input=mix.astype(np.float32).tobytes(), capture_output=True).stderr.decode()
lufs = float(probe.rsplit('I:', 1)[1].split('LUFS')[0])
mix = mix * 10 ** ((-14.0 - lufs) / 20)
ceil = 10 ** (-1.2 / 20)
mix = np.where(np.abs(mix) > 0.7 * ceil, np.sign(mix) * (0.7 * ceil + 0.3 * ceil * np.tanh((np.abs(mix) - 0.7 * ceil) / (0.3 * ceil))), mix)
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'f32le', '-ar', str(SR), '-ac', '2', '-i', '-', wav], input=mix.astype(np.float32).tobytes(), check=True)

# ---------------------------------------------------------------- video
dec = subprocess.Popen(['ffmpeg', '-v', 'error', '-i', SRC, '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'], stdout=subprocess.PIPE)
enc = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                        '-i', wav, '-map', '0:v', '-map', '1:a', '-c:v', 'libx264', '-preset', 'slow', '-crf', '15', '-pix_fmt', 'yuv420p',
                        '-ar', str(SR), '-c:a', 'aac', '-b:a', '256k', '-shortest',
                        '-movflags', '+faststart', OUT], stdin=subprocess.PIPE)
for i in range(N):
    buf = dec.stdout.read(W * H * 3)
    if len(buf) < W * H * 3:
        break
    t = i / FPS
    f = np.frombuffer(buf, np.uint8).reshape(H, W, 3).astype(np.float32)
    # bottom-left lines: gradient fades in first, lines slide up 40 px and fade in, staggered; all fade out together
    vis = clamp((t - TEXT_IN + 0.3) / 0.5) * clamp((TEXT_OUT - t) / 0.45)
    f = f * (1 - grad * vis)
    out_k = clamp((TEXT_OUT - t) / 0.45)
    for layer, delay in ((L1, 0.0), (L2, 0.18)):
        p = ease_out((t - TEXT_IN - delay) / 0.6)
        f = over(f, layer, p * out_k, dy=40 * (1 - p))
    # tagline under the logo
    p = ease_out((t - TAG_IN) / 0.7)
    f = over(f, TAG, p, dy=30 * (1 - p))
    enc.stdin.write(np.clip(f + 0.5, 0, 255).astype(np.uint8).tobytes())
enc.stdin.close()
enc.wait()
dec.wait()
os.remove(wav)
print(OUT)
