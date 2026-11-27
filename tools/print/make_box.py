#!/usr/bin/env python3
"""A fold-up 3D box for Stronkie's Clover Snake, in the style of the Amiga big boxes.
Writes print/StronkiesCloverSnake_Box.pdf:
  page 1: full size box on A3 (140 x 180 x 35 mm)
  page 2: mini box on A4 (about 100 x 129 x 25 mm)
  page 3: the five faces flat, for checking / showing off
Solid lines: cut.  Dashed lines: fold (score them first with a blunt knife)."""
import os, sys, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from printkit import *
from reportlab.lib.pagesizes import A3, A4, landscape
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas

OUT = os.path.join(ROOT, 'print', 'StronkiesCloverSnake_Box.pdf')
BOXBLUE = MEADOW
BW, BH, BD = 140 * mm, 180 * mm, 35 * mm
GL, TK = 12 * mm, 15 * mm

c = canvas.Canvas(OUT, pagesize=landscape(A3))
c.setTitle("Stronkie's Clover Snake - Fold-up box")
c.setAuthor('Mark Stronks - Stronkie Soft')


def clip_rect(x, y, w, h):
    p = c.beginPath(); p.rect(x, y, w, h); c.clipPath(p, stroke=0, fill=0)


def starburst(cx, cy, r, lines, rot=12, fill=RED, edge=YELLOW, px=1.6):
    pts = []
    for k in range(36):
        rr = r if k % 2 == 0 else r * 0.8
        a = math.pi * 2 * k / 36
        pts.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))
    p = c.beginPath(); p.moveTo(*pts[0])
    for q in pts[1:]: p.lineTo(*q)
    p.close()
    c.setFillColor(fill); c.setStrokeColor(edge); c.setLineWidth(2); c.drawPath(p, stroke=1, fill=1)
    c.saveState(); c.translate(cx, cy); c.rotate(rot)
    n = len(lines)
    for i, (t, col) in enumerate(lines):
        pixtext(c, t, 0, (n / 2 - i - 1) * 10 * px / 1.0 + 1, px, col, center=True, shadow=HexColor('#00000080', hasAlpha=True), sdx=0.6, sdy=0.6)
    c.restoreState()


def amiga_band(x, y, w, h):
    """The black top band with the rainbow stripes, like the boxes of 1988."""
    c.setFillColor(HexColor('#050505')); c.rect(x, y, w, h, stroke=0, fill=1)
    for i, col in enumerate([RED, ORANGE, YELLOW, GREEN, CYAN, BLUE]):
        c.setFillColor(col)
        c.rect(x + w - 70 - i * 0, y + 3 + i * (h - 6) / 6, 70, (h - 6) / 6, stroke=0, fill=1)
    pixtext(c, 'AMIGA', x + 10, y + h / 2 - 7, 1.9, white)
    c.setFillColor(GREY); c.setFont('PopB', 6); c.drawString(x + 110, y + h / 2 - 2, '500  •  500+  •  600  •  1200')


# ------------------------------------------------------------------ faces
def grid(x, y, w, h, col, step=12):
    c.setStrokeColor(col); c.setLineWidth(0.4)
    for gx in range(0, int(w) + 1, step): c.line(x + gx, y, x + gx, y + h)
    for gy in range(0, int(h) + 1, step): c.line(x, y + gy, x + w, y + gy)


