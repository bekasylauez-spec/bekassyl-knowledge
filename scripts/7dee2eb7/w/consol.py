# Consolidate dop zones: neighbouring/overlapping zones of one face merge into one rectangle when the merge
# wastes little steel; the merged zone takes the larger diameter. Re-clips bars to the slab.
import json, math, sys
from shapely.geometry import box, LineString
from shapely.ops import unary_union
from design import SLABS, slab_geom, as200, LA

WASTE = 0.25
GAPM = 800

def rect(z):
    a, b = z['pos'][0] - 100, z['pos'][-1] + 100
    return box(z['L0'], a, z['L1'], b) if z['f'] in (0, 1) else box(a, z['L0'], b, z['L1'])

def steel(z): return rect(z).area * as200(z['d'])

def merge(p, q):
    u = rect(p).union(rect(q)).envelope
    x0, y0, x1, y1 = u.bounds
    if p['f'] in (0, 1): L0, L1, P0, P1 = x0, x1, y0, y1
    else: L0, L1, P0, P1 = y0, y1, x0, x1
    pos = [float(v) for v in range(int(P0 + 100), int(P1 - 100) + 1, 200)]
    return dict(f=p['f'], d=max(p['d'], q['d']), pos=pos, n=len(pos), L0=L0, L1=L1)

def run(Z, g):
    gin = g.buffer(-30, join_style=2)
    ch = True
    while ch:
        ch = False; best = None
        for i in range(len(Z)):
            for j in range(i + 1, len(Z)):
                p, q = Z[i], Z[j]
                if p['f'] != q['f'] or p['d'] != q['d']: continue
                rp, rq = rect(p), rect(q)
                if rp.distance(rq) > GAPM: continue
                m = merge(p, q); rm = rect(m).intersection(gin)
                extra = rm.area * as200(m['d']) - (steel(p) + steel(q) - rp.intersection(rq).area * min(as200(p['d']), as200(q['d'])))
                over = rp.intersection(rq).area > 1e4
                rel = extra / max(rm.area * as200(m['d']), 1)
                if (rel <= WASTE or (over and rel <= 0.4)) and (best is None or rel < best[0]): best = (rel, i, j, m)
        if best:
            _, i, j, m = best; Z.pop(j); Z[i] = m; ch = True
    # clip to the slab interior
    out = []
    for z in Z:
        alongx = z['f'] in (0, 1); segs = []
        for p in z['pos']:
            ln = LineString([(z['L0'], p), (z['L1'], p)]) if alongx else LineString([(p, z['L0']), (p, z['L1'])])
            c = ln.intersection(gin)
            if c.is_empty: continue
            parts = list(c.geoms) if hasattr(c, 'geoms') else [c]
            best = max(parts, key=lambda s: s.length)
            segs.append(best.bounds)
        if not segs: continue
        z['L0'] = min(s[0] if alongx else s[1] for s in segs); z['L1'] = max(s[2] if alongx else s[3] for s in segs)
        z['L'] = int(math.ceil((z['L1'] - z['L0']) / 50.0) * 50); z['n'] = len(z['pos'])
        out.append(z)
    return out

if __name__ == '__main__':
    Z = json.load(open('zones3.json')); res = {}
    for k in SLABS:
        res[k] = run(Z[k], slab_geom(k))
        print(k, len(res[k]), [sum(1 for z in res[k] if z['f'] == f) for f in range(4)], 'bars', sum(z['n'] for z in res[k]))
    json.dump(res, open('zones4.json', 'w'), indent=1)
