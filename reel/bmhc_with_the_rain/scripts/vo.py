import soundfile as sf, numpy as np, json, sys, os
from kokoro_onnx import Kokoro
B = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
k = Kokoro(os.path.join(B, 'audio', 'kokoro-v1.0.onnx'), os.path.join(B, 'audio', 'voices-v1.0.bin'))
voice = sys.argv[1] if len(sys.argv) > 1 else 'bm_george'
speed = float(sys.argv[2]) if len(sys.argv) > 2 else 0.9
LINES = {
 'L1': "Manchester knows rain. Some days, so do we.",
 'L2': "A bill. A loss. A worry nobody sees.",
 'L3': "Allah says: For indeed, with hardship will be ease. Indeed, with hardship will be ease.",
 'L4': "Notice the word: with. Not only after the hardship. With it.",
 'L5': "Ease often comes while it's still raining: a warm cup,",
 'L6': "a friend who calls,",
 'L7': "a door that's open.",
 'L8': "Whatever you are going through, support is just a conversation away.",
 'L9': "Imam Counselling at B. M. H. C.",
}
out = {}
for key, text in LINES.items():
    samples, sr = k.create(text, voice=voice, speed=speed, lang='en-gb')
    samples = np.asarray(samples, dtype=np.float32)
    # trim silence
    a = np.abs(samples); thr = 0.01 * a.max(); idx = np.where(a > thr)[0]
    samples = samples[max(0, idx[0] - int(0.03 * sr)): idx[-1] + int(0.08 * sr)]
    fn = os.path.join(B, 'audio', 'vo', f'{key}.wav')
    sf.write(fn, samples, sr)
    out[key] = {'text': text, 'dur': round(len(samples) / sr, 3), 'sr': sr}
    print(key, out[key]['dur'], text)
json.dump(out, open(os.path.join(B, 'audio', 'vo', 'lines.json'), 'w'), indent=1)
