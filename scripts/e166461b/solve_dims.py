# place flagged dim texts ON their dim line (rule: point on the line), along their own segment, at the spot that is
# free of lines/texts in the REAL drawing. Box model measured 04.11: horizontal → x centred on point, y line+255..+505;
# vertical → x point-350..point-100, y centred on point.
import re, sys, json, ezdxf, logging
logging.disable(logging.CRITICAL)
from shapely.geometry import LineString as LS, box
from shapely.strtree import STRtree
oc = open('w/oc_fm.txt', encoding='utf-8').read()
hs = sorted(set(re.findall(r'ЛИНИЯ/ТЕКСТ\s+"[^"#]*#([0-9A-F]+)"', oc)) | set(re.findall(r'ТЕКСТ/ТЕКСТ\s+"[^"#]*#([0-9A-F]+)"', oc)))
skip = set(sys.argv[1].split(',')) if len(sys.argv) > 1 else set()
d = ezdxf.readfile('w/live.dxf'); ms = d.modelspace()
segs = []; texts = []
for ln in open('w/geom.txt', encoding='utf-8-sig'):
    f = ln.rstrip('\r\n').split('|')
    if f[0] == 'S':
        a = (float(f[3]), float(f[4])); b = (float(f[5]), float(f[6]))
        if a != b: segs.append((f[1], LS([a, b])))
    elif f[0] == 'T' and len(f) > 7 and f[7].strip(): texts.append((f[1], box(*[float(v) for v in f[3:7]]), f[7]))
for e in ms:
    t = e.dxftype()
    if t == 'LINE': segs.append((e.dxf.handle, LS([(e.dxf.start.x, e.dxf.start.y), (e.dxf.end.x, e.dxf.end.y)])))
    elif t == 'LWPOLYLINE':
        p = [tuple(q[:2]) for q in e.get_points('xy')]
        if e.closed: p = p + p[:1]
        if len(p) > 1: segs.append((e.dxf.handle, LS(p)))
G = [g for h, g in segs]; tree = STRtree(G)
TB = [t for h, t, s in texts]; ttree = STRtree(TB)
ops = []; placed = []
for h in hs:
    e = d.entitydb.get(h)
    if e is None or e.dxftype() != 'DIMENSION' or h in skip: continue
    own = [t for hh, t, s in texts if hh == h]
    if not own: continue
    cur = own[0]
    p1, p2, dp = e.dxf.defpoint2, e.dxf.defpoint3, e.dxf.defpoint
    vert = abs((e.dxf.get('angle', 0) or 0) % 180 - 90) < 1
    w = (cur.bounds[3] - cur.bounds[1]) if vert else (cur.bounds[2] - cur.bounds[0])
    a, b = sorted((p1.y, p2.y)) if vert else sorted((p1.x, p2.x))
    best = None
    steps = [k * 50 for k in range(-40, 41)]
    for st in steps:
        c = (a + b) / 2 + st
        if c - w / 2 > b + 150 or c + w / 2 < a - 150: continue       # stay at its own segment
        if vert:
            pt = (dp.x, c); bx = box(dp.x - 350, c - w / 2, dp.x - 100, c + w / 2)
        else:
            pt = (c, dp.y + 155); bx = box(c - w / 2, dp.y + 255, c + w / 2, dp.y + 505)
        bb = bx.buffer(30)
        nl = sum(1 for i in tree.query(bb) if segs[i][0] != h and G[i].intersects(bb))
        nt = sum(1 for i in ttree.query(bx.buffer(50)) if texts[i][0] != h and TB[i].intersects(bx.buffer(50))) + sum(1 for q in placed if q.intersects(bx.buffer(50)))
        cst = 20 * nl + 40 * nt + abs(st) / 200
        if best is None or cst < best[0]: best = (cst, pt, bx)
    cst, pt, bx = best
    placed.append(bx)
    ops.append({'t': 'dimtx', 'h': h, 'at': list(pt)})
    print(h, 'cost', round(cst, 1))
json.dump(ops, open('ops/solve_dims.json', 'w'))
print(len(ops), 'dims')
