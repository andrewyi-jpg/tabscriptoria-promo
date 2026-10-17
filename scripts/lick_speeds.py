"""Video: 'Play this lick. 3 speeds.' Original A minor pentatonic lick (box 1) shown as tab; each speed
gets a 2-beat count-in, then the lick in eighth notes at 70, 100 and 130 BPM with the current note lit.
Audio: original plucked-string synth + click. A CML track is attached at upload time (low volume).

Usage: python3 lick_speeds.py OUT.mp4 [STILLS_DIR]
"""
import os, sys, wave, subprocess, tempfile
import numpy as np
from PIL import ImageDraw
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from tslib import *

OUT = sys.argv[1]
STILLS = sys.argv[2] if len(sys.argv) > 2 else None
SR = 44100
OPEN = [64, 59, 55, 50, 45, 40]  # string 0 = high e ... 5 = low E
LICK = [(3, 7), (2, 5), (2, 7), (1, 5), (1, 8), (0, 5), (0, 8), (0, 5)]  # (string, fret), eighth notes
NAMES = ['A', 'C', 'D', 'E', 'G', 'A', 'C', 'A']
SPEEDS = [70, 100, 130]
COUNT = 2
TAIL = 0.5  # rest after each pass

# timeline: list of (start, kind, speed_idx, idx)
EV = []
t = 0.0
for si, bpm in enumerate(SPEEDS):
    beat = 60 / bpm
    for k in range(COUNT):
        EV.append((t, 'count', si, k)); t += beat
    for k in range(len(LICK)):
        EV.append((t, 'note', si, k)); t += beat / 2
    EV.append((t, 'rest', si, -1)); t += TAIL
PLAY_END = t
OUTRO = 2.8
T_TOTAL = PLAY_END + OUTRO
ET = np.array([e[0] for e in EV])

BG_IMG = background(141, glow=MINT, glow2=BLUE)

def tab_panel(d, y, lit):
    x0, x1 = 64, 950; gap = 66; top = y + 50
    d.rounded_rectangle((x0, y - 10, x1, top + 5 * gap + 50), 28, fill=BG2 + (240,), outline=BORDER + (255,), width=2)
    lx0, lx1 = x0 + 80, x1 - 30
    for i, nm in enumerate(STRINGS):
        yy = top + i * gap
        d.line((lx0 - 20, yy, lx1, yy), fill=BORDER2 + (255,), width=3)
        d.text((x0 + 26, yy - 18), nm, font=M(30), fill=TEXT3)
    step = (lx1 - lx0) / len(LICK); f = B(46)
    for c, (s, fr) in enumerate(LICK):
        cx = lx0 + (c + 0.5) * step; cy = top + s * gap
        tok = str(fr); tw = text_w(f, tok); on = c == lit
        pad = 16 if on else 11
        d.rounded_rectangle((cx - tw / 2 - pad, cy - 28 - (6 if on else 0), cx + tw / 2 + pad, cy + 28 + (6 if on else 0)), 14,
                            fill=(MINT if on else BG2) + (255,), outline=(TEXT if on else MINT) + (255,), width=3)
        d.text((cx - tw / 2, cy - 28), tok, font=f, fill=BG if on else MINT)
        nf = SB(32)
        d.text((cx - text_w(nf, NAMES[c]) / 2, top + 5 * gap + 64), NAMES[c], font=nf, fill=(AMBER if on else TEXT3))
    return top + 5 * gap + 120

def frame(t):
    img = BG_IMG.copy(); d = ImageDraw.Draw(img, 'RGBA')
    if t >= PLAY_END:
        u = ease((t - PLAY_END) / 0.4); a = int(255 * u)
        tag(d, (64, 170), 'TAB SCRIPTORIA')
        draw_lines(d, (64, 300), ['Which speed', ('broke you?', MINT)], XB(116), TEXT, lh=126)
        d.text((64, 600), 'Comment 70, 100 or 130.', font=SB(52), fill=TEXT2)
        d.rounded_rectangle((64, 900, 940, 1220), 30, fill=SURF + (int(240 * u),), outline=ACCENT + (a,), width=3)
        d.text((104, 935), 'Record your version.', font=DB(48), fill=TEXT + (a,))
        d.text((104, 1000), 'Get the tab back, slow it down.', font=SB(44), fill=TEXT2 + (a,))
        d.text((104, 1095), 'tabscriptoria.com', font=XB(72), fill=MINT + (a,))
        return img
    i = int(np.searchsorted(ET, t, side='right') - 1)
    _, kind, si, k = EV[i]
    draw_lines(d, (64, 190), ['Play this lick.', ('3 speeds.', MINT)], XB(100), TEXT, lh=110)
    for j, bpm in enumerate(SPEEDS):
        on = j == si
        pill(d, (64 + j * 250, 440), f'{bpm} BPM', B(38), (MINT if on else SURF2) + (255,), BG if on else TEXT3,
             pad=(22, 12), outline=None if on else BORDER2 + (255,))
    yb = tab_panel(d, 610, k if kind == 'note' else -1)
    if kind == 'count':
        s = str(k + 1)
        d.text((W / 2 - text_w(XB(130), s) / 2, yb + 10), s, font=XB(130), fill=AMBER)
    elif kind == 'note':
        d.text((W / 2 - text_w(SB(40), 'A minor pentatonic, box 1') / 2, yb + 40), 'A minor pentatonic, box 1', font=SB(40), fill=TEXT2)
    return img

def pluck(freq, dur, rng, bright=0.55):
    n = int(dur * SR); p = max(2, int(SR / freq))
    buf = rng.uniform(-1, 1, p)
    buf = bright * buf + (1 - bright) * np.convolve(buf, np.ones(3) / 3, 'same')
    out = np.zeros(n)
    for i in range(n):
        v = buf[i % p]; out[i] = v
        buf[i % p] = 0.996 * 0.5 * (v + buf[(i + 1) % p])
    return out

def audio(path):
    rng = np.random.default_rng(5)
    n = int(T_TOTAL * SR); out = np.zeros(n)
    tt = lambda dur: np.arange(int(dur * SR)) / SR
    def add(t, sig):
        i = int(t * SR); out[i:i + len(sig)] += sig[: max(0, n - i)]
    click = np.sin(2 * np.pi * 1500 * tt(0.04)) * np.exp(-tt(0.04) * 110)
    ding = sum(np.sin(2 * np.pi * f * tt(0.6)) * a for f, a in ((988, 0.4), (1319, 0.25), (1976, 0.1))) * np.exp(-tt(0.6) * 7)
    for (st, kind, si, k) in EV:
        if kind == 'count':
            add(st, click * 0.35)
        elif kind == 'note':
            s, fr = LICK[k]
            dur = 60 / SPEEDS[si] / 2 + (0.5 if k == len(LICK) - 1 else 0.06)
            sig = pluck(440 * 2 ** ((OPEN[s] + fr - 69) / 12), dur, rng)
            fade = int(0.03 * SR); sig[-fade:] *= np.linspace(1, 0, fade)
            add(st, sig * 0.6)
            if k % 2 == 0:
                add(st, click * 0.12)
    add(PLAY_END, ding * 0.3)
    out = out / max(1e-6, np.abs(out).max()) * 0.9
    stt = np.stack([out, out], 1)
    with wave.open(path, 'w') as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((stt * 32767).astype(np.int16).tobytes())

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
