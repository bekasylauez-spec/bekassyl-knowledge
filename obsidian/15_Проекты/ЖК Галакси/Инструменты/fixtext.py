# repair dimension texts flagged by oc.py using the REAL AutoCAD geometry (geom.txt + live.dxf):
# move each flagged text along its dimension line (or to the other side) to the first spot free of lines and texts.
import re, sys, json, math
import ezdxf
from shapely.geometry import box, LineString
from shapely.strtree import STRtree

dxf, geom, ocout, win = sys.argv[1], sys.argv[2], sys.argv[3], [float(v) for v in sys.argv[4].split(',')]
W = box(*win)
segs = {}; texts = {}
for ln in open(geom, encoding='utf-8-sig'):
    f = ln.rstrip('\r\n').split('|')
    if f[0] == 'S':
        a = (float(f[3]), float(f[4])); b = (float(f[5]), float(f[6]))
        if a != b: segs.setdefault(f[1], []).append(LineString([a, b]))
    elif f[0] == 'T' and f[7].strip():
        texts.setdefault(f[1], []).append(box(*[float(v) for v in f[3:7]]))
d = ezdxf.readfile(dxf); m = d.modelspace()
other = []
dims = {}
for e in m:
    t = e.dxftype()
    if t == 'LWPOLYLINE':
        p = [tuple(q[:2]) for q in e.get_points('xy')]
        if e.closed: p = p + p[:1]
        if len(p) > 1:
            g = LineString(p)
            if g.intersects(W): other.append(('pl', g))
    elif t == 'DIMENSION': dims[e.dxf.handle] = e
bad = set()
for ln in open(ocout, encoding='utf-8'):
    for h in re.findall(r'"[^"#]*#([0-9A-F]+)"', ln): bad.add(h)
    mm = re.search(r'ТЕКСТ/ТЕКСТ\s+"[^"]*#([0-9A-F]+)"\s+<>\s+[^#]*#([0-9A-F]+)', ln)
    if mm: bad.add(mm.group(1))
allL = [g for h, gs in segs.items() for g in gs if g.intersects(W)]
allLh = [h for h, gs in segs.items() for g in gs if g.intersects(W)]
allT = [(h, t) for h, ts in texts.items() for t in ts if t.intersects(W)]
ops = []; moved = {}
def free(bx, own):
    bb = bx.buffer(30)
    for g, h in zip(allL, allLh):
        if h != own and g.intersects(bb): return False
    for k, g in other:
        if g.intersects(bb): return False
    for h, t in allT:
        if h != own and t.intersects(bx.buffer(60)): return False
    for t in moved.values():
        if t.intersects(bx.buffer(60)): return False
    return True
for h in sorted(bad):
    if h not in dims or h not in texts: continue
    e = dims[h]; cur = texts[h][0]
    # side-placed short texts (on a shelf off the line) stay where the chain put them (Bekassyl 04.11)
    dp = e.dxf.defpoint; ang = e.dxf.get('angle', 0)
    if abs(math.sin(math.radians(ang))) > 0.5:
        if abs(cur.centroid.x - dp[0]) > 400: continue
    elif abs(cur.centroid.y - dp[1]) > 400: continue
    tm = e.dxf.get('text_midpoint')
    cx, cy = cur.centroid.x, cur.centroid.y
    corr = (tm[0] - cx, tm[1] - cy) if tm is not None else (0, 0)
    w, ht = cur.bounds[2] - cur.bounds[0], cur.bounds[3] - cur.bounds[1]
    vert = ht > w
    best = None
    steps = [k * s for k in range(1, 3) for s in (1, -1)]
    for side in (0,):
        for st in steps:
            dx, dy = (0, st * (max(w, ht) * 0.6 + 120)) if vert else (st * (max(w, ht) * 0.6 + 120), 0)
            if side: dx, dy = (dx - 520, dy) if vert else (dx, dy + 520)
            cand = box(cur.bounds[0] + dx, cur.bounds[1] + dy, cur.bounds[2] + dx, cur.bounds[3] + dy)
            if free(cand, h): best = (cx + dx, cy + dy, cand); break
        if best: break
    if best:
        moved[h] = best[2]
        ops.append({'t': 'dimtx', 'h': h, 'at': [best[0] + corr[0], best[1] + corr[1]]})
print(len(bad), 'flagged', len(ops), 'moved')
json.dump(ops, open('ops/fixtext.json', 'w'))
