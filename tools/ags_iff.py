#!/usr/bin/env python3
"""ags_iff.py <ref.iff> <in.ppm/png> <out.iff>: an AGS2 screenshot for the CF card menu:
320x128 (every other line of a 320x256 picture), colours 0-9 from the picture,
10-15 the menu's own colours (taken from an existing card screenshot)."""
import sys, struct, numpy as np
from PIL import Image
ref, src, out = sys.argv[1:4]
r = open(ref, 'rb').read(); i = 12; ch = {}
while i < len(r):
    t = r[i:i+4]; n = struct.unpack('>I', r[i+4:i+8])[0]; ch[t] = r[i+8:i+8+n]; i += 8+n+(n & 1)
menu = [tuple(ch[b'CMAP'][k*3:k*3+3]) for k in range(10, 16)]
a = np.asarray(Image.open(src).convert('RGB')).astype(int)[::2]
cols, cnt = np.unique(a.reshape(-1, 3), axis=0, return_counts=True)
pal = [tuple(int(v) for v in c) for c in cols[np.argsort(-cnt)][:10]]
while len(pal) < 10: pal.append((0, 0, 0))
P = np.array(pal)
idx = (((a[:, :, None, :] - P[None, None]) ** 2) * (3, 6, 1)).sum(-1).argmin(-1)
body = bytearray()
for y in range(128):
    for p in range(4):
        body += np.packbits(((idx[y] >> p) & 1).astype(np.uint8)).tobytes()
def chunk(t, d): return t + struct.pack('>I', len(d)) + d + (b'\0' if len(d) & 1 else b'')
data = b'ILBM' + chunk(b'BMHD', struct.pack('>HHhhBBBBHBBhh', 320, 128, 0, 0, 4, 0, 0, 0, 0, 22, 11, 320, 256)) \
     + chunk(b'CMAP', b''.join(bytes(c) for c in pal + menu)) + chunk(b'CAMG', ch[b'CAMG']) + chunk(b'BODY', bytes(body))
open(out, 'wb').write(b'FORM' + struct.pack('>I', len(data)) + data)
Image.fromarray(P[idx].astype(np.uint8)).resize((640, 256), Image.NEAREST).save(out + '.png')
