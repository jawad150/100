"""Build the on-set shooting guide (guide.html + guide_cover.html) from shot data."""
import html, os

OUT = os.path.dirname(os.path.abspath(__file__))
E = html.escape


def shot(code, what, frame, action, takes, say=None, ai=None):
    return dict(code=code, what=what, frame=frame, action=action, takes=takes, say=say, ai=ai)


def shot_table(rows):
    out = ['<table class="shots"><thead><tr><th></th><th>Shot</th><th>What to film</th><th>Framing / camera</th><th>Action, lines &amp; notes</th><th>Takes</th></tr></thead><tbody>']
    for r in rows:
        extra = ''
        if r['say']:
            extra += f'<span class="say">{r["say"]}</span>'
        if r['ai']:
            extra += f'<span class="ai-note">AI: {r["ai"]}</span>'
        out.append(f'<tr><td class="ck"></td><td class="code">{r["code"]}</td><td><b>{r["what"]}</b></td>'
                   f'<td class="fr">{r["frame"]}</td><td>{r["action"]}{extra}</td><td class="tk">{r["takes"]}</td></tr>')
    out.append('</tbody></table>')
    return '\n'.join(out)


def idea_sub(code, title, desc):
    return f'<div class="idea-sub"><span class="code">{code}</span><span class="t">{title}</span><span class="d">{desc}</span></div>'


def location(n, eyebrow, title, meta, setup_left, setup_right, blocks):
    parts = [f'<div class="loc"><div class="loc-band"><div class="n">{n}</div><div><div class="eyebrow">{eyebrow}</div><h2>{title}</h2></div><div class="meta">{meta}</div></div>']
    parts.append('<div class="setup"><div><span class="lbl">Set up</span><ul>' + ''.join(f'<li>{x}</li>' for x in setup_left) + '</ul></div>'
                 '<div><span class="lbl">Watch out</span><ul>' + ''.join(f'<li>{x}</li>' for x in setup_right) + '</ul></div></div>')
    for b in blocks:
        parts.append(b)
    parts.append('</div>')
    return '\n'.join(parts)


# ---------------------------------------------------------------- LOCATIONS
L1 = location(
    1, 'Location 1 · about 60 min', 'Reception',
    'Ideas <b>01 · J</b><br>Shoot first, while the room is tidy',
    ['Tripod with exposure, focus and white balance <b>locked</b> (no auto)',
     'Main camera vertical 9:16, 4K, 25fps',
     'Hide client files, post and visitor book (GDPR sweep)',
     'Sound: door chime ×3 + 30s of room tone (everyone silent)'],
    ['<b>Do not move the tripod</b> between the clean plate and stand-in takes; the AI needs identical framing',
     'Nobody walks through clean plates',
     'If sunlight is changing, close the blinds and light it yourself'],
    [idea_sub('01', 'The Door to Every Business in Bury', 'Empty reception fills with clients via AI'),
     shot_table([
         shot('01-A', 'Clean plate: WIDE', 'Tripod · wide of the whole reception', '15 seconds of the <b>empty</b> room. Nobody in frame.', '2', ai='frame-first + Kling 3.0'),
         shot('01-B', 'Clean plate: DESK', 'Tripod · medium on the front desk', '15 seconds empty.', '2', ai='frame-first'),
         shot('01-C', 'Clean plate: DOOR', 'Tripod · facing the entrance', '15 seconds empty.', '2', ai='frame-first'),
         shot('01-D', 'Stand-in welcome: WIDE', 'Same as 01-A (do not move tripod)', 'Real staff member behind the desk. A team member in a <b>plain t-shirt</b> walks in; handshake and smile.', '3', say='“Morning! Come on in.”', ai='Genjutsu Object Swap'),
         shot('01-E', 'Stand-in welcome: DESK + DOOR', 'Same as 01-B and 01-C', 'Repeat the welcome in each angle. Try 2 stand-ins at once.', '2 each', ai='Genjutsu Object Swap'),
         shot('01-F', 'Empty push-in', 'Gimbal · slow walk forward', '10–15 seconds, slow and steady, from the door to the desk. Empty room.', '3', ai='Seedance 2.5 / Kling Omni Edit'),
         shot('01-G', 'Clock 8:59 → 9:00', 'Close-up', 'Wall clock or a phone clock ticking over to 9:00.', '2'),
         shot('01-H', 'Door opening', 'Medium from inside', 'Team member unlocks and opens the door / flips the sign.', '2'),
         shot('01-I', 'Real handshake (human anchor)', 'Medium + close-up', 'Real staff greets a “client” (team member). Warm, natural.', '3'),
         shot('01-J', 'Logo wall', 'Slow push-in', 'For the end card. Clean, well lit.', '2'),
         shot('01-K', 'Whole team in reception', 'Tripod = 01-A framing', 'Everyone turns to camera and smiles (final wide shot).', '2'),
         shot('01-L', 'Reference stills', 'Photo · plain wall', 'Hi-vis, hard hat, chef whites, lanyard, keys, car fob, ring light. <b>Front, side and back</b> of each.', '—', ai='Genjutsu references (up to 30)'),
         shot('J-A', 'Greetings (idea J)', 'Tripod = 01-A framing', 'Whole team waves to camera. Do one take per greeting.', '1 each',
              say='“Merry Christmas from all of us at RKN!” · “Eid Mubarak!” · “Happy Diwali!” · “Happy New Year!”', ai='add snow/lights/lanterns'),
     ]),
    ])

