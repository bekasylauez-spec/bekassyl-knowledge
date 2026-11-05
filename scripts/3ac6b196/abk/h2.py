import ezdxf, sys, collections
d = ezdxf.readfile(sys.argv[1]); m = d.modelspace()
X0, Y0, X1, Y1 = map(float, sys.argv[2:6])
segs = []
for e in m.query('LWPOLYLINE LINE'):
    if e.dxftype() == 'LINE':
        pts = [(e.dxf.start.x, e.dxf.start.y), (e.dxf.end.x, e.dxf.end.y)]
    else:
        pts = [(p[0], p[1]) for p in e.get_points()]
        if e.closed: pts.append(pts[0])
    for a, b in zip(pts, pts[1:]):
        if not (X0 < a[0] < X1 and Y0 < a[1] < Y1): continue
        if abs(a[1] - b[1]) < 2 and abs(a[0] - b[0]) > 300: segs.append(('H', round(a[1]), min(a[0], b[0]), max(a[0], b[0]), e.dxf.layer, e.dxf.color, getattr(e.dxf,'const_width',0)))
        elif abs(a[0] - b[0]) < 2 and abs(a[1] - b[1]) > 300: segs.append(('V', round(a[0]), min(a[1], b[1]), max(a[1], b[1]), e.dxf.layer, e.dxf.color, getattr(e.dxf,'const_width',0)))
print(len(segs))
gaps = collections.Counter()
for o in 'HV':
    s = sorted([x for x in segs if x[0] == o], key=lambda x: x[1])
    for i, a in enumerate(s):
        for b in s[i + 1:]:
            g = b[1] - a[1]
            if g > 500: break
            if g < 30: continue
            ov = min(a[3], b[3]) - max(a[2], b[2])
            if ov > 400: gaps[(o, g)] += 1
for k, v in sorted(gaps.items(), key=lambda x: -x[1])[:40]: print(k, v)
