"""Shared drawing helpers for the printed extras (manual, labels, box).

The headings use the game's own 8x8 font (src/bin/font.bin), drawn as
vector squares so they stay sharp at any print size.
"""
import os
from reportlab.lib.colors import HexColor, white, black
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Paragraph
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.utils import ImageReader

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..')
FONT = open(os.path.join(ROOT, 'art', 'print', 'font.bin'), 'rb').read()
ART = os.path.join(ROOT, 'art', 'print')
TK = os.environ.get('AMIGA_TK', os.path.join(ROOT, '..', 'amiga-toolkit'))
LOGO = os.path.join(TK, 'art', 'stronkiesoft_logo.png')
SHOTS = os.path.join(ROOT, 'screenshots', 'print')

GF = '/usr/share/fonts/truetype/google-fonts/'
pdfmetrics.registerFont(TTFont('Pop', GF + 'Poppins-Regular.ttf'))
pdfmetrics.registerFont(TTFont('PopM', GF + 'Poppins-Medium.ttf'))
pdfmetrics.registerFont(TTFont('PopB', GF + 'Poppins-Bold.ttf'))
pdfmetrics.registerFont(TTFont('PopI', GF + 'Poppins-Italic.ttf'))
pdfmetrics.registerFont(TTFont('PopBI', GF + 'Poppins-BoldItalic.ttf'))
from reportlab.lib.fonts import addMapping
addMapping('Pop', 0, 0, 'Pop'); addMapping('Pop', 1, 0, 'PopB')
addMapping('Pop', 0, 1, 'PopI'); addMapping('Pop', 1, 1, 'PopBI')

NAVY = HexColor('#121735')
NAVY2 = HexColor('#1f2a5c')
INK = HexColor('#1b1b24')
PAPER = HexColor('#f5eedb')
PAPER2 = HexColor('#e9dfc4')
ORANGE = HexColor('#ff8a00')
MAGENTA = HexColor('#e8178a')
CYAN = HexColor('#19c8e6')
YELLOW = HexColor('#ffd21a')
GREEN = HexColor('#34c759')
RED = HexColor('#e8322a')
BLUE = HexColor('#2f6bff')
PURPLE = HexColor('#a03cff')
GREY = HexColor('#8a8a99')

# the seven pieces, in the game's colours
PIECES = {
    'I': ([(0, 0), (1, 0), (2, 0), (3, 0)], CYAN),
    'O': ([(0, 0), (1, 0), (0, 1), (1, 1)], YELLOW),
    'T': ([(0, 0), (1, 0), (2, 0), (1, 1)], PURPLE),
    'S': ([(1, 0), (2, 0), (0, 1), (1, 1)], GREEN),
    'Z': ([(0, 0), (1, 0), (1, 1), (2, 1)], RED),
    'J': ([(0, 0), (0, 1), (1, 1), (2, 1)], BLUE),
    'L': ([(2, 0), (0, 1), (1, 1), (2, 1)], ORANGE),
}
RAINBOW = [RED, ORANGE, YELLOW, GREEN, CYAN, BLUE, PURPLE, MAGENTA]
CHROME = ['#ffffff', '#d6e8ff', '#8fb8ff', '#3d5fd9', '#ffb347', '#ff7a1a', '#c94400', '#7a2800']


def lighten(c, f):
    return HexColor('#%02x%02x%02x' % tuple(int(255 * min(1, v + (1 - v) * f)) for v in (c.red, c.green, c.blue)))


def darken(c, f):
    return HexColor('#%02x%02x%02x' % tuple(int(255 * v * (1 - f)) for v in (c.red, c.green, c.blue)))


def pixwidth(text, px):
    return len(text) * 8 * px


def pixtext(c, text, x, y, px, color=white, shadow=None, center=False, right=False, rows=None, sdx=1, sdy=1):
    """Draw text in the game font. (x, y) = bottom-left; px = size of one pixel.
    rows: a list of 8 colours, one per pixel row (the chrome look)."""
    text = text.upper() if False else text
    w = pixwidth(text, px)
    if center: x -= w / 2
    if right: x -= w
    passes = []
    if shadow is not None: passes.append((sdx * px, -sdy * px, shadow, None))
    passes.append((0, 0, color, rows))
    for dx, dy, col, rws in passes:
        for i, ch in enumerate(text):
            o = ord(ch) - 32
            if o < 0 or o >= 96: continue
            for r in range(8):
                bits = FONT[o * 8 + r]
                if not bits: continue
                cc = HexColor(rws[r]) if rws else col
                c.setFillColor(cc)
                b = 0
                while b < 8:
                    if bits & (0x80 >> b):
                        e = b
                        while e < 8 and bits & (0x80 >> e): e += 1
                        c.rect(x + dx + (i * 8 + b) * px, y + dy + (7 - r) * px, (e - b) * px + 0.02, px + 0.02, stroke=0, fill=1)
                        b = e
                    else:
                        b += 1
    return w


