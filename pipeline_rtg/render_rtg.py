"""Render "Room to Grow": frames in parallel -> soundtrack -> master + share encodes.

Usage: python3 render_rtg.py [noframes]
"""
import os, subprocess, sys
from concurrent.futures import ThreadPoolExecutor
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
S = os.path.abspath(os.path.join(HERE, '..', 'workspace_rtg'))
OUT = os.path.abspath(os.path.join(HERE, '..', 'reel', 'organic_fostering'))
JOBS = int(os.environ.get('JOBS', '4'))
NF = int(open(f'{S}/nf.txt').read()) if os.path.exists(f'{S}/nf.txt') else 1201


def run(a, b):
    subprocess.run([sys.executable, f'{HERE}/reel_rtg.py', 'range', str(a), str(b)], check=True, env={**os.environ, 'RESUME': '1'},
                   stdout=subprocess.DEVNULL)


if __name__ == '__main__':
    if 'noframes' not in sys.argv:
        step = (NF + JOBS - 1) // JOBS
        with ThreadPoolExecutor(JOBS) as ex:
            list(ex.map(lambda c: run(*c), [(a, min(NF, a + step)) for a in range(0, NF, step)]))
    subprocess.run([sys.executable, f'{HERE}/audio_rtg.py'], check=True)
    os.makedirs(OUT, exist_ok=True)
    out = f'{OUT}/organic_fostering_room_to_grow.mp4'
    subprocess.run(['ffmpeg', '-y', '-v', 'error', '-framerate', '30', '-i', f'{S}/frames_out/%04d.jpg', '-i', f'{S}/audio/mix_raw.wav',
                    '-af', 'loudnorm=I=-14:TP=-1.5:LRA=11', '-c:v', 'libx264', '-preset', 'slow', '-b:v', '9M', '-maxrate', '11M',
                    '-bufsize', '18M', '-pix_fmt', 'yuv420p', '-profile:v', 'high', '-movflags', '+faststart',
                    '-c:a', 'aac', '-b:a', '256k', '-ar', '48000', '-shortest', out], check=True)
    share = out.replace('.mp4', '_share.mp4')
    subprocess.run(['ffmpeg', '-y', '-v', 'error', '-i', out, '-c:v', 'libx264', '-preset', 'slow', '-b:v', '4.2M', '-maxrate', '5.2M',
                    '-bufsize', '8M', '-pix_fmt', 'yuv420p', '-movflags', '+faststart', '-c:a', 'aac', '-b:a', '128k', share], check=True)
    print('wrote', out, share, flush=True)
