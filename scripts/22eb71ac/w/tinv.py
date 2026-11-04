import ezdxf,sys,collections
from ezdxf import bbox
d=ezdxf.readfile(sys.argv[1]); m=d.modelspace()
c=collections.Counter(e.dxftype() for e in m); print(c)
print('layouts',[l.name for l in d.layouts])
b=bbox.extents(m,fast=True); print('ext',b.extmin,b.extmax)
# proxies: class names
cls=collections.Counter()
for e in m:
    if e.dxftype()=='ACAD_PROXY_ENTITY':
        cls[e.dxf.get('proxy_entity_class_id')]+=1
print(cls)
print([ (k,v.name) for k,v in d.classes.classes.items()][:0])
for cl in d.classes: 
    if 'Mc' in cl.dxf.name or 'Spds' in cl.dxf.cpp_class_name: print(cl.dxf.name,cl.dxf.cpp_class_name)
