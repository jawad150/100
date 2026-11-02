import json, os, subprocess, sys
B = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = lambda *p: os.path.join(B, *p)
TL = json.load(open(P('timeline.json')))
SH = {s['name']: s for s in TL['shots']}
M = 0.6
SPEC = {
 'window':   (P('picks_rain', 's1_window_3.mp4'), 8.0, (608, 1080, 440, 0), 1.0, 0.07, 'night'),
 'man':      (P('picks_people', 's2_busstop_3.mp4'), 2.0, (608, 1080, 848, 0), 1.0, 0.06, 'night'),
 'verse':    (P('picks_rain', 's3_puddle_1.mp4'), 0.0, (608, 1080, 700, 0), 0.8, 0.035, 'deep'),
 'umbrella': (P('picks_people', 's4_umbrella_1.mp4'), 10.0, (1216, 2160, 1504, 0), 1.0, 0.05, 'night'),
 'ease':     (P('picks_people', 'x_city_3.mp4'), 1.0, (1215, 2160, 1150, 0), 1.0, 0.06, 'warm'),
}
SPEC.update(json.load(open(P('scripts', 'stage1_v2.json'))) if os.path.exists(P('scripts', 'stage1_v2.json')) else {})
only = sys.argv[1:] or list(SPEC)
for name in only:
    src, t_in, (cw, ch, cx, cy), speed, k, lut = SPEC[name]
    if not os.path.isabs(src): src = P(src)
    D = SH[name]['end'] - SH[name]['start'] + 2 * M
    vf = (f"setpts=(PTS-STARTPTS)/{speed},fps=30,crop={cw}:{ch}:{cx}:{cy},scale=1080:1920:flags=lanczos,"
          f"scale=w='1080*(1+{k}*t/{D:.3f})':h=-2:eval=frame:flags=bicubic,crop=1080:1920:(in_w-1080)/2:(in_h-1920)/2,"
          f"lut3d=file={P('luts', lut + '.cube')},format=yuv420p")
    out = P('shots', f'{name}.mp4')
    cmd = ['ffmpeg', '-v', 'error', '-y', '-ss', str(t_in), '-i', src, '-t', f'{D:.3f}', '-vf', vf, '-an', '-r', '30',
           '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '10', out]
    subprocess.run(cmd, check=True)
    d = subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', out], capture_output=True, text=True).stdout.strip()
    print(name, 'need', round(D, 2), 'got', d, flush=True)
