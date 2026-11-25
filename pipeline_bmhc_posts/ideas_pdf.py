"""BMHC static post ideas (researched from current Instagram / Pinterest trends) -> PDF with a 4:5 mockup per idea.
Brand: BMHC Digital & Social Brand Guidelines v1.0 (Inter, ink/white + one pillar colour, four-bar strip, pillar tag top-left).
Output: reel/bmhc/static_post_ideas/BMHC_static_post_ideas.pdf
"""
import os, base64, subprocess

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
FON = f'{ROOT}/workspace_sol/fonts'
IMG = f'{ROOT}/workspace_bmhc/web/img'
OUT = f'{ROOT}/reel/bmhc/static_post_ideas'
os.makedirs(OUT, exist_ok=True)


def b64(p, mime):
    return f'data:{mime};base64,' + base64.b64encode(open(p, 'rb').read()).decode()


def ff(fam, file, w, style='normal'):
    return f"@font-face{{font-family:{fam};font-weight:{w};font-style:{style};src:url({b64(f'{FON}/{file}.ttf', 'font/ttf')})}}"


SNOW = b64(f'{IMG}/1-BMHC-web.jpg', 'image/jpeg')
AUTUMN = b64(f'{IMG}/bhmc-f.png', 'image/png')
TOWER = b64(f'{IMG}/Dut-kbsW4AIRs6T.jpg', 'image/jpeg')
LOGO_W = b64(f'{IMG}/bmhc-white-logo.png', 'image/png')
LOGO_C = b64(f'{IMG}/Website-1-2.png', 'image/png')
BARS = '<div class=bars><i style="background:#E60585"></i><i style="background:#2DC892"></i><i style="background:#FF4200"></i><i style="background:#69FF00"></i></div>'


def tag(label, col, ink=False):
    return f'<div class=tag style="background:{col};color:{"#0B0B0B" if ink else "#fff"}">{label}</div>'


# ------------------------------------------------------------------ mockups (360 x 450 = 1080 x 1350 at 1/3)
M = {}
M['bento'] = f'''<div class="card ink">{tag('COMMUNITY', '#FFFFFF', True)}
<div class=h1 style="margin-top:40px">EVERYTHING<br>UNDER ONE ROOF</div>
<div class=bento>
<div style="background:#2DC892;color:#0B0B0B;grid-column:span 2"><b>Daily prayers</b><span>& Jummah</span></div>
<div style="background:#69FF00;color:#0B0B0B"><b>Qur'an</b><span>classes</span></div>
<div style="background:#E60585;color:#fff;grid-row:span 2"><b>Imam</b><span>counselling</span></div>
<div style="background:#FF4200;color:#0B0B0B"><b>Youth</b><span>clubs</span></div>
<div style="background:#fff;color:#0B0B0B"><b>90.6 FM</b><span>Heritage Radio</span></div>
<div style="background:#E9E6DF;color:#0B0B0B"><b>Heritage</b><span>tours</span></div>
<div style="background:#1F1F1F;color:#fff;grid-column:span 2"><b>Nikah</b><span>ceremonies</span></div>
</div><div class=foot>College Road, Whalley Range</div>{BARS}</div>'''

M['notes'] = f'''<div class="card" style="background:#F6F5F1">
<div class=notesbar><span>‹ Notes</span><span>⋯</span></div>
<div class=notestitle>Things nobody tells you before visiting BMHC</div>
<div class=notesdate>25 November 2026 at 10:14</div>
<ul class=notes>
<li>You don't have to be Muslim to visit. Everyone is welcome.</li>
<li>There's a shoe rack outside the prayer hall.</li>
<li>Ask for a tour. Someone will say yes.</li>
<li>Heritage Radio is broadcast from here. 90.6 FM.</li>
<li>The chai is <span style="background:#E60585;color:#fff;padding:0 3px">dangerously</span> good.</li>
</ul>{BARS}</div>'''

M['receipt'] = f'''<div class="card" style="background:#E9E6DF"><div class=receipt>
<div class=rc>BRITISH MUSLIM<br>HERITAGE CENTRE</div><div class=rs>College Road · Whalley Range · M16 8BP</div>
<div class=rs>SAT 29 NOV · 10:02</div><div class=dash></div>
<div class=ri><span>1 × Qur'an class</span><span>✓</span></div>
<div class=ri><span>1 × Taekwondo session</span><span>✓</span></div>
<div class=ri><span>2 × Cups of chai</span><span>✓</span></div>
<div class=ri><span>1 × Study circle</span><span>✓</span></div>
<div class=ri><span>1 × New friend</span><span>✓</span></div>
<div class=dash></div><div class=ri style="font-weight:800"><span>TOTAL</span><span>A FULL DAY</span></div>
<div class=ri><span>Paid with</span><span>showing up</span></div><div class=dash></div>
<div class=rs>THANK YOU · SEE YOU NEXT WEEK</div><div class=barcode></div></div>{BARS}</div>'''

