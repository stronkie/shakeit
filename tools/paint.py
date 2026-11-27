#!/usr/bin/env python3
"""paint.py - paints the pictures of Stronkie's Clover Snake (used by gen.py).

Everything is painted at 4x the Amiga size (1280 x 1024) in full colour,
then made smaller (smooth edges) and reduced to the Amiga's colours:
colours 0-15 are the game's palette (font, tiles, logo), 16-28 are picked
for the picture, 29-31 are the fireflies (they twinkle in the game by
changing those three colours).

  loading()  -> the loading picture: a forest with the snake, mushrooms,
                clovers, a ball, a heart and fireflies
  meadow()   -> the background of the title screen: trees, sky and a
                meadow where the game's things lie about
"""
import numpy as np
from PIL import Image, ImageDraw
from scipy.ndimage import gaussian_filter
from scipy.spatial import cKDTree

W, H = 320, 256
S = 4
WS, HS = W * S, H * S
FIRE = (29, 30, 31)


def clamp(a):
    return np.clip(a, 0, 255)


class Canvas:
    def __init__(self, top=(0, 0, 0)):
        self.a = np.zeros((HS, WS, 3), np.float32)
        self.a[:] = top

    def mask(self, fn):
        im = Image.new('L', (WS, HS), 0)
        fn(ImageDraw.Draw(im))
        return np.asarray(im, np.float32) / 255.0

    def put(self, m, col, alpha=1.0):
        m = (m * alpha)[..., None]
        self.a = self.a * (1 - m) + np.asarray(col, np.float32) * m

    def add(self, m, col, amount=1.0):
        self.a = self.a + (m * amount)[..., None] * np.asarray(col, np.float32)

    def small(self):
        im = Image.fromarray(clamp(self.a).astype(np.uint8))
        return np.asarray(im.reduce(S), np.float32)


# base coordinates -> canvas coordinates
def B(*v):
    return [x * S for x in v]


def ell(cx, cy, rx, ry):
    return B(cx - rx, cy - ry, cx + rx, cy + ry)


def noise(sigma, seed, sy=None):
    r = np.random.RandomState(seed).rand(HS, WS).astype(np.float32)
    n = gaussian_filter(r, (sigma * S if sy is None else sy * S, sigma * S))
    n -= n.min()
    return n / max(n.max(), 1e-6)


def ygrad(cols):
    """vertical gradient: [(y, rgb), ...] in base units"""
    ys = np.arange(HS, dtype=np.float32) / S
    out = np.zeros((HS, 3), np.float32)
    pts = sorted(cols)
    for c in range(3):
        out[:, c] = np.interp(ys, [p[0] for p in pts], [p[1][c] for p in pts])
    return np.repeat(out[:, None, :], WS, 1)


def radial(cx, cy, r):
    yy, xx = np.mgrid[0:HS, 0:WS].astype(np.float32) / S
    d = np.sqrt((xx - cx) ** 2 + (yy - cy) ** 2) / r
    return np.clip(1 - d, 0, 1) ** 2


YY, XX = None, None
def grid():
    global YY, XX
    if YY is None:
        YY, XX = np.mgrid[0:HS, 0:WS].astype(np.float32) / S
    return YY, XX


# ------------------------------------------------------------------ pieces
def light_rays(cv, ox, oy, rays, strength=0.22, seed=3):
    rng = np.random.RandomState(seed)
    m = cv.mask(lambda d: [d.polygon(B(ox + a, oy, ox + a + w, oy, ox + a + w - 150, oy + 240, ox + a - 150 - w * 0.5, oy + 240), fill=int(140 + rng.rand() * 115)) for a, w in rays])
    m = gaussian_filter(m, 3 * S)
    yy, _ = grid()
    m *= np.clip(1.15 - (yy - oy) / 230, 0, 1)
    cv.add(m, (255, 240, 170), strength)


