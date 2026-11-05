"""Extract partitions (pairs of parallel lines, gap ~T) from a PDF-imported plan.
args: dxf X0 Y0 X1 Y1 out.json [gapmin gapmax]"""
import ezdxf, sys, json, collections
d = ezdxf.readfile(sys.argv[1]); m = d.modelspace()
X0, Y0, X1, Y1 = map(float, sys.argv[2:6])
gmin = float(sys.argv[7]) if len(sys.argv) > 7 else 90
gmax = float(sys.argv[8]) if len(sys.argv) > 8 else 110
H = []; V = []
for e in m.query('LWPOLYLINE LINE'):
    if e.dxftype() == 'LINE':
        pts = [(e.dxf.start.x, e.dxf.start.y), (e.dxf.end.x, e.dxf.end.y)]
    else:
        pts = [(p[0], p[1]) for p in e.get_points()]
        if e.closed: pts.append(pts[0])
    for a, b in zip(pts, pts[1:]):
        if not (X0 <= min(a[0], b[0]) and max(a[0], b[0]) <= X1 and Y0 <= min(a[1], b[1]) and max(a[1], b[1]) <= Y1): continue
        if abs(a[1] - b[1]) < 1 and abs(a[0] - b[0]) > 150: H.append((a[1], min(a[0], b[0]), max(a[0], b[0])))
        elif abs(a[0] - b[0]) < 1 and abs(a[1] - b[1]) > 150: V.append((a[0], min(a[1], b[1]), max(a[1], b[1])))
def pairs(S):
    S = sorted(S)
    res = []
    for i, a in enumerate(S):
        for b in S[i + 1:]:
            g = b[0] - a[0]
            if g > gmax: break
            if g < gmin: continue
            lo, hi = max(a[1], b[1]), min(a[2], b[2])
            if hi - lo > 150: res.append(((a[0] + b[0]) / 2, lo, hi, g))
    # merge collinear overlapping: cluster by coordinate (<15 mm), then merge intervals inside a cluster
    res.sort()
    clusters = []
    for r in res:
        if clusters and abs(clusters[-1][-1][0] - r[0]) < 15: clusters[-1].append(r)
        else: clusters.append([r])
    mg = []
    for cl in clusters:
        cl.sort(key=lambda t: t[1]); cur = None
        for c, lo, hi, g in cl:
            if cur and lo <= cur[2] + 5: cur[2] = max(cur[2], hi)
            else:
                if cur: mg.append(cur)
                cur = [c, lo, hi, g]
        mg.append(cur)
    return mg
out = {'H': pairs(H), 'V': pairs(V)}
json.dump(out, open(sys.argv[6], 'w'), indent=0)
for k in out:
    for s in out[k]: print(k, ['%.0f' % v for v in s], 'L=%.0f' % (s[2] - s[1]))