M['dump'] = f'''<div class="card" style="background:#F6F5F1">{tag('THIS WEEK', '#0B0B0B')}
<div class=pol style="left:28px;top:62px;transform:rotate(-6deg)"><div class=ph style="background-image:url({SNOW})"></div><div class=hand>first snow on the tower</div></div>
<div class=pol style="left:178px;top:92px;transform:rotate(5deg)"><div class=ph style="background-image:url({AUTUMN})"></div><div class=hand>autumn open day</div></div>
<div class=pol style="left:70px;top:238px;transform:rotate(3deg);width:150px"><div class=ph style="background-image:url({TOWER});height:100px;background-position:center 12%"></div><div class=hand>the tower, up close</div></div>
<div class=tape style="left:58px;top:56px;transform:rotate(-20deg)"></div><div class=tape style="left:230px;top:84px;transform:rotate(15deg)"></div>
<div class=sticker style="right:26px;top:268px">90.6<br>FM</div>
<div class=hand style="position:absolute;left:236px;top:340px;font-size:22px;color:#E60585;transform:rotate(-4deg)">see you<br>Friday ♡</div>
{BARS}</div>'''

M['ayah'] = f'''<div class="card" style="background:#fff">{tag('HEART', '#E60585')}
<div class=arabic>[ Qur'an 94:6 in Arabic — copied from a verified mushaf, Amiri Quran ]</div>
<div class=h1 style="color:#0B0B0B;margin-top:22px;font-size:40px">WITH<br>HARDSHIP<br>COMES <span style="color:#E60585">EASE.</span></div>
<div class=src>Qur'an 94:6 · approved translation</div>
<div class=action><b>ONE ACTION</b><br>Write down one hard thing from last year that eased.</div>
{BARS}</div>'''

M['seasons'] = f'''<div class="card ink">{tag('HERITAGE', '#FFFFFF', True)}
<div class=quad>
<div style="background-image:url({SNOW})"><em>WINTER</em></div>
<div class=todo><em>SPRING</em><small>shoot in April</small></div>
<div class=todo><em>SUMMER</em><small>shoot in July</small></div>
<div style="background-image:url({AUTUMN})"><em>AUTUMN</em></div></div>
<div class=h1 style="font-size:30px;margin-top:14px">SAME TOWER.<br>EVERY SEASON.</div>{BARS}</div>'''

M['chat'] = f'''<div class="card" style="background:#F6F5F1">{tag('HERITAGE RADIO', '#FF4200', True)}
<div class=chathd>Mum ❤</div>
<div class="bub l">put 90.6 on</div>
<div class="bub l">the health podcast is on in 5 mins</div>
<div class="bub r">it's already on 😌</div>
<div class="bub l">that's my boy</div>
<div class=tune><b>90.6 FM</b> · DAB+ Manchester<br>Heritage Radio app · Alexa · Radio Garden</div>{BARS}</div>'''

M['thisorthat'] = f'''<div class="card ink">{tag('PRODUCTIVITY', '#FF4200', True)}
<div class=h1 style="margin-top:56px;font-size:30px">HOW DO YOU<br>LEARN BEST?</div>
<div class=tot><div><span class=emo>📖</span><b>Study circle</b><small>Tuesdays at the centre</small></div>
<div class=or>OR</div><div><span class=emo>🎧</span><b>Podcast on the bus</b><small>Heritage Radio app</small></div></div>
<div class=foot>Comment 1 or 2 — both count.</div>{BARS}</div>'''

M['cover'] = f'''<div class="card" style="background:#0B0B0B url({AUTUMN}) center/cover">
<div class=coverfade></div><div class=mast>HERITAGE</div><div class=issue>ISSUE 12 · WHALLEY RANGE</div>
<div class=cl style="top:150px"><b>130K+</b> visitors a year</div>
<div class=cl style="top:196px"><b>14</b> awards</div>
<div class=cl style="top:242px"><b>12+</b> years of Muslim heritage</div>
<div class=cl2>INSIDE: Heritage Radio 90.6 FM · Youth clubs · Heritage tours</div>
<img class=clogo src="{LOGO_W}">{BARS}</div>'''

M['tearoff'] = f'''<div class="card" style="background:#E9E6DF">{tag('HEART', '#E60585')}
<div class=poster><div class=h1 style="color:#0B0B0B;font-size:44px;margin:24px 0 8px">NEED TO<br>TALK?</div>
<div class=pbody>Confidential Imam counselling at the British Muslim Heritage Centre. You don't have to carry it alone.</div>
<div class=tabs>{''.join('<div><span>Imam counselling · 0161 881 8062</span></div>' for _ in range(7))}</div></div>{BARS}</div>'''

