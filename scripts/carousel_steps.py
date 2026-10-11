"""Carousel: '4 steps to solo over any chords' built from Tab Scriptoria Solo ideas practice steps.

Usage: python3 carousel_steps.py OUT_DIR
"""
import json, os, sys
from PIL import Image, ImageDraw
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from tslib import *

out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, 'out', 'steps')
os.makedirs(out, exist_ok=True)
data = json.load(open(os.path.join(ROOT, 'data', 'steps_AmFCG.json')))
BAR = data['bar']
CH = [(i * BAR, c) for i, c in enumerate(data['chords'])]
BARS = [i * BAR for i in range(5)]
L = data['levels']

X0, X1 = 70, 930          # tab row extents (right edge clear of TikTok's action rail)

def header(d, step=None, total=4):
    if step:
        pill(d, (64, 170), f'STEP {step}', B(32), MINT, BG, pad=(20, 9))
        d.text((64 + text_w(B(32), f'STEP {step}') + 58, 180), f'of {total}', font=SB(32), fill=TEXT3)
    else:
        tag(d, (64, 170), 'GUITAR IMPROV  ·  SAVE THIS')

def title_block(d, y, title_lines, body, title_size=86):
    y = draw_lines(d, (64, y), title_lines, XB(title_size), TEXT, lh=int(title_size * 1.08))
    y += 18
    y = draw_lines(d, (64, y), wrap(M(42), body, 860), M(42), TEXT2, lh=56, shadow=False)
    return y

def footer(d, y=1470):
    d.text((64, y), 'Am F C G  ·  from Tab Scriptoria  ·  Solo ideas', font=SB(30), fill=TEXT3)

def two_rows(img, y, notes, labels=None, roles=None, bar_labels=None):
    d = ImageDraw.Draw(img, 'RGBA')
    for r in range(2):
        t0, t1 = BARS[r * 2], BARS[r * 2 + 2]
        idx = [i for i, n in enumerate(notes) if t0 - 0.02 <= n[0] < t1 - 0.02]
        nn = [notes[i] for i in idx]
        lab = [labels[i] for i in idx] if labels else None
        rol = [roles[i] for i in idx] if roles else None
        y_end = draw_tab_row(img, (X0, y, X1, 0), nn, t0, t1, BARS, CH, labels=lab, roles=rol)
        if bar_labels:
            for b in range(2):
                txt = bar_labels[r * 2 + b]
                bx = X0 + 60 + (b * BAR) / (2 * BAR) * (X1 - X0 - 80) + 110
                d.text((bx, y + 10), txt, font=SB(28), fill=AMBER)
        y = y_end + 34
    return y

slides = []

# 1 - hook
img = background(1); d = ImageDraw.Draw(img, 'RGBA')
header(d)
y = draw_lines(d, (64, 260), ["Can't solo", "over chords?"], XB(110), TEXT, lh=118)
y = draw_lines(d, (64, y + 6), [("Do these 4 steps", MINT), ("in this order.", MINT)], XB(96), MINT, lh=104)
y += 26
y = draw_lines(d, (64, y), wrap(M(42), 'Works over any progression. Here it is over Am  F  C  G, the four chords in a thousand songs.', 860), M(42), TEXT2, lh=56, shadow=False)
# neck diagram: frets 4-8, the four chord roots used in step 1
ny0 = y + 120; nx0, nx1 = 100, 900
frets = [4, 5, 6, 7, 8]
gap = 62
d.rounded_rectangle((nx0 - 30, ny0 - 40, nx1 + 30, ny0 + 5 * gap + 80), 26, fill=BG2 + (235,), outline=BORDER + (255,), width=2)
fx = lambda f: nx0 + (f - 4) * (nx1 - nx0) / 4
for f in frets:
    d.line((fx(f), ny0, fx(f), ny0 + 5 * gap), fill=TEXT3 + (220,), width=4 if f == 4 else 3)
