"""Carousel: 'Every solo starts with this box.' A minor pentatonic box 1 (frets 5-8): shape + fingers,
root notes, an original descending lick, a target bend, a 2-minute drill + CTA.

Usage: python3 carousel_penta.py OUT_DIR
Neck drawn tab-style (top line = high e, bottom = low E), zoomed to frets 4-9.
"""
import os, sys
from PIL import ImageDraw
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from tslib import *

out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, 'out', 'penta')
os.makedirs(out, exist_ok=True)

F0, F1 = 4, 9            # first and last fret shown (fret wires F0..F1, so positions F0+1..F1)
X0, X1 = 150, 930
def fx(f):               # centre x of fret position f
    step = (X1 - X0) / (F1 - F0)
    return X0 + (f - F0 - 0.5) * step

# A minor pentatonic, box 1 (string 0=high e .. 5=low E): (string, fret, note, finger)
BOX = [(5, 5, 'A', 1), (5, 8, 'C', 4), (4, 5, 'D', 1), (4, 7, 'E', 3), (3, 5, 'G', 1), (3, 7, 'A', 3),
       (2, 5, 'C', 1), (2, 7, 'D', 3), (1, 5, 'E', 1), (1, 8, 'G', 4), (0, 5, 'A', 1), (0, 8, 'C', 4)]

def neck(img, y, dots, gap=92, arrows=(), show='note'):
    """dots: list of (string, fret, label, color, ring). Returns bottom y."""
    d = ImageDraw.Draw(img, 'RGBA')
    top, bot = y + 40, y + 40 + 5 * gap
    d.rounded_rectangle((64, y - 10, 950, bot + 100), 28, fill=BG2 + (240,), outline=BORDER + (255,), width=2)
    for f in (5, 7):
        cx = fx(f); d.ellipse((cx - 10, (top + bot) / 2 - 10, cx + 10, (top + bot) / 2 + 10), fill=BORDER2 + (255,))
    step = (X1 - X0) / (F1 - F0)
    for k in range(F1 - F0 + 1):
        x = X0 + k * step
        d.line((x, top, x, bot), fill=BORDER2 + (255,), width=3)
    for i, nm in enumerate(STRINGS):
        yy = top + i * gap
        d.line((X0 - 40, yy, X1, yy), fill=TEXT3 + (255,), width=3)
        d.text((80, yy - 16), nm, font=M(28), fill=TEXT3)
    for f in range(F0 + 1, F1 + 1):
        d.text((fx(f) - text_w(SB(28), str(f)) / 2, bot + 36), str(f), font=SB(28), fill=MINT if f == 5 else TEXT3)
    for (s1, f1), (s2, f2), col in arrows:
        d.line((fx(f1), top + s1 * gap, fx(f2), top + s2 * gap), fill=col + (220,), width=7)
    for s, f, lab, col, ring in dots:
        cx, cy = fx(f), top + s * gap; r = 32
        d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=col)
        if ring:
            d.ellipse((cx - r - 9, cy - r - 9, cx + r + 9, cy + r + 9), outline=TEXT, width=4)
        fo = B(30)
        d.text((cx - text_w(fo, lab) / 2, cy - 19), lab, font=fo, fill=BG)
    return bot + 100

def tabline(img, y, cols, title=None):
    """cols: list of (string, token). Simple one-bar tab panel; returns bottom y."""
    d = ImageDraw.Draw(img, 'RGBA'); gap = 56; top = y + 40
    d.rounded_rectangle((64, y - 10, 950, top + 5 * gap + 40), 28, fill=BG2 + (240,), outline=BORDER + (255,), width=2)
    lx0, lx1 = 150, 910
    for i, nm in enumerate(STRINGS):
        yy = top + i * gap
        d.line((lx0 - 30, yy, lx1, yy), fill=BORDER2 + (255,), width=3)
        d.text((86, yy - 17), nm, font=M(28), fill=TEXT3)
    stepx = (lx1 - lx0) / len(cols); f = B(42)
    for c, (s, tok) in enumerate(cols):
        cx = lx0 + (c + 0.5) * stepx; cy = top + s * gap
        tw = text_w(f, tok)
        d.rounded_rectangle((cx - tw / 2 - 12, cy - 26, cx + tw / 2 + 12, cy + 26), 13, fill=BG2 + (255,), outline=MINT + (255,), width=3)
        xx = cx - tw / 2
        for ch in tok:
            d.text((xx, cy - 26), ch, font=f, fill=AMBER if ch in 'br' else MINT)
            xx += text_w(f, ch)
    return top + 5 * gap + 40

def header(d, step=None):
    if step:
        pill(d, (64, 170), f'STEP {step}', B(32), MINT, BG, pad=(20, 9))
        d.text((64 + text_w(B(32), f'STEP {step}') + 58, 180), 'of 4', font=SB(32), fill=TEXT3)
    else:
        tag(d, (64, 170), 'SOLOING  ·  SAVE THIS')

def body(d, y, text, col=TEXT2, size=42):
    return draw_lines(d, (64, y), wrap(M(size), text, 860), M(size), col, lh=int(size * 1.34), shadow=False)

