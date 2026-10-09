"""Encode rendered frames + audio mix into the deliverable MP4.

Usage: python3 encode.py [out.mp4] [crf]
"""
import os, subprocess, sys
from common import WS, HERE

out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, '..', '..', 'reel', 'medspa', 'PS_MedSpa_Reel_1080x1920.mp4')
crf = sys.argv[2] if len(sys.argv) > 2 else '15'
os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
subprocess.run([
    'ffmpeg', '-v', 'error', '-y',
    '-framerate', '24000/1001', '-i', os.environ.get('FRAMES_DIR', f'{WS}/out/frames') + '/%04d.png',
    '-i', f'{WS}/out/mix.wav',
    '-map', '0:v', '-map', '1:a',
    # RGB -> BT.709 limited range with accurate rounding (unbiased round trip)
    '-vf', 'scale=out_color_matrix=bt709:out_range=tv:flags=accurate_rnd+full_chroma_int,format=yuv420p',
    '-c:v', 'libx264', '-preset', 'slow', '-crf', crf, '-profile:v', 'high', '-tune', 'film',
    '-colorspace', 'bt709', '-color_primaries', 'bt709', '-color_trc', 'bt709', '-color_range', 'tv',
    '-c:a', 'aac', '-b:a', '320k', '-movflags', '+faststart', '-shortest', out], check=True)
print('wrote', out, f'{os.path.getsize(out) / 1e6:.1f} MB')
