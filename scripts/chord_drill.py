"""Video: 'Keep up? G Em C D at 3 speeds.' Chord-change play-along: count-in, then the progression at
70, 100 and 130 BPM (2 beats per chord), big chord box for the current chord + small 'next' box.
Audio: original plucked-string synth strums + click. A CML track is attached at upload time (low volume).

Usage: python3 chord_drill.py OUT.mp4 [STILLS_DIR]
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
SHAPE = {'G': '320003', 'Em': '022000', 'C': 'x32010', 'D': 'xx0232'}
FING = {'G': '21xxx3', 'Em': 'x23xxx', 'C': 'x32x1x', 'D': 'xxx132'}
PROG = ['G', 'Em', 'C', 'D']
SPEEDS = [70, 100, 130]
BPC = 2  # beats per chord
COUNT = 2  # count-in beats at the first tempo

# beat timeline: (time, kind, speed_idx, chord_idx, beat_in_chord)
BEATS = []
t = 0.0
for k in range(COUNT):
    BEATS.append((t, 'count', 0, -1, k)); t += 60 / SPEEDS[0]
for si, bpm in enumerate(SPEEDS):
    for ci in range(len(PROG)):
        for b in range(BPC):
            BEATS.append((t, 'play', si, ci, b)); t += 60 / bpm
PLAY_END = t
OUTRO = 2.6
T_TOTAL = PLAY_END + OUTRO
BT = np.array([b[0] for b in BEATS])

BG_IMG = background(111, glow=BLUE, glow2=MINT)

def chord_box(d, x, y, name, w=460, h=470, small=False):
    shape, fing = SHAPE[name], FING[name]
    gx = w / 5; gy = h / 4; r = 18 if small else 36
    d.rounded_rectangle((x - (40 if small else 70), y - (90 if small else 205), x + w + (40 if small else 70), y + h + (50 if small else 80)),
                        24 if small else 34, fill=SURF + (240,), outline=(BORDER2 if small else MINT) + (255,), width=3)
    nf = SB(40) if small else XB(96)
    d.text((x + w / 2 - text_w(nf, name) / 2, y - (78 if small else 196)), name, font=nf, fill=TEXT2 if small else TEXT)
    for s in range(6):
        d.line((x + s * gx, y, x + s * gx, y + h), fill=TEXT3 + (255,), width=2 if small else 4)
    for f in range(5):
        d.line((x, y + f * gy, x + w, y + f * gy), fill=(TEXT if f == 0 else BORDER2) + (255,), width=(6 if small else 12) if f == 0 else (2 if small else 4))
    for s, c in enumerate(shape):
        cx = x + s * gx
        if c == 'x':
            o = 8 if small else 14
            d.line((cx - o, y - 3 * o, cx + o, y - o), fill=ROSE, width=3 if small else 5)
            d.line((cx + o, y - 3 * o, cx - o, y - o), fill=ROSE, width=3 if small else 5)
        elif c == '0':
            o = 8 if small else 15
            d.ellipse((cx - o, y - 3 * o, cx + o, y - o), outline=MINT, width=3 if small else 5)
        else:
            cy = y + (int(c) - 0.5) * gy
            d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=MINT)
            if not small:
                d.text((cx - text_w(B(36), fing[s]) / 2, cy - 22), fing[s], font=B(36), fill=BG)

def frame(t):
    img = BG_IMG.copy(); d = ImageDraw.Draw(img, 'RGBA')
    if t >= PLAY_END:
        u = ease((t - PLAY_END) / 0.35); a = int(255 * u)
        tag(d, (64, 170), 'TAB SCRIPTORIA')
        draw_lines(d, (64, 290), ['Made it to', ('130?', MINT)], XB(120), TEXT, lh=130)
        d.text((64, 580), 'Tell me your top speed.', font=SB(50), fill=TEXT2)
        d.rounded_rectangle((64, 860, 940, 1180), 30, fill=SURF + (int(240 * u),), outline=ACCENT + (a,), width=3)
        d.text((104, 895), 'Record your playing,', font=DB(48), fill=TEXT + (a,))
        d.text((104, 958), 'get tab with chord names.', font=SB(44), fill=TEXT2 + (a,))
        d.text((104, 1055), 'tabscriptoria.com', font=XB(72), fill=MINT + (a,))
        return img
    i = max(0, int(np.searchsorted(BT, t, side='right') - 1))
    bt, kind, si, ci, b = BEATS[i]
    draw_lines(d, (64, 180), ['Keep up?', ('3 speeds.', BLUE)], XB(96), TEXT, lh=104)
    bpm = SPEEDS[si]
    pill(d, (64, 410), f'{bpm} BPM', B(44), (AMBER if si == 2 else MINT if si == 0 else BLUE), BG, pad=(24, 12))
    d.text((64 + text_w(B(44), f'{bpm} BPM') + 80, 424), '  '.join(PROG), font=SB(42), fill=TEXT3)
    pulse = ease(1 - (t - bt) / 0.18) if t - bt < 0.18 else 0
    if kind == 'count':
        s = str(COUNT - b)
        f = XB(300)
        d.text((W / 2 - text_w(f, s) / 2, 740 - 20 * pulse), s, font=f, fill=TEXT)
        d.text((W / 2 - text_w(SB(46), 'get ready: G') / 2, 1120), 'get ready: G', font=SB(46), fill=TEXT2)
    else:
        name = PROG[ci]
        chord_box(d, 160, 750 - int(10 * pulse), name)
        nxt = PROG[(ci + 1) % len(PROG)]
        chord_box(d, 790, 790, nxt, w=120, h=130, small=True)
        d.text((770, 1040), 'next', font=SB(32), fill=TEXT3)
    # beat dots (2 per chord)
    for k in range(BPC):
        on = (kind == 'play' and k == b)
        cx = W / 2 - 50 + k * 100
        d.ellipse((cx - 20, 1360 - 20, cx + 20, 1360 + 20), fill=(MINT if on else SURF2) + (255,))
    return img

def pluck(freq, dur, rng, bright=0.5):
    n = int(dur * SR); p = max(2, int(SR / freq))
    buf = rng.uniform(-1, 1, p)
    buf = bright * buf + (1 - bright) * np.convolve(buf, np.ones(3) / 3, 'same')
    out = np.zeros(n); decay = 0.995
    for i in range(n):
        v = buf[i % p]; out[i] = v
        buf[i % p] = decay * 0.5 * (v + buf[(i + 1) % p])
    return out

def strum(voicing, dur, rng, gap=0.014):
    n = int(dur * SR); out = np.zeros(n); k = 0
    for s, c in enumerate(voicing):
        if c == 'x':
            continue
        f = 440 * 2 ** ((OPEN[s] + int(c) - 69) / 12)
        off = int(k * gap * SR); k += 1
        sig = pluck(f, dur - k * gap, rng) * (0.9 if s >= 3 else 0.7)
        out[off:off + len(sig)] += sig[: n - off]
    fade = int(0.04 * SR); out[-fade:] *= np.linspace(1, 0, fade)
    return out

def audio(path):
    rng = np.random.default_rng(5)
    n = int(T_TOTAL * SR); out = np.zeros(n)
    tt = lambda dur: np.arange(int(dur * SR)) / SR
    def add(t, sig):
        i = int(t * SR); out[i:i + len(sig)] += sig[: max(0, n - i)]
    click = np.sin(2 * np.pi * 2000 * tt(0.04)) * np.exp(-tt(0.04) * 110)
    ding = sum(np.sin(2 * np.pi * f * tt(0.6)) * a for f, a in ((988, 0.4), (1319, 0.25), (1976, 0.1))) * np.exp(-tt(0.6) * 7)
    for k, (bt, kind, si, ci, b) in enumerate(BEATS):
        nxt = BEATS[k + 1][0] if k + 1 < len(BEATS) else PLAY_END + 0.8
        add(bt, click * (0.35 if b == 0 else 0.2))
        if kind == 'play':
            add(bt, strum(SHAPE[PROG[ci]], nxt - bt + 0.02, rng) * (0.55 if b == 0 else 0.4))
    add(PLAY_END, ding * 0.3)
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
    if STILLS and i % 10 == 0:
        os.makedirs(STILLS, exist_ok=True); im.convert('RGB').resize((360, 640)).save(os.path.join(STILLS, f'{i // 10:03d}.jpg'))
enc.close()
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', vid, '-i', wav, '-map', '0:v', '-map', '1:a', '-c:v', 'copy',
                '-af', 'loudnorm=I=-14:TP=-1.5:LRA=11', '-ar', '44100', '-c:a', 'aac', '-b:a', '192k', '-shortest',
                '-movflags', '+faststart', OUT], check=True)
print('wrote', OUT, f'{T_TOTAL:.1f}s')
