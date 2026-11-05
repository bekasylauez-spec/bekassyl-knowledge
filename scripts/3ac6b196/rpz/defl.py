import sys, json, collections
sys.stdout.reconfigure(encoding='utf-8'); sys.path.insert(0, '.')
from lr import rows
xyz = {}
for r in rows('tbl01.101.csv'):
    if len(r) > 6 and r[0].isdigit() and r[2].strip().isdigit(): xyz[int(r[2])] = tuple(float(v) for v in r[3:6])
CS = {'1', '2', '3', '4', '5', '7', '8'}
Z = collections.defaultdict(float)
for r in rows('tbl03.5_1.csv'):
    if len(r) > 7 and r[0].isdigit() and r[2].strip() in CS:
        Z[int(r[4])] += float(r[7])
res = {}
for L in (3.3, 6.6):
    pts = {(round(p[0], 3), round(p[1], 3)): Z[n] for n, p in xyz.items() if abs(p[2] - L) < 1e-3}
    best = (0, None)
    for i in range(10):
        for j in range(2):
            x0, x1, y0, y1 = 6 * i, 6 * i + 6, 6 * j, 6 * j + 6
            cor = [pts.get((float(a), float(b))) for a in (x0, x1) for b in (y0, y1)]
            if None in cor: continue
            inner = [(k, v) for k, v in pts.items() if x0 < k[0] < x1 and y0 < k[1] < y1]
            for k, v in inner:
                # билинейная интерполяция опор
                u = (k[0] - x0) / 6; w = (k[1] - y0) / 6
                base = cor[0] * (1 - u) * (1 - w) + cor[2] * u * (1 - w) + cor[1] * (1 - u) * w + cor[3] * u * w
                f = base - v
                if f > best[0]: best = (f, (k, i, j))
    res[str(L)] = best
fz = [Z[n] for n, p in xyz.items() if abs(p[2] + 2.0) < 1e-3]
res['settle_max'] = min(fz); res['settle_min'] = max(fz)
print(res)
json.dump(res, open('defl.json', 'w'), default=str)
