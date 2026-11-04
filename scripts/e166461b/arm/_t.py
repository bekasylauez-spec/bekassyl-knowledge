# Фм-1 поперечное армирование (analog 3.7): ASW (cm2/m2) from LIRA -> shear bars at the 200x200 mesh nodes,
# rectangles of one Ø (pos 25.. per Ø), no overlaps. Ø capacity at ш.200x200: As/0.04 m2.
import json, sys
import numpy as np
from scipy import ndimage
sys.path.insert(0, '.')
import model as M
c = json.load(open('arm/fm_cells.json')); asw = json.load(open('arm/fm_asw.json'))
CAP = [(12, 28.3), (14, 38.5), (16, 50.3), (18, 63.6), (20, 78.5), (22, 95.0)]
def cls(a):
    if a <= 0: return 0
    for d, cap in CAP:
        if a <= cap: return d
    return 25
FX0, FY0, FX1, FY1 = M.FM
xs = np.arange(FX0 + 50, FX1 - 49, 200.0); ys = np.arange(FY0 + 50, FY1 - 49, 200.0)
R = np.zeros((len(ys), len(xs)), int)
for x in c:
    d = cls(asw[str(x['id'])])
    if not d: continue
    i0 = np.searchsorted(xs, x['x0'] - 100); i1 = np.searchsorted(xs, x['x1'] + 100)
    j0 = np.searchsorted(ys, x['y0'] - 100); j1 = np.searchsorted(ys, x['y1'] + 100)
    R[j0:j1, i0:i1] = np.maximum(R[j0:j1, i0:i1], d)
need = R > 0
need = ndimage.binary_closing(need, np.ones((3, 3)))
need = ndimage.binary_fill_holes(need)
R = np.where(need, np.maximum(R, 12), 0)
rects = []
lab, nl = ndimage.label(need)
def split(i, j, i1, j1, m):
    sub = m[j:j1 + 1, i:i1 + 1]
    if not sub.any(): return
    jj, ii = np.nonzero(sub)
    i, j, i1, j1 = i + ii.min(), j + jj.min(), i + ii.max(), j + jj.max()
    sub = m[j:j1 + 1, i:i1 + 1]
    if sub.mean() >= 0.4 or (i1 - i < 5 and j1 - j < 5):
        rects.append([int(i), int(j), int(i1), int(j1)]); return
    # cut along the longer side at the emptiest line
    if (i1 - i) >= (j1 - j):
        prof = sub.sum(axis=0); k = int(np.argmin(prof[2:-2])) + 2 if len(prof) > 5 else len(prof) // 2
        split(i, j, i + k - 1, j1, m); split(i + k, j, i1, j1, m)
    else:
        prof = sub.sum(axis=1); k = int(np.argmin(prof[2:-2])) + 2 if len(prof) > 5 else len(prof) // 2
        split(i, j, i1, j + k - 1, m); split(i, j + k, i1, j1, m)
for q in range(1, nl + 1):
    mm = lab == q
    jj, ii = np.nonzero(mm)
    split(ii.min(), jj.min(), ii.max(), jj.max(), mm)
# split each rectangle along its long side into bands of one Ø (min 2 rows)
zones = []
for ri, (i, j, i1, j1) in enumerate(rects):
    sub = R[j:j1 + 1, i:i1 + 1]
    along_x = (i1 - i) >= (j1 - j)
    prof = sub.max(axis=0) if along_x else sub.max(axis=1)
    k = 0
    bands = []
    while k < len(prof):
        k1 = k
        while k1 + 1 < len(prof) and prof[k1 + 1] == prof[k]: k1 += 1
        bands.append([k, k1, int(prof[k])])
        k = k1 + 1
    # merge 1-row bands into the stronger neighbour
    ch = True
    while ch and len(bands) > 1:
        ch = False
        for q, b in enumerate(bands):
            if b[1] - b[0] < 14:
                nb = q - 1 if q > 0 and (q == len(bands) - 1 or bands[q - 1][2] >= bands[q + 1][2]) else q + 1
                lo, hi = sorted((q, nb))
                bands[lo] = [bands[lo][0], bands[hi][1], max(bands[lo][2], bands[hi][2])]
                del bands[hi]; ch = True; break
    for a, b, d in bands:
        if along_x: zi, zj, zi1, zj1 = i + a, j, i + b, j1
        else: zi, zj, zi1, zj1 = i, j + a, i1, j + b
        zones.append({'d': d, 'x0': float(xs[zi]), 'x1': float(xs[zi1]), 'y0': float(ys[zj]), 'y1': float(ys[zj1]),
                      'nx': zi1 - zi + 1, 'ny': zj1 - zj + 1, 'r': ri, 'along_x': bool(along_x)})
from collections import Counter
import collections
KG={12:0.888,14:1.208,16:1.578,18:1.998,20:2.466,22:2.984,25:3.853}
print(0.4,14,'kg',round(sum(z['nx']*z['ny']*KG[z['d']]*0.72 for z in zones)),len(rects), 'rects', len(zones), 'zones', Counter(z['d'] for z in zones), 'bars', sum(z['nx'] * z['ny'] for z in zones))
pass
POS = {d: str(56 + k) for k, d in enumerate(sorted(set(z['d'] for z in zones)))}
for z in zones: z['pos'] = POS[z['d']]
pass
pass
print(POS)
