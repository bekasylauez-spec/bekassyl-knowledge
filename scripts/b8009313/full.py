import sys,io; sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding="utf-8")
import ezdxf
from ezdxf import bbox
from ezdxf.proxygraphic import ProxyGraphic
d=ezdxf.readfile(sys.argv[1]); m=d.modelspace()
x0,y0,x1,y1=map(float,sys.argv[2:6])
def r(v): return round(v,1)
for e in m:
    t=e.dxftype()
    try: b=bbox.extents([e],fast=True)
    except Exception: b=None
    info=''
    if t=='ACAD_PROXY_ENTITY':
        try:
            pg=ProxyGraphic(e.proxy_graphic,d); vs=list(pg.virtual_entities())
            pts=[];tx=[]
            for v in vs:
                vt=v.dxftype()
                if vt=='TEXT': tx.append(v.dxf.text); pts.append(v.dxf.insert)
                elif vt=='LINE': pts+=[v.dxf.start,v.dxf.end]
                elif vt=='LWPOLYLINE': pts+=[ezdxf.math.Vec3(p[0],p[1]) for p in v.get_points()]
                elif vt=='POLYLINE': pts+=[q.dxf.location for q in v.vertices]
                elif vt=='CIRCLE': pts.append(v.dxf.center)
            if not pts: continue
            xs=[p.x for p in pts if abs(p.x)>1];ys=[p.y for p in pts if abs(p.y)>1]
            if not xs or not ys: continue
            bb=(min(xs),min(ys),max(xs),max(ys)); info=str(tx[:4])
        except Exception as ex: continue
    elif b is not None and b.has_data: bb=(b.extmin.x,b.extmin.y,b.extmax.x,b.extmax.y)
    else: continue
    if not(bb[2]>x0 and bb[0]<x1 and bb[3]>y0 and bb[1]<y1): continue
    if t=='DIMENSION': info='M=%s p2=(%s,%s) p3=(%s,%s) dl=(%s,%s)'%(r(e.get_measurement()),r(e.dxf.defpoint2.x),r(e.dxf.defpoint2.y),r(e.dxf.defpoint3.x),r(e.dxf.defpoint3.y),r(e.dxf.defpoint.x),r(e.dxf.defpoint.y))
    elif t=='INSERT': info='%s @(%s,%s)'%(e.dxf.name,r(e.dxf.insert.x),r(e.dxf.insert.y))
    elif t=='LINE': info='(%s,%s)-(%s,%s)'%(r(e.dxf.start.x),r(e.dxf.start.y),r(e.dxf.end.x),r(e.dxf.end.y))
    elif t=='LWPOLYLINE': info=str([(r(p[0]),r(p[1])) for p in e.get_points()][:6])+(' w=%s'%e.get_points()[0][2] if e.get_points() else '')
    elif t in('TEXT','MTEXT'): info=(e.plain_text() if t=='MTEXT' else e.dxf.text)[:40]
    print(e.dxf.handle,t,e.dxf.layer,[round(v) for v in bb],info)