def tree_trunk(cv, x0, x1, y0, y1, col, light_from=1, bark=True, seed=1, roots=True, lean=0.0):
    """a trunk between x0..x1 from y0 to y1 (base units), shaded like a cylinder"""
    def poly(d):
        pts = [(x0 + lean * 0, y0), (x1 + lean, y0)]
        if roots:
            w = x1 - x0
            pts += [(x1 + lean * 0.2, y1 - w * 0.9), (x1 + w * 0.45, y1), (x0 + w * 0.55, y1 - w * 0.12),
                    (x0 - w * 0.45 + w * 0.1, y1), (x0, y1 - w * 0.9)]
        else:
            pts += [(x1, y1), (x0, y1)]
        d.polygon([v * S for p in pts for v in p], fill=255)
    m = cv.mask(poly)
    yy, xx = grid()
    t = np.clip((xx - x0) / max(x1 - x0, 1), 0, 1)
    if light_from < 0:
        t = 1 - t
    shade = 0.45 + 0.75 * np.sin(np.clip(t, 0, 1) * np.pi * 0.85 + 0.25) ** 1.5
    shade = shade * (0.85 + 0.25 * t)
    tex = 1.0
    if bark:
        n = noise(0.6, seed, sy=9)
        tex = 0.7 + 0.5 * n
        n2 = noise(1.2, seed + 7)
        moss = np.clip((n2 - 0.58) * 6, 0, 1) * np.clip(1 - t * 1.3, 0, 1)
    col = np.asarray(col, np.float32)
    rgb = (col * (shade * tex)[..., None])
    if bark:
        mossc = np.array([60, 120, 40], np.float32) * (0.6 + 0.6 * shade)[..., None]
        rgb = rgb * (1 - moss[..., None]) + mossc * moss[..., None]
    cv.put(m, rgb)


def leaf_cluster(cv, blobs, dark, mid, light, seed=1, edge=None):
    """blobs: [(cx, cy, r)], each painted as a dark ball with a lit top-left"""
    rng = np.random.RandomState(seed)
    m1 = cv.mask(lambda d: [d.ellipse(ell(x, y, r, r * 0.85), fill=255) for x, y, r in blobs])
    cv.put(m1, dark)
    m2 = cv.mask(lambda d: [d.ellipse(ell(x - r * 0.2, y - r * 0.25, r * 0.72, r * 0.6), fill=255) for x, y, r in blobs])
    cv.put(gaussian_filter(m2, 0.6 * S) * m1, mid)
    m3 = cv.mask(lambda d: [d.ellipse(ell(x - r * 0.38, y - r * 0.42, r * 0.38, r * 0.3), fill=255) for x, y, r in blobs])
    cv.put(gaussian_filter(m3, 0.8 * S) * m1, light, 0.85)
    # little leaf points around the edge
    if edge:
        pts = []
        for x, y, r in blobs:
            for k in range(int(r * 1.2)):
                a = rng.rand() * 2 * np.pi
                pts.append((x + np.cos(a) * r * 0.95, y + np.sin(a) * r * 0.8, 1.2 + rng.rand() * 1.4))
        m4 = cv.mask(lambda d: [d.ellipse(ell(x, y, s, s * 0.7), fill=255) for x, y, s in pts])
        cv.put(m4 * (1 - m1), edge)


def grass(cv, y0, y1, n, cols, seed=5, hmin=3, hmax=9, x0=0, x1=W):
    rng = np.random.RandomState(seed)
    groups = [[] for _ in cols]
    for i in range(n):
        x = x0 + rng.rand() * (x1 - x0)
        y = y0 + (rng.rand() ** 0.7) * (y1 - y0)
        h = hmin + rng.rand() * (hmax - hmin) * (0.5 + (y - y0) / max(y1 - y0, 1))
        lean = (rng.rand() - 0.5) * h * 0.7
        groups[rng.randint(len(cols))].append((x, y, x + lean * 0.4, y - h * 0.55, x + lean, y - h))
    for g, c in zip(groups, cols):
        def f(d, g=g):
            for x, y, mx, my, tx, ty in g:
                d.line(B(x, y, mx, my, tx, ty), fill=255, width=max(1, int(S * 0.9)))
        cv.put(cv.mask(f), c)


