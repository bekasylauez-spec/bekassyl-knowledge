"""Geometry of SPDS proxy objects on DWG sheet 7 (section 1-1, scale 1:50) and sheet 5 (plan, scale 1:75), in paper mm."""
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


region, sc = (2510000, -1726000, 2537000, -1700000), 50
if len(sys.argv) > 1 and sys.argv[1] == 'plan':
    region, sc = (2463000 - 1500, -1725000, 2490000, -1700000), 75
cnt = collections.Counter(); seen = set()
for e in m.query('ACAD_PROXY_ENTITY'):
    vs = vents(e)
    P = [p for v in vs for p in pts_of(v)]
    if not P: continue
    x0 = min(p[0] for p in P); y0 = min(p[1] for p in P); x1 = max(p[0] for p in P); y1 = max(p[1] for p in P)
    if not (region[0] < x0 < region[2] and region[1] < y0 < region[3]): continue
    c = cname(e); cnt[c] += 1
    if cnt[c] > 2: continue
    print('=====', c, 'size %.1f x %.1f mm' % ((x1 - x0) / sc, (y1 - y0) / sc))
    for v in vs[:30]:
        t = v.dxftype(); f = lambda q: '(%.1f,%.1f)' % ((q[0] - x0) / sc, (q[1] - y0) / sc)
        if t == 'LINE': print('   L', f(v.dxf.start), f(v.dxf.end), 'lw', v.dxf.lineweight)
        elif t == 'LWPOLYLINE': print('   P', [f(p) for p in v.get_points()][:8], 'w', v.dxf.const_width / sc if v.dxf.const_width else 0, [round(p[2] / sc, 2) for p in v.get_points('xyseb')][:3])
        elif t == 'POLYLINE': print('   PL', [f(q.dxf.location) for q in v.vertices][:8])
        elif t == 'CIRCLE': print('   C', f(v.dxf.center), 'r %.2f' % (v.dxf.radius / sc))
        elif t == 'ARC': print('   A', f(v.dxf.center), 'r %.2f' % (v.dxf.radius / sc), round(v.dxf.start_angle), round(v.dxf.end_angle))
        elif t in ('TEXT', 'MTEXT'):
            h = v.dxf.char_height if t == 'MTEXT' else v.dxf.height
            s = v.plain_text() if t == 'MTEXT' else v.dxf.text
            print('   T', repr(s), f(v.dxf.insert), 'h %.2f' % (h / sc), v.dxf.get('style', ''), 'align', (v.dxf.get('attachment_point', '') if t == 'MTEXT' else v.dxf.get('halign', '')), 'w', round(v.dxf.get('width', 1) ,2) if t=='TEXT' else '', 'obl', round(v.dxf.get('oblique',0),1) if t=='TEXT' else '')
        else: print('  ', t)
print(cnt)
