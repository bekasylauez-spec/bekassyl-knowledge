# -*- coding: utf-8 -*-
"""an_win.py sheet px0 py0 px1 py1 [types] : list entities of analog sheet inside PNG-pixel window (2000x1413 PNG)."""
import pickle, sys
R = pickle.load(open('an.pkl', 'rb'))
s = sys.argv[1]; i = int(s[2:]) - 3
X0, Y0 = -41822 + 59400 * i, -1593693
k = 59400 / 2000.0
px0, py0, px1, py1 = map(float, sys.argv[2:6])
wx0, wx1 = X0 + px0 * k, X0 + px1 * k
wy1, wy0 = Y0 + 42000 - py0 * k, Y0 + 42000 - py1 * k
ty = sys.argv[6].split(',') if len(sys.argv) > 6 else None
print('win', round(wx0), round(wy0), round(wx1), round(wy1))
for d in R:
    b = d.get('bb')
    if not b: continue
    if b[0] < wx0 or b[2] > wx1 or b[1] < wy0 or b[3] > wy1: continue
    if ty and d['t'] not in ty: continue
    ex = ''
    for kk in ('txt', 'ht', 'st', 'ds', 'dimlfac', 'meas', 'pat', 'psc', 'blk', 'r', 'np'):
        if kk in d and d[kk] not in (None, ''): ex += ' %s=%s' % (kk, str(d[kk])[:60].replace('\n', ' '))
    print(d['h'], d['t'], d['layer'], d['lt'], d['lw'], '(%d,%d,%d,%d)' % tuple(round(v) for v in b), ex)
