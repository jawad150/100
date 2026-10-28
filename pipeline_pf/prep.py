"""Portfolio media prep: curated manifest -> web-sized images, video posters and compressed video previews.

Usage: python3 prep.py   (writes workspace_pf/site/media/* and workspace_pf/site/works.json)
"""
import os, json, subprocess, sys
import cv2
from concurrent.futures import ThreadPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))
WS = os.path.abspath(os.path.join(HERE, '..', 'workspace_pf'))
A = f'{WS}/raw/MY all work/All work'
D = f'{WS}/raw/MY all work/Designs'
C = f'{WS}/raw_carousel'
G = f'{WS}/raw_drive'
REEL = os.path.abspath(os.path.join(HERE, '..', 'reel'))
OUT = f'{WS}/site/media'

# (id, category, client, title, note, source(s))
WORKS = [
    # ---- AI commercials
    ('b-football', 'ai', 'Bodyrade', 'Match Day', 'Stadium spot for an energy drink: AI-generated scenes, product hero shots and edit.', f'{A}/bodyrade videos/bodyrade football video (1).mp4'),
    ('b-padel', 'ai', 'Bodyrade', 'Padel', 'Athlete-led sports commercial, 4K vertical, built shot by shot with generative video.', f'{A}/bodyrade videos/bodyrade padel 2.0/bodyrade padel 2.0.mp4'),
    ('b-dumble', 'ai', 'Bodyrade', 'Gym Pouch', 'Product launch film for the protein pouch, staged in a cinematic gym.', f'{A}/bodyrade videos/Dumble video.mp4'),
    ('b-ugc', 'ai', 'Bodyrade', 'UGC Ad', 'Creator-style ad with a consistent AI presenter across every scene.', f'{A}/bodyrade videos/ugc video.mp4'),
    ('b-fresh', 'ai', 'Bodyrade', 'Load the Capsule', 'Motion-graphics product explainer for the shaker capsule.', f'{A}/bodyrade videos/bodyrade_fresh_share.mp4'),
    ('b-morning', 'ai', 'Bodyrade', 'Morning to Gym', 'Lifestyle story ad following one routine from breakfast to workout.', f'{A}/bodyrade videos/Adobe Express 2026-09-07 17.55.06.mp4'),
    ('b-city', 'ai', 'Bodyrade', 'City Run', 'Fast-cut urban running spot ending on the product line-up.', f'{A}/bodyrade videos/Adobe Express 2026-09-07 22.15.54.mp4'),
    ('b-powder', 'ai', 'Bodyrade', 'Powder Drop', 'Short product teaser: slow-motion powder and bottle reveal.', f'{A}/bodyrade videos/bodygrade.mp4'),
    ('b-drop', 'ai', 'Bodyrade', 'Street Drop', 'Fashion-led street campaign with a product drop finale.', f'{A}/bodyrade videos/bodyrade drop video.mp4'),
    ('b-rooftop', 'ai', 'Bodyrade', 'Rooftop Drop', 'Vertical hook video: the pouch lands on a city rooftop.', f'{A}/bodyrade videos/spidey video2.mp4'),
    ('b-cat', 'ai', 'Bodyrade', 'Gym Buddy', 'Playful social short built to stop the scroll.', f'{A}/bodyrade videos/cat.mp4'),
    ('mp-launch', 'ai', 'Muddy Panda', 'Launch Film', 'Streetwear launch film with AI-generated models and set pieces.', f'{G}/muddy_panda_final.mp4'),
    ('mp-merch', 'ai', 'Muddy Panda', 'Merch Collection', 'Product video for the merch range: hoodies, tees and bottles.', f'{G}/muddy_panda_product_1.mp4'),
    ('mp-box', 'ai', 'Muddy Panda', 'Unboxing', 'Unboxing-style product reveal for the gift box.', f'{G}/muddy_panda_product_2.mp4'),
    ('pd-reel', 'ai', 'Property Deals', 'Presenter Reel', 'Property marketing reel with an AI presenter and kinetic captions.', f'{G}/property_deals.mp4'),
    # ---- motion reels (voiceover, word-synced pop-ups)
    ('of-canif', 'motion', 'Organic Fostering', 'Can I Foster If…?', 'Phone-UI story answering five real FAQ doubts, word-synced captions and 3D props.', f'{REEL}/organic_fostering/organic_fostering_can_i_foster_if_share.mp4'),
    ('of-year', 'motion', 'Organic Fostering', 'A Year in Fostering', 'Year-in-review reel with 3D icons and a warm voiceover.', f'{A}/Organic foresting/Videos/organic_fostering_year_in_fostering_share.mp4'),
    ('of-flow', 'motion', 'Organic Fostering', 'Fostering Flow', 'Step-by-step journey to becoming a foster carer.', f'{A}/Organic foresting/Videos/organic_fostering_fostering_flow_share (1).mp4'),
    ('of-support', 'motion', 'Organic Fostering', 'Support Update', 'SaaS-style product update showing the support carers receive.', f'{A}/Organic foresting/Videos/organic_fostering_support_update_share (1).mp4'),
    ('of-day', 'motion', 'Organic Fostering', 'A Day in the Life', 'A foster carer\'s day, animated with brand illustrations.', f'{A}/Organic foresting/Videos/organic_fostering_day_in_the_life_vo_send.mp4'),
    ('of-anim', 'motion', 'Organic Fostering', 'Brand Animation', 'Short animated story piece with voiceover and music.', f'{A}/Organic foresting/Videos/anim1_vo_music_preview.mp4'),
    ('ic-sqe', 'motion', 'IC London', 'What Is the SQE?', 'Explainer reel with real people and word-synced 3D pop-ups.', f'{A}/ICD london/ic_london_what_is_the_sqe_share.mp4'),
    ('ic-cv', 'motion', 'IC London', 'Three CV Mistakes', 'Cinematic tips reel for law students.', f'{A}/ICD london/ic_london_cv_mistakes_v2_share.mp4'),
    ('ic-law', 'motion', 'IC London', 'No Law Degree?', '30-second reel on routes into law without a law degree.', f'{A}/ICD london/ic_london_no_law_degree_share.mp4'),
    ('bmhc', 'motion', 'British Muslim Heritage Centre', 'The First Word', 'Heritage story reel: people, archive photos and 3D props.', f'{A}/Bmhc/bmhc_the_first_word_share.mp4'),
    # ---- social design
    ('hm-cafe', 'social', 'Hulk Marketing', 'You Built the Business', 'Agency ad for local businesses: after-hours café scene.', f'{A}/Hulk marekting/static post/After-Hours Cafe#U0301 Marketing Glow.png'),
    ('hm-find', 'social', 'Hulk Marketing', 'Be the Business They Find', 'Agency ad: neon shopfront, search-visibility message.', f'{A}/Hulk marekting/static post/Be the Business They Find (1).png'),
    ('hm-first', 'social', 'Hulk Marketing', 'Different First Impression', 'Agency ad comparing two versions of the same business online.', f'{A}/Hulk marekting/static post/Same Business, Different First Impression.png'),
    ('of-carousel', 'social', 'Organic Fostering', 'Think You Can\'t Foster?', 'Five-slide recruitment carousel busting common myths.',
     [f'{C}/Slide 1 · Think you can’t foster.png', f'{C}/Slide 2 · Renting is fine.png', f'{C}/Slide 3 · All backgrounds welcome.png',
      f'{C}/Slide 4 · No experience needed.png', f'{C}/Slide 5 · Enquire with no obligation.png']),
    ('of-caring', 'social', 'Organic Fostering', 'Caring Homes, Brighter Futures', 'Recruitment post with an illustrated checklist of what carers do.', f'{A}/Organic foresting/Static post/Caring Homes, Brighter Futures.png'),
    ('of-teen', 'social', 'Organic Fostering', 'Fostering Teenagers', 'Post on fostering teenagers, phone-chat storytelling.', f'{A}/Organic foresting/Static post/Fostering Teenagers Looks Like This.png'),
    ('of-room', 'social', 'Organic Fostering', 'Spare Room to Safe Haven', 'Before-and-after spare room transformation post.', f'{A}/Organic foresting/Static post/From Cluttered Spare Room to Safe Haven.png'),
    ('of-lang', 'social', 'Organic Fostering', 'A Home That Speaks Their Language', 'Cultural-belonging post with multilingual labels.', f'{A}/Organic foresting/Static post/organic foresting static post.png'),
    ('f-cosmetics', 'social', 'Lalina Cosmetics', 'Which One Is Your Favourite?', 'Animated beauty product post.', f'{D}/Cosmetics design.MOV'),
    ('f-pizza', 'social', 'Mr Pizza', 'Mouthwatering Pizzas', 'Animated food promo with a 50% offer.', f'{D}/MR Pizza.mp4'),
    ('f-menu', 'social', 'Restaurant', 'Grand Opening Menu', 'Animated food menu for a restaurant opening.', f'{D}/menu design.MOV'),
    ('f-zaitoon', 'social', 'Zaitoon', 'Nature\'s Finest Olives', 'Olive oil product post, still and animated.', [f'{D}/Zaitoon design.png', f'{D}/zaitoon mp4 design.mp4']),
    ('f-hasham', 'social', 'Dr Hasham Khan', 'Meet Your Urologist', 'Doctor profile post with qualifications and booking details.', f'{D}/Dr hasham design.jpeg'),
    ('f-surgical', 'social', 'Surgical Centre', 'Orthopaedic Surgery Department', 'Healthcare services post.', f'{D}/surgical center design.jpeg'),
    ('f-hiring', 'social', 'Surgical Centre', 'We Are Hiring', 'Recruitment post for a hospital.', f'{D}/surgical hiring design.jpeg'),
    ('f-gym', 'social', 'Podcast', 'Gym Secrets', 'Podcast cover and episode art.', f'{D}/GYM Se.png'),
    ('f-stayhome', 'social', 'Instagram', 'Stay Home, Stay Safe', 'Awareness post for Instagram.', f'{D}/instagram design.png'),
    ('f-thumb', 'social', 'YouTube', 'How to Smile Confidently', 'YouTube thumbnail.', f'{D}/Youtube thumbnail.png'),
    ('f-salon', 'social', 'Salon', 'Salon Reel', 'Short-form edit for a hair salon.', f'{D}/salon video.MP4'),
    ('f-arfan', 'social', 'Fiverr', 'Fiverr Gig Video', 'Gig intro video for a freelance designer.', f'{D}/arfan fiver gig.MP4'),
    # ---- branding & print
    ('of-logo', 'brand', 'Organic Fostering', 'Logo Exploration', 'Twelve logo directions for the Organic Fostering identity.', f'{A}/Logo/logo versions2.png'),
    ('w-wedding', 'brand', 'Wedding', 'Wedding Card', 'Animated wedding invitation.', f'{D}/wedding card design.MOV'),
    ('w-parisa', 'brand', 'Wedding', 'Mehndi Invitation', 'Animated invitation with peacock motifs.', f'{D}/wedding card of parisa.MOV'),
    ('w-areej', 'brand', 'Wedding', 'Wedding Invitation', 'Illustrated couple invitation card.', f'{D}/areej design.PNG'),
    ('w-engage', 'brand', 'Engagement', 'Engagement Ceremony', 'Floral engagement invitation.', f'{D}/engagement design.PNG'),
    ('ses-eid', 'brand', 'Software Engineering Society, MUST', 'Eid Mubarak', 'Society greeting post.', f'{D}/SES eid design.PNG'),
    ('ses-vote', 'brand', 'Software Engineering Society, MUST', 'President Election Day', 'Society election poster.', f'{D}/SES vote design.PNG'),
    ('ses-invite', 'brand', 'Software Engineering Society, MUST', 'SES Get Together', 'Event invitation.', f'{D}/Ses invitation design.PNG'),
]