L2 = location(
    2, 'Location 2 · about 45 min', 'Outside Millett House',
    'Ideas <b>03 · 06 · 11 · 12</b><br>Best in good daylight',
    ['Gimbal for walks; tripod for the building plate',
     'Use 50fps for every slow-motion walk',
     'Check permission with the building / landlord'],
    ['Watch for passers-by and car number plates in frame',
     'Keep the wind off the mic (use a dead-cat / windshield)',
     'Get release forms from anyone recognisable'],
    [shot_table([
        shot('03-G', 'Building plate', 'Tripod · wide of Millett House', '15 seconds locked, plus <b>3 still photos</b>.', '1', ai='Cinema Studio horror: stormy night'),
        shot('11-A', 'Millett Street sign', 'Close-up', 'Clean shot of the street sign.', '2'),
        shot('12-A', 'Team arriving', 'Wide → medium', 'Team walks up and goes in through the main door, coffees in hand.', '2'),
        shot('12-B', 'Door silhouette', 'From inside looking out', 'A team member steps into the doorway, backlit.', '2'),
        shot('12-C', 'Hero group slow-walk', 'Gimbal · 50fps · low angle', 'Whole team walks <b>toward</b> camera in a line, serious faces, then one smirks.', '3'),
        shot('11-B', 'Spotlight series opener', 'Medium · gimbal following', 'Presenter walks out of the door toward camera.', '3',
             say='“Every week we’re spotlighting a Bury business. Nominate one in the comments. Let’s go!”'),
        shot('11-C', 'Gold “Spotlight” transition', 'Close · tripod', 'Presenter spins toward the lens and fills the frame (used as a wipe).', '3'),
        shot('06-A', 'Market quiz intro', 'Medium · holding the prop bag', 'Presenter shakes the bag of random props, grinning.', '3',
             say='“We’re taking a bag of random stuff to Bury Market to find out: can you claim it on your taxes?”'),
    ]),
    ])

L3 = location(
    3, 'Location 3 · about 75 min', 'Desk & Office',
    'Ideas <b>02 · 15 · 03 · 12</b><br>Do the ASMR shots while the office is quiet',
    ['A clean desk with a black mat, gold pens and black folders',
     'Use <b>blank or fake receipts only</b>',
     'For 15 (ASMR): phones on silent, aircon off, mic 20–30cm from the sound',
     'For 03 (Halloween): blinds closed, overheads off, one practical lamp'],
    ['No real client names, figures or screens anywhere in shot',
     'Use a <b>plastic</b> mug for the Halloween drop',
     'Keep the tripod locked for the 02 plates (same framing for the start and end frames)'],
    [idea_sub('02', 'The Shoebox Exorcism', 'Receipts swirl into a golden tornado'),
     shot_table([
         shot('02-A', 'The slam', 'Wide two-shot', 'The “client” slams the overflowing shoebox on the desk.', '3', say='Client: “It’s all in there.”'),
         shot('02-B', 'Receipts spilling', 'Close-up', 'Receipts spill across the desk.', '3'),
         shot('02-C', 'Deadpan + knuckle crack', 'Close-up on the accountant', 'Calm stare, then a slow knuckle crack.', '3'),
         shot('02-D', 'Finger snap', 'Hand close-up', 'One crisp snap, recorded with the sound.', '3'),
         shot('02-E', 'Plate: desk WITH shoebox', 'Tripod locked', '5 seconds, no hands in frame.', '2', ai='Kling start frame'),
         shot('02-F', 'Plate: desk CLEAN', 'Same tripod framing as 02-E', 'A neat black folder with a gold tick in the same spot.', '2', ai='Kling end frame'),
         shot('02-G', 'Jaw drop', 'Close-up on the client', 'Shocked reaction.', '3'),
         shot('02-H', 'The payoff', 'Medium on the accountant', 'A small smile and slides the folder across.', '2', say='“Filed. Before the thirty-first.”'),
         shot('02-I', 'Practical throw', 'Wide · 50fps', 'Throw a handful of receipts in the air (we may reverse it).', '3'),
     ]),
     idea_sub('15', 'The Most Satisfying Sounds in Accountancy', 'Macro close-ups at 50fps, silent office'),
     shot_table([
         shot('15-A', 'Gold pen signature', 'Macro', 'A slow, confident signature.', '3'),
         shot('15-B', '“FILED” stamp', 'Macro · top-down', 'One firm stamp.', '3'),
         shot('15-C', 'Calculator tape', 'Macro', 'The tape printing out.', '3'),
         shot('15-D', 'Receipts squared up', 'Close · top-down', 'Tap a stack straight on the desk.', '3'),
         shot('15-E', 'Binder snaps shut', 'Close', 'Ring binder clicking shut.', '3'),
         shot('15-F', 'Stapler', 'Macro', 'One satisfying <i>chunk</i>.', '3'),
         shot('15-G', 'Laptop closing', 'Side angle', 'Lid closes gently.', '3'),
         shot('15-H', 'The Submit click', 'Macro on finger + key/trackpad', 'The final “Submit” press (dummy screen).', '3', ai='gold sparkle added'),
     ]),
     idea_sub('03', 'The Scariest Letter in Britain', 'Halloween horror parody · must post by 30 Oct'),
     shot_table([
         shot('03-A', 'Dark office + flicker', 'Tripod · wide', 'Flick the lamp switch on and off irregularly.', '3'),
         shot('03-B', 'Envelope slides in', 'Close · letterbox or under the door', 'A <b>plain brown envelope</b> slides in slowly. Pull it with fishing line, or pull it out and reverse.', '4'),
         shot('03-C', 'The scream', 'Close · 50fps', 'Team member screams and drops a <b>plastic</b> mug.', '3'),
         shot('03-D', 'Lights snap on', 'Tripod = 03-A framing', 'Overheads switched on suddenly.', '2'),
         shot('03-E', 'Calm reveal', 'Medium', 'Accountant strolls in and picks up the envelope, unbothered.', '3', say='“Relax. We filed yours in September.”'),
         shot('03-F', 'Empty dark plate', 'Tripod = 03-A framing', '10 seconds of the dark office, nobody in it.', '1', ai='Kling Omni Edit: fog + shadow hand'),
         shot('03-H', 'Whisper', 'Mic close to mouth', 'A creepy whisper, recorded on its own.', '3', say='“…self… assessment…”'),
     ]),
     idea_sub('12', 'RKN: The Movie (trailer B-roll)', 'Dramatic close-ups at 50fps'),
     shot_table([
         shot('12-D', 'Coffee pour', 'Close · 50fps', 'Slow, dramatic pour.', '2'),
         shot('12-E', 'Detail hits', 'Macro · 50fps', 'Pen click · stamp · Enter key · papers landing on the desk.', '2 each'),
         shot('12-F', 'Look up in unison', 'Wide', 'Whole team looks up from their screens at the same time.', '3'),
         shot('12-G', 'High-five + huddle', 'Medium', 'Team huddle, then a big high-five.', '2'),
         shot('12-H', 'The heroic SUBMIT', 'Close · 50fps', 'A finger slams “Submit”, then everyone exhales.', '3'),
     ]),
    ])

