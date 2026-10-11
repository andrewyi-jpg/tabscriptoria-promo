"""Shared brand + drawing helpers for Tab Scriptoria promo videos and carousels.

Everything renders at 1080x1920 (TikTok 9:16). Colors come from tabscriptoria.com's :root tokens.
"""
import os, subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
W, H, FPS = 1080, 1920, 30

# --- brand tokens ---
BG = (8, 12, 22); BG2 = (12, 18, 32); SURF = (17, 26, 44); SURF2 = (22, 33, 58)
BORDER = (34, 48, 77); BORDER2 = (48, 65, 104)
TEXT = (238, 242, 251); TEXT2 = (185, 196, 220); TEXT3 = (134, 147, 176)
ACCENT = (157, 139, 255); ACCENT2 = (184, 169, 255)
MINT = (127, 227, 196); BLUE = (143, 184, 255); AMBER = (243, 198, 119); ROSE = (255, 143, 171)

# TikTok safe area (keep text inside): top status/tabs, right action rail, bottom caption band
SAFE = dict(top=150, left=64, right=W - 150, bottom=H - 380)

_FONT_DIRS = [os.path.join(ROOT, 'assets', 'fonts'), '/usr/share/fonts/opentype/inter']
_font_cache = {}
def font(name, size):
    key = (name, size)
    if key not in _font_cache:
        for d in _FONT_DIRS:
            p = os.path.join(d, name)
            if os.path.exists(p):
                _font_cache[key] = ImageFont.truetype(p, size)
                break
        else:
            _font_cache[key] = ImageFont.truetype('DejaVuSans-Bold.ttf', size)
    return _font_cache[key]

def XB(s): return font('InterDisplay-ExtraBold.otf', s)
def DB(s): return font('InterDisplay-Bold.otf', s)
def B(s): return font('Inter-Bold.otf', s)
def SB(s): return font('Inter-SemiBold.otf', s)
def M(s): return font('Inter-Medium.otf', s)

def clean(s):
    """Inter Display lacks the musical sharp/flat glyphs; use ASCII."""
    return s.replace('♯', '#').replace('♭', 'b')

def ease(x):
    x = max(0.0, min(1.0, x)); return x * x * (3 - 2 * x)

def text_w(f, s):
    return f.getbbox(s)[2]

def wrap(f, text, maxw):
    words, lines, cur = text.split(), [], ''
    for w_ in words:
        t = (cur + ' ' + w_).strip()
        if text_w(f, t) <= maxw or not cur:
            cur = t
        else:
            lines.append(cur); cur = w_
    if cur:
        lines.append(cur)
    return lines

def draw_lines(d, xy, lines, f, fill, lh=None, shadow=True, align='left', maxw=None):
    """lines: list of str or (str, color). Returns y after the block."""
    x, y = xy
    lh = lh or int(f.size * 1.12)
    for ln in lines:
        txt, col = (ln, fill) if isinstance(ln, str) else ln
        tx = x
        if align == 'center' and maxw:
            tx = x + (maxw - text_w(f, txt)) / 2
        if shadow:
            d.text((tx + 2, y + 3), txt, font=f, fill=(0, 0, 0, 150))
        d.text((tx, y), txt, font=f, fill=col)
        y += lh
    return y

def background(seed=0, glow=ACCENT, glow2=MINT):
    """Dark brand background with two soft color glows (varies by seed so slides don't look identical)."""
    rng = np.random.default_rng(seed)
    im = Image.new('RGB', (W, H), BG)
    g = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(g)
    cx, cy = int(rng.uniform(-100, 400)), int(rng.uniform(-200, 300))
    d.ellipse((cx - 650, cy - 650, cx + 650, cy + 650), fill=glow + (46,))
    cx2, cy2 = int(rng.uniform(700, 1200)), int(rng.uniform(1300, 1900))
    d.ellipse((cx2 - 600, cy2 - 600, cx2 + 600, cy2 + 600), fill=glow2 + (26,))
    g = g.filter(ImageFilter.GaussianBlur(160))
    im = Image.alpha_composite(im.convert('RGBA'), g)
    return im

def pill(d, xy, text, f, fill, txt_col, pad=(22, 10), radius=None, outline=None):
    x, y = xy
    tw = text_w(f, text)
    h = f.size + pad[1] * 2
    r = radius if radius is not None else h // 2
    box = (x, y, x + tw + pad[0] * 2, y + h)
    d.rounded_rectangle(box, r, fill=fill, outline=outline, width=2 if outline else 0)
    d.text((x + pad[0], y + pad[1] - 2), text, font=f, fill=txt_col)
    return box

def tag(d, xy, text, color=TEXT):
    return pill(d, xy, text, B(28), (46, 38, 92), color, pad=(18, 9), outline=ACCENT + (190,))

def rounded_paste(base, im, xy, radius=28, border=BORDER2, shadow=True):
    w, h = im.size
    m = Image.new('L', (w, h), 0)
    ImageDraw.Draw(m).rounded_rectangle((0, 0, w - 1, h - 1), radius, fill=255)
    if shadow:
        sh = Image.new('RGBA', (w + 120, h + 120), (0, 0, 0, 0))
        ImageDraw.Draw(sh).rounded_rectangle((60, 70, 60 + w, 70 + h), radius, fill=(0, 0, 0, 170))
        sh = sh.filter(ImageFilter.GaussianBlur(28))
        base.alpha_composite(sh, (int(xy[0]) - 60, int(xy[1]) - 60))
    tile = im.convert('RGBA'); tile.putalpha(m)
    base.alpha_composite(tile, (int(xy[0]), int(xy[1])))
    ImageDraw.Draw(base).rounded_rectangle((xy[0], xy[1], xy[0] + w - 1, xy[1] + h - 1), radius, outline=border, width=2)