IDEAS = [
    ('bento', 'Everything under one roof', 'Bento grid', 'Community · ink and white + four bars', 'Single post (or a 7-slide carousel, one tile per slide)',
     'Bento grids are the go-to layout for reference posts people save: one glance shows everything. Carousels and saveable reference posts drive saves, Instagram\'s strongest ranking signal.',
     'A tidy grid of rounded tiles on ink, each tile one BMHC service in a brand colour (prayer, Qur\'an classes, youth clubs, counselling, Heritage Radio, tours, Nikah). Headline in Inter ExtraBold caps.',
     'Prayer, Qur\'an classes, youth clubs, counselling, Heritage Radio, heritage tours and Nikah ceremonies — all at one address in Whalley Range. Save this for the next time someone asks what BMHC does. 📍 College Road, M16 8BP',
     'Tile colours follow the approved pairings: ink text on teal, lime and orange; white on magenta. Keep body copy off the coloured tiles.'),
    ('notes', 'Things nobody tells you before visiting', 'Notes-app screenshot', 'Welcome / outreach · magenta accent', 'Single post, or 2-3 slides of notes',
     'Lo-fi, "from a friend, not a marketing department" posts are winning over polished brand graphics in 2026. A notes-app list feels personal and gets shared to Stories.',
     'An iPhone Notes screen: grey title bar, a casual title, five short honest lines, one word highlighted in magenta. Four bars at the foot.',
     'Thinking of visiting but not sure what to expect? Here\'s what we\'d tell a friend. Everyone is welcome at the centre — open days, tours and Friday visits. Ask us anything in the comments.',
     'Every line must be true for BMHC — confirm the tour and visiting details with the team before posting.'),
    ('receipt', 'Receipt: one Saturday at the centre', 'Receipt / ticket', 'Community · ink on stone', 'Single post',
     'Receipt posts are a playful, tactile format that people screenshot and share. They fit the 2026 "imperfect by design" move away from glossy polish.',
     'A thermal-paper receipt on stone: centre name, address, date, five line items (Qur\'an class, taekwondo, chai, study circle, a new friend), "Total: a full day", "Paid with: showing up", barcode.',
     'What a Saturday at BMHC actually costs: a bit of time. What you get back: a full day. Classes, clubs and study circles every week in Whalley Range — link in bio for times.',
     'Match line items to real Saturday activities and times on the current timetable.'),
    ('dump', 'This week at BMHC', 'Photo dump / scrapbook', 'Community · ink tag, magenta handwriting', 'Carousel: scrapbook cover + 5-8 photos',
     'Photo dumps are one of Metricool\'s hot 2026 formats; Pinterest\'s 2026 predictions lean tactile and maximal. Taped polaroids and handwriting feel human, not AI-polished.',
     'Taped polaroids of the week (the tower in snow, the autumn open day, the tower up close), handwritten captions, a 90.6 FM sticker, a magenta "see you Friday ♡". Following slides: the full photos.',
     'A week at the centre in a few snaps 📸 Snow on the tower, open-day leaves, the tower up close. What should we photograph next week?',
     'Safeguarding: no identifiable under-18s without recorded parental consent. Use backs of heads, hands, objects and the building.'),
    ('ayah', 'With hardship comes ease', 'Bold-type ayah card', 'Heart Work · magenta', 'Single post (4:5) — the brand\'s ayah card template',
     'Big, simple, breathable type is one of the clearest 2026 shifts away from clutter, and quote cards are the most-saved static format.',
     'White card, HEART tag top-left, Arabic first (from a verified mushaf), then the hook in huge Inter ExtraBold with "EASE." in magenta, the reference, and one small action.',
     '"Indeed, with hardship comes ease." — Qur\'an 94:6. If this year has been heavy, you are not alone. Save this for the day you need it. Our Imam counselling service is here if you want to talk.',
     'Order: Arabic, translation, reference, one action. Copy the Arabic and the approved translation from a verified source; a second person checks before posting. No music if it is turned into a video.'),
    ('seasons', 'Same tower. Every season.', 'Seasonal 2×2 grid (heritage)', 'Heritage · ink and white', 'Single post now, completed over the year',
     'Heritage and architecture content taps the retro, Neo Deco mood in Pinterest Predicts 2026, and a four-season series gives followers a reason to come back.',
     'A 2×2 grid of the same view of the tower: winter (snow photo) and autumn (open-day photo) now, with spring and summer to shoot from the same spot.',
     'Same tower, every season. Our home in Whalley Range has stood through a lot of Manchester weather. Which season suits it best? ❄️🌸☀️🍂',
     'Shoot spring and summer from the exact same position and lens to keep the grid clean.'),
    ('chat', 'Mum: put 90.6 on', 'Text-message screenshot', 'Heritage Radio · orange accent', 'Single post',
     'Chat-screenshot humour is relatable, low-production and very shareable, which is the authenticity the 2026 trend reports describe.',
     'A family chat: "put 90.6 on" / "the health podcast is on in 5 mins" / "it\'s already on 😌". Under it, every way to listen.',
     'Every family has this chat. 😌 Heritage Radio — 90.6 FM, DAB+ Manchester, the Heritage Radio app, Alexa and Radio Garden. Faith, wellbeing and local stories, broadcast from the centre.',
     'Orange carries ink text (or white only at large sizes). Keep the joke warm and family-friendly.'),
    ('thisorthat', 'How do you learn best?', 'This or That', 'Productivity the Islamic Way · orange', 'Single post + a Story poll',
     'Two-option posts invite a one-tap comment, and comments plus shares feed reach. They work for short attention spans.',
     'Ink card, two big options side by side with an emoji each: "Study circle" or "Podcast on the bus", with a big "OR" between. "Comment 1 or 2".',
     'Study circle or podcast on the bus — how do you learn best? Comment 1 or 2. Both count: our study circles meet at the centre, and Heritage Radio podcasts are on every app.',
     'Keep both options positive. Use it to promote two real BMHC offers.'),
    ('cover', 'HERITAGE — the magazine cover', 'Editorial magazine cover', 'Heritage · ink, white type', 'Single post (pairs with an "inside the issue" carousel)',
     'Editorial and magazine-cover layouts are a polished counterpoint that still feels collectable; Pinterest 2026 leans into glamour and Neo Deco.',
     'The autumn building photo full bleed with a dark fade, a big "HERITAGE" masthead, cover lines with the centre\'s own figures (130K+ visitors a year, 14 awards, 12+ years), and the reversed logo.',
     'Our cover story: a centre in Whalley Range that 130,000+ people visit every year. 14 awards, 12+ years of sharing Muslim heritage — and Heritage Radio on 90.6 FM. Read the full story at bmhc.org.uk.',
     'Figures as stated on bmhc.org.uk — confirm they are current. Use the reversed logo over the dark overlay only.'),
    ('tearoff', 'Need to talk?', 'Tear-off poster', 'Heart Work · magenta', 'Single post',
     'Real-world ephemera (posters, tape, paper) is part of the tactile, human look that stands out in 2026. Tear-off tabs say "take one" without words.',
     'A paper poster on stone: "NEED TO TALK?" in big type, one gentle line about confidential Imam counselling, a row of tear-off tabs with the centre\'s phone number.',
     'You don\'t have to carry it alone. Confidential Imam counselling is available at the British Muslim Heritage Centre. Call 0161 881 8062 or message us — we\'ll take it from there.',
     'Calm, never fear-based. Confirm how bookings work and add signposting to urgent help (NHS 111, Samaritans 116 123) in the caption if BMHC agrees.'),
]

