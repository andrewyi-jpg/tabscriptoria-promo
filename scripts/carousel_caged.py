"""Carousel: 'You know C. Now play it 5 ways.' (CAGED shapes of a C major chord).

Usage: python3 carousel_caged.py OUT_DIR
Strings are indexed 0 = high e ... 5 = low E (same as tslib / Solo ideas).
"""
import os, sys
from PIL import ImageDraw
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from tslib import *

out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, 'out', 'caged')
os.makedirs(out, exist_ok=True)

ICOL = {'R': ACCENT, '3': MINT, '5': BLUE}
# shape name -> (fret window lo, hi, [(string, fret, interval)], muted strings)
SHAPES = {
    'C': (0, 4, [(4, 3, 'R'), (3, 2, '3'), (2, 0, '5'), (1, 1, 'R'), (0, 0, '3')], [5]),
    'A': (2, 6, [(4, 3, 'R'), (3, 5, '5'), (2, 5, 'R'), (1, 5, '3'), (0, 3, '5')], [5]),
    'G': (4, 8, [(5, 8, 'R'), (4, 7, '3'), (3, 5, '5'), (2, 5, 'R'), (1, 5, '3'), (0, 8, 'R')], []),
    'E': (7, 11, [(5, 8, 'R'), (4, 10, '5'), (3, 10, 'R'), (2, 9, '3'), (1, 8, '5'), (0, 8, 'R')], []),
    'D': (9, 13, [(3, 10, 'R'), (2, 12, '5'), (1, 13, 'R'), (0, 12, '3')], [5, 4]),
}
# TAB strings low->high as written in a chord chart
CHART = {'C': 'x32010', 'A': 'x35553', 'G': '875558', 'E': '8 10 10 9 8 8', 'D': 'xx 10 12 13 12'}

