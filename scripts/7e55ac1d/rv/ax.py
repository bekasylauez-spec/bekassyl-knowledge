import ezdxf
from ezdxf import bbox
d=ezdxf.readfile('r.dxf'); m=d.modelspace()
AXT={"1","2","3","3/1","4","5","Л","М","4/1","2/1","1/1"}
for e in m.query('ACAD_PROXY_ENTITY'):
    s=[]
    try:
        vs=list(e.virtual_entities())
    except Exception: continue
    for pe in vs:
        if pe.dxftype() in('TEXT','MTEXT'): s.append(pe.plain_text() if pe.dxftype()=='MTEXT' else pe.dxf.text)
    s='|'.join(s)
    if s in AXT:
        ln=[(round(pe.dxf.start.x),round(pe.dxf.start.y),round(pe.dxf.end.x),round(pe.dxf.end.y)) for pe in vs if pe.dxftype()=='LINE' and pe.dxf.start.distance(pe.dxf.end)>1500]
        b=bbox.extents([e],fast=True)
        if 2460000<b.extmin.x<2490000: print(s,round((b.extmin.x+b.extmax.x)/2),round((b.extmin.y+b.extmax.y)/2), round(b.extmax.x-b.extmin.x), [(round(pe.dxf.start.x),round(pe.dxf.start.y),round(pe.dxf.end.x),round(pe.dxf.end.y)) for pe in vs if pe.dxftype()=="LINE"][:3])
