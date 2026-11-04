import ezdxf,sys,math,collections
from ezdxf import bbox
import os; d=ezdxf.readfile(os.environ.get("DXF","w/cur.dxf")); m=d.modelspace()
x1,y1,x2,y2=map(float,sys.argv[1:5]); types=sys.argv[5].split(",") if len(sys.argv)>5 else ["LINE","ARC","LWPOLYLINE"]
for e in m:
    t=e.dxftype()
    if t not in types: continue
    try: b=bbox.extents([e],fast=True)
    except Exception: continue
    if not b.has_data: continue
    if not(b.extmin.x>=x1 and b.extmax.x<=x2 and b.extmin.y>=y1 and b.extmax.y<=y2): continue
    lt=e.dxf.get("linetype","BYLAYER")
    if t=="LINE":
        s,f=e.dxf.start,e.dxf.end; L=(f-s).magnitude
        print("L",e.dxf.handle,e.dxf.layer,lt,round(s.x),round(s.y),round(f.x),round(f.y),"len",round(L,1))
    elif t=="ARC":
        a=(e.dxf.end_angle-e.dxf.start_angle)%360
        print("A",e.dxf.handle,e.dxf.layer,lt,"c",round(e.dxf.center.x),round(e.dxf.center.y),"r",round(e.dxf.radius,1),"a",round(e.dxf.start_angle,3),round(e.dxf.end_angle,3),"len",round(math.radians(a)*e.dxf.radius,1))
    elif t=="LWPOLYLINE":
        pts=list(e.get_points("xyb"));
        L=0
        for i in range(len(pts)-(0 if e.closed else 1)):
            p,q=pts[i],pts[(i+1)%len(pts)]
            c=math.dist(p[:2],q[:2]); bl=p[2]
            if bl: th=4*math.atan(abs(bl)); r=c/2/math.sin(th/2); c=r*th
            L+=c
        print("P",e.dxf.handle,e.dxf.layer,lt,"n",len(pts),"closed",e.closed,"w",e.dxf.get("const_width",0),[(round(p[0]),round(p[1]),round(p[2],4)) for p in pts][:8],"len",round(L,1))
    else:
        print(t,e.dxf.handle,e.dxf.layer,[round(v) for v in (b.extmin.x,b.extmin.y,b.extmax.x,b.extmax.y)])