TRENDS = [
    ('Human beats polished', 'With AI making polish common, posts that feel made by a person — imperfect, lo-fi, friendly — are the ones that stand out.', 'Manypixels; PostNitro'),
    ('Simple, breathable layouts', 'A move away from clutter and heavy effects towards clean compositions with big type.', 'Mockupline 2026 design trends'),
    ('Saves are the signal', 'Carousels and reference-style posts earn far more saves than single images; saves and shares drive reach.', 'Metricool 2026 study; Sprout Social'),
    ('Photo dumps & scrapbooks', 'Casual carousels of snapshots, taped and annotated, read as genuine.', 'Metricool Instagram trends 2026'),
    ('Tactile & maximal', 'Pinterest Predicts 2026: maximalism, Neo Deco glamour, tactile "Gimme Gummy" textures.', 'Pinterest Newsroom; Graphic Design Junction'),
    ('4:5 portrait', 'Use 1080 × 1350 px for the most feed space — the first slide sets the carousel\'s shape.', 'Metricool'),
]
SOURCES = [
    ('Manypixels — The most important social media trends for 2026', 'https://www.manypixels.co/blog/social-media-design/trends-2021'),
    ('Mockupline — 2026 Instagram design trends', 'https://mockupline.com/2026-instagram-design-trends/'),
    ('Metricool — 10 Instagram trends backed by real data in 2026', 'https://metricool.com/instagram-trends/'),
    ('Metricool — Best practices for Instagram carousel posts', 'https://metricool.com/instagram-carousels/'),
    ('Sprout Social — Instagram trends', 'https://sproutsocial.com/insights/instagram-trends/'),
    ('PostNitro — Instagram trends', 'https://postnitro.ai/blog/post/instagram-trends'),
    ('Pinterest Newsroom — Pinterest Predicts 2026', 'https://newsroom.pinterest.com/en-gb/news/pinterest-predicts-nonconformity-self-preservation-and-escapism-drive-21-trends-for-2026/'),
    ('Graphic Design Junction — Pinterest trends in graphic design', 'https://graphicdesignjunction.com/2026/09/pinterest-trends-in-graphic-design/'),
    ('British Muslim Heritage Centre — bmhc.org.uk', 'https://bmhc.org.uk/'),
]

