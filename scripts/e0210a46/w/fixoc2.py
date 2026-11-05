# fixoc.py <dxf> <sheets.json> <geom> <out_ops.json> [sheet,...]
# Greedy fixer for oc.py findings: dimension texts slide along their dim line (dimtx), SPDS callouts move as a whole
# (origin = stretch point 0, arrow target stays). Every candidate is scored with the same tests as oc.py.
import sys, json, math
src = open(__file__.replace('fixoc2.py', 'oc.py'), encoding='utf-8').read()
head = src[:src.index('total = 0')]
sys.argv = [sys.argv[0], sys.argv[1], sys.argv[2], '--geom=' + sys.argv[3]] + sys.argv[4:]
OUT = sys.argv[4]; ONLY = set(sys.argv[5].split(',')) if len(sys.argv) > 5 else None
sys.argv = sys.argv[:4]
exec(head)
from shapely.geometry import box as BX, LineString as LS
from shapely import affinity
from shapely.strtree import STRtree

def tsh(poly, s):
    return poly.buffer(-0.12 * math.sqrt(poly.area / max(len(s), 1)))

# note leaders/arrow targets: for SPDSNOTEPOSITION we need target points; read from geom: shelf known; leader = other segs
ops = []
moved_total = 0
for name, (x0, y0, x1, y1) in sheets.items():
    if ONLY and name not in ONLY: continue
    W = BX(x0, y0, x1, y1)
    SC = {'2.3': 50, '3.7': 25}.get(name, max(1, round((x1 - x0) / 594))); m5, m20 = 5 * SC, 20 * SC
    inner = BX(x0 + m20, y0 + m5, x1 - m5, y1 - m5); stamp = BX(x1 - m5 - 185 * SC, y0 + m5, x1 - m5, y0 + m5 + 55 * SC)
    T = [[p, poly, s] for p, poly, s in texts if W.contains(poly.centroid)]
    L = [[p, ls] for p, ls in segs if W.intersects(ls)]
    H = [hg for hh_, hg in hatches if W.intersects(hg)]

    def cost_text(pid, poly, s, ignore=()):
        c = 0; a = tsh(poly, s)
        if a.is_empty: a = poly
        for p, b, sb in T:
            if p == pid or p in ignore: continue
            if a.intersects(b) and a.intersection(b).area > 0.005 * min(poly.area, b.area): c += 1
        lim = 0.03 * math.sqrt(poly.area / max(len(s), 1))
        for p, ls in L:
            if p == pid or p in ignore: continue
            if a.intersects(ls) and a.intersection(ls).length > lim: c += 1
        if not inner.contains(poly): c += 3
        elif poly.intersects(stamp) and not stamp.contains(poly): c += 3
        for hg in H:
            if hg.intersects(poly) and hg.intersection(poly).area > 0.15 * poly.area: c += 1; break
        return c

    def cost_shelf(pid, sh):
        c = 0
        for p, ls in L:
            if p == pid or (ptype.get(p) == 'SPDSCONSTRUCTIONLINE' and ls.length > 1000): continue
            if ptype.get(p) == 'DIMENSION' and sh.intersection(ls).geom_type == 'LineString' and sh.intersection(ls).length > 1: continue
            if sh.crosses(ls) or (sh.intersects(ls) and sh.intersection(ls).length > 1): c += 1
        return c

    def cross_others(seg_list, pid):
        """moved lines of pid crossing other texts"""
        c = 0
        for p, b, sb in T:
            if p == pid: continue
            a = tsh(b, sb)
            for ls in seg_list:
                if a.intersects(ls) and a.intersection(ls).length > 0.03 * math.sqrt(b.area / max(len(sb), 1)): c += 1
        return c

    changed = True; it = 0
    while changed and it < 3:
        changed = False; it += 1
        # current bad parents
        bad = {}
        for p, poly, s in T:
            ct = cost_text(p, poly, s)
            if ct: bad[p] = bad.get(p, 0) + ct
        for p, ls in segs:
            if ptype.get(p, '').startswith('SPDSNOTE') and W.intersects(ls) and _is_shelf(p, ls):
                cs = cost_shelf(p, ls)
                if cs: bad[p] = bad.get(p, 0) + cs
        for pid in sorted(bad, key=lambda k: -bad[k]):
            typ = ptype.get(pid, '')
            mine = [t for t in T if t[0] == pid]
            if not mine: continue
            mysegs = [l for l in L if l[0] == pid]
            def total_cost(dx, dy, rigid_segs, moving_segs):
                c = 0
                for p, poly, s in mine:
                    c += cost_text(pid, affinity.translate(poly, dx, dy), s)
                for ls in moving_segs:
                    ls2 = affinity.translate(ls, dx, dy)
                    if _is_shelf(pid, ls): c += cost_shelf(pid, ls2)
                c += cross_others([affinity.translate(ls, dx, dy) for ls in moving_segs], pid)
                return c
            base = sum(cost_text(pid, poly, s) for p, poly, s in mine) + sum(cost_shelf(pid, ls) for p, ls in mysegs if _is_shelf(pid, ls))
            if base == 0: continue
            best = None
            if typ == 'DIMENSION':
                e = doc.entitydb.get(pid)
                if e is None or len(mine) != 1: continue
                poly = mine[0][1]; c0 = poly.centroid
                try:
                    dp, p2, p3 = e.dxf.defpoint, e.dxf.defpoint2, e.dxf.defpoint3
                except Exception: continue
                dt = e.dimtype & 7
                if dt == 0:
                    ang = math.radians(e.dxf.get('angle', 0) or 0); ux, uy = math.cos(ang), math.sin(ang)
                elif dt == 1:
                    L_ = math.hypot(p3.x - p2.x, p3.y - p2.y) or 1; ux, uy = (p3.x - p2.x) / L_, (p3.y - p2.y) / L_
                else: continue
                nx, ny = -uy, ux
                pr = lambda x, y: ((x - dp.x) * ux + (y - dp.y) * uy, (x - dp.x) * nx + (y - dp.y) * ny)
                tA, _ = pr(p2.x, p2.y); tB, _ = pr(p3.x, p3.y); tA, tB = min(tA, tB), max(tA, tB)
                _, s2 = pr(p2.x, p2.y)
                out = -1 if s2 > 0 else 1                     # outward normal sign: from the element to the dim line
                tc, sc_ = pr(c0.x, c0.y)
                bx0, by0, bx1, by1 = poly.bounds
                w = abs((bx1 - bx0) * ux + (by1 - by0) * uy) if abs(ux) > 0.99 or abs(uy) > 0.99 else max(bx1 - bx0, by1 - by0)
                hgt = abs((bx1 - bx0) * nx + (by1 - by0) * ny) if abs(ux) > 0.99 or abs(uy) > 0.99 else min(bx1 - bx0, by1 - by0)
                g = 0.3 * hgt; seg = tB - tA
                cands = []
                if w + 2 * g <= seg:
                    n_ = 12
                    for i in range(n_ + 1):
                        cands.append((tA + w / 2 + g + (seg - w - 2 * g) * i / n_, sc_))
                    for k in (0.5, 1.0):
                        cands.append((tB + g + w / 2 + k * w, sc_)); cands.append((tA - g - w / 2 - k * w, sc_))
                else:
                    for k in (0, 0.5, 1.0, 1.5, 2.0):
                        cands.append((tB + g + w / 2 + k * w, sc_)); cands.append((tA - g - w / 2 - k * w, sc_))
                    for tt in (tB + g + w / 2, tA - g - w / 2, (tA + tB) / 2, tB + w, tA - w, tB + 1.6 * w, tA - 1.6 * w):
                        for j in (1.3, 2.4, -1.3, -2.4):
                            cands.append((tt, sc_ + out * j * hgt))
                for tt, ss in cands:
                    dx = (tt - tc) * ux + (ss - sc_) * nx; dy = (tt - tc) * uy + (ss - sc_) * ny
                    c = cost_text(pid, affinity.translate(poly, dx, dy), mine[0][2]) + 0.02 * math.hypot(dx, dy) / max(hgt, 1)
                    if best is None or c < best[0]: best = (c, dx, dy)
                if best and best[0] < base - 0.5:
                    ops.append({'t': 'dimtx', 'h': pid, 'at': [c0.x + best[1], c0.y + best[2]]})
            elif typ in ('SPDSNOTEPOSITION', 'SPDSNOTECOMB'):
                # moving part: texts + shelf (+ leader start); arrow targets stay
                shelf = [ls for p, ls in mysegs if _is_shelf(pid, ls)]
                hh = max((pp.bounds[3] - pp.bounds[1]) for p, pp, s in mine)
                cands = [(dx * hh, dy * hh) for dx in (0, -0.75, 0.75, -1.5, 1.5, -2.5, 2.5) for dy in (0, -0.6, 0.6, -1.2, 1.2, -2.0, 2.0, -3.0, 3.0) if dx or dy]
                for dx, dy in cands:
                    c = total_cost(dx, dy, [], shelf) + 0.04 * math.hypot(dx, dy) / hh
                    if best is None or c < best[0]: best = (c, dx, dy)
                if best and best[0] < base - 0.5:
                    ops.append({'t': 'movept', 'h': pid, 'idx': 0, 'd': [best[1], best[2]]})
            else:
                continue
            if best and best[0] < base - 0.5:
                # update in-memory geometry
                dx, dy = best[1], best[2]
                for t in T:
                    if t[0] == pid: t[1] = affinity.translate(t[1], dx, dy)
                for l in L:
                    if l[0] == pid and (typ == 'DIMENSION' and False or _is_shelf(pid, l[1])): l[1] = affinity.translate(l[1], dx, dy)
                moved_total += 1; changed = True
    print(name, 'ops so far', len(ops))
json.dump(ops, open(OUT, 'w'), ensure_ascii=False)
print('TOTAL OPS', len(ops))
