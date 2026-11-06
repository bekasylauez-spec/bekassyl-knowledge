# fixoc.py <dxf> <sheets.json> <geom> <out_ops.json> [sheet,...]
# Greedy fixer for oc.py findings: dimension texts slide along their dim line (dimtx), SPDS callouts move as a whole
# (origin = stretch point 0, arrow target stays). Every candidate is scored with the same tests as oc.py.
import sys, json, math
src = open(__file__.replace('fixoc.py', 'oc.py'), encoding='utf-8').read()
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
                poly = mine[0][1]; bx0, by0, bx1, by1 = poly.bounds
                horiz = (bx1 - bx0) >= (by1 - by0)
                step = max(bx1 - bx0, by1 - by0)
                cands = []
                for k in (0.2, 0.35, 0.6, 0.8, 1.0, 1.2, 1.4, 1.7, 1.9, 2.2, 2.5, 3.2, 4.0, 5.0):
                    for sg in (1, -1):
                        cands.append((sg * k * step, 0) if horiz else (0, sg * k * step))
                th = min(bx1 - bx0, by1 - by0)
                for j in (1.3, 2.2, 3.2):
                    for sj in (1, -1):
                        for k in (0, 0.5, -0.5, 1.0, -1.0, 1.6, -1.6):
                            a_, p_ = k * step, sj * j * th
                            cands.append((a_, p_) if horiz else (p_, a_))
                for dx, dy in cands:
                    perp = abs(dy) if horiz else abs(dx)
                    c = sum(cost_text(pid, affinity.translate(pp, dx, dy), s) for p, pp, s in mine) + 0.05 * math.hypot(dx, dy) / step + (0.3 if perp > 1 else 0)
                    if best is None or c < best[0]: best = (c, dx, dy)
                if best and best[0] < base - 0.5:
                    c0 = poly.centroid
                    ops.append({'t': 'dimtx', 'h': pid, 'at': [c0.x + best[1], c0.y + best[2]]})
            elif typ in ('SPDSNOTEPOSITION', 'SPDSNOTECOMB'):
                # moving part: texts + shelf (+ leader start); arrow targets stay
                shelf = [ls for p, ls in mysegs if _is_shelf(pid, ls)]
                hh = max((pp.bounds[3] - pp.bounds[1]) for p, pp, s in mine)
                cands = [(dx * hh, dy * hh) for dx in (0, -0.75, 0.75, -1.5, 1.5, -3, 3, -5, 5, -8, 8) for dy in (0, -0.6, 0.6, -1.2, 1.2, -2.4, 2.4, -3.6, 3.6, -5, 5) if dx or dy]
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
