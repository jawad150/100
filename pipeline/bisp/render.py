"""Parallel render of the BISP reel + mux + Instagram/master encodes.

    python3 render.py [--workers 4] [--range 0,300]    -> workspace_bisp/out/chunks/*.mp4, video.mp4
    python3 render.py --package                        -> reel/bisp/*.mp4, cover, srt, stems
"""
import os, sys, subprocess, argparse, json, shutil
import numpy as np
from multiprocessing import Process

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import edl

WS = edl.WS
OUT = os.path.join(WS, 'out')
CH = os.path.join(OUT, 'chunks')
REPO = os.path.abspath(os.path.join(HERE, '..', '..'))
DELIV = os.path.join(REPO, 'reel', 'bisp')
NAME = 'bisp_interoperability_reel'


def worker(i0, i1, path):
    import reel
    cmd = ['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', '1080x1920', '-r', '30',
           '-i', '-', '-c:v', 'libx264', '-preset', 'medium', '-crf', '12', '-pix_fmt', 'yuv420p',
           '-color_primaries', 'bt709', '-color_trc', 'bt709', '-colorspace', 'bt709', path + '.part.mp4']
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    for i in range(i0, i1):
        p.stdin.write(reel.render_frame(i / edl.FPS).tobytes())
    p.stdin.close(); p.wait()
    os.replace(path + '.part.mp4', path)


def render(workers, rng=None):
    os.makedirs(CH, exist_ok=True)
    n = edl.timeline().nframes
    a, b = rng or (0, n)
    size = 150
    chunks = [(s, min(s + size, b)) for s in range(a, b, size)]
    todo = [c for c in chunks if not os.path.exists(os.path.join(CH, f'{c[0]:05d}.mp4'))]
    print('frames', n, 'chunks', len(chunks), 'todo', len(todo), flush=True)
    procs = []
    while todo or procs:
        while todo and len(procs) < workers:
            c = todo.pop(0)
            p = Process(target=worker, args=(c[0], c[1], os.path.join(CH, f'{c[0]:05d}.mp4')))
            p.start(); procs.append(p)
        for p in procs[:]:
            p.join(timeout=0.5)
            if not p.is_alive():
                procs.remove(p)
                print('done chunk; left', len(todo) + len(procs), flush=True)
    if rng is None:
        lst = os.path.join(CH, 'list.txt')
        with open(lst, 'w') as f:
            for c in chunks:
                f.write(f"file '{os.path.join(CH, f'{c[0]:05d}.mp4')}'\n")
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', lst, '-c', 'copy',
                        os.path.join(OUT, 'video.mp4')], check=True)
        print('video ->', os.path.join(OUT, 'video.mp4'))


def srt():
    """Roman Urdu captions as SRT (the caption pages of the reel)."""
    import reel
    def ts(t):
        ms = int(round(t * 1000)); h, ms = divmod(ms, 3600000); m, ms = divmod(ms, 60000); s, ms = divmod(ms, 1000)
        return f'{h:02d}:{m:02d}:{s:02d},{ms:03d}'
    # full sentences, including the parts the graphics carry on screen
    lines, cur, k = [], [], 1
    for w in reel.WORDS:
        if cur and (w['sent'] != cur[-1]['sent'] or len(cur) >= 7 or cur[-1]['word'][-1] in ',.:!?'):
            lines.append(cur); cur = []
        cur.append(w)
    if cur: lines.append(cur)
    out = []
    for i, ln in enumerate(lines):
        t0 = ln[0]['ot'] - 0.05
        t1 = (lines[i + 1][0]['ot'] - 0.06) if i + 1 < len(lines) else ln[-1]['ot'] + 1.0
        t1 = min(t1, ln[-1]['ot'] + 1.2)
        out.append(f"{k}\n{ts(t0)} --> {ts(t1)}\n{' '.join(w['word'] for w in ln)}\n")
        k += 1
    return '\n'.join(out)


def package():
    os.makedirs(DELIV, exist_ok=True)
    video = os.path.join(OUT, 'video.mp4')
    mix = os.path.join(WS, 'audio_out', 'mix.wav')
    master = os.path.join(DELIV, f'{NAME}_master.mp4')
    ig = os.path.join(DELIV, f'{NAME}_instagram.mp4')
    tags = ['-color_primaries', 'bt709', '-color_trc', 'bt709', '-colorspace', 'bt709', '-movflags', '+faststart']
    # master: the CRF 12 render, AAC 320k
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', video, '-i', mix, '-map', '0:v', '-map', '1:a', '-c:v', 'copy',
                    '-c:a', 'aac', '-b:a', '320k', '-ar', '48000', '-shortest'] + tags + [master], check=True)
    # Instagram: 2-pass H.264 High, ~10 Mbps, AAC 256k
    pl = os.path.join(OUT, 'x264pass')
    common = ['-c:v', 'libx264', '-preset', 'slow', '-profile:v', 'high', '-level', '4.2', '-b:v', '10M',
              '-maxrate', '16M', '-bufsize', '24M', '-pix_fmt', 'yuv420p', '-r', '30', '-g', '60', '-passlogfile', pl]
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', video] + common + ['-pass', '1', '-an', '-f', 'mp4', os.devnull], check=True)
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', video, '-i', mix, '-map', '0:v', '-map', '1:a'] + common +
                   ['-pass', '2', '-c:a', 'aac', '-b:a', '256k', '-ar', '48000', '-shortest'] + tags + [ig], check=True)
    # cover (hook frame with the INTEROPERABILITY slab + both pills)
    import reel, cv2
    cov = reel.render_frame(5.6)
    cv2.imwrite(os.path.join(DELIV, f'{NAME}_cover.jpg'), cov[..., ::-1], [cv2.IMWRITE_JPEG_QUALITY, 93])
    open(os.path.join(DELIV, f'{NAME}_captions_roman_urdu.srt'), 'w').write(srt())
    st = os.path.join(DELIV, 'stems'); os.makedirs(st, exist_ok=True)
    for nm in ('voice', 'music', 'sfx'):
        shutil.copy(os.path.join(WS, 'audio_out', f'{nm}_stem.wav'), os.path.join(st, f'{NAME}_{nm}_stem.wav'))
    for p in sorted(os.listdir(DELIV)):
        fp = os.path.join(DELIV, p)
        if os.path.isfile(fp):
            print(p, '%.1f MB' % (os.path.getsize(fp) / 1e6))


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--workers', type=int, default=4)
    ap.add_argument('--range')
    ap.add_argument('--package', action='store_true')
    a = ap.parse_args()
    if a.package:
        package()
    else:
        render(a.workers, tuple(int(x) for x in a.range.split(',')) if a.range else None)
