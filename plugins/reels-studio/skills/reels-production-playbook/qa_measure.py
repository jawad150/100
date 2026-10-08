#!/usr/bin/env python3
"""qa_measure.py: objective QA measurements for 9:16 reels (reels-studio plugin). Read-only on its inputs.

Needs ffmpeg/ffprobe on PATH and python3 with numpy, opencv-python(-headless) and pillow (the toolkit venv).

    probe  VIDEO [--dur 26] [--fps 30] [--size 1080x1920] [--max-mb 100]   spec check: codec, profile, pix_fmt,
           size, fps, counted frames vs dur*fps, bt709 tags, AAC 48 kHz, +faststart (moov before mdat), MB, loudness
    sheets VIDEO OUTDIR [--fps 5]                 contact sheets (10x4 tiles, timestamps) -> OUTDIR/sheet_NN.jpg
    strips VIDEO OUTDIR --at 2.5,5.5 [--span 0.4] [--full]
                                                  every frame within +-span s of each time -> OUTDIR/strip_<t>.jpg
                                                  (--full also writes full-res PNGs to OUTDIR/t<t>/)
    frame  VIDEO T OUT.png                        the exact frame round(T * fps) at full resolution
    luma   VIDEO [--from A] [--to B]              per-frame signalstats YMIN/YAVG; flags one-frame black lifts
    snaps  VIDEO [--from A] [--to B]              global motion per frame (phase correlation); flags 1-frame spikes
    roi    VIDEO X0 Y0 X1 Y1 [--from A] [--to B]  mean luma of a region per frame; flags one-frame steps (glow
                                                  pops at text hand-offs, local flashes, exits that vanish in 1 frame)
    freeze VIDEO                                  duplicate frames (mpdecimate) grouped into runs
    guides IMAGE OUT.png                          draws the 1080x1920 safe-zone lines on a frame
    ink    IMAGE X0 Y0 X1 Y1 '#RRGGBB' [--tol 40] ink box of one text colour inside a ROI + margins to the lines
    cues   VIDEO CUES_JSON [--win 0.06] [--offset A]  audio onset nearest each align='hit' cue (ms and frames);
                                                  --offset A: VIDEO is a range render that starts at reel time A
    audio  MEDIA [--spec OUT.png]                 EBU R128 integrated / LRA / true peak (+ spectrogram)

Flags are prompts to LOOK, not verdicts: hard cuts legitimately change YMIN and produce motion spikes.
"""
import argparse
import json
import os
import re
import struct
import subprocess
import sys

SAFE = dict(x0=70, x1=1010, y0=230, y1=1480, cta=1600, bottom=1620, col_x=930, col_y0=1050, col_y1=1700)


def run(cmd, check=True):
    r = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if check and r.returncode != 0:
        sys.exit('command failed: %s\n%s' % (' '.join(cmd), r.stderr[-2000:]))
    return r


def ratio(s):
    n, _, d = str(s).partition('/')
    return float(n) / float(d or 1)


def fps_of(path):
    return ratio(json.loads(run(['ffprobe', '-v', 'error', '-select_streams', 'v:0', '-show_entries',
                                 'stream=r_frame_rate', '-of', 'json', path]).stdout)['streams'][0]['r_frame_rate'])


def atoms(path):
    out = []
    with open(path, 'rb') as f:
        while True:
            h = f.read(8)
            if len(h) < 8:
                break
            size, typ = struct.unpack('>I4s', h)
            if size == 1:
                size = struct.unpack('>Q', f.read(8))[0]
                f.seek(size - 16, 1)
            elif size == 0:
                out.append(typ.decode('latin1'))
                break
            else:
                f.seek(size - 8, 1)
            out.append(typ.decode('latin1'))
    return out


def loudness(path):
    r = run(['ffmpeg', '-nostats', '-hide_banner', '-i', path, '-map', '0:a:0', '-af',
             'ebur128=peak=true:framelog=quiet', '-f', 'null', '-'], check=False)
    g = lambda k: (re.findall(r'^\s+%s:\s+(-?[\d.]+|-inf)' % k, r.stderr, re.M) or [None])[-1]
    return dict(I=g('I'), LRA=g('LRA'), TP=g('Peak'))


