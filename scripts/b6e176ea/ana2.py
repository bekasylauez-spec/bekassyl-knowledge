import ezdxf
from ezdxf import bbox
d=ezdxf.readfile("w/cur.dxf"); m=d.modelspace()
def txt(e):
    t=e.dxftype()
    if t=="TEXT": return e.dxf.text
    if t=="MTEXT": return e.plain_text()
    if t=="ACAD_PROXY_ENTITY":
        s=[]
        try:
            for pe in e.virtual_entities():
                if pe.dxftype()=="TEXT": s.append(pe.dxf.text)
                elif pe.dxftype()=="MTEXT": s.append(pe.plain_text())
        except Exception: pass
        return "|".join(s)
    return ""
items=[]
for e in m:
    if e.dxftype() in("TEXT","MTEXT","ACAD_PROXY_ENTITY"):
        t=txt(e)
        if t:
            b=bbox.extents([e],fast=True)
            if b.has_data: items.append((e,t,b))
import pickle
stamps=[e for e in m.query("INSERT") if e.dxf.name=="крпкер"]
for st in sorted(stamps,key=lambda e:(-e.dxf.insert.y,e.dxf.insert.x)):
    x,y=st.dxf.insert.x,st.dxf.insert.y; s=st.dxf.xscale*100
    bb=bbox.extents([st],fast=True)
    print("==",st.dxf.handle,round(x),round(y),"sc",round(s),"bb",[round(v) for v in (bb.extmin.x,bb.extmin.y,bb.extmax.x,bb.extmax.y)])
    for e,t,b in items:
        cx=(b.extmin.x+b.extmax.x)/2; cy=(b.extmin.y+b.extmax.y)/2
        if bb.extmin.x-5<cx<bb.extmax.x+5 and bb.extmin.y-5<cy<bb.extmax.y+5:
            print("   ",e.dxftype()[:5],e.dxf.handle,repr(t[:90]))
