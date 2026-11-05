"""Лист 1.3 «Схема расположения котлована и раскатных свай» — Помещение обезвоживания.
Analog objects of ABK sheet 1.3 are kept as templates; their points are remapped piecewise-linearly
from the ABK grid (11 axes x 6000, A-B 12000, pit offset 2100) to the new grid."""
import json, sys, os, bisect
import ab, geo_ob
from shapely.geometry import Polygon

X1, YA = -1672229.0, -1732948.0          # new axis 1 / axis A on the sheet
AX = [X1 + v for v in geo_ob.AX]
AY = [YA + v for v in geo_ob.AY]
XI0, XI1 = X1 - 2100, X1 + 32000 + 2100  # pit bottom (inner) edge
YI0, YI1 = YA - 2600, YA + 12000 + 2600
SL = 650                                # slope projection
XO0, XO1, YO0, YO1 = XI0 - SL, XI1 + SL, YI0 - SL, YI1 + SL

KX = [(-1690412, XO0), (-1689329, XI0), (-1687229, X1), (-1627229, X1 + 32000), (-1625129, XI1), (-1623944, XO1)]
KY = [(-1736160, YO0), (-1735048, YI0), (-1732948, YA), (-1726948, YA + 6000), (-1720948, YA + 12000), (-1718848, YI1), (-1717693, YO1)]
SNAPX = [XO0, XI0, XI1, XO1] + AX
SNAPY = [YO0, YI0, YI1, YO1] + AY


def pw(v, K, snap):
    a = [k[0] for k in K]
    if v <= a[0]:
        r = v - a[0] + K[0][1]
    elif v >= a[-1]:
        r = v - a[-1] + K[-1][1]
    else:
        i = bisect.bisect_right(a, v) - 1
        (a0, b0), (a1, b1) = K[i], K[i + 1]
        r = b0 + (v - a0) * (b1 - b0) / (a1 - a0)
    for s in snap:
        if abs(r - s) < 90:
            return s
    return r


def M(p):
    return [round(pw(p[0], KX, SNAPX), 1), round(pw(p[1], KY, SNAPY), 1)]


def dimop(h, p1, p2, dl, tx, dl_a, tx_a, horiz=None):
    """remap a rotated dim; keep the analog text offset from the dim line"""
    q1, q2, qd = M(p1), M(p2), M(dl)
    if horiz is None:
        horiz = abs(abs(tx_a[1] - dl_a[1]) - 188) < 40
    if horiz:
        t = [(q1[0] + q2[0]) / 2, qd[1] + (tx_a[1] - dl_a[1])]
    else:
        t = [qd[0] + (tx_a[0] - dl_a[0]), (q1[1] + q2[1]) / 2]
    return {'t': 'dimset2', 'h': h, 'p1': q1, 'p2': q2, 'dl': qd, 'tx': t}


O = []
WIN = [-1701303, -1749172, -1612203, -1707172]

# --- foundation contour + подготовка (clone analog rings, then set points)
F = geo_ob.found()
P = F.buffer(100, join_style=2)
k = 0
for src, geom in (('3C3702', F), ('3C3717', P)):
    polys = geom.geoms if hasattr(geom, 'geoms') else [geom]
    for poly in polys:
        for ring in [poly.exterior] + list(poly.interiors):
            pts = [[round(X1 + x, 1), round(YA + y, 1)] for x, y in list(ring.coords)[:-1]]
            tag = 'f13_%d' % k; k += 1
            O.append({'t': 'clone', 'h': src, 'tag': tag})
            O.append({'t': 'plset', 'h': tag, 'p': pts, 'closed': True})

# --- erase analog piles, contours, surplus axes and chain dims
E = ab_erase = []
O.insert(0, {'t': 'noop'})

# --- axes: 8 vertical, 3 horizontal
VAX = ['37BAF2', '37BAF3', '37BAF4', '37BAF5', '37BAF6', '37BAF7', '37BAF8', '37BAF9']
for i, h in enumerate(VAX):
    O.append({'t': 'axis', 'h': h, 's': [AX[i], M((0, -1720948))[1]], 'e': [AX[i], M((0, -1738516))[1]], 'val': str(i + 1)})
for h, y in (('37BCC2', -1732948), ('37BCCC', -1726948), ('37BD18', -1720948)):
    O.append({'t': 'axis', 'h': h, 's': [AX[-1], M((0, y))[1]], 'e': [M((-1693278, 0))[0], M((0, y))[1]]})