def neck(d, x0, y0, x1, lo, hi, dots, muted=(), gap=52, r=32, show_open=True):
    """Horizontal neck, high e on top. lo==0 draws a nut. Returns bottom y."""
    nf = hi - lo
    fx = lambda f: x0 + 50 + (f - lo) * (x1 - x0 - 50) / nf          # fret wire x
    cx = lambda f: fx(f) - (fx(lo + 1) - fx(lo)) / 2 if f > lo else x0 + 20  # note x (between wires)
    d.rounded_rectangle((x0 - 30, y0 - 46, x1 + 30, y0 + 5 * gap + 90), 26, fill=BG2 + (235,), outline=BORDER + (255,), width=2)
    for f in range(lo, hi + 1):
        d.line((fx(f), y0, fx(f), y0 + 5 * gap), fill=TEXT + (255,) if (f == 0) else TEXT3 + (220,), width=10 if f == 0 else 3)
    for i in range(6):
        d.line((x0 + 50, y0 + i * gap, x1, y0 + i * gap), fill=BORDER2 + (255,), width=2 + i // 2)
    for f in (3, 5, 7, 9, 12, 15):
        if lo < f <= hi:
            for yy in ([2.5] if f != 12 else [1.5, 3.5]):
                d.ellipse((cx(f) - 9, y0 + yy * gap - 9, cx(f) + 9, y0 + yy * gap + 9), fill=BORDER2)
    for f in range(lo + 1, hi + 1):
        d.text((cx(f) - text_w(SB(28), str(f)) / 2, y0 + 5 * gap + 26), str(f), font=SB(28), fill=TEXT3)
    for s in muted:
        d.text((x0 - 8, y0 + s * gap - 22), '×', font=B(40), fill=TEXT3)
    for (s, f, lab) in dots:
        x = cx(f) if f > 0 else x0 + 22
        y = y0 + s * gap
        col = ICOL.get(lab, MINT)
        if f == 0:
            d.ellipse((x - r + 6, y - r + 6, x + r - 6, y + r - 6), fill=BG2, outline=col, width=5)
            d.text((x - text_w(B(28), lab) / 2, y - 17), lab, font=B(28), fill=col)
        else:
            d.ellipse((x - r, y - r, x + r, y + r), fill=col)
            d.text((x - text_w(B(30), lab) / 2, y - 18), lab, font=B(30), fill=BG)
    return y0 + 5 * gap + 90

def legend(d, x, y):
    for lab, name in (('R', 'root C'), ('3', '3rd E'), ('5', '5th G')):
        col = ICOL[lab]
        d.ellipse((x, y, x + 44, y + 44), fill=col)
        d.text((x + 22 - text_w(B(26), lab) / 2, y + 7), lab, font=B(26), fill=BG)
        d.text((x + 58, y + 4), name, font=SB(32), fill=TEXT2)
        x += 58 + text_w(SB(32), name) + 44

def head(d, label):
    tag(d, (64, 170), label)

def shape_block(d, y, name, num):
    lo, hi, dots, muted = SHAPES[name]
    pill(d, (64, y), f'{num}', B(34), MINT, BG, pad=(18, 8))
    d.text((130, y), f'{name} shape', font=XB(56), fill=TEXT)
    d.text((W - 150 - text_w(SB(34), CHART[name]), y + 14), CHART[name], font=SB(34), fill=TEXT3)
    return neck(d, 100, y + 116, 900, lo, hi, dots, muted)

slides = []

# 1 - hook + whole-neck map
img = background(11, glow=BLUE, glow2=ACCENT); d = ImageDraw.Draw(img, 'RGBA')
head(d, 'GUITAR CHORDS  ·  SAVE THIS')
y = draw_lines(d, (64, 255), ['You know C.'], XB(112), TEXT, lh=120)
y = draw_lines(d, (64, y), [('Now play it', MINT), ('5 ways.', MINT)], XB(112), MINT, lh=120)
y = draw_lines(d, (64, y + 24), wrap(M(42), 'Same three notes, five spots on the neck. Guitarists call it CAGED.', 860), M(42), TEXT2, lh=56, shadow=False)
# neck map 0-15 with shape windows
ny = y + 110; x0, x1 = 90, 920; lo, hi = 0, 15
fx = lambda f: x0 + (f - lo) * (x1 - x0) / (hi - lo)
gap = 40
d.rounded_rectangle((x0 - 30, ny - 110, x1 + 30, ny + 5 * gap + 80), 26, fill=BG2 + (235,), outline=BORDER + (255,), width=2)
bands = [('C', 0, 3, ACCENT), ('A', 2, 5, MINT), ('G', 4, 8, BLUE), ('E', 7, 10, AMBER), ('D', 9, 13, ROSE)]
for i, (nm, a, b, col) in enumerate(bands):
    yy = ny - 88 + (i % 2) * 34
    d.rounded_rectangle((fx(a) + 4, yy, fx(b) - 4, yy + 26), 13, fill=col + (230,))
    d.text(((fx(a) + fx(b)) / 2 - text_w(B(22), nm) / 2, yy), nm, font=B(22), fill=BG)
for f in range(lo, hi + 1):
    d.line((fx(f), ny, fx(f), ny + 5 * gap), fill=TEXT + (255,) if f == 0 else TEXT3 + (200,), width=8 if f == 0 else 2)
for i in range(6):
    d.line((x0, ny + i * gap, x1, ny + i * gap), fill=BORDER2 + (255,), width=2)
for f in (3, 5, 7, 9, 12, 15):
    lab = str(f); xm = (fx(f - 1) + fx(f)) / 2
    d.text((xm - text_w(SB(24), lab) / 2, ny + 5 * gap + 18), lab, font=SB(24), fill=TEXT3)
# every C note in frets 1-15 (string, fret)
for s, f in [(4, 3), (3, 10), (2, 5), (1, 1), (1, 13), (0, 8), (5, 8), (4, 15)]:
    xm = (fx(f - 1) + fx(f)) / 2; ym = ny + s * gap
    d.ellipse((xm - 15, ym - 15, xm + 15, ym + 15), fill=ACCENT)
d.text((64, ny + 5 * gap + 120), 'Purple dots = every C up to fret 15.', font=SB(38), fill=TEXT)
d.text((64, ny + 5 * gap + 172), 'Swipe for the 5 shapes  →', font=SB(38), fill=MINT)
slides.append(img)

# 2-4 - shapes
pairs = [(['C', 'A'], 'Shapes 1 + 2: the ones you know', 12), (['G', 'E'], 'Shapes 3 + 4: up the neck', 13), (['D'], None, 14)]
n = 1
for names, sub, seed in pairs:
    img = background(seed); d = ImageDraw.Draw(img, 'RGBA')
    head(d, 'CAGED  ·  C MAJOR')
    if sub:
        d.text((64, 250), sub, font=DB(50), fill=TEXT)
        legend(d, 64, 320)
        y = 410
    else:
        d.text((64, 250), 'Shape 5, then it repeats', font=DB(50), fill=TEXT)
        legend(d, 64, 320)
        y = 410
    for nm in names:
        y = shape_block(d, y, nm, n) + 30; n += 1
    if names == ['C', 'A']:
        pass
    if names == ['G', 'E']:
        d.text((64, y - 6), 'G shape is a stretch: play just the top 4 strings.', font=M(36), fill=AMBER)
    if names == ['D']:
        y = draw_lines(d, (64, y + 6), wrap(M(42), 'Go past fret 12 and the C shape comes back, an octave higher. Five shapes cover the whole neck.', 860), M(42), TEXT2, lh=56, shadow=False)
    slides.append(img)

# 5 - drill
img = background(15, glow=MINT, glow2=BLUE); d = ImageDraw.Draw(img, 'RGBA')
head(d, 'THE 2-MINUTE DRILL')
y = draw_lines(d, (64, 255), ['Find the root.', ('Then the shape.', MINT)], XB(92), TEXT, lh=100)
steps = [('1', 'Metronome at 60. Strum C once per beat, 4 beats per shape.'),
         ('2', 'Climb C, A, G, E, D, then walk back down.'),
         ('3', 'Before each move, look for the purple root first.'),
         ('4', 'Next day: same drill with G. The shapes slide, the order stays.')]
y += 50
for num, txt in steps:
    pill(d, (64, y), num, B(34), MINT, BG, pad=(18, 8))
    y = draw_lines(d, (140, y - 2), wrap(M(42), txt, 790), M(42), TEXT, lh=56, shadow=False) + 34
slides.append(img)

# 6 - CTA
img = background(16, glow=ACCENT, glow2=MINT); d = ImageDraw.Draw(img, 'RGBA')
head(d, 'TAB SCRIPTORIA')
y = draw_lines(d, (64, 255), ['Play it.', ('See every chord', MINT), ('written out.', MINT)], XB(100), TEXT, lh=110)
y = draw_lines(d, (64, y + 30), wrap(M(44), 'Record yourself on any guitar. Tab Scriptoria writes the tab with chord names and fingerings, so you can check which shape you used.', 860), M(44), TEXT2, lh=60, shadow=False)
d.rounded_rectangle((64, y + 60, 940, y + 260), 30, fill=SURF + (240,), outline=ACCENT + (200,), width=3)
d.text((104, y + 92), 'tabscriptoria.com', font=XB(70), fill=TEXT)
d.text((104, y + 186), 'Free: 5 min a month when you sign in', font=SB(36), fill=MINT)
d.text((64, y + 320), 'Which shape do you never use?', font=SB(40), fill=TEXT)
slides.append(img)

for i, im in enumerate(slides, 1):
    save_slide(im, os.path.join(out, f'slide{i}.jpg'))
print('wrote', len(slides), 'slides to', out)