L4 = location(
    4, 'Location 4 · about 60 min', 'Talking-Head Set',
    'Ideas <b>04 · 05 · 08 · 09 · 10 · A–I</b><br>All lines are on the script pages',
    ['Branded background (logo wall or black and gold)',
     '2 framings: <b>medium</b> (chest up) and <b>close</b> (shoulders up)',
     'Vertical 9:16 with headroom for text at the top',
     'Lav mic on; record 10s of room tone'],
    ['Read lines from the <b>Script pages</b> (end of this guide)',
     'Short takes: one sentence at a time is fine',
     'Look straight into the lens and smile at the end of each line',
     'Every tax line has been checked by a qualified team member'],
    [shot_table([
        shot('04-A', 'Budget “BREAKING” walk-in', 'Medium · tripod', 'Presenter walks into frame and sits at the desk, urgent energy.', '3'),
        shot('04-B', 'Budget intro ×4 audiences', 'Medium + close', 'One take for each: self-employed, landlords, employers, families.', '2 each', say='See script 04'),
        shot('04-C', 'Budget outro', 'Medium', 'The close and CTA.', '2', say='See script 04'),
        shot('04-D', 'Budget B-roll', 'Close-ups', 'Calculator, typing, pound coins, a notebook titled “BUDGET 2026”.', '2 each'),
        shot('04-E', 'Reactions for re-use', 'Close', 'Shock · relief · thinking · a slow nod.', '2 each'),
        shot('05-A', 'Reaction library (15)', 'Close · 9:16 with headroom', 'Laugh · facepalm · head shake · slow blink · coffee spit-take · “absolutely not” finger wag · approving nod · jaw drop · eye roll · confused squint · “wait, what?” · slow clap · thumbs down · thumbs up · hands on head.', '1 each'),
        shot('05-B', 'MYTH / FACT verdicts', 'Medium at the desk', 'Hold up the MYTH paddle, then the FACT paddle.', '3 each', say='See script 05'),
        shot('08-A', 'Say vs Think: POLITE takes', 'Tripod · medium · natural', 'All 6 polite lines: friendly, on a “client call” with a headset or phone.', '2 each', say='See script 08'),
        shot('08-B', 'Say vs Think: THINKING takes', '<b>Identical framing</b> to 08-A', 'All 6 inner-voice lines: dramatic and over the top.', '2 each', say='See script 08', ai='Genjutsu Styles (cartoon)'),
        shot('09-A', 'MTD facts', 'Medium + close', '3 facts, each as a separate take.', '2 each', say='See script 09'),
        shot('10-A', 'Creator tax tips', 'Medium + close', '3 tips, each as a separate take.', '2 each', say='See script 10'),
        shot('A-A', 'Founder story', 'Medium · seated, relaxed', 'Answer the founder prompts naturally; 60–90 seconds is fine.', '1–2', say='See script A'),
        shot('B–I', 'Quick-fire tips', 'Medium', 'One take per quick-fire line.', '2 each', say='See script B–I'),
    ]),
    ])