def is_video(p):
    return p.lower().rsplit('.', 1)[-1] in ('mp4', 'mov')


def probe(p):
    c = cv2.VideoCapture(p)
    return int(c.get(3)), int(c.get(4)), round(c.get(7) / max(1, c.get(5)), 1)


def enc_video(src, dst, w, h):
    vertical = h > w
    vf = 'scale=540:-2' if vertical else ('scale=960:-2' if w > h * 1.1 else 'scale=720:-2')
    subprocess.run(['ffmpeg', '-y', '-v', 'error', '-i', src, '-vf', vf + ',fps=30', '-c:v', 'libx264', '-preset', 'slow', '-crf', '29',
                    '-maxrate', '1100k', '-bufsize', '2200k', '-pix_fmt', 'yuv420p', '-movflags', '+faststart',
                    '-c:a', 'aac', '-b:a', '64k', '-ac', '1', dst], check=True)


def poster(src, dst, frac=0.35, long_edge=900):
    c = cv2.VideoCapture(src)
    c.set(cv2.CAP_PROP_POS_FRAMES, int(c.get(7) * frac))
    ok, im = c.read()
    save_img(im, dst, long_edge)


def save_img(im, dst, long_edge):
    h, w = im.shape[:2]
    s = min(1.0, long_edge / max(h, w))
    if s < 1:
        im = cv2.resize(im, (int(w * s), int(h * s)), interpolation=cv2.INTER_AREA)
    cv2.imwrite(dst, im, [cv2.IMWRITE_JPEG_QUALITY, 84])


