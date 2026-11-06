import ezdxf, collections
from ezdxf.addons.drawing import matplotlib as dm
d=ezdxf.readfile('sch.dxf'); m=d.modelspace()
c=collections.Counter()
for e in m.query('LWPOLYLINE'):
    p=e.get_points('xy'); x=min(q[0] for q in p); y=min(q[1] for q in p)
    c[(round(x,-5),round(y,-5),e.dxf.layer,len(p))]+=1
for k,v in sorted(c.items()): print(k,v)
b=d.blocks['15616169']
for x in b:
    if x.dxftype()=='TEXT': print('ax',x.dxf.text,[round(v) for v in x.dxf.insert])