# ---------- static tab (for carousels / stills) ----------
STRINGS = ['e', 'B', 'G', 'D', 'A', 'E']

def fret_pill(d, cx, cy, fret, col=MINT, size=34, ring=None, hollow=False):
    f = B(size)
    t = str(fret)
    tw = text_w(f, t)
    pw = max(size + 8, tw + 20); ph = size + 10
    box = (cx - pw / 2, cy - ph / 2, cx + pw / 2, cy + ph / 2)
    if hollow:
        d.rounded_rectangle(box, ph / 2, fill=BG2 + (255,), outline=col, width=4)
        d.text((cx - tw / 2, cy - ph / 2 + 3), t, font=f, fill=col)
    else:
        d.rounded_rectangle(box, ph / 2, fill=col)
        d.text((cx - tw / 2, cy - ph / 2 + 3), t, font=f, fill=BG)
    if ring:
        d.rounded_rectangle((box[0] - 6, box[1] - 6, box[2] + 6, box[3] + 6), ph / 2 + 6, outline=ring, width=4)

def draw_tab_row(img, box, notes, t0, t1, bars, chords, labels=None, roles=None, sustain=True,
                 str_gap=46, fret_size=30, chord_font=None, label_font=None):
    """Draw one tab row covering [t0, t1) seconds.
    notes: list of (start, dur, pitch, string, fret, [extra]) ; bars: list of bar start times (incl. t1 as end)
    chords: list of (start, label) ; labels: per-note text under the staff (same order as notes)
    roles: per-note 'T' (target, ring), 'A' (approach, hollow) or ''."""
    d = ImageDraw.Draw(img, 'RGBA')
    x0, y0, x1, _ = box
    chord_font = chord_font or DB(46)
    label_font = label_font or SB(26)
    top = y0 + 70
    # panel
    d.rounded_rectangle((x0 - 24, y0 - 10, x1 + 24, top + 5 * str_gap + 80 + (40 if labels else 0)), 26,
                        fill=BG2 + (235,), outline=BORDER + (255,), width=2)
    for i, nm in enumerate(STRINGS):
        y = top + i * str_gap
        d.line((x0 + 34, y, x1, y), fill=BORDER2 + (255,), width=2)
        d.text((x0, y - 15), nm, font=M(26), fill=TEXT3)
    span = t1 - t0
    X = lambda t: x0 + 60 + (t - t0) / span * (x1 - x0 - 80)
    # bar lines + chord names
    for b in bars:
        if t0 - 1e-6 <= b <= t1 + 1e-6:
            xb = X(b) - 20 if b > t0 + 1e-6 else x0 + 34
            d.line((xb, top, xb, top + 5 * str_gap), fill=TEXT3 + (200,), width=3)
    for (cs, lab) in chords:
        if t0 - 1e-6 <= cs < t1 - 1e-6:
            d.text((X(cs) - 8, y0 + 2), clean(lab), font=chord_font, fill=ACCENT2)
    # sustain bars
    for idx, n in enumerate(notes):
        s, du, _, st, fr = n[:5]
        if not (t0 - 0.02 <= s < t1 - 0.02):
            continue
        if sustain:
            y = top + st * str_gap
            d.rounded_rectangle((X(s), y - 5, min(X(s + du), x1), y + 5), 5, fill=MINT + (90,))
    for idx, n in enumerate(notes):
        s, du, _, st, fr = n[:5]
        if not (t0 - 0.02 <= s < t1 - 0.02):
            continue
        y = top + st * str_gap
        role = roles[idx] if roles else ''
        if role == 'A':
            fret_pill(d, X(s), y, fr, col=AMBER, size=fret_size, hollow=True)
        elif role == 'T':
            fret_pill(d, X(s), y, fr, col=MINT, size=fret_size, ring=TEXT)
        else:
            fret_pill(d, X(s), y, fr, col=MINT, size=fret_size)
        if labels and labels[idx]:
            lab = labels[idx]
            d.text((X(s) - text_w(label_font, lab) / 2, top + 5 * str_gap + 30), lab, font=label_font, fill=AMBER)
    return top + 5 * str_gap + 80 + (40 if labels else 0)

# ---------- video helpers ----------
class Encoder:
    def __init__(self, path, fps=FPS, crf=18):
        self.p = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}',
                                   '-r', str(fps), '-i', '-', '-c:v', 'libx264', '-preset', 'medium', '-crf', str(crf),
                                   '-pix_fmt', 'yuv420p', '-movflags', '+faststart', path], stdin=subprocess.PIPE)
    def write(self, im):
        self.p.stdin.write(im.convert('RGB').tobytes())
    def close(self):
        self.p.stdin.close(); self.p.wait()

def mux(video, audio, out, abitrate='192k'):
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', video, '-i', audio, '-map', '0:v', '-map', '1:a', '-c:v', 'copy',
                    '-c:a', 'aac', '-b:a', abitrate, '-shortest', '-movflags', '+faststart', out], check=True)

def save_slide(im, path):
    im.convert('RGB').save(path, quality=92)
