"""Video: 'Can you tab this by ear? 3 levels.' Each level plays a short original melody twice
(plucked-string synth), gives a countdown, then replays it while the tab fills in.
A Commercial Music Library track is attached at upload time (low volume under the melody).

Usage: python3 ear_tab.py OUT.mp4 [STILLS_DIR]
"""
import os, sys, wave, subprocess, tempfile
import numpy as np
from PIL import ImageDraw
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from tslib import *

OUT = sys.argv[1]
STILLS = sys.argv[2] if len(sys.argv) > 2 else None
SR = 44100
OPEN = [64, 59, 55, 50, 45, 40]  # string index 0 = high e ... 5 = low E

# (label, colour, hint, step seconds, [(string, token)])  - original melodies
LEVELS = [
    ('EASY', MINT, 'B string only. Starts open.', 0.5, [(1, '0'), (1, '1'), (1, '3'), (1, '5')]),
    ('MEDIUM', AMBER, 'G and B strings. Ends open.', 0.42, [(2, '2'), (1, '0'), (1, '1'), (2, '2'), (2, '0')]),
    ('HARD', ROSE, 'Top 3 strings + 1 hammer-on.', 0.4, [(0, '3'), (0, '0'), (1, '3'), (1, '1h3'), (2, '2')]),
]

def events(level):
    """-> list of (t_offset, midi, legato, col_index)"""
    _, _, _, step, notes = level
    ev = []; t = 0.0
    for c, (s, tok) in enumerate(notes):
        if 'h' in tok:
            a, b = tok.split('h')
            ev.append((t, OPEN[s] + int(a), False, c)); ev.append((t + step * 0.5, OPEN[s] + int(b), True, c))
        else:
            ev.append((t, OPEN[s] + int(tok), False, c))
        t += step
    return ev, t

LEAD = 0.25; GAP = 0.55; THINK = 2.0; HOLD = 0.9
def plan(level):
    _, mel = events(level)
    p1 = LEAD; p2 = p1 + mel + GAP; th = p2 + mel + 0.2; rv = th + THINK; end = rv + mel + HOLD
    return dict(p1=p1, p2=p2, th=th, rv=rv, end=end, mel=mel)
PLANS = [plan(l) for l in LEVELS]
STARTS = np.cumsum([0] + [p['end'] for p in PLANS])
OUTRO = 3.8
T_TOTAL = STARTS[-1] + OUTRO

BG_IMG = background(101, glow=MINT, glow2=ACCENT)

def tab_panel(d, y, notes, shown, playing=None):
    x0, x1 = 64, 950; gap = 64; top = y + 50
    d.rounded_rectangle((x0, y - 10, x1, top + 5 * gap + 50), 28, fill=BG2 + (240,), outline=BORDER + (255,), width=2)
    lx0, lx1 = x0 + 80, x1 - 40
    for i, nm in enumerate(STRINGS):
        yy = top + i * gap
        d.line((lx0 - 20, yy, lx1, yy), fill=BORDER2 + (255,), width=3)
        d.text((x0 + 26, yy - 18), nm, font=M(30), fill=TEXT3)
    n = len(notes); step = (lx1 - lx0) / n
    f = B(44)
    for c, (s, tok) in enumerate(notes):
        cx = lx0 + (c + 0.5) * step
        if c < shown:
            tw = sum(text_w(f, ch) for ch in tok)
            cy = top + s * gap
            d.rounded_rectangle((cx - tw / 2 - 12, cy - 28, cx + tw / 2 + 12, cy + 28), 14, fill=BG2 + (255,),
                                outline=(TEXT if c == playing else MINT) + (255,), width=3)
            xx = cx - tw / 2
            for ch in tok:
                d.text((xx, cy - 27), ch, font=f, fill=AMBER if ch == 'h' else MINT)
                xx += text_w(f, ch)
    return top + 5 * gap + 50, step, lx0

def slots(d, y, n, lit, step, lx0):
    for c in range(n):
        cx = lx0 + (c + 0.5) * step
        on = c in lit
        d.ellipse((cx - 30, y - 30, cx + 30, y + 30), fill=(AMBER if on else SURF2) + (255,), outline=BORDER2 + (255,), width=2)
        d.text((cx - text_w(B(34), '?') / 2, y - 21), '?', font=B(34), fill=BG if on else TEXT3)

