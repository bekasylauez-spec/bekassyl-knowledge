import json, sys, ezdxf, logging
logging.disable(logging.CRITICAL)
from shapely.geometry import LineString as LS, box
d = ezdxf.readfile('w/live.dxf'); ms = d.modelspace()
texts = {}; segs = []
for ln in open('w/geom.txt', encoding='utf-8-sig'):
    f = ln.rstrip('\r\n').split('|')
    if f[0] == 'T' and len(f) > 7 and f[7].strip(): texts.setdefault(f[1], []).append(box(*[float(v) for v in f[3:7]]))
    if f[0] == 'S':
        a = (float(f[3]), float(f[4])); b = (float(f[5]), float(f[6]))
        if a != b: segs.append((f[1], LS([a, b])))
for e in ms:
    if e.dxftype() == 'LINE': segs.append((e.dxf.handle, LS([(e.dxf.start.x, e.dxf.start.y), (e.dxf.end.x, e.dxf.end.y)])))
    if e.dxftype() == 'LWPOLYLINE':
        p = [tuple(q[:2]) for q in e.get_points('xy')]
        if len(p) > 1: segs.append((e.dxf.handle, LS(p)))
ops = []
for h in sys.argv[1].split(','):
    e = d.entitydb.get(h); cur = texts[h][0]; c = cur.centroid
    dp = e.dxf.defpoint; p1, p2 = e.dxf.defpoint2, e.dxf.defpoint3
    vert = abs(e.dxf.get('angle', 0) - 90) < 1 or abs(e.dxf.get('angle', 0) - 270) < 1
    tm = e.dxf.get('text_midpoint'); corr = (tm[0] - c.x, tm[1] - c.y)
    a, b = sorted((p1.y, p2.y)) if vert else sorted((p1.x, p2.x)); mid = (a + b) / 2
    best = None
    for off in (380, 480, 600, -380, -480, -600, 800, -800):
        for k in (0, 0.3, -0.3, 0.6, -0.6):
            w = (cur.bounds[3] - cur.bounds[1]) if vert else (cur.bounds[2] - cur.bounds[0])
            cx, cy = (dp.x + off, mid + k * w) if vert else (mid + k * w, dp.y + off)
            dx, dy = cx - c.x, cy - c.y
            cand = box(cur.bounds[0] + dx, cur.bounds[1] + dy, cur.bounds[2] + dx, cur.bounds[3] + dy)
            cst = 30 * sum(1 for hh, g in segs if hh != h and g.intersects(cand.buffer(25))) + 40 * sum(1 for hh, ts in texts.items() if hh != h for t in ts if t.intersects(cand.buffer(40)))
            cst += abs(off) / 200 + abs(k) * 2
            if best is None or cst < best[0]: best = (cst, cx, cy)
    cst, cx, cy = best
    print(h, e.dxf.get('text'), 'cost', cst)
    ops.append({'t': 'dimtx', 'h': h, 'at': [cx + corr[0], cy + corr[1]]})
json.dump(ops, open('ops/fix7.json', 'w'))