def clover_plant(cv, cx, cy, r, col=(60, 170, 50), dark=(25, 90, 25), light=(150, 230, 110), leaves=3, rot=0.0, stem=True):
    """a clover seen from above: heart shaped leaves with their points in the middle"""
    tt = np.linspace(0, 2 * np.pi, 60)
    hx = 16 * np.sin(tt) ** 3
    hy = -(13 * np.cos(tt) - 5 * np.cos(2 * tt) - 2 * np.cos(3 * tt) - np.cos(4 * tt))
    hy = hy - hy.max()                    # the point of the heart at 0, the lobes up (negative)
    hx, hy = hx / 32, hy / 32             # about 1 wide, 0.9 high
    def leaf(a, k=1.0):
        # outward direction a: the heart's "up" (-y) points along a
        ux, uy = np.cos(a), np.sin(a) * 0.82
        px, py = -np.sin(a), np.cos(a) * 0.82
        sz = r * 0.98 * k
        xs = cx + (hx * px + (-hy) * ux) * sz
        ys = cy + (hx * py + (-hy) * uy) * sz
        return [v * S for p in zip(xs, ys) for v in p]
    angs = [rot + i * 2 * np.pi / leaves - np.pi / 2 for i in range(leaves)]
    if stem:
        cv.put(cv.mask(lambda d: d.line(B(cx, cy, cx + r * 0.15, cy + r * 1.3), fill=255, width=max(1, int(S * r * 0.12)))), dark)
    m = cv.mask(lambda d: [d.polygon(leaf(a), fill=255) for a in angs])
    cv.put(np.clip(gaussian_filter(m, 0.3 * S) * 1.9, 0, 1), dark)
    yy, xx = grid()
    for a in angs:
        lm = cv.mask(lambda d: d.polygon(leaf(a, 0.86), fill=255))
        lx, ly = cx + np.cos(a) * r * 0.5, cy + np.sin(a) * r * 0.42
        sh = np.clip(1.2 - np.hypot(xx - (lx - r * 0.18), yy - (ly - r * 0.22)) / (r * 0.75), 0.6, 1.2)
        cv.put(lm, np.asarray(col, np.float32) * sh[..., None])
        vm = cv.mask(lambda d: d.line(B(cx + np.cos(a) * r * 0.22, cy + np.sin(a) * r * 0.18, cx + np.cos(a) * r * 0.55, cy + np.sin(a) * r * 0.45), fill=255, width=max(1, int(S * 0.5))))
        cv.put(vm * lm, light, 0.6)


def mushroom(cv, cx, by, w, sh, seed=1, cap=(215, 35, 25), lean=0.0):
    """a fly agaric: cream stem from by (ground) up sh, red cap w wide"""
    rng = np.random.RandomState(seed)
    yy, xx = grid()
    # shadow on the ground
    cv.put(gaussian_filter(cv.mask(lambda d: d.ellipse(ell(cx + w * 0.15, by + 1, w * 0.55, w * 0.12), fill=255)), 1.2 * S), (10, 25, 10), 0.55)
    sw = w * 0.17
    top = by - sh
    tx = cx + lean * sh
    stem = cv.mask(lambda d: d.polygon(B(cx - sw * 1.25, by, cx + sw * 1.25, by, tx + sw, top, tx - sw, top), fill=255))
    t = np.clip((xx - (cx - sw * 1.3)) / (sw * 2.6), 0, 1)
    shade = 0.62 + 0.45 * np.sin(t * np.pi * 0.9 + 0.1)
    cv.put(stem, np.array([238, 228, 198], np.float32) * shade[..., None])
    # the ring (skirt)
    ry = top + sh * 0.3
    rx = cx + (tx - cx) * 0.7
    ring = cv.mask(lambda d: d.chord(ell(rx, ry, sw * 1.55, sw * 0.6), 0, 180, fill=255))
    cv.put(ring, np.array([250, 245, 225], np.float32) * (0.75 + 0.3 * t)[..., None])
    # the gills under the cap
    ch = w * 0.42
    cy = top - ch * 0.08
    cv.put(cv.mask(lambda d: d.ellipse(ell(tx, cy + ch * 0.04, w * 0.47, ch * 0.2), fill=255)), (205, 185, 150))
    # the cap: a half dome
    capm = cv.mask(lambda d: d.pieslice(ell(tx, cy, w * 0.5, ch), 180, 360, fill=255))
    capm = np.maximum(capm, cv.mask(lambda d: d.ellipse(ell(tx, cy, w * 0.5, ch * 0.16), fill=255)))
    nx = (xx - tx) / (w * 0.5)
    ny = (yy - cy) / ch
    nz = np.sqrt(np.clip(1 - nx ** 2 - ny ** 2, 0, 1))
    L = np.array([-0.55, -0.65, 0.55])
    L = L / np.linalg.norm(L)
    dif = np.clip(nx * L[0] + ny * L[1] + nz * L[2], 0, 1)
    spec = np.clip(nx * -0.3 + ny * -0.55 + nz * 0.78, 0, 1) ** 18
    capc = np.asarray(cap, np.float32)
    rgb = capc * (0.35 + 0.8 * dif)[..., None] + np.array([255, 200, 180], np.float32) * (spec * 0.4)[..., None]
    cv.put(capm, rgb)
    # white spots, flattened towards the edge of the dome
    spots = []
    for k in range(int(6 + w * 0.3)):
        a = rng.rand() * np.pi
        rr = rng.rand() ** 0.6 * 0.85
        sx, sy = -np.cos(a) * rr, -np.sin(a) * rr
        if sy > -0.1:
            continue
        z = np.sqrt(max(0.05, 1 - sx * sx - sy * sy))
        s = w * (0.03 + rng.rand() * 0.035)
        spots.append((tx + sx * w * 0.5, cy + sy * ch, s * (0.5 + 0.5 * z) * 1.1, s * (0.35 + 0.65 * z) * 0.9))
    sm = cv.mask(lambda d: [d.ellipse(ell(x, y, a, b), fill=255) for x, y, a, b in spots])
    cv.put(sm * capm, np.array([252, 246, 232], np.float32) * (0.62 + 0.45 * dif)[..., None])
    # a dark rim
    rim = np.clip(gaussian_filter(capm, 0.5 * S) * -1 + capm, 0, 1) * 2
    cv.put(np.clip(rim, 0, 1), (90, 10, 10), 0.6)