L5 = location(
    5, 'Location 5 · about 60 min', 'Open Office',
    'Ideas <b>07 · 14 · 10 · 09 · 13</b><br>Team energy block: go after lunch',
    ['Gimbal + tripod; <b>50fps</b> for hero walks',
     'Plain wall area for full-body motion clips',
     'Ring light and PR-box set for 10; sofa set for 09',
     '<b>Signed AI-likeness consent</b> from each team member before filming them'],
    ['Full body must stay in frame for 14 motion clips (no cropping feet)',
     'Solid-colour clothes; no small checks or stripes',
     'For 13: <b>lock the tripod</b>, because before and after need identical framing',
     'Keep rolling between takes for bloopers (for the trailer, 12)'],
    [idea_sub('07', 'Meet the Team: Not Your Everyday Accountants', 'Repeat for every team member'),
     shot_table([
         shot('07-A', 'Hero walk', 'Gimbal · 50fps · low angle', 'Walk toward camera through the office, stop, smirk.', '3'),
         shot('07-B', 'Pose 1: arms crossed', 'Medium · tripod', 'Freeze for 3 seconds (becomes the trading-card frame).', '2', ai='Nano Banana Pro trading card'),
         shot('07-C', 'Pose 2: calculator spin', 'Medium', 'Spin the calculator like a gunslinger.', '2'),
         shot('07-D', 'Pose 3: pen click', 'Close', 'A confident pen click to camera.', '2'),
         shot('07-E', 'Fun fact', 'Close', 'One line to camera.', '2', say='See script 07'),
         shot('07-F', 'Reference stills', 'Photo · plain wall', 'Front, side and back, full body and face.', '—', ai='Genjutsu Motion Transfer'),
     ]),
     idea_sub('14', 'Trend Remix: Motion Library', 'Raw moves for future trends'),
     shot_table([
         shot('14-A', 'Walk-in', 'Full body · tripod', 'Confident walk into frame from the side.', '2'),
         shot('14-B', 'Spin', 'Full body', 'A slow 360 spin.', '2'),
         shot('14-C', 'Point at camera', 'Full body', 'Point and grin, “you!”.', '2'),
         shot('14-D', 'Fist-pump', 'Full body', 'Celebration (the “deadline met” moment).', '2'),
         shot('14-E', 'Lean back in chair', 'Medium-wide', 'Feet up, hands behind head, smug.', '2'),
         shot('14-F', 'Dramatic turn', 'Medium', 'Turns slowly toward camera, sunglasses on.', '2'),
         shot('14-G', 'Simple dance step', 'Full body', '4–15 seconds of an easy groove.', '2', ai='Genjutsu / Genjutsu Lite'),
     ]),
     idea_sub('10', 'Free PR Package? HMRC Calls That Income', 'Unboxing with an AI item swap'),
     shot_table([
         shot('10-A', 'Excited unboxing', 'Medium · ring light', '“Creator” opens a PR box with tissue paper, over-the-top excited.', '3', say='“Omg, thank you SO much!”'),
         shot('10-B', 'Hands lifting product', 'Close · tripod locked', '4–15 seconds: hands lift a generic product out of the box.', '3', ai='Genjutsu “Unboxed Item Swap”'),
         shot('10-C', 'Confused reaction', 'Close', 'Creator stares at the (soon-to-be) gold calculator.', '2'),
         shot('10-D', 'Accountant pops up', 'Medium', 'Accountant leans into frame next to the creator.', '2', say='“Lovely. Have you declared it?”'),
         shot('10-E', 'Prop references', 'Photo', 'Gold calculator / tax-form prop: front, side and top.', '—'),
     ]),
     idea_sub('09', 'The MTD Wake-Up Call (skit part)', 'Facts are filmed on the talking-head set'),
     shot_table([
         shot('09-B', 'Landlord asleep', 'Wide · sofa', 'Asleep among keys and paperwork.', '2'),
         shot('09-C', 'Alarm + phone', 'Close-ups', 'Alarm clock with a “7 NOV” note ringing · phone screen reading “Quarterly update due”.', '2 each'),
         shot('09-E', 'Jolt awake', 'Medium', 'A panicked wake-up.', '3'),
         shot('09-F', 'Empty spot plate', 'Tripod locked', '5 seconds of the spot where the accountant will appear.', '1', ai='Kling start frame'),
         shot('09-G', 'Accountant appears', 'Same tripod framing', 'Accountant steps in holding a phone, confident.', '3', say='“Quarterly update? Sorted.”', ai='Kling end frame'),
     ]),
     idea_sub('13', 'Client Glow-Up: Before & After', 'Locked tripod · match cut'),
     shot_table([
         shot('13-A', 'BEFORE', 'Tripod locked · desk', 'Messy piles of paper, head in hands, phone buzzing, stressed.', '3', ai='rain + grey light'),
         shot('13-B', 'AFTER', '<b>Identical</b> framing', 'Tidy desk, relaxed, smiling, coffee in hand.', '3', ai='warm golden light'),
         shot('13-C', 'Monthly catch-up', 'Medium · meeting room', 'Accountant and “client” reviewing a laptop, nodding, laughing.', '2'),
     ]),
    ])