def stills(src, prefix, n=4, long_edge=1200):
    c = cv2.VideoCapture(src)
    N = c.get(7)
    out = []
    for j, fr in enumerate([0.12 + 0.76 * k / (n - 1) for k in range(n)]):
        c.set(cv2.CAP_PROP_POS_FRAMES, int(N * fr))
        ok, im = c.read()
        p = f'{prefix}_s{j}.jpg'
        save_img(im, p, long_edge)
        out.append(os.path.basename(p))
    return out


def job(item):
    wid, cat, client, title, note, srcs = item
    srcs = srcs if isinstance(srcs, list) else [srcs]
    rec = {'id': wid, 'cat': cat, 'client': client, 'title': title, 'note': note, 'media': []}
    for k, s in enumerate(srcs):
        base = f'{OUT}/{wid}' + (f'-{k}' if len(srcs) > 1 else '')
        if is_video(s):
            w, h, dur = probe(s)
            if not os.path.exists(base + '.mp4'):
                enc_video(s, base + '.mp4', w, h)
            poster(s, base + '.jpg')
            st = stills(s, f'{WS}/print/{os.path.basename(base)}')
            rec['media'].append({'type': 'video', 'src': f'media/{os.path.basename(base)}.mp4', 'poster': f'media/{os.path.basename(base)}.jpg',
                                 'w': w, 'h': h, 'dur': dur, 'stills': st})
        else:
            im = cv2.imread(s)
            h, w = im.shape[:2]
            save_img(im, base + '.jpg', 1400)
            save_img(im, f'{WS}/print/{os.path.basename(base)}.jpg', 1800)
            rec['media'].append({'type': 'image', 'src': f'media/{os.path.basename(base)}.jpg', 'w': w, 'h': h})
    print('done', wid, flush=True)
    return rec


if __name__ == '__main__':
    os.makedirs(OUT, exist_ok=True)
    os.makedirs(f'{WS}/print', exist_ok=True)
    for it in WORKS:
        for s in (it[5] if isinstance(it[5], list) else [it[5]]):
            if not os.path.exists(s):
                print('MISSING', s)
                sys.exit(1)
    with ThreadPoolExecutor(4) as ex:
        recs = list(ex.map(job, WORKS))
    json.dump(recs, open(f'{WS}/site/works.json', 'w'), indent=1, ensure_ascii=False)
    print('works', len(recs))
