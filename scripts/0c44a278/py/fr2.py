import ezdxf,sys
from ezdxf import bbox
d=ezdxf.readfile(sys.argv[1]); m=d.modelspace()
for e in m.query('INSERT'):
    ext=bbox.extents([e],fast=True)
    if not ext.has_data: print(e.dxf.name,"nodata",e.dxf.insert); continue
    print(e.dxf.name,e.dxf.layer,[round(v) for v in (ext.extmin.x,ext.extmin.y,ext.extmax.x,ext.extmax.y)], e.dxf.xscale)
for e in m.query('LWPOLYLINE'):
    if e.dxf.layer not in ('Размеры',):
        ext=bbox.extents([e],fast=True); print('PL',e.dxf.layer,e.dxf.color,len(e),[round(v) for v in (ext.extmin.x,ext.extmin.y,ext.extmax.x,ext.extmax.y)])
