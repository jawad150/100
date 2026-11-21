"""Build the Growth Room shooting script (all six episodes) as a .docx."""
import sys
from docx import Document
from docx.shared import Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH

OUT = sys.argv[1]
GREEN = RGBColor(0x1F, 0x6B, 0x3A)
GREY = RGBColor(0x66, 0x66, 0x66)

doc = Document()
st = doc.styles["Normal"]
st.font.name = "Calibri"
st.font.size = Pt(11)
st.paragraph_format.space_after = Pt(4)
from docx.shared import Cm
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
for sec in doc.sections:
    sec.page_width, sec.page_height = Cm(21.0), Cm(29.7)
    sec.left_margin = sec.right_margin = Cm(2.0)
    sec.top_margin = sec.bottom_margin = Cm(1.8)


def heading(text, level):
    h = doc.add_heading(text, level=level)
    h.paragraph_format.keep_with_next = True
    if level == 1 and (text.startswith("Episode") or text.startswith("Recording")):
        h.paragraph_format.page_break_before = True
    for r in h.runs:
        r.font.color.rgb = GREEN if level <= 1 else RGBColor(0, 0, 0)


def note(text):
    p = doc.add_paragraph()
    r = p.add_run(text)
    r.italic = True
    r.font.color.rgb = GREY
    return p


def cam(shot, action=None):
    """A camera direction line: [SHOT] action."""
    p = doc.add_paragraph()
    r = p.add_run(f"[{shot}]")
    r.bold = True
    r.font.color.rgb = GREEN
    if action:
        a = p.add_run(" " + action)
        a.italic = True
    p.paragraph_format.space_after = Pt(2)
    return p


def line(who, words, how=None):
    p = doc.add_paragraph()
    p.paragraph_format.left_indent = Pt(24)
    r = p.add_run(who)
    r.bold = True
    if how:
        h = p.add_run(f" ({how})")
        h.italic = True
        h.font.color.rgb = GREY
    p.add_run(": " + words)
    p.paragraph_format.space_after = Pt(6)
    return p


def text_on_screen(t):
    p = doc.add_paragraph()
    p.paragraph_format.left_indent = Pt(24)
    r = p.add_run("ON SCREEN: " + t)
    r.font.size = Pt(9.5)
    r.font.color.rgb = GREY
    p.paragraph_format.space_after = Pt(6)


def endcard(n, cta=None):
    cam("BLACK CARD")
    t = f"THE GROWTH ROOM · with Hassan Pasha · Episode {n}"
    if cta:
        t += f" · Comment \"{cta}\""
    text_on_screen(t)


def extras(delivery, broll, record=None):
    """Delivery notes, B-roll table and what-to-record list for one episode."""
    heading("Delivery — how he says it", 3)
    for d in delivery:
        doc.add_paragraph(d, style="List Bullet")
    heading("B-roll to record", 3)
    if not broll:
        doc.add_paragraph("None needed — this episode is all Hassan.")
    else:
        tbl = doc.add_table(rows=1, cols=5)
        tbl.style = "Light Grid Accent 1"
        tbl.autofit = False
        for i, h in enumerate(["ID", "Shot", "Angle", "Length", "Takes"]):
            tbl.rows[0].cells[i].text = h
        for row in broll:
            cells = tbl.add_row().cells
            for i, v in enumerate(row):
                cells[i].text = v
        widths = [Cm(1.6), Cm(7.4), Cm(4.2), Cm(2.0), Cm(1.8)]
        for ci, col in enumerate(tbl.columns):
            col.width = widths[ci]
        for ri, r in enumerate(tbl.rows):
            trPr = r._tr.get_or_add_trPr()
            cs = OxmlElement("w:cantSplit"); trPr.append(cs)
            if ri == 0:
                th = OxmlElement("w:tblHeader"); trPr.append(th)
            for ci, c in enumerate(r.cells):
                c.width = widths[ci]
                for para in c.paragraphs:
                    para.paragraph_format.space_after = Pt(0)
                    for run in para.runs:
                        run.font.size = Pt(9.5)
                    if ri < len(tbl.rows) - 1:
                        para.paragraph_format.keep_with_next = True
    if record:
        heading("What to record", 3)
        for r in record:
            doc.add_paragraph(r, style="List Bullet")


