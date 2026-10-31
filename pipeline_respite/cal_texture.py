"""Draw the wall-calendar texture (photo top half, November 2026 grid, handwritten notes, two circled weekends)."""
import os, math
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont
S = '/home/user/100/workspace_respite'
F = '/home/user/100/workspace_sol/fonts'
W, H = 1500, 1900
im = Image.new('RGB', (W, H), (253, 251, 246))
d = ImageDraw.Draw(im)
# photo (top): a real landscape frame
cap = cv2.VideoCapture('/home/user/100/workspace_respite/clips/9726.mp4'); cap.set(1, int(cap.get(7) * 0.5)); ok, fr = cap.read()
fr = cv2.cvtColor(fr, cv2.COLOR_BGR2RGB); ph = 520
h0, w0 = fr.shape[:2]; sc = max(W / w0, ph / h0); fr = cv2.resize(fr, (int(w0 * sc) + 1, int(h0 * sc) + 1))
fr = fr[(fr.shape[0] - ph) // 2:(fr.shape[0] - ph) // 2 + ph, (fr.shape[1] - W) // 2:(fr.shape[1] - W) // 2 + W]
im.paste(Image.fromarray(fr), (0, 0))
d.rectangle([0, ph, W, ph + 8], fill=(91, 23, 79))
nun = lambda w, s: ImageFont.truetype(f'{F}/Nunito-{w}.ttf', s)
pop = ImageFont.truetype(f'{F}/Poppins-SemiBold.ttf', 30)
hand = ImageFont.truetype(f'{F}/Caveat-700.ttf', 44)
handb = ImageFont.truetype(f'{F}/Caveat-700.ttf', 62)
d.text((70, ph + 40), 'November', font=nun(900, 96), fill=(91, 23, 79))
d.text((W - 70, ph + 70), '2026', font=nun(800, 60), fill=(255, 100, 17), anchor='ra')
gx, gy, gw = 50, ph + 200, W - 100
cw = gw / 7; rows = 6; ch = (H - 60 - gy - 50) / rows
for i, dn in enumerate(['MON', 'TUE', 'WED', 'THU', 'FRI', 'SAT', 'SUN']):
    d.text((gx + i * cw + cw / 2, gy), dn, font=pop, fill=(255, 100, 17) if i >= 5 else (120, 90, 110), anchor='mm')
top = gy + 40
for r in range(rows + 1):
    d.line([(gx, top + r * ch), (gx + gw, top + r * ch)], fill=(215, 205, 210), width=3)
for i in range(8):
    d.line([(gx + i * cw, top), (gx + i * cw, top + rows * ch)], fill=(215, 205, 210), width=3)
notes = {3: ('Swim 6pm', (40, 50, 120)), 5: ('Bonfire night', (40, 50, 120)), 11: ('Dentist', (40, 50, 120)), 16: ('Book club', (40, 50, 120)),
         19: ('Training', (40, 50, 120)), 28: ("Mum's 60th", (40, 50, 120)), 25: ('Bins!', (40, 50, 120))}
cells = {}
for day in range(1, 31):
    r, c = divmod(day + 5, 7)
    x0, y0 = gx + c * cw, top + r * ch
    cells[day] = (x0, y0)
    d.text((x0 + 16, y0 + 10), str(day), font=nun(800, 40), fill=(91, 23, 79))
    if day in notes:
        t, col = notes[day]
        d.text((x0 + cw / 2, y0 + ch * 0.66), t, font=hand, fill=col, anchor='mm')
im.save(f'{S}/tex/cal_base.png')
# marker layer (orange) drawn with numpy for a felt-tip look
arr = np.array(im).astype(np.float32)
lay = np.zeros((H, W), np.uint8)
rng = np.random.default_rng(3)
for (sat, label) in ((7, 'Pancakes + park'), (21, 'Pancakes again!')):
    x0, y0 = cells[sat]
    cx, cy = x0 + cw, y0 + ch * 0.56
    t = np.linspace(0, 2 * math.pi * 1.1, 160)
    pts = np.stack([cx + cw * 1.02 * np.cos(t) * (1 + 0.04 * np.sin(3 * t)) + rng.normal(0, 1.2, len(t)),
                    cy + ch * 0.5 * np.sin(t) * (1 + 0.05 * np.cos(2 * t)) + rng.normal(0, 1.2, len(t))], 1)
    cv2.polylines(lay, [(pts * 4).astype(np.int32)], False, 255, 11 * 4, cv2.LINE_AA, shift=4 - 2)
m = (lay.astype(np.float32) / 255)[..., None]
arr = arr * (1 - m * 0.92) + np.array([255, 100, 17], np.float32) * m * 0.92
im2 = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8))
d2 = ImageDraw.Draw(im2)
for (sat, label) in ((7, 'Pancakes + park'), (21, 'Pancakes again!')):
    x0, y0 = cells[sat]
    d2.text((x0 + cw, y0 + ch * 0.68), label, font=handb, fill=(232, 80, 10), anchor='mm')
im2.save(f'{S}/tex/calendar.png')
print('ok', im2.size)