def tube_snake(cv, pts, r0, r1, body=(70, 200, 250), shade=(15, 70, 165), belly=(200, 245, 255), outline=(8, 25, 70), seed=1):
    """the snake's body: a shaded tube along a smooth curve through pts
    (tail first), radius r0 at the tail to r1 at the neck"""
    from scipy.interpolate import splprep, splev
    p = np.array(pts, np.float32).T
    tck, _ = splprep(p, s=0, k=3)
    u = np.linspace(0, 1, 3000)
    x, y = splev(u, tck)
    seg = np.sqrt(np.diff(x) ** 2 + np.diff(y) ** 2)
    s = np.concatenate([[0], np.cumsum(seg)])
    ln = s[-1]
    t = s / ln
    rad = r0 + (r1 - r0) * np.clip(t * 1.25, 0, 1) ** 0.6
    tree = cKDTree(np.stack([x, y], 1) * S)
    yy, xx = grid()
    x0, x1 = int((x.min() - r1 - 3) * S), int((x.max() + r1 + 3) * S)
    y0, y1 = int((y.min() - r1 - 3) * S), int((y.max() + r1 + 3) * S)
    x0, y0 = max(x0, 0), max(y0, 0)
    x1, y1 = min(x1, WS), min(y1, HS)
    py, px = np.mgrid[y0:y1, x0:x1]
    q = np.stack([px.ravel(), py.ravel()], 1).astype(np.float32)
    d, idx = tree.query(q)
    d = d.reshape(px.shape) / S
    idx = idx.reshape(px.shape)
    r = rad[idx]
    dx = (px / S - x[idx]) / r
    dy = (py / S - y[idx]) / r
    inside = d < r
    edge = (d >= r) & (d < r + 0.75)
    nz = np.sqrt(np.clip(1 - dx * dx - dy * dy, 0, 1))
    L = np.array([-0.45, -0.7, 0.55])
    L /= np.linalg.norm(L)
    dif = np.clip(dx * L[0] + dy * L[1] + nz * L[2], 0, 1)
    Hh = (L + np.array([0, 0, 1])) / np.linalg.norm(L + np.array([0, 0, 1]))
    spec = np.clip(dx * Hh[0] + dy * Hh[1] + nz * Hh[2], 0, 1) ** 24
    # pattern: dark diamonds along the back, a pale belly underneath
    tx_, ty_ = np.gradient(x)[idx], np.gradient(y)[idx]
    tn = np.sqrt(tx_ ** 2 + ty_ ** 2) + 1e-6
    side = (dx * -ty_ + dy * tx_) / tn            # across the body, -1..1
    arc = s[idx]
    diamond = (np.abs(np.mod(arc / 7.0, 1) - 0.5) * 2 + np.abs(side + 0.15) * 1.6) < 0.75
    bel = np.clip((side - 0.45) * 4, 0, 1) * (dy > -0.2)
    base = np.asarray(body, np.float32)
    dark = np.asarray(shade, np.float32)
    col = dark + (base - dark) * np.clip(dif * 1.25, 0, 1)[..., None]
    col = np.where(diamond[..., None], col * 0.55 + np.array([10, 30, 90]) * 0.45, col)
    col = col * (1 - bel[..., None] * 0.6) + np.asarray(belly, np.float32) * (bel * 0.6 * (0.5 + dif))[..., None]
    col = col + np.array([255, 255, 255]) * (spec * 0.85)[..., None]
    # scales: a fine grid of darker dots
    sc = (np.mod(arc * 1.3 + side * 2.0, 1.0) < 0.18) & (np.mod(side * 3.5 + 10, 1.0) < 0.25)
    col = np.where(sc[..., None] & inside[..., None], col * 0.85, col)
    region = cv.a[y0:y1, x0:x1]
    region[edge] = outline
    region[inside] = col[inside]
    cv.a[y0:y1, x0:x1] = region
    return x, y, rad