STD_RECORD = [
    "Full episode on CAM M, 3 takes. Full episode on CAM W, 2 takes.",
    "Every punchline and reaction on CAM P, 3 takes each.",
    "The last line to the lens, 5 takes.",
]

# ---------- Title ----------
t = doc.add_heading("The Growth Room with Hassan Pasha", 0)
t.alignment = WD_ALIGN_PARAGRAPH.LEFT
doc.add_paragraph("Shooting script · Episodes 1–6 · each 24–36 seconds")

heading("Who Hassan is (the facts every episode uses)", 2)
doc.add_paragraph(
    "Hassan Pasha, founder of Hulk Group and 360 Business Group, based in the UK. "
    "He helps UK businesses grow with SEO, digital marketing, AI and automation. "
    "He has delivered 700+ projects and built 250+ brands."
)

heading("The set (same every episode)", 2)
for b in [
    "Room: a corner of the Hulk office with at least 2.5 m behind the chair, darker and warmer than a plain white room.",
    "Chair: a lounge chair or leather armchair, angled about 30° toward the interviewer's spot. Same chair every episode.",
    "Side table at his left hand: his phone and a coffee. The phone is part of every episode.",
    "Behind him: a low shelf with 3–4 objects (books, a framed print of client work), a monitor with a soft, out-of-focus dashboard, one warm lamp.",
    "Brand accent: one deep-green element in frame (a plant, a cushion or book spines). Only one.",
    "Light: one large soft key light from his front-left (a window or a softbox), the other side of his face slightly darker, the warm lamp behind. Overhead lights off.",
    "Microphone: lav mic clipped mid-chest, visible. Phones on 4K, 25 fps, focus locked on his eyes.",
]:
    doc.add_paragraph(b, style="List Bullet")

heading("How he sits and talks", 2)
for b in [
    "Wardrobe: a signature look he repeats every episode — dark knit or overshirt, dark trousers, no logos, stripes or small checks.",
    "Sitting back, not perched. One ankle resting on the other knee, or legs crossed. Forearms on the armrests, hands loose; hands open only for a list or a number.",
    "Leans slightly forward for the serious point, sits back for the joke.",
    "Talks like he is telling a friend, not pitching on stage. Normal speed, warm, unhurried.",
    "Jokes are always deadpan: straight face, no laughing at his own line, let the pause do the work.",
    "Interviewer episodes: he looks at the interviewer, never the lens, except for the final line. Solo episodes 2 and 4: straight into the lens throughout.",
]:
    doc.add_paragraph(b, style="List Bullet")

heading("How to read this script", 2)
for b in [
    "CAM M = main camera, medium shot. In solo episodes 2 and 4 it sits straight in front of Hassan at eye level and he talks into the lens. In the other episodes it sits 30° off his eyeline, with the interviewer right beside it.",
    "CAM W = wide shot of the whole chair, side table and set.",
    "CAM P = profile close-up from his right side, for reactions.",
    "INSERT = a close-up recorded separately (the phone on the table, screens, hands).",
    "Every episode opens with the signature shot: Hassan's hand laying his phone face-down beside a coffee.",
    "Solo episodes: 1, 2 and 4 (only Hassan speaks). Interviewer episodes: 3, 5 and 6 (an off-camera voice asks).",
    "Someone off camera rings Hassan's phone on cue for the buzzes in Episodes 1, 3 and 4.",
    "Every take: 2 seconds of stillness before the first word and after the last. If a line fluffs, pause and restart the sentence without stopping the camera.",
]:
    doc.add_paragraph(b, style="List Bullet")