def cell(c, x, y, s, col, edge=True):
    """One shaded glass block, like in the game."""
    c.setFillColor(col); c.rect(x, y, s, s, stroke=0, fill=1)
    e = s * 0.16
    c.setFillColor(lighten(col, 0.55))
    p = c.beginPath(); p.moveTo(x, y + s); p.lineTo(x + s, y + s); p.lineTo(x + s - e, y + s - e); p.lineTo(x + e, y + s - e); p.lineTo(x + e, y + e); p.lineTo(x, y); p.close()
    c.drawPath(p, stroke=0, fill=1)
    c.setFillColor(darken(col, 0.45))
    p = c.beginPath(); p.moveTo(x + s, y + s); p.lineTo(x + s, y); p.lineTo(x, y); p.lineTo(x + e, y + e); p.lineTo(x + s - e, y + e); p.lineTo(x + s - e, y + s - e); p.close()
    c.drawPath(p, stroke=0, fill=1)
    c.setFillColor(lighten(col, 0.85)); c.rect(x + e * 1.4, y + s - e * 2.4, e, e, stroke=0, fill=1)
    if edge:
        c.setStrokeColor(darken(col, 0.7)); c.setLineWidth(0.3); c.rect(x, y, s, s, stroke=1, fill=0)


def piece(c, name, x, y, s):
    cells, col = PIECES[name]
    for (cx, cy) in cells:
        cell(c, x + cx * s, y - cy * s, s, col)


def block_row(c, x, y, w, s, start=0):
    n = int(w // s)
    for i in range(n):
        cell(c, x + i * s, y, s, RAINBOW[(i + start) % len(RAINBOW)])


def para(c, text, x, y_top, w, size=8.6, lead=None, font='Pop', color=INK, align=0, space=0):
    """Draw a paragraph with its top at y_top; returns the bottom y."""
    st = ParagraphStyle('p', fontName=font, fontSize=size, leading=lead or size * 1.38,
                        textColor=color, alignment=align, spaceAfter=space)
    p = Paragraph(text, st)
    _, h = p.wrapOn(c, w, 2000)
    p.drawOn(c, x, y_top - h)
    return y_top - h


def image(c, path, x, y, w, h=None, keep=True):
    im = ImageReader(path)
    iw, ih = im.getSize()
    if h is None: h = w * ih / iw
    c.drawImage(im, x, y, w, h, preserveAspectRatio=keep, anchor='c', mask='auto')
    return h


def shot(c, name, x, y_top, w, caption=None, bezel=NAVY, capcol=INK):
    """A screenshot in a monitor-ish frame; returns the bottom y."""
    path = name if os.path.isabs(name) else os.path.join(SHOTS, name)
    im = ImageReader(path)
    iw, ih = im.getSize()
    h = w * ih / iw
    b = 3.2
    c.setFillColor(HexColor('#00000033', hasAlpha=True)); c.roundRect(x - b + 2, y_top - h - b - 2, w + 2 * b, h + 2 * b, 3, stroke=0, fill=1)
    c.setFillColor(bezel); c.roundRect(x - b, y_top - h - b, w + 2 * b, h + 2 * b, 3, stroke=0, fill=1)
    c.drawImage(im, x, y_top - h, w, h)
    y = y_top - h - b
    if caption:
        y = para(c, caption, x, y - 3, w, size=6.6, font='PopI', color=capcol, align=1)
    return y


def factbox(c, x, y_top, w, title, text, col=YELLOW, size=7.6):
    """A 'did you know' box; returns the bottom y."""
    st = ParagraphStyle('f', fontName='Pop', fontSize=size, leading=size * 1.36, textColor=INK)
    p = Paragraph(text, st)
    pad = 7
    _, h = p.wrapOn(c, w - 2 * pad, 2000)
    th = 14
    H = h + th + 2 * pad
    c.setFillColor(HexColor('#00000030', hasAlpha=True)); c.rect(x + 2.5, y_top - H - 2.5, w, H, stroke=0, fill=1)
    c.setFillColor(lighten(col, 0.72)); c.setStrokeColor(INK); c.setLineWidth(1.2)
    c.rect(x, y_top - H, w, H, stroke=1, fill=1)
    c.setFillColor(col); c.rect(x, y_top - th - 2, w, th + 2, stroke=1, fill=1)
    pixtext(c, title, x + 6, y_top - th + 1.5, 1.25, INK)
    p.drawOn(c, x + pad, y_top - th - pad - h + 2)
    return y_top - H

# ---- Clover Snake extras
MEADOW = HexColor('#0d3b1e')
MEADOW2 = HexColor('#15542b')
GRASS = HexColor('#3dd13d')
SNAKE = HexColor('#44ccff')
FENCE = HexColor('#eeee22')
GAME = "STRONKIE'S CLOVER SNAKE"
VER = '0.3'
ITEMS = ['clover', 'ball', 'clover', 'heart', 'clover', 'block', 'clover', 'mush']


def icon(c, name, x, y, s):
    """One of the game's own 8x8 pictures (art/print/<name>.png), s points wide."""
    c.drawImage(ImageReader(os.path.join(ART, name + '.png')), x, y, s, s, mask='auto')


def item_row(c, x, y, w, s, start=0):
    """A row of clovers, balls, hearts... (the 'block row' of this game)."""
    n = int(w // (s * 1.5))
    gap = (w - n * s) / max(1, n)
    for i in range(n):
        icon(c, ITEMS[(i + start) % len(ITEMS)], x + gap / 2 + i * (s + gap), y, s)


def snake_line(c, x, y, n, s, head=True):
    """A straight snake, n cells long, facing right."""
    icon(c, 'snake8', x, y, s)
    for i in range(1, n - 1):
        icon(c, 'snake10', x + i * s, y, s)
    icon(c, 'head1' if head else 'snake10', x + (n - 1) * s, y, s)