def cmd_probe(a):
    j = json.loads(run(['ffprobe', '-v', 'error', '-count_frames', '-show_entries',
                        'stream=codec_type,codec_name,profile,width,height,pix_fmt,r_frame_rate,nb_read_frames,'
                        'color_space,color_primaries,color_transfer,sample_rate,channels,bit_rate:format=duration,'
                        'size,bit_rate', '-of', 'json', a.video]).stdout)
    v = next((s for s in j['streams'] if s['codec_type'] == 'video'), {})
    au = next((s for s in j['streams'] if s['codec_type'] == 'audio'), None)
    w, h = map(int, a.size.split('x'))
    dur = float(j['format']['duration'])
    mb = int(j['format']['size']) / 1e6
    n = int(v.get('nb_read_frames', 0))
    order = atoms(a.video)
    checks = [
        ('h264 High', v.get('codec_name') == 'h264' and v.get('profile') == 'High', '%s %s' % (v.get('codec_name'), v.get('profile'))),
        ('yuv420p', v.get('pix_fmt') == 'yuv420p', v.get('pix_fmt')),
        ('size %s' % a.size, (v.get('width'), v.get('height')) == (w, h), '%sx%s' % (v.get('width'), v.get('height'))),
        ('fps %g' % a.fps, abs(ratio(v.get('r_frame_rate', '0/1')) - a.fps) < 1e-3, v.get('r_frame_rate')),
        ('bt709 tags', all(v.get(k) == 'bt709' for k in ('color_space', 'color_primaries', 'color_transfer')),
         '%s/%s/%s' % (v.get('color_space'), v.get('color_primaries'), v.get('color_transfer'))),
        ('faststart', 'moov' in order and 'mdat' in order and order.index('moov') < order.index('mdat'), ','.join(order)),
        ('audio AAC 48 kHz', bool(au) and au.get('codec_name') == 'aac' and au.get('sample_rate') == '48000',
         '%s %s Hz %s ch' % (au.get('codec_name'), au.get('sample_rate'), au.get('channels')) if au else 'no audio'),
    ]
    if a.dur:
        exp = int(round(a.dur * a.fps))
        checks.append(('frames == %d' % exp, n == exp, str(n)))
        checks.append(('duration %.3f' % a.dur, abs(dur - a.dur) < 0.5 / a.fps + 0.03, '%.3f' % dur))
    if a.max_mb:
        checks.append(('< %g MB' % a.max_mb, mb < a.max_mb, '%.1f MB' % mb))
    for name, ok, val in checks:
        print('%-4s %-18s %s' % ('PASS' if ok else 'FAIL', name, val))
    print('info duration %.3f s, %d frames, %.1f MB, video %.1f Mbps' % (dur, n, mb, int(v.get('bit_rate') or 0) / 1e6))
    if au:
        print('info loudness', loudness(a.video))


def label_filter(t0, n0=None):
    txt = "%%{pts\\:flt\\:%.4f} s" % t0
    if n0 is not None:                               # exact frame number of each tile
        txt = "f%%{eif\\:n+%d\\:d}  " % n0 + txt
    return "drawtext=text='%s':x=6:y=6:fontsize=18:fontcolor=yellow:box=1:boxcolor=black@0.6" % txt


def ff_tiles(video, ss, nframes, fps, vf_core, out, n0):
    for vf in (vf_core.replace('LABEL', label_filter(max(ss, 0), n0)), vf_core.replace('LABEL,', '')):
        r = run(['ffmpeg', '-v', 'error', '-y', '-ss', '%.4f' % max(ss, 0), '-t', '%.4f' % ((nframes - 0.5) / fps),
                 '-i', video, '-vf', vf, '-frames:v', '1', '-q:v', '3', out], check=False)
        if r.returncode == 0:
            return out
    sys.exit(r.stderr[-1500:])


def cmd_sheets(a):
    os.makedirs(a.outdir, exist_ok=True)
    vf = 'fps=%g,scale=216:-2,LABEL,tile=10x4' % a.fps
    for vfx in (vf.replace('LABEL', label_filter(0)), vf.replace('LABEL,', '')):
        r = run(['ffmpeg', '-v', 'error', '-y', '-i', a.video, '-vf', vfx, '-q:v', '3',
                 os.path.join(a.outdir, 'sheet_%02d.jpg')], check=False)
        if r.returncode == 0:
            break
    print('\n'.join(sorted(os.path.join(a.outdir, f) for f in os.listdir(a.outdir) if f.startswith('sheet_'))))