# ---------- Episode 1 ----------
heading("Episode 1 — \"I'm Hassan Pasha\"", 1)
note("Solo · about 24 seconds · pinned intro. He talks to someone sitting silently beside the camera; looks into the lens only for the last line.")
cam("INSERT – table height", "Hassan's hand lays his phone face-down beside a coffee.")
cam("CAM W", "He settles back, ankle onto knee.")
cam("CAM M")
line("HASSAN", "I'm Hassan Pasha.", "relaxed")
line("HASSAN", "I'm the founder of Hulk Group and 360 Business Group, here in the UK.")
cam("INSERTS – 4 quick screens", "Google search · ads dashboard · AI reply · automation workflow.")
line("HASSAN", "We help UK businesses grow — with SEO, digital marketing, AI and automation.")
cam("CAM P")
line("HASSAN", "So far, we've delivered over seven hundred projects… and built more than two hundred and fifty brands.")
text_on_screen("700+ PROJECTS DELIVERED · 250+ BRANDS BUILT")
cam("INSERT – macro", "The face-down phone buzzes on the table.")
cam("CAM M", "He glances at it, turns it over and reads it. We never see the screen.")
line("HASSAN", "…Two hundred and fifty-one.", "deadpan")
text_on_screen("250+ ticks over to 251")
cam("CAM W", "He lays the phone face-down again. Small smile.")
cam("CAM M", "He turns straight to the lens.")
line("HASSAN", "This is The Growth Room.")
endcard(1)
extras(
    [
        "\"I'm Hassan Pasha.\" Short, a full stop after it.",
        "Founder line: steady and clear, light weight on \"Hulk Group\" and \"360 Business Group\"; \"here in the UK\" a touch softer.",
        "Services line: four even beats. Hands can open on this line only.",
        "Numbers line: proud but plain. A small pause after \"seven hundred projects\".",
        "The buzz: wait one second, glance down, turn the phone over like it's routine.",
        "\"…Two hundred and fifty-one.\" Completely flat, eyes on the phone. The smile comes only when he puts it down.",
        "\"This is The Growth Room.\" The only look into the lens. Calm, slight nod.",
    ],
    [
        ("E1-B1", "Hand lays the phone face-down next to a coffee", "Close-up, table height", "5s", "3"),
        ("E1-B2", "Google search \"electrician near me\", map results", "Phone screen", "6s", "2"),
        ("E1-B3", "Ads dashboard (numbers blurred or demo)", "Laptop screen", "6s", "2"),
        ("E1-B4", "AI assistant replying to a customer (demo)", "Phone screen", "6s", "2"),
        ("E1-B5", "Automation workflow (boxes and arrows)", "Laptop screen", "6s", "2"),
        ("E1-B6", "Face-down phone buzzing on the table", "Macro, table height", "5s", "3"),
    ],
    STD_RECORD + ["Alternative take: the phone buzzes again straight after \"…two hundred and fifty-one\"; without looking: \"…fifty-two.\""],
)