# --- axis chain (bottom) 7 of 10 analog dims, overall 32000
CH = ['37BB1D', '37BB47', '37BB71', '37BB9B', '37BBC5', '37BBEF', '37BC19']
yl = M((0, -1738516))[1]; yd = M((0, -1737913))[1]
for i, h in enumerate(CH):
    O.append({'t': 'dimset2', 'h': h, 'p1': [AX[i], yl], 'p2': [AX[i + 1], yl], 'dl': [AX[i], yd], 'tx': [(AX[i] + AX[i + 1]) / 2, yd + 187]})
yd2 = M((0, -1738613))[1]
O.append({'t': 'dimset2', 'h': '37BAFC', 'p1': [AX[0], yl], 'p2': [AX[-1], yl], 'dl': [AX[0], yd2], 'tx': [(AX[0] + AX[-1]) / 2, yd2 + 187]})

# --- left axis dims (A-Б, Б-В, A-В): same as analog, remapped
O.append(dimop('37BCEE', (-1693278, -1732948), (-1693278, -1726948), (-1692078, -1732948), None, (-1692078, -1732948), (-1692266, -1729948), False))
O.append(dimop('37BD22', (-1693278, -1726948), (-1693278, -1720948), (-1692078, -1726948), None, (-1692078, -1726948), (-1692266, -1723948), False))
O.append(dimop('37BCCD', (-1693278, -1732948), (-1693278, -1720948), (-1692778, -1732948), None, (-1692778, -1732948), (-1692966, -1726027), False))

# --- pit dims (0_ANNOT_Dimensions): p1, p2, dl, tx from the analog list
PD = {
    '37D2EC': ((-1625129, -1718848), (-1623909, -1717628), (-1625129, -1717026), (-1624519, -1716838)),
    '37D30D': ((-1625129, -1735048), (-1623979, -1736198), (-1625129, -1737913), (-1624554, -1737726)),
    '37D33E': ((-1689329, -1718848), (-1690419, -1717758), (-1689329, -1717026), (-1689874, -1716838)),
    '37D366': ((-1689329, -1735048), (-1690404, -1736123), (-1692078, -1735048), (-1692267, -1735585)),
    '37D38E': ((-1689329, -1735048), (-1690404, -1736123), (-1689329, -1737913), (-1689866, -1737724)),
    '37D3B6': ((-1625129, -1735048), (-1623979, -1736198), (-1622579, -1735048), (-1622766, -1735623)),
    '37D3DE': ((-1689329, -1735048), (-1687229, -1735048), (-1689329, -1737913), (-1688279, -1737726)),
    '37D406': ((-1625129, -1735048), (-1627229, -1735048), (-1625129, -1737913), (-1626179, -1737726)),
    '37D42E': ((-1689329, -1735048), (-1689329, -1732948), (-1692078, -1735048), (-1692266, -1733998)),
    '37D456': ((-1689329, -1720948), (-1689329, -1718848), (-1692078, -1720948), (-1692266, -1719898)),
    '37D47E': ((-1689329, -1718848), (-1690419, -1717758), (-1692078, -1718848), (-1692266, -1718303)),
    '37D4A6': ((-1689329, -1718848), (-1625129, -1718848), (-1689329, -1717026), (-1657229, -1716838)),
    '37D4CE': ((-1625129, -1718848), (-1623909, -1717628), (-1622579, -1718848), (-1622766, -1718238)),
    '37D4EF': ((-1625129, -1718848), (-1625129, -1735048), (-1622579, -1718848), (-1622766, -1726948)),
}
for h, (p1, p2, dl, tx) in PD.items():
    O.append(dimop(h, p1, p2, dl, tx, dl, tx))

# --- pit outlines, corner lines, slope hatches
O.append({'t': 'plset', 'h': '37BD43', 'p': [[XI0, YI0], [XI0, YI1], [XI1, YI1], [XI1, YI0]], 'closed': True})
O.append({'t': 'plset', 'h': '37BD4D', 'p': [M(p) for p in [(-1690419, -1717758), (-1623909, -1717628), (-1623979, -1736198), (-1690404, -1736123)]], 'closed': True})
for h, a, b in (('37BD52', (-1625129, -1718848), (-1623909, -1717628)), ('37BD53', (-1690404, -1736123), (-1689329, -1735048)),
                ('37BD54', (-1623979, -1736198), (-1625129, -1735048)), ('37BD55', (-1689329, -1718848), (-1690419, -1717758))):
    O.append({'t': 'lnset', 'h': h, 'p1': M(a), 'p2': M(b)})
