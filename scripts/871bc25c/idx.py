import ezdxf, pickle, sys
from ezdxf import bbox
d = ezdxf.readfile(sys.argv[1]); m = d.modelspace()
frames = {}
vps = {}
for l in d.layouts:
    if l.name == 'Model': continue
    for v in l.query('VIEWPORT'):
        sc = v.dxf.view_height / v.dxf.height
        if sc < 2: continue
        c = v.dxf.view_center_point; t = v.dxf.get('view_target_point', (0, 0, 0)); w = v.dxf.width * sc; h = v.dxf.view_height
        vps.setdefault(l.name, []).append((t[0] + c.x - w / 2, t[1] + c.y - h / 2, t[0] + c.x + w / 2, t[1] + c.y + h / 2, sc, v.dxf.handle))
ents = []
cache = bbox.Cache()
for e in m:
    try:
        b = bbox.extents([e], cache=cache)
        bb = (b.extmin.x, b.extmin.y, b.extmax.x, b.extmax.y) if b.has_data else None
    except Exception:
        bb = None
    ents.append((e.dxf.handle, e.dxftype(), e.dxf.layer, bb))
pickle.dump({'vps': vps, 'ents': ents}, open(sys.argv[2], 'wb'))
print(len(ents)); 
for k, v in vps.items(): print(k, [tuple(round(a) for a in x[:5]) + (x[5],) for x in v])