# ---------- Episode 2 ----------
heading("Episode 2 — \"You don't need more followers\"", 1)
note("Solo · about 28 seconds · Hassan talks straight into the lens the whole time.")
cam("INSERT – table height", "Phone laid face-down.")
cam("CAM M – straight-on")
line("HASSAN", "Unpopular opinion: most UK businesses don't need more followers.")
text_on_screen("UNPOPULAR OPINION")
line("HASSAN", "Two plumbers. One has thirty thousand followers and twelve reviews. The other has three hundred followers and two hundred reviews.")
text_on_screen("Two profile cards: 30,000 followers · 12 reviews  vs  300 followers · 200 reviews (Illustrative)")
cam("CAM P")
line("HASSAN", "The first one isn't a plumber. He's an influencer with a van.", "deadpan, no smile, moves straight on")
cam("CAM M")
line("HASSAN", "The second one's phone never stops ringing.")
line("HASSAN", "Followers are applause. Reviews are bookings.", "slower")
text_on_screen("FOLLOWERS ARE APPLAUSE. REVIEWS ARE BOOKINGS.")
line("HASSAN", "This week, ask ten happy customers for a review. Comment \"REVIEWS\" and I'll send you the exact message we use.")
endcard(2)
note("Backup punchlines (same spot): \"That's not a business. That's a fan club.\" / \"Nobody has ever said, 'Great plumber. Loved his Reels.'\"")
extras(
    [
        "Opening: calm and sure, like stating a fact, not starting an argument.",
        "The two plumbers: quick and flat, just the numbers.",
        "\"He's an influencer with a van.\" Straight face, no smile, no pause after. Move on; the audience does the laughing.",
        "\"Followers are applause. Reviews are bookings.\" Slower, a small pause in the middle.",
        "The CTA: warm and direct into the lens.",
    ],
    [("E2-B1", "Optional: Google reviews scrolling (demo account)", "Phone screen", "3s", "1")],
    STD_RECORD + ["Record both backup punchlines on CAM P, 3 takes each."],
)

# ---------- Episode 3 ----------
heading("Episode 3 — \"The 11pm WhatsApp\"", 1)
note("With interviewer · about 35 seconds.")
cam("INSERT – table height", "Phone laid face-down.")
cam("CAM W")
line("INTERVIEWER", "What's the most expensive employee in a small business?", "off camera")
cam("CAM M")
line("HASSAN", "The owner. Answering WhatsApp at eleven at night.")
cam("INSERT – macro", "The phone buzzes.")
cam("CAM P", "He glances down, back up.")
line("HASSAN", "…See?")
cam("CAM M ↔ INSERT", "Cut to the buzzing phone after each question, faster each time.")
line("HASSAN", "It's always the same questions. \"How much?\" (buzz) \"Are you free Saturday?\" (buzz) \"Where's my order?\" (buzz, buzz)")
text_on_screen("Message bubbles stack up the screen")
line("HASSAN", "…That one's asked twice.", "staring at the phone")
cam("CAM W")
line("INTERVIEWER", "Are you going to get that?", "laughing")
line("HASSAN", "No.")
cam("CAM W", "He slides the phone under his seat cushion. It keeps buzzing, muffled.")
cam("CAM M", "Serious, ignoring the buzzing.")
line("HASSAN", "Those questions don't need you. They need an answer in ten seconds, any hour, with a link to book. That's what we automate.")
cam("CAM W", "He pulls the phone out and reads it.")
line("HASSAN", "Fourteen.")
cam("CAM P")
line("INTERVIEWER", "Are you going to answer them?")
cam("INSERT → CAM M", "He turns the screen to camera: every message has an instant reply with a booking link.")
line("HASSAN", "Already done.", "first real smile")
endcard(3, "AUTOMATE")
extras(
    [
        "\"The owner.\" Instant, then a beat before the rest.",
        "The buzzes: leave a gap after each question; each gap slightly shorter, like a busy evening.",
        "\"…That one's asked twice.\" Flat, still looking at the phone.",
        "The cushion: calm, eyes on the interviewer, as if it's normal. Ignore the muffled buzzing completely.",
        "\"Already done.\" The first real smile of the episode.",
    ],
    [
        ("E3-B1", "Face-down phone buzzing (6–8 separate buzzes)", "Macro, table height", "10s", "3"),
        ("E3-B3", "Customer asks a price, instant reply with booking link (demo)", "Phone screen", "6s", "1"),
        ("E3-B7", "Chat list with every message answered (demo, set up before)", "Phone held to camera", "4s", "3"),
    ],
    STD_RECORD + ["Also record a muffled buzz with the phone under the real cushion, so the editor can place it by hand."],
)

