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

**`floret_saas_vo.mp4`** (Hinglish voiceover: "Floret Capitals… investment ko banaya aasaan, lakhon Pakistaniyon ke liye"), **`floret_saas_vo_voice2.mp4`** (the original English line, "Floret Capitals. Simplifying investments for millions of Pakistanis", read with a desi accent) and **`floret_saas_music.mp4`** (music only). The voiceover takes are `voiceover.wav` and `voiceover_voice2.wav`. They are ElevenLabs reads with the line written in Devanagari script so the voice speaks with a native Urdu/Hindi accent. Each starts 1.0 s in. This is an 11-second version with the same iPhone, products, Sell/Buy buttons, chart and navy background. It is presented in an original motion-graphics style rather than as a recreation of the reference shot.

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
SFX=saas DUR=11 python3 floret/audio.py floret/out/mix.wav floret/voiceover.wav 1.0
```

## 15-second app promo (`floret_app_15s`)

The finished versions of the supplied `floret_app_15s.mp4`:

- **`floret_app_15s_final.mp4`**: the main version, with the ElevenLabs "Mark" voice.
- **`floret_app_15s_final_voice2.mp4`**: the same video with the "Julian" voice.

What was added:

- **Voiceover (0.5–4.7 s):** "Floret Capitals. Simplifying investments for millions of Pakistanis." It opens the video, under the headline.
- **Headline (about 1.0–9.6 s):** "One platform" (white) over "Multiple markets" (logo gold) at the bottom left, on a black gradient. It fades out before the phone fills that corner.
- **Tagline (from 13.1 s):** "Simplifying investments for millions of Pakistanis", under the logo once it is fully drawn.
- **Audio:** the music bed and the voice only. The video's original sound effects are removed; pass `SFX=1` to keep them.
- **Music:** an original track (`music_app15.wav`, from `music_app15.py`) at 122.6 BPM, so that beat 24 hits the logo reveal. It has a pad and reverse-cymbal swell intro, then a groove with a layered kick, clap, hats, shaker and sidechained bass. Over that sit a supersaw pad with an opening filter, a ping-pong arpeggio and a bell hook, followed by a riser and snare roll, then an impact with a held C(add9) chord for the logo. It is mixed with reverb and mastered with glue compression and a limiter. The music dips under the voice, and the final mix is set to -14 LUFS with peaks at about -1.5 dB.

```bash
python3 floret/music_app15.py floret/music_app15.wav
MUSIC=floret/music_app15.wav python3 floret/finish_app15.py floret_app_15s.mp4 <voiceover.mp3> floret/floret_app_15s_final.mp4
```

### Text-style variations (`floret_app_15s_style1-4.mp4`)

Each variation has the top headline "One Platform for Multiple Markets" from 0.6 s, the bottom CTA "Start trading today with Floret Capitals" from 4.9 s (both out by 10.85 s, before the phone fills the frame), and the end tagline under the logo. All text stays inside the Reels safe area: the top 250 px, bottom 420 px and the right-hand button column are kept clear. The text sits on deep black gradients (about 92 % black at the top, about 94 % at the bottom). The audio is the finished voice-and-music mix, copied unchanged.

| Style | Fonts | Colours | Motion |
|---|---|---|---|
| 1 Fintech Clean | Plus Jakarta Sans ExtraBold / Bold / Medium | white + electric blue | left-aligned masked slide-ups, accent bar, drawn arrow |
| 2 Editorial Premium | DM Serif Display roman + italic, Montserrat tracked caps | ivory + champagne gold | soft blur-in, gold rules and a diamond |
| 3 Bold Impact | Poppins Black / ExtraBold caps | white + navy on a brand-gold highlight | pop-in, highlight wipe, frosted CTA card that springs up |
| 4 Serif Accent | Inter Regular over Instrument Serif roman + italic | white + brand-gold italic accent | words rise in one by one |

The fonts are in `floret/fonts`, all under the SIL Open Font License (licences included), so they are free for commercial use.

```bash
python3 floret/text_styles_app15.py floret_app_15s.mp4 floret/floret_app_15s_final.mp4 floret 1,2,3,4
```