def face_front(x, y, w, h):
    c.saveState(); clip_rect(x, y, w, h)
    for i in range(100):
        t = i / 99
        c.setFillColor(HexColor('#%02x%02x%02x' % (int(10 + 10 * t), int(70 - 30 * t), int(36 - 10 * t))))
        c.rect(x, y + h * (1 - (i + 1) / 100), w, h / 100 + 0.5, stroke=0, fill=1)
    grid(x, y, w, h, HexColor('#ffffff12', hasAlpha=True))
    amiga_band(x, y + h - 30, w, 30)
    lw = w * 0.90
    lh = image(c, os.path.join(ART, 'title_logo.png'), x + (w - lw) / 2, y + h - 40 - lw * 864 / 1904, lw)
    c.setFillColor(FENCE); c.setFont('PopB', 9)
    c.drawCentredString(x + w / 2, y + h - 52 - lh, 'ONE STEP AT A TIME.  EVERY BITE COUNTS.')
    # the game, tilted, in a yellow fence frame
    c.saveState(); c.translate(x + w / 2 + 14, y + 160); c.rotate(-5)
    sw = w * 0.64
    sh = sw * 0.8
    c.setFillColor(HexColor('#00000070', hasAlpha=True)); c.rect(-sw / 2 + 6, -sh / 2 - 6, sw, sh, stroke=0, fill=1)
    c.setFillColor(FENCE); c.rect(-sw / 2 - 5, -sh / 2 - 5, sw + 10, sh + 10, stroke=0, fill=1)
    c.drawImage(ImageReader(os.path.join(SHOTS, 'round05.png')), -sw / 2, -sh / 2, sw, sh)
    c.restoreState()
    c.saveState(); c.translate(x + 68, y + 92); c.rotate(7)
    sw2 = w * 0.34
    c.setFillColor(white); c.rect(-sw2 / 2 - 4, -sw2 * 0.4 - 4, sw2 + 8, sw2 * 0.8 + 8, stroke=0, fill=1)
    c.drawImage(ImageReader(os.path.join(SHOTS, 'round03.png')), -sw2 / 2, -sw2 * 0.4, sw2, sw2 * 0.8)
    c.restoreState()
    starburst(x + w - 54, y + 88, 44, [('12 ROUNDS', YELLOW), ('OF PUZZLE', white), ('FUN!', white)], px=1.2)
    c.setFillColor(HexColor('#000000a0', hasAlpha=True)); c.rect(x, y, w, 46, stroke=0, fill=1)
    item_row(c, x, y + 46, w, 11)
    pixtext(c, 'STRONKIE SOFT', x + 12, y + 22, 1.6, ORANGE, shadow=black)
    c.setFillColor(lighten(GREY, 0.4)); c.setFont('PopM', 6.2)
    c.drawString(x + 12, y + 10, 'Amiga 500  •  Kickstart 3.1  •  1 MB chip RAM')
    lg = ImageReader(LOGO); iw, ih = lg.getSize()
    c.drawImage(lg, x + w - 92, y + 6, 84, 84 * ih / iw, mask='auto')
    c.restoreState()


