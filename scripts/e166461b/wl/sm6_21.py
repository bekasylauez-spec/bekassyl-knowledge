import sys; sys.path.insert(0, 'wl'); from sm6_geom import *
from notes import notes
X = 1786200.0; A1 = 9701
R, ops, er = elevation(X, A1, 15206, 19506, None)
W = lambda x, y: [X + x, SY + y]
lo, hi = A1 + 5800, A1 + 6660
for r in R:
    if r['t'] == 'LINE' and lo < r['x0'] and r['x1'] < hi and r['y0'] > 15000: er.append(r['h'])
    elif r['t'] == 'DIMENSION' and r['y0'] > 15000 and all(lo - 1500 < p[0] < hi + 20 for p in r['sp'][:2]) and min(p[0] for p in r['sp'][:2]) > lo - 100: er.append(r['h'])
for n in notes(X, SY, 59400, 42000):
    xs = [p[0] for p in n['pts'][1:]]
    if xs and all(lo < x < hi for x in xs): er.append(n['h'])
er.append('1E0E19')                                   # axis 2/1 (not in our scheme)
diag = sorted([r for r in R if r['t'] == 'LWPOLYLINE' and len(r['sp']) == 3 and abs(r['sp'][0][1] - 19756) < 3], key=lambda r: r['x0'])
for i, r in enumerate(diag):
    x0 = A1 + 1225 if i == 0 else r['sp'][0][0]; x1 = A1 + 6675 if i == 0 else (A1 + 18825 if i == 3 else r['sp'][2][0])
    mx = r['sp'][1][0] - r['sp'][0][0]
    ops.append(dict(t='pl', p=[W(x0, 15206), W(x0 + mx, 19506 - 452), W(x1, 19506)], layer='Размеры', tag='VD%d' % i))
    ops.append(dict(t='eprops', src=r['h'], h=['VD%d' % i]))
ops = [dict(t='erase', h=er)] + [o for o in ops if o] + [dict(t='save')]
print('erase', len(er), 'ops', len(ops))
if '--run' in sys.argv:
    out = gx.run(ops, 'sm6_21'); print([l for l in out.splitlines() if 'ERR' in l or 'done' in l][-6:])
