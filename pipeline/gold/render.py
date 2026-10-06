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
WORKERS = int(os.environ.get('WORKERS', '3'))   # ~3 GB per 4K worker (render + encoder)
TOTAL = TL.NFRAMES
RENDERER = os.environ.get('RENDERER', 'gold_reel.py')     # ref_reel.py = the reference-style cut
NAME = os.environ.get('NAME', 'gold_reel')


def run(k):
    f0, f1 = k * TOTAL // CHUNKS, (k + 1) * TOTAL // CHUNKS
    out = f'{OUT}/chunk_{k:02d}.mp4'
    if os.path.exists(out) and os.environ.get('RESUME'):
        return out
    t = time.time()
    for attempt in range(2):          # one retry (e.g. after an out-of-memory kill)
        r = subprocess.run([sys.executable, RENDERER, 'range', str(f0), str(f1), out + '.tmp.mp4'], cwd=HERE,
                           stdout=open(f'{OUT}/chunk_{k:02d}.log', 'w'), stderr=subprocess.STDOUT)
        if r.returncode == 0:
            os.replace(out + '.tmp.mp4', out)
            print(f'chunk {k} [{f0},{f1}) {time.time() - t:.0f}s', flush=True)
            return out
        print(f'chunk {k} failed ({r.returncode}), attempt {attempt + 1}', flush=True)
    return None


if __name__ == '__main__':
    os.makedirs(OUT, exist_ok=True)
    t0 = time.time()
    with ThreadPoolExecutor(WORKERS) as ex:
        outs = list(ex.map(run, range(CHUNKS)))
    missing = [k for k, o in enumerate(outs) if o is None]
    if missing:
        sys.exit(f'chunks failed: {missing}')
    with open(f'{OUT}/concat.txt', 'w') as f:
        for o in outs:
            f.write(f"file '{o}'\n")
    env = dict(os.environ)
    if RENDERER == 'ref_reel.py':
        subprocess.run([sys.executable, RENDERER, 'sfx'], cwd=HERE, check=True)
        env['CUES'] = S + '/work/ref_sfx.json'
    subprocess.run([sys.executable, 'gold_audio.py'], cwd=HERE, check=True, env=env)
    src = ['-f', 'concat', '-safe', '0', '-i', f'{OUT}/concat.txt', '-i', f'{OUT}/audio.wav', '-map', '0:v', '-map', '1:a']
    master, share = f'{OUT}/{NAME}_4k.mp4', f'{OUT}/{NAME}_1080p.mp4'
    for out, vf, rate, lvl, ab in ((master, [], ('45M', '60M', '90M'), '5.2', '320k'),
                                   (share, ['-vf', 'scale=1080:1920:flags=lanczos'], ('12M', '16M', '24M'), '4.2', '256k')):
        enc = ['-c:v', 'libx264', '-preset', 'medium', '-tune', 'film', '-b:v', rate[0], '-maxrate', rate[1],
               '-bufsize', rate[2]]
        log = f'{OUT}/x264_{os.path.basename(out)}'
        subprocess.run(['ffmpeg', '-y', '-loglevel', 'error'] + src + vf + enc + ['-pass', '1', '-passlogfile', log,
                        '-an', '-f', 'mp4', '/dev/null'], check=True)
        subprocess.run(['ffmpeg', '-y', '-loglevel', 'error'] + src + vf + enc + ['-pass', '2', '-passlogfile', log,
                        '-profile:v', 'high', '-level', lvl, '-pix_fmt', 'yuv420p', '-r', '30000/1001',
                        '-movflags', '+faststart', '-c:a', 'aac', '-b:a', ab, '-shortest', out], check=True)
    for final in (master, share):
        print('final', final, round(os.path.getsize(final) / 1e6, 1), 'MB', f'{time.time() - t0:.0f}s', flush=True)
