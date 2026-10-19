# Floret Capitals — MT5 phone animation

A 12-second vertical video (1080×1920, 60 fps) in the style of the MT5 phone reference. A 3D-tilted phone flies in over the navy `#1A1734` background. Quote cards for Gold, Silver, Crude Oil, Brent, Natural Gas, Copper and Platinum rise off the screen with live-ticking red **Sell** and blue **Buy** prices. Below them, an MT5-style chart forms red and green candles in real time, and a second phone with a chart sits behind. There is no on-screen text or logo.

- **`floret_mt5_phone_vo.mp4`**: the final cut, with the voiceover *"Floret Capitals. Simplifying investments for millions of Pakistanis."* over a soft music bed and UI sound effects.
- **`floret_mt5_phone_music.mp4`**: the same video with music and sound effects but no voiceover.
- **`voiceover.wav`**: the voiceover on its own, starting at 1.1 s in the final cut.

## Rebuild

```bash
node floret/render.js still 1,4,8           # preview stills -> floret/out/stills
node floret/render.js video 60 12           # -> floret/out/video_silent.mp4
python3 floret/audio.py floret/out/mix.wav floret/voiceover.wav 1.1
ffmpeg -i floret/out/video_silent.mp4 -i floret/out/mix.wav -c:v copy \
  -af loudnorm=I=-14:TP=-1.5 -c:a aac -b:a 192k -shortest floret/floret_mt5_phone_vo.mp4
```

`scene.html` is the whole animation. It is plain HTML/CSS 3D plus canvas, and `render(t)` draws the frame at time `t`. Open it in a browser and call `render(4)` from the console to inspect any moment.