CSS = f'''
{ff('Inter', 'Inter-400', 400)}{ff('Inter', 'Inter-500', 500)}{ff('Inter', 'Inter-700', 700)}{ff('Inter', 'Inter-800', 800)}{ff('Inter', 'Inter-900', 900)}
{ff('Hand', 'Caveat', 500)}
@page{{size:A4;margin:0}}
*{{box-sizing:border-box}}
body{{margin:0;font-family:Inter;color:#0B0B0B;font-size:10pt}}
.page{{width:210mm;height:297mm;padding:16mm 15mm;position:relative;page-break-after:always;overflow:hidden}}
.page:last-child{{page-break-after:auto}}
.cover{{background:#0B0B0B;color:#fff;display:flex;flex-direction:column;justify-content:space-between}}
.cover h1{{font-weight:900;font-size:44pt;letter-spacing:.01em;line-height:1.02;margin:0}}
.cover .k{{color:#E60585;font-weight:800;letter-spacing:.12em;font-size:10pt}}
.cover p{{font-size:13pt;color:#cfcfcf;max-width:150mm;line-height:1.5}}
.bigbars{{display:flex;height:6mm}} .bigbars i{{flex:1}}
h2{{font-weight:900;font-size:22pt;margin:0 0 3mm}}
.eyebrow{{font-weight:800;color:#E60585;letter-spacing:.12em;font-size:8.5pt;margin-bottom:2mm}}
.lead{{color:#5C5C5C;font-size:10.5pt;line-height:1.5;margin-bottom:6mm}}
.tgrid{{display:grid;grid-template-columns:1fr 1fr;gap:4mm}}
.tgrid div{{background:#F6F5F1;border-radius:3mm;padding:4mm 5mm;border-top:1.5mm solid #0B0B0B}}
.tgrid b{{display:block;font-size:11.5pt;margin-bottom:1.5mm}} .tgrid span{{color:#5C5C5C;line-height:1.45;display:block}}
.tgrid em{{display:block;font-style:normal;color:#E60585;font-weight:700;font-size:8pt;margin-top:2mm}}
.rules{{margin-top:6mm;background:#0B0B0B;color:#fff;border-radius:3mm;padding:5mm 6mm;line-height:1.55}}
.rules b{{color:#69FF00}}
.idea{{display:grid;grid-template-columns:96mm 1fr;gap:8mm;align-items:start}}
.num{{font-weight:900;font-size:44pt;color:#E9E6DF;line-height:.9}}
.title{{font-weight:900;font-size:19pt;line-height:1.1;margin:1mm 0 3mm}}
.chips span{{display:inline-block;background:#F6F5F1;border:1px solid #E9E6DF;border-radius:10mm;padding:1mm 3mm;margin:0 1.5mm 1.5mm 0;font-weight:600;font-size:8.5pt}}
.chips span.t{{background:#0B0B0B;color:#fff;border-color:#0B0B0B}}
.f{{margin-top:3.5mm}} .f b{{display:block;font-weight:800;font-size:8pt;letter-spacing:.1em;color:#E60585;margin-bottom:1mm}}
.f p{{margin:0;line-height:1.5}}
.capbox{{background:#F6F5F1;border-left:1.2mm solid #0B0B0B;padding:3mm 4mm;border-radius:0 2mm 2mm 0;line-height:1.5}}
.note{{color:#5C5C5C;font-size:9pt;line-height:1.45}}
.footer{{position:absolute;left:15mm;right:15mm;bottom:9mm;display:flex;justify-content:space-between;color:#5C5C5C;font-size:8pt}}
/* --- mockup card: 360 x 450 css px --- */
.frame{{width:96mm}}
.card{{width:360px;height:450px;position:relative;overflow:hidden;border-radius:6px;box-shadow:0 6px 20px rgba(0,0,0,.18);font-family:Inter;color:#0B0B0B}}
.card.ink{{background:#0B0B0B;color:#fff}}
.mlabel{{font-size:8pt;color:#5C5C5C;margin-top:3mm}}
.bars{{position:absolute;left:0;right:0;bottom:0;height:8px;display:flex}} .bars i{{flex:1}}
.tag{{position:absolute;left:18px;top:18px;font-weight:800;font-size:9px;letter-spacing:.12em;padding:4px 8px;border-radius:3px}}
.h1{{font-weight:800;font-size:34px;line-height:1.02;letter-spacing:.02em;margin:0 18px}}
.foot{{position:absolute;left:18px;bottom:18px;font-size:10px;color:#aaa;font-weight:500}}
.bento{{display:grid;grid-template-columns:repeat(3,1fr);grid-auto-rows:62px;gap:6px;margin:14px 18px}}
.bento div{{border-radius:10px;padding:8px 9px;display:flex;flex-direction:column;justify-content:flex-end}}
.bento b{{font-weight:800;font-size:13px;line-height:1.05}} .bento span{{font-size:9.5px;font-weight:500;opacity:.85}}
.notesbar{{display:flex;justify-content:space-between;color:#E0A800;font-weight:600;font-size:13px;padding:16px 18px 6px}}
.notestitle{{font-weight:800;font-size:23px;line-height:1.12;margin:8px 18px 4px}}
.notesdate{{color:#8a8a8a;font-size:10px;margin:0 18px 10px;text-align:center}}
ul.notes{{margin:0 18px;padding-left:16px;font-size:13.5px;line-height:1.45}} ul.notes li{{margin-bottom:7px}}
.receipt{{position:absolute;left:58px;right:58px;top:24px;bottom:30px;background:#fff;padding:18px 16px;font-family:"Courier New",monospace;font-size:11px;
  transform:rotate(-2deg);box-shadow:0 6px 14px rgba(0,0,0,.18);clip-path:polygon(0 0,100% 0,100% 97%,95% 100%,90% 97%,85% 100%,80% 97%,75% 100%,70% 97%,65% 100%,60% 97%,55% 100%,50% 97%,45% 100%,40% 97%,35% 100%,30% 97%,25% 100%,20% 97%,15% 100%,10% 97%,5% 100%,0 97%)}}
.rc{{font-family:Inter;font-weight:900;text-align:center;font-size:14px;line-height:1.1}} .rs{{text-align:center;font-size:9.5px;margin-top:4px;color:#444}}
.dash{{border-top:1.5px dashed #999;margin:9px 0}} .ri{{display:flex;justify-content:space-between;margin:4px 0}}
.barcode{{height:30px;margin-top:10px;background:repeating-linear-gradient(90deg,#111 0 2px,transparent 2px 4px,#111 4px 5px,transparent 5px 8px)}}
.pol{{position:absolute;width:160px;background:#fff;padding:8px 8px 4px;box-shadow:0 5px 12px rgba(0,0,0,.2)}}
.ph{{height:110px;background-size:cover;background-position:center;filter:saturate(.9)}}
.hand{{font-family:Hand;font-size:17px;text-align:center;color:#1F1F1F;padding-top:2px}}
.tape{{position:absolute;width:60px;height:18px;background:rgba(233,230,223,.85);box-shadow:0 1px 2px rgba(0,0,0,.1)}}
.sticker{{position:absolute;width:64px;height:64px;border-radius:50%;background:#FF4200;color:#0B0B0B;font-weight:900;font-size:15px;line-height:1;display:flex;align-items:center;justify-content:center;text-align:center;transform:rotate(12deg)}}
.arabic{{margin:64px 18px 0;padding:14px;border:1.5px dashed #E9E6DF;border-radius:6px;color:#5C5C5C;font-size:11px;text-align:center;line-height:1.4}}
.src{{margin:10px 18px 0;font-weight:500;color:#5C5C5C;font-size:11px}}
.action{{position:absolute;left:18px;right:18px;bottom:26px;background:#F6F5F1;border-left:4px solid #E60585;padding:8px 10px;font-size:11px;line-height:1.4}}
.action b{{font-size:9px;letter-spacing:.12em;color:#E60585}}
.quad{{display:grid;grid-template-columns:1fr 1fr;gap:4px;margin:52px 18px 0;height:270px}}
.quad div{{background-size:cover;background-position:center;position:relative;border-radius:4px}}
.quad em{{position:absolute;left:8px;bottom:6px;font-style:normal;font-weight:800;font-size:10px;letter-spacing:.12em;color:#fff;text-shadow:0 1px 3px rgba(0,0,0,.6)}}
.quad .todo{{background:#1F1F1F;border:1.5px dashed #5C5C5C;display:flex;align-items:center;justify-content:center}} .quad .todo small{{color:#999;font-size:10px}}
.chathd{{margin:56px 0 10px;text-align:center;font-weight:700;font-size:13px}}
.bub{{max-width:68%;padding:8px 12px;border-radius:16px;font-size:14px;margin:6px 18px;line-height:1.3}}
.bub.l{{background:#E9E6DF}} .bub.r{{background:#0B0B0B;color:#fff;margin-left:auto}}
.tune{{position:absolute;left:18px;right:18px;bottom:26px;background:#FF4200;color:#0B0B0B;border-radius:8px;padding:10px 12px;font-size:11px;line-height:1.45}}
.tune b{{font-size:16px;font-weight:900}}
.tot{{display:grid;grid-template-columns:1fr auto 1fr;align-items:center;gap:8px;margin:28px 18px}}
.tot>div{{background:#1F1F1F;border-radius:12px;padding:16px 10px;text-align:center;height:170px;display:flex;flex-direction:column;justify-content:center}}
.tot .emo{{font-size:34px}} .tot b{{font-size:15px;font-weight:800;margin-top:8px}} .tot small{{color:#aaa;font-size:9.5px;margin-top:4px}}
.tot .or{{background:#FF4200!important;color:#0B0B0B;font-weight:900;font-size:13px;height:auto!important;border-radius:50%!important;width:42px;height:42px!important;padding:0!important}}
.coverfade{{position:absolute;inset:0;background:linear-gradient(180deg,rgba(11,11,11,.55) 0%,rgba(11,11,11,.15) 45%,rgba(11,11,11,.85) 100%)}}
.mast{{position:absolute;top:22px;left:0;right:0;text-align:center;font-weight:900;font-size:62px;letter-spacing:.04em;color:#fff}}
.issue{{position:absolute;top:96px;left:0;right:0;text-align:center;font-size:9px;letter-spacing:.2em;color:#fff;font-weight:600}}
.cl{{position:absolute;left:18px;color:#fff;font-size:12px;font-weight:500}} .cl b{{font-size:26px;font-weight:900;color:#E60585;margin-right:4px}}
.cl2{{position:absolute;left:18px;right:18px;bottom:76px;color:#fff;font-size:10.5px;font-weight:600;line-height:1.4}}
.clogo{{position:absolute;left:18px;bottom:20px;width:130px}}
.poster{{position:absolute;left:36px;right:36px;top:46px;bottom:28px;background:#fff;box-shadow:0 6px 14px rgba(0,0,0,.15);transform:rotate(1.2deg)}}
.poster .h1{{margin-left:16px}} .pbody{{margin:0 16px;font-size:12px;line-height:1.45;color:#1F1F1F}}
.tabs{{position:absolute;left:0;right:0;bottom:0;height:120px;display:flex;border-top:1.5px dashed #999}}
.tabs div{{flex:1;border-right:1.5px dashed #999;display:flex;align-items:center;justify-content:center}}
.tabs div:nth-child(3){{transform:translateY(8px) rotate(4deg);background:#fff;box-shadow:0 2px 4px rgba(0,0,0,.15)}}
.tabs div:nth-child(6){{visibility:hidden}}
.tabs span{{writing-mode:vertical-rl;transform:rotate(180deg);font-size:8.5px;font-weight:700;color:#0B0B0B}}
.plan{{width:100%;border-collapse:collapse;margin-top:4mm}} .plan td,.plan th{{border-bottom:1px solid #E9E6DF;padding:2.6mm 2mm;text-align:left;vertical-align:top;line-height:1.4}}
.plan th{{font-size:8pt;letter-spacing:.1em;color:#5C5C5C}}
.check li{{margin-bottom:1.8mm;line-height:1.45}}
.srcs li{{margin-bottom:1.4mm;font-size:9pt;line-height:1.4}} .srcs a{{color:#0B0B0B}}
'''