def face_back(x, y, w, h):
    c.saveState(); clip_rect(x, y, w, h)
    c.setFillColor(MEADOW); c.rect(x, y, w, h, stroke=0, fill=1)
    grid(x, y, w, h, MEADOW2, 14)
    M = 14
    top = y + h - 14
    pixtext(c, "STRONKIE'S CLOVER SNAKE", x + w / 2, top - 16, 1.45, center=True, rows=['#ffffff', '#e6ffd9', '#b5f5a0', '#5ee05e', '#34c734', '#1f9e2a', '#137a20', '#0b5216'], shadow=black)
    item_row(c, x, top - 32, w, 10)
    yy = para(c, '<b>A snake game - but not as you know it.</b> Your snake only moves when you do: one step for every push of '
              'the stick. Eat every <b>clover</b> - each one makes you longer and makes a <b>white ball</b> pop up. Eat the '
              'balls too. But every bite grows a <b>poison mushroom</b> on the next spore... unless your own tail is lying on it!',
              x + M, top - 40, w - 2 * M, 8.0, color=white, align=1)
    sw = (w - 2 * M - 16) / 3
    sh = sw * 0.8
    shots = [('round02.png', 'Three Walls'), ('round08.png', 'The Spiral'), ('heart.png', 'Catch the heart!')]
    for i, (s, cap) in enumerate(shots):
        sx = x + M + i * (sw + 8)
        sy = yy - 12 - sh
        c.setFillColor(FENCE); c.rect(sx - 2.5, sy - 2.5, sw + 5, sh + 5, stroke=0, fill=1)
        c.drawImage(ImageReader(os.path.join(SHOTS, s)), sx, sy, sw, sh)
        c.setFillColor(lighten(GRASS, 0.3)); c.setFont('PopI', 6.4); c.drawCentredString(sx + sw / 2, sy - 10, cap)
    yy = yy - 12 - sh - 26
    feats = [('clover', 'Twelve hand-made rounds - then they come back, faster'),
             ('block', 'Push crates to open doors and build safe paths'),
             ('spore', 'Spores: the order you eat in changes the meadow'),
             ('heart', 'Drifting hearts for a bonus multiplier up to x9'),
             ('ball', 'Retry a stuck round with one key  •  music and sound')]
    for nm, f in feats:
        icon(c, nm, x + M, yy - 9, 9)
        c.setFillColor(white); c.setFont('PopM', 8.0); c.drawString(x + M + 14, yy - 7, f)
        yy -= 14
    # the snake
    snake_line(c, x + M, yy - 28, 12, 14)
    icon(c, 'clover', x + M + 13 * 14, yy - 28, 14)
    icon(c, 'ball', x + M + 15 * 14, yy - 28, 14)
    c.setFillColor(HexColor('#05070f')); c.rect(x, y, w, 44, stroke=0, fill=1)
    lg = ImageReader(LOGO); iw, ih = lg.getSize()
    c.drawImage(lg, x + 8, y + 6, 64, 64 * ih / iw, mask='auto')
    c.setFillColor(GREY); c.setFont('Pop', 5.6)
    c.drawString(x + 80, y + 26, "© 2026 Mark Stronks - Stronkie Soft. Programming AI: Claude.")
    c.drawString(x + 80, y + 18, 'Inspired by Snake It (MSX, 1986).')
    c.drawString(x + 80, y + 10, 'stronkie.itch.io/stronkies-clover-snake')
    c.setFillColor(YELLOW); c.circle(x + w - 26, y + 22, 16, stroke=0, fill=1)
    pixtext(c, 'AGES', x + w - 26, y + 25, 0.8, INK, center=True)
    pixtext(c, '8-88', x + w - 26, y + 14, 1.0, INK, center=True)
    c.restoreState()


def face_spine(x, y, w, h):
    c.saveState(); clip_rect(x, y, w, h)
    c.setFillColor(MEADOW); c.rect(x, y, w, h, stroke=0, fill=1)
    c.setFillColor(HexColor('#050505')); c.rect(x, y + h - 52, w, 52, stroke=0, fill=1)
    for i, col in enumerate([RED, ORANGE, YELLOW, GREEN, CYAN, BLUE]):
        c.setFillColor(col); c.rect(x, y + h - 52 + 6 + i * 4, w, 4, stroke=0, fill=1)
    pixtext(c, 'AMIGA', x + w / 2, y + h - 18, 1.3, white, center=True)
    c.translate(x + w / 2, y + (h - 52) / 2 + 4); c.rotate(90)
    pixtext(c, "STRONKIE'S CLOVER SNAKE", 0, 2, 1.55, center=True, rows=['#ffffff', '#e6ffd9', '#b5f5a0', '#5ee05e', '#34c734', '#1f9e2a', '#137a20', '#0b5216'], shadow=black)
    c.setFillColor(FENCE); c.setFont('PopB', 6.5); c.drawCentredString(0, -14, 'A STEP-BY-STEP PUZZLE SNAKE')
    c.restoreState()
    c.saveState()
    for i, nm in enumerate(('clover', 'ball', 'heart')):
        icon(c, nm, x + w / 2 - 6, y + 10 + i * 14, 12)
    c.restoreState()