# ---------- Episode 4 ----------
heading("Episode 4 — \"The most expensive word\"", 1)
note("Solo · about 29 seconds · Hassan talks straight into the lens.")
cam("INSERT – table height", "Phone laid face-down.")
cam("CAM M – straight-on")
line("HASSAN", "The most expensive word in a small business? \"Later.\"", "one-second pause before \"Later\"")
text_on_screen("LATER.")
cam("CAM M → CAM P → CAM M")
line("HASSAN", "\"I'll reply later.\" \"I'll fix the website later.\" \"I'll ask for reviews later.\"")
cam("CAM M – slow push-in")
line("HASSAN", "And \"later\" is exactly when your customer finds someone else.")
cam("INSERT – macro", "The phone buzzes.")
cam("CAM M", "He glances at it.")
line("HASSAN", "…I'll get that later.", "casual, without thinking")
cam("CAM W", "A beat. He realises what he just said and picks the phone straight up.")
line("HASSAN", "…Fine.", "quiet, a little embarrassed")
cam("CAM M")
line("HASSAN", "Pick one \"later\" and do it today. Comment \"TODAY\" and tell me which one.")
endcard(4)
extras(
    [
        "\"Later.\" On its own, after a one-second pause.",
        "The three examples: light and familiar, things he hears every week.",
        "\"…I'll get that later.\" Totally casual, without thinking. The audience gets the joke before he does.",
        "The realisation: a slow look back at the lens, then pick the phone up quickly. \"…Fine\" is quiet and a little embarrassed.",
    ],
    [],
    STD_RECORD,
)

# ---------- Episode 5 ----------
heading("Episode 5 — \"£1,000 and a new business\"", 1)
note("With interviewer · about 33 seconds · prop: an envelope with £1,000 in prop notes.")
cam("INSERT – top-down", "The interviewer slides an envelope across the side table. Hassan opens it.")
line("INTERVIEWER", "A thousand pounds. Brand-new business. Where does it go?", "off camera")
cam("CAM M")
line("HASSAN", "First, nothing. Your Google Business Profile is free. Do it properly.", "small smile")
cam("INSERT – top-down ↔ CAM M", "He counts the notes into three piles, one per line.")
line("HASSAN", "Three hundred: a website with one job — a \"book now\" button. Five hundred: local ads for a month. You're buying data, not fame. One-fifty: automatic review requests.")
text_on_screen("WEBSITE £300 · LOCAL ADS £500 · REVIEWS £150 (Illustrative budget)")
cam("CAM W")
line("INTERVIEWER", "That leaves fifty.")
cam("CAM M", "He holds up one note.")
line("HASSAN", "Logo.", "flat")
cam("CAM W")
line("INTERVIEWER", "Fifty quid on a logo?")
cam("CAM P → CAM M")
line("HASSAN", "Nike paid thirty-five dollars for theirs. You can be famous later.")
cam("INSERT – top-down → CAM W", "The interviewer's hand creeps in for the fifty. Without looking, Hassan slides it away.")
line("HASSAN", "Logo budget.")
endcard(5, "START")
extras(
    [
        "\"First, nothing.\" A small smile; it surprises people.",
        "Counting: each pile lands, then the line. \"You're buying data, not fame\" is the quotable one.",
        "\"Logo.\" Totally flat, holding up one note.",
        "\"You can be famous later.\" A beat after the Nike line, warm, half-smile.",
        "\"Logo budget.\" Doesn't look at the hand.",
    ],
    [
        ("E5-B1", "Envelope slid across the table and opened", "Top-down", "4s", "3"),
        ("E5-B2", "Notes counted into three piles", "Top-down", "4s each", "2"),
        ("E5-B4", "Interviewer's hand creeping in; Hassan sliding the note away", "Top-down", "4s", "3"),
    ],
    STD_RECORD,
)