def snake_head(cv, cx, cy, rx, ry, face=1, body=(70, 200, 250), shade=(15, 70, 165), outline=(8, 25, 70)):
    yy, xx = grid()
    nx = (xx - cx) / rx
    ny = (yy - cy) / ry
    dd = nx * nx + ny * ny
    inside = dd < 1
    edge = (dd >= 1) & (dd < (1 + 0.8 / min(rx, ry)) ** 2)
    nz = np.sqrt(np.clip(1 - dd, 0, 1))
    L = np.array([-0.45, -0.7, 0.55])
    L /= np.linalg.norm(L)
    dif = np.clip(nx * L[0] + ny * L[1] + nz * L[2], 0, 1)
    spec = np.clip(nx * -0.25 + ny * -0.45 + nz * 0.86, 0, 1) ** 26
    base = np.asarray(body, np.float32)
    dark = np.asarray(shade, np.float32)
    col = dark + (base - dark) * np.clip(dif * 1.25, 0, 1)[..., None]
    col = col + 255 * (spec * 0.9)[..., None]
    cv.a[edge] = outline
    cv.a[inside] = col[inside]
    # cheeks
    ch = cv.mask(lambda d: d.ellipse(ell(cx + face * rx * 0.45, cy + ry * 0.35, rx * 0.2, ry * 0.13), fill=255))
    cv.put(gaussian_filter(ch, 0.8 * S), (255, 140, 190), 0.75)
    # the smile
    mx = cx + face * rx * 0.62
    cv.put(cv.mask(lambda d: d.arc(ell(mx - face * rx * 0.1, cy + ry * 0.2, rx * 0.36, ry * 0.32), 20 if face > 0 else 100, 80 if face > 0 else 160, fill=255, width=int(S * 1.1))), outline)
    # the eyes: big and friendly, looking forward
    for ex, ey, er in ((cx + face * rx * 0.12, cy - ry * 0.42, ry * 0.42), (cx + face * rx * 0.6, cy - ry * 0.36, ry * 0.36)):
        cv.put(cv.mask(lambda d: d.ellipse(ell(ex, ey, er * 1.12, er * 1.2), fill=255)), outline)
        cv.put(cv.mask(lambda d: d.ellipse(ell(ex, ey, er, er * 1.08), fill=255)), (250, 252, 255))
        cv.put(cv.mask(lambda d: d.ellipse(ell(ex + face * er * 0.35, ey + er * 0.1, er * 0.55, er * 0.68), fill=255)), (10, 10, 30))
        cv.put(cv.mask(lambda d: d.ellipse(ell(ex + face * er * 0.15, ey - er * 0.3, er * 0.22, er * 0.22), fill=255)), (255, 255, 255))


def tongue(cv, x0, y0, x1, y1, col=(230, 30, 40)):
    fx, fy = x1 - x0, y1 - y0
    n = np.hypot(fx, fy)
    px, py = -fy / n, fx / n
    w = int(S * 1.5)
    def f(d):
        d.line(B(x0, y0, x1, y1), fill=255, width=w)
        d.line(B(x1, y1, x1 + fx / n * 3 + px * 2, y1 + fy / n * 3 + py * 2), fill=255, width=w)
        d.line(B(x1, y1, x1 + fx / n * 3 - px * 2, y1 + fy / n * 3 - py * 2), fill=255, width=w)
    cv.put(cv.mask(f), col)


def orb(cv, cx, cy, r, glow=True):
    if glow:
        cv.add(radial(cx, cy, r * 3.2), (255, 255, 220), 0.55)
    yy, xx = grid()
    nx, ny = (xx - cx) / r, (yy - cy) / r
    dd = nx * nx + ny * ny
    nz = np.sqrt(np.clip(1 - dd, 0, 1))
    dif = np.clip(-0.45 * nx - 0.6 * ny + 0.66 * nz, 0, 1)
    col = np.array([150, 160, 185], np.float32) + np.array([105, 95, 70], np.float32) * dif[..., None]
    m = (dd < 1)
    cv.a[m] = col[m]
    # the dimples of the ball in the game
    dots = [(-0.35, -0.1), (0.25, -0.35), (0.3, 0.3), (-0.2, 0.45), (0.0, 0.05), (-0.55, 0.3), (0.6, -0.05)]
    cv.put(cv.mask(lambda d: [d.ellipse(ell(cx + a * r, cy + b * r, r * 0.11, r * 0.11), fill=255) for a, b in dots]), (140, 145, 170), 0.8)


