import ezdxf, collections
from ezdxf import bbox
d=ezdxf.readfile('an.dxf'); m=d.modelspace()
cache=bbox.Cache()
res=[]
for e in m.query('INSERT LWPOLYLINE POLYLINE'):
    try: b=bbox.extents([e],cache=cache)
    except: continue
    if not b.has_data: continue
    w=b.size.x; h=b.size.y
    if w>20000 and h>15000:
        res.append((e.dxftype(), getattr(e.dxf,'name',''), e.dxf.layer, e.dxf.handle, round(b.extmin.x),round(b.extmin.y),round(w),round(h)))
for r in sorted(res,key=lambda r:(-r[5],r[4])): print(r)