# ---------- Episode 6 ----------
heading("Episode 6 — \"How long does SEO take?\"", 1)
note("With interviewer · about 30 seconds · prop: a small dumbbell on the floor beside the chair. \"Three to six months\" is the usual guidance for local SEO; never promise a ranking or a date.")
cam("INSERT – table height", "Phone laid face-down.")
cam("CAM W")
line("INTERVIEWER", "How long does SEO take?", "off camera")
cam("CAM M")
line("HASSAN", "How long does the gym take?", "instant")
cam("CAM W")
line("INTERVIEWER", "…Depends?")
cam("CAM W → CAM P → CAM M", "He picks up the dumbbell, does one curl, checks his arm, puts it down.")
line("HASSAN", "Exactly. Go once, check the mirror, and you'll be disappointed.")
cam("CAM M – slow push-in")
line("HASSAN", "For most local businesses, SEO starts moving in three to six months. It depends how busy your area is.")
text_on_screen("MONTH 1 → MONTHS 3–6")
cam("CAM W")
line("INTERVIEWER", "So why do some people promise page one in a week?")
cam("CAM P")
line("HASSAN", "Same reason they sell six-pack abs in seven days.", "dry, sitting back")
cam("CAM W")
line("INTERVIEWER", "And if someone guarantees you page one?")
cam("CAM M – to the lens")
line("HASSAN", "Smile. Say thank you. (beat) And run.")
endcard(6, "SEO")
extras(
    [
        "\"How long does the gym take?\" Immediate, like he's heard the question a thousand times.",
        "The curl: one slow curl, a serious look at his arm, a slight disappointed nod.",
        "The SEO answer: calm and honest. \"It depends\" makes him sound trustworthy, not vague.",
        "\"Six-pack abs in seven days.\" Dry, sitting back, the faintest smile.",
        "\"Smile. Say thank you. And run.\" Three short beats, the longest pause before \"And run.\"",
    ],
    [("E6-B3", "Dumbbell set down beside the chair", "Close-up, floor level", "3s", "2")],
    STD_RECORD,
)

heading("Recording plan", 1)
for b in [
    "Day 1 (solo, about 4 hours): Episodes 1, 2 and 4. Episode 1 first, while Hassan is fresh.",
    "Day 2 (with interviewer, about 4 hours): Episodes 3, 5 and 6. The interviewer sits beside CAM M at Hassan's eye height.",
    "Same outfit both days. Take a photo of the set so it can be rebuilt exactly.",
    "Props: a second phone to ring Hassan's phone on cue (Episodes 1, 3, 4); prop cash in an envelope (Episode 5); a small dumbbell (Episode 6).",
    "Before rolling: 4K, 25 fps, HDR off, focus locked on his eyes, lav mic peaking around -12 dB, Do Not Disturb on every other phone, 30 seconds of room tone.",
    "Name files GR_E[episode]_[camera]_T[take] (for example GR_E2_CAMM_T03) and send the originals through Google Drive, never WhatsApp.",
]:
    doc.add_paragraph(b, style="List Bullet")

heading("Edit style", 1)
for b in [
    "Hard cuts only, on a sentence break, a laugh or a look. Longest shot about 5 seconds.",
    "Slow digital push-ins (100 to 106–110%) on CAM M for the serious line and the punchline.",
    "Captions: clean sans-serif, 2–4 words at a time, off-white, keywords in brand green, interviewer lines in italics.",
    "Sound: real room tone, keep the interviewer's laugh, soft piano bed cut to silence one beat before each punchline, one piano note on the black end card. Master to -14 LUFS.",
    "Black end card, 2 seconds: THE GROWTH ROOM / with Hassan Pasha · Episode N, then HULK GROUP · 360 BUSINESS GROUP.",
    "Exports: 1080x1920 at 25 fps for Instagram, TikTok and Shorts; 1080x1350 for LinkedIn with an .srt caption file.",
]:
    doc.add_paragraph(b, style="List Bullet")

doc.save(OUT)
print("saved", OUT)
