# Dop reinforcement zones from LIRA As (cm2/m) for the two Block 4 slabs.
# Local coords: mm, x from axis 32, y from axis А (LIRA x - 174.15 m).
import json, math, sys
import numpy as np
from shapely.geometry import Polygon, Point, box
from shapely.strtree import STRtree
from shapely.prepared import prep
from scipy import ndimage
from cells import cells

BASE_D = 10
AREA = {8: 0.503, 10: 0.785, 12: 1.131, 14: 1.539, 16: 2.011, 18: 2.545, 20: 3.142}
def as200(d): return AREA[d] * 5        # cm2/m at @200
BASE = as200(BASE_D)                      # 3.93
LA = {10: 400, 12: 500, 14: 600, 16: 650, 18: 750, 20: 800}   # anchorage past the zone, mm
STEP = 100

SLABS = {
    'P45': dict(z=4.5, poly=Polygon([(12300, -250), (25200, -250), (25200, 9950), (12300, 9950)]), holes=[]),
    'P70': dict(z=7.0, poly=Polygon([(415, 39300), (12950, 39300), (12950, 36250), (45100, 36250), (45100, -250), (415, -250),
                                      (415, 16400), (31550, 16400), (31550, 25500), (415, 25500)]),
                holes=[[(39950, 17050), (44550, 17050), (44550, 25950), (39950, 25950)],
                       [(26725, 1700), (29275, 1700), (29275, 7300), (26725, 7300)]]),
}

def slab_geom(k):
    s = SLABS[k]; g = s['poly']
    for h in s['holes']: g = g.difference(Polygon(h))
    return g

def pick_d(deficit):
    for d in (10, 12, 14, 16, 18, 20):
        if as200(d) >= deficit - 1e-6: return d
    return 20

def raster(k):
    s = SLABS[k]; g = slab_geom(k); C = cells(s['z'])
    polys = [Polygon(c['poly']) for c in C]
    tree = STRtree(polys)
    x0, y0, x1, y1 = g.bounds
    xs = np.arange(math.floor(x0 / STEP) * STEP + STEP / 2, x1, STEP)
    ys = np.arange(math.floor(y0 / STEP) * STEP + STEP / 2, y1, STEP)
    A = np.full((4, len(ys), len(xs)), np.nan)
    inside = np.zeros((len(ys), len(xs)), bool)
    pg = prep(g)
    for j, y in enumerate(ys):
        for i, x in enumerate(xs):
            p = Point(x, y)
            if not pg.contains(p): continue
            inside[j, i] = True
            for idx in tree.query(p):
                if polys[idx].covers(p):
                    A[:, j, i] = C[idx]['As']; break
    # slab points not covered by a LIRA plate (slab over beam/column faces beyond the mesh): nearest value
    miss = inside & np.isnan(A[0])
    if miss.any():
        for f in range(4):
            a = A[f].copy(); ok = ~np.isnan(a)
            idx = ndimage.distance_transform_edt(~ok, return_distances=False, return_indices=True)
            A[f][miss] = a[tuple(idx)][miss]
    return xs, ys, A, inside

def required(A, f):
    # As_avg of two neighbouring cells perpendicular to the bars (X bars: f 0,1 -> neighbours in y)
    a = A[f]; sh = 5      # 500 mm ~ one LIRA cell
    ax = 0 if f in (0, 1) else 1
    def shift(v, s):
        r = np.roll(v, s, axis=ax)
        if s > 0:
            if ax == 0: r[:s, :] = np.nan
            else: r[:, :s] = np.nan
        else:
            if ax == 0: r[s:, :] = np.nan
            else: r[:, s:] = np.nan
        return r
    p1 = np.nanmean(np.stack([a, shift(a, sh)]), axis=0)
    p2 = np.nanmean(np.stack([a, shift(a, -sh)]), axis=0)
    return np.fmax(p1, p2)

