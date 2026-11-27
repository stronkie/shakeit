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

def make_intro():
    p = new_pic()
    paste_logo(p, (W - 158 * 2) // 2, 72, 2)
    return p

def make_title():
    p = new_pic()
    paste_logo(p, (W - 158) // 2, 4, 1)
    big_text(p, "STRONKIE'S", (W - 10 * 16) // 2, 54, 2, CH['L'], CH['Y'], 0, 5)
    big_text(p, "CLOVER", (W - 6 * 32) // 2, 76, 4, CH['G'], CH['h'], 0, 3)
    big_text(p, "SNAKE", (W - 5 * 32) // 2, 112, 4, CH['C'], CH['b'], 0, 3)
    # a little snake chasing clovers along the bottom of the picture (2x tiles)
    y = 146
    xs = 40
    put_tile(p, 'SNAKE2', xs, y, 2)
    for i in range(1, 6):
        put_tile(p, 'SNAKE10', xs + i * 16, y, 2)
    put_tile(p, 'HEAD1', xs + 6 * 16, y, 2)
    put_tile(p, 'CLOVER', xs + 8 * 16, y, 2)
    put_tile(p, 'BALL', xs + 10 * 16, y, 2)
    put_tile(p, 'CLOVER', xs + 12 * 16, y, 2)
    put_tile(p, 'HEART', xs + 14 * 16, y, 2)
    return p

def planar(pic, nplanes=4):
    out = bytearray()
    for pl in range(nplanes):
        bits = ((pic >> pl) & 1).astype(np.uint8)
        out += np.packbits(bits, axis=1).tobytes()
    return bytes(out)

def save_preview(pic, name):
    im = Image.new('RGB', (W, H))
    px = im.load()
    for y in range(H):
        for x in range(W):
            px[x, y] = rgb(pic[y, x])
    im.resize((W * 2, H * 2), Image.NEAREST).save(os.path.join(PREV, name))

# ------------------------------------------------------------------ rounds
FW, FH = 34, 27           # the field inside the border
EMPTY, WALL, CLOVER, BALL, MUSH = 0, 1, 2, 3, 4
SX, SY = 17, 21           # start: the head; the body goes down; moving up

def in_zone(x, y):
    return abs(x - SX) <= 3 and abs(y - SY) <= 5

class Level:
    def __init__(self, name, seed):
        self.name = name
        self.m = [[EMPTY] * FW for _ in range(FH)]
        self.r = random.Random(seed)
    def wall(self, x0, y0, x1, y1):
        for y in range(min(y0, y1), max(y0, y1) + 1):
            for x in range(min(x0, x1), max(x0, x1) + 1):
                assert not in_zone(x, y), (self.name, x, y)
                self.m[y][x] = WALL
    def free(self, x, y, margin=0):
        if not (0 <= x < FW and 0 <= y < FH) or in_zone(x, y):
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
        k = 0
        tries = 0
        while k < n:
            tries += 1
            assert tries < 20000, self.name
            x, y = self.r.randrange(FW), self.r.randrange(FH)
            if self.free(x, y, margin):
                self.m[y][x] = what
                if what == MUSH and not self.connected():
                    self.m[y][x] = EMPTY
                    continue
                k += 1
    def clumps(self, n, margin=1):
        k = 0
        tries = 0
        while k < n:
            tries += 1
            assert tries < 20000, self.name
            x, y = self.r.randrange(FW - 1), self.r.randrange(FH - 1)
            if all(self.free(x + dx, y + dy, margin) for dx in (0, 1) for dy in (0, 1)):
                for dx in (0, 1):
                    for dy in (0, 1):
                        self.m[y + dy][x + dx] = CLOVER
                k += 1
    def connected(self):
        seen = set([(SX, SY)])
        q = deque([(SX, SY)])
        while q:
            x, y = q.popleft()
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                xx, yy = x + dx, y + dy
                if 0 <= xx < FW and 0 <= yy < FH and (xx, yy) not in seen and self.m[yy][xx] not in (WALL, MUSH):
                    seen.add((xx, yy))
                    q.append((xx, yy))
        for y in range(FH):
            for x in range(FW):
                if self.m[y][x] not in (WALL, MUSH) and (x, y) not in seen:
                    return False
        return True
    def check(self):
        assert self.connected(), self.name + ' not connected'
        for y in range(FH):
            for x in range(FW):
                if in_zone(x, y):
                    assert self.m[y][x] == EMPTY, (self.name, x, y)
        # no dead ends of width one between two walls that the snake can't turn in? (just connected)
        n = sum(r.count(CLOVER) for r in self.m)
        assert n > 0
        return n

levels = []

L = Level('OPEN MEADOW', 1)
L.scatter(CLOVER, 26, 1); L.scatter(MUSH, 10, 1)
levels.append(L)

L = Level('THREE WALLS', 2)
L.wall(6, 9, 6, 26); L.wall(12, 0, 12, 17); L.wall(22, 0, 22, 17); L.wall(28, 9, 28, 26)
L.clumps(9, 1)
levels.append(L)

L = Level('THE BOX', 3)
L.wall(8, 4, 25, 4); L.wall(8, 4, 8, 13); L.wall(25, 4, 25, 13); L.wall(8, 13, 14, 13); L.wall(19, 13, 25, 13)
for x in (11, 14, 17, 20, 23):
    L.put(x, 7, CLOVER); L.put(x, 10, CLOVER)
L.scatter(CLOVER, 14, 1); L.scatter(MUSH, 10, 1)
levels.append(L)

L = Level('SHELVES', 4)
L.wall(0, 4, 23, 4); L.wall(10, 9, 33, 9); L.wall(0, 14, 11, 14); L.wall(23, 14, 33, 14)
for x in range(2, 22, 3):
    L.put(x, 2, CLOVER)
for x in range(13, 33, 3):
    L.put(x, 7, CLOVER)
for x in range(3, 30, 4):
    L.put(x, 11, CLOVER)
L.scatter(MUSH, 8, 1)
levels.append(L)

L = Level('FOUR ROOMS', 5)
L.wall(16, 0, 16, 5); L.wall(16, 9, 16, 13); L.wall(0, 13, 9, 13); L.wall(24, 13, 33, 13); L.wall(9, 13, 9, 15); L.wall(24, 13, 24, 15)
L.clumps(8, 1); L.scatter(MUSH, 8, 1)
levels.append(L)

L = Level('PILLARS', 6)
for y in (2, 8, 14, 20):
    for x in (2, 8, 14, 20, 26, 31):
        if not any(in_zone(x + dx, y + dy) for dx in (-1, 0, 1, 2) for dy in (-1, 0, 1, 2)):
            L.wall(x, y, x + 1, y + 1)
L.scatter(CLOVER, 28, 1); L.scatter(MUSH, 6, 1)
levels.append(L)

L = Level('MUSHROOM FOREST', 7)
L.scatter(MUSH, 34, 1); L.scatter(CLOVER, 26, 1)
levels.append(L)

L = Level('THE SPIRAL', 8)
L.wall(3, 1, 30, 1); L.wall(30, 1, 30, 14); L.wall(7, 14, 30, 14); L.wall(3, 1, 3, 11)
L.wall(7, 5, 7, 14); L.wall(7, 5, 26, 5); L.wall(26, 5, 26, 10); L.wall(11, 10, 26, 10)
for x in range(9, 25, 3):
    L.put(x, 3, CLOVER); L.put(x + 1, 12, CLOVER)
for x in range(10, 24, 3):
    L.put(x, 8, CLOVER)
L.scatter(CLOVER, 10, 1); L.scatter(MUSH, 6, 1)
levels.append(L)

L = Level('THE COMB', 9)
for x in range(2, 34, 4):
    if not any(in_zone(x, y) for y in range(0, 13)):
        L.wall(x, 0, x, 12)
for x in range(4, 33, 4):
    if not in_zone(x, 6):
        L.put(x, 4, CLOVER); L.put(x, 9, CLOVER)
L.scatter(CLOVER, 8, 1); L.scatter(MUSH, 8, 1)
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
L.scatter(CLOVER, 16, 1); L.scatter(MUSH, 10, 1)
levels.append(L)

L = Level('CORRIDORS', 11)
L.wall(0, 3, 29, 3); L.wall(4, 7, 33, 7); L.wall(0, 11, 29, 11); L.wall(4, 15, 11, 15); L.wall(23, 15, 33, 15)
for x in range(2, 30, 3):
    L.put(x, 1, CLOVER); L.put(x + 2, 5, CLOVER); L.put(x, 9, CLOVER); L.put(x + 2, 13, CLOVER)
L.scatter(MUSH, 6, 1)
levels.append(L)

L = Level('THE GRAND FINALE', 12)
L.wall(4, 3, 13, 3); L.wall(20, 3, 29, 3); L.wall(4, 3, 4, 8); L.wall(29, 3, 29, 8)
L.wall(9, 9, 24, 9)
for (x, y) in ((1, 15), (31, 15), (1, 22), (31, 22)):
    L.wall(x, y, x + 1, y + 1)
L.clumps(6, 1); L.scatter(CLOVER, 10, 1); L.scatter(MUSH, 18, 1)
levels.append(L)

def level_preview():
    cols = 4
    sc = 4
    im = Image.new('RGB', (cols * (FW + 2) * sc, 3 * (FH + 2) * sc), (30, 30, 30))
    px = im.load()
    colr = {EMPTY: (0, 0, 0), WALL: (230, 230, 40), CLOVER: (50, 210, 50), MUSH: (230, 50, 30)}
    for i, L in enumerate(levels):
        ox, oy = (i % cols) * (FW + 2) * sc, (i // cols) * (FH + 2) * sc
        for y in range(FH):
            for x in range(FW):
                c = colr[L.m[y][x]]
                if in_zone(x, y):
                    c = (20, 20, 60) if c == (0, 0, 0) else (255, 0, 255)
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
WAVE_ORDER = ['SQ16', 'PU16', 'TRI32', 'SQ32', 'NOISE']
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

# music: two channels (0 = melody on PU16, 1 = bass on TRI32), notes in eighths
def tune(melody, bass, step):
    def ch(seq, wave):
        out = []
        for tok in seq.split():
            n, _, l = tok.partition(':')
            ln = int(l or 1) * step
            out.append((0 if n == '-' else period(n, WLEN[wave]), ln))
        return out
    return ch(melody, 'PU16'), ch(bass, 'TRI32')

TITLE_MEL = ("E5 G5 C6 G5 A5:2 G5 E5 "
             "F5 E5 D5 E5 C5:2 - G4 "
             "E5 G5 C6 G5 A5:2 C6 A5 "
             "G5 F5 E5 D5 C5:3 - "
             "A5 A5 G5 F5 E5:2 C5 E5 "
             "D5 D5 E5 F5 G5:3 - "
             "A5 B5 C6 A5 G5:2 E5 C5 "
             "D5 G4 B4 D5 C5:3 -")
TITLE_BAS = ("C3:2 G2:2 C3:2 G2:2 F2:2 C3:2 C3:2 G2:2 "
             "C3:2 G2:2 F2:2 A2:2 G2:2 G2:2 C3:2 G2:2 "
             "F2:2 C3:2 F2:2 C3:2 G2:2 D3:2 G2:2 B2:2 "
             "F2:2 C3:2 A2:2 C3:2 G2:2 G2:2 C3:2 C3:2")
GAME_MEL = ("A4 - C5 - E5 D5 C5 - "
            "G4 - B4 - D5 C5 B4 - "
            "F4 - A4 - C5 B4 A4 - "
            "E4 G#4 B4 E5 D5 C5 B4 - "
            "A4 - C5 - E5 G5 E5 - "
            "D5 - F5 - A5 G5 F5 - "
            "E5 - C5 - B4 A4 G#4 - "
            "A4:3 - E4:2 - -")
GAME_BAS = ("A2 - A2 E3 A2 - E3 - G2 - G2 D3 G2 - D3 - "
            "F2 - F2 C3 F2 - C3 - E2 - E2 B2 E2 - G#2 - "
            "A2 - A2 E3 A2 - E3 - D2 - D2 A2 D2 - A2 - "
            "E2 - E2 B2 E2 - E2 - A2 - A2 E3 A2 - - -")
TUNES = {'TITLE': tune(TITLE_MEL, TITLE_BAS, 12), 'GAME': tune(GAME_MEL, GAME_BAS, 10)}

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
    intro, title = make_intro(), make_title()
    save_preview(intro, 'intro_preview.png'); save_preview(title, 'title_preview.png')
    tiles_preview(); level_preview()
    s.append('\tcnop\t0,4')
    s.append('IntroPic:'); s.append(dcb(planar(intro)))
    s.append('\tcnop\t0,4')
    s.append('TitlePic:'); s.append(dcb(planar(title)))
    s.append('\tcnop\t0,4')
    s.append('; rounds: name (32 bytes), then %d x %d cells' % (FW, FH))
    s.append('Levels:')
    for i, L in enumerate(levels):
        n = L.check()
        print('round %2d %-18s clovers %3d mushrooms %3d' % (i + 1, L.name, n, sum(r.count(MUSH) for r in L.m)))
        nm = L.name.encode('ascii')[:31].ljust(32, b'\0')
        s.append(dcb(nm))
        s.append(dcb(bytes(v for r in L.m for v in r), FW))
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
                vals += [p, ln]
            vals += [0xffff, 0]
            s.append(dcw(vals))
        s.append('; %s tune: %d / %d frames' % (k, sum(l for _, l in mel), sum(l for _, l in bas)))
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
