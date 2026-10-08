"""Final mix: cleaned-up voice from the main clip + the reference video's own SFX at the cue
times exported by edit.py (`edit.py sfx cues.json`). Loudness-normalised for Instagram (-14 LUFS)."""
import json, subprocess, sys
import numpy as np
from scipy.io import wavfile

SR = 48000


def load(path):
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', path, '-f', 'f32le', '-ac', '2', '-ar', str(SR), '-'],
                         capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.float32).reshape(-1, 2).copy()


def main(main_clip, cues_json, sfx_dir, out_wav, dur):
    # voice: rumble cut, gentle compression, presence, then normalise
    vfilt = ('highpass=f=75,lowpass=f=15500,acompressor=threshold=-21dB:ratio=3:attack=6:release=90:makeup=2,'
             'equalizer=f=3200:t=q:w=1.2:g=2,equalizer=f=250:t=q:w=1.0:g=-1.5,loudnorm=I=-16:TP=-2:LRA=9')
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', main_clip, '-af', vfilt, '-ar', str(SR), '-ac', '2',
                    '/tmp/_voice.wav'], check=True)
    voice = load('/tmp/_voice.wav')
    n = int(dur * SR)
    mix = np.zeros((n, 2), np.float32)
    mix[:min(n, len(voice))] += voice[:n]
    cache = {}
    sfx_bus = np.zeros_like(mix)
    for t, name, gdb in json.load(open(cues_json)):
        if name not in cache:
            s = load(f'{sfx_dir}/{name}.wav')
            env = np.abs(s).mean(1)
            k = int(0.02 * SR)
            env = np.convolve(env, np.ones(k) / k, 'same')
            cache[name] = (s, int(np.argmax(env)))
        s, peak = cache[name]
        if name.startswith('whoosh'):
            i0 = int((t + 0.30) * SR) - peak  # whoosh peaks on the cut
        else:
            i0 = int(t * SR)
        i0 = max(0, i0)
        seg = s[:max(0, min(len(s), n - i0))]
        sfx_bus[i0:i0 + len(seg)] += seg * (10 ** (gdb / 20))
    sfx_bus *= 10 ** (-7 / 20)  # SFX bus sits under the voice
    # light sidechain duck of the SFX bus under speech
    venv = np.abs(mix).mean(1)
    k = int(0.05 * SR)
    venv = np.convolve(venv, np.ones(k) / k, 'same')
    duck = 1 - 0.35 * np.clip(venv / (venv.max() * 0.25 + 1e-9), 0, 1)
    mix += sfx_bus * duck[:, None]
    wavfile.write('/tmp/_mix.wav', SR, mix)
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', '/tmp/_mix.wav', '-af',
                    'alimiter=limit=0.89:attack=3:release=40,loudnorm=I=-14:TP=-1.5:LRA=11', '-ar', str(SR), out_wav],
                   check=True)
    print('mixed', out_wav)


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], float(sys.argv[5]))
