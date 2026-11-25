"""Scene sheet for OF "Can I add a page?" -> reel/organic_fostering/can_i_add_a_page/scenes_storyboard.jpg"""
import os, textwrap
from PIL import Image, ImageDraw, ImageFont
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
ST = f'{ROOT}/workspace_page/stills'
OUT = f'{ROOT}/reel/organic_fostering/can_i_add_a_page'
os.makedirs(OUT, exist_ok=True)
F = lambda w, s: ImageFont.truetype(f'{ROOT}/workspace_sol/fonts/Nunito-{w}.ttf', s)
SC = [('00190', '0:00', 'Young person: “Can I put something on this page?”', 'Opens on a soft defocus, overhead inside the open 3D book. “Can I / add a page?” stacked type. A tap ring, then a plum four-point star pops 0 to 110 to 100%.'),
      ('00830', '0:04', 'Carer: “Course. We made this so you could get to know us.”', 'Kitchen and park photos land on the page (94, 103, then 100%), opposing tilts, a faint grid behind each; labels reveal left to right with star bullets.'),
      ('00890', '0:08', '', 'The page corner lifts towards camera until the paper fills the screen, then peels away onto the blank new page.'),
      ('01440', '0:10', 'Young person: “I watch City with my brother. We always text when they score.”', 'Mostly monochrome; a 3D sky-blue scarf slides in. On “text” a 3D phone buzzes once and paper bubbles pop: “GOAL!”, then “I KNOW!” six frames later.'),
      ('01930', '0:18', 'Carer: “What time’s kick-off?”', 'Cut on the pen touching paper: a 3D pen writes “Match day” in real handwriting; the book is drawn a little closer; colour returns.'),
      ('02180', '0:21', 'Young person: “Three. I’ve already checked.”', 'On “Three”, a plum “3:00” stamp lands beside the scarf (four-frame scale settle, soft desk tap).'),
      ('02740', '0:26', 'On screen: “Room to grow, roots to keep.”', 'Pull back to the whole spread: household photos beside the new page. The line rises from behind the page edge.'),
      ('03150', '0:29', 'On screen: “Thinking about fostering in Greater Manchester?” · Start your enquiry · Link in bio', 'An ivory circle opens from the scarf stitch to the end card: official logo on ivory, held still, room tone.')]
tw, th, cols = 270, 480, 4
rows = (len(SC) + cols - 1) // cols
cellh = th + 210
sheet = Image.new('RGB', (cols * (tw + 26) + 26, 150 + rows * cellh), (247, 243, 238))
d = ImageDraw.Draw(sheet)
d.text((26, 26), 'Organic Fostering  ·  Can I add a page?', font=F(900, 42), fill=(43, 43, 43))
d.text((26, 86), '9:16 · 34 s · 25 fps · overhead 3D book on a pale grid (after your reference) · scenes for approval', font=F(400, 22), fill=(110, 105, 100))
for i, (f, tc, vo, vis) in enumerate(SC):
    im = Image.open(f'{ST}/{f}.png').resize((tw, th), Image.LANCZOS)
    x = 26 + (i % cols) * (tw + 26)
    y = 140 + (i // cols) * cellh
    sheet.paste(im, (x, y))
    d.rounded_rectangle([x, y, x + 70, y + 30], 8, fill=(91, 23, 79))
    d.text((x + 10, y + 4), tc, font=F(800, 19), fill=(255, 255, 255))
    yy = y + th + 8
    for ln in textwrap.wrap(vo, 34)[:3]:
        d.text((x, yy), ln, font=F(800, 16), fill=(43, 43, 43))
        yy += 20
    for ln in textwrap.wrap(vis, 40)[:5]:
        d.text((x, yy + 4), ln, font=F(400, 15), fill=(100, 96, 92))
        yy += 19
sheet.save(f'{OUT}/scenes_storyboard.jpg', quality=92)
print('sheet', sheet.size)
