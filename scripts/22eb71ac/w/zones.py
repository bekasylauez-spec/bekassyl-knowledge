import sys, json, numpy as np
sys.path.insert(0, sys.argv[1])
from mos import analyse
class ndimage:
    @staticmethod
    def label(B):
        lab = np.zeros(B.shape, int); n = 0
        for j in range(B.shape[0]):
            for i in range(B.shape[1]):
                if B[j, i] and not lab[j, i]:
                    n += 1; st = [(j, i)]; lab[j, i] = n
                    while st:
                        a, b = st.pop()
                        for da, db in ((1,0),(-1,0),(0,1),(0,-1),(1,1),(1,-1),(-1,1),(-1,-1)):
                            c, d = a + da, b + db
                            if 0 <= c < B.shape[0] and 0 <= d < B.shape[1] and B[c, d] and not lab[c, d]:
                                lab[c, d] = n; st.append((c, d))
        return lab, n
# px -> KZh mm (piecewise by axes); LIRA px axes (same in all 4 plots of -3.700)
PX = {'x': [(332, 0), (686, 8250), (970, 14750)], 'y': [(967, 0), (789, 4100), (602, 8400), (424, 12500), (197, 17750)]}
def m(v, ax):
    pts = sorted(PX[ax], key=lambda t: t[0]) if ax == 'x' else sorted(PX[ax], key=lambda t: -t[0])
    for (p0, k0), (p1, k1) in zip(pts, pts[1:]):
        if (ax == 'x' and v <= p1) or (ax == 'y' and v >= p1): break
    return k0 + (v - p0) * (k1 - k0) / (p1 - p0)
BARS = [(12, 5.65), (14, 7.70), (16, 10.05), (18, 12.72), (20, 15.71), (22, 19.01), (25, 24.54), (28, 30.79)]
def bar_for(need):
    for d, a in BARS:
        if a >= need - 1e-6: return d, a
    return None
out = {}
for key, f, bins in [('top_x', 'scr01`2.png', '5.66,7.7,10.1'), ('bot_x', 'scr02`2.png', '5.66,7.7,10.1,12.7,15.7,19,24.5,30.8'),
                     ('top_y', 'scr03`2.png', '5.66,7.7,10.1'), ('bot_y', 'scr04.png', '5.66,7.7,10.1,12.7,15.7,19,24.5')]:
    cells, cx, cy = analyse(sys.argv[1] + '/../zip/' + f, [float(b) for b in bins.split(',')])
    nx, ny = len(cx) - 1, len(cy) - 1
    R = np.zeros((ny, nx))
    for c in cells: R[cy.index(c[1]), cx.index(c[0])] = c[4]
    res = []
    for lvl, lo, hi in [(1, 5.66 + 0.01, 1e9), (2, 5.65 + 5.65 + 0.01, 1e9)]:
        lab, n = ndimage.label(R > lo)
        for k in range(1, n + 1):
            jj, ii = np.where(lab == k)
            req = R[lab == k].max()
            x0 = m(cx[ii.min()], 'x'); x1 = m(cx[ii.max() + 1], 'x'); y1 = m(cy[jj.min()], 'y'); y0 = m(cy[jj.max() + 1], 'y')
            need = req - 5.65 if lvl == 1 else req - 5.65
            res.append(dict(lvl=lvl, x0=round(x0), y0=round(y0), x1=round(x1), y1=round(y1), req=req, ncell=int((lab == k).sum()), bar=bar_for(need)))
    out[key] = res
    print('==', key)
    for r in res: print('  ', r)
json.dump(out, open(sys.argv[1] + '/zones.json', 'w'), indent=1)
