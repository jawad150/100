# Margin Trading 101: "Chandler Explains" carousel

| Path | What |
|---|---|
| `final/01.jpg` … `final/10.jpg` | Finished slides, 2048×2560 (4:5) |
| `final/instagram_1080/` | Same slides at 1080×1350 for Instagram / Facebook / TikTok |
| `final/margin_trading_carousel.pdf` | All 10 slides as one PDF (LinkedIn document post) |
| `raw/` | Text-free renders (GPT Image 2.5 Sunburst) + subject masks |
| `finish.py` | Finishing pipeline: Friends colour grade, 3D masked headlines, slide layouts + copy (`SLIDES`) |
| `design.py` | UI kit: liquid-glass panels, highlighter text, stickers, chat bubbles, avatars, progress footer |
| `assets/` | Chandler / Joey avatar cut-outs (from the character sheets) |
| `fonts/` | Gabriel Weiss' Friends Font (headlines; free for personal use only, see its README), Montserrat, Permanent Marker, Anton (OFL / Apache) |
| `STRATEGY.md` | Launch & distribution strategy, caption, hashtags |

Re-render a slide after editing its copy in `SLIDES` (inside `finish.py`):

    python3 finish.py cover raw/01.png final/01.jpg
    python3 finish.py slide 5 raw/05.png final/05.jpg

Needs `pillow`, `numpy`, `scipy`, `opencv-python-headless<5` (face guard), and `rembg` (only to create a missing `raw/NN_mask.png`).
