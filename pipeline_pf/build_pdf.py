"""PDF portfolio (16:9 pages, contact-sheet design) -> reel/portfolio/Laiba_Jamal_Portfolio.pdf

Usage: python3 build_pdf.py
"""
import os, json, html, subprocess, base64

HERE = os.path.dirname(os.path.abspath(__file__))
WS = os.path.abspath(os.path.join(HERE, '..', 'workspace_pf'))
PR = f'{WS}/print'
OUTDIR = os.path.abspath(os.path.join(HERE, '..', 'reel', 'portfolio'))
DRIVE = 'https://drive.google.com/drive/folders/1JM57n2UWl5T_WYAiXzFPpg7fWQgQY50r'
works = json.load(open(f'{WS}/site/works.json'))
W = {w['id']: w for w in works}
for i, w in enumerate(works):
    w['fno'] = 'F%02d' % (i + 1)
LABEL = {'ai': 'AI video', 'motion': 'Motion reel', 'social': 'Social design', 'brand': 'Branding'}
E = html.escape


def img(path):
    return 'file://' + path


BEST = {'mp-launch': 2, 'pd-reel': 2}


def still(wid, k=0):
    k = BEST.get(wid, k)
    w = W[wid]
    m = w['media'][0]
    if m['type'] == 'video':
        return img(f"{PR}/{m['stills'][k]}")
    base = os.path.basename(m['src'])
    return img(f'{PR}/{base}')


def media_img(wid, j):
    w = W[wid]
    m = w['media'][j]
    if m['type'] == 'video':
        return img(f"{PR}/{m['stills'][1]}")
    return img(f"{PR}/{os.path.basename(m['src'])}")


def cap(wid, extra=''):
    w = W[wid]
    m = w['media'][0]
    dur = f" · {round(m['dur'])}s" if m['type'] == 'video' else ''
    return (f'<div class="cap"><span class="t">{E(w["title"])}</span>'
            f'<span class="c">{E(w["client"])} · {LABEL[w["cat"]]}{dur}{extra}</span></div>')


def frame(wid, k=0, cls='', ring=False):
    w = W[wid]
    m = w['media'][0]
    play = '<span class="play">▶</span>' if m['type'] == 'video' else ''
    r = RING if ring else ''
    return f'<figure class="fr {cls}"><div class="ph"><img src="{still(wid, k)}">{play}{r}</div>{cap(wid)}</figure>'


RING_OLD = ('<svg class="ring" viewBox="0 0 100 100" preserveAspectRatio="none"><path d="M8,52 C4,22 40,4 62,6 C88,9 98,30 95,55 '
        'C92,82 66,97 42,95 C18,93 6,78 10,50"/></svg>')


RING = ''


def page(body, cls='', num=None, section=''):
    foot = (f'<div class="pfoot"><span>Laiba Jamal · Portfolio 2026</span><span>{E(section)}</span>'
            f'<span>{num:02d}</span></div>' if num else '')
    return f'<section class="page {cls}">{body}{foot}</section>'


def strip(ids, k=1):
    cells = ''.join(f'<div class="cell"><img src="{still(i, k)}"><span>{E(W[i]["client"].upper())}</span></div>' for i in ids)
    return f'<div class="film"><div class="cells">{cells}</div></div>'


def video_sheet(wid):
    """One video as a 4-frame contact strip."""
    w = W[wid]
    m = w['media'][0]
    cells = ''.join(f'<img src="{img(PR + "/" + s)}">' for s in m['stills'])
    return f'<div class="vsheet {"wide" if m["w"] > m["h"] else ""}"><div class="vframes">{cells}</div>{cap(wid)}</div>'


pages = []
n = 0


def add(body, cls='', section=''):
    global n
    n += 1
    pages.append(page(body, cls, n if n > 1 else None, section))


