import sys, json, ezdxf, logging
logging.disable(logging.CRITICAL)
from shapely.geometry import LineString as LS, box
d = ezdxf.readfile('w/live.dxf'); ms = d.modelspace()
bars = [LS([(e.dxf.start.x, e.dxf.start.y), (e.dxf.end.x, e.dxf.end.y)]) for e in ms if e.dxftype() == 'LINE' and e.dxf.layer.startswith('диам')]
T = []
for ln in open('w/geom.txt', encoding='utf-8-sig'):
    f = ln.rstrip().split('|')
    if f[0] == 'T' and len(f) > 7: T.append((f[1], box(*[float(v) for v in f[3:7]])))
side = int(sys.argv[2]) if len(sys.argv) > 2 else 0
ops = []
for pair in sys.argv[1].split(';'):
    small, big = pair.split(',')
    for h in (big,):
        e = d.entitydb.get(h); p1, p2, dp = e.dxf.defpoint2, e.dxf.defpoint3, e.dxf.defpoint
        vert = abs((e.dxf.get('angle', 0) or 0) % 180 - 90) < 1
        ops.append({'t': 'dimtx', 'h': h, 'at': [dp.x, (p1.y + p2.y) / 2] if vert else [(p1.x + p2.x) / 2, dp.y + 155]})
    e = d.entitydb.get(small); p1, p2, dp = e.dxf.defpoint2, e.dxf.defpoint3, e.dxf.defpoint
    vert = abs((e.dxf.get('angle', 0) or 0) % 180 - 90) < 1
    best = None
    for sg in ((1, -1) if side == 0 else (side,)):
        for off in (675, 900):
            if vert:
                cx, cy = dp.x + sg * off, (p1.y + p2.y) / 2; bx = box(cx - 130, cy - 270, cx + 130, cy + 270)
            else:
                cx, cy = (p1.x + p2.x) / 2, dp.y + sg * off; bx = box(cx - 270, cy - 130, cx + 270, cy + 130)
            c = 10 * sum(1 for b in bars if b.intersects(bx.buffer(40))) + 10 * sum(1 for hh, t in T if hh not in (small, big) and t.intersects(bx.buffer(40))) + off / 300
            if best is None or c < best[0]: best = (c, cx, cy, sg, off)
    c, cx, cy, sg, off = best
    at = [cx, cy - 265] if vert else [cx - 265, cy - 100]
    ops.append({'t': 'dimtx', 'h': small, 'at': at})
    print(small, 'side', sg, 'off', off, 'cost', c)
json.dump(ops, open('ops/pairfix.json', 'w'))
