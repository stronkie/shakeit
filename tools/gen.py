#!/usr/bin/env python3
"""gen.py - makes src/gfx_gen.s for Stronkie's Clover Snake:
palette, 8x8 tiles (font, walls, snake, items), the intro and title
pictures, the rounds, the waveforms, sound effects and music.

  python3 tools/gen.py            (from the project folder; needs $AMIGA_TK or ../amiga-toolkit)
"""
import os, sys, random
from collections import deque
import numpy as np
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TK = os.environ.get('AMIGA_TK', os.path.join(os.path.dirname(ROOT), 'amiga-toolkit'))
OUT = os.path.join(ROOT, 'src', 'gfx_gen.s')
PREV = os.path.join(ROOT, 'art')

# ------------------------------------------------------------------ palette
PAL = [
    (0x0, 0x0, 0x0),   # 0 black
    (0xF, 0xF, 0xF),   # 1 white
    (0xB, 0xB, 0xC),   # 2 light grey
    (0x5, 0x5, 0x6),   # 3 dark grey
    (0xE, 0xE, 0x2),   # 4 yellow
    (0x9, 0x8, 0x1),   # 5 dark yellow
    (0x3, 0xD, 0x3),   # 6 green
    (0x1, 0x7, 0x2),   # 7 dark green
    (0x4, 0xC, 0xF),   # 8 cyan (snake)
    (0x1, 0x6, 0xB),   # 9 blue (snake shade)
    (0xE, 0x3, 0x2),   # 10 red
    (0x8, 0x1, 0x1),   # 11 dark red
    (0xF, 0x8, 0xB),   # 12 pink
    (0xE, 0x9, 0x0),   # 13 orange
    (0xF, 0xF, 0xA),   # 14 pale yellow
    (0xE, 0xD, 0xA),   # 15 cream
]
CH = {'.': 0, 'W': 1, 'g': 2, 'd': 3, 'Y': 4, 'y': 5, 'G': 6, 'h': 7, 'C': 8, 'b': 9,
      'R': 10, 'r': 11, 'P': 12, 'O': 13, 'L': 14, 'n': 15}

def art(rows):
    return np.array([[CH[c] for c in r] for r in rows], dtype=np.uint8)

# ------------------------------------------------------------------ font
FONT = {
' ': ["......."] * 7,
'A': ["..###..", ".##.##.", "##...##", "##...##", "#######", "##...##", "##...##"],
'B': ["######.", "##...##", "##...##", "######.", "##...##", "##...##", "######."],
'C': [".#####.", "##...##", "##.....", "##.....", "##.....", "##...##", ".#####."],
'D': ["#####..", "##..##.", "##...##", "##...##", "##...##", "##..##.", "#####.."],
'E': ["#######", "##.....", "##.....", "######.", "##.....", "##.....", "#######"],
'F': ["#######", "##.....", "##.....", "######.", "##.....", "##.....", "##....."],
'G': [".#####.", "##...##", "##.....", "##.####", "##...##", "##...##", ".######"],
'H': ["##...##", "##...##", "##...##", "#######", "##...##", "##...##", "##...##"],
'I': ["######.", "..##...", "..##...", "..##...", "..##...", "..##...", "######."],
'J': ["....##.", "....##.", "....##.", "....##.", "##..##.", "##..##.", ".####.."],
'K': ["##...##", "##..##.", "##.##..", "####...", "##.##..", "##..##.", "##...##"],
'L': ["##.....", "##.....", "##.....", "##.....", "##.....", "##.....", "#######"],
'M': ["##...##", "###.###", "#######", "##.#.##", "##...##", "##...##", "##...##"],
'N': ["##...##", "###..##", "####.##", "##.####", "##..###", "##...##", "##...##"],
'O': [".#####.", "##...##", "##...##", "##...##", "##...##", "##...##", ".#####."],
'P': ["######.", "##...##", "##...##", "######.", "##.....", "##.....", "##....."],
'Q': [".#####.", "##...##", "##...##", "##...##", "##.#.##", "##..##.", ".###.##"],
'R': ["######.", "##...##", "##...##", "######.", "##.##..", "##..##.", "##...##"],
'S': [".#####.", "##...##", "##.....", ".#####.", ".....##", "##...##", ".#####."],
'T': ["######.", "..##...", "..##...", "..##...", "..##...", "..##...", "..##..."],
'U': ["##...##", "##...##", "##...##", "##...##", "##...##", "##...##", ".#####."],
'V': ["##...##", "##...##", "##...##", "##...##", ".##.##.", "..###..", "...#..."],
'W': ["##...##", "##...##", "##...##", "##.#.##", "#######", "###.###", "##...##"],
'X': ["##...##", ".##.##.", "..###..", "..###..", ".##.##.", "##...##", "##...##"],
'Y': ["##..##.", "##..##.", "##..##.", ".####..", "..##...", "..##...", "..##..."],
'Z': ["#######", "....##.", "...##..", "..##...", ".##....", "##.....", "#######"],
'0': [".#####.", "##..###", "##.####", "####.##", "###..##", "##...##", ".#####."],
'1': ["..##...", ".###...", "..##...", "..##...", "..##...", "..##...", "######."],
'2': [".#####.", "##...##", ".....##", "..####.", ".##....", "##.....", "#######"],
'3': [".#####.", "##...##", ".....##", "..####.", ".....##", "##...##", ".#####."],
'4': ["...###.", "..####.", ".##.##.", "##..##.", "#######", "....##.", "....##."],
'5': ["#######", "##.....", "######.", ".....##", ".....##", "##...##", ".#####."],
'6': [".#####.", "##.....", "##.....", "######.", "##...##", "##...##", ".#####."],
'7': ["#######", "##...##", "....##.", "...##..", "..##...", "..##...", "..##..."],
'8': [".#####.", "##...##", "##...##", ".#####.", "##...##", "##...##", ".#####."],
'9': [".#####.", "##...##", "##...##", ".######", ".....##", "....##.", ".####.."],
':': [".......", "..##...", "..##...", ".......", "..##...", "..##...", "......."],
'.': [".......", ".......", ".......", ".......", ".......", "..##...", "..##..."],
',': [".......", ".......", ".......", ".......", "..##...", "..##...", ".##...."],
'!': ["..##...", "..##...", "..##...", "..##...", "..##...", ".......", "..##..."],
'?': [".#####.", "##...##", "....##.", "...##..", "...##..", ".......", "...##.."],
'-': [".......", ".......", ".......", ".#####.", ".......", ".......", "......."],
'+': [".......", "..##...", "..##...", "######.", "..##...", "..##...", "......."],
'=': [".......", ".......", "######.", ".......", "######.", ".......", "......."],
'/': [".....##", "....##.", "...##..", "..##...", ".##....", "##.....", "#......"],
'(': ["...##..", "..##...", ".##....", ".##....", ".##....", "..##...", "...##.."],
')': [".##....", "..##...", "...##..", "...##..", "...##..", "..##...", ".##...."],
"'": ["..##...", "..##...", ".##....", ".......", ".......", ".......", "......."],
'"': [".##.##.", ".##.##.", ".##.##.", ".......", ".......", ".......", "......."],
'*': [".......", ".......", ".##.##.", "..###..", ".##.##.", ".......", "......."],  # small x
'@': [".#####.", "#.....#", "#.###.#", "#.#...#", "#.###.#", "#.....#", ".#####."],  # (c)
'%': ["##...##", "##..##.", "...##..", "..##...", ".##....", "##..##.", "#...##."],
'&': ["..##...", ".#..#..", "..##...", ".###.#.", "#..##..", "#...#..", ".###.#."],
'#': [".##.##.", "#######", ".##.##.", ".##.##.", "#######", ".##.##.", "......."],
'<': ["...##..", "..##...", ".##....", "##.....", ".##....", "..##...", "...##.."],
'>': ["##.....", ".##....", "..##...", "...##..", "..##...", ".##....", "##....."],
}
FONTCHARS = [chr(c) for c in range(32, 96)]

