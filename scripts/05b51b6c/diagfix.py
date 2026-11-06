"""Opening symbol = one straight diagonal (bottom-left -> top-right). Find kinked diagonals (3+ vertex open polylines inside an opening rectangle) on given sheets and straighten."""
import sys, json, ezdxf, ab
d = ezdxf.readfile('w/live.dxf'); ms = d.modelspace()
O = []; found = []
for f in sys.argv[1:]:
    if f == 'run': continue
    n, w = list(json.load(open('w/%s.json' % f, encoding='utf-8')).items())[0]
    P = []
    for e in ms.query('LWPOLYLINE'):
        pts = [tuple(p[:2]) for p in e.get_points()]
        if not all(w[0] < x < w[2] and w[1] < y < w[3] for x, y in pts): continue
        P.append((e, pts))
    rects = []
    for e, pts in P:
        if (e.closed or (len(pts) >= 4 and pts[0] == pts[-1])) and len(set(pts)) == 4:
            xs = [p[0] for p in pts]; ys = [p[1] for p in pts]
            rects.append((min(xs), min(ys), max(xs), max(ys)))
    for e, pts in P:
        if e.closed or len(pts) < 3: continue
        xs = [p[0] for p in pts]; ys = [p[1] for p in pts]
        bb = (min(xs), min(ys), max(xs), max(ys))
        for r in rects:
            if abs(bb[0] - r[0]) < 30 and abs(bb[2] - r[2]) < 30 and abs(bb[1] - r[1]) < 30 and abs(bb[3] - r[3]) < 30 and (r[2] - r[0]) > 200:
                found.append((n, e.dxf.handle, len(pts), [round(v) for v in r]))
                O.append({'t': 'plset', 'h': e.dxf.handle, 'p': [[r[0], r[1]], [r[2], r[3]]], 'closed': False})
                break
print(found)
if 'run' in sys.argv and O:
    O.append({'t': 'save'}); print(ab.run(O, 'diag', 600)[-300:])
