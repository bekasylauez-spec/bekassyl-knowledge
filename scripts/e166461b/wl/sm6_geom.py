# См-6 (axis В, scheme: only corner piers 125..1225 and 18825..19925, all storeys) from analog См-5 (4.16 / 4.17):
# drop the piers at 2, 2/1, 3 and the basement walls between the axes, stretch the corner piers 1075 -> 1100,
# opening diagonals stretched to the new pier faces; basement openings get the same diagonals; axis 2/1 dropped (См-9 wall stays, 250).
import sys; sys.path.insert(0, 'wl'); from common import *
SY = 455939.0
def xmove(r, X, mp, tol=3, ylo=-1e9, yhi=1e9):
    it = []
    for i, (x, y) in enumerate(r['sp']):
        for a, b in mp:
            if abs(x - a) < tol and ylo <= y <= yhi: it.append([i, X + b, SY + y]); break
    return dict(t='spmove', h=r['h'], items=it) if it else None
def elevation(X, A1, YB, YT, dims_y):
    """A1: axis 1 x on the sheet; YB/YT: basement bottom/top (slab); elevation analog layout (rel. to axis 1)"""
    R = listwin(X, SY, 59400, 42000, None)
    P1R, P2L, P2R, P4L = A1 + 1200, A1 + 5900, A1 + 6675, A1 + 18850
    N1R, N4L = A1 + 1225, A1 + 18825
    ops = []; er = []
    rect = lambda r: r['t'] == 'LWPOLYLINE' and len(r['sp']) == 4 and r['y0'] > YB - 5 and r['y1'] - r['y0'] > 1000
    for r in R:
        if r['y1'] > 40500 or r['y0'] < YB - 5 or r['x1'] > A1 + 20500: continue
        x0, x1 = r['x0'], r['x1']
        if rect(r) and abs(x0 - P2L) < 3 and abs(x1 - P2R) < 3: er.append(r['h'])                      # pier at 2
        elif rect(r) and r['y0'] < YT - 5 and abs(x0 - (A1 + 6925)) < 3: er.append(r['h'])                 # basement walls 2-2/1, 2/1-3
        elif rect(r) and r['y0'] < YT - 5 and abs(x0 - (A1 + 10525)) < 3: er.append(r['h'])
        elif rect(r) and abs(x0 - (A1 + 125)) < 3: o = xmove(r, X, [(P1R, N1R), (P2R, N1R)]); ops += [o] if o else []
        elif rect(r) and abs(x1 - (A1 + 19925)) < 3: o = xmove(r, X, [(P4L, N4L), (A1 + 13375, N4L)]); ops += [o] if o else []
        elif r['t'] == 'LWPOLYLINE' and len(r['sp']) == 3 and abs(r['sp'][0][0] - P1R) < 3:         # opening 1 diagonal
            ops.append(dict(t='spmove', h=r['h'], items=[[0, X + N1R, SY + r['sp'][0][1]], [1, X + r['sp'][1][0] + 25, SY + r['sp'][1][1]], [2, X + P2R, SY + r['sp'][2][1]]]))
        elif r['t'] == 'LWPOLYLINE' and len(r['sp']) == 3 and abs(r['sp'][2][0] - P4L) < 3:
            ops.append(dict(t='spmove', h=r['h'], items=[[2, X + N4L, SY + r['sp'][2][1]]]))
    return R, ops, er