for i in range(6):
    d.line((nx0, ny0 + i * gap, nx1, ny0 + i * gap), fill=BORDER2 + (255,), width=2 + i // 2)
for f in (5, 7):
    d.ellipse((fx(f) - (fx(5) - fx(4)) / 2 - 9, ny0 + 2.5 * gap - 9, fx(f) - (fx(5) - fx(4)) / 2 + 9, ny0 + 2.5 * gap + 9), fill=BORDER2)
for (st, fr, lab) in [(3, 7, 'Am'), (1, 6, 'F'), (2, 5, 'C'), (3, 5, 'G')]:
    cx = fx(fr) - (fx(5) - fx(4)) / 2; cy = ny0 + st * gap
    d.ellipse((cx - 40, cy - 40, cx + 40, cy + 40), fill=MINT)
    d.text((cx - text_w(B(32), lab) / 2, cy - 21), lab, font=B(32), fill=BG)
for f in (5, 6, 7):
    lab = str(f)
    d.text((fx(f) - (fx(5) - fx(4)) / 2 - text_w(SB(28), lab) / 2, ny0 + 5 * gap + 22), lab, font=SB(28), fill=TEXT3)
d.text((64, ny0 + 5 * gap + 120), 'Step 1 uses just these 4 notes.', font=SB(40), fill=TEXT)
d.text((64, ny0 + 5 * gap + 176), 'Swipe for steps 2, 3, 4  →', font=SB(40), fill=MINT)
slides.append(img)

# 2 - rhythm on one note
img = background(2); d = ImageDraw.Draw(img, 'RGBA'); header(d, 1)
y = title_block(d, 260, ['One note', 'per chord'], "Play only each chord's root. The rhythm is the idea, and leave space in every bar.")
two_rows(img, y + 50, L['rhythm']['notes'])
footer(d)
slides.append(img)

# 3 - guide tones
img = background(3); d = ImageDraw.Draw(img, 'RGBA'); header(d, 2)
y = title_block(d, 260, ['Land on', 'chord tones'], 'On beats 1 and 3, aim for the 3rd or 5th of the chord. They spell out each change.')
two_rows(img, y + 50, L['guide']['notes'], labels=L['guide']['labels'])
footer(d)
slides.append(img)

# 4 - targets + approach
img = background(4); d = ImageDraw.Draw(img, 'RGBA'); header(d, 3)
y = title_block(d, 260, ['Target +', 'approach'], 'Pick a chord tone for beat 1, then step into it from the note above on beat 4.')
fret_pill(d, 100, y + 34, 5, col=MINT, size=30, ring=TEXT); d.text((140, y + 14), 'target', font=SB(34), fill=TEXT2)
fret_pill(d, 330, y + 34, 7, col=AMBER, size=30, hollow=True); d.text((370, y + 14), 'approach', font=SB(34), fill=TEXT2)
two_rows(img, y + 100, L['approach']['notes'], roles=L['approach']['roles'])
footer(d)
slides.append(img)

# 5 - full idea
img = background(5); d = ImageDraw.Draw(img, 'RGBA'); header(d, 4)
y = title_block(d, 260, ['Motif, answer,', 'higher, end'], 'Play a short idea, answer it, repeat it higher, then finish on the root.')
two_rows(img, y + 50, L['idea']['notes'], bar_labels=['motif', 'answer', 'higher', 'ending'])
footer(d)
slides.append(img)

# 6 - CTA with the real app UI
img = background(6, glow=MINT, glow2=ACCENT); d = ImageDraw.Draw(img, 'RGBA')
tag(d, (64, 170), 'TAB SCRIPTORIA  ·  SOLO IDEAS')
y = draw_lines(d, (64, 255), ['Type any chords.'], XB(92), TEXT, lh=100)
y = draw_lines(d, (64, y), [('Get all 4 steps', MINT), ('+ a backing track.', MINT)], XB(92), MINT, lh=100)
ui = Image.open(os.path.join(ROOT, 'assets', 'ui', 'solo_form.jpg')).convert('RGB')
ui = ui.crop((0, 140, 540, 840)).resize((620, int(700 * 620 / 540)), Image.LANCZOS)
rounded_paste(img, ui, ((W - 620) // 2 - 40, y + 40), radius=30)
d = ImageDraw.Draw(img, 'RGBA')
yb = y + 40 + ui.height + 44
d.text((64, yb), 'tabscriptoria.com', font=XB(64), fill=TEXT)
d.text((64, yb + 80), '8 styles: blues, jazz, flamenco, metal…', font=M(38), fill=TEXT2)
slides.append(img)

for i, im in enumerate(slides, 1):
    save_slide(im, os.path.join(out, f'slide{i}.jpg'))
print('wrote', len(slides), 'slides to', out)
