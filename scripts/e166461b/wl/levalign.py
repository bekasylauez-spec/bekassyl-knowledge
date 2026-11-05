# level marks of one elevation in one column (the analog's): marks whose arrow x differs from the majority column are moved whole.
# usage: python wl/levalign.py X W H [x_from x_to]   (only marks with arrow x in [x_from, x_to] sheet-relative = one elevation)
import sys, collections; sys.path.insert(0, 'wl'); from common import *
X, W, H = (float(v) for v in sys.argv[1:4]); lo, hi = (float(sys.argv[4]), float(sys.argv[5])) if len(sys.argv) > 5 else (-1e9, 1e9)
M = [r for r in listwin(X, 455939, W, H, None) if r['t'] == 'SPDSLEVELMARK' and lo <= r['sp'][0][0] <= hi]
col = collections.Counter(round(r['sp'][0][0], -2) for r in M).most_common(1)[0][0]
ref = [r for r in M if round(r['sp'][0][0], -2) == col][0]
ops = [dict(t='move', h=[r['h']], d=[ref['sp'][0][0] - r['sp'][0][0], 0]) for r in M if abs(r['sp'][0][0] - ref['sp'][0][0]) > 100]
print('marks', len(M), 'column', col, 'moved', len(ops))
if ops: print(gx.run(ops + [dict(t='save')], 'lva')[-40:])
