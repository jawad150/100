# Floret Capitals — MT5 phone animation

A 12-second vertical video (1080×1920, 30 fps) in the style of the MT5 phone reference. A 3D iPhone 16 Pro, rendered in Blender and lying tilted over the navy `#1A1734` background, glides in one slow, continuous camera move, matching the reference. Quote cards for Gold, Silver, Crude Oil, Brent, Natural Gas, Copper and Platinum float above the screen with live-ticking red **Sell** and blue **Buy** prices. The list scrolls slowly, and cards that leave the top fold into a stacked deck. Below them, an MT5-style chart forms red and green candles in real time, and a second phone with a chart sits behind. There is no on-screen text or logo.

- **`floret_mt5_phone_vo.mp4`**: the final cut, with the voiceover *"Floret Capitals. Simplifying investments for millions of Pakistanis."* over a soft music bed and UI sound effects.
- **`floret_mt5_phone_music.mp4`**: the same video with music and sound effects but no voiceover.
- **`voiceover.wav`**: the voiceover on its own, starting at 1.1 s in the final cut.

## Rebuild

The phone is a modelled **iPhone 16 Pro** (71.5 × 149.6 × 8.25 mm, black titanium, Action/volume/side buttons, Camera Control, USB-C port and speaker holes) rendered in Blender Cycles. The MT5 UI is drawn in HTML and used as an animated texture on the display and on the floating quote-card slabs.

```bash
pip install bpy==5.2.2 numpy pillow
node floret/render.js atlas 30 12                          # UI textures, one atlas per frame + card positions
python3 floret/blender_phone.py still 1,180,360           # preview stills (PCT=50 SAMPLES=6 for quick ones)
python3 floret/blender_phone.py render 1 360              # RGBA frames (resumable; split ranges across processes)
python3 floret/composite.py                               # navy background, glow, vignette -> out/video_3d_silent.mp4
python3 floret/audio.py floret/out/mix.wav floret/voiceover.wav 1.1
ffmpeg -i floret/out/video_3d_silent.mp4 -i floret/out/mix.wav -c:v copy \
  -af loudnorm=I=-14:TP=-1.5 -c:a aac -b:a 192k -shortest floret/floret_mt5_phone_vo.mp4
```

`scene.html` holds all the UI animation: `render(t)` draws time `t`. Opened normally it shows the earlier CSS-3D version. Opened as `scene.html#atlas` it lays the screen, card faces and back-phone chart out flat for Blender.
