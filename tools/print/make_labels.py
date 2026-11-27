#!/usr/bin/env python3
"""3.5" disk labels for Stronkie's Clover Snake on an A4 sheet.
Writes print/StronkiesCloverSnake_DiskLabels.pdf.  Print at 100% (no 'fit to
page'), cut along the marks, fold the flap over the top edge of the disk."""
import os, sys, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from printkit import *
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas

OUT = os.path.join(ROOT, 'print', 'StronkiesCloverSnake_DiskLabels.pdf')
PW, PH = A4
LW, FRONT, FLAP = 70 * mm, 55 * mm, 20 * mm
LH = FRONT + FLAP
c = canvas.Canvas(OUT, pagesize=A4)
c.setTitle("Stronkie's Clover Snake - Disk labels")
c.setAuthor('Mark Stronks - Stronkie Soft')


def crop(x, y, w, h):
    c.setStrokeColor(HexColor('#888888')); c.setLineWidth(0.3)
    L = 4 * mm
    for (px, py, dx, dy) in ((x, y, -1, -1), (x + w, y, 1, -1), (x, y + h, -1, 1), (x + w, y + h, 1, 1)):
        c.line(px + dx * 1.5 * mm, py, px + dx * (1.5 * mm + L), py)
        c.line(px, py + dy * 1.5 * mm, px, py + dy * (1.5 * mm + L))


GR = ['#ffffff', '#e6ffd9', '#b5f5a0', '#5ee05e', '#34c734', '#1f9e2a', '#137a20', '#0b5216']


def front_dark(x, y, title2='GAME DISK'):
    w, h = LW, FRONT
    c.setFillColor(MEADOW); c.rect(x, y, w, h, stroke=0, fill=1)
    c.setFillColor(FENCE); c.rect(x, y + h - 46, w, 2, stroke=0, fill=1)
    pixtext(c, "STRONKIE'S", x + w / 2, y + h - 15, 1.45, center=True, rows=CHROME, shadow=black, sdx=0.8, sdy=0.8)
    pixtext(c, 'CLOVER SNAKE', x + w / 2, y + h - 36, 1.85, center=True, rows=GR, shadow=black, sdx=0.8, sdy=0.8)
    sw = 30 * mm
    sh = sw * 0.8
    c.setFillColor(FENCE); c.rect(x + 4, y + 8 - 1, sw + 2, sh + 2, stroke=0, fill=1)
    c.drawImage(ImageReader(os.path.join(SHOTS, 'round03.png')), x + 5, y + 8, sw, sh)
    tx = x + sw + 12
    pixtext(c, title2, tx, y + 62, 1.05, FENCE)
    for i, t in enumerate(('AMIGA 500', 'KICKSTART 3.1', '1 MB CHIP RAM')):
        pixtext(c, t, tx, y + 50 - i * 9, 0.82, white)
    c.setFillColor(SNAKE); c.rect(tx - 2, y + 11, w - (tx - x) - 3, 10, stroke=0, fill=1)
    pixtext(c, '12 ROUNDS  V' + VER, tx + 1, y + 13.5, 0.78, INK)
    c.setFillColor(GREY); c.setFont('PopM', 4.6)
    c.drawString(x + 5, y + 2.6, "© 2026 MARK STRONKS • STRONKIE SOFT")
    c.drawRightString(x + w - 4, y + 2.6, 'STRONKIE.ITCH.IO')