def glyph(ch):
    g = FONT.get(ch, FONT['?'] if ch not in FONT else None) or FONT['?']
    a = np.zeros((8, 8), bool)
    for y, r in enumerate(g):
        for x, c in enumerate(r):
            a[y, x] = c == '#'
    return a

def font_tile(ch, top, bottom, shadow=3):
    g = glyph(ch)
    t = np.zeros((8, 8), np.uint8)
    for y in range(8):
        for x in range(8):
            if g[y, x]:
                t[y, x] = top if y < 4 else bottom
            elif shadow and ((y > 0 and x > 0 and g[y - 1, x - 1]) or (x > 0 and g[y, x - 1])):
                t[y, x] = shadow
    return t

# ------------------------------------------------------------------ tiles
tiles = []
names = {}
def add(name, t):
    names[name] = len(tiles)
    tiles.append(np.array(t, np.uint8))

add('EMPTY', np.zeros((8, 8)))
add('CLOVER', art([
    ".GG..GG.",
    "GGGhGGGh",
    "GGGGGGGh",
    ".hGGGGh.",
    ".GGGGGG.",
    "GGGGhGGh",
    "GGGhhGGh",
    ".hh..hh."]))
add('BALL', art([
    "..WWWW..",
    ".WdWWdW.",
    "WWWWWWWg",
    "WdWWWdWg",
    "WWWWWWWg",
    "WWdWWdgg",
    ".gWWWWg.",
    "..gggg.."]))
add('MUSH', art([
    "..RRRR..",
    ".RWRRWR.",
    "RRRRRRRr",
    "RWRRRWRr",
    ".rrrrrr.",
    "...nn...",
    "..nnnn..",
    "..nggn.."]))
add('HEART', art([
    ".RR..RR.",
    "RPWRRRRr",
    "RPRRRRRr",
    "RRRRRRRr",
    ".RRRRRr.",
    "..RRRr..",
    "...Rr...",
    "........"]))
add('HEART2', art([           # blinking frame (dim)
    ".rr..rr.",
    "rRPrrrr.",
    "rRrrrrr.",
    "rrrrrrr.",
    ".rrrrr..",
    "..rrr...",
    "...r....",
    "........"]))

add('BLOCK', art([           # a wooden crate you can push
    "LLLLLLLO",
    "LOOyOOyy",
    "LOLOOyOy",
    "LOOLyOOy",
    "LOOyLOOy",
    "LOyOOLOy",
    "LyOOyOLy",
    "Oyyyyyyy"]))
add('SPORE', art([           # a mushroom will grow here
    "........",
    ".r...R..",
    "........",
    "...R..r.",
    ".R......",
    "....r...",
    "..R...R.",
    "........"]))
add('SPORE2', art([          # the next one (blinks)
    "........",
    ".R...P..",
    "...r....",
    "...P..R.",
    ".P....r.",
    "..r.R...",
    "..P...P.",
    "........"]))

def shaded(region, fill, hi, lo):
    t = np.zeros((8, 8), np.uint8)
    for y in range(8):
        for x in range(8):
            if not region[y][x]:
                continue
            def inside(xx, yy):
                if xx < 0 or yy < 0 or xx > 7 or yy > 7:
                    return True        # the tube goes on into the next cell
                return region[yy][xx]
            c = fill
            if not inside(x + 1, y) or not inside(x, y + 1):
                c = lo
            elif not inside(x - 1, y) or not inside(x, y - 1):
                c = hi
            t[y, x] = c
    return t

# connection bits: 1 up, 2 right, 4 down, 8 left
def tube(mask, a, b, round_end=False):
    """region of a tube a..b wide (inclusive) going to the connected sides"""
    reg = [[False] * 8 for _ in range(8)]
    for y in range(a, b + 1):
        for x in range(a, b + 1):
            reg[y][x] = True
    if round_end:
        for (x, y) in ((a, a), (b, a), (a, b), (b, b)):
            reg[y][x] = False
    for bit, (xs, ys) in ((1, (range(a, b + 1), range(0, a))), (4, (range(a, b + 1), range(b + 1, 8))),
                          (8, (range(0, a), range(a, b + 1))), (2, (range(b + 1, 8), range(a, b + 1)))):
        if mask & bit:
            for y in ys:
                for x in xs:
                    reg[y][x] = True
    if round_end and mask:
        # keep the corner pixels on the connected side
        if mask & 1: reg[a][a] = reg[a][b] = True
        if mask & 4: reg[b][a] = reg[b][b] = True
        if mask & 8: reg[a][a] = reg[b][a] = True
        if mask & 2: reg[a][b] = reg[b][b] = True
    return reg

# walls: 16 auto tiles (by the wall neighbours)
for m in range(16):
    add('WALL%d' % m, shaded(tube(m, 2, 5), CH['Y'], CH['L'], CH['y']))

# snake body: 16 tiles by connections (1 bit = tail end, 2 bits = body)
for m in range(16):
    nb = bin(m).count('1')
    t = shaded(tube(m, 1, 6, round_end=(nb <= 1)), CH['C'], CH['W'], CH['b'])
    if nb == 2 and m in (5, 10):          # straight: a segment mark
        if m == 5:
            t[7, 3] = t[7, 4] = CH['b']
        else:
            t[3, 7] = t[4, 7] = CH['b']
    add('SNAKE%d' % m, t)

# heads (dir 0 up, 1 right, 2 down, 3 left): round head, eyes to the front
head_up = art([
    "..CCCC..",
    ".CWCCWC.",
    "CWd.Wd.b",
    "CCCCCCCb",
    "CCCCCCCb",
    "CCCCCCCb",
    ".CCCCCb.",
    ".CCCCCb."])
