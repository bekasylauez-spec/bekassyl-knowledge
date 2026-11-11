import sys,io; sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding="utf-8")
import ezdxf,collections
from ezdxf import bbox
d=ezdxf.readfile(sys.argv[1]); m=d.modelspace()
x0,y0,x1,y1=map(float,sys.argv[2:6])
c=collections.Counter()
for e in m:
    try: b=bbox.extents([e],fast=True)
    except Exception: continue
    if not b.has_data: continue
    if b.extmax.x>x0 and b.extmin.x<x1 and b.extmax.y>y0 and b.extmin.y<y1:
        c[(e.dxftype(),e.dxf.layer)]+=1
        if len(sys.argv)>6: print(e.dxf.handle,e.dxftype(),e.dxf.layer,[round(v) for v in (b.extmin.x,b.extmin.y,b.extmax.x,b.extmax.y)], getattr(e.dxf,'name',''))
for k,v in sorted(c.items()): print(k,v)
