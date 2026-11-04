# Sections 1-1 (sheet 2.6), 2-2 and 3-3 (sheet 2.7) cut from model.py (+ LIRA slabs/stairs)
import json, math
from shapely.geometry import Polygon, box, LineString, MultiPolygon, GeometryCollection, MultiPoint
from shapely.ops import unary_union
import model as M
from dimtools import chain

B = M.boxes()
LP = M.lira_plates()
_SL = {}
for kind, pts in LP:
    if kind == 'slab': _SL.setdefault(round(pts[0][2]), []).append(MultiPoint([(p[0], p[1]) for p in pts]).convex_hull.buffer(8))
SLABU = {z: unary_union(v).buffer(-8) for z, v in _SL.items()}

LT6 = ('E064E', (1779945.2, -1326169.6), 1784837.9, '-4,350')    # level mark templates (Онкоцентр, 1:100)
LT7 = ('E064F', (1779945.2, -1310199.6), 1785787.9, '+11,620')


def geoms(g):
    if g.is_empty: return []
    if isinstance(g, (Polygon, LineString)): return [g]
    return [x for x in g.geoms]


def cut_plates(cut, pos):
    """intersect LIRA quads with the plane -> (kind, z, (u0,u1)) for slabs, polygons for stairs"""
    pos = pos + 0.37
    slabs = {}; stairs = []; vis = []
    ci = 0 if cut == 'x' else 1; ui = 1 - ci
    for kind, pts in LP:
        cs = [p[ci] for p in pts]
        if min(cs) < pos < max(cs):
            seg = []
            n = len(pts)
            for i in range(n):
              for j in range(i + 1, n):
                a, b = pts[i], pts[j]
                if (a[ci] - pos) * (b[ci] - pos) < 0:
                    t = (pos - a[ci]) / (b[ci] - a[ci])
                    seg.append((a[ui] + t * (b[ui] - a[ui]), a[2] + t * (b[2] - a[2])))
            if len(seg) < 2: continue
            seg.sort()
            (u0, z0), (u1, z1) = seg[0], seg[-1]
            if kind == 'slab':
                pass
            else:
                stairs.append(Polygon([(u0, z0), (u1, z1), (u1, z1 - 200), (u0, z0 - 200)]))
        elif kind == 'stair':
            vis.append((pts, cs))
    return slabs, stairs, vis


def merge(iv):
    iv = sorted(iv); out = []
    for a, b in iv:
        if out and a <= out[-1][1] + 80: out[-1][1] = max(out[-1][1], b)
        else: out.append([a, b])
    return out