def face_specs(x, y, w, h):
    c.saveState(); clip_rect(x, y, w, h)
    c.setFillColor(HexColor('#e9e4d4')); c.rect(x, y, w, h, stroke=0, fill=1)
    c.translate(x + w, y); c.rotate(90)
    L, T = h, w
    c.setFillColor(MEADOW); c.rect(0, T - 16, L, 16, stroke=0, fill=1)
    pixtext(c, 'SYSTEM REQUIREMENTS', 10, T - 12, 1.2, FENCE)
    pixtext(c, 'STRONKIE SOFT', L - 10, T - 12, 1.0, ORANGE, right=True)
    colw = (L - 30) / 2
    blocks = [('YOUR AMIGA', GRASS, ['Amiga 500 (PAL) with a 68000', 'Kickstart / Workbench 3.1 (1.3 works too)', '1 MB chip RAM (also fits in 512 KB)', 'Joystick in port 2 or cursor keys  •  1 player']),
              ('ON THE DISK', SNAKE, ['The game (boots straight away)', 'Hard disk installer', 'WHDLoad version: separate download', 'Runs in WinUAE, on a Gotek, from a CF card'])]
    for k, (t, col, ls) in enumerate(blocks):
        bx = 10 + k * (colw + 10)
        c.setFillColor(col); c.rect(bx, T - 31, colw, 11, stroke=0, fill=1)
        pixtext(c, t, bx + 4, T - 28.5, 0.9, INK)
        for j, l in enumerate(ls):
            c.setFillColor(INK); c.setFont('PopM', 6.3); c.drawString(bx + 2, T - 42 - j * 9.5, l)
    c.setFillColor(GREY); c.setFont('Pop', 5.2)
    c.drawString(10, 5, '1 × 3½" double-density disk (880 KB)  •  hard drive installable  •  12 rounds  •  V' + VER)
    c.restoreState()


def face_top(x, y, w, h):
    c.saveState(); clip_rect(x, y, w, h)
    c.setFillColor(MEADOW); c.rect(x, y, w, h, stroke=0, fill=1)
    item_row(c, x, y + 2, w, 9)
    item_row(c, x, y + h - 11, w, 9, 3)
    pixtext(c, "STRONKIE'S CLOVER SNAKE", x + w / 2, y + h / 2 - 5, 1.35, center=True, rows=['#ffffff', '#e6ffd9', '#b5f5a0', '#5ee05e', '#34c734', '#1f9e2a', '#137a20', '#0b5216'], shadow=black)
    c.restoreState()


def face_bottom(x, y, w, h):
    c.saveState(); clip_rect(x, y, w, h)
    c.setFillColor(MEADOW); c.rect(x, y, w, h, stroke=0, fill=1)
    pixtext(c, 'STRONKIE SOFT', x + w / 2, y + h / 2 + 4, 1.4, ORANGE, center=True)
    c.setFillColor(GREY); c.setFont('PopM', 6)
    c.drawCentredString(x + w / 2, y + h / 2 - 10, '1 DISK  •  12 ROUNDS  •  V' + VER + '  •  MADE IN 2026')
    c.restoreState()


# ------------------------------------------------------------------ the dieline
def tuck(x, y, w, h, up=True):
    """A tuck flap: rounded at the free corners."""
    p = c.beginPath()
    r = min(h * 0.9, 10 * mm)
    if up:
        p.moveTo(x, y); p.lineTo(x + 2, y + h - r); p.curveTo(x + 2, y + h, x + r, y + h, x + r + 2, y + h)
        p.lineTo(x + w - r - 2, y + h); p.curveTo(x + w - r, y + h, x + w - 2, y + h, x + w - 2, y + h - r); p.lineTo(x + w, y)
    else:
        p.moveTo(x, y + h); p.lineTo(x + 2, y + r); p.curveTo(x + 2, y, x + r, y, x + r + 2, y)
        p.lineTo(x + w - r - 2, y); p.curveTo(x + w - r, y, x + w - 2, y, x + w - 2, y + r); p.lineTo(x + w, y + h)
    p.close()
    return p