def front_classic(x, y):
    w, h = LW, FRONT
    c.setFillColor(white); c.rect(x, y, w, h, stroke=0, fill=1)
    c.setFillColor(MEADOW); c.rect(x, y + h - 30, w, 30, stroke=0, fill=1)
    c.setFillColor(FENCE); c.rect(x, y + h - 33, w, 3, stroke=0, fill=1)
    pixtext(c, "STRONKIE'S CLOVER SNAKE", x + w / 2, y + h - 19, 1.05, center=True, rows=GR, shadow=black, sdx=0.7, sdy=0.7)
    c.setFillColor(FENCE); c.setFont('PopB', 5)
    c.drawCentredString(x + w / 2, y + h - 27, 'THE STEP-BY-STEP PUZZLE SNAKE FOR YOUR AMIGA')
    pixtext(c, 'DISK 1 OF 1', x + 8, y + 88, 1.0, MAGENTA)
    snake_line(c, x + 8, y + 64, 6, 10)
    icon(c, 'clover', x + 80, y + 64, 10); icon(c, 'ball', x + 98, y + 64, 10); icon(c, 'mush', x + 116, y + 64, 10)
    icon(c, 'heart', x + 134, y + 64, 10); icon(c, 'block', x + 152, y + 64, 10); icon(c, 'clover', x + 170, y + 64, 10)
    pixtext(c, 'GAME DISK', x + 8, y + 38, 1.4, MEADOW)
    c.setFillColor(INK); c.setFont('Pop', 5.6)
    c.drawString(x + 8, y + 29.5, 'Amiga 500 • 68000 • Kickstart 3.1 • 1 MB chip RAM')
    c.drawString(x + 8, y + 21.5, 'Boots by itself  •  Install on the disk for a hard drive')
    c.drawString(x + 8, y + 14, 'Joystick in port 2 or cursor keys')
    c.setFillColor(MEADOW); c.rect(x, y, w, 9, stroke=0, fill=1)
    pixtext(c, 'STRONKIE SOFT', x + 6, y + 2.5, 0.78, ORANGE)
    c.setFillColor(white); c.setFont('PopM', 4.6); c.drawRightString(x + w - 5, y + 3, '© 2026  •  V' + VER)


def front_enhanced(x, y):
    """The meadow label: a big screenshot with the title on top."""
    w, h = LW, FRONT
    c.drawImage(ImageReader(os.path.join(SHOTS, 'round07.png')), x, y, w, h, preserveAspectRatio=False)
    c.setFillColor(HexColor('#000000')); c.setFillAlpha(0.45); c.rect(x, y, w, h, stroke=0, fill=1); c.setFillAlpha(1)
    pixtext(c, "STRONKIE'S", x + w / 2, y + h - 16, 1.45, center=True, rows=CHROME, shadow=black, sdx=0.8, sdy=0.8)
    pixtext(c, 'CLOVER SNAKE', x + w / 2, y + h - 38, 1.85, center=True, rows=GR, shadow=black, sdx=0.8, sdy=0.8)
    c.setFillColor(MEADOW); c.rect(x, y + 50, w, 14, stroke=0, fill=1)
    pixtext(c, 'EVERY BITE COUNTS', x + w / 2, y + 53.5, 1.15, FENCE, center=True, shadow=black, sdx=0.6, sdy=0.6)
    pixtext(c, '12 ROUNDS', x + w / 2, y + 36, 0.95, white, center=True, shadow=black, sdx=0.6, sdy=0.6)
    pixtext(c, 'AMIGA 500  1 MB', x + w / 2, y + 25, 0.95, SNAKE, center=True, shadow=black, sdx=0.6, sdy=0.6)
    c.setFillColor(lighten(GREY, 0.4)); c.setFont('PopM', 4.6)
    c.drawCentredString(x + w / 2, y + 4, "© 2026 MARK STRONKS • STRONKIE SOFT • V" + VER)


def flap(x, y, dark=True):
    w, h = LW, FLAP
    c.saveState(); c.translate(x + w, y + h); c.rotate(180)
    c.setFillColor(MEADOW if dark else white); c.rect(0, 0, w, h, stroke=0, fill=1)
    item_row(c, 0, h - 7, w, 6)
    col = white if dark else INK
    pixtext(c, "STRONKIE'S CLOVER SNAKE", 5, h - 16, 0.75, FENCE if dark else MEADOW)
    c.setFillColor(col); c.setFont('Pop', 4.4)
    c.drawString(5, h - 24, 'Boot from this disk, or double-click CloverSnake on Workbench.')
    c.drawString(5, h - 30, 'Install (on this disk) puts the game on your hard drive.')
    c.drawString(5, h - 36, 'Do not touch the magnetic surface. Do not feed to the snake.')
    c.setFont('PopB', 4.4); c.drawString(5, 6, 'GAME DISK  •  V' + VER)
    c.drawRightString(w - 5, 6, 'STRONKIE SOFT 2026')
    c.restoreState()


