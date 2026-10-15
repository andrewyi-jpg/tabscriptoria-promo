"""Carousel: 'Read any guitar tab: the symbols' (numbers/lines, h p, / \\ b, ~ x PM, drill + CTA).

Usage: python3 carousel_symbols.py OUT_DIR
All tab examples are original licks (no songs).
"""
import os, sys
from PIL import ImageDraw
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from tslib import *

out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, 'out', 'symbols')
os.makedirs(out, exist_ok=True)

SYM = set('hpb/\\~xr')

def tab(img, y, cols, gap=70, x0=64, x1=950, marks=None, above=None):
    """cols: list of dict {string_index: token}. Tokens like '5h7'. Symbol letters drawn amber.
    above: list of (col_from, col_to, text) drawn over the top line (e.g. PM----). Returns bottom y."""
    d = ImageDraw.Draw(img, 'RGBA')
    top = y + (90 if above else 50)
    bot = top + 5 * gap
    d.rounded_rectangle((x0, y - 10, x1, bot + 50), 28, fill=BG2 + (240,), outline=BORDER + (255,), width=2)
    lx0, lx1 = x0 + 80, x1 - 40
    for i, nm in enumerate(STRINGS):
        yy = top + i * gap
        d.line((lx0 - 20, yy, lx1, yy), fill=BORDER2 + (255,), width=3)
        d.text((x0 + 26, yy - 18), nm, font=M(30), fill=TEXT3)
    n = len(cols)
    step = (lx1 - lx0) / n
    X = lambda c: lx0 + (c + 0.5) * step
    f = B(40)
    for c, col in enumerate(cols):
        for s, tok in col.items():
            tw = sum(text_w(f, ch) for ch in tok)
            cx, cy = X(c), top + s * gap
            d.rounded_rectangle((cx - tw / 2 - 10, cy - 26, cx + tw / 2 + 10, cy + 26), 12, fill=BG2 + (255,))
            xx = cx - tw / 2
            for ch in tok:
                d.text((xx, cy - 25), ch, font=f, fill=AMBER if ch in SYM else MINT)
                xx += text_w(f, ch)
    for a, b_, txt in (above or []):
        xa, xb = X(a) - step * 0.4, X(b_) + step * 0.4
        d.text((xa, y + 14), txt, font=B(34), fill=AMBER)
        tx = xa + text_w(B(34), txt) + 10
        for xx in range(int(tx), int(xb), 22):
            d.line((xx, y + 34, xx + 12, y + 34), fill=AMBER, width=4)
    return bot + 50

def header(d, step=None):
    if step:
        pill(d, (64, 170), f'SYMBOL SET {step}', B(32), MINT, BG, pad=(20, 9))
        d.text((64 + text_w(B(32), f'SYMBOL SET {step}') + 58, 180), 'of 4', font=SB(32), fill=TEXT3)
    else:
        tag(d, (64, 170), 'TAB READING  ·  SAVE THIS')

def body(d, y, text, col=TEXT2, size=42):
    return draw_lines(d, (64, y), wrap(M(size), text, 860), M(size), col, lh=int(size * 1.34), shadow=False)

def legend(d, y, rows):
    for sym, txt in rows:
        d.text((64, y), sym, font=XB(50), fill=AMBER)
        d.text((250, y + 8), txt, font=SB(40), fill=TEXT)
        y += 74
    return y

slides = []

# 1 - hook: one original lick that uses every symbol
img = background(71, glow=AMBER, glow2=ACCENT); d = ImageDraw.Draw(img, 'RGBA')
header(d)
y = draw_lines(d, (64, 255), ['Read this tab', ('in 5 slides.', AMBER)], XB(112), TEXT, lh=120)
y = body(d, y + 20, 'Numbers are easy. The letters and squiggles are what trip people up. Here is every one, in order.')
lick = [{5: 'x'}, {5: 'x'}, {4: '5'}, {4: '5h7'}, {3: '7p5'}, {3: '7/9'}, {2: '7b9'}, {2: '7~'}]
y = tab(img, y + 40, lick, above=[(0, 2, 'PM')])
d.text((64, y + 40), 'Swipe for what each one means  →', font=SB(38), fill=MINT)
slides.append(img)

