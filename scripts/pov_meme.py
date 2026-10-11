"""POV meme: '20-second free transcriptions' -> 'then you find Tab Scriptoria', cut from Andrew's webcam clips.

Usage: python3 pov_meme.py CLIP_FRUSTRATED.mp4 CLIP_HAPPY.mp4 OUT.mp4 [--stills t1,t2]
The clips are silent 1280x720 webcam recordings; the post gets a Commercial Music Library track attached at
upload time, so this file only carries original sound effects.
"""
import os, sys, subprocess, tempfile, wave, math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from tslib import *

CLIP_A, CLIP_B, OUT = sys.argv[1], sys.argv[2], sys.argv[3]
SR = 44100

# (source clip, src_start, src_end, speed) in output order
SCENE1 = [('A', 2.10, 4.00, 1.0), ('A', 8.70, 9.90, 1.0), ('A', 17.20, 19.80, 1.0)]
SCENE2 = [('B', 2.30, 3.20, 1.0), ('B', 3.20, 3.90, 0.6), ('B', 3.90, 5.30, 1.0)]
S1_END = sum((e - s) / sp for _, s, e, sp in SCENE1)          # 5.7
FLASH = 0.25
S2_START = S1_END + FLASH
S2_END = S2_START + sum((e - s) / sp for _, s, e, sp in SCENE2)
END_T = S2_END
T_TOTAL = END_T + 2.6
CARD_T = 0.75                                                 # paywall pops in
THUMBS = S2_START + (3.20 - 2.30)                             # thumbs-up hold (slowed) in clip B

def load(path):
    p = subprocess.run(['ffmpeg', '-v', 'error', '-i', path, '-vf', 'fps=30,crop=720:720:280:0,scale=1080:1080:flags=lanczos',
                        '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'], stdout=subprocess.PIPE, check=True)
    n = len(p.stdout) // (1080 * BAND_H * 3)
    return np.frombuffer(p.stdout, np.uint8)[: n * 1080 * BAND_H * 3].reshape(n, BAND_H, 1080, 3)
BAND_Y, BAND_H = 560, 1080
FR = {'A': load(CLIP_A), 'B': load(CLIP_B)}

def src_frame(t):
    segs, t0 = (SCENE1, 0.0) if t < S1_END else (SCENE2, S2_START)
    tt = max(0.0, t - t0)
    for clip, s, e, sp in segs:
        d = (e - s) / sp
        if tt < d or (clip, s, e, sp) == segs[-1]:
            idx = int(min(e, s + tt * sp) * 30)
            arr = FR[clip][min(idx, len(FR[clip]) - 1)]
            return Image.fromarray(np.ascontiguousarray(arr), 'RGB'), clip, s + tt * sp
        tt -= d

UI = Image.open(os.path.join(ROOT, 'assets', 'ui', 'transcribe_form.jpg')).convert('RGB').crop((0, 240, 864, 1330))

def paywall_card():
    w, h = 820, 300
    im = Image.new('RGBA', (w + 80, h + 80), (0, 0, 0, 0))
    sh = Image.new('RGBA', im.size, (0, 0, 0, 0))
    ImageDraw.Draw(sh).rounded_rectangle((40, 50, 40 + w, 50 + h), 34, fill=(0, 0, 0, 170))
    im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(18)))
    d = ImageDraw.Draw(im)
    x0, y0 = 40, 40
    d.rounded_rectangle((x0, y0, x0 + w, y0 + h), 34, fill=(250, 250, 252))
    # lock icon
    d.rounded_rectangle((x0 + 40, y0 + 52, x0 + 92, y0 + 96), 8, fill=(30, 30, 36))
    d.arc((x0 + 48, y0 + 26, x0 + 84, y0 + 70), 180, 360, fill=(30, 30, 36), width=7)
    d.text((x0 + 116, y0 + 40), 'Free preview ended', font=XB(52), fill=(20, 20, 26))
    # progress bar stuck at 0:20
    by = y0 + 150
    d.rounded_rectangle((x0 + 40, by, x0 + w - 40, by + 16), 8, fill=(222, 222, 230))
    px = x0 + 40 + (w - 80) * (20 / 222)
    d.rounded_rectangle((x0 + 40, by, px, by + 16), 8, fill=(232, 72, 85))
    d.ellipse((px - 14, by - 6, px + 14, by + 22), fill=(232, 72, 85))
    d.text((x0 + 40, by + 30), '0:20', font=B(34), fill=(232, 72, 85))
    d.text((x0 + w - 40 - text_w(B(34), '3:42'), by + 30), '3:42', font=B(34), fill=(120, 120, 132))
    d.rounded_rectangle((x0 + 220, y0 + h - 76, x0 + w - 220, y0 + h - 22), 27, fill=(225, 225, 232))
    lab = 'Upgrade to continue'
    d.text((x0 + (w - text_w(SB(30), lab)) / 2, y0 + h - 68), lab, font=SB(30), fill=(110, 110, 122))
    return im
