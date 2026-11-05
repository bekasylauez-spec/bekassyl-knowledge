"""short adjacent dims sharing an endpoint: texts spread to both sides along the dim line (Bekassyl rule)"""
import ab, ezdxf, logging, json, math, sys
logging.disable(logging.CRITICAL)
ONLY = set(sys.argv[1].split(',')) if len(sys.argv) > 1 else None
d = ezdxf.readfile(ab.S + r'\w\live.dxf'); ms = d.modelspace()
P = json.load(open(ab.S + r'\w\sheets.json'))
T = {}
for ln in open(ab.S + r'\w\geom.txt', encoding='utf-8-sig'):
    f = ln.rstrip('\r\n').split('|')
    if f[0] == 'T' and len(f) > 7 and f[7].strip() and f[2] == 'DIMENSION':
        T.setdefault(f[1], []).append([float(v) for v in f[3:7]])
def sheet(p):
    for s, w in P.items():
        if w[0] <= p[0] <= w[2] and w[1] <= p[1] <= w[3]: return s
D = []
for e in ms.query('DIMENSION'):
    try:
        if e.dimtype & 7 not in (0, 1): continue
        a, b, c = e.dxf.defpoint2, e.dxf.defpoint3, e.dxf.defpoint
        s = sheet((a.x, a.y))
        if not s or (ONLY and s not in ONLY) or e.dxf.handle not in T: continue
        vert = abs(a.x - b.x) < 1 and abs(a.y - b.y) > 1
        if not vert and abs(a.y - b.y) > 1: continue
        t0, t1 = sorted([a.y, b.y] if vert else [a.x, b.x])
        bx = T[e.dxf.handle][0]; w = (bx[3] - bx[1]) if vert else (bx[2] - bx[0]); h = (bx[2] - bx[0]) if vert else (bx[3] - bx[1])
        cen = ((bx[0] + bx[2]) / 2, (bx[1] + bx[3]) / 2)
        D.append(dict(h=e.dxf.handle, s=s, vert=vert, line=round(c.x if vert else c.y), t0=t0, t1=t1, w=w, hh=h, cen=cen))
    except Exception:
        pass
ops = []; done = set()
from collections import defaultdict
G = defaultdict(list)
for x in D: G[(x['s'], x['vert'], x['line'])].append(x)
for k, L in G.items():
    L.sort(key=lambda x: x['t0'])
    for i in range(len(L) - 1):
        A, B = L[i], L[i + 1]
        if abs(A['t1'] - B['t0']) > 2: continue
        shortA = A['w'] + 0.4 * A['hh'] > (A['t1'] - A['t0'])
        shortB = B['w'] + 0.4 * B['hh'] > (B['t1'] - B['t0'])
        if not (shortA and shortB): continue
        g = 0.3 * A['hh']
        for X, pos in ((A, A['t0'] - g - A['w'] / 2), (B, B['t1'] + g + B['w'] / 2)):
            if X['h'] in done: continue
            cx, cy = X['cen']
            at = [cx, pos] if X['vert'] else [pos, cy]
            ops.append({'t': 'dimtx', 'h': X['h'], 'at': at}); done.add(X['h'])
print('pairs ops', len(ops))
json.dump(ops, open(ab.S + r'\w\pairs.json', 'w'))