def rot(t, k):   # k quarter turns clockwise
    return np.rot90(t, -k)
heads = [head_up, rot(head_up, 1), rot(head_up, 2), rot(head_up, 3)]
# re-shade after rotating (light from top-left)
for d in range(4):
    h = heads[d].copy()
    reg = [[h[y, x] != 0 for x in range(8)] for y in range(8)]
    sh = shaded(reg, CH['C'], CH['W'], CH['b'])
    for y in range(8):
        for x in range(8):
            if h[y, x] in (CH['C'], CH['W'], CH['b']):
                h[y, x] = sh[y, x]
    add('HEAD%d' % d, h)
# a dead head (x eyes) for the death flash
dead = art([
    "..CCCC..",
    ".CCCCCC.",
    "CdCCCdCb",
    "CCdCdCCb",
    "CdCCCdCb",
    "CCCCCCCb",
    ".CCCCCb.",
    ".CCCCCb."])
add('DEADHEAD', dead)

FONTW = len(tiles)
names['FONTW'] = FONTW
for ch in FONTCHARS:
    tiles.append(font_tile(ch, CH['W'], CH['g']))
names['FONTY'] = len(tiles)
for ch in FONTCHARS:
    tiles.append(font_tile(ch, CH['L'], CH['Y'], shadow=5))
names['FONTG'] = len(tiles)
for ch in FONTCHARS:
    tiles.append(font_tile(ch, CH['G'], CH['h']))
names['FONTC'] = len(tiles)
for ch in FONTCHARS:
    tiles.append(font_tile(ch, CH['C'], CH['b']))
NTILES = len(tiles)

def rgb(c):
    return tuple(v * 17 for v in PAL[c])

