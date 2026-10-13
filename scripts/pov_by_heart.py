"""POV video over a silent segment of Andrew's landscape clip: 'pov: you can play it by heart' -> 'record it once'.

Usage: python3 pov_by_heart.py CLIP.mp4 START_S DUR_S OUT.mp4 [--stills t1,t2,...]
The clip's own audio is dropped (silent hand footage); a Commercial Music Library track is attached at
upload time, so the file only carries a few original pops.
"""
import os, sys, subprocess, tempfile, wave
import numpy as np
from PIL import Image, ImageDraw
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from tslib import *

CLIP, START, DUR, OUT = sys.argv[1], float(sys.argv[2]), float(sys.argv[3]), sys.argv[4]
SR = 44100
CREDIT = 'Song: "Samba para Ti" by Fernando Perez'
BAND_Y, BAND_W, BAND_H = 600, 1080, 608
END_T = DUR
T_TOTAL = DUR + 3.0
BEATS = [(0.0, ['pov: you can play it', 'by heart'], 0),
         (DUR * 0.34, ['but it only exists', 'in your hands'], 1),
         (DUR * 0.68, ['skip a month', "and it's gone"], 1)]
VF = 'fps=30,crop=1707:960:213:120,scale=%d:%d:flags=lanczos' % (BAND_W, BAND_H)

def frames():
    p = subprocess.Popen(['ffmpeg', '-v', 'error', '-ss', str(START), '-t', str(DUR), '-i', CLIP, '-an', '-vf', VF,
                          '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'], stdout=subprocess.PIPE)
    n = BAND_W * BAND_H * 3
    last = None
    while True:
        b = p.stdout.read(n)
        if len(b) < n:
            break
        last = Image.frombytes('RGB', (BAND_W, BAND_H), b)
        yield last
    p.wait()
    while True:
        yield last

def chip_im(text):
    f = B(40); tw = text_w(f, text)
    im = Image.new('RGBA', (tw + 110, 78), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle((0, 0, tw + 104, 72), 36, fill=BG + (225,), outline=MINT + (255,), width=3)
    d.ellipse((18, 18, 54, 54), fill=MINT)
    d.line((27, 36, 34, 44), fill=BG, width=5); d.line((34, 44, 46, 28), fill=BG, width=5)
    d.text((70, 13), text, font=f, fill=TEXT)
    return im
CHIPS = [(END_T + 0.5, chip_im('tab + sheet music')), (END_T + 0.9, chip_im('chord names + fingerings'))]

def paste_a(base, im, xy, a=1.0):
    if a <= 0.01:
        return
    if a < 0.99:
        im = im.copy(); im.putalpha(im.getchannel('A').point(lambda v: int(v * a)))
    base.alpha_composite(im, (int(xy[0]), int(xy[1])))

BGS = {}
def compose(t, fr):
    beat = max(i for i, (t0, _, _) in enumerate(BEATS) if t >= t0)
    if beat not in BGS:
        BGS[beat] = background(seed=31 + beat, glow=ACCENT if beat == 0 else ROSE, glow2=MINT)
    img = BGS[beat].copy()
    # slow push-in across the segment
    z = 1.0 + 0.05 * min(1.0, t / DUR)
    w2, h2 = int(BAND_W / z), int(BAND_H / z)
    band = fr.crop(((BAND_W - w2) // 2, (BAND_H - h2) // 2, (BAND_W - w2) // 2 + w2, (BAND_H - h2) // 2 + h2)).resize((BAND_W, BAND_H), Image.LANCZOS)
    img.paste(band, (0, BAND_Y))
    d = ImageDraw.Draw(img, 'RGBA')
    d.line((0, BAND_Y, W, BAND_Y), fill=(255, 255, 255, 40), width=2)
    d.line((0, BAND_Y + BAND_H, W, BAND_Y + BAND_H), fill=(255, 255, 255, 40), width=2)
    if CREDIT:
        d.text((64, BAND_Y + BAND_H + 28), CREDIT, font=SB(34), fill=TEXT2)
    t0, lines, hi = BEATS[beat]
    a = 1.0 if beat == 0 else ease((t - t0) / 0.18)
    layer = Image.new('RGBA', (W, H), (0, 0, 0, 0)); dl = ImageDraw.Draw(layer)
    cols = [TEXT, ROSE if beat == 2 else (MINT if beat == 1 else TEXT)]
    y = 250
    for k, ln in enumerate(lines):
        y = draw_lines(dl, (64, y), [(ln, cols[k])], XB(88), cols[k], lh=100)
    paste_a(img, layer, (0, 20 * (1 - a)), a)
    if t >= END_T - 0.2:
        a = ease((t - (END_T - 0.2)) / 0.4)
        card = Image.new('RGBA', (W, H), BG + (248,)); dc = ImageDraw.Draw(card, 'RGBA')
        y = draw_lines(dc, (64, 250), ['Record it once.', ('Get the tab back.', MINT)], XB(92), TEXT, lh=104)
        for i, (tc, ch) in enumerate(CHIPS):
            if t >= tc:
                ca = ease((t - tc) / 0.2)
                paste_a(card, ch, (64 - 30 * (1 - ca), y + 70 + i * 100), ca)
        dc.text((64, y + 330), 'tabscriptoria.com', font=XB(84), fill=TEXT)
        dc.text((64, y + 440), 'Sign in for 5 free minutes a month', font=M(40), fill=TEXT2)
        paste_a(img, card, (0, 0), a)
    return img

def sfx_track(path):
    n = int(T_TOTAL * SR); out = np.zeros(n, np.float32)
    def add(t, sig):
        i = int(t * SR); out[i:i + len(sig)] += sig[: max(0, n - i)]
    tt = lambda d: np.arange(int(d * SR)) / SR
    for t0, _, _ in BEATS[1:]:
        x = tt(0.12); add(t0, (0.16 * np.sin(2 * np.pi * (520 + 700 * x) * x) * np.exp(-x * 30)).astype(np.float32))
    x = tt(1.0); add(END_T, (sum(a * np.sin(2 * np.pi * f * x) for f, a in ((1046.5, 0.22), (1568, 0.08))) * np.exp(-x * 4)).astype(np.float32))
    for tc, _ in CHIPS:
        x = tt(0.12); add(tc, (0.14 * np.sin(2 * np.pi * (660 + 900 * x) * x) * np.exp(-x * 30)).astype(np.float32))
    st = np.stack([out, out], 1)
    with wave.open(path, 'w') as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((np.clip(st, -1, 1) * 32767).astype(np.int16).tobytes())

def main():
    gen = frames()
    if '--stills' in sys.argv:
        want = sorted(float(x) for x in sys.argv[sys.argv.index('--stills') + 1].split(','))
        i = 0
        for t in want:
            while i <= int(min(t, DUR - 0.04) * FPS):
                fr = next(gen); i += 1
            compose(t, fr).convert('RGB').save(OUT.replace('.mp4', f'_{t:05.2f}.jpg'), quality=88)
        return
    tmp = tempfile.mkdtemp()
    wav = os.path.join(tmp, 's.wav'); sfx_track(wav)
    silent = os.path.join(tmp, 'v.mp4'); enc = Encoder(silent)
    fr = None
    for i in range(int(round(T_TOTAL * FPS))):
        t = i / FPS
        if t < DUR or fr is None:
            fr = next(gen)
        enc.write(compose(t, fr))
    enc.close()
    mux(silent, wav, OUT)
    print('wrote', OUT, f'{T_TOTAL:.2f}s')

if __name__ == '__main__':
    main()
