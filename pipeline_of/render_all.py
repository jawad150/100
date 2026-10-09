"""Render all frames in parallel chunks, then encode + mux the -14 LUFS soundtrack."""
import os, subprocess, sys
from concurrent.futures import ThreadPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))
S = os.environ.get('REEL_WORKDIR', os.path.abspath(os.path.join(HERE, '..', 'workspace_of')))
FPS, NF = 30, 570
JOBS = int(os.environ.get('JOBS', '4'))


def run(a, b):
    subprocess.run([sys.executable, f'{HERE}/reel_of.py', 'range', str(a), str(b)], check=True,
                   stdout=subprocess.DEVNULL)


if __name__ == '__main__':
    if 'noframes' not in sys.argv:
        step = (NF + JOBS * 3 - 1) // (JOBS * 3)
        chunks = [(a, min(NF, a + step)) for a in range(0, NF, step)]
        with ThreadPoolExecutor(JOBS) as ex:
            list(ex.map(lambda c: run(*c), chunks))
    subprocess.run([sys.executable, f'{HERE}/audio_of.py'], check=True)
    os.makedirs(f'{S}/out', exist_ok=True)
    out = f'{S}/out/organic_fostering_day_in_the_life.mp4'
    subprocess.run(['ffmpeg', '-y', '-v', 'error', '-framerate', str(FPS), '-i', f'{S}/frames_out/%04d.png',
                    '-i', f'{S}/audio/mix_raw.wav',
                    '-af', 'loudnorm=I=-14:TP=-1.5:LRA=11',
                    '-c:v', 'libx264', '-preset', 'slow', '-crf', '16', '-pix_fmt', 'yuv420p',
                    '-profile:v', 'high', '-movflags', '+faststart',
                    '-c:a', 'aac', '-b:a', '256k', '-ar', '48000', '-shortest', out], check=True)
    print('wrote', out)
