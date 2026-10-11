"""Video: '4 chords, 8 solos' - each bar of Am F C G is played by a different Solo ideas style.

Needs data/relay_AmFCG.json and data/audio/<style>.wav (idea.wav from tabscriptoria.com/ideas/<id>/idea.wav).
Usage: python3 solo_relay.py OUT.mp4 [--stills t1,t2]
"""
import json, os, sys, wave, subprocess, tempfile
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from tslib import *

D = json.load(open(os.path.join(ROOT, 'data', 'relay_AmFCG.json')))
BAR = D['bar']; CHORDS = D['chords']; RELAY = D['relay']
NB = len(RELAY)
TAIL = 1.9
T_END = NB * BAR
T_TOTAL = T_END + TAIL
STYLE_COL = {'blues': BLUE, 'metal': ROSE, 'melodic': MINT, 'flamenco': AMBER, 'funk': (255, 172, 112),
             'jazz': ACCENT2, 'classical': (226, 232, 246), 'arpeggio': (110, 214, 255)}

# ---------- notes on the global timeline ----------
NOTES = []  # (start, dur, string, fret, style, bar_index)
for i, (st, k) in enumerate(RELAY):
    for n in D['styles'][st]['notes']:
        s, du, _, string, fr = n
        if k * BAR - 0.02 <= s < (k + 1) * BAR - 0.02:
            NOTES.append((i * BAR + (s - k * BAR), min(du, (k + 1) * BAR - s), string, fr, st, i))
# tail: first notes of the melodic idea (resolution on Am)
for n in D['styles']['melodic']['notes']:
    if n[0] < TAIL - 0.3:
        NOTES.append((T_END + n[0], min(n[1], TAIL), n[3], n[4], 'melodic', NB))

# ---------- audio ----------
def read_wav(p):
    with wave.open(p) as w:
        sr = w.getframerate(); x = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32) / 32768
        if w.getnchannels() == 2:
            x = x.reshape(-1, 2).mean(1)
    return sr, x

def build_audio(path):
    segs, sr = [], None
    fade = 0.025
    for i, (st, k) in enumerate(RELAY):
        sr, x = read_wav(os.path.join(ROOT, 'data', 'audio', f'{st}.wav'))
        a, b = int(k * BAR * sr), int((k + 1) * BAR * sr)
        seg = x[a:b + int(fade * sr)].copy()
        segs.append(seg)
    sr, mel = read_wav(os.path.join(ROOT, 'data', 'audio', 'melodic.wav'))
    tail = mel[: int(TAIL * sr)].copy()
    env = np.ones_like(tail); n_f = int(1.2 * sr); env[-n_f:] = np.linspace(1, 0, n_f) ** 1.5
    tail *= env
    segs.append(tail)
    out = np.zeros(int(T_TOTAL * sr) + int(fade * sr) + 10, np.float32)
    nf = int(fade * sr)
    for i, seg in enumerate(segs):
        start = int(i * BAR * sr)
        s = seg.copy()
        if i > 0:
            s[:nf] *= np.linspace(0, 1, nf)
        if i < len(segs) - 1:
            s[-nf:] *= np.linspace(1, 0, nf)
        out[start:start + len(s)] += s[: len(out) - start]
    out = out[: int(T_TOTAL * sr)]
    out /= max(1e-6, np.abs(out).max()) / 0.9
    with wave.open(path, 'w') as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(sr)
        w.writeframes((out * 32767).astype(np.int16).tobytes())

