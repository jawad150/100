"""Parallel chunked render of the gold reel, then sound design + final mux.

  python3 render.py            -> $GOLD_WORKDIR/out/gold_reel_final.mp4
  RESUME=1 python3 render.py   -> reuse finished chunks
"""
import os, sys, subprocess, time
from concurrent.futures import ThreadPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import timeline as TL

S = os.environ.get('GOLD_WORKDIR', os.path.abspath(os.path.join(HERE, '..', '..', 'workspace')))
OUT = S + '/out'
CHUNKS = int(os.environ.get('CHUNKS', '24'))
WORKERS = int(os.environ.get('WORKERS', '4'))
TOTAL = TL.NFRAMES


def run(k):
    f0, f1 = k * TOTAL // CHUNKS, (k + 1) * TOTAL // CHUNKS
    out = f'{OUT}/chunk_{k:02d}.mp4'
    if os.path.exists(out) and os.environ.get('RESUME'):
        return out
    t = time.time()
    subprocess.run([sys.executable, 'gold_reel.py', 'range', str(f0), str(f1), out + '.tmp.mp4'], cwd=HERE, check=True,
                   stdout=open(f'{OUT}/chunk_{k:02d}.log', 'w'), stderr=subprocess.STDOUT)
    os.replace(out + '.tmp.mp4', out)
    print(f'chunk {k} [{f0},{f1}) {time.time() - t:.0f}s', flush=True)
    return out


if __name__ == '__main__':
    os.makedirs(OUT, exist_ok=True)
    t0 = time.time()
    with ThreadPoolExecutor(WORKERS) as ex:
        outs = list(ex.map(run, range(CHUNKS)))
    with open(f'{OUT}/concat.txt', 'w') as f:
        for o in outs:
            f.write(f"file '{o}'\n")
    subprocess.run([sys.executable, 'gold_audio.py'], cwd=HERE, check=True)
    master = f'{OUT}/gold_reel_4k.mp4'
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'concat', '-safe', '0', '-i', f'{OUT}/concat.txt',
                    '-i', f'{OUT}/audio.wav', '-map', '0:v', '-map', '1:a', '-c:v', 'libx264', '-preset', 'slow',
                    '-crf', '17', '-profile:v', 'high', '-level', '5.2', '-pix_fmt', 'yuv420p',
                    '-r', '30000/1001', '-movflags', '+faststart', '-c:a', 'aac', '-b:a', '320k', '-shortest', master],
                   check=True)
    share = f'{OUT}/gold_reel_1080p.mp4'
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', master, '-vf', 'scale=1080:1920:flags=lanczos',
                    '-c:v', 'libx264', '-preset', 'slow', '-crf', '18', '-profile:v', 'high', '-pix_fmt', 'yuv420p',
                    '-movflags', '+faststart', '-c:a', 'copy', share], check=True)
    for final in (master, share):
        print('final', final, round(os.path.getsize(final) / 1e6, 1), 'MB', f'{time.time() - t0:.0f}s', flush=True)
