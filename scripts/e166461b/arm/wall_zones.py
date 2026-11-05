# Edge zones ш.100 at piece ends, middle base Ø12@200 (or more by calc), horizontal Ø10@200 base.
import json, math, sys
C = json.load(open('arm/wall_cells.json'))
LEV = [-4.65, -0.1, 3.95, 7.1, 10.25, 13.4, 16.55, 19.7]
A = lambda d: math.pi * d * d / 400
DS = [12, 14, 16, 18, 20, 22, 25, 28, 32]
def edge_d(req):                       # bars @100
    for d in DS:
        if A(d) * 10 >= req - 1e-6: return d
def mid_pick(req):
    for d, s in ((12, 200), (14, 200), (16, 200), (12, 100), (14, 100), (16, 100), (18, 100), (20, 100)):
        if A(d) * 1000 / s >= req - 1e-6: return (d, s)
def hor_pick(req):
    for d, s in ((10, 200), (12, 200), (10, 100), (12, 100), (14, 100), (16, 100)):
        if A(d) * 1000 / s >= req - 1e-6: return (d, s)
BASE = A(12) * 1000 / 200
def smooth(ds):
    """Ø of neighbouring storeys differ by <= 4 mm: raise the smaller ones (None = no zone counts as 12)"""
    ds = list(ds); ch = True
    while ch:
        ch = False
        for i in range(len(ds)):
            for j in (i - 1, i + 1):
                if 0 <= j < len(ds) and ds[j] and ds[i]:
                    while ds[j] - ds[i] > 4:
                        ds[i] = DS[DS.index(ds[i]) + 1]; ch = True
                elif 0 <= j < len(ds) and ds[j] and not ds[i] and ds[j] > 16:
                    ds[i] = DS[DS.index(ds[j]) - 2] if ds[j] - 4 > 12 else 12; ch = True
    return ds
def design(ax, val, pieces, ends):
    """pieces [(a,b)], ends [(edge_left?, edge_right?)] -> per piece: dict(L=[Ø per storey], M=[(Ø,s)], R=[...], H=[(Ø,s)])"""
    sel = [c for c in C if tuple(c['pl']) == (ax, val)]
    k0, k1 = ('x0', 'x1') if ax == 'y' else ('y0', 'y1')
    res = []
    for (a, b), (el, er) in zip(pieces, ends):
        L, M, Rr, H = [], [], [], []
        for s in range(len(LEV) - 1):
            cs = [c for c in sel if LEV[s] - 1e-3 <= c['z0'] < LEV[s + 1] - 1e-3 and c[k1] > a + 1 and c[k0] < b - 1]
            v = lambda c: max(c['As'][2], c['As'][3])
            colx = sorted(set(round(c[k0]) for c in cs))
            col = lambda x: [c for c in cs if round(c[k0]) == x]
            lv = max(v(c) for c in col(colx[0])) if el else None
            rv = max(v(c) for c in col(colx[-1])) if er else None
            midc = [c for c in cs if (not el or round(c[k0]) != colx[0]) and (not er or round(c[k0]) != colx[-1])]
            L.append(edge_d(lv) if lv is not None and lv > BASE else None)
            Rr.append(edge_d(rv) if rv is not None and rv > BASE else None)
            M.append(mid_pick(max([v(c) for c in midc] + [0])))
            H.append(hor_pick(max(max(c['As'][0], c['As'][1]) for c in cs)))
        res.append(dict(a=a, b=b, L=smooth(L), R=smooth(Rr), M=M, H=H))
    return res
if __name__ == '__main__':
    P = [(0, 1225), (5875, 7725), (12325, 14175), (18825, 20050)]
    E = [(False, True), (True, True), (True, True), (True, False)]
    for i, p in enumerate(design('y', 0, P, E)):
        print('piece', i + 1, p['a'], p['b'])
        for s in range(len(LEV) - 1):
            print('  %6.2f  L %s  M %s  R %s  H %s' % (LEV[s], p['L'][s], p['M'][s], p['R'][s], p['H'][s]))
