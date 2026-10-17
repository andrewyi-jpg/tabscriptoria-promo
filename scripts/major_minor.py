"""Video: 'Major or minor? 5 chords, by ear.' Each round strums one chord twice (original plucked-string
synth, no samples), counts down, then reveals the chord and whether it is major or minor.
A Commercial Music Library track is attached at upload time (low volume under the strums).

Usage: python3 major_minor.py OUT.mp4 [STILLS_DIR]
"""
import os, sys, wave, subprocess, tempfile
import numpy as np
from PIL import ImageDraw
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from tslib import *

OUT = sys.argv[1]
STILLS = sys.argv[2] if len(sys.argv) > 2 else None
SR = 44100
OPEN = [40, 45, 50, 55, 59, 64]  # low E -> high e
V = {'D': 'xx0232', 'Em': '022000', 'A': 'x02220', 'F#m': '244222', 'C': 'x32010', 'Dm': 'xx0231'}
ROUNDS = [('D', 'MAJOR'), ('Em', 'MINOR'), ('A', 'MAJOR'), ('F#m', 'MINOR'), ('Dm', 'MINOR')]
S1, S2, TH = 0.15, 1.15, 2.35   # strum 1, strum 2, think start
REV = 3.35                      # reveal
ROUND = 4.6
OUTRO = 3.6
T_TOTAL = len(ROUNDS) * ROUND + OUTRO

BG_IMG = background(131, glow=AMBER, glow2=BLUE)

