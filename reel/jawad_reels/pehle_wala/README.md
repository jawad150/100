# @jawad_mp4 reel: pehle_wala

QA passed (session 5): full-quality master checked on a 16-frame sheet, cover, payoff, end card and the loop seam; audio A/B -14.0 LUFS, TP -2.3 dBTP in the wav, epic_mix checks all OK, VO 10.7 LU over the bed.

| file | size | what it is | measured |
|---|---|---|---|
| `jawad_pehle_wala_ig.mp4` | 86.5 MB | Instagram Reels upload (version A: VO + SFX + original music) | 1080x1920 30 fps, h264 High 19.9 Mbps, aac 48000 Hz 330 kbps; 34.133 s; -13.9 LUFS, LRA 2.3, TP -2.2 dBTP |
| `jawad_pehle_wala_ig_songready.mp4` | 86.4 MB | same picture, version B audio (VO + SFX only): add a trending song in-app | 1080x1920 30 fps, h264 High 19.9 Mbps, aac 48000 Hz 317 kbps; 34.133 s; -13.9 LUFS, LRA 3.2, TP -2.1 dBTP |
| `jawad_pehle_wala_master.mp4` | 88.8 MB | CRF 14 master, version A audio | 1080x1920 30 fps, h264 High 20.5 Mbps, aac 48000 Hz 330 kbps; 34.133 s; -13.9 LUFS, LRA 2.3, TP -2.2 dBTP |
| `stems/jawad_pehle_wala_stem_vo.wav` | 9.8 MB | VO stem at the A mix gains (48 kHz 24-bit) | -14.4 LUFS, TP -1.9 dBTP |
| `stems/jawad_pehle_wala_stem_sfx.wav` | 9.8 MB | sfx stem at the A mix gains (48 kHz 24-bit) | -18.3 LUFS, TP -1.8 dBTP |
| `stems/jawad_pehle_wala_stem_music.wav` | 9.8 MB | music stem at the A mix gains (48 kHz 24-bit) | -21.1 LUFS, TP -3.5 dBTP |
| `jawad_pehle_wala_cover.jpg` | 388.4 KB | cover frame 28.50 s (1080x1920) | |
| `jawad_pehle_wala_cover_grid_3x4.jpg` | 330.7 KB | 3:4 profile-grid crop (y 240-1680) | |
| `jawad_pehle_wala_caption.txt` | 0.5 KB | IG caption, comment prompt, hashtags, AI info note | |
| `jawad_pehle_wala.srt` | 0.9 KB | Roman Urdu captions (SRT) | |

All videos 1080x1920, 30 fps, duration 34.133 s +- 1 frame, -14 LUFS +- 0.5, TP <= -1.5 dBTP: PASS. CRF 14 master was >= 94 MB: re-encoded at CRF 14 -maxrate 20M -bufsize 40M.

Known minor items (listed, not re-rendered; LEAD_DECISIONS 7):

- Hook B (Trial Reel version) not built: bonus per LEAD_DECISIONS 6.
- The last frame carries the faded end card and the incoming caption ghost (loop cross-fade, by design).