L6 = location(
    6, 'Location 6 · about 60 min', 'Bury Town Centre & Market',
    'Ideas <b>06 · 11 · 12</b><br>Golden hour is best for the trailer shots',
    ['2 cameras (wide + close) and wireless lav mics for the quiz',
     'Branded gold mic flag and the prop bag',
     '<b>Release forms + pens</b>; prizes ready',
     'Check the market is open (outdoor market days vary)'],
    ['Ask stall-holders before filming their stalls',
     '<b>Avoid filming children</b>; ask adults before featuring them',
     'Keep answers to the agreed script (see the quiz answer sheet)'],
    [idea_sub('B-roll', 'Bury town B-roll', 'For Spotlight, the trailer and Budget videos'),
     shot_table([
         shot('BR-1', 'Bury Market stalls', 'Wide + details', 'Busy stalls, hands exchanging money (no faces needed).', '2'),
         shot('BR-2', 'Black pudding stall', 'Close-up', 'Product shot <b>with the stall-holder’s permission</b>.', '2'),
         shot('BR-3', 'Kay Gardens', 'Wide', 'Slow pan.', '1'),
         shot('BR-4', 'Robert Peel statue', 'Low angle', 'Hero angle against the sky.', '1'),
         shot('BR-5', 'The Rock', 'Wide', 'Shoppers and atmosphere.', '1'),
         shot('BR-6', 'East Lancashire Railway station', 'Wide', 'Steam or a train if one is running.', '1'),
         shot('BR-7', 'Town at golden hour', 'Wide · tripod', 'For the trailer’s establishing shot.', '1', ai='Cinema Studio 4.0'),
         shot('BR-8', 'Street time-lapse', 'Tripod · 30s+', 'People and traffic moving.', '1'),
     ]),
     idea_sub('06', '“Can I Claim It?” Bury Market quiz', 'Only if the market is busy today; otherwise book a market day'),
     shot_table([
         shot('06-B', 'Ask the question', 'Close on prop + person', 'Hold up each prop in turn.', '3–4 people per prop', say='“If you’re self-employed, can you claim this on your taxes?”'),
         shot('06-C', 'Guesses + reactions', 'Wide + close (2 cameras)', 'Let people talk; the funniest answers win.', '—'),
         shot('06-D', 'The verdict', 'Medium', 'Accountant gives the answer from the answer sheet.', '1 per prop'),
         shot('06-E', 'Prize moment', 'Medium', 'Hand over the prize, applause.', '2'),
         shot('06-F', 'Tease next week', 'Close', 'Presenter to camera.', '2', say='“Next week’s prop is… you’ll have to follow to find out.”'),
     ]),
    ])

# ---------------------------------------------------------------- SCRIPTS
def script(code, title, body):
    return f'<div class="script"><div class="h"><span class="code">{code}</span><span class="t">{title}</span></div>{body}</div>'


def lines(*ls):
    return ''.join(f'<p class="ln">{l}</p>' for l in ls)


S = []
S.append(script('01', 'Door to Every Business: welcome line', lines('Morning! Come on in.', 'Welcome to RKN. Tea or coffee?')))
S.append(script('02', 'Shoebox Exorcism', '<p><b>Client:</b> <span class="ln">It’s all in there.</span></p><p><b>Accountant</b> (after the snap): <span class="ln">Filed. Before the thirty-first.</span></p>'))
S.append(script('03', 'Scariest Letter in Britain', '<p><b>Whisper:</b> <span class="ln">…self… assessment…</span></p><p><b>Accountant:</b> <span class="ln">Relax. We filed yours in September.</span></p>'))
S.append(script('04', 'Budget Day in 60 Seconds (template)',
                '<p><b>Intro</b> (one per audience: self-employed / landlord / employer / family):</p>'
                + lines('The Budget’s just been announced. Here’s what it means for you if you’re [self-employed]. Three things, sixty seconds.')
                + '<p><b>Outro:</b></p>' + lines('That’s the Budget in sixty seconds. Got a question? Drop it in the comments and we’ll answer it in a video. RKN: not your everyday accountant.')
                + '<p class="small">On Budget day (Wed 28 Oct), record only the 3 points, after a qualified team member has checked them against the official documents.</p>'))
S.append(script('05', 'Accountant Reacts', lines('Absolutely not.', 'Please, please don’t do this.', 'Here’s the truth in fifteen seconds…', 'HMRC risk level: three flames.', 'That one’s actually true. Fact!', 'Want part two? Comment the next one you’ve seen.')))
S.append(script('07', 'Meet the Team: fun-fact prompts',
                '<p>Each person picks one and says it to camera in one line:</p>'
                + lines('My superpower? I can spot a missed expense from ten metres away.', 'My kryptonite? “I’ll send the receipts tomorrow.”', 'My favourite thing about Bury is…', 'My most-used Excel shortcut is…')))
S.append(script('08', 'What I Say vs What I’m Thinking',
                '<div class="pair"><div class="hd">Polite take (08-A)</div><div class="hd">Thinking take (08-B)</div>'
                + ''.join(f'<div class="p">“{a}”</div><div class="th">“{b}”</div>' for a, b in [
                    ('Oh, you’ve got a few receipts? No problem!', 'It’s a bin bag, Dave.'),
                    ('You bought a boat… for the business? Interesting!', 'What business needs a BOAT?!'),
                    ('Of course we can look at your 2019 records!', 'Why are we in 2019?!'),
                    ('VAT isn’t optional, I’m afraid.', 'It was NEVER optional.'),
                    ('Yes, the deadline is the same every year.', 'Thirty-first of January. Every. Single. Year.'),
                    ('Sure, send it over as a voice note!', 'A voice note… of a spreadsheet.'),
                ]) + '</div>'))
