# Vault rules (02_Фундамент/Фундаментная плита.md): base Ø by thickness (400 -> Ø14 @200 = 7.70 cm2/m),
# As_avg of the cell and its neighbour PERPENDICULAR to the bar direction, zone only if >= 4 cells,
# dop Ø10..32 @200 between base bars (same level), zones rationalised to rectangles.
import sys, json, numpy as np
sys.path.insert(0, sys.argv[1])
from mos import analyse
from zones import m, ndimage        # piecewise px->KZh map and labelling from zones.py
BASE = 7.70
DOP = [(10, 3.93), (12, 5.65), (14, 7.70), (16, 10.05), (18, 12.72), (20, 15.71), (22, 19.01), (25, 24.54), (28, 30.79), (32, 40.21)]
def dop_for(deficit):
    for d, a in DOP:
        if a >= deficit - 1e-6: return d
out = {}
for key, f, bins, dr in [('bot_x', 'scr02`2.png', '5.66,7.7,10.1,12.7,15.7,19,24.5,30.8', 'x'), ('bot_y', 'scr04.png', '5.66,7.7,10.1,12.7,15.7,19,24.5', 'y'),
                         ('top_x', 'scr01`2.png', '5.66,7.7,10.1', 'x'), ('top_y', 'scr03`2.png', '5.66,7.7,10.1', 'y')]:
    cells, cx, cy = analyse(sys.argv[1] + '/../zip/' + f, [float(b) for b in bins.split(',')])
    nx, ny = len(cx) - 1, len(cy) - 1
    R = np.zeros((ny, nx))
    for c in cells: R[cy.index(c[1]), cx.index(c[0])] = c[4]
    A = np.zeros_like(R)                      # As_avg with the neighbour perpendicular to the bars
    for j in range(ny):
        for i in range(nx):
            if dr == 'x': nb = [R[j2, i] for j2 in (j - 1, j + 1) if 0 <= j2 < ny]   # bars along X -> neighbours along Y
            else: nb = [R[j, i2] for i2 in (i - 1, i + 1) if 0 <= i2 < nx]
            A[j, i] = max((R[j, i] + v) / 2 for v in nb)
    lab, n = ndimage.label(A > BASE + 0.01)
    res = []
    for k in range(1, n + 1):
        jj, ii = np.where(lab == k)
        if len(jj) < 4: continue                # single local peak is not a zone
        defi = A[lab == k].max() - BASE
        x0 = m(cx[ii.min()], 'x'); x1 = m(cx[ii.max() + 1], 'x'); y1 = m(cy[jj.min()], 'y'); y0 = m(cy[jj.max() + 1], 'y')
        r = lambda v, f: int(f(v / 100.0) * 100)
        import math
        res.append(dict(x0=r(x0, math.floor), y0=r(y0, math.floor), x1=r(x1, math.ceil), y1=r(y1, math.ceil),
                        asmax=round(float(A[lab == k].max()), 2), cells=int(len(jj)), d=dop_for(defi)))
    area = sum((z['x1'] - z['x0']) * (z['y1'] - z['y0']) for z in res) / (16000 * 19000)
    out[key] = dict(zones=res, area_share=round(area, 3))
    print('==', key, 'zones', len(res), 'area share', round(area, 3))
    for z in res: print('  ', z)
json.dump(out, open(sys.argv[1] + '/zones2.json', 'w'), indent=1)
