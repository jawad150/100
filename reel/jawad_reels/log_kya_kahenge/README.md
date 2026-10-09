# @jawad_mp4 reel: log_kya_kahenge

QA passed (session 5): full-quality master checked on a 16-frame sheet, the reveal, payoff, end card and the loop seam (f1055 -> f0 continuous); audio A/B -14.0 LUFS, TP -2.3 dBTP in the wav, reveal is the loudest moment (+3.8 LU), every VO line >= 8.5 LU over the bed, loop seam click-free.

| file | size | what it is | measured |
|---|---|---|---|
| `jawad_log_kya_kahenge_ig.mp4` | 86.6 MB | Instagram Reels upload (version A: VO + SFX + original music) | 1080x1920 30 fps, h264 High 19.4 Mbps, aac 48000 Hz 320 kbps; 35.200 s; -14.0 LUFS, LRA 3.8, TP -1.8 dBTP |
| `jawad_log_kya_kahenge_ig_songready.mp4` | 86.6 MB | same picture, version B audio (VO + SFX only): add a trending song in-app | 1080x1920 30 fps, h264 High 19.4 Mbps, aac 48000 Hz 314 kbps; 35.200 s; -14.0 LUFS, LRA 6.2, TP -2.0 dBTP |
| `jawad_log_kya_kahenge_master.mp4` | 91.4 MB | CRF 14 master, version A audio | 1080x1920 30 fps, h264 High 20.4 Mbps, aac 48000 Hz 320 kbps; 35.200 s; -14.0 LUFS, LRA 3.8, TP -1.8 dBTP |
| `stems/jawad_log_kya_kahenge_stem_vo.wav` | 10.1 MB | VO stem at the A mix gains (48 kHz 24-bit) | -14.2 LUFS, TP -1.5 dBTP |
| `stems/jawad_log_kya_kahenge_stem_sfx.wav` | 10.1 MB | sfx stem at the A mix gains (48 kHz 24-bit) | -17.8 LUFS, TP -2.3 dBTP |
| `stems/jawad_log_kya_kahenge_stem_music.wav` | 10.1 MB | music stem at the A mix gains (48 kHz 24-bit) | -21.1 LUFS, TP -4.7 dBTP |
| `jawad_log_kya_kahenge_cover.jpg` | 299.0 KB | cover frame 1.50 s (1080x1920) | |
| `jawad_log_kya_kahenge_cover_grid_3x4.jpg` | 252.6 KB | 3:4 profile-grid crop (y 240-1680) | |
| `jawad_log_kya_kahenge_caption.txt` | 0.5 KB | IG caption, comment prompt, hashtags, AI info note | |
| `jawad_log_kya_kahenge.srt` | 0.9 KB | Roman Urdu captions (SRT) | |

All videos 1080x1920, 30 fps, duration 35.200 s +- 1 frame, -14 LUFS +- 0.5, TP <= -1.5 dBTP: PASS. CRF 14 master was >= 94 MB: re-encoded at CRF 14 -maxrate 20M -bufsize 40M.

Known minor items (listed, not re-rendered; LEAD_DECISIONS 7):

- Hook B (Trial Reel version) not packaged: bonus per LEAD_DECISIONS 6.
- Frame 0 starts on the hook's impact, so the first 50 ms are ~8 dB louder than the last 50 ms (by design; no click at the seam).
- Mix LRA 3.8 LU: inside LEAD_DECISIONS 1 (2-9 LU), below the older bible's 5-9.