def frame(t):
    img = BG_IMG.copy(); d = ImageDraw.Draw(img, 'RGBA')
    if t >= STARTS[-1]:
        u = ease((t - STARTS[-1]) / 0.4); a = int(255 * u)
        tag(d, (64, 170), 'TAB SCRIPTORIA')
        draw_lines(d, (64, 300), ['Which level', ('got you?', MINT)], XB(120), TEXT, lh=130)
        d.text((64, 600), 'Comment 1, 2 or 3.', font=SB(52), fill=TEXT2)
        d.rounded_rectangle((64, 900, 940, 1220), 30, fill=SURF + (int(240 * u),), outline=ACCENT + (a,), width=3)
        d.text((104, 935), 'Can\'t hear it? Record it.', font=DB(48), fill=TEXT + (a,))
        d.text((104, 1000), 'Tab Scriptoria writes the tab.', font=SB(44), fill=TEXT2 + (a,))
        d.text((104, 1095), 'tabscriptoria.com', font=XB(72), fill=MINT + (a,))
        return img
    r = int(np.searchsorted(STARTS, t, side='right') - 1)
    tt = t - STARTS[r]; P = PLANS[r]; lab, col, hint, step, notes = LEVELS[r]
    ev, _ = events(LEVELS[r])
    if r == 0:
        draw_lines(d, (64, 190), ['Can you tab this', ('by ear?', MINT)], XB(96), TEXT, lh=106)
    else:
        pill(d, (64, 200), f'LEVEL {r + 1} OF 3', B(36), SURF2 + (255,), TEXT2, pad=(22, 11), outline=BORDER2 + (255,))
        d.text((64, 290), 'Tab it by ear.', font=XB(84), fill=TEXT)
    pill(d, (64, 440), lab, B(40), col, BG, pad=(24, 12))
    d.text((64 + text_w(B(40), lab) + 80, 452), hint, font=SB(40), fill=TEXT2)
    # which phase
    def cols_played(t0):
        return {c for (o, m, lg, c) in ev if t0 + o <= tt}
    if tt < P['p2']:
        status, lit, shown, playing = 'LISTEN  1/2', (cols_played(P['p1']) if tt < P['p1'] + P['mel'] + 0.1 else set()), 0, None
    elif tt < P['th']:
        status, lit, shown, playing = 'LISTEN  2/2', cols_played(P['p2']), 0, None
    elif tt < P['rv']:
        status, lit, shown, playing = 'YOUR GUESS...', set(), 0, None
    else:
        played = cols_played(P['rv'])
        status, lit, shown = 'ANSWER', set(), len(played)
        playing = max(played) if played and tt < P['rv'] + P['mel'] else None
    yb, stp, lx0 = tab_panel(d, 720, notes, shown, playing)
    slots(d, 625, len(notes), lit, stp, lx0)
    sc = MINT if status == 'ANSWER' else (AMBER if status.startswith('YOUR') else TEXT)
    d.text((W / 2 - text_w(XB(70), status) / 2, yb + 70), status, font=XB(70), fill=sc)
    if P['th'] <= tt < P['rv']:
        left = (P['rv'] - tt) / THINK
        d.rounded_rectangle((W / 2 - 300, yb + 180, W / 2 - 300 + 600 * left, yb + 194), 7, fill=AMBER)
    return img

# ---------- audio ----------
def pluck(freq, dur, rng, bright=0.5, decay=0.996):
    n = int(dur * SR); p = max(2, int(SR / freq))
    buf = rng.uniform(-1, 1, p)
    buf = bright * buf + (1 - bright) * np.convolve(buf, np.ones(3) / 3, 'same')
    out = np.zeros(n)
    for i in range(n):
        v = buf[i % p]; out[i] = v
        buf[i % p] = decay * 0.5 * (v + buf[(i + 1) % p])
    return out

def melody(level, rng):
    ev, mel = events(level)
    n = int((mel + 1.2) * SR); out = np.zeros(n)
    for k, (o, m, legato, c) in enumerate(ev):
        nxt = ev[k + 1][0] if k + 1 < len(ev) else mel + 1.0
        dur = nxt - o + 0.03
        sig = pluck(440 * 2 ** ((m - 69) / 12), dur, rng, bright=0.25 if legato else 0.55) * (0.6 if legato else 1.0)
        fade = int(0.03 * SR); sig[-fade:] *= np.linspace(1, 0, fade)
        i = int(o * SR); out[i:i + len(sig)] += sig[: n - i]
    return out

def audio(path):
    rng = np.random.default_rng(7)
    n = int(T_TOTAL * SR); out = np.zeros(n)
    tt = lambda dur: np.arange(int(dur * SR)) / SR
    def add(t, sig):
        i = int(t * SR); out[i:i + len(sig)] += sig[: max(0, n - i)]
    ding = sum(np.sin(2 * np.pi * f * tt(0.6)) * a for f, a in ((988, 0.4), (1319, 0.25), (1976, 0.1))) * np.exp(-tt(0.6) * 7)
    tick = np.sin(2 * np.pi * 1800 * tt(0.05)) * np.exp(-tt(0.05) * 90)
    for r, lv in enumerate(LEVELS):
        P = PLANS[r]; s0 = STARTS[r]
        mel = melody(lv, rng)
        for key in ('p1', 'p2', 'rv'):
            add(s0 + P[key], mel * 0.6)
        for k in range(2):
            add(s0 + P['th'] + k * 1.0, tick * 0.25)
        add(s0 + P['rv'] - 0.05, ding * 0.25)
    add(STARTS[-1], ding * 0.3)
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
