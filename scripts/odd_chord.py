"""Video: 'One of these chords is NOT in the key.' 5-round quiz; each round strums 4 chords
(original plucked-string synth, no samples), then reveals the outsider and why.
A Commercial Music Library track is attached at upload time (low volume under the strums).

Usage: python3 odd_chord.py OUT.mp4 [STILLS_DIR]
"""
import os, sys, wave, subprocess, tempfile
import numpy as np
from PIL import ImageDraw
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from tslib import *

OUT = sys.argv[1]
STILLS = sys.argv[2] if len(sys.argv) > 2 else None
SR = 44100

# voicings low E -> high e
V = {'G': '320003', 'Em': '022000', 'C': 'x32010', 'F': '133211', 'Dm': 'xx0231', 'Ab': '466544',
     'D': 'xx0232', 'Bm': 'x24432', 'Gm': '355333', 'A': 'x02220', 'F#m': '244222', 'E': '022100',
     'B': 'x24442', 'C#m': 'x46654'}
ROUNDS = [('G', ['G', 'Em', 'C', 'F'], 'F', 'G major has F#, not F'),
          ('C', ['C', 'Ab', 'Dm', 'G'], 'Ab', 'C major has no flats'),
          ('D', ['D', 'Bm', 'Gm', 'A'], 'Gm', 'D major has B, not Bb'),
          ('A', ['A', 'Dm', 'E', 'F#m'], 'Dm', 'A major has F#, not F'),
          ('E', ['E', 'B', 'C#m', 'G'], 'G', 'E major has G#, not G')]
BEAT = 0.8; PLAY = 4 * BEAT; THINK = 0.9; ROUND = 5.6
OUTRO = 3.6
T_TOTAL = len(ROUNDS) * ROUND + OUTRO
OPEN = [40, 45, 50, 55, 59, 64]

BG_IMG = background(61, glow=ROSE, glow2=ACCENT)

def card_boxes():
    boxes = []
    for k in range(4):
        cx = 64 + (k % 2) * 450; cy = 560 + (k // 2) * 300
        boxes.append((cx, cy, cx + 426, cy + 270))
    return boxes

def frame(t):
    img = BG_IMG.copy(); d = ImageDraw.Draw(img, 'RGBA')
    if t >= len(ROUNDS) * ROUND:
        u = ease((t - len(ROUNDS) * ROUND) / 0.4); a = int(255 * u)
        tag(d, (64, 170), 'TAB SCRIPTORIA')
        draw_lines(d, (64, 300), ['How many', ('did you get?', MINT)], XB(116), TEXT, lh=126)
        y = 640
        for key, _, odd, _ in ROUNDS:
            d.text((64, y), f'Key of {key}', font=SB(44), fill=TEXT2)
            d.text((420, y), clean(odd), font=B(44), fill=ROSE)
            y += 66
        d.rounded_rectangle((64, 1020, 940, 1300), 30, fill=SURF + (int(240 * u),), outline=ACCENT + (a,), width=3)
        d.text((104, 1050), 'Tab Scriptoria names every', font=SB(44), fill=TEXT2 + (a,))
        d.text((104, 1106), 'chord in your recordings.', font=SB(44), fill=TEXT2 + (a,))
        d.text((104, 1184), 'tabscriptoria.com', font=XB(70), fill=TEXT + (a,))
        return img
    r = int(t // ROUND); tt = t - r * ROUND
    key, chords, odd, why = ROUNDS[r]
    if r == 0:
        draw_lines(d, (64, 190), ['1 chord is NOT', ('in the key. Which?', ROSE)], XB(80), TEXT, lh=90)
        pill(d, (64, 400), f'KEY OF {key}', B(40), MINT, BG, pad=(24, 12))
    else:
        pill(d, (64, 200), f'ROUND {r + 1} OF 5', B(36), SURF2 + (255,), TEXT2, pad=(22, 11), outline=BORDER2 + (255,))
        draw_lines(d, (64, 300), [(f'Key of {key}', MINT)], XB(110), TEXT)
    reveal = tt >= PLAY + THINK
    u = ease((tt - PLAY - THINK) / 0.25) if reveal else 0
    playing = int(tt // BEAT) if tt < PLAY else -1
    for k, (box, ch) in enumerate(zip(card_boxes(), chords)):
        on = k == playing
        col, out = SURF + (240,), BORDER2 + (255,)
        if on:
            col, out = SURF2 + (255,), ACCENT2 + (255,)
        if reveal:
            out = (ROSE if ch == odd else MINT) + (255,)
        lift = -10 if on else 0
        b = (box[0], box[1] + lift, box[2], box[3] + lift)
        d.rounded_rectangle(b, 30, fill=col, outline=out, width=6 if (on or reveal) else 3)
        f = XB(120)
        name = clean(ch)
        tc = TEXT
        if reveal:
            tc = ROSE if ch == odd else tuple(int(c * (1 - 0.45 * u)) for c in TEXT)
        d.text(((b[0] + b[2]) / 2 - text_w(f, name) / 2, b[1] + 60), name, font=f, fill=tc)
        if reveal and ch == odd:
            d.text((b[2] - 70, b[1] + 16), 'X', font=XB(52), fill=ROSE + (int(255 * u),))
    cy = 1230
    if not reveal and tt >= PLAY:
        s = '?'
        d.text((W / 2 - text_w(XB(110), s) / 2, cy - 60), s, font=XB(110), fill=AMBER)
    elif reveal:
        a = int(255 * u)
        d.text((W / 2 - text_w(B(52), why) / 2, cy - 20), why, font=B(52), fill=TEXT + (a,))
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

def audio(path):
    rng = np.random.default_rng(7)
    n = int(T_TOTAL * SR); out = np.zeros(n)
    tt = lambda dur: np.arange(int(dur * SR)) / SR
    def add(t, sig):
        i = int(t * SR); out[i:i + len(sig)] += sig[: max(0, n - i)]
    ding = sum(np.sin(2 * np.pi * f * tt(0.6)) * a for f, a in ((988, 0.4), (1319, 0.25), (1976, 0.1))) * np.exp(-tt(0.6) * 7)
    buzz = np.sign(np.sin(2 * np.pi * 140 * tt(0.25))) * np.exp(-tt(0.25) * 10) * 0.12
    cache = {}
    for r, (_, chords, odd, _) in enumerate(ROUNDS):
        for k, ch in enumerate(chords):
            if ch not in cache:
                cache[ch] = strum(V[ch], BEAT + 0.3, rng)
            add(r * ROUND + k * BEAT, cache[ch] * 0.5)
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