# 1 cover
add(f"""
<div class="cover">
  <div class="ctop"><span class="wm">laibajamal<span>.</span></span><span class="eyebrow">Portfolio 2026</span></div>
  <div class="chero">
    <span class="eyebrow dot">Design. AI. Photography.</span>
    <h1>Your brand. Their next<span class="pink">favourite scroll.</span></h1>
    <p>Laiba Jamal · Graphic Designer · AI Creative Specialist · Photographer</p>
  </div>
  <svg class="burst" viewBox="0 0 100 100"><path fill="currentColor" d="M50 0 57 33 82 9 66 40 100 38 69 54 96 76 62 66 70 100 50 72 30 100 38 66 4 76 31 54 0 38 34 40 18 9 43 33Z"/></svg>
  <div class="ccards">
    <div class="pc p1"><img src="{still('b-padel', 1)}"><span class="tag">✶ Good enough to double tap.</span></div>
    <div class="pc p2"><img src="{media_img('of-carousel', 0)}"><span class="tag dark">The little moments</span></div>
    <div class="pc p3"><img src="file://{WS}/site/media/portrait.jpg"><span class="tag dark">Laiba Jamal</span></div>
    <div class="pc p4"><img src="{still('hm-find')}"><span class="tag">✶ Brand-new energy.</span></div>
    <span class="hey">Hey, I'm Laiba!</span>
    <div class="badge">Less scrolling.<b>More stopping.</b></div>
  </div>
</div>""", 'cover-page')

# 2 about
add(f'''
<div class="two">
  <div>
    <figure class="print"><img src="file://{WS}/site/media/portrait.jpg"><figcaption><span>Hey, I'm Laiba!</span></figcaption></figure>
    <span class="eyebrow dot">About</span>
    <h2>I make brand content that people stop scrolling for.</h2>
    <p class="big">As AI Creative Content Specialist at Hulk Marketing I direct AI-generated commercials and voiceover reels for clients in fostering, legal education, heritage and fitness. As a freelancer I design social media, wedding cards, menus and thumbnails, and I bring a Software Engineering degree to every workflow.</p>
    <div class="facts"><div><strong>50+</strong><span>freelance projects</span></div><div><strong>30+</strong><span>clients</span></div><div><strong>{len(works)}</strong><span>pieces in this portfolio</span></div><div><strong>BS</strong><span>Software Engineering</span></div></div>
  </div>
  <div class="discs">
    <div class="disc"><span class="eyebrow dot">Graphic design</span><h3>Design that sells the message</h3><p>Social creatives and carousels · branding and logos · wedding cards and invitations · menus, posters, thumbnails · Fiverr gig graphics</p><div class="tools"><span>Photoshop</span><span>Illustrator</span><span>Canva</span><span>Adobe Express</span></div></div>
    <div class="disc"><span class="eyebrow dot">AI creative</span><h3>Generative video with direction</h3><p>AI product commercials and UGC ads · prompt engineering for image and video · storyboards and scene planning · voiceover reels with word-synced motion · short-form editing</p><div class="tools"><span>Generative AI</span><span>LLMs</span><span>CapCut Pro</span><span>InShot</span></div></div>
    <div class="disc"><span class="eyebrow dot">Photography</span><h3>Light, composition, detail</h3><p>Product photography · event photography · creative and portrait shoots · lighting and composition · editing and retouching</p><div class="tools"><span>Canon EOS 400D</span><span>Photoshop</span></div></div>
  </div>
</div>''', section='About')

# 3 brands + capabilities
counts = {k: sum(1 for w in works if w['cat'] == k) for k in ('ai', 'motion', 'social', 'brand')}
add(f"""
<span class="eyebrow dot">Brands I've worked with</span>
<h2 style="margin:18px 0 34px">Real brands.<br><span class="pink">Made to stop the scroll.</span></h2>
<div class="clients"><span>Organic Fostering</span><span>IC London</span><span>British Muslim Heritage Centre</span><span>Bodyrade</span><span>Muddy Panda</span><span>Property Deals</span><span>Hulk Marketing</span><span>Zaitoon</span><span>Mr Pizza</span><span>SES, MUST</span></div>
<div class="caps">
  <div><strong>{counts['ai']}</strong><span>AI commercials</span></div>
  <div><strong>{counts['motion']}</strong><span>Motion reels</span></div>
  <div><strong>{counts['social']}</strong><span>Social designs</span></div>
  <div><strong>{counts['brand']}</strong><span>Branding &amp; print</span></div>
</div>""", section='Brands')