def label(x, y, kind):
    flap(x, y + FRONT, dark=(kind != 'classic'))
    {'dark': front_dark, 'classic': front_classic, 'enh': front_enhanced}[kind](x, y)
    c.setStrokeColor(HexColor('#ffffff')); c.setDash(2, 2); c.setLineWidth(0.5)
    c.line(x + 2, y + FRONT, x + LW - 2, y + FRONT); c.setDash()
    crop(x, y, LW, LH)


# ---- the sheet
c.setFillColor(MEADOW); c.rect(0, PH - 26 * mm, PW, 26 * mm, stroke=0, fill=1)
pixtext(c, "CLOVER SNAKE - DISK LABELS", 14 * mm, PH - 13 * mm, 2.1, rows=CHROME, shadow=black)
c.setFillColor(white); c.setFont('Pop', 7.5)
c.drawString(14 * mm, PH - 20 * mm, 'Print at 100% (actual size) on white paper or A4 sticker sheets. Cut on the marks. The dashed line is the top edge of the disk:')
c.drawString(14 * mm, PH - 23.5 * mm, 'stick the big part on the front of the disk and fold the flap over onto the back. Label size 70 × 75 mm (front 70 × 55 mm).')
gx = (PW - 2 * LW - 16 * mm) / 2
kinds = [('dark', 'dark'), ('classic', 'classic'), ('enh', 'enh')]
top = PH - 34 * mm
for r, (k1, k2) in enumerate(kinds):
    yy = top - (r + 1) * LH - r * 10 * mm
    label(gx, yy, k1)
    label(gx + LW + 16 * mm, yy, k2)
c.setFillColor(GREY); c.setFont('PopM', 6.5)
c.drawCentredString(PW / 2, 8 * mm, "Three styles: the box-art label, the classic white publisher's label and the meadow label. © 2026 Mark Stronks - Stronkie Soft")
c.showPage()

# ---- page 2: the square labels (no fold) for disk boxes and cases, plus a spine strip
c.setFillColor(MEADOW); c.rect(0, PH - 20 * mm, PW, 20 * mm, stroke=0, fill=1)
pixtext(c, 'FLAT LABELS AND SPINE STRIPS', 14 * mm, PH - 13 * mm, 2.1, rows=CHROME, shadow=black)
c.setFillColor(GREY); c.setFont('Pop', 7); c.setFillColor(white)
c.drawString(14 * mm, PH - 17.5 * mm, 'Front-only labels (70 × 55 mm, no flap) and spine strips for a disk box. Print at 100%.')
gx = (PW - 2 * LW - 16 * mm) / 2
for r in range(2):
    for k, fn in enumerate((front_dark, front_classic, front_enhanced)):
        col = k % 2
        pass
pos = []
for r in range(3):
    for col in range(2):
        pos.append((gx + col * (LW + 16 * mm), PH - 30 * mm - (r + 1) * FRONT - r * 10 * mm))
for i, (x, y) in enumerate(pos):
    (front_dark, front_classic, front_enhanced)[i % 3](x, y)
    crop(x, y, LW, FRONT)
# spine strips
for i in range(3):
    x, y = gx, 20 * mm + i * 14 * mm
    w = 2 * LW + 16 * mm
    c.setFillColor(MEADOW); c.rect(x, y, w, 9 * mm, stroke=0, fill=1)
    snake_line(c, x + 3, y + 7, 5, 12)
    pixtext(c, "STRONKIE'S CLOVER SNAKE", x + 26 * mm, y + 9, 1.35, rows=GR, shadow=black)
    pixtext(c, 'AMIGA', x + w - 34 * mm, y + 9, 1.4, ORANGE)
    pixtext(c, 'SOFT', x + w - 12 * mm, y + 9, 1.1, white)
    crop(x, y, w, 9 * mm)
c.showPage()
c.save()
print('wrote', OUT)
