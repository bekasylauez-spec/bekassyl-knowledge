import sys
from ezdxf.recover import readfile
from ezdxf.math import area as parea
doc,_=readfile(sys.argv[1]); msp=doc.modelspace()
minA=float(sys.argv[2]); maxA=float(sys.argv[3])
res=[]
for e in msp.query('LWPOLYLINE POLYLINE'):
    try:
        pts=[(p[0],p[1]) for p in e.get_points('xy')] if e.dxftype()=='LWPOLYLINE' else [(v.dxf.location.x,v.dxf.location.y) for v in e.vertices]
    except Exception: continue
    if len(pts)<3: continue
    closed=e.closed or (abs(pts[0][0]-pts[-1][0])<1 and abs(pts[0][1]-pts[-1][1])<1)
    if not closed: continue
    a=0
    for i in range(len(pts)):
        x1,y1=pts[i];x2,y2=pts[(i+1)%len(pts)];a+=x1*y2-x2*y1
    a=abs(a)/2/1e6
    if minA<=a<=maxA:
        xs=[p[0] for p in pts];ys=[p[1] for p in pts]
        res.append((round(min(xs)),round(min(ys)),round((max(xs)-min(xs))),round(max(ys)-min(ys)),round(a,3),len(pts),e.dxf.layer))
for r in sorted(res): print(r)
