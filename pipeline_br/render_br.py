"""Render Bodyrade reels: parallel frame chunks -> soundtrack -> master + share encodes.

Usage: python3 render_br.py fresh five flavour   [noframes]
"""
import os, subprocess, sys
from concurrent.futures import ThreadPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))
S = os.environ.get('REEL_WORKDIR', os.path.abspath(os.path.join(HERE, '..', 'workspace_br')))
JOBS = int(os.environ.get('JOBS', '4'))
DURS = {'fresh': 28.5, 'five': 26.5, 'flavour': 25.0}


def run(reel, a, b):
    env = dict(os.environ, REEL=reel)
    subprocess.run([sys.executable, f'{HERE}/reel_br.py', 'range', str(a), str(b)], check=True, env=env,
                   stdout=subprocess.DEVNULL)


if __name__ == '__main__':
    reels = [r for r in sys.argv[1:] if r in DURS]
    os.makedirs(f'{S}/out', exist_ok=True)
    for reel in reels:
        nf = int(DURS[reel] * 30)
        if 'noframes' not in sys.argv:
            step = (nf + JOBS * 3 - 1) // (JOBS * 3)
            with ThreadPoolExecutor(JOBS) as ex:
                list(ex.map(lambda c: run(reel, *c), [(a, min(nf, a + step)) for a in range(0, nf, step)]))
        subprocess.run([sys.executable, f'{HERE}/audio_br.py'], check=True, env=dict(os.environ, REEL=reel))
        out = f'{S}/out/bodyrade_{reel}.mp4'
        subprocess.run(['ffmpeg', '-y', '-v', 'error', '-framerate', '30', '-i', f'{S}/frames_{reel}/%04d.png',
                        '-i', f'{S}/audio/mix_{reel}.wav', '-af', 'loudnorm=I=-14:TP=-1.5:LRA=11',
                        '-c:v', 'libx264', '-preset', 'slow', '-crf', '17', '-pix_fmt', 'yuv420p', '-profile:v', 'high',
                        '-movflags', '+faststart', '-c:a', 'aac', '-b:a', '256k', '-ar', '48000', '-shortest', out],
                       check=True)
        share = out.replace('.mp4', '_share.mp4')
        subprocess.run(['ffmpeg', '-y', '-v', 'error', '-i', out, '-c:v', 'libx264', '-preset', 'slow', '-b:v', '7M',
                        '-maxrate', '8.5M', '-bufsize', '14M', '-pix_fmt', 'yuv420p', '-movflags', '+faststart',
                        '-c:a', 'copy', share], check=True)
        print('wrote', out, share, flush=True)
