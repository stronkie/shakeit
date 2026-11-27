#!/usr/bin/env python3
"""export_art.py - the game's own font (art/print/font.bin, 96 x 8 bytes, ASCII 32-127),
the item tiles as big PNGs and the title logo with a transparent background,
for the print kit (manual, box, labels)."""
import os, sys
import numpy as np
from PIL import Image
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, 'tools'))
import gen
OUT = os.path.join(ROOT, 'art', 'print')
os.makedirs(OUT, exist_ok=True)
fb = bytearray()
for code in range(32, 128):
    ch = chr(code)
    if 'a' <= ch <= 'z':
        ch = ch.upper()
    g = gen.glyph(ch) if (ch in gen.FONT) else np.zeros((8, 8), bool)
    for y in range(8):
        v = 0
        for x in range(8):
            if g[y, x]:
                v |= 0x80 >> x
        fb.append(v)
open(os.path.join(OUT, 'font.bin'), 'wb').write(bytes(fb))
def rgba(t, scale):
    h, w = t.shape
    im = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    px = im.load()
    for y in range(h):
        for x in range(w):
            if t[y, x]:
                px[x, y] = gen.rgb(t[y, x]) + (255,)
    return im.resize((w * scale, h * scale), Image.NEAREST)
for n in ('CLOVER', 'BALL', 'MUSH', 'HEART', 'BLOCK', 'SPORE', 'SPORE2', 'HEAD0', 'HEAD1', 'SNAKE10', 'SNAKE5', 'SNAKE8', 'SNAKE2', 'WALL10', 'DEADHEAD'):
    rgba(gen.tiles[gen.names[n]], 32).save(os.path.join(OUT, n.lower() + '.png'))
# the title logo (STRONKIE'S / CLOVER / SNAKE + the little snake) without the black
title = gen.make_title()
crop = title[52:164, :]
ys, xs = np.nonzero(crop)
crop = crop[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
rgba(crop, 8).save(os.path.join(OUT, 'title_logo.png'))
# the Stronkie Soft logo is used as it is (toolkit art)
print('art ->', OUT)