def section(cut, pos, view):
    """cut 'x': plane x=pos, u=y, view toward -x (visible x<pos). cut 'y': plane y=pos, u=x, view toward +y."""
    cutp = []; podg = []; visual = []
    for k, x0, y0, x1, y1, z0, z1 in B:
        lo, hi = (x0, x1) if cut == 'x' else (y0, y1)
        u0, u1 = (y0, y1) if cut == 'x' else (x0, x1)
        r = box(u0, z0, u1, z1)
        if lo < pos < hi:
            (podg if k == 'podg' else cutp).append(r)
        else:
            d = (pos - hi) if (cut == 'x' and view < 0) else (lo - pos) if cut == 'y' else None
            if d is not None and d >= 0 and k != 'podg': visual.append((d, r))
    _, stairs, vstairs = cut_plates(cut, pos)
    slabs = {}
    for z, U in SLABU.items():
        ln = LineString([(pos + 0.37, -50000), (pos + 0.37, 90000)]) if cut == 'x' else LineString([(-50000, pos + 0.37), (90000, pos + 0.37)])
        for g in geoms(U.intersection(ln)):
            if g.geom_type != 'LineString': continue
            cs = [c[1] if cut == 'x' else c[0] for c in g.coords]
            slabs.setdefault(z, []).append((min(cs), max(cs)))
    ends = {-3275: -3275, 0: -125, 22750: 22875, 20050: 20175, 31175: 31175}
    for z, iv in slabs.items():
        for a, b in merge(iv):
            a = ends.get(round(a), a) if round(a) in ends else a
            b = ends.get(round(b), b) if round(b) in ends else b
            if round(a) == 0: a = -125
            cutp.append(box(a, z - M.T_SLAB, b, z))
    cutp += stairs
    vs = []; dmin = None
    for pts, cs in vstairs:
        d = (pos - max(cs)) if cut == 'x' else (min(cs) - pos)
        if d < 0: continue
        ui = 1 if cut == 'x' else 0
        pr = Polygon([(p[ui], p[2]) for p in pts]).convex_hull
        if pr.geom_type != 'Polygon' or pr.area < 1: continue
        vs.append(pr); vs.append(Polygon([(c[0], c[1] - 200) for c in pr.exterior.coords]).convex_hull)
        dmin = d if dmin is None else min(dmin, d)
    if vs:
        U = unary_union([v.buffer(30) for v in vs]).buffer(-30)
        for g in geoms(U):
            if g.geom_type == 'Polygon': visual.append((dmin, g))
    concrete = unary_union(cutp).buffer(0.5).buffer(-0.5)
    covered = concrete
    lines = []
    for d, r in sorted(visual, key=lambda a: a[0]):
        v = r.difference(covered)
        if v.area > 100:
            bd = v.boundary.difference(covered.buffer(2))
            for g in geoms(bd):
                if g.length > 30: lines.append(list(g.coords))
        covered = covered.union(r)
    return concrete, unary_union(podg), lines


def mark_ops(val, tu, tz, edge_u, X, Y, tag):
    T = LT7 if len(val) == 7 else LT6
    h, tip, xend, old = T
    dx = X + tu - tip[0]
    return [{'t': 'clone', 'h': h, 'base': list(tip), 'to': [X + tu, Y + tz], 'tag': tag + 'c'},
            {'t': 'serfix', 'h': tag + 'c', 's': [[old, val]], 'd': [[xend + dx, X + edge_u, 0.6]], 'tag': tag}]


def fmt(z):
    return ('+' if z > 0 else '-' if z < 0 else '±') + '%.3f' % (abs(z) / 1000.0)


def draw(cut, pos, view, X, Y, tagp, axes, levels_left, el_marks, bottom_pts, chains_extra, top_u):
    conc, podg, lines = section(cut, pos, view)
    ops = []
    i = 0
    for g in geoms(conc):
        if g.geom_type != 'Polygon': continue
        loops = [[[X + a, Y + b] for a, b in list(g.exterior.coords)[:-1]]] + [[[X + a, Y + b] for a, b in list(r.coords)[:-1]] for r in g.interiors]
        for lp in loops:
            ops.append({'t': 'pl', 'p': lp, 'closed': True, 'layer': '0', 'color': 124, 'lw': 30, 'tag': '%sC%d' % (tagp, i)}); i += 1
        ops.append({'t': 'hatch', 'pat': 'ANSI36', 'sc': 20, 'ang': 0, 'layer': '.', 'loops': loops, 'tag': '%sCH%d' % (tagp, i)})
    for g in geoms(podg):
        lp = [[X + a, Y + b] for a, b in list(g.exterior.coords)[:-1]]
        ops.append({'t': 'pl', 'p': lp, 'closed': True, 'layer': '0', 'color': 124, 'lw': 30, 'tag': tagp + 'P'})
        ops.append({'t': 'hatch', 'pat': 'AR-CONC', 'sc': 1.5, 'ang': 0, 'layer': '.', 'loops': [lp], 'tag': tagp + 'PH'})
    for k, ln in enumerate(lines):
        ops.append({'t': 'pl', 'p': [[X + a, Y + b] for a, b in ln], 'closed': False, 'layer': '0', 'color': 256, 'lw': 18, 'tag': '%sV%d' % (tagp, k)})
    # axes
    for name, u in axes:
        ops.append({'t': 'clone', 'h': 'C8719', 'base': [0, 0], 'to': [0, 0], 'tag': tagp + 'AX' + name})
        ops.append({'t': 'axis', 'h': tagp + 'AX' + name, 's': [X + u, Y + top_u], 'e': [X + u, Y - 8100], 'val': name})
    # vertical level chain + marks (left)
    uMin = min(e for _, e in levels_left)
    uch = uMin - 700; utip = uMin - 1600
    pts = []
    for z, e in levels_left:
        pts.append((e, z))
    ops += chain(pts + [(levels_left[0][1] - 100, -5450)], uch, True, -1, X=X, Y=Y)
    for z, e in levels_left:
        if z == -5350:
            ops += mark_ops(fmt(z), utip - 1600, z, e, X, Y, '%sLM%d' % (tagp, z))
        elif z in M.LEV or z == 21200:
            ops += mark_ops(fmt(z), utip, z, e, X, Y, '%sLM%d' % (tagp, z))
    for z, tu, e in el_marks:
        ops += mark_ops(fmt(z), tu, z, e, X, Y, '%sEM%d' % (tagp, z))
    for pts2, line, vert, outw in chains_extra:
        ops += chain(pts2, line, vert, outw, X=X, Y=Y)
    # bottom rows
    ops += chain(bottom_pts, -6450, False, -1, X=X, Y=Y)
    ax_u = [u for _, u in axes]
    ops += chain([(ax_u[0], -5450), (ax_u[-1], -5450)], -7250, False, -1, X=X, Y=Y)
    return ops


