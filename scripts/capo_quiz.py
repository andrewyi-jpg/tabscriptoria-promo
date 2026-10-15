"""Video: 'Capo quiz: what chord does it really sound like?' 5 rounds; each shows a capo position and an
open chord shape (chord box), strums the sounding chord (original plucked-string synth), then reveals it.
A Commercial Music Library track is attached at upload time (low volume under the strums).

Usage: python3 capo_quiz.py OUT.mp4 [STILLS_DIR]
"""
import os, sys, wave, subprocess, tempfile
import numpy as np
from PIL import ImageDraw
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from tslib import *

OUT = sys.argv[1]
STILLS = sys.argv[2] if len(sys.argv) > 2 else None
SR = 44100

# shape voicings low E -> high e
SHAPE = {'G': '320003', 'C': 'x32010', 'Em': '022000', 'D': 'xx0232', 'Am': 'x02210'}
# (capo, shape, sounding chord, why)
ROUNDS = [(2, 'G', 'A', 'G up 2 frets = A'),
          (3, 'C', 'Eb', 'C up 3 frets = Eb'),
          (5, 'Em', 'Am', 'Em up 5 frets = Am'),
          (4, 'D', 'F#', 'D up 4 frets = F#'),
          (7, 'Am', 'Em', 'Am up 7 frets = Em')]
BEAT = 0.75; STRUMS = 2; PLAY = STRUMS * BEAT; THINK = 1.6; ROUND = 5.4
OUTRO = 3.8
T_TOTAL = len(ROUNDS) * ROUND + OUTRO
OPEN = [40, 45, 50, 55, 59, 64]

BG_IMG = background(81, glow=AMBER, glow2=BLUE)

def chord_box(d, x, y, capo, shape, w=520, h=560):
    """Vertical chord box: strings left (low E) to right (high e); capo bar at top, 4 frets below it."""
    gx = w / 5; gy = h / 4
    d.rounded_rectangle((x - 60, y - 150, x + w + 60, y + h + 70), 34, fill=SURF + (240,), outline=BORDER2 + (255,), width=3)
    for s in range(6):
        d.line((x + s * gx, y, x + s * gx, y + h), fill=TEXT3 + (255,), width=4)
    for f in range(5):
        d.line((x, y + f * gy, x + w, y + f * gy), fill=BORDER2 + (255,), width=4)
    # capo bar
    d.rounded_rectangle((x - 30, y - 22, x + w + 30, y + 14), 16, fill=AMBER)
    lab = f'CAPO {capo}'
    d.text((x + w / 2 - text_w(B(34), lab) / 2, y - 80), lab, font=B(34), fill=AMBER)
    for s, c in enumerate(shape):
        cx = x + s * gx
        if c == 'x':
            d.line((cx - 14, y + h + 22, cx + 14, y + h + 50), fill=ROSE, width=5)
            d.line((cx + 14, y + h + 22, cx - 14, y + h + 50), fill=ROSE, width=5)
        elif c == '0':
            d.ellipse((cx - 15, y + h + 21, cx + 15, y + h + 51), outline=MINT, width=5)
        else:
            cy = y + (int(c) - 0.5) * gy
            d.ellipse((cx - 32, cy - 32, cx + 32, cy + 32), fill=MINT)