def heart(cv, cx, cy, r, glow=True):
    if glow:
        cv.add(radial(cx, cy, r * 3), (255, 120, 150), 0.4)
    def f(d):
        d.ellipse(ell(cx - r * 0.45, cy - r * 0.2, r * 0.55, r * 0.5), fill=255)
        d.ellipse(ell(cx + r * 0.45, cy - r * 0.2, r * 0.55, r * 0.5), fill=255)
        d.polygon(B(cx - r * 0.98, cy - r * 0.05, cx + r * 0.98, cy - r * 0.05, cx, cy + r * 0.95), fill=255)
    m = cv.mask(f)
    cv.put(np.clip(gaussian_filter(m, 0.3 * S) * 1.6 - 0.3, 0, 1), (110, 10, 20))
    inner = np.clip((gaussian_filter(m, 0.7 * S) - 0.55) * 4, 0, 1)
    yy, xx = grid()
    t = np.clip((yy - (cy - r)) / (2 * r), 0, 1)
    cv.put(inner, np.array([240, 50, 60], np.float32) * (1.05 - 0.45 * t)[..., None])
    cv.put(gaussian_filter(cv.mask(lambda d: d.ellipse(ell(cx - r * 0.5, cy - r * 0.32, r * 0.22, r * 0.16), fill=255)), 0.3 * S), (255, 220, 225), 0.9)


def crate(cv, x, y, s):
    """a wooden crate (the game's pushable block), front face s x s"""
    def f(d):
        d.rectangle(B(x, y, x + s, y + s), fill=255)
    m = cv.mask(f)
    yy, xx = grid()
    n = noise(0.5, 11, sy=0.1)
    wood = np.array([200, 130, 55], np.float32) * (0.8 + 0.35 * n)[..., None]
    cv.put(m, wood)
    b = s * 0.14
    frame = cv.mask(lambda d: [d.rectangle(B(x, y, x + s, y + b), fill=255), d.rectangle(B(x, y + s - b, x + s, y + s), fill=255),
                               d.rectangle(B(x, y, x + b, y + s), fill=255), d.rectangle(B(x + s - b, y, x + s, y + s), fill=255),
                               d.line(B(x + b, y + s - b, x + s - b, y + b), fill=255, width=int(S * b * 0.9))])
    cv.put(frame, np.array([150, 85, 30], np.float32) * (0.85 + 0.3 * n)[..., None])
    cv.put(cv.mask(lambda d: d.rectangle(B(x, y, x + s, y + s), outline=255, width=S)), (60, 30, 10))


# ------------------------------------------------------------------ fireflies
def fireflies(rng, n, box):
    x0, y0, x1, y1 = box
    return [(int(x0 + rng.rand() * (x1 - x0)), int(y0 + rng.rand() * (y1 - y0)), FIRE[i % 3]) for i in range(n)]


# ------------------------------------------------------------------ the scenes
def forest_back(cv, seed=1, horizon=170, glow=(205, 60)):
    rng = np.random.RandomState(seed)
    cv.a = ygrad([(0, (20, 58, 52)), (70, (70, 130, 85)), (130, (95, 150, 80)), (horizon, (70, 120, 60)), (256, (30, 60, 25))])
    cv.add(radial(glow[0], glow[1], 170), (255, 240, 170), 0.75)
    cv.add(radial(glow[0], glow[1], 60), (255, 250, 220), 0.6)
    # far trees: pale, misty
    for k in range(16):
        x = rng.rand() * W
        w = 3 + rng.rand() * 5
        mist = 0.55 + 0.25 * rng.rand()
        c = np.array([40, 85, 70]) * (1 - mist) + np.array([120, 170, 120]) * mist
        tree_trunk(cv, x, x + w, -5, horizon + 5, c, bark=False, roots=False)
    leaf_cluster(cv, [(rng.rand() * W, 10 + rng.rand() * 55, 10 + rng.rand() * 16) for _ in range(26)],
                 (60, 110, 80), (80, 135, 90), (115, 165, 105), seed=seed + 1)
    # mist over the far trees
    yy, _ = grid()
    cv.add(np.clip(1 - np.abs(yy - 120) / 70, 0, 1), (150, 190, 140), 0.25)
    light_rays(cv, glow[0] - 30, glow[1] - 60, [(0, 9), (22, 5), (40, 12), (66, 7), (88, 4)], 0.28, seed)
    # middle trees
    for k in range(7):
        x = rng.rand() * W
        w = 7 + rng.rand() * 7
        tree_trunk(cv, x, x + w, -5, horizon + 8 + rng.rand() * 6, (75, 70, 55), light_from=1 if x < glow[0] else -1, seed=seed + 10 + k)
    leaf_cluster(cv, [(rng.rand() * W, 5 + rng.rand() * 40, 12 + rng.rand() * 18) for _ in range(22)],
                 (30, 70, 40), (50, 105, 50), (100, 160, 70), seed=seed + 2, edge=(35, 80, 45))