def cmd_strips(a):
    fps = fps_of(a.video)
    os.makedirs(a.outdir, exist_ok=True)
    for t in [float(x) for x in a.at.split(',') if x.strip()]:
        n0 = max(0, int(round((t - a.span) * fps)))
        n = int(round(2 * a.span * fps)) + 1
        cols = 6 if n > 25 else 5
        rows = -(-n // cols)
        ss = (n0 - 0.25) / fps                       # lands exactly on frame n0
        out = os.path.join(a.outdir, 'strip_%07.3f.jpg' % t)
        ff_tiles(a.video, ss, n, fps, 'scale=270:-2,LABEL,tile=%dx%d' % (cols, rows), out, n0)
        print(out)
        if a.full:
            d = os.path.join(a.outdir, 't%07.3f' % t)
            os.makedirs(d, exist_ok=True)
            run(['ffmpeg', '-v', 'error', '-y', '-ss', '%.4f' % max(ss, 0), '-i', a.video, '-frames:v', str(n),
                 '-start_number', str(n0), os.path.join(d, 'f_%05d.png')])
            print(d + '/f_%05d.png (frame numbers)')


def cmd_frame(a):
    fps = fps_of(a.video)
    n = int(round(a.t * fps))
    run(['ffmpeg', '-v', 'error', '-y', '-ss', '%.4f' % max((n - 0.25) / fps, 0), '-i', a.video, '-frames:v', '1',
         a.out])
    print('%s (frame %d, t=%.3f)' % (a.out, n, n / fps))


def trim_args(a):
    """Input-side -ss/-t (both before -i): an output -t lets the filtergraph run past --to."""
    args = []
    if a.from_ is not None:
        args += ['-ss', '%.4f' % a.from_]
    if a.to is not None:
        args += ['-t', '%.4f' % (a.to - (a.from_ or 0.0))]
    args += ['-i', a.video]
    return args


def cmd_luma(a):
    r = run(['ffmpeg', '-v', 'error', *trim_args(a), '-map', '0:v:0', '-vf',
             'signalstats,metadata=mode=print:file=-', '-f', 'null', '-'])
    off = a.from_ or 0.0
    rows, cur = [], None
    for line in r.stdout.splitlines():
        m = re.match(r'frame:\s*\d+\s+pts:\s*\S+\s+pts_time:\s*(\S+)', line)
        if m:
            cur = {'t': float(m.group(1)) + off}
            rows.append(cur)
        elif cur is not None and '=' in line:
            k, v = line.split('=', 1)
            cur[k.split('.')[-1]] = float(v)
    if a.to is not None:
        rows = [r for r in rows if r['t'] < a.to - 1e-6]
    if not rows:
        sys.exit('no frames')
    ymin = [r['YMIN'] for r in rows]
    yavg = [r['YAVG'] for r in rows]
    print('frames %d  YMIN %.0f..%.0f  YAVG %.1f..%.1f' % (len(rows), min(ymin), max(ymin), min(yavg), max(yavg)))
    for i in range(1, len(rows) - 1):
        lift = ymin[i] - max(ymin[i - 1], ymin[i + 1])
        if lift >= 6 or ymin[i] - ymin[i - 1] >= 10:
            print('CHECK t=%.3f  YMIN %.0f > %.0f > %.0f   YAVG %.1f > %.1f > %.1f' % (
                rows[i]['t'], ymin[i - 1], ymin[i], ymin[i + 1], yavg[i - 1], yavg[i], yavg[i + 1]))


def read_gray(a, scale=(270, 480)):
    import cv2
    import numpy as np
    cap = cv2.VideoCapture(a.video)
    fps = cap.get(cv2.CAP_PROP_FPS)
    f0 = int(round((a.from_ or 0.0) * fps))
    f1 = int(round(a.to * fps)) if a.to is not None else int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    cap.set(cv2.CAP_PROP_POS_FRAMES, f0)
    for f in range(f0, f1):
        ok, im = cap.read()
        if not ok:
            break
        yield f, f / fps, cv2.resize(cv2.cvtColor(im, cv2.COLOR_BGR2GRAY), scale,
                                     interpolation=cv2.INTER_AREA).astype(np.float32)


def cmd_snaps(a):
    import cv2
    import numpy as np
    prev, d, ts = None, [], []
    win = cv2.createHanningWindow((270, 480), cv2.CV_32F)
    for f, t, g in read_gray(a):
        if prev is not None:
            (dx, dy), _ = cv2.phaseCorrelate(prev, g, win)
            d.append(4.0 * float(np.hypot(dx, dy)))   # back to 1080-wide px
            ts.append(t)
        prev = g
    for i in range(1, len(d) - 1):
        if d[i] > 3 * max(d[i - 1], d[i + 1], 2.0):
            print('CHECK t=%.3f  %.0f px/frame vs neighbours %.0f / %.0f (a cut, or a snap?)' % (
                ts[i], d[i], d[i - 1], d[i + 1]))
    if d:
        print('frames %d  max global motion %.0f px/frame at t=%.3f' % (len(d) + 1, max(d), ts[int(np.argmax(d))]))


def cmd_roi(a):
    import cv2
    import numpy as np
    cap = cv2.VideoCapture(a.video)
    fps = cap.get(cv2.CAP_PROP_FPS)
    f0 = int(round((a.from_ or 0.0) * fps))
    f1 = int(round(a.to * fps)) if a.to is not None else int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    cap.set(cv2.CAP_PROP_POS_FRAMES, f0)
    ys = []
    for f in range(f0, f1):
        ok, im = cap.read()
        if not ok:
            break
        g = cv2.cvtColor(im[a.y0:a.y1, a.x0:a.x1], cv2.COLOR_BGR2GRAY).astype(np.float32)
        ys.append((f, float(g.mean())))
    d = [ys[i + 1][1] - ys[i][1] for i in range(len(ys) - 1)]
    for i in range(1, len(d) - 1):
        if abs(d[i]) > 4 and abs(d[i]) > 3 * max(abs(d[i - 1]), abs(d[i + 1]), 1.0):
            f = ys[i + 1][0]
            print('CHECK frame %d (t=%.3f): mean luma %.1f -> %.1f (neighbour steps %+.1f / %+.1f)' % (
                f, f / fps, ys[i][1], ys[i + 1][1], d[i - 1], d[i + 1]))
    if a.csv:
        with open(a.csv, 'w') as fh:
            fh.writelines('%d,%.4f,%.2f\n' % (f, f / fps, y) for f, y in ys)
        print(a.csv)
    print('frames %d  mean luma %.1f..%.1f' % (len(ys), min(y for _, y in ys), max(y for _, y in ys)))


def cmd_freeze(a):
    r = run(['ffmpeg', '-hide_banner', '-nostats', '-loglevel', 'debug', '-i', a.video, '-map', '0:v:0', '-vf',
             'mpdecimate', '-f', 'null', '-'], check=False)
    ts = [float(x) for x in re.findall(r'mpdecimate.* drop pts:\S+ pts_time:(\S+)', r.stderr)]
    runs = []
    for t in ts:
        if runs and t - runs[-1][1] < 0.05:
            runs[-1][1] = t
        else:
            runs.append([t, t])
    print('%d duplicate frames' % len(ts))
    for t0, t1 in runs:
        print('  %.3f - %.3f s (%d frames)' % (t0, t1, int(round((t1 - t0) * 30)) + 1))


def cmd_guides(a):
    from PIL import Image, ImageDraw
    img = Image.open(a.image).convert('RGB')
    d = ImageDraw.Draw(img)
    for x in (SAFE['x0'], SAFE['x1']):
        d.line([(x, 0), (x, img.height)], fill=(0, 255, 255), width=2)
    for y in (SAFE['y0'], SAFE['y1']):
        d.line([(0, y), (img.width, y)], fill=(0, 255, 255), width=2)
    d.line([(0, SAFE['cta']), (img.width, SAFE['cta'])], fill=(255, 200, 0), width=2)
    d.line([(0, SAFE['bottom']), (img.width, SAFE['bottom'])], fill=(255, 0, 0), width=2)
    d.rectangle([SAFE['col_x'], SAFE['col_y0'], img.width - 1, SAFE['col_y1']], outline=(255, 0, 255), width=3)
    img.save(a.out)
    print(a.out, '(cyan key-copy box, amber CTA limit y1600, red bottom-300 line, magenta like/share column)')


def cmd_ink(a):
    import numpy as np
    from PIL import Image
    im = np.asarray(Image.open(a.image).convert('RGB'), np.float32)
    h = a.hex.lstrip('#')
    col = np.array([int(h[i:i + 2], 16) for i in (0, 2, 4)], np.float32)
    roi = im[a.y0:a.y1, a.x0:a.x1]
    m = np.linalg.norm(roi - col, axis=2) < a.tol
    ys, xs = np.nonzero(m)
    if not len(xs):
        sys.exit('no pixels within %g of %s in the ROI: sample the text colour from the frame' % (a.tol, a.hex))
    bx0, bx1, by0, by1 = a.x0 + xs.min(), a.x0 + xs.max(), a.y0 + ys.min(), a.y0 + ys.max()
    print('ink box x %d..%d  y %d..%d  (%d px, %d px tall)' % (bx0, bx1, by0, by1, m.sum(), by1 - by0 + 1))
    print('margins (negative = violation): left %+d  right %+d  top %+d  bottom-1480 %+d  cta-1600 %+d' % (
        bx0 - SAFE['x0'], SAFE['x1'] - bx1, by0 - SAFE['y0'], SAFE['y1'] - by1, SAFE['cta'] - by1))
    if by1 >= SAFE['col_y0'] and by0 <= SAFE['col_y1']:
        print('like/share column: right edge margin to x 930: %+d' % (SAFE['col_x'] - bx1))


def cmd_cues(a):
    import numpy as np
    raw = run_bytes(['ffmpeg', '-v', 'error', '-i', a.video, '-vn', '-ac', '1', '-ar', '48000', '-f', 'f32le', '-'])
    x = np.frombuffer(raw, np.float32)
    hop = 240                                         # 5 ms
    e = np.sqrt(np.convolve(x * x, np.ones(hop) / hop, 'same')[::hop] + 1e-12)
    db = 20 * np.log10(e)
    on = np.maximum(np.diff(db, prepend=db[0]), 0)
    data = json.load(open(a.cues))
    cues = data['cues'] if isinstance(data, dict) else data
    fps = fps_of(a.video)
    for c in sorted(cues, key=lambda c: c['t']):
        if c.get('align', 'hit') != 'hit':
            continue
        tv = c['t'] - a.offset                        # cue time inside this file (reel time printed)
        i0, i1 = int((tv - a.win) * 200), int((tv + a.win) * 200)
        if i0 < 0 or i1 >= len(on):
            continue
        k = i0 + int(np.argmax(on[i0:i1]))
        off = k / 200.0 - tv
        flag = 'CHECK' if abs(off) > 1.0 / fps and on[k] > 6 else '     '
        print('%s %7.3f %-16s onset %+5.0f ms (%+.1f fr)  rise %4.1f dB' % (
            flag, c['t'], c['name'], off * 1000, off * fps, on[k]))
    print('(transients - impacts, clicks, pops, ticks - should sit within 1 frame; whooshes peak broadly)')


def run_bytes(cmd):
    r = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if r.returncode != 0:
        sys.exit(r.stderr.decode()[-1500:])
    return r.stdout


def cmd_audio(a):
    r = json.loads(run(['ffprobe', '-v', 'error', '-select_streams', 'a:0', '-show_entries',
                        'stream=codec_name,sample_rate,channels,bits_per_sample,bits_per_raw_sample:format=duration',
                        '-of', 'json', a.media]).stdout)
    print('stream', r.get('streams'), 'duration', r.get('format', {}).get('duration'))
    print('loudness (LUFS / LU / dBTP)', loudness(a.media))
    if a.spec:
        run(['ffmpeg', '-v', 'error', '-y', '-i', a.media, '-lavfi', 'showspectrumpic=s=1600x512:legend=1:scale=log',
             a.spec])
        print(a.spec)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sp = ap.add_subparsers(dest='cmd', required=True)
    p = sp.add_parser('probe'); p.add_argument('video'); p.add_argument('--dur', type=float)
    p.add_argument('--fps', type=float, default=30.0); p.add_argument('--size', default='1080x1920')
    p.add_argument('--max-mb', type=float)
    p = sp.add_parser('sheets'); p.add_argument('video'); p.add_argument('outdir'); p.add_argument('--fps', type=float, default=5)
    p = sp.add_parser('strips'); p.add_argument('video'); p.add_argument('outdir'); p.add_argument('--at', required=True)
    p.add_argument('--span', type=float, default=0.4); p.add_argument('--full', action='store_true')
    p = sp.add_parser('frame'); p.add_argument('video'); p.add_argument('t', type=float); p.add_argument('out')
    for name in ('luma', 'snaps'):
        p = sp.add_parser(name); p.add_argument('video')
        p.add_argument('--from', dest='from_', type=float); p.add_argument('--to', type=float)
    p = sp.add_parser('roi'); p.add_argument('video')
    for k in ('x0', 'y0', 'x1', 'y1'):
        p.add_argument(k, type=int)
    p.add_argument('--from', dest='from_', type=float); p.add_argument('--to', type=float); p.add_argument('--csv')
    p = sp.add_parser('freeze'); p.add_argument('video')
    p = sp.add_parser('guides'); p.add_argument('image'); p.add_argument('out')
    p = sp.add_parser('ink'); p.add_argument('image')
    for k in ('x0', 'y0', 'x1', 'y1'):
        p.add_argument(k, type=int)
    p.add_argument('hex'); p.add_argument('--tol', type=float, default=40.0)
    p = sp.add_parser('cues'); p.add_argument('video'); p.add_argument('cues'); p.add_argument('--win', type=float, default=0.06)
    p.add_argument('--offset', type=float, default=0.0, help='reel time of the first frame (range renders)')
    p = sp.add_parser('audio'); p.add_argument('media'); p.add_argument('--spec')
    a = ap.parse_args()
    globals()['cmd_' + a.cmd](a)


if __name__ == '__main__':
    main()
