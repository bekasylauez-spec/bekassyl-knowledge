# Rational dop zones: rectangles over the required-dop mask (fill >= FILL), then inside each rectangle
# bands across the bars by the required diameter. Bars of a band run the full rectangle length + anchorage.
import json, math
import numpy as np
from scipy import ndimage
from shapely.geometry import LineString
from design import SLABS, slab_geom, raster, required, as200, BASE, LA, STEP

DS = (10, 12, 14, 16, 18, 20)
FILL = 0.65

def classes(D):
    cls = np.zeros(D.shape, int)
    for i, d in enumerate(DS):
        cls[D > (as200(DS[i - 1]) if i else 0.05)] = i + 1
    return cls

def split(mask, x0, y0, x1, y1, out, depth=0):
    sub = mask[y0:y1, x0:x1]
    if not sub.any(): return
    yy, xx = np.nonzero(sub)
    x0, x1, y0, y1 = x0 + xx.min(), x0 + xx.max() + 1, y0 + yy.min(), y0 + yy.max() + 1
    sub = mask[y0:y1, x0:x1]; w, h = x1 - x0, y1 - y0
    if sub.mean() >= FILL or depth > 10 or (w <= 12 and h <= 12):
        out.append((x0, y0, x1, y1)); return
    best = None
    for axis, n in ((1, w), (0, h)):
        for c in range(6, n - 5):
            a, b = (sub[:, :c], sub[:, c:]) if axis == 1 else (sub[:c, :], sub[c:, :])
            if not a.any() or not b.any(): continue
            cost = 0
            for m in (a, b):
                q, p = np.nonzero(m); cost += (q.max() - q.min() + 1) * (p.max() - p.min() + 1)
            if best is None or cost < best[0]: best = (cost, axis, c)
    if best is None: out.append((x0, y0, x1, y1)); return
    _, axis, c = best
    if axis == 1: split(mask, x0, y0, x0 + c, y1, out, depth + 1); split(mask, x0 + c, y0, x1, y1, out, depth + 1)
    else: split(mask, x0, y0, x1, y0 + c, out, depth + 1); split(mask, x0, y0 + c, x1, y1, out, depth + 1)

