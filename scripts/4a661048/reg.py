import ezdxf,sys
from ezdxf import bbox
d=ezdxf.readfile('src.dxf'); msp=d.modelspace()
# big rectangles = frames
for e in msp.query('LWPOLYLINE'):
    b=bbox.extents([e])
    if b.has_data and b.size.x>8000 and b.size.y>5000:
        print('PL',e.dxf.handle,e.dxf.layer,[round(v) for v in b.extmin][:2],[round(v) for v in b.size][:2])
for e in msp.query('INSERT'):
    print('INS',e.dxf.handle,e.dxf.name,[round(v) for v in e.dxf.insert][:2],round(e.dxf.xscale,2))
