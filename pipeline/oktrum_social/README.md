# Oktrum reel covers and captions

- `CAPTIONS.md`: Instagram captions + hashtags for the three Oktrum reels (approved copy only).
- `thumbs/`: covers, 9:16 (1080x1920) for Reels and 4:5 (1080x1350) for the feed grid.
- `thumbs.py`: the compositor (PIL/numpy), styled after JAWAD's dark "big serif word + hero object" references.
- `assets/`: the hero renders it uses, made with `r.py`, a wrapper around `pipeline/oktrum/assets3d_oktrum.py`
  (branch `claude/oktrum-reels-mtrnnc`) that renders one frame of a prop at a chosen size and variant.

Rebuild:
```bash
pip install bpy scipy opencv-python-headless pillow numpy      # bpy 5.2 for Python 3.13
FOSTER_WS=/tmp/ws OKT_THREADS=4 python3 r.py <path>/pipeline/oktrum shield_lock night yaw 30 48 1150
# fonts dir needs IS-Regular.ttf (Instrument Serif), IT-Medium.ttf / IT-SemiBold.ttf (Inter Tight)
python3 thumbs.py assets <fonts_dir> thumbs
```