def divider(letter, title, sub, ids):
    imgs = ''.join(f'<img src="{still(i, 1)}">' for i in ids)
    add(f'''<div class="div"><div><span class="eyebrow dot">{letter}</span><h2 class="huge">{title}</h2><p class="big">{sub}</p></div><div class="divimgs">{imgs}</div></div>''',
        'plum', section=title)


# AI commercials
divider('AI creative', 'AI commercials', 'Product films, UGC ads and launch videos built shot by shot with generative video: prompts, storyboards, consistent characters and products, then the edit.',
        ['b-padel', 'b-dumble', 'mp-launch'])
add(f'''
<div class="case"><div class="casehead"><span class="eyebrow dot">Bodyrade · sports nutrition</span><h2>Eleven commercials, one consistent product world</h2>
<p>Stadium, padel court, gym and city: every scene generated, the product kept identical from shot to shot, then cut for Reels and TikTok.</p></div>
<div class="g4">{frame('b-football', 1, 'wide2', True)}{frame('b-padel', 1)}{frame('b-dumble', 2)}{frame('b-ugc', 1)}{frame('b-fresh', 2)}</div></div>''', section='AI commercials')
add(f'''<div class="g6">{frame('b-morning', 1)}{frame('b-city', 2)}{frame('b-powder', 3)}{frame('b-rooftop', 2)}{frame('b-cat', 1)}{frame('b-drop', 1)}</div>''',
    section='AI commercials')
add(f'''
<div class="case"><div class="casehead"><span class="eyebrow dot">Muddy Panda · streetwear · Property Deals · real estate</span><h2>Launch films and presenter reels</h2>
<p>A streetwear launch with AI models and set pieces, merch and unboxing product videos, and a property reel fronted by a consistent AI presenter.</p></div>
<div class="g4n">{frame('mp-launch', 1, '', True)}{frame('mp-merch', 2)}{frame('mp-box', 1)}{frame('pd-reel', 1)}</div></div>''', section='AI commercials')

# Motion reels
divider('AI creative', 'Motion reels', 'Voiceover reels where every spoken word pops its object on screen: 3D props, real people footage, captions and sound design.',
        ['of-canif', 'ic-sqe', 'bmhc'])
add(f'''
<div class="case"><div class="casehead"><span class="eyebrow dot">Organic Fostering · foster care agency, Manchester</span><h2>Six reels for a fostering agency</h2>
<p>Recruitment and trust-building stories: honest FAQ answers, a year in review, the carer journey and the support behind it.</p></div>
<div class="g6">{frame('of-canif', 1, '', True)}{frame('of-year', 1)}{frame('of-flow', 1)}{frame('of-support', 1)}{frame('of-day', 1)}{frame('of-anim', 1)}</div></div>''', section='Motion reels')
add(f'''
<div class="case"><div class="casehead"><span class="eyebrow dot">IC London · legal education · BMHC · heritage charity</span><h2>Explainers with real people</h2>
<p>Law-career explainers with word-synced 3D pop-ups, and a heritage story reel for the British Muslim Heritage Centre.</p></div>
<div class="vrow">{video_sheet('ic-sqe')}{video_sheet('bmhc')}</div></div>''', section='Motion reels')
add(f'''<div class="vrow">{video_sheet('ic-cv')}{video_sheet('ic-law')}</div>''', section='Motion reels')

# Social design
divider('Graphic design', 'Social design', 'Posts, carousels and ads for agencies, healthcare, food and lifestyle brands, designed to the brand and to the feed.',
        ['hm-find', 'of-teen', 'f-hasham'])
