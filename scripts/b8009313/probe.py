import sys,io; sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding="utf-8")
import ezdxf
from ezdxf import bbox
from ezdxf.proxygraphic import ProxyGraphic
f,x0,y0,x1,y1,ax,ay=sys.argv[1],*map(float,sys.argv[2:8])
d=ezdxf.readfile(f); m=d.modelspace()
def ext(e):
    t=e.dxftype()
    if t=='ACAD_PROXY_ENTITY':
        vs=list(ProxyGraphic(e.proxy_graphic,d).virtual_entities()); pts=[];tx=[]
        for v in vs:
            vt=v.dxftype()
            if vt=='TEXT': tx.append(v.dxf.text); pts.append(v.dxf.insert)
            elif vt=='LINE': pts+=[v.dxf.start,v.dxf.end]
            elif vt=='LWPOLYLINE': pts+=[ezdxf.math.Vec3(p[0],p[1]) for p in v.get_points()]
            elif vt=='POLYLINE': pts+=[q.dxf.location for q in v.vertices]
            elif vt=='CIRCLE': pts.append(v.dxf.center)
        pts=[p for p in pts if abs(p.x)>1 and abs(p.y)>1]
        if not pts: return None
        return min(p.x for p in pts),min(p.y for p in pts),max(p.x for p in pts),max(p.y for p in pts),' '.join(tx[:3])
    b=bbox.extents([e],fast=True)
    if not b.has_data: return None
    return b.extmin.x,b.extmin.y,b.extmax.x,b.extmax.y,''
for e in m:
    try: r=ext(e)
    except Exception: continue
    if not r: continue
    a,b_,c,dd,tx=r
    if c<x0 or a>x1 or dd<y0 or b_>y1: continue
    t=e.dxftype()
    if t in('MTEXT','TEXT'): tx=(e.plain_text() if t=='MTEXT' else e.dxf.text)[:25]
    if t=='INSERT': tx=e.dxf.name[:20]
    if t=='DIMENSION':
        p2,p3=e.dxf.defpoint2,e.dxf.defpoint3
        tx='DIM M=%.1f p2(%.1f,%.1f) p3(%.1f,%.1f)'%(e.get_measurement(),p2.x-ax,p2.y-ay,p3.x-ax,p3.y-ay)
    if t=='LWPOLYLINE':
        tx+=' pts'+str([(round(p[0]-ax,1),round(p[1]-ay,1)) for p in e.get_points()][:5])+(' w%.0f'%e.dxf.const_width if e.dxf.hasattr('const_width') else '')
    print(e.dxf.handle,t,e.dxf.layer[:10],'x[%.0f,%.0f] y[%.1f,%.1f]'%(a-ax,c-ax,b_-ay,dd-ay),tx)
