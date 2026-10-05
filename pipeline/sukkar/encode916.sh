#!/bin/bash
# master (high quality picture + 320k AAC) and a review copy that fits a 30 MiB upload
set -e
V=out/sukkar_916_video.mp4
A=out/v3_preview.wav
ffmpeg -v error -y -i $V -i $A -map 0:v -map 1:a -c:v copy -c:a aac -b:a 320k -shortest -movflags +faststart \
  out/Dr_Sukkar_Behind_The_Mask_Reel_9x16_master.mp4
cd v916
ffmpeg -v error -y -i ../$V -c:v libx264 -preset slow -b:v 4600k -maxrate 9000k -bufsize 12000k -pass 1 -passlogfile x264r \
  -an -f mp4 /dev/null
ffmpeg -v error -y -i ../$V -i ../$A -map 0:v -map 1:a -c:v libx264 -preset slow -b:v 4600k -maxrate 9000k -bufsize 12000k \
  -pass 2 -passlogfile x264r -color_primaries bt709 -color_trc bt709 -colorspace bt709 \
  -c:a aac -b:a 192k -shortest -movflags +faststart ../deliver/Dr_Sukkar_Behind_The_Mask_Reel_9x16_review.mp4
cd ..
ls -la out/Dr_Sukkar_Behind_The_Mask_Reel_9x16_master.mp4 deliver/Dr_Sukkar_Behind_The_Mask_Reel_9x16_review.mp4
