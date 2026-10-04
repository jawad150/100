# Dr. Sukkar — Behind the Mask (hero reel)

A 49-second hero reel at **1440×1080 (4:3)** and 23.976 fps. The size matches the reference reel. It is cut from a sit-down interview with surgical and facility B-roll. The interview audio tells the story and the B-roll builds around it. It runs: cold open → intimate OR → interview reveal → build → the facility opens up → back into the OR → hero hold → **DR. SUKKAR / BEHIND THE MASK**.

The rendered reel is not committed here, because the repository is public and this is client footage. The pipeline below rebuilds it from the Dropbox source folder.

## Edit

| Time (s) | Section | Audio | Picture |
|---|---|---|---|
| 0.0–2.3 | Cold open | Natural OR sound only, space left for music | 12 flash cuts of 4–6 frames: gloves, loupes, instruments, headlamp glare, hands, eye above the mask, movement |
| 2.3–3.3 | Breath | Room tone | IV drip sharp, surgeon soft behind it |
| 3.3–8.6 | 1 | "…to see the cornea restore someone's sight, and I helped be a part of that." | Eye above the mask → hands with forceps → implant prep → loupes (slow dissolves) |
| 9.3–14.8 | 2 | "I think the craft of plastic surgery… it's boundless. You're always getting better." | **Interview reveal** (lip-synced) → him operating → hands → him with the team (zoom-blur transitions) |
| 15.9–21.7 | 3 | "We're always still learning and chasing perfection." | Interview close-up (punch-in) → whip into a quickening montage of hands, loupes and instruments |
| 21.7–35.0 | 4 (VO, C8951) | "What we've created here is a wonderful experience, not only for the patient, but for the staff… other doctors… which they love for their patients." | Light-leak flash → exterior with the clinic sign → atrium → staff preparing a room → observing doctors → lobby from above |
| 35.0–38.7 | 5 (VO) | "Actually, I'd like to say that going to surgery is like a spa day for me…" | Dip back into the OR, slower: gloving → the mask going on (played in reverse) |
| 39.0–45.4 | 6 (VO) | "…because when I'm in surgery, I'm in control." | Hero shot of him operating, slow push-in, held about 2.6 s after the line, then fade to black |
| 45.4–49.2 | End card | Silence (for music) | DR. SUKKAR / BEHIND THE MASK |

Dialogue notes:
- **The source wording differs from the brief.** The brief quoted "to see someone who could not see and then have their sight restored". The interview actually says "to see the cornea restore someone's sight". Both exports were checked.
- **Section 5 starts on "Actually,".** "I'd" runs straight on from "actually" with no gap to cut in, so the line begins one word earlier.
- **"I think the craft…" is joined from two takes.** His first, cleanly started "I think" is spliced to "…the craft" at matching *k* closures, which removes "you know, I think".
- **Hesitations are tightened only where his face is off screen.** The on-camera stretches keep the original audio, so lip sync is unaffected.
- **Every splice was checked by re-transcribing the cut audio**, plus the final mix.

## Grade

The B-roll is Sony S-Log3 / S-Gamut3.Cine, 10-bit 4:2:2, full range, as read from the camera metadata. `grade.py` does the conversion in two steps:

1. **Technical transform:** the published S-Log3 → linear curve, then the S-Gamut3.Cine → Rec.709 matrix (it matches Sony's published coefficients), then soft gamut compression and a filmic tone curve with a toe and a soft shoulder.
2. **Look matched to the graded interview:**
   - low-key exposure, with mid grey at about 30% and whites rolled off to about 82%
   - warm mids and highlights, slightly teal shadows
   - saturated gown blues rotated toward teal and calmed down
   - a small warm push on skin tones

`clipstats.py` measures each clip's exposure and near-neutral color. `clipgrades.py` turns those measurements into per-clip exposure and white-balance trims. The facility clips open up brighter for the reveal. Everything is baked into one 65³ LUT per clip, applied inside ffmpeg at 16-bit. The LUT matches the math to about 0.13 of an 8-bit code value on average.

`bake_luts.py` also writes a 33³ **show LUT** for grading other S-Log3 clips from this shoot. A copy is in [`reel/sukkar/`](../../reel/sukkar/SukkarReel_SLog3-SGamut3Cine_to_Rec709_look.cube).

## Sound

- **Dialogue:** sections 1–3 use the vertical export's audio (the better audio), which sits 2.9645 s ahead of the horizontal export at every point checked across the 15 minutes. Sections 4–6 use C8951's camera audio. The interviewer is never used.
- **Dialogue processing:** high-pass, light FFT denoise and gentle compression. The denoiser's 24.9 ms latency is measured and removed. `synccheck.py` confirms the on-camera shots are within 5 ms.
- **Natural OR sound:** taken only from speech-free stretches (C9017, C9019, the tray part of C8894, atrium and exterior). Several clips carry OR conversation about a patient, so their audio is never used. The natural-sound stem was transcribed to confirm that no speech gets through.
- **Mix:** natural sound is ducked about 14 dB under dialogue and comes forward in the cold open, the build, the exterior and the final hero hold. Normalized linearly to −16 LUFS integrated, −1.5 dBTP. The end card is left silent for music.

### Audio v3: denoised dialogue + sound design (no music)

- **`clean_dialogue.py`:** rebuilds the dialogue on the reel timeline, then cleans it.
  - Runs DeepFilterNet3 at 48 kHz, capped at 32 dB of attenuation. The weights come from the Hugging Face mirror `fal/DeepFilterNet3`, converted to `models/DeepFilterNet3/checkpoints/`.
  - Adds high-pass and gentle EQ, de-essing and 2:1 compression.
  - Applies a downward expander keyed 24 dB below the speech level, so gaps go quiet.
  - Latency is measured as zero, so lip sync is unchanged.
- **`sfx_sukkar.py`:** synthesises the whole SFX track, so it has no noise floor. Cues come from the edit list in `reel_sukkar.py`, so every cut lands on its frame:
  - **cold open:** a glove snap, shutter ticks, steel clinks, flash pops and a riser
  - **the cut into the breath:** a hit and a single heartbeat
  - **under the OR scenes:** a soft patient-monitor beep
  - **interview transitions:** whooshes and a low thump
  - **montage:** a whip, then clinks and ticks with a riser into the flash swell
  - **facility:** shimmer, air whooshes on each dissolve and a curtain swish
  - **back in the OR:** a dip whomp, a latex stretch and snap, and mask rustle
  - **end card:** a cinematic boom with shimmer
- **`final_audio.py`:** ducks the SFX about 5 dB under speech, gain-stages both stems to the same −16 LUFS mix, and writes `SFX`, `DIALOGUE_clean` and `PREVIEW` MP3s. Each is 49.17 s, so they line up with the picture at 0:00.

## Rebuild

Run everything from a workspace folder containing `src/`. The source zip from Dropbox is larger than most free disks, so `zipstream.py` streams it and saves only what is needed. Large interview files can be saved as audio-only sparse files using the sample tables that a first pass captures.

```bash
pip install numpy scipy opencv-python-headless pillow faster-whisper matplotlib
pip install torch torchaudio --index-url https://download.pytorch.org/whl/cpu
P=path/to/pipeline/sukkar
curl -sSL "<dropbox folder link with dl=1>" | python3 $P/zipstream.py meta '\.xml$'          # list + capture MP4 indexes
#  build an audio-only plan for the two interview files with mp4index.ranges(...), then:
curl -sSL "<link>" | python3 $P/zipstream.py src '^/?C(8893|8894|8955|8956|8999|9017|9019|9028|9031)\.MP4$|C8948 \(1\)\.mov$' plan.json
python3 $P/transcribe.py "src/C8948 (1).mov" tx/C8948      # find the lines
python3 $P/align_bites.py && python3 $P/dialogue.py         # exact word boundaries -> tx/bites.json
python3 $P/clipstats.py && python3 $P/bake_luts.py          # per-clip grade LUTs
python3 $P/fetch_fonts.py
python3 $P/reel_sukkar.py --plan                            # print the edit decision list
python3 $P/reel_sukkar.py --still 12.0,23.3                 # check frames
python3 $P/reel_sukkar.py --all                             # mix + render -> out/sukkar_reel.mp4
python3 $P/synccheck.py out/mix.wav                         # lip-sync check
```
