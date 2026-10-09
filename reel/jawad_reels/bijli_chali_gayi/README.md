# @jawad_mp4 reel: bijli_chali_gayi

Contact sheet, loop seam and f60 cover checked; new ending (Jawad 2026-10-09): Genjutsu-style profile outro with the question 'Aap ke ghar light jaane pe kya hota tha? / Chhat ya candle?', spliced from f920; ebur128 -14.0 LUFS.

| file | size | what it is | measured |
|---|---|---|---|
| `jawad_bijli_chali_gayi_ig.mp4` | 87.2 MB | Instagram Reels upload (version A: VO + SFX + original music) | 1080x1920 30 fps, h264 High 19.8 Mbps, aac 48000 Hz 321 kbps; 34.667 s; -13.9 LUFS, LRA 2.9, TP -2.4 dBTP |
| `jawad_bijli_chali_gayi_ig_songready.mp4` | 87.2 MB | same picture, version B audio (VO + SFX only): add a trending song in-app | 1080x1920 30 fps, h264 High 19.8 Mbps, aac 48000 Hz 321 kbps; 34.667 s; -13.9 LUFS, LRA 2.9, TP -1.9 dBTP |
| `jawad_bijli_chali_gayi_master.mp4` | 89.9 MB | CRF 14 master, version A audio | 1080x1920 30 fps, h264 High 20.4 Mbps, aac 48000 Hz 321 kbps; 34.667 s; -13.9 LUFS, LRA 2.9, TP -2.4 dBTP |
| `stems/jawad_bijli_chali_gayi_stem_vo.wav` | 10.0 MB | VO stem at the A mix gains (48 kHz 24-bit) | -14.3 LUFS, TP -3.3 dBTP |
| `stems/jawad_bijli_chali_gayi_stem_sfx.wav` | 10.0 MB | sfx stem at the A mix gains (48 kHz 24-bit) | -17.0 LUFS, TP -2.3 dBTP |
| `stems/jawad_bijli_chali_gayi_stem_music.wav` | 10.0 MB | music stem at the A mix gains (48 kHz 24-bit) | -15.2 LUFS, TP -2.2 dBTP |
| `jawad_bijli_chali_gayi_cover.jpg` | 191.4 KB | cover frame 2.00 s (1080x1920) | |
| `jawad_bijli_chali_gayi_cover_grid_3x4.jpg` | 167.9 KB | 3:4 profile-grid crop (y 240-1680) | |
| `jawad_bijli_chali_gayi_caption.txt` | 0.4 KB | IG caption, comment prompt, hashtags, AI info note | |
| `jawad_bijli_chali_gayi.srt` | 1.3 KB | Roman Urdu captions (SRT) | |

All videos 1080x1920, 30 fps, duration 34.667 s +- 1 frame, -14 LUFS +- 0.5, TP <= -1.5 dBTP: PASS. CRF 14 master was >= 94 MB: re-encoded at CRF 14 -maxrate 20M -bufsize 40M.

Known minor items (listed, not re-rendered; LEAD_DECISIONS 7):

- Cover: the indigo window region (x 720-1010, y 300-900) averages luma 17.6, above the brief's 10, because the glow of the Bijli lockup spills into it; the window bars themselves stay dark.
- Mix is the sound-designer rough A FULL (VO + SFX + music bed, -14 LUFS); B (song-ready) is A DRY (VO + SFX). Version A runs through a -3 dBTP true-peak limiter (max 0.7 dB gain reduction) before the mux, because AAC pushed the plain mix to -1.4 dBTP; the stems are pre-limiter.