CARD = paywall_card()

def chip_im(text):
    f = B(40)
    tw = text_w(f, text)
    im = Image.new('RGBA', (tw + 110, 78), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle((0, 0, tw + 104, 72), 36, fill=BG + (225,), outline=MINT + (255,), width=3)
    d.ellipse((18, 18, 54, 54), fill=MINT)
    d.line((27, 36, 34, 44), fill=BG, width=5); d.line((34, 44, 46, 28), fill=BG, width=5)
    d.text((70, 13), text, font=f, fill=TEXT)
    return im
CHIPS = [(THUMBS - 0.1, chip_im('5 free minutes a month')), (THUMBS + 0.55, chip_im('whole recordings')),
         (THUMBS + 1.2, chip_im('tab + sheet music + fingerings'))]

def paste_a(base, im, xy, a=1.0):
    if a <= 0.01:
        return
    if a < 0.99:
        im = im.copy(); im.putalpha(im.getchannel('A').point(lambda v: int(v * a)))
    base.alpha_composite(im, (int(xy[0]), int(xy[1])))

def compose(t):
    img = background(seed=11 if t < S1_END else 12, glow=(232, 72, 85) if t < S1_END else MINT, glow2=ACCENT)
    d = ImageDraw.Draw(img, 'RGBA')
    tt = min(t, END_T - 1 / 30)
    if t < S1_END + FLASH / 2:
        fr, clip, st = src_frame(min(tt, S1_END - 1 / 30))
    else:
        fr, clip, st = src_frame(max(tt, S2_START))
    # punch-in on the frustrated gestures / gentle push-in on the happy scene
    z = 1.0
    if t < S1_END:
        if (2.45 <= st <= 3.6) or (8.95 <= st <= 9.7) or (17.4 <= st <= 19.6):
            z = 1.12
    else:
        z = 1.0 + 0.06 * min(1, max(0, (t - S2_START) / (S2_END - S2_START)))
    if z > 1.001:
        w2, h2 = int(1080 / z), int(BAND_H / z)
        fr = fr.crop(((1080 - w2) // 2, (BAND_H - h2) // 2, (1080 - w2) // 2 + w2, (BAND_H - h2) // 2 + h2)).resize((1080, BAND_H), Image.LANCZOS)
    img.paste(fr, (0, BAND_Y))
    d = ImageDraw.Draw(img, 'RGBA')
    d.line((0, BAND_Y, W, BAND_Y), fill=(255, 255, 255, 40), width=2)
    d.line((0, BAND_Y + BAND_H, W, BAND_Y + BAND_H), fill=(255, 255, 255, 40), width=2)
    if t < S1_END + FLASH / 2:
        y = draw_lines(d, (64, 250), ['pov: the tab apps'], XB(92), TEXT, lh=100)
        y = draw_lines(d, (64, y), ['only let you transcribe'], XB(80), TEXT, lh=90)
        draw_lines(d, (64, y), [('20 seconds', (255, 120, 132))], XB(92), (255, 120, 132), lh=100)
        if t >= CARD_T:
            k = ease((t - CARD_T) / 0.22)
            shake = 0
            if t - CARD_T < 0.35:
                shake = int(12 * math.sin((t - CARD_T) * 70) * (1 - (t - CARD_T) / 0.35))
            sc = 0.85 + 0.15 * k
            card = CARD.resize((int(CARD.width * sc), int(CARD.height * sc)), Image.LANCZOS)
            paste_a(img, card, ((W - card.width) / 2 + shake, BAND_Y + 380), k)
    else:
        y = draw_lines(d, (64, 250), ['then you find'], XB(84), TEXT, lh=94)
        draw_lines(d, (64, y), [('Tab Scriptoria', MINT)], XB(118), MINT, lh=126)
        for i, (t0, ch) in enumerate(CHIPS):
            if t >= t0:
                a = ease((t - t0) / 0.2)
                paste_a(img, ch, (40 - 30 * (1 - a), BAND_Y + 36 + i * 88), a)
    # flash transition
    if S1_END - 0.02 <= t < S2_START + 0.15:
        a = 1 - abs((t - (S1_END + FLASH / 2)) / (FLASH / 2 + 0.15))
        img.alpha_composite(Image.new('RGBA', (W, H), (255, 255, 255, int(255 * max(0, min(1, a))))))
    # end card
    if t >= END_T - 0.2:
        a = ease((t - (END_T - 0.2)) / 0.4)
        card = Image.new('RGBA', (W, H), BG + (248,)); dc = ImageDraw.Draw(card, 'RGBA')
        y = draw_lines(dc, (64, 250), ['Turn your own', 'recording into tab.'], XB(88), TEXT, lh=96)
        ui = UI.resize((620, int(UI.height * 620 / UI.width)), Image.LANCZOS)
        rounded_paste(card, ui.crop((0, 0, 620, 560)), (64, y + 36), radius=28)
        dc = ImageDraw.Draw(card, 'RGBA')
        dc.text((64, y + 36 + 560 + 40), 'tabscriptoria.com', font=XB(76), fill=MINT)
        dc.text((64, y + 36 + 560 + 132), 'Sign in for 5 free minutes a month', font=M(40), fill=TEXT2)
        paste_a(img, card, (0, 0), a)
    return img

# ---------- original sound effects ----------
def sfx_track(path):
    n = int(T_TOTAL * SR); out = np.zeros(n, np.float32)
    def add(t, sig):
        i = int(t * SR); out[i:i + len(sig)] += sig[: max(0, n - i)]
    tt = lambda d: np.arange(int(d * SR)) / SR
    # buzzer when the paywall pops
    x = tt(0.45); buzz = 0.32 * np.sign(np.sin(2 * np.pi * (140 - 30 * x) * x)) * np.exp(-x * 3)
    add(CARD_T, buzz)
    # whoosh into the flash
    x = tt(0.5); noise = np.random.default_rng(1).standard_normal(len(x)).astype(np.float32)
    k = np.exp(-((x - 0.3) / 0.12) ** 2); wh = 0.3 * np.convolve(noise, np.ones(30) / 30, 'same') * k
    add(S1_END - 0.25, wh)
    # bright ding on the thumbs up
    x = tt(1.2); ding = sum(a * np.sin(2 * np.pi * f * x) for f, a in ((1318.5, 0.25), (2637, 0.08), (1975.5, 0.06))) * np.exp(-x * 4)
    add(THUMBS, ding.astype(np.float32))
    # soft pop for each chip and the end card
    for t0, _ in CHIPS:
        x = tt(0.12); add(t0, (0.18 * np.sin(2 * np.pi * (660 + 900 * x) * x) * np.exp(-x * 30)).astype(np.float32))
    x = tt(0.6); add(END_T, (0.2 * np.sin(2 * np.pi * 880 * x) * np.exp(-x * 6)).astype(np.float32))
    out = np.clip(out, -1, 1)
    st = np.stack([out, out], 1)
    with wave.open(path, 'w') as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((st * 32767).astype(np.int16).tobytes())

def main():
    if '--stills' in sys.argv:
        for x in sys.argv[sys.argv.index('--stills') + 1].split(','):
            compose(float(x)).convert('RGB').save(OUT.replace('.mp4', f'_{float(x):05.2f}.jpg'), quality=88)
        return
    tmp = tempfile.mkdtemp()
    wav = os.path.join(tmp, 's.wav'); sfx_track(wav)
    silent = os.path.join(tmp, 'v.mp4'); enc = Encoder(silent)
    for i in range(int(round(T_TOTAL * FPS))):
        enc.write(compose(i / FPS))
    enc.close()
    mux(silent, wav, OUT)
    print('wrote', OUT, f'{T_TOTAL:.2f}s')

if __name__ == '__main__':
    main()
