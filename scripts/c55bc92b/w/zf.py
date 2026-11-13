import io, collections, re, sys
from shapely.geometry import Polygon
import numpy as np
D = r"C:\Users\Admin\AppData\Local\Temp\claude\a7137524bdaa49d0\c55bc92b-0511-4932-9c00-c1294111057c\scratchpad\w\out" + "\\"
src = sys.argv[1] if len(sys.argv) > 1 else D + 'zfight2.tsv'
out = io.open(D + 'zf_analysis.txt', 'w', encoding='utf-8')
def P(*a): out.write(' '.join(str(x) for x in a) + '\n')
Z = [l.rstrip('\n').split('\t') for l in io.open(src, encoding='utf-8')]
def parse(loops):
    res = []
    for lp in loops.split('|'):
        pts = [tuple(map(float, p.split(';'))) for p in lp.split(' ') if p]
        res.append(np.array(pts))
    return res
def poly2d(loops, e1, e2):
    rings = []
    for arr in loops:
        if len(arr) < 3: continue
        rings.append([(float(np.dot(p, e1)), float(np.dot(p, e2))) for p in arr])
    if not rings: return None
    polys = [Polygon(r).buffer(0) for r in rings]
    outer = max(polys, key=lambda p: p.area)
    for p in polys:
        if p is not outer: outer = outer.difference(p)
    return outer
real = []
for z in Z:
    cn, ak, al, an, aid, am, bk, bl, bn, bid, bm, nx, ny, nz, area, ex_, ey_, ez_, la, lb = z
    n = np.array([float(nx), float(ny), float(nz)]); n = n / np.linalg.norm(n)
    h = np.array([1, 0, 0]) if abs(n[0]) < 0.9 else np.array([0, 1, 0])
    e1 = np.cross(n, h); e1 /= np.linalg.norm(e1); e2 = np.cross(n, e1)
    try:
        pa = poly2d(parse(la), e1, e2); pb = poly2d(parse(lb), e1, e2)
        if pa is None or pb is None: continue
        a = pa.intersection(pb).area
    except Exception as e:
        P('ERR', e); continue
    if a > 1.0: real.append((a, an, bn, aid, bid, cn))
P('candidate rows', len(Z))
P('real overlap area >1 mm2 (same-direction coplanar):', len(real), ' pairs; distinct element pairs:', len(set((r[3], r[4]) for r in real)))
def kind(n):
    n = re.sub(r' - [\w\-+А-Яа-я]+$', '', n); n = re.sub(r'\d+(\.\d+)?', '#', n); return n[:55]
c = collections.Counter()
for r in real: c[tuple(sorted([kind(r[1]), kind(r[2])]))] += 1
for k, v in c.most_common(30): P(v, k)
for r in sorted(real, reverse=True)[:15]: P(round(r[0], 1), r[1][:70], '<->', r[2][:70])
out.close()
print(io.open(D + 'zf_analysis.txt', encoding='utf-8').read())
