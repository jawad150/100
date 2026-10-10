"""Package a rendered reel into the delivery folder (reel/organic_fostering/, or project.json "deliver").

python3 package.py <module> <slug> [--cover SECONDS] [--bitrate 22M]

  e.g.  python3 package.py reel1 reel1_could_you --cover 3.6
        python3 package.py anim4 anim4_where_does_it_go --cover 1.2

Reads workspace3/out/<module>/<module>.mp4 (the render.py master) and writes
  organic_fostering_<slug>.mp4          Instagram-ready H.264 High, 2-pass ~22 Mbps, +faststart (< 100 MB for ~26 s)
  organic_fostering_<slug>_master.mp4   the CRF 14 master (stored with Git LFS)
  organic_fostering_<slug>_sfx_stem.wav the 48 kHz 24-bit SFX stem (workspace3/audio/<module>_sfx_stem.wav)
  organic_fostering_<slug>_cover.jpg    a frame of the master at --cover seconds
Another project sets its folder and file prefix in project.json:
  "deliver": {"dir": "reel/acme", "prefix": "acme"}   (add  reel/acme/*_master.mp4  to .gitattributes LFS)
"""
import argparse
import os
import shutil
import subprocess
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, '..', '..'))
import wsconf  # noqa: E402
WS = wsconf.workspace()
_DELIVER = wsconf.project().get('deliver', {})
DEST = os.path.join(REPO, _DELIVER.get('dir', os.path.join('reel', 'organic_fostering')))
PREFIX = _DELIVER.get('prefix', 'organic_fostering')


def run(cmd):
    subprocess.run(cmd, check=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('module')
    ap.add_argument('slug')
    ap.add_argument('--cover', type=float, default=2.0)
    ap.add_argument('--bitrate', default='22M')
    a = ap.parse_args()
    master = os.path.join(WS, 'out', a.module, a.module + '.mp4')
    if not os.path.exists(master):
        raise SystemExit(f'no master at {master}: run  python3 render.py {a.module} --workers 4  first')
    os.makedirs(DEST, exist_ok=True)
    base = os.path.join(DEST, PREFIX + '_' + a.slug)
    with tempfile.TemporaryDirectory() as tmp:
        log = os.path.join(tmp, 'pass')
        common = ['-c:v', 'libx264', '-preset', 'slow', '-b:v', a.bitrate, '-passlogfile', log]
        run(['ffmpeg', '-v', 'error', '-y', '-i', master, *common, '-pass', '1', '-an', '-f', 'null', os.devnull])
        run(['ffmpeg', '-v', 'error', '-y', '-i', master, *common, '-pass', '2', '-maxrate', '30M', '-bufsize', '44M',
             '-profile:v', 'high', '-pix_fmt', 'yuv420p', '-color_primaries', 'bt709', '-color_trc', 'bt709',
             '-colorspace', 'bt709', '-c:a', 'copy', '-movflags', '+faststart', base + '.mp4'])
    shutil.copyfile(master, base + '_master.mp4')
    stem = os.path.join(WS, 'audio', a.module + '_sfx_stem.wav')
    if os.path.exists(stem):
        shutil.copyfile(stem, base + '_sfx_stem.wav')
    run(['ffmpeg', '-v', 'error', '-y', '-ss', str(a.cover), '-i', master, '-frames:v', '1', '-q:v', '2', base + '_cover.jpg'])
    for suffix in ('.mp4', '_master.mp4', '_sfx_stem.wav', '_cover.jpg'):
        p = base + suffix
        if os.path.exists(p):
            print(f'{os.path.getsize(p) / 1e6:8.1f} MB  {os.path.relpath(p, REPO)}')


if __name__ == '__main__':
    main()
