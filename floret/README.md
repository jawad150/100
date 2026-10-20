# Floret Capitals — MT5 phone animation

A 10-second vertical video (1080×1920, 30 fps) matched shot-for-shot to the MT5 phone reference, on the navy `#1A1734` background, with no on-screen text or logo.

- **Phone:** a silver iPhone 16 Pro modelled in Blender. It lies on a steep diagonal, turned on its long axis so its silver left side and buttons face the camera. A second iPhone with a red/green candle chart sits behind it.
- **Quote cards:** Gold, Silver, Crude Oil, Brent and Natural Gas start as a normal list lying in the screen, then pop out of the glass one after another into floating cards. All the cards share the same size, tilt and left edge, with equal gaps, and show live red **Sell** and blue **Buy** prices.
- **Camera:** it slides slowly and steadily up the phone's long axis.

The camera pose, card poses and timing were measured from the reference. Landmarks such as the status bar, the phone edges and the card corners were solved through a pinhole camera model, then verified by overlaying renders on reference frames at 2, 4, 6 and 9 s.

- **`floret_mt5_phone_vo.mp4`**: the final cut, with the voiceover *"Floret Capitals. Simplifying investments for millions of Pakistanis."* over a soft music bed and UI sound effects.
- **`floret_mt5_phone_music.mp4`**: the same video with music and sound effects but no voiceover.
- **`voiceover.wav`**: the voiceover on its own, starting at 1.1 s in the final cut.

## Rebuild

The phone is a modelled **iPhone 16 Pro** (71.5 × 149.6 × 8.25 mm, natural silver titanium, Action/volume/side buttons, Camera Control, USB-C port and speaker holes) rendered in Blender Cycles. The MT5 UI is drawn in HTML and used as an animated texture on the display and on the floating quote-card slabs.

```bash
pip install bpy==5.2.2 numpy pillow
node floret/render.js atlas 30 10                          # UI textures (ui_atlas.html), one atlas per frame
python3 floret/blender_phone.py still 1,150,300           # preview stills (PCT=40 SAMPLES=4 for quick ones)
python3 floret/blender_phone.py render 1 300              # RGBA frames (resumable; split ranges across processes)
python3 floret/composite.py                               # navy background, glow, vignette -> out/video_3d_silent.mp4
python3 floret/audio.py floret/out/mix.wav floret/voiceover.wav 1.1
ffmpeg -i floret/out/video_3d_silent.mp4 -i floret/out/mix.wav -c:v copy \
  -af loudnorm=I=-14:TP=-1.5 -c:a aac -b:a 192k -shortest floret/floret_mt5_phone_vo.mp4
```

`ui_atlas.html` draws the UI (screen, card faces and back-phone chart, laid out flat) at time `t` via `render(t)`. `blender_phone.py` holds the fitted camera and card keyframes (`POSE`, `PHONE_POS`/`PAN`, `CARD_KEYS`). `scene.html` is the earlier CSS-only version.

## SaaS motion-graphics cut

**`floret_saas_vo.mp4`** (voiceover) and **`floret_saas_music.mp4`** (music only). This is an 11-second version with the same iPhone, products, Sell/Buy buttons, chart and navy background. It is presented in an original motion-graphics style rather than as a recreation of the reference shot.

| Time | Shot |
|---|---|
| 0.0–2.2 s | **Reveal.** The upright phone turns from edge-on to face the camera while the camera pushes in. The quote list lies flat. |
| 2.2–4.6 s | **Pop.** A low wide-angle shot skims the glass while the cards pop out toward the camera. Focus racks to each card as it rises. |
| 4.6–6.6 s | **Tap.** A macro shot on the Gold card glides from Sell to Buy. The Buy button is tapped (press, ripple, glow ring) while the other cards dim. |
| 6.6–8.6 s | **Chart.** A tracking shot runs across the red and green candles on the second phone. |
| 8.6–11.0 s | **Hero.** A three-quarter angle, mirrored from the reference, shows all five cards floating evenly while the camera pulls back slowly. |

Every cut has a white flash, a zoom punch and a light sweep. The sound effects (whooshes, card pops, a tap click) are synced to the cuts.

```bash
ATLAS_HASH='#tap=0:5.6' OUT=floret/out node floret/render.js atlas 30 11
python3 floret/saas_film.py render 1 330
python3 floret/composite_saas.py
SFX=saas DUR=11 python3 floret/audio.py floret/out/mix.wav floret/voiceover.wav 1.3
```
