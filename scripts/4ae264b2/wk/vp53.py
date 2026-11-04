import ezdxf,sys
d=ezdxf.readfile(sys.argv[1]); l=d.layouts.get('5.3')
for v in l.query('VIEWPORT'):
    print('VP',v.dxf.get('id'),'status',v.dxf.get('status'),'c',v.dxf.view_center_point,'h',v.dxf.view_height,'w',v.dxf.width,'H',v.dxf.height,'flags',v.dxf.get('flags'),'frozen',list(v.frozen_layers)[:10] if hasattr(v,'frozen_layers') else '')
for e in l:
    if e.dxftype()!='VIEWPORT': print(e.dxftype(), e.dxf.layer)
msp=d.modelspace()
import collections
c=collections.Counter()
for e in msp:
    try:
        p=e.dxf.insert if e.dxf.hasattr('insert') else (e.dxf.start if e.dxf.hasattr('start') else None)
    except Exception: p=None
    if p is None: continue
    if 4500000<p[0]<4517000 and 2225000<p[1]<2243000: c[(e.dxftype(),e.dxf.layer)]+=1
print(c.most_common(20))
