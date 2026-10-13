"""Carousel: 'Travis picking in 4 steps' (original pattern in G, then G Em C G).

Usage: python3 carousel_travis.py OUT_DIR
Strings: 0 = high e ... 5 = low E. Times are in beats (one 4/4 bar per row).
"""
import os, sys
from PIL import ImageDraw
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from tslib import *

out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, 'out', 'travis')
os.makedirs(out, exist_ok=True)
X0, X1 = 70, 930

# chord -> (thumb A string/fret, thumb B string/fret, index (G string) fret, middle (B string) fret)
CH = {'G': ((5, 3), (3, 0), 0, 3), 'Em': ((5, 0), (3, 2), 0, 0), 'C': ((4, 3), (3, 2), 0, 1)}

def pattern(ch, step):
    """Return notes (start, dur, pitch, string, fret), labels, roles for a one-bar pattern at a build-up step."""
    (sa, fa), (sb, fb), fi, fm = CH[ch]
    ev = []  # (start, string, fret, label, new_at_step)
    for b, (s, f) in enumerate([(sa, fa), (sb, fb), (sa, fa), (sb, fb)]):
        ev.append((b, s, f, 'T', 1))
    ev += [(1.5, 2, fi, 'i', 2), (3.5, 2, fi, 'i', 2), (2.5, 1, fm, 'm', 3), (0, 1, fm, '', 4)]
    ev = [e for e in ev if e[4] <= step]
    ev.sort(key=lambda e: (e[0], -e[1]))
    notes = [(s, 0.45, 0, st, fr) for s, st, fr, _, _ in ev]
    labels = []
    for s, st, fr, lab, k in ev:
        if s == 0 and lab == 'T' and step >= 4:
            lab = 'T+m'
        labels.append(lab)
    roles = ['T' if (k == step and step > 1) else '' for *_, k in ev]
    return notes, labels, roles

def row(img, y, ch, step, show_new=True, gap=56):
    notes, labels, roles = pattern(ch, step)
    return draw_tab_row(img, (X0, y, X1, 0), notes, 0, 4, [0, 4], [(0, ch)], labels=labels,
                        roles=roles if show_new else None, sustain=False, str_gap=gap)

def counts(d, y):
    span = X1 - X0 - 80
    for k, c in enumerate(['1', '&', '2', '&', '3', '&', '4', '&']):
        x = X0 + 60 + (k * 0.5) / 4 * span
        d.text((x - text_w(SB(30), c) / 2, y), c, font=SB(30), fill=TEXT3)

def header(d, step=None):
    if step:
        pill(d, (64, 170), f'STEP {step}', B(32), MINT, BG, pad=(20, 9))
        d.text((64 + text_w(B(32), f'STEP {step}') + 58, 180), 'of 4', font=SB(32), fill=TEXT3)
    else:
        tag(d, (64, 170), 'FINGERSTYLE  ·  SAVE THIS')

def body(d, y, text, col=TEXT2, size=42):
    return draw_lines(d, (64, y), wrap(M(size), text, 860), M(size), col, lh=int(size * 1.34), shadow=False)

def legend(d, y):
    x = 64
    for lab, name in (('T', 'thumb'), ('i', 'index'), ('m', 'middle')):
        d.text((x, y), lab, font=B(36), fill=AMBER)
        d.text((x + text_w(B(36), lab) + 14, y + 2), name, font=SB(34), fill=TEXT2)
        x += text_w(B(36), lab) + 14 + text_w(SB(34), name) + 50

slides = []

# 1 - hook + finished pattern
img = background(21, glow=MINT, glow2=ACCENT); d = ImageDraw.Draw(img, 'RGBA')
header(d)
y = draw_lines(d, (64, 255), ['Travis picking', ('in 4 steps.', MINT)], XB(112), TEXT, lh=120)
y = body(d, y + 20, 'Thumb keeps the bass going, fingers fill the gaps. This is where you end up:')
y = row(img, y + 50, 'G', 4, show_new=False)
legend(d, y + 10)
d.text((64, y + 100), 'Swipe to build it one finger at a time  →', font=SB(38), fill=MINT)
slides.append(img)

steps = [
    (1, ['Thumb only.'], 'Hold G. Thumb alternates low E and D, one note per beat. Do this until you stop thinking about it.'),
    (2, ['Add index.'], 'Index plucks the G string on the "and" of 2 and the "and" of 4. Thumb does not change.'),
    (3, ['Add middle.'], 'Middle plucks the B string on the "and" of 3. Now every off-beat after beat 1 has a note.'),
    (4, ['Pinch beat 1.'], 'Thumb and middle together on beat 1. That is the full pattern. Loop it at 60 BPM.'),
]
for step, title, txt in steps:
    img = background(21 + step); d = ImageDraw.Draw(img, 'RGBA')
    header(d, step)
    y = draw_lines(d, (64, 255), title, XB(100), TEXT, lh=108)
    y = body(d, y + 16, txt)
    y = row(img, y + 50, 'G', step)
    counts(d, y + 4)
    if step > 1:
        d.text((64, y + 70), 'Ringed numbers = the new notes', font=SB(34), fill=TEXT3)
    slides.append(img)

# 6 - chord changes + CTA (last slide = call to action)
img = background(27, glow=ACCENT, glow2=MINT); d = ImageDraw.Draw(img, 'RGBA')
tag(d, (64, 170), 'NEXT  ·  G  Em  C  G')
y = draw_lines(d, (64, 255), ['Same fingers.', ('Thumb follows the root.', MINT)], XB(78), TEXT, lh=88)
y = row(img, y + 30, 'Em', 4, show_new=False, gap=36)
y = row(img, y + 14, 'C', 4, show_new=False, gap=36)
d.rounded_rectangle((64, y + 20, 940, y + 200), 30, fill=SURF + (240,), outline=ACCENT + (200,), width=3)
d.text((104, y + 40), 'Record yours, get the tab', font=DB(46), fill=TEXT)
d.text((104, y + 104), 'tabscriptoria.com', font=XB(64), fill=MINT)
print('cta bottom', y + 200)
slides.append(img)

for i, im in enumerate(slides, 1):
    save_slide(im, os.path.join(out, f'slide{i}.jpg'))
print('wrote', len(slides), 'slides to', out)
