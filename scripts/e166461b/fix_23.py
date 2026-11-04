# clear texts crossed by the new beam lines on 2.2/2.3: notes → move the shelf (stretch point 0), dims → along-line
import re, json, sys, ezdxf, logging
logging.disable(logging.CRITICAL)
from shapely.geometry import LineString as LS, box
from shapely.strtree import STRtree
oc = open('w/oc_23.txt', encoding='utf-8').read()
oc = oc[oc.index('== 2.2'):]
hs = sorted(set(re.findall(r'ЛИНИЯ/ТЕКСТ\s+"[^"#]*#([0-9A-F]+)"', oc)))
d = ezdxf.readfile('w/live.dxf'); ms = d.modelspace()
segs = []; texts = []
for ln in open('w/geom.txt', encoding='utf-8-sig'):
    f = ln.rstrip('\r\n').split('|')
    if f[0] == 'S':
        a = (float(f[3]), float(f[4])); b = (float(f[5]), float(f[6]))
        if a != b: segs.append((f[1], LS([a, b])))
    elif f[0] == 'T' and len(f) > 7 and f[7].strip(): texts.append((f[1], box(*[float(v) for v in f[3:7]])))
for e in ms:
    t = e.dxftype()
    if t == 'LINE': segs.append((e.dxf.handle, LS([(e.dxf.start.x, e.dxf.start.y), (e.dxf.end.x, e.dxf.end.y)])))
    elif t == 'LWPOLYLINE':
        p = [tuple(q[:2]) for q in e.get_points('xy')]
        if e.closed: p = p + p[:1]
        if len(p) > 1: segs.append((e.dxf.handle, LS(p)))
G = [g for h, g in segs]; tree = STRtree(G)
def cost(h, bx, placed):
    bb = bx.buffer(40)
    return 20 * sum(1 for i in tree.query(bb) if segs[i][0] != h and G[i].intersects(bb)) + 40 * sum(1 for hh, t in texts if hh != h and t.intersects(bx.buffer(50))) + 40 * sum(1 for q in placed if q.intersects(bx.buffer(50)))
ops = []; placed = []
for h in hs:
    e = d.entitydb.get(h)
    own = [t for hh, t in texts if hh == h]
    if not own: continue
    u = own[0].union(own[-1]).envelope if len(own) > 1 else own[0]
    best = None
    if e is not None and e.dxftype() == 'DIMENSION':
        p1, p2, dp = e.dxf.defpoint2, e.dxf.defpoint3, e.dxf.defpoint
        vert = abs((e.dxf.get('angle', 0) or 0) % 180 - 90) < 1
        tm = e.dxf.text_midpoint; c = u.centroid
        for st in range(-12, 13):
            dx, dy = (0, st * 60) if vert else (st * 60, 0)
            bx = box(u.bounds[0] + dx, u.bounds[1] + dy, u.bounds[2] + dx, u.bounds[3] + dy)
            cs = cost(h, bx, placed) + abs(st) / 4
            if best is None or cs < best[0]: best = (cs, bx, {'t': 'dimtx', 'h': h, 'at': [tm[0] + dx, tm[1] + dy]})
    else:
        for dx in (0, 300, -300, 600, -600):
            for dy in (0, 300, -300, 500, -500, 700, -700, 900, -900):
                bx = box(u.bounds[0] + dx, u.bounds[1] + dy, u.bounds[2] + dx, u.bounds[3] + dy)
                cs = cost(h, bx, placed) + (abs(dx) + abs(dy)) / 300
                if best is None or cs < best[0]: best = (cs, bx, (dx, dy))
        dx, dy = best[2]
        best = (best[0], best[1], {'t': 'movept', 'h': h, 'd': [dx, dy]})
    placed.append(best[1]); ops.append(best[2]); print(h, round(best[0], 1), best[2])
json.dump(ops, open('ops/fix23.json', 'w'))
