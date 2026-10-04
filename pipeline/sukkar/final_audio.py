"""Clean dialogue + SFX (no music): duck SFX under speech, gain-stage stems, preview mix, MP3s."""
import subprocess, numpy as np
SR = 48000
DUR = 49.174125
def load(p):
    a = np.frombuffer(subprocess.run(["ffmpeg", "-v", "quiet", "-i", p, "-ac", "2", "-ar", str(SR), "-f", "f32le", "-"],
                                     capture_output=True).stdout, np.float32).reshape(-1, 2)
    n = int(round(DUR * SR))
    return np.vstack([a, np.zeros((max(0, n - len(a)), 2), np.float32)])[:n].copy()
dlg, sfx = load("out/dialogue_clean_raw.wav"), load("out/sfx.wav")
# duck SFX ~5 dB while he speaks (fast attack, gentle release)
hop = 240
k = len(dlg) // hop
e = 20 * np.log10(np.sqrt((dlg[:k * hop, 0].reshape(k, hop) ** 2).mean(1)) + 1e-9)
on = (e > -38).astype(np.float32)
g = np.zeros(k, np.float32); v = 0.0
for i, s in enumerate(on):
    v += (0.35 if s > v else 0.02) * (s - v); g[i] = v
duck = np.repeat(10 ** (-5 * g / 20), hop)
duck = np.concatenate([duck, np.full(len(sfx) - len(duck), duck[-1])])
sfx *= duck[:, None]
mix = dlg + sfx
def write(p, a, codec="pcm_f32le"):
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "f32le", "-ar", str(SR), "-ac", "2", "-i", "-", "-c:a", codec, p],
                   input=a.astype(np.float32).tobytes(), check=True)
write("out/mix_v3_raw.wav", mix)
o = subprocess.run(["ffmpeg", "-hide_banner", "-i", "out/mix_v3_raw.wav", "-af", "ebur128", "-f", "null", "-"], capture_output=True, text=True).stderr
I = float(o[o.rindex("Summary:"):].split("I:")[1].split("LUFS")[0])
gain = -16.0 - I
print(f"mix integrated {I:.1f} LUFS -> gain {gain:+.1f} dB (applied to mix and both stems)")
G = 10 ** (gain / 20)
write("out/v3_dialogue.wav", dlg * G)
write("out/v3_sfx.wav", sfx * G)
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", "out/mix_v3_raw.wav", "-af",
                f"volume={gain:.2f}dB,alimiter=limit={10 ** (-1.5 / 20):.4f}:attack=5:release=60:level=disabled",
                "-c:a", "pcm_f32le", "out/v3_preview.wav"], check=True)
for src, name, title in [("out/v3_sfx.wav", "Dr_Sukkar_Hero_Reel_SFX.mp3", "SFX only (no music)"),
                         ("out/v3_dialogue.wav", "Dr_Sukkar_Hero_Reel_DIALOGUE_clean.mp3", "Dialogue (denoised)"),
                         ("out/v3_preview.wav", "Dr_Sukkar_Hero_Reel_PREVIEW_dialogue+sfx.mp3", "Preview mix: clean dialogue + SFX")]:
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", src, "-t", f"{DUR}", "-c:a", "libmp3lame", "-b:a", "320k", "-ar", str(SR),
                    "-id3v2_version", "3", "-metadata", f"title=Dr. Sukkar Hero Reel - {title}", f"deliver/{name}"], check=True)
    print("deliver/" + name)