def dust(x, y, w, h, up=True):
    p = c.beginPath()
    if up:
        p.moveTo(x, y); p.lineTo(x + 1, y + h * 0.55); p.lineTo(x + w * 0.35, y + h); p.lineTo(x + w - 1, y + h); p.lineTo(x + w, y)
    else:
        p.moveTo(x, y + h); p.lineTo(x + 1, y + h * 0.45); p.lineTo(x + w * 0.35, y); p.lineTo(x + w - 1, y); p.lineTo(x + w, y + h)
    p.close()
    return p


def dieline(ox, oy, s, page_w, page_h, label):
    c.saveState(); c.translate(ox, oy); c.scale(s, s)
    yb = BD + TK
    xg, xl, xf, xr, xb = 0, GL, GL + BD, GL + BD + BW, GL + 2 * BD + BW
    # artwork (with 2 mm bleed under the cut lines)
    B = 2 * mm
    c.setFillColor(HexColor('#cfcfd6'))
    p = c.beginPath(); p.moveTo(xl, yb + 4 * mm); p.lineTo(xg, yb + 8 * mm); p.lineTo(xg, yb + BH - 8 * mm); p.lineTo(xl, yb + BH - 4 * mm); p.close()
    c.drawPath(p, stroke=0, fill=1)
    c.saveState(); c.translate(xg + GL / 2, yb + BH / 2); c.rotate(90)
    c.setFillColor(GREY); c.setFont('PopB', 7); c.drawCentredString(0, -2, 'GLUE  •  GLUE  •  GLUE')
    c.restoreState()
    face_specs(xl, yb, BD, BH)
    face_front(xf, yb, BW, BH)
    face_spine(xr, yb, BD, BH)
    face_back(xb, yb, BW, BH)
    # top lid on the back, bottom lid on the front (drawn so they read from the front)
    c.saveState(); c.translate(xb + BW, yb + BH + BD); c.rotate(180); face_top(0, 0, BW, BD); c.restoreState()
    face_bottom(xf, yb - BD, BW, BD)
    # tucks and dust flaps
    c.setFillColor(MEADOW2)
    c.drawPath(tuck(xb, yb + BH + BD, BW, TK, True), stroke=0, fill=1)
    c.drawPath(tuck(xf, yb - BD - TK, BW, TK, False), stroke=0, fill=1)
    for xx in (xl, xr):
        c.drawPath(dust(xx, yb + BH, BD, BD * 0.85, True), stroke=0, fill=1)
        c.drawPath(dust(xx, yb - BD * 0.85, BD, BD * 0.85, False), stroke=0, fill=1)
    # cut lines
    c.setStrokeColor(black); c.setLineWidth(0.6 / s)
    c.drawPath(tuck(xb, yb + BH + BD, BW, TK, True), stroke=1, fill=0)
    c.drawPath(tuck(xf, yb - BD - TK, BW, TK, False), stroke=1, fill=0)
    for xx in (xl, xr):
        c.drawPath(dust(xx, yb + BH, BD, BD * 0.85, True), stroke=1, fill=0)
        c.drawPath(dust(xx, yb - BD * 0.85, BD, BD * 0.85, False), stroke=1, fill=0)
    c.drawPath(p, stroke=1, fill=0)          # the glue flap
    c.line(xf, yb + BH, xf, yb + BH + 0.01)
    # outer edges of the body
    c.line(xb + BW, yb, xb + BW, yb + BH)
    c.line(xb, yb + BH, xb, yb + BH + BD); c.line(xb + BW, yb + BH, xb + BW, yb + BH + BD)   # top lid sides
    c.line(xf, yb - BD, xf, yb); c.line(xf + BW, yb - BD, xf + BW, yb)                       # bottom lid sides
    c.line(xf, yb + BH, xf + BW, yb + BH)    # top of front
    c.line(xb, yb, xb + BW, yb)              # bottom of back
    # fold lines
    c.setDash(3 / s, 2 / s); c.setStrokeColor(HexColor('#ffffff')); c.setLineWidth(0.5 / s)
    for xx in (xl, xf, xr, xb):
        c.line(xx, yb, xx, yb + BH)
    c.line(xb, yb + BH, xb + BW, yb + BH); c.line(xb, yb + BH + BD, xb + BW, yb + BH + BD)
    c.line(xf, yb, xf + BW, yb); c.line(xf, yb - BD, xf + BW, yb - BD)
    c.line(xl, yb + BH, xl + BD, yb + BH); c.line(xr, yb + BH, xr + BD, yb + BH)
    c.line(xl, yb, xl + BD, yb); c.line(xr, yb, xr + BD, yb)
    c.setDash()
    # instructions in the empty corner above the front
    ix, iy = xf + 4 * mm, yb + BH + BD + TK
    pixtext(c, 'FOLD-UP BOX', ix, iy - 9, 1.5, MEADOW)
    lines = [label, 'Print at 100% on thick paper (200-300 g/m²).',
             'Cut the solid lines, score and fold the dashed ones.',
             'Glue the grey flap behind the back panel, then fold',
             'the dust flaps in and tuck the lids.']
    c.setFillColor(INK); c.setFont('Pop', 6.3 / max(s, 0.85))
    for i, l in enumerate(lines):
        c.drawString(ix, iy - 20 - i * 8.5 / max(s, 0.85), l)
    c.restoreState()


