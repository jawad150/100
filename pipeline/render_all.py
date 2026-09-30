"""Parallel chunked render of the reel + final mux."""
import subprocess, sys, os, time
from concurrent.futures import ThreadPoolExecutor

S = os.environ.get('REEL_WORKDIR', os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'workspace')))
W = os.path.dirname(os.path.abspath(__file__))
OUT = S + '/out'
TOTAL = 900
CHUNKS = int(os.environ.get('CHUNKS', '12'))
WORKERS = int(os.environ.get('WORKERS', '4'))

def run(k):
    f0 = k * TOTAL // CHUNKS
    f1 = (k + 1) * TOTAL // CHUNKS
    out = f'{OUT}/chunk_{k:02d}.mp4'
    if os.path.exists(out) and os.environ.get('RESUME'):
        return out
    t = time.time()
    subprocess.run([sys.executable, 'reel.py', 'range', str(f0), str(f1), out], cwd=W, check=True,
                   stdout=open(f'{OUT}/chunk_{k:02d}.log', 'w'), stderr=subprocess.STDOUT)
    print(f'chunk {k} [{f0},{f1}) done in {time.time() - t:.0f}s', flush=True)
    return out

if __name__ == '__main__':
    os.makedirs(OUT, exist_ok=True)
    t0 = time.time()
    with ThreadPoolExecutor(WORKERS) as ex:
        outs = list(ex.map(run, range(CHUNKS)))
    with open(f'{OUT}/concat.txt', 'w') as f:
        for o in outs:
            f.write(f"file '{o}'\n")
    subprocess.run(['python3', 'audio.py'], cwd=W, check=True)
    final = f'{OUT}/higgsfield_genjutsu_reel.mp4'
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'concat', '-safe', '0', '-i', f'{OUT}/concat.txt',
                    '-i', f'{OUT}/audio.wav', '-map', '0:v', '-map', '1:a',
                    '-c:v', 'libx264', '-preset', 'slow', '-crf', os.environ.get('CRF', '17'), '-profile:v', 'high',
                    '-pix_fmt', 'yuv420p', '-r', '30', '-movflags', '+faststart',
                    '-c:a', 'aac', '-b:a', '256k', '-shortest', final], check=True)
    print('final', final, os.path.getsize(final) / 1e6, 'MB', f'total {time.time() - t0:.0f}s', flush=True)