S.append(script('09', 'MTD Wake-Up Call: three facts', lines(
    'Making Tax Digital started this April for self-employed people and landlords with income over fifty thousand pounds.',
    'It means sending HMRC a quarterly update every three months, and the next one’s due on the seventh of November.',
    'From April 2027 the threshold drops to thirty thousand. Not sure if it’s you? WhatsApp us and we’ll check.')))
S.append(script('10', 'Creator tax tips', lines(
    'If a brand sends you free stuff to promote, HMRC can treat it as income.',
    'There’s a thousand-pound trading allowance. Earn more than that from content and you’ll likely need to tell HMRC.',
    'Keep records of everything: every platform, every payment, every gift.')))
S.append(script('11', 'Spotlight opener', lines('Every week we’re spotlighting a Bury business. Nominate one in the comments. Let’s go!')))
S.append(script('12', 'Trailer narration (record now or add later)', lines(
    'In a town… where receipts go missing… and deadlines never sleep… one team… stands between you… and HMRC penalties.',
    'This January… RKN. Not your everyday accountant. Coming to a deadline near you.')))
S.append(script('A', 'Founder story prompts (answer naturally, 60–90s)',
                '<ul><li>Why did you start RKN?</li><li>Why Bury?</li><li>A moment a client made you proud.</li><li>What do you wish every business owner knew?</li><li>What does “not your everyday accountant” mean to you?</li></ul>'))
S.append(script('B–I', 'Quick-fire tips (one take each)', lines(
    '<b>C · Rate my expense:</b> Home office? Eight out of ten, with conditions.',
    '<b>D · Christmas party:</b> Your staff Christmas party can be tax-free: up to a hundred and fifty pounds a head, per year, if it’s open to all staff.',
    '<b>E · Staff gifts:</b> A Christmas gift for your team can be tax-free, up to fifty pounds each, as long as it’s not cash and not a reward for work.',
    '<b>F · Countdown intro:</b> Thirty-one days to the thirty-first of January. Today’s tip…',
    '<b>G · Jargon:</b> UTR? That’s your Unique Taxpayer Reference. Ten digits. Don’t lose it.',
    '<b>H · Penalty:</b> How much is the fine for filing your tax return late? A hundred pounds, even if you owe nothing.',
    '<b>I · Sector Saturday:</b> It’s Sector Saturday, and this one’s for [builders]…')
    + '<p class="small"><b>B</b> (reply-to-comment) has no fixed script; record later as questions come in.</p>'))

# ---------------------------------------------------------------- QUIZ ANSWERS
QUIZ = [
    ('Safety boots / protective clothing (builder)', '✅ Generally yes', 'Protective clothing or a uniform needed for the job is allowable.'),
    ('A smart suit for meetings', '❌ No', 'Everyday clothing isn’t allowable, even if you only wear it for work.'),
    ('Van fuel', '✅ Yes, for business journeys', 'Business mileage only, not personal trips. Or use the simplified mileage rate instead.'),
    ('Mobile phone', '✅ Partly', 'The business-use portion is allowable.'),
    ('Gym membership', '❌ No', 'Personal expense.'),
    ('Netflix subscription', '❌ Generally no', 'Personal entertainment.'),
    ('Black pudding (your lunch)', '❌ No…', '…but ✅ <b>yes if you run a café</b> and it’s stock you sell! (Great twist.)'),
    ('Dog lead (pet)', '❌ No', 'Personal.'),
]
quiz_rows = ''.join(f'<tr><td class="ck"></td><td><b>{a}</b></td><td><b>{b}</b></td><td>{c}</td></tr>' for a, b, c in QUIZ)

# ---------------------------------------------------------------- GLANCE
GLANCE = [
    ('01', 'The Door to Every Business in Bury', 'Empty reception fills with Bury’s businesses (AI)', 'Reception', '★'),
    ('02', 'The Shoebox Exorcism', 'Shoebox of receipts becomes a golden tornado', 'Desk', '★'),
    ('03', 'The Scariest Letter in Britain', 'Halloween horror parody: the brown envelope', 'Desk · Outside', '★ post by 30 Oct'),
    ('04', 'Budget Day in 60 Seconds', 'Intros, outros and B-roll now; facts on 28 Oct', 'Talking head', '★'),
    ('05', 'Accountant Reacts', 'Reaction library for stitching bad tax advice', 'Talking head', '★'),
    ('06', '“Can I Claim It?” Market quiz', 'Street quiz with props at Bury Market', 'Outside · Market', 'Market day'),
    ('07', 'Meet the Team', 'Hero walks into trading cards', 'Open office', '★'),
    ('08', 'What I Say vs What I’m Thinking', 'Polite line vs cartoon inner voice', 'Talking head', '★'),
    ('09', 'MTD Wake-Up Call', 'Landlord skit + 3 facts (due 7 Nov)', 'Open office · Talking head', '★'),
    ('10', 'Free PR Package?', 'Unboxing swap: creator tax tips', 'Open office · Talking head', '★'),
    ('11', 'Bury Business Spotlight', 'Series opener + town B-roll', 'Outside · Town', 'Opener today'),
    ('12', 'RKN: The Movie', 'Day-in-the-life as an epic trailer', 'Outside · Office · Town', '★'),
    ('13', 'Client Glow-Up', 'Before/after match cut (dramatisation)', 'Open office', 'If time'),
    ('14', 'Trend Remix', 'Motion library for future trends', 'Open office', '★'),
    ('15', 'Satisfying Sounds', 'ASMR macro close-ups', 'Desk (silent)', '★'),
]
glance_rows = ''.join(f'<tr><td><b>{a}</b></td><td><b>{b}</b></td><td>{c}</td><td>{d}</td><td>{"<span class=\"tag star\">" + e + "</span>" if e.startswith("★") else "<span class=\"tag\">" + e + "</span>"}</td></tr>' for a, b, c, d, e in GLANCE)

