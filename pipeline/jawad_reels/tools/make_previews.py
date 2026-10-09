import os, subprocess, json, tempfile
WS='/home/user/100/workspace/jawad_reels'
OUT='/home/user/100/brand_reels/previews'
R={
 'pehle_wala': dict(n=1, title='Pehle Wala Hi Theek Tha', dur=34.133, audio=['audio/pehle_wala_A_rough_mix.wav'],
   frames=[(0,'brief_proof/A_hookA_t0.70.jpg','hook 0.7s'),(15.6,'brief_proof/B_v16_t15.60.jpg','v16 15.6s'),(22.6,'brief_proof/C_v27_t22.60.jpg','v27 mess 22.6s'),(28.5,'brief_proof/D_cover_t28.50.jpg','payoff/cover 28.5s'),(31.6,'brief_proof/E_endcard_t31.60.jpg','end card 31.6s')],
   extra=[('brief_proof/F_hookB_t0.40.jpg','hook B (trial)'),('props/sheets/pw_chai_glass_preview_ad440.jpg','3D chai glass')]),
 'bijli_chali_gayi': dict(n=2, title='Bijli Chali Gayi', dur=34.667, audio=['audio/bijli_chali_gayi_rough_A_full.wav'],
   frames=[(0,'out/brief_proofs/p0_frame0_lit_room.png','frame 0'),(0.5,'out/brief_proofs_r2/f15_power_off.png','power cut 0.5s'),(2.0,'out/brief_proofs/p1_hookA_cover_f60.png','hook/cover 2.0s'),(8.5,'out/brief_proofs/p9_rooftops_slam_8s5.png','rooftops 8.5s'),(14,'out/brief_proofs/p3_modern_desk_14s.png','editor desk 14s'),(22,'out/brief_proofs/p4_keycaps_22s.png','keycaps 22s'),(27.95,'out/brief_proofs/p5_payoff_27s95.png','payoff 28s'),(30,'out/brief_proofs/p6_power_returns_30s.png','power returns 30s'),(33,'out/brief_proofs/p7_endcard_33s.png','end card 33s')],
   extra=[('out/brief_proofs/p8_hookB_f30.png','hook B (trial)'),('out/sheets3d/bcg_finals_contact_0.png','3D props')]),
 'ek_frame_ki_keemat': dict(n=3, title='Ek Frame ki Keemat', dur=33.6, audio=['vo/vo_stem.wav','music/music_full.wav','audio/ek_frame_ki_keemat_sfx_stem.wav'],
   frames=[(0,'previs/B1_f0.png','frame 0 / hook'),(5.1,'previs/F1_cover_5p1_safe.png','12 layers / cover 5.1s'),(7.8,'previs/F2_fly_7p8_safe.png','fly-through 7.8s'),(13.2,'previs/F3_rehook_13p2_safe.png','re-hook 13.2s'),(16.0,'previs/R2_rehook_16p0.png','16.0s'),(26.4,'previs/B2_payoff.png','payoff 26.4s'),(29.4,'previs/B3_card.png','end card 29.4s')],
   extra=[('previs/sheet_final.jpg','contact sheet')]),
 'beta_tum_karte_kya_ho': dict(n=4, title='Beta, tum karte kya ho?', dur=36.4, audio=['audio/rough/beta_tum_karte_kya_ho_mix.wav'],
   frames=[(0,'brief_proof/A_f000.jpg','frame 0'),(1.0,'brief_proof/A_f030_caps.jpg','hook 1.0s'),(5.6,'brief_proof/card_wedding_5p6.jpg','wrong genre 1 5.6s'),(8.0,'brief_proof/jd_shocked_8p0.jpg','JD shocked 8.0s'),(9.6,'brief_proof/card_stamp_9p6.jpg','stamp 9.6s'),(13.0,'brief_proof/card_killer_13p0.jpg','killer 13s'),(14.7,'brief_proof/jd_neutral_14p7.jpg','JD 14.7s'),(22.8,'brief_proof/chat_22p8.jpg','chat 22.8s'),(25.0,'brief_proof/chat_25p0.jpg','chat 25s'),(28.5,'brief_proof/payoff_28p5.jpg','payoff 28.5s'),(31.8,'brief_proof/payoff_31p8.jpg','31.8s'),(34.5,'brief_proof/end_34p5.jpg','end card 34.5s')],
   extra=[('brief_proof/B_f000.jpg','hook B (trial)')]),
 'log_kya_kahenge': dict(n=5, title='Log Kya Kahenge', dur=35.2, audio=['audio/final/log_kya_kahenge_mix.wav'],
   frames=[(0,'layout_proofs/p1_hookA_cover_1.5s.jpg','hook/cover 1.5s'),(8.9,'layout_proofs/p3_judgement_8.9s.jpg','judgement 8.9s'),(9.8,'layout_proofs/p6_S3_jd_small_9.8s.jpg','JD 9.8s'),(27.5,'layout_proofs/p4_payoff_27.5s.jpg','payoff 27.5s'),(33.8,'layout_proofs/p5_endcard_33.8s.jpg','end card 33.8s')],
   extra=[('layout_proofs/p2_hookB_1.0s.jpg','hook B (trial)')]),
}
def run(c): subprocess.run(c, check=True, capture_output=True)
for slug,c in R.items():
    src=f'{WS}/{slug}'; od=f'{OUT}/{c["n"]}_{slug}'; os.makedirs(od,exist_ok=True)
    fr=[(t,f'{src}/{p}',lab) for t,p,lab in c['frames'] if os.path.exists(f'{src}/{p}')]
    # audio
    aud=[f'{src}/{a}' for a in c['audio'] if os.path.exists(f'{src}/{a}')]
    mp3=f'{od}/{slug}_rough_audio.mp3'
    if len(aud)==1:
        run(['ffmpeg','-y','-i',aud[0],'-t',str(c['dur']),'-ac','2','-ar','44100','-b:a','160k',mp3])
    elif len(aud)>1:
        ins=sum([['-i',a] for a in aud],[])
        vols=['1.0','0.32','0.7'][:len(aud)]
        fc=''.join(f'[{i}:a]aformat=channel_layouts=stereo,aresample=48000,volume={v}[a{i}];' for i,v in enumerate(vols))
        fc+=''.join(f'[a{i}]' for i in range(len(aud)))+f'amix=inputs={len(aud)}:normalize=0,loudnorm=I=-14:TP=-2[m]'
        run(['ffmpeg','-y',*ins,'-filter_complex',fc,'-map','[m]','-t',str(c['dur']),'-ar','44100','-b:a','160k',mp3])
    # animatic
    lst=os.path.join(tempfile.mkdtemp(),'l.txt')
    with open(lst,'w') as f:
        for i,(t,p,lab) in enumerate(fr):
            nxt=fr[i+1][0] if i+1<len(fr) else c['dur']
            f.write(f"file '{p}'\nduration {max(0.2,nxt-t):.3f}\n")
        f.write(f"file '{fr[-1][1]}'\n")
    mp4=f'{od}/{slug}_animatic.mp4'
    vf='scale=540:960:force_original_aspect_ratio=decrease,pad=540:960:(ow-iw)/2:(oh-ih)/2,fps=30,format=yuv420p'
    cmd=['ffmpeg','-y','-f','concat','-safe','0','-i',lst]
    if os.path.exists(mp3): cmd+=['-i',mp3,'-map','0:v','-map','1:a','-c:a','aac','-b:a','128k']
    cmd+=['-vf',vf,'-c:v','libx264','-crf','24','-preset','veryfast','-t',str(c['dur']),'-movflags','+faststart',mp4]
    run(cmd)
    # keyframe sheet
    imgs=[p for _,p,_ in fr]+[f'{src}/{p}' for p,_ in c['extra'] if os.path.exists(f'{src}/{p}')]
    ins=sum([['-i',p] for p in imgs],[]); n=len(imgs); cols=min(5,n); rows=(n+cols-1)//cols
    fc=''.join(f'[{i}:v]scale=324:576:force_original_aspect_ratio=decrease,pad=324:576:(ow-iw)/2:(oh-ih)/2:color=black[v{i}];' for i in range(n))
    for i in range(n, rows*cols): pass
    layout='|'.join(f'{(i%cols)*324}_{(i//cols)*576}' for i in range(n))
    fc+=''.join(f'[v{i}]' for i in range(n))+f'xstack=inputs={n}:layout={layout}:fill=black[o]'
    run(['ffmpeg','-y',*ins,'-filter_complex',fc,'-map','[o]','-frames:v','1','-q:v','4',f'{od}/{slug}_keyframes.jpg'])
    labels=[lab for _,_,lab in fr]+[lab for p,lab in c['extra'] if os.path.exists(f'{src}/{p}')]
    json.dump({'title':c['title'],'tiles_left_to_right':labels,'audio_sources':[os.path.relpath(a,WS) for a in aud]},open(f'{od}/index.json','w'),indent=1)
    print(slug, len(fr),'frames', 'audio' if aud else 'NO AUDIO', os.path.getsize(mp4)//1024,'KB')
