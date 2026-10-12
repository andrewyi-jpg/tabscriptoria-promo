"""Video: 'Name these 5 chords from the tab alone.' Countdown quiz, original SFX only
(a Commercial Music Library track is attached at upload time).

Usage: python3 chord_quiz.py OUT.mp4 [STILLS_DIR]
"""
import os, sys, wave, subprocess, tempfile
import numpy as np
from PIL import ImageDraw
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from tslib import *

OUT = sys.argv[1]
STILLS = sys.argv[2] if len(sys.argv) > 2 else None
SR = 44100

# chart low E -> high e ; name ; notes
CHORDS = [('020100', 'E7', 'E  G#  B  D'),
          ('xx0230', 'Dsus2', 'D  E  A'),
          ('xx3210', 'Fmaj7', 'F  A  C  E'),
          ('x20202', 'Bm7', 'B  D  F#  A'),
          ('x32033', 'Cadd9', 'C  D  E  G')]
ROUND = 4.4; GUESS = 3.0
OUTRO = 3.4
T_TOTAL = len(CHORDS) * ROUND + OUTRO

def chart_to_tab(ch):
    """'x32033' -> list high e .. low E of str fret or 'x'."""
    vals = list(ch)
    return list(reversed(vals))

BG_IMG = background(21, glow=ACCENT, glow2=BLUE)

def frame(t):
    img = BG_IMG.copy(); d = ImageDraw.Draw(img, 'RGBA')
    if t >= len(CHORDS) * ROUND:
        u = ease((t - len(CHORDS) * ROUND) / 0.4)
        tag(d, (64, 170), 'TAB SCRIPTORIA')
        draw_lines(d, (64, 300), ['How many', ('did you get?', MINT)], XB(116), TEXT, lh=126)
        # recap grid
        x, yy = 64, 640
        for i, (_, nm, _) in enumerate(CHORDS):
            lab = f'{i + 1}  {nm}'
            if x + text_w(B(44), lab) + 52 > 950:
                x, yy = 64, yy + 120
            box = pill(d, (x, yy), lab, B(44), SURF2 + (255,), TEXT, pad=(26, 14), outline=BORDER2 + (255,))
            x = box[2] + 24
        a = int(255 * u)
        d.rounded_rectangle((64, 960, 940, 1240), 30, fill=SURF + (int(240 * u),), outline=ACCENT + (a,), width=3)
        d.text((104, 990), 'Tab Scriptoria names every', font=SB(44), fill=TEXT2 + (a,))
        d.text((104, 1046), 'chord in your recordings.', font=SB(44), fill=TEXT2 + (a,))
        d.text((104, 1124), 'tabscriptoria.com', font=XB(70), fill=TEXT + (a,))
        return img
    r = int(t // ROUND); tt = t - r * ROUND
    chart, name, notes = CHORDS[r]
    # header: hook on round 1, round counter after
    if r == 0:
        draw_lines(d, (64, 190), ['Name these 5 chords', ('from the tab alone.', MINT)], XB(76), TEXT, lh=84)
    else:
        pill(d, (64, 200), f'CHORD {r + 1} OF 5', B(40), MINT, BG, pad=(24, 12))
    # tab panel
    x0, x1, top, gap = 90, 930, 500, 92
    d.rounded_rectangle((64, top - 70, 950, top + 5 * gap + 70), 30, fill=BG2 + (240,), outline=BORDER + (255,), width=2)
    for i, nm in enumerate(STRINGS):
        y = top + i * gap
        d.line((x0 + 50, y, x1 - 20, y), fill=BORDER2 + (255,), width=3)
        d.text((x0, y - 20), nm, font=M(36), fill=TEXT3)
    d.line((x0 + 50, top, x0 + 50, top + 5 * gap), fill=TEXT3 + (220,), width=4)
    d.line((x1 - 20, top, x1 - 20, top + 5 * gap), fill=TEXT3 + (220,), width=4)
    tab = chart_to_tab(chart)
    cx = (x0 + 50 + x1 - 20) / 2
    for i, v in enumerate(tab):
        y = top + i * gap
        if v == 'x':
            d.text((cx - text_w(B(44), 'x') / 2, y - 27), 'x', font=B(44), fill=TEXT3)
        else:
            fret_pill(d, cx, y, int(v), col=MINT, size=50)
    # countdown / reveal
    cy = top + 5 * gap + 200
    if tt < GUESS:
        n = 3 - int(tt)
        frac = tt - int(tt)
        R = 92
        d.ellipse((W / 2 - R, cy - R, W / 2 + R, cy + R), outline=BORDER2 + (255,), width=10)
        d.arc((W / 2 - R, cy - R, W / 2 + R, cy + R), -90, -90 + 360 * (1 - tt / GUESS), fill=AMBER, width=10)
        s = str(n)
        d.text((W / 2 - text_w(XB(96), s) / 2, cy - 60), s, font=XB(96), fill=TEXT)
    else:
        u = ease((tt - GUESS) / 0.25)
        f = XB(int(130 + 20 * (1 - u)))
        d.text((W / 2 - text_w(f, name) / 2, cy - 100), name, font=f, fill=MINT + (int(255 * u),))
        d.text((W / 2 - text_w(SB(46), notes) / 2, cy + 70), notes, font=SB(46), fill=TEXT2 + (int(255 * u),))
    return img

def sfx(path):
    n = int(T_TOTAL * SR); out = np.zeros(n, np.float32)
    tt = lambda dur: np.arange(int(dur * SR)) / SR
    def add(t, sig):
        i = int(t * SR); out[i:i + len(sig)] += sig[: max(0, n - i)]
    tick = np.sin(2 * np.pi * 1500 * tt(0.05)) * np.exp(-tt(0.05) * 90) * 0.35
    ding = sum(np.sin(2 * np.pi * f * tt(0.6)) * a for f, a in ((988, 0.4), (1319, 0.25), (1976, 0.1))) * np.exp(-tt(0.6) * 7)
    for r in range(len(CHORDS)):
        for k in range(3):
            add(r * ROUND + k, tick)
        add(r * ROUND + GUESS, ding * 0.6)
    add(len(CHORDS) * ROUND, ding * 0.5)
    st = np.clip(np.stack([out, out], 1), -1, 1)
    with wave.open(path, 'w') as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((st * 32767).astype(np.int16).tobytes())

tmp = tempfile.mkdtemp()
vid = os.path.join(tmp, 'v.mp4'); wav = os.path.join(tmp, 's.wav')
enc = Encoder(vid)
for i in range(int(T_TOTAL * FPS)):
    t = i / FPS
    im = frame(t)
    enc.write(im)
    if STILLS and i % 30 == 0:
        os.makedirs(STILLS, exist_ok=True); im.convert('RGB').resize((540, 960)).save(os.path.join(STILLS, f'{i // 30:02d}.jpg'))
enc.close()
sfx(wav)
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', vid, '-i', wav, '-map', '0:v', '-map', '1:a', '-c:v', 'copy',
                '-af', 'loudnorm=I=-14:TP=-1.5:LRA=11', '-ar', '44100', '-c:a', 'aac', '-b:a', '192k', '-shortest',
                '-movflags', '+faststart', OUT], check=True)
print('wrote', OUT, f'{T_TOTAL:.1f}s')