# ---------------------------------------------------------------- PAGE
page = f'''<!doctype html>
<html lang="en-GB"><head><meta charset="utf-8"><title>RKN Accountancy – On-Set Shooting Guide</title>
<link rel="stylesheet" href="guide.css"></head><body>

<div>
  <div class="sec-head"><div class="t"><div class="eyebrow">Read this before you press record</div><h2>Before You Roll</h2></div></div>
  <div class="big3">
    <div class="tile gold"><div class="k">6 locations</div><div class="v">Shoot by location, not by idea. It saves hours of resetting.</div></div>
    <div class="tile gold"><div class="k">100+ shots</div><div class="v">Tick each box as you go. Shot codes match the idea numbers.</div></div>
    <div class="tile gold"><div class="k">25+ posts</div><div class="v">Enough footage for 8–10 weeks of content.</div></div>
  </div>

  <div class="rule-box"><span class="lbl">The golden rule for AI shots</span>
    <p style="margin-bottom:1.4mm">Anywhere we’ll add people or props with Higgsfield, film it <b>three ways</b>:</p>
    <ol>
      <li><b>Clean plate:</b> 10–15 seconds of the empty space, tripod <b>locked</b>, nobody walking through.</li>
      <li><b>Stand-in take:</b> the <b>same framing</b> with a team member doing the action. Genjutsu swaps what’s already in the shot, so it needs something to swap.</li>
      <li><b>Moving version:</b> a slow gimbal push-in of the empty space (for the Seedance / Kling video-edit models).</li>
    </ol>
    <p style="margin:1.4mm 0 0">Then take <b>reference photos</b> of every person and prop: front, side and back.</p>
  </div>

  <div class="grid2">
    <div class="tile"><h5>Camera settings</h5><ul class="check">
      <li>Vertical <b>9:16</b>, 4K, <b>25fps</b> (UK standard)</li>
      <li>Slow motion: <b>50fps</b> indoors (avoids light flicker on UK 50Hz mains)</li>
      <li>Shutter 1/50 at 25fps, 1/100 at 50fps</li>
      <li>Lock exposure, focus and white balance for every tripod shot</li>
      <li>Second camera (if you have one): horizontal 16:9 for YouTube and the website</li>
    </ul></div>
    <div class="tile"><h5>Sound</h5><ul class="check">
      <li>Lav mic on whoever is speaking</li>
      <li>Phone as a backup recorder</li>
      <li>30 seconds of room tone in every location</li>
      <li>Clap at the start of each take if using two cameras</li>
      <li>Phones on silent; aircon off for ASMR</li>
    </ul></div>
    <div class="tile"><h5>GDPR sweep (every location)</h5><ul class="check">
      <li>No client files, names or figures in shot</li>
      <li>Screens off or showing dummy data</li>
      <li>Whiteboards wiped; post and visitor book hidden</li>
      <li>Fake or blank receipts only</li>
    </ul></div>
    <div class="tile"><h5>Permissions</h5><ul class="check">
      <li>Release form from <b>everyone</b> filmed, staff included</li>
      <li>Consent for AI use of their likeness (07, 14)</li>
      <li>Client consent before any real client appears</li>
      <li>Building/landlord OK; stall-holders at the market</li>
      <li>No children in public shots</li>
    </ul></div>
  </div>
  <div class="callout"><span class="lbl">Wardrobe</span><p>Black, white, cream and gold tones. <b>Solid colours</b> only, with no small checks, stripes or logos (they flicker in AI). Bring one smart look and one “character” look each.</p></div>
</div>

<div class="section">
  <div class="sec-head"><div class="t"><div class="eyebrow">What we’re making today</div><h2>The 15 Ideas at a Glance</h2></div></div>
  <table class="glance compact"><thead><tr><th style="width:6%">#</th><th style="width:27%">Idea</th><th style="width:35%">In one line</th><th style="width:18%">Where</th><th>Priority</th></tr></thead><tbody>{glance_rows}</tbody></table>

  <h3>Shoot order <span class="g">(short on time? do every ★ first)</span></h3>
  <table class="compact"><thead><tr><th style="width:9%">Order</th><th style="width:26%">Location</th><th style="width:12%">Time</th><th>Ideas</th></tr></thead><tbody>
    <tr><td><b>0</b></td><td><b>Prep + GDPR sweep</b></td><td>30 min</td><td>Lights, props, mics, release forms</td></tr>
    <tr><td><b>1</b></td><td><b>Reception</b></td><td>60 min</td><td>01 · J</td></tr>
    <tr><td><b>2</b></td><td><b>Outside Millett House</b></td><td>45 min</td><td>03 · 06 · 11 · 12</td></tr>
    <tr><td><b>3</b></td><td><b>Desk &amp; Office</b></td><td>75 min</td><td>02 · 15 · 03 · 12 &nbsp;→&nbsp; <b>then lunch: back up all cards to 2 drives</b></td></tr>
    <tr><td><b>4</b></td><td><b>Talking-Head Set</b></td><td>60 min</td><td>04 · 05 · 08 · 09 · 10 · A–I</td></tr>
    <tr><td><b>5</b></td><td><b>Open Office</b></td><td>60 min</td><td>07 · 14 · 10 · 09 · 13</td></tr>
    <tr><td><b>6</b></td><td><b>Bury Town Centre &amp; Market</b></td><td>60 min</td><td>06 · 11 · 12 (golden hour)</td></tr>
  </tbody></table>
</div>

{L1}
{L2}
{L3}
{L4}
{L5}
{L6}

<div class="section">
  <div class="sec-head"><div class="t"><div class="eyebrow">For the presenter: read from here</div><h2>Script Pages</h2></div></div>
  <p class="small">Lines are written to be said naturally; rephrase in your own words if it feels stiff. Every tax line should be checked by a qualified team member before posting.</p>
  {''.join(S)}
</div>

<div class="section">
  <div class="sec-head"><div class="t"><div class="eyebrow">Idea 06 · Agreed answers</div><h2>Market Quiz Answer Sheet</h2></div></div>
  <p>Agree these with a qualified team member <b>before</b> going to the market. Keep the verdict short on camera; explain any “it depends” in the caption.</p>
  <table class="shots"><thead><tr><th></th><th>Prop</th><th>Verdict</th><th>One-line reason (say this)</th></tr></thead><tbody>{quiz_rows}</tbody></table>
  <p class="small">General guidance for self-employed sole traders; individual circumstances vary. Confirm on GOV.UK before posting.</p>

  <h3>Props &amp; kit checklist</h3>
  <div class="grid2 tight">
    <ul class="check">
      <li>Battered shoebox + 200 blank/fake receipts</li>
      <li>Plain brown envelopes (no HMRC logo)</li>
      <li>Gold pens, black folders, ring binder, stapler</li>
      <li>“FILED” stamp + ink pad, calculator with tape</li>
      <li>Gold calculator (for 10) + a neat black folder with a gold tick (02)</li>
      <li>MYTH / FACT paddles (black + gold)</li>
      <li>Hi-vis vest, hard hat, chef whites, lanyard, keys, car fob</li>
      <li>Ring light, PR-style box + tissue paper, generic product</li>
      <li>Alarm clock + “7 NOV” note, wall clock</li>
      <li>Notebook titled “BUDGET 2026”, pound coins</li>
      <li>Plastic mug, desk lamp, fishing line</li>
      <li>Sunglasses, coffee cups, headset/phone</li>
    </ul>
    <ul class="check">
      <li>2 cameras/phones + 2 tripods</li>
      <li>Gimbal</li>
      <li>2 wireless lav mics + windshields</li>
      <li>2 soft LED lights</li>
      <li>Spare batteries, memory cards, power bank</li>
      <li>2 backup drives / laptop</li>
      <li>Market: gold mic flag, prop bag, prizes</li>
      <li>Release forms + pens + clipboard</li>
      <li>Gaffer tape, clamps, extension lead</li>
      <li>Lint roller, mirror, water, snacks</li>
    </ul>
  </div>

  <div class="rule-box"><span class="lbl">End-of-day wrap</span>
    <ul class="check" style="color:#e9e6df">
      <li>Final shot: lights off at 5:30pm, door closes (12)</li>
      <li>Back up every card to <b>2 places</b> before formatting anything</li>
      <li>Make one folder per idea (01–15, A–J) and drop the best takes in</li>
      <li>Collect and photograph all signed release forms</li>
      <li>Note any missed shots for a pickup day (market quiz, extra Spotlight businesses)</li>
      <li>Post a behind-the-scenes Story tonight 🎬</li>
    </ul>
  </div>
</div>

</body></html>'''

open(os.path.join(OUT, 'guide.html'), 'w').write(page)

cover = '''<!doctype html>
<html lang="en-GB"><head><meta charset="utf-8"><title>RKN Accountancy – On-Set Shooting Guide</title>
<link rel="stylesheet" href="style.css"></head>
<body>
<div class="cover">
  <div class="frame"></div>
  <img class="logo" src="logo.png" alt="RKN Accountancy logo">
  <div class="kicker">On-set shooting guide</div>
  <h1>Shot Lists for <span class="g">Shoot Day</span></h1>
  <div class="rule"></div>
  <div class="sub">Every shot for the 15 video ideas, in the order you’ll film them, with framing, lines to say and tick boxes</div>
  <div class="chips">
    <span>Before you roll</span><span>6 locations</span><span>Shot lists</span><span>Script pages</span><span>Quiz answers</span><span>Props &amp; wrap</span>
  </div>
  <div class="meta">
    <b>RKN Accountancy Ltd</b> · Millett House, Millett Street, Bury BL9 0JA<br>
    Shoot day: 21 October 2026<br>
    Use alongside the full Video Content Strategy PDF
  </div>
</div>
</body></html>'''
open(os.path.join(OUT, 'guide_cover.html'), 'w').write(cover)
print('written')
