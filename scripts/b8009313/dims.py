import sys,io; sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding="utf-8")
import ezdxf
from ezdxf.proxygraphic import ProxyGraphic
d=ezdxf.readfile(sys.argv[1]); m=d.modelspace()
x0,y0,x1,y1=map(float,sys.argv[2:6])
def inb(p): return x0<p.x<x1 and y0<p.y<y1
for e in m:
    t=e.dxftype()
    if t=='DIMENSION':
        p2=e.dxf.defpoint2; p3=e.dxf.defpoint3
        if inb(p2) or inb(p3):
            print(e.dxf.handle,'DIM',round(e.get_measurement(),1),'p2',round(p2.x,1),round(p2.y,1),'p3',round(p3.x,1),round(p3.y,1),'txt',repr(e.dxf.text),e.dxf.get('dimstyle'))
    elif t=='ACAD_PROXY_ENTITY':
        try:
            pg=ProxyGraphic(e.acdb_proxy_graphic if hasattr(e,'acdb_proxy_graphic') else e.proxy_graphic, d)
            ents=list(pg.virtual_entities())
        except Exception as ex: continue
        pts=[];txt=[]
        for v in ents:
            if v.dxftype()=='TEXT': txt.append(v.dxf.text); pts.append(v.dxf.insert)
            elif v.dxftype()=='LINE': pts+= [v.dxf.start]
            elif v.dxftype() in('LWPOLYLINE','POLYLINE'):
                pts+=[ezdxf.math.Vec3(p[0],p[1]) for p in (v.get_points() if v.dxftype()=='LWPOLYLINE' else [q.dxf.location for q in v.vertices])]
            elif v.dxftype()=='CIRCLE': pts.append(v.dxf.center); txt.append('O%.0f'%v.dxf.radius)
        if pts and any(inb(p) for p in pts):
            xs=[p.x for p in pts]; ys=[p.y for p in pts]
            print(e.dxf.handle,'PROXY',e.dxf.layer,[round(min(xs)),round(min(ys)),round(max(xs)),round(max(ys))],txt[:6])
