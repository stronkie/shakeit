#!/usr/bin/env python3
"""whdlha.py <dir> <drawer> <out.lha>: put <dir>/<drawer>/ and <dir>/<drawer>.info
in an LhA archive (with the toolkit's LhA writer) and check it."""
import os, sys, time
TK = os.environ.get('AMIGA_TK', '/home/claude/amiga-toolkit')
sys.path.insert(0, os.path.join(TK, 'tools'))
base, drawer, out = sys.argv[1:4]
sys.argv = [sys.argv[0], '0']
import make_whdload as mw
now = time.time()
entries, files = [], {}
for root, dirs, fs in os.walk(os.path.join(base, drawer)):
    dirs.sort()
    rel = os.path.relpath(root, base).replace(os.sep, '/')
    entries.append(mw.lha_entry(rel + '/', b'', now, is_dir=True))
    for f in sorted(fs):
        data = open(os.path.join(root, f), 'rb').read()
        files[rel + '/' + f] = data
        entries.append(mw.lha_entry(rel + '/' + f, data, now))
info = drawer + '.info'
files[info] = open(os.path.join(base, info), 'rb').read()
entries.append(mw.lha_entry(info, files[info], now))
mw.write_lha(out, entries)
back = dict(mw.read_lha(out))
for n, b in files.items():
    assert back[n] == b, n
print('%s: %d bytes, %d entries (checked)' % (os.path.basename(out), os.path.getsize(out), len(entries)))