def design(k):
    xs, ys, A, inside = raster(k)
    g = slab_geom(k); gin = g.buffer(-30, join_style=2)
    out = []
    for f in range(4):
        R = required(A, f); D = np.where(inside, R - BASE, 0)
        cls = classes(D)
        mask = cls > 0
        lab, n = ndimage.label(mask, structure=np.ones((3, 3)))
        sizes = ndimage.sum(mask, lab, range(1, n + 1))
        for c, s in enumerate(sizes, 1):
            if s < 100: mask[lab == c] = False; cls[lab == c] = 0     # < ~1 m2 = under 4 LIRA cells
        # a high class needs >= 1 m2 too, else it is treated one class lower
        for ci in range(len(DS), 1, -1):
            m = cls >= ci; lab, n = ndimage.label(m, structure=np.ones((3, 3)))
            sizes = ndimage.sum(m, lab, range(1, n + 1))
            for c, s in enumerate(sizes, 1):
                if s < 100: cls[(lab == c) & (cls == ci)] = ci - 1
        rects = []; split(mask, 0, 0, mask.shape[1], mask.shape[0], rects)
        alongx = f in (0, 1)
        for (a, b, c2, d2) in rects:
            X0, X1 = xs[a] - STEP / 2, xs[c2 - 1] + STEP / 2
            Y0, Y1 = ys[b] - STEP / 2, ys[d2 - 1] + STEP / 2
            P0, P1 = (Y0, Y1) if alongx else (X0, X1)          # across the bars
            L0, L1 = (X0, X1) if alongx else (Y0, Y1)          # along the bars
            poss = list(np.arange(math.floor(P0 / 200) * 200 + 100, P1 + 1, 200))
            poss = [p for p in poss if p >= P0 - 100 and p <= P1 + 100] or [math.floor((P0 + P1) / 400) * 200 + 100]
            bc = []
            for p in poss:
                if alongx: idx = np.nonzero(np.abs(ys - p) <= 100)[0]; v = cls[idx][:, a:c2]
                else: idx = np.nonzero(np.abs(xs - p) <= 100)[0]; v = cls[b:d2][:, idx]
                bc.append(int(v.max()) if v.size else 0)
            # strips with no requirement at the rectangle edges are dropped
            while bc and bc[0] == 0: bc.pop(0); poss.pop(0)
            while bc and bc[-1] == 0: bc.pop(); poss.pop()
            if not bc: continue
            bc = [max(v, 1) for v in bc]
            # bands of equal class; a band of 1-2 bars joins its stronger neighbour
            bands = []
            for p, v in zip(poss, bc):
                if bands and bands[-1]['c'] == v: bands[-1]['pos'].append(p)
                else: bands.append(dict(c=v, pos=[p]))
            changed = True
            while changed and len(bands) > 1:
                changed = False
                for i, bd in enumerate(bands):
                    if len(bd['pos']) <= 2:
                        nb = [j for j in (i - 1, i + 1) if 0 <= j < len(bands)]
                        j = max(nb, key=lambda j: bands[j]['c'])
                        bands[j]['c'] = max(bands[j]['c'], bd['c'])
                        bands[j]['pos'] = sorted(bands[j]['pos'] + bd['pos']); bands.pop(i); changed = True; break
                # neighbours with the same class merge
                i = 0
                while i < len(bands) - 1:
                    if bands[i]['c'] == bands[i + 1]['c']: bands[i]['pos'] += bands.pop(i + 1)['pos']; changed = True
                    else: i += 1
            for bd in bands:
                # along the bars: class profile over the band, runs of one class (>= 1500 mm, else joined to the stronger side)
                if alongx:
                    idx = [i for i in range(len(ys)) if any(abs(ys[i] - p) <= 100 for p in bd['pos'])]
                    prof = cls[idx][:, a:c2].max(axis=0); cc = xs[a:c2]
                else:
                    idx = [i for i in range(len(xs)) if any(abs(xs[i] - p) <= 100 for p in bd['pos'])]
                    prof = cls[b:d2][:, idx].max(axis=1); cc = ys[b:d2]
                prof = np.maximum(prof, 1); prof = np.minimum(prof, bd['c'])
                runs = []
                for v, cpos in zip(prof, cc):
                    if runs and runs[-1][0] == v: runs[-1][2] = cpos + STEP / 2
                    else: runs.append([int(v), cpos - STEP / 2, cpos + STEP / 2])
                ch = True
                while ch and len(runs) > 1:
                    ch = False
                    for i, r in enumerate(runs):
                        if r[2] - r[1] < 1500:
                            nb = [j for j in (i - 1, i + 1) if 0 <= j < len(runs)]
                            j = max(nb, key=lambda j: runs[j][0])
                            runs[j][0] = max(runs[j][0], r[0]); runs[j][1] = min(runs[j][1], r[1]); runs[j][2] = max(runs[j][2], r[2])
                            runs.pop(i); ch = True; break
                    i = 0
                    while i < len(runs) - 1:
                        if runs[i][0] == runs[i + 1][0]: runs[i][2] = runs.pop(i + 1)[2]; ch = True
                        else: i += 1
                for cv, r0, r1 in runs:
                    d = DS[cv - 1]; la = LA[d]
                    segs = []
                    for p in bd['pos']:
                        ln = LineString([(r0 - la, p), (r1 + la, p)]) if alongx else LineString([(p, r0 - la), (p, r1 + la)])
                        cl = ln.intersection(gin)
                        if cl.is_empty: continue
                        parts = list(cl.geoms) if hasattr(cl, 'geoms') else [cl]
                        mid = (r0 + r1) / 2
                        best = min(parts, key=lambda q: abs(((q.bounds[0] + q.bounds[2]) if alongx else (q.bounds[1] + q.bounds[3])) / 2 - mid))
                        segs.append(best.bounds)
                    if not segs: continue
                    l0 = min(s[0] if alongx else s[1] for s in segs); l1 = max(s[2] if alongx else s[3] for s in segs)
                    out.append(dict(f=f, d=d, pos=[float(p) for p in bd['pos']], n=len(bd['pos']), L0=l0, L1=l1, r0=r0, r1=r1,
                                    L=int(math.ceil((l1 - l0) / 50.0) * 50)))
    # colinear zones of one face and diameter whose bars coincide and runs touch become one zone
    ch = True
    while ch:
        ch = False
        for i in range(len(out)):
            for j in range(i + 1, len(out)):
                p, q = out[i], out[j]
                if p['f'] != q['f'] or p['d'] != q['d']: continue
                if abs(p['pos'][0] - q['pos'][0]) > 400 or abs(p['pos'][-1] - q['pos'][-1]) > 400: continue
                if p['L0'] > q['L1'] + 200 or q['L0'] > p['L1'] + 200: continue
                ps = sorted(set(p['pos']) | set(q['pos']))
                ps = [float(v) for v in np.arange(ps[0], ps[-1] + 1, 200)]
                p.update(pos=ps, n=len(ps), L0=min(p['L0'], q['L0']), L1=max(p['L1'], q['L1']), r0=min(p['r0'], q['r0']), r1=max(p['r1'], q['r1']))
                p['L'] = int(math.ceil((p['L1'] - p['L0']) / 50.0) * 50)
                out.pop(j); ch = True; break
            if ch: break
    return out

if __name__ == '__main__':
    res = {}
    for k in SLABS:
        Z = design(k); res[k] = Z
        print(k, len(Z), 'bars', sum(z['n'] for z in Z), 'per face', [sum(1 for z in Z if z['f'] == f) for f in range(4)])
        for z in sorted(Z, key=lambda z: (z['f'], -z['d'])):
            print('  f%d Ø%d n=%d L=%d pos %.0f..%.0f  along %.0f..%.0f' % (z['f'], z['d'], z['n'], z['L'], z['pos'][0], z['pos'][-1], z['L0'], z['L1']))
    json.dump(res, open('zones3.json', 'w'), indent=1)