def frame(t):
    img = BG_IMG.copy(); d = ImageDraw.Draw(img, 'RGBA')
    if t >= len(ROUNDS) * ROUND:
        u = ease((t - len(ROUNDS) * ROUND) / 0.4); a = int(255 * u)
        tag(d, (64, 170), 'TAB SCRIPTORIA')
        draw_lines(d, (64, 300), ['How many', ('did you get?', MINT)], XB(116), TEXT, lh=126)
        y = 640
        for ch, q in ROUNDS:
            d.text((64, y), clean(ch), font=B(48), fill=TEXT)
            d.text((300, y), q.lower(), font=SB(48), fill=MINT if q == 'MAJOR' else BLUE)
            y += 70
        d.rounded_rectangle((64, 1060, 940, 1340), 30, fill=SURF + (int(240 * u),), outline=ACCENT + (a,), width=3)
        d.text((104, 1090), 'Record yourself playing.', font=SB(44), fill=TEXT2 + (a,))
        d.text((104, 1146), 'Tab Scriptoria names the chords.', font=SB(44), fill=TEXT2 + (a,))
        d.text((104, 1224), 'tabscriptoria.com', font=XB(70), fill=TEXT + (a,))
        return img
    r = int(t // ROUND); tt = t - r * ROUND
    ch, q = ROUNDS[r]
    if r == 0:
        draw_lines(d, (64, 190), ['Major or minor?', ('Use your ears.', AMBER)], XB(96), TEXT, lh=106)
        d.text((64, 420), 'Bright = major.  Darker = minor.', font=SB(42), fill=TEXT2)
    else:
        pill(d, (64, 200), f'CHORD {r + 1} OF 5', B(36), SURF2 + (255,), TEXT2, pad=(22, 11), outline=BORDER2 + (255,))
        d.text((64, 290), 'Major or minor?', font=XB(84), fill=TEXT)
    reveal = tt >= REV
    u = ease((tt - REV) / 0.25) if reveal else 0
    # centre card
    pulse = 0
    for s in (S1, S2):
        if s <= tt < s + 0.35:
            pulse = 1 - (tt - s) / 0.35
    box = (190 - 12 * pulse, 520 - 12 * pulse, 890 + 12 * pulse, 960 + 12 * pulse)
    out = (MINT if q == 'MAJOR' else BLUE) if reveal else (ACCENT2 if pulse > 0 else BORDER2)
    d.rounded_rectangle(box, 36, fill=SURF + (245,), outline=out + (255,), width=6)
    cx, cy = (box[0] + box[2]) / 2, (box[1] + box[3]) / 2
    if reveal:
        name = clean(ch); f = XB(190)
        d.text((cx - text_w(f, name) / 2, cy - 120), name, font=f, fill=TEXT + (int(255 * u),))
    else:
        f = XB(220)
        d.text((cx - text_w(f, '?') / 2, cy - 140), '?', font=f, fill=AMBER)
    # status line
    if tt < TH:
        st = 'LISTEN  1/2' if tt < S2 else 'LISTEN  2/2'
        d.text((W / 2 - text_w(B(46), st) / 2, 1000), st, font=B(46), fill=TEXT2)
    elif not reveal:
        left = (REV - tt) / (REV - TH)
        d.rounded_rectangle((W / 2 - 300, 1018, W / 2 - 300 + 600 * left, 1032), 7, fill=AMBER)
    # buttons
    for k, (lab, col) in enumerate((('MAJOR', MINT), ('MINOR', BLUE))):
        x = 64 + k * 450; b = (x, 1110, x + 426, 1290)
        hit = reveal and lab == q
        fill = (col + (int(60 + 195 * u),)) if hit else SURF + (230,)
        oc = col if (hit or not reveal) else BORDER
        d.rounded_rectangle(b, 30, fill=fill, outline=oc + (255,), width=5 if hit else 3)
        tc = BG if (hit and u > 0.5) else (TEXT3 if reveal else TEXT)
        d.text(((b[0] + b[2]) / 2 - text_w(XB(66), lab) / 2, 1160), lab, font=XB(66), fill=tc)
    return img

def pluck(freq, dur, rng, bright=0.5):
    n = int(dur * SR); p = max(2, int(SR / freq))
    buf = rng.uniform(-1, 1, p).astype(np.float64)
    buf = bright * buf + (1 - bright) * np.convolve(buf, np.ones(3) / 3, 'same')
    out = np.zeros(n); decay = 0.996
    for i in range(n):
        v = buf[i % p]; out[i] = v
        buf[i % p] = decay * 0.5 * (v + buf[(i + 1) % p])
    return out

def strum(voicing, dur, rng):
    n = int(dur * SR); out = np.zeros(n); k = 0
    for s, c in enumerate(voicing):
        if c == 'x':
            continue
        f = 440 * 2 ** ((OPEN[s] + int(c) - 69) / 12)
        off = int(k * 0.022 * SR); k += 1
        sig = pluck(f, dur - k * 0.022, rng) * (0.9 if s < 3 else 0.75)
        out[off:off + len(sig)] += sig[: n - off]
    env = np.ones(n); fade = int(0.1 * SR); env[-fade:] = np.linspace(1, 0, fade)
    return out * env

def audio(path):
    rng = np.random.default_rng(11)
    n = int(T_TOTAL * SR); out = np.zeros(n)
    tt = lambda dur: np.arange(int(dur * SR)) / SR
    def add(t, sig):
        i = int(t * SR); out[i:i + len(sig)] += sig[: max(0, n - i)]
    ding = sum(np.sin(2 * np.pi * f * tt(0.6)) * a for f, a in ((988, 0.4), (1319, 0.25), (1976, 0.1))) * np.exp(-tt(0.6) * 7)
    tick = np.sin(2 * np.pi * 1800 * tt(0.05)) * np.exp(-tt(0.05) * 90)
    for r, (ch, _) in enumerate(ROUNDS):
        s = strum(V[ch], 1.15, rng)
        add(r * ROUND + S1, s * 0.5); add(r * ROUND + S2, s * 0.5)
        add(r * ROUND + TH + 0.1, tick * 0.25); add(r * ROUND + TH + 0.6, tick * 0.25)
        add(r * ROUND + REV, ding * 0.3)
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
