# P.S. Med Spa reel: captions, motion graphics, transitions, grade

A 41.1 s vertical reel (1080×1920, 23.976 fps) made from the supplied edit `PS-Med-Spa.mov` (2160×3840, 14 shots, 40.5 s). The cut, voice and music are kept as delivered. The last frame is held about 0.6 s so the closing words land before the fade to black. On top of them the pipeline adds a color grade, motion-graphic captions, the before/after photo cards, and transitions at every cut, styled after the reference reel.

**Output:** [`reel/medspa/PS_MedSpa_Reel_1080x1920.mp4`](../../reel/medspa/PS_MedSpa_Reel_1080x1920.mp4) · Resolve LUT: [`reel/medspa/PS_MedSpa_Look_Rec709.cube`](../../reel/medspa/PS_MedSpa_Look_Rec709.cube)

## Look

- **Brand colors:** red `#EA1D25` and charcoal `#333740`.
- **Two-line captions** follow the "using / SEO" style, with grey in place of blue:
  - a lead-in in light italic grotesk, white
  - a big serif word in a silver-grey to charcoal gradient (or brand red), placed **behind** her
  - sometimes a white italic serif line in front
- **Small word-by-word captions** in the light italic grotesk, white with a soft shadow.
- **Fonts.** Founders Grotesk Light Italic and Freight Display Pro Semibold are commercial fonts, so free stand-ins are used:
  - Founders Grotesk → **Hanken Grotesk**
  - Freight Display Pro → **Fraunces** (opsz 144, SOFT 0, WONK 0)

  To use the real fonts, drop `.ttf` or `.otf` files into `workspace/medspa/fonts/` under the names in `prep.py:FONTS` and re-render.
- **Masking.** [Robust Video Matting](https://github.com/PeterL1n/RobustVideoMatting) (MobileNetV3, ONNX) produces a per-frame person matte, with its recurrent state reset at each cut. This lets words and cards sit behind her, her hair, her arms and her gloved hands. A background motion track (phase correlation with the person masked out) pins these graphics to the wall while the camera drifts. In the doorway shot, the out-of-focus door jamb is tracked too, so "8.5" sits behind both her and the jamb. In the sitting shots, the big words start at the edge of her hair, so the first letter tucks behind her and the word stays readable.
- **Photo cards** appear while she talks about her work (15–20.8 s). The four before/after photos are rounded glass cards with soft drop shadows, tilted in 3D. Two sit behind her and two in front, joined by a glowing brand-red line, and they fly into the camera on the cut.
- **Transitions:**
  - zoom-blur push
  - white flash
  - horizontal and vertical whip
  - punch-in
  - blur dissolve
  - brand-red light leak
- **SFX.** Quiet whooshes, pops and swells sit about 16 dB under the voice. The original voice and music are untouched.

## Grade, and the S-Log note

The file as delivered is **not S-Log**. Blacks sit at about code 20, contrast is normal, and skin and logos are already saturated. Running a proper S-Log3/S-Gamut3.Cine → Rec.709 transform on it blows out the highlights and over-saturates the skin, which suggests the conversion was already applied when the edit was exported. The grade therefore starts from Rec.709 (`grade.py`):

1. **Per-shot balance.** Exposure and white balance are set in linear light, measured from neutral highlights. Most shots read slightly blue and the hallway slightly green.
2. **Look**, as a 65³ 3D LUT:
   - filmic S-curve with soft highlight roll-off and shadow detail kept in the black outfit
   - richer reds (brand red, lips)
   - skin nudged golden
   - blue gloves calmed toward cyan
   - cool shadows and warm highlights

The look is exported as `PS_MedSpa_Look_Rec709.cube` (Rec.709 in and out). It loads in DaVinci Resolve (Color page → LUTs, or a node's LUT) and was cross-checked against ffmpeg's `lut3d` to within 1 code value. DaVinci Resolve itself isn't available in this build environment (headless Linux, no GPU), so the grade is applied by the renderer, using the same LUT.

## Rebuild

```bash
pip install numpy scipy pillow "opencv-python-headless==4.10.0.84" onnxruntime faster-whisper
# workspace/medspa/src/: PS-Med-Spa.mov, pic1-4.jpg, rvm_fp16.onnx (huggingface: inverseaibd/rvm_mobilenetv3_fp16)
cd pipeline/medspa
python3 prep.py            # fonts, 1440x2560 frames, words.json (already committed)
python3 matte.py           # person mattes
python3 track.py           # background motion track
python3 render.py frames 4 # all frames
python3 sfx.py             # SFX + original audio -> mix.wav
python3 encode.py          # -> reel/medspa/PS_MedSpa_Reel_1080x1920.mp4
```

To preview stills, run `python3 render.py still 0.9,17.2,31.7` (seconds or frame numbers). `qa_sheets.py` builds labeled contact sheets plus a caption/timing table for review. Two rounds of multi-agent QA (section reviewers plus adversarial verifiers) went over legibility, masking, caption timing, Reels safe zones and the transitions. The caption timeline lives in `render.py` (`hero(...)`, `cap(...)`). It's built from the word timings in `words.json`.