# ---- page 1: A3, full size
PW, PH = landscape(A3)
TOTW = GL + 2 * BD + 2 * BW
TOTH = BH + 2 * (BD + TK)
dieline((PW - TOTW) / 2, (PH - TOTH) / 2, 1.0, PW, PH, 'Full size: 140 × 180 × 35 mm (A3 paper).')
c.showPage()

# ---- page 2: A4, mini
c.setPageSize(landscape(A4))
PW, PH = landscape(A4)
s = min((PW - 14 * mm) / TOTW, (PH - 10 * mm) / TOTH)
dieline((PW - TOTW * s) / 2, (PH - TOTH * s) / 2, s, PW, PH,
        'Mini: %d × %d × %d mm (A4 paper).' % (round(140 * s), round(180 * s), round(35 * s)))
c.showPage()

# ---- page 3: the faces flat (A3)
c.setPageSize(landscape(A3))
PW, PH = landscape(A3)
c.setFillColor(HexColor('#2b2b33')); c.rect(0, 0, PW, PH, stroke=0, fill=1)
gx = (PW - (BD + BW + BD + BW + 3 * 8 * mm)) / 2
y0 = (PH - BH) / 2 - 8 * mm
face_specs(gx, y0, BD, BH)
face_front(gx + BD + 8 * mm, y0, BW, BH)
face_spine(gx + BD + BW + 16 * mm, y0, BD, BH)
face_back(gx + 2 * BD + BW + 24 * mm, y0, BW, BH)
face_top(gx + BD + 8 * mm, y0 + BH + 8 * mm, BW, BD)
face_bottom(gx + 2 * BD + BW + 24 * mm, y0 + BH + 8 * mm, BW, BD)
pixtext(c, "CLOVER SNAKE - THE BOX", PW / 2, PH - 18 * mm, 2.4, center=True, rows=CHROME, shadow=black)
c.setFillColor(GREY); c.setFont('PopM', 8)
c.drawCentredString(PW / 2, 10 * mm, 'Left to right: specs side, front, spine, back.  Top: lid and bottom.  This page is for previews; build the box from page 1 or 2.')
c.showPage()
c.save()
print('wrote', OUT)