def tiles_preview():
    cols = 32
    rows = (NTILES + cols - 1) // cols
    im = Image.new('RGB', (cols * 9, rows * 9), (40, 40, 60))
    px = im.load()
    for i, t in enumerate(tiles):
        ox, oy = (i % cols) * 9, (i // cols) * 9
        for y in range(8):
            for x in range(8):
                px[ox + x, oy + y] = rgb(t[y, x])
    im.resize((im.width * 3, im.height * 3), Image.NEAREST).save(os.path.join(PREV, 'tiles_preview.png'))

# ------------------------------------------------------------------ pictures
W, H = 320, 256
def new_pic():
    return np.zeros((H, W), np.uint8)

def nearest(r, g, b):
    best, bd = 0, 1e9
    for i, (pr, pg, pb) in enumerate(PAL):
        d = (r - pr * 17) ** 2 * 3 + (g - pg * 17) ** 2 * 6 + (b - pb * 17) ** 2
        if d < bd:
            best, bd = i, d
    return best

def paste_logo(pic, x0, y0, scale):
    lg = Image.open(os.path.join(TK, 'art', 'stronkiesoft_logo.png')).convert('RGBA')
    w, h = lg.size
    px = lg.load()
    for y in range(h):
        for x in range(w):
            r, g, b, a = px[x, y]
            if a < 128:
                continue
            c = nearest(r, g, b)
            pic[y0 + y * scale:y0 + (y + 1) * scale, x0 + x * scale:x0 + (x + 1) * scale] = c

def big_text(pic, text, x0, y0, scale, top, bottom, outline=0, shadow=3):
    """the font scaled up, two colours, a shadow and an outline"""
    n = len(text)
    gw = 8 * scale
    mask = np.zeros((8 * scale, n * gw), bool)
    for i, ch in enumerate(text):
        g = glyph(ch)
        big = np.kron(g, np.ones((scale, scale), bool))
        mask[:, i * gw:(i + 1) * gw] |= big
    hh, ww = mask.shape
    # shadow
    for y in range(hh):
        for x in range(ww):
            if mask[y, x]:
                sy, sx = y0 + y + scale, x0 + x + scale
                if 0 <= sy < H and 0 <= sx < W:
                    pic[sy, sx] = shadow
    # outline
    for y in range(hh):
        for x in range(ww):
            if mask[y, x]:
                for dy in (-1, 0, 1):
                    for dx in (-1, 0, 1):
                        sy, sx = y0 + y + dy, x0 + x + dx
                        if 0 <= sy < H and 0 <= sx < W and not (0 <= y + dy < hh and 0 <= x + dx < ww and mask[y + dy, x + dx]):
                            pic[sy, sx] = outline
    for y in range(hh):
        for x in range(ww):
            if mask[y, x]:
                c = top if y < hh * 0.5 else bottom
                if y == 0 or (y > 0 and not mask[y - 1, x]):
                    c = 1 if top != 1 else 2
                pic[y0 + y, x0 + x] = c

def put_tile(pic, name, x0, y0, scale=1):
    t = tiles[names[name]]
    big = np.kron(t, np.ones((scale, scale), np.uint8))
    for y in range(big.shape[0]):
        for x in range(big.shape[1]):
            if big[y, x]:
                pic[y0 + y, x0 + x] = big[y, x]

# the painted pictures (tools/paint.py): colours 0-15 are the game's,
# 16-28 the picture's own, 29-31 the fireflies (they twinkle in the game)
import paint
FIRE_PAL = [(15, 15, 9), (10, 12, 5), (6, 9, 4)]
_meadow = None
def meadow_rgb():
    global _meadow
    if _meadow is None:
        _meadow = paint.meadow()
    return _meadow

def text_mask(text, scale):
    n = len(text)
    m = np.zeros((8 * scale, n * 8 * scale), bool)
    for i, ch in enumerate(text):
        m[:, i * 8 * scale:(i + 1) * 8 * scale] |= np.kron(glyph(ch), np.ones((scale, scale), bool))
    return m

def halo(rgb, items, amount=0.6, blur=3.0):
    """darken the picture softly around big text so it stands out"""
    from scipy.ndimage import gaussian_filter, binary_dilation
    m = np.zeros((H, W), np.float32)
    for text, x0, y0, scale in items:
        tm = text_mask(text, scale)
        tm = binary_dilation(tm, iterations=scale)
        hh, ww = tm.shape
        m[y0:y0 + hh, x0:x0 + ww] = np.maximum(m[y0:y0 + hh, x0:x0 + ww], tm)
    m = np.clip(gaussian_filter(m, blur) * 2.2, 0, 1)
    return rgb * (1 - amount * m)[..., None]

def finish(rgb, fire, seed=1, dither=10.0):
    idx, pal = paint.quantize(rgb, {i: PAL[i] for i in range(16)}, 13, 16, seed=seed, dither=dither)
    for i, c in enumerate(FIRE_PAL):
        pal[29 + i] = c
    for x, y, c in fire:
        idx[y, x] = c
    return idx, pal

def fence(pic, c0, r0, c1, r1):
    """a frame of the game's walls (8x8 tiles) from cell c0,r0 to c1,r1"""
    for r in range(r0, r1 + 1):
        for c in range(c0, c1 + 1):
            if r not in (r0, r1) and c not in (c0, c1):
                continue
            m = 0
            if r > r0 and c in (c0, c1): m |= 1
            if r < r1 and c in (c0, c1): m |= 4
            if c < c1 and r in (r0, r1): m |= 2
            if c > c0 and r in (r0, r1): m |= 8
            pic[r * 8:r * 8 + 8, c * 8:c * 8 + 8] = 0
            put_tile(pic, 'WALL%d' % m, c * 8, r * 8)

def make_intro():
    rgb, fire = paint.loading()
    items = [("STRONKIE'S", (W - 10 * 16) // 2, 206, 2), ("CLOVER SNAKE", (W - 12 * 24) // 2, 226, 3), ('PRESENTS', (W - 8 * 8) // 2, 50, 1)]
    rgb = halo(rgb, items, 0.55)
    p, pal = finish(rgb, fire, seed=3)
    paste_logo(p, (W - 158) // 2, 4, 1)
    big_text(p, 'PRESENTS', (W - 8 * 8) // 2, 50, 1, CH['W'], CH['g'], 0, 3)
    big_text(p, "STRONKIE'S", (W - 10 * 16) // 2, 206, 2, CH['L'], CH['Y'], 0, 5)
    big_text(p, "CLOVER", (W - 12 * 24) // 2, 226, 3, CH['G'], CH['h'], 0, 3)
    big_text(p, "SNAKE", (W - 12 * 24) // 2 + 7 * 24, 226, 3, CH['C'], CH['b'], 0, 3)
    return p, pal

def make_title():
    rgb, fire = meadow_rgb()
    rgb = rgb.copy()
    items = [("STRONKIE'S", (W - 10 * 16) // 2, 50, 2), ("CLOVER", (W - 6 * 32) // 2, 68, 4), ("SNAKE", (W - 5 * 32) // 2, 102, 4)]
    rgb = halo(rgb, items, 0.6)
    # the menu: the meadow made dark inside a fence of the game's walls
    rgb[160:, :] *= 0.27
    p, pal = finish(rgb, [f for f in fire if f[1] < 150], seed=5)
    paste_logo(p, (W - 158) // 2, 2, 1)
    big_text(p, "STRONKIE'S", (W - 10 * 16) // 2, 50, 2, CH['L'], CH['Y'], 0, 5)
    big_text(p, "CLOVER", (W - 6 * 32) // 2, 68, 4, CH['G'], CH['h'], 0, 3)
    big_text(p, "SNAKE", (W - 5 * 32) // 2, 102, 4, CH['C'], CH['b'], 0, 3)
    # the game itself: a snake on its way to the clovers, a ball and a heart
    y, xs = 138, 44
    put_tile(p, 'SNAKE2', xs, y, 2)
    for i in range(1, 6):
        put_tile(p, 'SNAKE10', xs + i * 16, y, 2)
    put_tile(p, 'HEAD1', xs + 6 * 16, y, 2)
    for i, t in ((8, 'CLOVER'), (10, 'BALL'), (12, 'CLOVER'), (14, 'HEART')):
        put_tile(p, t, xs + i * 16, y, 2)
    fence(p, 0, 20, 39, 31)
    return p, pal

def make_howto():
    rgb, fire = meadow_rgb()
    rgb = rgb * 0.22
    p, pal = finish(rgb, [], seed=7, dither=6.0)
    fence(p, 0, 0, 39, 31)
    return p, pal

def planar(pic, nplanes=4):
    out = bytearray()
    for pl in range(nplanes):
        bits = ((pic >> pl) & 1).astype(np.uint8)
        out += np.packbits(bits, axis=1).tobytes()
    return bytes(out)

def save_preview(pic, name, pal=None):
    pal = pal or PAL
    P = np.array([[c * 17 for c in pal[i]] if i < len(pal) else [0, 0, 0] for i in range(32)], np.uint8)
    Image.fromarray(P[pic]).resize((W * 2, H * 2), Image.NEAREST).save(os.path.join(PREV, name))

# ------------------------------------------------------------------ rounds
FW, FH = 34, 27           # the field inside the border
EMPTY, WALL, CLOVER, BALL, MUSH, SNAKE, BLOCK = 0, 1, 2, 3, 4, 5, 6
SX, SY = 17, 21           # start: the head; the body goes down; facing up
MAXSPORES = 15

def in_zone(x, y):
    return abs(x - SX) <= 3 and abs(y - SY) <= 5

class Level:
    def __init__(self, name, seed):
        self.name = name
        self.m = [[EMPTY] * FW for _ in range(FH)]
        self.r = random.Random(seed)
        self.spore = []
    def wall(self, x0, y0, x1, y1, what=WALL):
        for y in range(min(y0, y1), max(y0, y1) + 1):
            for x in range(min(x0, x1), max(x0, x1) + 1):
                assert not in_zone(x, y), (self.name, x, y)
                self.m[y][x] = what
    def at(self, x, y):
        if not (0 <= x < FW and 0 <= y < FH):
            return WALL
        return self.m[y][x]
    def free(self, x, y, margin=0):
        if not (0 <= x < FW and 0 <= y < FH) or in_zone(x, y) or (x, y) in self.spore:
            return False
        for dy in range(-margin, margin + 1):
            for dx in range(-margin, margin + 1):
                xx, yy = x + dx, y + dy
                if 0 <= xx < FW and 0 <= yy < FH and self.m[yy][xx] != EMPTY:
                    return False
        return True
    def put(self, x, y, what):
        assert self.free(x, y), (self.name, x, y)
        self.m[y][x] = what
    def scatter(self, what, n, margin=1):
        k = tries = 0
        while k < n:
            tries += 1
            assert tries < 20000, self.name
            x, y = self.r.randrange(FW), self.r.randrange(FH)
            if self.free(x, y, margin):
                self.m[y][x] = what
                if what in (MUSH, BLOCK) and not self.connected():
                    self.m[y][x] = EMPTY
                    continue
                k += 1
    def clumps(self, n, margin=1):
        k = tries = 0
        while k < n:
            tries += 1
            assert tries < 20000, self.name
            x, y = self.r.randrange(FW - 1), self.r.randrange(FH - 1)
            if all(self.free(x + dx, y + dy, margin) for dx in (0, 1) for dy in (0, 1)):
                for dx in (0, 1):
                    for dy in (0, 1):
                        self.m[y + dy][x + dx] = CLOVER
                k += 1
    def spores(self, n, chokes):
        """n places where a mushroom grows each time something is eaten (in this
        order). About `chokes` of them in narrow places (a gap or a corridor), so
        the player has to think about the order - or cover them with the tail."""
        cand = []
        for y in range(FH):
            for x in range(FW):
                if not self.free(x, y):
                    continue
                solid = lambda v: v in (WALL, MUSH)
                if (solid(self.at(x - 1, y)) and solid(self.at(x + 1, y))) or \
                   (solid(self.at(x, y - 1)) and solid(self.at(x, y + 1))):
                    cand.append((x, y))
        self.r.shuffle(cand)
        picked = []
        for c in cand:
            if len(picked) >= chokes:
                break
            if all(abs(c[0] - p[0]) + abs(c[1] - p[1]) > 2 for p in picked):
                picked.append(c)
        tries = 0
        while len(picked) < n:
            tries += 1
            assert tries < 20000, self.name
            x, y = self.r.randrange(FW), self.r.randrange(FH)
            if self.free(x, y, 1) and all(abs(x - p[0]) + abs(y - p[1]) > 3 for p in picked):
                picked.append((x, y))
        self.r.shuffle(picked)
        assert len(picked) <= MAXSPORES
        self.spore = picked
    def connected(self, blocks_pass=True):
        seen = set([(SX, SY)])
        q = deque([(SX, SY)])
        stop = (WALL, MUSH) if blocks_pass else (WALL, MUSH, BLOCK)
        while q:
            x, y = q.popleft()
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                xx, yy = x + dx, y + dy
                if 0 <= xx < FW and 0 <= yy < FH and (xx, yy) not in seen and self.m[yy][xx] not in stop:
                    seen.add((xx, yy))
                    q.append((xx, yy))
        for y in range(FH):
            for x in range(FW):
                if self.m[y][x] not in stop and (x, y) not in seen:
                    return False
        return True
    def check(self):
        assert self.connected(), self.name + ' not connected'
        for y in range(FH):
            for x in range(FW):
                if in_zone(x, y):
                    assert self.m[y][x] == EMPTY, (self.name, x, y)
                if self.m[y][x] == BLOCK:      # every crate can be pushed one way or another
                    ok = False
                    for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                        if self.at(x - dx, y - dy) not in (WALL, MUSH, BLOCK) and self.at(x + dx, y + dy) == EMPTY:
                            ok = True
                    assert ok, (self.name, 'stuck crate', x, y)
        for (x, y) in self.spore:
            assert self.m[y][x] == EMPTY
        n = sum(r.count(CLOVER) for r in self.m)
        assert n > 0
        return n

levels = []

L = Level('FIRST STEPS', 1)
L.scatter(CLOVER, 16, 1); L.scatter(MUSH, 5, 1); L.scatter(BLOCK, 3, 1)
L.spores(4, 0)
levels.append(L)

L = Level('THREE WALLS', 2)
L.wall(6, 9, 6, 26); L.wall(12, 0, 12, 17); L.wall(22, 0, 22, 17); L.wall(28, 9, 28, 26)
L.put(6, 4, BLOCK); L.put(28, 4, BLOCK)
L.clumps(7, 1)
L.spores(6, 3)
levels.append(L)

L = Level('THE CRATE DOOR', 3)
L.wall(8, 4, 25, 4); L.wall(8, 4, 8, 13); L.wall(25, 4, 25, 13); L.wall(8, 13, 14, 13); L.wall(19, 13, 25, 13)
for x in range(15, 19):
    L.put(x, 13, BLOCK)
for x in (11, 14, 17, 20, 23):
    L.put(x, 7, CLOVER); L.put(x, 10, CLOVER)
L.scatter(CLOVER, 8, 1); L.scatter(MUSH, 6, 1)
L.spores(6, 2)
levels.append(L)

L = Level('SHELVES', 4)
L.wall(0, 4, 23, 4); L.wall(10, 9, 33, 9); L.wall(0, 14, 11, 14); L.wall(23, 14, 33, 14)
for x in range(2, 22, 3):
    L.put(x, 2, CLOVER)
for x in range(13, 33, 3):
    L.put(x, 7, CLOVER)
for x in range(3, 30, 4):
    L.put(x, 11, CLOVER)
L.put(27, 4, BLOCK); L.put(5, 9, BLOCK); L.put(16, 14, BLOCK)
L.scatter(MUSH, 6, 1)
L.spores(7, 4)
levels.append(L)

L = Level('FOUR ROOMS', 5)
L.wall(16, 0, 16, 13); L.wall(0, 13, 33, 13)
L.m[7][16] = BLOCK; L.m[13][8] = BLOCK; L.m[13][25] = BLOCK
L.clumps(6, 1); L.scatter(MUSH, 6, 1)
L.spores(7, 3)
levels.append(L)

L = Level('PILLARS', 6)
for y in (2, 8, 14, 20):
    for x in (2, 8, 14, 20, 26, 31):
        if not any(in_zone(x + dx, y + dy) for dx in (-1, 0, 1, 2) for dy in (-1, 0, 1, 2)):
            L.wall(x, y, x + 1, y + 1)
L.scatter(BLOCK, 6, 1); L.scatter(CLOVER, 22, 1); L.scatter(MUSH, 5, 1)
L.spores(8, 5)
levels.append(L)

L = Level('MUSHROOM FOREST', 7)
L.scatter(MUSH, 26, 1); L.scatter(CLOVER, 20, 1); L.scatter(BLOCK, 5, 1)
L.spores(8, 4)
levels.append(L)

L = Level('THE SPIRAL', 8)
L.wall(3, 1, 30, 1); L.wall(30, 1, 30, 14); L.wall(7, 14, 30, 14); L.wall(3, 1, 3, 11)
L.wall(7, 5, 7, 14); L.wall(7, 5, 26, 5); L.wall(26, 5, 26, 10); L.wall(11, 10, 26, 10)
for x in range(9, 25, 3):
    L.put(x, 3, CLOVER); L.put(x + 1, 12, CLOVER)
for x in range(12, 24, 3):
    L.put(x, 8, CLOVER)
L.m[12][7] = EMPTY; L.m[13][7] = EMPTY       # the way in at the bottom left ...
L.put(5, 12, BLOCK)                          # ... with a crate in front of it
L.scatter(CLOVER, 8, 1); L.scatter(MUSH, 5, 1)
L.spores(8, 5)
levels.append(L)

L = Level('THE COMB', 9)
for x in range(2, 34, 4):
    if not any(in_zone(x, y) for y in range(0, 13)):
        L.wall(x, 0, x, 12)
for x in range(4, 33, 4):
    if not in_zone(x, 6):
        L.put(x, 4, CLOVER); L.put(x, 9, CLOVER)
for x in (4, 12, 24):
    L.put(x, 12, BLOCK)
L.scatter(CLOVER, 6, 1); L.scatter(MUSH, 6, 1)
L.spores(10, 6)
levels.append(L)

L = Level('DIAMOND', 10)
cx, cy = 17, 8
for i in range(8):
    for (x, y) in ((cx - 8 + i, cy - i), (cx + 8 - i, cy - i), (cx - 8 + i, cy + i), (cx + 8 - i, cy + i)):
        if i not in (0, 4) and 0 <= y < FH and not in_zone(x, y):
            L.m[y][x] = WALL
for (x, y) in ((17, 5), (15, 7), (19, 7), (13, 9), (21, 9), (17, 9), (15, 11), (19, 11), (17, 3), (17, 13)):
    if L.free(x, y):
        L.put(x, y, CLOVER)
L.put(13, 12, BLOCK); L.put(21, 12, BLOCK)
L.scatter(CLOVER, 12, 1); L.scatter(MUSH, 8, 1)
L.spores(10, 5)
levels.append(L)

L = Level('CORRIDORS', 11)
L.wall(0, 3, 29, 3); L.wall(4, 7, 33, 7); L.wall(0, 11, 29, 11); L.wall(4, 15, 11, 15); L.wall(23, 15, 33, 15)
for x in range(2, 30, 3):
    L.put(x, 1, CLOVER); L.put(x + 2, 5, CLOVER); L.put(x, 9, CLOVER); L.put(x + 2, 13, CLOVER)
L.put(31, 9, BLOCK); L.put(2, 5, BLOCK)
L.scatter(MUSH, 4, 1)
L.spores(11, 7)
levels.append(L)

L = Level('THE GRAND FINALE', 12)
L.wall(4, 3, 13, 3); L.wall(20, 3, 29, 3); L.wall(4, 3, 4, 8); L.wall(29, 3, 29, 8)
L.wall(9, 9, 24, 9)
L.put(16, 3, BLOCK); L.put(17, 3, BLOCK)
for (x, y) in ((1, 15), (31, 15), (1, 22), (31, 22)):
    L.wall(x, y, x + 1, y + 1)
L.clumps(5, 1); L.scatter(CLOVER, 8, 1); L.scatter(MUSH, 14, 1); L.scatter(BLOCK, 4, 1)
L.spores(12, 7)
levels.append(L)

def level_preview():
    cols = 4
    sc = 4
    im = Image.new('RGB', (cols * (FW + 2) * sc, 3 * (FH + 2) * sc), (30, 30, 30))
    px = im.load()
    colr = {EMPTY: (0, 0, 0), WALL: (230, 230, 40), CLOVER: (50, 210, 50), MUSH: (230, 50, 30), BLOCK: (200, 130, 40)}
    for i, L in enumerate(levels):
        ox, oy = (i % cols) * (FW + 2) * sc, (i // cols) * (FH + 2) * sc
        for y in range(FH):
            for x in range(FW):
                c = colr[L.m[y][x]]
                if in_zone(x, y):
                    c = (20, 20, 60)
                if (x, y) in L.spore:
                    c = (140, 0, 140)
                if (x, y) == (SX, SY):
                    c = (60, 200, 255)
                for yy in range(sc):
                    for xx in range(sc):
                        px[ox + x * sc + xx, oy + y * sc + yy] = c
    im.save(os.path.join(PREV, 'levels_preview.png'))

# ------------------------------------------------------------------ sound
CLOCK = 3546895
NOTES = {'C': 0, 'C#': 1, 'D': 2, 'D#': 3, 'E': 4, 'F': 5, 'F#': 6, 'G': 7, 'G#': 8, 'A': 9, 'A#': 10, 'B': 11}
def freq(n):
    name, octv = n[:-1], int(n[-1])
    semis = NOTES[name] + 12 * (octv + 1) - 69
    return 440.0 * 2 ** (semis / 12)
def period(n, wavelen):
    p = int(round(CLOCK / (freq(n) * wavelen)))
    assert 124 <= p <= 65535, (n, p)
    return p

WAVES = {}
def sq(n, duty=0.5, amp=100):
    return bytes(((amp if i < n * duty else -amp) & 255) for i in range(n))
WAVES['SQ16'] = sq(16)
WAVES['PU16'] = sq(16, 0.25)
WAVES['TRI32'] = bytes((int(round(((i if i < 16 else 32 - i) / 16 * 2 - 1) * 110)) & 255) for i in range(32))
WAVES['SQ32'] = sq(32, 0.5, 90)
rng = random.Random(77)
WAVES['NOISE'] = bytes(rng.randrange(256) for _ in range(1024))
def harmonics(n, amps, amp=110):
    v = [sum(a * np.sin(2 * np.pi * (k + 1) * i / n) for k, a in enumerate(amps)) for i in range(n)]
    m = max(abs(x) for x in v)
    return bytes(int(round(x / m * amp)) & 255 for x in v)
WAVES['SINE8'] = harmonics(8, [1])
WAVES['SINE16'] = harmonics(16, [1])
WAVES['SINE32'] = harmonics(32, [1])
WAVES['FLUTE16'] = harmonics(16, [1, 0.22, 0.06])          # soft, round
WAVES['OBOE16'] = harmonics(16, [0.7, 1, 0.55, 0.3, 0.12])  # reedy
WAVES['HARP32'] = harmonics(32, [1, 0.45, 0.22, 0.1, 0.05]) # plucked strings
WAVE_ORDER = ['SQ16', 'PU16', 'TRI32', 'SQ32', 'NOISE', 'SINE8', 'SINE16', 'SINE32', 'FLUTE16', 'OBOE16', 'HARP32']
WLEN = {k: len(v) for k, v in WAVES.items()}

SFX = {}
def sfx(name, wave, frames):
    SFX[name] = (WAVE_ORDER.index(wave), frames)

# effect frames: (period, volume)
sfx('CLOVER', 'SQ16', [(period(n, 16), v) for n, v in (('C5', 50), ('E5', 48), ('G5', 44), ('C6', 40), ('C6', 30), ('C6', 18))])
sfx('BALL', 'PU16', [(period('G5', 16), 46)] * 3 + [(0x7fff, 0)] + [(period('D6', 16), 46)] * 3 + [(period('D6', 16), 24)] * 2)
sfx('HEART', 'SQ16', [(period(n, 16), 44) for n in ('C5', 'C5', 'E5', 'E5', 'G5', 'G5', 'C6', 'C6', 'E6', 'E6', 'G6', 'G6')] + [(period('C6', 16), v) for v in (30, 20, 10)])
sfx('DIE', 'NOISE', [(160 + i * 12, max(0, 60 - i)) for i in range(60)])
sfx('SPROUT', 'TRI32', [(period('C3', 32) + i * 30, 50 - i * 4) for i in range(12)])
sfx('PUSH', 'TRI32', [(period('E2', 32) + i * 40, 60 - i * 6) for i in range(8)])
sfx('BUMP', 'NOISE', [(400, 40), (500, 25), (600, 10)])
sfx('FIZZLE', 'NOISE', [(180 + i * 25, 30 - i * 2) for i in range(14)])
sfx('TICK', 'PU16', [(period('A5', 16), 30), (period('A5', 16), 12)])
sfx('LIFE', 'SQ16', [(period(n, 16), 46) for n in ('G5', 'G5', 'G5', 'C6', 'C6', 'C6', 'E6', 'E6', 'E6', 'G6', 'G6', 'G6', 'G6', 'G6')] + [(period('G6', 16), v) for v in (30, 20, 10)])
def jingle(notes, wave='SQ16', vol=46, step=6):
    fr = []
    for n in notes:
        if n == '-':
            fr += [(0x7fff, 0)] * step
        else:
            p = period(n, WLEN[wave])
            fr += [(p, vol)] * (step - 1) + [(p, vol // 3)]
    return fr
sfx('READY', 'SQ16', jingle(['C5', 'E5', 'G5', '-', 'E5', 'G5', 'C6', 'C6']))
sfx('CLEAR', 'SQ16', jingle(['G5', 'C6', 'E6', 'G6', '-', 'E6', 'G6', 'G6', 'C6', 'E6', 'G6', 'C6'], step=5))
sfx('GAMEOVER', 'TRI32', jingle(['G4', 'F#4', 'F4', 'E4', '-', 'C4', 'C4', 'C4'], 'TRI32', 56, 10))
sfx('START', 'SQ16', jingle(['C5', 'G5', 'C6'], step=4))

# the forest (played now and then on channel 3, quietly)
def pf(f, wave):
    return max(124, int(round(CLOCK / (f * WLEN[wave]))))
def chirp(f0, f1, n, vol, wave='SINE8'):
    return [(pf(f0 + (f1 - f0) * i / max(n - 1, 1), wave), int(vol * (1 - 0.35 * i / n))) for i in range(n)]
GAP = lambda n: [(0x7fff, 0)] * n
sfx('BIRD1', 'SINE8', chirp(3400, 2500, 4, 20) + GAP(4) + chirp(3400, 2500, 4, 22) + GAP(4) + chirp(3500, 2300, 6, 20))
sfx('BIRD2', 'SINE8', [(pf(2700 if i % 2 else 3200, 'SINE8'), 16 - i // 3) for i in range(18)] + GAP(6) + chirp(3000, 3400, 5, 14))
sfx('BIRD3', 'SINE8', [(pf(3000, 'SINE8'), 18)] * 6 + chirp(3000, 2000, 9, 18) + GAP(10) + [(pf(3000, 'SINE8'), 14)] * 5 + chirp(3000, 2100, 8, 14))
sfx('BIRD4', 'SINE8', chirp(2200, 3450, 10, 16) + GAP(3) + chirp(2600, 3450, 6, 14) + GAP(3) + chirp(2600, 3450, 6, 12))
sfx('CUCKOO', 'SINE16', ([(pf(740, 'SINE16'), v) for v in (14, 26, 26, 24, 22, 18, 10)] + GAP(3) +
                         [(pf(622, 'SINE16'), v) for v in (14, 26, 26, 25, 24, 22, 20, 17, 13, 8)] + GAP(14)) * 2)
sfx('WOODPECKER', 'NOISE', sum(([(380, 34 - k * 2), (0x7fff, 0), (0x7fff, 0)] for k in range(12)), []))
sfx('WIND', 'NOISE', [(int(820 - 120 * np.sin(i / 25)), int(11 * np.sin(np.pi * i / 150) ** 2)) for i in range(150)])
sfx('OWL', 'SINE32', [(pf(370, 'SINE32'), int(22 * min(1, i / 4, (16 - i) / 5))) for i in range(16)] + GAP(14) +
                     [(pf(340, 'SINE32'), int(20 * min(1, i / 3, (9 - i) / 3))) for i in range(9)] + GAP(3) +
                     [(pf(340, 'SINE32'), int(20 * min(1, i / 3, (16 - i) / 5))) for i in range(16)])

# music: two channels (0 = melody, 1 = accompaniment), lengths in eighths.
# tokens: NOTE[:len], -[:len] rest, w:WAVE (instrument), e:vol,decay,lowest,vibrato
def transpose(seq, k):
    out = []
    names = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
    for tok in seq.split():
        n, sep, l = tok.partition(':')
        if n in ('-', 'w', 'e') or n[0] not in 'ABCDEFG':
            out.append(tok)
            continue
        v = NOTES[n[:-1]] + 12 * int(n[-1]) + k
        out.append(names[v % 12] + str(v // 12) + (sep + l if sep else ''))
    return ' '.join(out)

def tune(melody, bass, step):
    def ch(seq):
        out, wave = [], 'FLUTE16'
        for tok in seq.split():
            n, _, l = tok.partition(':')
            if n == 'w':
                wave = l
                out.append(('W', WAVE_ORDER.index(l)))
                continue
            if n == 'e':
                out.append(('E', [int(v) for v in l.split(',')]))
                continue
            ln = int(l or 1) * step
            out.append((0 if n == '-' else period(n, WLEN[wave]), ln))
        return out
    return ch(melody), ch(bass)

# the title: Grieg, Morning Mood (Peer Gynt), 6/8 in E major;
# first the flute, then the oboe answers an octave up; harp underneath
MM_A = ("G4:2 E4 D4:2 C4 D4:2 E4 G4:2 E4 D4:2 C4 D4:2 E4 D4:6 "
        "E4:2 G4 E4:2 G4 A4:2 E4 A4:2 B4 G4:2 E4 D4:9 "
        "G4:2 E4 D4:2 C4 D4:2 E4 G4:2 E4 D4:2 C4 D4:2 E4 D4:6 "
        "E4:2 G4 E4:2 G4 A4:2 E4 A4:2 G4 E4:2 D4 C4:9")
def arp(ch):
    r, f, t = ch
    return '%s %s %s %s %s %s' % (r, f, transpose(r, 12), t, transpose(r, 12), f)
CHORDS = {'C': ('C3', 'G3', 'E4'), 'G': ('G2', 'D3', 'B3'), 'Am': ('A2', 'E3', 'C4'), 'F': ('F2', 'C3', 'A3'), 'Em': ('E2', 'B2', 'G3')}
MM_H = 'C C C G C Am G G C C C G C Am G C'.split()
MM_BASS = ' '.join(arp(CHORDS[c]) for c in MM_H)
TITLE_MEL = ('e:30,4,14,1 w:FLUTE16 ' + transpose(MM_A, 4) + ' -:6 '
             'e:26,4,12,1 w:OBOE16 ' + transpose(MM_A, 16) + ' -:6')
TITLE_BAS = 'e:24,1,0,0 w:HARP32 ' + transpose(MM_BASS, 4) + ' -:6 ' + transpose(MM_BASS, 4) + ' -:6'

# the game: Bach (Petzold), Minuet in G, AABB, soft
MIN_A = ("D5:2 G4 A4 B4 C5 D5:2 G4:2 G4:2 E5:2 C5 D5 E5 F#5 G5:2 G4:2 G4:2 "
         "C5:2 D5 C5 B4 A4 B4:2 C5 B4 A4 G4 F#4:2 G4 A4 B4 G4 A4:6 "
         "D5:2 G4 A4 B4 C5 D5:2 G4:2 G4:2 E5:2 C5 D5 E5 F#5 G5:2 G4:2 G4:2 "
         "C5:2 D5 C5 B4 A4 B4:2 C5 B4 A4 G4 A4:2 B4 A4 G4 F#4 G4:6 ")
MIN_B = ("B5:2 G5 A5 B5 G5 A5:2 D5 E5 F#5 D5 G5:2 E5 F#5 G5 D5 C#5:2 B4 C#5 A4:2 "
         "A4 B4 C#5 D5 E5 F#5 G5:2 F#5:2 E5:2 F#5:2 A4:2 C#5:2 D5:6 "
         "D5:2 G4 F#4 G4:2 E5:2 G4 F#4 G4:2 D5:2 C5:2 B4:2 A4 G4 F#4 G4 A4:2 "
         "D4 E4 F#4 G4 A4 B4 C5:2 B4:2 A4:2 B4 D5 G4:2 F#4:2 G4:6 ")
def bar3(root, fifth):
    return '%s:4 %s:2' % (root, fifth)
B3 = {'G': ('G2', 'D3'), 'C': ('C3', 'G3'), 'D': ('D3', 'A2'), 'Am': ('A2', 'E3'), 'A': ('A2', 'E3'), 'Em': ('E2', 'B2'), 'B': ('B2', 'F#3')}
MIN_HA = 'G G C G Am G D D G G C G Am G D G'.split()
MIN_HB = 'G D Em A A A D D G C G D D Am D G'.split()
MIN_BA = ' '.join(bar3(*B3[c]) for c in MIN_HA)
MIN_BB = ' '.join(bar3(*B3[c]) for c in MIN_HB)
GAME_MEL = 'e:22,5,10,1 w:FLUTE16 ' + MIN_A + MIN_A + MIN_B + MIN_B + '-:6'
GAME_BAS = 'e:20,2,0,0 w:HARP32 ' + MIN_BA + ' ' + MIN_BA + ' ' + MIN_BB + ' ' + MIN_BB + ' -:6'
TUNES = {'TITLE': tune(TITLE_MEL, TITLE_BAS, 13), 'GAME': tune(GAME_MEL, GAME_BAS, 11)}

# ------------------------------------------------------------------ output
def dcb(data, per=32):
    out = []
    for i in range(0, len(data), per):
        out.append('\tdc.b\t' + ','.join('$%02x' % b for b in data[i:i + per]))
    return '\n'.join(out)

def dcw(vals, per=16):
    out = []
    for i in range(0, len(vals), per):
        out.append('\tdc.w\t' + ','.join('$%04x' % (v & 0xffff) for v in vals[i:i + per]))
    return '\n'.join(out)

def main():
    os.makedirs(PREV, exist_ok=True)
    s = ['; gfx_gen.s - made by tools/gen.py, do not edit', '']
    for k, v in names.items():
        s.append('T_%s\tequ\t%d' % (k, v))
    s.append('NTILES\tequ\t%d' % NTILES)
    s.append('NLEVELS\tequ\t%d' % len(levels))
    for i, k in enumerate(SFX):
        s.append('SFX_%s\tequ\t%d' % (k, i))
    s.append('')
    s.append('\tsection\tgfxdata,data')
    s.append('Palette:')
    s.append(dcw([(r << 8) | (g << 4) | b for r, g, b in PAL]))
    s.append('Tiles:')
    tb = bytearray()
    for t in tiles:
        for y in range(8):
            for pl in range(4):
                v = 0
                for x in range(8):
                    if (t[y, x] >> pl) & 1:
                        v |= 0x80 >> x
                tb.append(v)
    s.append(dcb(tb))
    pics = {'IntroPic': make_intro(), 'TitlePic': make_title(), 'HowToPic': make_howto()}
    for k, (pic, pal) in pics.items():
        save_preview(pic, k.lower().replace('pic', '') + '_preview.png', pal)
        s.append('\tcnop\t0,4')
        s.append('%s:\tdc.w\t5' % k)
        s.append(dcw([(r << 8) | (g << 4) | b for r, g, b in pal]))
        s.append(dcb(planar(pic, 5)))
    tiles_preview(); level_preview()
    s.append('; rounds: name (32 bytes), %d x %d cells, spores: count + (x,y) pairs (32 bytes)' % (FW, FH))
    s.append('Levels:')
    for i, L in enumerate(levels):
        n = L.check()
        print('round %2d %-18s clovers %3d mushrooms %3d crates %d spores %d' % (i + 1, L.name, n, sum(r.count(MUSH) for r in L.m), sum(r.count(BLOCK) for r in L.m), len(L.spore)))
        nm = L.name.encode('ascii')[:31].ljust(32, b'\0')
        s.append(dcb(nm))
        s.append(dcb(bytes(v for r in L.m for v in r), FW))
        sp = bytes([len(L.spore)]) + bytes(v for p in L.spore for v in p)
        s.append(dcb(sp.ljust(32, b'\0')))
    s.append('\tcnop\t0,4')
    s.append('SfxTab:')
    for k in SFX:
        s.append('\tdc.l\tSfx_%s' % k)
    for k, (w, fr) in SFX.items():
        s.append('Sfx_%s:' % k)
        vals = [w]
        for p, v in fr:
            vals += [p, v]
        vals.append(0)
        s.append(dcw(vals))
    for k, (mel, bas) in TUNES.items():
        for ch, seq in (('Mel', mel), ('Bas', bas)):
            s.append('Tune%s%s:' % (k.capitalize(), ch))
            vals = []
            for p, ln in seq:
                if p == 'W':
                    vals += [0xfffe, ln]
                elif p == 'E':
                    vals += [0xfffd] + ln
                else:
                    vals += [p, ln]
            vals += [0xffff, 0]
            s.append(dcw(vals))
        fr = lambda q: sum(l for p, l in q if p not in ('W', 'E'))
        s.append('; %s tune: %d / %d frames' % (k, fr(mel), fr(bas)))
        print('tune', k, fr(mel), fr(bas))
    s.append('')
    s.append('\tsection\tsounddata,data_c')
    s.append('Waves:')
    for k in WAVE_ORDER:
        s.append('Wave_%s:' % k)
        s.append(dcb(WAVES[k]))
    s.append('\tsection\tgfxcode,code')
    s.append('WaveTab:')
    for k in WAVE_ORDER:
        s.append('\tdc.l\tWave_%s' % k)
        s.append('\tdc.w\t%d' % (WLEN[k] // 2))
    open(OUT, 'w').write('\n'.join(s) + '\n')
    print('tiles', NTILES, '->', OUT)

if __name__ == '__main__':
    main()
