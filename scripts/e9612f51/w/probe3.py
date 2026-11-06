import ezdxf, sys, collections
from ezdxf import bbox
d=ezdxf.readfile(sys.argv[1]); m=d.modelspace()
xs=collections.Counter()
for e in m.query('LWPOLYLINE'):
    b=bbox.extents([e]); 
    w=b.size.x; h=b.size.y
    xs[(int(b.extmin.x//84100), round(w), round(h), e.dxf.layer, e.closed, e.dxf.get('const_width',0))]+=1
for k,v in sorted(xs.items()): print(k,v)
b=bbox.extents(m.query('INSERT[name=="16951165"]')); print(b)
for e in d.blocks['16951165']:
    if e.dxftype()=='TEXT': print(e.dxf.text, round(e.dxf.insert.x), round(e.dxf.insert.y))
