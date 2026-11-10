# Lines of DWG sheets 1-2 (tables, underlines) in paper mm from the sheet's lower-left (1:100); frame, side stamp and title block are left out.
import sys, json, ezdxf
from ezdxf import path as ezpath
doc = ezdxf.readfile(sys.argv[1]); msp = doc.modelspace()
sheets = {1: 804165 - 42000, 2: 846165 - 42000}; y0 = -274400; out = []
def keep(n, a, b):
    xs = (a[0], b[0]); ys = (a[1], b[1])
    if max(xs) < 21 or min(xs) > 414 or max(ys) < 6 or min(ys) > 291: return False    # frame band
    if min(xs) > 234 and max(ys) < 57: return False                                       # title block
    if max(xs) < 21.5: return False                                                       # side stamp
    if abs(a[0] - b[0]) > 380 or abs(a[1] - b[1]) > 280: return False                     # frame lines
    return True
for e in msp.query('LINE LWPOLYLINE POLYLINE'):
    try: pts = [(v.x, v.y) for v in ezpath.make_path(e).flattening(1)] if e.dxftype() != 'LINE' else [(e.dxf.start.x, e.dxf.start.y), (e.dxf.end.x, e.dxf.end.y)]
    except Exception: continue
    for n, xa in sheets.items():
        if all(xa - 10 <= p[0] <= xa + 42010 and y0 - 10 <= p[1] <= y0 + 29710 for p in pts):
            q = [((p[0] - xa) / 100, (p[1] - y0) / 100) for p in pts]
            for a, b in zip(q, q[1:]):
                if (abs(a[0] - b[0]) + abs(a[1] - b[1])) > 0.3 and keep(n, a, b):
                    out.append(dict(s=n, a=[round(a[0], 2), round(a[1], 2)], b=[round(b[0], 2), round(b[1], 2)], lw=e.dxf.get('lineweight', -1)))
json.dump(out, open(sys.argv[2], 'w', encoding='utf-8'), indent=0)
for n in sheets: print(n, sum(1 for o in out if o['s'] == n))
