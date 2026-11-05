import ezdxf, sys, collections
d=ezdxf.readfile(sys.argv[1]); m=d.modelspace()
print('layouts',[l.name for l in d.layouts])
c=collections.Counter(e.dxftype() for e in m); print(c.most_common(25))
# frames: SPDS format proxies or big blocks
fr=[]
for e in m:
    t=e.dxftype()
    if t=='ACAD_PROXY_ENTITY' or t.startswith('SPDS') or t=='INSERT':
        try:
            b=ezdxf.bbox.extents([e])
            if b.has_data and b.size.x>200000/ (1) and False: pass
        except Exception: continue
for e in m.query('INSERT'):
    pass
import ezdxf.bbox as BB
big=[]
for e in m:
    if e.dxftype() in ('INSERT','ACAD_PROXY_ENTITY','LWPOLYLINE') or 'SPDS' in e.dxftype():
        try: b=BB.extents([e],fast=True)
        except Exception: continue
        if b.has_data and b.size.x>20000 and b.size.y>15000:
            big.append((round(b.extmin.x),round(b.extmin.y),round(b.size.x),round(b.size.y),e.dxftype(),getattr(e.dxf,'name','')))
for r in sorted(big): print(r)