# 2 - lines and numbers
img = background(72); d = ImageDraw.Draw(img, 'RGBA')
header(d, 1)
y = draw_lines(d, (64, 255), ['Lines = strings.', ('Numbers = frets.', MINT)], XB(88), TEXT, lh=100)
y = body(d, y + 16, 'Top line is the thin high e, bottom is the thick low E. 0 means open. Stacked numbers ring together: this is a G chord.')
gch = [{5: '3', 4: '2', 3: '0', 2: '0', 1: '0', 0: '3'}, {}, {5: '3'}, {4: '2'}, {3: '0'}, {2: '0'}]
y = tab(img, y + 40, gch)
d.text((64, y + 30), 'Left: strum it. Right: pick one at a time.', font=SB(34), fill=TEXT3)
slides.append(img)

# 3 - h and p
img = background(73, glow=MINT, glow2=ACCENT); d = ImageDraw.Draw(img, 'RGBA')
header(d, 2)
y = draw_lines(d, (64, 255), ['h and p:', ('pick once, play twice.', MINT)], XB(84), TEXT, lh=96)
y = legend(d, y + 20, [('5h7', 'hammer-on: pick 5, tap down 7'), ('7p5', 'pull-off: pick 7, flick off to 5')])
y = tab(img, y + 30, [{2: '5h7'}, {2: '7p5'}, {1: '5h8'}, {1: '8p5'}, {2: '7'}])
d.text((64, y + 30), 'Only the first note of each pair is picked.', font=SB(34), fill=TEXT3)
slides.append(img)

# 4 - slides and bends
img = background(74, glow=BLUE, glow2=AMBER); d = ImageDraw.Draw(img, 'RGBA')
header(d, 3)
y = draw_lines(d, (64, 255), ['/ \\ slides.', ('b bends.', AMBER)], XB(96), TEXT, lh=108)
y = legend(d, y + 20, [('7/9', 'slide up, keep pressing'), ('9\\7', 'slide back down'), ('7b9', 'bend 7 until it sounds like 9'),
                       ('7b9r7', 'bend, then release')])
y = tab(img, y + 30, [{3: '7/9'}, {3: '9\\7'}, {2: '7b9'}, {2: '7b9r7'}, {3: '7'}])
slides.append(img)

# 5 - vibrato, mutes, palm mute
img = background(75, glow=ROSE, glow2=ACCENT); d = ImageDraw.Draw(img, 'RGBA')
header(d, 4)
y = draw_lines(d, (64, 255), ['~ x PM:', ('the texture marks.', ROSE)], XB(92), TEXT, lh=104)
y = legend(d, y + 20, [('~', 'vibrato: wiggle the held note'), ('x', 'dead note: touch lightly, pick'),
                       ('PM', 'palm mute: hand edge at bridge')])
y = tab(img, y + 30, [{5: '0'}, {5: '0'}, {5: 'x'}, {5: '0'}, {5: '0'}, {5: 'x'}, {4: '2'}, {3: '2~'}], above=[(0, 5, 'PM')])
d.text((64, y + 30), 'PM lasts as long as the dashes do.', font=SB(34), fill=TEXT3)
slides.append(img)

# 6 - drill + CTA
img = background(76, glow=ACCENT, glow2=MINT); d = ImageDraw.Draw(img, 'RGBA')
tag(d, (64, 170), 'TRY IT  ·  2 MIN')
y = draw_lines(d, (64, 255), ['Go back to slide 1.', ('Play it at half speed.', MINT)], XB(80), TEXT, lh=92)
y = body(d, y + 20, 'Say each symbol out loud as you play it. When it feels easy, go full speed and add the PM.')
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
