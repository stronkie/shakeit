#!/usr/bin/env python3
"""The printed manual: a 12 page A5 booklet in the style of an old box manual.
Writes print/StronkiesCloverSnake_Manual.pdf.  Print it double-sided, or as a
booklet (most printers: 'booklet' in the print dialog), fold and staple."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from printkit import *
from reportlab.lib.pagesizes import A5
from reportlab.pdfgen import canvas

OUT = os.path.join(ROOT, 'print', 'StronkiesCloverSnake_Manual.pdf')
os.makedirs(os.path.dirname(OUT), exist_ok=True)
W, H = A5
M = 30
c = canvas.Canvas(OUT, pagesize=A5)
c.setTitle("Stronkie's Clover Snake - Instruction Manual")
c.setAuthor('Mark Stronks - Stronkie Soft')
c.setSubject('Amiga 500 step-by-step puzzle snake, V' + VER)
PAGE = [0]
GREENS = ['#ffffff', '#e6ffd9', '#b5f5a0', '#5ee05e', '#34c734', '#1f9e2a', '#137a20', '#0b5216']


def page(title, sub=None):
    PAGE[0] += 1
    c.setFillColor(PAPER); c.rect(0, 0, W, H, stroke=0, fill=1)
    c.setStrokeColor(PAPER2); c.setLineWidth(0.35)          # the field grid
    for gx in range(0, int(W) + 1, 14): c.line(gx, 0, gx, H)
    for gy in range(0, int(H) + 1, 14): c.line(0, gy, W, gy)
    c.setFillColor(MEADOW); c.rect(0, H - 62, W, 62, stroke=0, fill=1)
    for i in range(6):
        c.setFillColor(HexColor(['#0f4a24', '#13592b', '#186a33', '#1d7b3a', '#238d42', '#2aa14b'][i]))
        c.rect(0, H - 62 + i * 1.6, W, 1.6, stroke=0, fill=1)
    px = 2.6 if pixwidth(title, 2.6) < W - 2 * M else (W - 2 * M) / (len(title) * 8)
    pixtext(c, title, M, H - 40, px, rows=GREENS, shadow=HexColor('#000000'), sdx=1, sdy=1)
    if sub:
        c.setFillColor(FENCE); c.setFont('PopM', 7.5); c.drawString(M, H - 54, sub)
    c.setFillColor(FENCE); c.rect(0, H - 66, W, 4, stroke=0, fill=1)
    item_row(c, 6, H - 80, W - 12, 10, PAGE[0])
    c.setFillColor(MEADOW); c.rect(0, 0, W, 20, stroke=0, fill=1)
    pixtext(c, 'CLOVER SNAKE', M, 7, 1.1, lighten(GREY, 0.3))
    pixtext(c, 'AMIGA', W - M, 7, 1.1, ORANGE, right=True)
    n = str(PAGE[0])
    icon(c, 'clover', W / 2 - 8, 2, 16)
    pixtext(c, n, W / 2, 6.5, 1.0 if len(n) == 1 else 0.85, INK, center=True)
    return H - 92


def heading(text, x, y, col=HexColor('#137a20'), px=1.6):
    pixtext(c, text, x, y - 8 * px, px, col, shadow=HexColor('#00000040', hasAlpha=True))
    return y - 8 * px - 6


def item(name, title, text, y, s=22):
    icon(c, name, M, y - s, s)
    pixtext(c, title, M + s + 8, y - 9, 1.15, MEADOW)
    yb = para(c, text, M + s + 8, y - 13, W - 2 * M - s - 8, 8)
    return min(yb, y - s) - 8


# ------------------------------------------------------------------ 1: cover
PAGE[0] += 1
c.setFillColor(MEADOW); c.rect(0, 0, W, H, stroke=0, fill=1)
c.setStrokeColor(MEADOW2); c.setLineWidth(0.5)
for gx in range(0, int(W) + 1, 12): c.line(gx, 0, gx, H)
for gy in range(0, int(H) + 1, 12): c.line(0, gy, W, gy)
c.setFillColor(FENCE); c.rect(10, 10, W - 20, H - 20, stroke=0, fill=1)
c.setFillColor(MEADOW); c.rect(14, 14, W - 28, H - 28, stroke=0, fill=1)
c.setFillColor(HexColor('#050505')); c.rect(14, H - 44, W - 28, 30, stroke=0, fill=1)
pixtext(c, 'AMIGA', 24, H - 34, 1.9, white)
for i, col in enumerate([RED, ORANGE, YELLOW, GREEN, CYAN, BLUE]):
    c.setFillColor(col); c.rect(W - 84, H - 41 + i * 4, 70, 4, stroke=0, fill=1)
lw = W - 60
lh = image(c, os.path.join(ART, 'title_logo.png'), 30, H - 60 - (W - 60) * 864 / 1904, lw)
yy = H - 60 - lh
pixtext(c, 'INSTRUCTION MANUAL', W / 2, yy - 26, 1.7, FENCE, center=True, shadow=black)
sw = W - 130
yy = shot(c, 'round03.png', 65, yy - 40, sw, None, bezel=HexColor('#050505'))
c.setFillColor(white); c.setFont('PopM', 9)
c.drawCentredString(W / 2, yy - 16, 'A step-by-step puzzle snake for the Amiga 500')
lg = ImageReader(LOGO); iw, ih = lg.getSize()
c.drawImage(lg, W / 2 - 45, 30, 90, 90 * ih / iw, mask='auto')
c.setFillColor(lighten(GREY, 0.4)); c.setFont('Pop', 6.5)
c.drawCentredString(W / 2, 20, 'Version ' + VER + '  •  © 2026 Mark Stronks - Stronkie Soft')
c.showPage()

# ------------------------------------------------------------------ 2: welcome
y = page('WELCOME', 'Read this before your snake gets hungry')
y = para(c, "<b>Thank you for playing Stronkie's Clover Snake!</b> This is a snake game for the Commodore Amiga 500 - "
         "but not the kind where you race around the screen and crash into your own tail after ten seconds. "
         "This snake <b>only moves when you do</b>. One push of the joystick is one step. Nothing hurries you... "
         "except the bonus, which keeps counting down.", M, y, W - 2 * M, 9)
y = para(c, "The game was inspired by <b>Snake It</b>, a little gem for the MSX computers from 1986. Like that game it is "
         "a <b>puzzle</b> more than a race: every round is a meadow full of four-leaf clovers, and you have to eat them all. "
         "Easy? Every clover makes your snake longer, every bite makes a poison mushroom grow somewhere, and your own long "
         "body is the biggest wall on the field.", M, y - 8, W - 2 * M, 9)
y = shot(c, 'title.png', M + 75, y - 12, W - 2 * M - 150, 'The title screen. Wait a while and it shows you how to play.')
y = factbox(c, M, y - 12, W - 2 * M, 'CONTENTS',
            'Loading the game .... 3<br/>Controls .... 4<br/>How to play .... 5<br/>Spores and mushrooms .... 6<br/>'
            'Crates and getting stuck .... 7<br/>Scoring .... 8<br/>The twelve rounds .... 9-10<br/>Tips and tricks .... 11<br/>Credits .... 12',
            YELLOW, 7.6)
c.showPage()

# ------------------------------------------------------------------ 3: loading
y = page('LOADING', 'Floppy, hard drive or WHDLoad')
y = heading('WHAT YOU NEED', M, y)
y = para(c, '<b>Amiga 500</b> with a 68000 processor, <b>Kickstart / Workbench 3.1</b> (1.3 works too), <b>1 MB chip memory</b> '
         '(the game also fits in 512 KB) and a joystick in port 2 - or just the cursor keys. It runs just as well in WinUAE, '
         'on a Gotek or from a CF card.', M, y, W - 2 * M, 8.6)
ways = [('FROM FLOPPY DISK', 'Switch off your Amiga, put the game disk in the internal drive and switch on. The game starts all by itself.'),
        ('FROM WORKBENCH', 'Open the disk icon and double-click <b>CloverSnake</b>. Or type <font face="PopB">CloverSnake</font> in the CLI.'),
        ('ON A HARD DRIVE', 'Double-click <b>Install</b> on the game disk and choose a drive: it makes the drawer <b>StronkiesCloverSnake</b>. '
         'Or unpack the hard drive zip anywhere you like.'),
        ('WHDLOAD', 'Unpack the WHDLoad zip and double-click the icon (WHDLoad must be installed). '
         '<b>F10</b> quits back to Workbench - on the Stronkie Soft CF card it is the <b>Help</b> key.')]
y -= 6
for t, txt in ways:
    pixtext(c, t, M, y - 9, 1.15, MAGENTA)
    y = para(c, txt, M, y - 13, W - 2 * M, 8.2) - 7
y = factbox(c, M, y - 4, W - 2 * M, 'PLEASE NOTE',
            'Escape on the title screen takes you back to Workbench. The game does not write to the disk, so the disk may '
            'stay write-protected.', CYAN, 7.6)
c.showPage()

# ------------------------------------------------------------------ 4: controls
y = page('CONTROLS', 'One push - one step')
rows = [('JOYSTICK UP/DOWN/LEFT/RIGHT', 'The snake takes one step that way. Hold the stick and it keeps going, step by step.'),
        ('CURSOR KEYS', 'Exactly the same as the joystick.'),
        ('FIRE  /  SPACE  /  RETURN', 'Start the game. Skip the "ROUND" and "GET READY" messages.'),
        ('R  or  HOLD FIRE', 'Retry the round - for when you have boxed yourself in. It costs a life.'),
        ('P', 'Pause. Press P again (or fire) to go on.'),
        ('M', 'Music on / off (also on the title screen).'),
        ('ESC', 'Back to the title screen. On the title screen: back to Workbench.')]
for k, txt in rows:
    c.setFillColor(MEADOW); c.roundRect(M, y - 15, W - 2 * M, 15, 3, stroke=0, fill=1)
    pixtext(c, k, M + 6, y - 11, 1.0, FENCE)
    y = para(c, txt, M + 4, y - 18, W - 2 * M - 8, 8.2) - 9
y = factbox(c, M, y - 2, W - 2 * M, 'NO GOING BACK',
            'Pushing the stick straight back the way you came does nothing - your snake will not bite its own neck. '
            'Every other direction counts, so think before you push!', ORANGE, 7.6)
c.showPage()

# ------------------------------------------------------------------ 5: how to play
y = page('HOW TO PLAY', 'Eat everything - and stay alive')
y = para(c, 'Every round is a fenced meadow. Your snake starts near the bottom, facing up. <b>Clear the round by eating every clover '
         'and every white ball.</b>', M, y, W - 2 * M, 8.6) - 10
y = item('clover', 'CLOVER  20 POINTS', 'Your snake grows two pieces longer, and a white ball pops up somewhere on the field - always in a spot you can still reach.', y)
y = item('ball', 'BALL  50 POINTS', 'Eat these too: the round is not clear until every ball is gone. Balls do not make you grow.', y)
y = item('heart', 'HEART  100 POINTS', 'Now and then a heart drifts across the meadow, bouncing off everything. Catch it for 100 points and a bigger '
         'bonus multiplier (up to x9). It blinks before it flies away.', y)
y = item('mush', 'POISON MUSHROOM', 'Touch one and you lose a life. So do the walls, the yellow fence and your own tail.', y)
y = item('block', 'CRATE', 'Walk into it to push it one step - see page 7.', y)
y = item('spore', 'SPORE', 'A mushroom is waiting to grow here - see page 6.', y)
c.showPage()

# ------------------------------------------------------------------ 6: spores
y = page('SPORES', 'Every bite grows a mushroom')
y = para(c, 'Look closely at the meadow: here and there are little <b>red dots</b>. Those are <b>spores</b>. Every time you eat '
         'something - a clover <i>or</i> a ball - a poison mushroom grows on the <b>next</b> spore. The next one is the one that '
         '<b>blinks</b>.', M, y, W - 2 * M, 8.6)
icon(c, 'spore', M + 40, y - 40, 26); icon(c, 'spore2', M + 80, y - 40, 26)
c.setFillColor(INK); c.setFont('PopB', 14); c.drawString(M + 118, y - 32, '→')
icon(c, 'mush', M + 140, y - 40, 26)
y -= 50
y = para(c, 'So the <b>order</b> in which you eat changes the meadow: a mushroom can close a narrow passage you still need, '
         'or wall off the last clover.', M, y, W - 2 * M, 8.6)
y = factbox(c, M, y - 10, W - 2 * M, 'THE TAIL TRICK',
            'Is something lying on the spore when its turn comes - <b>your own tail</b>, a <b>crate</b> or the <b>heart</b>? '
            'Then <b>nothing grows</b>, and that spore is gone for good! Park your long body across a narrow passage before you '
            'take a bite, and the passage stays open.', GREEN, 7.8)
y = shot(c, 'crates_spores.png', M + 30, y - 12, W - 2 * M - 60, 'A crate pushed, a mushroom grown on a spore - and more red dots waiting.')
c.showPage()

# ------------------------------------------------------------------ 7: crates and stuck
y = page('CRATES', 'Push, block, escape')
y = para(c, 'Walk into a <b>crate</b> and you push it one step - if the place behind it is free. If it is not (a wall, a clover, '
         'a mushroom, another crate), the crate does not move and your snake simply stays where it is. Bumping into a crate never costs a life.',
         M, y, W - 2 * M, 8.6)
y = para(c, 'Crates are your tools: push one aside to <b>open a blocked door</b>, line them up to <b>build a safe path</b> for '
         'your long tail, or push one onto a <b>spore</b> so no mushroom can grow there.', M, y - 6, W - 2 * M, 8.6)
y = shot(c, 'round03.png', M + 30, y - 12, W - 2 * M - 60, 'Round 3, The Crate Door: four crates keep the clovers locked in.')
y = heading('STUCK?', M, y - 10)
y = para(c, 'It happens to the best snakes: you have boxed yourself in, or a mushroom has cut off the last ball. '
         'Press <b>R</b>, or hold <b>fire</b> for a second: the round starts again exactly as it was at the start. '
         'It costs a life. Losing a life in any other way also restarts the round.', M, y, W - 2 * M, 8.6)
c.showPage()

# ------------------------------------------------------------------ 8: scoring
y = page('SCORING', 'Clovers, balls, hearts and the bonus')
tab = [('clover', 'Clover', '20'), ('ball', 'Ball', '50'), ('heart', 'Heart', '100 + multiplier +1'),
       ('clover', 'Round clear', 'bonus left x multiplier')]
for nm, t, v in tab:
    icon(c, nm, M, y - 18, 16)
    c.setFillColor(INK); c.setFont('PopB', 9); c.drawString(M + 24, y - 13, t)
    c.setFont('PopM', 9); c.drawRightString(W - M, y - 13, v)
    c.setStrokeColor(PAPER2); c.line(M, y - 22, W - M, y - 22)
    y -= 26
y = heading('THE BONUS', M, y - 8)
y = para(c, 'Every round starts with a <b>bonus of 1000</b>, shown at the top right. It drops by 10 a little under '
         'every second. When you clear the round, what is left is added to your score - <b>times the multiplier</b> '
         '(the number after the small x). Each heart you catch adds one to the multiplier, up to x9. '
         'After round 12 the rounds come back, and the bonus drops faster.', M, y, W - 2 * M, 8.6)
y = heading('EXTRA LIVES', M, y - 10)
y = para(c, 'You start with <b>three lives</b> and get an <b>extra life every 10000 points</b>. The best score of the '
         'day is shown on the title screen.', M, y, W - 2 * M, 8.6)
y = shot(c, 'heart.png', M + 40, y - 12, W - 2 * M - 80, 'A heart on the loose. Quick - before it blinks away!')
c.showPage()

# ------------------------------------------------------------------ 9-10: the rounds
ROUNDS = [('FIRST STEPS', 'An open meadow to learn the ropes: clovers, a few mushrooms, three crates.'),
          ('THREE WALLS', 'Long walls from the top and the bottom, and clumps of four clovers.'),
          ('THE CRATE DOOR', 'The clovers are locked in a box. Push the crates in to open the door.'),
          ('SHELVES', 'Clovers on long shelves - mind the narrow ends.'),
          ('FOUR ROOMS', 'Every room has a crate for a door.'),
          ('PILLARS', 'A field of pillars with crates in between.'),
          ('MUSHROOM FOREST', 'Poison everywhere. Watch every step.'),
          ('THE SPIRAL', 'Wind your way in - and out again.'),
          ('THE COMB', 'Narrow gaps between long teeth: the spores love them.'),
          ('DIAMOND', 'A diamond of walls with treasure inside.'),
          ('CORRIDORS', 'Long corridors with the way out at the other end.'),
          ('THE GRAND FINALE', 'Everything at once. Good luck!')]
for half in (0, 1):
    y = page('THE ROUNDS', 'Rounds %d to %d' % (half * 6 + 1, half * 6 + 6))
    tw = (W - 2 * M - 12) / 2
    for k in range(6):
        i = half * 6 + k
        col, row = k % 2, k // 2
        x = M + col * (tw + 12)
        yt = y - row * 160
        name, txt = ROUNDS[i]
        pixtext(c, '%d %s' % (i + 1, name), x, yt - 8, 0.95 if len(name) < 14 else 0.82, MEADOW)
        yb = shot(c, 'round%02d.png' % (i + 1), x + 12, yt - 14, tw - 24)
        para(c, txt, x, yb - 3, tw, 6.8)
    c.showPage()

# ------------------------------------------------------------------ 11: tips
y = page('TIPS & TRICKS', 'From one snake to another')
tips = ['<b>Look before you eat.</b> Find the blinking spore first. If it sits in a passage you still need, cover it with your body - or eat somewhere else first.',
        '<b>Leave yourself a way out.</b> A long snake in a dead end is a stuck snake. Clear the far corners while you are still short.',
        '<b>Balls always appear where you can reach them</b> - at the moment they appear. Mushrooms and crates can change that later.',
        '<b>Crates do not kill.</b> If you are not sure, bump into one: the worst that can happen is nothing.',
        '<b>Hearts are worth chasing</b> early in a round: the multiplier counts for the whole bonus.',
        '<b>The tail moves too.</b> You may step onto the cell your tail is just leaving - unless you have just eaten and are growing.',
        '<b>Take your time.</b> Nothing moves until you do - only the bonus and the hearts.']
for t in tips:
    icon(c, 'clover', M, y - 12, 11)
    y = para(c, t, M + 17, y, W - 2 * M - 17, 8.4) - 8
y = factbox(c, M, y - 6, W - 2 * M, 'DID YOU KNOW?',
            'The whole game - graphics, rounds, music and sound effects - fits in about <b>17 KB</b> on the disk. '
            'Your snake can grow to more than 900 pieces... but we have never seen one get that far.', MAGENTA, 7.6)
c.showPage()

# ------------------------------------------------------------------ 12: credits / back
PAGE[0] += 1
c.setFillColor(MEADOW); c.rect(0, 0, W, H, stroke=0, fill=1)
c.setStrokeColor(MEADOW2); c.setLineWidth(0.5)
for gx in range(0, int(W) + 1, 12): c.line(gx, 0, gx, H)
for gy in range(0, int(H) + 1, 12): c.line(0, gy, W, gy)
pixtext(c, 'CREDITS', W / 2, H - 70, 2.6, rows=GREENS, shadow=black, center=True)
y = H - 92
for k, v in (('CREATED BY', 'Mark Stronks, Stronkie Soft'), ('INSPIRED BY', 'Snake It (MSX, 1986)'),
             ('PROGRAMMING HELP', 'Claude (AI)'), ('MADE FOR', 'The Commodore Amiga 500'), ('YEAR', '2026')):
    pixtext(c, k, W / 2, y - 9, 1.2, FENCE, center=True)
    c.setFillColor(white); c.setFont('PopM', 10); c.drawCentredString(W / 2, y - 24, v)
    y -= 40
snake_line(c, W / 2 - 70, y - 30, 7, 20)
icon(c, 'clover', W / 2 + 80, y - 30, 20)
lg = ImageReader(LOGO); iw, ih = lg.getSize()
c.drawImage(lg, W / 2 - 70, 60, 140, 140 * ih / iw, mask='auto')
c.setFillColor(lighten(GREY, 0.4)); c.setFont('Pop', 6.5)
c.drawCentredString(W / 2, 44, 'More Stronkie Soft games for your Amiga: stronkie.itch.io')
c.drawCentredString(W / 2, 34, "© 2026 Mark Stronks - Stronkie Soft. Copy the disk for yourself, not for the whole street.")
c.showPage()
c.save()
print('wrote', OUT, PAGE[0], 'pages')
