# Work-in-progress previews (@jawad_mp4 reels)

These are **not the final reels**. They are early checks made from the layout proofs while the reels are
being built: the real reels have full motion, transitions, 3D, faces and captions.

For each reel:
- `*_animatic.mp4` - key frames held on their timestamps over the rough audio (Vlad VO + music bed + SFX).
  Watch it for the story, the VO pacing and the words on screen.
- `*_keyframes.jpg` - the same frames side by side (plus hook B for the Trial Reel and 3D props where present).
  `index.json` lists what each tile is.
- `*_rough_audio.mp3` - the rough mix (not mastered).

| # | reel | look | folder |
|---|---|---|---|
| 1 | Pehle Wala Hi Theek Tha | inferno | `1_pehle_wala/` |
| 2 | Bijli Chali Gayi | dusk | `2_bijli_chali_gayi/` |
| 3 | Ek Frame ki Keemat | ember | `3_ek_frame_ki_keemat/` |
| 4 | Beta, tum karte kya ho? | gold_hour | `4_beta_tum_karte_kya_ho/` |
| 5 | Log Kya Kahenge | noir_ember | `5_log_kya_kahenge/` |

Rebuild: `python3 pipeline/jawad_reels/tools/make_previews.py`.