def split_rects(mask, x0i, y0i, x1i, y1i, out, depth=0):
    sub = mask[y0i:y1i, x0i:x1i]
    if not sub.any(): return
    ys, xs = np.nonzero(sub)
    x0i, x1i = x0i + xs.min(), x0i + xs.max() + 1
    y0i, y1i = y0i + ys.min(), y0i + ys.max() + 1
    sub = mask[y0i:y1i, x0i:x1i]
    fill = sub.mean()
    w, h = x1i - x0i, y1i - y0i
    if fill >= 0.6 or (w <= 15 and h <= 15) or depth > 8:
        out.append((x0i, y0i, x1i, y1i)); return
    best = None
    for axis, n in ((1, w), (0, h)):
        for c in range(4, n - 3):
            if axis == 1: a, b = sub[:, :c], sub[:, c:]
            else: a, b = sub[:c, :], sub[c:, :]
            if not a.any() or not b.any(): continue
            def bb(m):
                yy, xx = np.nonzero(m); return (yy.max() - yy.min() + 1) * (xx.max() - xx.min() + 1)
            cost = bb(a) + bb(b)
            if best is None or cost < best[0]: best = (cost, axis, c)
    if best is None or best[0] > 0.92 * w * h:
        out.append((x0i, y0i, x1i, y1i)); return
    _, axis, c = best
    if axis == 1:
        split_rects(mask, x0i, y0i, x0i + c, y1i, out, depth + 1); split_rects(mask, x0i + c, y0i, x1i, y1i, out, depth + 1)
    else:
        split_rects(mask, x0i, y0i, x1i, y0i + c, out, depth + 1); split_rects(mask, x0i, y0i + c, x1i, y1i, out, depth + 1)

def zones(k):
    xs, ys, A, inside = raster(k)
    g = slab_geom(k)
    res = []
    DS = (10, 12, 14, 16, 18, 20)
    for f in range(4):
        R = required(A, f)
        D = np.where(inside, R - BASE, 0)
        cls = np.zeros(D.shape, int)
        for i, d in enumerate(DS):
            cls[D > (as200(DS[i - 1]) if i else 0.05)] = i + 1
        covered = np.zeros(D.shape, bool)
        Z = []
        # strongest class first; a weaker zone fills what is left around it (its bars sit beside, or lap colinear)
        for ci in range(len(DS), 0, -1):
            mask = (cls >= ci) & ~covered
            lab, n = ndimage.label(mask, structure=np.ones((3, 3)))
            for c in range(1, n + 1):
                m = lab == c
                if m.sum() < 100: mask[m] = False      # under ~1 m2 (4 LIRA cells): local peak, no zone of this class
            rects = []
            split_rects(mask, 0, 0, mask.shape[1], mask.shape[0], rects)
            for (a, b, c2, d2) in rects:
                covered[b:d2, a:c2] = True
                Z.append(dict(x0=xs[a] - STEP / 2, y0=ys[b] - STEP / 2, x1=xs[c2 - 1] + STEP / 2, y1=ys[d2 - 1] + STEP / 2,
                              defi=as200(DS[ci - 1]), d=DS[ci - 1],
                              asmax=float(np.nanmax(np.where(mask[b:d2, a:c2], R[b:d2, a:c2], np.nan)))))
        for z in Z:
            d = z['d']; z['f'] = f
            bx = ext(z, f)
            # bars: along x for f 0,1; spacing 200 across, centred between base bars
            r = box(*bx).intersection(g.buffer(-30, join_style=2))
            if r.is_empty: continue
            z['rect'] = [round(v) for v in r.bounds]
            res.append(z)
    return res

def ext(z, f):
    d = pick_d(z['defi']); la = LA[d]
    if f in (0, 1): return (z['x0'] - la, z['y0'], z['x1'] + la, z['y1'])
    return (z['x0'], z['y0'] - la, z['x1'], z['y1'] + la)

if __name__ == '__main__':
    out = {}
    for k in SLABS:
        Z = zones(k); out[k] = Z
        print(k, len(Z))
        for z in Z: print('  f%d d%d asmax=%.2f rect=%s' % (z['f'], z['d'], z['asmax'], z['rect']))
    json.dump(out, open('zones.json', 'w'), indent=1)