def idea_page(i, key, title, fmt_name, pillar, fmt, why, layout, caption, check):
    return f'''<div class=page><div class=idea>
<div class=frame>{M[key]}<div class=mlabel>Mockup · 1080 × 1350 px (4:5) — shown at one third size</div></div>
<div><div class=num>{i:02d}</div><div class=title>{title}</div>
<div class=chips><span class=t>{fmt_name}</span><span>{pillar}</span><span>{fmt}</span></div>
<div class=f><b>WHY IT'S TRENDING</b><p>{why}</p></div>
<div class=f><b>LAYOUT</b><p>{layout}</p></div>
<div class=f><b>CAPTION</b><div class=capbox>{caption}</div></div>
<div class=f><b>BRAND & SAFEGUARDING CHECK</b><p class=note>{check}</p></div></div></div>
<div class=footer><span>BMHC · Static post ideas · November 2026</span><span>{i + 2}</span></div></div>'''


pages = [f'''<div class="page cover"><div><img src="{LOGO_W}" style="width:60mm"><div style="height:14mm"></div>
<div class=k>STATIC POST IDEAS · INSTAGRAM & FACEBOOK · 4:5</div><div style="height:4mm"></div>
<h1>10 posts for the British Muslim Heritage Centre</h1><div style="height:6mm"></div>
<p>Built from what is trending on Instagram and Pinterest right now, adapted to BMHC's brand guidelines: Inter type, ink and white with one pillar colour, the four-bar strip, and the content rules for Qur'an, imagery and safeguarding. Each idea comes with a mockup, layout notes and a ready caption.</p></div>
<div><div class=bigbars><i style="background:#E60585"></i><i style="background:#2DC892"></i><i style="background:#FF4200"></i><i style="background:#69FF00"></i></div>
<p style="font-size:9pt;margin-top:4mm">bmhc.org.uk · College Road, Whalley Range, Manchester M16 8BP</p></div></div>''']