def frame(t):
    img = BG_IMG.copy(); d = ImageDraw.Draw(img, 'RGBA')
    if t >= len(ROUNDS) * ROUND:
        u = ease((t - len(ROUNDS) * ROUND) / 0.4); a = int(255 * u)
        tag(d, (64, 170), 'TAB SCRIPTORIA')
        draw_lines(d, (64, 300), ['How many', ('did you get?', MINT)], XB(116), TEXT, lh=126)
        y = 640
        for capo, shape, real, _ in ROUNDS:
            d.text((64, y), f'Capo {capo} + {shape}', font=SB(44), fill=TEXT2)
            d.text((470, y), '= ' + clean(real), font=B(44), fill=MINT)
            y += 66
        d.rounded_rectangle((64, 1020, 940, 1300), 30, fill=SURF + (int(240 * u),), outline=ACCENT + (a,), width=3)
        d.text((104, 1050), 'Tab Scriptoria names the chords', font=SB(44), fill=TEXT2 + (a,))
        d.text((104, 1106), 'in your recordings.', font=SB(44), fill=TEXT2 + (a,))
        d.text((104, 1184), 'tabscriptoria.com', font=XB(70), fill=TEXT + (a,))
        return img
    r = int(t // ROUND); tt = t - r * ROUND
    capo, shape, real, why = ROUNDS[r]
    if r == 0:
        draw_lines(d, (64, 190), ['Capo on. What does', ('it REALLY sound like?', AMBER)], XB(74), TEXT, lh=86)
    else:
        pill(d, (64, 200), f'ROUND {r + 1} OF 5', B(36), SURF2 + (255,), TEXT2, pad=(22, 11), outline=BORDER2 + (255,))
        d.text((64, 285), 'What does it sound like?', font=XB(64), fill=TEXT)
    pill(d, (64, 390), f'{shape} shape', B(44), SURF2 + (255,), TEXT, pad=(24, 12), outline=MINT + (255,))
    bump = -8 if (tt < PLAY and (tt % BEAT) < 0.15) else 0
    chord_box(d, 280, 640 + bump, capo, SHAPE[shape])
    reveal = tt >= PLAY + THINK
    u = ease((tt - PLAY - THINK) / 0.25) if reveal else 0
    cy = 1300
    if not reveal and tt >= PLAY:
        left = PLAY + THINK - tt
        s = '?'
        d.text((W / 2 - text_w(XB(110), s) / 2, cy - 40), s, font=XB(110), fill=AMBER)
        bw = 600 * left / THINK
        d.rounded_rectangle((W / 2 - 300, cy + 100, W / 2 - 300 + bw, cy + 112), 6, fill=AMBER)
    elif reveal:
        a = int(255 * u)
        s = 'Sounds like ' + clean(real)
        d.text((W / 2 - text_w(XB(84), s) / 2, cy - 30), s, font=XB(84), fill=MINT + (a,))
        d.text((W / 2 - text_w(SB(42), why) / 2, cy + 80), why, font=SB(42), fill=TEXT2 + (a,))
    return img

def pluck(freq, dur, rng, bright=0.5):
    n = int(dur * SR); p = max(2, int(SR / freq))
    buf = rng.uniform(-1, 1, p).astype(np.float64)
    # soften the excitation a little (pick position / brightness)
    buf = bright * buf + (1 - bright) * np.convolve(buf, np.ones(3) / 3, 'same')
    out = np.zeros(n); decay = 0.996
    for i in range(n):
        v = buf[i % p]
        out[i] = v
        buf[i % p] = decay * 0.5 * (v + buf[(i + 1) % p])
    return out

def strum(voicing, dur, rng):
    n = int(dur * SR); out = np.zeros(n)
    k = 0
    for s, c in enumerate(voicing):
        if c == 'x':
            continue
        f = 440 * 2 ** ((OPEN[s] + int(c) - 69) / 12)
        off = int(k * 0.018 * SR); k += 1
        sig = pluck(f, dur - k * 0.018, rng) * (0.9 if s < 3 else 0.7)
        out[off:off + len(sig)] += sig[: n - off]
    env = np.ones(n); fade = int(0.08 * SR); env[-fade:] = np.linspace(1, 0, fade)
    return out * env

def shifted(shape, capo):
    return [c if c == 'x' else str(int(c) + capo) for c in shape]

def audio(path):
    rng = np.random.default_rng(11)
    n = int(T_TOTAL * SR); out = np.zeros(n)
    tt = lambda dur: np.arange(int(dur * SR)) / SR
    def add(t, sig):
        i = int(t * SR); out[i:i + len(sig)] += sig[: max(0, n - i)]
    ding = sum(np.sin(2 * np.pi * f * tt(0.6)) * a for f, a in ((988, 0.4), (1319, 0.25), (1976, 0.1))) * np.exp(-tt(0.6) * 7)
    for r, (capo, shape, _, _) in enumerate(ROUNDS):
        v = shifted(SHAPE[shape], capo)
        for k in range(STRUMS):
            add(r * ROUND + k * BEAT, strum(v, BEAT + (0.9 if k == STRUMS - 1 else 0.3), rng) * 0.5)
        add(r * ROUND + PLAY + THINK, ding * 0.35)
    add(len(ROUNDS) * ROUND, ding * 0.3)
    out = out / max(1e-6, np.abs(out).max()) * 0.9
    st = np.stack([out, out], 1)
    with wave.open(path, 'w') as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((st * 32767).astype(np.int16).tobytes())

tmp = tempfile.mkdtemp()
vid = os.path.join(tmp, 'v.mp4'); wav = os.path.join(tmp, 's.wav')
audio(wav)
enc = Encoder(vid)
for i in range(int(T_TOTAL * FPS)):
    t = i / FPS
    im = frame(t)
    enc.write(im)
    if STILLS and i % 15 == 0:
        os.makedirs(STILLS, exist_ok=True); im.convert('RGB').resize((360, 640)).save(os.path.join(STILLS, f'{i // 15:03d}.jpg'))
enc.close()
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', vid, '-i', wav, '-map', '0:v', '-map', '1:a', '-c:v', 'copy',
                '-af', 'loudnorm=I=-14:TP=-1.5:LRA=11', '-ar', '44100', '-c:a', 'aac', '-b:a', '192k', '-shortest',
                '-movflags', '+faststart', OUT], check=True)
print('wrote', OUT, f'{T_TOTAL:.1f}s')
