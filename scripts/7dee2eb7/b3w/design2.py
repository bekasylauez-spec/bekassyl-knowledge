# Bar-by-bar dop design: every dop bar sits midway between base bars (@200 grid, +100), its run follows
# the required As along it; neighbouring bars with the same diameter and ends within ±TOL are grouped into one zone.
import json, math
import numpy as np
from scipy import ndimage
from shapely.geometry import LineString, Polygon
from design import SLABS, slab_geom, raster, required, as200, BASE, LA, STEP

DS = (10, 12, 14, 16, 18, 20)
TOL = 400          # ends of grouped bars may differ this much (zone takes the envelope)
GAP = 600          # runs closer than this along one bar are joined
MINRUN = 600       # shorter required runs are dropped (single cell)

def classes(D):
    cls = np.zeros(D.shape, int)
    for i, d in enumerate(DS):
        cls[D > (as200(DS[i - 1]) if i else 0.05)] = i + 1
    return cls

def design(k):
    xs, ys, A, inside = raster(k)
    g = slab_geom(k); gin = g.buffer(-30, join_style=2)
    out = []
    for f in range(4):
        R = required(A, f); D = np.where(inside, R - BASE, 0)
        cls = classes(D)
        # local peaks under ~1 m2 (4 LIRA cells) make no zone: drop them class by class
        for ci in range(len(DS), 0, -1):
            m = cls >= ci
            lab, n = ndimage.label(m, structure=np.ones((3, 3)))
            sizes = ndimage.sum(m, lab, range(1, n + 1))
            for c, s in enumerate(sizes, 1):
                if s < 100: cls[(lab == c) & (cls == ci)] = ci - 1
        alongx = f in (0, 1)
        lo, hi = (g.bounds[1], g.bounds[3]) if alongx else (g.bounds[0], g.bounds[2])
        coords = xs if alongx else ys
        bars = []      # (pos, a, b, d)
        for pos in np.arange(math.floor(lo / 200) * 200 + 100, hi, 200):
            # band of raster rows/cols covering this bar (±100)
            if alongx: idx = np.nonzero(np.abs(ys - pos) <= 100)[0]; prof = cls[idx, :].max(axis=0) if len(idx) else None
            else: idx = np.nonzero(np.abs(xs - pos) <= 100)[0]; prof = cls[:, idx].max(axis=1) if len(idx) else None
            if prof is None or not prof.any(): continue
            on = prof > 0
            # join short gaps
            runs = []; i = 0; n = len(on)
            while i < n:
                if on[i]:
                    j = i
                    while j + 1 < n and on[j + 1]: j += 1
                    runs.append([i, j]); i = j + 1
                else: i += 1
            merged = []
            for r in runs:
                if merged and (coords[r[0]] - coords[merged[-1][1]]) <= GAP: merged[-1][1] = r[1]
                else: merged.append(r)
            for a, b in merged:
                if coords[b] - coords[a] + STEP < MINRUN: continue
                d = DS[prof[a:b + 1].max() - 1]
                bars.append([float(pos), coords[a] - STEP / 2, coords[b] + STEP / 2, d])
        # group bars into zones
        bars.sort(key=lambda t: (t[3], t[1], t[0]))
        zones = []
        for pos, a, b, d in sorted(bars, key=lambda t: t[0]):
            for z in zones:
                if z['d'] == d and abs(z['pos'][-1] - pos) <= 200 + 1 and abs(z['a'] - a) <= TOL and abs(z['b'] - b) <= TOL:
                    z['pos'].append(pos); z['a'] = min(z['a'], a); z['b'] = max(z['b'], b); break
            else:
                zones.append(dict(f=f, d=d, pos=[pos], a=a, b=b))
        for z in zones:
            la = LA[z['d']]
            a, b = z['a'] - la, z['b'] + la
            # clip each bar to the slab interior; zone length = envelope of the clipped bars
            segs = []
            for pos in z['pos']:
                ln = LineString([(a, pos), (b, pos)]) if alongx else LineString([(pos, a), (pos, b)])
                c = ln.intersection(gin)
                if c.is_empty: continue
                parts = list(c.geoms) if hasattr(c, 'geoms') else [c]
                mid = (z['a'] + z['b']) / 2
                best = min(parts, key=lambda p: abs(((p.bounds[0] + p.bounds[2]) / 2 if alongx else (p.bounds[1] + p.bounds[3]) / 2) - mid))
                segs.append(best.bounds)
            if not segs: continue
            if alongx: z['L0'] = min(s[0] for s in segs); z['L1'] = max(s[2] for s in segs)
            else: z['L0'] = min(s[1] for s in segs); z['L1'] = max(s[3] for s in segs)
            z['L'] = int(math.ceil((z['L1'] - z['L0']) / 50.0) * 50)
            z['n'] = len(z['pos'])
            out.append(z)
    return out

if __name__ == '__main__':
    res = {}
    for k in SLABS:
        Z = design(k); res[k] = Z
        print(k, len(Z), 'bars', sum(z['n'] for z in Z))
        for z in sorted(Z, key=lambda z: (z['f'], -z['d'])):
            print('  f%d Ø%d n=%d L=%d pos %.0f..%.0f  along %.0f..%.0f' % (z['f'], z['d'], z['n'], z['L'], z['pos'][0], z['pos'][-1], z['L0'], z['L1']))
    json.dump(res, open('zones2.json', 'w'), indent=1)