def forest_floor(cv, y0, seed=7):
    rng = np.random.RandomState(seed)
    def f(d):
        pts = [(0, H)]
        for i in range(0, W + 11, 10):
            pts.append((i, y0 + np.sin(i * 0.05 + seed) * 4 + rng.rand() * 3))
        pts.append((W, H))
        d.polygon([v * S for p in pts for v in p], fill=255)
    m = cv.mask(f)
    floor = ygrad([(y0 - 5, (95, 140, 55)), (y0 + 30, (60, 105, 40)), (256, (25, 55, 22))])
    n = noise(1.5, seed)
    floor = floor * (0.75 + 0.4 * n)[..., None]
    cv.put(m, floor)
    # sunny patch
    cv.add(m * radial(160, y0 + 30, 120), (200, 220, 120), 0.35)
    grass(cv, y0 - 3, H, 2600, [(40, 90, 30), (70, 130, 40), (110, 170, 60), (150, 200, 80), (55, 110, 35)], seed=seed, hmin=3, hmax=10)


def canopy(cv, seed=4):
    rng = np.random.RandomState(seed)
    blobs = []
    for i in range(42):
        x = rng.rand() * (W + 40) - 20
        y = -8 + (rng.rand() ** 1.6) * 34 + 14 * (abs(x - W / 2) / (W / 2)) ** 2
        blobs.append((x, y, 9 + rng.rand() * 12))
    leaf_cluster(cv, blobs, (18, 45, 25), (35, 85, 40), (90, 150, 60), seed=seed, edge=(22, 55, 30))


def loading():
    """the loading picture -> (rgb 256x320x3, fireflies [(x, y, colour)])"""
    rng = np.random.RandomState(42)
    cv = Canvas()
    forest_back(cv, seed=3, horizon=150, glow=(196, 70))
    forest_floor(cv, 150, seed=9)
    # the big trees at the sides
    tree_trunk(cv, -10, 34, -5, 222, (90, 64, 44), light_from=1, seed=31)
    tree_trunk(cv, 288, 330, -5, 218, (90, 64, 44), light_from=-1, seed=32)
    canopy(cv, seed=5)
    # clover patches on the floor
    for k in range(26):
        x = 40 + rng.rand() * 240
        y = 160 + rng.rand() * 70
        clover_plant(cv, x, y, 2.2 + rng.rand() * 2.5, leaves=3, rot=rng.rand() * 6, stem=False,
                     col=(70, 165, 55), dark=(25, 80, 25), light=(140, 215, 100))
    # little white flowers
    fl = [(rng.rand() * W, 158 + rng.rand() * 80) for _ in range(30)]
    cv.put(cv.mask(lambda d: [d.ellipse(ell(x, y, 0.9, 0.7), fill=255) for x, y in fl]), (245, 245, 225))
    # mushrooms: a group at the left, one at the right, little ones about
    mushroom(cv, 50, 198, 34, 22, seed=1, lean=-0.05)
    mushroom(cv, 22, 204, 22, 14, seed=2, lean=0.1)
    mushroom(cv, 76, 203, 15, 10, seed=3)
    mushroom(cv, 288, 196, 30, 20, seed=4, lean=0.08)
    mushroom(cv, 309, 204, 16, 11, seed=5)
    mushroom(cv, 150, 158, 10, 7, seed=6)
    mushroom(cv, 104, 164, 8, 5, seed=8)
    mushroom(cv, 246, 150, 9, 6, seed=7)
    # the snake: tail at the left, the neck up at the right
    pts = [(96, 190), (116, 196), (140, 188), (164, 196), (188, 189), (206, 178), (213, 160), (209, 144), (213, 130)]
    # shadow under the body
    sh = cv.mask(lambda d: d.line(B(*[v for p in pts[:7] for v in (p[0] + 2, p[1] + 5)]), fill=255, width=int(S * 9), joint='curve'))
    cv.put(gaussian_filter(sh, 2 * S), (10, 25, 8), 0.55)
    tube_snake(cv, pts, 2.0, 8.5)
    snake_head(cv, 221, 120, 15, 12, face=1)
    tongue(cv, 233, 125, 247, 128)
    # what the snake is after: a big four-leaf clover, a ball and a heart
    clover_plant(cv, 264, 132, 12, leaves=4, rot=0.4, col=(60, 190, 60), dark=(15, 95, 25), light=(170, 245, 130))
    orb(cv, 128, 150, 6.5)
    heart(cv, 270, 88, 8)
    ff = fireflies(rng, 18, (40, 60, 285, 150))
    return cv.small(), ff


