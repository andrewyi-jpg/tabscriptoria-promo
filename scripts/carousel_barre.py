"""Carousel: 'F barre buzzing? 4 fixes.' (E-shape barre chord fingering tips + drill + CTA).

Usage: python3 carousel_barre.py OUT_DIR
Chord boxes are vertical: low E on the left, high e on the right; finger numbers in the dots.
"""
import os, sys
from PIL import ImageDraw
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from tslib import *

out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, 'out', 'barre')
os.makedirs(out, exist_ok=True)

def eshape(f):
    """E-shape major barre at fret f: (string low E..high e, fret, finger)."""
    return [(0, f, 1), (1, f + 2, 3), (2, f + 2, 4), (3, f + 1, 2), (4, f, 1), (5, f, 1)]

def chord_box(d, x, y, base, notes, w=480, h=480, label=None, r=34, hl=None, warn=None, pad_l=130, pad_r=70, lf=52):
    """base = fret shown at the top row. hl: set of string indexes to ring (mint outline); warn: strings in rose."""
    gx = w / 5; gy = h / 4
    d.rounded_rectangle((x - pad_l, y - 120, x + w + pad_r, y + h + 50), 32, fill=SURF + (240,), outline=BORDER2 + (255,), width=3)
    if label:
        d.text((x + w / 2 - text_w(DB(lf), label) / 2, y - 100), label, font=DB(lf), fill=TEXT)
    for s in range(6):
        d.line((x + s * gx, y, x + s * gx, y + h), fill=TEXT3 + (255,), width=3 + (5 - s) // 2)
    for k in range(5):
        d.line((x, y + k * gy, x + w, y + k * gy), fill=(TEXT if (k == 0 and base == 1) else BORDER2) + (255,),
               width=12 if (k == 0 and base == 1) else 4)
    if pad_l >= 100: d.text((x - pad_l + 12, y + gy / 2 - 20), f'{base}fr', font=SB(30), fill=TEXT3)
    barre = [s for s, fr, fi in notes if fi == 1]
    if len(barre) > 1:
        cy = y + 0.5 * gy
        d.rounded_rectangle((x + min(barre) * gx - 30, cy - r, x + max(barre) * gx + r, cy + r), r, fill=MINT)
    for s, fr, fi in notes:
        cx = x + s * gx; cy = y + (fr - base + 0.5) * gy
        col = ROSE if (warn and s in warn) else MINT
        d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=col)
        d.text((cx - text_w(B(32), str(fi)) / 2, cy - 19), str(fi), font=B(32), fill=BG)
        if hl and s in hl:
            d.ellipse((cx - r - 10, cy - r - 10, cx + r + 10, cy + r + 10), outline=TEXT, width=4)
    return y + h + 60

def header(d, step=None):
    if step:
        pill(d, (64, 170), f'FIX {step}', B(32), MINT, BG, pad=(20, 9))
        d.text((64 + text_w(B(32), f'FIX {step}') + 58, 180), 'of 4', font=SB(32), fill=TEXT3)
    else:
        tag(d, (64, 170), 'BARRE CHORDS  ·  SAVE THIS')

def body(d, y, text, col=TEXT2, size=42):
    return draw_lines(d, (64, y), wrap(M(size), text, 860), M(size), col, lh=int(size * 1.34), shadow=False)

def bullets(d, y, rows, size=46):
    for txt in rows:
        d.ellipse((64, y + 14, 84, y + 34), fill=AMBER)
        y = draw_lines(d, (110, y), wrap(SB(size), txt, 820), SB(size), TEXT, lh=int(size * 1.3), shadow=False) + 14
    return y

slides = []

# 1 - hook
img = background(91, glow=ROSE, glow2=ACCENT); d = ImageDraw.Draw(img, 'RGBA')
header(d)
y = draw_lines(d, (64, 255), ['F barre buzzing?', ('4 fixes.', ROSE)], XB(104), TEXT, lh=114)
y = body(d, y + 16, 'Most buzz is not weak fingers. It is where your thumb, index and arm are. Fix them in this order.')
chord_box(d, 330, y + 160, 1, eshape(1), label='F  (E-shape, 1st fret)')
d.text((64, 1400), 'Swipe for the fixes  →', font=SB(38), fill=MINT)
slides.append(img)

