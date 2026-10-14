"""Carousel: 'Find any note on the neck in 4 steps' (natural notes on E/A, octave shapes, B-string shift).

Usage: python3 carousel_notes.py OUT_DIR
Fretboard drawn tab-style: top line = high e, bottom = low E. Frets 0-12, uniform spacing for readability.
"""
import os, sys
from PIL import ImageDraw
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from tslib import *

out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, 'out', 'notes')
os.makedirs(out, exist_ok=True)

FX0, FX1 = 172, 930   # nut x .. fret 12 x
def fx(f):            # center x of a fret position (0 = open, left of nut)
    if f == 0:
        return FX0 - 38
    step = (FX1 - FX0) / 12
    return FX0 + (f - 0.5) * step

def neck(img, y, dots, gap=96, strings_on=None, arrows=()):
    """dots: list of (string 0=high e..5=low E, fret, label, color). arrows: list of ((s,f),(s,f),color)."""
    d = ImageDraw.Draw(img, 'RGBA')
    top, bot = y + 40, y + 40 + 5 * gap
    d.rounded_rectangle((64, y - 10, 950, bot + 100), 28, fill=BG2 + (240,), outline=BORDER + (255,), width=2)
    # inlays
    for f in (3, 5, 7, 9):
        cx = fx(f); d.ellipse((cx - 9, (top + bot) / 2 - 9, cx + 9, (top + bot) / 2 + 9), fill=BORDER2 + (255,))
    cx = fx(12)
    for dy in (-gap, gap):
        d.ellipse((cx - 9, (top + bot) / 2 + dy - 9, cx + 9, (top + bot) / 2 + dy + 9), fill=BORDER2 + (255,))
    # frets
    step = (FX1 - FX0) / 12
    for k in range(13):
        x = FX0 + k * step
        d.line((x, top, x, bot), fill=(TEXT2 if k == 0 else BORDER2) + (255,), width=8 if k == 0 else 3)
    for i, nm in enumerate(STRINGS):
        yy = top + i * gap
        lit = strings_on is None or i in strings_on
        d.line((FX0 - 70, yy, FX1, yy), fill=(TEXT3 if lit else BORDER) + (255,), width=3 if lit else 2)
        d.text((74, yy - 16), nm, font=M(28), fill=TEXT3 if lit else BORDER2)
    for f in (3, 5, 7, 9, 12):
        d.text((fx(f) - text_w(SB(26), str(f)) / 2, bot + 34), str(f), font=SB(26), fill=TEXT3)
    for (s1, f1), (s2, f2), col in arrows:
        d.line((fx(f1), top + s1 * gap, fx(f2), top + s2 * gap), fill=col + (200,), width=6)
    for s, f, lab, col in dots:
        cx, cy = fx(f), top + s * gap
        r = 30
        d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=col)
        fo = B(30)
        d.text((cx - text_w(fo, lab) / 2, cy - 19), lab, font=fo, fill=BG)
    return bot + 100

def header(d, step=None):
    if step:
        pill(d, (64, 170), f'STEP {step}', B(32), MINT, BG, pad=(20, 9))
        d.text((64 + text_w(B(32), f'STEP {step}') + 58, 180), 'of 4', font=SB(32), fill=TEXT3)
    else:
        tag(d, (64, 170), 'FRETBOARD  ·  SAVE THIS')

def body(d, y, text, col=TEXT2, size=42):
    return draw_lines(d, (64, y), wrap(M(size), text, 860), M(size), col, lh=int(size * 1.34), shadow=False)

E_NAT = [(0, 'E'), (1, 'F'), (3, 'G'), (5, 'A'), (7, 'B'), (8, 'C'), (10, 'D'), (12, 'E')]
A_NAT = [(0, 'A'), (2, 'B'), (3, 'C'), (5, 'D'), (7, 'E'), (8, 'F'), (10, 'G'), (12, 'A')]

slides = []

# 1 - hook: every G in the first 12 frets
img = background(41, glow=BLUE, glow2=MINT); d = ImageDraw.Draw(img, 'RGBA')
header(d)
y = draw_lines(d, (64, 255), ['Find any note', ('on the neck.', MINT)], XB(112), TEXT, lh=120)
y = body(d, y + 20, 'You don\'t need to memorize every fret. Learn 2 strings and 2 shapes. Every G, found that way:')
dots = [(5, 3, 'G', MINT), (3, 5, 'G', MINT), (1, 8, 'G', MINT), (0, 3, 'G', MINT), (2, 12, 'G', MINT), (4, 10, 'G', MINT), (2, 0, 'G', MINT)]
y = neck(img, y + 40, dots)
d.text((64, y + 40), 'Swipe for the 4 steps  →', font=SB(38), fill=MINT)
slides.append(img)

