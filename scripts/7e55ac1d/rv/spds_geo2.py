"""SPDS proxy objects of the KM DWG in paper mm: the sheet scale comes from the SPDSFORMAT frame that contains the object."""
import ezdxf, collections, sys
d = ezdxf.readfile('r.dxf'); m = d.modelspace()
classes = [c.dxf.name for c in d.classes]


def cname(e):
    for t in e.acdb_proxy_entity:
        if t.code == 91:
            i = t.value - 500
            return classes[i] if 0 <= i < len(classes) else str(t.value)


def vents(e):
    try:
        return list(e.virtual_entities())
    except Exception:
        return []


def pts_of(v):
    t = v.dxftype()
    if t == 'LINE': return [v.dxf.start, v.dxf.end]
    if t == 'LWPOLYLINE': return [(p[0], p[1]) for p in v.get_points()]
    if t == 'POLYLINE': return [q.dxf.location for q in v.vertices]
    if t in ('CIRCLE', 'ARC'): c = v.dxf.center; r = v.dxf.radius; return [(c[0] - r, c[1] - r), (c[0] + r, c[1] + r)]
    if t in ('TEXT', 'MTEXT'): return [v.dxf.insert]
    return []


objs = []
for e in m.query('ACAD_PROXY_ENTITY'):
    vs = vents(e)
    P = [p for v in vs for p in pts_of(v) if p[0] > 1000000]
    if not P: continue
    bb = (min(p[0] for p in P), min(p[1] for p in P), max(p[0] for p in P), max(p[1] for p in P))
    objs.append((cname(e), bb, vs))
frames = []
for c, bb, vs in objs:
    if c == 'SPDSFORMAT':
        w = bb[2] - bb[0]; h = bb[3] - bb[1]
        for pw in (420, 594, 297, 841):
            s = w / pw
            if abs(s - round(s)) < 0.02 and round(s) in (1, 10, 20, 25, 50, 75, 100):
                frames.append((bb, round(s))); break
want = sys.argv[1:] or None
cnt = collections.Counter()
for c, bb, vs in objs:
    if c == 'SPDSFORMAT': continue
    fr = [f for f in frames if f[0][0] <= bb[0] <= f[0][2] and f[0][1] <= bb[1] <= f[0][3]]
    if not fr: continue
    sc = fr[0][1]
    cnt[c] += 1
    if want and c not in want: continue
    if cnt[c] > 3: continue
    x0, y0 = bb[0], bb[1]
    print('=====', c, 'scale 1:%d' % sc, 'size %.1f x %.1f mm' % ((bb[2] - x0) / sc, (bb[3] - y0) / sc))
    f = lambda q: '(%.2f,%.2f)' % ((q[0] - x0) / sc, (q[1] - y0) / sc)
    for v in vs[:40]:
        t = v.dxftype()
        if t == 'LINE': print('   L', f(v.dxf.start), f(v.dxf.end))
        elif t == 'LWPOLYLINE': print('   P', [f(p) for p in v.get_points()][:10], 'w', round(v.dxf.const_width / sc, 2) if v.dxf.const_width else 0)
        elif t == 'POLYLINE': print('   PL', [f(q.dxf.location) for q in v.vertices][:10], 'w', [round(q.dxf.start_width / sc, 2) for q in v.vertices][:3])
        elif t == 'CIRCLE': print('   C', f(v.dxf.center), 'r %.2f' % (v.dxf.radius / sc))
        elif t == 'ARC': print('   A', f(v.dxf.center), 'r %.2f' % (v.dxf.radius / sc), round(v.dxf.start_angle), round(v.dxf.end_angle))
        elif t in ('TEXT', 'MTEXT'):
            h = v.dxf.char_height if t == 'MTEXT' else v.dxf.height
            s = v.plain_text() if t == 'MTEXT' else v.dxf.text
            print('   T', repr(s), f(v.dxf.insert), 'h %.2f' % (h / sc), 'style', v.dxf.get('style', ''), 'wf', round(v.dxf.get('width', 1), 2) if t == 'TEXT' else '', 'rot', round(v.dxf.get('rotation', 0)))
        elif t == 'SOLID' or t == 'TRACE': print('   S', [f(v.dxf.get(a)) for a in ('vtx0', 'vtx1', 'vtx2', 'vtx3')])
        else: print('  ', t)
print(cnt)