HL = {
    '37D520': [(-1690404, -1736123), (-1689866, -1735585), (-1689874, -1718303), (-1690419, -1717758)],
    '37D521': [(-1689866, -1735585), (-1689329, -1735048), (-1689329, -1718848), (-1689874, -1718303)],
    '37D522': [(-1690419, -1717758), (-1623909, -1717628), (-1624519, -1718238), (-1689874, -1718303)],
    '37D523': [(-1689874, -1718303), (-1624519, -1718238), (-1625129, -1718848), (-1689329, -1718848)],
    '37D524': [(-1690404, -1736123), (-1623979, -1736198), (-1624554, -1735623), (-1689866, -1735585)],
    '37D525': [(-1689866, -1735585), (-1624554, -1735623), (-1625129, -1735048), (-1689329, -1735048)],
    '37D526': [(-1623979, -1736198), (-1624554, -1735623), (-1624519, -1718238), (-1623909, -1717628)],
    '37D527': [(-1624554, -1735623), (-1625129, -1735048), (-1625129, -1718848), (-1624519, -1718238)],
}
for h, L in HL.items():
    O.append({'t': 'hatchset', 'h': h, 'loops': [[M(p) for p in L]]})

# --- corner level notes: numerator = ground, denominator = pit bottom
for h, tgt in (('37BD4E', (-1690419, -1717810)), ('37BD4F', (-1623909, -1717628)), ('37BD50', (-1690404, -1736123)), ('37BD51', (-1623979, -1736198))):
    q = M(tgt)
    O.append({'t': 'moveto', 'h': h, 'idx': 1, 'to': q})
    O.append({'t': 'mcset', 'h': h, 'set': {'FirstLine': '-0.300', 'SecondLine': '-1.600'}})

# --- piles
Fp, Sp = geo_ob.piles()
for x, y in Fp + Sp:
    O.append({'t': 'circle', 'c': [X1 + x, YA + y], 'r': 250, 'layer': 'BASE-DJ'})
# pile notes: pad pile (axis 6/A, upper right corner of the pad) and a slab pile (bay 6-7, A-Б)
for h, c in (('3D13FB', (20000 + 1000, 1500)), ('3D13FC', (24000, 4000))):
    O.append({'t': 'moveto', 'h': h, 'idx': 1, 'to': [X1 + c[0] + 177, YA + c[1] + 177]})

# --- title and note
O.append({'t': 'moveto', 'h': '37D528', 'idx': 0, 'to': [M((-1687233, 0))[0], M((0, -1715603))[1]]})
NOTE = ('Раскатные сваи Св1 ∅500, L=11000 (бетон C16/20) - под фундаментами с шагом 1000х1000, под плитой по '
        'грунту с шагом 2000х2000 (%d + %d = %d шт.). Под фундаментами - подушка из уплотненного суглинка толщ. 1000 мм (К=0,95). '
        'На углах котлована: в числителе - отметка поверхности земли, в знаменателе - отметка дна котлована.') % (len(Fp), len(Sp), len(Fp) + len(Sp))
O.append({'t': 'settext', 'h': '3D13FD', 's': NOTE})
O.append({'t': 'moveto', 'h': '3D13FD', 'idx': 0, 'to': [M((-1684229, 0))[0], M((0, -1741948))[1]]})

# --- erase old piles / contours / surplus axes and dims (last: templates were cloned above)
import dx
old = [e['h'] for e in dx.win(*WIN) if (e['t'] == 'CIRCLE' and e['lay'] == 'BASE-DJ') or (e['t'] == 'LWPOLYLINE' and e['lay'] == 'Размеры')]
old += ['37BAFA', '37BAFB', '37BC97', '37BC43', '37BC6D', '37BCA1']
O = [o for o in O if o['t'] != 'noop']
O.append({'t': 'erase', 'h': old})
print(len(O), 'ops,', len(Fp), '+', len(Sp), 'piles,', k, 'rings, erase', len(old))
if len(sys.argv) > 1:
    out = ab.run(O, 'g13', 1200)
    open('w/g13.log', 'w', encoding='utf-8').write(out)
    print(out[-1500:])