tg = ''.join(f'<div><b>{a}</b><span>{b}</span><em>{c}</em></div>' for a, b, c in TRENDS)
pages.append(f'''<div class=page><div class=eyebrow>RESEARCH · NOVEMBER 2026</div><h2>What's working right now</h2>
<div class=lead>A scan of current Instagram and Pinterest trend reports. The common thread: as AI makes polish cheap, posts that feel human, simple and worth saving are the ones that travel.</div>
<div class=tgrid>{tg}</div>
<div class=rules><b>How every idea follows the BMHC guidelines</b><br>
Inter ExtraBold caps headlines, Inter Regular body · ink 45%, white/mist 35%, one pillar colour, four bars · pillar tag top-left ·
approved pairings only (ink text on teal, lime and orange; white on magenta) · reversed logo on ink, colour logo on white ·
Qur'an cards: Arabic first from a verified mushaf, approved translation, surah:ayah, checked by a second person ·
no identifiable under-18s without recorded parental consent · welcoming, grounded, clear, never clickbait.</div>
<div class=footer><span>BMHC · Static post ideas · November 2026</span><span>2</span></div></div>''')

for i, idea in enumerate(IDEAS, 1):
    pages.append(idea_page(i, *idea))

plan_rows = [('Week 1', 'Everything under one roof', 'Tue', 'Saveable intro to the centre — pin it to the top of the grid.'),
             ('Week 1', 'With hardship comes ease', 'Sat', 'Heart Work card, alongside the weekly animation.'),
             ('Week 2', 'Mum: put 90.6 on', 'Wed', 'Heritage Radio push; share to Stories with a link sticker.'),
             ('Week 2', 'This week at BMHC', 'Sun', 'Photo dump of the week; ask what to photograph next.'),
             ('Week 3', 'Receipt: one Saturday', 'Fri', 'Before the weekend; link to the timetable.'),
             ('Week 3', 'How do you learn best?', 'Mon', 'This or That + a Story poll with the same question.'),
             ('Week 4', 'Things nobody tells you', 'Thu', 'Ahead of an open day or school visit.'),
             ('Week 4', 'Need to talk?', 'Sat', 'Pair with the Heart Work content that week.'),
             ('Month 2', 'HERITAGE magazine cover', '—', 'With an "inside the issue" carousel.'),
             ('Ongoing', 'Same tower. Every season.', '—', 'Shoot spring and summer; repost as each season lands.')]
