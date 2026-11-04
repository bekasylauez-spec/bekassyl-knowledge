# move dim texts that lie on bars / far from their segment to a free spot AT their segment (along ≤ w, or an outer row
# on a shelf), checked against the real drawing. Output ops/fixdim2.json (dimtx).
import json, sys, math
import ezdxf, logging
logging.disable(logging.CRITICAL)
from shapely.geometry import LineString as LS, box
from shapely.strtree import STRtree
sys.path.insert(0, '.')
import gen_fm as G
d = ezdxf.readfile('w/live.dxf'); ms = d.modelspace()
segs = []; texts = {}
for ln in open('w/geom.txt', encoding='utf-8-sig'):
    f = ln.rstrip('\r\n').split('|')
    if f[0] == 'S':
        a = (float(f[3]), float(f[4])); b = (float(f[5]), float(f[6]))
        if a != b: segs.append((f[1], LS([a, b])))
    elif f[0] == 'T' and len(f) > 7 and f[7].strip(): texts.setdefault(f[1], []).append(box(*[float(v) for v in f[3:7]]))
bars = []
for e in ms:
    if e.dxftype() == 'LINE': segs.append((e.dxf.handle, LS([(e.dxf.start.x, e.dxf.start.y), (e.dxf.end.x, e.dxf.end.y)])))
    if e.dxftype() == 'LINE' and e.dxf.layer.startswith('диам'): bars.append(LS([(e.dxf.start.x, e.dxf.start.y), (e.dxf.end.x, e.dxf.end.y)]))
    if e.dxftype() == 'LWPOLYLINE':
        p = [tuple(q[:2]) for q in e.get_points('xy')]
        if e.closed: p = p + p[:1]
        if len(p) > 1: segs.append((e.dxf.handle, LS(p)))
bt = STRtree(bars)
ops = []; moved = []
for sh in ('3.3', '3.4', '3.5', '3.6'):
    fx, X, Y = G.origin(sh)
    W = box(fx, 455939, fx + 59400, 497939)
    L = [(h, g) for h, g in segs if g.intersects(W)]
    T = [(h, t) for h, ts in texts.items() for t in ts if t.intersects(W)]
    for e in ms:
        if e.dxftype() != 'DIMENSION': continue
        dp = e.dxf.defpoint
        if not W.contains(box(dp.x - 1, dp.y - 1, dp.x + 1, dp.y + 1)): continue
        h = e.dxf.handle
        if h not in texts: continue
        cur = texts[h][0]
        p1, p2 = e.dxf.defpoint2, e.dxf.defpoint3
        vert = abs(e.dxf.get('angle', 0) - 90) < 1 or abs(e.dxf.get('angle', 0) - 270) < 1
        c = cur.centroid
        if vert: a, b = sorted((p1.y, p2.y)); along = max(a - c.y, c.y - b, 0); off = abs(c.x - dp.x)
        else: a, b = sorted((p1.x, p2.x)); along = max(a - c.x, c.x - b, 0); off = abs(c.y - dp.y)
        onbar = any(bars[i].intersects(cur.buffer(-10)) for i in bt.query(cur))
        if not onbar and along <= 700 and off <= 1500: continue
        w = (cur.bounds[3] - cur.bounds[1]) if vert else (cur.bounds[2] - cur.bounds[0])
        mid = (a + b) / 2
        tm = e.dxf.get('text_midpoint'); corr = (tm[0] - c.x, tm[1] - c.y) if tm is not None else (0, 0)
        best = None
        for row in (0, 1, 2, 3, 4):
            for sgn in (1, -1):
                for k in (0, 0.25, -0.25, 0.5, -0.5, 0.75, -0.75, 1, -1, 1.25, -1.25):
                    cc = mid + k * w
                    if vert:
                        cx = dp.x - 225 if row == 0 else dp.x + sgn * (225 + 450 * row); cy = cc
                    else:
                        cy = dp.y + 225 if row == 0 else dp.y + sgn * (225 + 450 * row); cx = cc
                    dx, dy = cx - c.x, cy - c.y
                    cand = box(cur.bounds[0] + dx, cur.bounds[1] + dy, cur.bounds[2] + dx, cur.bounds[3] + dy)
                    cst = 50 * sum(1 for i in bt.query(cand) if bars[i].intersects(cand.buffer(40)))
                    cst += 20 * sum(1 for hh, g in L if hh != h and g.intersects(cand.buffer(30)))
                    cst += 40 * sum(1 for hh, t in T if hh != h and t.intersects(cand.buffer(50)))
                    cst += 30 * sum(1 for t in moved if t.intersects(cand.buffer(50)))
                    cst += row * 3 + abs(k) * 2
                    if best is None or cst < best[0]: best = (cst, cx, cy, cand)
                if row == 0: break
        cst, cx, cy, cand = best
        moved.append(cand)
        ops.append({'t': 'dimtx', 'h': h, 'at': [cx + corr[0], cy + corr[1]]})
        print(sh, e.dxf.get('text') or round(e.get_measurement()), 'cost', cst)
json.dump(ops, open('ops/fixdim2.json', 'w'))
print(len(ops), 'moved')