def meadow():
    """the title screen background -> (rgb, fireflies)"""
    rng = np.random.RandomState(7)
    cv = Canvas()
    forest_back(cv, seed=8, horizon=96, glow=(250, 36))
    # a bright meadow from y 70 down
    def f(d):
        pts = [(0, H)] + [(i, 66 + np.sin(i * 0.04) * 5 + np.sin(i * 0.13) * 2) for i in range(0, W + 9, 8)] + [(W, H)]
        d.polygon([v * S for p in pts for v in p], fill=255)
    m = cv.mask(f)
    fl = ygrad([(60, (120, 175, 70)), (120, (85, 150, 55)), (170, (55, 115, 40)), (256, (30, 70, 25))])
    n = noise(2.0, 3)
    cv.put(m, fl * (0.8 + 0.35 * n)[..., None])
    cv.add(m * radial(160, 90, 140), (220, 230, 140), 0.3)
    grass(cv, 64, H, 3200, [(50, 105, 35), (80, 145, 45), (120, 185, 65), (160, 210, 90), (60, 120, 40)], seed=4, hmin=2, hmax=7)
    for k in range(40):
        x, y = rng.rand() * W, 75 + rng.rand() * 90
        clover_plant(cv, x, y, 1.6 + rng.rand() * 1.8, leaves=3, rot=rng.rand() * 6, stem=False,
                     col=(80, 170, 60), dark=(30, 90, 30), light=(150, 220, 110))
    fls = [(rng.rand() * W, 70 + rng.rand() * 100, rng.randint(3)) for _ in range(60)]
    for i, c in enumerate([(250, 250, 235), (250, 230, 90), (240, 160, 200)]):
        cv.put(cv.mask(lambda d: [d.ellipse(ell(x, y, 0.8, 0.6), fill=255) for x, y, k in fls if k == i]), c)
    tree_trunk(cv, -8, 22, -5, 150, (90, 64, 44), light_from=1, seed=41)
    tree_trunk(cv, 298, 330, -5, 150, (90, 64, 44), light_from=-1, seed=42)
    canopy(cv, seed=12)
    mushroom(cv, 20, 152, 26, 16, seed=11)
    mushroom(cv, 302, 152, 24, 15, seed=13, lean=-0.06)
    ff = fireflies(rng, 12, (30, 40, 290, 100))
    return cv.small(), ff


# ------------------------------------------------------------------ colours
def quantize(rgb, fixed, nfree, first_free, seed=1, dither=10.0, keep=None):
    """reduce rgb (H x W x 3, 0..255) to indexes. fixed: {index: (r,g,b) 4 bit}
    nfree colours are chosen (k-means, colours given 4 bits a gun) and put
    at first_free...  keep: a mask of pixels that must not change (ignored
    for the colour choice). Returns (index picture, palette list of 32)"""
    w = np.array([0.30, 0.59, 0.11], np.float32) * 3
    px = rgb.reshape(-1, 3)
    use = px if keep is None else px[~keep.ravel()]
    rng = np.random.RandomState(seed)
    sample = use[rng.choice(len(use), min(len(use), 30000), replace=False)]
    fixc = np.array([[c * 17 for c in fixed[i]] for i in sorted(fixed)], np.float32)
    # start the free colours on spread pixels
    free = sample[rng.choice(len(sample), nfree, replace=False)].copy()
    for it in range(30):
        allc = np.vstack([fixc, free])
        d = (((sample[:, None, :] - allc[None, :, :]) ** 2) * w).sum(-1)
        a = d.argmin(1)
        for k in range(nfree):
            sel = sample[a == len(fixc) + k]
            if len(sel):
                free[k] = sel.mean(0)
            else:
                # an unused colour: put it on the worst pixel
                free[k] = sample[d.min(1).argmax()]
    free = np.clip(np.round(free / 17), 0, 15).astype(int)
    pal = [(0, 0, 0)] * 32
    for i in fixed:
        pal[i] = tuple(fixed[i])
    for k in range(nfree):
        pal[first_free + k] = tuple(int(v) for v in free[k])
    allow = sorted(fixed) + list(range(first_free, first_free + nfree))
    P = np.array([[c * 17 for c in pal[i]] for i in allow], np.float32)
    bayer = np.array([[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]], np.float32) / 16 - 0.47
    hh, ww = rgb.shape[:2]
    bt = np.tile(bayer, (hh // 4 + 1, ww // 4 + 1))[:hh, :ww]
    v = rgb + bt[..., None] * dither
    out = np.zeros((hh, ww), np.uint8)
    for y in range(hh):
        d = (((v[y][:, None, :] - P[None]) ** 2) * w).sum(-1)
        out[y] = np.array(allow)[d.argmin(1)]
    return out, pal
