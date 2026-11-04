import ezdxf,sys,collections
d=ezdxf.readfile(sys.argv[1]);msp=d.modelspace()
x0,y0,x1,y1=map(float,sys.argv[2:6])
c=collections.Counter()
for e in msp:
    p=None
    for a in ('insert','start','center'):
        if e.dxf.hasattr(a): p=e.dxf.get(a);break
    if p is None and e.dxftype()=='LWPOLYLINE':
        pts=list(e.get_points());p=pts[0] if pts else None
    if p is None: continue
    if x0<p[0]<x1 and y0<p[1]<y1: c[e.dxf.layer]+=1
for ln,n in c.most_common():
    L=d.layers.get(ln) if d.layers.has_entry(ln) else None
    print(ln,n, 'off' if L and L.is_off() else '', 'frozen' if L and L.is_frozen() else '', 'noplot' if L and not L.dxf.plot else '')
for l in d.layouts:
    if l.name in ('6.1','6.3'):
        for v in l.query('VIEWPORT'):
            print(l.name,'VP c',round(v.dxf.view_center_point.x),round(v.dxf.view_center_point.y),'h',round(v.dxf.view_height),'W',round(v.dxf.width),'H',round(v.dxf.height),'pc',round(v.dxf.center.x),round(v.dxf.center.y), 'frz',[x for x in v.frozen_layers][:8])