rows = ''.join(f'<tr><td><b>{a}</b></td><td>{b}</td><td>{c}</td><td class=note>{d}</td></tr>' for a, b, c, d in plan_rows)
srcs = ''.join(f'<li>{a} — <a href="{u}">{u}</a></li>' for a, u in SOURCES)
pages.append(f'''<div class=page><div class=eyebrow>PLAN</div><h2>A month of static posts</h2>
<div class=lead>Slots sit around the weekly video rhythm in the brand guide (Mon reminder, Tue Qur'an, Wed story, Thu dua, Fri Jummah, Sat animation, Sun Q&A).</div>
<table class=plan><tr><th>WHEN</th><th>POST</th><th>DAY</th><th>NOTE</th></tr>{rows}</table>
<div class=eyebrow style="margin-top:8mm">PRE-POST CHECK</div>
<ul class=check><li>One idea per post, one pillar colour, pillar tag top-left, four bars present.</li>
<li>Text readable on a phone at arm's length; nothing important under the 4:5 crop or profile-grid crop.</li>
<li>Facts and figures match bmhc.org.uk today (visitors, awards, years, times, phone numbers).</li>
<li>Any Qur'an or hadith text verified by a second person; reference included.</li>
<li>No identifiable under-18s without recorded consent; alt text written for every image.</li></ul>
<div class=eyebrow style="margin-top:8mm">SOURCES</div><ul class=srcs>{srcs}</ul>
<div class=footer><span>BMHC · Static post ideas · November 2026</span><span>{len(IDEAS) + 3}</span></div></div>''')

html = f'<!doctype html><html><head><meta charset=utf-8><style>{CSS}</style></head><body>{"".join(pages)}</body></html>'
open(f'{OUT}/ideas.html', 'w').write(html)
js = f"""const {{ chromium }} = require('playwright');
(async () => {{ const b = await chromium.launch(); const p = await b.newPage();
await p.goto('file://{OUT}/ideas.html'); await p.waitForTimeout(800);
await p.pdf({{ path: '{OUT}/BMHC_static_post_ideas.pdf', format: 'A4', printBackground: true, margin: {{top:'0',bottom:'0',left:'0',right:'0'}} }});
await b.close(); }})();"""
subprocess.run(['node', '-e', js], check=True)
os.remove(f'{OUT}/ideas.html')
print('pdf written')
