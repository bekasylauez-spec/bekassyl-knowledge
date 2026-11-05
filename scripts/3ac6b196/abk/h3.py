import ezdxf, sys
# probe: list segments crossing a probe line. args: dxf  orient(V|H) coord  lo hi
d = ezdxf.readfile(sys.argv[1]); m = d.modelspace()
o = sys.argv[2]; c = float(sys.argv[3]); lo, hi = float(sys.argv[4]), float(sys.argv[5])
hits = []
for e in m.query('LWPOLYLINE LINE'):
    if e.dxftype() == 'LINE':
        pts = [(e.dxf.start.x, e.dxf.start.y), (e.dxf.end.x, e.dxf.end.y)]
    else:
        pts = [(p[0], p[1]) for p in e.get_points()]
        if e.closed: pts.append(pts[0])
    for a, b in zip(pts, pts[1:]):
        if o == 'V':  # probe vertical line x=c, find crossing segments
            if (a[0] - c) * (b[0] - c) < 0 or (abs(a[0]-b[0])>1e-6 and (a[0]==c)):
                t = (c - a[0]) / (b[0] - a[0]); y = a[1] + t * (b[1] - a[1])
                if lo < y < hi: hits.append((round(y), round(abs(b[0]-a[0])), round(abs(b[1]-a[1])), e.dxf.layer[-6:]))
        else:
            if (a[1] - c) * (b[1] - c) < 0:
                t = (c - a[1]) / (b[1] - a[1]); x = a[0] + t * (b[0] - a[0])
                if lo < x < hi: hits.append((round(x), round(abs(b[0]-a[0])), round(abs(b[1]-a[1])), e.dxf.layer[-6:]))
hits.sort()
prev = None
for h in hits:
    print(h, '' if prev is None else 'd=%d' % (h[0] - prev)); prev = h[0]