def levels_for(edge_big, edge_typ, fm_edge, top):
    L = [(-5350, fm_edge), (-4650, fm_edge), (-350, edge_big), (-100, edge_big), (3700, edge_big), (3950, edge_big)]
    for z in M.LEV[3:]:
        L += [(z - 250, edge_typ), (z, edge_typ)]
    L += [(21200, edge_typ)]
    return L


if __name__ == '__main__':
    out = {}
    # 1-1: x = 11900, u = y (А/1 left), view -x; sheet 2.6 frame x0 = 53379
    X, Y = 62554.0, 466200.0
    ax1 = [('А/1', 0), ('А', 5000), ('Б', 14750), ('В', 22750), ('В/1', 28750)]
    lev = levels_for(-3275, -125, -1950, 21200)
    em = [(23100, 14325, 15225), (22400, 12825, 15225)]
    ch = [([(22875, 19700), (22875, 22150), (22875, 22400), (22875, 23100)], 23700, True, 1)]
    bp = [(-3275, -350), (-1950, -5350), (0, -5450), (5000, -5450), (14750, -5450), (22750, -5450), (28750, -5450), (29800, -5350), (31175, -350)]
    out['s11'] = draw('x', 11900, -1, X, Y, 'X1_', ax1, lev, em, bp, ch, 24300)
    # 2-2: y = 1500, u = x, view +y; sheet 2.7 frame x0 = 112779
    X2, Y2 = 119404.0, 471500.0
    ax2 = [('1', 0), ('2', 6800), ('3', 13250), ('4', 20050)]
    lev2 = levels_for(-125, -125, -825, 21200)
    bp2 = [(-825, -5350), (-125, -350), (0, -5450), (6800, -5450), (13250, -5450), (20050, -5450), (20175, -350), (20875, -5350)]
    out['s22'] = draw('y', 1500, 1, X2, Y2, 'X2_', ax2, lev2, [], bp2, [], 22300)
    # 3-3: y = 16600
    X3 = 145929.0
    em3 = [(23100, 9375, 10275), (22400, 7875, 10275), (21450, 4875, 6675)]
    ch3 = [([(6675, 19700), (6675, 21200), (6675, 21450)], 6000, True, -1),
           ([(13375, 19700), (13375, 22150), (13375, 22400), (13375, 23100)], 14100, True, 1)]
    out['s33'] = draw('y', 16600, 1, X3, Y2, 'X3_', ax2, lev2, em3, bp2, ch3, 24300)
    for k, v in out.items():
        json.dump(v, open('ops/%s.json' % k, 'w', encoding='utf-8'), ensure_ascii=False)
        print(k, len(v))