# 2 - low E naturals
img = background(42); d = ImageDraw.Draw(img, 'RGBA')
header(d, 1)
y = draw_lines(d, (64, 255), ['Low E string first.'], XB(88), TEXT, lh=100)
y = body(d, y + 16, 'Natural notes are 2 frets apart, except B to C and E to F: those are 1 fret. Say each name out loud.')
y = neck(img, y + 40, [(5, f, n, AMBER if n in 'CF' else MINT) for f, n in E_NAT], strings_on={5})
d.text((64, y + 30), 'Amber = the 1-fret steps (B-C, E-F)', font=SB(34), fill=TEXT3)
slides.append(img)

# 3 - A string naturals
img = background(43); d = ImageDraw.Draw(img, 'RGBA')
header(d, 2)
y = draw_lines(d, (64, 255), ['Then the A string.'], XB(88), TEXT, lh=100)
y = body(d, y + 16, 'Same rule, new start. These two strings give you the root of almost every barre chord.')
y = neck(img, y + 40, [(4, f, n, AMBER if n in 'CF' else MINT) for f, n in A_NAT], strings_on={4})
d.text((64, y + 30), 'Sharps sit between: fret 1 = A#/Bb', font=SB(34), fill=TEXT3)
slides.append(img)

# 4 - octave shape
img = background(44, glow=MINT, glow2=ACCENT); d = ImageDraw.Draw(img, 'RGBA')
header(d, 3)
y = draw_lines(d, (64, 255), ['Skip 2 strings,', ('go up 2 frets.', MINT)], XB(88), TEXT, lh=100)
y = body(d, y + 16, 'That\'s the octave shape. G on low E fret 3 is also G on the D string, fret 5. C on A fret 3 is C on G fret 5.')
y = neck(img, y + 40, [(5, 3, 'G', MINT), (3, 5, 'G', MINT), (4, 3, 'C', BLUE), (2, 5, 'C', BLUE)],
         strings_on={2, 3, 4, 5}, arrows=[((5, 3), (3, 5), MINT), ((4, 3), (2, 5), BLUE)])
d.text((64, y + 30), 'Works from E and A strings', font=SB(34), fill=TEXT3)
slides.append(img)

# 5 - B string shift
img = background(45, glow=AMBER, glow2=ACCENT); d = ImageDraw.Draw(img, 'RGBA')
header(d, 4)
y = draw_lines(d, (64, 255), ['Crossing the B string?', ('Up 3 frets.', AMBER)], XB(80), TEXT, lh=92)
y = body(d, y + 16, 'From D or G, skip 2 strings and go up 3 frets. G on D fret 5 is G on B fret 8. High e copies low E.')
y = neck(img, y + 40, [(3, 5, 'G', MINT), (1, 8, 'G', AMBER), (2, 5, 'C', BLUE), (0, 8, 'C', AMBER), (5, 3, 'G', MINT), (0, 3, 'G', MINT)],
         arrows=[((3, 5), (1, 8), AMBER), ((2, 5), (0, 8), AMBER)])
d.text((64, y + 30), 'Why: the G-to-B gap is 1 fret smaller', font=SB(34), fill=TEXT3)
slides.append(img)

# 6 - drill + CTA
img = background(46, glow=ACCENT, glow2=MINT); d = ImageDraw.Draw(img, 'RGBA')
tag(d, (64, 170), 'DAILY DRILL  ·  2 MIN')
y = draw_lines(d, (64, 255), ['Pick one note.', ('Find it 6 times.', MINT)], XB(96), TEXT, lh=108)
y = body(d, y + 20, 'Low E, octave up, B-string jump, high e. Under 30 seconds? Pick the next note. Do all 7 this week.')
for i, n in enumerate(['C', 'D', 'E', 'F', 'G', 'A', 'B']):
    cx = 100 + i * 122; cy = y + 90
    d.ellipse((cx - 44, cy - 44, cx + 44, cy + 44), fill=SURF2 + (255,), outline=MINT + (255,), width=3)
    d.text((cx - text_w(XB(44), n) / 2, cy - 28), n, font=XB(44), fill=TEXT)
y += 210
d.rounded_rectangle((64, y, 940, y + 230), 30, fill=SURF + (240,), outline=ACCENT + (200,), width=3)
d.text((104, y + 24), 'Record a riff, get tab with', font=DB(44), fill=TEXT)
d.text((104, y + 80), 'every note and chord named', font=DB(44), fill=TEXT)
d.text((104, y + 140), 'tabscriptoria.com', font=XB(64), fill=MINT)
print('cta bottom', y + 230)
slides.append(img)

for i, im in enumerate(slides, 1):
    save_slide(im, os.path.join(out, f'slide{i}.jpg'))
print('wrote', len(slides), 'slides to', out)