# ---------- drawing ----------
PANEL = (40, 1010, 1040, 1420)
STR_Y0 = 1110; STR_GAP = 50
PLAY_X = 290; PPS = 275.0
NX0, NX1 = 92, 1020
SPR = {}
def fret_sprite(fr, col, active):
    key = (fr, col, active)
    if key in SPR:
        return SPR[key]
    f = B(30); t = str(fr); tw = text_w(f, t)
    pw = max(42, tw + 22); ph = 42; pad = 16
    im = Image.new('RGBA', (pw + 2 * pad, ph + 2 * pad), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    if active:
        g = Image.new('RGBA', im.size, (0, 0, 0, 0))
        ImageDraw.Draw(g).rounded_rectangle((pad - 7, pad - 7, pad + pw + 7, pad + ph + 7), 26, fill=col + (170,))
        im.alpha_composite(g.filter(ImageFilter.GaussianBlur(8)))
    d.rounded_rectangle((pad, pad, pad + pw, pad + ph), ph // 2, fill=col)
    d.text((pad + (pw - tw) / 2, pad + 4), t, font=f, fill=BG)
    if active:
        im = im.resize((int(im.width * 1.15), int(im.height * 1.15)), Image.LANCZOS)
    SPR[key] = im
    return im

BGS = {}
def bg_for(st):
    if st not in BGS:
        BGS[st] = background(seed=hash(st) % 997, glow=STYLE_COL[st], glow2=ACCENT)
    return BGS[st]

PANEL_IM = None
def panel_im():
    global PANEL_IM
    if PANEL_IM is None:
        im = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
        d.rounded_rectangle(PANEL, 28, fill=BG2 + (240,), outline=BORDER + (255,), width=2)
        d.text((72, 1030), 'TAB', font=SB(24), fill=TEXT3)
        lab = 'Tab Scriptoria  ·  Solo ideas'
        d.text((PANEL[2] - 34 - text_w(SB(24), lab), 1030), lab, font=SB(24), fill=TEXT3)
        for i, nm in enumerate(STRINGS):
            y = STR_Y0 + i * STR_GAP
            d.line((NX0, y, NX1, y), fill=BORDER2 + (255,), width=2)
            d.text((62, y - 15), nm, font=M(26), fill=TEXT3)
        PANEL_IM = im
    return PANEL_IM

def paste_a(base, im, xy, a=1.0):
    if a <= 0.01:
        return
    if a < 0.99:
        im = im.copy(); im.putalpha(im.getchannel('A').point(lambda v: int(v * a)))
    base.alpha_composite(im, (int(xy[0]), int(xy[1])))

def compose(t):
    bi = min(NB - 1, int(t / BAR))
    st = RELAY[bi][0] if t < T_END else 'melodic'
    col = STYLE_COL[st]
    img = bg_for(st).copy()
    d = ImageDraw.Draw(img, 'RGBA')
    # --- hook (first 2 bars), then running title ---
    if t < 2 * BAR:
        tag(d, (64, 150), 'TAB SCRIPTORIA  ·  SOLO IDEAS')
        y = draw_lines(d, (64, 215), ['Same 4 chords.'], XB(92), TEXT, lh=100)
        draw_lines(d, (64, y), [('8 solos to learn.', MINT)], XB(92), MINT, lh=100)
    else:
        draw_lines(d, (64, 205), ['Same 4 chords,'], XB(78), TEXT, lh=86)
        draw_lines(d, (64, 291), [('8 solos to learn', MINT)], XB(78), MINT, lh=86)
    # --- chord strip ---
    cur = bi % 4 if t < T_END else 0
    cx0, cy0, cw, chh, gap = 64, 440, 205, 118, 22
    for i, c in enumerate(CHORDS):
        x = cx0 + i * (cw + gap)
        on = (i == cur)
        d.rounded_rectangle((x, cy0, x + cw, cy0 + chh), 24, fill=(col + (235,)) if on else (SURF + (230,)),
                            outline=(col + (255,)) if on else (BORDER2 + (255,)), width=3)
        f = XB(64)
        d.text((x + (cw - text_w(f, c)) / 2, cy0 + 20), c, font=f, fill=BG if on else TEXT2)
        if on and t < T_END:
            p = (t - bi * BAR) / BAR
            d.rounded_rectangle((x + 16, cy0 + chh - 14, x + 16 + (cw - 32) * p, cy0 + chh - 8), 3, fill=BG + (200,))
    # --- style label ---
    if t < T_END:
        tb = t - bi * BAR
        a = ease(tb / 0.18)
        label = D['styles'][st]['label'].upper()
        f = XB(120)
        lab_im = Image.new('RGBA', (1000, 150), (0, 0, 0, 0))
        dl = ImageDraw.Draw(lab_im)
        dl.text((2, 4), label, font=f, fill=(0, 0, 0, 160)); dl.text((0, 0), label, font=f, fill=col)
        paste_a(img, lab_im, (64 - 40 * (1 - a), 650), a)
        d = ImageDraw.Draw(img, 'RGBA')
        cnt = f'{bi + 1}/{NB}'
        d.text((64, 800), f'solo style {cnt}', font=SB(36), fill=TEXT3)
    else:
        pass
    # --- tab panel ---
    img.alpha_composite(panel_im())
    lay = Image.new('RGBA', (W, H), (0, 0, 0, 0)); dl = ImageDraw.Draw(lay, 'RGBA')
    t_lo, t_hi = t - (PLAY_X - NX0) / PPS - 0.3, t + (NX1 - PLAY_X) / PPS + 0.3
    vis = [n for n in NOTES if n[0] < t_hi and n[0] + n[1] > t_lo]
    for (s, du, string, fr, sty, b) in vis:
        y = STR_Y0 + string * STR_GAP
        xa = max(NX0, PLAY_X + (s - t) * PPS); xb = min(NX1, PLAY_X + (s + du - t) * PPS)
        if xb > xa:
            dl.rounded_rectangle((xa, y - 5, xb, y + 5), 5, fill=STYLE_COL[sty] + (70 if s + du < t else 120,))
    # bar lines (scrolling)
    for b in range(NB + 1):
        xb = PLAY_X + (b * BAR - t) * PPS
        if NX0 < xb < NX1:
            dl.line((xb, STR_Y0 - 14, xb, STR_Y0 + 5 * STR_GAP + 14), fill=TEXT3 + (120,), width=2)
    for wdt, a_ in ((20, 30), (10, 70), (4, 255)):
        dl.line((PLAY_X, STR_Y0 - 30, PLAY_X, STR_Y0 + 5 * STR_GAP + 30), fill=ACCENT + (a_,), width=wdt)
    img.alpha_composite(lay)
    for (s, du, string, fr, sty, b) in sorted(vis, key=lambda n: -n[0]):
        x = PLAY_X + (s - t) * PPS
        if x < NX0 - 10 or x > NX1 + 10:
            continue
        active = s <= t < s + max(du, 0.12)
        spr = fret_sprite(fr, STYLE_COL[sty], active)
        a = 0.35 if t >= s + max(du, 0.12) else 1.0
        if x < NX0 + 50: a *= max(0, (x - NX0 + 10) / 60)
        if x > NX1 - 80: a *= max(0, (NX1 + 10 - x) / 90)
        paste_a(img, spr, (x - spr.width / 2, STR_Y0 + string * STR_GAP - spr.height / 2), a)
    d = ImageDraw.Draw(img, 'RGBA')
    d.text((64, 1450), 'App playback  ·  solo ideas written by Tab Scriptoria', font=SB(32), fill=TEXT3)
    # --- end card ---
    if t > T_END - 0.25:
        a = ease((t - (T_END - 0.25)) / 0.45)
        ov = Image.new('RGBA', (W, H), BG + (int(250 * a),))
        img.alpha_composite(ov)
        card = Image.new('RGBA', (W, H), (0, 0, 0, 0)); dc = ImageDraw.Draw(card, 'RGBA')
        y = draw_lines(dc, (64, 300), ['Type your chords.', 'Pick a style.'], XB(92), TEXT, lh=100)
        y = draw_lines(dc, (64, y), [('Get a solo you', MINT), ('can actually learn.', MINT)], XB(92), MINT, lh=100)
        ui = Image.open(os.path.join(ROOT, 'assets', 'ui', 'solo_form.jpg')).convert('RGB').crop((0, 140, 540, 760))
        ui = ui.resize((470, int(620 * 470 / 540)), Image.LANCZOS)
        rounded_paste(card, ui, (64, y + 40), radius=26)
        dc = ImageDraw.Draw(card, 'RGBA')
        yb = y + 40 + ui.height + 46
        dc.text((64, yb), 'tabscriptoria.com', font=XB(70), fill=TEXT)
        dc.text((64, yb + 86), 'Solo ideas  ·  8 styles  ·  backing tracks', font=M(38), fill=TEXT2)
        paste_a(img, card, (0, 0), a)
    return img

def main():
    out = sys.argv[1]
    if '--stills' in sys.argv:
        ts = [float(x) for x in sys.argv[sys.argv.index('--stills') + 1].split(',')]
        for tt in ts:
            compose(tt).convert('RGB').save(out.replace('.mp4', f'_{tt:05.2f}.jpg'), quality=88)
        return
    tmp = tempfile.mkdtemp()
    wav = os.path.join(tmp, 'a.wav'); build_audio(wav)
    norm = os.path.join(tmp, 'n.wav')
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', wav, '-af', 'loudnorm=I=-14:TP=-1.5:LRA=11', '-ar', '44100', '-ac', '2', norm], check=True)
    silent = os.path.join(tmp, 'v.mp4')
    enc = Encoder(silent)
    n = int(round(T_TOTAL * FPS))
    for i in range(n):
        enc.write(compose(i / FPS))
    enc.close()
    mux(silent, norm, out)
    print('wrote', out, f'{T_TOTAL:.2f}s')

if __name__ == '__main__':
    main()
