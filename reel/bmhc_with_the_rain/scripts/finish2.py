"""Loudness-normalise each mix (two-pass, -14 LUFS / -1.5 dBTP), mux with the picture, and make 720p web previews.
Usage: python3 -I finish2.py VIDEO.mp4 OUTDIR name=audio.wav [name=audio.wav ...]"""
import json, os, subprocess, sys
video, outdir = sys.argv[1], sys.argv[2]
os.makedirs(outdir, exist_ok=True)
def run(cmd): return subprocess.run(cmd, check=True, capture_output=True, text=True)
for spec in sys.argv[3:]:
    name, wav = spec.split('=', 1)
    r = run(['ffmpeg', '-hide_banner', '-i', wav, '-af', 'loudnorm=I=-14:TP=-1.5:LRA=11:print_format=json', '-f', 'null', '-'])
    j = r.stderr[r.stderr.rfind('{'):r.stderr.rfind('}') + 1]; m = json.loads(j)
    af = (f"loudnorm=I=-14:TP=-1.5:LRA=11:measured_I={m['input_i']}:measured_TP={m['input_tp']}:measured_LRA={m['input_lra']}:"
          f"measured_thresh={m['input_thresh']}:offset={m['target_offset']}:linear=true,aresample=48000")
    full = os.path.join(outdir, f'bmhc_with_the_rain_{name}.mp4')
    run(['ffmpeg', '-v', 'error', '-y', '-i', video, '-i', wav, '-map', '0:v', '-map', '1:a', '-c:v', 'copy', '-af', af,
         '-c:a', 'aac', '-b:a', '320k', '-ar', '48000', '-shortest', '-movflags', '+faststart', full])
    prev = os.path.join(outdir, f'bmhc_with_the_rain_preview_{name}.mp4')
    run(['ffmpeg', '-v', 'error', '-y', '-i', full, '-vf', 'scale=720:1280:flags=lanczos', '-c:v', 'libx264', '-profile:v', 'main', '-level', '4.0',
         '-preset', 'slow', '-crf', '22', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '160k', '-movflags', '+faststart', prev])
    chk = run(['ffmpeg', '-hide_banner', '-i', full, '-af', 'ebur128=peak=true', '-f', 'null', '-']).stderr
    tail = chk[chk.rfind('Summary:'):]
    I = [l.split(':')[1].strip() for l in tail.splitlines() if l.strip().startswith('I:')]
    pk = [l.split(':')[1].strip() for l in tail.splitlines() if l.strip().startswith('Peak:')]
    print(name, 'I', I, 'true peak', pk, os.path.getsize(full) // 1024 // 1024, 'MB /', os.path.getsize(prev) // 1024 // 1024, 'MB preview')
