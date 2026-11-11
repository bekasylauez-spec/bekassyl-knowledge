import ezdxf
from ezdxf.math import area
doc=ezdxf.readfile('w.dxf'); msp=doc.modelspace()
X0,X1,Y0,Y1=1675000,1735000,1003000,1047000
for e in msp.query('LWPOLYLINE HATCH'):
    try:
        if e.dxftype()=='LWPOLYLINE':
            pts=[(p[0],p[1]) for p in e.get_points()]
            if not pts: continue
            x=sum(p[0] for p in pts)/len(pts); y=sum(p[1] for p in pts)/len(pts)
            if X0<x<X1 and Y0<y<Y1 and (e.closed or len(pts)>3):
                xs=[p[0] for p in pts]; ys=[p[1] for p in pts]
                print('PL',e.dxf.handle,e.dxf.layer,e.closed,len(pts),'bbox',round(min(xs)),round(min(ys)),round(max(xs)-min(xs)),round(max(ys)-min(ys)),'A',round(abs(area(pts))/1e6,4))
        else:
            for pth in e.paths:
                if hasattr(pth,'vertices'): pts=[(v[0],v[1]) for v in pth.vertices]
                else:
                    pts=[]
                    for ed in pth.edges:
                        if hasattr(ed,'start'): pts.append((ed.start[0],ed.start[1]))
                if not pts: continue
                x=sum(p[0] for p in pts)/len(pts); y=sum(p[1] for p in pts)/len(pts)
                if X0<x<X1 and Y0<y<Y1:
                    xs=[p[0] for p in pts]; ys=[p[1] for p in pts]
                    print('HA',e.dxf.handle,e.dxf.layer,e.dxf.pattern_name,len(pts),'bbox',round(min(xs)),round(min(ys)),round(max(xs)-min(xs)),round(max(ys)-min(ys)),'A',round(abs(area(pts))/1e6,4))
    except Exception as ex: pass
