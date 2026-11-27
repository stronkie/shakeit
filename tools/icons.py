#!/usr/bin/env python3
"""icons.py - Workbench icons for Stronkie's Clover Snake (WB 3.1 colours:
0 grey, 1 black, 2 white, 3 blue).  Writes them into build/icons/.
Uses diskobject() from the toolkit's make_whdload.py."""
import os, sys
from PIL import Image, ImageDraw
TK = os.environ.get('AMIGA_TK', '/home/claude/amiga-toolkit')
sys.path.insert(0, os.path.join(TK, 'tools'))
argv = sys.argv; sys.argv = [argv[0], '0']
import make_whdload as mw
import make_disk as md
sys.argv = argv
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, 'build', 'icons'); os.makedirs(OUT, exist_ok=True)

def snake_image():
    W, H = 52, 30
    im = Image.new('P', (W, H), 0); d = ImageDraw.Draw(im)
    # a blue snake in an S with a black outline, white eye, chasing a clover
    pts = [(6, 22), (16, 22), (20, 18), (20, 12), (24, 8), (34, 8)]
    d.line(pts, fill=1, width=7)
    d.line(pts, fill=3, width=5)
    d.ellipse([31, 3, 41, 13], fill=3, outline=1)
    d.point((37, 6), fill=2); d.point((38, 6), fill=2); d.point((37, 7), fill=1)
    d.line([41, 9, 44, 9], fill=1)
    for (x, y) in ((45, 18), (49, 18), (45, 22), (49, 22)):     # the clover
        d.ellipse([x - 2, y - 2, x + 1, y + 1], fill=1)
    d.line([47, 22, 47, 27], fill=1)
    return im

def readme_image():
    W, H = 40, 26
    im = Image.new('P', (W, H), 0); d = ImageDraw.Draw(im)
    d.rectangle([8, 1, 31, 24], fill=2, outline=1)
    for y in range(5, 22, 3):
        d.line([11, y, 28, y], fill=1 if y % 2 else 3)
    return im

def save(name, data):
    open(os.path.join(OUT, name), 'wb').write(data)

save('CloverSnake.info', mw.diskobject(3, snake_image()))
save('Install.info', mw.diskobject(3, md.install_image()))
save('ReadMe.txt.info', mw.diskobject(4, readme_image(), tool='SYS:Utilities/MultiView'))
save('drawer.info', mw.diskobject(2, md.drawer_image()))
save('whdload.info', mw.diskobject(4, snake_image(), tool='WHDLoad',
                                   tooltypes=('SLAVE=CloverSnake.slave', 'PRELOAD')))
im = snake_image(); im.putpalette([170, 170, 170, 0, 0, 0, 255, 255, 255, 100, 136, 187] + [0] * 756)
im.convert('RGB').resize((52 * 4, 30 * 4), Image.NEAREST).save(os.path.join(ROOT, 'art', 'icon_preview.png'))
print('icons ->', OUT)