car = ''.join(f'<img src="{media_img("of-carousel", j)}">' for j in range(5))
add(f'''
<div class="case"><div class="casehead"><span class="eyebrow dot">Organic Fostering · recruitment carousel</span><h2>Think you can't foster?</h2>
<p>Five slides that bust the myths that stop people enquiring: renting, background, experience, money.</p></div>
<div class="carousel">{car}</div>{cap('of-carousel', ' · 5 slides')}</div>''', section='Social design')
add(f'''<div class="g4 tall">{frame('of-caring')}{frame('of-teen')}{frame('of-room')}{frame('of-lang')}</div>''', section='Social design')
add(f'''
<div class="case"><div class="casehead"><span class="eyebrow dot">Hulk Marketing · agency's own ads</span><h2>Ads for a marketing agency</h2>
<p>Three ads selling visibility to local businesses: one scene, one promise, one call to action.</p></div>
<div class="g3">{frame('hm-cafe', 0, '', True)}{frame('hm-find')}{frame('hm-first')}</div></div>''', section='Social design')
add(f'''<div class="g5">{frame('f-hasham')}{frame('f-surgical')}{frame('f-hiring')}{frame('f-zaitoon')}{frame('f-cosmetics', 1)}</div>''', section='Social design')
add(f'''<div class="g5">{frame('f-pizza', 1)}{frame('f-menu', 1)}{frame('f-gym')}{frame('f-stayhome')}{frame('f-salon', 1)}</div>
<div class="g2b">{frame('f-thumb', 0, 'wide2')}{frame('f-arfan', 1, 'wide2')}</div>''', section='Social design')

# Branding & print
divider('Graphic design', 'Branding & print', 'Identity exploration, invitations and event design, from wedding cards to a university society.',
        ['of-logo', 'w-parisa', 'ses-vote'])
add(f'''
<div class="case"><div class="casehead"><span class="eyebrow dot">Organic Fostering · identity</span><h2>Twelve logo directions</h2>
<p>Exploration for the Organic Fostering mark: family, growth and care in the brand's magenta, orange and green.</p></div>
<div class="logo"><img src="{still('of-logo')}"></div>{cap('of-logo')}</div>''', section='Branding & print')
add(f'''<span class="eyebrow dot">Invitations and events</span><h2 style="font-size:60px;margin-bottom:28px">Cards, invitations and society posters</h2>
<div class="g7">{frame('w-wedding', 1)}{frame('w-parisa', 1)}{frame('w-areej')}{frame('w-engage')}{frame('ses-invite')}{frame('ses-eid')}{frame('ses-vote')}</div>''', section='Branding & print')

# Photography
add(f'''
<div class="div photo"><div><span class="eyebrow dot">Photography</span><h2 class="huge">Photography</h2>
<p class="big">Product, event and creative photography on a Canon EOS 400D, with careful lighting, composition and post-production.</p>
<ul class="plist"><li>Product photography for e-commerce and social</li><li>Event coverage: weddings, ceremonies, university events</li><li>Creative and portrait shoots</li><li>Lighting and composition</li><li>Editing, retouching and colour grading</li></ul>
<p class="note">Photography samples available on request.</p></div>
<svg class="burst big" viewBox="0 0 100 100"><path fill="currentColor" d="M50 0 57 33 82 9 66 40 100 38 69 54 96 76 62 66 70 100 50 72 30 100 38 66 4 76 31 54 0 38 34 40 18 9 43 33Z"/></svg></div>''', 'plum', section='Photography')