# 2 - thumb + arm
img = background(92, glow=AMBER, glow2=BLUE); d = ImageDraw.Draw(img, 'RGBA')
header(d, 1)
y = draw_lines(d, (64, 255), ['Stop squeezing.', ('Pull with your arm.', AMBER)], XB(88), TEXT, lh=100)
y = bullets(d, y + 30, ['Thumb low on the back of the neck, behind your middle finger.',
                        'Let the weight of your arm pull the neck back toward you.',
                        'Test: take your thumb off. If the chord still rings, you have it.'])
y += 40
d.rounded_rectangle((64, y, 940, y + 200), 30, fill=SURF + (240,), outline=AMBER + (220,), width=3)
d.text((104, y + 30), 'Squeeze harder?', font=DB(50), fill=ROSE)
d.text((104, y + 110), 'Hand tires in 30 s. Still buzzes.', font=SB(40), fill=TEXT2)
slides.append(img)

# 3 - index placement
img = background(93, glow=MINT, glow2=ACCENT); d = ImageDraw.Draw(img, 'RGBA')
header(d, 2)
y = draw_lines(d, (64, 255), ['Roll the index', ('onto its side.', MINT)], XB(92), TEXT, lh=104)
y = bullets(d, y + 30, ['Roll it slightly toward the headstock, onto the harder bony edge.',
                        'Sit it right behind the fret wire, not in the middle of the fret.',
                        'Creases in your finger mute strings. Slide up or down a few mm to dodge them.'])
chord_box(d, 330, y + 150, 1, eshape(1), label='Index = the bar', hl={0, 4, 5})
slides.append(img)

# 4 - string-by-string check
img = background(94, glow=BLUE, glow2=ROSE); d = ImageDraw.Draw(img, 'RGBA')
header(d, 3)
y = draw_lines(d, (64, 255), ['Pick one string', ('at a time.', BLUE)], XB(92), TEXT, lh=104)
y = body(d, y + 16, 'The buzzing string tells you which finger to fix. Most common culprit in red:')
yb = chord_box(d, 330, y + 160, 1, eshape(1), label='F', warn={4})
bullets(d, yb + 30, ['B string: index crease. Slide index a few mm.', 'D or G dead: arch fingers 2-4, tips straight down.'], size=40)
slides.append(img)

# 5 - start higher
img = background(95, glow=ACCENT, glow2=AMBER); d = ImageDraw.Draw(img, 'RGBA')
header(d, 4)
y = draw_lines(d, (64, 255), ['Start at fret 5,', ('then walk down.', ACCENT2)], XB(88), TEXT, lh=100)
y = body(d, y + 16, 'Strings are lower and frets closer up the neck. Same shape, less effort. Move down one fret a day.')
y += 40
row = [('A', 5, 'Day 1'), ('G', 3, 'Day 3'), ('F', 1, 'Day 5')]
for i, (nm, fr, day) in enumerate(row):
    chord_box(d, 134 + i * 308, y + 130, fr, eshape(fr), w=170, h=240, label=nm, r=16, pad_l=70, pad_r=30, lf=60)
for i, (nm, fr, day) in enumerate(row):
    x = 64 + i * 308
    d.text((x + 20, y + 460), f'fret {fr}', font=SB(34), fill=MINT if i == 0 else TEXT2)
    d.text((x + 20, y + 506), day, font=SB(30), fill=TEXT3)
slides.append(img)

# 6 - drill + CTA
img = background(96, glow=ACCENT, glow2=MINT); d = ImageDraw.Draw(img, 'RGBA')
tag(d, (64, 170), 'TRY IT  ·  60 SEC')
y = draw_lines(d, (64, 255), ['Place. Pick 6.', ('Let go. 10 times.', MINT)], XB(86), TEXT, lh=98)
y = body(d, y + 20, 'Place the shape, pick each string slowly, fully relax your hand, repeat. Speed comes from relaxing, not pressing.')
y += 50
d.rounded_rectangle((64, y, 940, y + 230), 30, fill=SURF + (240,), outline=ACCENT + (200,), width=3)
d.text((104, y + 24), 'Record your playing, get tab', font=DB(44), fill=TEXT)
d.text((104, y + 80), 'with chords + fingerings', font=DB(44), fill=TEXT)
d.text((104, y + 140), 'tabscriptoria.com', font=XB(64), fill=MINT)
print('cta bottom', y + 230)
slides.append(img)

for i, im in enumerate(slides, 1):
    save_slide(im, os.path.join(out, f'slide{i}.jpg'))
print('wrote', len(slides), 'slides to', out)
