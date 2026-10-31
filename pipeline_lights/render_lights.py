"""Render BMHC "Lights On": frames (already rendered in parallel) -> soundtrack -> master + share encodes.

Usage: python3 render_lights.py [noframes]
"""
import os, subprocess, sys
from concurrent.futures import ThreadPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))
S = os.path.abspath(os.path.join(HERE, '..', 'workspace_lights'))
OUT = os.path.abspath(os.path.join(HERE, '..', 'reel', 'bmhc'))
JOBS = int(os.environ.get('JOBS', '4'))
NF = 1476   # 49.23 s at 30 fps


def run(a, b):
    subprocess.run([sys.executable, f'{HERE}/reel_lights.py', 'range', str(a), str(b)], check=True, env={**os.environ, 'RESUME': '1'},
                   stdout=subprocess.DEVNULL)


if __name__ == '__main__':
    if 'noframes' not in sys.argv:
        step = (NF + JOBS - 1) // JOBS
        with ThreadPoolExecutor(JOBS) as ex:
            list(ex.map(lambda c: run(*c), [(a, min(NF, a + step)) for a in range(0, NF, step)]))
    subprocess.run([sys.executable, f'{HERE}/audio_lights.py'], check=True)
    os.makedirs(OUT, exist_ok=True)
    out = f'{OUT}/bmhc_lights_on.mp4'
    subprocess.run(['ffmpeg', '-y', '-v', 'error', '-framerate', '30', '-i', f'{S}/frames_out/%04d.jpg', '-i', f'{S}/audio/mix_raw.wav',
                    '-af', 'loudnorm=I=-14:TP=-1.5:LRA=11', '-c:v', 'libx264', '-preset', 'slow', '-b:v', '9M', '-maxrate', '11M',
                    '-bufsize', '18M', '-pix_fmt', 'yuv420p', '-profile:v', 'high', '-movflags', '+faststart',
                    '-c:a', 'aac', '-b:a', '256k', '-ar', '48000', '-shortest', out], check=True)
    share = out.replace('.mp4', '_share.mp4')
    subprocess.run(['ffmpeg', '-y', '-v', 'error', '-i', out, '-c:v', 'libx264', '-preset', 'slow', '-b:v', '4.2M', '-maxrate', '5.2M',
                    '-bufsize', '8M', '-pix_fmt', 'yuv420p', '-movflags', '+faststart', '-c:a', 'aac', '-b:a', '128k', share], check=True)
    print('wrote', out, share, flush=True)