# Experience
jobs = [
    ('Mar 2025 – Jul 2026', 'AI Creative Content Specialist', 'Hulk Marketing Ltd · Remote', 'Directed AI image and video content for client campaigns, from prompt to final edit. Built storyboards, scene descriptions and prompts that keep visuals consistent, and combined AI assets with design, editing and branding.'),
    ('May 2024 – Present', 'Graphic Designer & Video Editor', 'Self-employed · Gujranwala', '50+ projects for 30+ clients: social posts, thumbnails, wedding cards, posters and Fiverr gigs. Short-form video in CapCut and Adobe tools.'),
    ('Aug 2024 – Sep 2025', 'Social Services Manager', 'PTCL · Gujranwala', 'Social media content planning and management, post design, audience and analytics monitoring.'),
    ('Jun 2024 – Jul 2024', 'ICT Network Engineer', 'PTCL · Gujranwala', 'Network performance monitoring, issue logging and reporting.'),
    ('Oct 2023 – Nov 2023', 'Web Developer', 'Augury Tech · Rawalpindi', 'Front-end development in HTML and CSS; UI layout improvements.'),
    ('Jul 2023 – Aug 2023', 'Software Developer', 'Social Communication Organization · Mirpur, AJK', 'Windows billing-system features in C# and .NET; debugging and testing.'),
    ('2021 – 2025', 'BS Software Engineering', 'Mirpur University of Science and Technology', 'Python, C++, C#, OOP, software testing, AI and LLM fundamentals.'),
]
rows = ''.join(f'<div class="job"><span class="when">{a}</span><div><h3>{E(b)}</h3><span class="org">{E(c)}</span></div><p>{E(d)}</p></div>' for a, b, c, d in jobs)
add(f'<span class="eyebrow dot">Experience</span><h2 style="margin-bottom:22px">Creative work on an engineering foundation</h2><div class="xp">{rows}</div>', section='Experience')

# Contact
add(f'''
<div class="contact"><div><span class="eyebrow dot">Contact</span><h2 class="huge">Let's make something <span class="pink">people stop for.</span></h2>
<p class="big">Available for AI video, design and photography projects, remote or in Pakistan.</p></div>
<div class="rows">
<div><span class="k">Email</span><a href="mailto:laibajamalkhan6@gmail.com">laibajamalkhan6@gmail.com</a></div>
<div><span class="k">Phone / WhatsApp · Pakistan</span><span>+92 336776865</span></div>
<div><span class="k">Phone · Turkey</span><span>+90 (582) 552 8635</span></div>
<div><span class="k">LinkedIn</span><a href="https://www.linkedin.com/in/laiba-jamal-khan-5a1b89334/">linkedin.com/in/laiba-jamal-khan</a></div>
<div><span class="k">Instagram</span><a href="https://www.instagram.com/laibajamalk">@laibajamalk</a></div>
<div><span class="k">Watch the full videos</span><a href="{DRIVE}">Google Drive · full-resolution work folder</a></div>
</div></div>''', 'plum', section='Contact')

CSS = open(f'{HERE}/pdf.css').read()
doc = f'''<!doctype html><html><head><meta charset="utf-8">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@500;600;700&family=DM+Sans:opsz,wght@9..40,400;9..40,500;9..40,600&family=Caveat:wght@600&display=swap">
<style>{CSS}</style></head><body>{''.join(pages)}</body></html>'''
os.makedirs(OUTDIR, exist_ok=True)
open(f'{WS}/pdf.html', 'w').write(doc)
js = f'''
const {{ chromium }} = require('playwright');
(async () => {{
  const b = await chromium.launch();
  const p = await b.newPage({{ viewport: {{ width: 1920, height: 1080 }} }});
  await p.goto('file://{WS}/pdf.html', {{ waitUntil: 'networkidle' }});
  await p.evaluate(() => document.fonts.ready);
  await p.pdf({{ path: '{OUTDIR}/Laiba_Jamal_Portfolio.pdf', width: '1920px', height: '1080px', printBackground: true, margin: {{top:0,right:0,bottom:0,left:0}} }});
  await p.screenshot({{ path: '{WS}/pdf_preview.png', fullPage: true }});
  await b.close();
}})();'''
open(f'{WS}/pdf.js', 'w').write(js)
subprocess.run(['node', f'{WS}/pdf.js'], check=True, cwd=WS)
print('pages', len(pages))
