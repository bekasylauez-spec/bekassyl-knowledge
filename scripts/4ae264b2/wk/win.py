import ezdxf,sys,collections
d=ezdxf.readfile(sys.argv[1]);msp=d.modelspace()
x0,y0,x1,y1=map(float,sys.argv[2:6])
c=collections.Counter();txt=[]
for e in msp:
    p=None
    for a in ('insert','start','center'):
        if e.dxf.hasattr(a): p=e.dxf.get(a);break
    if p is None and e.dxftype()=='LWPOLYLINE':
        pts=list(e.get_points());p=pts[0] if pts else None
    if p is None: continue
    if x0<p[0]<x1 and y0<p[1]<y1:
        c[(e.dxftype(),e.dxf.layer)]+=1
        if e.dxftype() in('TEXT','MTEXT'): txt.append(e.dxf.text if e.dxftype()=='TEXT' else e.text)
print(sum(c.values()),c.most_common(12));print(txt[:40])