def bullets(d, y, rows, size=44):
    for txt in rows:
        d.ellipse((64, y + 14, 84, y + 34), fill=AMBER)
        y = draw_lines(d, (110, y), wrap(SB(size), txt, 820), SB(size), TEXT, lh=int(size * 1.3), shadow=False) + 14
    return y

slides = []

# 1 - hook
img = background(121, glow=MINT, glow2=ACCENT); d = ImageDraw.Draw(img, 'RGBA')
header(d)
y = draw_lines(d, (64, 255), ['Every solo starts', ('with this box.', MINT)], XB(100), TEXT, lh=110)
y = body(d, y + 16, 'A minor pentatonic, box 1. 12 notes, 2 per string, frets 5 to 8. Learn it in 4 steps.')
neck(img, y + 50, [(s, f, n, MINT if n == 'A' else ACCENT2, False) for s, f, n, _ in BOX])
d.text((64, 1400), 'Swipe for the 4 steps  →', font=SB(38), fill=MINT)
slides.append(img)

# 2 - fingers
img = background(122, glow=BLUE, glow2=MINT); d = ImageDraw.Draw(img, 'RGBA')
header(d, 1)
y = draw_lines(d, (64, 255), ['One finger', ('per fret.', BLUE)], XB(100), TEXT, lh=110)
y = bullets(d, y + 24, ['Index on fret 5 the whole time.',
                        'Ring finger on 7, pinky on 8.',
                        'Low E to high e and back. Slowly, every note clean.'])
neck(img, y + 40, [(s, f, str(fi), BLUE if fi == 1 else (MINT if fi == 3 else AMBER), False) for s, f, _, fi in BOX])
slides.append(img)

# 3 - roots
img = background(123, glow=AMBER, glow2=ACCENT); d = ImageDraw.Draw(img, 'RGBA')
header(d, 2)
y = draw_lines(d, (64, 255), ['Know where', ('home is.', AMBER)], XB(100), TEXT, lh=110)
y = body(d, y + 16, 'The A notes are home. Phrases that end on an A sound finished. There are 3 in the box:')
neck(img, y + 50, [(s, f, n, AMBER if n == 'A' else SURF2, n == 'A') for s, f, n, _ in BOX])
d.text((64, 1330), 'Low E fret 5  ·  D fret 7  ·  high e fret 5', font=SB(36), fill=TEXT2)
slides.append(img)

# 4 - first lick
img = background(124, glow=MINT, glow2=BLUE); d = ImageDraw.Draw(img, 'RGBA')
header(d, 3)
y = draw_lines(d, (64, 255), ['Walk down,', ('land on A.', MINT)], XB(100), TEXT, lh=110)
y = body(d, y + 16, 'Six notes from the box, top string down, ending on the D string root. Play it over an Am chord.')
y = tabline(img, y + 50, [(0, '5'), (1, '8'), (1, '5'), (2, '7'), (2, '5'), (3, '7')])
d.text((64, y + 40), 'A  ·  G  ·  E  ·  D  ·  C  ·  A', font=DB(48), fill=TEXT2)
slides.append(img)

# 5 - bend
img = background(125, glow=ROSE, glow2=ACCENT); d = ImageDraw.Draw(img, 'RGBA')
header(d, 4)
y = draw_lines(d, (64, 255), ['Bend the G string', ('a whole step.', ROSE)], XB(92), TEXT, lh=102)
y = bullets(d, y + 24, ['Ring finger on G fret 7, index and middle behind it to help push.',
                        'Push until it sounds like fret 9.',
                        'Then B fret 5, then high e fret 5. Home.'])
y = tabline(img, y + 40, [(2, '7b9'), (2, '9r7'), (1, '5'), (0, '5')])
d.text((64, y + 30), 'b = bend   r = release', font=SB(34), fill=TEXT3)
slides.append(img)

# 6 - drill + CTA
img = background(126, glow=ACCENT, glow2=MINT); d = ImageDraw.Draw(img, 'RGBA')
tag(d, (64, 170), 'TRY IT  ·  2 MIN')
y = draw_lines(d, (64, 255), ['Box up and down.', ('Then the 2 licks.', MINT)], XB(86), TEXT, lh=98)
y = body(d, y + 20, '30 s box at a slow, even speed. 30 s each lick. 30 s making your own, always ending on an A.')
y += 50
d.rounded_rectangle((64, y, 940, y + 230), 30, fill=SURF + (240,), outline=ACCENT + (200,), width=3)
d.text((104, y + 24), 'Record your solo, get the tab', font=DB(44), fill=TEXT)
d.text((104, y + 80), 'with fingerings to practice', font=DB(44), fill=TEXT)
d.text((104, y + 140), 'tabscriptoria.com', font=XB(64), fill=MINT)
print('cta bottom', y + 230)
slides.append(img)

for i, im in enumerate(slides, 1):
    save_slide(im, os.path.join(out, f'slide{i}.jpg'))
print('wrote', len(slides), 'slides to', out)
